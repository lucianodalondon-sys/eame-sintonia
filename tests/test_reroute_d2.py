"""REROUTE D2 (D56) na Admissao — sem rede, sem Sala.

O que se guarda:
  · NAO / NAO_SE_APLICA na gaveta da FONTE -> a MESMA pergunta do tema as outras gavetas com regua;
    cada SIM fica em REROUTE.DESTINOS com UNIVERSO, PONTUACAO e MOTIVO, e ORIGEM = a gaveta da fonte;
  · o VEREDITO da gaveta da fonte NAO muda (nenhuma regua baixa);
  · SIM e NAO_SEI na gaveta da fonte nao reencaminham;
  · UM item: uma so Decisao, e o REROUTE nao copia o texto (sem duplicar bytes).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "admissao"))
import admissao as A  # noqa: E402

# Um texto de mercado que a regua T10 aprova, julgado numa gaveta que o rejeita com prova (T5).
MERCADO = ("I prezzi delle pesche all'ingrosso sono in calo: le quotazioni della settimana mostrano "
           "prezzi piu bassi, esportazioni ferme e importazioni in aumento sul mercato.")
# Um texto sem vocabulario de nenhuma gaveta (NAO_SEI na origem).
NADA = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor."


def _item(t):
    return {"id": "derived:1", "texto": t}


def _item_completo(t):
    """Como nas provas da casa (provas/testa_coleta_canonica.py): com fonte e tempo, os portoes passam."""
    return {"id": "IT-X-1", "texto": t, "source_id": "IT-T10-021", "fact_time": "2026-09-25"}


class OReroute(unittest.TestCase):

    def test_1_nao_na_fonte_pergunta_as_outras_gavetas_e_regista_destinos(self):
        r, _, _ = A._do_universo(_item(MERCADO), "T5", A.PERGUNTAS_DO_UNIVERSO["T5"])
        self.assertIn(r, (A.NAO, A.NAO_SEI))
        rr = A.reencaminhar(_item(MERCADO), "T5")
        self.assertEqual(rr["ORIGEM"], "T5")
        self.assertIn("T10", [d["UNIVERSO"] for d in rr["DESTINOS"]])
        t10 = next(d for d in rr["DESTINOS"] if d["UNIVERSO"] == "T10")
        self.assertGreaterEqual(t10["PONTUACAO"], 2)
        self.assertIn("T10", t10["MOTIVO"])
        self.assertEqual((rr["UNIVERSE_MATCH"], rr["SINTONIA_RELEVANT"], rr["ACTION"]), ("NO", "YES", "REROUTE"))

    def test_2_a_gaveta_da_fonte_nunca_e_destino_e_os_destinos_sao_so_sim(self):
        rr = A.reencaminhar(_item(MERCADO), "T10")
        self.assertNotIn("T10", [d["UNIVERSO"] for d in rr["DESTINOS"]])
        for d in rr["DESTINOS"]:
            r, _, _ = A._do_universo(_item(MERCADO), d["UNIVERSO"], A.PERGUNTAS_DO_UNIVERSO[d["UNIVERSO"]])
            self.assertEqual(r, A.SIM, d)

    def test_3_o_veredito_da_fonte_nao_muda_e_o_reroute_fica_na_evidencia(self):
        """decidir() inteiro, passando o estagio desconhecido (texto nu): o veredito e o de _do_universo."""
        viu_nao = 0
        for uv in ("T3", "T5", "T7"):
            r0, _, _ = A._do_universo(_item(MERCADO), uv, A.PERGUNTAS_DO_UNIVERSO[uv])
            d = A.decidir(_item_completo(MERCADO), uv)
            self.assertEqual(d.regra, "pertence ao universo", d)   # nao pode parar antes: senao o teste e vazio
            self.assertEqual(d.resultado, r0)
            viu_nao += r0 in (A.NAO, A.NAO_SE_APLICA)
            if r0 in (A.NAO, A.NAO_SE_APLICA):
                self.assertIn("REROUTE", d.evidencia)
                self.assertEqual(d.universo, uv)            # a decisao continua a ser da gaveta da fonte
            else:
                self.assertNotIn("REROUTE", d.evidencia)
        self.assertGreaterEqual(viu_nao, 1, "nenhuma gaveta deu NAO: o teste nao provou o REROUTE")

    def test_4_sim_ou_nao_sei_na_fonte_nao_reencaminham(self):
        d = A.decidir(_item_completo(MERCADO), "T10")
        self.assertEqual((d.regra, d.resultado), ("pertence ao universo", A.SIM), d)
        self.assertNotIn("REROUTE", d.evidencia)
        d = A.decidir(_item_completo(NADA), "T5")
        self.assertEqual((d.regra, d.resultado), ("pertence ao universo", A.NAO_SEI), d)
        self.assertNotIn("REROUTE", d.evidencia)

    def test_5_um_item_sem_duplicar_o_texto(self):
        rr = A.reencaminhar(_item(MERCADO), "T5")
        s = repr(rr)
        self.assertNotIn(MERCADO[:40], s)                  # o texto nao e copiado para a evidencia
        self.assertTrue(all(set(d) == {"UNIVERSO", "PONTUACAO", "MOTIVO"} for d in rr["DESTINOS"]))

    def test_6_destinos_ordenados_por_pontuacao_e_deterministicos(self):
        a = A.reencaminhar(_item(MERCADO), "T5")["DESTINOS"]
        b = A.reencaminhar(_item(MERCADO), "T5")["DESTINOS"]
        self.assertEqual(a, b)
        self.assertEqual(a, sorted(a, key=lambda d: (-d["PONTUACAO"], d["UNIVERSO"])))


class D66SoAnotar(unittest.TestCase):
    """D66 (dono, 25/09): o REROUTE so anota; nada entra na Sala; quando ligar, so T1 e T2."""

    def test_7_configuracao_explicita(self):
        self.assertIs(A.REROUTE_ENTRA_NA_SALA, False)
        self.assertEqual(A.REROUTE_GAVETAS_PERMITIDAS, frozenset({"T1", "T2"}))

    def test_8_anota_os_destinos_mas_nenhum_vai_para_a_sala(self):
        rr = A.reencaminhar(_item(MERCADO), "T5")
        self.assertIn("T10", [d["UNIVERSO"] for d in rr["DESTINOS"]])   # a anotacao continua inteira
        self.assertIs(rr["ENTRA_NA_SALA"], False)
        self.assertEqual(rr["GAVETAS_PERMITIDAS"], ["T1", "T2"])
        self.assertEqual(rr["DESTINOS_PARA_A_SALA"], [])
        self.assertEqual(A.destinos_para_a_sala(rr), [])

    def test_9_um_nao_reencaminhado_nao_atravessa_a_porta_da_sala(self):
        d = A.decidir(_item_completo(MERCADO), "T5")
        self.assertEqual(d.regra, "pertence ao universo", d)
        self.assertIn(d.resultado, (A.NAO, A.NAO_SE_APLICA))
        self.assertTrue(d.evidencia["REROUTE"]["DESTINOS"])               # havia destino…
        with self.assertRaises(ValueError):                                # …e mesmo assim nao entra
            A.pronto_para_inteligencia(_item_completo(MERCADO), d)

    def test_10_quando_ligar_so_entram_t1_e_t2(self):
        rr = {"DESTINOS": [{"UNIVERSO": u, "PONTUACAO": 3, "MOTIVO": "-"} for u in ("T10", "T2", "T5", "T9", "T1", "T4")]}
        antes = A.REROUTE_ENTRA_NA_SALA
        try:
            A.REROUTE_ENTRA_NA_SALA = True
            self.assertEqual(A.destinos_para_a_sala(rr), ["T2", "T1"])
        finally:
            A.REROUTE_ENTRA_NA_SALA = antes
        self.assertEqual(A.destinos_para_a_sala(rr), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
