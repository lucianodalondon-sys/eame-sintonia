#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A RELEVANCIA DA FONTE — «esta fonte vale ser acompanhada PARA ESTE PROPOSITO?»

    py leis/relevancia_da_fonte.py          # o contrato, dito em voz alta

E a unica pergunta deste ficheiro. Ele nao pergunta se a fonte responde, se o
caminho ate ela existe, quanto custa la chegar, nem se vale a pena ir HOJE —
essas quatro tem donos, e estao nomeados no fim deste cabecalho.

POR QUE ISTO EXISTE
-------------------
Medido nesta arvore, antes desta lei:

    FIRST_PRE_SPEND_RELEVANCE_GATE = NONE

Um pedido atravessava `pedido/pedido.py` -> `pedido/receitas.py::resolver` ->
`orquestrador/orquestrador.py::correr` -> `subprocess.run(executor)` sem que
NENHUMA das quatro etapas perguntasse se a fonte servia para o assunto pedido.
O unico requisito para correr era existir uma linha no dicionario `EXECUTORES`
do territorio. As oito fontes de T9 tem `verdict = NAO SEI` e `access_method =
NAO SEI`, e o executor de T9 declara `custo = «pago quando passa pela rota
Apify»`. Oito fontes nunca avaliadas, uma rota que pode gastar, zero portoes.

    FONTE DESCOBERTA -> COLETA CARA -> MUITOS BYTES
    -> DEPOIS DESCOBRIMOS QUE ELA QUASE NUNCA SERVIA.

E o que isto impede. Nao e um ranking de fontes; e uma porta antes do gasto.

A DECISAO E DO PAR (FONTE, PROPOSITO) — NUNCA DA FONTE SOZINHA
---------------------------------------------------------------
    NAO EXISTE `relevante = true` NUMA FONTE.

E a COL-LAW-038 um andar acima do item: guardar a relevancia NA fonte obriga a
escolher um dono para a verdade, e o segundo proposito que perguntar recebe a
resposta do primeiro. A mesma ARPAV pode ser ouro para T2 e ruido para T9.

    relevante para T3 · irrelevante para T9 · NAO SEI para T5
    — tres decisoes independentes, e nenhuma fala pelas outras.

O `PROPOSITO` e o territorio que o atlas e o pedido JA usam (T1..T13). Nao se
inventa aqui uma segunda taxonomia de assuntos.

⚠️ E O TERRITORIO DECLARADO NA FICHA NAO E A DECISAO
-----------------------------------------------------
`IT-T3-002` diz «fonte 002 do territorio T3». Isso e uma AFIRMACAO de quem
escreveu a ficha, nao uma avaliacao. `provas/candidatos_tematicos.py` ja o
escreveu para o documento:

    DECLARED != OBSERVED.
    SOURCE_RELEVANCE != DOCUMENT_RELEVANCE.

Esta lei le o LIVRO, e mais nada. Se lesse a ficha, 78 de 78 fontes nasciam
relevantes no proprio identificador, e o portao aprovava por convencao.

AS CINCO PALAVRAS SAO AS DA CASA, E NAO SE INVENTAM AQUI
---------------------------------------------------------
O eixo semantico da COL-LAW-038 ja existe e tem dono: `admissao/admissao.py`.
Importa-se de la, e `tests/test_relevancia_da_fonte.py` reprova se os dois
conjuntos divergirem. Mesmo eixo, outra pergunta, outro livro, outra chave.

    SIM            provou que SERVE para este proposito
    NAO            olhou-se, e provou que NAO serve para este proposito
    NAO_SEI        avaliou-se e nao deu para concluir
    NAO_SE_APLICA  a pergunta nao faz sentido para este par
    ERRO           nao foi possivel avaliar — NAO e uma rejeicao

E ha um sexto estado que NAO e um resultado, porque nao houve decisao nenhuma:

    NAO_AVALIADA   ninguem olhou. Nao esta no livro.

