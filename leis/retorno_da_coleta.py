#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTRATO DE RETORNO DA COLETA — o que uma corrida devolveu, e qual parte é colheita.

    O INDICE DE UMA COLHEITA NAO E A COLHEITA.
    E UM RECIBO — E UM RECIBO NAO SE ADMITE, LE-SE.

POR QUE ISTO EXISTE
-------------------
`COL-LAW-013` escreveu esta pergunta e nunca a respondeu. Ela diz que todo
executor deve poder declarar `OUTPUT = onde larguei, E EM QUE FORMA`. O «onde»
tem campo desde sempre (`larga_em`, `COL-LAW-012`). O «em que forma» não tinha
campo nenhum, nem enum, nem guarda — vivia em prosa livre no `o_que_traz`, que
nenhum código lê.

`COL-LAW-014` já tinha listado os campos em falta pelo nome — `artifact_types`
e `produces` — e confessa, com todas as letras, que «o resto ainda não existe».

O preço disso foi medido em 2026-09-11:

    ITEMS_EMITTED        253
    REAL_HARVEST_ITEMS     0
    FALSE_HARVEST_TOTAL  253

Cento por cento de falsa colheita. Um manifesto de 163 descarregamentos, um
catálogo de 12 pessoas e 74 fichas de conta entraram na cadeia como se fossem
material observado, porque `a_colheita()` usa uma heurística genérica — «uma
lista, ou o primeiro campo do ficheiro que seja lista de fichas».

E o contraexemplo que fecha o assunto: `CLASSIFICADO-V1.json` TEM um contentor
de colheita chamado `ITEMS`, com `ITEM_COUNT = 0`. A heurística **salta-o por
estar vazio** e agarra a lista de catálogo ao lado.

    UMA HEURISTICA QUE PREFERE UMA LISTA CHEIA A UMA LISTA CERTA
    NAO ESTA A LER O RETORNO: ESTA A ADIVINHAR.

O QUE ESTE FICHEIRO É, E O QUE NÃO É
-------------------------------------
É o envelope de UMA corrida. Não é um formato de ficheiro novo, não é um
segundo `leis/artefato.py` e não substitui `pedido/receitas.py`.

    receitas.py         declara a INTENCAO   (que executor, que rota, onde larga)
    ESTE FICHEIRO       declara o RESULTADO  (o que a corrida devolveu, e o quê é o quê)
    leis/artefato.py    governa a FICHA      de cada coisa entregue
    coleta/ingresso.py  pergunta             «posso preservar esta observacao?»

`DECLARED != OBSERVED`, e a diferença não é teórica: `larga_em` é uma
declaração de intenção e duas das cinco receitas apontam para pastas que não
existem. Uma declaração pode apodrecer em silêncio; um envelope é emitido por
quem correu, e não pode estar errado sobre o que acabou de fazer.

AS ESPÉCIES, E SÓ AS QUE A REALIDADE EXIGIU
--------------------------------------------
Cada uma foi encontrada nesta árvore, com ficheiro:

    COLHEITA      unidade observada na fonte     collection-store/italy/...
    MANIFEST      listagem de payloads           data/raw/IT-ROTULOS/_MANIFESTO.json
    CATALOG       inventario de entidades de     RESEARCHER-CORPUS · CONTAS-V1 ·
                  onde se PODE coletar           UNIVERSO-CONTAS · ANCORAS
    RUN_RECEIPT   prova da execucao              MEDICAO-PRIMEIRO-LOTE-V1.json
    PLAN          o que se tenciona fazer        PUBLIC-COMM :: EXECUTION_ORDER
    UNKNOWN       declarado e nao classificavel  (nunca entra)

`INDEX` e `MANIFEST` **não** são espécies diferentes. Procurou-se a diferença e
ela não existe: as duas são uma listagem de payloads, e o que muda entre elas é
ONDE o payload está e SE está — que é o `PAYLOAD`, e não a espécie. Criar duas
espécies para uma diferença que já tem campo próprio seria inventar uma
distinção que a realidade não pediu.

