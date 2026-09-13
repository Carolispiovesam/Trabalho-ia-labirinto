import heapq
import time

class No:
    def __init__(self, estado, pai, acao, custo):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.custo = custo

def busca(problema, funcao_f, limite_tempo=60):
    estado_inicial = problema.estado_inicial

    # O nó inicial não possui pai nem ação anterior e começa com custo 0.
    no_inicial = No(
        estado_inicial,
        None, 
        None,
        0
    )

    # Fila de prioridade usada como fronteira da busca.
    fronteira = []

    # A função f define qual algoritmo será usado:
    prioridade = funcao_f(
        no_inicial.custo,
        problema.heuristica(no_inicial.estado)
    )

    heapq.heappush(
        fronteira,
        (prioridade, 0, no_inicial)
    )

    melhor_custo = {
        estado_inicial: 0
    }

    # Usado para desempatar nós que possuem a mesma prioridade no heap.
    contador = 1

    # Variáveis usadas para medir tempo e quantidade de nós expandidos.
    inicio = time.time()
    nos_expandidos = 0
    ordem_de_expansao = []

    while fronteira:

        if time.time() - inicio > limite_tempo:
            tempo_total = time.time() - inicio
            return {
                "timeout": True, 
                "custo": None, 
                "passos": None, 
                "nos_expandidos": nos_expandidos, 
                "tempo": tempo_total
            }
        
        # Retira o nó de maior prioridade da fronteira
        _, _, no_atual = heapq.heappop(fronteira)
        ordem_de_expansao.append(no_atual.estado)

        if no_atual.custo > melhor_custo[no_atual.estado]:
            continue

        if problema.eh_objetivo(no_atual.estado):
            tempo_total= time.time() - inicio
            return {
                "timeout": False,
                "custo": no_atual.custo,
                "passos": len(reconstruir_caminho(no_atual)),
                "nos_expandidos": nos_expandidos,
                "tempo": tempo_total,
                "caminho": reconstruir_caminho_estados(no_atual), 
                "ordem_de_expansao": ordem_de_expansao            
            }

        nos_expandidos += 1

        acoes_validas = problema.acoes(no_atual.estado)

        for acao in acoes_validas:
            novo_estado = problema.resultado(
                no_atual.estado,
                acao
            )

            novo_custo = no_atual.custo + 1

            # Só adiciona se for um estado novo ou um caminho mais barato
            if (
                novo_estado not in melhor_custo
                or novo_custo < melhor_custo[novo_estado]
            ):
                melhor_custo[novo_estado] = novo_custo

                novo_no = No(
                    novo_estado,
                    no_atual,
                    acao,
                    novo_custo
                )

                h = problema.heuristica(novo_estado)

                prioridade = funcao_f(
                    novo_custo,
                    h
                )

                heapq.heappush(
                    fronteira,
                    (prioridade, contador, novo_no)
                )

                contador += 1

    tempo_total = time.time() - inicio
    tempo_total = time.time() - inicio
    return {
        "timeout": False,
        "custo": "Sem solução",
        "passos": "-",
        "nos_expandidos": nos_expandidos,
        "tempo": tempo_total
    }

# Volta pelos nós pais até o estado inicial
def reconstruir_caminho(no_final):
    acoes = []

    no_atual = no_final

    while no_atual.pai is not None:
        acoes.append(no_atual.acao)
        no_atual = no_atual.pai

    acoes.reverse()

    return acoes

def f_ucs (g, h):
    return g

def f_gulosa(g, h):
    return h

def f_astar(g, h):
    return g + h

def reconstruir_caminho_estados(no_final):
    estados = []
    no_atual = no_final
    while no_atual is not None:
        estados.append(no_atual.estado)
        no_atual = no_atual.pai
    estados.reverse()
    return estados