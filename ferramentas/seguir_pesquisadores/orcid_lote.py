# -*- coding: utf-8 -*-
"""SEGUIR-PESQUISADORES refeito pela D90 §3.4: o ORCID em LOTE, <= 5 pedidos a orcid.org por 24 h.

As 16 rodadas x 5 pedidos da 1.a versao (seguir.py --rodada) nao cabem num dia. Agora:

    1. CANARIO (um dia, <= 5 pedidos a orcid.org, contando o robots): prova o FORMATO real de
         a) researcher-urls de UMA pessoa         (a seccao minima, por pessoa)
         b) expanded-search de 20 pessoas         (a busca em lote, como coleta/lista_mestra_mur.py)
         c) csv-search de 20 pessoas com a coluna researcher-urls   (⚠️ NAO SEI se o ORCID aceita a coluna)
       Nenhuma resposta real destas buscas foi gravada nesta casa: o canario e que diz o MODO.
         LOTE_COM_LINKS  c) traz os links  -> 20 pessoas por pedido, 5 pedidos por dia = 100 pessoas/dia
         POR_PESSOA      c) nao traz       -> links 1 pessoa por pedido (~5 pessoas/dia); o lote b) serve
                                              para achar o ORCID de quem nao o tem (20 por pedido)
         PARADO          a) nem b) tem o formato esperado -> nao se continua sem olhar
    2. DIA (um por dia): identidade em lote -> links -> paginas das universidades/casas. O que nao cabe
       fica PENDENTE com ADIADO_ATE. Nada se pede duas vezes.

    py ferramentas/seguir_pesquisadores/orcid_lote.py --plano   --pessoas=PESSOAS-ORDENADAS.json --fora=FORA-DO-MUR.json --saida=<pasta>
    py ferramentas/seguir_pesquisadores/orcid_lote.py --canario --autorizado --saida=<pasta>
    py ferramentas/seguir_pesquisadores/orcid_lote.py --dia     --autorizado --saida=<pasta>
    py ferramentas/seguir_pesquisadores/orcid_lote.py --candidatar --saida=<pasta> --fila=<COPIA da fila>
    (--seco --fixtures=<pasta> [--agora=ISO] faz o canario/dia com respostas inventadas, sem rede)

Os mesmos limites da seguir.py (robots, 3 s, portao IT antes/depois, bytes com sha256 fora do Git,
LinkedIn /in/ fora, nunca e-mail/contactos) e o contador de 24 h partilhado (contador.py).
"""
import csv
import io
import json
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import seguir as S          # noqa: E402
import pessoas as PE        # noqa: E402
import contador as CT       # noqa: E402

ORCID = "https://pub.orcid.org/v3.0"
BUSCA = ORCID + "/expanded-search/"
CSV = ORCID + "/csv-search/"
POR_PEDIDO = 20
CSV_FL = "orcid,given-names,family-name,current-institution-affiliation-name,researcher-urls"
PAGINAS_POR_PESSOA = 2
# a casa fora do MUR como o ORCID a escreve (nome da instituicao; ingles e italiano)
CASA_RX = {"FEM": r"edmund mach|fmach", "CREA": r"consiglio per la ricerca in agricoltura|council for agricultural research|\bcrea\b",
           "CNR": r"consiglio nazionale delle ricerche|national research council|\bcnr\b"}


# ═══════════════════════════════════ quem (sem rede)
def _nome_fora(nome: str):
    t = nome.split()
    return (t[-1], t[0]) if len(t) >= 2 else (nome, "")


