import os
import shutil
import tempfile
import winshell
import ctypes

class TempCleaner:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir() # %TEMP%
        self.win_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
        self.prefetch = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch')

    def get_size(self, path):
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                         if not os.path.islink(fp):
                            total_size += os.path.getsize(fp)
                    except: pass
        except: pass
        return total_size

    def format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels.get(n, '')}"

    def scan_junk(self):
        """Returns dict with sizes ofjunk folders."""
        info = {}
        
        # User Temp
        info['temp_user'] = {
            'path': self.temp_dir,
            'size': self.get_size(self.temp_dir),
            'name': 'Arquivos Temporários (Usuário)'
        }
        
        # Windows Temp (Admin)
        info['temp_sys'] = {
            'path': self.win_temp,
            'size': self.get_size(self.win_temp),
            'name': 'Arquivos Temporários (Sistema)'
        }
        
        # Prefetch (Admin)
        info['prefetch'] = {
            'path': self.prefetch,
            'size': self.get_size(self.prefetch),
            'name': 'Prefetch (Cache de Inicialização)'
        }
        
        # Recycle Bin size is hard to get via standard os, usually we check if it's empty or not.
        # For simplicity, we just list it as an option
        info['recycle'] = {
            'path': 'RecycleBin',
            'size': 0, # Placeholder
            'name': 'Lixeira'
        }

        return info

    def clean_folder(self, folder_path):
        deleted_size = 0
        errors = 0
        
        if not os.path.exists(folder_path):
            return 0, 0

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    size = os.path.getsize(item_path)
                    os.remove(item_path)
                    deleted_size += size
                elif os.path.isdir(item_path):
                     # Calculate size before delete (rough estimate)
                     size = self.get_size(item_path)
                     shutil.rmtree(item_path)
                     deleted_size += size
            except Exception:
                errors += 1
        
        return deleted_size, errors

    def empty_recycle_bin(self):
        try:
            # Flags: SHERB_NOCONFIRMATION = 0x00000001, SHERB_NOPROGRESSUI = 0x00000002, SHERB_NOSOUND = 0x00000004
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            return True, "Lixeira esvaziada."
        except Exception as e:
            return False, f"Erro: {e}"
