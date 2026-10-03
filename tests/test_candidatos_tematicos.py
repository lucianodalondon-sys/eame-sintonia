# -*- coding: utf-8 -*-
"""UM CANDIDATO DESENHADO DEPOIS DE VER O CORPUS E UMA RESPOSTA DECORADA.

Esta missao falha de quatro maneiras que nenhuma excecao denuncia:

    1. uma ficha le o caminho, e o caminho carrega o universo declarado;
    2. uma ficha alega treino independente que nao existe;
    3. um parametro fica solto, e afina-se depois de ver o resultado;
    4. mexer numa ficha nao muda o fingerprint, e o congelamento e teatro.

    A HIPOTESE VEM PRIMEIRO, E FICA ESCRITA. DEPOIS MEDE-SE.
"""
import copy
import importlib.util
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "cand_t", os.path.join(RAIZ, "provas", "candidatos_tematicos.py"))
c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c)


def _manifesto_no_disco():
    with open(os.path.join(RAIZ, c.MANIFESTO), encoding="utf-8") as f:
        return json.load(f)


def _boa():
    """Uma ficha valida, para mexer uma coisa de cada vez."""
    return copy.deepcopy(c.CANDIDATOS[0])


class OConjuntoEstaFechadoEDistinto(unittest.TestCase):

    def test_sao_3_a_5_candidatos(self):
        self.assertGreaterEqual(len(c.CANDIDATOS), 3)
        self.assertLessEqual(len(c.CANDIDATOS), 5)

    def test_os_ids_sao_unicos(self):
        ids = [f["CANDIDATE_ID"] for f in c.CANDIDATOS]
        self.assertEqual(len(set(ids)), len(ids))

    def test_cada_candidato_e_de_uma_familia_diferente(self):
        """Dez variacoes cosmeticas do mesmo mecanismo nao sao um benchmark."""
        fam = [f["FAMILY"] for f in c.CANDIDATOS]
        self.assertEqual(len(set(fam)), len(fam), fam)

    def test_toda_ficha_tem_os_32_campos(self):
        for f in c.CANDIDATOS:
            faltam = [k for k in c.CAMPOS_OBRIGATORIOS if k not in f]
            self.assertEqual(faltam, [], "%s: %s" % (f["CANDIDATE_ID"], faltam))

    def test_o_conjunto_inteiro_valida(self):
        self.assertTrue(c.validar_conjunto(c.CANDIDATOS))

    def test_ninguem_se_declara_validado(self):
        for f in c.CANDIDATOS:
            self.assertIn(f["IMPLEMENTATION_STATUS"], c.STATUS_PERMITIDO)

    def test_o_conjunto_com_2_candidatos_nao_passa(self):
        with self.assertRaises(c.FichaInvalida):
            c.validar_conjunto(c.CANDIDATOS[:2])

    def test_duas_fichas_na_mesma_familia_nao_passam(self):
        duplicado = copy.deepcopy(c.CANDIDATOS)
        duplicado[1] = dict(duplicado[1], FAMILY=duplicado[0]["FAMILY"])
        with self.assertRaises(c.FichaInvalida):
            c.validar_conjunto(duplicado)

    def test_id_repetido_nao_passa(self):
        duplicado = copy.deepcopy(c.CANDIDATOS)
        duplicado[1] = dict(duplicado[1],
                            CANDIDATE_ID=duplicado[0]["CANDIDATE_ID"])
        with self.assertRaises(c.FichaInvalida):
            c.validar_conjunto(duplicado)


