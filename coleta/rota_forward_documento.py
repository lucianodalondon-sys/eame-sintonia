#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A M2 — a primeira rota forward que atravessa DERIVED → STRUCTURED → ADMISSION.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

O censo mediu, e a resposta foi a boa: as TRES pecas ja existiam, e nenhuma
estava ligada a seguinte. Esta rota nao implementa nada de novo — ela COSE.

    DERIVED      coleta/derivacao_forward.py       ja instrumentado em O9R
    STRUCTURED   coleta/social_persistencia.py     o dono de `public.conteudo`
    ADMISSION    admissao/admissao.py              a peneira comum

    A M2 PODE CRIAR A COSTURA. NAO PODE CRIAR UMA SEGUNDA IMPLEMENTACAO
    DAS MESMAS DECISOES.

O que ELA acrescenta e o que nenhuma das tres podia saber sozinha: que sao a
mesma unidade de trabalho, e que essa unidade deixa rastro.

O QUE ESTA ROTA NAO FAZ, E POR QUE
-----------------------------------
NAO emite `RAW`. Quem escreve `raw_asset` e `guarda/preservar_coleta.py`, e ler
a linha de outro nao e ter corrido a etapa dele.

NAO emite `READY`. A COL-LAW-043 diz que READY significa CONTRATOS OBRIGATORIOS
satisfeitos, e o contrato de saida exige `ADMITIDO_POR`. Uma porta que disse SIM
nao e a lei de READY cumprida — e so a porta a dizer sim.

    ADMISSION PASS != READY PASS.

A M2 termina em ADMISSION, e terminar em ADMISSION e a verdade.

A TELEMETRIA NASCE JUNTO
------------------------
Nao se construiu a costura primeiro para a instrumentar depois. Cada etapa
escreve a sua passagem no mesmo ato em que acontece — e quando nao ha o que
medir, escreve-se NULL, nunca zero.

    100% NAO SIGNIFICA 100% PASS. SIGNIFICA 100% ACCOUNTED FOR.
