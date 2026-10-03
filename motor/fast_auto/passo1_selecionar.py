# SINTONIA_FAST_V1 - passo 1: 20 RAW reais da tabela raw_asset -> texto legivel
# Le o banco SO em leitura (transacao read only) e o arquivo do armazem. Nao escreve nada fora desta pasta.
#
# CAMADA DE TEXTO (duas camadas, ambas neste ficheiro -- nao existe extrator paralelo):
#   (1) ESTRUTURA - descarta o texto que vem de casca: <nav> <header> <footer> <form> <aside> <button>
#       <select> <label> <input>, e de container cujo class/id carrega um TOKEN INTEIRO de casca (menu,
#       menu-item, breadcrumb, cookie, sidebar, widget, related, newsletter, login, sponsor, ...).
#       Token inteiro de proposito: o class do <body> do WordPress costuma conter "navigation" e casar
#       por substring engoliria a materia inteira (defeito medido -- ver provas/).
#   (2) REPETICAO - linha CURTA (<= 80 chars) que aparece em 3 ou mais documentos DA MESMA RODADA e' template
#       do site (menu, rodape, aviso de cookies, "conta ou e-mail", "senha esquecida").
#   GUARDA: se a limpeza derrubar o texto abaixo de 15% do bruto (em documento com mais de 2000 chars), a
#       limpeza e' tratada como suspeita: entrega-se o BRUTO e grava-se o motivo. Nunca corta o corpo em silencio.
#
# HASH: TEXTO_SHA256 e' o sha256 do texto GRAVADO em raw_texto/<DOC>.txt -- exatamente o que o passo2 le e manda
#   ao modelo. TEXTO_SHA256_NO_DISCO e' o sha256 do mesmo texto lido DE VOLTA do ficheiro (a prova de que o
#   ficheiro em disco e' aquilo que foi hasheado). O corte que o passo2 faz antes de enviar tem dono unico aqui
#   (LIMITE_ENTREGA_CHARS) e o passo2 grava TEXTO_ENTREGUE_SHA256: o hash passa a descrever o que o modelo viu.
import hashlib, html, json, os, re, subprocess, sys
from collections import Counter
from html.parser import HTMLParser

AQUI = os.path.abspath(sys.argv[1])  # pasta da rodada (o codigo fica no Git, os dados fora)
BASE = r"C:/Users/London1/sintonia-sala-italia"
ARM = BASE + "/armazem/"
PSQL = r"C:/Users/London1/orca/pgtmp/pgsql/bin/psql.exe"
IDS = json.load(open(AQUI + "/IDS.json", encoding="utf-8"))  # escrito pelo rodada_fast.py

LIMITE_ENTREGA_CHARS = int(os.environ.get("FAST_MAX_CHARS", 18000))  # dono unico: o passo2 le daqui
LIMITE_SUSPEITO = 0.15      # limpeza que derruba abaixo disto (em documento grande) e' suspeita...
PROSA_MINIMA = 400          # ...a nao ser que o corpo tenha sobrevivido: prosa = chars em linhas com 80+
MINIMO_PARA_SUSPEITAR = 2000
LINHA_TEMPLATE_MAX = 80
REPETICOES_TEMPLATE = 3

env = dict(os.environ, PGPASSFILE=BASE + "/pgpass.conf", PGCLIENTENCODING="UTF8")
dsn = open(BASE + "/SALA_DSN.txt").read().strip()
sql = ("begin transaction read only; show transaction_read_only; "
       "select row_to_json(t) from (select id,run_id,source_id,source_url,storage_path,media_type,bytes,sha256,"
       "captured_at,document_key,identity_state,(select json_build_object('ID',d.id,'SHA256',d.sha256,"
       "'STORAGE_PATH',d.storage_path,'PRODUTOR',d.producer||'@'||coalesce(d.producer_version::text,'NAO_SEI')) "
       "from derived_artifact d where d.raw_asset_id=raw_asset.id and d.kind='TRANSCRIPTION' order by d.id desc "
       "limit 1) transcricao from raw_asset where id in (%s) order by id) t; commit;"
       % ",".join(map(str, IDS)))
out = subprocess.run([PSQL, "-w", "-X", "-A", "-t", "-c", sql, dsn], env=env, capture_output=True, text=True, encoding="utf-8").stdout
linhas = [l for l in out.splitlines() if l.strip()]
assert "on" in [l.strip() for l in linhas], ("transacao nao estava read only", linhas[:3])
rows = [json.loads(l) for l in linhas if l.startswith("{")]
assert len(rows) == len(IDS), (len(rows), len(IDS))

