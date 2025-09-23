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
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar tabela: {str(e)}")

    #Carregar Lista
    def carregar_lista_clientes(self, filtro=None):

        # Limpa a treeview
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
            
        # Consulta os clientes no banco de dados
        if filtro:
            self.c.execute('''SELECT id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel 
                                FROM clientes 
                                WHERE nome LIKE ? OR cnpj LIKE ? 
                                ORDER BY nome''', (f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel 
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

        # Frame para botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
            
        # Botão Salvar
        ttk.Button(btn_frame, text="Salvar", command=lambda: self.salvar_cliente(
            cnpj_entry.get(), nome_entry.get(), endereco_entry.get(), cidade_entry.get(), telefone_entry.get(), email_entry.get(), resp_entry.get(), cpfresp_entry.get()
        )).pack(side=tk.LEFT, padx=5)
            
        # Botão Cancelar
        ttk.Button(btn_frame, text="Cancelar", command=self.novo_cli_wnd.destroy).pack(side=tk.LEFT, padx=5)
            
        # Focar no campo nome
        cnpj_entry.focus_set()

    # Salvar clientes
    def salvar_cliente(self, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel):
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
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
            ''')
                
            # Inserir cliente
            cursor.execute(
                "INSERT INTO clientes (cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel)
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
        columns = ('id', 'cnpj', 'nome', 'endereco', 'cidade', 'telefone', 'email', 'responsavel', 'cpf_responsavel')
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

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()