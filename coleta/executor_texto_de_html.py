#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O TERCEIRO EXECUTOR A FALAR A LÍNGUA COMUM — texto a partir de HTML.

ISTO NÃO É UM EXTRATOR NOVO. É UMA LIGAÇÃO.
--------------------------------------------
A peça que transforma HTML em texto **já existia nesta árvore** desde antes
desta missão: `coleta/texto_fonte.py::limpar(dados, ctype)`. Ela tira
`<script>`/`<style>`, tira as marcas, desfaz as entidades e normaliza os
espaços. Medido a 2026-09-21, antes de este ficheiro existir:

    `limpar()` tinha ZERO chamadores no código de produção.
    O único que lhe chamava era um MEDIDOR
    (`medidas/porque_a_sala_nao_recebeu.py`), que mede e não colhe.

    CAPABILITY EXISTS != EDGE EXISTS.
    UMA CAPACIDADE QUE NINGUÉM CHAMA NÃO É UMA ETAPA DA ESTRADA.

Por isso a classificação do bloqueio é `MISSING_ROUTE`, e **não**
`NOT_IMPLEMENTED` (a capacidade existe) nem `NOT_APPLICABLE` (a derivação
APLICA-SE: dos 85 documentos HTML medidos, 85 dão texto, com 6 328 caracteres
de média).

⚠️ E NÃO SE DUPLICOU `limpar()`. Este ficheiro **importa-a**. Copiar as seis
linhas de expressão regular para aqui daria dois donos da mesma pergunta, e no
dia em que um deles aprendesse a tratar `<noscript>` os dois divergiam em
silêncio — que é o pecado que esta casa já nomeou (`O8C`).

    ONE CONCEPT -> ONE OWNER. QUEM SABE EXTRAIR É QUEM DIZ COMO SE EXTRAI.

O EXECUTOR NÃO JULGA
--------------------
Como o de PDF e o de mídia: aqui não se decide se um documento é relevante.
Isso é da porta de admissão. Aqui respondem-se quatro perguntas técnicas:

    consegui ler?   de qual original?   quanto texto saiu?   houve erro?

A FORMA É A DOS OUTROS DOIS, DE PROPÓSITO
------------------------------------------
`EXECUTOR_ID` · `CAPACIDADE` · `derivar_um(raw_asset_id, ..., armazem,
memoria, relogio, contexto_da_passagem)`. A posição dos parâmetros é a mesma
de `executor_texto_de_pdf.derivar_um` e de
`executor_transcricao_midia.derivar_um`, para que
`coleta/derivacao_forward.correr()` possa chamar os três sem saber qual tem na
mão.

    DOIS EXECUTORES COM A MESMA FORMA SÃO UM PONTO DE ESCOLHA.
    DOIS COM FORMAS DIFERENTES SÃO DOIS CAMINHOS, E AÍ ALGUÉM ESCREVE O `if`.

⚠️ DECLARAR NÃO É LIGAR. `SUPPORTS` viveu um ano inteiro em
`executor_texto_de_pdf.py` com zero leitores, e o próprio ficheiro escreveu o
preço disso. Por isso a ficha abaixo **não** basta: este executor só está
ligado porque o nome do módulo entrou em
`coleta/ingresso.py::_DONOS_DA_DERIVACAO`, e há prova de runtime —
`ingresso.executor_para("text/html")` tem de devolver **este** módulo.

SEM REDE
--------
Nenhuma ligação. `limpar()` não abre socket nenhum: só o `main()` de
`texto_fonte.py` é que vai à rede, e esse não é chamado daqui. O que entra são
bytes que o armazém já tem.

CORRER
------
    py coleta/executor_texto_de_html.py --ficha            # a capacidade
    py coleta/executor_texto_de_html.py --seco <ficheiro>  # só olha e conta
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402
import proveniencia as pv  # noqa: E402

from coleta.texto_fonte import limpar  # noqa: E402 — O DONO ÚNICO DA EXTRAÇÃO

# ── A FICHA DE CAPACIDADE ───────────────────────────────────────────────────
EXECUTOR_ID = "texto-de-html"
EXECUTOR_VERSION = "1"
PIPELINE_VERSION = "1"

