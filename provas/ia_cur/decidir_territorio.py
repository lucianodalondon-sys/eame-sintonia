"""IA-CUR: as decisoes de territorio do agente (Opus 5.5 via Orca), escritas pela PORTA
`curadoria/decisao_semantica.py` (DECISOES-SEMANTICAS-V1.json) numa COPIA do livro vivo.

As provas sao as paginas que a S2 ja leu (egresso IT, sha256 no provas.jsonl); o sha256 e
conferido de novo contra os bytes guardados antes de entrar. Nenhuma decisao anterior e
apagada: a de NAO SEI da S2 passa a ANTERIOR dentro da mesma linha (a porta recusa duas
linhas para a mesma candidata).
uso: py decidir_territorio.py <raiz da copia> <provas.jsonl>"""
import hashlib, json, os, sys
from datetime import datetime, timezone

RAIZ, PROVAS = sys.argv[1], sys.argv[2]
POR = "OPUS (claude-opus-5-5) via agente Orca IA-CUR"

# (candidata, territorio, pais, porque, pais_prova) — o juizo e do agente, lido nas paginas
DECIDE = [
    ("CAND-0503", "T11", "IT", "CeMi — Commodities Exchange Milano, o evento anual das agrocommodities da Associazione "
     "Granaria di Milano (desde 1902); as paginas sao a edicao 2025 (programa de analise de mercado de cereais) e a "
     "informacao da edicao 2026. E um EVENTO do setor.", "Palazzo del Ghiaccio, Milano; Associazione Granaria di Milano"),
    ("CAND-0515", "T9", "EU", "CropLife Europe representa as empresas que desenvolvem e vendem pesticidas e "
     "biopesticidas na Europa (a INSTITUCIONAL diz quem sao os membros); publica a revisao anual e a conferencia 2026 "
     "em Bruxelas. E a camada associativa dos CONCORRENTES.", "Bruxelas; representa o mercado europeu"),
    ("CAND-0527", "T10", "INT", "IFA — International Fertilizer Association, a unica associacao global de fertilizantes "
     "(~500 membros em ~80 paises); publica programas da industria (emissoes, Innovation Hub). MERCADO / INDUSTRIA de "
     "insumos.", "associacao global, sede em Paris, eventos em Barcelona"),
    ("CAND-0575", "T10", "IT", "Agridigital — associacao dos sistemas e tecnologias digitais para maquinas agricolas, "
     "aderente a FederUnacoma; publica noticias da associacao e das empresas costruttrici. INDUSTRIA de maquinas.",
     "FederUnacoma (Italia); assembleia em Zola Predosa-BO"),
    ("CAND-0577", "T10", "IT", "Assomao — Italian Implements Manufacturers Association (FederUnacoma); publica noticias "
     "e comunicados das empresas de alfaias. INDUSTRIA de maquinas.", "associacao italiana (FederUnacoma), Modena/Bologna"),
    ("CAND-0579", "T10", "IT", "Assotrattori — associacao dos construtores italianos de tratores (FederUnacoma); publica "
     "noticias (Agrilevante 2025) e comunicados das empresas. INDUSTRIA de maquinas.", "associacao italiana (FederUnacoma)"),
    ("CAND-0580", "T10", "IT", "Comacomp — associacao dos construtores italianos de componentes para maquinas agricolas "
     "(FederUnacoma); publica noticias (Agrilevante 2025) e comunicados. INDUSTRIA de maquinas.",
     "associacao italiana (FederUnacoma)"),
    ("CAND-0582", "T11", "INT", "Club of Bologna — task-force mundial sobre mecanizacao agricola (FederUnacoma + "
     "Accademia dei Georgofili); publica o premio Pellizzi e o encontro anual durante a EIMA. EVENTOS / encontros.",
     "task-force mundial (membros de varios paises), sede em Bologna"),
]
# (candidata, categoria, porque) — NAO SEI com o motivo do agente
NAO_SEI = [
    ("CAND-0057", "NAO_E_FONTE", "jornalismo de consumo alimentar (etiquetas, Coop, aditivos); fora do universo agro "
     "de protecao de culturas — relevancia duvidosa, nao ha territorio T1..T12 honesto"),
    ("CAND-0257", "IDENTIDADE_TROCADA", "sherwood.it e a Radio Sherwood (webzine cultural de Padova), nao a revista "
     "florestal «Sherwood — Foreste ed Alberi Oggi»; a candidata aponta para a organizacao errada"),
    ("CAND-0554", "NAO_E_FONTE", "loja online de produtos de cooperativas; os itens sao receitas e dicas de consumo"),
    ("CAND-0556", "PROVA_INSUFICIENTE", "ha 2 paginas de conteudo (Confcooperative: FonCoop, Caviro) e nenhuma "
     "INSTITUCIONAL guardada — a porta exige prova do que a organizacao E; precisa de rede"),
    ("CAND-0583", "NAO_E_FONTE", "projeto de energia renovavel de biomassa (2010, FederUnacoma/Ministerio); bioenergia, "
     "fora do universo; as provas de conteudo sao PDFs"),
    ("CAND-0581", "NAO_E_FONTE", "Comagarden — maquinas de jardinagem e espacos verdes, nao agricultura"),
]

