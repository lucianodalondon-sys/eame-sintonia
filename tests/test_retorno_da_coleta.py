# -*- coding: utf-8 -*-
"""O CONTRATO DE RETORNO DA COLETA, com dentes.

Onze casos que a realidade desta árvore exigiu (todos com ficheiro real por
trás) e catorze ataques. A trava existe para que isto nunca mais aconteça em
silêncio:

    ITEMS_EMITTED        253
    REAL_HARVEST_ITEMS     0
    FALSE_HARVEST_TOTAL  253

Nenhum teste aqui usa nome de ficheiro, nome de pasta, extensão ou «a primeira
lista do JSON» como autoridade semântica. A espécie é DECLARADA; o payload é
MEDIDO.
"""
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "leis"))
import retorno_da_coleta as r  # noqa: E402


def envelope(**kw):
    base = dict(RUN_ID="XX-T2-2026-09-11-000001", EXECUTOR_ID="coleta/italy_executor.py",
                EXECUTOR_VERSION="abc1234", ESTADO=r.SUCCESS,
                COLHEITA=[], SUPORTE=[], ERROS=[])
    base.update(kw)
    return base


def unidade(**kw):
    base = dict(ESPECIE=r.COLHEITA, SOURCE_ID="IT-T2-002",
                DOCUMENT_ID="ARPAV_Z24_20260902152048",
                SHA256="0be2d204c98a" + "0" * 52,
                PAYLOAD={"ONDE": "", "ESTADO": r.PAYLOAD_NAO_SE_APLICA})
    base.update(kw)
    return base


