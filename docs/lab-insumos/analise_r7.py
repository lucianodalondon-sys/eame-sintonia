# -*- coding: utf-8 -*-
"""RODADA 7 — crossings (X1-X4 da R6), regras D112, pares por secção, corte vertical mosca-da-oliveira e o que as 38
novas acrescentaram. EXPERIMENTAL / NAO_PARA_CLIENTE. Lê ficheiros; não abre banco.

    python analise_r7.py

REGRAS (as da R6, fixadas antes; mais as D112, verbatim do dono em DECISOES-DONO D112)
  X1  estado do piloto = as chaves EXISTEM em campo (não prova que falem do mesmo facto).
  X2  cultura do READY == cultura no rótulo ADAMA, por FORMA (maiúsculas, sem acento). 'vigneto' ≠ 'VITE': sem sinónimo.
  X3  a cultura que casou é NOMEADA no MESMO troço do boletim em que a substância aparece. Se não, GRAO_INCOMPATIVEL.
  X4  pergunta de rótulo não precisa de tempo; «não» = não encontrado na referência lida (nunca «a ADAMA não tem»).
  D112-1 LOCAL DO FATO só com sustentação explícita: cada nome do fact_location tem de aparecer num trecho «…» da BASE.
         Nome sem trecho que o contenha = LOCAL_NAO_SUSTENTADO (a Intelligence não o usa como REGION).
  D112-2 toda entidade leva a procedência: o READY não tem ENTITY_SOURCE (medido: 0/242). A única procedência por
         entidade que existe é PROBLEMA.SECOES[].PROBLEMAS[].TRECHO (+ ESTADO PRESENTE/CITADA). Por isso:
         cultura/praga do DOCUMENTO = ENTITY_SOURCE NAO SEI; par (cultura, praga) só de uma SECAO com CULTURA ≠ NAO SEI.
  D112-3 evidência insuficiente = NAO SEI.  D112-4 cada objeto separa FONTE (trecho literal) × INTERPRETACAO (regra nossa).
  EXT   o piloto só procura substâncias em fontes IT-T3 (FAMILIAS_AGRO). As 38 novas são CAND-* / IT-T12 / IT-T2 com
        universo T3: corro a mesma pergunta sobre elas como EXTENSAO_DECLARADA (fonte CANDIDATA ≠ fonte registada).
  W*  corte vertical: regras W0-W8 (CAP-WIN-DESENHO-R5.md), N = 30 dias, hoje = 27/09/2026. Par olivo × mosca SÓ por secção.
"""
import collections
import json
import re
import subprocess
import sys
import types
import unicodedata
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
B = AQUI.parent
ANT = B / "EXPD78-R6-20260927T142510Z"
WT = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/int-intake-g0v4-v1")
REPO = Path(r"C:/eame-sintonia")
PILOTO_SHA = "2b4e095f53a331a68ec016b289afca270b004d04"
VIVO = "18461b92dcf576816e45af27586d2d7f783d0a07"      # lote 4: grafo instalado (mesmo blob de eb3a7b1d)
LOTE_NOVO = "LINHA-BUSCA-RAW-20260927T152708"
NS = "NAO SEI"
N_CURRENT = 30
HOJE = date(2026, 9, 27)
C = collections.Counter


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, encoding="utf-8").stdout


def mod(nome, src, extra=None):
    m = types.ModuleType(nome)
    m.__dict__.update(extra or {})
    exec(compile(src, nome, "exec"), m.__dict__)
    return m


piloto = mod("o_piloto_da_sala", git("show", PILOTO_SHA + ":provas/o_piloto_da_sala.py"),
             {"__file__": str(WT / "provas" / "o_piloto_da_sala.py")})
GD = mod("grafo", git("show", VIVO + ":motor/grafo_de_dependencia.py"))
# meses italianos: do DONO (leis/fato_local.py no vivo 18461b92: MESES/MES_NUM), executado do blob, nao copiado
_src = git("show", VIVO + ":leis/fato_local.py")
exec(_src[_src.index("MESES = ("):_src.index("MES_NUM = ")] + "MES_NUM = {m: i + 1 for i, m in enumerate(MESES)}" + chr(10), globals())


def ign(v):
    return v is None or str(v).strip() == "" or str(v).strip().upper().startswith(("NAO SEI", "UNKNOWN", "NOT_KNOWN", "NONE"))


