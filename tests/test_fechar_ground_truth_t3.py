# -*- coding: utf-8 -*-
"""O GABARITO NAO PODE DECIDIR ONDE OS HUMANOS NAO FECHARAM.

Um gerador de gabarito falha de maneiras que nenhuma excecao denuncia. Ele
corre, escreve um JSON bonito, e o numero cresce — porque encheu:

    1. o item divergente entrou, com o rotulo de um dos lados;
    2. `EVIDENCIA_INSUFICIENTE` virou `NAO`, que e o que mais tenta;
    3. `AMBIGUO` virou `SIM`;
    4. quatro edicoes do mesmo boletim contaram como quatro observacoes.

    A != A2  ->  UNRESOLVED, E MAIS NADA.
    EVIDENCIA_INSUFICIENTE  !=  NAO
    QUATRO COPIAS DO MESMO BOLETIM NAO SAO QUATRO PROVAS.
"""
import copy
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "fechar_gt_t3", os.path.join(RAIZ, "provas", "fechar_ground_truth_t3.py"))
f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f)


def _doc():
    with open(os.path.join(RAIZ, f.GABARITO), encoding="utf-8") as fh:
        return json.load(fh)


class AsEntradasHumanasEntramInteiras(unittest.TestCase):
    """Os dois ficheiros sao evidencia externa. Nao se corrigem: conferem-se."""

    @classmethod
    def setUpClass(cls):
        cls.a, cls.g, cls.A = f.carregar()

    def test_o_portao_bate_com_o_ficheiro_no_disco(self):
        caminho = os.path.join(RAIZ, f.PORTAO)
        with open(caminho, "rb") as fh:
            esperado = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(f.sha256_do_ficheiro(f.PORTAO), esperado)

    def test_as_contagens_do_portao_fecham(self):
        self.assertEqual(self.g["STATUS"], "COMPLETE")
        self.assertEqual(self.g["TOTAL_ANSWERED"], 53)
        self.assertEqual(len(self.g["ITEMS"]), 53)

    def test_53_sha_unicos_e_todos_existem_em_a(self):
        shas = [x["DOC_SHA256"] for x in self.g["ITEMS"]]
        self.assertEqual(len(set(shas)), 53)
        self.assertTrue(all(s in self.A for s in shas))

    def test_as_duas_filas_tem_os_tamanhos_medidos(self):
        from collections import Counter
        c = Counter(x["QUEUE"] for x in self.g["ITEMS"])
        self.assertEqual(c["CONFIRMACAO"], 32)
        self.assertEqual(c["SEGUNDA_LEITURA"], 21)

    def test_o_portao_nao_alega_o_que_nao_e(self):
        self.assertEqual(self.g["AUTO_LABELS_ASSIGNED"], 0)
        self.assertIs(self.g["INDEPENDENT_SECOND_REVIEWER"], False)
        self.assertIs(self.g["FINAL_LABEL_DECIDIDO_AQUI"], False)

    # ⚠️ Estes testes chamam `carregar()` com um ficheiro estragado. Refazer a
    # conta dentro do teste e compara-la consigo passaria com a guarda apagada.
    def _com_portao_estragado(self, estraga):
        g = copy.deepcopy(self.g)
        estraga(g)
        guardado = f.PORTAO
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                          encoding="utf-8")
        try:
            json.dump(g, tmp, ensure_ascii=False)
            tmp.close()
            f.PORTAO = tmp.name
            with self.assertRaises(f.FechoInvalido):
                f.carregar()
        finally:
            f.PORTAO = guardado
            os.unlink(tmp.name)

    def test_schema_desconhecido_nao_passa(self):
        self._com_portao_estragado(
            lambda g: g.__setitem__("SCHEMA", "sintonia.outra-coisa/9"))

    def test_portao_incompleto_nao_passa(self):
        self._com_portao_estragado(
            lambda g: g.__setitem__("STATUS", "INCOMPLETE"))

    def test_contagem_que_nao_fecha_nao_passa(self):
        self._com_portao_estragado(lambda g: g["ITEMS"].pop())

    def test_sha_duplicado_nao_passa(self):
        self._com_portao_estragado(
            lambda g: g["ITEMS"][1].__setitem__(
                "DOC_SHA256", g["ITEMS"][0]["DOC_SHA256"]))

    def test_portao_que_alega_ter_decidido_o_final_nao_passa(self):
        self._com_portao_estragado(
            lambda g: g.__setitem__("FINAL_LABEL_DECIDIDO_AQUI", True))

    def test_portao_com_rotulo_de_maquina_nao_passa(self):
        self._com_portao_estragado(
            lambda g: g.__setitem__("AUTO_LABELS_ASSIGNED", 7))

    def test_portao_que_alega_revisor_independente_nao_passa(self):
        self._com_portao_estragado(
            lambda g: g.__setitem__("INDEPENDENT_SECOND_REVIEWER", True))

    def test_nenhuma_entrada_humana_e_tocada(self):
        antes = (f.sha256_do_ficheiro(f.REVISAO_A),
                 f.sha256_do_ficheiro(f.PORTAO))
        f.gerar()
        self.assertEqual((f.sha256_do_ficheiro(f.REVISAO_A),
                          f.sha256_do_ficheiro(f.PORTAO)), antes)


