import multiprocessing as mp

from docplex.cp.model import CpoModel

def solveCplexCp(n, resultQueue):
    try:
        mdl = CpoModel(name=f"NQueens_CP_{n}")
        queens = [mdl.integer_var(min=0, max=n - 1, name=f"q_{i}") for i in range(n)]
        mdl.add(mdl.all_diff(queens))
        mdl.add(mdl.all_diff([queens[i] + i for i in range(n)]))
        mdl.add(mdl.all_diff([queens[i] - i for i in range(n)]))
        sol = mdl.solve(LogVerbosity='Quiet')
        resultQueue.put(sol is not None)
    except Exception as error:
        resultQueue.put(None)

def solveCplexCpWithTimeout(n, timeoutSeconds):
    resultQueue = mp.Queue()
    process = mp.Process(target=solveCplexCp, args=(n, resultQueue))
    process.start()
    process.join(timeoutSeconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return "TIMEOUT"

    isOk = resultQueue.get()
    if isOk is None:
        return "ERROR"
    if isOk:
        return "SAT"
    else:
        return "UNSAT"

