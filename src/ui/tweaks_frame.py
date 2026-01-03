import customtkinter as ctk
from tkinter import messagebox
import threading
from src.system_tweaks import SystemTweaks

class TweaksFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(self, text="Otimizações do Sistema (Tweaks)", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, columnspan=2, pady=20)
        
        self.tweaks = SystemTweaks()
        
        # --- Performance Section ---
        perf_frame = ctk.CTkFrame(self)
        perf_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(perf_frame, text="⚡ Performance", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        ctk.CTkButton(perf_frame, text="Ativar 'Desempenho Máximo'", 
                      command=lambda: self.run_tweak(self.tweaks.enable_ultimate_performance)
                      ).pack(pady=10, padx=20, fill="x")
                      
        ctk.CTkLabel(perf_frame, text="Libera o plano de energia oculto\n'Ultimate Performance' para latência zero.", 
                     text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=5)

        # --- Usability Section ---
        usage_frame = ctk.CTkFrame(self)
        usage_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(usage_frame, text="🛠️ Utilidade & Visual", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        ctk.CTkButton(usage_frame, text="Restaurar Visualizador de Fotos Clássico", 
                      command=lambda: self.run_tweak(self.tweaks.restore_classic_photo_viewer)
                      ).pack(pady=(10, 5), padx=20, fill="x")
        
        ctk.CTkLabel(usage_frame, text="Traz de volta o visualizador rápido\ndo Windows 7 para abrir imagens.", 
                     text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=(0, 10))

        ctk.CTkButton(usage_frame, text="Menu de Contexto Clássico (Win 11)", 
                      fg_color="#e67e22", hover_color="#d35400",
                      command=lambda: self.run_tweak(self.tweaks.restore_classic_context_menu)
                      ).pack(pady=(10, 5), padx=20, fill="x")
        
        ctk.CTkLabel(usage_frame, text="Remove o menu 'Mostrar mais opções'\ne mostra tudo direto (Requer Restart Explorer).", 
                     text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=(0, 10))

                     
        # --- Privacy Section ---
        priv_frame = ctk.CTkFrame(self)
        priv_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(priv_frame, text="🛡️ Privacidade", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        ctk.CTkButton(priv_frame, text="Desativar Telemetria e Bing Search", fg_color="#d63031", hover_color="#c0392b",
                      command=lambda: self.run_tweak(self.tweaks.remove_telemetry)
                      ).pack(pady=10, padx=40, fill="x")

        # --- Appearance Section ---
        theme_frame = ctk.CTkFrame(self)
        theme_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(theme_frame, text="🎨 Aparência", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        btn_row = ctk.CTkFrame(theme_frame, fg_color="transparent")
        btn_row.pack(pady=10)
        
        ctk.CTkButton(btn_row, text="Escuro (Dark)", width=100, command=lambda: ctk.set_appearance_mode("Dark")).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Claro (Light)", width=100, command=lambda: ctk.set_appearance_mode("Light")).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Sistema", width=100, command=lambda: ctk.set_appearance_mode("System")).pack(side="left", padx=10)

    
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(weight="bold"))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=20)

    def run_tweak(self, func):
        self.status_label.configure(text="Aplicando...", text_color="yellow")
        
        def run():
            success, msg = func()
            color = "green" if success else "red"
            self.after(0, lambda: self.finish_tweak(msg, color))
            
        threading.Thread(target=run, daemon=True).start()
        
    def finish_tweak(self, msg, color):
        self.status_label.configure(text=msg, text_color=color)
        messagebox.showinfo("Resultado", msg)
