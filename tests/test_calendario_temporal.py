"""Regressoes do calendario agronomico que nao precisam de banco.

As regressoes de SIGNIFICADO rodam em supabase/tests/regressoes_calendario.sql,
contra um Postgres de verdade — nenhum teste aqui substitui aquelas. O que este
arquivo cobre e o outro lado da ponte: que todo valor que o motor SQL consegue
emitir tem tratamento de exibicao nas tres linguas, e que o contrato entregue ao
Design descreve o payload que o codigo realmente produz.

O risco especifico: uma enum ganha um valor novo na migration, o portal renderiza
a constante crua em maiuscula, e o cliente le WINDOW_STATE=NOT_KNOWN na tela.
"""
import json
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMOSTRAS = os.path.join(RAIZ, 'data', 'samples')
MIG = os.path.join(RAIZ, 'supabase', 'migrations')
TESTES_SQL = os.path.join(RAIZ, 'supabase', 'tests')
FIXTURES = os.path.join(RAIZ, 'supabase', 'fixtures')

LINGUAS = ('DISPLAY_TEXT_PT', 'DISPLAY_TEXT_EN', 'DISPLAY_TEXT_ES')


def carrega(nome):
    with open(os.path.join(AMOSTRAS, nome), encoding='utf-8') as f:
        return json.load(f)


def sql(nome):
    with open(os.path.join(MIG, nome), encoding='utf-8') as f:
        return f.read()


def enum_da_migration(texto, nome):
    m = re.search(r"create type %s as enum \((.*?)\);" % nome, texto, re.S)
    assert m, nome
    return re.findall(r"'([A-Z_]+)'", m.group(1))


def regras_de(campo):
    return [r for r in carrega('DISPLAY-LAYER-V1.json')['REGRAS']
            if r['SOURCE_FIELD'] == campo]


class TestTodaEnumTemTratamentoDeExibicao(unittest.TestCase):
    """Um valor sem regra de exibicao chega cru na tela do cliente."""

    def setUp(self):
        self.m010 = sql('010_calendario_agronomico.sql')

    def cobre(self, tipo_sql, campo_display, extras=()):
        valores = set(enum_da_migration(self.m010, tipo_sql)) | set(extras)
        cobertos = {r['SOURCE_VALUE'] for r in regras_de(campo_display)}
        faltando = valores - cobertos
        self.assertFalse(faltando, '%s sem texto de exibicao: %s'
                                   % (campo_display, sorted(faltando)))

    def test_resolucao_temporal(self):
        self.cobre('resolucao_temporal', 'TEMPORAL_RESOLUTION')

    def test_tipo_calendario(self):
        self.cobre('tipo_calendario', 'CALENDAR_TYPE')

    def test_fase_cultura(self):
        # NOT_KNOWN nao e valor da enum: e o que o payload devolve quando nao ha
        # calendario com precisao suficiente. Precisa de texto do mesmo jeito.
        self.cobre('fase_cultura', 'CROP_PHASE', extras=('NOT_KNOWN',))

    def test_tipo_janela_issue(self):
        self.cobre('tipo_janela_issue', 'ISSUE_WINDOW_TYPE')

    def test_estados_de_janela_emitidos_pelas_funcoes(self):
        m011 = sql('011_calendario_consultas.sql')
        m012 = sql('012_contexto_temporal_do_caso.sql')
        emitidos = set(re.findall(r"'(ACTIVE|UPCOMING|CLOSED|OUTSIDE_MONTH_RANGE|"
                                  r"NOT_KNOWN|NO_DATA|OBSERVED)'", m011 + m012))
        cobertos = {r['SOURCE_VALUE'] for r in regras_de('WINDOW_STATE')}
        self.assertFalse(emitidos - cobertos,
                         'WINDOW_STATE sem texto: %s' % sorted(emitidos - cobertos))

    def test_estados_de_frescor(self):
        m010, m011 = self.m010, sql('011_calendario_consultas.sql')
        # os quatro da constraint da tabela mais os dois que a funcao devolve
        na_tabela = set(re.findall(r"estado in \((.*?)\)", m010)[0].replace("'", '').split(','))
        na_funcao = set(re.findall(r"'(NO_RULE_FOR_PURPOSE|AGE_NOT_KNOWN|STALE_FOR_PURPOSE)'", m011))
        cobertos = {r['SOURCE_VALUE'] for r in regras_de('EVIDENCE_FRESHNESS')}
        faltando = (na_tabela | na_funcao) - cobertos
        self.assertFalse(faltando, 'EVIDENCE_FRESHNESS sem texto: %s' % sorted(faltando))


