"""O yt-dlp com o FREIO do teto D38/D41 — cada pedido dele reserva o lugar ANTES de sair.

    python ferramentas/yt_dlp_com_freio.py <os mesmos argumentos do yt-dlp>

FREIO-SOCIAL (26/09). O yt-dlp e outro processo: os pedidos dele (a pagina, o player,
a API, o stream em googlevideo.com) nao passam pelo portao do `scrap_http`. Ate aqui
eram so CONTADOS depois, pelo `--print-traffic`. Aqui entram no MESMO freio:

  `YoutubeDL.urlopen` e a porta por onde o yt-dlp faz TODOS os pedidos (extractores e
  descarregadores). Antes de delegar, `teto_da_onda.reservar(host)`; sem lugar, levanta
  e o pedido nao sai. O yt-dlp termina com erro, e a recusa fica escrita no ficheiro
  que o pai nomeou em SINTONIA_TETO_RECUSAS.

Sem livro da onda (SINTONIA_TETO_ONDA vazio) o freio nao trava — o mesmo que no
`scrap_http`. Tudo o resto do yt-dlp fica igual: mesmos argumentos, mesmo
`--print-traffic`, mesma saida.
"""
import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_AQUI), "coleta"))
import teto_da_onda as teto  # noqa: E402


class FreioDoYtDlp(Exception):
    """Levantada dentro do yt-dlp: o pedido nao saiu (teto do dominio)."""


def instalar():
    import yt_dlp  # noqa: PLC0415
    from urllib.parse import urlsplit  # noqa: PLC0415
    original = yt_dlp.YoutubeDL.urlopen

    def urlopen(self, req):
        url = req if isinstance(req, str) else getattr(req, "url", None) or getattr(req, "full_url", "")
        try:
            teto.reservar(urlsplit(url).hostname, url=url, quem="yt-dlp")
        except teto.TetoDaOnda as e:
            raise FreioDoYtDlp(str(e)) from e
        return original(self, req)

    yt_dlp.YoutubeDL.urlopen = urlopen
    return yt_dlp


def main(argv=None):
    yt_dlp = instalar()
    return yt_dlp.main(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
