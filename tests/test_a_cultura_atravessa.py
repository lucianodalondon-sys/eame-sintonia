# -*- coding: utf-8 -*-
"""A CULTURA ATRAVESSA — as provas da cirurgia C-CROP-E2E-V1.

Sete regressões que a missão exigiu, e as provas do executor de secções sobre
os boletins que o repositório já guarda (edições anteriores das mesmas três
fontes: os bytes reais dos itens da Sala vivem fora do Git).

    1. UNKNOWN não vira CROP
    2. PUBLISHED_AT não vira FACT_TIME
    3. SOURCE_LOCATION não vira FACT_LOCATION
    4. rederivação não duplica observação
    5. mesma evidência não vira duas evidências independentes
    6. CROP errado bloqueia autorização
    7. CROP correto realmente altera o resultado do gate

    MENÇÃO NÃO É CHAVE. CABEÇALHO É.
"""
import json
import os
import shutil
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import executor_secoes_por_cultura as S  # noqa: E402
import executor_texto_de_pdf as ex  # noqa: E402
import ingresso as ing  # noqa: E402
import regua_italia as regua  # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira  # noqa: E402
from guarda import preservar_derivado as pd  # noqa: E402

sys.path.insert(0, os.path.join(RAIZ, "provas"))
import o_piloto_da_sala as piloto  # noqa: E402

FIXTURES = {
    "SALERNO": os.path.join(RAIZ, "data", "collection-store", "italy", "IT-T3-002",
                            "CAMPANIA_SA_02-09-2026", "v1_0c2723e66201", "SA-02-09.pdf"),
    "APOL": os.path.join(RAIZ, "data", "collection-store", "italy", "IT-T3-010",
                         "APOL_2026_N9_BR-COLLINA", "v1_59da05274359",
                         "Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf"),
    "ARIF": os.path.join(RAIZ, "data", "collection-store", "italy", "IT-T3-008",
                         "ARIF_SETTIMANALE_2026_N36", "v1_e612807928b5",
                         "Notiziario_Agrometeorologico_N36_02-09-2026.pdf"),
}
CAPTURED_AT = "2026-09-18T13:07:10.733Z"

SALERNO_SINTETICO = (
    "BOLLETTINO FITOSANITARIO\n\nCOLTURA N° Comune 1 Eboli\n\nVITE UTM\nLocalità\n\n"
    "Azienda\n\nCONSIGLI DI DIFESA FITOSANITARIA\n"
    "• PERONOSPORA Chimico: intervenire con azoxystrobin.\n\n"
    "COLTURA\n\nN° Comune\n\n1\n\nSarno\n\nOLIVO UTM\nLocalità\n\n"
    "CONSIGLI DI DIFESA FITOSANITARIA\n• MOSCA Chimico: azoxystrobin non ammesso.\n"
)


def _tem_pdftotext():
    return ex.ha_ferramenta()


class OExecutorNaoRoubaAPorta(unittest.TestCase):
    def test_o_pdf_continua_a_ser_aberto_pelo_texto_de_pdf(self):
        self.assertEqual(ing.executor_para("application/pdf").EXECUTOR_ID, "texto-de-pdf")

    def test_o_kind_vem_do_vocabulario_fechado_da_022(self):
        self.assertEqual(S.KIND, "TABLE_EXTRACTION")
        self.assertEqual(S.CAPACIDADE["NETWORK_REQUIRED"], "NO")
        self.assertEqual(S.CAPACIDADE["OCR"], "NO")


