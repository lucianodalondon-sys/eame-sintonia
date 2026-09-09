#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O DONO CANÔNICO DA ESCRITA DO DERIVADO.

POR QUE ESTE FICHEIRO EXISTE
----------------------------
A `migration 022` está desenhada, provada e com a semântica fechada. Falta-lhe
a única coisa que a torna um caminho produtivo: **quem escreve nela**.

    ESQUEMA BOM SEM WRITER BOM
    AINDA NÃO É CAMINHO PRODUTIVO.

E há uma armadilha concreta à espera, que a tabela sozinha não apanha:

    ON CONFLICT DO NOTHING NÃO É IDEMPOTÊNCIA.

O banco recusa a segunda linha com a mesma identidade — bom. Mas se quem
escreve ler esse silêncio como «já lá estava, tudo igual», então uma derivação
que passou a produzir **outro resultado** entra como `REUSED`. O sistema fica
calado exatamente no dia em que devia gritar.

    IDEMPOTÊNCIA É REENCONTRO + COMPARAÇÃO + PROVA DE IGUALDADE.

Por isso a ordem aqui não é «tentar inserir e ver o que acontece». É: ler antes,
comparar, e depois de escrever **ler outra vez** e comparar campo a campo.

O QUE ESTE DONO POSSUI, E NINGUÉM MAIS
--------------------------------------
    o sha256 do PAI            lido do `raw_asset`, nunca aceite do chamador
    o sha256 e os bytes do FILHO   calculados dos bytes reais
    a serialização dos parâmetros   uma função só, e é esta
    o `parameters_hash`        derivado dessa função
    o `derived_at`             medido pelo relógio, nunca herdado
    o `storage_path`           construído da receita INTEIRA, nunca à mão
    o país do artefato         lido do bruto e da corrida que o trouxe

Um chamador que pudesse trazer qualquer um destes valores prontos poderia
mentir sobre a linhagem sem que nada o impedisse — e o banco não distingue um
`timestamptz` medido de um copiado.

    DB_PROVES_PRESENT  ≠  DB_PROVES_MEASURED.
    WRITER_PROVES_MEASURED.

