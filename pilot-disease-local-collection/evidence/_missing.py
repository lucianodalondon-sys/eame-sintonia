import re,sys,json
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_Allegato1_Elenco_Stazioni.pdf.decoded.txt'
t=open(p,encoding='utf-8').read()
HDR=re.compile(r'ARPAV MasterPlan rete di monitoraggio idro-nivo-agro-mete o ALLEGATO 1 . ELENCO DELLE STAZIONI \d+ dicembre 2024 codice SIRAV tipo nome stazione quota m s\.l\.m\. provincia')
flat=' '.join(HDR.sub('',' '.join(pg.split())) for pg in t.split('===PAGE==='))
# raw count of the token NIVO not followed by MET/IDRO
raw_nivo=[m.start() for m in re.finditer(r'\bNIVO(?!MET|IDROMET)\b',flat)]
print('raw NIVO tokens in text:',len(raw_nivo))
parsed=json.load(open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-elenco-stazioni-parsed.json',encoding='utf-8'))
pn=[r for r in parsed if r['tipo']=='NIVO']
print('parsed NIVO rows:',len(pn))
# show each raw NIVO context to find the unparsed one
got=set((r['codice_sirav'],r['nome']) for r in pn)
for s in raw_nivo:
    seg=flat[max(0,s-12):s+70]
    print('  ',seg)