⚠️ AS QUATRO AUSENCIAS NAO SAO A MESMA COISA, e achata-las e o defeito que
esta lei existe para impedir:

    NAO_AVALIADA   ninguem perguntou
    NAO_SEI        perguntou-se e nao se concluiu
    ERRO           tentou-se perguntar e a pergunta rebentou
    NAO            perguntou-se, concluiu-se, e a resposta e nao

Uma so delas e um julgamento. As outras tres sao confissoes — e uma confissao
nunca vira veredito.

O QUE ESTA LEI NAO E — E QUEM E O DONO DE CADA UMA
---------------------------------------------------
    SOURCE_RELEVANCE  != ITEM_RELEVANCE      -> admissao/admissao.py
    SOURCE_RELEVANCE  != SOURCE_HEALTH       -> medidas/source_health.py · COL-LAW-028
    SOURCE_RELEVANCE  != ACCESSIBILITY       -> pedido/receitas.py::_sabe_o_caminho
                                                coleta/social_rotas.py::permitido
    SOURCE_RELEVANCE  != SOURCE_RELIABILITY  -> COL-LAW-216
    SOURCE_RELEVANCE  != COST                -> COL-LAW-018 · COL-LAW-019
    SOURCE_RELEVANCE  != COLLECTION_PRIORITY -> leis/politica_da_coleta.py
    SOURCE_RELEVANCE  != CASE_RELEVANCE      -> leis/adama_relevance.py

    CHEAP != RELEVANT · EXPENSIVE != IRRELEVANT
    ACCESSIBLE != RELEVANT · BLOCKED != IRRELEVANT
    NOT_MEASURED != NOT_RELEVANT · ERROR != REJECTED
    HTTP 200 != RELEVANT · LISTA VAZIA != IRRELEVANTE
    NO KEYWORD MATCH != NOT_RELEVANT   (COL-LAW-036)

NAO HA SCORE, E E DE PROPOSITO
-------------------------------
`leis/aprender_com_a_fonte.py` ja o escreveu: `NAO_CRIAR = (SOURCE_SCORE,
RANKING_UNICO, NOTA_DE_0_A_100)`. Esta lei obedece. Nenhum eixo entra numa
media com outro: uma media deixa uma falha grave ser compensada por tres
sucessos baratos, e a partir dai ninguem consegue discutir a decisao.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas no caminho de importacao

# O EIXO SEMANTICO VEM DO DONO DELE. Duas listas com as mesmas cinco palavras
# sao duas verdades, e a segunda envelhece calada.
from admissao import (  # noqa: E402
    SIM, NAO, NAO_SEI, NAO_SE_APLICA, ERRO, RESULTADOS,
)

CONTRATO = 'RELEVANCIA_DA_FONTE/v1'

# A VERSAO DA AVALIACAO sobe quando a REGRA muda, e vai carimbada em cada
# decisao. E o que permite dizer «reavalia so o que a versao 1 recusou» sem
# reavaliar o resto — e o que impede mudar o portao depois de ver o resultado
# sem que a mudanca apareca.
VERSAO_DA_AVALIACAO = '1'

# A versao da REGRA DO PORTAO e outra pergunta: a decisao pode ser da versao 1
# e o portao ja ir na 2. Separadas de proposito.
VERSAO_DO_PORTAO = '1'

LIVRO = os.path.join('data', 'samples', 'LIVRO-DE-RELEVANCIA-DE-FONTE.json')

# ── O SEXTO ESTADO, QUE NAO E UM RESULTADO ──────────────────────────────────
# Nao entra em RESULTADOS de proposito: nao e uma decisao que alguem tomou, e
# escrever isto no livro seria fabricar uma avaliacao que nunca aconteceu.
NAO_AVALIADA = 'NAO_AVALIADA'

# As quatro maneiras de nao ter um «sim», e o que cada uma confessa.
AUSENCIAS = {
    NAO_AVALIADA: 'ninguem olhou para este par. Nao ha linha no livro.',
    NAO_SEI: 'olhou-se e nao deu para concluir.',
    ERRO: 'tentou-se olhar e a avaliacao rebentou. NAO e uma rejeicao.',
}

