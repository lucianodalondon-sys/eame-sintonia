# -*- coding: utf-8 -*-
"""Provas de IMPLEMENTACAO dos receptores no casco DATA-READY (index 11).

O arquivo irmao, test_v8_receptors.py, prova que o CONTRATO esta completo e mede
o casco anterior (index 10). Aqui a pergunta e outra: **o casco novo implementa?**

Estas provas TRAVAM A MEDICAO, nao aprovam o casco. Quando o Claude Design
corrigir um item, a prova correspondente vai reprovar — e isso e o comportamento
desejado: obriga a remedir em vez de deixar um veredito velho passar por novo.
Cada prova diz, no nome e na docstring, o que esta medido hoje.

Zero rede. Le apenas os bytes do casco versionado e os artefatos deste repositorio.
"""
import hashlib
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from v8_receptor_reaudit import (  # noqa: E402
    CASCO11, PAYLOAD_CANONICO, VOCABULARIO_HOSE, OITO_ESTADOS, ACAO_CANONICA,
    abrir, fatiar, campos_do_receptor, medir,
)

IMPL = os.path.join(ROOT, 'data', 'implementation')
with open(os.path.join(IMPL, 'V8-RECEPTOR-REAUDIT.json'), encoding='utf-8') as f:
    REAUDIT = json.load(f)
with open(os.path.join(IMPL, 'ORPHAN-INTELLIGENCE-OUTPUTS.json'), encoding='utf-8') as f:
    ORFAOS = json.load(f)

MARKUP, CAMADA, ATIVOS = abrir()
TELAS = fatiar(MARKUP)
M = medir()
V = M['VERDICTS']
POR_HOSE = {r['HOSE_ID']: r for r in M['RECEPTORES_DECLARADOS']}
POR_ID = {r['RECEPTOR_ID']: r for r in M['RECEPTORES_DECLARADOS']}


class Base(unittest.TestCase):

    def envelope_completo(self, hose):
        """Os nove campos do envelope canonico, presentes e nao vazios."""
        r = POR_HOSE[hose]
        for campo in ('RECEPTOR_ID', 'HOSE_ID', 'CANONICAL_PAYLOAD_TYPE', 'LOAD_STATE',
                      'NO_DATA_REASON', 'EVIDENCE_POINTERS', 'FAIL_CLOSED_BEHAVIOR'):
            self.assertTrue(r.get(campo), '%s sem %s' % (hose, campo))
        self.assertIn(r['LOAD_STATE'], OITO_ESTADOS)
        self.assertEqual(V['HOSES'][hose]['ENVELOPE'], 'COMPLETE')
        return r

    def alias_sem_mapa(self, hose):
        """Medido: o payload e alias e nao existe ADAPTER_ALIAS_MAP."""
        self.assertEqual(V['HOSES'][hose]['PAYLOAD_NAME'], 'ALIAS_WITHOUT_MAP')
        self.assertNotIn(POR_HOSE[hose]['CANONICAL_PAYLOAD_TYPE'], PAYLOAD_CANONICO[hose])
        self.assertEqual(V['HOSES'][hose]['VERDICT'], 'FAIL')

    def campos(self, receptor_id):
        return campos_do_receptor(CAMADA, receptor_id)


