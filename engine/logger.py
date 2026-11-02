import os
from datetime import datetime
from typing import List, Optional, Tuple

class ChessLogger:
    def __init__(self, filename: str = "partida_log.txt", archive: bool = True):
        self.filename = os.path.abspath(filename)
        self.archive = archive
        self._header = ""
        self._entries: List[Tuple[int, str]] = []   # (ply do lance, linha de texto)
        self.new_game()

    # ------------------------------------------------------------------
    # Ciclo de vida da partida
    # ------------------------------------------------------------------
    def new_game(self, fen: Optional[str] = None) -> None:
        """Começa um log limpo. Se o anterior tinha lances, ele é arquivado."""
        self._archive_current()
        self._entries.clear()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._header = f"--- Nova Partida: {stamp} ---\n"
        if fen:
            self._header += f"FEN inicial: {fen}\n"
        self._rewrite()

    def truncate_to(self, ply_count: int) -> None:
        """
        Mantém só os lances da engine anteriores a `ply_count` (len(move_stack)
        atual do tabuleiro). Chame depois de desfazer lances.
        """
        kept = [(ply, line) for ply, line in self._entries if ply < ply_count]
        if len(kept) != len(self._entries):
            self._entries = kept
            self._rewrite()

    # ------------------------------------------------------------------
    # Registro
    # ------------------------------------------------------------------
    def log_search(self, move_number: int, color: str, uci_move: str, depth: int, nodes: int, evaluation: str, pv: str, time_spent: float, ply: Optional[int] = None):
        log_line = (
            f"Lance: {move_number} | Cor: {color} | Lance (UCI): {uci_move} | "
            f"Prof: {depth} | Nós: {nodes} | Eval: {evaluation} | "
            f"PV: {pv} | Tempo: {time_spent:.2f}s\n"
        )
        if ply is None:
            ply = self._entries[-1][0] + 1 if self._entries else 0
        self._entries.append((ply, log_line))
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(log_line)

    def log_opponent_move(self, move_number: int, color: str, uci_move: str,
                          ply: Optional[int] = None):
        """
        Registra um lance NÃO feito pela engine (adversário/humano). Não há busca
        associada, então só entram número, cor e lance UCI. Assim o log mostra a
        partida completa, na ordem em que os lances ocorreram.
        """
        log_line = (
            f"Lance: {move_number} | Cor: {color} | Lance (UCI): {uci_move} | "
            f"Origem: Adversário\n"
        )
        if ply is None:
            ply = self._entries[-1][0] + 1 if self._entries else 0
        self._entries.append((ply, log_line))
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(log_line)

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _rewrite(self) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self._header)
            f.writelines(line for _, line in self._entries)

    def _archive_current(self) -> None:
        """Move o log atual para um nome com data/hora, se ele tiver algum lance."""
        if not self.archive or not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                has_moves = any(line.startswith("Lance:") for line in f)
            if not has_moves:
                return  # só cabeçalho: pode sobrescrever
            base, ext = os.path.splitext(self.filename)
            stamp = datetime.fromtimestamp(os.path.getmtime(self.filename)).strftime("%Y%m%d_%H%M%S")
            dest, n = f"{base}_{stamp}{ext}", 1
            while os.path.exists(dest):
                dest, n = f"{base}_{stamp}_{n}{ext}", n + 1
            os.replace(self.filename, dest)
        except OSError:
            pass  # se não der para arquivar, apenas sobrescreve