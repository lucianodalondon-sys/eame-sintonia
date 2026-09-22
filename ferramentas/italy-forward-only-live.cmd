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
REM
REM  ⚠️ CORRIGIDO EM 2026-09-22 (cutover, Fase 8). Este ficheiro chamava
REM  `node scripts\italy_recurrent_collect.mjs`, e o coletor ja nao vive em
REM  `scripts\` — vive em `coleta\`. Medido: o ficheiro apontado NAO EXISTIA,
REM  e a tarefa agendada passou a devolver `Ultimo resultado: 1`.
REM
REM      UM LANCADOR QUE APONTA PARA UM FICHEIRO QUE NAO EXISTE
REM      FALHA DE HORA EM HORA SEM COLHER NADA E SEM DIZER PORQUE.
REM
REM  A tarefa tambem apontava para `scripts\italy-forward-only-live.cmd`, que
REM  desapareceu no mesmo movimento. Passou a apontar para ESTE ficheiro.
REM  Cadencia mantida: de hora em hora, como estava desde 2026-09-07.
REM ============================================================================
setlocal
set ITALY_OPS_ROOT=C:\eame-sintonia-ops
cd /d %ITALY_OPS_ROOT%
node coleta\italy_recurrent_collect.mjs --profile forward-only-live --gate-hour
exit /b %ERRORLEVEL%
