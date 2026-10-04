#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS DOZE PROVAS DA ESPINHA — P1 a P12 do enunciado C-INT-SPINE-01.

    python3 -m unittest tests.test_espinha_da_intelligence -v
    python3 -m unittest discover -s tests -v

Cada teste é nomeado pela prova que o enunciado pede, e cada um tenta a coisa
errada primeiro. Um teste que só demonstra o caminho feliz não prova uma lei:
prova um exemplo.

    O QUE ESTAS PROVAS **NÃO** PROVAM
    ---------------------------------
    Que a Intelligence funciona em produção. Elas provam que a MÁQUINA DE
    ESTADOS recusa o que tem de recusar. `IMPLEMENTED` continua `NO`.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "provas"))

from espinha_da_intelligence import (            # noqa: E402
    NAO_SEI, AGROCLIMATIC_NAO_PROVA, CAMPOS_DO_READY,
    CAMPOS_QUE_NAO_ATRAVESSAM, QUASE_ESPECIE,
    Corrida, ItemPronto, LeiViolada, e_falso,
)


# ── casos descartáveis, e todos eles inventados PARA SEREM DESCARTADOS ──────
def clima(item_id="IT-CLIMA-1", quando="2026-05-02", onde="IT-Veneto-Verona"):
    return ItemPronto(
        ITEM_ID=item_id, UNIVERSO="T2", SOURCE_ID="IT-T2-001",
        TEXTO="piogge abbondanti e umidita elevata",
        FACT_TIME=quando, FACT_LOCATION=onde,
        especie="AGROCLIMATIC_SIGNAL",
        sujeito_declarado="peronospora della vite")


def campo(item_id="IT-CAMPO-1", quando="2026-05-04", onde="IT-Veneto-Verona",
          fonte="IT-T3-005"):
    return ItemPronto(
        ITEM_ID=item_id, UNIVERSO="T3", SOURCE_ID=fonte,
        TEXTO="sintomi di peronospora segnalati in vigneto",
        FACT_TIME=quando, FACT_LOCATION=onde,
        especie="OBSERVED_FIELD_SIGNAL",
        sujeito_declarado="peronospora della vite")


def corrida(dominio="DOENCA", rid="P"):
    return Corrida(rid, "ha pressao de peronospora em Verona em Maio?",
                   dominio)


class P1_ClimaFavoravelNaoViraOcorrencia(unittest.TestCase):
    """P1 · clima favorável NÃO vira ocorrência. (Caso A do enunciado)"""

    def test_clima_sozinho_nao_alcanca_nivel_de_relato(self):
        c = corrida(rid="P1")
        s = c.g0_sinal(clima())
        c.g1_rastrear(s, {"hospedeiro": "SIM"})
        with self.assertRaises(LeiViolada) as e:
            c.g3_hipotese([s.SIGNAL_ID], "ha doenca em Verona?",
                          [], "um boletim que declare ausencia", "NIVEL_1")
        self.assertIn("OBSERVED_FIELD_SIGNAL", str(e.exception))
        self.assertIn("AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE", str(e.exception))

    def test_clima_sozinho_tambem_nao_alcanca_nivel_2(self):
        c = corrida(rid="P1b")
        s = c.g0_sinal(clima())
        with self.assertRaises(LeiViolada):
            c.g3_hipotese([s.SIGNAL_ID], "ha doenca?", [], "ausencia", "NIVEL_2")

    def test_e_a_lei_viaja_escrita(self):
        self.assertIn("AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE",
                      AGROCLIMATIC_NAO_PROVA)


class P2_SinalNaoViraAchadoSemPromocao(unittest.TestCase):
    """P2 · signal NÃO vira finding sem promoção."""

    def test_nao_ha_caminho_de_sinal_para_achado(self):
        c = corrida(rid="P2")
        s = c.g0_sinal(campo())
        c.g1_rastrear(s, {"hospedeiro": "SIM"})
        self.assertEqual(c.achados, {})
        # não existe método que aceite um sinal e devolva um achado
        self.assertFalse(hasattr(c, "promover_sinal"))
        for nome in ("g4_promover",):
            with self.assertRaises((LeiViolada, AttributeError, TypeError)):
                getattr(c, nome)(s)

    def test_hipotese_sem_validacao_nao_promove(self):
        c = corrida(rid="P2b")
        s = c.g0_sinal(campo())
        c.g1_rastrear(s, {"hospedeiro": "SIM"})
        h = c.g3_hipotese([s.SIGNAL_ID], "ha relato?", [],
                          "um desmentido da mesma fonte", "NIVEL_1")
        self.assertEqual(h.VALIDACAO, "PENDENTE")
        with self.assertRaises(LeiViolada):
            c.g4_promover(h)
        self.assertEqual(c.achados, {})


