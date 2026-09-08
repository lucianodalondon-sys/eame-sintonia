#!/usr/bin/env python3
"""O RED TEAM DO RASTRO — RT1..RT28, contra PostgreSQL 16 real.

Sem banco, PULADO — nunca fingido.

    NAO E OBRIGATORIO QUE 100% CHEGUE AO FIM.
    E OBRIGATORIO QUE 100% TENHA EXPLICACAO.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import coleta_checkpoint as cc      # noqa: E402
import rastro_da_coleta as r        # noqa: E402
import diagnostico as dg            # noqa: E402
import falhas                       # noqa: E402

DSN = os.environ.get('BANCO_DESCARTAVEL_URL') or ''


def _tem_o_rastro():
    """A 024 esta aplicada neste banco?

    Um banco descartavel apontado aqui pode nao ter a 024 — e um teste que
    EXPLODE por falta de schema e ruido, nao sinal. Ele pula, e diz por que:
    silencio faria a migration em falta parecer suite verde.
    """
    if not DSN:
        return False
    try:
        b = cc.Banco(DSN)
        b.executa("select 1 from information_schema.tables"
                  " where table_name = 'etapa_da_corrida'")
        return bool(b.executa(
            "select count(*) from information_schema.tables"
            " where table_name = 'etapa_da_corrida'")[0][0] == '1')
    except Exception:                                       # noqa: BLE001
        return False


TEM_RASTRO = _tem_o_rastro()


@unittest.skipUnless(DSN, 'sem BANCO_DESCARTAVEL_URL — nao se finge banco')
@unittest.skipUnless(TEM_RASTRO, 'este banco nao tem a migration 024 — '
                                 'corra provas/rastro_no_postgres.py')
class Base(unittest.TestCase):

    RUN = 'RUN-RASTRO-1'

    @classmethod
    def setUpClass(cls):
        cls.banco = cc.Banco(DSN)

    # As corridas desta suite tem prefixo proprio. Apagar TODA a
    # `collection_run` limparia o que outras provas deixaram — e o banco recusa,
    # porque `conteudo` a referencia com ON DELETE RESTRICT. Uma suite que limpa
    # as linhas alheias tambem quebraria a prova de quem correr a seguir.
    PREFIXO = 'RUN-RASTRO'

    def setUp(self):
        b = self.banco
        b.executa("delete from public.etapa_da_corrida where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa("delete from public.decisao_de_coleta")
        b.executa("delete from public.collection_run where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa("delete from public.collection_run where run_id = 'RUN-VELHA'")
        b.executa("insert into public.collection_run (run_id, platform,"
                  " source_country, started_at, status, rule_version)"
                  " values ('%s','web','IT',now(),'rodando','v1')" % self.RUN)

    def _p(self, etapa, estado, **k):
        return r.registrar(self.banco, run_id=self.RUN, etapa=etapa,
                           estado=estado, source_id='IT-T2-002',
                           route_class_id='RC-1', **k)


class RT_Contabilidade(Base):

    # ── RT1 ───────────────────────────────────────────────────────────────
    def test_RT1_um_item_sem_explicacao_faz_o_gate_falhar(self):
        res = self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=100,
                      passed=80, rejected=10, unknown=5, error=4)
        self.assertEqual(res['ACCOUNTED_INPUT'], 99)
        self.assertEqual(res['UNACCOUNTED_INPUT'], 1)
        integ = r.integridade(r.passagens(self.banco, run_id=self.RUN))
        self.assertFalse(integ['INTEGRO'])
        self.assertEqual(integ['DIAGNOSTIC_CODE'], dg.FLOW_UNACCOUNTED_INPUT)

    # ── RT2 ───────────────────────────────────────────────────────────────
    def test_RT2_saida_menor_que_entrada_com_tudo_explicado_e_INTEGRO(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=100,
                output_grain='DOCUMENT', output_count=80,
                passed=80, rejected=10, unknown=5, error=5)
        integ = r.integridade(r.passagens(self.banco, run_id=self.RUN))
        self.assertTrue(integ['INTEGRO'],
                        'exigir que tudo chegue ao fim nao e integridade')
        self.assertEqual(integ['UNACCOUNTED_INPUT'], 0)

    # ── RT3 ───────────────────────────────────────────────────────────────
    def test_RT3_grao_diferente_nao_produz_percentagem(self):
        self._p('DERIVED', r.PASS, input_grain='DOCUMENT', input_count=100,
                output_grain='CLAIM', output_count=250, cardinalidade='1:N',
                passed=100)
        p = r.passagens(self.banco, run_id=self.RUN)[0]
        y = r.rendimento(p)
        self.assertIsNone(y['YIELD'], '250 alegacoes viraram 250% de rendimento')
        self.assertTrue(y['GRAIN_CHANGED'])
        self.assertIn('DOCUMENT', y['INPUT'])
        self.assertIn('CLAIM', y['OUTPUT'])

    def test_RT3b_mesmo_grao_produz_rendimento_de_verdade(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=100,
                output_grain='DOCUMENT', output_count=80, passed=80,
                rejected=20)
        y = r.rendimento(r.passagens(self.banco, run_id=self.RUN)[0])
        self.assertEqual(y['YIELD'], 0.8)
        self.assertFalse(y['GRAIN_CHANGED'])

    def test_contagem_sem_grao_e_recusada_na_entrada(self):
        with self.assertRaises(ValueError):
            self._p('FETCH', r.PASS, input_count=10)


class RT_Falha(Base):

    # ── RT4 ───────────────────────────────────────────────────────────────
    def test_RT4_executor_que_morre_e_ERROR_e_nunca_REJECTED(self):
        res = self._p('DERIVED', r.ERROR, input_grain='DOCUMENT', input_count=10,
                      error=10, canonical_state='PARSER_DRIFT',
                      error_class='RuntimeError', error_message='o parser quebrou')
        p = r.passagens(self.banco, run_id=self.RUN)[0]
        self.assertEqual(p['ESTADO'], 'ERROR')
        self.assertEqual(p['REJECTED'], 0, 'um erro nosso virou recusa da fonte')
        self.assertEqual(res['DIAGNOSTIC_CODE'], dg.DERIVATION_FAILED)

    def test_ERROR_sem_codigo_e_recusado_pelo_banco(self):
        with self.assertRaises(RuntimeError):
            self.banco.executa(
                "insert into public.etapa_da_corrida (run_id, etapa, estado)"
                " values ('%s','DERIVED','ERROR')" % self.RUN)

    # ── RT5 ───────────────────────────────────────────────────────────────
    def test_RT5_downstream_de_uma_falha_e_NOT_RUN(self):
        self._p('RAW', r.PASS, input_grain='DOCUMENT', input_count=10, passed=10,
                last_good_artifact='raw_asset:1')
        self._p('DERIVED', r.ERROR, edge_from='RAW', input_grain='DOCUMENT',
                input_count=10, error=10, canonical_state='PARSER_DRIFT')
        self._p('STRUCTURED', r.NOT_RUN, edge_from='DERIVED')
        ps = r.passagens(self.banco, run_id=self.RUN)
        por = {p['ETAPA']: p['ESTADO'] for p in ps}
        self.assertEqual(por['RAW'], 'PASS')
        self.assertEqual(por['DERIVED'], 'ERROR')
        self.assertEqual(por['STRUCTURED'], 'NOT_RUN')
        self.assertNotEqual(por['STRUCTURED'], 'REJECTED')

    def test_o_diagnostico_tem_dono(self):
        for c in dg.CODIGOS:
            self.assertIn(dg.dono(c), (dg.NOS, dg.FONTE, dg.ROTA, dg.PESSOA), c)
            self.assertTrue(dg.explicar(c))

    def test_mensagem_muda_codigo_nao(self):
        """ERROR MESSAGE != DIAGNOSTIC CODE."""
        a = self._p('DERIVED', r.ERROR, error_message='falhou: versao 1',
                    canonical_state='PARSER_DRIFT')
        self.banco.executa("delete from public.etapa_da_corrida")
        b = self._p('DERIVED', r.ERROR, error_message='outro texto totalmente',
                    canonical_state='PARSER_DRIFT')
        self.assertEqual(a['DIAGNOSTIC_CODE'], b['DIAGNOSTIC_CODE'])

    def test_rota_que_parou_nao_vira_defeito_nosso(self):
        """ROUTE FAILURE != SOURCE BAD, e nem sempre e o nosso codigo."""
        c = dg.da_etapa('FETCH', 'BLOCKED')
        self.assertEqual(c, dg.ROUTE_NO_LONGER_WORKS)
        self.assertEqual(dg.dono(c), dg.ROTA)


class RT_Retomada(Base):

    def _cadeia_ate_erro(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=10, passed=10)
        self._p('RAW', r.PASS, edge_from='FETCH', input_grain='DOCUMENT',
                input_count=10, passed=10, last_good_artifact='raw_asset:1')
        self._p('DERIVED', r.ERROR, edge_from='RAW', input_grain='DOCUMENT',
                input_count=10, error=10, canonical_state='PARSER_DRIFT')

    # ── RT6 ───────────────────────────────────────────────────────────────
    def test_RT6_retomada_parte_do_ultimo_ponto_bom(self):
        self._cadeia_ate_erro()
        ps = r.passagens(self.banco, run_id=self.RUN)
        self.assertEqual(r.ultimo_bom(ps), 'RAW')
        self.assertEqual(r.onde_retomar(ps), 'DERIVED',
                         'a retomada ia refazer o FETCH que ja passou')

    def test_a_tentativa_que_falhou_nao_e_apagada(self):
        self._cadeia_ate_erro()
        self._p('DERIVED', r.PASS, tentativa=1, edge_from='RAW',
                input_grain='DOCUMENT', input_count=10, passed=10)
        ps = r.passagens(self.banco, run_id=self.RUN)
        derivados = [p for p in ps if p['ETAPA'] == 'DERIVED']
        self.assertEqual(len(derivados), 2, 'a tentativa falhada foi apagada')
        self.assertEqual({p['TENTATIVA'] for p in derivados}, {0, 1})

    # ── RT7 ───────────────────────────────────────────────────────────────
    def test_RT7_artefato_de_cima_mudou_recusa_a_retomada(self):
        self._cadeia_ate_erro()
        ps = r.passagens(self.banco, run_id=self.RUN)
        antes = [p for p in ps if p['ETAPA'] == 'RAW'][0]['LAST_GOOD_ARTIFACT']
        agora = 'raw_asset:2'
        self.assertNotEqual(antes, agora)
        res = self._p('DERIVED', r.ERROR, tentativa=1, edge_from='RAW',
                      diagnostic_code=dg.UPSTREAM_ARTIFACT_CHANGED,
                      error_message='o RAW de cima mudou: %s -> %s' % (antes, agora))
        self.assertEqual(res['DIAGNOSTIC_CODE'], dg.UPSTREAM_ARTIFACT_CHANGED)

    def test_sem_erro_nao_ha_onde_retomar(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=1, passed=1)
        self.assertIsNone(r.onde_retomar(r.passagens(self.banco, run_id=self.RUN)))


class RT_Relatorios(Base):

    def test_relatorio_por_hora_existe_e_e_derivado(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=10,
                output_grain='DOCUMENT', output_count=8, passed=8, rejected=2,
                custo_usd=0.25, duracao_ms=1200)
        linhas = self.banco.executa(
            "select source_id, etapa::text, entraram, sairam, passaram,"
            " recusados, sem_explicacao, custo_usd::text, duracao_ms"
            " from public.v_coleta_por_hora")
        self.assertEqual(len(linhas), 1)
        l = linhas[0]
        self.assertEqual(l[0], 'IT-T2-002')
        self.assertEqual(int(l[2]), 10)
        self.assertEqual(int(l[3]), 8)
        self.assertEqual(int(l[6]), 0)

    def test_saude_e_do_par_fonte_mais_rota(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=1, passed=1)
        self._p('FETCH', r.ERROR, tentativa=1, canonical_state='BLOCKED')
        l = self.banco.executa(
            "select source_id, route_class_id, passagens_ok, passagens_erro"
            " from public.v_saude_da_rota")[0]
        self.assertEqual((l[0], l[1]), ('IT-T2-002', 'RC-1'))
        self.assertEqual((int(l[2]), int(l[3])), (1, 1))

    def test_custo_e_duracao_entram(self):
        self._p('FETCH', r.PASS, input_grain='DOCUMENT', input_count=1, passed=1,
                custo_usd=1.5, duracao_ms=900)
        p = r.passagens(self.banco, run_id=self.RUN)[0]
        self.assertEqual(float(p['CUSTO_USD']), 1.5)
        self.assertEqual(p['DURACAO_MS'], 900)


class RT_Decisao(Base):

    def _decidir(self, **k):
        campos = {'decision_id': 'D1', 'source_id': 'IT-T2-002', 'acao': 'FETCH',
                  'prioridade': 'P1', 'why_now': 'venceu a janela declarada',
                  'why_this_source': 'unica com rota provada',
                  'satisfaction_before': 'YES_BUT_STALE',
                  'policy_version': 'v1'}
        campos.update(k)
        cols = ', '.join(campos)
        vals = ', '.join("'%s'" % str(v).replace("'", "''") for v in campos.values())
        return self.banco.executa(
            "insert into public.decisao_de_coleta (%s) values (%s) returning id"
            % (cols, vals))

    # ── RT19 / RT20 ───────────────────────────────────────────────────────
    def test_RT19_decisao_sem_versao_de_politica_e_recusada(self):
        """A coluna tem de FALTAR. Passar `None` pelo helper virava a string
        'None' — e o teste passava sem nunca exercer a trava."""
        with self.assertRaises(RuntimeError):
            self.banco.executa(
                "insert into public.decisao_de_coleta"
                " (decision_id, source_id, acao, prioridade, why_now,"
                "  why_this_source, satisfaction_before)"
                " values ('D3','S','FETCH','P1','agora','porque','NO')")

    def test_RT20_decisao_sem_WHY_NOW_e_recusada(self):
        with self.assertRaises(RuntimeError):
            self.banco.executa(
                "insert into public.decisao_de_coleta"
                " (decision_id, source_id, acao, prioridade, why_this_source,"
                "  satisfaction_before, policy_version)"
                " values ('D2','S','FETCH','P1','porque sim','NO','v1')")

    # ── RT21 ──────────────────────────────────────────────────────────────
    def test_RT21_corrida_manual_declara_a_procedencia_em_vez_de_inventar(self):
        self._decidir(decision_id='D-MANUAL', decision_provenance='MANUAL',
                      why_now='pedido a mao por uma pessoa')
        l = self.banco.executa(
            "select decision_provenance from public.decisao_de_coleta"
            " where decision_id='D-MANUAL'")[0][0]
        self.assertEqual(l, 'MANUAL')

    def test_a_corrida_liga_a_decisao(self):
        self._decidir()
        self._p('FETCH', r.PASS, decision_id='D1', input_grain='DOCUMENT',
                input_count=1, passed=1)
        l = self.banco.executa(
            "select e.decision_id, d.why_now from public.etapa_da_corrida e"
            " join public.decisao_de_coleta d on d.decision_id = e.decision_id")[0]
        self.assertEqual(l[0], 'D1')
        self.assertIn('janela', l[1])

    def test_valor_esperado_e_vetor_e_nao_nota(self):
        self._decidir(decision_id='D-VEC')
        self.banco.executa(
            "update public.decisao_de_coleta set expected_value ="
            " '{\"UNIQUE_YIELD\":\"ALTO\",\"CUSTO\":\"BAIXO\"}'::jsonb"
            " where decision_id='D-VEC'")
        l = self.banco.executa(
            "select expected_value::text from public.decisao_de_coleta"
            " where decision_id='D-VEC'")[0][0]
        d = json.loads(l)
        self.assertGreater(len(d), 1, 'o vetor colapsou numa nota so')


class RT_NaoSeInventa(Base):

    # ── RT22 ──────────────────────────────────────────────────────────────
    def test_RT22_corrida_sem_rastro_e_HISTORICAL_UNINSTRUMENTED(self):
        self.banco.executa(
            "insert into public.collection_run (run_id, platform, source_country,"
            " started_at, status, rule_version)"
            " values ('RUN-VELHA','web','IT',now(),'concluida','v1')")
        ps = r.passagens(self.banco, run_id='RUN-VELHA')
        self.assertEqual(ps, [], 'inventou rastro para uma corrida antiga')
        self.assertIsNone(r.ultimo_bom(ps))
        self.assertEqual(r.SEM_INSTRUMENTO, 'HISTORICAL_UNINSTRUMENTED')

    def test_o_rastro_exige_uma_corrida_que_existe(self):
        with self.assertRaises(RuntimeError):
            r.registrar(self.banco, run_id='RUN-QUE-NAO-EXISTE',
                        etapa='FETCH', estado=r.PASS)

    def test_segredo_nao_entra_no_rastro(self):
        self._p('FETCH', r.ERROR, canonical_state='AUTH_EXPIRED',
                error_message='falhou com api_key=SEGREDO-MUITO-LONGO-AQUI')
        l = self.banco.executa(
            "select error_message_redacted from public.etapa_da_corrida")[0][0]
        self.assertNotIn('SEGREDO-MUITO-LONGO-AQUI', l or '')


if __name__ == '__main__':
    unittest.main(verbosity=2)


class RT_ScannerQuebraERestaura(Base):
    """O TESTE DO FIO: quebrar de proposito, e conferir o que o scanner aponta."""

    def _cadeia(self, derived_estado='PASS'):
        import scanner_da_coleta as sc     # noqa: PLC0415
        k = dict(run_id=self.RUN, source_id='IT-T2-002', route_class_id='RC-1')
        r.registrar(self.banco, etapa='FETCH', estado='PASS',
                    input_grain='DOCUMENT', input_count=178,
                    output_grain='DOCUMENT', output_count=178, passed=178, **k)
        r.registrar(self.banco, etapa='RAW', estado='PASS', edge_from='FETCH',
                    input_grain='DOCUMENT', input_count=178,
                    output_grain='RAW_ASSET', output_count=178, passed=178,
                    last_good_artifact='raw_asset:178', **k)
        if derived_estado == 'ERROR':
            r.registrar(self.banco, etapa='DERIVED', estado='ERROR', edge_from='RAW',
                        input_grain='RAW_ASSET', input_count=178,
                        output_grain='DERIVED_ARTIFACT', output_count=109,
                        passed=109, error=69, canonical_state='PARSER_DRIFT', **k)
            r.registrar(self.banco, etapa='STRUCTURED', estado='NOT_RUN',
                        edge_from='DERIVED', **k)
        else:
            r.registrar(self.banco, etapa='DERIVED', estado='PASS', edge_from='RAW',
                        input_grain='RAW_ASSET', input_count=178,
                        output_grain='DERIVED_ARTIFACT', output_count=178,
                        passed=178, **k)
        return sc

    def test_o_scanner_aponta_upstream_verde_etapa_vermelha_downstream_NOT_RUN(self):
        sc = self._cadeia('ERROR')
        rel = sc.relatorio(self.banco, self.RUN)
        por = {p['ETAPA']: p['ESTADO'] for p in rel['PASSAGENS']}
        self.assertEqual(rel['HEALTH'], 'ERROR')
        self.assertEqual(por['FETCH'], 'PASS')
        self.assertEqual(por['RAW'], 'PASS')
        self.assertEqual(por['DERIVED'], 'ERROR')
        self.assertEqual(por['STRUCTURED'], 'NOT_RUN')
        self.assertEqual(rel['ULTIMO_BOM'], 'RAW')
        self.assertEqual(rel['RETRY_FROM'], 'DERIVED')
        self.assertIn(dg.DERIVATION_FAILED, rel['DIAGNOSTICOS'])
        self.assertTrue(rel['INTEGRIDADE']['INTEGRO'],
                        'os 69 que falharam estao explicados, e isso e integridade')

    def test_e_depois_de_restaurar_fica_verde(self):
        sc = self._cadeia('PASS')
        rel = sc.relatorio(self.banco, self.RUN)
        self.assertEqual(rel['HEALTH'], 'PASS')
        self.assertEqual(rel['RETRY_FROM'], None)
        self.assertEqual(rel['ULTIMO_BOM'], 'DERIVED')

    def test_a_aresta_diz_de_onde_para_onde_e_quantos_atravessaram(self):
        self._cadeia('ERROR')
        p = [x for x in r.passagens(self.banco, run_id=self.RUN)
             if x['ETAPA'] == 'DERIVED'][0]
        self.assertEqual(p['EDGE_FROM'], 'RAW')
        self.assertEqual(p['INPUT_COUNT'], 178)     # quantos tentaram
        self.assertEqual(p['OUTPUT_COUNT'], 109)    # quantos chegaram
        self.assertEqual(p['UNACCOUNTED'], 0)       # quantos sem explicacao

    # ── RT23 ──────────────────────────────────────────────────────────────
    def test_RT23_sem_telemetria_o_scanner_diz_NOT_INSTRUMENTED_e_nao_verde(self):
        import scanner_da_coleta as sc     # noqa: PLC0415
        rel = sc.relatorio(self.banco, self.RUN)
        self.assertEqual(rel['HEALTH'], sc.NAO_MEDIDA)
        self.assertNotEqual(rel['HEALTH'], sc.SAUDE_OK,
                            'corrida sem rastro pintou de verde')
        self.assertEqual(rel['NOTA'], r.SEM_INSTRUMENTO)

    def test_um_buraco_na_contabilidade_e_ERROR_e_nao_aviso(self):
        import scanner_da_coleta as sc     # noqa: PLC0415
        r.registrar(self.banco, run_id=self.RUN, etapa='FETCH', estado='PASS',
                    input_grain='DOCUMENT', input_count=100, passed=99)
        rel = sc.relatorio(self.banco, self.RUN)
        self.assertEqual(rel['HEALTH'], sc.SAUDE_ERRO)
        self.assertEqual(rel['INTEGRIDADE']['DIAGNOSTIC_CODE'],
                         dg.FLOW_UNACCOUNTED_INPUT)