class ORedTeamDaContaminacao(unittest.TestCase):
    """Doze ataques. Cada um tem de falhar de maneira observavel."""

    def _recusa(self, muta):
        f = _boa()
        muta(f)
        with self.assertRaises(c.FichaInvalida):
            c.validar_ficha(f, c._termos_da_porta())

    def test_1_candidato_que_usa_a_fonte_como_resposta(self):
        self._recusa(lambda f: f["INPUTS_ALLOWED"].append("source_id"))

    def test_2_candidato_que_le_o_caminho_do_ficheiro(self):
        for campo in ("CONTENT_PATH", "BODY_PATH", "CANONICAL_PATH", "ITEM_ID"):
            self._recusa(lambda f, k=campo: f["INPUTS_ALLOWED"].append(k))

    def test_3_candidato_que_importa_o_gabarito(self):
        self._recusa(lambda f: f.__setitem__(
            "HYPOTHESIS", "le data/samples/T3-GROUND-TRUTH-EVAL-V1.json"))

    def test_4_candidato_que_usa_o_baseline_como_feature(self):
        self._recusa(lambda f: f.__setitem__(
            "TEXT_FIELDS_USED",
            ["data/derivados/BASELINE-ADMISSION-T3-V1.json"]))

    def test_5_candidato_com_parametro_nao_congelado(self):
        self._recusa(lambda f: f["TUNABLE_PARAMETERS"].append("limiar_solto"))

    def test_6_candidato_sem_abstencao_quando_declara_possuir(self):
        self._recusa(lambda f: f.__setitem__("DECISION_OUTPUT", ["SIM", "NAO"]))

    def test_7_candidato_duplicado_com_nome_diferente(self):
        clone = copy.deepcopy(c.CANDIDATOS)
        clone.append(dict(copy.deepcopy(clone[0]),
                          CANDIDATE_ID="C9-DISFARCE", NAME="outro nome"))
        with self.assertRaises(c.FichaInvalida):
            c.validar_conjunto(clone)

    def test_8_candidato_que_exige_treino_inexistente_e_se_diz_pronto(self):
        self._recusa(lambda f: f.update(
            TRAINING_REQUIRED="YES",
            TRAINING_SET_INDEPENDENT_FROM_EVALUATION="NO",
            CANDIDATE_STATUS="READY_FOR_IMPLEMENTATION"))

    def test_8b_treino_independente_alegado_sem_fonte(self):
        self._recusa(lambda f: f.update(
            TRAINING_REQUIRED="YES",
            TRAINING_SET_INDEPENDENT_FROM_EVALUATION="YES",
            TRAINING_SOURCE=None))

    def test_9_api_externa_sem_comportamento_de_falha(self):
        self._recusa(lambda f: f.update(EXTERNAL_API_DEPENDENCY="YES",
                                        FAILURE_BEHAVIOR=""))

    def test_10_alterar_a_ficha_muda_o_fingerprint(self):
        antes = c.impressao_da_ficha(_boa())
        f = _boa()
        f["HYPOTHESIS"] = f["HYPOTHESIS"] + " (mexido)"
        self.assertNotEqual(c.impressao_da_ficha(f), antes)

    def test_11_o_manifesto_nao_diverge_do_codigo(self):
        d = _manifesto_no_disco()
        self.assertEqual(d["CANDIDATE_SET_SHA256"],
                         c.impressao_do_conjunto(c.CANDIDATOS))
        self.assertEqual(d["CANDIDATE_COUNT"], len(c.CANDIDATOS))
        for ficha in d["CANDIDATES"]:
            viva = next(x for x in c.CANDIDATOS
                        if x["CANDIDATE_ID"] == ficha["CANDIDATE_ID"])
            self.assertEqual(ficha["CANDIDATE_SPEC_SHA256"],
                             c.impressao_da_ficha(viva))

    def test_12_candidato_que_promete_eame_sem_prova(self):
        self._recusa(lambda f: f.__setitem__(
            "EXPECTED_STRENGTH", "generaliza para EAME e Espanha"))

    def test_13_candidato_marcado_validado(self):
        self._recusa(lambda f: f.__setitem__("IMPLEMENTATION_STATUS",
                                             "VALIDATED"))

    def test_13b_status_inventado_e_recusado_pela_lista_branca(self):
        """⚠️ ESTE TESTE NASCEU DE UM MUTANTE SOBREVIVENTE.

        `test_13` poe `VALIDATED` e passa — mas passa pela lista NEGRA, nao
        pela lista BRANCA. Apagar a lista branca nao reprovava nada, porque a
        negra cobria o mesmo caso.

            DUAS GUARDAS QUE SE SOBREPOEM
            SAO UMA GUARDA E UMA TESTEMUNHA QUE NUNCA E CHAMADA.

        Um estado INVENTADO — nem permitido nem proibido — so pode ser
        apanhado pela lista branca, e e isso que este teste isola.
        """
        self.assertNotIn("QUASE_PRONTO", c.STATUS_PERMITIDO)
        self.assertNotIn("QUASE_PRONTO", c.STATUS_PROIBIDO)
        self._recusa(lambda f: f.__setitem__("IMPLEMENTATION_STATUS",
                                             "QUASE_PRONTO"))

    def test_14_configuracao_que_enumera_termos_da_regra_actual(self):
        """A memoria do corpus a entrar pela porta dos fundos."""
        import admissao as adm
        termo = adm.PERGUNTAS_DO_UNIVERSO["T3"][0]
        self._recusa(lambda f: f["FROZEN_PARAMETERS"].append(termo))

    def test_a_prosa_em_portugues_NAO_e_reprovada(self):
        """⚠️ A guarda dos termos ja reprovou texto legitimo uma vez.

        A lista de hoje contem palavras portuguesas comuns — `prova`,
        `registro`, `evento`. Se a guarda olhar para a prosa, ela reprova a
        explicacao do mecanismo em vez da contaminacao.
        """
        f = _boa()
        f["EXPECTED_STRENGTH"] = ("a prova deste registro e um evento "
                                  "auditavel do produto final")
        self.assertTrue(c.validar_ficha(f, c._termos_da_porta()))


