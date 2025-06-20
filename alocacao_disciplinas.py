import json
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import math
import time
import timeit
import random

from layout_grafo import modern_vertex_sizes, organizar_vertices_automaticamente
from tabela_horarios import gerar_tabelas_por_periodo

# Função para carregar o arquivo JSON de entrada
def carregar_dados_disciplinas():
    tk.Tk().withdraw() # Esconde a janela do Tkinter
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo JSON com as disciplinas",
        filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
        initialfile="entrada_disciplinas.json"
    )
    if not caminho_arquivo:
        messagebox.showerror("Erro", "Nenhum arquivo foi selecionado. Encerrando o programa.")
        exit()
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_entrada:
            dados_disciplinas_json = json.load(arquivo_entrada)
        # Ordena as disciplinas pelo nome
        dados_disciplinas_json = sorted(dados_disciplinas_json, key=lambda d: d["nome"].strip().lower())
    except Exception as e:
        messagebox.showerror("Erro ao abrir o arquivo", f"Não foi possível ler o arquivo selecionado:\n{e}")
        exit()
    return dados_disciplinas_json

def construir_grafo_conflitos(dados_disciplinas_json):
    grafo_conflitos = defaultdict(set)
    disciplinas_por_periodo = defaultdict(list)
    disciplinas_por_professor = defaultdict(list)
    for disciplina_info in dados_disciplinas_json:
        nome_disciplina = disciplina_info["nome"].strip()
        disciplinas_por_periodo[disciplina_info["periodo"]].append(nome_disciplina)
        disciplinas_por_professor[disciplina_info["professor"].strip()].append(nome_disciplina)
    for disciplinas_do_grupo in disciplinas_por_periodo.values():
        for i in range(len(disciplinas_do_grupo)):
            for j in range(i + 1, len(disciplinas_do_grupo)):
                A = disciplinas_do_grupo[i]
                B = disciplinas_do_grupo[j]
                grafo_conflitos[A].add(B)
                grafo_conflitos[B].add(A)
    for disciplinas_do_grupo in disciplinas_por_professor.values():
        for i in range(len(disciplinas_do_grupo)):
            for j in range(i + 1, len(disciplinas_do_grupo)):
                A = disciplinas_do_grupo[i]
                B = disciplinas_do_grupo[j]
                grafo_conflitos[A].add(B)
                grafo_conflitos[B].add(A)
    return grafo_conflitos

def criar_matriz_adjacencia(grafo_conflitos, disciplinas_ordenadas):
    n = len(disciplinas_ordenadas)
    matriz = [[0] * n for _ in range(n)]
    for i, nome_i in enumerate(disciplinas_ordenadas):
        for j, nome_j in enumerate(disciplinas_ordenadas):
            if nome_j in grafo_conflitos[nome_i]:
                matriz[i][j] = 1
    return matriz

# MÉTODO GULOSO
def colorir_grafo_guloso(grafo, ordem_vertices):
    coloracao = {}
    for v in ordem_vertices:
        usadas = {coloracao[u] for u in grafo[v] if u in coloracao}
        cor = 1
        while cor in usadas:
            cor += 1
        coloracao[v] = cor
    return coloracao

# HEURÍSTICA DSATUR

def colorir_grafo_dsatur(grafo, ordem_vertices):
    coloracao = {}
    saturacao = {v: 0 for v in ordem_vertices}
    graus = {v: len(grafo[v]) for v in ordem_vertices}
    nao_colorados = set(ordem_vertices)
    while nao_colorados:
        # Seleciona vértice de maior saturação (maior número de cores diferentes nos vizinhos)
        max_satur = -1
        candidatos = []
        for v in nao_colorados:
            cores_vizinhos = set(coloracao.get(u) for u in grafo[v] if u in coloracao)
            sat = len(cores_vizinhos)
            if sat > max_satur:
                max_satur = sat
                candidatos = [v]
            elif sat == max_satur:
                candidatos.append(v)
        # Se empate, escolhe o de maior grau
        if len(candidatos) > 1:
            v_escolhido = max(candidatos, key=lambda v: graus[v])
        else:
            v_escolhido = candidatos[0]
        cores_usadas = set(coloracao.get(u) for u in grafo[v_escolhido] if u in coloracao)
        cor = 1
        while cor in cores_usadas:
            cor += 1
        coloracao[v_escolhido] = cor
        nao_colorados.remove(v_escolhido)
    return coloracao

