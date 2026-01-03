import winreg
import os
import shutil
import winshell

class StartupManager:
    def __init__(self):
        pass

    def get_startup_items(self):
        """
        Retrieves a list of startup items from Registry and Startup Folder.
        Returns: list of dicts {'name':, 'path':, 'source':Str, 'enabled':Bool}
        """
        items = []

        # 1. Registry - HKCU Run
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({
                        'name': name,
                        'path': value,
                        'source': 'Registry (User)',
                        'type': 'reg',
                        'key_path': r"Software\Microsoft\Windows\CurrentVersion\Run",
                        'root': winreg.HKEY_CURRENT_USER
                    })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error reading HKCU Startup: {e}")

        # 2. Registry - HKLM Run (Read-only usually requires admin)
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({
                        'name': name,
                        'path': value,
                        'source': 'Registry (System)',
                        'type': 'reg',
                        'key_path': r"Software\Microsoft\Windows\CurrentVersion\Run",
                        'root': winreg.HKEY_LOCAL_MACHINE
                    })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
             # Often fails if not admin, safe to ignore or log
             print(f"Error reading HKLM Startup: {e}")

        # 3. Startup Folder - User
        try:
            startup_path = winshell.startup()
            if os.path.exists(startup_path):
                for filename in os.listdir(startup_path):
                    if filename.lower().endswith(".lnk") or filename.lower().endswith(".bat") or filename.lower().endswith(".exe"):
                        file_path = os.path.join(startup_path, filename)
                        items.append({
                            'name': filename,
                            'path': file_path,
                            'source': 'Folder (User)',
                            'type': 'folder'
                        })
        except Exception as e:
            print(f"Error reading Startup Folder: {e}")

        return items

    def delete_item(self, item):
        """
        Deletes/Disables a startup item.
        """
        try:
            if item['type'] == 'reg':
                key = winreg.OpenKey(item['root'], item['key_path'], 0, winreg.KEY_WRITE)
                winreg.DeleteValue(key, item['name'])
                winreg.CloseKey(key)
                return True, f"Removido do Registro: {item['name']}"
            
            elif item['type'] == 'folder':
                os.remove(item['path'])
                return True, f"Arquivo removido: {item['name']}"
                
        except Exception as e:
            return False, f"Erro ao remover: {e}"
        
        return False, "Tipo desconhecido"
