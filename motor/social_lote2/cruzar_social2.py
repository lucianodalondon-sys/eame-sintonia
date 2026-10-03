import json,os,re,sys,subprocess,shutil,time,hashlib
D=os.path.dirname(os.path.abspath(__file__)); S=D+"/saida"; OUT=S+"/cruzamento"; os.makedirs(OUT,exist_ok=True)
CL=shutil.which("claude.cmd") or shutil.which("claude")
F={f["ID"]:f for f in json.load(open(S+"/FICHAS.json",encoding="utf-8")) if f.get("CONFERENCIA")=="OK"}
C=json.load(open(S+"/CONJUNTO.json",encoding="utf-8")); X=json.load(open(S+"/CONTEXTO_ADAMA.json",encoding="utf-8"))
G={g["GRUPO_ID"]:g for g in C["GRUPOS"]}
top=[]
for gid in C["TOP10_AGRICOLA_COMERCIAL"]:
    g=dict(G[gid]); g["FICHAS"]=[{k:F[i].get(k) for k in ("ID","_AUTOR","_PAIS_DO_CANAL","_PUBLICADO_EM","_TIPO_TEXTO","CULTURA","PRAGA_DOENCA_ALVO","PRODUTO_OU_SUBSTANCIA","EMPRESA","LOCAL","DATA_FATO","RESUMO","TRECHO")} for i in g["IDS"] if i in F]
    top.append(g)
dados={"AGRUPAMENTOS":top,"CONTEXTO_ADAMA":X}
bp=OUT+"/SAIDA_BRUTA.json"
if not os.path.exists(bp):
    msg=open(D+"/cruzamento.prompt.md",encoding="utf-8").read()+"\n<<<DADOS>>>\n"+json.dumps(dados,ensure_ascii=False)+"\n<<<FIM_DADOS>>>\n"
    open(OUT+"/PROMPT.txt","w",encoding="utf-8").write(msg); t0=time.time()
    r=subprocess.run([CL,"-p","--model","claude-opus-5","--tools","","--strict-mcp-config","--no-session-persistence","--output-format","json"],input=msg,capture_output=True,text=True,encoding="utf-8",timeout=1700)
    env=json.loads(r.stdout); env["_S"]=round(time.time()-t0,1); json.dump(env,open(bp,"w",encoding="utf-8"),ensure_ascii=False)
env=json.load(open(bp,encoding="utf-8")); txt=env["result"]; m=re.search(r"\{.*\}",txt,re.S); R=json.loads(m.group(0))
uses={l.split("|")[0] for l in X["USOS"]}; fen={l.split("|")[0] for l in X["FENOLOGIA"]}
for o in R["CRUZAMENTOS"]:
    o["CLASSE_DO_MODELO"]=o["CLASSE"]; erros=[]
    for k in ("PORTFOLIO_ADAMA","LABEL"):
        bad=[u for u in o[k].get("USE_IDS",[]) if u not in uses]
        if bad: erros.append("USE_ID_INEXISTENTE:%s:%s"%(k,bad))
    badf=[x for x in o["JANELA"].get("FENOLOGIA_IDS",[]) if x not in fen]
    if badf: erros.append("FENOLOGIA_ID_INEXISTENTE:%s"%badf)
    badi=[i for i in o.get("ITEM_IDS",[]) if i not in F]
    if badi: erros.append("ITEM_ID_INEXISTENTE:%s"%badi)
    if o["CLASSE"]=="OPORTUNIDADE":
        nao=[k for k in ("CULTURA","ALVO","REGIAO_DO_FATO","POR_QUE_AGORA") if "NAO_SEI" in str(o[k]).upper()]
        if nao or not o["LABEL"].get("USE_IDS") or not o["JANELA"].get("FENOLOGIA_IDS"): o["CLASSE"]="LEAD"; erros.append("OPORTUNIDADE_COM_NAO_SEI_REBAIXADA:%s"%nao)
    if o["FERRAMENTA_CASCO"]=="OPPORTUNITY_RADAR" and o["CLASSE"]!="OPORTUNIDADE": o["FERRAMENTA_CASCO_DO_MODELO"]="OPPORTUNITY_RADAR"; o["FERRAMENTA_CASCO"]="COMPETITION" if "CONCORR" in json.dumps(G[o["GRUPO_ID"]]["CATEGORIA"]) else "FUTURE_RADAR"; erros.append("RADAR_OPORTUNIDADE_SEM_OPORTUNIDADE")
    o["CONFERENCIA_DO_PROGRAMA"]=erros or ["OK"]
    o["EVIDENCIAS"]=[{"ID":i,"URL":F[i]["_URL"],"AUTOR":F[i]["_AUTOR"],"PLATAFORMA":F[i]["_PLATAFORMA"],"PUBLICADO_EM":F[i]["_PUBLICADO_EM"],"TRECHO":F[i]["TRECHO"]} for i in o.get("ITEM_IDS",[]) if i in F]
R["MARCA"]="TESTE / NAO_PARA_CLIENTE"; R["CARIMBO_REFERENCIA"]=X["CARIMBO"]; R["MODELO"]=list((env.get("modelUsage") or {}).keys()); R["CUSTO_USD_REPORTADO"]=env.get("total_cost_usd"); R["SEGUNDOS"]=env.get("_S")
import collections; R["CONTAGEM"]=dict(collections.Counter(o["CLASSE"] for o in R["CRUZAMENTOS"]))
json.dump(R,open(OUT+"/CRUZAMENTO-SOCIAL-ADAMA.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(json.dumps({"CONTAGEM":R["CONTAGEM"],"CUSTO":R["CUSTO_USD_REPORTADO"],"S":R["SEGUNDOS"],"MODELO":R["MODELO"]}))
