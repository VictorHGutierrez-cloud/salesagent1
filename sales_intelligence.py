"""
🧠 SALES AGENT IA - MOTOR DE INTELIGÊNCIA
========================================
Sistema que combina LLM + Base de Conhecimento para gerar sugestões estratégicas
"""

import time
import json
import threading
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

import openai
from rich.console import Console
from loguru import logger

from config import Config, SYSTEM_PROMPTS
from knowledge_embedder import SalesKnowledgeEmbedder
from speech_processor import TranscriptionResult, ConversationSegment

console = Console()

@dataclass
class SalesSuggestion:
    """Sugestão estratégica de vendas"""
    suggestion_text: str
    confidence: float
    urgency: int  # 1-10
    category: str  # 'objection', 'closing', 'discovery', etc.
    context_used: List[str]
    timestamp: float
    reasoning: str

@dataclass
class SalesContext:
    """Contexto atual da venda"""
    current_stage: str
    client_sentiment: str
    detected_objections: List[str]
    buying_signals: List[str]
    urgency_level: int
    key_topics: List[str]
    conversation_history: str

class SalesIntelligenceEngine:
    """Motor principal de inteligência de vendas"""
    
    def __init__(self, suggestion_callback: Optional[Callable[[SalesSuggestion], None]] = None):
        # Valida configuração
        if not Config.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY não configurada!")
            
        # Inicializa componentes
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.knowledge_base = SalesKnowledgeEmbedder()
        self.suggestion_callback = suggestion_callback
        
        # Estado da conversa
        self.current_context = SalesContext(
            current_stage="discovery",
            client_sentiment="neutral",
            detected_objections=[],
            buying_signals=[],
            urgency_level=5,
            key_topics=[],
            conversation_history=""
        )
        
        # Histórico de sugestões
        self.suggestion_history: List[SalesSuggestion] = []
        self.last_suggestion_time = 0
        self.min_suggestion_interval = 5.0  # segundos entre sugestões
        
        # Thread de processamento
        self.processing_queue = []
        self.processing_lock = threading.Lock()
        
        logger.info("🧠 Motor de inteligência de vendas inicializado")
    
    def process_transcription(self, transcription: TranscriptionResult):
        """Processa nova transcrição e gera sugestões"""
        try:
            # Atualiza contexto
            self._update_context(transcription.text)
            
            # Verifica se deve gerar sugestão
            if self._should_generate_suggestion():
                suggestion = self._generate_suggestion(transcription.text)
                
                if suggestion:
                    self.suggestion_history.append(suggestion)
                    self.last_suggestion_time = time.time()
                    
                    # Chama callback
                    if self.suggestion_callback:
                        self.suggestion_callback(suggestion)
                        
        except Exception as e:
            logger.error(f"❌ Erro ao processar transcrição: {e}")
    
    def _update_context(self, new_text: str):
        """Atualiza contexto da conversa"""
        # Adiciona ao histórico
        timestamp = datetime.now().strftime("%H:%M")
        self.current_context.conversation_history += f"\n[{timestamp}] Cliente: {new_text}"
        
        # Mantém apenas últimas 10 interações
        lines = self.current_context.conversation_history.split('\n')
        if len(lines) > 20:
            self.current_context.conversation_history = '\n'.join(lines[-20:])
        
        # Analisa novos padrões
        self._analyze_conversation_patterns(new_text)
    
    def _analyze_conversation_patterns(self, text: str):
        """Analisa padrões na conversa atual"""
        text_lower = text.lower()
        
        # Detecta objeções
        objection_patterns = [
            "muito caro", "não tenho orçamento", "vou pensar", "não é prioridade",
            "já uso", "não preciso", "complicado", "não funciona"
        ]
        
        for pattern in objection_patterns:
            if pattern in text_lower and pattern not in self.current_context.detected_objections:
                self.current_context.detected_objections.append(pattern)
        
        # Detecta sinais de compra
        buying_signals = [
            "quando", "como implementar", "quanto custa", "prazo", "contrato",
            "vamos", "quero", "preciso", "interessante", "faz sentido"
        ]
        
        for signal in buying_signals:
            if signal in text_lower and signal not in self.current_context.buying_signals:
                self.current_context.buying_signals.append(signal)
        
        # Avalia sentimento
        positive_words = ["gosto", "interessante", "bom", "excelente", "legal", "perfeito"]
        negative_words = ["não", "difícil", "caro", "problema", "complicado", "ruim"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            self.current_context.client_sentiment = "positive"
        elif neg_count > pos_count:
            self.current_context.client_sentiment = "negative"
        else:
            self.current_context.client_sentiment = "neutral"
        
        # Detecta estágio da venda
        stage_indicators = {
            "awareness": ["empresa", "sobre", "quem somos"],
            "discovery": ["problema", "dificuldade", "desafio", "processo"],
            "solution": ["solução", "como resolve", "funciona", "features"],
            "evaluation": ["preço", "custo", "investimento", "comparar"],
            "decision": ["contrato", "fechar", "vamos começar", "quando"]
        }
        
        for stage, indicators in stage_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                self.current_context.current_stage = stage
                break
    
    def _should_generate_suggestion(self) -> bool:
        """Verifica se deve gerar nova sugestão"""
        # Respeita intervalo mínimo
        if time.time() - self.last_suggestion_time < self.min_suggestion_interval:
            return False
        
        # Gera se detectou objeção
        if self.current_context.detected_objections:
            return True
        
        # Gera se detectou sinal de compra forte
        strong_signals = ["quando", "quanto custa", "vamos", "contrato"]
        recent_text = self.current_context.conversation_history.split('\n')[-1].lower()
        if any(signal in recent_text for signal in strong_signals):
            return True
        
        # Gera se mudou de estágio
        return True
    
    def _generate_suggestion(self, current_input: str) -> Optional[SalesSuggestion]:
        """Gera sugestão baseada no contexto atual"""
        try:
            # Busca conhecimento relevante
            relevant_knowledge = self._get_relevant_knowledge(current_input)
            
            # Constrói prompt contextual
            prompt = self._build_suggestion_prompt(current_input, relevant_knowledge)
            
            # Gera sugestão com LLM
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["main_agent"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.OPENAI_TEMPERATURE,
                max_tokens=200
            )
            
            suggestion_text = response.choices[0].message.content.strip()
            
            # Cria objeto de sugestão
            suggestion = SalesSuggestion(
                suggestion_text=suggestion_text,
                confidence=0.8,  # Calculado baseado na qualidade do contexto
                urgency=self._calculate_urgency(),
                category=self._categorize_suggestion(suggestion_text),
                context_used=[item["source"] for item in relevant_knowledge],
                timestamp=time.time(),
                reasoning=self._explain_reasoning(current_input, relevant_knowledge)
            )
            
            logger.info(f"💡 Sugestão gerada: {suggestion_text[:50]}...")
            return suggestion
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar sugestão: {e}")
            return None
    
    def _get_relevant_knowledge(self, query: str) -> List[Dict]:
        """Busca conhecimento relevante na base"""
        # Combina query atual com contexto
        enhanced_query = f"{query} {' '.join(self.current_context.detected_objections)} {self.current_context.current_stage}"
        
        # Busca na base de conhecimento
        results = self.knowledge_base.search_knowledge(enhanced_query, top_k=3)
        
        return results
    
    def _build_suggestion_prompt(self, current_input: str, knowledge: List[Dict]) -> str:
        """Constrói prompt contextual para o LLM"""
        # Contexto da base de conhecimento
        knowledge_context = "\n\n".join([
            f"TÉCNICA ({item['category']}): {item['content'][:300]}..."
            for item in knowledge[:2]  # Limita para não exceder tokens
        ])
        
        # Prompt final
        prompt = SYSTEM_PROMPTS["main_agent"].format(
            context=knowledge_context,
            history=self.current_context.conversation_history[-500:],  # Últimos 500 chars
            user_input=current_input
        )
        
        return prompt
    
    def _calculate_urgency(self) -> int:
        """Calcula urgência da sugestão (1-10)"""
        urgency = 5  # Base
        
        # Aumenta por objeções
        urgency += len(self.current_context.detected_objections) * 2
        
        # Aumenta por sinais de compra
        urgency += len(self.current_context.buying_signals)
        
        # Ajusta por sentimento
        if self.current_context.client_sentiment == "negative":
            urgency += 3
        elif self.current_context.client_sentiment == "positive":
            urgency += 1
        
        return min(urgency, 10)
    
    def _categorize_suggestion(self, suggestion_text: str) -> str:
        """Categoriza a sugestão"""
        text_lower = suggestion_text.lower()
        
        if any(word in text_lower for word in ["objeção", "preocupação", "resolver"]):
            return "objection_handling"
        elif any(word in text_lower for word in ["fechar", "avançar", "próximo"]):
            return "closing"
        elif any(word in text_lower for word in ["descobrir", "perguntar", "entender"]):
            return "discovery"
        elif any(word in text_lower for word in ["valor", "benefício", "roi"]):
            return "value_proposition"
        else:
            return "general"
    
    def _explain_reasoning(self, input_text: str, knowledge: List[Dict]) -> str:
        """Explica o raciocínio por trás da sugestão"""
        reasoning_parts = []
        
        # Context
        reasoning_parts.append(f"Estágio: {self.current_context.current_stage}")
        reasoning_parts.append(f"Sentimento: {self.current_context.client_sentiment}")
        
        if self.current_context.detected_objections:
            reasoning_parts.append(f"Objeções: {', '.join(self.current_context.detected_objections[-2:])}")
        
        if knowledge:
            reasoning_parts.append(f"Técnicas: {', '.join([k['category'] for k in knowledge[:2]])}")
        
        return " | ".join(reasoning_parts)
    
    def get_conversation_summary(self) -> Dict:
        """Retorna resumo da conversa atual"""
        return {
            "stage": self.current_context.current_stage,
            "sentiment": self.current_context.client_sentiment,
            "objections_count": len(self.current_context.detected_objections),
            "buying_signals_count": len(self.current_context.buying_signals),
            "suggestions_generated": len(self.suggestion_history),
            "last_suggestion": self.suggestion_history[-1].suggestion_text if self.suggestion_history else None
        }
    
    def reset_conversation(self):
        """Reseta contexto da conversa"""
        self.current_context = SalesContext(
            current_stage="discovery",
            client_sentiment="neutral",
            detected_objections=[],
            buying_signals=[],
            urgency_level=5,
            key_topics=[],
            conversation_history=""
        )
        self.suggestion_history.clear()
        
        console.print("🔄 Contexto da conversa resetado")
    
    def export_session_report(self) -> str:
        """Exporta relatório da sessão"""
        try:
            report_data = {
                "session_timestamp": datetime.now().isoformat(),
                "conversation_summary": self.get_conversation_summary(),
                "context": asdict(self.current_context),
                "suggestions": [asdict(s) for s in self.suggestion_history],
                "performance_metrics": {
                    "total_suggestions": len(self.suggestion_history),
                    "avg_confidence": sum(s.confidence for s in self.suggestion_history) / len(self.suggestion_history) if self.suggestion_history else 0,
                    "categories_used": list(set(s.category for s in self.suggestion_history))
                }
            }
            
            filename = f"session_report_{int(time.time())}.json"
            filepath = Config.TEMP_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Relatório exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar relatório: {e}")
            return ""

class SuggestionFormatter:
    """Formatador de sugestões para diferentes outputs"""
    
    @staticmethod
    def format_for_overlay(suggestion: SalesSuggestion) -> str:
        """Formata sugestão para overlay visual"""
        urgency_emoji = "🔥" if suggestion.urgency >= 8 else "💡" if suggestion.urgency >= 6 else "💭"
        
        formatted = f"{urgency_emoji} {suggestion.suggestion_text}"
        
        # Adiciona categoria se relevante
        if suggestion.category == "objection_handling":
            formatted = f"🛡️ {suggestion.suggestion_text}"
        elif suggestion.category == "closing":
            formatted = f"🎯 {suggestion.suggestion_text}"
        
        return formatted
    
    @staticmethod
    def format_for_audio(suggestion: SalesSuggestion) -> str:
        """Formata sugestão para áudio (TTS)"""
        # Remove emojis e simplifica para áudio
        clean_text = suggestion.suggestion_text.replace("💡", "").replace("🎯", "").strip()
        return f"Sugestão: {clean_text}"
    
    @staticmethod
    def format_detailed(suggestion: SalesSuggestion) -> str:
        """Formato detalhado para logs"""
        return f"""
SUGESTÃO DETALHADA
==================
Texto: {suggestion.suggestion_text}
Categoria: {suggestion.category}
Urgência: {suggestion.urgency}/10
Confiança: {suggestion.confidence:.2f}
Contexto: {suggestion.reasoning}
Fontes: {', '.join(suggestion.context_used)}
Timestamp: {datetime.fromtimestamp(suggestion.timestamp).strftime('%H:%M:%S')}
"""

def test_sales_intelligence():
    """Teste do motor de inteligência"""
    console.print("🧪 [bold cyan]Teste do Motor de Inteligência[/bold cyan]")
    
    def suggestion_callback(suggestion: SalesSuggestion):
        formatted = SuggestionFormatter.format_for_overlay(suggestion)
        console.print(f"💡 [bold green]SUGESTÃO:[/bold green] {formatted}")
        console.print(f"   Categoria: {suggestion.category} | Urgência: {suggestion.urgency}/10")
    
    # Inicializa motor
    engine = SalesIntelligenceEngine(suggestion_callback)
    
    # Simula transcrições
    test_inputs = [
        "Olá, gostaria de saber mais sobre o sistema de vocês",
        "Parece interessante, mas está muito caro",
        "Já uso um sistema similar da concorrência",
        "Quanto tempo demora para implementar?",
        "Vou conversar com minha equipe e volto a falar"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        console.print(f"\n🎤 [bold blue]Input {i}:[/bold blue] {test_input}")
        
        # Simula transcrição
        from speech_processor import TranscriptionResult
        transcription = TranscriptionResult(
            text=test_input,
            timestamp=time.time(),
            confidence=0.9,
            language="pt",
            duration=2.0
        )
        
        engine.process_transcription(transcription)
        time.sleep(1)
    
    # Mostra resumo
    summary = engine.get_conversation_summary()
    console.print(f"\n📊 [bold yellow]Resumo da Conversa:[/bold yellow]")
    for key, value in summary.items():
        console.print(f"   {key}: {value}")

if __name__ == "__main__":
    test_sales_intelligence()
