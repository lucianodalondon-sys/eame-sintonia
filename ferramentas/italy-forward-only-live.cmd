@echo off
REM ============================================================================
REM  SINTONIA · ITALIA · COLETA FORWARD-ONLY
REM
REM  Chamado pelo Agendador de Tarefas do Windows. NAO contem logica de coleta:
REM  so aponta para o entrypoint canonico.
REM
REM  O gatilho dispara DE HORA EM HORA. Quem decide se e hora de coletar e o
REM  proprio coletor, com --gate-hour, comparando o relogio de Europe/Rome.
REM  Isso e de proposito: o Agendador do Windows NAO tem fuso por tarefa, e a
REM  maquina esta no fuso do Brasil. Deixar o fuso no codigo sobrevive ao
REM  horario de verao dos dois paises; deixar no agendador, nao.
REM
REM  Para remover o agendamento:
REM     schtasks /Delete /TN "SINTONIA-Italy-ForwardOnly" /F
REM ============================================================================
setlocal
set ITALY_OPS_ROOT=C:\eame-sintonia-ops
cd /d %ITALY_OPS_ROOT%
node scripts\italy_recurrent_collect.mjs --profile forward-only-live --gate-hour
exit /b %ERRORLEVEL%
