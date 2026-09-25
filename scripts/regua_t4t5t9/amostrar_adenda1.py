#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADENDA 1 · estrato FONTE-DECLARADA: os brutos T4/T5/T9 do armazem (COPIA), texto pelos extratores da casa.

    py scripts/regua_t4t5t9/amostrar_adenda1.py --brutos=C:/ajustes/brutos-t4t5t9

Sem rede. PDF -> coleta/executor_texto_de_pdf.extrair; HTML (e as paginas do YouTube sem extensao)
-> coleta/executor_texto_de_html.extrair; CSV entra como texto cru. JSON de OBSERVACAO que so diz
FAILED/TRANSPORT_OR_EMPTY nao tem conteudo e fica fora (contado). Semente 45945, 30 % para a prova cega.
"""
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).parent
sys.path.insert(0, str(RAIZ / "coleta"))
import executor_texto_de_html as EH  # noqa: E402
import executor_texto_de_pdf as EP   # noqa: E402

DESTINO = Path.home() / "sintonia-gabarito" / "REGUA-T4T5T9-V1" / "textos"
SEMENTE = 45945


def _arg(n, d=None):
    return next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--%s=" % n)), d)


def texto_de(p: Path):
    b = p.read_bytes()
    if b[:4] == b"%PDF":
        r = EP.extrair(p)
        return (r[0] if isinstance(r, tuple) else r), "PDF"
    if p.suffix.lower() == ".json":
        return None, "JSON_SEM_CONTEUDO"
    if p.suffix.lower() == ".csv":
        return b.decode("utf-8", "replace"), "CSV"
    if b.lstrip()[:1] == b"<":
        r = EH.extrair(b, "text/html")
        return (r[0] if isinstance(r, tuple) else r), "HTML"
    return None, "DESCONHECIDO"


def main():
    base = Path(_arg("brutos", "C:/ajustes/brutos-t4t5t9"))
    ja = {x["SHA256_NORMALIZADO"] for x in json.loads((AQUI / "A-ROTULAR.json").read_text(encoding="utf-8"))["ITENS"]}
    conta, itens, vistos = Counter(), [], set(ja)
    for p in sorted(base.rglob("*")):
        if not p.is_file():
            continue
        fonte = p.relative_to(base).parts[0].upper()
        try:
            t, esp = texto_de(p)
        except Exception as e:                                   # noqa: BLE001
            conta["ERRO_EXTRACAO"] += 1
            continue
        conta[esp] += 1
        if not t or len(t.strip()) < 150:
            conta["CURTO_OU_VAZIO"] += 1
            continue
        h = hashlib.sha256(re.sub(r"\s+", " ", t).strip().encode("utf-8")).hexdigest()
        if h in vistos:
            conta["DUPLICADO"] += 1
            continue
        vistos.add(h)
        DESTINO.mkdir(parents=True, exist_ok=True)
        (DESTINO / (h[:16] + ".txt")).write_text(t, encoding="utf-8")
        itens.append({"ID": h[:16], "SHA256_NORMALIZADO": h, "ORIGEM": "ARMAZEM-XX-COPIA", "FONTE": fonte,
                      "ESPECIE": esp, "FICHEIRO": p.name[:80], "ESTRATO": "FONTE-DECLARADA"})
    rnd = random.Random(SEMENTE)
    ordem = sorted(itens, key=lambda x: x["ID"])
    rnd.shuffle(ordem)
    ncega = round(len(ordem) * 0.30)
    for i, x in enumerate(ordem):
        x["CONJUNTO"] = "PROVA_CEGA" if i < ncega else "GABARITO"
    out = {"DATASET": "A-ROTULAR-T4T5T9-ADENDA1", "PROTOCOLO": "ADENDA 1", "SEMENTE": SEMENTE,
           "EXTRACAO": dict(conta), "POR_FONTE": dict(Counter(x["FONTE"][:5] for x in ordem)),
           "TEXTOS_FORA_DO_GIT": str(DESTINO), "ITENS": ordem}
    (AQUI / "A-ROTULAR-ADENDA1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("EXTRACAO", "POR_FONTE")}, ensure_ascii=False), "itens", len(ordem),
          "cega", ncega)


if __name__ == "__main__":
    main()
