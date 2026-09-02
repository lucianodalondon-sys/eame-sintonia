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


class TestVideoXField(unittest.TestCase):
    """A regra manda declarar um dos quatro estados e nao fabricar antecipacao."""

    def setUp(self):
        self.x = amostra('ES-X-VOICE-FIELD.json')

    def test_declara_um_dos_quatro_estados(self):
        self.assertIn(self.x['VIDEO_x_FIELD_STATE'],
                      ('LEADS', 'COINCIDES', 'LAGS', 'NO_RELIABLE_SIGNAL'))

    def test_o_rho_mais_alto_nao_virou_lead(self):
        r = self.x['RESULTADO']
        maior = max(abs(v) for k, v in r.items() if k.startswith('rho'))
        self.assertLess(maior, 0.648,
                        'algum coeficiente passou do valor critico: o estado precisa ser reavaliado')
        self.assertEqual('NO_RELIABLE_SIGNAL', self.x['VIDEO_x_FIELD_STATE'])
        self.assertIn('0,648', self.x['PORQUE_NAO_E_LEAD'])

    def test_o_denominador_corrige_o_artefato_de_rota(self):
        a = self.x['ARTEFATO_DE_ROTA_ENCONTRADO']
        self.assertIn('NAO mede atencao', a['leitura'])
        for linha in self.x['SERIE']:
            self.assertGreaterEqual(linha['VIDEOS_NO_ANO'], 8,
                                    'ano com denominador pequeno demais entrou na serie')
            self.assertAlmostEqual(linha['SHARE'],
                                   linha['VIDEOS_DE_REPILO'] / linha['VIDEOS_NO_ANO'], places=3)

    def test_o_achado_geografico_nao_foi_apagado(self):
        self.assertIn('ES-VOICE-x-REGUA', self.x['O_QUE_ISSO_NAO_SIGNIFICA'])


class TestVideoXScience(unittest.TestCase):

    def setUp(self):
        self.x = amostra('ES-X-VOICE-SCIENCE.json')

    def test_nome_igual_nao_confirma_identidade(self):
        self.assertEqual(0, self.x['RESULTADO_POR_PESSOA']['CONFIRMADOS_POR_SEGUNDO_CAMPO'])
        for l in self.x['RESULTADO_POR_PESSOA']['LINKS']:
            if l['MATCH_STATE'] == 'CANDIDATE_NAME_ONLY':
                self.assertIsNone(l['SECOND_FIELD'])

    def test_o_metodo_frouxo_foi_rejeitado_e_nao_publicado(self):
        m = self.x['RESULTADO_POR_INSTITUICAO']['CASAMENTO_FROUXO_POR_TOKEN']
        self.assertEqual('METODO_REJEITADO', m['VEREDITO'])
        self.assertGreaterEqual(len(m['FALSOS_POSITIVOS_MEDIDOS']), 3)

    def test_o_estado_e_not_reached_e_nao_refutado(self):
        self.assertEqual('NOT_REACHED', self.x['STATE'])
        self.assertIn('nao esta refutada', self.x['VEREDITO'])

    def test_o_que_falta_e_identificador_e_nao_algoritmo(self):
        self.assertIn('ORCID', self.x['O_QUE_FALTA_E_CONCRETO'])
        self.assertIn('nao de um algoritmo de similaridade', self.x['O_QUE_FALTA_E_CONCRETO'])


