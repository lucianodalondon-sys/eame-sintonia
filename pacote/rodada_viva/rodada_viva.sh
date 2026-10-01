#!/usr/bin/env bash
# RODADA VIVA DA INTELLIGENCE (dono 30/09 ~19:00: «Sala viva -> Intelligence -> C8 -> PARA-O-CASCO-AUTO, tudo automatico»)
# Uma volta por chamada (tarefa agendada SINTONIA-INTELLIGENCE-VIVA, acorda a cada 30 min). Nao escreve na Sala:
# copia so-leitura, nunca marca consumido_em (D140). Codigo = commits PUBLICADOS em worktrees destacadas e limpas.
#
# CADENCIA (o agendador acorda) != REGRA DE DISPARO (o que manda processar) — dono 30/09 22h, item 9, regra D90-5:
#   CORTE  = MANIFESTO.COPIA_DA_SALA.EM da entrega em PARA-O-CASCO-AUTO (o que a Intelligence provadamente viu).
#   NOVOS  = linhas da sala_de_espera com pousado_em > CORTE  +  revisoes com revisto_em > CORTE.
#   DISPARA se  NOVOS >= 10  (LOTE)   ou   NOVOS >= 1 e o mais velho espera >= 4 h  (ESPERA)
#           ou  o codigo do motor mudou (MANIFESTO.SOURCE_HEAD != HEAD do MOTOR)  (CODIGO_NOVO: nunca REUSED falso).
#   Senao   -> SEM_DISPARO (ou IGUAL, se nada mudou), e a volta acaba.
#   Mudanca na impressao sem linha nova datada conta como 1 item desde a 1a vez vista (VISTO-DESDE).
# Passos do disparo: copia RO (mesmo exportar.sql) -> produtor de afirmacoes -> C8 (liberacao_por_criterio) ->
#   troca atomica de PARA-O-CASCO-AUTO (a pasta que SINTONIA-CASCO-PREVIEW le). Falha = entrega anterior intacta.
# DESLIGAR: criar  $SI/intelligence-experimental/PARAR-RODADA-VIVA
set -u
SI=C:/Users/London1/sintonia-sala-italia
IE=$SI/intelligence-experimental
MOTOR=C:/g/int-viva-c5db5eedd            # claude/int-rota-natureza-v1 @ c5db5eedd (publicado; CAP-SCI P1/1B, 204->106; ordem do coordenador 01/10)
PRODUTOR=C:/Users/London1/orca/workspaces/eame-sintonia/io-produtor-197641c   # 197641c2b (familia do C8 provado)
ENTREGA=$IE/PARA-O-CASCO-AUTO
ESTADO=$IE/RODADA-VIVA-ESTADO.txt
VISTO=$IE/RODADA-VIVA-VISTO-DESDE.txt
LOG=$IE/RODADA-VIVA.log
LOTE=${LOTE:-10}; ESPERA_S=${ESPERA_S:-14400}
PY=C:/Users/London1/AppData/Local/Programs/Python/Launcher/py.exe
export PATH="/usr/bin:/mingw64/bin:/c/Program Files/Git/cmd:$PATH"
PSQL=C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe
export PGPASSFILE=$SI/pgpass.conf PGCLIENTENCODING=UTF8 PYTHONUTF8=1
log(){ echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }
[ -e "$IE/PARAR-RODADA-VIVA" ] && { log "PARADO (bandeira)"; exit 0; }
TR="$IE/RODADA-VIVA.trinco.d"          # mkdir e atomico; trinco com mais de 3 h = volta morta, retoma-se
if ! mkdir "$TR" 2>/dev/null; then
  if [ -n "$(find "$TR" -maxdepth 0 -mmin +180 2>/dev/null)" ]; then log "TRINCO velho (>3h) retomado"; else log "OCUPADO"; exit 0; fi
fi
trap 'rm -rf "$TR"' EXIT
for w in "$MOTOR" "$PRODUTOR"; do
  [ -z "$(git -C "$w" status --porcelain)" ] || { log "RECUSADO arvore suja $w"; exit 3; }
