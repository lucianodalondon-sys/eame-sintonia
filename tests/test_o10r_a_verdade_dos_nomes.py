#!/usr/bin/env python3
"""R1–R14 — os nomes deixam de prometer mais do que provam.

O9 provou que o instrumento funciona. Esta suite recusa quatro confusoes que
sobreviveram a essa prova, e que davam a uma medida honesta um nome grande
demais:

    ESTRADA HISTORICA   nao e estrada oficial      (LEGACY != FORWARD)
    TEXTO GUARDADO      nao e READY                (COL-LAW-043)
    54 CAMINHOS         nao sao 54 motores         (PATH != EXECUTOR)
    SENSOR EXISTE       nao e rota observavel      (INSTRUMENT != ROUTE)

E uma quinta, que era a mais silenciosa: a mesma corrida tinha uma identidade
quando corria bem e outra quando o executor morria cedo.
"""
import ast
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                      # noqa: E402,F401
import corrida_instrumentada as run  # noqa: E402

EXECUTOR = os.path.join(RAIZ, 'coleta', 'executor_texto_de_pdf.py')
CENSO = os.path.join(RAIZ, 'system-map', 'data', 'executores.generated.json')
LEDGER = os.path.join(RAIZ, 'system-map', 'data', 'provas-de-execucao.json')
BIBLIA = os.path.join(RAIZ, 'BIBLIA-CANONICA-DA-COLETA.md')


def _censo():
    return json.load(open(CENSO, encoding='utf-8'))


def _ledger():
    return json.load(open(LEDGER, encoding='utf-8'))


def _fonte(p):
    return open(p, encoding='utf-8').read()


def _codigo(p):
    """A fonte sem comentarios e sem docstrings.

    ⚠️ Um teste que proibisse o nome antigo em QUALQUER sitio proibiria tambem
    o comentario que explica por que ele saiu — e essa nota e o que impede
    alguem de o repor amanha sem saber o que se pagou por ele.

        UMA FRASE SOBRE O DEFEITO NAO E O DEFEITO.
    """
    import re as _re
    fonte = _fonte(p)
    arvore = ast.parse(fonte)
    docs = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                           ast.ClassDef)):
            d = ast.get_docstring(no, clean=False)
            if d:
                docs.add(d)
    texto = '\n'.join(_re.sub(r'#.*$', '', l) for l in fonte.split('\n'))
    for d in docs:
        texto = texto.replace(d, ' ')
    return texto


def _corpo_de(caminho, nome):
    """O codigo de UMA funcao, sem depender de o resto do ficheiro."""
    arvore = ast.parse(_fonte(caminho))
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return ast.dump(no)
    raise AssertionError('funcao %s nao existe em %s' % (nome, caminho))


class R1_R2_LegacyNaoEForward(unittest.TestCase):
    """R1 e R2. Um replay do historico nao e o fluxo forward canonico."""

    def test_R1_o_executor_declara_os_dois_modos_e_eles_sao_distintos(self):
        fonte = _fonte(EXECUTOR)
        self.assertIn('LEGADO', fonte)
        self.assertIn('FORWARD', fonte)
        self.assertIn('def correr(', fonte)
        self.assertIn('def derivar_um(', fonte)

    def test_R1_a_telemetria_esta_no_legado_e_nao_no_forward(self):
        """MEDIDO POR AST, e nao por leitura: `derivar_um` nao emite nada."""
        forward = _corpo_de(EXECUTOR, 'derivar_um')
        self.assertNotIn('emitir_rastro', forward,
                         'o forward passou a emitir e o ledger nao sabe')
        self.assertNotIn('registrar', forward)
        legado = _corpo_de(EXECUTOR, 'correr')
        self.assertIn('emitir_rastro', legado,
                      'o legado deixou de emitir')

    def test_R2_o_ledger_diz_qual_modo_foi_provado(self):
        """⚠️ ESTE TESTE MEDE, E DEIXOU DE CONGELAR.

        A primeira versao exigia `FORWARD_INSTRUMENTED is False`. Era a medicao
        daquele minuto escrita como se fosse lei — e no minuto em que o forward
        passou a emitir (`coleta/derivacao_forward.py`, em O9R), o teste
        reprovou o CONSERTO em vez do defeito.

            UM TESTE QUE FIXA O NUMERO DE HOJE PROIBE O DE AMANHA.

        O que ele tem de exigir e a CORRESPONDENCIA: o ledger diz `false` e o
        forward esta calado, ou diz `true` e aponta uma prova que existe. As
        duas afirmacoes continuam separadas — LEGACY prova o instrumento,
        FORWARD prova a estrada.
        """
        p = _ledger()['PROVADOS']['coleta/executor_texto_de_pdf.py']
        self.assertEqual('LEGACY_REPLAY', p['EXECUTION_MODE'])
        if p['FORWARD_INSTRUMENTED']:
            fw = p.get('FORWARD') or {}
            self.assertTrue(fw.get('FRONTEIRA'),
                            'diz FORWARD_INSTRUMENTED e nao diz por quem')
            for chave in ('FRONTEIRA', 'PROVA'):
                self.assertTrue(
                    os.path.exists(os.path.join(RAIZ, fw[chave])),
                    '%s aponta para um ficheiro que nao existe: %s'
                    % (chave, fw[chave]))
            self.assertFalse(p.get('PORQUE_FORWARD_NAO_ESTA'),
                             'diz que esta instrumentado E explica por que nao')
        else:
            self.assertTrue(p['PORQUE_FORWARD_NAO_ESTA'])

    def test_R2_o_ledger_nao_chama_legacy_de_forward(self):
        texto = json.dumps(_ledger(), ensure_ascii=False)
        self.assertNotIn('"FORWARD_PROVED": true', texto)
        self.assertIn('LEGACY_NAO_E_FORWARD', _ledger())


