#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""INTEGRAR O GATE DE DETALHE NO SOURCE CURATOR — os contratos, no dono certo.

    SEM MERGE CEGO. As duas arvores divergiram em 61 commits e um merge
    destruiria um dos livros. O que se integra e o SENTIDO, peca a peca:

      1. o juiz     -> retrato_html.py + canario.py (o gate CAPA != MATERIA)
      2. a regua    -> worker.py escreve no livro por que regua promoveu
      3. as rotas   -> ESTE FICHEIRO: os contratos que a outra linha provou
                       contra a rede, aplicados a tabela que o worker desta
                       arvore executa (italy_contracts_curator.json)

A AQUISICAO-DETALHE-V1 (f98f234c, PASSO 2 = 83385fe7) provou 52 listagens
com um GET cada e corrigiu 21 contratos, so onde a listagem respondeu 200 com
mais de um item. Desses 21, 9 sao fontes do SOURCE CURATOR; os outros 12
vivem na tabela do motor (regras/italy_contracts.mjs), que e de outro dono e
NAO e tocada aqui.

⚠️ O REGISTO DA OUTRA LINHA E A FONTE, E CONFERE-SE ANTES DE APLICAR.
`CONTRATOS-PASSO-2-V1.json` (copia byte a byte de f98f234c) traz, por
contrato, o ANTES e o DEPOIS do bloco ACQUISITION e a prova (listagem, item
real que o padrao casa, nao-item que exclui). Este script:

    - recusa aplicar se o ACQUISITION local nao for IGUAL ao ANTES do registo
      (se divergir, alguem mexeu no meio e o DEPOIS pode ja nao servir);
    - e idempotente: se o local ja for o DEPOIS, nao reescreve nem re-hasha;
    - recalcula SOURCE_CONTRACT_HASH pela formula do worker (VERSAO presente,
      HASH ausente) — o hash guardado nos 77 nao se recompoe por nenhuma
      formula conhecida, e isso fica dito, nao escondido;
    - valida o contrato corrigido pelas MESMAS portas dos 77;
    - grava a procedencia da rota NO CONTRATO (ROUTE_PROVENANCE), para que
      ninguem tenha de adivinhar de onde veio um LINK_PATTERN;
    - NAO toca no livro: os 9 estao READY_FOR_COLLECTION pela regua antiga, e
      continuar a chama-los READY com um contrato novo seria promover sem
      canario. Quem os separa e o PASSO 7; quem os remede e o worker.

    O CONTRATO MUDOU => O READY ANTIGO E LEGACY. NAO SE APAGA, NAO SE MISTURA.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import escrever_contratos as EC  # noqa: E402
import lifecycle as LC           # noqa: E402
import validar_contratos as VC   # noqa: E402

REGISTO = RAIZ / "curadoria" / "CONTRATOS-PASSO-2-V1.json"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
SAIDA = RAIZ / "curadoria" / "DETAIL-GATE-INTEGRATION-V1.json"

ORIGEM = {"MISSAO": "AQUISICAO-DETALHE-V1", "BANCADA": "aquisicao-detalhe-v1",
          "COMMIT_DO_PASSO_2": "83385fe7", "ARVORE_FINAL": "f98f234c",
          "REGISTO": "curadoria/CONTRATOS-PASSO-2-V1.json"}


