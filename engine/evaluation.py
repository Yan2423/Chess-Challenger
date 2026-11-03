import chess


# Valores das peças(em centipões: 100 = 1 peão)

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


# PIECE-SQUARE TABLES (PST) - MEIO-JOGO
# (do ponto de vista das Brancas; índice 0 = a8 ... índice 63 = h1)

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDDLEGAME_TABLE = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

PST_MAP = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_MIDDLEGAME_TABLE
}


# PIECE-SQUARE TABLES (PST) - FINAL DE JOGO

# Peão: avançar vale cada vez mais (promoção)
PAWN_ENDGAME_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    80, 80, 80, 80, 80, 80, 80, 80,
    50, 50, 50, 50, 50, 50, 50, 50,
    30, 30, 30, 30, 30, 30, 30, 30,
    20, 20, 20, 20, 20, 20, 20, 20,
    10, 10, 10, 10, 10, 10, 10, 10,
    10, 10, 10, 10, 10, 10, 10, 10,
     0,  0,  0,  0,  0,  0,  0,  0
]

# Cavalo: no final, a borda é ainda mais penalizada
KNIGHT_ENDGAME_TABLE = [
   -60,-45,-35,-30,-30,-35,-45,-60,
   -45,-25, -5,  0,  0, -5,-25,-45,
   -35, -5, 10, 15, 15, 10, -5,-35,
   -30,  0, 15, 25, 25, 15,  0,-30,
   -30,  0, 15, 25, 25, 15,  0,-30,
   -35, -5, 10, 15, 15, 10, -5,-35,
   -45,-25, -5,  0,  0, -5,-25,-45,
   -60,-45,-35,-30,-30,-35,-45,-60
]

BISHOP_ENDGAME_TABLE = [
   -15,-10,-10,-10,-10,-10,-10,-15,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  8, 10, 10,  8,  0,-10,
   -10,  0, 10, 15, 15, 10,  0,-10,
   -10,  0, 10, 15, 15, 10,  0,-10,
   -10,  0,  8, 10, 10,  8,  0,-10,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -15,-10,-10,-10,-10,-10,-10,-15
]

# Torre: valoriza a 7ª fileira (e a 8ª) no final
ROOK_ENDGAME_TABLE = [
    10, 10, 10, 10, 10, 10, 10, 10,
    10, 10, 10, 10, 10, 10, 10, 10,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0
]

# Dama: centralização
QUEEN_ENDGAME_TABLE = [
   -20,-10, -5, -5, -5, -5,-10,-20,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  5, 10, 10, 10, 10,  5, -5,
    -5,  5, 10, 15, 15, 10,  5, -5,
    -5,  5, 10, 15, 15, 10,  5, -5,
    -5,  5, 10, 10, 10, 10,  5, -5,
   -10,  0,  5,  5,  5,  5,  0,-10,
   -20,-10, -5, -5, -5, -5,-10,-20
]

# Rei: no final ele deve ir para o centro e participar do jogo
KING_ENDGAME_TABLE = [
   -50,-40,-30,-20,-20,-30,-40,-50,
   -30,-20,-10,  0,  0,-10,-20,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-30,  0,  0,  0,  0,-30,-30,
   -50,-30,-30,-30,-30,-30,-30,-50
]

PST_MAP_ENDGAME = {
    chess.PAWN: PAWN_ENDGAME_TABLE,
    chess.KNIGHT: KNIGHT_ENDGAME_TABLE,
    chess.BISHOP: BISHOP_ENDGAME_TABLE,
    chess.ROOK: ROOK_ENDGAME_TABLE,
    chess.QUEEN: QUEEN_ENDGAME_TABLE,
    chess.KING: KING_ENDGAME_TABLE
}


# FASE DA PARTIDA (meio-jogo <-> final)
# Peso de cada peça: Cavalo=1, Bispo=1, Torre=2, Dama=4 (total inicial = 24).
# 24 = meio-jogo completo | 0 = só Reis e Peões. A avaliação é interpolada.

PHASE_WEIGHTS = {
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4
}
MAX_PHASE = 24


# PESOS DOS TERMOS POSICIONAIS (centipões)

TEMPO_BONUS = 10                       # Bônus de quem tem a vez

BISHOP_PAIR_BONUS = (30, 45)           # Par de Bispos (meio-jogo, final)
ROOK_OPEN_FILE_BONUS = 20              # Torre em coluna aberta
ROOK_SEMI_OPEN_FILE_BONUS = 10         # Torre em coluna semiaberta

# Peão passado, indexado pela fileira relativa ao dono (0..7)
PASSED_PAWN_BONUS_MG = [0, 5, 10, 20, 35, 60, 100, 0]
PASSED_PAWN_BONUS_EG = [0, 10, 20, 40, 70, 120, 200, 0]

