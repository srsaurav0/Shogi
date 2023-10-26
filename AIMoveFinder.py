import random

pieceScores = {'K': 0, 'O': 15, 'H': 15, 'R': 10, 'B': 10, 'G': 5, 'S': 5, 'N': 3, 'L': 2, 'p': 1}
checkMate = 1000
staleMate = 0
DEPTH = 2

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def greedyMove(gs, validMoves):
    if gs.whiteToMove:
        turn = 1
    else:
        turn = -1

    maxScore = -checkMate
    bestMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        if gs.checkMate:
            score = checkMate
        elif gs.staleMate:
            score = staleMate
        else:
            score = turn * scoreValue(gs.board)
        if score > maxScore:
            maxScore = score
            bestMove = playerMove
        gs.undoMove()
    return bestMove

def scoreValue(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScores[square[1]]
            elif square[0] == 'b':
                score -= pieceScores[square[1]]

    return score

def findBestMoveAlphaBetaPruning(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)      #To get first move variation
    findMoveAlphaBetaPruning(gs, validMoves, DEPTH, -checkMate, checkMate, 1 if gs.whiteToMove else -1)
    #print(nextMove)
    return nextMove

def findMoveAlphaBetaPruning(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove

    if depth == 0:      #Return value when at the bottom of the depth
        return turnMultiplier * scoreBoard(gs)

    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveAlphaBetaPruning(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:  # To get the move at the very last evaluation
                nextMove = move
        gs.undoMove()       #Move is made for calculation, so undo is needed
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -checkMate
        else:
            return checkMate
    elif gs.staleMate:
        return staleMate

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScores[square[1]]
            elif square[0] == 'b':
                score -= pieceScores[square[1]]
    return score


