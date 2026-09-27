"""T2-REGUA · prova D29 pela porta canónica — 5 canais x 2 vídeos, banco descartável próprio.

    py C:/Users/London1/regua-t2-prova/prova.py --subir | --correr | --medir | --descer

Copia: worktree C:
egua-t2-base no commit da regua (nao a arvore de trabalho).
Banco descartavel proprio (pasta cluster-pai aqui). Cada fonte: portao de egresso IT
ANTES e DEPOIS; orquestrador com universo=T2 (o universo vem do PEDIDO — uma fonte T3
pedida como T2 e a pergunta D29 feita a um boletim fitossanitario).
"""
import json
import os
import subprocess
import sys
import tempfile
import time

WT = "C:/regua-t2-base"
AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "banco.json")
RES = os.path.join(AQUI, "resultados.json")
PG = r"C:\Users\London1\orca\pgtmp\pgsql\bin"
APELIDO = {"T2": "clima", "T5": "ciencia", "T7": "cooperativas", "T10": "mercado", "T12": "politica"}
sys.path.insert(0, os.path.join(WT, "provas"))
os.chdir(WT)


def ler(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def gravar(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def subir():
    tempfile.tempdir = os.path.join(AQUI, "cluster-pai")      # pasta PROPRIA (outro processo apaga %TEMP%\pg-prova-cli-*)
    os.makedirs(tempfile.tempdir, exist_ok=True)
    import a_porta_cli_liga_o_banco as P
    b = P.Bancada()
    url = b.subir()
    cod, n, saida, erro = P._migrations(url, dict(os.environ))
    gravar(ESTADO, {"URL": url, "CLUSTER": b.cluster, "PORTO": b.porto, "PGBIN": b.pgbin, "MIGRACOES": n, "RC": cod})
    print("BANCO", url, "migracoes", n, "rc", cod)


def descer():
    e = ler(ESTADO, None)
    if not e:
        print("sem banco")
        return
    subprocess.run([os.path.join(PG, "pg_ctl.exe"), "-D", e["CLUSTER"], "-w", "-m", "fast", "stop"],
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("DESLIGADO", e["CLUSTER"], "pid_file:", os.path.exists(os.path.join(e["CLUSTER"], "postmaster.pid")))


def egresso():
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return "\"EGRESS_GATE\": \"PASS\"" in r.stdout, r.stdout[-400:]


def ambiente(url):
    e = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
             BANCO_DESCARTAVEL_URL=url, SINTONIA_PSQL_EXE=os.path.join(PG, "psql.exe"),
             SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url,
             SINTONIA_LIBS=r"C:\Users\London1\AppData\Local\Programs\Python\Python312\Lib\site-packages",
             SINTONIA_ASR_DEVICE="AUTO",
             PYTHONPATH=os.pathsep.join([os.path.join(WT, ".sintonia-libs"), r"C:\Users\London1\soc5-libs"]))
    e.pop("SINTONIA_COLLECTION_DSN", None)
    e["PATH"] = PG + os.pathsep + e.get("PATH", "")
    return e


FONTES = [  # (fonte, porque)
    ("IT-T2-001", "ARPAE boletim agrometeorologico semanal (PDF) - esperado SIM"),
    ("IT-T2-002", "ARPAV Agrometeo Informa (PDF) - esperado SIM"),
    ("IT-T3-002", "Campania servico fitossanitario regional - esperado SIM"),
    ("IT-T3-010", "APOL boletim mosca da oliveira - esperado SIM"),
    ("IT-T2-051", "ARPAE pagina (1.a onda: oferta de emprego) - controlo, esperado nao SIM"),
    ("IT-T2-034", "ARPA Marche (1.a onda: jornadas de polen) - controlo, esperado nao SIM"),
]


def correr(maximo):
    e = ler(ESTADO, None)
    res = ler(RES, {})
    feitos = 0
    for fonte, porque in FONTES:
        if fonte in res or feitos >= maximo:
            continue
        ok, txt = egresso()
        if not ok:
            print("EGRESSO NAO E IT — parado antes de", fonte)
            gravar(RES, res)
            return
        cmd = [sys.executable, "orquestrador/orquestrador.py", "colete clima da italia",
               "--filtro", "pais=IT", "--filtro", "fonte=%s" % fonte, "--filtro", "universo=T2"]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=ambiente(e["URL"]), timeout=900)
        ok2, _ = egresso()
        import re
        m = re.search(r"(XX|IT)-T\d+-2026-\d\d-\d\d-\d{6}-[0-9a-f]+", r.stdout or "")
        res[fonte] = {"SOURCE_ID": fonte, "PORQUE": porque, "RC": r.returncode,
                      "RUN_ID": m.group(0) if m else None, "SEGUNDOS": round(time.time() - t0, 1),
                      "EGRESSO_DEPOIS_IT": ok2, "SAIDA_FIM": (r.stdout or "")[-3000:],
                      "ERRO_FIM": (r.stderr or "")[-1500:]}
        gravar(RES, res)
        feitos += 1
        print(fonte, "rc", r.returncode, "run", res[fonte]["RUN_ID"], "%.0fs" % (time.time() - t0), flush=True)
        time.sleep(10)
    print("FEITOS", feitos, "TOTAL", len(res))


OFFLINE = [  # (fonte, corrida ja no ledger da copia, porque)
    ("IT-T2-002", "IT-T2-2026-09-14-155903-f49139dc61b15b9c", "ARPAV Agrometeo Informa - esperado SIM"),
    ("IT-T3-002", "XX-T3-2026-09-18-171909-b66be5e4276b76f7", "Campania servico fitossanitario - esperado SIM"),
    ("IT-T3-008", "XX-T3-2026-09-18-171937-6f76511ca75100a5", "ARIF notiziario agrometeorologico - esperado SIM"),
    ("IT-T3-010", "IT-T3-2026-09-14-160206-d157d76ef0904580", "APOL mosca da oliveira - esperado SIM"),
    ("IT-T2-004", "PILOT_RUN_20260907153737_4c34b3", "SIAS tabela de chuva - controlo, esperado NAO_SEI"),
    ("IT-T10-018", "IT-T10-2026-09-21-190312-183419e87ae3961c", "myfruit noticias de mercado - controlo, esperado nao SIM"),
]


def offline():
    """Sem rede (proxy morto): reconstroi o envelope da corrida do ledger e leva-o
    a porta com universo=T2, numa corrida NOVA, com o banco descartavel."""
    e = ler(ESTADO, None)
    res = ler(RES, {})
    env = ambiente(e["URL"])
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
        env[k] = "http://127.0.0.1:9"
    for fonte, corrida, porque in OFFLINE:
        chave = "OFFLINE:" + fonte
        if chave in res:
            continue
        c = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path[:0]=['coleta','.']; import italy_executor as X; "
                            "import json; print(json.dumps(X.colher(%r), default=str))" % corrida],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        cmd = [sys.executable, "orquestrador/orquestrador.py", "colete clima da italia", "--so-a-porta",
               "--colheita-da-corrida=%s" % corrida,
               "--filtro", "pais=IT", "--filtro", "fonte=%s" % fonte, "--filtro", "universo=T2"]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=env, timeout=900)
        import re
        m = re.search(r"(XX|IT)-T\d+-2026-\d\d-\d\d-\d{6}-[0-9a-f]+", (r.stdout or "").replace(corrida, ""))
        res[chave] = {"SOURCE_ID": fonte, "COLHEITA_DA_CORRIDA": corrida, "PORQUE": porque,
                      "COLHER": (c.stdout or "")[-800:] + (c.stderr or "")[-400:],
                      "RC": r.returncode, "RUN_ID": m.group(0) if m else None,
                      "SEGUNDOS": round(time.time() - t0, 1), "SAIDA_FIM": (r.stdout or "")[-3000:],
                      "ERRO_FIM": (r.stderr or "")[-1500:]}
        gravar(RES, res)
        print(chave, "rc", r.returncode, "run", res[chave]["RUN_ID"], "%.0fs" % (time.time() - t0), flush=True)