# FORÇA BRUTA / BACKTRACKING - BASELINE
def eh_atribuicao_valida(vertice, cor, grafo, atribuicoes_atuais):
    for vizinho in grafo[vertice]:
        if atribuicoes_atuais.get(vizinho) == cor:
            return False
    return True

def resolver_coloracao_backtracking(grafo, k_cores, vertices, indice_vertice, atribuicoes):
    if indice_vertice == len(vertices):
        return True
    vertice_atual = vertices[indice_vertice]
    for cor_candidata in range(1, k_cores + 1):
        if eh_atribuicao_valida(vertice_atual, cor_candidata, grafo, atribuicoes):
            atribuicoes[vertice_atual] = cor_candidata
            if resolver_coloracao_backtracking(grafo, k_cores, vertices, indice_vertice + 1, atribuicoes):
                return True
            del atribuicoes[vertice_atual]
    return False

def encontrar_solucao_otima_baseline(grafo_conflitos, todas_as_disciplinas, pool_de_horarios):
    lista_ordenada_disciplinas = sorted(list(todas_as_disciplinas))
    if not lista_ordenada_disciplinas:
        print("⚠️  Nenhuma disciplina encontrada para alocar.")
        return {}, 0
    limite_k = min(len(lista_ordenada_disciplinas), len(pool_de_horarios))
    for k in range(1, limite_k + 1):
        print(f"⏳  Tentando resolver para k = {k} horários...")
        atribuicoes_numericas = {}
        if resolver_coloracao_backtracking(grafo_conflitos, k, lista_ordenada_disciplinas, 0, atribuicoes_numericas):
            print(f"✅  Solução ótima encontrada! Número mínimo de horários: {k}")
            horarios_finais = {}
            for disciplina, cor_num in atribuicoes_numericas.items():
                horarios_finais[disciplina] = cor_num
            total_conflitos = sum(len(vizinhos) for vizinhos in grafo_conflitos.values()) // 2
            print(f"🔎 Quantidade de conflitos encontrados: {total_conflitos}")
            return horarios_finais, k
    print(f"🛑  Não foi possível encontrar uma solução com até {limite_k} horários.")
    exit(), -1

