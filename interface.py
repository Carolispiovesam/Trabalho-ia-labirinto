# -*- coding: utf-8 -*-
"""
TRABALHO AVALIATIVO DE INTELIGÊNCIA ARTIFICIAL - UFAG
Problema 8: Empurrar Caixas no Labirinto (Sokoban)
Módulo de Interface Gráfica (GUI) em Python utilizando Tkinter.

Componentes da Interface:
1. Visualizador em Canvas (Grade, Paredes, Alvos, Caixas, Agente, Nós Expandidos)
2. Painel de Controle (Seleção de Algoritmo, Mapa, Velocidade da Animação)
3. Controle de Animação (Play, Pause, Passo Anterior, Próximo Passo, Reset)
4. Painel de Métricas em Tempo Real (Custo, Passos, Nós Expandidos, Tempo de Execução)
5. Suporte a Destaque de Nós Expandidos (Exploração da busca)
"""

import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# =============================================================================
# PARTE 1 - ESTRUTURA E MODELAGEM DO PROBLEMA (SOKOBAN)
# =============================================================================

class ProblemaSokoban:
    """
    Representação do problema Sokoban para os algoritmos de busca.
    O Estado é definido pela tupla: (posicao_agente, frozenset(posicoes_caixas))
    """
    MOVIMENTOS = {
        "cima": (-1, 0),
        "baixo": (1, 0),
        "esquerda": (0, -1),
        "direita": (0, 1),
    }

    def __init__(self, conteudo_ou_caminho):
        self.paredes = frozenset()
        self.alvos = frozenset()
        self.estado_inicial = None
        self.largura = 0
        self.comprimento = 0

        if isinstance(conteudo_ou_caminho, str) and ("\n" in conteudo_ou_caminho or "#" in conteudo_ou_caminho):
            self._carregar_mapa_string(conteudo_ou_caminho)
        else:
            self._carregar_mapa_arquivo(conteudo_ou_caminho)

    def _carregar_mapa_string(self, texto):
        linhas = [l.rstrip("\r\n") for l in texto.strip().split("\n") if l.rstrip("\r\n")]
        self._processar_linhas(linhas)

    def _carregar_mapa_arquivo(self, caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            linhas = [l.rstrip("\r\n") for l in f if l.rstrip("\r\n")]
        self._processar_linhas(linhas)

    def _processar_linhas(self, linhas):
        self.largura = len(linhas)
        self.comprimento = max(len(l) for l in linhas)
        paredes = set()
        alvos = set()
        caixas = set()
        agente = None

        for i, linha in enumerate(linhas):
            for j, sim in enumerate(linha):
                pos = (i, j)
                if sim == "#":
                    paredes.add(pos)
                elif sim in ("X", "x"):
                    alvos.add(pos)
                elif sim in ("C", "$"):
                    caixas.add(pos)
                elif sim in ("@", "S"):
                    agente = pos

        self.paredes = frozenset(paredes)
        self.alvos = frozenset(alvos)
        if agente is None:
            raise ValueError("O mapa deve possuir um agente (@).")
        self.estado_inicial = (agente, frozenset(caixas))

    def acoes(self, estado):
        """Retorna os nomes das ações válidas a partir do estado atual."""
        acoes_validas = []
        for acao in self.MOVIMENTOS:
            if self._acao_valida(estado, acao):
                acoes_validas.append(acao)
        return acoes_validas

    def resultado(self, estado, acao):
        """Gera o novo estado após aplicar a ação recebida."""
        if not self._acao_valida(estado, acao):
            raise ValueError(f"Ação inválida: {acao}")
        agente, caixas = estado
        dl, dc = self.MOVIMENTOS[acao]
        novo_agente = (agente[0] + dl, agente[1] + dc)
        
        if novo_agente in caixas:
            nova_pos_caixa = (novo_agente[0] + dl, novo_agente[1] + dc)
            novas_caixas = set(caixas)
            novas_caixas.remove(novo_agente)
            novas_caixas.add(nova_pos_caixa)
            return (novo_agente, frozenset(novas_caixas))
            
        return (novo_agente, caixas)

    def eh_objetivo(self, estado):
        """O objetivo é alcançado quando todas as caixas estão sobre os alvos."""
        _, caixas = estado
        return caixas == self.alvos

    def heuristica(self, estado):
        """
        Heurística da Distância de Manhattan:
        Soma da menor distância de Manhattan de cada caixa até o alvo mais próximo.
        É uma heurística admissível (nunca superestima o custo real).
        """
        _, caixas = estado
        soma_distancias = 0
        for caixa in caixas:
            menor = min(abs(caixa[0] - alvo[0]) + abs(caixa[1] - alvo[1]) for alvo in self.alvos)
            soma_distancias += menor
        return soma_distancias

    def vizinhos(self, estado):
        """Devolve a lista de pares (novo_estado, custo)."""
        saidas = []
        for acao in self.acoes(estado):
            novo_est = self.resultado(estado, acao)
            saidas.append((novo_est, 1)) # Custo 1 por movimento
        return saidas

    def _posicao_livre(self, pos, caixas):
        l, c = pos
        return (0 <= l < self.largura and 0 <= c < self.comprimento 
                and pos not in self.paredes and pos not in caixas)

    def _acao_valida(self, estado, acao):
        if acao not in self.MOVIMENTOS:
            return False
        agente, caixas = estado
        dl, dc = self.MOVIMENTOS[acao]
        destino = (agente[0] + dl, agente[1] + dc)

        if destino in caixas:
            destino_caixa = (destino[0] + dl, destino[1] + dc)
            if not self._posicao_livre(destino_caixa, caixas):
                return False
            novas_caixas = set(caixas)
            novas_caixas.remove(destino)
            novas_caixas.add(destino_caixa)
            novo_estado = (destino, frozenset(novas_caixas))
            
            # Detecção de becos sem saída (cantos e bloqueios 2x2)
            if self._caixa_canto(novo_estado) or self._bloqueio_2x2(novo_estado):
                return False
            return True

        return self._posicao_livre(destino, caixas)

    def _caixa_canto(self, estado):
        _, caixas = estado
        for l, c in caixas:
            if (l, c) in self.alvos:
                continue
            par_cima = (l - 1, c) in self.paredes
            par_baixo = (l + 1, c) in self.paredes
            par_esq = (l, c - 1) in self.paredes
            par_dir = (l, c + 1) in self.paredes
            if (par_cima or par_baixo) and (par_esq or par_dir):
                return True
        return False

    def _bloqueio_2x2(self, estado):
        _, caixas = estado
        for l, c in caixas:
            if (l, c) in self.alvos:
                continue
            for il in (l - 1, l):
                for ic in (c - 1, c):
                    bloco = ((il, ic), (il, ic + 1), (il + 1, ic), (il + 1, ic + 1))
                    if all(p in self.paredes or p in caixas for p in bloco):
                        return True
        return False

# =============================================================================
# PARTE 2 - MOTORES DE BUSCA (UCS, BUSCA GULOSA E A*)
# =============================================================================

def criar_no(estado, pai, custo, profundidade):
    return {"estado": estado, "pai": pai, "custo": custo, "profundidade": profundidade}

def remover_menor_f(fronteira, f):
    idx = 0
    for i in range(1, len(fronteira)):
        if f(fronteira[i]) < f(fronteira[idx]):
            idx = i
    return fronteira.pop(idx)

def caminho_ate(no):
    caminho = []
    while no is not None:
        caminho.append(no["estado"])
        no = no["pai"]
    caminho.reverse()
    return caminho

def executar_busca(problema, funcao_f):
    """
    Função genérica de busca informada/não informada.
    Troca o comportamento alternando apenas a função de avaliação f(n).
    """
    tempo_inicio = time.time()
    inicial = problema.estado_inicial
    fronteira = [criar_no(inicial, None, 0, 0)]
    alcancados = {inicial: 0}
    ja_expandidos = []

    while len(fronteira) > 0:
        no = remover_menor_f(fronteira, funcao_f)

        if problema.eh_objetivo(no["estado"]):
            tempo_fim = time.time()
            return {
                "sucesso": True,
                "caminho": caminho_ate(no),
                "custo": no["custo"],
                "passos": no["profundidade"],
                "expandidos": len(ja_expandidos),
                "ordem_de_expansao": ja_expandidos,
                "tempo_s": tempo_fim - tempo_inicio
            }

        ja_expandidos.append(no["estado"])

        for vizinha, custo_acao in problema.vizinhos(no["estado"]):
            novo_custo = no["custo"] + custo_acao
            if vizinha not in alcancados or novo_custo < alcancados[vizinha]:
                alcancados[vizinha] = novo_custo
                fronteira.append(criar_no(vizinha, no, novo_custo, no["profundidade"] + 1))

    tempo_fim = time.time()
    return {
        "sucesso": False,
        "caminho": [],
        "custo": 0,
        "passos": 0,
        "expandidos": len(ja_expandidos),
        "ordem_de_expansao": ja_expandidos,
        "tempo_s": tempo_fim - tempo_inicio
    }

# Definindo as funções f(n) para os três algoritmos
def f_ucs(no, problema=None):
    """UCS: f(n) = g(n) -> olha apenas para o custo acumulado."""
    return no["custo"]

def f_gulosa(no, problema):
    """Busca Gulosa: f(n) = h(n) -> olha apenas para o palpite heurístico."""
    return problema.heuristica(no["estado"])

def f_a_estrela(no, problema):
    """A*: f(n) = g(n) + h(n) -> combina custo acumulado e estimativa heurística."""
    return no["custo"] + problema.heuristica(no["estado"])


# MAPAS PADRÃO (Para execução autônoma)
MAPAS_PADRAO = {
    "Mapa 1 Caixa (Simples)": """#######
#...X.#
#..#..#
#...#.#
#.C...#
#...@.#
#######""",

    "Mapa 2 Caixas (Médio)": """########
#...X..#
#..C...#
#..X...#
#...C..#
#..@...#
########""",

    "Mapa 3 Caixas (Desafio)": """#########
#...X...#
#..C.C..#
#...X...#
#..X.C..#
#...@...#
#########"""
}

# =============================================================================
# PARTE 3 - INTERFACE GRÁFICA TKINTER (SokobanGUI)
# =============================================================================

class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban IA - Visualizador & Interface de Busca")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)

        self.problema = None
        self.resultado_busca = None
        self.passo_atual = 0
        self.em_animacao = False
        self.id_timer = None

        self._configurar_estilos()
        self._criar_layout()
        self._carregar_mapa_selecionado()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#1e293b")
        style.configure("SubHeader.TLabel", font=("Helvetica", 11, "bold"), foreground="#334155")
        style.configure("MetricTitle.TLabel", font=("Helvetica", 9, "bold"), foreground="#64748b")
        style.configure("MetricVal.TLabel", font=("Helvetica", 12, "bold"), foreground="#0f172a")

    def _criar_layout(self):
        # Container Principal (Dividido em Painel Esquerdo: Canvas, Direito: Controles e Métricas)
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------------------
        # PAINEL ESQUERDO: CANVAS DO TABULEIRO
        # ---------------------------------------------------------------------
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título do Tabuleiro
        lbl_tab = ttk.Label(left_frame, text="Visualização do Tabuleiro", style="Header.TLabel")
        lbl_tab.pack(anchor=tk.W, pady=(0, 5))

        # Canvas para desenho da grade
        self.canvas = tk.Canvas(left_frame, bg="#f8fafc", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Legenda das Cores
        legenda_frame = ttk.Frame(left_frame, padding=5)
        legenda_frame.pack(fill=tk.X, pady=(5, 0))
        
        itens_legenda = [
            ("Agente (@)", "#3b82f6"),
            ("Caixa (C)", "#d97706"),
            ("Caixa no Alvo", "#16a34a"),
            ("Alvo (X)", "#ef4444"),
            ("Parede (#)", "#334155"),
            ("Nó Expandido", "#fef08a")
        ]
        for idx, (texto, cor) in enumerate(itens_legenda):
            box = tk.Canvas(legenda_frame, width=14, height=14, bg=cor, highlightthickness=1)
            box.pack(side=tk.LEFT, padx=(8 if idx > 0 else 0, 2))
            lbl = ttk.Label(legenda_frame, text=texto, font=("Helvetica", 8))
            lbl.pack(side=tk.LEFT)

        # ---------------------------------------------------------------------
        # PAINEL DIREITO: CONTROLES E MÉTRICAS
        # ---------------------------------------------------------------------
        right_frame = ttk.Frame(main_frame, width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        # --- SEÇÃO 1: CONFIGURAÇÕES E SELEÇÃO ---
        grp_config = ttk.LabelFrame(right_frame, text=" Configurações ", padding=10)
        grp_config.pack(fill=tk.X, pady=(0, 10))

        # Seleção do Mapa
        ttk.Label(grp_config, text="Selecione o Mapa:", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 2))
        self.cb_mapas = ttk.Combobox(grp_config, values=list(MAPAS_PADRAO.keys()), state="readonly")
        self.cb_mapas.current(0)
        self.cb_mapas.pack(fill=tk.X, pady=(0, 8))
        self.cb_mapas.bind("<<ComboboxSelected>>", lambda e: self._carregar_mapa_selecionado())

        # Botão para carregar mapa customizado de arquivo
        btn_abrir_file = ttk.Button(grp_config, text="📁 Abrir Arquivo .txt", command=self._abrir_arquivo_mapa)
        btn_abrir_file.pack(fill=tk.X, pady=(0, 10))

        # Seleção do Algoritmo
        ttk.Label(grp_config, text="Algoritmo de Busca:", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 2))
        self.cb_algoritmos = ttk.Combobox(grp_config, values=[
            "UCS (Custo Uniforme - f = g)",
            "Busca Gulosa (f = h)",
            "A* (A-Estrela - f = g + h)"
        ], state="readonly")
        self.cb_algoritmos.current(2) # Default A*
        self.cb_algoritmos.pack(fill=tk.X, pady=(0, 10))

        # Botão Executar Busca
        btn_executar = ttk.Button(grp_config, text="🚀 Executar Algoritmo", command=self._executar_busca_gui)
        btn_executar.pack(fill=tk.X, ipady=4)

        # --- SEÇÃO 2: PAINEL DE MÉTRICAS ---
        grp_metricas = ttk.LabelFrame(right_frame, text=" Métricas do Algoritmo ", padding=10)
        grp_metricas.pack(fill=tk.X, pady=(0, 10))

        grid_m = ttk.Frame(grp_metricas)
        grid_m.pack(fill=tk.X)

        # Custo
        ttk.Label(grid_m, text="CUSTO (g):", style="MetricTitle.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_custo = ttk.Label(grid_m, text="-", style="MetricVal.TLabel")
        self.lbl_custo.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))

        # Passos
        ttk.Label(grid_m, text="PASSOS:", style="MetricTitle.TLabel").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_passos = ttk.Label(grid_m, text="-", style="MetricVal.TLabel")
        self.lbl_passos.grid(row=1, column=1, sticky=tk.E, padx=(10, 0))

        # Nós Expandidos
        ttk.Label(grid_m, text="NÓS EXPANDIDOS:", style="MetricTitle.TLabel").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_expandidos = ttk.Label(grid_m, text="-", style="MetricVal.TLabel", foreground="#dc2626")
        self.lbl_expandidos.grid(row=2, column=1, sticky=tk.E, padx=(10, 0))

        # Tempo de Execução
        ttk.Label(grid_m, text="TEMPO (ms):", style="MetricTitle.TLabel").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_tempo = ttk.Label(grid_m, text="-", style="MetricVal.TLabel")
        self.lbl_tempo.grid(row=3, column=1, sticky=tk.E, padx=(10, 0))

        # --- SEÇÃO 3: CONTROLES DE ANIMAÇÃO ---
        grp_anim = ttk.LabelFrame(right_frame, text=" Animação & Reprodução ", padding=10)
        grp_anim.pack(fill=tk.X, pady=(0, 10))

        # Botões de Play/Pause
        btn_box = ttk.Frame(grp_anim)
        btn_box.pack(fill=tk.X, pady=(0, 5))

        self.btn_play = ttk.Button(btn_box, text="▶ Play", command=self._alternar_animacao)
        self.btn_play.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        btn_step_back = ttk.Button(btn_box, text="◀ Anter.", command=self._passo_anterior)
        btn_step_back.pack(side=tk.LEFT, padx=2)

        btn_step_fwd = ttk.Button(btn_box, text="Próx. ▶", command=self._proximo_passo)
        btn_step_fwd.pack(side=tk.LEFT, padx=2)

        btn_reset = ttk.Button(btn_box, text="🔄 Reset", command=self._reset_animacao)
        btn_reset.pack(side=tk.LEFT, padx=(2, 0))

        # Slider de Velocidade
        ttk.Label(grp_anim, text="Velocidade da Animação:", font=("Helvetica", 8)).pack(anchor=tk.W, pady=(4, 0))
        self.slider_speed = ttk.Scale(grp_anim, from_=50, to=1000, value=300)
        self.slider_speed.pack(fill=tk.X)

        # Checkbox Destaque de Nós Expandidos
        self.var_mostrar_expandidos = tk.BooleanVar(value=True)
        chk_exp = ttk.Checkbutton(
            grp_anim, text="Destacar Nós Expandidos", variable=self.var_mostrar_expandidos, command=self._desenhar_tabuleiro
        )
        chk_exp.pack(anchor=tk.W, pady=(5, 0))

        # Rótulo de Status
        self.lbl_status = ttk.Label(right_frame, text="Status: Aguardando execução...", font=("Helvetica", 9, "italic"), foreground="#475569")
        self.lbl_status.pack(anchor=tk.W, pady=(5, 0))

    # =========================================================================
    # LÓGICA DE CARREGAMENTO E DESENHO
    # =========================================================================

    def _carregar_mapa_selecionado(self):
        nome_mapa = self.cb_mapas.get()
        conteudo = MAPAS_PADRAO.get(nome_mapa, "")
        try:
            self.problema = ProblemaSokoban(conteudo)
            self.resultado_busca = None
            self.passo_atual = 0
            self._limpar_metricas()
            self._desenhar_tabuleiro()
            self.lbl_status.config(text=f"Mapa '{nome_mapa}' carregado.")
        except Exception as e:
            messagebox.showerror("Erro ao carregar mapa", str(e))

    def _abrir_arquivo_mapa(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")])
        if caminho:
            try:
                self.problema = ProblemaSokoban(caminho)
                self.resultado_busca = None
                self.passo_atual = 0
                self._limpar_metricas()
                self._desenhar_tabuleiro()
                nome_arq = Path(caminho).name
                self.lbl_status.config(text=f"Mapa '{nome_arq}' carregado.")
            except Exception as e:
                messagebox.showerror("Erro ao ler arquivo", str(e))

    def _limpar_metricas(self):
        self.lbl_custo.config(text="-")
        self.lbl_passos.config(text="-")
        self.lbl_expandidos.config(text="-")
        self.lbl_tempo.config(text="-")

    def _desenhar_tabuleiro(self):
        self.canvas.delete("all")
        if not self.problema:
            return

        w_canvas = self.canvas.winfo_width()
        h_canvas = self.canvas.winfo_height()
        if w_canvas <= 1:
            w_canvas, h_canvas = 600, 500

        cols = self.problema.comprimento
        rows = self.problema.largura
        tamanho_celula = min((w_canvas - 20) // cols, (h_canvas - 20) // rows)
        tamanho_celula = max(tamanho_celula, 20)

        offset_x = (w_canvas - (cols * tamanho_celula)) // 2
        offset_y = (h_canvas - (rows * tamanho_celula)) // 2

        # Estado atual a desenhar (Se houver busca realizada, desenha o passo da solução)
        if self.resultado_busca and self.resultado_busca["sucesso"] and self.passo_atual < len(self.resultado_busca["caminho"]):
            agente, caixas = self.resultado_busca["caminho"][self.passo_atual]
        else:
            agente, caixas = self.problema.estado_inicial

        # 1. Coletar posições dos nós expandidos para destacar (se opção ativa)
        nos_expandidos_pos = set()
        if self.var_mostrar_expandidos.get() and self.resultado_busca:
            for est in self.resultado_busca["ordem_de_expansao"]:
                ag_exp, cx_exp = est
                nos_expandidos_pos.add(ag_exp)
                for c in cx_exp:
                    nos_expandidos_pos.add(c)

        # 2. Desenhar a Grade
        for r in range(rows):
            for c in range(cols):
                pos = (r, c)
                x1 = offset_x + c * tamanho_celula
                y1 = offset_y + r * tamanho_celula
                x2 = x1 + tamanho_celula
                y2 = y1 + tamanho_celula

                # Cor padrão do chão
                cor_fundo = "#f1f5f9"
                
                # Destaque de nó expandido
                if pos in nos_expandidos_pos and pos not in self.problema.paredes:
                    cor_fundo = "#fef08a"

                # Parede
                if pos in self.problema.paredes:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#334155", outline="#1e293b")
                    # Textura de tijolo simples
                    self.canvas.create_line(x1, y1 + tamanho_celula//2, x2, y1 + tamanho_celula//2, fill="#475569")
                    continue

                # Fundo do chão
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor_fundo, outline="#cbd5e1")

                # Alvo (X)
                if pos in self.problema.alvos:
                    pad = tamanho_celula * 0.2
                    self.canvas.create_oval(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill="#fecaca", outline="#ef4444", width=2)
                    self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text="✕", fill="#dc2626", font=("Helvetica", int(tamanho_celula*0.4), "bold"))

                # Caixa (C)
                if pos in caixas:
                    pad = tamanho_celula * 0.12
                    no_alvo = pos in self.problema.alvos
                    cor_caixa = "#16a34a" if no_alvo else "#d97706"
                    cor_borda = "#15803d" if no_alvo else "#b45309"
                    
                    self.canvas.create_rectangle(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill=cor_caixa, outline=cor_borda, width=2)
                    simbolo = "✓" if no_alvo else "📦"
                    self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=simbolo, fill="#ffffff", font=("Helvetica", int(tamanho_celula*0.4), "bold"))

                # Agente (@)
                if pos == agente:
                    pad = tamanho_celula * 0.15
                    self.canvas.create_oval(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill="#3b82f6", outline="#1d4ed8", width=2)
                    self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text="🤖", font=("Helvetica", int(tamanho_celula*0.4)))

    # =========================================================================
    # LÓGICA DE EXECUÇÃO E ANIMAÇÃO
    # =========================================================================

    def _executar_busca_gui(self):
        if not self.problema:
            return

        alg_nome = self.cb_algoritmos.get()
        if "UCS" in alg_nome:
            f_fun = f_ucs
        elif "Gulosa" in alg_nome:
            f_fun = lambda n: f_gulosa(n, self.problema)
        else:
            f_fun = lambda n: f_a_estrela(n, self.problema)

        self.lbl_status.config(text="Executando busca...")
        self.root.update()

        # Executa a busca
        res = executar_busca(self.problema, f_fun)
        self.resultado_busca = res
        self.passo_atual = 0

        if res["sucesso"]:
            self.lbl_custo.config(text=str(res["custo"]))
            self.lbl_passos.config(text=str(res["passos"]))
            self.lbl_expandidos.config(text=str(res["expandidos"]))
            self.lbl_tempo.config(text=f"{res['tempo_s']*1000:.1f}")
            self.lbl_status.config(text=f"Busca concluída! Solução em {res['passos']} passos.")
        else:
            self.lbl_custo.config(text="Sem Solução")
            self.lbl_passos.config(text="-")
            self.lbl_expandidos.config(text=str(res["expandidos"]))
            self.lbl_tempo.config(text=f"{res['tempo_s']*1000:.1f}")
            self.lbl_status.config(text="Busca encerrada: Nenhuma solução encontrada.")
            messagebox.showwarning("Sem Solução", "O algoritmo não encontrou um caminho válido até o objetivo.")

        self._desenhar_tabuleiro()

    def _alternar_animacao(self):
        if self.em_animacao:
            self._pausar_animacao()
        else:
            if not self.resultado_busca or not self.resultado_busca["sucesso"]:
                messagebox.showinfo("Aviso", "Execute o algoritmo primeiro para animar a solução.")
                return
            self.em_animacao = True
            self.btn_play.config(text="⏸ Pausar")
            self._loop_animacao()

    def _pausar_animacao(self):
        self.em_animacao = False
        self.btn_play.config(text="▶ Play")
        if self.id_timer:
            self.root.after_cancel(self.id_timer)
            self.id_timer = None

    def _loop_animacao(self):
        if not self.em_animacao or not self.resultado_busca:
            return

        if self.passo_atual < len(self.resultado_busca["caminho"]) - 1:
            self.passo_atual += 1
            self._desenhar_tabuleiro()
            delay = int(self.slider_speed.get())
            self.id_timer = self.root.after(delay, self._loop_animacao)
        else:
            self._pausar_animacao()
            self.lbl_status.config(text="Animação concluída.")

    def _proximo_passo(self):
        self._pausar_animacao()
        if self.resultado_busca and self.resultado_busca["sucesso"]:
            if self.passo_atual < len(self.resultado_busca["caminho"]) - 1:
                self.passo_atual += 1
                self._desenhar_tabuleiro()

    def _passo_anterior(self):
        self._pausar_animacao()
        if self.resultado_busca and self.resultado_busca["sucesso"]:
            if self.passo_atual > 0:
                self.passo_atual -= 1
                self._desenhar_tabuleiro()

    def _reset_animacao(self):
        self._pausar_animacao()
        self.passo_atual = 0
        self._desenhar_tabuleiro()
        self.lbl_status.config(text="Resetado para o estado inicial.")


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SokobanGUI(root)
    
    # Redimensionar canvas automaticamente com a janela
    root.bind("<Configure>", lambda e: app._desenhar_tabuleiro() if e.widget == root else None)
    
    root.mainloop()
