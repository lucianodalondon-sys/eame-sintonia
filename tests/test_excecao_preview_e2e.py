# -*- coding: utf-8 -*-
"""D140 · A EXCEÇÃO CONTROLADA PREVIEW_E2E — estreita no contrato E na guarda.

    COLLECTION_FOUNDATION_CLOSED = NAO   (continua)
    EXCECOES_CONTROLADAS[PREVIEW_E2E]    (so o preview do Casco original)

O red team (17:20) disse porque isto e um teste e nao um paragrafo: um bloco
novo no JSON, sozinho, nao abre rota nenhuma — e se a guarda nao o conhecer, o
contrato diz uma coisa e a maquina faz outra.

Cada classe abaixo responde a uma das seis perguntas da missao:

    (a) a excecao nao muda FOUNDATION_CLOSED
    (b) destino producao/cliente continua bloqueado
    (c) objeto EXPERIMENTAL/NAO_PARA_CLIENTE continua bloqueado
    (d) escrita na Sala continua bloqueada
    (e) sem a entrada D140 volta a bloquear tudo
    (f) remover a excecao da guarda faz o teste do preview reprovar

Os mutantes que provam que estes testes mordem estao em
`provas/l1_governanca/mutantes_excecao_preview.py`.
"""
import copy
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import fundacao_da_coleta as lei  # noqa: E402

sys.path.insert(0, os.path.join(RAIZ, "pacote"))
import pote_intelligence_casco as P  # noqa: E402

CORRIDA = os.path.join(RAIZ, "tests", "fixtures", "pote", "CORRIDA-SINTETICA-V2-UNICO.json")
LIBERADO = "LIBERADO_PARA_CLIENTE"


def _pote_liberado():
    """O pote sintetico do repositorio, com cada objeto liberado pelo contrato v2.2."""
    with open(CORRIDA, encoding="utf-8") as f:
        pote = P.ler_entrada(json.load(f))
    for e in pote["COMPARTIMENTOS"].values():
        for o in e["OBJETOS"]:
            o["LIBERACAO"] = LIBERADO
            o["LIBERADO_POR"] = "INTELLIGENCE"
            o["LIBERADO_NA_CORRIDA"] = pote["INTELLIGENCE_RUN_ID"]
            o["CONFERENCIA_DE_LIBERACAO"] = dict.fromkeys(lei.CONFERENCIAS_QUE_PASSAM, "PASSOU")
            o["CONFERENCIA_DE_LIBERACAO"][lei.DECISAO_DO_DONO] = "D-sintetica-do-teste"
    return pote


