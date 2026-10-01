#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTANTES DA DT-FATO-OBSERVADO (§5-D) contra o G0 do Intelligence owner (origin/claude/c8-auto-v1 @ d02e62489).

Escrito pela L2 FORA do ramo do owner (nao se commita no ramo de outro dono). Corre numa worktree destacada:

    py mutantes_dt_fato_observado.py <worktree em d02e62489>   ->  MUTANTES-DT-FATO-OBSERVADO.json (ao lado)

Cada mutante desliga UMA guarda do §5-D (ou do §1/§5-C que a DT cita) e tem de fazer
tests.test_g0_da_afirmacao REPROVAR. Mesmo harness de provas/l2/mutantes.py (alvo unico, restauro por SHA-256).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RAIZ / "provas" / "l2"))
from mutantes import aplicar, sha  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "MUTANTES-DT-FATO-OBSERVADO.json"
TESTE = "tests.test_g0_da_afirmacao"
G0 = "motor/g0_da_afirmacao.py"
MOT = "motor/motor_das_capacidades.py"

MUTANTES = [
    # (id, ficheiro, o mutante da DT que finge, velho, novo)
    ("D1", G0, "retirar a marca: bloco MARCA_DE_MEDICAO ausente aceite",
     '        falta.append("MARCA_DE_MEDICAO:AUSENTE")', "        pass"),
    ("D2", G0, "retirar a marca: verbo/valor sem posicao aceites",
     '                falta.append("MARCA_DE_MEDICAO:%s_SEM_POSICAO" % parte)', "                pass"),
    ("D3", G0, "ancora do campo como marca: vocabulario da marca desligado",
     '            elif not forma.fullmatch(m["TRECHO"].strip()):', "            elif False:"),
    ("D4", G0, "evento futuro («saranno registrati») aceite como medicao",
     '                falta.append("MARCA_DE_MEDICAO:VERBO_NO_FUTURO")', "                pass"),
    ("D5", G0, "ato regulatorio ou congresso no trecho: marca de outra classe aceite",
     "    if outras:", "    if False:"),
    ("D6", G0, "tempo = data de publicacao sem base no trecho aceite",
     "    return [] if _dentro(basis, span) else", "    return [] if True else"),
    ("D7", G0, "lugar = lugar da fonte (LOCATION_SOURCE != TEXT) aceite",
     '    elif lugar.get("LOCATION_SOURCE") != "TEXT":', "    elif False:"),
    ("D8", G0, "lugar sem posicao aceite",
     '        falta.append("FACT_LOCATION:SEM_POSICAO")', "        pass"),
    ("D9", G0, "lugar que nao esta no texto aceite",
     '    elif str(texto)[onde["INICIO"]:onde["FIM"]] != onde.get("TRECHO"):', "    elif False:"),
    ("D10", G0, "lugar fora do trecho aceite",
     "    elif not _dentro(onde, span):", "    elif False:"),
    ("D11", G0, "marca que nao bate com o texto aceite",
     '            elif str(texto)[m["INICIO"]:m["FIM"]] != m["TRECHO"]:', "            elif False:"),
    ("D12", G0, "marca fora do trecho aceite",
     "            elif not _dentro(m, span):", "            elif False:"),
    ("D13", G0, "sem texto para conferir aceite",
     '        return ["OBSERVACAO_MEDIDA:SEM_TEXTO_PARA_CONFERIR"]', "        return []"),
    ("D14", G0, "o §5-D inteiro desligado (OBSERVACAO_MEDIDA sem conferencia nenhuma)",
     "        falta += _observacao_medida(af, texto)", "        pass"),
    ("D15", G0, "misturar Europa 2004 com Italia 2012 (concorrencia desligada)",
     "    falta += _concorrentes(af)", "    pass"),
    ("D16", MOT, "o motor nao faz objeto de OBSERVACAO_MEDIDA (o controle bom morre)",
     '    return (sg.get("CLAIM_KIND") in ("ALERTA_EVENTO", "OBSERVACAO_MEDIDA")',
     '    return (sg.get("CLAIM_KIND") in ("ALERTA_EVENTO",)'),
]


def _correr():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", "-m", "unittest", TESTE], cwd=RAIZ, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=900, env=env)


def main() -> int:
    fs = sorted({m[1] for m in MUTANTES})
    antes = {f: sha(RAIZ / f) for f in fs}
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    base = _correr()
    out = {"ALVO": str(RAIZ), "HEAD": head, "TESTE": TESTE, "BASE_VERDE": base.returncode == 0, "MUTANTES": []}
    if base.returncode:
        out["ESTADO"] = "BASE_VERMELHA"
    else:
        for mid, f, finge, velho, novo in MUTANTES:
            p = RAIZ / f
            original = p.read_bytes()
            mutado, n = aplicar(original, velho, novo)
            if n != 1:
                out["MUTANTES"].append({"ID": mid, "FINGE": finge, "ESTADO": "ALVO_NAO_UNICO (%d)" % n})
                print(mid, "ALVO_NAO_UNICO", n, flush=True)
                continue
            try:
                p.write_bytes(mutado)
                r = _correr()
                quem = [l.split("(")[0].replace("FAIL: ", "").replace("ERROR: ", "").strip()
                        for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
                out["MUTANTES"].append({"ID": mid, "FICHEIRO": f, "FINGE": finge,
                                        "ESTADO": "MORTO" if r.returncode else "SOBREVIVEU", "APANHADO_POR": quem[:4]})
            finally:
                p.write_bytes(original)
            print(mid, out["MUTANTES"][-1]["ESTADO"], finge, flush=True)
        mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
        iguais = antes == {f: sha(RAIZ / f) for f in fs}
        out.update({"MORTOS": mortos, "TOTAL": len(MUTANTES), "RESTAURADOS_IGUAIS": iguais,
                    "ESTADO": "PASS" if mortos == len(MUTANTES) and iguais else "FAIL"})
        print("MORTOS %d/%d · restaurados iguais: %s" % (mortos, len(MUTANTES), iguais))
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0 if out.get("ESTADO") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
