#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G2 — gate APPROVED_SOURCE_ROUTE_COVERAGE medido numa FOTOGRAFIA dos livros vivos.

So leitura: le uma pasta de fotografia (copias + SHA256SUMS), nunca a lane viva.

    py medidas/medir_gates_g2.py --foto=<pasta g2-foto-...> [--saida=curadoria/G2-GATES-MEDIDOS-V1.json]

A REGUA (MANDATO-CONTINUO-ATE-BIG-COLLECTION.md:55): «fontes aprovadas possuem rota
ou bloqueio explicito». O mandato nao escreve a palavra SAFE; a regua dela e aquela
frase, e mede-se assim, fonte a fonte, sobre as APROVADAS = as que o portao da
Collection da por ELIGIBLE (`collection_gate.avaliar`, sem copia):

    ROTA_VALIDADA    a regua dos 4 passos passa (DETAIL/v1) — e o proprio ELIGIBLE
    NO_COLETOR       o coletor tem contrato para ela (regras/italy_contracts.mjs:
                     CONTRACTS, que ja inclui os onboarded). Sem isto a fonte esta
                     aprovada e NINGUEM a colhe: e a «aprovada sem rota» do mandato
    CANARIO_RECENTE  a prova da promocao tem <= 7 dias (REVALIDAR_ELEGIVEIS_DIAS, B3)
    CONTRATO_UNICO   a aquisicao e a MESMA no livro do portao (casa), no do bot e na
                     tabela do coletor (a regra da B2: um so dono do contrato)

SAFE  <=> toda aprovada tem ROTA_VALIDADA + NO_COLETOR + CANARIO_RECENTE + CONTRATO_UNICO,
          ou um bloqueio explicito escrito. Uma so que falhe = NOT_SAFE, com o nome dela.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as CG   # noqa: E402
import ready_split as RS       # noqa: E402
import gatilho_discovery as GD  # noqa: E402

DIAS = GD.REVALIDAR_ELEGIVEIS_DIAS


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _aq(c):
    return json.dumps((c or {}).get("ACQUISITION"), sort_keys=True, ensure_ascii=False)


def _quando(s):
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def ler_foto(foto: Path) -> dict:
    c, b = foto / "casa", foto / "bot"
    return {
        "livro": _j(c / "curadoria_LIFECYCLE-LEDGER-V1.json"),
        "evidencias": {p["EVIDENCE_REF"]: p for p in _j(c / "curadoria_LIFECYCLE-EVIDENCE-V1.json")["PROVAS"]},
        "contratos": {x["SOURCE_ID"]: x for x in _j(c / "curadoria_italy_contracts_curator.json")["FONTES"]},
        "bot_contratos": {x["SOURCE_ID"]: x for x in _j(b / "curadoria_italy_contracts_curator.json")["FONTES"]},
        "bot_evidencias": {p["EVIDENCE_REF"]: p for p in _j(b / "curadoria_LIFECYCLE-EVIDENCE-V1.json")["PROVAS"]},
        "coletor": _j(c / "coletor_CONTRACTS.json"),
        "rotas": _j(c / "curadoria_ROTAS-ELEGIVEIS-V1.json") if (c / "curadoria_ROTAS-ELEGIVEIS-V1.json").exists() else {},
        "quando": datetime.strptime(foto.name.split("g2-foto-")[1], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc),
    }


def hora_do_canario(sid: str, f: dict) -> tuple:
    """(instante da prova, de onde veio). A linha do livro pode ser a hora da
    reconciliacao que a copiou; a hora que conta e a da PROVA."""
    p = RS.ultima_promocao(sid, f["livro"])
    if not p:
        return None, "sem promocao"
    ref = p.get("EVIDENCE_REF") or ""
    ev = f["evidencias"].get(ref) or f["bot_evidencias"].get(ref)
    if ev and ev.get("OBSERVED_AT"):
        return _quando(ev["OBSERVED_AT"]), "prova %s" % ref
    return _quando(p.get("OBSERVED_AT")), "linha do livro %s (prova %s nao encontrada)" % (p.get("OBSERVED_AT"), ref)


