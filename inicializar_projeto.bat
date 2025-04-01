@echo off
echo =======================================================
echo   Senac Capsula - Sistema de Gerenciamento de Palestrantes
echo =======================================================
echo.
echo Este script irá inicializar o projeto completamente:
echo 1. Instalar dependências
echo 2. Inicializar o banco de dados
echo 3. Criar um usuário administrador 
echo 4. Iniciar a aplicação
echo.
echo =======================================================
echo.

REM Verificar se os requisitos estão instalados
echo Verificando dependências...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha ao instalar dependências.
    goto end
)

echo.
echo Dependências instaladas com sucesso!
echo.

REM Inicializar o banco de dados
echo Inicializando banco de dados...
python inicializar_db.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha ao inicializar o banco de dados.
    goto end
)

echo.
echo Banco de dados inicializado com sucesso!
echo.

REM Criar usuário administrador
echo Criando usuário administrador...
python criar_admin.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha ao criar o usuário administrador.
    goto end
)

echo.
echo.
echo =======================================================
echo Inicialização completa! Iniciando a aplicação...
echo =======================================================
echo.

REM Iniciar a aplicação
python executar_aplicacao.py

:end
echo.
pause