class TestReceptoresImplementados(Base):
    """Uma prova por mangueira, com o nome do briefing."""

    def test_H1_RECEPTOR_IMPLEMENTED(self):
        """Envelope completo. FAIL so pelo nome: TERRITORIAL_ATTENTION_OBJECT."""
        self.envelope_completo('H1')
        c = self.campos('RECEPTOR_TERRITORIAL_OBJECT')
        for campo in ('OBJECT_ID', 'COUNTRY_OF_FACT', 'REGION_OF_FACT', 'CROP', 'ISSUE',
                      'ISSUE_EVIDENCE_PASSAGE', 'PUBLISHED_AT', 'SOURCE_ID',
                      'ATTENTION_STATE', 'BLOCKER', 'LAST_EVIDENCE_AT'):
            self.assertIn(campo, c, 'H1 sem %s' % campo)
        self.alias_sem_mapa('H1')

    def test_H2_RECEPTOR_IMPLEMENTED(self):
        """Envelope completo, CROP/ISSUE = NOT_APPLICABLE por contrato."""
        r = self.envelope_completo('H2')
        c = self.campos('RECEPTOR_REGULATORY_DEADLINE')
        for campo in ('REGISTRATION_NUMBER', 'REGISTRATION_HOLDER', 'PRODUCT_NAME',
                      'DEADLINE_DATE', 'DEADLINE_KIND', 'STATUS_AS_DECLARED_BY_SOURCE'):
            self.assertIn(campo, c, 'H2 sem %s' % campo)
        self.assertIn('EXPIRY_IS_NOT_WITHDRAWAL', c)
        self.assertIn('REVIEW', r['FAIL_CLOSED_BEHAVIOR'])
        self.alias_sem_mapa('H2')

    def test_H3_RECEPTOR_IMPLEMENTED(self):
        """AGREEMENT_STATE e URBOLE_GUARD_RESULT entraram como campo."""
        self.envelope_completo('H3')
        c = self.campos('RECEPTOR_COMPETITOR_IDENTITY_CHAIN')
        for campo in ('COMPETITOR_NAME', 'NORMALIZED_PRODUCT', 'TRADEMARK_REGISTRATION_ID',
                      'TRADEMARK_HOLDER', 'LOCAL_REGISTRATION_ID', 'LOCAL_REGISTRATION_HOLDER',
                      'OBSERVED_PAID_ACTIVITY_REF', 'AGREEMENT_STATE', 'URBOLE_GUARD_RESULT'):
            self.assertIn(campo, c, 'H3 sem %s' % campo)
        self.alias_sem_mapa('H3')

    def test_H4_RECEPTOR_IMPLEMENTED(self):
        """Evidencia, nunca painel. CANNOT_CLAIM_LIST presente."""
        r = self.envelope_completo('H4')
        c = self.campos('RECEPTOR_OBSERVED_PAID_ACTIVITY')
        for campo in ('EVIDENCE_ID', 'PLATFORM', 'PAGE_ID', 'PAGE_COUNTRY_SCOPE',
                      'OBSERVED_AT', 'OBSERVATION_WINDOW', 'AD_CARD_COUNT', 'CANNOT_CLAIM_LIST'):
            self.assertIn(campo, c, 'H4 sem %s' % campo)
        self.assertIn('gaveta não abre', r['FAIL_CLOSED_BEHAVIOR'])
        self.alias_sem_mapa('H4')

    def test_H5_RECEPTOR_IMPLEMENTED(self):
        """READINGS[] e a dependencia de H1 declarada como campo."""
        self.envelope_completo('H5')
        c = self.campos('RECEPTOR_LONGITUDINAL_FIELD')
        for campo in ('READINGS[]', 'READING_N_PER_POINT', 'SEASON_RANGE', 'BASELINE_KIND',
                      'BASELINE_STATE', 'COHORT_STATE', 'BACKTEST_STATE',
                      'INDEPENDENCE_FROM_TERRITORIAL_STATE'):
            self.assertIn(campo, c, 'H5 sem %s' % campo)
        self.alias_sem_mapa('H5')

    def test_H6_RECEPTOR_IMPLEMENTED(self):
        """FAIL medido: nao existe receptor com HOSE_ID = H6.

        voices[] recebeu ENTITY_KIND, ENTRY_PATH, GDPR_TREATMENT_STATE e
        ROW_COUNT/ENTITY_COUNT — e nada disso e um receptor. Uma lista com campos
        certos nao tem LOAD_STATE, PROVENANCE, EVIDENCE_POINTERS nem
        FAIL_CLOSED_REASON, entao nao sabe dizer por que esta vazia.
        """
        self.assertNotIn('H6', POR_HOSE)
        self.assertIn('H6', M['HOSES']['SEM_RECEPTOR'])
        self.assertEqual(V['HOSES']['H6']['VERDICT'], 'FAIL')
        # os campos existem em voices[], o que torna a ausencia do envelope o unico gap
        for campo in ('ENTRY_PATH', 'GDPR_TREATMENT_STATE', 'ROW_COUNT / ENTITY_COUNT'):
            self.assertIn(campo, CAMADA, 'voices[] perdeu %s' % campo)
        # e os tres payloads canonicos de H6 continuam sem destino
        for payload in PAYLOAD_CANONICO['H6']:
            self.assertNotIn(payload, [r['CANONICAL_PAYLOAD_TYPE']
                                       for r in M['RECEPTORES_DECLARADOS']])

    def test_H7_RECEPTOR_IMPLEMENTED(self):
        """ISSUE_EXPERTISE_PROVED entrou como campo e como portao executavel."""
        r = self.envelope_completo('H7')
        c = self.campos('RECEPTOR_ISSUE_EXPERT')
        for campo in ('PERSON_ID', 'DISPLAY_NAME', 'ORGANIZATION',
                      'RELATION_TO_ISSUE_AS_DECLARED', 'ISSUE_EXPERTISE_PROVED',
                      'IDENTITY_PROVED', 'GDPR_TREATMENT_STATE'):
            self.assertIn(campo, c, 'H7 sem %s' % campo)
        self.assertIn('Ranking é proibido', r['FAIL_CLOSED_BEHAVIOR'])
        self.alias_sem_mapa('H7')

    def test_H7_gate_e_executavel_e_nao_prosa(self):
        """O portao virou codigo: sem prova, o rotulo e PESSOA RELACIONADA."""
        self.assertIn("role: e.proved ? 'ESPECIALISTA DO PROBLEMA' : 'PESSOA RELACIONADA'",
                      CAMADA)
        self.assertIn("'ISSUE_EXPERTISE_PROVED · ' + (e.proved ? 'TRUE' : 'FALSE')", CAMADA)
        # nenhuma das tres pessoas do fixture tem expertise provada
        self.assertEqual(CAMADA.count('proved: true'), 0)

    def test_H8_RECEPTOR_IMPLEMENTED(self):
        """NOT_STARTED e estado real, com a lei escrita no proprio motivo."""
        r = self.envelope_completo('H8')
        self.assertEqual(r['LOAD_STATE'], 'NOT_STARTED')
        c = self.campos('RECEPTOR_PUBLIC_COMMUNICATION')
        for campo in ('ACCOUNT_ID', 'COMPANY_NAME', 'PLATFORM', 'COUNTRY_SCOPE',
                      'PAGE_ROLE', 'CONTENT_COLLECTION_STAGE', 'ROUTE_STATE',
                      'IDENTITY_RESOLVED_AT'):
            self.assertIn(campo, c, 'H8 sem %s' % campo)
        self.alias_sem_mapa('H8')

    def test_H8_not_started_nao_vira_empty_nem_silencio(self):
        """A confusao proibida esta negada por escrito no receptor."""
        r = POR_HOSE['H8']
        self.assertIn('NOT_STARTED', r['NO_DATA_REASON'] + str(r))
        self.assertIn('Ausência de conteúdo coletado não é ausência de comunicação', CAMADA)
        self.assertNotEqual(r['LOAD_STATE'], 'EMPTY_VALID')
        self.assertNotIn('COMPANY_NOT_COMMUNICATING', CAMADA)

    def test_H9_RECEPTOR_IMPLEMENTED(self):
        """Um objeto, varias representacoes — nunca um objeto por idioma."""
        r = self.envelope_completo('H9')
        c = self.campos('RECEPTOR_MULTILINGUAL_CONTENT')
        for campo in ('CANONICAL_ENTITY_ID', 'SOURCE_LANGUAGE', 'DISPLAY_LANGUAGE',
                      'ORIGINAL_TEXT', 'TRANSLATED_TEXT', 'TRANSLATION_PROVENANCE',
                      'ONTOLOGY_TERM_ID'):
            self.assertIn(campo, c, 'H9 sem %s' % campo)
        self.assertIn('nunca substitui o original', r['FAIL_CLOSED_BEHAVIOR'])
        self.alias_sem_mapa('H9')

    def test_H9_cinco_idiomas_preservados(self):
        self.assertIn("const langs = { pt: 'PT', en: 'EN', es: 'ES', it: 'IT', fr: 'FR' }",
                      CAMADA)

    def test_oito_de_nove_tem_envelope_e_zero_passa(self):
        """Os dois numeros que nao se trocam um pelo outro."""
        self.assertEqual(V['HOSES_WITH_COMPLETE_ENVELOPE'], 8)
        self.assertEqual(V['HOSES_WITH_CANONICAL_PAYLOAD_NAME'], 0)
        self.assertEqual(V['HOSES_WITH_COMPLETE_RECEIVER'], 0)


