"""
engine/time_manager.py — Gestão do relógio e do tempo por lance.

Ideia central
-------------
Cada lance recebe um *orçamento* com dois limites (em segundos):

* soft: tempo "desejado". Antes de iniciar uma nova iteração do
  aprofundamento iterativo, a busca pergunta `should_start_new_iteration()`;
  se o tempo gasto já passou de uma fração do soft, ela para e joga o melhor
  lance da última profundidade completa.
* hard: limite absoluto. A busca consulta `time_up()` periodicamente e, se
  estourou, aborta imediatamente (levantando `SearchTimeout`).

Também suporta: tempo fixo por lance (movetime), busca infinita e
interrupção externa via `stop()` (ex.: comando "stop" do protocolo UCI,
chamado a partir de outra thread).

Todas as unidades de tempo públicas são SEGUNDOS (float), exceto
`start_from_uci`, que recebe milissegundos como no protocolo UCI.
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

import chess


def as_board(obj) -> chess.Board:
    """Aceita um BoardManager (atributo `.board`) ou um chess.Board puro."""
    inner = getattr(obj, "board", None)
    return inner if isinstance(inner, chess.Board) else obj


class SearchTimeout(Exception):
    """Levantada pela busca quando o limite hard é atingido ou `stop()` é chamado."""


class GamePhase(Enum):
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"


@dataclass(frozen=True)
class TimeBudget:
    """Orçamento de tempo de um lance (segundos). `math.inf` = sem limite."""
    soft: float
    hard: float


class TimeManager:
    # Quantos lances ainda esperamos jogar, por fase (usado quando o servidor
    # não informa `moves_to_go`).
    EXPECTED_MOVES_LEFT = {
        GamePhase.OPENING: 40,
        GamePhase.MIDDLEGAME: 28,
        GamePhase.ENDGAME: 18,
    }
    # Fator multiplicador do tempo-base: gasta menos na abertura (posições
    # conhecidas/calmas) e mais no meio-jogo (decisões críticas).
    PHASE_FACTOR = {
        GamePhase.OPENING: 0.75,
        GamePhase.MIDDLEGAME: 1.25,
        GamePhase.ENDGAME: 1.00,
    }

    INCREMENT_USAGE = 0.8          # fração do incremento que podemos gastar
    HARD_MULTIPLIER = 3.0          # hard = soft * 3 (limitado pelo relógio real)
    HARD_CLOCK_FRACTION = 0.9      # nunca gastar mais que 90% do tempo utilizável
    SOFT_ITERATION_FRACTION = 0.5  # não inicia nova profundidade após 50% do soft

    def __init__(
        self,
        move_overhead: float = 0.05,
        min_time: float = 0.02,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        """
        :param move_overhead: margem para latência de I/O/GUI (s) descontada
                              do relógio a cada lance.
        :param min_time: tempo mínimo de busca (s), mesmo em apuros de tempo.
        :param clock: função de relógio monotônico (injetável para testes).
        """
        self.move_overhead = move_overhead
        self.min_time = min_time
        self._clock = clock
        self._stop_event = threading.Event()
        self._start_time = clock()
        self.budget = TimeBudget(math.inf, math.inf)

    # ------------------------------------------------------------------
    # Fase da partida
    # ------------------------------------------------------------------
    @staticmethod
    def detect_phase(board: chess.Board) -> GamePhase:
        """
        Estima a fase pela combinação de material não-peão e nº do lance.

        Material ponderado (N=B=3, R=5, Q=9, ambas as cores); a posição
        inicial vale 62.
          * Final     : material <= 26
          * Abertura  : até o lance 10 e material >= 54
          * Meio-jogo : o restante
        """
        board = as_board(board)
        material = 0
        for pt, value in ((chess.KNIGHT, 3), (chess.BISHOP, 3),
                          (chess.ROOK, 5), (chess.QUEEN, 9)):
            material += value * (
                len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK))
            )
        if material <= 26:
            return GamePhase.ENDGAME
        if board.fullmove_number <= 10 and material >= 54:
            return GamePhase.OPENING
        return GamePhase.MIDDLEGAME

    # ------------------------------------------------------------------
    # Cálculo do orçamento
    # ------------------------------------------------------------------
    def allocate(
        self,
        board: chess.Board,
        time_left: float,
        increment: float = 0.0,
        moves_to_go: Optional[int] = None,
    ) -> TimeBudget:
        """
        Calcula (soft, hard) para o lance atual.

        :param board: chess.Board ou BoardManager.
        :param time_left: tempo restante no relógio de quem joga (s).
        :param increment: incremento por lance (s).
        :param moves_to_go: lances até o próximo controle de tempo (se houver).
        """
        phase = self.detect_phase(board)

        if moves_to_go is not None and moves_to_go > 0:
            moves_left = moves_to_go
        else:
            moves_left = self.EXPECTED_MOVES_LEFT[phase]

        # Tempo realmente utilizável: relógio menos margem de segurança.
        usable = max(0.0, time_left - self.move_overhead)
        if usable <= self.min_time:
            # Apuros de tempo: joga quase instantaneamente.
            t = max(self.min_time * 0.5, 0.001)
            return TimeBudget(soft=t, hard=max(t, usable * 0.9))

        # Tempo-base: fatia do relógio + a maior parte do incremento.
        base = usable / moves_left + increment * self.INCREMENT_USAGE
        soft = base * self.PHASE_FACTOR[phase]

        hard_cap = usable * self.HARD_CLOCK_FRACTION
        # O incremento só chega DEPOIS do lance: com relógio curto, limita o soft.
        soft = min(soft, hard_cap * (0.9 if moves_left == 1 else 0.5))
        soft = max(soft, self.min_time)
        hard = min(max(soft * self.HARD_MULTIPLIER, soft), hard_cap)
        hard = max(hard, soft)
        return TimeBudget(soft=soft, hard=hard)

    # ------------------------------------------------------------------
    # Início do relógio de busca (modos de uso)
    # ------------------------------------------------------------------
    def start(
        self,
        board: chess.Board,
        time_left: float,
        increment: float = 0.0,
        moves_to_go: Optional[int] = None,
    ) -> TimeBudget:
        """Modo relógio: calcula o orçamento e começa a contar."""
        return self._begin(self.allocate(board, time_left, increment, moves_to_go))

    def start_fixed(self, seconds: float) -> TimeBudget:
        """Modo movetime: tempo fixo; soft = hard."""
        seconds = max(seconds - self.move_overhead, self.min_time)
        return self._begin(TimeBudget(soft=seconds, hard=seconds))

    def start_infinite(self) -> TimeBudget:
        """Modo infinite/depth: sem limite de tempo (só `stop()` interrompe)."""
        return self._begin(TimeBudget(math.inf, math.inf))

    def start_from_uci(
        self,
        board: chess.Board,
        wtime: Optional[int] = None,
        btime: Optional[int] = None,
        winc: int = 0,
        binc: int = 0,
        movestogo: Optional[int] = None,
        movetime: Optional[int] = None,
        infinite: bool = False,
    ) -> TimeBudget:
        """Atalho que traduz os parâmetros de `go` do UCI (em milissegundos)."""
        board = as_board(board)
        if infinite:
            return self.start_infinite()
        if movetime is not None:
            return self.start_fixed(movetime / 1000.0)
        my_time = wtime if board.turn == chess.WHITE else btime
        my_inc = winc if board.turn == chess.WHITE else binc
        if my_time is None:
            return self.start_infinite()
        return self.start(board, my_time / 1000.0, (my_inc or 0) / 1000.0, movestogo)

    def _begin(self, budget: TimeBudget) -> TimeBudget:
        self.budget = budget
        self._stop_event.clear()
        self._start_time = self._clock()
        return budget

    # ------------------------------------------------------------------
    # Consultas feitas pela busca
    # ------------------------------------------------------------------
    def elapsed(self) -> float:
        """Segundos desde o início da busca atual."""
        return self._clock() - self._start_time

    def time_up(self) -> bool:
        """True se o limite hard estourou ou se `stop()` foi chamado."""
        return self._stop_event.is_set() or self.elapsed() >= self.budget.hard

    def should_start_new_iteration(self) -> bool:
        """
        Decide se vale começar a próxima profundidade. Cada iteração custa em
        média 2–4x a anterior; se já gastamos metade do soft, a próxima
        provavelmente não termina — melhor parar e jogar.
        """
        if self._stop_event.is_set():
            return False
        return self.elapsed() < self.budget.soft * self.SOFT_ITERATION_FRACTION

    def stop(self) -> None:
        """Interrompe a busca (thread-safe; ex.: comando UCI 'stop')."""
        self._stop_event.set()
