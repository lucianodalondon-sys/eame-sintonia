#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROCESSAR O TEMPO E O LUGAR DO QUE JÁ ESTÁ NA SALA — pela porta, sem rede.

D68 (dono, 25/09): as notícias JÁ coletadas também se arrumam. Para cada linha
da Sala, refaz-se SÓ a extracção de tempo e lugar, com o código novo, a partir
do que está guardado:

    o livro do coletor (pela RAW_SHA256 do bruto)  -> italy_executor.tempo_e_lugar
    o texto que a linha guardou                    -> leis/fato_do_texto (LUGAR-FATO)
    as duas coisas pela MESMA estrada da produção  -> orquestrador.item_documental_para_a_porta
                                                     -> admissao.pronto_para_inteligencia

e o resultado entra como REVISÃO (`sala_de_espera.rever`, migration 033):

    O RAW NÃO MUDA. A LINHA NÃO MUDA. NUNCA HÁ UPDATE CALADO.

Cada revisão diz o extractor, a VERSÃO (sha256 do código que a produziu), a
data e o porquê. Correr duas vezes com o mesmo código não escreve nada.

    py admissao/reprocessar_tempo_lugar.py --livros "<glob;glob>" [--aplicar] [--saida recibo.json]

Sem `--aplicar` só conta o que MUDARIA (e não escreve). Precisa da Sala
canónica (`SINTONIA_SALA_BACKEND=POSTGRES` + `SINTONIA_SALA_DSN`): o backend
de ficheiro não tem revisões e recusa.

O que NÃO faz: não abre rede, não relê páginas de índice (não foram guardadas),
não corre o extractor de publicação da página (é da nuvem tempo-publicacao e
ainda não chegou), não toca em raw_asset, derived_artifact nem na linha.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import admissao as adm  # noqa: E402
import italy_executor as ex  # noqa: E402
import orquestrador as ORQ  # noqa: E402
import sala_de_espera as espera  # noqa: E402

RAIZ = os.path.dirname(HERE)
EXTRATOR = ("admissao/reprocessar_tempo_lugar.py · coleta/italy_executor.tempo_e_lugar"
            " + leis/fato_do_texto.campos_do_fato + admissao.pronto_para_inteligencia")
MOTIVO = ("TEMPO-E-LUGAR (D61-D68): reprocessamento sem rede do tempo e do lugar "
          "a partir do livro do coletor e do texto guardado; a linha original nao muda")

#: O código que produz o resultado. A versão É o sha256 dele: outro código,
#: outra versão; o mesmo código, a mesma versão.
#: ⚠️ LEITOR-DATA-YOUTUBE (26/09): `coleta/executor_texto_de_html.py` e o leitor da pagina que
#: `italy_executor.tempo_e_lugar` chama desde a DA-9 (a PUBLICACAO). Faltava aqui: um conserto
#: nele saia com o carimbo da versao antiga.
CODIGO_DA_VERSAO = ("admissao/reprocessar_tempo_lugar.py", "admissao/admissao.py",
                    "coleta/italy_executor.py", "coleta/executor_texto_de_html.py", "coleta/ingresso.py",
                    "orquestrador/orquestrador.py", "leis/fato_do_texto.py",
                    "leis/fato_local.py", "regras/contratos_de_fonte.py",
                    "regras/italy_contracts.mjs")

#: campo da Sala -> (valor no READY, base no READY)
REVISTOS = (("published_at", "PUBLISHED_AT", "PUBLISHED_AT_BASIS"),
            ("source_location", "SOURCE_LOCATION", "SOURCE_LOCATION_BASIS"),
            ("fact_time", "FACT_TIME", "FACT_TIME_BASIS"),
            ("fact_location", "FACT_LOCATION", "FACT_LOCATION_BASIS"))


def versao_do_codigo():
    h = hashlib.sha256()
    for rel in CODIGO_DA_VERSAO:
        with open(os.path.join(RAIZ, rel), "rb") as fh:
            # o fim de linha nao e codigo: CRLF e LF dao a mesma versao
            h.update(fh.read().replace(b"\r\n", b"\n"))
    return "tempo-lugar@" + h.hexdigest()[:16]


def livros_por_sha(padroes):
    """`{RAW_SHA256: observacao}`. A primeira que tiver RAW_PATH ganha."""
    fora = {}
    for padrao in padroes:
        for f in sorted(glob.glob(padrao)):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for linha in fh:
                    try:
                        o = json.loads(linha)
                    except json.JSONDecodeError:
                        continue
                    s = o.get("RAW_SHA256")
                    if s and (s not in fora or (o.get("RAW_PATH")
                                                and not fora[s].get("RAW_PATH"))):
                        fora[s] = o
    return fora


