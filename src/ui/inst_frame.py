import customtkinter as ctk
import threading
from tkinter import messagebox
from src.software_installer import SoftwareInstaller

class InstallerFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="Instalador de Softwares (Winget)", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        ctk.CTkButton(header, text="Instalar Selecionados", fg_color="green", hover_color="darkgreen", 
                      command=self.install_softwares_action).pack(side="right")

        # Tabview for Categories
        self.inst_tabs = ctk.CTkTabview(self)
        self.inst_tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.installer = SoftwareInstaller()
        catalog = self.installer.get_catalog()
        self.soft_checkboxes = {} # Map "Category|Name" -> {id: id, var: BooleanVar}

        for category, apps in catalog.items():
            self.inst_tabs.add(category)
            tab_frame = self.inst_tabs.tab(category)
            
            # Simple Grid inside Tab
            tab_frame.grid_columnconfigure(0, weight=1)
            tab_frame.grid_columnconfigure(1, weight=1)

            for i, (app_name, app_id) in enumerate(apps.items()):
                var = ctk.BooleanVar()
                chk = ctk.CTkCheckBox(tab_frame, text=app_name, variable=var)
                chk.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=10)
                
                key = f"{category}|{app_name}"
                self.soft_checkboxes[key] = {"id": app_id, "var": var}

        # Shared Log Area (re-using a new log box for this frame)
        self.inst_log = ctk.CTkTextbox(self, height=120, font=ctk.CTkFont(family="Consolas", size=12))
        self.inst_log.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.inst_log.insert("0.0", "Terminal de Instalação...\n")
        self.inst_log.configure(state="disabled")

        if not self.installer.check_winget_availability():
            self.inst_log.configure(state="normal")
            self.inst_log.insert("end", "[AVISO] 'winget' não encontrado no PATH. Instalações podem falhar.\n")
            self.inst_log.configure(state="disabled")

    def append_inst_log(self, msg):
        self.inst_log.configure(state="normal")
        self.inst_log.insert("end", msg + "\n")
        self.inst_log.see("end")
        self.inst_log.configure(state="disabled")

    def install_softwares_action(self):
        to_install = []
        for key, data in self.soft_checkboxes.items():
            if data["var"].get():
                to_install.append(data["id"])
        
        if not to_install:
            messagebox.showinfo("Aviso", "Nenhum software selecionado.")
            return

        conf_msg = f"Deseja instalar {len(to_install)} softwares?\nIsso pode levar alguns minutos."
        if not messagebox.askyesno("Confirmar Instalação", conf_msg):
            return

        self.inst_log.configure(state="normal")
        self.inst_log.delete("1.0", "end")
        self.inst_log.configure(state="disabled")
        
        def run():
            def log_callback(msg):
                print(msg) 
                self.after(0, lambda: self.append_inst_log(msg))
            
            self.after(0, lambda: self.append_inst_log(f"Iniciando instalação de {len(to_install)} itens..."))
            success, fail = self.installer.install_apps(to_install, log_callback)
            
            msg = f"Concluído.\nSucesso: {success}\nFalhas: {fail}"
            self.after(0, lambda: messagebox.showinfo("Fim da Instalação", msg))

        threading.Thread(target=run, daemon=True).start()
