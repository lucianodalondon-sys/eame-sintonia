# SINTONIA FAST_BRAIN - rodada automatica
#   NOVO RAW -> passo1 texto -> passo2 OPUS fatos -> passo3 OPUS sinais
#   -> OPUS + catalogo + bulas + janelas (motor/fast_cruzamento_comercial.py) -> SINAL/LEAD/GAP/OPORTUNIDADE
# O codigo vive no Git (motor/fast_auto/ + motor/fast_cruzamento_comercial.py) e corre de um worktree
# destacado num sha publicado; os dados ficam fora do Git em FAST-AUTO/. Cada rodada grava CODIGO_HEAD.
# Contrato com o Casco: FAST-AUTO/<RUN_ID>/ com os 4 JSON + CRUZAMENTO-COMERCIAL.json + raw_texto/*.txt
#   + SHA256SUMS.txt (cobre tudo isso); ULTIMA.txt (RUN_ID=<id>) e escrito POR ULTIMO.
# Banco: so leitura. Falha em qualquer passo = ULTIMA.txt nao muda (Casco fica na rodada anterior).
# Uso: python rodada_fast.py [--max 20] [--por-fonte 2] [--listar]
#      python rodada_fast.py --pedido PEDIDO.json   # captura PEDIDA (BUSCA_ATIVA): escopa a rodada
#          aos RAW nomeados no pedido e carimba o PEDIDO.json na pasta. NAO move ULTIMA.txt.
import datetime, hashlib, json, os, re, shutil, subprocess, sys
from collections import OrderedDict
from pathlib import Path

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


