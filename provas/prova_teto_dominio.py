#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA-TETO-DOMINIO — a verificação INDEPENDENTE do teto por domínio depois de uma onda.

    py provas/prova_teto_dominio.py --livro <runs.ndjson> --onda <ficheiro com os RUN_ID> [--cortesia <livro.ndjson>]
                                    [--teto N] [--json saida.json]
    py provas/prova_teto_dominio.py --cortesia <livro da cortesia adaptativa>      (só o livro: a reprodução)

D38 (bot Luciano, 25/09 03:25): o teto conta-se por DOMÍNIO REGISTÁVEL e pela ONDA inteira (cia.it =
www.cia.it = sub.cia.it, repartidos entre as fontes). Na 1.ª onda, cia.it levou 16.

D124 (dono, 27/09): o 5 fixo SAIU. A prova deixa de perguntar «passou de 5?» e passa a perguntar:
  1. NUNCA PASSOU DO ORÇAMENTO VIGENTE DO DOMÍNIO: por domínio, os pedidos da onda (contados no livro de
     corridas) não passam do orçamento que estava em vigor (`--teto N` = um teto manual fixo);
  2. RECUOU NO SINAL: o livro da cortesia (`--cortesia`) é REPRODUZIDO reserva a reserva — nenhuma reserva
     durante uma pausa de 24 h, antes do fim de um Retry-After, com outro pedido do mesmo domínio em curso
     (rajada), antes da pausa mínima, acima do teto de segurança da classe, ou acima do orçamento vigente;
  3. NENHUM PEDIDO SEM RESERVA: com os dois livros, cada corrida fez no máximo os pedidos que reservou.
As verificações 2 (salvo o orçamento vigente) são escritas AQUI, a partir dos números da política
(`regras/POLITICA-CORTESIA-ADAPTATIVA.json`), sem usar a dobra do contador: o contador que corta não é o que
confere. O orçamento vigente é a regra (um dono só: `coleta/cortesia_adaptativa.dobrar_eventos`), aplicada
ao que o livro REGISTOU.

POR QUE É INDEPENDENTE
  - NÃO lê o resumo do condutor (`PEDIDOS_POR_SITE` do BC5) nem o livro de onda do disjuntor
    (`SINTONIA_TETO_ONDA`, que é o contador de quem está a ser verificado): lê o LIVRO DE CORRIDAS
    (`data/collection-ledger/italy/runs.ndjson`), onde o transporte do coletor escreve, por corrida,
    `CORTESIA.PEDIDOS_POR_HOST`.
  - O domínio registável vem de `coleta/dominio_registavel.py` (a lista de sufixos própria, sem Public Suffix
    List): um só dono da regra para o transporte, as rodadas e esta prova (DA-21). A independência é a do
    CONTADOR — esta prova não lê o de quem é verificado.
  - Uma corrida da onda que o livro não tem, ou sem `PEDIDOS_POR_HOST`, NÃO conta zero: a prova
    diz NAO_SEI (código 2). Contar zero deixaria uma onda cega passar.

