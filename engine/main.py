from board_manager import BoardManager
from board_viewer import BoardViewer
from logger import ChessLogger

manager = BoardManager()    
chessLogger = ChessLogger()
viewer = BoardViewer(manager, logger=chessLogger)
viewer.run()      
viewer.refresh(process_events=True)
