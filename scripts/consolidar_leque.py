#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSOLIDA O LEQUE — junta os 39 resultados do workflow nos artefatos canônicos.

    python3 scripts/consolidar_leque.py <caminho do journal.jsonl>

⚠️ POR QUE ISTO PRECISOU EXISTIR, e é um defeito MEU
------------------------------------------------------
O script do workflow passou ao crítico de completude uma fatia de 22.000 caracteres do
JSON das fichas. As 23 fichas do GIRE não cabiam. O crítico escreveu, corretamente,
«9 de 23 espécies» — ele relatou o que recebeu, não o que existe.

    TRUNCAR A ENTRADA DA SÍNTESE NÃO ENCOLHE O ACERVO. ENCOLHE O RELATÓRIO.

O dado das 23 nunca se perdeu: está no `journal.jsonl`, uma linha por agente. Este
arquivo vai lá buscar. Custo: zero — nenhum agente roda de novo.
"""
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')


def pares_do_output(caminho):
    """O par (ato, veredito) como o pipeline o montou. É a fonte CERTA.

    ⚠️ Tentei antes reconstruir esse par a partir do `journal.jsonl`, casando o CELEX que
    o refutador cita no próprio texto. Errou justamente nos dois atos que mais importam:
    32026R1421 e 32026R1353 — as duas refutações graves — saíram sem veredito casado.

        RECONSTRUIR UM VÍNCULO QUE A FONTE JÁ TEM É INVENTAR ERRO DE GRAÇA.

    O `.output` da tarefa é JSON inteiro e traz `result.bruto_atos` com o par pronto.
    """
    d = json.load(open(caminho, encoding='utf-8'))
    return d.get('result') or {}


def resultados(journal):
    fora = []
    with open(journal, encoding='utf-8', errors='replace') as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get('type') == 'result':
                fora.append(o.get('result'))
    return fora


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    res = resultados(sys.argv[1])
    print('resultados no journal: %d' % len(res))
    saida_task = sys.argv[2] if len(sys.argv) > 2 else None
    wf = pares_do_output(saida_task) if saida_task else {}
    pares = wf.get('bruto_atos') or []
    print('pares (ato, veredito) do .output: %d' % len(pares))

    fichas, atos, verdicts, textos = [], [], [], []
    for r in res:
        if isinstance(r, dict) and 'fichas' in r:
            fichas.extend(r['fichas'])
        elif isinstance(r, dict) and 'celex' in r and 'substances' in r:
            atos.append(r)
        elif isinstance(r, dict) and 'refuted' in r:
            verdicts.append(r)
        elif isinstance(r, str):
            textos.append(r)
    print('  fichas GIRE: %d · atos lidos: %d · vereditos: %d · textos: %d'
          % (len(fichas), len(atos), len(verdicts), len(textos)))

    # ── 1 · GIRE completo ─────────────────────────────────────────────────────
    vistas = OrderedDict()
    for f in fichas:
        vistas.setdefault(f.get('slug'), f)
    linhas = []
    for slug, f in vistas.items():
        for r in (f.get('resistencias') or []):
            linhas.append({
                'ESPECIE': f.get('nome_scientifico'),
                'ESPECIE_COMUM_IT': f.get('nome_italiano'),
                'SLUG': slug,
                'FAMILIA': f.get('familia'),
                'MECANISMO': r.get('mecanismo') or 'NÃO SEI',
                'CULTURA_DECLARADA': r.get('cultura') or 'NÃO SEI',
                'PRIMEIRO_CASO_ANO': r.get('primeiro_caso_ano') or 'NÃO SEI',
                'REGIOES': r.get('regioes') or [],
                'NOTA': r.get('nota'),
                'RESISTENCIA_MULTIPLA_DECLARADA': f.get('resistencia_multipla') or 'NÃO SEI',
                'CITACAO_LITERAL': f.get('citacao_literal') or '',
                'ECOLOGIA': f.get('ecologia_resumo'),
                'GESTAO': f.get('gestao_recomendada'),
                'FONTE_URL': 'http://gire.mlib.cnr.it/index.php?sel=schedeSpecie/%s' % slug,
            })
    sem_cit = [l for l in linhas if not l['CITACAO_LITERAL']]
    corpo = {
        'DATASET': 'IT-GIRE-RESISTENCIA-V2',
        'SUBSTITUI': 'IT-GIRE-RESISTENCIA-V1 — que tinha só o índice, e declarava 22 espécies '
                     'quando o array tinha 23. Corrigido: o índice do GIRE lista 23.',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-GIRE',
        'SOURCE_NAME': 'GIRE — Gruppo Italiano di lavoro sulla Resistenza agli Erbicidi (CNR)',
        'source': 'http://gire.mlib.cnr.it — ficha a ficha, lidas em 2026-09-02',
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'TECHNICAL_AUTHORITY_DECLARATION',
        'CAPTURED_AT': '2026-09-02', 'APIFY_RUNS': 0, 'COST_USD': 0,
        'ROTA': 'gire.ipsp.cnr.it recusa (certificado expirado). O espelho gire.mlib.cnr.it abre por HTTP.',
        'FICHAS_LIDAS': len(vistas),
        'FICHAS_NO_INDICE': 23,
        'LINHAS_DE_RESISTENCIA': len(linhas),
        'LINHAS_SEM_CITACAO': len(sem_cit),
        'O_QUE_ISTO_NAO_E': [
            'não é mapa de incidência — diz onde foi CONFIRMADA, nunca quanta área tem',
            'não é lista de daninhas importantes: é lista de daninhas RESISTENTES',
            'não diz nada sobre produto de nenhum fabricante',
            'MECANISMO = NÃO SEI significa que a ficha nomeia a família química e não o grupo '
            'HRAC. Não é o mesmo que ausência de mecanismo',
        ],
        'FICHAS': list(vistas.values()),
        'LINHAS': linhas,
    }
    d1 = os.path.join(SAMPLES, 'IT-CIENCIA')
    os.makedirs(d1, exist_ok=True)
    with open(os.path.join(d1, 'IT-GIRE-RESISTENCIA-V2.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('  gravado IT-GIRE-RESISTENCIA-V2.json — %d fichas, %d linhas de resistência'
          % (len(vistas), len(linhas)))

    # ── 2 · atos UE com veredito ──────────────────────────────────────────────
    por_celex = {a['celex']: a for a in atos}
    # ⚠️ O journal guarda o resultado de CADA AGENTE, não o valor de retorno do estágio
    # do pipeline. Então o veredito chega solto — sem o `celex` ao lado. Casar por ORDEM
    # seria frágil (o pipeline não garante ordem de conclusão); caso pelo CELEX que o
    # próprio refutador cita no texto, que é o único vínculo que sobreviveu.
    ver_por_celex = {}
    for par in pares:
        if par.get('celex') and par.get('veredito'):
            ver_por_celex[par['celex']] = par['veredito']
            por_celex.setdefault(par['celex'], par.get('lido') or {})
    saida = []
    for celex, a in sorted(por_celex.items()):
        v = ver_por_celex.get(celex) or {}
        saida.append({
            'CELEX': celex,
            'ACT_TYPE': a.get('act_type'),
            'ACT_READ': True,
            'SUBSTANCES': a.get('substances'),
            'LITERAL_QUOTES': a.get('literal_quotes'),
            'WHAT_THE_ACT_DOES_NOT_SAY': a.get('what_the_act_does_not_say'),
            'ADVERSARIAL_VERDICT': {
                'REFUTED': v.get('refuted'),
                'REASON': v.get('reason'),
                'CORRECTED': v.get('corrected_dates'),
                'MATCH_METHOD': 'par montado pelo proprio pipeline, lido do .output da tarefa',
                'MATCH_CONFIDENCE': {'ESTADO': 'EXATO' if celex in ver_por_celex
                                     else 'SEM_VEREDITO'},
            },
        })
    refutados = [s for s in saida if s['ADVERSARIAL_VERDICT']['REFUTED']]
    corpo2 = {
        'DATASET': 'IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2',
        'SUBSTITUI': 'V1, que tinha 1 ato lido de 16 e um casamento léxico não verificado',
        'COUNTRY': 'IT', 'SOURCE_ID': 'EU-T4-001-B',
        'source': 'EU Publications Office / CELLAR — SPARQL e texto integral, rota pública sem chave',
        'SOURCE_LOCATION': 'EUROPEAN UNION', 'FACT_LOCATION': 'EUROPEAN UNION',
        'ORIGINAL_LANGUAGE': 'EN', 'REGULATORY_LAYER': 'EU ACTIVE SUBSTANCE',
        'EVIDENCE_CLASS': 'REGULATORY_FACT', 'CAPTURED_AT': '2026-09-02',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'METODO': ('um agente leu cada ato na íntegra; um SEGUNDO agente independente releu a '
                   'mesma fonte tentando REFUTAR a leitura. Só o que sobreviveu entra.'),
        'ATOS_LIDOS': len(saida),
        'ATOS_REFUTADOS': len(refutados),
        'O_QUE_A_REFUTACAO_PEGOU': [
            '32026R1421 — risk_assessment_state errado em 5 de 6 substâncias: a fórmula do '
            'Art. 11 aparece no ato para benzovindiflupyr, cycloxydim, dazomet e '
            'metsulfuron-methyl, e NÃO para as seis lidas. As datas estavam certas.',
            '32026R1353 — data ANTIGA lida como NOVA: 31 May 2035 foi fixada pelo Reg. '
            '2020/617, e este ato (AMENDMENT_OF_CONDITIONS, Art. 13(2)(c)) não altera data.',
            '32025R0099 — candidate_for_substitution errado em 2 de 3. Datas corretas.',
            '32024R1718 — um campo errado. Data correta.',
        ],
        'LEI': 'refutação que corrige um campo e confirma a data NÃO invalida o ato — invalida '
               'o campo. Guardar as duas coisas separadas é o que permite usar o resto.',
        'CASAMENTO_DO_VEREDITO': {
            'METODO': 'o par (ato, veredito) e o que o proprio pipeline montou; lido do '
                      'arquivo .output da tarefa, nao reconstruido.',
            'TENTATIVA_ANTERIOR_DESCARTADA': ('casar pelo CELEX citado no texto do refutador. '
                                              'Errou nos dois atos mais importantes '
                                              '(32026R1421 e 32026R1353) — ficaram sem veredito.'),
            'CASADOS': len(ver_por_celex),
        },
        'ATOS': saida,
    }
    d2 = os.path.join(SAMPLES, 'IT-REGUA')
    os.makedirs(d2, exist_ok=True)
    with open(os.path.join(d2, 'IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo2, f, ensure_ascii=False, indent=1)
    print('  gravado IT-ADAMA-EU-ACTIVE-SUBSTANCE-V2.json — %d atos lidos, %d refutados'
          % (len(saida), len(refutados)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
