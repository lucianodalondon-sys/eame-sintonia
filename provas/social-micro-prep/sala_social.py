"""Leva o envelope remontado pela porta canonica ate uma Sala DESCARTAVEL e le as colunas (so SELECT).

    py C:/soc2/sala_social.py <RUN_ID> <SID> <Tn> <slug>
Sobe o banco (provas/a_porta_cli_liga_o_banco.Bancada da producao, em pasta propria), corre as migracoes,
chama o orquestrador EM PROCESSO com so_a_porta + colheita_da_corrida (nada vai a rede), le a Sala e desliga.
"""
import json
import os
import subprocess
import sys
import tempfile

E = os.environ.get("ENS", r"C:\ens-sr")
PG = os.path.join(os.path.expanduser("~"), "orca", "pgtmp", "pgsql", "bin")
run_id, sid, terr, slug = sys.argv[1:5]
os.chdir(E)
sys.path.insert(0, os.path.join(E, "provas"))
tempfile.tempdir = r"C:\soc2\sala-sr"
os.makedirs(tempfile.tempdir, exist_ok=True)
import a_porta_cli_liga_o_banco as P  # noqa: E402

b = P.Bancada()
url = b.subir()
try:
    cod, n, _s, _e = P._migrations(url, dict(os.environ))
    print("BANCO migracoes", n, "rc", cod)
    env = dict(os.environ, PYTHONUTF8="1", BANCO_DESCARTAVEL_URL=url, SINTONIA_PSQL_EXE=os.path.join(PG, "psql.exe"),
               SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url,
               SINTONIA_ARMAZEM_RAIZ=r"C:\soc2\sala-sr\armazem",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", NO_PROXY="localhost,127.0.0.1")
    env.pop("SINTONIA_COLLECTION_DSN", None)
    env["PATH"] = PG + os.pathsep + env.get("PATH", "")
    prog = ("import sys; sys.path[:0]=['.','orquestrador']; import _gavetas; import orquestrador as O; "
            "from pedido import Pedido; "
            "p=Pedido(alvo=%r, filtros={'fase':'video-linkedin','fonte':%r,'pagina':'https://www.linkedin.com/company/%s/',"
            "'teto':'1','pais':'IT','universo':%r}); "
            "import persistencia; rt=persistencia.dependencias_do_runtime(); "
            "r=O.correr(p, so_a_porta=True, colheita_da_corrida=%r, memoria=rt.memoria, "
            "banco_do_rastro=rt.banco_do_rastro, raiz_do_armazem=rt.raiz_do_armazem); "
            "r['PERSISTENCIA']=rt.para_json(); "
            "import json; r.pop('_plano', None); "
            "open('C:/soc2/recibo-db-%s.json','w',encoding='utf-8').write(json.dumps(r,ensure_ascii=False,default=str,indent=1)); "
            "print('STATUS', r.get('STATUS'), r.get('RUN_ID'))" % (terr, sid, slug, terr, run_id, sid))
    r = subprocess.run([sys.executable, "-c", prog], cwd=E, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    with open(r"C:\soc2\sala-orq-%s.txt" % sid, "w", encoding="utf-8") as fh:
        fh.write((r.stdout or "") + "\n---STDERR---\n" + (r.stderr or ""))
    print("ORQ rc", r.returncode, (r.stdout or "")[-300:])
    q = ("select source_id, published_at, published_at_basis, source_location, source_location_basis, "
         "tempo_lugar_evidencia::text, completude_tempo_lugar::text, estagio from public.sala_de_espera;")
    s = subprocess.run([os.path.join(PG, "psql.exe"), "-X", "-A", "-F", " | ", "-c", q, url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("SALA\n" + s.stdout[-4000:] + s.stderr[-400:])
    raw = subprocess.run([os.path.join(PG, "psql.exe"), "-X", "-A", "-t", "-c",
                          "select count(*) from public.raw_asset;", url], capture_output=True, text=True)
    print("RAW_ASSET", raw.stdout.strip())
finally:
    subprocess.run([os.path.join(PG, "pg_ctl.exe"), "-D", b.cluster, "-w", "-m", "fast", "stop"],
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("BANCO DESLIGADO", b.cluster)
