import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import openpyxl

class Main:
    def __init__(self, root):
        self.root = root
        self.root.title("Scovillain - Importador XLSX")
        self.root.geometry("1000x850")

        self.xlsx_path = tk.StringVar()

        self.criar_widgets
        
        try:
            root.iconbitmap("22.ico")
        except:
            pass

    def browse_xlsx(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            self.xlsx_path.set(filename)
            base = os.path.splitext(filename)[0]
            self.ofx_path.set(base + ".ofx")

    def criar_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Aba XLSX
        tab_xlsx_ofx = ttk.Frame()
        
        # Widgets XLSX
        ttk.Label(tab_xlsx_ofx, text="Arquivo XLSX:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(tab_xlsx_ofx, textvariable=self.xlsx_path, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(tab_xlsx_ofx, text="Procurar", command=self.browse_xlsx).grid(row=0, column=2, pady=5)