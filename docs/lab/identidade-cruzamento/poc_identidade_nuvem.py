#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SINTONIA LAB · MISSAO-05 · PROVA DE CONCEITO OFFLINE — VERSAO NUVEM (re-medicao de 27/09, noite).

    COPIA de docs/lab-insumos/missao05/poc_identidade.py com 4 cortes DECLARADOS, porque nesta maquina NAO
    existem a copia da Sala (SALA_ATUAL.json), os LIVROs R6/R7 nem o POTE-R6:
      (1) SALA = []  -> a identidade do documento cai para ITEM:<SALA_CHAVE> (a Campania 2x NAO colapsa aqui);
      (2) o bloco ROTACAO R6->R7 nao corre (NAO RE-MEDIDO);
      (3) INSUMOS_SHA256 e medido sobre os ficheiros de ./insumos;
      (4) saidas com sufixo -NUVEM.
    Insumos (identicos por SHA-256 aos da POC local):
      mkdir -p insumos && B=origin/claude/cruzamentos-max-sguy1x   # @399e79f8
      git show $B:docs/intelligence/r7/ANALISE-R7.json                  > insumos/max-ANALISE-R7.json
      git show $B:docs/intelligence/r7/CRUZAMENTOS-MAX.json             > insumos/max-CRUZAMENTOS-MAX.json
      git show $B:docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json > insumos/max-CRUZAMENTOS-MAX-ITENS-DO-POTE.json

ORIGINAL: SINTONIA LAB · MISSAO-05 · PROVA DE CONCEITO OFFLINE — identidade do cruzamento pela PERGUNTA.

    ESPECIE   estudo do LAB (NAO e motor, NAO e pote, NAO toca Sala nem repo). So LE copias locais.
    ENTRADAS  ANALISE-R7 (86 cruzamentos), CRUZAMENTOS-MAX (refeitos + portfolio_match + competitive_set),
              LIVRO R6 e R7 (sinais), POTE-R6 e POTE-R7 (objetos), SALA_ATUAL da R7 (identidade do documento).
    SAIDAS    POC-RESULTADO.json · MAPA-MIGRACAO.json · DELTA-R7-R8-SINTETICO.json (tudo nesta pasta)

    A IDEIA EM 4 PECAS
      1. CROSSING_KEY = a pergunta, em texto canonico legivel:  FAMILIA/vN|SLOT=VALOR|...  (ordem fixa por familia).
         CROSSING_ID  = "XQ-" + sha256(CROSSING_KEY)[:16]  (derivado; qualquer um reconfere).
      2. Slot com NAO SEI NUNCA junta: vira  NAO_SEI@<identidade do documento>  (NAO SEI != NAO SEI).
      3. A prova e um LINK (CROSSING_KEY x EVIDENCIA); EVIDENCIA = identidade do DOCUMENTO
         (raw_document_key, ou SHA:<raw_sha256> quando a Coleta nao deu document_key). O mesmo documento
         lido duas vezes pela Coleta e UMA evidencia.
      4. O estado e FUNCAO das provas validas + edicao da referencia + versao da regra; o DELTA entre duas
         corridas e a diferenca por CROSSING_KEY (NOVO / FORTALECEU / ENFRAQUECEU / MUDOU_ESTADO / SAIU / IGUAL).

    VOCABULARIO v0 (PROVISORIO, declarado): substancia = chave_substancia de motor/cruzamentos_max.py;
    praga = nome_do_problema de leis/boletim_do_campo.py (lista MESMO_PROBLEMA) + EPPO so onde o IAB verificou;
    cultura = tabela pequena abaixo (especie != grupo); lugar = tabela pequena abaixo (nivel do texto).
    D104.3: o dono do vocabulario e o registro canonico do IAB; este v0 so existe para a prova de conceito.
