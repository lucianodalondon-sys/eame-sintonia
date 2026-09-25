#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A PORTA DE ADMISSAO — a peneira comum, e o livro que guarda cada nao.

O censo mediu o buraco com numero: **um** ficheiro em toda a coleta decide o que
presta (`coleta/youtube_relevancia.py`), para **cinco** veiculos. Nos outros
quatro canais nao ha peneira nenhuma. O caminho de hoje e:

    colher -> carimbar -> guardar TUDO -> inteligencia

e nao:

    colher -> carimbar -> separar -> guardar o que passou -> inteligencia

A tentacao era escrever `instagram_relevancia.py`, `linkedin_relevancia.py`,
`facebook_relevancia.py`. Seriam quatro arquitecturas independentes para um
problema que e um so — e daqui a um ano seriam quatro leis diferentes sobre a
mesma pergunta, cada uma com o seu bug.

AS TRES REGRAS QUE ESTA PORTA NAO QUEBRA
-----------------------------------------

1 · RELEVANCIA NAO E UM BOOLEANO UNIVERSAL.
    O mesmo video pode ser ouro para Ciencia, ruido para Concorrencia e NAO_SEI
    para Regulatorio. Guardar `relevante=true` no item obriga a escolher um
    dono para a verdade, e o segundo universo que perguntar recebe a resposta
    do primeiro. Por isso a decisao e sempre do PAR (item, universo), e o mesmo
    bruto pode ter tres decisoes diferentes ao mesmo tempo, todas certas.

2 · ERRO NAO VIRA NAO.
    «Nao consegui ler o ficheiro» nao e «li e nao serve». Se a ferramenta
    falhou, o estado e ERRO, e o item volta a fila — nao morre com um carimbo
    de rejeitado que ninguem vai reabrir.

3 · AUSENCIA DE PROVA NAO VIRA NAO.
    NAO_SEI e uma resposta legitima e fica escrita como tal. Empurrar o NAO_SEI
    para o NAO faz a coleta encolher sozinha, sem ninguem ter decidido isso — e
    o encolhimento nao aparece em lado nenhum, porque um «nao» parece uma
    decisao tomada.

O LIVRO DE DECISOES
-------------------
`discarded=true` nao serve para nada: nao diz porque, nem por qual regra, nem
com que prova, nem se a regra mudou entretanto. Descarte sem testemunha e
trabalho perdido duas vezes — perde-se o item, e perde-se a informacao de que
aquela fonte entrega lixo. Na coleta seguinte gasta-se maquina para redescobrir
exatamente a mesma coisa.

Cada decisao guarda: o item, o universo, a regra, a versao da regra, o
resultado, o motivo em palavras, a prova, e de que corrida veio. Com a versao
guardada, quando a regra mudar da para reprocessar so o que ela decidiu.

