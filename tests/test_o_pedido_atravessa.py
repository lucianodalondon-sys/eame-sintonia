#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DA PROVA DO PEDIDO — ela tem de começar no botão, e não no meio.

A medição de valor vive em `provas/o_pedido_atravessa.py`, contra PostgreSQL
real, filesystem descartável e o executor REAL a ir à fonte real. Aqui ficam as
guardas que não precisam de rede nem de banco.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta")):
    if p not in sys.path:
        sys.path.insert(0, p)
import _gavetas                      # noqa: E402,F401
import telemetria as tel             # noqa: E402

PROVA = os.path.join(RAIZ, "provas", "o_pedido_atravessa.py")
ORQ = os.path.join(RAIZ, "orquestrador", "orquestrador.py")


def _fonte(caminho):
    return io.open(caminho, encoding="utf-8").read()


def _chamadas(caminho):
    """Os nomes chamados no ficheiro, lidos por AST e não por texto."""
    fora = set()
    for no in ast.walk(ast.parse(_fonte(caminho))):
        if isinstance(no, ast.Call):
            n = getattr(no.func, "attr", None) or getattr(no.func, "id", None)
            if n:
                fora.add(n)
    return fora


class AProvaComecaNoBotao(unittest.TestCase):
    """⚠️ UMA PROVA QUE COMEÇA PELO MEIO NÃO PROVA A ESTRADA.

    Ela prova o pedaço por onde começou. Esta guarda é o RT1 da missão: se a
    prova passar a chamar o downstream directamente, deixa de responder à
    pergunta e ninguém repara — o veredito continua a sair.
    """

    def test_a_prova_aperta_o_botao_canonico(self):
        self.assertIn("correr", _chamadas(PROVA))
        self.assertIn("orq.correr(p", _fonte(PROVA),
                      "a prova deixou de entrar pelo orquestrador")

    def test_e_NAO_chama_o_downstream_a_mao(self):
        proibidas = {"atravessar", "admitir", "pronto_para_inteligencia",
                     "pousar", "preservar", "estruturar", "levar_a_espera"}
        self.assertEqual(set(), proibidas & _chamadas(PROVA),
                         "a prova passou a comecar pelo meio")

    def test_e_nao_abre_a_corrida_a_mao(self):
        s = _fonte(PROVA).lower()
        self.assertNotIn("insert into public.collection_run", s)
        self.assertNotIn("insert into public.raw_asset", s)


class OPrimeiroBuracoEOPrimeiro(unittest.TestCase):
    """⚠️ MEDIDO: a primeira versão dizia `ADMISSION -> DERIVED`.

    Ela guardava a última etapa observada da lista INTEIRA — e como a ADMISSION
    corre depois de DERIVED faltar, a aresta saía ao contrário, mandando
    procurar o defeito a jusante de onde ele está.

        O PRIMEIRO BURACO É O QUE EXPLICA OS SEGUINTES.
    """

    def _primeiro_buraco(self, observadas):
        estrada = ("REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW",
                   "STORAGE", "DERIVED", "STRUCTURED", "ADMISSION", "READY",
                   "WAITING_ROOM")
        perdido = ultima = None
        for e in estrada:
            if perdido is None:
                if e in observadas:
                    ultima = e
                else:
                    perdido = e
        return ultima, perdido

    def test_o_buraco_do_meio_nao_e_mascarado_pelo_que_corre_depois(self):
        observadas = {"REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW",
                      "STORAGE", "ADMISSION"}
        self.assertEqual(("STORAGE", "DERIVED"),
                         self._primeiro_buraco(observadas))

    def test_estrada_inteira_nao_tem_buraco(self):
        todas = {"REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW",
                 "STORAGE", "DERIVED", "STRUCTURED", "ADMISSION", "READY",
                 "WAITING_ROOM"}
        self.assertEqual(("WAITING_ROOM", None), self._primeiro_buraco(todas))

    def test_a_prova_usa_esta_regra_e_nao_outra(self):
        s = _fonte(PROVA)
        self.assertIn("if perdido is None:", s,
                      "a prova voltou a percorrer a lista inteira")
        self.assertIn("ETAPAS_DEPOIS_DO_BURACO", s,
                      "o que corre depois do buraco deixou de ser dito")


