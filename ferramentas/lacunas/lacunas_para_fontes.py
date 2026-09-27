# -*- coding: utf-8 -*-
"""LACUNAS-PARA-FONTES (D87) · para cada lacuna que a Intelligence devolveu a Coleta, fontes e perfis CONCRETOS.

    py ferramentas/lacunas/lacunas_para_fontes.py --propor  --saida=<PROPOSTAS.json>
    py ferramentas/lacunas/lacunas_para_fontes.py --registar --propostas=<PROPOSTAS.json> --fila=<COPIA da fila>

SEM REDE. Tres regras:
  1. A lacuna vem dos livros da Intelligence (rodadas 1 e 2 da EXP-D78), com o ficheiro, o sha256 e o numero.
  2. Nenhum endereco e inventado: cada proposta traz a PROVA_IDENTIDADE — a pagina oficial que liga o perfil
     (bytes guardados no armazem, com sha256) ou o registo de outra missao (ramo:ficheiro) onde o endereco
     esta escrito. O script confirma que o endereco esta mesmo dentro da prova (`prova_contem`).
  3. So se regista o que e NOVO na fila do vivo (chave = URL normalizado da porta). O que ja existe vira
     ponteiro (CAND-id e estado; SOURCE_ID e estado no livro do Curator), nao linha nova.
O registo e numa COPIA da fila (a aplicacao no vivo e do coordenador), pela porta canonica
(`candidatas/fonte_nova.registar`, TIPOS existentes).
"""
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "candidatas"))
import fonte_nova as FN                                               # noqa: E402

INT = Path("C:/Users/London1/sintonia-sala-italia/intelligence-experimental")
R1 = INT / "EXPD78-20260926T093515Z"
R2 = INT / "EXPD78-R2-20260926T135653Z"
DERIV = RAIZ / "data" / "derivados" / "LACUNAS-PARA-FONTES"
QUEM = "LACUNAS-PARA-FONTES (ferramentas/lacunas/lacunas_para_fontes.py)"

