#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROCESSAR ANTES DE RECOLETAR — o material que já está guardado, medido outra vez.

    A pergunta: a Collection consegue preservar e entregar à Sala de Espera os
    factos e identidades que JÁ EXISTEM no material, sem fabricar o que falta?

Esta prova não colhe nada. Não abre rede, não chama coletor, não cria observação
nova. Ela pega no que está no disco desta árvore —

    data/collection-ledger/italy/observations.ndjson   o livro do coletor
    data/derivados/texto/RAW-*.txt                     os textos já extraídos
    regras/italy_contracts.mjs                         os contratos de fonte
    data/samples/ES-T4-001/eppo-dictionary.json        a autoridade taxonómica

— e atravessa a estrada inteira até ao contrato `READY`, dizendo, campo a campo,
o que foi PRESERVADO, o que foi NORMALIZADO com que prova, e o que continua
`NAO SEI` — e porquê.

⚠️ O QUE ESTA PROVA NÃO FAZ, E É METADE DO VALOR DELA.

Ela não preenche `FACT_TIME`. Ela não preenche `FACT_LOCATION`. Não porque não
tentou: porque **o material não prova nenhum dos dois**, e isso mede-se aqui em
vez de se adivinhar. O objectivo nunca foi encher campos.

    O ALVO NÃO É MAIS CAMPOS PREENCHIDOS.
    É O CONHECIDO PRESERVADO E O DESCONHECIDO A CONTINUAR DESCONHECIDO.

⚠️ E NÃO SE FABRICA OBSERVAÇÃO NOVA. Cada unidade que sai daqui aponta para a
MESMA observação bruta de onde nasceu — `RAW_SHA256` do livro, que é a chave que
liga o texto derivado ao ficheiro original. Reprocessar é olhar outra vez para o
mesmo bruto; fingir uma colheita nova seria inventar uma corrida que não houve.

    REPROCESSAMENTO != NOVA AQUISIÇÃO.