class TestNomesCanonicos(Base):

    def test_CANONICAL_PAYLOAD_NAMES_MATCH_OR_HAVE_EXPLICIT_ALIAS(self):
        """FAIL medido: oito aliases e nenhum ADAPTER_ALIAS_MAP.

        A regra do briefing: alias so e aceitavel com mapa explicito e univoco.
        Sem mapa, duas ontologias passam a coexistir em silencio — e e assim que
        um adapter futuro liga o cano errado sem ninguem perceber.
        """
        self.assertFalse(V['ADAPTER_ALIAS_MAP_EXISTE']
                         if 'ADAPTER_ALIAS_MAP_EXISTE' in V
                         else M['DRIFT']['ADAPTER_ALIAS_MAP_EXISTE'])
        self.assertEqual(V['CANONICAL_PAYLOAD_TYPE_DRIFT'], 'FAIL')
        self.assertEqual(len(M['DRIFT']['CANONICAL_PAYLOAD_TYPE_DRIFT']), 8)

    def test_cada_alias_nomeia_o_canonico_que_deveria_ter(self):
        for d in M['DRIFT']['CANONICAL_PAYLOAD_TYPE_DRIFT']:
            self.assertIn(d['HOSE_ID'], VOCABULARIO_HOSE)
            self.assertTrue(d['CANONICO'])
            self.assertNotIn(d['DECLARADO'], d['CANONICO'])

    def test_SUBRECEPTOR_PARENT_HOSE_VALID(self):
        """FAIL medido: H7·CIENCIA, H2·PORTFOLIO, H6·CAMPO e H0 sem PARENT_HOSE_ID."""
        self.assertEqual(V['SUBRECEPTOR_PARENT_HOSE_DRIFT'], 'FAIL')
        self.assertFalse(M['DRIFT']['PARENT_HOSE_ID_EXISTE'])
        fora = {d['HOSE_ID'] for d in M['DRIFT']['SUBRECEPTOR_PARENT_HOSE_DRIFT']}
        self.assertEqual(fora, {'H7·CIÊNCIA', 'H2·PORTFÓLIO', 'H6·CAMPO', 'H0'})
        for h in fora:
            self.assertNotIn(h, VOCABULARIO_HOSE)

    def test_os_tres_subreceptores_tem_payload_canonico(self):
        """O que ESTA certo: os nomes de payload dos subreceptores nao driftaram."""
        esperado = {
            'RECEPTOR_SCIENTIFIC_PUBLICATION': 'SCIENTIFIC_PUBLICATION',
            'RECEPTOR_LOCAL_ADAMA_PORTFOLIO': 'LOCAL_ADAMA_PORTFOLIO_CONTEXT',
            'RECEPTOR_FIELD_VOICE_OBSERVATION': 'FIELD_VOICE_OBSERVATION',
        }
        for rid, payload in esperado.items():
            self.assertEqual(POR_ID[rid]['CANONICAL_PAYLOAD_TYPE'], payload)

    def test_SCIENCE_PUBLICATION_RECEPTOR_COMPLETE(self):
        r = POR_ID['RECEPTOR_SCIENTIFIC_PUBLICATION']
        self.assertEqual(r['LOAD_STATE'], 'NOT_STARTED')
        c = self.campos('RECEPTOR_SCIENTIFIC_PUBLICATION')
        for campo in ('PUBLICATION_ID', 'TITLE', 'PUBLISHED_AT', 'VENUE', 'AUTHORS',
                      'RELATION_TO_ISSUE_AS_DECLARED', 'PEER_REVIEWED_STATE',
                      'SOURCE_LANGUAGE', 'DOI'):
            self.assertIn(campo, c)
        self.assertIn('SCIENTIFIC_PERSON ≠ SCIENTIFIC_PUBLICATION', CAMADA)

    def test_LOCAL_PORTFOLIO_RECEPTOR_COMPLETE(self):
        c = self.campos('RECEPTOR_LOCAL_ADAMA_PORTFOLIO')
        for campo in ('REGISTERED_RESPONSE_STATE', 'ADAMA_PRODUCT_REFS[]',
                      'REGISTRATION_REFS[]', 'LABEL_AUTHORIZES_TARGET_STATE'):
            self.assertIn(campo, c)
        self.assertIn('REGISTRATION_DEADLINE ≠ LOCAL_ADAMA_PORTFOLIO_CONTEXT', CAMADA)

    def test_FIELD_VOICE_RECEPTOR_COMPLETE(self):
        r = POR_ID['RECEPTOR_FIELD_VOICE_OBSERVATION']
        self.assertEqual(r['LOAD_STATE'], 'NOT_STARTED')
        c = self.campos('RECEPTOR_FIELD_VOICE_OBSERVATION')
        for campo in ('OBSERVATION_ID', 'ENTITY_ID', 'ENTITY_KIND', 'PLATFORM',
                      'OBSERVED_AT', 'CROP_MENTIONED', 'REGION_MENTIONED',
                      'ORIGINAL_TEXT', 'SOURCE_LANGUAGE', 'GDPR_TREATMENT_STATE'):
            self.assertIn(campo, c)


