#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutacao do condutor da MICRO SOCIAL: 20 mutantes, cada um confirmado por git diff; corre
tests/test_micro_social.py e repoe o ficheiro.  py ferramentas/micro_social/_mutantes_micro_social.py"""
import io,subprocess,sys,os
F="ferramentas/micro_social/micro_social.py"
M=[
 ("M1 sem autorizacao corre","    if not autorizado:\n        return {\"CORREU\": False, \"PORQUE\": \"falta --autorizado-pelo-dono\"}\n","    if False:\n        pass\n"),
 ("M2 lote 1 ignorado","    if falta_lote:\n        return","    if False:\n        return"),
 ("M3 flag de parada ignorada","    if flag.exists():\n","    if False:\n"),
 ("M4 robo nao conferido","    ok, porque = parado()\n","    ok, porque = True, ''\n"),
 ("M5 sala nao conferida","    falta = sala()\n    if falta:","    falta = []\n    if falta:"),
 ("M6 egresso antes ignorado","    if antes.get(\"GATE\") != \"PASS\":\n        return","    if False:\n        return"),
 ("M7 prova so da rodada","    ids = [f[\"RUN_ID\"] for f in estado[\"FONTES\"]]\n","    ids = [c[\"RUN_ID\"] for c in corridas if c.get(\"RUN_ID\") not in (None, AUSENCIA)]\n"),
 ("M8 NAO_SEI passa","    if prova.get(\"ESTADO\") != \"PASS\":\n","    if prova.get(\"ESTADO\") == \"FAIL\":\n"),
 ("M9 egresso depois ignorado","    if depois.get(\"GATE\") != \"PASS\":\n        parar","    if False:\n        parar"),
 ("M10 flag nao escrita","    if parar:\n        flag.write_text","    if False:\n        flag.write_text"),
 ("M11 duracao sem limite","        elif d > DURACAO_MAXIMA_S:\n","        elif False:\n"),
 ("M12 teto livre","        if int(it.get(\"TETO\") or 0) != 1:\n","        if False:\n"),
 ("M13 gate ignorado","        if not g.get(\"COLLECTION_ELIGIBLE\"):\n","        if False:\n"),
 ("M14 sala: valor sem base passa","            if l.get(c) not in DESCONHECIDO and l.get(c + \"_BASIS\") in DESCONHECIDO:\n","            if False:\n"),
 ("M15 sala: fact_time fabricado passa","        if l.get(\"FACT_TIME\") not in DESCONHECIDO and l.get(\"FACT_TIME\") == l.get(\"CAPTURED_AT\"):\n","        if False:\n"),
 ("M16 sala: run_id sem forma","        if not re.fullmatch(r\"[A-Z]{2}-T\d+-[0-9-]+-[0-9a-f]{16}\", i):\n","        if False:\n"),
 ("M17 lote1: D41 nao exigida","    if not _tem(\"provas/prova_teto_dominio.py\", '\"googlevideo.com\": \"youtube.com\"'):\n","    if False:\n"),
 ("M18 sem RUN_ID nao para","    if corridas_falhadas:\n","    if False:\n"),
 ("M19 yt-dlp nao conferido","        if not ok_yt:\n","        if False:\n"),
 ("M20 yt-dlp conferido sempre","    if any(it.get(\"FASE\") == \"audio-youtube\" for it in rodadas[0].get(\"ITENS\", [])):\n","    if True:\n"),
]
orig=io.open(F,encoding="utf-8",newline="").read()
env=dict(os.environ,PYTHONUTF8="1")
try:
  for nome,a,b in M:
    s=orig.replace("\r\n","\n")
    if s.count(a)!=1: print(nome,"NAO_APLICOU",s.count(a)); continue
    io.open(F,"w",encoding="utf-8",newline="").write(s.replace(a,b))
    d=subprocess.run(["git","diff","--quiet","--",F]).returncode
    r=subprocess.run([sys.executable,"-m","unittest","tests.test_micro_social"],capture_output=True,text=True,env=env,timeout=600)
    print(nome,"MORTO" if r.returncode!=0 else "SOBREVIVEU","(diff ok)" if d==1 else "(SEM DIFF!)")
finally:
  io.open(F,"w",encoding="utf-8",newline="").write(orig)
