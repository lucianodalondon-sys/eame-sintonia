# -*- coding: utf-8 -*-
"""Micro-reauditoria final — casco de deploy.

Mede os tres bloqueadores que restavam do index (12) e prova que nenhum PASS
anterior regrediu.

Formato novo da testemunha: este export nao e um HTML unico empacotado. E uma
pasta `deploy/` com markup e logica em index.html, o runtime em support.js e o
mapa em crop-map.js. O index fica GZIPADO porque neste ambiente o antivirus
prende o arquivo depois da escrita — ha prova de que o gz devolve os bytes
originais.

Zero rede.
"""
import gzip
import hashlib
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from v8_receptor_ready import (  # noqa: E402
    CREATOR_ENTITY_KIND, INDEX_GZ, OITO_ESTADOS, PAYLOAD_CANONICO, SHA_INDEX,
    SHA_SUPPORT, SHA_CROPMAP, SUBRECEPTORES, SUPPORT, CROPMAP,
    abrir, campo, fatiar, logica, markup, medir,
)

IMPL = os.path.join(ROOT, 'data', 'implementation')
with open(os.path.join(IMPL, 'V8-RECEPTOR-READY.json'), encoding='utf-8') as f:
    READY = json.load(f)
with open(os.path.join(IMPL, 'ORPHAN-INTELLIGENCE-OUTPUTS.json'), encoding='utf-8') as f:
    ORFAOS = json.load(f)

IDX, SUP, MAPJS = abrir()
CAM = logica(IDX)
MK = markup(IDX)
TELAS = fatiar(MK)
M = medir()
V = M['VERDICTS']
POR_ID = {r['RECEPTOR_ID']: r for r in M['RECEPTORES_DECLARADOS']}
POR_HOSE = {r['HOSE_ID']: r for r in M['RECEPTORES_DECLARADOS']
            if r['PARENT_HOSE_ID'] is None}


class TestOsTresBloqueadores(unittest.TestCase):

    def test_FINAL_HELPER_HOSE_ID_CANONICAL(self):
        """hoseId sai de r.hose, nao mais de r.displayLabel."""
        self.assertTrue(M['HELPER']['HOSE_ID_CANONICO'])
        self.assertFalse(M['HELPER']['HOSE_ID_DO_DISPLAY_LABEL'])
        self.assertIn('hoseId: r.hose', CAM)
        self.assertNotIn('hoseId: r.displayLabel', CAM)
        for rid, esp in SUBRECEPTORES.items():
            self.assertEqual(POR_ID[rid]['HOSE_ID'], esp['HOSE'])
            self.assertIn(POR_ID[rid]['HOSE_ID'], PAYLOAD_CANONICO)
        self.assertEqual(V['SUBRECEPTOR_HOSE_ID_CANONICAL'], 'PASS')

    def test_FINAL_DISPLAY_LABEL_SEPARATE(self):
        """O rotulo continua existindo — em campo proprio."""
        self.assertEqual(V['DISPLAY_LABEL_SEPARATE'], 'PASS')
        self.assertIn('displayLabel: r.displayLabel || r.hose', CAM)
        for rid, esp in SUBRECEPTORES.items():
            self.assertEqual(POR_ID[rid]['DISPLAY_LABEL'], esp['LABEL'])
        self.assertIn('{{ r.displayLabel }}', MK)

    def test_FINAL_PARENT_HOSE_ID_STRUCTURAL(self):
        """Campo proprio, e nao mais uma frase dentro de note."""
        self.assertEqual(V['PARENT_HOSE_ID_STRUCTURAL'], 'PASS')
        self.assertIn('parentHoseId: r.parent || null', CAM)
        self.assertFalse(M['HELPER']['PARENT_HOSE_ID_NO_NOTE'])
        self.assertNotIn("PARENT_HOSE_ID · ' + r.parent", CAM)
        # e chega ao usuario como linha de campo, nao como prosa
        self.assertTrue(M['HELPER']['PARENT_HOSE_ID_COMO_LINHA_DE_CAMPO'])
        for rid, esp in SUBRECEPTORES.items():
            self.assertEqual(POR_ID[rid]['PARENT_HOSE_ID'], esp['PARENT'])

    def test_FINAL_SCIENCE_SOURCE_LANGUAGE_UNKNOWN(self):
        v = M['SOURCE_LANGUAGE']['R-H7-SCIENTIFIC-PUBLICATION']
        self.assertTrue(v['CAI_EM_UNKNOWN'])
        self.assertFalse(v['CAI_EM_TRACO'])
        self.assertEqual(campo(CAM, 'R-H7-SCIENTIFIC-PUBLICATION', 'SOURCE_LANGUAGE'),
                         "'UNKNOWN'")

    def test_FINAL_FIELD_VOICE_SOURCE_LANGUAGE_UNKNOWN(self):
        v = M['SOURCE_LANGUAGE']['R-H6-FIELD-VOICE']
        self.assertTrue(v['CAI_EM_UNKNOWN'])
        self.assertFalse(v['CAI_EM_TRACO'])
        self.assertEqual(campo(CAM, 'R-H6-FIELD-VOICE', 'SOURCE_LANGUAGE'), "'UNKNOWN'")

    def test_FINAL_H9_SOURCE_LANGUAGE_UNKNOWN(self):
        v = M['SOURCE_LANGUAGE']['R-H9-CONTENT-ENTITY']
        self.assertTrue(v['CAI_EM_UNKNOWN'])
        self.assertIn("|| 'unknown'", v['EXPRESSAO'])

    def test_nenhum_payload_textual_cai_em_traco(self):
        self.assertEqual(V['SOURCE_LANGUAGE_UNKNOWN_GLOBAL'], 'PASS')
        for rid, v in M['SOURCE_LANGUAGE'].items():
            self.assertFalse(v['CAI_EM_TRACO'], rid)


