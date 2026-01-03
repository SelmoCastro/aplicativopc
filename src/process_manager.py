import psutil
import os
import ctypes
import sys

class ProcessManager:
    # Set of critical process names (lowercase) to AVOID listing/killing
    CRITICAL_PROCESSES = {
        'svchost.exe', 'explorer.exe', 'system', 'registry', 'smss.exe', 
        'csrss.exe', 'wininit.exe', 'services.exe', 'lsass.exe', 'winlogon.exe', 
        'fontdrvhost.exe', 'dwm.exe', 'spoolsv.exe', 'taskhostw.exe', 
        'runtimebroker.exe', 'sihost.exe', 'ctfmon.exe', 'smartscreen.exe',
        'securityhealthservice.exe', 'python.exe', 'pythonw.exe' # Don't kill self
    }

    def __init__(self):
        pass

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_heavy_processes(self, limit=50):
        """
        Returns a list of dictionaries with process info, sorted by Memory usage (descending).
        Filters out critical system processes.
        """
        process_list = []
        
        # Get current process PID to avoid killing self
        my_pid = os.getpid()

        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                p_info = proc.info
                name_lower = p_info['name'].lower()
                
                # Filter out critical processes and self
                if p_info['pid'] == my_pid:
                    continue
                if name_lower in self.CRITICAL_PROCESSES:
                    continue
                if name_lower.startswith('system'):
                    continue

                mem_mb = p_info['memory_info'].rss / (1024 * 1024)
                
                process_list.append({
                    'pid': p_info['pid'],
                    'name': p_info['name'],
                    'memory_mb': mem_mb,
                    'memory_str': f"{mem_mb:.2f} MB"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort by memory usage
        sorted_list = sorted(process_list, key=lambda x: x['memory_mb'], reverse=True)
        return sorted_list[:limit]

    def kill_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=3)
            return True, f"Processo {pid} finalizado."
        except psutil.AccessDenied:
            # Try force kill with OS command (sometimes works better or gives clearer error)
            try:
                result = os.system(f"taskkill /F /PID {pid}")
                if result == 0:
                    return True, f"Processo {pid} finalizado (Forçado via CMD)."
                else:
                    return False, "Acesso negado. Tente rodar como Administrador."
            except:
                return False, "Acesso negado. Tente rodar como Administrador."
        except psutil.NoSuchProcess:
            return False, "Processo não encontrado (já fechado?)."
        except Exception as e:
            return False, f"Erro: {e}"
