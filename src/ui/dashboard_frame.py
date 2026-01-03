import customtkinter as ctk
import psutil
import threading
import time
import queue

from src.hardware_info import HardwareInfo

class DashboardFrame(ctk.CTkFrame):
    def create_card(self, row, col, title, initial_value, color_theme=None, icon=None):
        card = ctk.CTkFrame(self, fg_color=("gray90", "#2b2b2b"), corner_radius=15, border_width=2, border_color=("gray80", "#333"))
        card.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
        
        # Color Stripe Header
        if color_theme:
            stripe = ctk.CTkFrame(card, height=6, fg_color=color_theme, corner_radius=0)
            stripe.pack(fill="x")

        # Icon + Title Frame
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        if icon:
             ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=24)).pack(side="left")

        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=("gray40", "gray70")).pack(side="left", padx=10)
        
        value_lbl = ctk.CTkLabel(card, text=initial_value, font=ctk.CTkFont(family="Roboto", size=32, weight="bold"))
        value_lbl.pack(pady=10)
        
        card.value_label = value_lbl
        return card

    def __init__(self, master, nav_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.nav_callback = nav_callback
        self.gui_queue = queue.Queue()
        self.running = True
        self.hw_info = HardwareInfo()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1) # 3 columns for better spacing
        
        # Header
        self.welcome_label = ctk.CTkLabel(self, text="Painel de Controle", font=ctk.CTkFont(family="Roboto", size=28, weight="bold"))
        self.welcome_label.grid(row=0, column=0, columnspan=3, pady=(30, 20), sticky="w", padx=30)

        # --- System Status Cards ---
        
        # CPU Card (Blue)
        self.cpu_card = self.create_card(1, 0, "CPU", "0%", color_theme="#3498db", icon="⚡")
        self.cpu_bar = ctk.CTkProgressBar(self.cpu_card, progress_color="#3498db", height=10)
        self.cpu_bar.pack(pady=15, padx=25, fill="x")
        self.cpu_bar.set(0)

        # RAM Card (Purple)
        self.ram_card = self.create_card(1, 1, "Memória RAM", "0/0 GB", color_theme="#9b59b6", icon="💾")
        self.ram_bar = ctk.CTkProgressBar(self.ram_card, progress_color="#9b59b6", height=10)
        self.ram_bar.pack(pady=15, padx=25, fill="x")
        self.ram_bar.set(0)

        # Disk Card (Green) - Using scrollable logic for multi-disk
        self.disk_card_container = self.create_card(1, 2, "Armazenamento", "", color_theme="#2ecc71", icon="💿")
        
        # We replace the single value label with a small frame to hold dynamic rows
        self.disk_card_container.value_label.destroy() # Remove single value
        
        self.disk_list_frame = ctk.CTkFrame(self.disk_card_container, fg_color="transparent")
        self.disk_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.disk_widgets = {} # Map device -> {label, progress_bar}

        # Quick Actions Card (Full Width)
        action_card = ctk.CTkFrame(self, fg_color=("gray90", "#2b2b2b"), corner_radius=15)
        action_card.grid(row=2, column=0, columnspan=3, sticky="ew", padx=15, pady=20)
        
        ctk.CTkLabel(action_card, text="Ações Rápidas", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        btn_frame = ctk.CTkFrame(action_card, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=20)
        
        # Modern Buttons
        self.create_action_btn(btn_frame, "🚀 Otimizar Agora", "#27ae60", lambda: self.navigate_to("ram"))
        self.create_action_btn(btn_frame, "🧹 Limpeza Junk", "#c0392b", lambda: self.navigate_to("temp"))
        self.create_action_btn(btn_frame, "💻 Info Hardware", "#2980b9", self.show_hardware_info)

        # Start Monitoring Thread
        threading.Thread(target=self.bg_monitor, daemon=True).start()
        
        self.check_queue()

    def create_action_btn(self, parent, text, color, command):
        btn = ctk.CTkButton(parent, text=text, fg_color=color, hover_color=color, 
                            height=40, font=ctk.CTkFont(size=14, weight="bold"),
                            command=command)
        btn.pack(side="left", expand=True, fill="x", padx=10)


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
                
                # Disks
                disks_info = []
                for part in psutil.disk_partitions(all=False):
                    if 'cdrom' in part.opts or part.fstype == '':
                        continue
                        
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        free_gb = usage.free / (1024**3)
                        
                        # Just grab basic info: "C:", 50%
                        disks_info.append({
                            'device': part.device,
                            'mountpoint': part.mountpoint,
                            'total_gb': usage.total / (1024**3),
                            'free_gb': free_gb,
                            'percent': usage.percent
                        })
                    except:
                        continue
                
                # Put data in queue
                self.gui_queue.put((cpu, ram_text, ram_val, disks_info))
                
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

    def _update_ui(self, cpu, ram_text, ram_val, disks_info):
        if not self.winfo_exists(): return
        
        # Performance optimization: Don't update visual elements if frame is hidden
        # This prevents "lag after a while" when user is on other tabs
        if not self.winfo_viewable():
            return

        # CPU & RAM
        self.cpu_card.value_label.configure(text=f"{cpu}%")
        self.cpu_bar.set(cpu / 100)
        
        self.ram_card.value_label.configure(text=ram_text)
        self.ram_bar.set(ram_val)
        
        # Disks logic
        # disks_info is list of dicts
        
        seen_devices = []
        
        for d in disks_info:
            dev = d['device']
            seen_devices.append(dev)
            
            # If new disk, create widgets
            if dev not in self.disk_widgets:
                row = ctk.CTkFrame(self.disk_list_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                # Label: "C: (100 GB Free)"
                lbl = ctk.CTkLabel(row, text=f"{dev}", font=ctk.CTkFont(size=12, weight="bold"), width=50, anchor="w")
                lbl.pack(side="left")
                
                details = ctk.CTkLabel(row, text="--", font=ctk.CTkFont(size=11), text_color="gray")
                details.pack(side="right")
                
                pb = ctk.CTkProgressBar(self.disk_list_frame, height=6, progress_color="#2ecc71")
                pb.pack(fill="x", pady=(0, 8))
                
                self.disk_widgets[dev] = {'lbl': lbl, 'details': details, 'pb': pb, 'row': row}
            
            # Update values
            widgets = self.disk_widgets[dev]
            widgets['details'].configure(text=f"{d['free_gb']:.0f} GB Livres")
            widgets['pb'].set(d['percent'] / 100)
            
        # Optional: Remove disks that vanished (unplugged USB) - skipped for simplicity

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
