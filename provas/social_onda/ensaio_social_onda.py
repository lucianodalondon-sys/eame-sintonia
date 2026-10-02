# -*- coding: utf-8 -*-
"""SOCIAL-ONDA · ensaio a seco da coleta continua, por linha, com --teto-24h numa COPIA e a flag do dono.

    py provas/social_onda/ensaio_social_onda.py --teto-24h-vivo=<TETO-24H.json> --plano=<RODADAS-PLANO.json>
        --estado-rodadas=<RODADAS-ESTADO.json> --historico=<a.json,b.json> --saida=<pasta nova>
        [--catalogo-social=<pasta do servico (SO LIDA)>] [--autorizado-pelo-dono]
        [--supor-social-ready]   (HIPOTESE: o portao admite as ACEITES da porta social; so com --catalogo-social)

O molde e `provas/t9_social/ensaio_social.py`, com duas diferencas:
1. a flag `--autorizado-pelo-dono` passa a `coleta_continua.main` (liga a onda SOCIAL; a seco nada corre);
2. com --catalogo-social, os QUATRO ficheiros que a linha SOCIAL e o portao da Collection leem
   (catalogo, livro do ciclo de vida, evidencias, coorte) sao COPIADOS dessa pasta para <saida>/catalogo-vivo
   (sha256 da origem antes e depois da copia; a pasta do servico nunca e escrita) e:
     · a linha SOCIAL le a copia (`CATALOGOS["SOCIAL"]`, como no T9);
     · o portao da Collection (`portao_da_fonte_real`, o mesmo codigo) le a copia: os tres caminhos
       `lifecycle.LIVRO`, `ready_split.EVIDENCIA`, `ready_split.CONTRATOS` apontam para ela durante a chamada.
   E a UNICA troca, declarada em TROCA_DECLARADA. As outras linhas leem os catalogos desta arvore.
Escreve <saida>/ENSAIO.json: por linha FONTES, ESTADO, PEDIDOS_PREVISTOS, PORQUE (+ PORTA_SOCIAL e as que
ESPERAM). 0 rede (proxy fechado no processo; as sondas sao locais), 0 Sala, 0 robo.
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
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas" / "big_collection"))
sys.path.insert(0, str(RAIZ / "curadoria"))
FICHEIROS = ("curadoria/italy_contracts_curator.json", "curadoria/LIFECYCLE-LEDGER-V1.json",
             "curadoria/LIFECYCLE-EVIDENCE-V1.json", "ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def copiar_catalogo(origem: Path, destino: Path) -> dict:
    out = {}
    for rel in FICHEIROS:
        o, d = origem / rel, destino / rel
        if not o.exists():
            out[rel] = {"ORIGEM": str(o), "EXISTE": False}
            continue
        antes = sha(o)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(o, d)
        out[rel] = {"ORIGEM": str(o), "SHA256_ORIGEM_ANTES": antes, "SHA256_COPIA": sha(d),
                    "SHA256_ORIGEM_DEPOIS": sha(o)}
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    flag = "--autorizado-pelo-dono" in argv
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
    import lifecycle as LC  # noqa: PLC0415
    import ready_split as RS  # noqa: PLC0415
    troca, pilha = None, contextlib.ExitStack()
    if a.get("catalogo-social"):
        cat = saida / "catalogo-vivo"
        lidos = copiar_catalogo(Path(a["catalogo-social"]), cat)
        original_cat, original_portao = C.CATALOGOS["SOCIAL"], C.portao_da_fonte_real

        supor = set(original_cat(cat)["PORTA_SOCIAL"]["ACEITES"]) if "--supor-social-ready" in argv else set()

        def portao_da_copia(ids):
            with mock.patch.object(LC, "LIVRO", cat / FICHEIROS[1]), \
                    mock.patch.object(RS, "EVIDENCIA", cat / FICHEIROS[2]), \
                    mock.patch.object(RS, "CONTRATOS", cat / FICHEIROS[0]):
                v = original_portao(ids)
            for s in supor & set(ids):                     # HIPOTESE declarada: so as ACEITES da porta social
                v[s] = dict(v[s], COLLECTION_ELIGIBLE=True, HIPOTESE="SUPOR_SOCIAL_READY (o estado lido era %s)"
                            % v[s].get("STATE"))
            return v
        pilha.enter_context(mock.patch.dict(C.CATALOGOS, {"SOCIAL": lambda _raiz: original_cat(cat)}))
        pilha.enter_context(mock.patch.object(C, "portao_da_fonte_real", portao_da_copia))
        troca = {"LINHA_SOCIAL_E_PORTAO_DA_COLLECTION_LEEM": str(cat), "LIDOS_DE": lidos,
                 "NOTA": "o portao da Collection le a copia para TODAS as linhas (como o vivo le o seu livro)",
                 "HIPOTESE_SUPOR_SOCIAL_READY": sorted(supor) or None}
    args = ["--ensaio-a-seco", "--base=%s" % (saida / "base"), "--plano=%s" % copias["plano"]["COPIA"],
            "--estado-rodadas=%s" % copias["estado-rodadas"]["COPIA"],
            "--teto-24h=%s" % copias["teto-24h-vivo"]["COPIA"]]
    if hist:
        args.append("--historico=%s" % ",".join(hist))
    if flag:
        args.append("--autorizado-pelo-dono")
    buf = io.StringIO()
    with pilha, contextlib.redirect_stdout(buf):
        rc = C.main(args)
    reg = json.loads(buf.getvalue())
    linhas = {n: {"ESTADO": l.get("ESTADO"), "FONTES": l.get("FONTES"), "PEDIDOS_PREVISTOS": l.get("PEDIDOS_PREVISTOS"),
                  "PORQUE": l.get("PORQUE"), "UNIDADES_GOVERNADAS": l.get("UNIDADES_GOVERNADAS"),
                  **({"PORTA_SOCIAL": l["PORTA_SOCIAL"]} if "PORTA_SOCIAL" in l else {}),
                  "MOTIVOS": [m.get("ESTADO") for m in l.get("MOTIVOS") or []],
                  "ESPERAM": [{k: e.get(k) for k in ("SOURCE_ID", "PORQUE", "ESTADO_LIDO", "MOTIVO_DO_PORTAO",
                                                     "DOMINIOS_FECHADOS", "ABRE_EM")}
                              for e in reg.get("ESPERAM") or [] if e.get("LINHA") == n]}
              for n, l in (reg.get("LINHAS") or {}).items()}
    out = {"DATASET": "SOCIAL-ONDA-ENSAIO-A-SECO-POR-LINHA", "RC": rc, "AUTORIZADO_PELO_DONO": flag, "ARGS": args,
           "COPIAS": copias, "TROCA_DECLARADA": troca,
           "LIVRO_VIVO": {"CAMINHO": str(vivo), "SHA256_ANTES": sha_vivo_antes, "SHA256_DEPOIS": sha(vivo)},
           "LIVRO_COPIA_SHA256_DEPOIS": sha(Path(copias["teto-24h-vivo"]["COPIA"])),
           "A_SECO": reg.get("A_SECO"), "PARA": reg.get("PARA"), "RUN_IDS": reg.get("RUN_IDS"),
           "AGORA_UTC": reg.get("AGORA_UTC"), "LINHAS": linhas}
    (saida / "ENSAIO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
                                       encoding="utf-8")
    (saida / "REGISTO-COMPLETO.json").write_text(buf.getvalue(), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
