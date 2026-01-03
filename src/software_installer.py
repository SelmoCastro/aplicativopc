import subprocess
import os

class SoftwareInstaller:
    # Categories and popular software with their Winget IDs
    SOFTWARE_CATALOG = {
        "Navegadores": {
            "Google Chrome": "Google.Chrome",
            "Mozilla Firefox": "Mozilla.Firefox",
            "Brave Browser": "Brave.Brave",
            "Opera GX": "Opera.OperaGX"
        },
        "Comunicação": {
            "Discord": "Discord.Discord",
            "WhatsApp": "WhatsApp.WhatsApp",
            "Telegram": "Telegram.TelegramDesktop",
            "Zoom": "Zoom.Zoom"
        },
        "Ferramentas / Utilitários": {
            "7-Zip": "7zip.7zip",
            "WinRAR": "RARLab.WinRAR",
            "PowerToys": "Microsoft.PowerToys",
            "Notepad++": "Notepad++.Notepad++",
            "AnyDesk": "AnyDeskSoftwareGmbH.AnyDesk"
        },
        "Mídia": {
            "VLC Media Player": "VideoLAN.VLC",
            "Spotify": "Spotify.Spotify",
            "OBS Studio": "OBSProject.OBSStudio"
        },
        "Desenvolvimento": {
            "VS Code": "Microsoft.VisualStudioCode",
            "Python 3.12": "Python.Python.3.12",
            "Git": "Git.Git",
            "Node.js (LTS)": "OpenJS.NodeJS.LTS"
        },
        "Gaming": {
            "Steam": "Valve.Steam",
            "Epic Games Launcher": "EpicGames.EpicGamesLauncher"
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
