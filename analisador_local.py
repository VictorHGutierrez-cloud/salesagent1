"""
Analisador Estratégico de Reuniões de Vendas - VERSÃO LOCAL
Sistema que funciona SEM chave da OpenAI - análise baseada em padrões e regras
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class AnalisadorReunioesLocal:
    def __init__(self):
        """Inicializa o analisador local sem dependência da OpenAI"""
        self.base_dir = Path("Reunioes em TXT")
        self.output_dir = Path("Analises")
        self.output_dir.mkdir(exist_ok=True)
        
        # Palavras-chave para análise
        self.palavras_urgencia = [
            'urgente', 'urgência', 'urgent', 'imediato', 'rápido', 'asap', 'emergência',
            'crítico', 'prioridade', 'deadline', 'prazo', 'tempo', 'pressa', 'corre',
            'agora', 'já', 'ontem', 'preciso', 'necessário', 'obrigatório'
        ]
        
        self.palavras_necessidade = [
            'preciso', 'necessário', 'problema', 'dificuldade', 'dor', 'desafio',
            'melhorar', 'otimizar', 'solução', 'resolver', 'implementar', 'adotar',
            'mudança', 'transformação', 'inovação', 'competitividade', 'eficiência'
        ]
        
        self.palavras_fit = [
            'perfeito', 'ideal', 'adequado', 'compatível', 'alinhado', 'correto',
            'certo', 'bom', 'excelente', 'ótimo', 'funciona', 'serve', 'atende',
            'satisfaz', 'resolve', 'cobre', 'suporta', 'integra', 'conecta'
        ]
        
        self.palavras_orcamento = [
            'orçamento', 'budget', 'investimento', 'custo', 'preço', 'valor',
            'dinheiro', 'recurso', 'financeiro', 'econômico', 'pagamento',
            'contrato', 'proposta', 'proposta comercial', 'comercial'
        ]
        
        self.palavras_decisao = [
            'decidir', 'decisão', 'aprovar', 'aprovação', 'autorizar', 'autorização',
            'chefe', 'diretor', 'gerente', 'presidente', 'ceo', 'cto', 'cfo',
            'responsável', 'quem decide', 'autoridade', 'hierarquia'
        ]
        
        self.palavras_objeção = [
            'mas', 'porém', 'contudo', 'entretanto', 'não', 'nunca', 'jamais',
            'difícil', 'complicado', 'caro', 'caro demais', 'muito caro',
            'não temos', 'não posso', 'não consigo', 'impossível', 'não vai dar',
            'problema', 'risco', 'preocupação', 'dúvida', 'incerteza'
        ]
        
        self.palavras_timeline = [
            'quando', 'prazo', 'data', 'mês', 'semana', 'dia', 'ano',
            'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
            'Q1', 'Q2', 'Q3', 'Q4', 'trimestre', 'semestre'
        ]
    
    def _contar_palavras_chave(self, texto, palavras):
        """Conta ocorrências de palavras-chave no texto"""
        texto_lower = texto.lower()
        contador = 0
        palavras_encontradas = []
        
        for palavra in palavras:
            if palavra.lower() in texto_lower:
                contador += texto_lower.count(palavra.lower())
                palavras_encontradas.append(palavra)
        
        return contador, palavras_encontradas
    
    def _extrair_stakeholders(self, texto):
        """Extrai stakeholders mencionados no texto"""
        stakeholders = []
        
        # Padrões para identificar pessoas e cargos
        padroes_cargos = [
            r'(?:Sr\.|Sra\.|Dr\.|Dra\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:diretor|gerente|presidente|ceo|cto|cfo|coo)',
            r'(?:diretor|gerente|presidente|ceo|cto|cfo|coo)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:da|do|de)\s+([A-Z][a-z]+)',
        ]
        
        for padrao in padroes_cargos:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    nome = ' '.join(match)
                else:
                    nome = match
                
                if len(nome.split()) >= 2:  # Pelo menos nome e sobrenome
                    stakeholders.append({
                        "nome": nome,
                        "cargo": "Não identificado",
                        "influencia": "Média",
                        "posicao": "Neutro"
                    })
        
        return stakeholders[:5]  # Máximo 5 stakeholders
    
    def _calcular_scores(self, texto):
        """Calcula scores baseados em análise de padrões"""
        # Conta palavras-chave
        urgencia_count, urgencia_palavras = self._contar_palavras_chave(texto, self.palavras_urgencia)
        necessidade_count, necessidade_palavras = self._contar_palavras_chave(texto, self.palavras_necessidade)
        fit_count, fit_palavras = self._contar_palavras_chave(texto, self.palavras_fit)
        orcamento_count, orcamento_palavras = self._contar_palavras_chave(texto, self.palavras_orcamento)
        decisao_count, decisao_palavras = self._contar_palavras_chave(texto, self.palavras_decisao)
        objeção_count, objeção_palavras = self._contar_palavras_chave(texto, self.palavras_objeção)
        
        # Calcula scores (0-1)
        total_palavras = len(texto.split())
        
        urgencia_score = min(urgencia_count / max(total_palavras / 100, 1), 1.0)
        necessidade_score = min(necessidade_count / max(total_palavras / 100, 1), 1.0)
        fit_score = min(fit_count / max(total_palavras / 100, 1), 1.0)
        
        # Score de confiança baseado na presença de elementos BANT
        confianca_score = 0
        if orcamento_count > 0:
            confianca_score += 0.3
        if decisao_count > 0:
            confianca_score += 0.3
        if necessidade_count > 0:
            confianca_score += 0.2
        if objeção_count == 0:  # Menos objeções = mais confiança
            confianca_score += 0.2
        
        confianca_score = min(confianca_score, 1.0)
        
        return {
            "urgencia": round(urgencia_score, 2),
            "necessidade": round(necessidade_score, 2),
            "fit": round(fit_score, 2),
            "confianca": round(confianca_score, 2)
        }, {
            "urgencia_palavras": urgencia_palavras,
            "necessidade_palavras": necessidade_palavras,
            "fit_palavras": fit_palavras,
            "orcamento_palavras": orcamento_palavras,
            "decisao_palavras": decisao_palavras,
            "objeção_palavras": objeção_palavras
        }
    
    def _determinar_temperatura(self, scores):
        """Determina a temperatura do lead baseada nos scores"""
        urgencia = scores.get("urgencia", 0)
        necessidade = scores.get("necessidade", 0)
        fit = scores.get("fit", 0)
        confianca = scores.get("confianca", 0)
        
        score_medio = (urgencia + necessidade + fit + confianca) / 4
        
        if score_medio >= 0.7:
            return "Hot"
        elif score_medio >= 0.4:
            return "Warm"
        else:
            return "Cold"
    
    def _extrair_objeções(self, texto):
        """Extrai objeções mencionadas no texto"""
        objeções = []
        
        # Padrões de objeção
        padroes_objeção = [
            r'(?:mas|porém|contudo|entretanto)\s+([^.!?]+)',
            r'(?:não|nunca|jamais)\s+(?:posso|consigo|tenho|vou|posso)\s+([^.!?]+)',
            r'(?:muito\s+)?(?:caro|difícil|complicado)\s+([^.!?]+)',
            r'(?:problema|risco|preocupação|dúvida)\s+([^.!?]+)',
        ]
        
        for padrao in padroes_objeção:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:  # Pelo menos 10 caracteres
                    objeções.append(match.strip())
        
        return objeções[:5]  # Máximo 5 objeções
    
    def _extrair_proximos_passos(self, texto):
        """Extrai próximos passos mencionados no texto"""
        proximos_passos = []
        
        # Padrões de próximos passos
        padroes_proximos = [
            r'(?:próximo|próxima)\s+(?:passo|etapa|fase|reunião)\s*:?\s*([^.!?]+)',
            r'(?:vamos|vou|iremos)\s+([^.!?]+)',
            r'(?:agendar|marcar|programar)\s+([^.!?]+)',
            r'(?:enviar|mandar)\s+([^.!?]+)',
            r'(?:analisar|estudar|avaliar)\s+([^.!?]+)',
        ]
        
        for padrao in padroes_proximos:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 5:  # Pelo menos 5 caracteres
                    proximos_passos.append({
                        "ação": match.strip(),
                        "prazo": "A definir",
                        "responsável": "A definir",
                        "prioridade": "Média"
                    })
        
        return proximos_passos[:3]  # Máximo 3 próximos passos
    
    def _gerar_frameworks(self, texto, scores, palavras_encontradas):
        """Gera frameworks BANT, MEDDIC e SPIN baseados na análise"""
        
        # BANT
        bant = {
            "budget": "Identificado" if palavras_encontradas["orcamento_palavras"] else "Não identificado",
            "authority": "Identificado" if palavras_encontradas["decisao_palavras"] else "Não identificado",
            "need": "Identificado" if palavras_encontradas["necessidade_palavras"] else "Não identificado",
            "timeline": "Identificado" if re.search(r'\b(?:quando|prazo|data|mês|semana)\b', texto, re.IGNORECASE) else "Não identificado"
        }
        
        # MEDDIC
        meddic = {
            "metrics": "A definir - precisa perguntar sobre KPIs e métricas de sucesso",
            "economic_buyer": "Identificado" if palavras_encontradas["decisao_palavras"] else "Não identificado",
            "decision_criteria": "A definir - precisa perguntar sobre critérios de decisão",
            "decision_process": "A definir - precisa perguntar sobre processo de decisão",
            "identify_pain": "Identificado" if palavras_encontradas["necessidade_palavras"] else "Não identificado",
            "champion": "A definir - precisa identificar campeão interno"
        }
        
        # SPIN
        spin = {
            "situation": "Situação atual identificada através da conversa",
            "problem": "Problemas identificados" if palavras_encontradas["necessidade_palavras"] else "Problemas não claros",
            "implication": "A definir - precisa explorar implicações dos problemas",
            "need_payoff": "A definir - precisa explorar benefícios da solução"
        }
        
        return {
            "BANT": bant,
            "MEDDIC": meddic,
            "SPIN": spin
        }
    
    def _gerar_recomendacoes(self, scores, temperatura, objeções):
        """Gera recomendações estratégicas baseadas na análise"""
        recomendacoes = []
        
        if temperatura == "Hot":
            recomendacoes.append("Lead quente - priorizar follow-up imediato")
            recomendacoes.append("Preparar proposta comercial detalhada")
        elif temperatura == "Warm":
            recomendacoes.append("Lead morno - manter engajamento regular")
            recomendacoes.append("Agendar próxima reunião para aprofundar necessidades")
        else:
            recomendacoes.append("Lead frio - focar em educação e relacionamento")
            recomendacoes.append("Enviar conteúdo de valor para aquecer o lead")
        
        if scores.get("urgencia", 0) < 0.3:
            recomendacoes.append("Criar senso de urgência - explorar consequências da inação")
        
        if scores.get("necessidade", 0) < 0.3:
            recomendacoes.append("Descobrir dores reais - fazer perguntas de descoberta")
        
        if scores.get("fit", 0) < 0.3:
            recomendacoes.append("Demonstrar fit - apresentar cases de sucesso similares")
        
        if objeções:
            recomendacoes.append(f"Abordar objeções identificadas: {', '.join(objeções[:2])}")
        
        return recomendacoes
    
    def _gerar_email_followup(self, nome_cliente, temperatura, highlights):
        """Gera template de email de follow-up"""
        if temperatura == "Hot":
            assunto = f"Próximos passos - {nome_cliente}"
            corpo = f"""Olá,