class P3_CruzamentoPreservaAsEvidencias(unittest.TestCase):
    """P3 · crossing preserva as evidências que o compõem."""

    def test_os_sinais_ficam_no_cruzamento_e_resolvem(self):
        c = corrida(rid="P3")
        s1 = c.g0_sinal(clima())
        s2 = c.g0_sinal(campo())
        x = c.g2_cruzar([s1, s2], "o clima permitia quando o campo relatou?")
        self.assertEqual(x.ESTADO, "PROVADO")
        self.assertEqual(set(x.SINAIS), {s1.SIGNAL_ID, s2.SIGNAL_ID})
        for sid in x.SINAIS:
            self.assertIn(sid, c.sinais)
            self.assertIn(c.sinais[sid].ITEM_ID, c.selecao)

    def test_o_cruzamento_herda_o_pior_lado(self):
        c = corrida(rid="P3b")
        s1 = c.g0_sinal(clima(quando="2026-05"))          # precisão MES
        s2 = c.g0_sinal(campo(quando="2026-05-04"))       # precisão DIA
        x = c.g2_cruzar([s1, s2], "compatibilidade temporal")
        self.assertEqual(x.ESTADO, "PROVADO")
        self.assertEqual(x.PRECISAO_TEMPO, "MES")

    def test_o_cruzamento_nao_tem_onde_escrever_julgamento(self):
        c = corrida(rid="P3c")
        x = c.g2_cruzar([c.g0_sinal(clima()), c.g0_sinal(campo())], "?")
        for proibido in ("APOIA", "CONTRADIZ", "SUPPORTS", "SUFICIENTE",
                         "CONCLUSAO", "VEREDITO"):
            self.assertNotIn(proibido, vars(x))


class P4_JudgmentTemProvenienciaPorDecisao(unittest.TestCase):
    """P4 · judgment tem provenance para cada decisão."""

    def test_cada_aresta_leva_regra_evidencia_e_motivo(self):
        c = corrida(rid="P4")
        s1, s2 = c.g0_sinal(clima()), c.g0_sinal(campo())
        x = c.g2_cruzar([s1, s2], "?")
        h = c.g3_hipotese([x.CROSSING_ID], "ha pressao?", [],
                          "boletim de ausencia", "NIVEL_2")
        a = c.julgar(h, "APOIA", x.CROSSING_ID, "clima e relato compativeis")
        b = c.julgar(h, "CONTRADIZ", s1.SIGNAL_ID,
                     "o clima sozinho nao distingue peronospora de oidio")
        for aresta in (a, b):
            self.assertTrue(aresta.REGRA)
            self.assertTrue(aresta.MOTIVO)
            self.assertTrue(aresta.EVIDENCIA)
        self.assertEqual(len(h.contraditorio()), 1)

    def test_julgamento_sem_motivo_e_recusado(self):
        c = corrida(rid="P4b")
        s = c.g0_sinal(campo())
        h = c.g3_hipotese([s.SIGNAL_ID], "?", [], "desmentido", "NIVEL_1")
        with self.assertRaises(LeiViolada):
            c.julgar(h, "APOIA", s.SIGNAL_ID, "   ")

    def test_o_traco_de_decisao_chega_ao_achado(self):
        c = corrida(rid="P4c")
        s = c.g0_sinal(campo())
        h = c.g3_hipotese([s.SIGNAL_ID], "ha relato?", ["a fonte e a ONPF"],
                          "desmentido", "NIVEL_1")
        c.julgar(h, "CONTRADIZ", s.SIGNAL_ID, "o relato nao declara metodo")
        c.validar(h, True, "agronomo", "nivel 1 correctamente declarado")
        a = c.g4_promover(h)
        t = a.TRACO_DE_DECISAO
        for chave in ("RUN_ID", "EVIDENCIAS", "PREMISSAS", "O_QUE_A_DERRUBA",
                      "ARESTAS", "CONTRADITORIO", "REGRA", "VALIDACAO",
                      "CONFIG"):
            self.assertIn(chave, t)
        self.assertEqual(len(t["CONTRADITORIO"]), 1,
                         "evidencia contraria escondida no achado")


