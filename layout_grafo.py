import math
import random

def modern_vertex_sizes(grafo, nomes_disciplinas, min_vertex_size=26, max_vertex_size=46):
    degree = {nome: len(grafo[nome]) for nome in nomes_disciplinas}
    sum_degree = sum(degree.values())
    n = len(nomes_disciplinas)
    sum_of_diameters = n * ((min_vertex_size + max_vertex_size)/2)
    diametros = {}
    for v in nomes_disciplinas:
        if sum_degree > 0:
            diam = max(min((degree[v] / sum_degree) * sum_of_diameters, max_vertex_size), min_vertex_size)
        else:
            diam = min_vertex_size
        diametros[v] = diam
    return diametros

def organizar_vertices_automaticamente(grafo, nomes_disciplinas, largura, altura, iterations=150):
    nodes = list(nomes_disciplinas.keys())
    n = len(nodes)
    # random.seed(42)
    diametros = modern_vertex_sizes(grafo, nomes_disciplinas)
    # Inicialização: posições aleatórias centralizadas
    positions = {v: [random.uniform(0.3,0.9)*largura, random.uniform(0.3,0.9)*altura] for v in nodes}
    area = largura * altura
    k = math.sqrt(area / (n+1))
    temperature = largura / 2.0

    for iter in range(iterations):
        disp = {v: [0.0, 0.0] for v in nodes}
        # Repulsão
        for i, v in enumerate(nodes):
            for j, u in enumerate(nodes):
                if i == j: continue
                dx = positions[v][0] - positions[u][0]
                dy = positions[v][1] - positions[u][1]
                dist = math.hypot(dx, dy) + 0.01
                rep = k*k / dist
                disp[v][0] += dx/dist * rep
                disp[v][1] += dy/dist * rep
        # Atração
        for v in nodes:
            for u in grafo[v]:
                if u == v: continue
                dx = positions[v][0] - positions[u][0]
                dy = positions[v][1] - positions[u][1]
                dist = math.hypot(dx, dy) + 0.01
                attr = dist*dist / k
                disp[v][0] -= dx/dist * attr
                disp[v][1] -= dy/dist * attr
        # Atualiza posições
        for v in nodes:
            dx, dy = disp[v]
            disp_mag = math.hypot(dx, dy)
            if disp_mag > 0:
                dx = dx / disp_mag * min(disp_mag, temperature)
                dy = dy / disp_mag * min(disp_mag, temperature)
            positions[v][0] += dx
            positions[v][1] += dy
        # Mantém dentro da área visível
        for v in nodes:
            raio = diametros.get(v, 32)/2 + 5
            positions[v][0] = min(max(raio, positions[v][0]), largura-raio)
            positions[v][1] = min(max(raio, positions[v][1]), altura-raio)
        # Diminui temperatura
        temperature *= 0.95
    return positions