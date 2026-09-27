# -*- coding: utf-8 -*-
"""PESQUISADORES-CONTEUDO (D92) · 1) OpenAlex: os autores por ORCID e as obras recentes dos prioritarios.

    py ferramentas/seguir_pesquisadores/openalex_conteudo.py --plano  --lista-mestra=<pasta> --pessoas=PESSOAS-ORDENADAS.json --saida=<pasta>
    py ferramentas/seguir_pesquisadores/openalex_conteudo.py --rodada --autorizado --saida=<pasta>
    py ferramentas/seguir_pesquisadores/openalex_conteudo.py --medir  --saida=<pasta> [--t6=UNIDADES-T6.json]
    (--seco --fixtures=<pasta> faz a rodada com respostas inventadas, sem rede)

SO a API publica oficial do OpenAlex (D91: segue os termos da API, nao o robots; sem login). Nenhum
pedido ao ORCID: o ORCID de cada pessoa ja esta nos nossos livros (lista-mestra: busca em lote de 26/09
20:18; PESSOAS-ORDENADAS: o indice).

    A. AUTORES   /authors?filter=orcid:A|B|...   50 ORCID por pedido: instituicao atual, temas, contagens
    B. OBRAS     /works?filter=author.orcid:A|B|...,from_publication_date:<desde>   50 ORCID por pedido,
                 200 obras por pagina, cursor guardado (a rodada seguinte continua onde parou).
                 Registos COMPLETOS (sem `select`): as paginas ficam com o nome `openalex-PESQUISADORES-*.json`,
                 o formato que `coleta/pesquisadores_t6_executor.py` (ramo t6-para-sala-v1) ja le.

Teto: 5 pedidos a api.openalex.org por RODADA (a regra comum; a D90 so pos o ORCID em 24 h). Os pedidos
ficam tambem no contador partilhado (contador.py), para a conta do dia.
O RAW e a resposta tal como veio (bytes com sha256). «Obra com resumo / PDF aberto» mede-se DEPOIS (--medir),
sem tocar no RAW.
"""
import json
import sys
import urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import seguir as S          # noqa: E402
import contador as CT       # noqa: E402

API = "https://api.openalex.org"
POR_PEDIDO = 50
POR_PAGINA = 200
DESDE = "2024-01-01"
MAILTO = "sintonia-eame@example.invalid"      # o mesmo de coleta/corpus_pesquisador.py (polite pool)
SELECT_AUTORES = "id,display_name,orcid,last_known_institutions,affiliations,topics,works_count,cited_by_count,summary_stats"


# ═══════════════════════════════════ quem (sem rede)
def orcids_da_lista_mestra(pasta: Path) -> dict:
    """{ORCID: chave} — so quem a busca deu UM ORCID (dois = ambiguo, nao se usa)."""
    est = json.loads((Path(pasta) / "ESTADO-LISTA-MESTRA.json").read_text(encoding="utf-8"))
    return {v[0]: k for k, v in (est.get("ORCID_ACHADOS") or {}).items() if len(v) == 1}


def orcids_prioritarios(pessoas: list) -> dict:
    return {p["ORCID"][0]: "%s|%s" % (p["NOME"], p.get("UNIVERSIDADE")) for p in pessoas
            if p.get("PRIORIDADE") and len(p.get("ORCID") or []) == 1}


def estado_novo(lista: dict, prio: dict) -> dict:
    autores = sorted(set(lista) | set(prio))
    prios = sorted(prio)
    return {"DATASET": "PESQUISADORES-CONTEUDO-OPENALEX", "DESDE": DESDE,
            "ORIGEM": {o: [x for x, d in (("LISTA-MESTRA", lista), ("PRIORITARIOS", prio)) if o in d] for o in autores},
            "AUTORES": {"LOTES": [autores[i:i + POR_PEDIDO] for i in range(0, len(autores), POR_PEDIDO)], "FEITOS": []},
            "OBRAS": {"GRUPOS": [{"ORCIDS": prios[i:i + POR_PEDIDO], "CURSOR": "*", "PAGINAS": 0, "FIM": False,
                                  "TOTAL_DECLARADO": None} for i in range(0, len(prios), POR_PEDIDO)]},
            "RODADAS": []}


def url_autores(orcids):
    return API + "/authors?" + urllib.parse.urlencode({"filter": "orcid:" + "|".join(orcids), "per-page": POR_PEDIDO,
                                                       "select": SELECT_AUTORES, "mailto": MAILTO})


def url_obras(orcids, cursor, desde=DESDE):
    return API + "/works?" + urllib.parse.urlencode({"filter": "author.orcid:%s,from_publication_date:%s" % ("|".join(orcids), desde),
                                                     "per-page": POR_PAGINA, "cursor": cursor, "mailto": MAILTO})


