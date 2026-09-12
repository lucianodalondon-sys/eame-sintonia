#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTORIZACAO DE GASTO — nenhuma compra nasce sem uma autorizacao que se possa ler.

    import autorizacao_de_gasto as ag
    ag.conferir(ag.normal(source_id='IT-T3-005', proposito='T3'), custo='pago')

O QUE ESTA LEI E, E O QUE ELA NAO E
------------------------------------
Ela NAO julga fonte. NAO le relevancia por conta propria. NAO decide se uma
fonte serve. Quem decide isso e `leis/relevancia_da_fonte.py`, que e o dono
externo — e esta lei apenas OBEDECE ao veredito dele.

    SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER.

O dono da relevancia responde «esta fonte serve para este proposito?».
Esta lei responde uma pergunta diferente: «esta compra esta autorizada?».
Colapsa-las faria o SCRAP virar juiz de fontes, que e exactamente o que a
missao proibiu.

TRES PROPOSITOS, E ELES NAO SAO INTERCAMBIAVEIS
------------------------------------------------
    NORMAL_COLLECTION        colher de uma fonte conhecida, para um proposito
    SOURCE_EVALUATION_PROBE  abrir uma fonte que NINGUEM avaliou, para a poder avaliar
    CAPABILITY_TRIAL         provar que uma capacidade/rota/fornecedor funciona

    NORMAL_COLLECTION != SOURCE_EVALUATION_PROBE != CAPABILITY_TRIAL.

Os tres gastam dinheiro e os tres precisam de autorizacao — mas de
autorizacoes DIFERENTES, e e por isso que sao tres e nao um.

A colheita normal precisa do veredito do dono da relevancia. O probe existe
precisamente para o caso em que esse veredito ainda nao existe, e por isso nao
o pode exigir — o que ele exige e mao humana e TECTOS. O ensaio nao e sobre a
fonte de todo: e sobre a maquina.

    E A PORTA DE UM NAO ABRE A DO OUTRO. Um pedido de colheita normal que se
    declare `CAPABILITY_TRIAL` para fugir a relevancia e recusado por esta lei,
    e a recusa tem nome proprio.

PROBE != DECISION
------------------
Um probe pode abrir uma fonte desconhecida. O que ele NAO pode e escrever no
livro da relevancia. Medir nao e decidir, e quem mede nao carimba.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
for _d in (RAIZ, _HERE):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import relevancia_da_fonte as rel  # noqa: E402

CONTRATO = 'AUTORIZACAO_DE_GASTO/v1'

# ── OS TRES PROPOSITOS ──────────────────────────────────────────────────────
NORMAL = 'NORMAL_COLLECTION'
PROBE = 'SOURCE_EVALUATION_PROBE'
TRIAL = 'CAPABILITY_TRIAL'
PROPOSITOS = (NORMAL, PROBE, TRIAL)

# ── OS VEREDITOS. Vocabulario fechado, e cada palavra diz QUEM recusou. ──────
AUTORIZADO = 'AUTORIZADO'
SEM_AUTORIZACAO = 'SEM_AUTORIZACAO'              # ninguem trouxe autorizacao
BARRADO_PELA_RELEVANCIA = 'BARRADO_PELA_RELEVANCIA'   # o dono disse NAO
EXIGE_AVALIACAO = 'EXIGE_AVALIACAO_DA_FONTE'     # o dono disse «nao sei»
AUTORIZACAO_INVALIDA = 'AUTORIZACAO_INVALIDA'    # veio malformada
FORA_DO_TECTO = 'FORA_DO_TECTO'                  # probe/ensaio sem limite ou acima dele
VEREDITOS = (AUTORIZADO, SEM_AUTORIZACAO, BARRADO_PELA_RELEVANCIA,
             EXIGE_AVALIACAO, AUTORIZACAO_INVALIDA, FORA_DO_TECTO)

#: NAO SE MISTURA «NAO ME AUTORIZARAM» COM «A FONTE NAO SERVE».
#: O primeiro e uma falta nossa; o segundo e uma decisao sobre o mundo. Um
#: relatorio que os junte diz que a fonte e ma quando o que houve foi esquecimento.
NEGADOS = (SEM_AUTORIZACAO, BARRADO_PELA_RELEVANCIA, EXIGE_AVALIACAO,
           AUTORIZACAO_INVALIDA, FORA_DO_TECTO)


