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
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import fundacao_da_coleta as lei  # noqa: E402

sys.path.insert(0, os.path.join(RAIZ, "pacote"))
import pote_intelligence_casco as P  # noqa: E402

CORRIDA = os.path.join(RAIZ, "tests", "fixtures", "pote", "CORRIDA-SINTETICA-V2-UNICO.json")
LIBERADO = "LIBERADO_PARA_CLIENTE"
RAMO_REAL = "claude/l3-radar-original-v1"
#: Uma decisao SINTETICA, so no diario que estes testes usam — nunca no diario real.
DECISAO_SINTETICA = ("\n\n---\n\n## D9001 · DECISAO SINTETICA DOS TESTES DA GUARDA\n\n"
                     "- **Autor:** DONO REAL (sintetico, so em tests/test_excecao_preview_e2e.py)\n"
                     "- **Estado:** DECIDIDO\n")
C8_REGISTADO = "D9001 · liberacao sintetica dos testes"


def _pote_liberado(sha_da_copia):
    """O pote sintetico do repositorio, feito DA copia dada, com cada objeto
    liberado pelo contrato v2.2 e o C8 a citar uma decisao registada."""
    with open(CORRIDA, encoding="utf-8") as f:
        pote = P.ler_entrada(json.load(f))
    pote["CORTE"] = {"COPIA_DA_SALA_EM": "2026-09-29T00:00:00+00", "TRANSACTION_READ_ONLY": "on/on",
                     "COPIA_SHA256": sha_da_copia}
    for e in pote["COMPARTIMENTOS"].values():
        for o in e["OBJETOS"]:
            o["LIBERACAO"] = LIBERADO
            o["LIBERADO_POR"] = "INTELLIGENCE"
            o["LIBERADO_NA_CORRIDA"] = pote["INTELLIGENCE_RUN_ID"]
            o["CONFERENCIA_DE_LIBERACAO"] = dict.fromkeys(lei.CONFERENCIAS_QUE_PASSAM, "PASSOU")
            o["CONFERENCIA_DE_LIBERACAO"][lei.DECISAO_DO_DONO] = C8_REGISTADO
    return pote


class OlhosFalsos:
    """O Verificador da guarda, trocado: git e Vercel simulados, sem rede."""

    MUDOS = ("mudo.vercel.app",)

    def __init__(self, ramo=RAMO_REAL, deployments=None, por_omissao=RAMO_REAL):
        self.ramo = ramo
        self.por_omissao = por_omissao
        self.deployments = {"x.vercel.app": "release/canonical"} if deployments is None else deployments

    def ramo_real(self):
        return self.ramo

    def deployment(self, host):
        """Host desconhecido responde a branch do preview: o pior caso, um
        deployment que MENTE — a guarda tem de recusar pelo resto."""
        if host is None or host in self.MUDOS:
            return None
        src = self.deployments.get(host, self.por_omissao)
        return None if src is None else {"SOURCE_BRANCH": src, "DEPLOYED_COMMIT": "0" * 40}


