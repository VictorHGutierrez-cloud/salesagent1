#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALISADOR COMERCIAL MESTRE - Cursor AI
Sistema de Inteligência Comercial para Análise de Reuniões

Transforma transcrições de reuniões em insights estratégicos acionáveis.
"""

import json
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')


class AnalisadorComercialMestre:
    def __init__(self, workspace_path: str = None):
        """
        Inicializa o analisador comercial mestre.
        
        Args:
            workspace_path: Caminho do workspace (padrão: diretório atual)
        """
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.analises_path = self.workspace_path / "Analises_Comerciais"
        self.reunioes_path = self.workspace_path / "Reunioes em TXT"
        
        # Criar diretórios se não existirem
        self.analises_path.mkdir(exist_ok=True)
        self.reunioes_path.mkdir(exist_ok=True)
        
        # Configurações de análise
        self.palavras_chave_urgencia = [
            'urgente', 'crítico', 'emergência', 'prazo', 'deadline',
            'problema sério', 'perdendo', 'competição', 'pressão'
        ]
        
        self.palavras_chave_autoridade = [
            'decido', 'aprovamos', 'nossa equipe', 'vou implementar',
            'tenho autonomia', 'sou responsável', 'minha decisão'
        ]
        
        self.palavras_chave_orcamento = [
            'orçamento', 'investimento', 'custo', 'valor', 'preço',
            'ROI', 'retorno', 'economia', 'redução de custos'
        ]
        
        self.palavras_chave_fit = [
            'perfeito', 'ideal', 'exatamente', 'resolveria', 'atenderia',
            'necessitamos', 'precisamos', 'faz sentido', 'alinhado'
        ]
        
        self.palavras_chave_timing = [
            'quando', 'prazo', 'timeline', 'cronograma', 'implementar',
            'começar', 'iniciar', 'já', 'imediatamente'
        ]

    def analisar_transcricao(self, nome_cliente: str, transcricao: str) -> Dict[str, Any]:
        """
        Analisa uma transcrição de reunião e gera insights estratégicos.
        
        Args:
            nome_cliente: Nome do cliente
            transcricao: Texto da transcrição
            
        Returns:
            Dicionário com análise completa
        """
        print(f"🔍 Analisando reunião com {nome_cliente}...")
        
        # 1. Diagnóstico do Cliente
        diagnostico = self._diagnosticar_cliente(transcricao)
        
        # 2. Termômetro da Oportunidade
        scores = self._calcular_scores_prioridade(transcricao)
        
        # 3. Estratégia de Follow-up
        followup = self._gerar_estrategia_followup(transcricao, diagnostico, scores)
        
        # 4. Feedback de Performance Pessoal
        feedback = self._analisar_performance_pessoal(transcricao)
        
        # 5. Próximos Passos
        proximos_passos = self._definir_proximos_passos(scores, diagnostico)
        
        # Compilar análise completa
        analise_completa = {
            "Cliente": nome_cliente,
            "Data_Analise": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Diagnostico": diagnostico,
            "Score_Prioridade": scores,
            "Resumo_FollowUp": followup,
            "Feedback_Pessoal": feedback,
            "Proximos_Passos": proximos_passos
        }
        
        # Salvar análise
        self._salvar_analise_cliente(nome_cliente, analise_completa)
        
        return analise_completa

    def _diagnosticar_cliente(self, transcricao: str) -> Dict[str, Any]:
        """Extrai perfil e características do cliente da transcrição."""
        transcricao_lower = transcricao.lower()
        
        # Detectar setor
        setores = {
            'tecnologia': ['software', 'tech', 'digital', 'app', 'sistema'],
            'saude': ['hospital', 'clinica', 'medico', 'saude', 'paciente'],
            'financeiro': ['banco', 'financeiro', 'credito', 'investimento'],
            'varejo': ['loja', 'varejo', 'comercio', 'vendas', 'cliente'],
            'industria': ['fabrica', 'producao', 'industria', 'manufatura'],
            'servicos': ['consultoria', 'servico', 'atendimento', 'suporte']
        }
        
        setor_detectado = 'não identificado'
        for setor, palavras in setores.items():
            if any(palavra in transcricao_lower for palavra in palavras):
                setor_detectado = setor
                break
        
        # Detectar porte da empresa
        porte = 'não identificado'
        if any(palavra in transcricao_lower for palavra in ['multinacional', 'grande', 'corporativo']):
            porte = 'grande'
        elif any(palavra in transcricao_lower for palavra in ['pequena', 'startup', 'iniciante']):
            porte = 'pequena'
        elif any(palavra in transcricao_lower for palavra in ['media', 'crescimento', 'expansao']):
            porte = 'media'
        
        # Extrair dores principais
        dores = self._extrair_dores(transcricao)
        
        # Identificar stakeholders
        stakeholders = self._identificar_stakeholders(transcricao)
        
        # Detectar gatilhos emocionais
        gatilhos = self._detectar_gatilhos_emocionais(transcricao)
        
        return {
            "Setor": setor_detectado,
            "Porte": porte,
            "Dores_Principais": dores,
            "Stakeholders": stakeholders,
            "Gatilhos_Emocionais": gatilhos,
            "Objetivos_Declarados": self._extrair_objetivos(transcricao)
        }

    def _extrair_dores(self, transcricao: str) -> List[str]:
        """Extrai as principais dores mencionadas na transcrição."""
        dores_padrao = [
            r'problema[s]?\s+(?:de|com|na|no)\s+([^.!?]+)',
            r'dificuldade[s]?\s+(?:de|com|na|no)\s+([^.!?]+)',
            r'desafio[s]?\s+(?:de|com|na|no)\s+([^.!?]+)',
            r'precisamos\s+(?:resolver|melhorar|otimizar)\s+([^.!?]+)',
            r'não\s+(?:conseguimos|estamos)\s+([^.!?]+)'
        ]
        
        dores = []
        for padrao in dores_padrao:
            matches = re.findall(padrao, transcricao, re.IGNORECASE)
            dores.extend([match.strip() for match in matches])
        
        return list(set(dores))[:5]  # Top 5 dores únicas

    def _identificar_stakeholders(self, transcricao: str) -> Dict[str, List[str]]:
        """Identifica diferentes tipos de stakeholders mencionados."""
        stakeholders = {
            "Decisores": [],
            "Influenciadores": [],
            "Usuarios": []
        }
        
        # Padrões para identificar decisores
        decisores_padrao = [
            r'(?:eu|nós)\s+(?:decido|decidimos|aprovamos)',
            r'(?:sou|são)\s+(?:responsável|responsáveis)',
            r'(?:tenho|temos)\s+(?:autonomia|poder)'
        ]
        
        for padrao in decisores_padrao:
            if re.search(padrao, transcricao, re.IGNORECASE):
                stakeholders["Decisores"].append("Contato atual")
        
        # Padrões para influenciadores
        influenciadores_padrao = [
            r'(?:equipe|time|pessoal)',
            r'(?:gerente|diretor|coordenador)',
            r'(?:preciso\s+conversar|vou\s+consultar)'
        ]
        
        for padrao in influenciadores_padrao:
            if re.search(padrao, transcricao, re.IGNORECASE):
                stakeholders["Influenciadores"].append("Equipe interna")
        
        return stakeholders

    def _detectar_gatilhos_emocionais(self, transcricao: str) -> List[str]:
        """Detecta gatilhos emocionais na conversa."""
        gatilhos = []
        
        if any(palavra in transcricao.lower() for palavra in ['frustrado', 'cansado', 'estressado']):
            gatilhos.append("Frustração com situação atual")
        
        if any(palavra in transcricao.lower() for palavra in ['preocupado', 'ansioso', 'nervoso']):
            gatilhos.append("Preocupação com resultados")
        
        if any(palavra in transcricao.lower() for palavra in ['empolgado', 'animado', 'interessado']):
            gatilhos.append("Entusiasmo com possibilidade")
        
        if any(palavra in transcricao.lower() for palavra in ['cético', 'desconfiado', 'duvidoso']):
            gatilhos.append("Ceticismo sobre solução")
        
        return gatilhos

    def _extrair_objetivos(self, transcricao: str) -> List[str]:
        """Extrai objetivos declarados pelo cliente."""
        objetivos_padrao = [
            r'(?:queremos|precisamos|objetivo)\s+([^.!?]+)',
            r'(?:meta|meta\s+é)\s+([^.!?]+)',
            r'(?:foco|focamos)\s+(?:em|na|no)\s+([^.!?]+)'
        ]
        
        objetivos = []
        for padrao in objetivos_padrao:
            matches = re.findall(padrao, transcricao, re.IGNORECASE)
            objetivos.extend([match.strip() for match in matches])
        
        return list(set(objetivos))[:3]

    def _calcular_scores_prioridade(self, transcricao: str) -> Dict[str, Any]:
        """Calcula scores de 0-10 para diferentes dimensões da oportunidade."""
        transcricao_lower = transcricao.lower()
        
        # Urgência (0-10)
        urgencia = self._calcular_score_urgencia(transcricao_lower)
        
        # Autoridade (0-10)
        autoridade = self._calcular_score_autoridade(transcricao_lower)
        
        # Orçamento (0-10)
        orcamento = self._calcular_score_orcamento(transcricao_lower)
        
        # Fit da solução (0-10)
        fit = self._calcular_score_fit(transcricao_lower)
        
        # Timing (0-10)
        timing = self._calcular_score_timing(transcricao_lower)
        
        # Score geral (média ponderada)
        score_geral = (urgencia * 0.3 + autoridade * 0.2 + orcamento * 0.2 + 
                      fit * 0.2 + timing * 0.1)
        
        return {
            "Urgencia": urgencia,
            "Autoridade": autoridade,
            "Orcamento": orcamento,
            "Fit_Solucao": fit,
            "Timing": timing,
            "Score_Geral": round(score_geral, 1),
            "Classificacao": self._classificar_prioridade(score_geral)
        }

    def _calcular_score_urgencia(self, transcricao: str) -> int:
        """Calcula score de urgência baseado em palavras-chave e contexto."""
        score = 5  # Base neutra
        
        # Palavras que aumentam urgência
        for palavra in self.palavras_chave_urgencia:
            if palavra in transcricao:
                score += 1
        
        # Contextos específicos de urgência
        if 'perdendo' in transcricao or 'competição' in transcricao:
            score += 2
        if 'prazo' in transcricao or 'deadline' in transcricao:
            score += 2
        
        return min(10, max(0, score))

    def _calcular_score_autoridade(self, transcricao: str) -> int:
        """Calcula score de autoridade do contato."""
        score = 5  # Base neutra
        
        for palavra in self.palavras_chave_autoridade:
            if palavra in transcricao:
                score += 1
        
        # Indicadores específicos de autoridade
        if 'decido' in transcricao or 'aprovamos' in transcricao:
            score += 2
        if 'autonomia' in transcricao or 'responsável' in transcricao:
            score += 1
        
        return min(10, max(0, score))

    def _calcular_score_orcamento(self, transcricao: str) -> int:
        """Calcula score de disponibilidade de orçamento."""
        score = 5  # Base neutra
        
        for palavra in self.palavras_chave_orcamento:
            if palavra in transcricao:
                score += 1
        
        # Indicadores específicos de orçamento
        if 'investimento' in transcricao or 'orçamento' in transcricao:
            score += 2
        if 'roi' in transcricao or 'retorno' in transcricao:
            score += 1
        
        return min(10, max(0, score))

    def _calcular_score_fit(self, transcricao: str) -> int:
        """Calcula score de fit da solução."""
        score = 5  # Base neutra
        
        for palavra in self.palavras_chave_fit:
            if palavra in transcricao:
                score += 1
        
        # Indicadores específicos de fit
        if 'perfeito' in transcricao or 'ideal' in transcricao:
            score += 2
        if 'exatamente' in transcricao or 'resolveria' in transcricao:
            score += 2
        
        return min(10, max(0, score))

    def _calcular_score_timing(self, transcricao: str) -> int:
        """Calcula score de timing para fechamento."""
        score = 5  # Base neutra
        
        for palavra in self.palavras_chave_timing:
            if palavra in transcricao:
                score += 1
        
        # Indicadores específicos de timing
        if 'imediatamente' in transcricao or 'já' in transcricao:
            score += 2
        if 'quando' in transcricao and 'implementar' in transcricao:
            score += 1
        
        return min(10, max(0, score))

    def _classificar_prioridade(self, score_geral: float) -> str:
        """Classifica a prioridade baseada no score geral."""
        if score_geral >= 8:
            return "ALTA PRIORIDADE"
        elif score_geral >= 6:
            return "MÉDIA PRIORIDADE"
        else:
            return "BAIXA PRIORIDADE"

    def _gerar_estrategia_followup(self, transcricao: str, diagnostico: Dict, scores: Dict) -> Dict[str, Any]:
        """Gera estratégia de follow-up baseada na análise."""
        
        # Resumo executivo (3 frases)
        resumo = self._gerar_resumo_executivo(diagnostico, scores)
        
        # Objeções e respostas
        objeções = self._identificar_objecoes(transcricao)
        respostas = self._gerar_respostas_objecoes(objeções)
        
        # Template de email
        email_template = self._gerar_template_email(diagnostico, scores, objeções)
        
        return {
            "Resumo_Executivo": resumo,
            "Objecoes_Identificadas": objeções,
            "Respostas_Strategicas": respostas,
            "Template_Email": email_template,
            "Proximos_Passos_Sugeridos": self._sugerir_proximos_passos(scores)
        }

    def _gerar_resumo_executivo(self, diagnostico: Dict, scores: Dict) -> str:
        """Gera resumo executivo em 3 frases."""
        setor = diagnostico.get('Setor', 'não identificado')
        score_geral = scores.get('Score_Geral', 0)
        classificacao = scores.get('Classificacao', 'BAIXA PRIORIDADE')
        
        frase1 = f"Cliente do setor {setor} com {classificacao.lower()} (score {score_geral}/10)."
        
        dores = diagnostico.get('Dores_Principais', [])
        frase2 = f"Principais dores: {', '.join(dores[:2]) if dores else 'não identificadas claramente'}."
        
        urgencia = scores.get('Urgencia', 0)
        if urgencia >= 7:
            frase3 = "Alta urgência detectada - priorizar follow-up imediato."
        elif urgencia >= 5:
            frase3 = "Urgência moderada - agendar follow-up em 48h."
        else:
            frase3 = "Baixa urgência - manter no pipeline de longo prazo."
        
        return f"{frase1} {frase2} {frase3}"

    def _identificar_objecoes(self, transcricao: str) -> List[str]:
        """Identifica objeções levantadas pelo cliente."""
        objeções_padrao = [
            r'(?:muito\s+)?(?:caro|caro\s+demais)',
            r'(?:não\s+)?(?:tenho|temos)\s+(?:tempo|recursos)',
            r'(?:preciso|precisamos)\s+(?:pensar|avaliar|consultar)',
            r'(?:não\s+)?(?:estou|estamos)\s+(?:convencido|seguros)',
            r'(?:já\s+)?(?:temos|usamos)\s+(?:outra|outro)'
        ]
        
        objeções = []
        for padrao in objeções_padrao:
            if re.search(padrao, transcricao, re.IGNORECASE):
                objeções.append(f"Objeção detectada: {padrao}")
        
        return objeções if objeções else ["Nenhuma objeção explícita identificada"]

    def _gerar_respostas_objecoes(self, objeções: List[str]) -> List[str]:
        """Gera respostas estratégicas para objeções."""
        respostas = []
        
        for objeção in objeções:
            if 'caro' in objeção.lower():
                respostas.append("Focar no ROI e economia de longo prazo. Apresentar casos de sucesso com retorno comprovado.")
            elif 'tempo' in objeção.lower() or 'recursos' in objeção.lower():
                respostas.append("Destacar facilidade de implementação e suporte completo. Oferecer piloto de baixo risco.")
            elif 'pensar' in objeção.lower() or 'avaliar' in objeção.lower():
                respostas.append("Fornecer material adicional e agendar call de esclarecimentos. Criar senso de urgência.")
            elif 'convencido' in objeção.lower() or 'seguros' in objeção.lower():
                respostas.append("Apresentar provas sociais e garantias. Oferecer período de teste.")
            elif 'outra' in objeção.lower() or 'outro' in objeção.lower():
                respostas.append("Focar em diferenciais únicos e benefícios específicos. Comparação lado a lado.")
        
        return respostas

    def _gerar_template_email(self, diagnostico: Dict, scores: Dict, objeções: List[str]) -> str:
        """Gera template de email de follow-up."""
        nome_cliente = "Cliente"  # Será substituído na implementação
        
        assunto = f"Próximos passos - {nome_cliente}"
        
        corpo = f"""
