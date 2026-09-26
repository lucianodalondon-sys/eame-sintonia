#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PASSO 9 da MICRO-PROVA, generico (lote 1, 2B, 3...) — com o ROBO PARADO. Corre a partir do clone com a ferramenta:

    py curadoria/micro_prova_passo9.py --vivo=<PASTA_DO_VIVO> --decididas=<DECIDIDAS-LOTE.json> --quem-viu=MICRO-PROVA-LOTE2B

1. recusa correr sem <VIVO>/curadoria/PARAR.flag (um so escritor);
2. copia o canal DECISOES-SEMANTICAS e a porta FONTES-CANDIDATAS do vivo para ao lado das DECIDIDAS (com sha256);
3. as decididas com id PROVISORIO (FICHAS_NOVAS, «L2B-01») registam-se AGORA pela porta do vivo (`fonte_nova.registar`,
   PAIS = o da prova) e passam a ter CAND-id; as A_DECIDIR nao se registam — nunca;
4. aplica as decisoes pelo validador do proprio canal (`colher_prova_territorio.aplicar`);
5. poe o QUALIFY de cada uma que entrou: as novas por `enfileirar`, as que ja estavam na porta reabrindo SO a tarefa
   barrada com o nome exacto; 6. escreve RECIBO-PASSO9.json ao lado das DECIDIDAS. Sem rede, sem RAW, sem Sala.

Os modulos do canal, da porta e da fila sao os DO VIVO (importados de la antes da ferramenta); so o `aplicar` e o
leitor do lote vem do clone.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def passo9(vivo: Path, decididas: list[dict], FN, F, CPT, quem_viu: str, onde_viu: str) -> dict:
    """O nucleo, com os modulos injectados (testavel numa pasta temporaria)."""
    import decisao_semantica as DS
    canal = vivo / "curadoria" / "DECISOES-SEMANTICAS-V1.json"
    registadas, sem_registo, recusadas_antes = [], [], []
    entram_prov = [d for d in decididas if d.get("TERRITORIO") not in (CPT.A_DECIDIR, None, "", "NAO SEI")]
    for d in entram_prov:
        if CPT.RE_ID_NAO_REGISTADA.match(d.get("CANDIDATA_ID", "")):
            # o validador do canal ANTES de registar: uma decisao que o canal recusa nao deixa ficha na porta
            motivo = DS.porque_invalida(d, {"URL": d["URL"]})
            if motivo:
                recusadas_antes.append({"CANDIDATA_ID": d["CANDIDATA_ID"], "PORQUE": motivo})
                d["TERRITORIO"] = CPT.A_DECIDIR
                continue
            pais = d.get("PAIS") if d.get("PAIS") in FN.PAISES else "NAO SEI"
            c = FN.registar(tipo="ORGANIZACAO", pais=pais, nome=d["NOME"], url=d["URL"],
                            para_que="avisos/boletins de defesa datados (micro-prova, decisao com prova)",
                            quem_viu=quem_viu, onde_viu=onde_viu,
                            nota="ID_PROVISORIO=%s | PROVAS=%s" % (d["CANDIDATA_ID"], ", ".join(
                                p["URL"] for p in d.get("PROVAS", []))))
            registadas.append({"PROVISORIO": d["CANDIDATA_ID"], "CANDIDATA_ID": c["CANDIDATA_ID"],
                               "JA_ESTAVA": c.get("QUEM_VIU") != quem_viu})
            d["CANDIDATA_ID"] = c["CANDIDATA_ID"]
    fichas = {c["CANDIDATA_ID"]: c for c in FN.carregar()["CANDIDATAS"]}
    r = CPT.aplicar(decididas, caminho=canal, fichas=fichas)
    novas = {x["CANDIDATA_ID"] for x in registadas}
    qualify = []
    for cid in r["ENTRAM"]:
        if cid in novas:
            t = F.enfileirar(cid, F.QUALIFY, priority=30, motivo="micro-prova: decisao com prova no canal")
            qualify.append((t["TASK_ID"], cid, "NOVA"))
        else:
            nome = fichas[cid]["NOME"]
            for t in F.recuperar_bloqueadas_por_defeito(["territorio indeterminado pelo nome (%s)" % nome], {F.QUALIFY}):
                qualify.append((t["TASK_ID"], cid, "REABERTA"))
    for x in registadas:
        if x["CANDIDATA_ID"] not in r["ENTRAM"]:
            sem_registo.append(x)
    return {"REGISTADAS": registadas, "ENTRAM": r["ENTRAM"], "FICAM": recusadas_antes + r["FICAM"], "QUALIFY": qualify,
            "REGISTADAS_SEM_DECISAO_ACEITE": sem_registo}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    vivo, dec = Path(a["vivo"]).resolve(), Path(a["decididas"]).resolve()
    if not (vivo / "curadoria" / "PARAR.flag").exists():
        print("RECUSADO: o robo nao esta parado (falta curadoria/PARAR.flag) — um so escritor", file=sys.stderr)
        return 2
    # os modulos DO VIVO primeiro; depois a ferramenta do clone (ja nao os substitui: ficam em sys.modules)
    for m in ("fila", "fonte_nova", "decisao_semantica", "colher_prova_territorio"):
        sys.modules.pop(m, None)
    sys.path[:0] = [str(vivo / "curadoria"), str(vivo / "candidatas")]
    import fila as F                      # noqa: E402
    import fonte_nova as FN               # noqa: E402
    import decisao_semantica              # noqa: E402,F401
    for m, mod in (("fila", F), ("fonte_nova", FN)):
        assert Path(mod.__file__).resolve().parents[1] == vivo, (m, mod.__file__)
    spec = importlib.util.spec_from_file_location("colher_prova_territorio", AQUI / "colher_prova_territorio.py")
    CPT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(CPT)
    hora = datetime.now().strftime("%H%M%S")
    antes = {}
    for rel in ("curadoria/DECISOES-SEMANTICAS-V1.json", "candidatas/FONTES-CANDIDATAS.json"):
        cop = dec.parent / ("%s.antes-%s.json" % (Path(rel).stem, hora))
        shutil.copyfile(vivo / rel, cop)
        antes[rel] = {"COPIA": str(cop), "SHA256": _sha(cop)}
    decididas = json.loads(dec.read_text(encoding="utf-8"))["PROPOSTAS"]
    r = passo9(vivo, decididas, FN, F, CPT, quem_viu=a.get("quem-viu", "MICRO-PROVA"),
               onde_viu=a.get("onde-viu", "provas em %s" % dec.parent))
    recibo = {"QUANDO": datetime.now(timezone.utc).isoformat(timespec="seconds"), "VIVO": str(vivo),
              "DECIDIDAS": {"FICHEIRO": str(dec), "SHA256": _sha(dec)}, "ANTES": antes,
              "DEPOIS_SHA256": {rel: _sha(vivo / rel) for rel in antes}, **r}
    (dec.parent / "RECIBO-PASSO9.json").write_text(json.dumps(recibo, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("REGISTADAS", "ENTRAM", "QUALIFY")}, ensure_ascii=False),
          "| ficam de fora:", len(r["FICAM"]))
    return 0 if not r["REGISTADAS_SEM_DECISAO_ACEITE"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