# Mobilidade: (casas "esperadas", peso por casa acima/abaixo do esperado)
MOBILITY_WEIGHTS = {
    chess.KNIGHT: (4, 4),
    chess.BISHOP: (6, 4),
    chess.ROOK: (7, 2),
    chess.QUEEN: (13, 1)
}

# Segurança do Rei
KING_OPEN_FILE_PENALTY = 14            # Coluna do Rei (ou vizinha) sem peão amigo
KING_ATTACK_UNITS = {                  # Peso de cada peça inimiga que ataca a zona do Rei
    chess.KNIGHT: 2,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 5
}
KING_DANGER_CAP = 100


def _extract_board(board_input) -> chess.Board:
    """Extrai a instância interna de chess.Board se o parâmetro for um BoardManager."""
    if hasattr(board_input, 'board') and isinstance(board_input.board, chess.Board):
        return board_input.board
    return board_input

# int.bit_count existe no Python 3.10+; abaixo disso usa o método antigo.
_popcount = int.bit_count if hasattr(int, "bit_count") else (lambda bb: bin(bb).count("1"))

def _blend(mg_score: int, eg_score: int, phase: int) -> int:
    #Interpola entre meio-jogo (phase=24) e final (phase=0)
    return (mg_score * phase + eg_score * (MAX_PHASE - phase)) // MAX_PHASE

_scan = chess.scan_forward
_WHITE, _BLACK = chess.WHITE, chess.BLACK


# TABELAS PRÉ-CALCULADAS (feitas uma única vez, ao importar o módulo)

_PIECE_TYPES = (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING)

# PST já indexada pela casa REAL (evita square_mirror a cada avaliação)
_PST_MG = {_WHITE: {}, _BLACK: {}}
_PST_EG = {_WHITE: {}, _BLACK: {}}
for _pt in _PIECE_TYPES:
    _PST_MG[_WHITE][_pt] = tuple(PST_MAP[_pt][chess.square_mirror(s)] for s in range(64))
    _PST_MG[_BLACK][_pt] = tuple(PST_MAP[_pt][s] for s in range(64))
    _PST_EG[_WHITE][_pt] = tuple(PST_MAP_ENDGAME[_pt][chess.square_mirror(s)] for s in range(64))
    _PST_EG[_BLACK][_pt] = tuple(PST_MAP_ENDGAME[_pt][s] for s in range(64))

# Máscaras de colunas vizinhas (f-1 e f+1) e das 3 colunas centradas em f
_ADJ_FILES = []
_FILES3 = []
for _f in range(8):
    _adj = 0
    for _g in (_f - 1, _f + 1):
        if 0 <= _g <= 7:
            _adj |= chess.BB_FILES[_g]
    _ADJ_FILES.append(_adj)
    _FILES3.append(_adj | chess.BB_FILES[_f])
_KING_FILE_MASKS = [
    tuple(chess.BB_FILES[g] for g in range(max(0, _f - 1), min(8, _f + 2))) for _f in range(8)
]

# Máscara de "peão passado": colunas f-1..f+1 nas fileiras À FRENTE do peão
_PASSED_MASK = {_WHITE: [0] * 64, _BLACK: [0] * 64}
for _s in range(64):
    _f, _r = chess.square_file(_s), chess.square_rank(_s)
    for _rr in range(_r + 1, 8):
        _PASSED_MASK[_WHITE][_s] |= _FILES3[_f] & chess.BB_RANKS[_rr]
    for _rr in range(0, _r):
        _PASSED_MASK[_BLACK][_s] |= _FILES3[_f] & chess.BB_RANKS[_rr]

# Bônus de passado já interpolado por fase: _PASSED_BLEND[fase][fileira relativa]
_PASSED_BLEND = [
    [_blend(PASSED_PAWN_BONUS_MG[r], PASSED_PAWN_BONUS_EG[r], p) for r in range(8)]
    for p in range(MAX_PHASE + 1)
]

# Peças que entram na mobilidade: (tipo, esperado, peso)
_MOBILITY_LIST = [(pt, exp, w) for pt, (exp, w) in MOBILITY_WEIGHTS.items()]
_KING_ATTACK_LIST = list(KING_ATTACK_UNITS.items())


def game_phase(board: chess.Board) -> int:
    #Fase da partida pelo material restante: 24 = meio-jogo cheio, 0 = só Reis e Peões
    phase = (_popcount(board.knights) + _popcount(board.bishops)
             + 2 * _popcount(board.rooks) + 4 * _popcount(board.queens))
    return phase if phase < MAX_PHASE else MAX_PHASE


# ESTRUTURA DE PEÕES (com cache por configuração de peões)

