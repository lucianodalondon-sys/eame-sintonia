#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUGAR-DO-PUBLICADOR · a porta que leva a SEDE de quem publica (SOURCE_LOCATION) do contrato para a Sala.

So o LUGAR DA FONTE. Os outros tres campos (publicacao, data e lugar do facto) NAO se refazem aqui: o
reprocessamento geral (`admissao/reprocessar_tempo_lugar.py`) refaz os quatro com o codigo do dia e mexia em
campos fora desta missao.

Para cada linha da Sala (pela vista `sala_de_espera_atual`):
  · o SOURCE_LOCATION sai de `regras/contratos_de_fonte.lugar_da_fonte` — A MESMA funcao que a estrada da
    producao usa (`italy_executor.tempo_e_lugar`), lida do contrato (tabela do coletor ou contrato a mao);
  · so se escreve quando o contrato DA um lugar e a Sala diz outra coisa. NAO SEI nunca pisa um valor;
  · `completude_tempo_lugar` acompanha: so a chave LOCAL_DA_FONTE muda e PROVADAS e recontada;
  · entra como REVISAO (`sala_de_espera.rever`, migration 033, append-only): a linha e o RAW nao mudam;
    correr duas vezes com o mesmo contrato nao escreve nada.

Por omissao SO MOSTRA. `--aplicar` escreve (na Sala que `SINTONIA_SALA_DSN` apontar — ensaio: a copia).

    py ferramentas/lugar_publicador/preencher_sede_na_sala.py [--aplicar] [--saida recibo.json]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "admissao"))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import admissao as adm  # noqa: E402
import contratos_de_fonte as CDF  # noqa: E402
import sala_de_espera as espera  # noqa: E402

EXTRATOR = ("ferramentas/lugar_publicador/preencher_sede_na_sala.py · "
            "regras/contratos_de_fonte.lugar_da_fonte (a mesma de italy_executor.tempo_e_lugar)")
MOTIVO = ("LUGAR-DO-PUBLICADOR (D83): a sede de quem publica, provada na pagina da propria fonte e escrita no "
          "contrato; so SOURCE_LOCATION e a completude; a linha original nao muda")
CODIGO_DA_VERSAO = ("ferramentas/lugar_publicador/preencher_sede_na_sala.py", "regras/contratos_de_fonte.py",
                    "regras/italy_contracts.mjs", "regras/italy_contracts_onboarded.json", "leis/fato_local.py")
VAZIOS = (None, "", adm.AUSENCIA, "NAO_SEI", "NÃO SEI")


def versao_do_codigo():
    """O codigo E o contrato que produzem o valor: outra tabela, outra versao."""
    h = hashlib.sha256()
    for rel in CODIGO_DA_VERSAO:
        with open(os.path.join(RAIZ, rel), "rb") as fh:
            h.update(fh.read().replace(b"\r\n", b"\n"))
    return "sede-publicador@" + h.hexdigest()[:16]


def completude_com_sede(atual: dict, tem_sede: bool) -> dict:
    fora = dict(atual)
    fora["LOCAL_DA_FONTE"] = adm.COMPLETUDE_PROVADA if tem_sede else adm.AUSENCIA
    fora["PROVADAS"] = sum(1 for n, _, _ in adm.QUATRO_DO_TEMPO_E_LUGAR if fora.get(n) not in (None, adm.AUSENCIA))
    return {k: fora[k] for k in sorted(fora)}


def revisoes_da_linha(u: dict):
    """-> (revisoes, porque). Lista vazia = nada a escrever nesta linha."""
    r = CDF.lugar_da_fonte(u["SOURCE_ID"])
    if r["VALOR"] in VAZIOS:
        return [], "o contrato nao da sede (%s)" % r["PORQUE"][:120]
    if u["SOURCE_LOCATION"] == r["VALOR"]:
        return [], "JA_E_ASSIM"
    if u["SOURCE_LOCATION"] not in VAZIOS:
        return [], "a Sala ja tem outra sede (%s); nao se pisa" % u["SOURCE_LOCATION"]
    c = CDF.lugar_para_o_contrato(r)
    return ([{"CAMPO": "source_location", "VALOR": c["SOURCE_LOCATION"], "BASE": c["SOURCE_LOCATION_BASIS"]},
             {"CAMPO": "completude_tempo_lugar",
              "VALOR": json.dumps(completude_com_sede(u["COMPLETUDE_TEMPO_LUGAR"], True), ensure_ascii=False,
                                  sort_keys=True),
              "BASE": "admissao.completude_tempo_lugar: so LOCAL_DA_FONTE muda (LUGAR-DO-PUBLICADOR)"}],
            r["PORQUE"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args(argv)
    espera.exigir_canonica()
    versao = versao_do_codigo()
    runs = sorted({l["RUN_ID"] for l in espera.linhas_para_revisao()})
    conta = collections.Counter()
    itens = []
    for run in runs:
        for u in espera.ler_atual(run) or []:
            conta["LINHAS"] += 1
            revs, porque = revisoes_da_linha(u)
            recibo = None
            if revs:
                conta["GANHAM_SEDE"] += 1
                if a.aplicar:
                    recibo = espera.rever(run, u["ORDEM"], revs, extrator=EXTRATOR, versao=versao, motivo=MOTIVO)
                    conta["INSERIDAS"] += recibo["INSERIDAS"]
                    conta["JA_ERAM_ASSIM"] += recibo["JA_ERAM_ASSIM"]
            elif porque == "JA_E_ASSIM":
                conta["JA_TINHAM_A_MESMA"] += 1
            else:
                conta["FICAM_NAO_SEI" if u["SOURCE_LOCATION"] in VAZIOS else "FICAM_COM_A_SUA"] += 1
            itens.append({"RUN_ID": run, "ORDEM": u["ORDEM"], "SOURCE_ID": u["SOURCE_ID"],
                          "ANTES": u["SOURCE_LOCATION"],
                          "DEPOIS": revs[0]["VALOR"] if revs else u["SOURCE_LOCATION"],
                          "PORQUE": porque, "RECIBO": recibo})
    fora = {"APLICOU": a.aplicar, "VERSAO": versao, "EXTRATOR": EXTRATOR, "CONTA": dict(conta),
            "COM_SEDE_DEPOIS": sum(1 for i in itens if i["DEPOIS"] not in VAZIOS),
            "FONTES_COM_SEDE_DEPOIS": len({i["SOURCE_ID"] for i in itens if i["DEPOIS"] not in VAZIOS}),
            "POR_SEDE": dict(collections.Counter(i["DEPOIS"] for i in itens)), "ITENS": itens}
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in fora.items() if k != "ITENS"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
