#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SALES AGENT IA - SISTEMA AVANÇADO INTEGRADO
==============================================
Sistema principal com todas as melhorias implementadas
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Importa os novos sistemas
from setup_advanced import AdvancedSetup
from backup_manager import BackupManager
from logging_system import get_logger, LogCategory, log_info, log_error, log_success
from dependency_monitor import DependencyMonitor
from config_gui import ConfigGUI

console = Console()

class SalesAgentAdvanced:
    """Sistema principal integrado com todas as melhorias"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.is_running = False
        
        # Inicializa sistemas
        self.setup_system = None
        self.backup_manager = None
        self.logger = None
        self.dependency_monitor = None
        
        # Threads de monitoramento
        self._monitoring_threads = []
        
        console.print(Panel.fit(
            "[bold blue]🚀 SALES AGENT IA - SISTEMA AVANÇADO[/bold blue]\n"
            "[cyan]Sistema integrado com todas as melhorias implementadas[/cyan]",
            border_style="blue"
        ))
    
    def initialize_systems(self):
        """Inicializa todos os sistemas"""
        console.print("\n🔧 [bold yellow]Inicializando sistemas avançados...[/bold yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # 1. Sistema de Setup
                task = progress.add_task("Inicializando setup avançado...", total=None)
                self.setup_system = AdvancedSetup()
                progress.update(task, description="✅ Setup avançado OK")
                
                # 2. Sistema de Backup
                task = progress.add_task("Inicializando backup manager...", total=None)
                self.backup_manager = BackupManager(self.base_dir)
                progress.update(task, description="✅ Backup manager OK")
                
                # 3. Sistema de Logs
                task = progress.add_task("Inicializando sistema de logs...", total=None)
                self.logger = get_logger()
                progress.update(task, description="✅ Sistema de logs OK")
                
                # 4. Monitor de Dependências
                task = progress.add_task("Inicializando monitor de dependências...", total=None)
                self.dependency_monitor = DependencyMonitor(self.base_dir)
                progress.update(task, description="✅ Monitor de dependências OK")
                
                # 5. Inicia monitoramentos
                task = progress.add_task("Iniciando monitoramentos...", total=None)
                self._start_monitoring()
                progress.update(task, description="✅ Monitoramentos OK")
            
            log_success(LogCategory.SYSTEM, "Sistema avançado inicializado com sucesso")
            console.print("\n✅ [bold green]Todos os sistemas inicializados![/bold green]")
            
        except Exception as e:
            log_error(LogCategory.SYSTEM, f"Erro na inicialização: {e}")
            console.print(f"\n❌ [bold red]Erro na inicialização: {e}[/bold red]")
            raise
    
    def _start_monitoring(self):
        """Inicia sistemas de monitoramento"""
        # Backup automático
        if self.backup_manager:
            self.backup_manager.start_auto_backup()
        
        # Análise de logs
        if self.logger:
            self.logger.start_analysis()
        
        # Monitor de dependências
        if self.dependency_monitor:
            self.dependency_monitor.start_monitoring()
    
    def show_system_status(self):
        """Mostra status completo do sistema"""
        console.print("\n📊 [bold cyan]STATUS DO SISTEMA AVANÇADO[/bold cyan]")
        
        # Tabela de componentes
        table = Table(title="Componentes do Sistema")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Descrição", style="white")
        
        components = [
            ("Setup Avançado", "✅ Ativo", "Instalação e configuração automática"),
            ("Backup Manager", "✅ Ativo", "Backup automático de configurações"),
            ("Sistema de Logs", "✅ Ativo", "Logging estruturado e análise"),
            ("Monitor de Deps", "✅ Ativo", "Validação de dependências em tempo real"),
            ("Interface Gráfica", "✅ Disponível", "Configurações via GUI"),
            ("Sales Agent Core", "⏸️ Pausado", "Sistema principal de vendas")
        ]
        
        for component, status, description in components:
            table.add_row(component, status, description)
        
        console.print(table)
        
        # Estatísticas de logs
        if self.logger:
            stats = self.logger.get_log_stats()
            console.print(f"\n📈 [bold yellow]Estatísticas de Logs:[/yellow]")
            console.print(f"   Total de entradas: {stats.total_entries}")
            console.print(f"   Taxa de erro: {stats.error_rate:.2f}%")
        
        # Saúde das dependências
        if self.dependency_monitor:
            health = self.dependency_monitor.get_system_health()
            console.print(f"\n🔍 [bold yellow]Saúde das Dependências:[/yellow]")
            console.print(f"   Status geral: {health.overall_status}")
            console.print(f"   Críticas: {health.critical_deps_ok}/{health.critical_deps_total}")
            console.print(f"   Opcionais: {health.optional_deps_ok}/{health.optional_deps_total}")
    
    def run_interactive_menu(self):
        """Executa menu interativo"""
        while True:
            console.print("\n[bold yellow]MENU PRINCIPAL - SALES AGENT IA AVANÇADO[/yellow]")
            console.print("1. Verificar status do sistema")
            console.print("2. Executar setup completo")
            console.print("3. Gerenciar backups")
            console.print("4. Ver logs e estatísticas")
            console.print("5. Verificar dependências")
            console.print("6. Abrir interface gráfica")
            console.print("7. Executar Sales Agent original")
            console.print("8. Sair")
            
            choice = console.input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                self.show_system_status()
            elif choice == "2":
                self._run_complete_setup()
            elif choice == "3":
                self._manage_backups()
            elif choice == "4":
                self._manage_logs()
            elif choice == "5":
                self._manage_dependencies()
            elif choice == "6":
                self._open_gui()
            elif choice == "7":
                self._run_original_sales_agent()
            elif choice == "8":
                self._shutdown_systems()
                break
            else:
                console.print("❌ Opção inválida")
    
    def _run_complete_setup(self):
        """Executa setup completo"""
        console.print("\n🔧 [bold yellow]Executando setup completo...[/yellow]")
        
        try:
            self.setup_system.run_complete_setup()
            log_success(LogCategory.SYSTEM, "Setup completo executado com sucesso")
        except Exception as e:
            log_error(LogCategory.SYSTEM, f"Erro no setup: {e}")
            console.print(f"❌ Erro no setup: {e}")
    
    def _manage_backups(self):
        """Gerencia backups"""
        console.print("\n💾 [bold yellow]Gerenciador de Backups[/yellow]")
        console.print("1. Criar backup")
        console.print("2. Listar backups")
        console.print("3. Restaurar backup")
        console.print("4. Deletar backup")
        console.print("5. Voltar")
        
        choice = console.input("Escolha uma opção: ").strip()
        
        if choice == "1":
            name = console.input("Nome do backup (ou Enter para automático): ").strip()
            description = console.input("Descrição: ").strip()
            self.backup_manager.create_backup(name or None, description)
        elif choice == "2":
            self.backup_manager.show_backup_status()
        elif choice == "3":
            self.backup_manager.show_backup_status()
            name = console.input("Nome do backup para restaurar: ").strip()
            if name:
                self.backup_manager.restore_backup(name)
        elif choice == "4":
            self.backup_manager.show_backup_status()
            name = console.input("Nome do backup para deletar: ").strip()
            if name:
                self.backup_manager.delete_backup(name)
    
    def _manage_logs(self):
        """Gerencia logs"""
        console.print("\n📝 [bold yellow]Gerenciador de Logs[/yellow]")
        console.print("1. Ver dashboard")
        console.print("2. Buscar logs")
        console.print("3. Exportar logs")
        console.print("4. Limpar logs antigos")
        console.print("5. Voltar")
        
        choice = console.input("Escolha uma opção: ").strip()
        
        if choice == "1":
            self.logger.show_log_dashboard()
        elif choice == "2":
            query = console.input("Query de busca: ").strip()
            if query:
                results = self.logger.search_logs(query)
                for result in results[:10]:
                    console.print(f"[{result.timestamp}] {result.level} | {result.category} | {result.message}")
        elif choice == "3":
            format_type = console.input("Formato (json/csv): ").strip() or "json"
            filename = self.logger.export_logs(format=format_type)
            console.print(f"Logs exportados para: {filename}")
        elif choice == "4":
            self.logger.cleanup_old_logs()
            console.print("✅ Logs antigos removidos")
    
    def _manage_dependencies(self):
        """Gerencia dependências"""
        console.print("\n🔍 [bold yellow]Gerenciador de Dependências[/yellow]")
        console.print("1. Verificar todas")
        console.print("2. Verificar específica")
        console.print("3. Instalar dependência")
        console.print("4. Mostrar saúde do sistema")
        console.print("5. Voltar")
        
        choice = console.input("Escolha uma opção: ").strip()
        
        if choice == "1":
            self.dependency_monitor.show_dependency_status()
        elif choice == "2":
            dep_name = console.input("Nome da dependência: ").strip()
            if dep_name:
                result = self.dependency_monitor.check_dependency(dep_name)
                console.print(f"Status: {result.status.value}")
                if result.error_message:
                    console.print(f"Erro: {result.error_message}")
        elif choice == "3":
            dep_name = console.input("Nome da dependência: ").strip()
            if dep_name:
                self.dependency_monitor.install_dependency(dep_name)
        elif choice == "4":
            health = self.dependency_monitor.get_system_health()
            console.print(f"Status: {health.overall_status}")
            console.print(f"Críticas: {health.critical_deps_ok}/{health.critical_deps_total}")
            console.print(f"Opcionais: {health.optional_deps_ok}/{health.optional_deps_total}")
    
    def _open_gui(self):
        """Abre interface gráfica"""
        console.print("\n🖥️ [bold yellow]Abrindo interface gráfica...[/yellow]")
        
        try:
            gui = ConfigGUI()
            gui.run()
            log_success(LogCategory.UI, "Interface gráfica executada")
        except Exception as e:
            log_error(LogCategory.UI, f"Erro na interface gráfica: {e}")
            console.print(f"❌ Erro na interface gráfica: {e}")
    
    def _run_original_sales_agent(self):
        """Executa o Sales Agent original"""
        console.print("\n🎯 [bold yellow]Executando Sales Agent original...[/yellow]")
        
        try:
            # Importa e executa o sistema original
            from sales_agent_main import main as original_main
            original_main()
        except ImportError:
            console.print("❌ Sales Agent original não encontrado")
        except Exception as e:
            log_error(LogCategory.SYSTEM, f"Erro no Sales Agent original: {e}")
            console.print(f"❌ Erro: {e}")
    
    def _shutdown_systems(self):
        """Desliga todos os sistemas"""
        console.print("\n⏹️ [bold yellow]Desligando sistemas...[/yellow]")
        
        try:
            # Para monitoramentos
            if self.backup_manager:
                self.backup_manager.stop_auto_backup()
            
            if self.logger:
                self.logger.stop_analysis()
            
            if self.dependency_monitor:
                self.dependency_monitor.stop_monitoring()
            
            log_success(LogCategory.SYSTEM, "Sistemas desligados com sucesso")
            console.print("✅ Sistemas desligados")
            
        except Exception as e:
            log_error(LogCategory.SYSTEM, f"Erro ao desligar sistemas: {e}")
            console.print(f"❌ Erro ao desligar: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sales Agent IA - Sistema Avançado")
    parser.add_argument("--setup", action="store_true", help="Executar setup completo")
    parser.add_argument("--status", action="store_true", help="Mostrar status do sistema")
    parser.add_argument("--gui", action="store_true", help="Abrir interface gráfica")
    parser.add_argument("--original", action="store_true", help="Executar Sales Agent original")
    
    args = parser.parse_args()
    
    # Cria sistema avançado
    system = SalesAgentAdvanced()
    
    try:
        # Inicializa sistemas
        system.initialize_systems()
        
        if args.setup:
            system._run_complete_setup()
        elif args.status:
            system.show_system_status()
        elif args.gui:
            system._open_gui()
        elif args.original:
            system._run_original_sales_agent()
        else:
            # Menu interativo
            system.run_interactive_menu()
    
    except KeyboardInterrupt:
        console.print("\n⏹️ [bold yellow]Interrompido pelo usuário[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [bold red]Erro fatal: {e}[/bold red]")
    finally:
        system._shutdown_systems()

if __name__ == "__main__":
    main()
