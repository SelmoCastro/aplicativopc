import customtkinter as ctk
from tkinter import messagebox
import threading
from src.temp_cleaner import TempCleaner

class TempCleanFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.cleaner = TempCleaner()
        self.checkboxes = {}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Spacer

        # Header
        ctk.CTkLabel(self, text="Limpeza de Arquivos Temporários", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=20)
        
        # Options Frame
        self.opts_frame = ctk.CTkScrollableFrame(self)
        self.opts_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.opts_frame.grid_columnconfigure(1, weight=1)
        
        # Status
        self.status_label = ctk.CTkLabel(self, text="Escaneando...", text_color="yellow")
        self.status_label.grid(row=3, column=0, pady=10)
        
        # Action
        self.clean_btn = ctk.CTkButton(self, text="Limpar Selecionados", command=self.run_clean, state="disabled", fg_color="green", hover_color="darkgreen")
        self.clean_btn.grid(row=4, column=0, pady=20)

        # Initial Scan
        self.scan()

    def scan(self):
        def _scan():
            data = self.cleaner.scan_junk()
            self.after(0, lambda: self.show_options(data))
            
        threading.Thread(target=_scan, daemon=True).start()

    def show_options(self, data):
        self.status_label.configure(text="Seleção concluída.", text_color="white")
        self.clean_btn.configure(state="normal")
        
        # Clear
        for w in self.opts_frame.winfo_children():
            w.destroy()
            
        self.items_data = data
        
        row = 0
        total_size = 0
        for key, info in data.items():
            size_str = self.cleaner.format_bytes(info['size']) if info['size'] > 0 else "Vazio / 0 KB"
            total_size += info['size']
            
            # Checkbox
            var = ctk.BooleanVar(value=True) # Default checked
            chk = ctk.CTkCheckBox(self.opts_frame, text=info['name'], variable=var, font=ctk.CTkFont(size=14, weight="bold"))
            chk.grid(row=row, column=0, sticky="w", padx=10, pady=10)
            
            # Size Label
            ctk.CTkLabel(self.opts_frame, text=size_str).grid(row=row, column=1, sticky="e", padx=10)
            
            self.checkboxes[key] = var
            row += 1
            
        self.total_lbl = ctk.CTkLabel(self.opts_frame, text=f"Total Encontrado: {self.cleaner.format_bytes(total_size)}", font=ctk.CTkFont(weight="bold"))
        self.total_lbl.grid(row=row, column=0, columnspan=2, pady=20)

    def run_clean(self):
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir permanentemente os itens selecionados?"):
            return
            
        self.status_label.configure(text="Limpando...", text_color="yellow")
        self.clean_btn.configure(state="disabled")
        
        selected_keys = [k for k, v in self.checkboxes.items() if v.get()]
        
        def _clean():
            total_cleared = 0
            msg = ""
            
            for key in selected_keys:
                if key == 'recycle':
                    success, m = self.cleaner.empty_recycle_bin()
                    msg += f"Lixeira: {m}\n"
                else:
                    path = self.items_data[key]['path']
                    cleared, errors = self.cleaner.clean_folder(path)
                    total_cleared += cleared
                    msg += f"{self.items_data[key]['name']}: -{self.cleaner.format_bytes(cleared)} ({errors} ignorados)\n"
            
            self.after(0, lambda: self.finish_clean(msg, total_cleared))

        threading.Thread(target=_clean, daemon=True).start()

    def finish_clean(self, log_msg, total_bytes):
        final_msg = f"Limpeza Concluída!\nEspaço recuperado: {self.cleaner.format_bytes(total_bytes)}\n\nDetalhes:\n{log_msg}"
        messagebox.showinfo("Relatório", final_msg)
        self.status_label.configure(text="Pronto.", text_color="green")
        self.scan() # Refresh
