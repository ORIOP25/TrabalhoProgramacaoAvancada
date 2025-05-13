import tkinter as tk
from tkinter import messagebox, filedialog
import re
import googlemaps
from datetime import datetime

# Inicializa API Google Maps
APIKey = "AIzaSyChx6k85OBC3Bwf-HSVuNf8dYA848DiPdo"
Maps = googlemaps.Client(key=APIKey)

# Lista de itinerários com metadados para ordenação
itinerarios_dados = []


# Função para limpar campos
def limpar_campos():
    entrada_local.delete(0, tk.END)
    entrada_cidade.delete(0, tk.END)
    var_tipo.set(tipos[0])
    entrada_data.delete(0, tk.END)
    entrada_hora.delete(0, tk.END)
    entrada_notas.delete("1.0", tk.END)


# Variável para armazenar o índice do itinerário selecionado
itinerario_selecionado_index = None


# Função principal para adicionar itinerário
def adicionar_itinerario():
    global itinerario_selecionado_index  # Adiciona o global aqui para garantir o uso correto da variável
    local = entrada_local.get().strip()
    cidade = entrada_cidade.get().strip()
    tipo = var_tipo.get()
    data = entrada_data.get().strip()
    hora = entrada_hora.get().strip()
    notas = entrada_notas.get("1.0", tk.END).strip()

    if not (local and cidade and tipo and data and hora):
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos obrigatórios.")
        return

    if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$", data):
        messagebox.showerror("Data inválida", "A data deve estar no formato DD/MM/YYYY.")
        return

    if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", hora):
        messagebox.showerror("Hora inválida", "A hora deve estar no formato 24:00.")
        return

    try:
        data_hora_obj = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
    except ValueError:
        messagebox.showerror("Erro", "Data e hora inválidas.")
        return

    # Cálculo da rota
    origem = local
    destino = cidade

    try:
        direcoes = Maps.directions(origem, destino, mode="driving", language="pt-pt")
        if direcoes:
            distancia = direcoes[0]['legs'][0]['distance']['text']
            duracao = direcoes[0]['legs'][0]['duration']['text']
            rota_info = f"Distância - {distancia}\n     Duração - {duracao}"
        else:
            rota_info = "Rota não encontrada."
    except Exception as e:
        rota_info = f"Erro ao calcular rota: {e}"

    resumo = (
        f"📍 De {local} até {cidade}\n"
        f"     Tipo de Atividade - Viagem {tipo}\n"
        f"     Data - {data}\n"
        f"     Hora - {hora}\n"
        f"     {rota_info}"
    )

    if notas:
        resumo += f"\n     Notas - {notas}"

    # Se um itinerário foi selecionado, atualiza-o
    if itinerario_selecionado_index is not None:
        itinerarios_dados[itinerario_selecionado_index] = (data_hora_obj, resumo)
        messagebox.showinfo("Atualização", "Itinerário atualizado com sucesso!")
    else:
        itinerarios_dados.append((data_hora_obj, resumo))

    itinerario_selecionado_index = None  # Reseta o índice após a atualização
    itinerarios_dados.sort()  # Ordena por data/hora

    # Atualizar área de texto com todos os itinerários
    atualizar_texto_itinerarios()
    limpar_campos()


def atualizar_texto_itinerarios():
    texto_itinerarios.config(state=tk.NORMAL)
    texto_itinerarios.delete("1.0", tk.END)
    for _, item in itinerarios_dados:
        texto_itinerarios.insert(tk.END, item + "\n\n")
    texto_itinerarios.config(state=tk.DISABLED)


# Função para exportar itinerários em .txt
def exportar_itinerarios():
    if not itinerarios_dados:
        messagebox.showinfo("Exportar", "Nenhum itinerário para exportar.")
        return

    caminho = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if caminho:
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                for _, item in itinerarios_dados:
                    f.write(item + "\n")
            messagebox.showinfo("Exportar", f"Itinerários exportados com sucesso para {caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")


# Função para importar itinerários de .txt
def importar_itinerarios():
    caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if caminho:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()  # Lê o ficheiro inteiro
                blocos = conteudo.split("\n\n")  # Divide em blocos separados por linhas em branco

            itinerarios_dados.clear()
            for bloco in blocos:
                match = re.search(r"Data\s*-\s*(\d{2}/\d{2}/\d{4})\n\s*Hora\s*-\s*(\d{2}:\d{2})", bloco)
                if match:
                    data_str, hora_str = match.groups()
                    try:
                        data_hora_obj = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M")
                        itinerarios_dados.append((data_hora_obj, bloco.strip()))
                    except ValueError:
                        continue

            itinerarios_dados.sort()
            # Atualizar área de texto com todos os itinerários
            texto_itinerarios.delete("1.0", tk.END)
            for _, item in itinerarios_dados:
                texto_itinerarios.insert(tk.END, item + "\n\n")
            messagebox.showinfo("Importar", "Itinerários importados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar: {e}")

    atualizar_texto_itinerarios()


def clicar_registo(event):
    global itinerario_selecionado_index
    index = texto_itinerarios.index(f"@{event.x},{event.y}")
    linha = texto_itinerarios.get(index + " linestart", index + " lineend").strip()

    # Procura o itinerário correspondente
    for i, (_, resumo) in enumerate(itinerarios_dados):  # antes estava: "for _, resumo in itinerarios_dados:"
        if linha and linha in resumo:
            preencher_formulario(resumo)
            itinerario_selecionado_index = i  # Armazena o índice do itinerário selecionado
            break


