#!/usr/bin/env python3
"""Serve a superficie publicada COM os cabecalhos reais do vercel.json.

Existe para que a pergunta «este cabecalho parte o portal?» possa ser
respondida por um navegador de verdade, antes de o cabecalho chegar a
producao — e sem depender de rede, o que faz dela uma prova repetivel.

    UM CABECALHO NAO SE PROVA A LER O FICHEIRO DE CONFIGURACAO.
    PROVA-SE A ABRIR A PAGINA.

Le o `outputDirectory` e a lista `headers` do proprio vercel.json: se alguem
mudar um cabecalho la, esta prova passa a testar o cabecalho novo sem que
ninguem se lembre de a actualizar.

    A PROVA QUE COPIA A CONFIGURACAO ENVELHECE. A QUE A LE, NAO.

Uso: python3 security/servir_como_a_vercel.py [porta]
"""
import functools, http.server, json, os, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / "vercel.json").read_text(encoding="utf-8"))
SAIDA = RAIZ / CFG["outputDirectory"]
CABECALHOS = [(h["key"], h["value"]) for r in CFG.get("headers", []) for h in r["headers"]]
CLEAN_URLS = CFG.get("cleanUrls", False)


class Mao(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        for k, v in CABECALHOS:
            self.send_header(k, v)
        super().end_headers()

    def translate_path(self, path):
        p = super().translate_path(path)
        # cleanUrls: /accesso serve accesso.html, como a Vercel faz.
        if CLEAN_URLS and not os.path.exists(p) and not path.endswith("/"):
            alt = p + ".html"
            if os.path.exists(alt):
                return alt
        return p

    def log_message(self, *a):
        pass


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8799
    os.chdir(SAIDA)
    with http.server.ThreadingHTTPServer(("127.0.0.1", porta), Mao) as s:
        print(f"a servir {SAIDA} em http://127.0.0.1:{porta} "
              f"com {len(CABECALHOS)} cabecalhos do vercel.json", flush=True)
        s.serve_forever()


if __name__ == "__main__":
    main()