# ---------------------------------------------------------------- 1 · as lacunas (dos livros da Intelligence)
LACUNAS = {
    "L1-CULTURA-PRAGA": {
        "LACUNA": "cultura e praga como CAMPO nos boletins T3",
        "FERRAMENTAS": ["Finestre Colturali", "Radar delle Opportunita", "Label Intelligence"],
        "PROVA": [("R1 MEDICAO.json", "PILOTO_CROP.LOST_IN_DERIVATION", 5),
                  ("R1 MEDICAO.json", "CROSSINGS_TENTADOS", 3), ("R1 MEDICAO.json", "CROSSINGS_POSSIVEIS", 0)],
        "O_QUE_A_FONTE_TEM_DE_TRAZER": "aviso de defesa com cultura + praga/doenca + zona + data no mesmo documento",
    },
    "L2-REGIAO": {
        "LACUNA": "regiao do facto: so 3 fontes T3 na Sala; lugar do facto em 19 de 94 itens",
        "FERRAMENTAS": ["Finestre Colturali", "Radar delle Opportunita"],
        "PROVA": [("R2 R1-X-R2-E-FONTES.json", "CLASSES_POR_T.T3.FONTES", 3)],
        "O_QUE_A_FONTE_TEM_DE_TRAZER": "servico/consorcio de uma regiao ou provincia nomeada, com avisos dessa zona",
    },
    "L3-PERIODO": {
        "LACUNA": "periodo/fase: 0 fontes T1 (fenologia) e 1 so T2 (e sem ano)",
        "FERRAMENTAS": ["Finestre Colturali", "Radar Futuro"],
        "PROVA": [("R2 R1-X-R2-E-FONTES.json", "NEVER_SAMPLED contem T1", True),
                  ("R2 LIVRO-IR-7e570c9eff94e402c720.json", "REQUIREMENTS FACT_TIME:SEM_ANO", 3)],
        "O_QUE_A_FONTE_TEM_DE_TRAZER": "boletim datado (com ano) com estadio da cultura ou calendario por zona",
    },
    "L4-PESSOA-CIENCIA": {
        "LACUNA": "pesquisador identificado: 0 fontes T6; 25 das 31 fontes T5 deram zero",
        "FERRAMENTAS": ["Intelligence Scientifica"],
        "PROVA": [("R2 R1-X-R2-E-FONTES.json", "NEVER_SAMPLED contem T6", True),
                  ("R2 R1-X-R2-E-FONTES.json", "CLASSES_POR_T.T5.FONTES", 31)],
        "O_QUE_A_FONTE_TEM_DE_TRAZER": "pesquisador com nome e instituicao a falar de cultura/praga (podcast, video, pagina do grupo)",
    },
    "L5-PESSOA-CAMPO": {
        "LACUNA": "voz de campo (agronomo/tecnico/produtor): 0 fontes T8; as 4 T7 deram zero (paginas institucionais)",
        "FERRAMENTAS": ["Voci dal Campo", "Radar Futuro"],
        "PROVA": [("R2 R1-X-R2-E-FONTES.json", "NEVER_SAMPLED contem T8", True),
                  ("R2 R1-X-R2-E-FONTES.json", "CLASSES_POR_T.T7.FONTES", 4)],
        "O_QUE_A_FONTE_TEM_DE_TRAZER": "video/webinar/post de tecnico com nome, cargo, cultura, lugar e data",
    },
    "L6-SERIE-PRECO": {
        "LACUNA": "serie de preco independente: todo o mercado vem de 1 fonte (myfruit.it: 6 dos 9 sinais)",
        "FERRAMENTAS": ["Polso di Mercato"],
        "PROVA": [("R2 R1-X-R2-E-FONTES.json", "CLASSES_POR_T.T10.FONTES", 1)],
        "O_QUE_A_FONTE_TEM_DE_TRAZER": "cotacao com praca, unidade, periodo e produto (listino, boletim de precos)",
    },
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def medir_lacunas() -> dict:
    """Confere cada numero das lacunas nos proprios livros (se um mudar, o script diz)."""
    med = json.loads((R1 / "saida" / "MEDICAO.json").read_text(encoding="utf-8"))
    r12 = json.loads((R2 / "R1-X-R2-E-FONTES.json").read_text(encoding="utf-8"))
    livro = json.loads((R2 / "saida" / "LIVRO-IR-7e570c9eff94e402c720.json").read_text(encoding="utf-8"))
    fontes_t = Counter(f["T"] for f in r12["FONTES"])
    valores = {
        "PILOTO_CROP.LOST_IN_DERIVATION": med["PILOTO_CROP"].get("LOST_IN_DERIVATION"),
        "CROSSINGS_TENTADOS": med["CROSSINGS_TENTADOS"], "CROSSINGS_POSSIVEIS": med["CROSSINGS_POSSIVEIS"],
        "CLASSES_POR_T.T3.FONTES": fontes_t["T3"], "CLASSES_POR_T.T5.FONTES": fontes_t["T5"],
        "CLASSES_POR_T.T7.FONTES": fontes_t["T7"], "CLASSES_POR_T.T10.FONTES": fontes_t["T10"],
        "NEVER_SAMPLED contem T1": "T1" in r12["NEVER_SAMPLED"], "NEVER_SAMPLED contem T6": "T6" in r12["NEVER_SAMPLED"],
        "NEVER_SAMPLED contem T8": "T8" in r12["NEVER_SAMPLED"],
        "REQUIREMENTS FACT_TIME:SEM_ANO": sum("FACT_TIME:SEM_ANO" in r["MISSING_FACT_OR_KEY"] for r in livro["REQUIREMENTS"]),
    }
    out = {}
    for lid, l in LACUNAS.items():
        prov = []
        for fich, campo, esperado in l["PROVA"]:
            prov.append({"FICHEIRO": fich, "CAMPO": campo, "ESPERADO": esperado, "MEDIDO": valores[campo],
                         "CONFERE": valores[campo] == esperado})
        out[lid] = dict(l, PROVA=prov)
    out["_FICHEIROS"] = {"R1 MEDICAO.json": sha(R1 / "saida" / "MEDICAO.json"),
                         "R2 R1-X-R2-E-FONTES.json": sha(R2 / "R1-X-R2-E-FONTES.json"),
                         "R2 LIVRO-IR-7e570c9eff94e402c720.json": sha(R2 / "saida" / "LIVRO-IR-7e570c9eff94e402c720.json"),
                         "FERRAMENTAS-DO-CASCO.md": sha(Path("C:/Users/London1/auditoria-madrugada/FERRAMENTAS-DO-CASCO.md"))}
    return out


# ---------------------------------------------------------------- 2 · o que ja existe (fila, livro, atlas)
def git_show(ref: str) -> str:
    r = subprocess.run(["git", "-C", str(RAIZ), "show", ref], capture_output=True)
    if r.returncode:
        raise SystemExit("git show falhou: %s" % ref)
    return r.stdout.decode("utf-8")


def indice_do_vivo(fila: Path) -> dict:
    q = json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]
    por_url = {FN.normalizar(c["URL"]): c for c in q}
    casa = fila.resolve().parents[1]          # o livro e o atlas lem-se na MESMA arvore da fila (o vivo)
    if not (casa / "curadoria" / "LIFECYCLE-LEDGER-V1.json").exists():
        casa = RAIZ
    trans = json.loads((casa / "curadoria" / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]
    cand_sid, estado_sid = {}, {}
    for t in trans:
        estado_sid[t["SOURCE_ID"]] = t.get("NEW_STATE")
        if "QUALIFY" in (t.get("REASON") or ""):
            for c in re.findall(r"CAND-\d{4}", t["REASON"]):
                cand_sid[c] = t["SOURCE_ID"]
    atlas = dict(re.findall(r"^#### (IT-T\d+-\d+) · (.+)$",
                            (casa / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md").read_text(encoding="utf-8"), re.M))
    handles = {}
    for c in q:
        h = handle(c["URL"])
        if h:
            handles.setdefault(h, c)
    return {"POR_URL": por_url, "CAND_SID": cand_sid, "ESTADO_SID": estado_sid, "ATLAS": atlas, "N": len(q),
            "HANDLES": handles}


def no_vivo(url: str, ix: dict):
    c = ix["POR_URL"].get(FN.normalizar(url))
    if not c:
        return None
    sid = ix["CAND_SID"].get(c["CANDIDATA_ID"])
    return {"CANDIDATA_ID": c["CANDIDATA_ID"], "ESTADO_NA_FILA": c["ESTADO"], "SOURCE_ID": sid,
            "ESTADO_NO_CURATOR": ix["ESTADO_SID"].get(sid) if sid else None}


def prova_contem(url: str, texto: str) -> bool:
    """O endereco esta mesmo escrito na prova? (com ou sem / final, com &amp; do HTML)"""
    u = url.rstrip("/")
    return u in texto or u.replace("&", "&amp;") in texto or u.replace("/", "\\/") in texto


# ---------------------------------------------------------------- 3 · as propostas
PLATAFORMA = [(r"youtube\.com/", "YOUTUBE"), (r"instagram\.com/", "INSTAGRAM"), (r"linkedin\.com/", "LINKEDIN"),
              (r"facebook\.com/", "FACEBOOK"), (r"(twitter|x)\.com/|t\.me/|tiktok\.com/|spotify\.com/", "OUTRO")]
RUIDO = re.compile(r"(facebook\.com/(profile\.php|people|share)|twitter\.com/home$|instagram\.com/p$|x\.com/i$|"
                   r"t\.me/share$|facebook\.com/[^/]*-\d{9,}$|\.com/(intent|share)$)", re.I)
# X, Telegram e TikTok: sem rota na casa (o QUALIFY trata-os como site e o canario reprova — SEGUIR-PESQUISADORES §5)
SEM_ROTA = re.compile(r"(//(www\.)?(twitter|x)\.com/|t\.me/|tiktok\.com/)", re.I)
# contas de governo/instituicao GERAL (regiao, provincia, CNR, universidade): nao sao do agro nem de campo
GERAL = re.compile(r"(regione|provincia|comune|ProvinciaTrento|info_regionelazio|facebook\.com/unito|CNRsocial|"
                   r"RegioneToscana|RegionedelVeneto|RegioneLazio|PATrento)", re.I)
# fora do foco do casco: animal (D26: veterinaria nao e foco), laticinio, vinagre
FORA_DO_FOCO = re.compile(r"(zootecnic|poultry|ruminant|parmigiano|granapadano|grana ?padano|balsamico|"
                          r"caiagromec|sherwood|foreste ed alberi|avicol|unaitalia)", re.I)
PAGINA_DE_GOVERNO = re.compile(r"^https?://(www\.)?(regione|provincia)\.", re.I)
T_LACUNA = {"T3": ["L1-CULTURA-PRAGA", "L2-REGIAO"], "T1": ["L3-PERIODO"], "T7": ["L5-PESSOA-CAMPO"],
            "T8": ["L5-PESSOA-CAMPO"], "T10": ["L6-SERIE-PRECO"]}
PARA_QUE_T = {
    "T3": "posts/videos do servico com avisos de defesa (cultura + praga + zona + data)",
    "T1": "publicacoes da agencia agricola regional com estadio/calendario das culturas",
    "T7": "tecnicos da organizacao a falar de campo (quem fala, cultura, lugar, data)",
    "T8": "videos/posts de imprensa tecnica com agronomos e produtores identificados",
    "T10": "precos e comentarios de mercado com praca e produto",
}


NOME_PLATAFORMA = {"YOUTUBE": "canal YouTube", "INSTAGRAM": "perfil Instagram", "LINKEDIN": "pagina LinkedIn",
                   "FACEBOOK": "pagina Facebook", "OUTRO": "perfil"}


def handle(u: str) -> tuple:
    """(plataforma, nome da conta) — para achar a mesma conta escrita de outra forma (user/X, @X, c/X)."""
    p = FN.normalizar(u).split("?")[0]
    m = re.match(r"(?:it\.)?(youtube|instagram|linkedin|facebook|twitter|x)\.com/(?:user/|c/|channel/|@|company/|showcase/|school/)?([^/]+)", p)
    return (m.group(1), m.group(2).lower()) if m else None


def plataforma(u: str) -> str:
    return next(t for rx, t in PLATAFORMA if re.search(rx, u, re.I))


def propostas_sociais(ix: dict) -> tuple:
    s = json.loads((DERIV / "SOCIAIS-NO-ARMAZEM.json").read_text(encoding="utf-8"))["POR_FONTE"]
    arm = Path("C:/Users/London1/sintonia-sala-italia/armazem")
    props, fora = {}, Counter()
    for sid, perfis in sorted(s.items()):
        t = sid.split("-")[1]
        for h, (pagina, sha_pag) in sorted(perfis.items()):
            if "youtube.com/watch" in pagina:
                fora["A_PAGINA_E_O_PROPRIO_CANAL (ja e fonte)"] += 1
                continue
            if RUIDO.search(h):
                fora["RUIDO (botao/pagina generica)"] += 1
                continue
            if t not in T_LACUNA:
                fora["FAMILIA_FORA_DAS_LACUNAS (%s)" % t] += 1
                continue
            if SEM_ROTA.search(h):
                fora["SEM_ROTA (X/Telegram/TikTok)"] += 1
                continue
            if GERAL.search(h) or (PAGINA_DE_GOVERNO.search(pagina) and not re.search(r"agri|fito", h, re.I)):
                fora["CONTA_GERAL (regiao/provincia/CNR/universidade)"] += 1
                continue
            if FORA_DO_FOCO.search(h) or FORA_DO_FOCO.search(pagina):
                fora["FORA_DO_FOCO (animal/laticinio/vinagre)"] += 1
                continue
            k = FN.normalizar(h)
            if k in props:
                props[k]["TAMBEM_LIGADO_POR"].append(sid)
                continue
            dono = ix["ATLAS"].get(sid) or "%s (%s)" % (re.sub(r"^https?://(www\.)?", "", pagina).split("/")[0], sid)
            props[k] = {
                "ORIGEM": "SOCIAIS-NO-ARMAZEM", "LACUNAS": T_LACUNA[t], "TIPO": plataforma(h), "PAIS": "IT",
                "NOME": "%s — %s" % (dono, NOME_PLATAFORMA[plataforma(h)]), "URL": h,
                "PROVA_IDENTIDADE": pagina, "PROVA_SHA256": sha_pag,
                "PARA_QUE": "%s: %s. Dono = fonte registada %s (%s)" % (
                    "/".join(LACUNAS[T_LACUNA[t][0]]["FERRAMENTAS"][:2]), PARA_QUE_T[t], sid, t),
                "NOTA": "PROVA_IDENTIDADE=%s (a pagina oficial da fonte %s liga este perfil; sha256 %s dos bytes "
                        "guardados no armazem). PAIS_PROVA=fonte italiana %s registada no atlas." % (pagina, sid, sha_pag[:16], sid),
                "TAMBEM_LIGADO_POR": [], "FONTE_DONA": sid,
            }
    # a prova: o perfil esta nos bytes da pagina? (le-se o ficheiro do armazem pelo sha256 guardado)
    return list(props.values()), dict(fora), arm


def propostas_de_ramos(ix: dict) -> list:
    out = []
    # 3a · 30 consorzi di difesa (Asnacodi) medidos pela P1g e fichados na GAPS-CANDIDATAS (lote 2): nunca registados
    ref = "origin/gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json"
    txt = git_show(ref)
    p1g = git_show("origin/janelas-regioes-v1:curadoria/JANELAS-REGIOES-V1.json")
    for f in json.loads(txt)["FICHAS"]:
        out.append({"ORIGEM": ref, "LACUNAS": ["L1-CULTURA-PRAGA", "L2-REGIAO", "L3-PERIODO"], "TIPO": "ORGANIZACAO",
                    "PAIS": "IT", "NOME": f["NOME"], "URL": f["URL"], "PROVA_IDENTIDADE": ref,
                    "PROVA_TEXTO": p1g if prova_contem(f["URL"], p1g) else txt,
                    "PARA_QUE": "Finestre Colturali/Radar: avisos de defesa datados do consorcio (%s) — cultura + praga + "
                                "zona + data. FALTA_PROVAR: %s" % (f["REGIAO"], f["FALTA_PROVAR"]),
                    "NOTA": "PAIS_PROVA=consorzio di difesa italiano na lista oficial da Asnacodi (asnacodi.it/le-sedi-"
                            "condifesa/). PROVA=%s. Medido pela P1g (JANELAS-REGIOES-V1) e fichado no lote 2 da "
                            "GAPS-CANDIDATAS; nunca registado no vivo." % f["PROVA_JA_EXISTENTE"]})
    # 3b · canais de organizacoes agricolas da YT3 (pagina oficial do dono liga o canal), 10 de 14 fora do vivo
    ref = "origin/canais-pessoas-v1:scripts/canais_pessoas/DECISOES-YT3-V1.json"
    dec = json.loads(git_show(ref))["DECISOES"]
    desc_ref = "origin/canais-pessoas-v1:scripts/canais_pessoas/DESCOBERTA-CANAIS-PESSOAS-V1.json"
    desc = json.loads(git_show(desc_ref))["HOSTS"]
    for d in dec:
        if d["DECISAO"] != "ENTRA":
            continue
        pag = next(((h.get("URL_FINAL") or h.get("URL"), h.get("PAGINA_SHA256")) for h in desc.values()
                    if any(FN.normalizar(a["URL"]) == FN.normalizar(d["URL"]) for a in h.get("ACHADOS") or [])), (None, None))
        # PODCAST nao e TIPO da porta: vai como OUTRO, e o PARA_QUE diz que e podcast
        out.append({"ORIGEM": ref, "LACUNAS": ["L5-PESSOA-CAMPO"], "TIPO": d["TIPO"] if d["TIPO"] in FN.TIPOS else "OUTRO",
                    "PAIS": "IT",
                    "NOME": d["NOME"], "URL": d["URL"], "PROVA_IDENTIDADE": pag[0], "PROVA_SHA256": pag[1],
                    "PROVA_TEXTO": git_show(desc_ref),
                    "PARA_QUE": "Voci dal Campo: %s de %s (%s) com tecnicos e produtores; frequencia NAO_MEDIDA"
                                % ("PODCAST" if d["TIPO"] == "PODCAST" else "videos", d["DONO"], d["TIPO_DE_DONO"]),
                    "NOTA": "PROVA_IDENTIDADE=%s (pagina oficial do dono liga o canal; sha256 %s; YT3 23/09). "
                            "PAIS_PROVA=organizacao italiana (semente IT da fila). Decisao YT3: %s" % (
                                pag[0], (pag[1] or "")[:16], d["PORQUE"])})
    # 3c · os 5 programas de ciencia/midia da research-media-sources-v1 (nao instalados)
    ref = "origin/research-media-sources-v1:research/media-sources-v1/ACHADOS.json"
    txt = git_show(ref)
    for a in json.loads(txt)["ACHADOS"]:
        out.append({"ORIGEM": ref, "LACUNAS": ["L4-PESSOA-CIENCIA"], "TIPO": a["tipo"], "PAIS": a["pais"],
                    "NOME": a["nome"], "URL": a["url"], "PROVA_IDENTIDADE": ref, "PROVA_TEXTO": txt,
                    "PARA_QUE": "Intelligence Scientifica: %s" % a["para_que"],
                    "NOTA": "%s | ONDE_VIU=%s | ROTA_HOJE: podcast/audio sem rota (NOT_IMPLEMENTED, research-media-"
                            "sources-v1)" % (a["nota"], a["onde_viu"])})
    # 3d · as paginas de eventos do CRPV e da ANBI (links nas paginas colhidas na ronda 1 da VOZES)
    ref = "origin/vozes-agronomos-v1:data/derivados/VOZES-AGRONOMOS/PLANO-PROGRAMAS.json"
    txt = git_show(ref)
    for f in json.loads(txt)["FICHAS"]:
        mae = "CAND-0022 (crpv.it)" if "crpv" in f["ALVO"] else "CAND-0266 (anbi.it)"
        out.append({"ORIGEM": ref, "LACUNAS": ["L5-PESSOA-CAMPO"], "TIPO": "ORGANIZACAO", "PAIS": "IT",
                    "NOME": ("CRPV — eventi e webinar" if "crpv" in f["ALVO"] else "ANBI — eventi"), "URL": f["ALVO"],
                    "PROVA_IDENTIDADE": ref, "PROVA_TEXTO": txt,
                    "PARA_QUE": "Voci dal Campo: programas com relatores nomeados — %s" % f["PESSOA"],
                    "NOTA": "PAIS_PROVA=organizacao italiana (%s ja na fila). Pagina de eventos, %s. A leitura "
                            "automatica da NAO SEI a series sem nome (VOZES-LEITURA-HUMANA)." % (mae, f["ORIGEM_DO_LINK"])})
    return out


def ponteiros(ix: dict) -> dict:
    """O que JA existe para cada lacuna e so precisa de reparo/onboarding (nao e linha nova)."""
    por_t = defaultdict(Counter)
    ready = defaultdict(list)
    for sid, est in ix["ESTADO_SID"].items():
        m = re.match(r"IT-(T\d+)-", sid or "")
        if m:
            por_t[m.group(1)][est] += 1
            if est == "READY_FOR_COLLECTION":
                ready[m.group(1)].append("%s %s" % (sid, ix["ATLAS"].get(sid, "")[:60]))
    lote1_ref = "origin/gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE1.json"
    lote1 = [{"CANDIDATA": f["CANDIDATA"], "SOURCE_ID": f["SOURCE_ID"], "NOME": f["NOME"],
              "ESTADO_NO_CURATOR": ix["ESTADO_SID"].get(f["SOURCE_ID"]), "PORQUE": f["PORQUE_NO_ROBO"][:160]}
             for f in json.loads(git_show(lote1_ref))["FICHAS"]]
    t10 = {sid: {"NOME": ix["ATLAS"].get(sid), "ESTADO_NO_CURATOR": ix["ESTADO_SID"].get(sid)}
           for sid in ("IT-T10-001", "IT-T10-002", "IT-T10-009", "IT-T10-010")}
    granaria = {c: no_vivo(u, ix) for c, u in (("CAND-0157", "https://www.granariamilano.org/"),
                                              ("CAND-0499", "https://www.granariamilano.it/listino/listino-bioenergetico-2026-09-08/"))}
    return {"ESTADOS_POR_T": {t: dict(c) for t, c in sorted(por_t.items(), key=lambda x: int(x[0][1:]))},
            "READY_POR_T": {t: v for t, v in ready.items() if t in ("T1", "T3", "T8", "T10")},
            "LOTE1_FITO_AGROMETEO_JA_NO_ROBO": {"REF": lote1_ref, "FICHAS": lote1},
            "T10_JA_REGISTADAS": t10, "GRANARIA_NA_FILA": granaria}


def conferir_nos_bytes(props: list) -> None:
    """Para cada perfil tirado do armazem: abre OUTRA VEZ os bytes da pagina (pelo sha256 guardado, so leitura)
    e confirma que o endereco esta la. Sem isto a prova seria so a palavra do varrimento."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ler_sala as LS
    shas = sorted({p["PROVA_SHA256"] for p in props if p["ORIGEM"] == "SOCIAIS-NO-ARMAZEM"})
    if not shas:
        return
    caminho = {}
    for l in LS.consultar("select sha256, storage_path from public.raw_asset where sha256 in (%s)" %
                          ",".join("'%s'" % x for x in shas if re.fullmatch(r"[0-9a-f]{64}", x))):
        a, b = [x.strip() for x in l.split(LS.SEP)]
        caminho.setdefault(a, b)
    arm = Path("C:/Users/London1/sintonia-sala-italia/armazem")
    for p in props:
        if p["ORIGEM"] != "SOCIAIS-NO-ARMAZEM":
            continue
        f = arm / caminho.get(p["PROVA_SHA256"], "__nada__")
        ok = f.is_file() and sha(f) == p["PROVA_SHA256"] and prova_contem(p["URL"], f.read_text(encoding="utf-8", errors="replace"))
        p["PROVA_CONFERIDA"] = ok
        p["PROVA_FICHEIRO"] = str(caminho.get(p["PROVA_SHA256"]))


def propor(fila: Path, bytes_: bool = True) -> dict:
    ix = indice_do_vivo(fila)
    soc, fora, arm = propostas_sociais(ix)
    todas = soc + propostas_de_ramos(ix)
    feitas, vistas = [], set()
    for p in todas:
        k = FN.normalizar(p["URL"])
        if k in vistas:
            continue
        vistas.add(k)
        texto = p.pop("PROVA_TEXTO", None)
        p["PROVA_CONFERIDA"] = (bool(texto and prova_contem(p["URL"], texto)) if p["ORIGEM"] != "SOCIAIS-NO-ARMAZEM"
                                else None)       # None = so o varrimento; conferir_nos_bytes() abre os bytes
        feitas.append(p)
    if bytes_:
        conferir_nos_bytes(feitas)
    for p in feitas:
        v = no_vivo(p["URL"], ix)
        p["NO_VIVO"] = v
        h = handle(p["URL"])
        outra = None if v else ix["HANDLES"].get(h) if h else None
        if outra:
            p["NO_VIVO"] = {"CANDIDATA_ID": outra["CANDIDATA_ID"], "ESTADO_NA_FILA": outra["ESTADO"],
                            "MESMA_CONTA_ESCRITA_ASSIM": outra["URL"]}
        if FORA_DO_FOCO.search(p["NOME"] + " " + p["URL"]):
            p["ACAO"] = "FORA_DO_FOCO"
        elif v:
            p["ACAO"] = "JA_NA_FILA"
        elif outra:
            p["ACAO"] = "JA_NA_FILA_OUTRA_FORMA"
        else:
            p["ACAO"] = "REGISTAR" if p["PROVA_CONFERIDA"] is True else "SEM_PROVA_NAO_REGISTAR"
    return {"DATASET": "LACUNAS-PARA-FONTES-V1", "REDE": 0, "FILA_LIDA": str(fila), "FILA_SHA256": sha(fila),
            "FILA_TAMANHO": ix["N"], "LACUNAS": medir_lacunas(), "PROPOSTAS": feitas,
            "SOCIAIS_DESCARTADOS": fora, "PONTEIROS": ponteiros(ix),
            "CONTAGEM": {"POR_ACAO": dict(Counter(p["ACAO"] for p in feitas)),
                         "REGISTAR_POR_LACUNA": dict(Counter(l for p in feitas if p["ACAO"] == "REGISTAR" for l in p["LACUNAS"])),
                         "REGISTAR_POR_TIPO": dict(Counter(p["TIPO"] for p in feitas if p["ACAO"] == "REGISTAR"))}}


def registar(propostas: dict, fila: Path, sociais_abertas: bool = False) -> list:
    FN.FILA = fila
    feitas = []
    for p in propostas["PROPOSTAS"]:
        if p["ACAO"] != "REGISTAR":
            continue
        nota = "LACUNAS=%s; %s" % (",".join(p["LACUNAS"]), p["NOTA"])
        onde = p["PROVA_IDENTIDADE"] or p["ORIGEM"]
        linha = FN.registar(p["TIPO"], p["PAIS"], p["NOME"], p["URL"], p["PARA_QUE"], QUEM, onde, nota)
        feitas.append({"CANDIDATA_ID": linha["CANDIDATA_ID"], "TIPO": linha["TIPO"], "URL": linha["URL"],
                       "LACUNAS": p["LACUNAS"]})
    # LinkedIn e Instagram de ORGANIZACAO: como a casa ja faz (D15), POLICY_BLOCK com o trecho dos termos.
    # A D24 abriu so perfis de PESSOA; a D88 abriu contorno TECNICO, nao os termos. Quem abre e o dono:
    # --sociais-abertas deixa-os CANDIDATA (a NOTA ja leva PROVA_IDENTIDADE=, que o guarda D24 aceita).
    if sociais_abertas:
        return feitas
    d = FN.carregar()
    ids = {x["CANDIDATA_ID"] for x in feitas if x["TIPO"] in ("LINKEDIN", "INSTAGRAM")}
    for c in d["CANDIDATAS"]:
        if c["CANDIDATA_ID"] in ids:
            ev = FN.evidencia_da_politica(c["TIPO"])
            if ev:
                c["ESTADO"] = "POLICY_BLOCK"
                c["EVIDENCIA_POLITICA"] = ev
                c["EVIDENCIA"] = FN.texto_da_evidencia(ev)
    FN.gravar(d)
    return feitas


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    if "--propor" in argv:
        fila = Path(arg.get("fila") or RAIZ / "candidatas" / "FONTES-CANDIDATAS.json")
        doc = propor(fila)
        Path(arg["saida"]).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(doc["CONTAGEM"], ensure_ascii=False))
        print("lacunas conferidas:", {k: all(x["CONFERE"] for x in v["PROVA"]) for k, v in doc["LACUNAS"].items() if k[0] == "L"})
        return 0
    if "--registar" in argv:
        fila = Path(arg["fila"])
        # a fila de QUALQUER arvore (este ramo, o vivo) mora em candidatas/FONTES-CANDIDATAS.json: essa nao
        if fila.name == "FONTES-CANDIDATAS.json" and fila.resolve().parent.name == "candidatas":
            print("RECUSADO: so numa COPIA da fila (a aplicacao no vivo e do coordenador)")
            return 2
        doc = json.loads(Path(arg["propostas"]).read_text(encoding="utf-8"))
        r = registar(doc, fila, "--sociais-abertas" in argv)
        print(len(r), "candidatas novas na copia;", dict(Counter(x["TIPO"] for x in r)),
              "ids", r[0]["CANDIDATA_ID"] if r else "-", "..", r[-1]["CANDIDATA_ID"] if r else "-")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