class Base(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        trava, diario, cls.publicacao = lei.carregar()
        cls.diario_real = diario
        cls.diario = diario + DECISAO_SINTETICA
        cls.pasta = tempfile.mkdtemp(prefix="l1-guarda-")
        cls.pasta_lab = os.path.join(cls.pasta, "lab")
        os.makedirs(cls.pasta_lab)
        # a pasta do LAB dos testes entra SO na copia da trava que os testes usam
        cls.trava_real = trava
        cls.trava = copy.deepcopy(trava)
        for e in cls.trava["EXCECOES_CONTROLADAS"]:
            if e["ID"] == lei.EXCECAO_PREVIEW:
                e["PASTAS_DO_LAB"] = list(e.get("PASTAS_DO_LAB") or []) + [cls.pasta_lab]
        cls.copia = os.path.join(cls.pasta, "COPIA-DA-SALA.json")
        with open(cls.copia, "w", encoding="utf-8") as f:
            f.write('{"SALA": "copia sintetica, READ_ONLY"}\n')
        with open(cls.copia, "rb") as f:
            cls.sha_copia = hashlib.sha256(f.read()).hexdigest()
        cls.pote = _pote_liberado(cls.sha_copia)
        cls.n_lab = 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.pasta, ignore_errors=True)

    def escrever(self, nome, texto):
        caminho = os.path.join(self.pasta, nome)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        return caminho

    def pedido(self, **muda):
        p = {
            "OPERACAO": lei.PUBLICAR_NO_PREVIEW,
            "DESTINO": {"TIPO": "BUILD_LOCAL", "BRANCH": RAMO_REAL,
                        "HOST": None, "PARA_CLIENTE": False},
            "ENTRADA": {"TIPO": lei.ENTRADA_READ_ONLY, "READ_ONLY": True,
                        "SNAPSHOT": {"FICHEIRO": self.copia, "SHA256": self.sha_copia}},
            "POTE": copy.deepcopy(self.pote),
            "_LAB_DESTE_POTE": "PROVA_REVERSA_DO_LAB" not in muda,
        }
        for k, v in muda.items():
            if isinstance(v, dict) and isinstance(p.get(k), dict):
                p[k].update(v)
            else:
                p[k] = v
        return p

    def _pasta_nova(self):
        """Cada prova numa subpasta propria da pasta do LAB: as versoes de um par so
        se encontram quando o teste as poe juntas de proposito."""
        type(self).n_lab += 1
        pasta = os.path.join(self.pasta_lab, "p%d" % self.n_lab)
        os.makedirs(pasta)
        return pasta

    def _gravar(self, texto, pasta, nome):
        caminho = os.path.join(pasta, nome)
        self.assertFalse(os.path.exists(caminho), "o LAB nunca sobrescreve uma prova")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        with open(caminho, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        return {"VEREDITO": "PASS", "ONDE": caminho, "SHA256": sha}

    def nome_deste_par(self, pote=None, versao=1):
        pote = self.pote if pote is None else pote
        return lei.nome_da_prova_do_lab(lei.sha256_do_pote(pote), pote["INTELLIGENCE_RUN_ID"], versao)

    def lab_de_texto(self, texto, pasta=None, nome=None):
        """Um ficheiro na pasta do LAB, com o nome da prova deste par, e este texto."""
        return self._gravar(texto, pasta or self._pasta_nova(), nome or self.nome_deste_par())

    def entrada(self, pote, veredito="PASS", run=None, **extra):
        """Uma prova no FORMATO REAL do LAB (29/09) para este pote e esta corrida."""
        e = {"LAB_ORIGIN": lei.LAB_ORIGIN, "DATA_UTC": "2026-09-29T10:00:00Z",
             "POTE_SHA256": lei.sha256_do_pote(pote),
             "RUN_ID": pote.get("INTELLIGENCE_RUN_ID") if run is None else run,
             "ENVELOPE_HASH": lei.ENVELOPE_INEXISTENTE, "VEREDITO": veredito,
             "VEREDITO_DETALHE": "sintetico dos testes da guarda",
             "ELOS": {"E%d" % k: "PASSOU" for k in range(1, 8)},
             "OBJETOS_PROVADOS": [], "SCRIPT": "tests/test_excecao_preview_e2e.py",
             "SCRIPT_SHA256": "0" * 64, "BRUTO": []}
        e.update(extra)
        return e

    def lab_json(self, obj, pasta=None, nome=None, versao=1):
        """Grava a prova com o nome real do par que ELA diz (ou o nome dado)."""
        if nome is None:
            if isinstance(obj, dict) and isinstance(obj.get("POTE_SHA256"), str) and obj.get("RUN_ID"):
                nome = lei.nome_da_prova_do_lab(obj["POTE_SHA256"], obj["RUN_ID"], versao)
            else:
                nome = self.nome_deste_par(versao=versao)
        return self._gravar(json.dumps(obj, ensure_ascii=False, indent=1), pasta or self._pasta_nova(), nome)

    def lab_para(self, pote, veredito="PASS", run=None, pasta=None):
        """A prova real do LAB para este pote e esta corrida, numa subpasta nova."""
        return self.lab_json(self.entrada(pote, veredito, run), pasta)

    def atravessa(self, pedido, trava=None, diario=None, olhos=None):
        if pedido.pop("_LAB_DESTE_POTE", False) and isinstance(pedido.get("POTE"), dict):
            pedido["PROVA_REVERSA_DO_LAB"] = self.lab_para(pedido["POTE"])
        return lei.pode_atravessar_a_trava(
            pedido, self.trava if trava is None else trava,
            self.diario if diario is None else diario, self.publicacao,
            verificar=OlhosFalsos() if olhos is None else olhos)

    def recusa(self, pedido, trava=None, diario=None, olhos=None):
        pode, motivo = self.atravessa(pedido, trava, diario, olhos)
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
        # e mesmo com um host de deployment que responde a branch do preview
        self.recusa(self.pedido(DESTINO={"TIPO": "PRODUCAO", "HOST": "sintonia-eame-git-x.vercel.app"}), trava=t)

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
                                                   validar=lambda _pote: [], verificar=OlhosFalsos())
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


