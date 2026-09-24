#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ONDA EM CURSO — a coleta le uma FOTO, o Curator continua (CUR-PRONTA, 24/09/2026).

    «o sistema final e uma orquestra: fontes, coleta e Intelligence nunca param,
     cada um no seu trabalho, em sincronia» — o dono, 24/09 09:25.

Ate aqui o passo 1 do BIG-COLLECTION-RUNBOOK PARAVA o Curator durante a onda
(«parar a escrita concorrente»). Medido ficheiro a ficheiro (PLANO-CUR-PRONTA):
a coleta NAO escreve em nenhum livro do Curator e o Curator NAO escreve em nada
da coleta. A colisao era de LEITURA: `italy_executor.admissao_do_curator`
pergunta ao portao VIVO antes de CADA fonte, e o portao le o livro do Curator
nessa hora. Um Curator a trabalhar podia (a) tirar de READY uma fonte da coorte
a meio da onda (VALIDATE_ROUTE -> CANARY_PENDING) e ela era recusada; (b) estar
a meio de uma escrita e o portao ler JSON cortado -> GATE_NAO_RESPONDEU ->
recusada; (c) no Windows, o leitor trava o `os.replace` do escritor.

O remedio e uma FOTO: quem abre a onda grava aqui a coorte congelada (a mesma
`COORTE-BIG-COLLECTION.json` do passo 2, com o sha256 dela). Enquanto a foto
existir:
  * o portao, perguntado por `--ids` (o caminho do executor), responde PELA
    FOTO e nao abre nenhum livro do Curator;
  * o Curator continua, mas nao canaria fontes de um anfitriao que esta na
    onda (cortesia: a pausa por host da A5 vale dentro de um processo, nao
    entre dois) — espera a onda seguinte;
  * o que o Curator promover durante a onda entra na ONDA SEGUINTE.

Ficheiro do lado da COLETA (`data/collection-ledger/italy/`): o Curator so o le.

    py curadoria/onda_em_curso.py --abrir <COORTE-BIG-COLLECTION.json>
    py curadoria/onda_em_curso.py --fechar
    py curadoria/onda_em_curso.py            # estado
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
ONDA = RAIZ / "data" / "collection-ledger" / "italy" / "ONDA-EM-CURSO.json"
CONTRATO = "ONDA_EM_CURSO/v1"


class OndaIlegivel(Exception):
    """A foto existe e nao se le. Nao e «nao ha onda»: e NAO SEI."""


def _host(url: str) -> str:
    h = urlparse(url or "").netloc.lower()
    return h[4:] if h.startswith("www.") else h


def ler() -> dict | None:
    """None = nao ha onda. Foto que existe e nao se le levanta OndaIlegivel."""
    if not ONDA.exists():
        return None
    try:
        d = json.loads(ONDA.read_text(encoding="utf-8"))
        assert d.get("CONTRATO") == CONTRATO and isinstance(d.get("COORTE"), list)
        return d
    except Exception as e:  # noqa: BLE001
        raise OndaIlegivel("%s existe e nao se le (%s): NAO SEI" % (ONDA, e)) from e


def abrir(coorte: Path) -> dict:
    """Congela a coorte que a onda vai correr. Escrita atomica."""
    bruto = Path(coorte).read_bytes()
    c = json.loads(bruto.decode("utf-8"))
    linhas = c.get("COORTE") or []
    d = {"CONTRATO": CONTRATO, "ABERTA_EM": datetime.now(timezone.utc).isoformat(),
         "COORTE_FICHEIRO": str(coorte), "COORTE_SHA256": hashlib.sha256(bruto).hexdigest(),
         "COORTE": [{"SOURCE_ID": x["SOURCE_ID"], "INDEX_URL": x.get("INDEX_URL", "")}
                    for x in linhas],
         "HOSTS": sorted({_host(x.get("INDEX_URL", "")) for x in linhas} - {""}),
         "LEI": ("durante a onda o portao responde por esta foto; o Curator continua e "
                 "nao canaria estes anfitrioes; o que promover entra na onda seguinte")}
    ONDA.parent.mkdir(parents=True, exist_ok=True)
    tmp = ONDA.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, ONDA)
    return d


def fechar() -> bool:
    if ONDA.exists():
        ONDA.unlink()
        return True
    return False


def veredito(source_id: str, onda: dict) -> dict:
    """A resposta do portao durante a onda, com os mesmos campos da de sempre."""
    dentro = any(x["SOURCE_ID"] == source_id for x in onda["COORTE"])
    return {"SOURCE_ID": source_id, "STATE": "COORTE_CONGELADA" if dentro else "FORA_DA_COORTE",
            "READY_RULE": "FOTO", "HUMAN_REVIEW_REQUIRED": None,
            "COLLECTION_ELIGIBLE": dentro,
            "MOTIVO": "ONDA_EM_CURSO" if dentro else "FORA_DA_ONDA_EM_CURSO",
            "PORQUE": ("na coorte congelada da onda aberta em %s (sha256 %s)"
                       if dentro else "a onda aberta em %s (sha256 %s) nao a inclui; "
                       "entra na onda seguinte se o portao a eleger")
                      % (onda["ABERTA_EM"][:19], onda["COORTE_SHA256"][:12])}


def hosts_na_onda() -> set:
    """Anfitrioes que a onda esta a visitar. Foto ilegivel -> conjunto vazio
    (o Curator nao sabe; a coleta, essa, recusa tudo pelo portao)."""
    try:
        o = ler()
    except OndaIlegivel:
        return set()
    return set(o["HOSTS"]) if o else set()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--abrir"] and len(a) == 2:
        print(json.dumps(abrir(Path(a[1])), ensure_ascii=False, indent=1))
    elif a == ["--fechar"]:
        print("fechada" if fechar() else "nao havia onda")
    else:
        print(json.dumps(ler(), ensure_ascii=False, indent=1))
