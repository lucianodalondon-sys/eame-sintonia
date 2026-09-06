import json, sys

INTERESTING = (
    'datasetCode', 'source', 'minDate', 'maxDate', 'fromDateProp', 'toDateProp',
    'propertyField', 'labelField', 'filterType', 'filterBy', 'mandatory',
    'sourcepropLab', 'sourcepropVal', 'provinceValues', 'url', 'href',
)


def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in INTERESTING and not isinstance(v, (dict, list)):
                print(f'{path}.{k} = {str(v)[:200]}')
            else:
                walk(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f'{path}[{i}]')


for path in sys.argv[1:]:
    d = json.load(open(path, encoding='utf-8'))
    print('=' * 70)
    print(path)
    print('TITLE:', d.get('title'))
    blocks = d.get('blocks') or {}
    for bid, b in blocks.items():
        t = b.get('@type')
        if t in ('slate', 'title', 'slateTable'):
            continue
        print(f'--- block @type={t}')
        walk(b, '   ')
    # plaintext blurbs often declare the real coverage
    for bid, b in blocks.items():
        pt = b.get('plaintext')
        if pt and pt.strip():
            print('   TEXT:', pt.strip()[:400].replace('\n', ' '))
