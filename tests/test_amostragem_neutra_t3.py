# -*- coding: utf-8 -*-
"""O SAMPLING FRAME NAO PODE APRENDER A ESCOLHER PELO ASSUNTO.

A §53 do know-how separou duas contaminacoes, e esta e a segunda:

    LEAKAGE NO ROTULADOR   quem decide o rotulo
    LEAKAGE NO AMOSTRADOR  quem decide QUEM entra na lista

Um frame contaminado nao da erro. Da um numero melhor.

    HUMAN LABEL DOES NOT REPAIR A BIASED SAMPLING FRAME.
"""
import importlib.util
import inspect
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "amostra_t3", os.path.join(RAIZ, "provas", "amostragem_neutra_t3.py"))
am = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(am)

FRAME = os.path.join(RAIZ, am.FRAME)


class AInclusaoNaoOlhaParaOAssunto(unittest.TestCase):
    """A trava central: `sampling_frame()` nao pode ler conteudo nem nome."""

    def test_a_inclusao_so_usa_existencia_extensao_e_legibilidade(self):
        codigo = inspect.getsource(am.sampling_frame)
        for proibido in ("fitosanitar", "agrometeo", "bollettino", "difesa",
                         "monitoraggio", "meteo", "SE_DECLARAM",
                         "PERGUNTAS_DO_UNIVERSO", "territory", "territorio"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, codigo.lower(),
                                 f"a selecao passou a olhar para «{proibido}». "
                                 f"Um frame escolhido pelo sinal que se vai "
                                 f"avaliar devolve esse sinal.")

    def test_a_inclusao_nao_le_o_gabarito_de_t2(self):
        codigo = inspect.getsource(am.sampling_frame)
        self.assertNotIn("gabarito", codigo)
        self.assertNotIn("corpus_com_corpo", codigo)

    def test_a_inclusao_nao_le_o_livro_de_decisoes(self):
        with open(os.path.join(RAIZ, "provas",
                               "amostragem_neutra_t3.py"),
                  encoding="utf-8") as f:
            inteiro = f.read()
        self.assertNotIn("LIVRO-DE-DECISOES", inteiro)


