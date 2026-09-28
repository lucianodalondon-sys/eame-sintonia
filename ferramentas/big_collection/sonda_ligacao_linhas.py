# -*- coding: utf-8 -*-
"""A SONDA DA LIGACAO DAS LINHAS PYTHON — medida pelo COMPORTAMENTO, nunca pelo texto (LINHAS-NO-CONTADOR, 28/09).

    py ferramentas/big_collection/sonda_ligacao_linhas.py --linha=BUSCA|CIENCIA|SOCIAL|PESQUISADORES [--raiz=<arvore>]

Porque existe: a coleta continua (`coleta_continua.py`) so corre uma linha LIGADA ao contador multicanal (o livro
da cortesia adaptativa, D90/D124). A linha SITES prova-se pela sonda Node (`sonda_ligacao_sites.mjs`). As outras
quatro provavam-se procurando o texto `reserva_24h.reservar(` no ficheiro: medido na producao (ciclo 20, 28/09),
BUSCA, CIENCIA e SOCIAL ficavam ESPERA_LIGACAO para sempre — e o texto la tambem nao provaria nada (pode estar
morto). Aqui mede-se o que o TRANSPORTE REAL da linha FAZ.

ZERO rede externa: um servidor HTTP em 127.0.0.1; os nomes `*.test` resolvem para ele por um `getaddrinfo` desta
sonda; os proxies saem do ambiente; livro e politica TEMPORARIOS (a politica e a real com as pausas minimas a 0,
so para a sonda nao demorar: mede-se o FIO, nao os numeros). Para CADA rota da linha:
  A  um pedido a um dominio livre: CADA pedido que chegou ao servidor tem uma RESERVA no livro escrita ANTES de
     ele chegar e uma RESPOSTA registada DEPOIS (reserva atomica antes de cada pedido);
  B  um pedido a um dominio que o livro diz PAUSADO (2 sinais em 24 h): ZERO pedidos no servidor;
  S  o servidor responde 429 a pagina: tres chamadas -> os 429 ficam no livro como SINAL (HTTP_429) e, depois do
     2.o sinal, a 3.a chamada NAO chega ao servidor (o recuo/pausa da politica e obedecido).
LIGADA = A, B e S em todas as rotas. Sai uma linha JSON (a ultima): {"LIGADA", "PORQUE", "MEDIDO"}.

CADA ROTA NUM PROCESSO SEU (medido nesta missao): o `scrap_http` instala o abridor do urllib para o processo
inteiro. Medidas no mesmo processo, a rota YouTube Data da arvore base (que nao reserva) aparecia LIGADA por
contagio do abridor da rota vizinha. Um processo por rota mede so o que AQUELA rota faz.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# as rotas de cada linha: (nome, ficheiro do transporte relativo a raiz, como se faz UM pedido por ele)
ROTAS = {
    "BUSCA": [("PAGINA", "coleta/linha_busca.py", "pagina"), ("API", "coleta/linha_busca.py", "api")],
    "CIENCIA": [("API", "coleta/pesquisadores_t6.py", "ciencia")],
    "SOCIAL": [("SCRAP_HTTP", "coleta/scrap_http.py", "scrap"), ("YOUTUBE_DATA", "coleta/youtube_oficial.py", "yt")],
    "PESQUISADORES": [("SEGUIR", "ferramentas/seguir_pesquisadores/seguir.py", "seguir")],
}


def _carregar(raiz: Path, rel: str):
    """O modulo do transporte DESTA arvore (uma copia mutada e medida como ela e)."""
    for p in (raiz, raiz / "coleta", raiz / "ferramentas" / "linha_busca", raiz / "curadoria",
              raiz / "ferramentas" / "seguir_pesquisadores"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    try:
        import _gavetas  # noqa: F401 — as gavetas do processo no caminho
    except ImportError:
        pass
    nome = Path(rel).stem
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, raiz / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def _um_pedido(raiz: Path, rel: str, como: str, url: str, tmp: Path):
    """UM pedido pelo caminho real da linha. Excecoes sao resultado (uma recusa e o que se quer ver em B)."""
    try:
        if como == "pagina":
            return _carregar(raiz, rel).pedir_para_sonda(url, "PAGINA", tmp)
        if como == "api":
            return _carregar(raiz, rel).pedir_para_sonda(url, "API", tmp)
        if como == "ciencia":
            return _carregar(raiz, rel).pedir_para_sonda(url)
        if como == "scrap":
            return _carregar(raiz, rel).buscar_bytes(url)
        if como == "yt":
            return _carregar(raiz, rel)._http(url)
        if como == "seguir":
            m = _carregar(raiz, rel)
            return m.Transporte(tmp / "seguir", pausa=0).get(url, "sonda")
        raise ValueError("rota desconhecida: %s" % como)
    except Exception as ex:                                        # noqa: BLE001
        return {"EXCECAO": "%s: %s" % (type(ex).__name__, str(ex)[:160])}


def sondar(linha: str, raiz: Path, timeout_s: float = 150.0) -> dict:
    """Cada rota num subprocesso (`--rota=i`); LIGADA so se todas o estiverem."""
    if linha not in ROTAS:
        return {"LIGADA": False, "PORQUE": "linha sem sonda Python: %s" % linha}
    import subprocess
    medido, porques = {}, []
    for i, (nome, _, _) in enumerate(ROTAS[linha]):
        try:
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--linha=" + linha, "--rota=%d" % i,
                                "--raiz=" + str(raiz)], capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=timeout_s)
            r = json.loads((p.stdout.strip().splitlines() or ["{}"])[-1])
        except (OSError, ValueError, subprocess.TimeoutExpired) as ex:
            r = {"LIGADA": False, "PORQUE": "%s: SONDA_DA_ROTA_NAO_CORREU: %s" % (nome, str(ex)[:160])}
        medido.update(r.get("MEDIDO") or {})
        porques.append((r.get("LIGADA") is True, r.get("PORQUE") or "%s: sem resposta" % nome))
    falhas = [q for ok, q in porques if not ok]
    return {"LIGADA": not falhas, "PORQUE": "; ".join(falhas) if falhas else "; ".join(q for _, q in porques),
            "MEDIDO": medido}


def sondar_rota(linha: str, i: int, raiz: Path) -> dict:
    """UMA rota, neste processo (limpo)."""
    if linha not in ROTAS or not 0 <= i < len(ROTAS[linha]):
        return {"LIGADA": False, "PORQUE": "rota sem sonda: %s/%s" % (linha, i)}
    for k in [k for k in os.environ if k.startswith("SINTONIA_")]:
        del os.environ[k]
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
        os.environ.pop(k, None)
    os.environ["NO_PROXY"] = os.environ["no_proxy"] = "*"
    tmp = Path(tempfile.mkdtemp(prefix="sonda-linhas-"))
    os.environ["TMPDIR"] = str(tmp)
    pedidos = []

    class H(BaseHTTPRequestHandler):
        def do_GET(self):                                          # noqa: N802
            host = (self.headers.get("Host") or "").split(":")[0]
            pedidos.append({"HOST": host, "P": self.path, "T": time.time()})
            if self.path.startswith("/robots.txt"):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"non trovato")
                return
            if host.startswith("recuo-"):
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "rate"}')
                return
            corpo = b'{"sonda": true, "group": [], "results": [], "items": []}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    porta = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    real = socket.getaddrinfo

    def resolver(host, *a, **k):
        if str(host).endswith(".test"):
            return real("127.0.0.1", *a, **k)
        return real(host, *a, **k)
    socket.getaddrinfo = resolver
    try:
        pol = json.loads((raiz / "regras" / "POLITICA-CORTESIA-ADAPTATIVA.json").read_text(encoding="utf-8"))
        for c in ("SITE", "PLATAFORMA_GRANDE"):
            pol["CLASSES"][c]["PAUSA_MINIMA_S"] = 0
        (tmp / "politica.json").write_text(json.dumps(pol), encoding="utf-8")
        os.environ["SINTONIA_CORTESIA_POLITICA"] = str(tmp / "politica.json")
        livro = tmp / "LIVRO-CORTESIA.ndjson"
        agora = time.time()
        rotas = [ROTAS[linha][i]]
        fechado = ["fechado-%d.test" % i]
        livro.write_text("".join(json.dumps({"TIPO": "RESPOSTA", "DOMINIO": d, "EM": agora - 10 + j, "LINHA": "SONDA",
                                             "MARCAS": [], "RUN_ID": "SONDA", "SINAIS": ["HTTP_429"], "STATUS": 429}) + "\n"
                                 for d in fechado for j in (1, 2)), encoding="utf-8")
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(livro)
        os.environ["SINTONIA_LINHA"] = linha
        medido, porque = {}, None
        for nome, rel, como in rotas:
            livre, recuo = "livre-%d.test" % i, "recuo-%d.test" % i
            n0 = len(pedidos)
            a = _um_pedido(raiz, rel, como, "http://%s:%d/pagina" % (livre, porta), tmp)
            nB = len(pedidos)
            b = _um_pedido(raiz, rel, como, "http://%s:%d/pagina" % (fechado[0], porta), tmp)
            nS = len(pedidos)
            s = [_um_pedido(raiz, rel, como, "http://%s:%d/pagina" % (recuo, porta), tmp) for _ in range(3)]
            ev = [json.loads(l) for l in livro.read_text(encoding="utf-8").splitlines() if l.strip()]
            pedA = [p for p in pedidos[n0:nB] if p["HOST"] == livre]
            res = sorted(e["EM"] for e in ev if e["DOMINIO"] == livre and e["TIPO"] == "RESERVA")
            resp = sorted(e["EM"] for e in ev if e["DOMINIO"] == livre and e["TIPO"] == "RESPOSTA")
            ordem = all(k < len(res) and res[k] <= p["T"] and k < len(resp) and resp[k] >= p["T"]
                        for k, p in enumerate(pedA))
            pedB = [p for p in pedidos[nB:nS] if p["HOST"] == fechado[0]]
            pedS = [p for p in pedidos[nS:] if p["HOST"] == recuo and not p["P"].startswith("/robots")]
            sinais = [e for e in ev if e["DOMINIO"] == recuo and e["TIPO"] == "RESPOSTA" and "HTTP_429" in (e.get("SINAIS") or [])]
            m = {"PEDIDOS_A": len(pedA), "RESERVAS_A": len(res), "RESPOSTAS_A": len(resp), "ORDEM_A": ordem,
                 "PEDIDOS_B": len(pedB), "PAGINAS_429_S": len(pedS), "SINAIS_NO_LIVRO_S": len(sinais),
                 "RESULTADO_A": str(a)[:120], "RESULTADO_B": str(b)[:160], "RESULTADO_S3": str(s[-1])[:160]}
            medido[nome] = m
            if porque:
                continue
            if not pedA:
                porque = "%s A: nenhum pedido chegou ao servidor (o transporte nao pediu: %s)" % (nome, m["RESULTADO_A"])
            elif len(res) != len(pedA):
                porque = "%s A: %d pedidos no servidor, %d reservas no livro" % (nome, len(pedA), len(res))
            elif len(resp) != len(pedA):
                porque = "%s A: %d pedidos no servidor, %d respostas no livro" % (nome, len(pedA), len(resp))
            elif not ordem:
                porque = "%s A: um pedido chegou antes da sua reserva (ou sem resposta registada)" % nome
            elif pedB:
                porque = "%s B: o livro dizia PAUSADO e %d pedido(s) sairam" % (nome, len(pedB))
            elif len(sinais) < 2 or len(pedS) != 2:
                porque = ("%s S: o 429 nao foi obedecido: %d pagina(s) pedida(s) em 3 chamadas (devia parar na 2.a), "
                          "%d sinal(is) no livro" % (nome, len(pedS), len(sinais)))
        ok = porque is None
        return {"LIGADA": ok, "PORQUE": porque or "; ".join(
            "%s: A %d pedidos = %d reservas antes + %d respostas; B 0 pedidos (pausado); S 429 no livro (%d) e a 3.a "
            "chamada nao saiu" % (n, v["PEDIDOS_A"], v["RESERVAS_A"], v["RESPOSTAS_A"], v["SINAIS_NO_LIVRO_S"])
            for n, v in medido.items()), "MEDIDO": medido}
    finally:
        socket.getaddrinfo = real
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    raiz = Path(arg.get("raiz") or AQUI.parents[1]).resolve()
    try:
        if "rota" in arg:
            r = sondar_rota(arg.get("linha", ""), int(arg["rota"]), raiz)
        else:
            r = sondar(arg.get("linha", ""), raiz)
    except Exception as ex:                                        # noqa: BLE001 — falha da sonda = NAO LIGADA
        r = {"LIGADA": False, "PORQUE": "SONDA_FALHOU: %s: %s" % (type(ex).__name__, str(ex)[:200])}
    r["LINHA"] = arg.get("linha")
    print(json.dumps(r, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
