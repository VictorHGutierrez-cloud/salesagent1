"""
🎯 SALES AGENT IA - CONFIGURAÇÕES
===============================
Configurações centralizadas para o agente de vendas IA
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações principais do sistema"""
    
    # ==========================================
    # OPENAI SETTINGS
    # ==========================================
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o-mini'
    OPENAI_TEMPERATURE = 0.3
    WHISPER_MODEL = 'whisper-1'
    
    # ==========================================
    # AUDIO SETTINGS
    # ==========================================
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_DURATION = 2.0  # segundos
    AUDIO_THRESHOLD = 0.01  # limiar de detecção de voz
    
    # ==========================================
    # PATHS
    # ==========================================
    BASE_DIR = Path(__file__).parent
    TOOLKIT_DIR = BASE_DIR / "AE_SENIOR_TOOLKIT"
    TEMP_DIR = BASE_DIR / "temp"
    EMBEDDINGS_DIR = BASE_DIR / "embeddings"
    
    # ==========================================
    # VECTOR DATABASE
    # ==========================================
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    VECTOR_DB_PATH = str(EMBEDDINGS_DIR / "sales_knowledge.db")
    TOP_K_RESULTS = 3  # Número de técnicas relevantes para buscar
    
    # ==========================================
    # INTERFACE
    # ==========================================
    OVERLAY_POSITION = "top-right"  # top-left, top-right, bottom-left, bottom-right
    OVERLAY_OPACITY = 0.9
    OVERLAY_WIDTH = 400
    OVERLAY_HEIGHT = 200
    
    # ==========================================
    # SYSTEM
    # ==========================================
    LOG_LEVEL = "INFO"
    MAX_HISTORY = 10  # Máximo de conversas anteriores para contexto
    
    @classmethod
    def create_directories(cls):
        """Cria diretórios necessários"""
        cls.TEMP_DIR.mkdir(exist_ok=True)
        cls.EMBEDDINGS_DIR.mkdir(exist_ok=True)
        
    @classmethod
    def validate_config(cls):
        """Valida configurações essenciais"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY não configurada! Adicione no arquivo .env")
        
        if not cls.TOOLKIT_DIR.exists():
            raise ValueError(f"❌ Diretório do toolkit não encontrado: {cls.TOOLKIT_DIR}")
            
        return True

# ==========================================
# PROMPTS DO SISTEMA
# ==========================================

SYSTEM_PROMPTS = {
    "main_agent": """Você é meu CONSULTOR ESTRATÉGICO DE VENDAS IA em tempo real.

🎯 PERFIL:
- QI 180, extremamente analítico
- Experiência em criar empresas bilionárias  
- Profundo conhecimento em psicologia, estratégia e vendas
- Foco em pontos de alavancagem de máximo impacto
- Pensamento por primeiros princípios

🎯 OBJETIVO:
Analisar conversas de vendas em TEMPO REAL e fornecer sugestões estratégicas INSTANTÂNEAS.

🎯 FORMATO DE RESPOSTA:
- MÁXIMO 2 frases curtas
- Foco em AÇÃO imediata
- Baseado nas técnicas do toolkit disponível
- Tom direto e estratégico

🎯 CONTEXTO DISPONÍVEL:
{context}

🎯 HISTÓRICO DA CONVERSA:
{history}

🎯 CLIENTE DISSE:
"{user_input}"

Forneça uma sugestão estratégica IMEDIATA:""",

    "context_analyzer": """Analise este trecho de conversa de vendas e identifique:

1. MOMENTO DA VENDA (prospecting/discovery/demo/proposal/closing)
2. SINAIS DE COMPRA ou OBJEÇÕES
3. TÉCNICA MAIS RELEVANTE do toolkit
4. URGÊNCIA (1-10)

Conversa: "{text}"

Resposta em JSON:
{{"momento": "", "sinais": [], "tecnica_relevante": "", "urgencia": 0}}"""
}

# ==========================================
# CONFIGURAÇÕES AVANÇADAS
# ==========================================

ADVANCED_CONFIG = {
    "audio_processing": {
        "noise_reduction": True,
        "auto_gain": True,
        "silence_detection": True
    },
    "ai_processing": {
        "batch_processing": False,
        "real_time_mode": True,
        "context_window": 4000
    },
    "interface": {
        "auto_hide": True,
        "fade_animation": True,
        "click_through": False
    }
}
