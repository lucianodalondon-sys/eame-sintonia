import json
d=json.load(open('F3b-od-meteoclima.json',encoding='utf-8'))
print('TITLE:',d.get('title'),'| type:',d.get('@type'))
for it in d.get('items',[]) or []:
    print('  ITEM:',it.get('@type'),'|',it.get('title'),'|',it.get('@id'))
print('items_total',d.get('items_total'))
s=json.load(open('F3b-od-clima-folder.json',encoding='utf-8'))
print('SEARCH under /open-data/clima total:',s.get('items_total'))
for it in s.get('items',[]):
    print('   ',it.get('@type'),'|',it.get('title'),'|',it.get('@id'))
