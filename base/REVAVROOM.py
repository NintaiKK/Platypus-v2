import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class AppControleCaminhoes:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Caminhões - Mecânica")
        self.root.geometry("900x600")
        
        # Dados
        self.caminhoes = []
        self.carregar_dados()
        
        # Interface
        self.criar_widgets()
        
    def carregar_dados(self):
        if os.path.exists("caminhoes.json"):
            try:
                with open("caminhoes.json", "r") as f:
                    self.caminhoes = json.load(f)
            except:
                self.caminhoes = []
    
    def salvar_dados(self):
        with open("caminhoes.json", "w") as f:
            json.dump(self.caminhoes, f, indent=4)
    
    def criar_widgets(self):
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(self.root, text="Cadastro de Caminhão", padding=10)
        frame_cadastro.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Campos do formulário
        ttk.Label(frame_cadastro, text="Placa:").grid(row=0, column=0, sticky="w")
        self.placa_entry = ttk.Entry(frame_cadastro)
        self.placa_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame_cadastro, text="KM:").grid(row=1, column=0, sticky="w")
        self.km_entry = ttk.Entry(frame_cadastro)
        self.km_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame_cadastro, text="Peças Utilizadas:").grid(row=2, column=0, sticky="w")
        self.pecas_text = tk.Text(frame_cadastro, height=4, width=30)
        self.pecas_text.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame_cadastro, text="Serviços Realizados:").grid(row=3, column=0, sticky="w")
        self.servicos_text = tk.Text(frame_cadastro, height=4, width=30)
        self.servicos_text.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(frame_cadastro, text="Observações:").grid(row=4, column=0, sticky="w")
        self.obs_text = tk.Text(frame_cadastro, height=4, width=30)
        self.obs_text.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        
        # Botões do formulário
        botoes_frame = ttk.Frame(frame_cadastro)
        botoes_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(botoes_frame, text="Adicionar", command=self.adicionar_caminhao).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Limpar", command=self.limpar_campos).pack(side="left", padx=5)
        
        # Frame de listagem
        frame_lista = ttk.LabelFrame(self.root, text="Caminhões Cadastrados", padding=10)
        frame_lista.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # Treeview para exibir os caminhões
        colunas = ("Placa", "KM", "Peças", "Serviços", "Obs")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=20)
        
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Botões de ação
        botoes_acao_frame = ttk.Frame(frame_lista)
        botoes_acao_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(botoes_acao_frame, text="Editar", command=self.editar_caminhao).pack(side="left", padx=5)
        ttk.Button(botoes_acao_frame, text="Excluir", command=self.excluir_caminhao).pack(side="left", padx=5)
        ttk.Button(botoes_acao_frame, text="Atualizar Lista", command=self.atualizar_lista).pack(side="left", padx=5)
        
        # Frame de busca
        frame_busca = ttk.LabelFrame(self.root, text="Buscar Caminhão", padding=10)
        frame_busca.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Label(frame_busca, text="Buscar por Placa:").pack(side="left")
        self.busca_entry = ttk.Entry(frame_busca, width=30)
        self.busca_entry.pack(side="left", padx=5)
        ttk.Button(frame_busca, text="Buscar", command=self.buscar_caminhao).pack(side="left", padx=5)
        
        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)
        
        # Atualizar lista inicial
        self.atualizar_lista()
    
    def adicionar_caminhao(self):
        placa = self.placa_entry.get().strip().upper()
        km = self.km_entry.get().strip()
        pecas = self.pecas_text.get("1.0", tk.END).strip()
        servicos = self.servicos_text.get("1.0", tk.END).strip()
        obs = self.obs_text.get("1.0", tk.END).strip()
        
        if not placa:
            messagebox.showerror("Erro", "Por favor, informe a placa do caminhão.")
            return
        
        # Verificar se placa já existe
        for caminhao in self.caminhoes:
            if caminhao["placa"] == placa:
                messagebox.showerror("Erro", f"Caminhão com placa {placa} já cadastrado.")
                return
        
        novo_caminhao = {
            "placa": placa,
            "km": km,
            "pecas": pecas,
            "servicos": servicos,
            "obs": obs
        }
        
        self.caminhoes.append(novo_caminhao)
        self.salvar_dados()
        self.atualizar_lista()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Caminhão cadastrado com sucesso!")
    
    def limpar_campos(self):
        self.placa_entry.delete(0, tk.END)
        self.km_entry.delete(0, tk.END)
        self.pecas_text.delete("1.0", tk.END)
        self.servicos_text.delete("1.0", tk.END)
        self.obs_text.delete("1.0", tk.END)
        self.placa_entry.focus_set()
    
    def atualizar_lista(self):
        # Limpar a treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar os itens
        for caminhao in self.caminhoes:
            # Limitar o tamanho do texto para exibição
            pecas = (caminhao["pecas"][:30] + "...") if len(caminhao["pecas"]) > 30 else caminhao["pecas"]
            servicos = (caminhao["servicos"][:30] + "...") if len(caminhao["servicos"]) > 30 else caminhao["servicos"]
            obs = (caminhao["obs"][:30] + "...") if len(caminhao["obs"]) > 30 else caminhao["obs"]
            
            self.tree.insert("", tk.END, values=(
                caminhao["placa"],
                caminhao["km"],
                pecas,
                servicos,
                obs
            ))
    
    def editar_caminhao(self):
        item_selecionado = self.tree.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Por favor, selecione um caminhão para editar.")
            return
        
        # Obter placa do item selecionado
        placa = self.tree.item(item_selecionado)["values"][0]
        
        # Encontrar o caminhão na lista
        for i, caminhao in enumerate(self.caminhoes):
            if caminhao["placa"] == placa:
                # Preencher os campos com os dados existentes
                self.limpar_campos()
                self.placa_entry.insert(0, caminhao["placa"])
                self.km_entry.insert(0, caminhao["km"])
                self.pecas_text.insert("1.0", caminhao["pecas"])
                self.servicos_text.insert("1.0", caminhao["servicos"])
                self.obs_text.insert("1.0", caminhao["obs"])
                
                # Remover o item antigo
                self.caminhoes.pop(i)
                self.tree.delete(item_selecionado)
                break
    
    def excluir_caminhao(self):
        item_selecionado = self.tree.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Por favor, selecione um caminhão para excluir.")
            return
        
        # Confirmar exclusão
        placa = self.tree.item(item_selecionado)["values"][0]
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o caminhão {placa}?"):
            # Encontrar e remover o caminhão
            for i, caminhao in enumerate(self.caminhoes):
                if caminhao["placa"] == placa:
                    self.caminhoes.pop(i)
                    break
            
            self.salvar_dados()
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Caminhão excluído com sucesso!")
    
    def buscar_caminhao(self):
        termo = self.busca_entry.get().strip().upper()
        if not termo:
            self.atualizar_lista()
            return
        
        # Limpar a treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar correspondências
        for caminhao in self.caminhoes:
            if termo in caminhao["placa"]:
                pecas = (caminhao["pecas"][:30] + "...") if len(caminhao["pecas"]) > 30 else caminhao["pecas"]
                servicos = (caminhao["servicos"][:30] + "...") if len(caminhao["servicos"]) > 30 else caminhao["servicos"]
                obs = (caminhao["obs"][:30] + "...") if len(caminhao["obs"]) > 30 else caminhao["obs"]
                
                self.tree.insert("", tk.END, values=(
                    caminhao["placa"],
                    caminhao["km"],
                    pecas,
                    servicos,
                    obs
                ))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppControleCaminhoes(root)
    root.mainloop()