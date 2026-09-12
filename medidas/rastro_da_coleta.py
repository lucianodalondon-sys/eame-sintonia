#!/usr/bin/env python3
"""O DONO DO RASTRO — quem registra o que passou por cada etapa, e o le de volta.

    UMA COLETA NAO E SO «RODOU».
    ELA PRECISA PODER RESPONDER: POR QUE RODOU? O QUE ENTROU? O QUE SAIU?
    O QUE NAO SAIU, E POR QUE? ONDE PAROU? QUANTO CUSTOU? ONDE RETOMAR?

O QUE ESTE MODULO NAO E DONO
-----------------------------
    RUN          `collection_run` — e ele que este rastro referencia
    RAW          o dono forward do G-42
    CHECKPOINT   `coleta/coleta_checkpoint.py`
    FALHA        `leis/falhas.py`
    DIAGNOSTICO  `leis/diagnostico.py`

Nao ha corrida nova aqui. `abrir()` exige um `run_id` que ja existe em
`collection_run`, e o banco recusa se nao existir — duas corridas paralelas
divergiriam na primeira pressa.

A CONTABILIDADE E A PARTE QUE IMPORTA
--------------------------------------
    NAO E OBRIGATORIO QUE 100% CHEGUE AO FIM.
    E OBRIGATORIO QUE 100% TENHA EXPLICACAO.

Cada passagem declara em que balde cada item terminou. `accounted` e
`unaccounted` sao colunas GERADAS pelo banco: ninguem as escreve, e por isso
ninguem pode fazer a conta fechar sem que ela feche.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import diagnostico as dg    # noqa: E402
import falhas               # noqa: E402
import telemetria as tel    # noqa: E402

# ⚠️ O WRITER NAO E DONO DO VOCABULARIO. ELE IMPORTA-O.
# Ate O8C este ficheiro declarava a sua propria tupla ESTADOS, com sete nomes
# escritos a mao. Era a TERCEIRA copia do mesmo vocabulario — contrato, banco e
# writer — e nada obrigava as tres a concordar. Uma copia que ninguem obriga a
# concordar acaba a discordar, e o dia em que discordar ninguem vai saber qual
# das tres estava certa.
ESTADOS = tel.ESTADOS_DE_ETAPA
DESTINOS = tel.DESTINOS_DO_ITEM

PASS = 'PASS'
FAIL = 'FAIL'
NOT_RUN = 'NOT_RUN'
RUNNING = 'RUNNING'
PARTIAL = 'PARTIAL'
SKIPPED = 'SKIPPED'
NOT_APPLICABLE = 'NOT_APPLICABLE'

# ⚠️ A QUARTA COPIA, FECHADA EM O9R. Ate aqui este ficheiro escrevia as nove
# etapas a mao — era a mesma especie de defeito que o O8C desfez nos ESTADOS e
# nos DESTINOS, e ficou de fora so porque ninguem tinha olhado para ela.
ETAPAS = tel.ETAPAS_DA_COLETA

# A ordem importa para «onde retomar»: o ultimo PASS na ordem canonica e o
# ultimo ponto bom, e as etapas depois dele ficam NOT_RUN — nunca REJECTED.
ORDEM = {e: i for i, e in enumerate(ETAPAS)}

# Corridas anteriores a este instrumento nao tem rastro, e nao se inventa um.
SEM_INSTRUMENTO = 'HISTORICAL_UNINSTRUMENTED'


def _lit(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


# ═════════════════════════════════════════════════════════════════════════
# ESCREVER
# ═════════════════════════════════════════════════════════════════════════
def registrar(banco, *, run_id, etapa, estado, edge_from=None, tentativa=0,
              source_id=None, route_class_id=None, decision_id=None,
              raw_asset_id=None,
              input_grain=None, input_count=None,
              output_grain=None, output_count=None, cardinalidade=None,
              passed=0, rejected=0, error=0, not_run=0, unknown=0, reused=0,
              custo_usd=None, duracao_ms=None, actor=None, actor_version=None,
              policy_version=None, diagnostic_code=None, canonical_state=None,
              error_class=None, error_message=None, http_status=None,
              last_good_artifact=None, checkpoint_before=None,
              checkpoint_after=None):
    """Uma passagem. Devolve o que o banco calculou, nao o que pedimos.

    `diagnostic_code` nao precisa vir pronto: quando o estado e FAIL e ninguem
    o forneceu, ele e derivado da ETAPA mais o estado canonico — porque a mesma
    falha em etapas diferentes manda a pessoa a sitios diferentes.

    A mensagem de erro passa por `falhas`/redacao antes de entrar. Um traceback
    pode carregar uma chave, e o rastro e para ser lido por gente.
    """
    assert estado in ESTADOS, 'estado fora do vocabulario: %s' % estado
    assert etapa in ETAPAS, 'etapa fora do vocabulario: %s' % etapa
    if estado == FAIL and not diagnostic_code:
        diagnostic_code = dg.da_etapa(etapa, canonical_state)
    if diagnostic_code:
        assert dg.valido(diagnostic_code), 'codigo fora do registry: %s' % diagnostic_code
    # ⚠️ O ESTADO CANONICO TAMBEM TEM DONO, E ELE E `falhas.py`.
    # Sem esta trava, um emissor escreveu `canonical_state='ERROR'` — que e um
    # DESTINO DE ITEM, nao um estado de falha — e a linha entrou calada. O
    # leitor via um estado que o dono nunca declarou.
    if canonical_state is not None:
        assert canonical_state in falhas.ESTADOS, (
            'estado canonico fora de falhas.py: %s' % canonical_state)
    if input_count is not None and not input_grain:
        raise ValueError('%s: ha contagem de entrada sem GRAO declarado. '
                         'Contagem sem grao nao se compara com contagem.' % etapa)
    if output_count is not None and not output_grain:
        raise ValueError('%s: ha contagem de saida sem GRAO declarado.' % etapa)

    # ⚠️ SO O RAW NOMEIA A OBSERVACAO, e o banco tem a mesma trava (028).
    # Uma linha de DERIVED que apontasse para `raw_asset` estaria a assinar o
    # trabalho da etapa anterior. Recusar aqui da o nome antes de o banco dar
    # um erro de constraint.
    if raw_asset_id is not None and etapa != 'RAW':
        raise ValueError('so a etapa RAW nomeia a observacao: %s pediu '
                         'raw_asset_id=%r' % (etapa, raw_asset_id))

    colunas = {
        'run_id': run_id, 'decision_id': decision_id, 'source_id': source_id,
        'raw_asset_id': raw_asset_id,
        'route_class_id': route_class_id, 'etapa': etapa, 'edge_from': edge_from,
        'tentativa': tentativa, 'input_grain': input_grain,
        'input_count': input_count, 'output_grain': output_grain,
        'output_count': output_count, 'cardinalidade': cardinalidade,
        'passed': passed, 'rejected': rejected, 'error_count': error,
        'not_run_count': not_run, 'unknown_count': unknown,
        'reused': reused, 'estado': estado,
        'custo_usd': custo_usd, 'duracao_ms': duracao_ms, 'actor': actor,
        'actor_version': actor_version, 'policy_version': policy_version,
        'diagnostic_code': diagnostic_code, 'canonical_state': canonical_state,
        'error_class': error_class,
        'error_message_redacted': _redigir(error_message),
        'http_status': http_status, 'last_good_artifact': last_good_artifact,
        'checkpoint_before': checkpoint_before, 'checkpoint_after': checkpoint_after,
    }
    nomes = [k for k, v in colunas.items() if v is not None]
    sql = ("insert into public.etapa_da_corrida (%s) values (%s)"
           " returning accounted_input, unaccounted_input, estado, diagnostic_code"
           % (', '.join(nomes),
              ', '.join(_lit(colunas[k]) if k != 'estado' and k != 'etapa'
                        and k != 'edge_from'
                        else "%s::%s" % (_lit(colunas[k]),
                                         'etapa_estado' if k == 'estado' else 'etapa_da_coleta')
                        for k in nomes)))
    linha = banco.executa(sql)[0]
    return {'ACCOUNTED_INPUT': int(linha[0]) if linha[0] else 0,
            'UNACCOUNTED_INPUT': int(linha[1]) if linha[1] else 0,
            'ESTADO': linha[2], 'DIAGNOSTIC_CODE': linha[3] or None}


def _uma_linha(texto):
    """Uma mensagem de erro nao pode partir o leitor do rastro.

    ⚠️ MEDIDO NA M2: o `psql` devolve o erro em VARIAS linhas e com `|`, que e
    o separador do leitor. Uma delas entrou no rastro e a leitura seguinte
    partiu as colunas ao meio — `KeyError: DURACAO_MS`. O retrato da falha
    estragava a leitura de TODAS as passagens da corrida, inclusive as boas.

        UMA FALHA NAO PODE APAGAR O RELATO DAS QUE CORRERAM BEM.
    """
    return ' · '.join(str(texto).replace('|', '/').split())


def _redigir(msg):
    """Nenhum segredo entra no rastro. O rastro e para ser lido."""
    if not msg:
        return None
    try:
        import social_sessao as ss
        return _uma_linha(ss.redigir(str(msg)))[:400]
    except Exception:                                        # noqa: BLE001
        return _uma_linha(msg)[:400]


# ═════════════════════════════════════════════════════════════════════════
# LER
# ═════════════════════════════════════════════════════════════════════════
def passagens(banco, *, run_id):
    linhas = banco.executa(
        "select etapa::text, coalesce(edge_from::text,'-'), estado::text,"
        " coalesce(source_id,'-'), coalesce(route_class_id,'-'),"
        " coalesce(input_grain,'-'), coalesce(input_count,-1),"
        " coalesce(output_grain,'-'), coalesce(output_count,-1),"
        " passed, rejected, error_count, not_run_count, unknown_count, reused,"
        " accounted_input, unaccounted_input,"
        " coalesce(diagnostic_code,'-'), coalesce(canonical_state,'-'),"
        " coalesce(error_class,'-'), coalesce(error_message_redacted,'-'),"
        " coalesce(actor,'-'), coalesce(actor_version,'-'),"
        " coalesce(last_good_artifact,'-'),"
        " coalesce(duracao_ms,0), coalesce(custo_usd,0), tentativa, '#'"
        " from public.etapa_da_corrida where run_id = %s"
        " order by tentativa, id" % _lit(run_id))
    # A ORDEM E A DO SELECT, e os nomes dos baldes sao os DESTINOS do contrato.
    campos = ('ETAPA', 'EDGE_FROM', 'ESTADO',
              # ⚠️ A ROTA TAMBEM VOLTA, E ELA FALTAVA.
              # O writer guardava `source_id` e `route_class_id`; o leitor nao
              # os devolvia. E a mesma especie de defeito que ja foi corrigido
              # aqui para `canonical_state`, `actor` e `actor_version` — este
              # ficou de fora, e sem ele NAO SE CONSEGUE PERGUNTAR AO BANCO
              # «esta passagem e de que rota?». O portao da M2 tinha de
              # acreditar no que o ledger DECLARA, em vez de conferir o que o
              # banco MEDIU.
              'SOURCE_ID', 'ROUTE_CLASS_ID',
              'INPUT_GRAIN', 'INPUT_COUNT',
              'OUTPUT_GRAIN', 'OUTPUT_COUNT',
              'PASSED', 'REJECTED', 'ERROR', 'NOT_RUN', 'UNKNOWN', 'REUSED',
              'ACCOUNTED', 'UNACCOUNTED', 'DIAGNOSTIC_CODE',
              # ⚠️ O SNAPSHOT PRECISA DAS DUAS RESPOSTAS, E DE QUEM CORREU.
              # Ate O9 o leitor devolvia so o DIAGNOSTIC_CODE: o writer
              # guardava o estado canonico, o actor e a versao, e ninguem os
              # conseguia ler de volta. Um retrato da falha a que falta «qual
              # versao do actor» nao responde a pergunta que se faz as tres da
              # manha.
              'CANONICAL_STATE', 'ERROR_CLASS', 'ERROR_MESSAGE',
              'ACTOR', 'ACTOR_VERSION',
              'LAST_GOOD_ARTIFACT', 'DURACAO_MS', 'CUSTO_USD', 'TENTATIVA')
    saida = []
    for l in linhas:
        d = dict(zip(campos, l[:len(campos)]))
        for k in (('INPUT_COUNT', 'OUTPUT_COUNT') + DESTINOS +
                  ('ACCOUNTED', 'UNACCOUNTED', 'DURACAO_MS', 'TENTATIVA')):
            d[k] = int(d[k])
        for k in ('EDGE_FROM', 'SOURCE_ID', 'ROUTE_CLASS_ID',
                  'INPUT_GRAIN', 'OUTPUT_GRAIN', 'DIAGNOSTIC_CODE',
                  'CANONICAL_STATE', 'ERROR_CLASS', 'ERROR_MESSAGE', 'ACTOR',
                  'ACTOR_VERSION', 'LAST_GOOD_ARTIFACT'):
            d[k] = None if d[k] == '-' else d[k]
        for k in ('INPUT_COUNT', 'OUTPUT_COUNT'):
            d[k] = None if d[k] == -1 else d[k]
        saida.append(d)
    return saida


# ═════════════════════════════════════════════════════════════════════════
# A IDENTIDADE DA ROTA, E O QUE ELA ATRAVESSOU DE VERDADE
# ═════════════════════════════════════════════════════════════════════════
#
#     DECLARED EDGE  !=  OBSERVED EDGE.
#
# ⚠️ NAO SE INVENTOU UM `ROUTE_ID`. A `024` ja declara qual e a chave da rota,
# e declara-a onde ela e usada: `v_saude_da_rota` agrupa por
# `(source_id, route_class_id)`, e o comentario da view diz porque — «a saude
# e do par (fonte, rota)». Um identificador novo seria uma SEGUNDA identidade,
# e as duas divergiriam no dia em que alguem escrevesse uma e lesse a outra.
def identidade_da_rota(passagem):
    """O par (fonte, rota) desta passagem, ou `None` se ela nao o declara.

    `None` NAO e um valor de rota: e a ausencia dele. Uma passagem anonima nao
    pertence a rota nenhuma para efeitos de cobertura, e conta-la a favor da
    rota que da jeito seria dar-lhe uma prova que ela nao tem.
    """
    fonte = passagem.get('SOURCE_ID')
    rota = passagem.get('ROUTE_CLASS_ID')
    if not fonte or not rota:
        return None
    return (fonte, rota)


def o_que_a_rota_observou(passagens_da_corrida, rota):
    """As etapas e as ARESTAS que ESTA rota atravessou — lidas do banco.

    ⚠️ ETAPA OBSERVADA E ETAPA QUE ACONTECEU, e nao etapa que tem linha.
    `NOT_RUN`, `SKIPPED` e `NOT_APPLICABLE` deixam linha e nao sao passagem. Se
    contassem, bastava escrever uma linha vazia para uma rota parecer coberta.

    ⚠️ E UMA ARESTA SO E OBSERVADA COM OS DOIS TOPOS.
    Uma passagem que diz `edge_from='DERIVED'` esta a DECLARAR de onde veio.
    Isso e a intencao de quem escreveu a linha — nao a prova de que a etapa de
    cima aconteceu nesta rota. Medido: na corrida que provava a rota da M2, o
    `STRUCTURED` declarava vir de `DERIVED` e NAO havia passagem de `DERIVED`
    nenhuma naquela corrida; a etapa tinha corrido noutra, noutro ficheiro.

        UMA SETA DESENHADA NAO E UM CAMINHO PERCORRIDO.

    Por isso a aresta so entra em `ARESTAS` quando a etapa de origem TAMBEM
    aconteceu nesta rota. O que foi apenas declarado fica em
    `ARESTAS_DECLARADAS_SEM_TOPO` — visivel, e nao contado.
    """
    minhas = [p for p in passagens_da_corrida
              if identidade_da_rota(p) == tuple(rota)]
    aconteceram = {p['ETAPA'] for p in minhas
                   if p.get('ESTADO') in ('PASS', 'PARTIAL')}
    declaradas = {(p['EDGE_FROM'], p['ETAPA']) for p in minhas
                  if p.get('EDGE_FROM') and p.get('ESTADO') in ('PASS', 'PARTIAL')}
    observadas = {(de, para) for de, para in declaradas if de in aconteceram}
    return {'ROTA': tuple(rota),
            'ETAPAS': aconteceram,
            'ARESTAS': observadas,
            'ARESTAS_DECLARADAS_SEM_TOPO': declaradas - observadas,
            'PASSAGENS': len(minhas)}


def rotas_da_corrida(passagens_da_corrida):
    """As rotas que deixaram passagem nesta corrida, sem as anonimas."""
    return sorted({r for r in (identidade_da_rota(p)
                               for p in passagens_da_corrida) if r})


def ultimo_bom(passagens_da_corrida):
    """A ultima etapa que passou. E daqui que uma retomada parte.

    Nao e «a ultima linha»: e a ultima que PASSOU na ordem canonica. Uma etapa
    depois de um erro fica NOT_RUN, e NOT_RUN nunca e ponto bom.
    """
    boas = [p for p in passagens_da_corrida if p['ESTADO'] == PASS]
    if not boas:
        return None
    return max(boas, key=lambda p: ORDEM.get(p['ETAPA'], -1))['ETAPA']


def onde_retomar(passagens_da_corrida):
    """A etapa que falhou — e so ela. Refazer o que ja passou e pagar duas vezes."""
    erros = [p for p in passagens_da_corrida if p['ESTADO'] == FAIL]
    if not erros:
        return None
    return min(erros, key=lambda p: ORDEM.get(p['ETAPA'], 99))['ETAPA']


def integridade(passagens_da_corrida):
    """UNACCOUNTED_INPUT = 0 e o alvo. Qualquer outro numero e defeito."""
    sem_explicacao = sum(p['UNACCOUNTED'] for p in passagens_da_corrida)
    etapas = [p['ETAPA'] for p in passagens_da_corrida if p['UNACCOUNTED']]
    return {
        'UNACCOUNTED_INPUT': sem_explicacao,
        'INTEGRO': sem_explicacao == 0,
        'DIAGNOSTIC_CODE': None if sem_explicacao == 0 else dg.FLOW_UNACCOUNTED_INPUT,
        'ETAPAS_COM_BURACO': etapas,
    }


def rendimento(p):
    """O rendimento de uma passagem — ou a recusa de o calcular.

        100 DOCUMENTOS -> 250 ALEGACOES NAO E 250% DE RENDIMENTO.

    Quando o grao muda, a razao entre as contagens nao e rendimento: e a
    cardinalidade da transformacao. Devolver um numero ali seria publicar uma
    percentagem que nao existe.
    """
    if not p.get('INPUT_COUNT') or p.get('OUTPUT_COUNT') is None:
        return {'YIELD': None, 'PORQUE': 'sem contagem dos dois lados'}
    if p.get('INPUT_GRAIN') != p.get('OUTPUT_GRAIN'):
        return {'YIELD': None,
                'GRAIN_CHANGED': True,
                'INPUT': '%d %s' % (p['INPUT_COUNT'], p['INPUT_GRAIN']),
                'OUTPUT': '%d %s' % (p['OUTPUT_COUNT'], p['OUTPUT_GRAIN']),
                'PORQUE': ('o grao mudou de %s para %s: a razao entre eles nao e '
                           'rendimento, e publicar uma percentagem aqui seria '
                           'inventar um numero' % (p['INPUT_GRAIN'], p['OUTPUT_GRAIN']))}
    return {'YIELD': round(p['OUTPUT_COUNT'] / p['INPUT_COUNT'], 4),
            'GRAIN_CHANGED': False}


if __name__ == '__main__':
    print(__doc__)
