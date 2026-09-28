"""SOCIAL-ATE-A-SALA · A — desfazer o POLICY_BLOCK das candidatas LinkedIn/Instagram pelas decisoes do dono.

    py curadoria/desbloquear_social.py                        # so mostra: quantas, quais, que decisao cobre cada uma
    py curadoria/desbloquear_social.py --aplicar --copia      # numa COPIA dos livros
    py curadoria/desbloquear_social.py --aplicar --vivo       # no vivo, SO com o bot parado (curadoria/PARAR.flag)
    py curadoria/desbloquear_social.py --ensaio --copia [--json SAIDA]   # aplicar + worker SEM rede, numa copia

PORQUE (buraco 1 do estudo do coordenador, 27/09): a ponte (`ponte_candidatas.POLITICA`, D15) marcou
todas as candidatas LinkedIn e Instagram POLICY_BLOCK — na fila (ESTADO) e no livro do ciclo de vida
(o CANDIDATA_ID). O dono ja liberou: D22 (Reel por URL), D23 (video de ORGANIZACAO no LinkedIn), D24
(video de PESSOA do agro), D106 (comentarios IG/LI). O bloqueio antigo nunca foi desfeito, e sem
QUALIFY nenhuma ganha SOURCE_ID.

O QUE FAZ, SO PELAS PORTAS CANONICAS
    1 · FILA   `candidatas/fonte_nova.desbloquear_por_decisao` — POLICY_BLOCK -> CANDIDATA, com as
               decisoes, OWNER_AUTHORIZED=SIM e PLATFORM_POLICY_STATUS MEDIDO lado a lado (nada se apaga)
    2 · LIVRO  `curadoria/lifecycle.registar` — o CANDIDATA_ID sai de POLICY_BLOCK para DISCOVERED
               (append-only; a linha antiga fica)
    3 · FILA DE TAREFAS  `curadoria/fila.enfileirar(QUALIFY)` — o worker faz o resto pelo caminho de
               sempre: QUALIFY -> numero (SOURCE_ID) -> BUILD_CONTRACT (rota do Scrap) -> VALIDATE_ROUTE ->
               CANARY_PENDING. O canario e uma colheita do Scrap (maestro, com a VPN IT) e a regua social.

O QUE NAO FAZ: nao cunha SOURCE_ID (quem cunha e o QUALIFY), nao escreve contrato, nao sai para a rede,
nao toca a ponte (a D15 continua a barrar candidatas NOVAS — mudar isso e outra decisao).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas"):
    sys.path.insert(0, str(RAIZ / _p))

VIVOS = ("source-curator-service-v1", "ponte-viva")
PARAR = RAIZ / "curadoria" / "PARAR.flag"
QUEM = "curadoria/desbloquear_social.py (SOCIAL-ATE-A-SALA)"
SEM_REDE = {"QUALIFY", "BUILD_CONTRACT", "VALIDATE_ROUTE"}
RE_PESSOA = re.compile(r"linkedin\.com/(?:in|pub)/", re.I)

# A politica da plataforma, MEDIDA — o que a casa ja leu e guardou (nunca uma sonda nova).
ROBOTS_LINKEDIN = {"ROBOTS_STATUS": "DISALLOW_ALL", "ROBOTS_URL": "https://www.linkedin.com/robots.txt",
                   "ROBOTS_MEDIDO_EM": "2026-09-08", "FONTE": "leis/social_matriz.py (cabecalho) · D37"}


def livros_de_identidade(raiz: Path = RAIZ) -> dict:
    """Os livros de identidade da MESMA arvore, lidos pelo dono (a curadoria): contratos do curador,
    alocacao de SOURCE_ID e a fila de candidatas. So leitura. Usado por coleta/social_por_url_achado.py
    (LOTE8-INTEGRA: a coleta pergunta a curadoria em vez de abrir o registo dela)."""
    def ler(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return {"CONTRATOS": ler(raiz / "curadoria" / "italy_contracts_curator.json"),
            "ALLOC": ler(raiz / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"),
            "FILA": ler(raiz / "candidatas" / "FONTES-CANDIDATAS.json")}


def decisoes_de(c: dict) -> list[str]:
    """As decisoes do dono que cobrem ESTA candidata (e so estas)."""
    if c.get("TIPO") == "INSTAGRAM":
        return ["D22", "D106"]
    if c.get("TIPO") == "LINKEDIN":
        return ["D24", "D106"] if RE_PESSOA.search(c.get("URL") or "") else ["D23", "D106"]
    return []


def politica_medida(c: dict) -> tuple[str, dict]:
    """→ (PLATFORM_POLICY_STATUS, prova). A prova e a que a ponte ja escreveu (os termos), mais o robots."""
    ev = c.get("EVIDENCIA_POLITICA") or {}
    prova = {"TERMOS": {k: ev.get(k) for k in ("URL", "EM_VIGOR", "LIDO_EM", "SHA256", "FICHEIRO")}} if ev else {}
    if c.get("TIPO") == "LINKEDIN":
        prova["ROBOTS"] = ROBOTS_LINKEDIN
    return ("DISALLOWED" if prova else "NAO SEI"), prova


def bloqueadas(tambem_candidatas: bool = False) -> list[dict]:
    """As LinkedIn/Instagram em POLICY_BLOCK e sem SOURCE_ID. `tambem_candidatas`: mais as que estao
    CANDIDATA (sem bloqueio a desfazer, so o QUALIFY) — a fila do repositorio tem 25 assim que no vivo
    estao POLICY_BLOCK (medido pelo coordenador: 68+26 bloqueadas)."""
    import fonte_nova as FN
    estados = ("POLICY_BLOCK", "CANDIDATA") if tambem_candidatas else ("POLICY_BLOCK",)
    return [c for c in FN.carregar()["CANDIDATAS"]
            if c.get("TIPO") in ("LINKEDIN", "INSTAGRAM") and c.get("ESTADO") in estados
            and not c.get("SOURCE_ID")]


def aplicar(cands: list[dict]) -> list[dict]:
    import fila as F
    import fonte_nova as FN
    import lifecycle as LC
    feitas = []
    for c in cands:
        dec = decisoes_de(c)
        status, prova = politica_medida(c)
        if status == "NAO SEI" and c.get("ESTADO") == "POLICY_BLOCK":
            feitas.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "FEITO": "PARADA",
                           "PORQUE": "sem a politica da plataforma medida na ficha: nao se desbloqueia as cegas"})
            continue
        linha, feito = FN.desbloquear_por_decisao(c["CANDIDATA_ID"], dec, status, prova, QUEM)
        razao = ("SOCIAL-ATE-A-SALA: %s desfazem o POLICY_BLOCK da D15 (OWNER_AUTHORIZED=SIM; "
                 "PLATFORM_POLICY_STATUS=%s medido); aguarda QUALIFY" % ("+".join(dec), status))
        if LC.estado_de(c["CANDIDATA_ID"]) == LC.POLICY_BLOCK:
            LC.registar(c["CANDIDATA_ID"], LC.DISCOVERED, razao[:200],
                        evidence_ref="candidatas/FONTES-CANDIDATAS.json#%s.DESBLOQUEIO" % c["CANDIDATA_ID"])
        F.enfileirar(c["CANDIDATA_ID"], F.QUALIFY, priority=30, motivo=razao[:160])
        feitas.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "TIPO": c["TIPO"], "FEITO": feito, "DECISOES": dec,
                       "PLATFORM_POLICY_STATUS": status, "ESTADO_NA_FILA": (linha or {}).get("ESTADO"),
                       "ESTADO_NO_LIVRO": LC.estado_de(c["CANDIDATA_ID"])})
    return feitas


def _classe(porque: str) -> str:
    """O motivo de paragem, em poucas palavras (para contar)."""
    p = porque or ""
    for chave, nome in (("PERFIL_DE_PESSOA", "PESSOA: a rota do Scrap le so /company/ (D24 sem fase)"),
                        ("SHOWCASE", "SHOWCASE: nao e alvo do adaptador"),
                        ("URL_LINKEDIN_SEM_PAGINA", "URL LinkedIn sem pagina de organizacao"),
                        ("SEM_LIGACAO_OFICIAL", "sem ligacao oficial (site que aponte para a conta)"),
                        ("ja esta ligada a", "pagina/canal ja ligado a varias fontes (colisao)"),
                        ("territorio indeterminado", "territorio NAO SEI (sem decisao semantica)"),
                        ("fora de IT", "territorio decidido fora de IT"),
                        ("listar os Reels da conta", "INSTAGRAM: sem rota que liste a conta (D22 so abre o Reel)"),
                        ("Curator nao tem molde", "INSTAGRAM: sem molde de contrato")):
        if chave in p:
            return nome
    return p[:90] or "?"


def ensaio(cands: list[dict]) -> dict:
    """Aplica e corre o worker SO nas tarefas destas candidatas, e so as sem rede."""
    import fila as F
    import lifecycle as LC
    import worker as W
    ids = {c["CANDIDATA_ID"] for c in cands}
    antes = {n["SOURCE_ID"] for n in W._ler_alloc()["NOVAS"]}
    feitas = aplicar(cands)

    def nossas() -> set:
        return ids | {n["SOURCE_ID"] for n in W._ler_alloc()["NOVAS"] if n.get("CANDIDATE_ID") in ids}

    original = F.elegiveis

    def so_estas(*a, **kw):
        ok, fora = nossas(), []
        for t in original(*a, **kw):
            if t["SOURCE_ID"] not in ok:
                continue
            if t["TASK_TYPE"] not in SEM_REDE:
                raise RuntimeError("tarefa com rede no ensaio: %s %s" % (t["TASK_TYPE"], t["SOURCE_ID"]))
            fora.append(t)
        return fora

    F.elegiveis = so_estas
    try:
        r = W.correr(max_tarefas=0, pausa=0, verboso=False)
    finally:
        F.elegiveis = original
    novas = [n for n in W._ler_alloc()["NOVAS"] if n["SOURCE_ID"] not in antes and n.get("CANDIDATE_ID") in ids]
    por_cand = {}
    for x in r:
        if x["TASK_TYPE"] == "QUALIFY":
            por_cand[x["SOURCE_ID"]] = x
    tipo = {c["CANDIDATA_ID"]: c["TIPO"] for c in cands}
    paradas = Counter()
    for cid, x in por_cand.items():
        if x["RESULTADO"] != "OK":
            paradas["%s · %s" % (tipo.get(cid), _classe(x.get("PORQUE")))] += 1
    reuso = [cid for cid, x in por_cand.items() if x["RESULTADO"] == "OK"
             and cid not in {n["CANDIDATE_ID"] for n in novas}]
    return {"DESBLOQUEADAS": dict(Counter("%s:%s" % (f.get("TIPO"), f["FEITO"]) for f in feitas)),
            "TAREFAS": dict(Counter("%s:%s" % (x["TASK_TYPE"], x["RESULTADO"]) for x in r)),
            "GANHAM_SOURCE_ID": dict(Counter(tipo.get(n["CANDIDATE_ID"]) for n in novas)),
            "REUSAM_SOURCE_ID_QUE_JA_EXISTIA": len(reuso),
            "PARAM_NO_QUALIFY": dict(paradas),
            "SEM_QUALIFY_CORRIDO": sorted(ids - set(por_cand)),
            "ESTADO_DAS_NOVAS": dict(Counter(LC.estado_de(n["SOURCE_ID"]) for n in novas)),
            "NOVAS": [{"CANDIDATA_ID": n["CANDIDATE_ID"], "SOURCE_ID": n["SOURCE_ID"], "URL": n.get("URL"),
                       "TERRITORY_REASON": n.get("TERRITORY_REASON")} for n in novas],
            "PARADAS": [{"CANDIDATA_ID": cid, "TIPO": tipo.get(cid), "RESULTADO": x["RESULTADO"],
                         "PORQUE": x.get("PORQUE")} for cid, x in sorted(por_cand.items())
                        if x["RESULTADO"] != "OK"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--ensaio", action="store_true")
    ap.add_argument("--copia", action="store_true")
    ap.add_argument("--vivo", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--tambem-candidatas", action="store_true",
                    help="inclui as LinkedIn/Instagram em CANDIDATA (so QUALIFY; nada a desbloquear)")
    a = ap.parse_args(argv)
    cands = bloqueadas(a.tambem_candidatas)
    por = Counter("%s %s" % (c["TIPO"], "+".join(decisoes_de(c))) for c in cands)
    print("candidatas %s sem SOURCE_ID: %d  %s" % ("POLICY_BLOCK+CANDIDATA" if a.tambem_candidatas
                                                    else "em POLICY_BLOCK", len(cands), dict(por)))
    if not (a.aplicar or a.ensaio):
        for c in cands:
            print("  %s  %-9s %-10s %s" % (c["CANDIDATA_ID"], c["TIPO"], "+".join(decisoes_de(c)), c.get("URL")))
        return 0
    no_vivo = any(v in str(RAIZ).replace("\\", "/") for v in VIVOS)
    if a.ensaio and (no_vivo or not a.copia):
        print("RECUSADO: o ensaio corre o worker — so numa copia (--copia)")
        return 2
    if no_vivo and not (a.vivo and PARAR.exists()):
        print("RECUSADO: no vivo so com --vivo E o bot parado (%s presente)" % PARAR.name)
        return 2
    if not no_vivo and not a.copia:
        print("RECUSADO: fora do vivo, declare --copia")
        return 2
    saida = ensaio(cands) if a.ensaio else {"APLICADAS": aplicar(cands)}
    print(json.dumps({k: v for k, v in saida.items() if k not in ("NOVAS", "PARADAS", "APLICADAS")},
                     ensure_ascii=False, indent=1))
    if a.aplicar and not a.ensaio:
        print(dict(Counter(x["FEITO"] for x in saida["APLICADAS"])))
    if a.json:
        Path(a.json).write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
