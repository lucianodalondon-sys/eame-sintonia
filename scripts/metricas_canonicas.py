#!/usr/bin/env python3
"""
LEDGER DE MÉTRICAS CANÔNICAS — todo número publicável tem um dono que o deriva.

O problema que este arquivo resolve: a MISSÃO 08 fechou com 91 provas e três documentos
ainda diziam "25 provas automatizadas". O atlas tinha 35 SOURCE_IDs e dois documentos
diziam 31. A amostra cega de X-006 dava 62,2% / 77,8% e um documento publicava
62,5% / 77,4%. Nenhum desses números era falso quando foi escrito — todos foram
**digitados**, e um número digitado envelhece em silêncio.

Aqui cada métrica declara:

    METRIC_ID          nome estável, usado nos testes
    VALUE              o valor, derivado agora
    DENOMINATOR        contra o que ele é medido (ou None quando é contagem absoluta)
    UNIT               count · pct · date · text
    SOURCE             o arquivo que é DONO do número
    SOURCE_VERSION     a versão daquele dono
    DERIVATION         como se chega ao valor a partir do dono
    REFERENCE_DATE     a data a que o valor se refere (nunca "hoje" implícito)
    STATUS             DERIVED · DECLARED · HISTORICAL

POLÍTICA DE ARREDONDAMENTO — única, para todos os consumidores:
  · percentuais com **uma casa decimal**, arredondamento padrão do Python (banker's);
  · derivados de contagens brutas, **nunca** de percentuais já arredondados;
  · cobertura ponderada por uso = 100 − peso do balde não resolvido, calculada dos brutos.

    python3 scripts/metricas_canonicas.py            # tabela legível
    python3 scripts/metricas_canonicas.py --json     # máquina
"""
import datetime
import gzip
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
DOCS = os.path.join(ROOT, 'docs')

# Data de referência do snapshot espanhol. Explícita de propósito: usar `hoje` faria o
# mesmo comando devolver números diferentes amanhã sem que nada tivesse mudado na fonte.
ES_REFERENCE_DATE = datetime.date(2026, 8, 29)


def _sample(name):
    with open(os.path.join(SAMPLES, name), encoding='utf-8') as f:
        return json.load(f)


def _doc(*p):
    with open(os.path.join(DOCS, *p), encoding='utf-8') as f:
        return f.read()


def _ropf():
    with gzip.open(os.path.join(SAMPLES, 'ES-T4-005', 'ropf_20260829.json.gz'),
                   'rt', encoding='utf-8') as f:
        return json.load(f)


def _d(s):
    try:
        return datetime.datetime.strptime(s, '%d-%m-%Y').date()
    except (ValueError, TypeError):
        return None


def pct(part, whole):
    return round(100.0 * part / whole, 1) if whole else None


class Ledger(dict):
    def add(self, metric_id, value, *, unit, source, derivation,
            denominator=None, source_version=None, reference_date=None,
            status='DERIVED'):
        self[metric_id] = {
            'METRIC_ID': metric_id, 'VALUE': value, 'DENOMINATOR': denominator,
            'UNIT': unit, 'SOURCE': source, 'SOURCE_VERSION': source_version,
            'DERIVATION': derivation, 'REFERENCE_DATE': reference_date,
            'STATUS': status,
        }
        return value