_PAWN_CACHE = {}
_PAWN_CACHE_MAX = 200_000

def _pawn_info(pawns: int, enemy_pawns: int, color: bool):
    """
    Parte da estrutura de peões que NÃO depende da fase:
    (penalidades de dobrados/isolados, tupla de fileiras relativas dos passados).
    """
    score = 0
    # Dobrados: mais de um peão na mesma coluna
    for f in range(8):
        count = _popcount(pawns & chess.BB_FILES[f])
        if count > 1:
            score -= (count - 1) * 20

    passed_ranks = []
    masks = _PASSED_MASK[color]
    for sq in _scan(pawns):
        # Isolado: nenhum peão amigo nas colunas vizinhas
        if not (pawns & _ADJ_FILES[sq & 7]):
            score -= 15
        # Passado: nenhum peão inimigo à frente (na coluna ou nas vizinhas)
        if not (enemy_pawns & masks[sq]):
            rank = sq >> 3
            passed_ranks.append(rank if color == _WHITE else 7 - rank)
    return score, tuple(passed_ranks)

def _pawn_structure_cached(white_pawns: int, black_pawns: int):
    key = (white_pawns, black_pawns)
    info = _PAWN_CACHE.get(key)
    if info is None:
        if len(_PAWN_CACHE) >= _PAWN_CACHE_MAX:
            _PAWN_CACHE.clear()
        info = (_pawn_info(white_pawns, black_pawns, _WHITE),
                _pawn_info(black_pawns, white_pawns, _BLACK))
        _PAWN_CACHE[key] = info
    return info

def evaluate_pawn_structure(board: chess.Board, color: chess.Color, phase: int = MAX_PHASE) -> int:
    #Penalidades de peões dobrados e isolados e bônus de peões passados para uma cor
    white_info, black_info = _pawn_structure_cached(board.pieces_mask(chess.PAWN, _WHITE),
                                                    board.pieces_mask(chess.PAWN, _BLACK))
    base, ranks = white_info if color == _WHITE else black_info
    blend = _PASSED_BLEND[phase]
    return base + sum(blend[r] for r in ranks)


