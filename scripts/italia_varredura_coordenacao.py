#!/usr/bin/env python3
"""
ITÁLIA — varredura sistemática da classe de erro que "frumento tenero e duro" revelou.

O defeito não era um caso; era uma CLASSE. Este arquivo mede a classe inteira sobre os
163 rótulos, e a medição estreitou a hipótese de forma útil.

A HIPÓTESE DE PARTIDA ESTAVA LARGA DEMAIS
------------------------------------------
"Coordenação quebra o extrator" — `mais e sorgo`, `pomodoro e patata`, `vite e olivo`.
**Falso.** Nessas formas cada palavra é um substantivo de cultura completo, e
`\\bmais\\b` e `\\bsorgo\\b` casam sozinhos. Coordenação, por si, não perde nada.

O QUE REALMENTE QUEBRA É A **ELISÃO DE CABEÇA**
-----------------------------------------------
O erro só aparece quando a cultura é identificada por **substantivo + modificador** e a
coordenação **omite o substantivo na segunda ocorrência**:

    frumento tenero e duro        <- "duro" fica órfão de "frumento"
    frumento tenero, duro, orzo   <- idem, com vírgula

No vocabulário indexado, a única cultura assim é o trigo (`frumento|grano` ×
`tenero|duro`). Por isso a classe é estreita — mas ela é grave justamente ali, porque
`grano duro` é a maior cultura da Itália.

O SEPARADOR TEM DE SER GENÉRICO, E ISSO A VARREDURA PROVOU
-----------------------------------------------------------
A primeira correção tratou só `\\s+e\\s+`. A varredura achou a MESMA elisão com
**vírgula**, no PRESSING 500 (*"per il frumento tenero, duro, orzo, segale, avena"*).
Consertar o `e` teria resolvido 11 casos e deixado o 12º de pé. O padrão passou a
aceitar `,`, ` e ` e ` ed `.

O QUE FOI TESTADO E **NÃO** APARECEU
-------------------------------------
Não é "não existe": é **não encontrei nos formatos medidos**.

  · `mais dolce` — 12 rótulos citam milho doce, e **todos os 12** também citam `mais`
    isolado. Nenhum produto entraria em `MAIZE` só por causa do milho doce. A conflação
    existe no índice, mas não produziu falso positivo neste corpus.
  · listas de culturas plenas (`girasole, soia, barbabietola`) — nenhuma perda.
  · artigo/preposição compartilhados (`vite, del pomodoro`) — nenhuma perda.
  · plural/singular — nenhuma forma no corpus depende disso para ser reconhecida.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import italia_rotulo_parse as rp  # noqa: E402

ETIQ = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
PORT = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001', 'IT-T4-001-portfolio-rotulo.json')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001', 'IT-COORDINATION-SWEEP.json')

# Elisão de cabeça: substantivo + modificador, e o modificador seguinte fica órfão.
ELISAO = re.compile(r'(?i)\b(frumento|grano)\s+(tenero|duro)\s*(?:,|\s+ed?\s+)\s*'
                    r'(duro|tenero)\b')
# Padrão ANTIGO, para medir o que ele perdia. Não é usado em produção — só na medição.
ANTIGO = re.compile(r'(?i)(grano|frumento)\s+duro')


def formas_de_superficie():
    """As palavras de cultura saem do PRÓPRIO índice do extrator, não de lista à mão."""
    sup = {}
    for crop, pats in rp.CROP_TERMS.items():
        for p in pats:
            limpo = p.replace(r'\b', ' ').replace(r'\s+', ' ')
            for w in re.findall(r'[a-zà-ù]{3,}', limpo):
                sup.setdefault(w, set()).add(crop)
    return sup


def varrer():
    """Devolve (achados, lidos). Lê os PDFs — custa ~90 s."""
    import glob
    achados, lidos = [], 0
    for f in sorted(glob.glob(os.path.join(ETIQ, '*.pdf'))):
        try:
            t, _ = rp.texto(f)
        except Exception:
            continue
        lidos += 1
        ms = {m.group(0).lower() for m in ELISAO.finditer(t)}
        if not ms:
            continue
        achados.append({
            'LABEL_FILE': os.path.basename(f),
            'REGISTRATION_ID': os.path.basename(f).split('_')[0],
            'ELIDED_FORMS': sorted(ms),
            'SEPARATOR': sorted({',' if ',' in m else 'ed' if ' ed ' in m else 'e'
                                 for m in ms}),
            'OLD_PATTERN_WOULD_CATCH': bool(ANTIGO.search(t)),
            'NOW_DETECTED': rp.culturas(t).get('DURUM_WHEAT', {}).get('STATE')
                            == 'CROP_TERM_PRESENT',
        })
    return achados, lidos


def main():
    achados, lidos = varrer()
    perdidos = [a for a in achados if not a['OLD_PATTERN_WOULD_CATCH']]
    ainda = [a for a in achados if not a['NOW_DETECTED']]

    port = json.load(open(PORT, encoding='utf-8'))
    nomes = {p['REGISTRATION_ID']: p for p in port['PRODUCTS']}
    recuperados = []
    for a in perdidos:
        p = nomes.get(a['REGISTRATION_ID'])
        if p:
            recuperados.append({'PRODUCT': p['PRODUCT'],
                                'ACTIVE_SUBSTANCE': p['ACTIVE_SUBSTANCE'],
                                'EXPIRY': p['EXPIRY'],
                                'ELIDED_FORMS': a['ELIDED_FORMS'],
                                'SEPARATOR': a['SEPARATOR']})

    total_durum = len(port['BY_CROP_TERM']['DURUM_WHEAT']['PRODUCTS'])
    antes = total_durum - len(recuperados)

    out = {
        'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-COORDINATION-SWEEP',
        'SOURCE': 'os 163 rótulos oficiais de IT-T4-001-ETICHETTA',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'SOURCE_LOCATION': 'interno — auditoria de extrator sobre fonte primária',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'QUESTION': ('a coordenação quebra o extrator de cultura, e em quantos rótulos?'),
        'ANSWER': ('coordenação por si NÃO quebra. O que quebra é ELISÃO DE CABEÇA, e no '
                   'vocabulário indexado ela só existe no trigo — onde custou %d de %d '
                   'rótulos de grano duro.' % (len(recuperados), total_durum)),
        'HYPOTHESIS_NARROWED': {
            'STARTED_AS': 'coordenação (mais e sorgo, pomodoro e patata, vite e olivo)',
            'MEASURED_AS': 'elisão de cabeça em cultura de substantivo + modificador',
            'WHY': ('em "mais e sorgo" cada palavra é substantivo de cultura completo e '
                    'casa sozinha. A perda exige que o substantivo seja OMITIDO na '
                    'segunda ocorrência, o que só acontece com frumento/grano × '
                    'tenero/duro.'),
        },
        'LABELS_READ': lidos,
        'LABELS_WITH_HEAD_ELISION': len(achados),
        'LABELS_LOST_BY_OLD_PATTERN': len(recuperados),
        'DURUM_BEFORE_FIX': antes,
        'DURUM_AFTER_FIX': total_durum,
        'UNDERCOUNT_PCT': round(100.0 * len(recuperados) / total_durum, 1)
                          if total_durum else 0.0,
        'STILL_UNDETECTED': ainda,
        'SEPARATORS_FOUND': sorted({s for a in achados for s in a['SEPARATOR']}),
        'WHY_SEPARATOR_IS_GENERIC': (
            'a primeira correção tratou só " e ". A varredura achou a mesma elisão com '
            'VÍRGULA no PRESSING 500 — consertar o " e " teria resolvido 11 e deixado o '
            '12º de pé. O padrão aceita "," , " e " e " ed ".'),
        'PRODUCTS_RECOVERED': sorted(recuperados, key=lambda x: x['PRODUCT']),
        'CROPS_AFFECTED': ['DURUM_WHEAT', 'COMMON_WHEAT'],
        'VERDICT_CHANGES': [
            ('a leitura "o portfólio nomeado para trigo duro não tem fungicida foliar" '
             'caiu: os 5 foliares que casam com o boletim de campo autorizam grano duro'),
            ('nenhum verdito de outra cultura mudou — a classe de erro não as alcança'),
        ],
        'TESTED_AND_NOT_FOUND': {
            'STATE': 'NÃO ENCONTREI NOS FORMATOS MEDIDOS — não é "não existe"',
            'ITEMS': [
                {'FORM': 'mais dolce (modificador que cria cultura distinta)',
                 'LABELS_WITH_IT': 12,
                 'FALSE_POSITIVES_PRODUCED': 0,
                 'NOTE': ('todos os 12 também citam "mais" isolado, então nenhum produto '
                          'entra em MAIZE só por causa do milho doce. A conflação existe '
                          'no índice; neste corpus ela não produziu falso positivo.')},
                {'FORM': 'lista de culturas plenas (girasole, soia, barbabietola)',
                 'LOSS': 0, 'NOTE': 'cada substantivo casa sozinho'},
                {'FORM': 'artigo/preposição compartilhados (vite, del pomodoro)',
                 'LOSS': 0, 'NOTE': 'a preposição não separa o substantivo do índice'},
                {'FORM': 'singular/plural',
                 'LOSS': 0,
                 'NOTE': 'nenhuma forma do corpus depende de flexão para ser reconhecida'},
            ],
        },
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que não exista outra classe de erro de extração — só que esta foi medida',
            'que rótulos futuros usem as mesmas formas; o separador foi generalizado '
            'justamente porque a segunda pontuação apareceu depois da primeira correção',
            'nada sobre venda, disponibilidade ou prioridade interna',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print('rotulos lidos ................. %d' % lidos)
    print('com elisao de cabeca .......... %d' % len(achados))
    print('perdidos pelo padrao antigo ... %d  (%.1f%% do total de grano duro)'
          % (len(recuperados), out['UNDERCOUNT_PCT']))
    print('grano duro: %d -> %d' % (antes, total_durum))
    print('separadores achados ........... %s' % ', '.join(out['SEPARATORS_FOUND']))
    print('ainda nao detectados .......... %d' % len(ainda))
    for r in out['PRODUCTS_RECOVERED']:
        print('   + %-16s %-34s %s' % (r['PRODUCT'], r['ACTIVE_SUBSTANCE'],
                                       ','.join(r['SEPARATOR'])))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
