# -*- coding: utf-8 -*-
"""REROUTE-T1T2 (D129 + D130) — o reroute ENTRA na Sala so por T1 e T2; a regua T5 C1 fica desligada.

D130 (dono real, 28/09 ~12:10), verbatim: «Ligar só clima e cultura, como a regra atual (ganho hoje: 0,
risco: 0)». As outras gavetas ANOTAM no livro (regra, motivo, trecho) e nao entram.

    A · o escopo              exactamente {T1, T2}; T3 e T10 com SIM da regua ficam NAO_SEI com trecho;
                              uma SIM de reroute fora do escopo, venha de onde vier, nunca chega a Sala
    B · a estrada             pela_porta (FICHEIRO): documento so-T3 por reroute = 0 READY, livro com tudo
    C · o reprocesso seco     a Sala que ja existe so ganha gavetas T1/T2
    D · a regua T5 C1         desligada por omissao; ligada: inicio de palavra + cultura/praga no corpo
    E · o replay versionado   REPLAY-T5-C1.json e o que o codigo de agora produz (os 22 de 28/09)

    py -m unittest tests.test_reroute_t1t2_d130
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("", "admissao", "coleta", "orquestrador"):
    if str(RAIZ / p) not in sys.path:
        sys.path.insert(0, str(RAIZ / p))
import _gavetas                          # noqa: E402,F401
import admissao as adm                   # noqa: E402
import sala_de_espera as espera          # noqa: E402
import reprocessar_reroute as rr         # noqa: E402

# So T3 (praga) no corpo: nenhuma cultura com dois momentos, nenhum tempo com ligacao agricola.
SO_T3 = ("Nei campi della zona la peronospora e comparsa: le larve dell'insetto e i sintomi della malattia "
         "sono evidenti sulle foglie, con un patogeno che si diffonde rapidamente tra le piante. ") * 3
SO_T10 = ("Il prezzo del grano duro sale: la quotazione alla borsa merci di Foggia e aumentata, con il "
          "listino in crescita per la domanda. ") * 3
# Cultura com dois momentos (T1) e tempo com ancora agricola (T2).
T1_E_T2 = ("Bollettino: i vigneti sono in piena fioritura e la difesa integrata consiglia di seguire le "
           "catture nelle trappole; le piogge e le temperature elevate della settimana aumentano "
           "l'infestazione. ") * 3


def doc(texto, **kw):
    it = {"id": "derived:1", "texto": texto, "source_id": "IT-T7-017",
          "artifact_type": "DERIVED", "parent_sha256": "a" * 64}
    it.update(kw)
    return it


def por_universo(ds):
    return {d.universo: d for d in ds}


class AEscopoD130(unittest.TestCase):

    def test_o_escopo_e_exactamente_clima_e_cultura(self):
        self.assertEqual(adm.REROUTE_NA_SALA_D130, frozenset({"T1", "T2"}))
        # a regua medida continua escrita (T3, T10) — o escopo e decisao do dono, nao medida
        self.assertTrue(adm.REROUTE_NA_SALA_D130 < adm.REROUTE_PROMOVE)

    def test_t3_e_t10_anotam_com_regra_motivo_e_trecho(self):
        for texto, u in ((SO_T3, "T3"), (SO_T10, "T10")):
            ds = adm.decidir_todas(doc(texto), "T7", corrida="t")
            d = por_universo(ds)[u]
            self.assertEqual(d.resultado, adm.NAO_SEI, u)
            self.assertEqual(d.regra, adm.REGRA_DO_REROUTE)
            self.assertIn("REROUTE_FORA_DO_ESCOPO_D130", d.motivo)
            self.assertTrue(d.evidencia["sim_da_regua"] and d.evidencia["fora_do_escopo_d130"])
            self.assertTrue(d.evidencia["trechos"], u)                  # o trecho fica no livro
            self.assertIsNone(adm.principal(ds), u)                     # nao entra
            self.assertEqual(adm.gavetas_para_a_sala(ds), [], u)

    def test_t1_e_t2_entram_como_um_item_com_duas_gavetas(self):
        ds = adm.decidir_todas(doc(T1_E_T2), "T7", corrida="t")
        u = por_universo(ds)
        self.assertEqual((u["T1"].resultado, u["T2"].resultado), (adm.SIM, adm.SIM))
        self.assertIn(adm.principal(ds).universo, {"T1", "T2"})
        self.assertEqual(sorted(g["UNIVERSO"] for g in adm.gavetas_para_a_sala(ds)), ["T1", "T2"])

    def test_nenhum_sim_de_reroute_fora_do_escopo_chega_a_sala_venha_de_onde_vier(self):
        # uma SIM de T3/T10 fabricada (livro antigo, regua alargada sem a D130): a Sala continua fechada
        ds = adm.decidir_todas(doc(SO_T3), "T7", corrida="t")
        for d in ds[1:]:
            if d.universo in ("T3", "T10"):
                d.resultado = adm.SIM
                d.evidencia["pontuacao"] = 9
        self.assertIsNone(adm.principal(ds))
        self.assertEqual(adm.gavetas_para_a_sala(ds), [])
        # e com o pedido SIM, a gaveta fabricada tambem nao viaja ao lado
        ds2 = adm.decidir_todas(doc(T1_E_T2), "T2", corrida="t")
        forjada = adm.Decisao(item=ds2[0].item, universo="T10", resultado=adm.SIM,
                              regra=adm.REGRA_DO_REROUTE, motivo="forjada", evidencia={"sinais": 9})
        self.assertNotIn("T10", [g["UNIVERSO"] for g in adm.gavetas_para_a_sala(ds2 + [forjada])])

    def test_o_pedido_nao_e_tocado_pela_d130(self):
        # o PEDIDO T3 continua a entrar por T3: a D130 e so do reroute
        ds = adm.decidir_todas(doc(SO_T3), "T3", corrida="t")
        self.assertIs(adm.principal(ds), ds[0])
        self.assertEqual(adm.gavetas_para_a_sala(ds)[0]["UNIVERSO"], "T3")


class AEstradaD130(unittest.TestCase):

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="reroute-d130-"))
        self._p = [mock.patch.object(espera, "MORADA", str(self.pasta / "sala")),
                   mock.patch.object(adm, "LIVRO", self.pasta / "LIVRO.json"),
                   mock.patch.dict(os.environ, {"SINTONIA_SALA_BACKEND": "FICHEIRO"})]
        for p in self._p:
            p.start()
        import orquestrador as orq
        self.orq = orq

    def tearDown(self):
        for p in self._p:
            p.stop()
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_so_t3_e_so_t10_por_reroute_nao_pousam_e_ficam_no_livro(self):
        r = self.orq.pela_porta([doc(SO_T3), doc(SO_T10, id="derived:2")], "T7", "RUN-D130")
        self.assertEqual(r["prontos"], 0)
        self.assertEqual(r["REROUTE"]["NA_SALA_D130"], ["T1", "T2"])
        self.assertEqual(r["REROUTE"]["ITENS_SO_POR_REROUTE"], 0)
        livro = json.loads((self.pasta / "LIVRO.json").read_text(encoding="utf-8"))["DECISOES"]
        anotadas = {(d["item"], d["universo"]) for d in livro
                    if "REROUTE_FORA_DO_ESCOPO_D130" in d["motivo"]}
        self.assertEqual(anotadas, {("derived:1", "T3"), ("derived:2", "T10")})


class OReprocessoD130(unittest.TestCase):

    def test_a_sala_que_ja_existe_so_ganha_gavetas_t1_t2(self):
        linhas = [{"RUN_ID": "R1", "ORDEM": 0, "ITEM_ID": "derived:1", "UNIVERSO": "T7",
                   "SOURCE_ID": "IT-T7-017", "SHA256": "a" * 64, "MEDIA_TYPE": "application/pdf",
                   "TEXTO": SO_T3 + T1_E_T2},
                  {"RUN_ID": "R1", "ORDEM": 1, "ITEM_ID": "derived:2", "UNIVERSO": "T7",
                   "SOURCE_ID": "IT-T7-017", "SHA256": "b" * 64, "MEDIA_TYPE": "application/pdf",
                   "TEXTO": SO_T10}]
        plano = rr.planear(linhas)
        self.assertEqual(sorted(g["UNIVERSO"] for g in plano["GAVETAS"]), ["T1", "T2"])
        self.assertEqual(plano["REROUTE_NA_SALA_D130"], ["T1", "T2"])
        anotadas = {(d["item"], d["universo"]) for d in plano["DECISOES"]
                    if "REROUTE_FORA_DO_ESCOPO_D130" in d["motivo"]}
        self.assertEqual(anotadas, {("derived:1", "T3"), ("derived:2", "T10")})


# ── D · a regua T5 C1 ────────────────────────────────────────────────────────
MENU_CIENCIA = "Home | Infrastrutture di ricerca | Università | Contatti\n"
CANARIO = ("Xylella fastidiosa: dalla ricerca nuove strategie per l'olivicoltura. Il progetto illustra i "
           "risultati finali attesi ed evidenzia le nuove varieta di olivo resistenti alla malattia, "
           "e il ruolo dell'insetto vettore negli oliveti. ") * 3
SCIENZA_SENZA_AGRO = ("Lo studio della ricerca sulla qualita dell'aria, presentato all'università con il "
                      "convegno sul particolato atmosferico, confronta i modelli di dispersione urbana. ") * 3
SCIENZA_AGRO = ("Lo studio della ricerca dell'università sul pomodoro mostra che il patogeno si diffonde "
                "con l'umidita; la sperimentazione ha confrontato tre varieta resistenti. ") * 3


class AReguaT5C1(unittest.TestCase):

    def test_a_chave_esta_desligada_por_omissao_e_o_pedido_nao_muda(self):
        self.assertIs(adm.REGUA_T5_EXIGE_AGRO, False)
        d = adm.decidir(doc(CANARIO), "T5", corrida="t")
        # como hoje em producao: «tesi» dentro de «attesi» conta como sinal (o LAB mediu-o no 1149)
        self.assertEqual(d.resultado, adm.SIM)
        self.assertIn("tesi", d.evidencia["palavras"])
        self.assertNotIn("regua_t5", d.evidencia)

    @mock.patch.object(adm, "REGUA_T5_EXIGE_AGRO", True)
    def test_ligada_o_termo_tem_de_comecar_palavra(self):
        d = adm.decidir(doc(CANARIO), "T5", corrida="t")
        self.assertEqual(d.resultado, adm.NAO_SEI)                      # so «ricerca»: um sinal
        self.assertNotIn("tesi", d.evidencia.get("palavras") or [])
        self.assertEqual(d.evidencia["regua_t5"], adm.VERSAO_DA_REGUA_T5)

    @mock.patch.object(adm, "REGUA_T5_EXIGE_AGRO", True)
    def test_ligada_ciencia_sem_cultura_nem_praga_fica_nao_sei(self):
        d = adm.decidir(doc(MENU_CIENCIA + SCIENZA_SENZA_AGRO), "T5", corrida="t")
        self.assertEqual(d.resultado, adm.NAO_SEI)                      # nunca NAO: ausencia != negativo
        self.assertIn("T5_SEM_ASSUNTO_AGRO", d.motivo)
        d2 = adm.decidir(doc(SCIENZA_AGRO), "T5", corrida="t")
        self.assertEqual(d2.resultado, adm.SIM)
        self.assertEqual((d2.evidencia["assunto_agro"]["cultura"], d2.evidencia["assunto_agro"]["praga"]),
                         (["pomodoro"], ["patogeno"]))

    @mock.patch.object(adm, "REGUA_T5_EXIGE_AGRO", True)
    def test_ligada_o_termo_agro_no_menu_nao_conta(self):
        menu_agro = "Home | Olivo | Vite | Peronospora | Contatti\n"
        pagina = doc(menu_agro + SCIENZA_SENZA_AGRO, media_type="text/html")
        d = adm.decidir(pagina, "T5", corrida="t")
        self.assertIn("T5_SEM_ASSUNTO_AGRO", d.motivo)
        # controlo: o MESMO texto lido inteiro (PDF) acharia o menu
        self.assertEqual(adm.decidir(doc(menu_agro + SCIENZA_SENZA_AGRO), "T5", corrida="t").resultado,
                         adm.SIM)

    @mock.patch.object(adm, "REGUA_T5_EXIGE_AGRO", True)
    def test_ligada_pagina_html_sem_corpo_fica_nao_sei(self):
        # uma linha so, com rodape: o caso CREA (corpo() = 0 caracteres)
        linha = " ".join(SCIENZA_AGRO.split()) + " Seguici su Facebook · Partita IVA 01234567890"
        d = adm.decidir(doc(linha, media_type="text/html"), "T5", corrida="t")
        self.assertEqual(d.resultado, adm.NAO_SEI)
        self.assertIn("T5_CORPO_NAO_SEPARAVEL", d.motivo)

    def test_ligada_so_muda_o_t5(self):
        antes = {u: adm.decidir(doc(SCIENZA_AGRO), u, corrida="t") for u in adm.universos_da_porta()}
        with mock.patch.object(adm, "REGUA_T5_EXIGE_AGRO", True):
            depois = {u: adm.decidir(doc(SCIENZA_AGRO), u, corrida="t") for u in adm.universos_da_porta()}
        mudaram = {u for u in antes if (antes[u].resultado, antes[u].motivo) !=
                   (depois[u].resultado, depois[u].motivo)}
        self.assertEqual(mudaram, {"T5"})


class OReplayVersionado(unittest.TestCase):
    """O REPLAY-T5-C1.json versionado e o que o codigo de agora produz — para os 22 de 28/09."""

    def test_os_22_de_28_09_batem_com_o_codigo(self):
        import importlib.util
        sp = importlib.util.spec_from_file_location(
            "replay_t5_c1", RAIZ / "provas" / "reroute_t1t2" / "replay_t5_c1.py")
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        rep = json.loads((RAIZ / "provas" / "reroute_t1t2" / "REPLAY-T5-C1.json").read_text(encoding="utf-8"))
        sala = {x["item_id"]: x for x in json.loads(
            (RAIZ / "docs" / "lab-insumos" / "reroute-prova" / "SALA-T5-EXPORT.json").read_text(encoding="utf-8"))}
        hoje = [l for l in rep["ITENS"] if l["DE_28_09"]]
        self.assertEqual(len(hoje), 22)
        for l in hoje:
            agora = m.julgar(sala[l["ITEM"]])
            for k in ("CORPO_ESTRITO", "CORPO_SENAO_INTEIRO", "TEXTO_INTEIRO"):
                self.assertEqual(agora[k], l[k], (l["ITEM"], k))
        # a promessa medida: nenhum NAO-AGRO (rotulo do LAB) fica, em nenhuma leitura
        for k in ("CORPO_ESTRITO", "CORPO_SENAO_INTEIRO", "TEXTO_INTEIRO"):
            self.assertNotIn("FICA·NAO", rep["OS_22_DE_28_09"][k]["POR_ROTULO_LAB"], k)


if __name__ == "__main__":
    unittest.main(verbosity=2)
