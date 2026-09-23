"""Ensaio X1 — o observador da ponte contra uma pasta de bot de ENSAIO.

    py ferramentas/cutover/observador_ensaio.py <raiz da linha> <pasta do bot> <voltas>

A CLI do ponte_automatica nao tem --lane: LANE_DO_BOT esta escrito com a pasta viva. Sem este
involucro, um ensaio leria o bot VIVO. 1.a volta com forcar=True (como a B2 manda), depois servir().
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "curadoria"))
import ponte_automatica as PA
lane = Path(sys.argv[2])
r = PA.uma_volta(lane=lane, forcar=True)
print("VOLTA_1_FORCAR", json.dumps({k: r.get(k) for k in ("ACCAO", "LIVRO_CANONICO", "PROVAS_IMPORTADAS", "PORTAO", "ERRO")}, ensure_ascii=False)[:1500], flush=True)
PA.servir(intervalo=20, voltas=int(sys.argv[3]), lane=lane)
print("SAUDE", json.dumps(PA.saude(), ensure_ascii=False)[:600], flush=True)
