import os
import psutil
from concurrent.futures import ThreadPoolExecutor

class ScamScanner:
    SUSPICIOUS_EXTENSIONS = {'.exe', '.msi', '.bat', '.vbs', '.ps1', '.cmd', '.scr', '.com'}
    
    def __init__(self):
        pass

    def get_drives(self):
        """Returns a list of all physical drives/partitions."""
        drives = []
        for partition in psutil.disk_partitions():
            if 'fixed' in partition.opts or 'removable' in partition.opts:
                drives.append(partition.mountpoint)
        return drives

    def find_download_folders(self, drives):
        """
        Attempts to find 'Downloads' folders on the given drives.
        It checks standard paths and the root for a folder named 'Downloads' or 'Download'.
        """
        found_folders = []
        
        # Standard user path for the main drive (usually C:)
        user_home = os.path.expanduser('~')
        default_downloads = os.path.join(user_home, 'Downloads')
        if os.path.exists(default_downloads):
            found_folders.append(default_downloads)
            
        # Common variations to check on other drives/roots
        target_names = ['Downloads', 'Download', 'Meus Downloads']
        
        for drive in drives:
            # Check roots
            for name in target_names:
                path = os.path.join(drive, name)
                if os.path.join(drive, name) != default_downloads: # Avoid partial duplicates if drive is C:
                     if os.path.exists(path):
                        found_folders.append(path)
                        
        # Remove duplicates
        return list(set(found_folders))

    def scan_folder(self, folder_path):
        """Scans a single folder for suspicious files."""
        suspicious_files = []
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.SUSPICIOUS_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        size_mb = os.path.getsize(full_path) / (1024 * 1024)
                        suspicious_files.append({
                            'name': file,
                            'path': full_path,
                            'size_mb': f"{size_mb:.2f} MB",
                            'extension': ext
                        })
        except Exception as e:
            print(f"Error scanning {folder_path}: {e}")
            
        return suspicious_files

    def scan_all(self):
        """Orchestrates the full scan."""
        drives = self.get_drives()
        folders = self.find_download_folders(drives)
        
        results = []
        
        # Use threading for faster scanning of multiple folders
        with ThreadPoolExecutor() as executor:
            future_to_folder = {executor.submit(self.scan_folder, folder): folder for folder in folders}
            for future in future_to_folder:
                results.extend(future.result())
                
        return {'scanned_folders': folders, 'suspicious_files': results}