class OsCasosQueARealidadeExigiu(unittest.TestCase):
    """Fase 7 — cada caso tem um ficheiro real desta árvore por trás."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def ok(self, env):
        return r.conferir(env, self.tmp)

    # A · JSON contendo directamente unidades colhidas
    def test_A_unidade_colhida_directa_passa(self):
        self.assertEqual(self.ok(envelope(COLHEITA=[unidade()])), [])

    # B · manifesto apontando para PDFs (data/raw/IT-ROTULOS/_MANIFESTO.json)
    def test_B_manifesto_e_suporte_e_nao_atravessa(self):
        env = envelope(SUPORTE=[{"ESPECIE": r.MANIFEST,
                                 "ONDE": "data/raw/IT-ROTULOS/_MANIFESTO.json"}])
        self.assertEqual(self.ok(env), [])
        self.assertEqual(r.so_o_que_entra(env), [])

    # C · catálogo de pesquisadores (RESEARCHER-CORPUS-EAME-V1.json)
    def test_C_catalogo_nunca_e_colheita(self):
        mal = self.ok(envelope(COLHEITA=[unidade(ESPECIE=r.CATALOG)]))
        self.assertTrue(any("nao e colheita" in m for m in mal), mal)

    # D · lista de contas/fontes futuras (CONTAS-V1.json)
    def test_D_lista_de_contas_e_catalogo(self):
        env = envelope(SUPORTE=[{"ESPECIE": r.CATALOG,
                                 "ONDE": "data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json"}])
        self.assertEqual(self.ok(env), [])

    # E · directório contendo documentos colhidos (collection-store)
    def test_E_payload_presente_e_medido_na_arvore(self):
        rel = os.path.join("loja", "agro_24.pdf")
        os.makedirs(os.path.join(self.tmp, "loja"))
        open(os.path.join(self.tmp, rel), "w").write("bytes")
        self.assertEqual(
            self.ok(envelope(COLHEITA=[unidade(
                PAYLOAD={"ONDE": rel, "ESTADO": r.PRESENTE})])), [])

    # F · execução válida com zero itens (CLASSIFICADO-V1.json, ITEM_COUNT=0)
    def test_F_zero_legitimo_nao_e_erro(self):
        self.assertEqual(self.ok(envelope(ESTADO=r.SUCCESS, COLHEITA=[])), [])

    # G · execução com erro
    def test_G_falha_exige_motivo_escrito(self):
        self.assertEqual(self.ok(envelope(ESTADO=r.FAILED, ERROS=["timeout na fonte"])), [])
        mal = self.ok(envelope(ESTADO=r.FAILED, ERROS=[]))
        self.assertTrue(any("sem motivo" in m or "sem nenhum erro" in m for m in mal), mal)

    # H · índice cujo payload não existe (163 linhas, 0 PDFs)
    def test_H_payload_ausente_tem_estado_proprio_e_nao_e_erro(self):
        env = envelope(COLHEITA=[unidade(
            PAYLOAD={"ONDE": "nao/existe.pdf", "ESTADO": r.AUSENTE})])
        self.assertEqual(self.ok(env), [], "AUSENTE é um estado, não uma falha")

    def test_H2_mentir_sobre_o_payload_e_apanhado(self):
        env = envelope(COLHEITA=[unidade(
            PAYLOAD={"ONDE": "nao/existe.pdf", "ESTADO": r.PRESENTE})])
        self.assertTrue(any("a arvore diz" in m for m in self.ok(env)))

    # I · uma RUN produz múltiplas observações (PILOT_RUN_...cf7519 tem 31)
    def test_I_uma_corrida_carrega_varias_unidades(self):
        env = envelope(COLHEITA=[unidade(DOCUMENT_ID="ARPAV_Z%02d" % i) for i in range(31)])
        self.assertEqual(self.ok(env), [])

    # J · uma RUN produz colheita E suporte
    def test_J_colheita_e_suporte_convivem_no_mesmo_envelope(self):
        env = envelope(COLHEITA=[unidade()],
                       SUPORTE=[{"ESPECIE": r.RUN_RECEIPT, "ONDE": "medicao.json"},
                                {"ESPECIE": r.PLAN, "ONDE": "ordem.json"}])
        self.assertEqual(self.ok(env), [])
        self.assertEqual(len(r.so_o_que_entra(env)), 1)

    # K · mesmo conteúdo em duas observações legítimas (35 sha repetidos)
    def test_K_mesmo_sha_em_duas_observacoes_e_legitimo(self):
        sha = "2e488a8232ba" + "0" * 52
        env = envelope(COLHEITA=[unidade(DOCUMENT_ID="TERRETRURIA_A", SHA256=sha),
                                 unidade(DOCUMENT_ID="TERRETRURIA_B", SHA256=sha)])
        self.assertEqual(self.ok(env), [],
                         "SHA256 NAO E IDENTIDADE DOCUMENTAL")


class OsAtaques(unittest.TestCase):
    """Fase 9 — catorze tentativas de fazer suporte passar por colheita."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def mal(self, env):
        return r.conferir(env, self.tmp)

    def test_1_manifesto_com_campo_items_continua_manifesto(self):
        """O nome do campo não é autoridade: a espécie é declarada."""
        env = envelope(SUPORTE=[{"ESPECIE": r.MANIFEST, "ONDE": "x.json",
                                 "items": [{"a": 1}] * 163}])
        self.assertEqual(self.mal(env), [])
        self.assertEqual(r.so_o_que_entra(env), [])

    def test_2_catalogo_com_campo_texto_continua_catalogo(self):
        env = envelope(COLHEITA=[unidade(ESPECIE=r.CATALOG, texto="parece prosa")])
        self.assertTrue(any("nao e colheita" in m for m in self.mal(env)))

    def test_3_ficheiro_chamado_harvest_que_e_indice(self):
        """Nome de ficheiro não promove nada."""
        env = envelope(SUPORTE=[{"ESPECIE": r.MANIFEST, "ONDE": "harvest.json"}])
        self.assertEqual(self.mal(env), [])

    def test_4_payload_sem_ficheiro_fisico(self):
        env = envelope(COLHEITA=[unidade(PAYLOAD={"ONDE": "fantasma.pdf",
                                                  "ESTADO": r.PRESENTE})])
        self.assertTrue(any("a arvore diz AUSENTE" in m for m in self.mal(env)))

    def test_5_ficheiro_fisico_sem_declaracao_nao_entra(self):
        """Bytes no disco não se auto-promovem: o que entra é o que foi declarado."""
        open(os.path.join(self.tmp, "solto.pdf"), "w").write("x")
        self.assertEqual(r.so_o_que_entra(envelope()), [])

    def test_6_dois_run_id_para_o_mesmo_objecto(self):
        env = envelope(RUN_ID="RUN-A", COLHEITA=[unidade(RUN_ID="RUN-B")])
        self.assertTrue(any("RUN_MISMATCH" in m for m in self.mal(env)))

    def test_7_mesmo_sha_nao_e_conflito(self):
        sha = "a" * 64
        env = envelope(COLHEITA=[unidade(DOCUMENT_ID="D1", SHA256=sha),
                                 unidade(DOCUMENT_ID="D2", SHA256=sha)])
        self.assertEqual(self.mal(env), [])

    def test_8_source_id_ausente_e_recusado(self):
        self.assertTrue(any("sem SOURCE_ID" in m
                            for m in self.mal(envelope(COLHEITA=[unidade(SOURCE_ID="")]))))

    def test_8b_source_id_nao_sei_nao_serve_para_colheita(self):
        self.assertTrue(any("NAO SEI" in m for m in
                            self.mal(envelope(COLHEITA=[unidade(SOURCE_ID=r.NAO_SEI)]))))

    def test_9_document_id_ausente_tem_de_ser_declarado_nao_sei(self):
        self.assertTrue(any("DOCUMENT_ID ausente" in m for m in
                            self.mal(envelope(COLHEITA=[unidade(DOCUMENT_ID="")]))))
        self.assertEqual(self.mal(envelope(COLHEITA=[unidade(DOCUMENT_ID=r.NAO_SEI)])), [],
                         "UNKNOWN PERMANECE UNKNOWN, e isso é legítimo")

    def test_10_document_id_fabricado_do_sha_e_recusado(self):
        sha = "b" * 64
        mal = self.mal(envelope(COLHEITA=[unidade(DOCUMENT_ID=sha, SHA256=sha)]))
        self.assertTrue(any("fabricado" in m for m in mal), mal)

    def test_10b_document_id_fabricado_do_endereco_e_recusado(self):
        mal = self.mal(envelope(COLHEITA=[unidade(
            DOCUMENT_ID="agro_24",
            PAYLOAD={"ONDE": "loja/agro_24.pdf", "ESTADO": r.AUSENTE})]))
        self.assertTrue(any("endereco" in m for m in mal), mal)

    def test_11_suporte_e_colheita_nao_se_misturam(self):
        env = envelope(SUPORTE=[{"ESPECIE": r.COLHEITA, "ONDE": "x"}])
        self.assertTrue(any("declarada como suporte" in m for m in self.mal(env)))

    def test_12_executor_produz_zero_legitimamente(self):
        self.assertEqual(self.mal(envelope(ESTADO=r.SUCCESS, COLHEITA=[])), [])

    def test_13_caminho_para_ficheiro_inexistente_e_estado_e_nao_crash(self):
        self.assertEqual(
            r.estado_do_payload("nao/existe/nada.pdf", self.tmp), r.AUSENTE)

    def test_14_output_kind_desconhecido_e_recusado(self):
        mal = self.mal(envelope(COLHEITA=[unidade(ESPECIE="INVENTADA")]))
        self.assertTrue(any("fora do vocabulario" in m for m in mal), mal)

    def test_14b_unidade_sem_payload_e_recusada(self):
        """Segunda trava que faltava, e outra vez foi a mutação a encontrá-la.

        Calar o `PAYLOAD` é diferente de declarar `NAO_SE_APLICA`. O primeiro
        não diz nada; o segundo afirma que a observação É o item. Sem esta
        trava, apagar a exigência inteira não matava um único teste.
        """
        u = unidade()
        del u["PAYLOAD"]
        mal = self.mal(envelope(COLHEITA=[u]))
        self.assertTrue(any("sem PAYLOAD" in m for m in mal), mal)

    def test_14c_estado_da_corrida_fora_do_vocabulario_e_recusado(self):
        """Terceira encontrada por mutação. `ESTADO` é vocabulário fechado —
        reutilizado de `regras/proveniencia.py::STATUS_RUN`, não redefinido."""
        mal = self.mal(envelope(ESTADO="OK"))
        self.assertTrue(any("ESTADO da corrida fora do vocabulario" in m for m in mal), mal)
        self.assertEqual(r.ESTADOS_DA_CORRIDA, ("SUCCESS", "PARTIAL", "FAILED"))

    def test_15_listas_ausentes_nao_passam_por_vazias(self):
        env = envelope()
        del env["COLHEITA"]
        self.assertTrue(any("tem de ser uma lista" in m for m in self.mal(env)))


