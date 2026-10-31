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

def _popcount(bitboard: int) -> int:
    #Conta quantas casas estão marcadas em um bitboard
    return bin(bitboard).count("1")

def _blend(mg_score: int, eg_score: int, phase: int) -> int:
    #Interpola entre meio-jogo (phase=24) e final (phase=0)
    return (mg_score * phase + eg_score * (MAX_PHASE - phase)) // MAX_PHASE

def game_phase(board: chess.Board) -> int:
    #Fase da partida pelo material restante: 24 = meio-jogo cheio, 0 = só Reis e Peões
    phase = 0
    for piece_type, weight in PHASE_WEIGHTS.items():
        phase += weight * (len(board.pieces(piece_type, chess.WHITE)) +
                           len(board.pieces(piece_type, chess.BLACK)))
    return min(phase, MAX_PHASE)

def evaluate_pawn_structure(board: chess.Board, color: chess.Color, phase: int = MAX_PHASE) -> int:
    #Calcula penalidades de peões dobrados e isolados e bônus de peões passados para uma cor
    score = 0
    pawns = board.pieces(chess.PAWN, color)
    enemy_pawns = board.pieces(chess.PAWN, not color)
    pawn_files = [chess.square_file(sq) for sq in pawns]

    # Penalidade para peões dobrados na mesma coluna
    for file_idx in range(8):
        count = pawn_files.count(file_idx)
        if count > 1:
            score -= (count - 1) * 20

    # Penalidade para peões isolados (sem vizinhos nas colunas adjacentes)
    for sq in pawns:
        f = chess.square_file(sq)
        if not any(adj_f in pawn_files for adj_f in (f - 1, f + 1) if 0 <= adj_f <= 7):
            score -= 15

    # Bônus para peões passados (nenhum peão inimigo à frente, na coluna ou nas vizinhas)
    for sq in pawns:
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        passed = True
        for enemy_sq in enemy_pawns:
            ef = chess.square_file(enemy_sq)
            er = chess.square_rank(enemy_sq)
            in_front = er > r if color == chess.WHITE else er < r
            if abs(ef - f) <= 1 and in_front:
                passed = False
                break
        if passed:
            relative_rank = r if color == chess.WHITE else 7 - r
            score += _blend(PASSED_PAWN_BONUS_MG[relative_rank],
                            PASSED_PAWN_BONUS_EG[relative_rank], phase)

    return score