class P5_CandidatoPodeSerRejeitado(unittest.TestCase):
    """P5 · candidate finding pode ser rejeitado sem virar finding."""

    def test_rejeicao_nao_produz_achado(self):
        c = corrida(rid="P5")
        s = c.g0_sinal(campo())
        h = c.g3_hipotese([s.SIGNAL_ID], "ha relato?", [], "desmentido",
                          "NIVEL_1")
        c.validar(h, False, "agronomo", "a fonte nao e autoridade no assunto")
        c.g4_rejeitar(h, "validacao recusada: fonte sem autoridade")
        self.assertEqual(h.ESTADO, "REJEITADA")
        self.assertEqual(c.achados, {})
        self.assertIn("REJEITADA", c.historia.estados_de(h.HYPOTHESIS_ID))

    def test_hipotese_sem_falsificador_nem_chega_a_nascer(self):
        c = corrida(rid="P5b")
        s = c.g0_sinal(campo())
        with self.assertRaises(LeiViolada):
            c.g3_hipotese([s.SIGNAL_ID], "ha relato?", [], "", "NIVEL_1")


class P6_AchadoPodeSerReaberto(unittest.TestCase):
    """P6 · finding pode ser reaberto. (Caso D do enunciado)"""

    def _achado(self, rid="P6"):
        c = corrida(rid=rid)
        s1, s2 = c.g0_sinal(clima()), c.g0_sinal(campo())
        x = c.g2_cruzar([s1, s2], "?")
        h = c.g3_hipotese([x.CROSSING_ID], "ha pressao?", [], "ausencia",
                          "NIVEL_2")
        c.validar(h, True, "agronomo", "nivel 2")
        return c, c.g4_promover(h)

    def test_as_sete_reversoes_tem_nome_e_destino(self):
        esperadas = {"RECORD_INVALIDATED", "NO_LONGER_PRESENT",
                     "NORMALIZATION_REVISED", "SOURCE_RETRACTED",
                     "DEPENDENCY_DISCOVERED", "AUTHORIZATION_CHANGED",
                     "WINDOW_CLOSED"}
        self.assertEqual(set(Corrida.CAUSAS_DE_REVERSAO), esperadas)

    def test_normalizacao_revista_reabre(self):
        c, a = self._achado()
        c.reverter(a, "NORMALIZATION_REVISED", "EPPO-GD-2026",
                   "a EPPO reclassificou o organismo")
        self.assertEqual(a.ESTADO, "REABERTO")
        self.assertTrue(a.ACTIVE)

    def test_dependencia_descoberta_rebaixa(self):
        c, a = self._achado("P6b")
        c.reverter(a, "DEPENDENCY_DISCOVERED", "IT-T3-005",
                   "as duas fontes eram a mesma ONPF")
        self.assertEqual(a.ESTADO, "REBAIXADO")

    def test_causa_sem_nome_canonico_e_recusada(self):
        c, a = self._achado("P6c")
        with self.assertRaises(LeiViolada):
            c.reverter(a, "MUDEI_DE_IDEIA", "x", "porque sim")


class P7_ReversaoNaoApagaHistorico(unittest.TestCase):
    """P7 · reversão não apaga histórico anterior."""

    def test_a_serie_completa_fica_legivel(self):
        c = corrida(rid="P7")
        s1, s2 = c.g0_sinal(clima()), c.g0_sinal(campo())
        x = c.g2_cruzar([s1, s2], "?")
        h = c.g3_hipotese([x.CROSSING_ID], "ha pressao?", [], "ausencia",
                          "NIVEL_2")
        c.validar(h, True, "agronomo", "nivel 2")
        a = c.g4_promover(h)
        antes = len(c.historia)
        c.reverter(a, "SOURCE_RETRACTED", "IT-T3-005", "boletim corrigido")
        c.reverter(a, "NORMALIZATION_REVISED", "EPPO-GD", "reclassificacao")

        self.assertGreater(len(c.historia), antes, "a historia encolheu")
        self.assertEqual(
            c.historia.estados_de(a.FINDING_ID),
            ["HIPOTESE", "CONFIRMADO", "REJEITADO", "REABERTO"])
        # e o traço de decisão original continua intacto
        self.assertEqual(a.TRACO_DE_DECISAO["EVIDENCIAS"], [x.CROSSING_ID])

    def test_os_eventos_sao_imutaveis(self):
        c = corrida(rid="P7b")
        c.g0_sinal(campo())
        evento = next(iter(c.historia))
        with self.assertRaises(Exception):
            evento.MOTIVO = "outra coisa"