"""
import collections, copy, hashlib, json, os, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
INS = os.path.join(AQUI, "insumos")
EXP = "C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
R7 = EXP + "/EXPD78-R7-20260927T183035Z"
R6 = EXP + "/EXPD78-R6-20260927T142510Z"
NAO_SEI = "NAO SEI"
VOCAB_VERSION = "VOCAB-v0-LAB-POC"
REGRA_VERSION = "IDENT-v0-LAB-POC"


def ler(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def dobrar(s):
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c)).lower()


def chave_substancia(s):  # copia de motor/cruzamentos_max.py:260
    return re.sub(r"[^A-Z0-9]", "", dobrar(s).upper())


# cultura: ESPECIE e GRUPO sao codigos diferentes; o grupo nunca vira o membro (red team C3)
CULTURA = {"vite": "CROP:VITE", "vigneto": "CROP:VITE", "uva": "CROP:VITE", "viti": "CROP:VITE",
           "melo": "CROP:MELO", "mele": "CROP:MELO", "olivo": "CROP:OLIVO", "ulivo": "CROP:OLIVO", "olive": "CROP:OLIVO",
           "pomacee": "CROP_GRUPO:POMACEE", "drupacee": "CROP_GRUPO:DRUPACEE", "cereali": "CROP_GRUPO:CEREALI"}
# praga: nome_do_problema (MESMO_PROBLEMA) -> codigo; EPPO so onde o IAB o verificou (DACUOL, CERTCA, PRAYOL)
PRAGA = {"mosca dell'olivo": "PEST:EPPO:DACUOL", "mosca della frutta": "PEST:EPPO:CERTCA",
         "tignola dell'olivo": "PEST:EPPO:PRAYOL", "flavescenza dorata della vite": "PEST:LOCAL:FLAVESCENZA_DORATA"}
MESMO_PROBLEMA = [(r"mosca dell['’ ]*oliv[ao]|mosca delle olive|bactrocera oleae", "mosca dell'olivo"),
                  (r"ceratitis capitata|mosca mediterranea", "mosca della frutta"),
                  (r"prays oleae|tignola delle olive|tignola dell['’ ]*olivo", "tignola dell'olivo")]
# lugar: so nomes que o texto sustentou (D112). Nivel diferente = chave diferente; a hierarquia so serve a vistas.
LUGAR = {"lecce": ("PROV", "IT-PROV:LE"), "siena": ("PROV", "IT-PROV:SI"), "puglia": ("REG", "IT-REG:PUGLIA"),
         "toscana": ("REG", "IT-REG:TOSCANA"), "calabria": ("REG", "IT-REG:CALABRIA"), "italia": ("PAIS", "IT")}
ORDEM_NIVEL = {"PROV": 0, "REG": 1, "PAIS": 2}


def nome_do_problema(f):
    f = re.sub(r"\s+", " ", str(f or "").strip().lower())
    return next((n for r, n in MESMO_PROBLEMA if re.fullmatch(r, f)), f)


def cod_cultura(nome):
    return CULTURA.get(dobrar(nome).strip())


def cod_praga(nome):
    n = nome_do_problema(nome)
    return PRAGA.get(n)


def lugar_mais_fino(fact_location):
    """'Puglia ; Lecce' -> ('IT-PROV:LE', 'IT-REG:PUGLIA'): o nivel mais fino que o texto sustentou + o pai."""
    if not fact_location or fact_location == NAO_SEI:
        return None, None
    achados = [LUGAR[dobrar(x).strip()] for x in str(fact_location).split(";") if dobrar(x).strip() in LUGAR]
    if not achados:
        return None, None
    achados.sort(key=lambda t: ORDEM_NIVEL[t[0]])
    return achados[0][1], (achados[1][1] if len(achados) > 1 else None)


FAMILIAS = {  # ordem fixa dos slots = parte da lei de cada familia
    "F1_ROTULO_X_SUBSTANCIA_CITADA": ("JURISDICAO", "AI", "CROP"),
    "F2_PORTFOLIO_MATCH": ("JURISDICAO", "CROP", "TARGET"),
    "F3_COMPETITIVE_SET": ("JURISDICAO", "AI", "REGISTRO"),
    "F4_JANELA_CULTURA_PRAGA": ("CROP", "TARGET", "LUGAR", "CAMPANHA"),
}


def chave(familia, slots, doc_token):
    """CROSSING_KEY canonica. Slot NAO SEI -> NAO_SEI@<documento>: nunca junta com outro NAO SEI."""
    partes, nao_sei = [familia + "/v1"], []
    for s in FAMILIAS[familia]:
        v = slots.get(s)
        if v in (None, "", NAO_SEI):
            v = "NAO_SEI@" + doc_token
            nao_sei.append(s)
        partes.append("%s=%s" % (s, v))
    k = "|".join(partes)
    return k, "XQ-" + sha(k)[:16], nao_sei


# ── identidade do DOCUMENTO (evidencia) a partir da copia da Sala ──────────────────────────────────────
SALA = []  # NUVEM: copia da Sala AUSENTE nesta maquina -> identidade do documento cai para ITEM:<SALA_CHAVE>
POR_SK = {"%s#%s" % (r["run_id"], r["ordem"]): r for r in SALA}
POR_ITEM = {str(r["item_id"]): r for r in SALA}


def doc_de(r):
    return r.get("raw_document_key") or ("SHA:" + (r.get("raw_sha256") or "")[:16])


def doc_de_sk(sk):
    r = POR_SK.get(sk)
    return (doc_de(r), r) if r else ("ITEM:" + str(sk), None)


# ══ 1 · F1 — os 86 cruzamentos R7 (rotulo x substancia citada) ═══════════════════════════════════════
ANALISE = ler(os.path.join(INS, "max-ANALISE-R7.json"))
MAX = ler(os.path.join(INS, "max-CRUZAMENTOS-MAX.json"))
REF = {r["OBJETO_ID"]: r for r in MAX["REFEITOS"]}
links = []  # cada link = (CROSSING_ID, EVIDENCIA, papel, estado do link, ...)
mapa = []
for c in ANALISE["CROSSINGS"]:
    r = REF[c["OBJETO_ID"]]
    doc, row = doc_de_sk(c["SALA_CHAVE"])
    ligadas = sorted(set(r.get("CULTURAS_LIGADAS_NO_TROCO") or []) | set(r.get("X3H_R7") or []))
    crop = cod_cultura(ligadas[0]) if len(ligadas) == 1 else None  # 2+ culturas ligadas = ambiguo -> NAO SEI
    k, xid, ns = chave("F1_ROTULO_X_SUBSTANCIA_CITADA",
                       {"JURISDICAO": "IT", "AI": "AI:" + chave_substancia(c["SUBSTANCIA"]), "CROP": crop}, doc)
    estado_link = r["FINAL"]
    links.append({"CROSSING_ID": xid, "CROSSING_KEY": k, "FAMILIA": "F1", "EVIDENCIA": doc, "SOURCE_ID": c["SOURCE_ID"],
                  "SALA_CHAVE": c["SALA_CHAVE"], "ESTADO_DO_LINK": estado_link, "CHAVE_COMPLETA": not ns,
                  "SLOTS_NAO_SEI": ns, "ENTITY_SOURCE_DA_CULTURA": ("HEADER/NEAR (ligada a substancia)" if crop
                                                                   else "DOCUMENT (lista do documento: NAO SEI por entidade)"),
                  "DATA_DO_BOLETIM": ((r.get("CONFIRMACAO") or {}).get("DATA_DO_BOLETIM") or c.get("PUBLISHED_AT") or NAO_SEI),
                  "CULTURAS_DO_DOCUMENTO": (c.get("FONTE") or {}).get("CULTURA_NO_READY") or []})
    mapa.append({"ID_ANTIGO": c["OBJETO_ID"], "ESQUEMA_ANTIGO": "XC (piloto 2b4e095f l.350 + @run da coleta, analise_r7.py:171)",
                 "CROSSING_ID": xid, "CROSSING_KEY": k, "PAPEL_NOVO": "LINK de evidencia (documento x pergunta)",
                 "RELACAO": "wasRevisionOf-like: o ID antigo passa a ALIAS do link, nunca e apagado"})

# ══ 2 · F2 — portfolio_match (par cultura x praga escrito na secao do boletim) ═════════════════════
for pm in MAX["PORTFOLIO"]:
    pb = pm["PAR_DO_BOLETIM"]
    doc, row = doc_de_sk(pb["SALA_CHAVE"])
    k, xid, ns = chave("F2_PORTFOLIO_MATCH", {"JURISDICAO": "IT", "CROP": cod_cultura(pb["CULTURA"]),
                                              "TARGET": cod_praga(pb["PRAGA"])}, doc)
    links.append({"CROSSING_ID": xid, "CROSSING_KEY": k, "FAMILIA": "F2", "EVIDENCIA": doc, "SOURCE_ID": pb["SOURCE_ID"],
                  "SALA_CHAVE": pb["SALA_CHAVE"], "ESTADO_DO_LINK": pm["ESTADO"], "CHAVE_COMPLETA": not ns,
                  "SLOTS_NAO_SEI": ns, "PRAGA_ESCRITA": pb["PRAGA"], "DATA_DO_BOLETIM": pb.get("PUBLISHED_AT") or NAO_SEI})

# ══ 3 · F3 — competitive_set (cadastro: mesma substancia, outra empresa) ═══════════════════════════
ITENS_MAX = ler(os.path.join(INS, "max-CRUZAMENTOS-MAX-ITENS-DO-POTE.json"))["ITENS_POR_FERRAMENTA"]
cs_antigos = ITENS_MAX["competitors"]
for o in cs_antigos:
    ch = o["CHAVES"]
    reg = str(ch["PRODUCT_ID"]).split(":")[-1]           # tira a EDICAO do id (IT-T4-001:MINSALUTE_FTS6_20260907:<reg>)
    for ai in ch["SUBSTANCIA_EM_COMUM"]:
        k, xid, ns = chave("F3_COMPETITIVE_SET", {"JURISDICAO": "IT", "AI": "AI:" + chave_substancia(ai),
                                                  "REGISTRO": "MINSALUTE:" + reg}, "cadastro")
        links.append({"CROSSING_ID": xid, "CROSSING_KEY": k, "FAMILIA": "F3",
                      "EVIDENCIA": "REFERENCIA:" + str(ch["PRODUCT_ID"]).rsplit(":", 1)[0],
                      "GATILHO": o["PROVA"][0]["ITEM_ID"], "SOURCE_ID": "IT-T4-001", "ESTADO_DO_LINK": "NO_CADASTRO",
                      "CHAVE_COMPLETA": True, "SLOTS_NAO_SEI": [], "ID_ANTIGO": o["OBJETO_ID"]})
    mapa.append({"ID_ANTIGO": o["OBJETO_ID"], "ESQUEMA_ANTIGO": "XMAX CS (cruzamentos_max.py:1042, preso a origem + edicao no PRODUCT_ID)",
                 "CROSSING_ID": [l["CROSSING_ID"] for l in links if l.get("ID_ANTIGO") == o["OBJETO_ID"]],
                 "PAPEL_NOVO": "pergunta F3 por (substancia, registo); a edicao do cadastro vai para a AVALIACAO"})

# ══ 4 · F4 — janela olivo x mosca (sonda R7): episodio = pergunta + CAMPANHA ═════════════════════════
for it in ANALISE["CORTE_VERTICAL"]["ITENS"]:
    doc, row = doc_de_sk(it["SALA_CHAVE"])
    fino, pai = lugar_mais_fino(it["LOCAL"].get("FACT_LOCATION"))
    tempo_ok = it["TEMPO"].get("TEMPORAL_STATE") == "ANCORADO" and "2026" in str(it["TEMPO"].get("FACT_TIME"))
    k, xid, ns = chave("F4_JANELA_CULTURA_PRAGA", {"CROP": "CROP:OLIVO", "TARGET": "PEST:EPPO:DACUOL",
                                                   "LUGAR": fino, "CAMPANHA": "2026" if tempo_ok else None}, doc)
    links.append({"CROSSING_ID": xid, "CROSSING_KEY": k, "FAMILIA": "F4", "EVIDENCIA": doc, "SOURCE_ID": it["SOURCE_ID"],
                  "SALA_CHAVE": it["SALA_CHAVE"], "ESTADO_DO_LINK": it.get("ABERTA_AGORA"), "METODO": it.get("METODO"),
                  "FACT_TIME": it["TEMPO"].get("FACT_TIME"), "LUGAR_PAI": pai, "CHAVE_COMPLETA": not ns, "SLOTS_NAO_SEI": ns})


# ── consolidacao: estado = funcao das provas VALIDAS (regra declarada por familia) ────────────────────
ORDEM_F1 = ["CONFIRMED_YES", "POSSIBLE_ANSWER_YES_A_CONFIRMAR", "UNRESOLVED", "PARTIAL_GRAO_INCOMPATIVEL",
            "POSSIBLE_ANSWER_NO", "NOT_POSSIBLE"]


def consolidar(ls):
    fam = ls[0]["FAMILIA"]
    evid = sorted({l["EVIDENCIA"] for l in ls})
    fontes = sorted({l["SOURCE_ID"] for l in ls})
    estados = collections.Counter(l["ESTADO_DO_LINK"] for l in ls)
    if fam == "F1":
        # a resposta do lado do ROTULO e a mesma para todos os links (depende de AI x CROP x edicao);
        # o link so muda a qualidade do lado do BOLETIM. Estado = o melhor estado PROVADO por um link valido.
        est = next(s for s in ORDEM_F1 if s in estados)
    elif fam == "F4":
        validos = [l for l in ls if l["ESTADO_DO_LINK"] in ("NO", "YES")]
        est = ("CONFLITANTE" if {"NO", "YES"} <= {l["ESTADO_DO_LINK"] for l in validos} else
               (validos[-1]["ESTADO_DO_LINK"] if validos else NAO_SEI))
    else:
        est = estados.most_common(1)[0][0] if len(estados) == 1 else "CONFLITANTE"
    return {"CROSSING_ID": ls[0]["CROSSING_ID"], "CROSSING_KEY": ls[0]["CROSSING_KEY"], "FAMILIA": fam,
            "CHAVE_COMPLETA": ls[0]["CHAVE_COMPLETA"], "ESTADO": est, "ESTADOS_DOS_LINKS": dict(estados),
            "N_LINKS": len(ls), "N_EVIDENCIAS_DOCUMENTO": len(evid), "N_SOURCE_ID": len(fontes),
            "EVIDENCIAS": evid, "SOURCE_IDS": fontes,
            "NOTA_INDEPENDENCIA": "N_SOURCE_ID e PROXY de originador (INT-LAW-071): SOURCE_ID != instituicao provada"}


def agrupar(ls):
    g = collections.OrderedDict()
    for l in ls:
        g.setdefault(l["CROSSING_ID"], []).append(l)
    return {k: consolidar(v) for k, v in g.items()}


PERGUNTAS = agrupar(links)


def resumo_familia(f, antigos):
    ls = [l for l in links if l["FAMILIA"] == f]
    qs = [q for q in PERGUNTAS.values() if q["FAMILIA"] == f]
    comp = [q for q in qs if q["CHAVE_COMPLETA"]]
    return {"OBJETOS_ANTIGOS": antigos, "LINKS": len(ls), "PERGUNTAS_DISTINTAS": len(qs),
            "PERGUNTAS_COM_CHAVE_COMPLETA": len(comp),
            "LINKS_EM_PERGUNTAS_COM_CHAVE_COMPLETA": sum(q["N_LINKS"] for q in comp),
            "PERGUNTAS_SEM_CHAVE (1 por documento, NAO juntam)": len(qs) - len(comp),
            "PERGUNTAS_COM_2+_LINKS": [{"CROSSING_KEY": q["CROSSING_KEY"], "N_LINKS": q["N_LINKS"],
                                        "N_EVIDENCIAS_DOCUMENTO": q["N_EVIDENCIAS_DOCUMENTO"], "N_SOURCE_ID": q["N_SOURCE_ID"],
                                        "ESTADO": q["ESTADO"], "ESTADOS_DOS_LINKS": q["ESTADOS_DOS_LINKS"]}
                                       for q in comp if q["N_LINKS"] > 1]}


RES = {"F1": resumo_familia("F1", len(ANALISE["CROSSINGS"])),
       "F2": resumo_familia("F2", len(MAX["PORTFOLIO"])),
       "F3": resumo_familia("F3", len(cs_antigos)),
       "F4": resumo_familia("F4", len(ANALISE["CORTE_VERTICAL"]["ITENS"]))}

# F3: quantos objetos de concorrente o esquema atual cria POR GATILHO (duplicaria a cada novo boletim)
cs_por_gatilho = collections.Counter(o["PROVA"][0]["ITEM_ID"] for o in cs_antigos)
RES["F3"]["OBJETOS_ANTIGOS_POR_GATILHO"] = dict(cs_por_gatilho)
RES["F3"]["EDICAO_DENTRO_DO_PRODUCT_ID_ANTIGO"] = sum(1 for o in cs_antigos if "MINSALUTE_FTS6_20260907" in str(o["CHAVES"]["PRODUCT_ID"]))

# ── contra-prova: a fusao INGENUA (cultura da LISTA do documento) que o LAB rejeita ─────────────────────
ingenua = collections.Counter()
for l in (x for x in links if x["FAMILIA"] == "F1"):
    for cu in l["CULTURAS_DO_DOCUMENTO"] or ["?"]:
        ingenua[(l["CROSSING_KEY"].split("|")[2], cod_cultura(cu) or "CROP:" + dobrar(cu))] += 1
RES["F1"]["CONTRA_PROVA_FUSAO_INGENUA_PELA_LISTA_DO_DOCUMENTO"] = {
    "GRUPOS": len(ingenua), "GRUPOS_COM_2+": sum(1 for v in ingenua.values() if v > 1),
    "MAIORES": [("|".join(k), v) for k, v in ingenua.most_common(5)],
    "PORQUE_E_ERRADA": "a cultura e a lista do DOCUMENTO (ENTITY_SOURCE=DOCUMENT); juntar por ela cria convergencia falsa (INT-LAW-037/081)"}

# ══ 5 · SINAIS / FUTURO: rotacao de ID entre corridas (medida) e o ID estavel proposto ════════════════
ROTACAO = {"NUVEM": "NAO RE-MEDIDO: LIVRO R6/R7 e POTE-R6 ausentes nesta maquina"}
# ── documentos repetidos na Sala (a mesma evidencia entrou 2x pela Coleta) ─────────────────────────────
rep = collections.Counter(doc_de(r) for r in SALA)
DOCS_REPETIDOS = {"ITENS_NA_SALA": len(SALA), "DOCUMENTOS_DISTINTOS": len(rep), "NUVEM": "Sala ausente: NAO RE-MEDIDO",
                  "DOCUMENTOS_COM_2+_ITENS": sum(1 for v in rep.values() if v > 1),
                  "EXEMPLO": [k for k, v in rep.items() if v > 1][:3]}


# ══ 6 · CORRIDA SEGUINTE SINTETICA (R8-SINT): 2 itens a mais + 1 repeticao ═══════════════════════════
def estado_publicavel(qs):
    return {q["CROSSING_ID"]: q for q in qs.values()}


antes = estado_publicavel(PERGUNTAS)
links8 = copy.deepcopy(links)
SINT = [
    # (a) boletim novo de UMA cultura (vite) que cita folpet: mesma pergunta F1 FOLPET x VITE
    {"FAMILIA": "F1", "slots": {"JURISDICAO": "IT", "AI": "AI:FOLPET", "CROP": "CROP:VITE"},
     "EVIDENCIA": "SINT:CAND-9001:bollettino-vite-22-09-2026", "SOURCE_ID": "CAND-9001-SINTETICO",
     "ESTADO_DO_LINK": "CONFIRMED_YES", "DATA_DO_BOLETIM": "2026-09-22", "SALA_CHAVE": "SINT-LINHA#0",
     "ENTITY_SOURCE_DA_CULTURA": "HEADER/NEAR (ligada a substancia)", "CULTURAS_DO_DOCUMENTO": ["vite"]},
    # (b) ARIF n.39 sintetico (mesma instituicao, semana seguinte, Lecce, soglia superada): F4 muda de estado; F2 ganha citacao
    {"FAMILIA": "F4", "slots": {"CROP": "CROP:OLIVO", "TARGET": "PEST:EPPO:DACUOL", "LUGAR": "IT-PROV:LE", "CAMPANHA": "2026"},
     "EVIDENCIA": "SINT:IT-T3-008:Notiziario_N39_23-09-2026", "SOURCE_ID": "IT-T3-008", "ESTADO_DO_LINK": "YES",
     "METODO": "FONTE_DECLARA_SOGLIA_SUPERADA (SINTETICO)", "FACT_TIME": "23 - 29 settembre 2026", "SALA_CHAVE": "SINT-ARIF#0"},
    {"FAMILIA": "F2", "slots": {"JURISDICAO": "IT", "CROP": "CROP:OLIVO", "TARGET": "PEST:EPPO:DACUOL"},
     "EVIDENCIA": "SINT:IT-T3-008:Notiziario_N39_23-09-2026", "SOURCE_ID": "IT-T3-008", "ESTADO_DO_LINK": "SEM_PAR_LIDO",
     "DATA_DO_BOLETIM": "2026-09-23", "SALA_CHAVE": "SINT-ARIF#0", "PRAGA_ESCRITA": "mosca delle olive"},
]
for s in SINT:
    fam = {"F1": "F1_ROTULO_X_SUBSTANCIA_CITADA", "F2": "F2_PORTFOLIO_MATCH", "F4": "F4_JANELA_CULTURA_PRAGA"}[s["FAMILIA"]]
    k, xid, ns = chave(fam, s["slots"], s["EVIDENCIA"])
    l = {kk: vv for kk, vv in s.items() if kk != "slots"}
    l.update({"CROSSING_ID": xid, "CROSSING_KEY": k, "CHAVE_COMPLETA": not ns, "SLOTS_NAO_SEI": ns, "SINTETICO": True})
    links8.append(l)
# (c) a Coleta traz DE NOVO o boletim da Campania SA-16-09 (3.a copia): mesma evidencia -> nao muda nada
camp = next((l for l in links8 if l["FAMILIA"] == "F2" and l["EVIDENCIA"] == "CAMPANIA:SA:16-09-2026"), None) or next(l for l in links8 if l["FAMILIA"] == "F2")
links8.append(dict(camp, SALA_CHAVE="SINT-REPETICAO-CAMPANIA#0", SINTETICO=True))


def dedupe(ls):
    """O mesmo (pergunta, documento) conta UMA vez — idempotencia do link."""
    vistos, out = set(), []
    for l in ls:
        k = (l["CROSSING_ID"], l["EVIDENCIA"])
        if k not in vistos:
            vistos.add(k)
            out.append(l)
    return out


RANK = {"CONFIRMED_YES": 6, "POSSIBLE_ANSWER_YES_A_CONFIRMAR": 5, "UNRESOLVED": 4, "PARTIAL_GRAO_INCOMPATIVEL": 3,
        "POSSIBLE_ANSWER_NO": 2, "NOT_POSSIBLE": 1}
depois = estado_publicavel(agrupar(dedupe(links8)))
antes = estado_publicavel(agrupar(dedupe(links)))


def diff(a, b):
    out = []
    for xid in sorted(set(a) | set(b)):
        x, y = a.get(xid), b.get(xid)
        if x and not y:
            out.append({"CROSSING_ID": xid, "CROSSING_KEY": x["CROSSING_KEY"], "MUDANCA": "SAIU", "ESTADO_DE": x["ESTADO"]})
            continue
        if y and not x:
            out.append({"CROSSING_ID": xid, "CROSSING_KEY": y["CROSSING_KEY"], "MUDANCA": "NOVO", "ESTADO_PARA": y["ESTADO"],
                        "EVIDENCIAS_PARA": y["N_EVIDENCIAS_DOCUMENTO"]})
            continue
        novas = sorted(set(y["EVIDENCIAS"]) - set(x["EVIDENCIAS"]))
        saidas = sorted(set(x["EVIDENCIAS"]) - set(y["EVIDENCIAS"]))
        if x["ESTADO"] != y["ESTADO"]:
            m = "MUDOU_ESTADO"
        elif novas and not saidas:
            m = "FORTALECEU" if y["N_SOURCE_ID"] > x["N_SOURCE_ID"] else "MAIS_EVIDENCIA_MESMA_ORIGEM"
        elif saidas:
            m = "ENFRAQUECEU"
        else:
            m = "IGUAL"
        if m == "IGUAL":
            continue
        rel = None
        if m == "MUDOU_ESTADO" and y["FAMILIA"] == "F4":
            rel = "TEMPORAL_CHANGE (mesma origem, semana seguinte; INT-LAW-079) — nao e contradicao"
        out.append({"CROSSING_ID": xid, "CROSSING_KEY": y["CROSSING_KEY"], "MUDANCA": m,
                    "ESTADO_DE": x["ESTADO"], "ESTADO_PARA": y["ESTADO"],
                    "EVIDENCIAS_DE": x["N_EVIDENCIAS_DOCUMENTO"], "EVIDENCIAS_PARA": y["N_EVIDENCIAS_DOCUMENTO"],
                    "SOURCE_ID_DE": x["N_SOURCE_ID"], "SOURCE_ID_PARA": y["N_SOURCE_ID"],
                    "EVIDENCIAS_NOVAS": novas, "CAUSA": "NOVA_EVIDENCIA", "RELACAO": rel})
    return out


mud = diff(antes, depois)

# o que o ESQUEMA ATUAL faria com os mesmos 2 itens (contagem de objetos novos/rotacionados)
folpet_cs = [o for o in cs_antigos if "FOLPET" in [chave_substancia(a) for a in o["CHAVES"]["SUBSTANCIA_EM_COMUM"]]]
ATUAL_FARIA = {
    "SINAIS": "todos os SG e FUT ganham ID novo (run_id no hash): 0 continuidade (medido R6->R7: 0/10 sinais, 0/47 objetos)",
    "F1_FOLPET_X_VITE": "+1 cartao XC novo (o 3.o sobre a mesma pergunta; hoje ja sao 2)",
    "F2_OLIVO_X_MOSCA": "+1 cartao PM novo (o 14.o sobre a mesma pergunta; hoje ja sao 13)",
    "F3_CONCORRENTES_FOLPET": "+%d objetos CS repetidos (a lista de concorrentes do folpet e recriada por gatilho)" % len(folpet_cs),
    "F4_JANELA_LECCE": "sem objeto de janela no pote (a sonda R7 so vive na ANALISE); o casco nao sabe dizer que mudou",
    "REPETICAO_CAMPANIA": "o item repetido vira mais 1 PM (e ja conta 2x hoje)"}

DELTA = {
    "SCHEMA": "POTE_DELTA/v0-PROPOSTA-LAB (NAO e contrato; exemplo sobre dados SINTETICOS marcados)",
    "ANTERIOR": {"INTELLIGENCE_RUN_ID": "IR-e09acab6365032523d6e", "POTE_SHA256": "0189967826ea79e05fa93b144144ddcedd151370ba56d11a56d5066946d2b930 (POTE-R7 publicado, docs/casco/r7)"},
    "ATUAL": {"INTELLIGENCE_RUN_ID": "IR-R8-SINTETICO", "CORRIDA_SINTETICA": True},
    "REGRA_DE_IDENTIDADE": REGRA_VERSION, "VOCABULARIO": VOCAB_VERSION,
    "CONTAGEM": dict(collections.Counter(m["MUDANCA"] for m in mud)),
    "MUDANCAS": mud,
    "SEM_MUDANCA": len(set(antes) & set(depois)) - sum(1 for m in mud if m["MUDANCA"] not in ("NOVO", "SAIU")),
    "O_QUE_O_ESQUEMA_ATUAL_FARIA": ATUAL_FARIA}

resultado = {
    "SCHEMA": "LAB-POC-IDENTIDADE/1", "REGRA": REGRA_VERSION, "VOCABULARIO": VOCAB_VERSION,
    "INSUMOS_SHA256": {n: hashlib.sha256(open(os.path.join(INS,n),"rb").read()).hexdigest() for n in sorted(os.listdir(INS))},
    "COLAPSO_POR_FAMILIA": RES, "ROTACAO_DE_ID_R6_R7": ROTACAO, "DOCUMENTOS_REPETIDOS_NA_SALA": DOCS_REPETIDOS,
    "PERGUNTAS": list(PERGUNTAS.values())}
for nome, obj in [("POC-RESULTADO-NUVEM.json", resultado), ("MAPA-MIGRACAO-NUVEM.json", mapa), ("DELTA-R7-R8-SINTETICO-NUVEM.json", DELTA)]:
    with open(os.path.join(AQUI, nome), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# ── resumo na tela ─────────────────────────────────────────────────────────────────────────────────────
for f, r in RES.items():
    print(f, "antigos=%d links=%d perguntas=%d (com chave=%d, cobrindo %d links; sem chave=%d)" % (
        r["OBJETOS_ANTIGOS"], r["LINKS"], r["PERGUNTAS_DISTINTAS"], r["PERGUNTAS_COM_CHAVE_COMPLETA"],
        r["LINKS_EM_PERGUNTAS_COM_CHAVE_COMPLETA"], r["PERGUNTAS_SEM_CHAVE (1 por documento, NAO juntam)"]))
    for q in r["PERGUNTAS_COM_2+_LINKS"]:
        print("   2+:", q)
print("F3 por gatilho:", RES["F3"]["OBJETOS_ANTIGOS_POR_GATILHO"], "edicao no PRODUCT_ID:", RES["F3"]["EDICAO_DENTRO_DO_PRODUCT_ID_ANTIGO"])
print("F1 contra-prova ingenua:", RES["F1"]["CONTRA_PROVA_FUSAO_INGENUA_PELA_LISTA_DO_DOCUMENTO"]["GRUPOS"],
      "grupos,", RES["F1"]["CONTRA_PROVA_FUSAO_INGENUA_PELA_LISTA_DO_DOCUMENTO"]["GRUPOS_COM_2+"], "com 2+")
print("ROTACAO:", {k: v for k, v in ROTACAO.items() if k not in ("EXEMPLOS", "CAUSA")})
print("DOCS REPETIDOS:", DOCS_REPETIDOS)
print("DELTA:", DELTA["CONTAGEM"], "sem mudanca:", DELTA["SEM_MUDANCA"])
for m in mud:
    print("   ", m["MUDANCA"], m["CROSSING_KEY"], m.get("ESTADO_DE"), "->", m.get("ESTADO_PARA"),
          "evid", m.get("EVIDENCIAS_DE"), "->", m.get("EVIDENCIAS_PARA"), "|", m.get("RELACAO") or "")
print("ATUAL FARIA:", ATUAL_FARIA)
print("mapa de migracao: %d linhas" % len(mapa))
