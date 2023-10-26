'''
Storing information about current state of the game.
Determining valid moves at current state
Keep a move log
'''

class GameState():
    def __init__(self):

        # 9x9 board
        # '--' is empty space, K->King, G->Gold general, S->Silver general, N->Knight, L->Lance, R->Rook, B->Bishop, p->Pawn
        # O->Promoted Rook, H->Promoted Bishop
        self.board = [
            ['bL', 'bN', 'bS', 'bG', 'bK', 'bG', 'bS', 'bN', 'bL'],
            ['--', 'bR', '--', '--', '--', '--', '--', 'bB', '--'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['--', 'wB', '--', '--', '--', '--', '--', 'wR', '--'],
            ['wL', 'wN', 'wS', 'wG', 'wK', 'wG', 'wS', 'wN', 'wL']]

        self.whiteToMove = True
        self.moveLog = []

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'B': self.getBishopMoves, 'L': self.getLanceMoves, 'N': self.getKnightMoves,
                              'S': self.getSilvGenMoves, 'G': self.getGoldGenMoves, 'K': self.getKingMoves, 'O': self.getPromRookMoves, 'H': self.getPromBishopMoves }

        self.whiteKingLocation = (8,4)
        self.blackKingLocation = (0,4)

        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)   #To save the moves so that we can undo later
        self.whiteToMove = not self.whiteToMove     #swap players

        #Update kings location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #Promotion to Gold General
        if move.isPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'G'

        #Rook promotion
        if move.isRookPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'O'

        #Bishop promotion
        if move.isBishopPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'H'



    #Undo the last move
    def undoMove(self):
        #Pop the last move and execute the move previous to it
        if len(self.moveLog) != 0:
            #print(self.moveLog)
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove     #switch turns back
            #Update king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

        self.checkMate = False
        self.staleMate = False

    '''
        All moves considering checks
        '''
    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1, -1, -1):   #Traverse from back so that no moves are missed
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])      #Remove invalid move from available moves list
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:     #No valid moves available
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False


        return moves


    '''
    If the current player is in check position 
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):    #Rows
            for c in range(len(self.board[r])):     #Columns
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves


    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:    #White pawn moves
            if self.board[r-1][c] == '--':
                moves.append(Move((r, c), (r-1, c), self.board))
            if self.board[r-1][c][0] == 'b':
                moves.append(Move((r, c), (r-1, c), self.board))

        else:    #Black pawn moves
            if self.board[r+1][c] == '--':
                moves.append(Move((r, c), (r+1, c), self.board))
            if self.board[r+1][c][0] == 'w':
                moves.append(Move((r, c), (r+1, c), self.board))


    def getRookMoves(self, r, c, moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1))     #Up, left, down, right
        if self.whiteToMove:
            enemy_color = 'b'
        else:
            enemy_color = 'w'
        for d in directions:
            for i in range(1,9):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':    #Blank space
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    elif endPiece[0] == enemy_color:   #Enemy piece
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                        break
                    else:
                        break   #Users piece
                else:
                    break   #Moves outside the board


    def getPromRookMoves(self, r, c, moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1))     #Up, left, down, right
        if self.whiteToMove:
            enemy_color = 'b'
        else:
            enemy_color = 'w'
        for d in directions:
            for i in range(1,9):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':    #Blank space
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    elif endPiece[0] == enemy_color:   #Enemy piece
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                        break
                    else:
                        break   #Users piece
                else:
                    break   #Move outside the board

        if self.whiteToMove:
            userColor = 'w'
            promRookMoves = ((-1, -1), (-1, 1), (1, -1), (1, 1))
            for i in range(4):
                endRow = r + promRookMoves[i][0]
                endCol = c + promRookMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

        else:
            userColor = 'b'
            promRookMoves = ((-1, -1), (-1, 1), (1, -1), (1, 1))
            for i in range(4):
                endRow = r + promRookMoves[i][0]
                endCol = c + promRookMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))




    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # Four corners
        if self.whiteToMove:
            enemy_color = 'b'
        else:
            enemy_color = 'w'
        for d in directions:
            for i in range(1, 9):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # Blank space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # Users piece
                else:
                    break  # Move outside the board


    def getPromBishopMoves(self, r, c, moves):
        if self.whiteToMove:
            userColor = 'w'
            promBishopMoves = ((-1, 0), (1, 0), (0, -1), (0, 1))
            for i in range(4):
                endRow = r + promBishopMoves[i][0]
                endCol = c + promBishopMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

        else:
            userColor = 'b'
            promBishopMoves = ((-1, 0), (1, 0), (0, -1), (0, 1))
            for i in range(4):
                endRow = r + promBishopMoves[i][0]
                endCol = c + promBishopMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

        ####
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # Diagonals
        if self.whiteToMove:
            enemy_color = 'b'
        else:
            enemy_color = 'w'
        for d in directions:
            for i in range(1, 9):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # Blank space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # Users piece
                else:
                    break  # Move outside the board

    def getLanceMoves(self, r, c, moves):
        if self.whiteToMove:
            enemyColor = 'b'
            for i in range(1, 9):
                endRow = r + (-1) * i
                endCol = c
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # Blank space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # Users piece
                else:
                    break

        else:
            enemyColor = 'w'
            for i in range(1, 9):
                endRow = r + 1 * i
                endCol = c
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # Blank space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # Users piece
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        if self.whiteToMove:
            knightMoves = ((-2,-1), (-2,1))
            userColor = 'w'
            for m in knightMoves:
                endRow = r + m[0]
                endCol = c + m[1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
        else:
            knightMoves = ((2, -1), (2, 1))
            userColor = 'b'
            for m in knightMoves:
                endRow = r + m[0]
                endCol = c + m[1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    def getSilvGenMoves(self, r, c, moves):
        if self.whiteToMove:
            userColor = 'w'
            silvGenMoves = ((-1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1))
            for i in range(5):
                endRow = r + silvGenMoves[i][0]
                endCol = c + silvGenMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

        else:
            userColor = 'b'
            silvGenMoves = ((1, 0), (1, -1), (1, 1), (-1, -1), (-1, 1))
            for i in range(5):
                endRow = r + silvGenMoves[i][0]
                endCol = c + silvGenMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getGoldGenMoves(self, r, c, moves):
        if self.whiteToMove:
            userColor = 'w'
            goldGenMoves = ((-1, 0), (-1, -1), (-1, 1), (0, -1), (0, 1),(1,0))
            for i in range(6):
                endRow = r + goldGenMoves[i][0]
                endCol = c + goldGenMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

        else:
            userColor = 'b'
            silvGenMoves = ((1, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1,0))
            for i in range(6):
                endRow = r + silvGenMoves[i][0]
                endCol = c + silvGenMoves[i][1]
                if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != userColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1,0),(1,0),(-1,1),(1,1),(0,1),(-1,-1),(0,-1),(1,-1))
        if  self.whiteToMove:
            userColor = 'w'
        else:
            userColor = 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow <= 8 and 0 <= endCol <= 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != userColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

class Move():


    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPromotion = False
        self.isRookPromotion = False
        self.isBishopPromotion = False
        if ((self.pieceMoved == 'wp' or self.pieceMoved == 'wS' or self.pieceMoved == 'wL' or self.pieceMoved == 'wN') and self.endRow <= 2 and self.endRow >=0) \
                or ((self.pieceMoved == 'bp' or self.pieceMoved == 'bS' or self.pieceMoved == 'bL' or self.pieceMoved == 'bN') and self.endRow <= 8 and self.endRow >=6):
            self.isPromotion = True

        if (self.pieceMoved == 'wR'  and self.endRow <= 2 and self.endRow >=0) \
                or (self.pieceMoved == 'bR'  and self.endRow <= 8 and self.endRow >=6):
            self.isRookPromotion = True

        if (self.pieceMoved == 'wB'  and self.endRow <= 2 and self.endRow >=0) \
                or (self.pieceMoved == 'bB'  and self.endRow <= 8 and self.endRow >=6):
            self.isBishopPromotion = True

        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    def __eq__(self, other):        #Compares object to other object
        if isinstance(other, Move):     #To make sure that this move is the instance of the move class and not make a move if not equal
            return self.moveId == other.moveId
        return False