SAIDA: data/samples/LIVRO-DE-DECISOES.json
"""

from __future__ import annotations

import json
import os
import tempfile
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
# O dono do vocabulario das confissoes. Importado, e nao copiado: as seis
# palavras foram CONTADAS no repositorio por quem preserva, e uma segunda copia
# divergiria no dia em que aparecesse a setima.
from preservar_coleta import _identifica  # noqa: E402
# O dono do vocabulario do artefato — cinco tempos, tres geografias, e as duas
# palavras de ausencia. Importado pela mesma razao: uma segunda copia de
# `"NAO SEI"` diverge no dia em que uma delas ganhar um acento.
from leis import artefato as art  # noqa: E402

LIVRO = RAIZ / "data" / "samples" / "LIVRO-DE-DECISOES.json"

# ── OS QUATRO RESULTADOS, E SO ESTES ────────────────────────────────────────
SIM = "SIM"                      # entra
NAO = "NAO"                      # olhei e nao serve para ESTE universo
NAO_SEI = "NAO_SEI"              # nao ha prova suficiente para dizer sim ou nao
NAO_SE_APLICA = "NAO_SE_APLICA"  # a pergunta nao faz sentido para este item
ERRO = "ERRO"                    # nao consegui olhar — NAO e uma rejeicao

RESULTADOS = (SIM, NAO, NAO_SEI, NAO_SE_APLICA, ERRO)

# ⚠️ DUAS PALAVRAS PARECIDAS, E NAO SAO A MESMA COISA.
# `NAO_SEI` (com `_`) e um RESULTADO da porta. `AUSENCIA` (com espaco) e o valor
# que o CONTRATO DE SAIDA escreve quando um campo nao tem prova — e e o unico
# que a Sala de Espera reconhece como «isto e NULL». Trocar um pelo outro faz a
# ausencia deixar de ser ausencia e virar a string `"NAO_SEI"`, que o banco
# guardaria como se fosse um valor medido.
#
#     O DONO DESTA PALAVRA E `leis/artefato.py::NAO_SEI`, e e de la que ela vem.
AUSENCIA = art.NAO_SEI
AUSENCIA_NAO_SE_APLICA = art.NAO_SE_APLICA

# A versao da regra vive aqui e sobe quando a regra muda. E o que permite dizer
# «reprocessa tudo o que a versao 1 rejeitou» sem reprocessar o resto.
# A VERSAO SOBE QUANDO A LEI MUDA, e ela mudou: a versao 1 dava NAO por
# ausencia de palavra. Tudo o que ela rejeitou assim tem de poder ser
# reprocessado — e sem numero de versao nao ha como saber o que reabrir.
# 3 · a porta passou a perguntar pelo ESTAGIO do item (COL-LAW-502). O que
#     mudou de resultado nao foi a evidencia: foi a pergunta. Decisoes
#     antigas ficam como estao — a versao e o que permite dizer «reavalia
#     so o que a v2 decidiu» sem reprocessar o resto.
# 4 · tres mudancas na regua do universo, e as tres APERTAM ou CORRIGEM — a
#     admissao nao se alarga para fazer numero:
#       a) a comparacao passa a dobrar acentos dos DOIS lados. `avversità` e
#          `avversita` deixam de ser palavras diferentes. Isto CORRIGE um falso
#          negativo real, medido no boletim `IT-T3-002`.
#       b) uma palavra solta deixa de promover: sao precisos DOIS termos
#          distintos. O que tem um so cai em `NAO_SEI` — nunca em `NAO`.
#          Isto APERTA, e e o que impede `sintoma` dentro de `sintomatologia`
#          de sozinho admitir um documento.
#       c) T3 ganha a terceira perna que o Atlas sempre lhe deu e que o lexico
#          nao tinha em lingua nenhuma: PLANTAS DANINHAS e resistencia.
#     Quem foi decidido pela v3 fica como esta. A versao e o que permite
#     reabrir exactamente o que (b) possa ter tornado `NAO_SEI`.
# 5 · duas mudancas de regua, e as duas APERTAM:
#       a) `identidade` passou a ser uma pergunta da porta. Um item sem `id` e
#          sem `url` saia com `ITEM_ID = "?"` — uma identidade fabricada, contra
#          a COL-LAW-034 em letra. Agora e `NAO_SEI`, e ele nao passa.
#       b) o campo generico `data` deixou de valer como TEMPO DO FATO. Continua
#          a servir de ancora para admitir; deixou de promover a FACT_TIME.
#     Tudo o que a v4 admitiu com `ITEM_ID = "?"` ou com `FACT_TIME` vindo de
#     `data` tem de poder ser reaberto — e a versao e o que permite dize-lo sem
#     reprocessar o resto.
# 6 · uma pergunta nova no estagio DOCUMENTO, e ela APERTA: `materia` (Q1, D11).
#     Uma pagina HTML que o detector diz ser CAPA passa a `NAO`; uma que ele nao
#     sabe classificar passa a `NAO_SEI` em QUARENTENA. Sem retrato do detector
#     (PDF, video, texto) nada muda. Tudo o que a v5 admitiu de HTML sem esta
#     pergunta pode ser reaberto pela versao.
# 7 · a pergunta `materia` ganha a V1 (V1A, 2026-09-23), e ela APERTA: uma pagina
#     que e o proprio INDEX_URL do contrato de uma fonte que passa os 4 passos e
#     CAPA, diga o detector o que disser (`retrato_html.veredito`). Nas fontes que
#     nao passam os 4 passos nada muda. O que a v6 admitiu ou reteve de HTML pode
#     ser reaberto pela versao.
# 8 · T2 (CLIMATE / WATER / SOIL) ganha regua (T2-REGUA, 2026-09-24). Ate aqui
#     todo o par (item, T2) saia `NAO_SE_APLICA`; agora sai SIM / NAO / NAO_SEI
#     pela regua medida em `scripts/regua_t2/`. Nenhum outro universo muda de
#     veredito (T2 e transversal — ver `TRANSVERSAIS`). O que a v7 deu a T2 pode
#     ser reaberto pela versao.
# 9 · T1 (CROP & PRODUCTION) ganha regua para janelas de cultura (T1-JANELA,
#     2026-09-24): cultura nomeada E dois momentos. Antes todo o par (item, T1) saia
#     `NAO_SE_APLICA`. T1 e transversal: nenhum outro universo muda de veredito
#     (medido em `scripts/regua_t1/`). O que a v8 deu a T1 pode ser reaberto pela versao.
VERSAO_DA_REGRA = "9"


@dataclass
class Decisao:
    item: str
    universo: str
    resultado: str
    regra: str
    motivo: str
    evidencia: dict = field(default_factory=dict)
    versao: str = VERSAO_DA_REGRA
    corrida: str = "NAO SEI"
    quando: str = ""

    def __post_init__(self):
        if self.resultado not in RESULTADOS:
            raise ValueError(f"resultado «{self.resultado}» nao existe. "
                             f"Ha: {', '.join(RESULTADOS)}")
        self.quando = self.quando or datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")


# ── AS PERGUNTAS DA PORTA ───────────────────────────────────────────────────
# Cada uma devolve (resultado, motivo, evidencia). A ordem importa: as que
# apuram se DA PARA OLHAR vem primeiro, porque nao se julga o que nao se leu.
# NAO E UMA COISA COLHIDA — E UM REGISTO SOBRE A COLETA.
#
# Sao duas especies diferentes, e confundi-las escondeu o achado mais duro desta
# missao. Ao ligar a porta pela primeira vez a uma colheita real, 253 registos
# sairam todos barrados na primeira pergunta, e o motivo dizia so «veio sem
# texto». Parecia um defeito da peneira. Nao era.
#
#     `RESEARCHER-CORPUS` guarda 12 PESSOAS com o campo MATERIALS_FOUND = 124.
#     Guarda a CONTAGEM dos materiais. Nao guarda os materiais.
#
# Um registo destes nao e um item mal colhido: e outra especie de coisa — a
# ficha de onde se pode coletar, ou o resumo do que se coletou. Chamar-lhe
# NAO_SEI e dar uma resposta educada a uma pergunta que nao se devia ter feito,
# e por isso ninguem vai investigar.
NAO_E_ITEM = (
    # ficha de conta: onde se pode coletar
    "ACCOUNT_HANDLE", "ACCOUNT_URL", "ACCOUNT_IDENTITY_STATE",
    "COLLECTION_AUTHORIZED", "ELIGIBLE_FOR_COMPANY_LOCAL_BATCH", "ANCHOR_KIND",
    # ficha de pessoa com contagem: o resumo do que se coletou
    "PERSON_ID", "MATERIALS_FOUND", "ORCID_WORKS_DECLARED", "IDENTITY_STATE",
    "PUBLIC_CHANNELS_DECLARED",
)
CHEIRA_A_CATALOGO = NAO_E_ITEM  # nome antigo, mantido para nao partir chamadas


def _legivel(item: dict) -> tuple:
    t = item.get("texto") or item.get("title") or item.get("nome") or ""
    if item.get("erro_de_leitura"):
        return ERRO, ("nao consegui ler este item — a ferramenta falhou. "
                      "Isto nao e uma rejeicao: ninguem chegou a olhar."), \
               {"erro": str(item["erro_de_leitura"])[:200]}
    if not str(t).strip():
        # SEPARAR «VEIO VAZIO» DE «NAO E UM ITEM».
        # A primeira vez que a porta correu sobre uma colheita real, os 78
        # registos sairam todos NAO_SEI — e isso escondia o que importava: nao
        # eram publicacoes mal colhidas, eram FICHAS DE CONTA. A pasta guardava
        # o catalogo de quem se pode coletar, nao o que foi coletado.
        # NAO_SEI ali era uma resposta educada a uma pergunta que nao se devia
        # ter feito, e por isso ninguem ia investigar.
        marcas = [k for k in CHEIRA_A_CATALOGO if k in item]
        if marcas:
            return NAO_SE_APLICA, (
                "isto nao e uma coisa colhida: e uma ficha de conta ou de "
                "catalogo. A pergunta «serve para este universo?» nao se aplica "
                "— o que esta aqui e o registo de ONDE se pode coletar, nao o "
                "que se coletou."), {"campos_de_catalogo": marcas[:4]}
        return NAO_SEI, ("o item veio sem texto nenhum. Sem conteudo nao da para "
                         "dizer se serve — e «nao consegui ver» nao e «nao serve»."), {}
    return SIM, "tem conteudo legivel", {"caracteres": len(str(t))}


# ── O QUE ESTA PORTA CHAMA DE «ORIGEM», E O QUE ELA NAO CHAMA ──────────────
# Esta pergunta e de PROCEDENCIA CONFERIVEL, e nao de identidade canonica. Nao
# e opiniao: le-se no contrato, em tres sitios independentes.
#
#   1. o motivo que ela propria escreve quando falha — «nao se consegue
#      CONFERIR DEPOIS»;
#   2. a companhia em que vive — `perguntas_do_estagio` chama-lhe «Prontidao
#      DOCUMENTAL: da para ler, sabe de onde veio, sabe de que original nasceu»;
#   3. e a prova que fecha o assunto: `pronto_para_inteligencia` monta o
#      `SOURCE_ID` de saida a partir de `source_id` ou `fonte` — e DEIXA `url`
#      DE FORA, de proposito. Se esta porta fosse um portao de identidade, a
#      saida partilharia a cadeia dela. Nao partilha.
#
#     ORIGIN_GATE = PROCEDENCIA.  IDENTITY_GATE = OUTRO, E NAO VIVE AQUI.
#
# Por isso um endereco PODE responder a esta pergunta. O que ele nao pode e
# virar identidade — e nao vira: `SOURCE_ID` nunca sai daqui, e a especie do
# que respondeu fica escrita na evidencia para ninguem confundir as duas.
#
#     UMA URL PROVA UM ENDERECO. UMA URL NAO CRIA SOURCE_ID.
IDENTIDADE_DA_FONTE = ("source_id", "SOURCE_ID", "fonte")
#: O endereco, na grafia do item e na do contrato do coletor (`DO_COLETOR`).
ENDERECO_DA_OBSERVACAO = ("url", "source_url", "SOURCE_URL")


def _declarado(item: dict, campos: tuple):
    """O primeiro campo que IDENTIFICA de verdade. → (valor, campo) ou (None, None).

    «Identifica de verdade» nao e «e truthy». O dono desse vocabulario e
    `guarda/preservar_coleta._identifica`, e e ele que se usa — repetir a lista
    das seis confissoes aqui seria criar um segundo dono da mesma pergunta, e
    dois donos divergem no dia em que alguem acrescentar a setima.
    """
    for c in campos:
        v = item.get(c)
        if _identifica(v):
            return v, c
    return None, None


def _tem_origem(item: dict) -> tuple:
    """Da para conferir depois de onde isto veio? → (resultado, motivo, evidencia).

    A ORDEM E DELIBERADA: identidade primeiro, endereco depois. As duas
    respondem a pergunta, e a primeira responde melhor — mas a segunda so entra
    quando a primeira nao existe, NUNCA por cima dela.

    TRES COISAS QUE ESTA FUNCAO FAZIA E DEIXOU DE FAZER
    ----------------------------------------------------
    Ela era `source_id or fonte or url`, e uma cadeia de `or` mede se o valor e
    truthy — nao se ele responde. Medido nesta casa:

        `source_id = "NAO SEI"` + url  ->  SIM, com evidencia «NAO SEI»
        `source_id = "NAO SEI"` SEM url ->  SIM, com evidencia «NAO SEI»

    O segundo caso e o que mostra o tamanho do buraco: um item sem endereco
    nenhum passava a dizer que a origem estava declarada. Nao havia NADA para
    conferir depois, que e exatamente o que esta pergunta existe para garantir.

        UMA CONFISSAO NAO E UMA ORIGEM. «Nao sei de onde veio» e a resposta
        NAO_SEI a esta pergunta — nao e o valor dela.

    E, no primeiro caso, a confissao AINDA ofuscava o endereco real: o `or`
    parava nela e o URL — que respondia — nunca chegava ao livro de decisoes.

    A terceira: a evidencia dizia so `origem`, sem dizer de que especie. Quem
    lesse o livro nao conseguia distinguir uma identidade de um endereco, e a
    leitura natural de «origem» e a primeira.
    """
    ident, campo = _declarado(item, IDENTIDADE_DA_FONTE)
    if ident:
        return SIM, "a origem esta declarada por identidade de fonte", {
            "origem": str(ident)[:160], "origem_especie": "SOURCE_ID",
            "origem_campo": campo}
    endereco, campo = _declarado(item, ENDERECO_DA_OBSERVACAO)
    if endereco:
        return SIM, ("a origem esta declarada por endereco conferivel. A fonte "
                     "canonica continua por identificar, e isto NAO e "
                     "IDENTITY_STATE."), {
            "origem": str(endereco)[:160], "origem_especie": "SOURCE_URL",
            "origem_campo": campo}
    return NAO_SEI, ("nao da para dizer de onde este item veio. Um item sem "
                     "origem nao se consegue conferir depois, e um numero que "
                     "nao se confere e um palpite bem vestido."), {}


def _tem_quando(item: dict) -> tuple:
    """Tem ALGUMA ancora de tempo? E, se tem, ela e o FATO ou so a PUBLICACAO?

    Esta funcao dizia «tem tempo do fato» para qualquer item que trouxesse
    `published_at`. Quer dizer: a data em que a fonte PUBLICOU entrava no livro
    de decisoes carimbada como a data em que o fato ACONTECEU — calada, sem
    ninguem escolher isso, e contra a lei que `leis/artefato.py` sustenta em
    cinco campos separados:

        FACT_TIME != PUBLISHED_AT != OBSERVED_AT != COLLECTED_AT != DERIVED_AT

    Um boletim publicado a 10 de setembro pode descrever uma armadilha lida a 2.
    Tratar as duas datas como uma faz a inteligencia a jusante ler antecipacao
    onde houve atraso, e o erro nao aparece em lado nenhum porque «tem tempo do
    fato» parece uma resposta boa.

    ⚠️ A DECISAO NAO MUDA, E ISSO E DE PROPOSITO. Uma ancora de publicacao
    continua a servir para admitir — mexer na regua nesta missao seria afrouxar
    a porta enquanto se conserta o transporte, e sao trabalhos diferentes. O que
    muda e a VERDADE ESCRITA AO LADO da decisao: o motivo e a evidencia passam a
    dizer QUAL das duas datas se achou, e `pronto_para_inteligencia()` continua
    a nao deixar `published_at` virar `FACT_TIME` no contrato de saida.

    ⚠️ E O CAMPO GENERICO `data` DEIXOU DE SER `FACT_TIME`, MEDIDO AQUI:

        _tem_quando({"data": "2026-06-30"})
        antes ->  ('SIM', 'tem tempo do fato', {'que_tempo': 'FACT_TIME'})

    `data` nao declara DE QUE TEMPO E. Um coletor que la ponha a data do
    documento — e e o que um coletor poe, porque e a data que ele tem — produzia
    um `FACT_TIME` falso, carimbado como fato, sem ninguem escolher isso. E o
    mesmo defeito de `published_at`, so que sem nome:

        UM CAMPO QUE NAO DIZ DE QUE ESPECIE E NAO PODE PROMOVER A ESPECIE NENHUMA.
        COL-LAW-031: «nao por conveniencia, nao por omissao, NAO POR FALLBACK.»

    Ele continua a servir de ANCORA para admitir — nao se aperta a porta aqui —
    e continua escrito na evidencia, com o nome que merece: `TIME_UNDECLARED`.
    """
    fato = item.get("fact_time")
    if fato:
        return SIM, "tem tempo do fato", {"quando": str(fato)[:40],
                                          "que_tempo": "FACT_TIME",
                                          "fact_time_basis": str(
                                              item.get("fact_time_basis")
                                              or "declarado pelo produtor do item")[:200]}
    pub = item.get("published_at")
    if pub:
        return SIM, ("tem ancora de tempo, mas e a data de PUBLICACAO — nao a do "
                     "fato. O tempo do fato continua NAO SEI, e segue NAO SEI "
                     "adiante."), {"quando": str(pub)[:40],
                                   "que_tempo": "PUBLICATION_TIME",
                                   "fact_time": "NAO SEI"}
    generica = item.get("data")
    if generica:
        return SIM, ("tem ancora de tempo, mas o campo `data` nao diz de que "
                     "tempo e. NAO se promove a FACT_TIME sem contrato que o "
                     "declare (COL-LAW-031). O tempo do fato continua NAO SEI."), \
               {"quando": str(generica)[:40], "que_tempo": "TIME_UNDECLARED",
                "campo": "data", "fact_time": "NAO SEI"}
    # ⚠️ D62 (dono, 25/09): «NUNCA reprovar/descartar um fato por lhe faltar
    # dado (data, local…)». Ate aqui isto devolvia NAO_SEI, e um FATO sem data
    # nenhuma NAO entrava na Sala. Agora a ausencia REGISTA-SE — na evidencia e,
    # a jusante, em `FACT_TIME = NAO SEI` — e a porta segue para as outras
    # perguntas. A precisao do item e da Intelligence, nao desta porta.
    #
    #     FALTA DE DATA E PRECISAO BAIXA, NAO E MOTIVO DE RECUSA.
    return SIM, ("o item nao diz quando o fato aconteceu nem quando foi "
                 "publicado: os dois ficam NAO SEI. Falta de data NAO barra "
                 "(D62) — regista-se."), {"que_tempo": "NENHUM",
                                          "fact_time": "NAO SEI",
                                          "published_at": "NAO SEI"}


def _tem_pai(item: dict) -> tuple:
    """A pergunta de prontidao DOCUMENTAL que faltava: de onde este texto nasceu?

    Um derivado sem pai nao se consegue conferir contra o original — e um texto
    que ninguem consegue ligar ao PDF de onde saiu e indistinguivel de um texto
    que alguem escreveu a mao.
    """
    pai = item.get("parent_artifact_id") or item.get("parent_sha256")
    if item.get("artifact_type") == "RAW":
        return SIM, "e o original: nao tem pai, e nao devia ter", {}
    if not pai or str(pai) in (NAO_SEI, "NAO_SE_APLICA", ""):
        return NAO_SEI, ("este documento nao diz de que original nasceu. Sem pai "
                         "nao da para conferir contra o bruto."), {}
    return SIM, "o pai esta declarado", {"pai": str(pai)[:60]}


def _identidade_do_item(item: dict):
    """O endereco deste item, ou `None`. NUNCA um simbolo a fingir de endereco."""
    for campo in ("id", "url"):
        v = item.get(campo)
        if v is not None and str(v).strip() and str(v).strip() not in (
                AUSENCIA, NAO_SEI, AUSENCIA_NAO_SE_APLICA, "?"):
            return str(v)
    return None


def _tem_identidade(item: dict) -> tuple:
    """Este item tem endereco proprio? Sem ele nao se consegue ir buscar depois.

    ⚠️ AQUI MORAVA UM `"?"`, E ELE ERA UMA IDENTIDADE FABRICADA.

        Decisao(item=str(item.get("id") or item.get("url") or "?"), ...)

    Medido nesta arvore: um item com `source_id`, sem `id` e sem `url` passava a
    porta e chegava a Sala de Espera com `ITEM_ID = '?'`. A `COL-LAW-034` diz o
    contrario em letra: *«`"?"` e a string vazia NAO DEVEM ser usados como
    identidade.»* E a Sala ja tinha a cicatriz escrita — `ItemAmbiguo` existe
    porque dois `"?"` na mesma corrida sao duas coisas com a mesma morada, e
    retirar «o item ?» seria retirar um dos dois a sorte.

        UM SIMBOLO QUE SIGNIFICA «NAO SEI» POSTO NO SITIO DA IDENTIDADE
        NAO E UM AVISO: E UMA CHAVE DUPLICADA COM AR DE CHAVE.

    A resposta certa nao e inventar um id — nem do sha256, nem da URL, nem do
    `source_id`, que e da FONTE e nao do ITEM. E dizer NAO_SEI e parar: falta a
    prova, nao o valor. Isto APERTA a porta, e de proposito. A rota canonica
    (`rota_forward_documento.item_para_a_porta`) poe sempre `id=CONTENT_ID`, e
    por isso nao e afectada.
    """
    if _identidade_do_item(item) is not None:
        return SIM, "o item tem endereco proprio", {}
    return NAO_SEI, (
        "este item nao traz `id` nem `url`: nao tem endereco proprio. Sem "
        "endereco ele nao se consegue ir buscar depois, e dois assim na mesma "
        "corrida ficariam com a mesma morada. `source_id` NAO serve — e da "
        "FONTE, nao do item (COL-LAW-034)."), {"identidade": "NAO SEI"}


# ── AS DUAS PRONTIDOES, E O ESTAGIO QUE AS SEPARA ───────────────────────────
# COL-LAW-502: DOCUMENTO PRONTO nao e FATO PRONTO. Sao duas perguntas, em dois
# momentos, e mede-las com a mesma regua faz o documento reprovar por nao saber
# uma coisa que so o fato sabe.
#
#     43 textos derivados sairam NAO_SEI porque a porta lhes perguntava «quando
#     o fato aconteceu». Um boletim nao acontece: ele RELATA. A data e do fato
#     que esta dentro dele, e esse fato ainda nao foi extraido.
#
# NAO SE CRIOU SEGUNDA PORTA. E a mesma, e ela passou a perguntar o que se
# aplica ao estagio do item — que e o que a lei manda.
DOCUMENTO, FATO, ESTAGIO_DESCONHECIDO = "DOCUMENTO", "FATO", "ESTAGIO_DESCONHECIDO"

# Marcas que dizem «isto e um fato/claim, nao um documento». Um claim tem
# sujeito e predicado; um documento tem bytes e pai.
MARCAS_DE_FATO = ("claim_id", "subject", "predicate", "fact_id")


def estagio(item: dict) -> str:
    """Que especie de coisa e esta? A resposta decide as perguntas."""
    if any(k in item for k in MARCAS_DE_FATO):
        return FATO
    if str(item.get("artifact_type") or "").upper() in ("RAW", "DERIVED"):
        return DOCUMENTO
    # NAO SE ADIVINHA. Quem nao se declara continua a ser medido pela regua
    # antiga — mudar o resultado de quem nao pediu seria alterar decisoes de
    # caminhos que esta missao nao mediu.
    return ESTAGIO_DESCONHECIDO


# ── A QUARENTENA DO «NAO SEI» DO DETECTOR (D11, opcao C, 2026-09-23) ────────
# O detector «materia vs pagina de entrada» (`curadoria/retrato_html.py`, dono
# LD3) so corria ao nivel da FONTE — no canario e na prova da listagem. Nenhuma
# pagina colhida passava por ele a caminho da Sala: medido nos dois gabaritos,
# 63/109 e 28/49 capas entrariam caladas.
#
# A D11 decidiu: quando o detector diz NAO SEI, a pagina NAO entra na Sala e fica
# em QUARENTENA registada. O estado JA EXISTIA — e este: `NAO_SEI` desta porta
# («nao ha prova suficiente para dizer sim ou nao») e exactamente o NAO SEI do
# detector. Classe antes do rotulo: nao se cria um segundo registo nem um estado
# novo. A pagina fica no LIVRO desta porta, com o retrato e a proveniencia; o
# bruto fica intacto no armazem; e o replay (`orquestrador --so-a-porta`,
# COL-LAW-027) volta a julga-la quando a regra mudar.
#
#     UNKNOWN NAO E NEVER. QUARENTENA NAO E DESCARTE.
#
# SO DUAS SAIDAS:
#   a) REGRA PROVADA — o detector (dono LD3), mudado e provado nos 2 gabaritos,
#      e re-corrido no replay e da MATERIA ou CAPA. A porta nao mede a prova do
#      detector: le o veredito que ele entrega.
#   b) DECISAO HUMANA REGISTADA — uma linha em `QUARENTENA_HUMANA` para o sha256
#      da pagina (MATERIA ou CAPA, com QUEM e PORQUE). Ler e opcional; registar
#      a leitura e obrigatorio para ela contar.
# Ao sair, a pagina passa pelas perguntas seguintes desta porta, como qualquer outra.
#
# A politica NAO se copia: e `curadoria/politica_nao_sei.py` (preparada na LD3,
# ACTIVA = QUARENTENA pela D11). Sem retrato — PDF, video, texto — a pergunta
# nao se aplica: a porta nao aperta para quem o detector nao sabe ler.
QUARENTENA_HUMANA = RAIZ / "data" / "samples" / "QUARENTENA-DECISOES-HUMANAS.jsonl"
QUARENTENA = "QUARENTENA"


def _politica_nao_sei():
    import importlib.util  # noqa: PLC0415
    f = RAIZ / "curadoria" / "politica_nao_sei.py"
    spec = importlib.util.spec_from_file_location("politica_nao_sei", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ── D14 (bot Luciano, delegado do dono, 23/09): OPCAO C — DESLIGADA ─────────
# CAPA de fonte cujo contrato passa a regua dos 4 passos (INDEX_URL provado) vai
# para QUARENTENA em vez de ser barrada. A D14 manda: desligada ate medir, e so
# ligar se as condicoes baterem. MEDIDO (D1, 2026-09-23, livros do portao das
# 08:25Z): das noticias barradas como capa, a C recupera 0/6 (original) e 0/4
# (controlo) — todas vem de fontes MAL configuradas —, e poria 3 capas
# verdadeiras em quarentena. «Se a C recuperar quase nada: volta ao dono».
# Fica DESLIGADA; ligar e mudar esta linha, com a medicao nova ao lado.
D14_C_LIGADA = False


def _da_curadoria(nome: str):
    """Um modulo do dono em curadoria/, carregado UMA vez (sys.modules): a
    V1A pergunta por pagina, e reexecutar o modulo a cada pagina relia o
    livro do lifecycle do zero."""
    m = sys.modules.get(nome)
    if m is not None:
        return m
    import importlib.util  # noqa: PLC0415
    if str(RAIZ / "curadoria") not in sys.path:
        sys.path.insert(0, str(RAIZ / "curadoria"))
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "curadoria" / (nome + ".py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def _fonte_bem_configurada(source_id) -> bool:
    """A fonte passa a regua dos 4 passos (DETAIL/v1)? Le o dono, sem copia."""
    try:
        return _da_curadoria("ready_split").regua_manda(source_id)
    except Exception:                                            # noqa: BLE001
        return False


def _contrato_da_fonte(source_id) -> dict | None:
    """O contrato que a regua le — a V1 compara a pagina com o INDEX_URL dele."""
    try:
        return _da_curadoria("ready_split").contrato_de(source_id)
    except Exception:                                            # noqa: BLE001
        return None


# ── V1A (2026-09-23): O INDEX_URL DO CONTRATO E CAPA, SO COM A REGUA A MANDAR ──
# A regra vive no detector (`curadoria/retrato_html.py::veredito`, gemeo Node em
# `coleta/retrato_html.mjs`); esta porta so lhe da o que ela precisa: o endereco
# da pagina (`url_da_pagina`, transportado desde `raw_asset.source_url`), o
# contrato da fonte e se a fonte passa os 4 passos. Sem endereco, a V1 nao se
# aplica e fica o detector — nao se adivinha se a pagina era o indice.


def _decisoes_humanas() -> dict:
    """{sha256 da pagina: ultima linha humana}. Append-only; a ultima manda."""
    out = {}
    if QUARENTENA_HUMANA.exists():
        for l in QUARENTENA_HUMANA.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                if d.get("SHA256") and d.get("VEREDITO") in ("MATERIA", "CAPA"):
                    out[d["SHA256"]] = d
    return out


def _e_materia(item: dict) -> tuple:
    """A pagina e materia, ou e uma pagina de entrada? → (resultado, motivo, evidencia)."""
    retrato = item.get("retrato_do_detector")
    if not retrato:
        return SIM, "sem retrato do detector (nao e HTML): a pergunta nao se aplica", \
               {"retrato": None}
    sha = item.get("parent_sha256") or item.get("PARENT_SHA256")
    ev = {"retrato": {k: retrato.get(k) for k in ("CAPA_OU_MATERIA", "HTML_KIND", "LINKS",
                                                  "NON_WHITESPACE_CHARACTERS", "PARAGRAPH_CHARACTERS")},
          "pagina_sha256": sha}
    humano = _decisoes_humanas().get(sha) if sha else None
    if humano:
        ev["decisao_humana"] = {k: humano.get(k) for k in ("VEREDITO", "QUEM", "QUANDO", "PORQUE")}
        if humano["VEREDITO"] == "MATERIA":
            return SIM, "uma pessoa leu e registou: e materia (saida humana da quarentena)", ev
        return NAO, "uma pessoa leu e registou: e pagina de entrada, nao materia", ev
    fonte = item.get("source_id") or item.get("SOURCE_ID")
    url = item.get("url_da_pagina")
    regua = _fonte_bem_configurada(fonte)
    rh = _da_curadoria("retrato_html")
    # Uma so trava: `regua_a_mandar`. O contrato vai sempre (o veredito e que o ignora
    # sem a regua) — duas travas para a mesma coisa escondiam-se uma a outra no ataque.
    k = rh.veredito(retrato, url=url, contrato=_contrato_da_fonte(fonte),
                    regua_a_mandar=regua)
    ev["url_da_pagina"] = url
    ev["regua_a_mandar"] = regua
    julgado = retrato
    if k != retrato.get("CAPA_OU_MATERIA"):
        ev["v1"] = {"REGRA": rh.REGRA_V1, "DETECTOR": retrato.get("CAPA_OU_MATERIA"), "VEREDITO": k}
        julgado = dict(retrato, CAPA_OU_MATERIA=k)
    pns = _politica_nao_sei()
    d = pns.decidir(julgado, pns.QUARENTENA)
    ev["politica"] = "QUARENTENA (D11)"
    if d["ACCAO"] == "ENTRA":
        return SIM, "o detector diz materia", ev
    if d["ACCAO"] == "REPROVA":
        # A capa barrada fica no livro com o que e preciso para voltar a porta:
        # a fonte e a observacao-pai (os bytes vivem no armazem pelo raw_asset).
        ev["fonte"] = fonte
        ev["raw_asset_id"] = item.get("raw_asset_id")
        if ev.get("v1"):
            return NAO, ("V1: a pagina e o proprio INDEX_URL do contrato, e a fonte passa os 4 "
                         "passos — e capa, nao materia; fica no livro e volta no replay"), ev
        if D14_C_LIGADA and _fonte_bem_configurada(ev["fonte"]):
            ev["estado"] = QUARENTENA
            ev["d14"] = "CAPA de fonte cujo contrato passa os 4 passos: QUARENTENA, nao barrada"
            return NAO_SEI, ("QUARENTENA (D14 opcao C): o detector diz capa, mas a fonte tem o "
                             "INDEX_URL provado pelos 4 passos — pode ser noticia mal lida. Sai "
                             "pela D11: regra provada ou decisao humana"), ev
        return NAO, ("o detector diz pagina de entrada (capa), nao materia — CAPA != MATERIA; "
                     "fica no livro e volta a ser julgada no replay"), ev
    ev["estado"] = QUARENTENA
    return NAO_SEI, ("QUARENTENA (D11): o detector nao sabe se isto e materia ou pagina de "
                     "entrada. Nao entra na Sala; nada se apaga; sai so por regra provada "
                     "(replay) ou por decisao humana registada"), ev


# ── O CUSTO DA QUARENTENA, VIGIADO (D11, ponto 3) ───────────────────────────
# Uma quarentena que so cresce e um descarte com outro nome. Os limites:
#
# QUARENTENA_JANELA_DIAS = 14
#   WHY: duas semanas cobrem duas revalidacoes semanais das fontes (B3) e mais do
#   que um ciclo de mudanca de regra do detector (LD1->LD3 levou 2 dias). Se em 14
#   dias nada saiu e ha paginas com mais de 14 dias la dentro, a quarentena
#   deixou de ser espera e virou deposito.
# QUARENTENA_TAMANHO_MAXIMO = 300
#   WHY: no ensaio dos dois gabaritos, 34/146 e 19/69 paginas HTML ficam em
#   quarentena (~25%). O lote-76 trouxe 76 documentos; 300 sao ~15 corridas
#   desse tamanho so de quarentena — acima disso a leitura humana ja nao chega.
# Qualquer dos dois dispara ALARME, e o alarme volta ao dono (nao decide nada).
QUARENTENA_JANELA_DIAS = 14
QUARENTENA_TAMANHO_MAXIMO = 300


def painel_da_quarentena(livro: dict | None = None, agora: datetime | None = None) -> dict:
    """Tamanho, idade e saidas da quarentena, lidos do LIVRO desta porta. So le."""
    if livro is None:
        livro = json.loads(LIVRO.read_text(encoding="utf-8")) if LIVRO.exists() else {"DECISOES": []}
    agora = agora or datetime.now(timezone.utc)

    def _t(s):
        try:
            return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        except ValueError:
            return None

    ultima, entrou, saiu = {}, {}, {}
    for d in livro.get("DECISOES", []):
        chave = (d.get("item"), d.get("universo"))
        q = ((d.get("evidencia") or {}).get("estado") == QUARENTENA
             and d.get("resultado") == NAO_SEI and d.get("regra") == "materia")
        if q:
            entrou.setdefault(chave, _t(d.get("quando")))
        elif chave in entrou:
            # saiu: a idade de uma reentrada conta de novo a partir dela
            saiu[chave] = _t(d.get("quando"))
            entrou.pop(chave)
        ultima[chave] = q
    dentro = [k for k, q in ultima.items() if q]
    idades = [(agora - entrou[k]).total_seconds() / 86400 for k in dentro if entrou.get(k)]
    janela = QUARENTENA_JANELA_DIAS * 86400
    saidas = [t for t in saiu.values() if t and (agora - t).total_seconds() <= janela]
    mais_antiga = round(max(idades), 1) if idades else 0
    alarmes = []
    if len(dentro) > QUARENTENA_TAMANHO_MAXIMO:
        alarmes.append("TAMANHO: %d paginas > %d" % (len(dentro), QUARENTENA_TAMANHO_MAXIMO))
    if dentro and mais_antiga > QUARENTENA_JANELA_DIAS and not saidas:
        alarmes.append("SEM_SAIDAS: a mais antiga tem %.1f dias e nada saiu em %d dias"
                       % (mais_antiga, QUARENTENA_JANELA_DIAS))
    # D14 (4): barradas vs retidas, separando fontes bem e mal configuradas.
    # Conta-se a ULTIMA decisao `materia` de cada pagina; a regua le-se uma vez por fonte.
    ult_materia = {}
    for d in livro.get("DECISOES", []):
        if d.get("regra") == "materia":
            ult_materia[(d.get("item"), d.get("universo"))] = d
    cache, d14 = {}, {}
    for d in ult_materia.values():
        fonte = (d.get("evidencia") or {}).get("fonte")
        if fonte not in cache:
            cache[fonte] = _fonte_bem_configurada(fonte)
        destino = "RETIDAS" if (d.get("evidencia") or {}).get("estado") == QUARENTENA else "BARRADAS"
        chave = "%s_FONTE_%s" % (destino, "BEM" if cache[fonte] else "MAL")
        d14[chave] = d14.get(chave, 0) + 1
    return {"TAMANHO": len(dentro), "MAIS_ANTIGA_DIAS": mais_antiga,
            "D14_BARRADAS_VS_RETIDAS": d14, "D14_C_LIGADA": D14_C_LIGADA,
            "SAIDAS_NA_JANELA": len(saidas), "JANELA_DIAS": QUARENTENA_JANELA_DIAS,
            "TAMANHO_MAXIMO": QUARENTENA_TAMANHO_MAXIMO,
            "ALARME": bool(alarmes), "PORQUE": alarmes,
            "ACCAO_SE_ALARME": "volta ao dono (D11): a quarentena cresce sem nada sair"}


def perguntas_do_estagio(est: str) -> tuple:
    """As perguntas aplicaveis, por estagio. Uma arquitetura, duas reguas."""
    if est == DOCUMENTO:
        # Prontidao DOCUMENTAL: da para ler, sabe de onde veio, sabe de que
        # original nasceu. O tempo do FATO nao se pergunta aqui.
        # `materia` vem depois de `identidade`: uma pagina em quarentena tem de
        # ter morada no livro, senao nao se consegue voltar a ela.
        return (("legivel", _legivel), ("origem", _tem_origem),
                ("linhagem", _tem_pai), ("identidade", _tem_identidade),
                ("materia", _e_materia))
    # FATO e ESTAGIO_DESCONHECIDO continuam a responder pelo tempo do fato.
    #
    # ⚠️ `identidade` e a ULTIMA das prontidoes, e nao a primeira, de proposito:
    # as outras perguntam sobre o ITEM, e esta pergunta sobre a MORADA que ele
    # vai ter na Sala. Pondo-a a frente, um item ilegivel passaria a ser
    # recusado por «identidade» e a razao verdadeira — «veio sem texto» —
    # deixaria de aparecer no livro.
    return (("legivel", _legivel), ("origem", _tem_origem),
            ("tempo do fato", _tem_quando), ("identidade", _tem_identidade))


# ── A PORTA LE O QUE ESTA ESCRITO, E O ITALIANO ESCREVE-SE COM ACENTO ──────
# Medido contra o boletim real `IT-T3-002` (Campania, fitossanitario): o texto
# diz `avversità` e o vocabulario dizia `avversita`. `"avversita" in texto` e
# False, e a palavra estava la, a vista, na lingua certa.
#
#     `avversità` E `avversita` SAO A MESMA PALAVRA.
#     UMA PENEIRA QUE AS SEPARA NAO ESTA A JULGAR: ESTA A TROPECAR NA ORTOGRAFIA.
#
# Isto NAO e traduzir nem alargar o lexico: e comparar as duas coisas na mesma
# forma. A dobra aplica-se aos DOIS lados — ao texto e ao termo — para que
# nenhum dos dois ganhe vantagem sobre o outro.
#
# ⚠️ E ELA NAO NORMALIZA SIGNIFICADO. `città` e `citta` passam a casar, e e o
# que se quer; `cita` continua a ser outra palavra, porque a dobra tira o
# acento e nao a letra.
def _dobrar(texto: str) -> str:
    """Minusculas e sem acento. A mesma forma dos dois lados da comparacao."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto).lower())
                   if not unicodedata.combining(c))