class R_RedTeamDoBotLuciano(Base):
    """RED TEAM (29/09, sobre 7f3dc857c): a guarda aceitava TEXTO onde devia
    exigir PROVA. Cada contraprova dele e aqui um teste que tem de ser RECUSADO."""

    def _com_c8(self, c8):
        p = self.pedido()
        for e in p["POTE"]["COMPARTIMENTOS"].values():
            for o in e["OBJETOS"]:
                o["CONFERENCIA_DE_LIBERACAO"][lei.DECISAO_DO_DONO] = c8
        return p

    # ── 1 · LAB forjado ─────────────────────────────────────────────────────
    def test_redteam_lab_forjado_ficheiro_inexistente(self):
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB={
            "VEREDITO": "PASS", "ONDE": "provas/INEXISTENTE-RED-TEAM.md"}))
        self.assertIn("nao existe", m)

    def test_redteam_lab_que_existe_mas_nao_cita_este_pote(self):
        outro = copy.deepcopy(self.pote)
        outro["INTELLIGENCE_RUN_ID"] = "IR-outra-corrida"
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            self.entrada(outro), nome=self.nome_deste_par())))
        self.assertIn("par (POTE_SHA256, RUN_ID)", m)

    def test_redteam_lab_que_diz_fail_ou_nao_e_um_objeto(self):
        run = self.pote["INTELLIGENCE_RUN_ID"]
        sha = lei.sha256_do_pote(self.pote)
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_para(self.pote, veredito="FAIL")))
        self.assertIn("VEREDITO", m)
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            [self.entrada(self.pote), self.entrada(self.pote, veredito="FAIL")])))
        self.assertIn("UM objeto", m)
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_de_texto(
            "VEREDITO=PASS\nPOTE_SHA256=%s\nRUN_ID=%s\nLAB_ORIGIN=sintonia-lab\n" % (sha, run))))
        self.assertIn("nao e estruturada", m)
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_para(self.pote, veredito="PASSOU")))
        self.assertIn("so PASS ou FAIL", m)

    def test_lab_com_o_sha_do_ficheiro_em_vez_do_canonico_recusa(self):
        """O LAB declara o sha CANONICO (sort_keys, compacto). O sha dos bytes de um
        ficheiro do pote nao e esse, e ja nao se aceita como alternativa."""
        f = self.escrever("POTE.json", json.dumps(self.pote, ensure_ascii=False, indent=1))
        with open(f, "rb") as h:
            sha_do_ficheiro = hashlib.sha256(h.read()).hexdigest()
        self.assertNotEqual(sha_do_ficheiro, lei.sha256_do_pote(self.pote))
        self.recusa(self.pedido(POTE_FICHEIRO=f, PROVA_REVERSA_DO_LAB=self.lab_json(
            self.entrada(self.pote, POTE_SHA256=sha_do_ficheiro), nome=self.nome_deste_par())))
        pode, motivo = self.atravessa(self.pedido(POTE_FICHEIRO=f, PROVA_REVERSA_DO_LAB=self.lab_para(self.pote)))
        self.assertTrue(pode, motivo)

    # ── 2 · C8 texto livre ──────────────────────────────────────────────────
    def test_redteam_c8_texto_livre(self):
        m = self.recusa(self._com_c8("QUALQUER-TEXTO-SEM-AUTORIZACAO"))
        self.assertIn("texto livre", m)

    def test_c8_com_decisao_que_nao_esta_no_diario(self):
        self.recusa(self._com_c8("D9999 · inventada"))
        # a D9001 so existe no diario dos testes: no diario real, o mesmo C8 recusa
        self.recusa(self.pedido(), diario=self.diario_real)

    def test_c8_que_cita_a_decisao_no_meio_do_texto_nao_casa(self):
        self.recusa(self._com_c8("nao e a D9001, e so uma frase"))

    def test_c8_com_decisao_revogada_ou_que_nao_e_do_dono(self):
        self.recusa(self.pedido(), diario=self.diario_real + DECISAO_SINTETICA.replace("DECIDIDO", "REVOGADA"))
        self.recusa(self.pedido(), diario=self.diario + "\n- REVOGA D9001 (sintetico)\n")
        alheia = DECISAO_SINTETICA.replace("DONO REAL", "COORDENADOR")
        self.recusa(self.pedido(), diario=self.diario_real + alheia)

    # ── 3 · READ_ONLY declarado sem prova ───────────────────────────────────
    def test_redteam_read_only_declarado_sem_prova(self):
        m = self.recusa(self.pedido(ENTRADA={"TIPO": lei.ENTRADA_READ_ONLY, "READ_ONLY": True,
                                             "SNAPSHOT": None}))
        self.assertIn("READ_ONLY sem prova", m)
        p = self.pedido()
        p["ENTRADA"] = {"TIPO": lei.ENTRADA_READ_ONLY, "READ_ONLY": True}
        self.recusa(p)

    def test_copia_que_nao_existe_ou_cujo_sha_nao_bate(self):
        self.recusa(self.pedido(ENTRADA={"SNAPSHOT": {"FICHEIRO": os.path.join(self.pasta, "nao-ha.json"),
                                                      "SHA256": self.sha_copia}}))
        self.recusa(self.pedido(ENTRADA={"SNAPSHOT": {"FICHEIRO": self.copia, "SHA256": "0" * 64}}))

    def test_copia_verdadeira_mas_o_pote_nao_foi_feito_dela(self):
        outra = self.escrever("OUTRA-COPIA.json", '{"SALA": "outra"}\n')
        with open(outra, "rb") as h:
            sha = hashlib.sha256(h.read()).hexdigest()
        m = self.recusa(self.pedido(ENTRADA={"SNAPSHOT": {"FICHEIRO": outra, "SHA256": sha}}))
        self.assertIn("CORTE", m)

    def test_entrada_que_aponta_a_sala_viva_e_recusada(self):
        for campo, valor in (("DSN", "postgresql://u@127.0.0.1:54330/sala_italia"),
                             ("MORADA", "127.0.0.1:54330/sala_italia"),
                             ("HOST", "db.xyz.supabase.co")):
            self.recusa(self.pedido(ENTRADA={campo: valor}))

    def test_corte_do_pote_que_diz_que_nao_era_read_only(self):
        p = self.pedido()
        p["POTE"]["CORTE"]["TRANSACTION_READ_ONLY"] = "off"
        self.recusa(p)


