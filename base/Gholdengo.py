import csv
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from fpdf import FPDF
import os
import tempfile

class ControleFinanceiro:
    def __init__(self, root):
        self.root = root
        self.root.title("Gholdengo Financeiro")
        self.root.geometry("1000x700")
        
        try:
            root.iconbitmap("icone.ico")
        except:
            pass
        
        # Nome do arquivo CSV para armazenar os dados
        self.arquivo_csv = "transacoes.csv"
        self.transacoes = []
        self.transacao_selecionada = None
        
        # Criar arquivo CSV se não existir
        self.inicializar_arquivo()
        
        # Variáveis de controle
        self.criar_variaveis_controle()
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Criar widgets
        self.criar_widgets()
        
        # Carregar transações
        self.carregar_transacoes()
    
    def inicializar_arquivo(self):
        if not os.path.exists(self.arquivo_csv):
            with open(self.arquivo_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Data", "Tipo", "Descrição", "Fonte", "Forma de Pagamento", "Valor", "Observações"])
    
    def criar_variaveis_controle(self):
        self.var_data = StringVar()
        self.var_tipo = StringVar()
        self.var_descricao = StringVar()
        self.var_fonte = StringVar()
        self.var_forma_pagamento = StringVar()
        self.var_valor = StringVar()
        self.var_observacoes = StringVar()
        self.var_filtro_tipo = StringVar(value="TODOS")
        self.var_filtro_mes = StringVar(value="TODOS")
        self.var_filtro_ano = StringVar(value="TODOS")
    
    def configurar_estilo(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Treeview', rowheight=25)
        self.style.map('Treeview', background=[('selected', '#0078d7')])
    
    def criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Frame de cadastro
        cadastro_frame = ttk.LabelFrame(main_frame, text="Nova Transação", padding=10)
        cadastro_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Campos do formulário
        self.criar_campos_formulario(cadastro_frame)
        
        # Frame de botões de ação
        botoes_acao_frame = ttk.Frame(cadastro_frame)
        botoes_acao_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(botoes_acao_frame, text="Salvar", command=self.salvar_transacao).pack(side=LEFT, padx=5)
        ttk.Button(botoes_acao_frame, text="Limpar", command=self.limpar_campos).pack(side=LEFT, padx=5)
        ttk.Button(botoes_acao_frame, text="Editar", command=self.editar_transacao).pack(side=LEFT, padx=5)
        ttk.Button(botoes_acao_frame, text="Excluir", command=self.excluir_transacao).pack(side=LEFT, padx=5)
        
        # Frame de relatório
        relatorio_frame = ttk.LabelFrame(main_frame, text="Relatório de Transações", padding=10)
        relatorio_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Treeview para exibir as transações
        self.criar_treeview(relatorio_frame)
        
        # Frame de filtros
        self.criar_filtros(relatorio_frame)
        
        # Configurar pesos das colunas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)
    
    def criar_campos_formulario(self, frame):
        ttk.Label(frame, text="Data (dd/mm/aaaa):").grid(row=0, column=0, sticky=W, pady=2)
        ttk.Entry(frame, textvariable=self.var_data).grid(row=0, column=1, sticky=EW, pady=2)
        self.var_data.set(datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky=W, pady=2)
        tipo_combobox = ttk.Combobox(frame, textvariable=self.var_tipo, values=["ENTRADA", "SAÍDA"], state="readonly")
        tipo_combobox.grid(row=1, column=1, sticky=EW, pady=2)
        tipo_combobox.set("ENTRADA")
        
        ttk.Label(frame, text="Descrição:").grid(row=2, column=0, sticky=W, pady=2)
        ttk.Entry(frame, textvariable=self.var_descricao).grid(row=2, column=1, sticky=EW, pady=2)
        
        ttk.Label(frame, text="Fonte:").grid(row=3, column=0, sticky=W, pady=2)
        ttk.Entry(frame, textvariable=self.var_fonte).grid(row=3, column=1, sticky=EW, pady=2)
        
        ttk.Label(frame, text="Forma de Pagamento:").grid(row=4, column=0, sticky=W, pady=2)
        ttk.Entry(frame, textvariable=self.var_forma_pagamento).grid(row=4, column=1, sticky=EW, pady=2)
        
        ttk.Label(frame, text="Valor:").grid(row=5, column=0, sticky=W, pady=2)
        ttk.Entry(frame, textvariable=self.var_valor).grid(row=5, column=1, sticky=EW, pady=2)
        
        ttk.Label(frame, text="Observações:").grid(row=6, column=0, sticky=W, pady=2)
        ttk.Entry(frame, textvariable=self.var_observacoes).grid(row=6, column=1, sticky=EW, pady=2)
    
    def criar_treeview(self, frame):
        self.tree = ttk.Treeview(frame, columns=("Data", "Tipo", "Descrição", "Fonte", "Forma Pagamento", "Valor"), show="headings", selectmode="browse")
        
        # Definir cabeçalhos
        colunas = [
            ("Data", 100),
            ("Tipo", 80),
            ("Descrição", 200),
            ("Fonte", 120),
            ("Forma Pagamento", 120),
            ("Valor", 100)
        ]
        
        for col, width in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        # Configurar cor para valores negativos
        self.tree.tag_configure('negativo', foreground='red')
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)
        
        # Vincular evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self.selecionar_transacao)
    
    def criar_filtros(self, frame):
        filtros_frame = ttk.Frame(frame)
        filtros_frame.pack(fill=X, pady=5)
        
        ttk.Label(filtros_frame, text="Filtrar por:").pack(side=LEFT, padx=5)
        
        # Filtro por tipo
        ttk.Combobox(filtros_frame, textvariable=self.var_filtro_tipo, 
                    values=["TODOS", "ENTRADA", "SAÍDA"], width=8, state="readonly").pack(side=LEFT, padx=5)
        
        # Filtro por mês
        meses = ["TODOS"] + [f"{m:02d}" for m in range(1, 13)]
        ttk.Combobox(filtros_frame, textvariable=self.var_filtro_mes, 
                    values=meses, width=5, state="readonly").pack(side=LEFT, padx=5)
        
        # Filtro por ano
        anos = ["TODOS"] + [str(ano) for ano in range(2020, datetime.now().year + 3)]
        ttk.Combobox(filtros_frame, textvariable=self.var_filtro_ano, 
                    values=anos, width=5, state="readonly").pack(side=LEFT, padx=5)
        
        # Botões de ação
        ttk.Button(filtros_frame, text="Aplicar Filtro", 
                  command=self.carregar_transacoes).pack(side=LEFT, padx=5)
        ttk.Button(filtros_frame, text="Exportar PDF", 
                  command=self.exportar_pdf).pack(side=LEFT, padx=5)
    
    def carregar_transacoes(self):
        # Limpar treeview e lista de transações
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.transacoes = []
        
        try:
            with open(self.arquivo_csv, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Pular cabeçalho
                
                total_entradas = 0
                total_saidas = 0
                
                for row in reader:
                    if len(row) < 7:  # Verificar se a linha tem todos os campos
                        continue
                    
                    data, tipo, descricao, fonte, forma_pagamento, valor, obs = row
                    try:
                        valor_float = float(valor)
                    except ValueError:
                        continue
                    
                    # Aplicar filtros
                    if not self.aplicar_filtros(data, tipo):
                        continue
                    
                    # Adicionar à lista de transações
                    self.transacoes.append({
                        'data': data,
                        'tipo': tipo,
                        'descricao': descricao,
                        'fonte': fonte,
                        'forma_pagamento': forma_pagamento,
                        'valor': valor_float,
                        'observacoes': obs
                    })
                    
                    # Calcular totais
                    if tipo == "ENTRADA":
                        total_entradas += valor_float
                        valor_formatado = f"R$ {valor_float:,.2f}"
                        tags = ()
                    else:
                        total_saidas += valor_float
                        valor_formatado = f"-R$ {valor_float:,.2f}"
                        tags = ('negativo',)
                    
                    # Inserir na treeview
                    self.tree.insert("", END, values=(
                        data, tipo, descricao, fonte, forma_pagamento, valor_formatado
                    ), tags=tags)
                
                # Adicionar totais
                saldo = total_entradas - total_saidas
                self.tree.insert("", END, values=("", "", "", "", "TOTAL ENTRADAS:", f"R$ {total_entradas:,.2f}"))
                self.tree.insert("", END, values=("", "", "", "", "TOTAL SAÍDAS:", f"-R$ {total_saidas:,.2f}"), tags=('negativo',))
                self.tree.insert("", END, values=("", "", "", "", "SALDO:", f"R$ {saldo:,.2f}"), 
                               tags=('negativo',) if saldo < 0 else ())
                
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo de transações não encontrado!")
    
    def aplicar_filtros(self, data, tipo):
        # Filtro por tipo
        filtro_tipo = self.var_filtro_tipo.get()
        if filtro_tipo != "TODOS" and tipo != filtro_tipo:
            return False
        
        # Filtro por mês e ano
        try:
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            filtro_mes = self.var_filtro_mes.get()
            filtro_ano = self.var_filtro_ano.get()
            
            if filtro_mes != "TODOS" and data_obj.month != int(filtro_mes):
                return False
            if filtro_ano != "TODOS" and data_obj.year != int(filtro_ano):
                return False
        except ValueError:
            return False
        
        return True
    
    def selecionar_transacao(self, event):
        item_selecionado = self.tree.selection()
        if not item_selecionado:
            return
            
        # Obter índice da transação selecionada
        index = self.tree.index(item_selecionado[0])
        
        # Verificar se não é uma linha de total
        if index >= len(self.transacoes):
            self.transacao_selecionada = None
            self.limpar_campos()
            return
        
        self.transacao_selecionada = index
        
        # Preencher campos com os dados da transação selecionada
        transacao = self.transacoes[index]
        self.var_data.set(transacao['data'])
        self.var_tipo.set(transacao['tipo'])
        self.var_descricao.set(transacao['descricao'])
        self.var_fonte.set(transacao['fonte'])
        self.var_forma_pagamento.set(transacao['forma_pagamento'])
        self.var_valor.set(str(abs(transacao['valor'])))
        self.var_observacoes.set(transacao['observacoes'])
    
    def salvar_transacao(self):
        # Validar campos obrigatórios
        if not self.var_data.get() or not self.var_descricao.get() or not self.var_valor.get():
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
            
        try:
            valor = float(self.var_valor.get())
            if self.var_tipo.get() == "SAÍDA":
                valor = -abs(valor)
            else:
                valor = abs(valor)
            
            nova_transacao = [
                self.var_data.get(),
                self.var_tipo.get(),
                self.var_descricao.get(),
                self.var_fonte.get(),
                self.var_forma_pagamento.get(),
                str(abs(valor)),
                self.var_observacoes.get()
            ]
            
            # Se há uma transação selecionada, editar. Caso contrário, adicionar nova
            if self.transacao_selecionada is not None:
                self.editar_transacao_arquivo(nova_transacao)
            else:
                self.adicionar_transacao_arquivo(nova_transacao)
            
            messagebox.showinfo("Sucesso", "Transação salva com sucesso!")
            self.limpar_campos()
            self.carregar_transacoes()
            
        except ValueError:
            messagebox.showerror("Erro", "Valor deve ser um número válido!")
    
    def adicionar_transacao_arquivo(self, transacao):
        with open(self.arquivo_csv, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(transacao)
    
    def editar_transacao_arquivo(self, transacao_atualizada):
        # Ler todas as transações
        with open(self.arquivo_csv, 'r', encoding='utf-8') as file:
            linhas = list(csv.reader(file))
        
        # Atualizar a transação selecionada (ignorando o cabeçalho)
        if 1 <= self.transacao_selecionada + 1 < len(linhas):
            linhas[self.transacao_selecionada + 1] = transacao_atualizada
        
        # Reescrever o arquivo
        with open(self.arquivo_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(linhas)
    
    def limpar_campos(self):
        self.var_data.set(datetime.now().strftime("%d/%m/%Y"))
        self.var_tipo.set("ENTRADA")
        self.var_descricao.set("")
        self.var_fonte.set("")
        self.var_forma_pagamento.set("")
        self.var_valor.set("")
        self.var_observacoes.set("")
        self.transacao_selecionada = None
        self.tree.selection_remove(self.tree.selection())
    
    def editar_transacao(self):
        if self.transacao_selecionada is None:
            messagebox.showwarning("Aviso", "Selecione uma transação para editar!")
            return
        self.salvar_transacao()
    
    def excluir_transacao(self):
        if self.transacao_selecionada is None:
            messagebox.showwarning("Aviso", "Selecione uma transação para excluir!")
            return
            
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?")
        if not resposta:
            return
            
        # Ler todas as transações
        with open(self.arquivo_csv, 'r', encoding='utf-8') as file:
            linhas = list(csv.reader(file))
        
        # Remover a transação selecionada (ignorando o cabeçalho)
        if 1 <= self.transacao_selecionada + 1 < len(linhas):
            linhas.pop(self.transacao_selecionada + 1)
        
        # Reescrever o arquivo
        with open(self.arquivo_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(linhas)
        
        messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
        self.limpar_campos()
        self.carregar_transacoes()
    
    def exportar_pdf(self):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Título
            pdf.cell(0, 10, "Relatório Financeiro", 0, 1, "C")
            pdf.ln(5)
            
            # Informações dos filtros
            filtros = []
            if self.var_filtro_tipo.get() != "TODOS":
                filtros.append(f"Tipo: {self.var_filtro_tipo.get()}")
            if self.var_filtro_mes.get() != "TODOS":
                filtros.append(f"Mês: {self.var_filtro_mes.get()}")
            if self.var_filtro_ano.get() != "TODOS":
                filtros.append(f"Ano: {self.var_filtro_ano.get()}")
            
            if filtros:
                pdf.set_font("Arial", "I", 10)
                pdf.cell(0, 10, "Filtros aplicados: " + ", ".join(filtros), 0, 1)
                pdf.ln(3)
            
            # Cabeçalho da tabela
            pdf.set_font("Arial", "B", 10)
            colunas = [
                ("Data", 25),
                ("Tipo", 20),
                ("Descrição", 60),
                ("Fonte", 30),
                ("Forma Pagto", 30),
                ("Valor", 25)
            ]
            
            for col, width in colunas:
                pdf.cell(width, 10, col, 1)
            pdf.ln()
            
            # Dados
            pdf.set_font("Arial", size=10)
            total_entradas = 0
            total_saidas = 0
            
            for transacao in self.transacoes:
                valor = transacao['valor']
                
                if transacao['tipo'] == "ENTRADA":
                    total_entradas += valor
                    valor_str = f"R$ {valor:,.2f}"
                else:
                    total_saidas += valor
                    valor_str = f"-R$ {valor:,.2f}"
                
                # Adicionar linha
                pdf.cell(25, 10, transacao['data'], 1)
                pdf.cell(20, 10, transacao['tipo'], 1)
                pdf.cell(60, 10, transacao['descricao'][:30], 1)  # Limitar tamanho
                pdf.cell(30, 10, transacao['fonte'][:15], 1)
                pdf.cell(30, 10, transacao['forma_pagamento'][:15], 1)
                pdf.cell(25, 10, valor_str, 1, 0, "R")
                pdf.ln()
            
            # Totais
            saldo = total_entradas - total_saidas
            pdf.set_font("Arial", "B", 10)
            pdf.cell(165, 10, "TOTAL ENTRADAS:", 1, 0, "R")
            pdf.cell(25, 10, f"R$ {total_entradas:,.2f}", 1, 0, "R")
            pdf.ln()
            pdf.cell(165, 10, "TOTAL SAÍDAS:", 1, 0, "R")
            pdf.cell(25, 10, f"-R$ {total_saidas:,.2f}", 1, 0, "R")
            pdf.ln()
            pdf.cell(165, 10, "SALDO:", 1, 0, "R")
            pdf.cell(25, 10, f"R$ {saldo:,.2f}", 1, 0, "R")
            
            # Salvar arquivo
            nome_arquivo = f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(nome_arquivo)
            messagebox.showinfo("Sucesso", f"Relatório exportado como:\n{nome_arquivo}")
            
            # Abrir o arquivo PDF automaticamente
            try:
                os.startfile(nome_arquivo)
            except:
                pass
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar PDF:\n{str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = ControleFinanceiro(root)
    root.mainloop()
