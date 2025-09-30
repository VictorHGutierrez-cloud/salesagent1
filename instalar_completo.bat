@echo off
echo ========================================
echo SALES AGENT IA - INSTALADOR COMPLETO
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado!
    echo.
    echo 1. Baixe Python em: https://www.python.org/downloads/
    echo 2. IMPORTANTE: Marque "Add Python to PATH" durante instalacao
    echo 3. Reinicie este script apos instalar
    echo.
    pause
    exit /b 1
)

echo Python encontrado! Continuando...
echo.

echo Atualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias...
python -m pip install -r requirements_ia_agent.txt

echo.
echo Testando sistema...
python -c "import openai; print('OpenAI OK')"

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para iniciar o sistema:
echo python sales_agent_main.py
echo.
pause
