# UNIVERSIDADE FEDERAL DO PIAUÍ
## CENTRO DE CIÊNCIAS DA NATUREZA – CCN
## DEPARTAMENTO DE COMPUTAÇÃO
## PROJETO E ANÁLISE DE ALGORITMOS
### PROFESSOR CARLOS ANDRE BATISTA DE CARVALHO

**Allyson Kawa Santos da Silva**  
**Arthur Rabelo de Carvalho**  
**Raimundo Nonato Gomes Neto**  

---

# Coloração de Grafos: Um Estudo de Caso de Problema NP-Completo

## Resumo

Problemas NP-completos são desafios centrais em ciência da computação, sendo a Coloração de Grafos um dos mais clássicos e com diversas aplicações práticas. Este trabalho apresenta a formulação do problema, um cenário de aplicação real e uma implementação exata baseada em força bruta para servir de linha de base (baseline) para futuras comparações com heurísticas. A coloração consiste em atribuir cores aos vértices de um grafo, garantindo que vértices adjacentes não compartilhem a mesma cor e minimizando o número total de cores utilizadas. Também é explorada a execução real do algoritmo sobre uma instância com 18 disciplinas, discutindo seus resultados e desempenho computacional.

**Palavras-chave:** Coloração de grafos, NP-completo, algoritmos, força bruta, Python.

---

## 1. Introdução

Problemas NP-completos constituem uma classe de problemas computacionalmente difíceis, cuja solução exata exige tempo exponencial em função do tamanho da entrada. A coloração de grafos se destaca nesse conjunto por suas aplicações em áreas como alocação de horários, frequências de rádio e coloração de mapas. Neste trabalho, o problema é abordado com foco na compreensão de sua formulação, complexidade e implementação inicial.

## 2. Formulação do Problema

Dado um grafo $G = (V, E)$, o problema da coloração consiste em atribuir uma cor a cada vértice $v \in V$ de modo que nenhum par de vértices adjacentes compartilhe a mesma cor. O objetivo é minimizar o número de cores utilizadas — o chamado número cromático. Este problema é NP-completo para grafos gerais, conforme demonstrado por Karp (1972).

## 3. Aplicação Prática

Na organização de horários de um curso universitário, é necessário evitar conflitos para disciplinas do mesmo período ou ministradas pelo mesmo professor. Cada disciplina é modelada como um vértice, e uma aresta é criada entre duas disciplinas se elas não puderem ocorrer simultaneamente. O problema da coloração de grafos permite atribuir horários distintos às disciplinas adjacentes, resolvendo o problema de escalonamento com precisão formal.

## 4. Solução Ótima por Força Bruta

A abordagem exata adotada foi baseada em backtracking, testando recursivamente atribuições de cores e retrocedendo sempre que uma violação de restrição é encontrada. O algoritmo verifica, para cada vértice, todas as cores possíveis e continua o processo caso a atribuição seja válida.

O funcionamento do algoritmo pode ser descrito por três etapas principais:
- Construção do grafo com arestas entre disciplinas que compartilham professor ou período.
- Definição de um conjunto de cores (horários reais) que serão testados.
- Execução do algoritmo de backtracking, que tenta atribuir o menor número possível de cores sem violar os conflitos definidos pelas arestas.

A complexidade do algoritmo é exponencial: $O(k^n)$, onde $n$ é o número de vértices e $k$ o número de cores consideradas. Apesar de ineficiente para grandes grafos, essa solução é útil como referência para medir a qualidade de heurísticas.

## 5. Implementação em Python

*(Código omitido para brevidade)*

## 7. Execução em instância com 18 disciplinas

Para testar a viabilidade do algoritmo, foi utilizada uma entrada com 18 disciplinas, respeitando as regras de conflitos por período e professor. O grafo gerado a partir desses dados apresentou um total de 33 arestas, representando os conflitos entre as disciplinas.

A execução identificou corretamente todos os conflitos e encontrou uma coloração ótima utilizando 3 horários diferentes, sem sobreposição entre disciplinas conflitantes. A complexidade da execução foi influenciada diretamente pela densidade do grafo: como havia diversos conflitos cruzados, o algoritmo precisou explorar múltiplas combinações de cores até encontrar a distribuição mínima possível.

O algoritmo percorreu todas as combinações possíveis até encontrar a menor alocação viável (número cromático = 3), respeitando os horários disponíveis de segunda a sábado em quatro blocos diários.

## 8. Análise de Complexidade dos Algoritmos

Foram implementados quatro algoritmos para resolver o problema da coloração de grafos, visando obter soluções eficientes para o problema de alocação de horários de disciplinas universitárias: uma abordagem de força bruta para obtenção da solução ótima, e três heurísticas que buscam aproximações eficientes.

### 8.1 Força Bruta (Backtracking)

A abordagem por força bruta testa todas as combinações possíveis de atribuições de cores para os vértices do grafo, recorrendo ao retrocesso (backtracking) quando ocorre um conflito. Apesar de garantir a solução ótima, sua complexidade a torna impraticável para grafos de tamanho moderado ou grande.

- **Complexidade de Tempo:** $O(k^n)$, onde $k$ é o número de cores e $n$ o número de vértices.

#### Prova de Complexidade (Força Bruta)

Para cada um dos $n$ vértices, tentamos atribuir uma das $k$ cores possíveis. No pior caso, todas as combinações são testadas, resultando em $k^n$ possibilidades. Assim, a complexidade é $O(k^n)$.

