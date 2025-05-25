# Importação de bibliotecas necessárias
import tkinter as tk                                # Interface gráfica
from tkinter import ttk, messagebox, filedialog     # Widgets avançados, janelas de aviso e seleção de ficheiros
import re                                           # Expressões regulares para validações
import googlemaps                                   # API do Google Maps para distâncias
from datetime import datetime                       # Para manipular datas e horas
import mysql.connector                              # Ligação à base de dados MySQL
from mysql.connector import errorcode               # Códigos de erro específicos do MySQL

# --- Base de Dados ---
# Configuração da ligação à base de dados MySQL
config = {
    'user': 'dev',                         # Nome de utilizador da base de dados (alterar user)
    'password': '',                         # Palavra-passe da base de dados (alterar password)
    'host': 'localhost',                    # Endereço do servidor
    'database': 'planejamento_viagens',     # Nome da base de dados
    'raise_on_warnings': True               # Mostra avisos como exceções
}

# Função responsável por criar a base de dados e as tabelas
def criar_base_e_tabelas():
    conn = None         # Variável para a ligação à base de dados
    cursor = None       # Variável para executar comandos SQL

    try:
        # Estabelece ligação ao servidor MySQL (ainda sem selecionar a base de dados)
        conn = mysql.connector.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            database=config['database']
        )
        cursor = conn.cursor()      # Cria o cursor para enviar comandos SQL
        # Cria a base de dados se ainda não existir, com codificação UTF8mb4 (suporte a emojis, ...)
        cursor.execute("CREATE DATABASE IF NOT EXISTS planejamento_viagens DEFAULT CHARACTER SET 'utf8mb4'")
        print("Base de dados criada ou já existe.")
        conn.database = config['database']      # Seleciona a base de dados criada

        cursor.execute("DELETE FROM itinerario_atracoes")
        cursor.execute("DELETE FROM itinerarios")
        cursor.execute("DELETE FROM atracoes")
        cursor.execute("DELETE FROM utilizadores")
        conn.commit()

        # Definição da tabela "utilizadores" (NÃO UTILIZADA)
        tabela_utilizadores = """
        CREATE TABLE IF NOT EXISTS utilizadores (
            id INT AUTO_INCREMENT PRIMARY KEY,      -- ID automático e chave primária
            nome VARCHAR(100) NOT NULL UNIQUE       -- Nome obrigatório e único
        )
        """

        # Definição da tabela "itinerarios"  (NÃO UTILIZADA)
        tabela_itinerarios = """
        CREATE TABLE IF NOT EXISTS itinerarios (
            id INT AUTO_INCREMENT PRIMARY KEY,          -- ID automático
            local_inicial VARCHAR(255) NOT NULL,
            local_final VARCHAR(255) NOT NULL,
            tipo VARCHAR(100) NOT NULL,
            data DATE NOT NULL,
            horario TIME NOT NULL,
            notas_opcionais TEXT
        )
        """
        # Definição da tabela "atracoes"  (UTILIZADA)
        tabela_atracoes = """
        CREATE TABLE IF NOT EXISTS atracoes (
            id INT AUTO_INCREMENT PRIMARY KEY,   -- ID automático
            nome VARCHAR(255) NOT NULL,          -- Nome da atração (obrigatório)
            morada VARCHAR(255),                 -- Morada da atração
            cidade VARCHAR(100),                 -- Cidade onde está localizada
            tipo VARCHAR(50)                     -- Tipo da atração (ex: parque, museu)
        )
        """

        # Execução dos comandos SQL para criar cada tabela
        cursor.execute(tabela_utilizadores)
        cursor.execute(tabela_itinerarios)
        cursor.execute(tabela_atracoes)
        print("Tabelas criadas ou já existem.")     # Confirmação visual no terminal
        conn.commit()       # Confirma as alterações na base de dados
    # Tratamento de erros do MySQL
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: usuário ou senha inválidos.")      # Caso o login falhe
        else:
            print(err)      # Outros erros
    # Fecha o cursor e a ligação, mesmo que ocorra erro
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

# Funções CRUD para itinerários
# Função para inserir um novo itinerário na base de dados
def inserir_itinerario(id_utilizador, nome_itinerario, data_inicio, data_fim):
    try:
        # Estabelece ligação à base de dados usando as configurações definidas
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        # Executa a instrução SQL para inserir um novo registo na tabela 'itinerarios'
        # Os valores são passados em forma de tupla (para evitar SQL injection)
        cursor.execute(
            "INSERT INTO itinerarios (id_utilizador, nome_itinerario, data_inicio, data_fim) VALUES (%s, %s, %s, %s)",
            (id_utilizador, nome_itinerario, data_inicio, data_fim)
        )
        conn.commit()       # Confirma a alteração à base de dados
        print(f"Itinerário '{nome_itinerario}' inserido.")      # Mensagem a indicar sucesso
    # Captura e mostra erros que possam ocorrer durante a inserção
    except mysql.connector.Error as err:
        print(f"Erro ao inserir itinerário: {err}")
    # Fecha o cursor e a ligação à base de dados, independentemente de ter havido erro ou não
    finally:
        cursor.close()
        conn.close()

