"""
🎤 SALES AGENT IA - VERSÃO COM ÁUDIO
===================================
Sistema com captura de áudio em tempo real
"""

import os
import time
import threading
import queue
from pathlib import Path
from dotenv import load_dotenv

try:
    import openai
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.table import Table
    console = Console()
    AUDIO_AVAILABLE = True
except ImportError as e:
    console = None
    AUDIO_AVAILABLE = False
    print(f"❌ Dependências não disponíveis: {e}")

# Carrega configurações
load_dotenv()

class SimpleAudioCapture:
    """Capturador de áudio simplificado"""
    
    def __init__(self):
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Configurações
        self.sample_rate = 16000
        self.chunk_duration = 3  # segundos
        self.silence_threshold = 0.01
        
        # Estado
        self.conversation_history = []
        self.suggestions_count = 0
        
    def audio_callback(self, indata, frames, time, status):
        """Callback de áudio"""
        if status:
            print(f"Status: {status}")
        
        # Detecta se tem som
        amplitude = np.sqrt(np.mean(indata**2))
        
        if amplitude > self.silence_threshold:
            self.audio_queue.put(indata.copy())
    
    def process_audio(self):
        """Processa áudio capturado"""
        audio_chunks = []
        
        # Coleta chunks por alguns segundos
        timeout = time.time() + self.chunk_duration
        
        while time.time() < timeout:
            try:
                chunk = self.audio_queue.get_nowait()
                audio_chunks.append(chunk)
            except queue.Empty:
                time.sleep(0.1)
        
        if not audio_chunks:
            return None
        
        # Concatena áudio
        audio_data = np.concatenate(audio_chunks, axis=0)
        
        # Salva temporariamente
        temp_file = "temp_audio.wav"
        sf.write(temp_file, audio_data, self.sample_rate)
        
        try:
            # Transcreve com OpenAI
            with open(temp_file, "rb") as f:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="pt"
                )
            
            text = response.text.strip()
            
            # Remove arquivo temporário
            os.remove(temp_file)
            
            if len(text) > 10:  # Ignora transcrições muito curtas
                return text
            
        except Exception as e:
            console.print(f"[red]❌ Erro na transcrição: {e}[/red]")
            
        return None
    
    def generate_suggestion(self, client_text):
        """Gera sugestão baseada no texto"""
        # Carrega contexto do toolkit
        context = self.load_toolkit_context()
        
        # Histórico recente
        recent_history = "\n".join(self.conversation_history[-3:])
        
        prompt = f"""Você é meu consultor estratégico de vendas IA.

CONTEXTO DO TOOLKIT:
{context}

CONVERSA RECENTE:
{recent_history}

CLIENTE DISSE: "{client_text}"

Forneça uma sugestão estratégica IMEDIATA (máximo 2 frases):"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            suggestion = response.choices[0].message.content
            self.suggestions_count += 1
            
            return suggestion
            
        except Exception as e:
            return f"Erro ao gerar sugestão: {e}"
    
    def load_toolkit_context(self):
        """Carrega contexto do toolkit"""
        toolkit_dir = Path("AE_SENIOR_TOOLKIT")
        context_parts = []
        
        key_files = [
            "02_QUALIFICACAO_LEADS/MEDDIC_Framework_Avancado.txt",
            "06_NEGOCIACAO_FECHAMENTO/Tecnicas_Fechamento_Avancadas.txt"
        ]
        
        for file_path in key_files:
            full_path = toolkit_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:500]  # Primeiros 500 chars
                        context_parts.append(content)
                except:
                    pass
        
        return "\n\n".join(context_parts)
    
    def create_status_table(self):
        """Cria tabela de status"""
        table = Table(title="🎤 SALES AGENT IA - CAPTURA AO VIVO")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Detalhes", style="yellow")
        
        # Status de gravação
        recording_status = "🟢 GRAVANDO" if self.is_recording else "🔴 PARADO"
        table.add_row("Captura de Áudio", recording_status, f"Taxa: {self.sample_rate} Hz")
        
        # Fila de áudio
        queue_size = self.audio_queue.qsize()
        table.add_row("Fila de Áudio", f"📊 {queue_size} chunks", "")
        
        # Conversação
        conv_count = len(self.conversation_history)
        table.add_row("Conversação", f"💬 {conv_count} falas", "")
        
        # Sugestões
        table.add_row("Sugestões", f"💡 {self.suggestions_count} geradas", "")
        
        # Última atividade
        if self.conversation_history:
            last_text = self.conversation_history[-1][:40] + "..."
            table.add_row("Última Fala", "🗣️ Detectada", last_text)
        
        return table
    
    def start_recording(self):
        """Inicia gravação"""
        if not AUDIO_AVAILABLE:
            console.print("[red]❌ Dependências de áudio não disponíveis[/red]")
            return
        
        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=1024
            )
            
            self.stream.start()
            self.is_recording = True
            
            console.print("[green]🎤 Gravação iniciada![/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Erro ao iniciar gravação: {e}[/red]")
    
    def stop_recording(self):
        """Para gravação"""
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        self.is_recording = False
        console.print("[red]🛑 Gravação parada[/red]")
    
    def run_live_capture(self):
        """Executa captura ao vivo"""
        console.print(Panel.fit(
            "[bold blue]🎤 SALES AGENT IA - CAPTURA AO VIVO[/bold blue]\n"
            "[cyan]Sistema monitorando áudio em tempo real[/cyan]",
            border_style="blue"
        ))
        
        self.start_recording()
        
        try:
            with Live(self.create_status_table(), refresh_per_second=2, screen=True) as live:
                while self.is_recording:
                    # Processa áudio
                    transcription = self.process_audio()
                    
                    if transcription:
                        console.print(f"\n🗣️ [bold blue]DETECTADO:[/bold blue] {transcription}")
                        
                        # Adiciona ao histórico
                        self.conversation_history.append(transcription)
                        
                        # Gera sugestão
                        console.print("🤔 [yellow]Analisando...[/yellow]")
                        suggestion = self.generate_suggestion(transcription)
                        
                        console.print(f"💡 [bold green]SUGESTÃO:[/bold green] {suggestion}\n")
                    
                    # Atualiza dashboard
                    live.update(self.create_status_table())
                    
        except KeyboardInterrupt:
            console.print("\n⏹️ [bold yellow]Parando captura...[/bold yellow]")
        finally:
            self.stop_recording()

def list_audio_devices():
    """Lista dispositivos de áudio"""
    if not AUDIO_AVAILABLE:
        print("❌ Áudio não disponível")
        return
    
    console.print("[bold blue]🔊 Dispositivos de Áudio Disponíveis:[/bold blue]")
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        device_type = "🎤" if device['max_input_channels'] > 0 else "🔊"
        console.print(f"  {i}: {device_type} {device['name']}")

def test_audio_simple():
    """Teste simples de áudio"""
    if not AUDIO_AVAILABLE:
        console.print("[red]❌ Dependências de áudio não disponíveis[/red]")
        return
    
    console.print("[blue]🧪 Teste rápido de áudio...[/blue]")
    console.print("Fale algo agora (5 segundos):")
    
    # Grava por 5 segundos
    duration = 5
    sample_rate = 16000
    
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    
    # Salva e testa
    sf.write("test_audio.wav", audio, sample_rate)
    
    # Testa transcrição
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        with open("test_audio.wav", "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="pt"
            )
        
        text = response.text
        console.print(f"✅ [green]Transcrito:[/green] {text}")
        
        # Remove arquivo
        os.remove("test_audio.wav")
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Erro:[/red] {e}")
        return False

def main():
    """Função principal"""
    console.print(Panel.fit(
        "[bold blue]🎤 SALES AGENT IA - VERSÃO ÁUDIO[/bold blue]\n"
        "[cyan]Captura e análise de áudio em tempo real[/cyan]",
        border_style="blue"
    ))
    
    if not AUDIO_AVAILABLE:
        console.print("[red]❌ Instale dependências: pip install sounddevice soundfile[/red]")
        return
    
    # Menu de opções
    console.print("\n📋 [bold yellow]Opções disponíveis:[/bold yellow]")
    console.print("1. 🎤 Captura ao vivo (recomendado)")
    console.print("2. 🔊 Listar dispositivos de áudio")
    console.print("3. 🧪 Teste rápido de áudio")
    console.print("4. 💬 Simulador texto (versão anterior)")
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    if choice == "1":
        capture = SimpleAudioCapture()
        capture.run_live_capture()
        
    elif choice == "2":
        list_audio_devices()
        
    elif choice == "3":
        test_audio_simple()
        
    elif choice == "4":
        # Chama versão texto
        from sales_agent_simple import simulate_sales_conversation
        simulate_sales_conversation()
        
    else:
        console.print("❌ Opção inválida")

if __name__ == "__main__":
    main()