---

### 8.2 Algoritmo Guloso

O algoritmo guloso percorre os vértices em uma ordem fixa, atribuindo a menor cor disponível que não gere conflito com os vizinhos já coloridos. É eficiente e simples, mas pode utilizar mais cores que o necessário.

- **Complexidade de Tempo:** $O(N + M)$, onde $N$ é o número de vértices e $M$ o número de arestas.

#### Prova de Complexidade (Guloso)

Para cada vértice, verificamos as cores dos seus vizinhos (no máximo grau máximo $d$). Como cada aresta é considerada duas vezes (uma para cada vértice), o custo total é proporcional ao número de arestas. Portanto, a complexidade é $O(N + M)$.

---

### 8.3 Heurística DSATUR

A heurística DSATUR seleciona a cada passo o vértice com maior saturação (maior número de cores distintas entre seus vizinhos). É mais sofisticada e gera soluções mais próximas da ótima, porém com maior custo computacional.

- **Complexidade de Tempo:** $O(N^2)$, onde $N$ é o número de vértices.

#### Prova de Complexidade (DSATUR)

A cada passo, é necessário selecionar o vértice de maior saturação, o que pode ser feito em $O(N)$, e atualizar as saturações, também em $O(N)$. Como há $N$ passos, a complexidade total é $O(N^2)$.

---

### 8.4 Algoritmo de Welsh-Powell

Este algoritmo ordena os vértices por grau decrescente e tenta colorir o máximo possível com uma mesma cor antes de passar para a próxima. Seu desempenho depende fortemente da ordem dos vértices.

- **Complexidade de Tempo:** $O(N^2)$, onde $N$ é o número de vértices.

#### Prova de Complexidade (Welsh-Powell)

Primeiro, os vértices são ordenados por grau ($O(N \log N)$). Para cada vértice, verificamos as cores dos seus vizinhos, o que pode ser feito em $O(N)$ no pior caso. Como há $N$ vértices, a complexidade é $O(N^2)$.

---

## 8.5 Prova de Complexidade por Método Mestre

O **Método Mestre** é utilizado para resolver recorrências do tipo:

$$
T(n) = aT\left(\frac{n}{b}\right) + f(n)
$$

onde:
- $a$ = número de subproblemas,
- $n/b$ = tamanho de cada subproblema,
- $f(n)$ = custo fora das chamadas recursivas.

**Exemplo:** Suponha um algoritmo recursivo para coloração de grafos por backtracking que, a cada passo, divide o problema em $k$ subproblemas (tentando $k$ cores para um vértice), com $n$ vértices restantes:

$$
T(n) = kT(n-1) + O(1)
$$

Esta recorrência não se encaixa diretamente no formato do método mestre, mas pode ser resolvida por expansão:

- $T(n) = kT(n-1) + c$
- $T(n-1) = kT(n-2) + c$
- ...
- $T(1) = c$

Expandindo:

$$
T(n) = kT(n-1) + c \\
= k[kT(n-2) + c] + c = k^2 T(n-2) + kc + c \\
= k^3 T(n-3) + k^2c + kc + c \\
= \dots \\
= k^{n-1} T(1) + c(k^{n-2} + k^{n-3} + \dots + 1)
$$

Como $T(1) = c$ e a soma é uma progressão geométrica:

$$
T(n) = k^{n-1}c + c\frac{k^{n-1} - 1}{k-1} \\
T(n) = O(k^n)
$$

Portanto, a complexidade do algoritmo de força bruta é **exponencial**.

---

## 9. Comparação de Desempenho

*(Resultados experimentais e gráficos omitidos para brevidade)*

---

## 10. Ambiente de Execução

- **Linguagem:** Python 3.11
- **Sistema Operacional:** Windows 11
- **Processador:** Intel Core i5 2,90 GHz x 6
- **Memória RAM:** 16 GB

---

## 11. Conclusão

A coloração de grafos, embora simples em sua definição, é um problema computacionalmente difícil. A implementação de uma solução exata baseada em backtracking oferece um ponto de partida sólido para estudos de heurísticas futuras. O próximo passo será propor e avaliar métodos aproximados mais eficientes, capazes de lidar com instâncias maiores.

---

## 12. Referências

- CORMEN, Thomas H.; LEISERSON, Charles E.; RIVEST, Ronald L.; STEIN, Clifford. Algoritmos: teoria e prática. 3. ed. Rio de Janeiro: Elsevier, 2013.
- ASLAN, Murat; BAYKAN, Nurdan Akhan. A Performance Comparison of Graph Coloring Algorithms. International Journal of Intelligence Systems and Applications in Engineering, Konia – Turkey, p. 266-273, 2016.
- ZIVIANI, NÍVIO. PROJETO DE ALGORITMOS COM IMPLEMENTAÇÕES EM PASCAL E C. UM PROJETO DE NIVIO ZIVIANI, PH.D., PROFESSOR EMÉRITO DO DEPARTAMENTO DE CIÊNCIA DA COMPUTAÇÃO, UNIVERSIDADE FEDERAL DE MINAS GERAIS. SÃO PAULO: PIONEIRA THOMSON.
- GRAPH ONLINE. Graph Online: Graph Visualization and Analysis Tool. Disponível em: https://graphonline.top.

---