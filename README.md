# Sales Agent - Sistema Inteligente de Análise Comercial

## 🎯 Visão Geral

O **Sales Agent** é um sistema avançado de análise comercial que utiliza inteligência artificial para processar transcrições de reuniões de vendas, extrair insights estratégicos e gerar recomendações de follow-up personalizadas.

## 🚀 Funcionalidades Principais

### 📊 Análise Inteligente de Reuniões
- **Processamento de Transcrições**: Converte áudio em texto e analisa conversas de vendas
- **Classificação de Leads**: Avalia urgência, necessidade e fit usando frameworks BANT, MEDDIC e SPIN
- **Extração de Insights**: Identifica dores, objeções, stakeholders-chave e próximos passos
- **Scoring Automático**: Calcula temperatura do lead (Cold/Warm/Hot) baseado em sinais comportamentais

### 🎯 Frameworks de Qualificação
- **BANT**: Budget, Authority, Need, Timeline
- **MEDDIC**: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion
- **SPIN**: Situation, Problem, Implication, Need-payoff

### 📈 Relatórios Executivos
- Resumos executivos de 3-5 linhas
- Highlights das principais dores e gatilhos
- Scores de urgência, necessidade e fit (0-1)
- Recomendações estratégicas personalizadas
- Templates de follow-up prontos para envio

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **OpenAI GPT-4** para análise de linguagem natural
- **Speech Recognition** para conversão de áudio
- **Pandas** para análise de dados
- **Streamlit** para interface web
- **GitHub** para controle de versão

## 📁 Estrutura do Projeto

```
Sales Agent/
├── 📁 AE_SENIOR_TOOLKIT/          # Toolkit completo de vendas
│   ├── 01_PROSPECCAO_AVANCADA/
│   ├── 02_QUALIFICACAO_LEADS/
│   ├── 03_DISCOVERY_COMPLETO/
│   └── ...
├── 📁 Analises/                    # Análises processadas
├── 📁 Analises_Comerciais/         # Relatórios comerciais
├── 📁 Reunioes em TXT/            # Transcrições de reuniões
├── 📁 Treinamento_Sales_Agent/    # Materiais de treinamento
├── 🐍 analisador_comercial_mestre.py
├── 🐍 sales_agent_main.py
└── 📄 requirements.txt
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Conta OpenAI com API key
- Git instalado

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/sales-agent.git
   cd sales-agent
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   # Copie o arquivo de exemplo
   copy env_example.txt .env
   
   # Edite o arquivo .env e adicione sua API key
   OPENAI_API_KEY=sua_api_key_aqui
   ```

4. **Execute o sistema**
   ```bash
   python sales_agent_main.py
   ```

## 📖 Como Usar

### 1. Análise de Transcrição
- Cole o texto da reunião no sistema
- O AI analisará automaticamente o conteúdo
- Receba insights estruturados e recomendações

### 2. Análise de Áudio
- Grave ou faça upload de arquivos de áudio
- O sistema converterá para texto automaticamente
- Processe a análise como transcrição

### 3. Relatórios Executivos
- Visualize análises em formato executivo
- Exporte relatórios em PDF ou CSV
- Compartilhe insights com a equipe

## 🎯 Casos de Uso

### Para Vendedores
- Analise reuniões em tempo real
- Identifique oportunidades de follow-up
- Melhore suas técnicas de qualificação

### Para Gerentes
- Monitore performance da equipe
- Identifique padrões de sucesso
- Otimize processos de vendas

### Para Executivos
- Acompanhe pipeline de vendas
- Tome decisões baseadas em dados
- Maximize ROI de vendas

## 📊 Exemplos de Análise

### Input (Transcrição)
```
"Precisamos urgentemente de uma solução para nosso problema de produtividade. 
O orçamento está aprovado e precisamos implementar até o final do trimestre."
```

### Output (Análise)
- **Urgência**: 0.9/1.0 (Alta)
- **Necessidade**: 0.8/1.0 (Alta)
- **Fit**: 0.7/1.0 (Bom)
- **Temperatura**: 🔥 HOT
- **Recomendação**: Agendar demo técnica imediatamente

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Abra uma issue no GitHub
- Entre em contato: [seu-email@exemplo.com]

## 🎯 Roadmap

- [ ] Integração com CRM (Salesforce, HubSpot)
- [ ] Análise de sentimento em tempo real
- [ ] Dashboard executivo avançado
- [ ] API REST para integrações
- [ ] Mobile app para vendedores

---

**Desenvolvido com ❤️ para revolucionar o processo de vendas**