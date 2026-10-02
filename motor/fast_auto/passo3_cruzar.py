# SINTONIA_FAST_V1 - passo 3: FACTS_FAST -> LLM cruzamento -> SIGNALS_FAST + OPPORTUNITIES_FAST
# O programa confere: todo FACT_ID citado existe e foi ACEITO; oportunidade precisa cruzar fatos de >=2 documentos.
import datetime, json, os, re, shutil, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.environ.get("FAST_MODELO", "claude-opus-5")
F = json.load(open(AQUI + "/FACTS_FAST.json", encoding="utf-8"))
CAMPOS = ["O_QUE", "ONDE", "QUANDO", "CULTURA", "PRAGA_DOENCA", "PRODUTO_OU_EMPRESA", "NUMERO"]
aceitos = {f["FACT_ID"]: f for f in F["FATOS"] if f["ESTADO"] != "REJEITADO"}


def compacto(f):
    c = {"FACT_ID": f["FACT_ID"], "TIPO": f["TIPO"], "FONTE": f["SOURCE_ID"]}
    for k in CAMPOS:
        if f[k]["VERIFICACAO"] == "TRECHO_ENCONTRADO_NO_RAW":
            c[k] = f[k]["VALOR"]
    return c


PROMPT = """Voce e o analista do SINTONIA para a ADAMA Italia (defensivos agricolas: fungicidas, inseticidas, herbicidas).
Recebe FATOS ja verificados (cada um com FACT_ID). Campo ausente = NAO SEI. Use SO estes fatos; nao traga conhecimento externo como fato.

Produza:
1) SINAIS: algo que mudou ou esta acontecendo e merece atencao. Cada sinal cita os FACT_IDS que o sustentam (1 ou mais).
2) OPORTUNIDADES: so quando o CRUZAMENTO de fatos de DOCUMENTOS DIFERENTES sugere uma acao comercial/tecnica para a ADAMA
   (ex.: praga ativa + cultura + regiao + janela). Cada oportunidade cita FACT_IDS de pelo menos 2 documentos diferentes
   (o documento e o trecho do FACT_ID entre 'F-' e o ultimo '-'), e os SIGNAL_IDS de onde nasce.
   Se o cruzamento nao fecha (local diferente, cultura diferente, tempo desconhecido), NAO crie a oportunidade.
   Zero oportunidades e resposta valida.
Para cada sinal e oportunidade escreva em portugues simples:
  O_QUE_ACONTECEU, POR_QUE_IMPORTA, ONDE (ou "NAO SEI"), QUANDO (ou "NAO SEI"), O_QUE_NAO_SABEMOS (lista),
  CONFIANCA (BAIXA/MEDIA/ALTA - julgamento, nao probabilidade).
Oportunidade tem ainda: ACAO_SUGERIDA, POR_QUE_CRUZAMENTO (como os fatos se ligam: mesma cultura? mesma regiao? mesma janela?).
Responda SO JSON:
{"SINAIS":[{"SIGNAL_ID":"S-01","TITULO":"...","FACT_IDS":[...],"O_QUE_ACONTECEU":"...","POR_QUE_IMPORTA":"...","ONDE":"...","QUANDO":"...","O_QUE_NAO_SABEMOS":[...],"CONFIANCA":"..."}],
 "OPORTUNIDADES":[{"OPPORTUNITY_ID":"O-01","TITULO":"...","FACT_IDS":[...],"SIGNAL_IDS":[...],"O_QUE_ACONTECEU":"...","POR_QUE_IMPORTA":"...","ACAO_SUGERIDA":"...","POR_QUE_CRUZAMENTO":"...","ONDE":"...","QUANDO":"...","O_QUE_NAO_SABEMOS":[...],"CONFIANCA":"..."}]}

FATOS:
%s"""

entrada = json.dumps([compacto(f) for f in aceitos.values()], ensure_ascii=False)
r = subprocess.run([shutil.which("claude"), "-p", "--model", MODELO, "--output-format", "json"], input=PROMPT % entrada,
                   capture_output=True, text=True, encoding="utf-8", timeout=1200)
