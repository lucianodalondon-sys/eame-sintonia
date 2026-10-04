"""SOC-ONDA2 · PASSOS 1-2 EM CÓPIA — o worker qualifica as sociais e escreve os contratos.

    py curadoria/social_onda2_ensaio.py --copia        # só numa CÓPIA dos livros vivos
    py curadoria/social_onda2_ensaio.py --copia --json SAIDA

Enfileira QUALIFY para cada candidata YouTube/LinkedIn/Instagram sem SOURCE_ID e
deixa o WORKER da casa fazer o resto, pela ordem dele: QUALIFY → BUILD_CONTRACT →
VALIDATE_ROUTE. Nada aqui decide identidade, território ou rota — só enfileira e
conta o que o worker fez.

⚠️ RECUSA correr na árvore do bot vivo ou na ponte viva (um escritor no vivo:
só o coordenador instala). `--copia` é a declaração de quem chama; a guarda
confere o caminho na mesma.

Sem rede: a validação da rota do Scrap lê a matriz dele, e o canário da rota
social é uma corrida do orquestrador, não do worker (para em CANARY_PENDING).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas"):
    sys.path.insert(0, str(RAIZ / _p))

VIVOS = ("source-curator-service-v1", "ponte-viva")
TIPOS = ("YOUTUBE", "LINKEDIN", "INSTAGRAM")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--copia", action="store_true", help="declaro que esta arvore e uma copia")
    ap.add_argument("--json")
    a = ap.parse_args()
    if not a.copia or any(v in str(RAIZ).replace("\\", "/") for v in VIVOS):
        print("RECUSADO: so corre numa copia dos livros (--copia), nunca em %s" % ", ".join(VIVOS))
        return 2

    import fila as F
    import fonte_nova as FN
    import lifecycle as LC
    import worker as W

    doc = FN.carregar()
    sociais = {c["CANDIDATA_ID"]: c for c in doc["CANDIDATAS"]
               if c.get("TIPO") in TIPOS and not c.get("SOURCE_ID")}
    alloc_antes = {n["SOURCE_ID"] for n in W._ler_alloc().get("NOVAS", [])}
    ready_antes = sum(1 for e in LC.snapshot().values() if e == LC.READY_FOR_COLLECTION)
    for cid in sociais:
        F.enfileirar(cid, F.QUALIFY, priority=30, motivo="SOC-ONDA2: social com identidade a medir")

    feitos = W.correr(max_tarefas=0, pausa=0, verboso=False)

    por_cand = {}
    for r in feitos:
        if r.get("TASK_TYPE") == F.QUALIFY and r["SOURCE_ID"] in sociais:
            por_cand[r["SOURCE_ID"]] = r
    ev = json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"]
    ult = {}
    for p in ev:
        if p["ETAPA"] == F.QUALIFY and p["SOURCE_ID"] in sociais:
            ult[p["SOURCE_ID"]] = p["DADOS"]
    novas = [n for n in W._ler_alloc().get("NOVAS", []) if n["SOURCE_ID"] not in alloc_antes]
    contratos = W._contratos()
    linhas = []
    for cid, c in sociais.items():
        r = por_cand.get(cid, {})
        d = ult.get(cid, {})
        sid = d.get("SOURCE_ID_REAL")
        linhas.append({
            "CANDIDATA_ID": cid, "TIPO": c["TIPO"], "URL": c.get("URL"),
            "QUALIFY": r.get("RESULTADO"), "CLASSE": d.get("CLASSE"),
            "PORQUE": (r.get("PORQUE") or d.get("PORQUE") or "")[:220],
            "SOURCE_ID": sid, "SOURCE_ID_NOVO": d.get("SOURCE_ID_NOVO"),
            "TERRITORIO": d.get("TERRITORY"),
            "ESTADO_DA_FONTE": LC.estado_de(sid) if sid else LC.estado_de(cid),
            "FASE_DO_SCRAP": ((contratos.get(sid) or {}).get("ACQUISITION") or {}).get("FASE") if sid else None,
        })
    resumo = {
        "SOCIAIS": len(sociais),
        "TAREFAS_EXECUTADAS": dict(Counter("%s:%s" % (r.get("TASK_TYPE"), r.get("RESULTADO")) for r in feitos)),
        "QUALIFY_POR_TIPO": {t: dict(Counter(l["QUALIFY"] for l in linhas if l["TIPO"] == t)) for t in TIPOS},
        "NUMEROS_NOVOS": len(novas),
        "NUMEROS_NOVOS_POR_TIPO": dict(Counter(n["FAMILY"] for n in novas)),
        "JA_ERAM_FONTE": sum(1 for l in linhas if l["SOURCE_ID"] and l["SOURCE_ID_NOVO"] is False),
        "ESTADO_DOS_NOVOS": dict(Counter(LC.estado_de(n["SOURCE_ID"]) for n in novas)),
        "CONTRATOS_SCRAP_NOVOS": dict(Counter(((contratos.get(n["SOURCE_ID"]) or {}).get("ACQUISITION") or {})
                                              .get("FASE") for n in novas)),
        "BLOQUEIOS": dict(Counter("%s:%s" % (l["TIPO"], l["CLASSE"]) for l in linhas if l["QUALIFY"] == "BLOCK")),
        "READY_ANTES": ready_antes,
        "READY_DEPOIS": sum(1 for e in LC.snapshot().values() if e == LC.READY_FOR_COLLECTION),
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps({"DATASET": "SOC-ONDA2-ENSAIO-QUALIFY-V1",
                                            "RESUMO": resumo, "NOVAS": novas, "LINHAS": linhas},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
