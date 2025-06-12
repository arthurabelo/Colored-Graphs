import json
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
import math
import time

tk.Tk().withdraw()

# Seleção do arquivo de entrada
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

# Construção do grafo de conflitos e agrupamento
grafo_conflitos = defaultdict(set)
agrupamentos = {"periodo": defaultdict(list), "professor": defaultdict(list)}

for d in dados_disciplinas_json:
    nome = d["nome"].strip()
    agrupamentos["periodo"][d["periodo"]].append(nome)
    agrupamentos["professor"][d["professor"].strip()].append(nome)

for grupo in agrupamentos.values():
    for disciplinas in grupo.values():
        for i in range(len(disciplinas)):
            for j in range(i + 1, len(disciplinas)):
                A, B = disciplinas[i], disciplinas[j]
                grafo_conflitos[A].add(B)
                grafo_conflitos[B].add(A)

# MATRIZ DE ADJACÊNCIA
disciplinas_ordenadas = sorted({d["nome"].strip() for d in dados_disciplinas_json})
n = len(disciplinas_ordenadas)
matriz = [[int(disciplinas_ordenadas[j] in grafo_conflitos[disciplinas_ordenadas[i]]) for j in range(n)] for i in range(n)]

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
    raio, largura, altura = 16, 1050, 700
    legenda_largura, legenda_altura = 200, 420
    cores = [
        "#ff0000", "#00ff00","#0000ff", "#00eeff", "#ff00ea",
        "#eeff00", "#505858", "#4b0069", "#00694a", "#A8570A",
        "#4B0C0C", "#1b3b11", "#0c1d33", "#2f5e3a", "#2b4de6"
    ]
    vertices = sorted(nomes_disciplinas, key=lambda x: nomes_disciplinas[x])
    n = len(vertices)
    centro_x, centro_y = largura // 2 - 100, altura // 2
    raio_circular = min(centro_x, centro_y) - 100
    posicoes = {nome: [
        centro_x + int(raio_circular * math.cos(2 * math.pi * (nomes_disciplinas[nome] - 1) / n)),
        centro_y + int(raio_circular * math.sin(2 * math.pi * (nomes_disciplinas[nome] - 1) / n))
    ] for nome in vertices}
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
        palavras, linhas, linha_atual = texto.split(' '), [], ""
        for palavra in palavras:
            if f.measure(linha_atual + " " + palavra) > largura_max:
                linhas.append(linha_atual)
                linha_atual = palavra
            else:
                linha_atual = palavra if not linha_atual else linha_atual + " " + palavra
        if linha_atual: linhas.append(linha_atual)
        return '\n'.join(linhas)
    arrastando = {"vertice": None, "offset_x": 0, "offset_y": 0}
    def desenhar_tudo():
        canvas.delete("all")
        for v, vizinhos in grafo.items():
            x1, y1 = posicoes[v]
            for u in vizinhos:
                if nomes_disciplinas[u] > nomes_disciplinas[v]:
                    x2, y2 = posicoes[u]
                    canvas.create_line(x1, y1, x2, y2, fill="#bbb", width=2)
        for nome in vertices:
            x, y = posicoes[nome]
            cor = cores[(atribuicoes.get(nome, 0) - 1) % len(cores)] if nome in atribuicoes else "#cccccc"
            canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=cor, outline="#444", width=2)
            canvas.create_text(x, y, text=str(nomes_disciplinas[nome]), font=("Arial", 12, "bold"), fill="black")
        for widget in legenda_inner.winfo_children(): widget.destroy()
        tk.Label(legenda_inner, text="Legenda", font=("Arial", 15, "bold"), bg="#f9f9f9").pack(anchor="w", pady=(0,8))
        for i, nome in enumerate(vertices):
            cor = cores[(atribuicoes.get(nome, 0) - 1) % len(cores)] if nome in atribuicoes else "#cccccc"
            item_frame = tk.Frame(legenda_inner, bg="#f9f9f9")
            item_frame.pack(anchor="w", fill="x", pady=(0, 10))
            color_canvas = tk.Canvas(item_frame, width=14, height=14, bg="#f9f9f9", highlightthickness=0)
            color_canvas.create_oval(0, 0, 14, 14, fill=cor, outline="#333")
            color_canvas.pack(side="left", padx=(0,4))
            texto_legenda = f"{nomes_disciplinas[nome]}: {nome}"
            tk.Label(item_frame, text=wrap_text(texto_legenda, legenda_largura-40), font=("Arial", 10), anchor="w", justify="left", bg="#f9f9f9").pack(side="left", fill="x", expand=True)
        legenda_inner.update_idletasks()
        legenda_canvas.configure(scrollregion=legenda_canvas.bbox("all"))
    desenhar_tudo()
    def on_press(event):
        x, y = event.x, event.y
        for nome in vertices:
            nx, ny = posicoes[nome]
            if (nx - x) ** 2 + (ny - y) <= raio ** 2:
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
    def on_release(event): arrastando["vertice"] = None
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    legenda_canvas.bind_all("<MouseWheel>", lambda event: legenda_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    root.mainloop()

# Horários reais
dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
slots = ["08:00–10:00", "10:00–12:00", "14:00–16:00", "16:00–18:00"]
pool_de_horarios = [f"{dia} {slot}" for dia in dias for slot in slots]

def eh_atribuicao_valida(vertice, cor, grafo, atribuicoes):
    return all(atribuicoes.get(vizinho) != cor for vizinho in grafo[vertice])

def resolver_coloracao_backtracking(grafo, k, vertices, idx, atribuicoes):
    if idx == len(vertices): return True
    v = vertices[idx]
    for cor in range(1, k + 1):
        if eh_atribuicao_valida(v, cor, grafo, atribuicoes):
            atribuicoes[v] = cor
            if resolver_coloracao_backtracking(grafo, k, vertices, idx + 1, atribuicoes): return True
            del atribuicoes[v]
    return False

def encontrar_solucao_otima_baseline(grafo, todas_as_disciplinas, pool_horarios):
    lista_ordenada = sorted(todas_as_disciplinas)
    if not lista_ordenada:
        print("⚠️  Nenhuma disciplina encontrada para alocar.")
        return {}, 0
    limite_k = min(len(lista_ordenada), len(pool_horarios))
    for k in range(1, limite_k + 1):
        atribuicoes = {}
        if resolver_coloracao_backtracking(grafo, k, lista_ordenada, 0, atribuicoes):
            horarios = {disc: pool_horarios[cor-1] for disc, cor in atribuicoes.items()}
            print(f"✅  Solução ótima encontrada! Número mínimo de horários: {k}")
            return horarios, k
    print(f"🛑  Não foi possível encontrar uma solução com até {limite_k} horários.")
    return None, -1

# Execução da força bruta
inicio = time.time()
nomes_disciplinas = {d["nome"].strip() for d in dados_disciplinas_json}
horarios_otimos, numero_cromatico = encontrar_solucao_otima_baseline(grafo_conflitos, nomes_disciplinas, pool_de_horarios)
fim = time.time()
print(f"⏰  Tempo total de execução: {fim - inicio:.2f} segundos.")

if horarios_otimos:
    grade_final = [
        {
            "nome": d["nome"].strip(),
            "professor": d["professor"].strip(),
            "periodo": d["periodo"],
            "horario": horarios_otimos.get(d["nome"].strip(), "ERRO")
        }
        for d in dados_disciplinas_json
    ]
    nome_arquivo_saida = filedialog.asksaveasfilename(
        title="Salvar tabela de horários como...",
        defaultextension=".json",
        filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
        initialfile="grade_horarios.json"
    )
    if nome_arquivo_saida:
        with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
            json.dump(grade_final, f, ensure_ascii=False, indent=4)
        print(f"✅  Tabela de horários salva em '{nome_arquivo_saida}'.")
    else:
        messagebox.showwarning("Aviso", "Nenhum local ou nome foi selecionado para salvar o arquivo.")
        print("⚠️  Salvar arquivo cancelado pelo usuário.")
else:
    print("⚠️  Não foi possível gerar a grade horária com solução ótima.")

# Salva a matriz de adjacência
conteudo_matriz = "\n".join("[" + ", ".join(map(str, linha)) + "]" for linha in matriz)
nome_arquivo_saida = filedialog.asksaveasfilename(
    title="Salvar matriz de adjacência...",
    defaultextension=".json",
    filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
    initialfile="matriz_adjacencia.json"
)
if nome_arquivo_saida:
    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_matriz)
    print(f"✅ Matriz salva em: {nome_arquivo_saida}")
else:
    print("❌ Salvamento da matriz cancelado.")

# Visualização do grafo
mostrar_grafo_colorizado(grafo_conflitos, coloracao_gulosa, indices_disciplinas)