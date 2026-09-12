# -*- coding: utf-8 -*-
"""O CENSO DO CORPUS ROTULADO NAO PODE APODRECER — nem afrouxar.

Este censo respondeu que ha chao para AVALIAR um mecanismo em T2 e para mais
nada. A maneira mais facil de essa resposta deixar de valer nao e o corpus
mudar: e alguem baixar o limiar ate o corpus passar.

    UM CRITERIO ESCRITO DEPOIS DA CONTAGEM
    E O ALVO DESENHADO A VOLTA DA FLECHA.

Por isso os limiares estao presos aqui, um a um, e nao como total. Subir um
limiar e legitimo e estes testes deixam. Baixar um limiar cai alto.
"""
import importlib.util
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "censo_corpus", os.path.join(RAIZ, "provas",
                                 "censo_corpus_rotulado_admission.py"))
censo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(censo)


class OsCriteriosNaoAfrouxam(unittest.TestCase):
    """Cada limiar preso pelo seu proprio nome, e nao por uma soma."""

    MINIMOS = {
        ("SANITY", "POSITIVOS_MIN"): 3,
        ("SANITY", "NEGATIVOS_MIN"): 3,
        ("SANITY", "PUBLICADORES_MIN"): 2,
        ("EVALUATION", "POSITIVOS_MIN"): 10,
        ("EVALUATION", "NEGATIVOS_MIN"): 10,
        ("EVALUATION", "PUBLICADORES_MIN"): 3,
        ("TRAINING", "POSITIVOS_MIN"): 100,
        ("TRAINING", "NEGATIVOS_MIN"): 100,
        ("TRAINING", "PUBLICADORES_MIN"): 5,
        ("TRAINING", "FAMILIAS_DE_DOCUMENTO_MIN"): 2,
    }

    def test_nenhum_limiar_desceu(self):
        for (uso, chave), minimo in self.MINIMOS.items():
            with self.subTest(uso=uso, chave=chave):
                self.assertGreaterEqual(
                    censo.CRITERIOS[uso][chave], minimo,
                    f"{uso}.{chave} desceu abaixo de {minimo}. Um limiar que "
                    f"baixa depois da contagem nao mede nada: refaca o censo, "
                    f"nao o criterio.")

    def test_o_holdout_de_publicador_continua_obrigatorio_para_avaliar(self):
        self.assertTrue(censo.CRITERIOS["EVALUATION"]
                        ["EXIGE_HOLDOUT_DE_PUBLICADOR"],
                        "sem holdout de publicador, a avaliacao repete o erro "
                        "que T2 mediu: 0/10 no publicador que nao viu")

    def test_todo_criterio_diz_porque(self):
        for uso, c in censo.CRITERIOS.items():
            with self.subTest(uso=uso):
                self.assertGreater(len(c.get("PORQUE", "")), 40,
                                   f"{uso} tem numero sem razao escrita")


class AAutoridadeDoRotuloNaoSeMistura(unittest.TestCase):
    """A regra que governa o censo inteiro, presa em codigo."""

    def test_keyword_derived_nunca_serve_de_gabarito(self):
        self.assertNotIn(
            censo.KEYWORD_DERIVED, censo.SERVEM_DE_GABARITO,
            "um rotulo produzido por `PERGUNTAS_DO_UNIVERSO` viraria gabarito "
            "do substituto dela. O mecanismo novo aprenderia as respostas do "
            "velho e herdaria o mesmo defeito.")

    def test_a_ficha_da_fonte_nao_serve_de_gabarito(self):
        self.assertNotIn(
            censo.SOURCE_CONTRACT_DECLARED, censo.SERVEM_DE_GABARITO,
            "a ARPAV publica T2 e T3. O territorio da FONTE nao e o universo "
            "do DOCUMENTO — e este gabarito tem os dois casos.")

    def test_so_pessoa_e_autodeclaracao_servem(self):
        self.assertEqual(sorted(censo.SERVEM_DE_GABARITO),
                         sorted((censo.HUMAN_VERIFIED,
                                 censo.DOCUMENT_SELF_DECLARED)))


