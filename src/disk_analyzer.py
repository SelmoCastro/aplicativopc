import os
import shutil

class DiskAnalyzer:
    def __init__(self):
        pass

    def get_folder_size(self, path):
        """Calculates total size of a folder in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        try:
                            total_size += os.path.getsize(fp)
                        except OSError:
                            continue
        except Exception:
            pass # Permissions issues or path not found
        return total_size

    def format_bytes(self, size):
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]}B"

    def scan_directory_structure(self, root_path):
        """
        Scans immediate children of root_path and calculates their deep sizes.
        Returns sorted list of dicts: {'name': str, 'path': str, 'size': int, 'size_str': str}
        """
        results = []
        if not os.path.exists(root_path):
            return []

        # List of system folders to ignore (only when scanning root C: or similar)
        # Using uppercase for case-insensitive check
        EXCLUDED_FOLDERS = [
            "WINDOWS", "PROGRAM FILES", "PROGRAM FILES (X86)", 
            "PROGRAMDATA", "SYSTEM VOLUME INFORMATION", "$RECYCLE.BIN", "RECOVERY",
            "HIBERFIL.SYS", "PAGEFILE.SYS", "SWAPFILE.SYS",
            "DOCUMENTS AND SETTINGS", "PERFLOGS", "MSOCACHE",
            "APPDATA", "LOCAL SETTINGS", "APPLICATION DATA" # Hiding AppData to focus on User Content
        ]

        try:
            # List immediate children
            items = os.listdir(root_path)
            
            for item in items:
                # Check exclusion (only if scanning a root-like drive, or we can just always exclude common system names)
                # To be compliant with user request "not list system folders", we apply this filter globally 
                # or specifically check if root_path is C:\
                
                if item.upper() in EXCLUDED_FOLDERS:
                    continue
                    
                item_path = os.path.join(root_path, item)
                
                if os.path.isdir(item_path):
                    size = self.get_folder_size(item_path)
                    mtime = os.path.getmtime(item_path)
                    results.append({
                        'name': item,
                        'path': item_path,
                        'size': size,
                        'size_str': self.format_bytes(size),
                        'type': 'folder',
                        'mtime': mtime
                    })
                else:
                    # It's a file
                    try:
                        size = os.path.getsize(item_path)
                        mtime = os.path.getmtime(item_path)
                        results.append({
                            'name': item,
                            'path': item_path,
                            'size': size,
                            'size_str': self.format_bytes(size),
                            'type': 'file',
                            'mtime': mtime
                        })
                    except:
                        pass
            
            # Default Sort by size (descending)
            results.sort(key=lambda x: x['size'], reverse=True)
            
        except Exception as e:
            print(f"Error scanning {root_path}: {e}")
            return []

        return results

    def delete_item(self, path):
        """Deletes a file or directory recursively."""
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True, "Item deletado com sucesso."
        except Exception as e:
            return False, f"Erro ao deletar: {e}"
