@echo off
rem SINTONIA-CASCO-PREVIEW (D156, coordenador 29/09) - UMA RODADA do gatilho do preview.
rem A tarefa agendada do Windows SINTONIA-CASCO-PREVIEW chama este ficheiro a cada 10 minutos.
rem Ela publica SO no PREVIEW, e so quando o MANIFESTO/SHA256SUMS de PARA-O-CASCO/ mudou e conferem.
rem
rem   DESLIGAR (bandeira): criar o ficheiro  %SINTONIA_CASCO%\estado\PARAR   -> cada rodada diz PARADO e nao publica
rem   RELIGAR:             apagar esse ficheiro
rem   PAUSAR A TAREFA:     schtasks /change /tn SINTONIA-CASCO-PREVIEW /disable     (voltar: /enable)
rem   REMOVER A TAREFA:    schtasks /delete /tn SINTONIA-CASCO-PREVIEW /f
rem   VER O REGISTO:       %SINTONIA_CASCO%\estado\RODADAS.ndjson  (uma linha por rodada)  e  tarefa.log
rem   O PREVIEW ATUAL:     %SINTONIA_PREVIEW_ATUAL% (URL, deployment, os dois sha do pote) - o LAB le daqui
rem
rem Producao: nao existe caminho. O gatilho so aceita --modo ensaio/preview (recusa producao antes do publicador),
rem e o implantador do preview publica num endereco de deployment, nunca no CANONICAL_HOST.
setlocal
if not defined SINTONIA_CASCO set "SINTONIA_CASCO=%USERPROFILE%\sintonia-casco-preview"
if not exist "%SINTONIA_CASCO%\estado" mkdir "%SINTONIA_CASCO%\estado"
if not defined SINTONIA_PREVIEW_ATUAL set "SINTONIA_PREVIEW_ATUAL=%USERPROFILE%\auditoria-madrugada\PREVIEW-ATUAL.json"
set "PATH=%SINTONIA_CASCO%\venv\Scripts;%ProgramFiles%\nodejs;%APPDATA%\npm;%ProgramFiles%\Git\cmd;%PATH%"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
set "PYTHONDONTWRITEBYTECODE=1"
cd /d "%~dp0.."
python3 portoes\publicar_preview_da_pasta.py --rodada --modo preview --estado "%SINTONIA_CASCO%\estado" --preview-atual "%SINTONIA_PREVIEW_ATUAL%" >> "%SINTONIA_CASCO%\estado\tarefa.log" 2>&1
endlocal
