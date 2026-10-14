import csv
import multiprocessing as mp
import time

from SatEncoder import pairwise
from SatEncoder import commander
from SatEncoder import product
from SatEncoder import sequential
from SatEncoder import binary
from IntegerLinearProgramming import cplexMip, gurobiSolver
from ConstraintsProgramming import cpSat, cplexCp

nValues = [4, 6, 8, 10, 16, 27, 36, 50, 100, 273, 568, 730, 1010, 1337]
timeoutSeconds = 100
outputFile = "results.csv"

encoders = {
    "Pairwise": pairwise.EncodeNQueens,
    "Commander": commander.EncodeNQueens,
    "Product": product.EncodeNQueens,
    "Sequential": sequential.EncodeNQueens,
    "Binary": binary.EncodeNQueens,
}

def solveSatProcess(encodeFunc, n, resultQueue):
    try:
        from pysat.solvers import Solver

        buildStart = time.time()
        clauses = encodeFunc(n)
        buildTime = time.time() - buildStart

        numClauses = len(clauses)
        numVars = 0
        for clause in clauses:
            for lit in clause:
                if abs(lit) > numVars:
                    numVars = abs(lit)

        solver = Solver(name="cadical153")
        for clause in clauses:
            solver.add_clause(clause)

        solveStart = time.time()
        isSat = solver.solve()
        solveTime = time.time() - solveStart

        solver.delete()
        del clauses

        resultQueue.put((isSat, numVars, numClauses, buildTime, solveTime))
    except Exception as error:
        resultQueue.put(("ERROR: " + str(error), 0, 0, 0, 0))

def solveSatWithTimeout(encodeFunc, n, timeoutSeconds):

    resultQueue = mp.Queue()
    process = mp.Process(target=solveSatProcess, args=(encodeFunc, n, resultQueue))
    process.start()
    process.join(timeoutSeconds)

    if process.is_alive():
        process.kill()
        process.join()
        return "-", "-", "-", "-", "TIMEOUT"

    if resultQueue.empty():
        return "-", "-", "-", "-", "ERROR"

    res = resultQueue.get()
    status_or_sat = res[0]

    if isinstance(status_or_sat, str):
        return res[1], res[2], res[3], res[4], status_or_sat

    status = "SAT" if status_or_sat else "UNSAT"
    return res[1], res[2], res[3], res[4], status

if __name__ == "__main__":

    mp.set_start_method("spawn", force=True)

    resultFile = open(outputFile, "w", newline="")
    csvWriter = csv.writer(resultFile)
    csvWriter.writerow(["N", "Method", "NumVars", "NumClauses", "BuildTime", "SolveTime", "Status"])

    for n in nValues:
        print(f"\n==================== Testing N = {n} ====================")

        for methodName, encodeFunc in encoders.items():
            try:
                numVars, numClauses, buildTime, solveTime, status = solveSatWithTimeout(encodeFunc, n, timeoutSeconds)
            except Exception as error:
                numVars, numClauses, buildTime, solveTime, status = "-", "-", "-", "-", "ERROR: " + str(error)

            print(
                f"SAT-{methodName:<10} | Vars: {str(numVars):<8} | Clauses: {str(numClauses):<10} | BuildTime: {str(buildTime):<8} | SolveTime: {str(solveTime):<8} | Status: {status}")
            csvWriter.writerow([n, methodName, numVars, numClauses, buildTime, solveTime, status])
            resultFile.flush()

        try:
            startTime = time.time()
            status = cplexMip.solveCplexWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(f"CPLEX MIP       | SolveTime: {solveTime:.4f}s | Status: {status}")
        csvWriter.writerow([n, "CPLEX", "-", "-", "-", solveTime, status])
        resultFile.flush()

        try:
            startTime = time.time()
            status = cpSat.solveCpSatWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(f"CP-SAT          | SolveTime: {solveTime:.4f}s | Status: {status}")
        csvWriter.writerow([n, "CP-SAT", "-", "-", "-", solveTime, status])
        resultFile.flush()

        try:
            startTime = time.time()
            status = cplexCp.solveCplexCpWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(f"CPLEX_CP        | SolveTime: {solveTime:.4f}s | Status: {status}")
        csvWriter.writerow([n, "CPLEX_CP", "-", "-", "-", solveTime, status])
        resultFile.flush()

        try:
            startTime = time.time()
            status = gurobiSolver.solveGurobiWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(f"Gurobi          | SolveTime: {solveTime:.4f}s | Status: {status}")
        csvWriter.writerow([n, "Gurobi", "-", "-", "-", solveTime, status])
        resultFile.flush()

    resultFile.close()
    print("\nDone! Results saved to", outputFile)