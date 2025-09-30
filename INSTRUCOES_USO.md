# 🎯 ANALISADOR COMERCIAL MESTRE - Instruções de Uso

## 📋 O que este sistema faz

Este sistema transforma transcrições de reuniões comerciais em **insights estratégicos acionáveis**, seguindo exatamente o prompt mestre que você forneceu.

### ✨ Funcionalidades principais:

1. **Diagnóstico do Cliente** - Perfil, dores, stakeholders, gatilhos emocionais
2. **Termômetro da Oportunidade** - Scores 0-10 para urgência, autoridade, orçamento, fit e timing
3. **Estratégia de Follow-up** - Resumo executivo, objeções, templates de email
4. **Feedback de Performance Pessoal** - Análise da sua participação na reunião
5. **Radar de Tendências** - Overview geral de todas as análises
6. **Organização Automática** - Pasta para cada cliente com arquivos estruturados

## 🚀 Como usar (PASSO A PASSO)

### Passo 1: Preparar os arquivos
1. Coloque suas transcrições de reunião na pasta `Reunioes em TXT`
2. Cada arquivo deve ter o nome do cliente (ex: `joao_silva.txt`)
3. Os arquivos devem estar em formato `.txt` com codificação UTF-8

### Passo 2: Executar a análise
**Opção A - Execução Simples:**
```bash
python executar_analise.py
```

**Opção B - Execução Completa:**
```bash
python analisador_comercial_mestre.py
```

### Passo 3: Ver os resultados
Os resultados serão salvos na pasta `Analises_Comerciais/` com:
- Uma subpasta para cada cliente
- Arquivos individuais para cada tipo de análise
- Overview geral em CSV e JSON

## 📁 Estrutura de saída

Para cada cliente, você terá:

```
Analises_Comerciais/
├── cliente_joao/
│   ├── analise_completa.json          # Análise completa em JSON
│   ├── Diagnostico_Cliente.txt        # Perfil e características
│   ├── Score_Prioridade.txt           # Scores 0-10 detalhados
│   ├── Resumo_FollowUp.txt            # Estratégia de follow-up
│   ├── Feedback_Pessoal.txt           # Sua performance na reunião
│   └── Proximos_Passos.txt            # Ações recomendadas
├── overview_geral.csv                 # Tabela com todos os clientes
├── overview_geral.json                # Dados em JSON
└── relatorio_executivo.txt            # Relatório consolidado
```

## 📊 Exemplo de saída

### Score de Prioridade:
- **Urgência**: 8/10 (problema crítico identificado)
- **Autoridade**: 7/10 (contato tem poder de decisão)
- **Orçamento**: 6/10 (disponibilidade moderada)
- **Fit da Solução**: 9/10 (solução perfeita para o problema)
- **Timing**: 7/10 (prazo definido)
- **SCORE GERAL**: 7.4/10 (ALTA PRIORIDADE)

### Resumo Executivo:
"Cliente do setor tecnologia com alta prioridade (score 7.4/10). Principais dores: produtividade baixa, custos altos. Alta urgência detectada - priorizar follow-up imediato."

## 🔧 Requisitos técnicos

### Dependências necessárias:
```bash
pip install pandas matplotlib seaborn
```

### Ou instale tudo de uma vez:
```bash
pip install -r requirements.txt
```

## 🎯 Como interpretar os resultados

### Scores de 0-10:
- **0-3**: Baixo (precisa de mais informações)
- **4-6**: Médio (acompanhar de perto)
- **7-10**: Alto (prioridade máxima)

### Classificações de Prioridade:
- **ALTA PRIORIDADE** (8+): Ação imediata
- **MÉDIA PRIORIDADE** (6-7): Follow-up em 1 semana
- **BAIXA PRIORIDADE** (<6): Pipeline de longo prazo

## 💡 Dicas de uso

1. **Transcrições detalhadas** = Análises mais precisas
2. **Use nomes descritivos** para os arquivos (ex: `cliente_empresa_setor.txt`)
3. **Revise os feedbacks pessoais** para melhorar suas próximas reuniões
4. **Foque nos clientes de alta prioridade** primeiro
5. **Use os templates de email** como base para seus follow-ups

## 🚨 Solução de problemas

### Erro: "Pasta 'Reunioes em TXT' não encontrada"
- Crie a pasta `Reunioes em TXT` na raiz do projeto
- Adicione os arquivos .txt das transcrições

### Erro: "Nenhum arquivo .txt encontrado"
- Verifique se os arquivos estão na pasta correta
- Confirme que têm extensão .txt
- Verifique a codificação (deve ser UTF-8)

### Erro de dependências
- Execute: `pip install pandas matplotlib seaborn`
- Ou: `pip install -r requirements.txt`

## 📞 Suporte

Se tiver dúvidas ou problemas:
1. Verifique se seguiu todos os passos
2. Confirme que os arquivos estão no lugar correto
3. Teste com um arquivo de transcrição simples primeiro

---

**🎉 Pronto para transformar suas reuniões em vendas!**
