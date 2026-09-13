class Problema:
    
    # Ações possíveis de se realizar
    MOVIMENTOS = {
        "cima": (-1, 0),
        "baixo": (1, 0),
        "esquerda": (0, -1),
        "direita": (0, 1), 
    }
    
    # Inicializar variáveis
    def __init__(self, caminho_mapa):
        self.paredes = frozenset()
        self.alvos = frozenset()
        self.estado_inicial = None
        self.comprimento = 0
        self.largura = 0
        
        self._carregar_mapa(caminho_mapa)
    
    def acoes(self, estado):
        # Retorna uma lista com os nomes das ações válidas no estado.
        acoes_validas = []

        for acao in self.MOVIMENTOS:
            if self._acao_valida(estado, acao):
                acoes_validas.append(acao)

        return acoes_validas
    
    def resultado(self, estado, acao):
        '''
        Retorna um novo estado, sem alterar o estado recebido.
        Uma ação inválida gera ValueError.
        Caixas sobre alvos ainda podem ser empurradas.
        '''
        if not self._acao_valida(estado, acao):
            raise ValueError(f"Ação inválida para este estado: {acao!r}.")
    
        agente, caixas = estado
        deslocamento_linha, deslocamento_coluna = self.MOVIMENTOS[acao]
        
        novo_agente = (
            agente[0] + deslocamento_linha,
            agente[1] + deslocamento_coluna,
        )
        
        if novo_agente in caixas:
            nova_posicao_caixa = (
                novo_agente[0] + deslocamento_linha,
                novo_agente[1] + deslocamento_coluna,
            )
            
            novas_caixas = set(caixas)
            novas_caixas.remove(novo_agente)
            novas_caixas.add(nova_posicao_caixa)
            
            return (novo_agente, frozenset(novas_caixas))
        
        return (novo_agente, caixas)
    
    def eh_objetivo(self, estado):
        # Verifica se todas as caixas estão nos alvos
        _, caixas = estado
        
        return caixas == self.alvos
    
    def heuristica(self, estado):
        ''' 
        Faz o cálculo de Manhattan, para cada caixa, em relação ao alvo mais próximo.
        Não faz atribuição exclusiva de alvos nem detecção de caixas presas.
        '''
        
        _, caixas = estado
        soma_distancias = 0
        
        for caixa in caixas:
            menor_distancia = min(
                abs(caixa[0] - alvo[0]) + abs(caixa[1] - alvo[1])
                for alvo in self.alvos
            )
            
            soma_distancias += menor_distancia
        
        return soma_distancias
    
    def _carregar_mapa(self, caminho_mapa):
        '''
        Lê e valida o mapa no arquivo .txt.
        Mapas malformados geram ValueError.
        Erros de abertura do arquivo são propagados para quem chamou a classe.
        '''
        
        # utf-8-sig aceita UTF-8 com ou sem BOM
        with open(caminho_mapa, "r", encoding = "utf-8-sig") as arquivo:
            linhas = [linha.rstrip("\n") for linha in arquivo]
        
        if not linhas or not linhas[0]:
            raise ValueError("O mapa está vazio ou a primeira linha está vazia!")
        
        largura = len(linhas)
        comprimento = len(linhas[0])
        
        if any(len(linha) != comprimento for linha in linhas):
            raise ValueError("Todas as linhas devem ter o mesmo tamanho!")
        
        paredes = set()
        alvos = set()
        caixas = set()
        agente = None
        simbolos_validos = {".", "#", "@", "C", "X"}
        
        for i, linha in enumerate(linhas):
            for j, simbolo in enumerate(linha):
                posicao = (i, j)

                if simbolo not in simbolos_validos:
                    raise ValueError(
                        f"Símbolo inválido {simbolo!r} na posição {posicao}."
                    )

                if simbolo == "#":
                    paredes.add(posicao)
                elif simbolo == "X":
                    alvos.add(posicao)
                elif simbolo == "C":
                    caixas.add(posicao)
                elif simbolo == "@":
                    if agente is not None:
                        raise ValueError("O mapa deve ter apenas um agente (@)!")
                    agente = posicao

        if agente is None:
            raise ValueError("O mapa deve ter um agente (@)!")

        if not caixas:
            raise ValueError("O mapa deve ter pelo menos uma caixa!")

        if len(caixas) != len(alvos):
            raise ValueError("A quantidade de caixas deve ser igual à de alvos!")

        for i, linha in enumerate(linhas):
            for j, simbolo in enumerate(linha):
                na_borda = i in (0, largura - 1) or j in (0, comprimento - 1)
                if na_borda and simbolo != "#":
                    raise ValueError("O mapa deve ser cercado por paredes.")

        self.largura = largura
        self.comprimento = comprimento
        self.paredes = frozenset(paredes)
        self.alvos = frozenset(alvos)
        self.estado_inicial = (agente, frozenset(caixas))
        
        if (self._caixa_canto(self.estado_inicial)):
            raise ValueError("Há uma caixa em um canto sem alvo!")
        
        if (self._bloqueio_2x2(self.estado_inicial)):
            raise ValueError("Há ao menos uma caixa em um bloqueio 2x2!")
        
    def _posicao_livre(self, posicao, caixas):
        """
        Verifica os limites do mapa e a ausência de parede ou caixa.
        É possível andar por alvos e eles não bloqueiam movimentos.
        """
        linha, coluna = posicao
        return (
            0 <= linha < self.largura
            and 0 <= coluna < self.comprimento
            and posicao not in self.paredes
            and posicao not in caixas
        )

    def _acao_valida(self, estado, acao):
        # Verifica se é possível andar ou empurrar uma única caixa.
        if acao not in self.MOVIMENTOS:
            return False

        agente, caixas = estado
        deslocamento_linha, deslocamento_coluna = self.MOVIMENTOS[acao]
        destino = (
            agente[0] + deslocamento_linha,
            agente[1] + deslocamento_coluna,
        )

        if destino in caixas:
            destino_caixa = (
                destino[0] + deslocamento_linha,
                destino[1] + deslocamento_coluna,
            )
            # Não é permitido empurrar contra paredes ou outra caixa.
            if not (self._posicao_livre(destino_caixa, caixas)):
                return False
            
            novas_caixas = set(caixas)
            novas_caixas.remove(destino)
            novas_caixas.add(destino_caixa)
            
            novo_estado = (destino, frozenset(novas_caixas))
            
            if (self._caixa_canto(novo_estado)):
                return False
            
            if (self._bloqueio_2x2(novo_estado)):
                return False
            
            return True

        return self._posicao_livre(destino, caixas)
    
    def _caixa_canto(self, estado):
        # Verifica se existe uma caixa em um canto de paredes sem alvo.
        _, caixas = estado

        for linha, coluna in caixas:
            if (linha, coluna) in self.alvos:
                continue

            parede_acima = (linha - 1, coluna) in self.paredes
            parede_abaixo = (linha + 1, coluna) in self.paredes
            parede_esquerda = (linha, coluna - 1) in self.paredes
            parede_direita = (linha, coluna + 1) in self.paredes

            bloqueio_vertical = parede_acima or parede_abaixo
            bloqueio_horizontal = parede_esquerda or parede_direita

            if bloqueio_vertical and bloqueio_horizontal:
                return True

        return False
    
    def _bloqueio_2x2(self, estado):
        # Detecta blocos 2x2 de paredes/caixas com caixa fora de alvo.
        _, caixas = estado

        for linha, coluna in caixas:
            # Só é necessário detectar blocos que prendam uma caixa fora do alvo.
            if (linha, coluna) in self.alvos:
                continue

            # Uma célula pertence a quatro possíveis blocos 2x2.
            for inicio_linha in (linha - 1, linha):
                for inicio_coluna in (coluna - 1, coluna):
                    bloco = (
                        (inicio_linha, inicio_coluna),
                        (inicio_linha, inicio_coluna + 1),
                        (inicio_linha + 1, inicio_coluna),
                        (inicio_linha + 1, inicio_coluna + 1),
                    )

                    todo_ocupado = all(
                        posicao in self.paredes or posicao in caixas
                        for posicao in bloco
                    )

                    if todo_ocupado:
                        return True

        return False