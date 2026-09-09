#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTRATO COMUM DE ARTEFATO — a língua que todo executor vai falar.

O PROBLEMA QUE ISTO RESOLVE
---------------------------
Hoje cada executor entrega o resultado à sua maneira: um deixa uma pasta, outro
um JSON, outro um PDF, outro uma transcrição, outro um ficheiro solto. Ligar o
orquestrador a isto obrigaria o cérebro da casa a **adivinhar** o que cada um
produziu — e adivinhação no meio não se conserta depois; espalha-se.

    ANTES DE MANDAR ALGUÉM TRABALHAR, É PRECISO COMBINAR COMO ELE ENTREGA.

Este ficheiro é essa combinação. Um artefato é uma coisa concreta que existe no
disco e que sabe responder a cinco perguntas:

    QUEM SOU?        ARTIFACT_ID + SHA256
    DE ONDE VIM?     SOURCE_ID, e — se for derivado — PARENT_ARTIFACT_ID
    QUANDO?          os tempos, cada um no seu campo
    ONDE?            a geografia, cada uma no seu campo
    QUEM ME FEZ?     EXECUTOR + versões + RUN_ID

O QUE ISTO **NÃO** É
--------------------
Não é um extrator de PDF. Não é um formato de ficheiro novo. Não é uma base de
dados. É só o combinado — a folha onde cada executor escreve o que entregou,
na mesma ordem e com as mesmas palavras.

O PDF é apenas o primeiro executor a prová-lo. Depois virão HTTP, Instagram,
YouTube, navegador, SINTONIA SCRAP e API, e todos terão de preencher esta
mesma folha.

O QUE FOI REAPROVEITADO, E DE ONDE
----------------------------------
Quase tudo. O censo em `docs/operacao/CENSO-DOS-CONTRATOS-DE-ARTEFATO.md`
mostra que tempo, geografia e procedência já são lei madura aqui:

  · `regras/proveniencia.py` já tem `CAMPOS_RUN`, com `ACTOR`/`ACTOR_VERSION`
    — que são, na prática, o executor e a sua versão. Não se inventou nome novo.
  · `data/samples/RUN-MANIFEST.json` já é o recibo das corridas, e escreve-se
    acrescentando, nunca substituindo.
  · `admissao/admissao.py` já é a porta, com cinco respostas possíveis.
  · `admissao.pronto_para_inteligencia()` já é o READY desta casa.

O que **não** existia era a ideia de artefato: a coisa em si, com nome próprio
e que sabe dizer de que outra nasceu. `ARTIFACT_ID`, `PARENT_ARTIFACT_ID`,
`EXECUTOR_VERSION` e `PIPELINE_VERSION` apareciam em **zero** ficheiros.

AS TRÊS REGRAS QUE NÃO SE DOBRAM
--------------------------------
1. **NUNCA FABRICAR VALOR PARA ENCHER CAMPO.** Não sei → `NAO SEI`. Não se
   aplica → `NAO_SE_APLICA`. Um campo cheio de mentira é pior que um vazio,
   porque o vazio avisa e a mentira não.

2. **CADA TEMPO NO SEU CAMPO.** `FACT_TIME` é quando o fato aconteceu.
   `DERIVED_AT` é quando esta máquina fez o derivado. Copiar um para o outro
   por conveniência transforma a hora de um trabalho de escritório na data de
   um acontecimento no campo.

3. **RAW É IMUTÁVEL.** O original nunca é reescrito, normalizado, comprimido
   nem substituído pelo seu texto. O texto nasce **ao lado**, como outra coisa,
   com pai declarado.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

# ── AS DUAS AUSÊNCIAS, E SÃO DIFERENTES ─────────────────────────────────────
# «Não sei» é uma confissão: o valor existe algures e eu não o alcancei.
# «Não se aplica» é uma constatação: a pergunta não faz sentido para isto.
# Juntá-las apaga a diferença entre um buraco a tapar e um campo que está certo.
NAO_SEI = "NAO SEI"
NAO_SE_APLICA = "NAO_SE_APLICA"

# ── OS TIPOS DE ARTEFATO ────────────────────────────────────────────────────
RAW = "RAW"              # veio de fora e é intocável
DERIVED = "DERIVED"      # nasceu de outro artefato, aqui dentro

