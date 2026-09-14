#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PORTAO DE ESCOPO DAS FONTES — dono unico de «esta fonte pode ser chamada?».

    import escopo_de_fontes as esc
    esc.veredito('ES-T3-001').permitido      -> False
    esc.veredito('IT-T3-002').permitido      -> True
    esc.exigir('FR-T4-001')                  -> levanta FonteForaDoEscopo

POR QUE ISTO EXISTE, E O QUE FOI MEDIDO
----------------------------------------
`pedido/receitas.py::resolver` e o seletor de fontes da Collection. Ele lia as
77 fontes do censo — 6 espanholas, 4 francesas, 11 europeias, 56 italianas — e
filtrava por pais assim:

    pais = (p.filtros.get("pais") or "").upper()
    ...
    if pais:
        ...

O filtro so existia QUANDO alguem escrevia o pais. Medido nesta arvore, com o
seletor a correr:

    «colete regulatorio»   -> 9 fontes: 4 ES · 1 FR · 2 EU · 2 IT
    «colete boletins de praga» -> 17 fontes: 1 ES · 2 FR · 1 EU · 13 IT

Nenhum pedido precisou de estar errado. Bastou nao dizer nada.

    UMA PROTECAO QUE DEPENDE DE ALGUEM SE LEMBRAR NAO E UMA PROTECAO.

E havia um segundo buraco, este ativo mesmo COM o pais escrito:

    if c not in mapa.get(pais, (pais,)) and c not in ("EU", "EUROPA"):
        continue

«EUROPA serve qualquer pais europeu» — e por isso `EU-T4-002` (EU Pesticides
Database, veredito NAO SEI, sem contrato, sem chamador italiano) entrava numa
corrida italiana sozinha. Isso e a lei que o §11 proibe, escrita em codigo:

    EU SOURCE  !=  ITALY SOURCE automaticamente.

AS CINCO COISAS QUE ESTE FICHEIRO NAO CONFUNDE
-----------------------------------------------
    OWNER            quem publica
    SOURCE           o canal de dados
    COUNTRY_SCOPE    para que pais aquela FONTE esta autorizada   <- so isto
    FACT_LOCATION    onde o facto aconteceu
    SOURCE_LOCATION  onde a fonte esta

Este portao responde pela terceira linha, e por nenhuma outra. Uma fonte
italiana que publique um facto frances continua ITALY_ACTIVE, e o facto
continua frances — `leis/lugar_do_fato.py` e que responde por isso, e nao foi
tocado. Bloquear a aquisicao nunca reescreve um facto ja colhido.

DE ONDE VEM O PAIS — E DE ONDE ELE NUNCA VEM
---------------------------------------------
Do prefixo do `SOURCE_ID` que o atlas ja atribuiu, que e a mesma leitura que
`system-map/scripts/scan_sources.py::PAIS` fazia antes desta missao. Nada aqui
cunha identidade nova.

    NUNCA de URL, host, slug, nome, caminho, hash ou LINGUA DO TEXTO.

Um `.it` nao prova uma fonte italiana. Um texto em italiano numa conta
espanhola nao muda o pais da conta. Fonte sem identidade canonica sai daqui
com `UNKNOWN` — e UNKNOWN e BLOQUEADO, nunca «provavelmente serve».

    AUSENCIA DE PROVA NAO E PROVA DE AUSENCIA, E TAMBEM NAO E AUTORIZACAO.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTO = os.path.join(RAIZ, 'regras', 'ESCOPO-DE-FONTES.json')

#: Os quatro grupos do §4, mais o quinto que a honestidade obriga.
ITALY_ACTIVE = 'ITALY_ACTIVE'
SPAIN_FUTURE = 'SPAIN_FUTURE'
FRANCE_FUTURE = 'FRANCE_FUTURE'
SHARED_EUROPE_INACTIVE = 'SHARED_EUROPE_INACTIVE'
UNKNOWN = 'UNKNOWN'
GRUPOS = (ITALY_ACTIVE, SPAIN_FUTURE, FRANCE_FUTURE, SHARED_EUROPE_INACTIVE, UNKNOWN)

NAO_SEI = 'NAO SEI'

