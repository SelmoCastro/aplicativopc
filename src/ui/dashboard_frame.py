import customtkinter as ctk
import psutil
import threading
import time
import queue

from src.hardware_info import HardwareInfo

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, nav_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.nav_callback = nav_callback
        self.gui_queue = queue.Queue()
        self.running = True
        self.hw_info = HardwareInfo()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Header
        self.welcome_label = ctk.CTkLabel(self, text="Bem-vindo ao SysGuard Ultimate", font=ctk.CTkFont(size=26, weight="bold"))
        self.welcome_label.grid(row=0, column=0, columnspan=2, pady=20)

        # --- System Status Cards ---
        
        # CPU Card
        self.cpu_card = self.create_card(1, 0, "Uso de CPU", "0%")
        self.cpu_bar = ctk.CTkProgressBar(self.cpu_card)
        self.cpu_bar.pack(pady=10, padx=20, fill="x")
        self.cpu_bar.set(0)

        # RAM Card
        self.ram_card = self.create_card(1, 1, "Uso de RAM", "0/0 GB")
        self.ram_bar = ctk.CTkProgressBar(self.ram_card, progress_color="#e67e22")
        self.ram_bar.pack(pady=10, padx=20, fill="x")
        self.ram_bar.set(0)

        # Disk Card
        self.disk_card = self.create_card(2, 0, "Disco Principal (C:)", " Livre")
        self.disk_bar = ctk.CTkProgressBar(self.disk_card, progress_color="#2980b9")
        self.disk_bar.pack(pady=10, padx=20, fill="x")
        self.disk_bar.set(0)

        # Quick Actions Card
        action_card = ctk.CTkFrame(self, fg_color=("gray80", "gray20"))
        action_card.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(action_card, text="Ações Rápidas", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        ctk.CTkButton(action_card, text="🚀 Otimizar Agora", fg_color="#2ecc71", hover_color="#27ae60", 
                      command=lambda: self.navigate_to("ram")).pack(pady=5, padx=20, fill="x")
                      
        ctk.CTkButton(action_card, text="🧹 Limpeza Expressa", fg_color="#e74c3c", hover_color="#c0392b",
                      command=lambda: self.navigate_to("temp")).pack(pady=5, padx=20, fill="x")

        # Hardware Details Button
        ctk.CTkButton(action_card, text="💻 Ver Hardware", fg_color="#34495e", hover_color="#2c3e50",
                      command=self.show_hardware_info).pack(pady=5, padx=20, fill="x")


        # Start Monitoring Thread
        threading.Thread(target=self.bg_monitor, daemon=True).start()
        
        # Start Polling (Main Thread)
        self.check_queue()

    def create_card(self, row, col, title, initial_value):
        card = ctk.CTkFrame(self, fg_color=("gray85", "gray25"))
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(pady=(15,0))
        
        value_lbl = ctk.CTkLabel(card, text=initial_value, font=ctk.CTkFont(size=22, weight="bold"))
        value_lbl.pack(pady=5)
        
        card.value_label = value_lbl
        return card

    def bg_monitor(self):
        """Runs in a background thread."""
        while self.running:
            try:
                # CPU
                cpu = psutil.cpu_percent(interval=None)
                
                # RAM
                ram = psutil.virtual_memory()
                total_gb = ram.total / (1024**3)
                used_gb = ram.used / (1024**3)
                ram_text = f"{used_gb:.1f} / {total_gb:.1f} GB"
                ram_val = ram.percent / 100
                
                # Disk C:
                disk = psutil.disk_usage('C:\\')
                free_gb = disk.free / (1024**3)
                disk_text = f"{free_gb:.0f} GB Livres"
                disk_val = disk.percent / 100
                
                # Put data in queue
                self.gui_queue.put((cpu, ram_text, ram_val, disk_text, disk_val))
                
                time.sleep(2)
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)

    def check_queue(self):
        """Runs on the main thread."""
        if not self.running: return

        try:
            # Process all pending updates, keeping only the last one to be snappy
            last_data = None
            while True:
                last_data = self.gui_queue.get_nowait()
        except queue.Empty:
            pass
            
        if last_data:
            self._update_ui(*last_data)
        
        # Schedule next check
        self.after(500, self.check_queue)

    def _update_ui(self, cpu, ram_text, ram_val, disk_text, disk_val):
        if not self.winfo_exists(): return
        
        self.cpu_card.value_label.configure(text=f"{cpu}%")
        self.cpu_bar.set(cpu / 100)
        
        self.ram_card.value_label.configure(text=ram_text)
        self.ram_bar.set(ram_val)
        
        self.disk_card.value_label.configure(text=disk_text)
        self.disk_bar.set(disk_val)

    def navigate_to(self, page_name):
        if self.nav_callback:
            self.nav_callback(page_name)

    def show_hardware_info(self):
        # Create Toplevel Window
        top = ctk.CTkToplevel(self)
        top.title("Detalhes do Hardware")
        top.geometry("500x350")
        top.transient(self) # Stay on top of main window
        
        ctk.CTkLabel(top, text="Especificações do Sistema", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        info_frame = ctk.CTkFrame(top)
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Async fetch to avoid freezing UI
        def _fetch():
            cpu = self.hw_info.get_cpu_info()
            gpu = self.hw_info.get_gpu_info()
            ram = self.hw_info.get_ram_info()
            os_info = self.hw_info.get_os_info()
            
            self.after(0, lambda: _show(cpu, gpu, ram, os_info))
            
        def _show(cpu, gpu, ram, os_info):
            row = 0
            for label, value in [("Sistema:", os_info), ("Processador:", cpu), ("Placa de Vídeo:", gpu), ("Memória RAM:", ram)]:
                ctk.CTkLabel(info_frame, text=label, font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=10)
                ctk.CTkLabel(info_frame, text=value, wraplength=300).grid(row=row, column=1, sticky="w", padx=10, pady=10)
                row += 1
                
        threading.Thread(target=_fetch, daemon=True).start()

    def destroy(self):

        self.running = False
        super().destroy()
