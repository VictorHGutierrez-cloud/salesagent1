"""
🧪 SALES AGENT IA - TESTE OFFLINE
================================
Testa todas as funcionalidades EXCETO OpenAI
"""

import os
from pathlib import Path
from dotenv import load_dotenv

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False

def print_status(text, status="info"):
    """Print com status colorido"""
    if RICH_AVAILABLE:
        colors = {"ok": "green", "error": "red", "info": "blue", "warn": "yellow"}
        console.print(text, style=colors.get(status, "white"))
    else:
        icons = {"ok": "✅", "error": "❌", "info": "ℹ️", "warn": "⚠️"}
        print(f"{icons.get(status, '•')} {text}")

def test_environment():
    """Testa ambiente"""
    print_status("TESTANDO AMBIENTE", "info")
    
    # 1. Arquivo .env
    if os.path.exists('.env'):
        print_status("Arquivo .env encontrado", "ok")
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key and len(api_key) > 20:
            print_status(f"API Key configurada (sk-...{api_key[-8:]})", "ok")
        else:
            print_status("API Key não configurada", "error")
    else:
        print_status("Arquivo .env não encontrado", "error")
    
    # 2. Diretórios
    dirs_to_check = ['temp', 'embeddings', 'logs', 'AE_SENIOR_TOOLKIT']
    for dir_name in dirs_to_check:
        if Path(dir_name).exists():
            print_status(f"Diretório {dir_name}/ encontrado", "ok")
        else:
            print_status(f"Diretório {dir_name}/ não encontrado", "warn")

def test_toolkit():
    """Testa carregamento do toolkit"""
    print_status("\nTESTANDO TOOLKIT DE VENDAS", "info")
    
    toolkit_dir = Path("AE_SENIOR_TOOLKIT")
    
    if not toolkit_dir.exists():
        print_status("AE_SENIOR_TOOLKIT não encontrado", "error")
        return
    
    # Conta arquivos
    txt_files = list(toolkit_dir.rglob("*.txt"))
    print_status(f"Encontrados {len(txt_files)} arquivos .txt", "ok")
    
    # Testa leitura de alguns arquivos importantes
    key_files = [
        "00_MASTER_INDEX.txt",
        "02_QUALIFICACAO_LEADS/MEDDIC_Framework_Avancado.txt",
        "06_NEGOCIACAO_FECHAMENTO/Tecnicas_Fechamento_Avancadas.txt"
    ]
    
    loaded_count = 0
    for file_path in key_files:
        full_path = toolkit_dir / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 100:
                        print_status(f"✓ {file_path} ({len(content)} chars)", "ok")
                        loaded_count += 1
                    else:
                        print_status(f"? {file_path} muito pequeno", "warn")
            except Exception as e:
                print_status(f"✗ {file_path} erro: {e}", "error")
        else:
            print_status(f"✗ {file_path} não encontrado", "warn")
    
    print_status(f"Carregados {loaded_count}/{len(key_files)} arquivos principais", "ok")

def test_dependencies():
    """Testa dependências Python"""
    print_status("\nTESTANDO DEPENDÊNCIAS", "info")
    
    # Dependências críticas
    critical_deps = [
        ("openai", "OpenAI GPT"),
        ("rich", "Interface"),
        ("dotenv", "Configurações"),
        ("pathlib", "Arquivos")
    ]
    
    for module_name, description in critical_deps:
        try:
            if module_name == "dotenv":
                from dotenv import load_dotenv
            elif module_name == "pathlib":
                from pathlib import Path
            else:
                __import__(module_name)
            print_status(f"{description} disponível", "ok")
        except ImportError:
            print_status(f"{description} NÃO disponível", "error")
    
    # Dependências opcionais
    optional_deps = [
        ("sounddevice", "Captura de áudio"),
        ("soundfile", "Processamento de áudio"),
        ("tkinter", "Interface gráfica"),
        ("sentence_transformers", "Embeddings"),
        ("pandas", "Análise de dados")
    ]
    
    print_status("\nDependências opcionais:", "info")
    available_count = 0
    
    for module_name, description in optional_deps:
        try:
            if module_name == "tkinter":
                import tkinter
            else:
                __import__(module_name)
            print_status(f"✓ {description}", "ok")
            available_count += 1
        except ImportError:
            print_status(f"✗ {description}", "warn")
    
    print_status(f"{available_count}/{len(optional_deps)} dependências opcionais disponíveis", "info")

def simulate_knowledge_base():
    """Simula criação de base de conhecimento"""
    print_status("\nSIMULANDO BASE DE CONHECIMENTO", "info")
    
    toolkit_dir = Path("AE_SENIOR_TOOLKIT")
    
    if not toolkit_dir.exists():
        print_status("Toolkit não disponível para simulação", "error")
        return
    
    # Simula extração de conhecimento
    chunks = []
    
    for txt_file in toolkit_dir.rglob("*.txt"):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Simula divisão em chunks
                lines = content.split('\n')
                sections = []
                current_section = []
                
                for line in lines:
                    if any(marker in line for marker in ['===', '---', '###', '🎯']):
                        if current_section:
                            sections.append('\n'.join(current_section))
                            current_section = []
                    current_section.append(line)
                
                if current_section:
                    sections.append('\n'.join(current_section))
                
                # Adiciona chunks válidos
                for section in sections:
                    if len(section.strip()) > 100:
                        chunks.append({
                            "source": str(txt_file.relative_to(toolkit_dir)),
                            "content": section[:200] + "...",
                            "length": len(section)
                        })
        except:
            pass
    
    print_status(f"Extraídos {len(chunks)} chunks de conhecimento", "ok")
    
    # Mostra alguns exemplos
    if chunks:
        print_status("\nExemplos de chunks:", "info")
        for i, chunk in enumerate(chunks[:3], 1):
            print_status(f"{i}. [{chunk['source']}] {chunk['content'][:80]}...", "info")

def main():
    """Função principal"""
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold blue]🧪 SALES AGENT IA - TESTE OFFLINE[/bold blue]\n"
            "[cyan]Validando sistema sem depender da OpenAI[/cyan]",
            border_style="blue"
        ))
    else:
        print("🧪 SALES AGENT IA - TESTE OFFLINE")
        print("=" * 50)
    
    # Executa todos os testes
    test_environment()
    test_toolkit()
    test_dependencies()
    simulate_knowledge_base()
    
    # Resumo final
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold green]✅ TESTES OFFLINE CONCLUÍDOS![/bold green]\n\n"
            "[yellow]PRÓXIMOS PASSOS:[/yellow]\n"
            "[cyan]1. Adicione créditos na OpenAI[/cyan]\n"
            "[cyan]2. Execute: python sales_agent_simple.py[/cyan]\n"
            "[cyan]3. Teste simulador de vendas[/cyan]",
            border_style="green"
        ))
    else:
        print("\n" + "=" * 50)
        print("✅ TESTES OFFLINE CONCLUÍDOS!")
        print("\nPRÓXIMOS PASSOS:")
        print("1. Adicione créditos na OpenAI")
        print("2. Execute: python sales_agent_simple.py")
        print("3. Teste simulador de vendas")
        print("=" * 50)

if __name__ == "__main__":
    main()
