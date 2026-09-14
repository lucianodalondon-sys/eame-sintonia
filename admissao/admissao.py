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

LIVRO = RAIZ / "data" / "samples" / "LIVRO-DE-DECISOES.json"

# ── OS QUATRO RESULTADOS, E SO ESTES ────────────────────────────────────────
SIM = "SIM"                      # entra
NAO = "NAO"                      # olhei e nao serve para ESTE universo
NAO_SEI = "NAO_SEI"              # nao ha prova suficiente para dizer sim ou nao
NAO_SE_APLICA = "NAO_SE_APLICA"  # a pergunta nao faz sentido para este item
ERRO = "ERRO"                    # nao consegui olhar — NAO e uma rejeicao

RESULTADOS = (SIM, NAO, NAO_SEI, NAO_SE_APLICA, ERRO)

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
VERSAO_DA_REGRA = "4"


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
    """
    fato = item.get("fact_time") or item.get("data")
    if fato:
        return SIM, "tem tempo do fato", {"quando": str(fato)[:40],
                                          "que_tempo": "FACT_TIME"}
    pub = item.get("published_at")
    if pub:
        return SIM, ("tem ancora de tempo, mas e a data de PUBLICACAO — nao a do "
                     "fato. O tempo do fato continua NAO SEI, e segue NAO SEI "
                     "adiante."), {"quando": str(pub)[:40],
                                   "que_tempo": "PUBLICATION_TIME",
                                   "fact_time": "NAO SEI"}
    return NAO_SEI, ("o item nao diz quando o fato aconteceu. Fica NAO_SEI, "
                     "nao NAO: falta a prova, nao o valor."), {}


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


def perguntas_do_estagio(est: str) -> tuple:
    """As perguntas aplicaveis, por estagio. Uma arquitetura, duas reguas."""
    if est == DOCUMENTO:
        # Prontidao DOCUMENTAL: da para ler, sabe de onde veio, sabe de que
        # original nasceu. O tempo do FATO nao se pergunta aqui.
        return (("legivel", _legivel), ("origem", _tem_origem),
                ("linhagem", _tem_pai))
    # FATO e ESTAGIO_DESCONHECIDO continuam a responder pelo tempo do fato.
    return (("legivel", _legivel), ("origem", _tem_origem),
            ("tempo do fato", _tem_quando))


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
        return NAO_SE_APLICA, (f"nao ha regra escrita do que conta como «{universo}». "
                               f"Sem regra, esta porta nao inventa uma."), {}
    texto = _dobrar(" ".join(str(item.get(k) or "") for k in
                             ("texto", "title", "nome", "topics", "crops", "resumo")))
    achadas = [p for p in palavras if _dobrar(p) in texto]
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
    for outro, termos in PERGUNTAS_DO_UNIVERSO.items():
        if outro == universo:
            continue
        casou = [t for t in termos if t.lower() in texto]
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
    "T7": ["cooperativa", "consorcio", "agronomo", "extensao",
           "assistencia tecnica",                            # pt
           "consorzio", "agronomi", "assistenza tecnica",
           "servizio agronomico", "tecnico di campo",
           "divulgazione tecnica", "soci"],                  # it
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
           "fitosanitario", "fitopatolog", "trappola", "trappole",
           "ovideposizione", "peronospora", "oidio", "botrite",
           "ticchiolatura",                                  # it · praga/doenca
           "infestante", "diserbo", "erbicida", "malerba"],  # it · daninha
}


def decidir(item: dict, universo: str, corrida: str = "NAO SEI") -> Decisao:
    """A porta. Uma decisao por par (item, universo) — nunca uma por item.

    E as perguntas vem do ESTAGIO do item (COL-LAW-502): a um documento nao se
    pergunta o tempo de um fato que ainda nao foi extraido dele.
    """
    est = estagio(item)
    for nome, f in perguntas_do_estagio(est):
        r, motivo, ev = f(item)
        if r != SIM:
            return Decisao(item=str(item.get("id") or item.get("url") or "?"),
                           universo=universo, resultado=r, regra=nome,
                           motivo=motivo, evidencia=dict(ev, estagio=est),
                           corrida=corrida)

    r, motivo, ev = _do_universo(item, universo, PERGUNTAS_DO_UNIVERSO.get(universo, []))
    ev = dict(ev, estagio=est)
    if est == DOCUMENTO:
        # O que NAO foi perguntado fica escrito. Um silencio nao explicado
        # reabre-se como duvida daqui a tres meses.
        ev["tempo_do_fato"] = (
            "NAO_SE_APLICA neste estagio: FACT_TIME pertence ao claim, nao ao "
            "documento (COL-LAW-201 · COL-LAW-502). Sera perguntado quando o "
            "fato for extraido.")
    return Decisao(item=str(item.get("id") or item.get("url") or "?"),
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
    import fcntl
    LIVRO.parent.mkdir(parents=True, exist_ok=True)
    trava = os.open(str(LIVRO) + ".lock", os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(trava, fcntl.LOCK_EX)
        return _escrever_sob_trava(decisoes)
    finally:
        fcntl.flock(trava, fcntl.LOCK_UN)
        os.close(trava)


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
    """
    if decisao.resultado != SIM:
        raise ValueError(f"item {decisao.item} nao passou a porta ({decisao.resultado})")
    # ⚠️ AUSENCIA NAO SE FABRICA, E `or` AQUI SERIA UM DEFEITO.
    # `raw_asset.id` e `bigserial`, mas quem escreve isto nao tem de saber
    # disso: `or` transformaria um id falsy num «NAO SEI» silencioso, e um
    # «NAO SEI» inventado e pior do que um id errado, porque ninguem o procura.
    # Nunca se deriva de sha256, URL, caminho, filename nem RUN_ID.
    observacao = item.get("raw_asset_id")
    return {
        "ESTADO": "PRONTO_PARA_INTELIGENCIA",
        "ITEM_ID": decisao.item,
        "RAW_OBSERVATION_ID": "NAO SEI" if observacao is None else observacao,
        "UNIVERSO": decisao.universo,
        "TEXTO": item.get("texto") or item.get("title") or "",
        "SOURCE_ID": item.get("source_id") or item.get("fonte") or "NAO SEI",
        "SOURCE_LOCATION": item.get("source_location", "NAO SEI"),
        "FACT_LOCATION": item.get("fact_location", "NAO SEI"),
        "FACT_TIME": item.get("fact_time") or item.get("data") or "NAO SEI",
        "CAPTURED_AT": item.get("captured_at", "NAO SEI"),
        "CORRIDA": decisao.corrida,
        "ADMITIDO_POR": f"{decisao.regra} v{decisao.versao}",
    }


if __name__ == "__main__":
    exemplo = {"id": "demo-1", "texto": "Ensaio de campo publicado com DOI",
               "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    d = decidir(exemplo, "T7", corrida="demo")
    print(f"{d.resultado} · {d.regra} · {d.motivo}")
    print(json.dumps(pronto_para_inteligencia(exemplo, d), ensure_ascii=False, indent=2))
