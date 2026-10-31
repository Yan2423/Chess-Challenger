"""
engine/search.py — Busca de lances: Negamax + Alpha-Beta, aprofundamento
iterativo, ordenação de lances e busca de quiescência.

Visão geral
-----------
* `Searcher.search()` roda o aprofundamento iterativo (profundidade 1, 2, 3...).
  A cada profundidade completa guardamos o melhor lance; se o tempo acabar no
  meio de uma iteração, ela é descartada e jogamos o resultado da anterior.
* `_negamax` é um Negamax com poda alfa-beta, estendido com:
    - tabela de transposição (TT) com limites EXACT/LOWER/UPPER;
    - extensão de xeque;
    - null-move pruning;
    - PVS (janela nula nos lances não-primeiros) + LMR (redução de lances tardios);
    - detecção de empate (repetição, 50 lances, material insuficiente).
* Ordenação: lance da TT > capturas (MVV-LVA) > promoções > killers > história.
* `_quiescence` resolve capturas pendentes (e evasões de xeque) antes de
  chamar a avaliação estática, mitigando o efeito horizonte.

Scores: centipeões do ponto de vista de quem joga. Mate em N plies vale
`MATE_SCORE - N` (mates mais rápidos pontuam mais).

Integração com o projeto: `search()` recebe um `BoardManager` ou um
`chess.Board`. A avaliação vem de `evaluation.evaluate_static` (convenção
"positivo = Brancas"), convertida aqui para "quem joga".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import chess
import chess.polyglot

# Funciona tanto como pacote (engine/) quanto com os arquivos na mesma pasta.
try:
    from .evaluation import PIECE_VALUES, evaluate_static
    from .time_manager import SearchTimeout, TimeManager, as_board
except ImportError:  # layout plano: evaluation.py / time_manager.py ao lado
    from evaluation import PIECE_VALUES, evaluate_static
    from time_manager import SearchTimeout, TimeManager, as_board

# Score de xeque-mate da BUSCA (independente do ±20000 de evaluation.evaluate,
# que só é usado fora da busca). Precisa ser maior que qualquer avaliação.
MATE_SCORE = 100_000


def evaluate(board: chess.Board) -> int:
    """
    Avaliação para o Negamax: do ponto de vista de QUEM JOGA.

    O evaluation.py do projeto devolve o score do ponto de vista das Brancas;
    aqui apenas invertemos o sinal quando a vez é das Pretas. Usamos
    `evaluate_static` (sem checagem de fim de jogo), pois a busca já detecta
    mate, afogamento e empates por conta própria.
    """
    score = evaluate_static(board)
    return score if board.turn == chess.WHITE else -score


INF = 1_000_000
MAX_PLY = 64
MATE_BOUND = MATE_SCORE - MAX_PLY  # scores >= isto são "mate em N"

# Flags da tabela de transposição
TT_EXACT, TT_LOWER, TT_UPPER = 0, 1, 2

# Prioridades de ordenação (maiores = tentados primeiro)
SCORE_TT_MOVE = 1_000_000
SCORE_CAPTURE = 100_000
SCORE_PROMOTION = 95_000
SCORE_KILLER_1 = 90_000
SCORE_KILLER_2 = 89_000

# Margem usada na poda "delta" da quiescência (cp)
DELTA_MARGIN = 200
# Verifica o relógio a cada (CHECK_INTERVAL + 1) nós
CHECK_INTERVAL = 2047
# Limite de entradas da TT (limpa quando excede, estratégia simples)
TT_MAX_ENTRIES = 1_000_000


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    best_move: Optional[chess.Move]
    score: int = 0
    depth: int = 0
    nodes: int = 0
    elapsed: float = 0.0
    pv: List[chess.Move] = field(default_factory=list)

    @property
    def nps(self) -> int:
        return int(self.nodes / self.elapsed) if self.elapsed > 0 else 0


def format_score(score: int) -> str:
    """Formata o score no estilo UCI: 'cp 35' ou 'mate 3' (negativo = sofrendo mate)."""
    if score >= MATE_BOUND:
        return f"mate {(MATE_SCORE - score + 1) // 2}"
    if score <= -MATE_BOUND:
        return f"mate -{(MATE_SCORE + score + 1) // 2}"
    return f"cp {score}"


# Callback opcional: (depth, score, nodes, elapsed, pv)
InfoCallback = Callable[[int, int, int, float, List[chess.Move]], None]


# ---------------------------------------------------------------------------
# Busca
# ---------------------------------------------------------------------------

class Searcher:
    def __init__(self) -> None:
        self.tt: Dict[int, Tuple[int, int, int, Optional[chess.Move]]] = {}
        self.killers: List[List[Optional[chess.Move]]] = [[None, None] for _ in range(MAX_PLY + 2)]
        self.history: Dict[Tuple[bool, int, int], int] = {}
        self.nodes = 0
        self._tm: Optional[TimeManager] = None

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def new_game(self) -> None:
        """Limpa TT e heurísticas (chame ao iniciar uma nova partida)."""
        self.tt.clear()
        self.history.clear()

    def search(
        self,
        board: chess.Board,
        time_manager: Optional[TimeManager] = None,
        max_depth: int = MAX_PLY,
        info_callback: Optional[InfoCallback] = None,
    ) -> SearchResult:
        """
        Aprofundamento iterativo a partir de `board`.

        O `time_manager` deve ter tido `start*/()` chamado ANTES (ele é quem
        inicia o relógio). Sem time_manager, a busca só para em `max_depth`.
        O tabuleiro recebido NÃO é modificado (trabalhamos numa cópia).
        """
        self._tm = time_manager
        self.nodes = 0
        self.killers = [[None, None] for _ in range(MAX_PLY + 2)]
        # Envelhece o histórico para não "congelar" ordenações antigas.
        for key in self.history:
            self.history[key] //= 2
        if len(self.tt) > TT_MAX_ENTRIES:
            self.tt.clear()

        # Aceita BoardManager ou chess.Board; trabalha numa cópia (com a pilha de
        # lances, para detectar repetições) e nunca altera o tabuleiro original.
        work = as_board(board).copy(stack=True)
        root_moves = list(work.legal_moves)
        if not root_moves:
            return SearchResult(best_move=None, score=-MATE_SCORE if work.is_check() else 0)

        # Fallback: se nem a profundidade 1 terminar, joga o melhor pela ordenação.
        root_moves.sort(key=lambda m: self._move_score(work, m, None, 0), reverse=True)
        result = SearchResult(best_move=root_moves[0])

        start_nodes_time = time_manager.elapsed() if time_manager else 0.0
        max_depth = min(max_depth, MAX_PLY)

        for depth in range(1, max_depth + 1):
            if depth > 1 and time_manager and not time_manager.should_start_new_iteration():
                break
            try:
                move, score = self._search_root(work, depth, result.best_move)
            except SearchTimeout:
                break  # descarta a iteração incompleta

            elapsed = (time_manager.elapsed() - start_nodes_time) if time_manager else 0.0
            result = SearchResult(
                best_move=move,
                score=score,
                depth=depth,
                nodes=self.nodes,
                elapsed=elapsed,
                pv=self._extract_pv(work, depth),
            )
            if info_callback:
                info_callback(depth, score, self.nodes, elapsed, result.pv)

            # Mate encontrado: não adianta aprofundar mais.
            if abs(score) >= MATE_BOUND:
                break

        result.nodes = self.nodes
        return result

    # ------------------------------------------------------------------
    # Controle de tempo
    # ------------------------------------------------------------------
    def _check_time(self) -> None:
        if self._tm is not None and (self.nodes & CHECK_INTERVAL) == 0 and self._tm.time_up():
            raise SearchTimeout

    # ------------------------------------------------------------------
    # Raiz
    # ------------------------------------------------------------------
    def _search_root(
        self, board: chess.Board, depth: int, prev_best: Optional[chess.Move]
    ) -> Tuple[chess.Move, int]:
        if self._tm is not None and self._tm.time_up():
            raise SearchTimeout

        moves = self._ordered_moves(board, prev_best, 0)
        alpha, beta = -INF, INF
        best_move, best_score = moves[0], -INF

        for i, move in enumerate(moves):
            board.push(move)
            if i == 0:
                score = -self._negamax(board, depth - 1, -beta, -alpha, 1)
            else:
                score = -self._negamax(board, depth - 1, -alpha - 1, -alpha, 1)  # janela nula
                if alpha < score < beta:
                    score = -self._negamax(board, depth - 1, -beta, -alpha, 1)
            board.pop()

            if score > best_score:
                best_score, best_move = score, move
            if score > alpha:
                alpha = score

        # Guarda o lance da raiz na TT para extração da PV.
        self._tt_store(chess.polyglot.zobrist_hash(board), depth, TT_EXACT, best_score, best_move, 0)
        return best_move, best_score

    # ------------------------------------------------------------------
    # Negamax com poda alfa-beta
    # ------------------------------------------------------------------
    def _negamax(
        self,
        board: chess.Board,
        depth: int,
        alpha: int,
        beta: int,
        ply: int,
        allow_null: bool = True,
    ) -> int:
        self.nodes += 1
        self._check_time()

        # --- Empates por regra (não aplicáveis à raiz) ---
        if board.is_repetition(2) or board.halfmove_clock >= 100 or board.is_insufficient_material():
            return 0
        if ply >= MAX_PLY:
            return evaluate(board)

        in_check = board.is_check()
        if in_check:
            depth += 1  # extensão de xeque

        if depth <= 0:
            return self._quiescence(board, alpha, beta, ply)

        # --- Consulta à tabela de transposição ---
        key = chess.polyglot.zobrist_hash(board)
        tt_move = None
        entry = self.tt.get(key)
        if entry is not None:
            e_depth, e_flag, e_score, tt_move = entry
            if e_depth >= depth:
                e_score = self._score_from_tt(e_score, ply)
                if e_flag == TT_EXACT:
                    return e_score
                if e_flag == TT_LOWER and e_score >= beta:
                    return e_score
                if e_flag == TT_UPPER and e_score <= alpha:
                    return e_score

        # --- Null-move pruning ---
        # "Passa a vez": se mesmo assim a posição supera beta, poda.
        # Desativado em xeque, sem peças pesadas (risco de zugzwang) e em
        # zonas de mate.
        if (
            allow_null
            and not in_check
            and depth >= 3
            and beta < MATE_BOUND
            and self._has_non_pawn_material(board, board.turn)
        ):
            reduction = 3 if depth > 6 else 2
            board.push(chess.Move.null())
            score = -self._negamax(board, depth - 1 - reduction, -beta, -beta + 1, ply + 1, False)
            board.pop()
            if score >= beta:
                return beta

        # --- Geração e ordenação dos lances ---
        moves = self._ordered_moves(board, tt_move, ply)
        if not moves:
            return -MATE_SCORE + ply if in_check else 0  # mate ou afogamento

        orig_alpha = alpha
        best_score = -INF
        best_move: Optional[chess.Move] = None

        for i, move in enumerate(moves):
            is_capture = board.is_capture(move)
            gives_check = board.gives_check(move)
            board.push(move)

            if i == 0:
                score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
            else:
                # LMR: reduz lances silenciosos tardios.
                reduction = 0
                if depth >= 3 and i >= 4 and not is_capture and not gives_check \
                        and not in_check and move.promotion is None:
                    reduction = 1
                # PVS: busca com janela nula; re-busca só se necessário.
                score = -self._negamax(board, depth - 1 - reduction, -alpha - 1, -alpha, ply + 1)
                if score > alpha and reduction:
                    score = -self._negamax(board, depth - 1, -alpha - 1, -alpha, ply + 1)
                if alpha < score < beta:
                    score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
            board.pop()

            if score > best_score:
                best_score, best_move = score, move
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        if not is_capture:
                            self._record_cutoff(board, move, depth, ply)
                        break

        # --- Grava na TT ---
        if best_score <= orig_alpha:
            flag = TT_UPPER
        elif best_score >= beta:
            flag = TT_LOWER
        else:
            flag = TT_EXACT
        self._tt_store(key, depth, flag, best_score, best_move, ply)
        return best_score

    # ------------------------------------------------------------------
    # Quiescence search
    # ------------------------------------------------------------------
    def _quiescence(self, board: chess.Board, alpha: int, beta: int, ply: int) -> int:
        """
        Só considera lances "barulhentos" (capturas), para não avaliar
        posições no meio de uma troca. Em xeque, considera todas as evasões,
        pois "stand pat" seria ilegal.
        """
        self.nodes += 1
        self._check_time()

        if ply >= MAX_PLY:
            return evaluate(board)

        in_check = board.is_check()
        if in_check:
            best = -MATE_SCORE + ply
            moves = list(board.legal_moves)
            if not moves:
                return best
        else:
            # Stand pat: quem joga pode "recusar" capturar se já está bem.
            stand_pat = evaluate(board)
            if stand_pat >= beta:
                return stand_pat
            # Poda delta global: nem capturar a dama salva a posição.
            if stand_pat + PIECE_VALUES[chess.QUEEN] + DELTA_MARGIN < alpha:
                return alpha
            if stand_pat > alpha:
                alpha = stand_pat
            best = stand_pat
            moves = list(board.generate_legal_captures())

        moves.sort(key=lambda m: self._mvv_lva(board, m), reverse=True)

        for move in moves:
            # Poda delta por lance: a captura não alcança alpha nem no melhor caso.
            if not in_check and move.promotion is None:
                victim = board.piece_type_at(move.to_square) or chess.PAWN  # en passant
                if best + PIECE_VALUES[victim] + DELTA_MARGIN < alpha:
                    continue

            board.push(move)
            score = -self._quiescence(board, -beta, -alpha, ply + 1)
            board.pop()

            if score > best:
                best = score
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        break
        return best

    # ------------------------------------------------------------------
    # Ordenação de lances
    # ------------------------------------------------------------------
    @staticmethod
    def _mvv_lva(board: chess.Board, move: chess.Move) -> int:
        """
        Most Valuable Victim – Least Valuable Attacker.
        Vítima domina o score (x10); entre vítimas iguais, o atacante mais
        barato vem primeiro. Tipos de peça: P=1 ... K=6.
        """
        if board.is_en_passant(move):
            victim = chess.PAWN
        else:
            victim = board.piece_type_at(move.to_square)
            if victim is None:  # não-captura (ex.: evasão de xeque na quiescence)
                return 0
        attacker = board.piece_type_at(move.from_square) or chess.PAWN
        score = 10 * victim - attacker
        if move.promotion:
            score += move.promotion
        return score

    def _move_score(
        self, board: chess.Board, move: chess.Move, tt_move: Optional[chess.Move], ply: int
    ) -> int:
        if move == tt_move:
            return SCORE_TT_MOVE
        if board.is_capture(move):
            return SCORE_CAPTURE + self._mvv_lva(board, move)
        if move.promotion:
            return SCORE_PROMOTION + move.promotion
        killers = self.killers[ply]
        if move == killers[0]:
            return SCORE_KILLER_1
        if move == killers[1]:
            return SCORE_KILLER_2
        return self.history.get((board.turn, move.from_square, move.to_square), 0)

    def _ordered_moves(
        self, board: chess.Board, tt_move: Optional[chess.Move], ply: int
    ) -> List[chess.Move]:
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: self._move_score(board, m, tt_move, ply), reverse=True)
        return moves

    def _record_cutoff(self, board: chess.Board, move: chess.Move, depth: int, ply: int) -> None:
        """Atualiza killers e history após um corte beta por lance silencioso."""
        # `board` já está sem o lance (pop feito) -> board.turn é quem jogou `move`.
        killers = self.killers[ply]
        if move != killers[0]:
            killers[1] = killers[0]
            killers[0] = move
        key = (board.turn, move.from_square, move.to_square)
        self.history[key] = self.history.get(key, 0) + depth * depth

    # ------------------------------------------------------------------
    # Tabela de transposição / utilidades
    # ------------------------------------------------------------------
    @staticmethod
    def _score_to_tt(score: int, ply: int) -> int:
        """Scores de mate são relativos à raiz; na TT guardamos relativos ao nó."""
        if score >= MATE_BOUND:
            return score + ply
        if score <= -MATE_BOUND:
            return score - ply
        return score

    @staticmethod
    def _score_from_tt(score: int, ply: int) -> int:
        if score >= MATE_BOUND:
            return score - ply
        if score <= -MATE_BOUND:
            return score + ply
        return score

    def _tt_store(
        self, key: int, depth: int, flag: int, score: int, move: Optional[chess.Move], ply: int
    ) -> None:
        old = self.tt.get(key)
        # Substituição: mantém a entrada mais profunda, exceto se a nova é exata.
        if old is not None and old[0] > depth and flag != TT_EXACT:
            return
        self.tt[key] = (depth, flag, self._score_to_tt(score, ply), move)

    @staticmethod
    def _has_non_pawn_material(board: chess.Board, color: bool) -> bool:
        non_pawns = board.occupied_co[color] & ~board.pawns & ~board.kings
        return non_pawns != 0

    def _extract_pv(self, board: chess.Board, max_len: int) -> List[chess.Move]:
        """Reconstrói a variante principal seguindo os lances guardados na TT."""
        pv: List[chess.Move] = []
        seen = set()
        while len(pv) < max_len:
            key = chess.polyglot.zobrist_hash(board)
            entry = self.tt.get(key)
            if entry is None or entry[3] is None or key in seen:
                break
            move = entry[3]
            if not board.is_legal(move):
                break
            seen.add(key)
            pv.append(move)
            board.push(move)
        for _ in pv:
            board.pop()
        return pv


# ---------------------------------------------------------------------------
# Atalho de uso
# ---------------------------------------------------------------------------

def find_best_move(
    board: chess.Board,
    time_manager: Optional[TimeManager] = None,
    max_depth: int = MAX_PLY,
    searcher: Optional[Searcher] = None,
    info_callback: Optional[InfoCallback] = None,
) -> SearchResult:
    """Função de conveniência: reutilize `searcher` entre lances para manter a TT."""
    searcher = searcher or Searcher()
    return searcher.search(board, time_manager, max_depth, info_callback)


def play_best_move(
    manager,
    time_manager: Optional[TimeManager] = None,
    max_depth: int = MAX_PLY,
    searcher: Optional[Searcher] = None,
    info_callback: Optional[InfoCallback] = None,
) -> SearchResult:
    """
    Busca o melhor lance para o `BoardManager` e o EXECUTA via
    `manager.make_move_uci`. Retorna o SearchResult (best_move None = sem lances).
    """
    result = find_best_move(manager, time_manager, max_depth, searcher, info_callback)
    if result.best_move is not None:
        manager.make_move_uci(result.best_move.uci())
    return result


if __name__ == "__main__":
    # Demo: a engine joga contra si mesma por alguns lances (relógio de 10 s + 0,1 s).
    from board_manager import BoardManager

    manager = BoardManager()
    searcher, tm = Searcher(), TimeManager()
    for _ in range(10):
        if manager.is_game_over():
            break
        tm.start(manager, time_left=10.0, increment=0.1)
        res = play_best_move(manager, tm, searcher=searcher)
        print(f"{res.best_move.uci():6} {format_score(res.score):>9}  prof={res.depth} "
              f"nós={res.nodes} {res.nps} n/s")
    manager.display()