Saída: `data/derivados/A-COLLECTION-PRESERVA-O-FATO.json`
"""
from __future__ import annotations

import glob
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ⚠️ O PREÂMBULO É O DA CASA, E ISTO CUSTOU UM ERRO DE COLETA.
# `from admissao import admissao` funciona quando isto corre sozinho e REBENTA
# quando outro ficheiro já pôs `admissao/` em `sys.path`: aí o nome `admissao`
# resolve para o MÓDULO e não para o pacote.
#
#     UM IMPORT QUE DEPENDE DE QUEM CORREU ANTES NÃO É UM IMPORT: É UMA APOSTA.
for _g in (RAIZ, os.path.join(RAIZ, "admissao")):
    if _g not in sys.path:
        sys.path.insert(0, _g)

import admissao  # noqa: E402
import sala_de_espera as espera  # noqa: E402
from coleta import ingresso  # noqa: E402
from coleta import rota_forward_documento as rota  # noqa: E402
from leis import artefato as art  # noqa: E402
from leis import fato_local as fl  # noqa: E402
from regras import contratos_de_fonte as cdf  # noqa: E402
import motor.normalize_agro as agro  # noqa: E402

LIVRO = os.path.join(RAIZ, "data", "collection-ledger", "italy",
                     "observations.ndjson")
TEXTOS = os.path.join(RAIZ, "data", "derivados", "texto")
SAIDA = os.path.join(RAIZ, "data", "derivados",
                     "A-COLLECTION-PRESERVA-O-FATO.json")

VERSAO_DO_REPROCESSAMENTO = "reprocessamento-v1"

#: Nomes comuns italianos de problema que os boletins usam e que esta árvore NÃO
#: sabe traduzir para EPPO. Declarados para a lacuna ser CONTÁVEL — e não para
#: virarem código nenhum. Lidos dos próprios boletins desta árvore.
TERMOS_ITALIANOS_SEM_AUTORIDADE = (
    "peronospora", "oidio", "botrite", "ticchiolatura", "mosca dell'olivo",
    "tignola", "cocciniglia", "cercospora", "antracnosi", "muffa grigia",
)


def observacoes():
    """O livro do coletor, tal como está. Uma linha ilegível FALHA, não sai."""
    fora = []
    with open(LIVRO, encoding="utf-8") as fh:
        for n, linha in enumerate(fh, 1):
            if not linha.strip():
                continue
            try:
                fora.append(json.loads(linha))
            except json.JSONDecodeError as e:
                raise ValueError(
                    "linha %d do livro do coletor nao e JSON (%s). NAO se "
                    "salta: um livro com um buraco nao e um livro com menos "
                    "uma linha." % (n, e)) from e
    return fora


def textos_por_impressao():
    """`{primeiros 16 do sha256: caminho}`.

    O nome do ficheiro derivado é `RAW-<16 primeiros do sha256 do original>`, e
    é essa a ponte entre o texto e a observação que o gerou. Não é uma
    convenção inventada aqui: é a que está no disco.

    ⚠️ E 16 DÍGITOS NÃO SÃO O SHA256. Isto liga o texto ao bruto para efeito de
    LEITURA; a linhagem canónica continua a ser `RAW_OBSERVATION_ID =
    raw_asset.id` (COL-LAW-043), e esta prova não a substitui nem a fabrica.
    """
    fora = {}
    for caminho in sorted(glob.glob(os.path.join(TEXTOS, "RAW-*.txt"))):
        chave = os.path.basename(caminho)[4:-4].lower()
        fora[chave] = caminho
    return fora


def unidade_reprocessada(obs, caminho_do_texto):
    """A unidade STRUCTURED enriquecida — e o recibo de como cada campo lá foi parar.

    Devolve `(unidade, recibo)`. A unidade fala a língua do contrato comum
    (`leis/artefato.py`), que é a que `ingresso.para_a_porta()` sabe traduzir.
    """
    sid = obs["SOURCE_ID"]
    texto = open(caminho_do_texto, encoding="utf-8", errors="replace").read()

    # ── ONDE ESTÁ QUEM PUBLICA ─────────────────────────────────────────────
    # Declarado no contrato de fonte, conferido contra o gazetteer. Nunca
    # deduzido da URL, do domínio nem do nome do ficheiro.
    lugar_fonte = cdf.lugar_declarado_pela_fonte(sid)

    # ── ONDE ACONTECEU O FACTO ─────────────────────────────────────────────
    # ⚠️ AQUI ESTÁ A RECUSA MAIS IMPORTANTE DESTA PROVA.
    # O contrato manda procurar a província do ficheiro, e a província ESTÁ
    # escrita no documento — «BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI
    # SALERNO». A tentação é promover isso a `FACT_LOCATION`, e seria errado:
    # aquilo é a ABRANGÊNCIA do boletim, não o sítio de um acontecimento.
    #
    #     TERRITORIAL_LIST != FACT_LIST   (leis/fato_local.py)
    #     PLACE_MENTION    != FACT_LOCATION (COL-LAW-032)
    #
    # Quem decide é o dono — `localizacoes_do_fato()` — e ele só aceita um lugar
    # que tenha ÂNCORA DE ACONTECIMENTO na mesma oração, com o trecho guardado.
    aceitas, recusadas = fl.localizacoes_do_fato(texto, origem="DERIVED_TEXT")
    if aceitas:
        fact_location = aceitas[0]["FACT_LOCATION"]
        base_lugar = ("ESCRITO: «%s» (ancora «%s», %s)"
                      % (aceitas[0]["FACT_LOCATION_EVIDENCE"][:120],
                         aceitas[0]["FACT_LOCATION_ANCHOR"],
                         aceitas[0]["TYPE_OF_EVIDENCE"]))
    else:
        fact_location = art.NAO_SEI
        base_lugar = (
            "NENHUMA ANCORA DE ACONTECIMENTO LIGA UM LUGAR A UM FACTO neste "
            "texto. A regra do contrato de fonte diz «%s» — e uma REGRA que "
            "manda procurar nao e o que se procurou. Recusados como mencao ou "
            "lista territorial: %d."
            % (cdf.regra_do_lugar_do_fato(sid)[:100], len(recusadas)))

    # ── QUANDO ACONTECEU O FACTO ───────────────────────────────────────────
    # O livro do coletor JÁ RESPONDEU a isto, uma observação de cada vez, e a
    # resposta é quase sempre `UNKNOWN` com o motivo escrito. Essa frase é uma
    # MEDIÇÃO e morria na fronteira. `SOURCE_DATE_ISO` é a data do DOCUMENTO e
    # vai para `PUBLISHED_AT` — nunca para `FACT_TIME`.
    declarado = str(obs.get("FACT_TIME") or "").strip()
    if declarado and not declarado.upper().startswith("UNKNOWN") \
            and not declarado.lower().startswith(("por linha", "por ponto")):
        fact_time, base_tempo = declarado, "declarado pelo coletor no livro"
    else:
        fact_time = art.NAO_SEI
        base_tempo = ("o coletor mediu e escreveu porque nao sabe: «%s». "
                      "`SOURCE_DATE_ISO` existe e e a data do DOCUMENTO, nao a "
                      "do facto (COL-LAW-031)."
                      % (declarado or "o livro nao declara FACT_TIME"))

    unidade = {
        "CONTENT_ID": obs["DOCUMENT_ID"],
        "TEXTO": texto,
        "URL": obs.get("SOURCE_URL"),
        "RAW_ASSET_ID": None,   # não há banco aqui: `NAO SEI`, nunca inventado
        "SOURCE_ID": sid,
        "ARTIFACT_TYPE": art.DERIVED,
        "PARENT_SHA256": obs["RAW_SHA256"],
        "SOURCE_LOCATION": lugar_fonte["VALOR"],
        "FACT_LOCATION": fact_location,
        "FACT_LOCATION_BASIS": base_lugar,
        "FACT_TIME": fact_time,
        "FACT_TIME_BASIS": base_tempo,
        "PUBLISHED_AT": obs.get("SOURCE_DATE_ISO") or art.NAO_SEI,
        "COLLECTED_AT": obs.get("CAPTURED_AT") or art.NAO_SEI,
        "SOURCE_DECLARED_EVIDENCE_CLASS": cdf.especie_de_evidencia_declarada(sid),
    }

    # ── A IDENTIDADE DO PROBLEMA ───────────────────────────────────────────
    # ⚠️ ISTO NÃO ENTRA NO `READY`, E A RAZÃO É A MESMA DE CIMA: uma menção não
    # é um facto. O que sai daqui é um DERIVADO com linhagem ao mesmo bruto —
    # a Intelligence chega-lhe pela observação, exactamente como a COL-LAW-043
    # já prescreve para as `TEXT_UNITS`.
    mencoes = agro.mencoes_de_problema(texto)
    sem_autoridade = agro.termos_sem_autoridade(
        texto, TERMOS_ITALIANOS_SEM_AUTORIDADE)

    recibo = {
        "SOURCE_ID": sid,
        "DOCUMENT_ID": obs["DOCUMENT_ID"],
        "RAW_SHA256": obs["RAW_SHA256"],
        "TEXTO_DERIVADO": os.path.relpath(caminho_do_texto, RAIZ).replace("\\", "/"),
        "RULE_VERSION": VERSAO_DO_REPROCESSAMENTO,
        "SOURCE_LOCATION": lugar_fonte,
        "FACT_LOCATION": {"VALOR": fact_location, "BASE": base_lugar,
                          "RECUSADOS": len(recusadas)},
        "FACT_TIME": {"VALOR": fact_time, "BASE": base_tempo},
        "ISSUE": {
            "MENCOES_COM_AUTORIDADE": mencoes,
            "TERMOS_SEM_AUTORIDADE": sem_autoridade,
            "O_QUE_ISTO_NAO_AFIRMA":
                "nenhuma destas mencoes afirma ocorrencia. ISSUE_MENTION != "
                "ISSUE_OCCURRENCE.",
        },
    }
    return unidade, recibo


def atravessar(unidade, universo="T3", corrida="REPROCESSAMENTO-LOCAL"):
    """STRUCTURED → ADMISSION → READY, pelo caminho REAL e por mais nenhum.

    Usa `rota.item_para_a_porta` — a mesma função que a rota canónica usa — de
    propósito. Uma prova que montasse o item à mão mediria a prova, e não a
    estrada.
    """
    item = rota.item_para_a_porta(unidade)
    decisao = admissao.decidir(item, universo, corrida=corrida)
    pronto = (admissao.pronto_para_inteligencia(item, decisao)
              if decisao.resultado == admissao.SIM else None)
    return item, decisao, pronto


def correr():
    obs = observacoes()
    textos = textos_por_impressao()
    recibos, prontos, nao_passaram = [], [], []
    sem_identidade = 0
    for o in obs:
        # ⚠️ UMA OBSERVACAO SEM DOCUMENT_ID NAO E UMA UNIDADE. E IDENTITY_FAILED:
        # ha bytes (e sha), nao ha documento. Medido em 20/09/2026: a Big
        # Collection 2 deixou no livro duas observacoes assim (IT-T3-011), com
        # o mesmo sha de um texto ja extraido — e esta prova levava-as a
        # fronteira com CONTENT_ID=None. Julgar o que nao tem identidade e
        # fabricar uma unidade; conta-se, e nao se atravessa.
        if not o.get("DOCUMENT_ID"):
            sem_identidade += 1
            continue
        sha = str(o.get("RAW_SHA256") or "").lower()
        caminho = textos.get(sha[:16])
        if not caminho:
            continue          # observação sem texto extraído nesta árvore
        unidade, recibo = unidade_reprocessada(o, caminho)
        item, decisao, pronto = atravessar(unidade)
        recibo["ADMISSAO"] = {"RESULTADO": decisao.resultado,
                              "REGRA": decisao.regra,
                              "ITEM_ID": decisao.item,
                              "MOTIVO": decisao.motivo[:200]}
        # A travessia mede-se pelo dono dela, e não por inspecção à mão.
        recibo["FRONTEIRA"] = ingresso.conferir_fronteira(item)
        # ── DE QUE BRUTO É ESTE RECIBO ──────────────────────────────────────
        # O livro do coletor já responde, e a resposta viaja para quem ler:
        # `True` = esta observação GUARDOU um objecto (e `RAW_PATH` prova-o);
        # `False` = foi lá, estava igual, e não guardou nada.
        recibo["RAW_OBJECT_CREATED"] = o.get("RAW_OBJECT_CREATED")
        recibos.append(recibo)
        # ── UM `raw_asset`, UM `READY` ──────────────────────────────────────
        # ⚠️ ISTO EMITIA UM READY POR OBSERVAÇÃO, E ERA POR ISSO QUE OS MESMOS
        # TRÊS DOCUMENTOS APARECIAM SEIS VEZES, BYTE A BYTE IGUAIS.
        #
        # A lei é de `BIBLIA-CANONICA-DA-COLETA.md`:
        #
        #     RAW_OBSERVATION_ID = raw_asset.id. Ausente: NAO SEI.
        #     **Nunca** derivado de sha256, URL, storage_path, filename ou RUN_ID.
        #
        # E `raw_asset` (migration `001`) é UMA LINHA POR OBJECTO GUARDADO —
        # `storage_path` é `unique`. Uma re-observação que não guarda objecto
        # novo não cria `raw_asset` novo; logo o READY que dela saísse teria a
        # linhagem do MESMO bruto. Não são dois READY: é um, contado duas vezes.
        #
        #     UM `raw_asset` -> UM `RAW_OBSERVATION_ID` -> UM `READY`.
        #
        # ⚠️ E NÃO SE DEDUPLICA POR `DOCUMENT_ID`. Esse é o nome do documento no
        # mundo, não é identidade de observação bruta, e usá-lo aqui seria a
        # segunda identidade que a lei proíbe. O que se lê é o campo que a
        # PRÓPRIA COLETA escreveu — medido: dos 175 registos, `RAW_OBJECT_CREATED
        # = True` em 35, e são exactamente as 35 impressões digitais distintas.
        #
        # ⚠️ E A RE-OBSERVAÇÃO NÃO DESAPARECE. O recibo dela fica acima, com a
        # decisão que teve. Deixar de contar o mesmo bruto duas vezes não é
        # apagar a segunda ida.
        #
        #     NÃO SE APAGA HISTÓRIA. DEIXA-SE DE CONTAR DUAS VEZES O MESMO BRUTO.
        guardou_bruto = o.get("RAW_OBJECT_CREATED") is True
        if pronto is not None and guardou_bruto:
            prontos.append(pronto)
        elif pronto is None:
            nao_passaram.append(recibo["DOCUMENT_ID"])

    def _conta(chave, valor):
        return sum(1 for p in prontos if p[chave] == valor)

    # ── A PORTA DA SALA, MEDIDA — e o que esta máquina NÃO consegue medir ──
    # `_conferir_unidades` é o guarda do contrato READY, e é o mesmo código que
    # corre antes de qualquer escrita nos dois backends. Chamá-lo aqui prova que
    # o que sai da admissão é aceite pela Sala.
    #
    # ⚠️ E ISTO NÃO É A SALA A FUNCIONAR. Nenhum dos dois backends corre nesta
    # máquina — o canónico precisa de `psql`, que não está instalado, e o de
    # ficheiro precisa de `fcntl`, que não existe em Windows. Dizer «a Sala
    # aceitou» com base nisto seria a mentira mais fácil desta prova.
    #
    #     CONTRATO CONFERIDO != ESCRITA PROVADA != SALA CANÓNICA VIVA.
    porta_da_sala = {"CONTRATO_ACEITE": None, "PORQUE": None,
                     "ESCRITA_PROVADA": "NO",
                     "PORQUE_NAO_SE_PROVOU_A_ESCRITA":
                         "esta maquina nao tem `psql` (backend canonico) nem "
                         "`fcntl` (backend de ficheiro). A escrita tem de ser "
                         "provada contra PostgreSQL descartavel, noutra maquina."}
    try:
        espera._conferir_unidades(prontos)
        porta_da_sala["CONTRATO_ACEITE"] = "YES"
        porta_da_sala["PORQUE"] = ("os %d campos de `CAMPOS_READY` estao todos "
                                   "presentes e nenhum campo a mais"
                                   % len(espera.CAMPOS_READY))
    except ValueError as erro:
        porta_da_sala["CONTRATO_ACEITE"] = "NO"
        porta_da_sala["PORQUE"] = str(erro)

    resumo = {
        "PERGUNTA": "o que ja esta guardado atravessa ate a Sala de Espera, e "
                    "com que fica pelo caminho?",
        "SO_LEITURA": "YES — nada foi colhido, nenhuma observacao nova foi criada",
        "REPROCESSAMENTO": VERSAO_DO_REPROCESSAMENTO,
        "OBSERVACOES_NO_LIVRO": len(obs),
        "COM_TEXTO_DERIVADO_NESTA_ARVORE": len(recibos),
        "ADMITIDOS": len(prontos),
        "PORTA_DA_SALA": porta_da_sala,
        "NAO_ADMITIDOS": nao_passaram,
        "PRESERVADO": {
            "SOURCE_LOCATION_CONHECIDO": len(prontos) - _conta("SOURCE_LOCATION", art.NAO_SEI),
            "SOURCE_DECLARED_EVIDENCE_CLASS_CONHECIDA":
                len(prontos) - _conta("SOURCE_DECLARED_EVIDENCE_CLASS", art.NAO_SEI),
            "PUBLISHED_AT_CONHECIDO": len(prontos) - _conta("PUBLISHED_AT", art.NAO_SEI),
        },
        "CONTINUA_DESCONHECIDO_E_ESTA_CERTO": {
            "FACT_TIME_NAO_SEI": _conta("FACT_TIME", art.NAO_SEI),
            "FACT_LOCATION_NAO_SEI": _conta("FACT_LOCATION", art.NAO_SEI),
            "PORQUE": "o material nao prova nenhum dos dois. Ver FACT_TIME.BASE "
                      "e FACT_LOCATION.BASE em cada recibo.",
        },
        "ISSUE": {
            "DOCUMENTOS_COM_MENCAO_COM_AUTORIDADE":
                sum(1 for r in recibos if r["ISSUE"]["MENCOES_COM_AUTORIDADE"]),
            "MENCOES_TOTAIS":
                sum(len(r["ISSUE"]["MENCOES_COM_AUTORIDADE"]) for r in recibos),
            "DOCUMENTOS_COM_TERMO_SEM_AUTORIDADE":
                sum(1 for r in recibos if r["ISSUE"]["TERMOS_SEM_AUTORIDADE"]),
            "O_QUE_ISTO_NAO_AFIRMA":
                "mencao nomeada no texto != ocorrencia. E nenhum ISSUE_ID foi "
                "cunhado a partir de nome comum italiano: nao ha autoridade "
                "italiano->EPPO nesta arvore.",
        },
        "RECIBOS": recibos,
        "READY": prontos,
        "GENERATED_BY": "provas/a_collection_preserva_o_fato.py",
    }
    return resumo


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    r = correr()
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in r.items()
                      if k not in ("RECIBOS", "READY")},
                     ensure_ascii=False, indent=2))
    print("\ngravado: %s" % SAIDA)