class P8_OntologiaAmbiguaNaoEscolheEmSilencio(unittest.TestCase):
    """P8 · ontologia 1:N não escolhe silenciosamente. (Caso E do enunciado)"""

    def test_termo_1_para_N_fica_unresolved_com_o_termo_original(self):
        c = corrida(rid="P8")
        ambiguo = ItemPronto(
            ITEM_ID="IT-AMB-1", UNIVERSO="T3", SOURCE_ID="IT-T3-005",
            TEXTO="peronospora segnalata", FACT_TIME="2026-05-04",
            FACT_LOCATION="IT-Veneto-Verona",
            especie="OBSERVED_FIELD_SIGNAL",
            sujeito_declarado="peronospora")          # 1:N — três candidatos
        s = c.g0_sinal(ambiguo)
        self.assertEqual(s.MATCH_TYPE, "UNRESOLVED")
        self.assertEqual(s.SUJEITO, "peronospora",
                         "o termo original tem de sobreviver")
        self.assertNotIn(s.SUJEITO, ("PLASVI", "PERO1", "BREMLA"))
        self.assertEqual(s.PRECISAO_SEMANTICA, NAO_SEI)

    def test_e_um_cruzamento_sobre_termo_ambiguo_nao_se_faz(self):
        c = corrida(rid="P8b")
        ambiguo = ItemPronto(
            ITEM_ID="IT-AMB-2", UNIVERSO="T3", SOURCE_ID="IT-T3-006",
            TEXTO="peronospora", FACT_TIME="2026-05-04",
            FACT_LOCATION="IT-Veneto-Verona", especie="OBSERVED_FIELD_SIGNAL",
            sujeito_declarado="peronospora")
        x = c.g2_cruzar([c.g0_sinal(clima()), c.g0_sinal(ambiguo)], "?")
        self.assertEqual(x.ESTADO, "NOT_POSSIBLE")
        self.assertIn("identidade nao resolvida", x.MOTIVO)


class P9_UnknownNaoViraFalso(unittest.TestCase):
    """P9 · UNKNOWN não vira FALSE."""

    def test_perguntar_se_nao_sei_e_falso_levanta_lei(self):
        with self.assertRaises(LeiViolada):
            e_falso(NAO_SEI)
        with self.assertRaises(LeiViolada):
            e_falso(None)
        self.assertTrue(e_falso(False))
        self.assertFalse(e_falso(True))

    def test_criterio_duro_em_nao_sei_nao_passa_o_rastreio(self):
        c = corrida(rid="P9")
        s = c.g0_sinal(campo())
        c.g1_rastrear(s, {"hospedeiro": NAO_SEI})
        self.assertEqual(s.ESTADO, "DESCARTADO")
        self.assertIn("hospedeiro", s.MOTIVO_DO_DESCARTE)

    def test_o_rastreio_sabe_dizer_nao(self):
        """Um rastreio que nunca descarta não é um rastreio."""
        c = corrida(rid="P9b")
        s = c.g0_sinal(campo())
        c.g1_rastrear(s, {"hospedeiro": "NAO"})
        self.assertEqual(s.ESTADO, "DESCARTADO")

    def test_precisao_desconhecida_contamina_o_cruzamento(self):
        c = corrida(rid="P9c")
        sem_lugar = ItemPronto(
            ITEM_ID="IT-SEM-LUGAR", UNIVERSO="T3", SOURCE_ID="IT-T3-007",
            TEXTO="segnalazione", FACT_TIME="2026-05-04",
            especie="OBSERVED_FIELD_SIGNAL",
            sujeito_declarado="peronospora della vite")
        x = c.g2_cruzar([c.g0_sinal(clima()), c.g0_sinal(sem_lugar)], "?")
        self.assertEqual(x.ESTADO, "NOT_POSSIBLE")
        self.assertIn("area", x.MOTIVO)