POR QUE AO LADO DE `preservar_coleta.py`, E NÃO DENTRO DELE
-----------------------------------------------------------
Aquele é o dono do **bruto**: sabe de corridas, de capturas, de
`collection_run`. Forçá-lo a ser genérico para caber o derivado faria dele uma
coisa que não é de ninguém. Aqui reusa-se o que é mesmo comum — as portas
`Armazem` e `Memoria`, e o `sha256` — e mais nada.
"""
import hashlib
import json
from datetime import datetime, timezone

from guarda.preservar_coleta import Armazem, Memoria, sha256  # noqa: F401

# ─────────────────────────────────────────────────────────────────────────
# OS ESTADOS — poucos, e cada um com uma decisão diferente por trás
# ─────────────────────────────────────────────────────────────────────────
INSERTED = "INSERTED"
REUSED = "REUSED"
REUSED_AFTER_RACE = "REUSED_AFTER_RACE"
DERIVATION_DRIFT = "DERIVATION_DRIFT"
STORAGE_CONFLICT = "STORAGE_CONFLICT"
# UMA LINHA NO BANCO NAO E PROVA DE QUE O BYTE AINDA EXISTE. Este estado
# existe porque «a ficha esta la e o artefato desapareceu» nao e a mesma coisa
# que «a ficha nao entrou» — sao duas avarias diferentes, com conserto
# diferente, e dar-lhes o mesmo nome mandaria o operador ao sitio errado.
STORAGE_MISSING = "STORAGE_MISSING"
METADATA_NOT_RECONCILED = "METADATA_NOT_RECONCILED"
RAW_PARENT_NOT_FOUND = "RAW_PARENT_NOT_FOUND"
ERROR = "ERROR"

# A identidade da receita. `raw_asset_id` NÃO está aqui — o grão é CONTEÚDO POR
# RECEITA, e a cópia lida é testemunha, não identidade.
IDENTIDADE = ("parent_sha256", "kind", "producer", "producer_version",
              "parameters_hash", "serie_posicao")

# O que se compara para decidir REUSED contra DRIFT. É o RESULTADO, não a
# receita — a receita já é a chave que os fez encontrar-se.
RESULTADO = ("sha256", "bytes", "media_type")

# O que a leitura pós-escrita confere, campo a campo. Contar não é conferir.
CAMPOS_DA_LINHA = ("raw_asset_id", "parent_sha256", "kind", "producer",
                   "producer_version", "pipeline_version", "parameters_hash",
                   "serie_posicao", "sha256", "bytes", "media_type",
                   "storage_path", "derived_at")


class MemoriaDoDerivado(Memoria):
    """A porta do banco, com as duas leituras que este dono precisa.

    Herda de `Memoria` porque é o mesmo banco e o mesmo `aplicar`. O que
    acrescenta são leituras — e são elas que fazem a diferença entre
    idempotência e silêncio.
    """

    def raw_por_id(self, raw_asset_id) -> dict:
        """A linha do bruto. É daqui que sai o `parent_sha256` — nunca do
        chamador."""
        raise NotImplementedError

    def derivado_com_identidade(self, identidade: dict) -> dict:
        """A linha que já ocupa esta receita, ou `None`."""
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────────────────
# 1 · OS PARÂMETROS — uma serialização, um dono
# ─────────────────────────────────────────────────────────────────────────
def parametros_canonicos(parametros) -> bytes:
    """A forma estável dos parâmetros, em bytes.

    O banco confere o **formato** do `parameters_hash` e nada mais: para
    conferir a correspondência teria de conhecer esta função. Então ela é a
    autoridade, e existe **uma vez só** — duas implementações da mesma regra
    seriam duas verdades livres para divergir.

    AS ESCOLHAS, E O QUE CADA UMA IMPEDE:

        sort_keys=True        a ordem em que alguém escreveu o dicionário não
                              muda o hash. `{"a":1,"b":2}` e `{"b":2,"a":1}`
                              são os mesmos parâmetros.
        separators sem espaço a formatação não entra na conta.
        ensure_ascii=False    `città` é `città`, e não uma sequência de
                              escapes — e a codificação é sempre UTF-8.
        NULL → b""            ausência de parâmetros tem uma forma só.

    ⚠️ ISTO NÃO É JSON CANÓNICO DA NORMA (JCS/RFC 8785). É determinístico para
    o que esta casa usa — dicionários, listas, texto, números inteiros,
    booleanos e nulos. Números de vírgula flutuante têm armadilhas de
    representação que esta função não resolve, e por isso não devem entrar em
    parâmetros de derivação sem uma decisão própria.
    """
    if parametros is None:
        return b""
    return json.dumps(parametros, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def hash_dos_parametros(parametros) -> str:
    """`sha256` da forma canónica. Sem parâmetros, é o hash da cadeia vazia —
    que é o valor que a `022` e as suas provas já usam."""
    return hashlib.sha256(parametros_canonicos(parametros)).hexdigest()


# ─────────────────────────────────────────────────────────────────────────
# 2 · O ENDEREÇO — derivado da receita, não escolhido
# ─────────────────────────────────────────────────────────────────────────
EXTENSOES = {"text/plain": "txt", "application/json": "json",
             "image/png": "png", "image/jpeg": "jpg", "application/pdf": "pdf"}


def id_da_receita(identidade: dict) -> str:
    """O `sha256` da identidade INTEIRA da derivação.

    Os seis campos que a `022` usa como chave, serializados pela mesma função
    canónica dos parâmetros — uma serialização só para a casa toda.
    """
    return hashlib.sha256(parametros_canonicos(
        {c: identidade.get(c) for c in IDENTIDADE})).hexdigest()


def caminho_do_derivado(identidade: dict, media_type: str,
                        country: str = "XX") -> str:
    """`PAIS/derivados/TIPO/<produtor>-<versao>-<receita_sha256>.<ext>`

    ⚠️ ISTO FOI CORRIGIDO, E O DEFEITO ERA ESTRUTURAL.

    O caminho antigo era
    `PAIS/derivados/TIPO/<pai16>-<produtor>-<versao>[-<n>]` — e **não incluía
    o `parameters_hash`**. Duas derivações que a `022` considera **diferentes**
    — o mesmo PDF a 150 e a 300 dpi, por exemplo — eram duas linhas legítimas
    a disputar **o mesmo endereço**. O banco distinguia-as; o armazém não.

        SE A IDENTIDADE DO BANCO DIZ QUE SÃO DUAS DERIVAÇÕES,
        O ENDEREÇO TEM DE PERMITIR QUE AS DUAS EXISTAM.

    Agora o discriminante é o `sha256` **completo** da receita inteira: pai,
    tipo, produtor, versão, hash dos parâmetros e posição na série. Não é um
    prefixo de 16 caracteres a fazer de identidade — é o hash todo.

    E O CAMINHO CONTINUA A NÃO SER A IDENTIDADE. Ele é `unique` na tabela
    porque dois objetos não vivem no mesmo endereço; quem decide se duas
    derivações são a mesma continua a ser a chave da receita. O `sha256` do
    FILHO **não** entra aqui de propósito: se entrasse, o mesmo `DERIVATION_DRIFT`
    ganharia um endereço novo e deixaria de ser drift — passaria a ser dois
    artefatos calados.
    """
    ext = EXTENSOES.get(media_type, "bin")
    return "%s/derivados/%s/%s-%s-%s.%s" % (
        country or "XX", identidade["kind"], identidade["producer"],
        identidade["producer_version"], id_da_receita(identidade), ext)


# ─────────────────────────────────────────────────────────────────────────
# 3 · O RELÓGIO — o momento da derivação é medido, não herdado
# ─────────────────────────────────────────────────────────────────────────
def agora_utc() -> str:
    """O instante em que a derivação terminou.

    Injetável **só** para os testes poderem ser determinísticos. O que nunca
    acontece é o `derived_at` vir do chamador — porque então nada impediria
    alguém de lhe passar o `captured_at` do pai, e a corrida diria que o texto
    nasceu no instante em que o PDF foi colhido.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────────────────