# O prefixo canonico de um SOURCE_ID do atlas: `IT-T3-002`, `EU-T4-001-B`.
# Ancorado no inicio e exigindo o territorio, de proposito: `ITALIA-QUALQUER`
# nao e um SOURCE_ID e nao pode passar por um.
_RE_SOURCE_ID = re.compile(r'^(EU|FR|ES|IT)-T\d{1,2}-\d{2,4}')
# O prefixo de um grupo de busca: `IT-VINE-FLAVESCENCE`, `ES-OLIVE-REPILO`.
_RE_GRUPO = re.compile(r'^(EU|FR|ES|IT)-')


def _registo() -> dict:
    with open(REGISTO, encoding='utf-8') as f:
        return json.load(f)


_R = _registo()
PAIS_OPERACIONAL_ATIVO = _R['PAIS_OPERACIONAL_ATIVO']
PAISES = _R['PAISES']
ALLOWLIST = {k: v for k, v in _R['ITALY_ALLOWLIST'].items() if k != 'NOTA'}


class FonteForaDoEscopo(RuntimeError):
    """A fonte existe, esta preservada, e NAO pode correr nesta operacao.

    E uma RECUSA, nunca um erro: o portao correu, mediu, e a resposta foi nao.
    Quem apanha isto nao deve tentar outra vez mais esperto.
    """

    def __init__(self, veredito_):
        super().__init__(veredito_.motivo)
        self.veredito = veredito_


@dataclass(frozen=True)
class Veredito:
    identidade: str
    pais: str
    grupo: str
    permitido: bool
    motivo: str
    italy_use_allowed: str

    def como_dicionario(self) -> dict:
        return {'IDENTIDADE': self.identidade, 'PAIS': self.pais,
                'GRUPO': self.grupo, 'PERMITIDO': self.permitido,
                'MOTIVO': self.motivo, 'ITALY_USE_ALLOWED': self.italy_use_allowed}


def pais_de(source_id) -> str:
    """→ 'IT' · 'ES' · 'FR' · 'EU' · NAO SEI. Le o prefixo canonico, e mais nada.

    Nao aceita nome, URL, host nem lingua. Se o identificador nao for um
    SOURCE_ID do atlas, a resposta e NAO SEI — que e a verdade, e nao um buraco.
    """
    m = _RE_SOURCE_ID.match(str(source_id or '').strip().upper())
    return m.group(1) if m else NAO_SEI


def pais_do_grupo_de_busca(nome) -> str:
    """→ o pais de um recorte de busca (`IT-VINE-FLAVESCENCE`), pelo prefixo."""
    m = _RE_GRUPO.match(str(nome or '').strip().upper())
    return m.group(1) if m else NAO_SEI


def _grupo_do_pais(pais: str) -> str:
    return (PAISES.get(pais) or {}).get('GRUPO', UNKNOWN)


def veredito(source_id, *, pais_da_operacao: str = None) -> Veredito:
    """A UNICA pergunta: esta fonte pode ser CHAMADA pela operacao ativa?

    Fecha por omissao. As unicas duas maneiras de passar sao:
      · o pais da fonte E o pais da operacao ativa;
      · a fonte esta, pelo SOURCE_ID, na allowlist explicita da operacao.
    """
    op = (pais_da_operacao or PAIS_OPERACIONAL_ATIVO).upper()
    ident = str(source_id or '').strip()
    pais = pais_de(ident)

    if pais == NAO_SEI:
        return Veredito(ident, NAO_SEI, UNKNOWN, False,
                        'SOURCE_ID sem identidade canonica (%r) — COUNTRY_SCOPE '
                        'UNKNOWN. UNKNOWN nao ativa.' % ident, NAO_SEI)

    grupo = _grupo_do_pais(pais)

    if pais == op:
        return Veredito(ident, pais, grupo, True,
                        'COUNTRY_SCOPE = %s = pais da operacao ativa' % pais, 'YES')

    # A allowlist e por SOURCE_ID, nunca por pais inteiro: autorizar «EU» seria
    # exactamente o buraco que esta missao fechou.
    aut = ALLOWLIST.get(ident.upper())
    if aut and aut.get('ITALY_USE_ALLOWED') == 'YES' and op == 'IT':
        return Veredito(ident, pais, ITALY_ACTIVE, True,
                        'autorizada explicitamente para a operacao italiana: %s'
                        % aut.get('PORQUE', ''), 'YES')

    estado = (PAISES.get(pais) or {}).get('STATUS_OPERACIONAL', 'INACTIVE')
    if pais == 'EU':
        motivo = ('fonte europeia/partilhada sem autorizacao explicita para a '
                  'operacao %s. ITALY_USE_ALLOWED = UNKNOWN — e UNKNOWN nao ativa.' % op)
        allowed = 'UNKNOWN'
    else:
        motivo = ('COUNTRY_SCOPE = %s, STATUS_OPERACIONAL = %s. Preservada e '
                  'pesquisavel; fora do caminho operacional %s.' % (pais, estado, op))
        allowed = 'NO'
    return Veredito(ident, pais, grupo, False, motivo, allowed)


