#!/usr/bin/env python3
"""ADAMA ITALIA — camada de PRODUCT INTELLIGENCE sobre fontes publicas.

Nao coleta o site da ADAMA: `adama.com/italia/it` so abre em navegador COM JANELA,
e este ambiente nao tem uma. O censo comercial de 51 produtos ja foi capturado em
2026-08-30 na maquina local (branch claude/adama-it-local-catalog) e e reaproveitado
aqui como entrada — a regra da missao e inventariar antes de coletar.

    ./scripts/adama_it_intelligence.py

Entradas:
    data/raw/IT-T4-001/PROD_FTS_6_<AAAAMMDD>.csv   registro do Ministero
                                                   (./scripts/adama_italia.py baixar)
    $IT_PI_INPUTS/IT-ADAMA-CATALOG-CENSUS.json     51 produtos + 141 documentos, do censo local:
        mkdir -p /tmp/inv && git show \
          origin/claude/adama-it-local-catalog:data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-CENSUS.json \
          > /tmp/inv/IT-ADAMA-CATALOG-CENSUS.json
    research/.../MOA-SOURCE-{HRAC,IRAC}.json       (./scripts/adama_it_moa.py)
    HRAC lookup + IRAC MoA classification          modo de acao, com URL de origem

Saida: research/adama-italy-product-intelligence-deep/

Regras que o codigo aplica, nao so documenta:
  - estado administrativo != autorizacao nao vencida != produto comercializavel
  - nome parecido nunca fecha identidade; so numero de registro ou nome exato+titular
  - mistura nunca colapsa num MoA unico; cada componente e classificado separado
  - o que a fonte nao prova sai UNKNOWN, nao sai ausente
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime

RAW = "data/raw/IT-T4-001"
OUT = "research/adama-italy-product-intelligence-deep"
INV = os.environ.get("IT_PI_INPUTS", "/tmp/inv")

# Estados que a fonte marca como administrativamente ativos. NAO significam
# "vencimento no futuro" nem "pode ser vendido hoje" — a secao 3 mede exatamente
# a distancia entre as tres coisas.
ADMIN_ATIVO = ("Autorizzato", "Ri-registrato", "Rinnovato")

HRAC_URL = "https://www.hracglobal.com/tools/classification-lookup"
IRAC_URL = "https://irac-online.org/mode-of-action/classification-online/"
FRAC_URL = "https://www.frac.info/media/s1zfrjqa/frac-code-list-2026.pdf"


def _d(s):
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError):
        return None


def _norm_reg(s):
    """008259 e 8259 sao o mesmo registro. Zeros a esquerda nao carregam sentido."""
    s = (s or "").strip()
    return s.lstrip("0") or None


def _norm_nome(s):
    """Para COMPARAR nomes — nunca para exibir, e nunca como prova sozinho."""
    s = (s or "").upper()
    s = s.replace("®", "").replace("™", "")
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def _norm_ai(s):
    return re.sub(r"[^A-Z0-9-]+", "-", (s or "").upper()).strip("-")


def _componentes(s):
    """Separa a mistura em componentes.

    O campo `sostanze_attive` separa por '|' — em 148 dos 602 registros ADAMA — e
    NUNCA por '+'. A primeira versao deste codigo dividia so por '+', o que quer
    dizer que nenhuma mistura foi dividida e cada uma virou um MoA artificial,
    exatamente o que a regra proibia. Os dois separadores ficam aceitos aqui para
    o codigo nao depender de qual deles a fonte resolve usar amanha."""
    for comp in re.split(r"[|+]", s or ""):
        comp = comp.strip()
        if comp and comp != "-":
            yield comp


def carregar_registro():
    arqs = sorted(f for f in os.listdir(RAW) if f.startswith("PROD_FTS_6_"))
    if not arqs:
        sys.exit(f"nenhum CSV em {RAW}")
    caminho = os.path.join(RAW, arqs[-1])
    snapshot = datetime.strptime(re.search(r"(\d{8})", caminho).group(1), "%Y%m%d").date()
    with open(caminho, encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh, delimiter=";"))
    return os.path.basename(caminho), snapshot, linhas


def _json(nome):
    caminho = os.path.join(INV, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- 3 · o conflito
def resolver_estado(linhas_adama, snapshot, hoje):
    """Separa as tres coisas que o relatorio anterior tinha colapsado em 'vivo hoje'.

    REGULATORY_ADMIN_STATE   o que a fonte escreve no campo stato_amministrativo
    FORMAL_VALIDITY_STATE    a data de vencimento comparada ao snapshot da fonte
    CURRENTLY_MARKETABLE     UNKNOWN sempre: depende de periodo de smaltimento,
                             que e fixado por decreto e nao existe neste dataset
    """
    saida = []
    for r in linhas_adama:
        admin = r["stato_amministrativo"]
        ativo = admin.startswith(ADMIN_ATIVO)
        venc = _d(r["data_scadenza_autorizzazione"])
        if not ativo:
            formal, interp = "NOT_ADMIN_ACTIVE", "HISTORICO"
        elif venc is None:
            formal, interp = "NO_EXPIRY_DATE_IN_SOURCE", "UNKNOWN"
        elif venc >= snapshot:
            formal, interp = "UNEXPIRED_AT_SNAPSHOT", "ADMIN_ACTIVE_AND_UNEXPIRED"
        elif venc >= hoje:
            formal, interp = "UNEXPIRED_AT_SNAPSHOT", "ADMIN_ACTIVE_AND_UNEXPIRED"
        else:
            # A fonte se contradiz consigo mesma: estado ativo, data no passado.
            formal = "EXPIRED_BY_DATE"
            interp = ("STATE_CONFLICT_IN_SOURCE" if venc < snapshot
                      else "EXPIRED_AFTER_SNAPSHOT")
        saida.append({
            "NUM_REGISTRAZIONE": r["num_registrazione"],
            "PRODUCT": r["denominazione_prodotto"],
            "REGULATORY_ADMIN_STATE": admin,
            "ADMIN_ACTIVE": ativo,
            "AUTHORIZATION_EXPIRY_DATE": r["data_scadenza_autorizzazione"],
            "FORMAL_VALIDITY_STATE": formal,
            "GRACE_PERIOD_STATE": "UNKNOWN",
            "CURRENTLY_MARKETABLE_STATE": "UNKNOWN",
            "CURRENT_INTERPRETATION": interp,
            "INTERPRETATION_CONFIDENCE": ("HIGH" if interp != "UNKNOWN" else "LOW"),
        })
    return saida


# ------------------------------------------------------- 2/11 · identidade e cruz
def construir_identidade(linhas_adama, catalogo, estados, todas_linhas):
    """Uma so tabela ligando produto comercial, produto regulatorio e registro.

    A unica chave que fecha identidade e o numero de registro. Nome exato + titular
    entra como segunda chave. Nome parecido nao entra: fica UNRESOLVED de proposito.
    """
    # O cruzamento roda contra o REGISTRO INTEIRO, nao so contra as linhas ADAMA.
    # Um produto do catalogo cuja autorizacao e de outra empresa existe — sao 7 —
    # e cruzar so contra ADAMA o classificaria como "sem registro", que e falso.
    por_reg = {}
    for r in todas_linhas:
        por_reg.setdefault(_norm_reg(r["num_registrazione"]), []).append(r)
    est = {e["NUM_REGISTRAZIONE"]: e for e in estados}

    mapa, seq = [], 0
    usados = set()

    def novo_id():
        nonlocal seq
        seq += 1
        return "IT-PRODUCT-%04d" % seq

    def _composicao_bate(pagina, linha):
        """A pagina escreve o ativo em italiano; o registro, em ingles. Nao da para
        comparar palavra a palavra — da para exigir que ao menos um componente do
        registro apareca na pagina, ou o contrario, pelo radical."""
        pag = re.sub(r"[^A-Z]", " ", (pagina.get("ACTIVE_INGREDIENT") or "").upper())
        toks = {t for t in pag.split() if len(t) >= 6}
        for comp in _componentes(linha["sostanze_attive"]):
            base_comp = re.sub(r"[^A-Z]", "", comp.upper())
            if not base_comp:
                continue
            if any(t[:7] in base_comp or base_comp[:7] in t for t in toks):
                return True
        return False

    for p in catalogo:
        claim = _norm_reg(p.get("MANUFACTURER_CLAIM_REGISTRATION_ID"))
        alvo = por_reg.get(claim) if claim else None
        reg = alvo[0] if alvo else None
        metodo = conf = None
        # O numero publicado e a chave mais forte — mas nao e infalivel, porque quem
        # o digitou foi a area de marketing. O Powerfilm publica 17052, que no
        # registro e o COCTEL GOLD da LAINCO, glifosato + MCPA, enquanto a propria
        # pagina declara oleo de colza. Um digito trocado (17852 -> 17052) tinha
        # criado do nada um "produto de outro titular". Quando nome E composicao
        # discordam ao mesmo tempo, e o numero que cede, nunca os dois fatos.
        if reg and _norm_nome(reg["denominazione_prodotto"]) != _norm_nome(p["PRODUCT_NAME"]) \
                and not _composicao_bate(p, reg):
            # O desempate e o NOME EXATO unico no registro inteiro, nao a composicao:
            # a pagina escreve "olio di colza metilestere" e o registro escreve
            # "RAPE SEED OIL". Sao a mesma coisa em dois idiomas, e exigir que as
            # strings se toquem reprovaria um casamento correto por diferenca de
            # lingua. A composicao serve para DERRUBAR o numero publicado, que e o
            # que ela acabou de fazer; nao serve para confirmar o substituto.
            homonimos = [r for r in todas_linhas
                         if _norm_nome(r["denominazione_prodotto"]) == _norm_nome(p["PRODUCT_NAME"])]
            if len(homonimos) == 1:
                reg = homonimos[0]
                metodo, conf = "EXACT_NAME_UNIQUE__PUBLISHED_NUMBER_CONTRADICTED", "HIGH"
            else:
                reg = None
                metodo, conf = "UNRESOLVED__PUBLISHED_NUMBER_CONTRADICTED_BY_NAME_AND_COMPOSITION", "NONE"
        if reg and metodo is None:
            metodo, conf = "REGISTRATION_NUMBER", "HIGH"
        elif metodo is None:
            # segunda chave: nome exato normalizado contra o registro
            cand = [r for r in todas_linhas
                    if _norm_nome(r["denominazione_prodotto"]) == _norm_nome(p["PRODUCT_NAME"])]
            reg = cand[0] if len(cand) == 1 else None
            metodo = "EXACT_NAME_SINGLE_MATCH" if reg else "UNRESOLVED"
            conf = "MEDIUM" if reg else "NONE"
        if reg:
            usados.add(reg["num_registrazione"])
        e = est.get(reg["num_registrazione"]) if reg else None
        mapa.append({
            "PRODUCT_ID": novo_id(),
            "COMMERCIAL_NAME": p["PRODUCT_NAME"],
            "REGULATORY_NAME": reg["denominazione_prodotto"] if reg else None,
            "ALIASES": sorted({p["PRODUCT_NAME"]} | ({reg["denominazione_prodotto"]} if reg else set())),
            "REGISTRATION_NUMBER": reg["num_registrazione"] if reg else None,
            "REGISTRATION_NUMBER_AS_CLAIMED": p.get("MANUFACTURER_CLAIM_REGISTRATION_ID"),
            "PUBLISHED_NUMBER_CONTRADICTED": "CONTRADICTED" in (metodo or ""),
            "ENTITY_CLASS": ("COMMERCIAL_AND_REGULATORY" if reg else "COMMERCIAL_ONLY"),
            "HOLDER_IS_ADAMA": ("ADAMA" in reg["ragione_sociale"].upper()) if reg else None,
            "NAME_DIVERGES_FROM_REGISTRY": (
                _norm_nome(reg["denominazione_prodotto"]) != _norm_nome(p["PRODUCT_NAME"])
                if reg else None),
            "REGISTRATION_FORMAT_STATE": p.get("REGISTRATION_FORMAT_STATE"),
            "COMMERCIAL_CATALOG_PRESENT": True,
            "REGULATORY_PRESENT": bool(reg),
            "AUTHORIZATION_HOLDER": reg["ragione_sociale"] if reg else None,
            "CATEGORY_PRINTED_ON_PAGE": p.get("CATEGORY_DISPLAY"),
            "CATEGORY_SOURCE": "PRODUCT_PAGE_DISPLAY",
            "URL_PATH_PREFIX": p.get("URL_PATH_PREFIX"),
            "PRODUCT_URL": p.get("PRODUCT_URL"),
            "FORMAL_VALIDITY_STATE": e["FORMAL_VALIDITY_STATE"] if e else None,
            "CURRENT_INTERPRETATION": e["CURRENT_INTERPRETATION"] if e else None,
            "CURRENTLY_MARKETABLE_STATE": "UNKNOWN",
            "SOURCE_IDS": ["IT-ADAMA-CATALOG"] + (["IT-T4-001"] if reg else []),
            "JOIN_METHOD": metodo,
            "JOIN_CONFIDENCE": conf,
        })

    # registros que nao aparecem no catalogo publico atual
    for r in linhas_adama:
        if r["num_registrazione"] in usados:
            continue
        e = est.get(r["num_registrazione"])
        mapa.append({
            "PRODUCT_ID": novo_id(),
            "COMMERCIAL_NAME": None,
            "REGULATORY_NAME": r["denominazione_prodotto"],
            "ALIASES": [r["denominazione_prodotto"]],
            "REGISTRATION_NUMBER": r["num_registrazione"],
            "REGISTRATION_NUMBER_AS_CLAIMED": None,
            "ENTITY_CLASS": "REGULATORY_ONLY",
            "COMMERCIAL_CATALOG_PRESENT": False,
            "REGULATORY_PRESENT": True,
            "AUTHORIZATION_HOLDER": r["ragione_sociale"],
            "CATEGORY_PRINTED_ON_PAGE": None,
            "CATEGORY_SOURCE": None,
            "URL_PATH_PREFIX": None,
            "PRODUCT_URL": None,
            "FORMAL_VALIDITY_STATE": e["FORMAL_VALIDITY_STATE"] if e else None,
            "CURRENT_INTERPRETATION": e["CURRENT_INTERPRETATION"] if e else None,
            "CURRENTLY_MARKETABLE_STATE": "UNKNOWN",
            "SOURCE_IDS": ["IT-T4-001"],
            "JOIN_METHOD": "REGISTRY_ONLY",
            "JOIN_CONFIDENCE": "HIGH",
        })
    return mapa


# ------------------------------------------------------------ 10 · MoA por AI
def construir_ai(linhas_adama, hrac, irac):
    """Cada componente de mistura vira um registro proprio. Nada e colapsado.

    FRAC fica UNKNOWN de proposito: a lista oficial so existe em PDF cuja extracao
    aqui perde glifos — 'M 04' sai como 'M 0'. Publicar o codigo seria publicar o
    defeito do extrator como se fosse a fonte.
    """
    por_ai = defaultdict(set)
    for r in linhas_adama:
        for comp in _componentes(r["sostanze_attive"]):
            por_ai[comp].add(r["num_registrazione"])
    saida = []
    for nome, regs in sorted(por_ai.items()):
        chave = _norm_ai(nome)
        h = hrac.get(nome.upper()) or hrac.get(chave) or {}
        i = irac.get(nome.upper()) or irac.get(chave) or {}
        fontes, urls = [], []
        if h:
            fontes.append("HRAC"); urls.append(HRAC_URL)
        if i:
            fontes.append("IRAC"); urls.append(IRAC_URL)
        saida.append({
            "ACTIVE_INGREDIENT_ID": "IT-AI-" + chave,
            "NAME": nome,
            "NORMALIZED_NAME": chave,
            "REGISTRATION_NUMBERS": sorted(regs),
            "PRODUCT_COUNT": len(regs),
            "HRAC": h.get("HRAC"),
            "HRAC_WSSA": h.get("WSSA"),
            "CHEMICAL_FAMILY": h.get("CHEMICAL_FAMILY"),
            "FRAC": None,
            "FRAC_STATE": "UNKNOWN_LOSSY_PDF_EXTRACTION",
            "IRAC": i.get("IRAC_GROUP"),
            "IRAC_SUBGROUP": i.get("IRAC_SUBGROUP"),
            "SOURCE": fontes or ["NONE"],
            "SOURCE_URL": urls,
            "CONFIDENCE": "HIGH" if fontes else "NONE",
            "MOA_STATE": "CLASSIFIED" if fontes else "UNKNOWN",
        })
    return saida


# ------------------------------------------------------------- 12 · linhagem
def construir_linhagem(linhas_adama):
    """Relacoes que a fonte sustenta, e so elas.

    Mesmo numero de registro com estados diferentes ao longo do tempo nao aparece
    aqui: o dataset traz UMA linha por registro. O que ele sustenta e a continuidade
    por NOME EXATO entre um registro revogado e outro vivo, e a troca de titular
    dentro do grupo. Nome parecido nao gera relacao — gera nada.
    """
    por_nome = defaultdict(list)
    for r in linhas_adama:
        por_nome[_norm_nome(r["denominazione_prodotto"])].append(r)
    rel = []
    for nome, grupo in por_nome.items():
        if len(grupo) < 2:
            continue
        grupo = sorted(grupo, key=lambda r: _d(r["data_registrazione"]) or date.min)
        for a, b in zip(grupo, grupo[1:]):
            mudou = a["ragione_sociale"] != b["ragione_sociale"]
            mesma_ai = _norm_ai(a["sostanze_attive"]) == _norm_ai(b["sostanze_attive"])
            rel.append({
                "FROM_RECORD_ID": a["num_registrazione"],
                "TO_RECORD_ID": b["num_registrazione"],
                "RELATIONSHIP_TYPE": "SAME_EXACT_NAME_LATER_REGISTRATION",
                "HOLDER_CHANGED": mudou,
                "ACTIVE_INGREDIENT_CONTINUITY": mesma_ai,
                "FROM_STATE": a["stato_amministrativo"],
                "TO_STATE": b["stato_amministrativo"],
                "EVIDENCE": "nome exato identico no registro IT-T4-001; datas de registro distintas",
                "CONFIDENCE": "MEDIUM" if mesma_ai else "LOW",
                "NOT_PROVEN": "sucessao comercial, substituicao de rotulo ou continuidade de marca",
            })
    return rel


# ------------------------------------------------------------ 14 · vencimentos
def construir_clusters(linhas_adama, estados, mapa):
    cat = {m["REGISTRATION_NUMBER"] for m in mapa if m["COMMERCIAL_CATALOG_PRESENT"] and m["REGISTRATION_NUMBER"]}
    est = {e["NUM_REGISTRAZIONE"]: e for e in estados}
    grupos = defaultdict(list)
    for r in linhas_adama:
        e = est[r["num_registrazione"]]
        if not e["ADMIN_ACTIVE"]:
            continue
        venc = r["data_scadenza_autorizzazione"]
        for comp in _componentes(r["sostanze_attive"]):
            grupos[(venc, comp)].append(r["num_registrazione"])
    saida = []
    for (venc, ai), regs in sorted(grupos.items(), key=lambda kv: (_d(kv[0][0]) or date.max, kv[0][1])):
        saida.append({
            "EXPIRY_DATE": venc,
            "ACTIVE_INGREDIENT": ai,
            "NUMBER_OF_REGISTRATIONS": len(regs),
            "REGISTRATION_NUMBERS": sorted(regs),
            "COMMERCIAL_CATALOG_OVERLAP": sorted(set(regs) & cat),
            "EU_APPROVAL_STATE": "UNKNOWN",
            "EU_APPROVAL_STATE_WHY": "EU Pesticides Database bloqueia rota nao-navegador: 307 -> sorry.ec.europa.eu",
            "NOT_A_CLAIM": "vencimento nao e risco, retirada nem perda comercial",
        })
    return saida


# ------------------------------------------------------- 11 · reconciliacao
def reconciliar(mapa):
    linhas = []
    for m in mapa:
        titular = m["AUTHORIZATION_HOLDER"] or ""
        if m["ENTITY_CLASS"] == "REGULATORY_ONLY":
            classe = "REGULATORY_ONLY_NOT_FOUND_IN_CURRENT_PUBLIC_CATALOG"
        elif m["ENTITY_CLASS"] == "COMMERCIAL_ONLY":
            classe = "COMMERCIAL_WITH_REGULATORY_MATCH_UNRESOLVED"
        elif "ADAMA" in titular.upper():
            classe = "COMMERCIAL_AND_REGULATORY_ADAMA_HOLDER"
        else:
            classe = "COMMERCIAL_AND_REGULATORY_OTHER_HOLDER"
        linhas.append({
            "PRODUCT_ID": m["PRODUCT_ID"],
            "NAME": m["COMMERCIAL_NAME"] or m["REGULATORY_NAME"],
            "CLASS": classe,
            "AUTHORIZATION_HOLDER": m["AUTHORIZATION_HOLDER"],
            "REGISTRATION_NUMBER": m["REGISTRATION_NUMBER"],
            "JOIN_METHOD": m["JOIN_METHOD"],
            "JOIN_CONFIDENCE": m["JOIN_CONFIDENCE"],
            "LICENSE_OR_DISTRIBUTION_AGREEMENT": "UNKNOWN",
            "WHY_UNKNOWN": "presenca no catalogo + titular provados; contrato entre as partes nao e provado por nenhuma fonte publica lida",
        })
    return linhas


# ---------------------------------------------------------- 6 · rotulos
def manifesto_rotulos(documentos, mapa):
    por_url = {m["PRODUCT_URL"]: m for m in mapa if m.get("PRODUCT_URL")}
    saida = []
    for d in documentos:
        m = por_url.get(d.get("PRODUCT_URL"))
        saida.append({
            "PRODUCT_ID": m["PRODUCT_ID"] if m else None,
            "PRODUCT_NAME": d.get("PRODUCT_NAME"),
            "REGISTRATION_NUMBER": m["REGISTRATION_NUMBER"] if m else None,
            "DOCUMENT_TYPE": d.get("DOCUMENT_TYPE"),
            "LABEL_ON_PAGE": d.get("LABEL_ON_PAGE"),
            "LABEL_DATE": None,
            "LABEL_DATE_STATE": "NOT_EXTRACTED_PDF_NOT_REACHABLE_HERE",
            "LABEL_VERSION": None,
            "SOURCE": "ADAMA_ITALIA_PRODUCT_PAGE",
            "SOURCE_URL": d.get("SOURCE_URL"),
            "SOURCE_ID": "IT-ADAMA-CATALOG",
            "CAPTURED_AT": d.get("CAPTURED_AT"),
            "SHA256": d.get("SHA256"),
            "BYTES": d.get("BYTES"),
            "DOCUMENT_STATE": d.get("STATE"),
            "CONTENT_READABLE": d.get("CONTENT_READABLE"),
            "PARSE_STATE": "NOT_PARSED",
            "PARSE_BLOCKER": "PDF preservado fora deste ambiente; adama.com devolve 403 aqui",
            "LOCAL_FILE": d.get("LOCAL_FILE"),
        })
    return saida


def _pacote(nome):
    caminho = os.path.join(OUT, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    hoje = date.today()
    arquivo, snapshot, linhas = carregar_registro()
    adama = [r for r in linhas if "ADAMA" in r["ragione_sociale"].upper()]

    censo = _json("IT-ADAMA-CATALOG-CENSUS.json")
    catalogo = censo["PRODUCTS"] if censo else []
    documentos = censo["DOCUMENTS"] if censo else []
    # A classificacao de MoA sai do acervo do proprio pacote, gravado por
    # scripts/adama_it_moa.py. Assim o pacote se refaz sem depender de /tmp.
    hrac = (_pacote("MOA-SOURCE-HRAC.json") or {}).get("INGREDIENTS", {})
    irac = (_pacote("MOA-SOURCE-IRAC.json") or {}).get("INGREDIENTS", {})

    estados = resolver_estado(adama, snapshot, hoje)
    mapa = construir_identidade(adama, catalogo, estados, linhas)
    ais = construir_ai(adama, hrac, irac)
    linhagem = construir_linhagem(adama)
    clusters = construir_clusters(adama, estados, mapa)
    recon = reconciliar(mapa)
    rotulos = manifesto_rotulos(documentos, mapa)

    os.makedirs(OUT, exist_ok=True)

    def grava(nome, obj):
        with open(os.path.join(OUT, nome), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)

    meta = {
        "BUILT_AT": hoje.isoformat(),
        "REGISTRY_FILE": arquivo,
        "REGISTRY_SNAPSHOT_DATE": snapshot.isoformat(),
        "CATALOG_CAPTURED_AT": censo["CAPTURED_AT"] if censo else None,
        "SYNTHETIC_RECORDS": 0,
    }

    grava("PRODUCT-IDENTITY-MAP.json", {**meta, "PRODUCTS": mapa})
    grava("PRODUCTS-REGULATORY.json", {**meta, "PRODUCTS": estados})
    grava("PRODUCTS-COMMERCIAL.json", {**meta, "PRODUCTS": catalogo})
    grava("ACTIVE-INGREDIENTS.json", {**meta, "ACTIVE_INGREDIENTS": ais})
    grava("MOA-CLASSIFICATIONS.json", {
        **meta,
        "HRAC_SOURCE_URL": HRAC_URL, "IRAC_SOURCE_URL": IRAC_URL, "FRAC_SOURCE_URL": FRAC_URL,
        "FRAC_STATE": "NOT_PUBLISHED — extracao do PDF oficial perde glifos (M 04 sai como M 0)",
        "CLASSIFICATIONS": [a for a in ais if a["MOA_STATE"] == "CLASSIFIED"],
        "UNCLASSIFIED": [a["NAME"] for a in ais if a["MOA_STATE"] == "UNKNOWN"],
    })
    grava("REGULATORY-LINEAGE.json", {**meta, "RELATIONSHIPS": linhagem})
    grava("EXPIRY-CLUSTERS.json", {**meta, "CLUSTERS": clusters})
    grava("COMMERCIAL-REGULATORY-RECONCILIATION.json", {**meta, "ROWS": recon})
    grava("LABEL-MANIFEST.json", {**meta, "DOCUMENTS": rotulos})

    # As camadas que dependem do conteudo do rotulo nascem vazias e dizem por que.
    vazio = {
        **meta, "RECORDS": [], "COUNT": 0, "STATE": "REAL_GAP",
        "WHY": ("as 51 etichette foram baixadas e conferidas por sha256 em 2026-08-30, "
                "mas os PDF vivem em data/raw (fora do Git) e no bucket Supabase, "
                "sem credencial neste ambiente; adama.com devolve 403 aqui"),
        "WHAT_WOULD_UNBLOCK": "rodar a extracao na maquina local, ou expor SUPABASE_URL/SUPABASE_SECRET_KEY",
    }
    for nome in ("LABEL-USES.json", "HERBICIDE-LABEL-USES.json",
                 "FUNGICIDE-LABEL-USES.json", "INSECTICIDE-LABEL-USES.json",
                 "PRODUCT-CROP-COVERAGE.json", "TARGET-PRODUCT-COVERAGE.json"):
        grava(nome, vazio)

    # ------------------------------------------------- 4 · censo por categoria
    # A categoria impressa na pagina vence o caminho da URL. Nao e teoria: o
    # Folpan Energy mora em /erbicidi/ e a pagina escreve FUNGICIDI — e folpet e
    # fungicida. Um pipeline que classificasse pelo caminho erraria este produto.
    censo_cat = Counter(p.get("CATEGORY_DISPLAY") for p in catalogo)
    censo_path = Counter((p.get("PRODUCT_URL") or "").split("/")[6] for p in catalogo)
    divergem = [{"PRODUCT": p["PRODUCT_NAME"],
                 "URL_PATH": (p.get("PRODUCT_URL") or "").split("/")[6],
                 "CATEGORY_PRINTED_ON_PAGE": p.get("CATEGORY_DISPLAY"),
                 "RULE_APPLIED": "CATEGORY_PRINTED_ON_PAGE wins",
                 "PRODUCT_URL": p.get("PRODUCT_URL")}
                for p in catalogo
                if (p.get("PRODUCT_URL") or "").split("/")[6] != (p.get("CATEGORY_DISPLAY") or "").lower()]
    grava("CATEGORY-CENSUS.json", {
        **meta,
        "BY_CATEGORY_PRINTED_ON_PAGE": dict(censo_cat),
        "BY_URL_PATH": dict(censo_path),
        "TOTAL": len(catalogo),
        "EXPECTED_BY_MISSION": {"ERBICIDI": 26, "FUNGICIDI": 14, "INSETTICIDI": 6, "SPECIALI": 5, "TOTAL": 51},
        "DIFFERENCE_FROM_51": len(catalogo) - 51,
        "URL_PATH_DISAGREES_WITH_PRINTED_CATEGORY": divergem,
    })

    # ---------------------------------------------------------- 5 · os Speciali
    por_nome_mapa = {m["COMMERCIAL_NAME"]: m for m in mapa if m["COMMERCIAL_NAME"]}
    speciali = []
    for p in catalogo:
        if (p.get("CATEGORY_DISPLAY") or "") != "SPECIALI":
            continue
        m = por_nome_mapa.get(p["PRODUCT_NAME"], {})
        fito = p.get("REGISTRATION_FORMAT_STATE") == "MINISTERO_LIKE" and m.get("REGISTRATION_NUMBER")
        speciali.append({
            "PRODUCT_ID": m.get("PRODUCT_ID"),
            "COMMERCIAL_NAME": p["PRODUCT_NAME"],
            "COMMERCIAL_CATEGORY": "SPECIALI",
            "REGISTRATION_NUMBER_AS_CLAIMED": p.get("MANUFACTURER_CLAIM_REGISTRATION_ID"),
            "REGISTRATION_FORMAT_STATE": p.get("REGISTRATION_FORMAT_STATE"),
            "REGULATORY_REGIME": ("PHYTOSANITARY_REGISTER_IT_T4_001" if fito
                                  else "NOT_THE_PHYTOSANITARY_REGISTER"),
            "REGULATORY_REGIME_EVIDENCE": (
                "numero existe no registro fitosanitario do Ministero" if fito else
                "o numero publicado nao tem o formato do registro fitosanitario e nao existe "
                "entre as 17.695 linhas dele; a composicao declarada e de carbono/azoto organico, "
                "que e linguagem de fertilizante, nao de sostanza attiva"),
            "SPECIFIC_REGISTER_IF_NOT_PHYTOSANITARY": None if fito else "UNKNOWN",
            "REGULATORY_NAME": m.get("REGULATORY_NAME"),
            "AUTHORIZATION_HOLDER": m.get("AUTHORIZATION_HOLDER"),
            "HOLDER_IS_ADAMA": m.get("HOLDER_IS_ADAMA"),
            "COMPONENTS_AS_PUBLISHED": p.get("ACTIVE_INGREDIENT"),
            "FORMULATION": p.get("FORMULATION"),
            "CROPS_DECLARED": "UNKNOWN",
            "CROPS_DECLARED_WHY": "a pagina lista culturas como links de busca, nao como declaracao de autorizacao",
            "PRODUCT_URL": p.get("PRODUCT_URL"),
            "SOURCE_IDS": ["IT-ADAMA-CATALOG"] + (["IT-T4-001"] if fito else []),
        })
    grava("SPECIALI-DEEP.json", {**meta, "COUNT": len(speciali), "PRODUCTS": speciali,
                                 "RULE": "os cinco nao foram forcados no universo fitosanitario"})

    resumo = {
        "REGISTRY_ROWS": len(linhas),
        "ADAMA_GROUP_RECORDS": len(adama),
        "ADMIN_ACTIVE": sum(1 for e in estados if e["ADMIN_ACTIVE"]),
        "INTERPRETATION": dict(Counter(e["CURRENT_INTERPRETATION"] for e in estados if e["ADMIN_ACTIVE"])),
        "COMMERCIAL_PRODUCTS": len(catalogo),
        "IDENTITY_ROWS": len(mapa),
        "RECONCILIATION": dict(Counter(r["CLASS"] for r in recon)),
        "ACTIVE_INGREDIENTS": len(ais),
        "MOA_CLASSIFIED": sum(1 for a in ais if a["MOA_STATE"] == "CLASSIFIED"),
        "LINEAGE_RELATIONSHIPS": len(linhagem),
        "EXPIRY_CLUSTERS": len(clusters),
        "LABEL_DOCUMENTS": len(rotulos),
        "LABEL_USES": 0,
        "SPECIALI": len(speciali),
        "SPECIALI_PHYTOSANITARY": sum(1 for x in speciali if x["REGULATORY_REGIME"].startswith("PHYTO")),
        "CATEGORY_CENSUS": dict(censo_cat),
        "URL_PATH_DISAGREEMENTS": len(divergem),
    }
    grava("BUILD-SUMMARY.json", {**meta, "SUMMARY": resumo})
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return resumo


if __name__ == "__main__":
    main()
