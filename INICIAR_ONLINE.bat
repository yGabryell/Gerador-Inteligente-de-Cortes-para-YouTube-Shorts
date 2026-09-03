@echo off
title GravitiCuts AI - Iniciar Online (Zero 403)
color 0b
cd /d "%~dp0"

echo ======================================================================
echo           INICIANDO GRAVITICUTS AI EM MODO ONLINE SEGURO
echo ======================================================================
echo Aguarde alguns segundos enquanto o servidor e o link sao gerados...
echo.

python run_online.py

if errorlevel 1 (
    echo.
    echo Ocorreu um erro ao executar. Pressione qualquer tecla para sair.
    pause >nul
)