class V_OQueSeMedeNaoSeAlega(Base):
    """ADENDO DO RED TEAM: BRANCH e HOST medem-se em runtime; PARA_CLIENTE e o
    conteudo do LAB nao se medem, e saem como ALEGADO — nunca como prova."""

    def test_branch_declarada_diferente_da_real_recusa(self):
        m = self.recusa(self.pedido(), olhos=OlhosFalsos(ramo="claude/outra-coisa"))
        self.assertIn("branch real", m)

    def test_branch_real_que_nao_se_mede_recusa(self):
        m = self.recusa(self.pedido(), olhos=OlhosFalsos(ramo=None))
        self.assertIn("ALEGADA", m)

    def test_arvore_real_em_producao_recusa(self):
        """Declarada e medida IGUAIS, e as duas de producao: nao ha desencontro que
        salve — so a recusa da branch de producao."""
        for ramo in ("release/canonical", "refs/heads/release/canonical", "RELEASE/CANONICAL"):
            self.recusa(self.pedido(DESTINO={"BRANCH": ramo}), olhos=OlhosFalsos(ramo=ramo))

    def test_host_que_nao_responde_recusa(self):
        m = self.recusa(self.pedido(DESTINO={"TIPO": "VERCEL_PREVIEW", "HOST": "mudo.vercel.app"}))
        self.assertIn("nao respondeu", m)

    def test_host_cujo_deployment_e_de_producao_ou_de_outra_branch_recusa(self):
        self.recusa(self.pedido(DESTINO={"TIPO": "VERCEL_PREVIEW", "HOST": "x.vercel.app"}))
        olhos = OlhosFalsos(deployments={"y.vercel.app": "claude/outra"}, por_omissao=None)
        self.recusa(self.pedido(DESTINO={"TIPO": "VERCEL_PREVIEW", "HOST": "y.vercel.app"}), olhos=olhos)

    def test_o_motivo_separa_verificado_de_alegado(self):
        pode, motivo = self.atravessa(self.pedido())
        self.assertTrue(pode, motivo)
        verificado, alegado = motivo.split("VERIFICADO: ")[1].split(" · ALEGADO (nao conta como prova): ")
        self.assertIn("BRANCH=" + RAMO_REAL, verificado)
        self.assertIn("COPIA DA SALA", verificado)
        self.assertIn("LAB:", verificado)
        self.assertIn("PARA_CLIENTE", alegado)
        self.assertNotIn("PARA_CLIENTE", verificado)

    def test_os_olhos_verdadeiros_medem_a_branch_desta_arvore(self):
        import subprocess
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=RAIZ,
                           capture_output=True, text=True)
        ambiente = [os.environ[k] for k in lei.Verificador.ENV_DO_RAMO if os.environ.get(k)]
        esperado = ambiente[0] if ambiente else (r.stdout.strip() if r.stdout.strip() != "HEAD" else None)
        self.assertEqual(lei.Verificador().ramo_real(), esperado)

    def test_a_politica_do_c8_por_objeto_esta_declarada_como_bloqueio(self):
        e = lei.excecao_vigente(self.trava, self.diario)
        b = e["BLOQUEIO_DE_POLITICA_C8"]
        self.assertEqual(b["ESTADO"], "BLOQUEIO_DE_POLITICA")
        self.assertIn("decisao do dono", b["O_QUE_FALTA"].lower())


