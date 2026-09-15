# -*- coding: utf-8 -*-
"""MEDIR UM BACKEND APOSENTADO NÃO PROVA O ESTADO DO ACTUAL.

`provas/a_fronteira_da_coleta.py` respondia «a Sala de Espera nunca recebeu
nada» a partir de uma linha só:

    produzido = os.path.isdir('data/samples/PRONTO-PARA-INTELIGENCIA')

Essa pasta é a morada do backend **FICHEIRO**, que a própria Sala declara
`CANONICO = False`. A Sala canónica é Postgres, e a prova nunca lhe perguntou
nada — não importava `sala_de_espera`, não abria ligação, não chamava o dono.
De um disco vazio saía:

    GAP = READY_NUNCA_PRODUZIDO   ·   «NUNCA foi produzido um READY»

e daí o mapa pintava `M-READY` bloqueado, e o texto dizia que a sala nunca
recebeu nada — com `pedido-t4.observado.json`, na mesma pasta, a mostrar a
unidade pousada.

    AUSÊNCIA DE MEDIÇÃO NÃO É MEDIÇÃO DE AUSÊNCIA.
    NOT_OBSERVED != DOES_NOT_EXIST.  UNKNOWN != NO.  ERROR != ZERO.

Estas travas prendem a semântica, e não os nomes: cada uma monta um mundo e
pergunta o que a prova conclui dele.
"""
import importlib.util
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _medidor():
    spec = importlib.util.spec_from_file_location(
        "_fronteira_sala", os.path.join(RAIZ, "provas", "a_fronteira_da_coleta.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class _SalaFalsa(object):
    """Um dono de mentira, com a MESMA superfície do verdadeiro.

    ⚠️ Ele imita a API, e não o banco. Trocar `listar_pendentes` por uma lista
    testa o que esta prova conclui; trocar a tabela testaria o Postgres, que
    não é o que aqui está partido.
    """

    # A excepção é a REAL, importada do dono. Uma cópia local passaria no
    # teste e falharia na vida: o `except` da prova apanha a classe dele.
    def __init__(self, estado, pendentes=None, erro=None, erro_no_estado=None):
        self._estado = estado
        self._pendentes = pendentes
        self._erro = erro
        self._erro_no_estado = erro_no_estado
        self.BACKEND_FICHEIRO = "FICHEIRO"

    def estado_operacional(self):
        if self._erro_no_estado:
            raise self._erro_no_estado
        return self._estado

    def listar_pendentes(self, limite=None):
        if self._erro:
            raise self._erro
        return list(self._pendentes or [])


CANONICA_DE_PE = {"BACKEND": "POSTGRES", "CANONICO": True, "DISPONIVEL": True,
                  "PORQUE": "a fila vive numa tabela com unicidade"}
SO_FICHEIRO = {"BACKEND": "FICHEIRO", "CANONICO": False, "DISPONIVEL": True,
               "PORQUE": "o ficheiro vive no workspace do runner"}
SEM_DSN = {"BACKEND": "POSTGRES", "CANONICO": False, "DISPONIVEL": False,
           "PORQUE": "SINTONIA_SALA_BACKEND=POSTGRES sem DSN"}


class ASalaEPerguntadaAoDonoDela(unittest.TestCase):
    """Os quatro mundos do enunciado, um a um."""

    def setUp(self):
        self.m = _medidor()

    def sala(self, falsa):
        self.m.espera = falsa
        return self.m.a_sala_canonica()

    # ── CASO C · sem runtime canónico ────────────────────────────────────
    def test_1_sem_dsn_e_NOT_MEASURED_e_nunca_um_veredito(self):
        r = self.sala(_SalaFalsa(SEM_DSN))
        self.assertEqual(r["READY_PRODUZIDO"], "NOT_MEASURED")
        self.assertEqual(r["SALA_MEDICAO"], "NOT_MEASURED")
        self.assertIsNone(r["SALA_PENDENTES"],
                          "sem medição não há número, e zero seria um número")
        gap, porque = self.m.o_estado_da_fronteira(r["READY_PRODUZIDO"], [])
        self.assertEqual(gap, "SALA_NAO_MEDIDA")
        self.assertNotIn("NUNCA", (porque or "").upper(),
                         "falta de medição não pode sair como «nunca produziu»")

    def test_1b_o_backend_de_ficheiro_disponivel_nao_conta_como_medicao(self):
        """DISPONÍVEL não é CANÓNICO — e é aqui que a árvore real cai.

        Sem variável de ambiente nenhuma, `backend()` devolve o FICHEIRO: ele
        está de pé e não é o dono do READY operacional. Ler o vazio DELE como
        estado da Sala é o defeito original, uma camada acima.
        """
        r = self.sala(_SalaFalsa(SO_FICHEIRO))
        self.assertTrue(r["SALA_DISPONIVEL"])
        self.assertFalse(r["SALA_CANONICO"])
        self.assertEqual(r["READY_PRODUZIDO"], "NOT_MEASURED")

    # ── CASO A · canónica, com material ──────────────────────────────────
    def test_2_sala_canonica_com_material_e_SIM_com_o_numero(self):
        r = self.sala(_SalaFalsa(CANONICA_DE_PE, pendentes=[
            {"RUN_ID": "IT-T3-1", "ORDEM": 0, "ITEM_ID": "derived:5"},
            {"RUN_ID": "IT-T3-1", "ORDEM": 1, "ITEM_ID": "derived:6"}]))
        self.assertEqual(r["READY_PRODUZIDO"], "SIM")
        self.assertEqual(r["SALA_MEDICAO"], "MEDIDA")
        self.assertEqual(r["SALA_PENDENTES"], 2)
        self.assertIsNone(self.m.o_estado_da_fronteira("SIM", [])[0],
                          "READY produzido com zero consumidores é o ALVO")

    # ── CASO B · canónica, vazia agora ───────────────────────────────────
    def test_3_sala_vazia_agora_nao_vira_nunca_recebeu_nada(self):
        """Quem já foi `retirar()` sai da fila. Zero à espera não é zero histórico."""
        r = self.sala(_SalaFalsa(CANONICA_DE_PE, pendentes=[]))
        self.assertEqual(r["SALA_MEDICAO"], "MEDIDA")
        self.assertEqual(r["SALA_PENDENTES"], 0)
        self.assertEqual(
            r["READY_PRODUZIDO"], "NOT_MEASURED",
            "a API canónica responde «quem espera AGORA». Concluir «nunca "
            "chegou» daí é responder uma pergunta que não foi feita.")
        gap, porque = self.m.o_estado_da_fronteira(r["READY_PRODUZIDO"], [])
        self.assertNotIn("NUNCA", (porque or "").upper())

    # ── CASO D · a consulta rebentou ─────────────────────────────────────
    def test_4_erro_de_consulta_e_ERROR_e_nao_zero_nem_bloqueio(self):
        import sys
        sys.path.insert(0, RAIZ)
        import _gavetas  # noqa: F401
        import sala_de_espera
        r = self.sala(_SalaFalsa(
            CANONICA_DE_PE,
            erro=sala_de_espera.SalaIndisponivel("connection refused")))
        self.assertEqual(r["READY_PRODUZIDO"], "ERROR")
        self.assertIsNone(r["SALA_PENDENTES"], "ERRO != ZERO")
        gap, porque = self.m.o_estado_da_fronteira("ERROR", [])
        self.assertEqual(gap, "SALA_ERRO_DE_CONSULTA")
        self.assertNotIn("NUNCA", (porque or "").upper())
        self.assertIn("ZERO", (porque or "").upper(),
                      "o motivo tem de dizer que isto não é zero")

    def test_4b_ate_o_estado_operacional_pode_rebentar_e_continua_ERROR(self):
        r = self.sala(_SalaFalsa(None, erro_no_estado=RuntimeError("psql sumiu")))
        self.assertEqual(r["READY_PRODUZIDO"], "ERROR")
        self.assertIsNone(r["SALA_PENDENTES"])

    # ── CASO 5 · o artefato antigo não governa mais ──────────────────────
    def test_5_a_pasta_da_v1_nao_governa_o_estado_da_sala(self):
        """Com a pasta lá e sem a pasta, a resposta da Sala é a mesma."""
        import tempfile
        r_sem = self.sala(_SalaFalsa(SEM_DSN))
        pasta = os.path.join(RAIZ, "data", "samples", "PRONTO-PARA-INTELIGENCIA")
        criada = False
        try:
            if not os.path.isdir(pasta):
                os.makedirs(pasta)
                criada = True
            r_com = self.sala(_SalaFalsa(SEM_DSN))
        finally:
            if criada:
                os.rmdir(pasta)
        self.assertEqual(r_sem, r_com,
                         "a existência da morada da V1 não pode mudar nada do "
                         "que se sabe sobre a Sala canónica")
        del tempfile

    def test_5b_a_prova_escreve_o_veredito_que_veio_do_dono(self):
        """Estrutural, e de propósito: o campo tem de vir de `a_sala_canonica`."""
        with open(os.path.join(RAIZ, "provas", "a_fronteira_da_coleta.py"),
                  encoding="utf-8") as f:
            linhas = [l.strip() for l in f
                      if l.strip().startswith('"READY_PRODUZIDO":')
                      and not l.lstrip().startswith("#")]
        # As de dentro de `a_sala_canonica()` são legítimas: é lá que o
        # veredito NASCE. A que importa aqui é a que o ARTEFATO leva, e ela
        # tem de vir da Sala — nunca do disco.
        do_artefato = [l for l in linhas if "sala[" in l]
        self.assertEqual(len(do_artefato), 1,
                         "esperava uma única escrita do campo no artefato")
        for l in linhas:
            self.assertNotIn("isdir", l, "o veredito não pode vir do disco: " + l)
            self.assertNotIn("produzido", l,
                             "o booleano da pasta da V1 não pode voltar: " + l)

    def test_5c_o_medidor_importa_o_dono_da_sala(self):
        self.assertTrue(hasattr(self.m, "espera"),
                        "a prova tem de consultar `admissao/sala_de_espera.py` "
                        "— o owner canónico — e não a tabela nem o disco")

    # ── O VOCABULÁRIO NÃO GANHOU UM «NÃO» QUE NINGUÉM PODE PROVAR ────────
    def test_nao_existe_veredito_negativo_neste_medidor(self):
        for mundo in (_SalaFalsa(SEM_DSN), _SalaFalsa(SO_FICHEIRO),
                      _SalaFalsa(CANONICA_DE_PE, pendentes=[]),
                      _SalaFalsa(CANONICA_DE_PE, pendentes=[{"x": 1}])):
            r = self.sala(mundo)
            self.assertIn(r["READY_PRODUZIDO"], ("SIM", "NOT_MEASURED", "ERROR"))
            self.assertNotEqual(r["READY_PRODUZIDO"], "NAO")


class ORedTeamDaSala(unittest.TestCase):
    """As oito hipóteses do enunciado, cada uma como uma trava."""

    def setUp(self):
        self.m = _medidor()

    def sala(self, falsa):
        self.m.espera = falsa
        return self.m.a_sala_canonica()

    def test_RT1_sem_dsn_o_gap_nao_e_um_bloqueio(self):
        gap, porque = self.m.o_estado_da_fronteira(
            self.sala(_SalaFalsa(SEM_DSN))["READY_PRODUZIDO"], [])
        self.assertEqual(gap, "SALA_NAO_MEDIDA")
        for proibido in ("BLOQUEAD", "NUNCA", "NAO EXISTE"):
            self.assertNotIn(proibido, (porque or "").upper())

    def test_RT2_diretorio_antigo_vazio_nao_vence_o_postgres(self):
        cheia = self.sala(_SalaFalsa(CANONICA_DE_PE, pendentes=[{"x": 1}]))
        self.assertEqual(cheia["READY_PRODUZIDO"], "SIM",
                         "a pasta da V1 está vazia nesta árvore e não pode "
                         "derrubar o que o backend canónico respondeu")

    def test_RT3_artefato_historico_nao_vira_material_actual(self):
        """Um ficheiro histórico com material não pode dizer que há fila hoje."""
        r = self.sala(_SalaFalsa(CANONICA_DE_PE, pendentes=[]))
        self.assertNotEqual(r["READY_PRODUZIDO"], "SIM")
        self.assertEqual(r["SALA_PENDENTES"], 0)

    def test_RT4_erro_de_ligacao_nao_vira_zero(self):
        import sys
        sys.path.insert(0, RAIZ)
        import _gavetas  # noqa: F401
        import sala_de_espera
        r = self.sala(_SalaFalsa(
            CANONICA_DE_PE, erro=sala_de_espera.SalaIndisponivel("timeout")))
        self.assertIsNone(r["SALA_PENDENTES"])
        self.assertNotEqual(r["SALA_PENDENTES"], 0)

    def test_RT5_a_prova_chama_o_owner_real_e_nao_uma_copia(self):
        import sys
        sys.path.insert(0, RAIZ)
        import _gavetas  # noqa: F401
        import sala_de_espera
        m = _medidor()
        self.assertIs(m.espera, sala_de_espera,
                      "`espera` tem de ser o módulo canónico, e não um clone")
        self.assertTrue(hasattr(sala_de_espera, "estado_operacional"))
        self.assertTrue(hasattr(sala_de_espera, "listar_pendentes"))

    def test_RT6_o_consumidor_a_jusante_nao_converte_UNKNOWN_em_travessia(self):
        """`bool("NOT_MEASURED")` é `True`. O censo não pode usá-lo."""
        caminho = os.path.join(RAIZ, "system-map", "scripts",
                               "censo_cards_sensores.py")
        with open(caminho, encoding="utf-8") as f:
            fonte = f.read()
        atribuicoes = [l.strip() for l in fonte.splitlines()
                       if l.strip().startswith("atravessou =")]
        self.assertEqual(len(atribuicoes), 1)
        self.assertNotIn("bool(", atribuicoes[0],
                         "converter três estados em booleano decide o terceiro "
                         "em silêncio. Linha: " + atribuicoes[0])
        self.assertIn('"SIM"', atribuicoes[0])

    def _censo(self):
        import importlib.util
        caminho = os.path.join(RAIZ, "system-map", "scripts",
                               "censo_cards_sensores.py")
        spec = importlib.util.spec_from_file_location("_censo_sala", caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _fronteira(self, medicao, **extra):
        base = {"LEI": "COL-LAW-043", "READY_PRODUZIDO": medicao,
                "SALA_BACKEND": "FICHEIRO", "SALA_CANONICO": False,
                "SALA_MEDICAO": medicao, "SALA_PORQUE": "sem DSN"}
        base.update(extra)
        return base

    def test_RT7_todo_leitor_do_artefato_usa_o_vocabulario_novo(self):
        """Uma camada a jusante que ainda faça `bool()` reacende o defeito.

        `bool("NOT_MEASURED") is True`: quem não foi atualizado não fica
        pessimista — fica OPTIMISTA, e diz que 58 sensores atravessaram.
        """
        import re
        maus = []
        for pasta in ("system-map/scripts", "provas", "medidas", "superficie"):
            raiz = os.path.join(RAIZ, *pasta.split("/"))
            if not os.path.isdir(raiz):
                continue
            for base, _, ficheiros in os.walk(raiz):
                if "__pycache__" in base:
                    continue
                for nome in ficheiros:
                    if not nome.endswith(".py"):
                        continue
                    caminho = os.path.join(base, nome)
                    with open(caminho, encoding="utf-8", errors="ignore") as f:
                        for i, linha in enumerate(f, 1):
                            if linha.lstrip().startswith("#"):
                                continue
                            if re.search(r"bool\([^)]*READY_PRODUZIDO", linha):
                                maus.append("%s:%d" % (
                                    os.path.relpath(caminho, RAIZ), i))
        self.assertEqual(maus, [], "estes ainda convertem o veredito da Sala "
                                   "para booleano: %s" % maus)

    def test_RT8_o_motivo_publicado_distingue_NAO_MEDIDO_de_NAO_HOUVE(self):
        """Semântico: corre o censo a sério e lê o que ele publica."""
        censo = self._censo()
        ss, _ = censo.sensores(self._fronteira("NOT_MEASURED"))
        motivo = ss[0]["PORQUE_NAO_ENTROU"].upper()
        self.assertFalse(ss[0]["ENTROU_NA_CADEIA"])
        self.assertIn("NAO FOI MEDIDA", motivo)
        self.assertNotIn("NUNCA", motivo,
                         "não medir não é «nunca produziu»")

        ss, _ = censo.sensores(self._fronteira("ERROR"))
        motivo = ss[0]["PORQUE_NAO_ENTROU"].upper()
        self.assertIn("REBENTOU", motivo)
        self.assertIn("ZERO", motivo, "ERRO != ZERO tem de estar escrito")
        self.assertNotIn("NUNCA", motivo)

        ss, _ = censo.sensores(self._fronteira("SIM", SALA_PENDENTES=3))
        self.assertTrue(ss[0]["ENTROU_NA_CADEIA"])
        self.assertIsNone(ss[0]["PORQUE_NAO_ENTROU"])


if __name__ == "__main__":
    unittest.main()