Saída: por domínio, o total, os hosts e as corridas que o somaram; PASS (0) / FAIL (1) / NAO_SEI (2).
"""
import argparse
import json
import os
import re
import sys
import time

# `XX-` tambem: o orquestrador cunha `{pais}-{alvo}-...` e um pedido sem pais sai `XX`
# (PROVA-TETO-SOCIAL). Uma corrida da onda ignorada pelo padrao seria contada como zero.
RE_RUN_ID = re.compile(r"(?:IT|XX)-T\d+-\d{4}-\d{2}-\d{2}-\d{6}-[0-9a-f]{16}")

# A regra do dominio registavel (sufixos, D41, host limpo) vive em `coleta/dominio_registavel.py` — um so dono
# no runtime (DA-21, lote 4). Importada com os MESMOS nomes: quem usa `prova_teto_dominio.X` continua igual.
# D124: o TETO_D38 (5) saiu; o orcamento vem da politica adaptativa (`coleta/cortesia_adaptativa.py`).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "coleta"))
from dominio_registavel import (SUFIXOS_DOIS_NIVEIS, MESMO_ORCAMENTO,  # noqa: E402,F401
                                host_limpo, dominio_registavel, orcamento_de)
import cortesia_adaptativa as CA  # noqa: E402


def _teto_manual():
    v = os.environ.get("SINTONIA_TETO_POR_HOST")
    return int(v) if v else None


def limite_do_dominio(dom, eventos=None, run_ids=None):
    """O orcamento que esteve em vigor para `dom` durante a onda: o manual declarado; senao o MAIOR orcamento
    vigente nos instantes das reservas da onda (a reproducao do livro da cortesia) e o de agora (sem livro:
    o inicial da classe, que e o que o transporte usou sem memoria)."""
    m = _teto_manual()
    if m is not None:
        return m
    ev = eventos if eventos is not None else (CA.ler_eventos(CA.livro()) if CA.livro() else [])
    d = CA.dominio(dom)
    pol = CA.politica()
    cand = [CA.dobrar_eventos(ev, d, time.time(), pol)["ORCAMENTO_24H"]]
    ids = set(run_ids or [])
    for e in ev:
        if e["DOMINIO"] == d and e["TIPO"] == "RESERVA" and (not ids or e.get("RUN_ID") in ids):
            antes = [x for x in ev if float(x["EM"]) < float(e["EM"])]
            cand.append(CA.dobrar_eventos(antes, d, float(e["EM"]), pol)["ORCAMENTO_24H"])
    return max(cand)


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


def _limites(teto, dominios, eventos=None, run_ids=None):
    if isinstance(teto, int):
        return {d: teto for d in dominios}
    return {d: limite_do_dominio(d, eventos, run_ids) for d in dominios}


def verificar(run_ids, corridas, teto=None, eventos=None):
    """`teto`: None = o orcamento vigente de cada dominio (D124); int = um teto manual fixo."""
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
            dom = orcamento_de(host)
            e = por_dom.setdefault(dom, {"PEDIDOS": 0, "HOSTS": {}, "CORRIDAS": {}})
            e["PEDIDOS"] += int(n)
            e["HOSTS"][host] = e["HOSTS"].get(host, 0) + int(n)
            e["CORRIDAS"][rid] = e["CORRIDAS"].get(rid, 0) + int(n)
    try:
        lim = _limites(teto, por_dom, eventos, run_ids)
    except ValueError as ex:                                        # livro da cortesia ilegivel: NAO SEI
        lim, sem_contagem = {}, sem_contagem + ["LIVRO_DA_CORTESIA_ILEGIVEL: %s" % ex]
    acima = {d: e["PEDIDOS"] for d, e in por_dom.items() if d in lim and e["PEDIDOS"] > lim[d]}
    if sem_livro or sem_contagem or not run_ids:
        estado = "NAO_SEI"
    else:
        estado = "FAIL" if acima else "PASS"
    return {"ESTADO": estado, "TETO_POR_DOMINIO_POR_ONDA": lim if not isinstance(teto, int) else teto,
            "TETO_VEM_DE": "manual (--teto)" if isinstance(teto, int) else
            ("SINTONIA_TETO_POR_HOST (manual)" if _teto_manual() is not None else "orcamento vigente (D124)"),
            "CORRIDAS_DA_ONDA": len(run_ids),
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


def verificar_plano(plano, coorte_ids=None, indices=None, teto=None):
    """Um PLANO (ex.: onda_web --so-plano) ainda nao tem corridas: confere-se o que ele PREVE.
    1. reagrupa PEDIDOS_POR_DOMINIO pelo dominio desta prova e reprova acima do teto;
    2. se houver coorte e indices: o dominio de cada fonte, calculado AQUI a partir do INDEX_URL do contrato,
       tem de ser uma chave do plano (senao o plano agrupou-a noutro sitio) — fonte sem indice = NAO_SEI."""
    por_dom = {}
    for d, n in (plano.get("PEDIDOS_POR_DOMINIO") or {}).items():
        k = orcamento_de(d)
        por_dom[k] = por_dom.get(k, 0) + int(n)
    lim = _limites(teto, por_dom)
    acima = {d: n for d, n in por_dom.items() if n > lim[d]}
    sem_indice, fora_do_plano, dominios = [], [], {}
    for s in coorte_ids or []:
        u = (indices or {}).get(s)
        if not u:
            sem_indice.append(s)
            continue
        d = orcamento_de(u)
        dominios[s] = d
        if d not in por_dom and s not in (plano.get("SALTAM_POR_TETO_DOMINIO") or []):
            fora_do_plano.append(s)
    if not plano.get("PEDIDOS_POR_DOMINIO") or sem_indice:
        estado = "NAO_SEI"
    elif acima or fora_do_plano:
        estado = "FAIL"
    else:
        estado = "PASS"
    return {"ESTADO": estado, "TETO_POR_DOMINIO_POR_ONDA": lim, "PEDIDOS_PREVISTOS_POR_DOMINIO": por_dom,
            "DOMINIOS_ACIMA_DO_TETO": acima, "FONTES_SEM_INDICE_NO_CONTRATO": sem_indice,
            "FONTES_CUJO_DOMINIO_NAO_ESTA_NO_PLANO": fora_do_plano, "DOMINIO_POR_FONTE": dominios,
            "PEDIDOS_PREVISTOS": sum(por_dom.values())}


# ── D124: a reproducao do livro da cortesia adaptativa ────────────────────────
def verificar_livro(eventos, pol=None):
    """Reproduz o livro reserva a reserva. As regras de pausa, Retry-After, rajada, pausa minima e teto de
    seguranca sao verificadas AQUI, a partir dos numeros da politica; o orcamento vigente, pela regra."""
    pol = pol or CA.politica()
    R, J = pol["RECUO"], float(pol["JANELA_S"])
    viol, por_dom = [], {}
    for i, e in enumerate(eventos):
        por_dom.setdefault(e["DOMINIO"], []).append((float(e["EM"]), i, e))
    reservas = 0
    for d, evs in sorted(por_dom.items()):
        evs.sort(key=lambda x: (x[0], x[1]))
        nome, k = CA.classe_de(d, pol)
        sinais, retry_ate, pausa_ate, crawl = [], 0.0, 0.0, 0.0
        ult_res = ult_resp = None
        vivas = []
        for j, (t, _i, e) in enumerate(evs):
            if e["TIPO"] == "RESERVA":
                reservas += 1
                if e.get("CRAWL_DELAY_S") is not None:
                    crawl = max(crawl, float(e["CRAWL_DELAY_S"]))
                if t < pausa_ate:
                    viol.append({"DOMINIO": d, "EM": t, "VIOLACAO": "RESERVA_DURANTE_PAUSA_24H", "ATE": pausa_ate})
                if t < retry_ate:
                    viol.append({"DOMINIO": d, "EM": t, "VIOLACAO": "RESERVA_ANTES_DO_RETRY_AFTER", "ATE": retry_ate})
                if ult_res is not None and (ult_resp is None or ult_resp < ult_res) and t < ult_res + pol["LEASE_S"]:
                    viol.append({"DOMINIO": d, "EM": t, "VIOLACAO": "RAJADA_NO_MESMO_DOMINIO", "EM_CURSO_DESDE": ult_res})
                marcos = [x for x in (ult_res, ult_resp) if x is not None]
                marco = max(marcos) if marcos else None
                if marco is not None and t < marco + max(float(k["PAUSA_S"]), crawl) - 1e-6:
                    viol.append({"DOMINIO": d, "EM": t, "VIOLACAO": "PAUSA_MINIMA_VIOLADA", "DESDE": marco})
                vivas = [x for x in vivas if x > t - J] + [t]
                if len(vivas) > int(k["TETO"]):
                    viol.append({"DOMINIO": d, "EM": t, "VIOLACAO": "ACIMA_DO_TETO_DE_SEGURANCA", "EM_24H": len(vivas)})
                vig = CA.dobrar_eventos([x[2] for x in evs[:j]], d, t, pol)
                if vig["CABEM_24H"] <= 0:
                    viol.append({"DOMINIO": d, "EM": t, "VIOLACAO": "PASSOU_DO_ORCAMENTO_VIGENTE",
                                 "ORCAMENTO_24H": vig["ORCAMENTO_24H"], "GASTO_24H": vig["GASTO_24H"]})
                ult_res = t
            elif e["TIPO"] == "RESPOSTA":
                ult_resp = t
                if e.get("SINAIS"):
                    sinais = [x for x in sinais if x > t - R["JANELA_DOS_SINAIS_S"]] + [t]
                    if e.get("RETRY_AFTER_S"):
                        retry_ate = max(retry_ate, t + float(e["RETRY_AFTER_S"]))
                    if len(sinais) >= R["SINAIS_PARA_PAUSA"]:
                        pausa_ate = max(pausa_ate, t + float(R["PAUSA_S"]))
    estado = "NAO_SEI" if not reservas else ("FAIL" if viol else "PASS")
    return {"ESTADO": estado, "RESERVAS": reservas, "DOMINIOS": len(por_dom), "VIOLACOES": viol}


def cruzar(run_ids, corridas, eventos):
    """Cada corrida da onda fez no maximo os pedidos que reservou no livro da cortesia (por dominio)."""
    sem = []
    for rid in run_ids:
        ph = ((corridas.get(rid) or {}).get("CORTESIA") or {}).get("PEDIDOS_POR_HOST") or {}
        pedidos = {}
        for h, n in ph.items():
            pedidos[CA.dominio(h)] = pedidos.get(CA.dominio(h), 0) + int(n)
        for d, n in pedidos.items():
            r = sum(1 for e in eventos if e["TIPO"] == "RESERVA" and e["DOMINIO"] == d and e.get("RUN_ID") == rid)
            if n > r:
                sem.append({"RUN_ID": rid, "DOMINIO": d, "PEDIDOS": n, "RESERVAS": r})
    return sem


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verificacao independente do teto D38 (pedidos por dominio por onda).")
    ap.add_argument("--livro", help="runs.ndjson (livro de corridas do coletor)")
    ap.add_argument("--onda", help="ficheiro que lista os RUN_ID da onda (qualquer texto/JSON)")
    ap.add_argument("--plano", help="PLANO da onda (onda_web --so-plano): confere o que ele PREVE, antes da rede")
    ap.add_argument("--coorte", help="coorte (COORTE-BIG-COLLECTION-V1.json) para conferir o dominio fonte a fonte")
    ap.add_argument("--contratos-json", default="regras/italy_contracts_onboarded.json")
    ap.add_argument("--contratos-mjs", default="regras/italy_contracts.mjs")
    ap.add_argument("--teto", type=int, default=None, help="teto MANUAL fixo; sem ele, o orcamento vigente (D124)")
    ap.add_argument("--cortesia", help="livro da cortesia adaptativa (ndjson): reproduz e cruza (D124)")
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
        print("PROVA_TETO_DOMINIO_PLANO=%s · previstos=%d · teto por dominio: %s"
              % (r["ESTADO"], r["PEDIDOS_PREVISTOS"], json.dumps(r["TETO_POR_DOMINIO_POR_ONDA"], sort_keys=True)))
        for d, n in r["DOMINIOS_ACIMA_DO_TETO"].items():
            print("  ACIMA DO TETO  %-32s %3d" % (d, n))
        for s in r["FONTES_CUJO_DOMINIO_NAO_ESTA_NO_PLANO"]:
            print("  FORA DO PLANO  %s (%s)" % (s, r["DOMINIO_POR_FONTE"].get(s)))
        for s in r["FONTES_SEM_INDICE_NO_CONTRATO"]:
            print("  NAO_SEI        %s (sem INDEX_URL nos contratos do coletor)" % s)
        return {"PASS": 0, "FAIL": 1}.get(r["ESTADO"], 2)
    eventos = None
    if a.cortesia:
        from pathlib import Path as _P
        try:
            eventos = CA.ler_eventos(_P(a.cortesia))
        except ValueError as ex:
            print("PROVA_TETO_DOMINIO_LIVRO=NAO_SEI · livro da cortesia ilegivel: %s" % ex)
            return 2
        rl = verificar_livro(eventos)
        print("PROVA_TETO_DOMINIO_LIVRO=%s · reservas=%d · dominios=%d · violacoes=%d"
              % (rl["ESTADO"], rl["RESERVAS"], rl["DOMINIOS"], len(rl["VIOLACOES"])))
        for v in rl["VIOLACOES"][:50]:
            print("  VIOLACAO       %-32s %s" % (v["DOMINIO"], v["VIOLACAO"]))
        if not (a.livro and a.onda):
            if a.json:
                with open(a.json, "w", encoding="utf-8") as f:
                    json.dump(rl, f, ensure_ascii=False, indent=1)
            return {"PASS": 0, "FAIL": 1}.get(rl["ESTADO"], 2)
    if not (a.livro and a.onda):
        ap.error("sem --plano ou --cortesia, --livro e --onda sao obrigatorios")
    with open(a.onda, encoding="utf-8") as f:
        ids = run_ids_da_onda(f.read())
    with open(a.livro, encoding="utf-8") as f:
        corridas = ler_livro(f)
    r = verificar(ids, corridas, a.teto, eventos)
    if eventos is not None:
        r["LIVRO_DA_CORTESIA"] = rl
        r["PEDIDOS_SEM_RESERVA"] = cruzar(ids, corridas, eventos)
        if r["ESTADO"] == "PASS" and (rl["ESTADO"] == "FAIL" or r["PEDIDOS_SEM_RESERVA"]):
            r["ESTADO"] = "FAIL"
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    print("PROVA_TETO_DOMINIO=%s · corridas=%d · pedidos=%d · teto por dominio: %s"
          % (r["ESTADO"], r["CORRIDAS_DA_ONDA"], r["PEDIDOS_NA_ONDA"], r["TETO_VEM_DE"]))
    for d, n in r["DOMINIOS_ACIMA_DO_TETO"].items():
        print("  ACIMA DO TETO  %-32s %3d  (%s)" % (d, n, ", ".join("%s=%d" % kv for kv in r["PEDIDOS_POR_DOMINIO"][d]["HOSTS"].items())))
    for rid in r["CORRIDAS_SEM_LINHA_NO_LIVRO"] + r["CORRIDAS_SEM_PEDIDOS_POR_HOST"]:
        print("  NAO_SEI        %s (sem linha ou sem PEDIDOS_POR_HOST no livro)" % rid)
    return {"PASS": 0, "FAIL": 1}.get(r["ESTADO"], 2)


if __name__ == "__main__":
    sys.exit(main())
