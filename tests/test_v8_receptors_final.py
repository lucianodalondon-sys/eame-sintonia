# -*- coding: utf-8 -*-
"""Provas do casco index (12) — o fechamento.

A autoridade e o MODELO CANONICO. O casco e consumidor: se ele chamar uma coisa
de um jeito e o contrato de outro, quem manda e o contrato.

Como nas rodadas anteriores, estas provas TRAVAM A MEDICAO. Quando um item for
corrigido, a prova correspondente reprova — e isso e o comportamento desejado:
obriga a remedir em vez de deixar um veredito velho passar por novo.

Zero rede.
"""
import hashlib
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from v8_receptor_final import (  # noqa: E402
    CASCO12, PAYLOAD_CANONICO, SUBRECEPTORES, OITO_ESTADOS, ACAO_CANONICA,
    LINGUA_FECHADA, PAYLOAD_TEXTUAL, abrir, fatiar, campos_do_receptor,
    valor_do_campo, medir,
)

IMPL = os.path.join(ROOT, 'data', 'implementation')
with open(os.path.join(IMPL, 'V8-RECEPTOR-FINAL.json'), encoding='utf-8') as f:
    FINAL = json.load(f)
with open(os.path.join(IMPL, 'ORPHAN-INTELLIGENCE-OUTPUTS.json'), encoding='utf-8') as f:
    ORFAOS = json.load(f)

MARKUP, CAMADA, ATIVOS = abrir()
TELAS = fatiar(MARKUP)
M = medir()
V = M['VERDICTS']
POR_ID = {r['RECEPTOR_ID']: r for r in M['RECEPTORES_DECLARADOS']}
POR_HOSE = {r['HOSE_ID']: r for r in M['RECEPTORES_DECLARADOS']
            if r['PARENT_HOSE_ID'] is None}


class Base(unittest.TestCase):

    def campos(self, rid):
        return campos_do_receptor(CAMADA, rid)


class TestHosesCanonicas(Base):

    def test_INDEX12_H1_H9_CANONICAL(self):
        """As nove, com HOSE_ID e CANONICAL_PAYLOAD_TYPE literalmente canonicos."""
        self.assertEqual(V['HOSES_WITH_COMPLETE_RECEIVER'], 9)
        for hose, esperados in PAYLOAD_CANONICO.items():
            v = V['HOSES'][hose]
            self.assertEqual(v['VERDICT'], 'PASS', '%s: %s' % (hose, v['MISSING']))
            declarados = [p.strip() for p in v['CANONICAL_PAYLOAD_TYPE'].split('|')]
            self.assertEqual(sorted(declarados), sorted(esperados))

    def test_INDEX12_NO_UI_ALIAS_REQUIRED_FOR_CANONICAL_RECEPTOR(self):
        """Nenhum alias do index (11) sobreviveu como tipo de payload."""
        # Testar o VALOR do payload, nunca o pedaco de texto: 'ISSUE_EXPERT' casa
        # dentro de 'ISSUE_EXPERTISE_PROVED', que e o portao CERTO e tem de ficar.
        # Quarta vez que confundo mencao com uso — daqui em diante, so valor.
        mortos = ['TERRITORIAL_ATTENTION_OBJECT', 'PAID_ACTIVITY_EVIDENCE',
                  'LONGITUDINAL_FIELD_SERIES', 'ISSUE_EXPERT', 'COMPANY_PUBLIC_ACCOUNT',
                  'MULTILINGUAL_CONTENT_REPRESENTATION']
        payloads = set()
        for r in M['RECEPTORES_DECLARADOS']:
            payloads.update(p.strip() for p in r['CANONICAL_PAYLOAD_TYPE'].split('|'))
        for alias in mortos:
            self.assertNotIn(alias, payloads, 'alias %s ainda e payload' % alias)
            self.assertFalse("CANONICAL_PAYLOAD_TYPE · %s'" % alias in CAMADA,
                             'alias %s ainda declarado como payload' % alias)
        # e o portao que contem o alias como substring continua vivo
        self.assertIn('ISSUE_EXPERTISE_PROVED', CAMADA)
        # e os dois OBJECT_TYPE que tinham sido usados como payload voltaram ao lugar
        self.assertEqual(POR_HOSE['H2']['CANONICAL_PAYLOAD_TYPE'], 'REGISTRATION_DEADLINE')
        self.assertEqual(POR_HOSE['H3']['CANONICAL_PAYLOAD_TYPE'],
                         'COMPETITOR_PRODUCT_IDENTITY')

    def test_todo_receptor_tem_o_envelope_completo(self):
        for hose in PAYLOAD_CANONICO:
            r = POR_HOSE[hose]
            for campo in ('RECEPTOR_ID', 'HOSE_ID', 'CANONICAL_PAYLOAD_TYPE',
                          'LOAD_STATE', 'NO_DATA_REASON'):
                self.assertTrue(r.get(campo), '%s sem %s' % (hose, campo))
            self.assertIn(r['LOAD_STATE'], OITO_ESTADOS)
        for chave in ('r.asOf', 'r.pointers', 'r.failClosed', 'r.backend', 'r.prov'):
            self.assertIn(chave, MARKUP, 'envelope sem %s no markup' % chave)

    def test_os_oito_estados_de_carga_continuam_declarados(self):
        self.assertEqual(set(M['LOAD_STATES']['DECLARADOS']), set(OITO_ESTADOS))

    def test_source_clocks_nao_e_mais_H0(self):
        r = POR_ID['R-INFRA-SOURCE-CLOCKS']
        self.assertEqual(r['HOSE_ID'], 'INFRA')
        self.assertNotIn('H0', [x['HOSE_ID'] for x in M['RECEPTORES_DECLARADOS']])


