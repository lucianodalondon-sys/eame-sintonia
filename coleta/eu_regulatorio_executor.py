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
import tempfile
import time
import urllib.error
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


# ⚠️ OS ESTADOS DA IDA A FONTE, E POR QUE SAO MAIS DO QUE DOIS.
# A primeira versao tinha `OK` e `VAZIO`. Entao o EUR-Lex comecou a responder
# `202` com corpo vazio — que e um servidor a dizer «aceitei, volta mais
# tarde» — e o executor chamou-lhe `VAZIO`, que se le como «a fonte nao tinha
# nada».
#
#     A FONTE QUE ME TRAVA NAO E A FONTE QUE NAO TEM NADA.
#     CONFUNDIR AS DUAS FAZ UMA CORRIDA TRAVADA PARECER UMA COLHEITA VAZIA.
#
# `EMPTY_SUCCESS != ERROR` continua a valer: uma fonte que responde e nao tem
# nada e um sucesso vazio. O que nao pode e um travao passar por isso.
OK = "OK"
VAZIO = "VAZIO"                       # respondeu, e nao havia nada
FONTE_INDISPONIVEL = "FONTE_INDISPONIVEL"   # travou-me, ou esta em baixo
NAO_E_PDF = "NAO_E_PDF"
DO_ARQUIVO = "DO_ARQUIVO_LOCAL"       # nao fui a rede: ja tinha estes bytes

# Os codigos com que um servidor diz «agora nao»: aceite-mas-nao-pronto,
# pedidos a mais, e serviço indisponivel.
TRAVOU = (202, 429, 503)

