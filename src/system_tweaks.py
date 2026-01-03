import subprocess
import os
import winreg
import ctypes
import sys

class SystemTweaks:
    def __init__(self):
        pass

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def restore_classic_context_menu(self):
        """
        Restores the Windows 10 style context menu on Windows 11.
        Key: HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32
        Val: (Default) = ""
        """
        try:
            # We use reg.exe because it handles the key creation and empty default value easily
            key = r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            cmd = f'reg add "{key}" /f /ve'
            
            subprocess.run(cmd, shell=True, check=True)
            
            # Restart explorer to apply
            subprocess.run("taskkill /f /im explorer.exe & start explorer.exe", shell=True)
            
            return True, "Menu Clássico ativado! O Explorer foi reiniciado para aplicar."
        except Exception as e:
            return False, f"Erro: {e}"


    def enable_ultimate_performance(self):
        """
        Enables the 'Ultimate Performance' power scheme.
        Command: powercfg /DuplicateScheme e9a42b02-d5df-448d-aa00-03f14749eb61
        """
        if not self.is_admin():
            return False, "Requer privilégios de Administrador."

        try:
            # 1. Duplicate the scheme
            cmd = "powercfg /DuplicateScheme e9a42b02-d5df-448d-aa00-03f14749eb61"
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                return False, f"Falha ao duplicar esquema: {result.stderr}"

            # 2. Check output to get new GUID (optional, but good for confirmation)
            # Output format: "Power Scheme GUID: <GUID>  (Ultimate Performance)"
            output = result.stdout.strip()
            
            # 3. Set as active
            if "Ultimate Performance" in output or "Desempenho Máximo" in output:
                 # Extract standard guid part if needed, or just set active via name listing?
                 # Easier: Just duplicate it. User can select it manually or we force it?
                 # Let's try to set it active if we find the GUID.
                 import re
                 match = re.search(r'([a-f0-9-]{36})', output)
                 if match:
                     new_guid = match.group(1)
                     subprocess.run(f"powercfg /SetActive {new_guid}", shell=True)
                     return True, "Modo Desempenho Máximo ativado com sucesso!"
            
            return True, "Esquema criado. Verifique nas Opções de Energia."
            
        except Exception as e:
            return False, f"Erro: {e}"

    def remove_telemetry(self):
        """
        Disables common telemetry and tracking keys via Registry.
        """
        if not self.is_admin():
            return False, "Requer privilégios de Administrador."
        
        commands = [
            # Allow Telemetry = 0 (Security level)
            r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
            # Disable Bing in Search
            r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v BingSearchEnabled /t REG_DWORD /d 0 /f',
            r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v CortezBox /t REG_DWORD /d 0 /f',
             # Disable Advertising ID
            r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'
        ]
        
        errors = 0
        for cmd in commands:
            res = subprocess.run(cmd, shell=True, capture_output=True)
            if res.returncode != 0:
                errors += 1
        
        if errors == 0:
            return True, "Telemetria e Bing Search desativados."
        else:
            return True, f"Aplicado com {errors} avisos/erros (algumas chaves podem não existir)."

    def restore_classic_photo_viewer(self):
        """
        Restores the old Windows Photo Viewer by adding registry keys.
        This is complex as it involves many keys. We will use a temporary .reg file.
        """
        if not self.is_admin():
            return False, "Requer privilégios de Administrador."

        reg_content = r"""Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Applications\photoviewer.dll\shell\open]
"MuiVerb"="@photoviewer.dll,-3043"

[HKEY_CLASSES_ROOT\Applications\photoviewer.dll\shell\open\command]
@=hex(2):25,00,53,00,79,00,73,00,74,00,65,00,6d,00,52,00,6f,00,6f,00,74,00,25,\
  00,5c,00,53,00,79,00,73,00,74,00,65,00,6d,00,33,00,32,00,5c,00,72,00,75,00,\
  6e,00,64,00,6c,00,6c,00,33,00,32,00,2e,00,65,00,78,00,65,00,20,00,22,00,25,\
  00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,00,46,00,69,00,6c,00,65,00,73,00,\
  25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,77,00,73,00,20,00,50,00,68,00,6f,\
  00,74,00,6f,00,20,00,56,00,69,00,65,00,77,00,65,00,72,00,5c,00,50,00,68,00,\
  6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,65,00,72,00,2e,00,64,00,6c,00,6c,\
  00,22,00,2c,00,20,00,49,00,6d,00,61,00,67,00,65,00,56,00,69,00,65,00,77,00,\
  5f,00,46,00,75,00,6c,00,6c,00,73,00,63,00,72,00,65,00,65,00,6e,00,20,00,25,\
  00,31,00,00,00

[HKEY_CLASSES_ROOT\Applications\photoviewer.dll\shell\open\DropTarget]
"Clsid"="{FFE2A43C-56B9-4bf5-9A79-CC6D4285608A}"

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Bitmap]
"ImageOptionFlags"=dword:00000001
"FriendlyTypeName"=hex(2):40,00,25,00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,\
  00,46,00,69,00,6c,00,65,00,73,00,25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,\
  77,00,73,00,20,00,50,00,68,00,6f,00,74,00,6f,00,20,00,56,00,69,00,65,00,77,\
  00,65,00,72,00,5c,00,50,00,68,00,6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,\
  65,00,72,00,2e,00,64,00,6c,00,6c,00,2c,00,2d,00,33,00,30,00,35,00,36,00,00,\
  00

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Bitmap\DefaultIcon]
@="%SystemRoot%\\System32\\imageres.dll,-70"

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Bitmap\shell\open\command]
@=hex(2):25,00,53,00,79,00,73,00,74,00,65,00,6d,00,52,00,6f,00,6f,00,74,00,25,\
  00,5c,00,53,00,79,00,73,00,74,00,65,00,6d,00,33,00,32,00,5c,00,72,00,75,00,\
  6e,00,64,00,6c,00,6c,00,33,00,32,00,2e,00,65,00,78,00,65,00,20,00,22,00,25,\
  00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,00,46,00,69,00,6c,00,65,00,73,00,\
  25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,77,00,73,00,20,00,50,00,68,00,6f,\
  00,74,00,6f,00,20,00,56,00,69,00,65,00,77,00,65,00,72,00,5c,00,50,00,68,00,\
  6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,65,00,72,00,2e,00,64,00,6c,00,6c,\
  00,22,00,2c,00,20,00,49,00,6d,00,61,00,67,00,65,00,56,00,69,00,65,00,77,00,\
  5f,00,46,00,75,00,6c,00,6c,00,73,00,63,00,72,00,65,00,65,00,6e,00,20,00,25,\
  00,31,00,00,00

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Bitmap\shell\open\DropTarget]
"Clsid"="{FFE2A43C-56B9-4bf5-9A79-CC6D4285608A}"

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Jpeg]
"EditFlags"=dword:00010000
"ImageOptionFlags"=dword:00000001
"FriendlyTypeName"=hex(2):40,00,25,00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,\
  00,46,00,69,00,6c,00,65,00,73,00,25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,\
  77,00,73,00,20,00,50,00,68,00,6f,00,74,00,6f,00,20,00,56,00,69,00,65,00,77,\
  00,65,00,72,00,5c,00,50,00,68,00,6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,\
  65,00,72,00,2e,00,64,00,6c,00,6c,00,2c,00,2d,00,33,00,30,00,35,00,35,00,00,\
  00

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Jpeg\DefaultIcon]
@="%SystemRoot%\\System32\\imageres.dll,-72"

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Jpeg\shell\open\command]
@=hex(2):25,00,53,00,79,00,73,00,74,00,65,00,6d,00,52,00,6f,00,6f,00,74,00,25,\
  00,5c,00,53,00,79,00,73,00,74,00,65,00,6d,00,33,00,32,00,5c,00,72,00,75,00,\
  6e,00,64,00,6c,00,6c,00,33,00,32,00,2e,00,65,00,78,00,65,00,20,00,22,00,25,\
  00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,00,46,00,69,00,6c,00,65,00,73,00,\
  25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,77,00,73,00,20,00,50,00,68,00,6f,\
  00,74,00,6f,00,20,00,56,00,69,00,65,00,77,00,65,00,72,00,5c,00,50,00,68,00,\
  6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,65,00,72,00,2e,00,64,00,6c,00,6c,\
  00,22,00,2c,00,20,00,49,00,6d,00,61,00,67,00,65,00,56,00,69,00,65,00,77,00,\
  5f,00,46,00,75,00,6c,00,6c,00,73,00,63,00,72,00,65,00,65,00,6e,00,20,00,25,\
  00,31,00,00,00

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Jpeg\shell\open\DropTarget]
"Clsid"="{FFE2A43C-56B9-4bf5-9A79-CC6D4285608A}"

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Png]
"ImageOptionFlags"=dword:00000001
"FriendlyTypeName"=hex(2):40,00,25,00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,\
  00,46,00,69,00,6c,00,65,00,73,00,25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,\
  77,00,73,00,20,00,50,00,68,00,6f,00,74,00,6f,00,20,00,56,00,69,00,65,00,77,\
  00,65,00,72,00,5c,00,50,00,68,00,6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,\
  65,00,72,00,2e,00,64,00,6c,00,6c,00,2c,00,2d,00,33,00,30,00,35,00,37,00,00,\
  00

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Png\DefaultIcon]
@="%SystemRoot%\\System32\\imageres.dll,-71"

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Png\shell\open\command]
@=hex(2):25,00,53,00,79,00,73,00,74,00,65,00,6d,00,52,00,6f,00,6f,00,74,00,25,\
  00,5c,00,53,00,79,00,73,00,74,00,65,00,6d,00,33,00,32,00,5c,00,72,00,75,00,\
  6e,00,64,00,6c,00,6c,00,33,00,32,00,2e,00,65,00,78,00,65,00,20,00,22,00,25,\
  00,50,00,72,00,6f,00,67,00,72,00,61,00,6d,00,46,00,69,00,6c,00,65,00,73,00,\
  25,00,5c,00,57,00,69,00,6e,00,64,00,6f,00,77,00,73,00,20,00,50,00,68,00,6f,\
  00,74,00,6f,00,20,00,56,00,69,00,65,00,77,00,65,00,72,00,5c,00,50,00,68,00,\
  6f,00,74,00,6f,00,56,00,69,00,65,00,77,00,65,00,72,00,2e,00,64,00,6c,00,6c,\
  00,22,00,2c,00,20,00,49,00,6d,00,61,00,67,00,65,00,56,00,69,00,65,00,77,00,\
  5f,00,46,00,75,00,6c,00,6c,00,73,00,63,00,72,00,65,00,65,00,6e,00,20,00,25,\
  00,31,00,00,00

[HKEY_CLASSES_ROOT\PhotoViewer.FileAssoc.Png\shell\open\DropTarget]
"Clsid"="{FFE2A43C-56B9-4bf5-9A79-CC6D4285608A}"

"""
        try:
            # Write temp file in current dir
            reg_path = os.path.join(os.getcwd(), "restore_photoviewer.reg")
            with open(reg_path, "w") as f:
                f.write(reg_content)
                
            # Import silently
            subprocess.run(f'reg import "{reg_path}"', shell=True, check=True)
            
            # Cleanup
            if os.path.exists(reg_path):
                os.remove(reg_path)
                
            return True, "Visualizador de Fotos restaurado! Tente abrir uma imagem e escolha 'Abrir com...' -> Visualizador clássico."
        except Exception as e:
            return False, f"Erro ao aplicar REG: {e}"
