#!/usr/bin/env python3
"""
ITÁLIA — cruzamento ADAMA × CULTURA × ALVO, a partir do rótulo oficial.

Este é o único lugar do repositório onde `ADAMA REGISTERED RESPONSE` para a Itália
pode ser afirmado, e a razão é simples: o rótulo é o documento que diz o que a
autorização permite. Site de fabricante diria outra coisa — diria o que o fabricante
comunica — e as duas coisas não se misturam.

    REGULATORY_FACT              o rótulo autorizado (aqui)
    MANUFACTURER_TECHNICAL_CLAIM o que o fabricante afirma tecnicamente
    MANUFACTURER_COMMERCIAL_CLAIM o que o fabricante comunica comercialmente
    DERIVED_INTERPRETATION       o que nós derivamos

O que sai daqui é a PRIMEIRA classe. As outras três não foram coletadas para a Itália
nesta rodada — e a razão está declarada no relatório: `adama.com` responde 403 a este
ambiente, inclusive em `/robots.txt`. Bloqueio de origem não é ausência de portfólio,
e não autoriza preencher a lacuna com o que se imagina que o site diria.

`CROP_TERM_PRESENT` NÃO é `AUTHORIZED_ON_CROP`: o rótulo cita a cultura, mas a
associação cultura↔alvo mora numa coluna de tabela que a extração de PDF perde.
O nome do campo carrega essa ressalva de propósito.
"""
import json
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import italia_rotulo_parse as rp  # noqa: E402

PDF_DIR = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                         'IT-T4-001-etichette-manifest.json')


def indice_manifesto():
    if not os.path.exists(MANIFESTO):
        return {}
    d = json.load(open(MANIFESTO, encoding='utf-8'))
    return {r['REGISTRATION_ID']: r for r in d.get('LABELS', []) if r.get('STATE') == 'OK'}


def analisar_todos():
    idx = indice_manifesto()
    produtos, falhas = [], []
    for f in sorted(os.listdir(PDF_DIR)):
        if not f.endswith('.pdf'):
            continue
        reg = f.split('_')[0]
        try:
            r = rp.analisar(os.path.join(PDF_DIR, f))
        except Exception as e:                                  # noqa: BLE001
            falhas.append({'REGISTRATION_ID': reg, 'ERROR': str(e)[:120]})
            continue
        m = idx.get(reg, {})
        produtos.append({
            'REGISTRATION_ID': reg,
            'PRODUCT': m.get('PRODUCT'), 'HOLDER': m.get('HOLDER'),
            'ACTIVE_SUBSTANCE': m.get('ACTIVE_SUBSTANCE'),
            'EXPIRY': m.get('EXPIRY'), 'STATUS': m.get('STATUS'),
            'LABEL_DATE': m.get('LABEL_DATE'), 'LABEL_URL': m.get('LABEL_URL'),
            'EXTRACTION_STATE': r['EXTRACTION_STATE'],
            # Só entra como presença quem tem contexto de USO. Quem só aparece em
            # cláusula de sucessão vai para outro campo e NUNCA se soma ao primeiro.
            'CROP_TERMS_PRESENT': sorted(c for c, d in r['CROP_TERMS_PRESENT'].items()
                                         if d['STATE'] == 'CROP_TERM_PRESENT'),
            'CROP_TERMS_ROTATION_ONLY': sorted(c for c, d in r['CROP_TERMS_PRESENT'].items()
                                               if d['STATE'] == 'ROTATION_CONTEXT_ONLY'),
            'MODE_OF_ACTION_DECLARED': r['MODE_OF_ACTION_DECLARED'],
            'MODE_OF_ACTION_EXTRACTION': r['MODE_OF_ACTION_EXTRACTION'],
            'CATEGORY_REGULATORY': (m.get('CATEGORY') or ''),
            'ISSUES_FROM_SOURCE': r['ISSUES_FROM_SOURCE'],
        })
    return produtos, falhas