class R3_ReadyTemLei(unittest.TestCase):
    """R3. DERIVED persistido nao vira READY."""

    def test_R3_o_executor_nao_emite_READY(self):
        fonte = _fonte(EXECUTOR)
        self.assertNotIn('etapa="READY"', fonte,
                         'READY voltou sem a lei de READY')
        self.assertNotIn("etapa='READY'", fonte)

    def test_R3_e_nao_se_inventou_uma_etapa_para_a_substituir(self):
        """A informacao cabe em DERIVED. Uma etapa nova seria contornar a lei."""
        fonte = _fonte(EXECUTOR)
        for fabricada in ('DERIVED_PERSISTED', 'PERSISTED', 'LANDED_STAGE'):
            self.assertNotIn('etapa="%s"' % fabricada, fonte)

    def test_R3_a_lei_canonica_de_READY_exige_admissao(self):
        """COL-LAW-043 — e ela e a razao, nao uma preferencia minha."""
        biblia = _fonte(BIBLIA)
        self.assertIn('COL-LAW-043', biblia)
        self.assertIn('ADMITIDO_POR', biblia)
        # e COL-LAW-044 separa os estados logicos
        self.assertIn('RAW · DERIVED · ADMITTED · READY', biblia)

    def test_R3_o_caminho_termina_em_DERIVED(self):
        p = _ledger()['PROVADOS']['coleta/executor_texto_de_pdf.py']
        self.assertEqual(['RAW', 'DERIVED'], p['ETAPAS_OBSERVADAS'])
        self.assertNotIn('READY', p['ETAPAS_OBSERVADAS'])
        self.assertNotIn('ADMISSION', p['ETAPAS_OBSERVADAS'])

    def test_R3_o_que_aterrou_continua_contado(self):
        """Remover a etapa nao pode apagar a medida — ela mudou de sitio."""
        fonte = _fonte(EXECUTOR)
        self.assertIn('passed=conta["DERIVED_LANDED"]', fonte)
        self.assertIn('unknown=conta["RAW_UNKNOWN"] + perdidos', fonte)


