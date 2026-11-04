from engine.board_manager import BoardManager
from engine.board_viewer import BoardViewer
from engine.logger import ChessLogger

manager = BoardManager() 
chessLogger = ChessLogger()
viewer = BoardViewer(manager, logger=chessLogger)
viewer.refresh(process_events=True)
viewer.run() 
