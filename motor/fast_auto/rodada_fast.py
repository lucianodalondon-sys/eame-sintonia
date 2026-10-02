# SINTONIA FAST_BRAIN - rodada automatica (NOVO RAW -> FATOS -> SINAIS -> OPORTUNIDADES -> pasta do Casco)
# Contrato com o Casco (gerar_fast_local.py @ 70ca62425):
#   FAST-AUTO/<RUN_ID>/ com FACTS_FAST.json SIGNALS_FAST.json OPPORTUNITIES_FAST.json DOCUMENTOS_FAST.json,
#   raw_texto/*.txt e SHA256SUMS.txt (cobre os 4 JSON + raw_texto/*); ULTIMA.txt (RUN_ID=<id>) e escrito POR ULTIMO.
# Reusa os passos do FAST-V1 sem reescrever: copia passo1/2/3 para a pasta da rodada (AQUI = pasta da rodada).
# Banco: so leitura (transacao read only). Falha em qualquer passo = ULTIMA.txt nao muda (Casco fica na rodada anterior).
# Uso: python rodada_fast.py [--max 20] [--listar]
import datetime, hashlib, json, os, re, shutil, subprocess, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.normpath(os.path.join(RAIZ, "..", "FAST-V1"))
BASE = r"C:/Users/London1/sintonia-sala-italia"
PSQL = r"C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe"
FEITOS = os.path.join(RAIZ, "RAW_PROCESSADOS.txt")
LOG = os.path.join(RAIZ, "RODADAS.log")
ARQS = ["FACTS_FAST.json", "SIGNALS_FAST.json", "OPPORTUNITIES_FAST.json", "DOCUMENTOS_FAST.json"]


def log(msg):
    linha = "%s %s" % (datetime.datetime.now().isoformat(timespec="seconds"), msg)
    print(linha)
    open(LOG, "a", encoding="utf-8").write(linha + "\n")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def feitos():
    if not os.path.exists(FEITOS):
        return set()
    return {int(l) for l in open(FEITOS, encoding="utf-8") if l.strip().isdigit()}


def candidatos(maximo):
    env = dict(os.environ, PGPASSFILE=BASE + "/pgpass.conf", PGCLIENTENCODING="UTF8")
    dsn = open(BASE + "/SALA_DSN.txt").read().strip()
    sql = ("begin transaction read only; show transaction_read_only; "
           "select row_to_json(t) from (select id,source_id,captured_at from raw_asset where preserved "
           "and media_type in ('text/html','application/pdf') and bytes>3000 order by captured_at desc, id desc limit 500) t; commit;")
    out = subprocess.run([PSQL, "-w", "-X", "-A", "-t", "-c", sql, dsn], env=env, capture_output=True,
                         text=True, encoding="utf-8").stdout
    linhas = [l.strip() for l in out.splitlines() if l.strip()]
    assert "on" in linhas, ("transacao nao estava read only", linhas[:3])
    rows = [json.loads(l) for l in linhas if l.startswith("{")]
    ja = feitos()
    novos = [r for r in rows if r["id"] not in ja]
    return novos[:maximo]