class TestEntityKind(unittest.TestCase):
    """A checagem literal que o briefing pediu — sem corrigir por inferencia."""

    def test_o_vocabulario_canonico_tem_autoridade_declarada(self):
        with open(os.path.join(ROOT, 'data', 'supabase',
                               'SUPABASE-CANONICAL-SCHEMA.json'), encoding='utf-8') as f:
            schema = json.load(f)
        self.assertEqual(schema['VOCABULARIES']['creator_entity_kind'],
                         list(CREATOR_ENTITY_KIND))
        # e field_voice_observation.entity_kind usa exatamente esse tipo
        tab = {t['name']: t for t in schema['TABLES']}['field_voice_observation']
        col = {c['name']: c for c in tab['columns']}['entity_kind']
        self.assertEqual(col['type'], 'creator_entity_kind')

    def test_FARM_BUSINESS_e_alias_declarado_e_nunca_enum(self):
        """A unica autoridade que menciona FARM_BUSINESS o marca como ALIAS."""
        with open(os.path.join(ROOT, 'data', 'supabase',
                               'SUPABASE-CANONICAL-SCHEMA.json'), encoding='utf-8') as f:
            schema = json.load(f)
        entrada = next(a for a in schema['UI_ALIAS_MAP']['MAP']
                       if a['CANONICAL'] == 'FARM_BUSINESS_ENTITY')
        self.assertEqual(entrada['UI_ALIAS_INDEX11'], 'FARM_BUSINESS')
        self.assertNotIn('FARM_BUSINESS', CREATOR_ENTITY_KIND)

    def test_FIELD_VOICE_ENTITY_KIND_DRIFT(self):
        """FAIL medido: FIELD_VOICE usa FARM_BUSINESS; H6 usa FARM_BUSINESS_ENTITY.

        Nao sao equivalentes por inferencia. O vocabulario canonico exige
        FARM_BUSINESS_ENTITY, e FARM_BUSINESS so existe no repositorio como alias
        de apresentacao declarado.
        """
        self.assertEqual(V['FIELD_VOICE_ENTITY_KIND_CANONICAL'], 'FAIL')
        self.assertEqual(M['ENTITY_KIND']['DRIFT'], ['FARM_BUSINESS'])
        self.assertEqual(M['ENTITY_KIND']['R-H6-CREATOR'],
                         ['FARM_BUSINESS_ENTITY', 'PERSON_CREATOR'])
        self.assertEqual(M['ENTITY_KIND']['R-H6-FIELD-VOICE'],
                         ['FARM_BUSINESS', 'PERSON_CREATOR'])

    def test_voices_ja_usa_o_nome_canonico(self):
        """O que ESTA certo: a lista visivel de vozes ja corrigiu."""
        self.assertIn("kind: 'ENTITY_KIND · FARM_BUSINESS_ENTITY'", CAM)