#: As espécies exactas que esta ponte abre.
#:
#: ⚠️ POR TIPO EXACTO, E NÃO POR FAMÍLIA — e a escolha é medida, não estética.
#: O executor de mídia declara-se por família (`audio`, `video`) porque a lista
#: exacta nunca fecha. Aqui é o contrário: a família `text` inclui
#: `text/plain`, `text/csv` e `text/markdown`, e **nenhum** desses precisa
#: desta ferramenta — `limpar()` sobre `text/csv` devolveria o CSV inteiro com
#: os espaços mexidos e chamar-lhe-ia extração.
#:
#:     UMA FAMÍLIA QUE APANHA MAIS DO QUE SE SABE ABRIR
#:     NÃO É GENEROSIDADE: É UMA RECLAMAÇÃO DE CAPACIDADE FALSA.
#:
#: `IT-T4-001` é `text/csv` e está medido nesta casa como `MISSING_ROUTE` de
#: outro dono — declarar `text` aqui roubava-lhe a rota e produzia lixo com ar
#: de texto.
ACEITA = ("text/html", "application/xhtml+xml")

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    # `HTML_RAW` segue a forma de `PDF_RAW` — o nome da espécie para gente ler.
    "SUPPORTS": ["HTML_RAW"],
    # E o MESMO facto na língua que a porta lê: o `media_type` que o
    # `raw_asset` guarda. Não é um segundo dono da capacidade: é a mesma
    # declaração, legível pelos dois lados.
    "ACEITA_MEDIA_TYPES": ACEITA,
    "ACEITA_FAMILIAS": (),
    "PRODUCES": ["TEXT_EXTRACTED"],
    "NETWORK_REQUIRED": "NO",
    "OCR": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    # ⚠️ NÃO HÁ FERRAMENTA DE FORA, e por isso este executor não tem o estado
    # `FERRAMENTA_AUSENTE` que o de PDF tem. `limpar()` é Python puro da
    # biblioteca padrão (`re`, `html`, `zlib`). Numa máquina sem `pdftotext` o
    # executor de PDF devolve `EXECUTOR_UNAVAILABLE`; este não pode ficar
    # indisponível por falta de instalação.
    "FERRAMENTA_EXTERNA": None,
    # Quem realmente extrai. Aponta-se para o dono em vez de o repetir — a
    # mesma disciplina do `ASR_OWNER` do executor de mídia.
    "TEXT_OWNER": "coleta/texto_fonte.py::limpar",
}

#: O `kind` da linha do derivado, na língua da tabela.
#:
#: ⚠️ PROCUROU-SE ANTES DE CRIAR, e a casa já tinha o nome — e não por acaso:
#: `supabase/migrations/022_o_derivado_ganha_casa.sql` escreve, à frente do
#: valor, o comentário `-- pdftotext, html->texto`. O vocabulário reservou a
#: palavra para este caso antes de existir quem a usasse.
#:
#:     ANTES DE CRIAR UM NOME, PROCURAR SE A CASA JÁ TEM UM.
KIND = "TEXT_EXTRACTION"

#: A espécie do texto que sai daqui, lida do dono do vocabulário
#: (`regras/proveniencia.py`) e não escrita aqui.
#:
#:     PAGE_TEXT      texto que estava numa PÁGINA publicada
#:     ORIGINAL       ninguém traduziu nada: é a língua em que foi publicado
#:
#: ⚠️ `TEXT_KIND_BASIS = DECLARED_BY_ROUTE`, e não `NOT_DECLARED`. A rota
#: declarou que aqueles bytes são `text/html` — a espécie do texto sai dessa
#: declaração, e não de alguém a ler o texto para adivinhar o que ele é. É
#: exactamente o limite que o dono escreveu: «QUAL CAMPO EU LI É UM FACTO
#: SOBRE MIM, NÃO UM PALPITE SOBRE O CONTEÚDO» — e ele justifica a ESPÉCIE,
#: nunca a LÍNGUA, que continua `UNKNOWN`.
TEXT_KIND = pv.PAGE_TEXT
TEXT_RELATION = pv.ORIGINAL
TEXT_BASIS = pv.DECLARED_BY_ROUTE

