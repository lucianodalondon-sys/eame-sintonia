# -*- coding: utf-8 -*-
"""PORTA-DA-SALA-RENDE · ataque de mutacao a proposta, numa COPIA (worktree destacada).

    py scripts/porta_sala_rende/mutar_porta_sala_rende.py <caminho-da-copia> [saida.json]

Cada mutante estraga UMA decisao da proposta em admissao/admissao.py; os testes
(tests/test_porta_sala_rende.py) tem de o matar (FAIL/ERROR novo). O original e reposto
no fim. Rede fechada (proxy morto). PYTHONDONTWRITEBYTECODE=1.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
SAIDA = sys.argv[2] if len(sys.argv) > 2 else None
F = os.path.join(R, "admissao", "admissao.py")
M = [
    ("nasce_ligada", "\nPORTA_SALA_RENDE_LIGADA = False\n", "\nPORTA_SALA_RENDE_LIGADA = True\n"),
    ("moldura_nunca_aplicada", "    return dict(item, texto=c), dict(ev, aplicada=True)",
     "    return item, dict(ev, aplicada=True)"),
    ("julga_o_corpo_vazio", "    if len(c.strip()) < CORPO_MINIMO_DA_MOLDURA:",
     "    if False:"),
    ("moldura_tambem_em_pdf",
     '    if not item.get("retrato_do_detector") or not str(item.get("texto") or "").strip():\n'
     '        return item, {"aplicada": False',
     '    if not str(item.get("texto") or "").strip():\n        return item, {"aplicada": False'),
    ("nao_com_um_sinal",
     "    if nao_com_dois and noutros and not any(len(w) >= SINAIS_MINIMOS for w in noutros.values()):",
     "    if False:"),
    ("nao_com_dois_vira_tres",
     "    if nao_com_dois and noutros and not any(len(w) >= SINAIS_MINIMOS for w in noutros.values()):",
     "    if nao_com_dois and noutros and not any(len(w) >= SINAIS_MINIMOS + 1 for w in noutros.values()):"),
    ("psr_nao_transversal", "    transversais = TRANSVERSAIS | frozenset(extra)",
     "    transversais = TRANSVERSAIS"),
    ("psr_por_pedaco", "    palavra_inteira = PALAVRA_INTEIRA | frozenset(extra)",
     "    palavra_inteira = PALAVRA_INTEIRA"),
    ("secao_desligada", '    if r == SIM and "SECAO" in PORTA_SALA_RENDE_PECAS:',
     "    if False:"),
    ("secao_ignora_algarismos", "    if any(ch.isdigit() for ch in ultimo):\n        return None",
     "    if False:\n        return None"),
    ("sim_sem_trecho", '        if not ev["trechos"]:', "        if False:"),
    ("t8_liga_o_nao_com_dois", 'nao_com_dois="NAO_COM_DOIS_SINAIS" in PORTA_SALA_RENDE_PECAS,',
     "nao_com_dois=True,"),
    ("t8_ignora_a_peca",
     '    return {u: fonte[u] for u in ("T8", "T12") if u in PORTA_SALA_RENDE_PECAS}',
     '    return {u: fonte[u] for u in ("T8", "T12")}'),
    ("t12_com_nome_de_ministerio", '    "T12": ["politica agricola comune|politica agricola comunitaria|pac",',
     '    "T12": ["politica agricola comune|politica agricola comunitaria|pac|politiche agricole|masaf",'),
    ("t12_sem_emendamento", '            "emendamento|emendamenti",\n', ""),
    ("lingua_do_corpo", "        lingua=_lingua_do_item(item))", "        lingua=None)"),
    ("desligada_usa_a_proposta", "        return _do_universo_regua(item, universo, palavras)\n    return _porta_sala_rende",
     "        return _porta_sala_rende(item, universo, palavras)\n    return _porta_sala_rende"),
]
orig = open(F, encoding="utf-8", newline="").read()
nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", HTTP_PROXY="http://127.0.0.1:9",
           HTTPS_PROXY="http://127.0.0.1:9")
res = {}
try:
    p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_porta_sala_rende"],
                       cwd=R, env=env, capture_output=True, text=True, timeout=600)
    res["_ORIGINAL"] = {"RC": p.returncode}
    assert p.returncode == 0, p.stderr[-2000:]
    for nome, a, b in M:
        a, b = a.replace(chr(10), nl), b.replace(chr(10), nl)
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_porta_sala_rende"],
                           cwd=R, env=env, capture_output=True, text=True, timeout=600)
        falhas = sorted({l.split(" ")[1] for l in p.stderr.splitlines()
                         if l.startswith(("FAIL:", "ERROR:"))})
        res[nome] = {"RESULTADO": "MORTO" if falhas else "SOBREVIVEU", "QUEDAS": falhas,
                     "EXECUTOU": "Ran " in p.stderr}
        print(nome, res[nome]["RESULTADO"], len(falhas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
mortos = sum(1 for k, v in res.items() if not k.startswith("_") and v["RESULTADO"] == "MORTO")
print("mortos %d/%d" % (mortos, len(M)))
if SAIDA:
    with open(SAIDA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"MUTANTES": len(M), "MORTOS": mortos, "RESULTADOS": res}, fh,
                  ensure_ascii=False, indent=1)
        fh.write("\n")
sys.exit(0 if mortos == len(M) else 1)
