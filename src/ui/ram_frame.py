import customtkinter as ctk
import threading
import time
from src.ram_cleaner import RamCleaner

class RamFrame(ctk.CTkFrame):
    def __init__(self, master, config_manager=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config_manager
        
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
        self.clean_btn.grid(row=3, column=0, pady=30)
        
        self.clean_status = ctk.CTkLabel(self, text="", text_color="green")
        self.clean_status.grid(row=4, column=0, pady=5)

        # --- Automation Section ---
        if self.config:
            auto_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray25"))
            auto_frame.grid(row=5, column=0, pady=20, padx=20, sticky="ew")
            auto_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(auto_frame, text="Automação Inteligente", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
            
            # Toggle
            self.auto_var = ctk.BooleanVar(value=self.config.get("auto_ram_clean"))
            self.auto_chk = ctk.CTkSwitch(auto_frame, text="Limpeza Automática", variable=self.auto_var, command=self.save_auto_settings)
            self.auto_chk.grid(row=1, column=0, padx=20, pady=10, sticky="w")
            
            # Slider
            self.thresh_lbl = ctk.CTkLabel(auto_frame, text=f"Limpar quando > {self.config.get('ram_threshold')}%")
            self.thresh_lbl.grid(row=1, column=1, sticky="e", padx=20)
            
            self.thresh_slider = ctk.CTkSlider(auto_frame, from_=50, to=95, number_of_steps=45, command=self.update_slider_label)
            self.thresh_slider.set(self.config.get("ram_threshold"))
            self.thresh_slider.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
            
            # Bind release event manually if needed, usually 'command' covers drag
            self.thresh_slider.bind("<ButtonRelease-1>", lambda event: self.save_auto_settings())

        # Start monitoring loop
        self.update_ram_loop()

    def update_slider_label(self, value):
        self.thresh_lbl.configure(text=f"Limpar quando > {int(value)}%")

    def save_auto_settings(self):
        if self.config:
            self.config.set("auto_ram_clean", self.auto_var.get())
            self.config.set("ram_threshold", int(self.thresh_slider.get()))

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