class L_OsDezasseisPedidosHostisDoAuditor(Base):
    """AUDITOR (VERIF-L1-7f3dc857c.md, criterio 3): 13 de 16 pedidos hostis
    atravessavam. Um teste por caso, com o mesmo harness — todos tem de RECUSAR."""

    def vercel(self, branch=None, host="sintonia-eame-git-l1-x.vercel.app"):
        d = {"TIPO": "VERCEL_PREVIEW", "HOST": host}
        if branch is not None:
            d["BRANCH"] = branch
        return self.pedido(DESTINO=d)

    def test_CTRL_os_legitimos_continuam_a_passar(self):
        for p in (self.pedido(), self.vercel()):
            pode, motivo = self.atravessa(p)
            self.assertTrue(pode, motivo)

    def test_L01_host_canonico_com_https(self):
        self.recusa(self.vercel(host="https://" + self.publicacao["CANONICAL_HOST"]))

    def test_L02_host_canonico_com_espaco(self):
        self.recusa(self.vercel(host=" " + self.publicacao["CANONICAL_HOST"]))
        self.recusa(self.vercel(host=self.publicacao["CANONICAL_HOST"].upper()))

    def test_L03_host_nao_vercel_com_sufixo_no_caminho(self):
        for h in ("evil.com/.vercel.app", "evil.com?.vercel.app", "evil.com#.vercel.app",
                  "user@evil.com/.vercel.app", "vercel.app", "x.vercel.app:443"):
            self.recusa(self.vercel(host=h))
        # e um host de preview LEGITIMO escrito com esquema, caminho ou porta: so o
        # nome limpo conta — a regra tem de morder sozinha, sem outra que a cubra
        for h in ("https://sintonia-eame-git-l1-x.vercel.app", "sintonia-eame-git-l1-x.vercel.app/caminho",
                  "sintonia-eame-git-l1-x.vercel.app:8443", "u@sintonia-eame-git-l1-x.vercel.app"):
            m = self.recusa(self.vercel(host=h))
            self.assertIn("nome de host limpo", m)

    def test_L04_L05_L06_branch_de_producao_por_grafia(self):
        prod = self.publicacao["PROMOTION_AUTHORITY_BRANCHES"][0]
        for b in ("refs/heads/" + prod, "origin/" + prod, prod.upper(), " " + prod + " ",
                  "refs/remotes/origin/" + prod):
            self.recusa(self.vercel(branch=b))
            self.recusa(self.pedido(DESTINO={"BRANCH": b}), olhos=OlhosFalsos(ramo=b))

    def test_L07_branch_main_que_o_deployment_nao_confirma(self):
        self.recusa(self.vercel(branch="main"))

    def test_L08_consumido_em_dentro_do_pote(self):
        p = self.pedido()
        p["POTE"]["CONSUMIDO_EM"] = "2026-09-29"
        self.recusa(p)
        p = self.pedido()
        list(p["POTE"]["COMPARTIMENTOS"].values())[0]["consumido_em"] = "x"
        self.recusa(p)

    def test_L09_chave_desconhecida_no_pedido_e_recusada(self):
        for onde in (None, "DESTINO", "ENTRADA", "PROVA_REVERSA_DO_LAB"):
            p = self.pedido()
            alvo = p if onde is None else p[onde] if onde != "PROVA_REVERSA_DO_LAB" else None
            if onde == "PROVA_REVERSA_DO_LAB":
                p.pop("_LAB_DESTE_POTE")
                p["PROVA_REVERSA_DO_LAB"] = dict(self.lab_para(p["POTE"]), ESCREVER=True)
            else:
                alvo["ESCREVER_NA_SALA"] = True
            m = self.recusa(p)
            self.assertIn("desconhecid", m)

    def test_L10_c8_falhou_em_qualquer_caixa_e_em_qualquer_sitio(self):
        for c8 in ("falhou", "FaLhOu: sem decisao", "D9001 · falhou: sem decisao"):
            p = self.pedido()
            for e in p["POTE"]["COMPARTIMENTOS"].values():
                for o in e["OBJETOS"]:
                    o["CONFERENCIA_DE_LIBERACAO"][lei.DECISAO_DO_DONO] = c8
            self.recusa(p)

    def test_L11_d140_marcada_revogada_no_diario(self):
        for d in (self.diario.replace(lei.MARCA_NO_DIARIO, "REVOGADA — " + lei.MARCA_NO_DIARIO),
                  self.diario + "\n- REVOGA D140 (sintetico)\n",
                  self.diario + "\nD140 foi REVOGADA (sintetico)\n"):
            self.assertIsNone(lei.excecao_vigente(self.trava, d))
            self.recusa(self.pedido(), diario=d)

    def test_L11_d140_so_conta_como_cabecalho_numa_linha_propria(self):
        citada = self.diario.replace("\n" + lei.MARCA_NO_DIARIO, "\n> citada: " + lei.MARCA_NO_DIARIO)
        self.assertNotIn("\n" + lei.MARCA_NO_DIARIO, citada)
        self.assertIsNone(lei.excecao_vigente(self.trava, citada))
        self.recusa(self.pedido(), diario=citada)

    def test_L11_a_frase_revogavel_da_propria_d140_nao_a_revoga(self):
        self.assertIsNotNone(lei.excecao_vigente(self.trava, self.diario_real))

    def test_L12_L13_L14_artefatos_em_branch_de_producao_por_grafia(self):
        prod = self.publicacao["PROMOTION_AUTHORITY_BRANCHES"][0]
        t = self.com_entrada(ARTEFATOS_AUTORIZADOS=[{"PATH": "x/y.json", "GIT_BLOB_SHA": "a" * 40}])
        for ramo in (prod, "refs/heads/" + prod, "origin/" + prod, prod.upper()):
            self.assertEqual(lei.artefatos_autorizados(t, self.diario, self.publicacao, (ramo,)), {}, ramo)


