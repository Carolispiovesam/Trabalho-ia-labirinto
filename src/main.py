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

    # Inicializa a classe do labirinto criada no problema.py
    labirinto = problema.Problema(caminho_mapa)


# 1. Busca de Custo Uniforme (UCS)
    print("\n[1/3] Executando Busca de Custo Uniforme (UCS)...")
    resultado_ucs = busca.busca(labirinto, busca.f_ucs)
    imprimir_metricas("UCS", resultado_ucs)

    # 2. Busca Gulosa
    print("\n[2/3] Executando Busca Gulosa...")
    resultado_gulosa = busca.busca(labirinto, busca.f_gulosa)
    imprimir_metricas("Busca Gulosa", resultado_gulosa)

    # 3. Busca A*
    print("\n[3/3] Executando Busca A*...")
    resultado_astar = busca.busca(labirinto, busca.f_astar)
    imprimir_metricas("A*", resultado_astar)

if __name__ == '__main__':
    main()