TAGS_CASCA = {"nav", "header", "footer", "form", "aside", "button", "select", "label", "input"}
TOKENS_CASCA = {"menu", "menu-item", "menu-label", "menulabel", "navbar", "submenu", "megamenu",
                "breadcrumb", "breadcrumbs", "cookie", "cookiebanner", "cmplz-cookiebanner", "widget", "sidebar",
                "related", "correlati", "correlate", "leggi-anche", "leggianche", "newsletter", "subscribe",
                "abbonati", "abbonamento", "login", "login-form", "search-form", "searchform", "subscr", "consent",
                "gdpr", "sponsor", "sponsorizzato", "pagination", "paginazione", "social", "share", "tagcloud",
                "skip-link", "site-header", "site-footer", "main-menu", "primary-menu", "secondary-menu",
                "topbar", "toolbar", "widget-area", "consenso"}
# fora da lista, de proposito: "navigation" -- e' TOKEN do class do <body> em tema WordPress e marcaria a
# pagina inteira como casca (defeito medido: derrubou o corpo de 9323 para 24 chars numa prova).
PREFIXOS_CASCA = ("menu-item-", "menu-", "td_block_wrap", "td_block", "td_module", "cmplz-")


class T(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head", "template"}
    BLOCO = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "tr", "section", "article", "td", "header", "footer"}

    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.o = []
        s.d = 0
        s.p = []
        s.casca = Counter()

    def _motivo(s, t, a):
        if t in TAGS_CASCA:
            return "<%s>" % t
        at = dict(a)
        for chave in ("class", "id", "role", "aria-label"):
            for x in (at.get(chave) or "").split():
                xl = x.lower()
                if xl in TOKENS_CASCA or xl.startswith(PREFIXOS_CASCA):
                    return x[:40]
        return None

    def _casca(s):
        for t, m in reversed(s.p):
            if m:
                return m
        return None

    def handle_starttag(s, t, a):
        if t in s.SKIP:
            s.d += 1
            return
        if t == "body" and s.d:      # <head>/<title> sem fecho deixava o corpo inteiro em silencio
            s.d = 0                  # (defeito medido numa prova: documento entregue com 24 caracteres)
        s.p.append((t, s._motivo(t, a)))
        if t in s.BLOCO:
            s.o.append("\n")

    def handle_endtag(s, t):
        if t in s.SKIP:
            if s.d:
                s.d -= 1
            return
        for i in range(len(s.p) - 1, -1, -1):
            if s.p[i][0] == t:
                del s.p[i:]
                break
        if t in s.BLOCO:
            s.o.append("\n")

    def handle_data(s, x):
        if s.d:
            return
        m = s._casca()
        if m:
            if x.strip():
                s.casca[m] += len(re.sub(r"[ \t\u00a0]+", " ", x))
        else:
            s.o.append(x)


def normaliza(t):
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def transcricao(r):
    """v0.3 §7A: video/audio entra pela TRANSCRICAO que a Collection ja gravou (derived_artifact). O texto e
    lido do armazem e o sha256 tem de bater com o do banco; nao bate = o passo para (nunca texto nao provado)."""
    tr = r.get("transcricao")
    if not tr:
        return None
    tb = open(ARM + tr["STORAGE_PATH"], "rb").read()
    assert hashlib.sha256(tb).hexdigest() == tr["SHA256"].strip(), ("TRANSCRICAO_SHA_NAO_CONFERE", r["id"], tr["ID"])
    return tb.decode("utf-8")


def bruto(path, mt, texto_transcrito=None):
    b = open(path, "rb").read()
    if texto_transcrito is not None:
        return b, texto_transcrito, Counter()
    if mt == "application/pdf":
        import pypdf
        r = pypdf.PdfReader(path)
        return b, "\n".join((p.extract_text() or "") for p in r.pages), Counter()
    p = T()
    p.feed(b.decode("utf-8", "replace"))
    return b, "".join(p.o), p.casca


def linhas_de_template(textos):
    vistos = Counter()
    for t in textos.values():
        for l in {re.sub(r"\s+", " ", x).strip().lower() for x in t.split("\n")}:
            if 15 < len(l) <= LINHA_TEMPLATE_MAX:
                vistos[l] += 1
    return {l for l, n in vistos.items() if n >= REPETICOES_TEMPLATE}


