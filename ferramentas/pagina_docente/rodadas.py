# -*- coding: utf-8 -*-
"""PAGINA-DO-DOCENTE · o comando por RODADAS (quem corre e o coordenador; VPN IT).

    py ferramentas/pagina_docente/rodadas.py --plano   --pessoas=<PESSOAS-ORDENADAS.json> --medida=<MEDIDA-OFFLINE.json>
    py ferramentas/pagina_docente/rodadas.py --rodada=N --autorizado --pessoas=... --medida=... --saida=<pasta fora do Git>
    py ferramentas/pagina_docente/rodadas.py --seco [--rodada=N] --fixtures=<pasta> --pessoas=<fixtures/PESSOAS.json> --saida=<pasta>

Uma rodada, por universidade (as 19; os 3 da consulta2 nao tem universidade MUR e ficam fora):
  1. as pessoas ainda por fazer (as ja feitas em rodadas anteriores da mesma --saida nao se repetem;
     as que ficaram PENDENTE pelo teto voltam na rodada seguinte, primeiro);
  2. o endereco da pagina de cada pessoa: o ja conhecido (lista guardada na MEDIDA-OFFLINE ou numa rodada
     anterior) ou, se nao, a LISTA de docentes (ENTRADA do leitor; CASA do site -> descobrir a lista);
     lista paginada (Udine) segue as paginas dentro do teto; regra de endereco medida (Milano, Bologna)
     so quando a lista nao traz a pessoa, e a pagina so vale se o NOME conferir nela;
  3. a pagina da pessoa, lida pelo leitor da universidade (so o BLOCO da pessoa);
  4. segundo passo: a pagina propria que a pagina oficial declara (campo «Sito web»/«Sito personale», lab)
     e aberta NA RODADA SEGUINTE (1 por pessoa), e dela tiram-se os links para canais publicos.
Limites (no codigo): 5 pedidos por dominio registavel por rodada CONTANDO o robots.txt (seguir.Transporte);
robots respeitado (nao lido = nao se pede); 3 s entre pedidos; portao de egresso IT antes e depois (para se
nao for IT); bytes com sha256 fora do Git. Perfis sociais NAO se abrem (so o endereco). E-mail/telefone nunca.
Saida: <saida>/RODADA-NN/RESULTADO.json no formato do seguir.py (PESSOAS[].CANAIS/NAO_ENTRAM), para que
`seguir.py --candidatar --saida=<saida>` leve os canais a porta canonica numa COPIA da fila.
"""
import json
import sys
import urllib.error
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import leitor as L                                                    # noqa: E402
import universidades as U                                             # noqa: E402

S = L.S
POR_RODADA = {"MEDIDA_EM_BYTES": 3, "SO_ENTRADA": 3, "CASA_DO_SITE": 2}   # pessoas por universidade por rodada
# FALHA (rede/servidor) e PENDENTE (teto) NAO sao finais: voltam na rodada seguinte
FINAIS = {"LIDA", "LIDA_OFFLINE", "NAO_ACHEI", "AMBIGUO", "NOME_NAO_CONFERE", "ROBOTS_OU_NAO_LIDO"}


def alvo(pessoas: list) -> tuple:
    dentro = [p for p in pessoas if p.get("PRIORIDADE") is True and p.get("UNIVERSIDADE") in U.UNIVERSIDADES]
    fora = [p for p in pessoas if p.get("PRIORIDADE") is True and p.get("UNIVERSIDADE") not in U.UNIVERSIDADES]
    return dentro, fora


def estado_anterior(saida: Path, medida: dict) -> dict:
    """O que ja se sabe por pessoa: a MEDIDA-OFFLINE (listas/paginas guardadas) e as rodadas anteriores."""
    st = {}
    for x in (medida or {}).get("PESSOAS", []):
        if x.get("ESTADO") == "NA_LISTA_GUARDADA: ACHEI" and x.get("URLS"):
            st[x["NOME"]] = {"ESTADO": "URL_CONHECIDA", "URL": x["URLS"][0], "DE": "MEDIDA-OFFLINE (lista guardada P5)"}
        if x.get("PAGINA_GUARDADA_LIDA") and x["PAGINA_GUARDADA_LIDA"].get("NOME_CONFERE"):
            lida = x["PAGINA_GUARDADA_LIDA"]
            st[x["NOME"]] = {"ESTADO": "LIDA_OFFLINE", "URL": x["URLS"][0], "DE": "pagina guardada P5 (24/09)",
                             "SEGUNDO_PASSO": segundo_passo(lida),
                             "VISTOS": [c["URL"].rstrip("/").lower() for c in lida["CANAIS"] + lida["NAO_ENTRAM"]]}
    listas = {}
    for r in sorted(saida.glob("RODADA-*/RESULTADO.json")) if saida else []:
        doc = json.loads(r.read_text(encoding="utf-8"))
        for p in doc["PESSOAS"]:
            vistos = (st.get(p["NOME"]) or {}).get("VISTOS") or []
            st[p["NOME"]] = {k: p.get(k) for k in ("ESTADO", "URL_PAGINA", "SEGUNDO_PASSO", "SEGUNDO_PASSO_FEITO")}
            st[p["NOME"]]["URL"] = p.get("URL_PAGINA")
            st[p["NOME"]]["VISTOS"] = vistos + [c["URL"].rstrip("/").lower() for c in p["CANAIS"] + p["NAO_ENTRAM"]]
        listas.update(doc.get("LISTAS_ACHADAS") or {})
    return st, listas