class AsEntradasForamMedidas(unittest.TestCase):

    def test_o_caminho_esta_proibido_e_a_razao_esta_escrita(self):
        d = _manifesto_no_disco()
        for k in ("CONTENT_PATH", "BODY_PATH", "CANONICAL_PATH", "ITEM_ID"):
            self.assertIn(k, d["ENTRADAS_PROIBIDAS"])
        self.assertIn("78 de 78", d["PORQUE_O_CAMINHO_E_PROIBIDO"])

    def test_nenhum_candidato_le_campo_morto(self):
        """`title`, `nome`, `topics`, `crops`, `resumo` nao sao povoados."""
        mortos = {"title", "nome", "topics", "crops", "resumo"}
        for f in c.CANDIDATOS:
            self.assertEqual(set(f["TEXT_FIELDS_USED"]) & mortos, set(),
                             f["CANDIDATE_ID"])

    def test_a_fonte_e_so_contexto(self):
        d = _manifesto_no_disco()
        self.assertIn("nunca para decidir", d["SOURCE_IS_CONTEXT_ONLY"])
        for f in c.CANDIDATOS:
            self.assertNotIn("PUBLISHER", f["INPUTS_ALLOWED"],
                             f["CANDIDATE_ID"])

    def test_toda_saida_fala_a_lingua_da_porta(self):
        import admissao as adm
        for f in c.CANDIDATOS:
            for s in f["DECISION_OUTPUT"]:
                self.assertIn(s, adm.RESULTADOS, f["CANDIDATE_ID"])


class ODocumentoNaoDivergeDoCodigo(unittest.TestCase):
    """Os numeros vivem no codigo. O documento explica e cita.

        UMA LEI EM DOIS SITIOS DIVERGE.
    """

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(RAIZ, "docs", "operacao",
                               "CANDIDATOS-TEMATICOS-V1.md"),
                  encoding="utf-8") as f:
            cls.doc = f.read()

    def test_o_fingerprint_do_conjunto_bate(self):
        self.assertIn("CANDIDATE_SET_SHA256     = %s"
                      % c.impressao_do_conjunto(c.CANDIDATOS), self.doc)

    def test_cada_ficha_publica_o_seu_fingerprint(self):
        for f in c.CANDIDATOS:
            self.assertIn(c.impressao_da_ficha(f), self.doc,
                          f["CANDIDATE_ID"])

    def test_o_documento_nomeia_os_quatro_candidatos(self):
        for f in c.CANDIDATOS:
            self.assertIn(f["CANDIDATE_ID"], self.doc)

    def test_o_documento_diz_que_nada_foi_medido(self):
        self.assertIn("BENCHMARK_EXECUTED       = NO", self.doc)
        self.assertIn("FROZEN_BEFORE_EVALUATION = YES", self.doc)

    def test_o_documento_declara_a_exposicao_previa(self):
        self.assertIn("DESIGNER_PRIOR_EXPOSURE = YES", self.doc)

    def test_o_documento_nao_e_o_dono(self):
        self.assertIn("vivem no código", self.doc)


