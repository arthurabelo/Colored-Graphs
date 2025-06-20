import os
import json
import time
import matplotlib.pyplot as plt
from alocacao_disciplinas import construir_grafo_conflitos,colorir_grafo_guloso,colorir_grafo_dsatur,encontrar_solucao_otima_baseline

PASTA_ENTRADAS = 'Outras quantidades de entradas'
ARQUIVOS_ENTRADA = sorted([
    f for f in os.listdir(PASTA_ENTRADAS)
    if f.endswith('.json')
], key=lambda x: int(x.split('.')[0]))

algoritmos = {
    'Guloso': colorir_grafo_guloso,
    'DSATUR': colorir_grafo_dsatur,
    'Força Bruta': None
}

resultados = {alg: [] for alg in algoritmos}
quantidades = []

for arquivo in ARQUIVOS_ENTRADA:
    caminho = os.path.join(PASTA_ENTRADAS, arquivo)
    with open(caminho, encoding='utf-8') as f:
        dados = json.load(f)
    disciplinas = [disc['nome'].strip() for disc in dados]
    grafo = construir_grafo_conflitos(dados)
    quantidades.append(len(disciplinas))
    
    # Guloso
    enable_guloso = True
    if len(disciplinas) >= 0 and len(disciplinas) <= 100 and enable_guloso == True:
        inicio = time.perf_counter()
        colorir_grafo_guloso(grafo, disciplinas)
        tempo_guloso = time.perf_counter() - inicio
        resultados['Guloso'].append(tempo_guloso)

    # DSATUR
    enable_dsatur = True
    if len(disciplinas) >= 0 and len(disciplinas) <= 100 and enable_dsatur == True:
        inicio = time.perf_counter()
        colorir_grafo_dsatur(grafo, disciplinas)
        tempo_dsatur = time.perf_counter() - inicio
        resultados['DSATUR'].append(tempo_dsatur)

    # Força Bruta
    enable_FB = False
    if len(disciplinas) >= 0 and len(disciplinas) <= 18 and enable_FB == True:
        inicio = time.perf_counter()
        encontrar_solucao_otima_baseline(grafo, disciplinas, list(range(1, len(disciplinas)+2)))
        tempo_fb = time.perf_counter() - inicio
        resultados['Força Bruta'].append(tempo_fb)

# Ajuste de unidade de tempo
all_times = [t for alg in resultados for t in resultados[alg] if t is not None]
max_time = max(all_times)
if max_time < 1:
    unidade = 'ms'
    fator = 1000
elif max_time < 60:
    unidade = 's'
    fator = 1
else:
    unidade = 'min'
    fator = 1/60

plt.figure(figsize=(10,6))
for alg, tempos in resultados.items():
    # Só plota se houver pelo menos um tempo válido
    if any(t is not None for t in tempos):
        # Filtra quantidades e tempos para remover None
        x = [q for q, t in zip(quantidades, tempos) if t is not None]
        y = [t*fator for t in tempos if t is not None]
        plt.plot(x, y, marker='.', label=alg)
plt.xlabel('Quantidade de Disciplinas', fontsize=12)
plt.ylabel(f'Tempo de Execução ({unidade})', fontsize=12)
plt.title('Comparação do Tempo de Execução dos Algoritmos de Alocação', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
