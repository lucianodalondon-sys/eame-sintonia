"""SOCIAL-MICRO-PREP · mutacao: cada mutante estraga a leitura de tempo e lugar da rota do bruto.

    py -B provas/_mutantes_social_bruto.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTES = ["tests.test_social_bruto_leva_a_evidencia"]
MUTANTES = [
    ("o bruto vai a porta sem leitura", "orquestrador/orquestrador.py",
     "            julgar = [item_do_bruto_para_a_porta(i) for i in\n"
     "                      recibo[\"INGRESSO\"].get(\"PARA_A_PORTA\") or []]\n",
     "            julgar = recibo[\"INGRESSO\"].get(\"PARA_A_PORTA\") or []\n"),
    ("as precisoes ficam para tras", "orquestrador/orquestrador.py",
     "    publicacao = {k: _v(k) for k in ing.TEMPO_E_LUGAR_PARA_A_EVIDENCIA\n",
     "    publicacao = {k: _v(k) for k in ()\n"),
    ("a publicacao vira data do facto", "orquestrador/orquestrador.py",
     "    fora = dict(item)\n    fora.update(ing.para_a_porta(_fato_do_texto(\n",
     "    fora = dict(item, fact_time=item.get('published_at'))\n    fora.update(ing.para_a_porta(_fato_do_texto(\n"),
    ("mexe no item da entrada", "orquestrador/orquestrador.py",
     "    fora = dict(item)\n    fora.update(ing.para_a_porta(_fato_do_texto(\n",
     "    fora = item\n    fora.update(ing.para_a_porta(_fato_do_texto(\n"),
    ("inventa precisao quando falta", "orquestrador/orquestrador.py",
     "        ev[k] = publicacao.get(k) or ing.NAO_SEI_ID\n",
     "        ev[k] = publicacao.get(k) or 'COUNTRY'\n"),
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
