import customtkinter as ctk
import threading
from tkinter import messagebox
from src.bloatware_remover import BloatwareRemover

class AppsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = ctk.CTkLabel(self, text="Remover Apps do Windows (Bloatware)", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)

        # Control Frame
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, pady=10)

        ctk.CTkButton(ctrl_frame, text="Marcar Todos", width=100, command=self.select_all_apps).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frame, text="Desmarcar Todos", width=100, command=self.deselect_all_apps).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frame, text="Desinstalar Selecionados", fg_color="red", hover_color="darkred", command=self.uninstall_apps_action).pack(side="left", padx=20)
        
        # Reload Button (Useful if list failed or want to refresh)
        ctk.CTkButton(ctrl_frame, text="Recarregar Lista", width=100, command=self.load_apps_async).pack(side="left", padx=5)

        # Apps Grid Scrollable
        self.apps_scroll = ctk.CTkScrollableFrame(self, label_text="Selecione os Apps para Remover")
        self.apps_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 5))
        
        self.apps_scroll.grid_columnconfigure(0, weight=1)
        self.apps_scroll.grid_columnconfigure(1, weight=1)

        # Log / Terminal Display
        self.log_textbox = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        self.log_textbox.insert("0.0", "Aguardando carregamento da lista de apps...\n")
        self.log_textbox.configure(state="disabled")

        self.apps_status = ctk.CTkLabel(self, text="Selecione com cuidado. A remoção é permanente.", text_color="gray")
        self.apps_status.grid(row=4, column=0, pady=5)

        self.remover = BloatwareRemover()
        self.app_checkboxes = {}
        
        # Load apps asynchronously to avoid freezing UI on creating this frame
        self.after(500, self.load_apps_async)

    def load_apps_async(self):
        self.append_log("Carregando lista de apps instalados (pode demorar um pouco)...")
        # Clear existing
        for widget in self.apps_scroll.winfo_children():
            widget.destroy()
        self.app_checkboxes = {}

        def run():
            try:
                # We want only installed apps
                apps = self.remover.get_installed_apps()
            except Exception as e:
                apps = self.remover.get_supported_apps() # Fallback
            
            self.after(0, lambda: self.display_apps(apps))

        threading.Thread(target=run, daemon=True).start()

    def display_apps(self, apps):
        self.append_log(f"Lista carregada. {len(apps)} apps encontrados.")
        for i, app_name in enumerate(apps):
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(self.apps_scroll, text=app_name, variable=var)
            chk.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=5)
            self.app_checkboxes[app_name] = var

    def select_all_apps(self):
        for var in self.app_checkboxes.values():
            var.set(True)

    def deselect_all_apps(self):
        for var in self.app_checkboxes.values():
            var.set(False)

    def append_log(self, msg):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def uninstall_apps_action(self):
        to_remove = [name for name, var in self.app_checkboxes.items() if var.get()]
        
        if not to_remove:
            messagebox.showinfo("Aviso", "Nenhum aplicativo selecionado.")
            return

        conf_msg = f"Você selecionou {len(to_remove)} aplicativos para REMOVER.\n\nEssa ação tentará desinstalar os apps via PowerShell.\n\nDeseja continuar?"
        if not messagebox.askyesno("Confirmar Remoção", conf_msg):
            return

        self.apps_status.configure(text="Removendo aplicativos... Por favor aguarde.", text_color="yellow")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
        def run():
            def log_callback(msg):
                print(msg) 
                # Schedule GUI update
                self.after(0, lambda: self.append_log(msg))
            
            self.after(0, lambda: self.append_log("Iniciando remoção..."))
            success, fail = self.remover.remove_apps(to_remove, log_callback)
            
            msg = f"Concluído.\nSucesso: {success}\nFalhas: {fail}"
            self.after(0, lambda: self.finish_uninstall(msg, fail > 0))

        threading.Thread(target=run, daemon=True).start()

    def finish_uninstall(self, msg, has_errors):
        self.apps_status.configure(text=msg, text_color="orange" if has_errors else "green")
        messagebox.showinfo("Resultado", msg)