def _hash(c: dict) -> str:
    """A formula que o worker usa ao contratar: VERSAO dentro, HASH fora."""
    d = {k: v for k, v in c.items() if k != "SOURCE_CONTRACT_HASH"}
    d["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
    return EC.hash_do_contrato(d)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    so_ver = "--check" in argv

    reg = json.loads(REGISTO.read_text(encoding="utf-8"))
    tabela = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    por_id = {c["SOURCE_ID"]: c for c in tabela["FONTES"]}
    estado = LC.snapshot()

    aplicados, ja_iguais, recusados, fora = [], [], [], []
    for t in reg["TOCADAS"]:
        sid = t["SOURCE_ID"]
        c = por_id.get(sid)
        if not c:
            fora.append({"SOURCE_ID": sid, "PORQUE": "fonte da tabela do motor, "
                         "nao do curator — dono: regras/italy_contracts.mjs"})
            continue
        if c["ACQUISITION"] == t["DEPOIS"]:
            ja_iguais.append(sid)
            continue
        if c["ACQUISITION"] != t["ANTES"]:
            recusados.append({"SOURCE_ID": sid,
                              "PORQUE": "ACQUISITION local difere do ANTES do registo: "
                                        "alguem mexeu no meio; nao se aplica as cegas",
                              "LOCAL": c["ACQUISITION"], "ANTES_DO_REGISTO": t["ANTES"]})
            continue
        hash_antes = c.get("SOURCE_CONTRACT_HASH")
        novo = dict(c)
        novo["ACQUISITION"] = dict(t["DEPOIS"])
        novo["ROUTE_PROVENANCE"] = {
            **ORIGEM,
            "PROVA": t.get("PROVA"),
            "ITEM_REAL_QUE_O_PADRAO_CASA": t.get("ITEM_REAL_QUE_O_PADRAO_CASA"),
            "NAO_ITEM_QUE_O_PADRAO_EXCLUI": t.get("NAO_ITEM_QUE_O_PADRAO_EXCLUI"),
            "MAX_TARGETS_DERIVACAO": t.get("MAX_TARGETS_DERIVACAO"),
            "NOTA": t.get("NOTA") or "",
            "INTEGRADO_EM": datetime.now(timezone.utc).isoformat(),
            "INTEGRADO_POR": "curadoria/integrar_gate_de_detalhe.py (CANDIDATE-FEEDER-V1, PASSO 6)",
        }
        novo["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
        novo["SOURCE_CONTRACT_HASH"] = _hash(novo)
        _, falhas = VC.validar([novo])
        if falhas:
            recusados.append({"SOURCE_ID": sid, "PORQUE": "contrato corrigido reprovou "
                              "na validacao: %s" % str(falhas[0])[:200]})
            continue
        aplicados.append({
            "SOURCE_ID": sid, "NAME": c.get("NAME"),
            "ESTADO_NO_LIVRO": estado.get(sid),
            "MUDOU": t.get("MUDOU"),
            "INDEX_URL": {"ANTES": t["ANTES"].get("INDEX_URL"), "DEPOIS": t["DEPOIS"].get("INDEX_URL")},
            "MAX_TARGETS": {"ANTES": t["ANTES"].get("MAX_TARGETS"), "DEPOIS": t["DEPOIS"].get("MAX_TARGETS")},
            "LINK_PATTERN_DEPOIS": t["DEPOIS"].get("LINK_PATTERN"),
            "SOURCE_CONTRACT_HASH": {"ANTES": hash_antes, "DEPOIS": novo["SOURCE_CONTRACT_HASH"]},
        })
        if not so_ver:
            c.clear()
            c.update(novo)

    ready_com_contrato_novo = [a["SOURCE_ID"] for a in aplicados
                               if a["ESTADO_NO_LIVRO"] == LC.READY_FOR_COLLECTION]
    saida = {
        "DATASET": "DETAIL-GATE-INTEGRATION-V1",
        "LEI": ("integracao semantica, nao merge. O juiz vive em retrato_html.py + "
                "canario.py; a regua no worker; as rotas provadas entram na tabela do "
                "curator com procedencia. O livro NAO e tocado: READY com contrato novo "
                "e READY_LEGACY ate o worker remedir."),
        "ORIGEM": ORIGEM,
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "MODO": "CHECK" if so_ver else "APLICADO",
        "TOCADAS_NO_REGISTO": len(reg["TOCADAS"]),
        "APLICADOS": len(aplicados), "JA_IGUAIS": len(ja_iguais),
        "RECUSADOS": len(recusados), "FORA_DO_CURATOR": len(fora),
        "READY_LEGACY_COM_CONTRATO_NOVO": ready_com_contrato_novo,
        "HASH_DOS_77_NAO_SE_RECOMPOE": ("medido: o SOURCE_CONTRACT_HASH guardado nos 77 "
                                        "nao bate com hash_do_contrato() em nenhuma de tres "
                                        "formulas (sem HASH; sem HASH+VERSAO; sem HASH+VERSAO+"
                                        "ONBOARDED_BY). E carimbo de escrita, nao prova de "
                                        "conteudo. Divida registada; nao se corrige aqui."),
        "DETALHE_APLICADOS": aplicados, "DETALHE_JA_IGUAIS": ja_iguais,
        "DETALHE_RECUSADOS": recusados, "DETALHE_FORA_DO_CURATOR": fora,
    }
    if not so_ver:
        tabela["GERADO_EM"] = datetime.now(timezone.utc).isoformat()
        tabela.setdefault("NOTAS", [])
        nota = ("%d contratos com rota corrigida pela AQUISICAO-DETALHE-V1 (ver "
                "ROUTE_PROVENANCE em cada um e DETAIL-GATE-INTEGRATION-V1.json)"
                % (len(aplicados) + len(ja_iguais)))
        if nota not in tabela["NOTAS"]:
            tabela["NOTAS"].append(nota)
        CONTRATOS.write_text(json.dumps(tabela, ensure_ascii=False, indent=1) + "\n",
                             encoding="utf-8")
        SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")

    print("MODO                       %s" % saida["MODO"])
    print("TOCADAS no registo         %d" % saida["TOCADAS_NO_REGISTO"])
    print("APLICADOS (curator)        %d" % len(aplicados))
    print("JA_IGUAIS                  %d" % len(ja_iguais))
    print("RECUSADOS                  %d" % len(recusados))
    print("FORA_DO_CURATOR (motor)    %d" % len(fora))
    print("READY_LEGACY c/ contrato novo: %s" % ", ".join(ready_com_contrato_novo))
    for r in recusados:
        print("  RECUSADO %s: %s" % (r["SOURCE_ID"], r["PORQUE"][:120]))
    return 2 if recusados else 0


if __name__ == "__main__":
    raise SystemExit(main())