class ANenhumaHeuristicaGenerica(unittest.TestCase):
    """A lei proíbe explicitamente as quatro autoridades falsas que causaram
    os 253 falsos positivos. Esta trava lê o próprio código do contrato."""

    def test_a_extensao_e_o_nome_nunca_classificam(self):
        """`basename`/`splitext` existem no contrato, mas só dentro de
        `_fabricado()` — para APANHAR um DOCUMENT_ID tirado do endereço, nunca
        para decidir espécie. Esta trava prende esse limite."""
        with open(os.path.join(RAIZ, "leis", "retorno_da_coleta.py"), encoding="utf-8") as f:
            linhas = [l for l in f if not l.strip().startswith("#")]
        corpo = "".join(linhas)
        self.assertNotIn("endswith", corpo,
                         "decidir por extensão é a heurística que esta lei proíbe")
        dentro = "".join(linhas[next(i for i, l in enumerate(linhas)
                                     if l.startswith("def _fabricado")):])
        for nome in ("basename(", "splitext("):
            self.assertEqual(corpo.count(nome), dentro.count(nome),
                             "%s só pode viver em _fabricado()" % nome)

    def test_so_a_colheita_atravessa_a_porta(self):
        """A trava que faltava, e a mutação encontrou-a.

        `conferir()` já recusava suporte dentro da lista COLHEITA — mas
        `so_o_que_entra()` é o filtro que o runtime vai usar, e ninguém o
        estava a prender. Alargar `ENTRAM_NO_INGRESSO` deixava um manifesto
        atravessar sem nenhum teste se queixar.

            UMA MUTACAO QUE NAO MATA NENHUM TESTE NAO PROVA QUE O CODIGO ESTA
            CERTO: PROVA QUE NINGUEM O ESTAVA A OLHAR.
        """
        self.assertEqual(r.ENTRAM_NO_INGRESSO, (r.COLHEITA,))
        for especie in (r.MANIFEST, r.CATALOG, r.RUN_RECEIPT, r.PLAN,
                        r.ESPECIE_DESCONHECIDA):
            env = envelope(COLHEITA=[unidade(ESPECIE=especie), unidade()])
            with self.subTest(especie=especie):
                passou = r.so_o_que_entra(env)
                self.assertEqual(len(passou), 1, "%s atravessou a porta" % especie)
                self.assertEqual(passou[0]["ESPECIE"], r.COLHEITA)

    def test_a_especie_vem_do_campo_declarado(self):
        u = {"ESPECIE": r.MANIFEST, "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "D",
             "PAYLOAD": {"ONDE": "", "ESTADO": r.PAYLOAD_NAO_SE_APLICA},
             "texto": "prosa", "title": "titulo", "items": [1, 2, 3]}
        mal = r.conferir_unidade(u, "RUN", tempfile.mkdtemp())
        self.assertTrue(any("nao e colheita" in m for m in mal),
                        "campos que cheiram a colheita não promovem um manifesto")


if __name__ == "__main__":
    unittest.main()
