import psutil
import ctypes
from ctypes import wintypes
import os

# Define necessary Windows API constants and types
PROCESS_SET_QUOTA = 0x0100
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

class RamCleaner:
    def __init__(self):
        self.files = []
        
    @staticmethod
    def clean_working_set():
        """
        Attempts to empty the working set of all accessible processes.
        This forces processes to release unused memory back to the system.
        """
        cleaned_count = 0
        total_freed_approx = 0 # It's hard to calculate exact freed amount without snapshotting before/after
        
        # Load PSAPI.DLL
        psapi = ctypes.WinDLL('psapi.dll')
        kernel32 = ctypes.WinDLL('kernel32.dll')

        # Iterate over all running processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                # Skip system idle process/system
                if pid <= 4:
                    continue
                
                # Open process with necessary permissions
                handle = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                if handle:
                    # Attempt to empty working set
                    success = psapi.EmptyWorkingSet(handle)
                    if success:
                        cleaned_count += 1
                    
                    kernel32.CloseHandle(handle)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                # print(f"Error cleaning {proc.info['name']}: {e}")
                pass
                
        return cleaned_count

    @staticmethod
    def get_memory_info():
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used,
            'free': mem.free
        }
