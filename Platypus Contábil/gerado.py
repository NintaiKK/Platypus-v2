import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
import sqlite3
from datetime import datetime
import os
import csv
import json

class Main:
    def __init__(self, root):
        self.root = root
        self.root.title("Platypus v2 - Sistema de Gestão")
        self.root.geometry("1200x700")
        
        try:
            root.iconbitmap("none.ico")
        except:
            pass

        # Conexão com o banco
        self.conn = sqlite3.connect('platycon.db', check_same_thread=False)
        self.c = self.conn.cursor()

        # Criar tabelas
        self.criar_tabelas()

        # Variáveis de controle
        self.cliente_id = None
        self.veiculo_id = None
        self.os_id = None
        self.itens_os = []

        # Dados da empresa
        self.dados_empresa = {
            "nome": "Viana & Viana Mecânica Diesel LTDA",
            "endereco": "Rua Miguel Oresko n90",
            "cidade": "Nova Santa Rita",
            "cnpj": "61.459.722/0001-01",
            "ie": "ISENTO",
            "telefone": "51 9 9903-6427"
        }

        self.criar_widgets_principal()

    def criar_tabelas(self):
        """Cria todas as tabelas necessárias no banco de dados"""
        tabelas = [
            '''CREATE TABLE IF NOT EXISTS clientes (
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
            )''',
            '''CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resp_veiculo TEXT NOT NULL,
                placa TEXT NOT NULL,
                km TEXT,
                ano TEXT,
                modelo TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS pecas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_nf TEXT,
                cod_in TEXT NOT NULL,
                descr TEXT,
                fabric TEXT,
                cod_pec TEXT,
                vlr_cust REAL,
                vlr_venda REAL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS ordens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                cliente_id INTEGER,
                veiculo_id INTEGER,
                data_emissao TIMESTAMP,
                servico_solicitado TEXT,
                observacoes TEXT,
                valor_total REAL,
                status TEXT,
                data_fechamento TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS itens_os (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER,
                descricao TEXT,
                quantidade REAL,
                valor_unitario REAL,
                valor_total REAL,
                FOREIGN KEY (os_id) REFERENCES ordens_servico (id)
            )'''
        ]
        
        for tabela in tabelas:
            try:
                self.c.execute(tabela)
            except Exception as e:
                print(f"Erro ao criar tabela: {e}")
        
        self.conn.commit()

    def criar_widgets_principal(self):
        """Cria a interface principal"""
        # Menu principal
        menubar = tk.Menu(self.root)
        
        # Menu Clientes
        menu_clientes = tk.Menu(menubar, tearoff=0)
        menu_clientes.add_command(label="Novo Cliente", command=self.novo_cliente)
        menu_clientes.add_command(label="Gerenciar Clientes", command=self.gerenciar_clientes)
        menubar.add_cascade(label="Clientes", menu=menu_clientes)
        
        # Menu Veículos
        menu_veiculos = tk.Menu(menubar, tearoff=0)
        menu_veiculos.add_command(label="Novo Veículo", command=self.novo_veiculo)
        menu_veiculos.add_command(label="Gerenciar Veículos", command=self.gerenciar_veiculos)
        menubar.add_cascade(label="Veículos", menu=menu_veiculos)
        
        # Menu Peças
        menu_pecas = tk.Menu(menubar, tearoff=0)
        menu_pecas.add_command(label="Nova Peça", command=self.nova_peca)
        menu_pecas.add_command(label="Estoque", command=self.gerenciar_estoque)
        menubar.add_cascade(label="Peças", menu=menu_pecas)
        
        # Menu OS
        menu_os = tk.Menu(menubar, tearoff=0)
        menu_os.add_command(label="Nova OS", command=self.nova_os)
        menu_os.add_command(label="Listar OS", command=self.listar_os)
        menu_os.add_command(label="Carregar OS", command=self.carregar_os_dialog)
        menubar.add_cascade(label="Ordens de Serviço", menu=menu_os)
        
        # Menu Relatórios
        menu_relatorios = tk.Menu(menubar, tearoff=0)
        menu_relatorios.add_command(label="Relatório de OS", command=self.gerar_relatorio_os)
        menu_relatorios.add_command(label="Exportar Dados", command=self.exportar_dados)
        menubar.add_cascade(label="Relatórios", menu=menu_relatorios)
        
        self.root.config(menu=menubar)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Platypus v2 - Sistema de Gestão", 
                          font=('Arial', 18, 'bold'))
        titulo.pack(pady=20)
        
        # Subtítulo
        subtitulo = ttk.Label(main_frame, text="Sistema completo para gestão de oficina mecânica",
                             font=('Arial', 12))
        subtitulo.pack(pady=10)
        
        # Frame de botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(pady=30)
        
        # Botões principais
        botoes = [
            ("📋 Nova OS", self.nova_os),
            ("👥 Clientes", self.gerenciar_clientes),
            ("🚗 Veículos", self.gerenciar_veiculos),
            ("🔧 Estoque", self.gerenciar_estoque),
            ("📊 Relatórios", self.listar_os),
            ("💾 Backup", self.fazer_backup)
        ]
        
        for i, (texto, comando) in enumerate(botoes):
            btn = ttk.Button(botoes_frame, text=texto, command=comando, width=20)
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Sistema pronto - Banco de dados conectado")
        self.status_label.pack()

    # ===== MÉTODOS PARA CLIENTES =====
    def novo_cliente(self):
        """Abre janela para cadastrar novo cliente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Cliente")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        ttk.Label(frame, text="CPF/CNPJ:").grid(row=0, column=0, sticky=tk.W, pady=5)
        cnpj_entry = ttk.Entry(frame, width=30)
        cnpj_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Nome/Razão Social:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        nome_entry = ttk.Entry(frame, width=30)
        nome_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=5)
        endereco_entry = ttk.Entry(frame, width=30)
        endereco_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Cidade/UF:").grid(row=3, column=0, sticky=tk.W, pady=5)
        cidade_entry = ttk.Entry(frame, width=30)
        cidade_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Telefone:").grid(row=4, column=0, sticky=tk.W, pady=5)
        telefone_entry = ttk.Entry(frame, width=30)
        telefone_entry.grid(row=4, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Email:").grid(row=5, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.grid(row=5, column=1, pady=5, padx=5)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salvar", 
                  command=lambda: self.salvar_cliente(
                      cnpj_entry.get(), nome_entry.get(), endereco_entry.get(),
                      cidade_entry.get(), telefone_entry.get(), email_entry.get(),
                      dialog)
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        nome_entry.focus()

    def salvar_cliente(self, cnpj, nome, endereco, cidade, telefone, email, dialog):
        """Salva cliente no banco de dados"""
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return
        
        try:
            self.c.execute('''INSERT INTO clientes 
                           (cnpj, nome, endereco, cidade, telefone, email) 
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (cnpj, nome, endereco, cidade, telefone, email))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {e}")

    def gerenciar_clientes(self):
        """Abre gerenciador de clientes"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Gerenciar Clientes")
        dialog.geometry("800x500")
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pesquisa
        pesquisa_frame = ttk.Frame(main_frame)
        pesquisa_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pesquisa_frame, text="Pesquisar:").pack(side=tk.LEFT)
        pesquisa_entry = ttk.Entry(pesquisa_frame, width=30)
        pesquisa_entry.pack(side=tk.LEFT, padx=5)
        pesquisa_entry.bind("<KeyRelease>", lambda e: self.pesquisar_clientes(pesquisa_entry.get(), tree))
        
        ttk.Button(pesquisa_frame, text="Novo Cliente", 
                  command=self.novo_cliente).pack(side=tk.RIGHT, padx=5)
        
        # Treeview
        columns = ('ID', 'Nome', 'Telefone', 'CPF/CNPJ', 'Cidade')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column('Nome', width=200)
        tree.column('Cidade', width=150)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(botoes_frame, text="Editar", 
                  command=lambda: self.editar_cliente(tree)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Excluir", 
                  command=lambda: self.excluir_cliente(tree)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Fechar", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Carregar dados
        self.carregar_clientes(tree)

    def carregar_clientes(self, tree):
        """Carrega clientes na treeview"""
        for item in tree.get_children():
            tree.delete(item)
        
        self.c.execute("SELECT id, nome, telefone, cnpj, cidade FROM clientes ORDER BY nome")
        for cliente in self.c.fetchall():
            tree.insert('', tk.END, values=cliente)

    def pesquisar_clientes(self, filtro, tree):
        """Pesquisa clientes"""
        for item in tree.get_children():
            tree.delete(item)
        
        self.c.execute('''SELECT id, nome, telefone, cnpj, cidade FROM clientes 
                       WHERE nome LIKE ? OR cnpj LIKE ? OR telefone LIKE ? 
                       ORDER BY nome''', 
                    (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
        
        for cliente in self.c.fetchall():
            tree.insert('', tk.END, values=cliente)

    def editar_cliente(self, tree):
        """Edita cliente selecionado"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar!")
            return
        
        cliente_id = tree.item(selected[0])['values'][0]
        # Implementar edição similar ao novo_cliente, mas carregando dados existentes

    def excluir_cliente(self, tree):
        """Exclui cliente selecionado"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir!")
            return
        
        cliente_id = tree.item(selected[0])['values'][0]
        cliente_nome = tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir cliente {cliente_nome}?"):
            try:
                self.c.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
                self.conn.commit()
                self.carregar_clientes(tree)
                messagebox.showinfo("Sucesso", "Cliente excluído!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    # ===== MÉTODOS PARA VEÍCULOS =====
    def novo_veiculo(self):
        """Abre janela para cadastrar novo veículo"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Veículo")
        dialog.geometry("400x300")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Responsável:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        resp_entry = ttk.Entry(frame, width=30)
        resp_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Placa:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        placa_entry = ttk.Entry(frame, width=30)
        placa_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="KM:").grid(row=2, column=0, sticky=tk.W, pady=5)
        km_entry = ttk.Entry(frame, width=30)
        km_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Ano:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ano_entry = ttk.Entry(frame, width=30)
        ano_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Modelo:*").grid(row=4, column=0, sticky=tk.W, pady=5)
        modelo_entry = ttk.Entry(frame, width=30)
        modelo_entry.grid(row=4, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salvar",
                  command=lambda: self.salvar_veiculo(
                      resp_entry.get(), placa_entry.get(), km_entry.get(),
                      ano_entry.get(), modelo_entry.get(), dialog)
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def salvar_veiculo(self, responsavel, placa, km, ano, modelo, dialog):
        """Salva veículo no banco"""
        if not responsavel or not placa or not modelo:
            messagebox.showerror("Erro", "Campos obrigatórios: Responsável, Placa e Modelo!")
            return
        
        try:
            self.c.execute('''INSERT INTO veiculos 
                           (resp_veiculo, placa, km, ano, modelo) 
                           VALUES (?, ?, ?, ?, ?)''',
                        (responsavel, placa, km, ano, modelo))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Veículo salvo com sucesso!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar veículo: {e}")

    def gerenciar_veiculos(self):
        """Abre gerenciador de veículos"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Gerenciar Veículos")
        dialog.geometry("700x400")
        
        # Implementação similar ao gerenciar_clientes
        # ...

    # ===== MÉTODOS PARA PEÇAS =====
    def nova_peca(self):
        """Abre janela para cadastrar nova peça"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova Peça")
        dialog.geometry("400x350")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Código Interno:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        cod_in_entry = ttk.Entry(frame, width=30)
        cod_in_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Descrição:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        descr_entry = ttk.Entry(frame, width=30)
        descr_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Fabricante:").grid(row=2, column=0, sticky=tk.W, pady=5)
        fabric_entry = ttk.Entry(frame, width=30)
        fabric_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Código OEM:").grid(row=3, column=0, sticky=tk.W, pady=5)
        cod_pec_entry = ttk.Entry(frame, width=30)
        cod_pec_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Valor Custo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        vlr_cust_entry = ttk.Entry(frame, width=30)
        vlr_cust_entry.grid(row=4, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Valor Venda:").grid(row=5, column=0, sticky=tk.W, pady=5)
        vlr_venda_entry = ttk.Entry(frame, width=30)
        vlr_venda_entry.grid(row=5, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salvar",
                  command=lambda: self.salvar_peca(
                      cod_in_entry.get(), descr_entry.get(), fabric_entry.get(),
                      cod_pec_entry.get(), vlr_cust_entry.get(), vlr_venda_entry.get(), dialog)
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def salvar_peca(self, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda, dialog):
        """Salva peça no banco"""
        if not cod_in or not descr:
            messagebox.showerror("Erro", "Código Interno e Descrição são obrigatórios!")
            return
        
        try:
            custo = float(vlr_cust) if vlr_cust else 0.0
            venda = float(vlr_venda) if vlr_venda else 0.0
            
            self.c.execute('''INSERT INTO pecas 
                           (cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda) 
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (cod_in, descr, fabric, cod_pec, custo, venda))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Peça salva com sucesso!")
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Valores de custo e venda devem ser números!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar peça: {e}")

    def gerenciar_estoque(self):
        """Abre gerenciador de estoque"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Gerenciar Estoque")
        dialog.geometry("800x500")
        
        # Implementação similar ao gerenciar_clientes
        # ...

    # ===== MÉTODOS PARA ORDENS DE SERVIÇO =====
    def nova_os(self):
        """Abre janela para nova ordem de serviço"""
        self.os_window = tk.Toplevel(self.root)
        self.os_window.title("Nova Ordem de Serviço")
        self.os_window.geometry("900x700")
        
        # Variáveis da OS
        self.numero_os = tk.StringVar(value=self.gerar_numero_os())
        self.data_emissao = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.cliente_nome = tk.StringVar()
        self.cliente_veiculo = tk.StringVar()
        self.servico_solicitado = tk.StringVar()
        self.observacoes = tk.StringVar()
        self.valor_total = tk.StringVar(value="R$ 0,00")
        self.itens_os = []
        
        main_frame = ttk.Frame(self.os_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho OS
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="OS Nº:").pack(side=tk.LEFT)
        ttk.Label(header_frame, textvariable=self.numero_os, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text="Data:").pack(side=tk.LEFT, padx=(20,0))
        ttk.Label(header_frame, textvariable=self.data_emissao).pack(side=tk.LEFT, padx=5)
        
        # Cliente e Veículo
        cliente_frame = ttk.LabelFrame(main_frame, text="Cliente e Veículo", padding="10")
        cliente_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(cliente_frame, text="Selecionar Cliente", 
                  command=self.selecionar_cliente_os).pack(anchor=tk.W, pady=2)
        ttk.Label(cliente_frame, textvariable=self.cliente_nome).pack(anchor=tk.W, fill=tk.X)
        
        ttk.Button(cliente_frame, text="Selecionar Veículo", 
                  command=self.selecionar_veiculo_os).pack(anchor=tk.W, pady=2)
        ttk.Label(cliente_frame, textvariable=self.cliente_veiculo).pack(anchor=tk.W, fill=tk.X)
        
        # Serviço Solicitado
        servico_frame = ttk.LabelFrame(main_frame, text="Serviço Solicitado", padding="10")
        servico_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(servico_frame, textvariable=self.servico_solicitado, width=80).pack(fill=tk.X)
        
        # Itens da OS
        itens_frame = ttk.LabelFrame(main_frame, text="Itens da OS", padding="10")
        itens_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para itens
        columns = ('Descrição', 'Quantidade', 'Valor Unit.', 'Valor Total')
        self.tree_itens = ttk.Treeview(itens_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tree_itens.heading(col, text=col)
            self.tree_itens.column(col, width=120)
        
        self.tree_itens.column('Descrição', width=300)
        
        self.tree_itens.pack(fill=tk.BOTH, expand=True)
        
        # Controles de itens
        controles_frame = ttk.Frame(itens_frame)
        controles_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(controles_frame, text="Descrição:").pack(side=tk.LEFT)
        self.desc_item = ttk.Entry(controles_frame, width=30)
        self.desc_item.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controles_frame, text="Qtd:").pack(side=tk.LEFT)
        self.qtd_item = ttk.Entry(controles_frame, width=8)
        self.qtd_item.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controles_frame, text="Valor:").pack(side=tk.LEFT)
        self.valor_item = ttk.Entry(controles_frame, width=10)
        self.valor_item.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controles_frame, text="Adicionar", 
                  command=self.adicionar_item_os).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controles_frame, text="Remover", 
                  command=self.remover_item_os).pack(side=tk.LEFT, padx=5)
        
        # Total e Observações
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(total_frame, text="Valor Total:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(total_frame, textvariable=self.valor_total, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        obs_frame = ttk.LabelFrame(main_frame, text="Observações", padding="10")
        obs_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(obs_frame, textvariable=self.observacoes).pack(fill=tk.X)
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(botoes_frame, text="Salvar OS", 
                  command=self.salvar_os).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Imprimir OS", 
                  command=self.gerar_pdf_os).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Fechar OS", 
                  command=self.fechar_os).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Limpar", 
                  command=self.limpar_os).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Fechar", 
                  command=self.os_window.destroy).pack(side=tk.RIGHT, padx=5)

    def gerar_numero_os(self):
        """Gera número único para OS"""
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def selecionar_cliente_os(self):
        """Seleciona cliente para a OS"""
        # Implementar seleção de cliente
        self.cliente_nome.set("Cliente Exemplo Selecionado")

    def selecionar_veiculo_os(self):
        """Seleciona veículo para a OS"""
        # Implementar seleção de veículo
        self.cliente_veiculo.set("Veículo Exemplo Selecionado")

    def adicionar_item_os(self):
        """Adiciona item à OS"""
        descricao = self.desc_item.get()
        quantidade = self.qtd_item.get()
        valor = self.valor_item.get()
        
        if not descricao or not quantidade or not valor:
            messagebox.showwarning("Aviso", "Preencha todos os campos do item!")
            return
        
        try:
            qtd = float(quantidade)
            vlr = float(valor)
            total = qtd * vlr
            
            # Adiciona à lista
            item = (descricao, qtd, vlr, total)
            self.itens_os.append(item)
            
            # Adiciona à treeview
            self.tree_itens.insert('', tk.END, values=item)
            
            # Atualiza total
            self.atualizar_total_os()
            
            # Limpa campos
            self.desc_item.delete(0, tk.END)
            self.qtd_item.delete(0, tk.END)
            self.valor_item.delete(0, tk.END)
            self.desc_item.focus()
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e Valor devem ser números!")

    def remover_item_os(self):
        """Remove item selecionado da OS"""
        selected = self.tree_itens.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return
        
        for item in selected:
            index = self.tree_itens.index(item)
            self.itens_os.pop(index)
            self.tree_itens.delete(item)
        
        self.atualizar_total_os()

    def atualizar_total_os(self):
        """Atualiza valor total da OS"""
        total = sum(item[3] for item in self.itens_os)
        self.valor_total.set(f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def salvar_os(self):
        """Salva OS no banco de dados"""
        if not self.itens_os:
            messagebox.showwarning("Aviso", "Adicione itens à OS antes de salvar!")
            return
        
        try:
            total = sum(item[3] for item in self.itens_os)
            
            self.c.execute('''INSERT INTO ordens_servico 
                           (numero, data_emissao, servico_solicitado, observacoes, valor_total, status) 
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (self.numero_os.get(), datetime.now(), self.servico_solicitado.get(),
                         self.observacoes.get(), total, 'Aberta'))
            
            os_id = self.c.lastrowid
            
            # Salva itens
            for item in self.itens_os:
                self.c.execute('''INSERT INTO itens_os 
                               (os_id, descricao, quantidade, valor_unitario, valor_total) 
                               VALUES (?, ?, ?, ?, ?)''',
                            (os_id, item[0], item[1], item[2], item[3]))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "OS salva com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar OS: {e}")

    def gerar_pdf_os(self):
        """Gera PDF da OS"""
        if not self.itens_os:
            messagebox.showwarning("Aviso", "Não há itens para gerar PDF!")
            return
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, self.dados_empresa["nome"], 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, self.dados_empresa["endereco"] + " - " + self.dados_empresa["cidade"], 0, 1, 'C')
            pdf.cell(0, 5, f"CNPJ: {self.dados_empresa['cnpj']} - Tel: {self.dados_empresa['telefone']}", 0, 1, 'C')
            
            pdf.ln(10)
            
            # Dados da OS
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f"ORDEM DE SERVIÇO Nº {self.numero_os.get()}", 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"Data: {self.data_emissao.get()}", 0, 1)
            
            # Cliente
            if self.cliente_nome.get():
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "CLIENTE:", 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 5, self.cliente_nome.get(), 0, 1)
            
            # Serviço
            if self.servico_solicitado.get():
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "SERVIÇO SOLICITADO:", 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 5, self.servico_solicitado.get())
            
            # Itens
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "ITENS:", 0, 1)
            
            # Cabeçalho da tabela
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(120, 8, "Descrição", 1, 0)
            pdf.cell(20, 8, "Qtd", 1, 0, 'C')
            pdf.cell(25, 8, "Vl. Unit.", 1, 0, 'R')
            pdf.cell(25, 8, "Vl. Total", 1, 1, 'R')
            
            # Itens
            pdf.set_font('Arial', '', 9)
            total = 0
            for item in self.itens_os:
                pdf.cell(120, 8, item[0], 1, 0)
                pdf.cell(20, 8, str(item[1]), 1, 0, 'C')
                pdf.cell(25, 8, f"R$ {item[2]:.2f}", 1, 0, 'R')
                pdf.cell(25, 8, f"R$ {item[3]:.2f}", 1, 1, 'R')
                total += item[3]
            
            # Total
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(165, 8, "TOTAL:", 1, 0, 'R')
            pdf.cell(25, 8, f"R$ {total:.2f}", 1, 1, 'R')
            
            # Observações
            if self.observacoes.get():
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 10, "Observações:", 0, 1)
                pdf.set_font('Arial', '', 9)
                pdf.multi_cell(0, 5, self.observacoes.get())
            
            # Salva o arquivo
            os.makedirs("ordens_servico", exist_ok=True)
            filename = f"ordens_servico/OS_{self.numero_os.get()}.pdf"
            pdf.output(filename)
            
            messagebox.showinfo("Sucesso", f"PDF gerado: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")

    def fechar_os(self):
        """Fecha a OS"""
        if messagebox.askyesno("Confirmar", "Fechar esta Ordem de Serviço?"):
            messagebox.showinfo("Sucesso", "OS fechada com sucesso!")

    def limpar_os(self):
        """Limpa os dados da OS atual"""
        if messagebox.askyesno("Confirmar", "Limpar todos os dados da OS?"):
            self.itens_os.clear()
            self.tree_itens.delete(*self.tree_itens.get_children())
            self.servico_solicitado.set("")
            self.observacoes.set("")
            self.valor_total.set("R$ 0,00")

    def listar_os(self):
        """Lista todas as ordens de serviço"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Lista de Ordens de Serviço")
        dialog.geometry("1000x500")
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        filtro_frame = ttk.Frame(main_frame)
        filtro_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filtro_frame, text="Data Início:").pack(side=tk.LEFT)
        data_inicio = ttk.Entry(filtro_frame, width=12)
        data_inicio.pack(side=tk.LEFT, padx=5)
        data_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Label(filtro_frame, text="Data Fim:").pack(side=tk.LEFT, padx=(10,0))
        data_fim = ttk.Entry(filtro_frame, width=12)
        data_fim.pack(side=tk.LEFT, padx=5)
        data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Button(filtro_frame, text="Filtrar").pack(side=tk.LEFT, padx=10)
        
        # Treeview
        columns = ('ID', 'Número', 'Cliente', 'Data', 'Valor', 'Status')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        tree.column('Cliente', width=200)
        tree.column('Data', width=100)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(botoes_frame, text="Carregar OS", 
                  command=lambda: self.carregar_os_selecionada(tree)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Imprimir Relatório", 
                  command=lambda: self.gerar_relatorio_os(tree)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Fechar", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Carregar dados
        self.carregar_os_treeview(tree)

    def carregar_os_treeview(self, tree):
        """Carrega OS na treeview"""
        for item in tree.get_children():
            tree.delete(item)
        
        self.c.execute('''SELECT id, numero, 
                         (SELECT nome FROM clientes WHERE id = cliente_id) as cliente,
                         data_emissao, valor_total, status 
                         FROM ordens_servico ORDER BY id DESC''')
        
        for os_data in self.c.fetchall():
            valor_formatado = f"R$ {os_data[4]:.2f}" if os_data[4] else "R$ 0,00"
            tree.insert('', tk.END, values=(
                os_data[0], os_data[1], os_data[2] or "N/A",
                os_data[3][:10] if os_data[3] else "", valor_formatado, os_data[5]
            ))

    def carregar_os_selecionada(self, tree):
        """Carrega OS selecionada para edição"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma OS!")
            return
        
        os_id = tree.item(selected[0])['values'][0]
        # Implementar carregamento completo da OS

    def carregar_os_dialog(self):
        """Diálogo para carregar OS existente"""
        # Implementação similar ao listar_os, mas com foco em carregar uma OS específica
        self.listar_os()

    def gerar_relatorio_os(self, tree):
        """Gera relatório das OS selecionadas"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma OS!")
            return
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, "RELATÓRIO DE ORDENS DE SERVIÇO", 0, 1, 'C')
            pdf.cell(0, 10, self.dados_empresa["nome"], 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'C')
            
            pdf.ln(10)
            
            # Tabela
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(20, 8, "OS", 1, 0, 'C')
            pdf.cell(80, 8, "Cliente", 1, 0)
            pdf.cell(30, 8, "Data", 1, 0, 'C')
            pdf.cell(30, 8, "Valor", 1, 0, 'R')
            pdf.cell(30, 8, "Status", 1, 1, 'C')
            
            pdf.set_font('Arial', '', 9)
            total_geral = 0
            
            for item in selected:
                os_data = tree.item(item)['values']
                pdf.cell(20, 8, os_data[1], 1, 0, 'C')
                pdf.cell(80, 8, os_data[2], 1, 0)
                pdf.cell(30, 8, os_data[3], 1, 0, 'C')
                pdf.cell(30, 8, os_data[4], 1, 0, 'R')
                pdf.cell(30, 8, os_data[5], 1, 1, 'C')
                
                # Soma o valor (remove formatação)
                valor = float(os_data[4].replace("R$", "").replace(".", "").replace(",", ".").strip())
                total_geral += valor
            
            # Total
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(160, 8, "TOTAL GERAL:", 1, 0, 'R')
            pdf.cell(30, 8, f"R$ {total_geral:.2f}", 1, 1, 'R')
            
            # Salva
            os.makedirs("relatorios", exist_ok=True)
            filename = f"relatorios/Relatorio_OS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")

    # ===== MÉTODOS UTILITÁRIOS =====
    def exportar_dados(self):
        """Exporta dados para CSV"""
        try:
            tabelas = ['clientes', 'veiculos', 'pecas', 'ordens_servico']
            
            for tabela in tabelas:
                self.c.execute(f"SELECT * FROM {tabela}")
                dados = self.c.fetchall()
                colunas = [desc[0] for desc in self.c.description]
                
                filename = f"export_{tabela}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(colunas)
                    writer.writerows(dados)
            
            messagebox.showinfo("Sucesso", "Dados exportados com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {e}")

    def fazer_backup(self):
        """Faz backup do banco de dados"""
        try:
            backup_file = f"backup_platycon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Fecha e recria conexão para garantir que não há locks
            self.conn.close()
            
            import shutil
            shutil.copy2('platycon.db', backup_file)
            
            # Reabre conexão
            self.conn = sqlite3.connect('platycon.db', check_same_thread=False)
            self.c = self.conn.cursor()
            
            messagebox.showinfo("Sucesso", f"Backup criado: {backup_file}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer backup: {e}")

    def __del__(self):
        """Destrutor - fecha conexão com o banco"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    
    # Configurar fechamento adequado
    root.protocol("WM_DELETE_WINDOW", lambda: (app.conn.close() if hasattr(app, 'conn') else None, root.destroy()))
    
    root.mainloop()