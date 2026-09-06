import json,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
d=json.load(open('F3b-search-masterplan-folder.json',encoding='utf-8'))
print('MASTERPLAN FOLDER items_total:',d.get('items_total'))
for it in d['items']:
    print('  ',it.get('@type'),'|',it.get('title'),'|',it.get('@id'))
print()
s=json.load(open('F3b-search-attivazione.json',encoding='utf-8'))
print('attivazione search total:',s.get('items_total'))
for it in s['items'][:12]:
    print('  ',it.get('@type'),'|',(it.get('title') or '')[:70],'|',it.get('@id'))