Obrigado pela reunião de hoje. Foi muito produtivo discutir {', '.join(highlights[:2])}.

Como combinado, vou preparar uma proposta detalhada e enviar até [DATA].

Posso contar com você para uma resposta até [PRAZO]?

Atenciosamente,
[SEU NOME]"""
        elif temperatura == "Warm":
            assunto = f"Material complementar - {nome_cliente}"
            corpo = f"""Olá,

Como prometido, segue material complementar sobre {', '.join(highlights[:1])}.

Gostaria de agendar uma breve conversa para discutir como isso pode ajudar sua empresa?

Disponível nos próximos dias.

Atenciosamente,
[SEU NOME]"""
        else:
            assunto = f"Conteúdo de valor - {nome_cliente}"
            corpo = f"""Olá,

Espero que esteja bem. Compartilho este artigo sobre {', '.join(highlights[:1])} que pode ser útil.

Se tiver interesse em conversar sobre como podemos ajudar, estou à disposição.

Atenciosamente,
[SEU NOME]"""
        
        return f"Assunto: {assunto}\n\n{corpo}"
    
    def _gerar_call_script(self, temperatura, objeções):
        """Gera roteiro para próxima ligação"""
        if temperatura == "Hot":
            return """ROTEIRO - LEAD QUENTE