class TestComentarios(unittest.TestCase):
    """Comentario e util, mas generico nao vira inteligencia e autor nao vira identidade."""

    def setUp(self):
        self.c = amostra('ES-T8-001-comentarios.json')

    def test_os_campos_da_regra_estao_todos(self):
        exigidos = {'COMMENT_ID', 'VIDEO_ID', 'AUTHOR_REFERENCE', 'DATE', 'TEXT',
                    'LIKE_COUNT', 'PARENT_COMMENT_ID', 'SOURCE_ID', 'RUN_ID'}
        for r in self.c['COMMENTS'][:40]:
            self.assertEqual(set(), exigidos - set(r))

    def test_dedupe_por_comment_id_e_nao_por_texto(self):
        d = self.c['DEDUPE']
        self.assertEqual('COMMENT_ID', d['KEY'])
        ids = [r['COMMENT_ID'] for r in self.c['COMMENTS']]
        self.assertEqual(len(ids), len(set(ids)))
        textos = [r['TEXT'] for r in self.c['COMMENTS']]
        self.assertGreater(len(textos), len(set(textos)),
                           'se nenhum texto se repete, a garantia de nao colapsar por texto '
                           'nunca foi exercida neste corpus')

    def test_todo_autor_entra_unverified(self):
        for r in self.c['COMMENTS']:
            self.assertEqual('UNVERIFIED', r['ORIGIN_STATUS'])

    def test_data_relativa_nao_virou_data(self):
        for r in self.c['COMMENTS'][:40]:
            self.assertTrue(r['DATE'].startswith('NÃO SEI'),
                            'tempo relativo nunca pode ser convertido em data')

    def test_generico_nao_conta_como_sinal(self):
        self.assertEqual(self.c['TOTAL'], len(self.c['COMMENTS']))
        real = sum(1 for r in self.c['COMMENTS'] if r['CLASS'] != 'NOT_CLASSIFIED')
        self.assertEqual(self.c['COM_CONTEUDO_CLASSIFICAVEL'], real)
        self.assertLess(real, self.c['TOTAL'],
                        'se tudo foi classificado, a classe NOT_CLASSIFIED virou decorativa')

    def test_a_camada_declara_o_que_nao_e(self):
        d = self.c['O_QUE_ESTA_CAMADA_E']
        self.assertGreater(d['PERGUNTAS'], d['OBSERVACOES_E_RELATOS'])
        self.assertIn('sensor de campo', d['O_QUE_ELA_NAO_E'])


class TestIntegridadeDoIdentificador(unittest.TestCase):
    """A auditoria adversarial de 2026-08-29 achou um id de autor conflacionado dentro do
    quadro publicado, e o proprio arquivo dizia que ele estava fora. Estes testes existem
    para que texto e dado nao voltem a divergir."""

    def setUp(self):
        self.r = amostra('ES-RESEARCHERS-OLIVE.json')

    def test_o_excluido_nao_esta_no_quadro(self):
        nomes = {x['NAME'] for x in self.r['RESEARCHERS']}
        for e in self.r['EXCLUSOES_APLICADAS']:
            self.assertNotIn(e['NAME'], nomes,
                             f"{e['NAME']} esta declarado como excluido E esta na lista")

    def test_o_texto_de_cautela_bate_com_o_dado(self):
        c = self.r['IDENTITY_CAUTION']
        for e in self.r['EXCLUSOES_APLICADAS']:
            self.assertIn(e['NAME'], c,
                          'a cautela precisa nomear quem foi excluido, senao volta a mentir')
        self.assertIn('EXCLUIDO', c)

    def test_nenhum_registro_restante_tem_sinal_de_conflacao(self):
        import statistics
        orgs = [len(x.get('ALL_ORGANIZATIONS') or []) for x in self.r['RESEARCHERS']]
        mediana = statistics.median(orgs)
        # o caso medido tinha 58 contra mediana 2. Um teto de 10x a mediana e folgado
        # e ainda assim teria pego aquele registro.
        self.assertLessEqual(max(orgs), max(10, mediana * 10),
                             'registro com organizacoes demais: verificar conflacao de homonimo')

    def test_todo_pesquisador_tem_ancora_de_identidade(self):
        for x in self.r['RESEARCHERS']:
            self.assertTrue(x.get('ORCID'), f"{x['NAME']} sem ORCID")

    def test_a_contagem_publicada_e_depois_das_exclusoes(self):
        self.assertEqual(self.r['COUNT'], len(self.r['RESEARCHERS']))


class TestDenominadorPublicado(unittest.TestCase):
    """O denominador publicado tem de ser o denominador usado no calculo."""

    def test_o_n_da_correlacao_e_a_interseccao_declarada(self):
        x = amostra('ES-VOICE-x-REGUA.json')['LINKEDIN_POST_ROUTE']
        self.assertEqual(x['n_provincias'], len(x['PROVINCIAS_NA_CORRELACAO']))
        self.assertLess(x['n_provincias'], len(x['mentions_by_province']),
                        'se a tabela e a correlacao tem o mesmo n, a ressalva ficou obsoleta')

    def test_toda_provincia_fora_da_correlacao_tem_motivo(self):
        x = amostra('ES-VOICE-x-REGUA.json')['LINKEDIN_POST_ROUTE']
        fora = set(x['mentions_by_province']) - set(x['PROVINCIAS_NA_CORRELACAO'])
        for p in fora:
            self.assertIn(p, x['PROVINCIAS_EXCLUIDAS'],
                          f'{p} saiu da correlacao sem motivo declarado')

    def test_as_origens_contadas_batem_com_a_tabela(self):
        x = amostra('ES-VOICE-x-REGUA.json')['LINKEDIN_POST_ROUTE']
        self.assertEqual(x['ORIGINS_COUNTED'], sum(x['mentions_by_province'].values()))


