import chess

class BoardManager:

    # Dicionário de conversão para Português
    NOME_PECAS_PT = {
        chess.PAWN: "Peão",
        chess.KNIGHT: "Cavalo",
        chess.BISHOP: "Bispo",
        chess.ROOK: "Torre",
        chess.QUEEN: "Dama",
        chess.KING: "Rei"
    }

    # Tabela de tradução das letras do tabuleiro (Inglês -> Português)
    TABELA_TRADUCAO = str.maketrans({
        'N': 'C', 'n': 'c',
        'R': 'T', 'r': 't',
        'Q': 'D', 'q': 'd',
        'K': 'R', 'k': 'r'
        # 'P', 'p', 'B', 'b' já são iguais em ambos os idiomas
    })

    def __init__(self, fen=None):
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()


    def get_piece_at_pt(self, uci_square):
        
        #Consulta uma casa específica e retorna o nome da peça em português com sua cor.
        
        try:
            square = chess.parse_square(uci_square)
            piece = self.board.piece_at(square)
            
            if piece:
                cor = "Branco(a)" if piece.color == chess.WHITE else "Preto(a)"
                nome = self.NOME_PECAS_PT.get(piece.piece_type, "Desconhecida")
                return f"{nome} {cor}"
            return "Casa vazia"
        except ValueError:
            return "Casa inválida"

    def get_legal_moves(self):
        #Fornece a lista de todos os lances legais possíveis no turno atual
        return [move.uci() for move in self.board.legal_moves]

    def make_move_uci(self, uci_string):
        #Converte a notação UCI digitada para comando interno e atualiza o tabuleiro
        try:
            move = chess.Move.from_uci(uci_string)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                return False
        except ValueError:
            #Erro Caso a Notação seja invalida
            return False
        
    def undo_move(self):

        if len(self.board.move_stack) > 0:
            return self.board.pop()
        return None
    
    def get_game_end_state(self):
        #Verifica os estados de fim de jogo: Xeque-mate, Empates variados, etc.

        if not self.board.is_game_over():
            return None
        if self.board.is_checkmate():
            return "Xeque-mate"
        elif self.board.is_stalemate():
            return "Empate por Rei Afogado (Stalemate)"
        elif self.board.is_insufficient_material():
            return "Empate por Material Insuficiente"
        elif self.board.can_claim_fifty_moves() or self.board.is_fifty_moves():
            return "Empate pela regra dos 50 lances"
        elif self.board.can_claim_threefold_repetition() or self.board.is_repetition():
            return "Empate por Tripla Repetição"
        else:
            return "Fim de jogo (Motivo desconhecido)"

    def is_game_over(self):
        #Retorna booleano indicando se o jogo acabou
        return self.board.is_game_over()

    def get_fen(self):
        #Retorna o estado atual do tabuleiro em notação FEN
        return self.board.fen()

    def display(self):
        #Imprime o tabuleiro no console traduzido para letras em Português
        # Pega a string original do tabuleiro em inglês
        tabuleiro_ingles = str(self.board)
        # Aplica a tradução simultânea usando a tabela
        tabuleiro_pt = tabuleiro_ingles.translate(self.TABELA_TRADUCAO)
        
        print("\n=== Tabuleiro ===")
        print(tabuleiro_pt)
        print("=================\n")

if __name__ == "__main__":
    manager = BoardManager()
    
    print("Estado inicial:")
    manager.display()
    
    print("Lances legais disponíveis:", manager.get_legal_moves()[:5], "...")
    
    # Executando um lance UCI
    lance_usuario = "e2e4"
    if manager.make_move_uci(lance_usuario):
        print(f"Lance {lance_usuario} executado com sucesso.")
    else:
        print(f"Lance {lance_usuario} inválido.")
        
    manager.display()
    
    # Checando fim de jogo
    estado = manager.get_game_end_state()
    if estado:
        print(f"Jogo finalizado: {estado}")
    else:
        print("O jogo continua.")