class AUnidadeEODocumentoENaoOCaminho(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.frame = am.sampling_frame()

    def test_documentos_em_dois_caminhos_contam_uma_vez(self):
        multi = [d for d in self.frame if len(d["ALL_PATHS"]) > 1]
        self.assertGreater(len(multi), 0, "a arvore tem documentos duplicados; "
                                          "se isto der zero, a deduplicacao "
                                          "deixou de funcionar")
        shas = [d["DOC_SHA256"] for d in self.frame]
        self.assertEqual(len(shas), len(set(shas)), "o mesmo documento aparece "
                                                    "duas vezes no frame")

    def test_todo_revisavel_tem_corpo_que_existe(self):
        for d in self.frame:
            with self.subTest(doc=d["CANONICAL_PATH"]):
                if d["REVIEWABLE"]:
                    self.assertTrue(
                        os.path.isfile(os.path.join(RAIZ, d["BODY_PATH"])))
                else:
                    self.assertIsNone(d["BODY_PATH"])

    def test_nao_revisavel_e_declarado_e_nao_escondido(self):
        naolegivel = [d for d in self.frame if not d["REVIEWABLE"]]
        self.assertEqual(len(naolegivel), 1,
                         "o numero de documentos sem corpo legivel mudou. "
                         "Isso muda a populacao, e obriga a refazer o frame.")

    def test_nenhum_publicador_e_uma_pasta(self):
        for d in self.frame:
            with self.subTest(doc=d["CANONICAL_PATH"]):
                self.assertNotIn("BOLLETTINI-VPN", d["PUBLISHER"])
                self.assertNotIn("/", d["PUBLISHER"])


class OFrameNaoTemRotulos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(FRAME, encoding="utf-8") as f:
            cls.disco = json.load(f)

    def test_o_ficheiro_declara_zero_rotulos(self):
        self.assertEqual(self.disco["HUMAN_LABELS_ADDED"], 0)
        self.assertEqual(self.disco["MACHINE_LABELS_ADDED"], 0)

    def test_nenhum_campo_de_documento_e_um_rotulo(self):
        permitidos = {"DOC_SHA256", "CANONICAL_PATH", "ALL_PATHS", "BODY_PATH",
                      "REVIEWABLE", "PUBLISHER", "SOURCE_ID",
                      "DOCUMENT_FAMILY", "RAW_FORMAT", "IN_CURRENT_PACKET"}
        for d in self.disco["DOCUMENTOS"]:
            with self.subTest(doc=d["CANONICAL_PATH"]):
                self.assertEqual(set(d), permitidos,
                                 "apareceu campo novo no frame. Se for um "
                                 "rotulo, nao pertence aqui.")

    def test_a_palavra_t3_nao_rotula_documento_nenhum(self):
        bruto = json.dumps(self.disco["DOCUMENTOS"], ensure_ascii=False)
        for proibido in ("T3_SIM", "T3_NAO", "T3_AMBIGUO", "LABEL"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, bruto)

    def test_o_ficheiro_bate_com_o_gerador(self):
        frame = am.sampling_frame()
        self.assertEqual([d["DOC_SHA256"] for d in self.disco["DOCUMENTOS"]],
                         [d["DOC_SHA256"] for d in frame],
                         "o frame versionado saiu de sincronia. Regenere: "
                         "py provas/amostragem_neutra_t3.py --escrever")


class OVeredictoContinuaMedido(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.frame = am.sampling_frame()
        cls.pacote = am.pacote_atual()
        cls.rev, cls.dentro, cls.fora = am.comparar(cls.frame, cls.pacote)

    def test_o_pacote_nasceu_da_pergunta_de_t2(self):
        o = am.origem_do_pacote()
        self.assertEqual(o["CURRENT_46_SELECTED_FOR_T2"], "YES")
        self.assertEqual(o["CURRENT_46_SELECTED_FOR_T3"], "NO")
        self.assertEqual(o["UNIVERSOS_QUE_O_GABARITO_ROTULA"], ["T2"])

    def test_o_pacote_esta_todo_dentro_do_frame(self):
        self.assertEqual(len(self.dentro), len(self.pacote),
                         "ha itens no pacote que o frame nao conhece")

    def test_o_frame_e_maior_que_o_pacote(self):
        self.assertGreater(len(self.rev), len(self.pacote))
        self.assertEqual(len(self.fora), 7,
                         "o numero de documentos fora do pacote mudou. Se for "
                         "verdade, o veredicto tem de ser refeito.")

    def test_ha_publicadores_inteiramente_ausentes_do_pacote(self):
        ausentes = ({d["PUBLISHER"] for d in self.rev}
                    - {d["PUBLISHER"] for d in self.dentro})
        self.assertTrue(ausentes, "se isto ficar vazio, a cobertura por "
                                  "publicador passou a ser total — e o "
                                  "veredicto muda")

    def test_o_portao_continua_a_reprovar_por_selecao_tematica(self):
        g = am.portao(self.rev, self.dentro, self.fora)
        self.assertFalse(g["SELECAO_NAO_TEMATICA"])
        self.assertEqual(
            g["CURRENT_46_ADEQUATE_FOR_GENERAL_T3_EVALUATION"], "NO")
        self.assertEqual(g["CURRENT_46_ROLE"], "B. PARTIAL_T3_EVAL_SLICE")

    def test_as_46_nao_foram_invalidadas(self):
        """Reaproveitar, nunca refazer sem motivo."""
        self.assertTrue(all(d["DOC_SHA256"] in self.pacote
                            for d in self.dentro))


class NadaFoiRotuladoNemAlterado(unittest.TestCase):

    def test_a_porta_continua_sem_t2_e_com_os_quatro_de_sempre(self):
        import admissao as adm
        self.assertEqual(sorted(adm.PERGUNTAS_DO_UNIVERSO),
                         ["T3", "T4", "T7", "T9"])

    def test_o_pacote_de_revisao_continua_vazio(self):
        with open(os.path.join(RAIZ, "data", "samples",
                               "T3-HUMAN-REVIEW-PENDING-V1.json"),
                  encoding="utf-8") as f:
            p = json.load(f)
        self.assertEqual(p["AUTO_LABELS_ADDED"] if "AUTO_LABELS_ADDED" in p
                         else p["AUTO_LABELS_ASSIGNED"], 0)
        for i in p["ITENS"]:
            self.assertEqual(i["FINAL_LABEL"], "NOT_RUN")

    def test_esta_prova_nao_escreve_sem_pedido(self):
        antes = os.path.getmtime(FRAME)
        am.sampling_frame()
        am.pacote_atual()
        self.assertEqual(antes, os.path.getmtime(FRAME))


if __name__ == "__main__":
    unittest.main()
