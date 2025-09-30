"""
🚀 SALES AGENT IA - VERSÃO SIMPLIFICADA
=====================================
Sistema básico para teste inicial com OpenAI
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

try:
    import openai
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Carrega configurações
load_dotenv()

def setup_console():
    """Configura console de output"""
    if RICH_AVAILABLE:
        return Console()
    else:
        return None

def print_formatted(text, style="", console=None):
    """Print formatado que funciona com ou sem rich"""
    if console and RICH_AVAILABLE:
        console.print(text, style=style)
    else:
        print(text)

def test_openai_connection():
    """Testa conexão com OpenAI"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        print("🔄 Testando conexão com OpenAI...")
        
        # Teste simples
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um consultor de vendas."},
                {"role": "user", "content": "Cliente disse: 'Está muito caro'. Dê uma sugestão rápida."}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        suggestion = response.choices[0].message.content
        
        print("✅ Conexão OpenAI - OK!")
        print(f"💡 Sugestão de teste: {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão OpenAI: {e}")
        return False

def read_sales_toolkit():
    """Lê alguns arquivos do toolkit como exemplo"""
    toolkit_dir = Path("AE_SENIOR_TOOLKIT")
    
    if not toolkit_dir.exists():
        print(f"❌ Diretório {toolkit_dir} não encontrado")
        return []
    
    techniques = []
    
    # Lê alguns arquivos principais
    key_files = [
        "02_QUALIFICACAO_LEADS/MEDDIC_Framework_Avancado.txt",
        "06_NEGOCIACAO_FECHAMENTO/Tecnicas_Fechamento_Avancadas.txt",
        "12_OBJECTION_HANDLING"  # Diretório inteiro se existir
    ]
    
    for file_path in key_files:
        full_path = toolkit_dir / file_path
        
        if full_path.exists():
            if full_path.is_file():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:500]  # Primeiros 500 chars
                        techniques.append({
                            "source": str(file_path),
                            "content": content,
                            "type": "framework"
                        })
                except:
                    pass
    
    print(f"📚 Carregadas {len(techniques)} técnicas do toolkit")
    return techniques

def simulate_sales_conversation():
    """Simula uma conversa de vendas para teste"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Configure OPENAI_API_KEY primeiro")
        return
    
    client = openai.OpenAI(api_key=api_key)
    techniques = read_sales_toolkit()
    
    # Contexto do toolkit
    context = "\n".join([t["content"][:200] for t in techniques[:2]])
    
    print("\n🎯 SIMULADOR DE VENDAS IA")
    print("=" * 50)
    print("Digite frases que um cliente diria.")
    print("O sistema dará sugestões baseadas no seu toolkit.")
    print("Digite 'sair' para encerrar.\n")
    
    conversation_history = []
    
    while True:
        try:
            client_input = input("🗣️ Cliente: ").strip()
            
            if client_input.lower() in ['sair', 'exit', 'quit']:
                break
            
            if not client_input:
                continue
            
            conversation_history.append(f"Cliente: {client_input}")
            
            # Prompt para o GPT
            prompt = f"""Você é meu consultor estratégico de vendas IA.

CONTEXTO DO TOOLKIT:
{context}

CONVERSA ATUAL:
{chr(10).join(conversation_history[-3:])}

CLIENTE DISSE: "{client_input}"

Forneça uma sugestão estratégica IMEDIATA em máximo 2 frases curtas:"""

            print("🤔 Analisando...")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            suggestion = response.choices[0].message.content
            print(f"💡 SUGESTÃO: {suggestion}\n")
            
            time.sleep(0.5)  # Pausa para simular processamento
            
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    console = setup_console()
    
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold blue]🚀 SALES AGENT IA - TESTE BÁSICO[/bold blue]\n"
            "[cyan]Versão simplificada para validação[/cyan]",
            border_style="blue"
        ))
    else:
        print("🚀 SALES AGENT IA - TESTE BÁSICO")
        print("=" * 40)
    
    print("\n📋 CHECKLIST DE VALIDAÇÃO:")
    
    # 1. Verifica arquivo .env
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
    else:
        print("❌ Arquivo .env não encontrado")
        return
    
    # 2. Testa OpenAI
    if test_openai_connection():
        print("✅ OpenAI configurada corretamente")
    else:
        print("❌ Problema com OpenAI")
        return
    
    # 3. Verifica toolkit
    if Path("AE_SENIOR_TOOLKIT").exists():
        print("✅ Toolkit encontrado")
    else:
        print("❌ AE_SENIOR_TOOLKIT não encontrado")
    
    print("\n🎯 SISTEMA PRONTO! Iniciando simulador...\n")
    
    # Inicia simulador
    simulate_sales_conversation()
    
    print("\n📊 PRÓXIMOS PASSOS:")
    print("1. ✅ OpenAI funcionando")
    print("2. ⏳ Instalar dependências de áudio")
    print("3. ⏳ Ativar captura de áudio em tempo real")
    print("4. ⏳ Interface de overlay")
    
    print("\n👋 Obrigado por testar o Sales Agent IA!")

if __name__ == "__main__":
    main()