def exigir(source_id, *, pais_da_operacao: str = None, onde: str = '') -> Veredito:
    """O PREFLIGHT. Chama-se ANTES da aquisicao, nunca depois do download.

    Depois do download ja se gastou rede, dinheiro e — o que nao se desfaz —
    ja se tocou na fonte. Um portao a seguir a aquisicao mede o estrago; nao o
    evita.
    """
    v = veredito(source_id, pais_da_operacao=pais_da_operacao)
    if not v.permitido:
        raise FonteForaDoEscopo(v)
    return v


def permitida(source_id, *, pais_da_operacao: str = None) -> bool:
    return veredito(source_id, pais_da_operacao=pais_da_operacao).permitido


def filtrar(fontes, *, chave='source_id', pais_da_operacao: str = None):
    """→ (deixadas_entrar, barradas). Nao apaga: separa, e diz o que separou.

    `barradas` leva o veredito de cada uma ao lado, porque uma recusa sem
    motivo escrito e indistinguivel de um desaparecimento.
    """
    dentro, fora = [], []
    for f in fontes:
        ident = f.get(chave) if isinstance(f, dict) else f
        v = veredito(ident, pais_da_operacao=pais_da_operacao)
        (dentro if v.permitido else fora).append((f, v) if not v.permitido else f)
    return dentro, fora


# ── AS CONTAS SOCIAIS: A IDENTIDADE E OUTRA, A PERGUNTA E A MESMA ──────────
# Uma conta nao tem SOURCE_ID do atlas: tem `ACCOUNT_CELL_ID` (`BAYER|IT|FACEBOOK`)
# e um `COUNTRY_SCOPE` PROVADO, escrito por `regras/comunicacao_identidade.py`.
# O pais da conta le-se DESSE campo — nunca da lingua do texto, nunca do dominio.
#
#     CONTA GLOBAL DA EMPRESA  !=  CONTA ITALIANA.
#     CONTA ESPANHOLA          !=  CONTA ITALIANA.
CONTAS = os.path.join(RAIZ, 'data', 'samples', 'COMPETITOR-PUBLIC-COMM',
                      'CONTAS-V1.json')


def _linhas_de_conta() -> list:
    if not os.path.isfile(CONTAS):
        return []
    with open(CONTAS, encoding='utf-8') as f:
        return json.load(f).get('ACCOUNTS', [])


# ⚠️ `ACCOUNT_CELL_ID` NAO E UMA IDENTIDADE DE CONTA. E UMA CELULA DO LOTE.
# Medido nesta arvore: 44 linhas, 36 `ACCOUNT_CELL_ID` distintos. OITO celulas
# levam DUAS contas diferentes — a conta provada e a candidata rejeitada que
# caiu na mesma casa da matriz (`BAYER|ES|YOUTUBE` leva
# `BayerCropScienceEspaña` PROVED e um `NOT_KNOWN` rejeitado).
#
#     UMA CELULA DA MATRIZ NAO E UM CANAL. «EMPRESA x PAIS x PLATAFORMA» e a
#     PERGUNTA que se foi fazer, e duas respostas diferentes cabem nela.
#
# Indexar por celula fazia uma das duas desaparecer em silencio — e qual das
# duas dependia da ordem do ficheiro. Entao a celula ambigua sai daqui como
# UNKNOWN, e UNKNOWN nao ativa. Nao se inventa aqui um identificador novo a
# partir de URL, handle ou par: §5 e explicita, e separar ficheiros nunca
# autorizou cunhar identidades.
def _contas_por_celula() -> dict:
    fora = {}
    for c in _linhas_de_conta():
        fora.setdefault(c.get('ACCOUNT_CELL_ID'), []).append(c)
    return fora