# 4 · A COMPARAÇÃO — o coração da idempotência
# ─────────────────────────────────────────────────────────────────────────
def _difere(existente: dict, esperado: dict, campos) -> list:
    fora = []
    for c in campos:
        a, b = existente.get(c), esperado.get(c)
        if a is None and b is None:
            continue
        if str(a) != str(b):
            fora.append({"CAMPO": c, "NO_BANCO": a, "NESTA_DERIVACAO": b})
    return fora


def _sql(v):
    if v is None:
        return "null"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def sql_do_derivado(linha: dict) -> str:
    """O `insert`, sem `on conflict`.

    ⚠️ A AUSÊNCIA DO `on conflict` É DELIBERADA. Ele tornaria o retry mudo, e é
    justamente o silêncio que este ficheiro existe para recusar. Se a chave já
    estiver ocupada, queremos **saber** — para ler o que lá está e comparar.
    """
    cols = [c for c in CAMPOS_DA_LINHA if c in linha] + ["parameters"]
    vals = [_sql(linha.get(c)) for c in CAMPOS_DA_LINHA if c in linha]
    p = linha.get("parameters")
    vals.append("null" if p is None
                else "%s::jsonb" % _sql(json.dumps(p, sort_keys=True,
                                                   ensure_ascii=False)))
    return ("insert into public.derived_artifact (%s) values (%s);"
            % (", ".join(cols), ", ".join(vals)))


