#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SALES AGENT IA - INSTALADOR AVANÇADO
======================================
Instala e configura o sistema completo com todas as melhorias
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm

console = Console()

def main():
    """Instalador principal"""
    console.print(Panel.fit(
        "[bold blue]🚀 SALES AGENT IA - INSTALADOR AVANÇADO[/bold blue]\n"
        "[cyan]Instalação completa com todas as melhorias implementadas[/cyan]",
        border_style="blue"
    ))
    
    # Verifica Python
    if sys.version_info < (3, 8):
        console.print("[bold red]❌ Python 3.8+ necessário![/bold red]")
        return
    
    console.print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Pergunta sobre instalação
    if not Confirm.ask("Deseja instalar o Sales Agent IA Avançado?"):
        console.print("❌ Instalação cancelada")
        return
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            # 1. Instala dependências básicas
            task = progress.add_task("Instalando dependências básicas...", total=100)
            
            basic_deps = [
                "openai>=1.0.0",
                "pandas>=1.5.0", 
                "numpy>=1.21.0",
                "rich>=13.0.0",
                "loguru>=0.7.0",
                "python-dotenv>=1.0.0",
                "requests>=2.28.0"
            ]
            
            for dep in basic_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             capture_output=True, check=True)
                progress.advance(task, advance=100//len(basic_deps))
            
            progress.update(task, description="✅ Dependências básicas instaladas")
            
            # 2. Instala dependências de áudio
            task = progress.add_task("Instalando dependências de áudio...", total=100)
            
            audio_deps = [
                "sounddevice>=0.4.0",
                "soundfile>=0.12.0",
                "scipy>=1.9.0"
            ]
            
            for dep in audio_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             capture_output=True, check=True)
                progress.advance(task, advance=100//len(audio_deps))
            
            progress.update(task, description="✅ Dependências de áudio instaladas")
            
            # 3. Instala dependências de IA
            task = progress.add_task("Instalando dependências de IA...", total=100)
            
            ai_deps = [
                "sentence-transformers>=2.2.0",
                "chromadb>=0.4.0"
            ]
            
            for dep in ai_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             capture_output=True, check=True)
                progress.advance(task, advance=100//len(ai_deps))
            
            progress.update(task, description="✅ Dependências de IA instaladas")
            
            # 4. Instala dependências opcionais
            task = progress.add_task("Instalando dependências opcionais...", total=100)
            
            optional_deps = [
                "pystray>=0.19.0",
                "Pillow>=9.0.0",
                "psutil>=5.9.0",
                "plyer>=2.1.0"
            ]
            
            for dep in optional_deps:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                 capture_output=True, check=True)
                except:
                    pass  # Opcionais podem falhar
                progress.advance(task, advance=100//len(optional_deps))
            
            progress.update(task, description="✅ Dependências opcionais instaladas")
            
            # 5. Cria estrutura de diretórios
            task = progress.add_task("Criando estrutura de diretórios...", total=100)
            
            directories = [
                "config",
                "backups", 
                "logs",
                "temp",
                "embeddings"
            ]
            
            for directory in directories:
                Path(directory).mkdir(exist_ok=True)
                progress.advance(task, advance=100//len(directories))
            
            progress.update(task, description="✅ Estrutura criada")
            
            # 6. Cria arquivo .env
            task = progress.add_task("Configurando ambiente...", total=100)
            
            env_content = """# Sales Agent IA - Configurações Avançadas
OPENAI_API_KEY=your_api_key_here
LOG_LEVEL=INFO

# Configurações de áudio
SAMPLE_RATE=16000
CHANNELS=1
AUDIO_THRESHOLD=0.01

# Configurações de IA
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
WHISPER_MODEL=whisper-1

# Configurações de interface
OVERLAY_POSITION=top-right
OVERLAY_OPACITY=0.9
OVERLAY_WIDTH=400
OVERLAY_HEIGHT=200

# Configurações de backup
BACKUP_ENABLED=true
BACKUP_INTERVAL=24
MAX_BACKUPS=10

# Configurações de logs
LOG_RETENTION_DAYS=30
LOG_MAX_FILE_SIZE=10MB
"""
            
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            
            progress.advance(task, 50)
            
            # 7. Cria script de execução
            launcher_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
🚀 SALES AGENT IA - LAUNCHER
===========================
Script de execução principal
\"\"\"

import sys
from pathlib import Path

# Adiciona diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sales_agent_advanced import main
    main()
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Execute: python install_advanced.py")
except Exception as e:
    print(f"❌ Erro: {e}")
"""
            
            with open("run_sales_agent.py", "w", encoding="utf-8") as f:
                f.write(launcher_content)
            
            progress.advance(task, 50)
            progress.update(task, description="✅ Ambiente configurado")
        
        # 8. Executa setup inicial
        console.print("\n🔧 [bold yellow]Executando setup inicial...[/yellow]")
        
        try:
            from setup_advanced import AdvancedSetup
            setup = AdvancedSetup()
            setup.run_complete_setup()
        except Exception as e:
            console.print(f"[yellow]⚠️ Setup automático falhou: {e}[/yellow]")
            console.print("Execute manualmente: python setup_advanced.py")
        
        # 9. Cria arquivo de instruções
        instructions = f"""
# 🚀 SALES AGENT IA - SISTEMA AVANÇADO INSTALADO

## ✅ Instalação Concluída em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

### 🎯 Como Usar

1. **Configurar OpenAI API Key:**
   - Edite o arquivo `.env`
   - Substitua `your_api_key_here` pela sua API key da OpenAI

2. **Executar o Sistema:**
   ```bash
   python run_sales_agent.py
   ```
   
   Ou diretamente:
   ```bash
   python sales_agent_advanced.py
   ```

3. **Interface Gráfica:**
   ```bash
   python config_gui.py
   ```

### 🔧 Componentes Instalados

- ✅ Setup Avançado (`setup_advanced.py`)
- ✅ Backup Manager (`backup_manager.py`) 
- ✅ Sistema de Logs (`logging_system.py`)
- ✅ Monitor de Dependências (`dependency_monitor.py`)
- ✅ Interface Gráfica (`config_gui.py`)
- ✅ Sistema Integrado (`sales_agent_advanced.py`)

### 📁 Estrutura de Arquivos

```
Sales Agent/
├── run_sales_agent.py          # 🚀 Launcher principal
├── sales_agent_advanced.py     # 🎯 Sistema integrado
├── setup_advanced.py           # ⚙️ Setup automático
├── backup_manager.py           # 💾 Gerenciador de backup
├── logging_system.py           # 📝 Sistema de logs
├── dependency_monitor.py       # 🔍 Monitor de dependências
├── config_gui.py              # 🖥️ Interface gráfica
├── .env                       # 🔑 Configurações
├── config/                    # 📁 Configurações do sistema
├── backups/                   # 💾 Backups automáticos
├── logs/                      # 📝 Logs do sistema
└── temp/                      # 📁 Arquivos temporários
```

### 🆘 Suporte

- Execute `python sales_agent_advanced.py --status` para verificar status
- Execute `python sales_agent_advanced.py --setup` para reconfigurar
- Consulte os logs em `logs/` para debugging
- Use `python config_gui.py` para configurações visuais

### 🎉 Pronto para Vender!

O Sales Agent IA Avançado está instalado e pronto para uso!
"""
        
        with open("INSTRUCOES_INSTALACAO_AVANCADA.md", "w", encoding="utf-8") as f:
            f.write(instructions)
        
        # Sucesso!
        console.print(Panel.fit(
            "[bold green]✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO![/bold green]\n"
            "[cyan]O Sales Agent IA Avançado está pronto para uso[/cyan]\n\n"
            "[yellow]Próximos passos:[/yellow]\n"
            "1. Configure sua OpenAI API Key no arquivo .env\n"
            "2. Execute: python run_sales_agent.py\n"
            "3. Use: python config_gui.py para configurações",
            border_style="green"
        ))
        
        # Pergunta se quer executar agora
        if Confirm.ask("Deseja executar o sistema agora?"):
            console.print("\n🚀 [bold green]Executando Sales Agent IA Avançado...[/green]")
            try:
                from sales_agent_advanced import main
                main()
            except Exception as e:
                console.print(f"❌ Erro ao executar: {e}")
                console.print("Execute manualmente: python run_sales_agent.py")
    
    except Exception as e:
        console.print(f"\n❌ [bold red]Erro na instalação: {e}[/bold red]")
        console.print("Tente executar: python setup_advanced.py")

if __name__ == "__main__":
    main()