class ADecisaoItemAItem(unittest.TestCase):
    """Cada saida da adjudicacao, provada com uma entrada construida a mao."""

    def _par(self, la, a2=None, fila="SEGUNDA_LEITURA", **extra):
        item_a = {"LABEL": la, "ITEM_ID": "x", "DOC_SHA256": "s",
                  "DECIDED_AT": "2026-09-11T00:00:00Z", "ORIGINAL_EVIDENCE": {}}
        item_g = {"QUEUE": fila, "ITEM_ID": "x", "LABEL_A2": a2,
                  "REASON_CODE": "ASSUNTO_DIFERENTE", "REASON_TEXT": None,
                  "EVIDENCE_ATTESTED": True, "CONFIRMED": fila == "CONFIRMACAO",
                  "DECIDED_AT": "2026-09-11T00:00:00Z"}
        item_g.update(extra)
        return f.adjudicar(item_a, item_g)

    def test_confirmacao_fica_com_o_rotulo_de_a(self):
        self.assertEqual(self._par("T3_SIM", fila="CONFIRMACAO"),
                         (f.CONFIRMED, "T3_SIM"))
        self.assertEqual(self._par("T3_NAO", fila="CONFIRMACAO"),
                         (f.CONFIRMED, "T3_NAO"))

    def test_releitura_cega_que_bate_confirma(self):
        self.assertEqual(self._par("T3_NAO", "T3_NAO"),
                         (f.CONFIRMED_CEGO, "T3_NAO"))
        self.assertEqual(self._par("T3_SIM", "T3_SIM"),
                         (f.CONFIRMED_CEGO, "T3_SIM"))

    def test_divergencia_nao_escolhe_lado_nenhum(self):
        for la, a2 in (("T3_SIM", "T3_NAO"), ("T3_NAO", "T3_SIM"),
                       ("T3_NAO", "EVIDENCIA_INSUFICIENTE"),
                       ("EVIDENCIA_INSUFICIENTE", "T3_NAO"),
                       ("T3_AMBIGUO", "T3_SIM")):
            estado, rotulo = self._par(la, a2)
            self.assertEqual(estado, f.UNRESOLVED, (la, a2))
            self.assertIsNone(rotulo, (la, a2))

    def test_insuficiente_dos_dois_lados_e_buraco_nao_negativo(self):
        estado, rotulo = self._par("EVIDENCIA_INSUFICIENTE",
                                   "EVIDENCIA_INSUFICIENTE")
        self.assertEqual(estado, f.EVIDENCE_GAP)
        self.assertIsNone(rotulo)

    def test_ambiguo_dos_dois_lados_nao_vira_sim(self):
        estado, rotulo = self._par("T3_AMBIGUO", "T3_AMBIGUO")
        self.assertEqual(estado, f.AMBIGUOUS)
        self.assertIsNone(rotulo)

    def test_sem_atestacao_nao_se_adjudica(self):
        with self.assertRaises(f.FechoInvalido):
            self._par("T3_NAO", "T3_NAO", EVIDENCE_ATTESTED=False)

    def test_sem_razao_nao_se_adjudica(self):
        with self.assertRaises(f.FechoInvalido):
            self._par("T3_NAO", "T3_NAO", REASON_CODE=None)

    def test_confirmacao_sem_confirmed_nao_se_adjudica(self):
        with self.assertRaises(f.FechoInvalido):
            self._par("T3_NAO", fila="CONFIRMACAO", CONFIRMED=False)