1. Confirmar interesse e urgência
2. Apresentar proposta comercial
3. Abordar objeções: """ + (', '.join(objeções[:2]) if objeções else "Nenhuma identificada") + """
4. Fechar para próxima reunião de decisão
5. Definir próximos passos e prazos"""
        elif temperatura == "Warm":
            return """ROTEIRO - LEAD MORNO
1. Retomar conversa anterior
2. Explorar necessidades mais profundas
3. Apresentar cases de sucesso
4. Identificar stakeholders adicionais
5. Agendar próxima reunião"""
        else:
            return """ROTEIRO - LEAD FRIO
1. Educar sobre o problema
2. Compartilhar insights de mercado
3. Fazer perguntas de descoberta
4. Identificar dores latentes
5. Propor conteúdo de valor"""
    
    def analisar_transcricao(self, arquivo_transcricao):
        """Analisa uma transcrição específica"""
        print(f"Analisando: {arquivo_transcricao.name}")
        
        # Lê o arquivo
        texto = arquivo_transcricao.read_text(encoding="utf-8")
        
        # Calcula scores
        scores, palavras_encontradas = self._calcular_scores(texto)
        
        # Determina temperatura
        temperatura = self._determinar_temperatura(scores)
        
        # Extrai informações
        stakeholders = self._extrair_stakeholders(texto)
        objeções = self._extrair_objeções(texto)
        proximos_passos = self._extrair_proximos_passos(texto)
        
        # Gera frameworks
        frameworks = self._gerar_frameworks(texto, scores, palavras_encontradas)
        
        # Gera highlights
        highlights = []
        if palavras_encontradas["urgencia_palavras"]:
            highlights.append(f"Urgência: {', '.join(palavras_encontradas['urgencia_palavras'][:3])}")
        if palavras_encontradas["necessidade_palavras"]:
            highlights.append(f"Necessidades: {', '.join(palavras_encontradas['necessidade_palavras'][:3])}")
        if palavras_encontradas["fit_palavras"]:
            highlights.append(f"Fit: {', '.join(palavras_encontradas['fit_palavras'][:3])}")
        
        # Gera recomendações
        recomendacoes = self._gerar_recomendacoes(scores, temperatura, objeções)
        
        # Gera follow-ups
        nome_cliente = arquivo_transcricao.stem
        email_followup = self._gerar_email_followup(nome_cliente, temperatura, highlights)
        call_script = self._gerar_call_script(temperatura, objeções)
        
        # Monta resultado final
        resultado = {
            "resumo_executivo": f"Lead {temperatura.lower()} com scores: Urgência {scores['urgencia']}, Necessidade {scores['necessidade']}, Fit {scores['fit']}. {len(stakeholders)} stakeholders identificados.",
            "highlights": highlights,
            "scores": scores,
            "temperature": temperatura,
            "frameworks": frameworks,
            "stakeholders": stakeholders,
            "objeções": objeções,
            "próximos_passos": proximos_passos,
            "recomendações_estratégicas": recomendacoes,
            "email_followup": email_followup,
            "call_script": call_script,
            "data_analise": datetime.now().strftime("%Y-%m-%d")
        }
        
        return resultado
    
    def salvar_analise(self, nome_cliente, analise):
        """Salva a análise em arquivos organizados"""
        cliente_dir = self.output_dir / nome_cliente
        cliente_dir.mkdir(exist_ok=True)
        
        # Salva análise completa em JSON
        (cliente_dir / "analise_completa.json").write_text(
            json.dumps(analise, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )
        
        # Salva resumo executivo
        (cliente_dir / "resumo_executivo.txt").write_text(
            analise.get("resumo_executivo", ""), 
            encoding="utf-8"
        )
        
        # Salva frameworks
        (cliente_dir / "frameworks.json").write_text(
            json.dumps(analise.get("frameworks", {}), indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )
        
        # Salva follow-up
        (cliente_dir / "email_followup.txt").write_text(
            analise.get("email_followup", ""), 
            encoding="utf-8"
        )
        
        (cliente_dir / "call_script.txt").write_text(
            analise.get("call_script", ""), 
            encoding="utf-8"
        )
        
        # Salva próximos passos
        proximos_passos = analise.get("próximos_passos", [])
        proximos_texto = "\n".join([
            f"• {p['ação']} (Prazo: {p['prazo']}, Responsável: {p['responsável']}, Prioridade: {p['prioridade']})"
            for p in proximos_passos
        ])
        (cliente_dir / "proximos_passos.txt").write_text(proximos_texto, encoding="utf-8")
        
        print(f"  ✓ Análise salva em: {cliente_dir}")
    
    def processar_todas_reunioes(self):
        """Processa todas as transcrições na pasta"""
        if not self.base_dir.exists():
            print(f"Pasta {self.base_dir} não encontrada!")
            return
        
        arquivos_txt = list(self.base_dir.glob("*.txt"))
        if not arquivos_txt:
            print(f"Nenhum arquivo .txt encontrado em {self.base_dir}")
            return
        
        print(f"Encontrados {len(arquivos_txt)} arquivos para processar")
        
        todas_analises = []
        
        for arquivo in arquivos_txt:
            nome_cliente = arquivo.stem  # Nome sem extensão
            
            try:
                analise = self.analisar_transcricao(arquivo)
                if analise:
                    analise["cliente"] = nome_cliente
                    analise["data_analise"] = datetime.now().strftime("%Y-%m-%d")
                    
                    self.salvar_analise(nome_cliente, analise)
                    todas_analises.append(analise)
                else:
                    print(f"  ✗ Falha ao analisar {nome_cliente}")
                    
            except Exception as e:
                print(f"  ✗ Erro ao processar {nome_cliente}: {str(e)}")
        
        # Salva overview geral
        self._salvar_overview(todas_analises)
        self._gerar_graficos(todas_analises)
        
        print(f"\n✓ Processamento concluído! {len(todas_analises)} análises geradas.")
        
        return todas_analises
    
    def _salvar_overview(self, analises):
        """Salva overview de todas as análises"""
        overview = []
        
        for analise in analises:
            scores = analise.get("scores", {})
            overview.append({
                "cliente": analise.get("cliente", ""),
                "urgencia": scores.get("urgencia", 0),
                "necessidade": scores.get("necessidade", 0),
                "fit": scores.get("fit", 0),
                "confianca": scores.get("confianca", 0),
                "temperature": analise.get("temperature", "Cold"),
                "prioridade": (scores.get("urgencia", 0) + scores.get("necessidade", 0) + scores.get("fit", 0)) / 3
            })
        
        # Ordena por prioridade
        overview.sort(key=lambda x: x["prioridade"], reverse=True)
        
        (self.output_dir / "overview_geral.json").write_text(
            json.dumps(overview, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )
        
        # Salva também em CSV para Excel
        df = pd.DataFrame(overview)
        df.to_csv(self.output_dir / "overview_geral.csv", index=False, encoding="utf-8")
        
        print(f"✓ Overview salvo em: {self.output_dir / 'overview_geral.json'}")
    
    def _gerar_graficos(self, analises):
        """Gera gráficos de análise"""
        if not analises:
            return
        
        # Prepara dados
        clientes = [a.get("cliente", "") for a in analises]
        urgencia = [a.get("scores", {}).get("urgencia", 0) for a in analises]
        necessidade = [a.get("scores", {}).get("necessidade", 0) for a in analises]
        fit = [a.get("scores", {}).get("fit", 0) for a in analises]
        prioridade = [(u + n + f) / 3 for u, n, f in zip(urgencia, necessidade, fit)]
        
        # Gráfico 1: Prioridade por cliente
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        bars = plt.bar(range(len(clientes)), prioridade, color='skyblue', alpha=0.7)
        plt.xticks(range(len(clientes)), clientes, rotation=45, ha='right')
        plt.ylabel('Prioridade (0-1)')
        plt.title('Prioridade de Contas')
        plt.grid(True, alpha=0.3)
        
        # Colorir barras por temperatura
        for i, analise in enumerate(analises):
            temp = analise.get("temperature", "Cold")
            if temp == "Hot":
                bars[i].set_color('red')
            elif temp == "Warm":
                bars[i].set_color('orange')
            else:
                bars[i].set_color('lightblue')
        
        # Gráfico 2: Scatter plot Urgência vs Necessidade
        plt.subplot(2, 2, 2)
        scatter = plt.scatter(urgencia, necessidade, s=[f*200 for f in fit], 
                            c=prioridade, cmap='RdYlGn', alpha=0.7)
        plt.xlabel('Urgência')
        plt.ylabel('Necessidade')
        plt.title('Urgência vs Necessidade\n(Tamanho = Fit, Cor = Prioridade)')
        plt.colorbar(scatter, label='Prioridade')
        plt.grid(True, alpha=0.3)
        
        # Adicionar labels dos clientes
        for i, cliente in enumerate(clientes):
            plt.annotate(cliente, (urgencia[i], necessidade[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Gráfico 3: Distribuição de temperaturas
        plt.subplot(2, 2, 3)
        temperaturas = [a.get("temperature", "Cold") for a in analises]
        temp_counts = pd.Series(temperaturas).value_counts()
        plt.pie(temp_counts.values, labels=temp_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Distribuição de Temperaturas')
        
        # Gráfico 4: Heatmap de scores
        plt.subplot(2, 2, 4)
        scores_matrix = [[u, n, f] for u, n, f in zip(urgencia, necessidade, fit)]
        sns.heatmap(scores_matrix, 
                   xticklabels=['Urgência', 'Necessidade', 'Fit'],
                   yticklabels=clientes,
                   annot=True, fmt='.2f', cmap='RdYlGn')
        plt.title('Heatmap de Scores')
        plt.tight_layout()
        
        # Salva gráfico
        plt.savefig(self.output_dir / "analise_visual.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Gráficos salvos em: {self.output_dir / 'analise_visual.png'}")
    
    def gerar_plano_acao(self, analises):
        """Gera um plano de ação concreto com datas e sugestões específicas"""
        print("\n🎯 Gerando Plano de Ação Estratégico...")
        
        # Ordena por prioridade
        analises_ordenadas = sorted(analises, key=lambda x: x.get("scores", {}).get("prioridade", 0), reverse=True)
        
        plano_acao = {
            "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "resumo_executivo": f"Plano de ação para {len(analises)} leads analisados",
            "leads_por_prioridade": [],
            "acoes_imediatas": [],
            "acoes_semana": [],
            "acoes_mes": [],
            "metricas_sucesso": [],
            "calendario_sugerido": []
        }
        
        # Analisa cada lead e gera sugestões específicas
        for i, analise in enumerate(analises_ordenadas):
            cliente = analise.get("cliente", "")
            scores = analise.get("scores", {})
            urgencia = scores.get("urgencia", 0)
            necessidade = scores.get("necessidade", 0)
            fit = scores.get("fit", 0)
            prioridade = (urgencia + necessidade + fit) / 3
            temperatura = analise.get("temperature", "Cold")
            
            # Classifica o lead
            if prioridade >= 0.8:
                categoria = "🔥 CRÍTICO"
                prazo_base = 1  # dias
            elif prioridade >= 0.6:
                categoria = "⚡ ALTO"
                prazo_base = 3  # dias
            elif prioridade >= 0.4:
                categoria = "📈 MÉDIO"
                prazo_base = 7  # dias
            else:
                categoria = "📋 BAIXO"
                prazo_base = 14  # dias
            
            # Gera sugestões específicas baseadas na análise
            sugestoes = self._gerar_sugestoes_especificas(analise, prazo_base)
            
            lead_info = {
                "cliente": cliente,
                "categoria": categoria,
                "prioridade": round(prioridade, 2),
                "temperatura": temperatura,
                "sugestoes": sugestoes
            }
            
            plano_acao["leads_por_prioridade"].append(lead_info)
            
            # Adiciona ações imediatas para leads críticos
            if prioridade >= 0.8:
                plano_acao["acoes_imediatas"].extend(sugestoes[:2])  # 2 primeiras sugestões
            elif prioridade >= 0.6:
                plano_acao["acoes_semana"].extend(sugestoes[:2])
            else:
                plano_acao["acoes_mes"].extend(sugestoes[:1])
        
        # Gera métricas de sucesso
        plano_acao["metricas_sucesso"] = [
            "Taxa de conversão de leads quentes: >70%",
            "Tempo médio de resposta: <24h para leads críticos",
            "Taxa de follow-up: 100% dos leads em 48h",
            "Taxa de reuniões agendadas: >50% dos contatos"
        ]
        
        # Gera calendário sugerido
        hoje = datetime.now()
        plano_acao["calendario_sugerido"] = [
            {
                "data": (hoje + timedelta(days=1)).strftime("%Y-%m-%d"),
                "atividade": "Follow-up imediato com leads críticos",
                "leads": [l["cliente"] for l in analises_ordenadas[:2] if l.get("scores", {}).get("prioridade", 0) >= 0.8]
            },
            {
                "data": (hoje + timedelta(days=3)).strftime("%Y-%m-%d"),
                "atividade": "Reuniões de qualificação com leads de alta prioridade",
                "leads": [l["cliente"] for l in analises_ordenadas[2:4] if l.get("scores", {}).get("prioridade", 0) >= 0.6]
            },
            {
                "data": (hoje + timedelta(days=7)).strftime("%Y-%m-%d"),
                "atividade": "Apresentação de propostas para leads quentes",
                "leads": [l["cliente"] for l in analises_ordenadas[:3] if l.get("scores", {}).get("prioridade", 0) >= 0.7]
            },
            {
                "data": (hoje + timedelta(days=14)).strftime("%Y-%m-%d"),
                "atividade": "Revisão de pipeline e ajustes estratégicos",
                "leads": "Todos os leads ativos"
            }
        ]
        
        # Salva o plano de ação
        self._salvar_plano_acao(plano_acao)
        
        # Exibe resumo no console
        self._exibir_resumo_plano(plano_acao)
        
        return plano_acao
    
    def _gerar_sugestoes_especificas(self, analise, prazo_base):
        """Gera sugestões específicas baseadas na análise do lead"""
        cliente = analise.get("cliente", "")
        scores = analise.get("scores", {})
        urgencia = scores.get("urgencia", 0)
        necessidade = scores.get("necessidade", 0)
        fit = scores.get("fit", 0)
        temperatura = analise.get("temperature", "Cold")
        
        sugestoes = []
        
        # Sugestões baseadas na urgência
        if urgencia >= 0.7:
            sugestoes.append({
                "acao": f"Ligação imediata para {cliente} - Lead com alta urgência",
                "prazo": f"{prazo_base} dia(s)",
                "prioridade": "ALTA",
                "tipo": "Contato direto"
            })
            sugestoes.append({
                "acao": f"Envio de proposta comercial para {cliente}",
                "prazo": f"{prazo_base + 1} dia(s)",
                "prioridade": "ALTA",
                "tipo": "Proposta"
            })
        elif urgencia >= 0.4:
            sugestoes.append({
                "acao": f"Email de follow-up para {cliente}",
                "prazo": f"{prazo_base} dia(s)",
                "prioridade": "MÉDIA",
                "tipo": "Follow-up"
            })
        
        # Sugestões baseadas na necessidade
        if necessidade >= 0.7:
            sugestoes.append({
                "acao": f"Agendar reunião de descoberta com {cliente}",
                "prazo": f"{prazo_base + 2} dias",
                "prioridade": "ALTA",
                "tipo": "Reunião"
            })
            sugestoes.append({
                "acao": f"Enviar case de sucesso relevante para {cliente}",
                "prazo": f"{prazo_base + 1} dia(s)",
                "prioridade": "MÉDIA",
                "tipo": "Conteúdo"
            })
        
        # Sugestões baseadas no fit
        if fit >= 0.7:
            sugestoes.append({
                "acao": f"Preparar demonstração personalizada para {cliente}",
                "prazo": f"{prazo_base + 3} dias",
                "prioridade": "ALTA",
                "tipo": "Demonstração"
            })
        elif fit >= 0.4:
            sugestoes.append({
                "acao": f"Agendar call de qualificação técnica com {cliente}",
                "prazo": f"{prazo_base + 5} dias",
                "prioridade": "MÉDIA",
                "tipo": "Qualificação"
            })
        
        # Sugestões baseadas na temperatura
        if temperatura == "Hot":
            sugestoes.append({
                "acao": f"Preparar contrato e fechar negócio com {cliente}",
                "prazo": f"{prazo_base} dia(s)",
                "prioridade": "CRÍTICA",
                "tipo": "Fechamento"
            })
        elif temperatura == "Warm":
            sugestoes.append({
                "acao": f"Nurturing campaign para {cliente}",
                "prazo": f"{prazo_base + 7} dias",
                "prioridade": "MÉDIA",
                "tipo": "Nurturing"
            })
        else:
            sugestoes.append({
                "acao": f"Educação e awareness para {cliente}",
                "prazo": f"{prazo_base + 14} dias",
                "prioridade": "BAIXA",
                "tipo": "Educação"
            })
        
        # Adiciona sugestões genéricas baseadas na prioridade
        prioridade = (urgencia + necessidade + fit) / 3
        if prioridade >= 0.8:
            sugestoes.append({
                "acao": f"Envolver gestor sênior no deal {cliente}",
                "prazo": f"{prazo_base} dia(s)",
                "prioridade": "ALTA",
                "tipo": "Gestão"
            })
        
        return sugestoes[:5]  # Máximo 5 sugestões por lead
    
    def _salvar_plano_acao(self, plano_acao):
        """Salva o plano de ação em arquivos organizados"""
        # Salva JSON completo
        (self.output_dir / "plano_acao_completo.json").write_text(
            json.dumps(plano_acao, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )
        
        # Salva resumo executivo
        resumo = f"""PLANO DE AÇÃO ESTRATÉGICO