class TestComponentes(Base):

    def test_CONVERGENCE_DEPENDENCY_EXECUTED(self):
        """A prova que o briefing pediu, executada sobre o casco.

        TERRITORIAL = INDEPENDENT, FIELD_HISTORICAL = DEPENDENT com
        SOURCE_DEPENDENCY. Duas pernas, UMA familia independente. O casco calcula
        SINGLE SIGNAL e nao MULTI SIGNAL — que era o erro que matou a V1.
        """
        c = M['CONVERGENCIA']
        self.assertEqual(len(c['PERNAS']), 2)
        familias = {p['SIGNAL_FAMILY']: p for p in c['PERNAS']}
        self.assertEqual(familias['TERRITORIAL']['INDEPENDENCE_STATE'], 'INDEPENDENT')
        self.assertEqual(familias['FIELD_HISTORICAL']['INDEPENDENCE_STATE'], 'DEPENDENT')
        self.assertEqual(familias['FIELD_HISTORICAL']['DEPENDENCY_RELATION'],
                         'SOURCE_DEPENDENCY')
        self.assertEqual(c['INDEPENDENT_FAMILY_COUNT'], 1)
        self.assertEqual(c['CONVERGENCE_STATE'], 'SINGLE_SIGNAL')
        # e a contagem e derivada no proprio casco, nao digitada
        self.assertIn("const independentCount = CONV_LEGS.filter(l => l.independence === "
                      "'INDEPENDENT').length", CAMADA)

    def test_convergencia_carrega_os_cinco_ids(self):
        for chave in ('propositionId', 'kind', 'independentCount'):
            self.assertIn('conv.%s' % chave, MARKUP)
        for chave in ('EVIDENCE_ID', 'SOURCE_ID', 'OBSERVED_AT', 'INDEPENDENCE_STATE'):
            self.assertIn(chave, CAMADA)

    def test_H3_H4_DERIVATION_DEPENDENCY_ainda_nao_representada(self):
        """FAIL medido: a unica dependencia com exemplo e H5→H1.

        A outra dependencia real do produto — a perna Meta da cadeia E o anuncio
        da Meta — nao tem exemplo em lugar nenhum, e DERIVATION_DEPENDENCY nao
        aparece no casco. O vocabulario esta incompleto onde mais custa.
        """
        self.assertNotIn('DERIVATION_DEPENDENCY', CAMADA)
        self.assertNotIn('DERIVATION_DEPENDENCY', MARKUP)

    def test_BLOCK_PARITY_RADAR_OBJ(self):
        """FAIL medido: o bloco de convergencia do Radar ficou na versao anterior.

        O Object Detail recebeu propositionId, kind, independentCount, dependency
        e dependencyNote. O Radar nao recebeu nenhum dos cinco. Duas telas mostram
        a mesma convergencia com leis diferentes.
        """
        self.assertEqual(V['BLOCK_PARITY_RADAR_OBJ'], 'FAIL')
        self.assertEqual(M['BLOCO_DIVERGENTE']['CONVERGENCIA_NO_RADAR'], [])
        self.assertEqual(len(M['BLOCO_DIVERGENTE']['CONVERGENCIA_NO_OBJ']), 5)

    def test_dead_handlers(self):
        """FAIL medido: openDrawer sobrou no Radar e sumiu de renderVals.

        O Object Detail passou a usar l.openEvidence. O Radar continua chamando
        openDrawer, que ja nao existe no retorno — um botao com cursor de clique
        e sem acao. Mesma classe do 'ranking de recorrencia' do V7.
        """
        self.assertEqual(M['HANDLERS_MORTOS'], ['openDrawer'])
        self.assertIn('{{ openDrawer }}', TELAS['radar'])
        self.assertNotIn('{{ openDrawer }}', TELAS['obj'])
        self.assertIn('{{ l.openEvidence }}', TELAS['obj'])

    def test_TIMELINE_TYPED(self):
        for campo in ("k: 'EVENT_ID'", "k: 'EVENT_TYPE'", "k: 'EVENT_AT'",
                      "k: 'OBSERVATION_ID'", "k: 'GAP_REASON'"):
            self.assertIn(campo, CAMADA, 'timeline sem %s' % campo)
        self.assertIn("res: 'DATA_EXATA'", CAMADA)
        self.assertIn("res: 'NAO_CONHECIDA'", CAMADA)
        self.assertIn('VAZIO TEMPORAL', CAMADA)
        # sem EVENT_AT real, nao se inventa precisao
        self.assertIn("at: null", CAMADA)
        self.assertIn("v: e.at || 'NULL'", CAMADA)

    def test_timeline_ainda_concatena_os_dois_estados(self):
        """Medido: STATE_BEFORE e STATE_AFTER chegam como uma string so."""
        self.assertIn("k: 'STATE', v: (e.before || '—') + ' → ' + (e.after || '—')", CAMADA)
        self.assertNotIn('STATE_BEFORE', CAMADA)
        self.assertNotIn('STATE_AFTER', CAMADA)

    def test_CROP_MAP_TYPED(self):
        for campo in ('OBJECT_ID', 'OBJECT_TYPE', 'ATTENTION_STATE', 'COUNTRY', 'REGION',
                      'LOCALITY_OR_GEOMETRY', 'GEO_RESOLUTION', 'CROP'):
            self.assertIn("%s:" % campo, CAMADA, 'mapa sem %s' % campo)
        self.assertIn("GEO_RESOLUTION: 'NOT_KNOWN'", CAMADA)

    def test_CROP_MAP_nao_desenha_ponto_sem_geo_resolution(self):
        """O guard nao esta no casco: esta no asset crop-map.js. Foi lido la."""
        self.assertTrue(M['MAPA']['GUARD_NO_ASSET'])
        self.assertTrue(M['MAPA']['DECLARA_NAO_DESENHAVEIS'])
        js = next(t for t in ATIVOS.values() if 'pointsjson' in t)
        self.assertIn("points.filter(p => p.GEO_RESOLUTION === 'POINT'", js)
        self.assertIn('LOCALITY_TEXT nunca é geocodificado silenciosamente', js)
        # com todos os pontos em NOT_KNOWN, nenhum e desenhavel
        pontos = re.findall(r"GEO_RESOLUTION: '([A-Z_]+)'", CAMADA)
        self.assertTrue(pontos)
        self.assertEqual([p for p in pontos if p == 'POINT'], [])

    def test_ACTION_TYPES_CANONICAL(self):
        """FAIL medido: BUSINESS e SYSTEM persistidos, sem DISPLAY_ACTION_TYPE."""
        self.assertEqual(V['ACTION_TYPE_CANONICAL_DRIFT'], 'FAIL')
        self.assertEqual(M['DRIFT']['ACTION_TYPE_PERSISTIDO'],
                         ['BUSINESS', 'INVESTIGATION', 'SYSTEM'])
        self.assertEqual(M['DRIFT']['ACTION_TYPE_CANONICAL_DRIFT'], ['BUSINESS', 'SYSTEM'])
        self.assertFalse(M['DRIFT']['DISPLAY_ACTION_TYPE_EXISTE'])
        self.assertIn('INVESTIGATION', ACAO_CANONICA)

    def test_ACTION_MAP_EVIDENCE_BASIS_GUARD(self):
        """O guard entrou como codigo executavel, nao como texto fixo."""
        self.assertIn("action: (a.kind === 'business' && (!a.basis || !a.basis.length)) "
                      "? 'SEM AÇÃO DEFENSÁVEL AINDA' : a.action", CAMADA)
        self.assertIn("basis: (a.basis && a.basis.length) ? 'EVIDENCE_BASIS · '", CAMADA)
        self.assertIn("'EVIDENCE_BASIS VAZIO'", CAMADA)
        self.assertIn('{{ a.basis }}', MARKUP)

    def test_action_map_ainda_sem_object_id(self):
        """Medido: nenhuma acao diz a que objeto pertence."""
        self.assertNotIn('{{ a.objectId }}', MARKUP)

    def test_EVIDENCE_DRAWER_PER_EVIDENCE(self):
        """A gaveta virou por evidencia: EV-0001 e EV-0002 abrem coisas diferentes."""
        self.assertIn('drawerRef: { objectId:', CAMADA)
        for chave in ('drawer.objectId', 'drawer.hoseId', 'drawer.evidenceId', 'drawer.claim'):
            self.assertIn('{{ %s }}' % chave, MARKUP)
        ev = re.search(r"const EVIDENCE = \{(.*?)\n    \};", CAMADA, re.S).group(1)
        entradas = re.findall(r"'(EV-\d{4})': \{ hose: '(H\d)'", ev)
        self.assertGreaterEqual(len(entradas), 6)
        d = dict(entradas)
        self.assertEqual(d['EV-0001'], 'H1')
        self.assertEqual(d['EV-0002'], 'H2')
        # e cada uma tem SOURCE_ID e backend proprios
        self.assertIn("sourceId: 'SRC-0001', backend: 'GITHUB'", ev)
        self.assertIn("sourceId: 'SRC-0003', backend: 'SUPABASE'", ev)

    def test_EVIDENCE_DRAWER_TRACES_ALL_HOSES(self):
        """FAIL medido: a gaveta alcanca 5 das 9 mangueiras."""
        self.assertEqual(M['GAVETA']['HOSES_ALCANCADAS'], ['H1', 'H2', 'H3', 'H4', 'H5'])
        self.assertEqual(V['EVIDENCE_DRAWER_TRACES_ALL_HOSES'], 'FAIL')

    def test_gaveta_sem_evidence_id_nao_abre(self):
        """O handler vira null — o link deixa de existir em vez de abrir vazio."""
        self.assertIn("evidence: o.evidenceId\n        ? () => this.set({ drawerOpen: true",
                      CAMADA)
        self.assertIn('hasEvidence: !!o.evidenceId, noEvidence: !o.evidenceId', CAMADA)
        # os dois objetos sem evidenceId (OBJ-04 e OBJ-06) existem no fixture:
        # se todos tivessem evidencia, o caminho do null nunca seria exercido
        ids = re.findall(r"\{ id: '(OBJ-\d+)'.*?\n", CAMADA)
        com_ev = re.findall(r"id: '(OBJ-\d+)'[^\n]*evidenceId: 'EV-", CAMADA)
        self.assertTrue(set(ids) - set(com_ev),
                        'nenhum objeto sem evidencia: o caminho do null nao e exercido')
        # e o mesmo padrao vale para as afirmacoes do objeto
        self.assertIn("tag: c[1] ? 'EVIDÊNCIA · ' + c[1] : 'SEM EVIDENCE_ID'", CAMADA)

    def test_ORIGINAL_HANDLER_WORKS(self):
        self.assertIn("showOriginal: () => this.set({ drawerView: 'original' })", CAMADA)
        self.assertIn('{{ drawer.showOriginal }}', MARKUP)
        self.assertIn('drawer.showOriginal', M['GAVETA']['HANDLERS'])

    def test_TRANSLATION_HANDLER_WORKS(self):
        self.assertIn("showTranslation: () => this.set({ drawerView: 'translation' })", CAMADA)
        self.assertIn('{{ drawer.showTranslation }}', MARKUP)
        self.assertIn('drawer.showTranslation', M['GAVETA']['HANDLERS'])

    def test_traducao_nunca_substitui_o_original(self):
        self.assertIn("const showTrans = s.drawerView === 'translation' && ev && ev.translated",
                      CAMADA)
        self.assertIn('TRADUÇÃO — NÃO SUBSTITUI O ORIGINAL', CAMADA)
        self.assertIn("k: 'TRANSLATION_PROVENANCE'", CAMADA)
        self.assertIn('hasTranslation', CAMADA)