def build():
    L = Ledger()

    # ---------------------------------------------------------------- provas
    suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, 'tests'))
    L.add('TEST_COUNT_CURRENT', suite.countTestCases(), unit='count',
          source='tests/', derivation='unittest.defaultTestLoader.discover().countTestCases()')

    # ---------------------------------------------------------------- fontes
    atlas = _doc('fontes', 'ATLAS-DE-FONTES-EAME.md')
    ids = set()
    for m in re.finditer(r'^SOURCE_ID:\s+(\S[^\n#]*)', atlas, re.M):
        raw = m.group(1).strip()
        if raw.startswith('#') or '<' in raw:
            continue
        for part in re.split(r'[·/]', re.sub(r'\(.*?\)', '', raw)):
            if re.fullmatch(r'(EU|FR|ES|IT)-T\d{1,2}-\d{3}', part.strip()):
                ids.add(part.strip())
    for m in re.finditer(r'\|\s*((?:EU|FR|ES|IT)-T\d{1,2}-\d{3})\s*\|', atlas):
        ids.add(m.group(1))
    L.add('SOURCE_ID_COUNT', len(ids), unit='count',
          source='docs/fontes/ATLAS-DE-FONTES-EAME.md',
          derivation='SOURCE_IDs distintos nas fichas + tabelas de fontes não alcançadas')
    # "ficha" = cabeçalho de nível 4 que abre um bloco SOURCE_ID. Duas seções de nível 4
    # são tabelas de fontes testadas e não alcançadas, não fichas — e uma ficha
    # (FR/ES/IT-T9-001) cobre três SOURCE_IDs. Por isso ficha ≠ SOURCE_ID.
    fichas_atlas = [h for h in re.findall(r'^#### (.+)$', atlas, re.M)
                    if re.match(r'(EU|FR|ES|IT)[-/]', h)]
    L.add('SOURCE_FICHA_COUNT', len(fichas_atlas), unit='count',
          source='docs/fontes/ATLAS-DE-FONTES-EAME.md',
          derivation='cabeçalhos "#### <ID> · <nome>"; exclui as seções de fontes testadas '
                     'e não alcançadas, que não são fichas')
    tot = re.search(r'\| \*\*Total\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* '
                    r'\| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|', atlas)
    if tot:
        L.add('SOURCE_GREEN_COUNT', int(tot.group(1)), unit='count',
              source='docs/fontes/ATLAS-DE-FONTES-EAME.md', derivation='linha Total do placar')

    # --------------------------------------------------------- pacote do piloto
    pack = _doc('piloto', 'SOURCE-PACK-PILOTO.md')
    fichas = re.findall(r'^### ((?:EU|FR|ES|IT)-T\d{1,2}-\d{3}[^\n]*)', pack, re.M)
    L.add('PILOT_SOURCE_COUNT', len(fichas), unit='count',
          source='docs/piloto/SOURCE-PACK-PILOTO.md',
          derivation='cabeçalhos "### <SOURCE_ID> · <nome> — `<dependência>`"')
    criticas = [f for f in fichas if 'CRITICAL' in f]
    L.add('CRITICAL_SOURCE_COUNT', len(criticas), unit='count',
          source='docs/piloto/SOURCE-PACK-PILOTO.md',
          derivation='fichas do pacote cuja dependência declarada é CRITICAL')
    L.add('CRITICAL_SOURCE_IDS',
          sorted(re.match(r'((?:EU|FR|ES|IT)-T\d{1,2}-\d{3})', f).group(1) for f in criticas),
          unit='text', source='docs/piloto/SOURCE-PACK-PILOTO.md',
          derivation='idem, só os identificadores')

    # ---------------------------------------------------------------- X-006
    x6 = _sample('X-006-substance-normalisation.json')
    ff, fb = x6['france_full'], x6['france_blind']
    L.add('X006_SPELLING_COVERAGE', pct(ff['resolved'], ff['spellings']), unit='pct',
          denominator=ff['spellings'], source='data/samples/X-006-substance-normalisation.json',
          source_version=x6['captured_at'], derivation='resolved / spellings, corpus completo FR')
    L.add('X006_USE_COVERAGE', round(100.0 - ff['weighted_by_use_pct']['NONE'], 1), unit='pct',
          source='data/samples/X-006-substance-normalisation.json', source_version=x6['captured_at'],
          derivation='100 − peso do balde NONE ponderado por uso, corpus completo FR')
    L.add('X006_BLIND_SPELLING', pct(fb['resolved'], fb['spellings']), unit='pct',
          denominator=fb['spellings'], source='data/samples/X-006-substance-normalisation.json',
          source_version=x6['captured_at'], derivation='resolved / spellings na amostra cega (30%, semente 20260828)')
    L.add('X006_BLIND_USE', round(100.0 - fb['weighted_by_use_pct']['NONE'], 1), unit='pct',
          source='data/samples/X-006-substance-normalisation.json', source_version=x6['captured_at'],
          derivation='100 − peso do balde NONE na amostra cega')

    x7 = _sample('X-007-canonical-agro-dictionary.json')['full_corpus']
    L.add('X007_USE_COVERAGE', x7['resolved_pct_uses'], unit='pct',
          denominator=x7['uses'], source='data/samples/X-007-canonical-agro-dictionary.json',
          derivation='resolved_uses / uses do corpus francês completo')

    # ---------------------------------------------------------------- RAIF
    raif = _sample('RAIF-COORTE-REPILO.json') if os.path.exists(
        os.path.join(SAMPLES, 'RAIF-COORTE-REPILO.json')) else None
    if raif:
        for prov in ('Huelva', 'Cádiz', 'Jaén', 'Sevilla'):
            serie = raif['cohort_by_province'].get(prov, {})
            for ano in ('2023', '2026'):
                if ano in serie:
                    key = f'RAIF_{prov.upper().replace("Á","A").replace("É","E")}_COHORT_{ano}'
                    L.add(key, serie[ano]['mean'], unit='pct',
                          denominator=serie[ano]['readings'],
                          source='data/samples/RAIF-COORTE-REPILO.json',
                          source_version=raif['source_version'],
                          reference_date=raif['captured_at'],
                          derivation=f'média de repilo visível nas parcelas da coorte de '
                                     f'{raif["cohort_year"]}, {prov}, safra {ano}')
        L.add('RAIF_SEASONS_AVAILABLE', raif['seasons_available'], unit='count',
              source='data/samples/RAIF-COORTE-REPILO.json',
              derivation='safras distintas com leitura do campo de repilo em TODOS os arquivos')
        L.add('RAIF_READINGS_TOTAL', raif['readings_total'], unit='count',
              source='data/samples/RAIF-COORTE-REPILO.json',
              derivation='leituras do campo 1702 em todos os arquivos do pacote')

    # ---------------------------------------------------------------- ROPF
    ropf = _ropf()
    rows = ropf['rows']
    vig = [r for r in rows if r['Estado'] == 'Vigente']
    ver = ropf['export_server_timestamp']
    L.add('ES_ROPF_TOTAL', len(rows), unit='count', source='data/samples/ES-T4-005/ropf_20260829.json.gz',
          source_version=ver, reference_date=str(ES_REFERENCE_DATE),
          derivation='linhas do export do ROPF')
    L.add('ES_ROPF_ACTIVE', len(vig), unit='count', denominator=len(rows),
          source='data/samples/ES-T4-005/ropf_20260829.json.gz', source_version=ver,
          reference_date=str(ES_REFERENCE_DATE), derivation="campo Estado == 'Vigente'")
    adama = [r for r in vig if 'ADAMA' in (r['Titular'] or '').upper()]
    L.add('ES_ADAMA_ACTIVE', len(adama), unit='count', denominator=len(vig),
          source='data/samples/ES-T4-005/ropf_20260829.json.gz', source_version=ver,
          reference_date=str(ES_REFERENCE_DATE),
          derivation="vigentes cujo Titular contém 'ADAMA' (uma única entidade legal na ES)")

    def mais_meses(d, meses):
        """Aritmética de MÊS CALENDÁRIO, não de 30,44 dias.

        A média de dias movia a fronteira em um dia e a contagem em 23 registros, porque
        as caducidades se concentram em fim de mês. Uma janela de 6 meses tem de
        significar "até a mesma data seis meses adiante", não "até daqui a 183 dias".
        """
        mes = d.month - 1 + meses
        ano = d.year + mes // 12
        mes = mes % 12 + 1
        dia = min(d.day, [31, 29 if ano % 4 == 0 and (ano % 100 or ano % 400 == 0) else 28,
                          31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes - 1])
        return datetime.date(ano, mes, dia)

    def janela(rs, meses):
        lim = mais_meses(ES_REFERENCE_DATE, meses)
        return [r for r in rs if _d(r['StrFechaCaducidad'])
                and ES_REFERENCE_DATE <= _d(r['StrFechaCaducidad']) <= lim]
    for meses in (6, 12):
        L.add(f'ES_EXPIRING_{meses}M', len(janela(vig, meses)), unit='count', denominator=len(vig),
              source='data/samples/ES-T4-005/ropf_20260829.json.gz', source_version=ver,
              reference_date=str(ES_REFERENCE_DATE),
              derivation=f'vigentes com fechaCaducidad entre a data de referência e +{meses} meses')
        L.add(f'ES_ADAMA_EXPIRING_{meses}M', len(janela(adama, meses)), unit='count',
              denominator=len(adama), source='data/samples/ES-T4-005/ropf_20260829.json.gz',
              source_version=ver, reference_date=str(ES_REFERENCE_DATE),
              derivation=f'idem, restrito ao titular ADAMA')
    passado = [r for r in vig if _d(r['StrFechaCaducidad'])
               and _d(r['StrFechaCaducidad']) < ES_REFERENCE_DATE]
    L.add('ES_ACTIVE_WITH_PAST_EXPIRY', len(passado), unit='count', denominator=len(vig),
          source='data/samples/ES-T4-005/ropf_20260829.json.gz', source_version=ver,
          reference_date=str(ES_REFERENCE_DATE),
          derivation="Estado == 'Vigente' e fechaCaducidad anterior à data de referência")
    L.add('ES_ADAMA_WITH_PAST_EXPIRY',
          len([r for r in passado if 'ADAMA' in (r['Titular'] or '').upper()]), unit='count',
          denominator=len(passado), source='data/samples/ES-T4-005/ropf_20260829.json.gz',
          source_version=ver, reference_date=str(ES_REFERENCE_DATE), derivation='idem, titular ADAMA')

    # ------------------------------------------------------------- benchmark
    bench = _sample('ASK-SINTONIA-benchmark.json')
    t = bench['totals']
    for k, mid in (('ANSWERABLE', 'ASK_ANSWERABLE'), ('CORRECT REFUSAL', 'ASK_REFUSAL'),
                   ('PARTIAL', 'ASK_PARTIAL')):
        L.add(mid, t.get(k, 0), unit='count', denominator=len(bench['questions']),
              source='data/samples/ASK-SINTONIA-benchmark.json',
              source_version=bench['captured_at'], derivation=f'totals[{k!r}]')
    L.add('ASK_WRONG', t.get('WRONG ANSWER', 0), unit='count',
          source='data/samples/ASK-SINTONIA-benchmark.json',
          source_version=bench['captured_at'], derivation="totals['WRONG ANSWER']")
    L.add('ASK_QUESTION_COUNT', len(bench['questions']), unit='count',
          source='data/samples/ASK-SINTONIA-benchmark.json',
          source_version=bench['captured_at'], derivation='len(questions)')

    # ---------------------------------------------------------------- casos
    casos = _doc('apresentacao', 'CASOS-PARA-APRESENTACAO.md')
    L.add('CASE_COUNT', len(re.findall(r'^### CASE-\d+', casos, re.M)), unit='count',
          source='docs/apresentacao/CASOS-PARA-APRESENTACAO.md', derivation='seções "### CASE-nnn"')
    caps = _doc('capacidades', 'ATLAS-DE-CAPACIDADES-EAME.md')
    L.add('CAPABILITY_COUNT', len(re.findall(r'^CONFIDENCE:\s+COMPROVADO', caps, re.M)),
          unit='count', source='docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md',
          derivation='fichas com CONFIDENCE: COMPROVADO')

    # ------------------------------------------------------ matriz de prova
    matriz = _doc('apresentacao', 'MATRIZ-DE-PROVA-EAME.md')
    for estado, mid in (('PROVED', 'DECK_PROVED'), ('PARTIAL', 'DECK_PARTIAL'),
                        ('UNPROVED', 'DECK_UNPROVED'), ('NOT TESTABLE YET', 'DECK_NOT_TESTABLE')):
        linha = next((l for l in matriz.split('\n')
                      if l.startswith(f'| **{estado}**')), None)
        # A célula escreve "DECK-001, 002, 003, …": só o primeiro traz o prefixo e os
        # demais são números soltos. Contar `DECK-\d+` devolvia 1 e escondia justamente
        # a divergência que esta métrica existe para pegar.
        cel = linha.split('|')[3] if linha and linha.count('|') > 3 else ''
        n = len({m.group(1) for m in re.finditer(r'(?:DECK-)?(\d{3})\b', cel)})
        L.add(mid, n, unit='count', source='docs/apresentacao/MATRIZ-DE-PROVA-EAME.md',
              derivation=f'DECK-ids DISTINTOS listados na linha {estado} do placar — '
                         f'a contagem passa a ser a lista, não um número digitado ao lado')

    # ------------------------------------------------------------ camada de voz ES
    li = _sample('ES-VOICE-LINKEDIN.json')
    es = [o for o in li['ORIGINS'] if o['COUNTRY'] == 'ES']
    L.add('VOICE_ES_LINKEDIN_ORIGINS', len(li['ORIGINS']), unit='count',
          source='data/samples/ES-VOICE-LINKEDIN.json',
          derivation='len(ORIGINS) — perfis enriquecidos, antes de qualquer filtro',
          reference_date=li['captured_at'])
    L.add('VOICE_ES_LINKEDIN_ROLE_COVERAGE', pct(li['ROLE_COVERAGE']['RESOLVED'], len(es)),
          unit='pct', denominator='origens com COUNTRY=ES declarado',
          source='data/samples/ES-VOICE-LINKEDIN.json',
          derivation='RESOLVED / TOTAL — AMBIGUOUS e NOT_DECLARED ficam FORA do numerador',
          reference_date=li['captured_at'])
    L.add('VOICE_ES_PUBLIC_TECHNICAL_VOICES', li['PUBLIC_TECHNICAL_VOICE']['TOTAL'], unit='count',
          source='data/samples/ES-VOICE-LINKEDIN.json',
          derivation='origens com COUNTRY=ES + papel técnico/institucional + tópico agrícola, '
                     'todos DECLARADOS. Alcance não entra.',
          reference_date=li['captured_at'])
    L.add('VOICE_ES_OLIVE_TECHNICAL_VOICES', li['PUBLIC_TECHNICAL_VOICE']['BY_TOPIC'].get('OLIVE', 0),
          unit='count', denominator='PUBLIC_TECHNICAL_VOICE',
          source='data/samples/ES-VOICE-LINKEDIN.json',
          derivation='subconjunto com tópico OLIVE declarado — é este o número acionável '
                     'para o Lab A, não o total',
          reference_date=li['captured_at'])

    yt = _sample('ES-VOICE-YOUTUBE.json')
    L.add('VOICE_ES_YOUTUBE_ORIGINS', yt['UNIQUE_ORIGINS'], unit='count',
          source='data/samples/ES-VOICE-YOUTUBE.json',
          derivation='canais distintos — UNIQUE_ORIGINS nunca é CONTENT_COUNT',
          reference_date=yt['captured_at'])

    rot = _sample('ES-VOICE-MEDIA-ROUTES.json')
    L.add('VOICE_ES_MEDIA_ROUTES_PROVED', rot['STATE_COUNTS'].get('PROVED', 0), unit='count',
          denominator=str(len(rot['ROUTES'])) + ' rotas testadas',
          source='data/samples/ES-VOICE-MEDIA-ROUTES.json',
          derivation='rotas com itens E data. HTTP 200 sem <item> conta como FAILED_WITH_REASON',
          reference_date=rot['captured_at'])

    ig = _sample('ES-VOICE-INSTAGRAM.json')
    L.add('VOICE_ES_INSTAGRAM_ACCOUNTS_DECLARING_ES', ig['IDENTITY_MEASURE']['DECLARE_ES'],
          unit='count', denominator=str(ig['IDENTITY_MEASURE']['AGRO_ACCOUNTS']) + ' contas agronômicas',
          source='data/samples/ES-VOICE-INSTAGRAM.json',
          derivation='contas cujo texto declara Espanha. Idioma espanhol NÃO conta como país.',
          reference_date=ig['captured_at'])

    rec = _sample('ES-VOICE-x-REGUA.json')
    for camada, mid in (('YOUTUBE', 'VOICE_ES_RHO_YOUTUBE_EXPOSURE'),
                        ('LINKEDIN_POST_ROUTE', 'VOICE_ES_RHO_LINKEDIN_EXPOSURE')):
        L.add(mid, rec[camada]['rho_vs_exposure_index'], unit='text',
              denominator='n=%s províncias' % rec[camada]['n_provincias'],
              source='data/samples/ES-VOICE-x-REGUA.json',
              derivation='Spearman entre a ordem das províncias na voz e o índice de exposição '
                         '(ha × incidência). Concordância de ordem NÃO é antecipação.',
              reference_date=rec['captured_at'])
    return L


