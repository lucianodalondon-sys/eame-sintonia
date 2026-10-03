#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PREFLIGHT — o egresso mede-se antes de adquirir, e UNKNOWN fecha a porta.

⚠️ NENHUM CASO AQUI LIGA VPN NENHUMA
-------------------------------------
Todos injetam o corpo do checker. Uma prova que só passa com a VPN ligada não
se repete, e o que não se repete não é prova.

    UM PORTÃO QUE SÓ SE TESTA COM A VPN LIGADA NÃO SE TESTA.
"""
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "superficie"), os.path.join(RAIZ, "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                                            # noqa: E402,F401
import rede                                                # noqa: E402


def _fonte(caminho):
    # Com `with`, e não sem: um ficheiro deixado aberto num varrimento de árvore
    # inteira enche o descritor do processo e enche o log de avisos.
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


class ODonoJaExistia(unittest.TestCase):
    """⚠️ O EGRESSO É PROPRIEDADE DO AMBIENTE, NUNCA DA FONTE."""

    def test_o_dono_e_o_portao_de_rede(self):
        self.assertTrue(hasattr(rede, "egresso"))
        self.assertTrue(hasattr(rede, "portao_de_egresso"))

    def test_nao_nasceu_um_segundo_dono(self):
        proibidos = ("egress_check.py", "egresso.py", "runner_health.py",
                     "environment_check.py", "preflight.py")
        achados = []
        for base, _dirs, ficheiros in os.walk(RAIZ):
            if any(x in base for x in (".git", "node_modules", "italia-portale")):
                continue
            achados += [f for f in ficheiros if f in proibidos]
        self.assertEqual([], achados)

    def test_o_dono_do_egresso_nao_importa_coletor_nenhum(self):
        """Um preflight que adquire para se provar já não é um preflight."""
        s = _fonte(os.path.join(RAIZ, "superficie", "rede.py"))
        for proibido in ("import instagram", "import youtube", "from coleta",
                         "import coletor", "scrap_executor"):
            self.assertNotIn(proibido, s)

    def test_nao_nasceu_um_compositor(self):
        """⚠️ UM COMPOSITOR QUE SÓ ENCADEIA DOIS DONOS
        É UM TERCEIRO SÍTIO ONDE A VERDADE PODE DIVERGIR.

        Houve um `motor/preflight_da_coleta.py` nesta missão. O próprio System
        Map o apanhou — uma peça nova a morar numa gaveta que não era a do seu
        território — e a pergunta seguinte matou-o: para que serve um terceiro
        ficheiro se cada dono já responde por si e a ordem mora no workflow?
        """
        self.assertFalse(os.path.isfile(
            os.path.join(RAIZ, "motor", "preflight_da_coleta.py")))


class ANormalizacaoEExplicita(unittest.TestCase):
    def test_it_minusculo_e_o_mesmo_pais(self):
        self.assertEqual("IT", rede.egresso(bruto='{"country":"it"}')
                                   ["EGRESS_COUNTRY_CODE"])

    def test_espacos_a_volta_nao_mudam_o_pais(self):
        self.assertEqual("IT", rede.egresso(bruto='{"country":" IT "}')
                                   ["EGRESS_COUNTRY_CODE"])

    def test_o_que_nao_tem_forma_de_pais_e_UNKNOWN(self):
        for corpo in ('{"country":"ITA"}', '{"country":"I"}',
                      '{"country":"1T"}', '{"country":"   "}',
                      '{"country":null}', '{"country":42}'):
            self.assertEqual("UNKNOWN",
                             rede.egresso(bruto=corpo)["EGRESS_COUNTRY_CODE"],
                             corpo)


class OPortaoFechaPorOmissao(unittest.TestCase):
    """⚠️ UNKNOWN != IT."""

    def test_o_pais_exigido_passa(self):
        self.assertEqual("PASS", rede.portao_de_egresso(
            "IT", bruto='{"country":"IT"}')["EGRESS_GATE"])

    def test_outro_pais_bloqueia(self):
        for pais in ("FR", "US", "DE", "GB"):
            self.assertEqual("BLOCKED", rede.portao_de_egresso(
                "IT", bruto='{"country":"%s"}' % pais)["EGRESS_GATE"], pais)

    def test_unknown_bloqueia(self):
        for corpo in (None, "", "<html>500</html>", '{"country":',
                      '{"ip":"1.2.3.4"}', "[]"):
            self.assertEqual("BLOCKED",
                             rede.portao_de_egresso("IT", bruto=corpo)["EGRESS_GATE"],
                             repr(corpo))

    def test_o_None_injetado_nao_vai_a_rede(self):
        """⚠️ DOIS SIGNIFICADOS NO MESMO VALOR É COMO SE LÊ O ERRADO.

        A primeira versão usava `None` para dizer «não me deram corpo, vai
        medir» — e `None` é também o que o checker devolve quando não
        respondeu. A prova do timeout foi à rede a sério e voltou com um país
        verdadeiro: um caso de red team passou por acidente.
        """
        self.assertEqual("UNKNOWN",
                         rede.egresso(bruto=None)["EGRESS_COUNTRY_CODE"])

    def test_o_portao_do_cli_sai_com_codigo(self):
        """Um passo que imprime BLOCKED e devolve zero não fecha porta nenhuma."""
        self.assertIn("sys.exit(0 if v['EGRESS_GATE'] == 'PASS' else 1)",
                      _fonte(os.path.join(RAIZ, "superficie", "rede.py")))


class OSegredoNaoViaja(unittest.TestCase):
    """⚠️ REGISTAR SÓ O QUE FOI PERGUNTADO."""

    CORPO = ('{"ip":"203.0.113.7","city":"Milano","region":"Lombardia",'
             '"country":"IT","org":"AS64500 Exemplo"}')

    def test_o_ip_nao_entra(self):
        self.assertNotIn("203.0.113.7",
                         json.dumps(rede.portao_de_egresso("IT", bruto=self.CORPO)))

    def test_nem_cidade_nem_organizacao(self):
        texto = json.dumps(rede.portao_de_egresso("IT", bruto=self.CORPO))
        self.assertNotIn("Milano", texto)
        self.assertNotIn("AS64500", texto)

    def test_o_que_fica_e_pais_momento_e_checker(self):
        # EGR (24/09): o consenso acrescenta QUEM votou O QUE (so paises, nunca IP),
        # a discordancia, a telemetria sem voto e se a medida veio da cache.
        v = rede.egresso(bruto=self.CORPO, quando="2026-09-13")
        self.assertEqual({"EGRESS_COUNTRY_CODE", "CHECKED_AT", "CHECKER",
                          "PORQUE", "VOTOS", "VOTOS_VALIDOS", "DISCORDANCIA",
                          "TELEMETRIA_SEM_VOTO", "DA_CACHE"}, set(v))


class OLimiteEstaDeclarado(unittest.TestCase):
    """⚠️ VPN_LOCATION != SOURCE_LOCATION != FACT_LOCATION."""

    def test_o_resultado_diz_o_que_nao_prova(self):
        v = rede.portao_de_egresso("IT", bruto='{"country":"IT"}')
        self.assertIn("VPN_LOCATION != SOURCE_LOCATION",
                      v["O_QUE_ISTO_NAO_PROVA"])

    def test_e_nao_devolve_geografia_de_dado(self):
        v = rede.portao_de_egresso("IT", bruto='{"country":"IT"}')
        self.assertEqual([], [k for k in v
                              if k in ("SOURCE_LOCATION", "FACT_LOCATION")])


class AOrdemNoWorkflow(unittest.TestCase):
    """⚠️ MODULE EXISTS != EDGE EXISTS.

    Um portão que existe e não é chamado antes da aquisição não protege nada.
    """

    YML = os.path.join(RAIZ, ".github", "workflows", "sintonia-scrap.yml")

    def test_os_dois_portoes_sao_chamados_antes_do_orquestrador(self):
        s = _fonte(self.YML)
        sala = s.find("sala_de_espera.py --portao")
        egresso = s.find("rede.py --portao-de-egresso")
        orq = s.find("orquestrador/orquestrador.py")
        self.assertGreaterEqual(sala, 0, "o workflow nao chama o portao da sala")
        self.assertGreaterEqual(egresso, 0, "nem o portao do egresso")
        self.assertGreaterEqual(orq, 0)
        self.assertLess(sala, egresso,
                        "a sala tem de vir primeiro: nao custa rede nenhuma")
        self.assertLess(max(sala, egresso), orq, "o portao ficou DEPOIS da porta")

    def test_o_ambiente_aprovado_e_o_ambiente_da_aquisicao(self):
        """⚠️ UM PORTÃO QUE MEDE UM AMBIENTE E DEIXA PASSAR PARA OUTRO
        NÃO MEDIU NADA.

        A primeira versão declarava `SINTONIA_SALA_BACKEND` só dentro do passo
        do preflight: ele passava, e o passo seguinte — o que adquire —
        escrevia o READY no ficheiro efémero.
        """
        import yaml
        d = yaml.safe_load(_fonte(self.YML))
        job = d["jobs"]["coleta"]
        self.assertEqual("POSTGRES", (job.get("env") or {})
                         .get("SINTONIA_SALA_BACKEND"))

    def test_a_condicao_do_preflight_e_lista_de_EXCLUSAO(self):
        """Uma fase nova nasce com o portão ligado, e não sem ele.

            FALHA FECHADA POR OMISSÃO.
        """
        import yaml
        d = yaml.safe_load(_fonte(self.YML))
        passos = [st for st in d["jobs"]["coleta"]["steps"]
                  if str(st.get("name", "")).startswith(("5b", "5c"))]
        self.assertEqual(2, len(passos))
        for st in passos:
            self.assertTrue(str(st["if"]).lstrip().startswith("!"),
                            "a condicao virou lista de INCLUSAO: uma fase nova "
                            "nasceria sem portao")


class OPortaoDaSalaSaiComCodigo(unittest.TestCase):
    """Um passo que imprime BLOCKED e devolve zero deixa a aquisição arrancar."""

    DONO = os.path.join(RAIZ, "admissao", "sala_de_espera.py")

    def _correr(self, **amb):
        base = {k: v for k, v in os.environ.items()
                if k not in ("SINTONIA_SALA_BACKEND", "SINTONIA_SALA_DSN")}
        base.update(amb)
        return subprocess.run([sys.executable, self.DONO, "--portao"],
                              capture_output=True, text=True, env=base)

    def test_sem_backend_canonico_sai_1(self):
        r = self._correr()
        self.assertEqual(1, r.returncode)
        self.assertIn("SALA_DE_ESPERA=BLOCKED", r.stdout)

    def test_postgres_sem_dsn_tambem_sai_1(self):
        r = self._correr(SINTONIA_SALA_BACKEND="POSTGRES")
        self.assertEqual(1, r.returncode)
        self.assertIn("SALA_DE_ESPERA=BLOCKED", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
