@echo off
echo ========================================================
echo Enviando projeto para o GitHub (yGabryell/cortes-ia)...
echo ========================================================
set PATH=C:\Users\gabriel.silva\AppData\Local\Programs\Git\cmd;%PATH%
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCESSO] Projeto enviado para o GitHub com sucesso!
) else (
    echo [AVISO] Se solicitou login, faca a autenticacao na janela do navegador.
)
echo.
pause
