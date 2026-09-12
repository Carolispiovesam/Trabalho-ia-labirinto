import time
import problema
import busca

def imprimir_metricas(nome_algoritmo, resultado):
    """
    Função auxiliar para imprimir as métricas no terminal de forma padronizada.
    Espera receber um dicionário ou objeto com as métricas do algoritmo.
    """
    print(f"\n Resultados da {nome_algoritmo} ")
    
    # Se a busca demorar muito e estourar o limite de tempo da equipe
    if resultado is None or resultado.get("timeout") == True:
        print("Status: Não concluiu no tempo limite estabelecido.")
        return

    # Imprime as quatro métricas obrigatórias do relatório
    print(f"Custo da solução: {resultado.get('custo')}")
    print(f"Número de passos: {resultado.get('passos')}")
    print(f"Nós expandidos:   {resultado.get('nos_expandidos')}")
    print(f"Tempo de execução:{resultado.get('tempo'):.4f} segundos")
    print("-" * 40)

def main():
    # Define o mapa carregado
    caminho_mapa = "mapas/mapa_1_caixa.txt"
    print(f"Iniciando resolução do mapa: {caminho_mapa}")

    # labirinto = problema.carregar_mapa(caminho_mapa)
    labirinto = None # temporário

    # 1. Busca de Custo Uniforme (UCS)
    # Para UCS, f(n) = g(n) - Olha apenas o custo já pago
    print("\n[1/3] Executando Busca de Custo Uniforme (UCS)...")
    # resultado_ucs = busca.busca_generica(labirinto, calcular_f=lambda no: no.g)
    # imprimir_metricas("UCS", resultado_ucs)


    # 2. Busca Gulosa
    # Para Gulosa, f(n) = h(n) - Olha apenas a heurística.
    print("\n[2/3] Executando Busca Gulosa...")
    # resultado_gulosa = busca.busca_generica(labirinto, calcular_f=lambda no: no.h)
    # imprimir_metricas("Busca Gulosa", resultado_gulosa)


    # 3. Busca A*
    # Para A*, f(n) = g(n) + h(n) - Soma o custo real com a heurística.
    print("\n[3/3] Executando Busca A*...")
    # resultado_astar = busca.busca_generica(labirinto, calcular_f=lambda no: no.g + no.h)
    # imprimir_metricas("A*", resultado_astar)

if __name__ == '__main__':
    main()