def mostrar_grafo_colorizado(grafo, atribuicoes, nomes_disciplinas):
    import tkinter.font as tkFont
    largura = 1050
    altura = 700
    legenda_largura = 200
    legenda_altura = 420
    colors = [
        "#FF0000", "#008000", "#0000FF", "#FF4800", "#F54FA2",
        "#FFA500", "#00FFFF", "#19FC24", "#A52A2A", "#580658"
    ]
    vertices = sorted(nomes_disciplinas, key=lambda x: nomes_disciplinas[x])
    n = len(vertices)
    diametros = modern_vertex_sizes(grafo, nomes_disciplinas)
    posicoes = organizar_vertices_automaticamente(grafo, nomes_disciplinas, largura - legenda_largura, altura)
    root = tk.Tk()
    root.title("Visualização do Grafo de Conflitos")
    canvas = tk.Canvas(root, width=largura, height=altura, bg="white", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    legenda_frame = tk.Frame(root, width=legenda_largura, height=legenda_altura)
    legenda_frame.pack(side="right", fill="y", padx=(5, 15), pady=20)
    legenda_frame.pack_propagate(False)
    legenda_canvas = tk.Canvas(legenda_frame, width=legenda_largura, height=legenda_altura, bg="#f9f9f9", highlightthickness=1, highlightbackground="#999")
    legenda_scrollbar = tk.Scrollbar(legenda_frame, orient="vertical", command=legenda_canvas.yview)
    legenda_canvas.configure(yscrollcommand=legenda_scrollbar.set)
    legenda_canvas.pack(side="left", fill="both", expand=True)
    legenda_scrollbar.pack(side="right", fill="y")
    legenda_inner = tk.Frame(legenda_canvas, bg="#f9f9f9")
    legenda_canvas.create_window((0, 0), window=legenda_inner, anchor="nw")
    def wrap_text(texto, largura_max, fonte=("Arial", 10)):
        f = tkFont.Font(family=fonte[0], size=fonte[1])
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            if f.measure(linha_atual + " " + palavra) > largura_max:
                linhas.append(linha_atual)
                linha_atual = palavra
            else:
                if linha_atual:
                    linha_atual += " " + palavra
                else:
                    linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return '\n'.join(linhas)
    arrastando = {"vertice": None, "offset_x": 0, "offset_y": 0}
    arestas_ids = {}
    nos_ids = {}
    textos_ids = {}
    def desenhar_tudo():
        canvas.delete("all")
        for v, vizinhos in grafo.items():
            x1, y1 = posicoes[v]
            for u in vizinhos:
                if nomes_disciplinas[u] > nomes_disciplinas[v]:
                    x2, y2 = posicoes[u]
                    dist = math.hypot(x1-x2, y1-y2)
                    raio1 = diametros[v]/2
                    raio2 = diametros[u]/2
                    # Ajusta linha para começar/terminar na borda do círculo (não no centro)
                    if dist > 1:
                        x1a = x1 + (x2-x1) * (raio1/dist)
                        y1a = y1 + (y2-y1) * (raio1/dist)
                        x2a = x2 + (x1-x2) * (raio2/dist)
                        y2a = y2 + (y1-y2) * (raio2/dist)
                    else:
                        x1a, y1a, x2a, y2a = x1, y1, x2, y2
                    eid = canvas.create_line(x1a, y1a, x2a, y2a, fill="#bbb", width=2, tags="aresta")
                    arestas_ids[(v, u)] = eid
        for nome in vertices:
            x, y = posicoes[nome]
            diam = diametros.get(nome, 32)
            raio = diam / 2
            cor = colors[(atribuicoes.get(nome, 0) - 1) % len(colors)] if nome in atribuicoes else "#cccccc"
            nid = canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=cor, outline="#444", width=2, tags="nodo")
            nos_ids[nome] = nid
            tid = canvas.create_text(x, y, text=str(nomes_disciplinas[nome]), font=("Arial", 12, "bold"), fill="black", tags="texto")
            textos_ids[nome] = tid
        for widget in legenda_inner.winfo_children():
            widget.destroy()
        tk.Label(legenda_inner, text="Legenda", font=("Arial", 15, "bold"), bg="#f9f9f9").pack(anchor="w", pady=(0,8))
        padding_vertical = 10
        max_text_width = legenda_largura - 40
        for i, nome in enumerate(vertices):
            cor = colors[(atribuicoes.get(nome, 0) - 1) % len(colors)] if nome in atribuicoes else "#cccccc"
            item_frame = tk.Frame(legenda_inner, bg="#f9f9f9")
            item_frame.pack(anchor="w", fill="x", pady=(0, padding_vertical))
            color_canvas = tk.Canvas(item_frame, width=14, height=14, bg="#f9f9f9", highlightthickness=0)
            color_canvas.create_oval(0, 0, 14, 14, fill=cor, outline="#333")
            color_canvas.pack(side="left", padx=(0,4))
            texto_legenda = f"{nomes_disciplinas[nome]}: {nome}"
            texto_legenda_wrapped = wrap_text(texto_legenda, max_text_width)
            tk.Label(item_frame, text=texto_legenda_wrapped, font=("Arial", 10), anchor="w", justify="left", bg="#f9f9f9").pack(side="left", fill="x", expand=True)
        legenda_inner.update_idletasks()
        legenda_canvas.configure(scrollregion=legenda_canvas.bbox("all"))
    desenhar_tudo()
    def on_press(event):
        x, y = event.x, event.y
        for nome in vertices:
            nx, ny = posicoes[nome]
            diam = diametros.get(nome, 32)
            raio = diam / 2
            if (nx - x) ** 2 + (ny - y) ** 2 <= raio ** 2:
                arrastando["vertice"] = nome
                arrastando["offset_x"] = nx - x
                arrastando["offset_y"] = ny - y
                return
    def on_drag(event):
        v = arrastando["vertice"]
        if v is not None:
            diam = diametros.get(v, 32)
            raio = diam / 2
            x = event.x + arrastando["offset_x"]
            y = event.y + arrastando["offset_y"]
            x = max(raio, min(x, largura - legenda_largura - raio))
            y = max(raio, min(y, altura - raio))
            posicoes[v] = [x, y]
            desenhar_tudo()
    def on_release(event):
        arrastando["vertice"] = None
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    def _on_mousewheel(event):
        legenda_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    legenda_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    root.mainloop()

