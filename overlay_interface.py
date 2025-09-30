"""
🖥️ SALES AGENT IA - INTERFACE DE OVERLAY
======================================
Interface visual não intrusiva para exibir sugestões em tempo real
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import queue
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime

import pystray
from PIL import Image, ImageDraw
from rich.console import Console
from loguru import logger

from config import Config
from sales_intelligence import SalesSuggestion, SuggestionFormatter

console = Console()

@dataclass
class UIConfig:
    """Configurações da interface"""
    width: int = 400
    height: int = 150
    opacity: float = 0.9
    position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right
    auto_hide_delay: int = 10  # segundos
    animation_duration: int = 300  # ms

class SalesOverlay:
    """Overlay principal para exibir sugestões"""
    
    def __init__(self, ui_config: Optional[UIConfig] = None):
        self.ui_config = ui_config or UIConfig()
        self.suggestion_queue = queue.Queue()
        
        # Estado da interface
        self.is_visible = False
        self.current_suggestion = None
        self.auto_hide_timer = None
        
        # Janela principal
        self.root = None
        self.overlay_window = None
        
        # System tray
        self.tray_icon = None
        
        # Thread da interface
        self.ui_thread = None
        self.should_stop = threading.Event()
        
        logger.info("🖥️ Interface de overlay inicializada")
    
    def start_interface(self):
        """Inicia interface em thread separada"""
        if self.ui_thread and self.ui_thread.is_alive():
            logger.warning("⚠️ Interface já está ativa")
            return
            
        self.should_stop.clear()
        self.ui_thread = threading.Thread(target=self._run_interface, daemon=True)
        self.ui_thread.start()
        
        console.print("🖥️ [bold green]Interface iniciada![/bold green]")
    
    def stop_interface(self):
        """Para interface"""
        self.should_stop.set()
        
        if self.overlay_window:
            self.overlay_window.destroy()
        
        if self.tray_icon:
            self.tray_icon.stop()
            
        console.print("🖥️ [bold red]Interface parada[/bold red]")
    
    def show_suggestion(self, suggestion: SalesSuggestion):
        """Exibe nova sugestão"""
        try:
            self.suggestion_queue.put_nowait(suggestion)
        except queue.Full:
            logger.warning("⚠️ Fila de sugestões cheia")
    
    def _run_interface(self):
        """Thread principal da interface"""
        try:
            # Cria janela principal (invisível)
            self.root = tk.Tk()
            self.root.withdraw()  # Esconde janela principal
            
            # Configura system tray
            self._setup_system_tray()
            
            # Processa eventos
            self._process_interface_events()
            
        except Exception as e:
            logger.error(f"❌ Erro na interface: {e}")
        finally:
            if self.root:
                self.root.quit()
    
    def _setup_system_tray(self):
        """Configura ícone na system tray"""
        try:
            # Cria ícone simples
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.ellipse([16, 16, 48, 48], fill='white')
            
            # Menu do tray
            menu = pystray.Menu(
                pystray.MenuItem("Sales Agent IA", self._show_main_window),
                pystray.MenuItem("Mostrar Sugestão", self._show_test_suggestion),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Configurações", self._show_settings),
                pystray.MenuItem("Sair", self._quit_application)
            )
            
            self.tray_icon = pystray.Icon("sales_agent", image, "Sales Agent IA", menu)
            
            # Inicia tray em thread separada
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar system tray: {e}")
    
    def _process_interface_events(self):
        """Processa eventos da interface"""
        while not self.should_stop.is_set():
            try:
                # Processa sugestões na fila
                if not self.suggestion_queue.empty():
                    suggestion = self.suggestion_queue.get_nowait()
                    self._display_suggestion(suggestion)
                
                # Processa eventos do Tkinter
                if self.root:
                    self.root.update_idletasks()
                    self.root.update()
                
                time.sleep(0.1)  # Evita CPU alta
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Erro no loop da interface: {e}")
                break
    
    def _display_suggestion(self, suggestion: SalesSuggestion):
        """Exibe sugestão no overlay"""
        try:
            # Fecha overlay anterior se existir
            if self.overlay_window:
                self.overlay_window.destroy()
            
            # Cria nova janela de overlay
            self.overlay_window = tk.Toplevel(self.root)
            self._configure_overlay_window(self.overlay_window)
            
            # Adiciona conteúdo
            self._populate_overlay_content(self.overlay_window, suggestion)
            
            # Posiciona janela
            self._position_overlay_window(self.overlay_window)
            
            # Mostra janela
            self.overlay_window.deiconify()
            self.is_visible = True
            
            # Configura auto-hide
            self._setup_auto_hide()
            
            logger.info(f"💡 Sugestão exibida: {suggestion.suggestion_text[:30]}...")
            
        except Exception as e:
            logger.error(f"❌ Erro ao exibir sugestão: {e}")
    
    def _configure_overlay_window(self, window):
        """Configura propriedades da janela de overlay"""
        # Remove decorações
        window.overrideredirect(True)
        
        # Configura transparência
        window.attributes('-alpha', self.ui_config.opacity)
        
        # Sempre no topo
        window.attributes('-topmost', True)
        
        # Não aparece na barra de tarefas
        window.attributes('-toolwindow', True)
        
        # Configura tamanho
        window.geometry(f"{self.ui_config.width}x{self.ui_config.height}")
        
        # Cor de fundo
        window.configure(bg='#2d3748')
    
    def _populate_overlay_content(self, window, suggestion: SalesSuggestion):
        """Adiciona conteúdo à janela de overlay"""
        # Frame principal
        main_frame = tk.Frame(window, bg='#2d3748', padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Header com categoria e urgência
        header_frame = tk.Frame(main_frame, bg='#2d3748')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Emoji baseado na urgência
        urgency_emoji = "🔥" if suggestion.urgency >= 8 else "💡" if suggestion.urgency >= 6 else "💭"
        
        # Categoria
        category_text = self._format_category(suggestion.category)
        header_label = tk.Label(
            header_frame,
            text=f"{urgency_emoji} {category_text}",
            font=('Arial', 10, 'bold'),
            fg='#a0aec0',
            bg='#2d3748'
        )
        header_label.pack(side='left')
        
        # Timestamp
        timestamp = datetime.fromtimestamp(suggestion.timestamp).strftime('%H:%M:%S')
        time_label = tk.Label(
            header_frame,
            text=timestamp,
            font=('Arial', 8),
            fg='#718096',
            bg='#2d3748'
        )
        time_label.pack(side='right')
        
        # Texto principal da sugestão
        suggestion_text = SuggestionFormatter.format_for_overlay(suggestion)
        text_label = tk.Label(
            main_frame,
            text=suggestion_text,
            font=('Arial', 11),
            fg='#ffffff',
            bg='#2d3748',
            wraplength=self.ui_config.width - 30,
            justify='left'
        )
        text_label.pack(fill='x', pady=(0, 10))
        
        # Botões de ação
        button_frame = tk.Frame(main_frame, bg='#2d3748')
        button_frame.pack(fill='x')
        
        # Botão fechar
        close_btn = tk.Button(
            button_frame,
            text="✕",
            command=self._hide_overlay,
            font=('Arial', 10),
            fg='#718096',
            bg='#4a5568',
            border=0,
            padx=10
        )
        close_btn.pack(side='right')
        
        # Botão mais informações
        info_btn = tk.Button(
            button_frame,
            text="💬 Mais",
            command=lambda: self._show_detailed_info(suggestion),
            font=('Arial', 9),
            fg='#ffffff',
            bg='#3182ce',
            border=0,
            padx=15
        )
        info_btn.pack(side='left')
        
        # Bind para fechar ao clicar fora
        window.bind('<Button-1>', lambda e: self._hide_overlay())
    
    def _format_category(self, category: str) -> str:
        """Formata categoria para exibição"""
        category_map = {
            "objection_handling": "Tratamento de Objeção",
            "closing": "Fechamento",
            "discovery": "Discovery",
            "value_proposition": "Proposta de Valor",
            "general": "Sugestão Geral"
        }
        return category_map.get(category, category.title())
    
    def _position_overlay_window(self, window):
        """Posiciona janela de overlay na tela"""
        window.update_idletasks()
        
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        margin = 20
        
        if self.ui_config.position == "top-right":
            x = screen_width - self.ui_config.width - margin
            y = margin
        elif self.ui_config.position == "top-left":
            x = margin
            y = margin
        elif self.ui_config.position == "bottom-right":
            x = screen_width - self.ui_config.width - margin
            y = screen_height - self.ui_config.height - margin - 50  # Espaço para taskbar
        elif self.ui_config.position == "bottom-left":
            x = margin
            y = screen_height - self.ui_config.height - margin - 50
        else:
            x = (screen_width - self.ui_config.width) // 2
            y = (screen_height - self.ui_config.height) // 2
        
        window.geometry(f"{self.ui_config.width}x{self.ui_config.height}+{x}+{y}")
    
    def _setup_auto_hide(self):
        """Configura auto-hide do overlay"""
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
        
        self.auto_hide_timer = self.root.after(
            self.ui_config.auto_hide_delay * 1000,
            self._hide_overlay
        )
    
    def _hide_overlay(self):
        """Esconde overlay atual"""
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
        
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
            self.auto_hide_timer = None
        
        self.is_visible = False
    
    def _show_detailed_info(self, suggestion: SalesSuggestion):
        """Mostra informações detalhadas da sugestão"""
        detailed_text = SuggestionFormatter.format_detailed(suggestion)
        
        # Cria janela de detalhes
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Detalhes da Sugestão")
        detail_window.geometry("600x400")
        detail_window.configure(bg='#1a202c')
        
        # Texto detalhado
        text_widget = tk.Text(
            detail_window,
            font=('Consolas', 10),
            bg='#2d3748',
            fg='#ffffff',
            padx=20,
            pady=20,
            wrap='word'
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', detailed_text)
        text_widget.config(state='disabled')
        
        # Centraliza janela
        detail_window.transient(self.root)
        detail_window.grab_set()
    
    # Métodos do system tray
    def _show_main_window(self, icon, item):
        """Mostra janela principal (placeholder)"""
        if self.root:
            messagebox.showinfo("Sales Agent IA", "Sistema ativo e monitorando!")
    
    def _show_test_suggestion(self, icon, item):
        """Mostra sugestão de teste"""
        test_suggestion = SalesSuggestion(
            suggestion_text="Esta é uma sugestão de teste do sistema!",
            confidence=0.9,
            urgency=7,
            category="general",
            context_used=["test"],
            timestamp=time.time(),
            reasoning="Teste do sistema"
        )
        self.show_suggestion(test_suggestion)
    
    def _show_settings(self, icon, item):
        """Mostra janela de configurações"""
        self._create_settings_window()
    
    def _quit_application(self, icon, item):
        """Encerra aplicação"""
        self.stop_interface()
    
    def _create_settings_window(self):
        """Cria janela de configurações"""
        if not self.root:
            return
            
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações - Sales Agent IA")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#1a202c')
        
        # Notebook para abas
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba Interface
        interface_frame = ttk.Frame(notebook)
        notebook.add(interface_frame, text="Interface")
        
        # Configurações de posição
        pos_label = tk.Label(interface_frame, text="Posição do Overlay:", bg='#1a202c', fg='#ffffff')
        pos_label.pack(anchor='w', padx=10, pady=5)
        
        position_var = tk.StringVar(value=self.ui_config.position)
        positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        
        for pos in positions:
            rb = tk.Radiobutton(
                interface_frame,
                text=pos.replace('-', ' ').title(),
                variable=position_var,
                value=pos,
                bg='#1a202c',
                fg='#ffffff',
                selectcolor='#2d3748'
            )
            rb.pack(anchor='w', padx=20)
        
        # Botão salvar
        save_btn = tk.Button(
            interface_frame,
            text="Salvar Configurações",
            command=lambda: self._save_settings(position_var.get()),
            bg='#3182ce',
            fg='#ffffff',
            padx=20,
            pady=5
        )
        save_btn.pack(pady=20)
    
    def _save_settings(self, position: str):
        """Salva configurações"""
        self.ui_config.position = position
        messagebox.showinfo("Configurações", "Configurações salvas com sucesso!")

class NotificationManager:
    """Gerenciador de notificações do sistema"""
    
    @staticmethod
    def show_system_notification(title: str, message: str):
        """Mostra notificação do sistema"""
        try:
            # Para Windows
            import plyer
            plyer.notification.notify(
                title=title,
                message=message,
                app_name="Sales Agent IA",
                timeout=5
            )
        except ImportError:
            logger.warning("⚠️ Plyer não disponível para notificações")
        except Exception as e:
            logger.error(f"❌ Erro na notificação: {e}")

def test_overlay_interface():
    """Teste da interface de overlay"""
    console.print("🧪 [bold cyan]Teste da Interface de Overlay[/bold cyan]")
    
    # Cria interface
    overlay = SalesOverlay()
    
    try:
        # Inicia interface
        overlay.start_interface()
        
        console.print("🖥️ Interface iniciada - verifique o system tray")
        
        # Simula sugestões
        time.sleep(3)
        
        test_suggestions = [
            SalesSuggestion(
                suggestion_text="Cliente mencionou preço. Foque no valor e ROI em vez do custo.",
                confidence=0.9,
                urgency=8,
                category="objection_handling",
                context_used=["objection_handling"],
                timestamp=time.time(),
                reasoning="Objeção de preço detectada"
            ),
            SalesSuggestion(
                suggestion_text="Momento ideal para apresentar case de sucesso similar.",
                confidence=0.8,
                urgency=6,
                category="value_proposition",
                context_used=["case_studies"],
                timestamp=time.time(),
                reasoning="Cliente demonstrou interesse"
            )
        ]
        
        for i, suggestion in enumerate(test_suggestions, 1):
            console.print(f"📱 Mostrando sugestão {i}...")
            overlay.show_suggestion(suggestion)
            time.sleep(8)  # Espera para ver resultado
        
        console.print("✅ Teste concluído!")
        
    except KeyboardInterrupt:
        console.print("\n⏹️ Encerrando teste...")
    finally:
        overlay.stop_interface()

if __name__ == "__main__":
    test_overlay_interface()