def veredito_de_conta(cell_id, *, url: str = None,
                      pais_da_operacao: str = None) -> Veredito:
    """Uma conta so entra na coleta italiana se as TRES fecharem — e nenhuma
    delas e a lingua do post:

        ACCOUNT_IDENTITY_STATE = PROVED
        COUNTRY_SCOPE          = LOCAL_COUNTRY_PROVED
        COUNTRY                = o pais da operacao

    `COLLECTION_AUTHORIZED` ja e o veredito das tres, escrito pelo dono da
    identidade. Este portao acrescenta a quarta pergunta, que e a desta missao:
    autorizada PARA QUE PAIS.
    """
    op = (pais_da_operacao or PAIS_OPERACIONAL_ATIVO).upper()
    ident = str(cell_id or '').strip()
    candidatas = _contas_por_celula().get(ident, [])
    if url is not None:
        candidatas = [c for c in candidatas if c.get('ACCOUNT_URL') == url]
        ident = '%s @ %s' % (ident, url)
    if not candidatas:
        return Veredito(ident, NAO_SEI, UNKNOWN, False,
                        'conta fora do cadastro provado — identidade UNKNOWN.', NAO_SEI)
    if len(candidatas) > 1:
        return Veredito(ident, NAO_SEI, UNKNOWN, False,
                        'celula do lote AMBIGUA: %d contas diferentes respondem por '
                        '%r. Celula nao e identidade — sem desempate provado isto e '
                        'UNKNOWN, e UNKNOWN nao ativa.' % (len(candidatas), ident),
                        NAO_SEI)
    c = candidatas[0]
    escopo = c.get('COUNTRY_SCOPE')
    # ⚠️ O PAIS DA CELULA NAO E O PAIS DA CONTA, e confundi-los foi o defeito
    # que esta missao veio fechar. `COUNTRY` diz que celula do lote se estava a
    # tentar preencher — «BASF em IT» — e isso e um ALVO, nao uma medicao. A
    # conta que se encontrou ali pode ser a conta GLOBAL da empresa.
    #
    #     ALVO DA BUSCA  !=  LOCALIDADE PROVADA DA CONTA.
    #
    # Medido: `basf_global` foi encontrada na celula BASF|IT e tem
    # COUNTRY_SCOPE = GLOBAL. Ler o pais da celula dava-lhe «IT» e punha uma
    # conta global dentro do lote italiano.
    if escopo != 'LOCAL_COUNTRY_PROVED':
        return Veredito(ident, NAO_SEI, UNKNOWN,
                        False, 'COUNTRY_SCOPE = %s — a localidade da conta nao esta '
                        'provada. UNKNOWN nao ativa (o pais da celula do lote '
                        'era %s, e alvo de busca nao e medicao).'
                        % (escopo, c.get('COUNTRY')), NAO_SEI)
    pais = str(c.get('COUNTRY') or NAO_SEI).upper()
    grupo = _grupo_do_pais(pais)
    if c.get('COLLECTION_AUTHORIZED') != 'YES':
        return Veredito(ident, pais, grupo, False,
                        'COLLECTION_AUTHORIZED = %s · %s'
                        % (c.get('COLLECTION_AUTHORIZED'),
                           c.get('COLLECTION_AUTHORIZED_WHY', '')), 'NO')
    if pais != op:
        return Veredito(ident, pais, grupo, False,
                        'conta local PROVADA de %s — preservada, e fora da '
                        'operacao %s.' % (pais, op), 'NO')
    return Veredito(ident, pais, grupo, True,
                    'identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + '
                    'pais %s = operacao ativa' % pais, 'YES')


def veredito_do_pedido(*, country_scope, source_id=None,
                       pais_da_operacao: str = None) -> Veredito:
    """O preflight do DESPACHO: um pedido de coleta pode seguir?

    Duas perguntas, e as duas tem de fechar:

      1. o `country_scope` declarado pelo pedido e o da operacao ativa?
      2. se o pedido nomeia uma FONTE, essa fonte pode ser chamada?

    A primeira existe porque `country_scope` chegava ao despacho e era so
    escrito no registo. Um campo que ninguem le para decidir nao e um portao:
    e um rotulo. Bastava um pedido com `country_scope='ES'` para uma corrida
    espanhola atravessar a rota italiana inteira sem nada a recusar.

    A segunda so corre quando ha fonte nomeada. Um pedido de busca por termo
    nao tem SOURCE_ID — e exigir um que nao existe obrigaria alguem a inventa-lo,
    que e exactamente o que a §5 proibe.
    """
    op = (pais_da_operacao or PAIS_OPERACIONAL_ATIVO).upper()
    declarado = str(country_scope or '').strip().upper()
    if not declarado:
        return Veredito(declarado or NAO_SEI, NAO_SEI, UNKNOWN, False,
                        'pedido sem COUNTRY_SCOPE declarado — UNKNOWN nao ativa.',
                        NAO_SEI)
    if declarado != op:
        grupo = _grupo_do_pais(declarado) if declarado in PAISES else UNKNOWN
        return Veredito(declarado, declarado, grupo, False,
                        'pedido declara COUNTRY_SCOPE = %s e a operacao ativa e %s. '
                        'O material de %s continua guardado; so nao corre aqui.'
                        % (declarado, op, declarado), 'NO')
    if source_id:
        return veredito(source_id, pais_da_operacao=op)
    return Veredito(declarado, declarado, _grupo_do_pais(declarado), True,
                    'COUNTRY_SCOPE = %s = operacao ativa; pedido sem fonte nomeada'
                    % declarado, 'YES')


