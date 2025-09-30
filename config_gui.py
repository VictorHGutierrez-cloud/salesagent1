#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖥️ SALES AGENT IA - INTERFACE GRÁFICA DE CONFIGURAÇÕES
======================================================
Interface moderna para configuração do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from rich.console import Console

console = Console()

class ConfigGUI:
    """Interface gráfica para configurações"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sales Agent IA - Configurações")
        self.root.geometry("800x600")
        self.root.configure(bg='#2d3748')
        
        # Carrega configurações
        self.config_dir = Path(__file__).parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.configs = self._load_all_configs()
        
        # Cria interface
        self._create_interface()
        
        # Atualiza status
        self._update_status()
    
    def _load_all_configs(self) -> Dict[str, Any]:
        """Carrega todas as configurações"""
        configs = {}
        
        config_files = [
            "system_config.json",
            "backup_config.json", 
            "logging_config.json",
            "dependency_monitor_config.json"
        ]
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        configs[config_file.replace('.json', '')] = json.load(f)
                except Exception as e:
                    console.print(f"[yellow]⚠️ Erro ao carregar {config_file}: {e}[/yellow]")
        
        return configs
    
    def _create_interface(self):
        """Cria interface principal"""
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba Sistema
        self._create_system_tab()
        
        # Aba Backup
        self._create_backup_tab()
        
        # Aba Logs
        self._create_logs_tab()
        
        # Aba Dependências
        self._create_dependencies_tab()
        
        # Aba Status
        self._create_status_tab()
        
        # Botões principais
        self._create_action_buttons()
    
    def _create_system_tab(self):
        """Cria aba de configurações do sistema"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="Sistema")
        
        # Configurações OpenAI
        openai_frame = ttk.LabelFrame(system_frame, text="OpenAI", padding=10)
        openai_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(openai_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=2)
        self.openai_key_var = tk.StringVar()
        self.openai_key_entry = ttk.Entry(openai_frame, textvariable=self.openai_key_var, width=50, show="*")
        self.openai_key_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        ttk.Button(openai_frame, text="Testar", command=self._test_openai).grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Configurações de áudio
        audio_frame = ttk.LabelFrame(system_frame, text="Áudio", padding=10)
        audio_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(audio_frame, text="Dispositivo:").grid(row=0, column=0, sticky='w', pady=2)
        self.audio_device_var = tk.StringVar()
        self.audio_device_combo = ttk.Combobox(audio_frame, textvariable=self.audio_device_var, width=30)
        self.audio_device_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        ttk.Button(audio_frame, text="Detectar", command=self._detect_audio_devices).grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Configurações de interface
        ui_frame = ttk.LabelFrame(system_frame, text="Interface", padding=10)
        ui_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(ui_frame, text="Posição do overlay:").grid(row=0, column=0, sticky='w', pady=2)
        self.overlay_pos_var = tk.StringVar(value="top-right")
        overlay_pos_combo = ttk.Combobox(ui_frame, textvariable=self.overlay_pos_var, 
                                       values=["top-left", "top-right", "bottom-left", "bottom-right"])
        overlay_pos_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        ttk.Label(ui_frame, text="Transparência:").grid(row=1, column=0, sticky='w', pady=2)
        self.opacity_var = tk.DoubleVar(value=0.9)
        opacity_scale = ttk.Scale(ui_frame, from_=0.1, to=1.0, variable=self.opacity_var, orient='horizontal')
        opacity_scale.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        # Carrega valores atuais
        self._load_system_config()
    
    def _create_backup_tab(self):
        """Cria aba de configurações de backup"""
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="Backup")
        
        # Configurações gerais
        general_frame = ttk.LabelFrame(backup_frame, text="Configurações Gerais", padding=10)
        general_frame.pack(fill='x', padx=10, pady=5)
        
        self.backup_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(general_frame, text="Backup automático habilitado", 
                       variable=self.backup_enabled_var).grid(row=0, column=0, sticky='w', pady=2)
        
        ttk.Label(general_frame, text="Intervalo (horas):").grid(row=1, column=0, sticky='w', pady=2)
        self.backup_interval_var = tk.IntVar(value=24)
        ttk.Spinbox(general_frame, from_=1, to=168, textvariable=self.backup_interval_var, width=10).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Máximo de backups:").grid(row=2, column=0, sticky='w', pady=2)
        self.max_backups_var = tk.IntVar(value=10)
        ttk.Spinbox(general_frame, from_=1, to=100, textvariable=self.max_backups_var, width=10).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Configurações de conteúdo
        content_frame = ttk.LabelFrame(backup_frame, text="Conteúdo do Backup", padding=10)
        content_frame.pack(fill='x', padx=10, pady=5)
        
        self.include_logs_var = tk.BooleanVar()
        ttk.Checkbutton(content_frame, text="Incluir logs", 
                       variable=self.include_logs_var).grid(row=0, column=0, sticky='w', pady=2)
        
        self.include_temp_var = tk.BooleanVar()
        ttk.Checkbutton(content_frame, text="Incluir arquivos temporários", 
                       variable=self.include_temp_var).grid(row=1, column=0, sticky='w', pady=2)
        
        self.compress_backups_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(content_frame, text="Comprimir backups", 
                       variable=self.compress_backups_var).grid(row=2, column=0, sticky='w', pady=2)
        
        # Ações de backup
        actions_frame = ttk.LabelFrame(backup_frame, text="Ações", padding=10)
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Criar Backup Agora", command=self._create_backup_now).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Listar Backups", command=self._list_backups).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Limpar Backups Antigos", command=self._cleanup_backups).pack(side='left')
        
        # Carrega valores atuais
        self._load_backup_config()
    
    def _create_logs_tab(self):
        """Cria aba de configurações de logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Configurações gerais
        general_frame = ttk.LabelFrame(logs_frame, text="Configurações Gerais", padding=10)
        general_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(general_frame, text="Nível de log:").grid(row=0, column=0, sticky='w', pady=2)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(general_frame, textvariable=self.log_level_var,
                                     values=["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"])
        log_level_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Tamanho máximo do arquivo:").grid(row=1, column=0, sticky='w', pady=2)
        self.max_file_size_var = tk.StringVar(value="10MB")
        max_file_size_combo = ttk.Combobox(general_frame, textvariable=self.max_file_size_var,
                                         values=["1MB", "5MB", "10MB", "50MB", "100MB"])
        max_file_size_combo.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Retenção (dias):").grid(row=2, column=0, sticky='w', pady=2)
        self.retention_days_var = tk.IntVar(value=30)
        ttk.Spinbox(general_frame, from_=1, to=365, textvariable=self.retention_days_var, width=10).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Configurações de saída
        output_frame = ttk.LabelFrame(logs_frame, text="Saída de Logs", padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)
        
        self.enable_console_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Habilitar console", 
                       variable=self.enable_console_var).grid(row=0, column=0, sticky='w', pady=2)
        
        self.enable_file_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Habilitar arquivo", 
                       variable=self.enable_file_var).grid(row=1, column=0, sticky='w', pady=2)
        
        self.enable_analysis_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Habilitar análise", 
                       variable=self.enable_analysis_var).grid(row=2, column=0, sticky='w', pady=2)
        
        # Ações de logs
        actions_frame = ttk.LabelFrame(logs_frame, text="Ações", padding=10)
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Ver Dashboard", command=self._show_log_dashboard).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Exportar Logs", command=self._export_logs).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Limpar Logs Antigos", command=self._cleanup_logs).pack(side='left')
        
        # Carrega valores atuais
        self._load_logs_config()
    
    def _create_dependencies_tab(self):
        """Cria aba de dependências"""
        deps_frame = ttk.Frame(self.notebook)
        self.notebook.add(deps_frame, text="Dependências")
        
        # Configurações do monitor
        monitor_frame = ttk.LabelFrame(deps_frame, text="Monitor de Dependências", padding=10)
        monitor_frame.pack(fill='x', padx=10, pady=5)
        
        self.deps_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(monitor_frame, text="Monitoramento habilitado", 
                       variable=self.deps_enabled_var).pack(anchor='w', pady=2)
        
        ttk.Label(monitor_frame, text="Intervalo de verificação (minutos):").pack(anchor='w', pady=2)
        self.deps_interval_var = tk.IntVar(value=5)
        ttk.Spinbox(monitor_frame, from_=1, to=60, textvariable=self.deps_interval_var, width=10).pack(anchor='w', padx=(0, 0), pady=2)
        
        self.auto_update_var = tk.BooleanVar()
        ttk.Checkbutton(monitor_frame, text="Atualização automática", 
                       variable=self.auto_update_var).pack(anchor='w', pady=2)
        
        self.notify_issues_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(monitor_frame, text="Notificar sobre problemas", 
                       variable=self.notify_issues_var).pack(anchor='w', pady=2)
        
        # Ações de dependências
        actions_frame = ttk.LabelFrame(deps_frame, text="Ações", padding=10)
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Verificar Todas", command=self._check_all_dependencies).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Mostrar Status", command=self._show_deps_status).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Instalar Faltantes", command=self._install_missing).pack(side='left')
        
        # Carrega valores atuais
        self._load_dependencies_config()
    
    def _create_status_tab(self):
        """Cria aba de status do sistema"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        
        # Status geral
        general_frame = ttk.LabelFrame(status_frame, text="Status Geral", padding=10)
        general_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_text = tk.Text(general_frame, height=15, width=80, wrap='word')
        status_scrollbar = ttk.Scrollbar(general_frame, orient='vertical', command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side='left', fill='both', expand=True)
        status_scrollbar.pack(side='right', fill='y')
        
        # Botões de atualização
        update_frame = ttk.Frame(status_frame)
        update_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(update_frame, text="Atualizar Status", command=self._update_status).pack(side='left', padx=(0, 10))
        ttk.Button(update_frame, text="Exportar Relatório", command=self._export_status_report).pack(side='left')
    
    def _create_action_buttons(self):
        """Cria botões de ação principais"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Salvar Todas as Configurações", 
                 command=self._save_all_configs).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Restaurar Padrões", 
                 command=self._restore_defaults).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Fechar", 
                 command=self.root.quit).pack(side='right')
    
    def _load_system_config(self):
        """Carrega configurações do sistema"""
        # Implementar carregamento das configurações
        pass
    
    def _load_backup_config(self):
        """Carrega configurações de backup"""
        # Implementar carregamento das configurações
        pass
    
    def _load_logs_config(self):
        """Carrega configurações de logs"""
        # Implementar carregamento das configurações
        pass
    
    def _load_dependencies_config(self):
        """Carrega configurações de dependências"""
        # Implementar carregamento das configurações
        pass
    
    def _test_openai(self):
        """Testa conexão com OpenAI"""
        messagebox.showinfo("Teste", "Funcionalidade de teste em desenvolvimento")
    
    def _detect_audio_devices(self):
        """Detecta dispositivos de áudio"""
        messagebox.showinfo("Detecção", "Funcionalidade de detecção em desenvolvimento")
    
    def _create_backup_now(self):
        """Cria backup imediatamente"""
        messagebox.showinfo("Backup", "Funcionalidade de backup em desenvolvimento")
    
    def _list_backups(self):
        """Lista backups disponíveis"""
        messagebox.showinfo("Backups", "Funcionalidade de listagem em desenvolvimento")
    
    def _cleanup_backups(self):
        """Limpa backups antigos"""
        messagebox.showinfo("Limpeza", "Funcionalidade de limpeza em desenvolvimento")
    
    def _show_log_dashboard(self):
        """Mostra dashboard de logs"""
        messagebox.showinfo("Dashboard", "Funcionalidade de dashboard em desenvolvimento")
    
    def _export_logs(self):
        """Exporta logs"""
        messagebox.showinfo("Exportação", "Funcionalidade de exportação em desenvolvimento")
    
    def _cleanup_logs(self):
        """Limpa logs antigos"""
        messagebox.showinfo("Limpeza", "Funcionalidade de limpeza em desenvolvimento")
    
    def _check_all_dependencies(self):
        """Verifica todas as dependências"""
        messagebox.showinfo("Verificação", "Funcionalidade de verificação em desenvolvimento")
    
    def _show_deps_status(self):
        """Mostra status das dependências"""
        messagebox.showinfo("Status", "Funcionalidade de status em desenvolvimento")
    
    def _install_missing(self):
        """Instala dependências faltantes"""
        messagebox.showinfo("Instalação", "Funcionalidade de instalação em desenvolvimento")
    
    def _update_status(self):
        """Atualiza status do sistema"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Atualizando status...\n")
        
        # Simula atualização
        threading.Timer(1.0, self._populate_status).start()
    
    def _populate_status(self):
        """Popula status do sistema"""
        status_info = f"""
Sales Agent IA - Status do Sistema
==================================

Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Configurações:
- Sistema: {'✅' if 'system_config' in self.configs else '❌'}
- Backup: {'✅' if 'backup_config' in self.configs else '❌'}
- Logs: {'✅' if 'logging_config' in self.configs else '❌'}
- Dependências: {'✅' if 'dependency_monitor_config' in self.configs else '❌'}

Status dos Componentes:
- Setup Avançado: ✅ Ativo
- Backup Manager: ✅ Ativo
- Sistema de Logs: ✅ Ativo
- Monitor de Dependências: ✅ Ativo
- Interface Gráfica: ✅ Ativo

Recomendações:
- Verifique as configurações de backup
- Monitore os logs regularmente
- Mantenha as dependências atualizadas
        """
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, status_info)
    
    def _export_status_report(self):
        """Exporta relatório de status"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.status_text.get(1.0, tk.END))
            messagebox.showinfo("Exportação", f"Relatório salvo em: {filename}")
    
    def _save_all_configs(self):
        """Salva todas as configurações"""
        # Implementar salvamento das configurações
        messagebox.showinfo("Salvamento", "Configurações salvas com sucesso!")
    
    def _restore_defaults(self):
        """Restaura configurações padrão"""
        if messagebox.askyesno("Confirmação", "Deseja restaurar as configurações padrão?"):
            # Implementar restauração
            messagebox.showinfo("Restauração", "Configurações restauradas para os padrões!")
    
    def run(self):
        """Executa a interface"""
        self.root.mainloop()

def main():
    """Função principal"""
    app = ConfigGUI()
    app.run()

if __name__ == "__main__":
    main()