# ---------------------------------------------------------------- cobertura por estágio
#
# Uma métrica só, chamada COVERAGE, media DOWNLOAD e era lida como LEITURA: o artefato
# declarava `163/163 COMPLETE` com `PARSE_FAILURES = 0` enquanto 40 produtos saíam sem uma
# cultura e sem um alvo. As leis que este bloco existe para tornar impossíveis de ignorar:
#
#     163/163 DOWNLOADED  não implica  163/163 READ
#     163/163 READ        não implica  163/163 USE_ROWS_STRUCTURED
#     PARSER_FAILURE   != ABSENCE
#     ZERO_PARSED_ROWS != ZERO_AUTHORIZED_USES
#
# Isto mora no GERADOR, não só no arquivo gerado: uma correção que vive apenas no artefato
# é apagada na próxima execução, e a régua volta a mentir sem ninguém tocar em nada.

PARES_V3 = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'IT-ROTULOS-PARES-V3.json')
TESTO = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'testo')
# Um .txt de rotulo tem sempre milhares de bytes. O piso existe porque
# `os.path.exists` da True para um ficheiro vazio, e um ficheiro vazio nao prova
# que o rotulo diz alguma coisa. EXISTE != TEM CONTEUDO.
MIN_BYTES_DO_TEXTO = 1000
# O parser conhece 17 termos de cultura. Um rotulo que so declara AGRUMI sai
# "nao lido" — e o que falta e o VOCABULARIO, nao a leitura.
FORA_DO_VOCABULARIO = ('agrum', 'carciofo', 'cavolo', 'cetriolo', 'cocomero',
                       'fagiolo', 'mandorlo', 'carota', 'melanzana', 'pisello',
                       'tabacco', 'zucchino', 'sedano', 'finocchio')


def _cobertura_antiga_depreciada():
    return {
        'DEPRECATED': True,
        'WHY': ('Uma metrica so, chamada COVERAGE, media DOWNLOAD e era lida como LEITURA. '
                'Declarava 163/163 COMPLETE com PARSE_FAILURES=0 enquanto 40 produtos saiam '
                'sem uma cultura e sem um alvo. Substituida pelos seis estagios abaixo.'),
        'SUBSTITUIDA_POR': ['LABEL_DISCOVERY_COVERAGE', 'LABEL_DOWNLOAD_COVERAGE',
                            'TEXT_EXTRACTION_COVERAGE', 'LABEL_READ_COVERAGE',
                            'CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE',
                            'MODE_OF_ACTION_DECLARED_COVERAGE'],
        'E_TAMBEM_POR': ['COBERTURA_DO_LEITOR_CANONICO — outro leitor, fora da escada'],
    }


def _mudos(produtos):
    """Produtos que saem deste artefato sem UMA cultura e sem UM alvo."""
    return [p for p in produtos
            if not p.get('CROP_TERMS_PRESENT') and not p.get('ISSUES_FROM_SOURCE')]


def _pares_v3():
    if not os.path.exists(PARES_V3):
        return None
    with open(PARES_V3, encoding='utf-8') as fh:
        return json.load(fh)


def _estagio(obtido, alvo, mede, **extra):
    e = {'OBTAINED': obtido, 'TARGET': alvo,
         'PCT': round(100.0 * obtido / alvo, 1) if alvo else None, 'MEDE': mede}
    e.update(extra)
    return e


def _textos_no_repo():
    """Os .txt de rotulo que existem E tem conteudo. Medido no disco, nunca assumido."""
    if not os.path.isdir(TESTO):
        return {}
    fora = {}
    for nome in os.listdir(TESTO):
        if nome.endswith('.txt'):
            caminho = os.path.join(TESTO, nome)
            tamanho = os.path.getsize(caminho)
            if tamanho >= MIN_BYTES_DO_TEXTO:
                fora[nome[:-4]] = tamanho
    return fora