class UmMencaoNaoViraCrop(unittest.TestCase):
    """1 · UNKNOWN não vira CROP."""

    def test_olivo_no_corpo_e_candidato_e_nao_chave(self):
        texto = ("Situazione Fenologica:\nAccrescimento frutto.\n"
                 "Situazione Fitosanitaria:\nPresenza di mosca dell'olivo nell'oliveto; "
                 "trattamento fitosanitario consigliato.\n")
        r = S.seccionar(texto)
        self.assertEqual(r["RESUMO"]["EXPLICIT"], 0)
        s = [x for x in r["SECOES"] if x["KIND"] == S.CONTEXT_BLOCK][0]
        self.assertEqual(s["STATUS"], S.CONTEXT_ONLY)
        self.assertIsNone(s["CROP_EXPLICIT"])
        self.assertIn("OLIVO", [c["CROP"] for c in s["CROP_CONTEXT"]["CANDIDATES"]])
        self.assertEqual(s["CERTEZA"], S.OBSERVADO_NO_CORPO)

    def test_texto_sem_cultura_fica_unknown_e_nao_vazio(self):
        r = S.seccionar("Situazione Fenologica:\nMaturazione.\nProgramma di Difesa:\nNessuno.\n")
        self.assertEqual(r["RESUMO"]["EXPLICIT"], 0)
        self.assertEqual(r["RESUMO"]["CONTEXT_ONLY"], 0)
        self.assertGreaterEqual(r["RESUMO"]["UNKNOWN"], 1)
        self.assertEqual(r["SECOES"][0]["CERTEZA"], S.NAO_SEI)

    def test_o_gate_com_cultura_desconhecida_nao_decide(self):
        self.assertEqual(piloto.gate_de_cultura(None, ["OLIVO"]), piloto.CROP_UNKNOWN)
        self.assertEqual(piloto.gate_de_cultura("", ["OLIVO"]), piloto.CROP_UNKNOWN)

    def test_a_secao_context_only_sai_not_possible_no_crossing(self):
        item = {"source_id": "IT-T3-008", "run_id": "R", "ordem": 0,
                "raw_observation_id": 9, "texto": "x"}
        secoes = {"SECOES": [{
            "ORDEM": 0, "KIND": S.CONTEXT_BLOCK, "STATUS": S.CONTEXT_ONLY,
            "CROP_EXPLICIT": None, "CROP_TERM_AS_WRITTEN": None,
            "CROP_CONTEXT": {"HEADER_TEXT": "", "HEADER_WINDOW": "",
                             "CANDIDATES": [{"CROP": "OLIVO", "TERM": "olivo", "N": 2}],
                             "ANCORA_AGRICOLA_NO_CORPO": True},
            "EVIDENCE_ANCHOR": {}, "PRECISION": "BODY_MENTION",
            "CERTEZA": S.OBSERVADO_NO_CORPO, "CHARS": 10,
            "TEXTO": "mosca dell'olivo: azoxystrobin"}]}
        usos = [{"REGISTRATION_NUMBER": "R1", "CROP_ON_LABEL": "OLIVO"}]
        vivos = [{"num_registrazione": "R1", "produto": "P"}]
        xs = piloto.cruzar([item], {"AZOXYSTROBIN": {"R1"}}, usos, vivos,
                           {("R", 0): secoes})
        self.assertEqual(len(xs), 1)
        self.assertEqual(xs[0]["CROSSING_STATE"], piloto.NOT_POSSIBLE)
        self.assertEqual(xs[0]["CROP_GATE"], piloto.CROP_UNKNOWN)
        self.assertIn("CROP", xs[0]["JOIN_KEYS_MISSING"])


