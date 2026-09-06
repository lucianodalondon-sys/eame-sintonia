p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_Allegato1_Elenco_Stazioni.pdf.decoded.txt'
t=open(p,encoding='utf-8').read()
pages=t.split('===PAGE===')
for i,pg in enumerate(pages,1):
    print('########## PAGE',i,'chars',len(pg))
for i in (6,7,8):
    print('\n########## FULL PAGE',i,'##########')
    print(' '.join(pages[i-1].split()))
