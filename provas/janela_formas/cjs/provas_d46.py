"""D46: provas com rede, trabalho leve. Portao de consenso PASS IT antes de tudo.
Puglia (agrometeopuglia): robots VIVO pelo leitor da casa (GATE.robots_de) e guardado inteiro; /api/ tem de
ser permitido ANTES do 1.o pedido a API; pagina /bollettini numa visita nova (cookies so desta visita);
a chave so vai para a API se a pagina ao vivo tiver drupalSettings.api (condicao 1: a chave entregue E o
parametro api) — nada de chutar `key` no lugar de `api`. Depois 1 PDF, se o seu host for permitido.
Emilia-Romagna: 1 pedido ++api++ por provincia (4), robots da copia da medicao RFC (grupo * so proibe
/search e afins). D38: no maximo 5 pedidos por dominio registado; 5 s entre pedidos ao mesmo anfitriao.
Login/bloqueio (401/403/429 ou pagina de login) = parar a fonte."""
import hashlib, http.cookiejar, json, re, subprocess, sys, time, urllib.request, urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path("C:/Users/London1/orca/workspaces/eame-sintonia/janela-formas-v1")
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN, capturador as CAP, gate_de_rota as GATE   # noqa: E402

r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py",
                    "--portao-de-egresso", "IT"], capture_output=True, text=True)
assert '"EGRESS_GATE": "PASS"' in r.stdout, "portao de egresso nao da PASS IT:\n" + r.stdout[-800:]

PASTA = Path("C:/cur/cjs/d46"); PASTA.mkdir(parents=True, exist_ok=True)
DOM, ULT, LOG = {}, {}, []
PAUSA = 5.0


def dominio(host):
    return ".".join(host.split(".")[-2:])


def guardar(nome, b):
    h = hashlib.sha256(b).hexdigest()
    p = PASTA / nome; p.write_bytes(b)
    return h, str(p)


def pedir(url, opener=None, nome=None, conta=True):
    host = url.split("/")[2]
    if conta:
        if DOM.get(dominio(host), 0) >= 5:
            LOG.append({"URL": url, "ESTADO": "TETO_D38"}); return None, b""
        DOM[dominio(host)] = DOM.get(dominio(host), 0) + 1
    w = PAUSA - (time.time() - ULT.get(host, 0))
    if w > 0: time.sleep(w)
    if opener is None:
        st, b, e = CAN.buscar(url)
    else:
        req = urllib.request.Request(url, headers={"User-Agent": CAP.UA, "Accept": "*/*",
                                                   "Accept-Language": "it-IT,it;q=0.9"})
        try:
            with opener.open(req, timeout=60) as resp:
                st, b, e = resp.status, resp.read(8_000_000), ""
        except urllib.error.HTTPError as ex:
            st, b, e = ex.code, b"", "HTTP %d" % ex.code
        except Exception as ex:
            st, b, e = 0, b"", "%s: %s" % (type(ex).__name__, str(ex)[:90])
    ULT[host] = time.time()
    lin = {"URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b), "LIDO_EM": datetime.now(timezone.utc).isoformat()}
    if nome and b:
        lin["SHA256"], lin["EM"] = guardar(nome, b)
    LOG.append(lin); print(st, len(b), url)
    return st, b


def robots_vivo(host):
    DOM[dominio(host)] = DOM.get(dominio(host), 0) + 1
    rp, txt = GATE.robots_de(host)
    ULT[host] = time.time()
    b = (txt if isinstance(txt, str) else str(txt)).encode("utf-8")
    h, p = guardar("robots-%s.txt" % host, b)
    LOG.append({"URL": "https://%s/robots.txt" % host, "ROBOTS": True, "SHA256": h, "EM": p, "BYTES": len(b)})
    return rp


RES = {}

# ---------------- Puglia ----------------
P = {"PASSOS": []}
rp = robots_vivo("www.agrometeopuglia.it")
api_url = "https://www.agrometeopuglia.it/api/bollettini?api=X&tipologia=Settimanale"
P["ROBOTS_API_PERMITIDO"] = GATE.permitido(api_url, rp)
P["ROBOTS_PAGINA_PERMITIDO"] = GATE.permitido("https://www.agrometeopuglia.it/bollettini", rp)
if not (P["ROBOTS_API_PERMITIDO"] and P["ROBOTS_PAGINA_PERMITIDO"]):
    P["FIM"] = "ROBOTS_PROIBE — fora (D46 (2))"
else:
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(context=CAN.CTX))
    st, b = pedir("https://www.agrometeopuglia.it/bollettini", op, "pagina-bollettini.html")
    m = re.search(rb'data-drupal-selector="drupal-settings-json">([^<]*)<', b or b"")
    ds = json.loads(m.group(1)) if m else {}
    P["PAGINA_HTTP"] = st
    P["DRUPALSETTINGS_CHAVES"] = sorted(ds.keys())
    P["TEM_API"] = "api" in ds
    P["TEM_KEY"] = "key" in ds
    P["REMOTE_ADDR_E_O_NOSSO"] = ds.get("REMOTE_ADDR")
    P["LOGIN_NA_PAGINA"] = bool(re.search(rb"user/login|type=\"password\"", b or b""))
    if st in (401, 403, 429) or P["LOGIN_NA_PAGINA"]:
        P["FIM"] = "LOGIN/BLOQUEIO — fora (D46 (4))"
    elif not P["TEM_API"]:
        P["FIM"] = "CONDICAO_1_NAO_CONFIRMADA — a pagina nao entrega drupalSettings.api; API NAO chamada"
    else:
        chave = ds["api"]
        st2, b2 = pedir("https://www.agrometeopuglia.it/api/bollettini?api=%s&tipologia=Settimanale" % chave, op, "api-settimanale.json")
        P["API_HTTP"] = st2
        try:
            dados = json.loads(b2)
        except Exception:
            dados = None
        P["API_E_JSON"] = dados is not None
        lista = dados if isinstance(dados, list) else (dados or {}).get("data") if isinstance(dados, dict) else None
        if isinstance(lista, list) and lista:
            P["API_N"] = len(lista)
            P["API_CAMPOS"] = sorted(lista[0].keys())
            P["API_PRIMEIRO"] = {k: lista[0].get(k) for k in ("NUMBER", "DATA_EMISSIONE_FORMAT", "DATA_VALIDITA_FORMAT", "PATH_COMP")}
            pc = lista[0].get("PATH_COMP") or ""
            pdf = ("https://www.agrometeopuglia.it/" + pc) if "bollettino-elettronico" in pc else \
                  ("http://wwwold.agrometeopuglia.it/opencms/Documenti/" + pc)
            P["PDF_URL"] = pdf
            host = pdf.split("/")[2]
            rp2 = rp if host == "www.agrometeopuglia.it" else robots_vivo(host)
            if GATE.permitido(pdf, rp2):
                st3, b3 = pedir(pdf, op, "boletim.pdf")
                P["PDF_HTTP"] = st3
                P["PDF_E_PDF"] = (b3 or b"")[:5] == b"%PDF-"
                P["PDF_BYTES"] = len(b3 or b"")
            else:
                P["PDF"] = "ROBOTS_PROIBE"
        P["FIM"] = "FEITO"
    jar.clear()   # chave e cookies desta visita nao ficam para outra (D46 (3))
