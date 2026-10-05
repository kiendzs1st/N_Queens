import multiprocessing as mp

from docplex.mp.model import Model
def solveCplex(n, resultQueue):
    try:
        model = Model(name="NQueens")
        x = model.binary_var_matrix(keys1=n, keys2=n, name='x')
        for i in range(n):
            model.add_constraint(model.sum(x[i, c] for c in range(n)) == 1)
            model.add_constraint(model.sum(x[r, i] for r in range(n)) == 1)
        for k in range(-n + 1, n):
            diag = [x[r, r - k] for r in range(n) if 0 <= r - k < n]
            if len(diag) > 1:
                model.add_constraint(model.sum(diag) <= 1)
        for k in range(2 * n - 1):
            antiDiag = [x[r, k - r] for r in range(n) if 0 <= k - r < n]
            if len(antiDiag) > 1:
                model.add_constraint(model.sum(antiDiag) <= 1)
        solution = model.solve()
        resultQueue.put(solution is not None)
    except Exception as error:
        resultQueue.put(None)

def solveCplexWithTimeout(n, timeoutSeconds):
    resultQueue = mp.Queue()
    process = mp.Process(target=solveCplex, args=(n, resultQueue))
    process.start()
    process.join(timeoutSeconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return "TIMEOUT"

    isSat = resultQueue.get()
    if isSat is None:
        return "ERROR"
    if isSat:
        return "SAT"
    else:
        return "UNSAT"

