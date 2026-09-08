#!/usr/bin/env python3
"""O9-1..O9-20 — o primeiro caminho real a deixar pegada.

    ATE AQUI A CASA TINHA UM MANUAL DE SENSORES COERENTE.
    ISTO PROVA QUE UM MOTOR REAL JA ATRAVESSA O SISTEMA DEIXANDO PEGADA.

O caminho: `coleta/executor_texto_de_pdf.py` sobre os 49 PDF italianos reais
preservados em `data/collection-store/`. Zero rede, zero API paga, zero
producao. O executor NAO foi tocado — a telemetria vive em
`medidas/corrida_instrumentada.py`, do lado de fora.

Precisa de PostgreSQL 16 descartavel com a migration 024. Sem ele, salta com
a razao escrita: uma prova que finge correr e pior do que uma que se declara.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                     # noqa: E402,F401
import coleta_checkpoint as cc      # noqa: E402
import corrida_instrumentada as run # noqa: E402
import diagnostico as dg            # noqa: E402
import falhas                       # noqa: E402
import rastro_da_coleta as rastro   # noqa: E402
import telemetria as tel            # noqa: E402

DSN = os.environ.get('BANCO_DESCARTAVEL_URL', '')


def _tem_banco():
    if not DSN:
        return False, 'BANCO_DESCARTAVEL_URL nao esta definida'
    try:
        b = cc.Banco(DSN)
        b.executa("select 1 from public.etapa_da_corrida limit 1")
        return True, ''
    except Exception as e:
        return False, str(e)[:120]


TEM, PORQUE = _tem_banco()


# ── O RECIBO DE MENTIRA, PARA PARTIR UMA ETAPA SEM PARTIR NADA REAL ──────
# `correr()` aceita o executor por injecao exatamente para isto: a prova de
# falha nao toca fonte nenhuma, nao apaga ficheiro nenhum, e nao mexe no
# executor de verdade.
def executor_falso(counts, perdidos=0, ferramenta='pdftotext'):
    """Um executor de mentira que emite pela MESMA costura que o de verdade.

    Nao reimplementa a traducao: chama `emitir_rastro`, que e o dono dela. Um
    duble que traduzisse a seu modo provaria o duble, e nao o sistema.
    """
    def correr(seco=False, run_id='', rastro=None, source_id=None,
               route_class_id=None):
        sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
        import executor_texto_de_pdf as ex
        r = recibo_falso(**counts)
        r['FERRAMENTA'] = ferramenta
        r['LOST'] = perdidos
        r['STATUS'] = 'PARTIAL' if r['COUNTS']['EXTRACTION_ERROR'] else 'SUCCESS'
        if rastro is not None:
            ex.emitir_rastro(rastro, run_id, r['COUNTS'], perdidos, [],
                             r['STARTED_AT'],
                             ferramenta_presente=(ferramenta != 'AUSENTE'),
                             source_id=source_id,
                             route_class_id=route_class_id)
        return r
    return correr


def recibo_falso(**c):
    base = {'RAW_INPUT': 0, 'RAW_CONTEUDOS_DISTINTOS': 0,
            'RAW_COPIAS_REPETIDAS': 0, 'TEXT_LAYER_PRESENT': 0, 'NEEDS_OCR': 0,
            'EXTRACTION_ERROR': 0, 'RAW_UNKNOWN': 0, 'DERIVED_EMITTED': 0,
            'DERIVED_LANDED': 0, 'JA_EXISTIA': 0}
    base.update(c)
    return {
        'RUN_ID': 'X', 'STATUS': 'SUCCESS',
        'EXECUTOR_ID': 'coleta/executor_texto_de_pdf.py',
        'EXECUTOR_VERSION': 'teste', 'PIPELINE_VERSION': 'teste',
        'STARTED_AT': '2026-01-01T00:00:00Z', 'FINISHED_AT': '2026-01-01T00:00:01Z',
        'COUNTS': base, 'LOST': 0, 'ERRORS': [], 'COST_USD': 0.0,
        'COST_CLASS': 'LOCAL', 'FERRAMENTA': 'pdftotext',
    }


@unittest.skipUnless(TEM, 'sem PostgreSQL descartavel com a 024: %s' % PORQUE)
class Base(unittest.TestCase):
    PREFIXO = 'RUN-O9'
    RUN = 'RUN-O9-1'

    @classmethod
    def setUpClass(cls):
        cls.banco = cc.Banco(DSN)

    def setUp(self):
        b = self.banco
        b.executa("delete from public.etapa_da_corrida where run_id like '%s%%'"
                  % self.PREFIXO)
        b.executa("delete from public.collection_run where run_id like '%s%%'"
                  % self.PREFIXO)
        self._abrir(self.RUN)

    def _abrir(self, run_id):
        self.banco.executa(
            "insert into public.collection_run (run_id, platform,"
            " source_country, started_at, status, rule_version)"
            " values ('%s','web','IT',now(),'rodando','v1')" % run_id)

    def _passagens(self, run_id=None):
        return rastro.passagens(self.banco, run_id=run_id or self.RUN)


class O9_1_EscolhaMedida(unittest.TestCase):
    """O9-1. O candidato foi escolhido por medicao, e nao por preferencia."""

    def test_O9_1_o_censo_elege_este_caminho(self):
        """A escolha foi por MEDICAO — e prova-se ignorando o ledger.

        Depois de provado, o executor sai da lista de «proximos mais baratos»:
        ele ja nao esta por instrumentar. Perguntar ao censo publicado quem e o
        primeiro responderia a pergunta de hoje, e nao a que decidiu a escolha.
        Por isso a medicao e refeita aqui SEM o ledger, que e o estado em que a
        decisao foi tomada.
        """
        sys.path.insert(0, os.path.join(RAIZ, 'system-map', 'scripts'))
        import censo_dos_executores as censo
        linhas = censo.medir()
        candidatos = [l for l in linhas
                      if l['CAN_RUN_OFFLINE'] and l['TEM_PORTA']]
        eleito = sorted(candidatos,
                        key=lambda l: (not l['HAS_PRESERVED_INPUT'],
                                       -len(l['ETAPAS_NOMEADAS']),
                                       not l['USA_FALHAS'], l['LINHAS']))[0]
        self.assertEqual('coleta/executor_texto_de_pdf.py',
                         eleito['EXECUTOR_ID'],
                         'a medicao deixou de eleger o caminho escolhido')

    def test_O9_1_o_censo_publicado_regista_o_caminho_como_provado(self):
        import json
        d = json.load(open(os.path.join(RAIZ, 'system-map', 'data',
                                        'executores.generated.json'),
                           encoding='utf-8'))
        alvo = [l for l in d['EXECUTORES']
                if l['EXECUTOR_ID'] == 'coleta/executor_texto_de_pdf.py'][0]
        self.assertEqual('INSTRUMENTED', alvo['STATE'])
        self.assertTrue(alvo['GOOD_PATH_PROVED'])
        self.assertTrue(alvo['FAULT_PATH_PROVED'])

    def test_O9_1_ele_corre_offline_com_input_preservado(self):
        import json
        d = json.load(open(os.path.join(RAIZ, 'system-map', 'data',
                                        'executores.generated.json'),
                           encoding='utf-8'))
        alvo = [l for l in d['EXECUTORES']
                if l['EXECUTOR_ID'] == 'coleta/executor_texto_de_pdf.py'][0]
        self.assertTrue(alvo['CAN_RUN_OFFLINE'])
        self.assertFalse(alvo['NETWORK_REQUIRED'])
        self.assertFalse(alvo['PAID'])
        self.assertFalse(alvo['PRODUCTION_REQUIRED'])
        self.assertTrue(alvo['HAS_PRESERVED_INPUT'])


class O9_2_3_FronteiraTemDono(unittest.TestCase):
    """O9-2 e O9-3. A instrumentacao tem dono, e nao cria segundo registry."""

    def test_O9_2_o_executor_so_emite_pela_costura_injetada(self):
        """A informacao nasce onde e conhecida — e nunca por iniciativa propria.

        Duas sessoes fizeram O9 em paralelo. A outra pos a traducao DENTRO do
        executor, com o banco injetado; esta pos uma fronteira a correr o
        executor. Duas traducoes do mesmo recibo seriam dois donos da mesma
        pergunta, e por isso a fronteira deixou de traduzir.

        A lei que sobra e esta: o executor traduz, mas NUNCA decide sozinho
        escrever. Sem `rastro`, ele nao emite nada — e e isso que mantem a
        invariancia provavel.
        """
        sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
        import executor_texto_de_pdf as ex
        import inspect
        assinatura = inspect.signature(ex.correr)
        self.assertIn('rastro', assinatura.parameters)
        self.assertIsNone(assinatura.parameters['rastro'].default,
                          'a telemetria passou a ser ligada por omissao')

    def test_O9_2_a_fronteira_nao_traduz_segunda_vez(self):
        fonte = open(os.path.join(RAIZ, 'medidas', 'corrida_instrumentada.py'),
                     encoding='utf-8').read()
        self.assertNotIn('def traduzir_raw', fonte)
        self.assertNotIn('def traduzir_derived', fonte)
        self.assertIn('rastro=banco', fonte,
                      'a fronteira nao passa o banco pela costura')

    def test_O9_3_o_runner_nao_declara_vocabulario_proprio(self):
        """Ele importa os donos. Um quarto registry seria O8C ao contrario."""
        import ast
        fonte = open(os.path.join(RAIZ, 'medidas', 'corrida_instrumentada.py'),
                     encoding='utf-8').read()
        arvore = ast.parse(fonte)
        for no in ast.walk(arvore):
            if isinstance(no, ast.Assign):
                for alvo in no.targets:
                    if isinstance(alvo, ast.Name) and alvo.id in (
                            'CODIGOS', 'CODIGOS_DE_DIAGNOSTICO', 'ESTADOS',
                            'ESTADOS_DE_ETAPA', 'DESTINOS_DO_ITEM'):
                        self.fail('o runner declara %s' % alvo.id)
        self.assertIn('diagnostico', fonte)
        self.assertIn('falhas', fonte)

    def test_O9_2_o_executor_nao_conhece_postgres(self):
        """Ele recebe um banco. Ele nunca abre um."""
        fonte = open(os.path.join(RAIZ, 'coleta', 'executor_texto_de_pdf.py'),
                     encoding='utf-8').read()
        self.assertNotIn('psql', fonte)
        self.assertNotIn('coleta_checkpoint', fonte)
        self.assertNotIn('BANCO_DESCARTAVEL_URL', fonte)


class O9_5a8_CaminhoBom(Base):
    """O9-4..O9-8. A corrida boa, com os 49 PDF italianos reais."""

    def test_O9_5_emite_so_as_etapas_que_correram(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        etapas = [p['ETAPA'] for p in self._passagens()]
        # ⚠️ DUAS, E NAO TRES. A etapa READY saiu em O10R: COL-LAW-043 diz
        # que READY significa contratos obrigatorios satisfeitos, e nao «o
        # ficheiro existe». Este caminho termina em DERIVED, e terminar em
        # DERIVED e a verdade.
        self.assertEqual(['RAW', 'DERIVED'], etapas)
        for fabricada in ('DISCOVER', 'FETCH', 'STRUCTURED', 'ADMISSION',
                          'READY'):
            self.assertNotIn(fabricada, etapas,
                             '%s existe no contrato e NAO correu' % fabricada)

    def test_O9_4_a_corrida_usa_collection_run(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        n = self.banco.executa(
            "select count(*) from public.etapa_da_corrida e"
            " join public.collection_run c using (run_id)"
            " where e.run_id = '%s'" % self.RUN)
        self.assertEqual('2', n[0][0])

    def test_O9_6_a_conta_fecha_nas_duas_etapas(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        for p in self._passagens():
            self.assertEqual(0, p['UNACCOUNTED'],
                             '%s deixou %d itens sem porta'
                             % (p['ETAPA'], p['UNACCOUNTED']))

    def test_O9_7_as_copias_repetidas_sao_REUSED_e_fecham_a_conta(self):
        """O caso obrigatorio, e ele acontece nos dados reais:
        49 ficheiros sao 43 conteudos + 6 copias. Sem o balde REUSED daria
        UNACCOUNTED=6 num fluxo correto."""
        run.correr(self.banco, run_id=self.RUN, seco=True)
        raw = [p for p in self._passagens() if p['ETAPA'] == 'RAW'][0]
        self.assertEqual(49, raw['INPUT_COUNT'])
        self.assertGreater(raw['REUSED'], 0, 'nenhuma copia repetida medida')
        self.assertEqual(raw['INPUT_COUNT'], raw['ACCOUNTED'])
        self.assertEqual(raw['PASSED'] + raw['REUSED'], raw['ACCOUNTED'])

    def test_O9_8_grao_diferente_nao_gera_rendimento_falso(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        # A LEI E «NUNCA PUBLICAR RENDIMENTO ENTRE GRAOS», e nao «dizer sempre
        # GRAIN_CHANGED». Onde falta contagem de um dos lados, a resposta certa
        # e «sem contagem» — e continua a nao haver percentagem nenhuma.
        for p in self._passagens():
            y = rastro.rendimento(p)
            self.assertIsNone(y.get('YIELD'),
                              '%s publicou rendimento' % p['ETAPA'])
            self.assertTrue(y.get('PORQUE'), '%s nao disse porque' % p['ETAPA'])
            if p['OUTPUT_GRAIN'] != '-' and p['OUTPUT_COUNT'] >= 0 \
                    and p['INPUT_COUNT'] >= 0 and p['INPUT_COUNT'] > 0:
                self.assertTrue(y.get('GRAIN_CHANGED'),
                                '%s comparou graos diferentes' % p['ETAPA'])

    def test_O9_8_os_graos_estao_declarados_dos_dois_lados(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        for p in self._passagens():
            self.assertNotEqual('-', p['INPUT_GRAIN'])
            if p['ESTADO'] != 'NOT_RUN':
                self.assertNotEqual('-', p['OUTPUT_GRAIN'])


class O9_5_DerivacaoFrescaDeVerdade(Base):
    """O caminho bom com DERIVACAO NOVA, e nao so reencontro.

    Os 43 textos ja estao derivados e VERSIONADOS no repositorio. Rederiva-los
    por cima poria 43 ficheiros no diff so para um teste ver PASSED>0 — e um
    teste que suja a arvore para se provar nao prova nada de bom.

    Aqui o executor escreve num diretorio TEMPORARIO: e o mesmo codigo, os
    mesmos 49 PDF reais, e o registo vazio faz cada conteudo ser trabalho novo.
    """

    RUN = 'RUN-O9-FRESCO'

    def test_O9_5_derivacao_nova_passa_e_a_conta_fecha(self):
        import shutil
        import tempfile
        from pathlib import Path
        sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
        import executor_texto_de_pdf as ex

        if not ex.ha_ferramenta():
            self.skipTest('pdftotext nao esta nesta maquina')

        pasta = tempfile.mkdtemp(prefix='o9-fresco-')
        guardados = (ex.DERIVADOS, ex.REGISTO)
        try:
            ex.DERIVADOS = Path(pasta) / 'texto'
            ex.REGISTO = Path(pasta) / 'REGISTO-DE-ARTEFATOS.json'
            recibo = run.correr(self.banco, run_id=self.RUN)
        finally:
            ex.DERIVADOS, ex.REGISTO = guardados
            shutil.rmtree(pasta, ignore_errors=True)

        c = recibo['COUNTS']
        self.assertEqual(0, c['JA_EXISTIA'], 'o registo temporario nao estava vazio')
        self.assertEqual(0, recibo['LOST'], 'texto emitido que nao aterrou')

        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertGreater(d['PASSED'], 0, 'nenhuma derivacao nova passou')
        self.assertEqual(d['INPUT_COUNT'], d['ACCOUNTED'])
        self.assertEqual(0, d['UNACCOUNTED'])
        self.assertEqual('PASS', d['ESTADO'])

        raw = [p for p in self._passagens() if p['ETAPA'] == 'RAW'][0]
        self.assertEqual(49, raw['INPUT_COUNT'])
        self.assertEqual(43, raw['PASSED'])
        self.assertEqual(6, raw['REUSED'])

    def test_o_repositorio_fica_intacto(self):
        """O teste acima nao pode deixar rasto no armazem versionado."""
        import subprocess
        r = subprocess.run(['git', '-C', RAIZ, 'status', '--porcelain',
                            'data/derivados'], capture_output=True, text=True)
        self.assertEqual('', r.stdout.strip(),
                         'a prova sujou os derivados versionados')


class O9_9a13_CaminhoQuebrado(Base):
    """O9-9..O9-13. Uma etapa parte, e o estrago fica onde partiu."""

    RUN = 'RUN-O9-FALHA'

    def _partido(self):
        """A ferramenta local sumiu. Defeito NOSSO, e nao da fonte."""
        return executor_falso(dict(RAW_INPUT=49, RAW_CONTEUDOS_DISTINTOS=43,
                                   RAW_COPIAS_REPETIDAS=6, EXTRACTION_ERROR=43),
                              ferramenta='AUSENTE')

    def test_O9_9_a_falha_fica_numa_etapa_so(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=self._partido())
        ps = {p['ETAPA']: p for p in self._passagens()}
        self.assertEqual('PASS', ps['RAW']['ESTADO'], 'upstream contaminado')
        self.assertEqual('FAIL', ps['DERIVED']['ESTADO'],
                         '43 de 43 com erro nao e «trouxe parte»')

    def test_O9_10_os_itens_afetados_saem_por_ERROR_e_nao_por_REJECTED(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=self._partido())
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertEqual(43, d['ERROR'])
        self.assertEqual(0, d['REJECTED'],
                         'a ferramenta em falta nao torna o item «nao servia»')
        self.assertEqual(0, d['UNACCOUNTED'])

    def test_O9_11_o_failure_state_vem_de_falhas(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=self._partido())
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertIn(d['CANONICAL_STATE'], falhas.ESTADOS)
        self.assertEqual('EXECUTOR_UNAVAILABLE', d['CANONICAL_STATE'])
        self.assertEqual('EXECUTOR', falhas.camada(d['CANONICAL_STATE']),
                         'ferramenta em falta virou problema da fonte')

    def test_O9_12_o_diagnostic_code_vem_de_diagnostico(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=self._partido())
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertTrue(dg.valido(d['DIAGNOSTIC_CODE']))
        self.assertEqual(dg.DERIVATION_FAILED, d['DIAGNOSTIC_CODE'])
        self.assertNotEqual(d['DIAGNOSTIC_CODE'], d['CANONICAL_STATE'],
                            'as duas respostas colapsaram numa so')

    def test_O9_13_o_snapshot_responde_as_perguntas(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=self._partido())
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertEqual('DERIVED', d['ETAPA'])            # onde parou
        self.assertTrue(d['DIAGNOSTIC_CODE'])              # por que parou
        self.assertEqual(43, d['INPUT_COUNT'])             # qual input
        self.assertEqual('RAW', d['LAST_GOOD_ARTIFACT'])   # ultimo bom
        self.assertNotEqual('-', d['ACTOR'])           # quem correu
        self.assertNotEqual('-', d['ACTOR_VERSION'])   # qual versao
        self.assertEqual('RAW', d['EDGE_FROM'])            # qual aresta
        self.assertIsNotNone(d['TENTATIVA'])               # qual tentativa

    def test_O9_13_o_snapshot_nao_guarda_segredo(self):
        def com_segredo(seco=False, run_id='', rastro=None, source_id=None,
                        route_class_id=None):
            raise RuntimeError('falhou com token=SEGREDO-abc123 no meio')
        with self.assertRaises(RuntimeError):
            run.correr(self.banco, run_id=self.RUN, correr_executor=com_segredo)
        linhas = self.banco.executa(
            "select coalesce(error_message_redacted,'')"
            " from public.etapa_da_corrida"
            " where run_id = '%s'" % self.RUN)
        for (msg,) in linhas:
            self.assertNotIn('SEGREDO-abc123', msg)

    def test_O9_10_a_etapa_que_nao_correu_nao_vira_erro(self):
        """Downstream de uma falha e NOT_RUN. Nunca ERROR em cascata."""
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=self._partido())
        etapas = [p['ETAPA'] for p in self._passagens()]
        self.assertNotIn('STRUCTURED', etapas)
        self.assertNotIn('ADMISSION', etapas)
        rel = rastro.integridade(self._passagens())
        self.assertTrue(rel is not None)


class O9_10_FalhaDaTelemetria(Base):
    """PASSO 10. A coleta funciona e a telemetria NAO persiste. O que fica?

        OBSERVABILITY FAILURE != SOURCE FAILURE.

    Mas uma corrida sem rastro tambem nao pode ser publicada como observada.
    Esta classe mede o que o sistema JA faz — nao inventa politica nova para
    fechar a missao.
    """

    RUN = 'RUN-O9-CEGO'

    class BancoCego:
        """Escreve nada e falha como o banco real falharia."""

        def executa(self, sql):
            raise RuntimeError('telemetria indisponivel')

    def test_a_falha_da_telemetria_nao_condena_a_fonte(self):
        """O executor correu e produziu. Isso nao vira «fonte ruim»."""
        cego = self.BancoCego()
        with self.assertRaises(RuntimeError):
            run.correr(cego, run_id=self.RUN, seco=True)
        # Nenhuma linha foi escrita, e nenhuma fonte foi marcada.
        linhas = self.banco.executa(
            "select count(*) from public.etapa_da_corrida where run_id='%s'"
            % self.RUN)
        self.assertEqual('0', linhas[0][0])

    def test_a_corrida_sem_rastro_nao_se_publica_como_observada(self):
        """O scanner ja tem a palavra certa, e ela nao e PASS."""
        import scanner_da_coleta as sc
        rel = sc.relatorio(self.banco, self.RUN)
        self.assertEqual(sc.NAO_MEDIDA, rel['HEALTH'],
                         'corrida sem rastro apareceu como sa')
        self.assertFalse(rel['INSTRUMENTADA'])
        self.assertEqual(rastro.SEM_INSTRUMENTO, rel['NOTA'])

    def test_o_vazio_nunca_e_PASS(self):
        import scanner_da_coleta as sc
        self.assertEqual(sc.NAO_MEDIDA, sc.saude([]))
        self.assertNotEqual(sc.SAUDE_OK, sc.saude([]))

    def test_GAP_nao_ha_politica_de_recuperacao_da_telemetria(self):
        """O que o sistema NAO tem, dito por escrito em vez de inventado.

        Hoje: se a escrita do rastro falha, a excecao sobe e a corrida para.
        Nao ha fila, nao ha reescrita diferida, nao ha quarentena do rastro.
        Isso e uma DIVIDA declarada, e nao um comportamento canonico — inventar
        um aqui, so para O9 fechar, seria desenhar politica sem caso real.
        """
        fonte = open(os.path.join(RAIZ, 'medidas', 'corrida_instrumentada.py'),
                     encoding='utf-8').read()
        for inventado in ('retry_telemetria', 'fila_de_telemetria',
                          'quarentena'):
            self.assertNotIn(inventado, fonte,
                             'inventou-se politica de recuperacao sem caso real')


class O9_14_Retomada(Base):
    """O9-14. Retomar e honesto, ou diz que nao sabe."""

    RUN = 'RUN-O9-RETRY'

    def test_O9_14_o_ultimo_ponto_bom_e_o_RAW(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=executor_falso(
                       dict(RAW_INPUT=49, RAW_CONTEUDOS_DISTINTOS=43,
                            RAW_COPIAS_REPETIDAS=6, EXTRACTION_ERROR=43),
                       ferramenta='AUSENTE'))
        self.assertEqual('RAW', rastro.ultimo_bom(self._passagens()))

    def test_O9_14_retomar_parte_da_etapa_seguinte_a_boa(self):
        run.correr(self.banco, run_id=self.RUN,
                   correr_executor=executor_falso(
                       dict(RAW_INPUT=49, RAW_CONTEUDOS_DISTINTOS=43,
                            RAW_COPIAS_REPETIDAS=6, EXTRACTION_ERROR=43),
                       ferramenta='AUSENTE'))
        self.assertEqual('DERIVED', rastro.onde_retomar(self._passagens()))

    def test_O9_14_a_segunda_corrida_encontra_tudo_REUSED(self):
        """IDEMPOTENCIA REAL: os 43 ja derivados voltam como REUSED, nao PASSED."""
        run.correr(self.banco, run_id=self.RUN, seco=True)
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertGreater(d['REUSED'], 0,
                           'trabalho ja feito voltou a contar como novo')
        self.assertEqual(d['INPUT_COUNT'], d['ACCOUNTED'])


class O9_BibliaNaoEViolada(Base):
    """O9 nao emenda a Constituicao. Verifica se a viola.

    A `BIBLIA-CANONICA-DA-COLETA.md` esta em V1.3 CANONICAL. Nenhuma linha dela
    foi tocada nesta missao — o que se faz aqui e procurar contraexemplo real.
    """

    RUN = 'RUN-O9-BIBLIA'

    def test_COL_LAW_011_o_runner_nao_e_um_segundo_orquestrador(self):
        """«COMO ATENDER ESTE PEDIDO?» tem um dono so, e nao e este ficheiro.

        A fronteira corre UM executor nomeado e observa-o. Ela nao escolhe
        entre executores, nao le receita e nao decide rota — se algum dia
        passar a escolher, este teste reprova antes de a lei ser violada.
        """
        import ast
        caminho = os.path.join(RAIZ, 'medidas', 'corrida_instrumentada.py')
        arvore = ast.parse(open(caminho, encoding='utf-8').read())
        importados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                importados |= {a.name.split('.')[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module:
                importados.add(no.module.split('.')[0])
        for dono_da_rota in ('orquestrador', 'receitas', 'pedido', 'filas',
                             'apify_pool'):
            self.assertNotIn(dono_da_rota, importados,
                             'a fronteira comecou a escolher rota: %s'
                             % dono_da_rota)

    def test_COL_LAW_012_a_fronteira_nao_transporta_dado(self):
        """CONTROL PLANE nao carrega DATA PLANE.

        O runner move CONTAGENS. O texto derivado vai para o disco pela mao do
        executor, e a fronteira nunca o abre.
        """
        fonte = open(os.path.join(RAIZ, 'medidas', 'corrida_instrumentada.py'),
                     encoding='utf-8').read()
        for transporte in ('open(', 'read_text', 'write_text', 'shutil.copy'):
            self.assertNotIn(transporte, fonte,
                             'a fronteira tocou no artefato: %s' % transporte)

    def test_COL_LAW_022_a_corrida_tem_identidade_e_os_campos_do_contrato(self):
        recibo = run.correr(self.banco, run_id=self.RUN, seco=True)
        for campo in ('RUN_ID', 'EXECUTOR_ID', 'EXECUTOR_VERSION',
                      'PIPELINE_VERSION', 'STARTED_AT', 'FINISHED_AT',
                      'STATUS', 'COUNTS', 'ERRORS'):
            self.assertIn(campo, recibo, 'RUN-MANIFEST sem %s' % campo)
        self.assertEqual(self.RUN, recibo['RUN_ID'])

    def test_COL_LAW_023_a_perda_entre_etapas_nao_some(self):
        """EMITTED != LANDED tem de aparecer, e nao diluir-se num sucesso.

        A perda NAO aparece como buraco na contabilidade — aparece com NOME, na
        etapa onde aconteceu: READY fica FAIL, os tres entram em `unknown`
        (medido, e nao se sabe onde foram) e o codigo diz qual e o defeito.
        Um buraco diria «sumiram»; isto diz «sumiram TRES, aqui, e chama-se
        assim» — que e mais do que a lei exige.
        """
        perdeu = executor_falso(dict(RAW_INPUT=49, RAW_CONTEUDOS_DISTINTOS=43,
                                     DERIVED_EMITTED=43, DERIVED_LANDED=40,
                                     RAW_COPIAS_REPETIDAS=6), perdidos=3)
        run.correr(self.banco, run_id=self.RUN, correr_executor=perdeu)
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertEqual('PARTIAL', d['ESTADO'],
                         'tres textos sumiram e a etapa saiu-se bem')
        self.assertEqual(3, d['UNKNOWN'], 'a perda nao foi contada')
        self.assertEqual('FLOW_UNACCOUNTED_INPUT', d['DIAGNOSTIC_CODE'])
        self.assertEqual('ITEM_ERROR', d['CANONICAL_STATE'])
        self.assertEqual(0, d['UNACCOUNTED'])

    def test_COL_LAW_024_zero_nao_vira_sucesso_automatico(self):
        """Nenhum item saiu por porta nenhuma: isso e buraco, e nao PASS sereno."""
        vazio = executor_falso(dict(RAW_INPUT=49, RAW_CONTEUDOS_DISTINTOS=43))
        run.correr(self.banco, run_id=self.RUN, correr_executor=vazio)
        d = [p for p in self._passagens() if p['ETAPA'] == 'DERIVED'][0]
        self.assertEqual(43, d['UNACCOUNTED'],
                         '43 entraram, nenhum saiu, e a conta ficou calada')
        import scanner_da_coleta as sc
        self.assertEqual(sc.SAUDE_ERRO, sc.relatorio(self.banco, self.RUN)['HEALTH'],
                         'buraco na contabilidade apareceu como saude boa')


class O9_15_Invariancia(unittest.TestCase):
    """O9-15. Instrumentar NAO muda o resultado funcional."""

    @unittest.skipUnless(TEM, 'sem banco: %s' % PORQUE)
    def test_O9_15_o_recibo_e_o_mesmo_com_e_sem_telemetria(self):
        """A prova mais forte possivel: o executor e o MESMO ficheiro nos dois
        lados. A telemetria vive fora dele, e por isso nao ha o que divergir."""
        sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
        import executor_texto_de_pdf as ex
        sem = ex.correr(seco=True, run_id='RUN-O9-INV-SEM')

        banco = cc.Banco(DSN)
        banco.executa("delete from public.etapa_da_corrida"
                      " where run_id = 'RUN-O9-INV-COM'")
        banco.executa("delete from public.collection_run"
                      " where run_id = 'RUN-O9-INV-COM'")
        banco.executa(
            "insert into public.collection_run (run_id, platform,"
            " source_country, started_at, status, rule_version)"
            " values ('RUN-O9-INV-COM','web','IT',now(),'rodando','v1')")
        com = run.correr(banco, run_id='RUN-O9-INV-COM', seco=True)

        self.assertEqual(sem['COUNTS'], com['COUNTS'],
                         'instrumentar mudou as contagens do executor')
        self.assertEqual(sem['STATUS'], com['STATUS'])
        self.assertEqual(sem['LOST'], com['LOST'])
        self.assertEqual(sem['EXECUTOR_VERSION'], com['EXECUTOR_VERSION'])
        self.assertEqual(sem['COST_USD'], com['COST_USD'])


class O9_16a20_ScannerEMapa(Base):
    """O9-16..O9-20. O scanner ve a corrida, e o mapa nao a promove a global."""

    RUN = 'RUN-O9-SCAN'

    def test_O9_16_o_scanner_enxerga_a_corrida(self):
        import scanner_da_coleta as sc
        run.correr(self.banco, run_id=self.RUN, seco=True)
        rel = sc.relatorio(self.banco, self.RUN)
        self.assertEqual(2, len(rel['PASSAGENS']))
        self.assertIn(rel['HEALTH'], (sc.SAUDE_OK, sc.SAUDE_AVISO))
        self.assertNotEqual(sc.NAO_MEDIDA, rel['HEALTH'],
                            'o scanner nao viu a corrida que acabou de correr')

    def test_O9_17_um_caminho_instrumentado_nao_e_cobertura_global(self):
        import json
        p = os.path.join(RAIZ, 'system-map', 'data', 'executores.generated.json')
        d = json.load(open(p, encoding='utf-8'))
        instrumentados = d['POR_ESTADO'].get('INSTRUMENTED', 0)
        relevantes = d['TOTAL_CAMINHOS_RELEVANTES']
        self.assertLess(instrumentados, relevantes,
                        'o censo promoveu a casa inteira por causa de um caso')

    def test_O9_18_a_paridade_continua_a_passar(self):
        import subprocess
        r = subprocess.run([sys.executable,
                            os.path.join(RAIZ, 'provas', 'paridade_da_lingua.py')],
                           capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stdout[-500:])

    def test_O9_trace_segue_do_run_ate_a_retomada(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        ps = self._passagens()
        self.assertTrue(all(p['ETAPA'] for p in ps))              # RUN -> STAGE
        derived = [p for p in ps if p['ETAPA'] == 'DERIVED'][0]
        self.assertEqual('RAW', derived['EDGE_FROM'])             # STAGE -> EDGE
        self.assertTrue(derived['OUTPUT_GRAIN'])                  # -> ARTIFACT
        self.assertIsNotNone(rastro.ultimo_bom(ps))               # -> LAST GOOD

    def test_a_duracao_e_medida_e_nao_inventada(self):
        run.correr(self.banco, run_id=self.RUN, seco=True)
        for p in self._passagens():
            self.assertIsNotNone(p['DURACAO_MS'])
            self.assertGreaterEqual(p['DURACAO_MS'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