# ── OS VEREDITOS DO PORTAO ──────────────────────────────────────────────────
# Tres, e nenhum e sinonimo de outro. O portao NAO devolve um booleano: um
# booleano obrigaria «nao sei» a escolher um lado, e o lado que ele escolheria
# seria sempre o «nao».
AUTORIZA = 'AUTORIZA'                  # provou que serve -> segue para o proximo portao
BARRA = 'BARRA'                        # olhou-se e nao serve para ESTE proposito
EXIGE_AVALIACAO = 'EXIGE_AVALIACAO'    # nao se sabe: nao autoriza gasto, e NAO diz nao
VEREDITOS = (AUTORIZA, BARRA, EXIGE_AVALIACAO)

# ── O QUE CONTA COMO GASTO ──────────────────────────────────────────────────
# Tres formas de gastar, e nenhuma precisa de fatura para ser cara.
#
#     ROTA PAGA        gasta dinheiro
#     COLETA RECORRENTE gasta para sempre, sozinha, sem ninguem por perto
#     COLETA TOTAL     gasta rede, disco e tempo de uma vez so
#
# A missao pediu para impedir «fonte descoberta -> coleta cara -> muitos bytes».
# Prender so o dinheiro deixaria as outras duas portas abertas.
GASTO_DINHEIRO = 'ROTA_PAGA'
GASTO_RECORRENTE = 'COLETA_RECORRENTE'
GASTO_VOLUME = 'COLETA_TOTAL'
FORMAS_DE_GASTO = (GASTO_DINHEIRO, GASTO_RECORRENTE, GASTO_VOLUME)

# A UNICA palavra que esta casa ja usa para dizer «isto nao gasta dinheiro».
# Ela vem de `pedido/receitas.py::EXECUTORES[*]['custo']`.
CUSTO_DECLARADO_GRATUITO = 'gratuito'


def custo_e_gratuito(custo) -> bool:
    """→ True SO quando o custo esta declarado, textualmente, como gratuito.

    ⚠️ FAIL-CLOSED NO DINHEIRO. «NAO SEI» nao e gratuito, `None` nao e
    gratuito, e uma palavra nova que ninguem previu tambem nao e. O custo de
    errar para o lado do «gratuito» e uma corrida paga que ninguem autorizou;
    o custo de errar para o outro lado e alguem ter de escrever uma linha.

        NAO SABER QUANTO CUSTA NAO E CUSTAR ZERO.
    """
    return isinstance(custo, str) and custo.strip().lower() == CUSTO_DECLARADO_GRATUITO


# ── A IDENTIDADE DA FONTE ───────────────────────────────────────────────────
# COL-LAW-206: tres identidades, e a URL nao e uma delas.
class SourceIdInvalido(ValueError):
    """Nao se fabrica SOURCE_ID. Para-se, e escreve-se porque."""


_PREFIXOS_DE_URL = ('http://', 'https://', 'ftp://', 'www.', '//')


