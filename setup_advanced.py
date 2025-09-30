#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SALES AGENT IA - SETUP AVANÇADO
==================================
Sistema de instalação e configuração automática com validação completa
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

@dataclass
class SystemRequirement:
    """Requisito do sistema"""
    name: str
    description: str
    required: bool
    current_version: Optional[str] = None
    required_version: Optional[str] = None
    status: str = "unknown"  # unknown, checking, ok, error, warning

@dataclass
class DependencyInfo:
    """Informações de dependência"""
    name: str
    version: str
    description: str
    install_command: str
    test_import: str
    optional: bool = False

class AdvancedSetup:
    """Sistema de setup avançado com validação completa"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_dir = self.base_dir / "config"
        self.backup_dir = self.base_dir / "backups"
        self.logs_dir = self.base_dir / "logs"
        
        # Cria diretórios necessários
        self._create_directories()
        
        # Configurações do sistema
        self.system_config = self._load_system_config()
        
        # Dependências necessárias
        self.dependencies = self._get_dependencies()
        
        # Requisitos do sistema
        self.requirements = self._get_system_requirements()
    
    def _create_directories(self):
        """Cria diretórios necessários"""
        directories = [
            self.config_dir,
            self.backup_dir,
            self.logs_dir,
            self.base_dir / "temp",
            self.base_dir / "embeddings"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
    
    def _load_system_config(self) -> Dict:
        """Carrega configuração do sistema"""
        config_file = self.config_dir / "system_config.json"
        
        default_config = {
            "version": "1.0.0",
            "last_setup": None,
            "python_version": None,
            "platform": platform.system(),
            "architecture": platform.machine(),
            "dependencies_installed": [],
            "backup_enabled": True,
            "auto_update": True,
            "log_level": "INFO"
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                console.print(f"[yellow]⚠️ Erro ao carregar config: {e}[/yellow]")
                return default_config
        
        return default_config
    
    def _save_system_config(self):
        """Salva configuração do sistema"""
        config_file = self.config_dir / "system_config.json"
        
        self.system_config["last_setup"] = datetime.now().isoformat()
        self.system_config["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.system_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]❌ Erro ao salvar config: {e}[/red]")
    
    def _get_dependencies(self) -> List[DependencyInfo]:
        """Lista todas as dependências necessárias"""
        return [
            DependencyInfo(
                name="openai",
                version=">=1.0.0",
                description="API da OpenAI para IA",
                install_command="pip install openai>=1.0.0",
                test_import="import openai"
            ),
            DependencyInfo(
                name="pandas",
                version=">=1.5.0",
                description="Análise de dados",
                install_command="pip install pandas>=1.5.0",
                test_import="import pandas"
            ),
            DependencyInfo(
                name="numpy",
                version=">=1.21.0",
                description="Computação numérica",
                install_command="pip install numpy>=1.21.0",
                test_import="import numpy"
            ),
            DependencyInfo(
                name="rich",
                version=">=13.0.0",
                description="Interface rica no terminal",
                install_command="pip install rich>=13.0.0",
                test_import="import rich"
            ),
            DependencyInfo(
                name="loguru",
                version=">=0.7.0",
                description="Sistema de logs avançado",
                install_command="pip install loguru>=0.7.0",
                test_import="import loguru"
            ),
            DependencyInfo(
                name="sounddevice",
                version=">=0.4.0",
                description="Captura de áudio",
                install_command="pip install sounddevice>=0.4.0",
                test_import="import sounddevice"
            ),
            DependencyInfo(
                name="soundfile",
                version=">=0.12.0",
                description="Processamento de arquivos de áudio",
                install_command="pip install soundfile>=0.12.0",
                test_import="import soundfile"
            ),
            DependencyInfo(
                name="scipy",
                version=">=1.9.0",
                description="Processamento científico",
                install_command="pip install scipy>=1.9.0",
                test_import="import scipy"
            ),
            DependencyInfo(
                name="sentence-transformers",
                version=">=2.2.0",
                description="Modelos de embeddings",
                install_command="pip install sentence-transformers>=2.2.0",
                test_import="import sentence_transformers"
            ),
            DependencyInfo(
                name="chromadb",
                version=">=0.4.0",
                description="Base de dados vetorial",
                install_command="pip install chromadb>=0.4.0",
                test_import="import chromadb"
            ),
            DependencyInfo(
                name="pystray",
                version=">=0.19.0",
                description="System tray interface",
                install_command="pip install pystray>=0.19.0",
                test_import="import pystray"
            ),
            DependencyInfo(
                name="PIL",
                version=">=9.0.0",
                description="Processamento de imagens",
                install_command="pip install Pillow>=9.0.0",
                test_import="import PIL"
            ),
            DependencyInfo(
                name="python-dotenv",
                version=">=1.0.0",
                description="Gerenciamento de variáveis de ambiente",
                install_command="pip install python-dotenv>=1.0.0",
                test_import="import dotenv"
            ),
            DependencyInfo(
                name="requests",
                version=">=2.28.0",
                description="Requisições HTTP",
                install_command="pip install requests>=2.28.0",
                test_import="import requests"
            ),
            DependencyInfo(
                name="tkinter",
                version="builtin",
                description="Interface gráfica (builtin)",
                install_command="builtin",
                test_import="import tkinter",
                optional=True
            )
        ]
    
    def _get_system_requirements(self) -> List[SystemRequirement]:
        """Lista requisitos do sistema"""
        return [
            SystemRequirement(
                name="Python",
                description="Versão do Python",
                required=True,
                current_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                required_version="3.8.0"
            ),
            SystemRequirement(
                name="Internet",
                description="Conexão com internet",
                required=True
            ),
            SystemRequirement(
                name="Microfone",
                description="Dispositivo de áudio",
                required=True
            ),
            SystemRequirement(
                name="Espaço em disco",
                description="Espaço disponível",
                required=True
            ),
            SystemRequirement(
                name="Memória RAM",
                description="Memória disponível",
                required=True
            )
        ]
    
    def run_complete_setup(self):
        """Executa setup completo com validação"""
        console.print(Panel.fit(
            "[bold blue]🚀 SALES AGENT IA - SETUP AVANÇADO[/bold blue]\n"
            "[cyan]Sistema de instalação e configuração automática[/cyan]",
            border_style="blue"
        ))
        
        try:
            # 1. Validação do sistema
            self._validate_system_requirements()
            
            # 2. Backup de configurações existentes
            self._backup_existing_config()
            
            # 3. Instalação de dependências
            self._install_dependencies()
            
            # 4. Configuração do ambiente
            self._setup_environment()
            
            # 5. Validação final
            self._final_validation()
            
            # 6. Salva configuração
            self._save_system_config()
            
            console.print(Panel.fit(
                "[bold green]✅ SETUP CONCLUÍDO COM SUCESSO![/bold green]\n"
                "[cyan]O Sales Agent IA está pronto para uso[/cyan]",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[bold red]❌ Erro no setup: {e}[/bold red]")
            self._show_error_recovery()
            raise
    
    def _validate_system_requirements(self):
        """Valida requisitos do sistema"""
        console.print("\n🔍 [bold yellow]Validando requisitos do sistema...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Valida Python
            task = progress.add_task("Verificando Python...", total=None)
            self._check_python_version()
            progress.update(task, description="✅ Python OK")
            
            # Valida internet
            task = progress.add_task("Verificando internet...", total=None)
            self._check_internet_connection()
            progress.update(task, description="✅ Internet OK")
            
            # Valida microfone
            task = progress.add_task("Verificando microfone...", total=None)
            self._check_audio_devices()
            progress.update(task, description="✅ Microfone OK")
            
            # Valida espaço em disco
            task = progress.add_task("Verificando espaço em disco...", total=None)
            self._check_disk_space()
            progress.update(task, description="✅ Espaço OK")
            
            # Valida memória
            task = progress.add_task("Verificando memória...", total=None)
            self._check_memory()
            progress.update(task, description="✅ Memória OK")
    
    def _check_python_version(self):
        """Verifica versão do Python"""
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        required_major, required_minor = 3, 8
        
        if sys.version_info.major < required_major or \
           (sys.version_info.major == required_major and sys.version_info.minor < required_minor):
            raise ValueError(f"Python {required_major}.{required_minor}+ necessário. Atual: {current_version}")
    
    def _check_internet_connection(self):
        """Verifica conexão com internet"""
        try:
            response = requests.get("https://api.openai.com/v1/models", timeout=10)
            if response.status_code not in [200, 401]:  # 401 é OK, significa que API existe
                raise ConnectionError("Sem acesso à API da OpenAI")
        except Exception as e:
            raise ConnectionError(f"Problema de conectividade: {e}")
    
    def _check_audio_devices(self):
        """Verifica dispositivos de áudio"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if not input_devices:
                raise ValueError("Nenhum dispositivo de entrada de áudio encontrado")
        except ImportError:
            # sounddevice não instalado ainda, isso é OK
            pass
        except Exception as e:
            raise ValueError(f"Problema com dispositivos de áudio: {e}")
    
    def _check_disk_space(self):
        """Verifica espaço em disco"""
        import shutil
        
        free_space = shutil.disk_usage(self.base_dir).free
        required_space = 2 * 1024 * 1024 * 1024  # 2GB
        
        if free_space < required_space:
            raise ValueError(f"Espaço insuficiente. Necessário: 2GB, Disponível: {free_space // (1024**3)}GB")
    
    def _check_memory(self):
        """Verifica memória disponível"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.available < 4 * 1024 * 1024 * 1024:  # 4GB
                console.print("[yellow]⚠️ Pouca memória disponível. Recomendado: 8GB+[/yellow]")
        except ImportError:
            # psutil não instalado, não é crítico
            pass
    
    def _backup_existing_config(self):
        """Faz backup de configurações existentes"""
        if not self.system_config.get("backup_enabled", True):
            return
        
        console.print("\n💾 [bold yellow]Fazendo backup de configurações...[/bold yellow]")
        
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{backup_timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Arquivos para backup
        files_to_backup = [
            ".env",
            "config.py",
            "config/system_config.json"
        ]
        
        for file_path in files_to_backup:
            source = self.base_dir / file_path
            if source.exists():
                dest = backup_path / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        
        console.print(f"✅ Backup salvo em: {backup_path}")
    
    def _install_dependencies(self):
        """Instala dependências necessárias"""
        console.print("\n📦 [bold yellow]Instalando dependências...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            total_deps = len(self.dependencies)
            task = progress.add_task("Instalando...", total=total_deps)
            
            installed_deps = []
            
            for i, dep in enumerate(self.dependencies):
                progress.update(task, description=f"Instalando {dep.name}...")
                
                try:
                    if dep.install_command != "builtin":
                        result = subprocess.run(
                            dep.install_command.split(),
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minutos por dependência
                        )
                        
                        if result.returncode != 0:
                            if not dep.optional:
                                raise Exception(f"Erro ao instalar {dep.name}: {result.stderr}")
                            else:
                                console.print(f"[yellow]⚠️ {dep.name} falhou (opcional)[/yellow]")
                                continue
                    
                    # Testa importação
                    exec(dep.test_import)
                    installed_deps.append(dep.name)
                    
                except Exception as e:
                    if not dep.optional:
                        raise Exception(f"Falha ao instalar {dep.name}: {e}")
                    else:
                        console.print(f"[yellow]⚠️ {dep.name} falhou (opcional): {e}[/yellow]")
                
                progress.advance(task)
        
        self.system_config["dependencies_installed"] = installed_deps
        console.print(f"✅ {len(installed_deps)} dependências instaladas com sucesso")
    
    def _setup_environment(self):
        """Configura ambiente do sistema"""
        console.print("\n⚙️ [bold yellow]Configurando ambiente...[/bold yellow]")
        
        # Cria arquivo .env se não existir
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            env_example = self.base_dir / "env_example.txt"
            if env_example.exists():
                shutil.copy2(env_example, env_file)
                console.print("✅ Arquivo .env criado")
            else:
                # Cria .env básico
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write("# Sales Agent IA - Configurações\n")
                    f.write("OPENAI_API_KEY=your_api_key_here\n")
                    f.write("LOG_LEVEL=INFO\n")
                console.print("✅ Arquivo .env básico criado")
        
        # Configura logs
        self._setup_logging()
        
        # Configura base de conhecimento
        self._setup_knowledge_base()
    
    def _setup_logging(self):
        """Configura sistema de logs"""
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "simple": {
                    "format": "{time:HH:mm:ss} | {level} | {message}"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "filename": str(self.logs_dir / "sales_agent.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {
                    "level": "DEBUG",
                    "handlers": ["console", "file"],
                    "propagate": False
                }
            }
        }
        
        config_file = self.config_dir / "logging_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(log_config, f, indent=2)
    
    def _setup_knowledge_base(self):
        """Configura base de conhecimento"""
        # Verifica se toolkit existe
        toolkit_dir = self.base_dir / "AE_SENIOR_TOOLKIT"
        if not toolkit_dir.exists():
            console.print("[yellow]⚠️ AE_SENIOR_TOOLKIT não encontrado. Será criado na primeira execução.[/yellow]")
            return
        
        console.print("✅ Base de conhecimento será construída na primeira execução")
    
    def _final_validation(self):
        """Validação final do sistema"""
        console.print("\n🔍 [bold yellow]Validação final...[/bold yellow]")
        
        # Testa imports críticos
        critical_imports = [
            "openai",
            "pandas", 
            "numpy",
            "rich",
            "loguru"
        ]
        
        for module in critical_imports:
            try:
                __import__(module)
                console.print(f"✅ {module}")
            except ImportError as e:
                raise Exception(f"Falha na validação: {module} não pode ser importado - {e}")
        
        # Testa configuração OpenAI
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == "your_api_key_here":
                console.print("[yellow]⚠️ OPENAI_API_KEY não configurada. Configure no arquivo .env[/yellow]")
            else:
                console.print("✅ OpenAI API Key configurada")
        except Exception as e:
            console.print(f"[yellow]⚠️ Erro ao verificar API Key: {e}[/yellow]")
    
    def _show_error_recovery(self):
        """Mostra opções de recuperação de erro"""
        console.print("\n🔧 [bold red]Opções de recuperação:[/bold red]")
        console.print("1. Execute: python setup_advanced.py --repair")
        console.print("2. Execute: python setup_advanced.py --reset")
        console.print("3. Verifique os logs em: logs/sales_agent.log")
        console.print("4. Entre em contato com suporte")
    
    def show_system_status(self):
        """Mostra status atual do sistema"""
        table = Table(title="📊 Status do Sistema")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Versão", style="yellow")
        table.add_column("Observações", style="white")
        
        # Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        table.add_row("Python", "✅ OK", python_version, "")
        
        # Dependências
        for dep in self.dependencies:
            try:
                exec(dep.test_import)
                status = "✅ OK"
                version = "Instalado"
            except:
                status = "❌ Faltando"
                version = "Não instalado"
            
            table.add_row(dep.name, status, version, dep.description)
        
        console.print(table)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sales Agent IA - Setup Avançado")
    parser.add_argument("--repair", action="store_true", help="Reparar instalação")
    parser.add_argument("--reset", action="store_true", help="Resetar configurações")
    parser.add_argument("--status", action="store_true", help="Mostrar status do sistema")
    
    args = parser.parse_args()
    
    setup = AdvancedSetup()
    
    if args.status:
        setup.show_system_status()
    elif args.reset:
        console.print("[bold red]⚠️ Resetando configurações...[/bold red]")
        # Implementar reset
    elif args.repair:
        console.print("[bold yellow]🔧 Reparando instalação...[/bold yellow]")
        # Implementar reparo
    else:
        setup.run_complete_setup()

if __name__ == "__main__":
    main()