#: Como o texto nasceu. `EXTRACTED_FROM_DOCUMENT` e não
#: `SCRAPED_FROM_RENDERED_PAGE`: esta casa **não renderizou** página nenhuma.
#: Leram-se os bytes do documento arquivado no armazém. Dizer «raspado da
#: página renderizada» prometeria um navegador que não correu.
METODO = pv.EXTRAIDO_DO_DOCUMENTO

#: A ferramenta, obrigatória porque `EXTRACTED_FROM_DOCUMENT` é método de
#: máquina e o dono do vocabulário recusa máquina sem máquina declarada.
FERRAMENTA = "coleta/texto_fonte.py::limpar"

# ── OS MOTIVOS DE «NÃO SAIU DERIVADO» ───────────────────────────────────────
# ⚠️ NÃO SE REUTILIZOU `art.TEXT_LAYER_ABSENT`, E A RAZÃO ESTÁ ESCRITA AO LADO
# DELE: `leis/artefato.py:102` anota-o com `# → NEEDS_OCR`. Um HTML sem texto
# **não precisa de OCR** — ou é uma casca que monta o conteúdo com JavaScript,
# ou é uma página vazia. Herdar o nome faria o recibo mandar alguém comprar
# reconhecimento óptico para um ficheiro que não tem imagem nenhuma.
#
#     UM NOME EMPRESTADO TRAZ A CONCLUSÃO DE QUEM O CUNHOU.
#
#: O documento não trazia texto. Facto sobre o ORIGINAL — a ferramenta não
#: falhou. Irmão de `SEM_FAIXA_DE_AUDIO` no executor de mídia.
SEM_TEXTO_NO_DOCUMENTO = "SEM_TEXTO_NO_DOCUMENTO"

#: Os bytes não são HTML, e a espécie declarada dizia que eram.
#:
#: ⚠️ ISTO EXISTE PARA NÃO ROUBAR O TRABALHO AO DONO CERTO. `limpar()` tem um
#: ramo de PDF lá dentro (`_pdf`), e ele dispara pelos bytes — `%PDF-` — mesmo
#: quando o `ctype` diz HTML. Sem esta guarda, um PDF mal declarado entraria
#: aqui e sairia com uma extração pobre, feita por quem não é o dono de PDF
#: nesta casa, e a linha do derivado ficaria carimbada `texto-de-html`.
#:
#:     DOIS EXTRACTORES A ABRIR A MESMA ESPÉCIE SÃO DOIS DONOS,
#:     E O SEGUNDO GANHA POR ACIDENTE DE DECLARAÇÃO.
BYTES_NAO_SAO_HTML = "BYTES_NAO_SAO_HTML"

#: A unidade de texto não passou no dono do vocabulário. Mesmo nome, mesmo
#: significado e mesmo destino do executor de mídia — a forma da unidade é que
#: falhou, e isso é um facto sobre NÓS.
UNIDADE_RECUSADA = "UNIDADE_RECUSADA"

#: Os oito primeiros bytes que identificam um PDF, sem ambiguidade.
ASSINATURA_PDF = b"%PDF-"


def aceita(media_type) -> bool:
    """Esta ficha abre esta espécie? → bool. A mesma regra que a porta aplica."""
    tipo = str(media_type or "").split(";")[0].strip().lower()
    return tipo in ACEITA


def extrair(dados: bytes, media_type: str = "text/html") -> tuple:
    """Tenta tirar o texto. Devolve `(texto, estado, erro, medidas)`.

    Três saídas, e nenhuma delas é «não serve»:

        TEXT_LAYER_PRESENT      saiu texto
        SEM_TEXTO_NO_DOCUMENTO  leu bem, e não havia letra nenhuma
        EXTRACTION_ERROR        a extração partiu-se — problema NOSSO

    ⚠️ `TEXT_LAYER_PRESENT` é reaproveitado de propósito (é de
    `leis/artefato.py` e diz exactamente isto: saiu texto), enquanto o estado
    de ausência tem nome próprio, porque o de lá promete OCR.
    """
    if dados[:5] == ASSINATURA_PDF:
        return ("", BYTES_NAO_SAO_HTML,
                "os bytes comecam por %PDF- e a especie declarada era %r. O "
                "dono de PDF nesta casa e coleta/executor_texto_de_pdf.py"
                % media_type, {"BYTES": len(dados)})
    try:
        texto = limpar(dados, media_type or "text/html")
    except Exception as e:                                       # noqa: BLE001
        return ("", art.EXTRACTION_ERROR,
                "%s: %s" % (type(e).__name__, str(e)[:200]),
                {"BYTES": len(dados)})

    # PRODUZIR FICHEIRO VAZIO NÃO É SUCESSO — a mesma lei do executor de PDF.
    sem_brancos = len("".join(texto.split()))
    medidas = {"BYTES": len(dados),
               "CHARACTERS": len(texto),
               "NON_WHITESPACE_CHARACTERS": sem_brancos}
    if sem_brancos == 0:
        return texto, SEM_TEXTO_NO_DOCUMENTO, "", medidas
    return texto, art.TEXT_LAYER_PRESENT, "", medidas