class R3_ProvaQueMorde(unittest.TestCase):
    """A prova obrigatoria: DERIVED sem ADMISSION nao produz READY PASS.

    ⚠️ E ela e feita CONTRA O BANCO, e nao por leitura do ficheiro. Um teste
    que so procurasse a string `READY` no codigo passaria no dia em que alguem
    a escrevesse por outra via. Aqui corre-se o caminho de verdade e olha-se o
    que ficou escrito.
    """

    @classmethod
    def setUpClass(cls):
        dsn = os.environ.get('BANCO_DESCARTAVEL_URL', '')
        if not dsn:
            raise unittest.SkipTest('sem BANCO_DESCARTAVEL_URL')
        import coleta_checkpoint as cc
        try:
            cls.banco = cc.Banco(dsn)
            cls.banco.executa('select 1 from public.etapa_da_corrida limit 1')
        except Exception as e:
            raise unittest.SkipTest('sem a 024 no banco: %s' % str(e)[:80])

    def setUp(self):
        self.RUN = 'RUN-O10R-1'
        b = self.banco
        b.executa("delete from public.etapa_da_corrida where run_id like 'RUN-O10R%'")
        b.executa("delete from public.collection_run where run_id like 'RUN-O10R%'")
        b.executa("insert into public.collection_run (run_id, platform,"
                  " source_country, started_at, status, rule_version)"
                  " values ('%s','web','IT',now(),'rodando','v1')" % self.RUN)

    def test_correr_o_caminho_real_nao_escreve_nenhum_READY(self):
        import rastro_da_coleta as rastro
        run.correr(self.banco, run_id=self.RUN, seco=True)
        etapas = [p['ETAPA'] for p in rastro.passagens(self.banco,
                                                       run_id=self.RUN)]
        self.assertNotIn('READY', etapas,
                         'um texto guardado voltou a chamar-se READY')
        self.assertNotIn('ADMISSION', etapas)
        self.assertEqual('DERIVED', etapas[-1],
                         'o caminho deixou de terminar em DERIVED')

    def test_o_banco_nao_tem_READY_em_PASS_sem_ADMISSION_antes(self):
        """A pergunta na lingua do banco: alguma corrida diz READY=PASS sem
        ter uma ADMISSION que a preceda?"""
        run.correr(self.banco, run_id=self.RUN, seco=True)
        linhas = self.banco.executa(
            "select count(*) from public.etapa_da_corrida r"
            " where r.etapa = 'READY' and r.estado = 'PASS'"
            " and not exists (select 1 from public.etapa_da_corrida a"
            "                 where a.run_id = r.run_id"
            "                   and a.etapa = 'ADMISSION'"
            "                   and a.estado = 'PASS')")
        self.assertEqual('0', linhas[0][0],
                         'ha READY PASS sem ADMISSION PASS na mesma corrida')

    def test_a_identidade_e_a_mesma_quando_o_executor_morre_cedo(self):
        """R4 contra o banco: a morte precoce escreve a MESMA fonte."""
        import rastro_da_coleta as rastro

        def morre(seco=False, run_id='', rastro=None, source_id=None,
                  route_class_id=None):
            raise RuntimeError('morri antes de emitir')

        run.correr(self.banco, run_id=self.RUN, seco=True)
        boas = rastro.passagens(self.banco, run_id=self.RUN)
        with self.assertRaises(RuntimeError):
            run.correr(self.banco, run_id=self.RUN, correr_executor=morre)
        todas = rastro.passagens(self.banco, run_id=self.RUN)
        self.assertGreater(len(todas), len(boas),
                           'a morte nao deixou linha — a escrita colidiu e o '
                           'erro do banco passou por erro do executor')
        morta = [p for p in todas if p['ESTADO'] == 'FAIL'][0]
        self.assertEqual('DERIVED', morta['ETAPA'])
        self.assertTrue(morta['DIAGNOSTIC_CODE'])
        vistas = self.banco.executa(
            "select distinct coalesce(source_id,'<NULL>'),"
            " coalesce(route_class_id,'<NULL>')"
            " from public.etapa_da_corrida where run_id = '%s'" % self.RUN)
        self.assertEqual([['<NULL>', '<NULL>']],
                         [list(v) for v in vistas],
                         'a corrida tem mais de uma identidade: %s' % vistas)


class R4_R5_R6_Identidade(unittest.TestCase):
    """R4, R5, R6. A identidade nao muda com o sitio onde se morre."""

    def test_R4_os_dois_lados_declaram_a_mesma_identidade(self):
        self.assertIsNone(run.SOURCE_ID)
        self.assertIsNone(run.ROUTE_CLASS_ID)
        codigo = _codigo(EXECUTOR)
        self.assertNotIn('IT-PDF-ITALIANOS', codigo,
                         'o executor voltou a inventar um source_id')

    def test_R4_nenhum_dos_nomes_inventados_sobreviveu(self):
        for ficheiro in (EXECUTOR,
                         os.path.join(RAIZ, 'medidas',
                                      'corrida_instrumentada.py')):
            codigo = _codigo(ficheiro)
            for inventado in ('IT-CORPUS-PDF', 'IT-PDF-ITALIANOS'):
                self.assertNotIn(inventado, codigo, ficheiro)

    def test_R5_a_identidade_vem_de_fora_e_nao_nasce_no_executor(self):
        import inspect
        sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
        import executor_texto_de_pdf as ex
        for fn in (ex.correr, ex.emitir_rastro):
            par = inspect.signature(fn).parameters
            self.assertIn('source_id', par, fn.__name__)
            self.assertIn('route_class_id', par, fn.__name__)
            self.assertIsNone(par['source_id'].default,
                              '%s tem source_id por omissao' % fn.__name__)

    def test_R5_o_ledger_explica_por_que_a_fonte_e_nula(self):
        p = _ledger()['PROVADOS']['coleta/executor_texto_de_pdf.py']
        self.assertIsNone(p['SOURCE_ID'])
        self.assertIn('OITO', p['PORQUE_IDENTIDADE_NULA'])

    def test_R6_a_rota_tambem_fica_UNKNOWN_e_com_razao_escrita(self):
        p = _ledger()['PROVADOS']['coleta/executor_texto_de_pdf.py']
        self.assertIsNone(p['ROUTE_CLASS_ID'])
        self.assertIn('route_class', p['PORQUE_IDENTIDADE_NULA'])

    def test_R6_o_banco_aceita_nulo_nos_dois(self):
        """A representacao honesta ja existia — era so nao a contornar."""
        sql = _fonte(os.path.join(RAIZ, 'supabase', 'migrations',
                                  '024_a_corrida_conta_o_que_passou.sql'))
        trecho = sql[sql.index('create table public.etapa_da_corrida'):]
        trecho = trecho[:trecho.index(');')]
        for linha in trecho.splitlines():
            nu = linha.strip()
            if nu.startswith('source_id') or nu.startswith('route_class_id'):
                self.assertNotIn('not null', nu.lower(), nu)


