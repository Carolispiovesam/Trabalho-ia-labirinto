
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class SokobanGUI:
    def __init__(self, root, problema=None, resultado=None, nome_algoritmo=""):
        self.root = root
        self.root.title(f"Sokoban - Visualizador ({nome_algoritmo})" if nome_algoritmo else "Sokoban - Visualizador")
        self.root.geometry("900x650")
        self.root.minsize(800, 500)

        self.problema = problema
        self.resultado_busca = resultado
        self.passo_atual = 0
        self.em_animacao = False
        self.id_timer = None

        self._criar_interface()
        if self.problema and self.resultado_busca:
            self._preencher_metricas_e_desenhar()

    def _criar_interface(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Painel esquerdo: Canvas do Tabuleiro
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
            ("Nó Expandido", "#fef08a")
        ]
        for idx, (texto, cor) in enumerate(itens_legenda):
            box = tk.Canvas(legenda_frame, width=12, height=12, bg=cor, highlightthickness=1)
            box.pack(side=tk.LEFT, padx=(6 if idx > 0 else 0, 2))
            lbl = ttk.Label(legenda_frame, text=texto, font=("Helvetica", 8))
            lbl.pack(side=tk.LEFT)

        # Painel direito: Métricas e Controles de Animação
        right_frame = ttk.Frame(main_frame, width=280)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        # Painel de Métricas
        grp_met = ttk.LabelFrame(right_frame, text=" Métricas da Execução ", padding=10)
        grp_met.pack(fill=tk.X, pady=(0, 10))

        grid_m = ttk.Frame(grp_met)
        grid_m.pack(fill=tk.X)

        ttk.Label(grid_m, text="Custo (g):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_custo = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_custo.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))

        ttk.Label(grid_m, text="Passos:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_passos = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_passos.grid(row=1, column=1, sticky=tk.E, padx=(10, 0))

        ttk.Label(grid_m, text="Nós Expandidos:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_expandidos = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"), foreground="#dc2626")
        self.lbl_expandidos.grid(row=2, column=1, sticky=tk.E, padx=(10, 0))

        ttk.Label(grid_m, text="Tempo (ms):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_tempo = ttk.Label(grid_m, text="-", font=("Helvetica", 10, "bold"))
        self.lbl_tempo.grid(row=3, column=1, sticky=tk.E, padx=(10, 0))

        # Controles de Animação
        grp_anim = ttk.LabelFrame(right_frame, text=" Controles de Animação ", padding=10)
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
        chk_exp = ttk.Checkbutton(grp_anim, text="Destacar nós expandidos", variable=self.var_expandidos, command=self._desenhar)
        chk_exp.pack(anchor=tk.W, pady=(5, 0))

        self.lbl_status = ttk.Label(right_frame, text="Status: Pronto", font=("Helvetica", 9, "italic"))
        self.lbl_status.pack(anchor=tk.W, pady=(5, 0))

    def _preencher_metricas_e_desenhar(self):
        if not self.resultado_busca:
            return
        self.lbl_custo.config(text=str(self.resultado_busca.get('custo', '-')))
        self.lbl_passos.config(text=str(self.resultado_busca.get('passos', '-')))
        self.lbl_expandidos.config(text=str(self.resultado_busca.get('nos_expandidos', '-')))
        tempo_s = self.resultado_busca.get('tempo', 0)
        self.lbl_tempo.config(text=f"{tempo_s * 1000:.2f}")
        self.lbl_status.config(text="Busca carregada com sucesso!")
        self._desenhar()

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

        if self.resultado_busca and 'caminho' in self.resultado_busca and self.passo_atual < len(self.resultado_busca['caminho']):
            agente, caixas = self.resultado_busca['caminho'][self.passo_atual]
        else:
            agente, caixas = self.problema.estado_inicial

        nos_exp = set()
        if self.var_expandidos.get() and self.resultado_busca and 'ordem_de_expansao' in self.resultado_busca:
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

    def _play_pause(self):
        if not self.resultado_busca or 'caminho' not in self.resultado_busca:
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
        if self.resultado_busca and 'caminho' in self.resultado_busca and self.passo_atual > 0:
            self.passo_atual -= 1
            self._desenhar()

    def _proximo_passo(self):
        if self.resultado_busca and 'caminho' in self.resultado_busca and self.passo_atual < len(self.resultado_busca['caminho']) - 1:
            self.passo_atual += 1
            self._desenhar()

    def _reset(self):
        self.em_animacao = False
        self.btn_play.config(text="Play")
        if self.id_timer:
            self.root.after_cancel(self.id_timer)
        self.passo_atual = 0
        self._desenhar()
