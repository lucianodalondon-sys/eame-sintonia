# -*- coding: utf-8 -*-
"""A ONDA WEB DA BIG COLLECTION (2.a onda em diante), UMA fonte de cada vez, pela porta canonica.

    py ferramentas/big_collection/onda_web.py --so-plano [--coorte=...] [--saida=...]
    py ferramentas/big_collection/onda_web.py --correr --sha256=<da coorte congelada> --saida=<pasta nova>

O que muda em relacao ao `bc5_big_collection.py` (a 1.a onda, que fica como registo):

  1. A COORTE VEM DO LUGAR OFICIAL. Le `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json`
     DESTA arvore, confere que o ficheiro no disco e byte a byte o do commit (`git show HEAD:...`)
     e, para correr, que o sha256 e o que quem autoriza declarou (`--sha256=`) e que o ESTADO e
     CONGELADA. O `C:\\bc\\COORTE-BIG-COLLECTION.json` (fora do Git) deixa de ser lido.
  2. O TETO E POR DOMINIO E PELA ONDA INTEIRA (D38). Cada onda nomeia um livro novo
     (`<saida>/TETO-ONDA.json`) em SINTONIA_TETO_ONDA; o transporte (`coleta/italy_pilot_collect.mjs`,
     o dono unico do teto) soma nele os pedidos por dominio registavel de todas as corridas.
     Uma fonte cujo dominio ja gastou o teto NAO corre: fica com PORQUE=TETO_DOMINIO, e isso nao e
     FAILED (nao conta para o disjuntor das 3 seguidas). Separar fontes em ondas diferentes para
     ganhar pedidos contornava a protecao: o livro e um por onda e a onda e uma.
  3. `--so-plano`: sem rede e sem Sala. Pergunta ao plano do runbook (`micro_coleta.plano`) se cada
     fonte continua PRONTA, preve os pedidos por fonte pelo que a 1.a onda gastou (sem historico, o
     teto inteiro) e reparte o teto por dominio pela ordem da coorte.

Disjuntores (BIG-COLLECTION-RUNBOOK §6), os mesmos da 1.a onda, mais um:
  egresso sai de IT (antes/depois) · a Sala desce · corrida > 30 min · 3 fontes seguidas FAILED ·
  C6 != PASS · C4 com cadeia partida · pedidos por SITE acima do teto numa corrida ·
  NOVO: pedidos por DOMINIO acima do teto no livro da onda -> PARA TUDO
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[2]
COORTE_OFICIAL = "ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json"
HISTORICO_1A_ONDA = RAIZ / "ferramentas/big_collection/BC5-BIG-COLLECTION-1A-ONDA.json"
TETO = 5                                   # D7/D38; o transporte le SINTONIA_TETO_POR_HOST, com o mesmo padrao
AVISO = Path(r"C:\Users\London1\auditoria-madrugada\bc4-aviso-vivo.txt")
LEDGER = RAIZ / "data/collection-ledger/italy/runs.ndjson"


def agora():
    return datetime.now().strftime("%H:%M:%S")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ── o dominio registavel: o MESMO do transporte (um so dono da regra) ────────
def dominios(hosts: list[str]) -> dict:
    """Pergunta ao transporte (node) o dominio registavel de cada host. Nao ha segunda copia da regra."""
    r = subprocess.run(["node", "--input-type=module", "-e",
                        "const m = await import('./coleta/italy_pilot_collect.mjs');"
                        "const hs = JSON.parse(process.argv[1]); const o = {};"
                        "for (const h of hs) o[h] = m.dominioRegistavel(h); console.log(JSON.stringify(o));",
                        json.dumps(hosts)], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=120)
    if r.returncode:
        raise SystemExit("o transporte nao respondeu o dominio registavel: " + r.stderr[-400:])
    return json.loads(r.stdout.strip().splitlines()[-1])


# ── a coorte, do lugar oficial, conferida ────────────────────────────────────
def coorte_oficial(caminho: str = COORTE_OFICIAL, *, exigir_congelada: bool, sha_declarado: str | None) -> dict:
    disco = (RAIZ / caminho).read_bytes()
    git = subprocess.run(["git", "show", "HEAD:%s" % caminho], cwd=RAIZ, capture_output=True)
    if git.returncode:
        raise SystemExit("COORTE_FORA_DO_GIT: %s nao esta no commit desta arvore" % caminho)
    # O Windows pode devolver o blob com \n e o disco com \r\n: compara-se o conteudo JSON E os bytes.
    igual_bytes = sha256(disco) == sha256(git.stdout)
    igual_json = json.loads(disco) == json.loads(git.stdout)
    if not igual_json:
        raise SystemExit("COORTE_ALTERADA_FORA_DO_COMMIT: o ficheiro no disco nao e o do commit")
    c = json.loads(disco)
    impressao = sha256(git.stdout)
    if sha_declarado and sha_declarado != impressao:
        raise SystemExit("COORTE_SHA256_DIFERENTE: declarado %s, commit %s" % (sha_declarado, impressao))
    if exigir_congelada and c.get("ESTADO") != "CONGELADA":
        raise SystemExit("COORTE_NAO_CONGELADA: ESTADO=%s — a onda so corre sobre uma coorte CONGELADA (G3)"
                         % c.get("ESTADO"))
    return {"COORTE": c, "SHA256_DO_COMMIT": impressao, "BYTES_IGUAIS_AO_COMMIT": igual_bytes,
            "HEAD": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                                   text=True).stdout.strip()}


def historico_por_fonte() -> dict:
    if not HISTORICO_1A_ONDA.exists():
        return {}
    d = json.loads(HISTORICO_1A_ONDA.read_text(encoding="utf-8"))
    return {f["SOURCE_ID"]: sum((f.get("PEDIDOS_POR_SITE") or {}).values()) for f in d.get("FONTES", [])}


def repartir(linhas: list[dict], teto: int = TETO) -> list[dict]:
    """Reparte o teto por dominio pela ordem da coorte. Puro: sem rede, sem ficheiros."""
    gasto = {}
    for l in linhas:
        d = l["DOMINIO"]
        resta = teto - gasto.get(d, 0)
        prev = l["PEDIDOS_PREVISTOS"]
        if resta <= 0:
            l.update(PEDIDOS_NA_ONDA=0, PORQUE="TETO_DOMINIO", NOTA="o dominio %s ja gastou %d na onda" % (d, teto))
        else:
            dados = min(prev, resta)
            l.update(PEDIDOS_NA_ONDA=dados, PORQUE=None if dados == prev else "TETO_DOMINIO_PARCIAL",
                     NOTA=None if dados == prev else "previa %d, cabem %d" % (prev, dados))
            gasto[d] = gasto.get(d, 0) + dados
    return linhas


def so_plano(caminho: str, saida: Path | None) -> dict:
    oficial = coorte_oficial(caminho, exigir_congelada=False, sha_declarado=None)
    c = oficial["COORTE"]
    fontes = [(x["SOURCE_ID"], x.get("INDEX_URL") or "") for x in c["COORTE"]]
    hosts = sorted({urlparse(u).hostname or "" for _, u in fontes if u})
    dom = dominios(hosts)
    hist = historico_por_fonte()
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import micro_coleta as M                                  # noqa: E402 — o plano do runbook (sem rede)
    p = M.plano([s for s, _ in fontes])
    estado = {l["SOURCE_ID"]: l for l in p["LINHAS"]}
    linhas = []
    for s, u in fontes:
        h = urlparse(u).hostname or ""
        linhas.append({"SOURCE_ID": s, "INDEX_URL": u, "HOST": h, "DOMINIO": dom.get(h, h),
                       "PLANO_AGORA": estado.get(s, {}).get("ESTADO", "NAO_MEDIDA"),
                       "FALTA": estado.get(s, {}).get("FALTA"),
                       "PEDIDOS_PREVISTOS": hist.get(s, TETO),
                       "PREVISAO_VEM_DE": "1.a onda (BC5)" if s in hist else "sem historico: o teto inteiro"})
    repartir(linhas)
    por_dom = {}
    for l in linhas:
        por_dom[l["DOMINIO"]] = por_dom.get(l["DOMINIO"], 0) + l["PEDIDOS_NA_ONDA"]
    out = {"DATASET": "ONDA-WEB-SO-PLANO", "GERADO_EM": datetime.now().astimezone().isoformat(timespec="seconds"),
           "ARVORE": oficial["HEAD"], "COORTE_FICHEIRO": caminho, "COORTE_SHA256_DO_COMMIT": oficial["SHA256_DO_COMMIT"],
           "COORTE_ESTADO": c.get("ESTADO"), "PODE_CORRER": c.get("ESTADO") == "CONGELADA",
           "TETO_POR_DOMINIO_NA_ONDA": TETO, "FONTES": len(linhas),
           "CORREM": sum(1 for l in linhas if l["PORQUE"] != "TETO_DOMINIO"),
           "SALTAM_POR_TETO_DOMINIO": [l["SOURCE_ID"] for l in linhas if l["PORQUE"] == "TETO_DOMINIO"],
           "PARCIAIS": [l["SOURCE_ID"] for l in linhas if l["PORQUE"] == "TETO_DOMINIO_PARCIAL"],
           "PEDIDOS_POR_DOMINIO": por_dom, "MAXIMO_POR_DOMINIO": max(por_dom.values() or [0]),
           "PEDIDOS_TOTAL_PREVISTO": sum(por_dom.values()),
           "PLANO_AGORA_NAO_PRONTAS": [l["SOURCE_ID"] for l in linhas if l["PLANO_AGORA"] != "PRONTA"],
           "LINHAS": linhas}
    if saida:
        saida.mkdir(parents=True, exist_ok=True)
        (saida / "ONDA-WEB-SO-PLANO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ── as duas decisoes do teto na onda, puras (testaveis sem rede) ─────────────
def ler_livro(livro: Path) -> dict:
    if not livro.exists():
        return {}
    return json.loads(livro.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"]   # ilegivel rebenta: nao e vazio


def antes_da_fonte(livro: Path, dominio: str) -> str | None:
    """TETO_DOMINIO se o dominio desta fonte ja gastou o teto na onda: a fonte nao corre."""
    return "TETO_DOMINIO" if ler_livro(livro).get(dominio, 0) >= TETO else None


def disjuntor_de_dominio(livro_agora: dict) -> str | None:
    """Se o livro da onda passou do teto em algum dominio, o transporte falhou: PARA TUDO."""
    acima = {d: v for d, v in livro_agora.items() if v > TETO}
    return "PEDIDOS_POR_DOMINIO_ACIMA_DO_TETO_NA_ONDA %s" % acima if acima else None


# ── correr (a unica parte com rede; exige coorte CONGELADA e o sha256 declarado) ──
def correr(caminho: str, sha: str, saida: Path) -> int:
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import micro_coleta as M                                  # noqa: E402
    import ensaio_offline as E                                # noqa: E402
    oficial = coorte_oficial(caminho, exigir_congelada=True, sha_declarado=sha)
    falta = M.precondicoes()
    if falta:
        print("PRECONDICOES", falta)
        return 2
    saida.mkdir(parents=True, exist_ok=True)
    livro = saida / "TETO-ONDA.json"
    os.environ["SINTONIA_TETO_ONDA"] = str(livro)             # herdado por orquestrador -> executor -> node
    fontes = [(x["SOURCE_ID"], x.get("INDEX_URL") or "") for x in oficial["COORTE"]["COORTE"]]
    dom = dominios(sorted({urlparse(u).hostname or "" for _, u in fontes if u}))
    foto = lambda: {k: v["LINHAS"] for k, v in E.fotografia().items()}      # noqa: E731
    estado = {"INICIO": agora(), "COORTE_SHA256": oficial["SHA256_DO_COMMIT"], "ARVORE": oficial["HEAD"],
              "LIVRO_DA_ONDA": str(livro), "SALA_INICIO": foto(), "FONTES": [], "PAROU": None}
    grava = lambda: (saida / "ONDA-WEB-ESTADO.json").write_text(                # noqa: E731
        json.dumps(estado, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    falhas_seguidas = 0
    for i, (s, u) in enumerate(fontes, 1):
        d = dom.get(urlparse(u).hostname or "", "")
        if antes_da_fonte(livro, d):
            gasto = ler_livro(livro).get(d, 0)
            estado["FONTES"].append({"N": i, "SOURCE_ID": s, "HORA": agora(), "CORREU": False,
                                     "PORQUE_NAO_CORREU": "TETO_DOMINIO", "DOMINIO": d, "GASTO_NA_ONDA": gasto})
            grava()
            print("%02d %s TETO_DOMINIO %s=%d" % (i, s, d, gasto), flush=True)
            continue                                          # nao e FAILED: nao mexe em falhas_seguidas
        antes = foto()
        t0 = time.time()
        r = M.correr([s], autorizado=True, saida=saida / s)
        seg = round(time.time() - t0)
        depois = foto()
        c = (r.get("CORRIDAS") or [{}])[0]
        C = (r.get("RELATORIO") or {}).get("CRITERIOS") or {}
        cort = {}
        for l in reversed(LEDGER.read_text(encoding="utf-8").splitlines() if LEDGER.exists() else []):
            try:
                x = json.loads(l)
            except ValueError:
                continue
            if x.get("RUN_ID") == c.get("RUN_ID"):
                cort = x.get("CORTESIA") or {}
                break
        livro_agora = ler_livro(livro)
        linha = {"N": i, "SOURCE_ID": s, "HORA": agora(), "SEGUNDOS": seg, "CORREU": c.get("CORREU"),
                 "STATUS": c.get("STATUS"), "RUN_ID": c.get("RUN_ID"), "PORQUE_NAO_CORREU": c.get("PORQUE"),
                 "GATE": c.get("GATE_NO_INSTANTE"), "DOMINIO": d,
                 "EGRESSO": [(c.get("EGRESSO_ANTES") or {}).get("PAIS"), (c.get("EGRESSO_DEPOIS") or {}).get("PAIS")],
                 "PEDIDOS_POR_SITE": cort.get("PEDIDOS_POR_HOST"), "PEDIDOS_POR_DOMINIO": cort.get("PEDIDOS_POR_DOMINIO"),
                 "LIVRO_DA_ONDA": livro_agora, "SALA_ANTES": antes, "SALA_DEPOIS": depois,
                 "C4": C.get("C4_PROVENIENCIA_COMPLETA") or {},
                 "CRITERIOS": {k: (v.get("ESTADO") or ("PASS" if v.get("PASSA") else "FAIL")) for k, v in C.items()}}
        estado["FONTES"].append(linha)
        grava()
        print("%02d %s %s %ss livro %s" % (i, s, linha["STATUS"], seg, livro_agora), flush=True)
        parar = None
        if c.get("CORREU") and linha["EGRESSO"] != ["IT", "IT"]:
            parar = "EGRESSO_SAIU_DE_IT %s" % linha["EGRESSO"]
        elif c.get("PORQUE") == "EGRESSO_NAO_IT":
            parar = "EGRESSO_NAO_IT antes da fonte"
        elif any(depois[k] < antes[k] for k in antes):
            parar = "SALA_DESCEU"
        elif seg > 1800:
            parar = "CORRIDA_MAIS_DE_30_MIN"
        elif C and C.get("C6_ZERO_BYPASS", {}).get("PASSA") is False:
            parar = "C6_BYPASS"
        elif C and linha["C4"].get("SALA_LINHAS") != linha["C4"].get("SALA_COM_CADEIA_INTEIRA"):
            parar = "PROVENIENCIA_PARTIDA"
        elif any(v > TETO for v in (cort.get("PEDIDOS_POR_HOST") or {}).values()):
            parar = "PEDIDOS_POR_SITE_ACIMA_DO_TETO %s" % cort.get("PEDIDOS_POR_HOST")
        elif disjuntor_de_dominio(livro_agora):
            parar = disjuntor_de_dominio(livro_agora)
        falhas_seguidas = falhas_seguidas + 1 if linha["STATUS"] == "FAILED" else 0
        if falhas_seguidas >= 3:
            parar = "TRES_FONTES_SEGUIDAS_FAILED"
        if parar:
            estado["PAROU"] = {"FONTE": s, "PORQUE": parar, "HORA": agora()}
            grava()
            with open(AVISO, "a", encoding="utf-8") as f:
                f.write("\nONDA-WEB -> COORDENADOR (%s): DISJUNTOR na fonte %d (%s): %s. PARADO.\n" % (agora(), i, s, parar))
            print("PAROU", parar, flush=True)
            return 1
    estado["FIM"] = agora()
    estado["SALA_FIM"] = foto()
    grava()
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    caminho = arg.get("coorte", COORTE_OFICIAL)
    saida = Path(arg["saida"]) if arg.get("saida") else None
    if "--so-plano" in argv:
        out = so_plano(caminho, saida)
        print(json.dumps({k: v for k, v in out.items() if k != "LINHAS"}, ensure_ascii=False, indent=1))
        return 0
    if "--correr" in argv:
        if not arg.get("sha256") or not saida:
            raise SystemExit("--correr exige --sha256=<da coorte congelada> e --saida=<pasta nova da onda>")
        if (saida / "TETO-ONDA.json").exists() and "--retomar" not in argv:
            raise SystemExit("LIVRO_DA_ONDA_JA_EXISTE: %s — uma onda nova tem pasta nova; para retomar a MESMA onda, --retomar"
                             % (saida / "TETO-ONDA.json"))
        return correr(caminho, arg["sha256"], saida)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
