# -*- coding: utf-8 -*-
"""Fechamento do casco — o patch de uma linha.

A rodada anterior deixou exatamente um bloqueador: R-H6-FIELD-VOICE usava
ENTITY_KIND = 'PERSON_CREATOR | FARM_BUSINESS' quando o vocabulario canonico
exige FARM_BUSINESS_ENTITY.

Estas provas medem o novo export e provam que nada mais mudou junto — o diff
contra a testemunha anterior tem UMA linha.

Zero rede.
"""
import gzip
import hashlib
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from v8_receptor_ready import (  # noqa: E402
    CREATOR_ENTITY_KIND, OITO_ESTADOS, PAYLOAD_CANONICO, SUBRECEPTORES,
    campo, fatiar, logica, markup,
)
from v8_receptor_closeout import (  # noqa: E402
    CROPMAP, INDEX_GZ, SHAS, SUPPORT, abrir, medir,
)

IMPL = os.path.join(ROOT, 'data', 'implementation')
with open(os.path.join(IMPL, 'V8-RECEPTOR-CLOSEOUT.json'), encoding='utf-8') as f:
    CLOSE = json.load(f)
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


class TestOBloqueadorFinal(unittest.TestCase):

    def test_FINAL_FIELD_VOICE_ENTITY_KIND_CANONICAL(self):
        self.assertEqual(V['FIELD_VOICE_ENTITY_KIND_CANONICAL'], 'PASS')
        self.assertEqual(M['ENTITY_KIND']['DRIFT'], [])
        self.assertEqual(M['ENTITY_KIND']['R-H6-FIELD-VOICE'],
                         ['FARM_BUSINESS_ENTITY', 'PERSON_CREATOR'])
        self.assertEqual(campo(CAM, 'R-H6-FIELD-VOICE', 'ENTITY_KIND'),
                         "'PERSON_CREATOR | FARM_BUSINESS_ENTITY'")

    def test_os_dois_receptores_de_H6_falam_a_mesma_lingua(self):
        self.assertEqual(M['ENTITY_KIND']['R-H6-FIELD-VOICE'],
                         M['ENTITY_KIND']['R-H6-CREATOR'])
        self.assertEqual(sorted(CREATOR_ENTITY_KIND),
                         M['ENTITY_KIND']['R-H6-FIELD-VOICE'])

    def test_FARM_BUSINESS_abreviado_sumiu_como_valor_estrutural(self):
        """Nenhum FARM_BUSINESS que nao seja FARM_BUSINESS_ENTITY."""
        import re
        sobrou = re.findall(r'FARM_BUSINESS(?!_ENTITY)', CAM)
        self.assertEqual(sobrou, [], 'FARM_BUSINESS abreviado ainda no casco')

    def test_o_receptor_de_voz_continua_com_o_resto_do_contrato(self):
        r = POR_ID['R-H6-FIELD-VOICE']
        self.assertEqual(r['HOSE_ID'], 'H6')
        self.assertEqual(r['PARENT_HOSE_ID'], 'H6')
        self.assertEqual(r['DISPLAY_LABEL'], 'H6 · CAMPO')
        self.assertEqual(r['CANONICAL_PAYLOAD_TYPE'], 'FIELD_VOICE_OBSERVATION')
        self.assertEqual(r['LOAD_STATE'], 'NOT_STARTED')


class TestUmaLinhaESoUma(unittest.TestCase):
    """A prova de que nada mais entrou de carona."""

    def test_o_diff_tem_uma_linha_trocada(self):
        d = M['DIFF_CONTRA_TESTEMUNHA_ANTERIOR']
        self.assertEqual(d['LINHAS_ALTERADAS'], 2, 'uma removida e uma adicionada')
        removida = [l for l in d['LINHAS'] if l.startswith('-')]
        adicionada = [l for l in d['LINHAS'] if l.startswith('+')]
        self.assertEqual(len(removida), 1)
        self.assertEqual(len(adicionada), 1)
        self.assertIn("'PERSON_CREATOR | FARM_BUSINESS'", removida[0])
        self.assertIn("'PERSON_CREATOR | FARM_BUSINESS_ENTITY'", adicionada[0])

    def test_sete_bytes_a_mais_e_o_tamanho_de_ENTITY(self):
        d = M['DIFF_CONTRA_TESTEMUNHA_ANTERIOR']
        self.assertEqual(d['BYTES_A_MAIS'], 7)
        self.assertEqual(len('_ENTITY'), 7)

    def test_support_e_cropmap_nao_mudaram(self):
        """SHA identico ao export anterior: so o index foi tocado."""
        self.assertEqual(SHAS['SUPPORT'],
                         '8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe')
        self.assertEqual(SHAS['CROPMAP'],
                         'a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8')
        for caminho, sha in ((SUPPORT, SHAS['SUPPORT']), (CROPMAP, SHAS['CROPMAP'])):
            with open(caminho, 'rb') as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), sha)