class P10_FaltaDeEvidenciaProduzRequisito(unittest.TestCase):
    """P10 · falta de evidência produz COLLECTION_GAP, não chamada de coletor.

    E o nome canónico do que a Intelligence emite é `INTELLIGENCE_REQUIREMENT`:
    o `GAP`, a `DECISION` e a `ROTA` já têm dono em `GESTAO_DA_COLETA/v1`.
    """

    def test_item_sem_especie_bloqueia_e_levanta_requisito(self):
        c = corrida(rid="P10")
        mudo = ItemPronto(
            ITEM_ID="IT-MUDO-1", UNIVERSO="T3", SOURCE_ID="IT-T3-005",
            TEXTO="un testo qualsiasi", FACT_TIME="2026-05-04",
            FACT_LOCATION="IT-Veneto-Verona")     # especie = NAO SEI (o hoje)
        self.assertIsNone(c.g0_sinal(mudo))
        self.assertEqual(len(c.requisitos), 1)
        r = c.requisitos[0]
        self.assertIn("especie", r.O_QUE)
        self.assertEqual(r.LEVANTADO_POR, c.RUN_ID)

    def test_o_requisito_nao_pode_nomear_rota_executor_nem_decisao(self):
        c = corrida(rid="P10b")
        for veneno in ("chamar o coletor de boletins",
                       "usar a API da EPPO",
                       "DECISION = COLLECT_NOW",
                       "abrir a URL do bollettino"):
            with self.assertRaises(LeiViolada, msg=veneno):
                c.pedir_a_coleta(o_que=veneno, janela="2026", frescura="7d",
                                 grao="documento", porque="faz falta")

    def test_o_requisito_usa_o_vocabulario_que_ja_tem_dono(self):
        c = corrida(rid="P10c")
        r = c.pedir_a_coleta(
            o_que="a especie da evidencia nos boletins do Veneto",
            janela="campanha 2026", frescura="7 dias",
            grao="campo do contrato READY",
            porque="sem ela, clima e relato sao o mesmo texto")
        campos = set(vars(r))
        for c_necessidade in ("REQUIREMENT_ID", "O_QUE", "JANELA",
                              "FRESCURA_EXIGIDA", "GRAO", "PORQUE_IMPORTA",
                              "POLICY_VERSION"):
            self.assertIn(c_necessidade, campos)
        for c_da_collection in ("GAP_ID", "SATISFACTION_STATE", "DECISION",
                                "ROTA", "EXECUTOR"):
            self.assertNotIn(c_da_collection, campos)

    def test_a_maquina_nao_tem_nenhuma_porta_para_coletar(self):
        import espinha_da_intelligence as esp
        with open(esp.__file__, encoding="utf-8") as f:
            fonte = f.read().lower()
        for chamada in ("import requests", "urllib.request", "http://",
                        "https://", "subprocess", "socket"):
            self.assertNotIn(chamada, fonte,
                             "a espinha abriu um caminho paralelo de coleta")