class ACorridaCanonicaDeixaRasto(unittest.TestCase):
    """⚠️ UM PARÂMETRO OPCIONAL QUE NINGUÉM CONSEGUE PASSAR NÃO É OPCIONAL.

    MEDIDO: um pedido real atravessou até à ADMISSION, escreveu quatro linhas
    em `raw_asset` — e `etapa_da_corrida` ficou com ZERO. A etapa RAW já sabia
    falar; quem a chamava é que não lhe dava onde.
    """

    def test_a_fronteira_do_orquestrador_passa_o_banco_do_rastro(self):
        arv = ast.parse(_fonte(ORQ))
        for no in ast.walk(arv):
            if not isinstance(no, ast.Call):
                continue
            if getattr(no.func, "attr", None) != "receber":
                continue
            nomes = {kw.arg for kw in no.keywords}
            self.assertIn("banco_do_rastro", nomes,
                          "a corrida canonica voltou a correr sem rasto")
            return
        self.fail("a fronteira deixou de chamar `ing.receber`")

    def test_e_quem_a_chama_tem_por_onde_o_passar(self):
        arv = ast.parse(_fonte(ORQ))
        for no in ast.walk(arv):
            if isinstance(no, ast.FunctionDef) and no.name in ("correr",
                                                               "pela_entrada"):
                nomes = [a.arg for a in no.args.args + no.args.kwonlyargs]
                with self.subTest(funcao=no.name):
                    self.assertIn("banco_do_rastro", nomes)

    def test_a_etapa_RAW_ja_estava_no_vocabulario(self):
        self.assertIn("RAW", tel.ETAPAS_DA_COLETA)


class NenhumCasoSeAutoAprova(unittest.TestCase):
    """⚠️ CINCO MUTANTES SOBREVIVERAM AQUI, E SAO TODOS O MESMO.

    Trocar a condicao de um caso por `True`, ou por `True or <a condicao>`,
    nao muda nada: o caso continua a dizer PASS, e o mundo medido continua
    igual. Nada reprova, porque a resposta certa ja era «sim».

        UM CASO QUE PASSA MESMO SEM COMPARAR NADA
        NAO E UMA MEDICAO: E UMA AFIRMACAO.

    ⚠️ E ESTA GUARDA JA EXISTIA, escrita em §74.5 para outra prova, e eu nao
    a apliquei a esta. UMA LICAO ESCRITA E NAO APLICADA E O MESMO QUE UMA
    LICAO NAO ESCRITA.
    """

    def _condicoes(self):
        arv = ast.parse(_fonte(PROVA))
        fora = []
        for no in ast.walk(arv):
            if not isinstance(no, ast.Call):
                continue
            if getattr(no.func, "id", None) != "caso" or len(no.args) < 2:
                continue
            nome = (no.args[0].value if isinstance(no.args[0], ast.Constant)
                    else "?")
            fora.append((nome, no.args[1], no.lineno))
        return fora

    def test_ha_casos_para_conferir(self):
        self.assertGreaterEqual(len(self._condicoes()), 12)

    def test_nenhuma_condicao_e_uma_constante(self):
        for nome, cond, linha in self._condicoes():
            with self.subTest(caso=nome):
                self.assertNotIsInstance(
                    cond, ast.Constant,
                    "o caso %s (linha %d) deixou de comparar" % (nome, linha))

    def test_nenhuma_condicao_comeca_por_uma_constante(self):
        """`True or <condicao>` passa sempre, e parece uma condicao."""
        for nome, cond, linha in self._condicoes():
            if not isinstance(cond, ast.BoolOp):
                continue
            with self.subTest(caso=nome):
                for valor in cond.values:
                    self.assertNotIsInstance(
                        valor, ast.Constant,
                        "o caso %s (linha %d) tem uma constante a curto-"
                        "circuitar a condicao" % (nome, linha))

    def test_nenhuma_condicao_e_sempre_verdadeira_por_disjuncao(self):
        """`x or True` passa sempre. `x or ""` e outra coisa.

        ⚠️ A PRIMEIRA VERSAO DESTA GUARDA ACUSOU QUATRO CASOS CERTOS.
        Ela proibia QUALQUER constante dentro de um `or`, e apanhou
        `(recusa.get("QUEM_RESOLVE") or "")` — um valor por omissao para nao
        rebentar em `None`. Isso nao curto-circuita nada: `""` e falso.

            UMA GUARDA QUE PROIBE A FORMA EM VEZ DO EFEITO
            RECUSA CODIGO CERTO JUNTO COM O DEFEITO.

        O que torna a condicao sempre verdadeira e uma constante VERDADEIRA.
        E so isso que se proibe.
        """
        for nome, cond, linha in self._condicoes():
            for dentro in ast.walk(cond):
                if not (isinstance(dentro, ast.BoolOp)
                        and isinstance(dentro.op, ast.Or)):
                    continue
                for v in dentro.values:
                    if not isinstance(v, ast.Constant):
                        continue
                    with self.subTest(caso=nome):
                        self.assertFalse(
                            bool(v.value),
                            "o caso %s (linha %d) tem uma constante VERDADEIRA"
                            " dentro de um `or`: passa sempre"
                            % (nome, linha))