#: Quantos termos DISTINTOS o texto tem de trazer para a porta promover.
#: Um so fica `NAO_SEI` — ver `_do_universo`.
SINAIS_MINIMOS = 2

# ── T2: POR CONCEITO, PALAVRA INTEIRA, E TRANSVERSAL (T2-REGUA, 2026-09-24) ──
# O mesmo desenho da regua T8 (YT2, branch `youtube-regua-t8-v1`), com os
# mesmos nomes, para as duas se juntarem sem conflito de ideia: quando T8
# entrar, os conjuntos passam a {"T2", "T8"}.
#
# 1 · UM TERMO DE T2 E UM CONCEITO, e as formas dele vao separadas por «|»
#     («pioggia|piogge|precipitazione|...»). Conta UMA vez: chuva no singular e
#     no plural e o mesmo indicio, e SINAIS_MINIMOS exige dois indicios
#     independentes.
# 2 · PALAVRA INTEIRA, SO NOS UNIVERSOS DESTE CONJUNTO. Medido no gabarito:
#     `temporale` (trovoada) e tambem «serie TEMPORALI» (series temporais) numa
#     carta de servicos de laboratorio; `seca` vive dentro de «biblioteca». As
#     reguas antigas ficam como estao — muda-las e outra missao, com outra
#     medicao.
# 3 · T2 E TRANSVERSAL. O tempo que faz esta em quase tudo o que e agricola: o
#     boletim fitossanitario diz que «as chuvas da semana passada aumentaram os
#     voos da mosca», a noticia de mercado diz que «a seca subiu o preco». Isso
#     nao prova que o boletim NAO e T3 nem que a noticia NAO e T10. Por isso um
#     termo de T2 NUNCA serve de «prova de outro universo» para dizer NAO a
#     outro universo — e as decisoes antigas nao mudam por T2 existir
#     (medido: 0 vereditos vizinhos mudados, `MEDICAO-REGUA-T2-V1.json`).
#
#     FALAR DO TEMPO NAO E MUDAR DE ASSUNTO.
PALAVRA_INTEIRA = frozenset({"T2", "T1"})
TRANSVERSAIS = frozenset({"T2", "T1"})


def _casa(termo: str, texto_dobrado: str) -> bool:
    """Uma das formas do conceito (separadas por «|») esta no texto como PALAVRA INTEIRA?"""
    import re
    for forma in str(termo).split("|"):
        f = _dobrar(forma)
        if f and re.search(r"(?<![a-z0-9])" + re.escape(f) + r"(?![a-z0-9])", texto_dobrado):
            return True
    return False


