#!/usr/bin/env python3
"""LUGAR-FATO · teste de mutacao do extrator (leis/fato_do_texto.py).

Cada mutante estraga UMA regra da missao numa COPIA (pasta temporaria; a arvore nao e tocada) e corre
tests/test_fato_do_texto.py contra ela. Mutante que passa nos testes = o teste nao guarda a regra.

    py scripts/lugar_fato/mutar_fato_do_texto.py      -> escreve MUTACAO-FATO-DO-TEXTO-V1.json ao lado
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = "leis/fato_do_texto.py"

MUTANTES = [
    ("M1_SOURCE_LOCATION_COPIADO", "reprova se o lugar da fonte puder virar lugar do facto",
     [("publication_time_basis: str | None = None) -> dict:",
       "publication_time_basis: str | None = None, source_location: str | None = None) -> dict:"),
      ("        fact_location = fact_location_precision = NAO_SEI\n",
       "        fact_location = source_location or NAO_SEI\n        fact_location_precision = NAO_SEI\n")]),
    ("M2_PUBLICACAO_VIRA_FACT_TIME", "reprova se a data de publicacao preencher o fact_time",
     [("        fact_time = fact_time_kind = NAO_SEI\n",
       "        fact_time = publication_time or NAO_SEI\n        fact_time_kind = NAO_SEI\n")]),
    ("M3_LUGAR_DO_MENU_CONTA", "reprova se a pagina inteira (menu/rodape) for lida como corpo",
     [("    c = corpo(texto)\n", "    c = str(texto or '')\n")]),
    ("M4_RODAPE_E_CORPO", "reprova se a linha de rodape/institucional entrar no corpo",
     [("        if RODAPE.search(l):\n            continue\n", "")]),
    ("M5_RELATIVA_SEM_PUBLICACAO", "reprova se 'ieri/la settimana scorsa' valer sem publicacao provada",
     [("    if not publication_time or not publication_time_basis:\n        return None\n",
       "    if not publication_time:\n        return None\n    if not publication_time_basis:\n        publication_time_basis = 'sem base'\n")]),
    ("M5b_DATA_DE_COLETA_NO_LUGAR_DA_PUBLICACAO", "D63: reprova se a conta usar a data de coleta (agora) em vez da publicacao",
     [("    pub = publicacao_provada(publication_time, publication_time_basis)\n",
       "    pub = date.today()\n")]),
    ("M5c_PARAMETRO_DE_COLETA", "D63: reprova se a funcao aceitar a data de coleta como ancora de reserva",
     [("publication_time_basis: str | None = None) -> dict:",
       "publication_time_basis: str | None = None, captured_at: str | None = None) -> dict:"),
      ("    pub = publicacao_provada(publication_time, publication_time_basis)\n",
       "    pub = publicacao_provada(publication_time, publication_time_basis) or publicacao_provada(captured_at, 'CAPTURED_AT')\n")]),
    ("M6_PUBLICACAO_SEM_BASE_ANCORA", "reprova se publicacao com base NAO SEI ancorar relativas",
     [("    if str(publication_time_basis).strip().upper().startswith((\"NAO SEI\", \"NÃO SEI\", \"UNKNOWN\")):\n        return None\n", "")]),
    ("M7_SEM_TAPAR_SERIE", "reprova se a serie de anos virar ano do facto",
     [('("SERIE_DE_ANOS", re.compile(r"', '("SERIE_DE_ANOS", re.compile(r"(?!x)x')]),
    ("M7c_SEM_TAPAR_CARIMBO", "reprova se a data no inicio da linha de lista virar tempo do facto",
     [('("CARIMBO_DE_LISTA", re.compile(r"', '("CARIMBO_DE_LISTA", re.compile(r"(?!x)x')]),
    ("M7d_SEM_TAPAR_PRAZO", "reprova se 'fino a novembre' virar tempo do facto",
     [('("FIM_DE_PRAZO", re.compile(r"', '("FIM_DE_PRAZO", re.compile(r"(?!x)x')]),
    ("M8_SO_O_PRIMEIRO_LUGAR", "reprova se varios lugares forem reduzidos a um por adivinhacao",
     [("    for a in aceitas:\n", "    for a in aceitas[:1]:\n")]),
    ("M9_BASE_SEM_TRECHO", "reprova se a base do lugar perder o trecho",
     [('l["TIPO_DE_EVIDENCIA"], l["TRECHO"]) for l in esc)', 'l["TIPO_DE_EVIDENCIA"], "") for l in esc)')]),
    ("M10_EVENTO_VIRA_CAMPO", "D62: reprova se o lugar de evento virar lugar de campo (doenca/praga)",
     [("[(m, EVENTO, None) for m in _RE_EVENTO", "[(m, CAMPO, None) for m in _RE_EVENTO")]),
    ("M11_MERCADO_VIRA_CAMPO", "D62: reprova se o lugar de mercado virar lugar de campo",
     [("[(m, MERCADO, None) for m in _RE_MERCADO", "[(m, CAMPO, None) for m in _RE_MERCADO")]),
    ("M12_EVENTO_VENCE_CAMPO", "D62: reprova se o lugar de evento passar a frente do de campo",
     [("ORDEM_DOS_TIPOS = (CAMPO, EVENTO, MERCADO)", "ORDEM_DOS_TIPOS = (EVENTO, CAMPO, MERCADO)")]),
    ("M13_SEMANA_VIRA_UM_DIA", "D63: reprova se 'la settimana scorsa' virar um dia inventado",
     [('return "%s/%s" % (seg.isoformat(), (seg + timedelta(days=6)).isoformat()), "WEEK"',
       'return (seg + timedelta(days=2)).isoformat(), "WEEK"')]),
    ("M14_SEM_MEDIDA_VIRA_DATA", "D63: reprova se 'nei giorni scorsi' virar uma data",
     [('recentemente", ("SEM_MEDIDA", None)),', 'recentemente", ("DIA", -3)),')]),
    ("M16_PALAVRA_COMUM_VIRA_LUGAR", "reprova se «fermo» (parado) voltar a ser a provincia de Fermo",
     [('re.escape(lugar), str(frase or ""))', 're.escape(lugar), str(frase or ""), re.I)')]),
    ("M17_EVENTI_ESTREMI_VIRA_EVENTO", "reprova se «eventi estremi» (tempo no campo) virar evento tecnico",
     [(r'r"event[oi](?!\s+(?:estrem|meteo|atmosferic|climatic|calamitos|alluvional|avvers))"', r'r"event[oi]"')]),
    ("M18_OGGI_SEM_MARCA_CONTA", "D64: reprova se «oggi» sem marca de dia virar a data",
     [('    return False, "«oggi» sem marca de que é o próprio dia', '    return True, "«oggi» sem marca de que é o próprio dia')]),
    ("M19_AD_OGGI_CONTA", "D64: reprova se «ad oggi / fino ad oggi / al giorno d'oggi» virar a data",
     [("    if _OGGI_HOJE_EM_DIA_ANTES.search(antes):\n", "    if False:\n")]),
    ("M20_OGGI_COM_MARCA_NAO_CONTA", "D64: reprova se «oggi, lunedì» / «oggi alle» deixar de contar",
     [("    if _OGGI_DIA_DEPOIS.search(depois) or _OGGI_DIA_ANTES.search(antes):\n", "    if False:\n")]),
    ("M21_PRODUCAO_VIRA_MERCADO", "(a): reprova se o lugar onde se produz voltar a sair MERCADO",
     [("[(m, CAMPO, \"PRODUCAO\") for m in _RE_PRODUCAO", "[(m, MERCADO, None) for m in _RE_PRODUCAO")]),
    ("M22_PRODUCAO_VIRA_FOCO", "(a): reprova se o lugar de producao ganhar evidencia de foco/observacao",
     [('"TIPO_DE_EVIDENCIA": FL.OTHER_EVIDENCE, "TRECHO": _trecho(r["EVIDENCE"])', '"TIPO_DE_EVIDENCIA": FL.OTHER_EVIDENCE if kind != CAMPO else "FIELD_OBSERVATION", "TRECHO": _trecho(r["EVIDENCE"])')]),
    ("M23_INSTITUCIONAL_E_FACTO", "(b): reprova se a data de exame/curso voltar a ser tempo do facto",
     [('        motivo = ("INSTITUCIONAL_NAO_FATO" if _RE_INSTITUCIONAL.search(ev)\n', '        motivo = ("INSTITUCIONAL_NAO_FATO" if False\n')]),
    ("M24_ANCORA_DENTRO_DA_PALAVRA", "reprova se «coltura» dentro de «agricoltura» voltar a amarrar a data",
     [('_RE_ANCORAS_DE_CAMPO = re.compile(r"(?<![0-9a-z])(?:%s)"', '_RE_ANCORAS_DE_CAMPO = re.compile(r"(?:%s)"')]),
    ("M25_AMBIGUO_ESCOLHE", "reprova se duas contas diferentes no mesmo texto derem uma data escolhida",
     [('        if len({x["CONTA"]["VALOR"] for x in xs}) > 1:\n', '        if False:\n')]),
    ("M26_COMPARACAO_CONTA", "reprova se «rispetto allo stesso periodo dello scorso anno» virar o tempo do facto",
     [("    if _RE_COMPARACAO.search(antes):\n        return None, \"termo de compara", "    if False:\n        return None, \"termo de compara")]),
    ("M27_PRODUCAO_SEM_DISTANCIA", "(a): reprova se a palavra de producao longe do lugar o fizer CAMPO",
     [("DISTANCIA_MAXIMA_DA_PRODUCAO = 60 ", "DISTANCIA_MAXIMA_DA_PRODUCAO = 9999 ")]),
    ("M28_DIA_CALCULADO_VIRA_INTERVALO_DE_FUGA", "D70: reprova se o dia calculado voltar a escrever-se como intervalo "
     "desse dia so para fugir a comparacao da lei (contorno)",
     [("    return d.isoformat()\n", '    return "%s/%s" % (d.isoformat(), d.isoformat())\n')]),
    ("M29_PUBLISHED_AT_COM_PROVA_VOLTA", "D69: reprova se a data calculada disser PUBLISHED_AT_COM_PROVA («o mesmo instante», nao provado)",
     [("            fact_time_basis = RELATIVA\n", "            fact_time_basis = \"PUBLISHED_AT_COM_PROVA\"\n")]),
    ("M30_EVIDENCIA_DA_CONTA_PERDIDA", "D70: reprova se o trecho da conta se perder (a lei nao a refaz)",
     [('            fact_time_evidencia = tempo["TRECHO"]', "            fact_time_evidencia = NAO_SE_APLICA")]),
    ("M31_EXPRESSAO_PERDIDA", "D70: reprova se a expressao original se perder (a lei nao a refaz)",
     [('            fact_time_expressao = tempo["EXPRESSAO"]', "            fact_time_expressao = NAO_SE_APLICA")]),
    ("M32_TRECHO_SEM_A_EXPRESSAO", "D70: reprova se o trecho guardado puder cortar a expressao (frase longa)",
     [("    return _trecho(t[max(a, ini - 150):min(b, fim + 150)], 400)", "    return _trecho(t[a:b], 200)")]),
    ("M15_CALCULADA_ESCONDIDA", "D63: reprova se a precisao nao disser que a data foi calculada",
     [('("+CALCULADA" if tempo.get("CALCULADA") else "")', '""')]),
]


def correr(pasta):
    p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_fato_do_texto"], cwd=pasta,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ult = [l for l in p.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return p.returncode, " | ".join(ult)


def main():
    orig = (RAIZ / ALVO).read_text(encoding="utf-8")
    res = {"DATASET": "MUTACAO-FATO-DO-TEXTO-V1", "ALVO": ALVO,
           "ALVO_SHA256": hashlib.sha256(orig.encode("utf-8")).hexdigest(), "MUTANTES": []}
    with tempfile.TemporaryDirectory(prefix="mut-fato-") as tmp:
        tmp = Path(tmp)
        for d in ("leis", "tests"):
            shutil.copytree(RAIZ / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        rc, linha = correr(tmp)
        res["SEM_MUTANTE"] = {"RC": rc, "SAIDA": linha}
        if rc != 0:
            print("o original ja falha:", linha)
            sys.exit(2)
        for nome, regra, trocas in MUTANTES:
            s = orig
            for a, b in trocas:
                if s.count(a) != 1:
                    raise SystemExit("mutante %s: trecho aparece %d vezes: %r" % (nome, s.count(a), a[:60]))
                s = s.replace(a, b)
            (tmp / ALVO).write_text(s, encoding="utf-8")
            shutil.rmtree(tmp / "leis" / "__pycache__", ignore_errors=True)
            comp = subprocess.run([sys.executable, "-c", "import ast,sys;ast.parse(open(sys.argv[1],encoding='utf-8').read())",
                                   str(tmp / ALVO)], capture_output=True, text=True)
            rc, linha = correr(tmp)
            # so conta como morto se um teste FALHOU (assert); erro de execucao nao prova nada
            morto = rc != 0 and comp.returncode == 0 and "FAILED (failures=" in linha
            res["MUTANTES"].append({"MUTANTE": nome, "REGRA": regra, "COMPILA": comp.returncode == 0,
                                    "RC": rc, "SAIDA": linha, "RESULTADO": "MORTO" if morto else "SOBREVIVEU"})
            print("%-32s %s  %s" % (nome, "MORTO" if morto else "SOBREVIVEU", linha))
        (tmp / ALVO).write_text(orig, encoding="utf-8")
    res["MORTOS"] = sum(m["RESULTADO"] == "MORTO" for m in res["MUTANTES"])
    res["TOTAL"] = len(res["MUTANTES"])
    out = Path(__file__).with_name("MUTACAO-FATO-DO-TEXTO-V1.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mortos %d de %d -> %s" % (res["MORTOS"], res["TOTAL"], out.name))
    sys.exit(0 if res["MORTOS"] == res["TOTAL"] else 1)


if __name__ == "__main__":
    main()
