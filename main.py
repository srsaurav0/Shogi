import pygame as p
import ShogiEngine
import AIMoveFinder

width = height = 760    #Shogi board height and width
dimension = 9   #Shogi board dimensions
sq_size = height//dimension     #Square size
max_fps = 15    #For animation

IMAGES = {}

'''
Initialization of a dictionary of images
'''
def loadImages():
    pieces = ['wp','wB','wR','wL','wN','wS','wG','wK','wO','wH','bp','bB','bR','bL','bN','bS','bG','bK','bO','bH']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+ piece + ".png"),(sq_size,sq_size))


'''
Main driver.
Handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((width,height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ShogiEngine.GameState()

    validMoves = gs.getValidMoves()     #Get valid moves
    moveMade = False    #Flag variable for when a move is made
    animate = False     #Initially no animation

    loadImages()
    running = True      #To declear the beginning and end of the game
    sqSelected = ()     #To get desired square
    playerClicks = []   #Initial and final click location

    gameOver = False    #To stop the moves

    playerOne = True    #True if human, false if AI
    playerTwo = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()    #(x,y) coordinates of the mouse
                    col = location[0]//sq_size
                    row = location[1]//sq_size
                    if sqSelected == (row,col):     #Same row and column selected
                        sqSelected = ()     #deselect
                        playerClicks = []   #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)     #Append first and second click

                    if len(playerClicks) == 2:  #After second click
                        move = ShogiEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        #print(move.getShogiNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()     #Reset user click
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            #To undo a move or restart the game
            elif e.type == p.KEYDOWN:
                keys = p.key.get_pressed()
                if keys[p.K_z] and keys[p.K_LCTRL]:     #For undoing the last move
                    if playerOne and playerTwo:
                        gs.undoMove()
                        moveMade = True
                        animate = False
                        gameOver = False
                    else:
                        gs.undoMove()
                        gs.undoMove()   #Case handled in movelog
                        moveMade = True
                        animate = False
                        gameOver = False

                if e.key == p.K_r:
                    gs = ShogiEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI move using algorithm
        if not gameOver and not humanTurn:
            AIMove = AIMoveFinder.findBestMoveAlphaBetaPruning(gs, validMoves)
            # if AIMove is None:
            #     AIMove = AIMoveFinder.findRandomMove(validMoves)
            # print(AIMove)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate!')
            else:
                drawText(screen, 'White wins by checkmate!')

        elif gs.staleMate:
            if gs.whiteToMove:
                drawText(screen, 'Black wins by stalemate!')
            else:
                drawText(screen, 'White wins by stalemate!')

        clock.tick(max_fps)
        p.display.flip()



'''
Highlights piece moves
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  #A piece that can be moved
            #Highlight selected squares
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(150)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*sq_size, r*sq_size))
            #Highlight moves from that square
            s.fill(p.Color('violet'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*sq_size,move.endRow*sq_size))



'''
Functions for graphics in the game
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)   #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board)     #draw pieces on the board


def drawBoard(screen):
    colors = [p.Color("white"),p.Color("light green")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c)%2)]   #Coloring the board squares
            p.draw.rect(screen,color,p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))


def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece!= '--':
                #Show the pieces in the board
                screen.blit(IMAGES[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))


def drawText(screen, text):     #When the game ends with checkmate or stalemate
    font = p.font.SysFont('Calibri', 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, height, width).move(width/2 - textObject.get_width()/2, height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

def animateMove(move, screen, board, clock):
    colors = [p.Color("red"),p.Color("light blue")]
    dr = move.endRow - move.startRow
    dc = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dr)+abs(dc)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dr * frame/frameCount, move.startCol + dc*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #Erase piece from its initial space
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*sq_size,move.endRow*sq_size,sq_size,sq_size)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece into rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        #Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*sq_size, r*sq_size,sq_size,sq_size))
        p.display.flip()
        clock.tick(60)

main()

