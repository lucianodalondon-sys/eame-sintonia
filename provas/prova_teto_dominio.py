#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA-TETO-DOMINIO — a verificação INDEPENDENTE do teto D38 depois de uma onda.

    py provas/prova_teto_dominio.py --livro <runs.ndjson> --onda <ficheiro com os RUN_ID> [--teto 5] [--json saida.json]

D38 (bot Luciano, 25/09 03:25): no máximo 5 pedidos por DOMÍNIO REGISTÁVEL e pela ONDA inteira
(cia.it = www.cia.it = sub.cia.it, repartidos entre as fontes). Na 1.ª onda, cia.it levou 16.

POR QUE É INDEPENDENTE
  - NÃO lê o resumo do condutor (`PEDIDOS_POR_SITE` do BC5) nem o livro de onda do disjuntor
    (`SINTONIA_TETO_ONDA`, que é o contador de quem está a ser verificado): lê o LIVRO DE CORRIDAS
    (`data/collection-ledger/italy/runs.ndjson`), onde o transporte do coletor escreve, por corrida,
    `CORTESIA.PEDIDOS_POR_HOST`.
  - O domínio registável é calculado AQUI, com uma lista de sufixos própria (abaixo).
  - Uma corrida da onda que o livro não tem, ou sem `PEDIDOS_POR_HOST`, NÃO conta zero: a prova
    diz NAO_SEI (código 2). Contar zero deixaria uma onda cega passar.