# Função para ler (listar) todos os itinerários da base de dados
def ler_todos_itinerarios():
    try:
        # Estabelece ligação à base de dados com as credenciais fornecidas
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itinerarios")     # Executa um comando SQL para obter todos os registos da tabela 'itinerarios'
        return cursor.fetchall()        # Retorna todos os resultados como uma lista de tuplas
    # Se houver algum erro durante a ligação ou execução do SQL, é tratado aqui
    except mysql.connector.Error as err:
        print(f"Erro ao ler itinerários: {err}")
        return []       # Retorna uma lista vazia em caso de erro
    # Fecha sempre o cursor e a ligação para liberar recursos
    finally:
        cursor.close()
        conn.close()

# Função para apagar (remover) um itinerário da base de dados com base no seu ID
def apagar_itinerario(id_itinerario):
    try:
        # Estabelece ligação à base de dados com as configurações fornecidas
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        # Executa um comando SQL para apagar o itinerário com o ID fornecido
        cursor.execute("DELETE FROM itinerarios WHERE id = %s", (id_itinerario,))
        conn.commit()       # Confirma a alteração na base de dados
        print(f"Itinerário com id {id_itinerario} apagado.")        # Mensagem de sucesso no terminal
    # Captura e exibe qualquer erro que ocorra durante o processo
    except mysql.connector.Error as err:
        print(f"Erro ao apagar itinerário: {err}")
    # Garante que o cursor e a conexão são fechados, independentemente do sucesso ou erro
    finally:
        cursor.close()
        conn.close()

# Funções CRUD para atrações
# Função para inserir uma nova atração turística na base de dados
def inserir_atracao(nome, morada, cidade, tipo):
    try:
        # Estabelece ligação à base de dados com as credenciais definidas no dicionário config
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        # Verifica se já existe uma atração com o mesmo nome e morada
        cursor.execute("SELECT id FROM atracoes WHERE nome=%s AND morada=%s", (nome, morada))
        result = cursor.fetchall()      # Lê todos os resultados para evitar erros de buffer
        if result:
            # Se já existir uma atração com o mesmo nome e morada, não insere novamente
            print(f"Atracao '{nome}' já existe. Ignorando inserção.")
        else:
            # Prepara e executa a query de inserção na tabela atracoes
            sql = "INSERT INTO atracoes (nome, morada, cidade, tipo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nome, morada, cidade, tipo))
            conn.commit()       # Confirma a inserção na base de dados
            print(f"Atracao '{nome}' inserida com sucesso.")
    # Em caso de erro com o MySQL (como problema de ligação ou sintaxe), mostra mensagem
    except mysql.connector.Error as err:
        print(f"Erro ao inserir atração '{nome}': {err}")
    # Fecha sempre o cursor e a ligação, mesmo que haja erro
    finally:
        cursor.close()
        conn.close()

# Função para ler (listar) todas as atrações da base de dados
def ler_todas_atracoes():
    try:
        # Estabelece a ligação à base de dados com as configurações fornecidas
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        # Executa uma query para obter todas as colunas de todas as linhas da tabela atracoes
        cursor.execute("SELECT * FROM atracoes")
        return cursor.fetchall()        # Retorna o resultado da query (uma lista de tuplas com os dados das atrações)
    # Se ocorrer algum erro ao tentar comunicar com a base de dados, mostra mensagem e retorna lista vazia
    except mysql.connector.Error as err:
        print(f"Erro ao ler atrações: {err}")
        return []
    # Fecha o cursor e a conexão com a base de dados, garantindo que os recursos são libertados
    finally:
        cursor.close()
        conn.close()

# Função para apagar (remover) uma atração da base de dados com base no seu ID
def apagar_atracao(id_atracao):
    try:
        # Estabelece ligação à base de dados usando as configurações definidas no dicionário config
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        # Executa o comando SQL para apagar a atração com o ID especificado
        cursor.execute("DELETE FROM atracoes WHERE id = %s", (id_atracao,))
        conn.commit()       # Confirma (commita) a alteração na base de dados
        print(f"Atração com id {id_atracao} apagada.")      # Informa no terminal que a atração foi apagada com sucesso
    # Captura e imprime qualquer erro que possa ocorrer durante a operação
    except mysql.connector.Error as err:
        print(f"Erro ao apagar atração: {err}")
    # Garante que o cursor e a conexão são fechados corretamente, mesmo que ocorra erro
    finally:
        cursor.close()
        conn.close()