# Marcador de sincronização. Um documento escreve `<!--M:NOME-->valor<!--/M-->` e o
# comando `--sync` reescreve o valor a partir do ledger. É o que impede o número
# publicado de envelhecer sem que ninguém perceba: o teste reprova, o sync conserta.
MARK = re.compile(r'<!--M:([A-Z0-9_]+)-->(.*?)<!--/M-->', re.S)


def sync(check_only=False):
    L = build()
    mudou = []
    for dirpath, _, files in os.walk(DOCS):
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(dirpath, f)
            with open(path, encoding='utf-8') as fh:
                txt = fh.read()
            if '<!--M:' not in txt:
                continue

            def repl(m):
                mid, atual = m.group(1), m.group(2)
                v = L[mid]['VALUE'] if mid in L else atual
                if isinstance(v, float):
                    novo = ('%g' % v).replace('.', ',')
                elif isinstance(v, list):
                    novo = ' · '.join(f'`{x}`' for x in v)
                else:
                    novo = f'{v:,}'.replace(',', '.')
                if novo != atual:
                    mudou.append((os.path.relpath(path, ROOT), mid, atual, novo))
                return f'<!--M:{mid}-->{novo}<!--/M-->'
            novo_txt = MARK.sub(repl, txt)
            if novo_txt != txt and not check_only:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(novo_txt)
    return mudou


HEADER = f"{'METRIC_ID':<34}{'VALUE':>10}  {'UNIT':<6}{'DENOM':>8}  DONO"


def main():
    if '--sync' in sys.argv:
        for rel, mid, antes, depois in sync():
            print(f'{rel}: {mid} {antes!r} -> {depois!r}')
        return
    L = build()
    if '--json' in sys.argv:
        print(json.dumps(L, ensure_ascii=False, indent=1))
        return
    print(HEADER)
    print('-' * 110)
    for k, m in L.items():
        v = m['VALUE']
        v = ','.join(v) if isinstance(v, list) else v
        d = m['DENOMINATOR'] if m['DENOMINATOR'] is not None else '—'
        print(f"{k:<34}{str(v)[:10]:>10}  {m['UNIT']:<6}{str(d):>8}  {m['SOURCE']}")


if __name__ == '__main__':
    main()
