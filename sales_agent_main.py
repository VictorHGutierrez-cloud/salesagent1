"""
🚀 SALES AGENT IA - SISTEMA PRINCIPAL
===================================
Sistema completo que integra todos os componentes
"""

import threading
import time
import signal
import sys
from typing import Optional
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from loguru import logger

from config import Config
from audio_capture import AudioCapture, AudioChunk
from speech_processor import SpeechProcessor, TranscriptionResult
from sales_intelligence import SalesIntelligenceEngine, SalesSuggestion
from overlay_interface import SalesOverlay, UIConfig
from knowledge_embedder import SalesKnowledgeEmbedder

console = Console()

@dataclass
class SystemStats:
    """Estatísticas do sistema"""
    uptime: float = 0
    audio_chunks_processed: int = 0
    transcriptions_made: int = 0
    suggestions_generated: int = 0
    knowledge_base_ready: bool = False
    is_recording: bool = False

class SalesAgentSystem:
    """Sistema principal do Sales Agent IA"""
    
    def __init__(self):
        # Validação inicial
        Config.validate_config()
        Config.create_directories()
        
        # Estatísticas
        self.stats = SystemStats()
        self.start_time = time.time()
        
        # Componentes principais
        self.audio_capture: Optional[AudioCapture] = None
        self.speech_processor: Optional[SpeechProcessor] = None
        self.intelligence_engine: Optional[SalesIntelligenceEngine] = None
        self.overlay_interface: Optional[SalesOverlay] = None
        self.knowledge_embedder: Optional[SalesKnowledgeEmbedder] = None
        
        # Estado do sistema
        self.is_running = False
        self.system_ready = False
        
        # Setup de logging
        self._setup_logging()
        
        logger.info("🚀 Sales Agent IA - Sistema inicializado")
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        logger.remove()  # Remove handler padrão
        
        # Handler para console
        logger.add(
            sys.stderr,
            level=Config.LOG_LEVEL,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # Handler para arquivo
        logger.add(
            Config.BASE_DIR / "logs" / "sales_agent_{time}.log",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            format="{time} | {level} | {name}:{function}:{line} - {message}"
        )
    
    def initialize_system(self):
        """Inicializa todos os componentes do sistema"""
        console.print(Panel.fit(
            "[bold blue]🚀 SALES AGENT IA - INICIALIZANDO SISTEMA[/bold blue]",
            border_style="blue"
        ))
        
        try:
            # 1. Inicializa base de conhecimento
            console.print("📚 [bold yellow]Inicializando base de conhecimento...[/bold yellow]")
            self._initialize_knowledge_base()
            
            # 2. Inicializa motor de inteligência
            console.print("🧠 [bold yellow]Inicializando motor de inteligência...[/bold yellow]")
            self._initialize_intelligence_engine()
            
            # 3. Inicializa processador de fala
            console.print("🗣️ [bold yellow]Inicializando processador de fala...[/bold yellow]")
            self._initialize_speech_processor()
            
            # 4. Inicializa captura de áudio
            console.print("🎤 [bold yellow]Inicializando captura de áudio...[/bold yellow]")
            self._initialize_audio_capture()
            
            # 5. Inicializa interface
            console.print("🖥️ [bold yellow]Inicializando interface...[/bold yellow]")
            self._initialize_interface()
            
            self.system_ready = True
            
            console.print(Panel.fit(
                "[bold green]✅ SISTEMA INICIALIZADO COM SUCESSO![/bold green]",
                border_style="green"
            ))
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            console.print(f"[bold red]❌ Erro na inicialização: {e}[/bold red]")
            raise
    
    def _initialize_knowledge_base(self):
        """Inicializa base de conhecimento"""
        self.knowledge_embedder = SalesKnowledgeEmbedder()
        
        # Verifica se base já existe
        try:
            stats = self.knowledge_embedder.get_stats()
            if "error" not in stats:
                console.print("✅ Base de conhecimento encontrada")
                self.stats.knowledge_base_ready = True
            else:
                raise ValueError("Base não encontrada")
        except:
            console.print("🔄 Construindo base de conhecimento...")
            self.knowledge_embedder.build_knowledge_base()
            self.stats.knowledge_base_ready = True
    
    def _initialize_intelligence_engine(self):
        """Inicializa motor de inteligência"""
        def suggestion_callback(suggestion: SalesSuggestion):
            self.stats.suggestions_generated += 1
            # Envia para interface
            if self.overlay_interface:
                self.overlay_interface.show_suggestion(suggestion)
            
            logger.info(f"💡 Sugestão: {suggestion.suggestion_text[:50]}...")
        
        self.intelligence_engine = SalesIntelligenceEngine(suggestion_callback)
    
    def _initialize_speech_processor(self):
        """Inicializa processador de fala"""
        def transcription_callback(transcription: TranscriptionResult):
            self.stats.transcriptions_made += 1
            
            # Envia para motor de inteligência
            if self.intelligence_engine:
                self.intelligence_engine.process_transcription(transcription)
            
            logger.info(f"🎙️ Transcrito: {transcription.text[:50]}...")
        
        self.speech_processor = SpeechProcessor(transcription_callback)
    
    def _initialize_audio_capture(self):
        """Inicializa captura de áudio"""
        def audio_callback(audio_chunk: AudioChunk):
            self.stats.audio_chunks_processed += 1
            
            # Envia para processador de fala
            if self.speech_processor:
                self.speech_processor.process_audio_chunk(audio_chunk)
        
        self.audio_capture = AudioCapture(audio_callback)
    
    def _initialize_interface(self):
        """Inicializa interface"""
        ui_config = UIConfig(
            position=Config.OVERLAY_POSITION,
            opacity=Config.OVERLAY_OPACITY,
            width=Config.OVERLAY_WIDTH,
            height=Config.OVERLAY_HEIGHT
        )
        
        self.overlay_interface = SalesOverlay(ui_config)
    
    def start_system(self):
        """Inicia sistema completo"""
        if not self.system_ready:
            raise RuntimeError("Sistema não inicializado. Execute initialize_system() primeiro.")
        
        if self.is_running:
            logger.warning("⚠️ Sistema já está rodando")
            return
        
        console.print(Panel.fit(
            "[bold green]🎯 INICIANDO SALES AGENT IA[/bold green]",
            border_style="green"
        ))
        
        try:
            # Inicia componentes em ordem
            self.overlay_interface.start_interface()
            self.speech_processor.start_processing()
            self.audio_capture.start_recording()
            
            self.is_running = True
            self.stats.is_recording = True
            
            console.print("✅ [bold green]Sistema ativo e monitorando![/bold green]")
            console.print("💡 [yellow]Fale durante suas reuniões para receber sugestões em tempo real[/yellow]")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema: {e}")
            self.stop_system()
            raise
    
    def stop_system(self):
        """Para sistema completo"""
        if not self.is_running:
            return
        
        console.print("⏹️ [bold yellow]Parando sistema...[/bold yellow]")
        
        try:
            # Para componentes em ordem reversa
            if self.audio_capture:
                self.audio_capture.stop_recording()
            
            if self.speech_processor:
                self.speech_processor.stop_processing()
            
            if self.overlay_interface:
                self.overlay_interface.stop_interface()
            
            self.is_running = False
            self.stats.is_recording = False
            
            console.print("✅ [bold green]Sistema parado com sucesso[/bold green]")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar sistema: {e}")
    
    def get_system_status(self) -> dict:
        """Retorna status completo do sistema"""
        self.stats.uptime = time.time() - self.start_time
        
        return {
            "system_ready": self.system_ready,
            "is_running": self.is_running,
            "uptime": self.stats.uptime,
            "stats": {
                "audio_chunks": self.stats.audio_chunks_processed,
                "transcriptions": self.stats.transcriptions_made,
                "suggestions": self.stats.suggestions_generated,
                "knowledge_base_ready": self.stats.knowledge_base_ready,
                "is_recording": self.stats.is_recording
            },
            "components": {
                "audio_capture": self.audio_capture.get_audio_stats() if self.audio_capture else {},
                "speech_processor": self.speech_processor.get_stats() if self.speech_processor else {},
                "intelligence": self.intelligence_engine.get_conversation_summary() if self.intelligence_engine else {}
            }
        }
    
    def create_status_display(self) -> Table:
        """Cria display de status em tempo real"""
        status = self.get_system_status()
        
        table = Table(title="📊 SALES AGENT IA - STATUS")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Detalhes", style="yellow")
        
        # Status geral
        system_status = "🟢 ATIVO" if status["is_running"] else "🔴 PARADO"
        uptime_str = f"{status['uptime']:.0f}s"
        table.add_row("Sistema", system_status, f"Uptime: {uptime_str}")
        
        # Base de conhecimento
        kb_status = "✅ Pronta" if status["stats"]["knowledge_base_ready"] else "❌ Não pronta"
        table.add_row("Base de Conhecimento", kb_status, "")
        
        # Captura de áudio
        audio_status = "🎤 Gravando" if status["stats"]["is_recording"] else "⏸️ Parado"
        audio_details = f"Chunks: {status['stats']['audio_chunks']}"
        table.add_row("Captura de Áudio", audio_status, audio_details)
        
        # Processamento de fala
        speech_details = f"Transcrições: {status['stats']['transcriptions']}"
        table.add_row("Processamento de Fala", "🗣️ Ativo", speech_details)
        
        # Motor de inteligência
        intel_details = f"Sugestões: {status['stats']['suggestions']}"
        table.add_row("Motor de Inteligência", "🧠 Ativo", intel_details)
        
        # Interface
        table.add_row("Interface", "🖥️ Ativa", "Overlay + System Tray")
        
        return table
    
    def run_interactive_mode(self):
        """Executa sistema em modo interativo com dashboard"""
        try:
            # Inicializa sistema
            self.initialize_system()
            self.start_system()
            
            # Dashboard em tempo real
            with Live(self.create_status_display(), refresh_per_second=1, screen=True) as live:
                while self.is_running:
                    live.update(self.create_status_display())
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            console.print("\n⏹️ [bold yellow]Interrompido pelo usuário[/bold yellow]")
        except Exception as e:
            console.print(f"\n❌ [bold red]Erro: {e}[/bold red]")
        finally:
            self.stop_system()
    
    def export_session_report(self) -> str:
        """Exporta relatório da sessão"""
        if self.intelligence_engine:
            return self.intelligence_engine.export_session_report()
        return ""

def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    console.print("\n⏹️ [bold yellow]Encerrando sistema...[/bold yellow]")
    sys.exit(0)

def main():
    """Função principal"""
    # Configura handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    console.print(Panel.fit(
        """
[bold blue]🚀 SALES AGENT IA[/bold blue]
[cyan]Seu consultor estratégico de vendas em tempo real[/cyan]

[yellow]Funcionalidades:[/yellow]
• 🎤 Captura de áudio em tempo real
• 🗣️ Transcrição com OpenAI Whisper  
• 🧠 Análise inteligente com GPT-4
• 💡 Sugestões baseadas em seu toolkit
• 🖥️ Interface não intrusiva
        """,
        border_style="blue"
    ))
    
    # Verifica configuração
    try:
        Config.validate_config()
    except ValueError as e:
        console.print(f"[bold red]❌ Erro de configuração: {e}[/bold red]")
        console.print("\n📝 [yellow]Para configurar:[/yellow]")
        console.print("1. Copie env_example.txt para .env")
        console.print("2. Adicione sua OPENAI_API_KEY no arquivo .env")
        console.print("3. Execute novamente")
        return
    
    # Cria e executa sistema
    system = SalesAgentSystem()
    
    try:
        system.run_interactive_mode()
    except Exception as e:
        console.print(f"[bold red]❌ Erro fatal: {e}[/bold red]")
        logger.exception("Erro fatal no sistema")
    
    console.print("\n👋 [bold blue]Obrigado por usar o Sales Agent IA![/bold blue]")

if __name__ == "__main__":
    main()
