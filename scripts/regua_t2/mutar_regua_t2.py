# T2-REGUA · ataque de mutacao a regua T2, numa COPIA (worktree destacada). Uso: py scripts/regua_t2/mutar_regua_t2.py (R = caminho da copia)
import subprocess,os,sys,json
R=r'C:\regua-t2-base'; F=os.path.join(R,'admissao','admissao.py')
orig=open(F,encoding='utf-8').read()
M=[("transversal_off","if outro == universo or outro in TRANSVERSAIS:","if outro == universo:"),
("e_vira_ou","if (achadas and fortes) or (agro and len(achadas) >= SINAIS_MINIMOS):","if (achadas or fortes) or (agro and len(achadas) >= SINAIS_MINIMOS):"),
("agrometeo_1_condicao","(agro and len(achadas) >= SINAIS_MINIMOS)","(agro and len(achadas) >= 1)"),
("palavra_inteira_off",'PALAVRA_INTEIRA = frozenset({"T2"})','PALAVRA_INTEIRA = frozenset()'),
("casa_substring",'if f and re.search(r"(?<![a-z0-9])" + re.escape(f) + r"(?![a-z0-9])", texto_dobrado):','if f and f in texto_dobrado:'),
("metade_vira_nao","            return NAO_SEI, (\n                f\"{falta}:","            return NAO, (\n                f\"{falta}:"),
("sem_d2",'"d2": "REROUTE_POSSIVEL" if not ancoras else None}','"d2": None}'),
("ancora_en_off",'anc = (ANCORAS_EN if lingua == "en" else ANCORAS)[universo]','anc = ANCORAS[universo]'),
("regua_t2_apagada",'    "T2": ["pioggia|piogge|precipitazione|precipitazioni"','    "T2_X": ["pioggia|piogge|precipitazione|precipitazioni"'),
]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',HTTP_PROXY='http://127.0.0.1:9',HTTPS_PROXY='http://127.0.0.1:9')
res={}
for nome,a,b in M:
    assert orig.count(a)==1,(nome,orig.count(a))
    open(F,'w',encoding='utf-8',newline='').write(orig.replace(a,b))
    p=subprocess.run([sys.executable,'-m','unittest','tests.test_regua_t2','tests.test_a_regra_de_t2'],cwd=R,env=env,capture_output=True,text=True,timeout=600)
    last=[l for l in p.stderr.splitlines() if l.startswith(('OK','FAILED'))]
    res[nome]=('MORTO' if p.returncode else 'SOBREVIVEU', last[-1] if last else p.stderr[-200:])
    print(nome,res[nome],flush=True)
open(F,'w',encoding='utf-8',newline='').write(orig)
json.dump(res,open(os.path.join(os.environ['TEMP'],'t2','mutacao.json'),'w'),indent=1)