def preencher_formulario(texto):
    match_local = re.search(r"De (.*?) até", texto)
    match_cidade = re.search(r"até (.*?)\n", texto)
    match_tipo = re.search(r"Viagem (.*?)\n", texto)
    match_data = re.search(r"Data - (.*?)\n", texto)
    match_hora = re.search(r"Hora - (.*?)\n", texto)
    match_notas = re.search(r"Notas - (.*)", texto)

    if match_local:
        entrada_local.delete(0, tk.END)
        entrada_local.insert(0, match_local.group(1))

    if match_cidade:
        entrada_cidade.delete(0, tk.END)
        entrada_cidade.insert(0, match_cidade.group(1))

    if match_tipo:
        var_tipo.set(match_tipo.group(1))

    if match_data:
        entrada_data.delete(0, tk.END)
        entrada_data.insert(0, match_data.group(1))

    if match_hora:
        entrada_hora.delete(0, tk.END)
        entrada_hora.insert(0, match_hora.group(1))

    if match_notas:
        entrada_notas.delete("1.0", tk.END)
        entrada_notas.insert("1.0", match_notas.group(1))


# Interface gráfica
janela = tk.Tk()
janela.title("Formulário de Planeamento de Viagens")
janela.geometry("700x700")
janela.configure(bg="#f0f4f7")

tk.Label(janela, text="📌 Adicionar Itinerário", font=("Helvetica", 23, "bold"), bg="#f0f4f7", fg="#2a4d69").pack(
    pady=10)

frame = tk.Frame(janela, bg="#f0f4f7")
frame.pack(pady=10)

# Campos
tk.Label(frame, text="Localização Atual:", bg="#f0f4f7", font=("Arial", 13, "bold")).grid(row=0, column=0, sticky="e",
                                                                                          pady=5)
entrada_local = tk.Entry(frame, width=40, font=("Arial", 11))
entrada_local.grid(row=0, column=1)

tk.Label(frame, text="Para onde deseja ir:", bg="#f0f4f7", font=("Arial", 13, "bold")).grid(row=1, column=0, sticky="e",
                                                                                            pady=5)
entrada_cidade = tk.Entry(frame, width=40, font=("Arial", 11))
entrada_cidade.grid(row=1, column=1)

tk.Label(frame, text="Tipo de Atividade:", bg="#f0f4f7", font=("Arial", 13, "bold")).grid(row=2, column=0, sticky="e",
                                                                                          pady=5)
tipos = ["Cultural", "Desportiva", "Gastronómica", "Outro"]
var_tipo = tk.StringVar(value=tipos[0])
dropdown_tipo = tk.OptionMenu(frame, var_tipo, *tipos)
dropdown_tipo.config(font=("Arial", 11))
dropdown_tipo.grid(row=2, column=1, sticky="w")

tk.Label(frame, text="Data (DD/MM/YYYY):", bg="#f0f4f7", font=("Arial", 13, "bold")).grid(row=3, column=0, sticky="e",
                                                                                          pady=5)
entrada_data = tk.Entry(frame, width=11, font=("Arial", 11))
entrada_data.grid(row=3, column=1, sticky="w")

tk.Label(frame, text="Hora (HH:MM):", bg="#f0f4f7", font=("Arial", 13, "bold")).grid(row=4, column=0, sticky="e",
                                                                                     pady=5)
entrada_hora = tk.Entry(frame, width=6, font=("Arial", 11))
entrada_hora.grid(row=4, column=1, sticky="w")

tk.Label(frame, text="Notas:", bg="#f0f4f7", font=("Arial", 13, "bold")).grid(row=5, column=0, sticky="ne", pady=5)
entrada_notas = tk.Text(frame, width=40, height=4, font=("Arial", 11))
entrada_notas.grid(row=5, column=1, pady=5)

tk.Button(janela, text="➕ Adicionar Itinerário", command=adicionar_itinerario, bg="#2a4d69", font=("Arial", 13, "bold"),
          fg="white", padx=10, pady=5).pack(pady=10)

# Área de texto para mostrar os itinerários
frame_texto = tk.Frame(janela, bg="#f0f4f7")
frame_texto.pack(pady=10)

texto_itinerarios = tk.Text(frame_texto, width=70, height=12, bg="white", font=("Arial", 10))
texto_itinerarios.pack(side=tk.LEFT)
texto_itinerarios.config(state=tk.DISABLED)  # Torna somente leitura

texto_itinerarios.bind("<Button-1>", clicar_registo)

# Scrollbar ligada ao Text
scrollbar = tk.Scrollbar(frame_texto, command=texto_itinerarios.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
texto_itinerarios.config(yscrollcommand=scrollbar.set)

# Botões de exportação/importação
frame_botoes = tk.Frame(janela, bg="#f0f4f7")
frame_botoes.pack(pady=5)

tk.Button(frame_botoes, text="Exportar Itinerários", command=exportar_itinerarios, bg="#4CAF50",
          font=("Arial", 13, "bold"), fg="white", padx=10).grid(row=0, column=0, padx=10)
tk.Button(frame_botoes, text="Importar Itinerários", command=importar_itinerarios, bg="#2196F3",
          font=("Arial", 13, "bold"), fg="white", padx=10).grid(row=0, column=1, padx=10)

tk.Label(janela, text="Projeto Final Programação Avançada - Grupo 4 ✈️", font=("Arial", 10), bg="#f0f4f7",
         fg="#888").pack(pady=5)

janela.mainloop()