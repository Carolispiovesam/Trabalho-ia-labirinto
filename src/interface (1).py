# -*- coding: utf-8 -*-
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# Importa a classe do problema criada pelo grupo
try:
    from problema import Problema
except ImportError:
    try:
        from src.problema import Problema
    except ImportError:
        Problema = None


def busca_generica(problema, f_eval):
    inicial = problema.estado_inicial
    fronteira = [{'estado': inicial, 'pai': None, 'custo': 0, 'passos': 0}]
    alcancados = {inicial: 0}
    ja_expandidos = []

    while fronteira:
        idx_menor = 0
        for i in range(1, len(fronteira)):
            if f_eval(fronteira[i]) < f_eval(fronteira[idx_menor]):
                idx_menor = i
        no = fronteira.pop(idx_menor)

        if problema.eh_objetivo(no['estado']):
            caminho = []
            curr = no
            while curr:
                caminho.append(curr['estado'])
                curr = curr['pai']
            caminho.reverse()
            return {
                'caminho': caminho,
                'custo': no['custo'],
                'passos': no['passos'],
                'expandidos': len(ja_expandidos),
                'ordem_de_expansao': ja_expandidos
            }

        ja_expandidos.append(no['estado'])

        for acao in problema.acoes(no['estado']):
            novo_est = problema.resultado(no['estado'], acao)
            novo_custo = no['custo'] + 1
            if novo_est not in alcancados or novo_custo < alcancados[novo_est]:
                alcancados[novo_est] = novo_custo
                fronteira.append({
                    'estado': novo_est,
                    'pai': no,
                    'custo': novo_custo,
                    'passos': no['passos'] + 1
                })
    return None


