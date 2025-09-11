import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
import os
from fpdf import FPDF

class SistemaFinanceiro:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Financeiro Completo v3.0 (SQLite)")
        self.root.geometry("1200x750")
        
        # Configuração de ícone
        try:
            root.iconbitmap("financeiro.ico")
        except:
            pass
        
        # Banco de dados
        self.db_name = "financeiro.db"
        
        # Inicialização
        self.inicializar_banco_dados()
        self.criar_variaveis()
        self.criar_interface()
        self.carregar_dados()

    def inicializar_banco_dados(self):
        """Cria o banco de dados e tabelas se não existirem"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabela de clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT
        )
        """)
        
        # Tabela de contas a receber
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_vencimento TEXT NOT NULL,
            status TEXT NOT NULL,
            data_pagamento TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        )
        """)
        
        # Tabela de contas a pagar
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            fornecedor TEXT,
            valor REAL NOT NULL,
            data_vencimento TEXT NOT NULL,
            status TEXT NOT NULL,
            data_pagamento TEXT,
            categoria TEXT NOT NULL
        )
        """)
        
        conn.commit()
        conn.close()

    def criar_variaveis(self):
        """Cria todas as variáveis de controle"""
        # Variáveis para clientes
        self.var_cliente = {
            'id': StringVar(),
            'nome': StringVar(),
            'telefone': StringVar(),
            'email': StringVar()
        }
        
        # Variáveis para contas a receber
        self.var_receber = {
            'id': StringVar(),
            'descricao': StringVar(),
            'valor': StringVar(),
            'vencimento': StringVar(),
            'status': StringVar(value="Pendente"),
            'pagamento': StringVar()
        }
        
        # Variáveis para contas a pagar
        self.var_pagar = {
            'id': StringVar(),
            'descricao': StringVar(),
            'fornecedor': StringVar(),
            'valor': StringVar(),
            'vencimento': StringVar(),
            'status': StringVar(value="Pendente"),
            'pagamento': StringVar(),
            'categoria': StringVar(value="Outros")
        }
        
        # Variáveis para filtros
        self.filtros = {
            'status': StringVar(value="TODOS"),
            'status_pagar': StringVar(value="TODOS"),
            'status_todas_receber': StringVar(value="TODOS")
        }
        
        # Dados e seleções
        self.clientes = []
        self.contas_receber = []
        self.contas_pagar = []
        self.todas_contas_receber = []
        self.cliente_selecionado = None
        self.conta_receber_selecionada = None
        self.conta_pagar_selecionada = None

    def criar_interface(self):
        """Cria toda a interface gráfica"""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Treeview', rowheight=25)
        style.map('Treeview', background=[('selected', '#0078d7')])

        # Notebook (Abas)
        self.notebook = ttk.Notebook(self.root)
        
        # Abas do sistema
        self.criar_aba_clientes()
        self.criar_aba_receber()
        self.criar_aba_pagar()
        self.criar_aba_todas_receber()
        
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # ========== ABA CLIENTES ==========
    def criar_aba_clientes(self):
        """Cria a aba de cadastro de clientes"""
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Clientes")
        
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(aba, text="Cadastro de Cliente", padding=10)
        frame_cadastro.pack(fill=X, padx=5, pady=5)
        
        # Formulário
        campos = [
            ("ID:", "id", True),
            ("Nome*:", "nome", False),
            ("Telefone:", "telefone", False),
            ("Email:", "email", False)
        ]
        
        for i, (label, var, readonly) in enumerate(campos):
            ttk.Label(frame_cadastro, text=label).grid(row=i, column=0, sticky=W, pady=2)
            state = "readonly" if readonly else "normal"
            ttk.Entry(frame_cadastro, textvariable=self.var_cliente[var], state=state).grid(row=i, column=1, sticky=EW, pady=2)
        
        # Botões
        botoes = [
            ("Novo", self.novo_cliente),
            ("Salvar", self.salvar_cliente),
            ("Excluir", self.excluir_cliente),
            ("Limpar", self.limpar_cliente),
            ("Selecionar", self.confirmar_selecao_cliente)
        ]
        
        frame_botoes = ttk.Frame(frame_cadastro)
        frame_botoes.grid(row=len(campos), column=0, columnspan=2, pady=10)
        
        for i, (texto, comando) in enumerate(botoes):
            ttk.Button(frame_botoes, text=texto, command=comando).pack(side=LEFT, padx=5)
        
        # Listagem
        frame_lista = ttk.Frame(aba)
        frame_lista.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        colunas = [
            ("ID", 50),
            ("Nome", 250),
            ("Telefone", 150),
            ("Email", 300)
        ]
        
        self.tree_clientes = ttk.Treeview(frame_lista, columns=[c[0] for c in colunas], show="headings")
        for col, width in colunas:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=width)
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame_lista, orient=VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.tree_clientes.pack(fill=BOTH, expand=True)
        
        # Eventos
        self.tree_clientes.bind("<ButtonRelease-1>", self.selecionar_cliente)

    def confirmar_selecao_cliente(self):
        """Confirma a seleção do cliente e atualiza a aba de contas a receber"""
        if not hasattr(self, 'cliente_selecionado') or not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Nenhum cliente selecionado!")
            return
        
        # Atualiza as labels na aba de contas a receber
        self.labels_cliente['nome'].config(text=self.cliente_selecionado['nome'])
        self.labels_cliente['telefone'].config(text=self.cliente_selecionado['telefone'])
        self.labels_cliente['email'].config(text=self.cliente_selecionado['email'])
        
        messagebox.showinfo("Sucesso", f"Cliente {self.cliente_selecionado['nome']} selecionado!")
        self.carregar_contas_receber()
        self.notebook.select(1)  # Vai para a aba de contas a receber

    def selecionar_cliente(self, event):
        """Seleciona um cliente da lista"""
        item_selecionado = self.tree_clientes.selection()
        
        if not item_selecionado:
            self.cliente_selecionado = None
            return
        
        try:
            item = self.tree_clientes.item(item_selecionado[0])
            valores = item['values']
            
            if not valores:
                return
                
            # Atualiza o cliente selecionado
            self.cliente_selecionado = {
                'id': valores[0],
                'nome': valores[1],
                'telefone': valores[2] if len(valores) > 2 else "",
                'email': valores[3] if len(valores) > 3 else ""
            }
            
            # Atualiza os campos do formulário
            for i, campo in enumerate(['id', 'nome', 'telefone', 'email']):
                if i < len(valores):
                    self.var_cliente[campo].set(valores[i])
                else:
                    self.var_cliente[campo].set("")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao selecionar cliente:\n{str(e)}")
            self.cliente_selecionado = None

    def carregar_clientes(self):
        """Carrega os clientes do banco de dados"""
        self.clientes = []
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nome, telefone, email FROM clientes ORDER BY nome")
            rows = cursor.fetchall()
            
            for row in rows:
                self.clientes.append({
                    'id': row[0],
                    'nome': row[1],
                    'telefone': row[2],
                    'email': row[3]
                })
                self.tree_clientes.insert("", END, values=row)
            
            conn.close()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar clientes:\n{str(e)}")
    
    def novo_cliente(self):
        """Prepara o formulário para um novo cliente"""
        self.limpar_cliente()
        self.var_cliente['id'].set("Novo")
        self.cliente_selecionado = None
        self.tree_clientes.selection_remove(self.tree_clientes.selection())
    
    def salvar_cliente(self):
        """Salva o cliente no banco de dados"""
        # Validação
        if not self.var_cliente['nome'].get():
            messagebox.showerror("Erro", "O campo Nome é obrigatório!")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            dados = {
                'nome': self.var_cliente['nome'].get(),
                'telefone': self.var_cliente['telefone'].get(),
                'email': self.var_cliente['email'].get()
            }
            
            if self.var_cliente['id'].get() in ("Novo", ""):
                # Inserir novo cliente
                cursor.execute("""
                INSERT INTO clientes (nome, telefone, email)
                VALUES (:nome, :telefone, :email)
                """, dados)
                conn.commit()
                messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            else:
                # Atualizar cliente existente
                dados['id'] = self.var_cliente['id'].get()
                cursor.execute("""
                UPDATE clientes 
                SET nome = :nome, telefone = :telefone, email = :email
                WHERE id = :id
                """, dados)
                conn.commit()
                messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            
            conn.close()
            self.carregar_clientes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar cliente:\n{str(e)}")
    
    def excluir_cliente(self):
        """Exclui o cliente selecionado"""
        if not self.var_cliente['id'].get() or self.var_cliente['id'].get() == "Novo":
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir!")
            return
        
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este cliente e todas as suas contas a receber?")
        if not resposta:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Excluir contas a receber do cliente primeiro
            cursor.execute("DELETE FROM contas_receber WHERE id_cliente = ?", (self.var_cliente['id'].get(),))
            
            # Excluir o cliente
            cursor.execute("DELETE FROM clientes WHERE id = ?", (self.var_cliente['id'].get(),))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Cliente e contas associadas excluídos com sucesso!")
            self.limpar_cliente()
            self.carregar_clientes()
            self.carregar_contas_receber()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir cliente:\n{str(e)}")
    
    def limpar_cliente(self):
        """Limpa o formulário de cliente"""
        for var in self.var_cliente.values():
            var.set("")
        self.cliente_selecionado = None

    # ========== ABA CONTAS A RECEBER ==========
    def criar_aba_receber(self):
        """Cria a aba de contas a receber"""
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Contas a Receber")
        
        # Frame superior (informações + filtros)
        frame_superior = ttk.Frame(aba)
        frame_superior.pack(fill=X, padx=5, pady=5)
        
        # Informações do cliente selecionado
        frame_info = ttk.LabelFrame(frame_superior, text="Cliente Selecionado", padding=10)
        frame_info.pack(side=LEFT, fill=X, expand=True)
        
        self.labels_cliente = {
            'nome': ttk.Label(frame_info, text="Nenhum cliente selecionado", font=('Arial', 10, 'bold')),
            'telefone': ttk.Label(frame_info, text=""),
            'email': ttk.Label(frame_info, text="")
        }
        
        ttk.Label(frame_info, text="Nome:").grid(row=0, column=0, sticky=W)
        self.labels_cliente['nome'].grid(row=0, column=1, sticky=W)
        
        ttk.Label(frame_info, text="Telefone:").grid(row=1, column=0, sticky=W)
        self.labels_cliente['telefone'].grid(row=1, column=1, sticky=W)
        
        ttk.Label(frame_info, text="Email:").grid(row=2, column=0, sticky=W)
        self.labels_cliente['email'].grid(row=2, column=1, sticky=W)
        
        # Filtros
        frame_filtros = ttk.LabelFrame(frame_superior, text="Filtros", padding=10)
        frame_filtros.pack(side=RIGHT, fill=X)
        
        ttk.Label(frame_filtros, text="Status:").grid(row=0, column=0, sticky=W)
        ttk.Combobox(frame_filtros, textvariable=self.filtros['status'], 
                     values=["TODOS", "Pendente", "Paga", "Atrasada"], width=10).grid(row=0, column=1, sticky=W)
        
        ttk.Button(frame_filtros, text="Aplicar", command=self.carregar_contas_receber).grid(row=0, column=2, padx=5)
        ttk.Button(frame_filtros, text="Gerar PDF", command=self.gerar_relatorio_receber).grid(row=0, column=3, padx=5)
        
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(aba, text="Cadastro de Conta", padding=10)
        frame_cadastro.pack(fill=X, padx=5, pady=5)
        
        # Formulário
        campos = [
            ("ID:", "id", True),
            ("Descrição*:", "descricao", False),
            ("Valor*:", "valor", False),
            ("Vencimento* (dd/mm/aaaa):", "vencimento", False),
            ("Status:", "status", True),
            ("Data Pagamento:", "pagamento", False)
        ]
        
        for i, (label, var, readonly) in enumerate(campos):
            ttk.Label(frame_cadastro, text=label).grid(row=i, column=0, sticky=W, pady=2)
            if var == "status":
                ttk.Combobox(frame_cadastro, textvariable=self.var_receber[var],
                           values=["Pendente", "Paga", "Atrasada"], state="readonly").grid(row=i, column=1, sticky=EW, pady=2)
            else:
                state = "readonly" if readonly else "normal"
                ttk.Entry(frame_cadastro, textvariable=self.var_receber[var], state=state).grid(row=i, column=1, sticky=EW, pady=2)
        
        # Botões
        botoes = [
            ("Nova", self.nova_conta_receber),
            ("Salvar", self.salvar_conta_receber),
            ("Excluir", self.excluir_conta_receber),
            ("Limpar", self.limpar_conta_receber),
            ("Marcar como Paga", self.marcar_conta_recebida)
        ]
        
        frame_botoes = ttk.Frame(frame_cadastro)
        frame_botoes.grid(row=len(campos), column=0, columnspan=2, pady=10)
        
        for i, (texto, comando) in enumerate(botoes):
            ttk.Button(frame_botoes, text=texto, command=comando).pack(side=LEFT, padx=5)
        
        # Listagem
        frame_lista = ttk.Frame(aba)
        frame_lista.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        colunas = [
            ("ID", 50),
            ("Descrição", 250),
            ("Valor", 100),
            ("Vencimento", 100),
            ("Status", 100),
            ("Pagamento", 100)
        ]
        
        self.tree_receber = ttk.Treeview(frame_lista, columns=[c[0] for c in colunas], show="headings")
        for col, width in colunas:
            self.tree_receber.heading(col, text=col)
            self.tree_receber.column(col, width=width)
        
        # Configurar tags para cores
        self.tree_receber.tag_configure('Pendente', foreground='black')
        self.tree_receber.tag_configure('Paga', foreground='green')
        self.tree_receber.tag_configure('Atrasada', foreground='red')
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame_lista, orient=VERTICAL, command=self.tree_receber.yview)
        self.tree_receber.configure(yscroll=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.tree_receber.pack(fill=BOTH, expand=True)
        
        # Eventos
        self.tree_receber.bind("<<TreeviewSelect>>", self.selecionar_conta_receber)

    def nova_conta_receber(self):
        """Prepara o formulário para uma nova conta a receber"""
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro!")
            self.notebook.select(0)  # Vai para a aba de clientes
            return
        
        self.limpar_conta_receber()
        self.var_receber['id'].set("Novo")
    
    def salvar_conta_receber(self):
        """Salva a conta a receber no banco de dados"""
        # Verificação reforçada do cliente selecionado
        if not hasattr(self, 'cliente_selecionado') or not self.cliente_selecionado:
            messagebox.showerror("Erro", "Nenhum cliente selecionado! Selecione um cliente na aba de Clientes.")
            self.notebook.select(0)
            return
        
        # Validação
        campos_obrigatorios = ['descricao', 'valor', 'vencimento']
        for campo in campos_obrigatorios:
            if not self.var_receber[campo].get():
                messagebox.showerror("Erro", f"O campo {campo.replace('_', ' ').title()} é obrigatório!")
                return
        
        try:
            # Converter valor para float
            valor = float(self.var_receber['valor'].get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido! Use números com ponto ou vírgula decimal.")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            dados = {
                'id_cliente': self.cliente_selecionado['id'],
                'descricao': self.var_receber['descricao'].get(),
                'valor': valor,
                'data_vencimento': self.var_receber['vencimento'].get(),
                'status': self.var_receber['status'].get(),
                'data_pagamento': self.var_receber['pagamento'].get() if self.var_receber['pagamento'].get() else None
            }
            
            if self.var_receber['id'].get() in ("Novo", ""):
                # Inserir nova conta
                cursor.execute("""
                INSERT INTO contas_receber (id_cliente, descricao, valor, data_vencimento, status, data_pagamento)
                VALUES (:id_cliente, :descricao, :valor, :data_vencimento, :status, :data_pagamento)
                """, dados)
                conn.commit()
                messagebox.showinfo("Sucesso", "Conta cadastrada com sucesso!")
            else:
                # Atualizar conta existente
                dados['id'] = self.var_receber['id'].get()
                cursor.execute("""
                UPDATE contas_receber 
                SET descricao = :descricao, valor = :valor, data_vencimento = :data_vencimento, 
                    status = :status, data_pagamento = :data_pagamento
                WHERE id = :id
                """, dados)
                conn.commit()
                messagebox.showinfo("Sucesso", "Conta atualizada com sucesso!")
            
            conn.close()
            self.carregar_contas_receber()
            self.carregar_todas_contas_receber()  # Atualiza a aba de todas as contas
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar conta:\n{str(e)}")
    
    def carregar_contas_receber(self):
        """Carrega as contas a receber do cliente selecionado"""
        self.contas_receber = []
        for item in self.tree_receber.get_children():
            self.tree_receber.delete(item)
        
        if not self.cliente_selecionado:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Construir a query com filtro
            query = "SELECT id, descricao, valor, data_vencimento, status, data_pagamento FROM contas_receber WHERE id_cliente = ?"
            params = [self.cliente_selecionado['id']]
            
            status_filtro = self.filtros['status'].get()
            if status_filtro != "TODOS":
                query += " AND status = ?"
                params.append(status_filtro)
            
            query += " ORDER BY data_vencimento"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            total_pendente = 0
            total_pago = 0
            
            for row in rows:
                conta = {
                    'id': row[0],
                    'descricao': row[1],
                    'valor': row[2],
                    'vencimento': row[3],
                    'status': row[4],
                    'pagamento': row[5]
                }
                
                self.contas_receber.append(conta)
                
                # Calcular totais
                if conta['status'] == "Paga":
                    total_pago += conta['valor']
                else:
                    total_pendente += conta['valor']
                
                # Adicionar à treeview
                self.tree_receber.insert("", END, values=(
                    conta['id'],
                    conta['descricao'],
                    f"R$ {conta['valor']:.2f}",
                    conta['vencimento'],
                    conta['status'],
                    conta['pagamento'] if conta['pagamento'] else "-"
                ), tags=(conta['status'],))
            
            # Adicionar totais
            self.tree_receber.insert("", END, values=("", "", "", "", "TOTAL PENDENTE:", f"R$ {total_pendente:.2f}"), tags=('Pendente',))
            self.tree_receber.insert("", END, values=("", "", "", "", "TOTAL PAGO:", f"R$ {total_pago:.2f}"), tags=('Paga',))
            self.tree_receber.insert("", END, values=("", "", "", "", "SALDO:", f"R$ {(total_pago - total_pendente):.2f}"))
            
            conn.close()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar contas:\n{str(e)}")
    
    def selecionar_conta_receber(self, event):
        """Seleciona uma conta a receber da lista"""
        item = self.tree_receber.selection()
        if not item:
            return
        
        valores = self.tree_receber.item(item[0], 'values')
        if valores and valores[0]:  # Ignorar linhas de total
            campos = ['id', 'descricao', 'valor', 'vencimento', 'status', 'pagamento']
            for i, campo in enumerate(campos):
                if campo == 'valor' and i < len(valores):
                    # Remove "R$ " do valor para armazenar
                    valor = valores[i].replace("R$ ", "").strip()
                    self.var_receber[campo].set(valor)
                elif i < len(valores):
                    self.var_receber[campo].set(valores[i])
            
            # Armazena a conta selecionada
            self.conta_receber_selecionada = {
                'id': valores[0],
                'descricao': valores[1],
                'valor': float(valores[2].replace("R$ ", "").replace(".", "").replace(",", ".")),
                'vencimento': valores[3],
                'status': valores[4],
                'pagamento': valores[5] if len(valores) > 5 else ""
            }
    
    def excluir_conta_receber(self):
        """Exclui a conta a receber selecionada"""
        if not self.conta_receber_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma conta para excluir!")
            return
        
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta conta?")
        if not resposta:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM contas_receber WHERE id = ?", (self.conta_receber_selecionada['id'],))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
            self.limpar_conta_receber()
            self.carregar_contas_receber()
            self.carregar_todas_contas_receber()  # Atualiza a aba de todas as contas
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir conta:\n{str(e)}")
    
    def limpar_conta_receber(self):
        """Limpa o formulário de contas a receber"""
        for var in self.var_receber.values():
            var.set("")
        self.var_receber['status'].set("Pendente")
        self.conta_receber_selecionada = None
    
    def marcar_conta_recebida(self):
        """Marca a conta como recebida"""
        if not self.conta_receber_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma conta para marcar como paga!")
            return
        
        self.var_receber['status'].set("Paga")
        self.var_receber['pagamento'].set(datetime.now().strftime("%d/%m/%Y"))
        self.salvar_conta_receber()
    
    def gerar_relatorio_receber(self):
        """Gera relatório em PDF das contas a receber"""
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro!")
            return
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Cabeçalho
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Relatório de Contas a Receber", 0, 1, 'C')
            pdf.ln(5)
            
            # Informações do Cliente
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Cliente: {self.cliente_selecionado['nome']}", 0, 1)
            pdf.cell(0, 10, f"Telefone: {self.cliente_selecionado['telefone']}", 0, 1)
            pdf.cell(0, 10, f"Email: {self.cliente_selecionado['email']}", 0, 1)
            pdf.ln(5)
            
            # Filtros aplicados
            if self.filtros['status'].get() != "TODOS":
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, f"Filtro: Status = {self.filtros['status'].get()}", 0, 1)
                pdf.ln(3)
            
            # Tabela
            pdf.set_font("Arial", 'B', 10)
            colunas = [
                ("Descrição", 70),
                ("Valor", 30),
                ("Vencimento", 30),
                ("Status", 25),
                ("Pagamento", 30)
            ]
            
            for col, width in colunas:
                pdf.cell(width, 10, col, border=1)
            pdf.ln()
            
            # Dados
            pdf.set_font("Arial", size=10)
            total_pendente = 0
            total_pago = 0
            
            for conta in self.contas_receber:
                valor = conta['valor']
                if conta['status'] == "Paga":
                    total_pago += valor
                else:
                    total_pendente += valor
                
                pdf.cell(70, 10, conta['descricao'][:50], border=1)
                pdf.cell(30, 10, f"R$ {valor:.2f}", border=1)
                pdf.cell(30, 10, conta['vencimento'], border=1)
                pdf.cell(25, 10, conta['status'], border=1)
                pdf.cell(30, 10, conta['pagamento'] if conta['pagamento'] else "-", border=1)
                pdf.ln()
            
            # Totais
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(135, 10, "TOTAL PENDENTE:", border=1)
            pdf.cell(30, 10, f"R$ {total_pendente:.2f}", border=1, ln=1)
            pdf.cell(135, 10, "TOTAL PAGO:", border=1)
            pdf.cell(30, 10, f"R$ {total_pago:.2f}", border=1, ln=1)
            pdf.cell(135, 10, "SALDO:", border=1)
            saldo = total_pago - total_pendente
            pdf.cell(30, 10, f"R$ {saldo:.2f}", border=1, ln=1)
            
            # Rodapé
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 10, f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0, 'C')
            
            # Salvar arquivo
            nome_arquivo = f"relatorio_receber_{self.cliente_selecionado['nome']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(nome_arquivo)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nArquivo: {nome_arquivo}")
            
            # Tentar abrir o PDF automaticamente
            try:
                os.startfile(nome_arquivo)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório:\n{str(e)}")

    # ========== ABA CONTAS A PAGAR ==========
    def criar_aba_pagar(self):
        """Cria a aba de contas a pagar"""
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Contas a Pagar")
        
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(aba, text="Filtros", padding=10)
        frame_filtros.pack(fill=X, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Status:").grid(row=0, column=0, sticky=W)
        ttk.Combobox(frame_filtros, textvariable=self.filtros['status_pagar'], 
                    values=["TODOS", "Pendente", "Paga", "Atrasada"], width=10).grid(row=0, column=1, sticky=W)
        
        ttk.Button(frame_filtros, text="Aplicar", command=self.carregar_contas_pagar).grid(row=0, column=2, padx=5)
        ttk.Button(frame_filtros, text="Gerar PDF", command=self.gerar_relatorio_pagar).grid(row=0, column=3, padx=5)
        
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(aba, text="Cadastro de Conta", padding=10)
        frame_cadastro.pack(fill=X, padx=5, pady=5)
        
        # Formulário
        campos = [
            ("ID:", "id", True),
            ("Descrição*:", "descricao", False),
            ("Fornecedor:", "fornecedor", False),
            ("Valor*:", "valor", False),
            ("Vencimento* (dd/mm/aaaa):", "vencimento", False),
            ("Status:", "status", True),
            ("Data Pagamento:", "pagamento", False),
            ("Categoria:", "categoria", True)
        ]
        
        for i, (label, var, readonly) in enumerate(campos):
            ttk.Label(frame_cadastro, text=label).grid(row=i, column=0, sticky=W, pady=2)
            if var == "status":
                ttk.Combobox(frame_cadastro, textvariable=self.var_pagar[var],
                           values=["Pendente", "Paga", "Atrasada"], state="readonly").grid(row=i, column=1, sticky=EW, pady=2)
            elif var == "categoria":
                ttk.Combobox(frame_cadastro, textvariable=self.var_pagar[var],
                           values=["Aluguel", "Energia", "Água", "Internet", "Salários", "Matéria-prima", "Outros"]).grid(row=i, column=1, sticky=EW, pady=2)
            else:
                state = "readonly" if readonly else "normal"
                ttk.Entry(frame_cadastro, textvariable=self.var_pagar[var], state=state).grid(row=i, column=1, sticky=EW, pady=2)
        
        # Botões
        botoes = [
            ("Nova", self.nova_conta_pagar),
            ("Salvar", self.salvar_conta_pagar),
            ("Excluir", self.excluir_conta_pagar),
            ("Limpar", self.limpar_conta_pagar),
            ("Marcar como Paga", self.marcar_conta_paga)
        ]
        
        frame_botoes = ttk.Frame(frame_cadastro)
        frame_botoes.grid(row=len(campos), column=0, columnspan=2, pady=10)
        
        for i, (texto, comando) in enumerate(botoes):
            ttk.Button(frame_botoes, text=texto, command=comando).pack(side=LEFT, padx=5)
        
        # Listagem
        frame_lista = ttk.Frame(aba)
        frame_lista.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        colunas = [
            ("ID", 50),
            ("Descrição", 200),
            ("Fornecedor", 150),
            ("Valor", 100),
            ("Vencimento", 100),
            ("Status", 100),
            ("Pagamento", 100),
            ("Categoria", 100)
        ]
        
        self.tree_pagar = ttk.Treeview(frame_lista, columns=[c[0] for c in colunas], show="headings")
        for col, width in colunas:
            self.tree_pagar.heading(col, text=col)
            self.tree_pagar.column(col, width=width)
        
        # Configurar tags para cores
        self.tree_pagar.tag_configure('Pendente', foreground='black')
        self.tree_pagar.tag_configure('Paga', foreground='green')
        self.tree_pagar.tag_configure('Atrasada', foreground='red')
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame_lista, orient=VERTICAL, command=self.tree_pagar.yview)
        self.tree_pagar.configure(yscroll=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.tree_pagar.pack(fill=BOTH, expand=True)
        
        # Eventos
        self.tree_pagar.bind("<<TreeviewSelect>>", self.selecionar_conta_pagar)

    def nova_conta_pagar(self):
        """Prepara o formulário para uma nova conta a pagar"""
        self.limpar_conta_pagar()
        self.var_pagar['id'].set("Novo")
    
    def salvar_conta_pagar(self):
        """Salva a conta a pagar no banco de dados"""
        # Validação
        campos_obrigatorios = ['descricao', 'valor', 'vencimento']
        for campo in campos_obrigatorios:
            if not self.var_pagar[campo].get():
                messagebox.showerror("Erro", f"O campo {campo.replace('_', ' ').title()} é obrigatório!")
                return
        
        try:
            # Converter valor para float
            valor = float(self.var_pagar['valor'].get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido! Use números com ponto ou vírgula decimal.")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            dados = {
                'descricao': self.var_pagar['descricao'].get(),
                'fornecedor': self.var_pagar['fornecedor'].get(),
                'valor': valor,
                'data_vencimento': self.var_pagar['vencimento'].get(),
                'status': self.var_pagar['status'].get(),
                'data_pagamento': self.var_pagar['pagamento'].get() if self.var_pagar['pagamento'].get() else None,
                'categoria': self.var_pagar['categoria'].get()
            }
            
            if self.var_pagar['id'].get() in ("Novo", ""):
                # Inserir nova conta
                cursor.execute("""
                INSERT INTO contas_pagar (descricao, fornecedor, valor, data_vencimento, status, data_pagamento, categoria)
                VALUES (:descricao, :fornecedor, :valor, :data_vencimento, :status, :data_pagamento, :categoria)
                """, dados)
                conn.commit()
                messagebox.showinfo("Sucesso", "Conta cadastrada com sucesso!")
            else:
                # Atualizar conta existente
                dados['id'] = self.var_pagar['id'].get()
                cursor.execute("""
                UPDATE contas_pagar 
                SET descricao = :descricao, fornecedor = :fornecedor, valor = :valor, 
                    data_vencimento = :data_vencimento, status = :status, 
                    data_pagamento = :data_pagamento, categoria = :categoria
                WHERE id = :id
                """, dados)
                conn.commit()
                messagebox.showinfo("Sucesso", "Conta atualizada com sucesso!")
            
            conn.close()
            self.carregar_contas_pagar()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar conta:\n{str(e)}")
    
    def carregar_contas_pagar(self):
        """Carrega as contas a pagar do banco de dados"""
        self.contas_pagar = []
        for item in self.tree_pagar.get_children():
            self.tree_pagar.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Construir a query com filtro
            query = "SELECT id, descricao, fornecedor, valor, data_vencimento, status, data_pagamento, categoria FROM contas_pagar"
            params = []
            
            status_filtro = self.filtros['status_pagar'].get()
            if status_filtro != "TODOS":
                query += " WHERE status = ?"
                params.append(status_filtro)
            
            query += " ORDER BY data_vencimento"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            total_pendente = 0
            total_pago = 0
            
            for row in rows:
                conta = {
                    'id': row[0],
                    'descricao': row[1],
                    'fornecedor': row[2],
                    'valor': row[3],
                    'vencimento': row[4],
                    'status': row[5],
                    'pagamento': row[6],
                    'categoria': row[7]
                }
                
                self.contas_pagar.append(conta)
                
                # Calcular totais
                if conta['status'] == "Paga":
                    total_pago += conta['valor']
                else:
                    total_pendente += conta['valor']
                
                # Adicionar à treeview
                self.tree_pagar.insert("", END, values=(
                    conta['id'],
                    conta['descricao'],
                    conta['fornecedor'],
                    f"R$ {conta['valor']:.2f}",
                    conta['vencimento'],
                    conta['status'],
                    conta['pagamento'] if conta['pagamento'] else "-",
                    conta['categoria']
                ), tags=(conta['status'],))
            
            # Adicionar totais
            self.tree_pagar.insert("", END, values=("", "", "", "", "", "TOTAL PENDENTE:", f"R$ {total_pendente:.2f}", ""), tags=('Pendente',))
            self.tree_pagar.insert("", END, values=("", "", "", "", "", "TOTAL PAGO:", f"R$ {total_pago:.2f}", ""), tags=('Paga',))
            self.tree_pagar.insert("", END, values=("", "", "", "", "", "SALDO:", f"R$ {(total_pago - total_pendente):.2f}", ""))
            
            conn.close()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar contas:\n{str(e)}")
    
    def selecionar_conta_pagar(self, event):
        """Seleciona uma conta a pagar da lista"""
        item = self.tree_pagar.selection()
        if not item:
            return
        
        valores = self.tree_pagar.item(item[0], 'values')
        if valores and valores[0]:  # Ignorar linhas de total
            campos = ['id', 'descricao', 'fornecedor', 'valor', 'vencimento', 'status', 'pagamento', 'categoria']
            for i, campo in enumerate(campos):
                if campo == 'valor' and i < len(valores):
                    # Remove "R$ " do valor para armazenar
                    valor = valores[i].replace("R$ ", "").strip()
                    self.var_pagar[campo].set(valor)
                elif i < len(valores):
                    self.var_pagar[campo].set(valores[i])
            
            # Armazena a conta selecionada
            self.conta_pagar_selecionada = {
                'id': valores[0],
                'descricao': valores[1],
                'fornecedor': valores[2],
                'valor': float(valores[3].replace("R$ ", "").replace(".", "").replace(",", ".")),
                'vencimento': valores[4],
                'status': valores[5],
                'pagamento': valores[6] if len(valores) > 6 else "",
                'categoria': valores[7] if len(valores) > 7 else ""
            }
    
    def excluir_conta_pagar(self):
        """Exclui a conta a pagar selecionada"""
        if not self.conta_pagar_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma conta para excluir!")
            return
        
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta conta?")
        if not resposta:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM contas_pagar WHERE id = ?", (self.conta_pagar_selecionada['id'],))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
            self.limpar_conta_pagar()
            self.carregar_contas_pagar()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir conta:\n{str(e)}")
    
    def limpar_conta_pagar(self):
        """Limpa o formulário de contas a pagar"""
        for var in self.var_pagar.values():
            var.set("")
        self.var_pagar['status'].set("Pendente")
        self.var_pagar['categoria'].set("Outros")
        self.conta_pagar_selecionada = None
    
    def marcar_conta_paga(self):
        """Marca a conta como paga"""
        if not self.conta_pagar_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma conta para marcar como paga!")
            return
        
        self.var_pagar['status'].set("Paga")
        self.var_pagar['pagamento'].set(datetime.now().strftime("%d/%m/%Y"))
        self.salvar_conta_pagar()
    
    def gerar_relatorio_pagar(self):
        """Gera relatório em PDF das contas a pagar"""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Cabeçalho
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Relatório de Contas a Pagar", 0, 1, 'C')
            pdf.ln(5)
            
            # Filtros aplicados
            if self.filtros['status_pagar'].get() != "TODOS":
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, f"Filtro: Status = {self.filtros['status_pagar'].get()}", 0, 1)
                pdf.ln(3)
            
            # Tabela
            pdf.set_font("Arial", 'B', 10)
            colunas = [
                ("Descrição", 60),
                ("Fornecedor", 50),
                ("Valor", 30),
                ("Vencimento", 30),
                ("Status", 25),
                ("Pagamento", 30),
                ("Categoria", 40)
            ]
            
            for col, width in colunas:
                pdf.cell(width, 10, col, border=1)
            pdf.ln()
            
            # Dados
            pdf.set_font("Arial", size=10)
            total_pendente = 0
            total_pago = 0
            
            for conta in self.contas_pagar:
                valor = conta['valor']
                if conta['status'] == "Paga":
                    total_pago += valor
                else:
                    total_pendente += valor
                
                pdf.cell(60, 10, conta['descricao'][:40], border=1)
                pdf.cell(50, 10, conta['fornecedor'][:30], border=1)
                pdf.cell(30, 10, f"R$ {valor:.2f}", border=1)
                pdf.cell(30, 10, conta['vencimento'], border=1)
                pdf.cell(25, 10, conta['status'], border=1)
                pdf.cell(30, 10, conta['pagamento'] if conta['pagamento'] else "-", border=1)
                pdf.cell(40, 10, conta['categoria'], border=1)
                pdf.ln()
            
            # Totais
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(185, 10, "TOTAL PENDENTE:", border=1)
            pdf.cell(30, 10, f"R$ {total_pendente:.2f}", border=1, ln=1)
            pdf.cell(185, 10, "TOTAL PAGO:", border=1)
            pdf.cell(30, 10, f"R$ {total_pago:.2f}", border=1, ln=1)
            pdf.cell(185, 10, "SALDO:", border=1)
            saldo = total_pago - total_pendente
            pdf.cell(30, 10, f"R$ {saldo:.2f}", border=1, ln=1)
            
            # Rodapé
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 10, f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0, 'C')
            
            # Salvar arquivo
            nome_arquivo = f"relatorio_pagar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(nome_arquivo)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nArquivo: {nome_arquivo}")
            
            # Tentar abrir o PDF automaticamente
            try:
                os.startfile(nome_arquivo)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório:\n{str(e)}")

    # ========== ABA TODAS AS CONTAS A RECEBER ==========
    def criar_aba_todas_receber(self):
        """Cria a aba para visualizar todas as contas a receber"""
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Todas a Receber")
        
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(aba, text="Filtros", padding=10)
        frame_filtros.pack(fill=X, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Status:").grid(row=0, column=0, sticky=W)
        ttk.Combobox(frame_filtros, textvariable=self.filtros['status_todas_receber'], 
                     values=["TODOS", "Pendente", "Paga", "Atrasada"], width=10).grid(row=0, column=1, sticky=W)
        
        ttk.Button(frame_filtros, text="Aplicar", command=self.carregar_todas_contas_receber).grid(row=0, column=2, padx=5)
        ttk.Button(frame_filtros, text="Gerar PDF", command=self.gerar_relatorio_todas_receber).grid(row=0, column=3, padx=5)
        
        # Listagem
        frame_lista = ttk.Frame(aba)
        frame_lista.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        colunas = [
            ("ID", 50),
            ("Cliente", 150),
            ("Descrição", 200),
            ("Valor", 100),
            ("Vencimento", 100),
            ("Status", 100),
            ("Pagamento", 100)
        ]
        
        self.tree_todas_receber = ttk.Treeview(frame_lista, columns=[c[0] for c in colunas], show="headings")
        for col, width in colunas:
            self.tree_todas_receber.heading(col, text=col)
            self.tree_todas_receber.column(col, width=width)
        
        # Configurar tags para cores
        self.tree_todas_receber.tag_configure('Pendente', foreground='black')
        self.tree_todas_receber.tag_configure('Paga', foreground='green')
        self.tree_todas_receber.tag_configure('Atrasada', foreground='red')
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame_lista, orient=VERTICAL, command=self.tree_todas_receber.yview)
        self.tree_todas_receber.configure(yscroll=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.tree_todas_receber.pack(fill=BOTH, expand=True)
        
        # Evento de seleção
        self.tree_todas_receber.bind("<<TreeviewSelect>>", self.selecionar_conta_todas_receber)

    def carregar_todas_contas_receber(self):
        """Carrega todas as contas a receber de todos os clientes"""
        self.todas_contas_receber = []
        for item in self.tree_todas_receber.get_children():
            self.tree_todas_receber.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Construir a query com JOIN para pegar o nome do cliente
            query = """
            SELECT cr.id, c.nome, cr.descricao, cr.valor, cr.data_vencimento, cr.status, cr.data_pagamento 
            FROM contas_receber cr
            JOIN clientes c ON cr.id_cliente = c.id
            """
            params = []
            
            status_filtro = self.filtros['status_todas_receber'].get()
            if status_filtro != "TODOS":
                query += " WHERE cr.status = ?"
                params.append(status_filtro)
            
            query += " ORDER BY cr.data_vencimento"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            total_pendente = 0
            total_pago = 0
            
            for row in rows:
                conta = {
                    'id': row[0],
                    'cliente': row[1],
                    'descricao': row[2],
                    'valor': row[3],
                    'vencimento': row[4],
                    'status': row[5],
                    'pagamento': row[6]
                }
                
                self.todas_contas_receber.append(conta)
                
                # Calcular totais
                if conta['status'] == "Paga":
                    total_pago += conta['valor']
                else:
                    total_pendente += conta['valor']
                
                # Adicionar à treeview
                self.tree_todas_receber.insert("", END, values=(
                    conta['id'],
                    conta['cliente'],
                    conta['descricao'],
                    f"R$ {conta['valor']:.2f}",
                    conta['vencimento'],
                    conta['status'],
                    conta['pagamento'] if conta['pagamento'] else "-"
                ), tags=(conta['status'],))
            
            # Adicionar totais
            self.tree_todas_receber.insert("", END, values=("", "", "", "", "TOTAL PENDENTE:", f"R$ {total_pendente:.2f}", ""), tags=('Pendente',))
            self.tree_todas_receber.insert("", END, values=("", "", "", "", "TOTAL PAGO:", f"R$ {total_pago:.2f}", ""), tags=('Paga',))
            self.tree_todas_receber.insert("", END, values=("", "", "", "", "SALDO:", f"R$ {(total_pago - total_pendente):.2f}", ""))
            
            conn.close()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar contas:\n{str(e)}")

    def selecionar_conta_todas_receber(self, event):
        """Seleciona uma conta da lista de todas as contas a receber"""
        item = self.tree_todas_receber.selection()
        if not item:
            return
        
        valores = self.tree_todas_receber.item(item[0], 'values')
        if valores and valores[0]:  # Ignorar linhas de total
            # Pode implementar alguma ação quando selecionar uma conta aqui
            pass

    def gerar_relatorio_todas_receber(self):
        """Gera relatório em PDF de todas as contas a receber"""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Cabeçalho
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Relatório de Todas as Contas a Receber", 0, 1, 'C')
            pdf.ln(5)
            
            # Filtros aplicados
            if self.filtros['status_todas_receber'].get() != "TODOS":
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, f"Filtro: Status = {self.filtros['status_todas_receber'].get()}", 0, 1)
                pdf.ln(3)
            
            # Tabela
            pdf.set_font("Arial", 'B', 10)
            colunas = [
                ("Cliente", 60),
                ("Descrição", 80),
                ("Valor", 30),
                ("Vencimento", 30),
                ("Status", 25),
                ("Pagamento", 30)
            ]
            
            for col, width in colunas:
                pdf.cell(width, 10, col, border=1)
            pdf.ln()
            
            # Dados
            pdf.set_font("Arial", size=10)
            total_pendente = 0
            total_pago = 0
            
            for conta in self.todas_contas_receber:
                valor = conta['valor']
                if conta['status'] == "Paga":
                    total_pago += valor
                else:
                    total_pendente += valor
                
                pdf.cell(60, 10, conta['cliente'][:30], border=1)
                pdf.cell(80, 10, conta['descricao'][:50], border=1)
                pdf.cell(30, 10, f"R$ {valor:.2f}", border=1)
                pdf.cell(30, 10, conta['vencimento'], border=1)
                pdf.cell(25, 10, conta['status'], border=1)
                pdf.cell(30, 10, conta['pagamento'] if conta['pagamento'] else "-", border=1)
                pdf.ln()
            
            # Totais
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(170, 10, "TOTAL PENDENTE:", border=1)
            pdf.cell(30, 10, f"R$ {total_pendente:.2f}", border=1, ln=1)
            pdf.cell(170, 10, "TOTAL PAGO:", border=1)
            pdf.cell(30, 10, f"R$ {total_pago:.2f}", border=1, ln=1)
            pdf.cell(170, 10, "SALDO:", border=1)
            saldo = total_pago - total_pendente
            pdf.cell(30, 10, f"R$ {saldo:.2f}", border=1, ln=1)
            
            # Rodapé
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 10, f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0, 'C')
            
            # Salvar arquivo
            nome_arquivo = f"relatorio_todas_receber_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(nome_arquivo)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nArquivo: {nome_arquivo}")
            
            # Tentar abrir o PDF automaticamente
            try:
                os.startfile(nome_arquivo)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório:\n{str(e)}")

    # ========== MÉTODOS GERAIS ==========
    def carregar_dados(self):
        """Carrega todos os dados iniciais"""
        self.carregar_clientes()
        self.carregar_contas_receber()
        self.carregar_contas_pagar()
        self.carregar_todas_contas_receber()

if __name__ == "__main__":
    root = Tk()
    app = SistemaFinanceiro(root)
    root.mainloop()
