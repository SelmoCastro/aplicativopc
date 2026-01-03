import customtkinter as ctk
import threading
import os
from tkinter import messagebox, filedialog
from src.disk_analyzer import DiskAnalyzer

class ScanFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) 
        
        self.label = ctk.CTkLabel(self, text="Analisador de Disco (Folders)", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)
        
        # Controls
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, pady=10)
        
        self.path_entry = ctk.CTkEntry(ctrl_frame, width=300, placeholder_text="C:\\")
        self.path_entry.pack(side="left", padx=10)
        self.path_entry.insert(0, "C:\\")

        btn_browse = ctk.CTkButton(ctrl_frame, text="...", width=40, command=self.browse_folder)
        btn_browse.pack(side="left", padx=5)
        
        self.scan_btn = ctk.CTkButton(ctrl_frame, text="Analisar Pasta", command=self.scan_action)
        self.scan_btn.pack(side="left", padx=10)
        
        # Results area
        self.results_scroll = ctk.CTkScrollableFrame(self, label_text="Pastas e Arquivos (Ordenados por Tamanho)")
        self.results_scroll.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Selecione uma pasta para analisar.", text_color="gray")
        self.status_label.grid(row=4, column=0, pady=10)

        self.analyzer = DiskAnalyzer()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def scan_action(self):
        root_path = self.path_entry.get()
        if not os.path.exists(root_path):
            messagebox.showerror("Erro", "Caminho não existe.")
            return

        self.status_label.configure(text=f"Analisando {root_path}... Isso pode demorar.", text_color="yellow")
        self.scan_btn.configure(state="disabled")
        
        # Clear UI
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        def run():
            results = self.analyzer.scan_directory_structure(root_path)
            self.after(0, lambda: self.display_results(results))

        threading.Thread(target=run, daemon=True).start()

    def display_results(self, results):
        self.scan_btn.configure(state="normal")
        self.status_label.configure(text=f"Análise concluída. {len(results)} itens encontrados.", text_color="green")

        if not results:
            ctk.CTkLabel(self.results_scroll, text="A pasta está vazia.").pack(pady=20)
            return

        # Max size for progress bar calculation
        max_size = results[0]['size'] if results else 1

        for item in results:
            # Row
            row = ctk.CTkFrame(self.results_scroll, fg_color=("gray85", "gray25"), corner_radius=6)
            row.pack(fill="x", padx=5, pady=5)
            
            # Icon/Type
            icon = "📁" if item['type'] == 'folder' else "📄"
            
            # Left side: Name and visual bar
            left_frame = ctk.CTkFrame(row, fg_color="transparent")
            left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            ctk.CTkLabel(left_frame, text=f"{icon} {item['name']}", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            
            # Progress bar relative to biggest folder
            progress = item['size'] / max_size
            pb = ctk.CTkProgressBar(left_frame, height=8)
            pb.pack(fill="x", pady=(5,0))
            pb.set(progress)
            
            # Right side: Size and Delete
            right_frame = ctk.CTkFrame(row, fg_color="transparent")
            right_frame.pack(side="right", padx=10)
            
            ctk.CTkLabel(right_frame, text=item['size_str'], font=ctk.CTkFont(family="Consolas")).pack(anchor="e")
            
            # Delete Button
            ctk.CTkButton(right_frame, text="Excluir", width=60, fg_color="red", hover_color="#8b0000",
                          command=lambda p=item['path']: self.delete_item_action(p)).pack(anchor="e", pady=5)

    def delete_item_action(self, path):
        # Safety check for critical paths
        lower_path = path.lower()
        if "windows" in lower_path or "program files" in lower_path:
            if not messagebox.askyesno("ALERTA DE SEGURANÇA", f"Você está tentando deletar uma pasta de sistema:\n{path}\n\nIsso pode QUEBRAR o Windows. Tem certeza absoluta?"):
                return

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja apagar permanentemente:\n{path}?"):
            success, msg = self.analyzer.delete_item(path)
            if success:
                messagebox.showinfo("Sucesso", msg)
                # Refresh list (re-scan)
                self.scan_action()
            else:
                messagebox.showerror("Erro", msg)
