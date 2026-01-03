import subprocess
import platform

class HardwareInfo:
    def __init__(self):
        pass

    def _run_powershell(self, cmd):
        try:
            full_cmd = f'powershell -Command "{cmd}"'
            result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)
            return result.stdout.strip()
        except:
            return "Desconhecido"

    def get_cpu_info(self):
        # Fallback to platform if powershell fails, but PS is better for full name
        name = self._run_powershell("Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name")
        if not name:
            name = platform.processor()
        return name

    def get_gpu_info(self):
        # Can return multiple lines if multiple GPUs
        name = self._run_powershell("Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name")
        return name.replace("\r\n", " & ") if name else "VGA Padrão"

    def get_ram_info(self):
        # Get Speed and PartNumber/Manufacturer
        speed = self._run_powershell("Get-CimInstance Win32_PhysicalMemory | Select-Object -ExpandProperty Speed | Select-Object -First 1")
        capacity = self._run_powershell("Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory")
        
        try:
            cap_gb = int(capacity) / (1024**3)
            cap_str = f"{cap_gb:.1f} GB"
        except:
            cap_str = "?"

        return f"{cap_str} (Velocidade: {speed} MHz)"

    def get_os_info(self):
        return f"{platform.system()} {platform.release()} ({platform.version()})"
