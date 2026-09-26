"""SOCIAL-QUALIFICAR · quantos pedidos o yt-dlp faz por video — medido SEM REDE.

    py provas/social-qualificar/medir_yt_dlp_offline.py [--json SAIDA]

Um intermediario (proxy) LOCAL recebe TODO o trafego do yt-dlp: aceita o CONNECT, termina o TLS
com um certificado proprio (o yt-dlp corre com --no-check-certificates) e responde ele mesmo,
como se fosse youtube.com e googlevideo.com. Nunca repassa nada: nenhum byte sai desta maquina.
Conta-se de DOIS lados e compara-se: o que o servidor recebeu, e o que o `--print-traffic` do
yt-dlp diz (a mesma leitura que o Scrap usa: `youtube_transcrever.trafego_do_yt_dlp`).

O yt-dlp corre com os MESMOS argumentos de `ferramentas/youtube_transcrever._audio`.

⚠️ O QUE ISTO MEDE E O QUE NAO MEDE
- Mede o caminho do yt-dlp INSTALADO nesta maquina (versao, clientes por omissao, sem runtime de
  JavaScript → cliente `visionos` so), e o fatiamento do download (10 MiB por pedido).
- As respostas sao SINTETICAS (formato das respostas reais: ytcfg + ytInitialPlayerResponse + API
  /youtubei/v1/player). O YouTube real pode acrescentar pedidos que um servidor bem-comportado nao
  provoca: 403 no stream e nova tentativa, pedido de PO token, redireccionamento, consentimento.
  Por isso o numero daqui e o MINIMO do caminho, nao o maximo.
"""
import argparse
import http.server
import json
import os
import re
import shutil
import socket
import socketserver
import ssl
import subprocess
import sys
import tempfile
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas"))
import youtube_transcrever as ytv  # noqa: E402

VID = "AbCdEfGhIjK"
PEDIDOS = []
TAMANHO = {"n": 3 << 20}


def _player_response(host_stream):
    n = TAMANHO["n"]
    fmt = {"itag": 140, "url": "https://%s/videoplayback?itag=140&id=x&clen=%d&dur=600.0" % (host_stream, n),
           "mimeType": 'audio/mp4; codecs="mp4a.40.2"', "bitrate": 130000, "averageBitrate": 128000,
           "contentLength": str(n), "approxDurationMs": "600000", "audioQuality": "AUDIO_QUALITY_MEDIUM",
           "audioSampleRate": "44100", "audioChannels": 2, "lastModified": "1", "quality": "tiny"}
    return {"playabilityStatus": {"status": "OK", "playableInEmbed": True},
            "videoDetails": {"videoId": VID, "title": "Video sintetico", "lengthSeconds": "600",
                             "channelId": "UCxxxxxxxxxxxxxxxxxxxxxx", "author": "Canal", "viewCount": "10",
                             "shortDescription": "descricao", "isLiveContent": False},
            "microformat": {"playerMicroformatRenderer": {"publishDate": "2026-09-19T09:38:04-07:00",
                                                          "uploadDate": "2026-09-19T09:38:04-07:00",
                                                          "category": "Education"}},
            "streamingData": {"expiresInSeconds": "21540", "adaptiveFormats": [fmt]}}


# O `ytInitialData` que a pagina real traz (conteudo da coluna do video). Vazio, o yt-dlp
# pede-o a parte (/youtubei/v1/next) — o que a pagina real nao provoca.
DADOS_INICIAIS = {"contents": {"twoColumnWatchNextResults": {"results": {"results": {"contents": [
    {"videoPrimaryInfoRenderer": {"title": {"runs": [{"text": "Video sintetico"}]}}},
    {"videoSecondaryInfoRenderer": {"owner": {"videoOwnerRenderer": {"title": {"runs": [{"text": "Canal"}]}}}}}]}}}}}


