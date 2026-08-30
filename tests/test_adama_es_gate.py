"""O portao do handoff ADAMA Espanha continua sendo um portao.

Um portao que aprova tudo nao e portao. Estes testes guardam duas coisas:
que o veredito continua vindo de medicao (e nao de opiniao), e que os
defeitos ja encontrados nao somem do artefato sem alguem consertar a origem.

Nenhum teste aqui importa dado. O ensaio contra Postgres real vive em
supabase/ensaios/ e roda no workflow adama-es-gate.
"""
import json
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMOSTRAS = os.path.join(RAIZ, 'data', 'samples')
PORTAO = os.path.join(AMOSTRAS, 'ADAMA-ES-HANDOFF-GATE-V1.json')


def carrega():
    with open(PORTAO, encoding='utf-8') as f:
        return json.load(f)


class TestOPortaoMediu(unittest.TestCase):

    def setUp(self):
        self.d = carrega()

    def test_o_handoff_esta_identificado_com_ref_e_head(self):
        a = self.d['A_LOCALIZACAO']
        self.assertEqual('origin/claude/adama-es-local-browser', a['REF'])
        self.assertRegex(a['HEAD'], r'^[0-9a-f]{40}$')
        self.assertTrue(a['PUSHED'])
        self.assertGreater(len(a['ARQUIVOS']), 30)

    def test_o_handoff_continua_nao_mesclado(self):
        """Esta rodada e de GATE. Se aparecer mesclado, alguem importou."""
        self.assertFalse(self.d['A_LOCALIZACAO']['MESCLADO_NA_PRINCIPAL'])
        self.assertTrue(self.d['NAO_IMPORTOU_NADA'])

    def test_os_tres_estados_de_portfolio_e_so_tres(self):
        p = self.d['PORTFOLIO_LOCAL']
        estados = {x['ESTADO'] for x in p['LINHAS']}
        self.assertLessEqual(estados, {'LOCAL_REGISTERED',
                                       'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED',
                                       'NOT_KNOWN'})
        self.assertEqual(len(p['LINHAS']),
                         p['LOCAL_REGISTERED']
                         + p['LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED']
                         + p['NOT_KNOWN'])

    def test_ausencia_no_registro_nunca_vira_nao_registrado(self):
        """NOT_FOUND != DOES NOT EXIST, tambem aqui."""
        p = self.d['PORTFOLIO_LOCAL']
        self.assertIn('AUSENTE_MEDIDO', p['PORQUE_NENHUM_E_NAO_REGISTRADO'])
        for x in p['LINHAS']:
            self.assertNotIn('NAO_REGISTRADO', x['ESTADO'])

    def test_o_casamento_por_nome_fica_visivel(self):
        """3 produtos entram por nome+composicao, e isso nao pode sumir."""
        p = self.d['PORTFOLIO_LOCAL']
        bases = p['POR_BASE_DE_CASAMENTO']
        self.assertIn('NAME_AND_COMPOSITION', bases)
        for x in p['LINHAS']:
            if x['ESTADO'] == 'LOCAL_REGISTERED':
                self.assertIn(x['MATCH_BASIS'],
                              ('REGISTRATION_NUMBER', 'NAME_AND_COMPOSITION'))


class TestOsDefeitosContinuamNomeados(unittest.TestCase):
    """Se um defeito sumir daqui, ou a origem foi consertada — e o teste tem
    de ser atualizado de proposito — ou alguem apagou o achado."""

    def setUp(self):
        self.rt = {x['ID']: x for x in carrega()['RED_TEAM']}

    def test_bbch_00_00_continua_marcado(self):
        self.assertEqual('DEFEITO_CONFIRMADO', self.rt['RT-6']['RESULTADO'],
                         'se a origem corrigiu BBCH_TO para 07, atualize este teste')
        self.assertIn('00-00', self.rt['RT-6']['PROVA'])

    def test_os_dois_numeros_de_registro_continuam_marcados(self):
        self.assertEqual('DEFEITO_CONFIRMADO', self.rt['RT-10']['RESULTADO'])

    def test_a_contaminacao_de_alvo_continua_marcada(self):
        self.assertEqual('DEFEITO_CONFIRMADO', self.rt['RT-11']['RESULTADO'])
        self.assertIn('DECLARATION_SOURCE', self.rt['RT-11']['PROVA'])

    def test_o_site_nao_virou_prova_regulatoria(self):
        self.assertEqual('HIPOTESE_DERRUBADA', self.rt['RT-1']['RESULTADO'])

    def test_nenhum_produto_de_outro_pais(self):
        self.assertEqual('HIPOTESE_DERRUBADA', self.rt['RT-2']['RESULTADO'])

    def test_o_catalogo_nao_virou_segundo_dono_da_janela(self):
        self.assertEqual('HIPOTESE_DERRUBADA', self.rt['RT-9']['RESULTADO'])


