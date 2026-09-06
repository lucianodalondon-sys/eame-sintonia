import re,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_rete_monitoraggio_v2.0.pdf.decoded.txt'
t=' '.join(open(p,encoding='utf-8').read().split())
print('CHARS:',len(t))
for kw in ['bagnatura','Bagnatura','AGRO','agrometeorolog','1985','1990','1992','1994','anagrafic','stazioni agro']:
    n=len(re.findall(re.escape(kw),t))
    print('--- "%s" occurrences: %d'%(kw,n))
for m in re.finditer(r'(?i)bagnatur',t):
    s=max(0,m.start()-350); e=min(len(t),m.end()+350)
    print('  CTX:',t[s:e])
    print()
