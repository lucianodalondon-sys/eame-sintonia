# -*- coding: utf-8 -*-
"""O RESUMO AUDITAVEL DE UMA ONDA (D59) — o que entra no Git para a trava poder contar a corrida.

    py ferramentas/big_collection/resumo_da_onda.py <pasta-da-onda> [<pasta-da-onda> ...]

D59 (bot Luciano, 25/09): uma corrida real pelo orquestrador PODE provar estrada no criterio A por
SOURCE_ID, se mostrar sucesso, RAW e DERIVED reais, rota/executor identificaveis e proveniencia
integra. O estado completo da onda (`ONDA-WEB-ESTADO.json`, relatorios, livros) fica FORA do Git;
entra so este resumo, ligado por RUN_ID e conferido pelo medidor contra o livro de corridas do
coletor.

LE (so leitura) o que o condutor da onda ja escreveu:
  · `<pasta>/ONDA-WEB-ESTADO.json`               a linha de cada fonte (RUN_ID, STATUS, GATE, EGRESSO,
                                                 pedidos por dominio, C4)
  · `<pasta>/<SOURCE_ID>/RELATORIO-PASSAGEM.json` o relatorio DAQUELA corrida (`micro_coleta.relatorio`):
                                                 RAW = CONTAGENS.RAW_CREATED, DERIVED = C4.COM_DERIVADO,
                                                 proveniencia = C4, veredictos da Admission = C7
ESCREVE `ferramentas/big_collection/ondas/<ONDA>-RESUMO.json`.

NAO INVENTA. Um numero que nenhum artefacto da onda diz fica "UNKNOWN" — e UNKNOWN nao conta.
O relatorio da fonte so vale se o RUN_ID dele for o da linha do estado. Sem bytes, sem texto, sem DSN,
sem caminhos de livros: so contagens, identificadores e sha256 dos artefactos lidos.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DESTINO = AQUI / "ondas"
UNKNOWN = "UNKNOWN"
DATASET = "RESUMO-DA-ONDA-V1"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def executor_da_porta() -> str:
    """O executor que a porta canonica lanca (`micro_coleta.EXECUTOR`), lido no codigo — nao repetido a mao."""
    m = re.search(r'^EXECUTOR\s*=\s*"([^"]+)"', (RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py")
                  .read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else UNKNOWN


def _numero(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else UNKNOWN


def linha_da_fonte(f: dict, pasta: Path) -> dict:
    """Uma linha do resumo, a partir da linha do estado e do relatorio da corrida (se for da mesma)."""
    out = {"SOURCE_ID": f.get("SOURCE_ID"), "RUN_ID": f.get("RUN_ID"), "CORREU": bool(f.get("CORREU")),
           "STATUS": f.get("STATUS") or UNKNOWN}
    if not f.get("RUN_ID"):
        out["PORQUE_NAO_CORREU"] = f.get("PORQUE_NAO_CORREU") or UNKNOWN
        return out
    rel_p = pasta / str(f["SOURCE_ID"]) / "RELATORIO-PASSAGEM.json"
    rel = {}
    if rel_p.exists():
        rel = json.loads(rel_p.read_text(encoding="utf-8"))
        if rel.get("RUN_IDS") != [f["RUN_ID"]]:
            out["RELATORIO_RECUSADO"] = "o relatorio da pasta e de outra corrida: %s" % rel.get("RUN_IDS")
            rel = {}
        else:
            out["RELATORIO_SHA256"] = _sha(rel_p)
    c4 = ((rel.get("CRITERIOS") or {}).get("C4_PROVENIENCIA_COMPLETA")) or f.get("C4") or {}
    # RAW: o relatorio da corrida; se nao houver, o que o proprio estado gravou (onda_web >= D59); senao UNKNOWN
    out["RAW"] = _numero((rel.get("CONTAGENS") or {}).get("RAW_CREATED")) if rel else _numero(f.get("RAW"))
    out["DERIVED"] = _numero(c4.get("COM_DERIVADO")) if c4 else _numero(f.get("DERIVED"))
    out["DE_ONDE"] = "RELATORIO-PASSAGEM da corrida" if rel else ("linha do estado" if "RAW" in f else UNKNOWN)
    out["PROVENIENCIA"] = {k: _numero(c4.get(k)) for k in
                           ("OBSERVACOES", "COM_STORAGE", "COM_DERIVADO", "COM_DECISAO", "SALA_LINHAS",
                            "SALA_COM_CADEIA_INTEIRA")} if c4 else UNKNOWN
    por_fonte = ((rel.get("CRITERIOS") or {}).get("C7_PROPORCAO_POR_FONTE_E_CLASSE") or {}).get("POR_FONTE") or {}
    out["VEREDICTOS_DA_ADMISSION"] = por_fonte.get(f["SOURCE_ID"], UNKNOWN) if rel else UNKNOWN
    out["GATE"] = f.get("GATE") or UNKNOWN
    out["EGRESSO"] = f.get("EGRESSO") or UNKNOWN
    out["DOMINIO"] = f.get("DOMINIO") or UNKNOWN
    out["PEDIDOS_POR_DOMINIO"] = f.get("PEDIDOS_POR_DOMINIO") or UNKNOWN
    return out


def resumo(pasta: Path) -> dict:
    pasta = Path(pasta)
    estado_p = pasta / "ONDA-WEB-ESTADO.json"
    e = json.loads(estado_p.read_text(encoding="utf-8"))
    fontes = [linha_da_fonte(f, pasta) for f in e.get("FONTES") or []]
    return {
        "DATASET": DATASET, "ONDA": pasta.name,
        "LEI": "D59: resumo auditavel ligado por RUN_ID; o estado completo fica fora do Git; UNKNOWN nao conta",
        "INICIO": e.get("INICIO"), "FIM": e.get("FIM"), "PAROU": e.get("PAROU"),
        "ARVORE": e.get("ARVORE"), "COORTE_SHA256": e.get("COORTE_SHA256"),
        "ESTADO_SHA256": _sha(estado_p),
        "PORTA": "scripts/micro_coleta/micro_coleta.py:correr", "EXECUTOR": executor_da_porta(),
        "RUN_IDS": [f["RUN_ID"] for f in fontes if f.get("RUN_ID")],
        "FONTES": fontes,
    }


def escrever(pasta: Path, destino: Path = DESTINO) -> Path:
    r = resumo(pasta)
    destino.mkdir(parents=True, exist_ok=True)
    p = destino / ("%s-RESUMO.json" % r["ONDA"])
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(r, ensure_ascii=False, indent=1) + "\n")
    return p


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    for a in argv:
        p = escrever(Path(a))
        r = json.loads(p.read_text(encoding="utf-8"))
        print(p, "·", len(r["RUN_IDS"]), "corridas ·",
              sum(1 for f in r["FONTES"] if f.get("RAW") == UNKNOWN and f.get("RUN_ID")), "com RAW UNKNOWN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