class OCabecalhoDeclaraECorpoNao(unittest.TestCase):
    def test_coltura_seguida_da_cultura_e_explicit(self):
        r = S.seccionar(SALERNO_SINTETICO)
        exp = [s for s in r["SECOES"] if s["STATUS"] == S.EXPLICIT]
        self.assertEqual([s["CROP_EXPLICIT"] for s in exp], ["VITE", "OLIVO"])
        self.assertEqual(exp[0]["CROP_TERM_AS_WRITTEN"], "VITE")
        self.assertEqual(exp[0]["PRECISION"], S.SECTION_HEADER)
        self.assertEqual(exp[0]["CERTEZA"], S.OBSERVADO_NO_CABECALHO)
        # a âncora aponta para dentro do texto, e para o bloco certo
        a = exp[1]["EVIDENCE_ANCHOR"]
        bloco = SALERNO_SINTETICO[a["CHAR_START"]:a["CHAR_END"]]
        self.assertTrue(bloco.startswith("COLTURA"))
        self.assertIn("OLIVO UTM", bloco)
        self.assertNotIn("VITE UTM", bloco)

    def test_o_titulo_do_disciplinare_nomeia_a_cultura(self):
        r = S.seccionar("Difesa integrata Olivo Puglia 2026\nAVVERSITA'\nAzoxystrobin\n")
        s = r["SECOES"][0]
        self.assertEqual((s["KIND"], s["STATUS"], s["CROP_EXPLICIT"]),
                         (S.TABLE_TITLE, S.EXPLICIT, "OLIVO"))

    def test_difesa_integrata_em_prosa_nao_e_titulo(self):
        r = S.seccionar("informazioni sull'applicazione della\ndifesa integrata\nN 27\n")
        self.assertEqual([s["KIND"] for s in r["SECOES"]], [S.PREAMBLE])

    def test_uma_comuna_parecida_com_cultura_nao_vira_cultura(self):
        # «Viterbo» começa por «vite»; no cabeçalho exige-se palavra inteira.
        # No corpo, a régua casa por prefixo e conta com a âncora — e aqui a
        # âncora é a própria palavra «COLTURA». Fica CANDIDATO, com risco
        # residual declarado pela régua; o que não pode acontecer é ser CHAVE.
        r = S.seccionar("COLTURA Comune\nViterbo\nAzienda\n")
        self.assertNotEqual(r["SECOES"][0]["STATUS"], S.EXPLICIT)
        self.assertIsNone(r["SECOES"][0]["CROP_EXPLICIT"])

    def test_os_bytes_sao_deterministicos(self):
        a = S.bytes_do_artefato(S.seccionar(SALERNO_SINTETICO))
        b = S.bytes_do_artefato(S.seccionar(SALERNO_SINTETICO))
        self.assertEqual(a, b)
        self.assertNotIn(b"\r\n", a)

    def test_o_vocabulario_e_o_da_regua_e_nao_um_segundo(self):
        chaves = {k for k, _rx, _a in regua.CULTURAS}
        for c in ("ACTINIDIA", "CILIEGIO", "FRAGOLA", "NOCCIOLO", "NOCE", "CASTAGNO",
                  "MELANZANA", "OLIVO", "VITE", "AGRUMI", "PESCO", "POMODORO"):
            self.assertIn(c, chaves)
        r = S.seccionar(SALERNO_SINTETICO)
        for s in r["SECOES"]:
            if s["CROP_EXPLICIT"]:
                self.assertIn(s["CROP_EXPLICIT"], chaves)


@unittest.skipUnless(_tem_pdftotext(), "pdftotext ausente nesta máquina")
class OsBoletinsDoRepositorio(unittest.TestCase):
    """As edições anteriores das MESMAS três fontes, guardadas no Git. O padrão
    tem de ser o mesmo dos bytes reais da Sala — e é: medido na missão."""

    def _sec(self, nome):
        if not os.path.isfile(FIXTURES[nome]):
            self.skipTest("fixture %s ausente" % nome)
        s, estado, _e, _m = S.extrair(FIXTURES[nome])
        self.assertIsNotNone(s, estado)
        return s

    def test_salerno_declara_a_cultura_por_coluna(self):
        s = self._sec("SALERNO")
        for c in ("ACTINIDIA", "AGRUMI", "CILIEGIO", "VITE", "FRAGOLA", "NOCCIOLO",
                  "OLIVO", "PESCO", "POMODORO"):
            self.assertIn(c, s["RESUMO"]["CROPS_EXPLICIT"])
        self.assertTrue(all(x["KIND"] == S.SECTION_HEADER for x in s["SECOES"]
                            if x["STATUS"] == S.EXPLICIT))

    def test_apol_declara_a_cultura_no_titulo_da_tabela(self):
        s = self._sec("APOL")
        self.assertEqual(s["RESUMO"]["CROPS_EXPLICIT"], ["OLIVO"])
        titulos = [x for x in s["SECOES"] if x["KIND"] == S.TABLE_TITLE]
        self.assertTrue(titulos)
        self.assertTrue(all(x["CROP_EXPLICIT"] == "OLIVO" for x in titulos))
        # o boletim de monitorização nomeia a PRAGA, não a cultura: contexto
        self.assertEqual(s["SECOES"][0]["STATUS"], S.CONTEXT_ONLY)

    def test_arif_nao_nomeia_cultura_na_camada_de_texto(self):
        s = self._sec("ARIF")
        self.assertEqual(s["RESUMO"]["EXPLICIT"], 0)
        self.assertGreater(s["RESUMO"]["CONTEXT_ONLY"], 0)
        self.assertEqual(s["RESUMO"]["CROPS_EXPLICIT"], [])