def _cobertura_por_estagio(produtos, manifesto):
    # `ATTEMPTED` e `TARGET_TOTAL` sao numeros DIFERENTES no manifesto, e a
    # descoberta e o primeiro: quantos rotulos se tentou alcancar contra quantos o
    # registo declara. Publicar OBTAINED := TARGET fazia o primeiro degrau da
    # escada ser 100% para qualquer entrada — um degrau que nao pode falhar nao
    # mede nada, e e justamente o degrau em que se confia para dizer "achamos todos".
    alvo = manifesto.get('TARGET_TOTAL') or len(produtos)
    tentados = manifesto.get('ATTEMPTED')
    baixados = manifesto.get('LABELS_OBTAINED') or len(produtos)
    textos = _textos_no_repo()
    est = {
        'LABEL_DISCOVERY_COVERAGE': _estagio(
            tentados if tentados is not None else len(produtos), alvo,
            'rotulos que se tentou alcancar, contra os que o registo nacional declara'),
        'LABEL_DOWNLOAD_COVERAGE': _estagio(
            baixados, alvo, 'PDF efetivamente baixado e com sha256 conferido'),
        'TEXT_EXTRACTION_COVERAGE': _estagio(
            len(textos) if textos else len(produtos), alvo,
            'ficheiro de texto com >= %d bytes em data/samples/IT-ROTULOS-V1/testo/'
            % MIN_BYTES_DO_TEXTO),
        'LABEL_READ_COVERAGE': _estagio(
            sum(1 for p in produtos
                if p.get('CROP_TERMS_PRESENT') or p.get('ISSUES_FROM_SOURCE')),
            alvo,
            'este artefacto produziu pelo menos uma cultura OU um alvo. NAO e "lido": '
            'e o que o vocabulario FECHADO de 17 termos alcanca'),
        'CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE': _estagio(
            sum(1 for p in produtos
                if p.get('CROP_TERMS_PRESENT') and p.get('ISSUES_FROM_SOURCE')),
            alvo,
            'o rotulo tem ALGUMA cultura E ALGUM alvo, em qualquer parte do texto',
            NAO_E=('AUTHORIZED_USE_ROW. Esse termo ja tem dono nesta casa e vale 19: '
                   'cultura, alvo e dose na MESMA linha da tabela '
                   '(ITALY-ADAMA-REGULATORY-INTELLIGENCE.json, LINK_CLASSES). Usar o '
                   'mesmo nome para uma conjuncao de presencas inflava 19 para 96')),
    }
    est['MODE_OF_ACTION_DECLARED_COVERAGE'] = _estagio(
        sum(1 for p in produtos if p.get('MODE_OF_ACTION_DECLARED')), alvo,
        'o rotulo declara grupo de acao HRAC/FRAC/IRAC')
    return est


def _cobertura_do_leitor_canonico(produtos):
    """NAO e um degrau desta escada — e outro leitor, e por isso mora fora dela.

    `USE_ROWS_STRUCTURED = 128` vinha dentro de `COBERTURA_POR_ESTAGIO`, depois de
    `READ = 123`, e lia-se como o degrau seguinte. Nao e: 128 > 123, e 31 dos 40 que
    ESTE artefacto nao leu estao dentro dos 128. Sao dois leitores medindo o mesmo
    universo, nao dois estagios do mesmo leitor.
    """
    v3 = _pares_v3()
    if not v3:
        return None
    com_par = {p['REGISTRATION_ID'] for p in v3['PAIRS']}
    universo = {p['REGISTRATION_ID'] for p in produtos}
    return {
        'DATASET': 'IT-ROTULOS-PARES-V3',
        'LEITOR': v3.get('PARSER_VERSION'),
        'NAO_E_DERIVADO_DESTE_ARTEFACTO': (
            'o numerador vem do leitor canonico e o denominador deste portfolio; '
            'os dois descrevem o mesmo universo de rotulos, e isso e conferido abaixo'),
        'ROTULOS_COM_PAR': len(com_par & universo),
        'UNIVERSO': len(universo),
        'PCT': round(100.0 * len(com_par & universo) / len(universo), 1) if universo else None,
        'UNIVERSOS_BATEM': not (com_par - universo),
    }


