import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class SistemaPecasCaminhao:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Peças - Mecânica Diesel")
        self.root.geometry("1000x600")
        
        # Conexão com o banco de dados
        self.conn = sqlite3.connect('pecas_caminhao.db')
        self.criar_tabelas()
        
        # Interface
        self.criar_widgets()
        self.carregar_dados()
        
    def criar_tabelas(self):
        cursor = self.conn.cursor()
        
        # Tabela de peças
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            descricao TEXT,
            fabricante TEXT,
            numero_oem TEXT,
            tipo TEXT,
            veiculos_compativel TEXT,
            estoque_atual INTEGER,
            estoque_minimo INTEGER,
            preco_custo REAL,
            preco_venda REAL,
            localizacao TEXT,
            data_cadastro TEXT
        )
        ''')
        
        # Tabela de movimentações
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peca_id INTEGER,
            tipo TEXT,
            quantidade INTEGER,
            data TEXT,
            responsavel TEXT,
            observacao TEXT,
            FOREIGN KEY(peca_id) REFERENCES pecas(id)
        )
        ''')
        
        self.conn.commit()
    
    def criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Abas
        self.notebook = ttk.Notebook(main_frame)
        
        # Aba de Cadastro
        self.aba_cadastro = ttk.Frame(self.notebook)
        self.criar_aba_cadastro()
        
        # Aba de Estoque
        self.aba_estoque = ttk.Frame(self.notebook)
        self.criar_aba_estoque()
        
        # Aba de Movimentações
        self.aba_movimentacoes = ttk.Frame(self.notebook)
        self.criar_aba_movimentacoes()
        
        self.notebook.add(self.aba_cadastro, text="Cadastro")
        self.notebook.add(self.aba_estoque, text="Estoque")
        self.notebook.add(self.aba_movimentacoes, text="Movimentações")
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def criar_aba_cadastro(self):
        # Frame de formulário
        form_frame = ttk.LabelFrame(self.aba_cadastro, text="Dados da Peça")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos do formulário
        campos = [
            ("Código:", "entry_codigo"),
            ("Descrição:", "entry_descricao"),
            ("Fabricante:", "entry_fabricante"),
            ("Número OEM:", "entry_oem"),
            ("Tipo:", "combo_tipo"),
            ("Veículos Compatíveis:", "entry_veiculos"),
            ("Estoque Atual:", "entry_estoque"),
            ("Estoque Mínimo:", "entry_estoque_min"),
            ("Preço Custo:", "entry_custo"),
            ("Preço Venda:", "entry_venda"),
            ("Localização:", "entry_localizacao")
        ]
        
        self.widgets_cadastro = {}
        tipos_peca = ["Motor", "Transmissão", "Elétrica", "Suspensão", "Freio", "Direção", "Arla", "Filtro", "Outros"]
        
        for i, (label, nome) in enumerate(campos):
            lbl = ttk.Label(form_frame, text=label)
            lbl.grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            
            if nome == "combo_tipo":
                widget = ttk.Combobox(form_frame, values=tipos_peca, state="readonly")
            else:
                widget = ttk.Entry(form_frame)
                
            widget.grid(row=i, column=1, padx=5, pady=2, sticky=tk.EW)
            self.widgets_cadastro[nome] = widget
        
        # Frame de botões
        btn_frame = ttk.Frame(self.aba_cadastro)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self.salvar_peca)
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_limpar = ttk.Button(btn_frame, text="Limpar", command=self.limpar_formulario)
        btn_limpar.pack(side=tk.LEFT, padx=5)
        
        # Treeview para listagem
        tree_frame = ttk.Frame(self.aba_cadastro)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Código", "Descrição", "Fabricante", "Tipo", "Estoque", "Preço Venda")
        self.tree_pecas = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree_pecas.heading(col, text=col)
            self.tree_pecas.column(col, width=100)
        
        self.tree_pecas.column("Descrição", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_pecas.yview)
        self.tree_pecas.configure(yscroll=scrollbar.set)
        
        self.tree_pecas.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree_pecas.bind("<<TreeviewSelect>>", self.carregar_peca_selecionada)
    
    def criar_aba_estoque(self):
        # Filtros
        filter_frame = ttk.LabelFrame(self.aba_estoque, text="Filtros")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=2)
        self.combo_filtro_tipo = ttk.Combobox(filter_frame, values=["Todos", "Motor", "Transmissão", "Elétrica", "Suspensão", "Freio", "Direção", "Arla", "Filtro", "Outros"], state="readonly")
        self.combo_filtro_tipo.grid(row=0, column=1, padx=5, pady=2)
        self.combo_filtro_tipo.set("Todos")
        
        ttk.Label(filter_frame, text="Estoque:").grid(row=0, column=2, padx=5, pady=2)
        self.combo_filtro_estoque = ttk.Combobox(filter_frame, values=["Todos", "Abaixo do mínimo", "Em estoque", "Sem estoque"], state="readonly")
        self.combo_filtro_estoque.grid(row=0, column=3, padx=5, pady=2)
        self.combo_filtro_estoque.set("Todos")
        
        btn_filtrar = ttk.Button(filter_frame, text="Filtrar", command=self.filtrar_estoque)
        btn_filtrar.grid(row=0, column=4, padx=5, pady=2)
        
        # Treeview de estoque
        tree_frame = ttk.Frame(self.aba_estoque)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Código", "Descrição", "Tipo", "Estoque", "Mínimo", "Localização", "Status")
        self.tree_estoque = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree_estoque.heading(col, text=col)
            self.tree_estoque.column(col, width=100)
        
        self.tree_estoque.column("Descrição", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_estoque.yview)
        self.tree_estoque.configure(yscroll=scrollbar.set)
        
        self.tree_estoque.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Botões de ação
        btn_frame = ttk.Frame(self.aba_estoque)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_entrada = ttk.Button(btn_frame, text="Registrar Entrada", command=lambda: self.abrir_dialog_movimentacao("entrada"))
        btn_entrada.pack(side=tk.LEFT, padx=5)
        
        btn_saida = ttk.Button(btn_frame, text="Registrar Saída", command=lambda: self.abrir_dialog_movimentacao("saida"))
        btn_saida.pack(side=tk.LEFT, padx=5)
        
        btn_relatorio = ttk.Button(btn_frame, text="Gerar Relatório", command=self.gerar_relatorio_estoque)
        btn_relatorio.pack(side=tk.RIGHT, padx=5)
    
    def criar_aba_movimentacoes(self):
        # Filtros
        filter_frame = ttk.LabelFrame(self.aba_movimentacoes, text="Filtros")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=2)
        self.combo_filtro_mov_tipo = ttk.Combobox(filter_frame, values=["Todos", "Entrada", "Saída"], state="readonly")
        self.combo_filtro_mov_tipo.grid(row=0, column=1, padx=5, pady=2)
        self.combo_filtro_mov_tipo.set("Todos")
        
        ttk.Label(filter_frame, text="Data Início:").grid(row=0, column=2, padx=5, pady=2)
        self.entry_mov_data_inicio = ttk.Entry(filter_frame)
        self.entry_mov_data_inicio.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="Data Fim:").grid(row=0, column=4, padx=5, pady=2)
        self.entry_mov_data_fim = ttk.Entry(filter_frame)
        self.entry_mov_data_fim.grid(row=0, column=5, padx=5, pady=2)
        
        btn_filtrar = ttk.Button(filter_frame, text="Filtrar", command=self.filtrar_movimentacoes)
        btn_filtrar.grid(row=0, column=6, padx=5, pady=2)
        
        # Treeview de movimentações
        tree_frame = ttk.Frame(self.aba_movimentacoes)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Data", "Tipo", "Código", "Descrição", "Quantidade", "Responsável", "Observação")
        self.tree_movimentacoes = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree_movimentacoes.heading(col, text=col)
            self.tree_movimentacoes.column(col, width=100)
        
        self.tree_movimentacoes.column("Descrição", width=200)
        self.tree_movimentacoes.column("Observação", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_movimentacoes.yview)
        self.tree_movimentacoes.configure(yscroll=scrollbar.set)
        
        self.tree_movimentacoes.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def carregar_dados(self):
        self.carregar_pecas()
        self.carregar_estoque()
        self.carregar_movimentacoes()
    
    def carregar_pecas(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, codigo, descricao, fabricante, tipo, estoque_atual, preco_venda FROM pecas")
        rows = cursor.fetchall()
        
        self.tree_pecas.delete(*self.tree_pecas.get_children())
        for row in rows:
            self.tree_pecas.insert("", tk.END, values=row)
    
    def carregar_estoque(self):
        cursor = self.conn.cursor()
        query = """
        SELECT 
            p.id, 
            p.codigo, 
            p.descricao, 
            p.tipo, 
            p.estoque_atual, 
            p.estoque_minimo, 
            p.localizacao,
            CASE 
                WHEN p.estoque_atual <= 0 THEN 'Sem Estoque'
                WHEN p.estoque_atual < p.estoque_minimo THEN 'Abaixo do Mínimo'
                ELSE 'OK'
            END as status
        FROM pecas p
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        self.tree_estoque.delete(*self.tree_estoque.get_children())
        for row in rows:
            self.tree_estoque.insert("", tk.END, values=row)
    
    def carregar_movimentacoes(self):
        cursor = self.conn.cursor()
        query = """
        SELECT 
            m.id,
            m.data,
            m.tipo,
            p.codigo,
            p.descricao,
            m.quantidade,
            m.responsavel,
            m.observacao
        FROM movimentacoes m
        JOIN pecas p ON m.peca_id = p.id
        ORDER BY m.data DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        self.tree_movimentacoes.delete(*self.tree_movimentacoes.get_children())
        for row in rows:
            self.tree_movimentacoes.insert("", tk.END, values=row)
    
    def salvar_peca(self):
        dados = {
            'codigo': self.widgets_cadastro['entry_codigo'].get(),
            'descricao': self.widgets_cadastro['entry_descricao'].get(),
            'fabricante': self.widgets_cadastro['entry_fabricante'].get(),
            'numero_oem': self.widgets_cadastro['entry_oem'].get(),
            'tipo': self.widgets_cadastro['combo_tipo'].get(),
            'veiculos_compativel': self.widgets_cadastro['entry_veiculos'].get(),
            'estoque_atual': self.widgets_cadastro['entry_estoque'].get() or 0,
            'estoque_minimo': self.widgets_cadastro['entry_estoque_min'].get() or 0,
            'preco_custo': self.widgets_cadastro['entry_custo'].get() or 0,
            'preco_venda': self.widgets_cadastro['entry_venda'].get() or 0,
            'localizacao': self.widgets_cadastro['entry_localizacao'].get(),
            'data_cadastro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Validação básica
        if not dados['codigo'] or not dados['descricao']:
            messagebox.showerror("Erro", "Código e Descrição são obrigatórios!")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Verifica se é uma atualização
            selected_item = self.tree_pecas.selection()
            if selected_item:
                item_id = self.tree_pecas.item(selected_item)['values'][0]
                cursor.execute('''
                UPDATE pecas SET 
                    codigo=?, descricao=?, fabricante=?, numero_oem=?, tipo=?, veiculos_compativel=?,
                    estoque_atual=?, estoque_minimo=?, preco_custo=?, preco_venda=?, localizacao=?
                WHERE id=?
                ''', (
                    dados['codigo'], dados['descricao'], dados['fabricante'], dados['numero_oem'], dados['tipo'],
                    dados['veiculos_compativel'], dados['estoque_atual'], dados['estoque_minimo'],
                    dados['preco_custo'], dados['preco_venda'], dados['localizacao'], item_id
                ))
                messagebox.showinfo("Sucesso", "Peça atualizada com sucesso!")
            else:
                cursor.execute('''
                INSERT INTO pecas (
                    codigo, descricao, fabricante, numero_oem, tipo, veiculos_compativel,
                    estoque_atual, estoque_minimo, preco_custo, preco_venda, localizacao, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', tuple(dados.values()))
                messagebox.showinfo("Sucesso", "Peça cadastrada com sucesso!")
            
            self.conn.commit()
            self.limpar_formulario()
            self.carregar_dados()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código já cadastrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def limpar_formulario(self):
        for widget in self.widgets_cadastro.values():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set('')
        
        # Desmarcar seleção na treeview
        for item in self.tree_pecas.selection():
            self.tree_pecas.selection_remove(item)
    
    def carregar_peca_selecionada(self, event):
        selected_item = self.tree_pecas.selection()
        if not selected_item:
            return
        
        item_id = self.tree_pecas.item(selected_item)['values'][0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pecas WHERE id=?", (item_id,))
        peca = cursor.fetchone()
        
        if peca:
            colunas = ['codigo', 'descricao', 'fabricante', 'numero_oem', 'tipo', 
                      'veiculos_compativel', 'estoque_atual', 'estoque_minimo',
                      'preco_custo', 'preco_venda', 'localizacao']
            
            for col, widget_name in zip(colunas, self.widgets_cadastro.keys()):
                widget = self.widgets_cadastro[widget_name]
                value = peca[colunas.index(col)+1]  # +1 porque o ID é o primeiro
                
                if isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value) if value is not None else "")
                elif isinstance(widget, ttk.Combobox):
                    widget.set(value if value is not None else "")
    
    def filtrar_estoque(self):
        tipo = self.combo_filtro_tipo.get()
        estoque = self.combo_filtro_estoque.get()
        
        query = """
        SELECT 
            p.id, 
            p.codigo, 
            p.descricao, 
            p.tipo, 
            p.estoque_atual, 
            p.estoque_minimo, 
            p.localizacao,
            CASE 
                WHEN p.estoque_atual <= 0 THEN 'Sem Estoque'
                WHEN p.estoque_atual < p.estoque_minimo THEN 'Abaixo do Mínimo'
                ELSE 'OK'
            END as status
        FROM pecas p
        WHERE 1=1
        """
        
        params = []
        
        if tipo != "Todos":
            query += " AND p.tipo = ?"
            params.append(tipo)
        
        if estoque == "Abaixo do mínimo":
            query += " AND p.estoque_atual < p.estoque_minimo AND p.estoque_atual > 0"
        elif estoque == "Em estoque":
            query += " AND p.estoque_atual >= p.estoque_minimo"
        elif estoque == "Sem estoque":
            query += " AND p.estoque_atual <= 0"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        self.tree_estoque.delete(*self.tree_estoque.get_children())
        for row in rows:
            self.tree_estoque.insert("", tk.END, values=row)
    
    def abrir_dialog_movimentacao(self, tipo):
        selected_item = self.tree_estoque.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma peça para registrar movimentação!")
            return
        
        peca_id = self.tree_estoque.item(selected_item)['values'][0]
        peca_codigo = self.tree_estoque.item(selected_item)['values'][1]
        peca_descricao = self.tree_estoque.item(selected_item)['values'][2]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Registrar {'Entrada' if tipo == 'entrada' else 'Saída'}")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text=f"Peça: {peca_codigo} - {peca_descricao}").pack(pady=5)
        
        ttk.Label(dialog, text="Quantidade:").pack(pady=5)
        entry_quantidade = ttk.Entry(dialog)
        entry_quantidade.pack(pady=5)
        
        ttk.Label(dialog, text="Responsável:").pack(pady=5)
        entry_responsavel = ttk.Entry(dialog)
        entry_responsavel.pack(pady=5)
        
        ttk.Label(dialog, text="Observação:").pack(pady=5)
        text_observacao = tk.Text(dialog, height=4, width=40)
        text_observacao.pack(pady=5)
        
        def registrar_movimentacao():
            try:
                quantidade = int(entry_quantidade.get())
                if quantidade <= 0:
                    raise ValueError("Quantidade deve ser positiva")
                
                responsavel = entry_responsavel.get()
                if not responsavel:
                    raise ValueError("Responsável é obrigatório")
                
                observacao = text_observacao.get("1.0", tk.END).strip()
                
                cursor = self.conn.cursor()
                
                # Atualiza estoque
                if tipo == "entrada":
                    cursor.execute("UPDATE pecas SET estoque_atual = estoque_atual + ? WHERE id = ?", (quantidade, peca_id))
                else:
                    # Verifica se há estoque suficiente
                    cursor.execute("SELECT estoque_atual FROM pecas WHERE id = ?", (peca_id,))
                    estoque_atual = cursor.fetchone()[0]
                    if estoque_atual < quantidade:
                        raise ValueError("Estoque insuficiente")
                    cursor.execute("UPDATE pecas SET estoque_atual = estoque_atual - ? WHERE id = ?", (quantidade, peca_id))
                
                # Registra movimentação
                cursor.execute('''
                INSERT INTO movimentacoes (
                    peca_id, tipo, quantidade, data, responsavel, observacao
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    peca_id,
                    'ENTRADA' if tipo == 'entrada' else 'SAIDA',
                    quantidade,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    responsavel,
                    observacao
                ))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Movimentação registrada com sucesso!")
                dialog.destroy()
                self.carregar_dados()
                
            except ValueError as ve:
                messagebox.showerror("Erro", str(ve))
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
        
        btn_registrar = ttk.Button(dialog, text="Registrar", command=registrar_movimentacao)
        btn_registrar.pack(pady=10)
    
    def filtrar_movimentacoes(self):
        tipo = self.combo_filtro_mov_tipo.get()
        data_inicio = self.entry_mov_data_inicio.get()
        data_fim = self.entry_mov_data_fim.get()
        
        query = """
        SELECT 
            m.id,
            m.data,
            m.tipo,
            p.codigo,
            p.descricao,
            m.quantidade,
            m.responsavel,
            m.observacao
        FROM movimentacoes m
        JOIN pecas p ON m.peca_id = p.id
        WHERE 1=1
        """
        
        params = []
        
        if tipo != "Todos":
            query += " AND m.tipo = ?"
            params.append(tipo)
        
        if data_inicio:
            try:
                datetime.strptime(data_inicio, "%Y-%m-%d")
                query += " AND date(m.data) >= ?"
                params.append(data_inicio)
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido (use YYYY-MM-DD)")
                return
        
        if data_fim:
            try:
                datetime.strptime(data_fim, "%Y-%m-%d")
                query += " AND date(m.data) <= ?"
                params.append(data_fim)
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido (use YYYY-MM-DD)")
                return
        
        query += " ORDER BY m.data DESC"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        self.tree_movimentacoes.delete(*self.tree_movimentacoes.get_children())
        for row in rows:
            self.tree_movimentacoes.insert("", tk.END, values=row)
    
    def gerar_relatorio_estoque(self):
        # Esta função poderia ser expandida para gerar um relatório em PDF ou Excel
        messagebox.showinfo("Relatório", "Funcionalidade de relatório será implementada aqui")
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaPecasCaminhao(root)
    root.mainloop()
