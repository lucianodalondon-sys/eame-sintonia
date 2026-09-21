#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A GUARDA PERMANENTE DO ISOLAMENTO — a suite nao escreve na arvore real.

Medido (PROVAS-P1, DEFEITO 2): um unico ficheiro de testes sem redirecionar
F.FILA moveu 10 tarefas REAIS de PENDING para BLOCKED numa lane, avancou
PROXIMO_ID noutra, e apagou o lock de um supervisor vivo numa terceira — tudo
com `git status` limpo ou quase. O defeito escondeu-se porque ninguem media
os bytes da fila antes e depois da suite.

    GIT STATUS VAZIO NAO E PROVA. O SHA256 DA FILA MANDA.

Este modulo mede em dois tempos:

1. DINAMICO — a impressao (sha256) dos ficheiros reais e tirada AQUI, no
   import. O `unittest discover` importa todos os modulos antes de correr o
   primeiro teste, e este modulo chama-se `test_zz_...` para ser o ULTIMO a
   correr: o que ele compara e o estado da arvore do principio ao fim da
   suite inteira. Se qualquer teste, de qualquer ficheiro, escreveu na fila,
   no livro, na evidencia, nos contratos, nos lotes ou no lock reais, este
   teste reprova e diz qual ficheiro mudou.

   Corrido sozinho (`py -m unittest test_zz_guarda_isolamento`) o dinamico
   compara o ficheiro consigo proprio e passa por vazio — declarado no nome
   do teste e na mensagem; a prova e a suite completa.

2. ESTATICO — le o texto de cada `test_*.py` desta pasta. Quem chama o que
   escreve na fila (`F.enfileirar`, `F.proxima`, `W.executar_uma`...) tem de
   atribuir `F.FILA =`; quem chama `LC.registar` tem de atribuir `LC.LIVRO =`;
   quem chama `uma_volta_sup` tem de redirecionar ESTADO, DIARIO e F.FILA;
   quem chama `_adquirir_lock` tem de redirecionar LOCK. E todos eles tem de
   usar `TemporaryDirectory`. Um ficheiro novo que esqueca o molde reprova
   aqui antes de contaminar o que quer que seja.

