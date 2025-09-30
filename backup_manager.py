#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 SALES AGENT IA - GERENCIADOR DE BACKUP
========================================
Sistema automático de backup e restauração de configurações
"""

import os
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from loguru import logger

console = Console()

@dataclass
class BackupInfo:
    """Informações de um backup"""
    name: str
    timestamp: str
    size: int
    files_count: int
    description: str
    version: str
    checksum: str
    auto_backup: bool = False

@dataclass
class BackupConfig:
    """Configuração do sistema de backup"""
    enabled: bool = True
    auto_backup_interval: int = 24  # horas
    max_backups: int = 10
    backup_on_startup: bool = True
    backup_on_config_change: bool = True
    compress_backups: bool = True
    include_logs: bool = False
    include_temp: bool = False

class BackupManager:
    """Gerenciador de backup automático"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.backup_dir = self.base_dir / "backups"
        self.config_dir = self.base_dir / "config"
        self.backup_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        # Carrega configuração
        self.config = self._load_backup_config()
        
        # Thread de backup automático
        self._backup_thread = None
        self._stop_backup_thread = threading.Event()
        
        # Arquivos e diretórios para backup
        self.backup_items = self._get_backup_items()
        
        logger.info("💾 Gerenciador de backup inicializado", extra={"category": "BACKUP"})
    
    def _load_backup_config(self) -> BackupConfig:
        """Carrega configuração de backup"""
        config_file = self.config_dir / "backup_config.json"
        
        default_config = BackupConfig()
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return BackupConfig(**data)
            except Exception as e:
                logger.error(f"Erro ao carregar config de backup: {e}")
                return default_config
        
        # Salva configuração padrão
        self._save_backup_config(default_config)
        return default_config
    
    def _save_backup_config(self, config: BackupConfig):
        """Salva configuração de backup"""
        config_file = self.config_dir / "backup_config.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar config de backup: {e}")
    
    def _get_backup_items(self) -> List[Dict]:
        """Lista itens para backup"""
        return [
            {
                "path": ".env",
                "description": "Variáveis de ambiente",
                "critical": True
            },
            {
                "path": "config.py",
                "description": "Configurações principais",
                "critical": True
            },
            {
                "path": "config/",
                "description": "Diretório de configurações",
                "critical": True,
                "recursive": True
            },
            {
                "path": "AE_SENIOR_TOOLKIT/",
                "description": "Base de conhecimento",
                "critical": True,
                "recursive": True
            },
            {
                "path": "embeddings/",
                "description": "Base de embeddings",
                "critical": False,
                "recursive": True
            },
            {
                "path": "logs/",
                "description": "Logs do sistema",
                "critical": False,
                "recursive": True,
                "include": self.config.include_logs
            },
            {
                "path": "temp/",
                "description": "Arquivos temporários",
                "critical": False,
                "recursive": True,
                "include": self.config.include_temp
            }
        ]
    
    def create_backup(self, name: str = None, description: str = "", auto: bool = False) -> BackupInfo:
        """Cria um novo backup"""
        if not self.config.enabled:
            logger.info("Backup desabilitado")
            return None
        
        # Gera nome do backup
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"backup_{timestamp}"
        
        backup_path = self.backup_dir / name
        
        console.print(f"💾 [bold yellow]Criando backup: {name}[/bold yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task("Preparando backup...", total=None)
                
                # Cria diretório do backup
                backup_path.mkdir(exist_ok=True)
                
                files_copied = 0
                total_size = 0
                
                # Copia arquivos
                for item in self.backup_items:
                    if not item.get("include", True):
                        continue
                    
                    source_path = self.base_dir / item["path"]
                    if not source_path.exists():
                        continue
                    
                    progress.update(task, description=f"Copiando {item['description']}...")
                    
                    if source_path.is_file():
                        # Arquivo único
                        dest_path = backup_path / item["path"]
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        shutil.copy2(source_path, dest_path)
                        files_copied += 1
                        total_size += source_path.stat().st_size
                        
                    elif source_path.is_dir() and item.get("recursive", False):
                        # Diretório recursivo
                        dest_path = backup_path / item["path"]
                        
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                src_file = Path(root) / file
                                rel_path = src_file.relative_to(source_path)
                                dst_file = dest_path / rel_path
                                dst_file.parent.mkdir(parents=True, exist_ok=True)
                                
                                shutil.copy2(src_file, dst_file)
                                files_copied += 1
                                total_size += src_file.stat().st_size
                
                # Cria arquivo de metadados
                metadata = {
                    "name": name,
                    "timestamp": datetime.now().isoformat(),
                    "description": description,
                    "version": "1.0.0",
                    "files_count": files_copied,
                    "size": total_size,
                    "auto_backup": auto,
                    "config": asdict(self.config)
                }
                
                metadata_file = backup_path / "backup_info.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Calcula checksum
                checksum = self._calculate_checksum(backup_path)
                
                # Cria objeto BackupInfo
                backup_info = BackupInfo(
                    name=name,
                    timestamp=metadata["timestamp"],
                    size=total_size,
                    files_count=files_copied,
                    description=description,
                    version="1.0.0",
                    checksum=checksum,
                    auto_backup=auto
                )
                
                # Atualiza metadados com checksum
                metadata["checksum"] = checksum
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Compressa se configurado
                if self.config.compress_backups:
                    progress.update(task, description="Comprimindo backup...")
                    self._compress_backup(backup_path)
                
                progress.update(task, description="✅ Backup concluído!")
            
            logger.info(f"Backup criado: {name} ({files_copied} arquivos, {total_size // 1024}KB)", extra={"category": "BACKUP"})
            return backup_info
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}", extra={"category": "BACKUP"})
            # Limpa backup parcial
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise
    
    def _calculate_checksum(self, backup_path: Path) -> str:
        """Calcula checksum do backup"""
        hasher = hashlib.md5()
        
        for file_path in sorted(backup_path.rglob("*")):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _compress_backup(self, backup_path: Path):
        """Comprime backup em arquivo ZIP"""
        zip_path = backup_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        # Remove diretório original
        shutil.rmtree(backup_path)
        
        # Renomeia ZIP para nome original
        zip_path.rename(backup_path)
    
    def list_backups(self) -> List[BackupInfo]:
        """Lista todos os backups disponíveis"""
        backups = []
        
        for backup_path in self.backup_dir.iterdir():
            if backup_path.is_dir():
                # Backup não comprimido
                info_file = backup_path / "backup_info.json"
            elif backup_path.suffix == '.zip':
                # Backup comprimido
                info_file = backup_path.with_suffix('') / "backup_info.json"
            else:
                continue
            
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Remove campos não suportados pelo BackupInfo
                        data_clean = {k: v for k, v in data.items() if k in ['name', 'timestamp', 'size', 'files_count', 'description', 'version', 'checksum', 'auto_backup']}
                        backup_info = BackupInfo(**data_clean)
                        backups.append(backup_info)
                except Exception as e:
                    logger.warning(f"Erro ao ler backup {backup_path}: {e}")
        
        # Ordena por timestamp
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str, confirm: bool = False) -> bool:
        """Restaura um backup"""
        if not confirm:
            if not console.input(f"⚠️ Restaurar backup '{backup_name}'? Isso sobrescreverá arquivos atuais. (y/N): ").lower().startswith('y'):
                console.print("❌ Restauração cancelada")
                return False
        
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            console.print(f"❌ Backup '{backup_name}' não encontrado")
            return False
        
        console.print(f"🔄 [bold yellow]Restaurando backup: {backup_name}[/bold yellow]")
        
        try:
            # Verifica se é comprimido
            if backup_path.suffix == '.zip':
                # Extrai ZIP temporariamente
                temp_path = backup_path.with_suffix('')
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(temp_path)
                restore_path = temp_path
            else:
                restore_path = backup_path
            
            # Restaura arquivos
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task("Restaurando arquivos...", total=None)
                
                for item in self.backup_items:
                    if not item.get("include", True):
                        continue
                    
                    source_path = restore_path / item["path"]
                    if not source_path.exists():
                        continue
                    
                    progress.update(task, description=f"Restaurando {item['description']}...")
                    
                    dest_path = self.base_dir / item["path"]
                    
                    if source_path.is_file():
                        # Arquivo único
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        
                    elif source_path.is_dir():
                        # Diretório
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                
                progress.update(task, description="✅ Restauração concluída!")
            
            # Limpa arquivos temporários
            if backup_path.suffix == '.zip' and restore_path.exists():
                shutil.rmtree(restore_path)
            
            logger.info(f"Backup restaurado: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            console.print(f"❌ Erro na restauração: {e}")
            return False
    
    def delete_backup(self, backup_name: str, confirm: bool = False) -> bool:
        """Remove um backup"""
        if not confirm:
            if not console.input(f"⚠️ Deletar backup '{backup_name}'? (y/N): ").lower().startswith('y'):
                console.print("❌ Exclusão cancelada")
                return False
        
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            console.print(f"❌ Backup '{backup_name}' não encontrado")
            return False
        
        try:
            if backup_path.is_dir():
                shutil.rmtree(backup_path)
            else:
                backup_path.unlink()
            
            logger.info(f"Backup deletado: {backup_name}")
            console.print(f"✅ Backup '{backup_name}' deletado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar backup: {e}")
            console.print(f"❌ Erro ao deletar: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups antigos baseado na configuração"""
        if not self.config.enabled:
            return
        
        backups = self.list_backups()
        
        # Remove backups automáticos antigos
        auto_backups = [b for b in backups if b.auto_backup]
        if len(auto_backups) > self.config.max_backups:
            to_remove = auto_backups[self.config.max_backups:]
            for backup in to_remove:
                self.delete_backup(backup.name, confirm=True)
        
        logger.info(f"Limpeza de backups: {len(to_remove) if 'to_remove' in locals() else 0} removidos")
    
    def start_auto_backup(self):
        """Inicia backup automático em thread separada"""
        if not self.config.enabled or not self.config.auto_backup_interval:
            return
        
        if self._backup_thread and self._backup_thread.is_alive():
            logger.warning("Thread de backup automático já está ativa")
            return
        
        self._stop_backup_thread.clear()
        self._backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
        self._backup_thread.start()
        
        logger.info(f"Backup automático iniciado (intervalo: {self.config.auto_backup_interval}h)")
    
    def stop_auto_backup(self):
        """Para backup automático"""
        if self._backup_thread:
            self._stop_backup_thread.set()
            self._backup_thread.join(timeout=5)
            logger.info("Backup automático parado")
    
    def _auto_backup_loop(self):
        """Loop de backup automático"""
        while not self._stop_backup_thread.is_set():
            try:
                # Cria backup automático
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"auto_backup_{timestamp}"
                description = f"Backup automático - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                
                self.create_backup(name, description, auto=True)
                
                # Limpa backups antigos
                self.cleanup_old_backups()
                
                # Aguarda próximo backup
                self._stop_backup_thread.wait(self.config.auto_backup_interval * 3600)
                
            except Exception as e:
                logger.error(f"Erro no backup automático: {e}")
                # Aguarda 1 hora antes de tentar novamente
                self._stop_backup_thread.wait(3600)
    
    def show_backup_status(self):
        """Mostra status dos backups"""
        backups = self.list_backups()
        
        table = Table(title="💾 Status dos Backups")
        table.add_column("Nome", style="cyan")
        table.add_column("Data", style="green")
        table.add_column("Tamanho", style="yellow")
        table.add_column("Arquivos", style="blue")
        table.add_column("Tipo", style="magenta")
        table.add_column("Descrição", style="white")
        
        for backup in backups:
            size_mb = backup.size // (1024 * 1024)
            date_str = datetime.fromisoformat(backup.timestamp).strftime("%d/%m/%Y %H:%M")
            backup_type = "🤖 Auto" if backup.auto_backup else "👤 Manual"
            
            table.add_row(
                backup.name,
                date_str,
                f"{size_mb}MB",
                str(backup.files_count),
                backup_type,
                backup.description[:30] + "..." if len(backup.description) > 30 else backup.description
            )
        
        console.print(table)
        
        # Estatísticas
        total_size = sum(b.size for b in backups)
        auto_count = sum(1 for b in backups if b.auto_backup)
        manual_count = len(backups) - auto_count
        
        console.print(f"\n📊 [bold cyan]Estatísticas:[/bold cyan]")
        console.print(f"   Total de backups: {len(backups)}")
        console.print(f"   Backups automáticos: {auto_count}")
        console.print(f"   Backups manuais: {manual_count}")
        console.print(f"   Espaço total: {total_size // (1024 * 1024)}MB")
    
    def update_config(self, **kwargs):
        """Atualiza configuração de backup"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self._save_backup_config(self.config)
        
        # Reinicia backup automático se necessário
        if 'auto_backup_interval' in kwargs or 'enabled' in kwargs:
            self.stop_auto_backup()
            if self.config.enabled and self.config.auto_backup_interval:
                self.start_auto_backup()

def main():
    """Função principal para gerenciar backups"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sales Agent IA - Gerenciador de Backup")
    parser.add_argument("--create", help="Criar backup com nome específico")
    parser.add_argument("--restore", help="Restaurar backup")
    parser.add_argument("--delete", help="Deletar backup")
    parser.add_argument("--list", action="store_true", help="Listar backups")
    parser.add_argument("--auto-start", action="store_true", help="Iniciar backup automático")
    parser.add_argument("--auto-stop", action="store_true", help="Parar backup automático")
    parser.add_argument("--cleanup", action="store_true", help="Limpar backups antigos")
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.create:
        manager.create_backup(args.create, f"Backup manual - {args.create}")
    elif args.restore:
        manager.restore_backup(args.restore)
    elif args.delete:
        manager.delete_backup(args.delete)
    elif args.list:
        manager.show_backup_status()
    elif args.auto_start:
        manager.start_auto_backup()
    elif args.auto_stop:
        manager.stop_auto_backup()
    elif args.cleanup:
        manager.cleanup_old_backups()
    else:
        # Modo interativo
        console.print(Panel.fit(
            "[bold blue]💾 GERENCIADOR DE BACKUP[/bold blue]\n"
            "[cyan]Sistema de backup automático do Sales Agent IA[/cyan]",
            border_style="blue"
        ))
        
        while True:
            console.print("\n[bold yellow]Opções:[/yellow]")
            console.print("1. Criar backup")
            console.print("2. Restaurar backup")
            console.print("3. Listar backups")
            console.print("4. Deletar backup")
            console.print("5. Configurações")
            console.print("6. Sair")
            
            choice = console.input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                name = console.input("Nome do backup (ou Enter para automático): ").strip()
                description = console.input("Descrição: ").strip()
                manager.create_backup(name or None, description)
                
            elif choice == "2":
                manager.show_backup_status()
                name = console.input("Nome do backup para restaurar: ").strip()
                if name:
                    manager.restore_backup(name)
                    
            elif choice == "3":
                manager.show_backup_status()
                
            elif choice == "4":
                manager.show_backup_status()
                name = console.input("Nome do backup para deletar: ").strip()
                if name:
                    manager.delete_backup(name)
                    
            elif choice == "5":
                console.print(f"Configuração atual: {manager.config}")
                
            elif choice == "6":
                break
                
            else:
                console.print("❌ Opção inválida")

if __name__ == "__main__":
    main()