def _do_universo(item: dict, universo: str, palavras: list) -> tuple:
    """Pertence ao universo pedido? A resposta muda com o universo — de proposito.

    A LEI CANONICA QUE ESTA FUNCAO VIOLAVA
    ---------------------------------------
        AUSENCIA DE EVIDENCIA NAO E EVIDENCIA DE AUSENCIA.

    Ela devolvia NAO sempre que nenhuma palavra casava. Isso parece razoavel e
    nao e: «nao encontrei nada deste universo» pode querer dizer duas coisas
    completamente diferentes —

        o item nao e disto                     ... e uma conclusao
        o meu vocabulario nao chega a este item ... e uma confissao

    e a porta nao tinha como as distinguir. Com um vocabulario incompleto — e o
    desta casa esta comprovadamente incompleto — o NAO por ausencia transforma
    cada buraco do lexico numa rejeicao com ar de julgamento. A coleta encolhe
    sozinha e ninguem ve, porque um «nao» parece uma decisao tomada.

    AGORA SO HA NAO COM EVIDENCIA POSITIVA:
    quando o item fala claramente de OUTRO universo e nao deste. Isso e uma
    prova a favor da exclusao, nao a falta de uma prova a favor da inclusao.

    Sem essa prova, a resposta e NAO_SEI — que e mais util do que um nao errado,
    porque um NAO_SEI faz alguem ir ver, e um NAO fecha o assunto.
    """
    if not palavras:
        if not str(universo or '').strip():
            # ⚠️ AUSENCIA DE UNIVERSO != UNIVERSO SEM REGRA. Sao duas faltas
            # diferentes, e chamar-lhes o mesmo nome escondia a pior: um item
            # julgado contra um universo que ninguem declarou recebia a resposta
            # «nao ha regra escrita do que conta como «None»» — que se le como
            # um buraco do lexico, e nao como um PEDIDO incompleto.
            #
            #     O UNIVERSO VEM DO PEDIDO. SEM PEDIDO NAO HA PERGUNTA.
            return NAO_SE_APLICA, (
                "UNIVERSO_NAO_DECLARADO: esta porta julga um par (item, "
                "universo), e o universo vem do PEDIDO — nunca da fonte, do "
                "territorio dela, da plataforma nem do conteudo. Sem universo "
                "declarado nao ha pergunta: esta porta nao escolhe uma."), {}
        return NAO_SE_APLICA, (f"nao ha regra escrita do que conta como «{universo}». "
                               f"Sem regra, esta porta nao inventa uma."), {}
    texto = _dobrar(" ".join(str(item.get(k) or "") for k in
                             ("texto", "title", "nome", "topics", "crops", "resumo")))
    # D3: a mesma regua, na lingua do texto. it/pt/NAO SEI: nada muda.
    lingua = _lingua_do_item(item)
    reguas = PERGUNTAS_DO_UNIVERSO
    if lingua in IDIOMAS_SEM_REGUA:
        return NAO_SEI, (f"IDIOMA_NAO_SUPORTADO:{lingua} — o texto esta em «{lingua}» e esta "
                         f"porta nao tem regua nessa lingua. NAO_SEI dito, nao fingido."), \
            {"idioma": lingua}
    if lingua == "en":
        reguas = PERGUNTAS_EN
        palavras = PERGUNTAS_EN.get(universo, [])
    if universo in PALAVRA_INTEIRA:
        achadas = [p.split("|")[0] for p in palavras if _casa(p, texto)]
    else:
        achadas = [p for p in palavras if _dobrar(p) in texto]
    if universo in CULTURA_OBRIGATORIA:
        # T1-JANELA (24/09): cultura nomeada E dois momentos distintos (fase, estadio,
        # colheita/sementeira, tratamento, limiar...). Ver CULTURA_OBRIGATORIA.
        cult = (CULTURA_OBRIGATORIA_EN if lingua == "en" else CULTURA_OBRIGATORIA)[universo]
        tem_cultura = _casa(cult, texto)
        if tem_cultura and len(achadas) >= SINAIS_MINIMOS and not _momento_de_passagem(
                texto, (PERGUNTAS_EN if lingua == "en" else PERGUNTAS_DO_UNIVERSO)[universo]):
            return SIM, (f"nomeia uma cultura e fala de {', '.join(achadas[:3])} — fase ou momento "
                         f"de operacao, que e o que «{universo}» (janela de cultura, D29) pede. A "
                         f"janela em si nao e decidida aqui: e da Intelligence (CAP-WIN)"), \
                {"palavras": achadas[:8], "cultura": True, "sinais": len(achadas)}
        if achadas or tem_cultura:
            falta = ("SEM_CULTURA_NOMEADA" if not tem_cultura else
                     "SEM_MOMENTO" if not achadas else
                     "UM_SO_MOMENTO" if len(achadas) < SINAIS_MINIMOS else
                     "MOMENTO_SO_DE_PASSAGEM")
            return NAO_SEI, (
                f"{falta}: «{universo}» (D29) pede uma cultura nomeada E dois sinais de momento "
                f"(fase, colheita, sementeira, tratamento). Com menos, fica NAO_SEI — nao entra e "
                f"nao e rejeitado."), {"palavras": achadas, "cultura": tem_cultura, "falta": falta}
    if universo in ANCORAS:
        anc = (ANCORAS_EN if lingua == "en" else ANCORAS)[universo]
        fortes = [p.split("|")[0] for p in anc["FORTES"] if _casa(p, texto)]
        agro = _casa(anc["AGROMETEO"], texto)
        via_agro = agro and len(achadas) >= SINAIS_MINIMOS and _corpo_de_boletim(texto, anc)
        if (achadas and fortes) or via_agro:
            ancoras = fortes + (["agrometeo"] if agro else [])
            return SIM, (f"fala de {', '.join(achadas[:3])} e de {', '.join(ancoras[:3])} — "
                         f"condicao do campo com ligacao agricola escrita, que e o que "
                         f"«{universo}» (janela de cultura, D29) pede. A janela em si nao e "
                         f"decidida aqui: e da Intelligence (CAP-WIN)"),                 {"palavras": achadas[:8], "ancoras": ancoras[:8],
                 "sinais": len(achadas) + len(ancoras)}
        ancoras = fortes + (["agrometeo"] if agro else [])
        if achadas or ancoras:
            falta = "SEM_LIGACAO_AGRICOLA" if not ancoras else "SEM_CONDICAO_DO_CAMPO"
            return NAO_SEI, (
                f"{falta}: ha {', '.join((achadas or ancoras)[:3])}, mas «{universo}» (D29) "
                f"pede as duas coisas juntas — a condicao (tempo, agua, solo) E a ligacao "
                f"agricola escrita (fenologia, defesa, monitorizacao). "
                + ("Tempo sem cultura pode ser de outra pergunta (D2: REROUTE); "
                   if not ancoras else "")
                + "Com metade, fica NAO_SEI — nao entra e nao e rejeitado."),                 {"palavras": achadas, "ancoras": ancoras, "falta": falta,
                 "d2": "REROUTE_POSSIVEL" if not ancoras else None}
    # ── UMA PALAVRA SOLTA NAO PROMOVE ───────────────────────────────────────
    # Medido: `sintoma` (pt) casa dentro de `sintomatologia` (it), `prova` casa
    # dentro de `approvazione`. Uma unica palavra pode ser um acidente de
    # substring, uma citacao de passagem ou um cabecalho — e promover por ela
    # deixa entrar material que ninguem leu.
    #
    #     UMA PALAVRA E UM INDICIO. DOIS INDICIOS INDEPENDENTES SAO UM SINAL.
    #
    # ⚠️ E O QUE FALTA NAO VIRA `NAO`. Um indicio so nao prova pertenca, e
    # tambem nao prova o contrario: fica `NAO_SEI`, que e o que ele e, e que
    # manda alguem ir ver. Transformar «pouca prova» em «nao» seria exactamente
    # a lei que esta funcao existe para nao quebrar.
    if len(achadas) >= SINAIS_MINIMOS:
        return SIM, (f"fala de {', '.join(achadas[:4])} — que e do que «{universo}» "
                     f"trata"), {"palavras": achadas[:8], "sinais": len(achadas)}
    if achadas:
        return NAO_SEI, (
            f"so uma palavra de «{universo}» aparece ({achadas[0]}), e uma "
            f"palavra solta pode ser acidente de substring, citacao de passagem "
            f"ou cabecalho. E indicio, nao sinal — e indicio nao promove nem "
            f"rejeita."), {"palavras": achadas, "sinais": len(achadas),
                           "sinais_minimos": SINAIS_MINIMOS}

    # nada deste universo. Fala de outro? Isso e prova POSITIVA de exclusao.
    noutros = {}
    for outro, termos in reguas.items():
        if outro == universo or outro in TRANSVERSAIS:
            continue
        # um universo por conceito («forma|forma») so casa pelas suas formas, e por
        # palavra inteira; os antigos continuam como estavam.
        casou = [t.split("|")[0] for t in termos
                 if (_casa(t, texto) if outro in PALAVRA_INTEIRA else t.lower() in texto)]
        if casou:
            noutros[outro] = casou[:4]
    if noutros:
        quais = "; ".join(f"{u}: {', '.join(w)}" for u, w in noutros.items())
        return NAO, (f"nao fala de «{universo}», e fala claramente de outro "
                     f"universo ({quais}). Isto e um NAO com prova a favor — nao "
                     f"a simples falta de uma palavra."), {"achado_noutro": noutros}

    return NAO_SEI, (f"nao encontrei nada de «{universo}» — nem de nenhum outro "
                     f"universo. Isso NAO prova que o item nao pertence: prova que "
                     f"o vocabulario nao lhe chegou. Ausencia de evidencia nao e "
                     f"evidencia de ausencia, e por isso fica NAO_SEI."), {}


