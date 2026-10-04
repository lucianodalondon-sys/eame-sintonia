# Testes do ESTADO VIVO ACUMULADO (motor/fast_auto/estado_vivo.py) sobre rodadas com a FORMA REAL
# (pasta <RUN_ID>/ com CRUZAMENTO-COMERCIAL.json + SHA256SUMS.txt), nao dicts soltos.
import hashlib, json, os, shutil, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "motor", "fast_auto"))
import estado_vivo as EV  # noqa: E402

URL_MYFRUIT = "https://www.myfruit.it/news/invitalia-incontra-melinda"


def ev(fid, doc, url, trecho):
    return {"FACT_ID": fid, "DOCUMENT_ID": doc, "SOURCE_ID": "IT-T10-018", "URL": url, "trecho": trecho}


def obj(local, destino, evidencias, titulo, classe="SINAL"):
    return {"ID": local, "CLASSE": classe, "DESTINO_FERRAMENTA": [destino], "TITULO_IT": titulo,
            "EVIDENCIAS": evidencias}


def rodada(raiz, run_id, objetos):
    p = os.path.join(raiz, run_id)
    os.makedirs(p)
    dest = {g: [] for g in EV.GAVETAS + [EV.NAO_PUBLICAR]}
    for o in objetos:
        dest[o["DESTINO_FERRAMENTA"][0]].append(o["ID"])
    c = {"CODIGO_HEAD": "teste", "DESTINOS": dest, "OBJETOS": objetos}
    pc = os.path.join(p, "CRUZAMENTO-COMERCIAL.json")
    json.dump(c, open(pc, "w", encoding="utf-8"), ensure_ascii=False)
    s = hashlib.sha256(open(pc, "rb").read()).hexdigest()
    open(os.path.join(p, "SHA256SUMS.txt"), "w").write("%s *CRUZAMENTO-COMERCIAL.json\n" % s)


MELINDA = obj("C01", "MARKET_PULSE", [ev("F-RAW-2336-01", "RAW-2336", URL_MYFRUIT, "Melinda investe 37,5 milioni"),
                                      ev("F-RAW-2336-06", "RAW-2336", URL_MYFRUIT, "703 contratti di sviluppo")],
              "Melinda")
INVITALIA = obj("C02", "MARKET_PULSE", [ev("F-RAW-2336-06", "RAW-2336", URL_MYFRUIT, "703 contratti di sviluppo")],
                "Invitalia")
AGRI = obj("C03", "MARKET_PULSE", [ev("F-RAW-2335-01", "RAW-2335", "https://www.myfruit.it/agrisicilia",
                                      "Agrisicilia rilancia il negozio online")], "Agrisicilia")
CENA = obj("C01", "NAO_PUBLICAR", [ev("F-RAW-2418-01", "RAW-2418", "https://x.it/cena", "cena aziendale 2024")],
           "Cena")