env = json.loads(r.stdout)
res = json.loads(re.search(r"\{.*\}", env["result"], re.S).group(0))
RUN = "FAST-RUN-X-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def provas(ids):
    out = []
    for i in ids:
        f = aceitos[i]
        out.append({"FACT_ID": i, "DOCUMENT_ID": f["DOCUMENT_ID"], "RAW_ASSET_ID": f["RAW_ASSET_ID"], "SOURCE_ID": f["SOURCE_ID"],
                    "URL": f["URL"], "RAW_SHA256": f["RAW_SHA256"], "O_QUE": f["O_QUE"]["VALOR"], "TRECHO": f["O_QUE"]["TRECHO"]})
    return out


sinais, opps = [], []
for s in res.get("SINAIS", []):
    ids = s.get("FACT_IDS", [])
    falt = [i for i in ids if i not in aceitos]
    s["VALIDACAO"] = "REJEITADO_FACT_ID_INEXISTENTE:" + ",".join(falt) if falt or not ids else "OK_FATOS_EXISTEM"
    if not falt and ids:
        s["FONTES"] = sorted({aceitos[i]["SOURCE_ID"] for i in ids})
        s["DOCUMENTOS"] = sorted({aceitos[i]["DOCUMENT_ID"] for i in ids})
        s["EVIDENCIAS"] = provas(ids)
    sinais.append(s)
sinal_ok = {s["SIGNAL_ID"] for s in sinais if s["VALIDACAO"] == "OK_FATOS_EXISTEM"}
for o in res.get("OPORTUNIDADES", []):
    ids = o.get("FACT_IDS", [])
    falt = [i for i in ids if i not in aceitos]
    sfalt = [i for i in o.get("SIGNAL_IDS", []) if i not in sinal_ok]
    docs = sorted({aceitos[i]["DOCUMENT_ID"] for i in ids if i in aceitos})
    if falt or not ids: o["VALIDACAO"] = "REJEITADO_FACT_ID_INEXISTENTE:" + ",".join(falt)
    elif sfalt: o["VALIDACAO"] = "REJEITADO_SIGNAL_ID_INVALIDO:" + ",".join(sfalt)
    elif len(docs) < 2: o["VALIDACAO"] = "REJEITADO_SEM_CRUZAMENTO_UM_SO_DOCUMENTO"
    else: o["VALIDACAO"] = "OK_CRUZA_%d_DOCUMENTOS" % len(docs)
    if not falt and ids:
        o["FONTES"] = sorted({aceitos[i]["SOURCE_ID"] for i in ids}); o["DOCUMENTOS"] = docs; o["EVIDENCIAS"] = provas(ids)
    opps.append(o)

base = dict(VERSAO="SINTONIA_FAST_V1", RUN_ID=RUN, RUN_FATOS=F["RUN_ID"], MODELO_PEDIDO=MODELO,
            MODELOS_USADOS=list((env.get("modelUsage") or {}).keys()), CUSTO_USD=env.get("total_cost_usd"),
            GERADO_EM=datetime.datetime.now().astimezone().isoformat(), MARCA="EXPERIMENTAL / NAO_PARA_CLIENTE",
            ENTRADA="FACTS_FAST.json (%d fatos aceitos)" % len(aceitos))
json.dump(dict(ARTEFATO="SIGNALS_FAST", **base, SINAIS=sinais), open(AQUI + "/SIGNALS_FAST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(dict(ARTEFATO="OPPORTUNITIES_FAST", **base, OPORTUNIDADES=opps), open(AQUI + "/OPPORTUNITIES_FAST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("SINAIS", len(sinais), "ok", len(sinal_ok), "| OPORTUNIDADES", len(opps), "ok", sum(o["VALIDACAO"].startswith("OK") for o in opps), "| custo", env.get("total_cost_usd"))
for o in opps: print(o["OPPORTUNITY_ID"], o["VALIDACAO"], o.get("TITULO"))
