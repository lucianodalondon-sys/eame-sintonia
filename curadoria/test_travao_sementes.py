"""S4 -- o travao de sementes: uma semente e uma ORGANIZACAO a explorar, nao uma pagina.

Medido em 23/09 na copia dos livros do servico: 210 sementes tematicas livres,
190 eram paginas internas de organizacoes ja conhecidas, e sherwood.it (a Radio
Sherwood, registada por engano como revista florestal) gerou 14 candidatas-lixo.

Pela porta publica (crawl_sementes), orcamento 0: nenhum pedido a rede, nenhum
ficheiro escrito. As decisoes semanticas vivem num ficheiro temporario.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import descobrir as D            # noqa: E402
import decisao_semantica as DS   # noqa: E402

RAIZ_NOVA = "https://biocontrollo.cia.it/"
PAGINA_INTERNA = "https://www.arpae.it/it/notizie/30-anni-per-l-ambiente"
HOME_DE_JA_SEMEADA = "https://www.crea.gov.it/home"


def _vis(registadas=(), semeadas=(), rejeitadas=()):
    v = {"VISITADOS": {}, "REJEITADOS": {}}
    for u in registadas:
        v["VISITADOS"][D.normalizar(u)] = {"AT": "x", "MOTIVO": "REGISTADO_CAND-9999"}
    for u in semeadas:
        v["VISITADOS"][D.normalizar(u)] = {"AT": "x", "MOTIVO": "SEMENTE_PROCESSADA"}
    for u in rejeitadas:
        v["REJEITADOS"][D.normalizar(u)] = {"AT": "x", "MOTIVO": "ROBOTS_BLOCKED_SEMENTE"}
    return v


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="travao-"))
        self.decisoes = self.tmp / "decisoes.json"
        self._dec([])

    def _dec(self, decisoes):
        self.decisoes.write_text(json.dumps({"DECISOES": decisoes}), encoding="utf-8")

    def _correr(self, sementes, visitados, catalogo=()):
        s2 = [{"URL": u, "CANDIDATA_ID": cid, "ONDE_VIU": "x", "CLASSIFICACAO": "t"}
              for cid, u in sementes]
        with mock.patch.object(D, "_extrair_sementes_legitimas", return_value=list(catalogo)), \
             mock.patch.object(D, "_sementes_de_segunda_geracao", return_value=s2), \
             mock.patch.object(D, "_gravar_visitados", lambda *_a, **_k: None), \
             mock.patch.object(DS, "DECISOES", self.decisoes):
            _, stats = D.crawl_sementes(D.Orcamento(total=0), set(), visitados, [],
                                        max_sementes=15)
        return stats


class TestTravaoDeixaPassar(_Base):

    def test_entrada_de_organizacao_nova_vira_semente(self):
        st = self._correr([("CAND-9001", RAIZ_NOVA)], _vis(registadas=[RAIZ_NOVA]))
        self.assertEqual(st["SEMENTES_A_USAR"], 1)
        self.assertEqual(st["SEMENTES_TRAVADAS"], {})

    def test_prova_insuficiente_nao_trava(self):
        """Falta de prova nao e prova de lixo."""
        self._dec([{"CANDIDATA_ID": "CAND-9001", "TERRITORIO": "NAO SEI",
                    "CATEGORIA": "PROVA_INSUFICIENTE", "MOTIVO": "404"}])
        st = self._correr([("CAND-9001", RAIZ_NOVA)], _vis(registadas=[RAIZ_NOVA]))
        self.assertEqual(st["SEMENTES_A_USAR"], 1)

    def test_catalogo_nao_passa_pelo_travao(self):
        """So a 2.a geracao e travada; o catalogo continua como era."""
        st = self._correr([], _vis(), catalogo=[PAGINA_INTERNA])
        self.assertEqual(st["SEMENTES_A_USAR"], 1)


class TestTravaoPara(_Base):

    def _travada(self, sementes, visitados, motivo):
        st = self._correr(sementes, visitados)
        self.assertEqual(st["SEMENTES_A_USAR"], 0, st)
        self.assertEqual(st["SEMENTES_TRAVADAS"], {motivo: len(sementes)})

    def test_pagina_interna_nao_vira_semente(self):
        self._travada([("CAND-9002", PAGINA_INTERNA)], _vis(registadas=[PAGINA_INTERNA]),
                      "PAGINA_INTERNA")

    def test_pagina_com_query_nao_e_entrada(self):
        u = "https://www.crea.gov.it/?p_l_id=40632"
        self._travada([("CAND-9003", u)], _vis(registadas=[u]), "PAGINA_INTERNA")

    def test_home_de_organizacao_ja_semeada(self):
        self._travada([("CAND-9004", HOME_DE_JA_SEMEADA)],
                      _vis(registadas=[HOME_DE_JA_SEMEADA], semeadas=["https://www.crea.gov.it/"]),
                      "ORGANIZACAO_JA_SEMEADA")

    def test_organizacao_recusada_como_semente_tambem_conta(self):
        u = "https://puglia.coldiretti.it/home"
        self._travada([("CAND-9005", u)],
                      _vis(registadas=[u], rejeitadas=["https://puglia.coldiretti.it/"]),
                      "ORGANIZACAO_JA_SEMEADA")

    def test_identidade_trocada_nao_semeia(self):
        u = "https://www.sherwood.it/"
        self._dec([{"CANDIDATA_ID": "CAND-0257", "TERRITORIO": "NAO SEI",
                    "CATEGORIA": "IDENTIDADE_TROCADA", "MOTIVO": "radio, nao revista"}])
        self._travada([("CAND-0257", u)], _vis(registadas=[u]),
                      "DECISAO_SEMANTICA_IDENTIDADE_TROCADA")

    def test_nao_fonte_e_pagina_de_outra_fonte_nao_semeiam(self):
        for cat in ("NAO_E_FONTE", "PAGINA_DE_OUTRA_FONTE", "SEMENTE_ERRADA"):
            with self.subTest(cat=cat):
                self._dec([{"CANDIDATA_ID": "CAND-9006", "TERRITORIO": "NAO SEI",
                            "CATEGORIA": cat, "MOTIVO": "x"}])
                self._travada([("CAND-9006", RAIZ_NOVA)], _vis(registadas=[RAIZ_NOVA]),
                              "DECISAO_SEMANTICA_" + cat)

    def test_semente_gasta_continua_gasta_e_nao_conta_como_travada(self):
        st = self._correr([("CAND-9007", RAIZ_NOVA)], _vis(semeadas=[RAIZ_NOVA]))
        self.assertEqual(st["SEMENTES_A_USAR"], 0)
        self.assertEqual(st["SEMENTES_TRAVADAS"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
