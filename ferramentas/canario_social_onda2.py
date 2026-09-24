"""SOC-ONDA2 · canário social pela porta canónica — 1-2 itens por conta, banco descartável próprio.

    py C:/soc2/canario/canario_social.py --subir                 # banco em pasta própria + migrações
    py C:/soc2/canario/canario_social.py --correr [--max=N] [--fase=video-linkedin]
    py C:/soc2/canario/canario_social.py --medir                 # RAW/DERIVED/Sala por corrida, lido do banco
    py C:/soc2/canario/canario_social.py --descer                # desliga o banco

Corre na CÓPIA (C:/soc2/copia), nunca no vivo. Cada conta: portão de egresso IT ANTES
(se não for IT, para); orquestrador com a fase do contrato (scrap-colheita);
portão de egresso DEPOIS. Resumível: resultados.json.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

WT = r"C:\soc2\copia"
AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "banco.json")
RES = os.path.join(AQUI, "resultados.json")
PG = os.path.join(os.path.expanduser("~"), "orca", "pgtmp", "pgsql", "bin")
APELIDO = {"T1": "culturas", "T2": "clima", "T3": "pragas", "T4": "regulatorio", "T5": "ciencia",
           "T7": "cooperativas", "T8": "agricultores", "T9": "concorrentes", "T10": "mercado",
           "T11": "feiras", "T12": "politica", "T13": "distribuidores"}
sys.path.insert(0, os.path.join(WT, "provas"))
os.chdir(WT)


def ler(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def gravar(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def subir():
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
             SINTONIA_ARMAZEM_RAIZ=os.path.join(AQUI, "armazem"))
    e.pop("SINTONIA_COLLECTION_DSN", None)
    e["PATH"] = PG + os.pathsep + e.get("PATH", "")
    return e


def alvos(fase):
    d = json.load(open(os.path.join(WT, "curadoria", "italy_contracts_curator.json"), encoding="utf-8"))
    ens = json.load(open(r"C:\soc2\ensaio_qualify.json", encoding="utf-8"))
    novos = {n["SOURCE_ID"] for n in ens["NOVAS"]}
    out = []
    for c in d["FONTES"]:
        aq = c.get("ACQUISITION") or {}
        if c["SOURCE_ID"] in novos and aq.get("FASE") == fase:
            out.append((c["SOURCE_ID"], c["TERRITORY"], aq["FILTROS"]))
    return out


def correr(maximo, fase):
    e = ler(ESTADO, None)
    res = ler(RES, {})
    feitos = 0
    for sid, terr, filtros in alvos(fase):
        chave = "%s:%s" % (sid, fase)
        if chave in res or feitos >= maximo:
            continue
        ok, txt = egresso()
        if not ok:
            print("EGRESSO NAO E IT — parado antes de", chave, txt)
            gravar(RES, res)
            return
        cmd = [sys.executable, "orquestrador/orquestrador.py", "colete %s" % APELIDO[terr],
               "--filtro", "fase=%s" % fase, "--filtro", "fonte=%s" % sid]
        for k, v in filtros.items():
            cmd += ["--filtro", "%s=%s" % (k, v)]
        cmd += ["--filtro", "pais=IT", "--filtro", "universo=%s" % terr]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=ambiente(e["URL"]))
        ok2, _ = egresso()
        m = re.search(r"\b(?:XX|IT)-T\d+-2026-\d\d-\d\d-\d{6}-[0-9a-f]+\b", r.stdout or "")
        res[chave] = {"SOURCE_ID": sid, "TERRITORY": terr, "FASE": fase, "FILTROS": filtros,
                      "RC": r.returncode, "RUN_ID": m.group(0) if m else None,
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
    fase = next((x.split("=", 1)[1] for x in a if x.startswith("--fase=")), "video-linkedin")
    if "--subir" in a:
        subir()
    elif "--correr" in a:
        correr(next((int(x.split("=")[1]) for x in a if x.startswith("--max=")), 99), fase)
    elif "--medir" in a:
        medir()
    elif "--descer" in a:
        descer()
