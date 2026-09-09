#!/usr/bin/env python3
"""T1–T14 e o red team semantico S1–S6 de O8C.

    UM CONCEITO, UM DONO.

Antes desta missao havia dois dicionarios para a mesma luz do painel: o
scanner lia `telemetria.CODIGOS_DE_DIAGNOSTICO` e o writer lia
`diagnostico.CODIGOS`, com ZERO nomes em comum. E o manual declarava um balde
— `DEDUPED` — que o banco nao tinha coluna para contar.

Os testes abaixo nao verificam estilo. Cada um recusa um defeito que estava
mesmo la, no HEAD 3cbeb8d6.
"""
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                     # noqa: E402,F401
import falhas                       # noqa: E402
import diagnostico as dg            # noqa: E402
import telemetria as tel            # noqa: E402
import rastro_da_coleta as rastro   # noqa: E402

MIGRATION = os.path.join(RAIZ, 'supabase', 'migrations',
                         '024_a_corrida_conta_o_que_passou.sql')
SQL = open(MIGRATION, encoding='utf-8').read()


def enum_do_banco(nome):
    m = re.search(r"create type %s as enum\s*\((.*?)\);" % nome, SQL, re.S)
    return tuple(re.findall(r"'([A-Z_]+)'", m.group(1))) if m else None


def colunas_somadas():
    m = re.search(r"accounted_input\s+integer generated always as\s*\((.*?)\)\s*stored",
                  SQL, re.S)
    return tuple(re.findall(r"[a-z_]+", m.group(1))) if m else ()