class TestProveniencia(Base):

    def test_GITHUB_PROVENANCE_SUPPORTED(self):
        self.assertIn("const provGithub = ['SOURCE_BACKEND','REPOSITORY','PATH',"
                      "'COMMIT_SHA','HASH','SOURCE_ID','AS_OF_DATE']", CAMADA)
        self.assertIn('sc-for list="{{ provGithub }}"', MARKUP)
        for campo in ('REPOSITORY', 'PATH', 'COMMIT_SHA', 'HASH'):
            self.assertIn("['%s','—']" % campo, CAMADA)

    def test_SUPABASE_PROVENANCE_SUPPORTED(self):
        self.assertIn("const provSupabase = ['SOURCE_BACKEND','SCHEMA','TABLE_OR_VIEW',"
                      "'PRIMARY_KEY','SNAPSHOT_ID','CAPTURED_AT','SOURCE_ID','AS_OF_DATE']",
                      CAMADA)
        for campo in ('SCHEMA', 'TABLE_OR_VIEW', 'PRIMARY_KEY', 'SNAPSHOT_ID', 'CAPTURED_AT'):
            self.assertIn("['%s','—']" % campo, CAMADA)

    def test_uma_ui_so_para_os_dois_backends(self):
        """O mesmo componente r.prov renderiza GitHub e Supabase."""
        self.assertIn('sc-for list="{{ r.prov }}"', MARKUP)
        self.assertEqual(MARKUP.count('sc-for list="{{ r.prov }}"'), 3)
        self.assertIn("prov: (PROV_ROWS[r.backend] || PROV_ROWS.UNWIRED)", CAMADA)

    def test_backend_nao_declarado_tem_estado_proprio(self):
        self.assertIn("UNWIRED: [['SOURCE_BACKEND','NÃO DECLARADO']", CAMADA)

    def test_o_casco_nao_carrega_nenhum_segredo(self):
        for proibido in ('SERVICE_ROLE_KEY', 'service_role', 'SUPABASE_KEY',
                         'apikey', 'Bearer ', 'eyJhbGciOi'):
            self.assertFalse(proibido in MARKUP, 'markup contem %r' % proibido)
            self.assertFalse(proibido in CAMADA, 'camada contem %r' % proibido)