class TestORedTeamTemDentes(unittest.TestCase):
    """Um red team que passaria num handoff quebrado nao vale nada."""

    def test_toda_hipotese_derrubada_tem_mutacao_que_a_derruba(self):
        d = carrega()
        derrubadas = {x['ID'] for x in d['RED_TEAM']
                      if x['RESULTADO'] == 'HIPOTESE_DERRUBADA'}
        com_mutacao = {m['ALVO'] for m in d['RED_TEAM_MUTACOES']}
        self.assertFalse(derrubadas - com_mutacao,
                         'hipotese aprovada sem mutacao que a teste: %s'
                         % sorted(derrubadas - com_mutacao))

    def test_nenhuma_mutacao_passou_batido(self):
        for m in carrega()['RED_TEAM_MUTACOES']:
            self.assertEqual('PEGOU', m['RESULTADO'],
                             '%s: %s' % (m['ALVO'], m['MUTACAO']))


class TestEsCase001(unittest.TestCase):
    """A divergencia nao pode ser fechada por conveniencia."""

    def setUp(self):
        self.e = carrega()['ES_CASE_001']

    def test_continua_aberta(self):
        self.assertEqual('ABERTA', self.e['ESTADO'])
        self.assertFalse(self.e['RESOLVE'])

    def test_o_handoff_nao_traz_janela_nem_par_do_neptune(self):
        self.assertEqual(0, self.e['O_HANDOFF_TRAZ_JANELA_DO_NEPTUNE'])
        self.assertEqual(0, self.e['O_HANDOFF_TRAZ_PAR_OLIVO_x_REPILO_DO_NEPTUNE'])

    def test_citar_a_palavra_floracao_nao_conta_como_evidencia(self):
        """A primeira versao deste portao fechou a divergencia com 18 acertos
        de palavra, todos em AMBIGUOUS_TERMS. Nenhum era uma data."""
        self.assertGreater(self.e['CITACOES_DE_FLORACAO_NO_ARTEFATO'], 0)
        self.assertEqual(0, self.e['CITACOES_QUE_SERVEM_COMO_EVIDENCIA'])
        self.assertIn('AMBIGUOUS_TERMS', self.e['PORQUE_AS_CITACOES_NAO_SERVEM'])

    def test_o_documento_que_fecharia_esta_localizado(self):
        docs = self.e['ONDE_A_EVIDENCIA_PROVAVELMENTE_ESTA']
        self.assertTrue(docs)
        for x in docs:
            self.assertRegex(x['SHA256'], r'^[0-9a-f]{64}$')


