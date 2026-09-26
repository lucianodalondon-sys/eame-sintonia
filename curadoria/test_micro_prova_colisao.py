# -*- coding: utf-8 -*-
"""MICRO-PROVA × ONDA — a colisão com a rodada 1 e com as últimas 24 h do coletor. Sem rede."""
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import micro_prova_colisao as M   # noqa: E402

RODADAS = """RODADAS 15

RODADA 1: 3 fontes, 14 pedidos previstos
   cnr.it                       5  IT-T5-160(5)
   enea.it                      5  IT-T5-187(5*)
   imagelinenetwork.com         4  IT-T10-021(4)

RODADA 2: 1 fontes
   coldiretti.it                5  IT-T7-050(5)
"""
AGORA = datetime(2026, 9, 26, 6, 0, tzinfo=timezone.utc)


def obs(url, horas_atras):
    return json.dumps({"SOURCE_URL": url, "CAPTURED_AT": (AGORA - timedelta(hours=horas_atras)).isoformat()})


class Colisao(unittest.TestCase):
    def test_so_a_rodada_1_conta(self):
        r1 = M.rodada1(RODADAS)
        self.assertEqual({"cnr.it", "enea.it", "imagelinenetwork.com"}, set(r1))
        self.assertNotIn("coldiretti.it", r1)

    def test_subdominio_colide_pelo_dominio_registavel(self):
        col = M.verificar({"CAND-0003": "https://fitogest.imagelinenetwork.com/"}, M.rodada1(RODADAS), {})
        self.assertEqual("imagelinenetwork.com", col[0]["DOMINIO"])

    def test_ultimas_24h_pelas_observacoes(self):
        linhas = [obs("https://www.enea.it/x", 3), obs("https://www.unaprol.it/y", 30), "{estragada"]
        rec = M.colhidos(linhas, AGORA)
        self.assertEqual({"enea.it": 1}, rec)

    def test_sem_colisao_pode_correr(self):
        col = M.verificar({"IT-T7-051": "https://puglia.coldiretti.it/"}, M.rodada1(RODADAS), {})
        self.assertEqual([], col)

    def test_regional_fica_regional(self):
        self.assertEqual("regione.veneto.it", M.dominio("www.regione.veneto.it"))
        self.assertEqual("coldiretti.it", M.dominio("veneto.coldiretti.it"))


if __name__ == "__main__":
    unittest.main()
