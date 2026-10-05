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

nValues = [4, 8, 9, 16, 27, 36, 49, 64, 81, 100, 125, 343, 512, 729, 1000, 1337]
timeoutSeconds = 100
outputFile = "results.csv"

encoders = {
    "Pairwise": pairwise.EncodeNQueens,
    "Commander": commander.EncodeNQueens,
    "Product": product.EncodeNQueens,
    "Sequential": sequential.EncodeNQueens,
    "Binary": binary.EncodeNQueens,
}

def solveClauses(clauses, resultQueue):
    try:
        from pysat.solvers import Solver
        solver = Solver(name='g3', bootstrap_with=clauses)
        isSat = solver.solve()
        solver.delete()
        resultQueue.put(isSat)
    except Exception as error:
        resultQueue.put(None)

def solveWithTimeout(clauses, timeoutSeconds):
    resultQueue = mp.Queue()
    process = mp.Process(target=solveClauses, args=(clauses, resultQueue))
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

if __name__ == "__main__":

    resultFile = open(outputFile, "w", newline="")
    csvWriter = csv.writer(resultFile)
    csvWriter.writerow(["N", "Method", "NumVars", "NumClauses", "BuildTime", "SolveTime", "Status"])

    for n in nValues:

        for methodName in encoders:
            encodeFunc = encoders[methodName]

            startTime = time.time()
            clauses = encodeFunc(n)
            buildTime = time.time() - startTime

            numVars = 0
            for clause in clauses:
                for lit in clause:
                    if abs(lit) > numVars:
                        numVars = abs(lit)
            numClauses = len(clauses)

            startTime = time.time()
            status = solveWithTimeout(clauses, timeoutSeconds)
            solveTime = time.time() - startTime

            print(n, methodName, numVars, numClauses, buildTime, solveTime, status)
            csvWriter.writerow([n, methodName, numVars, numClauses, buildTime, solveTime, status])
            resultFile.flush()

        try:
            startTime = time.time()
            status = cplexMip.solveCplexWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(n, "CPLEX", "-", "-", "-", solveTime, status)
        csvWriter.writerow([n, "CPLEX", "-", "-", "-", solveTime, status])
        resultFile.flush()

        try:
            startTime = time.time()
            status = cpSat.solveCpSatWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(n, "CP-SAT", "-", "-", "-", solveTime, status)
        csvWriter.writerow([n, "CP-SAT", "-", "-", "-", solveTime, status])
        resultFile.flush()

        try:
            startTime = time.time()
            status = cplexCp.solveCplexCpWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(n, "CPLEX_CP", "-", "-", "-", solveTime, status)
        csvWriter.writerow([n, "CPLEX_CP", "-", "-", "-", solveTime, status])
        resultFile.flush()

        try:
            startTime = time.time()
            status = gurobiSolver.solveGurobiWithTimeout(n, timeoutSeconds)
            solveTime = time.time() - startTime
        except Exception as error:
            status = "ERROR: " + str(error)
            solveTime = 0
        print(n, "Gurobi", "-", "-", "-", solveTime, status)
        csvWriter.writerow([n, "Gurobi", "-", "-", "-", solveTime, status])
        resultFile.flush()

    resultFile.close()
    print("Done", outputFile)