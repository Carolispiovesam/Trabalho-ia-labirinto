import os
import time
import tkinter as tk
from pathlib import Path

import problema
import busca
import interface

def imprimir_metricas(nome_algoritmo, resultado):
    """Função auxiliar para imprimir as métricas no terminal de forma padronizada."""
    print(f"\n=== Resultados da {nome_algoritmo} ===")
    if resultado is None or resultado.get("timeout") == True:
        print("Status: Não concluiu no tempo limite estabelecido.")
        print("-" * 40)
        return
    print(f"Custo da solução: {resultado.get('custo')}")
    print(f"Número de passos: {resultado.get('passos')}")
    print(f"Nós expandidos:   {resultado.get('nos_expandidos')}")
    print(f"Tempo de execução:{resultado.get('tempo') * 1000:.4f} ms")
    print("-" * 40)

def escolher_mapa():
    """Menu para escolha do arquivo de mapa"""
    print("\nESCOLHA O MAPA")
    print("1. Mapa 1 Caixa")
    print("2. Mapa 2 Caixas")
    print("3. Mapa 3 Caixas")
    
    opcao = input("Digite o número da opção (1-3): ")
    
    # Busca a pasta mapas voltando um diretório a partir de src/
    base_path = Path(__file__).resolve().parent.parent / "mapas"
    
    if opcao == '1':
        return str(base_path / "mapa_1_caixa.txt")
    elif opcao == '2':
        return str(base_path / "mapa_2_caixas.txt")
    elif opcao == '3':
        return str(base_path / "mapa_3_caixas.txt")
    else:
        print("Opção inválida. Carregando Mapa 1 por padrão.")
        return str(base_path / "mapa_1_caixa.txt")

def main():
    
    # Escolhe o mapa
    caminho_mapa = escolher_mapa()
    
    if not os.path.exists(caminho_mapa):
        print(f"\n[ERRO] O arquivo '{caminho_mapa}' não foi encontrado.")
        return

    print(f"\n[+] Inicializando o labirinto: {caminho_mapa}")
    labirinto = problema.Problema(caminho_mapa)

    # Escolhe o algoritmo
    print("\nESCOLHA O ALGORITMO")
    print("1. Busca de Custo Uniforme (UCS)")
    print("2. Busca Gulosa")
    print("3. Busca A*")
    
    opcao_alg = input("Digite o número da opção (1-3): ")

    if opcao_alg == '1':
        nome_alg = "UCS"
        f_eval = busca.f_ucs
    elif opcao_alg == '2':
        nome_alg = "Busca Gulosa"
        f_eval = busca.f_gulosa
    elif opcao_alg == '3':
        nome_alg = "A*"
        f_eval = busca.f_astar
    else:
        print("\n[ERRO] Opção de algoritmo inválida.")
        return

    print(f"\nExecutando {nome_alg}...")
    resultado = busca.busca(labirinto, f_eval)
    
    # Exibe no terminal
    imprimir_metricas(nome_alg, resultado)

    # Abre a interface gráfica com os dados já processados
    if resultado and not resultado.get("timeout") and resultado.get("custo") != "Sem solução":
        print("\n[+] Abrindo interface visual com a solução calculada...")
        root = tk.Tk()
        app = interface.SokobanGUI(root, problema=labirinto, resultado=resultado, nome_algoritmo=nome_alg)
        root.mainloop()
    else:
        print("\n[!] Nenhuma solução encontrada para exibir na interface.")

if __name__ == '__main__':
    main()