from pysat.solvers import Solver

from SatEncoder import pairwise
from SatEncoder import commander
from SatEncoder import product
from SatEncoder import sequential
from SatEncoder import binary

Encoders = {
    "Pairwise": pairwise.EncodeNQueens,
    "Commander": commander.EncodeNQueens,
    "Product": product.EncodeNQueens,
    "Sequential": sequential.EncodeNQueens,
    "Binary": binary.EncodeNQueens,
}

KnownSolutionCounts = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}


def CountSolutions(encodeFunc, n):
    clauses = encodeFunc(n)
    solver = Solver(name='g3', bootstrap_with=clauses)
    count = 0
    while solver.solve():
        model = solver.get_model()
        mainLits = [lit for lit in model if 1 <= abs(lit) <= n * n]
        solver.add_clause([-lit for lit in mainLits])
        count += 1
    solver.delete()
    return count


def IsValidBoard(board):
    n = len(board)
    queens = [(r, c) for r in range(n) for c in range(n) if board[r][c]]
    if len(queens) != n:
        return False
    for i in range(len(queens)):
        for j in range(i + 1, len(queens)):
            r1, c1 = queens[i]
            r2, c2 = queens[j]
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                return False
    return True


def DecodeBoard(model, n):
    trueVars = set(lit for lit in model if lit > 0)
    return [[1 if (r * n + c + 1) in trueVars else 0 for c in range(n)] for r in range(n)]


def CheckOneSolutionValid(encodeFunc, n):
    clauses = encodeFunc(n)
    solver = Solver(name='g3', bootstrap_with=clauses)
    sat = solver.solve()
    board = DecodeBoard(solver.get_model(), n) if sat else None
    solver.delete()
    if n <= 3:
        return sat is False
    return sat and IsValidBoard(board)


if __name__ == '__main__':
    allOk = True

    print("Number of result (Have to match solutions)")
    for encoderName, encodeFunc in Encoders.items():
        print(f"\n{encoderName}")
        for n, expected in KnownSolutionCounts.items():
            got = CountSolutions(encodeFunc, n)
            ok = got == expected
            allOk = allOk and ok
            print(f"  N={n:<2} number={got:<4} expected={expected:<4} {'OK' if ok else 'WRONG !!'}")

    print("\nCheck ìf the result is valid (For N in range from 4 to 10 )")
    for encoderName, encodeFunc in Encoders.items():
        print(f"\n{encoderName}")
        for n in range(4, 11):
            ok = CheckOneSolutionValid(encodeFunc, n)
            allOk = allOk and ok
            print(f"  N={n:<2} {'OK' if ok else 'SAI !!'}")

    print("\n" + ("Everything is right" if allOk else "ERROR"))
