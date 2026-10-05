import multiprocessing as mp

from ortools.sat.python import cp_model

def solveCpSat(n, resultQueue):
    try:
        model = cp_model.CpModel()
        queens = [model.NewIntVar(0, n - 1, f'queen_{i}') for i in range(n)]
        model.AddAllDifferent(queens)
        model.AddAllDifferent([queens[i] + i for i in range(n)])
        model.AddAllDifferent([queens[i] - i for i in range(n)])
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        isOk = status == cp_model.OPTIMAL or status == cp_model.FEASIBLE
        resultQueue.put(isOk)
    except Exception as error:
        resultQueue.put(None)

def solveCpSatWithTimeout(n, timeoutSeconds):
    resultQueue = mp.Queue()
    process = mp.Process(target=solveCpSat, args=(n, resultQueue))
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
