#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LOTE6-INTEGRA · mutacao dos PONTOS DE JUNCAO das quatro entregas. Sem rede.

    python3 provas/lote6_integra/mutacao_juncao.py   -> MUTACAO-JUNCAO.json ao lado

Cada mutante estraga UM ponto onde duas entregas se tocam (a lei D112 do metodo-puglia, o extrator por
secao do boletim-por-secao, o extrator dos estudos, o motor das capacidades do int-r7-caps), numa COPIA da
arvore (pasta temporaria; a arvore nao e tocada), e corre os testes da juncao contra ela. So conta MORTO
quando um teste FALHA por assert: erro de execucao nao prova que o teste guarda a regra.
Um mutante e uma lista de (antes, depois); cada «antes» tem de aparecer UMA vez no ficheiro.
"""
import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTES = ["tests.test_lote6_integra", "tests.test_metodo_puglia", "tests.test_boletim_por_secao",
          "tests.test_estudo_chaves", "tests.test_motor_das_capacidades"]
BC, EC, MO, GP = ("leis/boletim_do_campo.py", "leis/estudo_chaves.py", "motor/motor_das_capacidades.py",
                  "scripts/lugar_fato/gold_puglia.py")

MUTANTES = [
    ("J01_TRAVA_DO_LUGAR_DESLIGADA", "a COL-LAW-032 deixa de decidir o lugar do extrator", BC,
     [("    valor, porque = LF.fact_location(lugar[\"LOCATION_SOURCE\"], proposto)",
       "    valor, porque = lugar[\"VALOR\"], \"\"")]),
    ("J02_TRAVA_DA_ENTIDADE_DESLIGADA", "a COL-LAW-221 deixa de decidir a procedencia do extrator", BC,
     [("    if ok:\n        return r\n", "    if True:\n        return r\n")]),
    # medido: `tuple(AF.ENTITY_SOURCES)` sobreviveu — era EQUIVALENTE (tuple() de uma tupla devolve o
    # mesmo objeto). O defeito real e a copia escrita a mao, que e o que o ramo tinha antes da juncao.
    ("J03_VOCABULARIO_COPIADO", "o extrator volta a ter vocabulario proprio (dois donos)", BC,
     [("ENTITY_SOURCES = AF.ENTITY_SOURCES\n",
       'ENTITY_SOURCES = ("SPAN", "PARAGRAPH_CONTEXT", "SECTION_TITLE", "DOCUMENT_TITLE", "UNKNOWN")\n')]),
    ("J04_GOLD_GEMEO", "o harness volta a ler a copia gemea em docs/iab", GP,
     [('GOLD = RAIZ / "tests" / "fixtures" / "puglia" / "GOLD-FIXTURE-PUGLIA-V1.json"',
       'GOLD = RAIZ / "docs" / "iab" / "puglia" / "GOLD-FIXTURE-PUGLIA-V1.json"')]),
    ("J05_ESTUDO_GRAVA_NAO_SEI_NA_PROCEDENCIA", "ENTITY_SOURCE sem trecho volta a ser «NAO SEI» (fora da lei)", EC,
     [('ENTITY_SOURCE_SEM_TRECHO = "UNKNOWN"', 'ENTITY_SOURCE_SEM_TRECHO = "NAO SEI"'),
      ("\n_conferir_vocabulario()\n", "\n")]),
    ("J06_JANELA_AO_LADO_DO_READY", "o motor volta a levar a janela fora do READY (duas copias)", MO,
     [('        itens.append({"READY": ready})',
       '        itens.append({"READY": ready, "JANELA_DECLARADA": ready["JANELA_DECLARADA"]})'),
      ('        sobra = sorted(set(r) - {"READY"})', '        sobra = sorted(set(r) - {"READY", "JANELA_DECLARADA"})')]),
    ("J07_COPIA_DAS_CAPACIDADES_SEM_D112A", "as capacidades recebem a janela crua, sem a D112a", MO,
     [('        ready["JANELA_DECLARADA"] = jd     #', '        pass  #')]),
    ("J08_078_ENTRE_CASAS", "mesma redacao em casas diferentes vira INT-LAW-078", MO,
     [('"RELATION": REL_078 if len(por) == 1 else REL_NAO_SEI,', '"RELATION": REL_078,')]),
    ("J09_DIVERGENT_NA_MESMA_CASA", "limites diferentes da mesma casa viram DIVERGENT_RECOMMENDATIONS", MO,
     [('"RELATION": REL_DIVERGENT if len(casas) > 1 else REL_NAO_SEI,', '"RELATION": REL_DIVERGENT,')]),
    ("J10_TEMPORAL_PROVA_O_CAMPO", "mudanca de recomendacao no tempo passa a provar o campo", MO,
     [('"CONCLUIR_MUDANCA_DO_CAMPO": False, "LEI": "INT-LAW-079",',
       '"CONCLUIR_MUDANCA_DO_CAMPO": True, "LEI": "INT-LAW-079",')]),
    ("J11_RELACAO_FORA_DA_LEI", "a relacao temporal volta a falar a palavra do motor", MO,
     [('                "RELATION": REL_TEMPORAL, "CONTRADICTION_STATUS": "NO",',
       '                "RELATION": TEMPORAL_CHANGE, "CONTRADICTION_STATUS": "NO",')]),
    ("J12_078_COM_CONTRADICAO", "a mesma afirmacao numa casa passa a ter contradicao aberta", MO,
     [('"CONTRADICTION_STATUS": "NO" if len(por) == 1 else UNRESOLVED,',
       '"CONTRADICTION_STATUS": UNRESOLVED,')]),
]


def correr(raiz: Path):
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PATH": "/usr/bin:/bin",
           "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
           "http_proxy": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9", "NO_PROXY": ""}
    p = subprocess.run([sys.executable, "-m", "unittest", *TESTES], cwd=raiz, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=900)
    fim = [l for l in p.stderr.strip().splitlines() if l.strip()]
    return p.returncode, (fim[-1] if fim else "")


def main():
    res = {"DATASET": "MUTACAO-JUNCAO-LOTE6", "TESTES": TESTES, "MUTANTES": []}
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "arvore"
        shutil.copytree(RAIZ, tmp, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
        rc, linha = correr(tmp)
        res["SEM_MUTANTE"] = {"RC": rc, "SAIDA": linha}
        if rc != 0:
            print("o original ja falha:", linha)
            sys.exit(2)
        for nome, regra, alvo, trocas in MUTANTES:
            original = (tmp / alvo).read_text(encoding="utf-8")
            s = original
            for a, b in trocas:
                if s.count(a) != 1:
                    raise SystemExit("mutante %s: trecho aparece %d vezes: %r" % (nome, s.count(a), a[:70]))
                s = s.replace(a, b)
            (tmp / alvo).write_text(s, encoding="utf-8")
            try:
                ast.parse(s)
                compila = True
            except SyntaxError:
                compila = False
            rc, linha = correr(tmp)
            morto = rc != 0 and compila and "failures=" in linha
            res["MUTANTES"].append({"MUTANTE": nome, "REGRA": regra, "ALVO": alvo, "COMPILA": compila, "RC": rc,
                                    "SAIDA": linha, "RESULTADO": "MORTO" if morto else "SOBREVIVEU"})
            print("%-40s %s  %s" % (nome, "MORTO" if morto else "SOBREVIVEU", linha))
            (tmp / alvo).write_text(original, encoding="utf-8")
    res["MORTOS"] = sum(m["RESULTADO"] == "MORTO" for m in res["MUTANTES"])
    res["TOTAL"] = len(res["MUTANTES"])
    out = Path(__file__).with_name("MUTACAO-JUNCAO.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mortos %d de %d -> %s" % (res["MORTOS"], res["TOTAL"], out.name))
    sys.exit(0 if res["MORTOS"] == res["TOTAL"] else 1)


if __name__ == "__main__":
    main()