Olá {nome_cliente},

Obrigado pela reunião de hoje. Foi muito produtivo entender melhor suas necessidades.

Baseado na nossa conversa, identifiquei algumas oportunidades interessantes:
{chr(10).join([f"• {dor}" for dor in diagnostico.get('Dores_Principais', [])[:3]])}

Próximos passos sugeridos:
• [Ação específica baseada no score de prioridade]
• [Segunda ação]
• [Terceira ação]

Gostaria de agendar uma call de 15 minutos para discutirmos os detalhes?

Atenciosamente,
[Seu nome]
"""
        
        return f"Assunto: {assunto}\n\n{corpo}"

    def _sugerir_proximos_passos(self, scores: Dict) -> List[str]:
        """Sugere próximos passos baseados nos scores."""
        score_geral = scores.get('Score_Geral', 0)
        urgencia = scores.get('Urgencia', 0)
        
        passos = []
        
        if score_geral >= 8:
            passos.extend([
                "Agendar call de fechamento em 24-48h",
                "Preparar proposta comercial detalhada",
                "Envolver stakeholders-chave identificados"
            ])
        elif score_geral >= 6:
            passos.extend([
                "Enviar material de apoio e cases de sucesso",
                "Agendar call de esclarecimentos em 1 semana",
                "Preparar piloto ou demonstração específica"
            ])
        else:
            passos.extend([
                "Manter no pipeline de longo prazo",
                "Enviar newsletter mensal com insights",
                "Reagendar follow-up em 30 dias"
            ])
        
        if urgencia >= 7:
            passos.insert(0, "PRIORIDADE: Contato imediato via telefone")
        
        return passos

    def _analisar_performance_pessoal(self, transcricao: str) -> Dict[str, Any]:
        """Analisa a performance pessoal na reunião."""
        # Dividir transcrição em falas (simplificado)
        falas = transcricao.split('\n')
        
        # Contar perguntas
        perguntas = len([fala for fala in falas if '?' in fala])
        
        # Identificar tipos de perguntas
        perguntas_abertas = len([fala for fala in falas if any(palavra in fala.lower() 
                              for palavra in ['como', 'por que', 'o que', 'quando', 'onde'])])
        
        perguntas_fechadas = perguntas - perguntas_abertas
        
        # Palavras que indicam insegurança
        palavras_inseguranca = ['acho', 'talvez', 'pode ser', 'não sei', 'acho que']
        inseguranca = sum([fala.lower().count(palavra) for fala in falas 
                          for palavra in palavras_inseguranca])
        
        # Palavras que indicam confiança
        palavras_confianca = ['tenho certeza', 'sabemos', 'garantimos', 'comprovado']
        confianca = sum([fala.lower().count(palavra) for fala in falas 
                        for palavra in palavras_confianca])
        
        return {
            "Total_Perguntas": perguntas,
            "Perguntas_Abertas": perguntas_abertas,
            "Perguntas_Fechadas": perguntas_fechadas,
            "Razao_Abertas_Fechadas": round(perguntas_abertas / max(perguntas_fechadas, 1), 2),
            "Indicadores_Inseguranca": inseguranca,
            "Indicadores_Confianca": confianca,
            "Score_Confianca": max(0, min(10, 5 + confianca - inseguranca)),
            "Melhorias_Sugeridas": self._sugerir_melhorias(perguntas_abertas, perguntas_fechadas, inseguranca, confianca)
        }

    def _sugerir_melhorias(self, perguntas_abertas: int, perguntas_fechadas: int, 
                          inseguranca: int, confianca: int) -> List[str]:
        """Sugere melhorias para performance pessoal."""
        melhorias = []
        
        if perguntas_abertas < perguntas_fechadas:
            melhorias.append("Aumentar proporção de perguntas abertas (como, por que, o que)")
        
        if inseguranca > confianca:
            melhorias.append("Reduzir uso de palavras que transmitem insegurança (acho, talvez)")
            melhorias.append("Usar mais linguagem assertiva e baseada em fatos")
        
        if perguntas_abertas + perguntas_fechadas < 5:
            melhorias.append("Fazer mais perguntas para entender melhor as necessidades")
        
        melhorias.extend([
            "Preparar perguntas específicas sobre dores e objetivos",
            "Usar mais cases de sucesso para construir credibilidade",
            "Focar em benefícios específicos para o cliente"
        ])
        
        return melhorias

    def _definir_proximos_passos(self, scores: Dict, diagnostico: Dict) -> Dict[str, Any]:
        """Define próximos passos estratégicos."""
        score_geral = scores.get('Score_Geral', 0)
        
        if score_geral >= 8:
            return {
                "Prioridade": "ALTA",
                "Acoes_Imediatas": [
                    "Contato telefônico em 24h",
                    "Preparar proposta comercial",
                    "Agendar reunião de fechamento"
                ],
                "Prazo_Proxima_Acao": "24-48 horas",
                "Objetivo_Proxima_Call": "Fechamento da venda"
            }
        elif score_geral >= 6:
            return {
                "Prioridade": "MÉDIA",
                "Acoes_Imediatas": [
                    "Enviar material de apoio",
                    "Agendar call de esclarecimentos",
                    "Preparar demonstração específica"
                ],
                "Prazo_Proxima_Acao": "1 semana",
                "Objetivo_Proxima_Call": "Avançar no processo de vendas"
            }
        else:
            return {
                "Prioridade": "BAIXA",
                "Acoes_Imediatas": [
                    "Manter no pipeline",
                    "Enviar newsletter",
                    "Reagendar follow-up"
                ],
                "Prazo_Proxima_Acao": "30 dias",
                "Objetivo_Proxima_Call": "Manter relacionamento"
            }

    def _salvar_analise_cliente(self, nome_cliente: str, analise: Dict[str, Any]):
        """Salva análise do cliente em arquivos organizados."""
        cliente_path = self.analises_path / nome_cliente.lower().replace(' ', '_')
        cliente_path.mkdir(exist_ok=True)
        
        # Salvar análise completa em JSON
        with open(cliente_path / "analise_completa.json", 'w', encoding='utf-8') as f:
            json.dump(analise, f, ensure_ascii=False, indent=2)
        
        # Salvar arquivos individuais
        self._salvar_diagnostico_cliente(cliente_path, analise['Diagnostico'])
        self._salvar_score_prioridade(cliente_path, analise['Score_Prioridade'])
        self._salvar_resumo_followup(cliente_path, analise['Resumo_FollowUp'])
        self._salvar_feedback_pessoal(cliente_path, analise['Feedback_Pessoal'])
        self._salvar_proximos_passos(cliente_path, analise['Proximos_Passos'])
        
        print(f"✅ Análise salva em: {cliente_path}")

    def _salvar_diagnostico_cliente(self, cliente_path: Path, diagnostico: Dict):
        """Salva diagnóstico do cliente."""
        with open(cliente_path / "Diagnostico_Cliente.txt", 'w', encoding='utf-8') as f:
            f.write("=== DIAGNÓSTICO DO CLIENTE ===\n\n")
            f.write(f"Setor: {diagnostico.get('Setor', 'N/A')}\n")
            f.write(f"Porte: {diagnostico.get('Porte', 'N/A')}\n\n")
            
            f.write("DORES PRINCIPAIS:\n")
            for dor in diagnostico.get('Dores_Principais', []):
                f.write(f"• {dor}\n")
            
            f.write("\nSTAKEHOLDERS:\n")
            for tipo, pessoas in diagnostico.get('Stakeholders', {}).items():
                f.write(f"{tipo}: {', '.join(pessoas)}\n")
            
            f.write("\nGATILHOS EMOCIONAIS:\n")
            for gatilho in diagnostico.get('Gatilhos_Emocionais', []):
                f.write(f"• {gatilho}\n")
            
            f.write("\nOBJETIVOS DECLARADOS:\n")
            for objetivo in diagnostico.get('Objetivos_Declarados', []):
                f.write(f"• {objetivo}\n")

    def _salvar_score_prioridade(self, cliente_path: Path, scores: Dict):
        """Salva scores de prioridade."""
        with open(cliente_path / "Score_Prioridade.txt", 'w', encoding='utf-8') as f:
            f.write("=== SCORE DE PRIORIDADE ===\n\n")
            f.write(f"Urgência: {scores.get('Urgencia', 0)}/10\n")
            f.write(f"Autoridade: {scores.get('Autoridade', 0)}/10\n")
            f.write(f"Orçamento: {scores.get('Orcamento', 0)}/10\n")
            f.write(f"Fit da Solução: {scores.get('Fit_Solucao', 0)}/10\n")
            f.write(f"Timing: {scores.get('Timing', 0)}/10\n")
            f.write(f"\nSCORE GERAL: {scores.get('Score_Geral', 0)}/10\n")
            f.write(f"CLASSIFICAÇÃO: {scores.get('Classificacao', 'N/A')}\n")

    def _salvar_resumo_followup(self, cliente_path: Path, followup: Dict):
        """Salva resumo de follow-up."""
        with open(cliente_path / "Resumo_FollowUp.txt", 'w', encoding='utf-8') as f:
            f.write("=== ESTRATÉGIA DE FOLLOW-UP ===\n\n")
            f.write("RESUMO EXECUTIVO:\n")
            f.write(f"{followup.get('Resumo_Executivo', 'N/A')}\n\n")
            
            f.write("OBJEÇÕES IDENTIFICADAS:\n")
            for objecao in followup.get('Objecoes_Identificadas', []):
                f.write(f"• {objecao}\n")
            
            f.write("\nRESPOSTAS ESTRATÉGICAS:\n")
            for resposta in followup.get('Respostas_Strategicas', []):
                f.write(f"• {resposta}\n")
            
            f.write("\nTEMPLATE DE EMAIL:\n")
            f.write(followup.get('Template_Email', 'N/A'))

    def _salvar_feedback_pessoal(self, cliente_path: Path, feedback: Dict):
        """Salva feedback de performance pessoal."""
        with open(cliente_path / "Feedback_Pessoal.txt", 'w', encoding='utf-8') as f:
            f.write("=== FEEDBACK DE PERFORMANCE PESSOAL ===\n\n")
            f.write(f"Total de Perguntas: {feedback.get('Total_Perguntas', 0)}\n")
            f.write(f"Perguntas Abertas: {feedback.get('Perguntas_Abertas', 0)}\n")
            f.write(f"Perguntas Fechadas: {feedback.get('Perguntas_Fechadas', 0)}\n")
            f.write(f"Razão Abertas/Fechadas: {feedback.get('Razao_Abertas_Fechadas', 0)}\n")
            f.write(f"Score de Confiança: {feedback.get('Score_Confianca', 0)}/10\n\n")
            
            f.write("MELHORIAS SUGERIDAS:\n")
            for melhoria in feedback.get('Melhorias_Sugeridas', []):
                f.write(f"• {melhoria}\n")

    def _salvar_proximos_passos(self, cliente_path: Path, proximos: Dict):
        """Salva próximos passos."""
        with open(cliente_path / "Proximos_Passos.txt", 'w', encoding='utf-8') as f:
            f.write("=== PRÓXIMOS PASSOS ===\n\n")
            f.write(f"Prioridade: {proximos.get('Prioridade', 'N/A')}\n")
            f.write(f"Prazo Próxima Ação: {proximos.get('Prazo_Proxima_Acao', 'N/A')}\n")
            f.write(f"Objetivo Próxima Call: {proximos.get('Objetivo_Proxima_Call', 'N/A')}\n\n")
            
            f.write("AÇÕES IMEDIATAS:\n")
            for acao in proximos.get('Acoes_Imediatas', []):
                f.write(f"• {acao}\n")

    def processar_todas_reunioes(self) -> Dict[str, Any]:
        """Processa todas as transcrições disponíveis."""
        print("🚀 Iniciando processamento de todas as reuniões...")
        
        resultados = {}
        arquivos_txt = list(self.reunioes_path.glob("*.txt"))
        
        if not arquivos_txt:
            print("❌ Nenhum arquivo de transcrição encontrado!")
            return {}
        
        for arquivo in arquivos_txt:
            nome_cliente = arquivo.stem
            print(f"\n📄 Processando: {nome_cliente}")
            
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    transcricao = f.read()
                
                analise = self.analisar_transcricao(nome_cliente, transcricao)
                resultados[nome_cliente] = analise
                
            except Exception as e:
                print(f"❌ Erro ao processar {nome_cliente}: {e}")
        
        # Gerar overview geral
        self._gerar_overview_geral(resultados)
        
        print(f"\n✅ Processamento concluído! {len(resultados)} reuniões analisadas.")
        return resultados

    def _gerar_overview_geral(self, resultados: Dict[str, Any]):
        """Gera overview geral de todas as análises."""
        overview_data = []
        
        for cliente, analise in resultados.items():
            scores = analise.get('Score_Prioridade', {})
            overview_data.append({
                'Cliente': cliente,
                'Score_Geral': scores.get('Score_Geral', 0),
                'Urgencia': scores.get('Urgencia', 0),
                'Autoridade': scores.get('Autoridade', 0),
                'Orcamento': scores.get('Orcamento', 0),
                'Fit_Solucao': scores.get('Fit_Solucao', 0),
                'Timing': scores.get('Timing', 0),
                'Classificacao': scores.get('Classificacao', 'N/A'),
                'Prioridade': analise.get('Proximos_Passos', {}).get('Prioridade', 'N/A')
            })
        
        # Salvar como CSV
        df = pd.DataFrame(overview_data)
        df.to_csv(self.analises_path / "overview_geral.csv", index=False, encoding='utf-8')
        
        # Salvar como JSON
        with open(self.analises_path / "overview_geral.json", 'w', encoding='utf-8') as f:
            json.dump(overview_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Overview geral salvo em: {self.analises_path}")

    def gerar_relatorio_executivo(self, resultados: Dict[str, Any]) -> str:
        """Gera relatório executivo consolidado."""
        if not resultados:
            return "Nenhum resultado disponível para relatório."
        
        # Calcular estatísticas gerais
        scores_gerais = [analise['Score_Prioridade']['Score_Geral'] 
                        for analise in resultados.values()]
        
        total_clientes = len(resultados)
        score_medio = sum(scores_gerais) / len(scores_gerais)
        clientes_alta_prioridade = len([s for s in scores_gerais if s >= 8])
        
        relatorio = f"""