def _pagina():
    ytcfg = {"INNERTUBE_API_KEY": "k", "INNERTUBE_CONTEXT": {"client": {"clientName": "WEB",
                                                                         "clientVersion": "2.20260901.00.00",
                                                                         "hl": "en", "gl": "IT"}},
             "INNERTUBE_CONTEXT_CLIENT_NAME": 1, "INNERTUBE_CLIENT_VERSION": "2.20260901.00.00",
             "VISITOR_DATA": "Cgt2aXNpdG9y", "PLAYER_JS_URL": "/s/player/abcdef12/player_ias.vflset/en_US/base.js"}
    pr = _player_response("rr1---sn-abc.googlevideo.com")
    return ("<html><head><title>Video sintetico - YouTube</title></head><body><script>ytcfg.set(%s);</script>"
            "<script>var ytInitialPlayerResponse = %s;</script><script>var ytInitialData = %s;</script>"
            "</body></html>" % (json.dumps(ytcfg), json.dumps(pr), json.dumps(DADOS_INICIAIS))).encode()


class Resp(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _host(self):
        return (self.headers.get("Host") or getattr(self.server, "alvo", "?")).split(":")[0]

    def _enviar(self, corpo, tipo, codigo=200, extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def _tratar(self):
        host = self._host()
        corpo = b""
        if self.headers.get("Content-Length"):
            corpo = self.rfile.read(int(self.headers["Content-Length"]))
        PEDIDOS.append({"HOST": host, "METODO": self.command, "CAMINHO": self.path.split("?")[0],
                        "RANGE": self.headers.get("Range"), "CORPO": corpo[:200].decode("utf-8", "replace")})
        if "googlevideo.com" in host:
            n = TAMANHO["n"]
            m = re.search(r"range=(\d+)-(\d+)", self.path) or re.search(r"bytes=(\d+)-(\d*)", self.headers.get("Range") or "")
            ini, fim = (int(m.group(1)), int(m.group(2) or n - 1)) if m else (0, n - 1)
            fim = min(fim, n - 1)
            parte = b"\0" * (fim - ini + 1)
            extra = {"Accept-Ranges": "bytes"}
            if m and self.headers.get("Range"):
                extra["Content-Range"] = "bytes %d-%d/%d" % (ini, fim, n)
                return self._enviar(parte, "audio/mp4", 206, extra)
            return self._enviar(parte, "audio/mp4", 200, extra)
        if self.path.startswith("/watch"):
            return self._enviar(_pagina(), "text/html; charset=utf-8")
        if self.path.startswith("/youtubei/v1/next"):
            return self._enviar(json.dumps(DADOS_INICIAIS).encode(), "application/json")
        if self.path.startswith("/youtubei/v1/player"):
            return self._enviar(json.dumps(_player_response("rr1---sn-abc.googlevideo.com")).encode(),
                                "application/json")
        return self._enviar(b"{}", "application/json", 404)

    do_GET = do_POST = do_HEAD = _tratar

    def do_CONNECT(self):
        # o aperto de mao com o proxy nao e pedido ao site (a leitura do Scrap tambem o ignora)
        alvo = self.path.split(":")[0]
        self.send_response(200, "Connection established")
        self.end_headers()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(self.server.cert, self.server.chave)
        try:
            tls = ctx.wrap_socket(self.connection, server_side=True)
        except (ssl.SSLError, OSError):
            return
        interno = _Interno(tls, alvo)
        interno.corre()
        self.close_connection = True


class _Interno:
    """Serve HTTP dentro do tunel TLS, com o mesmo tratador."""

    def __init__(self, tls, alvo):
        self.tls, self.alvo = tls, alvo

    def corre(self):
        srv = type("S", (), {"alvo": self.alvo})()
        try:
            Resp(self.tls, ("127.0.0.1", 0), srv)
        except (ssl.SSLError, OSError, ValueError):
            pass


class Proxy(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def certificado(pasta):
    cert, chave = os.path.join(pasta, "c.pem"), os.path.join(pasta, "k.pem")
    cfg = os.path.join(pasta, "o.cnf")
    with open(cfg, "w") as f:
        f.write("[req]\ndistinguished_name=d\nx509_extensions=e\nprompt=no\n[d]\nCN=youtube.com\n"
                "[e]\nsubjectAltName=DNS:youtube.com,DNS:*.youtube.com,DNS:*.googlevideo.com,DNS:*.ytimg.com,"
                "DNS:*.google.com,DNS:*.googleapis.com\n")
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2", "-keyout", chave,
                    "-out", cert, "-config", cfg], check=True, capture_output=True)
    return cert, chave


def medir(tamanho, extra_args=()):
    PEDIDOS.clear()
    TAMANHO["n"] = tamanho
    tmp = tempfile.mkdtemp(prefix="myd-")
    try:
        cert, chave = certificado(tmp)
        p = Proxy(("127.0.0.1", 0), Resp)
        p.cert, p.chave = cert, chave
        threading.Thread(target=p.serve_forever, daemon=True).start()
        url_proxy = "http://127.0.0.1:%d" % p.server_address[1]
        so_yt = os.path.join(tmp, "libs")
        shutil.copytree(os.path.join(os.path.expanduser("~"), ".sintonia-libs", "yt_dlp"),
                        os.path.join(so_yt, "yt_dlp"))
        env = dict(os.environ, PYTHONPATH=so_yt, HTTP_PROXY=url_proxy, HTTPS_PROXY=url_proxy,
                   http_proxy=url_proxy, https_proxy=url_proxy, NO_PROXY="", no_proxy="")
        # os MESMOS argumentos de youtube_transcrever._audio, mais o proxy local
        args = [sys.executable, "-m", "yt_dlp", "-q", "--no-warnings", "--print-traffic",
                "-f", "bestaudio/best", "-x", "--audio-format", "wav",
                "--postprocessor-args", "-ac 1 -ar 16000", "--write-info-json",
                "--proxy", url_proxy, "--no-check-certificates", "--no-cache-dir",
                *extra_args,
                "-o", os.path.join(tmp, "%(id)s.%(ext)s"), "https://www.youtube.com/watch?v=" + VID]
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=env, timeout=300)
        p.shutdown()
        lidos = ytv.trafego_do_yt_dlp(r.stdout)
        info = os.path.join(tmp, VID + ".info.json")
        return {"TAMANHO_BYTES": tamanho, "ARGS_EXTRA": list(extra_args),
                "SERVIDOR_RECEBEU": list(PEDIDOS),
                "SERVIDOR_POR_HOST": _por_host(PEDIDOS),
                "PRINT_TRAFFIC_POR_HOST": lidos,
                "INFO_JSON_ESCRITO": os.path.exists(info),
                "RC": r.returncode, "STDERR_FIM": (r.stderr or "")[-400:]}
    finally:
        shutil.rmtree(tmp, True)


def _por_host(pedidos):
    c = {}
    for x in pedidos:
        c[x["HOST"]] = c.get(x["HOST"], 0) + 1
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    import yt_dlp.version as V  # noqa: PLC0415 — so para registar a versao medida
    casos = [("3 MiB (~3 min de audio)", 3 << 20, ()),
             ("10 MiB exactos", 10 << 20, ()),
             ("25 MiB (~25 min)", 25 << 20, ()),
             ("25 MiB sem pagina (player_skip=webpage)", 25 << 20,
              ("--extractor-args", "youtube:player_skip=webpage")),
             ("25 MiB, fatia de 50M", 25 << 20, ("--http-chunk-size", "50M"))]
    fora = {"YT_DLP": V.__version__, "DENO": shutil.which("deno") is not None, "CASOS": []}
    for nome, n, extra in casos:
        m = medir(n, extra)
        m["CASO"] = nome
        fora["CASOS"].append(m)
        print("%-42s servidor=%s  print-traffic=%s  rc=%s" % (nome, m["SERVIDOR_POR_HOST"],
                                                            m["PRINT_TRAFFIC_POR_HOST"], m["RC"]))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(fora, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".sintonia-libs"))
    main()