def juntar(mur: list, fora: list, so_casco: bool = True) -> list:
    """MUR (prioridade) + FEM/CREA/CNR do FORA-DO-MUR, sem repetir o mesmo ORCID, pela ordem de interesse."""
    out, vistos = [], set()
    for p in mur:
        if not p.get("PRIORIDADE") or p.get("LIGACAO_T6") not in ("NOME+UNIVERSIDADE", "RESOLVIDO"):
            continue
        sob, nom = PE.partir_nome_mur(p["NOME"])
        out.append({"CHAVE": "MUR|%s|%s" % (p["NOME"], p.get("UNIVERSIDADE")), "NOME": p["NOME"],
                    "SOBRENOME": sob, "NOME_PROPRIO": nom, "ONDE": p.get("UNIVERSIDADE"), "TIPO_ONDE": "UNIVERSIDADE",
                    "ORCID": list(p.get("ORCID") or []), "ORIGEM": "MUR",
                    "PRIORIDADE": [1, p.get("PAR_DO_CASCO_RECENTE") or 0, p.get("OBRAS_T6") or 0]})
    for p in fora:
        casas = sorted({c.split("/")[0] for c in p.get("CASAS") or []} & set(CASA_RX))
        if not casas or (so_casco and not (p.get("PAR_DO_CASCO_RECENTE") or p.get("PEDIDA_PELO_NOME"))):
            continue
        sob, nom = _nome_fora(p["NOME"])
        out.append({"CHAVE": "OA|%s" % p.get("OPENALEX_ID"), "NOME": p["NOME"], "SOBRENOME": PE.chave(sob),
                    "NOME_PROPRIO": PE.chave(nom), "ONDE": casas, "TIPO_ONDE": "CASA", "ORCID": list(p.get("ORCID") or []),
                    "ORIGEM": "FORA-DO-MUR",
                    "PRIORIDADE": [2 if p.get("PEDIDA_PELO_NOME") else 0, p.get("PAR_DO_CASCO_RECENTE") or 0,
                                   p.get("OBRAS_T6") or 0]})
    out.sort(key=lambda x: [-v for v in x["PRIORIDADE"]])
    final = []
    for x in out:
        if len(x["ORCID"]) == 1 and x["ORCID"][0] in vistos:
            continue
        vistos.update(x["ORCID"])
        final.append(x)
    return final


def estado_novo(pessoas: list) -> dict:
    for p in pessoas:
        n = len(p["ORCID"])
        p["FASE"] = "LINKS" if n == 1 else "IDENTIDADE" if n == 0 else "AMBIGUO"
        p["LINKS"], p["PAGINAS"], p["CANAIS"], p["NAO_ENTRAM"], p["PASSOS"] = None, [], [], [], []
    return {"DATASET": "ORCID-LOTE", "PESSOAS": pessoas, "CANARIO": None, "DIAS": []}


