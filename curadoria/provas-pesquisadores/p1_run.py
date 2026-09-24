import sys, os, unittest, json
raiz = sys.argv[1]; out = sys.argv[2]
files = ["curadoria/test_discovery.py","curadoria/test_livros_reais_intactos.py","curadoria/test_ponte_cadeia.py",
 "curadoria/test_ponte_candidatas.py","curadoria/test_reconciliar_livros.py","curadoria/test_zz_guarda_isolamento.py",
 "tests/test_fila_italia_decisoes.py","tests/test_medir_cutover.py","tests/test_portao.py","tests/test_porta_de_candidatas.py"]
os.chdir(raiz)
res = {}
class R(unittest.TextTestResult):
    def addSuccess(s,t): res[t.id()]="OK"; super().addSuccess(t)
    def addFailure(s,t,e): res[t.id()]="FAIL"; super().addFailure(t,e)
    def addError(s,t,e): res[t.id()]="ERROR"; super().addError(t,e)
    def addSkip(s,t,r): res[t.id()]="SKIP"; super().addSkip(t,r)
for f in files:
    d, b = os.path.split(f)
    sys.path.insert(0, os.path.join(raiz, d))
    try:
        suite = unittest.defaultTestLoader.discover(os.path.join(raiz,d), pattern=b, top_level_dir=os.path.join(raiz,d))
        unittest.TextTestRunner(resultclass=R, verbosity=0, stream=open(os.devnull,"w")).run(suite)
    except Exception as ex:
        res[f+"::LOAD"]="ERROR "+type(ex).__name__
json.dump(res, open(out,"w"), indent=0)
from collections import Counter; print(raiz, Counter(v.split()[0] for v in res.values()))
