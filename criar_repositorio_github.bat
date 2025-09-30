@echo off
echo ========================================
echo    CRIANDO REPOSITORIO NO GITHUB
echo ========================================
echo.

echo 1. Abrindo GitHub para criar repositorio...
echo    Nome: sales-agent
echo    Descricao: Sales Agent - Sistema inteligente de analise comercial
echo    Visibilidade: Publico
echo.

start https://github.com/new

echo.
echo 2. Apos criar o repositorio no GitHub:
echo    - Copie a URL do repositorio (ex: https://github.com/seu-usuario/sales-agent.git)
echo    - Cole abaixo quando solicitado
echo.

set /p REPO_URL="Cole a URL do repositorio aqui: "

echo.
echo 3. Conectando repositorio local com GitHub...
git remote add origin %REPO_URL%

echo.
echo 4. Enviando codigo para GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo    REPOSITORIO CRIADO COM SUCESSO!
echo ========================================
echo.
echo Seu projeto esta disponivel em: %REPO_URL%
echo.
pause