# ─────────────────────────────────────────────────────────────────────────
# 5 · A CADEIA
# ─────────────────────────────────────────────────────────────────────────
def preservar_derivado(pedido: dict, bytes_do_filho: bytes,
                       armazem: Armazem, memoria: MemoriaDoDerivado,
                       relogio=agora_utc) -> dict:
    """Escreve UM derivado, e prova o que escreveu.

        LER O PAI → RECEITA → MEDIR O FILHO → LER A IDENTIDADE
        → COMPARAR → GUARDAR OS BYTES → CONFERIR → ESCREVER
        → LER OUTRA VEZ → RECONCILIAR

    O que o chamador entrega: `raw_asset_id`, `kind`, `producer`,
    `producer_version`, `parameters`, `serie_posicao`, `media_type`, e os bytes
    do filho. **Nada mais.** O `parent_sha256`, o `parameters_hash`, o
    `derived_at`, o `sha256`, os `bytes` e o `storage_path` são deste ficheiro.
    """
    # ── O PAI, LIDO DO BANCO ────────────────────────────────────────────
    # Nunca aceite do chamador: era assim que se conseguia declarar
    # `raw_asset_id` = A com `parent_sha256` = B. A chave estrangeira composta
    # da 022 continua a ser a última trava — mas o writer também não fabrica a
    # contradição para ela apanhar.
    pai = memoria.raw_por_id(pedido["raw_asset_id"])
    if not pai:
        return {"ESTADO": RAW_PARENT_NOT_FOUND,
                "PORQUE": ("o bruto %s nao existe. Nada foi guardado e nada foi "
                           "escrito — a recusa acontece ANTES do armazem."
                           % pedido["raw_asset_id"]),
                "BYTES_GUARDADOS": False}

    p = dict(pedido)

    # ── O PAIS TAMBEM E DO PAI ──────────────────────────────────────────
    # Se o bruto sabe de que pais e — pela corrida que o trouxe — e esse que
    # vale. Um chamador que pudesse mandar `country="ES"` para um bruto
    # italiano poria o byte derivado a morar no sitio errado, e ninguem
    # reparava. Onde o pai nao prova, fica NAO_SEI: nao se infere.
    pais = pai.get("source_country") or "NAO_SEI"
    if pais in ("", "NAO_SEI", None):
        pais = "NAO_SEI"

    # ── A RECEITA E O FILHO, MEDIDOS ────────────────────────────────────
    sha_filho = sha256(bytes_do_filho)
    identidade = {
        "parent_sha256": pai["sha256"],
        "kind": p["kind"],
        "producer": p["producer"],
        "producer_version": p["producer_version"],
        "parameters_hash": hash_dos_parametros(p.get("parameters")),
        "serie_posicao": p.get("serie_posicao"),
    }
    caminho = caminho_do_derivado(identidade, p["media_type"], pais)
    esperado = dict(identidade,
                    raw_asset_id=pedido["raw_asset_id"],
                    pipeline_version=p.get("pipeline_version"),
                    sha256=sha_filho,
                    bytes=len(bytes_do_filho),
                    media_type=p["media_type"],
                    storage_path=caminho,
                    parameters=p.get("parameters"))

    # ── PRÉ-LEITURA: a identidade já está ocupada? ──────────────────────
    ja = memoria.derivado_com_identidade(identidade)
    if ja:
        divergem = _difere(ja, esperado, RESULTADO)
        if divergem:
            # A MESMA RECEITA DEU OUTRO RESULTADO. Nao se apaga, nao se
            # sobrescreve, e sobretudo nao se chama a isto REUSED. O sistema
            # grita, e quem decide o que fazer e uma pessoa.
            return {"ESTADO": DERIVATION_DRIFT,
                    "DIVERGENCIAS": divergem,
                    "PORQUE": ("a mesma receita produziu outro resultado. Nao se "
                               "apaga o antigo nem se escreve por cima: as duas "
                               "versoes sao factos, e um deles e um defeito por "
                               "descobrir."),
                    "LINHA_EXISTENTE": ja,
                    "BYTES_GUARDADOS": False}
        # ⚠️ E AGORA A PARTE QUE FALTAVA: O BYTE AINDA EXISTE?
        #
        #     UMA LINHA NO BANCO NAO E PROVA DE QUE O BYTE AINDA EXISTE.
        #
        # A versao anterior devolvia REUSED aqui, sem nunca perguntar ao
        # armazem. Uma ficha viva sobre um artefato apagado passava por
        # «reaproveitado, esta tudo bem» — que e a mentira mais confortavel que
        # este sistema podia contar. Nao era limite conhecido: era defeito.
        onde = ja.get("storage_path")
        if not onde or not armazem.existe(onde):
            return {"ESTADO": STORAGE_MISSING,
                    "LINHA_EXISTENTE": ja, "STORAGE_PATH": onde,
                    "BYTES_CONFERIDOS_NO_ARMAZEM": False,
                    "PORQUE": ("a ficha esta no banco e o artefato nao esta no "
                               "armazem. NAO e REUSED: nao ha o que reaproveitar."),
                    "O_QUE_NAO_SE_FAZ": (
                        "NAO se reenvia o byte por conta propria. Um "
                        "desaparecimento de evidencia regista-se primeiro; curar "
                        "em silencio apagaria o rasto de que houve um buraco."),
                    "BYTES_GUARDADOS": False, "NOVO_UPLOAD": False}

        guardado = sha256(armazem.ler(onde))
        if guardado != ja.get("sha256") or guardado != sha_filho:
            return {"ESTADO": STORAGE_CONFLICT,
                    "LINHA_EXISTENTE": ja, "STORAGE_PATH": onde,
                    "BYTES_CONFERIDOS_NO_ARMAZEM": True,
                    "SHA_NO_ARMAZEM": guardado,
                    "SHA_NA_LINHA": ja.get("sha256"),
                    "SHA_DESTA_EXECUCAO": sha_filho,
                    "PORQUE": ("o byte que esta no armazem nao bate com o que a "
                               "ficha diz, ou com o que esta execucao produziu."),
                    "BYTES_GUARDADOS": True, "NOVO_UPLOAD": False}

        return {"ESTADO": REUSED,
                "LINHA_EXISTENTE": ja,
                "TESTEMUNHA_NO_BANCO": ja.get("raw_asset_id"),
                "TESTEMUNHA_DESTA_CHAMADA": pedido["raw_asset_id"],
                "BYTES_CONFERIDOS_NO_ARMAZEM": True,
                "PORQUE": _porque_reused(ja, pedido),
                "BYTES_GUARDADOS": True, "NOVO_UPLOAD": False}

    # ── OS BYTES, E SEM SOBRESCREVER NADA ───────────────────────────────
    novo_upload = False
    if armazem.existe(caminho):
        guardado = armazem.ler(caminho)
        if sha256(guardado) != sha_filho:
            # Ha outro artefato neste endereco. Apagar para «tentar de novo»
            # destruiria evidencia; escrever por cima destruiria em silencio.
            return {"ESTADO": STORAGE_CONFLICT,
                    "STORAGE_PATH": caminho,
                    "PORQUE": ("o armazem ja tem outro conteudo neste endereco. "
                               "Nao se apaga e nao se escreve por cima."),
                    "BYTES_GUARDADOS": True}
    else:
        try:
            armazem.enviar(caminho, bytes_do_filho, p["media_type"])
            novo_upload = True
        except Exception as erro:                      # noqa: BLE001
            return {"ESTADO": ERROR, "PORQUE": "o armazem recusou: %s" % erro,
                    "BYTES_GUARDADOS": False}
        # «Enviei» nao e «chegou».
        if sha256(armazem.ler(caminho)) != sha_filho:
            return {"ESTADO": STORAGE_CONFLICT, "STORAGE_PATH": caminho,
                    "PORQUE": "o que voltou do armazem nao bate com o que se enviou.",
                    "BYTES_GUARDADOS": True}

    # ── A MEMÓRIA ───────────────────────────────────────────────────────
    esperado["derived_at"] = relogio()
    erro_do_insert = None
    try:
        memoria.aplicar(sql_do_derivado(esperado))
    except Exception as erro:                          # noqa: BLE001
        erro_do_insert = str(erro)

    # ── PÓS-LEITURA — e é ela que decide, não o retorno do insert ───────
    escrita = memoria.derivado_com_identidade(identidade)

    if erro_do_insert and escrita:
        # A CORRIDA: outro escritor chegou primeiro entre a nossa leitura e o
        # nosso insert. A violacao de unicidade NAO e sucesso automatico — vai-se
        # ler a linha que venceu e compara-se.
        divergem = _difere(escrita, esperado, RESULTADO)
        if divergem:
            return {"ESTADO": DERIVATION_DRIFT, "DIVERGENCIAS": divergem,
                    "PORQUE": ("outro escritor ganhou a corrida E o resultado dele "
                               "difere do nosso. Nao se sobrepoe."),
                    "LINHA_EXISTENTE": escrita, "BYTES_GUARDADOS": True,
                    "NOVO_UPLOAD": novo_upload}
        return {"ESTADO": REUSED_AFTER_RACE, "LINHA_EXISTENTE": escrita,
                "PORQUE": ("outro escritor ganhou a corrida e escreveu o MESMO "
                           "resultado. Foi lido e comparado — nao presumido."),
                "BYTES_GUARDADOS": True, "NOVO_UPLOAD": novo_upload}

    if erro_do_insert or not escrita:
        # BYTES GUARDADOS, MEMORIA POR ESCREVER. Nao se apaga o artefato para
        # fingir que a transacao foi atomica: e a lei do G-42, e o byte
        # preservado e a unica evidencia que sobra.
        return {"ESTADO": METADATA_NOT_RECONCILED,
                "ERRO": erro_do_insert,
                "STORAGE_PATH": caminho,
                "PORQUE": ("os bytes ficaram no armazem e a linha nao entrou. Os "
                           "bytes NAO sao apagados: apagar evidencia para fingir "
                           "atomicidade e pior do que a falha."),
                "BYTES_GUARDADOS": True, "NOVO_UPLOAD": novo_upload,
                "BYTE_APAGADO_COMO_COMPENSACAO": "NAO"}

    divergem = _difere(escrita, esperado, CAMPOS_DA_LINHA)
    if divergem:
        return {"ESTADO": METADATA_NOT_RECONCILED, "DIVERGENCIAS": divergem,
                "PORQUE": ("a linha entrou, mas nao e a que se pediu. Contar nao "
                           "e conferir."),
                "BYTES_GUARDADOS": True, "NOVO_UPLOAD": novo_upload}

    return {"ESTADO": INSERTED, "LINHA_ESCRITA": escrita,
            "STORAGE_PATH": caminho, "BYTES_GUARDADOS": True,
            "NOVO_UPLOAD": novo_upload,
            "CAMPOS_CONFERIDOS": len(CAMPOS_DA_LINHA),
            "PORQUE": "escrita, lida de volta e conferida campo a campo."}


def _porque_reused(ja: dict, pedido: dict) -> str:
    """A explicação muda quando a testemunha é outra — e essa distinção importa.

    Duas capturas dos mesmos bytes derivadas com a mesma receita dão UMA
    derivação: o grão é CONTEÚDO POR RECEITA. A linha aponta para a cópia que
    foi lida da primeira vez, e **não se troca** — trocá-la reescreveria a
    história por nada. A outra captura continua inteira em `raw_asset`.
    """
    if str(ja.get("raw_asset_id")) != str(pedido["raw_asset_id"]):
        return ("reencontro: a mesma receita sobre os MESMOS bytes, chegando por "
                "outra captura. UMA derivacao, e a testemunha existente fica como "
                "esta — a outra captura continua inteira em raw_asset.")
    return ("reencontro: mesma identidade e mesmo resultado, LIDOS e comparados. "
            "Nenhum byte subiu, nenhuma linha entrou.")