def evaluate_king_safety(board: chess.Board, color: chess.Color, phase: int = MAX_PHASE) -> int:
    #Avalia posições de roque, escudo de peões, colunas abertas e ataques ao redor do rei
    #O resultado é ponderado pela fase: importa no meio-jogo e some no final
    score = 0
    king_sq = board.king(color)
    if king_sq is None:
        return 0

    king_file = chess.square_file(king_sq)
    king_rank = chess.square_rank(king_sq)

    # Bônus por se manter nas alas de roque (G1/C1 para Brancas, G8/C8 para Pretas)
    if color == chess.WHITE and king_sq in (chess.G1, chess.C1):
        score += 30
    elif color == chess.BLACK and king_sq in (chess.G8, chess.C8):
        score += 30

    # Escudo de Peões (Pawn Shield) à frente do rei
    forward_rank = king_rank + 1 if color == chess.WHITE else king_rank - 1
    if 0 <= forward_rank <= 7:
        for f in range(max(0, king_file - 1), min(8, king_file + 2)):
            shield_sq = chess.square(f, forward_rank)
            piece = board.piece_at(shield_sq)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                score += 10

    # Penalidade por colunas (do rei e vizinhas) sem nenhum peão amigo
    own_pawns = board.pieces_mask(chess.PAWN, color)
    for f in range(max(0, king_file - 1), min(8, king_file + 2)):
        if not (own_pawns & chess.BB_FILES[f]):
            score -= KING_OPEN_FILE_PENALTY

    # Ataques inimigos à zona do rei (casas vizinhas + a própria casa do rei)
    # Só conta como perigo quando 2 ou mais peças inimigas participam do ataque
    king_zone = board.attacks_mask(king_sq) | chess.BB_SQUARES[king_sq]
    attack_units = 0
    attackers = 0
    for piece_type, units in KING_ATTACK_UNITS.items():
        for enemy_sq in board.pieces(piece_type, not color):
            if board.attacks_mask(enemy_sq) & king_zone:
                attack_units += units
                attackers += 1
    if attackers >= 2:
        score -= min(KING_DANGER_CAP, attack_units ** 2 // 2)

    return score * phase // MAX_PHASE

def evaluate_mobility(board: chess.Board, color: chess.Color) -> int:
    #Mobilidade básica: casas atacadas (e não ocupadas por peça própria) por Cavalo, Bispo, Torre e Dama
    score = 0
    own_pieces = board.occupied_co[color]
    for piece_type, (expected, weight) in MOBILITY_WEIGHTS.items():
        for sq in board.pieces(piece_type, color):
            squares = _popcount(board.attacks_mask(sq) & ~own_pieces)
            score += (squares - expected) * weight
    return score

def evaluate_pieces(board: chess.Board, color: chess.Color, phase: int = MAX_PHASE) -> int:
    #Par de Bispos e Torres em colunas abertas/semiabertas
    score = 0

    # Par de Bispos
    if len(board.pieces(chess.BISHOP, color)) >= 2:
        score += _blend(BISHOP_PAIR_BONUS[0], BISHOP_PAIR_BONUS[1], phase)

    # Torres em colunas abertas (sem peões) ou semiabertas (sem peões amigos)
    own_pawns = board.pieces_mask(chess.PAWN, color)
    enemy_pawns = board.pieces_mask(chess.PAWN, not color)
    for sq in board.pieces(chess.ROOK, color):
        file_mask = chess.BB_FILES[chess.square_file(sq)]
        if not (own_pawns & file_mask):
            if not (enemy_pawns & file_mask):
                score += ROOK_OPEN_FILE_BONUS
            else:
                score += ROOK_SEMI_OPEN_FILE_BONUS

    return score

def evaluate_static(board_input) -> int:
    """
    Avaliação estática PURA (sem checar fim de jogo), em centipões,
    do ponto de vista das BRANCAS (positivo = vantagem das Brancas).

    Foi separada de `evaluate` para a busca (search.py) poder chamá-la
    nos nós folha sem pagar o custo de is_checkmate/is_stalemate/
    can_claim_draw a cada avaliação — a busca já trata o fim de jogo
    por conta própria.
    """
    board = _extract_board(board_input)
    phase = game_phase(board)

    white_score = 0
    black_score = 0
    white_pst_mg = white_pst_eg = 0
    black_pst_mg = black_pst_eg = 0

    # Material e Piece-Square Tables (PST) de meio-jogo e final
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = PIECE_VALUES[piece.piece_type]
        pst_mg = PST_MAP[piece.piece_type]
        pst_eg = PST_MAP_ENDGAME[piece.piece_type]

        if piece.color == chess.WHITE:
            index = chess.square_mirror(square)
            white_score += value
            white_pst_mg += pst_mg[index]
            white_pst_eg += pst_eg[index]
        else:
            black_score += value
            black_pst_mg += pst_mg[square]
            black_pst_eg += pst_eg[square]

    # Interpolação das PSTs pela fase da partida
    white_score += _blend(white_pst_mg, white_pst_eg, phase)
    black_score += _blend(black_pst_mg, black_pst_eg, phase)

    # Estrutura de Peões (dobrados, isolados e passados)
    white_score += evaluate_pawn_structure(board, chess.WHITE, phase)
    black_score += evaluate_pawn_structure(board, chess.BLACK, phase)

    # Segurança do Rei
    white_score += evaluate_king_safety(board, chess.WHITE, phase)
    black_score += evaluate_king_safety(board, chess.BLACK, phase)

    # Mobilidade
    white_score += evaluate_mobility(board, chess.WHITE)
    black_score += evaluate_mobility(board, chess.BLACK)

    # Par de Bispos e Torres em colunas abertas
    white_score += evaluate_pieces(board, chess.WHITE, phase)
    black_score += evaluate_pieces(board, chess.BLACK, phase)

    # Bônus de tempo para quem tem a vez
    if board.turn == chess.WHITE:
        white_score += TEMPO_BONUS
    else:
        black_score += TEMPO_BONUS

    return white_score - black_score

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
