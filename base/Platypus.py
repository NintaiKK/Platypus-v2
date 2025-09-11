import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import os
from tkinter import PhotoImage
from fpdf import FPDF

class OrdemServicoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ordem de Serviço - Mecânica")
        self.root.geometry("1000x850")
        
        try:
            root.iconbitmap("22.ico")
        except:
            pass
        
        # Inicializa o banco de dados
        self.inicializar_banco_dados()
        
        # Carrega configurações da empresa
        self.carregar_configuracoes_empresa()
        
        # Variáveis para os dados do cliente
        self.cliente_id = None
        self.veiculo_id = None
        self.cliente_nome = tk.StringVar()
        self.cliente_endereco = tk.StringVar()
        self.cliente_cidade = tk.StringVar()
        self.cliente_cpf_cnpj = tk.StringVar()
        self.cliente_telefone = tk.StringVar()
        self.cliente_email = tk.StringVar()
        self.cliente_veiculo = tk.StringVar()
        self.cliente_placa = tk.StringVar()
        self.cliente_km = tk.StringVar()
        
        # Variáveis para a ordem de serviço
        self.os_id = None
        self.numero_os = tk.StringVar(value=self.gerar_numero_os())
        self.data_emissao = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.servico_solicitado = tk.StringVar()
        self.observacoes = tk.StringVar()
        self.status_os = tk.StringVar(value="Aberta")
        self.servico_qtd = tk.StringVar()
        self.servico_valor = tk.StringVar()
        self.servico_total = tk.StringVar(value="R$ 0,00")
        
        # Lista de itens da OS
        self.itens_os = []
        
        # Configura o estilo
        self.configurar_estilos()
        
        # Cria a interface
        self.criar_widgets()
        
        # Carrega a última OS se existir
        self.carregar_ultima_os()

    def configurar_estilos(self):
        """Configura estilos para a interface"""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TEntry', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Total.TLabel', font=('Arial', 10, 'bold'))
        style.configure('StatusAberta.TLabel', foreground='blue', font=('Arial', 10, 'bold'))
        style.configure('StatusFechada.TLabel', foreground='green', font=('Arial', 10, 'bold'))
    
    def inicializar_banco_dados(self):
        """Inicializa o banco de dados SQLite"""
        self.conn = sqlite3.connect('mecanica.db')
        self.c = self.conn.cursor()
        
        # Tabela de clientes
        self.c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nome TEXT NOT NULL,
                          endereco TEXT,
                          cidade TEXT,
                          cpf_cnpj TEXT,
                          telefone TEXT,
                          email TEXT,
                          data_cadastro TEXT)''')
        
        # Tabela de veículos
        self.c.execute('''CREATE TABLE IF NOT EXISTS veiculos (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          cliente_id INTEGER,
                          modelo TEXT,
                          placa TEXT UNIQUE,
                          km TEXT,
                          FOREIGN KEY(cliente_id) REFERENCES clientes(id))''')
        
        # Tabela de ordens de serviço
        self.c.execute('''CREATE TABLE IF NOT EXISTS ordens_servico (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          numero TEXT UNIQUE,
                          cliente_id INTEGER,
                          veiculo_id INTEGER,
                          data_emissao TEXT,
                          servico_solicitado TEXT,
                          observacoes TEXT,
                          valor_total REAL,
                          status TEXT,
                          data_fechamento TEXT,
                          FOREIGN KEY(cliente_id) REFERENCES clientes(id),
                          FOREIGN KEY(veiculo_id) REFERENCES veiculos(id))''')
        
        # Tabela de itens da OS
        self.c.execute('''CREATE TABLE IF NOT EXISTS itens_os (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          os_id INTEGER,
                          descricao TEXT,
                          quantidade REAL,
                          valor_unitario REAL,
                          valor_total REAL,
                          FOREIGN KEY(os_id) REFERENCES ordens_servico(id))''')
        
        # Tabela de configurações da empresa
        self.c.execute('''CREATE TABLE IF NOT EXISTS empresa_config (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nome TEXT,
                          endereco TEXT,
                          cidade TEXT,
                          cnpj TEXT,
                          ie TEXT,
                          telefone TEXT,
                          cabecalho_img TEXT)''')
        
        self.conn.commit()
    
    def carregar_configuracoes_empresa(self):
        """Carrega as configurações da empresa do banco de dados"""
        self.c.execute("SELECT * FROM empresa_config LIMIT 1")
        config = self.c.fetchone()
        
        if config:
            self.dados_empresa = {
                "nome": config[1],
                "endereco": config[2],
                "cidade": config[3],
                "cnpj": config[4],
                "ie": config[5],
                "telefone": config[6],
                "cabecalho_img": config[7]
            }
        else:
            # Valores padrão
            self.dados_empresa = {
                "nome": "AutoMecânica SpeedMaster Ltda",
                "endereco": "Av. das Oficinas, 123 - Centro",
                "cidade": "São Paulo - SP",
                "cnpj": "12.345.678/0001-99",
                "ie": "123.456.789.111",
                "telefone": "(11) 5555-1234",
                "cabecalho_img": ""
            }
            # Insere os valores padrão no banco de dados
            self.salvar_configuracoes_empresa()
        
        # Carrega a imagem do cabeçalho se existir
        self.cabecalho_img = None
        if self.dados_empresa.get("cabecalho_img") and os.path.exists(self.dados_empresa["cabecalho_img"]):
            try:
                self.cabecalho_img = PhotoImage(file=self.dados_empresa["cabecalho_img"])
            except:
                print(f"Erro ao carregar imagem do cabeçalho: {self.dados_empresa['cabecalho_img']}")
    
    def salvar_configuracoes_empresa(self):
        """Salva as configurações da empresa no banco de dados"""
        # Primeiro verifica se já existe configuração
        self.c.execute("SELECT COUNT(*) FROM empresa_config")
        if self.c.fetchone()[0] > 0:
            # Atualiza
            self.c.execute('''UPDATE empresa_config SET 
                            nome=?, endereco=?, cidade=?, cnpj=?, ie=?, telefone=?, cabecalho_img=?''',
                          (self.dados_empresa["nome"], self.dados_empresa["endereco"],
                           self.dados_empresa["cidade"], self.dados_empresa["cnpj"],
                           self.dados_empresa["ie"], self.dados_empresa["telefone"],
                           self.dados_empresa["cabecalho_img"]))
        else:
            # Insere
            self.c.execute('''INSERT INTO empresa_config 
                            (nome, endereco, cidade, cnpj, ie, telefone, cabecalho_img)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (self.dados_empresa["nome"], self.dados_empresa["endereco"],
                           self.dados_empresa["cidade"], self.dados_empresa["cnpj"],
                           self.dados_empresa["ie"], self.dados_empresa["telefone"],
                           self.dados_empresa["cabecalho_img"]))
        
        self.conn.commit()
    
    def gerar_numero_os(self):
        """Gera um número fictício de OS baseado na data/hora"""
        return datetime.now().strftime("%Y%m%d%H%M")
    
    def criar_widgets(self):
        # Frame principal que contém o canvas e a scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas rolável
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Frame interno onde os widgets serão adicionados
        second_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=second_frame, anchor="nw")

        # Barra de menu
        menubar = tk.Menu(self.root)
        
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menu_arquivo.add_command(label="Nova OS", command=self.nova_os)
        menu_arquivo.add_command(label="Salvar OS", command=self.salvar_os)
        menu_arquivo.add_command(label="Carregar OS", command=self.carregar_os_dialog)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        
        menu_empresa = tk.Menu(menubar, tearoff=0)
        menu_empresa.add_command(label="Configurar Empresa", command=self.abrir_config_empresa)
        menubar.add_cascade(label="Empresa", menu=menu_empresa)
        
        menu_clientes = tk.Menu(menubar, tearoff=0)
        menu_clientes.add_command(label="Gerenciar Clientes", command=self.abrir_gerenciador_clientes)
        menubar.add_cascade(label="Clientes", menu=menu_clientes)

        menu_os = tk.Menu(menubar, tearoff=0)
        menu_os.add_command(label="Listar Todas OS", command=self.listar_ordens_servico)
        menubar.add_cascade(label="Ordens", menu=menu_os)

        self.root.config(menu=menubar)

        # Cabeçalho da empresa
        if self.cabecalho_img:
            frame_cabecalho = ttk.Frame(second_frame)
            frame_cabecalho.pack(fill=tk.X, pady=5)
            lbl_cabecalho = ttk.Label(frame_cabecalho, image=self.cabecalho_img)
            lbl_cabecalho.pack()
        else:
            frame_empresa = ttk.LabelFrame(second_frame, text="Dados da Empresa", padding="10")
            frame_empresa.pack(fill=tk.X, pady=5)
            ttk.Label(frame_empresa, text=self.dados_empresa["nome"], style='Title.TLabel').pack(anchor=tk.W)
            ttk.Label(frame_empresa, text=f"CNPJ: {self.dados_empresa['cnpj']} - IE: {self.dados_empresa['ie']}").pack(anchor=tk.W)
            ttk.Label(frame_empresa, text=f"Endereço: {self.dados_empresa['endereco']}").pack(anchor=tk.W)
            ttk.Label(frame_empresa, text=f"{self.dados_empresa['cidade']} - Tel: {self.dados_empresa['telefone']}").pack(anchor=tk.W)

        # Área da OS e data
        frame_info_os = ttk.Frame(second_frame, padding="5")
        frame_info_os.pack(fill=tk.X, pady=5)
        ttk.Label(frame_info_os, text=f"Ordem de Serviço Nº: {self.numero_os.get()}", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Status com cor diferente
        status_style = 'StatusAberta.TLabel' if self.status_os.get() == "Aberta" else 'StatusFechada.TLabel'
        ttk.Label(frame_info_os, text=f"Status: {self.status_os.get()}", style=status_style).pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(frame_info_os, text=f"Data Emissão: {self.data_emissao.get()}").pack(side=tk.RIGHT)

        # Área do cliente
        frame_cliente = ttk.LabelFrame(second_frame, text="Dados do Cliente/Veículo", padding="10")
        frame_cliente.pack(fill=tk.X, pady=5)

        # Configurar grid para o frame do cliente
        frame_cliente.grid_columnconfigure(1, weight=1)
        frame_cliente.grid_columnconfigure(3, weight=1)

        # Linha 1
        ttk.Label(frame_cliente, text="Nome/Razão Social:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_nome, width=40).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(frame_cliente, text="Telefone:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_telefone, width=15).grid(row=0, column=3, sticky=tk.W, pady=2)
        
        ttk.Button(frame_cliente, text="Selecionar Cliente", command=self.selecionar_cliente).grid(row=0, column=4, padx=5, pady=2)

        # Linha 2
        ttk.Label(frame_cliente, text="Endereço:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_endereco, width=40).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(frame_cliente, text="E-mail:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_email, width=25).grid(row=1, column=3, sticky=tk.W, pady=2)

        # Linha 3
        ttk.Label(frame_cliente, text="Cidade/UF:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_cidade, width=25).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(frame_cliente, text="Veículo:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_veiculo, width=20).grid(row=2, column=3, sticky=tk.W, pady=2)

        # Linha 4
        ttk.Label(frame_cliente, text="CPF/CNPJ:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_cpf_cnpj, width=20).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(frame_cliente, text="Placa:").grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_placa, width=10).grid(row=3, column=3, sticky=tk.W, pady=2)

        # Linha 5
        ttk.Label(frame_cliente, text="KM:").grid(row=4, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame_cliente, textvariable=self.cliente_km, width=10).grid(row=4, column=3, sticky=tk.W, pady=2)
        
        ttk.Button(frame_cliente, text="Salvar Cliente", command=self.salvar_cliente).grid(row=4, column=4, padx=5, pady=2)

        # Serviço Solicitado (versão simplificada sem quantidade e valor)
        frame_servico = ttk.LabelFrame(second_frame, text="Serviço Solicitado", padding="10")
        frame_servico.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_servico, text="Descrição do Serviço:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(frame_servico, textvariable=self.servico_solicitado, width=100).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Itens da OS
        frame_itens = ttk.LabelFrame(second_frame, text="Itens da Ordem de Serviço", padding="10")
        frame_itens.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ('seq', 'descricao', 'quantidade', 'valor_unit', 'valor_total')
        self.tree_itens = ttk.Treeview(frame_itens, columns=columns, show='headings', height=8)

        # Configurar colunas
        self.tree_itens.heading('seq', text='Seq')
        self.tree_itens.heading('descricao', text='Descrição')
        self.tree_itens.heading('quantidade', text='Qtd')
        self.tree_itens.heading('valor_unit', text='Vl. Unitário')
        self.tree_itens.heading('valor_total', text='Vl. Total')

        self.tree_itens.column('seq', width=40, anchor=tk.CENTER)
        self.tree_itens.column('descricao', width=400, anchor=tk.W)
        self.tree_itens.column('quantidade', width=60, anchor=tk.CENTER)
        self.tree_itens.column('valor_unit', width=100, anchor=tk.E)
        self.tree_itens.column('valor_total', width=100, anchor=tk.E)

        self.tree_itens.pack(fill=tk.BOTH, expand=True)

        # Frame para adicionar itens
        frame_add_item = ttk.Frame(frame_itens)
        frame_add_item.pack(fill=tk.X, pady=5)

        ttk.Label(frame_add_item, text="Descrição:").pack(side=tk.LEFT, padx=2)
        self.entry_descricao = ttk.Entry(frame_add_item, width=40)
        self.entry_descricao.pack(side=tk.LEFT, padx=2)

        ttk.Label(frame_add_item, text="Qtd:").pack(side=tk.LEFT, padx=2)
        self.entry_quantidade = ttk.Entry(frame_add_item, width=5)
        self.entry_quantidade.pack(side=tk.LEFT, padx=2)

        ttk.Label(frame_add_item, text="Vl. Unit:").pack(side=tk.LEFT, padx=2)
        self.entry_valor_unit = ttk.Entry(frame_add_item, width=10)
        self.entry_valor_unit.pack(side=tk.LEFT, padx=2)

        btn_add_item = ttk.Button(frame_add_item, text="Adicionar", command=self.adicionar_item)
        btn_add_item.pack(side=tk.LEFT, padx=10)

        btn_remover_item = ttk.Button(frame_add_item, text="Remover", command=self.remover_item)
        btn_remover_item.pack(side=tk.LEFT, padx=2)

        # Totais
        frame_totais = ttk.Frame(second_frame)
        frame_totais.pack(fill=tk.X, pady=5)

        self.valor_total = tk.DoubleVar(value=0.0)
        ttk.Label(frame_totais, text="Valor Total:", style='Total.TLabel').pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_totais, textvariable=self.valor_total, style='Total.TLabel').pack(side=tk.LEFT)

        # Observações
        frame_obs = ttk.LabelFrame(second_frame, text="Observações", padding="10")
        frame_obs.pack(fill=tk.X, pady=5)
        ttk.Entry(frame_obs, textvariable=self.observacoes, width=100).pack(fill=tk.X)

        # Botões finais
        frame_botoes = ttk.Frame(second_frame)
        frame_botoes.pack(fill=tk.X, pady=10)

        ttk.Button(frame_botoes, text="Fechar OS", command=self.fechar_os).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Imprimir OS", command=self.gerar_pdf_os).pack(side=tk.RIGHT, padx=5)
        ttk.Button(frame_botoes, text="Salvar OS", command=self.salvar_os).pack(side=tk.RIGHT, padx=5)
        ttk.Button(frame_botoes, text="Limpar Tudo", command=self.limpar_tudo).pack(side=tk.RIGHT, padx=5)

    def abrir_config_empresa(self):
        """Abre janela para configurar dados da empresa"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurações da Empresa")
        config_window.geometry("600x450")
        
        # Variáveis temporárias para edição
        temp_nome = tk.StringVar(value=self.dados_empresa.get("nome", ""))
        temp_endereco = tk.StringVar(value=self.dados_empresa.get("endereco", ""))
        temp_cidade = tk.StringVar(value=self.dados_empresa.get("cidade", ""))
        temp_cnpj = tk.StringVar(value=self.dados_empresa.get("cnpj", ""))
        temp_ie = tk.StringVar(value=self.dados_empresa.get("ie", ""))
        temp_telefone = tk.StringVar(value=self.dados_empresa.get("telefone", ""))
        temp_img_path = tk.StringVar(value=self.dados_empresa.get("cabecalho_img", ""))
        
        # Frame principal
        main_frame = ttk.Frame(config_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Formulário de edição
        ttk.Label(main_frame, text="Nome da Empresa:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_nome, width=40).grid(row=0, column=1, sticky=tk.W, pady=5, columnspan=2)
        
        ttk.Label(main_frame, text="Endereço:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_endereco, width=40).grid(row=1, column=1, sticky=tk.W, pady=5, columnspan=2)
        
        ttk.Label(main_frame, text="Cidade/UF:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_cidade, width=25).grid(row=2, column=1, sticky=tk.W, pady=5, columnspan=2)
        
        ttk.Label(main_frame, text="CNPJ:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_cnpj, width=20).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Inscrição Estadual:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_ie, width=20).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Telefone:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_telefone, width=15).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Imagem do Cabeçalho:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=temp_img_path, width=30).grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Procurar...", 
                  command=lambda: self.procurar_imagem(temp_img_path)).grid(row=6, column=2, sticky=tk.W, pady=5)
        
        # Visualização da imagem (se existir)
        self.preview_img = None
        self.lbl_preview = ttk.Label(main_frame)
        self.lbl_preview.grid(row=7, column=0, columnspan=3, pady=10)
        self.atualizar_preview_imagem(temp_img_path.get())
        
        # Atualiza preview quando o caminho da imagem muda
        temp_img_path.trace_add("write", lambda *args: self.atualizar_preview_imagem(temp_img_path.get()))
        
        # Botões de ação
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Salvar", 
                  command=lambda: self.salvar_config_empresa(
                      temp_nome.get(),
                      temp_endereco.get(),
                      temp_cidade.get(),
                      temp_cnpj.get(),
                      temp_ie.get(),
                      temp_telefone.get(),
                      temp_img_path.get(),
                      config_window
                  )).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(btn_frame, text="Cancelar", command=config_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def atualizar_preview_imagem(self, img_path):
        """Atualiza a visualização da imagem do cabeçalho"""
        if img_path and os.path.exists(img_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(img_path)
                img.thumbnail((400, 150))  # Redimensiona mantendo proporção
                self.preview_img = ImageTk.PhotoImage(img)
                self.lbl_preview.config(image=self.preview_img)
            except Exception as e:
                print(f"Erro ao carregar preview da imagem: {e}")
                self.lbl_preview.config(image='', text="Pré-visualização não disponível")
        else:
            self.lbl_preview.config(image='', text="Nenhuma imagem selecionada")
    
    def procurar_imagem(self, img_path_var):
        """Abre diálogo para selecionar imagem do cabeçalho"""
        filepath = filedialog.askopenfilename(
            title="Selecione a imagem do cabeçalho",
            filetypes=(("Imagens PNG", "*.png"), ("Imagens JPEG", "*.jpg;*.jpeg"), ("Todos os arquivos", "*.*")))
        
        if filepath:
            img_path_var.set(filepath)
    
    def salvar_config_empresa(self, nome, endereco, cidade, cnpj, ie, telefone, img_path, window):
        """Salva as novas configurações da empresa"""
        if not nome:
            messagebox.showerror("Erro", "O nome da empresa é obrigatório!")
            return
        
        self.dados_empresa = {
            "nome": nome,
            "endereco": endereco,
            "cidade": cidade,
            "cnpj": cnpj,
            "ie": ie,
            "telefone": telefone,
            "cabecalho_img": img_path
        }
        
        self.salvar_configuracoes_empresa()
        
        # Recarrega a imagem do cabeçalho se foi alterada
        if img_path and os.path.exists(img_path):
            try:
                self.cabecalho_img = PhotoImage(file=img_path)
            except:
                messagebox.showerror("Erro", "Não foi possível carregar a nova imagem do cabeçalho!")
        
        window.destroy()
        messagebox.showinfo("Sucesso", "Configurações da empresa atualizadas com sucesso!")
        
        # Recria a interface para atualizar os dados exibidos
        for widget in self.root.winfo_children():
            widget.destroy()
        self.criar_widgets()
    
    def abrir_gerenciador_clientes(self):
        """Abre a janela de gerenciamento de clientes"""
        clientes_window = tk.Toplevel(self.root)
        clientes_window.title("Gerenciador de Clientes")
        clientes_window.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(clientes_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de pesquisa
        frame_pesquisa = ttk.Frame(main_frame)
        frame_pesquisa.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa_cliente = ttk.Entry(frame_pesquisa, width=30)
        self.entry_pesquisa_cliente.pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa_cliente.bind("<KeyRelease>", self.pesquisar_clientes)
        
        ttk.Button(frame_pesquisa, text="Novo Cliente", 
                  command=self.novo_cliente).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para listar clientes
        columns = ('id', 'nome', 'telefone', 'cpf_cnpj', 'cidade')
        self.tree_clientes = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Definindo cabeçalhos
        self.tree_clientes.heading('id', text='ID')
        self.tree_clientes.heading('nome', text='Nome/Razão Social')
        self.tree_clientes.heading('telefone', text='Telefone')
        self.tree_clientes.heading('cpf_cnpj', text='CPF/CNPJ')
        self.tree_clientes.heading('cidade', text='Cidade/UF')
        
        # Definindo largura das colunas
        self.tree_clientes.column('id', width=50, anchor=tk.CENTER)
        self.tree_clientes.column('nome', width=250, anchor=tk.W)
        self.tree_clientes.column('telefone', width=100, anchor=tk.W)
        self.tree_clientes.column('cpf_cnpj', width=120, anchor=tk.W)
        self.tree_clientes.column('cidade', width=150, anchor=tk.W)
        
        self.tree_clientes.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        ttk.Button(frame_botoes, text="Selecionar", 
                  command=lambda: self.selecionar_cliente_na_lista(clientes_window)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Editar", 
                  command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Excluir", 
                  command=self.excluir_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Fechar", 
                  command=clientes_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Carrega a lista de clientes
        self.carregar_lista_clientes()
    
    def carregar_lista_clientes(self, filtro=None):
        """Carrega a lista de clientes na Treeview"""
        # Limpa a treeview
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        # Consulta os clientes no banco de dados
        if filtro:
            self.c.execute('''SELECT id, nome, telefone, cpf_cnpj, cidade 
                            FROM clientes 
                            WHERE nome LIKE ? OR cpf_cnpj LIKE ? 
                            ORDER BY nome''', (f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT id, nome, telefone, cpf_cnpj, cidade 
                            FROM clientes 
                            ORDER BY nome''')
        
        clientes = self.c.fetchall()
        
        # Adiciona os clientes na treeview
        for cliente in clientes:
            self.tree_clientes.insert('', tk.END, values=cliente)
    
    def pesquisar_clientes(self, event=None):
        """Pesquisa clientes conforme texto digitado"""
        filtro = self.entry_pesquisa_cliente.get()
        self.carregar_lista_clientes(filtro)
    
    def novo_cliente(self):
        """Abre formulário para cadastrar novo cliente"""
        self.limpar_campos_cliente()
        
        # Define o foco no campo nome
        self.root.focus_set()
        self.root.focus_force()
        self.cliente_nome.focus()
    
    def editar_cliente(self):
        """Edita o cliente selecionado na lista"""
        selected_item = self.tree_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um cliente para editar!")
            return
        
        # Obtém os dados do cliente selecionado
        cliente_id = self.tree_clientes.item(selected_item)['values'][0]
        self.carregar_dados_cliente(cliente_id)
    
    def excluir_cliente(self):
        """Exclui o cliente selecionado na lista"""
        selected_item = self.tree_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um cliente para excluir!")
            return
        
        cliente_id = self.tree_clientes.item(selected_item)['values'][0]
        cliente_nome = self.tree_clientes.item(selected_item)['values'][1]
        
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o cliente {cliente_nome}?"):
            return
        
        try:
            # Primeiro verifica se existem ordens de serviço para este cliente
            self.c.execute("SELECT COUNT(*) FROM ordens_servico WHERE cliente_id=?", (cliente_id,))
            if self.c.fetchone()[0] > 0:
                messagebox.showerror("Erro", "Este cliente possui ordens de serviço vinculadas e não pode ser excluído!")
                return
            
            # Exclui os veículos do cliente primeiro
            self.c.execute("DELETE FROM veiculos WHERE cliente_id=?", (cliente_id,))
            
            # Exclui o cliente
            self.c.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
            self.conn.commit()
            
            # Atualiza a lista de clientes
            self.carregar_lista_clientes()
            
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao excluir o cliente: {e}")
    
    def selecionar_cliente_na_lista(self, window):
        """Seleciona o cliente da lista para a ordem de serviço"""
        selected_item = self.tree_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um cliente!")
            return
        
        cliente_id = self.tree_clientes.item(selected_item)['values'][0]
        self.carregar_dados_cliente(cliente_id)
        window.destroy()
    
    def carregar_dados_cliente(self, cliente_id):
        """Carrega os dados do cliente nos campos do formulário"""
        self.c.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
        cliente = self.c.fetchone()
        
        if cliente:
            self.cliente_id = cliente[0]
            self.cliente_nome.set(cliente[1])
            self.cliente_endereco.set(cliente[2])
            self.cliente_cidade.set(cliente[3])
            self.cliente_cpf_cnpj.set(cliente[4])
            self.cliente_telefone.set(cliente[5])
            self.cliente_email.set(cliente[6])
            
            # Carrega os veículos do cliente
            self.c.execute("SELECT * FROM veiculos WHERE cliente_id=?", (cliente_id,))
            veiculos = self.c.fetchall()
            
            if veiculos:
                # Por enquanto, vamos pegar apenas o primeiro veículo
                veiculo = veiculos[0]
                self.veiculo_id = veiculo[0]
                self.cliente_veiculo.set(veiculo[2])
                self.cliente_placa.set(veiculo[3])
                self.cliente_km.set(veiculo[4])
            else:
                self.veiculo_id = None
                self.cliente_veiculo.set("")
                self.cliente_placa.set("")
                self.cliente_km.set("")
    
    def selecionar_cliente(self):
        """Abre o gerenciador de clientes em modo de seleção"""
        self.abrir_gerenciador_clientes()
    
    def salvar_cliente(self):
        """Salva ou atualiza os dados do cliente"""
        if not self.cliente_nome.get():
            messagebox.showwarning("Atenção", "O nome do cliente é obrigatório!")
            return
        
        try:
            dados_cliente = (
                self.cliente_nome.get(),
                self.cliente_endereco.get(),
                self.cliente_cidade.get(),
                self.cliente_cpf_cnpj.get(),
                self.cliente_telefone.get(),
                self.cliente_email.get(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            dados_veiculo = (
                self.cliente_veiculo.get(),
                self.cliente_placa.get(),
                self.cliente_km.get()
            )
            
            if self.cliente_id:
                # Atualiza cliente existente
                self.c.execute('''UPDATE clientes SET 
                                nome=?, endereco=?, cidade=?, cpf_cnpj=?, telefone=?, email=?
                                WHERE id=?''',
                             (*dados_cliente[:-1], self.cliente_id))
                
                # Verifica se já existe um veículo para este cliente
                if self.veiculo_id:
                    # Atualiza veículo existente
                    self.c.execute('''UPDATE veiculos SET 
                                    modelo=?, placa=?, km=?
                                    WHERE id=?''',
                                 (*dados_veiculo, self.veiculo_id))
                else:
                    # Insere novo veículo
                    self.c.execute('''INSERT INTO veiculos 
                                    (cliente_id, modelo, placa, km)
                                    VALUES (?, ?, ?, ?)''',
                                 (self.cliente_id, *dados_veiculo))
                    self.veiculo_id = self.c.lastrowid
                
                messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            else:
                # Insere novo cliente
                self.c.execute('''INSERT INTO clientes 
                                (nome, endereco, cidade, cpf_cnpj, telefone, email, data_cadastro)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             dados_cliente)
                self.cliente_id = self.c.lastrowid
                
                # Insere o veículo do cliente
                if self.cliente_veiculo.get():
                    self.c.execute('''INSERT INTO veiculos 
                                    (cliente_id, modelo, placa, km)
                                    VALUES (?, ?, ?, ?)''',
                                 (self.cliente_id, *dados_veiculo))
                    self.veiculo_id = self.c.lastrowid
                
                messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            
            self.conn.commit()
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e) and "placa" in str(e):
                messagebox.showerror("Erro", "Já existe um veículo com esta placa cadastrada!")
            else:
                messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o cliente: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o cliente: {e}")
    
    def limpar_campos_cliente(self):
        """Limpa todos os campos do cliente"""
        self.cliente_id = None
        self.veiculo_id = None
        self.cliente_nome.set("")
        self.cliente_endereco.set("")
        self.cliente_cidade.set("")
        self.cliente_cpf_cnpj.set("")
        self.cliente_telefone.set("")
        self.cliente_email.set("")
        self.cliente_veiculo.set("")
        self.cliente_placa.set("")
        self.cliente_km.set("")
    
    def adicionar_item(self):
        """Adiciona um novo item à ordem de serviço"""
        descricao = self.entry_descricao.get()
        quantidade = self.entry_quantidade.get()
        valor_unit = self.entry_valor_unit.get()
        
        if not descricao or not quantidade or not valor_unit:
            messagebox.showwarning("Atenção", "Preencha todos os campos do item!")
            return
        
        try:
            qtd = float(quantidade)
            vl_unit = float(valor_unit)
            vl_total = qtd * vl_unit
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e Valor Unitário devem ser números!")
            return
        
        # Adiciona item na lista
        seq = len(self.itens_os) + 1
        item = (seq, descricao, qtd, vl_unit, vl_total)
        self.itens_os.append(item)
        
        # Adiciona na Treeview
        self.tree_itens.insert('', tk.END, values=item)
        
        # Atualiza total
        self.atualizar_total()
        
        # Limpa campos
        self.entry_descricao.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_valor_unit.delete(0, tk.END)
        self.entry_descricao.focus()
    
    def remover_item(self):
        """Remove o item selecionado da ordem de serviço"""
        selected_item = self.tree_itens.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um item para remover!")
            return
        
        # Remove da Treeview
        item_data = self.tree_itens.item(selected_item)['values']
        self.tree_itens.delete(selected_item)
        
        # Remove da lista
        for idx, item in enumerate(self.itens_os):
            if item[0] == item_data[0]:
                self.itens_os.pop(idx)
                break
        
        # Reorganiza as sequências
        for idx, item in enumerate(self.itens_os):
            self.itens_os[idx] = (idx+1,) + item[1:]
        
        # Atualiza a Treeview
        self.tree_itens.delete(*self.tree_itens.get_children())
        for item in self.itens_os:
            self.tree_itens.insert('', tk.END, values=item)
        
        # Atualiza total
        self.atualizar_total()
    
    def atualizar_total(self):
        """Atualiza o valor total da ordem de serviço"""
        total = sum(item[4] for item in self.itens_os)
        self.valor_total.set(self.formatar_moeda(total))
    
    def formatar_moeda(self, valor):
        """Formata um valor float como string monetária"""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def calcular_total_servico(self, *args):
        """Calcula o valor total do serviço solicitado"""
        try:
            qtd = float(self.servico_qtd.get() or 0)
            valor = float(self.servico_valor.get() or 0)
            total = qtd * valor
            self.servico_total.set(self.formatar_moeda(total))
        except ValueError:
            self.servico_total.set("R$ 0,00")

    def adicionar_servico_como_item(self):
        """Adiciona o serviço solicitado como um item da OS"""
        descricao = self.servico_solicitado.get()
        qtd = self.servico_qtd.get()
        valor = self.servico_valor.get()
        
        if not descricao:
            messagebox.showwarning("Atenção", "Informe a descrição do serviço!")
            return
            
        if not qtd or not valor:
            messagebox.showwarning("Atenção", "Informe quantidade e valor unitário!")
            return
            
        try:
            qtd = float(qtd)
            vl_unit = float(valor)
            vl_total = qtd * vl_unit
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e Valor Unitário devem ser números!")
            return
        
        # Adiciona item na lista
        seq = len(self.itens_os) + 1
        item = (seq, descricao, qtd, vl_unit, vl_total)
        self.itens_os.append(item)
        
        # Adiciona na Treeview
        self.tree_itens.insert('', tk.END, values=item)
        
        # Atualiza total
        self.atualizar_total()
        
        # Limpa campos do serviço
        self.servico_solicitado.set("")
        self.servico_qtd.set("")
        self.servico_valor.set("")
        self.servico_total.set("R$ 0,00")
    
    def salvar_os(self):
        """Salva a ordem de serviço no banco de dados"""
        if not self.cliente_id:
            messagebox.showwarning("Atenção", "Selecione um cliente para a OS!")
            return
            
        if not self.itens_os:
            messagebox.showwarning("Atenção", "Adicione pelo menos um item na OS!")
            return
            
        try:
            valor_total = sum(item[4] for item in self.itens_os)
            
            if self.os_id:
                # Atualiza OS existente
                self.c.execute('''UPDATE ordens_servico SET
                                cliente_id=?, veiculo_id=?, servico_solicitado=?, 
                                observacoes=?, valor_total=?, status=?
                                WHERE id=?''',
                             (self.cliente_id, self.veiculo_id, self.servico_solicitado.get(),
                              self.observacoes.get(), valor_total, self.status_os.get(),
                              self.os_id))
                
                # Remove os itens antigos
                self.c.execute("DELETE FROM itens_os WHERE os_id=?", (self.os_id,))
            else:
                # Insere nova OS
                self.c.execute('''INSERT INTO ordens_servico 
                                (numero, cliente_id, veiculo_id, data_emissao, 
                                servico_solicitado, observacoes, valor_total, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                             (self.numero_os.get(), self.cliente_id, self.veiculo_id,
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              self.servico_solicitado.get(), self.observacoes.get(),
                              valor_total, self.status_os.get()))
                self.os_id = self.c.lastrowid
            
            # Insere os itens da OS
            for item in self.itens_os:
                self.c.execute('''INSERT INTO itens_os 
                                (os_id, descricao, quantidade, valor_unitario, valor_total)
                                VALUES (?, ?, ?, ?, ?)''',
                             (self.os_id, item[1], item[2], item[3], item[4]))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Ordem de Serviço salva com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar a OS: {e}")

    def carregar_os(self, os_id):
        """Carrega uma OS existente para edição"""
        try:
            # Limpa os campos atuais
            self.limpar_campos_os()
            
            # Carrega os dados da OS
            self.c.execute("SELECT * FROM ordens_servico WHERE id=?", (os_id,))
            os_data = self.c.fetchone()
            
            if not os_data:
                messagebox.showerror("Erro", "OS não encontrada!")
                return
                
            self.os_id = os_data[0]
            self.numero_os.set(os_data[1])
            self.cliente_id = os_data[2]
            self.veiculo_id = os_data[3]
            self.data_emissao.set(os_data[4])
            self.servico_solicitado.set(os_data[5])
            self.observacoes.set(os_data[6])
            self.status_os.set(os_data[8])
            
            # Carrega os dados do cliente e veículo
            self.carregar_dados_cliente(self.cliente_id)
            
            # Carrega os itens da OS
            self.c.execute("SELECT descricao, quantidade, valor_unitario, valor_total FROM itens_os WHERE os_id=?", (os_id,))
            itens = self.c.fetchall()
            
            self.itens_os = []
            for idx, item in enumerate(itens):
                self.itens_os.append((idx+1, item[0], item[1], item[2], item[3]))
                self.tree_itens.insert('', tk.END, values=(idx+1, item[0], item[1], item[2], item[3]))
            
            self.atualizar_total()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar a OS: {e}")

    def carregar_ultima_os(self):
        """Carrega a última OS criada, se existir"""
        self.c.execute("SELECT id FROM ordens_servico ORDER BY id DESC LIMIT 1")
        ultima_os = self.c.fetchone()
        if ultima_os:
            self.carregar_os(ultima_os[0])

    def carregar_os_dialog(self):
        """Abre diálogo para selecionar uma OS para carregar"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Carregar Ordem de Serviço")
        dialog.geometry("800x500")
        
        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(dialog, padding="10")
        frame_pesquisa.pack(fill=tk.X)
        
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT)
        entry_pesquisa = ttk.Entry(frame_pesquisa, width=30)
        entry_pesquisa.pack(side=tk.LEFT, padx=5)
        entry_pesquisa.bind("<KeyRelease>", lambda e: self.atualizar_lista_os(entry_pesquisa.get(), tree))
        
        # Treeview para listar OS
        columns = ('id', 'numero', 'cliente', 'data', 'valor', 'status')
        tree = ttk.Treeview(dialog, columns=columns, show='headings', height=15)
        
        tree.heading('id', text='ID')
        tree.heading('numero', text='Número OS')
        tree.heading('cliente', text='Cliente')
        tree.heading('data', text='Data')
        tree.heading('valor', text='Valor')
        tree.heading('status', text='Status')
        
        tree.column('id', width=50, anchor=tk.CENTER)
        tree.column('numero', width=100, anchor=tk.CENTER)
        tree.column('cliente', width=250, anchor=tk.W)
        tree.column('data', width=100, anchor=tk.CENTER)
        tree.column('valor', width=100, anchor=tk.E)
        tree.column('status', width=100, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões
        frame_botoes = ttk.Frame(dialog, padding="10")
        frame_botoes.pack(fill=tk.X)
        
        ttk.Button(frame_botoes, text="Carregar", 
                  command=lambda: self.selecionar_os_para_carregar(tree, dialog)).pack(side=tk.LEFT)
        ttk.Button(frame_botoes, text="Cancelar", 
                  command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Carrega a lista inicial
        self.atualizar_lista_os("", tree)

    def atualizar_lista_os(self, filtro, tree):
        """Atualiza a lista de OS na treeview"""
        for item in tree.get_children():
            tree.delete(item)
            
        if filtro:
            self.c.execute('''SELECT os.id, os.numero, c.nome, os.data_emissao, os.valor_total, os.status
                           FROM ordens_servico os
                           JOIN clientes c ON os.cliente_id = c.id
                           WHERE os.numero LIKE ? OR c.nome LIKE ? OR os.status LIKE ?
                           ORDER BY os.id DESC''',
                        (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT os.id, os.numero, c.nome, os.data_emissao, os.valor_total, os.status
                           FROM ordens_servico os
                           JOIN clientes c ON os.cliente_id = c.id
                           ORDER BY os.id DESC''')
        
        for os_data in self.c.fetchall():
            valor_formatado = f"R$ {os_data[4]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tree.insert('', tk.END, values=(os_data[0], os_data[1], os_data[2], 
                                      os_data[3][:10], valor_formatado, os_data[5]))

    def selecionar_os_para_carregar(self, tree, dialog):
        """Seleciona a OS para carregar"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione uma OS para carregar!")
            return
            
        os_id = tree.item(selected_item)['values'][0]
        self.carregar_os(os_id)
        dialog.destroy()

    def fechar_os(self):
        """Fecha a OS, alterando seu status"""
        if not self.os_id:
            messagebox.showwarning("Atenção", "Salve a OS antes de fechar!")
            return
            
        if self.status_os.get() == "Fechada":
            messagebox.showinfo("Informação", "Esta OS já está fechada!")
            return
            
        if messagebox.askyesno("Confirmar", "Deseja realmente fechar esta OS?"):
            self.status_os.set("Fechada")
            self.c.execute('''UPDATE ordens_servico SET 
                            status=?, data_fechamento=?
                            WHERE id=?''',
                         ("Fechada", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.os_id))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "OS fechada com sucesso!")

    def listar_ordens_servico(self):
        """Lista todas as ordens de serviço"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Lista de Ordens de Serviço")
        dialog.geometry("1000x600")
        
        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(dialog, padding="10")
        frame_pesquisa.pack(fill=tk.X)
        
        ttk.Label(frame_pesquisa, text="Período:").pack(side=tk.LEFT)
        
        self.data_inicio = ttk.Entry(frame_pesquisa, width=10)
        self.data_inicio.pack(side=tk.LEFT, padx=5)
        self.data_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Label(frame_pesquisa, text="até").pack(side=tk.LEFT)
        
        self.data_fim = ttk.Entry(frame_pesquisa, width=10)
        self.data_fim.pack(side=tk.LEFT, padx=5)
        self.data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Button(frame_pesquisa, text="Filtrar", 
                  command=lambda: self.filtrar_os(tree)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(frame_pesquisa, text="Imprimir Relatório", 
                  command=lambda: self.gerar_relatorio_os(tree)).pack(side=tk.RIGHT)
        
        # Treeview para listar OS
        columns = ('id', 'numero', 'cliente', 'veiculo', 'data', 'valor', 'status')
        tree = ttk.Treeview(dialog, columns=columns, show='headings', height=20)
        
        tree.heading('id', text='ID')
        tree.heading('numero', text='Número OS')
        tree.heading('cliente', text='Cliente')
        tree.heading('veiculo', text='Veículo')
        tree.heading('data', text='Data')
        tree.heading('valor', text='Valor')
        tree.heading('status', text='Status')
        
        tree.column('id', width=50, anchor=tk.CENTER)
        tree.column('numero', width=100, anchor=tk.CENTER)
        tree.column('cliente', width=200, anchor=tk.W)
        tree.column('veiculo', width=150, anchor=tk.W)
        tree.column('data', width=100, anchor=tk.CENTER)
        tree.column('valor', width=100, anchor=tk.E)
        tree.column('status', width=100, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Carrega a lista inicial
        self.filtrar_os(tree)

    def filtrar_os(self, tree):
        """Filtra as OS por período"""
        try:
            data_inicio = datetime.strptime(self.data_inicio.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            data_fim = datetime.strptime(self.data_fim.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
            return
            
        for item in tree.get_children():
            tree.delete(item)
            
        self.c.execute('''SELECT os.id, os.numero, c.nome, v.modelo, os.data_emissao, os.valor_total, os.status
                       FROM ordens_servico os
                       JOIN clientes c ON os.cliente_id = c.id
                       LEFT JOIN veiculos v ON os.veiculo_id = v.id
                       WHERE date(os.data_emissao) BETWEEN ? AND ?
                       ORDER BY os.id DESC''',
                    (data_inicio, data_fim))
        
        for os_data in self.c.fetchall():
            valor_formatado = f"R$ {os_data[5]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tree.insert('', tk.END, values=(os_data[0], os_data[1], os_data[2], os_data[3], 
                                          os_data[4][:10], valor_formatado, os_data[6]))

    def gerar_relatorio_os(self, tree):
        """Gera um relatório em PDF com as OS listadas"""
        try:
            selected_items = tree.selection()
            if not selected_items:
                if not messagebox.askyesno("Confirmar", "Deseja gerar relatório para todas as OS listadas?"):
                    return
                selected_items = tree.get_children()
            
            os_list = []
            for item in selected_items:
                os_data = tree.item(item)['values']
                os_list.append({
                    'id': os_data[0],
                    'numero': os_data[1],
                    'cliente': os_data[2],
                    'veiculo': os_data[3],
                    'data': os_data[4],
                    'valor': os_data[5],
                    'status': os_data[6]
                })
            
            # Cria o PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Cabeçalho
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, self.dados_empresa["nome"], 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, self.dados_empresa["endereco"] + " - " + self.dados_empresa["cidade"], 0, 1, 'C')
            pdf.cell(0, 5, f"CNPJ: {self.dados_empresa['cnpj']} - IE: {self.dados_empresa['ie']}", 0, 1, 'C')
            
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, "Relatório de Ordens de Serviço", 0, 1, 'C')
            
            periodo = f"Período: {self.data_inicio.get()} a {self.data_fim.get()}"
            pdf.cell(0, 5, periodo, 0, 1, 'C')
            
            pdf.ln(5)
            
            # Cabeçalho da tabela
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(15, 8, "ID", 1, 0, 'C')
            pdf.cell(25, 8, "Número", 1, 0, 'C')
            pdf.cell(60, 8, "Cliente", 1, 0)
            pdf.cell(40, 8, "Veículo", 1, 0)
            pdf.cell(25, 8, "Data", 1, 0, 'C')
            pdf.cell(25, 8, "Valor", 1, 0, 'R')
            pdf.cell(20, 8, "Status", 1, 1, 'C')
            
            # Dados das OS
            pdf.set_font('Arial', '', 9)
            total = 0
            for os_item in os_list:
                pdf.cell(15, 8, str(os_item['id']), 1, 0, 'C')
                pdf.cell(25, 8, os_item['numero'], 1, 0, 'C')
                pdf.cell(60, 8, os_item['cliente'], 1, 0)
                pdf.cell(40, 8, os_item['veiculo'], 1, 0)
                pdf.cell(25, 8, os_item['data'], 1, 0, 'C')
                pdf.cell(25, 8, os_item['valor'], 1, 0, 'R')
                pdf.cell(20, 8, os_item['status'], 1, 1, 'C')
                
                # Soma o valor total
                valor = float(os_item['valor'].replace("R$ ", "").replace(".", "").replace(",", "."))
                total += valor
            
            # Total
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(165, 8, "TOTAL:", 1, 0, 'R')
            pdf.cell(25, 8, f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 1, 'R')
            
            # Salva o PDF
            os.makedirs("relatorios", exist_ok=True)
            data_relatorio = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = f"relatorios/Relatorio_OS_{data_relatorio}.pdf"
            pdf.output(pdf_path)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nSalvo em: {os.path.abspath(pdf_path)}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o relatório: {e}")

    def gerar_pdf_os(self):
        """Gera um PDF da ordem de serviço"""
        if not self.cliente_id:
            messagebox.showwarning("Atenção", "Selecione um cliente para a OS!")
            return
            
        if not self.itens_os:
            messagebox.showwarning("Atenção", "Adicione pelo menos um item na OS!")
            return
        
        try:
            from fpdf import FPDF
            from datetime import datetime
            
            # Cria o PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Cabeçalho
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, self.dados_empresa["nome"], 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, self.dados_empresa["endereco"] + " - " + self.dados_empresa["cidade"], 0, 1, 'C')
            pdf.cell(0, 5, f"CNPJ: {self.dados_empresa['cnpj']} - IE: {self.dados_empresa['ie']} - Tel: {self.dados_empresa['telefone']}", 0, 1, 'C')
            
            pdf.ln(5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(10)
            
            # Dados da OS
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(95, 10, f"Ordem de Serviço Nº: {self.numero_os.get()}", 0, 0)
            pdf.cell(95, 10, f"Data: {self.data_emissao.get()}", 0, 1, 'R')
            
            # Dados do cliente
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Dados do Cliente", 0, 1)
            pdf.set_font('Arial', '', 10)
            
            pdf.cell(0, 5, f"Nome: {self.cliente_nome.get()}", 0, 1)
            pdf.cell(0, 5, f"Endereço: {self.cliente_endereco.get()}", 0, 1)
            pdf.cell(0, 5, f"Cidade: {self.cliente_cidade.get()}", 0, 1)
            pdf.cell(0, 5, f"CPF/CNPJ: {self.cliente_cpf_cnpj.get()} - Tel: {self.cliente_telefone.get()}", 0, 1)
            
            pdf.ln(5)
            
            # Dados do veículo
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Dados do Veículo", 0, 1)
            pdf.set_font('Arial', '', 10)
            
            pdf.cell(0, 5, f"Modelo: {self.cliente_veiculo.get()}", 0, 1)
            pdf.cell(0, 5, f"Placa: {self.cliente_placa.get()} - KM: {self.cliente_km.get()}", 0, 1)
            
            pdf.ln(10)
            
            # Serviço Solicitado
            if self.servico_solicitado.get():
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "Serviço Solicitado:", 0, 1)
                pdf.set_font('Arial', '', 10)
                
                pdf.cell(100, 8, self.servico_solicitado.get(), 1, 0)
                pdf.cell(20, 8, self.servico_qtd.get() or "0", 1, 0, 'C')
                pdf.cell(30, 8, f"R$ {float(self.servico_valor.get() or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 0, 'R')
                pdf.cell(30, 8, self.servico_total.get(), 1, 1, 'R')
                
                pdf.ln(5)
            
            # Itens da OS
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Itens da Ordem de Serviço", 0, 1)
            
            # Cabeçalho dos itens
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(100, 8, "Descrição", 1, 0)
            pdf.cell(20, 8, "Qtd", 1, 0, 'C')
            pdf.cell(30, 8, "Vl. Unit.", 1, 0, 'R')
            pdf.cell(30, 8, "Vl. Total", 1, 1, 'R')
            
            # Itens
            pdf.set_font('Arial', '', 10)
            for item in self.itens_os:
                pdf.cell(100, 8, item[1], 1, 0)
                pdf.cell(20, 8, f"{item[2]:.2f}", 1, 0, 'C')
                pdf.cell(30, 8, f"R$ {item[3]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 0, 'R')
                pdf.cell(30, 8, f"R$ {item[4]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 1, 'R')
            
            # Total
            total = sum(item[4] for item in self.itens_os)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(150, 10, "TOTAL:", 0, 0, 'R')
            pdf.cell(30, 10, f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 0, 1, 'R')
            
            # Observações
            if self.observacoes.get():
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "Observações:", 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 5, self.observacoes.get())
            
            # Status
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Status: {self.status_os.get()}", 0, 1)
            
            # Salva o PDF
            os.makedirs("ordens_servico", exist_ok=True)
            pdf_path = f"ordens_servico/OS_{self.numero_os.get()}.pdf"
            pdf.output(pdf_path)
            
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nSalvo em: {os.path.abspath(pdf_path)}")
        
        except ImportError:
            messagebox.showerror("Erro", "Biblioteca FPDF não instalada. Instale com: pip install fpdf")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {e}")
    
    def limpar_campos_os(self):
        """Limpa todos os campos da OS, exceto número e data"""
        self.os_id = None
        self.cliente_id = None
        self.veiculo_id = None
        self.limpar_campos_cliente()
        self.servico_solicitado.set("")
        self.observacoes.set("")
        self.status_os.set("Aberta")
        self.itens_os = []
        self.tree_itens.delete(*self.tree_itens.get_children())
        self.valor_total.set(0.0)
        self.servico_solicitado.set("")
        self.servico_qtd.set("")
        self.servico_valor.set("")
        self.servico_total.set("R$ 0,00")

    def limpar_tudo(self):
        """Limpa todos os campos da ordem de serviço"""
        if not messagebox.askyesno("Confirmar", "Deseja realmente limpar todos os dados?"):
            return
        
        self.limpar_campos_os()
        self.numero_os.set(self.gerar_numero_os())
        self.data_emissao.set(datetime.now().strftime("%d/%m/%Y %H:%M"))

    def nova_os(self):
        """Cria uma nova OS"""
        if not messagebox.askyesno("Confirmar", "Deseja criar uma nova OS? Todos os dados não salvos serão perdidos."):
            return
            
        self.limpar_campos_os()
        self.numero_os.set(self.gerar_numero_os())
        self.data_emissao.set(datetime.now().strftime("%d/%m/%Y %H:%M"))

if __name__ == "__main__":
    root = tk.Tk()
    app = OrdemServicoApp(root)
    root.mainloop()
