import json
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
import math
import time

tk.Tk().withdraw()

caminho_arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo JSON com as disciplinas",
    filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
    initialfile="entrada_disciplinas.json"
)

if not caminho_arquivo:
    messagebox.showerror("Erro", "Nenhum arquivo foi selecionado. Encerrando o programa.")
    exit()

# Carrega o arquivo JSON
try:
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_entrada:
        dados_disciplinas_json = json.load(arquivo_entrada)
except Exception as e:
    messagebox.showerror("Erro ao abrir o arquivo", f"Não foi possível ler o arquivo selecionado:\n{e}")
    exit()

# Construção do grafo de conflitos
grafo_conflitos = defaultdict(set) # set para evitar repetições
disciplinas_por_periodo = defaultdict(list)
disciplinas_por_professor = defaultdict(list)

for disciplina_info in dados_disciplinas_json:
    nome_disciplina = disciplina_info["nome"].strip()
    disciplinas_por_periodo[disciplina_info["periodo"]].append(nome_disciplina)
    disciplinas_por_professor[disciplina_info["professor"].strip()].append(nome_disciplina)

# Grafo de conflitos para disciplinas no mesmo período
for disciplinas_do_grupo in disciplinas_por_periodo.values():
    for i in range(len(disciplinas_do_grupo)):
        for j in range(i + 1, len(disciplinas_do_grupo)):
            A = disciplinas_do_grupo[i]
            B = disciplinas_do_grupo[j]
            grafo_conflitos[A].add(B)
            grafo_conflitos[B].add(A)

# Grafo de conflitos para disciplinas com o mesmo professor
for disciplinas_do_grupo in disciplinas_por_professor.values():
    for i in range(len(disciplinas_do_grupo)):
        for j in range(i + 1, len(disciplinas_do_grupo)):
            A = disciplinas_do_grupo[i]
            B = disciplinas_do_grupo[j]
            grafo_conflitos[A].add(B)
            grafo_conflitos[B].add(A)

# MATRIZ DE ADJACÊNCIA
disciplinas_ordenadas = sorted({disc["nome"] for disc in dados_disciplinas_json})
n = len(disciplinas_ordenadas)
matriz = [[0] * n for _ in range(n)]
for i, nome_i in enumerate(disciplinas_ordenadas):
    for j, nome_j in enumerate(disciplinas_ordenadas):
        if nome_j in grafo_conflitos[nome_i]:
            matriz[i][j] = 1

# COLORAÇÃO GULOSA
def colorir_grafo_guloso(grafo, ordem_vertices):
    coloracao = {}
    for v in ordem_vertices:
        usadas = {coloracao[u] for u in grafo[v] if u in coloracao}
        cor = 1
        while cor in usadas:
            cor += 1
        coloracao[v] = cor
    return coloracao

coloracao_gulosa = colorir_grafo_guloso(grafo_conflitos, disciplinas_ordenadas)
indices_disciplinas = {nome: i+1 for i, nome in enumerate(disciplinas_ordenadas)}

# VISUALIZAÇÃO DO GRAFO
def mostrar_grafo_colorizado(grafo, atribuicoes, nomes_disciplinas):
    import tkinter.font as tkFont
    raio = 16
    largura = 1050
    altura = 700
    legenda_largura = 200
    legenda_altura = 420
    colors = [
        "#ff0000", "#00ff00","#0000ff", "#00eeff", "#ff00ea",
        "#eeff00", "#505858", "#4b0069", "#00694a", "#A8570A",
        "#4B0C0C", "#1b3b11", "#0c1d33", "#2f5e3a", "#2b4de6"
    ]
    vertices = sorted(nomes_disciplinas, key=lambda x: nomes_disciplinas[x])
    n = len(vertices)
    centro_x = largura // 2 - 100
    centro_y = altura // 2
    raio_circular = min(centro_x, centro_y) - 100
    posicoes = {}
    for nome in vertices:
        idx = nomes_disciplinas[nome] - 1
        angle = 2 * math.pi * idx / n
        x = centro_x + int(raio_circular * math.cos(angle))
        y = centro_y + int(raio_circular * math.sin(angle))
        posicoes[nome] = [x, y]
    root = tk.Tk()
    root.title("Visualização do Grafo de Conflitos - Estilo GraphOnline")
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
                    eid = canvas.create_line(x1, y1, x2, y2, fill="#bbb", width=2, tags="aresta")
                    arestas_ids[(v, u)] = eid
        for nome in vertices:
            x, y = posicoes[nome]
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
            if (nx - x) ** 2 + (ny - y) ** 2 <= raio ** 2:
                arrastando["vertice"] = nome
                arrastando["offset_x"] = nx - x
                arrastando["offset_y"] = ny - y
                return
    def on_drag(event):
        v = arrastando["vertice"]
        if v is not None:
            x = event.x + arrastando["offset_x"]
            y = event.y + arrastando["offset_y"]
            x = max(raio, min(x, largura - raio - legenda_largura - 20))
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

# Horários reais
dias_com_folga = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
slots_de_horario_diarios = ["08:00–10:00", "10:00–12:00", "14:00–16:00", "16:00–18:00"]
pool_de_horarios_reais = [f"{dia} {slot}" for dia in dias_com_folga for slot in slots_de_horario_diarios]

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

    print(f"ℹ️  Iniciando busca por força bruta para {len(lista_ordenada_disciplinas)} disciplinas...")
    limite_k = min(len(lista_ordenada_disciplinas), len(pool_de_horarios))

    for k in range(1, limite_k + 1):
        print(f"⏳  Tentando resolver para k = {k} horários...")
        atribuicoes_numericas = {}
        if resolver_coloracao_backtracking(grafo_conflitos, k, lista_ordenada_disciplinas, 0, atribuicoes_numericas):
            print(f"✅  Solução ótima encontrada! Número mínimo de horários: {k}")
            horarios_finais = {}
            for disciplina, cor_num in atribuicoes_numericas.items():
                horarios_finais[disciplina] = pool_de_horarios[cor_num - 1]
            return horarios_finais, k

    print(f"🛑  Não foi possível encontrar uma solução com até {limite_k} horários.")
    return None, -1

# Execução da força bruta
inicio_execucao = time.time()
nomes_unicos_disciplinas = {disc["nome"].strip() for disc in dados_disciplinas_json}

horarios_otimos, numero_cromatico = encontrar_solucao_otima_baseline(
    grafo_conflitos,
    nomes_unicos_disciplinas,
    pool_de_horarios_reais
)

fim_execucao = time.time()
print(f"⏰  Tempo total de execução: {fim_execucao - inicio_execucao:.2f} segundos.")

if horarios_otimos:
    grade_final_otima = []
    for info_disciplina in dados_disciplinas_json:
        nome = info_disciplina["nome"].strip()
        horario = horarios_otimos.get(nome, "ERRO")
        grade_final_otima.append({
            "nome": nome,
            "professor": info_disciplina["professor"].strip(),
            "periodo": info_disciplina["periodo"],
            "horario": horario
        })

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
            json.dump(grade_final_otima, f, ensure_ascii=False, indent=4)
        print(f"✅  Tabela de horários salva em '{nome_arquivo_saida}'.")
else:
    print("⚠️  Não foi possível gerar a grade horária com solução ótima.")

# Salva a matriz de adjacência
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

# Visualização do grafo
mostrar_grafo_colorizado(grafo_conflitos, coloracao_gulosa, indices_disciplinas)