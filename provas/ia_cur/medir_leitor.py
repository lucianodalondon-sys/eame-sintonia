"""O conserto do leitor do canario no LIVRO INTEIRO (copia do vivo): o MESMO canario, duas vezes
por fonte — leitor antigo e leitor novo — sobre os MESMOS bytes (cada pagina buscada uma vez).
Transporte do robo; portao de egresso (superficie/rede.py) de 25 em 25 pedidos; robots pela porta
do robo; pausa por anfitriao. Saida: uma linha por fonte em LEITOR.jsonl.
uso: py medir_leitor.py <raiz da copia> <saida.jsonl>"""
import json, os, re, subprocess, sys, time
from datetime import datetime, timezone
from urllib.parse import urlparse

RAIZ, SAIDA = sys.argv[1], sys.argv[2]
os.chdir(RAIZ); sys.path.insert(0, RAIZ + "/curadoria")
import canario as CAN, gate_de_rota as GATE, ready_split as RS   # noqa: E402

NOVO = CAN.hrefs_da_entrada


def ANTIGO(b, index_url):                       # o leitor de antes de 5239309a, literal
    html = b.decode("utf-8", "replace")
    base = re.match(r"^(https?://[^/]+)", index_url).group(1)
    hrefs = set()
    for h in re.findall(r'href=["\']([^"\']+)["\']', html):
        if h.startswith("//"):
            h = "https:" + h
        elif h.startswith("/"):
            h = base + h
        elif not h.startswith("http"):
            continue
        hrefs.add(h.split("#")[0])
    return hrefs


def egresso():
    r = subprocess.run([sys.executable, "superficie/rede.py", "--portao-de-egresso", "IT"],
                       capture_output=True, text=True)
    return '"EGRESS_GATE": "PASS"' in r.stdout


CACHE, ULTIMO, ROBOTS, N = {}, {}, {}, [0]
real_buscar = CAN.buscar


def buscar(url):
    if url in CACHE:
        return CACHE[url]
    host = urlparse(url).netloc
    if host not in ROBOTS:
        try:
            ROBOTS[host] = GATE.robots_de(host)[0]
        except Exception:                        # noqa: BLE001
            ROBOTS[host] = None
    rp = ROBOTS[host]
    if rp is None:
        CACHE[url] = (0, b"", "ROBOTS_ILEGIVEL"); return CACHE[url]
    if not GATE.permitido(url, rp):
        CACHE[url] = (0, b"", "ROBOTS_PROIBE"); return CACHE[url]
    if N[0] % 25 == 0 and not egresso():
        sys.exit("PARAR: egresso IT nao passa (pedido %d)" % N[0])
    espera = 2.0 - (time.time() - ULTIMO.get(host, 0))
    if espera > 0:
        time.sleep(espera)
    N[0] += 1
    CACHE[url] = real_buscar(url)
    ULTIMO[host] = time.time()
    return CACHE[url]


CAN.buscar = buscar
con = {c["SOURCE_ID"]: c for c in json.load(open("curadoria/italy_contracts_curator.json", encoding="utf-8"))["FONTES"]}
import escrever_contratos as EC   # noqa: E402
for c in json.load(open("regras/italy_contracts_onboarded.json", encoding="utf-8"))["FONTES"]:
    if c["SOURCE_ID"] in con:
        continue
    # a linha do coletor nao traz IDENTITY (o canario so a usa DEPOIS de passar, para o DOCUMENT_ID):
    # a da casa, do molde, so para esta medicao
    idt = EC.contrato_html({"SOURCE_ID": c["SOURCE_ID"], "NOME": c.get("NAME") or "", "TERRITORY": c.get("TERRITORY"),
                            "URL": (c.get("ACQUISITION") or {}).get("INDEX_URL") or "https://x/"}, {})["IDENTITY"]
    con[c["SOURCE_ID"]] = dict(c, _ORIGEM="TABELA_DO_COLETOR", IDENTITY=c.get("IDENTITY") or idt)
alvo = [c for s, c in sorted(con.items())
        if (c.get("ACQUISITION") or {}).get("STRATEGY") == "HTML_LINK_DISCOVERY"
        and (c["ACQUISITION"].get("INDEX_URL") and c["ACQUISITION"].get("LINK_PATTERN"))]
feitos = set()
if os.path.exists(SAIDA):
    feitos = {json.loads(l)["SOURCE_ID"] for l in open(SAIDA, encoding="utf-8")}
out = open(SAIDA, "a", encoding="utf-8")
print("fontes HTML com INDEX+PATTERN:", len(alvo), "ja feitas:", len(feitos), flush=True)


def resumo(r, c):
    it = r.get("ITEM_ABERTO") or {}
    reg = None
    if r.get("PASS"):
        reg = RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "x"},
                                    {"DADOS": r}, c)["REGUA"]
    return {"PASS": r.get("PASS"), "CLASSE": r.get("CLASSE"), "HREFS": r.get("HREFS"),
            "ALVOS": r.get("DETAIL_ENUMERATED"), "ALVO": r.get("ALVO"), "PORQUE": (r.get("PORQUE") or "")[:160],
            "HTML_KIND": it.get("HTML_KIND"), "CAPA_OU_MATERIA": it.get("CAPA_OU_MATERIA"),
            "PARAGRAPH_CHARACTERS": it.get("PARAGRAPH_CHARACTERS"), "REGUA": reg}


for c in alvo:
    s = c["SOURCE_ID"]
    if s in feitos:
        continue
    linha = {"SOURCE_ID": s, "ORIGEM": c.get("_ORIGEM", "LIVRO_DO_ROBO"), "INDEX_URL": c["ACQUISITION"]["INDEX_URL"]}
    for nome, leitor in (("ANTIGO", ANTIGO), ("NOVO", NOVO)):
        CAN.hrefs_da_entrada = leitor
        try:
            r = CAN.canario_html(c)
        except Exception as e:                   # noqa: BLE001
            r = {"PASS": False, "CLASSE": "EXCECAO", "PORQUE": "%s: %s" % (type(e).__name__, str(e)[:100])}
        linha[nome] = resumo(r, c)
    st, b, _ = CACHE.get(c["ACQUISITION"]["INDEX_URL"], (None, b"", None))
    if b:
        for nome, leitor in (("HREFS_ANTIGO", ANTIGO), ("HREFS_NOVO", NOVO)):
            try:
                linha[nome] = len(leitor(b, linha["INDEX_URL"]))
            except Exception as e:           # noqa: BLE001
                linha[nome] = "EXCECAO: %s" % type(e).__name__
    out.write(json.dumps(linha, ensure_ascii=False) + "\n"); out.flush()
print("pedidos:", N[0], "fim", datetime.now().isoformat(), flush=True)