class OQueEstaMissaoNaoFez(unittest.TestCase):

    def test_nenhum_benchmark_foi_executado(self):
        d = _manifesto_no_disco()
        self.assertEqual(d["BENCHMARK_EXECUTED"], "NO")
        self.assertEqual(d["CANDIDATE_RESULTS_VIEWED"], "NO")
        self.assertEqual(d["FROZEN_BEFORE_EVALUATION"], "YES")

    def test_o_manifesto_nao_contem_metrica_de_resultado(self):
        """Um numero que so poderia vir do corpus de avaliacao."""
        bruto = json.dumps(_manifesto_no_disco(), ensure_ascii=False)
        for proibido in ('"TP"', '"TN"', '"FP"', '"FN"', "GROUP_PASS",
                         "DECISION_COVERAGE", "PRECISION_T3", "ACCURACY"):
            self.assertNotIn(proibido, bruto, proibido)

    def test_o_modulo_nao_le_o_gabarito(self):
        with open(os.path.join(RAIZ, "provas", "candidatos_tematicos.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        # citar em FICHEIROS_PROIBIDOS e declarar; abrir e outra coisa.
        import ast
        arvore = ast.parse(fonte)
        for no in ast.walk(arvore):
            if isinstance(no, ast.Call) and getattr(no.func, "id", "") == "open":
                arg = ast.unparse(no.args[0]) if no.args else ""
                for mau in c.FICHEIROS_PROIBIDOS:
                    self.assertNotIn(mau, arg)

    def test_a_admissao_e_o_gate_nao_mudaram(self):
        import subprocess
        for caminho in ("admissao/", "provas/gate_de_aceitacao_tematica.py"):
            d = subprocess.run(["git", "diff", "HEAD", "--stat", "--", caminho],
                               cwd=RAIZ, capture_output=True, text=True).stdout
            self.assertEqual(d.strip(), "", caminho)

    def test_o_mecanismo_actual_nao_e_candidato(self):
        d = _manifesto_no_disco()
        self.assertIn("BASELINE", d["O_MECANISMO_ACTUAL_NAO_E_CANDIDATO"])

    def test_as_exclusoes_tem_razao_medida(self):
        d = _manifesto_no_disco()
        self.assertEqual(len(d["FAMILIAS_EXCLUIDAS"]), 2)
        for x in d["FAMILIAS_EXCLUIDAS"]:
            self.assertGreater(len(x["PORQUE"]), 100, x["FAMILY"])
            self.assertTrue(x["O_QUE_DESBLOQUEIA"], x["FAMILY"])

    def test_a_exposicao_previa_esta_declarada(self):
        """Fingir que nao vi seria a propria contaminacao."""
        e = _manifesto_no_disco()["EXPOSICAO_PREVIA_DE_QUEM_DESENHOU"]
        self.assertEqual(e["DESIGNER_PRIOR_EXPOSURE"], "YES")
        self.assertTrue(e["MITIGACAO_ESTRUTURAL"])
        self.assertTrue(e["O_QUE_ISTO_NAO_RESOLVE"])

    def test_as_lacunas_do_estudo_ficam_escritas(self):
        d = _manifesto_no_disco()
        self.assertGreaterEqual(len(d["LACUNAS_DO_ESTUDO"]), 3)


if __name__ == "__main__":
    unittest.main()
