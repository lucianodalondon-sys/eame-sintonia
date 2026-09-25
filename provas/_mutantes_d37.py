"""D37 · mutacao: cada mutante estraga os campos de politica; o teste tem de morrer.

    py -B provas/_mutantes_d37.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALVO = os.path.join(RAIZ, "coleta", "adaptador_linkedin.py")
MUTANTES = [
    ("sem ROBOTS_STATUS", "        'ROBOTS_STATUS': ROBOTS_STATUS,\n", ""),
    ("ROBOTS igual a politica", "ROBOTS_STATUS = 'DISALLOW_ALL'", "ROBOTS_STATUS = 'DISALLOWED'"),
    ("sem endereco do robots", "ROBOTS_URL = 'https://www.linkedin.com/robots.txt'", "ROBOTS_URL = ''"),
    ("envelope sem os campos", "    envelope.update(politica_do_objeto(nome_decisao, decisao_robots))\n",
     "    envelope['OWNER_AUTHORIZED'] = 'SIM'\n"),
    ("bruto sem os campos", "        **politica_do_objeto(nome_decisao, decisao_robots),\n",
     "        'OWNER_AUTHORIZED': 'SIM',\n"),
    # D41: a pessoa leva os mesmos campos, com a decisao dela
    ("pessoa carimbada D37", "    'DECISAO_DO_ROBOTS': 'D41',\n", "    'DECISAO_DO_ROBOTS': 'D37',\n"),
    ("pessoa perde a decisao da porta", "    decisao_robots = dec.get('DECISAO_DO_ROBOTS', DECISAO_DO_ROBOTS)\n",
     "    decisao_robots = DECISAO_DO_ROBOTS\n"),
    ("data da medicao inventada", "ROBOTS_MEDIDO_EM = '2026-09-08'", "ROBOTS_MEDIDO_EM = '2026-09-24'"),
]


def main():
    original = open(ALVO, encoding="utf-8").read()
    mortos = 0
    try:
        for nome, de, para in MUTANTES:
            assert original.count(de) == 1, nome
            open(ALVO, "w", encoding="utf-8", newline="").write(original.replace(de, para))
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_d37_campos_de_politica"],
                               cwd=RAIZ, capture_output=True, text=True,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            morto = r.returncode != 0
            mortos += morto
            print("%-28s %s" % (nome, "MORTO" if morto else "SOBREVIVEU"))
    finally:
        open(ALVO, "w", encoding="utf-8", newline="").write(original)
    print("MUTANTES %d/%d mortos" % (mortos, len(MUTANTES)))
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())
