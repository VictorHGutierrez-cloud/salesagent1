# 🚀 Otimização para Cursor IDE

## Configurações Recomendadas

### 1. Atalhos Personalizados
Adicione estes atalhos no Cursor para acelerar seu workflow:

```json
{
    "key": "ctrl+shift+a",
    "command": "workbench.action.terminal.sendSequence",
    "args": {
        "text": "python analisador_reunioes.py\r"
    }
},
{
    "key": "ctrl+shift+e",
    "command": "workbench.action.terminal.sendSequence",
    "args": {
        "text": "python exemplo_uso.py\r"
    }
},
{
    "key": "ctrl+shift+s",
    "command": "workbench.action.terminal.sendSequence",
    "args": {
        "text": "python setup.py\r"
    }
}
```

### 2. Snippets Personalizados
Crie snippets para acelerar a criação de análises:

**Arquivo: `.cursor/snippets/sales.json`**
```json
{
    "Análise Rápida": {
        "prefix": "analise",
        "body": [
            "from analisador_reunioes import AnalisadorReunioes",
            "from pathlib import Path",
            "",
            "# Inicializa analisador",
            "analisador = AnalisadorReunioes()",
            "",
            "# Analisa arquivo específico",
            "arquivo = Path('Reunioes em TXT/${1:nome_cliente}.txt')",
            "analise = analisador.analisar_transcricao(arquivo)",
            "",
            "# Salva análise",
            "if analise:",
            "    analisador.salvar_analise('${1:nome_cliente}', analise)",
            "    print('✅ Análise salva!')"
        ],
        "description": "Template para análise rápida"
    }
}
```

### 3. Workspace Recomendado
Organize seu workspace assim:

```
📁 Analise Reunioes/
├── 📁 Reunioes em TXT/          # Suas transcrições
├── 📁 Analises/                 # Resultados (não versionar)
├── 📁 .cursor/                  # Configurações do Cursor
├── 📁 scripts/                  # Scripts auxiliares
├── 📄 analisador_reunioes.py    # Script principal
├── 📄 exemplo_uso.py            # Exemplos
├── 📄 setup.py                  # Configuração
└── 📄 README.md                 # Documentação
```

### 4. Extensões Recomendadas
Instale estas extensões no Cursor:

- **Python** (Microsoft) - Suporte completo ao Python
- **Python Docstring Generator** - Gera documentação automaticamente
- **Excel Viewer** - Visualiza CSVs gerados
- **Markdown Preview Enhanced** - Visualiza README.md
- **JSON** - Suporte a arquivos JSON
- **Path Intellisense** - Autocomplete para caminhos

### 5. Configurações de Terminal
Configure o terminal para abrir na pasta do projeto:

**settings.json:**
```json
{
    "terminal.integrated.cwd": "${workspaceFolder}",
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

### 6. Comandos Personalizados
Crie estes comandos no Command Palette (Ctrl+Shift+P):

**Arquivo: `.cursor/tasks.json`**
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Analisar Reuniões",
            "type": "shell",
            "command": "python",
            "args": ["analisador_reunioes.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "Exemplos de Uso",
            "type": "shell",
            "command": "python",
            "args": ["exemplo_uso.py"],
            "group": "build"
        },
        {
            "label": "Setup Inicial",
            "type": "shell",
            "command": "python",
            "args": ["setup.py"],
            "group": "build"
        }
    ]
}
```

### 7. Debugging
Configure o debugger para testar análises:

**Arquivo: `.cursor/launch.json`**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Analisar Reunião",
            "type": "python",
            "request": "launch",
            "program": "analisador_reunioes.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Exemplo de Uso",
            "type": "python",
            "request": "launch",
            "program": "exemplo_uso.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### 8. Git Ignore
Crie `.gitignore` para não versionar arquivos desnecessários:

```gitignore
# Análises geradas
Analises/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# Dados sensíveis
.env
*.key
```

### 9. Workflow Recomendado

#### Para Nova Reunião:
1. **Coloque** a transcrição em `Reunioes em TXT/`
2. **Execute** `python analisador_reunioes.py`
3. **Revise** os resultados em `Analises/`
4. **Execute** follow-ups sugeridos

#### Para Análise Rápida:
1. **Use** o snippet `analise` (digite `analise` + Tab)
2. **Modifique** o nome do cliente
3. **Execute** o código (Ctrl+Enter)

#### Para Debugging:
1. **Coloque** breakpoints no código
2. **Execute** F5 para debug
3. **Inspecione** variáveis no debugger

### 10. Dicas Avançadas

#### Multi-cursor para Edição Rápida:
- **Ctrl+D**: Seleciona próxima ocorrência
- **Ctrl+Shift+L**: Seleciona todas as ocorrências
- **Alt+Click**: Adiciona cursor

#### Busca Inteligente:
- **Ctrl+Shift+F**: Busca em todos os arquivos
- **Ctrl+F**: Busca no arquivo atual
- **Ctrl+G**: Vai para linha específica

#### Navegação Rápida:
- **Ctrl+P**: Abre arquivo rapidamente
- **Ctrl+Shift+O**: Vai para símbolo no arquivo
- **Ctrl+T**: Vai para símbolo no workspace

### 11. Integração com IA
Use o Cursor AI para:

- **Gerar** análises personalizadas
- **Modificar** templates de follow-up
- **Criar** novos frameworks de análise
- **Otimizar** prompts para melhor precisão

**Exemplo de prompt para IA:**
```
Analise esta transcrição de reunião focando em:
1. Sinais de urgência e necessidade
2. Stakeholders e tomadores de decisão
3. Objeções e preocupações
4. Próximos passos estratégicos

Transcrição: [cole aqui]
```

### 12. Monitoramento de Performance
Configure alertas para:

- **Tempo** de processamento > 30s
- **Erros** de API
- **Arquivos** não processados
- **Scores** muito baixos

---

**Com essas configurações, você terá um ambiente de desenvolvimento otimizado para análise estratégica de vendas!**