Saída: por domínio, o total, os hosts e as corridas que o somaram; PASS (0) / FAIL (1) / NAO_SEI (2).
"""
import argparse
import json
import re
import sys

TETO_D38 = 5
RE_RUN_ID = re.compile(r"IT-T\d+-\d{4}-\d{2}-\d{2}-\d{6}-[0-9a-f]{16}")

# Sufixos públicos de DOIS níveis que esta prova conhece (escritos aqui, sem Public Suffix List:
# nenhuma nesta casa, e nenhuma se vai buscar à rede). Um sufixo que falte junta MAIS do que devia
# (ex.: `x.provincia.it` com `provincia.it`): a prova fica mais exigente, nunca mais branda.
SUFIXOS_DOIS_NIVEIS = frozenset("""
gov.it edu.it
abruzzo.it abr.it basilicata.it bas.it calabria.it cal.it campania.it cam.it
emilia-romagna.it emiliaromagna.it emr.it friuli-venezia-giulia.it friuli-vgiulia.it friulivenezia-giulia.it
friulivgiulia.it fvg.it lazio.it laz.it liguria.it lig.it lombardia.it lom.it marche.it mar.it molise.it mol.it
piemonte.it pmn.it puglia.it pug.it sardegna.it sar.it sicilia.it sic.it toscana.it tos.it trentino.it
trentino-alto-adige.it trentinoaltoadige.it taa.it umbria.it umb.it valledaosta.it valle-daosta.it vda.it vao.it
veneto.it ven.it
co.uk org.uk ac.uk gov.uk com.br org.br gov.br com.au org.au co.jp com.es com.pt co.nz com.ar com.mx
""".split())


def host_limpo(h):
    h = str(h or "").strip().lower()
    h = re.sub(r"^[a-z][a-z0-9+.-]*://", "", h)      # aceita tambem uma origem com esquema
    h = h.split("/")[0].split("@")[-1]
    if h.startswith("[") and "]" in h:                # IPv6 entre parenteses
        return h[: h.index("]") + 1]
    h = h.split(":")[0].rstrip(".")
    return h[4:] if h.startswith("www.") else h


def dominio_registavel(host):
    h = host_limpo(host)
    if not h or re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", h) or h.startswith("["):
        return h
    partes = [p for p in h.split(".") if p]
    if len(partes) <= 2:
        return ".".join(partes)
    dois = ".".join(partes[-2:])
    return ".".join(partes[-3:]) if dois in SUFIXOS_DOIS_NIVEIS else dois


def run_ids_da_onda(texto):
    return sorted(set(RE_RUN_ID.findall(texto)))


def ler_livro(linhas):
    corridas = {}
    for l in linhas:
        l = l.strip()
        if not l:
            continue
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("RUN_ID"):
            corridas[d["RUN_ID"]] = d
    return corridas


def verificar(run_ids, corridas, teto=TETO_D38):
    por_dom, sem_livro, sem_contagem = {}, [], []
    for rid in run_ids:
        c = corridas.get(rid)
        if c is None:
            sem_livro.append(rid)
            continue
        ph = (c.get("CORTESIA") or {}).get("PEDIDOS_POR_HOST")
        if not isinstance(ph, dict):
            sem_contagem.append(rid)
            continue
        for host, n in ph.items():
            dom = dominio_registavel(host)
            e = por_dom.setdefault(dom, {"PEDIDOS": 0, "HOSTS": {}, "CORRIDAS": {}})
            e["PEDIDOS"] += int(n)
            e["HOSTS"][host] = e["HOSTS"].get(host, 0) + int(n)
            e["CORRIDAS"][rid] = e["CORRIDAS"].get(rid, 0) + int(n)
    acima = {d: e["PEDIDOS"] for d, e in por_dom.items() if e["PEDIDOS"] > teto}
    if sem_livro or sem_contagem or not run_ids:
        estado = "NAO_SEI"
    else:
        estado = "FAIL" if acima else "PASS"
    return {"ESTADO": estado, "TETO_POR_DOMINIO_POR_ONDA": teto, "CORRIDAS_DA_ONDA": len(run_ids),
            "CORRIDAS_SEM_LINHA_NO_LIVRO": sem_livro, "CORRIDAS_SEM_PEDIDOS_POR_HOST": sem_contagem,
            "DOMINIOS_ACIMA_DO_TETO": dict(sorted(acima.items(), key=lambda kv: -kv[1])),
            "PEDIDOS_POR_DOMINIO": dict(sorted(por_dom.items(), key=lambda kv: -kv[1]["PEDIDOS"])),
            "PEDIDOS_NA_ONDA": sum(e["PEDIDOS"] for e in por_dom.values())}


def indices_dos_contratos(texto_json_onboarded, texto_mjs):
    """SOURCE_ID -> INDEX_URL, lidos como TEXTO dos dois donos dos contratos do coletor (sem correr codigo)."""
    out = {}
    try:
        for f in json.loads(texto_json_onboarded).get("FONTES", []):
            u = (f.get("ACQUISITION") or {}).get("INDEX_URL")
            if f.get("SOURCE_ID") and u:
                out[f["SOURCE_ID"]] = u
    except ValueError:
        pass
    for m in re.finditer(r'"?(IT-T\d+-\d{3})"?\s*:\s*\{(.{0,4000}?)INDEX_URL\s*:\s*"([^"]+)"', texto_mjs or "", re.S):
        if "IT-T" not in m.group(2):          # o INDEX_URL pertence a ESTE bloco, nao ao seguinte
            out.setdefault(m.group(1), m.group(3))
    return out


def verificar_plano(plano, coorte_ids=None, indices=None, teto=TETO_D38):
    """Um PLANO (ex.: onda_web --so-plano) ainda nao tem corridas: confere-se o que ele PREVE.
    1. reagrupa PEDIDOS_POR_DOMINIO pelo dominio desta prova e reprova acima do teto;
    2. se houver coorte e indices: o dominio de cada fonte, calculado AQUI a partir do INDEX_URL do contrato,
       tem de ser uma chave do plano (senao o plano agrupou-a noutro sitio) — fonte sem indice = NAO_SEI."""
    por_dom = {}
    for d, n in (plano.get("PEDIDOS_POR_DOMINIO") or {}).items():
        k = dominio_registavel(d)
        por_dom[k] = por_dom.get(k, 0) + int(n)
    acima = {d: n for d, n in por_dom.items() if n > teto}
    sem_indice, fora_do_plano, dominios = [], [], {}
    for s in coorte_ids or []:
        u = (indices or {}).get(s)
        if not u:
            sem_indice.append(s)
            continue
        d = dominio_registavel(u)
        dominios[s] = d
        if d not in por_dom and s not in (plano.get("SALTAM_POR_TETO_DOMINIO") or []):
            fora_do_plano.append(s)
    if not plano.get("PEDIDOS_POR_DOMINIO") or sem_indice:
        estado = "NAO_SEI"
    elif acima or fora_do_plano:
        estado = "FAIL"
    else:
        estado = "PASS"
    return {"ESTADO": estado, "TETO_POR_DOMINIO_POR_ONDA": teto, "PEDIDOS_PREVISTOS_POR_DOMINIO": por_dom,
            "DOMINIOS_ACIMA_DO_TETO": acima, "FONTES_SEM_INDICE_NO_CONTRATO": sem_indice,
            "FONTES_CUJO_DOMINIO_NAO_ESTA_NO_PLANO": fora_do_plano, "DOMINIO_POR_FONTE": dominios,
            "PEDIDOS_PREVISTOS": sum(por_dom.values())}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verificacao independente do teto D38 (pedidos por dominio por onda).")
    ap.add_argument("--livro", help="runs.ndjson (livro de corridas do coletor)")
    ap.add_argument("--onda", help="ficheiro que lista os RUN_ID da onda (qualquer texto/JSON)")
    ap.add_argument("--plano", help="PLANO da onda (onda_web --so-plano): confere o que ele PREVE, antes da rede")
    ap.add_argument("--coorte", help="coorte (COORTE-BIG-COLLECTION-V1.json) para conferir o dominio fonte a fonte")
    ap.add_argument("--contratos-json", default="regras/italy_contracts_onboarded.json")
    ap.add_argument("--contratos-mjs", default="regras/italy_contracts.mjs")
    ap.add_argument("--teto", type=int, default=TETO_D38)
    ap.add_argument("--json", help="onde gravar o resultado")
    a = ap.parse_args(argv)
    if a.plano:
        with open(a.plano, encoding="utf-8") as f:
            plano = json.load(f)
        ids, indices = None, None
        if a.coorte:
            with open(a.coorte, encoding="utf-8") as f:
                c = json.load(f)
            ids = [x if isinstance(x, str) else x.get("SOURCE_ID") for x in c.get("COORTE", [])]
            def _ler(p):
                try:
                    with open(p, encoding="utf-8") as f:
                        return f.read()
                except OSError:
                    return ""
            indices = indices_dos_contratos(_ler(a.contratos_json), _ler(a.contratos_mjs))
        r = verificar_plano(plano, ids, indices, a.teto)
        if a.json:
            with open(a.json, "w", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False, indent=1)
        print("PROVA_TETO_DOMINIO_PLANO=%s · previstos=%d · teto=%d por dominio por onda"
              % (r["ESTADO"], r["PEDIDOS_PREVISTOS"], r["TETO_POR_DOMINIO_POR_ONDA"]))
        for d, n in r["DOMINIOS_ACIMA_DO_TETO"].items():
            print("  ACIMA DO TETO  %-32s %3d" % (d, n))
        for s in r["FONTES_CUJO_DOMINIO_NAO_ESTA_NO_PLANO"]:
            print("  FORA DO PLANO  %s (%s)" % (s, r["DOMINIO_POR_FONTE"].get(s)))
        for s in r["FONTES_SEM_INDICE_NO_CONTRATO"]:
            print("  NAO_SEI        %s (sem INDEX_URL nos contratos do coletor)" % s)
        return {"PASS": 0, "FAIL": 1}.get(r["ESTADO"], 2)
    if not (a.livro and a.onda):
        ap.error("sem --plano, --livro e --onda sao obrigatorios")
    with open(a.onda, encoding="utf-8") as f:
        ids = run_ids_da_onda(f.read())
    with open(a.livro, encoding="utf-8") as f:
        corridas = ler_livro(f)
    r = verificar(ids, corridas, a.teto)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    print("PROVA_TETO_DOMINIO=%s · corridas=%d · pedidos=%d · teto=%d por dominio por onda"
          % (r["ESTADO"], r["CORRIDAS_DA_ONDA"], r["PEDIDOS_NA_ONDA"], r["TETO_POR_DOMINIO_POR_ONDA"]))
    for d, n in r["DOMINIOS_ACIMA_DO_TETO"].items():
        print("  ACIMA DO TETO  %-32s %3d  (%s)" % (d, n, ", ".join("%s=%d" % kv for kv in r["PEDIDOS_POR_DOMINIO"][d]["HOSTS"].items())))
    for rid in r["CORRIDAS_SEM_LINHA_NO_LIVRO"] + r["CORRIDAS_SEM_PEDIDOS_POR_HOST"]:
        print("  NAO_SEI        %s (sem linha ou sem PEDIDOS_POR_HOST no livro)" % rid)
    return {"PASS": 0, "FAIL": 1}.get(r["ESTADO"], 2)


if __name__ == "__main__":
    sys.exit(main())
