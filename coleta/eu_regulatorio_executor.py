#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T4 · REGULATORIO — o executor que colhe um ato oficial e DECLARA o que colheu.

    python3 coleta/eu_regulatorio_executor.py --run-id=<RUN_ID> [CELEX]

POR QUE ESTE FICHEIRO EXISTE
----------------------------
O censo das classes mediu que T4 estava a UMA peca de atravessar a Collection
inteira: ja tinha regra de admissao escrita, ja tinha dono STRUCTURED
documental, e nao tinha AQUISICAO CANONICA. O executor que a receita nomeava
(`coleta/rotulos_baixar.py`) vai a um servlet do Ministero e declara o retorno
como `LEGADO/MANIFEST` — SUPORTE, e suporte nunca atravessa (COL-LAW-505).

    DECLARAR SUPORTE E INOFENSIVO MESMO QUANDO ERRADO: SUPORTE NAO ATRAVESSA.
    DECLARAR COLHEITA NAO E — E POR ISSO TEM DE SER A CORRIDA A DIZE-LO.

E POR QUE NAO SE CORRIGIU O OUTRO EXECUTOR
-------------------------------------------
Porque a fonte dele nao e alcancavel com a verificacao de TLS intacta:
`www.fitosanitari.salute.gov.it` nao envia a cadeia intermedia, e o erro e
`unable to get local issuer certificate`. Desligar a verificacao para a missao
passar seria fabricar o PASS pela porta dos fundos.

    UMA FONTE QUE NAO VERIFICA NAO SE TORNA VERIFICAVEL BAIXANDO A REGUA.

Entao mediram-se TODAS as fontes T4 aprovadas do atlas, e usou-se uma que
responde: `EU-T4-001`, o Publications Office da UE, `verdict = GREEN`,
`sabe_coletar = true`. Nao e uma fonte nova: e uma fonte que ja estava aprovada
e que ninguem tinha ligado a estrada canonica.

A ROTA E A QUE O PROPRIO CONTRATO DA FONTE DECLARA
---------------------------------------------------
O contrato de `EU-T4-001` (docs/operacao/CONTRATOS-DAS-FONTES-EAME.md) escreve,
no campo `fallback`:

    «EUR-Lex por CELEX (mesma casa, outra rota)»

Usa-se essa rota, e por um motivo tecnico medido: o CELLAR devolve XHTML, e o
derivador canonico desta casa extrai texto de PDF. O EUR-Lex devolve o MESMO
ato em PDF oficial. Escolher a rota que o contrato ja previa nao e inventar
fonte — e usar a fonte como ela se declara.

A IDENTIDADE, E ESTA E A PARTE RARA
------------------------------------
Pela primeira vez nesta casa um `DOCUMENT_ID` e ESCRITO em vez de ficar
`NAO SEI` — e escreve-se porque a FONTE o prova. O contrato de `EU-T4-001`
declara, textualmente:

    identity_keys: CELEX

O CELEX nao e o nosso sha, nao e o caminho no armazem, nao e a URL. E o nome
que o emissor da ao ato, e por isso cabe onde a lei o deixa caber.

    SHA E DOS BYTES. CAMINHO E MORADA. URL E ENDPOINT.
    CELEX E O NOME QUE O MUNDO DEU AO DOCUMENTO.

