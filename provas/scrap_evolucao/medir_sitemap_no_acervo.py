"""FEED-LIGADO (3) · SITEMAP_DECLARADO k/N — quantos robots.txt JA GUARDADOS no acervo declaram `Sitemap:`.

    py provas/scrap_evolucao/medir_sitemap_no_acervo.py [saida.json]

Sem rede. Le os corpos de robots.txt que a casa ja guardou com o SOURCE_ID ao lado:
  curadoria/LIFECYCLE-EVIDENCE-V1.json      PROVAS[].DADOS.ROBOTS   (canario / gate de rota do Curator)
  curadoria/LISTAGENS-PROVADAS-V1.json      RESULTADOS[].ROBOTS     (prova de listagem)
  scripts/detector_capa/MANIFESTO-RECOLHA-V1.json  REGISTO[].ROBOTS (recolha do detector de capa)

Por fonte vale o robots MAIS RECENTE que se leu (um corpo em HTML, vazio ou ausente nao e robots — NAO SEI, e
fica fora do N). As linhas `Sitemap:` leem-se com a mesma regra do coletor
(`coleta/italy_pilot_collect.mjs::sitemapsDoRobots`): comentario fora, `sitemap:` sem olhar a caixa.

    SO MEDE. Nenhuma estrategia nova nasce daqui: declarar SITEMAP como rota exige caso medido (a missao).

⚠️ MEDIDO AO ESCREVER ISTO: os tres livros guardam o robots CORTADO (120, 100 e 120 caracteres). Uma linha
`Sitemap:` depois do corte nao se ve, e o endereco pode vir cortado a meio. Por isso:
  COM_SITEMAP   ha pelo menos uma linha visivel (o endereco pode estar cortado: `CORTADO=true`)
  SEM_SITEMAP   o texto guardado e INTEIRO (mais curto que o corte do livro) e nao tem a linha
  NAO_SEI       o texto chegou ao corte e nao mostra a linha — pode estar depois
O k/N e sobre as fontes com resposta (COM + SEM); o NAO_SEI sai ao lado, e nao entra em nenhum dos dois.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AQUI = os.path.dirname(os.path.abspath(__file__))
LIVROS = (   # (ficheiro, chave, robots, quando, corte medido do texto guardado)
    ("curadoria/LIFECYCLE-EVIDENCE-V1.json", "PROVAS", lambda x: (x.get("DADOS") or {}).get("ROBOTS"),
     lambda x: x.get("OBSERVED_AT"), 120),
    ("curadoria/LISTAGENS-PROVADAS-V1.json", "RESULTADOS", lambda x: x.get("ROBOTS"), lambda x: x.get("PROVADO_EM"), 100),
    ("scripts/detector_capa/MANIFESTO-RECOLHA-V1.json", "REGISTO", lambda x: x.get("ROBOTS"), lambda x: None, 120),
)
FEED_LIGADO = ("IT-T10-022", "IT-T12-117", "IT-T12-137", "IT-T5-090", "IT-T5-186", "IT-T7-021", "IT-T7-033",
               "IT-T7-042", "IT-T7-049", "IT-T7-125", "IT-T7-139", "IT-T9-009", "IT-T9-021")


def sitemaps(txt: str) -> list:
    fora = []
    for bruta in re.split(r"\r\n|\r|\n", txt or ""):
        m = re.match(r"^sitemap\s*:\s*(\S+)$", re.sub(r"#.*$", "", bruta).strip(), re.I)
        if m and m.group(1) not in fora:
            fora.append(m.group(1))
    return fora


def e_robots(txt) -> bool:
    """So e robots o texto com pelo menos uma directiva. MEDIDO: o campo ROBOTS dos livros tambem guarda as
    MENSAGENS da casa (313× «robots inacessivel apos 2 tentativas…», 102× «HTTP 404 — o host nao publica
    robots.txt») e paginas HTML — nenhuma delas e o ficheiro, e nenhuma entra no N."""
    if not isinstance(txt, str) or not txt.strip() or txt.lstrip().startswith("<"):
        return False
    return re.search(r"^\s*(user-agent|disallow|allow|sitemap|crawl-delay)\s*:", txt, re.I | re.M) is not None


def medir(raiz=RAIZ) -> dict:
    por_fonte, ilegiveis = {}, set()
    for rel, chave, ler, quando, corte in LIVROS:
        with open(os.path.join(raiz, rel), encoding="utf-8") as f:
            linhas = json.load(f).get(chave) or []
        for i, x in enumerate(linhas):
            sid, txt = x.get("SOURCE_ID"), ler(x)
            if not sid or txt is None:
                continue
            if not e_robots(txt):
                ilegiveis.add(sid)
                continue
            q = (quando(x) or "", rel, i)
            if sid not in por_fonte or q > por_fonte[sid]["_Q"]:
                sm, cortado = sitemaps(txt), len(txt) >= corte
                estado = "COM_SITEMAP" if sm else "NAO_SEI" if cortado else "SEM_SITEMAP"
                por_fonte[sid] = {"_Q": q, "LIVRO": rel, "ESTADO": estado, "SITEMAPS": sm, "CORTADO": cortado}
    com = sorted(s for s, v in por_fonte.items() if v["ESTADO"] == "COM_SITEMAP")
    sem = sorted(s for s, v in por_fonte.items() if v["ESTADO"] == "SEM_SITEMAP")
    nao_sei = sorted(s for s, v in por_fonte.items() if v["ESTADO"] == "NAO_SEI")
    feed = {s: ({"ESTADO": por_fonte[s]["ESTADO"], "SITEMAPS": por_fonte[s]["SITEMAPS"]} if s in por_fonte
                else {"ESTADO": "NAO_SEI", "PORQUE": "nenhum robots legivel guardado"}) for s in FEED_LIGADO}
    return {
        "O_QUE_MEDE": "fontes cujo robots.txt guardado no acervo declara pelo menos uma linha Sitemap:",
        "SITEMAP_DECLARADO": f"{len(com)}/{len(com) + len(sem)}",
        "K": len(com), "N": len(com) + len(sem), "NAO_SEI_TEXTO_CORTADO": len(nao_sei),
        "FONTES_COM_ROBOTS_LEGIVEL": len(por_fonte),
        "CORTE_DOS_LIVROS": {l[0]: l[4] for l in LIVROS},
        "FORA_DO_N_SEM_ROBOTS_GUARDADO": sorted(ilegiveis - set(por_fonte)),
        "LIVROS": [l[0] for l in LIVROS],
        "NAS_13_DO_FEED": feed,
        "POR_FONTE": {s: {k: v[k] for k in ("LIVRO", "ESTADO", "SITEMAPS", "CORTADO")} for s, v in sorted(por_fonte.items())},
        "NAO_E": "estrategia: nenhum pedido sai por causa destas linhas (a coleta so as GUARDA no resumo da corrida)",
    }


if __name__ == "__main__":
    r = medir()
    saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "SITEMAP-NO-ACERVO.json")
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    print("SITEMAP_DECLARADO", r["SITEMAP_DECLARADO"], "->", saida)
    print("NAO SEI (texto cortado):", r["NAO_SEI_TEXTO_CORTADO"])
    e = [v["ESTADO"] for v in r["NAS_13_DO_FEED"].values()]
    print("nas 13 do feed:", {k: e.count(k) for k in sorted(set(e))})