# ── A PORTA TEM DE FALAR A LINGUA DO ITEM ──────────────────────────────────
# Esta lista nasceu em PORTUGUES, e a porta decide sobre item ITALIANO. Medido
# contra o unico texto italiano real desta arvore: **1 de 28** palavras aparecia
# la. E das 28, **20 mudam** em italiano — `pesquisa` e `ricerca`, `artigo` e
# `articolo`, `rotulo` e `etichetta`, `doenca` e `malattia`.
#
#     A BUSCA FOI CORRIGIDA E A PORTA FICOU PARA TRAS.
#
# O efeito e o pior possivel: o item chega, e como nenhuma palavra casa, ele nao
# vira NAO_SEI — vira «nao pertence a este universo». Uma peneira que fala outra
# lingua nao separa o que presta do que nao presta: rejeita tudo, e com ar de
# quem julgou.
#
# NAO SE TRADUZ A LISTA: JUNTA-SE A OUTRA LINGUA AO LADO.
# Traduzir apagaria o portugues, e ha itens nesta casa que vem em portugues (as
# licoes do Brasil, os relatorios). O termo internacional — `doi`, `orcid` — nao
# tem lingua e serve a todos.
#
# O QUE ISTO **NAO** RESOLVE, e fica dito: a arquitetura certa e CONCEITO ->
# TERMO LOCAL (um `WHEAT_SEPTORIA` com as suas formas em IT/ES/FR/EN), e ela
# NAO existe aqui. Isto e a correcao minima que faz a porta italiana funcionar
# hoje; a arquitetura fica registada como proposta.
# ⚠️ AS CHAVES DESTE DICIONARIO ERAM A QUARTA COPIA DA TAXONOMIA.
# `"T7"` carregava o lexico de CIENCIA — porque `pedido/pedido.py` dizia que
# `T7` era «Ciencia e ensaio». No Atlas, que e o dono, `T7` e TECHNICAL NETWORK
# e o lexico de ciencia e de `T5`. As chaves passam a ser as do Atlas
# (`leis/territorios.py`), e ha uma prova que reprova quem inventar uma chave
# que o dono nao conhece.
#
#     UMA CHAVE DE DICIONARIO TAMBEM E UMA DECLARACAO DE TAXONOMIA.
PERGUNTAS_DO_UNIVERSO = {
    # T5 · SCIENCE — papers, estudos, trials, institutos
    #
    # ⚠️ `prova` SAIU, E A MEDICAO QUE O TIROU E O MELHOR ARGUMENTO DESTE
    # FICHEIRO. Ela estava aqui como «trial» em italiano. Medido no corpus
    # italiano real desta arvore, 49 itens:
    #
    #     42 de 49 eram admitidos a CIENCIA por UMA palavra — `prova` —
    #     e ela casava dentro de «ap-PROV-al» e «ap-PROV-ing», em titulos
    #     de regulamento da UE escritos em INGLES.
    #
    # Nenhum dos 42 era ciencia. O recall de 85.7% que esta casa media e
    # publicava era um artefacto de substring, e nao um acerto.
    #
    #     UMA PALAVRA CURTA QUE VIVE DENTRO DE UMA PALAVRA COMUM DE OUTRA
    #     LINGUA NAO E VOCABULARIO: E RUIDO COM AR DE PROVA.
    #
    # O conceito nao se perde — `sperimentazione`, `prova di campo` e
    # `prove sperimentali` dizem-no sem casar com «approval».
    "T5": ["doi", "orcid",                                   # sem lingua
           "estudo", "ensaio", "pesquisa", "revista", "artigo",
           "universidade", "instituto", "publicacao",        # pt
           "studio", "ricerca", "rivista", "articolo",
           "universita", "istituto", "pubblicazione", "convegno",
           "sperimentazione", "prova di campo", "prove sperimentali",
           "tesi"],                                          # it
    # T7 · TECHNICAL NETWORK — agronomos, consultores, cooperativas, extensao
    #
    # ⚠️ ESTE UNIVERSO NUNCA TEVE REGUA, e o que ocupava a chave dele era o
    # lexico de outro. As doze fontes italianas de T7 sao cooperativas e
    # consorcios com servico agronomico; e esse o vocabulario que as nomeia.
    #
    # ⚠️ `soci` SAIU, E FOI A REGUA DE T10 QUE O DESMASCAROU.
    # Enquanto T10 nao tinha regua, `_do_universo` saia mais cedo com
    # `NAO_SE_APLICA` e o ciclo dos OUTROS universos nunca corria para estes
    # itens. Com a regua de T10 escrita, ele passou a correr — e 26 dos 39
    # documentos de T10 sairam `NAO` com a prova «fala claramente de T7:
    # soci».
    #
    # Medido, palavra inteira por palavra inteira, nos mesmos 26 documentos:
    #
    #     sociale 22 · association 10 · social 9 · sociali 8 ·
    #     societario 2 · associations 2 · societa 1 · society 1
    #
    #     `soci` NAO CASOU UMA UNICA VEZ COM A PALAVRA `soci`.
    #
    # E o estrago era o pior que esta porta consegue fazer: um `NAO`, que e a
    # unica resposta que FECHA o assunto — «prova a favor da exclusao» — e a
    # prova era `associazione`.
    #
    #     UMA PALAVRA CURTA QUE VIVE DENTRO DE PALAVRAS CORRENTES
    #     NAO E VOCABULARIO: E RUIDO COM AR DE PROVA.
    #
    # E a mesma familia de `prova` dentro de `approvazione` (T5) e de
    # `fitosanitario` no rodape institucional (T3), com a mesma medicao.
    #
    # NAO SE INVENTOU SUBSTITUTO. O conceito de T7 — a rede tecnica — ja esta
    # coberto por `cooperativa`, `consorzio`, `agronomi`, `assistenza
    # tecnica`, `servizio agronomico`, `tecnico di campo` e `divulgazione
    # tecnica`. Acrescentar `soci conferenti` ou `assemblea dei soci` sem um
    # corpus onde os medir seria trocar um termo por medir por outro por
    # medir.
    "T7": ["cooperativa", "consorcio", "agronomo", "extensao",
           "assistencia tecnica",                            # pt
           "consorzio", "agronomi", "assistenza tecnica",
           "servizio agronomico", "tecnico di campo",
           "divulgazione tecnica"],                          # it
    # T9 · o que o concorrente publica
    "T9": ["concorrente", "evento",                          # serve nas duas
           "lancamento", "campanha", "produto", "anuncio",   # pt
           "lancio", "campagna", "prodotto", "annuncio",
           "novita", "fiera"],                               # it
    # T4 · regulatorio
    "T4": ["registro", "ministero", "decreto",               # serve nas duas
           "autorizacao", "rotulo", "bula",                  # pt
           "autorizzazione", "etichetta", "foglietto",
           "registrazione", "gazzetta"],                     # it
    # T3 · PEST / DISEASE / WEEDS — os tres, e nao dois
    #
    # ⚠️ O NOME DESTE UNIVERSO NO ATLAS TEM TRES PERNAS, E A TERCEIRA FALTAVA.
    # `docs/fontes/ATLAS-DE-FONTES-EAME.md` escreve T3 como «doenças, insetos,
    # PLANTAS DANINHAS, alertas, intensidade, geografia, evolução temporal,
    # RESISTÊNCIA». O vocabulario aqui nao tinha uma unica palavra de daninha
    # nem de resistencia — em lingua nenhuma. Nao era um buraco de traducao:
    # era um TERCO DO CONCEITO ausente dos dois lados.
    #
    #     O LEXICO ESTAVA INCOMPLETO NA MESMA LINGUA EM QUE FOI ESCRITO.
    #
    # E isso tinha consequencia com nome: `IT-T5-005` e a SIRFI — «flora
    # infestante e resistencia a herbicidas» — e um documento dela nunca
    # poderia responder a esta porta.
    #
    # ⚠️ O QUE ENTROU E O QUE NAO ENTROU. So entram termos cujo sentido E do
    # universo. `soglia`, `monitoraggio` e `campo` ficaram DE FORA de proposito:
    # sao vocabulario de qualquer boletim agricola, e um boletim meteorologico
    # T2 traz os tres. Encher a lista com eles subiria a contagem de itens
    # admitidos sem subir a verdade — que e a definicao de afrouxar a regua.
    #
    #     UMA PALAVRA QUE QUALQUER DOCUMENTO TEM NAO SEPARA DOCUMENTO NENHUM.
    "T3": ["fungo", "larva",                                 # serve nas duas
           "praga", "doenca", "inseto", "infestacao", "sintoma",   # pt
           "daninha", "erva daninha", "herbicida", "resistencia",  # pt · daninha
           "parassita", "malattia", "insetto", "infestazione",
           "sintomo", "avversita", "patogeno",               # it
           # ⚠️ `fitosanitario` SAIU, E FOI O GABARITO QUE O TIROU.
           # Eu acrescentei-o por parecer obviamente de T3, e nao o medi
           # contra o gabarito humano antes. Medido depois, com a porta v3
           # contra a v4 sobre os mesmos 36 documentos: os acertos CAIRAM de
           # 6 para 4, e QUATRO boletins que o humano rotulou `T3_NAO`
           # passaram a `SIM` — todos boletins agrometeorologicos da ARPAV,
           # todos pela mesma dupla: `fitosanitario` + `ovideposizione`.
           #
           # E `fitosanitario` estava, nos quatro, no RODAPE INSTITUCIONAL:
           #
           #     «Regione Veneto — Unita Organizzativa FITOSANITARIO —
           #      Difesa Integrata — Ambiente Rurale»
           #
           # E o nome de um DEPARTAMENTO, e ele esta em todos os boletins
           # daquele publicador, falem eles de praga ou de chuva.
           #
           #     O NOME DE QUEM PUBLICA NAO E O ASSUNTO DO QUE SE PUBLICA.
           #
           # A regra que o devia ter travado ja estava escrita quatro linhas
           # acima — «uma palavra que qualquer documento tem nao separa
           # documento nenhum» — e eu escrevi-a e nao a apliquei ao termo que
           # estava a acrescentar.
           #
           # `fitopatolog` FICA: e raiz de conteudo (fitopatologia,
           # fitopatologico), e nao nome de orgao.
           "fitopatolog", "trappola", "trappole",
           "ovideposizione", "peronospora", "oidio", "botrite",
           "ticchiolatura",                                  # it · praga/doenca
           "infestante", "diserbo", "erbicida", "malerba"],  # it · daninha
    # T10 · MARKET / TRADE / INDUSTRY
    #
    # ⚠️ ESTE UNIVERSO NUNCA TEVE REGUA, E O SILENCIO DELE TINHA PRECO MEDIDO:
    # 39 documentos italianos reais recebiam `NAO_SE_APLICA` com toda a
    # educacao — «nao ha regra escrita do que conta como T10» — e essa educacao
    # escondia que ninguem tinha escrito a pergunta.
    #
    # DE ONDE VEM CADA PALAVRA. Nao foram escolhidas a partir do corpus: saem
    # dos DOIS donos que ja declaram o que T10 e.
    #
    #     docs/fontes/ATLAS-DE-FONTES-EAME.md   «commodities, producao, precos
    #                                            confiaveis, importacoes,
    #                                            exportacoes, industria,
    #                                            ingredientes ativos,
    #                                            movimentos de mercado»
    #     leis/territorios.py::APELIDOS         preco · mercado · comercio ·
    #                                            importacao · exportacao ·
    #                                            commodity · industria
    #
    # ── O QUE FICOU DE FORA, E PORQUE — TUDO MEDIDO NOS 85 REAIS ──────────
    # A lei desta casa ja estava escrita quatro universos acima, e aqui ela
    # mordeu seis vezes:
    #
    #     UMA PALAVRA QUE QUALQUER DOCUMENTO TEM NAO SEPARA DOCUMENTO NENHUM.
    #     O NOME DE QUEM PUBLICA NAO E O ASSUNTO DO QUE SE PUBLICA.
    #
    # `dazi`       SAIU. Vive dentro de `reDAZIone` — a redacao, que assina
    #              todas as paginas de qualquer jornal italiano. Casava em
    #              32 dos 85, e em nenhum deles falava de tarifas.
    # `preco`      SAIU. Vive dentro de `sPRECO` (desperdicio) e de `PRECOce`
    #              (precoce), duas palavras correntes numa pagina agricola.
    #              Fica a forma plural `precos`, que nao cabe em nenhuma das
    #              duas. Perde-se o singular portugues: e uma perda declarada,
    #              e um `NAO_SEI` a mais vale mais do que um `SIM` errado.
    # `mercato` ·  SAIRAM. Casavam em 40, 34, 30 e 31 dos 85 — e o contexto,
    # `mercati` ·  lido documento a documento, era o MENU do site
    # `ingrosso` · («Trend e mercati», «Ingrosso»), a NUVEM DE ETIQUETAS
    # `grossist`   («ingrosso 872») e a lista de artigos relacionados. Um
    #              artigo sobre mobilidade sustentavel marcava SEIS sinais de
    #              mercado sem ter uma palavra de mercado no corpo.
    # `export`     SAIU. Os tres exemplos medidos estavam todos no bloco
    #              «potrebbe interessarti anche» — o texto de OUTRO artigo,
    #              colado ao lado deste. Fica `esportazion`, que e a palavra
    #              italiana de verdade, e `exportacao`/`exportacoes` em
    #              portugues.
    # `commercio`· SAIRAM. Dois dos tres usos medidos eram nome de orgao —
    # `comercio`   «camera di commercio», «ministero del commercio». E a mesma
    #              familia de `fitosanitario`, que ja saiu de T3 por isto.
    # `industria`  SAIU. Casava em 7 dos 85, e nos dois contextos lidos era
    #              «prodotto industriale» e «industria alimentare»: o nome de
    #              um SECTOR, nao um movimento de mercado.
    # `atacado`    SAIU. Em portugues tambem e o particio de «atacar», e numa
    #              pagina agricola «cultivo atacado por pragas» e T3, nao T10.
    #
    # ⚠️ E NENHUMA FORMA CABE DENTRO DE OUTRA DESTA LISTA. `importazione`
    # dentro de `importazioni` daria DOIS sinais a UMA palavra, e a regra dos
    # `SINAIS_MINIMOS` deixava de valer sem ninguem dar por isso. Por isso as
    # raizes: `quotazion`, `importazion`, `esportazion`, `rincar` — a mesma
    # solucao que `fitopatolog` ja usa em T3.
    "T10": ["commodity",                                     # sem lingua
            "prezzo", "prezzi", "quotazion", "listino",
            "importazion", "esportazion", "rincar",
            "borsa merci", "domanda e offerta",              # it
            "precos", "cotacao", "cotacoes",
            "importacao", "importacoes",
            "exportacao", "exportacoes"],                    # pt
    # T2 · CLIMATE / WATER / SOIL
    #
    # ⚠️ ESTE UNIVERSO NUNCA TEVE REGUA. Medido na 1.a onda da Big Collection
    # (BC5, 24/09): as fontes T2 (ARPA Marche, ARPAE) nunca podiam dar SIM, e
    # 12 dos 50 canais YouTube vivem em T2/T12 (SOC5).
    #
    # DE ONDE VEM CADA CONCEITO. Dos dois donos que ja declaram o que T2 e:
    #     docs/fontes/ATLAS-DE-FONTES-EAME.md:46  «chuva, temperatura, seca,
    #         geada, ondas de calor, umidade do solo, estresse hidrico, eventos
    #         extremos, indicadores agronomicos»
    #     leis/territorios.py::APELIDOS            clima · tempo · meteorologia ·
    #         chuva · seca · solo · agua · irrigacao
    # e do vocabulario do BOLETIM DO TEMPO (anticiclone, saccatura,
    # perturbazione, nuvolosita, temporalesco, pluviometro) — que o gabarito
    # mostrou ser a forma como «tempo/meteorologia» aparece no corpo de um
    # texto. Esta ultima parte foi lida no gabarito: e medida DENTRO da amostra.
    #
    # ── O QUE FICOU DE FORA, E PORQUE — MEDIDO NO GABARITO T2-V1 ──────────
    #     O MENU DO SITE NAO E O ASSUNTO DA PAGINA.
    # Toda a pagina de uma ARPA traz o menu «Meteo e clima · Agrometeo ·
    # Cambiamenti climatici · Suolo · Acque». Casavam em paginas de concursos,
    # tarifarios e comites de garantia:
    # `clima`                     SAIU. 45 dos 217 NO, 2 dos 27 YES.
    # `meteorologia` e familia    SAIRAM. 19 NO («Servizio meteorologico» no
    #                             menu e no rodape), e os YES ja tem o boletim.
    # `agrometeo`/`agrometeorologia`/`agrometeorologico` SAIRAM. 6 a 14 NO: o
    #                             item de menu e o nome da rede de estacoes.
    # `cambiamento/i climatico/i` SAIRAM. 17 e 16 NO: tema de menu, e o slogan
    #                             de qualquer programa europeu.
    # `suolo`, `acqua`, `acque`   SAIRAM. 76 e 52 NO: menu. Fica o SOLO pela
    #                             `umidita del suolo` e a AGUA pela
    #                             `risorsa idrica` e pela `irrigazione`.
    # `irrigue`/`irrigua`         SAIRAM. «Consorzi di ... acque irrigue» e o
    #                             NOME da ANBI, no rodape de cada pagina dela —
    #                             o nome de quem publica nao e o assunto.
    # `temporale`/`temporali`     SAIRAM. Sao tambem «serie temporali». Ficam
    #                             `temporalesco` e familia.
    # `previsioni meteo`          SAIU. 1 YES e 1 NO: o menu da Arpal.
    # T1 · os MOMENTOS da janela (fase, estadio, colheita/sementeira em frase, defesa,
    # limiar, capturas, tratamento). A CULTURA vive em CULTURA_OBRIGATORIA.
    "T1": ["fenologia|fenologica|fenologico|fenologiche|fenologici|bbch|estadio fenologico",
           "fioritura|allegagione|invaiatura|germogliamento|ingrossamento|inolizione"
           "|floracao|florescimento",
           "difesa integrata|lotta integrata|producao integrada|manejo integrado",
           "soglia di intervento|soglia di trattamento|nivel de controle|nivel de dano",
           "infestazione|infestazioni|infestacao|catture|capturas",
           "trattamento fitosanitario|trattamenti fitosanitari|trattamento insetticida"
           "|trattamenti insetticidi|intervento fitosanitario|interventi fitosanitari"
           "|tratamento fitossanitario|tratamentos fitossanitarios",
           "inizio della raccolta|avvio della raccolta|raccolta iniziata|epoca di raccolta"
           "|tempi di raccolta|in corso di raccolta|la raccolta 2026|prime vendemmie"
           "|vendemmia in corso|semina|semine|trebbiatura|inicio da colheita|semeadura"],
    "T2": ["pioggia|piogge|precipitazione|precipitazioni"        # it
           "|chuva|chuvas|precipitacao|precipitacoes",           # pt
           "temperatura|temperature|temperaturas",
           "siccita|seca|secas|estiagem",
           "gelata|gelate|brina|brinate|geada|geadas",
           "grandine|grandinata|grandinate|granizo",
           "ondata di calore|ondate di calore|onda de calor|ondas de calor",
           "umidita del suolo|umidade do solo",
           "stress idrico|deficit idrico|bilancio idrico"
           "|estresse hidrico|deficit hidrico|balanco hidrico",
           "eventi estremi|evento estremo|eventos extremos",
           "evapotraspirazione|evapotranspiracao",
           "irrigazione|irrigazioni|irrigacao",
           "risorsa idrica|risorse idriche|recurso hidrico|recursos hidricos",
           "anticiclone|anticicloni|anticiclonico|anticiclonica|anticiclones",
           "saccatura|saccature|cavado|cavados",
           "perturbazione|perturbazioni|perturbacao",
           "temporalesco|temporaleschi|temporalesca|temporalesche|trovoada|trovoadas",
           "nuvolosita|nuvolosa|nuvoloso|nebulosidade",
           "pluviometro|pluviometri|pluviometrico|pluviometrica|anemometro|anemometri"],
}


# ── A MESMA REGUA, NA LINGUA DO TEXTO (D3 do dono, 23/09/2026) ─────────────
# Medido no lote-76: 10 de 76 documentos eram NAO_SEI so por estarem em ingles
# (os 10 da Zootecnica), e o dono validou dois deles como ENTRA (gabarito itens 5
# e 6: precos e exportacoes de frango). Uma regua que so fala italiano e
# portugues nao julga um texto ingles: cala-se, e o calar tem nome de NAO_SEI.
#
# A CORRECCAO NAO JUNTA O INGLES A LISTA ITALIANA. `export` saiu de T10 porque
# casava nos blocos «potrebbe interessarti» de paginas ITALIANAS; juntar o ingles
# ao lado traria esse ruido de volta e mudaria vereditos italianos. Em vez disso,
# a porta ve em que lingua o texto esta (`admissao/idioma.py`) e aplica a lista
# DESSA lingua:
#
#     it / pt / lingua NAO SEI  ->  PERGUNTAS_DO_UNIVERSO, exactamente como antes
#     en                        ->  PERGUNTAS_EN (os mesmos conceitos, em ingles)
#     fr / es / de              ->  NAO_SEI com motivo IDIOMA_NAO_SUPORTADO:<xx>
#
# Os limiares nao mudam (SINAIS_MINIMOS = 2; NAO so com prova de outro universo).
#
# CADA TERMO INGLES E O EQUIVALENTE DE UM TERMO QUE JA ESTA NA LISTA IT/PT. As
# mesmas licoes de substring que limparam o italiano valem aqui, e por isso
# ficaram DE FORA, declarado:
#     trial   dentro de «indusTRIAL»          event    dentro de «prEVENT»
#     product dentro de «PRODUCTion»           thesis   dentro de «synTHESIS»
#     import  dentro de «IMPORTant»            pest     dentro de «PESTicide», «BudaPEST»
#     trap    dentro de «sTRAP»                resistance: nao ha equivalente italiano na lista
#     listino / rincar / borsa merci: as formas inglesas («price list», «price
#     increase», «commodity exchange») cabem dentro de `price`/`commodity`, e dariam
#     dois sinais a uma palavra — a regra dos SINAIS_MINIMOS deixava de valer.
# E, como no italiano, NENHUMA FORMA CABE DENTRO DE OUTRA DA MESMA LISTA.
PERGUNTAS_EN = {
    "T5": ["doi", "orcid",                                    # sem lingua
           "study", "research", "journal", "article", "university", "institute",
           "publication", "conference", "experiment", "field trial"],
    "T7": ["cooperative", "consortium", "agronomist", "extension service",
           "technical assistance", "agronomic advice", "field technician"],
    "T9": ["competitor", "launch", "campaign", "announce", "novelty", "trade fair"],
    "T4": ["registration", "ministry", "decree", "authorisation", "authorization",
           "label", "leaflet", "gazette"],
    "T3": ["fungus", "fungi", "larva",                        # larva: sem lingua
           "pests", "disease", "insect", "infestation", "symptom",
           "weeds", "weed control", "herbicide", "parasit", "pathogen",
           "phytopatholog", "plant patholog", "oviposition",
           "downy mildew", "powdery mildew", "botrytis", "apple scab"],
    "T10": ["commodity",                                      # sem lingua
            "price", "quotation", "imports", "exports", "supply and demand"],
    # T2 · os mesmos conceitos da lista it/pt, um a um, por PALAVRA INTEIRA.
    # ⚠️ NAO MEDIDO: o gabarito T2-V1 nao tem nenhum texto ingles de T2. Fica
    # escrito para a porta nao se calar com um boletim em ingles, e o numero
    # dele e `NAO SEI` ate haver exemplos.
    "T1": ["phenology|phenological|bbch|growth stage",
           "flowering|fruit set|veraison|bud break|budbreak",
           "integrated pest management|integrated production",
           "action threshold|intervention threshold|economic threshold",
           "infestation|trap catches|trap catch",
           "crop protection treatment|insecticide treatment|fungicide treatment",
           "harvest started|start of harvest|harvest time|sowing|planting|threshing"],
    "T2": ["rain|rainfall|precipitation",
           "temperature|temperatures",
           "drought|droughts",
           "frost|frosts",
           "hail|hailstorm|hailstorms",
           "heatwave|heatwaves|heat wave|heat waves",
           "soil moisture",
           "water stress|water deficit|water balance",
           "extreme events|extreme weather",
           "evapotranspiration",
           "irrigation",
           "water resources|water resource",
           "anticyclone|anticyclones|anticyclonic",
           "trough",
           "weather front|cold front|warm front",
           "thunderstorm|thunderstorms",
           "cloud cover|cloudiness",
           "rain gauge|rain gauges|anemometer|anemometers"],
}
IDIOMAS_SEM_REGUA = ("fr", "es", "de")


