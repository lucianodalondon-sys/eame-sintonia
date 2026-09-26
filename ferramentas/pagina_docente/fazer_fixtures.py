# -*- coding: utf-8 -*-
"""PAGINA-DO-DOCENTE · as fixtures REAIS, reduzidas a partir dos bytes da P5 (sha256 conferido). Sem rede.

    py ferramentas/pagina_docente/fazer_fixtures.py --p5=<EVIDENCIA-P5.json> --bytes=<pasta p5-evidencia>

Reducao (minimizacao, D85): fora <script>/<style>/<svg>/comentarios; e-mails, links mailto/tel e protecao de
e-mail da Cloudflare trocados; numeros de telefone no TEXTO trocados. Paginas de PESSOA ficam com a estrutura
(o corte do BLOCO precisa do cabecalho e do rodape). Paginas de LISTA ficam so com os <a> (e o que o leitor usa); a de Udine fica inteira (o nome esta no cartao, fora do <a>).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FX = AQUI / "fixtures"
# (ficheiro, url, tipo)
REAIS = [
    ("milano-pessoa-toffolatti.html", "https://www.unimi.it/it/ugov/rubrica/person0000044501", "PESSOA"),
    ("milano-pessoa-com-youtube.html", "https://www.unimi.it/it/ugov/rubrica/person0000017592", "PESSOA"),
    ("milano-lista-disaa.html", "https://disaa.unimi.it/it/dipartimento/contatti/persone", "LISTA"),
    ("palermo-pessoa-matic.html", "https://www.unipa.it/persone/docenti/m/slavica.matic", "PESSOA"),
    ("palermo-lista-saaf.html", "https://www.unipa.it/dipartimenti/saaf/?pagina=personale&ruolo=docenti", "LISTA"),
    ("verona-pessoa-polverari.html", "https://www.dbt.univr.it/?ent=persona&id=27", "PESSOA"),
    ("verona-pessoa-com-perfis.html", "https://www.dbt.univr.it/?ent=persona&id=54972", "PESSOA"),
    ("verona-lista-dbt.html", "https://www.dbt.univr.it/?ent=persona", "LISTA"),
    ("padova-pessoa-dafnae.html", "https://www.dafnae.unipd.it/category/ruoli/personale-docente?key=6BFCC95C222DC94588FC97DD18715361", "PESSOA"),
    ("padova-lista-dafnae.html", "https://www.dafnae.unipd.it/category/ruoli/personale-docente", "LISTA"),
    ("udine-pessoa-di4a.html", "https://di4a.uniud.it/it/cercapersone/@@cercapersone_detail?person-id=0931d0f9a6250eb45671a10467c64cfd", "PESSOA"),
    ("udine-lista-di4a-p0.html", "https://di4a.uniud.it/it/cercapersone/cercapersone_dept?afferenza=107404", "LISTA_CARTAO"),
]


def reduzir(html: str, tipo: str) -> str:
    t = re.sub(r"(?is)<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<svg\b.*?</svg>|<noscript\b.*?</noscript>", "", html)
    t = re.sub(r'(?i)href="(mailto|tel):[^"]*"', 'href="#"', t)
    t = re.sub(r'\sdata-cfemail="[^"]*"', "", t)
    t = re.sub(r"(?i)/cdn-cgi/l/email-protection#[0-9a-f]+", "#", t)
    t = re.sub(r"[\w.+-]+(@|\(at\)|\[at\])[\w-]+\.[\w.]+", "email-removido", t)

    def texto(m):   # telefone so no TEXTO (entre > e <), nunca dentro de um endereco
        return re.sub(r"(?<![\w/=.-])\+?\d[\d ./-]{7,}\d", "numero-removido", m.group(0))
    t = re.sub(r">[^<]+<", texto, t)
    if tipo == "LISTA":
        t = "\n".join(re.findall(r"(?is)<a\b[^>]*>.*?</a>", t))
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t)


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    ev = {x["URL"]: x for x in json.loads(Path(arg["p5"]).read_text(encoding="utf-8"))["PAGINAS"] if x.get("URL")}
    FX.mkdir(exist_ok=True)
    origem = {}
    for nome, url, tipo in REAIS:
        x = ev[url]
        b = (Path(arg["bytes"]) / Path(x["FICHEIRO"].replace("\\", "/")).name).read_bytes()
        assert hashlib.sha256(b).hexdigest() == x["SHA256"], url
        (FX / nome).write_text(reduzir(b.decode("utf-8", "replace"), tipo), encoding="utf-8", newline="\n")
        origem[nome] = {"URL": url, "TIPO": tipo, "SHA256_ORIGINAL": x["SHA256"], "BYTES_ORIGINAL": x["BYTES"],
                        "ORIGEM": "P5 pessoas-docentes-v1, EVIDENCIA-P5.json (colhido 24/09/2026)"}
    (FX / "ORIGEM-DAS-FIXTURES.json").write_text(json.dumps(origem, ensure_ascii=False, indent=1) + "\n",
                                                 encoding="utf-8", newline="\n")
    print(len(origem), "fixtures reais reduzidas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
