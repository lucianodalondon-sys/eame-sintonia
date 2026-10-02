# SINTONIA FAST_BRAIN - rodada automatica
#   NOVO RAW -> passo1 texto -> passo2 OPUS fatos -> passo3 OPUS sinais
#   -> OPUS + catalogo + bulas + janelas (motor/fast_cruzamento_comercial.py) -> SINAL/LEAD/GAP/OPORTUNIDADE
# O codigo vive no Git (motor/fast_auto/ + motor/fast_cruzamento_comercial.py) e corre de um worktree
# destacado num sha publicado; os dados ficam fora do Git em FAST-AUTO/. Cada rodada grava CODIGO_HEAD.
# Contrato com o Casco: FAST-AUTO/<RUN_ID>/ com os 4 JSON + CRUZAMENTO-COMERCIAL.json + raw_texto/*.txt
#   + SHA256SUMS.txt (cobre tudo isso); ULTIMA.txt (RUN_ID=<id>) e escrito POR ULTIMO.
# Banco: so leitura. Falha em qualquer passo = ULTIMA.txt nao muda (Casco fica na rodada anterior).
# Uso: python rodada_fast.py [--max 20] [--por-fonte 2] [--listar]
import datetime, hashlib, json, os, re, shutil, subprocess, sys
from collections import OrderedDict

CODIGO = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(CODIGO))
RAIZ = os.environ.get("FAST_AUTO_DIR", r"C:/Users/London1/sintonia-sala-italia/intelligence-experimental/FAST-AUTO")
BASE = r"C:/Users/London1/sintonia-sala-italia"
PSQL = r"C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe"
FEITOS = os.path.join(RAIZ, "RAW_PROCESSADOS.txt")
LOG = os.path.join(RAIZ, "RODADAS.log")
ARQS = ["FACTS_FAST.json", "SIGNALS_FAST.json", "OPPORTUNITIES_FAST.json", "DOCUMENTOS_FAST.json"]
PASSOS = ["passo1_selecionar.py", "passo2_fatos.py", "passo3_cruzar.py"]
COMERCIAL = os.path.join(REPO, "motor", "fast_cruzamento_comercial.py")


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout.strip()


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
    return alternar_fontes(novos, maximo, POR_FONTE)


POR_FONTE = 2


def alternar_fontes(novos, maximo, por_fonte):
    """Defeito medido: os RAW mais novos sao muitas vezes 20 paginas do mesmo site.
    Correcao minima autorizada: alternar SOURCE_ID (mais novo primeiro) e no maximo `por_fonte` por rodada.
    Nao e filtro de relevancia: o que fica de fora espera a proxima rodada (nao entra em RAW_PROCESSADOS)."""
    filas = OrderedDict()
    for r in novos:  # ja vem do mais novo para o mais velho
        filas.setdefault(r["source_id"], []).append(r)
    out, volta = [], 0
    while len(out) < maximo and volta < por_fonte:
        for fila in filas.values():
            if len(fila) > volta and len(out) < maximo:
                out.append(fila[volta])
        volta += 1
    return out


def texto_entregue(F) -> dict:
    """O texto que o modelo viu, por documento, lido de FACTS_FAST.DOCUMENTOS (gravado pelo passo2 no ponto de
    entrega). TEXTO_LIMPO_PROVADO so com TODOS os documentos com hash e com o ficheiro a conferir (vazio nao prova)."""
    docs = F.get("DOCUMENTOS") or []
    sem = [d.get("DOCUMENT_ID") for d in docs if not d.get("TEXTO_ENTREGUE_SHA256")]
    nao_conf = [d.get("DOCUMENT_ID") for d in docs
                if d.get("TEXTO_ENTREGUE_SHA256") and d.get("CONFERE_COM_DOCUMENTOS") is not True]
    return OrderedDict([
        ("TEXTO_LIMPO_PROVADO", bool(docs) and not sem and not nao_conf),
        ("TEXTO_ENTREGUE_SHA256", {d.get("DOCUMENT_ID"): d["TEXTO_ENTREGUE_SHA256"] for d in docs
                                   if d.get("TEXTO_ENTREGUE_SHA256")}),
        ("TEXTO_ENTREGUE_CHARS", sum(d.get("TEXTO_ENTREGUE_CHARS") or 0 for d in docs)),
        ("DOCUMENTOS_SEM_HASH", sem),
        ("DOCUMENTOS_QUE_NAO_CONFEREM", nao_conf),
        ("FONTE", "FACTS_FAST.json DOCUMENTOS (passo2_fatos.py, ponto de entrega ao modelo)")])