def _divida_de_leitura(produtos):
    """Os mudos deste artefato, com a razão pela qual mudo NÃO é ausência.

    E com a razao SEPARADA para aqueles em que ela ainda nao existe. Dizer "nunca do
    rotulo" para os 40 generalizava uma prova que so cobre 31: para os outros 9
    nenhum leitor da casa produziu par nenhum, e "nao sei" nao pode virar "e divida"
    so porque essa e a direcao lisonjeira. `UNCONFIRMED_SILENCE != DEBT != ABSENCE`.
    """
    mudos = _mudos(produtos)
    ids = sorted(p['REGISTRATION_ID'] for p in mudos)
    v3 = _pares_v3()
    # Pertenca POSITIVA. `r not in sem_par` dava por lido pelo canonico qualquer
    # registo que o canonico nunca tivesse visto — bastava o universo divergir de um.
    com_par = {p['REGISTRATION_ID'] for p in v3['PAIRS']} if v3 else set()
    textos = _textos_no_repo()
    com_texto = sorted(r for r in ids if r in textos)
    # DUAS provas independentes de que a divida e do parser, nao do rotulo:
    # o leitor canonico leu par no mesmo rotulo, OU o vocabulario da propria casa
    # acha a cultura no texto arquivado, fora de contexto de rotacao.
    por_leitor = {r for r in ids if r in com_par}
    por_texto = {r for r in ids if r not in por_leitor and _culturas_no_texto_arquivado(r)}
    ja_lidos = sorted(por_leitor | por_texto)
    mudos_de_verdade = sorted(r for r in ids if r not in por_leitor and r not in por_texto)
    fora_vocab = sorted(
        r for r in mudos_de_verdade
        if r in textos and _cita_cultura_fora_do_vocabulario(r))
    return {
        'COUNT': len(ids),
        'CLASSE': 'READ/STRUCTURING_DEBT',
        'NAO_E': 'REGULATORY_ABSENCE',
        'POR_QUE': ('Os %d produtos abaixo saem deste artefacto sem cultura e sem alvo. '
                    'Para %d deles a divida esta PROVADA: o leitor canonico '
                    'IT-ROTULOS-PARES-V3 leu par cultura x alvo no mesmo rotulo, logo o '
                    'silencio e do parser deste artefacto e dizer ABSENCE seria afirmar '
                    'que a ADAMA nao registou uso onde ela registou. Para os outros %d '
                    'nenhum leitor da casa produziu par: eles ficam em NAO SEI, e nao em '
                    'divida nem em ausencia.'
                    % (len(ids), len(ja_lidos), len(mudos_de_verdade))),
        'REGISTRATION_IDS': ids,
        'COM_TEXTO_INTEGRAL_NO_REPO': len(com_texto),
        'MIN_BYTES_DO_TEXTO': MIN_BYTES_DO_TEXTO,
        'CONFIRMED_PARSER_DEBT': {
            'COUNT': len(ja_lidos),
            'IDS': ja_lidos,
            'PROVA_POR_LEITOR_CANONICO': sorted(por_leitor),
            'PROVA_POR_TEXTO_ARQUIVADO': sorted(por_texto),
            'PROVA': ('duas provas independentes, e basta uma: o leitor canonico produziu '
                      'par cultura x alvo no mesmo rotulo, OU o vocabulario fechado desta '
                      'casa acha a cultura no texto arquivado fora de contexto de rotacao. '
                      'Nos dois casos o silencio e da extracao, nao do rotulo.'),
        },
        'UNCONFIRMED_SILENCE': {
            'COUNT': len(mudos_de_verdade),
            'IDS': mudos_de_verdade,
            'O_QUE_SE_SABE_DE_CADA': {r: _o_que_se_sabe(r) for r in mudos_de_verdade},
            'CLASSE': 'NAO SEI',
            'NAO_E': 'REGULATORY_ABSENCE nem READ/STRUCTURING_DEBT',
            'POR_QUE': ('nem o leitor canonico nem o vocabulario da casa acham cultura no '
                        'texto arquivado. NAO SEI aqui e sobre a NOSSA leitura, e cada um '
                        'destes tem razao propria escrita abaixo — "nao sei" generico sobre '
                        'um ficheiro que temos em disco e nao ter olhado.'),
            'SUSPEITA_DE_VOCABULARIO': {
                'COUNT': len(fora_vocab),
                'IDS': fora_vocab,
                'POR_QUE': ('o texto cita cultura que o vocabulario FECHADO de 17 termos '
                            'nao tem (agrumi, carciofo, mandorlo...). Se for isso, a divida '
                            'e de VOCABULARIO e nao de geometria de tabela.'),
            },
        },
    }


def _cita_cultura_fora_do_vocabulario(registro):
    caminho = os.path.join(TESTO, registro + '.txt')
    if not os.path.exists(caminho):
        return False
    with open(caminho, encoding='utf-8', errors='replace') as fh:
        baixo = fh.read().lower()
    return any(t in baixo for t in FORA_DO_VOCABULARIO)