def segundo_passo(leitura: dict) -> list:
    """Paginas proprias declaradas no bloco da pessoa (campo medido, ou rotulo de pagina pessoal/lab) e sites
    externos com rotulo: abrem-se na rodada seguinte, 1 por pessoa."""
    xs = [x["URL"] for x in leitura.get("PAGINAS_PROPRIAS", []) if x.get("CAMPO")]
    xs += [x["URL"] for x in leitura.get("PAGINAS_PROPRIAS", []) if not x.get("CAMPO")]
    xs += [x["URL"] for x in leitura.get("CANAIS", []) if x["PLATAFORMA"] == "PAGINA_INSTITUCIONAL_OU_PESSOAL"]
    return list(dict.fromkeys(xs))[:1]


def fila_da_rodada(dentro: list, st: dict) -> dict:
    """Por universidade: primeiro os segundos passos por fazer, depois os PENDENTE, depois os novos."""
    por = defaultdict(list)
    for p in sorted(dentro, key=lambda p: p.get("ORDEM", 0)):
        e = st.get(p["NOME"], {})
        if e.get("ESTADO") in FINAIS and (not e.get("SEGUNDO_PASSO") or e.get("SEGUNDO_PASSO_FEITO")):
            continue
        por[p["UNIVERSIDADE"]].append(p)
    out = {}
    for uni, ps in por.items():
        def ordem(p):
            e = st.get(p["NOME"], {}).get("ESTADO")
            return (0 if e in FINAIS else 1 if e in ("PENDENTE", "FALHA") else 2, p.get("ORDEM", 0))
        out[uni] = sorted(ps, key=ordem)[:POR_RODADA[U.UNIVERSIDADES[uni]["FORMA"]]]
    return out


def base_da_pessoa(p: dict) -> dict:
    return {"NOME": p["NOME"], "UNIVERSIDADE": p["UNIVERSIDADE"], "SSD": p.get("SSD"), "ORCID": p.get("ORCID") or [],
            "ORDEM": p.get("ORDEM"), "CANAIS": [], "NAO_ENTRAM": [], "PAGINAS_PROPRIAS": [], "EXTERNOS_SEM_ROTULO": [],
            "PASSOS": []}


def teto_bateu(t) -> bool:
    return bool(t.registo) and t.registo[-1].get("RESULTADO") == "TETO_DO_DOMINIO"


