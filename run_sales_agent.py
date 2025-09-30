#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SALES AGENT IA - LAUNCHER
===========================
Script de execução principal
"""

import sys
from pathlib import Path

# Adiciona diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sales_agent_advanced import main
    main()
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Execute: python install_advanced.py")
except Exception as e:
    print(f"❌ Erro: {e}")