class TestOEnsaioDosCincoCasos(unittest.TestCase):

    def setUp(self):
        self.e = carrega()['ENSAIO_DOS_CINCO_CASOS']

    def test_os_cinco_casos_foram_executados(self):
        self.assertEqual('EXECUTADO', self.e['ESTADO'],
                         'NAO_EXECUTADO nao e PASSOU')
        self.assertEqual(['A', 'B', 'C', 'D', 'E'], [c['CASO'] for c in self.e['CASOS']])

    def test_nenhum_produto_some_ao_perguntar_por_um_alvo(self):
        for c in self.e['CASOS']:
            self.assertFalse(c['SOME_AO_PERGUNTAR_POR_ISSUE'],
                             'caso %s: produto sumiu' % c['CASO'])

    def test_o_produto_de_nivel_cultura_e_marcado_como_tal(self):
        b = [c for c in self.e['CASOS'] if c['CASO'] == 'B'][0]
        self.assertIn('CROP_LEVEL', b['ESCOPO'])

    def test_validade_vencida_aparece_e_nao_vira_retirada(self):
        c = [x for x in self.e['CASOS'] if x['CASO'] == 'C'][0]
        self.assertIn('EXPIRY_DATE_PASSED', c['CADUCIDADE'])
        self.assertNotIn('WITHDRAWN', json.dumps(c))

    def test_o_aproximado_nao_virou_faixa_numerica(self):
        d = [x for x in self.e['CASOS'] if x['CASO'] == 'D'][0]
        self.assertIn('APPROXIMATE', d['RESOLUCAO'])
        self.assertNotIn('CLOSED', d['ESTADO_DA_JANELA'])

    def test_o_dado_ausente_continua_not_known(self):
        e = [x for x in self.e['CASOS'] if x['CASO'] == 'E'][0]
        self.assertEqual(['NOT_KNOWN'], e['RESOLUCAO'])
        self.assertEqual(['NOT_KNOWN'], e['ESTADO_DA_JANELA'])

    def test_todo_caso_carrega_o_texto_original(self):
        for c in self.e['CASOS']:
            self.assertTrue(c['REPRESENTADO_SEM_PERDA'], c['CASO'])


class TestInterferencia(unittest.TestCase):
    """As duas camadas juntas: o log continua inteiro e a resposta e uma so."""

    def setUp(self):
        self.i = carrega()['ENSAIO_DE_INTERFERENCIA']

    def test_a_interferencia_foi_medida(self):
        self.assertEqual('EXECUTADO', self.i['ESTADO'],
                         'NAO_EXECUTADO nao e PASSOU')

    def test_o_historico_continua_inteiro(self):
        self.assertGreater(self.i['CAPTURAS_A_MAIS_NO_LOG'], 0,
                           'sem captura repetida no log, o teste nao exerce nada')
        self.assertGreater(self.i['LOG_LINHAS'], self.i['REGISTROS_DISTINTOS'])

    def test_o_estado_corrente_nao_duplica(self):
        self.assertEqual(0, self.i['DUPLICADOS_NO_ESTADO_CORRENTE'])
        self.assertEqual(1, self.i['JANELAS_DO_NEPTUNE_CORRENTES'])
        self.assertEqual('RESOLVIDO', self.i['ESTADO_DO_C7'])

    def test_as_duas_coisas_valem_ao_mesmo_tempo(self):
        self.assertGreater(self.i['JANELAS_NO_LOG'], self.i['JANELAS_CORRENTES'],
                           'o log tem mais janelas que o corrente — e isso e o ponto')

    def test_a_chave_de_captura_inclui_a_fonte(self):
        self.assertIn('fonte, fonte_versao', self.i['CHAVE_DE_CAPTURA'])

    def test_capture_nao_e_registration(self):
        self.assertIn('CAPTURE_NAO_E_REGISTRATION', self.i)