def fazer_universidade(uni: str, grupo: list, st: dict, listas: dict, t) -> tuple:
    u = U.UNIVERSIDADES[uni]
    res, novas_listas, paginas = [], {}, []
    precisam = []
    for p in grupo:
        o = base_da_pessoa(p)
        e = st.get(p["NOME"], {})
        o["DE_ANTES"] = e.get("ESTADO")
        if e.get("ESTADO") in FINAIS:                     # so falta o segundo passo
            o.update(ESTADO=e["ESTADO"], URL_PAGINA=e.get("URL"), SEGUNDO_PASSO=e.get("SEGUNDO_PASSO") or [])
            fazer_segundo_passo(o, t, set(e.get("VISTOS") or []))
            res.append(o)
            continue
        if e.get("URL"):
            o["URL_PAGINA"] = e["URL"]
            o["PASSOS"].append("endereco ja conhecido (%s)" % e.get("DE", "rodada anterior"))
        else:
            precisam.append(o)
        res.append(o)
    # a lista (uma vez por ENTRADA por rodada; a lista descoberta pela CASA fica guardada para as seguintes)
    por_entrada = defaultdict(list)
    for o in precisam:
        p = next(x for x in grupo if x["NOME"] == o["NOME"])
        por_entrada[U.entrada_para(uni, p.get("DEPARTAMENTO"))].append((o, p))
    for entrada, pares in por_entrada.items():
        lista_url, motivo = listas.get(entrada) or entrada, None
        if u["FORMA"] == "CASA_DO_SITE" and entrada not in listas:
            _, b = t.get(entrada, "casa do site (%s): descobrir a lista de pessoas" % uni)
            motivo = None if b else t.registo[-1].get("RESULTADO")
            cands = L.descobrir_lista(b.decode("utf-8", "replace"), entrada, uni) if b else []
            lista_url = cands[0]["URL"] if cands else None
            if lista_url:
                novas_listas[entrada] = lista_url
            for o, _ in pares:
                o["PASSOS"].append("casa %s: %s" % (entrada, "lista = %s" % lista_url if lista_url else
                                                    "nenhum link de lista de pessoas (%s)" % (motivo or "NAO SEI onde fica")))
        htmls = []
        if lista_url:
            _, b = t.get(lista_url, "lista de docentes (%s)" % uni)
            if b:
                htmls.append((b.decode("utf-8", "replace"), lista_url))
            else:
                motivo = t.registo[-1].get("RESULTADO")
        for o, p in pares:
            achado, seguintes = {"ESTADO": "NAO_ACHEI", "URLS": []}, []
            for h, base in htmls:
                achado = L.achar_pessoa(h, base, p, uni)
                seguintes += L.proximas_paginas(h, base, uni)
                if achado["ESTADO"] != "NAO_ACHEI":
                    break
            vistas = {b for _, b in htmls}
            while achado["ESTADO"] == "NAO_ACHEI" and seguintes:
                prox = seguintes.pop(0)
                if prox in vistas:
                    continue
                vistas.add(prox)
                _, b = t.get(prox, "lista de docentes, pagina seguinte (%s)" % uni)
                if not b:
                    motivo = t.registo[-1].get("RESULTADO")
                    break
                h = b.decode("utf-8", "replace")
                htmls.append((h, prox))
                achado = L.achar_pessoa(h, prox, p, uni)
                seguintes += [x for x in L.proximas_paginas(h, prox, uni) if x not in vistas]
            o["PASSOS"].append("lista: %s %s" % (achado["ESTADO"], achado.get("URLS", [])[:3]))
            if achado["ESTADO"] == "ACHEI":
                o["URL_PAGINA"] = achado["URL"]
            elif achado["ESTADO"] == "AMBIGUO":
                o["ESTADO"] = "AMBIGUO"
            elif motivo == "TETO_DO_DOMINIO":
                o["ESTADO"] = "PENDENTE"
                o["PASSOS"].append("a lista (ou a pagina seguinte dela) nao coube no teto desta rodada: volta na proxima")
            elif L.construir(p, uni):
                o["URL_PAGINA"] = L.construir(p, uni)
                o["CONSTRUIDO"] = U.UNIVERSIDADES[uni]["CONSTRUIR"][1]
                o["PASSOS"].append("endereco CONSTRUIDO pela regra (%s): so vale se o nome conferir" % o["CONSTRUIDO"])
            elif motivo == "ROBOTS_OU_NAO_LIDO":
                o["ESTADO"] = "ROBOTS_OU_NAO_LIDO"
            elif not htmls:
                o["ESTADO"] = "FALHA"
            else:
                o["ESTADO"] = "NAO_ACHEI"
    # as paginas das pessoas
    for o in res:
        if o.get("ESTADO") or not o.get("URL_PAGINA"):
            continue
        p = next(x for x in grupo if x["NOME"] == o["NOME"])
        antes = len(t.registo)
        st_http, b = t.get(o["URL_PAGINA"], "pagina oficial do docente %s" % o["NOME"])
        ult = t.registo[-1] if len(t.registo) > antes else {}
        if not b:
            o["ESTADO"] = ("PENDENTE" if ult.get("RESULTADO") == "TETO_DO_DOMINIO" else
                           "ROBOTS_OU_NAO_LIDO" if ult.get("RESULTADO") == "ROBOTS_OU_NAO_LIDO" else
                           "NAO_ACHEI" if o.get("CONSTRUIDO") else "FALHA")
            o["PASSOS"].append("pagina: %s (HTTP %s)" % (ult.get("RESULTADO"), st_http))
            continue
        html = b.decode("utf-8", "replace")
        if not L.nome_confere(html, p, uni):
            o["ESTADO"] = "NOME_NAO_CONFERE"
            o["PASSOS"].append("pagina aberta, mas o nome nao esta no bloco da pessoa: nao se le (homonimo/regra errada)")
            continue
        paginas.append((o, html))
    mold = L.gabarito([(h, o["URL_PAGINA"]) for o, h in paginas])
    for o, html in paginas:
        r = L.ler_pagina(html, o["URL_PAGINA"], uni, mold)
        for k in ("CANAIS", "NAO_ENTRAM", "PAGINAS_PROPRIAS", "EXTERNOS_SEM_ROTULO"):
            o[k] = r[k]
        o["BLOCO"] = r["BLOCO"]
        o["ESTADO"] = "LIDA"
        o["SEGUNDO_PASSO"] = segundo_passo(r)
        o["PASSOS"].append("pagina lida (%s): %d canal(is), %d fora, %d pagina(s) propria(s)" % (
            r["BLOCO"], len(r["CANAIS"]), len(r["NAO_ENTRAM"]), len(r["PAGINAS_PROPRIAS"])))
    return res, novas_listas