class TestAfirmacaoDeOrdemExigeCarimbo(unittest.TestCase):
    """Nada no repositorio registra hora de coleta por camada. Enquanto for assim,
    nenhuma afirmacao de 'X veio antes de Y' pode ser publicada."""

    def test_a_afirmacao_sem_lastro_foi_retirada(self):
        with open(os.path.join(ROOT, 'docs', 'descoberta', 'CAMADA-DE-VOZ-ESPANHA.md'),
                  encoding='utf-8') as f:
            t = f.read()
        self.assertNotIn('antes\n   de qualquer gasto em LinkedIn', t)
        self.assertIn('não é auditável', t)
        self.assertIn('carimbo por camada', t)


CAMPOS_DOC_DA_REGRA = ['DOCUMENT_ID','TITLE','AUTHORS','YEAR','DATE','DOI','INSTITUTION',
                       'CROP','ISSUE','MOLECULE','COUNTRY','REGION_OF_STUDY','DOCUMENT_TYPE',
                       'SOURCE_ID','URL','EVIDENCE_PATH']


class TestCorpusPorDocumento(unittest.TestCase):
    """A secao 7 pede campos POR DOCUMENTO. Antes so existia o agregado."""

    def setUp(self):
        self.c = amostra('ES-T5-002-corpus-documentos.json')

    def test_todo_documento_tem_todos_os_campos_da_regra(self):
        for d in self.c['DOCUMENTS'][:200]:
            self.assertEqual(set(), set(CAMPOS_DOC_DA_REGRA) - set(d))

    def test_document_id_e_unico_e_nunca_ausente(self):
        ids = [d['DOCUMENT_ID'] for d in self.c['DOCUMENTS']]
        self.assertNotIn('NÃO SEI', ids)
        self.assertEqual(len(ids), len(set(ids)))

    def test_crop_e_issue_sao_declarados_pela_consulta(self):
        # sao os temas da busca que trouxe o documento, nao leitura livre do titulo
        for d in self.c['DOCUMENTS'][:200]:
            self.assertIsInstance(d['CROP'], list)
            self.assertIsInstance(d['ISSUE'], list)
            self.assertTrue(d['CROP'] and d['ISSUE'])

    def test_campo_incompleto_tem_motivo_escrito(self):
        for campo, pct in self.c['FIELD_COVERAGE'].items():
            if pct < 50:
                self.assertIn(campo, self.c['CAMPOS_INCOMPLETOS_COM_MOTIVO'],
                              f'{campo} com {pct}% e sem motivo declarado')

    def test_afiliacao_nunca_virou_regiao_de_estudo(self):
        for d in self.c['DOCUMENTS'][:300]:
            self.assertEqual('NÃO SEI', d['REGION_OF_STUDY'])

    def test_os_tipos_nao_cobertos_seguem_declarados(self):
        t = self.c['TIPOS_QUE_A_REGRA_PEDE_E_NAO_EXISTEM_AQUI']
        for tipo in ('technical reports', 'research projects', 'institutional publications',
                     'extension material'):
            self.assertIn(tipo, t)
        self.assertIn('NOT_REACHED', t)

    def test_a_contagem_bate(self):
        self.assertEqual(self.c['COUNT'], len(self.c['DOCUMENTS']))

    def test_o_documento_leva_de_volta_as_pessoas(self):
        # a lacuna que este arquivo fecha: do papel para os autores
        com_autor = [d for d in self.c['DOCUMENTS'] if d['AUTHORS'] != 'NÃO SEI']
        self.assertEqual(len(self.c['DOCUMENTS']), len(com_autor))
        self.assertGreater(self.c['AUTHORS_DISTINCT'], 1000)