def medir_cobertura(f: dict) -> dict:
    ctx = {"livro": f["livro"], "evidencias": f["evidencias"], "contratos": f["contratos"]}
    inv = CG.inventario(ctx=ctx)
    painel = CG.painel(ctx=ctx)
    col = f["coletor"]["CONTRATOS"]
    linhas = []
    for l in inv:
        if not l["COLLECTION_ELIGIBLE"]:
            continue
        s = l["SOURCE_ID"]
        quando, origem = hora_do_canario(s, f)
        idade = (f["quando"] - quando).total_seconds() / 86400 if quando else None
        a_casa, a_bot = _aq(f["contratos"].get(s)), _aq(f["bot_contratos"].get(s))
        a_col = json.dumps((col.get(s) or {}).get("ACQUISITION"), sort_keys=True, ensure_ascii=False) if s in col else None
        donos = {"CASA": a_casa, "BOT": a_bot if s in f["bot_contratos"] else None, "COLETOR": a_col}
        presentes = {k: v for k, v in donos.items() if v is not None}
        linha = {"SOURCE_ID": s,
                 "ROTA_VALIDADA": l["READY_RULE"] == RS.REGUA_CURRENT,
                 "NO_COLETOR": s in col,
                 "CANARIO_EM": quando.isoformat() if quando else None, "CANARIO_ORIGEM": origem,
                 "CANARIO_IDADE_DIAS": round(idade, 2) if idade is not None else None,
                 "CANARIO_RECENTE": idade is not None and idade <= DIAS,
                 "CONTRATO_UNICO": len(presentes) == 3 and len(set(presentes.values())) == 1,
                 "DONOS_PRESENTES": sorted(presentes), "DONOS_QUE_DIVERGEM": len(set(presentes.values())) > 1,
                 "ROTA_M3": ((f["rotas"].get("FONTES") or {}) if isinstance(f["rotas"].get("FONTES"), dict) else
                             {x.get("SOURCE_ID"): x for x in (f["rotas"].get("FONTES") or f["rotas"].get("LINHAS") or [])}
                             ).get(s, {}).get("VEREDITO")}
        linha["OK"] = all(linha[k] for k in ("ROTA_VALIDADA", "NO_COLETOR", "CANARIO_RECENTE", "CONTRATO_UNICO"))
        linhas.append(linha)
    falham = [x for x in linhas if not x["OK"]]
    return {
        "PAINEL_DO_PORTAO": painel,
        "APROVADAS": len(linhas),
        "COM_ROTA_VALIDADA": sum(x["ROTA_VALIDADA"] for x in linhas),
        "COM_CONTRATO_NO_COLETOR": sum(x["NO_COLETOR"] for x in linhas),
        "APROVADAS_SEM_ROTA_NO_COLETOR": sorted(x["SOURCE_ID"] for x in linhas if not x["NO_COLETOR"]),
        "COM_CANARIO_RECENTE_7D": sum(x["CANARIO_RECENTE"] for x in linhas),
        "COM_CONTRATO_UNICO": sum(x["CONTRATO_UNICO"] for x in linhas),
        "CONTRATO_DIVERGENTE": sorted(x["SOURCE_ID"] for x in linhas if x["DONOS_QUE_DIVERGEM"]),
        "OK_NOS_QUATRO": len(linhas) - len(falham),
        "APPROVED_SOURCE_ROUTE_COVERAGE": "SAFE" if not falham else "NOT_SAFE",
        "LINHAS": linhas,
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    foto = Path(arg["foto"])
    f = ler_foto(foto)
    r = medir_cobertura(f)
    r = {"DATASET": "G2-GATES-MEDIDOS-V1", "GATE": "APPROVED_SOURCE_ROUTE_COVERAGE", "FOTO": foto.name,
         "SHA256SUMS": (foto / "SHA256SUMS").read_text(encoding="utf-8"), **r}
    print(json.dumps({k: v for k, v in r.items() if k not in ("LINHAS", "SHA256SUMS")}, ensure_ascii=False, indent=1))
    if "saida" in arg:
        Path(arg["saida"]).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