def forma(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def jd(r, k, sub="VALOR"):
    j = r.get("janela_declarada") if isinstance(r.get("janela_declarada"), dict) else {}
    v = j.get(k)
    return v.get(sub) if isinstance(v, dict) else (v if sub == "VALOR" else None)


def lista(v):
    if ign(v):
        return []
    return [x for x in (v if isinstance(v, list) else [v]) if not ign(x)]


def trocos(texto):
    t = unicodedata.normalize("NFKC", texto or "").replace("\r", "")
    partes = re.split(r"(?=Situazione Fenologica:)", t)
    return partes if len(partes) > 1 else re.split(r"\n\s*\n", t)


def local_sustentado(r):
    """D112-1: cada nome do fact_location tem de estar num trecho «…» da BASE."""
    fl = r.get("fact_location")
    if ign(fl):
        return {"FACT_LOCATION": NS, "ESTADO": "NAO_SEI", "SUSTENTADOS": [], "NAO_SUSTENTADOS": []}
    base = unicodedata.normalize("NFKC", str(r.get("fact_location_basis") or ""))
    trechos = " ".join(re.findall(r"«([^»]*)»", base))
    nomes = [n.strip() for n in str(fl).split(";") if n.strip()]
    ok = [n for n in nomes if forma(n) and forma(n) in forma(trechos)]
    nao = [n for n in nomes if n not in ok]
    return {"FACT_LOCATION": fl, "ESTADO": "SUSTENTADO" if not nao else "PARCIAL" if ok else "LOCAL_NAO_SUSTENTADO",
            "SUSTENTADOS": ok, "NAO_SUSTENTADOS": nao, "LOCATION_SOURCE": "TEXT" if ok else "UNRESOLVED"}


def pares_por_secao(r):
    """D112-2: (cultura, praga, estado, trecho) só de secções com cultura nomeada."""
    out = []
    for s in jd(r, "PROBLEMA", "SECOES") or []:
        if not isinstance(s, dict) or ign(s.get("CULTURA")):
            continue
        for p in s.get("PROBLEMAS") or []:
            out.append({"CULTURA": s["CULTURA"], "PRAGA": p.get("NOME"), "ESTADO": p.get("ESTADO"),
                        "TRECHO": p.get("TRECHO"), "ENTITY_SOURCE": "SECTION (trecho do boletim)"})
    return out


def main():
    sala = json.loads((AQUI / "copia" / "SALA_ATUAL.json").read_text(encoding="utf-8"))
    sala_ant = json.loads((ANT / "copia" / "SALA_ATUAL.json").read_text(encoding="utf-8"))
    livro = json.loads(next((AQUI / "saida").glob("LIVRO-IR-*.json")).read_text(encoding="utf-8"))
    RUN = livro["INTELLIGENCE_RUN_ID"]
    lin = {(str(l["ITEM_ID"]), l["CORRIDA_UPSTREAM"]): l for l in livro["LINEAGE"]}
    sk = lambda r: "%s#%s" % (r["run_id"], r["ordem"])
    por_sk = {sk(r): r for r in sala}
    novo = lambda r: r["run_id"] == LOTE_NOVO

    # ── 1 · crossings (X1-X4) + extensão declarada às 38 ────────────────────────────────────
    subs, usos, vivos = piloto.ler_referencia_adama()
    xs_ant = {x["CROSSING_ID"] + "@" + x["SOURCE_ITEM"]["RUN_ID"]: x for x in piloto.cruzar(sala_ant, subs, usos, vivos)}
    xs = [(x, "PILOTO") for x in piloto.cruzar(sala, subs, usos, vivos)]
    fam0 = piloto.FAMILIAS_AGRO
    piloto.FAMILIAS_AGRO = tuple(sorted({r["source_id"] for r in sala if novo(r) and r["universo"] == "T3"}
                                        - {r["source_id"] for r in sala if r["source_id"].startswith(fam0)}))
    ext = [(x, "EXTENSAO_DECLARADA") for x in piloto.cruzar(sala, subs, usos, vivos)]
    piloto.FAMILIAS_AGRO = fam0
    cross = []
    for x, via in xs + ext:
        si = x["SOURCE_ITEM"]
        r = por_sk["%s#%s" % (si["RUN_ID"], si["ORDEM"])]
        culturas = lista(jd(r, "CULTURA"))
        rot = {forma(c) for c in x["ADAMA_CROPS_ON_LABEL"]}
        casam = sorted({c for c in culturas if forma(c) in rot})
        sub = x["ACTIVE_INGREDIENT_OBSERVED"]
        trs = [tr for tr in trocos(r["texto"]) if sub in forma(tr)]
        no_troco = sorted({c for c in casam for tr in trs if re.search(r"(?i)\b%s\w*" % re.escape(c[:5]), tr)})
        # X3w (nova na R7, declarada): um troço do tamanho do documento não prova proximidade. A cultura tem de
        # estar a <= 400 caracteres de uma menção da substância (nome do rótulo, sem separadores). Final exige X3 E X3w.
        tt = unicodedata.normalize("NFKC", r["texto"] or "")
        pad = "[^A-Za-z0-9]{0,2}".join(map(re.escape, sub))
        pos_sub = [m.start() for m in re.finditer("(?i)" + pad, tt)]
        janela = sorted({c for c in casam for q in pos_sub if re.search(r"(?i)%s\w*" % re.escape(c[:5]), tt[max(0, q - 400):q + 400])})
        no_troco = sorted(set(no_troco) & set(janela))
        # X3h (D112 «cabecalho escrito»): boletim DE UMA SO CULTURA, nomeada no cabeçalho (primeiros 200 caracteres) e
        # todas as culturas do READY são essa mesma (mesmo prefixo de 4 letras: vite/vigneto). O cabeçalho vale como
        # âmbito de todo o documento → ENTITY_SOURCE = HEADER.  Senão, só X3 ∧ X3w (ENTITY_SOURCE = SECTION/NEAR).
        cab = forma(tt[:200]).lower()
        unica = {forma(c)[:4] for c in culturas}
        cabecalho = sorted(c for c in casam if len(unica) == 1 and forma(c)[:4].lower() in cab)
        entity_source = "HEADER (boletim de uma cultura)" if cabecalho else "SECTION+NEAR_400" if no_troco else "DOCUMENT (NAO SEI por entidade)"
        no_troco = sorted(set(no_troco) | set(cabecalho))
        if not culturas:
            final = "NOT_POSSIBLE"
        elif not casam:
            final = "POSSIBLE_ANSWER_NO"
        elif not no_troco:
            final = "PARTIAL_GRAO_INCOMPATIVEL"
        else:
            final = "POSSIBLE_ANSWER_YES_A_CONFIRMAR"
        loc = local_sustentado(r)
        oid = x["CROSSING_ID"] + "@" + si["RUN_ID"]
        cross.append({
            "OBJETO_ID": oid, "VIA": via, "NOVO_LOTE": novo(r), "SALA_CHAVE": sk(r), "SOURCE_ID": r["source_id"],
            "RAW_OBSERVATION_ID": r["raw_observation_id"], "URL": r.get("raw_source_url"), "PUBLISHED_AT": r.get("published_at"),
            "SUBSTANCIA": sub, "PRODUTOS_ADAMA": x["ADAMA_PRODUCTS"], "CULTURAS_NO_ROTULO": x["ADAMA_CROPS_ON_LABEL"],
            "ANTES": xs_ant.get(oid, {}).get("CROSSING_STATE", "NAO_EXISTIA"),
            "PILOTO": {"CROSSING_STATE": x["CROSSING_STATE"], "JOIN_KEYS_MISSING": x["JOIN_KEYS_MISSING"]},
            "FONTE": {"CULTURA_NO_READY": culturas, "ENTITY_SOURCE_DA_CULTURA": "DOCUMENT (lista do boletim; NAO SEI por entidade)",
                      "TROCO_COM_A_SUBSTANCIA": [re.sub(r"\s+", " ", t)[:300] for t in trs][:1],
                      "LOCAL": loc},
            "INTERPRETACAO": {"X2_CULTURAS_QUE_CASAM": casam, "X3_NOMEADA_NO_TROCO_E_A_400": no_troco, "X3W_A_400_CARACTERES": janela, "TROCOS_NO_DOCUMENTO": len(trocos(r["texto"])), "MENCOES_DA_SUBSTANCIA": len(pos_sub), "X3H_CABECALHO": cabecalho, "ENTITY_SOURCE_DA_CULTURA": entity_source, "ESTADO": final},
            "ESTADO_R7": final, "NAO_E": ["OPPORTUNITY", "RECOMENDACAO"], "INTELLIGENCE_RUN_ID": RUN})
    resumo_x = {"TOTAL": len(cross), "POR_VIA": dict(C(c["VIA"] for c in cross)),
                "POR_ESTADO": dict(C(c["ESTADO_R7"] for c in cross)),
                "POR_ESTADO_SO_NOVAS": dict(C(c["ESTADO_R7"] for c in cross if c["NOVO_LOTE"])),
                "PILOTO_ESTADO": dict(C(c["PILOTO"]["CROSSING_STATE"] for c in cross)),
                "SUBSTANCIAS": dict(C(c["SUBSTANCIA"] for c in cross))}

    # ── 2 · D112 sobre os 242 ────────────────────────────────────────────────────────────────
    locs = {sk(r): local_sustentado(r) for r in sala}
    d112 = {"ENTITY_SOURCE_NO_READY": sum("ENTITY_SOURCE" in json.dumps(r, ensure_ascii=False) for r in sala),
            "LOCATION_SOURCE_NO_READY": sum("LOCATION_SOURCE" in json.dumps(r, ensure_ascii=False) for r in sala),
            "LOCAL_POR_ESTADO": dict(C(v["ESTADO"] for v in locs.values())),
            "LOCAL_POR_ESTADO_SO_NOVAS": dict(C(locs[sk(r)]["ESTADO"] for r in sala if novo(r))),
            "LOCAL_NAO_SUSTENTADO": [{"SALA_CHAVE": k, "SOURCE_ID": por_sk[k]["source_id"], **v} for k, v in locs.items()
                                     if v["ESTADO"] in ("PARCIAL", "LOCAL_NAO_SUSTENTADO")],
            "ITENS_COM_PARES_POR_SECAO": sum(1 for r in sala if pares_por_secao(r)),
            "PARES_POR_SECAO": sum(len(pares_por_secao(r)) for r in sala)}

    # ── 3 · corte vertical: olivo × mosca-da-oliveira, por SECÇÃO ─────────────────────────
    NEG = re.compile(r"(?i)(non si sono rilevat\w*[^.]{0,40}(raggiungiment|superament)\w*[^.]{0,30}soglia"
                     r"|al di ?sotto delle soglie|non si ritiene giustificat\w* l.esecuzione di un trattamento"
                     r"|non si giustificano interventi|catture ancora limitate|sotto la soglia)")
    POS = re.compile(r"(?i)(superament\w* della soglia[^.]{0,40}(rilevat|riscontrat|registrat)"
                     r"|soglia[^.]{0,30}(superata|raggiunta)|si consiglia di intervenire|e.? necessario intervenire)")
    corte = []
    for r in sala:
        ps = [p for p in pares_por_secao(r) if "oliv" in forma(p["CULTURA"]).lower() and "mosca" in str(p["PRAGA"]).lower()
              and "oliv" in str(p["PRAGA"]).lower()]
        doc_par = bool([c for c in lista(jd(r, "CULTURA")) if "oliv" in c.lower()]) and \
            any("mosca" in p.lower() and "oliv" in p.lower() for p in lista(jd(r, "PROBLEMA")))
        if not (ps or doc_par):
            continue
        l = lin[(str(r["item_id"]), r["run_id"])]
        t = unicodedata.normalize("NFKC", r["texto"] or "")
        ctx = lambda m: re.search(r"(?i)mosca|bactrocera|olive|punture", t[max(0, m.start() - 400):m.end() + 100])
        neg = [re.sub(r"\s+", " ", t[max(0, m.start() - 140):m.end() + 50]) for m in NEG.finditer(t) if ctx(m)]
        COND = re.compile(r"(?i)(nei casi di|in caso di|qualora|laddove|ove si)[^.]{0,160}$")
        pos, cond = [], []
        for m in POS.finditer(t):
            if not re.search(r"(?i)mosca dell.oliv|bactrocera|olive da olio", t[max(0, m.start() - 300):m.end() + 100]):
                continue
            tr = re.sub(r"\s+", " ", t[max(0, m.start() - 140):m.end() + 50])
            (cond if COND.search(t[max(0, m.start() - 170):m.start()]) else pos).append(tr)
        fim = None
        if l["TEMPORAL_STATE"] == "ANCORADO":
            iv = __import__("json").loads(json.dumps(l)).get("FACT_TIME")
            m = re.findall(r"(\d{4})-(\d{2})-(\d{2})", str(r["fact_time"]))
            if m:
                fim = max(date(int(a), int(b), int(c)) for a, b, c in m)
            else:
                mi = re.search(r"(\d{1,2})\s*(?:-|al|/)?\s*(\d{1,2})?\s+([A-Za-z]+)\s+(\d{4})", str(r["fact_time"]))
                if mi and mi.group(3).lower() in MES_NUM:
                    fim = date(int(mi.group(4)), MES_NUM[mi.group(3).lower()], int(mi.group(2) or mi.group(1)))
        aberta = ("NO", "FONTE_DECLARA_SOGLIA_NAO_ATINGIDA") if neg and not pos else \
                 ("CONFLICTING_EVIDENCE", "NEGACAO_E_ACAO_NO_MESMO_DOCUMENTO") if neg and pos else \
                 ("YES_A_CONFIRMAR", "FONTE_RECOMENDA_INTERVIR") if pos else \
                 ("UNKNOWN", "FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE")
        loc = locs[sk(r)]
        corte.append({"SALA_CHAVE": sk(r), "SOURCE_ID": r["source_id"], "NOVO_LOTE": novo(r),
                      "URL": r.get("raw_source_url"), "PUBLISHED_AT": r.get("published_at"),
                      "PAR": "SECAO" if ps else "SO_DOCUMENTO (ENTITY_SOURCE NAO SEI)",
                      "PAR_TRECHO": (ps[0]["TRECHO"][:200] if ps and ps[0].get("TRECHO") else NS),
                      "TEMPO": {"FACT_TIME": r["fact_time"], "TEMPORAL_STATE": l["TEMPORAL_STATE"],
                                "ESTADO": NS if not fim else "CURRENT" if (HOJE - fim).days <= N_CURRENT else "STALE (%d d)" % (HOJE - fim).days},
                      "LOCAL": loc, "ABERTA_AGORA": aberta[0], "METODO": aberta[1], "TRECHO_NEG": neg[:1], "TRECHO_POS": pos[:1], "TRECHO_CONDICIONAL": cond[:1], "LEI_W": "recomendacao condicional (nei casi di accertata presenza...) nao e soglia superada"})
    apoios = [c for c in corte if c["PAR"] == "SECAO" and c["TEMPO"]["ESTADO"] == "CURRENT"
              and c["LOCAL"]["ESTADO"] == "SUSTENTADO" and c["ABERTA_AGORA"] in ("NO", "YES_A_CONFIRMAR")]
    g = GD.grafo([{"ID": c["SALA_CHAVE"], "SOURCE_ID": c["SOURCE_ID"], "URL": c["URL"],
                   "DOCUMENT_ID": por_sk[c["SALA_CHAVE"]].get("raw_document_key"),
                   "SHA256": por_sk[c["SALA_CHAVE"]].get("raw_sha256")} for c in apoios]) if apoios else {}
    por_regiao = collections.defaultdict(list)
    for c in apoios:
        for n in c["LOCAL"]["SUSTENTADOS"]:
            por_regiao[n].append(c["SOURCE_ID"] + ":" + c["ABERTA_AGORA"])
    fora = C()
    for c in corte:
        if c in apoios:
            continue
        for k, ok in (("PAR_SO_DOCUMENTO", c["PAR"] == "SECAO"), ("TEMPO_NAO_CURRENT", c["TEMPO"]["ESTADO"] == "CURRENT"),
                      ("LOCAL_NAO_SUSTENTADO", c["LOCAL"]["ESTADO"] == "SUSTENTADO"),
                      ("SEM_MEDICAO", c["ABERTA_AGORA"] in ("NO", "YES_A_CONFIRMAR"))):
            fora[k] += not ok
    valores = {c["ABERTA_AGORA"] for c in apoios}
    julg = {"PERGUNTA": "olivo x mosca-da-oliveira, setembro 2026: ha janela em que agir faz diferenca AGORA, e onde?",
            "ESTADO_DA_EXECUCAO": "SONDA W0-W8 (nao e CAP-WIN instalada; nao e FINDING)",
            "ITENS_COM_O_PAR": len(corte), "DAS_38_NOVAS": sum(c["NOVO_LOTE"] for c in corte),
            "APOIOS_VALIDOS": [c["SALA_CHAVE"] + " " + c["SOURCE_ID"] + " " + c["ABERTA_AGORA"] for c in apoios],
            "ORIGINADORES_DOS_APOIOS": g.get("INDEPENDENT_SOURCE_COUNT", 0) if g else 0,
            "POR_REGIAO_SUSTENTADA": dict(por_regiao), "PORQUE_FICARAM_FORA": dict(fora),
            "WINDOW_OPEN_NOW": ("NO" if valores == {"NO"} else "CONFLICTING_EVIDENCE" if len(valores) > 1
                                else "YES_A_CONFIRMAR" if valores == {"YES_A_CONFIRMAR"} else NS),
            "ACT_NOW": "NAO", "RESULTADO": "NO_DEFENSIBLE_ACTION_YET"}

    # ── 4 · o que as 38 acrescentaram ──────────────────────────────────────────────────────
    novas = [r for r in sala if novo(r)]
    sig_novos = [s for s in livro["SIGNALS"] if any(l["CORRIDA_UPSTREAM"] == LOTE_NOVO and str(l["ITEM_ID"]) == str(s["ITEM_ID"])
                                                   and l["SOURCE_ID"] == s["SOURCE_ID"] for l in livro["LINEAGE"])]
    acres = {"ITENS": len(novas), "FONTES": len({r["source_id"] for r in novas}),
             "FONTES_CANDIDATAS": len({r["source_id"] for r in novas if r["source_id"].startswith("CAND-")}),
             "UNIVERSO": dict(C(r["universo"] for r in novas)),
             "TEMPORAL_STATE": dict(C(lin[(str(r["item_id"]), r["run_id"])]["TEMPORAL_STATE"] for r in novas)),
             "SINAIS": [{"SOURCE_ID": s["SOURCE_ID"], "FACT_TIME": s["FACT_TIME"], "KIND": s.get("FACT_TIME_KIND"),
                         "IDADE_MIN_DIAS": (s.get("IDADE_NA_CAPTURA") or {}).get("MIN_DIAS"),
                         "LOCAL": s.get("FACT_LOCATION"), "URL": por_sk.get(next((sk(r) for r in novas if str(r["item_id"]) == str(s["ITEM_ID"])), ""), {}).get("raw_source_url")}
                        for s in sig_novos],
             "COM_CULTURA": sum(1 for r in novas if lista(jd(r, "CULTURA"))),
             "COM_PRAGA": sum(1 for r in novas if lista(jd(r, "PROBLEMA"))),
             "COM_PARES_POR_SECAO": sum(1 for r in novas if pares_por_secao(r)),
             "COM_PUBLISHED_AT": sum(1 for r in novas if not ign(r["published_at"])),
             "PUBLICADAS_ANTES_DE_2026": sum(1 for r in novas if not ign(r["published_at"]) and str(r["published_at"])[:4] < "2026"),
             "FORA_DE_ITALIA": [r["source_id"] + " " + str(r["raw_source_url"])[:60] for r in novas
                                if re.search(r"ti\.ch|agrometeo\.ch", str(r["raw_source_url"]))],
             "CROSSINGS": resumo_x["POR_ESTADO_SO_NOVAS"]}

    out = {"MARCA": "EXPERIMENTAL · NAO_PARA_CLIENTE", "INTELLIGENCE_RUN_ID": RUN, "CROSSINGS_RESUMO": resumo_x,
           "CROSSINGS": cross, "D112": d112, "CORTE_VERTICAL": {"ITENS": corte, "JULGAMENTO_DA_SONDA": julg},
           "O_QUE_AS_38_ACRESCENTARAM": acres}
    (AQUI / "ANALISE-R7.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(resumo_x, ensure_ascii=False))
    print(json.dumps({k: v for k, v in d112.items() if k != "LOCAL_NAO_SUSTENTADO"}, ensure_ascii=False))
    for v in d112["LOCAL_NAO_SUSTENTADO"][:12]:
        print("  LOCAL", v["SOURCE_ID"], v["FACT_LOCATION"], "| nao sustentados:", v["NAO_SUSTENTADOS"])
    for c in cross:
        if c["ESTADO_R7"] not in ("NOT_POSSIBLE",):
            print("  X", c["VIA"][:4], c["SOURCE_ID"], c["SUBSTANCIA"], c["ANTES"], "->", c["ESTADO_R7"], c["INTERPRETACAO"]["X2_CULTURAS_QUE_CASAM"],
                  c["INTERPRETACAO"]["X3_NOMEADA_NO_TROCO_E_A_400"], c["INTERPRETACAO"]["ENTITY_SOURCE_DA_CULTURA"][:8], "| cult", c["FONTE"]["CULTURA_NO_READY"][:4])
    for c in corte:
        print("  W", c["SOURCE_ID"], "novo" if c["NOVO_LOTE"] else "", c["PAR"][:6], c["TEMPO"]["ESTADO"], c["LOCAL"]["ESTADO"],
              c["LOCAL"]["SUSTENTADOS"], c["ABERTA_AGORA"], c["METODO"][:40])
    print(json.dumps(julg, ensure_ascii=False, indent=1))
    print(json.dumps(acres, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
