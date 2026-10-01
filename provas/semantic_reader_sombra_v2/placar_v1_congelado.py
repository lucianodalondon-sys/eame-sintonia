# Placar do lote 30 (deterministico, so leitura). Uso: python placar.py <lote> <copia> <R1> <R2> <saida>
import json, sys, re, hashlib
lote, copia, f1, f2, saida = sys.argv[1:6]
L = json.load(open(lote, encoding='utf-8'))
S = json.load(open(copia, encoding='utf-8'))
by = {f"{r['item_id']}|{r['run_id']}|{r['ordem']}": r for r in S}
R1 = {i['ID']: i for i in json.load(open(f1, encoding='utf-8'))['ITENS']}
R2 = {i['ID']: i for i in json.load(open(f2, encoding='utf-8'))['ITENS']}
J1, J2 = json.load(open(f1, encoding='utf-8')), json.load(open(f2, encoding='utf-8'))
MES = {m: i + 1 for i, m in enumerate('gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre'.split())}


def datas(v):
    """conjunto de (ano, mes) e anos escritos num valor"""
    v = (v or '').lower()
    out = set()
    for a, m, d in re.findall(r'(20\d\d)-(\d\d)-(\d\d)', v): out.add((int(a), int(m), int(d)))
    for d, m, a in re.findall(r'(\d{1,2})[/.](\d{1,2})[/.](20\d\d)', v): out.add((int(a), int(m), int(d)))
    for d, mn, a in re.findall(r'(\d{1,2})\s+(' + '|'.join(MES) + r')\s+(20\d\d)', v): out.add((int(a), MES[mn], int(d)))
    return out


def anos(v): return set(int(a) for a in re.findall(r'(?<!\d)(20\d\d)(?!\d)', v or ''))


linhas, cont = [], dict(ALVOS=0, CONTROLES=0, ARMADILHAS=0, DATAS_FALSAS=0, REGRESSOES=0, DIFERENCAS_R1_R2=0)
for it in L['ITENS']:
    a, b = R1[it['ID']], R2[it['ID']]
    texto = by[it['CHAVE']]['texto']
    tsha = hashlib.sha256(texto.encode('utf-8')).hexdigest()
    ident = (a['FACT_TIME'], a.get('TRECHO_LITERAL'), a.get('POSICAO')) == (b['FACT_TIME'], b.get('TRECHO_LITERAL'), b.get('POSICAO'))
    if not ident: cont['DIFERENCAS_R1_R2'] += 1
    ok_prova = all(x['FACT_TIME'] == 'NAO SEI' or (x['TEXTO_SHA256'] == tsha and texto[x['POSICAO'][0]:x['POSICAO'][1]] == x['TRECHO_LITERAL']) for x in (a, b))
    # data falsa: armadilha devolveu data, ou o trecho cobre a posicao de uma data falsa conhecida
    def falsa(x):
        if x['FACT_TIME'] == 'NAO SEI': return False
        if it['CLASSE'] == 'ARMADILHA_DATA_FALSA': return True
        p0, p1 = x['POSICAO']
        # sobreposicao com a janela (POS..POS+len) de uma data falsa conhecida, ou o valor ser essa data
        return any((p0 < f['POS'] + len(f['TRECHO']) and f['POS'] < p1 and f['DATA'].lower() in texto[p0:p1].lower())
                   or f['DATA'].lower() == x['FACT_TIME'].strip().lower() for f in it['DATAS_FALSAS_CONHECIDAS'])
    fal = falsa(a) or falsa(b)
    est = ''
    if it['CLASSE'] == 'ALVO_PERDA_FACT_TIME':
        rec = ident and ok_prova and not fal and a['FACT_TIME'] != 'NAO SEI'
        cont['ALVOS'] += rec; est = 'RECUPERADO' if rec else 'NAO_RECUPERADO'
    elif it['CLASSE'] == 'CONTROLE_JA_CORRETO':
        cur = it['FACT_TIME_ATUAL']
        dc, dn = datas(cur), datas(a['FACT_TIME'] + ' ' + str(a.get('INICIO')) + ' ' + str(a.get('FIM')))
        mesmo = a['FACT_TIME'] != 'NAO SEI' and ((dc and dc == datas(a['FACT_TIME'])) or (not dc and anos(cur) == anos(a['FACT_TIME'])))  # regra do lote: diferente = REGRESSAO
        reg = not mesmo
        cont['CONTROLES'] += (not reg) and ident; cont['REGRESSOES'] += reg; est = 'REGRESSAO' if reg else 'MANTIDO'
    else:
        ok = a['FACT_TIME'] == 'NAO SEI' and b['FACT_TIME'] == 'NAO SEI'
        cont['ARMADILHAS'] += ok; est = 'NAO_SEI_OK' if ok else 'DATA_DEVOLVIDA'
    cont['DATAS_FALSAS'] += fal
    linhas.append(dict(ID=it['ID'], CLASSE=it['CLASSE'], SOURCE_ID=it['SOURCE_ID'], FACT_TIME_ANTES=it['FACT_TIME_ATUAL'],
                       VALOR=a['FACT_TIME'], TRECHO_LITERAL=a.get('TRECHO_LITERAL'), POSICAO=a.get('POSICAO'),
                       TEXTO_SHA256=a['TEXTO_SHA256'], MOTIVO_R1=a['MOTIVO'], MOTIVO_R2=b['MOTIVO'], VALOR_R2=b['FACT_TIME'],
                       RODADAS_IDENTICAS=ident, PROVA_CONFERE=ok_prova, DATA_FALSA=fal, ESTADO=est,
                       PORQUE_LLM=(a.get('LLM') or {}).get('PORQUE')))