class Base(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.trava, cls.diario, cls.publicacao = lei.carregar()
        cls.pote = _pote_liberado()

    def pedido(self, **muda):
        p = {
            "OPERACAO": lei.PUBLICAR_NO_PREVIEW,
            "DESTINO": {"TIPO": "BUILD_LOCAL", "BRANCH": "claude/l3-radar-original-v1",
                        "HOST": None, "PARA_CLIENTE": False},
            "ENTRADA": {"TIPO": lei.ENTRADA_READ_ONLY, "READ_ONLY": True},
            "POTE": copy.deepcopy(self.pote),
            "PROVA_REVERSA_DO_LAB": {"VEREDITO": "PASS", "ONDE": "provas/l3/PARA-O-LAB.md"},
        }
        for k, v in muda.items():
            if isinstance(v, dict) and isinstance(p.get(k), dict):
                p[k].update(v)
            else:
                p[k] = v
        return p

    def atravessa(self, pedido, trava=None, diario=None):
        return lei.pode_atravessar_a_trava(
            pedido, self.trava if trava is None else trava,
            self.diario if diario is None else diario, self.publicacao)

    def recusa(self, pedido, trava=None, diario=None):
        pode, motivo = self.atravessa(pedido, trava, diario)
        self.assertFalse(pode, "a guarda deixou passar: %s" % motivo)
        self.assertIn(lei.BLOQUEIO, motivo)
        return motivo

    def sem_excecao(self):
        t = copy.deepcopy(self.trava)
        t.pop("EXCECOES_CONTROLADAS", None)
        return t

    def com_entrada(self, **muda):
        t = copy.deepcopy(self.trava)
        for e in t["EXCECOES_CONTROLADAS"]:
            if e["ID"] == lei.EXCECAO_PREVIEW:
                e.update(muda)
        return t


class F_OPreviewDeclaradoPassa(Base):
    """(f) O caminho estreito existe e passa. Se a excecao sair da guarda, estes
    reprovam — e e isso que distingue uma excecao executavel de um paragrafo."""

    def test_f_pedido_de_preview_completo_atravessa(self):
        pode, motivo = self.atravessa(self.pedido())
        self.assertTrue(pode, motivo)
        self.assertIn("EXCECAO PREVIEW_E2E (D140)", motivo)
        self.assertIn("COLLECTION_FOUNDATION_CLOSED continua NAO", motivo)

    def test_f_preview_da_vercel_numa_branch_que_nao_e_de_promocao_atravessa(self):
        pode, motivo = self.atravessa(self.pedido(DESTINO={
            "TIPO": "VERCEL_PREVIEW", "HOST": "sintonia-eame-git-l3-radar-x.vercel.app"}))
        self.assertTrue(pode, motivo)

    def test_f_a_mesma_trava_sem_a_excecao_recusa_o_mesmo_pedido(self):
        self.recusa(self.pedido(), trava=self.sem_excecao())


class G_PreviewSimProducaoNaoVazamentoZero(Base):
    """D152 · o estado pedido pelo dono, provado na guarda que governa a execucao:

        PREVIEW_PODE_RECEBER            = SIM
        PRODUCAO_PODE_RECEBER           = NAO   (fail-closed, mesmo com pote LIBERADO)
        VAZAMENTO_PREVIEW_PARA_PRODUCAO = 0
    """

    def _producao(self, d):
        return (d.get("BRANCH") in self.publicacao["PROMOTION_AUTHORITY_BRANCHES"]
                or d.get("HOST") == self.publicacao["CANONICAL_HOST"]
                or d.get("PARA_CLIENTE") is not False
                or d.get("TIPO") not in ("BUILD_LOCAL", "VERCEL_PREVIEW"))  # regua fixa, nao a do codigo

    def test_PREVIEW_PODE_RECEBER_SIM(self):
        for d in ({"TIPO": "BUILD_LOCAL", "HOST": None},
                  {"TIPO": "BUILD_LOCAL", "HOST": "127.0.0.1"},
                  {"TIPO": "VERCEL_PREVIEW", "HOST": "sintonia-eame-git-l3-x.vercel.app"}):
            pode, motivo = self.atravessa(self.pedido(DESTINO=d))
            self.assertTrue(pode, "PREVIEW_PODE_RECEBER = NAO para %s: %s" % (d, motivo))

    def test_PRODUCAO_PODE_RECEBER_NAO_mesmo_com_pote_liberado(self):
        # o pote do pedido tem TODOS os objetos LIBERADO_PARA_CLIENTE e passa o pote v2
        self.assertTrue(self.atravessa(self.pedido())[0], "o pote de base tinha de estar liberado")
        canon = self.publicacao["CANONICAL_HOST"]
        for d in [{"TIPO": "VERCEL_PREVIEW", "BRANCH": r, "HOST": "x.vercel.app"}
                  for r in self.publicacao["PROMOTION_AUTHORITY_BRANCHES"]] + [
                  {"TIPO": "VERCEL_PREVIEW", "HOST": canon},
                  {"TIPO": "BUILD_LOCAL", "HOST": canon},
                  {"TIPO": "PRODUCAO", "HOST": canon},
                  {"TIPO": "PRODUCAO"}, {"TIPO": "CLIENTE"},
                  {"PARA_CLIENTE": True}, {"TIPO": None}, {"BRANCH": ""}]:
            self.recusa(self.pedido(DESTINO=d))

    def test_PRODUCAO_PODE_RECEBER_NAO_fail_closed_com_destino_estranho(self):
        for destino in (None, {}, {"TIPO": "BUILD_LOCAL"}, "producao", []):
            p = self.pedido()
            p["DESTINO"] = destino
            # recusar por REBENTAR nao conta: a recusa tem de ser dita, com o motivo
            pode, motivo = self.atravessa(p)
            self.assertFalse(pode, "destino %r deixou passar: %s" % (destino, motivo))
            self.assertIn(lei.BLOQUEIO, motivo)
            if not isinstance(destino, dict):
                self.assertIn("destino ilegivel", motivo)

    def test_VAZAMENTO_PREVIEW_PARA_PRODUCAO_ZERO(self):
        """Todas as combinacoes de tipo x branch x host x para-cliente: nenhuma
        que toque producao pode atravessar. O numero tem de ser 0."""
        tipos = list(lei.DESTINOS_DO_PREVIEW) + ["PRODUCAO", "CLIENTE", None]
        ramos = ["claude/l3-radar-original-v1", "main", None] + self.publicacao["PROMOTION_AUTHORITY_BRANCHES"]
        hosts = [None, "localhost", "sintonia-eame-git-x.vercel.app", self.publicacao["CANONICAL_HOST"],
                 "sintonia.example.com"]
        vazamentos, preview_ok, total = [], 0, 0
        for tipo in tipos:
            for ramo in ramos:
                for host in hosts:
                    for cliente in (False, True, None):
                        d = {"TIPO": tipo, "BRANCH": ramo, "HOST": host, "PARA_CLIENTE": cliente}
                        total += 1
                        pode, _ = self.atravessa(self.pedido(DESTINO=d))
                        if pode and self._producao(d):
                            vazamentos.append(d)
                        preview_ok += bool(pode)
        self.assertEqual(len(vazamentos), 0, "VAZAMENTO_PREVIEW_PARA_PRODUCAO = %d: %s"
                         % (len(vazamentos), vazamentos[:3]))
        self.assertGreater(preview_ok, 0, "zero vazamentos porque nada passa nao prova nada")
        self.assertGreater(total, 100)


class A_AExcecaoNaoFechaAFundacao(Base):

    def test_a_a_fundacao_continua_nao_fechada_nos_tres_sitios(self):
        self.assertIsNotNone(lei.excecao_vigente(self.trava, self.diario))
        self.assertEqual(self.trava["COLLECTION_FOUNDATION_CLOSED"], "NAO")
        self.assertFalse(lei.COLLECTION_FOUNDATION_CLOSED)
        pode, motivo = lei.pode_implementar_inteligencia()
        self.assertFalse(pode, "a excecao destravou a inteligencia inteira: %s" % motivo)

    def test_a_a_regra_principal_nao_mudou(self):
        self.assertEqual(self.trava["REGRA"],
                         "COLLECTION_FOUNDATION_CLOSED != SIM  →  INTELLIGENCE_IMPLEMENTATION_BLOCKED")

    def test_a_atravessar_nao_mexe_na_fundacao(self):
        antes = lei.COLLECTION_FOUNDATION_CLOSED
        self.atravessa(self.pedido())
        self.assertEqual(lei.COLLECTION_FOUNDATION_CLOSED, antes)
        self.assertFalse(lei.pode_implementar_inteligencia()[0])

    def test_a_os_criterios_nao_sao_dados_por_cumpridos_pela_excecao(self):
        """A..N medidos pela lei; a excecao nao aparece na medicao."""
        with open(os.path.join(RAIZ, "system-map", "data", "estradas-it.generated.json"),
                  encoding="utf-8") as f:
            estado = json.load(f)
        m = lei.medir_criterios(estado)
        self.assertEqual(sorted(m), list("ABCDEFGHIJKLMN"))
        self.assertEqual(m["N"]["ESTADO"], lei.FAIL)
        self.assertNotIn("PREVIEW", json.dumps(m))

    def test_a_a_trava_diz_o_que_a_cadeia_mediu(self):
        """A..N no contrato = CRITERIOS_A_N que a cadeia escreveu pela lei. Uma
        lista escrita a mao que diverge da medicao reprova aqui."""
        with open(os.path.join(RAIZ, "system-map", "data", "estradas-it.generated.json"),
                  encoding="utf-8") as f:
            medido = json.load(f)["CRITERIOS_A_N"]
        por = {e: sorted(k for k, v in medido.items() if v["ESTADO"] == e)
               for e in (lei.PASS, lei.FAIL, lei.NAO_SEI)}
        self.assertEqual(sorted(self.trava["QUAIS_JA_CUMPRIDOS"]), por[lei.PASS])
        self.assertEqual(sorted(self.trava["QUAIS_FALHAM"]), por[lei.FAIL])
        self.assertEqual(sorted(self.trava["QUAIS_NAO_SEI"]), por[lei.NAO_SEI])
        self.assertEqual(sorted(self.trava["QUAIS_FALTAM"]), sorted(por[lei.FAIL] + por[lei.NAO_SEI]))
        self.assertEqual(self.trava["COLLECTION_FOUNDATION_CLOSED"], "NAO")

    def test_a_os_obrigatorios_do_preview_valem_hoje_e_producao_exige_os_14(self):
        """D152: o que o preview exige tem de estar PASS na medicao; a producao
        exige os catorze. Se um obrigatorio do preview cair, isto reprova."""
        e = lei.excecao_vigente(self.trava, self.diario)
        c = e["CRITERIOS_A_N_E_ESTA_EXCECAO"]
        self.assertEqual(c["SO_PARA_PRODUCAO_E_PARA_FECHAR_A_FUNDACAO"], list("ABCDEFGHIJKLMN"))
        with open(os.path.join(RAIZ, "system-map", "data", "estradas-it.generated.json"),
                  encoding="utf-8") as f:
            medido = json.load(f)["CRITERIOS_A_N"]
        for k in c["OBRIGATORIOS_PARA_O_PREVIEW"]:
            self.assertEqual(medido[k]["ESTADO"], lei.PASS,
                             "o preview exige %s e a medicao diz %s" % (k, medido[k]))
        # e nada disto conta criterio como cumprido
        self.assertEqual(self.trava["COLLECTION_FOUNDATION_CLOSED"], "NAO")
        self.assertNotIn("N", self.trava["QUAIS_JA_CUMPRIDOS"])

    def test_a_entrada_que_diz_que_fecha_a_fundacao_nao_vale(self):
        self.assertIsNone(lei.excecao_vigente(self.com_entrada(NAO_FECHA_A_FUNDACAO=False), self.diario))


class B_ProducaoEClienteContinuamFechados(Base):

    def test_b_branch_de_promocao_e_recusada(self):
        for ramo in self.publicacao["PROMOTION_AUTHORITY_BRANCHES"]:
            self.recusa(self.pedido(DESTINO={"BRANCH": ramo}))

    def test_b_o_host_canonico_e_recusado_mesmo_com_preview_no_nome(self):
        host = self.publicacao["CANONICAL_HOST"]
        self.assertIn("preview", host)   # a armadilha: o nome engana
        self.recusa(self.pedido(DESTINO={"TIPO": "VERCEL_PREVIEW", "HOST": host}))

    def test_b_destino_producao_ou_cliente_e_recusado(self):
        for tipo in ("PRODUCAO", "CLIENTE", "URL_PUBLICA", None):
            self.recusa(self.pedido(DESTINO={"TIPO": tipo}))

    def test_b_para_cliente_verdadeiro_ou_nao_dito_e_recusado(self):
        self.recusa(self.pedido(DESTINO={"PARA_CLIENTE": True}))
        self.recusa(self.pedido(DESTINO={"PARA_CLIENTE": None}))

    def test_b_o_contrato_nao_ensina_a_guarda_a_aceitar_producao(self):
        e = [x for x in self.trava["EXCECOES_CONTROLADAS"] if x["ID"] == lei.EXCECAO_PREVIEW][0]
        t = self.com_entrada(ESCOPO=dict(e["ESCOPO"], DESTINOS_TIPO=["BUILD_LOCAL", "VERCEL_PREVIEW", "PRODUCAO"]))
        self.recusa(self.pedido(DESTINO={"TIPO": "PRODUCAO"}), trava=t)

    def test_b_build_local_com_host_publico_e_recusado(self):
        self.recusa(self.pedido(DESTINO={"HOST": "sintonia.example.com"}))

    def test_b_branch_nao_dita_e_recusada(self):
        self.recusa(self.pedido(DESTINO={"BRANCH": None}))

    def test_b_numa_branch_de_producao_nenhum_artefato_e_autorizado(self):
        t = self.com_entrada(ARTEFATOS_AUTORIZADOS=[{"PATH": "x/y.js", "GIT_BLOB_SHA": "a" * 40}])
        self.assertEqual(lei.artefatos_autorizados(t, self.diario, self.publicacao, ("claude/x",)),
                         {"x/y.js": "a" * 40})
        for ramo in self.publicacao["PROMOTION_AUTHORITY_BRANCHES"]:
            self.assertEqual(lei.artefatos_autorizados(t, self.diario, self.publicacao, ("HEAD", ramo)), {})


class C_OQueNaoFoiLiberadoNaoSai(Base):

    def _com_objeto(self, muda):
        p = self.pedido()
        for e in p["POTE"]["COMPARTIMENTOS"].values():
            if e["OBJETOS"]:
                muda(e["OBJETOS"][0])
                break
        return p

    def test_c_objeto_nao_para_cliente_recusa_o_pote_inteiro(self):
        self.recusa(self._com_objeto(lambda o: o.update(LIBERACAO="NAO_PARA_CLIENTE")))

    def test_c_objeto_sem_liberacao_recusa(self):
        self.recusa(self._com_objeto(lambda o: o.pop("LIBERACAO")))

    def test_c_conferencia_falhada_recusa(self):
        self.recusa(self._com_objeto(
            lambda o: o["CONFERENCIA_DE_LIBERACAO"].update(C2_DATA_PROPRIA="FALHOU: data da publicacao")))

    def test_c_sem_decisao_do_dono_recusa(self):
        self.recusa(self._com_objeto(
            lambda o: o["CONFERENCIA_DE_LIBERACAO"].update(C8_DECISAO_DO_DONO="FALHOU: sem decisao")))

    def test_c_liberado_por_outra_corrida_recusa(self):
        self.recusa(self._com_objeto(lambda o: o.update(LIBERADO_NA_CORRIDA="IR-outra")))

    def test_c_pote_que_reprova_nos_gates_do_pote_v2_recusa(self):
        p = self.pedido()
        p["POTE"]["NAO_PARA_CLIENTE"] = False     # tirar a marca EXPERIMENTAL e reprovar a lei do pote
        self.recusa(p)

    def test_c_pote_sem_objeto_nenhum_recusa(self):
        p = self.pedido()
        for e in p["POTE"]["COMPARTIMENTOS"].values():
            e["OBJETOS"] = []
        self.recusa(p)
        # e mesmo que os gates do pote v2 o deixassem passar, a guarda recusa-o
        # por si: isolar a regra, senao ela so vive a sombra do validador
        pode, motivo = lei.pode_atravessar_a_trava(p, self.trava, self.diario, self.publicacao,
                                                   validar=lambda _pote: [])
        self.assertFalse(pode, motivo)
        self.assertIn("nada a publicar", motivo)

    def test_c_contagem_de_liberados_que_mente_recusa(self):
        p = self.pedido()
        p["POTE"]["OBJETOS_LIBERADOS"] = 99
        self.recusa(p)


class D_ASalaNaoSeEscreve(Base):

    def test_d_escrever_na_sala_e_recusado(self):
        for op in ("ESCREVER_NA_SALA", "MARCAR_CONSUMIDO_EM", None):
            self.recusa(self.pedido(OPERACAO=op))

    def test_d_consumido_em_fica_fora(self):
        self.recusa(self.pedido(CONSUMIDO_EM="2026-09-28T20:00:00Z"))
        self.recusa(self.pedido(MARCAR_CONSUMIDO_EM=True))

    def test_d_sala_real_sem_copia_read_only_e_recusada(self):
        self.recusa(self.pedido(ENTRADA={"TIPO": "SALA_REAL"}))
        self.recusa(self.pedido(ENTRADA={"READ_ONLY": False}))

    def test_d_sem_prova_reversa_do_lab_e_recusado(self):
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=None))
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB={"VEREDITO": "FAIL", "ONDE": "x"}))