=== RELATÓRIO EXECUTIVO - ANÁLISE COMERCIAL ===
Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}

RESUMO GERAL:
• Total de clientes analisados: {total_clientes}
• Score médio de prioridade: {score_medio:.1f}/10
• Clientes de alta prioridade: {clientes_alta_prioridade}
• Taxa de alta prioridade: {(clientes_alta_prioridade/total_clientes)*100:.1f}%

TOP 3 CLIENTES POR PRIORIDADE:
"""
        
        # Ordenar por score geral
        clientes_ordenados = sorted(resultados.items(), 
                                  key=lambda x: x[1]['Score_Prioridade']['Score_Geral'], 
                                  reverse=True)
        
        for i, (cliente, analise) in enumerate(clientes_ordenados[:3], 1):
            score = analise['Score_Prioridade']['Score_Geral']
            classificacao = analise['Score_Prioridade']['Classificacao']
            relatorio += f"{i}. {cliente}: {score}/10 ({classificacao})\n"
        
        relatorio += f"\nPRÓXIMAS AÇÕES RECOMENDADAS:\n"
        relatorio += f"• Focar nos {clientes_alta_prioridade} clientes de alta prioridade\n"
        relatorio += f"• Revisar estratégia para clientes de baixa prioridade\n"
        relatorio += f"• Implementar melhorias de performance identificadas\n"
        
        return relatorio

def main():
    """Função principal para executar o analisador."""
    print("🎯 ANALISADOR COMERCIAL MESTRE - Cursor AI")
    print("=" * 50)
    
    # Inicializar analisador
    analisador = AnalisadorComercialMestre()
    
    # Processar todas as reuniões
    resultados = analisador.processar_todas_reunioes()
    
    if resultados:
        # Gerar relatório executivo
        relatorio = analisador.gerar_relatorio_executivo(resultados)
        print("\n" + relatorio)
        
        # Salvar relatório
        with open(analisador.analises_path / "relatorio_executivo.txt", 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print(f"\n📋 Relatório executivo salvo em: {analisador.analises_path}")
    
    print("\n🎉 Análise comercial concluída com sucesso!")

if __name__ == "__main__":
    main()
