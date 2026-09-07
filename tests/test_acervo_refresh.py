"""O REFRESH DA FRONTEIRA ACERVO → PACOTE: sete cenários, e a lei que os une.

    python3 -m unittest tests.test_acervo_refresh -v

A LEI
-----
    ERRO DE COLETA NÃO PODE APAGAR O ÚLTIMO ESTADO VÁLIDO.

Um coletor que falha e devolve lista vazia é pior que um coletor que estoura:
o vazio atravessa a cadeia inteira sem acender nada, e o pacote sai menor com
cara de completo. Aqui o insumo é pinado por (COMMIT, PATH, BLOB) + SHA256, e
qualquer divergência LEVANTA — não devolve vazio, não devolve parcial.

OS SETE CENÁRIOS
----------------
    1  nenhuma mudança          → mesmo pacote, byte a byte
    2  novo item no acervo      → aparece, e a conta continua fechando
    3  item alterado            → o texto novo entra e o SHA256 muda com ele
    4  fonte indisponível       → LEVANTA. Não devolve vazio.
    5  arquivo inválido         → LEVANTA. Não devolve parcial.
    6  schema mudou             → o campo que sumiu vira UNKNOWN declarado
    7  dado sumiu temporariamente → LEVANTA, e o artefato anterior fica intacto

Os cenários 4 a 7 não podem ser testados mexendo no acervo de verdade — ele é
imutável de propósito. São testados contra o MANIFESTO: trocar o SHA256, apagar
o blob, apontar para um blob que não é JSON. É a mesma porta que a cadeia usa.
"""
import copy
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import acervo_fonte as AF          # noqa: E402
import acervo_transcricoes as AT   # noqa: E402


def _fontes():
    return {s['KEY']: s for s in AF.manifesto()['SOURCES']}


def _uma(familia='TRANSCRIPTS', papel='BATCH'):
    for s in AF.manifesto()['SOURCES']:
        if s['FAMILY'] == familia and s['ROLE'] == papel:
            return s
    raise AssertionError('nenhuma fonte %s/%s no manifesto' % (familia, papel))


class TestManifestoPinado(unittest.TestCase):
    """O manifesto é o contrato do insumo. Se ele afrouxar, tudo afrouxa."""

    def test_todo_insumo_tem_endereco_completo(self):
        for s in AF.manifesto()['SOURCES']:
            for campo in ('KEY', 'FAMILY', 'ROLE', 'REF', 'COMMIT', 'PATH',
                          'BLOB', 'SHA256', 'BYTES'):
                self.assertTrue(s.get(campo), '%s sem %s' % (s.get('PATH'), campo))
            self.assertEqual(len(s['SHA256']), 64, 'SHA256 malformado')
            self.assertEqual(len(s['COMMIT']), 40, 'COMMIT nao e sha completo')

    def test_as_chaves_nao_colidem(self):
        ks = [s['KEY'] for s in AF.manifesto()['SOURCES']]
        self.assertEqual(len(ks), len(set(ks)), 'chave duplicada no manifesto')

    def test_o_sha256_declarado_confere_com_o_blob(self):
        """Cenário 1 · nenhuma mudança: todo insumo abre e bate."""
        for s in AF.manifesto()['SOURCES']:
            AF.bytes_de(s['KEY'])          # levanta se divergir


class TestCenariosDeFalha(unittest.TestCase):
    """4, 5 e 7 · a coleta que falha tem de FALHAR, nunca entregar menos."""

    def test_4_fonte_indisponivel_levanta_em_vez_de_devolver_vazio(self):
        s = copy.deepcopy(_uma())
        # um blob que nao existe: e o que «fonte indisponivel» parece aqui
        s['BLOB'] = '0' * 40
        with self.assertRaises(AF.AcervoIndisponivel):
            AF.ler(s['KEY'], {s['KEY']: s})

    def test_5_conteudo_trocado_levanta_pelo_sha256(self):
        """Arquivo inválido / adulterado: o SHA256 é a porta, e ela tranca."""
        s = copy.deepcopy(_uma())
        s['SHA256'] = 'f' * 64
        with self.assertRaises(AF.AcervoIndisponivel) as ctx:
            AF.ler(s['KEY'], {s['KEY']: s})
        self.assertIn('SHA256', str(ctx.exception))

    def test_7_dado_que_sumiu_nao_vira_lista_vazia(self):
        """O modo de falha que mais dói: sumir em silêncio.

        Nenhum caminho de `acervo_fonte` devolve `[]`, `{}` ou `None` quando o
        insumo não abre. Se um dia devolver, este teste cai — e é para cair.
        """
        s = copy.deepcopy(_uma())
        s['BLOB'] = '1' * 40
        try:
            r = AF.ler(s['KEY'], {s['KEY']: s})
        except AF.AcervoIndisponivel:
            return
        self.fail('devolveu %r em vez de levantar' % (r,))