def fazer_segundo_passo(o: dict, t, ja_vistos: set = frozenset()) -> None:
    """Abre a pagina propria declarada (1 por pessoa). Canal ja registado numa rodada anterior nao se repete.
    Falha de rede/teto = o segundo passo fica por fazer (volta na rodada seguinte); robots = feito (nao se pede)."""
    feito = True
    for url in o.get("SEGUNDO_PASSO") or []:
        _, b = t.get(url, "pagina propria declarada na pagina oficial de %s" % o["NOME"])
        if not b:
            r = t.registo[-1].get("RESULTADO") if t.registo else None
            o["PASSOS"].append("segundo passo %s: nao aberto (%s)" % (url, r))
            feito = feito and r == "ROBOTS_OU_NAO_LIDO"
            continue
        n = 0
        for href, txt in L.ancoras(b.decode("utf-8", "replace"), url):
            plat, tipo, entra = S.classificar(href)
            if plat in ("PAGINA_INSTITUCIONAL_OU_PESSOAL", "ORCID", "GOOGLE_SCHOLAR") or L.UTILIDADES.search(href):
                continue
            if L.e_conta_social(href, plat) and L.INSTITUCIONAL.search(href):
                continue
            k = href.rstrip("/").lower()
            if k in ja_vistos or any(x["URL"].rstrip("/").lower() == k for x in o["CANAIS"] + o["NAO_ENTRAM"]):
                continue
            linha = {"URL": href, "PLATAFORMA": plat, "TIPO": tipo, "TEXTO": txt[:80], "VISTO_EM": url,
                     "PROVA": "LIGADO NA PAGINA PROPRIA que a pagina oficial do docente declara"}
            (o["CANAIS"] if entra else o["NAO_ENTRAM"]).append(linha)
            n += 1
        o["PASSOS"].append("segundo passo %s: %d link(s) novo(s) para canais publicos" % (url, n))
    o["SEGUNDO_PASSO_FEITO"] = feito


def correr(pessoas: list, saida: Path, t, medida: dict, raiz: Path) -> dict:
    dentro, fora = alvo(pessoas)
    st, listas = estado_anterior(raiz, medida)
    fila = fila_da_rodada(dentro, st)
    todos, novas = [], {}
    for uni in sorted(fila):
        r, nl = fazer_universidade(uni, fila[uni], st, {**listas, **novas}, t)
        todos += r
        novas.update(nl)
    doc = {"DATASET": "PAGINA-DOCENTE-RODADA", "PESSOAS": todos, "LISTAS_ACHADAS": {**listas, **novas},
           "FORA_DAS_19": [p["NOME"] for p in fora], "PEDIDOS": t.registo, "PEDIDOS_POR_DOMINIO": dict(t.conta),
           "TETO": S.TETO, "TETO_RESPEITADO": all(v <= S.TETO for v in t.conta.values()),
           "ESTADOS": dict(Counter(p.get("ESTADO") or "SEM_ESTADO" for p in todos))}
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "RESULTADO.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return doc