class OQueNaoSeMistura(unittest.TestCase):
    """2 · PUBLISHED_AT não vira FACT_TIME. 3 · SOURCE_LOCATION não vira
    FACT_LOCATION. A derivação de secções não fala de tempo nem de lugar, e o
    crossing continua a exigir FACT_TIME e REGION mesmo com a cultura certa."""

    def test_a_derivacao_nao_emite_tempo_nem_lugar(self):
        r = S.seccionar(SALERNO_SINTETICO)
        chaves = set(json.dumps(r).upper().split('"'))
        for proibida in ("FACT_TIME", "PUBLISHED_AT", "FACT_LOCATION", "SOURCE_LOCATION"):
            self.assertNotIn(proibida, chaves)

    def test_com_cultura_autorizada_fact_time_e_region_continuam_em_falta(self):
        item = {"source_id": "IT-T3-002", "run_id": "R", "ordem": 0,
                "raw_observation_id": 7, "texto": "x",
                "published_at": "2026-09-16", "source_location": "Salerno"}
        secoes = S.seccionar(SALERNO_SINTETICO)
        usos = [{"REGISTRATION_NUMBER": "R1", "CROP_ON_LABEL": "VITE"}]
        vivos = [{"num_registrazione": "R1", "produto": "P"}]
        xs = piloto.cruzar([item], {"AZOXYSTROBIN": {"R1"}}, usos, vivos,
                           {("R", 0): secoes})
        passou = [x for x in xs if x["CROSSING_STATE"] == piloto.CROP_GATE_PASSED]
        self.assertTrue(passou)
        for x in passou:
            self.assertIn("FACT_TIME", x["JOIN_KEYS_MISSING"])
            self.assertIn("REGION", x["JOIN_KEYS_MISSING"])
            self.assertNotIn("2026-09-16", json.dumps(x))
            self.assertNotIn("Salerno", json.dumps(x["JOIN_KEYS_PRESENT"]))


class ARederivacaoNaoDuplica(unittest.TestCase):
    """4 · rederivação não duplica observação. 5 · mesma evidência não vira
    duas evidências. Medido num banco real (SQLite descartável, com as travas
    da 022), pelo DONO da escrita — não por um dicionário."""

    def setUp(self):
        self.banco = MemoriaDescartavel()
        self.armazem = ArmazemDeMentira()
        self.addCleanup(self.banco.fechar)
        self.pai = self._raw("IT-W-1", "IT/x/DOCUMENT/pai.pdf", "a" * 64)

    def _raw(self, run_id, caminho, sha):
        self.banco.aplicar(
            "insert into public.collection_run (run_id, platform, started_at, "
            "rule_version, source_country) values ('%s','t','%s','1','IT') "
            "on conflict (run_id) do nothing;" % (run_id, CAPTURED_AT))
        self.banco.aplicar(
            "insert into public.storage_object (storage_path, media_type, bytes, sha256) "
            "values ('%s','application/pdf',100,'%s') on conflict (storage_path) do nothing;"
            % (caminho, sha))
        self.banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, bytes, "
            "sha256, captured_at, storage_object_id, identity_state, source_id, "
            "document_key, document_key_basis) select '%s','%s','application/pdf',100,"
            "'%s','%s', o.id, 'FORWARD_IDENTIFIED','IT-T3-002','DOC:%s','SOURCE_DOCUMENT_ID' "
            "from public.storage_object o where o.storage_path = '%s';"
            % (run_id, caminho, sha, CAPTURED_AT, sha[:12], caminho))
        return int(self.banco.con.execute(
            "select id from raw_asset where storage_path = ?", (caminho,)).fetchone()[0])

    def _derivar(self, raw_id):
        # O executor entrega receita + bytes; o dono escreve. Aqui salta-se o
        # pdftotext (é o que a classe acima prova) e usa-se o texto sintético.
        dados = S.bytes_do_artefato(S.seccionar(SALERNO_SINTETICO))
        return pd.preservar_derivado(
            {"raw_asset_id": raw_id, "kind": S.KIND, "producer": S.EXECUTOR_ID,
             "producer_version": S.EXECUTOR_VERSION, "pipeline_version": S.PIPELINE_VERSION,
             "parameters": {"REGRA": "secoes-por-cultura"}, "serie_posicao": None,
             "media_type": S.MEDIA_TYPE},
            dados, self.armazem, self.banco, relogio=lambda: CAPTURED_AT)

    def test_rederivar_duas_vezes_da_uma_linha_e_nenhuma_observacao_nova(self):
        antes = self.banco.contar("raw_asset")
        a = self._derivar(self.pai)
        b = self._derivar(self.pai)
        self.assertEqual(a["ESTADO"], pd.INSERTED)
        self.assertEqual(b["ESTADO"], pd.REUSED)
        self.assertEqual(self.banco.contar("raw_asset"), antes)
        self.assertEqual(self.banco.contar("collection_run"), 1)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)
        self.assertEqual(self.armazem.envios, 1)

    def test_a_segunda_captura_dos_mesmos_bytes_reencontra_e_nao_duplica(self):
        gemeo = self._raw("IT-W-2", "IT/x/DOCUMENT/gemeo.pdf", "a" * 64)
        a = self._derivar(self.pai)
        b = self._derivar(gemeo)
        self.assertEqual(a["ESTADO"], pd.INSERTED)
        self.assertEqual(b["ESTADO"], pd.REUSED)
        self.assertEqual(self.banco.contar("derived_artifact"), 1)
        self.assertEqual(self.banco.contar("raw_asset"), 2)   # as duas capturas ficam
        self.assertEqual(int(b["LINHA_EXISTENTE"]["raw_asset_id"]), self.pai)