class TestAuditoriaPreservada(unittest.TestCase):
    """A auditoria e evidencia como qualquer outra: fica versionada, com o seu proprio
    limite de metodo declarado, e o backlog nao se perde."""

    def setUp(self):
        self.a = amostra('AUDITORIA-REGRA-COLETA-EXTERNA.json')

    def test_o_limite_do_metodo_esta_declarado(self):
        l = self.a['LIMITE_DO_METODO']
        self.assertIn('EM MOVIMENTO', l)
        self.assertIn('defeito meu', l,
                      'auditar alvo movel foi erro de desenho e precisa continuar assumido')

    def test_a_contagem_bate_com_os_achados(self):
        r = self.a['RESULTADO']
        self.assertEqual(r['TOTAL'], len(self.a['ACHADOS']))
        soma = sum(r['POR_STATUS'].values())
        self.assertEqual(r['TOTAL'], soma)

    def test_o_backlog_bate_com_os_nao_atendidos(self):
        na = [f for f in self.a['ACHADOS'] if f['status_final'] == 'NAO_ATENDIDO']
        self.assertEqual(self.a['BACKLOG_ABERTO']['TOTAL_NAO_ATENDIDO'], len(na))
        self.assertEqual(self.a['RESULTADO']['POR_STATUS']['NAO_ATENDIDO'], len(na))

    def test_a_verificacao_corrigiu_nos_dois_sentidos(self):
        r = self.a['RESULTADO']
        self.assertGreater(r['STATUS_CORRIGIDO_NA_VERIFICACAO'], 0,
                           'se a verificacao nunca corrige nada, ela e decorativa')
        # houve refutacao tanto de ATENDIDO falso quanto de lacuna inventada
        refutados = [f for f in self.a['ACHADOS'] if f['refutado']]
        alegados = {f['status_alegado'] for f in refutados}
        self.assertGreater(len(alegados), 1,
                           'a verificacao precisa ter corrigido em mais de uma direcao')

    def test_o_que_foi_fechado_esta_nomeado(self):
        f = self.a['BACKLOG_ABERTO']['FECHADOS_NESTA_SESSAO']
        self.assertGreaterEqual(len(f), 5)


class TestPortaoDeRede(unittest.TestCase):
    """MISSAO 11R — recusa de gateway nao pode virar ausencia de fonte.

    Duas missoes seguidas foram bloqueadas por politica de egresso. O risco nao e o
    bloqueio: e a proxima conta ler "000" e concluir que a fonte morreu, ou que a rota
    precisa ser trocada, ou que falta chave.
    """

    @classmethod
    def setUpClass(cls):
        import rede
        cls.rede = rede
        with open(os.path.join(SAMPLES, 'PORTAO-DE-REDE-ES.json'), encoding='utf-8') as f:
            cls.d = json.load(f)

    def test_o_portao_declara_para_que_serve_cada_host(self):
        """Host recusado sem dizer o que se perde e so um erro; com isso e uma decisao."""
        for host, url, para_que in self.rede.HOSTS:
            with self.subTest(host=host):
                self.assertTrue(para_que.strip(), f'{host} sem PARA_QUE_SERVE')

    def test_os_essenciais_estao_declarados(self):
        for h in ('api.openalex.org', 'pub.orcid.org', 'www.youtube.com', 'api.apify.com'):
            self.assertIn(h, self.rede.ESSENCIAIS)

    def test_o_veredito_e_derivado_dos_essenciais(self):
        """NAO se o essencial cai; nunca digitado."""
        v = {'ESSENCIAIS_RECUSADOS': []}
        self.assertEqual('YES', 'NO' if v['ESSENCIAIS_RECUSADOS'] else 'YES')
        self.assertEqual('NO' if self.d['ESSENCIAIS_RECUSADOS'] else 'YES',
                         self.d['NETWORK_COLLECTION_READY'])

    def test_o_registro_separa_ambiente_de_fonte(self):
        self.assertIn('SOURCE FAILURE != ZERO', self.d['O_QUE_ISTO_NAO_SIGNIFICA'])
        self.assertIn('AMBIENTE', self.d['O_QUE_ISTO_NAO_SIGNIFICA'])

    def test_a_chave_apify_nao_foi_gasta_nem_versionada(self):
        c = self.d['CHAVE_APIFY']
        self.assertFalse(c['USADA'])
        self.assertFalse(c['TOKEN_VERSIONADO'])
        self.assertTrue(c['NAO_E_PROBLEMA_DE_CHAVE'])
        self.assertIn('CONNECT', c['PORQUE_NAO_FOI_USADA'])

    def test_as_filas_continuam_intocadas(self):
        self.assertIn('NOT_TESTED', self.d['ESTADO_DAS_FILAS'])
        for arq in ('RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json',
                    'PUBLIC-TECHNICAL-VOICE-QUEUE-ES.json'):
            with open(os.path.join(SAMPLES, arq), encoding='utf-8') as f:
                for e in json.load(f)['QUEUE']:
                    for c in e:
                        if c.endswith('_STATUS'):
                            self.assertEqual('NOT_TESTED', e[c])


