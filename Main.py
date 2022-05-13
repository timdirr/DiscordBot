"""
♟️ 
Input, interacts with engine, makes image
#TODO move chessMain and chessEngine in chessGame/ (causes problem when calling main) too lazy to fix for now
"""
from PIL import Image
from colorama import Fore, Style, init
import Engine as Engine
import os

class ChessGame: #now a class so it can store the gameID, and for future management
	def __init__(self, gameID):
		self.gameID = gameID
		self.spritesFolder = "chessGame/sprites/"
		self.board_filename = f"{self.spritesFolder}chessboard.png"
		self.outPath = 'chessGame/games/'
		self.logFile = f'{self.outPath}\logs\{self.gameID}.log'
		self.dimension = 8 #8 caselle
		self.sprites = {}
		self.posy = {
		#   c :  y
			1 : 409,
			2 : 353,
			3 : 297,
			4 : 241,
			5 : 185,
			6 : 129,
			7 : 73,
			8 : 17
		}
		self.posx = {
		#    r  : x
			"A" : 40,
			"B" : 96,
			"C" : 153,
			"D" : 209,
			"E" : 265,
			"F" : 321,
			"G" : 377,
			"H" : 433
		}

		if not os.path.exists(self.outPath): #make games folder if it does not exist
			print('making games folder')
			os.makedirs(self.outPath)

		if not os.path.exists(f'{self.outPath}\logs'): #create log folder inside games if not exist
			print('making logs file')
			os.makedirs(f'{self.outPath}\logs')
		
		with open(f'{self.logFile}', 'w'): #make log file
			pass
		#DO NOT USE mPrint BEFORE THIS POINT (may cause errors)


	def mPrint(self, prefix, value, p2 = ''):
		#p2 is only used by engine
		log = False
		style = Style.RESET_ALL
		if p2 != '':
			p2 = f'{Fore.YELLOW}{p2}{Fore.RESET} '

		if prefix == 'GAME':
			log = True
			col = Fore.GREEN
			
		elif prefix == 'WARN':
			log = True
			col = Fore.YELLOW
			style = Style.BRIGHT
		elif prefix == 'ERROR' or prefix == 'FATAL' or prefix == 'GAMEErr':
			log = True
			col = Fore.RED
			style = Style.BRIGHT
		elif prefix == 'DEBUG':
			col = Fore.MAGENTA
		elif prefix == 'VARS':
			col = Fore.YELLOW
			style = Style.DIM
		elif prefix == 'FUNC':
			col = Fore.LIGHTBLACK_EX
		elif prefix == 'USER':
			log = True
			col = Fore.CYAN
		else:
			col = Fore.WHITE	

		print(f'{style}{col}[{p2}{col}{prefix}] {value}{Fore.RESET}')
		if log:
			self.appendToLog(f'[{p2}{prefix}] {value}')

	def loadSprites(self) -> dict:
		"""
			Inizializza la dict sprites con le immagini delle pedine
		"""
		pieces = ["NT", "NA", "NC", "NQ", "NK", "NP", "BT", "BA", "BC", "BQ", "BK", "BP"]
		for piece in pieces:
			self.sprites[piece] = Image.open(f"{self.spritesFolder}{piece}.png").convert("RGBA")
		return self.sprites
		#possiamo accedere ad uno sprite così e.g.: sprites["BP"]

	def appendToLog(self, text) -> None:
		with open(f'{self.logFile}', 'a') as f:
			f.write(f'{text}\n')

	def drawGameState(self, boardGS, id) -> Image: #TODO if isCheck draw red square
		"""Responsible for the graphics of the game"""
		self.mPrint("DEBUG", "Generating board")

		#Drawing the pieces on the board
		boardImg = Image.open(f"{self.board_filename}").convert("RGBA")
		for c, x in enumerate(self.posx):
			for r, y in enumerate(self.posy):
				piece = boardGS[r][c]
				if (piece != "--"):
					boardImg.paste(self.sprites[piece], (self.posx[x], self.posy[y]), self.sprites[piece])
		boardImg.save(self.getOutputFile(id))
		
		self.mPrint("DEBUG", "Board Generated")
		return boardImg

	def getOutputFile(self, id:int) -> str:
		return f'{self.outPath}{id}.png'





##Only use for testing the engine
def main(): 
	cg = ChessGame(1)
	gs = Engine.GameState(1, cg)
	
	cg.loadSprites()
	

	#ask for move
	while True:
		#moveMade = False
		
		cg.drawGameState(gs.board, 1)
		#if moveMade:
		validMoves = gs.getValidMoves()

		if gs.checkMate:
			cg.mPrint('GAME', 'CHECKMATE!')
			break
		elif gs.staleMate:
			cg.mPrint('GAME', 'StaleMate!')
			break

		userMove = input("Move (A1A1): ").replace('/', '').replace(',','').replace(' ','').lower()
		if(userMove == "undo"):
			gs.undoMove()
			continue

		playerMoves = [#omg this is so confusing
			#                          rank (1)                              file (A)
			(Engine.Move.ranksToRows[userMove[1]], Engine.Move.filesToCols[userMove[0]]),
			(Engine.Move.ranksToRows[userMove[3]], Engine.Move.filesToCols[userMove[2]])
		]

		cg.mPrint("USER", playerMoves)
		
		move = Engine.Move(playerMoves[0], playerMoves[1], gs.board)
		if move in validMoves:
			cg.mPrint("GAME", f"Valid move: {move.getChessNotation()}")
			gs.makeMove(move)
			#moveMade = True
		else:
			cg.mPrint("GAMEErr", "Invalid move.")
			cg.mPrint("GAME", f"your move: {move.moveID} ({move.getChessNotation()})")


if __name__ == '__main__':
	main()