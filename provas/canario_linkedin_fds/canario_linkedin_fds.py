"""CANARIO-LINKEDIN-FDS · o canário SCRAP_FASE das 6 páginas LinkedIn de organização (D23).

    py provas/canario_linkedin_fds/canario_linkedin_fds.py --subir     # banco descartável próprio + migrações
    py provas/canario_linkedin_fds/canario_linkedin_fds.py --correr    # as 6 corridas video-linkedin
    py provas/canario_linkedin_fds/canario_linkedin_fds.py --medir     # RAW/DERIVED/Sala por corrida, lido do banco
    py provas/canario_linkedin_fds/canario_linkedin_fds.py --descer    # desliga o banco

É o `provas/canario_social_onda2.py` (SOC-ONDA2) com três diferenças, e só estas:
  · corre NESTA worktree (cópia), com o catálogo do Curator copiado da cópia de trabalho
    do serviço vivo (as 6 fontes não existem no catálogo do Git — T9, 01/10);
  · os alvos são os 6 SOURCE_ID da missão, lidos do contrato (FILTROS do contrato, teto=2);
  · banco, armazém e resultados ficam fora do Git, em %TEMP%/canario-li-fds.
Mesma linha de comando (orquestrador -> scrap-colheita, fase do contrato), mesmo portão
de egresso IT antes e depois de cada conta, mesmo ritmo (20 s entre contas).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AQUI = os.path.join(os.environ.get("TEMP") or tempfile.gettempdir(), "canario-li-fds")
ESTADO = os.path.join(AQUI, "banco.json")
RES = os.path.join(AQUI, "resultados.json")
PG = os.path.join(os.path.expanduser("~"), "orca", "pgtmp", "pgsql", "bin")
FASE = "video-linkedin"
SIDS = ("IT-T9-026", "IT-T7-253", "IT-T5-191", "IT-T5-190", "IT-T7-254", "IT-T9-025")
APELIDO = {"T5": "ciencia", "T7": "cooperativas", "T9": "concorrentes"}
sys.path.insert(0, os.path.join(WT, "provas"))
os.chdir(WT)


def ler(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def gravar(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def subir():
    os.makedirs(AQUI, exist_ok=True)
    tempfile.tempdir = os.path.join(AQUI, "cluster-pai")
    os.makedirs(tempfile.tempdir, exist_ok=True)
    import a_porta_cli_liga_o_banco as P
    b = P.Bancada()
    url = b.subir()
    cod, n, saida, erro = P._migrations(url, dict(os.environ))
    gravar(ESTADO, {"URL": url, "CLUSTER": b.cluster, "PORTO": b.porto, "PGBIN": b.pgbin,
                    "MIGRACOES": n, "RC": cod})
    print("BANCO porto", b.porto, "migracoes", n, "rc", cod)


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
    return "\"EGRESS_GATE\": \"PASS\"" in r.stdout, r.stdout[-300:]


def ambiente(url):
    e = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
             BANCO_DESCARTAVEL_URL=url, SINTONIA_PSQL_EXE=os.path.join(PG, "psql.exe"),
             SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url,
             SINTONIA_ARMAZEM_RAIZ=os.path.join(AQUI, "armazem"),
             # o mesmo ambiente do canario SOC-ONDA2 (ASR na placa, se a derivacao o pedir)
             SINTONIA_LIBS=os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Python",
                                        "Python312", "Lib", "site-packages"),
             SINTONIA_ASR_DEVICE="AUTO",
             PYTHONPATH=os.pathsep.join([os.path.expanduser("~/.sintonia-libs"),
                                         os.path.join(os.path.expanduser("~"), "soc5-libs")]))
    e.pop("SINTONIA_COLLECTION_DSN", None)
    e["PATH"] = PG + os.pathsep + e.get("PATH", "")
    return e


def alvos():
    d = json.load(open(os.path.join(WT, "curadoria", "italy_contracts_curator.json"), encoding="utf-8"))
    por_sid = {c["SOURCE_ID"]: c for c in d["FONTES"]}
    out = []
    for sid in SIDS:
        c = por_sid[sid]
        aq = c.get("ACQUISITION") or {}
        assert aq.get("FASE") == FASE, (sid, aq.get("FASE"))
        out.append((sid, c["TERRITORY"], aq["FILTROS"]))
    return out


def correr():
    e = ler(ESTADO, None)
    res = ler(RES, {})
    feitos = 0
    for sid, terr, filtros in alvos():
        chave = "%s:%s" % (sid, FASE)
        if chave in res:
            continue
        ok, txt = egresso()
        if not ok:
            print("EGRESSO NAO E IT — parado antes de", chave, txt)
            gravar(RES, res)
            return
        cmd = [sys.executable, "orquestrador/orquestrador.py", "colete %s" % APELIDO[terr],
               "--filtro", "fase=%s" % FASE, "--filtro", "fonte=%s" % sid]
        for k, v in filtros.items():
            cmd += ["--filtro", "%s=%s" % (k, v)]
        cmd += ["--filtro", "pais=IT", "--filtro", "universo=%s" % terr]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=ambiente(e["URL"]))
        ok2, _ = egresso()
        m = re.search(r"\b(?:XX|IT)-T\d+-2026-\d\d-\d\d-\d{6}-[0-9a-f]+\b", r.stdout or "")
        res[chave] = {"SOURCE_ID": sid, "TERRITORY": terr, "FASE": FASE, "FILTROS": filtros,
                      "COMANDO": cmd[1:], "RC": r.returncode, "RUN_ID": m.group(0) if m else None,
                      "SEGUNDOS": round(time.time() - t0, 1), "EGRESSO_DEPOIS_IT": ok2,
                      "SAIDA_FIM": (r.stdout or "")[-3000:], "ERRO_FIM": (r.stderr or "")[-1500:]}
        gravar(RES, res)
        feitos += 1
        print(chave, "rc", r.returncode, "run", res[chave]["RUN_ID"], "%.0fs" % (time.time() - t0), flush=True)
        time.sleep(20)                                             # ritmo baixo
    print("FEITOS", feitos, "TOTAL", len(res))


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
        der = q("select d.kind, d.bytes from public.derived_artifact d join public.raw_asset r "
                "on r.id = d.raw_asset_id where r.run_id = '%s';" % rid)
        sala = q("select universo, estagio, left(texto, 80) from public.sala_de_espera where run_id = '%s';" % rid)
        x["MEDIDA"] = {"RAW": raw, "DERIVED": der, "SALA": sala}
    gravar(RES, res)
    for k, x in res.items():
        m = x.get("MEDIDA") or {}
        dm = isinstance(m, dict)
        print(k, x.get("TERRITORY"), "rc", x.get("RC"), "RAW", len(m.get("RAW", [])) if dm else m,
              "DERIVED", len(m.get("DERIVED", [])) if dm else "-", "SALA", len(m.get("SALA", [])) if dm else "-")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--subir" in a:
        subir()
    elif "--correr" in a:
        correr()
    elif "--medir" in a:
        medir()
    elif "--descer" in a:
        descer()
