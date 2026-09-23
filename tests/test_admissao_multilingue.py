"""L1 — a regua da Admission na lingua do texto (D3 do dono), sem afrouxar nada.

Sem rede, sem Sala. Cada caso diz o que a regra manda:
  · texto ingles de mercado com dois sinais -> SIM (gabarito itens 5 e 6);
  · texto ingles fora do tema / marketing -> nunca SIM em T10;
  · o limiar nao muda: um sinal so continua NAO_SEI;
  · texto italiano (mesmo com palavras inglesas pelo meio) -> a regua de sempre;
  · lingua sem regua (fr/es/de) -> NAO_SEI dito: IDIOMA_NAO_SUPORTADO:<xx>;
  · lingua duvidosa -> a regua de sempre.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as A  # noqa: E402

ENCHIMENTO_EN = " The report of the sector is on the table and it was published this year with the data from the market. "
ENCHIMENTO_IT = " Il rapporto della filiera e stato pubblicato con i dati del settore per questo anno e anche per il prossimo che non sono. "

# excertos no espirito dos itens 5 e 6 do gabarito validado pelo dono
FRANGO_UE = ("EU poultry output rises as broiler prices decline. Imports from Ukraine grew and exports "
             "to the UK fell." + ENCHIMENTO_EN * 3)
INDONESIA = ("Indonesia eyes China and the Middle East for poultry exports; the price of chicken on the "
             "domestic market is falling." + ENCHIMENTO_EN * 3)
OBITUARIO = ("Remembering Dr James McKay, who dedicated his life to poultry genetics research at the "
             "university and was loved by his colleagues." + ENCHIMENTO_EN * 3)
MARKETING = ("Discover our new premium wine line! This summer we launch the exclusive campaign at the "
             "trade fair. Taste the novelty and win prizes, the party is free for all our fans." + ENCHIMENTO_EN * 3)


def veredito(texto, u="T10"):
    return A._do_universo({"texto": texto}, u, A.PERGUNTAS_DO_UNIVERSO.get(u, []))


class TestInglesJulgadoPelaMesmaRegua(unittest.TestCase):

    def test_itens_5_e_6_do_gabarito_entram(self):
        for t in (FRANGO_UE, INDONESIA):
            r, _, ev = veredito(t)
            self.assertEqual(r, A.SIM, t[:40])
            self.assertGreaterEqual(ev["sinais"], A.SINAIS_MINIMOS)

    def test_fora_do_tema_e_marketing_nunca_sao_sim_em_T10(self):
        for t in (OBITUARIO, MARKETING):
            self.assertNotEqual(veredito(t)[0], A.SIM, t[:40])

    def test_o_limiar_nao_muda_um_sinal_so_continua_nao_sei(self):
        t = "The price was not the point of the story, which was about a family farm." + ENCHIMENTO_EN * 3
        r, _, ev = veredito(t)
        self.assertEqual(r, A.NAO_SEI)
        self.assertEqual(ev["sinais"], 1)

    def test_nao_so_com_prova_de_outro_universo(self):
        r, motivo, ev = veredito(OBITUARIO)
        self.assertEqual(r, A.NAO)
        self.assertIn("achado_noutro", ev)


class TestItalianoFicaComoEstava(unittest.TestCase):

    def test_italiano_com_palavras_inglesas_usa_a_regua_italiana(self):
        # a pagina italiana tem «export» e «price» no menu: nao podem contar
        t = ("Menu: Export · Price list · Market news. Etichette compostabili per la frutta." + ENCHIMENTO_IT * 3)
        r, _, ev = veredito(t)
        self.assertNotEqual(r, A.SIM)
        self.assertFalse(set(ev.get("palavras", [])) & {"price", "exports", "imports"})

    def test_italiano_de_mercado_continua_sim_pela_lista_italiana(self):
        t = "I prezzi del pomodoro e le quotazioni all'ingrosso." + ENCHIMENTO_IT * 3
        r, _, ev = veredito(t)
        self.assertEqual(r, A.SIM)
        self.assertTrue(set(ev["palavras"]) <= set(A.PERGUNTAS_DO_UNIVERSO["T10"]))

    def test_lingua_duvidosa_usa_a_regua_de_sempre(self):
        t = "prezzi quotazioni price exports"          # sem palavras-funcao: lingua NAO SEI
        self.assertEqual(A._lingua_do_item({"texto": t}), "NAO_SEI")
        r, _, ev = veredito(t)
        self.assertEqual(sorted(ev["palavras"]), ["prezzi", "quotazion"])


class TestLinguaSemRegua(unittest.TestCase):

    def test_frances_e_nao_sei_dito(self):
        t = ("Le prix des exportations pour le marche est dans les pays avec une hausse sur des cette "
             "annee qui sont pour les producteurs.") * 3
        r, motivo, ev = veredito(t)
        self.assertEqual(r, A.NAO_SEI)
        self.assertTrue(motivo.startswith("IDIOMA_NAO_SUPORTADO:fr"))
        self.assertEqual(ev["idioma"], "fr")


class TestAListaInglesa(unittest.TestCase):

    def test_so_universos_que_ja_tem_regua(self):
        self.assertTrue(set(A.PERGUNTAS_EN) <= set(A.PERGUNTAS_DO_UNIVERSO))

    def test_nenhuma_forma_cabe_dentro_de_outra(self):
        for u, termos in A.PERGUNTAS_EN.items():
            for a in termos:
                for b in termos:
                    if a != b:
                        self.assertNotIn(a, b, f"{u}: «{a}» cabe dentro de «{b}»")

    def test_as_armadilhas_medidas_ficaram_de_fora(self):
        todas = {t for ts in A.PERGUNTAS_EN.values() for t in ts}
        for mau in ("trial", "event", "product", "thesis", "import", "pest", "trap"):
            self.assertNotIn(mau, todas)


if __name__ == "__main__":
    unittest.main()
