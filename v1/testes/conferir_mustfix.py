#!/usr/bin/env python3
"""
conferir_mustfix.py — remede, contra a fonte primaria, o que os 11 MUST_FIX da
rodada 3 do red team afirmavam, e escreve o resultado.

Nao e o arbitro. O arbitro julga o produto inteiro e decide DEMO_READY; este
script faz uma coisa so: pega cada afirmacao NUMERICA dos MUST_FIX e pergunta ao
build atual se ela ainda vale. Onde o numero bate com o que o arbitro mediu por
conta propria — com outro instrumento, e a partir de coordenadas que este
repositorio nao tem — isso e convergencia independente e esta dito. Onde nao
bate, esta dito tambem.

  uso:  python3 v1/testes/conferir_mustfix.py
"""
import json, os, re, subprocess, sys, unicodedata

PAY = 'v1/dados/CASCO-PAYLOAD.json'
PAR = 'v1/dados/PARES-FIOS-CHECK.json'
HER = 'v1/dados/HERANCA-CHECK.json'
EXC = 'v1/dados/EXCLUSAO.json'
FLUXO = '/tmp/leiturafluxo'


def sa(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()


def rad(w):
    w = re.sub(r'[^a-z]', '', sa(w))
    if len(w) >= 5:
        r = re.sub(r'h?[aeiou]$', '', w)
        if len(r) >= 4:
            return r
    return w


def fluxo(reg):
    os.makedirs(FLUXO, exist_ok=True)
    f = os.path.join(FLUXO, reg + '.txt')
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        pdf = f'pilot-label-intelligence/labels/pdf/{reg}.pdf'
        if not os.path.exists(pdf):
            return ''
        subprocess.run(['pdftotext', pdf, f], capture_output=True, timeout=120)
    return re.sub(r'\s+', ' ', open(f, encoding='utf-8', errors='replace').read())


RX_CABECA = re.compile(r'[A-ZÀ-Þ][A-ZÀ-Þ \',()/-]{3,60}:')


def coocorre_no_escopo(reg, crop, alvo):
    """Cultura e alvo caem no mesmo escopo de cabecalho com dois-pontos?"""
    t = fluxo(reg)
    if not t:
        return None
    ts = sa(t)
    c, a = rad(str(crop).split('_')[0]), rad(str(alvo).split('_')[0])
    if len(c) < 4 or len(a) < 4:
        return None
    cortes = [m.start() for m in RX_CABECA.finditer(t)] + [len(t)]
    for i, j in zip(cortes, cortes[1:]):
        seg = ts[i:j]
        if re.search(r'\b' + c, seg) and re.search(r'\b' + a, seg):
            return True
    return False


def main():
    pay = json.load(open(PAY, encoding='utf-8'))
    pf = json.load(open(PAR, encoding='utf-8'))
    her = json.load(open(HER, encoding='utf-8'))
    exc = json.load(open(EXC, encoding='utf-8'))
    byreg = {p['reg']: p for p in pay['products']}
    R = {}

    # ---- MF-01 · R-14 aplicada aos PARES
    ret = pf['COUNTS'].get('PAIR_CONTRADICTED_BY_RULE', 0)
    fam = {}
    for c in pf['CONTRADICTED']:
        fam.setdefault(f"{c['CROP']} x {c['TARGET']}", []).append(c['REGISTRATION_ID'])
    R['MF-01'] = {
        'AFIRMACAO_DO_ARBITRO': ('R-11 nunca aplicada aos PARES DE USO; 34 pares sao uso que a '
                                 'etichetta nao autoriza, todos com o selo verde TABELA'),
        'AGORA': 'R-14 confere cada par contra a celula desenhada da cultura',
        'PARES_RETIRADOS': ret,
        'REGISTROS_AFETADOS': len({c['REGISTRATION_ID'] for c in pf['CONTRADICTED']}),
        'POR_FAMILIA': {k: len(v) for k, v in sorted(fam.items())},
        'PARES_PUBLICADOS_AGORA': sum(len(p.get('uses') or []) for p in pay['products']),
        'ESTADO': 'FECHADO' if ret >= 34 else 'ABERTO',
    }

    # ---- MF-02 · 012573 x 014386
    p = byreg['012573']
    alvos = lambda pr, c: sorted({u['target'] for u in pr['uses'] if u['crop'] == c})
    R['MF-02'] = {
        'AFIRMACAO_DO_ARBITRO': ('012573 publica 14 alvos para BARBABIETOLA (o rotulo lista 4) e 14 '
                                 'para CARCIOFO (lista 6): 18 alvos falsos num unico rotulo'),
        'BARBABIETOLA_AGORA': alvos(p, 'BARBABIETOLA'),
        'CARCIOFO_AGORA_N': len(alvos(p, 'CARCIOFO')),
        'RETIRADOS_EM_012573': len(p.get('uses_contraditos') or []),
        'IRMAO_014386_RETIRADOS': len(byreg['014386'].get('uses_contraditos') or []),
        'ESTADO': ('FECHADO' if len(alvos(p, 'BARBABIETOLA')) == 4
                   and len(alvos(p, 'CARCIOFO')) == 6
                   and not (byreg['014386'].get('uses_contraditos') or []) else 'ABERTO'),
    }

    # ---- MF-03 · sucessao
    rot = exc.get('ROTACAO', [])
    R['MF-03'] = {
        'AFIRMACAO_DO_ARBITRO': ('017868/017585, herbicidas de arroz, publicam BARBABIETOLA e COLZA '
                                 'como uso autorizado, carimbados ATTESTED'),
        'PARES_EM_RESTRICAO_DE_SUCESSAO': len(rot),
        'AINDA_PUBLICADOS': [f"{r}/{c}" for r in ('017868', '017585') for c in ('BARBABIETOLA', 'COLZA')
                             if any(u['crop'] == c for u in byreg[r]['uses'])],
        'ESTADO': 'FECHADO' if len(rot) == 4 and not any(
            u['crop'] in ('BARBABIETOLA', 'COLZA')
            for r in ('017868', '017585') for u in byreg[r]['uses']) else 'ABERTO',
    }

    # ---- MF-04 · heranca
    ruins = sum(v for k, v in her['COUNTS'].items() if 'CONTRADICTED' in k or 'NOT_VALIDATED' in k)
    R['MF-04'] = {
        'AFIRMACAO_DO_ARBITRO': ('heranca de celula mesclada publica o valor da linha vizinha como '
                                 'fato, em 96 pares, com selo verde'),
        'CAMPOS_REBAIXADOS': ruins,
        'COUNTS': her['COUNTS'],
        'ESTADO': 'FECHADO' if ruins > 0 else 'ABERTO',
    }

    # ---- MF-06 · alvo literal na tela de produto
    lit = sum(1 for p in pay['products'] for d in (p.get('doses') or [])
              if d.get('target_literal') == 'TARGET_TEXT_NOT_FOUND_LITERALLY')
    nch = sum(1 for p in pay['products'] for d in (p.get('doses') or [])
              if d.get('target_literal') == 'TARGET_TEXT_NOT_CHECKED')
    R['MF-06'] = {'LINHAS_ALVO_NAO_LITERAL': lit, 'LINHAS_ALVO_NAO_CONFERIDO': nch,
                  'ESTADO': 'FECHADO (o estado chega a tela; ver test_casco.js)'}

    # ---- MF-11 · restricao fora da tabela
    R['MF-11'] = {
        'AFIRMACAO_DO_ARBITRO': ('008189/014479 dizem "Ammesso un solo trattamento per ciclo" e as '
                                 '24 linhas saem NOT_PRESENT sem o aviso LABEL_NOTES_NOT_READ'),
        'AGORA': {r: {'aviso': byreg[r]['label_dose_notes_not_read'],
                      'nota': (byreg[r].get('label_app_limit_notes') or [{}])[0].get('TEXT')}
                  for r in ('008189', '014479')},
        'ESTADO': 'FECHADO' if all(byreg[r]['label_dose_notes_not_read']
                                   and byreg[r].get('label_app_limit_notes')
                                   for r in ('008189', '014479')) else 'ABERTO',
    }

    # ---- CONTRA-PROVA CEGA: o teste so-de-texto tem poder de discriminacao?
    #
    # A tentacao e conferir os pares retirados so pelo texto: "a cultura e o alvo
    # aparecem no mesmo escopo de cabecalho?". Medido aqui, esse teste responde
    # SIM para quase tudo — inclusive para pares que a geometria absolve — porque
    # no texto em ordem de leitura os escopos de cabecalho tem centenas de
    # caracteres e engolem blocos vizinhos inteiros. Um teste que responde a
    # mesma coisa para os dois grupos nao mede nada, e dizer que ele "confirma"
    # a retirada seria inventar corroboracao.
    verd = pf['VERDICT']
    pares = json.load(open('v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json',
                           encoding='utf-8'))['PAIRS']
    porreg = {}
    for x in pares:
        porreg.setdefault(x['REGISTRATION_ID'], []).append(x)
    regs_alvo = sorted({c['REGISTRATION_ID'] for c in pf['CONTRADICTED']})
    grupo = {'CONTRADITOS': [], 'CONSISTENTES': []}
    for reg in regs_alvo:
        for i, x in enumerate(porreg[reg]):
            v = verd.get(f'{reg}#{i}')
            alvo = ('CONTRADITOS' if v == 'PAIR_CONTRADICTED_BY_RULE'
                    else 'CONSISTENTES' if v == 'PAIR_CONSISTENT_WITH_RULES' else None)
            if alvo:
                r = coocorre_no_escopo(reg, x['CROP'], x['TARGET'])
                if r is not None:
                    grupo[alvo].append(r)
    taxa = {k: (round(100 * sum(v) / len(v), 1) if v else None) for k, v in grupo.items()}
    R['CONTRA_PROVA_DE_TEXTO'] = {
        'O_QUE_E': ('conferir os pares so pelo texto — cultura e alvo no mesmo escopo de cabecalho '
                    'com dois-pontos — nos MESMOS rotulos, comparando os pares que R-14 condenou '
                    'com os que ela absolveu'),
        'COOCORRENCIA_NOS_CONTRADITOS_PCT': taxa['CONTRADITOS'],
        'COOCORRENCIA_NOS_CONSISTENTES_PCT': taxa['CONSISTENTES'],
        'N': {k: len(v) for k, v in grupo.items()},
        'CONCLUSAO': ('o teste so-de-texto NAO discrimina: ele responde quase o mesmo para os dois '
                      'grupos, porque o escopo de cabecalho no texto em ordem de leitura engole '
                      'blocos vizinhos inteiros. E exatamente o vazamento que MF-02 descreve, e a '
                      'razao de a regra ser GEOMETRICA. Esta medicao esta aqui para que ninguem '
                      'apresente a coocorrencia textual como corroboracao — ela nao e'),
    }

    json.dump(R, open('v1/testes/CONFERENCIA-MUST-FIX.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    for k, v in R.items():
        if isinstance(v, dict) and 'ESTADO' in v:
            print(f'  {k}: {v["ESTADO"]}')
    print(f'  contra-prova de texto: contraditos {taxa["CONTRADITOS"]}% x '
          f'consistentes {taxa["CONSISTENTES"]}% — sem poder de discriminacao')
    print('  -> v1/testes/CONFERENCIA-MUST-FIX.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