class P_AProvaDoLabEDoLabEDestaCorrida(Base):
    """ADENDO DO RED TEAM (LAB): ligada ao pote E a corrida, de outro autor."""

    def test_lab_de_outra_corrida_recusa(self):
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            self.entrada(self.pote, run="IR-outra-corrida"), nome=self.nome_deste_par())))
        self.assertIn("corrida", m)

    def test_lab_com_a_corrida_so_como_pedaco_de_outra_recusa(self):
        run = self.pote["INTELLIGENCE_RUN_ID"]
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            self.entrada(self.pote, run=run + "-x"), nome=self.nome_deste_par())))

    def test_lab_fora_das_pastas_do_lab_recusa(self):
        fora = os.path.join(self.pasta, "fora-do-lab-%d" % self.n_lab)
        os.makedirs(fora)
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_para(self.pote, pasta=fora)))
        self.assertIn("pasta do LAB", m)

    def test_lab_na_pasta_do_proprio_pote_recusa(self):
        f = os.path.join(self.pasta_lab, "POTE-no-lab.json")
        with open(f, "w", encoding="utf-8") as h:
            json.dump(self.pote, h)
        m = self.recusa(self.pedido(POTE_FICHEIRO=f, PROVA_REVERSA_DO_LAB=self.lab_para(self.pote)))
        self.assertIn("produtor", m)

    def test_lab_com_sha_fixado_errado_ou_sem_sha_recusa(self):
        lab = self.lab_para(self.pote)
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=dict(lab, SHA256="0" * 64)))
        sem = dict(lab)
        sem.pop("SHA256")
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=sem))

    def test_lab_adulterado_depois_de_fixado_recusa(self):
        lab = self.lab_para(self.pote)
        with open(lab["ONDE"], "a", encoding="utf-8") as h:
            h.write("linha acrescentada depois\n")
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=lab))

    def test_na_trava_real_as_pastas_do_lab_nao_incluem_a_pasta_dos_testes(self):
        e = lei.excecao_vigente(self.trava_real, self.diario_real)
        self.assertNotIn(self.pasta_lab, e.get("PASTAS_DO_LAB") or [])
        self.recusa(self.pedido(), trava=self.trava_real)

    def test_copia_da_sala_adulterada_com_o_sha_original_recusa(self):
        adulterada = self.escrever("COPIA-ADULTERADA.json", '{"SALA": "mexida"}\n')
        m = self.recusa(self.pedido(ENTRADA={"SNAPSHOT": {"FICHEIRO": adulterada, "SHA256": self.sha_copia}}))
        self.assertIn("nao bate", m)


class LB_AProvaDoLabEstruturadaPorIgualdadeDeCampo(Base):
    """AUDITOR (VERIF-L1-cb8f20bcf) + decisao do coordenador + FORMATO REAL DO LAB:
    LB1–LB6. Um objeto JSON por prova, comparado por IGUALDADE DE CAMPO."""

    OUTRO_SHA = "f" * 64
    OUTRA_RUN = "IR-OUTRA-RODADA-0001"

    def setUp(self):
        self.sha = lei.sha256_do_pote(self.pote)
        self.run = self.pote["INTELLIGENCE_RUN_ID"]

    def outra(self, **extra):
        e = self.entrada(self.pote, POTE_SHA256=self.OUTRO_SHA, RUN_ID=self.OUTRA_RUN)
        e.update(extra)
        return e

    def test_CTRL_prova_real_deste_pote_passa(self):
        pode, motivo = self.atravessa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_para(self.pote)))
        self.assertTrue(pode, motivo)

    def test_LB1_prova_de_outro_pote_que_so_menciona_este(self):
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(self.outra(
            VEREDITO_DETALHE="comparado com o pote %s da rodada %s, NAO verificado" % (self.sha, self.run)),
            nome=self.nome_deste_par())))
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_de_texto(
            "VEREDITO=PASS\nPOTE_SHA256=%s\nRUN=%s\nNota: %s %s\n"
            % (self.OUTRO_SHA, self.OUTRA_RUN, self.sha, self.run))))

    def test_LB2_indice_com_varios_potes_nao_e_uma_prova(self):
        for indice in ({"VEREDITO": "PASS", "LAB_ORIGIN": lei.LAB_ORIGIN,
                        "ENTRADAS": [self.outra(), self.entrada(self.pote)]},
                       [self.outra(), self.entrada(self.pote)]):
            self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(indice, nome=self.nome_deste_par())))

    def test_LB3_este_pote_citado_como_rejeitado(self):
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            self.entrada(self.pote, POTE_REJEITADO=self.sha))))
        self.assertIn("POTE_REJEITADO", m)
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            self.outra(POTE_REJEITADO=[self.OUTRO_SHA, self.sha]), nome=self.nome_deste_par())))

    def test_LB4_corrida_com_sufixo(self):
        for run in (self.run + ".anterior", self.run + "-x", " " + self.run, self.run + " "):
            self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
                self.entrada(self.pote, run=run), nome=self.nome_deste_par())))

    def test_LB4_sha_do_pote_com_caixa_ou_pedaco_diferente_recusa(self):
        for sha in ("x" + self.sha, self.sha.upper(), self.sha + " ", self.sha[:63]):
            m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
                self.entrada(self.pote, POTE_SHA256=sha), nome=self.nome_deste_par())))
            # recusada pela regra CERTA — a igualdade do campo —, nao so pela das versoes
            self.assertIn("par (POTE_SHA256, RUN_ID)", m)

    def test_LB5_pote_do_produtor_em_subpasta_da_pasta_do_lab(self):
        sub = os.path.join(self.pasta_lab, "produtor", "fundo")
        os.makedirs(sub, exist_ok=True)
        pf = os.path.join(sub, "POTE.json")
        with open(pf, "w", encoding="utf-8") as h:
            json.dump(self.pote, h)
        m = self.recusa(self.pedido(POTE_FICHEIRO=pf, PROVA_REVERSA_DO_LAB=self.lab_para(self.pote)))
        self.assertIn("dentro da pasta do LAB", m)

    def test_LB6_lab_origin_e_dado_e_tem_de_ser_sintonia_lab(self):
        self.assertEqual(lei.LAB_ORIGIN, "sintonia-lab")
        for origem in (None, "", "intelligence", "INTELLIGENCE", "Sintonia-Lab", "sintonia-lab "):
            e = self.entrada(self.pote, LAB_ORIGIN=origem)
            if origem is None:
                e.pop("LAB_ORIGIN")
            self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(e)))

    def test_LB6_o_lab_nao_pode_ser_o_produtor_do_pote(self):
        p = self.pedido()
        p["POTE"]["PRODUTOR"] = lei.LAB_ORIGIN
        m = self.recusa(p)
        self.assertIn("produtor", m)

    def test_pastas_do_lab_na_trava_real_sao_so_a_pasta_exclusiva(self):
        e = lei.excecao_vigente(self.trava_real, self.diario_real)
        self.assertEqual(e["PASTAS_DO_LAB"], ["C:/Users/London1/sintonia-lab-provas/"])


