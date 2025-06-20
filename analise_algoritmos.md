# Análise de Complexidade dos Algoritmos: Força Bruta e Guloso

Este documento apresenta uma análise detalhada e técnica da complexidade dos algoritmos de força bruta e guloso implementados no projeto de alocação de disciplinas, com base nos princípios da análise de algoritmos.

## 1. Algoritmo de Força Bruta

### Descrição Geral
O algoritmo de força bruta busca todas as possíveis combinações de alocação de disciplinas aos horários, verificando cada possibilidade para encontrar uma solução válida que satisfaça todas as restrições do problema.

### Complexidade de Tempo
A complexidade de tempo do algoritmo de força bruta é, em geral, **exponencial**. Supondo que temos `n` disciplinas e `m` horários possíveis para cada disciplina, o número total de combinações possíveis é `m^n`.

- **Pior caso:** O algoritmo pode precisar verificar todas as `m^n` combinações para encontrar uma solução válida.
- **Complexidade:** O(n) = O(m^n)

#### Justificativa
Cada disciplina pode ser alocada em qualquer um dos horários disponíveis, e o algoritmo tenta todas as possibilidades. Para cada combinação, é necessário verificar se as restrições são satisfeitas, o que pode adicionar um fator polinomial, mas o termo dominante é o número de combinações.

### Complexidade de Espaço
A complexidade de espaço também pode ser **exponencial**, pois o algoritmo pode armazenar todas as combinações possíveis em memória, dependendo da implementação.

## 2. Algoritmo Guloso

### Descrição Geral
O algoritmo guloso faz escolhas locais ótimas em cada etapa, alocando disciplinas aos horários de acordo com algum critério (por exemplo, menor número de conflitos ou maior prioridade), sem considerar todas as combinações possíveis.

### Complexidade de Tempo
A complexidade de tempo do algoritmo guloso é, em geral, **polinomial**. Supondo `n` disciplinas e `m` horários:

- Para cada disciplina, o algoritmo avalia até `m` horários possíveis.
- **Complexidade:** O(n * m)

#### Justificativa
O algoritmo percorre cada disciplina e, para cada uma, avalia as opções disponíveis de forma sequencial, escolhendo a melhor opção local. Não há necessidade de explorar todas as combinações, o que reduz drasticamente o tempo de execução em relação ao método de força bruta.

### Complexidade de Espaço
A complexidade de espaço é **linear** ou **polinomial**, pois o algoritmo armazena apenas a solução parcial ou final, sem manter todas as combinações possíveis em memória.

## 3. Comparação Resumida

| Algoritmo      | Complexidade de Tempo | Complexidade de Espaço |
|---------------|----------------------|-----------------------|
| Força Bruta   | O(m^n)               | O(m^n)                |
| Guloso        | O(n * m)             | O(n) ou O(n * m)      |

## 4. Considerações Finais
- O algoritmo de força bruta garante encontrar a solução ótima, mas é inviável para instâncias grandes devido ao crescimento exponencial.
- O algoritmo guloso é eficiente e prático para grandes instâncias, mas pode não garantir a solução ótima, apenas uma solução viável e geralmente boa.

> **Nota:** As análises acima consideram o pior caso e podem variar conforme detalhes específicos da implementação e restrições do problema.
