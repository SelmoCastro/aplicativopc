import customtkinter as ctk
from src.game_optimizer import GameOptimizer
import threading

class GameModeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.optimizer = GameOptimizer()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Centered Container
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(center_frame, text="GAME MODE 🎮", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(center_frame, text="Prepara o PC para máxima performance em jogos.", font=ctk.CTkFont(size=14)).pack(pady=5)
        
        # Big Boost Button
        self.boost_btn = ctk.CTkButton(center_frame, text="ATIVAR BOOST", 
                                       font=ctk.CTkFont(size=24, weight="bold"),
                                       fg_color="#e74c3c", hover_color="#c0392b",
                                       height=80, corner_radius=20,
                                       command=self.run_boost)
        self.boost_btn.pack(pady=40, fill="x", padx=40)
        
        # Status Log
        self.log_box = ctk.CTkTextbox(center_frame, height=150)
        self.log_box.pack(pady=20, fill="x", padx=40)
        self.log_box.insert("0.0", "Aguardando ativação...")
        self.log_box.configure(state="disabled")
        
        # Restore Button
        ctk.CTkButton(center_frame, text="Restaurar Padrão (Sair do Jogo)", 
                      fg_color="transparent", border_width=1,
                      command=self.restore).pack(pady=10)

    def run_boost(self):
        self.boost_btn.configure(state="disabled", text="OTIMIZANDO...")
        
        def _target():
            log = self.optimizer.optimize_for_gaming()
            self.after(0, lambda: self.finish_boost(log))
            
        threading.Thread(target=_target, daemon=True).start()

    def finish_boost(self, log):
        self.boost_btn.configure(state="normal", text="BOOST ATIVADO! 🚀", fg_color="#27ae60", hover_color="#2ecc71")
        
        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")
        self.log_box.insert("0.0", log)
        self.log_box.configure(state="disabled")

    def restore(self):
        msg = self.optimizer.restore_default()
        self.boost_btn.configure(text="ATIVAR BOOST", fg_color="#e74c3c", hover_color="#c0392b")
        
        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")
        self.log_box.insert("0.0", msg)
        self.log_box.configure(state="disabled")