class E_SemAD140VoltaABloquearTudo(Base):

    def test_e_ambito_exato_esta_escrito_e_e_lido(self):
        e = lei.excecao_vigente(self.trava, self.diario)
        self.assertEqual({k: e["AMBITO_EXATO"][k] for k in lei.AMBITO_EXATO}, lei.AMBITO_EXATO)
        for k in lei.AMBITO_EXATO:
            amb = dict(e["AMBITO_EXATO"], **{k: "SIM"})
            self.recusa(self.pedido(), trava=self.com_entrada(AMBITO_EXATO=amb))
        t = self.com_entrada()
        for x in t["EXCECOES_CONTROLADAS"]:
            x.pop("AMBITO_EXATO")
        self.recusa(self.pedido(), trava=t)

    def test_e_sem_a_d140_no_diario_recusa(self):
        diario = self.diario.replace(lei.MARCA_NO_DIARIO, "## (retirada)")
        self.assertIsNone(lei.excecao_vigente(self.trava, diario))
        self.recusa(self.pedido(), diario=diario)

    def test_e_autoridade_diferente_recusa(self):
        self.recusa(self.pedido(), trava=self.com_entrada(AUTORIDADE="D999"))

    def test_e_revogada_recusa(self):
        self.recusa(self.pedido(), trava=self.com_entrada(REVOGADA=True))

    def test_e_revogada_nao_dita_recusa(self):
        t = self.com_entrada()
        for e in t["EXCECOES_CONTROLADAS"]:
            e.pop("REVOGADA")
        self.recusa(self.pedido(), trava=t)

    def test_e_sem_a_entrada_nenhum_artefato_e_autorizado(self):
        self.assertEqual(lei.artefatos_autorizados(self.sem_excecao(), self.diario, self.publicacao), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
