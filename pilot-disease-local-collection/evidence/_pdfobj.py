import re
d=open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_Allegato1_Elenco_Stazioni.pdf','rb').read()
for n in [7,8,10,12]:
    for m in re.finditer((r'(?<![0-9])'+str(n)+r' 0 obj').encode(), d):
        chunk=d[m.start():m.start()+420]
        safe=''.join(ch if 32<=ord(ch)<127 else '.' for ch in chunk.decode('latin-1'))
        print('=== obj',n,'@',m.start(),'===')
        print(safe)
        break
