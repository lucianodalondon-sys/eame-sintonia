import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'motor'))
import voce_dal_campo as vc  # noqa: E402

so = sys.argv[1:] or None
for d in vc.documentos_do_repo():
    if so and d['EXTERNAL_ID'] not in so:
        continue
    r = vc.extrair(d)
    print('##', d['EXTERNAL_ID'], d['TEXT_LANGUAGE'], d['TITLE_LANGUAGE'], d['QUOTE_ORIGINALITY'], d['TITLE'][:50])
    for f in r['FALANTES']:
        print('   ', repr(f['SPEAKER_NAME']), f['ROLES_DECLARED'], f['ORGANIZATION'][:40], f['ORGANIZATION_KIND'],
              '|', f['SPEAKER_PLACE'][:30], '|', f['NAME_EVIDENCE'][0]['REGRA'])
    for v in r['VOZES']:
        if so:
            print('  V', v['SPEAKER_NAME'], v['ROLE'], v['STATEMENT_KIND'], v['CROP'], v['ISSUE'], '| T:', v['FACT_TIME'],
                  '| L:', v['FACT_LOCATION'], '|', v['QUOTE_ORIGINAL'][:110].replace('\n', ' '))
        for e in vc.validar_voce(v, d):
            print('  VIOL', e, v['SPEAKER_NAME'], v['PUBLISHER'])
if not so:
    print(json.dumps(vc.medir()['CONTAGEM']))