# Função que insere um conjunto de atrações de exemplo na base de dados
def inserir_atracoes_exemplo():
    # Lista de tuplas, cada uma contendo dados de uma atração:
    # (nome, morada, cidade, tipo)
    atracoes = [
        ("Torre de Belém", "Avenida Brasília, 1400-038 Lisboa, Portugal", "Lisboa", "Cultural"),
        ("Estádio do Dragão", "Via Futebol Clube do Porto, 4350-415 Porto, Portugal", "Porto", "Desportivo"),
        ("Mercado do Bolhão", "Rua Formosa 214, 4000-214 Porto, Portugal", "Porto", "Gastronómico"),
        ("Praia da Marinha", "Praia da Marinha, 8400-450 Lagoa, Portugal", "Algarve", "Outro"),
        ("Mosteiro dos Jerónimos", "Praça do Império 1400-206 Lisboa, Portugal", "Lisboa", "Cultural"),
        ("Pavilhão Multiusos de Guimarães", "Avenida Conde Margaride 239, 4810-161 Guimarães, Portugal", "Guimarães", "Desportivo"),
        ("Mercado Municipal de Faro", "Largo da Feira Nova, 8000-133 Faro, Portugal", "Faro", "Gastronómico"),
        ("Castelo de São Jorge", "Rua de Santa Cruz do Castelo, 1100-129 Lisboa, Portugal", "Lisboa", "Cultural"),
        ("Parque Natural da Serra da Estrela", "Serra da Estrela, 6230-618 Seia, Portugal", "Guarda", "Outro"),
        ("Festival do Marisco", "Avenida do Mar, 8700-329 Olhão, Portugal", "Olhão", "Gastronómico")
    ]
    # Para cada atração na lista, chama a função 'inserir_atracao'
    # A sintaxe '*atracao' desempacota a tupla em argumentos separados
    for atracao in atracoes:
        inserir_atracao(*atracao)       # equivalente a inserir_atracao(nome, morada, cidade, tipo)

# Este bloco só é executado se este ficheiro for executado diretamente,
# e não quando for importado como módulo noutra parte do programa
if __name__ == "__main__":
    # Chama a função para criar a base de dados e as tabelas (caso ainda não existam)
    criar_base_e_tabelas()
    # Insere atrações de exemplo na base de dados (para povoar a tabela 'atracoes')
    inserir_atracoes_exemplo()
    # Imprime todas as atrações existentes na tabela 'atracoes'
    print("Atrações:", ler_todas_atracoes())


# --- API do Google Maps ---
# Inicializa a API do Google Maps lendo a chave do ficheiro
with open("APIkey.txt", "r") as f:
    APIKey = f.read()                       # Lê a chave da API armazenada no ficheiro
Maps = googlemaps.Client(key=APIKey)        # Cria o cliente para usar a API do Google Maps


