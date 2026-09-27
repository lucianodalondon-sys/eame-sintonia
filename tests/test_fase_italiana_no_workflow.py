#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BG-01 — A FASE ITALIANA DO WORKFLOW CANÓNICO, MEDIDA NO YAML.

    py -m unittest tests.test_fase_italiana_no_workflow

O `sintonia-scrap.yml` é o único sítio onde o portão da Sala (5b) e o portão
do egresso (5c) correm ANTES da aquisição. A fase `italia-documento` nasce
DENTRO dele — e estas provas garantem que ela não nasce torta:

    a bancada nasce ANTES dos portões (5a-IT < 5b) e morre SEMPRE (9z-IT,
    always); a fonte é obrigatória; o alvo deriva do território do
    SOURCE_ID; quem corre é o ORQUESTRADOR, nunca o coletor direto; e a
    Sala da fase é o descartável (SINTONIA_SALA_DSN via GITHUB_ENV), nunca
    a Supabase de produção.

Estas provas leem o YAML — a estrutura. A prova de EXECUÇÃO é a corrida real
da fase, que exige o runner e não cabe num unittest.
"""
import io
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(RAIZ, ".github", "workflows", "sintonia-scrap.yml")


def _texto():
    return io.open(WF, encoding="utf-8").read()


def _yaml():
    import yaml
    return yaml.safe_load(_texto())


def _passos():
    return _yaml()["jobs"]["coleta"]["steps"]


def _indice(passos, prefixo):
    for i, s in enumerate(passos):
        if str(s.get("name", "")).startswith(prefixo):
            return i
    return -1


def _ramo_italia(corpo):
    """O texto do ramo `italia-documento)` do case EXTERNO.

    Não se corta no primeiro `;;`: o ramo tem um `case` interno (o mapa
    território→assunto) cujos `;;` chegam primeiro. O fim do ramo é o início
    do ramo seguinte do case externo — a linha `janela|janela-perfis|...)`.
    """
    m = re.search(r"italia-documento\)\n(.*?)\n\s*janela\|", corpo, re.S)
    return m.group(1) if m else ""


class AFaseItalianaExisteENasceCerta(unittest.TestCase):

    def test_1_a_fase_esta_nas_opcoes(self):
        on = _yaml().get("on") or _yaml().get(True)
        self.assertIn("italia-documento",
                      on["workflow_dispatch"]["inputs"]["fase"]["options"])

    def test_2_a_bancada_nasce_antes_dos_portoes(self):
        p = _passos()
        a, b = _indice(p, "5a-IT"), _indice(p, "5b")
        self.assertGreater(a, -1, "o passo 5a-IT sumiu")
        self.assertLess(a, b, "a bancada tem de nascer ANTES do portao da Sala")

    def test_3_a_bancada_morre_sempre(self):
        p = _passos()
        z = _indice(p, "9z-IT")
        self.assertGreater(z, -1)
        cond = str(p[z].get("if", ""))
        self.assertIn("always()", cond,
                      "sem always(), um FAIL deixa o cluster vivo no runner")

    def test_4_os_portoes_cobrem_a_fase(self):
        """A condição dos 5b/5c é lista de EXCLUSÃO — a fase nova entra
        coberta sem ninguém mexer nos portões."""
        p = _passos()
        for prefixo in ("5b", "5c"):
            cond = str(p[_indice(p, prefixo)].get("if", ""))
            self.assertNotIn("italia", cond,
                             "%s passou a excluir a fase italiana" % prefixo)
            self.assertFalse(p[_indice(p, prefixo)].get("env"),
                             "%s ganhou ambiente proprio" % prefixo)

    def test_5_a_sala_da_fase_e_o_descartavel_e_nao_a_producao(self):
        corpo = _passos()[_indice(_passos(), "5a-IT")]["run"]
        self.assertIn("SINTONIA_SALA_DSN=postgresql://postgres:descartavel"
                      "@localhost:54329/descartavel", corpo)
        self.assertIn("GITHUB_ENV", corpo,
                      "a DSN tem de valer para os passos seguintes do job")
        self.assertNotIn("SUPABASE", corpo.upper().replace("_", ""),
                         "a bancada italiana nao toca em nada de Supabase")

    def test_6_as_migrations_vem_da_cadeia_canonica(self):
        corpo = _passos()[_indice(_passos(), "5a-IT")]["run"]
        self.assertIn("motor/cadeia_canonica.sh migrations", corpo,
                      "nao se inventa segundo aplicador de migrations")

    def test_7_o_banco_da_fase_chama_se_descartavel_em_host_local(self):
        """Os nomes que os guards desta casa aceitam: host local + lista curta."""
        corpo = _passos()[_indice(_passos(), "5a-IT")]["run"]
        self.assertIn("localhost:54329/descartavel", corpo)


class ORamoDaFaseFalaComOOrquestrador(unittest.TestCase):

    def setUp(self):
        p = _passos()
        self.corpo = p[_indice(p, "6")]["run"]
        self.ramo = _ramo_italia(self.corpo)
        self.assertTrue(self.ramo, "o ramo italia-documento sumiu do case")

    def test_8_a_fonte_e_obrigatoria_e_a_falta_sai_com_2(self):
        self.assertIn("FONTE_OBRIGATORIA", self.ramo)
        self.assertIn("exit 2", self.ramo)

    def test_9_o_alvo_deriva_do_territorio_do_source_id(self):
        for pedaco in ("IT-T2-*", "IT-T3-*", "IT-T4-*",
                       "colete clima", "colete pragas", "colete regulatorio"):
            self.assertIn(pedaco, self.ramo, pedaco)

    def test_10_quem_corre_e_o_orquestrador_com_o_filtro_fonte(self):
        self.assertIn("orquestrador/orquestrador.py", self.ramo)
        self.assertIn('--filtro fonte="$FONTE_IT"', self.ramo)

    def test_11_o_ramo_nao_chama_o_coletor_nem_o_adapter_directo(self):
        for proibido in ("italy_pilot_collect", "italy_executor",
                         "italy_recurrent_collect"):
            self.assertNotIn(proibido, self.ramo,
                             "workflow e disparador, nao motor de coleta")

    def test_12_fonte_fora_de_T2_T3_T4_recusa(self):
        self.assertIn("FONTE_FORA_DO_PILOTO", self.ramo)


class ASeguranca(unittest.TestCase):

    def test_13_nenhuma_senha_fora_do_cluster_descartavel(self):
        """`descartavel` é a única credencial escrita, e é a do cluster que
        morre com o job. Nenhum secret novo entra pela fase italiana."""
        corpo = _passos()[_indice(_passos(), "5a-IT")]["run"]
        self.assertNotIn("secrets.", corpo)

    def test_14_o_teardown_apaga_cluster_e_ops_root(self):
        corpo = _passos()[_indice(_passos(), "9z-IT")]["run"]
        self.assertIn("rm -rf", corpo)
        self.assertIn("ops-italia", corpo)

    def test_15_o_ops_root_da_fase_e_temporario(self):
        corpo = _passos()[_indice(_passos(), "5a-IT")]["run"]
        self.assertIn("ITALY_OPS_ROOT=$RUNNER_TEMP", corpo,
                      "sem OPS_ROOT proprio, a fase engordaria o livro "
                      "versionado da arvore do runner")


if __name__ == "__main__":
    unittest.main()