done
HEAD_MOTOR=$(git -C "$MOTOR" rev-parse HEAD)
DSN="$(cat $SI/SALA_DSN.txt)"
# o que a entrega atual provadamente viu (sem entrega valida: CORTE vazio -> dispara)
read -r CORTE HEAD_ENTREGUE < <("$PY" -3 -c "
import json,sys
try:
    m=json.load(open(sys.argv[1],encoding='utf-8')); print(m['COPIA_DA_SALA']['EM'].replace(' ','T'), m['SOURCE_HEAD'])
except Exception: print('- -')" "$ENTREGA/MANIFESTO.json" 2>/dev/null | grep -v platform | tr -d '\r')
[ "${CORTE:--}" = "-" ] && CORTE=""
Q="begin transaction read only;
select 'IMP|'||(select count(*)||':'||encode(sha256(convert_to(coalesce(string_agg(md5(row_to_json(t)::text), ',' order by t.run_id, t.ordem),''),'UTF8')),'hex') from public.sala_de_espera t)
  ||'+'||(select count(*)||':'||encode(sha256(convert_to(coalesce(string_agg(md5(row_to_json(t)::text), ',' order by t.run_id, t.ordem, t.campo, t.revisao),''),'UTF8')),'hex') from public.sala_de_espera_revisao t);"
if [ -n "$CORTE" ]; then
  Q="$Q
select 'NOV|'||count(*)||'|'||coalesce(extract(epoch from now()-min(q.em))::bigint::text,'') from (
  select pousado_em em from public.sala_de_espera where pousado_em > '$CORTE'::timestamptz
  union all select revisto_em from public.sala_de_espera_revisao where revisto_em > '$CORTE'::timestamptz) q;"
fi
OUT=$("$PSQL" -w -X -q -A -t -c "$Q commit;" "$DSN" 2>>"$LOG" | tr -d '\r')
IMP=$(echo "$OUT" | sed -n 's/^IMP|//p')
[ -n "$IMP" ] || { log "NAO_SEI impressao da Sala nao medida"; exit 1; }
NOVOS=$(echo "$OUT" | sed -n 's/^NOV|\([0-9]*\)|.*/\1/p'); IDADE=$(echo "$OUT" | sed -n 's/^NOV|[0-9]*|//p')
NOVOS=${NOVOS:-0}
MESMO_CODIGO=0; [ "$HEAD_MOTOR" = "${HEAD_ENTREGUE:-}" ] && MESMO_CODIGO=1
if [ $MESMO_CODIGO = 1 ] && [ -f "$ESTADO" ] && [ "$(cat "$ESTADO")" = "$IMP" ]; then rm -f "$VISTO"; log "IGUAL $IMP"; exit 0; fi
if [ "$NOVOS" = 0 ] && [ -n "$CORTE" ]; then         # mudou sem linha nova datada: espera desde a 1a vez vista
  [ -f "$VISTO" ] || date +%s > "$VISTO"
  NOVOS=1; IDADE=$(( $(date +%s) - $(cat "$VISTO") ))
fi
IDADE=${IDADE:-0}
if [ -z "$CORTE" ]; then MOTIVO="SEM_ENTREGA_VALIDA"
elif [ $MESMO_CODIGO = 0 ]; then MOTIVO="CODIGO_NOVO ${HEAD_ENTREGUE:0:9}->${HEAD_MOTOR:0:9}"
elif [ "$NOVOS" -ge "$LOTE" ]; then MOTIVO="D90-5_LOTE novos=$NOVOS"
elif [ "$NOVOS" -ge 1 ] && [ "$IDADE" -ge "$ESPERA_S" ]; then MOTIVO="D90-5_ESPERA novos=$NOVOS espera=${IDADE}s"
else log "SEM_DISPARO novos=$NOVOS espera=${IDADE}s (regra D90-5: >=$LOTE ou >=1 e >=${ESPERA_S}s) corte=$CORTE"; exit 0; fi
log "DISPARO $MOTIVO corte=$CORTE"
[ -n "${SO_DECIDIR:-}" ] && { log "SO_DECIDIR: nao processa (ensaio da regra)"; exit 0; }
TS=$(date -u +%Y%m%dT%H%M%SZ); D=$IE/SALA-VIVA-$TS; mkdir -p "$D/copia"
echo "$MOTIVO" > "$D/MOTIVO_DO_DISPARO.txt"
cp "$IE/AFIRMACOES-SALA309-20260930T113403Z/copia/exportar.sql" "$D/copia/"
( cd "$D/copia" && "$PSQL" -w -X -q -f exportar.sql "$DSN" > psql.out 2>&1 ) || { log "ERRO copia $D"; exit 1; }
[ "$(head -1 "$D/copia/PROVA_RO.txt" | tr -d '\r')" = on ] && [ "$(head -1 "$D/copia/PROVA_RO_FIM.txt" | tr -d '\r')" = on ] || { log "ERRO copia sem prova RO"; exit 1; }
log "COPIA $D $(sha256sum "$D/copia/SALA_ATUAL.json" | cut -c1-16) sala=$IMP"
date -u +%FT%TZ > "$D/INICIO.txt"
( cd "$PRODUTOR" && "$PY" -3 admissao/produtor_de_afirmacoes.py "$D/copia/SALA_ATUAL.json" "$D/AFIRMACOES.json" > "$D/produtor.out.txt" 2>&1 ) || { log "ERRO produtor $D"; exit 1; }
( cd "$MOTOR" && "$PY" -3 pacote/liberacao_por_criterio.py --copia "$D/copia" --afirmacoes "$D/AFIRMACOES.json" \
    --armazem "$SI/armazem" --entrega "$ENTREGA" --produtor "$PRODUTOR" > "$D/c8.out.txt" 2>&1 ) || { log "ERRO C8 $D (entrega anterior intacta)"; exit 1; }
date -u +%FT%TZ > "$D/FIM.txt"
( cd "$ENTREGA" && sha256sum -c SHA256SUMS.txt >> "$D/c8.out.txt" 2>&1 ) || { log "ERRO SHA256SUMS da entrega"; exit 1; }
echo "$IMP" > "$ESTADO"; rm -f "$VISTO"
rm -f "$D/AFIRMACOES.json.gz"; ls -t -d "$IE"/SALA-VIVA-* | tail -n +4 | while read old; do rm -f "$old/AFIRMACOES.json"; done
log "ENTREGUE $D $MOTIVO $(tr -d '\n ' < "$D/c8.out.txt" | cut -c1-300)"