def linhas_banco(sql):
    """Leitura do banco, SO em transacao read only (o `show` e conferido, nao suposto)."""
    env = dict(os.environ, PGPASSFILE=BASE + "/pgpass.conf", PGCLIENTENCODING="UTF8")
    dsn = open(BASE + "/SALA_DSN.txt").read().strip()
    r = subprocess.run([PSQL, "-w", "-X", "-A", "-t", "-c", sql, dsn], env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    linhas = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    # o motivo da recusa vai na propria mensagem: sem o stderr do psql, "nao estava read only"
    # com a lista vazia esconde a causa real (foi medido: um erro do psql chega aqui sem explicacao).
    assert "on" in linhas, ("transacao nao estava read only", "rc=%s" % r.returncode,
                            (r.stderr or "").strip()[:300], linhas[:3])
    return [json.loads(l) for l in linhas if l.startswith("{")]


def candidatos(maximo):
    rows = linhas_banco("begin transaction read only; show transaction_read_only; "
                        "select row_to_json(t) from (select id,source_id,captured_at from raw_asset where preserved "
                        "and media_type in ('text/html','application/pdf') and bytes>3000 "
                        "order by captured_at desc, id desc limit 500) t; commit;")
    ja = feitos()
    novos = [r for r in rows if r["id"] not in ja]
    return alternar_fontes(novos, maximo, POR_FONTE)


# ── MODO PEDIDO (BUSCA_ATIVA) ─────────────────────────────────────────────────
# A rodada do ciclo escolhe SOZINHA os RAW (`candidatos`). Uma CAPTURA PEDIDA nao: ela responde a
# um EVIDENCE_REQUEST, e por isso chega nomeada de fora, num `PEDIDO.json` escrito pelo Scrap.
# Este modo so faz tres coisas, e nenhuma delas e semantica:
#   1) CONFERE o pedido (CASE_ID, ER e os RAW que ele nomeia) -- ou recusa a rodada inteira;
#   2) ESCOPA a rodada exatamente aos RAW nomeados (nada de "mais novo primeiro");
#   3) CARIMBA o `PEDIDO.json` DENTRO da pasta da rodada, porque e assim que o `fast_casos`
#      aceita ligar a captura ao caso: sem o ficheiro ele recusa a incorporacao.
# E isto NAO e a rodada das 2 h: `ULTIMA.txt` nao se move (o Casco fica na ultima rodada do
# ciclo) e o Casco nao e publicado. A rodada pedida so serve ao caso que a pediu.
ER_DE_PEDIDO = re.compile(r"^ER-[A-Z0-9_-]+$")
CASE_DE_PEDIDO = re.compile(r"^CASE-\d{3,}$")


class PedidoInvalido(Exception):
    pass


def ler_pedido(caminho):
    """Confere o PEDIDO.json. Sem CASE_ID, sem ER ou sem RAW nomeado nao ha rodada:
    uma captura que nao se liga a pedido nenhum nao pode ser incorporada (o `fast_casos`
    recusa-a), e por isso nasce-se recusada aqui, e nao na hora de incorporar."""
    p = Path(caminho)
    if not p.exists():
        raise PedidoInvalido("PEDIDO.json inexistente: %s" % p)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise PedidoInvalido("PEDIDO.json ilegivel (%r)" % e)
    if not isinstance(d, dict):
        raise PedidoInvalido("PEDIDO.json nao e um objeto")
    cid, er = d.get("CASE_ID"), d.get("EVIDENCE_REQUEST_ID")
    if not isinstance(cid, str) or not CASE_DE_PEDIDO.match(cid):
        raise PedidoInvalido("CASE_ID ausente ou mal formado: %r" % (cid,))
    if not isinstance(er, str) or not ER_DE_PEDIDO.match(er):
        raise PedidoInvalido("EVIDENCE_REQUEST_ID ausente ou mal formado: %r" % (er,))
    raws = d.get("RAW_ASSET_IDS")
    if not isinstance(raws, list) or not raws:
        raise PedidoInvalido("RAW_ASSET_IDS ausente ou vazio: %r" % (raws,))
    if not all(isinstance(x, int) and not isinstance(x, bool) and x > 0 for x in raws):
        raise PedidoInvalido("RAW_ASSET_IDS com id invalido: %r" % (raws,))
    if len(set(raws)) != len(raws):
        raise PedidoInvalido("RAW_ASSET_IDS com id repetido: %r" % (raws,))
    # linhagem da BUSCA_ATIVA (ordem do dono 02/10): SOURCE_CONTRACT_ID e SOURCE_ID vem COPIADOS do
    # Source Contract do Bot de Fontes; aqui so se confere a forma, nunca se calcula nem se inventa.
    for k in ("SOURCE_CONTRACT_ID", "SOURCE_ID"):
        v = d.get(k)
        if not isinstance(v, str) or not v.strip() or v.strip().upper() in ("NAO_SEI", "UNKNOWN", "NONE"):
            raise PedidoInvalido("%s ausente no PEDIDO.json (copiar do Source Contract): %r" % (k, v))
    return d


def conferir_contrato(ped, caminho):
    """`--contrato SOURCE_CONTRACT.json`: o PEDIDO tem de dizer o MESMO que o Source Contract do Bot de Fontes
    (SOURCE_CONTRACT_ID, CASE_ID, EVIDENCE_REQUEST_ID, SOURCE_ID) e a fonte tem de estar aprovada para captura.
    Divergencia recusa a rodada: nao se escolhe um dos dois."""
    p = Path(caminho)
    try:
        sc = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise PedidoInvalido("Source Contract ilegivel ou inexistente (%s: %r)" % (p, e))
    for k in ("SOURCE_CONTRACT_ID", "CASE_ID", "EVIDENCE_REQUEST_ID", "SOURCE_ID"):
        if sc.get(k) != ped.get(k):
            raise PedidoInvalido("%s do PEDIDO (%r) diverge do Source Contract (%r)" % (k, ped.get(k), sc.get(k)))
    if str(sc.get("APROVADA_PARA_CAPTURA")).upper() not in ("SIM", "TRUE"):
        raise PedidoInvalido("Source Contract sem APROVADA_PARA_CAPTURA=SIM: %r" % (sc.get("APROVADA_PARA_CAPTURA"),))
    return sc


def carimbar_pedido(pasta, pedido, run_id):
    """Escreve o `PEDIDO.json` DENTRO da pasta da rodada: e o elo que o `fast_casos` exige
    para aceitar a captura como BUSCA_ATIVA (sem este ficheiro ele recusa a incorporacao).
    Ao pedido acrescenta-se apenas a identidade da rodada que o serviu."""
    json.dump(dict(pedido, RUN_ID=run_id, RODADA_PEDIDA=True),
              open(os.path.join(pasta, "PEDIDO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def raws_do_pedido(ped):
    """Os RAW do pedido, lidos do banco SO em leitura. Um id que nao existe em `raw_asset`
    recusa a rodada inteira: a pasta nao pode nomear um RAW que nao existe."""
    ids = list(ped["RAW_ASSET_IDS"])
    rows = linhas_banco("begin transaction read only; show transaction_read_only; "
                        "select row_to_json(t) from (select id,source_id,captured_at from raw_asset where id in (%s) "
                        "order by id) t; commit;" % ",".join(map(str, ids)))
    faltam = sorted(set(ids) - {r["id"] for r in rows})
    if faltam:
        raise PedidoInvalido("RAW_ASSET_ID inexistente em raw_asset: %s" % faltam)
    sobram = sorted({r["id"] for r in rows} - set(ids))
    if sobram:
        # a rodada pedida nao pode trazer RAW que o pedido nao nomeia: se o banco devolve
        # mais do que se pediu, recusa-se a rodada em vez de a estreitar em silencio.
        raise PedidoInvalido("raw_asset devolveu RAW fora do pedido: %s" % sobram)
    # o SOURCE_ID do contrato tem de ser o da captura: RAW de outra fonte nao responde a este pedido
    outra = sorted(r["id"] for r in rows if r["source_id"] != ped["SOURCE_ID"])
    if outra:
        raise PedidoInvalido("RAW de outra fonte que nao o SOURCE_ID do pedido (%s): %s" % (ped["SOURCE_ID"], outra))
    # ordem fixada aqui, e nao pela clausula do banco: a rodada pedida entra sempre por id crescente
    # (e o mesmo `order by id` que o passo1 usa ao reler)
    return [{"id": r["id"], "source_id": r["source_id"]} for r in sorted(rows, key=lambda r: r["id"])]


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
    pedido = None
    if "--pedido" in sys.argv:
        if "--retomar" in sys.argv:
            log("ERRO --pedido e --retomar sao modos diferentes - nao corro")
            sys.exit(2)
        try:
            pedido = ler_pedido(sys.argv[sys.argv.index("--pedido") + 1])
            if "--contrato" in sys.argv:
                conferir_contrato(pedido, sys.argv[sys.argv.index("--contrato") + 1])
            novos = raws_do_pedido(pedido)
        except PedidoInvalido as e:
            log("ERRO --pedido recusado: %s (ULTIMA.txt inalterado)" % e)
            sys.exit(2)
    else:
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
        if pedido:
            carimbar_pedido(pasta, pedido, run_id)
        primeiro = 0
    fontes = OrderedDict()
    for r in novos:
        fontes[r["source_id"]] = fontes.get(r["source_id"], 0) + 1
    log("%s %s CODIGO_HEAD=%s RAW=%s FONTES=%d MAX_POR_FONTE=%d%s" % (
        "RETOMA" if retomar else "INICIO", run_id, head, ",".join(map(str, ids)), len(fontes), max(fontes.values()),
        " MODO=PEDIDO CASE=%s ER=%s SC=%s SOURCE_ID=%s" % (pedido["CASE_ID"], pedido["EVIDENCE_REQUEST_ID"],
                                                           pedido["SOURCE_CONTRACT_ID"], pedido["SOURCE_ID"])
        if pedido else ""))
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
                          ("MODO", "PEDIDO" if pedido else "CICLO"),
                          ("PEDIDO", ({"CASE_ID": pedido["CASE_ID"], "EVIDENCE_REQUEST_ID": pedido["EVIDENCE_REQUEST_ID"],
                                       "SOURCE_CONTRACT_ID": pedido["SOURCE_CONTRACT_ID"], "SOURCE_ID": pedido["SOURCE_ID"],
                                       "RAW_ASSET_IDS": pedido["RAW_ASSET_IDS"]} if pedido else None)),
                          ("SELECAO", {"MAX": maximo, "MAX_POR_FONTE": POR_FONTE, "FONTES": fontes})])
    json.dump(codigo, open(os.path.join(pasta, "CODIGO.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # SHA256SUMS: 4 JSON + cruzamento + raw_texto + codigo
    nomes = ARQS + ["CRUZAMENTO-COMERCIAL.json", "CODIGO.json", "IDS.json"] + (["PEDIDO.json"] if pedido else []) + \
        ["cruzamento-comercial/" + f for f in ("PROMPT.txt", "SAIDA_BRUTA_DO_MODELO.json", "CRUZAMENTO-COMERCIAL.json")] + \
        ["raw_texto/" + f for f in sorted(os.listdir(os.path.join(pasta, "raw_texto")))]
    with open(os.path.join(pasta, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        for n in nomes:
            f.write("%s *%s\n" % (sha(os.path.join(pasta, n)), n))
    F = json.load(open(os.path.join(pasta, "FACTS_FAST.json"), encoding="utf-8"))
    S = json.load(open(os.path.join(pasta, "SIGNALS_FAST.json"), encoding="utf-8"))
    # ponteiro por ultimo, troca atomica
    if pedido:
        # A RODADA PEDIDA NAO E O PONTEIRO DO CASCO. `ULTIMA.txt` fica onde estava e o Casco
        # nao e publicado: a rodada do ciclo continua a ser a das 2 h. Os RAW entram em
        # RAW_PROCESSADOS porque FORAM processados (se nao entrassem, a rodada das 2 h
        # pagaria outra vez passo1/passo2 sobre os mesmos bytes).
        with open(FEITOS, "a", encoding="utf-8") as f:
            for i in ids:
                f.write("%d\n" % i)
        k = C["CONTAGEM"]
        log("ENTREGUE %s MODO=PEDIDO CASE=%s ER=%s DOCUMENTOS=%d FONTES=%d FATOS=%d SINAIS_PASSO3=%d "
            "| PEDIDO.json carimbado | ULTIMA.txt INALTERADO" % (
                run_id, pedido["CASE_ID"], pedido["EVIDENCE_REQUEST_ID"], len(ids), len(fontes),
                len(F.get("FATOS", [])), len(S.get("SINAIS", []))))
        return
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