class TestNaoRegressao(unittest.TestCase):

    def test_FINAL_H1_H9_PASS(self):
        self.assertEqual(V['HOSES_WITH_COMPLETE_RECEIVER'], 9)
        for hose, esperados in PAYLOAD_CANONICO.items():
            v = V['HOSES'][hose]
            self.assertEqual(v['VERDICT'], 'PASS', '%s: %s' % (hose, v['MISSING']))
            declarados = [p.strip() for p in v['CANONICAL_PAYLOAD_TYPE'].split('|')]
            self.assertEqual(sorted(declarados), sorted(esperados))

    def test_FINAL_SUBRECEPTORS_PASS(self):
        self.assertEqual(V['SUBRECEPTOR_HOSE_ID_CANONICAL'], 'PASS')
        self.assertEqual(V['DISPLAY_LABEL_SEPARATE'], 'PASS')
        self.assertEqual(V['PARENT_HOSE_ID_STRUCTURAL'], 'PASS')
        for rid, esp in SUBRECEPTORES.items():
            r = POR_ID[rid]
            self.assertEqual(r['HOSE_ID'], esp['HOSE'])
            self.assertEqual(r['PARENT_HOSE_ID'], esp['PARENT'])
            self.assertEqual(r['DISPLAY_LABEL'], esp['LABEL'])
            self.assertEqual(r['CANONICAL_PAYLOAD_TYPE'], esp['PAYLOAD'])
        self.assertIn('hoseId: r.hose', CAM)
        self.assertIn('parentHoseId: r.parent || null', CAM)
        self.assertNotIn('hoseId: r.displayLabel', CAM)

    def test_FINAL_SOURCE_LANGUAGE_UNKNOWN(self):
        self.assertEqual(V['SOURCE_LANGUAGE_UNKNOWN_GLOBAL'], 'PASS')
        for rid in ('R-H7-SCIENTIFIC-PUBLICATION', 'R-H6-FIELD-VOICE'):
            self.assertEqual(campo(CAM, rid, 'SOURCE_LANGUAGE'), "'UNKNOWN'")
        self.assertIn("|| 'unknown'",
                      M['SOURCE_LANGUAGE']['R-H9-CONTENT-ENTITY']['EXPRESSAO'])
        for rid, v in M['SOURCE_LANGUAGE'].items():
            self.assertFalse(v['CAI_EM_TRACO'], rid)

    def test_FINAL_NO_DEAD_HANDLERS(self):
        self.assertEqual(V['DEAD_HANDLERS'], 0)
        self.assertEqual(M['HANDLERS_MORTOS'], [])

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
        self.assertEqual(pernas['FIELD_HISTORICAL']['INDEPENDENCE_STATE'], 'DEPENDENT')
        self.assertEqual(pernas['FIELD_HISTORICAL']['DEPENDENCY_RELATION'],
                         'SOURCE_DEPENDENCY')
        self.assertIn('SINGLE SIGNAL · 1 FAMÍLIA', CAM)

    def test_handlers_de_original_e_traducao(self):
        self.assertIn('{{ drawer.showOriginal }}', MK)
        self.assertIn('{{ drawer.showTranslation }}', MK)

    def test_componentes_preservados(self):
        for chave in ('ACTION_TYPE_CANONICAL', 'ACTION_MAP_OBJECT_ID', 'TIMELINE_TYPED',
                      'CROP_MAP_GUARD', 'GITHUB_PROVENANCE', 'SUPABASE_PROVENANCE',
                      'NO_FRONTEND_SECRET'):
            self.assertEqual(V[chave], 'PASS', chave)
        self.assertEqual(len(M['TIMELINE']['CAMPOS']), 9)
        self.assertEqual(set(M['LOAD_STATES']['DECLARADOS']), set(OITO_ESTADOS))

    def test_H6_creator_preservado(self):
        r = POR_ID['R-H6-CREATOR']
        self.assertEqual(r['HOSE_ID'], 'H6')
        self.assertIsNone(r['PARENT_HOSE_ID'])
        for valor in ('FROM_ATTENTION_OBJECT', 'FROM_CROP_REGION_SEARCH'):
            self.assertIn(valor, CAM)

    def test_todos_os_vereditos_sao_PASS(self):
        """O fechamento: nenhum FAIL sobrou na medicao."""
        falhas = [k for k, v in V.items()
                  if isinstance(v, str) and v == 'FAIL']
        self.assertEqual(falhas, [])


