import gurobipy as gp
import multiprocessing as mp

from gurobipy import GRB

def solveGurobi(n, resultQueue):
    try:
        model = gp.Model("NQueens_Gurobi")
        model.Params.OutputFlag = 0
        x = model.addVars(n, n, vtype=GRB.BINARY, name="x")
        for r in range(n):
            model.addConstr(gp.quicksum(x[r, c] for c in range(n)) == 1)
        for c in range(n):
            model.addConstr(gp.quicksum(x[r, c] for r in range(n)) == 1)
        for k in range(-n + 1, n):
            diag = [x[r, r - k] for r in range(n) if 0 <= r - k < n]
            if len(diag) > 1:
                model.addConstr(gp.quicksum(diag) <= 1)
        for k in range(2 * n - 1):
            antiDiag = [x[r, k - r] for r in range(n) if 0 <= k - r < n]
            if len(antiDiag) > 1:
                model.addConstr(gp.quicksum(antiDiag) <= 1)
        model.optimize()
        isOk = model.status == GRB.OPTIMAL or model.SolCount > 0
        resultQueue.put(isOk)
    except Exception as error:
        resultQueue.put(None)

def solveGurobiWithTimeout(n, timeoutSeconds):
    resultQueue = mp.Queue()
    process = mp.Process(target=solveGurobi, args=(n, resultQueue))
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