def tira_template(t, template):
    fora, n, chars = [], 0, 0
    for l in t.split("\n"):
        if re.sub(r"\s+", " ", l).strip().lower() in template:
            n += 1
            chars += len(l)
            continue
        fora.append(l)
    return normaliza("\n".join(fora)), n, chars


os.makedirs(AQUI + "/raw_texto", exist_ok=True)
preparo = []
for r in rows:
    path = ARM + r["storage_path"]
    b, t_bruto, casca = bruto(path, r["media_type"], transcricao(r))
    preparo.append((r, b, normaliza(t_bruto), casca, t_bruto))

template = linhas_de_template({r["id"]: t for r, b, t, c, n in preparo})

docs = []
for r, b, t_corpo, casca, t_bruto in preparo:
    did = "RAW-%d" % r["id"]
    limpo, linhas_removidas, chars_linhas = tira_template(t_corpo, template)
    prosa = sum(len(l) for l in limpo.split("\n") if len(l) >= 80)
    motivo = "LIMPO"
    if len(limpo) < LIMITE_SUSPEITO * len(t_corpo) and len(t_corpo) > MINIMO_PARA_SUSPEITAR and prosa < PROSA_MINIMA:
        limpo, motivo = t_corpo, "LIMPEZA_SUSPEITA_MANTIDO_BRUTO"
    sha = hashlib.sha256(b).hexdigest()
    with open(AQUI + "/raw_texto/%s.txt" % did, "w", encoding="utf-8", newline="\n") as f:
        f.write(limpo)
    lido = open(AQUI + "/raw_texto/%s.txt" % did, "rb").read()   # o ficheiro como ele esta' no disco
    docs.append(dict(DOCUMENT_ID=did, RAW_ASSET_ID=r["id"], SOURCE_ID=r["source_id"], URL=r["source_url"],
                     DOCUMENT_KEY=r.get("document_key") or "NAO_SEI",  # identidade do ledger (Scrap), so copiada
                     TEXTO_ORIGEM=("TRANSCRIPTION" if r.get("transcricao") else "TEXT_EXTRACTION"),
                     TRANSCRICAO=(r.get("transcricao") or "NAO_APLICAVEL"),  # DERIVED id/sha/produtor, so copiados
                     STORAGE_PATH=r["storage_path"], MEDIA_TYPE=r["media_type"], CAPTURED_AT=r["captured_at"],
                     RAW_SHA256_BANCO=r["sha256"], RAW_SHA256_ARQUIVO=sha, SHA_CONFERE=(sha == r["sha256"].strip()),
                     TEXTO_BRUTO_CHARS=len(t_corpo),
                     CASCA_POR_ESTRUTURA_CHARS=sum(casca.values()),
                     CASCA_POR_ESTRUTURA_MOTIVOS=dict(casca.most_common(5)),
                     CASCA_POR_REPETICAO_LINHAS=linhas_removidas,
                     CASCA_POR_REPETICAO_CHARS=chars_linhas,
                     LIMPEZA=motivo, TEXTO_CHARS=len(limpo),
                     TEXTO_SHA256=hashlib.sha256(limpo.encode("utf-8")).hexdigest(),
                     TEXTO_SHA256_NO_DISCO=hashlib.sha256(lido).hexdigest(),
                     LIMITE_ENTREGA_CHARS=LIMITE_ENTREGA_CHARS,
                     ENTREGA_CORTADA=(len(limpo) > LIMITE_ENTREGA_CHARS)))
    print(did, r["source_id"], r["media_type"], len(t_corpo), "->", len(limpo),
          "casca=%d" % sum(casca.values()), "linhas=%d" % linhas_removidas, motivo,
          "SHA_OK" if sha == r["sha256"].strip() else "SHA_DIFERENTE")
json.dump(docs, open(AQUI + "/DOCUMENTOS_FAST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tb = sum(d["TEXTO_BRUTO_CHARS"] for d in docs)
tc = sum(d["TEXTO_CHARS"] for d in docs)
print("TOTAL bruto=%d entregue=%d removido=%d (%.1f%%) linhas_de_template=%d" % (
    tb, tc, tb - tc, 100.0 * (tb - tc) / max(1, tb), len(template)))