custo = [x['CUSTO'] for r in (R1, R2) for x in r.values()]
res = dict(SCHEMA='SEMANTIC-READER-SOMBRA-PLACAR-L30/v1', MARCA='EXPERIMENTAL / NAO_PARA_CLIENTE',
           LOTE_SHA256=hashlib.sha256(open(lote, 'rb').read()).hexdigest(), MODELO=J1['MODELO'], PROMPT_SHA256=J1['PROMPT_SHA256'],
           ALVOS=f"{cont['ALVOS']}/20", CONTROLES=f"{cont['CONTROLES']}/6", ARMADILHAS=f"{cont['ARMADILHAS']}/4",
           DATAS_FALSAS=cont['DATAS_FALSAS'], REGRESSOES=cont['REGRESSOES'],
           RODADAS_IDENTICAS='SIM' if cont['DIFERENCAS_R1_R2'] == 0 else f"NAO ({cont['DIFERENCAS_R1_R2']} itens diferem)",
           CUSTO_ITEM=dict(USD_MEDIO=round(sum(c['CUSTO_USD'] or 0 for c in custo) / len(custo), 3),
                           TOKENS_ENTRADA_MEDIO=round(sum(c['TOKENS_ENTRADA'] for c in custo) / len(custo)),
                           TOKENS_SAIDA_MEDIO=round(sum(c['TOKENS_SAIDA'] for c in custo) / len(custo)),
                           SEGUNDOS_MEDIO=round(sum(c['SEGUNDOS'] for c in custo) / len(custo), 1)),
           TEMPO_TOTAL_S=dict(RODADA_1=J1['TEMPO_TOTAL_S'], RODADA_2=J2['TEMPO_TOTAL_S']),
           CUSTO_TOTAL_USD=round(sum(c['CUSTO_USD'] or 0 for c in custo), 2), LINHAS=linhas)
json.dump(res, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'LINHAS'}, ensure_ascii=False, indent=1))
for l in linhas:
    print(l['ID'], l['ESTADO'], '|', l['FACT_TIME_ANTES'][:24], '->', l['VALOR'][:50], '| R2:', l['VALOR_R2'][:40], '|', l['MOTIVO_R1'], l['RODADAS_IDENTICAS'], l['DATA_FALSA'], '|', repr(l['TRECHO_LITERAL'])[:120])
