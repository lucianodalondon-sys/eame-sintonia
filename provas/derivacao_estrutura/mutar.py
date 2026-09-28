#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTAÇÃO DA DERIVACAO-ESTRUTURA: cada mutante tem de pôr pelo menos um teste vermelho.

Escreve o mutante no ficheiro, corre os testes, e repõe SEMPRE o original (try/finally).
Para cada mutante diz QUAIS ficheiros de teste ficaram vermelhos — não basta «algum».

    py provas/derivacao_estrutura/mutar.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

RAIZ = Path(__file__).resolve().parents[2]
LIMPAR = RAIZ / "coleta" / "texto_fonte.py"
EXECUTOR = RAIZ / "coleta" / "executor_texto_de_html.py"
TESTES = ["tests/test_derivacao_estrutura.py", "tests/test_a_receita_tem_versao.py",
          "tests/test_derivacao_estrutura_v2.py",
          "tests/test_tempo_e_lugar_da_publicacao.py", "tests/test_leitor_data_youtube.py",
          "tests/test_a_rota_do_html.py"]

#: nome -> (ficheiro, trecho original, trecho mutante, testes que TÊM de ficar vermelhos)
MUTANTES = {
    # B1 revertido: as etiquetas de bloco voltam a dar espaço (a limpar() antiga)
    "M1_B1_revertido": (LIMPAR, "    return '\\n' if _RE_BLOCO.match(m.group(0)) else ' '\n",
                        "    return ' '\n",
                        ["tests/test_derivacao_estrutura.py", "tests/test_a_receita_tem_versao.py",
                         "tests/test_derivacao_estrutura_v2.py"]),
    # B1 parcial: `td`/`th` deixam de ser bloco — a régua muda e a versão não
    "M2_regua_muda_sem_versao": (LIMPAR, "          'td', 'th', 'section',", "          'section',",
                                 ["tests/test_a_receita_tem_versao.py"]),
    # a subida de versão revertida
    "M3_versao_nao_subiu": (EXECUTOR, 'EXECUTOR_VERSION = "4"', 'EXECUTOR_VERSION = "3"',
                            ["tests/test_a_receita_tem_versao.py"]),
    # a régua sai da receita
    "M4_regua_fora_da_receita": (
        EXECUTOR, '        "TEXT_RULE_PROBE_SHA256": _texto_fonte.impressao_da_regua(),\n', "",
        ["tests/test_a_receita_tem_versao.py"]),
    # V2 revertido: a limpar/2 de duas passagens (o «</» órfão engole título e subtítulo)
    "M9_V2_duas_passagens": (
        LIMPAR, "    t = _RE_ETIQUETA.sub(_etiqueta, t)\n    t = _RE_ORFAO.sub(' ', t)\n",
        "    t = re.sub(r'</?(?:%s)\\b[^>]*>' % '|'.join(BLOCOS), '\\n', t, flags=re.I)\n"
        "    t = re.sub(r'<[^>]+>', ' ', t)\n",
        ["tests/test_derivacao_estrutura_v2.py", "tests/test_a_receita_tem_versao.py"]),
    # V2 relaxado: a etiqueta volta a poder atravessar outro «<» (mas numa passagem só)
    "M10_V2_etiqueta_atravessa_menor": (
        LIMPAR, "_RE_ETIQUETA = re.compile(r'<!--[^>]*>|<[A-Za-z/!?][^<>]*>')",
        "_RE_ETIQUETA = re.compile(r'<!--[^>]*>|<[^>]+>')",
        ["tests/test_derivacao_estrutura_v2.py", "tests/test_a_receita_tem_versao.py"]),
    # V2 relaxado: o «<» de marcação órfão fica como texto
    "M11_V2_orfao_fica": (LIMPAR, "    t = _RE_ORFAO.sub(' ', t)\n", "",
                          ["tests/test_derivacao_estrutura_v2.py", "tests/test_a_receita_tem_versao.py"]),
    # B2 relaxado: qualquer classe com «date»
    "M5_B2_qualquer_classe_date": (
        EXECUTOR, '    return "content-date" in classes',
        '    return any("date" in c for c in classes)',
        ["tests/test_derivacao_estrutura.py"]),
    # B2 relaxado: sem exigir o irmão content-category
    "M6_B2_sem_irmao_categoria": (EXECUTOR, "            if not cats:\n",
                                  "            if False and not cats:\n",
                                  ["tests/test_derivacao_estrutura.py"]),
    # B2 relaxado: a data pode estar DENTRO do valor (rótulos, eventos passam)
    "M7_B2_data_em_qualquer_parte_do_valor": (
        EXECUTOR, "    m = _RE_DATA_IT.match(s)\n", "    m = _RE_DATA_IT.search(s)\n",
        ["tests/test_derivacao_estrutura.py"]),
    # B2 relaxado: mais de um campo, fica o primeiro
    "M8_B2_mais_de_um_campo_fica_o_primeiro": (
        EXECUTOR, "    elif len(brutas) > 1:\n", "    elif False and len(brutas) > 1:\n",
        ["tests/test_derivacao_estrutura.py"]),
}


def correr():
    vermelhos = []
    for t in TESTES:
        r = subprocess.run([sys.executable, "-B", t], cwd=RAIZ, capture_output=True, text=True)
        if r.returncode != 0:
            vermelhos.append(t)
    return vermelhos


def main():
    originais = {f: f.read_bytes() for f in (LIMPAR, EXECUTOR)}
    res = {}
    try:
        base = correr()
        assert not base, "os testes tem de passar antes de mutar: %s" % base
        for nome, (alvo, a, b, esperados) in MUTANTES.items():
            texto = originais[alvo].decode("utf-8")
            nl = "\r\n" if "\r\n" in texto else "\n"
            a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
            assert texto.count(a2) == 1, nome
            mutado = texto.replace(a2, b2)
            if nome == "M7_B2_data_em_qualquer_parte_do_valor":
                # `search` sozinho ainda esbarra no ^...$ da expressão: tira-se a âncora também
                ancora = 'r"^(\\d{1,2})\\s+(%s)\\.?\\s+(\\d{4})$"'
                assert mutado.count(ancora) == 1, nome
                mutado = mutado.replace(ancora, 'r"(\\d{1,2})\\s+(%s)\\.?\\s+(\\d{4})"')
            alvo.write_bytes(mutado.encode("utf-8"))
            try:
                v = correr()
            finally:
                alvo.write_bytes(originais[alvo])
            res[nome] = {"ESTADO": "MORTO" if v else "SOBREVIVEU", "VERMELHOS": v,
                         "ESPERADOS_VERMELHOS": esperados,
                         "ESPERADOS_CUMPRIDOS": all(e in v for e in esperados)}
    finally:
        for f, b in originais.items():
            f.write_bytes(b)
    ok = all(v["ESTADO"] == "MORTO" and v["ESPERADOS_CUMPRIDOS"] for v in res.values())
    print(json.dumps({"MUTANTES": res,
                      "MORTOS": sum(v["ESTADO"] == "MORTO" for v in res.values()), "DE": len(res),
                      "ORIGINAIS_REPOSTOS": all(f.read_bytes() == b for f, b in originais.items())},
                     ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