class OGateDistingue(unittest.TestCase):
    """6 · CROP errado bloqueia. 7 · CROP certo altera o resultado. A mesma
    substância, a mesma referência, só a cultura muda — e o veredito muda."""

    ITEM = {"source_id": "IT-T3-002", "run_id": "R", "ordem": 0,
            "raw_observation_id": 7, "texto": "x"}
    USOS = [{"REGISTRATION_NUMBER": "R1", "CROP_ON_LABEL": "VITE"},
            {"REGISTRATION_NUMBER": "R1", "CROP_ON_LABEL": "POMODORO"}]
    VIVOS = [{"num_registrazione": "R1", "produto": "MIRADOR"}]

    def _estados(self):
        secoes = S.seccionar(SALERNO_SINTETICO)
        xs = piloto.cruzar([self.ITEM], {"AZOXYSTROBIN": {"R1"}}, self.USOS,
                           self.VIVOS, {("R", 0): secoes})
        return {x["CROP_KEY"]: x for x in xs if x["CROP_KEY"]}

    def test_gate_puro(self):
        self.assertEqual(piloto.gate_de_cultura("VITE", ["VITE", "POMODORO"]),
                         piloto.CROP_AUTHORIZED)
        self.assertEqual(piloto.gate_de_cultura("OLIVO", ["VITE", "POMODORO"]),
                         piloto.CROP_NOT_AUTHORIZED)
        self.assertEqual(piloto.gate_de_cultura("GRANO_GEN", ["FRUMENTO"]),
                         piloto.CROP_NOT_AUTHORIZED)   # genérico não é rótulo

    def test_crop_errado_bloqueia(self):
        e = self._estados()
        self.assertEqual(e["OLIVO"]["CROSSING_STATE"], piloto.BLOCKED_BY_CROP)
        self.assertEqual(e["OLIVO"]["CROP_GATE"], piloto.CROP_NOT_AUTHORIZED)

    def test_crop_certo_altera_o_resultado(self):
        e = self._estados()
        self.assertEqual(e["VITE"]["CROSSING_STATE"], piloto.CROP_GATE_PASSED)
        self.assertNotEqual(e["VITE"]["CROSSING_STATE"], e["OLIVO"]["CROSSING_STATE"])
        # e mesmo assim não é oportunidade: faltam REGION e FACT_TIME
        self.assertTrue(e["VITE"]["JOIN_KEYS_MISSING"])

    def test_sem_derivacao_o_comportamento_antigo_continua_fechado(self):
        item = dict(self.ITEM, texto="VITE azoxystrobin peronospora")
        xs = piloto.cruzar([item], {"AZOXYSTROBIN": {"R1"}}, self.USOS, self.VIVOS, {})
        self.assertEqual({x["CROSSING_STATE"] for x in xs}, {piloto.NOT_POSSIBLE})

    def test_medir_crop_so_e_present_com_cabecalho(self):
        item = dict(self.ITEM, texto="mosca dell'olivo")
        self.assertEqual(piloto.medir_crop(item, None)[0], "LOST_IN_DERIVATION")
        self.assertEqual(piloto.medir_crop(item, S.seccionar(SALERNO_SINTETICO))[0],
                         "PRESENT")
        so_contexto = S.seccionar("Situazione Fenologica:\nmosca dell'olivo nell'oliveto\n")
        self.assertEqual(piloto.medir_crop(item, so_contexto)[0], "UNKNOWN_IN_DERIVED")