class VER_AsVersoesDoMesmoParDecidemSePelaData(Base):
    """PRECISAO DO LAB: vale a prova MAIS RECENTE do par pelo DATA_UTC DE DENTRO do
    JSON — nunca pela ordem do nome. Empate = FAIL. Data ausente/invalida = FAIL."""

    def versao(self, pasta, n, data, veredito="PASS", **extra):
        return self.lab_json(self.entrada(self.pote, veredito, DATA_UTC=data, **extra), pasta=pasta, versao=n)

    def test_a_um_FAIL_mais_novo_em_menos_2_derruba_o_PASS_antigo_sem_sufixo(self):
        pasta = self._pasta_nova()
        antigo = self.versao(pasta, 1, "2026-09-29T08:00:00Z", "PASS")
        novo = self.versao(pasta, 2, "2026-09-29T09:00:00Z", "FAIL")
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=antigo))
        self.assertIn("mais recente", m)
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=novo))
        self.assertIn("VEREDITO", m)

    def test_a_um_PASS_mais_novo_em_menos_2_vale_sobre_o_FAIL_antigo(self):
        pasta = self._pasta_nova()
        self.versao(pasta, 1, "2026-09-29T08:00:00Z", "FAIL")
        novo = self.versao(pasta, 2, "2026-09-29T09:00:00Z", "PASS")
        pode, motivo = self.atravessa(self.pedido(PROVA_REVERSA_DO_LAB=novo))
        self.assertTrue(pode, motivo)

    def test_b_menos_10_contra_menos_2_decide_se_pela_data_e_nao_pelo_nome(self):
        # no alfabeto, '-10' vem ANTES de '-2'; so a data decide
        pasta = self._pasta_nova()
        dez = self.versao(pasta, 10, "2026-09-29T11:00:00Z", "PASS")
        self.versao(pasta, 2, "2026-09-29T10:00:00Z", "FAIL")
        pode, motivo = self.atravessa(self.pedido(PROVA_REVERSA_DO_LAB=dez))
        self.assertTrue(pode, motivo)
        pasta = self._pasta_nova()
        dez = self.versao(pasta, 10, "2026-09-29T10:00:00Z", "PASS")
        self.versao(pasta, 2, "2026-09-29T11:00:00Z", "FAIL")
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=dez))

    def test_b_fusos_diferentes_comparam_se_no_mesmo_instante(self):
        pasta = self._pasta_nova()
        self.versao(pasta, 1, "2026-09-29T09:30:00+00:00", "FAIL")
        novo = self.versao(pasta, 2, "2026-09-29T07:00:00-03:00", "PASS")   # 10:00 UTC
        pode, motivo = self.atravessa(self.pedido(PROVA_REVERSA_DO_LAB=novo))
        self.assertTrue(pode, motivo)

    def test_c_empate_de_data_e_FAIL(self):
        pasta = self._pasta_nova()
        um = self.versao(pasta, 1, "2026-09-29T10:00:00Z", "PASS")
        self.versao(pasta, 2, "2026-09-29T10:00:00+00:00", "PASS")
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=um))
        self.assertIn("empate", m)

    def test_data_ausente_ou_invalida_e_FAIL(self):
        for data in (None, "", "ontem", "2026-13-40T99:00:00Z", 1727600000):
            e = self.entrada(self.pote, DATA_UTC=data)
            if data is None:
                e.pop("DATA_UTC")
            self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(e)))
        # e uma versao irma com data invalida tambem derruba a prova boa
        pasta = self._pasta_nova()
        boa = self.versao(pasta, 1, "2026-09-29T10:00:00Z", "PASS")
        self.versao(pasta, 2, "sem-data", "PASS")
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=boa))

    def test_versao_irma_com_o_nome_deste_par_e_conteudo_de_outro_e_FAIL(self):
        pasta = self._pasta_nova()
        boa = self.versao(pasta, 1, "2026-09-29T10:00:00Z", "PASS")
        self.lab_json(self.entrada(self.pote, POTE_SHA256="f" * 64, DATA_UTC="2026-09-29T09:00:00Z"),
                      pasta=pasta, nome=self.nome_deste_par(versao=2))
        self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=boa))

    def test_o_nome_da_prova_tem_de_ser_o_do_formato_real(self):
        for nome in ("LAB-1.json", "PROVA-REVERSA_pote-x_run-y.json", self.nome_deste_par()[:-5] + "-1.json",
                     self.nome_deste_par()[:-5] + "-02.json", self.nome_deste_par()[:-5] + ".JSON"):
            m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(self.entrada(self.pote), nome=nome)))
            self.assertIn("nome da prova", m)

    def test_run_id_que_acaba_em_numero_nao_se_confunde_com_versao(self):
        # o RUN_ID sintetico acaba em '-0001': o nome '...-0001.json' e a versao 1
        self.assertRegex(self.pote["INTELLIGENCE_RUN_ID"], r"-\d+$")
        self.assertEqual(lei._versao_do_nome(self.nome_deste_par(), lei.sha256_do_pote(self.pote),
                                             self.pote["INTELLIGENCE_RUN_ID"]), 1)
        pode, motivo = self.atravessa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_para(self.pote)))
        self.assertTrue(pode, motivo)

    def test_envelope_do_pote_tem_de_bater(self):
        p = self.pedido()
        p["POTE"]["ENVELOPE_HASH"] = "e" * 64
        p.pop("_LAB_DESTE_POTE")
        p["PROVA_REVERSA_DO_LAB"] = self.lab_json(self.entrada(p["POTE"], ENVELOPE_HASH="e" * 64))
        pode, motivo = self.atravessa(p)
        self.assertTrue(pode, motivo)
        for env in (lei.ENVELOPE_INEXISTENTE, "d" * 64, None):
            q = self.pedido()
            q["POTE"]["ENVELOPE_HASH"] = "e" * 64
            q.pop("_LAB_DESTE_POTE")
            q["PROVA_REVERSA_DO_LAB"] = self.lab_json(self.entrada(q["POTE"], ENVELOPE_HASH=env))
            m = self.recusa(q)
            self.assertIn("ENVELOPE_HASH", m)
        # pote sem envelope: a prova tem de dizer que nao existe
        m = self.recusa(self.pedido(PROVA_REVERSA_DO_LAB=self.lab_json(
            self.entrada(self.pote, ENVELOPE_HASH="e" * 64))))
        self.assertIn("ENVELOPE_HASH", m)


