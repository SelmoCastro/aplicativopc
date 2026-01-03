import subprocess
import ctypes
from src.ram_cleaner import RamCleaner
from src.system_tweaks import SystemTweaks

class GameOptimizer:
    def __init__(self):
        self.ram_cleaner = RamCleaner()
        self.tweaks = SystemTweaks()

    def optimize_for_gaming(self):
        """
        Applies a series of safe optimizations for gaming.
        1. Enables Ultimate Performance Power Plan.
        2. Clears RAM Standby List/Working Set.
        3. Flushes DNS (lower latency potential).
        """
        log = []
        
        # 1. Power Plan
        success, msg = self.tweaks.enable_ultimate_performance()
        if success:
            log.append(f"Energia: {msg}")
        else:
            log.append(f"Energia: Falha ({msg})")

        # 2. RAM Cleaning
        try:
            cleaned_count = self.ram_cleaner.clean_working_set()
            log.append(f"Memória: Otimizada (Processos limpos: {cleaned_count})")
        except Exception as e:
            log.append(f"Memória: Erro ao limpar ({e})")

        # 3. Network Flush
        try:
            subprocess.run("ipconfig /flushdns", shell=True, check=False, stdout=subprocess.DEVNULL)
            log.append("Rede: Cache DNS limpo.")
        except:
            pass
            
        return "\n".join(log)

    def restore_default(self):
        """
        Tries to restore Balanced power plan.
        GUID for Balanced: 381b4222-f694-41f0-9685-ff5bb260df2e
        """
        try:
            subprocess.run("powercfg /SetActive 381b4222-f694-41f0-9685-ff5bb260df2e", shell=True)
            return "Plano de energia 'Equilibrado' restaurado."
        except:
            return "Erro ao restaurar plano de energia."