"""
from __future__ import annotations

import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                      # noqa: E402,F401
import admissao                      # noqa: E402
import derivacao_forward as deriv     # noqa: E402
import diagnostico as dg             # noqa: E402
import falhas                        # noqa: E402
import rastro_da_coleta as rastro    # noqa: E402
import social_persistencia as sp     # noqa: E402

# ── OS GRAOS ─────────────────────────────────────────────────────────────
# O grao muda em cada aresta, e por isso nenhuma razao entre entrada e saida e
# rendimento. Isto nao e detalhe: e a diferenca entre «43 de 49» e «49 caminhos
# viraram 43 conteudos porque seis estavam guardados duas vezes».
GRAO_DERIVADO = 'artefato derivado'
GRAO_REGISTO = 'registo estruturado'
GRAO_DECISAO = 'decisao de admissao'

POLICY_VERSION = 'm2:rota-forward-documento'

# O universo da peneira. Vem de fora quando o chamador o souber; nao se inventa.
UNIVERSO_PADRAO = 'T3'   # praga e doenca — o universo dos boletins agrometeorologicos


def _ms(t0):
    return int((time.time() - t0) * 1000)


def _tentativa(banco, run_id, etapa):
    """A proxima tentativa desta etapa nesta corrida.

    ⚠️ Fixar `tentativa=0` faria a SEGUNDA passagem colidir na chave
    (run_id, etapa, tentativa) — e o erro do banco subiria com o mesmo tipo do
    erro do fluxo. Uma falha que nao deixa linha e a que ninguem vai procurar.
    """
    try:
        r = banco.executa(
            "select coalesce(max(tentativa), -1) from public.etapa_da_corrida"
            " where run_id = %s and etapa = %s"
            % (rastro._lit(run_id), rastro._lit(etapa)))
        return int(r[0][0]) + 1
    except Exception:
        return 0


def _identidade(unidade):
    """A identidade acompanha a UNIDADE DE TRABALHO, e nao a corrida.

    Se a unidade prova `source_id` e `route_class_id`, usam-se. Se nao prova,
    ficam NULL — e `etapa_da_corrida` aceita NULL nos dois de proposito.

        UNKNOWN HONESTO > ID INVENTADO.
    """
    return {'source_id': unidade.get('SOURCE_ID'),
            'route_class_id': unidade.get('ROUTE_CLASS_ID')}


def estruturar(banco, *, unidade, run_id, canal_id, tentativa=None):
    """STRUCTURED — o texto derivado vira registo, pelo dono de `conteudo`.

    Devolve o recibo do dono. Esta funcao NAO escreve `conteudo`: ela chama
    quem escreve, e conta o que aconteceu.
    """
    t0 = time.time()
    comum = dict(_identidade(unidade), run_id=run_id, actor='social_persistencia',
                 actor_version=sp.CORPO_VERSAO, policy_version=POLICY_VERSION)
    tentativa = _tentativa(banco, run_id, 'STRUCTURED') if tentativa is None \
        else tentativa
    try:
        recibo = sp.persistir_video(
            banco, canal_id=canal_id, run_id=run_id,
            content_id=unidade['CONTENT_ID'],
            texto_canonico=unidade['TEXTO'],
            # ⚠️ RAW VEM ANTES DE CONTEUDO, e o dono recusa sem esta prova.
            raw_durou=bool(unidade.get('RAW_ASSET_ID')),
            rule_version=unidade.get('RULE_VERSION', 'v1'),
            tipo=unidade.get('TIPO', 'nota_tecnica'))
    except Exception as erro:
        rastro.registrar(
            banco, etapa='STRUCTURED', edge_from='DERIVED', estado='FAIL',
            tentativa=tentativa,
            input_grain=GRAO_DERIVADO, input_count=1,
            error=1, duracao_ms=_ms(t0),
            canonical_state='UNKNOWN_ERROR',
            diagnostic_code=dg.STRUCTURED_NOT_CONNECTED,
            error_class=type(erro).__name__, error_message=str(erro),
            last_good_artifact='DERIVED', **comum)
        raise

    # O recibo do dono decide o destino do item — a costura nao re-julga.
    estado = recibo.get('STATE')
    if estado == 'OK':
        baldes, etapa_estado = {'passed': 1}, 'PASS'
    elif estado == sp.REOBSERVADO:
        # Ja estava la, com prova de igualdade. REUSED, e nao PASSED novo.
        baldes, etapa_estado = {'reused': 1}, 'PASS'
    elif estado == sp.RAW_NAO_DUROU:
        # NAO e erro nosso: e o item que nao cumpre a pre-condicao da cadeia.
        baldes, etapa_estado = {'rejected': 1}, 'PASS'
    else:
        # Divergencia de corpo, ou qualquer estado que o dono nomeie e a costura
        # nao conhece. UNKNOWN e a resposta honesta — nunca PASS por omissao.
        baldes, etapa_estado = {'unknown': 1}, 'PARTIAL'

    rastro.registrar(
        banco, etapa='STRUCTURED', edge_from='DERIVED', estado=etapa_estado,
        tentativa=tentativa,
        input_grain=GRAO_DERIVADO, input_count=1,
        output_grain=GRAO_REGISTO,
        output_count=1 if estado in ('OK', sp.REOBSERVADO) else 0,
        cardinalidade='1:1',
        duracao_ms=_ms(t0),
        canonical_state=('ITEM_ERROR' if etapa_estado == 'PARTIAL' else None),
        diagnostic_code=(dg.STRUCTURED_NOT_CONNECTED
                         if etapa_estado == 'PARTIAL' else None),
        last_good_artifact=('DERIVED' if etapa_estado == 'PARTIAL' else None),
        **dict(baldes, **comum))
    return recibo


def admitir(banco, *, unidade, run_id, conteudo_id, universo=UNIVERSO_PADRAO,
            tentativa=None):
    """ADMISSION — a porta decide, e a costura conta a decisao.

    ⚠️ UM «NAO» DA PORTA E UMA PROVA BOA.
    Ele sai por `rejected`, e nao por `error`: a peneira funcionou. Contar uma
    recusa como falha tecnica faria a porta parecer avariada de cada vez que ela
    fizesse o seu trabalho.
    """
    t0 = time.time()
    comum = dict(_identidade(unidade), run_id=run_id, actor='admissao',
                 actor_version=admissao.VERSAO_DA_REGRA,
                 policy_version=POLICY_VERSION)
    tentativa = _tentativa(banco, run_id, 'ADMISSION') if tentativa is None \
        else tentativa
    item = {
        'id': unidade['CONTENT_ID'],
        'texto': unidade['TEXTO'],
        'url': unidade.get('URL'),
        'source_id': unidade.get('SOURCE_ID'),
        'captured_at': unidade.get('CAPTURED_AT'),
        'raw_asset_id': unidade.get('RAW_ASSET_ID'),
    }
    try:
        decisao = admissao.decidir(item, universo, corrida=run_id)
    except Exception as erro:
        rastro.registrar(
            banco, etapa='ADMISSION', edge_from='STRUCTURED', estado='FAIL',
            tentativa=tentativa,
            input_grain=GRAO_REGISTO, input_count=1,
            error=1, duracao_ms=_ms(t0),
            canonical_state='UNKNOWN_ERROR',
            diagnostic_code=dg.ADMISSION_NOT_CONNECTED,
            error_class=type(erro).__name__, error_message=str(erro),
            last_good_artifact='STRUCTURED', **comum)
        raise

    # AS QUATRO RESPOSTAS DA PORTA, E CADA UMA NUM BALDE DIFERENTE.
    # `ERRO` da porta e o unico que e falha tecnica. Os outros tres sao
    # decisoes medidas, e uma decisao medida nao e um defeito.
    destino = {admissao.SIM: 'passed', admissao.NAO: 'rejected',
               admissao.NAO_SEI: 'unknown',
               admissao.NAO_SE_APLICA: 'rejected',
               admissao.ERRO: 'error'}[decisao.resultado]
    e_erro = destino == 'error'

    rastro.registrar(
        banco, etapa='ADMISSION', edge_from='STRUCTURED',
        estado='FAIL' if e_erro else 'PASS',
        tentativa=tentativa,
        input_grain=GRAO_REGISTO, input_count=1,
        output_grain=GRAO_DECISAO, output_count=1,
        cardinalidade='1:1',
        duracao_ms=_ms(t0),
        canonical_state='ITEM_ERROR' if e_erro else None,
        diagnostic_code=dg.ADMISSION_NOT_CONNECTED if e_erro else None,
        last_good_artifact='STRUCTURED' if e_erro else None,
        **dict({destino: 1}, **comum))
    return decisao


def derivar(banco, *, unidade, run_id, armazem, memoria, tentativa=None):
    """DERIVED — chamado de verdade, e nao declarado como ja feito.

        PRELOADED DERIVED CONTENT != DERIVATION EXECUTED IN THIS FLOW.

    Ate a M2R esta rota comecava de um objeto que ja trazia `TEXTO`. Isso
    provava STRUCTURED e ADMISSION, e emprestava o DERIVED de OUTRA prova —
    a de O9R — porque as duas partilhavam `SOURCE_ID` e `ROUTE_CLASS_ID`.

        SAME ROUTE CLASS != SAME EXECUTION FLOW.
        TWO COMPATIBLE PROOFS != ONE END-TO-END EXECUTION.

    Agora a derivacao acontece AQUI, no mesmo `run_id`, e o que ela produz e o
    que segue para a frente. `REUSED` continua a valer — reencontrar por
    idempotencia e um resultado legitimo — porque REUSED != NOT_RUN: a
    derivacao foi chamada, e a passagem DERIVED existe nesta execucao.
    """
    # ⚠️ A TENTATIVA E MEDIDA, COMO NAS OUTRAS DUAS ETAPAS.
    # Ela estava fixa em 0 aqui e medida em `estruturar` e `admitir`. Uma
    # segunda passagem pela mesma corrida colidia na chave
    # (run_id, etapa, tentativa) — e a linha da segunda derivacao perdia-se.
    tentativa = _tentativa(banco, run_id, 'DERIVED') if tentativa is None \
        else tentativa
    return deriv.correr(
        [{'RAW_ASSET_ID': unidade['RAW_ASSET_ID'], 'PDF': unidade['PDF']}],
        banco_do_rastro=banco, run_id=run_id, armazem=armazem, memoria=memoria,
        source_id=unidade.get('SOURCE_ID'),
        route_class_id=unidade.get('ROUTE_CLASS_ID'),
        tentativa=tentativa)


def _texto_derivado(recibo_deriv, armazem):
    """O TEXTO que a derivacao acabou de produzir, lido do armazem.

    ⚠️ ESTA E A DEPENDENCIA REAL, e nao um rotulo `edge_from`.

        EDGE LABEL != DATA DEPENDENCY.

    O `storage_path` vem da linha que o dono do derivado escreveu e releu campo
    a campo. Ler os bytes por esse caminho e o que faz de STRUCTURED um
    consumidor do DERIVED desta execucao — se a derivacao nao tiver produzido
    nada, nao ha o que ler, e a cadeia para aqui em vez de continuar com um
    texto que veio de outro sitio.
    """
    bons = [r for r in (recibo_deriv.get('RESULTADOS') or [])
            if r.get('PORTA') in ('PASSED', 'REUSED')]
    if not bons:
        return None, None
    caminho = bons[0].get('STORAGE_PATH')
    if not caminho:
        return None, None
    guardado = armazem.objetos.get(caminho) if hasattr(armazem, 'objetos') \
        else None
    if guardado is None:
        return None, caminho
    dados = guardado[0] if isinstance(guardado, tuple) else guardado
    return dados.decode('utf-8', errors='replace'), caminho


def atravessar(banco, *, unidade, run_id, armazem, memoria, canal_id,
               universo=UNIVERSO_PADRAO):
    """A rota inteira, NUMA execucao: DERIVED → STRUCTURED → ADMISSION.

    ⚠️ SE STRUCTURED NAO PASSAR, ADMISSION NAO CORRE — E ISSO NAO E UM ERRO
    DELA. Ela sai `NOT_RUN`, porque nunca comecou. Marca-la FAIL faria UM
    defeito parecer DOIS, e mandaria procurar avaria onde nao ha nenhuma.

        NOT_RUN != ERROR.

    E se a DERIVACAO nao produzir, a cadeia para em DERIVED: nem STRUCTURED nem
    ADMISSION aparecem. Uma cadeia que continua depois de a primeira etapa nao
    entregar estaria a inventar o que atravessou.
    """
    recibo_d = derivar(banco, unidade=unidade, run_id=run_id,
                       armazem=armazem, memoria=memoria)
    texto, caminho = _texto_derivado(recibo_d, armazem)
    if not texto:
        # A cadeia diz a verdade sobre onde parou. Nao se forca STRUCTURED a
        # aparecer para o diagrama ficar bonito.
        return {'DERIVED': recibo_d, 'STRUCTURED': None, 'ADMISSION': None,
                'PORQUE_PAROU': ('a derivacao nao entregou artefato nesta '
                                 'execucao; nao ha texto para estruturar')}

    # ⚠️ A UNIDADE QUE SEGUE E A QUE SAIU DA DERIVACAO, e nao a que entrou.
    # O texto vem do armazem, pelo `storage_path` da linha do derivado; a
    # identidade do conteudo e o sha do artefato derivado, e nao um nome
    # escolhido pelo chamador.
    bons = [r for r in (recibo_d.get('RESULTADOS') or [])
            if r.get('PORTA') in ('PASSED', 'REUSED')]
    linha = (bons[0].get('LINHA') or {}) if bons else {}
    a_frente = dict(unidade)
    a_frente['TEXTO'] = texto
    a_frente['DERIVED_STORAGE_PATH'] = caminho
    a_frente['DERIVED_SHA256'] = linha.get('sha256')
    a_frente['CONTENT_ID'] = (linha.get('sha256') or unidade.get('CONTENT_ID'))

    recibo_s = estruturar(banco, unidade=a_frente, run_id=run_id,
                          canal_id=canal_id)
    if recibo_s.get('STATE') not in ('OK', sp.REOBSERVADO):
        rastro.registrar(
            banco, etapa='ADMISSION', edge_from='STRUCTURED', estado='NOT_RUN',
            tentativa=_tentativa(banco, run_id, 'ADMISSION'),
            input_grain=GRAO_REGISTO, input_count=1, not_run=1,
            diagnostic_code=dg.UPSTREAM_NOT_RUN,
            last_good_artifact='DERIVED',
            **dict(_identidade(a_frente), run_id=run_id, actor='admissao',
                   actor_version=admissao.VERSAO_DA_REGRA,
                   policy_version=POLICY_VERSION))
        return {'DERIVED': recibo_d, 'STRUCTURED': recibo_s, 'ADMISSION': None}

    decisao = admitir(banco, unidade=a_frente, run_id=run_id,
                      conteudo_id=recibo_s.get('CONTEUDO_ID'),
                      universo=universo)
    return {'DERIVED': recibo_d, 'STRUCTURED': recibo_s, 'ADMISSION': decisao,
            'TEXTO_VEIO_DE': caminho}


def main():
    print(__doc__.strip().split('\n')[0])
    print('etapas: DERIVED (O9R) -> STRUCTURED -> ADMISSION')
    print('donos : derivacao_forward · social_persistencia · admissao')
    print('termina em ADMISSION. ADMISSION PASS != READY PASS.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
