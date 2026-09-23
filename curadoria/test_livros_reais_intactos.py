#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUARDA: nenhuma suite pode escrever nos livros REAIS da arvore.

Medido em 23/09: `test_supervisor` (depois de `test_fila_windows` ou de
`test_worker_pendurado`) mudava `curadoria/LIFECYCLE-QUEUE-V1.json` desta
worktree — a IT-T7-050 passava de WAITING_RETRY a IN_PROGRESS. O teste
redirecionava `F.FILA` para um ficheiro temporario, mas o supervisor lancava o
worker VERDADEIRO como outro processo, e esse processo le a fila do DISCO. Numa
worktree de servico, isto e escrever na fila viva e mandar um canario a rede.

    REDIRECIONAR NO PROCESSO NAO ISOLA O FILHO.

A guarda corre as suites que tocam supervisor/worker/fila num processo a parte
e compara o md5 dos livros reais antes e depois. Se algum mudou, repoe os bytes
e reprova, dizendo qual.

⚠️ NAO CORRER NA WORKTREE DO SERVICO VIVO: la o proprio bot escreve nestes
livros e a guarda reprovaria sem culpa. Com SUPERVISOR.lock presente, salta.
"""
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent

LIVROS = [AQUI / n for n in (
    "LIFECYCLE-QUEUE-V1.json", "LIFECYCLE-LEDGER-V1.json", "LIFECYCLE-EVIDENCE-V1.json",
    "SOURCE-ID-ALLOCATION-V1.json", "DISCOVERY-VISITED.json", "DECISOES-SEMANTICAS-V1.json",
)] + [RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"]

# Pares e conjuntos em que o vazamento foi MEDIDO (a ordem importa: o worker
# filho so chegava a escrever com a maquina ja «quente»).
CORRIDAS = [
    ["test_fila_windows", "test_supervisor"],
    ["test_worker_pendurado", "test_supervisor"],
    ["test_decisao_semantica", "test_fila_windows", "test_worker_pendurado",
     "test_supervisor", "test_discovery_sementes", "test_gatilho_ocioso",
     "test_worker_qualify"],
]


def _foto():
    return {p: (p.read_bytes() if p.exists() else None) for p in LIVROS}


def _md5(b):
    return None if b is None else hashlib.md5(b).hexdigest()


class TestLivrosReaisIntactos(unittest.TestCase):

    def setUp(self):
        if (AQUI / "SUPERVISOR.lock").exists():
            self.skipTest("SUPERVISOR.lock presente: arvore de servico vivo")

    def test_suites_nao_escrevem_nos_livros_reais(self):
        for corrida in CORRIDAS:
            antes = _foto()
            tmps_antes = set(AQUI.glob("*.tmp"))
            r = subprocess.run([sys.executable, "-m", "unittest", *corrida],
                               cwd=str(AQUI), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=600)
            depois = _foto()
            # um worker real morto a meio da escrita atomica deixa um .tmp com a
            # fila inteira dentro (medido: tmpwc_7s330.tmp, 303 KB, 23/09)
            tmps_novos = sorted(set(AQUI.glob("*.tmp")) - tmps_antes)
            for t in tmps_novos:
                t.unlink(missing_ok=True)
            mudados = [p.name for p in LIVROS if _md5(antes[p]) != _md5(depois[p])]
            for p in LIVROS:                      # repor antes de reprovar
                if _md5(antes[p]) != _md5(depois[p]):
                    if antes[p] is None:
                        p.unlink(missing_ok=True)
                    else:
                        p.write_bytes(antes[p])
            # a corrida tem de ter corrido — «limpo» sem testes e verde vazio
            self.assertRegex(r.stderr, r"Ran [1-9]\d* tests?",
                             "a corrida %s nao correu testes:\n%s" % (corrida, r.stderr[-800:]))
            self.assertEqual([t.name for t in tmps_novos], [],
                             "a corrida %s deixou ficheiros soltos" % corrida)
            self.assertEqual(mudados, [],
                             "a corrida %s escreveu nos livros reais: %s" % (corrida, mudados))


if __name__ == "__main__":
    unittest.main(verbosity=2)