def salvar_matriz_adjacencia(matriz):
    linhas_formatadas = ["[" + ", ".join(map(str, linha)) + "]" for linha in matriz]
    conteudo_simples = "\n".join(linhas_formatadas)
    nome_arquivo_saida = filedialog.asksaveasfilename(
        title="Salvar matriz de adjacência...",
        defaultextension=".json",
        filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
        initialfile="matriz_adjacencia.json"
    )
    if nome_arquivo_saida:
        with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
            f.write(conteudo_simples)
        print(f"✅ Matriz salva em: {nome_arquivo_saida}")
    else:
        print("❌ Salvamento da matriz cancelado.")

def salvar_grade_horarios(grade_final):
    nome_arquivo_saida = filedialog.asksaveasfilename(
        title="Salvar tabela de horários como...",
        defaultextension=".json",
        filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
        initialfile="grade_horarios.json"
    )
    if not nome_arquivo_saida:
        messagebox.showwarning("Aviso", "Nenhum local ou nome foi selecionado para salvar o arquivo.")
        print("⚠️  Salvar arquivo cancelado pelo usuário.")
    else:
        with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
            json.dump(grade_final, f, ensure_ascii=False, indent=4)
        print(f"✅  Tabela de horários salva em '{nome_arquivo_saida}'.")

dias_disponiveis = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
horarios_disponiveis = ["08:00–10:00", "10:00–12:00", "14:00–16:00", "16:00–18:00"]
dias_horarios_disponiveis = [f"{dia} {slot}" for dia in dias_disponiveis for slot in horarios_disponiveis]

def selecionar_algoritmo():
    root = tk.Tk()
    root.title("Algoritmo - Alocação de Disciplinas")
    root.geometry("350x140")
    root.resizable(False, True)
    root.eval('tk::PlaceWindow . center')
    var = tk.StringVar()
    var.set("")
    frame = tk.Frame(root)
    frame.pack(pady=20)
    tk.Label(frame, text="Selecione o algoritmo:", font=("Arial", 11)).pack(pady=(0, 10))
    combo = ttk.Combobox(frame, textvariable=var, state="readonly", font=("Arial", 11), width=22)
    combo['values'] = ("", "forcabruta", "guloso", "dsatur")
    combo.pack()
    def confirmar():
        root.quit()
    btn = tk.Button(root, text="Confirmar", command=confirmar, font=("Arial", 11), width=12, height=5)
    btn.pack(pady=10)
    root.mainloop()
    algoritmo = var.get()
    try:
        root.destroy()
    except tk.TclError:
        pass
    return algoritmo

