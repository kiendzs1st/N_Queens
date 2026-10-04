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


def AmoBinary(literals, nextVarTracker=None):
    n = len(literals)
    if n <= 1:
        return []
    if n <= 3:
        return AmoPairwise(literals)

    if nextVarTracker is None:
        nextVarTracker = [max(literals) + 1]

    clauses = []

    k = math.ceil(math.log2(n))

    bitVars = [nextVarTracker[0] + j for j in range(k)]
    nextVarTracker[0] += k

    for i, lit in enumerate(literals):
        for j in range(k):
            isBitSet = (i >> j) & 1
            if isBitSet:
                clauses.append([-lit, bitVars[j]])
            else:
                clauses.append([-lit, -bitVars[j]])

    return clauses


def EncodeNQueens(boardSize):
    clauses = []
    nextVarTracker = [boardSize * boardSize + 1]

    for r in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for c in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoBinary(lits, nextVarTracker=nextVarTracker))

    for c in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for r in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoBinary(lits, nextVarTracker=nextVarTracker))

    for k in range(-boardSize + 1, boardSize):
        lits = [GetVariableIndex(r, r - k, boardSize) for r in range(boardSize) if 0 <= r - k < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoBinary(lits, nextVarTracker=nextVarTracker))

    for k in range(2 * boardSize - 1):
        lits = [GetVariableIndex(r, k - r, boardSize) for r in range(boardSize) if 0 <= k - r < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoBinary(lits, nextVarTracker=nextVarTracker))

    return clauses