class EstadoVivo(unittest.TestCase):
    def setUp(self):
        self.raiz = tempfile.mkdtemp()
        self.arq = os.path.join(self.raiz, EV.NOME)

    def tearDown(self):
        shutil.rmtree(self.raiz)

    def market(self, est):
        t = {o["ID"]: o["TITULO_IT"] for o in est["OBJETOS"]}
        return sorted(t[i] for i in est["DESTINOS"]["MARKET_PULSE"])

    def test_V1_rodada_so_nao_publicar_nao_zera_market(self):
        rodada(self.raiz, "FAST-A", [MELINDA, INVITALIA, AGRI])
        rodada(self.raiz, "FAST-B", [CENA])
        EV.aplicar_rodadas(self.raiz, ["FAST-A"], self.arq)
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-B"], self.arq)
        self.assertEqual(self.market(est), ["Agrisicilia", "Invitalia", "Melinda"])

    def test_V2_rodada_vazia_nao_limpa_nada(self):
        rodada(self.raiz, "FAST-A", [MELINDA, INVITALIA, AGRI])
        rodada(self.raiz, "FAST-B", [])
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-A", "FAST-B"], self.arq)
        self.assertEqual(len(est["DESTINOS"]["MARKET_PULSE"]), 3)

    def test_V3_nao_publicar_nunca_entra_em_superficie(self):
        rodada(self.raiz, "FAST-B", [CENA])
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-B"], self.arq)
        self.assertNotIn(EV.NAO_PUBLICAR, est["DESTINOS"])
        self.assertEqual(est["OBJETOS"], [])

    def test_V4_mesma_url_e_documento_dois_itens_distintos(self):
        # armadilha medida: Melinda e Invitalia = mesma URL e mesmo DOCUMENT_ID
        rodada(self.raiz, "FAST-A", [MELINDA, INVITALIA])
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-A"], self.arq)
        self.assertEqual(len(est["DESTINOS"]["MARKET_PULSE"]), 2)
        self.assertEqual(len(est["POSSIVEIS_DUPLICADOS"]), 1)  # registado, nao fundido

    def test_V5_recaptura_do_mesmo_acontecimento_atualiza_nao_duplica(self):
        # mesmo acontecimento recapturado: RAW/DOCUMENT_ID/FACT_ID/C0x novos, mesma URL + mesmo trecho
        rodada(self.raiz, "FAST-A", [MELINDA, INVITALIA, AGRI])
        recap = obj("C07", "MARKET_PULSE", [ev("F-RAW-9999-04", "RAW-9999", "https://www.myfruit.it/agrisicilia",
                                               "Agrisicilia  RILANCIA il negozio online")], "Agrisicilia v2", "LEAD")
        rodada(self.raiz, "FAST-C", [recap])
        est, rs = EV.aplicar_rodadas(self.raiz, ["FAST-A", "FAST-C"], self.arq)
        self.assertEqual(len(est["OBJETOS"]), 3)
        self.assertEqual(len(rs[1]["ATUALIZADOS"]), 1)
        a = [o for o in est["OBJETOS"] if o["TITULO_IT"] == "Agrisicilia v2"][0]
        self.assertEqual(a["CLASSE"], "LEAD")
        self.assertEqual(a["VIVO"]["PRIMEIRA_RODADA"], "FAST-A")
        self.assertEqual([h["RUN_ID"] for h in a["VIVO"]["HISTORICO"]], ["FAST-A", "FAST-C"])
        self.assertEqual(a["VIVO"]["MUDANCAS"][0]["ANTES"]["CLASSE"], "SINAL")

    def test_V6_reaplicar_mesma_rodada_e_idempotente(self):
        rodada(self.raiz, "FAST-A", [MELINDA, INVITALIA, AGRI])
        EV.aplicar_rodadas(self.raiz, ["FAST-A"], self.arq)
        antes = open(self.arq, encoding="utf-8").read()
        est, rs = EV.aplicar_rodadas(self.raiz, ["FAST-A"], self.arq)
        self.assertEqual(len(est["OBJETOS"]), 3)
        self.assertEqual(rs[0]["NOVOS"], [])

    def test_V7_mesmo_item_reclassificado_nao_publicar_sai_com_motivo_sem_apagar(self):
        rodada(self.raiz, "FAST-A", [AGRI])
        volta = dict(AGRI, DESTINO_FERRAMENTA=["NAO_PUBLICAR"])
        rodada(self.raiz, "FAST-B", [volta])
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-A", "FAST-B"], self.arq)
        self.assertEqual(est["DESTINOS"]["MARKET_PULSE"], [])
        self.assertEqual(len(est["OBJETOS"]), 1)
        self.assertTrue(est["FORA_DA_SUPERFICIE"][0]["MOTIVO"].startswith("RECLASSIFICADO_NAO_PUBLICAR"))

    def test_V8_retirar_exige_motivo_da_lista_e_porque(self):
        rodada(self.raiz, "FAST-A", [AGRI])
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-A"], self.arq)
        iid = est["OBJETOS"][0]["ID"]
        with self.assertRaises(ValueError):
            EV.retirar(est, iid, "PORQUE_SIM", "x")
        with self.assertRaises(ValueError):
            EV.retirar(est, iid, "EXPIRED", "")
        EV.retirar(est, iid, "EXPIRED", "campanha encerrada")
        self.assertEqual(est["DESTINOS"]["MARKET_PULSE"], [])

    def test_V9_rodada_adulterada_e_recusada_e_estado_fica_intacto(self):
        rodada(self.raiz, "FAST-A", [AGRI])
        EV.aplicar_rodadas(self.raiz, ["FAST-A"], self.arq)
        antes = open(self.arq, encoding="utf-8").read()
        rodada(self.raiz, "FAST-B", [CENA])
        with open(os.path.join(self.raiz, "FAST-B", "CRUZAMENTO-COMERCIAL.json"), "a") as f:
            f.write(" ")
        with self.assertRaises(EV.RodadaRecusada):
            EV.aplicar_rodadas(self.raiz, ["FAST-B"], self.arq)
        self.assertEqual(open(self.arq, encoding="utf-8").read(), antes)

    def test_V10_identidade_nao_usa_c0x_nem_document_id(self):
        a = EV.id_vivo(AGRI)
        b = EV.id_vivo(dict(AGRI, ID="C99", EVIDENCIAS=[dict(AGRI["EVIDENCIAS"][0], DOCUMENT_ID="RAW-1", FACT_ID="F-X")]))
        self.assertEqual(a, b)
        self.assertNotEqual(EV.id_vivo(MELINDA), EV.id_vivo(INVITALIA))

    def test_V11_nao_publicar_parcial_fica_visivel_no_item_vivo_sem_o_retirar(self):
        # caso real do LAB: Riunite Tour Music Fest = 3 ancoras em FUTURE_RADAR (03/10 16:42),
        # depois 2 dessas ancoras em NAO_PUBLICAR (04/10 02:42)
        a1 = ev("F-1", "RAW-2851", "https://riunite/tour", "il 16 ottobre tour music fest")
        a2 = ev("F-2", "RAW-2851", "https://riunite/tour", "parte di questo progetto da 6 anni")
        a3 = ev("F-3", "RAW-2850", "https://prosecco/x", "prosecco premiato")
        rodada(self.raiz, "FAST-A", [obj("C07", "FUTURE_RADAR", [a1, a2, a3], "Due cantine")])
        rodada(self.raiz, "FAST-B", [obj("C07", "NAO_PUBLICAR", [dict(a1, DOCUMENT_ID="RAW-2567"),
                                                                 dict(a2, DOCUMENT_ID="RAW-2567")], "Riunite")])
        est, _ = EV.aplicar_rodadas(self.raiz, ["FAST-A", "FAST-B"], self.arq)
        self.assertEqual(len(est["DESTINOS"]["FUTURE_RADAR"]), 1)  # nao retira por semelhanca
        viv = est["OBJETOS"][0]["VIVO"]
        self.assertEqual({c["TIPO"] for c in viv["CONFLITOS"]}, {"NAO_PUBLICAR_PARTILHA_ANCORA"})
        self.assertEqual(len(viv["CONFLITOS"]), 2)


if __name__ == "__main__":
    unittest.main()