def _o_que_se_sabe(registro):
    """O pouco que o texto arquivado diz, medido — nunca "nao sei" em branco.

    Um `NAO SEI` sem razao sobre um ficheiro que temos em disco e uma confissao de
    nao ter olhado. Estes dois campos sao medidos no texto, nao redigidos.
    """
    caminho = os.path.join(TESTO, registro + '.txt')
    if not os.path.exists(caminho):
        return {'TEXTO_ARQUIVADO': 'AUSENTE'}
    with open(caminho, encoding='utf-8', errors='replace') as fh:
        baixo = fh.read().lower()
    fora = sorted({t for t in FORA_DO_VOCABULARIO if t in baixo})
    return {
        'E_COADIUVANTE': 'coadiuvante' in baixo,
        'CITA_CULTURA_FORA_DO_VOCABULARIO': fora,
        'LEITURA': ('coadjuvante declarado: usa-se em mistura com outros produtos e nao '
                    'tem cultura propria — o silencio e do documento'
                    if 'coadiuvante' in baixo else
                    'o texto cita cultura(s) que o vocabulario fechado de 17 termos nao '
                    'tem: %s — divida de VOCABULARIO, nao de leitura' % ', '.join(fora)
                    if fora else
                    'nem o leitor canonico nem o vocabulario da casa acham cultura neste '
                    'texto; fica NAO SEI de verdade'),
    }


def _culturas_no_texto_arquivado(registro):
    """As culturas que o vocabulário DA CASA encontra no texto que a casa guardou.

    Existe porque a primeira versão desta classificação perguntava só ao leitor
    canónico e mandava para `NAO SEI` tudo o que ele não tivesse visto — e o texto
    arquivado respondia. `015630` tem uma secção literal `COLTURE AUTORIZZATE` com
    `VITE / Contro peronospora (Plasmopara viticola): impiegare 270 g/ha`, e estava
    publicado como «não sei se o rótulo declara uso». Não saber o que está escrito no
    ficheiro que se cita como prova não é `NAO SEI`: é não ter olhado.
    """
    caminho = os.path.join(TESTO, registro + '.txt')
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding='utf-8', errors='replace') as fh:
        texto = fh.read()
    try:
        import italia_rotulo_parse as rp
    except ImportError:
        return []
    achadas = set()
    for cultura, padroes in rp.CROP_TERMS.items():
        for padrao in padroes:
            for m in re.finditer(padrao, texto, re.I):
                antes = texto[max(0, m.start() - 120):m.start()]
                if not rp.CONTEXTO_ROTACAO.search(antes):
                    achadas.add(cultura)
                    break
    return sorted(achadas)