pv = {}
for l in open(PROVAS, encoding="utf-8"):
    r = json.loads(l)
    pv.setdefault(r["CAND"], []).append(r)
cand = {c["CANDIDATA_ID"]: c for c in json.load(open(RAIZ + "/candidatas/FONTES-CANDIDATAS.json",
                                                     encoding="utf-8"))["CANDIDATAS"]}
p = RAIZ + "/curadoria/DECISOES-SEMANTICAS-V1.json"
doc = json.load(open(p, encoding="utf-8"))
L = doc["DECISOES"]
agora = datetime.now(timezone.utc).isoformat()
res = []


def rever(cid, novo):
    ix = [i for i, d in enumerate(L) if d.get("CANDIDATA_ID") == cid]
    assert len(ix) <= 1, (cid, "mais de uma decisao ja na copia")
    if ix:
        ant = {k: L[ix[0]].get(k) for k in ("TERRITORIO", "CATEGORIA", "MOTIVO", "DECIDIDO_POR", "DECIDIDO_EM")}
        novo["ANTERIOR"] = ant
        L[ix[0]] = novo
    else:
        L.append(novo)


for cid, ter, pais, porque, pais_prova in DECIDE:
    provas = []
    for r in pv[cid]:
        if r.get("ESTADO") != "OK":
            continue
        b = open(r["CAMINHO"], "rb").read()
        assert hashlib.sha256(b).hexdigest() == r["SHA256"], (cid, r["URL"], "sha256 nao confere")
        assert r["EGRESSO"] == "IT", (cid, r["URL"], r["EGRESSO"])
        provas.append({"PAPEL": r["PAPEL"], "URL": r["URL"], "SHA256": r["SHA256"], "BYTES": r["BYTES"],
                       "LIDO_EM": r["AT"], "EGRESSO": r["EGRESSO"],
                       "BYTES_EM": "%TEMP%\\s2\\provas\\" + cid + "\\" + os.path.basename(r["CAMINHO"])})
    rever(cid, {"CANDIDATA_ID": cid, "NOME": cand[cid]["NOME"], "URL": cand[cid]["URL"], "TERRITORIO": ter,
                "DECIDIDO_POR": POR, "DECIDIDO_EM": agora, "PORQUE": porque, "PROVAS": provas,
                "SEGUNDA_LEITURA": None, "PAIS": pais, "PAIS_PROVA": pais_prova,
                # D31 (24/09, bot Luciano por delegacao do dono): EU/INT entram como candidatas
                **({"NUMERACAO_FORA_DE_IT": "D31"} if pais in ("EU", "INT") else {})})
    res.append((cid, ter, pais, len(provas)))

for cid, cat, porque in NAO_SEI:
    rever(cid, {"CANDIDATA_ID": cid, "NOME": cand[cid]["NOME"], "URL": cand[cid]["URL"], "TERRITORIO": "NAO SEI",
                "MOTIVO": porque, "DECIDIDO_POR": POR, "DECIDIDO_EM": agora, "CATEGORIA": cat})
    res.append((cid, "NAO SEI", cat, 0))

doc["DECIDIDAS"] = sum(1 for d in L if d.get("TERRITORIO") not in (None, "NAO SEI"))
doc["NAO_SEI"] = sum(1 for d in L if d.get("TERRITORIO") == "NAO SEI")
tmp = p + ".tmp"
open(tmp, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
os.replace(tmp, p)
for r in res:
    print(*r)