Gerado em: {plano_acao['data_geracao']}

RESUMO EXECUTIVO:
{plano_acao['resumo_executivo']}

LEADS POR PRIORIDADE:
"""
        for lead in plano_acao['leads_por_prioridade']:
            resumo += f"\n{lead['categoria']} - {lead['cliente']} (Prioridade: {lead['prioridade']})"
            for sugestao in lead['sugestoes'][:3]:  # Top 3 sugestões
                resumo += f"\n  • {sugestao['acao']} ({sugestao['prazo']})"
        
        resumo += f"\n\nAÇÕES IMEDIATAS ({len(plano_acao['acoes_imediatas'])} ações):\n"
        for acao in plano_acao['acoes_imediatas']:
            resumo += f"• {acao['acao']} ({acao['prazo']})\n"
        
        resumo += f"\nCALENDÁRIO SUGERIDO:\n"
        for evento in plano_acao['calendario_sugerido']:
            resumo += f"• {evento['data']}: {evento['atividade']}\n"
        
        (self.output_dir / "plano_acao_resumo.txt").write_text(resumo, encoding="utf-8")
        
        # Salva CSV para Excel
        dados_csv = []
        for lead in plano_acao['leads_por_prioridade']:
            for sugestao in lead['sugestoes']:
                dados_csv.append({
                    'Cliente': lead['cliente'],
                    'Categoria': lead['categoria'],
                    'Prioridade': lead['prioridade'],
                    'Temperatura': lead['temperatura'],
                    'Ação': sugestao['acao'],
                    'Prazo': sugestao['prazo'],
                    'Prioridade_Ação': sugestao['prioridade'],
                    'Tipo': sugestao['tipo']
                })
        
        df = pd.DataFrame(dados_csv)
        df.to_csv(self.output_dir / "plano_acao_detalhado.csv", index=False, encoding="utf-8")
        
        print(f"✓ Plano de ação salvo em: {self.output_dir}")
    
    def _exibir_resumo_plano(self, plano_acao):
        """Exibe resumo do plano de ação no console"""
        print("\n" + "="*60)
        print("🎯 PLANO DE AÇÃO ESTRATÉGICO GERADO")
        print("="*60)
        
        print(f"\n📊 RESUMO:")
        print(f"   • {len(plano_acao['leads_por_prioridade'])} leads analisados")
        print(f"   • {len(plano_acao['acoes_imediatas'])} ações imediatas")
        print(f"   • {len(plano_acao['acoes_semana'])} ações para esta semana")
        print(f"   • {len(plano_acao['acoes_mes'])} ações para este mês")
        
        print(f"\n🔥 TOP 3 LEADS CRÍTICOS:")
        for i, lead in enumerate(plano_acao['leads_por_prioridade'][:3], 1):
            print(f"   {i}. {lead['cliente']} - {lead['categoria']} (Prioridade: {lead['prioridade']})")
        
        print(f"\n⚡ AÇÕES IMEDIATAS (próximos 2 dias):")
        for acao in plano_acao['acoes_imediatas'][:3]:
            print(f"   • {acao['acao']} ({acao['prazo']})")
        
        print(f"\n📅 PRÓXIMAS ATIVIDADES:")
        for evento in plano_acao['calendario_sugerido'][:3]:
            print(f"   • {evento['data']}: {evento['atividade']}")
        
        print(f"\n📁 Arquivos gerados:")
        print(f"   • plano_acao_completo.json")
        print(f"   • plano_acao_resumo.txt")
        print(f"   • plano_acao_detalhado.csv")
        
        print("="*60)

def main():
    """Função principal para executar o analisador"""
    print("🚀 Iniciando Analisador Estratégico de Reuniões - VERSÃO LOCAL")
    print("=" * 60)
    print("✅ Funciona SEM chave da OpenAI!")
    print("✅ Análise baseada em padrões e regras locais!")
    print("=" * 60)
    
    # Inicializa e executa
    analisador = AnalisadorReunioesLocal()
    analises = analisador.processar_todas_reunioes()
    
    # Gera plano de ação estratégico
    if analises:
        analisador.gerar_plano_acao(analises)
    
    print("\n🎯 Análise concluída! Verifique a pasta 'Analises' para os resultados.")

if __name__ == "__main__":
    main()
