# engine/logger.py
import os
from datetime import datetime

class ChessLogger:
    def __init__(self, filename="partida_log.txt"):
        self.filename = filename
        # Cria ou limpa o arquivo no início da partida
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(f"--- Nova Partida: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    def log_search(self, move_number: int, color: str, uci_move: str, depth: int, 
                 nodes: int, evaluation: str, pv: str, time_spent: float):
        """
        número do lance, cor, lance UCI, profundidade, nós, avaliação, PV e tempo.
        """
        log_line = (
            f"Lance: {move_number} | Cor: {color} | Lance (UCI): {uci_move} | "
            f"Prof: {depth} | Nós: {nodes} | Eval: {evaluation} | "
            f"PV: {pv} | Tempo: {time_spent:.2f}s\n"
        )
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(log_line)