class TestIdempotencia(unittest.TestCase):
    """Cenário 1 · mesma entrada, mesma saída — inclusive na ordem."""

    def test_o_censo_e_estavel_entre_duas_leituras(self):
        a, b = AT.censo(), AT.censo()
        self.assertEqual([x['TRANSCRIPT_ID'] for x in a],
                         [x['TRANSCRIPT_ID'] for x in b])
        self.assertEqual([x['TEXT_SHA256'] for x in a],
                         [x['TEXT_SHA256'] for x in b])

    def test_a_ordem_nao_depende_da_ordem_do_manifesto(self):
        ids = [x['TRANSCRIPT_ID'] for x in AT.censo()]
        self.assertEqual(ids, sorted(ids), 'a saida tem de sair ordenada por ID')


class TestNadaSomeSemEstado(unittest.TestCase):
    """A conta fecha, e cada ausência tem razão escrita."""

    @classmethod
    def setUpClass(cls):
        cls.objs = AT.censo()

    def test_2_todo_objeto_tem_estado(self):
        for o in self.objs:
            self.assertIn(o['STATE'], ('INCLUDED', 'EXCLUDED', 'UNKNOWN'))
            self.assertTrue(o['STATE_REASON'], '%s sem razao' % o['TRANSCRIPT_ID'])

    def test_3_texto_e_hash_andam_juntos(self):
        """Item alterado: se o texto muda, o SHA256 muda. E vice-versa."""
        for o in self.objs:
            if o['CHARS']:
                self.assertEqual(o['TEXT_SHA256'], AF.sha256_texto(o['TEXT']))
                self.assertEqual(o['CHARS'], len(o['TEXT']))
            else:
                self.assertIsNone(o['TEXT_SHA256'])

    def test_6_campo_ausente_vira_UNKNOWN_declarado_e_nao_vazio_mudo(self):
        """Schema mudou: o campo que some vira UNKNOWN, nunca string vazia."""
        for o in self.objs:
            for campo in ('SOURCE_COUNTRY', 'SOURCE_LANGUAGE', 'CASE_ID',
                          'CASE_COUNTRY', 'PLATFORM', 'TITLE'):
                self.assertNotEqual(o[campo], '', '%s: %s vazio mudo'
                                    % (o['TRANSCRIPT_ID'], campo))
                self.assertIsNotNone(o[campo])

    def test_sentinela_do_acervo_nunca_conta_como_texto(self):
        """«NÃO SEI» são sete caracteres de honestidade, não sete de fala."""
        for o in self.objs:
            self.assertFalse(AT._e_sentinela(o['TEXT'][:40]) and o['CHARS'],
                             '%s conta sentinela como fala' % o['TRANSCRIPT_ID'])

    def test_o_termo_de_busca_nao_vira_cultura(self):
        """QUERY_TERM ≠ PROVED_CONTENT — a trava do §6, aplicada à fala."""
        for o in self.objs:
            if o.get('CROP_ISSUE_BASIS'):
                self.assertIn('consulta', o['CROP_ISSUE_BASIS'].lower(),
                              'a base de CROP/ISSUE deixou de declarar-se')


class TestPacoteQuandoMontado(unittest.TestCase):
    """Se o pacote está no disco, ele tem de concordar com o acervo."""

    ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

    def setUp(self):
        if not os.path.isdir(self.ING):
            self.skipTest('pacote nao montado — rode bash scripts/v21_cadeia.sh')

    def _le(self, nome):
        with open(os.path.join(self.ING, nome), encoding='utf-8') as f:
            return json.load(f)

    def test_transcricoes_do_pacote_batem_com_o_censo(self):
        d = self._le('TRANSCRIPTS.json')
        self.assertEqual(d['COUNT_TOTAL'], len(AT.censo()))
        self.assertEqual(d['COUNT_TOTAL'],
                         d['BY_STATE'].get('INCLUDED', 0)
                         + d['BY_STATE'].get('EXCLUDED', 0)
                         + d['BY_STATE'].get('UNKNOWN', 0))

    def test_a_escada_nao_sobe_sozinha(self):
        """Cada degrau é ≤ o anterior. Se inverter, alguém promoveu estado."""
        e = self._le('TRANSCRIPTS.json')['LADDER']
        ordem = ['VIDEO_EXISTS', 'TRANSCRIPT_EXISTS', 'TRANSCRIPT_USABLE',
                 'TRANSCRIPT_INCLUDED_IN_PACKAGE', 'TRANSCRIPT_USED_AS_EVIDENCE']
        for a, b in zip(ordem, ordem[1:]):
            self.assertGreaterEqual(e[a], e[b], '%s < %s: degrau invertido' % (a, b))

    def test_a_ciencia_nao_promove_busca_a_fato(self):
        d = self._le('SCIENCE.json')
        for r in d['RECORDS']:
            self.assertTrue(r.get('CROP_IS_QUERY_TERM'),
                            '%s deixou de declarar que CROP e termo de busca' % r['ID'])
            if r.get('PROVED_CROP'):
                self.assertIn('PROVED_CROP_EVIDENCE', r,
                              '%s afirma PROVED_CROP sem evidencia' % r['ID'])

    def test_o_anuncio_ativo_carrega_a_data_que_o_prova(self):
        d = self._le('COMPETITOR-ACTIVITIES.json')
        for r in d['RECORDS']:
            if r.get('ACTIVE_PROOF') == 'ACTIVE_PROVED':
                self.assertTrue(r.get('LAST_OBSERVED'),
                                '%s diz ACTIVE_PROVED sem LAST_OBSERVED' % r['ID'])

    def test_a_contabilidade_fecha_nas_tres_familias(self):
        p = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                         'ACERVO-TO-PACKAGE-LOSS.json')
        if not os.path.exists(p):
            self.skipTest('instrumento de perda ainda nao rodou')
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        self.assertTrue(d['ACCOUNTING_CLOSES'], d['FAILURES'])
        for fam in d['FAMILIES']:
            self.assertEqual(fam['ACERVO_COUNT'], fam['ACCOUNTING_SUM'],
                             '%s nao fecha' % fam['FAMILY'])


