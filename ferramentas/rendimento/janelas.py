# -*- coding: utf-8 -*-
"""REND · D29 — a fonte publica informacao de JANELA de cultura?

Janela = boletim fitossanitario/agrometeo, fenologia, alerta de praga,
tratamento, sementeira/colheita. Duas provas, SEM rede:

  CAPA   as ligacoes da pagina de entrada ja pedida (C:/rend/indices*, sha256 na
         medida): endereco OU texto da ligacao com um termo de janela.
  ACERVO os textos ja tirados desta fonte (documento_estruturado, Sala, so
         leitura): documentos com um termo de janela.

JANELA = SIM   se ha prova em pelo menos um dos dois (com 1 URL de exemplo)
         NAO   se a capa foi lida E o acervo tem textos E nenhum casa
         NAO_SEI no resto (capa nao lida, ou acervo vazio e capa sem termo)
⚠️ E um INDICIO por palavra, nao uma leitura: uma ligacao «bollettino» na capa
nao prova que a fonte publique janelas com regularidade. Os termos ficam aqui,
a vista, para quem quiser discordar.

Uso: py ferramentas/rendimento/janelas.py --indices C:/rend/indices,C:/rend/indices-r1
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sala_por_fonte import psql  # noqa: E402

AQUI = Path(__file__).resolve().parent
# FORTES = a fonte da uma JANELA (quando agir): boletim, fase fenologica, aviso, tratamento aconselhado, data de sementeira.
# TEMA   = a fonte FALA do assunto (praga, colheita, sementeira) — medido em 24/09: «vendemmia» num menu,
#          «in fase di semina» num artigo de precos. Tema nao e janela: fica NAO_SEI com a nota.
TERMOS = [r"bollettin\w*\s+(fitosanitar|agrometeo|colturale|di\s+difesa|della\s+difesa|agrofenolog|viticol|frutticol|olivicol|di\s+produzione\s+integrata)",
          r"agrometeo", r"agro-?meteorolog", r"difesa\s+integrata", r"produzione\s+integrata",
          r"(fase|stadio|stadi|fasi)\s+fenolog", r"avvis\w*\s+(fitosanitar|di\s+difesa|ai\s+trattament)",
          r"allert\w*\s+(fitosanitar|parassit)", r"trattament\w*\s+(consigliat|da\s+eseguire|in\s+corso)",
          r"(epoca|data|periodo)\s+(di|della)\s+(semina|raccolta|vendemmia|trapianto)",
          r"monitoraggio\s+(fitosanitar|parassit|insett|della\s+mosca|dei\s+fitofagi)", r"catture\s+(settimanal|della\s+mosca|di\s+adulti)"]
TEMA = [r"vendemmi", r"semin[ae]\b",r"trebbiatur", r"fitosanitar", r"fenolog", r"peronospor", r"oidio",
        r"mosca\s+dell.olivo", r"cimice\s+asiatica", r"flavescenza", r"xylella", r"popillia", r"difesa\s+delle\s+colture"]
RE = re.compile("|".join("(?:%s)" % t for t in TERMOS), re.I)
RE_TEMA = re.compile("|".join("(?:%s)" % t for t in TEMA), re.I)
def _sql(ts):
    return "|".join(ts).replace("\\w", "[[:alnum:]_]").replace("\\s", "[[:space:]]").replace("\\b", "\\y")


SQL_RE, SQL_TEMA = _sql(TERMOS), _sql(TEMA)


def capa(pastas, sid):
    for p in pastas:
        f = Path(p) / (sid + ".html")
        if f.exists():
            break
    else:
        return None, None
    txt = f.read_bytes().decode("utf-8", "replace")
    tema = None
    for m in re.finditer(r'<a\b[^>]*href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', txt, re.I | re.S):
        texto = html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        alvo = m.group(1).replace("-", " ").replace("_", " ")   # «bollettino-fitosanitario» casa como texto
        achou = RE.search(alvo) or RE.search(texto)
        if achou:
            return True, {"URL": m.group(1), "TEXTO": re.sub(r"\s+", " ", texto).strip()[:80],
                          "TERMO": achou.group(0), "NIVEL": "JANELA"}
        t = RE_TEMA.search(alvo) or RE_TEMA.search(texto)
        if t and not tema:
            tema = {"URL": m.group(1), "TEXTO": re.sub(r"\s+", " ", texto).strip()[:80],
                    "TERMO": t.group(0), "NIVEL": "TEMA"}
    return True, tema


def main(argv):
    pastas = argv[argv.index("--indices") + 1].split(",")
    t = json.loads((AQUI / "REND-TABELA-V1.json").read_text(encoding="utf-8"))
    ids = [x["SOURCE_ID"] for x in t["TABELA"]]
    lista = ",".join("'%s'" % i for i in ids)
    acervo = {}
    for sid, n, casam, ex, tema in psql(
            # o endereco do documento_estruturado vem vazio em parte das linhas: cai para o do raw_asset
            "select d.source_id, count(*), count(*) filter (where d.texto ~* $re$%s$re$), "
            "min(coalesce(d.source_url, r.source_url)) filter (where d.texto ~* $re$%s$re$), "
            "count(*) filter (where d.texto ~* $re$%s$re$) "
            "from documento_estruturado d left join derived_artifact a on a.id = d.derived_artifact_id "
            "left join raw_asset r on r.id = a.raw_asset_id "
            "where d.source_id in (%s) group by 1" % (SQL_RE, SQL_RE, SQL_TEMA, lista)):
        acervo[sid] = {"TEXTOS": int(n), "COM_JANELA": int(casam), "EXEMPLO": ex or None, "SO_TEMA": int(tema)}
    idx = {}
    # a medida da R1 com o contrato de antes do reparo (entrada-r1.json, -passo2) e so historia
    antigos = {"entrada-r1.json", "entrada-r1-passo2.json"}
    for f in sorted(p for p in (AQUI / "medidas").glob("entrada-*.json") if p.name not in antigos):
        for l in json.loads(f.read_text(encoding="utf-8"))["LINHAS"]:
            if l.get("INDEX_URL"):
                idx[l["SOURCE_ID"]] = l["INDEX_URL"]
    out = {}
    for x in t["TABELA"]:
        sid = x["SOURCE_ID"]
        lida, prova = capa(pastas, sid)
        if prova and idx.get(sid):
            prova["URL"] = urljoin(idx[sid], prova["URL"])
        a = acervo.get(sid, {"TEXTOS": 0, "COM_JANELA": 0, "EXEMPLO": None, "SO_TEMA": 0})
        janela_capa = prova if prova and prova["NIVEL"] == "JANELA" else None
        if janela_capa or a["COM_JANELA"]:
            v = "SIM"
        elif prova or a["SO_TEMA"]:
            v = "NAO_SEI"
        elif lida and a["TEXTOS"]:
            v = "NAO"
        else:
            v = "NAO_SEI"
        ex = a["EXEMPLO"] or (janela_capa or {}).get("URL") or (prova or {}).get("URL")
        if a["COM_JANELA"]:
            forca = "FORTE (texto ja colhido fala de janela)"
        elif janela_capa:
            forca = "MEDIA (a capa liga para uma pagina de janela)"
        elif v == "NAO_SEI" and (prova or a["SO_TEMA"]):
            forca = "SO_TEMA (fala do assunto, sem janela provada)"
        else:
            forca = None
        out[sid] = {"JANELA": v, "FORCA": forca, "EXEMPLO_URL": ex, "CAPA_LIDA": lida, "CAPA_PROVA": prova, "ACERVO": a}
    (AQUI / "medidas" / "janelas.json").write_text(json.dumps(
        {"DATASET": "REND-JANELAS-D29-V1", "TERMOS": TERMOS, "POR_FONTE": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c = {}
    for v in out.values():
        c[v["JANELA"]] = c.get(v["JANELA"], 0) + 1
    print(c)
    for sid, v in out.items():
        if v["JANELA"] == "SIM":
            print(sid, v["ACERVO"]["COM_JANELA"], "/", v["ACERVO"]["TEXTOS"], (v["CAPA_PROVA"] or {}).get("TERMO"), v["EXEMPLO_URL"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
