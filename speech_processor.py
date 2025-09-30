"""
🗣️ SALES AGENT IA - PROCESSAMENTO DE FALA
========================================
Integração com OpenAI Whisper para Speech-to-Text em tempo real
"""

import os
import io
import time
import threading
import queue
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
from pathlib import Path

import openai
import soundfile as sf
import numpy as np
from rich.console import Console
from loguru import logger

from config import Config
from audio_capture import AudioChunk

console = Console()

@dataclass
class TranscriptionResult:
    """Resultado de transcrição"""
    text: str
    timestamp: float
    confidence: float
    language: str
    duration: float
    
@dataclass
class ConversationSegment:
    """Segmento de conversa transcrito"""
    speaker: str  # 'user' ou 'client'
    text: str
    timestamp: float
    confidence: float

class SpeechProcessor:
    """Processador de fala com OpenAI Whisper"""
    
    def __init__(self, transcription_callback: Optional[Callable[[TranscriptionResult], None]] = None):
        # Valida configuração
        if not Config.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY não configurada!")
            
        # Inicializa cliente OpenAI
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Callback para resultados
        self.transcription_callback = transcription_callback
        
        # Fila de processamento
        self.audio_queue = queue.Queue(maxsize=10)
        self.processing_thread = None
        self.should_stop = threading.Event()
        
        # Buffer para acumular áudio
        self.audio_buffer = []
        self.buffer_duration = 0
        self.min_audio_duration = 1.0  # segundos mínimos para transcrever
        self.max_buffer_duration = 10.0  # máximo buffer antes de forçar transcrição
        
        # Histórico de transcrições
        self.conversation_history: List[ConversationSegment] = []
        self.last_transcription_time = 0
        
        Config.create_directories()
        logger.info("🗣️ Processador de fala inicializado")
    
    def start_processing(self):
        """Inicia processamento de áudio"""
        if self.processing_thread and self.processing_thread.is_alive():
            logger.warning("⚠️ Processamento já está ativo")
            return
            
        self.should_stop.clear()
        self.processing_thread = threading.Thread(
            target=self._process_audio_queue,
            daemon=True
        )
        self.processing_thread.start()
        
        console.print("🗣️ [bold green]Processamento de fala iniciado![/bold green]")
    
    def stop_processing(self):
        """Para processamento de áudio"""
        self.should_stop.set()
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
            
        console.print("🗣️ [bold red]Processamento de fala parado[/bold red]")
    
    def process_audio_chunk(self, audio_chunk: AudioChunk):
        """Adiciona chunk de áudio para processamento"""
        if not audio_chunk.is_speech:
            return
            
        try:
            self.audio_queue.put_nowait(audio_chunk)
        except queue.Full:
            logger.warning("⚠️ Fila de processamento cheia, descartando áudio")
    
    def _process_audio_queue(self):
        """Thread principal de processamento"""
        logger.info("🔄 Thread de processamento de fala iniciada")
        
        while not self.should_stop.is_set():
            try:
                # Processa chunks da fila
                audio_chunk = self.audio_queue.get(timeout=0.5)
                self._accumulate_audio(audio_chunk)
                
            except queue.Empty:
                # Verifica se deve processar buffer acumulado
                self._check_buffer_timeout()
                continue
            except Exception as e:
                logger.error(f"❌ Erro no processamento: {e}")
        
        # Processa buffer final
        if self.audio_buffer:
            self._process_accumulated_audio()
            
        logger.info("🔄 Thread de processamento finalizada")
    
    def _accumulate_audio(self, audio_chunk: AudioChunk):
        """Acumula áudio no buffer para processamento em lote"""
        self.audio_buffer.append(audio_chunk.data)
        self.buffer_duration += audio_chunk.duration
        
        # Processa se atingiu duração mínima ou máxima
        if (self.buffer_duration >= self.min_audio_duration and 
            len(self.audio_buffer) > 5) or self.buffer_duration >= self.max_buffer_duration:
            self._process_accumulated_audio()
    
    def _check_buffer_timeout(self):
        """Verifica se buffer deve ser processado por timeout"""
        if not self.audio_buffer:
            return
            
        time_since_last = time.time() - self.last_transcription_time
        if time_since_last > 2.0 and self.buffer_duration >= self.min_audio_duration:
            self._process_accumulated_audio()
    
    def _process_accumulated_audio(self):
        """Processa áudio acumulado no buffer"""
        if not self.audio_buffer:
            return
            
        try:
            # Concatena chunks de áudio
            combined_audio = np.concatenate(self.audio_buffer)
            
            # Limpa buffer
            self.audio_buffer = []
            self.buffer_duration = 0
            
            # Transcreve áudio
            result = self._transcribe_audio(combined_audio)
            
            if result and result.text.strip():
                # Atualiza histórico
                segment = ConversationSegment(
                    speaker="client",  # Assume que é o cliente falando
                    text=result.text,
                    timestamp=result.timestamp,
                    confidence=result.confidence
                )
                self.conversation_history.append(segment)
                
                # Chama callback
                if self.transcription_callback:
                    self.transcription_callback(result)
                    
                self.last_transcription_time = time.time()
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio acumulado: {e}")
    
    def _transcribe_audio(self, audio_data: np.ndarray) -> Optional[TranscriptionResult]:
        """Transcreve áudio usando OpenAI Whisper"""
        try:
            timestamp = time.time()
            
            # Salva áudio temporário
            temp_file = Config.TEMP_DIR / f"audio_{int(timestamp)}.wav"
            sf.write(str(temp_file), audio_data, Config.SAMPLE_RATE)
            
            # Transcreve com OpenAI
            with open(temp_file, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=Config.WHISPER_MODEL,
                    file=audio_file,
                    language="pt",  # Português
                    temperature=0.1  # Baixa temperatura para mais precisão
                )
            
            # Remove arquivo temporário
            temp_file.unlink()
            
            # Cria resultado
            result = TranscriptionResult(
                text=response.text,
                timestamp=timestamp,
                confidence=0.9,  # Whisper não retorna confidence, assumimos alto
                language="pt",
                duration=len(audio_data) / Config.SAMPLE_RATE
            )
            
            logger.info(f"🎙️ Transcrito: '{result.text[:50]}...'")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na transcrição: {e}")
            return None
    
    def get_recent_conversation(self, max_segments: int = 5) -> List[ConversationSegment]:
        """Retorna conversação recente"""
        return self.conversation_history[-max_segments:] if self.conversation_history else []
    
    def get_conversation_context(self, max_chars: int = 1000) -> str:
        """Retorna contexto da conversa para o LLM"""
        recent_segments = self.get_recent_conversation(10)
        
        context_parts = []
        total_chars = 0
        
        for segment in reversed(recent_segments):
            segment_text = f"{segment.speaker}: {segment.text}"
            if total_chars + len(segment_text) > max_chars:
                break
            context_parts.insert(0, segment_text)
            total_chars += len(segment_text)
        
        return "\n".join(context_parts)
    
    def clear_conversation_history(self):
        """Limpa histórico de conversa"""
        self.conversation_history.clear()
        console.print("🗑️ Histórico de conversa limpo")
    
    def save_conversation(self, filename: Optional[str] = None):
        """Salva conversa em arquivo"""
        if not self.conversation_history:
            logger.warning("⚠️ Nenhuma conversa para salvar")
            return None
            
        if not filename:
            timestamp = int(time.time())
            filename = f"conversation_{timestamp}.txt"
            
        filepath = Config.TEMP_DIR / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("CONVERSA DE VENDAS - TRANSCRIÇÃO\n")
                f.write("=" * 50 + "\n\n")
                
                for segment in self.conversation_history:
                    f.write(f"[{time.strftime('%H:%M:%S', time.localtime(segment.timestamp))}] ")
                    f.write(f"{segment.speaker.upper()}: {segment.text}\n\n")
            
            logger.info(f"💾 Conversa salva: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar conversa: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do processamento"""
        return {
            "total_segments": len(self.conversation_history),
            "queue_size": self.audio_queue.qsize(),
            "buffer_duration": self.buffer_duration,
            "is_processing": self.processing_thread and self.processing_thread.is_alive(),
            "recent_activity": time.time() - self.last_transcription_time if self.last_transcription_time else None
        }

class ConversationAnalyzer:
    """Analisador de padrões de conversa"""
    
    def __init__(self):
        self.sales_keywords = {
            "objections": ["muito caro", "não tenho orçamento", "vou pensar", "não é prioridade"],
            "interest": ["interessante", "gostei", "faz sentido", "como funciona"],
            "buying_signals": ["quando", "como implementar", "quanto custa", "prazo"],
            "decision_makers": ["vou falar com", "preciso aprovar", "decisão", "gerente"]
        }
    
    def analyze_segment(self, segment: ConversationSegment) -> Dict:
        """Analisa um segmento de conversa"""
        text_lower = segment.text.lower()
        
        analysis = {
            "sentiment": self._analyze_sentiment(text_lower),
            "intent": self._detect_intent(text_lower),
            "keywords_found": self._find_keywords(text_lower),
            "urgency_level": self._assess_urgency(text_lower),
            "sales_stage": self._identify_sales_stage(text_lower)
        }
        
        return analysis
    
    def _analyze_sentiment(self, text: str) -> str:
        """Análise básica de sentimento"""
        positive_words = ["gosto", "interessante", "bom", "excelente", "legal"]
        negative_words = ["não", "difícil", "caro", "problema", "complicado"]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def _detect_intent(self, text: str) -> str:
        """Detecta intenção do cliente"""
        if any(word in text for word in ["como", "quando", "onde", "quanto"]):
            return "information_seeking"
        elif any(word in text for word in ["quero", "preciso", "vamos"]):
            return "ready_to_buy"
        elif any(word in text for word in ["não", "mas", "porém"]):
            return "objection"
        else:
            return "general"
    
    def _find_keywords(self, text: str) -> Dict[str, List[str]]:
        """Encontra palavras-chave por categoria"""
        found = {}
        
        for category, keywords in self.sales_keywords.items():
            found_keywords = [kw for kw in keywords if kw in text]
            if found_keywords:
                found[category] = found_keywords
                
        return found
    
    def _assess_urgency(self, text: str) -> int:
        """Avalia urgência (1-10)"""
        urgency_indicators = {
            "urgent": ["urgente", "agora", "hoje", "imediato"],
            "soon": ["semana", "mês", "próximo"],
            "later": ["futuro", "talvez", "eventualmente"]
        }
        
        if any(word in text for word in urgency_indicators["urgent"]):
            return 8
        elif any(word in text for word in urgency_indicators["soon"]):
            return 6
        elif any(word in text for word in urgency_indicators["later"]):
            return 3
        else:
            return 5
    
    def _identify_sales_stage(self, text: str) -> str:
        """Identifica estágio da venda"""
        if any(word in text for word in ["empresa", "sobre", "quem"]):
            return "awareness"
        elif any(word in text for word in ["problema", "dificuldade", "desafio"]):
            return "problem_identification"
        elif any(word in text for word in ["solução", "como resolve", "funciona"]):
            return "solution_exploration"
        elif any(word in text for word in ["preço", "custo", "investimento"]):
            return "evaluation"
        elif any(word in text for word in ["contrato", "fechar", "vamos"]):
            return "decision"
        else:
            return "discovery"

def test_speech_processor():
    """Teste do processador de fala"""
    console.print("🧪 [bold cyan]Teste do Processador de Fala[/bold cyan]")
    
    def transcription_callback(result: TranscriptionResult):
        console.print(f"📝 [bold green]Transcrito:[/bold green] {result.text}")
        console.print(f"   Confiança: {result.confidence:.2f} | Duração: {result.duration:.1f}s")
    
    processor = SpeechProcessor(transcription_callback)
    
    try:
        processor.start_processing()
        console.print("🎤 Processador ativo - aguardando áudio...")
        
        # Simula processamento
        time.sleep(30)
        
    except KeyboardInterrupt:
        console.print("\n⏹️ Parando processador...")
    finally:
        processor.stop_processing()
        
        # Mostra estatísticas
        stats = processor.get_stats()
        console.print(f"📊 Estatísticas: {stats}")

if __name__ == "__main__":
    test_speech_processor()