class OFechoMedido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a, cls.g, cls.itens, cls.doc = f.gerar()
        cls.c = cls.doc["COUNTS"]

    def test_as_contagens_reproduzem_o_esperado(self):
        self.assertEqual(self.c["EVAL_ELIGIBLE"], 36)
        self.assertEqual(self.c["CONFIRMED_SIM"], 14)
        self.assertEqual(self.c["CONFIRMED_NAO"], 22)
        self.assertEqual(self.c["EVIDENCE_GAP"], 6)
        self.assertEqual(self.c["UNRESOLVED"], 11)
        self.assertEqual(self.c["AMBIGUOUS"], 0)

    def test_os_quatro_estados_somam_os_53(self):
        self.assertEqual(
            self.c["EVAL_ELIGIBLE"] + self.c["UNRESOLVED"]
            + self.c["EVIDENCE_GAP"] + self.c["AMBIGUOUS"], 53)

    def test_o_gabarito_leva_so_os_confirmados(self):
        gt = self.doc["GROUND_TRUTH"]
        self.assertEqual(len(gt), 36)
        self.assertEqual({x["LABEL"] for x in gt}, {"T3_SIM", "T3_NAO"})

    def test_nenhum_unresolved_no_gabarito(self):
        fora = {x["DOC_SHA256"] for x in self.doc["EXCLUDED_FROM_EVALUATION"]
                if x["STATUS"] == f.UNRESOLVED}
        dentro = {x["DOC_SHA256"] for x in self.doc["GROUND_TRUTH"]}
        self.assertEqual(fora & dentro, set())
        self.assertEqual(len(fora), 11)

    def test_nenhum_insuficiente_no_gabarito(self):
        insuf = {i["DOC_SHA256"] for i in self.itens
                 if i["FINAL_STATUS"] == f.EVIDENCE_GAP}
        dentro = {x["DOC_SHA256"] for x in self.doc["GROUND_TRUTH"]}
        self.assertEqual(insuf & dentro, set())

    def test_nenhum_sha_repetido_no_gabarito(self):
        shas = [x["DOC_SHA256"] for x in self.doc["GROUND_TRUTH"]]
        self.assertEqual(len(set(shas)), len(shas))

    def test_os_17_de_fora_ficam_guardados_com_o_nome_do_estado(self):
        fora = self.doc["EXCLUDED_FROM_EVALUATION"]
        self.assertEqual(len(fora), 17)
        self.assertEqual({x["STATUS"] for x in fora},
                         {f.UNRESOLVED, f.EVIDENCE_GAP})
        for x in fora:
            self.assertIn("LABEL_A", x)
            self.assertIn("LABEL_A2", x)

    def test_dentro_mais_fora_sao_os_53_e_nao_se_cruzam(self):
        d = {x["DOC_SHA256"] for x in self.doc["GROUND_TRUTH"]}
        o = {x["DOC_SHA256"] for x in self.doc["EXCLUDED_FROM_EVALUATION"]}
        self.assertEqual(len(d | o), 53)
        self.assertEqual(d & o, set())

    def test_toda_autoridade_e_humana(self):
        self.assertEqual({x["LABEL_AUTHORITY"] for x in self.doc["GROUND_TRUTH"]},
                         {"HUMAN_VERIFIED"})

    def test_todo_item_tem_razao_estruturada_e_evidencia_atestada(self):
        for x in self.doc["GROUND_TRUTH"]:
            self.assertTrue(x["HUMAN_REASON_CODE"], x["ITEM_ID"])
            self.assertIs(x["EVIDENCE_ATTESTED"], True, x["ITEM_ID"])

    def test_nenhum_texto_de_razao_foi_inventado(self):
        """A pessoa nao escreveu nenhum. O campo fica null, e nao preenchido."""
        for x in self.doc["GROUND_TRUTH"]:
            self.assertIsNone(x["HUMAN_REASON_TEXT"], x["ITEM_ID"])

    def test_a_linhagem_esta_declarada(self):
        self.assertEqual(self.doc["SOURCE_REVIEW_A_SHA256"],
                         f.sha256_do_ficheiro(f.REVISAO_A))
        self.assertEqual(self.doc["SOURCE_QUALITY_GATE_SHA256"],
                         f.sha256_do_ficheiro(f.PORTAO))
        self.assertEqual(self.doc["GENERATOR"], f.GERADOR)
        self.assertTrue(self.doc["GENERATED_AT"])

    def test_o_artefato_sai_igual_duas_vezes(self):
        um = json.dumps(f.gerar()[3], ensure_ascii=False, sort_keys=True)
        dois = json.dumps(f.gerar()[3], ensure_ascii=False, sort_keys=True)
        self.assertEqual(um, dois)

    def test_o_ficheiro_no_disco_bate_com_o_gerador(self):
        self.assertEqual(
            json.dumps(_doc(), ensure_ascii=False, sort_keys=True),
            json.dumps(self.doc, ensure_ascii=False, sort_keys=True))