def plano(pessoas: list, medida: dict) -> list:
    """Estimativa sem rede (o executor e que manda: o que nao couber no teto fica PENDENTE e volta)."""
    dentro, fora = alvo(pessoas)
    st, _ = estado_anterior(None, medida)
    linhas = []
    for uni in sorted({p["UNIVERSIDADE"] for p in dentro}, key=lambda x: -sum(p["UNIVERSIDADE"] == x for p in dentro)):
        ps = [p for p in dentro if p["UNIVERSIDADE"] == uni]
        ja = [p for p in ps if st.get(p["NOME"], {}).get("ESTADO") == "LIDA_OFFLINE"]
        conh = [p for p in ps if st.get(p["NOME"], {}).get("ESTADO") == "URL_CONHECIDA"]
        k = POR_RODADA[U.UNIVERSIDADES[uni]["FORMA"]]
        falta = len(ps) - len(ja)
        linhas.append({"UNIVERSIDADE": uni, "PESSOAS": len(ps), "PAGINA_JA_LIDA_OFFLINE": len(ja),
                       "ENDERECO_JA_CONHECIDO": len(conh), "LEITOR": U.UNIVERSIDADES[uni]["FORMA"],
                       "POR_RODADA": k, "RODADAS_ESTIMADAS": -(-falta // k) if falta else 0,
                       "ENTRADA": U.UNIVERSIDADES[uni]["ENTRADAS"][0][1]})
    return linhas, [p["NOME"] for p in fora]


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    pessoas = json.loads(Path(arg["pessoas"]).read_text(encoding="utf-8")) if "pessoas" in arg else []
    pessoas = pessoas["PESSOAS"] if isinstance(pessoas, dict) else pessoas
    medida = json.loads(Path(arg["medida"]).read_text(encoding="utf-8")) if arg.get("medida") else {}
    if "--plano" in argv:
        linhas, fora = plano(pessoas, medida)
        for x in linhas:
            print("%-26s pessoas %2d | ja lida %d | endereco conhecido %d | leitor %-15s | %d/rodada -> ~%d rodada(s) | %s" % (
                x["UNIVERSIDADE"][:26], x["PESSOAS"], x["PAGINA_JA_LIDA_OFFLINE"], x["ENDERECO_JA_CONHECIDO"], x["LEITOR"],
                x["POR_RODADA"], x["RODADAS_ESTIMADAS"], x["ENTRADA"]))
        print("rodadas estimadas: %d (+1 para os segundos passos); fora das 19: %s" % (
            max(x["RODADAS_ESTIMADAS"] for x in linhas), "; ".join(fora)))
        return 0
    if "rodada" in arg and "--seco" not in argv:
        if "--autorizado" not in argv:
            print("RECUSADO: --rodada sai a rede; so com --autorizado (quem corre e o coordenador)")
            return 2
        raiz = Path(arg["saida"])
        saida = raiz / ("RODADA-%02d" % int(arg["rodada"]))
        if saida.exists() and any(saida.iterdir()):
            print("RECUSADO: %s ja existe (uma rodada corre uma vez; a seguinte e --rodada=N+1)" % saida)
            return 2
        saida.mkdir(parents=True, exist_ok=True)
        if not S.portao(saida, "ANTES"):
            print("PAROU: portao de egresso nao e IT (antes)")
            return 3
        doc = correr(pessoas, saida, S.Transporte(saida), medida, raiz)
        ok = S.portao(saida, "DEPOIS")
        print(json.dumps({"PEDIDOS_POR_DOMINIO": doc["PEDIDOS_POR_DOMINIO"], "TETO_RESPEITADO": doc["TETO_RESPEITADO"],
                          "ESTADOS": doc["ESTADOS"], "PORTAO_DEPOIS_IT": ok,
                          "CANAIS": sum(len(p["CANAIS"]) for p in doc["PESSOAS"])}, ensure_ascii=False))
        return 0 if ok else 3
    if "--seco" in argv:
        fx = Path(arg["fixtures"])
        respostas = json.loads((fx / "RESPOSTAS.json").read_text(encoding="utf-8"))

        def falso(url):
            r = respostas.get(url)
            if r is None:
                raise urllib.error.HTTPError(url, 404, "nao ha fixture", {}, None)
            corpo = (fx / r["FICHEIRO"]).read_bytes() if r.get("FICHEIRO") else r.get("TEXTO", "").encode("utf-8")
            return r.get("HTTP", 200), corpo
        raiz = Path(arg["saida"])
        n = int(arg.get("rodada", "1"))
        doc = correr(pessoas, raiz / ("RODADA-%02d" % n), S.Transporte(raiz / ("RODADA-%02d" % n), buscar=falso, pausa=0),
                     medida, raiz)
        print(json.dumps({"PEDIDOS_POR_DOMINIO": doc["PEDIDOS_POR_DOMINIO"], "TETO_RESPEITADO": doc["TETO_RESPEITADO"],
                          "ESTADOS": doc["ESTADOS"],
                          "CANAIS": [(p["NOME"], c["PLATAFORMA"]) for p in doc["PESSOAS"] for c in p["CANAIS"]]},
                         ensure_ascii=False, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
