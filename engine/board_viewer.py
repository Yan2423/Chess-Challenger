"""
board_viewer.py — Visualizador gráfico do tabuleiro (Tkinter, só biblioteca padrão).

Mostra o tabuleiro com as peças, a lista com a casa atual de CADA peça
(nomes em português, vindos do BoardManager), o histórico de lances e,
opcionalmente, joga contra a engine (search.py).

Uso rápido
----------
    python board_viewer.py                 # abre a janela com uma partida nova

    # ou, dentro do seu código:
    from board_manager import BoardManager
    from board_viewer import BoardViewer

    manager = BoardManager()
    viewer = BoardViewer(manager)
    viewer.run()                           # abre a janela (bloqueia até fechar)

    # Se você mesmo controla o laço de jogo, atualize a tela após cada lance:
    manager.make_move_uci("e2e4")
    viewer.refresh(process_events=True)

Requisitos: board_manager.py na mesma pasta (ou no PYTHONPATH). Para jogar
contra a engine: search.py, time_manager.py e evaluation.py também.
No Linux, o Tkinter pode exigir o pacote do sistema `python3-tk`.
"""

import queue
import sys
import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

import chess

try:
    from board_manager import BoardManager
except ImportError as exc:  # pragma: no cover
    raise ImportError("board_viewer.py precisa do board_manager.py na mesma pasta.") from exc

# A engine é opcional: sem ela o visualizador funciona só como tabuleiro.
try:
    from search import MATE_BOUND, Searcher, format_score
    from time_manager import TimeManager
    ENGINE_OK = True
except Exception:  # noqa: BLE001
    ENGINE_OK = False

try:
    from evaluation import evaluate_static
    EVAL_OK = True
except Exception:  # noqa: BLE001
    EVAL_OK = False


# ---------------------------------------------------------------------------
# Aparência
# ---------------------------------------------------------------------------

SQUARE = 72          # tamanho de cada casa (px)
MARGIN = 26          # margem para as coordenadas (a-h / 1-8)

COLOR_LIGHT = "#f0d9b5"
COLOR_DARK = "#b58863"
COLOR_LAST_LIGHT = "#f7ec8a"
COLOR_LAST_DARK = "#dac34b"
COLOR_SELECTED = "#7fc97f"
COLOR_CHECK = "#e8605a"
COLOR_FOCUS = "#2f6fdb"

# O peão (U+265F) tem versão emoji no macOS; o seletor \ufe0e força o desenho em texto.
# No Windows/Linux o Tk desenha o seletor como um caractere extra e desloca o peão
# para fora do centro da casa, então ele só é usado no macOS.
PAWN_SUFFIX = "\ufe0e" if sys.platform == "darwin" else ""

# Glifos "cheios" para as duas cores; a cor da peça vem do preenchimento.
GLYPHS = {
    chess.PAWN: "\u265F" + PAWN_SUFFIX,
    chess.KNIGHT: "\u265E",
    chess.BISHOP: "\u265D",
    chess.ROOK: "\u265C",
    chess.QUEEN: "\u265B",
    chess.KING: "\u265A",
}
PIECE_FILL = {chess.WHITE: "#fafafa", chess.BLACK: "#1b1b1b"}
PIECE_OUTLINE = {chess.WHITE: "#2b2b2b", chess.BLACK: None}

FONT_CANDIDATES = (
    "Segoe UI Symbol", "DejaVu Sans", "Noto Sans Symbols2", "Noto Sans Symbols",
    "Apple Symbols", "Arial Unicode MS", "FreeSerif", "Symbola",
)

# Material clássico, só para o resumo exibido no painel (Rei não conta).
MATERIAL_VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                   chess.ROOK: 5, chess.QUEEN: 9}


def _pick_piece_font(root) -> str:
    available = set(tkfont.families(root))
    for family in FONT_CANDIDATES:
        if family in available:
            return family
    return "TkDefaultFont"


# ---------------------------------------------------------------------------
# Visualizador
# ---------------------------------------------------------------------------