class TestSnapshotHistoricoNaoViraCorrente(unittest.TestCase):
    """O snapshot velho mediu um ambiente que nao existe mais.

    O risco nao e o arquivo estar errado — ele esta certo sobre AQUELE ambiente. O risco
    e alguem ler `NETWORK_COLLECTION_READY = NO` de 2026-08-29 e concluir que a coleta
    de hoje esta bloqueada. Historico e corrente precisam ser distinguiveis por campo,
    nunca por quem leu com atencao.
    """

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(SAMPLES, 'PORTAO-DE-REDE-ES.json'), encoding='utf-8') as f:
            cls.velho = json.load(f)
        with open(os.path.join(SAMPLES, 'PORTAO-DE-REDE-ES-CURRENT.json'), encoding='utf-8') as f:
            cls.atual = json.load(f)

    def test_cada_registro_declara_se_e_historico_ou_corrente(self):
        self.assertEqual('HISTORICO', self.velho['ESTADO_DO_REGISTRO'])
        self.assertEqual('CURRENT', self.atual['ESTADO_DO_REGISTRO'])

    def test_existe_exatamente_um_corrente(self):
        """Dois CURRENT e pior que nenhum: nao da para saber qual manda."""
        correntes = []
        for nome in os.listdir(SAMPLES):
            if not nome.startswith('PORTAO-DE-REDE'):
                continue
            with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
                if json.load(f).get('ESTADO_DO_REGISTRO') == 'CURRENT':
                    correntes.append(nome)
        self.assertEqual(1, len(correntes), f'esperado 1 CURRENT, achei {correntes}')

    def test_o_historico_aponta_para_quem_o_substituiu(self):
        self.assertEqual('PORTAO-DE-REDE-ES-CURRENT', self.velho['SUPERSEDED_BY'])
        self.assertEqual(self.velho['SUPERSEDED_BY'], self.atual['SOURCE_ID'])

    def test_o_historico_diz_em_voz_alta_que_nao_e_o_estado_atual(self):
        aviso = self.velho['NAO_LEIA_COMO_ESTADO_ATUAL']
        self.assertIn('NAO EXISTE MAIS', aviso)
        self.assertIn('PORTAO-DE-REDE-ES-CURRENT', aviso)

    def test_os_dois_ambientes_estao_nomeados_e_sao_diferentes(self):
        self.assertEqual('OLD_ENVIRONMENT', self.velho['AMBIENTE'])
        self.assertEqual('CURRENT_COLLECTION_ENVIRONMENT', self.atual['AMBIENTE'])
        self.assertEqual('BLOCKED', self.velho['STATUS'])
        self.assertEqual('READY', self.atual['STATUS'])

    def test_o_corrente_carrega_o_que_torna_a_medicao_rastreavel(self):
        for campo in ('CAPTURE_DATE', 'HEAD', 'PROXY_STATE', 'HOSTS', 'STATUS',
                      'NETWORK_COLLECTION_READY'):
            self.assertIn(campo, self.atual, f'CURRENT sem {campo}')
        self.assertEqual(40, len(self.atual['HEAD']), 'HEAD nao e um SHA completo')

    def test_o_veredito_do_corrente_e_derivado_e_nao_digitado(self):
        """Mesma lei do portao velho: NO se um essencial cai."""
        self.assertEqual('NO' if self.atual['ESSENCIAIS_RECUSADOS'] else 'YES',
                         self.atual['NETWORK_COLLECTION_READY'])
        self.assertEqual('READY' if self.atual['NETWORK_COLLECTION_READY'] == 'YES'
                         else 'BLOCKED', self.atual['STATUS'])

    def test_o_corrente_nao_se_declara_dono_do_estado_vivo(self):
        self.assertIn('scripts/rede.py', self.atual['QUEM_MANDA'])
        self.assertIn('REGISTRO', self.atual['QUEM_MANDA'])