class ADiversidadeEOHoldout(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.doc = _doc()
        cls.d = cls.doc["DIVERSITY"]

    def test_os_publicadores_reproduzem_o_medido(self):
        self.assertEqual(len(self.d["POSITIVE_PUBLISHERS"]), 6)
        self.assertEqual(len(self.d["NEGATIVE_PUBLISHERS"]), 9)

    def test_nao_sei_nao_conta_como_fonte(self):
        for campo in ("POSITIVE_SOURCE_IDS", "NEGATIVE_SOURCE_IDS",
                      "POSITIVE_PUBLISHERS", "NEGATIVE_PUBLISHERS"):
            self.assertNotIn(f.SEM_VALOR, self.d[campo], campo)
        self.assertGreater(self.d["SOURCE_ID_AUSENTE"], 0,
                           "se nao houvesse ausentes este teste nao provaria nada")

    def test_o_holdout_exige_as_duas_classes(self):
        h = self.doc["HOLDOUT"]
        self.assertEqual(h["PUBLISHER_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE"], "YES")
        self.assertEqual(h["COUNTRY_HOLDOUT_POSSIBLE"], "NO")
        self.assertEqual(h["LANGUAGE_HOLDOUT_POSSIBLE"], "NO")

    def test_um_publicador_so_no_lado_positivo_reprova_o_holdout(self):
        """Mutacao: se todos os positivos vierem do mesmo sitio, cai."""
        pos = [{"PUBLISHER": "UM SO", "SOURCE_ID": "x"} for _ in range(14)]
        neg = [{"PUBLISHER": "UM SO", "SOURCE_ID": "x"} for _ in range(22)]
        ok, _ = f.holdout_possivel(pos, neg, "PUBLISHER")
        self.assertFalse(ok)

    def test_quase_duplicados_foram_medidos_e_encontrados(self):
        nd = self.doc["NEAR_DUPLICATES"]
        self.assertEqual(nd["LIMIAR"], f.LIMIAR_QUASE_DUPLICADO)
        self.assertGreater(nd["TOTAL_PARES"], 0,
                           "sem pares, a medida de independencia nao prova nada")

    def test_os_14_positivos_sao_menos_observacoes_do_que_ficheiros(self):
        ind = self.doc["INDEPENDENCIA"]
        self.assertEqual(ind["POSITIVOS_DOCUMENTOS"], 14)
        self.assertEqual(ind["POSITIVOS_INDEPENDENTES"], 11)
        self.assertLess(ind["GRUPOS_INDEPENDENTES"], ind["DOCUMENTS"])

    def test_o_portao_conta_grupos_e_passa_criterio_a_criterio(self):
        g = self.doc["EVALUATION_GATE"]
        self.assertTrue(g["PASSA"])
        self.assertEqual(len(g["LINHAS"]), 7)
        for l in g["LINHAS"]:
            self.assertTrue(l["PASSA"], l["CRITERIO"])

    def test_o_portao_reprova_se_os_positivos_independentes_cairem(self):
        """Mutacao: 9 positivos independentes tem de reprovar, nao arredondar."""
        pos = [{"PUBLISHER": "P%d" % i, "SOURCE_ID": "s%d" % i,
                "REASON_CODE_A2": "X", "EVIDENCE_ATTESTED": True,
                "CORPO_NO_DISCO": True} for i in range(9)]
        neg = [{"PUBLISHER": "N%d" % i, "SOURCE_ID": "t%d" % i,
                "REASON_CODE_A2": "X", "EVIDENCE_ATTESTED": True,
                "CORPO_NO_DISCO": True} for i in range(20)]
        self.assertFalse(f.portao_de_avaliacao(pos, neg, True)["PASSA"])

    def test_o_escopo_esta_declarado_e_nao_promete_eame(self):
        self.assertEqual(self.doc["EVALUATION_SCOPE"],
                         "ITALIAN_AGRO_INSTITUTIONAL_CORPUS")
        bruto = json.dumps(self.doc, ensure_ascii=False)
        for proibido in ("GENERALIZA PARA", "generaliza para EAME"):
            self.assertNotIn(proibido, bruto)

    def test_o_idioma_foi_medido_e_nao_presumido(self):
        idi = self.doc["IDIOMA_MEDIDO"]
        self.assertGreater(idi["NAO_RESOLVIDO"], 0)
        self.assertEqual(idi["NAO_ITALIANO"], ["91515"])
        self.assertEqual(self.doc["DIVERSITY"]["COUNTRIES"], ["IT"])


class OCensoVeODeVerdade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "_censo_t3", os.path.join(RAIZ, "provas",
                                      "censo_corpus_rotulado_admission.py"))
        cls.c = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.c)

    def test_o_gabarito_entra_como_origem_humana(self):
        origens = self.c.origens_de_rotulo()
        nossa = [o for o in origens if o["PATH"] == self.c.GABARITO_T3]
        self.assertEqual(len(nossa), 1)
        self.assertEqual(nossa[0]["AUTORIDADE"], self.c.HUMAN_VERIFIED)
        self.assertIn(nossa[0]["AUTORIDADE"], self.c.SERVEM_DE_GABARITO)

    def test_nao_e_derivado_de_keyword_nem_de_modelo(self):
        origens = self.c.origens_de_rotulo()
        nossa = next(o for o in origens if o["PATH"] == self.c.GABARITO_T3)
        self.assertNotEqual(nossa["AUTORIDADE"], self.c.KEYWORD_DERIVED)
        self.assertNotEqual(nossa["AUTORIDADE"], self.c.MODEL_DERIVED)

    def test_o_censo_conta_grupos_e_nao_ficheiros(self):
        todos, ind = self.c.corpus_t3()
        self.assertEqual(len(todos), 36)
        self.assertEqual(len(ind), 31)

    def test_t3_passa_o_portao_com_os_criterios_congelados(self):
        _, ind = self.c.corpus_t3()
        p = [x for x in ind if x["LABEL"] == "T3:SIM"]
        n = [x for x in ind if x["LABEL"] == "T3:NAO"]
        publ = sorted({x["PUBLICADOR"] for x in p + n})
        fam = sorted({x["FAMILIA"] for x in p + n})
        g = self.c.portao("T3", p, n, publ, fam)
        self.assertTrue(g["SANITY"])
        self.assertTrue(g["EVALUATION"])
        self.assertFalse(g["TRAINING"])
        self.assertEqual(g["VEREDICTO"], "B")

    def test_os_criterios_nao_foram_mexidos_nesta_missao(self):
        """Criar limiar depois de ver o resultado e desenhar o alvo a volta
        da flecha. Estes numeros vieram da missao do censo."""
        c = self.c.CRITERIOS
        self.assertEqual(c["EVALUATION"]["POSITIVOS_MIN"], 10)
        self.assertEqual(c["EVALUATION"]["NEGATIVOS_MIN"], 10)
        self.assertEqual(c["EVALUATION"]["PUBLICADORES_MIN"], 3)
        self.assertEqual(c["SANITY"]["POSITIVOS_MIN"], 3)
        self.assertEqual(c["TRAINING"]["POSITIVOS_MIN"], 100)

    def test_t3_nao_atinge_treino(self):
        _, ind = self.c.corpus_t3()
        self.assertLess(len(ind), self.c.CRITERIOS["TRAINING"]["POSITIVOS_MIN"])