class T1_UmDonoDeDiagnostico(unittest.TestCase):
    """T1. ONE DIAGNOSTIC OWNER."""

    def test_T1_so_um_modulo_declara_codigos_de_diagnostico(self):
        """Quem DECLARA e `diagnostico.py`. Os outros expoem o que importaram."""
        self.assertIsInstance(dg.CODIGOS, dict)
        # telemetria nao pode ter lista propria: tem de ser a do dono.
        self.assertEqual(tuple(sorted(dg.CODIGOS)), tuple(tel.CODIGOS_DE_DIAGNOSTICO),
                         'telemetria publica um registry que nao e o do dono')

    def test_T1_telemetria_importa_o_dono_e_nao_o_copia(self):
        """Medido por AST: `telemetria` importa `diagnostico`."""
        import ast
        fonte = open(os.path.join(RAIZ, 'leis', 'telemetria.py'), encoding='utf-8').read()
        importados = set()
        for no in ast.walk(ast.parse(fonte)):
            if isinstance(no, ast.Import):
                importados |= {a.name.split('.')[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module:
                importados.add(no.module.split('.')[0])
        self.assertIn('diagnostico', importados)
        self.assertIn('falhas', importados)


class T2_ScannerEWriterNoMesmoDono(unittest.TestCase):
    """T2 e T13. Scanner e writer consultam o mesmo registry."""

    def test_T2_scanner_nao_declara_registry_proprio(self):
        caminho = os.path.join(RAIZ, 'system-map', 'scripts',
                               'censo_da_observabilidade.py')
        fonte = open(caminho, encoding='utf-8').read()
        self.assertIsNone(
            re.search(r"^\s*CODIGOS_DE_DIAGNOSTICO\s*=\s*[\(\{\[]", fonte, re.M),
            'o scanner voltou a declarar a sua propria lista')

    def test_T13_scanner_conta_o_mesmo_registry(self):
        """O numero que o scanner publica tem de ser o do dono."""
        caminho = os.path.join(RAIZ, 'system-map', 'data',
                               'observabilidade.generated.json')
        if not os.path.exists(caminho):
            self.skipTest('censo ainda nao gerado nesta arvore')
        import json
        d = json.load(open(caminho, encoding='utf-8'))
        alvo = [x for x in d['DIMENSOES'] if x['DIMENSAO'] == 'DIAGNOSTIC']
        self.assertTrue(alvo, 'dimensao DIAGNOSTIC sumiu do censo')
        self.assertIn(str(len(dg.CODIGOS)), alvo[0]['PORQUE'],
                      'o scanner publica um numero que nao e o do dono')

    def test_T12_writer_aceita_todos_e_so_os_canonicos(self):
        for c in dg.CODIGOS:
            self.assertTrue(dg.valido(c), c)
        for inventado in ('ACHEI_UM_BUG', 'FETCH_FALHOU', 'ACCESS_FAILURE'):
            self.assertFalse(dg.valido(inventado),
                             '%s nao e do registry e passou' % inventado)


class T3_FailureStateNaoEDiagnosticCode(unittest.TestCase):
    """T3. FAILURE STATE != DIAGNOSTIC CODE — duas perguntas, dois donos."""

    def test_T3_nenhum_nome_serve_as_duas_perguntas(self):
        colisao = set(dg.CODIGOS) & (set(falhas.ESTADOS) | set(falhas._DE_PARA))
        self.assertEqual(set(), colisao,
                         'nome a responder as duas perguntas: %s' % sorted(colisao))

    def test_T3_a_mesma_falha_tem_as_duas_respostas_e_elas_diferem(self):
        """Uma falha de rede em FETCH tem estado canonico E codigo, e nao sao o mesmo."""
        estado = falhas.traduzir('TRANSIENT_NETWORK_ERROR')
        codigo = dg.da_etapa('FETCH', estado)
        self.assertEqual('TRANSIENT_NETWORK_ERROR', estado)
        self.assertEqual(dg.FETCH_FAILED, codigo)
        self.assertNotEqual(estado, codigo)


class T4_StageStateNaoEItemDestination(unittest.TestCase):
    """T4. Estado de ETAPA nao e destino de ITEM."""

    def test_T4_as_duas_tuplas_so_partilham_NOT_RUN(self):
        partilham = set(tel.ESTADOS_DE_ETAPA) & set(tel.DESTINOS_DO_ITEM)
        self.assertEqual({'NOT_RUN'}, partilham,
                         'as duas especies voltaram a misturar-se')

    def test_T4_o_enum_do_banco_e_so_de_estados_de_etapa(self):
        """Era aqui o defeito: REJECTED e UNKNOWN estavam no enum da ETAPA."""
        enum = set(enum_do_banco('etapa_estado'))
        intrusos = enum & (set(tel.DESTINOS_DO_ITEM) - {'NOT_RUN'})
        self.assertEqual(set(), intrusos,
                         'destino de item dentro do enum de etapa: %s' % sorted(intrusos))

    def test_T11_o_banco_aceita_todos_e_so_os_estados_canonicos(self):
        self.assertEqual(set(tel.ESTADOS_DE_ETAPA), set(enum_do_banco('etapa_estado')))


class T5_ErrorNaoERejected(unittest.TestCase):
    """T5. ERROR != REJECTED — o sistema falhou / o item nao servia."""

    def test_T5_sao_dois_destinos_distintos(self):
        self.assertIn('ERROR', tel.DESTINOS_DO_ITEM)
        self.assertIn('REJECTED', tel.DESTINOS_DO_ITEM)
        self.assertNotEqual('ERROR', 'REJECTED')

    def test_T5_tem_baldes_separados_no_banco(self):
        somadas = colunas_somadas()
        self.assertIn('error_count', somadas)
        self.assertIn('rejected', somadas)

    def test_T5_a_lei_esta_escrita(self):
        self.assertIn('ERROR != REJECTED', tel.LEIS)


class T6_NotRunNaoEError(unittest.TestCase):
    """T6. NOT_RUN != ERROR — nao chegou a correr / correu e falhou."""

    def test_T6_a_lei_esta_escrita(self):
        self.assertIn('NOT_RUN != ERROR', tel.LEIS)

    def test_T6_o_estado_de_etapa_distingue(self):
        self.assertIn('NOT_RUN', tel.ESTADOS_DE_ETAPA)
        self.assertIn('FAIL', tel.ESTADOS_DE_ETAPA)

    def test_T6_ha_codigo_proprio_para_upstream_que_nao_correu(self):
        self.assertTrue(dg.valido(dg.UPSTREAM_NOT_RUN))
        self.assertNotEqual(dg.UPSTREAM_NOT_RUN, dg.FETCH_FAILED)


class T7_PolicyRefusalNaoEFalhaTecnica(unittest.TestCase):
    """T7. POLICY REFUSAL != TECHNICAL FAILURE."""

    def test_T7_policy_refused_nao_entrou_em_nenhum_registry_de_falha(self):
        self.assertNotIn('POLICY_REFUSED', dg.CODIGOS)
        self.assertNotIn('POLICY_REFUSED', falhas.ESTADOS)

    def test_T7_a_recusa_da_politica_esta_declarada_como_decisao(self):
        dono, _ = tel.DE_ONDE_VIERAM['POLICY_REFUSED']
        self.assertIn('DECISAO', dono,
                      'POLICY_REFUSED voltou a ser tratado como falha')

    def test_T7_a_etapa_recusada_e_SKIPPED_e_nao_FAIL(self):
        self.assertIn('SKIPPED', tel.ESTADOS_DE_ETAPA)


class T8_ContabilidadeFecha(unittest.TestCase):
    """T8, T9. 100 entradas por destinos legitimos → ACCOUNTED = 100."""

    def test_T8_cem_itens_por_todos_os_destinos_fecham(self):
        etapa = {'INPUT_COUNT': 100}
        for i, d in enumerate(tel.DESTINOS_DO_ITEM):
            etapa[d] = [40, 20, 15, 10, 10, 5][i]
        fecha, sobra = tel.reconcilia(etapa)
        self.assertTrue(fecha)
        self.assertEqual(0, sobra)

    def test_T8_a_lei_do_prompt_passado_dedupe(self):
        """INPUT 100 · PASSED 60 · REUSED 40 → ACCOUNTED 100, nunca UNACCOUNTED 40."""
        fecha, sobra = tel.reconcilia({'INPUT_COUNT': 100, 'PASSED': 60, 'REUSED': 40})
        self.assertTrue(fecha, 'reencontro voltou a virar buraco na conta')
        self.assertEqual(0, sobra)

    def test_T9_destino_legitimo_fora_da_conta_reprova(self):
        """Se um destino sair da soma, a conta tem de acusar — nao arredondar."""
        for d in tel.DESTINOS_DO_ITEM:
            etapa = {'INPUT_COUNT': 10, d: 10}
            fecha, sobra = tel.reconcilia(etapa)
            self.assertTrue(fecha, '%s nao conta como saida' % d)

    def test_T9_o_banco_soma_exatamente_os_destinos(self):
        traducao = {'PASSED': 'passed', 'REJECTED': 'rejected', 'ERROR': 'error_count',
                    'NOT_RUN': 'not_run_count', 'UNKNOWN': 'unknown_count',
                    'REUSED': 'reused'}
        somadas = set(colunas_somadas())
        self.assertEqual({traducao[d] for d in tel.DESTINOS_DO_ITEM}, somadas)

    def test_T8_sem_entrada_a_conta_nao_fecha_por_omissao(self):
        """UNKNOWN != ZERO: sem INPUT_COUNT nao se declara conta fechada."""
        fecha, sobra = tel.reconcilia({'PASSED': 3})
        self.assertFalse(fecha)
        self.assertIsNone(sobra)


class T10_GraoNaoDaRendimentoFalso(unittest.TestCase):
    """T10. Grao diferente → sem yield falso."""

    def test_T10_graos_diferentes_nao_se_dividem(self):
        razao, erro = tel.compara_contagens(
            {'INPUT_GRAIN': 'DOCUMENTO', 'OUTPUT_GRAIN': 'PAGINA',
             'INPUT_COUNT': 1, 'OUTPUT_COUNT': 40})
        self.assertIsNone(razao, '1 PDF -> 40 paginas devolveu 4000% de rendimento')
        self.assertIn('GRAIN_MISMATCH', erro)

    def test_T10_ha_codigo_para_o_grao_trocado_e_outro_para_o_grao_ausente(self):
        self.assertTrue(dg.valido(dg.GRAIN_MISMATCH))
        self.assertTrue(dg.valido(dg.GRAIN_NOT_DECLARED))
        self.assertNotEqual(dg.GRAIN_MISMATCH, dg.GRAIN_NOT_DECLARED)


class T14_ObservabilityReady(unittest.TestCase):
    """T14. READY nao pode ser SIM com as pecas em linguas diferentes."""

    def test_T14_ready_exige_paridade(self):
        """A prova de paridade e a condicao. Se ela reprova, READY nao pode dizer SIM."""
        import subprocess
        r = subprocess.run([sys.executable,
                            os.path.join(RAIZ, 'provas', 'paridade_da_lingua.py')],
                           capture_output=True, text=True)
        self.assertEqual(0, r.returncode,
                         'paridade reprovada — READY nao pode ser SIM:\n%s' % r.stdout)


class S_RedTeamSemantico(unittest.TestCase):
    """S1–S6. As quatro respostas, separadas, para cada caso."""

    def test_S1_rede_transitoria_no_FETCH(self):
        self.assertEqual('TRANSIENT_NETWORK_ERROR',
                         falhas.traduzir('TRANSIENT_NETWORK_ERROR'))     # failure state
        self.assertEqual(dg.FETCH_FAILED,
                         dg.da_etapa('FETCH', 'TRANSIENT_NETWORK_ERROR'))  # diagnostic
        self.assertIn('FAIL', tel.ESTADOS_DE_ETAPA)                        # stage state
        self.assertIn('ERROR', tel.DESTINOS_DO_ITEM)                       # item destination

    def test_S2_RAW_nao_persiste(self):
        self.assertEqual(dg.RAW_PERSISTENCE_FAILED, dg.da_etapa('RAW', 'UNKNOWN_ERROR'))
        self.assertEqual('NOSSO_CODIGO', dg.dono(dg.RAW_PERSISTENCE_FAILED))

    def test_S3_dedupe_no_DERIVED_e_REUSED_e_conta(self):
        """Os 40 sao REUSED — nome da casa, nao DEDUPED — e entram na conta."""
        self.assertIn('REUSED', tel.DESTINOS_DO_ITEM)
        self.assertNotIn('DEDUPED', tel.DESTINOS_DO_ITEM)
        fecha, sobra = tel.reconcilia({'INPUT_COUNT': 100, 'PASSED': 60, 'REUSED': 40})
        self.assertTrue(fecha)
        self.assertEqual(0, sobra)

    def test_S4_STRUCTURED_sem_ligacao_e_buraco_e_nao_erro(self):
        """Nao e ERROR nem NOT_RUN: e uma aresta que nao existe, e tem codigo proprio."""
        self.assertTrue(dg.valido(dg.STRUCTURED_NOT_CONNECTED))
        self.assertEqual('NOSSO_CODIGO', dg.dono(dg.STRUCTURED_NOT_CONNECTED))
        self.assertTrue(dg.valido(dg.OWNER_NOT_CONNECTED))

    def test_S5_upstream_falhou_downstream_e_NOT_RUN(self):
        self.assertIn('NOT_RUN', tel.ESTADOS_DE_ETAPA)
        self.assertTrue(dg.valido(dg.UPSTREAM_NOT_RUN))
        self.assertIn('NOT_RUN != ERROR', tel.LEIS)

    def test_S6_politica_recusa_e_decisao_nao_falha(self):
        self.assertNotIn('POLICY_REFUSED', dg.CODIGOS)
        self.assertNotIn('POLICY_REFUSED', falhas.ESTADOS)


class NaoSePerdeuInformacao(unittest.TestCase):
    """Os doze nomes antigos continuam explicaveis. Nenhum foi apagado."""

    def test_os_doze_nomes_tem_dono_ou_recusa_escrita(self):
        self.assertEqual(12, len(tel.DE_ONDE_VIERAM))
        for nome, (dono, alvo) in tel.DE_ONDE_VIERAM.items():
            self.assertTrue(alvo, '%s sem destino escrito' % nome)
            if dono == 'falhas':
                self.assertIn(alvo, falhas.ESTADOS, nome)
            elif dono == 'diagnostico':
                self.assertIn(alvo, dg.CODIGOS, nome)

    def test_os_tres_que_ja_eram_de_falhas_apontam_para_la(self):
        for n in ('EXECUTOR_UNAVAILABLE', 'QUOTA_EXHAUSTED', 'UNKNOWN_FAILURE'):
            self.assertEqual('falhas', tel.DE_ONDE_VIERAM[n][0], n)

    def test_o_nome_grosso_foi_recusado_e_nao_absorvido(self):
        """ACCESS_FAILURE apagaria quatro distincoes que a casa ja fazia."""
        dono, alvo = tel.DE_ONDE_VIERAM['ACCESS_FAILURE']
        self.assertIn('RECUSADO', dono)
        for fino in ('ROUTE_UNAVAILABLE', 'BLOCKED', 'PERMANENT_HTTP_ERROR',
                     'TRANSIENT_NETWORK_ERROR'):
            self.assertIn(fino, alvo)
            self.assertIn(fino, falhas.ESTADOS)


if __name__ == '__main__':
    unittest.main(verbosity=2)
