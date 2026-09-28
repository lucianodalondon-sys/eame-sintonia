# -*- coding: utf-8 -*-
"""L5-P3 · bateria de regressao: o que quebraria com a proposta instalada.

Corre os testes que tocam `leis/fato_local.py` / `leis/fato_do_texto.py` DUAS vezes —
uma com o codigo vivo, outra com `leis.fato_local.tempo_do_fato` trocado pela proposta
(monkeypatch em memoria, nenhum ficheiro alterado) — e compara teste a teste.

    py -3.12 provas/l5-p3/regressao.py
    py -3.12 provas/l5-p3/regressao.py --python <interprete com pytest>

O interprete precisa de pytest. Nesta maquina o `py -3.12` do runner NAO tem pytest;
o que tem e o do hermes-agent (medido em 28/09/2026), e e por isso que existe a opcao
`--python`. Dois verdes ao mesmo tempo nao se medem (regra da maquina partilhada): as
duas corridas sao sequenciais.
"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))

TESTES = [
    "tests/test_a_collection_preserva_o_fato.py", "tests/test_artefato_tempo_do_fato.py",
    "tests/test_boletim_do_campo.py", "tests/test_boletim_por_secao.py",
    "tests/test_c7_lugar_do_fato.py", "tests/test_comentarios_v1.py",
    "tests/test_conserto_regua.py", "tests/test_data_do_fato.py",
    "tests/test_estudo_chaves.py", "tests/test_extrator_evento_v2.py",
    "tests/test_extrator_lugar_v2.py", "tests/test_fato_do_texto.py",
    "tests/test_lugar_do_fato.py", "tests/test_metodo_puglia.py",
    "tests/test_periodo_e_chaves.py", "tests/test_social_bruto_leva_a_evidencia.py",
    "tests/test_voce_dal_campo.py",
]


# ── o coletor: escreve o resultado teste a teste ─────────────────────────────
class Coletor:
    def __init__(self, saida):
        self.saida, self.r = saida, {}

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
            antigo = self.r.get(report.nodeid)
            if antigo != "failed":
                self.r[report.nodeid] = report.outcome

    def pytest_sessionfinish(self, session, exitstatus):
        with open(self.saida, "w", encoding="utf-8") as f:
            json.dump({"EXIT": int(exitstatus), "TESTES": self.r}, f, ensure_ascii=False, indent=1)


def corre(saida, com_proposta):
    import importlib.util
    import pytest
    plugins = [Coletor(saida)]
    if com_proposta:
        spec = importlib.util.spec_from_file_location("plugin_proposta",
                                                      os.path.join(AQUI, "plugin_proposta.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        plugins.append(mod)
    return pytest.main(TESTES + ["-q", "--tb=no", "-p", "no:cacheprovider"], plugins=plugins)


def main(argv):
    if "--interno" in argv:
        os.chdir(RAIZ)
        return corre(argv[argv.index("--interno") + 1], "--com-proposta" in argv)
    py = argv[argv.index("--python") + 1] if "--python" in argv else sys.executable
    env = dict(os.environ, PYTHONPATH="C:/Users/London1/.sintonia-libs;" + RAIZ,
               PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    fora = {}
    for rotulo, extra in (("BASE", []), ("COM_PROPOSTA", ["--com-proposta"])):
        saida = os.path.join(AQUI, "_regressao_%s.json" % rotulo)
        print("== corrida %s ==" % rotulo, flush=True)
        subprocess.run([py, os.path.abspath(__file__), "--interno", saida] + extra,
                       cwd=RAIZ, env=env)
        with open(saida, encoding="utf-8") as f:
            fora[rotulo] = json.load(f)
    a, b = fora["BASE"]["TESTES"], fora["COM_PROPOSTA"]["TESTES"]
    quebra = sorted(k for k in a if a[k] == "passed" and b.get(k) != "passed")
    cura = sorted(k for k in a if a[k] != "passed" and b.get(k) == "passed")
    sumiu = sorted(set(a) - set(b))
    print("\nBASE           %d testes, %d passaram" % (len(a), sum(v == "passed" for v in a.values())))
    print("COM_PROPOSTA   %d testes, %d passaram" % (len(b), sum(v == "passed" for v in b.values())))
    print("REGRESSOES     %d" % len(quebra))
    for k in quebra:
        print("  - %s (%s)" % (k, b.get(k, "sumiu")))
    print("CURADOS        %d" % len(cura))
    for k in cura:
        print("  + %s" % k)
    if sumiu:
        print("SUMIRAM        %d: %s" % (len(sumiu), ", ".join(sumiu[:5])))
    with open(os.path.join(AQUI, "_regressao.json"), "w", encoding="utf-8") as f:
        json.dump({"BASE_PASSOU": sum(v == "passed" for v in a.values()), "BASE_TOTAL": len(a),
                   "PROPOSTA_PASSOU": sum(v == "passed" for v in b.values()), "PROPOSTA_TOTAL": len(b),
                   "REGRESSOES": quebra, "CURADOS": cura, "SUMIRAM": sumiu},
                  f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