def evaluate_king_safety(board: chess.Board, color: chess.Color, phase: int = MAX_PHASE) -> int:
    #Roque, escudo de peões, colunas abertas e ataques ao redor do rei
    #O resultado é ponderado pela fase: importa no meio-jogo e some no final
    if phase == 0:
        return 0  # (score * 0) // 24 == 0: nem precisa calcular
    king_sq = board.king(color)
    if king_sq is None:
        return 0

    king_file = king_sq & 7
    king_rank = king_sq >> 3
    own_pawns = board.pieces_mask(chess.PAWN, color)
    score = 0

    # Bônus por se manter nas alas de roque (G1/C1 para Brancas, G8/C8 para Pretas)
    if color == _WHITE:
        if king_sq == chess.G1 or king_sq == chess.C1:
            score += 30
    elif king_sq == chess.G8 or king_sq == chess.C8:
        score += 30

    # Escudo de peões: fileira à frente do rei, colunas f-1..f+1
    forward_rank = king_rank + 1 if color == _WHITE else king_rank - 1
    if 0 <= forward_rank <= 7:
        score += 10 * _popcount(own_pawns & _FILES3[king_file] & chess.BB_RANKS[forward_rank])

    # Penalidade por colunas (do rei e vizinhas) sem nenhum peão amigo
    for file_mask in _KING_FILE_MASKS[king_file]:
        if not (own_pawns & file_mask):
            score -= KING_OPEN_FILE_PENALTY

    # Ataques inimigos à zona do rei (só conta com 2 ou mais atacantes)
    king_zone = board.attacks_mask(king_sq) | chess.BB_SQUARES[king_sq]
    attack_units = 0
    attackers = 0
    enemy = not color
    for piece_type, units in _KING_ATTACK_LIST:
        for enemy_sq in _scan(board.pieces_mask(piece_type, enemy)):
            if board.attacks_mask(enemy_sq) & king_zone:
                attack_units += units
                attackers += 1
    if attackers >= 2:
        score -= min(KING_DANGER_CAP, attack_units ** 2 // 2)

    return score * phase // MAX_PHASE

def evaluate_mobility(board: chess.Board, color: chess.Color) -> int:
    #Mobilidade básica: casas atacadas (e não ocupadas por peça própria) por Cavalo, Bispo, Torre e Dama
    score = 0
    not_own = ~board.occupied_co[color]
    attacks_mask = board.attacks_mask
    for piece_type, expected, weight in _MOBILITY_LIST:
        for sq in _scan(board.pieces_mask(piece_type, color)):
            score += (_popcount(attacks_mask(sq) & not_own) - expected) * weight
    return score

def evaluate_pieces(board: chess.Board, color: chess.Color, phase: int = MAX_PHASE) -> int:
    #Par de Bispos e Torres em colunas abertas/semiabertas
    score = 0

    if _popcount(board.pieces_mask(chess.BISHOP, color)) >= 2:
        score += _blend(BISHOP_PAIR_BONUS[0], BISHOP_PAIR_BONUS[1], phase)

    own_pawns = board.pieces_mask(chess.PAWN, color)
    enemy_pawns = board.pieces_mask(chess.PAWN, not color)
    for sq in _scan(board.pieces_mask(chess.ROOK, color)):
        file_mask = chess.BB_FILES[sq & 7]
        if not (own_pawns & file_mask):
            if not (enemy_pawns & file_mask):
                score += ROOK_OPEN_FILE_BONUS
            else:
                score += ROOK_SEMI_OPEN_FILE_BONUS

    return score


# CACHE DE AVALIAÇÃO
# A avaliação só depende de onde estão as peças e de quem joga (não de roque,
# en passant ou relógio), então essa chave é barata e suficiente.

_EVAL_CACHE = {}
_EVAL_CACHE_MAX = 500_000

def clear_eval_caches() -> None:
    """Esvazia os caches (útil ao iniciar uma nova partida ou em testes)."""
    _EVAL_CACHE.clear()
    _PAWN_CACHE.clear()

def evaluate_static(board_input) -> int:
    board = _extract_board(board_input)

    occ_w = board.occupied_co[_WHITE]
    occ_b = board.occupied_co[_BLACK]
    turn = board.turn
    key = (occ_w, occ_b, board.pawns, board.knights, board.bishops,
           board.rooks, board.queens, turn)
    cached = _EVAL_CACHE.get(key)
    if cached is not None:
        return cached

    phase = game_phase(board)

    # Material e Piece-Square Tables (PST), por tipo de peça via bitboards
    bbs = (board.pawns, board.knights, board.bishops, board.rooks, board.queens, board.kings)
    totals = []
    for color, occ in ((_WHITE, occ_w), (_BLACK, occ_b)):
        material = 0
        pst_mg = pst_eg = 0
        mg_tables = _PST_MG[color]
        eg_tables = _PST_EG[color]
        for pt, bb in zip(_PIECE_TYPES, bbs):
            mask = bb & occ
            if not mask:
                continue
            material += PIECE_VALUES[pt] * _popcount(mask)
            mg = mg_tables[pt]
            eg = eg_tables[pt]
            for sq in _scan(mask):
                pst_mg += mg[sq]
                pst_eg += eg[sq]
        totals.append(material + _blend(pst_mg, pst_eg, phase))
    white_score, black_score = totals

    # Estrutura de Peões (dobrados, isolados e passados) — cache por peões
    (w_base, w_passed), (b_base, b_passed) = _pawn_structure_cached(
        board.pawns & occ_w, board.pawns & occ_b)
    blend = _PASSED_BLEND[phase]
    white_score += w_base + sum([blend[r] for r in w_passed])
    black_score += b_base + sum([blend[r] for r in b_passed])

    # Segurança do Rei
    white_score += evaluate_king_safety(board, _WHITE, phase)
    black_score += evaluate_king_safety(board, _BLACK, phase)

    # Mobilidade
    white_score += evaluate_mobility(board, _WHITE)
    black_score += evaluate_mobility(board, _BLACK)

    # Par de Bispos e Torres em colunas abertas
    white_score += evaluate_pieces(board, _WHITE, phase)
    black_score += evaluate_pieces(board, _BLACK, phase)

    # Bônus de tempo para quem tem a vez
    if turn == _WHITE:
        white_score += TEMPO_BONUS
    else:
        black_score += TEMPO_BONUS

    result = white_score - black_score

    if len(_EVAL_CACHE) >= _EVAL_CACHE_MAX:
        _EVAL_CACHE.clear()
    _EVAL_CACHE[key] = result
    return result

def evaluate(board_input) -> int:
    """
    Avalia a posição do tabuleiro em centipões (100 = 1 peão)
    
    Retorna:
      - Valor positivo: Vantagem para as Brancas
      - Valor negativo: Vantagem para as Pretas
    """
    board = _extract_board(board_input)

    # Fim de jogo e xeque-mate
    if board.is_checkmate():
        return -20000 if board.turn == chess.WHITE else 20000

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    return evaluate_static(board)


if __name__ == "__main__":
    from board_manager import BoardManager

    manager = BoardManager()
    
    # Exemplo testando diretamente com a classe BoardManager
    print("Avaliação na Posição Inicial:", evaluate(manager))

    # Executando um lance e reavaliando
    manager.make_move_uci("e2e4")
    print("Avaliação após e2e4:", evaluate(manager))