class AutorizacaoInvalida(ValueError):
    """A autorizacao nao respeita o contrato. NAO e o mesmo que fonte irrelevante."""


class GastoNaoAutorizado(RuntimeError):
    """Alguem tentou comprar sem autorizacao valida para AQUELA compra."""

    def __init__(self, veredito):
        self.veredito = veredito
        super().__init__('%s · %s' % (veredito['VEREDITO'], veredito['PORQUE']))


# ══════════════════════════════════════════════════════════════════════════
# AS TRES AUTORIZACOES
# ══════════════════════════════════════════════════════════════════════════
def normal(*, source_id, proposito):
    """Colheita normal: o par (fonte, proposito) que sera julgado pelo dono.

    NAO aceita URL no lugar de `source_id`. A verificacao e do dono da
    relevancia — `conferir_source_id` vive la — porque duas casas a validar o
    mesmo identificador dariam dois formatos validos.

        URL NUNCA SUBSTITUI SOURCE_ID.
    """
    return {'CONTRATO': CONTRATO, 'PROPOSITO_DO_GASTO': NORMAL,
            'SOURCE_ID': source_id, 'PROPOSITO': proposito}


def probe(*, source_id, proposito, humano, max_runs, max_posts, max_usd,
          max_items, condicao_de_paragem):
    """Probe de avaliacao: abrir uma fonte que ninguem avaliou, com tectos.

    Exige mao humana E tectos. Sem qualquer um deles nao ha probe — ha uma
    colheita normal a fingir que e outra coisa.
    """
    return {'CONTRATO': CONTRATO, 'PROPOSITO_DO_GASTO': PROBE,
            'SOURCE_ID': source_id, 'PROPOSITO': proposito,
            'HUMAN_AUTHORIZATION': humano,
            'MAX_PROVIDER_RUNS': max_runs, 'MAX_START_POSTS': max_posts,
            'MAX_USD': max_usd, 'MAX_ITEMS': max_items,
            'STOP_CONDITION': condicao_de_paragem}


def trial(*, capacidade, alvo, humano, max_runs, max_posts, max_usd, max_items,
          condicao_de_paragem):
    """Ensaio de capacidade: provar a maquina, nao a fonte.

    NAO pede relevancia, e a razao e que a pergunta nao e sobre a fonte: e
    sobre a rota, o fornecedor e o adaptador. O que ele pede em troca sao os
    mesmos tectos do probe, mais um ALVO FIXO — um ensaio sem alvo escrito e
    uma coleta com outro nome.
    """
    return {'CONTRATO': CONTRATO, 'PROPOSITO_DO_GASTO': TRIAL,
            'CAPACIDADE': capacidade, 'ALVO': alvo,
            'HUMAN_AUTHORIZATION': humano,
            'MAX_PROVIDER_RUNS': max_runs, 'MAX_START_POSTS': max_posts,
            'MAX_USD': max_usd, 'MAX_ITEMS': max_items,
            'STOP_CONDITION': condicao_de_paragem}


# ══════════════════════════════════════════════════════════════════════════
# A GUARDA
# ══════════════════════════════════════════════════════════════════════════
#: Os tectos que um probe e um ensaio tem de trazer. Faltar UM chega para
#: recusar: um tecto pela metade e um tecto que nao existe.
TECTOS = ('MAX_PROVIDER_RUNS', 'MAX_START_POSTS', 'MAX_USD', 'MAX_ITEMS')


def _tectos_validos(a):
    """Os quatro tectos existem e sao numeros positivos? → (bool, motivo)."""
    for t in TECTOS:
        v = a.get(t)
        if v is None:
            return False, 'falta o tecto %s' % t
        try:
            n = float(v)
        except (TypeError, ValueError):
            return False, '%s nao e numero: %r' % (t, v)
        if n <= 0:
            return False, '%s = %s. Um tecto de zero nao limita: proibe.' % (t, v)
    if not str(a.get('STOP_CONDITION') or '').strip():
        return False, 'falta STOP_CONDITION — um limite sem condicao de paragem'
    if not str(a.get('HUMAN_AUTHORIZATION') or '').strip():
        return False, 'falta HUMAN_AUTHORIZATION — nenhuma mao humana assinou'
    return True, None


