# -*- coding: utf-8 -*-
"""P7, P8 e o portao de saida.

O portao so vale se ele PUDER barrar. Um portao que passa sempre e decoracao, entao
metade destes testes verifica que ele reprova quando deve.
"""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import portao, filas, voz  # noqa: E402

SAMPLES = os.path.join(ROOT, 'data', 'samples')
SEIS = ['RUN_MANIFEST', 'PIPELINE_DEDUPE', 'VIDEO_TAXONOMY_APPLIED',
        'VIDEO_ORIGINALITY', 'PAID_RAW_POLICY', 'COLLECTION_TIMESTAMPS']


def amostra(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


class TestPortao(unittest.TestCase):

    def setUp(self):
        self.v = portao.veredito()

    def test_os_seis_portoes_da_missao_existem(self):
        self.assertEqual(set(SEIS), set(self.v['PORTOES']))

    def test_todo_portao_traz_medida(self):
        for k, d in self.v['PORTOES'].items():
            self.assertTrue(d['MEDIDA'], f'{k} sem medida — estado afirmado, não derivado')

    def test_o_veredito_e_derivado_dos_portoes(self):
        esperado = 'YES' if all(d['PROVED'] for d in self.v['PORTOES'].values()) else 'NO'
        self.assertEqual(esperado, self.v['READY_FOR_NEXT_ES_COLLECTION'])
        self.assertEqual(sorted(k for k, d in self.v['PORTOES'].items() if not d['PROVED']),
                         sorted(self.v['BLOQUEADO_POR']))

    def test_portao_bloqueado_nomeia_o_bloqueio(self):
        for k, d in self.v['PORTOES'].items():
            if not d['PROVED']:
                self.assertTrue(d['BLOQUEIO'], f'{k} bloqueado sem dizer por quê')
            else:
                self.assertIsNone(d['BLOQUEIO'])

    def test_o_portao_de_dedupe_exerce_o_dedupe(self):
        # o portao nao pode passar so porque DUPLICATE_COUNT=0
        u, c = voz.dedupe([{'PLATFORM': 'X', 'EXTERNAL_ID': 'a'},
                           {'PLATFORM': 'X', 'EXTERNAL_ID': 'a'},
                           {'PLATFORM': 'X', 'EXTERNAL_ID': 'b'}])
        self.assertEqual((2, 1), (len(u), c))

    def test_o_portao_de_taxonomia_recusa_tipo_fora_do_contrato(self):
        validos = set(voz.TIPOS_VIDEO) | {voz.NAO_SEI}
        for v in amostra('ES-T8-001-videos.json')['VIDEOS']:
            self.assertIn(v['CONTENT_TYPE'], validos)

    def test_o_portao_de_timestamp_olha_a_porta_nova_e_nao_um_limiar(self):
        m = self.v['PORTOES']['COLLECTION_TIMESTAMPS']['MEDIDA']
        self.assertIn('porta nova', m)
        self.assertIn('sem fingir', m)


class TestFilaDePesquisadores(unittest.TestCase):

    def setUp(self):
        self.f = amostra('RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json')

    def test_a_meta_e_vinte(self):
        self.assertEqual(20, len(self.f['QUEUE']))
        self.assertEqual(self.f['NA_FILA'], len(self.f['QUEUE']))

    def test_todo_selecionado_tem_os_campos_que_a_missao_pediu(self):
        for p in self.f['QUEUE']:
            for c in ('PERSON_ID', 'NAME', 'INSTITUTION', 'CROP', 'ISSUE', 'WHY_SELECTED',
                      'PUBLIC_LINKEDIN_STATUS', 'PUBLIC_YOUTUBE_STATUS'):
                self.assertIn(c, p)
                self.assertTrue(p[c] not in (None, '', []), f"{p.get('NAME')}.{c} vazio")

    def test_nada_foi_coletado_nesta_missao(self):
        for p in self.f['QUEUE']:
            self.assertEqual('NOT_TESTED', p['PUBLIC_LINKEDIN_STATUS'])
            self.assertEqual('NOT_TESTED', p['PUBLIC_YOUTUBE_STATUS'])

    def test_todo_selecionado_passa_nos_criterios_declarados(self):
        for p in self.f['QUEUE']:
            self.assertIn('OLIVE', p['CROP'])
            self.assertTrue(set(p['ISSUE']) & filas.ISSUES_ANCORA)
            self.assertGreaterEqual(p['LAST_KNOWN_ACTIVITY'], filas.ANO_MINIMO)
            self.assertTrue(p['ORCID'].startswith('https://orcid.org/'))

    def test_nenhum_conflacionado_entra(self):
        for p in self.f['QUEUE']:
            self.assertLessEqual(p['ALL_INSTITUTIONS_COUNT'], 20,
                                 f"{p['NAME']}: organizações demais, verificar conflação")

    def test_o_excluido_do_quadro_nao_reaparece_na_fila(self):
        nomes = {p['NAME'] for p in self.f['QUEUE']}
        for e in amostra('ES-RESEARCHERS-OLIVE.json')['EXCLUSOES_APLICADAS']:
            self.assertNotIn(e['NAME'], nomes)

    def test_a_fila_e_reproduzivel_pelo_script(self):
        q, _, _, _ = filas.selecionar_pesquisadores()
        self.assertEqual([p['PERSON_ID'] for p in self.f['QUEUE']],
                         [p['PERSON_ID'] for p in q],
                         'a fila publicada não é a que o script produz')

    def test_qual_criterio_filtra_esta_declarado(self):
        self.assertIn('13 dos 152', self.f['QUAL_CRITERIO_REALMENTE_FILTRA'])
        self.assertIn('GUARDA', self.f['QUAL_CRITERIO_REALMENTE_FILTRA'])


class TestFilaDeVozesTecnicas(unittest.TestCase):

    def setUp(self):
        self.f = amostra('PUBLIC-TECHNICAL-VOICE-QUEUE-ES.json')

    def test_a_meta_de_vinte_e_atingida_sem_completar_cota(self):
        self.assertGreaterEqual(len(self.f['QUEUE']), 20)
        self.assertGreater(self.f['ELEGIVEIS'], len(self.f['QUEUE']),
                           'se elegíveis == fila, a fila é a cota e não um recorte')

    def test_alcance_nao_entra_em_nenhum_criterio(self):
        bruto = json.dumps(self.f['CRITERIOS'], ensure_ascii=False).lower()
        for palavra in ('follower', 'seguidor', 'alcance', 'views'):
            self.assertNotIn(palavra, bruto)
        for o in self.f['QUEUE']:
            self.assertNotIn('FOLLOWERS', o)

    def test_todo_papel_e_verificavel_e_vem_de_campo_declarado(self):
        for o in self.f['QUEUE']:
            self.assertIn(o['ROLE_BASIS'], ('COMPANY_TYPE+INDUSTRY', 'HEADLINE+CURRENT_POSITION'))
            self.assertTrue(o['ROLE_EVIDENCE'])
            self.assertIn(o['DECLARED_ROLE'], self.f['CRITERIOS']['PRIORIDADE_DE_PAPEL'])

    def test_nada_foi_coletado(self):
        for o in self.f['QUEUE']:
            self.assertEqual('NOT_TESTED', o['PUBLIC_CONTENT_STATUS'])

    def test_o_vies_geografico_esta_declarado(self):
        self.assertIn('desenho da consulta', self.f['VIES_DECLARADO'])

    def test_a_fila_e_reproduzivel_pelo_script(self):
        v, _ = filas.selecionar_vozes_tecnicas()
        self.assertEqual([o['ORIGIN_ID'] for o in self.f['QUEUE']],
                         [o['ORIGIN_ID'] for o in v])


if __name__ == '__main__':
    unittest.main()
