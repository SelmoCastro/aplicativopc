import customtkinter as ctk
import threading
import time
from src.ram_cleaner import RamCleaner

class RamFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self, text="Otimização de RAM", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)

        self.ram_usage_label = ctk.CTkLabel(self, text="Uso Atual: --%", font=ctk.CTkFont(size=18))
        self.ram_usage_label.grid(row=1, column=0, pady=10)
        
        self.ram_progress = ctk.CTkProgressBar(self, width=400)
        self.ram_progress.grid(row=2, column=0, pady=10)
        self.ram_progress.set(0)

        self.clean_btn = ctk.CTkButton(self, text="OTIMIZAR RAM AGORA", height=50, 
                                       font=ctk.CTkFont(size=16, weight="bold"), 
                                       command=self.clean_ram_action)
        self.clean_btn.grid(row=3, column=0, pady=40)
        
        self.clean_status = ctk.CTkLabel(self, text="", text_color="green")
        self.clean_status.grid(row=4, column=0, pady=10)
        
        # Start monitoring loop
        self.update_ram_loop()

    def update_ram_loop(self):
        try:
            info = RamCleaner.get_memory_info()
            self.ram_usage_label.configure(text=f"Uso Atual: {info['percent']}%")
            self.ram_progress.set(info['percent'] / 100)
        except Exception:
            pass # Avoid errors on close
        
        self.after(2000, self.update_ram_loop)

    def clean_ram_action(self):
        self.clean_status.configure(text="Limpando...", text_color="yellow")
        self.clean_btn.configure(state="disabled")
        
        def run():
            before = RamCleaner.get_memory_info()
            cleaned_count = RamCleaner.clean_working_set()
            time.sleep(1) # Let system update metrics
            after = RamCleaner.get_memory_info()
            
            diff = before['used'] - after['used']
            diff_mb = diff / (1024 * 1024)
            
            msg = f"Limpo: {cleaned_count} processos.\nLiberado aprox {diff_mb:.2f} MB"
            
            # UI Update
            self.after(0, lambda: self._finish_clean(msg))
            
        threading.Thread(target=run, daemon=True).start()

    def _finish_clean(self, msg):
        self.clean_status.configure(text=msg, text_color="green")
        self.clean_btn.configure(state="normal")