def artefato():
    """Escreve o gêmeo REGULATÓRIO do portfólio italiano. Não é o gêmeo do site."""
    import datetime
    produtos, falhas = analisar_todos()
    pc = por_cultura(produtos)
    moa = {}
    for p in produtos:
        for esq, gs in (p.get('MODE_OF_ACTION_DECLARED') or {}).items():
            for g in gs:
                moa['%s %s' % (esq, g)] = moa.get('%s %s' % (esq, g), 0) + 1
    d = json.load(open(MANIFESTO, encoding='utf-8')) if os.path.exists(MANIFESTO) else {}
    out = {
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'WHAT_THIS_IS': ('Gêmeo REGULATÓRIO do portfólio ADAMA italiano, lido no rótulo '
                         'autorizado. NÃO é o gêmeo do site do fabricante: adama.com '
                         'devolve 403 a este ambiente e a camada de afirmação comercial '
                         'continua NOT_COLLECTED.'),
        'LABEL_COVERAGE': _cobertura_antiga_depreciada(),
        'LABELS_PARSED': len(produtos),
        'PARSE_FAILURES': {
            'VALOR_ANTIGO': 0,
            'POR_QUE_MUDOU': ('PARSE_FAILURES=0 contava excecoes, nao rendimento. Nenhum PDF '
                              'rebentou; 40 produziram zero linhas. Zero excecoes com zero '
                              'linhas e divida de leitura, e agora esta contada como tal.'),
            'EXCECOES': len(falhas),
            'ZERO_ROW_YIELD': len(_mudos(produtos)),
        },
        'CROP_TERM_CONTRACT': ('CROP_TERM_PRESENT = o termo aparece em contexto de uso. '
                               'NÃO É AUTHORIZED_ON_CROP: a coluna cultura↔alvo da tabela '
                               'de doses não foi reconstruída a partir do PDF.'),
        'BY_CROP_TERM': pc,
        'MODE_OF_ACTION_GROUPS_DECLARED': dict(sorted(moa.items(), key=lambda kv: -kv[1])),
        'PRODUCTS': produtos,
        'LEI_DA_COBERTURA': [
            'DOWNLOADED nao implica READ',
            'READ nao implica USE_ROWS_STRUCTURED',
            'PARSER_FAILURE != ABSENCE',
            'ZERO_PARSED_ROWS != ZERO_AUTHORIZED_USES',
            'UNCONFIRMED_SILENCE != DEBT != ABSENCE',
        ],
        'COBERTURA_POR_ESTAGIO': _cobertura_por_estagio(produtos, d),
        'COBERTURA_DO_LEITOR_CANONICO': _cobertura_do_leitor_canonico(produtos),
        'READ_STRUCTURING_DEBT': _divida_de_leitura(produtos),
    }
    dest = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                        'IT-T4-001-portfolio-rotulo.json')
    with open(dest, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    return dest, out


def por_cultura(produtos):
    out = {}
    for p in produtos:
        for c in p['CROP_TERMS_PRESENT']:
            d = out.setdefault(c, {'PRODUCTS': [], 'SUBSTANCES': set(), 'ISSUES': {}})
            d['PRODUCTS'].append(p['PRODUCT'])
            for s in (p['ACTIVE_SUBSTANCE'] or '').split('|'):
                if s.strip() and s.strip() != '-':
                    d['SUBSTANCES'].add(s.strip())
            for i in p['ISSUES_FROM_SOURCE']:
                k = i['SCIENTIFIC_NAME']
                e = d['ISSUES'].setdefault(k, {'SCIENTIFIC_NAME': k,
                                               'VERNACULAR_IT': i['ISSUE_VERNACULAR_IT'],
                                               'PRODUCTS': 0})
                e['PRODUCTS'] += 1
    for c, d in out.items():
        d['PRODUCT_COUNT'] = len(d['PRODUCTS'])
        d['SUBSTANCES'] = sorted(d['SUBSTANCES'])
        d['ISSUES'] = sorted(d['ISSUES'].values(), key=lambda x: -x['PRODUCTS'])
        d['CONTRACT'] = ('CROP_TERM_PRESENT no rótulo. NÃO significa autorização para '
                         'todos os alvos listados: a coluna cultura↔alvo não foi reconstruída.')
    return dict(sorted(out.items(), key=lambda kv: -kv[1]['PRODUCT_COUNT']))


def main():
    if '--artefato' in sys.argv:
        dest, out = artefato()
        print('escrito %s' % os.path.relpath(dest, ROOT))
        est = out['COBERTURA_POR_ESTAGIO']
        print('rotulos %d | baixados %s%% | LIDOS %s%% | cultura E alvo %s%%'
              % (out['LABELS_PARSED'],
                 est['LABEL_DOWNLOAD_COVERAGE']['PCT'],
                 est['LABEL_READ_COVERAGE']['PCT'],
                 est['CROP_TERM_AND_ISSUE_BOTH_PRESENT_COVERAGE']['PCT']))
        return
    produtos, falhas = analisar_todos()
    pc = por_cultura(produtos)
    print('ETICHETTAS ANALISADAS: %d (falhas %d)' % (len(produtos), len(falhas)))
    print('\nCULTURA (presença de termo)      PRODUTOS  SUBSTÂNCIAS  ALVOS')
    for c, d in pc.items():
        print('  %-28s %6d %10d %8d' % (c, d['PRODUCT_COUNT'], len(d['SUBSTANCES']),
                                        len(d['ISSUES'])))
    if 'MAIZE' in pc:
        d = pc['MAIZE']
        print('\nMILHO — %d produtos, %d substâncias' % (d['PRODUCT_COUNT'], len(d['SUBSTANCES'])))
        print('  substâncias:', ', '.join(d['SUBSTANCES'][:14]))
        print('  alvos mais recorrentes:')
        for i in d['ISSUES'][:12]:
            print('    %-30s %s (%d produtos)' % (i['VERNACULAR_IT'][:30],
                                                  i['SCIENTIFIC_NAME'], i['PRODUCTS']))


if __name__ == '__main__':
    main()
