#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS 26 REGISTROS QUE ENTRAM PELA PORTA E NÃO PERTENCEM A COLEÇÃO ALGUMA.

    python3 scripts/v21_censo_das_16_janelas.py

    NÃO INGERE NADA. Este arquivo é um CENSO.

Por que ele existe: a testemunha universal achou 26 registros reais que entram
por `CANONICAL-INTELLIGENCE.json` e não existem no pacote — sem erro, sem
quarentena, sem estado. Dez são meta-registro sobre a própria coleta; dezesseis
dizem-se janelas correntes de herbicida.

⚠️ E A PERGUNTA MUDOU DEPOIS DA RECONCILIAÇÃO DE LINHAGEM.
Na linha antiga, «não existe `WINDOW_KIND=APPLICATION` no pacote» era verdade, e
essas 16 pareciam a lacuna que faltava. A linhagem `e7c154c` trouxe
`v21_janelas.py`, que lê a janela **do texto do próprio sinal** por fenologia,
pré-colheita, limiar, fase da praga e condição climática. Então antes de
ingerir é obrigatório perguntar outra coisa:

    ESTAS 16 SÃO JANELA QUE FALTA, OU SÃO A MESMA JANELA QUE A LINHAGEM NOVA
    JÁ MODELA DE OUTRA FORMA — E ENTÃO INGERI-LAS SERIA CRIAR DUPLICATA?

Este censo responde par a par, com o tipo que `v21_janelas` daria a cada texto e
com o que já existe no pacote para a mesma combinação cultura × alvo × região.
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTA = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2',
                     'CANONICAL-INTELLIGENCE.json')
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'CENSO-DOS-26-SEM-COLECAO.json')

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_janelas as JAN        # noqa: E402  · dono do tipo de janela
import v21_normalizar as N       # noqa: E402  · dono dos eixos canonicos


def _texto(r):
    return ' '.join(str(r.get(c) or '') for c in
                    ('tipo', 'o_que', 'o_que_prova', 'valor', 'periodo'))