class ONaoMedidoNaoEPassNoPortao(unittest.TestCase):
    """⚠️ MEDIDO: o ramo `NOT_MEASURED` podia devolver PASS sem ninguem ver.

    Ele so corre quando a medicao NUNCA correu — e como no repositorio o
    ficheiro existe, o mutante que o trocava por `PASS` sobrevivia. A guarda
    apaga o ficheiro num sitio descartavel e pergunta-lhe directamente.

        NOT_MEASURED != PASS.
    """

    def _portoes(self):
        import importlib.util as u
        sp = u.spec_from_file_location(
            "portoes", os.path.join(RAIZ, "provas",
                                    "os_portoes_da_collection.py"))
        m = u.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m

    def test_sem_medicao_o_portao_nao_diz_PASS(self):
        import shutil
        import tempfile
        m = self._portoes()
        alvo = os.path.join(m.RAIZ, "system-map", "data",
                            "pedido.observado.json")
        guardado = None
        if os.path.isfile(alvo):
            guardado = tempfile.mktemp(suffix=".json")
            shutil.copy(alvo, guardado)
            os.unlink(alvo)
        try:
            estado, porque = m.uma_historia_so()
            self.assertEqual("NOT_MEASURED", estado)
            self.assertIn("NOT_MEASURED != PASS", porque)
        finally:
            if guardado:
                shutil.copy(guardado, alvo)
                os.unlink(guardado)

    def test_e_uma_historia_partida_tambem_nao(self):
        m = self._portoes()
        estado, porque = m.uma_historia_so()
        if estado == "FAIL":
            self.assertIn("parou em", porque)


class OVereditoSaiSempre(unittest.TestCase):
    """Uma prova que não consegue dizer FAIL não está a aprovar: cala-se."""

    def test_a_prova_separa_MEDIDO_de_ESTRADA_INTEIRA(self):
        s = _fonte(PROVA)
        self.assertIn("PEDIDO_ATRAVESSA=", s)
        self.assertIn("CANONICAL_E2E=", s)
        self.assertIn("medido = all(ok for n, ok, _d in fora", s,
                      "o veredito da medicao voltou a depender do mundo"
                      " estar bom")

    def test_e_declara_o_ambiente_descartavel_em_vez_de_saltar(self):
        s = _fonte(PROVA)
        self.assertIn("SKIP != PASS", s)
        self.assertIn("NOT_MEASURED", s)

    def test_a_sala_da_prova_e_descartavel(self):
        s = _fonte(PROVA)
        self.assertIn("SALA_DESCARTAVEL", s)
        self.assertIn("ITALY_OPS_ROOT", s,
                      "a prova voltou a escrever o livro append-only da arvore")


if __name__ == "__main__":
    unittest.main()