class BoardViewer:
    def __init__(self, manager=None, root=None, flipped=False, think_time=1.0):
        """
        :param manager: BoardManager a exibir (cria um novo se None).
        :param root: janela Tk existente (cria uma nova se None).
        :param flipped: True = mostra o tabuleiro do ponto de vista das Pretas.
        :param think_time: segundos por lance da engine.
        """
        self.manager = manager or BoardManager()
        self.root = root or tk.Tk()
        self.flipped = flipped

        self.selected = None          # casa da peça selecionada para mover
        self.targets = {}             # {casa_destino: é_captura}
        self.focus_square = None      # casa destacada pela lista de peças

        # Estado da engine
        self.searcher = Searcher() if ENGINE_OK else None
        self.thinking = False
        self.search_id = 0
        self.time_manager = None
        self.search_board = None
        self.events = queue.Queue()

        self.root.title("Visualizador de Xadrez")
        self.root.resizable(False, False)
        self.piece_font = tkfont.Font(family=_pick_piece_font(self.root), size=-int(SQUARE * 0.78))
        self.coord_font = tkfont.Font(family="TkDefaultFont", size=10, weight="bold")

        self.engine_white = tk.BooleanVar(value=False)
        self.engine_black = tk.BooleanVar(value=False)
        self.think_var = tk.StringVar(value=str(think_time))

        self._build_ui()
        self.refresh()

    def run(self) -> None:
        """Entra no laço principal da janela (bloqueia até ela ser fechada)."""
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        size = 8 * SQUARE + 2 * MARGIN
        left = ttk.Frame(self.root)
        left.grid(row=0, column=0, padx=8, pady=8)
        right = ttk.Frame(self.root)
        right.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="ns")

        # --- Tabuleiro ---
        self.canvas = tk.Canvas(left, width=size, height=size, highlightthickness=0, bg="#2b2b2b")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

        # --- Painel direito ---
        self.status_var = tk.StringVar()
        ttk.Label(right, textvariable=self.status_var, font=("TkDefaultFont", 11, "bold"),
                  wraplength=330, justify="left").pack(anchor="w")
        self.eval_var = tk.StringVar()
        ttk.Label(right, textvariable=self.eval_var).pack(anchor="w")
        self.material_var = tk.StringVar()
        ttk.Label(right, textvariable=self.material_var).pack(anchor="w")
        self.engine_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.engine_var, wraplength=330, justify="left",
                  foreground="#2f6fdb").pack(anchor="w", pady=(0, 4))

        # Lista com a posição de cada peça
        ttk.Label(right, text="Posição de cada peça (clique para destacar):").pack(anchor="w")
        list_frame = ttk.Frame(right)
        list_frame.pack(fill="both", expand=True)
        self.pieces_tree = ttk.Treeview(list_frame, columns=("peca", "casa"),
                                        show="headings", height=13, selectmode="browse")
        self.pieces_tree.heading("peca", text="Peça")
        self.pieces_tree.heading("casa", text="Casa")
        self.pieces_tree.column("peca", width=210)
        self.pieces_tree.column("casa", width=60, anchor="center")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.pieces_tree.yview)
        self.pieces_tree.configure(yscrollcommand=scroll.set)
        self.pieces_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.pieces_tree.bind("<<TreeviewSelect>>", self._on_piece_selected)

        # Histórico de lances
        ttk.Label(right, text="Lances:").pack(anchor="w", pady=(6, 0))
        self.moves_text = tk.Text(right, height=5, width=42, wrap="word", state="disabled")
        self.moves_text.pack(fill="x")

        # Botões
        row1 = ttk.Frame(right)
        row1.pack(fill="x", pady=(6, 0))
        ttk.Button(row1, text="Desfazer", command=self.undo).pack(side="left", padx=(0, 4))
        ttk.Button(row1, text="Novo jogo", command=self.new_game).pack(side="left", padx=4)
        ttk.Button(row1, text="Virar", command=self.flip).pack(side="left", padx=4)

        # Controles da engine
        eng = ttk.LabelFrame(right, text="Engine")
        eng.pack(fill="x", pady=(6, 0))
        self.btn_engine_move = ttk.Button(eng, text="Jogar lance da engine", command=self.start_engine)
        self.btn_engine_move.grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        self.btn_stop = ttk.Button(eng, text="Parar", command=self.stop_engine)
        self.btn_stop.grid(row=0, column=2, sticky="e", padx=4, pady=2)
        ttk.Checkbutton(eng, text="Engine joga de Brancas", variable=self.engine_white,
                        command=self._on_engine_toggle).grid(row=1, column=0, columnspan=3, sticky="w", padx=4)
        ttk.Checkbutton(eng, text="Engine joga de Pretas", variable=self.engine_black,
                        command=self._on_engine_toggle).grid(row=2, column=0, columnspan=3, sticky="w", padx=4)
        ttk.Label(eng, text="Tempo por lance (s):").grid(row=3, column=0, sticky="w", padx=4, pady=2)
        ttk.Spinbox(eng, from_=0.1, to=60, increment=0.5, width=6,
                    textvariable=self.think_var).grid(row=3, column=1, sticky="w")
        if not ENGINE_OK:
            for child in eng.winfo_children():
                try:
                    child.state(["disabled"])
                except tk.TclError:
                    pass
            ttk.Label(eng, text="search.py/time_manager.py não encontrados.",
                      foreground="#b00020").grid(row=4, column=0, columnspan=3, padx=4)

        # FEN
        fen_row = ttk.Frame(right)
        fen_row.pack(fill="x", pady=(6, 0))
        ttk.Label(fen_row, text="FEN:").pack(side="left")
        self.fen_var = tk.StringVar()
        ttk.Entry(fen_row, textvariable=self.fen_var, width=34).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(fen_row, text="Carregar", command=self.load_fen).pack(side="left")

        self.root.bind("<Left>", lambda _e: self.undo())
        self.root.bind("<f>", lambda _e: self.flip())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Geometria
    # ------------------------------------------------------------------
    def _square_origin(self, square: int):
        f, r = chess.square_file(square), chess.square_rank(square)
        col = 7 - f if self.flipped else f
        row = r if self.flipped else 7 - r
        return MARGIN + col * SQUARE, MARGIN + row * SQUARE

    def _square_at(self, x: int, y: int):
        col, row = (x - MARGIN) // SQUARE, (y - MARGIN) // SQUARE
        if not (0 <= col <= 7 and 0 <= row <= 7):
            return None
        f = 7 - col if self.flipped else col
        r = row if self.flipped else 7 - row
        return chess.square(f, r)

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def refresh(self, process_events: bool = False) -> None:
        """Redesenha tudo a partir do estado atual do BoardManager."""
        self._draw_board()
        self._update_status()
        self._update_pieces_list()
        self._update_moves()
        self.fen_var.set(self.manager.get_fen())
        if process_events:
            self.root.update()
        else:
            self.root.update_idletasks()

    def _draw_board(self) -> None:
        c = self.canvas
        board = self.manager.board
        c.delete("all")

        last = board.peek() if board.move_stack else None
        check_square = board.king(board.turn) if board.is_check() else None

        # Casas
        for sq in chess.SQUARES:
            x, y = self._square_origin(sq)
            light = (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1
            color = COLOR_LIGHT if light else COLOR_DARK
            if last is not None and sq in (last.from_square, last.to_square):
                color = COLOR_LAST_LIGHT if light else COLOR_LAST_DARK
            if sq == self.selected:
                color = COLOR_SELECTED
            if sq == check_square:
                color = COLOR_CHECK
            c.create_rectangle(x, y, x + SQUARE, y + SQUARE, fill=color, outline=color)

        # Coordenadas
        for i in range(8):
            file_idx = 7 - i if self.flipped else i
            rank_idx = i if self.flipped else 7 - i
            c.create_text(MARGIN + i * SQUARE + SQUARE / 2, MARGIN + 8 * SQUARE + MARGIN / 2,
                          text="abcdefgh"[file_idx], fill="#dddddd", font=self.coord_font)
            c.create_text(MARGIN / 2, MARGIN + i * SQUARE + SQUARE / 2,
                          text=str(rank_idx + 1), fill="#dddddd", font=self.coord_font)

        # Peças
        for sq, piece in board.piece_map().items():
            self._draw_piece(sq, piece)

        # Destinos legais da peça selecionada: ponto (lance) ou anel (captura)
        for sq, is_capture in self.targets.items():
            x, y = self._square_origin(sq)
            cx, cy = x + SQUARE / 2, y + SQUARE / 2
            if is_capture:
                c.create_oval(x + 5, y + 5, x + SQUARE - 5, y + SQUARE - 5,
                              outline="#3b7d3b", width=5)
            else:
                r = SQUARE * 0.14
                c.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#3b7d3b", outline="")

        # Casa destacada pela lista de peças
        if self.focus_square is not None:
            x, y = self._square_origin(self.focus_square)
            c.create_rectangle(x + 2, y + 2, x + SQUARE - 2, y + SQUARE - 2,
                               outline=COLOR_FOCUS, width=4)

    def _draw_piece(self, square: int, piece: chess.Piece) -> None:
        x, y = self._square_origin(square)
        cx, cy = x + SQUARE / 2, y + SQUARE / 2 + 2
        glyph = GLYPHS[piece.piece_type]
        outline = PIECE_OUTLINE[piece.color]
        if outline:
            for dx, dy in ((-1.5, 0), (1.5, 0), (0, -1.5), (0, 1.5), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                self.canvas.create_text(cx + dx, cy + dy, text=glyph, font=self.piece_font, fill=outline)
        self.canvas.create_text(cx, cy, text=glyph, font=self.piece_font, fill=PIECE_FILL[piece.color])

    # ------------------------------------------------------------------
    # Painel
    # ------------------------------------------------------------------
    def _update_status(self) -> None:
        board = self.manager.board
        end = self.manager.get_game_end_state()
        if end:
            text = f"Fim de jogo: {end} ({board.result()})"
        else:
            side = "Brancas" if board.turn == chess.WHITE else "Pretas"
            text = f"Vez das {side} — lance {board.fullmove_number}"
            if board.is_check():
                text += " — XEQUE!"
        if self.thinking:
            text += "\nEngine pensando..."
        self.status_var.set(text)

        if EVAL_OK:
            self.eval_var.set(f"Avaliação estática: {evaluate_static(board) / 100:+.2f} (+ = Brancas)")
        else:
            self.eval_var.set("")

        totals = {chess.WHITE: 0, chess.BLACK: 0}
        for piece in board.piece_map().values():
            totals[piece.color] += MATERIAL_VALUES.get(piece.piece_type, 0)
        self.material_var.set(f"Material: Brancas {totals[chess.WHITE]} × Pretas {totals[chess.BLACK]}")

    def _update_pieces_list(self) -> None:
        """Uma linha por peça: nome em português (BoardManager) e casa atual."""
        tree = self.pieces_tree
        tree.delete(*tree.get_children())
        pieces = sorted(self.manager.board.piece_map().items(),
                        key=lambda item: (item[1].color == chess.BLACK, -item[1].piece_type, item[0]))
        for sq, _piece in pieces:
            name = chess.square_name(sq)
            tree.insert("", "end", values=(self.manager.get_piece_at_pt(name), name))

    def _update_moves(self) -> None:
        board = self.manager.board
        try:
            text = board.root().variation_san(board.move_stack)
            text = text.translate(BoardManager.TABELA_TRADUCAO)  # N->C, R->T, Q->D, K->R
        except Exception:  # noqa: BLE001
            text = " ".join(m.uci() for m in board.move_stack)
        self.moves_text.configure(state="normal")
        self.moves_text.delete("1.0", "end")
        self.moves_text.insert("1.0", text)
        self.moves_text.see("end")
        self.moves_text.configure(state="disabled")

    def _on_piece_selected(self, _event) -> None:
        selection = self.pieces_tree.selection()
        if not selection:
            return
        square_name = self.pieces_tree.item(selection[0], "values")[1]
        self.focus_square = chess.parse_square(square_name)
        self._draw_board()

    # ------------------------------------------------------------------
    # Interação humana
    # ------------------------------------------------------------------
    def _engine_controls(self, color: bool) -> bool:
        if not ENGINE_OK:
            return False
        return (self.engine_white if color == chess.WHITE else self.engine_black).get()

    def _on_click(self, event) -> None:
        if self.thinking or self.manager.is_game_over():
            return
        square = self._square_at(event.x, event.y)
        if square is None:
            return
        board = self.manager.board
        if self._engine_controls(board.turn):
            return

        self.focus_square = None
        if self.selected is not None and square in self.targets:
            self._try_move(self.selected, square)
            return

        piece = board.piece_at(square)
        if piece is not None and piece.color == board.turn:
            self.selected = square
            self.targets = {m.to_square: board.is_capture(m)
                            for m in board.legal_moves if m.from_square == square}
        else:
            self.selected, self.targets = None, {}
        self._draw_board()

    def _try_move(self, from_sq: int, to_sq: int) -> None:
        board = self.manager.board
        promotion = None
        # Se existe a versão "com promoção a Dama", o lance exige escolher a peça.
        if chess.Move(from_sq, to_sq, promotion=chess.QUEEN) in board.legal_moves:
            promotion = self._ask_promotion()
            if promotion is None:
                return
        move = chess.Move(from_sq, to_sq, promotion=promotion)
        if self.manager.make_move_uci(move.uci()):
            self.selected, self.targets = None, {}
            self._after_move()

    def _ask_promotion(self):
        win = tk.Toplevel(self.root)
        win.title("Promoção")
        win.transient(self.root)
        win.resizable(False, False)
        win.wait_visibility()
        win.grab_set()
        choice = {"piece": None}

        def pick(piece_type):
            choice["piece"] = piece_type
            win.destroy()

        ttk.Label(win, text="Promover o peão para:").pack(padx=14, pady=(10, 6))
        for piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT):
            ttk.Button(win, text=BoardManager.NOME_PECAS_PT[piece_type],
                       command=lambda p=piece_type: pick(p)).pack(fill="x", padx=14, pady=2)
        ttk.Label(win, text="").pack()
        self.root.wait_window(win)
        return choice["piece"]

    def _after_move(self) -> None:
        self.focus_square = None
        self.refresh()
        self.root.after(50, self._maybe_engine_move)

    # ------------------------------------------------------------------
    # Ações dos botões
    # ------------------------------------------------------------------
    def undo(self) -> None:
        if self.thinking:
            return
        if self.manager.undo_move() is None:
            return
        # Contra a engine, desfaz também o lance dela para devolver a vez ao humano.
        both_engines = self._engine_controls(chess.WHITE) and self._engine_controls(chess.BLACK)
        if not both_engines and self._engine_controls(self.manager.board.turn):
            self.manager.undo_move()
        self.selected, self.targets, self.focus_square = None, {}, None
        self.refresh()

    def new_game(self) -> None:
        self.stop_engine()
        self.manager.board.reset()
        if self.searcher:
            self.searcher.new_game()
        self.selected, self.targets, self.focus_square = None, {}, None
        self.engine_var.set("")
        self.refresh()
        self.root.after(50, self._maybe_engine_move)

    def flip(self) -> None:
        self.flipped = not self.flipped
        self._draw_board()

    def load_fen(self) -> None:
        fen = self.fen_var.get().strip()
        try:
            chess.Board(fen)  # valida antes de alterar o jogo atual
        except ValueError:
            messagebox.showerror("FEN inválido", "Não foi possível interpretar o FEN informado.")
            return
        self.stop_engine()
        self.manager.board.set_fen(fen)
        if self.searcher:
            self.searcher.new_game()
        self.selected, self.targets, self.focus_square = None, {}, None
        self.refresh()
        self.root.after(50, self._maybe_engine_move)

    def _on_engine_toggle(self) -> None:
        self._maybe_engine_move()

    def _on_close(self) -> None:
        self.stop_engine()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Engine (roda em thread separada para não travar a janela)
    # ------------------------------------------------------------------
    def _think_seconds(self) -> float:
        try:
            return max(0.1, float(self.think_var.get().replace(",", ".")))
        except ValueError:
            return 1.0

    def _maybe_engine_move(self) -> None:
        if (not ENGINE_OK or self.thinking or self.manager.is_game_over()
                or not self._engine_controls(self.manager.board.turn)):
            return
        self.start_engine()

    def start_engine(self) -> None:
        """Faz a engine buscar e jogar o lance da vez atual."""
        if not ENGINE_OK or self.thinking or self.manager.is_game_over():
            return
        self.search_id += 1
        search_id = self.search_id
        self.search_board = self.manager.board.copy(stack=True)
        self.selected, self.targets, self.focus_square = None, {}, None
        self.thinking = True

        self.time_manager = TimeManager()
        self.time_manager.start_fixed(self._think_seconds())
        searcher, tm, board = self.searcher, self.time_manager, self.search_board.copy(stack=True)

        def on_info(depth, score, nodes, elapsed, pv):
            self.events.put(("info", search_id, depth, score, nodes, elapsed, pv))

        def worker():
            try:
                result = searcher.search(board, tm, info_callback=on_info)
                self.events.put(("done", search_id, result))
            except Exception as exc:  # noqa: BLE001
                self.events.put(("error", search_id, exc))

        threading.Thread(target=worker, daemon=True).start()
        self.refresh()
        self.root.after(50, self._poll_engine)

    def stop_engine(self) -> None:
        """Interrompe a busca em andamento e descarta o resultado dela."""
        if self.thinking and self.time_manager is not None:
            self.time_manager.stop()
            # A thread antiga ainda usa o Searcher até perceber o stop(); damos um
            # novo à próxima busca para não haver estado compartilhado entre elas.
            self.searcher = Searcher()
        self.search_id += 1   # invalida mensagens da busca antiga
        self.thinking = False
        self.refresh()

    def _poll_engine(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                if event[1] != self.search_id:
                    continue  # mensagem de uma busca cancelada
                if event[0] == "info":
                    self._show_engine_info(*event[2:])
                elif event[0] == "done":
                    self._finish_engine(event[2])
                    return
                elif event[0] == "error":
                    self.thinking = False
                    self.refresh()
                    messagebox.showerror("Erro na engine", str(event[2]))
                    return
        except queue.Empty:
            pass
        if self.thinking:
            self.root.after(50, self._poll_engine)

    def _show_engine_info(self, depth, score, nodes, elapsed, pv) -> None:
        turn = self.search_board.turn
        text = format_score(score)
        if text.startswith("mate"):
            n = int(text.split()[1])
            shown = f"#{-n if turn == chess.BLACK else n}"
        else:
            white_pov = -score if turn == chess.BLACK else score
            shown = f"{white_pov / 100:+.2f}"
        tmp, parts = self.search_board.copy(stack=False), []
        for move in pv[:6]:
            if move not in tmp.legal_moves:
                break
            parts.append(tmp.san(move))
            tmp.push(move)
        line = " ".join(parts).translate(BoardManager.TABELA_TRADUCAO)
        self.engine_var.set(f"Prof. {depth} | {shown} | {nodes} nós | {line}")

    def _finish_engine(self, result) -> None:
        self.thinking = False
        move = result.best_move
        if move is not None:
            self.manager.make_move_uci(move.uci())
        self._after_move()


# ---------------------------------------------------------------------------

def abrir(manager=None, **kwargs) -> BoardViewer:
    """Atalho: cria a janela e entra no laço principal."""
    viewer = BoardViewer(manager, **kwargs)
    viewer.run()
    return viewer


if __name__ == "__main__":
    abrir()