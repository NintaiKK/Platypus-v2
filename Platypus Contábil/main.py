import tkinter as tk
from tkinter import PhotoImage
from fpdf import FPDF
import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
import os
import csv
import json
import sqlite3

class Main:
    def __init__(self, root):
        self.root = root
        self.root.title("Platypus v2 - Contábil")
        self.root.geometry("1000x650")
        
        try:
            root.iconbitmap("none.ico")
        except:
            pass

        self.conn = sqlite3.connect('platycon.db')
        self.c = self.conn.cursor()

        self.criar_widgets()
        self.criar_tabela_clientes()
        self.criar_tabela_veiculos()
        self.criar_tabela_pecas()

    def criar_tabela_clientes(self):
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cnpj TEXT,
                    nome TEXT NOT NULL,
                    endereco TEXT,
                    cidade TEXT,
                    telefone TEXT,
                    email TEXT,
                    responsavel TEXT,
                    cpf_responsavel TEXT,
                    dt_nascimento TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar tabela: {str(e)}")

    def criar_tabela_veiculos(self):
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS veiculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resp_veiculo TEXT NOT NULL,
                    placa TEXT NOT NULL,
                    km TEXT,
                    ano TEXT,
                    modelo TEXT
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar tabela: {str(e)}")

    def criar_tabela_pecas(self):
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS pecas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_nf TEXT,
                    cod_in TEXT NOT NULL,
                    descr TEXT,
                    fabric TEXT,
                    cod_pec TEXT,
                    vlr_cust TEXT,
                    vlr_venda TEXT
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar tabela: {str(e)}")

    def pesquisar_clientes(self, event=None):
        """Pesquisa clientes conforme texto digitado"""
        filtro = self.entry_pesquisa_cliente.get()
        self.carregar_lista_clientes(filtro)

    def pesquisar_veiculo(self, event=None):
        """Pesquisa veiculos conforme texto digitado"""
        filtro = self.entry_pesquisa_veiculo.get()
        self.carregar_lista_veiculos(filtro)

    def pesquisar_peca(self, event=None):
        """Pesquisa veiculos conforme texto digitado"""
        filtro = self.entry_pesquisa_peca.get()
        self.carregar_lista_peca(filtro)

    def carregar_lista_veiculos(self, filtro=None):

        # Limpa a treeview
        for item in self.tree_veiculos.get_children():
            self.tree_veiculos.delete(item)
            
        # Consulta os veiculos no banco de dados
        if filtro:
            self.c.execute('''SELECT id, resp_veiculo, placa, km, ano, modelo 
                            FROM veiculos 
                            WHERE resp_veiculo LIKE ? OR placa LIKE ? 
                            ORDER BY resp_veiculo''', (f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT id, resp_veiculo, placa, km, ano, modelo 
                            FROM veiculos 
                            ORDER BY resp_veiculo''')
            
        veiculo = self.c.fetchall()
            
        # Adiciona os veiculos na treeview
        for veiculo in veiculo:
            self.tree_veiculos.insert('', tk.END, values=veiculo)

    #Carregar Lista
    def carregar_lista_clientes(self, filtro=None):

        # Limpa a treeview
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
            
        # Consulta os clientes no banco de dados
        if filtro:
            self.c.execute('''SELECT id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento 
                                FROM clientes 
                                WHERE nome LIKE ? OR cnpj LIKE ? 
                                ORDER BY nome''', (f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento 
                                FROM clientes 
                                ORDER BY nome''')
            
        cliente = self.c.fetchall()
            
        # Adiciona os clientes na treeview
        for cliente in cliente:
            self.tree_clientes.insert('', tk.END, values=cliente)

    #Carregar Lista
    def carregar_lista_peca(self, filtro=None):

        # Limpa a treeview
        for item in self.tree_pecas.get_children():
            self.tree_peca.delete(item)
            
        # Consulta os clientes no banco de dados
        if filtro:
            self.c.execute('''SELECT id, cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda 
                                FROM pecas 
                                WHERE descr LIKE ? OR cod_pec LIKE ? 
                                ORDER BY id''', (f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT id, cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda 
                                FROM pecas 
                                ORDER BY id''')
            
        cliente = self.c.fetchall()
            
        # Adiciona os clientes na treeview
        for cliente in cliente:
            self.tree_clientes.insert('', tk.END, values=cliente)

    #Novo Cliente
    def novo_cliente(self):

        self.novo_cli_wnd = tk.Toplevel(self.root)
        self.novo_cli_wnd.title("Cadastrar Cliente")
        self.novo_cli_wnd.geometry("800x400")
        self.novo_cli_wnd.resizable(False, False)

        self.novo_cli_wnd.transient(self.root)
        self.novo_cli_wnd.grab_set()

        frame = ttk.Frame(self.novo_cli_wnd, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="CNPJ/CPF").grid(row=0, column=0, sticky=tk.W, pady=5)
        cnpj_entry = ttk.Entry(frame, width=40)
        cnpj_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Razão Social/Nome").grid(row=1, column=0, sticky=tk.W, pady=5)
        nome_entry = ttk.Entry(frame, width=40)
        nome_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Endereço").grid(row=2, column=0, sticky=tk.W, pady=5)
        endereco_entry = ttk.Entry(frame, width=40)
        endereco_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Cidade/UF").grid(row=2, column=2, sticky=tk.E, pady=5)
        cidade_entry = ttk.Entry(frame, width=40)
        cidade_entry.grid(row=2, column=3, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Telefone").grid(row=3, column=0, sticky=tk.W, pady=5)
        telefone_entry = ttk.Entry(frame, width=40)
        telefone_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="E-mail").grid(row=3, column=2, sticky=tk.E, pady=5)
        email_entry = ttk.Entry(frame, width=40)
        email_entry.grid(row=3, column=3, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Responsável").grid(row=4, column=0, sticky=tk.W, pady=5)
        resp_entry = ttk.Entry(frame, width=40)
        resp_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="CPF Responsável").grid(row=4, column=2, sticky=tk.E, pady=5)
        cpfresp_entry = ttk.Entry(frame, width=40)
        cpfresp_entry.grid(row=4, column=3, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Data de Nascimento").grid(row=5, column=0, sticky=tk.E, pady=5)
        dtnascimento_entry = ttk.Entry(frame, width=40)
        dtnascimento_entry.grid(row=5, column=1, pady=5, padx=(10, 0))

        # Frame para botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
            
        # Botão Salvar
        ttk.Button(btn_frame, text="Salvar", command=lambda: self.salvar_cliente(
            cnpj_entry.get(), nome_entry.get(), endereco_entry.get(), cidade_entry.get(), telefone_entry.get(), email_entry.get(), resp_entry.get(), cpfresp_entry.get(), dtnascimento_entry.get()
        )).pack(side=tk.LEFT, padx=5)
            
        # Botão Cancelar
        ttk.Button(btn_frame, text="Cancelar", command=self.novo_cli_wnd.destroy).pack(side=tk.LEFT, padx=5)
            
        # Focar no campo nome
        cnpj_entry.focus_set()

    # Salvar clientes
    def salvar_cliente(self, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento):
        if not nome:
            messagebox.showerror("Erro", "O campo nome é obrigatório!")
            return
            
        try:
            conn = sqlite3.connect('platycon.db')
            cursor = conn.cursor()
                
            # Criar tabela se não existir
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cnpj TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        endereco TEXT,
                        cidade TEXT,
                        telefone TEXT,
                        email TEXT,
                        responsavel TEXT,
                        cpf_responsavel TEXT,
                        dt_nascimento TEXT,
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
            ''')
                
            # Inserir cliente
            cursor.execute(
                "INSERT INTO clientes (cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento)
            )
                
            conn.commit()
            conn.close()
                
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.novo_cli_wnd.destroy()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {str(e)}")

        #Clientes
    def rel_clientes(self):

        self.rel_cli_wnd = tk.Toplevel(self.root)
        self.rel_cli_wnd.title("Relátório Clientes")
        self.rel_cli_wnd.geometry("1200x500")

        self.rel_cli_wnd.transient(self.root)
        self.rel_cli_wnd.grab_set()

        # Frame principal
        main_frame = ttk.Frame(self.rel_cli_wnd, padding="10")
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
        columns = ('id', 'cnpj', 'nome', 'endereco', 'cidade', 'telefone', 'email', 'responsavel', 'cpf_responsavel', 'dt_nascimento')
        self.tree_clientes = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
        # Cabeçalhos
        self.tree_clientes.heading('id', text='ID')
        self.tree_clientes.heading('cnpj', text='CPF/CNPJ')
        self.tree_clientes.heading('nome', text='Nome/Razão Social')
        self.tree_clientes.heading('endereco', text='Endereço')
        self.tree_clientes.heading('cidade', text='Cidade/UF')
        self.tree_clientes.heading('telefone', text='Telefone')
        self.tree_clientes.heading('email', text='Email')
        self.tree_clientes.heading('responsavel', text='Responsável')
        self.tree_clientes.heading('cpf_responsavel', text='CPF Responsável')
        self.tree_clientes.heading('dt_nascimento', text='Data de Nascimento')
            
        # Largura das colunas
        self.tree_clientes.column('id', width=50, anchor=tk.CENTER)
        self.tree_clientes.column('cnpj', width=120, anchor=tk.W)
        self.tree_clientes.column('nome', width=250, anchor=tk.W)
        self.tree_clientes.column('endereco', width=150, anchor=tk.W)
        self.tree_clientes.column('cidade', width=150, anchor=tk.W)
        self.tree_clientes.column('telefone', width=100, anchor=tk.W)
        self.tree_clientes.column('email', width=100, anchor=tk.W)
        self.tree_clientes.column('responsavel', width=100, anchor=tk.W)
        self.tree_clientes.column('cpf_responsavel', width=120, anchor=tk.W)
        self.tree_clientes.column('dt_nascimento', width=100, anchor=tk.W)
            
        self.tree_clientes.pack(fill=tk.BOTH, expand=True)
            
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        # Botões de ação
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=10)
            
        #ttk.Button(frame_botoes, text="Editar", 
        #        command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
            
        #ttk.Button(frame_botoes, text="Excluir", 
        #        command=self.excluir_cliente).pack(side=tk.LEFT, padx=5)
            
        # Carrega a lista de clientes
        self.carregar_lista_clientes()

    def novo_veiculo(self):

        self.novo_veiculo_wnd = tk.Toplevel(self.root)
        self.novo_veiculo_wnd.title("Cadastrar Veículo")
        self.novo_veiculo_wnd.geometry("500x400")
        self.novo_veiculo_wnd.resizable(False, False)

        self.novo_veiculo_wnd.transient(self.root)
        self.novo_veiculo_wnd.grab_set()

        frame = ttk.Frame(self.novo_veiculo_wnd, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Responsável").grid(row=0, column=0, sticky=tk.W, pady=5)
        resp_entry = ttk.Entry(frame, width=40)
        resp_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        #ttk.Button(frame, text="Buscar", command=self.busc_resp).grid(row=0, column=1, sticky=tk.E, pady=5)

        ttk.Label(frame, text="Placa").grid(row=1, column=0, sticky=tk.W, pady=5)
        placa_entry = ttk.Entry(frame, width=40)
        placa_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="KM").grid(row=2, column=0, sticky=tk.W, pady=5)
        km_entry = ttk.Entry(frame, width=40)
        km_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Ano").grid(row=3, column=0, sticky=tk.W, pady=5)
        ano_entry = ttk.Entry(frame, width=40)
        ano_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Modelo").grid(row=4, column=0, sticky=tk.W, pady=5)
        modelo_entry = ttk.Entry(frame, width=40)
        modelo_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        # Frame para botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
            
        # Botão Salvar
        ttk.Button(btn_frame, text="Salvar", command=lambda: self.salvar_veiculo(
            resp_entry.get(), placa_entry.get(), km_entry.get(), ano_entry.get(), modelo_entry.get()
        )).pack(side=tk.LEFT, padx=5)
            
        # Botão Cancelar
        ttk.Button(btn_frame, text="Cancelar", command=self.novo_veiculo_wnd.destroy).pack(side=tk.LEFT, padx=5)

    # Salvar veiculos
    def salvar_veiculo(self, resp_veiculo, placa, km, ano, modelo):
        if not resp_veiculo:
            messagebox.showerror("Erro", 'O campo "responsável" é obrigatório!')
            return
            
        try:
            conn = sqlite3.connect('platycon.db')
            cursor = conn.cursor()
                
            # Criar tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS veiculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resp_veiculo TEXT NOT NULL,
                    placa TEXT NOT NULL,
                    km TEXT,
                    ano TEXT,
                    modelo TEXT
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
                
            # Inserir veiculo
            cursor.execute(
                "INSERT INTO veiculos (resp_veiculo, placa, km, ano, modelo) VALUES (?, ?, ?, ?, ?)",
                (resp_veiculo, placa, km, ano, modelo)
            )
                
            conn.commit()
            conn.close()
                
            messagebox.showinfo("Sucesso", "Veículo cadastrado com sucesso!")
            self.novo_veiculo_wnd.destroy()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar veículo: {str(e)}")

    def rel_veiculos(self):

        self.rel_veic_wnd = tk.Toplevel(self.root)
        self.rel_veic_wnd.title("Relátório Veículos")
        self.rel_veic_wnd.geometry("1200x500")
        self.rel_veic_wnd.resizable(False, False)

        self.rel_veic_wnd.transient(self.root)
        self.rel_veic_wnd.grab_set()

        # Frame principal
        main_frame = ttk.Frame(self.rel_veic_wnd, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
            
        # Barra de pesquisa
        frame_pesq_vei = ttk.Frame(main_frame)
        frame_pesq_vei.pack(fill=tk.X, pady=5)
            
        ttk.Label(frame_pesq_vei, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa_veiculo = ttk.Entry(frame_pesq_vei, width=30)
        self.entry_pesquisa_veiculo.pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa_veiculo.bind("<KeyRelease>", self.pesquisar_veiculo)
            
        ttk.Button(frame_pesq_vei, text="Novo Veículo", 
            command=self.novo_veiculo).pack(side=tk.RIGHT, padx=5)
            
        # Treeview para listar veiculos
        columns = ('id', 'resp_veiculo', 'placa', 'km', 'ano', 'modelo')
        self.tree_veiculos = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
        # Cabeçalhos
        self.tree_veiculos.heading('id', text='ID')
        self.tree_veiculos.heading('resp_veiculo', text='Responsável')
        self.tree_veiculos.heading('placa', text='Placa')
        self.tree_veiculos.heading('km', text='KM')
        self.tree_veiculos.heading('ano', text='Ano')
        self.tree_veiculos.heading('modelo', text='Modelo')
            
        # Largura das colunas
        self.tree_veiculos.column('id', width=50, anchor=tk.CENTER)
        self.tree_veiculos.column('resp_veiculo', width=120, anchor=tk.W)
        self.tree_veiculos.column('placa', width=80, anchor=tk.W)
        self.tree_veiculos.column('km', width=80, anchor=tk.W)
        self.tree_veiculos.column('ano', width=80, anchor=tk.W)
        self.tree_veiculos.column('modelo', width=150, anchor=tk.W)
            
        self.tree_veiculos.pack(fill=tk.BOTH, expand=True)
            
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree_veiculos.yview)
        self.tree_veiculos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        # Botões de ação
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=10)
            
        #ttk.Button(frame_botoes, text="Editar", 
        #    command=self.editar_veiculo).pack(side=tk.LEFT, padx=5)
            
        #ttk.Button(frame_botoes, text="Excluir", 
        #    command=self.excluir_veiculo).pack(side=tk.LEFT, padx=5)
            
        # Carrega a lista de veículos
        self.carregar_lista_veiculos()

    def nova_peca(self):

        self.nova_peca_wnd = tk.Toplevel(self.root)
        self.nova_peca_wnd.title("Cadastrar peça")
        self.nova_peca_wnd.geometry("500x400")
        self.nova_peca_wnd.resizable(False, False)

        self.nova_peca_wnd.transient(self.root)
        self.nova_peca_wnd.grab_set()

        # Frame principal
        main_frame = ttk.Frame(self.nova_peca_wnd, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Código NF").grid(row=0, column=0, sticky=tk.W, pady=5)
        cod_nf_entry = ttk.Entry(main_frame, width=40)
        cod_nf_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Código interno").grid(row=1, column=0, sticky=tk.W, pady=5)
        cod_in_entry = ttk.Entry(main_frame, width=40)
        cod_in_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Descrição").grid(row=2, column=0, sticky=tk.W, pady=5)
        descr_entry = ttk.Entry(main_frame, width=40)
        descr_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Fabricante").grid(row=3, column=0, sticky=tk.W, pady=5)
        fabric_entry = ttk.Entry(main_frame, width=40)
        fabric_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Código Peça").grid(row=4, column=0, sticky=tk.W, pady=5)
        cod_pec_entry = ttk.Entry(main_frame, width=40)
        cod_pec_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Preço custo").grid(row=5, column=0, sticky=tk.W, pady=5)
        vlr_cust_entry = ttk.Entry(main_frame, width=40)
        vlr_cust_entry.grid(row=5, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Valor venda").grid(row=5, column=0, sticky=tk.W, pady=5)
        vlr_venda_entry = ttk.Entry(main_frame, width=40)
        vlr_venda_entry.grid(row=6, column=1, pady=5, padx=(10, 0))

        # Frame para botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
           
        # Botão Salvar
        ttk.Button(btn_frame, text="Salvar", command=lambda: self.salvar_peca(
            cod_nf_entry.get(), cod_in_entry.get(), descr_entry.get(), fabric_entry.get(), cod_pec_entry.get(), vlr_cust_entry.get(), vlr_venda_entry.get(), self.novo_cli_wnd
        )).pack(side=tk.LEFT, padx=5)
            
        # Botão Cancelar
        ttk.Button(btn_frame, text="Cancelar", command=self.nova_peca_wnd.destroy).pack(side=tk.LEFT, padx=5)

        # Salvar peças
    def salvar_veiculo(self, cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda):
        if not cod_in:
            messagebox.showerror("Erro", 'O campo "Código interno" é obrigatório!')
            return
            
        try:
            conn = sqlite3.connect('platypus.db')
            cursor = conn.cursor()
                
            # Criar tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pecas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_nf TEXT,
                    cod_in TEXT NOT NULL,
                    descr TEXT,
                    fabric TEXT,
                    cod_pec TEXT,
                    vlr_cust TEXT,
                    vlr_venda TEXT
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
                
            # Inserir cliente
            cursor.execute(
                "INSERT INTO clientes (cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda)
            )
                
            conn.commit()
            conn.close()
                
            messagebox.showinfo("Sucesso", "Peça cadastrado com sucesso!")
            self.novo_cli_wnd.destroy()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar peça: {str(e)}")

    def estoque(self):

        self.estoque_wnd = tk.Toplevel(self.root)
        self.estoque_wnd.title("Estoque")
        self.estoque_wnd.geometry("1200x500")
        self.estoque_wnd.resizable(False, False)

        self.estoque_wnd.transient(self.root)
        self.estoque_wnd.grab_set()

        # Frame principal
        main_frame = ttk.Frame(self.estoque_wnd, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
            
        # Barra de pesquisa
        frame_pesq_peca = ttk.Frame(main_frame)
        frame_pesq_peca.pack(fill=tk.X, pady=5)
            
        ttk.Label(frame_pesq_peca, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa_peca = ttk.Entry(frame_pesq_peca, width=30)
        self.entry_pesquisa_peca.pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa_peca.bind("<KeyRelease>", self.pesquisar_peca)
            
        ttk.Button(frame_pesq_peca, text="Nova Peça", 
            command=self.nova_peca).pack(side=tk.RIGHT, padx=5)
            
        # Treeview para listar veiculos
        columns = ('id','cod_nf', 'cod_in', 'descr', 'fabric', 'cod_pec', 'vlr_cust', 'vlr_venda')
        self.tree_pecas = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
        # Cabeçalhos
        self.tree_pecas.heading('id', text='ID')
        self.tree_pecas.heading('cod_nf', text='Código NF')
        self.tree_pecas.heading('cod_in', text='Código interno')
        self.tree_pecas.heading('descr', text='Descrição')
        self.tree_pecas.heading('fabric', text='Fabricante')
        self.tree_pecas.heading('cod_pec', text='Código OEM')
        self.tree_pecas.heading('vlr_cust', text='Valor custo')
        self.tree_pecas.heading('vlr_venda', text='Valor venda')
            
        # Largura das colunas
        self.tree_pecas.column('id', width=50, anchor=tk.CENTER)
        self.tree_pecas.column('cod_nf', width=80, anchor=tk.W)
        self.tree_pecas.column('cod_in', width=80, anchor=tk.W)
        self.tree_pecas.column('descr', width=150, anchor=tk.W)
        self.tree_pecas.column('fabric', width=90, anchor=tk.W)
        self.tree_pecas.column('cod_pec', width=150, anchor=tk.W)
        self.tree_pecas.column('vlr_cust', width=80, anchor=tk.W)
        self.tree_pecas.column('vlr_venda', width=80, anchor=tk.W)
            
        self.tree_pecas.pack(fill=tk.BOTH, expand=True)
            
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree_pecas.yview)
        self.tree_pecas.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        # Botões de ação
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=10)
            
        #ttk.Button(frame_botoes, text="Editar", 
        #    command=self.editar_veiculo).pack(side=tk.LEFT, padx=5)
            
        #ttk.Button(frame_botoes, text="Excluir", 
        #    command=self.excluir_veiculo).pack(side=tk.LEFT, padx=5)
            
        # Carrega a lista de veículos
        self.carregar_lista_peca()

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


        #Barra menu cabeçalho
        menubar = tk.Menu(self.root)

        #Clientes
        menu_clientes = tk.Menu(menubar, tearoff=0)
        menu_clientes.add_command(label="Novo Cliente", command=self.novo_cliente)
        menu_clientes.add_command(label="Clientes", command=self.rel_clientes)

        menubar.add_cascade(label="Clientes", menu=menu_clientes)

        self.root.config(menu=menubar)

        #Veículos
        menu_veiculos = tk.Menu(menubar, tearoff=0)
        menu_veiculos.add_command(label="Novo Veículo", command=self.novo_veiculo)
        menu_veiculos.add_command(label="Veículos", command=self.rel_veiculos)

        menubar.add_cascade(label="Veículos", menu=menu_veiculos)

        #Peças
        menu_pecas = tk.Menu(menubar, tearoff=0)
        menu_pecas.add_command(label="Cadastrar Peça", command=self.nova_peca)
        menu_pecas.add_command(label="Estoque", command=self.estoque)
        #menu_pecas.add_command(label="Histórico", command=self.hist_pecas)

        menubar.add_cascade(label="Peças", menu=menu_pecas)

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()