def bytes_guardados(linha, raizes):
    """Os bytes do bruto no armazem, SO com o sha256 certo (DA-9: o leitor da pagina)."""
    if not linha.get("STORAGE_PATH") or "html" not in (linha.get("MEDIA_TYPE") or ""):
        return None
    for raiz in raizes:
        for cand in glob.glob(os.path.join(raiz, linha["STORAGE_PATH"])):
            try:
                dados = open(cand, "rb").read()
            except OSError:
                continue
            if hashlib.sha256(dados).hexdigest() == linha["SHA256"]:
                return dados
    return None


def ready_de(linha, obs, dados=None):
    """O READY que a estrada de hoje daria a esta linha — sem rede e sem banco."""
    tl = ex.tempo_e_lugar(obs or {"SOURCE_ID": linha["SOURCE_ID"]}, dados)
    item_id = str(linha["ITEM_ID"])
    est = {"SOURCE_ID": linha["SOURCE_ID"], "TEXTO": linha["TEXTO"],
           "DERIVED_ARTIFACT_ID": item_id.split(":", 1)[-1],
           "RAW_ASSET_ID": linha["RAW_OBSERVATION_ID"],
           "PARENT_SHA256": linha["SHA256"] or None,
           "CAPTURED_AT": linha["CAPTURED_AT"], "TEMPO_E_LUGAR": tl}
    item = ORQ.item_documental_para_a_porta(est, source_id=linha["SOURCE_ID"])
    # a linha JA foi admitida: a decisao nao se refaz, so os campos
    d = adm.Decisao(item=item_id, universo=linha["UNIVERSO"], resultado=adm.SIM,
                    regra="reprocessamento tempo-lugar", motivo=MOTIVO)
    return adm.pronto_para_inteligencia(item, d)


def revisoes_de(ready):
    fora = [{"CAMPO": c, "VALOR": ready[v], "BASE": ready[b]} for c, v, b in REVISTOS]
    fora.append({"CAMPO": "completude_tempo_lugar",
                 "VALOR": json.dumps(ready["COMPLETUDE_TEMPO_LUGAR"],
                                     ensure_ascii=False, sort_keys=True),
                 "BASE": "admissao.completude_tempo_lugar sobre os valores revistos"})
    fora.append({"CAMPO": "tempo_lugar_evidencia",
                 "VALOR": json.dumps(ready["TEMPO_LUGAR_EVIDENCIA"],
                                     ensure_ascii=False, sort_keys=True),
                 "BASE": "leis/fato_do_texto.campos_do_fato (DA-7)"})
    return fora


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--livros", required=True,
                    help="globs dos livros do coletor (observations.ndjson), separados por ;")
    ap.add_argument("--raizes", default="",
                    help="onde estao os bytes guardados (armazem), separados por ;"
                         " — para o leitor da pagina (DA-9); sem isto, so o contrato")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args(argv)
    espera.exigir_canonica()
    versao = versao_do_codigo()
    livros = livros_por_sha([x for x in a.livros.split(";") if x])
    linhas = espera.linhas_para_revisao()
    raizes = [x for x in a.raizes.split(";") if x]
    conta = {"LINHAS": len(linhas), "SEM_LIVRO": 0, "COM_PAGINA": 0,
             "INSERIDAS": 0, "JA_ERAM_ASSIM": 0}
    por_campo = {c: 0 for c, _, _ in REVISTOS}
    itens = []
    for linha in linhas:
        obs = livros.get(linha["SHA256"])
        if obs is None:
            conta["SEM_LIVRO"] += 1
        dados = bytes_guardados(linha, raizes) if raizes else None
        conta["COM_PAGINA"] += dados is not None
        ready = ready_de(linha, obs, dados)
        revs = revisoes_de(ready)
        for r in revs:
            if r["CAMPO"] in por_campo and r["VALOR"] != adm.AUSENCIA:
                por_campo[r["CAMPO"]] += 1
        recibo = None
        if a.aplicar:
            recibo = espera.rever(linha["RUN_ID"], linha["ORDEM"], revs,
                                  extrator=EXTRATOR, versao=versao, motivo=MOTIVO)
            conta["INSERIDAS"] += recibo["INSERIDAS"]
            conta["JA_ERAM_ASSIM"] += recibo["JA_ERAM_ASSIM"]
        itens.append({"RUN_ID": linha["RUN_ID"], "ORDEM": linha["ORDEM"],
                      "SOURCE_ID": linha["SOURCE_ID"], "LIVRO": obs is not None,
                      "REVISOES": revs, "RECIBO": recibo})
    fora = {"APLICOU": a.aplicar, "VERSAO_DO_EXTRATOR": versao, "EXTRATOR": EXTRATOR,
            "CONTA": conta, "SAEM_DE_NAO_SEI": por_campo, "ITENS": itens}
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: fora[k] for k in ("APLICOU", "VERSAO_DO_EXTRATOR", "CONTA",
                                           "SAEM_DE_NAO_SEI")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