class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban - Interface de Visualizacao")
        self.root.geometry("1000x680")
        self.root.minsize(850, 580)

        self.problema = None
        self.resultado_busca = None
        self.passo_atual = 0
        self.em_animacao = False
        self.id_timer = None
        self.caminho_mapa_atual = None

        self._criar_interface()
        self._carregar_mapa_padrao()

    def _criar_interface(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Painel esquerdo: Canvas
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(left_frame, text="Tabuleiro", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        self.canvas = tk.Canvas(left_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Legenda simples
        legenda_frame = ttk.Frame(left_frame, padding=5)
        legenda_frame.pack(fill=tk.X, pady=(5, 0))

        itens_legenda = [
            ("Agente (@)", "#3b82f6"),
            ("Caixa (C)", "#d97706"),
            ("Caixa no Alvo", "#16a34a"),
            ("Alvo (X)", "#ef4444"),
            ("Parede (#)", "#334155"),
            ("No Expandido", "#fef08a")
        ]
        for idx, (texto, cor) in enumerate(itens_legenda):
            box = tk.Canvas(legenda_frame, width=12, height=12, bg=cor, highlightthickness=1)
            box.pack(side=tk.LEFT, padx=(6 if idx > 0 else 0, 2))
            lbl = ttk.Label(legenda_frame, text=texto, font=("Helvetica", 8))
            lbl.pack(side=tk.LEFT)

        # Painel direito: Controles e Metricas
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        # Configuracoes
        grp_config = ttk.LabelFrame(right_frame, text=" Configuracoes ", padding=10)
        grp_config.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(grp_config, text="Selecione o Mapa:").pack(anchor=tk.W, pady=(0, 2))
        self.cb_mapas = ttk.Combobox(grp_config, values=["mapa_1_caixa.txt", "mapa_2_caixas.txt", "mapa_3_caixas.txt"], state="readonly")
        self.cb_mapas.current(0)
        self.cb_mapas.pack(fill=tk.X, pady=(0, 5))
        self.cb_mapas.bind("<<ComboboxSelected>>", lambda e: self._carregar_mapa_padrao())

        btn_abrir = ttk.Button(grp_config, text="Abrir arquivo .txt...", command=self._abrir_arquivo)
        btn_abrir.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(grp_config, text="Algoritmo:").pack(anchor=tk.W, pady=(0, 2))
        self.cb_alg = ttk.Combobox(grp_config, values=[
            "UCS (Custo Uniforme)",
            "Busca Gulosa",
            "A*"
        ], state="readonly")
        self.cb_alg.current(2)
        self.cb_alg.pack(fill=tk.X, pady=(0, 10))

        btn_executar = ttk.Button(grp_config, text="Executar Busca", command=self._executar)
        btn_executar.pack(fill=tk.X)

        # Metricas
        grp_met = ttk.LabelFrame(right_frame, text=" Metricas ", padding=10)
        grp_met.pack(fill=tk.X, pady=(0, 10))

        grid_m = ttk.Frame(grp_met)
        grid_m.pack(fill=tk.X)

        ttk.Label(grid_m, text="Custo (g):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_custo = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_custo.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))

        ttk.Label(grid_m, text="Passos:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_passos = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_passos.grid(row=1, column=1, sticky=tk.E, padx=(10, 0))

        ttk.Label(grid_m, text="Nos Expandidos:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_expandidos = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"), foreground="#dc2626")
        self.lbl_expandidos.grid(row=2, column=1, sticky=tk.E, padx=(10, 0))

        ttk.Label(grid_m, text="Tempo (ms):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_tempo = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_tempo.grid(row=3, column=1, sticky=tk.E, padx=(10, 0))

        # Controles de animacao
        grp_anim = ttk.LabelFrame(right_frame, text=" Controles de Animacao ", padding=10)
        grp_anim.pack(fill=tk.X, pady=(0, 10))

        btn_box = ttk.Frame(grp_anim)
        btn_box.pack(fill=tk.X, pady=(0, 5))

        self.btn_play = ttk.Button(btn_box, text="Play", command=self._play_pause)
        self.btn_play.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        ttk.Button(btn_box, text="Anter.", command=self._passo_anterior, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_box, text="Prox.", command=self._proximo_passo, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_box, text="Reset", command=self._reset, width=6).pack(side=tk.LEFT, padx=(2, 0))

        ttk.Label(grp_anim, text="Velocidade (ms):", font=("Helvetica", 8)).pack(anchor=tk.W, pady=(4, 0))
        self.slider_speed = ttk.Scale(grp_anim, from_=50, to=1000, value=300)
        self.slider_speed.pack(fill=tk.X)

        self.var_expandidos = tk.BooleanVar(value=True)
        chk_exp = ttk.Checkbutton(grp_anim, text="Destacar nos expandidos", variable=self.var_expandidos, command=self._desenhar)
        chk_exp.pack(anchor=tk.W, pady=(5, 0))

        self.lbl_status = ttk.Label(right_frame, text="Status: Pronto", font=("Helvetica", 9, "italic"))
        self.lbl_status.pack(anchor=tk.W, pady=(5, 0))

    def _carregar_mapa_padrao(self):
        nome_mapa = self.cb_mapas.get()
        # Procura a pasta mapas no projeto
        base_path = Path(__file__).resolve().parent
        candidatos = [
            base_path / "mapas" / nome_mapa,
            base_path.parent / "mapas" / nome_mapa,
            Path("mapas") / nome_mapa
        ]
        caminho_encontrado = None
        for c in candidatos:
            if c.exists():
                caminho_encontrado = c
                break

        if caminho_encontrado and Problema is not None:
            try:
                self.problema = Problema(str(caminho_encontrado))
                self.caminho_mapa_atual = str(caminho_encontrado)
                self.resultado_busca = None
                self.passo_atual = 0
                self._reset_metricas()
                self._desenhar()
                self.lbl_status.config(text=f"Mapa '{nome_mapa}' carregado.")
            except Exception as e:
                self.lbl_status.config(text="Erro ao carregar mapa.")
        else:
            self.lbl_status.config(text="Selecione um arquivo de mapa válido.")

    def _abrir_arquivo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")])
        if caminho and Problema is not None:
            try:
                self.problema = Problema(caminho)
                self.caminho_mapa_atual = caminho
                self.resultado_busca = None
                self.passo_atual = 0
                self._reset_metricas()
                self._desenhar()
                self.lbl_status.config(text="Mapa customizado carregado.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar arquivo: {e}")

    def _executar(self):
        if not self.problema:
            messagebox.showwarning("Aviso", "Nenhum mapa carregado!")
            return

        alg = self.cb_alg.get()
        if "UCS" in alg:
            f = lambda n: n['custo']
        elif "Gulosa" in alg:
            f = lambda n: self.problema.heuristica(n['estado'])
        else:
            f = lambda n: n['custo'] + self.problema.heuristica(n['estado'])

        self.lbl_status.config(text="Executando busca...")
        self.root.update()

        t0 = time.perfcounter()
        res = busca_generica(self.problema, f)
        t1 = time.perfcounter()

        if res:
            tempo_ms = (t1 - t0) * 1000
            self.resultado_busca = res
            self.passo_atual = 0
            self.lbl_custo.config(text=str(res['custo']))
            self.lbl_passos.config(text=str(res['passos']))
            self.lbl_expandidos.config(text=str(res['expandidos']))
            self.lbl_tempo.config(text=f"{tempo_ms:.2f}")
            self.lbl_status.config(text="Busca concluída com sucesso!")
            self._desenhar()
        else:
            self.lbl_status.config(text="Sem solução para este mapa.")
            messagebox.showinfo("Resultado", "Não foi encontrada solução.")

    def _desenhar(self):
        self.canvas.delete("all")
        if not self.problema:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 10 or h <= 10:
            w, h = 600, 500

        cols = self.problema.comprimento
        rows = self.problema.largura
        if cols == 0 or rows == 0:
            return

        tam = min(w // cols, h // rows)
        tam = max(tam, 15)

        off_x = (w - (cols * tam)) // 2
        off_y = (h - (rows * tam)) // 2

        # Estado atual da animacao
        if self.resultado_busca and self.passo_atual < len(self.resultado_busca['caminho']):
            agente, caixas = self.resultado_busca['caminho'][self.passo_atual]
        else:
            agente, caixas = self.problema.estado_inicial

        # Destacar nos expandidos
        nos_exp = set()
        if self.var_expandidos.get() and self.resultado_busca:
            for est in self.resultado_busca['ordem_de_expansao']:
                pos_ag, _ = est
                nos_exp.add(pos_ag)

        for r in range(rows):
            for c in range(cols):
                pos = (r, c)
                x1 = off_x + c * tam
                y1 = off_y + r * tam
                x2 = x1 + tam
                y2 = y1 + tam

                if pos in self.problema.paredes:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#334155", outline="#1e293b")
                else:
                    bg = "#ffffff"
                    if pos in nos_exp and pos != agente and pos not in caixas:
                        bg = "#fef08a"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#e2e8f0")

                if pos in self.problema.alvos:
                    r_alvo = tam // 4
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    self.canvas.create_oval(cx - r_alvo, cy - r_alvo, cx + r_alvo, cy + r_alvo, fill="#ef4444", outline="")

                if pos in caixas:
                    pad = tam // 8
                    cor = "#16a34a" if pos in self.problema.alvos else "#d97706"
                    self.canvas.create_rectangle(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill=cor, outline="#78350f", width=2)
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="C", fill="#ffffff", font=("Helvetica", max(8, tam // 3), "bold"))

                if pos == agente:
                    pad = tam // 10
                    self.canvas.create_oval(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill="#3b82f6", outline="#1d4ed8", width=2)
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="@", fill="#ffffff", font=("Helvetica", max(8, tam // 3), "bold"))

    def _reset_metricas(self):
        self.lbl_custo.config(text="-")
        self.lbl_passos.config(text="-")
        self.lbl_expandidos.config(text="-")
        self.lbl_tempo.config(text="-")

    def _play_pause(self):
        if not self.resultado_busca:
            return
        self.em_animacao = not self.em_animacao
        if self.em_animacao:
            self.btn_play.config(text="Pause")
            self._passo_animacao()
        else:
            self.btn_play.config(text="Play")
            if self.id_timer:
                self.root.after_cancel(self.id_timer)

    def _passo_animacao(self):
        if not self.em_animacao or not self.resultado_busca:
            return
        if self.passo_atual < len(self.resultado_busca['caminho']) - 1:
            self.passo_atual += 1
            self._desenhar()
            ms = int(self.slider_speed.get())
            self.id_timer = self.root.after(ms, self._passo_animacao)
        else:
            self.em_animacao = False
            self.btn_play.config(text="Play")

    def _passo_anterior(self):
        if self.resultado_busca and self.passo_atual > 0:
            self.passo_atual -= 1
            self._desenhar()

    def _proximo_passo(self):
        if self.resultado_busca and self.passo_atual < len(self.resultado_busca['caminho']) - 1:
            self.passo_atual += 1
            self._desenhar()

    def _reset(self):
        self.em_animacao = False
        self.btn_play.config(text="Play")
        if self.id_timer:
            self.root.after_cancel(self.id_timer)
        self.passo_atual = 0
        self._desenhar()


if __name__ == "__main__":
    root = tk.Tk()
    app = SokobanGUI(root)
    root.mainloop()
