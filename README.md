# ♟️ Chess-Challenger

Engine de xadrez escrita em Python, com interface gráfica em Tkinter, busca Negamax com poda alfa-beta, avaliação posicional interpolada por fase da partida e gerenciamento de tempo por lance. Jogue contra a engine, deixe-a jogar sozinha ou use o tabuleiro apenas para analisar posições.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Como usar](#como-usar)
- [Como a engine funciona](#como-a-engine-funciona)
  - [Busca](#busca-searchpy)
  - [Avaliação](#avaliação-evaluationpy)
  - [Gerenciamento de tempo](#gerenciamento-de-tempo-time_managerpy)
- [Uso como biblioteca](#uso-como-biblioteca)
- [Log das partidas](#log-das-partidas)
- [Limitações conhecidas e próximos passos](#limitações-conhecidas-e-próximos-passos)
- [Tecnologias](#tecnologias)

---

## Funcionalidades

- **Interface gráfica completa** (Tkinter, sem dependências extras): clique para mover, destaque do último lance, do xeque e dos lances legais, escolha de peça na promoção.
- **Jogue contra a engine** como Brancas, Pretas, ou deixe a engine jogar os dois lados.
- **Engine com busca moderna**: aprofundamento iterativo, tabela de transposição, null-move pruning, PVS, LMR e busca de quiescência.
- **Avaliação rica**: material, tabelas de casas (PST) de meio-jogo e final, estrutura de peões, segurança do rei, mobilidade, par de bispos e torres em colunas abertas.
- **Controle de tempo por lance** configurável na interface, com limites *soft* e *hard*.
- **Busca em thread separada**: a janela não trava enquanto a engine pensa, e é possível interromper a busca a qualquer momento.
- **Painel de informações**: avaliação, material, profundidade, nós, variante principal (PV) e lista com a casa de cada peça (em português).
- **Utilitários**: desfazer lance (também com a tecla `←`), virar o tabuleiro (tecla `F`), novo jogo e carregamento de posições via **FEN**.
- **Log de partidas** em arquivo texto com profundidade, nós, avaliação, PV e tempo de cada lance da engine.

## Estrutura do projeto

O `main.py` importa os módulos a partir do pacote `engine/`, portanto organize os arquivos assim:

```
Chess-Challenger/
├── main.py                # Ponto de entrada
├── requirements.txt       # Dependências (python-chess)
├── README.md
├── partida_log.txt        # Gerado automaticamente a cada execução
└── engine/
    ├── __init__.py
    ├── board_manager.py   # Encapsula o chess.Board (lances UCI, FEN, fim de jogo)
    ├── board_viewer.py    # Interface gráfica (Tkinter)
    ├── search.py          # Busca: Negamax + alfa-beta e heurísticas
    ├── evaluation.py      # Função de avaliação estática
    ├── time_manager.py    # Orçamento de tempo e interrupção da busca
    └── logger.py          # Registro das jogadas da engine
```

| Módulo | Responsabilidade |
|---|---|
| `board_manager.py` | Camada fina sobre `chess.Board`: executa lances em UCI, lista lances legais, detecta fim de jogo e exibe o tabuleiro no console com letras em português (C, B, T, D, R). |
| `board_viewer.py` | `BoardViewer`: desenha o tabuleiro, trata cliques, controla a engine em *thread* própria e atualiza o painel lateral. |
| `search.py` | `Searcher` e `SearchResult`: aprofundamento iterativo com todas as otimizações de busca. |
| `evaluation.py` | `evaluate` (com detecção de fim de jogo) e `evaluate_static` (usada nos nós folha da busca). |
| `time_manager.py` | `TimeManager`: calcula o orçamento por lance e sinaliza quando a busca deve parar. |
| `logger.py` | `ChessLogger`: grava uma linha por lance da engine em `partida_log.txt`. |

## Instalação

**Requisitos**

- Python 3.8 ou superior
- Tkinter (já incluído no Python para Windows e macOS)

**Passos**

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd Chess-Challenger

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

> **Linux:** o Tkinter pode exigir um pacote do sistema. No Debian/Ubuntu: `sudo apt install python3-tk`.

## Como usar

```bash
python main.py
```

A janela abre com uma partida nova. No painel **Engine** você pode:

| Controle | Ação |
|---|---|
| **Jogar lance da engine** | A engine calcula e joga um lance para o lado que está na vez. |
| **Parar** | Interrompe a busca em andamento. |
| **Engine joga de Brancas / Pretas** | A engine responde automaticamente após cada lance. Marque os dois para assistir engine contra engine. |
| **Tempo por lance (s)** | Tempo de busca por lance (de 0,1 a 60 s). Mais tempo significa maior profundidade e jogo mais forte. |

Demais controles:

| Controle | Ação |
|---|---|
| **Desfazer** / `←` | Desfaz o último lance. |
| **Virar** / `F` | Inverte a orientação do tabuleiro. |
| **Novo jogo** | Reinicia a partida e limpa a tabela de transposição. |
| **FEN → Carregar** | Carrega uma posição arbitrária (FEN inválido é rejeitado sem alterar a partida atual). |

Para jogar contra a engine como Brancas, marque apenas **"Engine joga de Pretas"** e faça o primeiro lance.

## Como a engine funciona

### Busca (`search.py`)

A função `Searcher.search()` executa **aprofundamento iterativo**: busca profundidade 1, 2, 3… e guarda o melhor lance de cada iteração completa. Se o tempo acabar no meio de uma iteração, ela é descartada e a engine joga o resultado da anterior.

O núcleo é um **Negamax com poda alfa-beta**, acrescido de:

| Técnica | Descrição |
|---|---|
| Tabela de transposição | Chave Zobrist, com limites `EXACT`, `LOWER` e `UPPER`; scores de mate normalizados por *ply*. |
| Extensão de xeque | Posições em xeque ganham +1 de profundidade. |
| Null-move pruning | Poda posições em que "passar a vez" já supera beta (desativado em xeque, sem peças pesadas e perto de mates). |
| PVS | Janela nula nos lances não-primeiros, com re-busca apenas quando necessário. |
| LMR | Reduz a profundidade de lances silenciosos tardios. |
| Quiescência | Resolve capturas (e evasões de xeque) antes de avaliar, atenuando o efeito horizonte; usa poda delta. |
| Ordenação de lances | Lance da TT > capturas (MVV-LVA) > promoções > *killers* > heurística de história. |
| Detecção de empates | Repetição, regra dos 50 lances e material insuficiente. |

Os scores são expressos em centipeões do ponto de vista de quem joga. Mates são codificados como `MATE_SCORE - N`, de modo que mates mais rápidos valem mais.

### Avaliação (`evaluation.py`)

A avaliação é dada em **centipeões** (100 = 1 peão), do ponto de vista das Brancas. Os termos de meio-jogo e final são **interpolados** conforme a fase da partida, calculada pelo material restante (24 = meio-jogo cheio, 0 = só reis e peões).

- **Material** (P=100, C=320, B=330, T=500, D=900)
- **Piece-Square Tables** separadas para meio-jogo e final
- **Estrutura de peões:** dobrados, isolados e passados (bônus crescente com o avanço)
- **Segurança do rei:** escudo de peões, colunas abertas, bônus de roque e pressão de peças inimigas sobre a zona do rei
- **Mobilidade** de cavalos, bispos, torres e damas
- **Par de bispos** e **torres em colunas abertas/semiabertas**
- **Bônus de tempo** para quem tem a vez

A busca usa `evaluate_static` nos nós folha, evitando o custo de checar fim de jogo a cada avaliação, já que a própria busca trata mate e afogamento.

### Gerenciamento de tempo (`time_manager.py`)

Cada lance recebe um orçamento com dois limites:

- **Soft:** tempo desejado. A busca não inicia uma nova profundidade após gastar metade dele.
- **Hard:** limite absoluto (até 3× o soft, limitado a 90% do relógio utilizável). Ao estourar, a busca aborta via `SearchTimeout`.

O `TimeManager` suporta relógio com incremento, tempo fixo por lance (`movetime`), busca infinita, tradução dos parâmetros `go` do protocolo UCI e interrupção externa por `stop()` (thread-safe). O tempo-base varia com a fase: gasta-se menos na abertura e mais no meio-jogo.

## Uso como biblioteca

Os módulos podem ser usados sem a interface gráfica:

```python
from engine.board_manager import BoardManager
from engine.search import Searcher, play_best_move, format_score
from engine.time_manager import TimeManager

manager = BoardManager()
searcher, tm = Searcher(), TimeManager()

while not manager.is_game_over():
    tm.start_fixed(1.0)                      # 1 segundo por lance
    result = play_best_move(manager, tm, searcher=searcher)
    print(f"{result.best_move.uci():6} {format_score(result.score):>9} "
          f"prof={result.depth} nós={result.nodes} {result.nps} n/s")

manager.display()
print(manager.get_game_end_state())
```

Para avaliar uma posição diretamente:

```python
from engine.evaluation import evaluate

manager = BoardManager("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
print(evaluate(manager))   # centipeões; positivo = vantagem das Brancas
```

## Log das partidas

A cada execução o `ChessLogger` recria o arquivo `partida_log.txt` e registra uma linha por lance da engine:

```
--- Nova Partida: 2026-11-01 09:31:12 ---
Lance: 1 | Cor: Pretas | Lance (UCI): b8c6 | Prof: 5 | Nós: 13993 | Eval: +0.09 | PV: Cc6 Cc3 Cf6 Cf3 d5 | Tempo: 0.98s
```

Campos: número do lance, cor, lance em UCI, profundidade atingida, nós visitados, avaliação (em peões), variante principal (em notação algébrica com letras em português) e tempo gasto.

> O arquivo é sobrescrito a cada nova execução. Copie-o antes de iniciar outra partida se quiser preservá-lo.

## Limitações conhecidas e próximos passos

- Não há livro de aberturas nem tablebases de finais.
- A tabela de transposição é limpa por completo ao atingir o limite de entradas (1 milhão), sem política de substituição mais refinada.
- A engine ainda não implementa o protocolo UCI completo, mas o `TimeManager` e a estrutura da busca já foram preparados para isso.
- Não há suíte de testes automatizados.

Ideias para evoluir o projeto:

- [ ] Protocolo UCI para uso em GUIs como Arena e Cutechess
- [ ] Livro de aberturas (o `python-chess` já oferece suporte a Polyglot)
- [ ] Testes automatizados (perft, posições táticas, regressão de avaliação)
- [ ] Poda por futilidade e *aspiration windows*
- [ ] Seleção de nível de dificuldade na interface

## Tecnologias

- [Python](https://www.python.org/)
- [python-chess](https://python-chess.readthedocs.io/) `1.11.2`: regras, geração de lances e hash Zobrist
- [Tkinter](https://docs.python.org/3/library/tkinter.html): interface gráfica

---

<sub>Projeto desenvolvido para estudo de programação de engines de xadrez.</sub>