def main():
    global POR_FONTE
    maximo = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 20
    if "--por-fonte" in sys.argv:
        POR_FONTE = int(sys.argv[sys.argv.index("--por-fonte") + 1])
    novos = [] if "--retomar" in sys.argv else candidatos(maximo)
    if "--listar" in sys.argv:
        for r in novos:
            print(r)
        return
    head, sujo = git("rev-parse", "HEAD"), git("status", "--porcelain", "--", "motor")
    if not head or sujo:
        log("ERRO codigo nao versionado ou sujo em %s (HEAD=%s) - nao corro" % (REPO, head or "NAO_SEI"))
        sys.exit(1)
    retomar = sys.argv[sys.argv.index("--retomar") + 1] if "--retomar" in sys.argv else None
    if retomar:
        # rodada que caiu depois dos fatos: nao repaga passo1/passo2; corre o resto com o codigo atual
        run_id, pasta = retomar, os.path.join(RAIZ, retomar)
        ids = json.load(open(os.path.join(pasta, "IDS.json"), encoding="utf-8"))
        D = json.load(open(os.path.join(pasta, "DOCUMENTOS_FAST.json"), encoding="utf-8"))
        novos = [{"id": x["RAW_ASSET_ID"], "source_id": x["SOURCE_ID"]} for x in D]
        assert sorted(r["id"] for r in novos) == sorted(ids), "IDS.json != DOCUMENTOS_FAST.json"
        assert os.path.exists(os.path.join(pasta, "FACTS_FAST.json")), "sem FACTS_FAST.json: nao ha o que retomar"
        primeiro = 2
    elif not novos:
        log("SEM_RAW_NOVO (nada a fazer; ULTIMA.txt inalterado) CODIGO_HEAD=%s" % head)
        return
    else:
        ids = sorted(r["id"] for r in novos)
        run_id = "FAST-" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        pasta = os.path.join(RAIZ, run_id)
        os.makedirs(pasta)
        json.dump(ids, open(os.path.join(pasta, "IDS.json"), "w", encoding="utf-8"))
        primeiro = 0
    fontes = OrderedDict()
    for r in novos:
        fontes[r["source_id"]] = fontes.get(r["source_id"], 0) + 1
    log("%s %s CODIGO_HEAD=%s RAW=%s FONTES=%d MAX_POR_FONTE=%d" % (
        "RETOMA" if retomar else "INICIO", run_id, head, ",".join(map(str, ids)), len(fontes), max(fontes.values())))
    passos = [(s, [sys.executable, os.path.join(CODIGO, s), pasta]) for s in PASSOS][primeiro:]
    passos.append(("fast_cruzamento_comercial.py", [sys.executable, COMERCIAL, pasta]))
    for nome, cmd in passos:
        r = subprocess.run(cmd, cwd=pasta, capture_output=True, text=True, encoding="utf-8", errors="replace")
        open(os.path.join(pasta, nome.replace(".py", ".log")), "w", encoding="utf-8").write(
            r.stdout + "\n--STDERR--\n" + r.stderr)
        if r.returncode != 0:
            log("ERRO %s em %s rc=%s (ULTIMA.txt inalterado)" % (run_id, nome, r.returncode))
            sys.exit(1)
    # o Casco le CRUZAMENTO-COMERCIAL.json na raiz da rodada; mesma copia de cruzamento-comercial/ (mesmo sha)
    shutil.copyfile(os.path.join(pasta, "cruzamento-comercial", "CRUZAMENTO-COMERCIAL.json"),
                    os.path.join(pasta, "CRUZAMENTO-COMERCIAL.json"))
    C = json.load(open(os.path.join(pasta, "CRUZAMENTO-COMERCIAL.json"), encoding="utf-8"))
    assert C.get("CODIGO_HEAD") == head and C.get("CODIGO_LIMPO_EM_MOTOR") is True, "cruzamento sem CODIGO_HEAD provado"
    # todas as versoes que tocaram esta rodada (retomada = mais de uma), lidas do RODADAS.log
    versoes = []
    for l in open(LOG, encoding="utf-8"):
        m = re.search(r" (INICIO|RETOMA) %s CODIGO_HEAD=([0-9a-f]{40})" % re.escape(run_id), l)
        if m and m.group(2) not in [v["CODIGO_HEAD"] for v in versoes]:
            versoes.append({"CODIGO_HEAD": m.group(2), "EVENTO": m.group(1), "EM": l[:19]})
    F = json.load(open(os.path.join(pasta, "FACTS_FAST.json"), encoding="utf-8"))
    codigo = OrderedDict([("CODIGO_HEAD", head), ("VERSOES_DA_RODADA", versoes), ("REPO", REPO),
                          ("ARQUIVOS", {os.path.relpath(p, REPO).replace("\\", "/"): sha(p) for p in
                                        [os.path.join(CODIGO, s) for s in PASSOS] + [COMERCIAL, __file__]}),
                          ("TEXTO_ENTREGUE", texto_entregue(F)),
                          ("SELECAO", {"MAX": maximo, "MAX_POR_FONTE": POR_FONTE, "FONTES": fontes})])
    json.dump(codigo, open(os.path.join(pasta, "CODIGO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # SHA256SUMS: 4 JSON + cruzamento + raw_texto + codigo
    nomes = ARQS + ["CRUZAMENTO-COMERCIAL.json", "CODIGO.json", "IDS.json"] + \
        ["cruzamento-comercial/" + f for f in ("PROMPT.txt", "SAIDA_BRUTA_DO_MODELO.json", "CRUZAMENTO-COMERCIAL.json")] + \
        ["raw_texto/" + f for f in sorted(os.listdir(os.path.join(pasta, "raw_texto")))]
    with open(os.path.join(pasta, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        for n in nomes:
            f.write("%s *%s\n" % (sha(os.path.join(pasta, n)), n))
    F = json.load(open(os.path.join(pasta, "FACTS_FAST.json"), encoding="utf-8"))
    S = json.load(open(os.path.join(pasta, "SIGNALS_FAST.json"), encoding="utf-8"))
    # ponteiro por ultimo, troca atomica
    tmp = os.path.join(RAIZ, "ULTIMA.txt.tmp")
    open(tmp, "w", encoding="utf-8", newline="\n").write("RUN_ID=%s\n" % run_id)
    os.replace(tmp, os.path.join(RAIZ, "ULTIMA.txt"))
    with open(FEITOS, "a", encoding="utf-8") as f:
        for i in ids:
            f.write("%d\n" % i)
    k = C["CONTAGEM"]
    log("ENTREGUE %s CODIGO_HEAD=%s DOCUMENTOS=%d FONTES=%d FATOS=%d SINAIS_PASSO3=%d | COMERCIAL SINAL=%d LEAD=%d "
        "GAP=%d OPORTUNIDADE=%d REJEITADOS=%d MODELOS=%s" % (
            run_id, head, len(ids), len(fontes), len(F.get("FATOS", [])), len(S.get("SINAIS", [])), k["SINAL"],
            k["LEAD"], k["GAP"], k["OPORTUNIDADE"], len(C.get("REJEITADOS_POR_ID") or []),
            ",".join(C["CUSTO"].get("MODELOS") or [])))
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