def valida(b: bytes):
    try:
        d = json.loads(b)
    except (ValueError, TypeError):
        return None
    return d if isinstance(d, dict) and isinstance(d.get("results"), list) and isinstance(d.get("meta"), dict) else None


# ═══════════════════════════════════ a rodada
def rodada(estado: dict, t: "S.Transporte", saida: Path) -> dict:
    n = len(estado["RODADAS"]) + 1
    feito = {"RODADA": n, "AUTORES_LOTES": 0, "OBRAS_PAGINAS": 0, "FICHEIROS": []}
    livre = lambda: t.conta["openalex.org"] < S.TETO       # noqa: E731

    def guardar(nome, b):
        (saida / nome).write_bytes(b)            # a resposta tal como veio (RAW); o sha256 esta no PEDIDOS.json
        feito["FICHEIROS"].append(nome)

    for i, lote in enumerate(estado["AUTORES"]["LOTES"]):
        if i in estado["AUTORES"]["FEITOS"] or not livre():
            continue
        st, b = t.get(url_autores(lote), "autores por ORCID (lote %d, %d)" % (i + 1, len(lote)))
        d = valida(b) if b else None
        if d is None:
            break                                # nao se insiste: fica para a rodada seguinte
        guardar("autores-orcid-c%d-%d.json" % (n, i + 1), b)
        estado["AUTORES"]["FEITOS"].append(i)
        feito["AUTORES_LOTES"] += 1
    for g, grupo in enumerate(estado["OBRAS"]["GRUPOS"]):
        while not grupo["FIM"] and livre():
            st, b = t.get(url_obras(grupo["ORCIDS"], grupo["CURSOR"], estado["DESDE"]),
                          "obras desde %s (grupo %d, pagina %d)" % (estado["DESDE"], g + 1, grupo["PAGINAS"] + 1))
            d = valida(b) if b else None
            if d is None:
                break
            grupo["PAGINAS"] += 1
            guardar("openalex-PESQUISADORES-g%d-p%d.json" % (g + 1, grupo["PAGINAS"]), b)
            grupo["TOTAL_DECLARADO"] = d["meta"].get("count")
            proximo = d["meta"].get("next_cursor")
            grupo["CURSOR"], grupo["FIM"] = proximo, (not proximo or not d["results"])
            feito["OBRAS_PAGINAS"] += 1
    feito["PEDIDOS_OPENALEX"] = t.conta["openalex.org"]
    feito["FALTA"] = {"AUTORES_LOTES": len(estado["AUTORES"]["LOTES"]) - len(estado["AUTORES"]["FEITOS"]),
                      "OBRAS_GRUPOS_POR_ACABAR": sum(1 for x in estado["OBRAS"]["GRUPOS"] if not x["FIM"])}
    estado["RODADAS"].append({k: v for k, v in feito.items() if k != "FICHEIROS"})
    return feito


# ═══════════════════════════════════ a medida (sem rede; o RAW nao se toca)
def _dois_t6(t6: Path):
    if not t6:
        return set()
    d = json.loads(Path(t6).read_text(encoding="utf-8"))
    return {(u.get("DOI") or "").lower() for u in d.get("UNIDADES", []) if u.get("DOI")}


def medir(saida: Path, t6: Path = None) -> dict:
    estado = json.loads((saida / "ESTADO-OPENALEX.json").read_text(encoding="utf-8"))
    autores = {}
    for f in sorted(saida.glob("autores-orcid-*.json")):
        for a in (valida(f.read_bytes()) or {"results": []})["results"]:
            o = (a.get("orcid") or "").rsplit("/", 1)[-1]
            autores.setdefault(o, []).append(a)
    obras = {}
    for f in sorted(saida.glob("openalex-PESQUISADORES-*.json")):
        for w in (valida(f.read_bytes()) or {"results": []})["results"]:
            obras.setdefault((w.get("doi") or w.get("id") or "").lower(), w)
    ja = _dois_t6(t6)
    com_resumo = sum(1 for w in obras.values() if w.get("abstract_inverted_index"))
    pdf = sum(1 for w in obras.values() if ((w.get("best_oa_location") or {}).get("pdf_url")))
    oa = sum(1 for w in obras.values() if ((w.get("open_access") or {}).get("is_oa")))
    pedidos = set(estado["ORIGEM"])
    inst = {}
    for o, lst in autores.items():
        insts = [i.get("display_name") for a in lst for i in (a.get("last_known_institutions") or [])]
        inst[o] = {"NOMES_OPENALEX": [a.get("display_name") for a in lst], "IDS_OPENALEX": len(lst),
                   "INSTITUICAO_ATUAL": insts or "NAO SEI",
                   "TEMAS": [t.get("display_name") for t in (lst[0].get("topics") or [])][:6]}
    return {"AUTORES_PEDIDOS": len(pedidos), "AUTORES_ACHADOS": len(autores),
            "AUTORES_SEM_REGISTO": sorted(pedidos - set(autores)),
            "ORCID_EM_MAIS_DE_UM_ID_OPENALEX": sorted(o for o, l in autores.items() if len(l) > 1),
            "OBRAS_DISTINTAS": len(obras), "COM_RESUMO": com_resumo, "COM_PDF_ABERTO": pdf, "ACESSO_ABERTO": oa,
            "SO_TITULO": sum(1 for w in obras.values() if not w.get("abstract_inverted_index")),
            "JA_NAS_589": sum(1 for k in obras if k.replace("https://doi.org/", "") in {d.replace("https://doi.org/", "") for d in ja}) if ja else "NAO MEDIDO",
            "POR_AUTOR": inst}


