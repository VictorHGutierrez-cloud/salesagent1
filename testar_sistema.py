#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE TESTE - Analisador Comercial Mestre
Testa o sistema com uma transcrição de exemplo
"""

from analisador_comercial_mestre import AnalisadorComercialMestre
from pathlib import Path


def criar_transcricao_exemplo():
    """Cria uma transcrição de exemplo para teste."""
    transcricao_exemplo = """
REUNIÃO COM CLIENTE - TECH SOLUTIONS LTDA
Data: 15/01/2024
Participantes: João Silva (Cliente), Maria Santos (Vendedora)

Maria: Olá João, obrigada por aceitar esta reunião. Como está o projeto de digitalização na Tech Solutions?

João: Olha Maria, estamos com um problema sério. Nossa produtividade caiu 30% nos últimos 3 meses porque o sistema atual está travando constantemente. É crítico resolver isso urgentemente.

Maria: Entendo a urgência. Pode me contar mais sobre os impactos que vocês estão sentindo?

João: Sim, claro. Estamos perdendo clientes para a concorrência porque não conseguimos entregar no prazo. O CEO está pressionando nossa equipe e eu sou responsável por essa área. Precisamos de uma solução que funcione imediatamente.

Maria: E qual seria o orçamento que vocês têm disponível para investir em uma solução?

João: Temos um orçamento de R$ 50.000 para resolver isso. O ROI precisa ser rápido porque estamos perdendo muito dinheiro. Vocês têm algo que atenda exatamente nossa necessidade?

Maria: Sim, nossa solução é perfeita para o seu caso. Já resolvemos problemas similares em outras empresas do setor. Quando vocês gostariam de implementar?

João: O mais rápido possível. Preciso apresentar uma solução para o CEO até o final do mês. Vocês conseguem fazer uma demonstração esta semana?

Maria: Perfeito! Vou agendar para quinta-feira. Você poderia convidar mais alguém da equipe?

João: Sim, vou chamar o gerente de TI e o coordenador de operações. Eles precisam aprovar também.

Maria: Excelente! Vou preparar uma apresentação focada nos seus problemas específicos. Até quinta então!
"""
    return transcricao_exemplo


def main():
    """Executa teste do sistema."""
    print("🧪 TESTE DO ANALISADOR COMERCIAL MESTRE")
    print("=" * 50)
    
    # Criar pasta de reuniões se não existir
    reunioes_path = Path("Reunioes em TXT")
    reunioes_path.mkdir(exist_ok=True)
    
    # Criar transcrição de exemplo
    transcricao = criar_transcricao_exemplo()
    
    # Salvar transcrição de exemplo
    arquivo_exemplo = reunioes_path / "tech_solutions_exemplo.txt"
    with open(arquivo_exemplo, 'w', encoding='utf-8') as f:
        f.write(transcricao)
    
    print(f"📄 Transcrição de exemplo criada: {arquivo_exemplo}")
    print()
    
    # Inicializar analisador
    analisador = AnalisadorComercialMestre()
    
    # Processar transcrição de exemplo
    print("🔄 Processando transcrição de exemplo...")
    resultado = analisador.analisar_transcricao("Tech Solutions", transcricao)
    
    # Mostrar resultados
    print("\n✅ ANÁLISE CONCLUÍDA!")
    print("=" * 30)
    
    # Mostrar scores
    scores = resultado['Score_Prioridade']
    print(f"📊 SCORES DE PRIORIDADE:")
    print(f"   • Urgência: {scores['Urgencia']}/10")
    print(f"   • Autoridade: {scores['Autoridade']}/10")
    print(f"   • Orçamento: {scores['Orcamento']}/10")
    print(f"   • Fit da Solução: {scores['Fit_Solucao']}/10")
    print(f"   • Timing: {scores['Timing']}/10")
    print(f"   • SCORE GERAL: {scores['Score_Geral']}/10")
    print(f"   • CLASSIFICAÇÃO: {scores['Classificacao']}")
    
    # Mostrar resumo executivo
    print(f"\n📋 RESUMO EXECUTIVO:")
    print(f"   {resultado['Resumo_FollowUp']['Resumo_Executivo']}")
    
    # Mostrar próximos passos
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    for passo in resultado['Proximos_Passos']['Acoes_Imediatas']:
        print(f"   • {passo}")
    
    # Mostrar feedback pessoal
    feedback = resultado['Feedback_Pessoal']
    print(f"\n👤 FEEDBACK PESSOAL:")
    print(f"   • Total de perguntas: {feedback['Total_Perguntas']}")
    print(f"   • Perguntas abertas: {feedback['Perguntas_Abertas']}")
    print(f"   • Score de confiança: {feedback['Score_Confianca']}/10")
    
    print(f"\n📁 Resultados salvos em: Analises_Comerciais/Tech_Solutions/")
    print(f"📊 Para ver todos os detalhes, acesse os arquivos na pasta do cliente.")
    
    print(f"\n🎉 Teste concluído com sucesso!")
    print(f"💡 Agora você pode usar o sistema com suas próprias transcrições!")

if __name__ == "__main__":
    main()