def veredito_de_grupo_de_busca(nome, *, pais_da_operacao: str = None) -> Veredito:
    """O recorte de busca e selecao de fonte tambem: decide o que se procura.

    `regras/sensor_coleta.py::recortes_no_escopo` continua a ser o dono da
    decisao no runner; isto responde a mesma pergunta pela mesma regra, para o
    censo e para a prova de que as duas nao divergiram.
    """
    op = (pais_da_operacao or PAIS_OPERACIONAL_ATIVO).upper()
    ident = str(nome or '').strip()
    pais = pais_do_grupo_de_busca(ident)
    if pais == NAO_SEI:
        return Veredito(ident, NAO_SEI, UNKNOWN, False,
                        'recorte sem pais no nome — UNKNOWN nao corre.', NAO_SEI)
    grupo = _grupo_do_pais(pais)
    if pais == op:
        return Veredito(ident, pais, grupo, True,
                        'recorte do pais da operacao ativa', 'YES')
    return Veredito(ident, pais, grupo, False,
                    'recorte de %s — guardado, e inativo na operacao %s.' % (pais, op),
                    'NO')


# ── O CENSO, DERIVADO — nunca digitado ─────────────────────────────────────
def censo(medido: dict = None) -> dict:
    """Cada fonte, conta e recorte conhecidos, com o grupo onde cada um cai.

    Le do censo ja medido (`system-map/data/sources.generated.json`), do
    cadastro de contas e dos recortes declarados no codigo. Nao ha aqui uma
    lista escrita a mao: uma lista a mao envelhece calada.

    `medido` existe para quem esta A GERAR aquele ficheiro: o scanner do mapa
    tem a medicao em memoria e ainda nao a escreveu. Sem este parametro, ele
    censearia a medicao ANTERIOR — um censo de uma arvore que ja nao e esta, e
    com o agravante de parecer certo.
    """
    if medido is not None:
        S = medido
    else:
        caminho = os.path.join(RAIZ, 'system-map', 'data', 'sources.generated.json')
        S = {}
        if os.path.isfile(caminho):
            with open(caminho, encoding='utf-8') as f:
                S = json.load(f)

    fontes, vistos = [], set()
    for bloco, onde in (('SOURCES', 'docs/fontes/ATLAS-DE-FONTES-EAME.md'),
                        ('MASTER_ITALIANO', 'candidatas/ITALY-SOURCE-MASTER-V1.json')):
        for f in S.get(bloco, []):
            sid = f.get('source_id')
            if not sid or sid in vistos:
                continue
            vistos.add(sid)
            v = veredito(sid)
            fontes.append({
                'SOURCE_ID': sid, 'OWNER': f.get('owner') or NAO_SEI,
                'SOURCE_NAME': f.get('name') or NAO_SEI,
                'COUNTRY_SCOPE': v.pais, 'TERRITORIO': f.get('territory') or NAO_SEI,
                'TIPO': f.get('type') or NAO_SEI, 'URL': f.get('url') or NAO_SEI,
                'CONTRATO_EXISTE': bool(f.get('contract')),
                'ONDE_ESTA_A_FICHA': onde,
                'GRUPO': v.grupo, 'ATIVO_NA_ITALIA': v.permitido,
                'ITALY_USE_ALLOWED': v.italy_use_allowed, 'MOTIVO': v.motivo,
            })

    # O censo conta LINHAS, nao celulas: as 44 contas levantadas, cada uma com o
    # seu veredito. Contar celulas perdia oito.
    contas = []
    for c in sorted(_linhas_de_conta(),
                    key=lambda x: (x.get('ACCOUNT_CELL_ID') or '',
                                   x.get('ACCOUNT_URL') or '')):
        v = veredito_de_conta(c.get('ACCOUNT_CELL_ID'), url=c.get('ACCOUNT_URL'))
        contas.append({
            'ACCOUNT_CELL_ID': c.get('ACCOUNT_CELL_ID'),
            # §5: conta nao tem SOURCE_ID canonico no atlas, e nao se lhe cunha um.
            'SOURCE_ID': NAO_SEI,
            'OWNER': c.get('COMPANY'), 'CELULA_PAIS_ALVO': c.get('COUNTRY'),
            'CANAL': c.get('PLATFORM'), 'URL': c.get('ACCOUNT_URL'),
            'COUNTRY_SCOPE': v.pais, 'IDENTIDADE': c.get('ACCOUNT_IDENTITY_STATE'),
            'ESCOPO_PROVADO': c.get('COUNTRY_SCOPE'),
            'GRUPO': v.grupo, 'ATIVO_NA_ITALIA': v.permitido, 'MOTIVO': v.motivo,
        })

    recortes = []
    for nome in sorted(_recortes_declarados()):
        v = veredito_de_grupo_de_busca(nome)
        recortes.append({'GRUPO_DE_BUSCA': nome, 'COUNTRY_SCOPE': v.pais,
                         'GRUPO': v.grupo, 'ATIVO_NA_ITALIA': v.permitido})

    return {'PAIS_OPERACIONAL_ATIVO': PAIS_OPERACIONAL_ATIVO,
            'FONTES': fontes, 'CONTAS': contas, 'RECORTES': recortes,
            'CONTAGENS': _contagens(fontes, contas, recortes)}


