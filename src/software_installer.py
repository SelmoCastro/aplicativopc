import subprocess
import os

class SoftwareInstaller:
    # Categories and popular software with their Winget IDs
    SOFTWARE_CATALOG = {
        "Essenciais (Pós-Format)": {
            "Google Chrome": "Google.Chrome",
            "Mozilla Firefox": "Mozilla.Firefox",
            "WinRAR": "RARLab.WinRAR",
            "7-Zip": "7zip.7zip",
            "VLC Media Player": "VideoLAN.VLC",
            "WhatsApp": "WhatsApp.WhatsApp",
        },
        "Runtimes & Sistema": {
            "Visual C++ Redist. 2015-2022": "Microsoft.VCRedist.2015+.x64",
            ".NET Desktop Runtime 8": "Microsoft.DotNet.DesktopRuntime.8",
            "DirectX (End-User Runtime)": "Microsoft.DirectX",
            "Java Runtime (JRE)": "Oracle.JavaRuntimeEnvironment",
        },
        "Utilitários & Office": {
            "Adobe Acrobat Reader": "Adobe.Acrobat.Reader.64-bit",
            "AnyDesk": "AnyDeskSoftwareGmbH.AnyDesk",
            "Notepad++": "Notepad++.Notepad++",
            "qBittorrent": "qBittorrent.qBittorrent",
            "PowerToys": "Microsoft.PowerToys",
            "LibreOffice": "TheDocumentFoundation.LibreOffice",
        },
        "Mídia & Design": {
            "Spotify": "Spotify.Spotify",
            "OBS Studio": "OBSProject.OBSStudio",
            "GIMP": "GIMP.GIMP",
            "Audacity": "Audacity.Audacity",
        },
        "Gaming": {
            "Steam": "Valve.Steam",
            "Epic Games Launcher": "EpicGames.EpicGamesLauncher",
            "Discord": "Discord.Discord",
            "MSI Afterburner": "Guru3D.Afterburner",
        },
        "Desenvolvimento": {
            "VS Code": "Microsoft.VisualStudioCode",
            "Python 3.12": "Python.Python.3.12",
            "Git": "Git.Git",
            "Node.js (LTS)": "OpenJS.NodeJS.LTS"
        }
    }

    def __init__(self):
        pass

    def get_catalog(self):
        return self.SOFTWARE_CATALOG

    def check_winget_availability(self):
        """Checks if winget is available in the system path."""
        try:
            subprocess.run(["winget", "--version"], capture_output=True, check=True, shell=True)
            return True
        except Exception:
            return False

    def install_apps(self, app_ids, callback_log=None):
        """
        Installs list of app IDs using winget.
        """
        success_count = 0
        fail_count = 0

        for app_id in app_ids:
            if callback_log:
                callback_log(f"Iniciando instalação: {app_id}...")
            
            # Winget install command with silent flags
            # -e: Exact match
            # --silent: No UI
            # --accept-package-agreements: Auto accept license
            # --accept-source-agreements: Auto accept source license
            cmd = f'winget install -e --id {app_id} --silent --accept-package-agreements --accept-source-agreements'
            
            try:
                # hide console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                process = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo, shell=True)
                
                if process.returncode == 0:
                    success_count += 1
                    if callback_log:
                        callback_log(f"SUCESSO: {app_id} instalado.")
                else:
                    fail_count += 1
                    if callback_log:
                        err_msg = process.stderr.strip() or process.stdout.strip() or "Erro desconhecido"
                        callback_log(f"FALHA ao instalar {app_id}: {err_msg}")
            
            except Exception as e:
                fail_count += 1
                if callback_log:
                    callback_log(f"ERRO de execução para {app_id}: {e}")

        return success_count, fail_count