def _veredito(v, porque, aut, extra=None):
    d = {'VEREDITO': v, 'PORQUE': porque, 'CONTRATO': CONTRATO,
         'PROPOSITO_DO_GASTO': (aut or {}).get('PROPOSITO_DO_GASTO'),
         'PODE_COMPRAR': v == AUTORIZADO}
    if extra:
        d.update(extra)
    return d


def conferir(autorizacao, *, custo=None, acionamento=None, escopo=None,
             livro=None, raiz=RAIZ, source_id_pedido=None, proposito_pedido=None):
    """A GUARDA. → veredito. NUNCA levanta por recusa: recusa e resultado.

    `source_id_pedido` e `proposito_pedido` sao o que a EXECUCAO vai realmente
    fazer. Eles existem porque uma autorizacao para (A, T3) nao autoriza uma
    corrida contra (B, T3) nem contra (A, T9) — e sem os comparar, a guarda
    verificaria o papel em vez da compra.

        AUTORIZACAO NAO E UM CARIMBO: E UM PAR.
    """
    if autorizacao is None:
        return _veredito(SEM_AUTORIZACAO,
                         'nenhuma autorizacao foi apresentada para esta compra',
                         None)
    if not isinstance(autorizacao, dict):
        return _veredito(AUTORIZACAO_INVALIDA,
                         'a autorizacao nao e um registo do contrato %s' % CONTRATO,
                         None)
    if autorizacao.get('CONTRATO') != CONTRATO:
        return _veredito(AUTORIZACAO_INVALIDA,
                         'contrato %r nao e %s' % (autorizacao.get('CONTRATO'), CONTRATO),
                         autorizacao)
    prop = autorizacao.get('PROPOSITO_DO_GASTO')
    if prop not in PROPOSITOS:
        return _veredito(AUTORIZACAO_INVALIDA,
                         'proposito %r fora de %s' % (prop, ', '.join(PROPOSITOS)),
                         autorizacao)

    # ── ENSAIO DE CAPACIDADE ────────────────────────────────────────────────
    # Nao pede relevancia porque nao e sobre a fonte. Pede tectos e alvo fixo.
    if prop == TRIAL:
        ok, porque = _tectos_validos(autorizacao)
        if not ok:
            return _veredito(FORA_DO_TECTO, 'ensaio sem limite: %s' % porque, autorizacao)
        if not str(autorizacao.get('ALVO') or '').strip():
            return _veredito(FORA_DO_TECTO,
                             'ensaio sem ALVO fixo e uma coleta com outro nome',
                             autorizacao)
        # ⚠️ E AQUI ESTA A PORTA QUE NAO PODE ABRIR.
        # Se a execucao nomeia uma FONTE, ela nao e um ensaio de capacidade —
        # e uma colheita. Deixar passar seria dar a toda a gente uma forma de
        # contornar a relevancia escrevendo `mode=TRIAL`.
        #
        #     NORMAL_COLLECTION NAO PODE VESTIR-SE DE CAPABILITY_TRIAL.
        if source_id_pedido:
            return _veredito(AUTORIZACAO_INVALIDA,
                             'a execucao nomeia a fonte %r: isso e colheita normal, e '
                             'colheita normal precisa do veredito do dono da relevancia. '
                             'Um ensaio de capacidade prova a maquina, nao a fonte.'
                             % source_id_pedido,
                             autorizacao)
        return _veredito(AUTORIZADO,
                         'ensaio de capacidade autorizado por mao humana, com alvo fixo '
                         'e os quatro tectos declarados', autorizacao)

    # ── DAQUI PARA BAIXO HA FONTE, E ELA TEM DE BATER CERTO ─────────────────
    sid = autorizacao.get('SOURCE_ID')
    pro = autorizacao.get('PROPOSITO')
    try:
        sid = rel.conferir_source_id(sid)
    except rel.SourceIdInvalido as e:
        return _veredito(AUTORIZACAO_INVALIDA, str(e), autorizacao)
    if not str(pro or '').strip():
        return _veredito(AUTORIZACAO_INVALIDA,
                         'a autorizacao nao nomeia o PROPOSITO', autorizacao)

    # A autorizacao e um PAR, e a compra tem de ser o MESMO par.
    if source_id_pedido is not None and str(source_id_pedido) != sid:
        return _veredito(AUTORIZACAO_INVALIDA,
                         'autorizacao para a fonte %r e a corrida e contra %r'
                         % (sid, source_id_pedido), autorizacao)
    if proposito_pedido is not None and str(proposito_pedido).strip() != str(pro).strip():
        return _veredito(AUTORIZACAO_INVALIDA,
                         'autorizacao para o proposito %r e a corrida e para %r'
                         % (pro, proposito_pedido), autorizacao)

    # ── PROBE DE AVALIACAO ──────────────────────────────────────────────────
    # Existe para o caso em que o dono AINDA NAO decidiu. Logo nao pode exigir
    # a decisao — o que exige sao tectos e mao humana.
    if prop == PROBE:
        ok, porque = _tectos_validos(autorizacao)
        if not ok:
            return _veredito(FORA_DO_TECTO, 'probe sem limite: %s' % porque, autorizacao)
        return _veredito(AUTORIZADO,
                         'probe de avaliacao autorizado por mao humana, com os quatro '
                         'tectos e condicao de paragem declarados', autorizacao,
                         {'SOURCE_ID': sid, 'PROPOSITO': pro})

    # ── COLHEITA NORMAL — O DONO DA RELEVANCIA DECIDE, NAO ESTA LEI ─────────
    if livro is None:
        try:
            livro = rel.ler_livro(raiz)
        except rel.LivroIlegivel as e:
            # LIVRO ILEGIVEL NAO E LIVRO VAZIO. Um livro que nao se conseguiu
            # ler nao autoriza nada, e tambem nao condena a fonte.
            return _veredito(EXIGE_AVALIACAO,
                             'o livro da relevancia existe e nao se conseguiu ler: %s' % e,
                             autorizacao, {'SOURCE_ID': sid, 'PROPOSITO': pro})
    p = rel.portao(sid, pro, livro, custo=custo, acionamento=acionamento, escopo=escopo)
    if p['VEREDITO'] == rel.AUTORIZA:
        return _veredito(AUTORIZADO, p['PORQUE'], autorizacao,
                         {'SOURCE_ID': sid, 'PROPOSITO': pro,
                          'ESTADO_DA_RELEVANCIA': p['ESTADO_DA_RELEVANCIA'],
                          'DECISAO': p['DECISAO']})
    # E as duas recusas do dono NAO se escrevem com a mesma palavra: uma fecha
    # o assunto, a outra pede uma avaliacao que ninguem fez.
    v = BARRADO_PELA_RELEVANCIA if p['VEREDITO'] == rel.BARRA else EXIGE_AVALIACAO
    return _veredito(v, p['PORQUE'], autorizacao,
                     {'SOURCE_ID': sid, 'PROPOSITO': pro,
                      'ESTADO_DA_RELEVANCIA': p['ESTADO_DA_RELEVANCIA']})


def exigir(autorizacao, **kw):
    """Como `conferir`, mas levanta `GastoNaoAutorizado` quando nao autoriza.

    E esta que o dono da compra chama: no ponto onde o dinheiro nasce, uma
    recusa TEM de parar o programa — devolver um dicionario e esperar que
    alguem o leia e como pedir por favor.
    """
    v = conferir(autorizacao, **kw)
    if v['VEREDITO'] != AUTORIZADO:
        raise GastoNaoAutorizado(v)
    return v


LEIS = (
    'SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER',
    'NORMAL_COLLECTION != SOURCE_EVALUATION_PROBE != CAPABILITY_TRIAL',
    'URL NUNCA SUBSTITUI SOURCE_ID',
    'AUTORIZACAO NAO E UM CARIMBO: E UM PAR (FONTE, PROPOSITO)',
    'PROBE != DECISION — quem mede nao carimba',
    'UM TECTO PELA METADE E UM TECTO QUE NAO EXISTE',
    'LIVRO ILEGIVEL != LIVRO VAZIO',
)