class R7_R8_ODenominador(unittest.TestCase):
    """R7 e R8. Os caminhos varridos nao sao os motores provados."""

    def test_R7_nao_se_publica_executores_provados_sem_prova(self):
        """⚠️ MEDE A RELACAO, E NAO O NUMERO DE HOJE.

        A primeira versao exigia `TOTAL_RELEVANT_PATHS == 54`. Bastou esta
        missao acrescentar UM ficheiro a `coleta/` para o teste reprovar — e
        reprovar o acrescento, nao um defeito.

            UM TESTE QUE FIXA O NUMERO DE HOJE PROIBE O DE AMANHA,
            E O DEFEITO QUE ELE APANHA E O CRESCIMENTO.

        O que R7 existe para impedir e outra coisa, e ela nao tem numero:
        publicar «executores provados» sem que cada um aponte uma prova. Isso
        continua exigido, e agora exigido de todos.
        """
        d = _censo()['DENOMINADORES']
        self.assertGreater(d['TOTAL_RELEVANT_PATHS'], 0)
        self.assertLess(d['TOTAL_EXECUTORS_PROVEN'], d['TOTAL_RELEVANT_PATHS'])
        # Cada provado tem de estar no ledger, com prova apontada.
        ledger = _ledger()['PROVADOS']
        provados = [l for l in _censo()['EXECUTORES']
                    if l['STATE'] == 'INSTRUMENTED']
        self.assertEqual(d['TOTAL_EXECUTORS_PROVEN'], len(provados))
        for l in provados:
            self.assertIn(l['EXECUTOR_ID'], ledger)
            self.assertTrue(ledger[l['EXECUTOR_ID']].get('PROVA'),
                            '%s publicado como provado sem prova apontada'
                            % l['EXECUTOR_ID'])

    def test_R7_o_artefato_nao_tem_campo_TOTAL_EXECUTORS(self):
        """O nome que daria autoridade ao denominador errado nao existe."""
        texto = json.dumps(_censo(), ensure_ascii=False)
        self.assertNotIn('"TOTAL_EXECUTORS"', texto)

    def test_R8_o_denominador_vem_separado_e_soma_com_UNKNOWN(self):
        d = _censo()['DENOMINADORES']
        for campo in ('TOTAL_FILES_SCANNED', 'TOTAL_RELEVANT_PATHS',
                      'TOTAL_EXECUTORS_PROVEN', 'TOTAL_ORCHESTRATORS',
                      'TOTAL_UNKNOWN'):
            self.assertIn(campo, d)
        self.assertGreater(d['TOTAL_UNKNOWN'], 0,
                           'nenhum caminho ficou UNKNOWN — a tipagem esta a '
                           'adivinhar em vez de medir')

    def test_R8_todo_caminho_relevante_tem_papel(self):
        for l in _censo()['EXECUTORES']:
            if l['STATE'] == 'NOT_APPLICABLE':
                continue
            self.assertTrue(l['PAPEIS'], l['EXECUTOR_ID'])

    def test_R8_uma_peca_pode_ter_mais_de_um_papel(self):
        """Nao se forca exclusividade — mas cada papel tem evidencia propria."""
        multi = [l for l in _censo()['EXECUTORES'] if len(l['PAPEIS']) > 1]
        self.assertTrue(multi, 'a tipagem forcou papel unico')