# ⚠️ A CORTESIA NAO E ENFEITE, E ISTO FOI MEDIDO DA MANEIRA CARA.
# Este executor foi a mesma fonte dez vezes em duas horas, sem pausa e sem
# reaproveitar o que ja tinha em disco. O EUR-Lex passou a responder `202` a
# TUDO — qualquer formato, qualquer CELEX. Foi a nossa propria pressa que
# fechou a porta.
#
#     UM COLETOR SEM CORTESIA NAO PERDE UM DOCUMENTO: PERDE A FONTE.
PAUSA_ENTRE_IDAS = 2.0
TENTATIVAS = 3
ESPERA_INICIAL = 5.0


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
    espera = ESPERA_INICIAL
    for tentativa in range(1, TENTATIVAS + 1):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept": "application/pdf,*/*"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                codigo, b = r.status, r.read()
        except urllib.error.HTTPError as ex:
            codigo, b = ex.code, b""
        except Exception as ex:                               # noqa: BLE001
            return b"", "ERRO_%s" % type(ex).__name__, url
        if b[:4] == b"%PDF":
            return b, OK, url
        # ── O SERVIDOR DISSE «AGORA NAO» ────────────────────────────────
        # Nao e vazio, nao e erro nosso, e nao se insiste de imediato.
        if codigo in TRAVOU or (codigo == 200 and not b):
            if tentativa < TENTATIVAS:
                time.sleep(espera)
                espera *= 2
                continue
            return b"", FONTE_INDISPONIVEL, url
        if not b:
            return b"", VAZIO, url
        # HTML de erro devolvido com 200 e a armadilha classica destes portais.
        return b, NAO_E_PDF, url
    return b"", FONTE_INDISPONIVEL, url


def _bytes_que_ja_temos(celex: str, iso2: str = IDIOMA):
    """Os bytes deste ato que esta arvore ja preservou, ou `None`.

    ⚠️ SO CONTA SE FOREM MESMO UM PDF. Um ficheiro truncado por uma corrida
    interrompida tem o nome certo e nao serve — e reaproveita-lo em silencio
    poria a corrida seguinte a derivar lixo com cara de documento.

        TER UM FICHEIRO COM O NOME CERTO NAO E TER O DOCUMENTO.
    """
    caminho = os.path.join(RAIZ, ARMAZEM, "%s-%s.pdf" % (celex, iso2))
    if not os.path.isfile(caminho):
        return None
    try:
        with open(caminho, "rb") as fh:
            b = fh.read()
    except OSError:
        return None
    return b if b[:4] == b"%PDF" else None


def preservar(b: bytes, celex: str, iso2: str = IDIOMA) -> str:
    """Larga os bytes e devolve o caminho RELATIVO a raiz do repositorio.

    O nome do ficheiro e o CELEX porque ele ja e a identidade do ato — mas o
    caminho continua a ser MORADA, e ninguem o le como identidade: quem quiser
    o `DOCUMENT_ID` le o campo, que viaja declarado ao lado.
    """
    destino = os.path.join(RAIZ, ARMAZEM, "%s-%s.pdf" % (celex, iso2))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    # ⚠️ ESCRITA ATOMICA, E ISTO CUSTOU DUAS CORRIDAS EM VINTE.
    # A primeira versao fazia `open(destino, "wb")` e escrevia por cima. Duas
    # corridas concorrentes do mesmo ato davam isto:
    #
    #     A abre o ficheiro (trunca para zero) e comeca a escrever
    #     B le o mesmo caminho  ->  nao comeca por %PDF  ->  «nao tenho isto»
    #     B vai a rede          ->  a fonte estava a travar  ->  corrida perde
    #
    # O ficheiro nunca ficou corrompido no fim — mas houve um INSTANTE em que
    # ele nao era um PDF, e a corrida que leu nesse instante pagou.
    #
    #     UM FICHEIRO A MEIO DE SER ESCRITO NAO E UM FICHEIRO VAZIO:
    #     E UM FICHEIRO QUE MENTE DURANTE UNS MILISSEGUNDOS.
    #
    # Corpo inteiro num temporario NA MESMA pasta, `fsync`, e so entao
    # `os.replace` — atomico no POSIX. Quem ler durante a escrita ve o
    # ficheiro ANTERIOR, inteiro. E a mesma cura da Sala de Espera e do livro
    # de decisoes: tres sitios, um so defeito.
    fd, temporario = tempfile.mkstemp(prefix=".eu-", suffix=".pdf",
                                      dir=os.path.dirname(destino))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(b)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporario, destino)
        temporario = None
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)
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
    # ⚠️ PRIMEIRO VE-SE O QUE JA SE TEM. Ir buscar outra vez bytes que ja
    # estao preservados nao traz informacao nenhuma — traz um pedido a mais a
    # uma fonte publica, e foi assim que este executor se fez travar.
    #
    #     O QUE JA ESTA PRESERVADO NAO SE VAI BUSCAR OUTRA VEZ.
    #
    # E ISTO DIZ-SE. Uma corrida que reaproveitou bytes locais NAO provou
    # aquisicao, e quem le o envelope tem de conseguir ver a diferenca:
    # `ORIGEM_DOS_BYTES` viaja declarado.
    b, estado, url = b"", "", ROTA % {"iso2": iso2, "celex": celex}
    ja = _bytes_que_ja_temos(celex, iso2)
    if ja is not None:
        b, estado = ja, DO_ARQUIVO
    else:
        b, estado, url = baixar(celex, iso2)
        time.sleep(PAUSA_ENTRE_IDAS)
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
        "ORIGEM_DOS_BYTES": "REDE" if estado == OK else (
            "ARQUIVO_LOCAL" if estado == DO_ARQUIVO else "NENHUMA"),
    }
    if estado not in (OK, DO_ARQUIVO):
        # NAO COLHIDO NAO E COLHIDO E VAZIO. O erro vai declarado, e a unidade
        # nao entra na COLHEITA.
        return {"ESTADO": estado, "ITEM": item, "SHA256": "", "ONDE": ""}
    # ⚠️ E NAO SE REESCREVE O QUE JA ESTAVA LA.
    # Quando os bytes vieram do arquivo local, grava-los outra vez e escrever
    # exactamente o mesmo conteudo por cima de si proprio — zero informacao
    # nova, e uma janela de escrita a mais para outra corrida apanhar.
    #
    #     A ESCRITA MAIS SEGURA E A QUE NAO ACONTECE.
    if estado == DO_ARQUIVO:
        onde = os.path.join(ARMAZEM, "%s-%s.pdf" % (celex, iso2)).replace(
            os.sep, "/")
    else:
        onde = preservar(b, celex, iso2)
    item["STORAGE_LOCATION"] = onde
    return {"ESTADO": estado, "ITEM": item,
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
    # ⚠️ O ENDERECO E DA CORRIDA, E A REGRA NAO E DESTE FICHEIRO.
    # Escrever sempre no mesmo sitio fazia duas corridas do mesmo executor
    # colidirem, e a segunda apagava a primeira sem ninguem notar (`G-ENV-01`).
    # Quem sabe onde vive o envelope de uma corrida e `leis/retorno_da_coleta`.
    #
    # ISTO NAO FAZ DESTE EXECUTOR O DONO DA CORRIDA: ele recebe o `run_id` do
    # orquestrador e USA-O como endereco. Transportar e usar o contexto que
    # lhe deram; decidir a identidade seria outra coisa, e continua a nao ser
    # dele.
    onde = rdc.endereco_do_envelope(RETORNO.replace(os.sep, "/"), run_id)
    destino = os.path.join(raiz, onde)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(envelope, fh, ensure_ascii=False, indent=1)
    return onde


def colher(run_id: str, celex: str = "", iso2: str = IDIOMA,
           raiz: str = RAIZ) -> dict:
    if not str(run_id or "").strip():
        raise SemCorrida(
            "este executor nao cunha corrida: o RUN_ID vem do orquestrador")
    alvo = celex or CELEX_POR_OMISSAO
    r = observar(alvo, run_id, iso2)
    bom = r["ESTADO"] in (OK, DO_ARQUIVO)
    colhidas = [r] if bom else []
    erros = ([] if bom else
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
    return 0 if r["ESTADO"] in (OK, DO_ARQUIVO) else 1


if __name__ == "__main__":
    raise SystemExit(main())
