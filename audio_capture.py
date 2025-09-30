"""
🎤 SALES AGENT IA - CAPTURA DE ÁUDIO
==================================
Sistema robusto de captura e processamento de áudio em tempo real
"""

import threading
import queue
import time
import numpy as np
from typing import Callable, Optional
from dataclasses import dataclass

import sounddevice as sd
import soundfile as sf
from scipy import signal
from rich.console import Console
from loguru import logger

from config import Config

console = Console()

@dataclass
class AudioChunk:
    """Representa um pedaço de áudio capturado"""
    data: np.ndarray
    timestamp: float
    duration: float
    is_speech: bool
    amplitude: float

class AudioCapture:
    """Sistema de captura de áudio em tempo real"""
    
    def __init__(self, callback: Optional[Callable[[AudioChunk], None]] = None):
        self.callback = callback
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
        # Configurações de áudio
        self.sample_rate = Config.SAMPLE_RATE
        self.channels = Config.CHANNELS
        self.chunk_duration = Config.CHUNK_DURATION
        self.frames_per_chunk = int(self.sample_rate * self.chunk_duration)
        
        # Buffer para acumular frames
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()
        
        # Configurações de detecção de voz
        self.silence_threshold = Config.AUDIO_THRESHOLD
        self.min_speech_duration = 0.5  # segundos
        self.max_silence_duration = 1.0  # segundos
        
        # Thread de processamento
        self.processing_thread = None
        self.should_stop = threading.Event()
        
        logger.info("🎤 Sistema de captura de áudio inicializado")
    
    def list_audio_devices(self):
        """Lista dispositivos de áudio disponíveis"""
        console.print("🔊 [bold blue]Dispositivos de áudio disponíveis:[/bold blue]")
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            device_type = "🎤" if device['max_input_channels'] > 0 else "🔊"
            console.print(f"  {i}: {device_type} {device['name']}")
            
        return devices
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback chamado pelo sounddevice para cada chunk de áudio"""
        if status:
            logger.warning(f"Audio callback status: {status}")
            
        # Copia dados para evitar problemas de concorrência
        audio_data = indata.copy()
        
        with self.buffer_lock:
            self.audio_buffer.extend(audio_data.flatten())
            
            # Quando buffer atinge tamanho do chunk, processa
            if len(self.audio_buffer) >= self.frames_per_chunk:
                chunk_data = np.array(self.audio_buffer[:self.frames_per_chunk])
                self.audio_buffer = self.audio_buffer[self.frames_per_chunk:]
                
                # Cria chunk de áudio
                audio_chunk = self._create_audio_chunk(chunk_data)
                
                # Adiciona à fila para processamento
                try:
                    self.audio_queue.put_nowait(audio_chunk)
                except queue.Full:
                    logger.warning("⚠️ Fila de áudio cheia, descartando chunk")
    
    def _create_audio_chunk(self, data: np.ndarray) -> AudioChunk:
        """Cria objeto AudioChunk com análise básica"""
        timestamp = time.time()
        duration = len(data) / self.sample_rate
        
        # Calcula amplitude RMS
        amplitude = np.sqrt(np.mean(data**2))
        
        # Detecta se é fala (básico por amplitude)
        is_speech = amplitude > self.silence_threshold
        
        return AudioChunk(
            data=data,
            timestamp=timestamp,
            duration=duration,
            is_speech=is_speech,
            amplitude=amplitude
        )
    
    def _enhance_audio(self, data: np.ndarray) -> np.ndarray:
        """Aplica melhorias básicas no áudio"""
        # Normalização
        if np.max(np.abs(data)) > 0:
            data = data / np.max(np.abs(data)) * 0.9
            
        # Filtro passa-alta para remover ruído de baixa frequência
        sos = signal.butter(4, 80, btype='highpass', fs=self.sample_rate, output='sos')
        data = signal.sosfilt(sos, data)
        
        return data
    
    def _process_audio_queue(self):
        """Processa fila de áudio em thread separada"""
        logger.info("🔄 Thread de processamento de áudio iniciada")
        
        while not self.should_stop.is_set():
            try:
                # Pega chunk da fila com timeout
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # Aplica melhorias no áudio
                enhanced_data = self._enhance_audio(audio_chunk.data)
                audio_chunk.data = enhanced_data
                
                # Chama callback se fornecido
                if self.callback and audio_chunk.is_speech:
                    try:
                        self.callback(audio_chunk)
                    except Exception as e:
                        logger.error(f"❌ Erro no callback: {e}")
                        
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Erro no processamento de áudio: {e}")
        
        logger.info("🔄 Thread de processamento de áudio finalizada")
    
    def start_recording(self, device_index: Optional[int] = None):
        """Inicia captura de áudio"""
        if self.is_recording:
            logger.warning("⚠️ Gravação já está ativa")
            return
            
        try:
            # Inicia thread de processamento
            self.should_stop.clear()
            self.processing_thread = threading.Thread(
                target=self._process_audio_queue, 
                daemon=True
            )
            self.processing_thread.start()
            
            # Inicia stream de áudio
            self.stream = sd.InputStream(
                device=device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=1024,  # Blocks pequenos para baixa latência
                dtype=np.float32
            )
            
            self.stream.start()
            self.is_recording = True
            
            console.print("🎤 [bold green]Captura de áudio iniciada![/bold green]")
            console.print(f"   Frequência: {self.sample_rate} Hz")
            console.print(f"   Canais: {self.channels}")
            console.print(f"   Chunks: {self.chunk_duration}s")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar captura: {e}")
            self.is_recording = False
            raise
    
    def stop_recording(self):
        """Para captura de áudio"""
        if not self.is_recording:
            return
            
        try:
            # Para stream de áudio
            self.stream.stop()
            self.stream.close()
            
            # Para thread de processamento
            self.should_stop.set()
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2)
            
            self.is_recording = False
            
            console.print("🎤 [bold red]Captura de áudio parada[/bold red]")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar captura: {e}")
    
    def save_audio_chunk(self, audio_chunk: AudioChunk, filename: str):
        """Salva chunk de áudio em arquivo"""
        Config.create_directories()
        filepath = Config.TEMP_DIR / filename
        
        try:
            sf.write(str(filepath), audio_chunk.data, self.sample_rate)
            logger.info(f"💾 Áudio salvo: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar áudio: {e}")
            return None
    
    def get_audio_stats(self) -> dict:
        """Retorna estatísticas do sistema de áudio"""
        return {
            "is_recording": self.is_recording,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_duration": self.chunk_duration,
            "queue_size": self.audio_queue.qsize(),
            "buffer_size": len(self.audio_buffer) if hasattr(self, 'audio_buffer') else 0
        }

class SpeechDetector:
    """Detector de fala mais avançado"""
    
    def __init__(self):
        self.is_speaking = False
        self.speech_start_time = None
        self.silence_start_time = None
        
        # Configurações
        self.min_speech_duration = 0.5
        self.max_silence_duration = 1.0
        self.amplitude_threshold = 0.01
        
    def analyze_chunk(self, audio_chunk: AudioChunk) -> dict:
        """Analisa chunk para detectar início/fim de fala"""
        current_time = audio_chunk.timestamp
        is_speech = audio_chunk.amplitude > self.amplitude_threshold
        
        result = {
            "is_speech": is_speech,
            "speech_start": False,
            "speech_end": False,
            "speech_duration": 0
        }
        
        if is_speech:
            if not self.is_speaking:
                # Início de fala
                self.is_speaking = True
                self.speech_start_time = current_time
                self.silence_start_time = None
                result["speech_start"] = True
                
        else:  # Silêncio
            if self.is_speaking:
                if self.silence_start_time is None:
                    self.silence_start_time = current_time
                elif current_time - self.silence_start_time > self.max_silence_duration:
                    # Fim de fala
                    self.is_speaking = False
                    if self.speech_start_time:
                        result["speech_duration"] = current_time - self.speech_start_time
                        result["speech_end"] = True
                    self.speech_start_time = None
                    self.silence_start_time = None
        
        return result

def test_audio_capture():
    """Função de teste para captura de áudio"""
    console.print("🧪 [bold cyan]Teste de Captura de Áudio[/bold cyan]")
    
    def audio_callback(chunk: AudioChunk):
        if chunk.is_speech:
            console.print(f"🎤 Fala detectada: {chunk.amplitude:.4f} | {chunk.timestamp:.2f}s")
    
    capture = AudioCapture(callback=audio_callback)
    
    # Lista dispositivos
    capture.list_audio_devices()
    
    try:
        # Inicia captura
        capture.start_recording()
        
        console.print("🎤 [bold yellow]Fale algo... (Ctrl+C para parar)[/bold yellow]")
        
        # Mantém rodando
        while True:
            time.sleep(1)
            stats = capture.get_audio_stats()
            console.print(f"📊 Queue: {stats['queue_size']} | Buffer: {stats['buffer_size']}")
            
    except KeyboardInterrupt:
        console.print("\n⏹️ Parando captura...")
    finally:
        capture.stop_recording()

if __name__ == "__main__":
    test_audio_capture()
