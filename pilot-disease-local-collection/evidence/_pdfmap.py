import re, sys
path=sys.argv[1]
data=open(path,'rb').read()
for m in re.finditer(rb'/R(\d+)\s+(\d+)\s+0\s+R', data):
    print('resource /R%s -> obj %s' % (m.group(1).decode(), m.group(2).decode()))
print('---- font objects ----')
for m in re.finditer(rb'(\d+)\s+0\s+obj\s*<<([^>]{0,500}?/Type\s*/Font.{0,500}?)>>', data, re.S):
    print('obj', m.group(1).decode(), ':', m.group(2).decode('latin-1').replace('\n',' ')[:400])
