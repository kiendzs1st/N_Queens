import math


def GetVariableIndex(row, col, boardSize):
    return row * boardSize + col + 1


def AmoPairwise(literals):
    clauses = []
    litsCount = len(literals)
    for i in range(litsCount):
        for j in range(i + 1, litsCount):
            clauses.append([-literals[i], -literals[j]])
    return clauses


def AmoProduct(literals, nextVarTracker=None):
    n = len(literals)
    if n <= 1:
        return []
    if n <= 3:
        return AmoPairwise(literals)

    if nextVarTracker is None:
        nextVarTracker = [max(literals) + 1]

    clauses = []

    p = math.ceil(math.sqrt(n))
    q = math.ceil(n / p)

    uVars = [nextVarTracker[0] + i for i in range(p)]
    nextVarTracker[0] += p

    vVars = [nextVarTracker[0] + j for j in range(q)]
    nextVarTracker[0] += q

    clauses.extend(AmoPairwise(uVars))
    clauses.extend(AmoPairwise(vVars))

    for index, lit in enumerate(literals):
        r = index // q
        c = index % q
        clauses.append([-lit, uVars[r]])
        clauses.append([-lit, vVars[c]])

    return clauses


def EncodeNQueens(boardSize):
    clauses = []
    nextVarTracker = [boardSize * boardSize + 1]

    for r in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for c in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoProduct(lits, nextVarTracker=nextVarTracker))

    for c in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for r in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoProduct(lits, nextVarTracker=nextVarTracker))

    for k in range(-boardSize + 1, boardSize):
        lits = [GetVariableIndex(r, r - k, boardSize) for r in range(boardSize) if 0 <= r - k < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoProduct(lits, nextVarTracker=nextVarTracker))

    for k in range(2 * boardSize - 1):
        lits = [GetVariableIndex(r, k - r, boardSize) for r in range(boardSize) if 0 <= k - r < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoProduct(lits, nextVarTracker=nextVarTracker))

    return clauses