class TestCorrecoes(unittest.TestCase):
    """Cada defeito diz ONDE foi resolvido e com QUAL prova."""

    def setUp(self):
        self.c = carrega()['CORRECOES']

    def test_os_quatro_defeitos_estao_tratados(self):
        self.assertEqual({'C-7', 'RT-6', 'RT-11', 'RT-10'}, set(self.c))
        for k, v in self.c.items():
            self.assertIn(v['ESTADO'], ('RESOLVED', 'MODELADO_SEM_AMBIGUIDADE'), k)
            self.assertTrue(v.get('ONDE_FOI_RESOLVIDO') or v.get('COMO_FOI_MODELADO'), k)

    def test_c7_preserva_historico(self):
        self.assertIn('log continua', self.c['C-7']['COMO'])
        self.assertIn('HISTORY_ROWS=2', self.c['C-7']['PROVA'])

    def test_rt6_nomeia_a_causa_no_coletor(self):
        self.assertIn('search()', self.c['RT-6']['CAUSA_MEDIDA'])
        for j in self.c['RT-6']['JANELAS']:
            self.assertNotEqual(('00', '00'), (str(j['PARSED_START']), str(j['PARSED_END'])))
            self.assertTrue(j['RAW_TEXT'] or j['RESOLUCAO'] == 'NOT_KNOWN')

    def test_rt6_muda_exatamente_duas_janelas(self):
        self.assertEqual(2, sum(1 for j in self.c['RT-6']['JANELAS'] if j['MUDOU']))

    def test_rt11_nao_copiou_o_schema_por_simetria(self):
        self.assertIn('bloco', self.c['RT-11']['POR_QUE_NAO_COPIEI_O_SCHEMA_DE_CULTIVO'])
        self.assertIn('56', self.c['RT-11']['O_QUE_A_MEDICAO_MOSTROU'])

    def test_rt11_corrige_a_leitura_anterior(self):
        """A rodada passada disse 25 com o denominador errado. Sao 56."""
        self.assertIn('denominador', self.c['RT-11']['CORRECAO_DA_LEITURA_ANTERIOR'])

    def test_rt11_so_admite_linha_ancorada(self):
        o = self.c['RT-11']['ORIGENS_MEDIDAS']
        self.assertEqual(5, o['PAIR_TABLE_ROW'])
        self.assertEqual(176, o['PAGE_BODY_TEXT'])

    def test_rt10_nao_reconciliou_por_nome(self):
        r = self.c['RT-10']
        self.assertEqual('NOME IGUAL != MESMO REGISTRO', r['A_LEI'])
        self.assertEqual('PLAUSIBLE_NOT_PROVED', r['LINK_STATE'])
        self.assertEqual(2, len(r['IDENTIFICADORES']))
        for i in r['IDENTIFICADORES']:
            self.assertTrue(i['EVIDENCIA'], i['TIPO'])

    def test_rt10_investigou_as_cinco_hipoteses(self):
        v = {x['HIPOTESE'][0]: x['VEREDITO'] for x in self.c['RT-10']['A_INVESTIGACAO']}
        self.assertEqual('REFUTADA', v['B'], 'id interno tinha de ser refutada com dado')
        self.assertEqual('REFUTADA', v['C'], 'erro de extracao tinha de ser refutada')
        self.assertIn('RESPOSTA', v['E'])


class TestVeredito(unittest.TestCase):

    def setUp(self):
        self.v = carrega()['VEREDITO']

    def test_o_veredito_e_um_dos_tres(self):
        self.assertIn(self.v['VEREDITO'],
                      ('HANDOFF_READY_TO_IMPORT', 'HANDOFF_PARTIAL', 'HANDOFF_REJECTED'))

    def test_partial_precisa_dizer_o_que_entra_e_o_que_nao(self):
        if self.v['VEREDITO'] == 'HANDOFF_PARTIAL':
            self.assertTrue(self.v['PODE_ENTRAR_AGORA'])
            self.assertTrue(self.v['NAO_PODE_ENTRAR_AINDA'])
            for x in self.v['NAO_PODE_ENTRAR_AINDA']:
                self.assertTrue(x['O_QUE_DESTRAVA'], x['ESTRUTURA'])

    def test_todo_bloqueio_aponta_um_achado_real(self):
        ids = {x['ID'] for x in carrega()['RED_TEAM']} | \
              {c['ID'] for c in carrega()['CONFLITOS_COM_O_SCHEMA']}
        for x in self.v['NAO_PODE_ENTRAR_AINDA']:
            for b in re.split(r'\s*·\s*', x['BLOQUEIO']):
                self.assertIn(b, ids, x['ESTRUTURA'])

    def test_o_procedimento_existe_e_nao_foi_executado(self):
        self.assertGreaterEqual(len(self.v['PROCEDIMENTO_DE_IMPORTACAO_QUANDO_DESTRAVAR']), 5)
        naofez = ' '.join(self.v['O_QUE_ESTA_RODADA_NAO_FEZ'])
        for termo in ('nao importou', 'nao aplicou', 'nao mesclou'):
            self.assertIn(termo, naofez)


