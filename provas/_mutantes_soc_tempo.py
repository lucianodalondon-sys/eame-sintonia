"""SOC-TEMPO (D61/D63) · mutacao: cada mutante estraga a data de publicacao ou o lugar de quem publica.

    py -B provas/_mutantes_soc_tempo.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTES = ["tests.test_soc_tempo_publicacao_e_lugar", "curadoria.test_soc_onda2_social"]
MUTANTES = [
    ("a hora da coleta vira publicacao (D63)", "coleta/scrap_colheita.py",
     "    'COLLECTED_AT': 'OBSERVED_AT',\n", "    'COLLECTED_AT': 'PUBLISHED_AT',\n"),
    ("base sem a data que ela prova", "coleta/scrap_colheita.py",
     "        fora.pop('PUBLISHED_AT_BASIS', None)\n", "        pass\n"),
    ("o pais do pedido vira lugar da fonte", "coleta/scrap_colheita.py",
     "    if 'SOURCE_LOCATION' not in fora and fonte:\n",
     "    if 'SOURCE_LOCATION' not in fora and objeto.get('COUNTRY_SCOPE'):\n"
     "        fora['SOURCE_LOCATION'] = objeto.get('COUNTRY_SCOPE')\n"
     "    if 'SOURCE_LOCATION' not in fora and fonte:\n"),
    ("a regiao de cobertura vira morada", "leis/lugar_da_organizacao.py",
     'RE_PAIS = re.compile(r"^COUNTRY:\\s*(.+)$")', 'RE_PAIS = re.compile(r"^REGION:\\s*(.+)$")'),
    ("minuto vira segundo", "coleta/adaptador_linkedin.py",
     "        return 'MINUTE'\n", "        return 'SECOND'\n"),
    ("a base nao atravessa a porta", "coleta/ingresso.py",
     '    "PUBLISHED_AT_BASIS": "published_at_basis",\n', ""),
    ("o contrato nao guarda o lugar", "curadoria/worker.py",
     "        novo.update(LO.lugar_da_organizacao(site))\n", "        pass\n"),
]


def main():
    mortos = 0
    for nome, rel, de, para in MUTANTES:
        alvo = os.path.join(RAIZ, rel)
        original = open(alvo, encoding="utf-8").read()
        assert original.count(de) == 1, nome
        try:
            open(alvo, "w", encoding="utf-8", newline="").write(original.replace(de, para))
            r = subprocess.run([sys.executable, "-B", "-m", "unittest"] + TESTES, cwd=RAIZ,
                               capture_output=True, text=True,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        finally:
            open(alvo, "w", encoding="utf-8", newline="").write(original)
        morto = r.returncode != 0
        mortos += morto
        print("%-40s %s" % (nome, "MORTO" if morto else "SOBREVIVEU"))
    print("MUTANTES %d/%d mortos" % (mortos, len(MUTANTES)))
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
