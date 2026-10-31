from board_manager import BoardManager
from board_viewer import BoardViewer
manager = BoardManager()
viewer = BoardViewer(manager)
viewer.run()      
viewer.refresh(process_events=True)