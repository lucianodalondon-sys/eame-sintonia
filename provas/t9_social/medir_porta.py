# -*- coding: utf-8 -*-
"""T9 SOCIAL-CATALOGO-AUTORIZADO · a medicao por plataforma: com rastro / sem rastro / recusado e motivo.

    py provas/t9_social/medir_porta.py --contratos=<italy_contracts_curator.json> --livro=<LIFECYCLE-LEDGER-V1.json>
        [--lista-curator=<CURATOR-FONTES-CANARIO-MULTICANAL.json>] [--json=<saida>]

So leitura: le os dois ficheiros (pode ser uma COPIA dos do servico vivo), corre a porta
(`plano_onda_social.triagem_social`) e escreve a contagem. Com a lista do Curator, diz tambem que
itens dela NAO estao no catalogo (a porta nunca os ve: nao e recusa, e ausencia). 0 rede, 0 escrita
fora de --json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ, RAIZ / "curadoria"):
    sys.path.insert(0, str(_p))
import _gavetas  # noqa: E402,F401
import lifecycle as LC  # noqa: E402
import plano_onda_social as P  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def medir(contratos_f: Path, livro_f: Path, lista_f: Path | None = None) -> dict:
    contratos = {c["SOURCE_ID"]: c for c in json.loads(contratos_f.read_text(encoding="utf-8"))["FONTES"]}
    livro = json.loads(livro_f.read_text(encoding="utf-8"))
    t = P.triagem_social(contratos, estado_de=lambda s: LC.estado_de(s, livro))
    estrategias = Counter(str((c.get("ACQUISITION") or {}).get("STRATEGY")) for c in contratos.values())
    plat = {}
    for r in t["RECUSADAS"]:
        p = plat.setdefault(r["PLATAFORMA"] or "NAO_SEI", {"ACEITES": [], "RECUSADAS": {}})
        p["RECUSADAS"].setdefault(r["MOTIVO"], []).append(r["SOURCE_ID"])
    for s in t["ACEITES"]:
        aq = contratos[s]["ACQUISITION"]
        k = "YOUTUBE" if aq.get("STRATEGY") == P.FEED else (aq.get("PLATFORM") or "NAO_SEI")
        plat.setdefault(k, {"ACEITES": [], "RECUSADAS": {}})["ACEITES"].append(s)
    # "com rastro" = o contrato cita a decisao do dono que a plataforma pede (o mesmo teste da porta)
    rastro = {}
    for s, c in contratos.items():
        aq = c.get("ACQUISITION") or {}
        st = aq.get("STRATEGY")
        if st in P.NAO_SOCIAIS:
            continue
        k = "YOUTUBE" if st == P.FEED else (aq.get("PLATFORM") or "NAO_SEI")
        tem = not P._rastro_do_dono(k, aq)
        r = rastro.setdefault(k, {"COM_RASTRO": 0, "SEM_RASTRO": 0})
        r["COM_RASTRO" if tem else "SEM_RASTRO"] += 1
    out = {"DATASET": "T9-PORTA-SOCIAL-MEDICAO",
           "ENTRADAS": {"CONTRATOS": {"CAMINHO": str(contratos_f), "SHA256": sha(contratos_f)},
                        "LIVRO": {"CAMINHO": str(livro_f), "SHA256": sha(livro_f),
                                  "TRANSICOES": len(livro.get("TRANSICOES") or [])}},
           "CONTRATOS": len(contratos), "STRATEGY": dict(estrategias),
           "ESTADO_POR_STRATEGY_FASE": dict(Counter(
               "%s/%s/%s" % ((c.get("ACQUISITION") or {}).get("STRATEGY"), (c.get("ACQUISITION") or {}).get("FASE"),
                             LC.estado_de(s, livro))
               for s, c in contratos.items()
               if (c.get("ACQUISITION") or {}).get("STRATEGY") not in P.NAO_SOCIAIS)),
           "ACEITES": t["ACEITES"], "RECUSADAS_POR_MOTIVO": t["RECUSADAS_POR_MOTIVO"],
           "POR_PLATAFORMA": plat, "RASTRO_DO_DONO_POR_PLATAFORMA": rastro, "NAO_SOCIAIS": t["NAO_SOCIAIS"],
           "RECUSADAS": t["RECUSADAS"]}
    if lista_f:
        lista = json.loads(lista_f.read_text(encoding="utf-8"))
        fora = {}
        for chave in ("YOUTUBE", "LINKEDIN", "LINKEDIN_PESSOAS_OPCIONAIS", "INSTAGRAM"):
            for it in lista.get(chave) or []:
                if it["SOURCE_ID"] not in contratos:
                    fora.setdefault(chave, []).append({
                        "SOURCE_ID": it["SOURCE_ID"], "URL": it.get("URL"), "ESTADO_NO_LIVRO": it.get("ESTADO_NO_LIVRO"),
                        "REELS_JA_NO_REPOSITORIO": it.get("REELS_JA_NO_REPOSITORIO"),
                        "DECISAO_QUE_AUTORIZA": (it.get("DECISAO_QUE_AUTORIZA") or "")[:80]})
        out["LISTA_DO_CURATOR"] = {"CAMINHO": str(lista_f), "SHA256": sha(lista_f),
                                   "NO_CATALOGO": {k: sum(1 for it in lista.get(k) or [] if it["SOURCE_ID"] in contratos)
                                                   for k in ("YOUTUBE", "LINKEDIN", "LINKEDIN_PESSOAS_OPCIONAIS",
                                                             "INSTAGRAM")},
                                   "FORA_DO_CATALOGO": fora}
    return out


def main(argv=None) -> int:
    a = dict(x[2:].split("=", 1) for x in (sys.argv[1:] if argv is None else argv) if x.startswith("--") and "=" in x)
    r = medir(Path(a["contratos"]), Path(a["livro"]), Path(a["lista-curator"]) if a.get("lista-curator") else None)
    if a.get("json"):
        Path(a["json"]).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k not in ("RECUSADAS",)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
