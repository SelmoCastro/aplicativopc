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
        # Default to User directory for safer/more relevant scanning
        default_path = os.path.expanduser("~")
        self.path_entry.insert(0, default_path)

        btn_browse = ctk.CTkButton(ctrl_frame, text="...", width=40, command=self.browse_folder)
        btn_browse.pack(side="left", padx=5)
        
        self.scan_btn = ctk.CTkButton(ctrl_frame, text="Analisar Pasta", command=self.scan_action)
        self.scan_btn.pack(side="left", padx=10)

        # Sort Options
        self.sort_var = ctk.StringVar(value="Tamanho (Maior > Menor)")
        self.sort_box = ctk.CTkComboBox(ctrl_frame, values=["Tamanho (Maior > Menor)", "Data (Mais Antigo)", "Data (Mais Novo)"],
                                        variable=self.sort_var, width=180, command=self.resort_results)
        self.sort_box.pack(side="left", padx=10)
        
        self.bulk_btn = ctk.CTkButton(ctrl_frame, text="🗑️ Limpar Antigos", fg_color="#e74c3c", hover_color="#c0392b", width=120, command=self.clean_old_items)
        self.bulk_btn.pack(side="left", padx=5)
        
        self.current_results = [] # Store results for resorting
        
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
            self.current_results = results
            self.after(0, lambda: self.resort_results(None))

        threading.Thread(target=run, daemon=True).start()

    def resort_results(self, _):
        if not self.current_results: return
        
        mode = self.sort_var.get()
        if "Tamanho" in mode:
            self.current_results.sort(key=lambda x: x['size'], reverse=True)
        elif "Antigo" in mode:
             self.current_results.sort(key=lambda x: x.get('mtime', 0))
        elif "Novo" in mode:
             self.current_results.sort(key=lambda x: x.get('mtime', 0), reverse=True)
             
        self.display_results(self.current_results)

    def display_results(self, results):
        self.scan_btn.configure(state="normal")
        self.status_label.configure(text=f"Análise concluída. {len(results)} itens encontrados.", text_color="green")

        if not results:
            ctk.CTkLabel(self.results_scroll, text="A pasta está vazia.").pack(pady=20)
            return

        # Max size for progress bar calculation
        max_size = results[0]['size'] if results else 1
        
        # Limit display to avoid UI freezing with thousands of widgets
        MAX_DISPLAY = 150
        display_items = results[:MAX_DISPLAY]
        
        if len(results) > MAX_DISPLAY:
             ctk.CTkLabel(self.results_scroll, text=f"⚠️ Exibindo os top {MAX_DISPLAY} itens (de {len(results)}) para evitar travamentos.", text_color="orange").pack(pady=5)

        for item in display_items:
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
            
            # Date str
            import datetime
            ts = item.get('mtime', 0)
            date_str = datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y')
            
            ctk.CTkLabel(right_frame, text=date_str, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="e")
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
                self.scan_action()
            else:
                messagebox.showerror("Erro", msg)

    def clean_old_items(self):
        import datetime
        import tkinter as tk
        
        if not self.current_results:
             messagebox.showwarning("Aviso", "Faça uma análise primeiro.")
             return

        # Custom Dialog for better visibility
        dialog = ctk.CTkToplevel(self)
        dialog.title("Limpeza por Data")
        dialog.geometry("400x200")
        dialog.transient(self) 
        dialog.lift()
        dialog.focus_force()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text="Digite a data limite (DD/MM/AAAA):\n(Tudo ANTES desta data será APAGADO)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        
        date_entry = ctk.CTkEntry(dialog, width=150, justify="center")
        date_entry.pack(pady=10)
        
        # Default to 6 months ago
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        date_entry.insert(0, six_months_ago.strftime("%d/%m/%Y"))
        
        selected_date = [None] # Mutable container to capture result

        def on_confirm():
            val = date_entry.get()
            selected_date[0] = val
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Confirmar", command=on_confirm, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)
        
        dialog.update() # Force render to prevent "black window" glitch
        dialog.grab_set() # Modal behavior
        self.wait_window(dialog) # Block until closed
        
        date_str = selected_date[0]
        if not date_str:
            return
            
        try:
            cutoff_date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
            cutoff_ts = cutoff_date.timestamp()
        except ValueError:
            messagebox.showerror("Erro", "Formato inválido! Use DD/MM/AAAA (ex: 31/12/2023)")
            return
            
        # Filter items
        to_delete = []
        total_size = 0
        
        for item in self.current_results:
            if item.get('mtime', 0) < cutoff_ts:
                to_delete.append(item)
                total_size += item['size']
                
        if not to_delete:
            messagebox.showinfo("Info", f"Nenhum item encontrado anterior a {date_str}.")
            return
            
        # Confirmation
        size_str = self.analyzer.format_bytes(total_size)
        confirm = messagebox.askyesno("CONFIRMAÇÃO DE LIMPEZA", 
                                      f"Encontrados {len(to_delete)} itens antigos ({size_str}).\n\n"
                                      f"Isso apagará TUDO modificado antes de {date_str}.\n"
                                      "Deseja continuar?")
        
        if confirm:
            deleted_count = 0
            errors = 0
            
            self.status_label.configure(text=f"Deletando {len(to_delete)} itens...", text_color="yellow")
            self.update_idletasks()
            
            for item in to_delete:
                ok, _ = self.analyzer.delete_item(item['path'])
                if ok:
                    deleted_count += 1
                else:
                    errors += 1
            
            messagebox.showinfo("Limpeza Concluída", f"{deleted_count} itens apagados.\n{errors} erros.")
            self.scan_action()
