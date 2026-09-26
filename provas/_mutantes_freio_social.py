"""FREIO-SOCIAL · mutacao: cada mutante tira uma peca do freio; os testes tem de morrer.

    py -B provas/_mutantes_freio_social.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTES = ["tests.test_freio_social", "tests.test_teto_dominio"]
MUTANTES = [
    ("o portao do Scrap nao reserva", "coleta/scrap_http.py",
     "            teto.reservar(host, url=req.full_url, quem='scrap_http')\n",
     "            pass\n"),
    ("o 6.o passa (>= vira >)", "coleta/teto_da_onda.py",
     "            if gasto >= teto():\n", "            if gasto > teto():\n"),
    ("D41 esquecida no Scrap", "coleta/teto_da_onda.py",
     'MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}\n', "MESMO_ORCAMENTO = {}\n"),
    ("o yt-dlp corre sem freio", "ferramentas/yt_dlp_com_freio.py",
     "    yt_dlp.YoutubeDL.urlopen = urlopen\n", "    pass\n"),
    ("o transcritor volta ao yt-dlp nu", "ferramentas/youtube_transcrever.py",
     "            [sys.executable, FREIO_DO_YT_DLP, '-q', '--no-warnings',\n",
     "            [sys.executable, '-m', 'yt_dlp', '-q', '--no-warnings',\n"),
    ("as recusas do filho perdem-se", "ferramentas/youtube_transcrever.py",
     "    teto.acrescentar_recusas(lidas)\n", "    pass\n"),
    ("corrida social sozinha sem livro proprio", "coleta/scrap_colheita.py",
     "    if fase not in FASES_CONTADAS or teto.livro():\n        return None\n",
     "    return None\n"),
    ("a recusa nao vai para a linha", "coleta/scrap_colheita.py",
     "        linha['CORTESIA']['RECUSAS'] = recusadas\n", "        pass\n"),
    ("D41 esquecida na web", "coleta/italy_pilot_collect.mjs",
     "  return MESMO_ORCAMENTO[d] || d;\n", "  return d;\n"),
]


def main():
    mortos = 0
    for nome, rel, de, para in MUTANTES:
        alvo = os.path.join(RAIZ, rel)
        with open(alvo, encoding="utf-8", newline="") as f:
            original = f.read()
        de_ = de.replace("\n", "\r\n") if "\r\n" in original and de not in original else de
        para_ = para.replace("\n", "\r\n") if de_ != de else para
        assert original.count(de_) == 1, nome
        try:
            with open(alvo, "w", encoding="utf-8", newline="") as f:
                f.write(original.replace(de_, para_))
            r = subprocess.run([sys.executable, "-B", "-m", "unittest"] + TESTES, cwd=RAIZ,
                               capture_output=True, text=True,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                                        NODE_DISABLE_COMPILE_CACHE="1"))
        finally:
            with open(alvo, "w", encoding="utf-8", newline="") as f:
                f.write(original)
        morto = r.returncode != 0
        mortos += morto
        print("%-42s %s" % (nome, "MORTO" if morto else "SOBREVIVEU"))
    print("MUTANTES %d/%d mortos" % (mortos, len(MUTANTES)))
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