class ORedTeamPodeMesmoCeder(unittest.TestCase):
    """Uma sonda que nao pode ser falsa nao e uma sonda.

    ⚠️ TRES DESTAS SONDAS NASCERAM ASSIM. Uma comparava os grupos consigo
    propria; outra perguntava se o dicionario de idiomas estava vazio; a
    terceira tinha um `or` que a fazia passar sempre.

        UMA SONDA QUE NAO PODE FALHAR NAO ESTA A MEDIR NADA:
        ESTA A DIZER QUE SIM.
    """

    @classmethod
    def setUpClass(cls):
        cls.a, cls.g, cls.itens, cls.doc = f.gerar()

    def _sonda(self, doc, prefixo, itens=None):
        rt = f.red_team(itens or self.itens, doc)
        return next(r for r in rt if r["SONDA"].startswith(prefixo))

    def test_as_dez_sondas_aguentam_no_estado_real(self):
        self.assertEqual(len(self.doc["RED_TEAM"]), 10)
        for r in self.doc["RED_TEAM"]:
            self.assertTrue(r["AGUENTA"], r["SONDA"])

    def test_sonda_2_cede_se_o_portao_contar_ficheiros(self):
        d = copy.deepcopy(self.doc)
        for l in d["EVALUATION_GATE"]["LINHAS"]:
            if l["CRITERIO"].startswith("POSITIVOS"):
                l["MEDIDO"] = d["INDEPENDENCIA"]["POSITIVOS_DOCUMENTOS"]
        self.assertFalse(self._sonda(d, "2 ·")["AGUENTA"])

    def test_sonda_5_cede_se_um_divergente_entrar(self):
        d = copy.deepcopy(self.doc)
        divergente = next(i for i in self.itens
                          if i["FINAL_STATUS"] == f.UNRESOLVED)
        d["GROUND_TRUTH"].append({
            "DOC_SHA256": divergente["DOC_SHA256"], "ITEM_ID": "intruso",
            "LABEL": "T3_NAO", "REVIEW_PATH": "A_CONFIRMED",
            "HUMAN_REASON_CODE": "X", "EVIDENCE_ATTESTED": True})
        self.assertFalse(self._sonda(d, "5 ·")["AGUENTA"])

    def test_sonda_6_cede_se_um_buraco_de_evidencia_entrar(self):
        d = copy.deepcopy(self.doc)
        buraco = next(i for i in self.itens
                      if i["FINAL_STATUS"] == f.EVIDENCE_GAP)
        d["GROUND_TRUTH"].append({
            "DOC_SHA256": buraco["DOC_SHA256"], "ITEM_ID": "intruso",
            "LABEL": "T3_NAO", "REVIEW_PATH": "A_CONFIRMED",
            "HUMAN_REASON_CODE": "X", "EVIDENCE_ATTESTED": True})
        self.assertFalse(self._sonda(d, "6 ·")["AGUENTA"])

    def test_sonda_4_cede_se_faltar_atestacao(self):
        d = copy.deepcopy(self.doc)
        d["GROUND_TRUTH"][0]["EVIDENCE_ATTESTED"] = False
        self.assertFalse(self._sonda(d, "4 ·")["AGUENTA"])

    def test_sonda_7_cede_se_a2_trocar_a_em_silencio(self):
        d = copy.deepcopy(self.doc)
        alvo = next(x for x in d["GROUND_TRUTH"]
                    if x["REVIEW_PATH"] == "A_CONFIRMED")
        alvo["LABEL"] = "T3_SIM" if alvo["LABEL"] == "T3_NAO" else "T3_NAO"
        self.assertFalse(self._sonda(d, "7 ·")["AGUENTA"])

    def test_sonda_8_cede_se_nao_sei_virar_fonte(self):
        d = copy.deepcopy(self.doc)
        d["DIVERSITY"]["POSITIVE_SOURCE_IDS"].append(f.SEM_VALOR)
        self.assertFalse(self._sonda(d, "8 ·")["AGUENTA"])

    def test_sonda_9_cede_se_um_item_ficar_fora_da_contagem_de_idioma(self):
        d = copy.deepcopy(self.doc)
        d["IDIOMA_MEDIDO"]["NAO_RESOLVIDO"] -= 1
        self.assertFalse(self._sonda(d, "9 ·")["AGUENTA"])

    def test_sonda_10_cede_se_a_ressalva_desaparecer(self):
        d = copy.deepcopy(self.doc)
        d["O_LIMITE_DO_ESCOPO"] = "sem ressalva nenhuma"
        self.assertFalse(self._sonda(d, "10 ·")["AGUENTA"])

    def test_sonda_10_cede_se_o_artefato_afirmar_generalizacao(self):
        d = copy.deepcopy(self.doc)
        d["NOTA"] = "este gabarito generaliza para EAME"
        self.assertFalse(self._sonda(d, "10 ·")["AGUENTA"])

    def test_sonda_1_cede_se_todos_os_positivos_forem_da_mesma_serie(self):
        itens = copy.deepcopy(self.itens)
        for i in itens:
            if i["FINAL_LABEL"] == "T3_SIM":
                i["PUBLICATION_SERIES"] = "uma so"
        self.assertFalse(self._sonda(self.doc, "1 ·", itens)["AGUENTA"])

    def test_sonda_3_cede_se_um_duplicado_atravessar_publicadores(self):
        d = copy.deepcopy(self.doc)
        par = d["NEAR_DUPLICATES"]["PARES"][0]
        itens = copy.deepcopy(self.itens)
        for i in itens:
            if i["DOC_SHA256"] == par["A"]:
                i["PUBLISHER"] = "OUTRO PUBLICADOR"
        self.assertFalse(self._sonda(d, "3 ·", itens)["AGUENTA"])


