#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 SALES AGENT IA - MONITOR DE DEPENDÊNCIAS
==========================================
Sistema de validação e monitoramento de dependências em tempo real
"""

import os
import sys
import json
import time
import threading
import subprocess
import importlib
import pkg_resources
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

class DependencyStatus(Enum):
    """Status de dependência"""
    OK = "OK"
    MISSING = "MISSING"
    OUTDATED = "OUTDATED"
    ERROR = "ERROR"
    CHECKING = "CHECKING"

@dataclass
class DependencyInfo:
    """Informações de uma dependência"""
    name: str
    version_installed: Optional[str]
    version_required: str
    status: DependencyStatus
    last_checked: str
    error_message: Optional[str] = None
    is_critical: bool = True
    auto_update: bool = False
    update_available: bool = False
    latest_version: Optional[str] = None

@dataclass
class SystemHealth:
    """Saúde geral do sistema"""
    overall_status: str
    critical_deps_ok: int
    critical_deps_total: int
    optional_deps_ok: int
    optional_deps_total: int
    last_check: str
    issues_found: List[str]
    recommendations: List[str]

class DependencyMonitor:
    """Monitor de dependências em tempo real"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.config_dir = self.base_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Carrega configuração
        self.config = self._load_monitor_config()
        
        # Lista de dependências
        self.dependencies = self._get_dependency_list()
        
        # Cache de verificações
        self.dependency_cache: Dict[str, DependencyInfo] = {}
        self.cache_expiry = 300  # 5 minutos
        
        # Thread de monitoramento
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        
        # Callbacks para notificações
        self._status_callbacks: List[callable] = []
        
        console.print("🔍 Monitor de dependências inicializado")
    
    def _load_monitor_config(self) -> Dict:
        """Carrega configuração do monitor"""
        config_file = self.config_dir / "dependency_monitor_config.json"
        
        default_config = {
            "enabled": True,
            "check_interval": 300,  # 5 minutos
            "auto_update": False,
            "notify_on_issues": True,
            "check_pypi": True,
            "critical_dependencies": [
                "openai",
                "pandas",
                "numpy",
                "rich",
                "loguru",
                "sounddevice",
                "soundfile",
                "scipy",
                "sentence-transformers",
                "chromadb"
            ],
            "optional_dependencies": [
                "pystray",
                "PIL",
                "psutil",
                "plyer"
            ]
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                console.print(f"[yellow]⚠️ Erro ao carregar config do monitor: {e}[/yellow]")
                return default_config
        
        # Salva configuração padrão
        self._save_monitor_config(default_config)
        return default_config
    
    def _save_monitor_config(self, config: Dict):
        """Salva configuração do monitor"""
        config_file = self.config_dir / "dependency_monitor_config.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]❌ Erro ao salvar config do monitor: {e}[/red]")
    
    def _get_dependency_list(self) -> List[Dict]:
        """Lista todas as dependências do sistema"""
        return [
            {
                "name": "openai",
                "version": ">=1.0.0",
                "critical": True,
                "description": "API da OpenAI para IA",
                "test_import": "import openai"
            },
            {
                "name": "pandas",
                "version": ">=1.5.0",
                "critical": True,
                "description": "Análise de dados",
                "test_import": "import pandas"
            },
            {
                "name": "numpy",
                "version": ">=1.21.0",
                "critical": True,
                "description": "Computação numérica",
                "test_import": "import numpy"
            },
            {
                "name": "rich",
                "version": ">=13.0.0",
                "critical": True,
                "description": "Interface rica no terminal",
                "test_import": "import rich"
            },
            {
                "name": "loguru",
                "version": ">=0.7.0",
                "critical": True,
                "description": "Sistema de logs avançado",
                "test_import": "import loguru"
            },
            {
                "name": "sounddevice",
                "version": ">=0.4.0",
                "critical": True,
                "description": "Captura de áudio",
                "test_import": "import sounddevice"
            },
            {
                "name": "soundfile",
                "version": ">=0.12.0",
                "critical": True,
                "description": "Processamento de arquivos de áudio",
                "test_import": "import soundfile"
            },
            {
                "name": "scipy",
                "version": ">=1.9.0",
                "critical": True,
                "description": "Processamento científico",
                "test_import": "import scipy"
            },
            {
                "name": "sentence-transformers",
                "version": ">=2.2.0",
                "critical": True,
                "description": "Modelos de embeddings",
                "test_import": "import sentence_transformers"
            },
            {
                "name": "chromadb",
                "version": ">=0.4.0",
                "critical": True,
                "description": "Base de dados vetorial",
                "test_import": "import chromadb"
            },
            {
                "name": "pystray",
                "version": ">=0.19.0",
                "critical": False,
                "description": "System tray interface",
                "test_import": "import pystray"
            },
            {
                "name": "PIL",
                "version": ">=9.0.0",
                "critical": False,
                "description": "Processamento de imagens",
                "test_import": "import PIL"
            },
            {
                "name": "python-dotenv",
                "version": ">=1.0.0",
                "critical": True,
                "description": "Gerenciamento de variáveis de ambiente",
                "test_import": "import dotenv"
            },
            {
                "name": "requests",
                "version": ">=2.28.0",
                "critical": True,
                "description": "Requisições HTTP",
                "test_import": "import requests"
            },
            {
                "name": "tkinter",
                "version": "builtin",
                "critical": False,
                "description": "Interface gráfica (builtin)",
                "test_import": "import tkinter"
            }
        ]
    
    def check_dependency(self, dep_name: str, force_check: bool = False) -> DependencyInfo:
        """Verifica status de uma dependência específica"""
        # Verifica cache
        if not force_check and dep_name in self.dependency_cache:
            cached = self.dependency_cache[dep_name]
            cache_time = datetime.fromisoformat(cached.last_checked)
            if (datetime.now() - cache_time).seconds < self.cache_expiry:
                return cached
        
        # Busca informações da dependência
        dep_info = None
        for dep in self.dependencies:
            if dep["name"] == dep_name:
                dep_info = dep
                break
        
        if not dep_info:
            return DependencyInfo(
                name=dep_name,
                version_installed=None,
                version_required="unknown",
                status=DependencyStatus.ERROR,
                last_checked=datetime.now().isoformat(),
                error_message="Dependência não encontrada na lista",
                is_critical=False
            )
        
        # Verifica se está instalada
        try:
            if dep_info["version"] == "builtin":
                # Dependência builtin do Python
                exec(dep_info["test_import"])
                version_installed = "builtin"
                status = DependencyStatus.OK
                error_message = None
            else:
                # Dependência externa
                try:
                    exec(dep_info["test_import"])
                    # Tenta obter versão
                    try:
                        module = importlib.import_module(dep_info["name"])
                        version_installed = getattr(module, "__version__", "unknown")
                    except:
                        # Fallback para pkg_resources
                        try:
                            version_installed = pkg_resources.get_distribution(dep_info["name"]).version
                        except:
                            version_installed = "installed"
                    
                    # Verifica se versão atende requisito
                    if self._check_version_requirement(version_installed, dep_info["version"]):
                        status = DependencyStatus.OK
                    else:
                        status = DependencyStatus.OUTDATED
                    
                    error_message = None
                    
                except ImportError:
                    version_installed = None
                    status = DependencyStatus.MISSING
                    error_message = f"Módulo {dep_name} não encontrado"
        
        except Exception as e:
            version_installed = None
            status = DependencyStatus.ERROR
            error_message = str(e)
        
        # Verifica se há atualização disponível
        update_available = False
        latest_version = None
        
        if status == DependencyStatus.OK and self.config.get("check_pypi", True):
            try:
                latest_version = self._get_latest_version(dep_name)
                if latest_version and version_installed != "builtin":
                    update_available = self._is_newer_version(latest_version, version_installed)
            except:
                pass  # Falha silenciosa na verificação de atualização
        
        # Cria objeto DependencyInfo
        dependency_info = DependencyInfo(
            name=dep_name,
            version_installed=version_installed,
            version_required=dep_info["version"],
            status=status,
            last_checked=datetime.now().isoformat(),
            error_message=error_message,
            is_critical=dep_info["critical"],
            auto_update=self.config.get("auto_update", False),
            update_available=update_available,
            latest_version=latest_version
        )
        
        # Atualiza cache
        self.dependency_cache[dep_name] = dependency_info
        
        return dependency_info
    
    def _check_version_requirement(self, installed: str, required: str) -> bool:
        """Verifica se versão instalada atende requisito"""
        if installed == "builtin" or installed == "unknown":
            return True
        
        try:
            from packaging import version
            return version.parse(installed) >= version.parse(required.replace(">=", ""))
        except:
            # Fallback simples
            return True
    
    def _get_latest_version(self, package_name: str) -> Optional[str]:
        """Obtém versão mais recente do PyPI"""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data["info"]["version"]
        except:
            pass
        return None
    
    def _is_newer_version(self, latest: str, installed: str) -> bool:
        """Verifica se versão mais recente é mais nova"""
        try:
            from packaging import version
            return version.parse(latest) > version.parse(installed)
        except:
            return False
    
    def check_all_dependencies(self, force_check: bool = False) -> List[DependencyInfo]:
        """Verifica todas as dependências"""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            total_deps = len(self.dependencies)
            task = progress.add_task("Verificando dependências...", total=total_deps)
            
            for dep in self.dependencies:
                progress.update(task, description=f"Verificando {dep['name']}...")
                
                result = self.check_dependency(dep["name"], force_check)
                results.append(result)
                
                progress.advance(task)
        
        return results
    
    def get_system_health(self) -> SystemHealth:
        """Retorna saúde geral do sistema"""
        dependencies = self.check_all_dependencies()
        
        critical_deps = [d for d in dependencies if d.is_critical]
        optional_deps = [d for d in dependencies if not d.is_critical]
        
        critical_ok = sum(1 for d in critical_deps if d.status == DependencyStatus.OK)
        optional_ok = sum(1 for d in optional_deps if d.status == DependencyStatus.OK)
        
        issues = []
        recommendations = []
        
        # Analisa problemas
        for dep in dependencies:
            if dep.status == DependencyStatus.MISSING:
                if dep.is_critical:
                    issues.append(f"Dependência crítica ausente: {dep.name}")
                    recommendations.append(f"Instale: pip install {dep.name}{dep.version_required}")
                else:
                    issues.append(f"Dependência opcional ausente: {dep.name}")
            
            elif dep.status == DependencyStatus.OUTDATED:
                issues.append(f"Dependência desatualizada: {dep.name} ({dep.version_installed} < {dep.version_required})")
                recommendations.append(f"Atualize: pip install --upgrade {dep.name}")
            
            elif dep.status == DependencyStatus.ERROR:
                issues.append(f"Erro na dependência {dep.name}: {dep.error_message}")
                recommendations.append(f"Reinstale: pip uninstall {dep.name} && pip install {dep.name}")
            
            elif dep.update_available:
                recommendations.append(f"Atualização disponível para {dep.name}: {dep.latest_version}")
        
        # Determina status geral
        if critical_ok == len(critical_deps):
            overall_status = "HEALTHY"
        elif critical_ok >= len(critical_deps) * 0.8:
            overall_status = "WARNING"
        else:
            overall_status = "CRITICAL"
        
        return SystemHealth(
            overall_status=overall_status,
            critical_deps_ok=critical_ok,
            critical_deps_total=len(critical_deps),
            optional_deps_ok=optional_ok,
            optional_deps_total=len(optional_deps),
            last_check=datetime.now().isoformat(),
            issues_found=issues,
            recommendations=recommendations
        )
    
    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if not self.config.get("enabled", True):
            return
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        
        console.print("🔍 Monitoramento de dependências iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        if self._monitor_thread:
            self._stop_monitoring.set()
            self._monitor_thread.join(timeout=5)
            console.print("🔍 Monitoramento de dependências parado")
    
    def _monitoring_loop(self):
        """Loop de monitoramento"""
        while not self._stop_monitoring.is_set():
            try:
                # Verifica saúde do sistema
                health = self.get_system_health()
                
                # Notifica se há problemas
                if self.config.get("notify_on_issues", True) and health.issues_found:
                    self._notify_issues(health)
                
                # Aguarda próxima verificação
                interval = self.config.get("check_interval", 300)
                self._stop_monitoring.wait(interval)
                
            except Exception as e:
                console.print(f"[red]❌ Erro no monitoramento: {e}[/red]")
                self._stop_monitoring.wait(60)  # Aguarda 1 minuto em caso de erro
    
    def _notify_issues(self, health: SystemHealth):
        """Notifica sobre problemas encontrados"""
        console.print(f"\n⚠️ [bold yellow]Problemas detectados no sistema:[/bold yellow]")
        
        for issue in health.issues_found:
            console.print(f"   • {issue}")
        
        for recommendation in health.recommendations:
            console.print(f"   💡 {recommendation}")
    
    def add_status_callback(self, callback: callable):
        """Adiciona callback para notificações de status"""
        self._status_callbacks.append(callback)
    
    def install_dependency(self, dep_name: str, version: str = None) -> bool:
        """Instala ou atualiza uma dependência"""
        try:
            if version:
                cmd = f"pip install {dep_name}=={version}"
            else:
                cmd = f"pip install {dep_name}"
            
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Limpa cache para forçar nova verificação
                if dep_name in self.dependency_cache:
                    del self.dependency_cache[dep_name]
                
                console.print(f"✅ {dep_name} instalado com sucesso")
                return True
            else:
                console.print(f"❌ Erro ao instalar {dep_name}: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Erro ao instalar {dep_name}: {e}")
            return False
    
    def show_dependency_status(self):
        """Mostra status de todas as dependências"""
        dependencies = self.check_all_dependencies()
        
        # Tabela de dependências críticas
        critical_table = Table(title="🔴 Dependências Críticas")
        critical_table.add_column("Nome", style="cyan")
        critical_table.add_column("Instalada", style="green")
        critical_table.add_column("Requerida", style="yellow")
        critical_table.add_column("Status", style="magenta")
        critical_table.add_column("Atualização", style="blue")
        
        # Tabela de dependências opcionais
        optional_table = Table(title="🟡 Dependências Opcionais")
        optional_table.add_column("Nome", style="cyan")
        optional_table.add_column("Instalada", style="green")
        optional_table.add_column("Requerida", style="yellow")
        optional_table.add_column("Status", style="magenta")
        optional_table.add_column("Atualização", style="blue")
        
        for dep in dependencies:
            status_emoji = {
                DependencyStatus.OK: "✅",
                DependencyStatus.MISSING: "❌",
                DependencyStatus.OUTDATED: "⚠️",
                DependencyStatus.ERROR: "💥",
                DependencyStatus.CHECKING: "🔄"
            }.get(dep.status, "❓")
            
            update_info = ""
            if dep.update_available and dep.latest_version:
                update_info = f"→ {dep.latest_version}"
            
            row_data = [
                dep.name,
                dep.version_installed or "N/A",
                dep.version_required,
                f"{status_emoji} {dep.status.value}",
                update_info
            ]
            
            if dep.is_critical:
                critical_table.add_row(*row_data)
            else:
                optional_table.add_row(*row_data)
        
        console.print(critical_table)
        console.print(optional_table)
        
        # Mostra saúde geral
        health = self.get_system_health()
        
        health_color = {
            "HEALTHY": "green",
            "WARNING": "yellow", 
            "CRITICAL": "red"
        }.get(health.overall_status, "white")
        
        console.print(f"\n📊 [bold {health_color}]Status Geral: {health.overall_status}[/bold {health_color}]")
        console.print(f"   Dependências críticas: {health.critical_deps_ok}/{health.critical_deps_total}")
        console.print(f"   Dependências opcionais: {health.optional_deps_ok}/{health.optional_deps_total}")
        
        if health.issues_found:
            console.print(f"\n⚠️ [bold yellow]Problemas encontrados:[/bold yellow]")
            for issue in health.issues_found:
                console.print(f"   • {issue}")
        
        if health.recommendations:
            console.print(f"\n💡 [bold cyan]Recomendações:[/bold cyan]")
            for rec in health.recommendations:
                console.print(f"   • {rec}")

def main():
    """Função principal para gerenciar dependências"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sales Agent IA - Monitor de Dependências")
    parser.add_argument("--check", action="store_true", help="Verificar todas as dependências")
    parser.add_argument("--check-one", help="Verificar dependência específica")
    parser.add_argument("--install", help="Instalar dependência")
    parser.add_argument("--health", action="store_true", help="Mostrar saúde do sistema")
    parser.add_argument("--start-monitor", action="store_true", help="Iniciar monitoramento")
    parser.add_argument("--stop-monitor", action="store_true", help="Parar monitoramento")
    
    args = parser.parse_args()
    
    monitor = DependencyMonitor()
    
    if args.check:
        monitor.show_dependency_status()
    elif args.check_one:
        result = monitor.check_dependency(args.check_one)
        console.print(f"Status de {args.check_one}: {result.status.value}")
        if result.error_message:
            console.print(f"Erro: {result.error_message}")
    elif args.install:
        monitor.install_dependency(args.install)
    elif args.health:
        health = monitor.get_system_health()
        console.print(f"Status: {health.overall_status}")
        console.print(f"Críticas: {health.critical_deps_ok}/{health.critical_deps_total}")
        console.print(f"Opcionais: {health.optional_deps_ok}/{health.optional_deps_total}")
    elif args.start_monitor:
        monitor.start_monitoring()
    elif args.stop_monitor:
        monitor.stop_monitoring()
    else:
        # Modo interativo
        console.print(Panel.fit(
            "[bold blue]🔍 MONITOR DE DEPENDÊNCIAS[/bold blue]\n"
            "[cyan]Sistema de validação e monitoramento em tempo real[/cyan]",
            border_style="blue"
        ))
        
        while True:
            console.print("\n[bold yellow]Opções:[/yellow]")
            console.print("1. Verificar todas as dependências")
            console.print("2. Verificar dependência específica")
            console.print("3. Instalar dependência")
            console.print("4. Mostrar saúde do sistema")
            console.print("5. Iniciar monitoramento")
            console.print("6. Parar monitoramento")
            console.print("7. Sair")
            
            choice = console.input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                monitor.show_dependency_status()
            elif choice == "2":
                dep_name = console.input("Nome da dependência: ").strip()
                if dep_name:
                    result = monitor.check_dependency(dep_name)
                    console.print(f"Status: {result.status.value}")
                    if result.error_message:
                        console.print(f"Erro: {result.error_message}")
            elif choice == "3":
                dep_name = console.input("Nome da dependência: ").strip()
                if dep_name:
                    monitor.install_dependency(dep_name)
            elif choice == "4":
                health = monitor.get_system_health()
                console.print(f"Status: {health.overall_status}")
                console.print(f"Críticas: {health.critical_deps_ok}/{health.critical_deps_total}")
                console.print(f"Opcionais: {health.optional_deps_ok}/{health.optional_deps_total}")
            elif choice == "5":
                monitor.start_monitoring()
            elif choice == "6":
                monitor.stop_monitoring()
            elif choice == "7":
                break
            else:
                console.print("❌ Opção inválida")

if __name__ == "__main__":
    main()
