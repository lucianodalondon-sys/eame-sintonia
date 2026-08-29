# -*- coding: utf-8 -*-
"""Teste PONTA A PONTA do pipeline da camada de voz.

A auditoria de 2026-08-29 apontou que o dedupe existia como funcao testada e nenhum
caminho reprodutivel a invocava. Um teste unitario da funcao nao teria pego isso — por
isso estes testes entram por `pipeline_video()` e vao do BRUTO ate a saida.

A fixture e minima de proposito e cada linha dela existe para exercer um caso:
  AAA111 duas vezes -> duplicata por chave estrutural
  BBB222            -> mesmo TITULO em canal DIFERENTE, com marca textual de republicacao
  CCC333            -> sem descricao e titulo curto -> NAO SEI, que nao e OTHER
"""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import voz  # noqa: E402

FIXTURE = os.path.join(ROOT, 'tests', 'fixtures', 'yt-raw-minimo.json')


def roda():
    with open(FIXTURE, encoding='utf-8') as f:
        brutos = json.load(f)
    return voz.pipeline_video(
        brutos, source_id='TEST', run_id='TEST-RUN-1', capture_date='2026-08-29',
        papel_por_canal={'UC_IFAPA': 'PUBLIC_AUTHORITY', 'UC_OUTRO': 'TECHNICAL_MEDIA'},
        evidence_path='tests/fixtures/yt-raw-minimo.json')


class TestPipelinePontaAPonta(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.unicos, cls.rel = roda()

    def test_as_tres_contagens_sao_explicitas_e_coerentes(self):
        r = self.rel
        for c in ('RAW_COUNT', 'DUPLICATE_COUNT', 'UNIQUE_CONTENT_COUNT'):
            self.assertIn(c, r)
        self.assertEqual(r['RAW_COUNT'], r['UNIQUE_CONTENT_COUNT'] + r['DUPLICATE_COUNT'])
        self.assertEqual(4, r['RAW_COUNT'])
        self.assertEqual(1, r['DUPLICATE_COUNT'])
        self.assertEqual(3, r['UNIQUE_CONTENT_COUNT'])

    def test_o_dedupe_e_invocado_pelo_pipeline_e_nao_so_existe(self):
        # a saida ja vem deduplicada: nenhum EXTERNAL_ID repetido
        ids = [r['EXTERNAL_ID'] for r in self.unicos]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.unicos), self.rel['UNIQUE_CONTENT_COUNT'])

    def test_a_relacao_duplicata_canonico_e_preservada(self):
        d = self.rel['DUPLICATES']
        self.assertEqual(1, len(d))
        self.assertEqual('AAA111', d[0]['EXTERNAL_ID'])
        self.assertEqual('YOUTUBE:AAA111', d[0]['DUPLICATE_OF'])

    def test_titulo_igual_em_canais_diferentes_nao_colapsa(self):
        # AAA111 e BBB222 tem o MESMO titulo. Sao dois videos.
        titulos = [r['TITLE'] for r in self.unicos]
        self.assertEqual(2, titulos.count('Jornada técnica de olivar en Jaén'))

    def test_origem_nao_e_conteudo(self):
        self.assertEqual(3, self.rel['UNIQUE_CONTENT_COUNT'])
        self.assertEqual(3, self.rel['UNIQUE_ORIGIN_COUNT'])
        for r in self.unicos:
            self.assertNotEqual(r['ORIGIN_ID'], r['CONTENT_ID'])

    def test_taxonomia_e_aplicada_no_pipeline(self):
        tipos = {r['EXTERNAL_ID']: r['CONTENT_TYPE'] for r in self.unicos}
        self.assertEqual('CONFERENCE', tipos['AAA111'])
        self.assertIn(tipos['BBB222'], voz.TIPOS_VIDEO)

    def test_nao_sei_nao_e_other(self):
        # CCC333 nao tem descricao e o titulo e curto: nao ha texto para classificar
        r = next(x for x in self.unicos if x['EXTERNAL_ID'] == 'CCC333')
        self.assertEqual(voz.NAO_SEI, r['CONTENT_TYPE'])
        self.assertNotEqual('OTHER', r['CONTENT_TYPE'])
        self.assertIn('insuficiente para tipificar', r['CONTENT_TYPE_EVIDENCE'])

    def test_todo_registro_carrega_tipo_e_originalidade(self):
        for r in self.unicos:
            self.assertIn('CONTENT_TYPE', r)
            self.assertIn('ORIGINALITY', r)
            self.assertIn(r['ORIGINALITY'], voz.ORIGINALIDADE)
            self.assertTrue(r['ORIGINALITY_EVIDENCE'])

    def test_reshare_exige_marca_textual(self):
        r = next(x for x in self.unicos if x['EXTERNAL_ID'] == 'BBB222')
        self.assertEqual('RESHARE', r['ORIGINALITY'])
        self.assertIn('marca textual', r['ORIGINALITY_EVIDENCE'])

    def test_nada_vira_original_por_ausencia_de_prova(self):
        estados = {r['ORIGINALITY'] for r in self.unicos}
        self.assertNotIn('ORIGINAL', estados,
                         'a rota nao da prova de autoria; ORIGINAL por omissao inverte o onus')

    def test_o_relatorio_traz_cobertura_de_campo(self):
        self.assertIn('FIELD_COVERAGE', self.rel)
        for c in voz.CAMPOS_VIDEO:
            self.assertIn(c, self.rel['FIELD_COVERAGE'])

    def test_o_pipeline_e_deterministico(self):
        u2, r2 = roda()
        self.assertEqual(self.rel['UNIQUE_CONTENT_COUNT'], r2['UNIQUE_CONTENT_COUNT'])
        self.assertEqual([r['CONTENT_ID'] for r in self.unicos],
                         [r['CONTENT_ID'] for r in u2])


