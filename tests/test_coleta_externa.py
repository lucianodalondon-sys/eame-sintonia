# -*- coding: utf-8 -*-
"""A REGRA DE COLETA EXTERNA so vale se o codigo e o dado a sustentarem.

Estes testes existem para impedir que a lista de campos encolha, que a chave de dedupe
vire texto, que a identidade seja derivada do conteudo, e que um numero publicado
sobreviva a uma correcao sem ser corrigido junto.
"""
import json, os, re, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import voz  # noqa: E402


def amostra(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


def regra():
    with open(os.path.join(ROOT, 'docs', 'regras', 'REGRA-DE-COLETA-EXTERNA-EAME.md'),
              encoding='utf-8') as f:
        return f.read()


# A lista da regra, transcrita aqui de proposito. Se scripts/voz.py encolher, os dois
# lados divergem e o teste reprova — que e exatamente o ponto.
CAMPOS_DA_REGRA = [
    'SOURCE_ID', 'ORIGIN_ID', 'CHANNEL_ID', 'CONTENT_ID', 'PLATFORM', 'EXTERNAL_ID', 'URL',
    'TITLE', 'DESCRIPTION', 'PUBLICATION_DATE', 'CAPTURE_DATE', 'CHANNEL_NAME',
    'DECLARED_AUTHOR', 'DECLARED_ROLE', 'ORGANIZATION', 'COUNTRY', 'LANGUAGE', 'DURATION',
    'VIEWS', 'LIKES', 'COMMENTS_COUNT', 'TRANSCRIPT', 'TRANSCRIPT_LANGUAGE', 'CAPTION_SOURCE',
    'CROP', 'ISSUE', 'PRODUCT', 'MOLECULE', 'FACT_LOCATION', 'SOURCE_LOCATION',
    'RUN_ID', 'EVIDENCE_PATH',
]


class TestContratoDeCampos(unittest.TestCase):

    def test_a_lista_nao_encolheu(self):
        self.assertEqual(CAMPOS_DA_REGRA, voz.CAMPOS_VIDEO,
                         'scripts/voz.py divergiu da lista de campos da regra')

    def test_registro_vazio_tem_todas_as_chaves(self):
        r = voz.registro_vazio()
        self.assertEqual(set(CAMPOS_DA_REGRA), set(r))
        self.assertTrue(all(v == voz.NAO_SEI for v in r.values()),
                        'campo ausente vira NAO SEI, nunca vazio nem None')

    def test_todo_video_publicado_tem_todas_as_chaves(self):
        vids = amostra('ES-T8-001-videos.json')['VIDEOS']
        for v in vids:
            faltando = set(CAMPOS_DA_REGRA) - set(v)
            self.assertEqual(set(), faltando, f"{v.get('EXTERNAL_ID')} sem: {faltando}")

    def test_campo_em_nao_sei_integral_e_declarado_com_motivo(self):
        d = amostra('ES-T8-001-videos.json')
        for c in d['CAMPOS_EM_NAO_SEI_INTEGRAL']:
            self.assertIn(c, d['PORQUE_ESSES_CAMPOS_FALTAM'],
                          f'{c} esta vazio em todos os registros e ninguem explicou por que')

    def test_cobertura_bate_com_os_registros(self):
        d = amostra('ES-T8-001-videos.json')
        vids = d['VIDEOS']
        for campo, v in d['FIELD_COVERAGE'].items():
            self.assertEqual(v['TOTAL'], len(vids))
            real = sum(1 for r in vids if r.get(campo) not in (voz.NAO_SEI, None, ''))
            self.assertEqual(v['DECLARED'], real, f'cobertura de {campo} nao bate')


class TestOrigemNaoEConteudo(unittest.TestCase):

    def test_origens_e_conteudos_sao_contagens_diferentes(self):
        for nome in ('ES-T8-001-videos.json', 'ES-T8-002-posts.json'):
            d = amostra(nome)['ORIGIN_NAO_E_CONTENT']
            self.assertLess(d['ORIGINS'], d['CONTENTS'],
                            f'{nome}: origens iguais a conteudos e sinal de colapso das entidades')

    def test_origens_do_video_batem_com_os_registros(self):
        d = amostra('ES-T8-001-videos.json')
        vids = d['VIDEOS']
        self.assertEqual(d['ORIGIN_NAO_E_CONTENT']['CONTENTS'], len(vids))
        self.assertEqual(d['ORIGIN_NAO_E_CONTENT']['ORIGINS'],
                         len({v['ORIGIN_ID'] for v in vids}))

    def test_origin_id_nunca_e_content_id(self):
        for v in amostra('ES-T8-001-videos.json')['VIDEOS']:
            self.assertNotEqual(v['ORIGIN_ID'], v['CONTENT_ID'])
            self.assertTrue(v['ORIGIN_ID'].startswith('YOUTUBE:'))


class TestDedupeEstrutural(unittest.TestCase):

    def test_a_chave_e_estrutural_e_nao_texto(self):
        a = {'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': 'aaa', 'TITLE': 'mesmo titulo'}
        b = {'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': 'bbb', 'TITLE': 'mesmo titulo'}
        unicos, colaps = voz.dedupe([a, b])
        self.assertEqual(2, len(unicos), 'titulo igual nao pode colapsar dois registros')
        self.assertEqual(0, colaps)

    def test_mesmo_id_colapsa(self):
        a = {'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': 'aaa', 'TITLE': 'x'}
        b = {'PLATFORM': 'YOUTUBE', 'EXTERNAL_ID': 'aaa', 'TITLE': 'y'}
        unicos, colaps = voz.dedupe([a, b])
        self.assertEqual(1, len(unicos))
        self.assertEqual(1, colaps)

    def test_o_corpus_de_posts_declara_o_que_colapsou(self):
        d = amostra('ES-T8-002-posts.json')['DEDUPE']
        self.assertEqual(d['RAW'] - d['UNIQUE'], d['COLLAPSED'])
        self.assertGreater(d['COLLAPSED'], 0,
                           'se nada colapsou, ou a chave esta errada ou o corpus mudou')
        self.assertEqual('POST_ID', d['KEY'])

    def test_videos_sem_duplicata_continuam_sem_duplicata(self):
        vids = amostra('ES-T8-001-videos.json')['VIDEOS']
        ids = [v['EXTERNAL_ID'] for v in vids]
        self.assertEqual(len(ids), len(set(ids)))


class TestIdentidadeNaoSaiDoConteudo(unittest.TestCase):

    def test_o_post_nao_declara_lugar(self):
        for p in amostra('ES-T8-002-posts.json')['POSTS'][:50]:
            self.assertTrue(p['FACT_LOCATION'].startswith('NÃO SEI'),
                            'o texto de um post nao pode virar FACT_LOCATION')

    def test_identidade_e_conteudo_moram_em_arquivos_diferentes(self):
        d = amostra('ES-T8-002-posts.json')
        self.assertIn('ES-VOICE-LINKEDIN.json', d['IDENTIDADE_FICA_NO_OUTRO_ARQUIVO'])
        self.assertNotIn('DECLARED_ROLE', d['POSTS'][0],
                         'papel nao pode viver no registro de conteudo')

    def test_fact_location_de_video_so_quando_nomeado(self):
        for v in amostra('ES-T8-001-videos.json')['VIDEOS']:
            if v['FACT_LOCATION'] != voz.NAO_SEI:
                self.assertEqual('NOMEADO_NO_TEXTO', v.get('FACT_LOCATION_RULE'))

    def test_source_location_nunca_vira_fact_location(self):
        for v in amostra('ES-T8-001-videos.json')['VIDEOS'][:50]:
            self.assertEqual('plataforma global', v['SOURCE_LOCATION'])
            self.assertNotEqual(v['SOURCE_LOCATION'], v['FACT_LOCATION'])


class TestTranscricao(unittest.TestCase):

    def setUp(self):
        self.t = amostra('ES-T8-001-transcricoes.json')

    def test_original_e_traducao_sao_campos_separados(self):
        for t in self.t['TRANSCRIPTS']:
            self.assertIn('TRANSCRIPT_ORIGINAL', t)
            self.assertIn('TRANSLATION', t)
            self.assertIsNone(t['TRANSLATION'],
                              'null significa NAO TRADUZIDO; nunca copiar o original para ca')

    def test_como_foi_obtida_esta_registrado(self):
        for t in self.t['TRANSCRIPTS']:
            self.assertTrue(t['CAPTION_SOURCE'])

    def test_transcricao_vazia_e_estado_e_nao_ausencia(self):
        d = amostra('ES-T8-001-videos.json')['TRANSCRIPT_STATE']
        self.assertEqual(d['REQUESTED'], d['RETURNED'] + d['REQUESTED_EMPTY'])
        vazios = [v for v in amostra('ES-T8-001-videos.json')['VIDEOS']
                  if v['CAPTION_SOURCE'] == 'REQUESTED_EMPTY']
        self.assertEqual(d['REQUESTED_EMPTY'], len(vazios))

    def test_o_total_de_caracteres_bate(self):
        self.assertEqual(self.t['TOTAL_CHARS'],
                         sum(len(t['TRANSCRIPT_ORIGINAL']) for t in self.t['TRANSCRIPTS']))


class TestRotaPagaEVersionada(unittest.TestCase):

    def test_toda_amostra_de_rota_paga_tem_run_id(self):
        for nome in ('ES-T8-001-videos.json', 'ES-T8-001-transcricoes.json',
                     'ES-T8-002-posts.json'):
            self.assertTrue(amostra(nome).get('RUN_ID'), f'{nome} sem RUN_ID')

    def test_todo_registro_carrega_o_run_id(self):
        d = amostra('ES-T8-001-videos.json')
        for v in d['VIDEOS']:
            self.assertEqual(d['RUN_ID'], v['RUN_ID'])

    def test_a_excecao_a_d003_esta_declarada(self):
        d = amostra('ES-T8-001-videos.json')
        self.assertIn('D-003', d['PORQUE_ESTE_ARQUIVO_E_VERSIONADO'])
        self.assertIn('nao replicavel', d['PORQUE_ESTE_ARQUIVO_E_VERSIONADO'])
        self.assertIn('D-003', regra())


class TestCorrecaoDoConcorrente(unittest.TestCase):
    """O numero caiu de 54 para 26. As duas causas precisam continuar separadas."""

    def setUp(self):
        self.c = amostra('ES-COMPETITOR-VOICE.json')

    def test_as_duas_causas_estao_separadas(self):
        d = self.c['CORRECAO_2026-08-29']['duas_causas_separadas']
        self.assertIn('DEDUPE_ESTRUTURAL', d)
        self.assertIn('FUNCIONARIO_NAO_E_CANAL', d)

    def test_os_numeros_novos_batem_com_a_tabela(self):
        self.assertEqual(self.c['INDUSTRY_POSTS'], sum(x['POSTS'] for x in self.c['BY_ORIGIN']))
        self.assertEqual(self.c['INDUSTRY_ORIGINS'], len(self.c['BY_ORIGIN']))
        self.assertEqual(self.c['CORPUS_POSTS'], amostra('ES-T8-002-posts.json')['DEDUPE']['UNIQUE'])

    def test_o_numero_antigo_nao_sobrevive_no_documento(self):
        with open(os.path.join(ROOT, 'docs', 'descoberta', 'CAMADA-DE-VOZ-ESPANHA.md'),
                  encoding='utf-8') as f:
            t = f.read()
        self.assertNotIn('14 origens de indústria de proteção de cultivos, 54 posts', t)
        self.assertIn('26 posts', t)


class TestARegraCitaOQueJaExiste(unittest.TestCase):
    """A regra manda nao recomecar do zero. Entao ela precisa apontar para o que ja existe."""

    def test_aponta_para_as_regras_anteriores(self):
        t = regra()
        for doc in ('MODELO-DE-IDENTIDADE-EAME.md', 'REGUA-DE-CHANGE-EVENT-EAME.md',
                    'REGUA-DE-ALERTA-EAME.md', 'POLITICA-DE-CHAVES-DESCARTAVEIS.md'):
            self.assertIn(doc, t, f'a regra nao referencia {doc} e estaria reescrevendo do zero')
            self.assertTrue(os.path.exists(os.path.join(ROOT, 'docs', 'regras', doc)))

    def test_os_quatro_estados_de_video_x_field_existem(self):
        t = regra()
        for e in ('LEADS', 'COINCIDES', 'LAGS', 'NO_RELIABLE_SIGNAL'):
            self.assertIn(e, t)

    def test_baseline_nunca_e_no_change(self):
        self.assertIn('Nunca `NO_CHANGE`', regra())


if __name__ == '__main__':
    unittest.main()


class TestBaselinePorCanal(unittest.TestCase):
    """A regra manda dar baseline por CANAL, nao por camada."""

    def setUp(self):
        self.b = amostra('ES-T8-001-baseline-canais.json')

    def test_todo_canal_tem_baseline(self):
        vids = amostra('ES-T8-001-videos.json')['VIDEOS']
        canais_no_video = {v['CHANNEL_ID'] for v in vids}
        canais_no_baseline = {c['CHANNEL_ID'] for c in self.b['BASELINE']}
        self.assertEqual(canais_no_video, canais_no_baseline,
                         'todo canal que sobreviveu ao discovery precisa de baseline')

    def test_primeira_observacao_nunca_e_no_change(self):
        for c in self.b['BASELINE']:
            self.assertEqual('BASELINE_ESTABLISHED', c['VERSION_STATE'])
            self.assertNotEqual('NO_CHANGE', c['VERSION_STATE'])

    def test_os_sete_eventos_da_regra_estao_declarados(self):
        for e in ('NEW_VIDEO', 'NEW_TOPIC', 'NEW_RESEARCHER_ACTIVITY', 'NEW_COMPETITOR_CLAIM',
                  'NEW_TECHNICAL_DISCUSSION', 'NEW_PRODUCT_MENTION', 'NEW_REGION_MENTION'):
            self.assertIn(e, self.b['EVENTOS_A_DETECTAR'])

    def test_as_contagens_batem(self):
        self.assertEqual(self.b['CHANNELS'], len(self.b['BASELINE']))
        self.assertEqual(self.b['CONTENTS'], sum(c['CONTENT_COUNT'] for c in self.b['BASELINE']))
        self.assertEqual(self.b['CONTENTS'], len(amostra('ES-T8-001-videos.json')['VIDEOS']))

    def test_content_ids_do_canal_sao_os_videos_dele(self):
        vids = amostra('ES-T8-001-videos.json')['VIDEOS']
        for c in self.b['BASELINE'][:20]:
            esperado = sorted(v['EXTERNAL_ID'] for v in vids if v['CHANNEL_ID'] == c['CHANNEL_ID'])
            self.assertEqual(esperado, sorted(c['CONTENT_IDS']))