# --- Interface Gráfica ---
# Entry com autocomplete mostrando sugestões
class AutocompleteEntry(tk.Entry):
    # Inicializa o Entry com lista de sugestões (nova classe criada)
    def __init__(self, suggestion_list, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        # Guarda a lista de sugestões ordenada alfabeticamente (ignora maiúsculas/minúsculas)
        self.suggestion_list = sorted(set(suggestion_list), key=str.lower)
        # Variável associada ao texto da Entry (campo de texto)
        self.var = self["textvariable"] = tk.StringVar()
        # Detecta qualquer alteração no texto para atualizar a lista de sugestões
        self.var.trace("w", self.changed)

        # Liga eventos do teclado e foco
        self.bind("<Down>", self.move_down)                # seta para baixo para navegar sugestões
        self.bind("<Return>", self.select)                 # Enter para selecionar sugestão
        self.bind("<FocusIn>", self.mostrar_todas_opcoes)  # ao focar no campo, mostra todas sugestões

        self.listbox = None             # Lista para mostrar as sugestões (Listbox)
        self.listbox_open = False       # Estado se a lista está aberta ou fechada

    def changed(self, *args):
        # Função chamada quando o texto na Entry muda
        texto = self.var.get()      # texto atual
        if texto == '':
            self.close_listbox()            # se texto vazio, fecha lista
        else:
            words = self.matches()          # procura sugestões que contenham o texto
            if words:
                self.mostrar_lista(words)   # mostra as sugestões encontradas
            else:
                self.close_listbox()        # fecha lista se não há sugestões

    def matches(self):
        # Retorna todas as sugestões que contenham o texto atual (case insensitive)
        pattern = self.var.get().lower()
        return [w for w in self.suggestion_list if pattern in w.lower()]

    def mostrar_todas_opcoes(self, event=None):
        # Mostra todas as sugestões independentemente do texto escrito
        self.mostrar_lista(self.suggestion_list)

    def mostrar_lista(self, opcoes):
        # Mostra a lista de sugestões no ecrã
        if self.listbox:
            self.listbox.destroy()      # remove a lista antiga se existir

        if not opcoes:
            return      # se não há opções, não mostra nada

        height = min(len(opcoes), 6)        # altura máxima da lista é 6 linhas
        self.listbox = tk.Listbox(self.master, height=height)
        # Liga eventos de clique e Enter para selecionar
        self.listbox.bind("<Double-Button-1>", self.select)
        self.listbox.bind("<Return>", self.select)

        # Insere cada opção na Listbox
        for opcao in opcoes:
            self.listbox.insert(tk.END, opcao)

        # Posiciona a Listbox logo abaixo da Entry, com mesma largura
        self.listbox.place(in_=self, relx=0, rely=1, relwidth=1)
        self.listbox_open = True        # marca lista como aberta

    def select(self, event=None):
        # Função para quando o utilizador seleciona uma sugestão
        if self.listbox_open and self.listbox.curselection():
            # Pega o texto da sugestão selecionada
            self.var.set(self.listbox.get(tk.ACTIVE))
            self.close_listbox()        # fecha a lista
            self.icursor(tk.END)        # move o cursor para o fim do texto

    def move_up(self, event):
        # Mover seleção para cima na lista de sugestões
        if self.listbox_open:
            if self.listbox.curselection():
                index = self.listbox.curselection()[0]
                if index > 0:
                    self.listbox.selection_clear(index)
                    index -= 1
                    self.listbox.selection_set(index)
                    self.listbox.activate(index)
            return "break"      # para evitar comportamento padrão da tecla

    def move_down(self, event):
        # Mover seleção para baixo (ou abrir a lista)
        if self.listbox_open and self.listbox.size() > 0:
            self.listbox.focus_set()       # foca a lista para navegar com o teclado
            self.listbox.select_set(0)     # seleciona a primeira opção
            self.listbox.activate(0)       # ativa a primeira opção
            return "break"                 # evita comportamento padrão

    def open_listbox(self):
        # Abre a lista de sugestões (se não estiver já aberta)
        if not self.listbox_open:
            self.listbox = tk.Listbox(master=self.master)
            self.listbox.bind("<Double-Button-1>", self.select)
            self.listbox.place(in_=self, relx=0, rely=1, relwidth=1)
            self.listbox_open = True

    def close_listbox(self):
        # Fecha a lista de sugestões (se estiver aberta)
        if self.listbox_open:
            self.listbox.destroy()
            self.listbox_open = False

# Função para obter os nomes das atrações da base de dados (aparece lista atrações enquando pessoa escreve locais)
def obter_localizacoes_banco():
    # Conectar à base de dados
    conn = mysql.connector.connect(
        user=config['user'],
        password=config['password'],
        host=config['host'],
        database=config['database']
    )
    cursor = conn.cursor()                          # Criar cursor para executar comandos SQL
    cursor.execute("SELECT nome FROM atracoes")     # Selecionar todos os nomes da tabela atracoes
    resultados = cursor.fetchall()                  # Buscar todos os resultados da consulta
    cursor.close()      # Fechar cursor
    conn.close()        # Fechar conexão com a base de dados
    # Extrair os nomes da tupla retornada e remover duplicados com set
    nomes_unicos = sorted(set([nome[0] for nome in resultados]))
    return nomes_unicos     # Retornar lista ordenada de nomes únicos

# Função para limpar todos os campos do formulário, preparando-os para nova entrada
def limpar_campos():
    entrada_local.delete(0, tk.END)    # Apaga texto do campo de local
    entrada_cidade.delete(0, tk.END)   # Apaga texto do campo de cidade
    var_tipo.set(tipos[0])                  # Reseta o menu de seleção do tipo para o valor padrão
    entrada_data.delete(0, tk.END)     # Apaga texto do campo de data
    entrada_hora.delete(0, tk.END)     # Apaga texto do campo de hora
    entrada_notas.delete(0, tk.END)    # Apaga texto do campo de notas

# Lista que vai armazenar os dados dos itinerários, incluindo informações úteis para ordenar e mostrar
itinerarios_dados = []
# Variável para armazenar o índice do itinerário selecionado
itinerario_selecionado_index = None

# Função para adicionar ou atualizar um itinerário baseado nos dados do formulário
def adicionar_itinerario():
    global itinerario_selecionado_index     # Garantir acesso à variável global que controla a seleção
    # Ler valores dos campos do formulário, removendo espaços em branco nas extremidades
    local = entrada_local.get().strip()
    cidade = entrada_cidade.get().strip()
    tipo = var_tipo.get()
    data = entrada_data.get().strip()
    hora = entrada_hora.get().strip()
    notas = entrada_notas.get().strip()

    # Verificar se os campos obrigatórios estão preenchidos
    if not (local and cidade and tipo and data and hora):
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos obrigatórios.")
        return
    # Validar formato da data (DD/MM/YYYY)
    if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$", data):
        messagebox.showerror("Data inválida", "A data deve estar no formato DD/MM/YYYY.")
        return
    # Validar formato da hora (HH:MM no formato 24h)
    if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", hora):
        messagebox.showerror("Hora inválida", "A hora deve estar no formato 24:00.")
        return
    # Converter data e hora em objeto datetime para manipulação e ordenação
    try:
        data_hora_obj = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
    except ValueError:
        messagebox.showerror("Erro", "Data e hora inválidas.")
        return
    # Definir origem e destino para cálculo de rota via API Google Maps
    origem = local
    destino = cidade
    # Tentar obter direções, distância e duração usando API
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
    # Construir resumo textual do itinerário com os dados e rota
    resumo = (
        f"📍 De {local} até {cidade}\n"
        f"     Tipo de Atividade - Viagem {tipo}\n"
        f"     Data - {data}\n"
        f"     Hora - {hora}\n"
        f"     {rota_info}"
    )
    if notas:
        resumo += f"\n     Notas - {notas}"
    # Se um itinerário está selecionado, atualiza o existente; senão, adiciona novo
    if itinerario_selecionado_index is not None:
        itinerarios_dados[itinerario_selecionado_index] = (data_hora_obj, resumo)
        messagebox.showinfo("Atualização", "Itinerário atualizado com sucesso!")
    else:
        itinerarios_dados.append((data_hora_obj, resumo))
    # Resetar seleção e ordenar lista de itinerários pela data/hora
    itinerario_selecionado_index = None
    itinerarios_dados.sort()
    # Atualizar interface para mostrar itinerários e limpar formulário
    atualizar_texto_itinerarios()
    limpar_campos()

# Atualiza o widget de texto com os itinerários ordenados (com função recursiva)
def atualizar_texto_itinerarios():
    texto_itinerarios.config(state=tk.NORMAL)               # Permite editar o widget de texto antes de fazer alterações
    texto_itinerarios.delete("1.0", tk.END)          # Limpa o conteúdo atual do widget de texto

    # Função interna recursiva que insere itinerários um a um
    def inserir_itinerarios(index=0):
        # Caso base: se o índice ultrapassar o tamanho da lista, termina a recursão
        if index >= len(itinerarios_dados):
            return
        _, item = itinerarios_dados[index]                  # Obtém o resumo do itinerário atual (ignorando a data/hora)
        texto_itinerarios.insert(tk.END, item + "\n\n")     # Insere o texto do itinerário no widget Text
        inserir_itinerarios(index + 1)                      # Chamada recursiva para inserir o próximo itinerário
    inserir_itinerarios()                                   # Chamada inicial da função recursiva com o índice 0 (1º item da lista)
    texto_itinerarios.config(state=tk.DISABLED)             # Torna o widget de texto somente leitura novamente/bloqueia edição

# Função que detecta o clique num itinerário listado e carrega os seus dados no formulário para edição
def clicar_registo(event):
    global itinerario_selecionado_index

    # Obtém a posição do cursor no widget de texto com base nas coordenadas do clique
    index = texto_itinerarios.index(f"@{event.x},{event.y}")
    linha_num = int(index.split(".")[0])  # Extrai o número da linha clicada

    # Obtém todo o texto do widget, dividido em blocos separados por linhas em branco
    linhas = texto_itinerarios.get("1.0", tk.END).strip().split("\n\n")
    texto_completo = texto_itinerarios.get("1.0", tk.END)

    # Obtém o índice do caractere na linha clicada (não usado diretamente, mas calculado)
    char_index = int(texto_itinerarios.index(index).split(".")[1])
    # Aqui tenta-se encontrar o índice global da linha dentro do texto completo (parece que não está a ser usado)
    char_global_index = texto_completo.split("\n").index(
        texto_itinerarios.get(f"{linha_num}.0", f"{linha_num}.end").strip())

    # Percorre todos os itinerários para encontrar qual corresponde ao bloco clicado
    for i, (_, resumo) in enumerate(itinerarios_dados):
        # Compara se o início do resumo coincide com o texto da linha clicada (mais 5 linhas à frente para cobrir o bloco)
        if resumo.startswith(texto_itinerarios.get(f"{linha_num}.0", f"{linha_num + 5}.end").strip().split("\n")[0]):
            itinerario_selecionado_index = i        # Define o índice do itinerário selecionado globalmente
            preencher_formulario(resumo)            # Preenche o formulário com os dados do itinerário selecionado
            break

# Preenche os campos do formulário com os dados extraídos do texto do itinerário selecionado
def preencher_formulario(texto):
    # Extrai as informações do itinerário
    match_local = re.search(r"De (.*?) até", texto)
    match_cidade = re.search(r"até (.*?)\n", texto)
    match_tipo = re.search(r"Viagem (.*?)\n", texto)
    match_data = re.search(r"Data - (.*?)\n", texto)
    match_hora = re.search(r"Hora - (.*?)\n", texto)
    match_notas = re.search(r"Notas - (.*)", texto)

    # Se encontrou x insere no campo correspondente
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

# Apaga todos os itinerários após confirmação do utilizador
def apagar_registos():
    global itinerarios_dados, itinerario_selecionado_index      # Usa as variáveis globais do programa
    confirmar = messagebox.askyesno("Apagar Registos",
                                    "Tem a certeza que deseja apagar todos os itinerários?")  # Pergunta ao utilizador
    if confirmar:
        itinerarios_dados.clear()               # Limpa a lista de itinerários
        itinerario_selecionado_index = None     # Reseta o índice de seleção
        atualizar_texto_itinerarios()           # Atualiza a área de texto para refletir as alterações

# Função para exportar a lista de itinerários para um ficheiro .txt
def exportar_itinerarios():
    # Verifica se há itinerários para exportar
    if not itinerarios_dados:
        messagebox.showinfo("Exportar", "Nenhum itinerário para exportar.")
        return
    # Abre diálogo para escolher o local e nome do ficheiro a salvar
    caminho = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if caminho:
        try:
            # Abre o ficheiro em modo escrita com codificação UTF-8
            with open(caminho, "w", encoding="utf-8") as f:
                # Escreve cada resumo de itinerário no ficheiro, separado por linhas em branco
                for _, item in itinerarios_dados:
                    f.write(item + "\n\n")
            messagebox.showinfo("Exportar", f"Itinerários exportados com sucesso para {caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

# Função para importar itinerários a partir de um ficheiro .txt
def importar_itinerarios():
    # Abre diálogo para escolher o ficheiro a importar
    caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if caminho:
        try:
            # Abre o ficheiro e lê todo o conteúdo
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()         # Remove espaços em branco nas extremidades
                blocos = conteudo.split("\n\n")     # Divide o conteúdo em blocos separados por linhas em branco

            # Limpa a lista atual de itinerários antes de importar novos
            itinerarios_dados.clear()

            # Processa cada bloco, tentando extrair data e hora com regex
            for bloco in blocos:
                match = re.search(r"Data\s*-\s*(\d{2}/\d{2}/\d{4})\n\s*Hora\s*-\s*(\d{2}:\d{2})", bloco)
                if match:
                    data_str, hora_str = match.groups()
                    try:
                        # Converte as strings de data e hora em objeto datetime
                        data_hora_obj = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M")
                        # Adiciona o itinerário à lista com a data/hora e o texto completo
                        itinerarios_dados.append((data_hora_obj, bloco.strip()))
                    except ValueError:
                        # Se a data/hora for inválida, ignora este bloco
                        continue

            # Ordena a lista de itinerários pela data/hora
            itinerarios_dados.sort()

            # Atualiza a área de texto com os itinerários importados
            texto_itinerarios.delete("1.0", tk.END)
            for _, item in itinerarios_dados:
                texto_itinerarios.insert(tk.END, item + "\n\n")

            messagebox.showinfo("Importar", "Itinerários importados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar: {e}")

    # Atualiza o texto para garantir sincronização da interface
    atualizar_texto_itinerarios()

# Abre uma nova janela para adicionar uma atração turística, com campos para nome, morada, cidade e tipo
def abrir_janela_adicionar_atracao():
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Adicionar Atração")
    nova_janela.geometry("400x200")
    nova_janela.configure(bg="#f0f4f7")

    # Frame para organizar widgets na janela
    frame = tk.Frame(nova_janela, bg="#f0f4f7", padx=20, pady=20)
    frame.pack(expand=True, fill="both")
    # Campo Nome
    tk.Label(frame, text="Nome:", bg="#f0f4f7").grid(row=0, column=0, sticky="w")
    entry_nome = tk.Entry(frame, width=50)
    entry_nome.grid(row=0, column=1, pady=5)
    # Campo Morada
    tk.Label(frame, text="Morada:", bg="#f0f4f7").grid(row=1, column=0, sticky="w")
    entry_morada = tk.Entry(frame, width=50)
    entry_morada.grid(row=1, column=1, pady=5)
    # Campo Cidade
    tk.Label(frame, text="Cidade:", bg="#f0f4f7").grid(row=2, column=0, sticky="w")
    entry_cidade = tk.Entry(frame, width=50)
    entry_cidade.grid(row=2, column=1, pady=5)
    # Campo Tipo
    tipos = ["Cultural", "Desportiva", "Gastronómica", "Outro"]
    var_tipo = tk.StringVar(value=tipos[0])
    tk.Label(frame, text="Tipo:", bg="#f0f4f7").grid(row=3, column=0, sticky="w")
    dropdown_tipo = tk.OptionMenu(frame, var_tipo, *tipos)
    dropdown_tipo.config(width=44)
    dropdown_tipo.grid(row=3, column=1, pady=5)

    # Função interna para guardar a atração na base de dados
    def guardar_atracao():
        conn = mysql.connector.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            database=config['database']
        )
        nome = entry_nome.get()
        morada = entry_morada.get()
        cidade = entry_cidade.get()
        tipo = var_tipo.get()

        # Verifica se todos os campos estão preenchidos
        if nome and morada and cidade and tipo:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO atracoes (nome, morada, cidade, tipo) VALUES (%s, %s, %s, %s)",
                               (nome, morada, cidade, tipo))
                conn.commit()
                messagebox.showinfo("Sucesso", "Atração adicionada com sucesso!")
                nova_janela.destroy()       # Fecha a janela após adicionar
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao adicionar atração: {err}")
        else:
            messagebox.showwarning("Campos vazios", "Por favor, preencha todos os campos.")

    # Botão para guardar os dados da atração
    btn_guardar = tk.Button(frame, text="Guardar Atração", command=guardar_atracao, bg="#2a4d69", fg="white")
    btn_guardar.grid(row=4, column=0, columnspan=2, pady=20)

