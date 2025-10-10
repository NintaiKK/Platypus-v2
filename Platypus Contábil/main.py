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

        self.valor_total = tk.DoubleVar(value=0.0)

        self.criar_tabela_ordens_servico()

        self.dados_empresa = {
            "nome": "Viana & Viana Mecânica Diesel LTDA",
            "endereco": "Rua Miguel Oresko n90",
            "cidade": "Nova Santa Rita",
            "cnpj": "61.459.722/0001-01",
            "ie": "n lembro hehe",
            "telefone": "51 9 9903-6427"
        }
        
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
    
    #Carregar Lista
    def carregar_lista_clientes(self, filtro=None):
        """Carrega a lista de clientes na treeview"""
        # Limpa a treeview
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
            
        # Consulta os clientes no banco de dados
        if filtro:
            self.c.execute('''SELECT id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento 
                            FROM clientes 
                            WHERE nome LIKE ? OR cnpj LIKE ? 
                            ORDER BY nome''', 
                        (f'%{filtro}%', f'%{filtro}%'))
        else:
            self.c.execute('''SELECT id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento 
                            FROM clientes 
                            ORDER BY nome''')
            
        clientes = self.c.fetchall()
            
        # Adiciona os clientes na treeview
        for cliente in clientes:
            self.tree_clientes.insert('', tk.END, values=cliente)

    #Carregar Lista
    def carregar_lista_peca(self, filtro=None):

        # Limpa a treeview
        for item in self.tree_pecas.get_children():
            self.tree_pecas.delete(item)
            
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
            
        pecas = self.c.fetchall()
            
        # Adiciona os clientes na treeview
        for peca in pecas:
            self.tree_pecas.insert('', tk.END, values=peca)

    def gerar_numero_os(self):
        """Gera um número fictício de OS baseado na data/hora"""
        return datetime.now().strftime("%Y%m%d%H%M")
    
    def criar_tabela_ordens_servico(self):
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS ordens_servico (
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
                )
            ''')
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS itens_os (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    os_id INTEGER,
                    descricao TEXT,
                    quantidade REAL,
                    valor_unitario REAL,
                    valor_total REAL,
                    FOREIGN KEY (os_id) REFERENCES ordens_servico (id)
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar tabela OS: {str(e)}")

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
                    modelo TEXT,
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
                    vlr_venda TEXT,
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

    def carregar_os_dialog(self):
        #Abre diálogo para selecionar uma OS para carregar
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
            
            pdf.cell(0, 5, f"CPF/CNPJ: {self.cliente_nome.get()}", 0, 1)
            pdf.cell(0, 5, f"Nome: {self.cliente_endereco.get()}", 0, 1)
            pdf.cell(0, 5, f"Endereço: {self.cliente_cidade.get()}", 0, 1)
            pdf.cell(0, 5, f"Cidade: {self.cliente_cpf_cnpj.get()} - Tel: {self.cliente_telefone.get()}", 0, 1)
            
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
        
        if self.cliente_id:
            self.preencher_campos_os_cliente()
            
        self.limpar_campos_os()
        self.numero_os.set(self.gerar_numero_os())
        self.data_emissao.set(datetime.now().strftime("%d/%m/%Y %H:%M"))

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
        descricao = self.desc_item.get()
        quantidade = self.qtd_item.get()
        valor_unit = self.valor_item.get()
        
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
        self.desc_item.delete(0, tk.END)
        self.qtd_item.delete(0, tk.END)
        self.valor_item.delete(0, tk.END)
        self.desc_item.focus()
    
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

    def excluir_cliente(self):
        """Exclui o cliente selecionado na lista"""
        selected_item = self.tree_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um cliente para excluir!")
            return
        
        cliente_id = self.tree_clientes.item(selected_item)['values'][0]
        cliente_nome = self.tree_clientes.item(selected_item)['values'][2]
        
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o cliente {cliente_nome}?"):
            return
        
        try:
            # Verifica se existem ordens de serviço para este cliente
            self.c.execute("SELECT COUNT(*) FROM ordens_servico WHERE cliente_id=?", (cliente_id,))
            if self.c.fetchone()[0] > 0:
                messagebox.showerror("Erro", "Este cliente possui ordens de serviço vinculadas e não pode ser excluído!")
                return
            
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
        
        # O ID está na primeira coluna (índice 0)
        cliente_id = self.tree_clientes.item(selected_item)['values'][0]
        
        # Carrega os dados do cliente selecionado
        self.carregar_dados_cliente(cliente_id)
        
        # Fecha a janela de seleção
        if window:
            window.destroy()

    def selecionar_veiculo_na_lista(self, window):
        """Seleciona o cliente da lista para a ordem de serviço"""
        selected_item = self.tree_veiculos.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um veículo!")
            return
        
        veiculo_id = self.tree_veiculos.item(selected_item)['values'][0]
        self.carregar_dados_veiculo(veiculo_id)
        window.destroy()
    
    def carregar_dados_veiculo(self, veiculo_id):
        """Carrega os dados do cliente nos campos do formulário"""
        self.c.execute("SELECT * FROM veiculos WHERE id=?", (veiculo_id,))
        veiculo = self.c.fetchone()
        
        if veiculo:
            self.veiculo_id = veiculo[0]
            self.cliente_veiculo.set(veiculo[5])
            self.cliente_placa.set(veiculo[2])
            self.cliente_km.set(veiculo[3])
    
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

    def atualizar_cliente(self, cliente_id, cnpj, nome, endereco, cidade, telefone, email, responsavel, cpf_responsavel, dt_nascimento, janela):
        """Atualiza os dados do cliente no banco de dados"""
        if not nome:
            messagebox.showerror("Erro", "O campo nome é obrigatório!")
            return
            
        try:
            self.c.execute('''UPDATE clientes SET 
                            cnpj=?, nome=?, endereco=?, cidade=?, telefone=?, 
                            email=?, responsavel=?, cpf_responsavel=?, dt_nascimento=?
                            WHERE id=?''',
                        (cnpj, nome, endereco, cidade, telefone, email, 
                        responsavel, cpf_responsavel, dt_nascimento, cliente_id))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            
            # Fecha a janela de edição
            janela.destroy()
            
            # Atualiza a lista de clientes se estiver aberta
            if hasattr(self, 'tree_clientes') and self.tree_clientes.winfo_exists():
                self.carregar_lista_clientes()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar cliente: {str(e)}")

    def abrir_editor_cliente(self, cliente_data):
        """Abre janela para editar cliente existente"""
        editor = tk.Toplevel(self.root)
        editor.title("Editar Cliente")
        editor.geometry("800x300")
        editor.resizable(False, False)
        editor.transient(self.root)
        editor.grab_set()

        frame = ttk.Frame(editor, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Preenche os campos com os dados do cliente
        ttk.Label(frame, text="CNPJ/CPF").grid(row=0, column=0, sticky=tk.W, pady=5)
        cnpj_entry = ttk.Entry(frame, width=40)
        cnpj_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        cnpj_entry.insert(0, cliente_data[1] if cliente_data[1] else "")

        ttk.Label(frame, text="Razão Social/Nome").grid(row=1, column=0, sticky=tk.W, pady=5)
        nome_entry = ttk.Entry(frame, width=40)
        nome_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        nome_entry.insert(0, cliente_data[2] if cliente_data[2] else "")

        ttk.Label(frame, text="Endereço").grid(row=2, column=0, sticky=tk.W, pady=5)
        endereco_entry = ttk.Entry(frame, width=40)
        endereco_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        endereco_entry.insert(0, cliente_data[3] if cliente_data[3] else "")

        ttk.Label(frame, text="Cidade/UF").grid(row=2, column=2, sticky=tk.E, pady=5)
        cidade_entry = ttk.Entry(frame, width=40)
        cidade_entry.grid(row=2, column=3, pady=5, padx=(10, 0))
        cidade_entry.insert(0, cliente_data[4] if cliente_data[4] else "")

        ttk.Label(frame, text="Telefone").grid(row=3, column=0, sticky=tk.W, pady=5)
        telefone_entry = ttk.Entry(frame, width=40)
        telefone_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        telefone_entry.insert(0, cliente_data[5] if cliente_data[5] else "")

        ttk.Label(frame, text="E-mail").grid(row=3, column=2, sticky=tk.E, pady=5)
        email_entry = ttk.Entry(frame, width=40)
        email_entry.grid(row=3, column=3, pady=5, padx=(10, 0))
        email_entry.insert(0, cliente_data[6] if cliente_data[6] else "")

        ttk.Label(frame, text="Responsável").grid(row=4, column=0, sticky=tk.W, pady=5)
        resp_entry = ttk.Entry(frame, width=40)
        resp_entry.grid(row=4, column=1, pady=5, padx=(10, 0))
        resp_entry.insert(0, cliente_data[7] if cliente_data[7] else "")

        ttk.Label(frame, text="CPF Responsável").grid(row=4, column=2, sticky=tk.E, pady=5)
        cpfresp_entry = ttk.Entry(frame, width=40)
        cpfresp_entry.grid(row=4, column=3, pady=5, padx=(10, 0))
        cpfresp_entry.insert(0, cliente_data[8] if cliente_data[8] else "")

        ttk.Label(frame, text="Data de Nascimento").grid(row=5, column=0, sticky=tk.E, pady=5)
        dtnascimento_entry = ttk.Entry(frame, width=40)
        dtnascimento_entry.grid(row=5, column=1, pady=5, padx=(10, 0))
        dtnascimento_entry.insert(0, cliente_data[9] if cliente_data[9] else "")

        # Frame para botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=20)
        
        # Botão Salvar
        ttk.Button(btn_frame, text="Salvar Alterações", 
                command=lambda: self.atualizar_cliente(
                    cliente_data[0],  # ID do cliente
                    cnpj_entry.get(), nome_entry.get(), endereco_entry.get(), 
                    cidade_entry.get(), telefone_entry.get(), email_entry.get(), 
                    resp_entry.get(), cpfresp_entry.get(), dtnascimento_entry.get(),
                    editor
                )).pack(side=tk.LEFT, padx=5)
        
        # Botão Cancelar
        ttk.Button(btn_frame, text="Cancelar", command=editor.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focar no campo nome
        nome_entry.focus_set()

    def editar_veiculo(self):
        selected_item = self.tree_veiculos.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um veículo para editar!")
            return
        
        veiculo_id = self.tree_veiculos.item(selected_item)['values'][0]
        
        # Carrega dados do veículo
        self.c.execute("SELECT * FROM veiculos WHERE id=?", (veiculo_id,))
        veiculo_data = self.c.fetchone()
        
        if veiculo_data:
            self.abrir_editor_veiculo(veiculo_data)

    def abrir_editor_veiculo(self, veiculo_data):
        """Abre janela para editar veículo existente"""
        # Implementação similar ao novo_veiculo com dados pré-carregados
        pass

    def excluir_veiculo(self):
        """Exclui o veículo selecionado na lista"""
        selected_item = self.tree_veiculos.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um veículo para excluir!")
            return
        
        veiculo_id = self.tree_veiculos.item(selected_item)['values'][0]
        
        # Verifica se o veículo está em alguma OS
        self.c.execute("SELECT COUNT(*) FROM ordens_servico WHERE veiculo_id=?", (veiculo_id,))
        if self.c.fetchone()[0] > 0:
            messagebox.showerror("Erro", "Este veículo está vinculado a ordens de serviço e não pode ser excluído!")
            return
        
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este veículo?"):
            self.c.execute("DELETE FROM veiculos WHERE id=?", (veiculo_id,))
            self.conn.commit()
            self.carregar_lista_veiculos()
            messagebox.showinfo("Sucesso", "Veículo excluído com sucesso!")

    def editar_cliente(self):
        """Edita o cliente selecionado na lista"""
        try:
            # Verifica se a treeview existe e está disponível
            if not hasattr(self, 'tree_clientes') or not self.tree_clientes.winfo_exists():
                messagebox.showwarning("Atenção", "Lista de clientes não disponível. Abra a lista de clientes primeiro!")
                return
            
            selected_item = self.tree_clientes.selection()
            if not selected_item:
                messagebox.showwarning("Atenção", "Selecione um cliente para editar!")
                return
            
            cliente_id = self.tree_clientes.item(selected_item)['values'][0]
            self.c.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
            cliente_data = self.c.fetchone()
            
            if cliente_data:
                # Abre janela de edição com dados pré-carregados
                self.abrir_editor_cliente(cliente_data)
            else:
                messagebox.showerror("Erro", "Cliente não encontrado!")
                
        except tk.TclError as e:
            messagebox.showerror("Erro", f"Erro ao acessar a lista de clientes: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    def abrir_gerenciador_clientes(self):
        """Abre a janela de gerenciamento de clientes"""
        veiculos_window = tk.Toplevel(self.root)
        veiculos_window.title("Gerenciador de Clientes")
        veiculos_window.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(veiculos_window, padding="10")
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
                  command=lambda: self.selecionar_cliente_na_lista(veiculos_window)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Editar", 
                  command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Excluir", 
                  command=self.excluir_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Fechar", 
                  command=veiculos_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Carrega a lista de clientes
        self.carregar_lista_veiculos()

    def selecionar_cliente(self):
        """Abre o gerenciador de clientes em modo de seleção"""
        # Verifica se a janela de OS está aberta
        if not hasattr(self, 'nova_os_wnd') or not self.nova_os_wnd.winfo_exists():
            messagebox.showwarning("Atenção", "Abra uma OS primeiro para selecionar cliente!")
            return
        
        self.rel_clientes()

    def selecionar_veiculo(self):
        """Abre o gerenciador de clientes em modo de seleção"""
        self.rel_veiculos()

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
        
        ttk.Button(frame_botoes, text="Selecionar", 
                  command=lambda: self.selecionar_cliente_na_lista(self.rel_cli_wnd)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Editar", 
                  command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Excluir", 
                  command=self.excluir_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Fechar", 
                  command=self.rel_cli_wnd.destroy).pack(side=tk.RIGHT, padx=5)
        
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
                    modelo TEXT,
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
        
        ttk.Button(frame_botoes, text="Selecionar", 
                  command=lambda: self.selecionar_veiculo_na_lista(self.rel_veic_wnd)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Editar", 
                  command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Excluir", 
                  command=self.excluir_cliente).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_botoes, text="Fechar", 
                  command=self.rel_veic_wnd.destroy).pack(side=tk.RIGHT, padx=5)
            
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
    def salvar_peca(self, cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda):
        if not cod_in:
            messagebox.showerror("Erro", 'O campo "Código interno" é obrigatório!')
            return
            
        try:
            conn = sqlite3.connect('platycon.db')
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
                    vlr_venda TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
                
            # Inserir cliente
            cursor.execute(
                "INSERT INTO pecas (cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cod_nf, cod_in, descr, fabric, cod_pec, vlr_cust, vlr_venda)
            )
                
            conn.commit()
            conn.close()
                
            messagebox.showinfo("Sucesso", "Peça cadastrado com sucesso!")
            self.nova_peca_wnd.destroy()
                
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

    #OS
    def nova_os(self):
        """Abre janela para nova ordem de serviço"""
        self.nova_os_wnd = tk.Toplevel(self.root)
        self.nova_os_wnd.title("Nova Ordem de Serviço")
        self.nova_os_wnd.geometry("900x700")
        
        # Variáveis da OS
        self.numero_os = tk.StringVar(value=self.gerar_numero_os())
        self.data_emissao = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.cliente_nome = tk.StringVar()
        self.cliente_veiculo = tk.StringVar()
        self.servico_solicitado = tk.StringVar()
        self.observacoes = tk.StringVar()
        self.valor_total = tk.StringVar(value="R$ 0,00")
        self.itens_os = []
        
        main_frame = ttk.Frame(self.nova_os_wnd, padding="10")
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
                  command=self.selecionar_cliente).pack(anchor=tk.W, pady=2)
        ttk.Label(cliente_frame, textvariable=self.cliente_nome).pack(anchor=tk.W, fill=tk.X)
        
        ttk.Button(cliente_frame, text="Selecionar Veículo", 
                  command=self.selecionar_veiculo).pack(anchor=tk.W, pady=2)
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
                  command=self.adicionar_item).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controles_frame, text="Remover", 
                  command=self.remover_item).pack(side=tk.LEFT, padx=5)
        
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
        
        #ttk.Button(botoes_frame, text="Limpar", 
        #          command=self.limpar_os).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botoes_frame, text="Fechar", 
                  command=self.nova_os_wnd.destroy).pack(side=tk.RIGHT, padx=5)

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

        #OS
        menu_os = tk.Menu(menubar, tearoff=0)
        menu_os.add_command(label="Nova OS", command=self.nova_os)

        menubar.add_cascade(label="OS", menu=menu_os)

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
            ("📋 Ordens de serviço", self.nova_os),
            ("👥 Clientes", self.rel_clientes),
            ("🚗 Veículos", self.rel_veiculos),
            ("🔧 Estoque", self.estoque),
            ("💰 Financeiro", self.estoque),
            #("💾 Backup", self.fazer_backup)
        ]
        
        for i, (texto, comando) in enumerate(botoes):
            btn = ttk.Button(botoes_frame, text=texto, command=comando, width=20)
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Sistema pronto - Banco de dados conectado")
        self.status_label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()