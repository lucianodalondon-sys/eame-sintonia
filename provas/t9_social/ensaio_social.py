# -*- coding: utf-8 -*-
"""T9 SOCIAL-CATALOGO-AUTORIZADO · ensaio a seco da coleta continua, por linha, com --teto-24h numa COPIA.

    py provas/t9_social/ensaio_social.py --teto-24h-vivo=<TETO-24H.json> --plano=<RODADAS-PLANO.json>
        --estado-rodadas=<RODADAS-ESTADO.json> --historico=<a.json,b.json> --saida=<pasta nova>
        [--catalogo-social=<pasta com curadoria/italy_contracts_curator.json, curadoria/LIFECYCLE-LEDGER-V1.json
                            e ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json>]

1. COPIA o livro de 24 h, o plano, o estado das rodadas e o historico para <saida>/entradas (sha256 antes);
2. corre `coleta_continua.main(["--ensaio-a-seco", ...])` com `--teto-24h=<a copia>` (0 rede, 0 Sala, 0 robo);
3. com --catalogo-social, a linha SOCIAL le o catalogo dessa pasta (copias do vivo) em vez do desta arvore — a
   UNICA troca, e declarada no resultado; as outras linhas leem os catalogos desta arvore;
4. escreve <saida>/ENSAIO.json: por linha FONTES, ESTADO, PEDIDOS_PREVISTOS (+ PORTA_SOCIAL), e o sha256 do
   livro vivo antes e depois (tem de ser IGUAL: o ensaio nunca o le pelo caminho vivo).
Proxy fechado no processo (HTTP(S)_PROXY numa porta morta; localhost fora) — as sondas sao locais.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
sys.path.insert(0, str(RAIZ / "curadoria"))         # a pasta do catalogo copiado nao traz codigo: a porta e DESTA arvore


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    a = dict(x[2:].split("=", 1) for x in (sys.argv[1:] if argv is None else argv) if x.startswith("--") and "=" in x)
    saida = Path(a["saida"])
    if saida.exists():
        raise SystemExit("SAIDA_JA_EXISTE: %s" % saida)
    ent = saida / "entradas"
    ent.mkdir(parents=True)
    vivo = Path(a["teto-24h-vivo"])
    sha_vivo_antes = sha(vivo)
    copias = {}
    for nome in ("teto-24h-vivo", "plano", "estado-rodadas"):
        p = Path(a[nome])
        d = ent / p.name
        shutil.copyfile(p, d)
        copias[nome] = {"ORIGEM": str(p), "COPIA": str(d), "SHA256": sha(d)}
    hist = []
    for i, h in enumerate(x for x in a.get("historico", "").split(",") if x):
        d = ent / ("historico-%d-%s" % (i, Path(h).name))
        shutil.copyfile(h, d)
        hist.append(str(d))
        copias["historico-%d" % i] = {"ORIGEM": h, "COPIA": str(d), "SHA256": sha(d)}
    os.environ.update({"HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
                       "NO_PROXY": "127.0.0.1,localhost"})
    import coleta_continua as C  # noqa: PLC0415
    import plano_onda_social  # noqa: PLC0415,F401 — carregada daqui antes de `_catalogo_social` mexer no sys.path
    troca = None
    if a.get("catalogo-social"):
        cat = Path(a["catalogo-social"])
        original = C.CATALOGOS["SOCIAL"]
        C.CATALOGOS["SOCIAL"] = lambda _raiz: original(cat)
        troca = {"LINHA": "SOCIAL", "CATALOGO_DE": str(cat), "SHA256": {
            f: sha(cat / f) for f in ("curadoria/italy_contracts_curator.json", "curadoria/LIFECYCLE-LEDGER-V1.json",
                                      "ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json")}}
    args = ["--ensaio-a-seco", "--base=%s" % (saida / "base"), "--plano=%s" % copias["plano"]["COPIA"],
            "--estado-rodadas=%s" % copias["estado-rodadas"]["COPIA"],
            "--teto-24h=%s" % copias["teto-24h-vivo"]["COPIA"]]
    if hist:
        args.append("--historico=%s" % ",".join(hist))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = C.main(args)
    reg = json.loads(buf.getvalue())
    linhas = {n: {"ESTADO": l.get("ESTADO"), "FONTES": l.get("FONTES"), "PEDIDOS_PREVISTOS": l.get("PEDIDOS_PREVISTOS"),
                  "PORQUE": l.get("PORQUE"), "UNIDADES_GOVERNADAS": l.get("UNIDADES_GOVERNADAS"),
                  **({"PORTA_SOCIAL": l["PORTA_SOCIAL"]} if "PORTA_SOCIAL" in l else {}),
                  "MOTIVOS": [m.get("ESTADO") for m in l.get("MOTIVOS") or []]}
              for n, l in (reg.get("LINHAS") or {}).items()}
    out = {"DATASET": "T9-ENSAIO-A-SECO-POR-LINHA", "RC": rc, "ARGS": args, "COPIAS": copias,
           "TROCA_DECLARADA": troca, "LIVRO_VIVO": {"CAMINHO": str(vivo), "SHA256_ANTES": sha_vivo_antes,
                                                   "SHA256_DEPOIS": sha(vivo)},
           "LIVRO_COPIA_SHA256_DEPOIS": sha(Path(copias["teto-24h-vivo"]["COPIA"])),
           "A_SECO": reg.get("A_SECO"), "PARA": reg.get("PARA"), "AGORA_UTC": reg.get("AGORA_UTC"),
           "LINHAS": linhas}
    (saida / "ENSAIO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
                                       encoding="utf-8")
    (saida / "REGISTO-COMPLETO.json").write_text(buf.getvalue(), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
