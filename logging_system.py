#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 SALES AGENT IA - SISTEMA DE LOGS ESTRUTURADO
==============================================
Sistema avançado de logging com categorização, análise e monitoramento
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import traceback
import sys

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.text import Text
from rich import box

console = Console()

class LogLevel(Enum):
    """Níveis de log"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Categorias de log"""
    SYSTEM = "SYSTEM"
    AUDIO = "AUDIO"
    SPEECH = "SPEECH"
    AI = "AI"
    UI = "UI"
    BACKUP = "BACKUP"
    CONFIG = "CONFIG"
    ERROR = "ERROR"
    PERFORMANCE = "PERFORMANCE"
    USER = "USER"

@dataclass
class LogEntry:
    """Entrada de log estruturada"""
    timestamp: str
    level: str
    category: str
    message: str
    module: str
    function: str
    line: int
    thread_id: str
    process_id: int
    extra_data: Dict[str, Any] = None
    traceback: str = None

@dataclass
class LogStats:
    """Estatísticas de logs"""
    total_entries: int
    entries_by_level: Dict[str, int]
    entries_by_category: Dict[str, int]
    entries_by_hour: Dict[str, int]
    error_rate: float
    avg_response_time: float
    peak_usage: Dict[str, Any]

class StructuredLogger:
    """Sistema de logging estruturado"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configuração
        self.config = self._load_logging_config()
        
        # Estatísticas em tempo real
        self.stats = LogStats(
            total_entries=0,
            entries_by_level={},
            entries_by_category={},
            entries_by_hour={},
            error_rate=0.0,
            avg_response_time=0.0,
            peak_usage={}
        )
        
        # Buffer de logs para análise
        self.log_buffer: List[LogEntry] = []
        self.buffer_lock = threading.Lock()
        self.max_buffer_size = 1000
        
        # Configura loguru
        self._setup_loguru()
        
        # Thread de análise
        self._analysis_thread = None
        self._stop_analysis = threading.Event()
        
        logger.info("Sistema de logs estruturado inicializado")
    
    def _load_logging_config(self) -> Dict:
        """Carrega configuração de logging"""
        config_file = self.logs_dir / "logging_config.json"
        
        default_config = {
            "level": "INFO",
            "max_file_size": "10MB",
            "retention_days": 30,
            "enable_console": True,
            "enable_file": True,
            "enable_analysis": True,
            "enable_performance_logging": True,
            "categories": {
                "SYSTEM": {"level": "INFO", "enabled": True},
                "AUDIO": {"level": "DEBUG", "enabled": True},
                "SPEECH": {"level": "INFO", "enabled": True},
                "AI": {"level": "DEBUG", "enabled": True},
                "UI": {"level": "INFO", "enabled": True},
                "BACKUP": {"level": "INFO", "enabled": True},
                "CONFIG": {"level": "DEBUG", "enabled": True},
                "ERROR": {"level": "ERROR", "enabled": True},
                "PERFORMANCE": {"level": "INFO", "enabled": True},
                "USER": {"level": "INFO", "enabled": True}
            },
            "formats": {
                "console": "{time:HH:mm:ss} | {level: <8} | {category: <12} | {message}",
                "file": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {category: <12} | {module}:{function}:{line} | {message}",
                "json": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {category} | {module}:{function}:{line} | {message} | {extra_data}"
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                console.print(f"[yellow]⚠️ Erro ao carregar config de logs: {e}[/yellow]")
                return default_config
        
        # Salva configuração padrão
        self._save_logging_config(default_config)
        return default_config
    
    def _save_logging_config(self, config: Dict):
        """Salva configuração de logging"""
        config_file = self.logs_dir / "logging_config.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]❌ Erro ao salvar config de logs: {e}[/red]")
    
    def _setup_loguru(self):
        """Configura loguru com handlers personalizados"""
        # Remove handlers padrão
        logger.remove()
        
        # Handler para console
        if self.config["enable_console"]:
            logger.add(
                sys.stderr,
                level=self.config["level"],
                format=self._get_console_format(),
                colorize=True,
                filter=self._console_filter
            )
        
        # Handler para arquivo principal
        if self.config["enable_file"]:
            logger.add(
                self.logs_dir / "sales_agent.log",
                level=self.config["level"],
                format=self._get_file_format(),
                rotation=self.config["max_file_size"],
                retention=f"{self.config['retention_days']} days",
                compression="zip",
                filter=self._file_filter
            )
        
        # Handler para erros
        logger.add(
            self.logs_dir / "errors.log",
            level="ERROR",
            format=self._get_file_format(),
            rotation="1 day",
            retention="90 days",
            compression="zip"
        )
        
        # Handler para performance
        if self.config["enable_performance_logging"]:
            logger.add(
                self.logs_dir / "performance.log",
                level="INFO",
                format=self._get_file_format(),
                rotation="1 day",
                retention="30 days",
                compression="zip",
                filter=lambda record: record["extra"].get("category") == "PERFORMANCE"
            )
        
        # Handler para JSON (análise)
        logger.add(
            self._json_log_handler,
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {category} | {module}:{function}:{line} | {message} | {extra_data}",
            filter=self._json_filter
        )
    
    def _get_console_format(self) -> str:
        """Formato para console"""
        return self.config["formats"]["console"]
    
    def _get_file_format(self) -> str:
        """Formato para arquivo"""
        return self.config["formats"]["file"]
    
    def _console_filter(self, record):
        """Filtro para console"""
        category = record["extra"].get("category", "SYSTEM")
        category_config = self.config["categories"].get(category, {})
        
        if not category_config.get("enabled", True):
            return False
        
        # Verifica nível
        level_num = logger.level(record["level"].name).no
        category_level_num = logger.level(category_config.get("level", "INFO")).no
        
        return level_num >= category_level_num
    
    def _file_filter(self, record):
        """Filtro para arquivo"""
        return True  # Logs tudo para arquivo
    
    def _json_filter(self, record):
        """Filtro para JSON"""
        return True  # Logs tudo para análise
    
    def _json_log_handler(self, message):
        """Handler personalizado para JSON"""
        try:
            # Extrai dados da mensagem
            parts = message.split(" | ")
            if len(parts) >= 6:
                timestamp = parts[0]
                level = parts[1]
                category = parts[2]
                location = parts[3]
                msg = parts[4]
                extra_data = parts[5] if len(parts) > 5 else "{}"
                
                # Cria entrada estruturada
                entry = LogEntry(
                    timestamp=timestamp,
                    level=level,
                    category=category,
                    message=msg,
                    module=location.split(":")[0] if ":" in location else "unknown",
                    function=location.split(":")[1] if ":" in location else "unknown",
                    line=int(location.split(":")[2]) if ":" in location and location.split(":")[2].isdigit() else 0,
                    thread_id=str(threading.get_ident()),
                    process_id=os.getpid(),
                    extra_data=json.loads(extra_data) if extra_data != "{}" else {}
                )
                
                # Adiciona ao buffer
                with self.buffer_lock:
                    self.log_buffer.append(entry)
                    if len(self.log_buffer) > self.max_buffer_size:
                        self.log_buffer.pop(0)
                
                # Atualiza estatísticas
                self._update_stats(entry)
                
        except Exception as e:
            # Não queremos que o handler de log cause erro
            pass
    
    def _update_stats(self, entry: LogEntry):
        """Atualiza estatísticas em tempo real"""
        self.stats.total_entries += 1
        
        # Por nível
        self.stats.entries_by_level[entry.level] = self.stats.entries_by_level.get(entry.level, 0) + 1
        
        # Por categoria
        self.stats.entries_by_category[entry.category] = self.stats.entries_by_category.get(entry.category, 0) + 1
        
        # Por hora
        hour = entry.timestamp.split(" ")[1].split(":")[0]
        self.stats.entries_by_hour[hour] = self.stats.entries_by_hour.get(hour, 0) + 1
        
        # Taxa de erro
        error_count = self.stats.entries_by_level.get("ERROR", 0) + self.stats.entries_by_level.get("CRITICAL", 0)
        self.stats.error_rate = (error_count / self.stats.total_entries) * 100 if self.stats.total_entries > 0 else 0
    
    def log(self, level: LogLevel, category: LogCategory, message: str, **kwargs):
        """Método principal de logging"""
        extra_data = {
            "category": category.value,
            **kwargs
        }
        
        # Adiciona traceback para erros
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            extra_data["traceback"] = traceback.format_exc()
        
        # Log com loguru
        logger.bind(**extra_data).log(level.value, message)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log específico para performance"""
        self.log(
            LogLevel.INFO,
            LogCategory.PERFORMANCE,
            f"Performance: {operation} took {duration:.3f}s",
            operation=operation,
            duration=duration,
            **kwargs
        )
    
    def log_user_action(self, action: str, **kwargs):
        """Log específico para ações do usuário"""
        self.log(
            LogLevel.INFO,
            LogCategory.USER,
            f"User action: {action}",
            action=action,
            **kwargs
        )
    
    def log_error(self, error: Exception, context: str = "", **kwargs):
        """Log específico para erros"""
        self.log(
            LogLevel.ERROR,
            LogCategory.ERROR,
            f"Error in {context}: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            **kwargs
        )
    
    def start_analysis(self):
        """Inicia análise de logs em background"""
        if self._analysis_thread and self._analysis_thread.is_alive():
            return
        
        self._stop_analysis.clear()
        self._analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self._analysis_thread.start()
        
        logger.info("Análise de logs iniciada")
    
    def stop_analysis(self):
        """Para análise de logs"""
        if self._analysis_thread:
            self._stop_analysis.set()
            self._analysis_thread.join(timeout=5)
            logger.info("Análise de logs parada")
    
    def _analysis_loop(self):
        """Loop de análise de logs"""
        while not self._stop_analysis.is_set():
            try:
                # Analisa logs recentes
                self._analyze_recent_logs()
                
                # Aguarda próxima análise
                self._stop_analysis.wait(60)  # A cada minuto
                
            except Exception as e:
                logger.error(f"Erro na análise de logs: {e}")
                self._stop_analysis.wait(60)
    
    def _analyze_recent_logs(self):
        """Analisa logs recentes para detectar padrões"""
        with self.buffer_lock:
            recent_logs = self.log_buffer[-100:]  # Últimos 100 logs
        
        # Detecta erros frequentes
        error_logs = [log for log in recent_logs if log.level in ["ERROR", "CRITICAL"]]
        if len(error_logs) > 10:  # Mais de 10 erros recentes
            logger.warning(f"Alto número de erros detectado: {len(error_logs)} nos últimos logs")
        
        # Detecta performance degradada
        perf_logs = [log for log in recent_logs if log.category == "PERFORMANCE"]
        if perf_logs:
            durations = [log.extra_data.get("duration", 0) for log in perf_logs if "duration" in log.extra_data]
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 5.0:  # Mais de 5 segundos em média
                    logger.warning(f"Performance degradada detectada: {avg_duration:.2f}s em média")
    
    def get_log_stats(self) -> LogStats:
        """Retorna estatísticas atuais"""
        return self.stats
    
    def search_logs(self, query: str, category: str = None, level: str = None, 
                   start_time: str = None, end_time: str = None) -> List[LogEntry]:
        """Busca logs com filtros"""
        results = []
        
        with self.buffer_lock:
            for entry in self.log_buffer:
                # Filtro por query
                if query and query.lower() not in entry.message.lower():
                    continue
                
                # Filtro por categoria
                if category and entry.category != category:
                    continue
                
                # Filtro por nível
                if level and entry.level != level:
                    continue
                
                # Filtro por tempo (implementação básica)
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                
                results.append(entry)
        
        return results
    
    def export_logs(self, filename: str = None, format: str = "json") -> str:
        """Exporta logs para arquivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_export_{timestamp}.{format}"
        
        export_path = self.logs_dir / filename
        
        with self.buffer_lock:
            logs_to_export = self.log_buffer.copy()
        
        if format == "json":
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(log) for log in logs_to_export], f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            import csv
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                if logs_to_export:
                    writer = csv.DictWriter(f, fieldnames=asdict(logs_to_export[0]).keys())
                    writer.writeheader()
                    for log in logs_to_export:
                        writer.writerow(asdict(log))
        
        logger.info(f"Logs exportados para: {export_path}")
        return str(export_path)
    
    def show_log_dashboard(self):
        """Mostra dashboard de logs"""
        stats = self.get_log_stats()
        
        # Tabela de estatísticas por nível
        level_table = Table(title="📊 Logs por Nível")
        level_table.add_column("Nível", style="cyan")
        level_table.add_column("Quantidade", style="green")
        level_table.add_column("Percentual", style="yellow")
        
        for level, count in stats.entries_by_level.items():
            percentage = (count / stats.total_entries) * 100 if stats.total_entries > 0 else 0
            level_table.add_row(level, str(count), f"{percentage:.1f}%")
        
        # Tabela de estatísticas por categoria
        category_table = Table(title="📊 Logs por Categoria")
        category_table.add_column("Categoria", style="cyan")
        category_table.add_column("Quantidade", style="green")
        category_table.add_column("Percentual", style="yellow")
        
        for category, count in stats.entries_by_category.items():
            percentage = (count / stats.total_entries) * 100 if stats.total_entries > 0 else 0
            category_table.add_row(category, str(count), f"{percentage:.1f}%")
        
        # Tabela de logs por hora
        hour_table = Table(title="📊 Logs por Hora")
        hour_table.add_column("Hora", style="cyan")
        hour_table.add_column("Quantidade", style="green")
        
        for hour in sorted(stats.entries_by_hour.keys()):
            count = stats.entries_by_hour[hour]
            hour_table.add_row(f"{hour}:00", str(count))
        
        console.print(level_table)
        console.print(category_table)
        console.print(hour_table)
        
        # Estatísticas gerais
        console.print(f"\n📈 [bold cyan]Estatísticas Gerais:[/cyan]")
        console.print(f"   Total de entradas: {stats.total_entries}")
        console.print(f"   Taxa de erro: {stats.error_rate:.2f}%")
        console.print(f"   Tempo médio de resposta: {stats.avg_response_time:.3f}s")
    
    def cleanup_old_logs(self):
        """Limpa logs antigos baseado na configuração"""
        retention_days = self.config.get("retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Remove arquivos de log antigos
        for log_file in self.logs_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                logger.info(f"Arquivo de log antigo removido: {log_file.name}")

# Instância global do logger
structured_logger = StructuredLogger()

def get_logger():
    """Retorna instância do logger estruturado"""
    return structured_logger

# Funções de conveniência
def log_info(category: LogCategory, message: str, **kwargs):
    """Log de informação"""
    structured_logger.log(LogLevel.INFO, category, message, **kwargs)

def log_error(category: LogCategory, message: str, error: Exception = None, **kwargs):
    """Log de erro"""
    if error:
        structured_logger.log_error(error, message, **kwargs)
    else:
        structured_logger.log(LogLevel.ERROR, category, message, **kwargs)

def log_warning(category: LogCategory, message: str, **kwargs):
    """Log de aviso"""
    structured_logger.log(LogLevel.WARNING, category, message, **kwargs)

def log_success(category: LogCategory, message: str, **kwargs):
    """Log de sucesso"""
    structured_logger.log(LogLevel.SUCCESS, category, message, **kwargs)

def log_performance(operation: str, duration: float, **kwargs):
    """Log de performance"""
    structured_logger.log_performance(operation, duration, **kwargs)

def log_user_action(action: str, **kwargs):
    """Log de ação do usuário"""
    structured_logger.log_user_action(action, **kwargs)

def main():
    """Função principal para gerenciar logs"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sales Agent IA - Sistema de Logs")
    parser.add_argument("--dashboard", action="store_true", help="Mostrar dashboard de logs")
    parser.add_argument("--search", help="Buscar logs")
    parser.add_argument("--export", help="Exportar logs")
    parser.add_argument("--cleanup", action="store_true", help="Limpar logs antigos")
    parser.add_argument("--start-analysis", action="store_true", help="Iniciar análise")
    parser.add_argument("--stop-analysis", action="store_true", help="Parar análise")
    
    args = parser.parse_args()
    
    logger_system = get_logger()
    
    if args.dashboard:
        logger_system.show_log_dashboard()
    elif args.search:
        results = logger_system.search_logs(args.search)
        for result in results[:10]:  # Mostra apenas os 10 primeiros
            console.print(f"[{result.timestamp}] {result.level} | {result.category} | {result.message}")
    elif args.export:
        filename = logger_system.export_logs(args.export)
        console.print(f"Logs exportados para: {filename}")
    elif args.cleanup:
        logger_system.cleanup_old_logs()
        console.print("✅ Logs antigos removidos")
    elif args.start_analysis:
        logger_system.start_analysis()
        console.print("✅ Análise de logs iniciada")
    elif args.stop_analysis:
        logger_system.stop_analysis()
        console.print("✅ Análise de logs parada")
    else:
        # Modo interativo
        console.print(Panel.fit(
            "[bold blue]📝 SISTEMA DE LOGS ESTRUTURADO[/bold blue]\n"
            "[cyan]Sistema avançado de logging do Sales Agent IA[/cyan]",
            border_style="blue"
        ))
        
        while True:
            console.print("\n[bold yellow]Opções:[/yellow]")
            console.print("1. Mostrar dashboard")
            console.print("2. Buscar logs")
            console.print("3. Exportar logs")
            console.print("4. Limpar logs antigos")
            console.print("5. Iniciar análise")
            console.print("6. Parar análise")
            console.print("7. Sair")
            
            choice = console.input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                logger_system.show_log_dashboard()
            elif choice == "2":
                query = console.input("Query de busca: ").strip()
                if query:
                    results = logger_system.search_logs(query)
                    for result in results[:10]:
                        console.print(f"[{result.timestamp}] {result.level} | {result.category} | {result.message}")
            elif choice == "3":
                format_type = console.input("Formato (json/csv): ").strip() or "json"
                filename = logger_system.export_logs(format=format_type)
                console.print(f"Logs exportados para: {filename}")
            elif choice == "4":
                logger_system.cleanup_old_logs()
                console.print("✅ Logs antigos removidos")
            elif choice == "5":
                logger_system.start_analysis()
                console.print("✅ Análise de logs iniciada")
            elif choice == "6":
                logger_system.stop_analysis()
                console.print("✅ Análise de logs parada")
            elif choice == "7":
                break
            else:
                console.print("❌ Opção inválida")

if __name__ == "__main__":
    main()
