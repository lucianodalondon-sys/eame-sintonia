"""C1 -- REGISTADO como candidata != RASTEJADO como semente.

Medido em 23/09 (copia dos livros do servico): 166 sementes, 6 livres; 125
sementes de 2.a geracao estavam fora do crawl so porque o link tinha sido
REGISTADO como candidata (VISITADOS[...].MOTIVO = "REGISTADO_CAND-xxxx").

Os testes vao pela porta publica (crawl_sementes) com orcamento 0: nenhum
pedido a rede, nenhum ficheiro escrito (_gravar_visitados substituido).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import descobrir as D  # noqa: E402

TEMATICA = "https://www.coldiretti.it/"
TEMATICA_2 = "https://www.arpae.it/"
UNKNOWN = "https://www.cnr.it/it/istituto?cds=0"
GENERICA = "https://www.regione.calabria.it/"


def _correr(sementes: list[str], visitados: dict) -> tuple[dict, list[dict]]:
    s2 = [{"URL": u, "CANDIDATA_ID": "CAND-%04d" % i, "ONDE_VIU": "x",
           "CLASSIFICACAO": "t"} for i, u in enumerate(sementes)]
    log: list[dict] = []
    with mock.patch.object(D, "_extrair_sementes_legitimas", return_value=[]), \
         mock.patch.object(D, "_sementes_de_segunda_geracao", return_value=s2), \
         mock.patch.object(D, "_gravar_visitados", lambda *_a, **_k: None):
        _, stats = D.crawl_sementes(D.Orcamento(total=0), set(), visitados,
                                    log, max_sementes=15)
    return stats, log


def _vis(**por_url) -> dict:
    v = {"VISITADOS": {}, "REJEITADOS": {}}
    for url, (livro, motivo) in por_url.items():
        v[livro][D.normalizar(url)] = {"AT": "2026-09-23", "MOTIVO": motivo}
    return v


class TestRegistadoNaoImpedeSemente(unittest.TestCase):

    def test_candidata_registada_tematica_vira_semente(self):
        v = _vis(**{TEMATICA: ("VISITADOS", "REGISTADO_CAND-0125")})
        stats, log = _correr([TEMATICA], v)
        self.assertEqual(stats["SEMENTES_A_USAR"], 1)
        self.assertEqual(stats["SEMENTES_TEMATICAS_USADAS"], 1)
        self.assertFalse([e for e in log if e.get("acao") == "SEMENTE_JA_VISITADA"])

    def test_varias_registadas_todas_livres(self):
        v = _vis(**{TEMATICA: ("VISITADOS", "REGISTADO_CAND-0001"),
                    TEMATICA_2: ("VISITADOS", "REGISTADO_CAND-0002")})
        stats, _ = _correr([TEMATICA, TEMATICA_2], v)
        self.assertEqual(stats["SEMENTES_A_USAR"], 2)


class TestSementeGastaContinuaFora(unittest.TestCase):

    def test_semente_processada_nao_repete(self):
        v = _vis(**{TEMATICA: ("VISITADOS", "SEMENTE_PROCESSADA")})
        stats, _ = _correr([TEMATICA], v)
        self.assertEqual(stats["SEMENTES_A_USAR"], 0)

    def test_rejeitada_continua_fora(self):
        v = _vis(**{TEMATICA: ("REJEITADOS", "ROBOTS_BLOCKED_SEMENTE")})
        stats, _ = _correr([TEMATICA], v)
        self.assertEqual(stats["SEMENTES_A_USAR"], 0)

    def test_registada_e_rejeitada_continua_fora(self):
        v = _vis(**{TEMATICA: ("VISITADOS", "REGISTADO_CAND-0003")})
        v["REJEITADOS"][D.normalizar(TEMATICA)] = {"AT": "x", "MOTIVO": "HTTP_404"}
        stats, _ = _correr([TEMATICA], v)
        self.assertEqual(stats["SEMENTES_A_USAR"], 0)

    def test_regra_nao_afrouxa_unknown_e_generica(self):
        v = _vis(**{UNKNOWN: ("VISITADOS", "REGISTADO_CAND-0004"),
                    GENERICA: ("VISITADOS", "REGISTADO_CAND-0005")})
        stats, _ = _correr([UNKNOWN, GENERICA], v)
        self.assertEqual(stats["SEMENTES_TEMATICAS_USADAS"], 0)
        self.assertEqual(stats["SEMENTES_GENERICAS_RECUSADAS"], 2)

    def test_tecto_por_corrida_mantido(self):
        urls = ["https://www.coldiretti.it/p%d" % i for i in range(40)]
        v = _vis(**{u: ("VISITADOS", "REGISTADO_CAND-%04d" % i)
                    for i, u in enumerate(urls)})
        stats, _ = _correr(urls, v)
        self.assertEqual(stats["SEMENTES_A_USAR"], 15)


if __name__ == "__main__":
    unittest.main()