# Abre uma janela com a lista de atrações da base de dados, permitindo apagar uma atração selecionada
def abrir_janela_apagar_atracao():
    # Conexão com a base de dados MySQL
    conn = mysql.connector.connect(
        user=config['user'],
        password=config['password'],
        host=config['host'],
        database=config['database']
    )
    cursor = conn.cursor()

    # Cria uma nova janela para mostrar a tabela de atrações
    janela_tabela = tk.Toplevel(janela)
    janela_tabela.title("Lista de Atrações da Base de Dados")
    janela_tabela.geometry("900x400")

    # Configura a tabela (Treeview) com colunas para ID, Nome, Morada, Cidade e Tipo
    tree = ttk.Treeview(janela_tabela, columns=("ID", "Nome", "Morada", "Cidade", "Tipo"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Morada", text="Morada")
    tree.heading("Cidade", text="Cidade")
    tree.heading("Tipo", text="Tipo")

    # Define larguras para as colunas
    tree.column("ID", width=50)
    tree.column("Nome", width=200)
    tree.column("Morada", width=400)
    tree.column("Cidade", width=100)
    tree.column("Tipo", width=100)
    tree.pack(fill="both", expand=True)

    # Função para carregar os dados da base de dados na tabela
    def carregar_tabela():
        # Limpa a tabela antes de inserir dados novos
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM atracoes")
        for atracao in cursor.fetchall():
            tree.insert("", "end", values=atracao)

    carregar_tabela()

    # Função que apaga a atração selecionada pelo seu ID
    def apagar_atracao(id_atracao):
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que quer apagar esta atração?")
        if resposta:
            try:
                cursor.execute("DELETE FROM atracoes WHERE id = %s", (id_atracao,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Atração apagada com sucesso.")
                carregar_tabela()  # Atualiza a tabela após apagar
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao apagar: {e}")
        else:
            messagebox.showinfo("Cancelado", "Ação cancelada.")

    # Função chamada ao clicar no botão apagar, que verifica se algo foi selecionado
    def botao_apagar_click():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione uma atração para apagar.")
            return
        valores = tree.item(selecionado)["values"]
        if not valores:
            messagebox.showerror("Erro", "Erro ao obter os dados da seleção.")
            return
        id_atracao = valores[0]
        apagar_atracao(id_atracao)

    # Botão para apagar a atração selecionada na tabela
    btn_apagar = tk.Button(janela_tabela, text="Apagar Atração Selecionada", command=botao_apagar_click)
    btn_apagar.pack(pady=10)

    # Fecha a conexão com a base de dados e destrói a janela ao fechar a janela
    def ao_fechar():
        cursor.close()
        conn.close()
        janela_tabela.destroy()

    janela_tabela.protocol("WM_DELETE_WINDOW", ao_fechar)

# Função auxiliar para criar um campo do formulário com um rótulo e um widget (ex: Entry, Text)
def criar_campo_formulario(label_texto, widget):
    # Cria um label com o texto fornecido, com estilo e cor de fundo definidos
    tk.Label(frame_formulario, text=label_texto, bg="#f0f4f7", font=("Arial", 13, "bold")).pack(anchor="w", pady=(5, 0))
    # Empacota (exibe) o widget fornecido abaixo do label, ocupando toda a largura disponível com margem horizontal
    widget.pack(fill=tk.X, padx=5)


# --- Configuração da janela principal ---
janela = tk.Tk()
janela.title("Formulário de Planeamento de Viagens")
janela.geometry("800x600")
janela.configure(bg="#f0f4f7")

# --- Container principal que divide a janela em duas áreas ---
container_principal = tk.Frame(janela, bg="#f0f4f7")
container_principal.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

# Frame do formulário (lado esquerdo)
frame_formulario = tk.Frame(container_principal, bg="#f0f4f7")
frame_formulario.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

# Frame dos registos (lado direito)
frame_registos = tk.Frame(container_principal, bg="#f0f4f7")
frame_registos.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

# --- Cabeçalhos ---
tk.Label(frame_formulario, text="📌 Planeamento de Itinerário", font=("Arial", 20, "bold"),
         bg="#f0f4f7", fg="#2a4d69").pack(pady=10)
tk.Label(frame_registos, text="🧾 Itinerários Registados", font=("Arial", 20, "bold"),
         bg="#f0f4f7", fg="#2a4d69").pack(pady=10)

# --- Campos do formulário com autocomplete ---
locais = obter_localizacoes_banco()  # lista de locais para autocomplete

entrada_local = AutocompleteEntry(locais, frame_formulario, font=("Arial", 11))
criar_campo_formulario("Localização Atual:", entrada_local)

entrada_cidade = AutocompleteEntry(locais, frame_formulario, font=("Arial", 11))
criar_campo_formulario("Para Onde Deseja Ir:", entrada_cidade)

# --- Dropdown para tipo ---
tipos = ["Cultural", "Desportiva", "Gastronómica", "Outro"]
var_tipo = tk.StringVar(value=tipos[0])
dropdown_tipo = tk.OptionMenu(frame_formulario, var_tipo, *tipos)
dropdown_tipo.config(font=("Arial", 11), width=20)
criar_campo_formulario("Tipo de Atividade:", dropdown_tipo)

# --- Outros campos do formulário ---
entrada_data = tk.Entry(frame_formulario, font=("Arial", 11))
criar_campo_formulario("Data (DD/MM/YYYY):", entrada_data)

entrada_hora = tk.Entry(frame_formulario, font=("Arial", 11))
criar_campo_formulario("Hora (HH:MM):", entrada_hora)

entrada_notas = tk.Entry(frame_formulario, font=("Arial", 11))
criar_campo_formulario("Notas:", entrada_notas)

# --- Botão para adicionar itinerário ---
tk.Button(frame_formulario, text="Adicionar Itinerário", command=adicionar_itinerario,
          bg="#2a4d69", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

# --- Botões para gerenciar atrações ---
frame_botoes_atracoes = tk.Frame(frame_formulario, bg="#f0f4f7")
frame_botoes_atracoes.pack(pady=10)

btn_adicionar_atracao = tk.Button(frame_botoes_atracoes, text="Adicionar Atração",
                                command=abrir_janela_adicionar_atracao,
                                bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
btn_adicionar_atracao.pack(side=tk.LEFT, padx=5)

btn_apagar_atracao = tk.Button(frame_botoes_atracoes, text="Apagar Atração",
                               command=abrir_janela_apagar_atracao,
                               bg="#c0392b", fg="white", font=("Arial", 12, "bold"))
btn_apagar_atracao.pack(side=tk.LEFT, padx=5)

# --- Área de texto para mostrar itinerários ---
frame_texto = tk.Frame(frame_registos, bg="#f0f4f7")
frame_texto.pack(fill=tk.BOTH, expand=True)

texto_itinerarios = tk.Text(frame_texto, bg="white", font=("Arial", 10), wrap=tk.WORD)
texto_itinerarios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
texto_itinerarios.config(state=tk.DISABLED)

texto_itinerarios.bind("<Button-1>", clicar_registo)

# Scrollbar para área de texto
scrollbar = tk.Scrollbar(frame_texto, command=texto_itinerarios.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

texto_itinerarios.config(yscrollcommand=scrollbar.set)

# --- Botão para apagar todos os itinerários ---
tk.Button(frame_registos, text="Apagar Registos", command=apagar_registos,
          bg="#c0392b", fg="white", font=("Arial", 12, "bold"), width=18).pack(pady=10)

# --- Botões para exportar/importar itinerários ---
frame_botoes = tk.Frame(frame_registos, bg="#f0f4f7")
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="Exportar", command=exportar_itinerarios,
          bg="#2196F3", fg="white", font=("Arial", 12, "bold"), width=12).pack(side=tk.LEFT, padx=10)

tk.Button(frame_botoes, text="Importar", command=importar_itinerarios,
          bg="#2196F3", fg="white", font=("Arial", 12, "bold"), width=12).pack(side=tk.LEFT, padx=10)

# --- Rodapé ---
tk.Label(janela, text="Projeto Final Programação Avançada - Grupo 4 ✈️", font=("Arial", 10),
         bg="#f0f4f7", fg="#888").pack(pady=5)

# Inicia o loop principal da interface
janela.mainloop()