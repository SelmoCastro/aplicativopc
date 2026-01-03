import customtkinter as ctk
from tkinter import messagebox
import threading
import os
from src.startup_manager import StartupManager

class StartupFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.manager = StartupManager()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(top_frame, text="Gerenciador de Inicialização", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        ctk.CTkButton(top_frame, text="Atualizar Lista", width=100, command=self.refresh_list).pack(side="right")

        # List Area
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=2, column=0, pady=10)

        self.refresh_list()

    def refresh_list(self):
        # Clear existing
        for widget in self.scroll.winfo_children():
            widget.destroy()
            
        items = self.manager.get_startup_items()
        
        if not items:
            ctk.CTkLabel(self.scroll, text="Nenhum item de inicialização encontrado.").pack(pady=20)
            return

        for item in items:
            row = ctk.CTkFrame(self.scroll, fg_color=("gray85", "gray25"))
            row.pack(fill="x", padx=5, pady=5)
            
            # Icon/Name Info
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            name_lbl = ctk.CTkLabel(info_frame, text=item['name'], font=ctk.CTkFont(weight="bold"))
            name_lbl.pack(anchor="w")
            
            path_lbl = ctk.CTkLabel(info_frame, text=f"{item['source']} - {item['path']}", font=ctk.CTkFont(size=10), text_color="gray")
            path_lbl.pack(anchor="w")
            
            # Action Button
            ctk.CTkButton(row, text="Remover/Desativar", fg_color="red", hover_color="#c0392b", width=100,
                          command=lambda i=item: self.delete_item(i)).pack(side="right", padx=10, pady=10)

    def delete_item(self, item):
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja impedir que '{item['name']}' inicie com o Windows?"):
            success, msg = self.manager.delete_item(item)
            if success:
                messagebox.showinfo("Sucesso", msg)
                self.refresh_list()
            else:
                messagebox.showerror("Erro", msg)