class TestOEnsaioNaoEImportacao(unittest.TestCase):

    def test_o_arquivo_do_ensaio_declara_que_nao_e_importacao(self):
        p = os.path.join(RAIZ, 'supabase', 'ensaios', 'ADAMA-ES-ENSAIO-CINCO-CASOS.sql')
        self.assertTrue(os.path.exists(p))
        with open(p, encoding='utf-8') as f:
            cab = f.read(1200)
        self.assertIn('NÃO É IMPORTAÇÃO', cab)
        self.assertIn('DESCARTÁVEL', cab)

    def test_o_ensaio_nao_mora_em_migrations(self):
        mig = os.listdir(os.path.join(RAIZ, 'supabase', 'migrations'))
        self.assertFalse([f for f in mig if 'ADAMA' in f.upper() or 'ENSAIO' in f.upper()],
                         'ensaio virou migration — isso seria importacao')

    # As migrations 001-012 sao a fundacao. Tudo depois delas entrou por causa de
    # um defeito MEDIDO, e o defeito tem de estar escrito no proprio arquivo.
    # A primeira versao deste teste exigia `len(mig) == 14`, o que obrigava a
    # subir o numero a cada rodada — mover a regua em vez de exercer a lei. O
    # que importa nao e QUANTAS migrations existem: e que nenhuma nova exista
    # sem o defeito que a justifica.
    FUNDACAO = 12
    DEFEITO_MEDIDO = {
        '013_captura_nao_e_registro.sql': 'CAPTURE != REGISTRATION',
        '015_cicatrizes_do_brasil.sql': 'praca',
        '016_checkpoint_e_unidade_analitica.sql': 'SEM_CHECKPOINT_NAO_GASTEI',
        '017_o_que_a_conferencia_de_localizacao_achou.sql': 'PUBLISHED_AT != FACT_TIME',
        '018_o_lugar_do_fato_ganha_dono.sql': 'DOIS DONOS DA MESMA LEI',
        '014_catalogo_publico_fabricante.sql': 'HANDOFF_SCHEMA_VALID_THEN',
    }

    def test_a_unica_migration_nova_tem_incompatibilidade_provada(self):
        """Migration nova so entra com defeito MEDIDO, escrito no arquivo."""
        mig = sorted(f for f in os.listdir(os.path.join(RAIZ, 'supabase', 'migrations'))
                     if f.endswith('.sql'))
        novas = [f for f in mig if int(f[:3]) > self.FUNDACAO]
        self.assertEqual(sorted(self.DEFEITO_MEDIDO), novas,
                         'migration nova sem defeito declarado neste teste: %s' % novas)
        self.assertIn('013_captura_nao_e_registro.sql', mig)
        for nome, marca in self.DEFEITO_MEDIDO.items():
            with open(os.path.join(RAIZ, 'supabase', 'migrations', nome),
                      encoding='utf-8') as f:
                texto = f.read()
            self.assertIn(marca, texto, nome)
            self.assertIn('NÃO EXECUTADA em Supabase', texto, nome)
        with open(os.path.join(RAIZ, 'supabase', 'migrations',
                               '013_captura_nao_e_registro.sql'), encoding='utf-8') as f:
            self.assertIn('3 vezes', f.read(), 'a 013 cita o defeito medido')

    def test_o_catalogo_entrou_SELETIVAMENTE_e_nao_por_merge(self):
        """Este teste ja afirmou que o catalogo estava FORA, e afirmava certo.

        Ele existia para impedir um merge cego enquanto a importacao nao
        estava autorizada. A missao de importacao controlada autorizou, e o
        que mudou foi UMA migration renumerada mais os artefatos que ela
        precisa — nao a branch inteira.

        O que o teste guarda agora e a diferenca entre integracao seletiva e
        merge: os scripts que so fazem sentido na maquina do operador
        continuam FORA, e e por eles que se mede se alguem mesclou.
        """
        mig = os.listdir(os.path.join(RAIZ, 'supabase', 'migrations'))
        cat = [f for f in mig if 'catalogo' in f.lower()]
        self.assertEqual(['014_catalogo_publico_fabricante.sql'], cat,
                         'entrou mais de uma migration de catalogo: %s' % cat)
        # Categoria E do inventario: ferramenta de coleta e de envio moram na
        # maquina do operador. Se aparecerem aqui, houve merge.
        so_do_operador = ('storage_preservar.py', 'recolher_lote.sh', 'adama_es.py')
        scripts = os.listdir(os.path.join(RAIZ, 'scripts'))
        for f in so_do_operador:
            self.assertNotIn(f, scripts,
                             '%s e da maquina do operador — se subiu, foi merge' % f)


if __name__ == '__main__':
    unittest.main()
