import json
from collections import defaultdict
import time  # Para medir o tempo de execução
import tkinter as tk
from tkinter import filedialog, messagebox

# Inicializa a janela Tk (mas oculta ela)
tk.Tk().withdraw()

# Abre janela para o usuário escolher o arquivo
caminho_arquivo = filedialog.askopenfilename(
    title="Selecione o arquivo JSON com as disciplinas",
    filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
)

# Verifica se o usuário selecionou um arquivo
if not caminho_arquivo:
    messagebox.showerror("Erro", "Nenhum arquivo foi selecionado. Encerrando o programa.")
    exit()

# Tenta carregar o arquivo JSON selecionado
try:
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_entrada:
        dados_disciplinas_json = json.load(arquivo_entrada)
except Exception as e:
    messagebox.showerror("Erro ao abrir o arquivo", f"Não foi possível ler o arquivo selecionado:\n{e}")
    exit()

# O grafo representa quais disciplinas NÃO PODEM ocorrer no mesmo horário.
grafo_conflitos = defaultdict(set)
disciplinas_por_periodo = defaultdict(list)
disciplinas_por_professor = defaultdict(list)

for disciplina_info in dados_disciplinas_json:
    nome_disciplina = disciplina_info["nome"].strip()
    disciplinas_por_periodo[disciplina_info["periodo"]].append(nome_disciplina)
    disciplinas_por_professor[disciplina_info["professor"].strip()].append(nome_disciplina)

# Conflitos por período
for disciplinas_do_grupo in disciplinas_por_periodo.values():
    for i in range(len(disciplinas_do_grupo)):
        for j in range(i + 1, len(disciplinas_do_grupo)):
            A = disciplinas_do_grupo[i]
            B = disciplinas_do_grupo[j]
            grafo_conflitos[A].add(B)
            grafo_conflitos[B].add(A)

# Conflitos por professor
for disciplinas_do_grupo in disciplinas_por_professor.values():
    for i in range(len(disciplinas_do_grupo)):
        for j in range(i + 1, len(disciplinas_do_grupo)):
            A = disciplinas_do_grupo[i]
            B = disciplinas_do_grupo[j]
            grafo_conflitos[A].add(B)
            grafo_conflitos[B].add(A)

# --- Definição do pool de horários ---
dias_com_folga = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
slots_de_horario_diarios = ["08:00–10:00", "10:00–12:00", "14:00–16:00", "16:00–18:00"]
pool_de_horarios_reais = [f"{dia} {slot}" for dia in dias_com_folga for slot in slots_de_horario_diarios]

# --- Algoritmo de backtracking ---

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

# --- Execução principal ---
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
        initialfile="grade_horarios_otima.json"
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

# --- Salvamento da matriz de adjacência em formato simples ---

# Construção da matriz
disciplinas_ordenadas = sorted(nomes_unicos_disciplinas)
indice_disciplina = {nome: idx for idx, nome in enumerate(disciplinas_ordenadas)}
tamanho = len(disciplinas_ordenadas)
matriz = [[0] * tamanho for _ in range(tamanho)]

for i, nome_i in enumerate(disciplinas_ordenadas):
    for j, nome_j in enumerate(disciplinas_ordenadas):
        if nome_j in grafo_conflitos[nome_i]:
            matriz[i][j] = 1

# Preparar conteúdo como linhas simples
linhas_formatadas = ["[" + ", ".join(map(str, linha)) + "]" for linha in matriz]
conteudo_simples = "\n".join(linhas_formatadas)

# Diálogo para salvar o arquivo
nome_arquivo_saida = filedialog.asksaveasfilename(
    title="Salvar matriz de adjacência...",
    defaultextension=".json",
    filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
    initialfile="matriz_adjacencia.json"
)

# Salvar se o usuário confirmar
if nome_arquivo_saida:
    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_simples)
    print(f"✅ Matriz salva com sucesso: {nome_arquivo_saida}")
else:
    print("❌ Salvamento da matriz cancelado.")
