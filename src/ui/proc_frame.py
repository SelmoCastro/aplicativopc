import customtkinter as ctk
from tkinter import messagebox
from src.process_manager import ProcessManager

class ProcessFrame(ctk.CTkFrame):
    def __init__(self, master, restart_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.restart_callback = restart_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = ctk.CTkLabel(self, text="Gerenciador de Processos", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, pady=(20, 10))
        
        # Admin Status / Relaunch
        is_admin = ProcessManager.is_admin()
        status_color = "green" if is_admin else "orange"
        status_text = "Modo: Administrador (Acesso Total)" if is_admin else "Modo: Usuário Limitado"
        
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=1, column=0, pady=5)
        
        ctk.CTkLabel(status_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        if not is_admin and self.restart_callback:
            ctk.CTkButton(status_frame, text="Reiniciar como Admin", fg_color="orange", hover_color="darkorange", text_color="black",
                          command=self.restart_callback).pack(side="left", padx=10)
        
        ctk.CTkButton(status_frame, text="Atualizar Lista", command=self.refresh_process_list).pack(side="left", padx=10)

        self.proc_scroll = ctk.CTkScrollableFrame(self, label_text="Processos (Ordenados por RAM)")
        self.proc_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        self.proc_status = ctk.CTkLabel(self, text="Clique em 'Finalizar' para fechar um processo.", text_color="gray")
        self.proc_status.grid(row=3, column=0, pady=10)
        
        # Load initial list
        self.refresh_process_list()

    def refresh_process_list(self):
        # Clear existing
        for widget in self.proc_scroll.winfo_children():
            widget.destroy()
            
        pm = ProcessManager()
        processes = pm.get_heavy_processes()
        
        if not processes:
            ctk.CTkLabel(self.proc_scroll, text="Nenhum processo pesado encontrado.").pack(pady=20)
            return

        for p in processes:
            # Visually distinct row
            row = ctk.CTkFrame(self.proc_scroll, fg_color=("gray80", "gray25"), corner_radius=8)
            row.pack(fill="x", padx=10, pady=5)
            
            # Info Label
            info_text = f"{p['name']} (PID: {p['pid']}) - {p['memory_str']}"
            ctk.CTkLabel(row, text=info_text, font=ctk.CTkFont(size=13, weight="normal")).pack(side="left", padx=15, pady=10)
            
            # Kill Button
            ctk.CTkButton(row, text="Finalizar", width=100, fg_color="#d63031", hover_color="#c0392b",
                          command=lambda pid=p['pid']: self.kill_proc_action(pid)).pack(side="right", padx=15, pady=10)

    def kill_proc_action(self, pid):
        if messagebox.askyesno("Confirmar", f"Deseja finalizar o processo {pid}?"):
            pm = ProcessManager()
            success, msg = pm.kill_process(pid)
            
            if success:
                messagebox.showinfo("Sucesso", msg)
                self.refresh_process_list()
            else:
                messagebox.showerror("Erro", msg)