class OQueEstaMissaoNaoFaz(unittest.TestCase):

    def _fonte(self, ficheiro):
        with open(os.path.join(RAIZ, "provas", ficheiro), encoding="utf-8") as fh:
            return fh.read()

    def test_nao_ha_classificador_nem_treino(self):
        fonte = self._fonte("fechar_ground_truth_t3.py")
        for proibido in ("sklearn", "torch", "transformers", "embedding",
                         "def treinar", ".fit(", ".predict("):
            self.assertNotIn(proibido, fonte)

    def test_nao_ha_rede(self):
        fonte = self._fonte("fechar_ground_truth_t3.py")
        for proibido in ("requests", "urllib", "httpx", "socket"):
            self.assertNotIn(proibido, fonte)

    def test_as_entradas_humanas_nao_sao_abertas_para_escrita(self):
        fonte = self._fonte("fechar_ground_truth_t3.py")
        self.assertNotIn('open(os.path.join(RAIZ, PORTAO), "w"', fonte)
        self.assertNotIn('open(os.path.join(RAIZ, REVISAO_A), "w"', fonte)

    def test_a_admission_nao_e_importada_para_escrita(self):
        fonte = self._fonte("fechar_ground_truth_t3.py")
        self.assertNotIn("PERGUNTAS_DO_UNIVERSO", fonte)

    def test_nao_se_criou_um_segundo_gabarito_paralelo(self):
        base = os.path.join(RAIZ, "data", "samples")
        maus = [n for n in os.listdir(base)
                if n.startswith("T3-GROUND-TRUTH")
                and n != os.path.basename(f.GABARITO)]
        self.assertEqual(maus, [])


if __name__ == "__main__":
    unittest.main()