class TestAsRegrasNovasNaoDerivam(unittest.TestCase):

    def test_toda_regra_temporal_tem_as_tres_linguas_e_a_semantica(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        for r in d['REGRAS']:
            if r['SOURCE_FIELD'] not in d['CAMPOS_TEMPORAIS_ADICIONADOS']:
                continue
            for k in LINGUAS + ('SEMANTIC_RULE',):
                self.assertTrue(r.get(k), '%s sem %s' % (r['DISPLAY_KEY'], k))

    def test_nenhum_texto_temporal_vira_recomendacao(self):
        """WINDOW_OPEN != APPLY_NOW tambem na camada de exibicao."""
        proibidas = ('aplique', 'aplicar agora', 'apply now', 'aplique ahora',
                     'aplicar ahora', 'trate agora', 'recomendamos', 'we recommend')
        d = carrega('DISPLAY-LAYER-V1.json')
        for r in d['REGRAS']:
            if r['SOURCE_FIELD'] not in d['CAMPOS_TEMPORAIS_ADICIONADOS']:
                continue
            for k in LINGUAS:
                for p in proibidas:
                    self.assertNotIn(p, r[k].lower(), '%s:%s' % (r['DISPLAY_KEY'], k))

    def test_not_known_nunca_e_traduzido_como_fechado(self):
        """O pior erro possivel do calendario, checado nas tres linguas.

        A busca e por INICIO DE PALAVRA. Sem isso o teste acusa "nao
        determinada" de conter "terminad" — armadilha que este projeto ja
        pisou tres vezes com listas de termos proibidos.
        """
        fechado = ('fechad', 'closed', 'cerrad', 'encerrad', 'terminad', 'acabou')
        for campo in ('WINDOW_STATE', 'TEMPORAL_RESOLUTION', 'CROP_PHASE',
                      'REGISTRATION_EXPIRY_STATE', 'EVIDENCE_FRESHNESS'):
            for r in regras_de(campo):
                if r['SOURCE_VALUE'] not in ('NOT_KNOWN', 'NO_DATA', 'AGE_NOT_KNOWN',
                                             'NO_RULE_FOR_PURPOSE'):
                    continue
                for k in LINGUAS:
                    for p in fechado:
                        self.assertIsNone(re.search(r'\b' + p, r[k].lower()),
                                          '%s:%s diz fechado sobre um desconhecido'
                                          % (r['DISPLAY_KEY'], k))

    def test_expiry_nunca_e_traduzido_como_retirada(self):
        r = [x for x in regras_de('REGISTRATION_EXPIRY_STATE')
             if x['SOURCE_VALUE'] == 'EXPIRY_DATE_PASSED'][0]
        for k in LINGUAS:
            for p in ('retirad', 'withdraw', 'cancelad', 'proibid', 'prohibid', 'banned'):
                self.assertIsNone(re.search(r'\b' + p, r[k].lower()), k)

    def test_outside_month_range_nao_vira_closed(self):
        r = [x for x in regras_de('WINDOW_STATE')
             if x['SOURCE_VALUE'] == 'OUTSIDE_MONTH_RANGE'][0]
        for k in LINGUAS:
            for p in ('fechad', 'closed', 'cerrad'):
                self.assertIsNone(re.search(r'\b' + p, r[k].lower()), k)

    def test_closed_diz_o_ciclo(self):
        """CLOSED != NO_ACTION: sem 'neste ciclo' a frase encerra o assunto."""
        r = [x for x in regras_de('WINDOW_STATE') if x['SOURCE_VALUE'] == 'CLOSED'][0]
        self.assertRegex(r['DISPLAY_TEXT_PT'].lower(), 'ciclo')
        self.assertRegex(r['DISPLAY_TEXT_EN'].lower(), 'cycle')
        self.assertRegex(r['DISPLAY_TEXT_ES'].lower(), 'ciclo')

    def test_o_contador_de_regras_bate_com_a_lista(self):
        d = carrega('DISPLAY-LAYER-V1.json')
        self.assertEqual(d['REGRAS_COUNT'], len(d['REGRAS']))

    def test_nenhuma_display_key_repetida(self):
        chaves = [r['DISPLAY_KEY'] for r in carrega('DISPLAY-LAYER-V1.json')['REGRAS']]
        self.assertEqual(len(chaves), len(set(chaves)))


class TestContratoParaODesign(unittest.TestCase):

    def setUp(self):
        self.d = carrega('AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1.json')

    def test_os_quatro_relogios_estao_nomeados_e_separados(self):
        r = self.d['OS_QUATRO_RELOGIOS']
        self.assertEqual(4, len(r))
        self.assertEqual(['A', 'B', 'C', 'D'], [x['CLOCK'] for x in r])
        donos = [x['DONO'] for x in r]
        self.assertEqual(len(donos), len(set(donos)), 'dois relogios com o mesmo dono')
        for x in r:
            self.assertTrue(x['NAO_E'], '%s sem a fronteira declarada' % x['NOME'])

    def test_o_relogio_d_nao_tem_tabela_e_isso_e_dito(self):
        d = [x for x in self.d['OS_QUATRO_RELOGIOS'] if x['CLOCK'] == 'D'][0]
        self.assertIn('nao tem tabela', d['DONO'])

    def test_nao_ha_cor_no_contrato_de_dado(self):
        s = json.dumps(self.d, ensure_ascii=False)
        self.assertEqual([], re.findall(r'#[0-9A-Fa-f]{6}', s))
        self.assertNotIn('"COR"', s.upper())

    def test_nao_existe_closing(self):
        valores = {x['VALOR'] for x in self.d['WINDOW_STATE']}
        self.assertNotIn('CLOSING', valores)
        self.assertIn('limiar', self.d['NAO_EXISTE_CLOSING'])

    def test_todo_estado_de_janela_diz_o_que_nao_significa(self):
        for x in self.d['WINDOW_STATE']:
            self.assertTrue(x.get('NAO_SIGNIFICA'), x['VALOR'])

    def test_o_exemplo_e_lido_do_banco_e_nao_escrito_a_mao(self):
        e = self.d['EXEMPLO_REAL_LIDO_DO_BANCO']
        self.assertIn('psql', e['COMO_FOI_GERADO'])
        for caso in ('CASO_OLIVE_REPILO', 'CASO_MAIZE_AMARANTHUS_PALMERI'):
            p = e[caso]
            self.assertEqual('2026-08-30', p['as_of_date'])
            self.assertEqual('ES', p['country'])
            for k in ('current_crop_phase', 'current_issue_window_state',
                      'product_window_state', 'observation_freshness',
                      'next_relevant_window', 'temporal_unknown_count', 'law'):
                self.assertIn(k, p, '%s sem %s' % (caso, k))

    def test_o_exemplo_carrega_a_lei_no_proprio_payload(self):
        for caso in ('CASO_OLIVE_REPILO', 'CASO_MAIZE_AMARANTHUS_PALMERI'):
            lei = self.d['EXEMPLO_REAL_LIDO_DO_BANCO'][caso]['law']
            self.assertEqual('NOT_KNOWN', lei['current_field_need'])
            self.assertEqual('NOT_KNOWN', lei['commercial_availability'])

    def test_o_exemplo_nao_carrega_nada_de_infraestrutura(self):
        s = json.dumps(self.d['EXEMPLO_REAL_LIDO_DO_BANCO'], ensure_ascii=False).lower()
        for p in ('raw_asset', 'bucket', 's3://', 'api_key', 'token', 'custo'):
            self.assertNotIn(p, s)

    def test_a_divergencia_do_neptune_esta_registrada_e_aberta(self):
        """A maquina discorda do cartao. Isso se registra, nao se maquia."""
        v = self.d['DIVERGENCIA_HONESTA_A_RESOLVER']
        self.assertEqual('CLOSED', v['O_CARTAO_DIZ'])
        self.assertEqual('NOT_KNOWN', v['O_MOTOR_DIZ'])
        self.assertIn('ABERTO', v['STATUS'])
        neptune = [p for p in self.d['EXEMPLO_REAL_LIDO_DO_BANCO']
                   ['CASO_OLIVE_REPILO']['product_window_state']
                   if p['product'] == 'NEPTUNE']
        self.assertEqual(1, len(neptune))
        self.assertEqual('NOT_KNOWN', neptune[0]['state'],
                         'o exemplo tem de mostrar a divergencia, nao esconde-la')

    def test_as_cinco_ignorancias_continuam_cinco(self):
        c = self.d['CINCO_IGNORANCIAS_QUE_NAO_PODEM_COLAPSAR']
        for k in ('NAO_SEI', 'NOT_COLLECTED', 'NOT_KNOWN', 'AUSENTE_MEDIDO', 'NAO_TESTADO'):
            self.assertIn(k, c)
        self.assertEqual(5, len({c[k] for k in
                                 ('NAO_SEI', 'NOT_COLLECTED', 'NOT_KNOWN',
                                  'AUSENTE_MEDIDO', 'NAO_TESTADO')}))

    def test_o_contrato_nao_promete_o_que_o_payload_nao_traz(self):
        proibido = self.d['O_QUE_NUNCA_VEM_NESTE_PAYLOAD']
        self.assertTrue(any('disponibilidade comercial' in x for x in proibido))
        self.assertTrue(any('recomendacao' in x for x in proibido))


class TestAsMigrationsDoCalendario(unittest.TestCase):

    def test_as_tres_migrations_existem_e_estao_numeradas_em_sequencia(self):
        for n in ('010_calendario_agronomico.sql', '011_calendario_consultas.sql',
                  '012_contexto_temporal_do_caso.sql'):
            self.assertTrue(os.path.exists(os.path.join(MIG, n)), n)

    def test_issue_window_nao_ganhou_coluna_de_pressao(self):
        m = sql('010_calendario_agronomico.sql')
        corpo = m[m.index('create table public.issue_window'):m.index('create table public.registro_uso_janela')]
        for p in ('pressao', 'incidencia', 'severidade', 'intensidade'):
            self.assertNotIn('\n  ' + p, corpo, 'issue_window ganhou coluna %s' % p)

    def test_a_janela_do_produto_e_filha_de_registro_uso(self):
        m = sql('010_calendario_agronomico.sql')
        self.assertIn('references public.registro_uso(id)', m)
        self.assertNotIn('create table public.registro_uso (', m,
                         'registro_uso ja tem dono em 006; nao pode nascer de novo aqui')

    def test_nenhuma_tabela_do_calendario_guarda_hoje(self):
        """Estado corrente e derivado na pergunta, nunca coluna.

        Procura so nas DEFINICOES DE COLUNA. Comentario que menciona as_of_date
        para explicar por que ele nao esta aqui e o oposto de uma violacao.
        """
        m = sql('010_calendario_agronomico.sql')
        for tabela in ('crop_calendar', 'issue_window', 'registro_uso_janela'):
            corpo = m[m.index('create table public.%s (' % tabela):]
            corpo = corpo[:corpo.index('\n);')]
            colunas = [l.split()[0] for l in corpo.split('\n')
                       if re.match(r'  [a-z_]+ +[a-z]', l)]
            for c in ('hoje', 'today', 'as_of', 'as_of_date', 'estado_atual', 'status_atual'):
                self.assertNotIn(c, colunas, '%s ganhou a coluna %s' % (tabela, c))

    def test_a_regua_de_frescor_e_dado_com_justificativa(self):
        m = sql('010_calendario_agronomico.sql')
        self.assertIn('justificativa text not null', m)

    def test_as_tres_ignorancias_do_frescor_sao_distintas_no_codigo(self):
        m = sql('011_calendario_consultas.sql')
        for e in ('AGE_NOT_KNOWN', 'NO_RULE_FOR_PURPOSE', 'STALE_FOR_PURPOSE'):
            self.assertIn("'%s'" % e, m)

    def test_a_proxima_janela_so_olha_recorrente(self):
        m = sql('011_calendario_consultas.sql')
        corpo = m[m.index('function public.f_next_relevant_window'):]
        corpo = corpo[:corpo.index('comment on function public.f_next_relevant_window')]
        self.assertIn('and cc.recorrente', corpo, 'metade CROP_CALENDAR sem filtro')
        self.assertIn('and iw.recorrente', corpo, 'metade ISSUE_WINDOW sem filtro')

    def test_toda_funcao_temporal_recebe_pais(self):
        m = sql('011_calendario_consultas.sql') + sql('012_contexto_temporal_do_caso.sql')
        for f in ('f_crop_calendar', 'f_next_relevant_window', 'f_latest_observations',
                  'f_bbch_observado', 'f_case_temporal_context'):
            corpo = m[m.index('function public.%s(' % f):]
            self.assertIn('p_pais', corpo[:corpo.index(')')], f)

    def test_a_verificacao_pos_aplicacao_confere_os_quatro_relogios(self):
        m = sql('008_verificacao_pos_aplicacao.sql')
        for t in ('crop_calendar', 'issue_window', 'registro_uso_janela', 'freshness_regra'):
            self.assertIn("'%s'" % t, m, '008 nao confere a tabela %s' % t)
        self.assertIn('campanha_observada_nao_recorre', m)
        self.assertIn('f_case_temporal_context', m)


class TestFixtureEProvas(unittest.TestCase):

    def test_a_fixture_es_existe_e_declara_o_que_nao_esta_nela(self):
        p = os.path.join(FIXTURES, 'es_calendario_mvp.sql')
        self.assertTrue(os.path.exists(p))
        with open(p, encoding='utf-8') as f:
            cab = f.read(3000)
        self.assertIn('deliberadamente', cab.lower(),
                      'a fixture precisa dizer o que ficou de fora e por que')

    def test_a_fixture_nao_inventa_calendario_de_2027(self):
        """O caso do milho diz NEXT_CYCLE, e e so isso que a fonte sustenta.

        A proibicao e sobre CALENDARIO inventado, nao sobre o ano 2027. A
        caducidade 2027-07-31 do ACCRESTO e fato lido do registro espanhol e
        tem de continuar ali — por isso o teste olha as tabelas de tempo, e nao
        o arquivo inteiro.
        """
        with open(os.path.join(FIXTURES, 'es_calendario_mvp.sql'), encoding='utf-8') as f:
            texto = f.read()
        corpo = '\n'.join(l for l in texto.split('\n') if not l.lstrip().startswith('--'))
        for tabela in ('crop_calendar', 'issue_window', 'registro_uso_janela'):
            for bloco in re.findall(r'insert into public\.%s\b(.*?);' % tabela, corpo, re.S):
                self.assertEqual([], re.findall(r"'2027-\d{2}-\d{2}'", bloco),
                                 '%s recebeu data de 2027 sem fonte' % tabela)
        # e a caducidade real continua la, onde ela pertence
        self.assertIn("'2027-07-31'", corpo)

    def test_as_regressoes_sql_existem_e_falham_alto(self):
        p = os.path.join(TESTES_SQL, 'regressoes_calendario.sql')
        self.assertTrue(os.path.exists(p))
        with open(p, encoding='utf-8') as f:
            t = f.read()
        self.assertIn('REGRESSOES_FALHARAM', t, 'a suite precisa terminar em excecao')
        # cada distincao nomeada pelo contrato tem pelo menos uma afirmacao
        for d in ('CROP_CALENDAR != PRODUCT_WINDOW', 'PRODUCT_WINDOW_OPEN != APPLY_NOW',
                  'ISSUE_WINDOW != FIELD_PRESSURE', 'OBSERVATION_DATE != PUBLICATION_DATE',
                  'PUBLICATION_DATE != CAPTURE_DATE', 'SOURCE_COUNTRY != FACT_COUNTRY',
                  'TYPICAL_CALENDAR != OBSERVED_CAMPAIGN', 'FIRST_YEAR != RECURRING_CALENDAR',
                  'MONTH_RESOLUTION != EXACT_DATE', 'BBCH_RANGE != CALENDAR_DATE',
                  'NEXT_CYCLE != EXACT_NEXT_DATE', 'UNKNOWN != CLOSED',
                  'NO_DATA != NO_WINDOW', 'CLOSED != NO_ACTION',
                  'APPLICATION_WINDOW != COMMERCIAL_AVAILABILITY',
                  'EXPIRY != WITHDRAWAL', 'AS_OF_DATE != STORED_TODAY',
                  'COUNTRY_ISOLATION'):
            self.assertIn(d, t, 'distincao sem regressao: %s' % d)


if __name__ == '__main__':
    unittest.main()