# ── T2 · A LIGACAO AGRICOLA ESCRITA (D29 — JANELAS DE CULTURA, 2026-09-24) ──
# O dono (D29): «na coleta precisamos coletar informacoes relevantes sobre as
# JANELAS DE CULTURA». A regua T2 deixa de perguntar «isto fala de clima?» e passa
# a perguntar «isto sustenta uma janela de cultura?» (Biblia `CAP-WIN`, join keys
# CROP x REGION x PHENOLOGY_STAGE x TIME_WINDOW).
#
#     O TEMPO SO ABRE UMA JANELA QUANDO HA UMA CULTURA DO OUTRO LADO.
#
# Por isso SIM pede as DUAS coisas no texto: um conceito de CONDICAO do campo
# (`PERGUNTAS_DO_UNIVERSO["T2"]`: chuva, temperatura, seca, rega...) E um conceito
# FORTE daqui — a ligacao agricola escrita (fenologia, estadio, defesa integrada,
# limiar, capturas, tratamento fitossanitario) —, ou `agrometeo` com DUAS
# condicoes. So condicao (a previsao do tempo, a tabela
# de chuva, o verao de calor recorde) fica NAO_SEI com motivo SEM_LIGACAO_AGRICOLA
# e a marca D2 REROUTE_POSSIVEL: nao e lixo, e de outra pergunta. So ancora (o
# premio do vinho que fala da vindima) fica NAO_SEI tambem. Nenhuma das metades
# vira NAO: ausencia de evidencia nao e evidencia de ausencia.
#
# A ADMISSAO NAO DECIDE A JANELA. Nao le datas, nao escreve FACT_TIME nem
# FACT_LOCATION: data de calendario != janela, data regulatoria != janela,
# FACT_TIME != PUBLICATION_TIME, SOURCE_LOCATION != FACT_LOCATION. Admite e
# deixa os campos do item como vieram; a janela e da Intelligence.
#
# ── O QUE FICOU DE FORA, E PORQUE — MEDIDO NO GABARITO T2-V2 ──────────────
# `trattamento`/`trattamenti`  SAIRAM soltos: 37 dos 225 NO — «trattamento dei
#                              dati personali» no rodape de privacidade. Ficam as
#                              formas `trattamento fitosanitario`/`insetticida`.
# `raccolta`                   SAIU: «raccolta differenziata» (lixo), 28 NO.
# `semina`, `plantio`          SAIRAM: casavam em programas de fundos e menus.
# `vite`                       SAIU: em italiano e tambem «vidas».
# `coltura`/`colture`          SAIRAM: «Difesa delle colture» e nome de servico.
# NOMES DE CULTURA E `vendemmia`/`trebbiatura`/`colheita` SAIRAM COMO ANCORA.
#     Mediu-se FORA do gabarito (1.259 textos, os 14 SIM lidos um a um): a
#     noticia de mercado fala de tomate e de onda de calor, o premio do vinho
#     fala da vindima e da temperatura — e nenhuma diz o momento de agir. Os
#     boletins que falam de colheita trazem tambem fenologia ou limiar, e entram
#     por ai. A CULTURA E O ASSUNTO DE QUASE TUDO O QUE E AGRICOLA; NAO E A PROVA
#     DE UMA JANELA.
# ⚠️ `agrometeo...` e o nome de muitos menus («Agrometeo») e de seccoes de
#    jornal (AgroNotizie): so conta com DUAS condicoes escritas.
# ── T2C (24/09): A VIA `agrometeo` SO COM CORPO DE BOLETIM ─────────────────
# Medido nos 1.309 textos: a via `agrometeo` + 2 condicoes acrescentava 16 SIM, e so 8
# eram boletins (PDF); os outros 8 eram PAGINAS DE SITE onde «Agrometeo» e item de menu
# ou nome de servico (LaMMA x3, ARPAV x2, ARPAE, Campania, Puglia) — 2 chegariam a Sala.
#
#     O NOME DO SERVICO NAO E O BOLETIM DO SERVICO.
#
# Por isso a via so da SIM quando ha CORPO DE BOLETIM — uma marca de edicao (numero,
# «n. 34/2026», periodo «17 agosto 2026 - 23 agosto 2026», «del 07-09-2026») OU uma
# cultura nomeada — E o texto NAO traz marcas de pagina de site (navegacao, «chi siamo»,
# inscricao, newsletter, «accesso rapido», a descricao do «centro agrometeorologico»).
# O resto da regua nao muda: a via forte (condicao + fenologia/defesa/limiar...) nao
# olha para isto.
_MESES = "gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre"
_EDICAO_DE_BOLETIM = (
    r"\b(bollettino|notiziario|settimanale|giornaliero)\b[^.]{0,80}?\b(n\.?|n°|nr\.?)\s*\d{1,3}\b",
    r"\bn\.?\s*\d{1,3}\s*/\s*20\d\d\b",
    r"\b\d{1,2}\s+(%s)\s+20\d\d\s*-\s*\d{1,2}\s+(%s)\s+20\d\d" % (_MESES, _MESES),
    r"\bdel\s+\d{1,2}[./-]\d{1,2}[./-]20\d\d\b",
)


def _corpo_de_boletim(texto_dobrado: str, anc: dict) -> bool:
    """A via `agrometeo` pede corpo de boletim e recusa pagina de site (T2C)."""
    import re
    if any(_casa(m, texto_dobrado) for m in anc.get("PAGINA_DE_SITE", ())):
        return False
    return (any(re.search(r, texto_dobrado) for r in anc.get("EDICAO", ()))
            or _casa(anc.get("CULTURA", ""), texto_dobrado))


ANCORAS = {
    "T2": {
        # basta UMA destas com UMA condicao
        "FORTES": ["fenologia|fenologica|fenologico|fenologiche|fenologici|bbch|estadio fenologico",
                   "fioritura|allegagione|invaiatura|germogliamento|ingrossamento|inolizione"
                   "|floracao|florescimento",
                   "difesa integrata|lotta integrata|producao integrada|manejo integrado",
                   "soglia di intervento|soglia di trattamento|nivel de controle|nivel de dano",
                   "infestazione|infestazioni|infestacao|catture|capturas",
                   "trattamento fitosanitario|trattamenti fitosanitari|trattamento insetticida"
                   "|trattamenti insetticidi|intervento fitosanitario|interventi fitosanitari"
                   "|tratamento fitossanitario|tratamentos fitossanitarios"],
        # `agrometeo` e tambem nome de menu e de seccao de jornal: so conta com DUAS
        # condicoes escritas (o boletim traz chuva E temperatura; o menu nao traz nada)
        "AGROMETEO": "agrometeorologico|agrometeorologica|agrometeorologici|agrometeorologiche"
                     "|agrometeorologia|agrometeo",
        # T2C: o que faz de `agrometeo` um boletim, e o que faz dele um menu
        "EDICAO": _EDICAO_DE_BOLETIM,
        "CULTURA": "vigneto|vigneti|vite|oliveto|oliveti|olivo|frutteto|frutteti|frumento|grano"
                   "|mais|pomodoro|nocciolo|agrumi|barbabietola|colture",
        "PAGINA_DE_SITE": ("salta al contenuto", "vai al contenuto", "skip to content",
                           "toggle navigation", "main navigation", "menu principale", "chi siamo",
                           "iscrizione", "iscriviti", "newsletter", "area riservata",
                           "accesso rapido", "centro agrometeorologico"),
    },
}
# ── T1 · CROP & PRODUCTION, PARA JANELAS DE CULTURA (T1-JANELA, 2026-09-24) ──
# D29: a Intelligence (CAP-WIN) precisa de CULTURA x REGIAO x FASE x JANELA. T1 nunca
# teve regua: tudo saia NAO_SE_APLICA. Esta regua cobre a parte «calendario agricola /
# desenvolvimento da cultura» do Atlas (docs/fontes/ATLAS-DE-FONTES-EAME.md:45); area,
# producao, preco e previsao de safra NAO estao nela, e isso fica dito.
#
#     SEM CULTURA NOMEADA NAO HA JANELA DE CULTURA.
#
# SIM pede uma cultura nomeada E dois sinais de momento distintos (SINAIS_MINIMOS).
# Medido no gabarito T1-V1 (scripts/regua_t1/): com UM so momento entravam paginas de
# servico (ERSA, CAAR «modellistica fenologica») e a campanha de uma marca de macas
# («fioritura primaverile») — 8 falsos SIM; com dois, 2. O preco: as noticias de
# colheita («la raccolta e iniziata») ficam NAO_SEI — vai-se ver, nao se rejeita.
# `raccolta` solto NAO e momento («raccolta dati», «raccolta differenziata»): so em frase.
# `pero` (= «pero», mas), `riso` (= riso) e `mais` (= «mais» pt) nao sao cultura.
# T1 e TRANSVERSAL: uma cultura nunca prova que um texto NAO e de outro universo.
# T1B (25/09): O MOMENTO TEM DE ESTAR NO CORPO, NAO SO DE PASSAGEM. Medido: um livro de
# 172 mil caracteres sobre inovacao agricola nomeava culturas e citava «trattamento
# fitosanitario» e «inizio della raccolta» UMA vez cada (0,1 por 10 mil caracteres) e
# entrava. Nos boletins do gabarito e da prova cega a densidade mais baixa e 3,8. Abaixo de
# 2 ocorrencias de momento por 10 mil caracteres o texto fica NAO_SEI
# (MOMENTO_SO_DE_PASSAGEM). ⚠️ Limiar escolhido DENTRO da amostra (entre 0,1 e 3,8).
DENSIDADE_MINIMA_DE_MOMENTO = 2.0      # ocorrencias por 10 mil caracteres


def _momento_de_passagem(texto_dobrado: str, conceitos) -> bool:
    import re
    n = 0
    for c in conceitos:
        for forma in str(c).split("|"):
            f = _dobrar(forma)
            if f:
                n += len(re.findall(r"(?<![a-z0-9])" + re.escape(f) + r"(?![a-z0-9])", texto_dobrado))
    return n * 10000.0 / max(len(texto_dobrado), 1) < DENSIDADE_MINIMA_DE_MOMENTO


CULTURA_OBRIGATORIA = {
    "T1": "vite|vigneto|vigneti|uva|uve|olivo|olive|oliveto|oliveti|drupe|melo|mele|meleto"
          "|pere|pesco|pesche|ciliegio|ciliegie|actinidia|kiwi|frumento|grano|pomodoro|pomodori"
          "|patata|patate|nocciolo|nocciole|noccioleto|agrumi|arancio|limone|fragola|fragole"
          "|soia|orzo|girasole|barbabietola|arachidi|castagno|castagne|albicocco|susino|nettarine"
          "|videira|oliveira|trigo|milho|soja|batata|tomate",
}
# ⚠️ NAO MEDIDO (nenhum texto ingles no gabarito T1-V1).
CULTURA_OBRIGATORIA_EN = {
    "T1": "vine|vines|vineyard|vineyards|grapes|olive|olives|olive grove|apple|apples|pear|pears"
          "|peach|cherry|kiwifruit|wheat|tomato|tomatoes|potato|potatoes|hazelnut|hazelnuts"
          "|citrus|strawberry|strawberries|soybean|barley|sunflower|sugar beet|maize|corn",
}

# Os mesmos conceitos em ingles. ⚠️ NAO MEDIDO: o gabarito nao tem texto ingles de
# janela de cultura; o numero fica NAO SEI ate haver exemplos.
ANCORAS_EN = {
    "T2": {
        "FORTES": ["phenology|phenological|bbch|growth stage",
                   "flowering|fruit set|veraison|bud break|budbreak",
                   "integrated pest management|integrated production",
                   "action threshold|intervention threshold|economic threshold",
                   "infestation|trap catches|trap catch",
                   "crop protection treatment|insecticide treatment|fungicide treatment"],
        "AGROMETEO": "agrometeorological|agrometeorology",
    },
}


def _lingua_do_item(item: dict) -> str:
    import importlib.util as _iu
    global _IDIOMA
    if "_IDIOMA" not in globals():
        _sp = _iu.spec_from_file_location("admissao_idioma", Path(__file__).resolve().parent / "idioma.py")
        _IDIOMA = _iu.module_from_spec(_sp)
        _sp.loader.exec_module(_IDIOMA)
    _I = _IDIOMA
    return _I.idioma(" ".join(str(item.get(k) or "") for k in
                              ("texto", "title", "nome", "topics", "crops", "resumo")))


def decidir(item: dict, universo: str, corrida: str = "NAO SEI") -> Decisao:
    """A porta. Uma decisao por par (item, universo) — nunca uma por item.

    E as perguntas vem do ESTAGIO do item (COL-LAW-502): a um documento nao se
    pergunta o tempo de um fato que ainda nao foi extraido dele.
    """
    est = estagio(item)
    endereco = _identidade_do_item(item)
    # `NAO SEI` e ausencia declarada — nunca `"?"`, que e um simbolo com ar de
    # chave. Quem cai aqui NAO passa a porta (`_tem_identidade` recusa), por
    # isso este valor nunca chega a ser a morada de nada na Sala.
    nome_do_item = endereco if endereco is not None else AUSENCIA

    # ── O LIVRO GUARDA A PROVA DE CADA PORTAO, E NAO SO A DO ULTIMO ─────────
    # ⚠️ MEDIDO: `decidir` devolvia a evidencia da ULTIMA pergunta, e so dela.
    # Um item que atravessava o portao temporal por uma data de PUBLICACAO
    # chegava ao livro com `{"palavras": [...], "estagio": "FATO"}` — a chave
    # `quando` nao estava la, e portanto nao havia em lado nenhum a prova de
    # que o tempo do fato continuava por saber.
    #
    #     COL-LAW-042 exige `evidence`. Ela estava la, e NAO era a que provava
    #     a passagem. UMA PROVA QUE NAO PROVA O QUE PASSOU E UM CARIMBO.
    #
    # Cada portao escreve debaixo do seu nome. Nao se fundem chaves: dois
    # portoes podem chamar `quando` a coisas diferentes, e achatar isso faria o
    # segundo apagar o primeiro — exactamente o defeito, com mais passos.
    provas = {}
    for nome, f in perguntas_do_estagio(est):
        r, motivo, ev = f(item)
        provas[nome] = dict(ev, resultado=r)
        if r != SIM:
            return Decisao(item=nome_do_item,
                           universo=universo, resultado=r, regra=nome,
                           motivo=motivo,
                           evidencia=dict(ev, estagio=est, portoes=provas),
                           corrida=corrida)

    r, motivo, ev = _do_universo(item, universo, PERGUNTAS_DO_UNIVERSO.get(universo, []))
    provas["pertence ao universo"] = dict(ev, resultado=r)
    ev = dict(ev, estagio=est, portoes=provas)
    if est == DOCUMENTO:
        # O que NAO foi perguntado fica escrito. Um silencio nao explicado
        # reabre-se como duvida daqui a tres meses.
        ev["tempo_do_fato"] = (
            "NAO_SE_APLICA neste estagio: FACT_TIME pertence ao claim, nao ao "
            "documento (COL-LAW-201 · COL-LAW-502). Sera perguntado quando o "
            "fato for extraido.")
    return Decisao(item=nome_do_item,
                   universo=universo, resultado=r, regra="pertence ao universo",
                   motivo=motivo, evidencia=ev, corrida=corrida)


