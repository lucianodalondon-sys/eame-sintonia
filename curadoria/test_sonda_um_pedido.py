# -*- coding: utf-8 -*-
"""BLOQUEADAS-DESTRAVAR — a sonda faz 1 pedido por fonte, 1 por organização por ronda, e nada sem portão IT.
Sem rede: `buscar`, `portao` e `dormir` são falsos."""
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import sonda_um_pedido as S   # noqa: E402

CONTRATOS = {
    "IT-T7-050": {"SOURCE_ID": "IT-T7-050", "ACQUISITION": {"INDEX_URL": "https://www.coldiretti.it/notizie"}},
    "IT-T7-051": {"SOURCE_ID": "IT-T7-051", "ACQUISITION": {"INDEX_URL": "https://puglia.coldiretti.it/"}},
    "IT-T7-052": {"SOURCE_ID": "IT-T7-052", "ACQUISITION": {"INDEX_URL": "https://sicilia.coldiretti.it/"}},
    "IT-T7-058": {"SOURCE_ID": "IT-T7-058", "ACQUISITION": {"INDEX_URL": "https://www.unaprol.it/news"}},
    "IT-T5-006": {"SOURCE_ID": "IT-T5-006", "ACQUISITION": {"INDEX_URL": "https://www.cnr.it/it/news"}},
}
IDS = ["IT-T5-006", "IT-T7-050", "IT-T7-051", "IT-T7-052", "IT-T7-058"]


class Sonda(unittest.TestCase):
    def setUp(self):
        self.pedidos, self.sonos = [], []
        self.fontes = S.planear(IDS, CONTRATOS)

    def buscar(self, respostas):
        def f(url):
            self.pedidos.append(url)
            return respostas.get(url, (200, b"User-agent: *", ""))
        return f

    def test_um_pedido_por_fonte_e_so_ao_robots(self):
        out = S.correr(self.fontes, self.buscar({}), lambda: {"EGRESS_GATE": "PASS"}, dormir=self.sonos.append)
        self.assertEqual(len(IDS), len(self.pedidos))
        self.assertTrue(all(u.endswith("/robots.txt") for u in self.pedidos))
        self.assertEqual(len(IDS), out["PEDIDOS"])

    def test_uma_organizacao_por_ronda(self):
        planos = S.rondas(self.fontes)
        for r in planos:
            orgs = [f["ORGANIZACAO"] for f in r]
            self.assertEqual(len(orgs), len(set(orgs)))
        self.assertEqual(3, len(planos), "3 hosts da Coldiretti = 3 rondas")
        S.correr(self.fontes, self.buscar({}), lambda: {"EGRESS_GATE": "PASS"}, dormir=self.sonos.append,
                 pausa_ronda=1200, pausa_pedido=60)
        self.assertEqual(2, self.sonos.count(1200), "espera entre rondas")

    def test_sem_portao_nao_ha_pedido(self):
        out = S.correr(self.fontes, self.buscar({}), lambda: {"EGRESS_GATE": "BLOCKED"}, dormir=self.sonos.append)
        self.assertEqual([], self.pedidos)
        self.assertEqual({"NAO_MEDIDO": len(IDS)}, out["POR_RESULTADO"])

    def test_classifica_os_recibos_do_vivo(self):
        casos = {
            (0, "URLError: <urlopen error [WinError 10054] Foi forçado o cancelamento de uma conexão"): "FECHO_DE_LIGACAO",
            (0, "URLError: <urlopen error [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake"): "TLS",
            (403, "HTTP 403"): "RECUSA_HTTP",
            (404, "HTTP 404"): "OK",
            (200, ""): "OK",
            (0, "URLError: <urlopen error timed out>"): "SEM_RESPOSTA",
        }
        for (st, err), esperado in casos.items():
            with self.subTest(err=err):
                self.assertEqual(esperado, S.classificar(st, err))

    def test_subdominio_da_coldiretti_e_a_mesma_organizacao(self):
        self.assertEqual("coldiretti.it", S.organizacao("veneto.coldiretti.it"))
        self.assertEqual("coldiretti.it", S.organizacao("www.coldiretti.it"))
        self.assertEqual("unaprol.it", S.organizacao("www.unaprol.it"))


if __name__ == "__main__":
    unittest.main()