class TestH6(Base):

    def test_INDEX12_H6_RECEIVER_EXISTS(self):
        r = POR_ID['R-H6-CREATOR']
        self.assertEqual(r['HOSE_ID'], 'H6')
        self.assertIsNone(r['PARENT_HOSE_ID'])
        self.assertEqual(V['HOSES']['H6']['VERDICT'], 'PASS')

    def test_INDEX12_H6_THREE_CANONICAL_PAYLOADS(self):
        declarados = [p.strip() for p in
                      POR_ID['R-H6-CREATOR']['CANONICAL_PAYLOAD_TYPE'].split('|')]
        self.assertEqual(sorted(declarados),
                         ['CREATOR_CONTENT_PROFILE', 'FARM_BUSINESS_ENTITY', 'PERSON_CREATOR'])

    def test_H6_entry_path_com_os_dois_valores(self):
        self.assertIn('ENTRY_PATH', self.campos('R-H6-CREATOR'))
        self.assertEqual(M['CREATOR']['ENTRY_PATH_VALORES'],
                         ['FROM_ATTENTION_OBJECT', 'FROM_CROP_REGION_SEARCH'])

    def test_INDEX12_CREATOR_ENTITY_KIND_CANONICAL(self):
        """FARM_BUSINESS_ENTITY no valor estrutural; FARM BUSINESS so no visual."""
        self.assertEqual(V['CREATOR_ENTITY_KIND_CANONICAL'], 'PASS')
        self.assertIn("FIELD('ENTITY_KIND', 'PERSON_CREATOR | FARM_BUSINESS_ENTITY'", CAMADA)
        self.assertIn("FIELD('CONTENT_PROFILE_TYPE', 'CREATOR_CONTENT_PROFILE'", CAMADA)
        # o abreviado nao aparece mais como valor de ENTITY_KIND
        self.assertNotIn("'ENTITY_KIND · FARM_BUSINESS'", CAMADA)

    def test_H6_linha_e_entidade_continuam_separadas(self):
        campos = self.campos('R-H6-CREATOR')
        self.assertIn('ROW_COUNT', campos)
        self.assertIn('ENTITY_COUNT', campos)
        self.assertIn('nunca somam pessoas com negócios agrícolas', CAMADA)