def plano(estado: dict) -> dict:
    """Quantos dias, nos dois modos que o canario pode dar. Conta como se toda a identidade achasse ORCID
    (o pior caso para os dias)."""
    ps = estado["PESSOAS"]
    n = {f: sum(1 for p in ps if p["FASE"] == f) for f in ("LINKS", "IDENTIDADE", "AMBIGUO", "PAGINAS", "FEITO")}
    teto = CT.TETO_24H["orcid.org"]
    lotes_id = -(-n["IDENTIDADE"] // POR_PEDIDO)
    ped_lote = lotes_id + -(-(n["LINKS"] + n["IDENTIDADE"]) // POR_PEDIDO)
    ped_pessoa = lotes_id + n["LINKS"] + n["IDENTIDADE"]
    return {"PESSOAS": len(ps), "POR_FASE": n, "PEDIDOS_ORCID_POR_24H": teto,
            "SE_LOTE_COM_LINKS": {"PEDIDOS_ORCID": ped_lote, "DIAS": 1 + -(-ped_lote // teto)},
            "SE_POR_PESSOA": {"PEDIDOS_ORCID": ped_pessoa, "DIAS": 1 + -(-ped_pessoa // teto)},
            "NOTA": "1 dia de canario + os dias de busca. O robots de orcid.org le-se 1 vez por 24 h e fica guardado no "
                    "contador. As paginas declaradas correm nos mesmos dias, noutros dominios, 5 por dominio por 24 h."}


# ═══════════════════════════════════ os pedidos
def url_links(oid):
    return S.ORCID_URLS % oid


def q_por_orcid(ps):
    return " OR ".join("orcid:%s" % p["ORCID"][0] for p in ps)


def q_por_nome(ps):
    return " OR ".join('(family-name:"%s" AND given-names:"%s")' % (p["SOBRENOME"].title(), p["NOME_PROPRIO"].split()[0].title())
                       for p in ps if p["NOME_PROPRIO"])


def url_busca(q):
    return BUSCA + "?" + urllib.parse.urlencode({"q": q, "rows": 200})


def url_csv(q):
    return CSV + "?" + urllib.parse.urlencode({"q": q, "fl": CSV_FL, "rows": 200})


def ler_links(b: bytes):
    """researcher-urls -> lista de URLs, ou None se o formato nao e o esperado."""
    try:
        d = json.loads(b)
    except ValueError:
        return None
    if not isinstance(d, dict) or "researcher-url" not in d:
        return None
    return [((u.get("url") or {}).get("value") or "").strip() for u in (d.get("researcher-url") or []) if u]


def ler_busca(b: bytes):
    try:
        d = json.loads(b)
    except ValueError:
        return None
    if not isinstance(d, dict) or "expanded-result" not in d:
        return None
    return d.get("expanded-result") or []


def ler_csv(b: bytes):
    """-> {orcid: [links]} se houver coluna de researcher-urls; {} se a coluna nao veio; None se nao e CSV."""
    try:
        linhas = list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    except Exception:                                                     # noqa: BLE001
        return None
    if not linhas:
        return {}
    col_url = next((k for k in linhas[0] if k and "researcher" in k.lower()), None)
    col_id = next((k for k in linhas[0] if k and k.lower() in ("orcid", "orcid-id", "orcid_id")), None)
    if not col_url or not col_id:
        return {}
    return {r[col_id].strip().split("/")[-1]: [u for u in re.split(r"[\s,;|]+", r[col_url] or "") if u.startswith("http")]
            for r in linhas}


def casa_bate(p: dict, instituicoes: list) -> bool:
    if p["TIPO_ONDE"] == "UNIVERSIDADE":
        return PE.mesma_universidade(p["ONDE"], set(instituicoes))
    return any(re.search(CASA_RX[c], PE.chave(i)) for c in p["ONDE"] for i in instituicoes)


# ═══════════════════════════════════ aplicar respostas ao estado
def _anotar(p, url, prova, origem):
    plat, tipo, entra = S.classificar(url)
    k = url.rstrip("/").lower()
    if any(x["URL"].rstrip("/").lower() == k for x in p["CANAIS"] + p["NAO_ENTRAM"]) or k in [x.lower() for x in p["PAGINAS"]]:
        return plat
    if plat == "PAGINA_INSTITUCIONAL_OU_PESSOAL" and origem.startswith(ORCID):
        if len(p["PAGINAS"]) < PAGINAS_POR_PESSOA:
            p["PAGINAS"].append(url)                 # a pagina declarada abre-se depois, noutro dominio
        return plat
    if plat in ("ORCID", "GOOGLE_SCHOLAR", "PAGINA_INSTITUCIONAL_OU_PESSOAL"):
        return plat
    (p["CANAIS"] if entra else p["NAO_ENTRAM"]).append({"URL": url, "PLATAFORMA": plat, "TIPO": tipo, "PROVA": prova,
                                                        "VISTO_EM": origem})
    return plat


def aplicar_links(p, urls, origem):
    p["LINKS"] = [u for u in urls if u]
    p["PASSOS"].append("ORCID %s: %d link(s) declarados pela pessoa" % (p["ORCID"][0], len(p["LINKS"])))
    for u in p["LINKS"]:
        _anotar(p, u, "ORCID_RESEARCHER_URLS (declarado pela propria pessoa)", origem)
    p["FASE"] = "PAGINAS" if p["PAGINAS"] else "FEITO"


def aplicar_identidade(grupo, resultados, origem):
    for p in grupo:
        bate = sorted({r.get("orcid-id") for r in resultados
                       if PE.casa_nome(p["SOBRENOME"], p["NOME_PROPRIO"],
                                       {"%s %s" % (r.get("given-names") or "", r.get("family-names") or "")})
                       and casa_bate(p, r.get("institution-name") or [])} - {None})
        if len(bate) == 1:
            p["ORCID"], p["FASE"] = bate, "LINKS"
            p["PASSOS"].append("ORCID achado em lote (nome + %s): %s" % (p["TIPO_ONDE"].lower(), bate[0]))
        else:
            p["FASE"] = "AMBIGUO" if bate else "SEM_ORCID"
            p["PASSOS"].append("busca em lote: %s" % ("%d ORCID possiveis — nao se funde" % len(bate) if bate
                                                        else "nenhum ORCID com nome + %s" % p["TIPO_ONDE"].lower()))
        p["IDENTIDADE_PROVA"] = origem


# ═══════════════════════════════════ canario e dia
def canario(estado: dict, t: "S.Transporte") -> dict:
    fila = [p for p in estado["PESSOAS"] if p["FASE"] == "LINKS"]
    if not fila:
        return {"MODO": "PARADO", "PORQUE": "ninguem com ORCID unico"}
    um, lote = fila[0], fila[:POR_PEDIDO]
    c = {"EM": CT._iso(t.contador._agora()) if t.contador is not None else datetime.now(timezone.utc).isoformat(timespec="seconds"), "PESSOA_A": um["NOME"], "LOTE_N": len(lote)}
    st, b = t.get(url_links(um["ORCID"][0]), "canario a) researcher-urls")
    urls = ler_links(b) if b else None
    c["A_POR_PESSOA"] = {"HTTP": st, "FORMATO_OK": urls is not None}
    if urls is not None:
        aplicar_links(um, urls, url_links(um["ORCID"][0]))
    st, b = t.get(url_busca(q_por_orcid(lote)), "canario b) expanded-search em lote")
    res = ler_busca(b) if b else None
    c["B_LOTE_BUSCA"] = {"HTTP": st, "FORMATO_OK": res is not None, "DEVOLVIDOS": None if res is None else len(res),
                         "CAMPOS": sorted({k for r in (res or []) for k in r})}
    st, b = t.get(url_csv(q_por_orcid(lote)), "canario c) csv-search com researcher-urls")
    cs = ler_csv(b) if (b and st == 200) else None
    traz = cs is not None and len(cs) > 0
    c["C_LOTE_CSV"] = {"HTTP": st, "TRAZ_LINKS": "SIM" if traz else ("NAO" if st in (200, 400) else "NAO_SEI")}
    proibidos = [x for x in t.registo if x["RESULTADO"] == "ROBOTS_OU_NAO_LIDO" and "orcid.org" in x["URL"]]
    if len(proibidos) == 3:
        rb = t.contador.robots_de("https://pub.orcid.org") if t.contador is not None else None
        c["MODO"] = "PARADO"
        c["PORQUE"] = ("ROBOTS: o robots.txt de pub.orcid.org nao deixa pedir nenhum dos 3 enderecos (%s). A regra da casa "
                       "(D34/D39) respeita o robots; seguir sem ele e decisao do coordenador/dono, nao desta ferramenta"
                       % (repr(rb[1]) if rb else "robots nao lido"))
        c["PEDIDOS_ORCID"] = t.conta.get("orcid.org", 0)
        return c
    if traz:
        c["MODO"] = "LOTE_COM_LINKS"
    elif c["A_POR_PESSOA"]["FORMATO_OK"]:
        c["MODO"] = "POR_PESSOA"
    else:
        c["MODO"] = "PARADO"
    c["PEDIDOS_ORCID"] = t.conta.get("orcid.org", 0)
    return c


def dia(estado: dict, t: "S.Transporte") -> dict:
    modo, feito = estado["CANARIO"]["MODO"], {"IDENTIDADE": 0, "LINKS": 0, "PAGINAS": 0, "PENDENTES": 0}
    livre = lambda d: t.contador.livres(d) > 0 and t.conta[d] < S.TETO      # noqa: E731
    ps = estado["PESSOAS"]
    # 1) identidade em lote (quem nao tem ORCID), 20 por pedido
    grupo = [p for p in ps if p["FASE"] == "IDENTIDADE"][:POR_PEDIDO]
    if grupo and livre("orcid.org"):
        u = url_busca(q_por_nome(grupo))
        st, b = t.get(u, "identidade em lote (%d)" % len(grupo))
        res = ler_busca(b) if b else None
        if res is not None:
            aplicar_identidade(grupo, res, u)
            feito["IDENTIDADE"] += len(grupo)
    # 2) os links: 20 por pedido (LOTE_COM_LINKS) ou 1 por pedido (POR_PESSOA)
    while livre("orcid.org"):
        fila = [p for p in ps if p["FASE"] == "LINKS"]
        if not fila:
            break
        if modo == "LOTE_COM_LINKS":
            g = fila[:POR_PEDIDO]
            u = url_csv(q_por_orcid(g))
            st, b = t.get(u, "links em lote (%d)" % len(g))
            cs = ler_csv(b) if b else None
            if cs is None:
                break
            for p in g:
                aplicar_links(p, cs.get(p["ORCID"][0], []), u)
                feito["LINKS"] += 1
        else:
            p = fila[0]
            u = url_links(p["ORCID"][0])
            st, b = t.get(u, "researcher-urls de %s" % p["NOME"])
            urls = ler_links(b) if b else None
            if urls is None:
                if t.registo and t.registo[-1]["RESULTADO"] in S.TETOS:
                    break
                p["FASE"] = "SEM_RESPOSTA"
                p["PASSOS"].append("ORCID %s: sem resposta legivel (HTTP %s)" % (p["ORCID"][0], st))
                continue
            aplicar_links(p, urls, u)
            feito["LINKS"] += 1
    # 3) as paginas declaradas (universidades/casas), 5 por dominio por 24 h: espalham-se pelos dias
    for p in [p for p in ps if p["FASE"] == "PAGINAS"]:
        abertas = p.setdefault("PAGINAS_LIDAS", [])
        for pg in [x for x in p["PAGINAS"] if x not in abertas]:
            if not livre(S.dominio(pg)):
                continue
            st, b = t.get(pg, "pagina declarada por %s" % p["NOME"])
            if b is None and t.registo and t.registo[-1]["RESULTADO"] in S.TETOS:
                continue
            abertas.append(pg)
            if b is None:
                p["PASSOS"].append("pagina %s: nao aberta (%s)" % (pg, st))
                continue
            for l in S.links_da_pagina(b.decode("utf-8", "replace"), pg):
                _anotar(p, l, "LIGADO NA PAGINA que a pessoa declarou no ORCID", pg)
            feito["PAGINAS"] += 1
        if len(abertas) >= len(p["PAGINAS"]):
            p["FASE"] = "FEITO"
    feito["PENDENTES"] = sum(1 for p in ps if p["FASE"] in ("LINKS", "IDENTIDADE", "PAGINAS"))
    # quando o proximo --dia tem pedido livre a orcid.org (so se ainda ha quem espere pelo ORCID)
    espera = any(p["FASE"] in ("LINKS", "IDENTIDADE") for p in ps)
    feito["PROXIMO_DIA_A_PARTIR_DE"] = t.contador.proximo_livre("orcid.org") if espera else None
    return feito


# ═══════════════════════════════════ candidatas (numa COPIA da fila)
def candidatar(estado: dict, fila: Path) -> dict:
    sys.path.insert(0, str(S.RAIZ / "candidatas"))
    import fonte_nova as FN
    FN.FILA = fila
    feitas, fora = [], []
    for p in estado["PESSOAS"]:
        for c in p["CANAIS"]:
            onde = p["ONDE"] if isinstance(p["ONDE"], str) else "/".join(p["ONDE"])
            para = ("D85: canal publico onde o pesquisador %s (%s) publica — %s; conhecimento/sinal precoce para "
                    "Intelligence Scientifica e Voci dal Campo" % (p["NOME"], onde, c["PLATAFORMA"]))
            nota = ("PESSOA=%s; IDENTIDADE=%s; ORCID=%s; PROVA=%s; VISTO_EM=%s; PAIS_PROVA=instituicao italiana da pessoa "
                    "(%s), nao o lugar do facto; ROTA_HOJE=%s" % (p["NOME"], p["ORIGEM"], ",".join(p["ORCID"]), c["PROVA"],
                                                                  c["VISTO_EM"], onde, S.ROTA_HOJE.get(c["PLATAFORMA"], "NAO SEI")))
            linha = FN.registar(c["TIPO"], "IT", "%s — %s" % (p["NOME"], c["PLATAFORMA"]), c["URL"], para,
                                "SEGUIR-PESQUISADORES/ORCID-LOTE (ferramentas/seguir_pesquisadores/orcid_lote.py)",
                                c["VISTO_EM"], nota)
            feitas.append({"CANDIDATA_ID": linha["CANDIDATA_ID"], "TIPO": linha["TIPO"], "URL": linha["URL"]})
        fora += [dict(x, PESSOA=p["NOME"]) for x in p["NAO_ENTRAM"]]
    return {"CANDIDATAS": feitas, "NAO_ENTRAM": fora}


# ═══════════════════════════════════ linha de comando
def _ler(caminho):
    d = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return d["PESSOAS"] if isinstance(d, dict) else d


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    saida = Path(arg["saida"])
    arq = saida / "ESTADO-ORCID.json"
    if "--plano" in argv:
        if not arq.exists():
            saida.mkdir(parents=True, exist_ok=True)
            e = estado_novo(juntar(_ler(arg["pessoas"]) if "pessoas" in arg else [],
                                   _ler(arg["fora"]) if "fora" in arg else [], "--todos" not in argv))
            arq.write_text(json.dumps(e, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(plano(json.loads(arq.read_text(encoding="utf-8"))), ensure_ascii=False, indent=1))
        return 0
    estado = json.loads(arq.read_text(encoding="utf-8"))
    if "--candidatar" in argv:
        r = candidatar(estado, Path(arg["fila"]))
        print(json.dumps({"CANDIDATAS": len(r["CANDIDATAS"]), "NAO_ENTRAM": len(r["NAO_ENTRAM"])}, ensure_ascii=False))
        return 0
    quero = "CANARIO" if "--canario" in argv else "DIA" if "--dia" in argv else None
    if not quero:
        print(__doc__)
        return 2
    if quero == "CANARIO" and estado.get("CANARIO"):
        print("RECUSADO: o canario ja correu (%s); agora e --dia" % estado["CANARIO"]["MODO"])
        return 2
    if quero == "DIA" and (not estado.get("CANARIO") or estado["CANARIO"]["MODO"] == "PARADO"):
        print("RECUSADO: sem canario com formato provado nao ha busca em lote (%s)" % (estado.get("CANARIO") or {}).get("MODO"))
        return 2
    seco = "--seco" in argv
    if seco:
        fx = Path(arg["fixtures"])
        resp = json.loads((fx / "RESPOSTAS-ORCID.json").read_text(encoding="utf-8"))
        agora = datetime.fromisoformat(arg["agora"]) if "agora" in arg else None
        ctd = CT.Contador24h(Path(arg.get("contador") or saida / "CONTADOR-24H.json"), agora=(lambda: agora) if agora else None)

        def falso(url):
            r = resp.get(url)
            if r is None:
                raise S.urllib.error.HTTPError(url, 404, "sem fixture", {}, None)
            return r.get("HTTP", 200), r["TEXTO"].encode("utf-8")
        buscar, pausa = falso, 0
    else:
        if "--autorizado" not in argv:
            print("RECUSADO: sai a rede; so com --autorizado (quem corre e o coordenador)")
            return 2
        ctd = CT.Contador24h(Path(arg.get("contador") or CT.CONTADOR_PADRAO))
        buscar, pausa = None, S.PAUSA_S
    n = len(estado["DIAS"]) + (1 if estado.get("CANARIO") else 0) + 1
    pasta = saida / ("%s-%02d" % (quero, n))
    pasta.mkdir(parents=True, exist_ok=True)
    if not seco and not S.portao(pasta, "ANTES"):
        print("PAROU: portao de egresso nao e IT (antes)")
        return 3
    t = S.Transporte(pasta, buscar=buscar, pausa=pausa, contador=ctd)
    if quero == "CANARIO":
        estado["CANARIO"] = r = canario(estado, t)
    else:
        r = dia(estado, t)
        estado["DIAS"].append(dict(r, PASTA=pasta.name, PEDIDOS_POR_DOMINIO=dict(t.conta)))
    arq.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (pasta / "PEDIDOS.json").write_text(json.dumps({"PEDIDOS": t.registo, "POR_DOMINIO": dict(t.conta)},
                                                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if not seco and not S.portao(pasta, "DEPOIS"):
        print("PAROU: portao de egresso nao e IT (depois)")
        return 3
    print(json.dumps(dict(r, PEDIDOS_POR_DOMINIO=dict(t.conta)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
