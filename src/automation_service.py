import threading
import time
import psutil
from src.ram_cleaner import RamCleaner

class AutomationService:
    def __init__(self, config_manager, log_callback=None):
        self.config = config_manager
        self.ram_cleaner = RamCleaner()
        self.running = False
        self.log_callback = log_callback
        self.last_clean_time = 0
        self.cooldown = 60 # Seconds between auto-cleans

    def start(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        print("Automation started.")
        while self.running:
            try:
                # 1. Auto RAM Clean
                if self.config.get("auto_ram_clean"):
                    threshold = self.config.get("ram_threshold")
                    current_usage = psutil.virtual_memory().percent
                    
                    # Only clean if usage > threshold AND cooldown passed
                    if current_usage >= threshold and (time.time() - self.last_clean_time > self.cooldown):
                        self._trigger_ram_clean(current_usage, threshold)
                
                time.sleep(5) # Check every 5 seconds
            except Exception as e:
                print(f"Auto error: {e}")
                time.sleep(10)

    def _trigger_ram_clean(self, usage, threshold):
        try:
            if self.log_callback:
                self.log_callback(f"[AUTO] RAM ({usage}%) > {threshold}%. Limpando...")
            
            cleaned = self.ram_cleaner.clean_working_set()
            self.last_clean_time = time.time()
            
            if self.log_callback:
                self.log_callback(f"[AUTO] Limpeza concluída. {cleaned} processos otimizados.")
        except Exception as e:
            print(f"Auto clean error: {e}")