class TestSubreceptores(Base):

    def test_INDEX12_SUBRECEPTOR_HOSE_ID_CANONICAL(self):
        """O campo `hose` do dado e canonico nos tres."""
        for rid, esperado in SUBRECEPTORES.items():
            r = POR_ID[rid]
            self.assertEqual(r['HOSE_ID'], esperado['HOSE'], rid)
            self.assertIn(r['HOSE_ID'], PAYLOAD_CANONICO)
            self.assertEqual(r['CANONICAL_PAYLOAD_TYPE'], esperado['PAYLOAD'])

    def test_INDEX12_PARENT_HOSE_ID_STRUCTURAL(self):
        """FAIL medido: PARENT_HOSE_ID e texto dentro de note, nao campo.

        O helper faz:
            note: ... r.note + ' · PARENT_HOSE_ID · ' + r.parent
        Um adapter que precise do pai teria de fatiar uma frase.
        """
        self.assertFalse(V['PARENT_HOSE_ID_ESTRUTURAL'])
        self.assertTrue(V['PARENT_HOSE_ID_NO_NOTE'])
        self.assertNotIn('parentHoseId', CAMADA)
        self.assertNotIn('{{ r.parentHoseId }}', MARKUP)

    def test_helper_ainda_expoe_display_label_como_hose_id(self):
        """FAIL medido, e nomeado no briefing como reprovacao explicita.

            hoseId: r.displayLabel || r.hose

        Os tres subreceptores definem displayLabel, entao `{{ r.hoseId }}`
        renderiza 'H7 · CIENCIA', 'H2 · PORTFOLIO' e 'H6 · CAMPO'. O HOSE_ID
        canonico existe no dado e NAO e o que o receptor expoe.
        """
        self.assertTrue(V['HELPER_HOSE_ID_VEM_DO_DISPLAY_LABEL'])
        self.assertIn('hoseId: r.displayLabel || r.hose', CAMADA)
        for rid, rotulo in (('R-H7-SCIENTIFIC-PUBLICATION', 'H7 · CIÊNCIA'),
                            ('R-H2-LOCAL-ADAMA-PORTFOLIO', 'H2 · PORTFÓLIO'),
                            ('R-H6-FIELD-VOICE', 'H6 · CAMPO')):
            self.assertEqual(POR_ID[rid]['DISPLAY_LABEL'], rotulo)
        self.assertEqual(V['SUBRECEPTORES_PASS'], 0)

    def test_o_que_esta_certo_nos_subreceptores(self):
        """As duas leis continuam escritas dentro dos receptores."""
        self.assertIn('SCIENTIFIC_PERSON ≠ SCIENTIFIC_PUBLICATION', CAMADA)
        self.assertIn('REGISTRATION_DEADLINE ≠ LOCAL_ADAMA_PORTFOLIO_CONTEXT', CAMADA)
        for campo in ('PUBLICATION_ID', 'TITLE', 'AUTHORS', 'PEER_REVIEWED_STATE'):
            self.assertIn(campo, self.campos('R-H7-SCIENTIFIC-PUBLICATION'))
        for campo in ('REGISTERED_RESPONSE_STATE', 'LABEL_AUTHORIZES_TARGET_STATE'):
            self.assertIn(campo, self.campos('R-H2-LOCAL-ADAMA-PORTFOLIO'))
        for campo in ('OBSERVATION_ID', 'ORIGINAL_TEXT', 'GDPR_TREATMENT_STATE'):
            self.assertIn(campo, self.campos('R-H6-FIELD-VOICE'))


class TestConvergencia(Base):

    def test_INDEX12_RADAR_OBJECT_CONVERGENCE_PARITY(self):
        self.assertEqual(V['RADAR_CONVERGENCE_PARITY'], 'PASS')
        self.assertEqual(M['CONVERGENCIA']['RADAR'], M['CONVERGENCIA']['OBJ'])
        self.assertEqual(len(M['CONVERGENCIA']['OBJ']), 8)

    def test_a_conta_da_convergencia_continua_derivada(self):
        """TERRITORIAL independente + FIELD_HISTORICAL dependente = SINGLE SIGNAL."""
        pernas = {p['SIGNAL_FAMILY']: p for p in M['CONVERGENCIA']['PERNAS']}
        self.assertEqual(pernas['TERRITORIAL']['INDEPENDENCE_STATE'], 'INDEPENDENT')
        self.assertEqual(pernas['FIELD_HISTORICAL']['INDEPENDENCE_STATE'], 'DEPENDENT')
        self.assertEqual(pernas['FIELD_HISTORICAL']['DEPENDENCY_RELATION'],
                         'SOURCE_DEPENDENCY')
        self.assertTrue(M['CONVERGENCIA']['CONTAGEM_DERIVADA'])
        self.assertIn("const independentCount = CONV_LEGS.filter(l => l.independence === "
                      "'INDEPENDENT').length", CAMADA)
        self.assertIn("independentCount >= 2", CAMADA)
        self.assertIn('SINGLE SIGNAL · 1 FAMÍLIA', CAMADA)

    def test_as_duas_telas_mostram_a_mesma_dependencia(self):
        for tela in ('radar', 'obj'):
            self.assertIn('{{ l.dependency }}', TELAS[tela])
            self.assertIn('{{ conv.propositionId }}', TELAS[tela])
            self.assertIn('{{ conv.independentCount }}', TELAS[tela])