`SUPORTE` não é uma sexta espécie: é tudo o que não é colheita. Deriva-se, e
por isso não há saco misto onde esconder o que não se soube classificar.
"""
from __future__ import annotations

import os
import re

# ── AS ESPÉCIES DE RETORNO ──────────────────────────────────────────────────
COLHEITA = "COLHEITA"
MANIFEST = "MANIFEST"
CATALOG = "CATALOG"
RUN_RECEIPT = "RUN_RECEIPT"
PLAN = "PLAN"
ESPECIE_DESCONHECIDA = "UNKNOWN"

ESPECIES = (COLHEITA, MANIFEST, CATALOG, RUN_RECEIPT, PLAN, ESPECIE_DESCONHECIDA)
#     SO A COLHEITA ATRAVESSA A PORTA. As outras leem-se.
ENTRAM_NO_INGRESSO = (COLHEITA,)

# ── O ESTADO DA CORRIDA ─────────────────────────────────────────────────────
# Reutilizado de `regras/proveniencia.py::STATUS_RUN`, e nao redefinido: duas
# listas para o mesmo vocabulario divergem no dia em que alguem acrescenta um
# estado a uma delas.
SUCCESS, PARTIAL, FAILED = "SUCCESS", "PARTIAL", "FAILED"
ESTADOS_DA_CORRIDA = (SUCCESS, PARTIAL, FAILED)

# ── ONDE ESTÁ O PAYLOAD ─────────────────────────────────────────────────────
#     PRESENTE       ha bytes nesta arvore, no caminho declarado
#     AUSENTE        o caminho foi declarado e os bytes nao estao ca
#     NAO_SE_APLICA  a observacao E o proprio item; nao ha ficheiro separado
#
# ⚠️ AUSENTE NAO E ERRO, e esta distincao custou a medicao inteira do
# `_MANIFESTO.json`: 163 linhas a declarar ficheiros, ZERO ficheiros ao lado.
# Chamar-lhe erro faria a corrida falhar; calar faria o indice passar por
# colheita. E um TERCEIRO estado, e precisa de nome.
PRESENTE, AUSENTE, PAYLOAD_NAO_SE_APLICA = "PRESENTE", "AUSENTE", "NAO_SE_APLICA"
ESTADOS_DO_PAYLOAD = (PRESENTE, AUSENTE, PAYLOAD_NAO_SE_APLICA)

NAO_SEI = "NAO SEI"

_SHA = re.compile(r"^[0-9a-f]{12,64}$", re.I)


def estado_do_payload(onde: str, raiz: str) -> str:
    """Mede — não pergunta ao executor. Quem declara o caminho não confirma os bytes."""
    if not str(onde or "").strip():
        return PAYLOAD_NAO_SE_APLICA
    return PRESENTE if os.path.exists(os.path.join(raiz, onde)) else AUSENTE


def _fabricado(document_id: str, sha256: str, onde: str) -> str:
    """O `DOCUMENT_ID` derivado do conteúdo ou do endereço — e porque é mentira.

        SHA256 NAO E IDENTIDADE DOCUMENTAL.
        storage_path NAO E IDENTIDADE.

    Medido nesta árvore: 35 valores de `sha256` aparecem em observações
    DISTINTAS do livro. Um `DOCUMENT_ID` tirado do sha colaria duas observações
    legítimas numa só. E um tirado do caminho morre quando o ficheiro se move.
    """
    d = str(document_id or "").strip()
    if not d:
        return ""
    s = str(sha256 or "").strip()
    if s and (d == s or (len(d) >= 12 and s.startswith(d))):
        return "o DOCUMENT_ID e o proprio sha256 (ou um prefixo dele)"
    if _SHA.match(d) and not s:
        return "o DOCUMENT_ID tem cara de hash e nada o liga a um documento"
    o = str(onde or "").strip()
    if o and d in (o, os.path.basename(o), os.path.splitext(os.path.basename(o))[0]):
        return "o DOCUMENT_ID e o endereco do ficheiro"
    return ""


def conferir_unidade(u: dict, run_id: str, raiz: str) -> list:
    """As leis que uma unidade de COLHEITA não pode quebrar. Devolve os motivos."""
    mal = []
    especie = u.get("ESPECIE")
    if especie not in ESPECIES:
        mal.append("ESPECIE fora do vocabulario: %r. Ha: %s"
                   % (especie, ", ".join(ESPECIES)))
        return mal
    if especie != COLHEITA:
        mal.append("%s nao e colheita e nao pode viajar como unidade colhida: "
                   "so %s atravessa a porta" % (especie, ", ".join(ENTRAM_NO_INGRESSO)))
        return mal

    # ── SOURCE_ID: provado, nunca fabricado ────────────────────────────────
    if not str(u.get("SOURCE_ID") or "").strip():
        mal.append("unidade colhida sem SOURCE_ID. Nao se inventa uma fonte: "
                   "sem ela a unidade nao se consegue conferir depois")
    elif str(u.get("SOURCE_ID")).strip() == NAO_SEI:
        mal.append("SOURCE_ID = «NAO SEI» nao serve para colheita: uma unidade "
                   "sem fonte provada nao e observacao, e candidata")

    # ── DOCUMENT_ID: pode faltar, nao pode ser inventado ───────────────────
    #     UNKNOWN PERMANECE UNKNOWN. Um «NAO SEI» escrito e honesto; um
    #     identificador tirado do sha ou do caminho e uma mentira com forma
    #     de dado, e ninguem a vai investigar.
    doc = str(u.get("DOCUMENT_ID") or "").strip()
    if not doc:
        mal.append("DOCUMENT_ID ausente. Escreva «%s» — a falta declarada e "
                   "legitima; a falta calada nao" % NAO_SEI)
    elif doc != NAO_SEI:
        porque = _fabricado(doc, u.get("SHA256"), (u.get("PAYLOAD") or {}).get("ONDE"))
        if porque:
            mal.append("DOCUMENT_ID fabricado: " + porque)

    # ── A CORRIDA: a unidade pertence a esta, ou nao viaja nela ────────────
    seu = str(u.get("RUN_ID") or "").strip()
    if seu and seu != run_id:
        mal.append("RUN_MISMATCH: a unidade diz %r e o envelope diz %r. Saida "
                   "antiga numa pasta nao se atribui a corrida nova" % (seu, run_id))

    # ── O PAYLOAD: medido, e com estado explicito ──────────────────────────
    pay = u.get("PAYLOAD")
    if not isinstance(pay, dict):
        mal.append("unidade colhida sem PAYLOAD. Mesmo quando a observacao E o "
                   "item, isso diz-se: ESTADO = %s" % PAYLOAD_NAO_SE_APLICA)
    else:
        est = pay.get("ESTADO")
        if est not in ESTADOS_DO_PAYLOAD:
            mal.append("ESTADO do payload fora do vocabulario: %r. Ha: %s"
                       % (est, ", ".join(ESTADOS_DO_PAYLOAD)))
        else:
            medido = estado_do_payload(pay.get("ONDE"), raiz)
            if est != medido:
                mal.append("o payload diz %s e a arvore diz %s (%s). Quem declara "
                           "o caminho nao confirma os bytes"
                           % (est, medido, pay.get("ONDE") or "sem caminho"))
    return mal


def conferir(envelope: dict, raiz: str) -> list:
    """As leis do envelope inteiro. Lista vazia = o retorno respeita o contrato."""
    mal = []
    for campo in ("RUN_ID", "EXECUTOR_ID", "EXECUTOR_VERSION", "ESTADO"):
        if not str(envelope.get(campo) or "").strip():
            mal.append("envelope sem %s: uma corrida que nao diz quem correu nao "
                       "se audita" % campo)
    estado = envelope.get("ESTADO")
    if estado and estado not in ESTADOS_DA_CORRIDA:
        mal.append("ESTADO da corrida fora do vocabulario: %r. Ha: %s"
                   % (estado, ", ".join(ESTADOS_DA_CORRIDA)))

    colheita = envelope.get("COLHEITA")
    suporte = envelope.get("SUPORTE")
    erros = envelope.get("ERROS")
    for nome, v in (("COLHEITA", colheita), ("SUPORTE", suporte), ("ERROS", erros)):
        if not isinstance(v, list):
            mal.append("%s tem de ser uma lista, mesmo vazia. Ausente e «nao sei»; "
                       "vazia e «mediu-se e nao havia»" % nome)

    # ── ZERO LEGITIMO NAO E FALHA ──────────────────────────────────────────
    #     EMPTY_SUCCESS != ERROR. Medido: CLASSIFICADO-V1.json declara
    #     ITEM_COUNT = 0 numa execucao que correu ate ao fim. Tratar isso como
    #     erro ensinaria a casa a fabricar itens para nao falhar.
    if estado == FAILED and isinstance(erros, list) and not erros:
        mal.append("ESTADO = FAILED sem nenhum erro escrito. Uma falha sem "
                   "motivo e um rotulo")
    if estado == SUCCESS and isinstance(erros, list) and erros:
        mal.append("ESTADO = SUCCESS com erros escritos: use PARTIAL")

    if isinstance(colheita, list):
        for i, u in enumerate(colheita):
            for m in conferir_unidade(u, str(envelope.get("RUN_ID") or ""), raiz):
                mal.append("COLHEITA[%d]: %s" % (i, m))
    if isinstance(suporte, list):
        for i, a in enumerate(suporte):
            esp = a.get("ESPECIE")
            if esp not in ESPECIES:
                mal.append("SUPORTE[%d]: ESPECIE fora do vocabulario: %r" % (i, esp))
            elif esp == COLHEITA:
                mal.append("SUPORTE[%d]: colheita declarada como suporte. Sao "
                           "listas diferentes de proposito" % i)
    return mal


def so_o_que_entra(envelope: dict) -> list:
    """O que pode atravessar a porta. Nunca deduz: lê a espécie declarada."""
    return [u for u in (envelope.get("COLHEITA") or [])
            if u.get("ESPECIE") in ENTRAM_NO_INGRESSO]


# ── O QUE JÁ ESTÁ EM DISCO, E NUNCA FOI DECLARADO POR NINGUÉM ───────────────
#
# Há executores que largaram ficheiros muito antes desta lei existir, e que não
# correm offline para os voltar a declarar. Eles precisam de uma ponte — e a
# ponte tem de ser segura por construção, não por boa vontade.
#
#     O LEGADO SO PODE DECLARAR SUPORTE.
#     COLHEITA VEM DE UMA CORRIDA, E DE MAIS NADA.
#
# Porquê: uma declaração escrita na receita é feita ANTES da corrida, e envelhece
# sozinha — `larga_em` prova isso, com dois caminhos apontando para pastas que
# não existem sem ninguém notar. Se essa declaração pudesse dizer «aqui há
# colheita», uma linha desactualizada mandaria suporte para o ingresso outra
# vez, e teríamos trocado uma heurística por um literal.
#
# Declarar suporte é inofensivo mesmo quando errado: suporte nunca atravessa.
# Declarar colheita não é — e por isso não se pode.
LEGADO_SO_DECLARA_SUPORTE = tuple(e for e in ESPECIES if e != COLHEITA)


def envelope_do_legado(run_id: str, executor_id: str, executor_version: str,
                       declarado: dict, raiz: str) -> dict:
    """Um envelope para o que já está em disco. COLHEITA sai sempre vazia.

    `declarado` é `{caminho: ESPECIE}` — a espécie que alguém declarou para
    aquele sítio, na receita. Uma espécie fora de `LEGADO_SO_DECLARA_SUPORTE`
    entra como `UNKNOWN` e o motivo fica escrito: não se cala, e também não se
    obedece.
    """
    suporte, erros = [], []
    for onde in sorted(declarado or {}):
        especie = declarado[onde]
        if especie == COLHEITA:
            erros.append(
                "«%s» foi declarado como COLHEITA no legado, e o legado so pode "
                "declarar suporte. Colheita vem de uma corrida. Registado como "
                "%s." % (onde, ESPECIE_DESCONHECIDA))
            especie = ESPECIE_DESCONHECIDA
        elif especie not in ESPECIES:
            erros.append("«%s» declara a especie %r, que nao existe. Registado "
                         "como %s." % (onde, especie, ESPECIE_DESCONHECIDA))
            especie = ESPECIE_DESCONHECIDA
        suporte.append({"ESPECIE": especie, "ONDE": onde,
                        "PAYLOAD": {"ONDE": onde,
                                    "ESTADO": estado_do_payload(onde, raiz)}})
    return {
        "RUN_ID": run_id,
        "EXECUTOR_ID": executor_id,
        "EXECUTOR_VERSION": executor_version or NAO_SEI,
        # PARCIAL e nao FAILED: o executor nao falhou — ele nunca declarou.
        # E nao e SUCCESS, porque dizer «correu bem» a um retorno que ninguem
        # declarou seria a casa a dar-se por satisfeita com o silencio.
        "ESTADO": PARTIAL if erros else SUCCESS,
        "COLHEITA": [],
        "SUPORTE": suporte,
        "ERROS": erros,
        "PORQUE_ZERO_COLHEITA": (
            "o retorno deste executor e legado: esta declarado como suporte e "
            "nao como colheita. ZERO COLHEITA AQUI E A RESPOSTA CERTA."),
    }


def envelope_de_quem_nao_declarou(run_id: str, executor_id: str,
                                  executor_version: str, porque: str) -> dict:
    """Nem envelope, nem legado declarado. Isto NÃO é uma corrida vazia.

        UM RETORNO SEM DECLARACAO NAO E UM RETORNO VAZIO:
        E UM RETORNO QUE NAO SE DECLAROU — E O QUE NAO SE DECLAROU NAO ENTRA.

    Antes, era exactamente aqui que a heurística entrava a adivinhar. Agora o
    silêncio tem nome e sai no recibo.
    """
    return {
        "RUN_ID": run_id,
        "EXECUTOR_ID": executor_id,
        "EXECUTOR_VERSION": executor_version or NAO_SEI,
        "ESTADO": PARTIAL,
        "COLHEITA": [],
        "SUPORTE": [],
        "ERROS": [],
        "RETORNO_NAO_DECLARADO": True,
        "PORQUE_ZERO_COLHEITA": porque,
    }
