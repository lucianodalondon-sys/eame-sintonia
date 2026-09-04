#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM SEMÂNTICO · a evidência sustenta a conclusão que o motor produziu?

    python3 scripts/v21_red_team_semantico.py     # mede o pacote e grava a sombra

A PERGUNTA QUE ESTE ARQUIVO FAZ
-------------------------------
Não é «o código rodou?». Os cinco vãos da coleta dirigida rodaram todos: cinco
perguntas, cinco respostas, exit 0. A pergunta aqui é outra e é mais dura:

    A EVIDÊNCIA REALMENTE SUSTENTA A CONCLUSÃO QUE O MOTOR PRODUZIU?

E a primeira coisa que ela encontrou não foi um estado errado. Foi uma RAZÃO
errada ao lado de um estado certo — que é pior, porque ninguém audita a razão.
O melo × carpocapsa do Veneto saía `UNKNOWN` (correto) com o método
`CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS` (falso: o boletim do Veneto de 03/09/2026
declara «terzo volo terminato», que é exatamente a medição).

    UM CARTÃO QUE ACERTA O ESTADO E MENTE A RAZÃO ENSINA A NÃO LER A RAZÃO.

O que o red team NÃO faz
------------------------
Não altera limiar, não muda portão, não coleta, não publica. Ele lê o pacote
construído pela cadeia real e verifica, elo a elo, quem provou o quê.
"""
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_janelas as JN      # noqa: E402
import v21_necessidade as NE  # noqa: E402

ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

# Os cinco vãos da coleta dirigida, pelos IDs que a identidade determinística
# lhes deu. Se um deles sumir do pacote, o red team quebra — e é para quebrar.
CASOS = {
    1: ('OPP_3C8C3960CC66', 'videira x tignoletta · Emilia-Romagna'),
    2: ('OPP_75C37DED9160', 'macieira x carpocapsa · Veneto'),
    3: ('OPP_9C600748BB1B', 'milho x piralide · Friuli-Venezia Giulia'),
    4: ('OPP_F8106D5E1767', 'videira x botrite · Toscana'),
    5: ('OPP_169BD86DB324', 'videira x tignoletta · Umbria'),
}

# ⚠️ TESTEMUNHAS NEGATIVAS. Frases que um dia vão aparecer num boletim e que
# NUNCA podem virar resposta a uma condição quantitativa. Cada uma esteve perto
# de virar: «fase conclusa» abriria a janela pelo padrão de presente, e
# «tendenzialmente buono» é literalmente o que o Consorzio de Reggio Emilia
# escreveu sobre a tignoletta que o motor classifica como SALES_READY.
FRASES_QUE_NAO_RESPONDEM = (
    'la situazione buona in tutta la provincia',
    'il quadro rimane tendenzialmente buono',
    'pressione contenuta nella maggior parte dei vigneti',
    'siamo nella fase conclusa della difesa',
    'danni presenti nei frutteti',
)


def _le(nome):
    return json.load(open(os.path.join(ING, nome), encoding='utf-8'))['RECORDS']


def _achar(ops, oid):
    return next((o for o in ops if o.get('ID') == oid), None)


def _fato(cond, ok, nao):
    return ok if cond else nao


def item_1(o, sinais):
    """ER · o 5% está satisfeito agora? Só «NÃO» com prova de que não está."""
    falhas = []
    if o['WINDOW_OPEN_NOW'] == 'NO':
        falhas.append('declarou NO sem medicao que negue os 5%')
    # ninguém, em nenhum registro do par, declarou percentagem medida
    medido = [s['ID'] for s in sinais
              if s['ID'] in (o.get('EVIDENCE_IDS') or [])
              and any(NE.limiar_declarado(c) for _f, _m, _cr, _is, c
                      in NE.atribuicoes(s))]
    if medido:
        falhas.append('ha medicao declarada e nao foi lida: %s' % medido)
    return {
        'PERGUNTA': 'A percentagem de cachos infestados esta acima de 5% agora?',
        'CLASSIFICACAO': 'UNKNOWN',
        'POR_QUE': 'nenhum registro do par declara percentagem medida; a fonte '
                   'de 03/09 descreve o quadro territorial em prosa.',
        'WINDOW_OPEN_NOW': o['WINDOW_OPEN_NOW'],
        'METODO': o['WINDOW_OPEN_NOW_METHOD'],
        'THRESHOLD_STATE': o['THRESHOLD_STATE'],
        'MEDICAO_DECLARADA_NO_PAR': medido,
        'FALHAS': falhas,
    }


def item_2(o):
    """Veneto · fim do voo não é fim da necessidade. Quatro respostas, quatro donos."""
    falhas = []
    if o['PEST_STAGE_STATE'] != NE.STAGE_ENDED:
        falhas.append('a fase declarada pela fonte nao chegou ao cartao')
    if o['ACTION_RECOMMENDATION_STATE'] != NE.CONTINUE_RECOMMENDED:
        falhas.append('«continuare la difesa» nao chegou ao cartao')
    if o['WINDOW_OPEN_NOW'] == 'YES':
        falhas.append('recomendacao de continuar virou janela aberta')
    if o['WINDOW_OPEN_NOW_METHOD'] == 'CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS':
        falhas.append('o metodo acusa falta de medicao que a fonte declarou')
    if o['STATUS'] == 'WATCH':
        falhas.append('fim do voo foi lido como fim da necessidade')
    return {
        'PERGUNTA': 'O motor confunde fase da praga encerrada com acao encerrada?',
        'PEST_STAGE_STATE': o['PEST_STAGE_STATE'],
        'PEST_STAGE_EVIDENCE_ID': o['PEST_STAGE_EVIDENCE_ID'],
        'ACTION_RECOMMENDATION_STATE': o['ACTION_RECOMMENDATION_STATE'],
        'ACTION_RECOMMENDATION_EVIDENCE_ID': o['ACTION_RECOMMENDATION_EVIDENCE_ID'],
        'WINDOW_DEFINED': o['WINDOW_DEFINED'],
        'WINDOW_OPEN_NOW': o['WINDOW_OPEN_NOW'],
        'METODO': o['WINDOW_OPEN_NOW_METHOD'],
        'STATUS': o['STATUS'],
        'POR_QUE_NAO_E_JANELA': 'a fonte recomenda continuar a defesa, e isso e '
                                'DIRECAO. Nenhuma oracao amarra a acao a um '
                                'estadio da praga: ninguem declarou QUAL '
                                'condicao define o momento.',
        'FALHAS': falhas,
    }


def item_3(o, sinais):
    """Friuli · a fonte parou de publicar. Isso só diz UNKNOWN."""
    falhas = []
    if o['WINDOW_OPEN_NOW'] != 'UNKNOWN':
        falhas.append('serie fechada virou resposta')
    if o['THRESHOLD_STATE'] == 'MEASUREMENT_DECLARED':
        falhas.append('inventou medicao onde a fonte parou')
    # ⚠️ O TESTE ANTIGO OLHAVA O PREFIXO DO ID, e o prefixo nao e um facto sobre
    # o mundo: o lote seguinte usou o mesmo prefixo para uma REGRA do Friuli com
    # fonte, data e citacao, e o red team acusou-a de invencao.
    #
    #     UM TESTE QUE OLHA O NOME DO ARQUIVO EM VEZ DO CONTEUDO ACUSA QUEM
    #     CUMPRIU A REGRA.
    #
    # O que importa e o que a missao proibiu: inventar MEDICAO de milho no
    # Friuli depois de a serie ter fechado em 12/08/2026.
    inventados = [s['ID'] for s in sinais
                  if 'CROP_MAIZE' in (s.get('CROP_IDS') or [])
                  and 'REGION_FRIULI_VENEZIA_GIULIA' in (s.get('REGION_IDS') or [])
                  and str(s.get('REFERENCE_DATE') or '') > '2026-08-12']
    if inventados:
        falhas.append('medicao de milho no Friuli depois de a serie fechar: %s'
                      % inventados)
    return {
        'PERGUNTA': 'A ultima publicacao de 12/08 responde alguma coisa?',
        'CLASSIFICACAO': 'UNKNOWN',
        'POR_QUE': 'a serie do milho fechou para a temporada. Serie fechada nao '
                   'e limiar nao ultrapassado: e ausencia de medicao.',
        'WINDOW_OPEN_NOW': o['WINDOW_OPEN_NOW'],
        'THRESHOLD_STATE': o['THRESHOLD_STATE'],
        'REGISTRO_NOVO_CRIADO': inventados,
        'FALHAS': falhas,
    }


def item_4(o):
    """Toscana · cada elo com dono separado, provado um a um."""
    janela = o.get('WINDOW_EVIDENCE_ID')
    direcao = o.get('NEED_EVIDENCE_ID')
    produto = sorted({e['EVIDENCE_ID'] for e in (o.get('EVIDENCE_ROLES') or [])
                      if e.get('ROLE') == 'SUPPORTS_PRODUCT_MATCH'})
    elos = {
        'SINAL_ATUAL': {'DONO': direcao, 'FATO': o.get('SIGNAL_DATE'),
                        'TIPO': 'DECLARADO'},
        'DIRECAO_POSITIVA': {'DONO': direcao, 'FATO': o.get('NEED_DIRECTION'),
                             'TIPO': 'DECLARADO'},
        'JANELA_DEFINIDA': {'DONO': janela, 'FATO': o.get('WINDOW_TYPE'),
                            'TIPO': 'DECLARADO'},
        'JANELA_ABERTA_AGORA': {'DONO': janela,
                                'FATO': o.get('WINDOW_OPEN_NOW_METHOD'),
                                'TIPO': 'DECLARADO'},
        'VINCULO_COM_PORTFOLIO': {'DONO': produto,
                                  'FATO': o.get('PRODUCT_LINK_STATE'),
                                  'TIPO': 'DECLARADO'},
        'TEMPO_PARA_ACAO': {'DONO': [janela, direcao],
                            'FATO': 'janela aberta agora + documento corrente',
                            'TIPO': 'DERIVADO_DECLARADO'},
    }
    falhas = []
    if janela == direcao:
        falhas.append('a mesma frase provou janela e direcao')
    if janela in produto or direcao in produto:
        falhas.append('a frase do boletim provou tambem o vinculo com produto')
    if o['WINDOW_OPEN_NOW_METHOD'] != 'FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE':
        falhas.append('a janela aberta nao vem de declaracao da fonte')
    return {
        'PERGUNTA': 'A frase «siamo nella fase di maggior suscettibilita» prova '
                    'quantos elos?',
        'RESPOSTA': 'um: JANELA_ABERTA_AGORA. Pressao, direcao e produto tem '
                    'donos diferentes, e TEMPO_PARA_ACAO e derivado declarado.',
        'ELOS': elos,
        'STATUS': o['STATUS'],
        'FALHAS': falhas,
    }


def item_5(o, ops):
    """Umbria · 10–15% é da Umbria. Os 5% da Emilia-Romagna não viajam."""
    falhas = []
    cond = str(o.get('WINDOW_CONDITION') or '')
    if '10-15' not in cond:
        falhas.append('a regra da Umbria nao esta no cartao')
    # ⚠️ «10-15%» CONTÉM «5%». Procurar substring aqui acusaria a Umbria de
    # usar a régua da Emilia-Romagna por causa do dígito de outra régua.
    #
    #     O TESTE QUE CONFUNDE «15%» COM «5%» É O MESMO ERRO QUE ELE PROCURA.
    if re.search(r'(?<![\d-])5\s?%', cond):
        falhas.append('a soglia da Emilia-Romagna apareceu na Umbria')
    er = next((x for x in ops if x.get('ID') == CASOS[1][0]), None)
    if er and o.get('WINDOW_EVIDENCE_ID') == er.get('WINDOW_EVIDENCE_ID'):
        falhas.append('as duas regioes partilham a mesma evidencia de janela')
    if o.get('NEED_DIRECTION') != NE.NO_ACTION_RECOMMENDED:
        falhas.append('a direcao declarada pela fonte nao chegou')
    if o.get('STATUS') != 'WATCH':
        falhas.append('«non sono necessari interventi» nao virou WATCH')
    return {
        'PERGUNTA': 'A regra da Umbria e a da Umbria, e ela fecha a porta?',
        'REGRA_NA_UMBRIA': cond[:200],
        'EVIDENCIA_DA_JANELA': o.get('WINDOW_EVIDENCE_ID'),
        'EVIDENCIA_DA_JANELA_NA_ER': er.get('WINDOW_EVIDENCE_ID') if er else None,
        'NEED_DIRECTION': o.get('NEED_DIRECTION'),
        'STATUS': o.get('STATUS'),
        'COMMERCIAL_PRIORITY': o.get('COMMERCIAL_PRIORITY'),
        'FALHAS': falhas,
    }


def item_6():
    """As testemunhas negativas · frase vaga nunca responde condição medida."""
    linhas, falhas = [], []
    for frase in FRASES_QUE_NAO_RESPONDEM:
        for tipo in (JN.THRESHOLD_WINDOW, JN.WEATHER_TRIGGERED_WINDOW,
                     JN.PEST_STAGE_WINDOW, JN.PHENOLOGY_WINDOW):
            aberta, metodo = JN.aberta_agora(tipo, frase,
                                             'Vite: «maturazione».', True)
            if aberta == 'YES':
                falhas.append('«%s» abriu janela %s' % (frase, tipo))
            linhas.append({'FRASE': frase, 'TIPO': tipo,
                           'WINDOW_OPEN_NOW': aberta, 'METODO': metodo})
    return {
        'PERGUNTA': 'Uma frase qualitativa pode responder a uma condicao medida?',
        'RESPOSTA': 'nao. So quando a propria fonte declara a equivalencia — e '
                    'nenhuma delas declara.',
        'TESTEMUNHAS': linhas,
        'FALHAS': falhas,
    }


ANTES = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V115-ANTES-DO-RED-TEAM.json')

# O que se compara caso a caso no reprocessamento. Fora daqui ficam as leis e as
# traduções: elas não medem o conserto e enchem o relatório de ruído.
COMPARADOS = ('STATUS', 'COMMERCIAL_PRIORITY', 'EXTERNAL_MATERIAL_READY',
              'NEED_DIRECTION', 'WINDOW_TYPE', 'WINDOW_DEFINED',
              'WINDOW_OPEN_NOW', 'WINDOW_OPEN_NOW_METHOD', 'WINDOW_EVIDENCE_ID',
              'WHY_NOW_CODES')


def item_7(ops):
    """O acervo inteiro relido — o que mudou, caso a caso, e por quê.

    O ANTES sai de um arquivo gerado repondo os módulos de `4b97cf5` e rodando a
    cadeia real; não de lembrança. O caso é o arquétipo × cultura × alvo ×
    região, nunca o hash: o hash é como o caso se chama hoje.
    """
    if not os.path.exists(ANTES):
        return {'PERGUNTA': 'o que mudou no acervo?',
                'FALHAS': ['sem ANTES gravado — nada a comparar']}
    a = json.load(open(ANTES, encoding='utf-8'))

    def chave(r):
        return '%s|%s|%s|%s' % (r.get('ARCHETYPE'), r.get('CROP'),
                                r.get('TARGET'), r.get('GEOGRAPHY'))
    antes = {chave(r): r for r in a['RECORDS']}
    depois = {chave(r): r for r in ops}
    mudancas, falhas = [], []
    for k in sorted(set(antes) | set(depois)):
        x, y = antes.get(k), depois.get(k)
        if not x or not y:
            falhas.append('caso %s %s' % (k, 'sumiu' if x else 'apareceu'))
            continue
        difs = {c: [x.get(c), y.get(c)] for c in COMPARADOS
                if x.get(c) != y.get(c)}
        if difs:
            mudancas.append({'CASO': k, 'DIFERENCAS': difs})
    return {
        'PERGUNTA': 'o acervo relido inteiro: o que mudou, e so isso mudou?',
        'BUILD_ID_ANTES': a.get('BUILD_ID'),
        'CASOS_ANTES': a.get('COUNT'),
        'CASOS_DEPOIS': len(ops),
        'CASOS_QUE_MUDARAM': len(mudancas),
        'MUDANCAS': mudancas,
        'FALHAS': falhas,
    }


def main():
    ops = _le('OPPORTUNITIES.json')
    sinais = _le('CURRENT-FIELD-SIGNALS.json')
    pacote = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'),
                            encoding='utf-8'))
    casos = {}
    for n, (oid, rotulo) in CASOS.items():
        o = _achar(ops, oid)
        if not o:
            casos[n] = {'ROTULO': rotulo, 'FALHAS': ['caso sumiu do pacote']}
            continue
        f = {1: lambda: item_1(o, sinais), 2: lambda: item_2(o),
             3: lambda: item_3(o, sinais), 4: lambda: item_4(o),
             5: lambda: item_5(o, ops)}[n]()
        f['OPPORTUNITY_ID'] = oid
        f['ROTULO'] = rotulo
        casos[n] = f
    casos[6] = item_6()
    casos[7] = item_7(ops)

    falhas = [(n, m) for n, c in casos.items() for m in c.get('FALHAS', [])]
    veredito = 'PASS' if not falhas else (
        'PARTIAL' if len(falhas) <= 2 else 'FAIL')

    for n in sorted(casos):
        c = casos[n]
        print('── %d · %s' % (n, c.get('ROTULO', 'testemunhas negativas')))
        print('   %s' % c.get('PERGUNTA', ''))
        for k in ('CLASSIFICACAO', 'WINDOW_OPEN_NOW', 'METODO', 'STATUS',
                  'PEST_STAGE_STATE', 'ACTION_RECOMMENDATION_STATE',
                  'THRESHOLD_STATE', 'RESPOSTA', 'BUILD_ID_ANTES',
                  'CASOS_ANTES', 'CASOS_DEPOIS', 'CASOS_QUE_MUDARAM'):
            if c.get(k) is not None and k in c:
                print('   %-30s %s' % (k, str(c[k])[:110]))
        print('   FALHAS: %s' % (c.get('FALHAS') or 'nenhuma'))
    print('\nSEMANTIC_RED_TEAM = %s  (%d falhas)' % (veredito, len(falhas)))

    fora = {
        'COLLECTION': 'V115-RED-TEAM-SEMANTICO',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/'
                  'OPPORTUNITIES.json · BUILD_ID %s' % pacote.get('BUILD_ID'),
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'nao pergunta se o codigo rodou. Pergunta se a evidencia sustenta '
               'a conclusao — elo a elo, com o dono de cada um nomeado.',
        'SEMANTIC_RED_TEAM': veredito,
        'FALHAS': [{'ITEM': n, 'FALHA': m} for n, m in falhas],
        'ITENS': casos,
    }
    saida = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V115-RED-TEAM-SEMANTICO.json')
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    json.dump(fora, open(saida, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('gravado em %s' % os.path.relpath(saida, ROOT))
    return 0 if veredito == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
