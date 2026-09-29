# -*- coding: utf-8 -*-
"""A SONDA DE COMPORTAMENTO das linhas de coleta — mede o que o transporte FAZ, nao o texto.

CONTRATO (o mesmo da `sonda_ligacao_sites.mjs`, D124-REBASE):
    python ferramentas/big_collection/sonda_ligacao_linha.py --transporte=<ficheiro>
    ultima linha do stdout -> {"LIGADA": bool, "PORQUE": texto, "MEDIDO": {...}}

Sem `--transporte`: corre TODAS as linhas e imprime a tabela (a prova).

PORQUE EXISTE
    O portao do coletor continuo decidia LIGADA por PROCURA DE TEXTO
    (`coleta_continua.py`: `if linha["CHAMADA"] not in f.read_text()`). O texto
    prova que a STRING esta no ficheiro — nao prova que o pedido reserva. A
    propria SITES foi mudada para sonda por isso.

    Medido a 28/09, com a sonda a correr cada linha em PROCESSO PROPRIO:

        SOCIAL   coleta/teto_da_onda.py    consome 1 reserva   (via cortesia_adaptativa)
        BUSCA    coleta/linha_busca.py     consome 4           (robots + pagina, via scrap_http)
        CIENCIA  coleta/pesquisadores_t6.py consome 1          (DEPOIS de ligar corpus_pesquisador)
        PESQUISADORES coleta/seguir.py     transporte ausente

    SOCIAL e BUSCA reservavam no livro desde sempre — o texto e que nao estava no
    ficheiro do transporte, porque a reserva vive na PORTA (scrap_http,
    cortesia_adaptativa), nao no ficheiro que o portao lia.

    ONE MOMENTO DE ATENCAO, medido e que custou uma medicacao errada: correr duas
    linhas no MESMO processo da resultado FALSO. `coleta/scrap_http.py` instala um
    abridor global (`urllib.request.install_opener`) para que `urlopen` seja a
    unica porta e passe pelo teto. Basta importa-lo antes — como a BUSCA faz — e a
    CIENCIA, que chamava `urlopen` cru, aparecia a reservar SEM ESTAR LIGADA.
    Por isso cada linha corre num subprocesso.

        A ORDEM DOS IMPORTS NAO PODE SER O QUE LIGA UMA LINHA AO CONTADOR.
"""
import argparse
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ficheiro do transporte -> (nome da linha, como se mede)
LINHAS = {
    "coleta/linha_busca.py": ("BUSCA", "scrap_http"),
    "coleta/pesquisadores_t6.py": ("CIENCIA", "corpus_pesquisador"),
    "coleta/teto_da_onda.py": ("SOCIAL", "teto_da_onda"),
    "coleta/seguir.py": ("PESQUISADORES", None),          # sem porta medida: o ficheiro nao existe
}


class _ServidorLocal(http.server.BaseHTTPRequestHandler):
    """Responde 200 a tudo, em 127.0.0.1. Zero rede."""

    def do_GET(self):
        corpo = json.dumps({"ok": True, "path": self.path}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *a):
        pass


def _eventos(livro: str) -> int:
    if not os.path.exists(livro):
        return 0
    return sum(1 for l in open(livro, encoding="utf-8") if l.strip())


def _medir(como: str, base: str, livro: str, tmp: str) -> str | None:
    """Toca a porta do transporte UMA vez. Devolve o erro, ou None."""
    os.environ["SINTONIA_CORTESIA_LIVRO"] = livro
    os.environ.pop("SINTONIA_TETO_ONDA", None)
    os.environ.pop("SINTONIA_TETO_POR_HOST", None)
    sys.path.insert(0, os.path.join(RAIZ, "coleta"))
    try:
        if como == "teto_da_onda":
            os.environ["SINTONIA_TETO_ONDA"] = os.path.join(tmp, "onda.json")
            import teto_da_onda as TO
            TO.reservar("127.0.0.1", url=base, quem="sonda")
        elif como == "scrap_http":
            import scrap_http as http
            http.buscar_bytes(base, aceitar="application/json")
        elif como == "corpus_pesquisador":
            import corpus_pesquisador as CP
            CP._get(base)
        else:
            return "PORTA_NAO_MEDIDA"
    except Exception as ex:                                          # noqa: BLE001
        return "%s: %s" % (type(ex).__name__, str(ex)[:160])
    return None


def _uma(como: str) -> dict:
    """Modo filho: um servidor local, UMA linha, imprime o veredito. Processo novo de proposito."""
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _ServidorLocal)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = tempfile.mkdtemp(prefix="sonda-linha-")
    livro = os.path.join(tmp, "cortesia.ndjson")
    open(livro, "w", encoding="utf-8").close()
    erro = _medir(como, "http://127.0.0.1:%d/" % srv.server_address[1], livro, tmp)
    n = _eventos(livro)
    srv.shutdown()
    return {"LIGADA": n > 0, "PORQUE": ("%s reservou no livro de 24 h" % como) if n > 0
            else ("%s NAO reservou (%s)" % (como, erro or "zero eventos")),
            "MEDIDO": {"EVENTOS": n, "ERRO": erro, "PORTA": como}}


def _linha_de(transporte: str) -> dict:
    rel = transporte.replace("\\", "/")
    for chave, (nome, como) in LINHAS.items():
        if rel.endswith(chave):
            f = os.path.join(RAIZ, chave)
            if not os.path.exists(f):
                return {"LINHA": nome, "LIGADA": False,
                        "PORQUE": "TRANSPORTE_NAO_EXISTE_NESTA_ARVORE: %s" % chave, "MEDIDO": {}}
            if como is None:
                return {"LINHA": nome, "LIGADA": False, "PORQUE": "PORTA_NAO_MEDIDA: %s" % chave,
                        "MEDIDO": {}}
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--como=" + como],
                               capture_output=True, text=True, cwd=RAIZ, timeout=300,
                               encoding="utf-8", errors="replace")
            ult = (r.stdout.strip().splitlines() or [""])[-1]
            try:
                m = json.loads(ult)
            except ValueError:
                return {"LINHA": nome, "LIGADA": False,
                        "PORQUE": "SONDA_NAO_RESPONDEU: %s" % (r.stderr or r.stdout)[-200:], "MEDIDO": {}}
            m["LINHA"] = nome
            return m
    return {"LINHA": "?", "LIGADA": False, "PORQUE": "TRANSPORTE_NAO_SONDADO: %s" % transporte, "MEDIDO": {}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transporte", default=None)
    ap.add_argument("--como", default=None)
    a = ap.parse_args()
    if a.como:
        print(json.dumps(_uma(a.como), ensure_ascii=False))
        return 0
    if a.transporte:
        r = _linha_de(a.transporte)
        print(json.dumps(r, ensure_ascii=False))
        return 0
    tabela = {}
    for chave, (nome, como) in LINHAS.items():
        if not os.path.exists(os.path.join(RAIZ, chave)):
            tabela[nome] = {"TRANSPORTE": chave, "CONSOME_RESERVA": None,
                            "ERRO": "TRANSPORTE_NAO_EXISTE_NESTA_ARVORE"}
            continue
        if como is None:
            tabela[nome] = {"TRANSPORTE": chave, "CONSOME_RESERVA": None, "ERRO": "PORTA_NAO_MEDIDA"}
            continue
        r = _linha_de(chave)
        tabela[nome] = {"TRANSPORTE": chave, "CONSOME_RESERVA": r["LIGADA"],
                        "MEDIDO": r.get("MEDIDO"), "ERRO": None if r["LIGADA"] else r["PORQUE"]}
    print(json.dumps(tabela, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())