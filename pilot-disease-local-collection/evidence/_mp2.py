import re,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_rete_monitoraggio_v2.0.pdf.decoded.txt'
t=' '.join(open(p,encoding='utf-8').read().split())
i=t.find('Tabella 3: Consistenza della rete')
print(t[i:i+2600])
print()
print('######## other mentions of TOTALE / consistenza ########')
for m in re.finditer(r'(?i)consistenza della rete',t):
    print('  @',m.start())