class P11_DoisDominiosNaMesmaEspinha(unittest.TestCase):
    """P11 · dois domínios diferentes usam a mesma espinha."""

    def test_o_dominio_regulatorio_atravessa_os_mesmos_portoes(self):
        c = Corrida("P11", "quem depende do protioconazolo em Italia?",
                    "REGULATORIO")
        registo = ItemPronto(
            ITEM_ID="IT-REG-1", UNIVERSO="T9", SOURCE_ID="IT-BANCA-DATI",
            TEXTO="revoca dell'autorizzazione", FACT_TIME="2026-03-01",
            FACT_LOCATION="IT", especie="REGULATORY_AUTHORIZATION",
            sujeito_declarado="protioconazolo")
        s = c.g0_sinal(registo)
        self.assertEqual(s.MATCH_TYPE, "EXACT")
        c.g1_rastrear(s, {"autoridade": "SIM", "vigencia": "SIM"})
        self.assertEqual(s.ESTADO, "RASTREADO")
        h = c.g3_hipotese([s.SIGNAL_ID], "ha produtos afectados?",
                          ["o registo nacional esta completo"],
                          "um decreto posterior que reponha o uso", "REGISTO")
        c.julgar(h, "APOIA", s.SIGNAL_ID, "a autoridade publicou a revogacao")
        c.validar(h, True, "perito regulatorio", "vigencia conferida")
        a = c.g4_promover(h)
        self.assertEqual(a.ESTADO, "CONFIRMADO")
        c.reverter(a, "AUTHORIZATION_CHANGED", "GU-2026-99",
                   "o decreto foi suspenso")
        self.assertEqual(a.ESTADO, "SUBSTITUIDO")

    def test_o_dominio_so_traz_dados_nunca_portoes(self):
        """Se um domínio precisasse de portão próprio, seria uma segunda
        arquitetura — e é exactamente isso que este teste impede."""
        from espinha_da_intelligence import DOMINIOS, PacoteDeDominio
        campos = set(PacoteDeDominio.__dataclass_fields__)
        self.assertEqual(
            campos,
            {"NOME", "ONTOLOGIA", "CRITERIOS_DE_RASTREIO", "CRITERIOS_DUROS",
             "CHAVES_DE_CRUZAMENTO", "VALIDACAO_HUMANA_EXIGIDA", "NIVEIS",
             "NIVEL_EXIGE"})
        for pacote in DOMINIOS.values():
            for valor in vars(pacote).values():
                self.assertFalse(callable(valor),
                                 "um dominio trouxe comportamento proprio")

    def test_a_regua_de_um_dominio_nao_vale_no_outro(self):
        c = Corrida("P11c", "?", "REGULATORIO")
        s = c.g0_sinal(ItemPronto(
            ITEM_ID="IT-REG-2", UNIVERSO="T9", SOURCE_ID="IT-BANCA-DATI",
            TEXTO="autorizzazione", FACT_TIME="2026-03-01", FACT_LOCATION="IT",
            especie="REGULATORY_AUTHORIZATION",
            sujeito_declarado="metiram"))
        with self.assertRaises(LeiViolada):
            c.g3_hipotese([s.SIGNAL_ID], "?", [], "decreto", "NIVEL_2")


class P12_OportunidadeNaoGanhaFatosComerciais(unittest.TestCase):
    """P12 · Opportunity não ganha fatos comerciais a partir de dados públicos."""

    def _achado_publico(self):
        c = corrida(rid="P12")
        s1, s2 = c.g0_sinal(clima()), c.g0_sinal(campo())
        x = c.g2_cruzar([s1, s2], "?")
        h = c.g3_hipotese([x.CROSSING_ID], "ha pressao?", [], "ausencia",
                          "NIVEL_2")
        c.validar(h, True, "agronomo", "nivel 2")
        return c, c.g4_promover(h)

    def test_dado_publico_chega_a_A_e_a_B(self):
        c, a = self._achado_publico()
        for nivel in ("A", "B"):
            o = c.oportunidade(a, nivel, ["PUBLICO", "PUBLICO"])
            self.assertEqual(o["NIVEL"], nivel)
            self.assertFalse(o["CLIENT_SAFE"])

    def test_dado_publico_nao_chega_a_C_nem_a_D(self):
        c, a = self._achado_publico()
        for nivel in ("C", "D"):
            with self.assertRaises(LeiViolada) as e:
                c.oportunidade(a, nivel, ["PUBLICO", "PUBLICO"])
            self.assertIn("dado interno", str(e.exception))

    def test_C_exige_contrato_declarado_e_nao_so_a_palavra(self):
        c, a = self._achado_publico()
        with self.assertRaises(LeiViolada):
            c.oportunidade(a, "C", ["PUBLICO"], contrato_de_dado_privado="")
        o = c.oportunidade(a, "C", ["PUBLICO", "ADAMA_INTERNO"],
                           contrato_de_dado_privado="CTR-ADAMA-2026-01")
        self.assertEqual(o["NIVEL"], "C")

    def test_nivel_nao_declarado_e_recusado(self):
        c, a = self._achado_publico()
        with self.assertRaises(LeiViolada):
            c.oportunidade(a, NAO_SEI, ["PUBLICO"])