@unittest.skipUnless(os.path.isfile(piloto.USOS) and os.path.isfile(piloto.PORTFOLIO),
                     "referência ADAMA ausente")
class AContraprovaComORotuloReal(unittest.TestCase):
    """A MESMA substância, o rótulo ADAMA REAL, e só a cultura muda.

    Medido na Sala real: azoxystrobin no disciplinare do olivo → BLOQUEADO,
    porque o rótulo ADAMA não lista OLIVO. A contraprova é a mesma substância
    sob um cabeçalho de cultura que o rótulo real LISTA — e o gate passa. A
    secção é sintética (nenhum boletim da Sala junta azoxystrobin a uma
    cultura autorizada); o rótulo, os registos e os produtos são os reais."""

    @classmethod
    def setUpClass(cls):
        cls.substancias, cls.usos, cls.vivos = piloto.ler_referencia_adama()
        cls.ai = "AZOXYSTROBIN"
        if cls.ai not in cls.substancias:
            raise unittest.SkipTest("azoxystrobin não está no portfólio vivo")
        regs = cls.substancias[cls.ai]
        cls.no_rotulo = sorted({u["CROP_ON_LABEL"] for u in cls.usos
                                if u["REGISTRATION_NUMBER"] in regs})

    def _crossing_para(self, cultura):
        texto = ("COLTURA\n\n%s UTM\nLocalità\n\nCONSIGLI DI DIFESA FITOSANITARIA\n"
                 "• Chimico: azoxystrobin.\n" % cultura)
        item = {"source_id": "IT-T3-002", "run_id": "R", "ordem": 0,
                "raw_observation_id": 7, "texto": texto}
        xs = piloto.cruzar([item], self.substancias, self.usos, self.vivos,
                           {("R", 0): S.seccionar(texto)})
        xs = [x for x in xs if x["ACTIVE_INGREDIENT_OBSERVED"] == self.ai]
        self.assertEqual(len(xs), 1)
        return xs[0]

    def test_o_rotulo_real_nao_lista_olivo_e_lista_vite(self):
        self.assertNotIn("OLIVO", self.no_rotulo)
        self.assertIn("VITE", self.no_rotulo)

    def test_unauthorized_crop_case_olivo_bloqueia(self):
        x = self._crossing_para("OLIVO")
        self.assertEqual(x["CROSSING_STATE"], piloto.BLOCKED_BY_CROP)
        self.assertEqual(x["CROP_GATE"], piloto.CROP_NOT_AUTHORIZED)

    def test_authorized_crop_case_vite_passa_o_gate_e_nao_e_oportunidade(self):
        x = self._crossing_para("VITE")
        self.assertEqual(x["CROSSING_STATE"], piloto.CROP_GATE_PASSED)
        self.assertEqual(x["CROP_GATE"], piloto.CROP_AUTHORIZED)
        self.assertEqual(x["JOIN_KEYS_MISSING"], ["REGION", "FACT_TIME"])

    def test_unknown_crop_case_sem_cabecalho_nao_decide(self):
        texto = "Situazione Fenologica:\nmosca dell'olivo; azoxystrobin.\n"
        item = {"source_id": "IT-T3-008", "run_id": "R", "ordem": 0,
                "raw_observation_id": 36, "texto": texto}
        xs = piloto.cruzar([item], self.substancias, self.usos, self.vivos,
                           {("R", 0): S.seccionar(texto)})
        xs = [x for x in xs if x["ACTIVE_INGREDIENT_OBSERVED"] == self.ai]
        self.assertEqual({x["CROSSING_STATE"] for x in xs}, {piloto.NOT_POSSIBLE})


if __name__ == "__main__":
    unittest.main()
