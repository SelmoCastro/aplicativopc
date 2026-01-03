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
from src.ui.startup_frame import StartupFrame
from src.ui.temp_clean_frame import TempCleanFrame
from src.ui.dashboard_frame import DashboardFrame
from src.ui.game_frame import GameModeFrame
from src.config_manager import ConfigManager
from src.automation_service import AutomationService

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
        
        # Services
        self.app_config = ConfigManager()
        self.automation = AutomationService(self.app_config)
        self.automation.start()

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SysGuard", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Buttons
        self.dash_button = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_frame_by_name("dashboard"))
        self.dash_button.grid(row=1, column=0, padx=20, pady=10)

        self.ram_button = ctk.CTkButton(self.sidebar, text="Otimizar RAM", command=lambda: self.show_frame_by_name("ram"))
        self.ram_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.scan_button = ctk.CTkButton(self.sidebar, text="Analisador de Disco", command=lambda: self.show_frame_by_name("scan"))
        self.scan_button.grid(row=3, column=0, padx=20, pady=10)

        self.apps_button = ctk.CTkButton(self.sidebar, text="Removedor de Apps", command=lambda: self.show_frame_by_name("apps"))
        self.apps_button.grid(row=4, column=0, padx=20, pady=10)

        self.proc_button = ctk.CTkButton(self.sidebar, text="Gerenciador Processos", command=lambda: self.show_frame_by_name("proc"))
        self.proc_button.grid(row=5, column=0, padx=20, pady=10)

        self.inst_button = ctk.CTkButton(self.sidebar, text="Instalar Softwares", command=lambda: self.show_frame_by_name("inst"))
        self.inst_button.grid(row=6, column=0, padx=20, pady=10)

        self.tweaks_button = ctk.CTkButton(self.sidebar, text="Tweaks do Sistema", fg_color="#9b59b6", hover_color="#8e44ad",
                                           command=lambda: self.show_frame_by_name("tweaks"))
        self.tweaks_button.grid(row=7, column=0, padx=20, pady=10)

        self.startup_button = ctk.CTkButton(self.sidebar, text="Inicialização (Boot)", command=lambda: self.show_frame_by_name("startup"))
        self.startup_button.grid(row=8, column=0, padx=20, pady=10)

        self.temp_button = ctk.CTkButton(self.sidebar, text="Limpeza Junk", command=lambda: self.show_frame_by_name("temp"))
        self.temp_button.grid(row=9, column=0, padx=20, pady=10)

        self.game_button = ctk.CTkButton(self.sidebar, text="GAME MODE 🎮", fg_color="#e74c3c", hover_color="#c0392b", 
                                         height=40, font=ctk.CTkFont(weight="bold"),
                                         command=lambda: self.show_frame_by_name("game"))
        self.game_button.grid(row=10, column=0, padx=20, pady=(20, 10))

        # Main Content Area
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        # Initialize Frames
        # Note: We pass 'self.restart_as_admin' to ProcessFrame so it can call it
        self.dash_frame = DashboardFrame(self.main_area, nav_callback=self.show_frame_by_name)
        self.ram_frame = RamFrame(self.main_area, config_manager=self.app_config)
        self.scan_frame = ScanFrame(self.main_area)
        self.apps_frame = AppsFrame(self.main_area)

        # Fix: ProcessFrame constructor expects 'restart_callback'
        self.proc_frame = ProcessFrame(self.main_area, restart_callback=self.restart_as_admin)
        self.inst_frame = InstallerFrame(self.main_area)
        self.tweaks_frame = TweaksFrame(self.main_area)
        self.startup_frame = StartupFrame(self.main_area)
        self.temp_frame = TempCleanFrame(self.main_area)
        self.game_frame = GameModeFrame(self.main_area)

        # Start with Dashboard frame
        self.show_frame_by_name("dashboard")

    def show_frame_by_name(self, name):
        # Hide all
        self.dash_frame.grid_forget()
        self.ram_frame.grid_forget()
        self.scan_frame.grid_forget()
        self.apps_frame.grid_forget()
        self.proc_frame.grid_forget()
        self.inst_frame.grid_forget()
        self.tweaks_frame.grid_forget()
        self.startup_frame.grid_forget()
        self.temp_frame.grid_forget()
        self.game_frame.grid_forget()
        
        # Show target
        if name == "dashboard":
            self.dash_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.dash_button)
        elif name == "ram":
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
        elif name == "startup":
            self.startup_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.startup_button)
        elif name == "temp":
            self.temp_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.temp_button)
        elif name == "game":
            self.game_frame.grid(row=0, column=0, sticky="nsew")
            self.highlight_active_button(self.game_button)

    def highlight_active_button(self, active_btn):
        # Reset all buttons to default
        buttons = [self.dash_button, self.ram_button, self.scan_button, self.apps_button, self.proc_button, 
                   self.inst_button, self.tweaks_button, self.startup_button, self.temp_button, self.game_button]
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


    def on_closing(self):
        self.automation.stop()
        self.destroy()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        # Re-run the program with admin rights
        try:
            # SW_SHOWMINIMIZED = 2
            # Use '1' (Normal) if you want to see the console for debugging
            # Using '0' (Hide) avoids the extra window popping up
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
        except Exception as e:
            print(f"Error starting as admin: {e}")
        # Exit the non-admin instance
        sys.exit()
        
    app = App()

    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