def _recortes_declarados() -> set:
    """Os nomes de recorte que o codigo realmente declara, lidos com `ast`.

    Sem executar codigo: importar `sensor_coleta` puxa a casa toda atras.
    """
    import ast
    nomes = set()
    for rel in ('regras/sensor_coleta.py', 'regras/rotulos_censo.py'):
        p = os.path.join(RAIZ, rel)
        if not os.path.isfile(p):
            continue
        with open(p, encoding='utf-8') as f:
            arvore = ast.parse(f.read())
        for no in ast.walk(arvore):
            if not isinstance(no, ast.Assign):
                continue
            if not any(isinstance(a, ast.Name) and a.id == 'TERMOS' for a in no.targets):
                continue
            if isinstance(no.value, ast.Dict):
                for k in no.value.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        nomes.add(k.value)
    return nomes


def _contagens(fontes, contas, recortes) -> dict:
    """ENTIDADE e CANAL contam-se separados — 54 canais nao sao 54 organizacoes.

    Uma organizacao tem site, Instagram, LinkedIn, YouTube, API, PDF e RSS, e
    continua a ser UMA organizacao. Somar canais e chamar-lhes empresas foi o
    erro que esta casa ja cometeu uma vez.
    """
    out = {}
    for pais, rotulo in (('IT', 'ITALY'), ('ES', 'SPAIN'), ('FR', 'FRANCE'),
                         ('EU', 'EU_SHARED'), (NAO_SEI, 'UNKNOWN')):
        do_pais = [f for f in fontes if f['COUNTRY_SCOPE'] == pais]
        cont = [c for c in contas if c['COUNTRY_SCOPE'] == pais]
        donos = {f['OWNER'] for f in do_pais if f['OWNER'] != NAO_SEI}
        donos |= {c['OWNER'] for c in cont if c.get('OWNER')}
        out['%s_OWNER_COUNT' % rotulo] = len(donos)
        out['%s_SOURCE_CHANNEL_COUNT' % rotulo] = len(do_pais) + len(cont)
        out['%s_FICHAS' % rotulo] = len(do_pais)
        out['%s_CONTAS' % rotulo] = len(cont)
        out['%s_RECORTES' % rotulo] = len([r for r in recortes
                                           if r['COUNTRY_SCOPE'] == pais])
    out['ATIVAS_NA_ITALIA'] = len([f for f in fontes if f['ATIVO_NA_ITALIA']])
    out['CONTAS_ATIVAS_NA_ITALIA'] = len([c for c in contas if c['ATIVO_NA_ITALIA']])
    out['RECORTES_ATIVOS_NA_ITALIA'] = len([r for r in recortes if r['ATIVO_NA_ITALIA']])
    return out