def main():
    maximo = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 20
    novos = candidatos(maximo)
    if "--listar" in sys.argv:
        for r in novos:
            print(r)
        return
    if not novos:
        log("SEM_RAW_NOVO (nada a fazer; ULTIMA.txt inalterado)")
        return
    ids = sorted(r["id"] for r in novos)
    run_id = "FAST-" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    pasta = os.path.join(RAIZ, run_id)
    os.makedirs(pasta)
    log("INICIO %s RAW=%s" % (run_id, ",".join(map(str, ids))))
    # passo 1 do V1 com a lista de ids desta rodada (unica mudanca: IDS e a contagem esperada)
    p1 = open(os.path.join(V1, "passo1_selecionar.py"), encoding="utf-8").read()
    p1, n1 = re.subn(r"IDS = \[[^\]]*\]", "IDS = %r" % ids, p1)
    p1, n2 = re.subn(r"assert len\(rows\) == 20, len\(rows\)", "assert len(rows) == len(IDS), len(rows)", p1)
    assert n1 == 1 and n2 == 1, ("passo1 do V1 mudou de forma; nao adivinho", n1, n2)
    open(os.path.join(pasta, "passo1_selecionar.py"), "w", encoding="utf-8").write(p1)
    for s in ("passo2_fatos.py", "passo3_cruzar.py"):
        shutil.copy2(os.path.join(V1, s), os.path.join(pasta, s))
    for s in ("passo1_selecionar.py", "passo2_fatos.py", "passo3_cruzar.py"):
        r = subprocess.run([sys.executable, os.path.join(pasta, s)], cwd=pasta, capture_output=True,
                           text=True, encoding="utf-8")
        open(os.path.join(pasta, s.replace(".py", ".log")), "w", encoding="utf-8").write(r.stdout + "\n--STDERR--\n" + r.stderr)
        if r.returncode != 0:
            log("ERRO %s em %s rc=%s (ULTIMA.txt inalterado)" % (run_id, s, r.returncode))
            sys.exit(1)
    # SHA256SUMS: 4 JSON + raw_texto + scripts
    nomes = ARQS + ["raw_texto/" + f for f in sorted(os.listdir(os.path.join(pasta, "raw_texto")))] + \
        ["passo1_selecionar.py", "passo2_fatos.py", "passo3_cruzar.py"]
    with open(os.path.join(pasta, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        for n in nomes:
            f.write("%s *%s\n" % (sha(os.path.join(pasta, n)), n))
    F = json.load(open(os.path.join(pasta, "FACTS_FAST.json"), encoding="utf-8"))
    S = json.load(open(os.path.join(pasta, "SIGNALS_FAST.json"), encoding="utf-8"))
    O = json.load(open(os.path.join(pasta, "OPPORTUNITIES_FAST.json"), encoding="utf-8"))
    # ponteiro por ultimo, troca atomica
    tmp = os.path.join(RAIZ, "ULTIMA.txt.tmp")
    open(tmp, "w", encoding="utf-8", newline="\n").write("RUN_ID=%s\n" % run_id)
    os.replace(tmp, os.path.join(RAIZ, "ULTIMA.txt"))
    with open(FEITOS, "a", encoding="utf-8") as f:
        for i in ids:
            f.write("%d\n" % i)
    log("ENTREGUE %s DOCUMENTOS=%d FATOS=%d SINAIS=%d OPORTUNIDADES=%d" % (
        run_id, len(ids), len(F.get("FATOS", [])), len(S.get("SINAIS", [])), len(O.get("OPORTUNIDADES", []))))
    pos_rodada(run_id)


# Depois do ULTIMA.txt: entrega ao Casco. Falha aqui NAO desfaz a rodada (ela ja vale).
GERADOR_CASCO = r"C:/g/casco/italia-portale/audit/casco/gerar_fast_local.py"
HOOK_PUBLICAR = os.path.join(RAIZ, "POS_RODADA_PUBLICAR.cmd")  # dono = Casco (publica so se mudou)


def pos_rodada(run_id):
    raiz_ie = os.path.dirname(RAIZ)
    passos = [("GERADOR_CASCO", [sys.executable, GERADOR_CASCO, raiz_ie])]
    if os.path.exists(HOOK_PUBLICAR):
        passos.append(("PUBLICAR_CASCO", ["cmd.exe", "/c", HOOK_PUBLICAR, run_id]))
    else:
        log("POS_RODADA %s PUBLICAR_CASCO=AUSENTE (Casco ainda nao instalou %s)" % (run_id, HOOK_PUBLICAR))
    for nome, cmd in passos:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
            open(os.path.join(RAIZ, run_id, nome + ".log"), "w", encoding="utf-8").write(
                r.stdout + "\n--STDERR--\n" + r.stderr)
            log("POS_RODADA %s %s rc=%s" % (run_id, nome, r.returncode))
            if r.returncode != 0:
                return
        except Exception as e:
            log("POS_RODADA %s %s ERRO %r" % (run_id, nome, e))
            return


if __name__ == "__main__":
    main()
