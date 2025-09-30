"""
⚙️ SALES AGENT IA - SETUP DO SISTEMA
===================================
Script para configuração inicial e instalação
"""

import os
import sys
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt, Confirm

console = Console()

class SystemSetup:
    """Configurador do sistema"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.requirements_file = self.base_dir / "requirements_ia_agent.txt"
        self.env_file = self.base_dir / ".env"
        self.env_example = self.base_dir / "env_example.txt"
    
    def check_python_version(self):
        """Verifica versão do Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            console.print("[bold red]❌ Python 3.8+ é necessário[/bold red]")
            console.print(f"Versão atual: {version.major}.{version.minor}")
            return False
        
        console.print(f"✅ Python {version.major}.{version.minor} - OK")
        return True
    
    def install_dependencies(self):
        """Instala dependências"""
        if not self.requirements_file.exists():
            console.print("[bold red]❌ Arquivo requirements_ia_agent.txt não encontrado[/bold red]")
            return False
        
        console.print("📦 [bold yellow]Instalando dependências...[/bold yellow]")
        
        try:
            # Instala dependências
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ])
            console.print("✅ Dependências instaladas com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]❌ Erro na instalação: {e}[/bold red]")
            return False
    
    def configure_environment(self):
        """Configura variáveis de ambiente"""
        if self.env_file.exists():
            overwrite = Confirm.ask(
                "Arquivo .env já existe. Deseja reconfigurar?",
                default=False
            )
            if not overwrite:
                return True
        
        console.print("🔧 [bold yellow]Configurando ambiente...[/bold yellow]")
        
        # Solicita API Key da OpenAI
        api_key = Prompt.ask(
            "Insira sua OpenAI API Key",
            password=True
        )
        
        if not api_key or len(api_key) < 20:
            console.print("[bold red]❌ API Key inválida[/bold red]")
            return False
        
        # Outras configurações
        overlay_position = Prompt.ask(
            "Posição do overlay",
            choices=["top-left", "top-right", "bottom-left", "bottom-right"],
            default="top-right"
        )
        
        # Cria arquivo .env
        env_content = f"""# SALES AGENT IA - CONFIGURAÇÕES
OPENAI_API_KEY={api_key}
DEBUG=false
LOG_LEVEL=INFO
OVERLAY_POSITION={overlay_position}
OVERLAY_OPACITY=0.9
AUDIO_DEVICE_INDEX=-1
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            console.print("✅ Configuração salva em .env")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao salvar configuração: {e}[/bold red]")
            return False
    
    def create_directories(self):
        """Cria diretórios necessários"""
        directories = [
            self.base_dir / "temp",
            self.base_dir / "embeddings", 
            self.base_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
        
        console.print("✅ Diretórios criados")
    
    def test_audio_devices(self):
        """Testa dispositivos de áudio"""
        try:
            import sounddevice as sd
            
            console.print("🔊 [bold blue]Dispositivos de áudio disponíveis:[/bold blue]")
            devices = sd.query_devices()
            
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    console.print(f"  {i}: 🎤 {device['name']}")
                    input_devices.append(i)
                else:
                    console.print(f"  {i}: 🔊 {device['name']}")
            
            if not input_devices:
                console.print("[bold red]❌ Nenhum dispositivo de entrada encontrado[/bold red]")
                return False
            
            console.print(f"✅ {len(input_devices)} dispositivo(s) de entrada encontrado(s)")
            return True
            
        except ImportError:
            console.print("[bold yellow]⚠️ sounddevice não instalado - pulando teste de áudio[/bold yellow]")
            return True
        except Exception as e:
            console.print(f"[bold red]❌ Erro no teste de áudio: {e}[/bold red]")
            return False
    
    def test_openai_connection(self):
        """Testa conexão com OpenAI"""
        try:
            import openai
            from dotenv import load_dotenv
            
            load_dotenv(self.env_file)
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                console.print("[bold red]❌ API Key não encontrada[/bold red]")
                return False
            
            client = openai.OpenAI(api_key=api_key)
            
            # Teste simples
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            console.print("✅ Conexão com OpenAI - OK")
            return True
            
        except ImportError:
            console.print("[bold yellow]⚠️ OpenAI não instalado - pulando teste[/bold yellow]")
            return True
        except Exception as e:
            console.print(f"[bold red]❌ Erro na conexão OpenAI: {e}[/bold red]")
            return False
    
    def run_full_setup(self):
        """Executa setup completo"""
        console.print(Panel.fit(
            "[bold blue]⚙️ SALES AGENT IA - SETUP[/bold blue]\n[cyan]Configuração inicial do sistema[/cyan]",
            border_style="blue"
        ))
        
        steps = [
            ("Verificando Python", self.check_python_version),
            ("Criando diretórios", self.create_directories),
            ("Instalando dependências", self.install_dependencies),
            ("Configurando ambiente", self.configure_environment),
            ("Testando dispositivos de áudio", self.test_audio_devices),
            ("Testando conexão OpenAI", self.test_openai_connection)
        ]
        
        success_count = 0
        
        for step_name, step_func in track(steps, description="Configurando..."):
            console.print(f"\n🔄 {step_name}...")
            if step_func():
                success_count += 1
            else:
                console.print(f"[bold red]❌ Falha em: {step_name}[/bold red]")
        
        console.print(f"\n📊 [bold blue]Resultado: {success_count}/{len(steps)} etapas concluídas[/bold blue]")
        
        if success_count == len(steps):
            console.print(Panel.fit(
                "[bold green]🎉 SETUP CONCLUÍDO COM SUCESSO![/bold green]\n\n"
                "[yellow]Para iniciar o sistema:[/yellow]\n"
                "[cyan]python sales_agent_main.py[/cyan]",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold yellow]⚠️ SETUP PARCIALMENTE CONCLUÍDO[/bold yellow]\n\n"
                "[red]Corrija os erros acima antes de prosseguir[/red]",
                border_style="yellow"
            ))
        
        return success_count == len(steps)

def main():
    """Função principal"""
    setup = SystemSetup()
    setup.run_full_setup()

if __name__ == "__main__":
    main()