# ═══════════════════════════════════ linha de comando
def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    saida = Path(arg["saida"])
    arq = saida / "ESTADO-OPENALEX.json"
    if "--plano" in argv:
        if not arq.exists():
            saida.mkdir(parents=True, exist_ok=True)
            pessoas = json.loads(Path(arg["pessoas"]).read_text(encoding="utf-8"))
            e = estado_novo(orcids_da_lista_mestra(Path(arg["lista-mestra"])), orcids_prioritarios(pessoas["PESSOAS"]))
            arq.write_text(json.dumps(e, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        e = json.loads(arq.read_text(encoding="utf-8"))
        print(json.dumps({"AUTORES": len(e["ORIGEM"]), "LOTES_DE_AUTORES": len(e["AUTORES"]["LOTES"]),
                          "PRIORITARIOS_COM_ORCID": sum(len(g["ORCIDS"]) for g in e["OBRAS"]["GRUPOS"]),
                          "GRUPOS_DE_OBRAS": len(e["OBRAS"]["GRUPOS"]), "DESDE": e["DESDE"],
                          "RODADA_1": "autores %d pedidos + obras %d (1.a pagina de cada grupo) = %d de %d"
                                      % (len(e["AUTORES"]["LOTES"]), min(len(e["OBRAS"]["GRUPOS"]), S.TETO - len(e["AUTORES"]["LOTES"])),
                                         min(S.TETO, len(e["AUTORES"]["LOTES"]) + len(e["OBRAS"]["GRUPOS"])), S.TETO),
                          "PAGINAS_DE_OBRAS": "NAO SEI ate a 1.a pagina (meta.count diz o total de cada grupo)"},
                         ensure_ascii=False, indent=1))
        return 0
    if "--medir" in argv:
        m = medir(saida, Path(arg["t6"]) if "t6" in arg else None)
        (saida / "MEDIDA-OPENALEX.json").write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in m.items() if k != "POR_AUTOR"}, ensure_ascii=False, indent=1))
        return 0
    if "--rodada" not in argv:
        print(__doc__)
        return 2
    estado = json.loads(arq.read_text(encoding="utf-8"))
    if "--seco" in argv:
        resp = json.loads((Path(arg["fixtures"]) / "RESPOSTAS-OPENALEX.json").read_text(encoding="utf-8"))

        def falso(url):
            if url not in resp:
                raise S.urllib.error.HTTPError(url, 404, "sem fixture", {}, None)
            return 200, json.dumps(resp[url]).encode("utf-8")
        t = S.Transporte(saida / ("RODADA-%02d" % (len(estado["RODADAS"]) + 1)), buscar=falso, pausa=0,
                         contador=CT.Contador24h(saida / "CONTADOR-24H.json"))
    else:
        if "--autorizado" not in argv:
            print("RECUSADO: sai a rede; so com --autorizado (quem corre e o coordenador)")
            return 2
        pasta = saida / ("RODADA-%02d" % (len(estado["RODADAS"]) + 1))
        pasta.mkdir(parents=True, exist_ok=True)
        if not S.portao(pasta, "ANTES"):
            print("PAROU: portao de egresso nao e IT (antes)")
            return 3
        t = S.Transporte(pasta, contador=CT.Contador24h(Path(arg.get("contador") or CT.CONTADOR_PADRAO)))
    r = rodada(estado, t, saida)
    arq.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    t.pasta.mkdir(parents=True, exist_ok=True)
    (t.pasta / "PEDIDOS.json").write_text(json.dumps({"PEDIDOS": t.registo, "POR_DOMINIO": dict(t.conta)},
                                                     ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if "--seco" not in argv and not S.portao(t.pasta, "DEPOIS"):
        print("PAROU: portao de egresso nao e IT (depois)")
        return 3
    print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
