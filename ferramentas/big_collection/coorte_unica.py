#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G3 — A COORTE UNICA DA BIG COLLECTION (D25), com a prova fonte a fonte. Sem rede.

    py ferramentas/big_collection/coorte_unica.py --plano=<saida de micro_coleta.py plano>
        [--saida=ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json]

Le o que ja existe, nao decide nada de novo:
  · `scripts/micro_coleta/micro_coleta.py plano` (a ferramenta do runbook, passo 2): PRONTA
    ou BLOQUEADA, com o FALTA de cada uma;
  · os livros desta arvore (portao: `collection_gate.avaliar`; provas do canario);
  · o dono dos contratos do coletor (`regras/italy_contracts.mjs`, via node).

Uma PRONTA so entra na coorte se, alem do plano, as tres provas da G3 baterem:
  CONTRATO_EXECUTAVEL  o coletor tem contrato e a ACQUISITION e a do portao, byte a byte
  ROTA_VALIDADA        o portao da ELIGIBLE pela regua dos 4 passos (DETAIL/v1)
  CANARIO_7D           a prova da promocao existe nas provas e tem <= 7 dias
                       (REVALIDAR_ELEGIVEIS_DIAS); sem prova nao ha canario
Se uma PRONTA falhar alguma, sai com o nome da prova que falhou — nao se cala.

PROVISORIA POR OMISSAO (bot Luciano, 23/09 19:20): a coorte FINAL so se congela DEPOIS da
instalacao (runbook passo I) e da demotion (B5). Sem `--congelar` o ficheiro sai
ESTADO=PROVISORIA. `--congelar` exige `--instalacao=<commit>` e `--demotion=<referencia B5>`
declarados, e grava-os. Nunca e a contagem de READY do livro (143 READY != coorte).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as CG     # noqa: E402
import ready_split as RS         # noqa: E402
import gatilho_discovery as GD   # noqa: E402

LIVROS = ("curadoria/LIFECYCLE-LEDGER-V1.json", "curadoria/LIFECYCLE-EVIDENCE-V1.json",
          "curadoria/italy_contracts_curator.json", "regras/italy_contracts_onboarded.json")


def _aq(a) -> str:
    return json.dumps(a, sort_keys=True, ensure_ascii=False)


def contratos_do_coletor() -> dict:
    r = subprocess.run(["node", "--input-type=module", "-e",
                        "const m = await import('./regras/italy_contracts.mjs');"
                        "const o = {}; for (const i of m.CONTRACT_IDS) o[i] = m.CONTRACTS[i].ACQUISITION ?? null;"
                        "console.log(JSON.stringify(o));"],
                       cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=120)
    if r.returncode:
        raise SystemExit("o dono dos contratos nao carregou: " + r.stderr[-300:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def _quando(s):
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def construir(plano: dict, agora: datetime) -> dict:
    ctx = CG._contexto()
    col = contratos_do_coletor()
    linhas, fora = [], []
    for l in plano["LINHAS"]:
        s = l["SOURCE_ID"]
        if l["ESTADO"] != "PRONTA":
            fora.append({"SOURCE_ID": s, "UNIVERSO": l.get("UNIVERSO"), "FALTA": l.get("FALTA")})
            continue
        v = CG.avaliar(s, **ctx)
        p = RS.ultima_promocao(s, ctx["livro"]) or {}
        ev = ctx["evidencias"].get(p.get("EVIDENCE_REF") or "")
        quando = _quando(ev.get("OBSERVED_AT")) if ev else None
        idade = (agora - quando).total_seconds() / 86400 if quando else None
        c_portao = (ctx["contratos"].get(s) or {}).get("ACQUISITION")
        provas = {
            "CONTRATO_EXECUTAVEL": s in col and col[s] is not None and _aq(col[s]) == _aq(c_portao),
            "ROTA_VALIDADA": bool(v["COLLECTION_ELIGIBLE"]) and v["READY_RULE"] == RS.REGUA_CURRENT,
            "CANARIO_7D": idade is not None and idade <= GD.REVALIDAR_ELEGIVEIS_DIAS,
        }
        linha = {"SOURCE_ID": s, "UNIVERSO": l.get("UNIVERSO"),
                 "ULTIMO_CANARIO": {"EVIDENCE_REF": p.get("EVIDENCE_REF"),
                                    "OBSERVED_AT": ev.get("OBSERVED_AT") if ev else None,
                                    "IDADE_DIAS": round(idade, 2) if idade is not None else None,
                                    "ITEM_ABERTO": ((ev or {}).get("DADOS") or {}).get("ITEM_ABERTO", {}).get("URL")},
                 "INDEX_URL": (c_portao or {}).get("INDEX_URL"),
                 "PROVAS": provas}
        (linhas if all(provas.values()) else fora).append(
            linha if all(provas.values()) else dict(linha, FALTA=[k for k, ok in provas.items() if not ok]))
    itens = {}
    for x in linhas:
        itens.setdefault(x["ULTIMO_CANARIO"]["ITEM_ABERTO"], []).append(x["SOURCE_ID"])
    return {"COORTE": linhas, "FORA": fora,
            "DUPLICADAS_NA_COORTE": {k: v for k, v in itens.items() if k and len(v) > 1}}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    congelar = "--congelar" in argv
    if congelar and not (arg.get("instalacao") and arg.get("demotion")):
        raise SystemExit("--congelar exige --instalacao=<commit> e --demotion=<ref B5>: "
                         "a coorte final so se congela depois dos dois")
    plano = json.loads(Path(arg["plano"]).read_text(encoding="utf-8"))
    agora = datetime.now(timezone.utc)
    r = construir(plano, agora)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                          text=True).stdout.strip()
    out = {"DATASET": "COORTE-BIG-COLLECTION-V1", "DECISAO": "D25 (dono real, 23/09 ~15:20)",
           "ESTADO": "CONGELADA" if congelar else "PROVISORIA",
           "CONGELAMENTO": ({"INSTALACAO": arg["instalacao"], "DEMOTION_B5": arg["demotion"],
                             "EM": agora.isoformat(timespec="seconds")} if congelar else
                            "so depois da instalacao (passo I) e da demotion (B5) — bot Luciano, 23/09 19:20"),
           "NAO_E": "a contagem de READY do livro (READY_TOTAL do painel); a coorte e so a lista COORTE",
           "MEDIDO_EM": agora.isoformat(timespec="seconds"), "ARVORE": head,
           "PLANO": {"GERADO_EM": plano.get("GERADO_EM"), "PAINEL_DO_GATE": plano.get("PAINEL_DO_GATE"),
                     "PRONTAS": plano.get("PRONTAS"), "BLOQUEADAS": plano.get("BLOQUEADAS")},
           "LIVROS_SHA256": {f: hashlib.sha256((RAIZ / f).read_bytes()).hexdigest() for f in LIVROS},
           "REGRA": ("PRONTA no micro_coleta plano E contrato executavel no coletor E rota validada "
                     "(portao ELIGIBLE, DETAIL/v1) E canario com prova <= %d dias" % GD.REVALIDAR_ELEGIVEIS_DIAS),
           "COORTE_BIG_COLLECTION": len(r["COORTE"]), **r}
    print(json.dumps({k: out[k] for k in ("COORTE_BIG_COLLECTION", "DUPLICADAS_NA_COORTE")}, ensure_ascii=False))
    if "saida" in arg:
        Path(arg["saida"]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
