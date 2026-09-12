from pathlib import Path
from problema import Problema

# Pasta onde está localizado este main.py.
pasta_projeto = Path(__file__).resolve().parent

# Troque o nome para escolher outro mapa.
nome_mapa = "mapa_1_caixa.txt"

caminho_mapa = r"C:\Users\pedro\OneDrive\Área de Trabalho\Trabalho-IA\mapas\mapa_1_caixa.txt"

problema = Problema(caminho_mapa)

# Conferência inicial.
print("Mapa escolhido:", nome_mapa)
print("Estado inicial:", problema.estado_inicial)
print("Ações disponíveis:", problema.acoes(problema.estado_inicial))