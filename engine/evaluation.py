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


# PIECE-SQUARE TABLES (PST)

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

def _extract_board(board_input) -> chess.Board:
    """Extrai a instância interna de chess.Board se o parâmetro for um BoardManager."""
    if hasattr(board_input, 'board') and isinstance(board_input.board, chess.Board):
        return board_input.board
    return board_input

def evaluate_pawn_structure(board: chess.Board, color: chess.Color) -> int:
    #Calcula penalidades de peões dobrados e isolados para uma cor
    score = 0
    pawns = board.pieces(chess.PAWN, color)
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

    return score

def evaluate_king_safety(board: chess.Board, color: chess.Color) -> int:
    #Avalia posições de roque e escudo de peões ao redor do rei
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

    return score

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

    white_score = 0
    black_score = 0

    # Material e Piece-Square Tables (PST)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = PIECE_VALUES[piece.piece_type]
        pst = PST_MAP[piece.piece_type]

        if piece.color == chess.WHITE:
            pst_score = pst[chess.square_mirror(square)]
            white_score += value + pst_score
        else:
            pst_score = pst[square]
            black_score += value + pst_score

    # Estrutura de Peões
    white_score += evaluate_pawn_structure(board, chess.WHITE)
    black_score += evaluate_pawn_structure(board, chess.BLACK)

    # Segurança do Rei
    white_score += evaluate_king_safety(board, chess.WHITE)
    black_score += evaluate_king_safety(board, chess.BLACK)

    return white_score - black_score


if __name__ == "__main__":
    from board_manager import BoardManager

    manager = BoardManager()
    
    # Exemplo testando diretamente com a classe BoardManager
    print("Avaliação na Posição Inicial:", evaluate(manager))

    # Executando um lance e reavaliando
    manager.make_move_uci("e2e4")
    print("Avaliação após e2e4:", evaluate(manager))