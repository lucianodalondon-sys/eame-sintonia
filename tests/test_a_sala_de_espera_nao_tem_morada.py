#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS GUARDAS DA MEDIÇÃO DA SALA DE ESPERA.

A medição de valor vive em `provas/a_sala_de_espera_nao_tem_morada.py`, contra
PostgreSQL real. Aqui ficam as guardas das duas lições que ela custou — as
duas por eu ter lido TEXTO onde a pergunta era de ESTRUTURA.
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
import _gavetas                    # noqa: E402,F401
import admissao                    # noqa: E402

MEDICAO = os.path.join(RAIZ, "provas", "a_sala_de_espera_nao_tem_morada.py")
ORQ = os.path.join(RAIZ, "orquestrador", "orquestrador.py")


def _fonte(caminho):
    return io.open(caminho, encoding="utf-8").read()


class OContratoREADYNaoMudou(unittest.TestCase):
    """Os 11 campos da COL-LAW-043, e um dono só."""

    CAMPOS = ("ESTADO", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO", "TEXTO", "SOURCE_ID",
              "SOURCE_LOCATION", "FACT_LOCATION", "FACT_TIME",
              "CAPTURED_AT", "CORRIDA", "ADMITIDO_POR")

    def _unidade(self):
        item = {"id": "g-1", "texto": "Ensaio de campo com DOI",
                "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
        d = admissao.decidir(item, "T7", corrida="guarda")
        return admissao.pronto_para_inteligencia(item, d)

    def test_os_onze_campos_estao_la_e_na_ordem(self):
        self.assertEqual(self.CAMPOS, tuple(self._unidade()))

    def test_nao_ha_READY_sem_SIM_na_porta(self):
        item = {"id": "g-2"}
        d = admissao.decidir(item, "T7", corrida="guarda")
        if d.resultado == admissao.SIM:
            self.skipTest("a porta aceitou; este caso precisa de um NAO")
        with self.assertRaises(ValueError):
            admissao.pronto_para_inteligencia(item, d)


class MencionarNaoEImplementar(unittest.TestCase):
    """⚠️ A PRIMEIRA LIÇÃO, E ELA CUSTOU UMA ACUSAÇÃO FALSA.

    A medição procurava a string `PRONTO_PARA_INTELIGENCIA` nos ficheiros e
    concluiu que `orquestrador/orquestrador.py` era um SEGUNDO construtor do
    registo READY. Não é: ele escreve aquele texto como ESTADO de um recibo, e
    CHAMA o dono. Chamar não é construir.

        MENCIONAR UM CONTRATO NÃO É IMPLEMENTÁ-LO.
        E A DIFERENÇA SÓ SE VÊ NA ESTRUTURA, NUNCA NO TEXTO.
    """

    def test_o_orquestrador_menciona_o_estado_e_nao_constroi_a_unidade(self):
        s = _fonte(ORQ)
        self.assertIn("PRONTO_PARA_INTELIGENCIA", s,
                      "o orquestrador deixou de nomear o estado")
        arv = ast.parse(s)
        constroi = False
        for no in ast.walk(arv):
            if isinstance(no, ast.Dict):
                chaves = {k.value for k in no.keys
                          if isinstance(k, ast.Constant)
                          and isinstance(k.value, str)}
                if set(OContratoREADYNaoMudou.CAMPOS) <= chaves:
                    constroi = True
        self.assertFalse(constroi,
                         "nasceu um segundo construtor do registo READY")

    def test_e_a_medicao_le_por_AST_e_nao_por_texto(self):
        s = _fonte(MEDICAO)
        self.assertIn("import ast", s)
        self.assertIn("ast.Dict", s,
                      "a medicao voltou a procurar a palavra em vez da forma")


class DestinoVazioNaoEDestinoSemDono(unittest.TestCase):
    """⚠️ A SEGUNDA LIÇÃO, E ELA MUDOU A DECISÃO QUE EU IA APRESENTAR.

    Eu ia declarar que a morada declarada no mapa «não tem escritor». TEM: o
    orquestrador decide, escreve o livro da porta, chama o dono do READY por
    cada SIM e grava o ficheiro da corrida. A pasta não existe porque nenhuma
    corrida daquele caminho produziu aceites.

        DESTINO VAZIO != DESTINO SEM DONO.
    """

    def test_o_escritor_da_morada_declarada_MUDOU_DE_CASA(self):
        """⚠️ ESTE TESTE MUDOU DE LADO, E ELE PROPRIO EXPLICA PORQUE.

        Quando foi escrito, ele guardava um facto verdadeiro: o orquestrador
        decidia, admitia e GRAVAVA o ficheiro da corrida. Era essa medicao que
        mostrava que a morada tinha dono — `DESTINO VAZIO != DESTINO SEM DONO`.

        `C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1` nao lhe tirou a razao:
        mudou a escrita de casa. A COL-LAW-012 separa control plane de data
        plane, e a escrita estava do lado errado.

            UM TESTE QUE SO ESTA CERTO ENQUANTO NADA AVANCA
            E UM TESTE QUE MEDE O PRIMEIRO DIA.

        O que ele guarda agora e o mesmo facto, no dono certo: o caminho que
        produz READY continua inteiro — decide, admite, e POUSA.
        """
        s = _fonte(ORQ)
        for pedaco in ("adm.pronto_para_inteligencia(x, d)", "adm.escrever(",
                       "espera.pousar("):
            with self.subTest(pedaco=pedaco):
                self.assertIn(pedaco, s,
                              "o caminho que produz READY perdeu uma peca")
        self.assertNotIn(".write_text(", s,
                         "a escrita voltou para o control plane")
        dono = _fonte(os.path.join(RAIZ, "admissao", "sala_de_espera.py"))
        self.assertIn("PRONTO-PARA-INTELIGENCIA", dono,
                      "a morada perdeu o dono")

    def test_e_a_medicao_diz_isso_e_nao_o_contrario(self):
        s = _fonte(MEDICAO)
        self.assertIn("DESTINO VAZIO != DESTINO SEM DONO", s)
        self.assertNotIn("S5_e_ninguem_escreve_nela", s,
                         "a medicao voltou a afirmar que ninguem escreve")
        # A medicao continua a valer como HISTORIA: ela e o retrato do dia em
        # que a decisao foi posta. Nao se reescreve um retrato para ele
        # parecer a fotografia de hoje.
        self.assertIn("A DECISAO QUE FALTA", s)


class AMedicaoNaoFechaNada(unittest.TestCase):
    """Ela mede e para. Fechar antes da decisão seria decidir em silêncio."""

    def test_nao_cria_tabela_nem_migration(self):
        s = _fonte(MEDICAO).lower()
        for proibido in ("create table", "alter table", "insert into"):
            self.assertNotIn(proibido, s,
                             "a medicao passou a escrever esquema: %s"
                             % proibido)

    def test_nenhuma_migration_deu_MORADA_a_sala_de_espera(self):
        """⚠️ ISTO EXIGIA QUE NÃO EXISTISSE UMA MIGRATION `029`, E REPROVOU.

        O número seguinte era, na altura, um bom atalho para «ninguém escolheu
        a morada por baixo». Deixou de o ser no dia em que a `029` nasceu para
        outra coisa — a linhagem material da derivação, que nada tem a ver com
        a Sala de Espera.

            UM NÚMERO DE MIGRATION NÃO É UMA PROPRIEDADE.
            PRENDER A GUARDA AO NÚMERO SEGUINTE FAZ O VIZINHO REPROVAR.

        O que ela protege de verdade é que **nenhuma** migration — seja qual
        for o número — dê casa em SQL à Sala de Espera ou ao READY. A decisão
        (`ADR-SALA-DE-ESPERA-V1`) diz filesystem, e continua a dizer.
        """
        import re
        pasta = os.path.join(RAIZ, "supabase", "migrations")
        proibidas = ("waiting_room", "sala_de_espera", "ready",
                     "pronto_para_inteligencia", "unidade_pronta")
        # ⚠️ E O QUE SE OLHA É O NOME DA TABELA CRIADA, e não a presença da
        # palavra no ficheiro. A primeira versão perguntava «há `create table`
        # e há a palavra `ready` algures?» — e acusou a `024`, que cria
        # `etapa_da_corrida` e menciona `ready` noutro contexto.
        #
        #     UMA GUARDA LARGA DE MAIS ACUSA O VIZINHO.
        nomes_criados = []
        for f in sorted(os.listdir(pasta)):
            if not f.endswith(".sql"):
                continue
            with io.open(os.path.join(pasta, f), encoding="utf-8") as fh:
                sql = "\n".join(l for l in fh.read().lower().splitlines()
                                 if not l.strip().startswith("--"))
            for nome in re.findall(
                    r"create table\s+(?:if not exists\s+)?(?:public\.)?(\w+)",
                    sql):
                nomes_criados.append((f, nome))
        achados = ["%s: %s" % (f, nome) for f, nome in nomes_criados
                   if any(pr in nome for pr in proibidas)]
        self.assertEqual([], achados,
                         "a morada foi escolhida em SQL sem a decisao mudar: %s"
                         % achados)
        self.assertTrue(nomes_criados, "a varredura nao encontrou tabela nenhuma")

    def test_a_medicao_apresenta_as_DUAS_saidas(self):
        s = _fonte(MEDICAO)
        self.assertIn("(A)", s)
        self.assertIn("(B)", s)
        self.assertIn("DECISAO DE ARQUITETURA", s)


class NenhumCasoSeAutoAprova(unittest.TestCase):
    """⚠️ DOIS MUTANTES SOBREVIVERAM AQUI, E OS DOIS SÃO O MESMO.

    Trocar a condição de um caso por `True`, ou por `True or <a condição>`,
    não muda nada: o caso continua a dizer PASS, e o mundo medido continua
    igual. Nada reprova, porque a resposta certa já era «sim».

        UM CASO QUE PASSA MESMO SEM COMPARAR NADA
        NÃO É UMA MEDIÇÃO: É UMA AFIRMAÇÃO.

    Esta guarda não confere o VALOR de cada caso — confere que cada um ainda
    faz uma pergunta. É finita, e morde as duas formas do defeito.
    """

    def _condicoes(self):
        arv = ast.parse(_fonte(MEDICAO))
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
        self.assertGreaterEqual(len(self._condicoes()), 10)

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


class ALeiNaoEscolheAMorada(unittest.TestCase):
    """É por isso que a decisão não se lê num contrato: não há contrato."""

    def test_a_lei_lista_ficheiro_e_banco_como_armazenamento(self):
        b = _fonte(os.path.join(RAIZ, "BIBLIA-CANONICA-DA-COLETA.md"))
        i = b.find("COL-LAW-044")
        trecho = b[i:i + 600]
        self.assertIn("data/samples", trecho)
        self.assertIn("Supabase", trecho)

    def test_e_a_lei_do_READY_cala_se_sobre_onde_a_unidade_pousa(self):
        b = _fonte(os.path.join(RAIZ, "BIBLIA-CANONICA-DA-COLETA.md"))
        trecho = b[b.find("COL-LAW-043"):b.find("COL-LAW-044")]
        self.assertNotIn("PRONTO-PARA-INTELIGENCIA", trecho)
        self.assertIn("ADMITIDO_POR", trecho,
                      "a lei deixou de declarar os 11 campos")


if __name__ == "__main__":
    unittest.main()
