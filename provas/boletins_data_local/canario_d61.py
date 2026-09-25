"""BOLETINS D61/D62 fase 3 — os contratos das rotas de boletim pela PORTA (reparar_contrato.aplicar, numa
COPIA — nada escrito nos livros vivos) e o canario de cada um, com a data de emissao, o periodo e a area
que a ROTA declara (PUBLISHED_AT / FACT_TIME / FACT_LOCATION + _BASIS), NAO SEI com o porque quando o
boletim nao os diz (D62: nada e obrigatorio, nada e descartado).

Bytes: a lista e os documentos que as fases 1/2 (e a T2-BOLETINS/Umbria) ja guardaram hoje. Se o canario
escolher um documento que nao esta guardado, busca-o de verdade: portao PASS IT, robots guardado na fase 2
(RFC 9309 + D39), teto D38 pela mesma conta, 5 s (10 s com Crawl-delay).
Base = o contrato do livro VIVO do Curator (so leitura).
uso: py provas/boletins_data_local/canario_d61.py <pasta d61> --rede-autorizada <missao>"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--rede-autorizada")
a = ap.parse_args()
if not (a.rede_autorizada or "").strip():
    sys.exit("RECUSA (D41.3): sem --rede-autorizada <missao> nao vai a rede")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402
import capturador as CAP         # noqa: E402
import ready_split as RS         # noqa: E402
import reparar_contrato as RC    # noqa: E402
_s = importlib.util.spec_from_file_location(
    "robots_rfc9309", "C:/Users/London1/orca/workspaces/eame-sintonia/robots-rfc9309-v1/coleta/robots_rfc9309.py")
RR = importlib.util.module_from_spec(_s); sys.modules["robots_rfc9309"] = RR; _s.loader.exec_module(RR)
LIVRO_VIVO = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/curadoria/italy_contracts_curator.json")
OUT = Path(a.pasta)

r = subprocess.run([sys.executable, "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/superficie/rede.py",
                    "--portao-de-egresso", "IT"], capture_output=True, text=True)
if '"EGRESS_GATE": "PASS"' not in r.stdout:
    sys.exit("PARAR: portao de egresso de consenso nao da PASS IT")


def opc(frm, pattern, n, flags=None):
    c = {"FROM": frm, "PATTERN": pattern, "REQUIRED": False, "DEFAULTS": ["x"] * n}
    if flags:
        c["FLAGS"] = flags
    return c


URL_DOC = {"FROM": "URL", "PATTERN": "^https?://[^/]+/?(.*?)/?$"}
DATA_IT = r"(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})"

RECEITAS = {
    "IT-T2-148": {   # ARSAC Calabria — uma pagina por edicao (HTML)
        "INDEX_URL": "https://arsac.calabria.it/category/ultime-notizie/",
        "LINK_PATTERN": r"^https?://arsac\.calabria\.it/bollettino-agrometeorologico-e-fitosanitario-[a-z0-9-]*valido-fino-[a-z0-9-]*-20\d{2}/?$",
        "OUTPUT_TYPE": "HTML",
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {
                "doc": URL_DOC,
                "pa": opc("PAGE_TEXT", r"Settimana\s+\d+\s*\((\d{1,2})/(\d{1,2})/(\d{4})\s*[–-]\s*(\d{1,2})/(\d{1,2})/(\d{4})\)", 6),
                "pb": opc("PAGE_TEXT", r"Settimana\s+\d+\s+dal\s+(?:dal\s+)?(\d{1,2})/(\d{1,2})\s+al\s+(\d{1,2})/(\d{1,2})/(\d{4})", 5),
                "loc": opc("PAGE_TEXT", r"mandato della Regione (\w+)[^\n]{0,300}?tutto il territorio regionale suddiviso in (\d+) aree", 2),
            },
            "DOCUMENT_ID": "IT-T2-148:URL:{doc.1}",
            "FACT_TIME": ["{pa.3}-{pa.2:MES2}-{pa.1:DIA2}/{pa.6}-{pa.5:MES2}-{pa.4:DIA2}",
                          "{pb.5}-{pb.2:MES2}-{pb.1:DIA2}/{pb.5}-{pb.4:MES2}-{pb.3:DIA2}"],
            "FACT_TIME_BASIS": "VALIDADE_DECLARADA_NA_PAGINA_DA_EDICAO · «Pubblicato il bollettino Settimana NN (…)»",
            "PUBLISHED_AT_BASIS": ("NAO_DECLARADA_NA_PAGINA · a pagina da edicao so diz «Ultima modifica» (a ultima "
                                   "alteracao, nao a emissao) e «valido fino al …» (o fim da validade)"),
            "FACT_LOCATION": "{loc.1} — tutto il territorio regionale ({loc.2} aree climaticamente omogenee)",
            "FACT_LOCATION_BASIS": "AREA_DECLARADA_NA_PAGINA_DA_EDICAO · «riguardanti tutto il territorio regionale suddiviso in N aree»",
            "FACT_TIME_NOTA": "o ano do inicio, na forma 2, e o do fim: so vale se o intervalo ficar coerente (virada do ano = NAO SEI)",
        },
        "PORQUE": "o site antigo arsacweb.it parou em 2022; as edicoes vivas sao paginas em arsac.calabria.it (uma por semana)",
    },
    "IT-T3-032": {   # Molise — anexos PDF da pagina 18077
        "INDEX_URL": "https://www.regione.molise.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/18077",
        "LINK_PATTERN": r"^https?://www\.regione\.molise\.it/flex/cm/pages/ServeAttachment\.php/L/IT/D/[^/]+/P/BLOB%3AID%3D18077/E/pdf\?mode=download$",
        "OUTPUT_TYPE": "PDF",
        "PDF_SEM_EXTENSAO": "o anexo e servido por ServeAttachment.php …/E/pdf?mode=download (sem «.pdf»); medido: %PDF- nos bytes",
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {
                "doc": URL_DOC,
                "vig": opc("PDF_TEXT", r"[Bb]ollettino\s+(?:di\s+)?vig[i]?l[i]?anza\s+del\s+(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", 3),
            },
            "DOCUMENT_ID": "IT-T3-032:URL:{doc.1}",
            "PUBLISHED_AT": "{vig.3}-{vig.2:MES2}-{vig.1:DIA2}",
            "PUBLISHED_AT_BASIS": ("EMISSAO_DECLARADA_NO_PDF · «Bollettino vigilanza del DD-MM-AAAA» (so os de vigilanza; "
                                   "o «Comunicato fitosanitario N» medido nao traz data de emissao — a data esta so no titulo da lista)"),
            "FACT_TIME_BASIS": "NAO_DECLARADO · o comunicato nao declara periodo de validade ou de observacao",
            "FACT_LOCATION_BASIS": "NAO_DECLARADA · o cabecalho e o do publicador (Regione Molise) — SOURCE_LOCATION nao e FACT_LOCATION",
        },
        "PORQUE": "os comunicados e boletins de vigilanza sao anexos PDF da pagina fitossanitaria",
    },
    "IT-T3-055": {   # Valle d'Aosta — avisos PDF (allegato.aspx)
        "INDEX_URL": "https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/frutticoltura_i.asp",
        "LINK_PATTERN": r"^https?://www\.regione\.vda\.it/allegato\.aspx\?pk=\d+$",
        "OUTPUT_TYPE": "PDF",
        "PDF_SEM_EXTENSAO": "o aviso e servido por allegato.aspx?pk=N (sem «.pdf»); medido: %PDF- nos bytes",
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {
                "doc": URL_DOC,
                "em": opc("PDF_TEXT", r"Avviso\s+fitosanitario\s+del\s+" + DATA_IT, 3, "i"),
            },
            "DOCUMENT_ID": "IT-T3-055:URL:{doc.1}",
            "PUBLISHED_AT": "{em.3}-{em.2:MES_IT}-{em.1:DIA2}",
            "PUBLISHED_AT_BASIS": "EMISSAO_DECLARADA_NO_AVISO · «Avviso fitosanitario del <data>»",
            "FACT_TIME_BASIS": "NAO_DECLARADO · o aviso nao declara periodo",
            "FACT_LOCATION_BASIS": ("NAO_DECLARADA · o aviso nao declara uma area propria; as zonas citadas no texto "
                                    "(ex.: «fino a Saint Pierre») sao do leitor do texto (LUGAR-FATO), nao da rota"),
        },
        "PORQUE": "os avisos de frutticoltura sao anexos PDF na pagina",
    },
    "IT-T3-053": {   # Umbria — Liferay (a identidade por endereco preservada; data e area acrescentadas)
        "INDEX_URL": "https://www.regione.umbria.it/agricoltura/bollettini-fitosanitari",
        "LINK_PATTERN": r"^https?://(www\.)?regione\.umbria\.it/documents/18/\d+/bollettino\+[^/]+/[0-9a-f-]{36}\?version=[\d.]+$",
        "OUTPUT_TYPE": "PDF",
        "PDF_SEM_EXTENSAO": "Liferay …/bollettino+<cultura>+n.N+del+<data>[.pdf]/<uuid>?version= — 27 de 52 sem «.pdf»; medido: %PDF- nos bytes",
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {
                "doc": URL_DOC,
                "cab": opc("PDF_TEXT", r"N\.\s*\d+\s+del\s+(\d{1,2})/(\d{1,2})/(\d{2,4})", 3),
                "nome": opc("URL", r"\+del\+{1,2}(\d{1,2})_(\d{1,2})_(\d{2,4})", 3),
                "area": opc("PDF_TEXT", r"valido per le province di ([A-Z][a-z]+(?: e [A-Z][a-z]+)*)", 1),
            },
            "DOCUMENT_ID": "IT-T3-053:URL:{doc.1}",
            "PUBLISHED_AT": ["{cab.3:ANO4}-{cab.2:MES2}-{cab.1:DIA2}", "{nome.3:ANO4}-{nome.2:MES2}-{nome.1:DIA2}"],
            "PUBLISHED_AT_BASIS": "EMISSAO_DECLARADA_NO_BOLETIM · cabecalho «N.NN del DD/MM/AAAA» (forma 1) ou nome do ficheiro «del DD_MM_AA» (forma 2)",
            "FACT_TIME_BASIS": "NAO_DECLARADO · o boletim nao declara o periodo (o grafico diz «del periodo» sem datas)",
            "FACT_LOCATION": "{area.1}",
            "FACT_LOCATION_BASIS": "AREA_DECLARADA_NO_BOLETIM · «valido per le province di …»",
        },
        "PORQUE": "D51.3 + D61/D62: a rota PDF com a data e a area do boletim",
    },
    "IT-T2-051": {   # ARPAE — a receita da D47, agora com o periodo do PDF
        "INDEX_URL": "https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo/bollettini-2026",
        "LINK_PATTERN": (r"^https?://(www\.)?arpae\.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/"
                         r"bollettini-agrometeo/bollettini-2026/\d{2}_boll_agro_\d{8}(-\d+)?\.pdf$"),
        "OUTPUT_TYPE": "PDF", "STRIP_SUFFIX": "/view",
        "IDENTITY": {
            "STRATEGY": "CONTENT_CAPTURE",
            "CAPTURES": {
                "b": {"FROM": "URL", "PATTERN": r"/(\d{2})_boll_agro_(\d{4})(\d{2})(\d{2})(?:-\d+)?\.pdf$"},
                "em": opc("PDF_TEXT", r"n\.\s*\d+/\d{4}\s+del\s+" + DATA_IT, 3, "i"),
                "per": opc("PDF_TEXT", DATA_IT + r"\s*-\s*" + DATA_IT, 6, "i"),
                "nome": opc("URL", r"_boll_agro_(\d{4})(\d{2})(\d{2})", 3),
            },
            "DOCUMENT_ID": "IT-T2-051:BOLETIM:AGROMETEO:{b.2}-{b.1}",
            "SOURCE_DATE_ISO": "{b.2}-{b.3}-{b.4}",
            "FACT_TIME": "{per.3}-{per.2:MES_IT}-{per.1:DIA2}/{per.6}-{per.5:MES_IT}-{per.4:DIA2}",
            "FACT_TIME_BASIS": "PERIODO_DE_OBSERVACAO_DECLARADO_NO_BOLETIM · 2.a linha «<data> - <data>» do PDF",
            "PUBLISHED_AT": ["{em.3}-{em.2:MES_IT}-{em.1:DIA2}", "{nome.1}-{nome.2}-{nome.3}"],
            "PUBLISHED_AT_BASIS": "EMISSAO_DECLARADA_NO_BOLETIM · cabecalho «n. NN/AAAA del <data>» (forma 1) ou o nome AAAAMMDD (forma 2)",
            "FACT_LOCATION_BASIS": "NAO_DECLARADA · o boletim cobre a regiao mas nao a declara no cabecalho (lugares no corpo: leitor LUGAR-FATO)",
        },
        "PORQUE": "D47 + D61/D62: o periodo e a emissao lidos no PDF",
    },
}
BYTES_GUARDADOS = {}   # url -> caminho: listas e documentos ja buscados hoje
for f in ("FASE1.json", "FASE2-ITENS.json"):
    d = json.loads((OUT / f).read_text(encoding="utf-8"))
    for x in d.get("RESULTADOS", []):
        if x.get("PAGINA"):
            BYTES_GUARDADOS[x["PAGINA"]["URL"]] = x["PAGINA"]["EM"]
    for x in d.get("ITENS", {}).values():
        if x.get("ITEM"):
            BYTES_GUARDADOS[x["ITEM"]["URL"]] = x["ITEM"]["EM"]
for f, chave in (("C:/cur/umbria/UMBRIA-LISTA.json", "LISTA"),):
    x = json.loads(Path(f).read_text(encoding="utf-8"))[chave]; BYTES_GUARDADOS[x["URL"]] = x["EM"]
um = json.loads(Path("C:/cur/umbria/UMBRIA-CANARIO.json").read_text(encoding="utf-8"))
for x in um["PEDIDOS"]:
    if x["URL"].startswith("https://www.regione.umbria.it/documents/"):
        BYTES_GUARDADOS[x["URL"]] = x["EM"]
t2 = json.loads(Path("C:/cur/t2b/CANARIO-ARPAE.json").read_text(encoding="utf-8"))
BYTES_GUARDADOS[t2["LISTAGEM_GUARDADA"]["URL"]] = json.loads(Path("C:/cur/t2b/FASE1.json").read_text(encoding="utf-8"))["RESULTADOS"][4]["PAGINA"]["EM"]
for x in t2["PEDIDOS_A_REDE"]:
    if x["URL"].endswith(".pdf"):
        BYTES_GUARDADOS[x["URL"]] = x["EM"]

CONTA = OUT / "PEDIDOS-POR-DOMINIO.json"
DOM = json.loads(CONTA.read_text(encoding="utf-8"))
ROBOTS = {}
F2 = json.loads((OUT / "FASE2-ITENS.json").read_text(encoding="utf-8"))
for x in F2["ITENS"].values():
    rb = x["ROBOTS"]
    ROBOTS[rb["URL"].split("/")[2]] = RR.de_resposta(rb["HTTP"] or None, Path(rb["EM"]).read_bytes())
REDE, VEIO_DE = [], []


def dominio(host):
    return ".".join(host.split(".")[-2:])


def buscar(url):
    if url in BYTES_GUARDADOS:
        VEIO_DE.append({"URL": url, "DE": "GUARDADO HOJE", "EM": BYTES_GUARDADOS[url]})
        return 200, Path(BYTES_GUARDADOS[url]).read_bytes(), ""
    host = url.split("/")[2]
    rob = ROBOTS.get(host)
    if rob is None:
        return 0, b"", "SEM ROBOTS GUARDADO PARA %s — nao se pede" % host
    dec = rob.decidir(CAP.UA, url)
    if not dec.permite:
        return 0, b"", "ROBOTS_RECUSA: " + dec.regra
    d = dominio(host)
    if DOM.get(d, 0) >= 5:
        return 0, b"", "TETO_D38"
    DOM[d] = DOM.get(d, 0) + 1
    CONTA.write_text(json.dumps(DOM, indent=1), encoding="utf-8")
    time.sleep(max(5.0, rob.crawl_delay(CAP.UA) or 0))
    st, b, e = REAL(url)
    b = b or b""
    h = hashlib.sha256(b).hexdigest()
    p = OUT / "bytes" / ("%s.bin" % h[:20]); p.write_bytes(b)
    REDE.append({"URL": url, "HTTP": st, "ERRO": e, "BYTES": len(b), "SHA256": h, "EM": str(p),
                 "LIDO_EM": datetime.now(timezone.utc).isoformat()})
    BYTES_GUARDADOS[url] = str(p)
    VEIO_DE.append({"URL": url, "DE": "REDE AGORA", "EM": str(p)})
    return st, b, e


REAL = CAN.buscar
CAN.buscar = buscar
livro = {c["SOURCE_ID"]: c for c in json.loads(LIVRO_VIVO.read_text(encoding="utf-8"))["FONTES"]}
saida = {"FASE": "BOLETINS D61/D62 fase 3 — contratos pela porta + canario", "REDE_AUTORIZADA_POR": a.rede_autorizada,
         "EM": datetime.now(timezone.utc).isoformat(), "FONTES": {}}
for sid, rec in RECEITAS.items():
    base = livro[sid]
    proposta = dict({k: v for k, v in rec.items() if k != "PORQUE"}, DESFECHO="PADRAO_NOVO",
                    COMO="D61/D62 boletins (bancada, agente)", PORQUE=rec["PORQUE"])
    proposta["IDENTITY"] = {k: v for k, v in rec["IDENTITY"].items() if k != "FACT_TIME_NOTA"}
    lin = {"CONTRATO_BASE_HASH": base.get("SOURCE_CONTRACT_HASH")}
    try:
        novo = RC.aplicar(base, proposta)
    except RC.ReparoInvalido as e:
        lin["PORTA"] = "RECUSOU: %s" % e
        saida["FONTES"][sid] = lin; print(sid, lin["PORTA"][:200]); continue
    lin["PORTA"] = "ACEITOU"
    lin["CONTRATO_PROPOSTO"] = novo
    lin["IDENTIDADE_DOCUMENT_ID_PRESERVADA"] = novo["IDENTITY"]["DOCUMENT_ID"] == (base.get("IDENTITY") or {}).get("DOCUMENT_ID")
    res = CAN.canario_html(novo)
    lin["CANARIO"] = {k: res.get(k) for k in ("PASS", "CLASSE", "PORQUE", "DETAIL_ENUMERATED", "ALVO", "DOCUMENT_ID", "TEMPOS", "DETAIL_GATE")}
    lin["ITEM_ABERTO"] = res.get("ITEM_ABERTO")
    lin["REGUA"] = RS.passos_da_promocao({"OBSERVED_AT": datetime.now(timezone.utc).isoformat(), "EVIDENCE_REF": "copia"},
                                         {"DADOS": res}, novo) if res.get("PASS") else None
    # os OUTROS documentos desta fonte ja guardados hoje: a mesma identidade/data/area, pelo motor, sem rede
    outros = []
    for url, em in list(BYTES_GUARDADOS.items()):
        if url != res.get("ALVO") and url != rec["INDEX_URL"] and __import__("re").match(rec["LINK_PATTERN"], url):
            ident = CAN.identidade_pelo_motor(novo, url, Path(em).read_bytes())
            outros.append({"URL": url, "DOCUMENT_ID": ident.get("DOCUMENT_ID"), "TEMPOS": CAN.tempos_do_motor(ident) if not ident.get("ERRO") else ident})
    lin["OUTROS_DOCUMENTOS_GUARDADOS"] = outros
    saida["FONTES"][sid] = lin
    t = res.get("TEMPOS") or {}
    print(sid, "PASS" if res.get("PASS") else "FALHA", res.get("CLASSE"), (res.get("PORQUE") or "")[:90], "|",
          t.get("PUBLISHED_AT"), "|", t.get("FACT_TIME"), "|", t.get("FACT_LOCATION"), "| regua:", (lin["REGUA"] or {}).get("REGUA"))
saida["VEIO_DE"] = VEIO_DE
saida["PEDIDOS_A_REDE"] = REDE
saida["PEDIDOS_POR_DOMINIO"] = DOM
(OUT / "CANARIO-D61.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print("pedidos novos:", len(REDE), DOM)