class FronteiraMedida(unittest.TestCase):
    """O CURRENT, escrito como teste para não virar lembrança.

    Se um dia o contrato READY passar a transportar a espécie da evidência,
    este teste falha — e falhar é o comportamento certo: é o sinal de que o
    bloqueio G0 caiu e a régua pode subir.
    """

    def test_o_contrato_de_entrada_e_o_do_dono_da_sala(self):
        """⚠️ D8. Este teste chamava-se «tem dezanove campos» e fixava o 19.

        O dono da Sala cresceu para 23 (migration 033) e a cópia ficou em 19 —
        e o teste continuou verde, porque comparava a cópia consigo própria.

            UM ALARME QUE OLHA PARA SI PROPRIO NAO AVISA NADA.

        Agora compara-se com o DONO, lido de forma independente (import real do
        módulo do dono, e não o mesmo parser AST que a espinha usa), e com a
        porta que constrói o READY (`admissao.pronto_para_inteligencia`).
        """
        sys.path.insert(0, os.path.join(RAIZ, "admissao"))
        import sala_de_espera as DONO                          # noqa: E402
        from admissao import decidir, pronto_para_inteligencia  # noqa: E402
        self.assertEqual(tuple(CAMPOS_DO_READY), tuple(DONO.CAMPOS_READY))
        item = {"id": "D8", "texto": "Ensaio de campo publicado com DOI",
                "source_id": "IT-T5-001", "fact_time": "2026-05-02"}
        d = decidir(item, "T5", corrida="d8")
        self.assertEqual(sorted(CAMPOS_DO_READY),
                         sorted(pronto_para_inteligencia(item, d)))
        self.assertGreaterEqual(len(CAMPOS_DO_READY), 23,
                                "a fronteira cresce; encolher em silencio e perda")

    def test_D8_sem_o_dono_a_espinha_falha_fechado(self):
        """Contraprova: um dono que deixa de declarar a lista rebenta, nao cai
        para uma lista de reserva."""
        import tempfile
        from pathlib import Path
        from espinha_da_intelligence import campos_do_dono, LeiViolada
        with tempfile.TemporaryDirectory() as d:
            falso = Path(d) / "sala_de_espera.py"
            falso.write_text("CAMPOS_READY = None\n", encoding="utf-8")
            with self.assertRaises(LeiViolada):
                campos_do_dono(falso)
            falso.write_text("OUTRA = ('A',)\n", encoding="utf-8")
            with self.assertRaises(LeiViolada):
                campos_do_dono(falso)
            falso.write_text("CAMPOS_READY = ('X', 'Y')\n", encoding="utf-8")
            self.assertEqual(campos_do_dono(falso), ("X", "Y"))

    def test_os_doze_campos_antigos_nenhum_se_perdeu(self):
        """A fronteira cresceu. Crescer não pode ser perder em silêncio."""
        for antigo in ("ESTADO", "ITEM_ID", "RAW_OBSERVATION_ID", "UNIVERSO",
                       "TEXTO", "SOURCE_ID", "SOURCE_LOCATION",
                       "FACT_LOCATION", "FACT_TIME", "CAPTURED_AT", "CORRIDA",
                       "ADMITIDO_POR"):
            self.assertIn(antigo, CAMPOS_DO_READY)

    def test_nenhum_campo_agronomico_atravessa_hoje(self):
        for ausente in CAMPOS_QUE_NAO_ATRAVESSAM:
            self.assertNotIn(ausente, CAMPOS_DO_READY)

    def test_a_classe_declarada_pela_fonte_nao_e_a_especie_da_evidencia(self):
        """⚠️ O quase-homónimo, pregado para não ser confundido por leitura.

        `SOURCE_DECLARED_EVIDENCE_CLASS` atravessa. `EVIDENCE_SPECIES` não.
        Quem os tratar como o mesmo campo faz um boletim agroclimático valer
        por relato de campo — e ai o G0 não caiu, foi contornado.

            DECLARADO PELA FONTE != MEDIDO NO DOCUMENTO.
        """
        self.assertIn(QUASE_ESPECIE, CAMPOS_DO_READY)
        self.assertNotIn("EVIDENCE_SPECIES", CAMPOS_DO_READY)
        self.assertNotEqual(QUASE_ESPECIE, "EVIDENCE_SPECIES")
        self.assertIn("EVIDENCE_SPECIES", CAMPOS_QUE_NAO_ATRAVESSAM)
        self.assertNotIn(QUASE_ESPECIE, CAMPOS_QUE_NAO_ATRAVESSAM)

    def test_o_item_real_de_hoje_nao_produz_sinal(self):
        c = corrida(rid="HOJE")
        real = ItemPronto(
            ITEM_ID="IT-REAL-1", UNIVERSO="T3", SOURCE_ID="IT-T3-005",
            TEXTO="bollettino fitosanitario", FACT_TIME="2026-05-04",
            FACT_LOCATION="IT-Veneto-Verona")
        self.assertIsNone(c.g0_sinal(real))
        self.assertEqual(c.sinais, {})
        self.assertEqual(len(c.requisitos), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