class LIMITE_AGuardaNaoAfirmaMaisDoQueProva(Base):
    """ADENDO (ponto do auditor, aceite): todos os agentes correm como o mesmo
    utilizador Windows. A autoria do LAB e DECLARADA, nao provada. A guarda tem de
    o dizer — e nunca dizer mais."""

    def test_o_resultado_diz_autoria_provada_false(self):
        pode, motivo = self.atravessa(self.pedido())
        self.assertTrue(pode, motivo)
        self.assertTrue(motivo.endswith("AUTORIA_PROVADA=false"), motivo[-80:])
        self.assertNotIn("AUTORIA_PROVADA=true", motivo)
        alegado = motivo.split("ALEGADO (nao conta como prova): ")[1]
        self.assertIn("AUTORIA_DO_LAB=DECLARADA", alegado)
        verificado = motivo.split("VERIFICADO: ")[1].split(" · ALEGADO")[0]
        self.assertNotIn("AUTOR", verificado.upper().replace("AUTORIA_PROVADA", ""))

    def test_o_limite_esta_na_lei_e_na_trava_com_os_mesmos_valores(self):
        self.assertEqual(lei.LIMITE_CONHECIDO["AUTORIA_DO_LAB"], "DECLARADA")
        self.assertIs(lei.LIMITE_CONHECIDO["AUTORIA_PROVADA"], False)
        e = lei.excecao_vigente(self.trava_real, self.diario_real)
        self.assertEqual(e["LIMITE_CONHECIDO"]["AUTORIA_DO_LAB"], "DECLARADA")
        self.assertIs(e["LIMITE_CONHECIDO"]["AUTORIA_PROVADA"], False)
        self.assertIn("(POTE_SHA256, RUN_ID)", e["LIMITE_CONHECIDO"]["O_QUE_A_GUARDA_PROVA"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
