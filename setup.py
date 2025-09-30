"""
Script de configuração rápida para o Analisador de Reuniões
Execute este script para configurar tudo automaticamente
"""

import os
import sys
from pathlib import Path
import subprocess


def verificar_python():
    """Verifica se Python está instalado"""
    print("🐍 Verificando Python...")
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}."
                  f"{version.micro} - OK")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}."
                  f"{version.micro} - Versão muito antiga")
            print("   Necessário Python 3.8 ou superior")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar Python: {e}")
        return False


def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                              "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    except FileNotFoundError:
        print("❌ Arquivo requirements.txt não encontrado!")
        return False


def criar_estrutura_pastas():
    """Cria a estrutura de pastas necessária"""
    print("\n📁 Criando estrutura de pastas...")

    pastas = [
        "Reunioes em TXT",
        "Analises",
        ".cursor/rules"
    ]
    
    for pasta in pastas:
        Path(pasta).mkdir(parents=True, exist_ok=True)
        print(f"✅ Pasta criada: {pasta}")
    
    return True


def verificar_api_key():
    """Verifica se a API key está configurada"""
    print("\n🔑 Verificando API Key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OPENAI_API_KEY configurada!")
        return True
    else:
        print("❌ OPENAI_API_KEY não encontrada!")
        print("\n📝 Para configurar:")
        print("   Windows PowerShell: $env:OPENAI_API_KEY="
                  "'sk-sua-chave-aqui'")
        print("   Windows CMD: set OPENAI_API_KEY=sk-sua-chave-aqui")
        print("   Linux/Mac: export OPENAI_API_KEY="
                  "'sk-sua-chave-aqui'")
        return False


def criar_arquivo_exemplo():
    """Cria um arquivo de exemplo para teste"""
    print("\n📄 Criando arquivo de exemplo...")

    exemplo_transcricao = """REUNIÃO COM CLIENTE EXEMPLO
Data: 2024-12-01
Participantes: João Silva (CEO), Maria Santos (CTO), Pedro Costa (Vendedor)

PEDRO: Bom dia! Obrigado por aceitar esta reunião. Como está o projeto de digitalização?

JOÃO: Olá Pedro! Estamos com alguns desafios. O sistema atual está muito lento e nossos clientes estão reclamando.

MARIA: Exato. Temos problemas de performance críticos. Se não resolvermos em 30 dias, vamos perder contratos importantes.

PEDRO: Entendo a urgência. Qual o impacto financeiro estimado?

JOÃO: Estamos falando de R$ 500.000 em receita em risco. Precisamos de uma solução robusta e escalável.

MARIA: Temos orçamento aprovado de R$ 100.000 para este projeto. O prazo é crítico.

PEDRO: Perfeito! Nossa solução pode resolver isso em 20 dias. Vou enviar uma proposta detalhada.

JOÃO: Excelente! Quando podemos ter a proposta?

PEDRO: Até amanhã. Posso agendar uma apresentação para quinta-feira?

MARIA: Perfeito! Vou convidar o time técnico também.

PEDRO: Combinado! Vou preparar tudo e enviar por email.
"""
    
    arquivo_exemplo = Path("Reunioes em TXT/exemplo_cliente.txt")
    arquivo_exemplo.write_text(exemplo_transcricao, encoding="utf-8")
    print(f"✅ Arquivo de exemplo criado: {arquivo_exemplo}")


def testar_sistema():
    """Testa se o sistema está funcionando"""
    print("\n🧪 Testando sistema...")
    
    try:
        from analisador_reunioes import AnalisadorReunioes
        print("✅ Módulo principal importado com sucesso!")
        
        # Testa se consegue inicializar
        AnalisadorReunioes()
        print("✅ Analisador inicializado com sucesso!")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def main():
    """Função principal de setup"""
    print("🚀 CONFIGURAÇÃO DO ANALISADOR ESTRATÉGICO DE REUNIÕES")
    print("=" * 60)

    # Lista de verificações
    verificacoes = [
        ("Python", verificar_python),
        ("Dependências", instalar_dependencias),
        ("Estrutura de pastas", criar_estrutura_pastas),
        ("API Key", verificar_api_key),
        ("Sistema", testar_sistema)
    ]
    
    sucessos = 0
    total = len(verificacoes)
    
    for nome, funcao in verificacoes:
        if funcao():
            sucessos += 1
        print()  # Linha em branco

    # Cria arquivo de exemplo se tudo estiver OK
    if sucessos >= 4:  # Pelo menos 4 de 5 verificações
        criar_arquivo_exemplo()
    
    # Resultado final
    print("=" * 60)
    print(f"📊 RESULTADO: {sucessos}/{total} verificações passaram")

    if sucessos == total:
        print("🎉 CONFIGURAÇÃO COMPLETA!")
        print("\n📝 Próximos passos:")
        print("1. Configure sua OPENAI_API_KEY se ainda não fez")
        print("2. Coloque suas transcrições na pasta 'Reunioes em TXT'")
        print("3. Execute: python analisador_reunioes.py")
        print("4. Ou execute: python exemplo_uso.py para exemplos")
    elif sucessos >= 4:
        print("⚠️  CONFIGURAÇÃO QUASE COMPLETA!")
        print("   Configure apenas a OPENAI_API_KEY e estará pronto!")
    else:
        print("❌ CONFIGURAÇÃO INCOMPLETA!")
        print("   Resolva os problemas acima e execute novamente.")

    print("\n📚 Para mais informações, consulte o README.md")


if __name__ == "__main__":
    main()