class TestEstadosDeCarga(Base):

    def test_FAIL_CLOSED_STATES_SUPPORTED(self):
        self.assertEqual(set(M['LOAD_STATES']['DECLARADOS']), set(OITO_ESTADOS))
        self.assertIn('sc-for list="{{ loadStates }}"', MARKUP)

    def test_cada_estado_tem_definicao_propria(self):
        for estado in OITO_ESTADOS:
            self.assertIn('%s:' % estado, CAMADA)
        self.assertIn('o receptor existe, o cano não está ligado', CAMADA)
        self.assertIn('O único estado que pode parecer vazio', CAMADA)

    def test_transporte_nao_virou_dado(self):
        """UNWIRED e NOT_STARTED renderizam diferente de EMPTY_VALID."""
        self.assertIn("NOT_STARTED:       { color: T3, border: EARTH, dash: 'dashed'", CAMADA)
        self.assertIn("EMPTY_VALID:       { color: T2, border: EARTH, dash: 'solid'", CAMADA)

    def test_so_dois_dos_oito_estao_exercidos_nos_fixtures(self):
        """Medido, e aceitavel: o vocabulario esta completo, os dados e que nao."""
        self.assertEqual(set(M['LOAD_STATES']['EXERCIDOS']), {'UNWIRED', 'NOT_STARTED'})


