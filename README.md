# 🛡️ SysGuard Ultimate - Otimizador de Sistema Avançado

**SysGuard Ultimate** é uma ferramenta "Canivete Suíço" desenvolvida em Python para monitoramento, limpeza, otimização e personalização do Windows 10/11. Projetado para ser leve, moderno e independente.

![Dashboard Preview](https://i.imgur.com/PLACEHOLDER.png) 
*(Substitua por um print real se desejar)*

---

## 🚀 Funcionalidades Principais

### 📊 Dashboard Interativo
- Monitoramento em tempo real de **CPU**, **RAM** e **Disco**.
- Visualização gráfica moderna com suporte a múltiplos discos.
- Atualização em background sem travar a interface.

### 🧹 Limpeza & Manutenção
- **Limpeza de Junk**: Remove arquivos temporários, cache do Windows e lixeira.
- **Analisador de Disco**: Escaneie pastas para encontrar arquivos pesados ou antigos (com filtro por data).
- **Otimizador de RAM**: Limpa a memória *Standby* e *Working Set* para liberar recursos imediatos.

### 🎮 Game Mode (Modo Jogo)
- Aplica plano de energia "Desempenho Máximo".
- Fecha processos desnecessários.
- Limpa o cache de DNS e otimiza a rede para reduzir latência.

### 🛠️ Ferramentas de Sistema
- **Startup Manager**: Gerencie (e remova) programas que iniciam com o Windows.
- **Bloatware Remover**: Remova aplicativos pré-instalados inúteis (Xbox, Clima, Notícias, etc.).
- **Instalador de Softwares**: Um "Kit Pós-Formatação" que instala automaticamente itens essenciais (Navegadores, Runtimes, WinRAR, etc.) usando o `winget`.
- **Tweaks**: Ative o "Menu de Contexto Clássico" (Win 11) e outros ajustes visuais.

---

## 📦 Como Rodar (Desenvolvimento)

### Pré-requisitos
- Python 3.10 ou superior.
- Permissões de Administrador (o app solicita automaticamente).

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SeuUsuario/SysGuard.git
   cd SysGuard
   ```

2. **Crie um ambiente virtual (opcional mas recomendado):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   pip install pypiwin32 packaging darkdetect
   ```

4. **Execute o projeto:**
   ```bash
   python main.py
   ```

---

## 🏗️ Como Compilar (.exe)

Para gerar um executável único (`.exe`) que funciona em qualquer PC sem Python instalado, utilize o **PyInstaller** com os seguintes parâmetros para garantir que todas as dependências (CustomTkinter, Win32, etc.) sejam incluídas:

```bash
pyinstaller --noconsole --onefile --uac-admin --name="SysGuard_Ultimate" ^
 --collect-all winshell --collect-all customtkinter ^
 --hidden-import=packaging --hidden-import=packaging.version --hidden-import=packaging.specifiers ^
 --hidden-import=tkinter --hidden-import=tkinter.font --hidden-import=tkinter.messagebox ^
 --hidden-import=tkinter.filedialog --hidden-import=tkinter.ttk --hidden-import=tkinter.colorchooser ^
 --hidden-import=darkdetect --hidden-import=win32con --hidden-import=win32api --hidden-import=win32gui ^
 --add-data "venv/Lib/site-packages/customtkinter;customtkinter" main.py
```

O arquivo final estará na pasta `dist/`.

---

## 🛠️ Tecnologias Usadas
- **Python**: Linguagem base.
- **CustomTkinter**: Interface gráfica moderna (UI).
- **Psutil**: Monitoramento de Hardware.
- **PyWin32 / Ctypes**: Interação profunda com APIs do Windows.
- **Winget**: Gerenciamento de pacotes para instalação de softwares.

---

## ⚠️ Aviso Legal
Esta ferramenta realiza alterações no sistema (registro, arquivos, processos). Embora testada extensivamente, utilize com responsabilidade. Recomenda-se criar um Ponto de Restauração antes de aplicar Tweaks profundos.

---
*Desenvolvido com ❤️ e Python.*