def main():
    porta = json.load(open(PORTA, encoding='utf-8'))['RECORDS']
    no_pacote = set()
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq.startswith('CANONICAL'):
            continue
        d = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        for x in (d.get('RECORDS') or []):
            if isinstance(x, dict) and x.get('ID'):
                no_pacote.add(x['ID'])

    # O que o pacote JA tem de janela, por cultura x alvo x regiao.
    opp = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'),
                         encoding='utf-8'))['RECORDS']
    # ⚠️ DUAS PERGUNTAS DIFERENTES, E O CENSO ANTERIOR SO FAZIA UMA.
    #
    #     REPRESENTADO  = o pacote ja tem um caso para esta cultura x regiao
    #     DUPLICATA     = o pacote ja tem JANELA DEFINIDA para o mesmo par
    #
    # Um registro pode falar de uma cultura que o pacote conhece sem ser
    # duplicata de janela nenhuma. Confundir as duas faz o censo dizer «novo»
    # sobre coisa conhecida, ou «duplicata» sobre coisa que ninguem modelou.
    ja_modelado, representado = {}, {}
    for o in opp:
        representado.setdefault((o.get('CROP'), o.get('GEOGRAPHY')), []).append(
            {'OPPORTUNITY_ID': o['ID'], 'TARGET': o.get('TARGET'),
             'WINDOW_RULE_STATE': o.get('WINDOW_RULE_STATE')})
        if o.get('WINDOW_DEFINED') != 'YES':
            continue
        ja_modelado[(o.get('CROP'), o.get('TARGET'), o.get('GEOGRAPHY'))] = {
            'OPPORTUNITY_ID': o['ID'], 'WINDOW_TYPE': o.get('WINDOW_TYPE'),
            'WINDOW_OPEN_NOW': o.get('WINDOW_OPEN_NOW'),
            'WINDOW_RULE_STATE': o.get('WINDOW_RULE_STATE'),
            'WINDOW_EVIDENCE_ID': o.get('WINDOW_EVIDENCE_ID')}
    por_crop = {}
    for (c, a, g), v in ja_modelado.items():
        por_crop.setdefault(c, []).append(dict(v, TARGET=a, REGION=g))

    fora = []
    for r in porta:
        rid = r.get('CANONICAL_RECORD_ID')
        if rid in no_pacote:
            continue
        fam = r.get('FAMILIA')
        txt = _texto(r)
        # `tipos_da_oracao` devolve [(TIPO, padrao_que_casou)] — o padrão viaja
        # junto para que a leitura seja auditável. Aqui só o tipo interessa.
        tipos = [t for t, _p in
                 (JAN.tipos_da_oracao(txt) if fam == 'HERBICIDE_CURRENT_CONTEXT'
                  else [])]
        crop = N.crop_id(r.get('crop'))
        issues = N.issues_no_texto(txt)
        regs = N.region_ids(r.get('region'))
        agronomica = any(t in JAN.AGRONOMICOS for t in tipos)
        equivalentes = [x for x in por_crop.get(crop, [])
                        if not regs or x['REGION'] in regs or x['REGION'] == 'GEO_ITALY']
        fora.append({
            'RECORD_ID': rid,
            'FAMILIA': fam,
            'CLASSE': ('PAPEL_DE_TRABALHO' if fam == 'COMMERCIAL_CATALOG'
                       else 'JANELA_CORRENTE_DECLARADA'),
            'SOURCE_ID': r.get('source_name'),
            'SOURCE_URL': r.get('source_url'),
            'PUBLICATION_DATE': r.get('publication_date'),
            'CROP_DECLARED': r.get('crop'),
            'CROP': crop,
            'TARGETS_NO_TEXTO': issues,
            'REGION_DECLARED': r.get('region'),
            'REGION_IDS': regs,
            'TIPO_DECLARADO': r.get('tipo'),
            'WINDOW_TYPE_QUE_v21_janelas_DARIA': tipos,
            'AGRONOMIC_OR_ADMINISTRATIVE': (
                'AGRONOMIC' if agronomica else
                'ADMINISTRATIVE' if JAN.ADMINISTRATIVE_WINDOW in tipos else
                'UNKNOWN'),
            'CURRENT': r.get('observation_class'),
            'WINDOW_RULE_STATE_DO_EQUIVALENTE': [x.get('WINDOW_RULE_STATE')
                                                 for x in equivalentes],
            'JA_MODELADO_NA_INTELIGENCIA_NOVA': equivalentes,
            'ALREADY_REPRESENTED': sorted({
                y['OPPORTUNITY_ID'] for g in (regs or ['GEO_ITALY'])
                for y in representado.get((crop, g), [])}) if crop else [],
            'DUPLICATE': (bool(equivalentes)
                          and bool(set(issues) & {x['TARGET']
                                                  for x in equivalentes})
                          ) if crop else 'UNKNOWN',
            'SERIA_DUPLICATA': bool(equivalentes) if crop else 'UNKNOWN',
            'COLECAO_CANONICA_QUE_DEVERIA_POSSUIR': (
                'NENHUMA — e papel de trabalho, e papel de trabalho nao vira '
                'material (INTERNAL-ARCHIVE, se algum dia)'
                if fam == 'COMMERCIAL_CATALOG' else
                'CURRENT-FIELD-SIGNALS.json — o texto e observacao datada do '
                'servico regional, e e de la que v21_janelas le a janela. '
                'CROP-WINDOWS.json seria o lugar errado: aquela colecao guarda '
                'janela de CALENDARIO, e estas nao sao de calendario.'),
        })

    por_classe = Counter(x['CLASSE'] for x in fora)
    janelas = [x for x in fora if x['CLASSE'] == 'JANELA_CORRENTE_DECLARADA']
    dup = [x for x in janelas if x['DUPLICATE'] is True]
    repr_ = [x for x in janelas if x['ALREADY_REPRESENTED']]
    agro = [x for x in janelas if x['AGRONOMIC_OR_ADMINISTRATIVE'] == 'AGRONOMIC']
    sem_alvo = [x for x in janelas if not x['TARGETS_NO_TEXTO']]

    r = {
        'WHAT_IT_IS': 'os registros que entram pela porta e nao pertencem a '
                      'colecao alguma, no estado RECONCILIADO',
        'NAO_INGERE_NADA': True,
        'TOTAL': len(fora),
        'POR_CLASSE': dict(por_classe),
        'PAPEL_DE_TRABALHO': por_classe.get('PAPEL_DE_TRABALHO', 0),
        'JANELAS_CORRENTES': por_classe.get('JANELA_CORRENTE_DECLARADA', 0),
        'DESSAS_JANELAS': {
            'COM_TIPO_AGRONOMICO_RECONHECIDO': len(agro),
            'SEM_ALVO_NOMEADO_NO_TEXTO': len(sem_alvo),
            'JA_MODELADAS_PELA_LINHAGEM_NOVA': len(dup),
            'CULTURA_X_REGIAO_JA_REPRESENTADA': len(repr_),
            'REALMENTE_NOVAS': len(janelas) - len(dup),
        },
        'LEI': 'antes de ingerir, provar que nao se esta recolocando janela que a '
               'linhagem nova ja modela de outra forma. v21_janelas le a janela do '
               'TEXTO do sinal, por fenologia, pre-colheita, limiar, fase da praga '
               'ou condicao climatica — nao de uma colecao de janelas.',
        'RECORDS': fora,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(r, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== OS %d SEM COLECAO ==' % len(fora))
    print('  papel de trabalho   : %d' % r['PAPEL_DE_TRABALHO'])
    print('  janelas correntes   : %d' % r['JANELAS_CORRENTES'])
    for k, v in r['DESSAS_JANELAS'].items():
        print('    %-36s %d' % (k, v))
    print('\n  %-16s %-22s %-26s %s'
          % ('RECORD', 'CROP', 'TIPO_v21_janelas', 'JA_MODELADO'))
    for x in janelas:
        print('  %-16s %-22s %-26s %s'
              % (x['RECORD_ID'], str(x['CROP'])[:22],
                 ','.join(x['WINDOW_TYPE_QUE_v21_janelas_DARIA'])[:26] or '—',
                 ('SIM: ' + x['JA_MODELADO_NA_INTELIGENCIA_NOVA'][0]['OPPORTUNITY_ID'])
                 if x['SERIA_DUPLICATA'] is True else 'nao'))
    print('\ngravado: %s' % SAIDA)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