# ── AS MANEIRAS DE DERIVAR ──────────────────────────────────────────────────
# `MANUAL_LEGACY` existe porque a casa tem seis textos tirados de PDF à mão,
# antes de haver contrato. Não se apagam e não se fingem automáticos: ganham um
# nome próprio que diz exatamente o que são.
TEXT_EXTRACTION = "TEXT_EXTRACTION"
MANUAL_LEGACY = "MANUAL_LEGACY"

# ── OS ESTADOS DE DERIVAÇÃO ─────────────────────────────────────────────────
# NEEDS_OCR **NÃO** é rejeição. Um PDF que é fotografia de papel não é
# irrelevante nem mau: é um trabalho que ainda não foi feito. Confundir «ainda
# não consegui ler» com «não serve» é a mesma família de erro que dava NAO na
# admissão quando faltava palavra no dicionário.
TEXT_LAYER_PRESENT = "TEXT_LAYER_PRESENT"
TEXT_LAYER_ABSENT = "TEXT_LAYER_ABSENT"      # → NEEDS_OCR
EXTRACTION_ERROR = "EXTRACTION_ERROR"
DERIVATION_UNKNOWN = "UNKNOWN"

NEEDS_OCR = "NEEDS_OCR"


def agora() -> str:
    """O instante, em UTC, no formato que o resto da casa já usa."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_do_ficheiro(caminho: str) -> str:
    """A impressão digital de um ficheiro, lida byte a byte.

    Sem normalizar nada. Um artefato bruto é bytes; mexer neles para «arrumar»
    antes de assinar seria assinar outra coisa.
    """
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def artifact_id(sha256: str, tipo: str, derivacao: str = "") -> str:
    """O nome próprio de um artefato. Determinístico, e honesto sobre o que é.

    POR QUE ASSIM

    A fonte não nos deu identidade nenhuma: um PDF de boletim regional não vem
    com número de série. Então há duas saídas — inventar um número e fingir que
    é da fonte, ou construir um a partir do que o artefato realmente é.

    Aqui constrói-se. O nome sai da impressão digital do conteúdo, com o tipo à
    frente para nunca se confundir um bruto com o seu derivado:

        RAW-a1b2c3d4e5f6a7b8
        DERIVED-TEXT_EXTRACTION-9f8e7d6c5b4a3928

    Determinístico quer dizer: o mesmo conteúdo dá sempre o mesmo nome, em
    qualquer máquina, hoje e daqui a um ano. É isso que torna a idempotência
    possível — correr duas vezes não cria dois artefatos.

    E é por isso que o prefixo importa: um PDF e o texto que sai dele são
    coisas diferentes, com nomes diferentes, mesmo que um venha do outro.
    """
    curto = sha256[:16]
    if tipo == RAW:
        return f"RAW-{curto}"
    if derivacao:
        return f"DERIVED-{derivacao}-{curto}"
    return f"DERIVED-{curto}"


@dataclass
class Artefato:
    """A folha que todo executor preenche. Uma linha por coisa entregue.

    Os campos estão agrupados pela pergunta que respondem, e a ordem é a ordem
    das perguntas — para quem lê de cima a baixo ir sabendo mais a cada bloco.
    """

    # ── QUEM SOU ────────────────────────────────────────────────────────────
    ARTIFACT_ID: str
    ARTIFACT_TYPE: str                      # RAW ou DERIVED
    STORAGE_LOCATION: str                   # onde está, relativo à raiz
    SHA256: str
    CONTENT_TYPE: str = NAO_SEI             # application/pdf, text/plain...
    BYTES: int = 0

    # ── DE ONDE VIM ─────────────────────────────────────────────────────────
    SOURCE_ID: str = NAO_SEI
    SOURCE_URL: str = NAO_SEI
    PUBLISHER: str = NAO_SEI
    # O pai. Um RAW não tem pai — não é ausência de informação, é a natureza da
    # coisa; por isso NAO_SE_APLICA e não NAO SEI.
    PARENT_ARTIFACT_ID: str = NAO_SE_APLICA
    PARENT_SHA256: str = NAO_SE_APLICA
    DERIVATION_TYPE: str = NAO_SE_APLICA

    # ── ONDE (geografia — três coisas diferentes) ───────────────────────────
    # COUNTRY_SCOPE é a nossa decisão: de que frente de trabalho isto faz parte.
    # SOURCE_LOCATION é onde a fonte está.
    # FACT_LOCATION é onde o fato aconteceu.
    # As três podem ser diferentes, e muitas vezes são: uma revista italiana
    # (SOURCE_LOCATION=IT) pode noticiar uma praga em Espanha (FACT_LOCATION=ES)
    # dentro de um trabalho nosso sobre Itália (COUNTRY_SCOPE=IT). Preencher
    # umas com as outras destrói exatamente a informação que interessa.
    COUNTRY_SCOPE: str = NAO_SEI
    SOURCE_LOCATION: str = NAO_SEI
    FACT_LOCATION: str = NAO_SEI

    # ── EM QUE LÍNGUA ───────────────────────────────────────────────────────
    # País NÃO é língua. Um documento da frente italiana pode estar em inglês,
    # e escrever IT aqui por omissão seria uma afirmação sobre o conteúdo feita
    # sem ninguém ter lido o conteúdo.
    ITEM_LANGUAGE: str = NAO_SEI

    # ── QUANDO (cinco tempos, cinco campos) ─────────────────────────────────
    FACT_TIME: str = NAO_SEI          # quando o fato aconteceu
    PUBLISHED_AT: str = NAO_SEI       # quando a fonte publicou
    OBSERVED_AT: str = NAO_SEI        # quando a fonte registou ter observado
    COLLECTED_AT: str = NAO_SEI       # quando o SINTONIA trouxe o original
    DERIVED_AT: str = NAO_SE_APLICA   # quando ESTA máquina fez o derivado

    # ── QUEM ME FEZ ─────────────────────────────────────────────────────────
    RUN_ID: str = NAO_SEI
    EXECUTOR_ID: str = NAO_SEI
    EXECUTOR_VERSION: str = NAO_SEI
    PIPELINE_VERSION: str = NAO_SEI

    # ── EM QUE PÉ ESTOU ─────────────────────────────────────────────────────
    STATE: str = DERIVATION_UNKNOWN
    ERROR: str = ""
    COST: str = NAO_SE_APLICA
    NOTES: dict = field(default_factory=dict)

    def para_json(self) -> dict:
        return asdict(self)


def raw_do_disco(caminho_abs: str, raiz: str, **campos) -> Artefato:
    """Faz a ficha de um ficheiro que já existe, sem lhe tocar.

    Repare no que esta função **não** faz: não abre o ficheiro para adivinhar
    de quando é, não lê o nome para deduzir o país, não infere a língua. Tudo
    isso teria de vir de fora, com prova. Aqui só se mede o que é medível sem
    interpretar: onde está, quanto pesa, e qual a sua impressão digital.
    """
    rel = os.path.relpath(caminho_abs, raiz).replace("\\", "/")
    sha = sha256_do_ficheiro(caminho_abs)
    ext = os.path.splitext(caminho_abs)[1].lower()
    tipos = {".pdf": "application/pdf", ".txt": "text/plain",
             ".json": "application/json", ".html": "text/html"}
    return Artefato(
        ARTIFACT_ID=artifact_id(sha, RAW),
        ARTIFACT_TYPE=RAW,
        STORAGE_LOCATION=rel,
        SHA256=sha,
        CONTENT_TYPE=tipos.get(ext, NAO_SEI),
        BYTES=os.path.getsize(caminho_abs),
        **campos,
    )


def derivado_de(pai: Artefato, caminho_abs: str, raiz: str, *,
                derivacao: str, executor: str, executor_versao: str,
                pipeline_versao: str, run_id: str, estado: str,
                erro: str = "", notas: dict | None = None) -> Artefato:
    """Faz a ficha de uma coisa que nasceu de outra.

    O QUE O FILHO HERDA, E O QUE NÃO HERDA

    Herda a **procedência** — de onde o original veio, quando o fato aconteceu,
    onde ficou o fato, em que país entra no nosso trabalho. Isso é verdade
    sobre o assunto, e o assunto não muda por o termos passado a texto.

    Não herda **identidade**: o filho tem nome próprio e impressão digital
    própria. E não herda `COLLECTED_AT`, porque esta corrida não foi buscar
    nada a lado nenhum — só abriu o que já cá estava. O que ela ganha é
    `DERIVED_AT`, que é outra coisa e vive noutro campo.
    """
    rel = os.path.relpath(caminho_abs, raiz).replace("\\", "/")
    sha = sha256_do_ficheiro(caminho_abs)
    return Artefato(
        ARTIFACT_ID=artifact_id(sha, DERIVED, derivacao),
        ARTIFACT_TYPE=DERIVED,
        STORAGE_LOCATION=rel,
        SHA256=sha,
        CONTENT_TYPE="text/plain",
        BYTES=os.path.getsize(caminho_abs),

        SOURCE_ID=pai.SOURCE_ID,
        SOURCE_URL=pai.SOURCE_URL,
        PUBLISHER=pai.PUBLISHER,
        PARENT_ARTIFACT_ID=pai.ARTIFACT_ID,
        PARENT_SHA256=pai.SHA256,
        DERIVATION_TYPE=derivacao,

        COUNTRY_SCOPE=pai.COUNTRY_SCOPE,
        SOURCE_LOCATION=pai.SOURCE_LOCATION,
        FACT_LOCATION=pai.FACT_LOCATION,
        ITEM_LANGUAGE=pai.ITEM_LANGUAGE,

        FACT_TIME=pai.FACT_TIME,
        PUBLISHED_AT=pai.PUBLISHED_AT,
        OBSERVED_AT=pai.OBSERVED_AT,
        COLLECTED_AT=pai.COLLECTED_AT,
        DERIVED_AT=agora(),

        RUN_ID=run_id,
        EXECUTOR_ID=executor,
        EXECUTOR_VERSION=executor_versao,
        PIPELINE_VERSION=pipeline_versao,

        STATE=estado,
        ERROR=erro,
        COST="LOCAL",
        NOTES=notas or {},
    )


# ── AS PROIBIÇÕES, EM CÓDIGO ────────────────────────────────────────────────
# Escrever a lei no comentário não impede ninguém de a quebrar. Estas funções
# existem para a lei ter dentes: se alguém copiar um tempo para o outro, isto
# reclama antes de o valor entrar em qualquer ficheiro.
def conferir(a: Artefato) -> list[str]:
    """Devolve a lista de leis quebradas. Vazia quer dizer que está de pé."""
    quebras = []

    # 1 · o tempo do fato não se enche com a hora do trabalho
    if a.FACT_TIME not in (NAO_SEI, NAO_SE_APLICA, ""):
        for nome, v in (("DERIVED_AT", a.DERIVED_AT),
                        ("COLLECTED_AT", a.COLLECTED_AT)):
            if v not in (NAO_SEI, NAO_SE_APLICA, "") and a.FACT_TIME == v:
                quebras.append(
                    f"FACT_TIME == {nome}: a hora em que a maquina trabalhou "
                    f"nao e a hora em que o fato aconteceu")
        if (a.PUBLISHED_AT not in (NAO_SEI, NAO_SE_APLICA, "")
                and a.FACT_TIME == a.PUBLISHED_AT
                and a.NOTES.get("FACT_TIME_BASIS") != "PUBLISHED_AT_COM_PROVA"):
            quebras.append(
                "FACT_TIME == PUBLISHED_AT sem prova: publicar e contar, e "
                "contar nao e acontecer. Se for mesmo o mesmo instante, tem de "
                "haver prova declarada em NOTES.FACT_TIME_BASIS")

    # 2 · o lugar do fato não se enche com o lugar da fonte nem com o escopo
    if a.FACT_LOCATION not in (NAO_SEI, NAO_SE_APLICA, ""):
        base = a.NOTES.get("FACT_LOCATION_BASIS", "")
        if not base:
            quebras.append(
                "FACT_LOCATION preenchido sem dizer de onde saiu. Onde a fonte "
                "esta e onde o fato aconteceu sao coisas diferentes, e o "
                "escopo do pais e uma decisao nossa, nao uma prova")

    # 3 · o pai tem de estar inteiro, ou inteiramente ausente
    tem = [a.PARENT_ARTIFACT_ID, a.PARENT_SHA256, a.DERIVATION_TYPE]
    conhecidos = [x for x in tem if x not in (NAO_SEI, NAO_SE_APLICA, "")]
    if conhecidos and len(conhecidos) != 3:
        quebras.append(
            "pai pela metade: ou se sabe quem e o pai, a sua impressao digital "
            "e como se derivou, ou nao se sabe nada. Meio pai nao se confere")

    # 4 · um derivado não pode ter o mesmo nome do pai
    if a.ARTIFACT_TYPE == DERIVED and a.ARTIFACT_ID == a.PARENT_ARTIFACT_ID:
        quebras.append("o derivado tem o mesmo nome do pai: sao duas coisas")

    # 5 · erro sem explicação é pior que erro
    if a.STATE == EXTRACTION_ERROR and not a.ERROR:
        quebras.append("estado de erro sem uma linha a dizer qual foi")

    return quebras
