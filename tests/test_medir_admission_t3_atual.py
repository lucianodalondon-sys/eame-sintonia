# -*- coding: utf-8 -*-
"""UMA BASELINE QUE MEDE UMA COPIA NAO MEDE NADA.

Esta prova falha de quatro maneiras que nenhuma excecao denuncia:

    1. reimplementa as palavras da porta e mede a si propria;
    2. esmaga `NAO_SEI` em `NAO` e inventa cobertura que nao existe;
    3. reagrupa os documentos depois de ver o score;
    4. esconde um falso positivo do relatorio.

    MEASURE != FIX
    NAO != NAO_SEI != NAO_SE_APLICA != ERRO
"""
import copy
import hashlib
import importlib.util
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "medir_t3", os.path.join(RAIZ, "provas", "medir_admission_t3_atual.py"))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

ARTEFATO = os.path.join(RAIZ, m.SAIDA)


def _art():
    with open(ARTEFATO, encoding="utf-8") as f:
        return json.load(f)


class ODonoRealFoiProvado(unittest.TestCase):
    """Nao basta «o modulo existe»: cada elo e lido no ficheiro."""

    @classmethod
    def setUpClass(cls):
        cls.cadeia = m.provar_cadeia()

    def test_cada_elo_aponta_para_linha_que_existe(self):
        for e in self.cadeia:
            with open(os.path.join(RAIZ, e["FILE"]), encoding="utf-8") as f:
                linhas = f.read().splitlines()
            self.assertIn(e["MARCA"], linhas[e["LINE"] - 1], e["FILE"])

    def test_a_cadeia_chega_ao_chamador_de_producao(self):
        ficheiros = {e["FILE"] for e in self.cadeia}
        self.assertIn("orquestrador/orquestrador.py", ficheiros)
        self.assertIn("coleta/rota_forward_documento.py", ficheiros)

    def test_um_elo_que_desapareca_derruba_a_medicao(self):
        guardado = m.CADEIA
        try:
            m.CADEIA = list(guardado) + [
                ("admissao/admissao.py", "def funcao_que_nao_existe(", "x")]
            with self.assertRaises(m.MedicaoInvalida):
                m.provar_cadeia()
        finally:
            m.CADEIA = guardado

    def test_ha_um_unico_dono_tematico(self):
        self.assertEqual(_art()["THEMATIC_DECISION_OWNERS"], 1)
        self.assertEqual(_art()["ADMISSION_OWNER_FILE"], "admissao/admissao.py")


