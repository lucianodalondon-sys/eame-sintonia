import re, json, collections
p = r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_Allegato1_Elenco_Stazioni.pdf.decoded.txt'
t = open(p, encoding='utf-8').read()
print('PAGES:', t.count('===PAGE===') + 1)
flat = ' '.join(t.split())
# strip page headers
flat = re.sub(r'ARPAV MasterPlan rete di monitoraggio idro-nivo-agro-mete o ALLEGATO 1 . ELENCO DELLE STAZIONI \d+ dicembre 2024 codice SIRAV tipo nome stazione quota m s\.l\.m\. provincia', ' ', flat)
TIPI = r'(?:NIVOIDROMET|NIVOMET|IDROMET|IDRO|METEO|AGRO|NIVO)'
pat = re.compile(r'(\d{1,4})\s+(' + TIPI + r')\s+(.+?)\s+(-?\d{1,4})\s+(BL|TV|VI|VR|PD|RO|VE|UD)(?=\s|$)')
rows = []
for m in pat.finditer(flat):
    rows.append(dict(codice_sirav=int(m.group(1)), tipo=m.group(2), nome=m.group(3).strip(),
                     quota_m=int(m.group(4)), prov=m.group(5)))
print('PARSED ROWS:', len(rows))
codes = [r['codice_sirav'] for r in rows]
print('UNIQUE CODES:', len(set(codes)))
print('BY TIPO:', dict(collections.Counter(r['tipo'] for r in rows)))
print('BY PROV:', dict(collections.Counter(r['prov'] for r in rows)))
print()
print('=== TREVISO (TV) STATIONS IN OFFICIAL LIST ===')
tv = [r for r in rows if r['prov'] == 'TV']
print('N TV =', len(tv))
for r in sorted(tv, key=lambda x: x['codice_sirav']):
    print('  SIRAV %-5s %-12s %-45s %5s m' % (r['codice_sirav'], r['tipo'], r['nome'], r['quota_m']))
print()
print('=== TV by tipo:', dict(collections.Counter(r['tipo'] for r in tv)))
json.dump(rows, open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-elenco-stazioni-parsed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('tail of flat text (last 300):', flat[-300:])
