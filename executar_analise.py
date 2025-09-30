#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE EXECUÇÃO SIMPLIFICADO
Analisador Comercial Mestre - Cursor AI

Este script executa a análise de todas as reuniões de forma simples.
"""

from pathlib import Path
from analisador_comercial_mestre import AnalisadorComercialMestre


def main():
    """Executa a análise comercial de forma simplificada."""
    print("🎯 ANALISADOR COMERCIAL MESTRE")
    print("=" * 40)
    print("Iniciando análise de reuniões...")
    print()
    
    try:
        # Inicializar analisador
        analisador = AnalisadorComercialMestre()
        
        # Verificar se existem arquivos de transcrição
        reunioes_path = Path("Reunioes em TXT")
        if not reunioes_path.exists():
            print("❌ ERRO: Pasta 'Reunioes em TXT' não encontrada!")
            print("📁 Crie a pasta e adicione os arquivos .txt das transcrições.")
            return
        
        arquivos_txt = list(reunioes_path.glob("*.txt"))
        if not arquivos_txt:
            print("❌ ERRO: Nenhum arquivo .txt encontrado na pasta 'Reunioes em TXT'!")
            print("📄 Adicione os arquivos de transcrição (.txt) na pasta.")
            return
        
        print(f"📄 Encontrados {len(arquivos_txt)} arquivos de transcrição:")
        for arquivo in arquivos_txt:
            print(f"   • {arquivo.name}")
        print()
        
        # Processar todas as reuniões
        print("🔄 Processando reuniões...")
        resultados = analisador.processar_todas_reunioes()
        
        if resultados:
        print(f"\n✅ SUCESSO! {len(resultados)} reuniões analisadas.")
        print("📁 Resultados salvos em: Analises_Comerciais/")
            print()
            
            # Mostrar resumo dos resultados
            print("📊 RESUMO DOS RESULTADOS:")
            print("-" * 30)
            
            for cliente, analise in resultados.items():
                score = analise['Score_Prioridade']['Score_Geral']
                classificacao = analise['Score_Prioridade']['Classificacao']
                print(f"• {cliente}: {score}/10 ({classificacao})")
            
            print()
            print("📋 Para ver análises detalhadas, acesse a pasta 'Analises_Comerciais'")
            print("📊 Para overview geral, veja 'overview_geral.csv' e 'overview_geral.json'")
            
        else:
            print("❌ Nenhuma reunião foi processada com sucesso.")
            
    except Exception as e:
        print(f"❌ ERRO durante a execução: {e}")
        print("🔧 Verifique se todos os arquivos estão no lugar correto.")
        return
    
    print("\n🎉 Análise concluída!")

if __name__ == "__main__":
    main()
