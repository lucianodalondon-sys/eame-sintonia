# -*- coding: utf-8 -*-
"""JANELAS-68-v2 · B — entrada de janela: so o endereco muda, so com prova da P1g, nunca gemea. Sem rede."""
import copy
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import entrada_janela as EJ        # noqa: E402
import reparar_contrato as RC      # noqa: E402
from test_reparar_contrato import _contrato   # noqa: E402

LISTA = "https://www.exemplo.it/bollettini-2026"
EX = {"URL": "https://www.exemplo.it/bollettini-2026/n-12-del-28-agosto-2026", "DATA": "2026-08-28",
      "REVISAO": "BOLETIM_REAL"}


def _celula(url=LISTA, estado="PUBLICO_COM_BOLETIM", ex=EX, aprofundado=None):
    return {"URL": url, "ESTADO_MEDIDO": estado, "EXEMPLO": ex, "APROFUNDADO": aprofundado or []}


class Propor(unittest.TestCase):
    def setUp(self):
        self.c = _contrato(sid="IT-T3-900", index="https://www.exemplo.it/servizio-fitosanitario")

    def test_prova_da_p1g_troca_so_a_entrada(self):
        p = EJ.propor(self.c, EJ.entradas_provadas([_celula()]), EJ.donos_de_entrada([self.c]))
        self.assertEqual("PADRAO_NOVO", p["DESFECHO"], p.get("PORQUE"))
        self.assertEqual(LISTA, p["INDEX_URL"])
        self.assertEqual(self.c["ACQUISITION"]["LINK_PATTERN"], p["LINK_PATTERN"])
        novo = RC.aplicar(self.c, p)
        self.assertTrue(novo["REPARO_DE_CONTRATO"]["PRECISA_DE_REMEDIR"])
        self.assertEqual(self.c["ACQUISITION"], novo["REPARO_DE_CONTRATO"]["ACQUISITION_ANTERIOR"])
        mudou = {k for k in novo["ACQUISITION"] if novo["ACQUISITION"][k] != self.c["ACQUISITION"].get(k)}
        self.assertEqual({"INDEX_URL"}, mudou)

    def test_sem_exemplo_datado_e_revisto_nao_ha_prova(self):
        for ex in (None, dict(EX, DATA=None), dict(EX, REVISAO="NAO_REVISTO")):
            with self.subTest(ex=ex):
                p = EJ.propor(self.c, EJ.entradas_provadas([_celula(ex=ex)]), {})
                self.assertEqual(("SEM_PROPOSTA", "SEM_PROVA_NA_P1G"), (p["DESFECHO"], p["MOTIVO"]))

    def test_celula_sem_boletim_nao_prova(self):
        p = EJ.propor(self.c, EJ.entradas_provadas([_celula(estado="PUBLICO_SEM_BOLETIM_DATADO")]), {})
        self.assertEqual("SEM_PROVA_NA_P1G", p["MOTIVO"])

    def test_outro_host_e_outra_fonte(self):
        p = EJ.propor(self.c, EJ.entradas_provadas([_celula(url="https://meteo.exemplo.it/bollettini",
                                                            ex=dict(EX, VIA=None))]), {})
        self.assertEqual("SEM_PROPOSTA", p["DESFECHO"])

    def test_endereco_com_dono_nao_se_toma(self):
        dono = _contrato(sid="IT-T3-901", index=LISTA)
        p = EJ.propor(self.c, EJ.entradas_provadas([_celula()]), EJ.donos_de_entrada([self.c, dono]))
        self.assertEqual(("SEM_PROPOSTA", "ENTRADA_JA_TEM_DONO"), (p["DESFECHO"], p["MOTIVO"]))
        self.assertEqual(["IT-T3-901"], p["DONO"])

    def test_dono_com_www_diferente_continua_dono(self):
        dono = _contrato(sid="IT-T3-901", index=LISTA.replace("://www.", "://") + "/")
        p = EJ.propor(self.c, EJ.entradas_provadas([_celula()]), EJ.donos_de_entrada([self.c, dono]))
        self.assertEqual("ENTRADA_JA_TEM_DONO", p["MOTIVO"])

    def test_via_do_exemplo_e_a_entrada_e_o_aprofundado_conta(self):
        via = "https://www.exemplo.it/archivio"
        cel = _celula(url="https://www.exemplo.it/", estado="PUBLICO_SEM_BOLETIM_DATADO", ex=dict(EX, VIA=via),
                      aprofundado=[{"URL": via, "ESTADO_MEDIDO": "PUBLICO_COM_BOLETIM"}])
        p = EJ.propor(self.c, EJ.entradas_provadas([cel]), {})
        self.assertEqual(via, p["INDEX_URL"])

    def test_ja_na_entrada_provada_nao_ha_troca(self):
        c = copy.deepcopy(self.c)
        c["ACQUISITION"]["INDEX_URL"] = LISTA
        self.assertEqual("SEM_PROVA_NA_P1G", EJ.propor(c, EJ.entradas_provadas([_celula()]), {})["MOTIVO"])


if __name__ == "__main__":
    unittest.main()
