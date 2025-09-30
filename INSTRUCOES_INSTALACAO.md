# 🚀 SALES AGENT IA - INSTRUÇÕES DE INSTALAÇÃO

## 📋 **REQUISITOS**

### Sistema Operacional
- ✅ Windows 10/11
- ✅ Python 3.8 ou superior
- ✅ Conexão com internet

### APIs Necessárias
- 🔑 **OpenAI API Key** (obrigatório)
  - Acesse: https://platform.openai.com/api-keys
  - Crie uma nova API key
  - Certifique-se de ter créditos disponíveis

## 🛠️ **INSTALAÇÃO PASSO A PASSO**

### **PASSO 1: Preparação**

1. **Abra o PowerShell como Administrador**
   - Tecle `Windows + X`
   - Clique em "Windows PowerShell (Admin)"

2. **Verifique o Python**
   ```powershell
   python --version
   ```
   - Deve mostrar Python 3.8 ou superior
   - Se não tiver Python: baixe em https://python.org

### **PASSO 2: Instalação Automática**

1. **Execute o setup automático**
   ```powershell
   cd "C:\Users\victo\Sales Agent"
   python setup_system.py
   ```

2. **Siga as instruções na tela:**
   - ✅ Será verificado o Python
   - ✅ Instaladas todas as dependências
   - ✅ Solicitada sua OpenAI API Key
   - ✅ Configurado o sistema

### **PASSO 3: Configuração Manual (se necessário)**

Se o setup automático falhar:

1. **Instale dependências manualmente:**
   ```powershell
   pip install -r requirements_ia_agent.txt
   ```

2. **Configure o arquivo .env:**
   - Copie `env_example.txt` para `.env`
   - Abra `.env` e adicione sua API key:
   ```
   OPENAI_API_KEY=sua_api_key_aqui
   ```

## 🚀 **INICIANDO O SISTEMA**

### **Primeiro Uso**

1. **Execute o sistema principal:**
   ```powershell
   python sales_agent_main.py
   ```

2. **O que vai acontecer:**
   - 📚 Construção da base de conhecimento (primeira vez)
   - 🎤 Teste de dispositivos de áudio
   - 🖥️ Abertura da interface
   - 🔄 Sistema pronto para uso

### **Dashboard Interativo**

- ✅ **Status em tempo real** de todos os componentes
- 📊 **Estatísticas** de uso
- 🎤 **Indicador** de captura de áudio
- 💡 **Contador** de sugestões geradas

## 🎯 **COMO USAR**

### **Durante uma Reunião de Vendas**

1. **Inicie o sistema** antes da reunião
2. **Posicione o microfone** para captar sua conversa
3. **Observe as sugestões** que aparecem automaticamente
4. **Use as sugestões** para guiar sua abordagem

### **Sugestões Aparecerão Quando:**

- 🛡️ **Cliente faz objeções** → Técnicas de tratamento
- 🎯 **Momento de fechar** → Scripts de fechamento  
- 💡 **Oportunidade de valor** → Propostas de ROI
- 🔍 **Discovery** → Perguntas estratégicas

## ⚙️ **CONFIGURAÇÕES**

### **Interface**

- **Posição do overlay:** Canto da tela
- **Transparência:** Ajustável
- **Auto-hide:** Sugestões somem automaticamente

### **System Tray**

- 🔍 **Ícone azul** na system tray
- 🖱️ **Clique direito** para opções
- ⚙️ **Configurações** disponíveis

## 🔧 **SOLUÇÃO DE PROBLEMAS**

### **Erro: "OPENAI_API_KEY não configurada"**

```powershell
# Verifique se o arquivo .env existe
ls .env

# Se não existir, copie do exemplo
cp env_example.txt .env

# Edite o arquivo .env e adicione sua API key
notepad .env
```

### **Erro: "Microfone não detectado"**

1. **Verifique dispositivos:**
   ```powershell
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

2. **Configure no Windows:**
   - Configurações → Sistema → Som
   - Teste o microfone

### **Erro: "Base de conhecimento não encontrada"**

```powershell
# Execute o construtor da base
python knowledge_embedder.py
```

### **Performance Lenta**

1. **Verifique recursos:**
   - CPU: Mínimo 4 cores
   - RAM: Mínimo 8GB
   - Internet: Estável para OpenAI

2. **Otimizações:**
   - Feche outros programas
   - Use SSD se possível

## 📁 **ESTRUTURA DE ARQUIVOS**

```
Sales Agent/
├── sales_agent_main.py      # 🚀 Sistema principal
├── setup_system.py          # ⚙️ Instalador
├── config.py                # 🔧 Configurações
├── knowledge_embedder.py    # 📚 Base de conhecimento
├── audio_capture.py         # 🎤 Captura de áudio
├── speech_processor.py      # 🗣️ Speech-to-Text
├── sales_intelligence.py    # 🧠 Motor de IA
├── overlay_interface.py     # 🖥️ Interface visual
├── .env                     # 🔑 Configurações (criar)
├── temp/                    # 📁 Arquivos temporários
├── embeddings/              # 📁 Base de conhecimento
├── logs/                    # 📁 Logs do sistema
└── AE_SENIOR_TOOLKIT/       # 📚 Sua base de técnicas
```

## 💡 **DICAS DE USO**

### **Maximizando Resultados**

1. **Posicione bem o microfone**
   - Próximo à sua boca
   - Evite ruídos de fundo

2. **Customize sua base**
   - Adicione seus próprios scripts
   - Atualize técnicas regularmente

3. **Use o feedback**
   - Marque sugestões úteis
   - Sistema aprende com uso

### **Boas Práticas**

- 🎤 **Teste o áudio** antes de reuniões importantes
- 📱 **Mantenha API credits** suficientes
- 🔄 **Atualize regularmente** o sistema
- 💾 **Faça backup** das configurações

## 📞 **SUPORTE**

### **Logs do Sistema**

```powershell
# Visualizar logs em tempo real
Get-Content logs\sales_agent_*.log -Wait -Tail 50
```

### **Reiniciar Sistema**

```powershell
# Para tudo e reinicia
python sales_agent_main.py
```

### **Reset Completo**

```powershell
# Remove base de conhecimento (será recriada)
rm -rf embeddings\*

# Remove logs
rm -rf logs\*

# Reconstrói tudo
python sales_agent_main.py
```

---

## 🎯 **PRONTO PARA VENDER!**

Agora você tem um **consultor estratégico IA** que:

- 🎤 **Escuta** suas reuniões em tempo real
- 🧠 **Analisa** com base em seu toolkit
- 💡 **Sugere** ações estratégicas instantâneas
- 🎯 **Maximiza** seus resultados de vendas

**Boa sorte nas vendas! 🚀**