def conferir_source_id(source_id) -> str:
    """→ o SOURCE_ID, ou levanta. NUNCA o inventa a partir de uma URL.

    Um endereco e onde se bate; nao e quem publica. Aceitar uma URL aqui faria
    a mesma fonte nascer duas vezes no dia em que ela mudasse de dominio — e a
    decisao antiga ficaria orfa sem ninguem reparar.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        raise SourceIdInvalido(
            'SOURCE_ID ausente. Uma decisao sem fonte nao e uma decisao: '
            'e uma opiniao sobre nada.')
    s = source_id.strip()
    baixo = s.lower()
    if any(baixo.startswith(p) for p in _PREFIXOS_DE_URL) or '/' in s:
        raise SourceIdInvalido(
            'URL NAO E SOURCE_ID (COL-LAW-206): «%s». O endereco muda e a '
            'fonte fica. Levante a ficha e use o identificador dela.' % s[:80])
    return s


# ── A DECISAO ───────────────────────────────────────────────────────────────
class DecisaoInvalida(ValueError):
    """Uma decisao que nao cumpre o contrato NAO entra no livro."""


# Os campos que a missao exige, com os nomes que esta casa ja usa.
# (`admissao.Decisao` e a irma deste contrato, um andar abaixo.)
CAMPOS_DA_DECISAO = (
    'SOURCE_ID',        # quem — nunca uma URL, nunca fabricado
    'PROPOSITO',        # para que — o territorio (T1..T13). A decisao e do PAR.
    'RESULTADO',        # uma das cinco palavras da COL-LAW-038
    'MOTIVO',           # porque, em palavras de gente
    'EVIDENCIA',        # o que se olhou — apontavel
    'AVALIADO_EM',      # quando
    'METODO',           # como
    'VERSAO',           # sob que regra
    'CORRIDA',          # em que corrida, quando houve uma
)

# EVIDENCIA obrigatoria para os dois resultados que AFIRMAM alguma coisa.
# Nao se exige para as ausencias: exigir prova de quem confessa que nao tem
# empurraria toda a gente a escrever `NAO` — que e barato e nao precisa de
# nada — em vez de `NAO_SEI`.
RESULTADOS_QUE_AFIRMAM = (SIM, NAO)


@dataclass
class Decisao:
    """Uma linha do livro. Uma por par (fonte, proposito) e por avaliacao."""

    source_id: str
    proposito: str
    resultado: str
    motivo: str
    metodo: str
    evidencia: dict = field(default_factory=dict)
    versao: str = VERSAO_DA_AVALIACAO
    corrida: str = 'NAO SEI'
    avaliado_em: str = ''

    def __post_init__(self):
        self.source_id = conferir_source_id(self.source_id)
        if self.resultado not in RESULTADOS:
            raise DecisaoInvalida(
                'resultado «%s» nao existe. Ha: %s'
                % (self.resultado, ', '.join(RESULTADOS)))
        if not str(self.proposito or '').strip():
            raise DecisaoInvalida(
                'PROPOSITO ausente. A relevancia e do PAR (fonte, proposito): '
                'sem proposito, a decisao vazaria para todos os universos.')
        if not str(self.motivo or '').strip():
            raise DecisaoInvalida(
                'MOTIVO ausente. `resultado` sem motivo e `discarded=true` '
                'outra vez (COL-LAW-042): nao diz por que, nem com que prova.')
        if not str(self.metodo or '').strip():
            raise DecisaoInvalida(
                'METODO ausente. Sem saber COMO se avaliou, nao ha como '
                'repetir a avaliacao nem como saber o que ela nao olhou.')
        if not str(self.versao or '').strip():
            raise DecisaoInvalida(
                'VERSAO ausente. E a versao que permite reabrir so o que a '
                'regra anterior recusou.')
        if self.resultado in RESULTADOS_QUE_AFIRMAM and not self.evidencia:
            raise DecisaoInvalida(
                'EVIDENCIA obrigatoria para «%s»: um SIM ou um NAO sem nada '
                'apontavel e uma opiniao com ar de medicao.' % self.resultado)
        self.avaliado_em = self.avaliado_em or datetime.now(
            timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def para_livro(self) -> dict:
        d = asdict(self)
        return {
            'SOURCE_ID': d['source_id'],
            'PROPOSITO': d['proposito'],
            'RESULTADO': d['resultado'],
            'MOTIVO': d['motivo'],
            'EVIDENCIA': d['evidencia'],
            'AVALIADO_EM': d['avaliado_em'],
            'METODO': d['metodo'],
            'VERSAO': d['versao'],
            'CORRIDA': d['corrida'],
        }


# ── A LEITURA DO ESTADO ─────────────────────────────────────────────────────
def estado(source_id: str, proposito: str, livro: list) -> dict:
    """→ o estado da relevancia do par (fonte, proposito). Le o LIVRO, e so.

    ⚠️ NAO recebe saude, nem custo, nem acesso, nem a ficha da fonte. Se
    recebesse, a primeira pressa escreveria `if health == HEALTHY: return SIM`
    e a lei inteira virava um sinonimo caro de `HTTP 200`.

    A ULTIMA DECISAO MANDA, E AS ANTERIORES FICAM. Reavaliar e legitimo;
    apagar o «nao» de ontem para o «sim» de hoje parecer sempre ter sido
    verdade nao e (COL-LAW-209).
    """
    sid = conferir_source_id(source_id)
    alvo = str(proposito or '').strip()
    linhas = [l for l in (livro or [])
              if l.get('SOURCE_ID') == sid and l.get('PROPOSITO') == alvo]
    if not linhas:
        return {
            'SOURCE_ID': sid, 'PROPOSITO': alvo,
            'ESTADO': NAO_AVALIADA,
            'PORQUE': AUSENCIAS[NAO_AVALIADA],
            'DECISAO': None,
            'HISTORICO': 0,
        }
    # ordem de chegada do livro: a ultima linha e a decisao vigente.
    vigente = linhas[-1]
    return {
        'SOURCE_ID': sid, 'PROPOSITO': alvo,
        'ESTADO': vigente.get('RESULTADO'),
        'PORQUE': vigente.get('MOTIVO'),
        'DECISAO': vigente,
        'HISTORICO': len(linhas),
    }


# ── O PORTAO ────────────────────────────────────────────────────────────────
# A TABELA DA REGRA, ESCRITA ANTES DE SE VER QUALQUER RESULTADO.
#
#     SIM            -> AUTORIZA        em todas as formas de gasto
#     NAO            -> BARRA           em todas — inclusive na rota de graca
#     NAO_SE_APLICA  -> BARRA           a pergunta nao faz sentido para o par
#     NAO_SEI        -> EXIGE_AVALIACAO
#     ERRO           -> EXIGE_AVALIACAO
#     NAO_AVALIADA   -> EXIGE_AVALIACAO
#
# ⚠️ E `BARRA` NAO E O MESMO QUE `EXIGE_AVALIACAO`. O primeiro fecha o assunto;
# o segundo diz «volte com uma avaliacao». Um sistema que respondesse a mesma
# coisa aos dois estaria a dizer «nao serve» a uma fonte que ninguem abriu.
REGRA_DO_PORTAO = {
    SIM: AUTORIZA,
    NAO: BARRA,
    NAO_SE_APLICA: BARRA,
    NAO_SEI: EXIGE_AVALIACAO,
    ERRO: EXIGE_AVALIACAO,
    NAO_AVALIADA: EXIGE_AVALIACAO,
}


def formas_de_gasto(*, custo=None, acionamento=None, escopo=None) -> list:
    """→ que formas de gasto este plano abre. Lista vazia = so observacao barata.

    NAO le relevancia nenhuma: e a pergunta oposta, e responde-se sozinha.
    """
    g = []
    if not custo_e_gratuito(custo):
        g.append(GASTO_DINHEIRO)
    if str(acionamento or '').upper() == 'AGENDADO':
        g.append(GASTO_RECORRENTE)
    if str(escopo or '').upper() == 'TOTAL':
        g.append(GASTO_VOLUME)
    return g


def portao(source_id, proposito, livro, *, custo=None, acionamento=None,
           escopo=None) -> dict:
    """O PORTAO CANONICO, ANTES DO GASTO. → o veredito, com o motivo e a prova.

    `source_id = None` e um caso legitimo e NAO e um erro: quer dizer que o
    plano nao nomeia fonte nenhuma. Nesse caso nao ha par para julgar, e um
    plano que nao nomeia a fonte nunca pode autorizar gasto sobre ela.

        NAO SE AUTORIZA GASTO SOBRE UMA FONTE QUE O PLANO NAO NOMEIA.
    """
    gastos = formas_de_gasto(custo=custo, acionamento=acionamento, escopo=escopo)

    if source_id is None:
        est = {
            'SOURCE_ID': None, 'PROPOSITO': str(proposito or '').strip(),
            'ESTADO': NAO_AVALIADA, 'DECISAO': None, 'HISTORICO': 0,
            'PORQUE': ('o plano nao nomeia a fonte: nao ha par '
                       '(fonte, proposito) para julgar.'),
        }
        veredito = EXIGE_AVALIACAO
    else:
        est = estado(source_id, proposito, livro)
        veredito = REGRA_DO_PORTAO[est['ESTADO']]

    # O veredito nao muda por causa do gasto. O que muda e a CONSEQUENCIA:
    # sem gasto aberto, `EXIGE_AVALIACAO` ainda deixa observar de graca; com
    # gasto aberto, nao deixa nada.
    #
    #     O PORTAO GUARDA O GASTO, NAO A OBSERVACAO.  (COL-LAW-018)
    pode_gastar = veredito == AUTORIZA
    pode_observar_barato = veredito != BARRA

    if veredito == AUTORIZA:
        porque = ('a fonte provou que serve para «%s», e a decisao esta no '
                  'livro com evidencia apontavel.' % est['PROPOSITO'])
    elif veredito == BARRA:
        porque = ('decisao explicita de que esta fonte NAO serve para «%s»: %s'
                  % (est['PROPOSITO'], est['PORQUE']))
    else:
        porque = ('a relevancia desta fonte para «%s» esta em %s — %s '
                  'NAO_SEI, ERRO e NAO_AVALIADA nao sao «nao»: sao confissoes, '
                  'e uma confissao nao autoriza gasto nem o condena.'
                  % (est['PROPOSITO'], est['ESTADO'], est['PORQUE']))

    return {
        'VEREDITO': veredito,
        'PORQUE': porque,
        'ESTADO_DA_RELEVANCIA': est['ESTADO'],
        'SOURCE_ID': est['SOURCE_ID'],
        'PROPOSITO': est['PROPOSITO'],
        'DECISAO': est['DECISAO'],
        'HISTORICO': est['HISTORICO'],
        'FORMAS_DE_GASTO_ABERTAS': gastos,
        'PODE_GASTAR': pode_gastar,
        'PODE_OBSERVAR_BARATO': pode_observar_barato,
        # O que o chamador tem de obedecer, dito numa palavra.
        'BLOQUEIA_A_CORRIDA': bool(gastos) and not pode_gastar,
        'VERSAO_DO_PORTAO': VERSAO_DO_PORTAO,
        'CONTRATO': CONTRATO,
    }


# ── O LIVRO ─────────────────────────────────────────────────────────────────
# Mesmo dono, mesmo ficheiro. Duas pecas a saber escrever o mesmo livro sao
# duas leis, e a segunda aprende a escrever o que a primeira recusa.
class LivroIlegivel(Exception):
    """O livro existe e nao se conseguiu ler. NAO e um livro vazio."""


def caminho_do_livro(raiz=RAIZ) -> str:
    return os.path.join(raiz, LIVRO)


def ler_livro(raiz=RAIZ) -> list:
    """→ as decisoes, em ordem de chegada. Livro que nao existe = livro vazio.

    ⚠️ MAS LIVRO ILEGIVEL NAO E LIVRO VAZIO, e a diferenca ja custou 813
    decisoes na porta de admissao (ver `admissao.escrever`). Aqui o ilegivel
    levanta, e quem levanta nao escreveu nada.
    """
    import json
    caminho = caminho_do_livro(raiz)
    if not os.path.isfile(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        bruto = f.read()
    try:
        d = json.loads(bruto)
    except json.JSONDecodeError as e:
        raise LivroIlegivel(
            '%s existe e nao e JSON valido (%s). Um livro ilegivel nao e um '
            'livro vazio: tratar os dois como o mesmo faria toda a fonte '
            'avaliada voltar a NAO_AVALIADA em silencio.' % (LIVRO, e)) from e
    if not isinstance(d, dict) or not isinstance(d.get('DECISOES', []), list):
        raise LivroIlegivel(
            '%s tem JSON valido mas nao a forma do livro (esperava um objecto '
            'com a lista DECISOES). NAO foi lido nada.' % LIVRO)
    return list(d.get('DECISOES') or [])


def registar(decisoes, raiz=RAIZ) -> int:
    """Junta ao livro. NUNCA reescreve nem apaga o que la estava.

    ⚠️ NAO HA FUNCAO DE APAGAR, E E DE PROPOSITO. Reavaliar uma fonte e
    legitimo e faz-se escrevendo POR CIMA — outra linha, com outra data e
    outra versao. Apagar o «nao» de ontem para o «sim» de hoje parecer sempre
    ter sido verdade e reescrever a historia (COL-LAW-209), e a partir dai
    ninguem consegue perguntar «o que e que a versao 1 recusou?».
    """
    import json
    linhas = [d.para_livro() if isinstance(d, Decisao) else d for d in decisoes]
    for l in linhas:
        faltam = [c for c in CAMPOS_DA_DECISAO if c not in l]
        if faltam:
            raise DecisaoInvalida(
                'linha sem os campos do contrato: %s' % ', '.join(faltam))
    caminho = caminho_do_livro(raiz)
    d = {'DATASET': 'SINTONIA-LIVRO-DE-RELEVANCIA-DE-FONTE-V1',
         'LEI': ('uma decisao por par (FONTE, PROPOSITO) e por avaliacao. '
                 'Append-only: reavaliar escreve por cima, nunca apaga.'),
         'CONTRATO': CONTRATO, 'DECISOES': []}
    if os.path.isfile(caminho):
        d_existente = {'DECISOES': ler_livro(raiz)}
        with open(caminho, encoding='utf-8') as f:
            d = json.loads(f.read())
        d['DECISOES'] = d_existente['DECISOES']
    d.setdefault('DECISOES', []).extend(linhas)
    d['TOTAL'] = len(d['DECISOES'])
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
    return len(d['DECISOES'])


# ── O QUE ESTA LEI RECUSA, DITO EM CODIGO ───────────────────────────────────
NAO_CRIAR = ('SOURCE_SCORE', 'RANKING_UNICO', 'NOTA_DE_0_A_100',
             'RELEVANTE_BOOLEANO_DA_FONTE')

LEIS = (
    'A RELEVANCIA E DO PAR (FONTE, PROPOSITO) — NUNCA DA FONTE SOZINHA',
    'NAO_AVALIADA != NAO_SEI != ERRO != NAO',
    'ERRO NAO E REJEICAO',
    'AUSENCIA DE EVIDENCIA NAO E EVIDENCIA DE AUSENCIA (COL-LAW-035)',
    'NO KEYWORD MATCH NAO E NOT_RELEVANT (COL-LAW-036)',
    'SOURCE_RELEVANCE != SOURCE_HEALTH != ACCESS != COST != PRIORITY',
    'CHEAP != RELEVANT · EXPENSIVE != IRRELEVANT',
    'UM ITEM NAO PROMOVE NEM CONDENA A FONTE INTEIRA',
    'DECLARED != OBSERVED: O TERRITORIO DA FICHA NAO E A DECISAO',
    'URL NAO E SOURCE_ID (COL-LAW-206)',
    'NAO SABER QUANTO CUSTA NAO E CUSTAR ZERO',
    'O PORTAO GUARDA O GASTO, NAO A OBSERVACAO',
    'UMA DECISAO NEGATIVA NAO SE APAGA — REAVALIA-SE POR CIMA (COL-LAW-209)',
)


def main() -> int:
    print('CONTRATO %s · portao v%s · avaliacao v%s'
          % (CONTRATO, VERSAO_DO_PORTAO, VERSAO_DA_AVALIACAO))
    print('LIVRO    %s' % LIVRO)
    print()
    print('A REGRA DO PORTAO, escrita antes de qualquer resultado:')
    for est, ver in REGRA_DO_PORTAO.items():
        print('    %-14s -> %s' % (est, ver))
    print()
    print('AS FORMAS DE GASTO que fecham a porta: %s'
          % ' · '.join(FORMAS_DE_GASTO))
    print('NAO CRIAR: %s' % ', '.join(NAO_CRIAR))
    print()
    for l in LEIS:
        print('  · %s' % l)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