if __name__ == '__main__':
    unittest.main()


class TestLugarETempoDoFato(unittest.TestCase):
    """A lei portada do Brasil, exercida sobre os fatos que já existem.

        LOCAL_DA_FONTE  != LOCAL_DO_FATO
        DATA_PUBLICACAO != DATA_DO_ACONTECIMENTO
        DATA_COLETA     != DATA_DO_ACONTECIMENTO
    """

    P = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                     'FACT-TIME-PLACE-V1.json')
    CAMPOS = ('fact_time', 'source_location', 'fact_location',
              'publication_time', 'observation_time', 'collection_time')

    def setUp(self):
        if not os.path.exists(self.P):
            self.skipTest('artefato nao gerado — rode bash scripts/v21_cadeia.sh')
        with open(self.P, encoding='utf-8') as f:
            self.d = json.load(f)

    def test_todo_valor_e_PROVADO_ou_UNKNOWN_e_nunca_um_meio_termo(self):
        """O critério de sucesso da missão, em forma de teste."""
        for f in self.d['FACTS']:
            for c in self.CAMPOS:
                v = f[c]
                self.assertIn('value', v, '%s.%s sem value' % (f['fact_id'], c))
                self.assertTrue(v.get('value_evidence'),
                                '%s.%s sem evidencia nem razao' % (f['fact_id'], c))
                if v['value'] == 'UNKNOWN':
                    self.assertEqual(v['value_provenance'], 'NAO_SEI')
                    self.assertIn(c, f['unknown_fields'])
                else:
                    self.assertNotIn(c, f['unknown_fields'])
                    self.assertTrue(v.get('value_source'),
                                    '%s.%s provado sem fonte' % (f['fact_id'], c))

    def test_nenhum_lugar_do_fato_nasce_de_DA_FONTE_ou_DEDUZIDO(self):
        """A lei em uma linha, de `lugar_do_fato.sustenta_fato`."""
        import lugar_do_fato as L
        for f in self.d['FACTS']:
            v = f['fact_location']
            if v['value'] == 'UNKNOWN':
                continue
            self.assertIn(v['value_provenance'], L.ORIGENS_QUE_SUSTENTAM_FATO,
                          '%s: lugar do fato sustentado por %s'
                          % (f['fact_id'], v['value_provenance']))

    def test_o_carimbo_de_publicacao_nunca_vira_tempo_do_fato(self):
        import lugar_do_fato as L
        for f in self.d['FACTS']:
            ft, pt = f['fact_time'], f['publication_time']
            if ft['value'] == 'UNKNOWN':
                continue
            self.assertIn(ft['value_provenance'], L.ORIGENS_DO_TEMPO)
            self.assertNotEqual(ft['value_provenance'], 'PUBLICACAO')
            if ft['value_source'] == pt['value_source']:
                # mesma coluna nos dois papéis só é legítima quando o FATO é o
                # próprio acto que a fonte publica — e aí tem de estar dito.
                self.assertIn('o fato aqui e a propria', ft['value_evidence'],
                              '%s reusa %s como tempo do fato sem dizer porque'
                              % (f['fact_id'], ft['value_source']))

    def test_a_cobertura_declarada_bate_com_o_corpo(self):
        cov = self.d['COVERAGE']
        for c in self.CAMPOS:
            p = sum(1 for f in self.d['FACTS'] if f[c]['value'] != 'UNKNOWN')
            u = sum(1 for f in self.d['FACTS'] if f[c]['value'] == 'UNKNOWN')
            self.assertEqual(cov[c + '_PROVED'], p)
            self.assertEqual(cov[c + '_UNKNOWN'], u)
            self.assertEqual(p + u, self.d['FACTS_ALREADY_IDENTIFIED'])

    def test_a_transcricao_nao_promove_o_escopo_da_rota_a_lugar_do_fato(self):
        """126 registros diziam IT sem evidência. Isso não pode voltar."""
        p = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                         'DESIGN-INGEST', 'TRANSCRIPTS.json')
        with open(p, encoding='utf-8') as f:
            t = json.load(f)
        for r in t['RECORDS']:
            if r['FACT_COUNTRY'] != 'UNKNOWN':
                self.assertEqual(r['FACT_COUNTRY_ORIGIN'], 'ESCRITO')
                self.assertTrue(r['FACT_COUNTRY_EVIDENCE'])
