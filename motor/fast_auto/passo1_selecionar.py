# SINTONIA_FAST_V1 - passo 1: 20 RAW reais da tabela raw_asset -> texto legivel
# Le o banco SO em leitura (transacao read only) e o arquivo do armazem. Nao escreve nada fora desta pasta.
import hashlib, html, json, os, re, subprocess, sys
from html.parser import HTMLParser

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = r"C:/Users/London1/sintonia-sala-italia"
ARM = BASE + "/armazem/"
PSQL = r"C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe"
IDS = [2785, 2781, 2777, 2728, 2732, 2666, 2621, 2616, 2613, 2564,
       2540, 2384, 2277, 2243, 2242, 2241, 2240, 2231, 2232, 2230]

env = dict(os.environ, PGPASSFILE=BASE + "/pgpass.conf", PGCLIENTENCODING="UTF8")
dsn = open(BASE + "/SALA_DSN.txt").read().strip()
sql = ("begin transaction read only; show transaction_read_only; "
       "select row_to_json(t) from (select id,run_id,source_id,source_url,storage_path,media_type,bytes,sha256,"
       "captured_at,document_key,identity_state from raw_asset where id in (%s) order by id) t; commit;"
       % ",".join(map(str, IDS)))
out = subprocess.run([PSQL, "-w", "-X", "-A", "-t", "-c", sql, dsn], env=env, capture_output=True, text=True, encoding="utf-8").stdout
linhas = [l for l in out.splitlines() if l.strip()]
assert "on" in [l.strip() for l in linhas], ("transacao nao estava read only", linhas[:3])
rows = [json.loads(l) for l in linhas if l.startswith("{")]
assert len(rows) == 20, len(rows)


class T(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head", "template"}
    BLOCO = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "tr", "section", "article", "td", "header", "footer"}
    def __init__(s):
        super().__init__(convert_charrefs=True); s.o = []; s.d = 0
    def handle_starttag(s, t, a):
        if t in s.SKIP: s.d += 1
        elif t in s.BLOCO: s.o.append("\n")
    def handle_endtag(s, t):
        if t in s.SKIP and s.d: s.d -= 1
        elif t in s.BLOCO: s.o.append("\n")
    def handle_data(s, x):
        if not s.d: s.o.append(x)


def texto(path, mt):
    b = open(path, "rb").read()
    if mt == "application/pdf":
        import pypdf
        r = pypdf.PdfReader(path)
        t = "\n".join((p.extract_text() or "") for p in r.pages)
    else:
        p = T(); p.feed(b.decode("utf-8", "replace")); t = "".join(p.o)
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return b, t.strip()


os.makedirs(AQUI + "/raw_texto", exist_ok=True)
docs = []
for r in rows:
    path = ARM + r["storage_path"]
    b, t = texto(path, r["media_type"])
    sha = hashlib.sha256(b).hexdigest()
    did = "RAW-%d" % r["id"]
    open(AQUI + "/raw_texto/%s.txt" % did, "w", encoding="utf-8").write(t)
    docs.append(dict(DOCUMENT_ID=did, RAW_ASSET_ID=r["id"], SOURCE_ID=r["source_id"], URL=r["source_url"],
                     STORAGE_PATH=r["storage_path"], MEDIA_TYPE=r["media_type"], CAPTURED_AT=r["captured_at"],
                     RAW_SHA256_BANCO=r["sha256"], RAW_SHA256_ARQUIVO=sha, SHA_CONFERE=(sha == r["sha256"].strip()),
                     TEXTO_CHARS=len(t), TEXTO_SHA256=hashlib.sha256(t.encode()).hexdigest()))
    print(did, r["source_id"], r["media_type"], len(t), "SHA_OK" if sha == r["sha256"].strip() else "SHA_DIFERENTE")
json.dump(docs, open(AQUI + "/DOCUMENTOS_FAST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