def medir():
    e = ler(ESTADO, None)
    res = ler(RES, {})

    def q(sql):
        r = subprocess.run([os.path.join(PG, "psql.exe"), "-X", "-A", "-t", "-F", "|", "-f", "-", e["URL"]],
                           input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return [l.split("|") for l in r.stdout.replace("\r", "").splitlines() if l != ""]
    for k, x in res.items():
        rid = x.get("RUN_ID")
        if not rid:
            x["MEDIDA"] = "SEM_RUN_ID"
            continue
        raw = q("select id, media_type, bytes, preserved from public.raw_asset where run_id = '%s';" % rid)
        der = q("select d.kind, d.bytes from public.derived_artifact d join public.raw_asset r on r.id = d.raw_asset_id "
                "where r.run_id = '%s';" % rid)
        sala = q("select * from public.sala_de_espera where run_id = '%s';" % rid)
        x["MEDIDA"] = {"RAW": raw, "DERIVED": der, "SALA": sala}
    gravar(RES, res)
    for k, x in res.items():
        m = x.get("MEDIDA") or {}
        print(k, x.get("TERRITORY"), "rc", x.get("RC"), "RAW", len(m.get("RAW", [])) if isinstance(m, dict) else m,
              "DERIVED", len(m.get("DERIVED", [])) if isinstance(m, dict) else "-",
              "SALA", len(m.get("SALA", [])) if isinstance(m, dict) else "-")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--subir" in a:
        subir()
    elif "--correr" in a:
        mx = next((int(x.split("=")[1]) for x in a if x.startswith("--max=")), 99)
        correr(mx)
    elif "--offline" in a:
        offline()
    elif "--medir" in a:
        medir()
    elif "--descer" in a:
        descer()
