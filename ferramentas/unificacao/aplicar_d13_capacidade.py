"""D13 (3): candidata social SEM CAPACIDADE fica CAPABILITY_BLOCK, nao RECUSADA.

    py ferramentas/unificacao/aplicar_d13_capacidade.py [--escrever] [--porta FICHEIRO]

A ponte (curadoria/ponte_candidatas.py) escrevia RECUSADA para o Facebook, com o
motivo FACEBOOK_CAPABILITY_BLOCK. Desde a D13 escreve CAPABILITY_BLOCK. Esta
ferramenta corrige as linhas que ja estavam escritas, pela MESMA regra e so
essas: MOTIVO_DA_RECUSA a comecar por FACEBOOK_CAPABILITY_BLOCK.

Nada se apaga: o motivo passa para MOTIVO_DO_BLOQUEIO, e a linha ganha
D13 = {ESTADO_ANTERIOR, MOTIVO_ANTERIOR, QUANDO}. Idempotente: a segunda corrida
nao muda nada. Sem --escrever so conta. Grava pelo dono da porta (fonte_nova.gravar).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "candidatas"))
import fonte_nova as FN  # noqa: E402

PREFIXO = "FACEBOOK_CAPABILITY_BLOCK"


def aplicar(doc: dict) -> list[str]:
    mudadas = []
    for c in doc["CANDIDATAS"]:
        motivo = c.get("MOTIVO_DA_RECUSA") or ""
        if c.get("ESTADO") != "RECUSADA" or not motivo.startswith(PREFIXO):
            continue
        c["D13"] = {"ESTADO_ANTERIOR": "RECUSADA", "MOTIVO_ANTERIOR": motivo,
                    "QUANDO": datetime.now(timezone.utc).isoformat(),
                    "DECISAO": "D13 (DECISOES-DONO-2026-09-23, linha 116): sem capacidade nao e recusa"}
        c["ESTADO"] = "CAPABILITY_BLOCK"
        c["MOTIVO_DO_BLOQUEIO"] = motivo
        c["MOTIVO_DA_RECUSA"] = None
        mudadas.append(c["CANDIDATA_ID"])
    if mudadas or any(c.get("ESTADO") == "CAPABILITY_BLOCK" for c in doc["CANDIDATAS"]):
        doc.setdefault("ESTADOS", {}).setdefault("CAPABILITY_BLOCK", FN.ESTADO_CAPABILITY_BLOCK)
    return mudadas


if __name__ == "__main__":
    if "--porta" in sys.argv:
        FN.FILA = Path(sys.argv[sys.argv.index("--porta") + 1])
    doc = FN.carregar()
    m = aplicar(doc)
    print(json.dumps({"MUDADAS": m, "N": len(m)}, ensure_ascii=False))
    if "--escrever" in sys.argv and m:
        FN.gravar(doc)
