#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS ATAQUES AO INSTRUMENTO DA CORRIDA CANONICA.

    py -m unittest discover -s medidas -t . -p "test_corrida_canonica.py"

NENHUMA PROVA AQUI ABRE A REDE, e isso nao e uma promessa — e um mecanismo.
O lancador do coletor e injectado (`lancar`), e a leitura de robots e
substituida caso a caso. Medido nesta casa em 2026-09-21: uma mutacao de red
team desligou o portao e a funcao fez o que sempre fez — foi a fonte, e
colheu tres vezes o boletim da APOL.

    UM TESTE QUE SO E SEGURO ENQUANTO O CODIGO ESTIVER CERTO
    NAO E UM TESTE SEGURO.

O QUE ESTAS PROVAS GUARDAM
--------------------------
As tres perguntas do instrumento, cada uma com o seu dono, e a regra de que
nenhuma responde pela outra:

    elegivel (portao)  !=  percorrivel (contrato)  !=  permitido (robots)

E os quatro estados do robots, que NAO se fundem:

    «nao consegui ler» nunca vira «o site proibiu».
"""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "medidas"))
sys.path.insert(0, str(RAIZ / "coleta"))
sys.path.insert(0, str(RAIZ / "curadoria"))

import corrida_canonica as CC   # noqa: E402
import scrap_http as HTTP       # noqa: E402


class LancadorFalso:
    """O coletor nunca corre. Guarda quem lhe bateu a porta."""

    def __init__(self):
        self.comandos = []

    def __call__(self, comando):
        self.comandos.append(comando)
        return {"CODIGO": 0, "ERRO": "", "CORREU": False, "LANCADOR": "FAKE"}

    @property
    def fontes(self):
        return sorted(a.split("=", 1)[1] for c in self.comandos for a in c
                      if a.startswith("--fonte="))


class OsQuatroEstadosDoRobotsNaoSeFundem(unittest.TestCase):
    """`ROBOTS_GATE_FAIL` nao e `ROBOTS_DISALLOW`, e nunca passa a ser."""

    def setUp(self):
        self._real = HTTP.permitido
        self.addCleanup(setattr, HTTP, "permitido", self._real)

    def _com(self, resposta):
        def falso(url):
            if isinstance(resposta, Exception):
                raise resposta
            return resposta
        HTTP.permitido = falso
        return CC.robots_desta_visita("https://exemplo.it/news/")

    def test_permitido_e_ALLOW_e_deixa_ir(self):
        r = self._com((True, "robots.txt do host permite este caminho"))
        self.assertEqual("ROBOTS_ALLOW", r["ROBOTS_RESULT"])
        self.assertTrue(r["PODE_IR"])

    def test_barrado_e_DISALLOW_e_nao_deixa_ir(self):
        r = self._com((False, "robots.txt do host barra este caminho para SintoniaScrap"))
        self.assertEqual("ROBOTS_DISALLOW", r["ROBOTS_RESULT"])
        self.assertFalse(r["PODE_IR"])

    def test_ilegivel_e_UNREADABLE_e_NAO_e_uma_proibicao(self):
        r = self._com((False, "robots.txt ilegível deste host — não afirmamos permissão que não lemos"))
        self.assertEqual("ROBOTS_UNREADABLE", r["ROBOTS_RESULT"],
                         "um robots ilegivel passou a ser acusado de proibir")
        self.assertFalse(r["PODE_IR"], "ilegivel deixou de travar a visita")

    def test_transporte_caido_e_GATE_FAIL_e_NAO_e_uma_proibicao(self):
        r = self._com(HTTP.PortaoIndisponivel("o transporte caiu antes da resposta"))
        self.assertEqual("ROBOTS_GATE_FAIL", r["ROBOTS_RESULT"],
                         "«nao consegui ler» virou «o site proibiu» — isso e uma "
                         "acusacao ao site, e nao se faz sem prova")
        self.assertFalse(r["PODE_IR"],
                         "nao saber se se pode passou a autorizar a visita")

    def test_nenhum_dos_quatro_estados_deixa_de_dizer_a_LEI(self):
        for r in (self._com((False, "robots.txt ilegível deste host")),
                  self._com(HTTP.PortaoIndisponivel("caiu"))):
            self.assertIn("nao consegui LER", r["LEI"])

    def test_o_veredito_nao_vem_de_cache_de_outra_corrida(self):
        HTTP._ROBOTS["https://exemplo.it"] = ("lixo de outra corrida", "AUSENTE")
        self._com((True, "lido agora"))
        self.assertNotIn("https://exemplo.it", HTTP._ROBOTS,
                         "o cache de robots sobreviveu a visita — entre duas "
                         "corridas o bloqueio ja mudou de fonte nesta casa")


class ASSENHASDeCadaPerguntaNaoSeMisturam(unittest.TestCase):
    """Elegivel, percorrivel e permitido sao TRES perguntas com TRES donos."""

    def setUp(self):
        self._el, self._ct, self._rb = CC.CG.elegiveis, CC.contratos_executaveis, CC.robots_desta_visita
        self.addCleanup(setattr, CC.CG, "elegiveis", self._el)
        self.addCleanup(setattr, CC, "contratos_executaveis", self._ct)
        self.addCleanup(setattr, CC, "robots_desta_visita", self._rb)
        self._painel = CC.CG.painel
        self.addCleanup(setattr, CC.CG, "painel", self._painel)
        CC.CG.painel = lambda **kw: {"FALSO": True}
        # A 4.a pergunta — a admissao que o EXECUTOR faz ao Curator
        # (`italy_executor.admissao_do_curator`, por subprocess ao portao REAL)
        # — nao e o sujeito desta classe, e sem isto o teste lia o LIVRO VIVO:
        # a IT-T7-042 estava READY quando ele foi escrito (03cdd993) e foi
        # despromovida na reconciliacao do cutover (345f0e46, RECONCILIACAO-V1).
        # O portao do executor continua provado pelo seu proprio caminho
        # (`BLOQUEADA_PELO_CURATOR`); aqui responde-se-lhe que sim, como as
        # outras tres perguntas ja sao respondidas pela bancada.
        self._adm = CC.EX.admissao_do_curator
        self.addCleanup(setattr, CC.EX, "admissao_do_curator", self._adm)
        CC.EX.admissao_do_curator = lambda fonte, raiz=None: {
            "ADMITIDA": True, "MOTIVO": "BANCADA"}

    def _monta(self, elegiveis, contratos, robots):
        CC.CG.elegiveis = lambda **kw: list(elegiveis)
        CC.contratos_executaveis = lambda: dict(contratos)
        CC.robots_desta_visita = lambda url, ler=True: dict(robots)
        lanc = LancadorFalso()
        return CC.correr("PROVA", lancar=lanc), lanc

    ROTA_BOA = {"PERCORRIVEL": True, "STRATEGY": "HTML_LINK_DISCOVERY",
                "ENTRADA": "https://exemplo.it/news/"}
    ROBOTS_OK = {"ROBOTS_RESULT": "ROBOTS_ALLOW", "PODE_IR": True, "PORQUE": "permite"}

    def test_elegivel_SEM_contrato_nao_chega_a_rede(self):
        m, lanc = self._monta(["IT-T5-041"], {}, self.ROBOTS_OK)
        self.assertEqual("SEM_ROTA", m["FONTES"][0]["DESFECHO"])
        self.assertEqual([], lanc.fontes,
                         "o coletor foi chamado para uma fonte sem contrato — "
                         "o portao aprovar nao quer dizer que se sabe o caminho")

    def test_nem_se_le_o_robots_de_um_sitio_onde_nao_se_vai(self):
        m, _ = self._monta(["IT-T5-041"], {}, self.ROBOTS_OK)
        self.assertEqual("NAO_LIDO", m["FONTES"][0]["ROBOTS"]["ROBOTS_RESULT"])

    def test_percorrivel_mas_BARRADO_pelo_robots_nao_chega_a_rede(self):
        m, lanc = self._monta(["IT-T7-033"], {"IT-T7-033": self.ROTA_BOA},
                              {"ROBOTS_RESULT": "ROBOTS_DISALLOW", "PODE_IR": False,
                               "PORQUE": "o robots barra"})
        self.assertEqual("ROBOTS_DISALLOW", m["FONTES"][0]["DESFECHO"])
        self.assertEqual([], lanc.fontes, "colheu-se um sitio que disse que nao")

    def test_robots_ILEGIVEL_tambem_nao_chega_a_rede(self):
        m, lanc = self._monta(["IT-T7-033"], {"IT-T7-033": self.ROTA_BOA},
                              {"ROBOTS_RESULT": "ROBOTS_UNREADABLE", "PODE_IR": False,
                               "PORQUE": "ilegivel"})
        self.assertEqual([], lanc.fontes,
                         "nao se conseguiu ler o robots e foi-se na mesma")

    def test_as_tres_verdes_e_ai_sim_o_coletor_e_chamado(self):
        m, lanc = self._monta(["IT-T7-042"], {"IT-T7-042": self.ROTA_BOA}, self.ROBOTS_OK)
        self.assertEqual(["IT-T7-042"], lanc.fontes)

    def test_a_lista_de_fontes_vem_do_PORTAO_e_nao_esta_escrita_aqui(self):
        """Um SOURCE_ID literal neste ficheiro seria um carimbo, nao um portao."""
        with io.open(RAIZ / "medidas" / "corrida_canonica.py", encoding="utf-8") as fh:
            texto = fh.read()
        import re
        # Os SOURCE_ID que aparecem no ficheiro so podem estar em comentario ou
        # docstring — nunca numa lista que o codigo percorra.
        codigo = "\n".join(l.split("#")[0] for l in texto.split("\n"))
        codigo = re.sub(r'"""[\s\S]*?"""', "", codigo)
        achados = re.findall(r"\bIT-T\d+-\d{3}\b", codigo)
        self.assertEqual([], achados,
                         "nasceu uma lista de IDs autorizados dentro do instrumento")

    def test_o_PAID_USD_e_zero_e_diz_porque(self):
        m, _ = self._monta(["IT-T7-042"], {"IT-T7-042": self.ROTA_BOA}, self.ROBOTS_OK)
        self.assertEqual(0.00, m["PAID_USD"])
        self.assertIn("HTTP publico", m["PAID_USD_PORQUE"])


class OTradutorNaoInventaCampo(unittest.TestCase):
    """Campo que o livro nao tem sai AUSENTE — nunca preenchido para agradar."""

    ROBOTS = {"ROBOTS_RESULT": "ROBOTS_ALLOW"}

    def test_livro_vazio_da_tudo_AUSENTE_e_nenhum_valor_bonito(self):
        r = CC.observacao_para_o_relatorio({}, self.ROBOTS)
        for campo in ("DETAIL_URL", "SHA256", "STORAGE_PATH", "BYTES", "FACT_TIME"):
            self.assertIn("AUSENTE_NO_LIVRO", str(r[campo]),
                          "%s nasceu do nada" % campo)

    def test_OBSERVATION_ID_e_RAW_ASSET_ID_dizem_ONDE_nascem(self):
        r = CC.observacao_para_o_relatorio({}, self.ROBOTS)
        for campo in ("OBSERVATION_ID", "RAW_ASSET_ID"):
            self.assertIn("nasce na porta", r[campo],
                          "%s ficou a parecer um campo perdido, e nao uma etapa "
                          "que ainda nao correu" % campo)

    def test_o_HTTP_STATUS_ausente_nao_vira_200(self):
        r = CC.observacao_para_o_relatorio({"OBSERVATION_RESULT": "NEW_DOCUMENT"}, self.ROBOTS)
        self.assertNotIn("200", str(r["HTTP_STATUS"]),
                         "um 200 que ninguem mediu entrou no relatorio")

    def test_o_veredito_do_robots_acompanha_a_observacao(self):
        r = CC.observacao_para_o_relatorio({}, {"ROBOTS_RESULT": "ROBOTS_GATE_FAIL"})
        self.assertEqual("ROBOTS_GATE_FAIL", r["ROBOTS_RESULT"])


class ORunIdCumpreOFormatoCanonico(unittest.TestCase):

    def test_o_alvo_vem_do_SOURCE_ID_e_nao_se_escolhe(self):
        self.assertEqual("T7", CC.alvo_de("IT-T7-033"))
        self.assertEqual("T10", CC.alvo_de("IT-T10-018"))

    def test_o_formato_e_o_do_cunhador_canonico(self):
        import re
        r = CC.cunhar_run_id("IT-T7-033")
        self.assertRegex(r, r"^IT-T7-\d{4}-\d{2}-\d{2}-\d{6}-[0-9a-f]{16}$")

    def test_duas_corridas_nao_partilham_identidade(self):
        self.assertNotEqual(CC.cunhar_run_id("IT-T7-033"), CC.cunhar_run_id("IT-T7-033"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