Molde do isolamento: test_ready_split.py:44-48. Nao ha um segundo.
"""
from __future__ import annotations

import hashlib
import re
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

# Os ficheiros reais que a suite NUNCA pode alterar. Escritos por extenso: se
# um modulo deixou F.FILA a apontar para uma pasta descartavel, ler F.FILA
# aqui mediria o ficheiro errado.
FICHEIROS_REAIS = [
    "LIFECYCLE-QUEUE-V1.json",
    "LIFECYCLE-LEDGER-V1.json",
    "LIFECYCLE-EVIDENCE-V1.json",
    "italy_contracts_curator.json",
    "READY-BATCHES-V1.json",
    "DISCOVERY-SIGNAL-V1.json",
    "SUPERVISOR.lock",
    "PARAR.flag",
    # BRIDGE-FEEDER: a porta, o ledger da ponte e a memoria da descoberta.
    # A porta vive noutra gaveta (candidatas/), por isso o caminho relativo.
    "../candidatas/FONTES-CANDIDATAS.json",
    "BRIDGE-LEDGER-V1.json",
    "DISCOVERY-VISITED.json",
    "DISCOVERY-PROOF-V1.json",
    # RECONCILIACAO-V1: o censo dos tres livros e os livros que ele le.
    "RECONCILIACAO-V1.json",
    "LISTAGENS-PROVADAS-V1.json",
    "SOURCE-ID-ALLOCATION-V1.json",
    "CANDIDATE-TO-SOURCE-MATCH-V1.json",
]


def _impressao(p: Path) -> str:
    if not p.exists():
        return "AUSENTE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def impressoes() -> dict:
    return {n: _impressao(AQUI / n) for n in FICHEIROS_REAIS}


# Tirada no IMPORT — antes de qualquer teste da suite correr.
IMPRESSAO_NO_IMPORT = impressoes()


# ---------------------------------------------------------------------------
# Regras estaticas: (o que o ficheiro usa) -> (o que o ficheiro tem de ter)
# ---------------------------------------------------------------------------
ESCREVE_NA_FILA = re.compile(
    r"F\.(enfileirar|proxima|_gravar|adiar|concluir|bloquear|recuperar_orfas)\("
    r"|W\.(correr|executar_uma)\("
    r"|CC\.uma_volta\(")
ESCREVE_NO_LIVRO = re.compile(r"LC\.registar\(")
USA_O_LOCK = re.compile(r"_adquirir_lock\(")
USA_A_VOLTA_DO_SUPERVISOR = re.compile(r"uma_volta_sup\(")
USA_O_ESTADO_DO_SERVICO = re.compile(r"ler_estado_servico\(")

REDIRECIONA_FILA = re.compile(r"F\.FILA\s*=[^=]")
REDIRECIONA_LIVRO = re.compile(r"LC\.LIVRO\s*=[^=]")
REDIRECIONA_LOCK = re.compile(r"(S|SUP)\.LOCK\s*=[^=]")
REDIRECIONA_ESTADO = re.compile(r"(S|SUP)\.ESTADO\s*(,\s*(S|SUP)\.\w+\s*)*=[^=]")
REDIRECIONA_DIARIO = re.compile(r"(S|SUP)\.DIARIO\s*=[^=]|(S|SUP)\.ESTADO\s*,\s*(S|SUP)\.DIARIO\s*=[^=]"
                                r"|(S|SUP)\.ESTADO\s*,\s*(S|SUP)\.PARAR\s*,\s*(S|SUP)\.DIARIO\s*=[^=]")
USA_PASTA_DESCARTAVEL = re.compile(r"TemporaryDirectory\(")

# BRIDGE-FEEDER (G4): a porta, a ponte e a descoberta. O test_discovery.py do
# bridge chamava FN.registar() contra a porta REAL e D._marcar_visitado()
# contra o DISCOVERY-VISITED real, e 'limpava' reescrevendo os ficheiros.
ESCREVE_NA_PORTA = re.compile(
    r"FN\.(registar|gravar)\(|P\.processar\(|D\.(descobrir|_descobrir_familia)\(")
ESCREVE_NOS_VISITADOS = re.compile(
    r"D\.(_marcar_visitado|_marcar_rejeitado|_gravar_visitados|descobrir|"
    r"_descobrir_familia)\(")
CORRE_A_PONTE = re.compile(r"P\.processar\(")

# RECONCILIACAO-V1: quem aplica a reconciliacao escreve no livro (por LC.registar)
# e no censo (R.SAIDA). Os dois tem de apontar para a pasta descartavel.
APLICA_A_RECONCILIACAO = re.compile(r"R\.(aplicar|main)\(")
REDIRECIONA_SAIDA_DA_RECONCILIACAO = re.compile(r"R\.SAIDA\s*=[^=]")

REDIRECIONA_PORTA = re.compile(r"FN\.FILA\s*=[^=]")
REDIRECIONA_VISITADOS = re.compile(r"D\.VISITADOS_JSON\s*=[^=]")
REDIRECIONA_LEDGER_DA_PONTE = re.compile(r"P\.LEDGER\s*=[^=]")

REGRAS = [
    ("aplica a reconciliacao -> LC.LIVRO e R.SAIDA redirecionados",
     APLICA_A_RECONCILIACAO, [("LC.LIVRO =", REDIRECIONA_LIVRO),
                              ("R.SAIDA =", REDIRECIONA_SAIDA_DA_RECONCILIACAO)]),
    ("escreve na porta -> FN.FILA redirecionada",
     ESCREVE_NA_PORTA, [("FN.FILA =", REDIRECIONA_PORTA)]),
    ("escreve nos visitados -> D.VISITADOS_JSON redirecionado",
     ESCREVE_NOS_VISITADOS, [("D.VISITADOS_JSON =", REDIRECIONA_VISITADOS)]),
    ("corre a ponte -> P.LEDGER, F.FILA e LC.LIVRO redirecionados",
     CORRE_A_PONTE, [("P.LEDGER =", REDIRECIONA_LEDGER_DA_PONTE),
                     ("F.FILA =", REDIRECIONA_FILA),
                     ("LC.LIVRO =", REDIRECIONA_LIVRO)]),
    # (nome, gatilho, exigencias)
    ("escreve na fila -> F.FILA redirecionada",
     ESCREVE_NA_FILA, [("F.FILA =", REDIRECIONA_FILA)]),
    ("escreve no livro -> LC.LIVRO redirecionado",
     ESCREVE_NO_LIVRO, [("LC.LIVRO =", REDIRECIONA_LIVRO)]),
    ("usa o lock -> LOCK redirecionado",
     USA_O_LOCK, [("S.LOCK =", REDIRECIONA_LOCK)]),
    ("da voltas ao supervisor -> ESTADO, DIARIO e F.FILA redirecionados",
     USA_A_VOLTA_DO_SUPERVISOR, [("S.ESTADO =", REDIRECIONA_ESTADO),
                                 ("S.DIARIO =", REDIRECIONA_DIARIO),
                                 ("F.FILA =", REDIRECIONA_FILA)]),
    ("le o estado do servico -> ESTADO redirecionado",
     USA_O_ESTADO_DO_SERVICO, [("S.ESTADO =", REDIRECIONA_ESTADO)]),
]


def ficheiros_de_teste() -> list[Path]:
    return sorted(p for p in AQUI.glob("test_*.py") if p.name != Path(__file__).name)


def faltas_de(p: Path) -> list[str]:
    texto = p.read_text(encoding="utf-8", errors="replace")
    faltas = []
    disparou = False
    for nome, gatilho, exigencias in REGRAS:
        if not gatilho.search(texto):
            continue
        disparou = True
        for rotulo, padrao in exigencias:
            if not padrao.search(texto):
                faltas.append("%s: falta `%s` (%s)" % (p.name, rotulo, nome))
    if disparou and not USA_PASTA_DESCARTAVEL.search(texto):
        faltas.append("%s: toca em estado e nao usa TemporaryDirectory" % p.name)
    return faltas


class AGuardaDoIsolamento(unittest.TestCase):

    def test_1_estatico_todo_o_teste_que_toca_estado_redireciona(self):
        faltas = []
        for p in ficheiros_de_teste():
            faltas.extend(faltas_de(p))
        self.assertEqual(faltas, [], "\n".join(
            ["ficheiros de teste que tocam em estado sem o redirecionar "
             "(molde: test_ready_split.py:44-48):"] + faltas))

    def test_2_estatico_a_regra_apanha_o_defeito_original(self):
        """A regra tem de reprovar o test_supervisor.py de antes: enfileirava
        na fila real e apagava o lock real sem redirecionar nada."""
        antigo = (
            "import fila as F\nimport supervisor as S\n"
            "class TestLock(unittest.TestCase):\n"
            "    def setUp(self):\n        S.LOCK.unlink(missing_ok=True)\n"
            "    def test_a(self):\n        fd = S._adquirir_lock()\n"
            "class TestUmaVoltaSup(unittest.TestCase):\n"
            "    def test_b(self):\n        F.enfileirar('X', F.CANARY)\n"
            "        S.uma_volta_sup({}, None)\n")
        falso = AQUI / "_guarda_amostra_nao_e_teste.py"
        try:
            falso.write_text(antigo, encoding="utf-8")
            faltas = faltas_de(falso)
        finally:
            falso.unlink(missing_ok=True)
        self.assertTrue(faltas, "a regra deixou passar o defeito original")
        self.assertTrue(any("F.FILA" in f for f in faltas), faltas)
        self.assertTrue(any("S.LOCK" in f for f in faltas), faltas)
        self.assertTrue(any("TemporaryDirectory" in f for f in faltas), faltas)

    def test_2b_estatico_a_regra_apanha_o_test_discovery_do_bridge(self):
        """O test_discovery.py de 63b71421 registava na porta real e marcava
        visitados reais sem redirecionar nada — a regra tem de o apanhar."""
        antigo = (
            "import fonte_nova as FN\nimport descobrir as D\n"
            "class TestDedup(unittest.TestCase):\n"
            "    def test_a(self):\n"
            "        FN.registar(tipo='ORGANIZACAO', pais='IT', nome='x', url='u',\n"
            "                    para_que='t', quem_viu='TEST_')\n"
            "        D._marcar_rejeitado('u', 'TESTE', D._ler_visitados())\n")
        falso = AQUI / "_guarda_amostra_nao_e_teste.py"
        try:
            falso.write_text(antigo, encoding="utf-8")
            faltas = faltas_de(falso)
        finally:
            falso.unlink(missing_ok=True)
        self.assertTrue(faltas, "a regra deixou passar o test_discovery do bridge")
        self.assertTrue(any("FN.FILA" in f for f in faltas), faltas)
        self.assertTrue(any("D.VISITADOS_JSON" in f for f in faltas), faltas)
        self.assertTrue(any("TemporaryDirectory" in f for f in faltas), faltas)

    def test_2c_estatico_a_regra_apanha_uma_ponte_sem_ledger_redirecionado(self):
        antigo = (
            "import fila as F\nimport lifecycle as LC\nimport fonte_nova as FN\n"
            "import ponte_candidatas as P\n"
            "class T(unittest.TestCase):\n"
            "    def setUp(self):\n"
            "        self.tmp = tempfile.TemporaryDirectory()\n"
            "        F.FILA = Path(self.tmp.name) / 'q.json'\n"
            "        LC.LIVRO = Path(self.tmp.name) / 'l.json'\n"
            "        FN.FILA = Path(self.tmp.name) / 'p.json'\n"
            "    def test_a(self):\n        P.processar()\n")
        falso = AQUI / "_guarda_amostra_nao_e_teste.py"
        try:
            falso.write_text(antigo, encoding="utf-8")
            faltas = faltas_de(falso)
        finally:
            falso.unlink(missing_ok=True)
        self.assertEqual(len(faltas), 1, faltas)
        self.assertIn("P.LEDGER", faltas[0])

    def test_2d_estatico_a_regra_apanha_uma_reconciliacao_sem_saida_redirecionada(self):
        antigo = (
            "import lifecycle as LC" + chr(10) + "import reconciliar_livros as R" + chr(10) +
            "class T(unittest.TestCase):" + chr(10) +
            "    def setUp(self):" + chr(10) +
            "        self.tmp = tempfile.TemporaryDirectory()" + chr(10) +
            "        LC.LIVRO = Path(self.tmp.name) / 'l.json'" + chr(10) +
            "    def test_a(self):" + chr(10) + "        R.aplicar({}, {})" + chr(10))
        falso = AQUI / "_guarda_amostra_nao_e_teste.py"
        try:
            falso.write_text(antigo, encoding="utf-8")
            faltas = faltas_de(falso)
        finally:
            falso.unlink(missing_ok=True)
        self.assertEqual(len(faltas), 1, faltas)
        self.assertIn("R.SAIDA", faltas[0])

    def test_3_dinamico_os_ficheiros_reais_nao_mudaram_durante_a_suite(self):
        """Compara a arvore real de agora com a impressao tirada no import.
        So prova alguma coisa na suite completa: sozinho, compara o ficheiro
        consigo proprio."""
        agora = impressoes()
        mudaram = [n for n in FICHEIROS_REAIS
                   if IMPRESSAO_NO_IMPORT[n] != agora[n]]
        self.assertEqual(mudaram, [], (
            "ficheiros REAIS alterados durante a suite: %s — ou um teste "
            "escreveu fora da pasta descartavel, ou ha um servico vivo a "
            "escrever nesta arvore; em ambos os casos a medicao nao vale"
            % mudaram))


if __name__ == "__main__":
    unittest.main(verbosity=2)
