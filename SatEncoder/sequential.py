def GetVariableIndex(row, col, boardSize):
    return row * boardSize + col + 1


def AmoPairwise(literals):
    clauses = []
    litsCount = len(literals)
    for i in range(litsCount):
        for j in range(i + 1, litsCount):
            clauses.append([-literals[i], -literals[j]])
    return clauses


def AmoSequential(literals, nextVarTracker=None):
    n = len(literals)
    if n <= 1:
        return []
    if n == 2:
        return AmoPairwise(literals)

    if nextVarTracker is None:
        nextVarTracker = [max(literals) + 1]

    clauses = []

    sVars = [nextVarTracker[0] + i for i in range(n - 1)]
    nextVarTracker[0] += (n - 1)

    clauses.append([-literals[0], sVars[0]])

    for i in range(1, n - 1):
        clauses.append([-literals[i], sVars[i]])
        clauses.append([-sVars[i - 1], sVars[i]])
        clauses.append([-sVars[i - 1], -literals[i]])

    clauses.append([-sVars[n - 2], -literals[n - 1]])

    return clauses


def EncodeNQueens(boardSize):
    clauses = []
    nextVarTracker = [boardSize * boardSize + 1]

    for r in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for c in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoSequential(lits, nextVarTracker=nextVarTracker))

    for c in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for r in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoSequential(lits, nextVarTracker=nextVarTracker))

    for k in range(-boardSize + 1, boardSize):
        lits = [GetVariableIndex(r, r - k, boardSize) for r in range(boardSize) if 0 <= r - k < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoSequential(lits, nextVarTracker=nextVarTracker))

    for k in range(2 * boardSize - 1):
        lits = [GetVariableIndex(r, k - r, boardSize) for r in range(boardSize) if 0 <= k - r < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoSequential(lits, nextVarTracker=nextVarTracker))

    return clauses
