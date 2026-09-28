#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REROUTE-T1T2 · MUTACAO: planta um defeito de cada vez (D130 e regua T5 C1) e prova que os testes o apanham.

    python3 provas/reroute_t1t2/mutar_reroute_t1t2.py [--saida=provas/reroute_t1t2/MUTACAO-REROUTE-T1T2.json]

O mesmo mecanismo de `provas/reroute_d56/mutar_reroute_d56.py` (que continua a valer para a D56): cada
mutante troca UM trecho (que tem de existir UMA vez), corre os testes, repoe o ficheiro e confere o sha256.
Corre `tests.test_reroute_t1t2_d130` e `tests.test_reroute_d56` juntos.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "reroute_d56"))
import mutar_reroute_d56 as M  # noqa: E402 — o mecanismo, sem copia

AD, OQ, RR = M.AD, M.OQ, M.RR
M.TESTE = "tests.test_reroute_t1t2_d130 tests.test_reroute_d56"
M.SAIDA = os.path.join(AQUI, "MUTACAO-REROUTE-T1T2.json")
M.DATASET = "MUTACAO-REROUTE-T1T2-V1"
M.MUTANTES = [
    # ── D130: o escopo ──
    ("D01", AD, 'REROUTE_NA_SALA_D130 = frozenset({"T1", "T2"})',
     'REROUTE_NA_SALA_D130 = frozenset({"T1", "T2", "T3"})',
     "T3 entra na Sala por reroute (o ramo antigo)"),
    ("D02", AD, 'REROUTE_NA_SALA_D130 = frozenset({"T1", "T2"})',
     'REROUTE_NA_SALA_D130 = frozenset({"T1", "T2", "T10"})',
     "T10 entra na Sala por reroute"),
    ("D03", AD, 'REROUTE_NA_SALA_D130 = frozenset({"T1", "T2"})', "REROUTE_NA_SALA_D130 = REROUTE_PROMOVE",
     "o escopo volta a ser a regua medida (T1, T2, T3, T10)"),
    ("D04", AD, "    if universo not in REROUTE_NA_SALA_D130:\n", "    if False:\n",
     "julgar_reroute deixa de anotar: T3/T10 dizem SIM"),
    ("D05", AD, "    return d.resultado == SIM and d.universo in REROUTE_NA_SALA_D130",
     "    return d.resultado == SIM",
     "a segunda trava cai: uma SIM fora do escopo chega a Sala"),
    ("D06", AD, "        ev[\"fora_do_escopo_d130\"] = True\n        return NAO_SEI, (",
     "        ev[\"fora_do_escopo_d130\"] = True\n        return NAO, (",
     "fora do escopo vira NAO (rejeicao) em vez de anotar"),
    ("D07", AD, "        ev[\"sim_da_regua\"] = True\n        ev[\"fora_do_escopo_d130\"] = True\n",
     "        ev.pop(\"trechos\", None)\n        ev[\"sim_da_regua\"] = True\n        ev[\"fora_do_escopo_d130\"] = True\n",
     "a anotacao perde o trecho"),
    ("D08", RR, "            if r == adm.SIM and adm.REROUTE_ENTRA_NA_SALA and u in adm.REROUTE_NA_SALA_D130:",
     "            if r in (adm.SIM, adm.NAO_SEI) and adm.REROUTE_ENTRA_NA_SALA and ev.get(\"sim_da_regua\") is not False:",
     "o reprocesso da gaveta ao que so foi anotado"),
    ("D09", OQ, "        d = adm.principal(ds)",
     "        d = ds[0] if ds[0].resultado == adm.SIM else next((x for x in ds[1:] if x.resultado == adm.SIM or (x.evidencia or {}).get(\"sim_da_regua\")), None)",
     "pela_porta pousa o que a regua disse SIM mesmo anotado"),
    # ── T5 C1 ──
    ("T01", AD, "REGUA_T5_EXIGE_AGRO = False", "REGUA_T5_EXIGE_AGRO = True",
     "a regua T5 C1 ligada por omissao (antes de o dono ver o replay)"),
    ("T02", AD, '    r, motivo, ev = _do_universo(item, "T5", palavras, lingua=lingua, inicio_de_palavra=True)',
     '    r, motivo, ev = _do_universo(item, "T5", palavras, lingua=lingua)',
     "C1 sem inicio de palavra: «tesi» dentro de «attesi» volta a contar"),
    ("T03", AD, '    if not (agro["cultura"] or agro["praga"]):', "    if False:",
     "C1 sem assunto agro: a ENEA volta a entrar"),
    ("T04", AD, "    texto, como = _texto_do_reroute(item)          # o mesmo corte do reroute: HTML -> corpo",
     "    texto, como = item.get(\"texto\"), \"TEXTO_INTEIRO\"",
     "o termo agro do MENU conta"),
    ("T05", AD, "    if texto is None and sem_corpo == \"TEXTO_INTEIRO\":",
     "    if texto is None:",
     "pagina HTML sem corpo cai para o texto inteiro (menu) em silencio"),
    ("T06", AD, "            \"entra; tambem nao e rejeitada (fica NAO_SEI).\" % (motivo, VERSAO_DA_REGUA_T5)), ev",
     "            \"entra; tambem nao e rejeitada (fica NAO_SEI).\" % (motivo, VERSAO_DA_REGUA_T5)), ev\n"
     "    return NAO, \"x\", ev",
     "com assunto agro, C1 rejeita (NAO) em vez de admitir"),
    ("T07", AD, '    if universo == "T5" and REGUA_T5_EXIGE_AGRO:', '    if universo in ("T5", "T3") and REGUA_T5_EXIGE_AGRO:',
     "C1 escorrega para outro universo (T3)"),
]

if __name__ == "__main__":
    raise SystemExit(M.main(sys.argv[1:]))