def prova_seca() -> dict:
    """§17 — O QUE O SELETOR ITALIANO CONSEGUIRIA EXECUTAR, PERGUNTADO A ELE.

    Nao ao registo: AO SELETOR. Perguntar ao registo «quem esta autorizado?»
    devolve a lei; perguntar ao seletor «o que e que tu me davas?» devolve o que
    a maquina faria — e as duas respostas so batem se a trava estiver mesmo no
    caminho. Foi a segunda que apanhou o defeito original, e por isso e a
    segunda que continua a ser feita aqui.
    """
    sys.path.insert(0, RAIZ)
    sys.path.insert(0, os.path.join(RAIZ, 'pedido'))
    import _gavetas  # noqa: F401
    import receitas
    import pedido as pd

    from pedido import ALVOS
    vistos, barradas = {}, {}
    for alvo in ALVOS:
        p = pd.Pedido(alvo=alvo, filtros={})
        plano = receitas.resolver(p)
        for f in plano.fontes_do_assunto:
            vistos[f.get('source_id')] = veredito(f.get('source_id'))
        for x in plano.fora_do_escopo:
            barradas[x['source_id']] = x['veredito']

    por_pais = {}
    for sid, v in vistos.items():
        por_pais[v.pais] = por_pais.get(v.pais, 0) + 1
    return {
        'PERGUNTADO_A': 'pedido/receitas.py::resolver — o seletor real',
        'ALVOS_VARRIDOS': sorted(ALVOS),
        'EXECUTAVEIS': sorted(vistos),
        'EXECUTAVEIS_POR_PAIS': dict(sorted(por_pais.items())),
        'BARRADAS': dict(sorted(barradas.items())),
        'ES_ACTIVE_IN_ITALY': len([v for v in vistos.values() if v.pais == 'ES']),
        'FR_ACTIVE_IN_ITALY': len([v for v in vistos.values() if v.pais == 'FR']),
        'UNKNOWN_ACTIVE_IN_ITALY': len([v for v in vistos.values()
                                        if v.pais == NAO_SEI]),
        'EU_UNAPPROVED_ACTIVE_IN_ITALY': len(
            [s for s, v in vistos.items() if v.pais == 'EU' and s not in ALLOWLIST]),
    }


def main() -> int:
    if '--prova-seca' in sys.argv:
        r = prova_seca()
        print('PROVA SECA · %s' % r['PERGUNTADO_A'])
        print('  alvos varridos: %s' % ', '.join(r['ALVOS_VARRIDOS']))
        print('  executaveis: %d  %s' % (len(r['EXECUTAVEIS']),
                                         r['EXECUTAVEIS_POR_PAIS']))
        print('  barradas:    %d' % len(r['BARRADAS']))
        for sid, v in sorted(r['BARRADAS'].items()):
            print('     %-14s %s' % (sid, v['MOTIVO'][:88]))
        print()
        mau = 0
        for k in ('ES_ACTIVE_IN_ITALY', 'FR_ACTIVE_IN_ITALY',
                  'UNKNOWN_ACTIVE_IN_ITALY', 'EU_UNAPPROVED_ACTIVE_IN_ITALY'):
            print('  %-32s %d  %s' % (k, r[k], 'OK' if r[k] == 0 else 'CONTAMINADO'))
            mau += r[k]
        print()
        print('CONTAMINACAO=%s' % ('ZERO' if mau == 0 else 'DETECTADA'))
        return 0 if mau == 0 else 1

    c = censo()
    print('PAIS OPERACIONAL ATIVO = %s' % c['PAIS_OPERACIONAL_ATIVO'])
    print()
    for k, v in sorted(c['CONTAGENS'].items()):
        print('  %-34s %s' % (k, v))
    print()
    for grupo in GRUPOS:
        f = [x for x in c['FONTES'] if x['GRUPO'] == grupo]
        ct = [x for x in c['CONTAS'] if x['GRUPO'] == grupo]
        r = [x for x in c['RECORTES'] if x['GRUPO'] == grupo]
        print('  %-24s fichas=%-4d contas=%-4d recortes=%d' % (grupo, len(f), len(ct), len(r)))
    if '--json' in sys.argv:
        print(json.dumps(c, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