RES["PUGLIA"] = P

# ---------------- Emilia-Romagna ----------------
E = {"PROVINCIAS": []}
rpe = urllib.robotparser.RobotFileParser()
rpe.parse(Path("C:/cur/rfc/rede/robots/agricoltura.regione.emilia-romagna.it.txt").read_text(encoding="utf-8", errors="replace").splitlines())
base = "https://agricoltura.regione.emilia-romagna.it/++api++/fitosanitario/difesa-sostenibile/bollettini/bollettini-interprovinciali-di-produzione-integrata-e-biologica-2026/"
for prov in ("bologna-e-ferrara", "forli-cesena-ravenna-rimini", "modena-reggio-emilia", "parma-piacenza"):
    u = base + prov
    if not GATE.permitido(u, rpe):
        E["PROVINCIAS"].append({"PROV": prov, "ESTADO": "ROBOTS_PROIBE"}); continue
    st, b = pedir(u, None, "er-%s.json" % prov)
    lin = {"PROV": prov, "HTTP": st}
    try:
        d = json.loads(b)
        lin.update(TIPO=d.get("@type"), TITULO=d.get("title"), EFFECTIVE=d.get("effective"), MODIFIED=d.get("modified"),
                   ITEMS_TOTAL=d.get("items_total"),
                   FILHOS=[{"id": i.get("@id", "").rsplit("/", 1)[-1], "tipo": i.get("@type"), "titulo": i.get("title")}
                           for i in (d.get("items") or [])][:60],
                   BLOCOS=sorted({v.get("@type") for v in (d.get("blocks") or {}).values()}),
                   DOWNLOADS=len(re.findall(r"@@download", b.decode("utf-8", "replace"))))
    except Exception as ex:
        lin["ERRO_JSON"] = str(ex)[:80]
    E["PROVINCIAS"].append(lin)
RES["EMILIA_ROMAGNA"] = E
RES["PEDIDOS_POR_DOMINIO"] = DOM
RES["LOG"] = LOG
json.dump(RES, open(PASTA / "RESULTADO-D46.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in RES.items() if k != "LOG"}, ensure_ascii=False, indent=1)[:6000])