O QUE ESTE EXECUTOR NAO FAZ
---------------------------
Nao cunha corrida — recebe-a do orquestrador, como o adapter italiano.
Nao julga: nao decide se o ato serve, nem para que universo. Nao escreve em
`raw_asset`, `derived_artifact` nem em tabela nenhuma: larga bytes e DECLARA.
Nao inventa `SOURCE_ID`, `channel_id` nem `content_id`.
"""
import hashlib
import json
import os
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import retorno_da_coleta as rdc  # noqa: E402

EXECUTOR_ID = "regulatorio-eu"
EXECUTOR_VERSION = "adapter-v1"
PIPELINE_VERSION = "collection-v1"

# A FONTE, COMO O ATLAS A DECLARA. Nao se escreve aqui um nome bonito: escreve-se
# o identificador que o atlas ja usa, para que a ficha e a colheita falem do
# mesmo objecto.
SOURCE_ID = "EU-T4-001"
PUBLISHER = "Publications Office of the European Union"
COUNTRY_SCOPE = "EU"

# A rota declarada no contrato da fonte, no campo `fallback`. O `%s` e o CELEX,
# e o idioma vai no caminho porque e assim que o EUR-Lex o pede.
ROTA = ("https://eur-lex.europa.eu/legal-content/%(iso2)s/TXT/PDF/"
        "?uri=CELEX:%(celex)s")
UA = "SINTONIA-EAME/1.0 (colheita regulatoria; contacto no repositorio)"

# ⚠️ O ATO POR OMISSAO NAO FOI ESCOLHIDO POR MIM, E ISSO IMPORTA.
# A missao exige que o criterio do canario positivo seja registado ANTES de se
# ver o resultado da porta. O CELEX abaixo e o que a FICHA DA FONTE ja nomeia
# no campo `real_example`, escrito por outra missao, muito antes desta:
#
#     «CELEX 32026R1696 — Reg. Exec. (UE) 2026/1696, de 14/07/2026, renova a
#      aprovacao da substancia ativa acido pelargonico ...»
#
# Nao se varreu um catalogo a procura de um ato que casasse com o vocabulario
# da porta. Pegou-se no exemplo que a propria ficha da fonte declara.
#
#     ESCOLHER O CASO DEPOIS DE VER O RESULTADO E DESENHAR O ALVO A VOLTA DA
#     FLECHA. O CRITERIO TEM DE SER MAIS VELHO DO QUE A MEDICAO.
CELEX_POR_OMISSAO = "32026R1696"
IDIOMA = "IT"

# ⚠️ OS BYTES TEM DE ATERRAR ONDE A PORTA OS SABE PROCURAR, e isso nao e
# configuravel. `coleta/ingresso.py::ficha` resolve o `STORAGE_LOCATION`
# contra a RAIZ do repositorio: se os bytes estiverem fora dela, a porta nao
# os encontra e preserva o JSON do item NO LUGAR do documento — em silencio,
# e com um `raw_asset` que parece bom.
#
#     PRESERVAR O ITEM EM VEZ DO DOCUMENTO NAO DA ERRO: DA UM PDF QUE NAO EXISTE.
#
# A primeira versao disto tinha um `EU_OPS_ROOT` para isolar a medicao, e o
# envelope saiu com `PAYLOAD = AUSENTE`. A trava do contrato apanhou-o — mas
# so porque o executor foi honesto a declarar a ausencia. Uma variavel que
# parte a preservacao quando alguem a usa e uma armadilha com ar de opcao.
#
# A arvore nao suja: `data/raw/` e `data/colheita/` estao no `.gitignore`.
BALCAO = os.path.join("data", "colheita", "eu-regulatorio")
RETORNO = os.path.join(BALCAO, "RETORNO.json")
ARMAZEM = os.path.join("data", "raw", "eu-regulatorio")


class SemCorrida(ValueError):
    """Um executor que cunha a propria corrida nao e chamado: e um segundo
    pipeline com o mesmo nome.

        PROVENIENCIA E PROSPECTIVA — a corrida vem de quem a cunhou.
    """


def baixar(celex: str, iso2: str = IDIOMA) -> tuple:
    """→ (bytes, estado, url). Nunca levanta: o erro vira estado declarado.

    ⚠️ NAO HA `verify=False` NESTE FICHEIRO, e nao e por esquecimento. Uma
    fonte que nao verifica nao se torna verificavel baixando a regua: ela fica
    por colher, e isso diz-se alto.
    """
    url = ROTA % {"iso2": iso2, "celex": celex}
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/pdf,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            b = r.read()
    except Exception as ex:                                   # noqa: BLE001
        return b"", "ERRO_%s" % type(ex).__name__, url
    if not b:
        return b"", "VAZIO", url
    # HTML de erro devolvido com 200 e a armadilha classica destes portais.
    if b[:4] != b"%PDF":
        return b, "NAO_E_PDF", url
    return b, "OK", url


def preservar(b: bytes, celex: str, iso2: str = IDIOMA) -> str:
    """Larga os bytes e devolve o caminho RELATIVO a raiz do repositorio.

    O nome do ficheiro e o CELEX porque ele ja e a identidade do ato — mas o
    caminho continua a ser MORADA, e ninguem o le como identidade: quem quiser
    o `DOCUMENT_ID` le o campo, que viaja declarado ao lado.
    """
    destino = os.path.join(RAIZ, ARMAZEM, "%s-%s.pdf" % (celex, iso2))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "wb") as fh:
        fh.write(b)
    return os.path.join(ARMAZEM, "%s-%s.pdf" % (celex, iso2)).replace(
        os.sep, "/")


def observar(celex: str, run_id: str, iso2: str = IDIOMA) -> dict:
    """UMA observacao: o ato que a fonte publicou, como ela o publicou.

    ⚠️ UM ATO E UMA OBSERVACAO, E NAO UMA POR ARTIGO.
    Partir o ato em artigos seria DERIVAR, e derivar nao e observar: a fonte
    publicou um documento, e e esse documento que se preserva.

        O QUE SE OBSERVA E O QUE A FONTE PUBLICOU,
        E NAO O QUE NOS SABEMOS FAZER COM ISSO DEPOIS.
    """
    b, estado, url = baixar(celex, iso2)
    item = {
        "SOURCE_ID": SOURCE_ID,
        "SOURCE_URL": url,
        "PUBLISHER": PUBLISHER,
        "COUNTRY_SCOPE": COUNTRY_SCOPE,
        "ITEM_LANGUAGE": iso2.lower(),
        "EXECUTOR_ID": EXECUTOR_ID,
        "EXECUTOR_VERSION": EXECUTOR_VERSION,
        "PIPELINE_VERSION": PIPELINE_VERSION,
        # A FONTE PROVA ESTE, e por isso ele e escrito.
        "DOCUMENT_ID": celex,
        "RUN_ID": run_id,
    }
    if estado != "OK":
        # NAO COLHIDO NAO E COLHIDO E VAZIO. O erro vai declarado, e a unidade
        # nao entra na COLHEITA.
        return {"ESTADO": estado, "ITEM": item, "SHA256": "", "ONDE": ""}
    onde = preservar(b, celex, iso2)
    item["STORAGE_LOCATION"] = onde
    return {"ESTADO": "OK", "ITEM": item,
            "SHA256": hashlib.sha256(b).hexdigest(), "ONDE": onde}


def declarar(colhidas: list, erros: list, run_id: str,
             raiz: str = RAIZ) -> str:
    """O ENVELOPE — a corrida diz o que produziu (COL-LAW-505)."""
    unidades = []
    for c in colhidas:
        unidades.append({
            **c["ITEM"],
            "ESPECIE": rdc.COLHEITA,
            "SOURCE_ID": SOURCE_ID,
            "DOCUMENT_ID": c["ITEM"].get("DOCUMENT_ID") or rdc.NAO_SEI,
            "SHA256": c["SHA256"],
            "RUN_ID": run_id,
            "PAYLOAD": {"ONDE": c["ONDE"],
                        "ESTADO": rdc.estado_do_payload(c["ONDE"], raiz)},
        })
    envelope = {
        "RUN_ID": run_id,
        "EXECUTOR_ID": EXECUTOR_ID,
        "EXECUTOR_VERSION": EXECUTOR_VERSION,
        # ZERO ATOS NAO E FALHA: `EMPTY_SUCCESS != ERROR`. Mas um ato pedido
        # que nao veio E um erro, e vai escrito.
        "ESTADO": rdc.SUCCESS if not erros else rdc.PARTIAL,
        "COLHEITA": unidades,
        "SUPORTE": [],
        "ERROS": erros,
    }
    destino = os.path.join(raiz, RETORNO)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(envelope, fh, ensure_ascii=False, indent=1)
    return RETORNO.replace(os.sep, "/")


def colher(run_id: str, celex: str = "", iso2: str = IDIOMA,
           raiz: str = RAIZ) -> dict:
    if not str(run_id or "").strip():
        raise SemCorrida(
            "este executor nao cunha corrida: o RUN_ID vem do orquestrador")
    alvo = celex or CELEX_POR_OMISSAO
    r = observar(alvo, run_id, iso2)
    colhidas = [r] if r["ESTADO"] == "OK" else []
    erros = ([] if r["ESTADO"] == "OK" else
             [{"CELEX": alvo, "ESTADO": r["ESTADO"],
               "ONDE": r["ITEM"].get("SOURCE_URL", "")}])
    onde = declarar(colhidas, erros, run_id, raiz)
    return {"RUN_ID": run_id, "CELEX": alvo, "ESTADO": r["ESTADO"],
            "COLHIDAS": len(colhidas), "DECLAROU_EM": onde}


def main() -> int:
    run_id, celex = "", ""
    for a in sys.argv[1:]:
        if a.startswith("--run-id="):
            run_id = a.split("=", 1)[1]
        elif not a.startswith("--"):
            celex = a
    if not run_id:
        print("uso: python3 coleta/eu_regulatorio_executor.py "
              "--run-id=<RUN_ID> [CELEX]", file=sys.stderr)
        print("     este adapter NAO cunha corrida: o RUN_ID vem do "
              "orquestrador.", file=sys.stderr)
        return 2
    r = colher(run_id, celex)
    print("T4 · %s · %s · colhidas=%d · declarou em %s"
          % (r["CELEX"], r["ESTADO"], r["COLHIDAS"], r["DECLAROU_EM"]))
    return 0 if r["ESTADO"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