class ONaoSeiNaoContaComoPublicador(unittest.TestCase):
    """Este defeito esteve nesta prova, e ela deu verde com ele."""

    def test_um_balde_de_desconhecidos_nao_e_diversidade(self):
        pos = [{"PUBLICADOR": "NAO SEI"}] * 20
        neg = [{"PUBLICADOR": "NAO SEI"}] * 20
        g = censo.portao("TX", pos, neg, ["NAO SEI"], ["PDF", "HTML"])
        self.assertFalse(g["SANITY"],
                         "20 positivos e 20 negativos de publicador "
                         "desconhecido passaram o portao. «NAO SEI» esta a "
                         "contar como categoria.")
        self.assertEqual(g["VEREDICTO"], "D")

    def test_a_linhagem_resolve_o_publicador_do_texto_derivado(self):
        """Os derivados nao tem a fonte no nome; tem-na no pai."""
        p = censo.publicador_de("data/derivados/texto/RAW-f88c89d73d6a132a.txt")
        self.assertEqual(p, "ARPAV")
        self.assertEqual(
            censo.fonte_de("data/derivados/texto/RAW-f88c89d73d6a132a.txt"),
            "IT-T2-002")


class OCensoContinuaAMedirOMesmo(unittest.TestCase):
    """Se estes numeros mudarem, o veredicto tem de ser refeito — nao ignorado."""

    @classmethod
    def setUpClass(cls):
        cls.gab = censo._gabarito_t2()
        cls.corpo = censo.corpus_com_corpo(cls.gab)

    def test_o_unico_corpus_com_corpo_e_razao_e_o_gabarito_de_t2(self):
        self.assertEqual(len(self.corpo), 46)
        sem_corpo = [c for c in self.corpo
                     if not os.path.isfile(os.path.join(RAIZ, c["CONTENT_PATH"]))]
        self.assertEqual(sem_corpo, [], "rotulo sem corpo verificavel nao e "
                                        "elegivel para treino nem avaliacao")

    def test_todo_item_confiavel_responde_as_sete_perguntas(self):
        for c in self.corpo:
            with self.subTest(item=c["ITEM_ID"]):
                for campo in ("ITEM_ID", "SOURCE_ID", "CONTENT_PATH", "LABEL",
                              "LABEL_AUTHORITY", "LABEL_REASON"):
                    self.assertTrue(c.get(campo), f"{campo} em falta")

    def test_t2_tem_avaliacao_e_nao_tem_treino(self):
        pos = [c for c in self.corpo if c["LABEL"] == "T2:SIM"]
        neg = [c for c in self.corpo if c["LABEL"] == "T2:NAO"]
        publ = sorted({c["PUBLICADOR"] for c in pos + neg})
        fam = sorted({c["FAMILIA"] for c in pos + neg})
        g = censo.portao("T2", pos, neg, publ, fam)
        self.assertTrue(g["SANITY"])
        self.assertTrue(g["EVALUATION"])
        self.assertFalse(g["TRAINING"], "T2 passou a dar para TREINAR. Isso "
                                        "pode ser verdade — mas obriga a "
                                        "refazer o censo, nao a assumir.")
        self.assertEqual(g["VEREDICTO"], "B")

    def test_o_holdout_de_publicador_de_t2_e_real(self):
        pos = [c for c in self.corpo if c["LABEL"] == "T2:SIM"]
        publ = {c["PUBLICADOR"] for c in pos} - {"NAO SEI"}
        self.assertGreaterEqual(len(publ), 3, f"so {publ} do lado positivo")
        for fora in publ:
            with self.subTest(retido=fora):
                self.assertTrue([c for c in pos if c["PUBLICADOR"] != fora],
                                f"reter {fora} nao deixa positivo nenhum")

    def test_os_outros_universos_nao_ganharam_gabarito_em_silencio(self):
        rotulos = {c["LABEL"].split(":")[0] for c in self.corpo}
        self.assertEqual(rotulos, {"T2"},
                         "o gabarito passou a rotular outro universo. Se for "
                         "verdade, o veredicto desse universo tem de ser "
                         "recalculado neste censo.")


class OLivroNaoEGabaritoENaoESujo(unittest.TestCase):

    def test_toda_decisao_do_livro_veio_das_keywords_de_hoje(self):
        livro = censo._json("data/samples/LIVRO-DE-DECISOES.json")["DECISOES"]
        versoes = {d.get("versao") for d in livro}
        self.assertTrue(versoes <= {adm.VERSAO_DA_REGRA, "1", "2", "3"},
                        f"versoes inesperadas no livro: {versoes}")
        self.assertEqual(
            [d for d in livro if d["universo"] == "T2"], [],
            "apareceu decisao de T2 no livro. T2 nao tem regra escrita.")

    def test_o_censo_nao_escreve_no_livro_real(self):
        antes = os.path.getmtime(adm.LIVRO)
        censo.corpus_com_corpo(censo._gabarito_t2())
        censo.origens_de_rotulo()
        self.assertEqual(antes, os.path.getmtime(adm.LIVRO))


if __name__ == "__main__":
    unittest.main()
