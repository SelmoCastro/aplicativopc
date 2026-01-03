import customtkinter as ctk
import sys
import ctypes
from tkinter import messagebox

# Imports dos Módulos de UI
from src.ui.ram_frame import RamFrame
from src.ui.scan_frame import ScanFrame
from src.ui.apps_frame import AppsFrame
from src.ui.proc_frame import ProcessFrame
from src.ui.inst_frame import InstallerFrame
from src.ui.tweaks_frame import TweaksFrame

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Otimizador de Sistema e Scanner")
        self.geometry("1100x700") 
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SysGuard", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Buttons
        self.ram_button = ctk.CTkButton(self.sidebar, text="Otimizar RAM", command=lambda: self.show_frame_by_name("ram"))
        self.ram_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.scan_button = ctk.CTkButton(self.sidebar, text="Analisador de Disco", command=lambda: self.show_frame_by_name("scan"))
        self.scan_button.grid(row=2, column=0, padx=20, pady=10)

        self.apps_button = ctk.CTkButton(self.sidebar, text="Removedor de Apps", command=lambda: self.show_frame_by_name("apps"))
        self.apps_button.grid(row=3, column=0, padx=20, pady=10)

        self.proc_button = ctk.CTkButton(self.sidebar, text="Gerenciador Processos", command=lambda: self.show_frame_by_name("proc"))
        self.proc_button.grid(row=4, column=0, padx=20, pady=10)

        self.inst_button = ctk.CTkButton(self.sidebar, text="Instalar Softwares", command=lambda: self.show_frame_by_name("inst"))
        self.inst_button.grid(row=5, column=0, padx=20, pady=10)

        self.tweaks_button = ctk.CTkButton(self.sidebar, text="Tweaks do Sistema", fg_color="#9b59b6", hover_color="#8e44ad",
                                           command=lambda: self.show_frame_by_name("tweaks"))
        self.tweaks_button.grid(row=6, column=0, padx=20, pady=10)

        # Main Content Area
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        # Initialize Frames
        # Note: We pass 'self.restart_as_admin' to ProcessFrame so it can call it
        self.ram_frame = RamFrame(self.main_area)
        self.scan_frame = ScanFrame(self.main_area)
        self.apps_frame = AppsFrame(self.main_area)
        # Fix: ProcessFrame constructor expects 'restart_callback'
        self.proc_frame = ProcessFrame(self.main_area, restart_callback=self.restart_as_admin)
        self.inst_frame = InstallerFrame(self.main_area)
        self.tweaks_frame = TweaksFrame(self.main_area)

        # Start with RAM frame
        self.show_frame_by_name("ram")

    def show_frame_by_name(self, name):
        # Hide all
        self.ram_frame.grid_forget()
        self.scan_frame.grid_forget()
        self.apps_frame.grid_forget()
        self.proc_frame.grid_forget()
        self.inst_frame.grid_forget()
        self.tweaks_frame.grid_forget()
        
        # Show target
        if name == "ram":
            self.ram_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.ram_button)
        elif name == "scan":
            self.scan_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.scan_button)
        elif name == "apps":
            self.apps_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.apps_button)
        elif name == "proc":
            self.proc_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.proc_button)
        elif name == "inst":
            self.inst_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.inst_button)
        elif name == "tweaks":
            self.tweaks_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.tweaks_button)

    def highlight_active_button(self, active_btn):
        # Reset all buttons to default
        buttons = [self.ram_button, self.scan_button, self.apps_button, self.proc_button, self.inst_button, self.tweaks_button]
        for btn in buttons:
            if btn == self.tweaks_button:
                 btn.configure(fg_color="#9b59b6") # Default purple
            else:
                 btn.configure(fg_color=["#3a7ebf", "#1f538d"])
            
        # Highlight active
        active_btn.configure(fg_color=["#2cc985", "#2fa572"])

    def restart_as_admin(self):
        if ctypes.windll.shell32.IsUserAnAdmin():
            return
        
        try:
             ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
             self.destroy() 
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao reiniciar como admin: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