class TestOrfaosReauditados(Base):

    def test_NO_ORPHAN_CANONICAL_INTELLIGENCE(self):
        self.assertEqual(ORFAOS['SUMMARY']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'], 0)
        self.assertNotIn('ORPHAN_INTELLIGENCE_OUTPUT',
                         [o['CLASS'] for o in ORFAOS['OUTPUTS']])

    def test_no_index11_faltava_so_o_receptor_de_H6(self):
        """Fato historico do index (11), preservado no proprio arquivo.

        O inventario e vivo e hoje mede o index (12); o que ficou registrado do
        index (11) e a lista de receptores ausentes daquele momento. Apagar
        apagaria a prova de que o patch mudou algo.
        """
        self.assertEqual(len(ORFAOS['RECEPTORS_ABSENT_IN_CASCO_INDEX11']), 1)
        self.assertEqual(ORFAOS['RECEPTORS_ABSENT_IN_CASCO_INDEX11'][0]['RECEPTOR'],
                         'R-H6-CREATOR-ENTITY')
        self.assertIn('index (11): 2 saidas ausentes',
                      ORFAOS['TWO_DIFFERENT_NUMBERS']['HISTORICO'])

    def test_o_inventario_anterior_nao_foi_apagado(self):
        """Apagar o 'antes' apagaria a prova de que o patch mudou algo."""
        self.assertGreaterEqual(len(ORFAOS['RECEPTORS_ABSENT_IN_CASCO_INDEX10']), 6)

    def test_nenhuma_classificacao_mudou_para_chegar_a_zero(self):
        """As classes sao as mesmas do inventario anterior — so o estado mudou."""
        self.assertEqual(ORFAOS['SUMMARY']['CLASS_COUNTS'], {
            'SUBRECEPTOR_OF_EXISTING_HOSE': 21,
            'AUXILIARY_RECEPTOR_REQUIRED': 8,
            'NOT_CANONICAL': 5,
            'DEPRECATED': 1,
        })


class TestTestemunha(Base):

    def test_a_testemunha_confere_byte_a_byte(self):
        with open(CASCO11, 'rb') as f:
            dados = f.read()
        self.assertEqual(len(dados), 1513823)
        self.assertEqual(hashlib.sha256(dados).hexdigest(),
                         '774ce0fbf3cdc567d95df872bd4299c89f5f46dfcede977a68387021abe6968a')

    def test_as_tres_testemunhas_coexistem(self):
        for nome in ('SINTONIA-EAME-PILOT-V7.html',
                     'SINTONIA-EAME-V8-RECEPTOR-CANDIDATE.html',
                     'SINTONIA-EAME-V8-DATA-READY.html'):
            self.assertTrue(os.path.exists(
                os.path.join(ROOT, 'casco', 'canonical', nome)), nome)

    def test_as_nove_telas_continuam(self):
        self.assertEqual(set(M['CASCO']['TELAS']),
                         {'home', 'radar', 'obj', 'acervo', 'fontes',
                          'relatorios', 'eame', 'lib', 'config'})

    def test_o_script_de_reauditoria_nao_toca_a_rede(self):
        import ast
        with open(os.path.join(ROOT, 'scripts', 'v8_receptor_reaudit.py'),
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