class LivroIlegivel(Exception):
    """O livro existe e nao se conseguiu ler. NAO e um livro vazio."""


def escrever(decisoes: list) -> int:
    """Junta ao livro; nunca reescreve o que ja estava la.

    ⚠️ ESTA FRASE JA FOI FALSA, E DE MANEIRA DESTRUTIVA.

    O `except json.JSONDecodeError: pass` engolia a falha de leitura, `d`
    ficava `{"DECISOES": []}`, e a linha seguinte ESCREVIA esse dicionario por
    cima do ficheiro. Um livro truncado — um `write` interrompido, um disco
    cheio, um merge mal resolvido — era lido como zero decisoes e substituido
    pelo lote da vez. Reproduzido nesta arvore:

        813 decisoes  ->  livro truncado  ->  escrever([1 decisao])
        813 decisoes  ->  1

    e a funcao devolvia `1` como se fosse o total verdadeiro, de modo que nem
    quem chamou ficava a saber.

        FICHEIRO ILEGIVEL != FICHEIRO VAZIO.
        UNKNOWN NASCIDO COMO ZERO, E AQUI COM PODER DE APAGAR.

    Agora recusa-se. Um livro que nao se consegue ler e um caso para uma
    pessoa olhar — nunca para uma maquina resolver deitando fora o que nao
    entendeu. O ficheiro fica intacto: quem levanta esta excecao nao escreveu
    nada.

    ⚠️ E A SEGUNDA MANEIRA DE PERDER O LIVRO ERA A CONCORRENCIA.
    A funcao LE, junta e ESCREVE. Duas corridas ao mesmo tempo davam duas
    falhas diferentes, e as duas silenciosas na origem:

        as duas leem 100 · cada uma junta 1 · a ultima escreve 101
        -> a decisao da outra desapareceu, e o total parece certo

        uma le enquanto a outra escreve
        -> JSON truncado -> LivroIlegivel na corrida seguinte

    Medido nesta arvore com cinco corridas concorrentes: uma das cinco morreu
    com `LivroIlegivel`. A recusa estava certa; o que estava errado era haver
    o que recusar.

        LER, JUNTAR E ESCREVER SEM TRAVA NAO E ACRESCENTAR:
        E ESCREVER POR CIMA DE QUEM ESTAVA A ACRESCENTAR.

    A trava e BLOQUEANTE, e nao fail-fast como a da Sala de Espera — e a
    diferenca e de conceito, nao de gosto. Na sala, duas escritas da MESMA
    corrida na mesma morada sao um conflito e devem gritar. Aqui, muitas
    corridas DIFERENTES acrescentam ao MESMO livro: nao ha conflito nenhum,
    ha fila. Fazer isto falhar seria transformar trabalho legitimo em erro.
    """
    LIVRO.parent.mkdir(parents=True, exist_ok=True)
    trava = os.open(str(LIVRO) + ".lock", os.O_CREAT | os.O_RDWR, 0o644)
    try:
        _prender(trava)
        return _escrever_sob_trava(decisoes)
    finally:
        _soltar(trava)
        os.close(trava)


# ── A TRAVA, NOS DOIS SISTEMAS — E CONTINUA A SER A MESMA TRAVA ─────────────
#
# ⚠️ `import fcntl` ESTAVA AQUI DENTRO, E `fcntl` NAO EXISTE EM WINDOWS.
# O efeito nao era «a trava e mais fraca no Windows»: era a PORTA NAO ABRIR.
# `escrever()` e chamada por `orquestrador.pela_porta()` em TODA corrida, e a
# primeira linha dela rebentava com `ModuleNotFoundError`. Medido nesta bancada
# a 2026-09-15, com a rota canonica italiana a correr contra Postgres real: a
# corrida atravessou SOURCE, RUN, RAW e STORAGE, e morreu ao bater na admissao.
#
#     UMA ETAPA QUE NAO CORRE NAO E UMA ETAPA QUE RECUSOU.
#     E A ESTRADA A ACABAR ANTES DA PORTA.
#
# O QUE **NAO** MUDOU, E E O QUE IMPORTA: a trava continua EXCLUSIVA e
# BLOQUEANTE, pela razao escrita no corpo de `escrever()` — aqui nao ha
# conflito, ha fila, e fazer isto falhar transformaria trabalho legitimo em
# erro. Em POSIX e o mesmo `flock` de sempre, byte a byte igual. Em Windows e
# `msvcrt.locking`, que trava uma REGIAO do ficheiro e e igualmente visivel
# entre processos.
#
# ⚠️ NAO HA TETO DE ESPERA, E A AUSENCIA DELE E A DECISAO.
# A primeira versao desta peca desistia ao fim de 120 segundos e levantava
# `OSError`. O numero nasceu aqui, sem contrato, sem lei e sem precedente nesta
# casa — e um numero inventado num sitio so nao e uma politica: e uma diferenca
# de comportamento entre sistemas, disfarcada de prudencia.
#
#     POSIX esperava.  Windows desistia aos 120 s.
#     A MESMA CONTENCAO LEGITIMA DAVA DOIS DESFECHOS.
#
# E o desfecho do Windows era exactamente o que o corpo de `escrever()` proibe
# tres paragrafos acima: aqui nao ha conflito, HA FILA, e transformar fila em
# erro transforma trabalho legitimo em falha. Uma corrida honesta que calhasse
# de esperar dois minutos atras de outra corrida honesta seria acusada de
# avaria.
#
#     UM TETO ARBITRARIO NAO PROTEGE DE NADA:
#     SO DECIDE, POR NUMERO REDONDO, QUEM E QUE LEVA A CULPA.
#
# Fica a semantica que o POSIX sempre teve: quem espera pela trava, espera pela
# trava. Se ela nunca se soltar, isso e uma trava presa — e trava presa e um
# defeito a diagnosticar, nao um erro a fabricar no fim de uma contagem.
#
# ⚠️ E USA-SE `LK_NBLCK` E NAO `LK_LOCK`. O `LK_LOCK` tem um teto proprio
# escondido — tenta dez vezes, com um segundo de intervalo, e levanta. Um teto
# que se herda da biblioteca e tao arbitrario como um escrito a mao, com o
# agravante de nao estar a vista. A tentativa nao-bloqueante, repetida por nos,
# e a unica forma de a espera ser realmente nossa e realmente sem fim.


def _prender(fd) -> None:
    """Trava exclusiva e BLOQUEANTE sobre `fd`, nos dois sistemas. → None."""
    try:
        import fcntl                                           # noqa: PLC0415
    except ImportError:
        pass
    else:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return
    import msvcrt                                              # noqa: PLC0415
    import time                                                # noqa: PLC0415
    while True:
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            # UM BYTE CHEGA: o que importa e a REGIAO ser a mesma para todos
            # os que a disputam, e nao o tamanho dela. O ficheiro de trava
            # nunca tem conteudo — travar alem do fim e legitimo em Windows.
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return
        except OSError:
            time.sleep(0.05)


def _soltar(fd) -> None:
    """Larga a trava. Nunca rebenta: isto corre dentro de um `finally`."""
    try:
        import fcntl                                           # noqa: PLC0415
    except ImportError:
        pass
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)
        return
    import msvcrt                                              # noqa: PLC0415
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    except OSError:
        # Largar uma trava que nao se chegou a prender nao e um erro, e
        # rebentar aqui esconderia a excecao verdadeira que trouxe o `finally`.
        pass


def _escrever_sob_trava(decisoes: list) -> int:
    """O corpo de `escrever`, com a trava ja presa por quem chamou."""
    d = {"DECISOES": []}
    if LIVRO.is_file():
        try:
            d = json.loads(LIVRO.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise LivroIlegivel(
                "%s existe e nao e JSON valido (%s). NAO foi escrito nada: um "
                "livro ilegivel nao e um livro vazio, e continuar aqui "
                "apagaria as decisoes que ja la estavam. Repare o ficheiro, ou "
                "arquive-o com outro nome, antes de voltar a correr."
                % (LIVRO, e)) from e
        if not isinstance(d, dict) or not isinstance(d.get("DECISOES", []), list):
            raise LivroIlegivel(
                "%s tem JSON valido mas nao a forma do livro (esperava um "
                "objecto com a lista DECISOES). NAO foi escrito nada." % LIVRO)
    d.setdefault("DECISOES", []).extend(asdict(x) for x in decisoes)
    LIVRO.parent.mkdir(parents=True, exist_ok=True)
    # ⚠️ E A ESCRITA E ATOMICA, PELA MESMA RAZAO DA SALA DE ESPERA.
    # `write_text` deixa o ficheiro truncado se o processo morrer a meio — no
    # sitio exacto onde o livro bom estava. Corpo inteiro num temporario na
    # MESMA pasta, `fsync`, e so entao `os.replace`, que e atomico no POSIX.
    # Quem ler durante a escrita ve o livro ANTERIOR, inteiro.
    #
    #     FICHEIRO PARCIAL NAO E ESTADO LEGITIMO.
    corpo = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
    fd, temporario = tempfile.mkstemp(prefix=".livro-", suffix=".json",
                                      dir=str(LIVRO.parent))
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write(corpo)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporario, str(LIVRO))
        temporario = None
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)
    return len(d["DECISOES"])


# ── A FRONTEIRA DESTA MISSAO ────────────────────────────────────────────────
#
# Os nomes que a SAIDA ja carrega, na lingua da porta. O envelope do fato NAO os
# repete: repetir daria DOIS donos do mesmo conceito, livres para divergir a
# partir do dia em que um deles mudar.
#
#     ONE CONCEPT -> ONE OWNER, e um campo copiado e meio dono.
JA_TEM_CAMPO_PROPRIO_NO_READY = (
    "id", "url", "texto", "title", "nome",
    "source_id", "fonte",
    "source_location", "fact_location", "fact_time",
    "fact_time_basis", "fact_location_basis",
    "published_at", "observed_at", "captured_at",
    "published_at_basis", "source_location_basis", "tempo_lugar_evidencia",
    "source_declared_evidence_class",
    "raw_asset_id",
    # `data` NAO entra no envelope: e o campo generico que a `_tem_quando`
    # acabou de recusar como tempo do fato. Deixa-lo viajar dentro do fato
    # daria-lhe uma segunda porta para voltar a ser lido como FACT_TIME.
    "data",
    # Vocabulario de TRANSPORTE, nao de fato. A linhagem documental fecha-se
    # por `RAW_OBSERVATION_ID` (COL-LAW-033 · COL-LAW-043), e nao aqui.
    "artifact_type", "parent_artifact_id", "parent_sha256",
    "erro_de_leitura",
)


def envelope_do_fato(item: dict, est: str):
    """O que o produtor declarou como FATO, preservado tal e qual.

    ⚠️ ISTO NAO E UMA LISTA DE CAMPOS. E DE PROPOSITO.

    Medido no caminho real, com um fato agronomico de 39 campos:

        campos na entrada ...... 39
        campos no READY ........ 12
        perdidos ............... 20, entre eles `claim_id`, `subject`,
                                 `predicate`, `crop_eppo`, `problem_eppo`,
                                 `method`, `unit`, `scale`, `denominator`,
                                 `doi` e `registration_id`

    E o que torna isto um defeito e nao uma escolha: **a porta JA SABE que
    aquilo e um fato**. `MARCAS_DE_FATO` le `claim_id`, `subject`, `predicate` e
    `fact_id`, `estagio()` devolve `FATO`, e a regua aplicada muda por causa
    disso. Os campos entram, sao lidos, DECIDEM — e nao saem.

        O SISTEMA SABE O QUE E UM CLAIM.
        O CONTRATO DE SAIDA NAO TINHA ONDE O POR.

    A tentacao era escrever cem nomes fixos — `crop`, `crop_eppo`, `problem`,
    `method`, `unit`... — e a `COL-LAW-202` diz porque nao: ela declara o que um
    claim **PODE** preservar, e nao um esquema fechado. Uma lista fixa escolhida
    por mim decidiria hoje, sem caso que obrigue, que campos o agro tem direito
    a ter — e o campo numero 101 morreria calado, que e exactamente a doenca.

        PRESERVAR O QUE CHEGOU != ADIVINHAR O QUE DEVIA TER CHEGADO.

    ⚠️ E ELE SO EXISTE QUANDO O ESTAGIO E `FATO`. Um documento nao tem fato
    estruturado dentro — ele RELATA (COL-LAW-201 · COL-LAW-502). Devolver um
    envelope vazio para um boletim seria dizer «olhei e nao havia», quando a
    verdade e «a pergunta nao se aplica a esta especie de coisa».

    ⚠️ E ELE NAO EXTRAI NADA. Nao le o texto, nao infere, nao normaliza, nao
    cunha `crop_eppo` nenhum. Extraccao de claim e `TARGET` na `COL-LAW-202` e
    NAO existe nesta casa. Isto e transporte, e so.
    """
    if est != FATO:
        return AUSENCIA_NAO_SE_APLICA
    # ⚠️ A ORDEM DAS CHAVES E CANONICA, E NAO E ARRUMACAO.
    # `sala_de_espera.impressao_da_corrida()` assina os BYTES do corpo, e e essa
    # assinatura que distingue um retry legitimo («ja estava») de um conflito
    # («esta corrida ja contou outra historia»). O envelope vai ao banco e volta
    # como texto; se a ordem das chaves mudasse na volta, o MESMO conteudo dava
    # uma impressao diferente — e um retry honesto seria acusado de conflito.
    #
    #     UMA IMPRESSAO QUE DEPENDE DA ORDEM EM QUE ALGUEM ESCREVEU O DICIONARIO
    #     NAO E UMA IMPRESSAO.
    return {k: item[k] for k in sorted(item)
            if k not in JA_TEM_CAMPO_PROPRIO_NO_READY
            and not str(k).startswith("_")}


# ── O GRAU DE PRECISAO DO ITEM EM TEMPO E LUGAR (D62 · D63, dono, 25/09) ────
# «A Intelligence tem de saber o grau de precisao de cada item e o que fazer
# com ele.» Nada disto barra: diz, por cada uma das quatro perguntas, se a
# resposta esta PROVADA, se foi CALCULADA (data relativa contada a partir da
# publicacao provada — D63) ou se e NAO SEI.
COMPLETUDE_PROVADA, COMPLETUDE_CALCULADA = "PROVADA", "CALCULADA"
# O default da coluna `completude_tempo_lugar` (migration 033), BYTE A BYTE
# `json.dumps(COMPLETUDE_NAO_MEDIDA, sort_keys=True, ensure_ascii=False)`:
# uma linha pousada antes da 033 diz «nao medido», e nao «nada provado».
COMPLETUDE_NAO_MEDIDA = {
    "PUBLICACAO": AUSENCIA, "LOCAL_DA_FONTE": AUSENCIA,
    "DATA_DO_FATO": AUSENCIA, "LOCAL_DO_FATO": AUSENCIA, "PROVADAS": AUSENCIA,
    "ORIGEM": "pousado antes da migration 033: a completude nao foi medida"}
