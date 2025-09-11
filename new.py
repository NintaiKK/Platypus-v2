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
        self.root.title("Platypus v2 - Mecânica")
        self.root.geometry("1000x850")
        
        try:
            root.iconbitmap("22.ico")
        except:
            pass

        #self.iniciar_dtb

        #Carregar Lista
        def carregar_lista_clientes(self, filtro=None):

            # Limpa a treeview
            for item in self.tree_clientes.get_children():
                self.tree_clientes.delete(item)
            
            # Consulta os clientes no banco de dados
            if filtro:
                self.c.execute('''SELECT id, cnpj, nome, endereço, cidade, telefone, email, responsavel, cpf_responsavel 
                                FROM clientes 
                                WHERE nome LIKE ? OR cnpj LIKE ? 
                                ORDER BY nome''', (f'%{filtro}%', f'%{filtro}%'))
            else:
                self.c.execute('''SELECT id, cnpj, nome, endereço, cidade, telefone, email, responsavel, cpf_responsavel 
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

        #Janelas

        #Novo Cliente
        def novo_cliente(self):

            self.novo_cli_wnd = tk.Toplevel(self.root)
            self.novo_cli_wnd.title("Cadastrar Cliente")
            self.novo_cli_wnd.geometry("500x400")
            self.novo_cli_wnd.resizable(False, False)

            self.novo_cli_wnd.transient(self.root)
            self.novo_cli_wnd.grab_set()

            frame = ttk.Frame(self.novo_cli_wnd, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="CNPJ/CPF").grid(row=0, column=0, sticky=tk.W, pady=5)
            cnpj_entry = ttk.Entry(frame, widht=40)
            cnpj_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

            ttk.Label(frame, text="Razão Social/Nome").grid(row=1, column=0, sticky=tk.W, pady=5)
            nome_entry = ttk.Entry(frame, width=40)
            nome_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

            ttk.Label(frame, text="Endereço").grid(row=2, column=0, sticky=tk.W, pady=5)
            endereço_entry = ttk.Entry(frame, width=40)
            endereço_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

            ttk.Label(frame, text="Cidade/UF").grid(row=2, column=1, sticky=tk.E, pady=5)
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
            btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
            
            # Botão Salvar
            ttk.Button(btn_frame, text="Salvar", command=lambda: self.salvar_cliente(
                cnpj_entry.get(), nome_entry.get(), endereço_entry.get(), cidade_entry.get(), telefone_entry.get(), email_entry.get(), resp_entry.get(), cpfresp_entry.get(), self.novo_cli_wnd
            )).pack(side=tk.LEFT, padx=5)
            
            # Botão Cancelar
            ttk.Button(btn_frame, text="Cancelar", command=self.novo_cli_wnd.destroy).pack(side=tk.LEFT, padx=5)
            
            # Focar no campo nome
            cnpj_entry.focus_set()

        # Salvar clientes
        def salvar_cliente(self, cnpj, nome, endereço, cidade, telefone, email, responsavel, cpf_responsavel):
            if not nome:
                messagebox.showerror("Erro", "O campo nome é obrigatório!")
                return
            
            try:
                conn = sqlite3.connect('platypus.db')
                cursor = conn.cursor()
                
                # Criar tabela se não existir
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cnpj TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        cidade TEXT,
                        telefone TEXT,
                        email TEXT,
                        responsavel TEXT,
                        cpf_responsavel TEXT
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Inserir cliente
                cursor.execute(
                    "INSERT INTO clientes (nome, telefone, email, endereço) VALUES (?, ?, ?, ?)",
                    (cnpj, nome, endereço, cidade, telefone, email, responsavel, cpf_responsavel)
                )
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
                self.novo_cli_wnd.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar cliente: {str(e)}")

        #Clientes
        def rel_clientes():

            self.rel_cli_wnd = tk.Toplevel(self.root)
            self.rel_cli_wnd.title("Relátório Clientes")
            self.rel_cli_wnd.geometry("500x400")
            self.rel_cli_wnd.resizable(False, False)

            self.rel_cli_wnd.transient(self.root)
            self.rel_cli_wnd.grab_set()

            # Frame principal
            main_frame = ttk.Frame(self.rel_cli_wind, padding="10")
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
            columns = ('id', 'cnpj', 'nome', 'endereço', 'cidade', 'telefone', 'email', 'responsavel', 'cpf_responsavel')
            self.tree_clientes = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
            # Cabeçalhos
            self.tree_clientes.heading('id', text='ID')
            self.tree_clientes.heading('cnpj', text='CPF/CNPJ')
            self.tree_clientes.heading('nome', text='Nome/Razão Social')
            self.tree_clientes.heading('endereço', text='ENdereço')
            self.tree_clientes.heading('cidade', text='Cidade/UF')
            self.tree_clientes.heading('telefone', text='Telefone')
            self.tree_clientes.heading('email', text='Email')
            self.tree_clientes.heading('responsavel', text='Responsável')
            self.tree_clientes.heading('cpf_responsavel', text='CPF Responsável')
            
            # Largura das colunas
            self.tree_clientes.column('id', width=50, anchor=tk.CENTER)
            self.tree_clientes.column('cnpj', width=120, anchor=tk.W)
            self.tree_clientes.column('nome', width=250, anchor=tk.W)
            self.tree_clientes.column('endereço', width=150, anchor=tk.W)
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
            
            ttk.Button(frame_botoes, text="Editar", 
                    command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(frame_botoes, text="Excluir", 
                    command=self.excluir_cliente).pack(side=tk.LEFT, padx=5)
            
            # Carrega a lista de clientes
            self.carregar_lista_clientes()

        #Veículos
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
            resp_entry = ttk.Entry(frame, widht=40)
            resp_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

            ttk.Button(frame, text="Buscar", command=self.busc_resp).grid(row=0, column=1, sticky=tk.E, pady=5)

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

        #Barra menu cabeçalho
        menubar = tk.Menu(self.root)

        #Clientes
        menu_clientes = tk.Menu(menubar, tearoff=0)
        menu_clientes.add_command(label="Novo Cliente", command=self.novo_cliente)
        menu_clientes.add_command(label="Clientes", command=self.rel_clientes)
        menu_clientes.add_command(label="Novo Veículo", command=self.novo_veiculo)
        menu_clientes.add_command(label="Veículos", command=self.rel_veiculos)

        menubar.add_cascade(label="Clientes", menu=menu_clientes)

        #Peças
        menu_pecas = tk.Menu(menubar, tearoff=0)
        menu_pecas.add_command(label="Cadastrar Peça", command=self.nova_peca)
        menu_pecas.add_command(label="Estoque", command=self.estoque)
        menu_pecas.add_command(label="Histórico", command=self.hist_pecas)

        menubar.add_cascade(label="Peças", menu=menu_pecas)

        #Financeiro
        menu_financeiro = tk.Menu(menubar, tearoff=0)
        menu_financeiro.add_command(label="Registrar", command=self.reg_fin)
        menu_financeiro.add_command(label="Relatório", command=self.rel_fin)

        menubar.add_cascade(label="Financeiro", menu=menu_financeiro)

        #Ordem Serviço
        menu_os = tk.Menu(menubar, tearoff=0)
        menu_os.add_command(label="Nova OS", command=self.nova_os)
        menu_os.add_command(label="Relatório", command=self.relt_os)

        menubar.add_cascade(label="Ordens de Serviço", menu=menu_os)

        #Cobranças
        menu_cobr = tk.Menu(menubar, tearoff=0)
        menu_cobr.add_command(label="Registrar Cobrança", command=self.reg_cobr)
        menu_cobr.add_command(label="Relatório", command=self.relt_cobr)

        menubar.add_cascade(label="Cobranças", menu=menu_cobr)

        #Certificado Garantia
        menu_certificado = tk.Menu(menubar, tearoff=0)
        menu_certificado.add_command(label="Gerar Certificado", command=self.novo_cert)
        menu_certificado.add_command(label="Relatório", command=self.rel_cert)

        menubar.add_cascade(label="Certificado Garantia", menu=menu_certificado)

        #Recibos
        menu_recibo = tk.Menu(menubar, tearoff=0)
        menu_recibo.add_command(label="Novo Recibo", command=self.novo_recibo)
        menu_recibo.add_command(label="Relatório", command=self.rel_recibo)

        menubar.add_cascade(label="Recibos", menu=menu_recibo)

        #NFe/NFSe
        menu_NFNFS = tk.Menu(menubar, tearoff=0)
        menu_NFNFS.add_command(label="Emitir NFe", command=self.nova_NFe)
        menu_NFNFS.add_command(label="Relatório NFe", command=self.rel_NFe)
        menu_NFNFS.add_command(label="Emitir NFSe", command=self.nova_NFSe)
        menu_NFNFS.add_command(label="Relatório NFSe", command=self.rel_NFSe)

        menubar.add_cascade(label="NFe/NFSe", menu=menu_NFNFS)

        #Opções
        menu_opcoes = tk.Menu(menubar, tearoff=0)
        menu_opcoes.add_command(label="Empresa", command=self.op_empresa)
        menu_opcoes.add_command(label="Notificações", command=self.op_notif)
        menu_opcoes.add_command(label="Certificado Digital", command=self.op_cert)

        menubar.add_cascade(label="Opções", menu=menu_opcoes)

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()