"""IA-CUR: o livro das propostas do agente (append) na copia. Nao escreve em nenhum livro de
estado; cada linha diz por que PORTA a proposta volta e em que estado ficou.
uso: py registar_propostas.py <raiz da copia>"""
import hashlib, json, os, sys
from datetime import datetime, timezone
RAIZ = sys.argv[1]
POR = "OPUS (claude-opus-5-5) via agente Orca IA-CUR"
agora = datetime.now(timezone.utc).isoformat()
S = os.path.expanduser("~/sintonia-sala-italia")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


P = []
def add(caso, tipo, janela, proposta, porta, estado, provas=None, trecho=""):
    P.append({"CASO": caso, "TIPO": tipo, "JANELA_D29": janela, "PROPOSTA": proposta, "PORTA": porta,
              "ESTADO": estado, "PROVAS": provas or [], "TRECHO": trecho[:400],
              "PROPOSTO_POR": POR, "PROPOSTO_EM": agora})

# 1 · territorio (14) — ja escritos pela porta semantica
for c, t in [("CAND-0503", "T11/IT"), ("CAND-0515", "T9/EU"), ("CAND-0527", "T10/INT"), ("CAND-0575", "T10/IT"),
             ("CAND-0577", "T10/IT"), ("CAND-0579", "T10/IT"), ("CAND-0580", "T10/IT"), ("CAND-0582", "T11/INT")]:
    add(c, "TERRITORIO", False, "territorio %s" % t, "decisao_semantica -> QUALIFY",
        "ESCRITA_NA_PORTA", [{"VER": "DECISOES-SEMANTICAS-V1.json (3 provas, sha256 conferido)"}])
for c, cat in [("CAND-0057", "NAO_E_FONTE"), ("CAND-0257", "IDENTIDADE_TROCADA"), ("CAND-0554", "NAO_E_FONTE"),
               ("CAND-0583", "NAO_E_FONTE"), ("CAND-0581", "NAO_E_FONTE")]:
    add(c, "RELEVANCIA", False, "recusar como fonte: %s" % cat, "decisao_semantica (NAO SEI com categoria) -> "
        "porta das candidatas (RECUSADA e decisao do dono)", "PROPOSTA_REGISTADA")
add("CAND-0556", "TERRITORIO", False, "NAO SEI: falta pagina INSTITUCIONAL", "decisao_semantica", "PRECISA_DE_REDE")

# 2 · janela de cultura (16)
t305 = S + "/acervo-coletor-bcr/data/collection-store/italy/IT-T3-005/TERRETRURIA_07-09-2026_13-09-2026/v1_bced66652f25/monitoraggio.html"
add("IT-T3-005", "ATLAS", True, "ficha no Atlas: Terre dell'Etruria (cooperativa olivicola, Toscana) — Servizio "
    "Agronomico, boletim semanal de monitorizacao da mosca-da-azeitona; T3, IT", "Atlas (decisao humana, D-ficha)",
    "PROPOSTA_REGISTADA", [{"PAPEL": "CONTEUDO", "URL": "https://terretruria.it/monitoraggio", "SHA256": sha(t305),
                            "BYTES_EM": t305.replace(os.path.expanduser("~"), "~")}],
    "Monitoraggio della mosca dell'olivo a cura del Servizio Agronomico. Bollettino del periodo dal 07-09-2026 al 13-09-2026")
CAPA = {  # o que a coleta colheu por engano (a causa do CANARY_PENDING): o padrao apanha paginas institucionais
    "IT-T3-013": "Piani Programmi Progetti", "IT-T3-014": "Account area riservata", "IT-T3-015": "PEC — Regione Toscana",
    "IT-T3-016": "PR Veneto FESR 2021-2027", "IT-T3-018": "ISPA — sede di Bari", "IT-T3-019": "Progetti in corso",
    "IT-T1-006": "Arsac chi siamo"}
for s, capa in CAPA.items():
    add(s, "LINK_PATTERN", True, "o LINK_PATTERN apanha a pagina institucional «%s» em vez do boletim; propor "
        "INDEX_URL da seccao de boletins e padrao do item depois de LER a listagem viva" % capa,
        "porta de contratos D10 (reparar_contrato.aplicar) -> VALIDATE_ROUTE -> CANARY -> regua",
        "PRECISA_DE_REDE")
for s, porque in [("IT-T3-022", "CCF: 0 enderecos da entrada casam"), ("IT-T2-109", "CCF: 0 enderecos"),
                  ("IT-T3-023", "CCF: 131 enderecos, nenhum casa"), ("IT-T3-024", "CCF: 3 enderecos, nenhum casa"),
                  ("IT-T3-017", "DEGRADED: EMPTY_LIST na BCR"), ("IT-T3-021", "DEGRADED: EMPTY_LIST na BCR"),
                  ("IT-T2-015", "UNKNOWN: a coleta colheu a brochura PDF (papelada)"),
                  ("IT-T3-020", "UNKNOWN: a coleta colheu PDF de papelada")]:
    add(s, "LINK_PATTERN", True, porque + " — reparo pelo dono (R1) primeiro; a IA so entra no que a R1 recusar, "
        "com a pagina viva lida", "porta de contratos D10 -> VALIDATE_ROUTE -> CANARY -> regua", "PRECISA_DE_REDE")

assert len(P) == 30, len(P)
p = RAIZ + "/curadoria/PROPOSTAS-IA-CUR-V1.json"
doc = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {
    "DATASET": "PROPOSTAS-IA-CUR-V1", "LEI": "o agente PROPOE com prova; a porta decide; nunca escreve estado nem promove",
    "PROPOSTAS": []}
doc["PROPOSTAS"] += P
open(p, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
import collections
print(len(P), collections.Counter(x["ESTADO"] for x in P), collections.Counter(x["JANELA_D29"] for x in P))