class TestRuntimeSeparado(unittest.TestCase):

    def test_FINAL_NO_DUPLICATE_RECEPTOR_LOGIC_IN_SUPPORT_JS(self):
        """Nao pode haver duas fontes de verdade para R-H6-FIELD-VOICE."""
        self.assertTrue(M['CASCO']['SUPPORT_E_RUNTIME_NAO_LOGICA'])
        self.assertIn('GENERATED from dc-runtime', SUP)
        for marca in ('const receptor', 'CONV_LEGS', "'EV-0001'", 'R-H6-FIELD-VOICE',
                      'FIELD_VOICE_OBSERVATION', 'ENTITY_KIND'):
            self.assertNotIn(marca, SUP, 'support.js contem %s' % marca)
        # e a unica definicao vive no bloco data-dc-script do index
        self.assertIn('class Component extends DCLogic', CAM)
        self.assertEqual(CAM.count("id: 'R-H6-FIELD-VOICE'"), 1)


class TestOrfaos(unittest.TestCase):

    def test_FINAL_NO_ORPHANS(self):
        self.assertEqual(ORFAOS['SUMMARY']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'], 0)
        self.assertEqual(ORFAOS['SUMMARY']['OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO'], 0)

    def test_nenhum_receptor_com_drift_de_helper(self):
        estados = {o.get('CASCO_RECEPTOR_STATE') for o in ORFAOS['OUTPUTS']}
        self.assertNotIn('PRESENT_HELPER_DRIFT', estados)
        self.assertNotIn('ABSENT', estados)

    def test_nenhuma_classificacao_mudou_em_nenhuma_rodada(self):
        self.assertEqual(ORFAOS['SUMMARY']['CLASS_COUNTS'], {
            'SUBRECEPTOR_OF_EXISTING_HOSE': 21,
            'AUXILIARY_RECEPTOR_REQUIRED': 8,
            'NOT_CANONICAL': 5,
            'DEPRECATED': 1,
        })

    def test_o_historico_das_quatro_medicoes_esta_preservado(self):
        h = ORFAOS['TWO_DIFFERENT_NUMBERS']['HISTORICO']
        for marca in ('index (10)', 'index (11)', 'index (12)', 'closeout'):
            self.assertIn(marca, h)


class TestTestemunha(unittest.TestCase):

    def test_o_gz_devolve_os_bytes_originais(self):
        with open(INDEX_GZ, 'rb') as f:
            bruto = gzip.decompress(f.read())
        self.assertEqual(len(bruto), SHAS['INDEX_BYTES'])
        self.assertEqual(hashlib.sha256(bruto).hexdigest(), SHAS['INDEX'])

    def test_as_seis_testemunhas_coexistem(self):
        canonico = os.path.join(ROOT, 'casco', 'canonical')
        for nome in ('SINTONIA-EAME-PILOT-V7.html',
                     'SINTONIA-EAME-V8-RECEPTOR-CANDIDATE.html',
                     'SINTONIA-EAME-V8-DATA-READY.html',
                     'SINTONIA-EAME-V8-FINAL.html',
                     os.path.join('deploy-v8-receptor-ready', 'deploy-index.html.gz'),
                     os.path.join('deploy-v8-closeout', 'deploy-index.html.gz')):
            self.assertTrue(os.path.exists(os.path.join(canonico, nome)), nome)

    def test_um_medidor_so_para_as_duas_testemunhas(self):
        """Dois medidores poderiam divergir e parecer que o casco melhorou."""
        import inspect
        from v8_receptor_ready import medir as base
        self.assertIn('fontes', inspect.signature(base).parameters)

    def test_as_nove_telas_continuam(self):
        self.assertEqual(set(M['CASCO']['TELAS']),
                         {'home', 'radar', 'obj', 'acervo', 'fontes',
                          'relatorios', 'eame', 'lib', 'config'})

    def test_o_medidor_nao_toca_a_rede(self):
        import ast
        with open(os.path.join(ROOT, 'scripts', 'v8_receptor_closeout.py'),
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
