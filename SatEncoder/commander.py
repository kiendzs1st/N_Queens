def GetVariableIndex(row, col, boardSize):
    return row * boardSize + col + 1


def AmoPairwise(literals):
    clauses = []
    litsCount = len(literals)
    for i in range(litsCount):
        for j in range(i + 1, litsCount):
            clauses.append([-literals[i], -literals[j]])
    return clauses


def AmoCommander(literals, groupSize=3, nextVarTracker=None):
    if len(literals) <= 1:
        return []
    if len(literals) <= groupSize:
        return AmoPairwise(literals)

    if nextVarTracker is None:
        nextVarTracker = [max(literals) + 1]

    clauses = []
    groups = [literals[i:i + groupSize] for i in range(0, len(literals), groupSize)]
    commanders = []

    for grp in groups:
        cmd = nextVarTracker[0]
        nextVarTracker[0] += 1
        commanders.append(cmd)

        clauses.extend(AmoPairwise(grp))
        clauses.append([-cmd] + grp)
        for x in grp:
            clauses.append([cmd, -x])

    clauses.extend(AmoCommander(commanders, groupSize, nextVarTracker))
    return clauses


def EncodeNQueens(boardSize):
    clauses = []
    nextVarTracker = [boardSize * boardSize + 1]

    for r in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for c in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoCommander(lits, nextVarTracker=nextVarTracker))

    for c in range(boardSize):
        lits = [GetVariableIndex(r, c, boardSize) for r in range(boardSize)]
        clauses.append(lits)
        clauses.extend(AmoCommander(lits, nextVarTracker=nextVarTracker))

    for k in range(-boardSize + 1, boardSize):
        lits = [GetVariableIndex(r, r - k, boardSize) for r in range(boardSize) if 0 <= r - k < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoCommander(lits, nextVarTracker=nextVarTracker))

    for k in range(2 * boardSize - 1):
        lits = [GetVariableIndex(r, k - r, boardSize) for r in range(boardSize) if 0 <= k - r < boardSize]
        if len(lits) > 1:
            clauses.extend(AmoCommander(lits, nextVarTracker=nextVarTracker))

    return clauses
