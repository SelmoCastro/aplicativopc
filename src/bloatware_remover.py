import subprocess
import threading

class BloatwareRemover:
    # Mapeamento de Nome Amigável -> Nome do Pacote (Parcial ou Completo)
    APP_MAP = {
        "Calculadora": "Microsoft.WindowsCalculator",
        "Câmera": "Microsoft.WindowsCamera",
        "Alarmes e Relógio": "Microsoft.WindowsAlarms",
        "Email e Calendário": "microsoft.windowscommunicationsapps",
        "Mapas": "Microsoft.WindowsMaps",
        "Gravador de Voz": "Microsoft.WindowsSoundRecorder",
        "Xbox App": "Microsoft.XboxApp",
        "Xbox Game Bar": "Microsoft.XboxGamingOverlay",
        "Xbox Identity": "Microsoft.XboxIdentityProvider",
        "Xbox Speech": "Microsoft.XboxSpeechToTextOverlay",
        "Notícias (Bing News)": "Microsoft.BingNews",
        "Clima (Bing Weather)": "Microsoft.BingWeather",
        "Cortana": "Microsoft.549981C3F5F10", 
        "Feedback Hub": "Microsoft.WindowsFeedbackHub",
        "Get Help (Ajuda)": "Microsoft.GetHelp",
        "Dicas (Get Started)": "Microsoft.Getstarted",
        "Solitaire Collection": "Microsoft.MicrosoftSolitaireCollection",
        "Office Hub (Microsoft 365)": "Microsoft.MicrosoftOfficeHub",
        "OneNote": "Microsoft.Office.OneNote",
        "Outlook (Novo)": "Microsoft.OutlookForWindows",
        "Paint 3D": "Microsoft.MSPaint",
        "Pessoas (People)": "Microsoft.People",
        "Power Automate": "Microsoft.PowerAutomateDesktop",
        "Quick Assist": "MicrosoftCorporationII.QuickAssist",
        "Skype": "Microsoft.SkypeApp",
        "Microsoft Teams": "MicrosoftTeams",
        "To Do": "Microsoft.Todos",
        "Wallet (Carteira)": "Microsoft.Wallet",
        "Windows Hello (Face)": "Hello.Face",
        "Groove Música": "Microsoft.ZuneMusic",
        "Filmes e TV": "Microsoft.ZuneVideo",
        "Your Phone (Vincular Celular)": "Microsoft.YourPhone",
        "Clipchamp": "Clipchamp.Clipchamp",
        "3D Viewer": "Microsoft.Microsoft3DViewer",
        "Dev Home": "Microsoft.Windows.DevHome",
        "Microsoft Family": "MicrosoftCorporationII.MicrosoftFamily",
        "Mixed Reality Portal": "Microsoft.MixedReality.Portal",
        "Bloco de Notas (App Store)": "Microsoft.WindowsNotepad",
        "Spotify": "SpotifyAB.SpotifyMusic",
        "OneDrive": "Microsoft.OneDriveSync",
        "Sticky Notes": "Microsoft.MicrosoftStickyNotes",
    }

    def __init__(self):
        pass

    def get_supported_apps(self):
        """Retorna a lista de nomes amigáveis suportados (todos)."""
        return sorted(list(self.APP_MAP.keys()))

    def get_installed_apps(self):
        """
        Verifica quais dos apps suportados estão realmente instalados no sistema.
        Retorna lista de nomes amigáveis.
        """
        installed_friendly_names = []
        
        try:
            # Check all installed packages
            cmd = 'powershell -Command "Get-AppxPackage | Select-Object -ExpandProperty PackageFullName"'
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
            installed_packages = process.stdout.lower()
            
            for friendly_name, package_id in self.APP_MAP.items():
                if package_id.lower() in installed_packages:
                    installed_friendly_names.append(friendly_name)
                    
        except Exception as e:
            print(f"Erro ao verificar apps instalados: {e}")
            return self.get_supported_apps()
            
        return sorted(installed_friendly_names)

    def remove_apps(self, selected_friendly_names, callback_log=None):
        """
        Remove os apps selecionados usando PowerShell.
        """
        success_count = 0
        fail_count = 0

        for name in selected_friendly_names:
            package_id = self.APP_MAP.get(name)
            if not package_id:
                continue

            if callback_log:
                callback_log(f"Removendo {name}...")

            # Use Wildcard for robust removal
            cmd = f'powershell -Command "Get-AppxPackage *{package_id}* | Remove-AppxPackage"'
            
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                process = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
                
                if process.returncode == 0:
                    success_count += 1
                else:
                    fail_count += 1
                    if callback_log:
                        callback_log(f"Falha ao remover {name}: {process.stderr}")

            except Exception as e:
                fail_count += 1
                if callback_log:
                    callback_log(f"Erro ao executar comando para {name}: {e}")
        
        return success_count, fail_count