class TestHandlers(Base):

    def test_INDEX12_NO_DEAD_HANDLERS(self):
        self.assertEqual(V['DEAD_HANDLERS'], 0)
        self.assertEqual(M['HANDLERS_MORTOS'], [])
        self.assertNotIn('{{ openDrawer }}', MARKUP)

    def test_o_radar_abre_evidencia_pelo_mesmo_fluxo_do_objeto(self):
        for tela in ('radar', 'obj'):
            self.assertIn('{{ l.openEvidence }}', TELAS[tela])
        self.assertIn('drawerRef: { objectId:', CAMADA)


class TestGaveta(Base):

    def test_INDEX12_DRAWER_COVERS_H1_H9(self):
        self.assertEqual(V['EVIDENCE_DRAWER_HOSES_COVERED'], 9)
        self.assertEqual(M['GAVETA']['HOSES'],
                         ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9'])

    def test_as_cinco_evidencias_pedidas_existem_e_diferem(self):
        entradas = dict(M['GAVETA']['ENTRADAS'])
        for eid, hose in (('EV-0001', 'H1'), ('EV-0007', 'H6'), ('EV-0008', 'H7'),
                          ('EV-0009', 'H8'), ('EV-0010', 'H9')):
            self.assertEqual(entradas[eid], hose)
        ev = re.search(r"const EVIDENCE = \{(.*?)\n    \};", CAMADA, re.S).group(1)
        fontes = re.findall(r"sourceId: '(SRC-\d+)'", ev)
        self.assertEqual(len(set(fontes)), 9, 'evidencias diferentes com a mesma fonte')

    def test_a_gaveta_muda_os_cinco_campos(self):
        for chave in ('drawer.objectId', 'drawer.hoseId', 'drawer.evidenceId',
                      'drawer.claim'):
            self.assertIn('{{ %s }}' % chave, MARKUP)
        self.assertIn("{ k: 'SOURCE_ID', v: ev ? ev.sourceId : '—'", CAMADA)

    def test_original_e_traducao_separados_com_handler(self):
        self.assertEqual(M['GAVETA']['HANDLERS'],
                         ['drawer.showOriginal', 'drawer.showTranslation'])
        self.assertIn("showOriginal: () => this.set({ drawerView: 'original' })", CAMADA)
        self.assertIn("showTranslation: () => this.set({ drawerView: 'translation' })", CAMADA)
        self.assertIn('TRADUÇÃO — NÃO SUBSTITUI O ORIGINAL', CAMADA)
        for campo in ('CANONICAL_ENTITY_ID', 'SOURCE_LANGUAGE', 'DISPLAY_LANGUAGE',
                      'TRANSLATION_PROVENANCE'):
            self.assertIn("k: '%s'" % campo, CAMADA)

    def test_a_gaveta_usa_UNKNOWN_e_nao_traco(self):
        self.assertIn("'SOURCE_LANGUAGE · ' + (ev ? ev.lang : 'UNKNOWN')", CAMADA)
        self.assertIn("{ k: 'SOURCE_LANGUAGE', v: ev ? ev.lang : 'UNKNOWN' }", CAMADA)
        self.assertIn('UNKNOWN', M['GAVETA']['LINGUAS'])


class TestAcao(Base):

    def test_INDEX12_ACTION_TYPES_CANONICAL(self):
        self.assertEqual(V['ACTION_TYPE_CANONICAL'], 'PASS')
        self.assertEqual(sorted(M['ACAO']['CANONICOS']), sorted(ACAO_CANONICA))
        self.assertTrue(M['ACAO']['PERSISTE_CANONICO'])
        self.assertIn('actionType: KIND[a.kind].canonical', CAMADA)
        self.assertIn('kind: KIND[a.kind].display', CAMADA)
        self.assertEqual(sorted(M['ACAO']['DISPLAYS']),
                         ['BUSINESS', 'INVESTIGATION', 'SYSTEM'])

    def test_INDEX12_ACTION_OBJECT_ID(self):
        self.assertEqual(V['ACTION_MAP_OBJECT_ID'], 'PASS')
        self.assertIn('objectId: base.id', CAMADA)

    def test_business_decision_sem_evidencia_nao_e_defensavel(self):
        self.assertTrue(M['ACAO']['GUARD_EVIDENCE_BASIS'])
        self.assertIn("(a.kind === 'business' && (!a.basis || !a.basis.length)) "
                      "? 'SEM AÇÃO DEFENSÁVEL AINDA'", CAMADA)
        self.assertIn("'ACTION_TYPE · ' + KIND[a.kind].canonical + ' · EVIDENCE_BASIS VAZIO'",
                      CAMADA)


class TestTimeline(Base):

    def test_INDEX12_TIMELINE_STATES_SEPARATE(self):
        self.assertEqual(V['TIMELINE_STATES_SEPARATE'], 'PASS')
        self.assertIn('STATE_BEFORE', M['TIMELINE']['CAMPOS'])
        self.assertIn('STATE_AFTER', M['TIMELINE']['CAMPOS'])
        self.assertFalse(M['TIMELINE']['SETA_CONCATENADA'])

    def test_INDEX12_TIMELINE_SOURCE_ID_TYPED(self):
        self.assertEqual(V['TIMELINE_SOURCE_ID_TYPED'], 'PASS')
        self.assertIn("k: 'SOURCE_ID'", CAMADA)

    def test_timeline_carrega_os_nove_campos(self):
        for campo in ('EVENT_ID', 'EVENT_TYPE', 'EVENT_AT', 'EVENT_AT_RESOLUTION',
                      'SOURCE_ID', 'OBSERVATION_ID', 'STATE_BEFORE', 'STATE_AFTER',
                      'GAP_REASON'):
            self.assertIn(campo, M['TIMELINE']['CAMPOS'])


class TestLingua(Base):

    def test_INDEX12_SOURCE_LANGUAGE_UNKNOWN_GLOBAL(self):
        """FAIL medido: a regra global vale em 1 dos 3 payloads textuais.

        H9 faz certo — (base.srcLang || 'unknown').toUpperCase(). Os outros dois
        passam null, e FIELD() transforma null em '—'. O briefing nomeou
        exatamente estes dois: SCIENTIFIC_PUBLICATION e FIELD_VOICE_OBSERVATION.
        """
        self.assertEqual(V['SOURCE_LANGUAGE_UNKNOWN_GLOBAL'], 'FAIL')
        lingua = M['SOURCE_LANGUAGE']
        self.assertTrue(lingua['R-H9-CONTENT-ENTITY']['CAI_EM_UNKNOWN'])
        for rid in ('R-H7-SCIENTIFIC-PUBLICATION', 'R-H6-FIELD-VOICE'):
            self.assertTrue(lingua[rid]['CAI_EM_TRACO'],
                            '%s deixou de cair em traco — remedir' % rid)
            self.assertFalse(lingua[rid]['CAI_EM_UNKNOWN'])

    def test_o_traco_vem_do_helper_FIELD(self):
        """A causa e uma linha: null vira '—' por padrao."""
        self.assertIn("const FIELD = (k, v, st) => ({ k, v: v == null ? '—' : v", CAMADA)

    def test_o_vocabulario_fechado_esta_declarado(self):
        self.assertIn("'pt · en · es · fr · it · MULTILINGUAL · UNKNOWN'", CAMADA)
        self.assertEqual(len(LINGUA_FECHADA), 7)

    def test_os_cinco_idiomas_de_interface_continuam(self):
        self.assertIn("const langs = { pt: 'PT', en: 'EN', es: 'ES', it: 'IT', fr: 'FR' }",
                      CAMADA)


class TestMapaEProveniencia(Base):

    def test_INDEX12_CROP_MAP_GUARD_PRESERVED(self):
        self.assertEqual(V['CROP_MAP_GUARD'], 'PASS')
        self.assertTrue(M['MAPA']['GUARD_NO_ASSET'])
        self.assertTrue(M['MAPA']['DECLARA_NAO_DESENHAVEIS'])
        self.assertEqual(M['MAPA']['RESOLUCOES_NOS_PONTOS'], ['NOT_KNOWN'])
        js = next(t for t in ATIVOS.values() if 'pointsjson' in t)
        self.assertIn("points.filter(p => p.GEO_RESOLUTION === 'POINT'", js)
        self.assertIn('LOCALITY_TEXT nunca é geocodificado silenciosamente', js)

    def test_proveniencia_e_agnostica_de_backend(self):
        self.assertEqual(V['GITHUB_PROVENANCE'], 'PASS')
        self.assertEqual(V['SUPABASE_PROVENANCE'], 'PASS')
        self.assertEqual(MARKUP.count('sc-for list="{{ r.prov }}"'), 3)
        self.assertIn("prov: (PROV_ROWS[r.backend] || PROV_ROWS.UNWIRED)", CAMADA)

    def test_nenhum_segredo_no_frontend(self):
        self.assertEqual(V['NO_FRONTEND_SECRET'], 'PASS')
        self.assertEqual(M['PROVENIENCIA']['SEGREDOS'], [])


class TestOrfaos(Base):

    def test_NO_ORPHAN_CANONICAL_INTELLIGENCE(self):
        self.assertEqual(ORFAOS['SUMMARY']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'], 0)

    def test_nenhuma_saida_aponta_para_receptor_ausente(self):
        self.assertEqual(ORFAOS['SUMMARY']['OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO'], 0)
        estados = {o.get('CASCO_RECEPTOR_STATE') for o in ORFAOS['OUTPUTS']}
        self.assertNotIn('ABSENT', estados)
        self.assertNotIn('ABSENT_AS_RECEPTOR', estados)

    def test_zero_orfa_nao_e_lido_como_casco_pronto(self):
        """A ressalva continua no arquivo mesmo depois de tudo fechar.

        No index (12) o zero convivia com tres receptores expondo o rotulo no
        lugar do HOSE_ID. O texto foi reescrito no fechamento, e a lei
        permanece: quem fecha o casco e a medicao dos receptores, nao esta
        contagem.
        """
        texto = ORFAOS['TWO_DIFFERENT_NUMBERS']['O_QUE_ZERO_AQUI_NAO_SIGNIFICA']
        self.assertIn('nunca significou casco pronto', texto)
        self.assertIn('DISPLAY_LABEL no lugar do HOSE_ID', texto)

    def test_nenhuma_classificacao_mudou_para_chegar_a_zero(self):
        self.assertEqual(ORFAOS['SUMMARY']['CLASS_COUNTS'], {
            'SUBRECEPTOR_OF_EXISTING_HOSE': 21,
            'AUXILIARY_RECEPTOR_REQUIRED': 8,
            'NOT_CANONICAL': 5,
            'DEPRECATED': 1,
        })

    def test_o_historico_das_tres_medicoes_esta_preservado(self):
        h = ORFAOS['TWO_DIFFERENT_NUMBERS']['HISTORICO']
        for marca in ('index (10)', 'index (11)', 'index (12)'):
            self.assertIn(marca, h)


class TestTestemunha(Base):

    def test_a_testemunha_confere_byte_a_byte(self):
        with open(CASCO12, 'rb') as f:
            dados = f.read()
        self.assertEqual(len(dados), 1521561)
        self.assertEqual(hashlib.sha256(dados).hexdigest(),
                         'b12ad20ebba85277e32819f3a7f35279c6af22c870c3c956ae10ff8eb42d8a66')

    def test_as_quatro_testemunhas_coexistem(self):
        for nome in ('SINTONIA-EAME-PILOT-V7.html',
                     'SINTONIA-EAME-V8-RECEPTOR-CANDIDATE.html',
                     'SINTONIA-EAME-V8-DATA-READY.html',
                     'SINTONIA-EAME-V8-FINAL.html'):
            self.assertTrue(os.path.exists(
                os.path.join(ROOT, 'casco', 'canonical', nome)), nome)

    def test_as_nove_telas_continuam(self):
        self.assertEqual(set(M['CASCO']['TELAS']),
                         {'home', 'radar', 'obj', 'acervo', 'fontes',
                          'relatorios', 'eame', 'lib', 'config'})

    def test_o_medidor_nao_toca_a_rede(self):
        import ast
        with open(os.path.join(ROOT, 'scripts', 'v8_receptor_final.py'),
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
