# INTEGRANTES #

Andrei Gustavo de Lima Macedo, Auricelia Lima Sousa, Caroline Balko Piovesam e Pedro Henrique Hideo Makiyama.

# REQUISITOS #

- Python, versão 3.13.0;
- Tkinter disponível na instalação do Python;
- Ambiente gráfico para exibir a interface.

# COMO EXECUTAR #

Na pasta raiz do projeto, execute:

```bash
python src/main.py
```

No Windows, também é possível utilizar:

```bash
py src/main.py
```

Após isso:

- Selecione um dos três mapas (com 1 caixa, 2 caixas ou 3 caixas);
- Selecione o algoritmo de busca (UCS, Gulosa ou A*);
- Aguarde o processamento;
- Confira as métricas no terminal;
- Utilize a interface gráfica para acompanhar os movimentos da resolução.

# INTERFACE GRÁFICA #

A interface gráfica foi desenvolvida com o Tkinter e apresenta uma animação com os movimentos da solução, a qual o usuário pode controlar na seção "Controles de Animação".
Ela também mostra, na seção "Métricas da Execução", as métricas que foram previamente apresentadas no terminal (Custo (g), Passos, Nós Expandidos e Tempo (ms)).
Os símbolos e cores usadas para representar visualmente a solução são explicadas em legendas logo abaixo da animação.
A interface é aberta após o processamento, somente se houver uma solução para o mapa.

Em relação aos mecanismos de controle da animação, temos:

Play - apresenta os movimentos a partir do estado atual até o estado final da solução;
Anter. - volta ao estado anterior;
Prox. - avança para o próximo estado;
Reset - volta ao estado inicial;
Velocidade (ms) - slider que permite alterar a velocidade, em ms, dos movimentos;
Destacar nós expandidos - permite visualizar os nós expandidos na resolução.