def derivar_um(raw_asset_id, html, armazem, memoria, relogio=None,
               contexto_da_passagem=None) -> dict:
    """Um HTML, um pai canónico, um texto — pelo dono da escrita.

    O segundo parâmetro chama-se `html` e não `pdf` porque é o que é — mas a
    POSIÇÃO é a mesma dos outros dois executores, e é isso que deixa
    `derivacao_forward.correr()` chamar os três sem um `if`.

    ⚠️ O QUE ESTE EXECUTOR NÃO CALCULA, E POR ISSO NÃO PODE MENTIR:
    `parent_sha256`, `sha256` do filho, `parameters_hash`, `derived_at` e
    `storage_path` são todos do dono da escrita
    (`guarda/preservar_derivado.py`). Ele entrega a RECEITA e os BYTES.

    `contexto_da_passagem` é um envelope OPACO que este executor não lê.
    Viaja daqui para o dono da escrita e nada mais.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado

    contexto = contexto_da_passagem or {}
    # ⚠️ A ESPÉCIE DE ENTRADA NÃO SE LÊ AQUI, E ISSO É DELIBERADO.
    # `contexto_da_passagem` é um envelope OPACO (a doutrina está escrita em
    # `executor_texto_de_pdf.derivar_um`): ler lá dentro quebrá-la-ia. E não é
    # preciso — quem escolhe este executor é `ingresso.executor_para`, que só
    # o escolhe para as espécies de `ACEITA`, e `limpar()` trata `text/html` e
    # `application/xhtml+xml` da mesma maneira.
    #
    #     TRANSPORTAR NÃO É CONHECER.
    media_type = "text/html"

    try:
        with open(html, "rb") as fh:
            dados = fh.read()
    except OSError as e:
        # ⚠️ NÃO CONSEGUIR ABRIR O FICHEIRO É AVARIA NOSSA, e não um documento
        # vazio. Um executor que confunde «não tenho os bytes» com «não há
        # texto» mente sobre o acervo, e a mentira fica guardada.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": art.EXTRACTION_ERROR,
                "ERRO": "nao consegui ler %s: %s" % (html, e),
                "PORQUE": "nao consegui ler %s: %s" % (html, e),
                "NAO_SIGNIFICA": "que o documento nao tem texto.",
                "MEDIDAS": {}}

    texto, estado, erro, medidas = extrair(dados, media_type)
    if estado != art.TEXT_LAYER_PRESENT:
        # Sem texto não há artefato. Isso é um facto sobre o ORIGINAL (ou sobre
        # a declaração da espécie), e vai no recibo — não vira linha de
        # derivado.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": estado,
                "ERRO": erro,
                "PORQUE": erro or "o documento nao trazia texto",
                "NAO_SIGNIFICA": ("que a Admissao recusou. A Admissao nem foi "
                                  "chamada."),
                "MEDIDAS": medidas}

    # ── A RECEITA ───────────────────────────────────────────────────────────
    # ⚠️ SÓ ENTRA AQUI O QUE DEFINE O ARTEFATO, NUNCA O QUE MEDE A MÁQUINA.
    # `parameters` é hasheado para `parameters_hash`, e esse hash é metade da
    # identidade da receita. `CHARACTERS` não entra: é medida, e o mesmo
    # documento extraído duas vezes pela mesma régua tem de reencontrar a
    # primeira linha em vez de escrever uma segunda.
    #
    #     O QUE VARIA ENTRE DUAS CORRIDAS IGUAIS NÃO É IDENTIDADE: É MEDIDA.
    parametros = {
        "TEXT_KIND": TEXT_KIND,
        "TEXT_RELATION": TEXT_RELATION,
        "TEXT_BASIS": TEXT_BASIS,
        "DERIVATION_METHOD": METODO,
        "TEXT_OWNER": CAPACIDADE["TEXT_OWNER"],
    }

    # ── A UNIDADE DE TEXTO, MONTADA E CONFERIDA PELO DONO ───────────────────
    # O construtor e o validador vêm de `regras/proveniencia.py`, e correm
    # ANTES de `preservar_derivado` de propósito: apanha-se a unidade inválida
    # enquanto ainda não se escreveu byte nenhum no armazém.
    unidade = pv.unidade_de_texto(
        texto=texto,
        kind=TEXT_KIND,
        kind_basis=TEXT_BASIS,
        relation=TEXT_RELATION,
        # ⚠️ A LÍNGUA NÃO SE DEDUZ DO TEXTO, e este executor não tem por onde a
        # saber: nenhum provedor a declarou a estes bytes. Fica `UNKNOWN`, que
        # é a resposta certa — «texto italiano não prova `it`».
        language=None,
        raw_observation_id=raw_asset_id,
        derivation_method=METODO,
        # A morada dentro desta observação, com produtor e versão: duas
        # extrações do MESMO HTML por réguas diferentes são duas unidades
        # legítimas.
        unit_id="TU-%s-%s" % (EXECUTOR_ID, EXECUTOR_VERSION),
        tool=FERRAMENTA)

    problemas = pv.conferir_unidade_de_texto(unidade)
    if problemas:
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": UNIDADE_RECUSADA,
                "ERRO": "; ".join(str(p) for p in problemas)[:300],
                "PORQUE": "; ".join(str(p) for p in problemas)[:300],
                "NAO_SIGNIFICA": ("que o documento nao tem texto, nem que a "
                                  "Admissao recusou. A unidade de texto e que "
                                  "nao passou no dono do vocabulario."),
                "MEDIDAS": medidas}

    recibo = preservar_derivado(
        {**contexto,
         "raw_asset_id": raw_asset_id,
         "kind": KIND,
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         "parameters": parametros,
         "serie_posicao": None,
         "media_type": "text/plain"},
        texto.encode("utf-8"), armazem, memoria,
        relogio=relogio or agora_utc)

    # A espécie do texto viaja no recibo TAMBÉM, e não só dentro de
    # `parameters`: quem lê o recibo não tem de desempacotar um hash para saber
    # que isto é `PAGE_TEXT` e não uma `CAPTION`.
    return {**recibo,
            "TEXT_KIND": TEXT_KIND,
            "TEXT_RELATION": TEXT_RELATION,
            "TEXT_UNIT": unidade,
            "LANGUAGE": None,
            "LANGUAGE_SOURCE": None,
            "MEDIDAS": medidas}


def _seco(caminho):
    """Olha o ficheiro e conta o que daria — sem escrever, sem banco."""
    if not os.path.isfile(caminho):
        return {"FICHEIRO": caminho, "EXISTE": False}
    with open(caminho, "rb") as fh:
        dados = fh.read()
    _, estado, erro, medidas = extrair(dados)
    return {
        "FICHEIRO": os.path.basename(caminho),
        "EXISTE": True,
        "ESTADO": estado,
        "ERRO": erro,
        "MEDIDAS": medidas,
        "TEXT_KIND_QUE_SAIRIA": TEXT_KIND,
        "TEXT_RELATION_QUE_SAIRIA": TEXT_RELATION,
        "KIND_QUE_SAIRIA": KIND,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--ficha" in args or not args:
        print(json.dumps(CAPACIDADE, ensure_ascii=False, indent=1, default=str))
        raise SystemExit(0)
    if "--seco" in args:
        alvo = [a for a in args if a != "--seco"]
        if not alvo:
            print("uso: --seco <ficheiro>")
            raise SystemExit(2)
        print(json.dumps(_seco(alvo[0]), ensure_ascii=False, indent=1,
                         default=str))
        raise SystemExit(0)
    print("uso: --ficha | --seco <ficheiro>")
    raise SystemExit(2)