def main():
    algoritmo = selecionar_algoritmo()
    if not algoritmo:
        messagebox.showerror("Erro", "Nenhuma opção foi selecionada. Encerrando o programa.")
        exit()
    algoritmo = algoritmo.strip().lower()
    dados_disciplinas_json = carregar_dados_disciplinas()
    disciplinas_ordenadas = [disc["nome"].strip() for disc in dados_disciplinas_json]
    indices_disciplinas = {nome: i+1 for i, nome in enumerate(disciplinas_ordenadas)}
    grafo_conflitos = construir_grafo_conflitos(dados_disciplinas_json)
    matriz = criar_matriz_adjacencia(grafo_conflitos, disciplinas_ordenadas)
    if algoritmo == "guloso":
        print(f"ℹ️  Iniciando alocação gulosa para {len(dados_disciplinas_json)} disciplinas...")
        inicio_execucao = timeit.default_timer()
        coloracao_gulosa = colorir_grafo_guloso(grafo_conflitos, disciplinas_ordenadas)
        fim_execucao = timeit.default_timer()
        print(f"✅  Alocação gulosa concluída! Número de horários utilizados: {max(coloracao_gulosa.values()) if coloracao_gulosa else 0}")
        total_conflitos = sum(len(vizinhos) for vizinhos in grafo_conflitos.values()) // 2
        print(f"🔎 Quantidade de conflitos encontrados: {total_conflitos}")
        print(f"⏰  Tempo total de execução (guloso): {fim_execucao - inicio_execucao:.6f} segundos.")
        grade_final = []
        for info_disciplina in dados_disciplinas_json:
            nome = info_disciplina["nome"].strip()
            cor = coloracao_gulosa.get(nome, 0)
            horario = dias_horarios_disponiveis[cor-1] if cor > 0 and cor <= len(dias_horarios_disponiveis) else "ERRO"
            grade_final.append({
                "nome": nome,
                "professor": info_disciplina["professor"].strip(),
                "periodo": info_disciplina["periodo"],
                "horario": horario
            })
        salvar_grade_horarios(grade_final)
        salvar_matriz_adjacencia(matriz)
        gerar_tabelas_por_periodo(grade_final, 'tabela_horarios.xlsx')
        print('Tabelas de horários por período geradas em tabela_horarios.xlsx')
        mostrar_grafo_colorizado(grafo_conflitos, coloracao_gulosa, indices_disciplinas)
    elif algoritmo == "forcabruta":
        print(f"ℹ️  Iniciando alocação por força bruta para {len(dados_disciplinas_json)} disciplinas...")
        inicio_execucao = timeit.default_timer()
        horarios_otimos, numero_cromatico = encontrar_solucao_otima_baseline(
            grafo_conflitos,
            disciplinas_ordenadas,
            dias_horarios_disponiveis
        )
        fim_execucao = timeit.default_timer()
        print(f"⏰  Tempo total de execução (força bruta): {fim_execucao - inicio_execucao:.6f} segundos.")
        if horarios_otimos:
            print(f"✅  Solução ótima encontrada! Número mínimo de horários: {numero_cromatico}")
            grade_final_otima = []
            for info_disciplina in dados_disciplinas_json:
                nome = info_disciplina["nome"].strip()
                cor = horarios_otimos.get(nome, 0)
                # Converte o índice para o nome do horário, igual ao guloso
                horario = dias_horarios_disponiveis[cor-1] if cor > 0 and cor <= len(dias_horarios_disponiveis) else "ERRO"
                grade_final_otima.append({
                    "nome": nome,
                    "professor": info_disciplina["professor"].strip(),
                    "periodo": info_disciplina["periodo"],
                    "horario": horario
                })
            salvar_grade_horarios(grade_final_otima)
            salvar_matriz_adjacencia(matriz)
            gerar_tabelas_por_periodo(grade_final_otima, 'tabela_horarios.xlsx')
            print('Tabelas de horários por período geradas em tabela_horarios.xlsx')
            mostrar_grafo_colorizado(grafo_conflitos, horarios_otimos, indices_disciplinas)
        else:
            print("⚠️  Não foi possível gerar a grade horária com solução ótima.")
            salvar_matriz_adjacencia(matriz)
    elif algoritmo == "dsatur":
        print(f"ℹ️  Iniciando alocação DSATUR para {len(dados_disciplinas_json)} disciplinas...")
        inicio_execucao = timeit.default_timer()
        coloracao_dsatur = colorir_grafo_dsatur(grafo_conflitos, disciplinas_ordenadas)
        fim_execucao = timeit.default_timer()
        print(f"✅  Alocação DSATUR concluída! Número de horários utilizados: {max(coloracao_dsatur.values()) if coloracao_dsatur else 0}")
        total_conflitos = sum(len(vizinhos) for vizinhos in grafo_conflitos.values()) // 2
        print(f"🔎 Quantidade de conflitos encontrados: {total_conflitos}")
        print(f"⏰  Tempo total de execução (DSATUR): {fim_execucao - inicio_execucao:.6f} segundos.")
        grade_final = []
        for info_disciplina in dados_disciplinas_json:
            nome = info_disciplina["nome"].strip()
            cor = coloracao_dsatur.get(nome, 0)
            horario = dias_horarios_disponiveis[cor-1] if cor > 0 and cor <= len(dias_horarios_disponiveis) else "ERRO"
            grade_final.append({
                "nome": nome,
                "professor": info_disciplina["professor"].strip(),
                "periodo": info_disciplina["periodo"],
                "horario": horario
            })
        salvar_grade_horarios(grade_final)
        salvar_matriz_adjacencia(matriz)
        gerar_tabelas_por_periodo(grade_final, 'tabela_horarios.xlsx')
        print('Tabelas de horários por período geradas em tabela_horarios.xlsx')
        mostrar_grafo_colorizado(grafo_conflitos, coloracao_dsatur, indices_disciplinas)
    else:
        messagebox.showerror("Erro", "Opção inválida. Encerrando o programa.")
        exit()

if __name__ == "__main__":
    main()
    exit()