class TestNaoRegressao(unittest.TestCase):

    def test_FINAL_H1_H9_NO_REGRESSION(self):
        self.assertEqual(V['HOSES_WITH_COMPLETE_RECEIVER'], 9)
        for hose, esperados in PAYLOAD_CANONICO.items():
            v = V['HOSES'][hose]
            self.assertEqual(v['VERDICT'], 'PASS', '%s: %s' % (hose, v['MISSING']))
            declarados = [p.strip() for p in v['CANONICAL_PAYLOAD_TYPE'].split('|')]
            self.assertEqual(sorted(declarados), sorted(esperados))

    def test_H6_preservado(self):
        r = POR_ID['R-H6-CREATOR']
        self.assertEqual(r['HOSE_ID'], 'H6')
        self.assertIsNone(r['PARENT_HOSE_ID'])
        self.assertIn('ENTRY_PATH', CAM)
        for valor in ('FROM_ATTENTION_OBJECT', 'FROM_CROP_REGION_SEARCH'):
            self.assertIn(valor, CAM)

    def test_FINAL_NO_DEAD_HANDLERS(self):
        self.assertEqual(V['DEAD_HANDLERS'], 0)
        self.assertEqual(M['HANDLERS_MORTOS'], [])
        self.assertNotIn('{{ openDrawer }}', MK)

    def test_FINAL_DRAWER_9_OF_9(self):
        self.assertEqual(V['EVIDENCE_DRAWER_HOSES_COVERED'], 9)
        self.assertEqual(M['GAVETA']['HOSES'],
                         ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9'])

    def test_convergencia_preservada(self):
        self.assertEqual(V['RADAR_CONVERGENCE_PARITY'], 'PASS')
        self.assertEqual(M['CONVERGENCIA']['RADAR'], M['CONVERGENCIA']['OBJ'])
        self.assertTrue(M['CONVERGENCIA']['CONTAGEM_DERIVADA'])
        pernas = {p['SIGNAL_FAMILY']: p for p in M['CONVERGENCIA']['PERNAS']}
        self.assertEqual(pernas['TERRITORIAL']['INDEPENDENCE_STATE'], 'INDEPENDENT')
        self.assertEqual(pernas['FIELD_HISTORICAL']['DEPENDENCY_RELATION'],
                         'SOURCE_DEPENDENCY')
        self.assertIn('SINGLE SIGNAL · 1 FAMÍLIA', CAM)

    def test_acao_timeline_proveniencia_mapa_preservados(self):
        for chave in ('ACTION_TYPE_CANONICAL', 'ACTION_MAP_OBJECT_ID', 'TIMELINE_TYPED',
                      'GITHUB_PROVENANCE', 'SUPABASE_PROVENANCE', 'CROP_MAP_GUARD',
                      'NO_FRONTEND_SECRET'):
            self.assertEqual(V[chave], 'PASS', chave)
        self.assertEqual(len(M['TIMELINE']['CAMPOS']), 9)

    def test_os_oito_estados_de_carga_continuam(self):
        self.assertEqual(set(M['LOAD_STATES']['DECLARADOS']), set(OITO_ESTADOS))

    def test_handlers_de_original_e_traducao_vivos(self):
        self.assertIn('{{ drawer.showOriginal }}', MK)
        self.assertIn('{{ drawer.showTranslation }}', MK)


class TestOrfaos(unittest.TestCase):

    def test_FINAL_NO_ORPHANS(self):
        self.assertEqual(ORFAOS['SUMMARY']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'], 0)
        self.assertEqual(ORFAOS['SUMMARY']['OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO'], 0)

    def test_nenhuma_classificacao_mudou(self):
        self.assertEqual(ORFAOS['SUMMARY']['CLASS_COUNTS'], {
            'SUBRECEPTOR_OF_EXISTING_HOSE': 21,
            'AUXILIARY_RECEPTOR_REQUIRED': 8,
            'NOT_CANONICAL': 5,
            'DEPRECATED': 1,
        })


class TestTestemunha(unittest.TestCase):

    def test_o_gz_devolve_os_bytes_originais(self):
        """O index e guardado comprimido; o SHA registrado e o do original."""
        with open(INDEX_GZ, 'rb') as f:
            bruto = gzip.decompress(f.read())
        self.assertEqual(len(bruto), 372418)
        self.assertEqual(hashlib.sha256(bruto).hexdigest(), SHA_INDEX)

    def test_support_e_cropmap_conferem(self):
        for caminho, sha in ((SUPPORT, SHA_SUPPORT), (CROPMAP, SHA_CROPMAP)):
            with open(caminho, 'rb') as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), sha,
                                 os.path.basename(caminho))

    def test_support_js_e_runtime_e_nao_uma_segunda_logica(self):
        """Duas copias da logica divergiriam. Nao ha duas."""
        self.assertTrue(M['CASCO']['SUPPORT_E_RUNTIME_NAO_LOGICA'])
        self.assertIn('GENERATED from dc-runtime', SUP)
        self.assertNotIn('const receptor', SUP)
        self.assertNotIn("'EV-0001'", SUP)
        self.assertIn('class Component extends DCLogic', CAM)

    def test_as_cinco_testemunhas_coexistem(self):
        canonico = os.path.join(ROOT, 'casco', 'canonical')
        for nome in ('SINTONIA-EAME-PILOT-V7.html',
                     'SINTONIA-EAME-V8-RECEPTOR-CANDIDATE.html',
                     'SINTONIA-EAME-V8-DATA-READY.html',
                     'SINTONIA-EAME-V8-FINAL.html'):
            self.assertTrue(os.path.exists(os.path.join(canonico, nome)), nome)
        self.assertTrue(os.path.exists(INDEX_GZ))

    def test_as_nove_telas_continuam(self):
        self.assertEqual(set(M['CASCO']['TELAS']),
                         {'home', 'radar', 'obj', 'acervo', 'fontes',
                          'relatorios', 'eame', 'lib', 'config'})

    def test_o_medidor_nao_toca_a_rede(self):
        import ast
        with open(os.path.join(ROOT, 'scripts', 'v8_receptor_ready.py'),
                  encoding='utf-8') as f:
            arvore = ast.parse(f.read())
        proibidos = {'requests', 'urllib', 'http', 'socket', 'httpx', 'subprocess'}
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for a in no.names:
                    self.assertNotIn(a.name.split('.')[0], proibidos)
            elif isinstance(no, ast.ImportFrom) and no.module:
                self.assertNotIn(no.module.split('.')[0], proibidos)


if __name__ == '__main__':
    unittest.main()
