"""MICRO-COLETA COM REDE REAL (VPN IT) SOBRE UMA SALA DESCARTAVEL — A4.

    py scripts/micro_coleta/micro_rede_real.py [--fontes=...] [--manter] [--ajudas-da-a4]

O mesmo caminho do ensaio offline (orquestrador -> coletor Node -> RAW -> DERIVED ->
Admission -> Sala, pelo comando do micro_coleta), mas os pedidos vao a INTERNET
pela VPN italiana. A Sala e um Postgres DESCARTAVEL (`sala_italia` numa porta
livre, migrations pela cadeia): nenhuma variavel aponta para a Sala real (54330).

LIMITES (D7 do dono: «ate 5 pedidos por site: robots + pagina + ate 3 materias»),
por PASSAGEM; com as duas passagens da prova de idempotencia, o teto por site e 10:
  * robots.txt lido AQUI antes de cada fonte (o coletor Node NAO le robots — medido
    na A4): proibida a pagina de entrada ou o caminho das materias -> a fonte nao corre;
  * MAX_TARGETS do contrato baixado para 3 SO na copia temporaria da arvore;
  * portao de egresso IT (superficie/rede.py) antes e depois de CADA fonte; se cair,
    PARA tudo e regista — nunca continua pela rede do Brasil;
  * 15 s entre fontes. Dentro de uma fonte o coletor nao espaça os pedidos (medido;
    nao se muda o coletor aqui).
US$0: nenhuma rota paga, sem login. A coorte e a do PORTAO (micro_coleta.plano).

⚠️ DESDE A A5 AS TRES AJUDAS DE CIMA SAIRAM DO CAMINHO POR OMISSAO. O robots, a pausa
entre pedidos ao mesmo host e o teto de 5 pedidos por site (D7) vivem agora DENTRO do
coletor (`coleta/italy_pilot_collect.mjs::baixar`), que e o dono do transporte. Correr
as ajudas por cima seria ter DOIS donos da mesma regra. Sem flag, este condutor:
  * NAO le robots (quem le e o coletor, por origem, uma vez por corrida);
  * NAO baixa MAX_TARGETS (o teto por host do coletor corta aos 5 pedidos);
  * NAO espera entre fontes (a pausa e por host, dentro do coletor).
Fica so o que e do condutor: o portao de egresso IT antes e depois de cada fonte, e
a Sala descartavel. `--ajudas-da-a4` repoe as tres, SO para reproduzir a A4.
Os pedidos por site passam a ler-se do resumo do coletor (`CORTESIA.PEDIDOS_POR_HOST`):
e a conta do transporte, com robots, saltos e retentativas, e nao uma soma deduzida.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "curadoria"))
import ensaio_offline as E      # noqa: E402
import micro_coleta as MC       # noqa: E402

MAX_MATERIAS = 3
PAUSA_ENTRE_FONTES = 15
AUSENCIA = "NAO SEI"


def portao_de_egresso(tentativas: int = 3, espera: int = 20) -> dict:
    """O portao, repetido SO quando a resposta e UNKNOWN (o checker nao respondeu).

    ⚠️ MEDIDO NA A5 (23/09): tres paragens em 40 min com PAIS=UNKNOWN, e em todas
    a medicao seguinte (16 s depois) deu IT — e o proprio coletor, na mesma
    corrida, mediu IT no ipinfo. UNKNOWN e o checker calado, nao a VPN noutro
    pais. Por isso: UNKNOWN mede-se outra vez (ate `tentativas`, `espera` s
    entre elas); UNKNOWN NUNCA passa; um pais != IT para logo, sem repetir.
    Todas as medicoes ficam no resultado, em `MEDICOES`.
    """
    medicoes = []
    for i in range(tentativas):
        if i:
            time.sleep(espera)
        m = _uma_medicao_de_egresso()
        medicoes.append({k: m[k] for k in ("GATE", "PAIS", "QUANDO")})
        if m["PAIS"] not in ("UNKNOWN", AUSENCIA):
            break
    m["MEDICOES"] = medicoes
    return m


def _uma_medicao_de_egresso() -> dict:
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"],
                       cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=90)
    try:
        d = json.loads(r.stdout[r.stdout.index("{"):])
    except ValueError:
        d = {"EGRESS_GATE": "BLOCKED", "PORQUE_BLOQUEADO": "saida ilegivel: " + r.stdout[-200:]}
    return {"GATE": d.get("EGRESS_GATE"), "PAIS": d.get("EGRESS_COUNTRY_CODE", AUSENCIA),
            "IP": d.get("EGRESS_IP") or d.get("IP"), "QUANDO": E.agora()}


def prefixo_das_materias(link_pattern: str) -> str:
    """O caminho literal que o padrao das materias exige (ex.: '/news/'), para o robots."""
    s = re.sub(r"^\^?https\?://", "", link_pattern or "")
    s = s.replace(r"(www\.)?", "")
    s = s.split("/", 1)[1] if "/" in s else ""
    lit = re.split(r"[\[\(\?\*\+\{\$\\|.]", s.replace(r"\.", "."), maxsplit=1)[0]
    return "/" + lit


def robots(contrato: dict) -> dict:
    """Le o robots do site (a peca da casa, gate_de_rota.robots_de) e decide."""
    import gate_de_rota as GR                                    # noqa: PLC0415
    aq = contrato.get("ACQUISITION") or {}
    indice = aq.get("INDEX_URL") or ""
    p = urlsplit(indice)
    rp, txt = GR.robots_de(p.hostname or "")
    amostra = "%s://%s%sexemplo-de-materia" % (p.scheme, p.hostname,
                                               prefixo_das_materias(aq.get("LINK_PATTERN", "")))
    ok_i, ok_m = GR.permitido(indice, rp), GR.permitido(amostra, rp)
    return {"INDEX_URL": indice, "SONDA_MATERIA": amostra, "INDICE_PERMITIDO": ok_i,
            "MATERIAS_PERMITIDAS": ok_m, "ROBOTS": (txt or "")[:120].replace("\n", " "),
            "PERMITE": ok_i and ok_m}


def limitar_contratos(arvore: Path) -> dict:
    """MAX_TARGETS <= 3 so na copia temporaria (D7). Devolve o que foi baixado."""
    f = arvore / "regras" / "italy_contracts_onboarded.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    mudados = {}
    for c in d["FONTES"]:
        # setdefault e nao `or {}`: um ACQUISITION vazio e falso, e `or {}` dava um
        # dicionario solto — o teto nao ficava gravado (apanhado pelo teste).
        aq = c.setdefault("ACQUISITION", {})
        antes = aq.get("MAX_TARGETS")
        if not isinstance(antes, int) or antes > MAX_MATERIAS:
            aq["MAX_TARGETS"] = MAX_MATERIAS
            mudados[c["SOURCE_ID"]] = antes
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return mudados


def passagem(nome, fontes, arvore, env, saida, contratos, robots_lidos, log, ajudas=False):
    corridas, parou = [], None
    for i, s in enumerate(fontes):
        if i and ajudas:
            time.sleep(PAUSA_ENTRE_FONTES)
        antes = portao_de_egresso()
        if antes["GATE"] != "PASS":
            parou = {"FONTE": s, "EGRESSO": antes, "PORQUE": "portao de egresso caiu antes da fonte"}
            log(f"PARAR {nome}: egresso {antes} antes de {s}")
            break
        if ajudas and s not in robots_lidos:
            robots_lidos[s] = robots(contratos.get(s) or {})
        rb = robots_lidos.get(s) or {"PERMITE": True}
        if not rb["PERMITE"]:
            corridas.append({"SOURCE_ID": s, "CORREU": False, "PORQUE": "ROBOTS_PROIBE", "ROBOTS": rb,
                             "EGRESSO_ANTES": antes})
            log(f"{nome} {s} ROBOTS_PROIBE")
            continue
        try:
            gate = MC.GATE.avaliar(s, **MC.GATE._contexto())["MOTIVO"]
        except Exception as ex:                                    # noqa: BLE001
            gate = "ERRO:%s" % type(ex).__name__
        cmd = MC.comando(s)
        medida = saida / f"rede-{nome}-{s}.json"
        x = subprocess.run([sys.executable, "medidas/corrida_sem_rede.py", f"--saida={medida}", "--"]
                           + cmd[2:], cwd=str(arvore), env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=1800)
        (saida / f"saida-{nome}-{s}.txt").write_text(x.stdout + "\n--- ERR\n" + x.stderr, encoding="utf-8")
        depois = portao_de_egresso()
        m = re.search(r"CORRIDA (\S+) · (\S+)", x.stdout)
        corridas.append({"SOURCE_ID": s, "CORREU": True, "CODIGO": x.returncode,
                         "STATUS": m.group(1) if m else AUSENCIA, "RUN_ID": m.group(2) if m else AUSENCIA,
                         "GATE_NO_INSTANTE": gate,
                         "EGRESSO_ANTES": {"PAIS": antes["PAIS"], "GATE": antes["GATE"], "MEDICOES": antes.get("MEDICOES")},
                         "EGRESSO_DEPOIS": {"PAIS": depois["PAIS"], "GATE": depois["GATE"],
                                            "MEDICOES": depois.get("MEDICOES")}})
        log(f"{nome} {s} {corridas[-1]['STATUS']} {corridas[-1]['RUN_ID']} egresso {antes['PAIS']}->{depois['PAIS']}")
        if depois["GATE"] != "PASS":
            parou = {"FONTE": s, "EGRESSO": depois, "PORQUE": "portao de egresso caiu depois da fonte"}
            log(f"PARAR {nome}: egresso {depois} depois de {s}")
            break
    return corridas, parou


def por_site(corridas, runs, obs, robots_lidos) -> dict:
    """Pedidos reais e falhas por site, sem esconder codigo nenhum.

    Desde a A5 o coletor conta ele proprio os pedidos HTTP por host (`CORTESIA` no
    resumo da corrida). Quando essa conta existe, ela manda: `PEDIDOS_POR_HOST`,
    `MAX_POR_HOST` e as `RECUSAS` da cortesia vem de la. ROBOTS/INDICE/MATERIAS
    continuam, para comparar com a A4.
    """
    out = {}
    for c in corridas:
        s = c["SOURCE_ID"]
        linha = out.setdefault(s, {"ROBOTS": 0, "INDICE": 0, "MATERIAS": 0, "FALHAS": []})
        if s in robots_lidos and not linha.get("_robots_contado"):
            linha["ROBOTS"] = 1
            linha["_robots_contado"] = True
        for r in runs:
            if r.get("RUN_ID") == c.get("RUN_ID"):
                k = r.get("contadores") or {}
                linha["INDICE"] += int(k.get("INDEX_REQUESTS") or 0)
                linha["MATERIAS"] += int(k.get("DETAIL_REQUESTS") or 0)
                cort = r.get("CORTESIA")
                if isinstance(cort, dict):
                    linha["ROBOTS"] += int(k.get("ROBOTS_REQUESTS") or 0)
                    ph = linha.setdefault("PEDIDOS_POR_HOST", {})
                    for h, n in (cort.get("PEDIDOS_POR_HOST") or {}).items():
                        ph[h] = ph.get(h, 0) + int(n)
                    linha.setdefault("RECUSAS", []).extend(
                        {"URL": x.get("URL"), "MOTIVO": x.get("MOTIVO")} for x in cort.get("RECUSAS") or [])
                    linha["ROBOTS_ESTADO"] = {o: v.get("ESTADO") for o, v in (cort.get("ROBOTS") or {}).items()}
        for o in obs:
            if o.get("RUN_ID") == c.get("RUN_ID") and o.get("HEALTH_STATE") == "FAILED":
                linha["FALHAS"].append({"URL": o.get("SOURCE_URL"), "RESULTADO": o.get("OBSERVATION_RESULT"),
                                        "MOTIVO": str(o.get("motivo") or AUSENCIA)[:80]})
    for s, l in out.items():
        l.pop("_robots_contado", None)
        if "PEDIDOS_POR_HOST" in l:
            # A conta do transporte: inclui saltos e retentativas, que a soma nao ve.
            l["TOTAL"] = sum(l["PEDIDOS_POR_HOST"].values())
            l["MAX_POR_HOST"] = max(l["PEDIDOS_POR_HOST"].values(), default=0)
        else:
            l["TOTAL"] = l["ROBOTS"] + l["INDICE"] + l["MATERIAS"]
    return out


def quarentena(livro: Path, run_ids) -> int:
    if not livro.exists():
        return 0
    d = json.loads(livro.read_text(encoding="utf-8"))
    return sum(1 for x in d.get("DECISOES", []) if x.get("corrida") in run_ids
               and (x.get("evidencia") or {}).get("estado") == "QUARENTENA")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    fontes = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--fontes=")), None)
    manter = "--manter" in argv
    ajudas = "--ajudas-da-a4" in argv
    D = Path(os.environ.get("TEMP", "/tmp")) / ("micro-rede-real-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    saida = D / "saida"
    saida.mkdir(parents=True)
    diario = saida / "DIARIO.txt"

    def log(t):
        print(t, flush=True)
        with diario.open("a", encoding="utf-8") as f:
            f.write(E.agora() + " " + t + "\n")

    resultado = {"INICIO": E.agora(), "PASTA": str(D),
                 "AJUDAS_EXTERNAS": "A4 (robots no condutor, MAX_TARGETS 3, 15 s entre fontes)"
                 if ajudas else "NENHUMA — robots, pausa e teto sao do coletor (A5)"}
    resultado["EGRESSO_INICIO"] = portao_de_egresso()
    log(f"egresso inicio {resultado['EGRESSO_INICIO']}")
    if resultado["EGRESSO_INICIO"]["GATE"] != "PASS":
        resultado["PAROU"] = "portao de egresso BLOCKED no inicio: nada foi pedido a rede"
        (saida / "MICRO-REDE-REAL.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
        log(resultado["PAROU"])
        return 2
    plano = MC.plano()
    if fontes is None:
        fontes = [l["SOURCE_ID"] for l in plano["LINHAS"] if l["ESTADO"] == "PRONTA"]
    fontes = [s for s in fontes if MC.universo_de(s) != "T12"]          # D9: T12 fora
    resultado.update({"COORTE": plano["COORTE"], "FONTES": fontes, "N": len(fontes),
                      "BLOQUEADAS_PELA_CAPACIDADE": [{"SOURCE_ID": l["SOURCE_ID"], "FALTA": l["FALTA"]}
                                                     for l in plano["LINHAS"] if l["ESTADO"] != "PRONTA"],
                      "G1_FORA_DO_PORTAO": plano.get("G1_FORA_DO_PORTAO")})
    log(f"coorte do portao: {len(fontes)} {fontes}")
    arvore = D / "arvore"
    subprocess.run(["git", "worktree", "add", "--detach", str(arvore), "HEAD"], cwd=RAIZ,
                   check=True, capture_output=True)
    resultado["MAX_TARGETS_BAIXADO"] = limitar_contratos(arvore) if ajudas else "NAO — teto por host do coletor"
    contratos = {c["SOURCE_ID"]: c for c in json.loads(
        (arvore / "regras" / "italy_contracts_onboarded.json").read_text(encoding="utf-8"))["FONTES"]}
    base = E.Base(D / "pg")
    (D / "curl").mkdir()           # CURL_HOME vazio: nenhum _curlrc de ninguem desvia a rede
    (D / "ops").mkdir()
    env = {k: v for k, v in os.environ.items()
           if k not in ("BANCO_DESCARTAVEL_URL", "SUPABASE_DB_URL", "HTTPS_PROXY", "HTTP_PROXY")}
    env.update({"CURL_HOME": str(D / "curl"), "ITALY_OPS_ROOT": str(D / "ops"),
                "SINTONIA_COLLECTION_DSN": base.url, "SINTONIA_SALA_DSN": base.url,
                "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": base.exe("psql"),
                # ⚠️ FORA da arvore: a bancada e OPERACIONAL (SINTONIA_COLLECTION_DSN),
                # e raiz_do_armazem_local recusa armazem operacional dentro do repo (BC4).
                "SINTONIA_ARMAZEM_RAIZ": str(D / "armazem"), "PYTHONUTF8": "1",
                "PATH": str(E.PG_BIN) + os.pathsep + os.environ.get("PATH", "")})
    led = D / "ops" / "data" / "collection-ledger" / "italy"
    robots_lidos: dict = {}
    try:
        resultado["BASE"] = base.subir(arvore, env)
        os.environ.update({k: env[k] for k in ("SINTONIA_SALA_DSN", "SINTONIA_PSQL_EXE", "ITALY_OPS_ROOT",
                                               "SINTONIA_ARMAZEM_RAIZ")})
        antes = E.contagens()
        c1, parou1 = passagem("1a", fontes, arvore, env, saida, contratos, robots_lidos, log, ajudas)
        depois1 = E.contagens()
        runs1 = [c["RUN_ID"] for c in c1 if c.get("RUN_ID") not in (None, AUSENCIA)]
        rel = MC.relatorio(runs1, corridas=[c for c in c1 if c.get("CORREU")],
                           livro=arvore / "data" / "samples" / "LIVRO-DE-DECISOES.json",
                           armazem=D / "armazem", saida=saida, ledger=led) if runs1 else None
        obs1 = E.ler_ndjson(led / "observations.ndjson")
        runs_nd = E.ler_ndjson(led / "runs.ndjson")
        resultado["PRIMEIRA"] = {
            "CORRIDAS": c1, "PAROU": parou1, "SALA_ANTES": antes, "SALA_DEPOIS": depois1,
            "SALA_DELTA": depois1["sala_de_espera"] - antes["sala_de_espera"],
            "CRITERIOS": ({k: (v.get("ESTADO") or ("PASS" if v["PASSA"] else "FAIL"))
                           for k, v in rel["CRITERIOS"].items()} if rel else None),
            "CONTAGENS": ({k: v for k, v in rel["CONTAGENS"].items() if k != "TENTATIVAS"} if rel else None),
            "ADMISSION": (rel["CRITERIOS"]["C7_PROPORCAO_POR_FONTE_E_CLASSE"]["POR_FONTE"] if rel else None),
            "C8": ({k: v for k, v in rel["CRITERIOS"]["C8_DUAS_PERGUNTAS"].items()
                    if k != "ITENS_DO_GABARITO"} if rel else None),
            "QUARENTENA": quarentena(arvore / "data" / "samples" / "LIVRO-DE-DECISOES.json", runs1),
            "POR_SITE": por_site(c1, runs_nd, obs1, robots_lidos)}
        if parou1 is None:
            antes2 = E.contagens()
            c2, parou2 = passagem("2a", fontes, arvore, env, saida, contratos, robots_lidos, log, ajudas)
            runs2 = {c["RUN_ID"] for c in c2 if c.get("RUN_ID") not in (None, AUSENCIA)}
            obs_t = E.ler_ndjson(led / "observations.ndjson")
            runs_t = E.ler_ndjson(led / "runs.ndjson")
            sp = E.segunda_passagem(obs1, [o for o in obs_t if o.get("RUN_ID") in runs2],
                                    [r for r in runs_t if r.get("RUN_ID") in runs2], [], antes2, E.contagens())
            sp["CORRIDAS"] = c2
            sp["PAROU"] = parou2
            sp["POR_SITE"] = por_site(c2, runs_t, obs_t, {})
            sp["SALA_ITENS_EM_MAIS_DE_UMA_CORRIDA"] = [x[0] for x in MC.sql(
                "select item_id from sala_de_espera group by item_id, universo"
                " having count(distinct run_id) > 1 order by 1")]
            resultado["SEGUNDA"] = sp
    finally:
        resultado["EGRESSO_FIM"] = portao_de_egresso()
        log(f"egresso fim {resultado['EGRESSO_FIM']}")
        base.descer()
        if not manter:
            subprocess.run(["git", "worktree", "remove", "--force", str(arvore)], cwd=RAIZ,
                           capture_output=True)
        resultado["FIM"] = E.agora()
        (saida / "MICRO-REDE-REAL.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1,
                                                               default=str), encoding="utf-8")
        log("escrito: %s" % (saida / "MICRO-REDE-REAL.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
