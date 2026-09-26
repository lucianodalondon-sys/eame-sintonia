"""MAESTRO-SOCIAL · mutacao: cada mutante tira uma peca do maestro, do baixador ou do escritor da 037.

    py -B provas/_mutantes_maestro_social.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTES = ["tests.test_maestro_social", "tests.test_baixador_social", "tests.test_video_na_sala",
          "tests.test_prova_de_post_de_pessoa"]
M = "ferramentas/maestro_social/maestro_social.py"
Y = "ferramentas/youtube_transcrever.py"
MUTANTES = [
    ("a onda nao nomeia o livro", M,
     '        os.environ["SINTONIA_TETO_ONDA"] = str(livro)       # herdado: orquestrador -> scrap -> yt-dlp com freio\n',
     "        pass\n"),
    ("um livro so para todas as ondas", M,
     '        livro = saida / ("ONDA-%02d" % n) / "TETO-ONDA.json"\n', '        livro = saida / "TETO-ONDA.json"\n'),
    ("VPN antes nao se confere", M,
     '            if antes.get("PAIS") != "IT":\n', '            if False:\n'),
    ("VPN depois nao se confere", M,
     '            if depois.get("PAIS") != "IT":\n', '            if False:\n'),
    ("prova-teto ignorada", M,
     '        if pt.get("ESTADO") != "PASS":\n', '        if False:\n'),
    ("retomar relanca as feitas", M,
     '    feitas = {f["SOURCE_ID"] for f in estado["FONTES"]}\n', '    feitas = set()\n'),
    ("--canario nao abre nada", M,
     '        if canario and not l["NA_ONDA"]', '        if False and not l["NA_ONDA"]'),
    ("baixador sem fatia grande", Y, "            '--http-chunk-size', '50M',\n", ""),
    ("baixador sem filtro de duracao", Y,
     "            '--match-filter', 'duration <= %d' % duracao_max_s(),\n", ""),
    ("video longo sem nome", Y,
     "    if r.returncode == 0 and 'MAESTRO_PASSOU_O_FILTRO' not in (r.stdout or ''):\n", "    if False:\n"),
    ("UNKNOWN entra na Sala", "admissao/video_na_sala.py",
     "    if not RE_IDENTIDADE.match(vid):\n        return None\n", "    if not vid:\n        return None\n"),
    ("D80: a busca publica prova", "leis/prova_de_post_de_pessoa.py",
     '    if origem == "BUSCA_PUBLICA":
', '    if False:
'),
    ("D80: um pedaco do nome basta", "leis/prova_de_post_de_pessoa.py",
     "    return len(pedacos) >= 2 and all(", "    return len(pedacos) >= 1 and all("),
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
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        finally:
            with open(alvo, "w", encoding="utf-8", newline="") as f:
                f.write(original)
        morto = r.returncode != 0
        mortos += morto
        print("%-38s %s" % (nome, "MORTO" if morto else "SOBREVIVEU"))
    print("MUTANTES %d/%d mortos" % (mortos, len(MUTANTES)))
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