class R9_R10_DuasPerguntas(unittest.TestCase):
    """R9 e R10. Cada nome mede uma coisa so."""

    def test_R9_o_instrumento_mede_o_instrumento(self):
        """⚠️ O QUE R9 EXIGE E QUE O BLOCO NAO SE ARROGUE A OUTRA PERGUNTA.

        A primeira versao procurava a palavra `LEGACY_REPLAY` na ressalva. Era
        a maneira de dizer «este bloco nao mede o fluxo forward» no dia em que
        a unica prova era um replay. Em O9R o forward passou a ter prova
        propria e o campo mudou de sitio: `CANONICAL_FORWARD_PATH`, ao lado.
        Procurar a palavra antiga passaria a reprovar a separacao que R9 pediu.

        O que continua exigido — e agora com mais forca — e que o bloco do
        INSTRUMENTO nao afirme nada sobre a estrada, nem sobre a rota da M2.
        """
        m2 = _censo()['M2']
        i = m2['TELEMETRY_INFRASTRUCTURE']
        self.assertEqual('YES', i['TELEMETRY_INFRASTRUCTURE_PROVED'])
        self.assertNotIn('FORWARD_PROVED', i)
        self.assertNotIn('M2_ROUTE_OBSERVABILITY_READY', i)
        for palavra in ('rota da M2', 'cobertura'):
            self.assertIn(palavra, i['O_QUE_NAO_MEDE'])
        # A pergunta do forward existe, e vive num campo SEPARADO.
        fw = m2['CANONICAL_FORWARD_PATH']
        self.assertIn('CANONICAL_FORWARD_PATH_PROVED', fw)
        self.assertNotIn('TELEMETRY_INFRASTRUCTURE_PROVED', fw)

    def test_R9_o_forward_mede_o_forward_e_aponta_prova(self):
        """LEGACY_REPLAY_INSTRUMENTED != CANONICAL_FORWARD_INSTRUMENTED."""
        fw = _censo()['M2']['CANONICAL_FORWARD_PATH']
        self.assertIn('LEGACY_REPLAY_INSTRUMENTED', fw['A_LEI'])
        if fw['CANONICAL_FORWARD_PATH_PROVED'] == 'YES':
            self.assertTrue(fw['FRONTEIRAS'])
            for caminho in fw['FRONTEIRAS'] + fw['PROVAS']:
                self.assertTrue(os.path.exists(os.path.join(RAIZ, caminho)),
                                caminho)
        else:
            self.assertEqual([], fw['QUAIS'])

    def test_R10_a_rota_mede_a_rota(self):
        r = _censo()['M2']['M2_ROUTE']
        self.assertEqual('NO', r['M2_ROUTE_OBSERVABILITY_READY'])
        self.assertEqual(['STRUCTURED', 'ADMISSION'],
                         r['ETAPAS_DA_ROTA_M2_NUNCA_OBSERVADAS'])

    def test_R9_R10_o_nome_antigo_que_juntava_as_duas_sumiu(self):
        texto = json.dumps(_censo(), ensure_ascii=False)
        self.assertNotIn('MINIMAL_OPERATIONAL_OBSERVABILITY_FOR_M2', texto,
                         'o nome que respondia duas perguntas voltou')

    def test_o_portao_da_M2_e_nascer_instrumentada_e_nao_ja_estar(self):
        r = _censo()['M2']['M2_ROUTE']
        self.assertEqual('YES', r['M2_CONSTRUCTION_CAN_BEGIN'])
        self.assertIs(True, r['M2_CANNOT_CLOSE_UNTIL_INSTRUMENTED'])
        self.assertIn('nasce', r['O_PORTAO_CORRETO'])

    def test_as_duas_respostas_nao_sao_iguais(self):
        """Se voltarem a ser iguais, ou uma delas mudou de sentido, ou o nome
        voltou a responder as duas perguntas."""
        m = _censo()['M2']
        self.assertNotEqual(
            m['TELEMETRY_INFRASTRUCTURE']['TELEMETRY_INFRASTRUCTURE_PROVED'],
            m['M2_ROUTE']['M2_ROUTE_OBSERVABILITY_READY'])


class R11_R12_R13_AsPortasQueJaExistiam(unittest.TestCase):
    """R11, R12, R13. O que O8C e O9 fecharam continua fechado."""

    def test_R11_paridade_da_lingua_continua_a_passar(self):
        import subprocess
        r = subprocess.run([sys.executable,
                            os.path.join(RAIZ, 'provas', 'paridade_da_lingua.py')],
                           capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stdout[-400:])

    def test_R13_o_censo_e_derivado_e_nao_digitado(self):
        """Nenhum numero do censo pode ser escrito a mao no artefato."""
        self.assertIn('MEDIDO_POR', _censo()['PROVENANCE'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