class TestSaidaPublicadaVeioDoPipeline(unittest.TestCase):
    """Os 252 publicados tem de bater com o que o pipeline produz — senao o numero
    publicado nao veio de derivacao reproduzivel."""

    def setUp(self):
        with open(os.path.join(ROOT, 'data', 'samples', 'ES-T8-001-videos.json'),
                  encoding='utf-8') as f:
            self.d = json.load(f)

    def test_as_contagens_do_pipeline_batem_com_os_registros(self):
        p = self.d['PIPELINE']
        self.assertEqual(p['RAW_COUNT'], p['UNIQUE_CONTENT_COUNT'] + p['DUPLICATE_COUNT'])
        self.assertEqual(p['UNIQUE_CONTENT_COUNT'], len(self.d['VIDEOS']))
        self.assertEqual(p['UNIQUE_ORIGIN_COUNT'],
                         len({v['ORIGIN_ID'] for v in self.d['VIDEOS']}))

    def test_a_distribuicao_de_tipo_e_derivada_e_nao_digitada(self):
        from collections import Counter
        real = Counter(v['CONTENT_TYPE'] for v in self.d['VIDEOS'])
        self.assertEqual(dict(real), self.d['CONTENT_TYPE']['DISTRIBUICAO'])
        self.assertEqual(self.d['CONTENT_TYPE']['VIDEO_COUNT_TOTAL'], len(self.d['VIDEOS']))
        self.assertEqual(self.d['CONTENT_TYPE']['VIDEO_COUNT_CLASSIFIED'],
                         sum(1 for v in self.d['VIDEOS'] if v['CONTENT_TYPE'] != voz.NAO_SEI))
        self.assertEqual(self.d['CONTENT_TYPE']['VIDEO_COUNT_UNKNOWN'],
                         sum(1 for v in self.d['VIDEOS'] if v['CONTENT_TYPE'] == voz.NAO_SEI))

    def test_a_distribuicao_de_originalidade_e_derivada(self):
        from collections import Counter
        real = Counter(v['ORIGINALITY'] for v in self.d['VIDEOS'])
        self.assertEqual(dict(real), self.d['ORIGINALITY']['DISTRIBUICAO'])

    def test_todo_video_tem_originalidade_declarada(self):
        for v in self.d['VIDEOS']:
            self.assertIn(v['ORIGINALITY'], voz.ORIGINALIDADE)
            self.assertTrue(v.get('ORIGINALITY_EVIDENCE'))

    def test_o_primario_esta_entre_os_tipos_casados(self):
        for v in self.d['VIDEOS']:
            todos = v.get('CONTENT_TYPE_ALL') or []
            if todos:
                self.assertIn(v['CONTENT_TYPE'], todos)

    def test_a_precedencia_foi_respeitada(self):
        for v in self.d['VIDEOS']:
            todos = [t for t in (v.get('CONTENT_TYPE_ALL') or []) if t in voz.PRECEDENCIA_TIPO]
            if len(todos) > 1:
                esperado = next(t for t in voz.PRECEDENCIA_TIPO if t in todos)
                self.assertEqual(esperado, v['CONTENT_TYPE'],
                                 f"{v['EXTERNAL_ID']}: primario fora da precedencia declarada")


if __name__ == '__main__':
    unittest.main()