class AProvaNaoCopiouAPorta(unittest.TestCase):
    """COPYING_CURRENT_KEYWORDS_INTO_THE_PROOF = PROIBIDO."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(RAIZ, "provas",
                               "medir_admission_t3_atual.py"),
                  encoding="utf-8") as f:
            cls.fonte = f.read()

    def test_nenhuma_palavra_da_porta_esta_escrita_na_prova(self):
        for termo in adm.PERGUNTAS_DO_UNIVERSO["T3"]:
            self.assertNotIn('"%s"' % termo, self.fonte, termo)
            self.assertNotIn("'%s'" % termo, self.fonte, termo)

    def test_a_prova_chama_a_funcao_real(self):
        self.assertIn("adm.decidir(item, UNIVERSO)", self.fonte)

    # ⚠️ A PRIMEIRA VERSAO DESTE TESTE PROCURAVA `"in texto:"` E ACENDIA NA
    # PROPRIA SONDA DE SUBSTRING — que le texto para MEDIR, e nao para decidir.
    # E acendia tambem nos ponteiros da CADEIA, que sao DADOS a apontar para a
    # producao, nao codigo a imita-la.
    #
    #     PROCURAR UMA STRING QUE TAMBEM APARECE NO SITIO CERTO
    #     REPROVA CODIGO CERTO E ENSINA A IGNORAR O TESTE.
    #
    # O que interessa nao e uma string: e se esta prova tem uma LISTA DE TERMOS
    # propria, e se algum veredicto sai de outro sitio que nao a porta.
    def test_a_prova_nao_tem_lista_de_termos_propria(self):
        import ast
        arvore = ast.parse(self.fonte)
        for no in arvore.body:
            if not isinstance(no, (ast.Assign, ast.AnnAssign)):
                continue
            valor = no.value
            if not isinstance(valor, (ast.List, ast.Tuple)):
                continue
            palavras = [e.value for e in valor.elts
                        if isinstance(e, ast.Constant)
                        and isinstance(e.value, str)
                        and e.value.isalpha() and e.value.islower()]
            self.assertLess(
                len(palavras), 3,
                "esta prova tem uma lista de termos propria: %s" % palavras)

    def test_o_veredicto_so_pode_vir_da_porta(self):
        """Em `medir`, `cru` so e atribuido por `d.resultado` ou pelo ERRO."""
        import ast
        arvore = ast.parse(self.fonte)
        fn = next(n for n in ast.walk(arvore)
                  if isinstance(n, ast.FunctionDef) and n.name == "medir")
        fontes = []
        for no in ast.walk(fn):
            if not isinstance(no, ast.Assign):
                continue
            alvos = [t.id for t in ast.walk(no) if isinstance(t, ast.Name)][:1]
            if not alvos or alvos[0] != "cru":
                continue
            fontes.append(ast.unparse(no.value))
        self.assertTrue(fontes)
        for f in fontes:
            self.assertTrue("d.resultado" in f or "adm.ERRO" in f, f)

    def test_a_sonda_de_substring_nao_alimenta_nenhuma_previsao(self):
        """Ela MEDE o defeito. Se decidisse, a baseline seria dela."""
        import ast
        arvore = ast.parse(self.fonte)
        for nome in ("substring_falso", "_so_substring",
                     "decisoes_assentes_em_falso_casamento"):
            fn = next(n for n in ast.walk(arvore)
                      if isinstance(n, ast.FunctionDef) and n.name == nome)
            corpo = ast.unparse(fn)
            self.assertNotIn("RAW_OUTPUT'] =", corpo)
            self.assertNotIn("NORMALIZED_EVAL_BUCKET'] =", corpo)

    def test_a_traducao_de_campos_e_do_dono_dela(self):
        """O mapa de nomes vive em `coleta/ingresso.py`, e nao aqui."""
        self.assertIn("ing.para_a_porta(", self.fonte)
        self.assertNotIn('"SOURCE_ID": "source_id"', self.fonte)

    def test_o_adapter_nao_infere_fonte_nem_fabrica_id(self):
        self.assertNotIn("def fonte_de", self.fonte)
        self.assertNotIn("uuid", self.fonte.lower())
        self.assertEqual(_art()["THIN_ADAPTER_HAS_SEMANTIC_LOGIC"], "NO")

    def test_o_texto_vai_inteiro_e_nao_um_trecho_escolhido(self):
        """Escolher trecho por conteudo seria escolher a resposta."""
        self.assertIn('return f.read().decode("utf-8", "replace")', self.fonte)
        self.assertNotIn("[:3600]", self.fonte)


class OGabaritoNaoEToctado(unittest.TestCase):

    def test_o_sha_do_gabarito_e_o_do_ficheiro(self):
        caminho = os.path.join(RAIZ, m.GABARITO)
        with open(caminho, "rb") as f:
            esperado = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(m.sha256_do_ficheiro(m.GABARITO), esperado)
        self.assertEqual(_art()["GROUND_TRUTH"]["SHA256"], esperado)

    def test_correr_a_medicao_nao_muda_o_gabarito(self):
        antes = m.sha256_do_ficheiro(m.GABARITO)
        m.medir_tudo()
        self.assertEqual(m.sha256_do_ficheiro(m.GABARITO), antes)

    def test_um_gabarito_com_rotulo_fora_do_binario_nao_passa(self):
        doc, gt = m.carregar_gabarito()
        sujo = copy.deepcopy(doc)
        sujo["GROUND_TRUTH"][0]["LABEL"] = "T3_AMBIGUO"
        with self.assertRaises(m.MedicaoInvalida):
            _validar(sujo)

    def test_um_gabarito_com_35_itens_nao_passa(self):
        doc, _ = m.carregar_gabarito()
        sujo = copy.deepcopy(doc)
        sujo["GROUND_TRUTH"].pop()
        with self.assertRaises(m.MedicaoInvalida):
            _validar(sujo)

    def test_um_sha_duplicado_nao_passa(self):
        doc, _ = m.carregar_gabarito()
        sujo = copy.deepcopy(doc)
        sujo["GROUND_TRUTH"][1]["DOC_SHA256"] = \
            sujo["GROUND_TRUTH"][0]["DOC_SHA256"]
        with self.assertRaises(m.MedicaoInvalida):
            _validar(sujo)

    def test_os_17_excluidos_nao_entram_no_score(self):
        a = _art()
        self.assertEqual(a["GROUND_TRUTH"]["EXCLUIDOS_NAO_ENTRAM_NO_SCORE"], 17)
        self.assertEqual(a["DOCUMENT_PLANE"]["TOTAL"], 36)
        self.assertEqual(len(a["CASES"]), 36)


def _validar(doc):
    """A mesma conferencia de `carregar_gabarito`, sobre um doc em memoria."""
    guardado = m._json
    try:
        m._json = lambda _c: doc
        return m.carregar_gabarito()
    finally:
        m._json = guardado


class OsEstadosNaoForamEsmagados(unittest.TestCase):

    def test_o_vocabulario_vem_do_runtime_e_nao_desta_prova(self):
        self.assertEqual(m.estados_do_runtime(), list(adm.RESULTADOS))
        self.assertEqual(_art()["RUNTIME_OUTPUT_STATES"], list(adm.RESULTADOS))

    def test_cada_estado_tem_o_seu_proprio_balde(self):
        baldes = [m.BALDE[e] for e in adm.RESULTADOS]
        self.assertEqual(len(set(baldes)), len(adm.RESULTADOS))

    def test_abstencao_nao_e_negativo_nem_erro(self):
        self.assertEqual(m.BALDE[adm.NAO_SEI], m.ABSTAIN)
        self.assertNotEqual(m.BALDE[adm.NAO_SEI], m.BALDE[adm.NAO])
        self.assertNotEqual(m.BALDE[adm.NAO_SEI], m.BALDE[adm.ERRO])

    def test_nao_se_aplica_e_estado_proprio(self):
        self.assertEqual(m.BALDE[adm.NAO_SE_APLICA], m.NOT_APPLICABLE)

    def test_so_binarios_entram_na_matriz(self):
        self.assertEqual(set(m.BINARIOS), {m.PRED_POSITIVE, m.PRED_NEGATIVE})

    def test_um_estado_novo_no_runtime_nao_e_engolido(self):
        with self.assertRaises(m.MedicaoInvalida):
            m.balde_de("UM_ESTADO_QUE_A_PROVA_NAO_CONHECE")


class AMatrizFecha(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a = _art()
        cls.d = cls.a["DOCUMENT_PLANE"]

    def test_todos_os_36_foram_medidos(self):
        self.assertEqual(self.d["TOTAL"], 36)
        self.assertEqual(len({c["DOC_SHA256"] for c in self.a["CASES"]}), 36)

    def test_a_matriz_soma_36(self):
        d = self.d
        self.assertEqual(d["TP"] + d["TN"] + d["FP"] + d["FN"]
                         + d["ABSTAIN"] + d["NOT_APPLICABLE"] + d["ERROR"], 36)

    def test_uma_matriz_que_nao_soma_e_recusada(self):
        casos = copy.deepcopy(self.a["CASES"])
        casos.append(dict(casos[0], DOC_SHA256="x",
                          NORMALIZED_EVAL_BUCKET="UM_BALDE_INVENTADO"))
        with self.assertRaises(m.MedicaoInvalida):
            m.matriz(casos)

    # ⚠️ A PRIMEIRA VERSAO DESTE TESTE SO EXIGIA `EFFECTIVE <= CONDITIONAL`.
    # Uma mutacao que calculava AS DUAS sobre as decisoes binarias passava —
    # ficavam iguais, e `<=` continuava verdadeiro. A cobertura baixa
    # desaparecia e o teste aplaudia.
    #
    #     UMA RELACAO QUE A MUTACAO TAMBEM SATISFAZ
    #     NAO DISTINGUE O CERTO DO ERRADO.
    #
    # Agora exige-se a FORMULA: cada acuracia contra o seu denominador.
    def test_cada_acuracia_vem_do_seu_denominador(self):
        d = self.d
        self.assertAlmostEqual(d["EFFECTIVE_ACCURACY"] * d["TOTAL"],
                               d["CORRECT_BINARY"], places=2)
        self.assertAlmostEqual(d["CONDITIONAL_ACCURACY"] * d["BINARY_DECISIONS"],
                               d["CORRECT_BINARY"], places=2)
        self.assertAlmostEqual(d["DECISION_COVERAGE"] * d["TOTAL"],
                               d["BINARY_DECISIONS"], places=2)

    def test_com_cobertura_parcial_as_duas_acuracias_diferem(self):
        """Se fossem iguais com cobertura < 1, uma delas estava errada."""
        d = self.d
        self.assertLess(d["BINARY_DECISIONS"], d["TOTAL"],
                        "sem abstencao este teste nao provaria nada")
        self.assertLess(d["EFFECTIVE_ACCURACY"], d["CONDITIONAL_ACCURACY"])

    def test_denominador_zero_e_nao_sei_e_nao_zero(self):
        vazio = m.matriz([])
        self.assertEqual(vazio["CONDITIONAL_ACCURACY"], "NAO SEI")
        self.assertEqual(vazio["PRECISION_T3"], "NAO SEI")

    def test_todo_erro_esta_publicado(self):
        a = self.a
        errados = [c for c in a["CASES"] if c["CORRECT"] == "NO"]
        self.assertEqual(len(errados), a["DOCUMENT_PLANE"]["FP"]
                         + a["DOCUMENT_PLANE"]["FN"])
        for c in errados:
            for campo in ("DOC_SHA256", "ITEM_ID", "PUBLISHER",
                          "HUMAN_LABEL", "RAW_OUTPUT"):
                self.assertTrue(c[campo], campo)

    def test_o_relatorio_impresso_nomeia_cada_erro(self):
        """O JSON ter o erro nao chega: quem le o terminal tem de o ver.

        A primeira versao desta suite so olhava para o artefato, e uma mutacao
        que filtrava os erros do relatorio passava — o numero ficava certo e o
        leitor nunca via qual documento tinha falhado.
        """
        import contextlib
        import io
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            m.main()
        texto = saida.getvalue()
        # ⚠️ E PRECISO OLHAR PARA A SECCAO DOS ERROS, E NAO PARA A PAGINA.
        # A primeira versao procurava o ITEM_ID no relatorio inteiro — e ele
        # aparece tambem nas sondas de red team. A mutacao que apagava a lista
        # de erros passava, porque o id continuava algures no ecra.
        #
        #     PROCURAR NO SITIO ERRADO E ENCONTRAR
        #     E PIOR DO QUE NAO PROCURAR.
        inicio = texto.index("OS ERROS, UM A UM")
        fim = texto.index("QUEBRAS POR GRUPO")
        seccao = texto[inicio:fim]
        errados = [c for c in self.a["CASES"] if c["CORRECT"] == "NO"]
        self.assertTrue(errados, "sem erros este teste nao provaria nada")
        for c in errados:
            self.assertIn(c["ITEM_ID"][:38], seccao, c["ITEM_ID"])
            self.assertIn(c["RAW_OUTPUT"], seccao)

    def test_toda_abstencao_esta_publicada(self):
        a = self.a
        ab = [c for c in a["CASES"]
              if c["NORMALIZED_EVAL_BUCKET"] == m.ABSTAIN]
        self.assertEqual(len(ab), a["DOCUMENT_PLANE"]["ABSTAIN"])

    def test_os_dois_planos_de_entrada_estao_ambos_publicados(self):
        p = self.a["OS_DOIS_PLANOS_DE_ENTRADA"]
        self.assertIn("CONTRATO", p)
        self.assertIn("LINHAGEM", p)
        self.assertEqual(p["BASELINE_TEMATICA"], m.LINHAGEM)


class OAgrupamentoJaExistiaAntesDoScore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a = _art()
        cls.o = cls.a["OBSERVATION_PLANE"]

    def test_o_agrupamento_vem_do_gabarito_e_nao_das_previsoes(self):
        self.assertEqual(self.a["CANONICAL_OBSERVATION_GROUPING_FOUND"], "YES")
        self.assertIn(m.GABARITO, self.a["GROUPING_SOURCE"])
        with open(os.path.join(RAIZ, "provas",
                               "medir_admission_t3_atual.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        # O agrupador nao pode sequer ver uma previsao.
        inicio = fonte.index("def agrupamento_canonico")
        fim = fonte.index("GROUP_PASS, GROUP_FAIL")
        corpo = fonte[inicio:fim]
        for proibido in ("RAW_OUTPUT", "NORMALIZED_EVAL_BUCKET", "CORRECT"):
            self.assertNotIn(proibido, corpo, proibido)

    def test_sao_31_grupos_11_positivos_20_negativos(self):
        self.assertEqual(self.o["GROUP_TOTAL"], 31)
        self.assertEqual(self.o["GROUP_POSITIVE"], 11)
        self.assertEqual(self.o["GROUP_NEGATIVE"], 20)

    def test_os_estados_de_grupo_somam_o_total(self):
        o = self.o
        self.assertEqual(o["GROUP_PASS"] + o["GROUP_FAIL"]
                         + o["GROUP_NOT_DECIDED"], o["GROUP_TOTAL"])

    def test_um_grupo_so_passa_se_todos_acertarem(self):
        """Sem voto de maioria, sem «a melhor edicao»."""
        grupos = {"a": "g", "b": "g"}
        casos = [
            {"DOC_SHA256": "a", "ITEM_ID": "a", "HUMAN_LABEL": "T3_SIM",
             "NORMALIZED_EVAL_BUCKET": m.PRED_POSITIVE, "CORRECT": "YES",
             "RAW_OUTPUT": adm.SIM},
            {"DOC_SHA256": "b", "ITEM_ID": "b", "HUMAN_LABEL": "T3_SIM",
             "NORMALIZED_EVAL_BUCKET": m.PRED_NEGATIVE, "CORRECT": "NO",
             "RAW_OUTPUT": adm.NAO},
        ]
        r = m.por_observacao(casos, grupos)
        self.assertEqual(r["GROUP_FAIL"], 1)
        self.assertEqual(r["GROUP_PASS"], 0)

    def test_uma_abstencao_no_grupo_nao_vira_acerto(self):
        grupos = {"a": "g", "b": "g"}
        casos = [
            {"DOC_SHA256": "a", "ITEM_ID": "a", "HUMAN_LABEL": "T3_SIM",
             "NORMALIZED_EVAL_BUCKET": m.PRED_POSITIVE, "CORRECT": "YES",
             "RAW_OUTPUT": adm.SIM},
            {"DOC_SHA256": "b", "ITEM_ID": "b", "HUMAN_LABEL": "T3_SIM",
             "NORMALIZED_EVAL_BUCKET": m.ABSTAIN, "CORRECT": "NOT_DECIDED",
             "RAW_OUTPUT": adm.NAO_SEI},
        ]
        r = m.por_observacao(casos, grupos)
        self.assertEqual(r["GROUP_NOT_DECIDED"], 1)
        self.assertEqual(r["GROUP_PASS"], 0)

    def test_um_grupo_com_gabarito_misto_nao_e_colapsado(self):
        grupos = {"a": "g", "b": "g"}
        casos = [
            {"DOC_SHA256": "a", "ITEM_ID": "a", "HUMAN_LABEL": "T3_SIM",
             "NORMALIZED_EVAL_BUCKET": m.PRED_POSITIVE, "CORRECT": "YES",
             "RAW_OUTPUT": adm.SIM},
            {"DOC_SHA256": "b", "ITEM_ID": "b", "HUMAN_LABEL": "T3_NAO",
             "NORMALIZED_EVAL_BUCKET": m.PRED_NEGATIVE, "CORRECT": "YES",
             "RAW_OUTPUT": adm.NAO},
        ]
        r = m.por_observacao(casos, grupos)
        self.assertEqual(r["GROUP_TOTAL"], 0)
        self.assertEqual(len(r["MIXED_GROUND_TRUTH_GROUP"]), 1)

    def test_o_gabarito_desta_arvore_nao_tem_grupo_misto(self):
        self.assertEqual(len(self.o["MIXED_GROUND_TRUTH_GROUP"]), 0)

    def test_a_estabilidade_entre_edicoes_foi_medida(self):
        o = self.o
        self.assertEqual(o["SAME_GROUP_SAME_PREDICTION"]
                         + o["SAME_GROUP_MIXED_PREDICTIONS"],
                         o["GRUPOS_COM_MAIS_DE_UM"])


class OSubstringEOAcertoPorAcidente(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a = _art()

    def test_o_defeito_historico_foi_medido_e_nao_consertado(self):
        self.assertIn(self.a["SUBSTRING_FALSE_MATCH_STILL_EXISTS"],
                      ("YES", "NO"))
        # A porta continua a casar por substring — esta missao mede, nao muda.
        with open(os.path.join(RAIZ, "admissao", "admissao.py"),
                  encoding="utf-8") as f:
            self.assertIn("p.lower() in texto", f.read())

    def test_lancio_dentro_de_bilancio_continua_a_acender(self):
        achados = [s for s in self.a["SUBSTRING_FALSE_MATCHES"]
                   if s["TERMO"] == "lancio"]
        self.assertTrue(achados, "o caso historico devia estar medido")
        self.assertTrue(all(s["DENTRO_DE"] == "bilancio" for s in achados))

    def test_uma_decisao_assente_so_em_casamento_falso_esta_marcada(self):
        acidente = self.a["DECISIONS_RESTING_ONLY_ON_FALSE_MATCH"]
        self.assertTrue(acidente)
        for x in acidente:
            self.assertIn(x["RAW_OUTPUT"], (adm.SIM, adm.NAO))

    def test_o_acerto_por_acidente_foi_contado(self):
        self.assertEqual(
            self.a["CORRECT_BY_ACCIDENT"],
            sum(1 for x in self.a["DECISIONS_RESTING_ONLY_ON_FALSE_MATCH"]
                if x["CORRECT"] == "YES"))

    def test_a_sonda_detecta_a_palavra_so_dentro_de_outra(self):
        self.assertTrue(m._so_substring("lancio", "il bilancio fitosanitario"))
        self.assertFalse(m._so_substring("lancio", "lancio del prodotto"))
        self.assertFalse(m._so_substring("lancio", "bilancio e lancio"))


class ANaoContaminacaoFoiProvada(unittest.TestCase):

    def test_o_mecanismo_e_mais_velho_do_que_o_gabarito(self):
        la = _art()["LEAKAGE_AUDIT"]
        self.assertEqual(la["GROUND_TRUTH_AUTHORITY"], "HUMAN_VERIFIED")
        self.assertEqual(
            la["CURRENT_ADMISSION_NEVER_SAW_GROUND_TRUTH_DURING_ITS_DESIGN"],
            "YES")
        self.assertLess(la["MECANISMO_MEXIDO_PELA_ULTIMA_VEZ_EM"],
                        la["GABARITO_COMMITADO_EM"])

    def test_sem_datas_a_independencia_e_nao_sei_e_nao_yes(self):
        """Nao se inventa independencia historica."""
        guardado = m._git
        try:
            m._git = lambda *a: ""
            doc, _ = m.carregar_gabarito()
            r = m.auditoria_de_vazamento(doc)
            self.assertEqual(
                r["CURRENT_ADMISSION_NEVER_SAW_GROUND_TRUTH_DURING_ITS_DESIGN"],
                "NAO SEI")
        finally:
            m._git = guardado

    def test_a_impressao_digital_identifica_esta_medicao(self):
        a = _art()
        self.assertEqual(len(a["FIRST_VALID_BASELINE_FINGERPRINT"]), 64)
        self.assertEqual(m.impressao_digital(a),
                         a["FIRST_VALID_BASELINE_FINGERPRINT"])

    def test_uma_previsao_diferente_muda_a_impressao(self):
        a = copy.deepcopy(_art())
        a["CASES"][0]["RAW_OUTPUT"] = adm.NAO_SE_APLICA
        self.assertNotEqual(m.impressao_digital(a),
                            _art()["FIRST_VALID_BASELINE_FINGERPRINT"])


class OVereditoNaoFoiInventado(unittest.TestCase):

    def test_nao_ha_gate_previo_e_por_isso_nao_se_aprova(self):
        a = _art()
        self.assertEqual(a["PERFORMANCE_GATE_PREDEFINED"], "NO")
        self.assertEqual(a["CURRENT_MECHANISM_ACCEPTABLE"], "NOT_DECIDED")

    def test_o_artefato_nao_propoe_substituto(self):
        a = _art()
        self.assertEqual(a["REPLACEMENT_PROPOSED"], "NO")
        bruto = json.dumps(a, ensure_ascii=False).upper()
        for proibido in ("EMBEDDING", "FINE-TUNING", "DEVIA USAR",
                         "RECOMENDA-SE TROCAR"):
            self.assertNotIn(proibido, bruto, proibido)

    def test_a_missao_nao_mexeu_na_porta(self):
        a = _art()
        self.assertEqual(a["ADMISSION_CHANGED"], "NO")
        self.assertEqual(a["KEYWORDS_CHANGED"], "NO")
        self.assertEqual(a["CLASSIFIER_BUILT"], "NO")


if __name__ == "__main__":
    unittest.main()