# O default de `tempo_lugar_evidencia` (033), byte a byte, pela mesma razao.
TEMPO_LUGAR_EVIDENCIA_NAO_MEDIDA = {
    "FACT_LOCATION_KIND": AUSENCIA, "FACT_LOCATION_PRECISION": AUSENCIA,
    "FACT_LOCATION_VEIO_DE": AUSENCIA, "FACT_TIME_CALCULO": AUSENCIA,
    "FACT_TIME_EVIDENCIA": AUSENCIA, "FACT_TIME_EXPRESSAO": AUSENCIA,
    "FACT_TIME_KIND": AUSENCIA,
    "FACT_TIME_PRECISION": AUSENCIA, "FACT_TIME_VEIO_DE": AUSENCIA,
    "LEITOR": AUSENCIA,
    "PUBLISHED_AT_CONFLITO": AUSENCIA, "PUBLISHED_AT_OUTRA": AUSENCIA,
    "PUBLISHED_AT_OUTRA_BASIS": AUSENCIA, "PUBLISHED_AT_PRECISION": AUSENCIA,
    "SOURCE_LOCATION_PRECISION": AUSENCIA,
    "ORIGEM": "pousado antes da migration 033: a evidencia do tempo e do lugar nao foi medida"}
#: As palavras de uma data do facto CALCULADA a partir da publicacao (D63/DA-7).
BASES_CALCULADAS = ("RELATIVA_A_PUBLICACAO", "PUBLISHED_AT_COM_PROVA")
QUATRO_DO_TEMPO_E_LUGAR = (("PUBLICACAO", "PUBLISHED_AT", None),
                           ("LOCAL_DA_FONTE", "SOURCE_LOCATION", None),
                           ("DATA_DO_FATO", "FACT_TIME", "FACT_TIME_BASIS"),
                           ("LOCAL_DO_FATO", "FACT_LOCATION", "FACT_LOCATION_BASIS"))


def completude_tempo_lugar(ready: dict) -> dict:
    """`{PUBLICACAO|LOCAL_DA_FONTE|DATA_DO_FATO|LOCAL_DO_FATO: estado, PROVADAS: n}`.

    Le so o contrato de saida (o READY, ou uma linha da Sala com os mesmos
    nomes). Nao preenche nada e nao decide nada.
    """
    fora = {}
    for nome, campo, base in QUATRO_DO_TEMPO_E_LUGAR:
        v = ready.get(campo)
        if v in (None, "", AUSENCIA, AUSENCIA_NAO_SE_APLICA, "NÃO SEI", "NAO_SEI"):
            fora[nome] = AUSENCIA
        elif base == "FACT_TIME_BASIS" and (
                str(ready.get(base) or "").startswith(BASES_CALCULADAS)
                or (ready.get("TEMPO_LUGAR_EVIDENCIA") or {}).get(
                    "FACT_TIME_CALCULO") == "RELATIVA_A_PUBLICACAO"):
            fora[nome] = COMPLETUDE_CALCULADA
        else:
            fora[nome] = COMPLETUDE_PROVADA
    fora["PROVADAS"] = sum(1 for n, _, _ in QUATRO_DO_TEMPO_E_LUGAR if fora[n] != AUSENCIA)
    # ⚠️ CHAVES ORDENADAS, pela razao do `envelope_do_fato`: a Sala guarda isto
    # como JSON com `sort_keys`, e `impressao_da_corrida` assina o corpo pela
    # ordem das chaves. Medido (test_migracao_033_sala, teste 3): com a ordem
    # de montagem, reler e repousar a MESMA corrida dava RUN_ID_CONFLICT.
    return {k: fora[k] for k in sorted(fora)}


def pronto_para_inteligencia(item: dict, decisao: Decisao) -> dict:
    """O contrato de saida. A inteligencia recebe ISTO, e mais nada.

    Ela nao sabe — nem precisa de saber — qual raspador trouxe, qual API, qual
    veiculo, nem que remendo foi preciso pelo caminho. Se amanha o executor for
    outro, este contrato nao muda, e nenhum consumidor a jusante mexe uma linha.

    ⚠️ E DESDE `C-READY-LINEAGE-BEFORE-SCALE-V1` ELE LEVA A OBSERVACAO.
    Nao e um campo de conveniencia: sem ele, a unica maneira de voltar do item
    ao bruto era procurar `derived_artifact` pelo `sha256` — e isso MEDIU-SE
    ambiguo contra PostgreSQL real. Dois PDFs diferentes com o mesmo texto
    extraido dao DOIS derivados com o mesmo `sha256`, e a procura devolve os
    dois, com duas observacoes e dois objetos de armazem.

        SHA256 IDENTIFICA BYTES. NAO IDENTIFICA OBSERVACAO.
        DOIS CANDIDATOS NAO SAO UMA LINHAGEM.

    A COL-LAW-033 ja exigia linhagem a todo artefato, e ja tinha escrito o
    porque: «A PROCEDENCIA SO VALE SE FOR POSTA NA COLETA. Depois e tarde.»
    O valor ja estava em maos — as duas rotas canonicas poem `raw_asset_id` no
    item que entregam a porta — e era deitado fora exactamente aqui.

        RUNTIME SABE != O SISTEMA GUARDA (know-how §86.4).

    ⚠️ E SO ESTE ID VIAJA. `storage_object_id` NAO entra: `raw_asset` ja aponta
    para a copia por chave estrangeira composta `(storage_object_id, sha256)`,
    e duplica-lo aqui daria duas declaracoes do mesmo parentesco, livres para
    divergir. A MENOR IDENTIDADE QUE FECHA A ESTRADA E A CERTA.

    ⚠️ E DESDE `C-COL-PRESERVE-FACTS-V1` ELE LEVA MAIS SETE, E NENHUM E NOVO.
    A propria COL-LAW-043 escrevia o alvo — *«QUEM disse O QUE sobre QUE CULTURA
    e QUE PROBLEMA, ONDE, QUANDO, DE QUE PAPEL e COM QUE EVIDENCIA»* — e a lista
    de doze nao tinha onde por nem a especie da coisa, nem a especie da
    evidencia, nem o fato. A lei contradizia-se a si propria tres paragrafos
    abaixo, e o `isto e mais nada` venceu na pratica.

        ESTAGIO · PUBLISHED_AT · OBSERVED_AT · FACT_TIME_BASIS ·
        FACT_LOCATION_BASIS · SOURCE_DECLARED_EVIDENCE_CLASS · FATO

    Cada um tem dono declarado ANTES desta missao — `admissao.estagio()`,
    `coleta/ingresso.py::FRONTEIRA_TRANSPORTA`, `leis/artefato.py::conferir`,
    `regras/italy_contracts.mjs`, `MARCAS_DE_FATO`. Nenhum e um conceito novo:
    sao conceitos que existiam, eram lidos, decidiam — e nao saiam.

        RUNTIME SABE != O SISTEMA GUARDA (know-how §86.4).

    ⚠️ E NENHUM DELES PREENCHE NADA. Ausencia continua `NAO SEI`; a pergunta que
    nao se aplica continua `NAO_SE_APLICA`; e os dois continuam a ser coisas
    diferentes de vazio e de zero.
    """
    if decisao.resultado != SIM:
        raise ValueError(f"item {decisao.item} nao passou a porta ({decisao.resultado})")
    # ⚠️ AUSENCIA NAO SE FABRICA, E `or` AQUI SERIA UM DEFEITO.
    # `raw_asset.id` e `bigserial`, mas quem escreve isto nao tem de saber
    # disso: `or` transformaria um id falsy num «NAO SEI» silencioso, e um
    # «NAO SEI» inventado e pior do que um id errado, porque ninguem o procura.
    # Nunca se deriva de sha256, URL, caminho, filename nem RUN_ID.
    observacao = item.get("raw_asset_id")
    est = estagio(item)

    def _ou_nao_sei(chave):
        v = item.get(chave)
        return AUSENCIA if v is None or str(v).strip() == "" else v

    ready = {
        "ESTADO": "PRONTO_PARA_INTELIGENCIA",
        "ITEM_ID": decisao.item,
        "RAW_OBSERVATION_ID": AUSENCIA if observacao is None else observacao,
        "UNIVERSO": decisao.universo,
        # ⚠️ A ESPECIE DA COISA VIAJA. Ela ja era calculada e deitada fora.
        # `estagio()` decide QUE PERGUNTAS a porta faz (COL-LAW-502), e a
        # jusante nao havia como saber se aquele READY era um DOCUMENTO que
        # relata ou um FATO extraido. Sao coisas diferentes, e medi-las com a
        # mesma regua e o erro que a propria lei veio impedir.
        "ESTAGIO": est,
        "TEXTO": item.get("texto") or item.get("title") or "",
        "SOURCE_ID": item.get("source_id") or item.get("fonte") or AUSENCIA,
        "SOURCE_LOCATION": item.get("source_location", AUSENCIA),
        "FACT_LOCATION": item.get("fact_location", AUSENCIA),
        # ⚠️ O `or item.get("data")` SAIU DAQUI, E ERA UM DEFEITO MEDIDO.
        # `data` nao declara de que tempo e. Um coletor que la pusesse a data do
        # documento — e e a data que um coletor tem — produzia `FACT_TIME` falso
        # carimbado como fato. `COL-LAW-031`: nao por fallback.
        "FACT_TIME": item.get("fact_time") or AUSENCIA,
        # ── COMO SE SABE, E PORQUE NAO SE SABE ──────────────────────────────
        # A `leis/artefato.py::conferir` JA reprovava um `FACT_LOCATION`
        # preenchido «sem dizer de onde saiu» — a lei existia e o contrato de
        # saida nao tinha onde por a resposta. E do outro lado, medido no livro
        # italiano real: as 175 observacoes escrevem, uma a uma, PORQUE o tempo
        # do fato e desconhecido — «UNKNOWN — o PDF nao expoe a data do fato
        # medido, so a de geracao». Essa frase morria aqui.
        #
        #     UM `UNKNOWN` COM RAZAO E UMA MEDICAO.
        #     UM `UNKNOWN` SEM RAZAO E INDISTINGUIVEL DE DESLEIXO.
        "FACT_TIME_BASIS": _ou_nao_sei("fact_time_basis"),
        "FACT_LOCATION_BASIS": _ou_nao_sei("fact_location_basis"),
        # ── OS OUTROS TEMPOS, QUE NAO SAO O DO FATO ─────────────────────────
        # `coleta/ingresso.py::FRONTEIRA_TRANSPORTA` ja os declarava como coisas
        # que atravessam, e eles atravessavam ate aqui para morrer. Sem eles, a
        # jusante «nao sei quando o fato foi» e «nao sei nada sobre tempo» sao a
        # mesma resposta — e nao sao (COL-LAW-031).
        "PUBLISHED_AT": _ou_nao_sei("published_at"),
        "OBSERVED_AT": _ou_nao_sei("observed_at"),
        # ── 033 · A BASE DOS OUTROS DOIS VALORES, E O GRAU DE PRECISAO ──────
        # TEMPO-E-LUGAR (D61): o VALOR de `published_at` e de `source_location`
        # chegava e a BASE parava aqui. D62: a completude diz, das quatro, quais
        # estao provadas — calculada no fim, sobre este mesmo dicionario.
        "PUBLISHED_AT_BASIS": _ou_nao_sei("published_at_basis"),
        "SOURCE_LOCATION_BASIS": _ou_nao_sei("source_location_basis"),
        "COMPLETUDE_TEMPO_LUGAR": None,
        # DA-7: o que o leitor do texto mediu (especie, precisao, CALCULADA,
        # a expressao com a conta). Sem leitura: o default «nao medido».
        # ⚠️ CHAVES ORDENADAS, SEMPRE — tambem no default. A Sala guarda o JSON
        # com `sort_keys` e a impressao da corrida assina pela ordem: medido no
        # test_migracao_033_sala (teste 3), o default pela ordem de montagem
        # fazia um retry honesto virar RUN_ID_CONFLICT.
        "TEMPO_LUGAR_EVIDENCIA": {k: v for k, v in sorted(
            (item.get("tempo_lugar_evidencia")
             or TEMPO_LUGAR_EVIDENCIA_NAO_MEDIDA).items())},
        # ── A ESPECIE PROBATORIA, DECLARADA PELA FONTE ──────────────────────
        # ⚠️ O NOME E LONGO DE PROPOSITO, E NAO SE ENCURTA.
        # Os 13 contratos de fonte italianos declaram `EVIDENCE_CLASS` ANTES de
        # qualquer execucao, e com leis escritas ao lado —
        # `AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE`, `COMPANY_CLAIM !=
        # REGULATORY_FACT`. Nenhuma atravessava: a jusante, um boletim
        # agroclimatico da ARPAV e um relato de campo da ARIF eram o MESMO
        # objecto, `TEXTO`.
        #
        # Mas o valor e TEXTO LIVRE e e DA FONTE, nao do documento — medido:
        # «OBSERVED_FIELD_SIGNAL + TECHNICAL_GUIDELINE (separar por bloco)».
        # Chamar-lhe `EVIDENCE_CLASS` aqui faria qualquer leitor le-lo como a
        # especie DESTE documento, medida. Nao e. E a expectativa declarada de
        # quem publica.
        #
        #     DECLARADO PELA FONTE != MEDIDO NO DOCUMENTO.
        #     UM NOME QUE PERMITE A CONFUSAO E METADE DA CONFUSAO.
        "SOURCE_DECLARED_EVIDENCE_CLASS": _ou_nao_sei(
            "source_declared_evidence_class"),
        # ── O FATO, QUANDO O ITEM E UM FATO ─────────────────────────────────
        "FATO": envelope_do_fato(item, est),
        "CAPTURED_AT": item.get("captured_at", AUSENCIA),
        "CORRIDA": decisao.corrida,
        "ADMITIDO_POR": f"{decisao.regra} v{decisao.versao}",
    }
    # ⚠️ A CHAVE JA ESTA NO SITIO CERTO: `impressao_da_corrida` assina o corpo
    # pela ORDEM das chaves, e a ordem e a de `sala_de_espera.CAMPOS_READY`.
    ready["COMPLETUDE_TEMPO_LUGAR"] = completude_tempo_lugar(ready)
    return ready


if __name__ == "__main__":
    # ⚠️ A DEMO FICOU INCOERENTE QUANDO A TAXONOMIA FOI CORRIGIDA, E NINGUEM
    # DEU POR ISSO — porque uma demo nao tem quem a reprove.
    # Ela mandava «Ensaio de campo publicado com DOI» a `T7` e logo a seguir
    # chamava `pronto_para_inteligencia()`, que so faz sentido para um item
    # ADMITIDO. Depois de `T7` voltar a ser TECHNICAL NETWORK — e a ciencia
    # voltar para `T5`, como o Atlas sempre disse — a demo passou a imprimir
    # NAO e a construir um READY a partir de uma recusa.
    #
    #     UM EXEMPLO QUE NAO CORRE E UMA DOCUMENTACAO QUE MENTE DEVAGAR.
    exemplo = {"id": "demo-1",
               "texto": ("Boletim tecnico da cooperativa para os socios, "
                         "assinado pelo agronomo de campo"),
               "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    d = decidir(exemplo, "T7", corrida="demo")
    print(f"{d.resultado} · {d.regra} · {d.motivo}")
    print(json.dumps(pronto_para_inteligencia(exemplo, d), ensure_ascii=False, indent=2))
