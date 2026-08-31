# -*- coding: utf-8 -*-
"""Provas do CONTRATO MULTILINGUE — v1 congelada apos o red team de 2026-08-30.

Um contrato que so existe em documento nao impede nada. Estas provas existem para que as
regras REPROVEM quem as quebrar — inclusive eu, daqui a tres semanas.

As oito ultimas classes sao as regressoes do RED TEAM: cada uma trava um erro que eu
mesmo cometi na rodada anterior.

Nada aqui traduz de verdade. MASS_TRANSLATION_EXECUTED = NO.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import multilingual_contract as mc  # noqa: E402

QUOTE_FR = "la pression mildiou reste forte"


def _entidade(**kw):
    """Um boletim frances real em forma, ficticio em conteudo."""
    base = dict(
        content_id='CE-FR-0001',
        source_language='fr',
        original_text="Vigne : la pression mildiou reste forte dans le Bordelais.",
        source={'SOURCE_ID': 'FR-T3-BSV', 'URL': 'https://exemplo.fr/bsv/2026-08'},
        published_at='2026-08-14',
        fact_country='FR',
        original_quote=QUOTE_FR,
        source_reference='https://exemplo.fr/bsv/2026-08#p3',
        identidades={
            'PRODUCT_COMMERCIAL_NAME': 'MAXENTIS',
            'COMPANY_LEGAL_NAME': 'ADAMA France S.A.S.',
            'TRADEMARK_CANONICAL_NAME': 'MAXENTIS',
            'SCIENTIFIC_NAME': 'Plasmopara viticola',
            'REGISTRATION_ID': '2230815',
        })
    base.update(kw)
    return mc.content_entity(**base)


def _mildiou():
    return mc.termo('PLASVI', 'ISSUE',
                    labels={'es': 'Mildiu de la vid', 'fr': 'Mildiou de la vigne',
                            'it': 'Peronospora della vite', 'en': 'Grapevine downy mildew'},
                    scientific_name='Plasmopara viticola',
                    aliases={'es': ['mildiu'], 'it': ['peronospora']},
                    eppo_backed='YES')


# ═══════════════════════════════════════════════ contrato base (preservado)
class TestSourceLanguage(unittest.TestCase):
    """SOURCE_LANGUAGE nunca muda por causa de traducao."""

    def test_traduzir_para_quatro_linguas_nao_mexe_na_origem(self):
        e = _entidade()
        antes = (e['SOURCE_LANGUAGE'], e['ORIGINAL_TEXT'], e['ORIGINAL_TEXT_HASH'])
        for lang in ('es', 'it', 'en', 'pt'):
            mc.registrar_traducao(e, lang, 'texto em %s' % lang, 'MACHINE', '2026-08-30')
        self.assertEqual(antes, (e['SOURCE_LANGUAGE'], e['ORIGINAL_TEXT'],
                                 e['ORIGINAL_TEXT_HASH']))
        self.assertEqual(e['SOURCE_LANGUAGE'], 'fr')

    def test_uma_traducao_espanhola_nao_torna_a_fonte_espanhola(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'La presion de mildiu sigue alta.',
                              'MACHINE', '2026-08-30')
        v = mc.montar_exibicao(e, 'es')
        self.assertEqual(v['SOURCE_LANGUAGE'], 'fr')
        self.assertEqual(v['TRANSLATED_FROM'], 'fr')

    def test_traduzir_para_a_propria_lingua_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.registrar_traducao(_entidade(), 'fr', 'x', 'MACHINE', '2026-08-30')


class TestUmObjetoVariasLinguas(unittest.TestCase):
    def test_quatro_traducoes_um_unico_id(self):
        e = _entidade()
        for lang in ('es', 'it', 'en', 'pt'):
            t = mc.registrar_traducao(e, lang, 'texto %s' % lang, 'MACHINE', '2026-08-30')
            self.assertEqual(t['CONTENT_ID'], 'CE-FR-0001')
        self.assertEqual(len(e['TRANSLATIONS']), 4)

    def test_o_id_canonico_sobrevive_a_exibicao_em_qualquer_lingua(self):
        e = _entidade()
        for lang in ('es', 'it'):
            mc.registrar_traducao(e, lang, 'texto %s' % lang, 'MACHINE', '2026-08-30')
        ids = set(mc.montar_exibicao(e, l)['CONTENT_ID'] for l in ('fr', 'es', 'it', 'en'))
        self.assertEqual(ids, {'CE-FR-0001'})


class TestVocabularioDeLingua(unittest.TestCase):
    """O acervo tem 15 grafias para 5 linguas. O portao fecha sem apagar o caso."""

    def test_grafias_reais_do_acervo(self):
        for entrada, esperado in {'ES': ('es', 'OK'), 'es': ('es', 'OK'),
                                  'EN': ('en', 'OK'), 'pt': ('pt', 'OK'),
                                  'FR': ('fr', 'OK'), 'IT': ('it', 'OK')}.items():
            self.assertEqual(mc.normalizar_lingua(entrada), esperado, entrada)

    def test_multilingue_nao_e_lingua(self):
        for v in ('multi', 'FR/ES', 'FR/ES/IT', 'FR/ES/IT/EN', 'ES / EN', 'EN / FR',
                  'FR/IT', 'en (majoritario)'):
            self.assertEqual(mc.normalizar_lingua(v)[1], 'MULTILINGUAL', v)

    def test_desconhecido_falha_fechado(self):
        self.assertEqual(mc.normalizar_lingua('klingon')[1], 'UNKNOWN')
        self.assertEqual(mc.normalizar_lingua(None)[1], 'UNKNOWN')
        with self.assertRaises(mc.ContratoViolado):
            _entidade(source_language='klingon')

    def test_vocabulario_e_fechado_e_tem_sete_valores(self):
        self.assertEqual(len(mc.VOCABULARIO_FECHADO), 7)
        for v in ('pt', 'en', 'es', 'fr', 'it', 'MULTILINGUAL', 'UNKNOWN'):
            self.assertIn(v, mc.VOCABULARIO_FECHADO)


class TestOntologia(unittest.TestCase):
    def test_o_id_nao_muda_com_o_rotulo(self):
        t = _mildiou()
        self.assertEqual(set(mc.resolver_rotulo(t, l)['TERM_ID'] for l in mc.LINGUAS),
                         {'PLASVI'})

    def test_rotulos_diferentes_por_lingua(self):
        t = _mildiou()
        self.assertEqual(mc.resolver_rotulo(t, 'fr')['TEXT'], 'Mildiou de la vigne')
        self.assertEqual(mc.resolver_rotulo(t, 'es')['TEXT'], 'Mildiu de la vid')

    def test_fallback_e_declarado_nunca_silencioso(self):
        t = mc.termo('PLASVI', 'ISSUE', labels={'es': 'Mildiu'},
                     scientific_name='Plasmopara viticola', eppo_backed='YES')
        r = mc.resolver_rotulo(t, 'it')
        self.assertEqual(r['FALLBACK'], 'SCIENTIFIC_NAME')

    def test_nunca_devolve_vazio(self):
        r = mc.resolver_rotulo(mc.termo('XXXX1', 'ISSUE', labels={}), 'pt')
        self.assertTrue(r['TEXT'])
        self.assertEqual(r['FALLBACK'], 'TERM_ID')

    def test_rotulo_fora_do_vocabulario_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.termo('X', 'ISSUE', labels={'de': 'Falscher Mehltau'})

    def test_eppo_nao_cobre_molecula_nem_departamento(self):
        for kind in ('MOLECULE', 'EVENT_TYPE', 'DEPARTMENT'):
            with self.assertRaises(mc.ContratoViolado):
                mc.termo('X', kind, labels={'en': 'x'}, eppo_backed='YES')

    def test_eppo_backed_e_declarado_nunca_adivinhado(self):
        t = mc.termo('X', 'MOLECULE', labels={'en': 'prothioconazole'})
        self.assertEqual(t['EPPO_BACKED_ENTITY_ID'], 'NOT_MEASURED')


class TestEvidencia(unittest.TestCase):
    def test_traducao_nunca_e_evidencia(self):
        e = _entidade()
        t = mc.registrar_traducao(e, 'es', 'texto es', 'MACHINE', '2026-08-30')
        self.assertFalse(t['IS_EVIDENCE'])
        self.assertFalse(mc.montar_exibicao(e, 'es')['IS_EVIDENCE'])
        self.assertTrue(mc.montar_exibicao(e, 'fr')['IS_EVIDENCE'])

    def test_toda_exibicao_carrega_a_porta_de_volta(self):
        e = _entidade()
        mc.registrar_traducao(e, 'it', 'testo it', 'MACHINE', '2026-08-30')
        for lang in ('fr', 'it', 'en'):
            v = mc.montar_exibicao(e, lang)
            self.assertTrue(v['VIEW_ORIGINAL'])
            self.assertTrue(v['SOURCE'])
            self.assertTrue(v['SOURCE_REFERENCE'])
            self.assertIn('SOURCE_LANGUAGE', v)

    def test_sem_traducao_mostra_o_original_e_nao_vazio(self):
        v = mc.montar_exibicao(_entidade(), 'pt')
        self.assertEqual(v['QUALITY_STATE'], 'SOURCE_ORIGINAL')
        self.assertIsNone(v['TRANSLATED_FROM'])


class TestIdentidadesImutaveis(unittest.TestCase):
    def test_identidade_identica_em_todas_as_linguas(self):
        e = _entidade()
        for lang in ('es', 'it', 'en'):
            mc.registrar_traducao(e, lang, 'texto %s' % lang, 'MACHINE', '2026-08-30')
        base = mc.montar_exibicao(e, 'fr')
        for lang in ('es', 'it', 'en', 'pt'):
            v = mc.montar_exibicao(e, lang)
            for campo in e['IDENTITIES']:
                self.assertEqual(v[campo], base[campo], '%s mudou em %s' % (campo, lang))

    def test_campo_fora_da_lista_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            _entidade(identidades={'TITULO': 'x'})


class TestProveniencia(unittest.TestCase):
    def test_maquina_nao_declara_revisao_humana_sozinha(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.registrar_traducao(_entidade(), 'es', 'x', 'HUMAN', '2026-08-30',
                                  quality_state='MACHINE_TRANSLATED')

    def test_metodo_maquina_cai_em_machine_translated(self):
        t = mc.registrar_traducao(_entidade(), 'es', 'x', 'MACHINE', '2026-08-30')
        self.assertEqual(t['QUALITY_STATE'], 'MACHINE_TRANSLATED')

    def test_maquina_revisada_por_pessoa_pode_subir(self):
        t = mc.registrar_traducao(_entidade(), 'es', 'x', 'MACHINE', '2026-08-30',
                                  quality_state='HUMAN_REVIEWED')
        self.assertEqual(t['QUALITY_STATE'], 'HUMAN_REVIEWED')

    def test_fonte_que_publica_na_lingua_tem_estado_proprio(self):
        t = mc.registrar_traducao(_entidade(), 'en', 'x', 'SOURCE_PROVIDED', '2026-08-30')
        self.assertEqual(t['QUALITY_STATE'], 'SOURCE_PROVIDED_TRANSLATION')

    def test_toda_traducao_responde_as_seis_perguntas(self):
        t = mc.registrar_traducao(_entidade(), 'es', 'x', 'MACHINE', '2026-08-30')
        for c in ('TRANSLATION_TARGET_LANGUAGE', 'TRANSLATION_METHOD',
                  'TRANSLATION_VERSION', 'TRANSLATED_AT', 'QUALITY_STATE', 'CONTENT_ID'):
            self.assertIn(c, t)


class TestCacheEVersao(unittest.TestCase):
    def test_reexibir_nao_envelhece(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'x', 'MACHINE', '2026-08-30')
        for _ in range(5):
            mc.montar_exibicao(e, 'es')
        self.assertEqual(mc.precisa_retraduzir(e, 'es')[0], 'FRESH')

    def test_texto_canonico_mudou_invalida(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'x', 'MACHINE', '2026-08-30')
        e['ORIGINAL_TEXT'] = 'texto corrigido pela fonte'
        e['ORIGINAL_TEXT_HASH'] = mc._hash(e['ORIGINAL_TEXT'])
        self.assertEqual(mc.precisa_retraduzir(e, 'es')[0], 'STALE')

    def test_lingua_nunca_traduzida_e_missing(self):
        self.assertEqual(mc.precisa_retraduzir(_entidade(), 'it')[0], 'MISSING')


class TestBusca(unittest.TestCase):
    def _idx(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'La presion de mildiu sigue alta en Burdeos.',
                              'MACHINE', '2026-08-30')
        mc.registrar_traducao(e, 'it', 'La pressione di peronospora resta alta.',
                              'HUMAN', '2026-08-30')
        return mc.indexar([e], [_mildiou()])

    def test_busca_em_espanhol_acha_material_originalmente_frances(self):
        r = mc.buscar(self._idx(), 'mildiu')
        self.assertIn('CE-FR-0001', r)
        self.assertIn('PLASVI', r)

    def test_busca_em_italiano_acha_o_mesmo_objeto(self):
        self.assertIn('CE-FR-0001', mc.buscar(self._idx(), 'peronospora'))

    def test_nome_cientifico_atravessa_todas_as_linguas(self):
        r = mc.buscar(self._idx(), 'Plasmopara viticola')
        self.assertIn('PLASVI', r)
        self.assertIn('CE-FR-0001', r)

    def test_identificador_acha_sem_depender_de_lingua(self):
        r = mc.buscar(self._idx(), '2230815')
        self.assertIn('CE-FR-0001', r)
        self.assertIn('REGISTRATION_ID_MATCH', [x['PATH'] for x in r['CE-FR-0001']])

    def test_maquina_e_humano_sao_caminhos_diferentes(self):
        idx = self._idx()
        caminhos = set(x['PATH'] for x in idx)
        self.assertIn('MACHINE_TRANSLATION_MATCH', caminhos)
        self.assertIn('HUMAN_REVIEWED_TRANSLATION_MATCH', caminhos)

    def test_todo_caminho_esta_no_vocabulario_declarado(self):
        for x in self._idx():
            self.assertIn(x['PATH'], mc.MATCH_PATHS)

    def test_um_indice_nao_um_acervo_por_lingua(self):
        self.assertEqual(set(x['CANONICAL_ID'] for x in self._idx()),
                         {'CE-FR-0001', 'PLASVI'})

    def test_busca_semantica_esta_declarada_e_nao_implementada(self):
        self.assertIn('SEMANTIC_MATCH', mc.MATCH_PATHS)
        self.assertNotIn('SEMANTIC_MATCH', set(x['PATH'] for x in self._idx()))


# ═══════════════════════════════════════ REGRESSOES DO RED TEAM 2026-08-30
class TestGuardSourceLanguageNeArtifactLanguage(unittest.TestCase):
    """`SOURCE_LANGUAGE_NE_ARTIFACT_LANGUAGE_GUARD`.

    Quinze artefatos do acervo declaram lingua `pt`. Nenhuma fonte ES/FR/IT e
    portuguesa: sao ANALISES escritas em portugues. O campo registrava a lingua de quem
    escreveu, nao a da fonte.
    """

    def test_os_dois_campos_coexistem_e_nao_se_substituem(self):
        e = _entidade(source_language='fr', artifact_language='pt')
        self.assertEqual(e['SOURCE_LANGUAGE'], 'fr')
        self.assertEqual(e['ARTIFACT_LANGUAGE'], 'pt')

    def test_a_exibicao_carrega_os_dois(self):
        v = mc.montar_exibicao(_entidade(artifact_language='pt'), 'fr')
        self.assertEqual(v['SOURCE_LANGUAGE'], 'fr')
        self.assertEqual(v['ARTIFACT_LANGUAGE'], 'pt')

    def test_artifact_language_ausente_nao_vira_source_language(self):
        e = _entidade(artifact_language=None)
        self.assertIsNone(e['ARTIFACT_LANGUAGE'])
        self.assertEqual(e['ARTIFACT_LANGUAGE_STATE'], 'UNKNOWN')
        self.assertEqual(e['SOURCE_LANGUAGE'], 'fr')

    def test_os_cinco_papeis_estao_nomeados(self):
        for p in ('SOURCE_LANGUAGE', 'ARTIFACT_LANGUAGE', 'UI_LANGUAGE',
                  'DISPLAY_LANGUAGE', 'TRANSLATION_TARGET_LANGUAGE'):
            self.assertIn(p, mc.PAPEIS_DE_LINGUA)


class TestGuardMultilingualExigeSegmento(unittest.TestCase):
    """`MULTILINGUAL_SOURCE_REQUIRES_SEGMENT_OR_MULTILINGUAL_STATE_GUARD`."""

    def test_string_composta_sem_segmento_e_recusada(self):
        for v in ('FR/ES/IT/EN', 'ES / EN', 'multi'):
            with self.assertRaises(mc.ContratoViolado):
                _entidade(source_language=v)

    def test_com_segmentos_e_aceito(self):
        e = _entidade(source_language='FR/ES', segments=[
            {'SEGMENT_ID': 's1', 'SEGMENT_LANGUAGE': 'fr', 'TEXT': 'bloc francais'},
            {'SEGMENT_ID': 's2', 'SEGMENT_LANGUAGE': 'es', 'TEXT': 'bloque espanol'}])
        self.assertEqual(e['SOURCE_LANGUAGE_STATE'], 'MULTILINGUAL')
        self.assertEqual(len(e['SEGMENTS']), 2)

    def test_declaracao_explicita_e_aceita_sem_segmentos(self):
        e = _entidade(source_language='MULTILINGUAL')
        self.assertEqual(e['SOURCE_LANGUAGE_STATE'], 'MULTILINGUAL')
        self.assertIsNone(e['SOURCE_LANGUAGE'])

    def test_segmento_com_lingua_composta_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            _entidade(source_language='MULTILINGUAL', segments=[
                {'SEGMENT_ID': 's1', 'SEGMENT_LANGUAGE': 'FR/ES', 'TEXT': 'x'}])


class TestGuardCanonicalIdNeDisplayLabel(unittest.TestCase):
    """`CANONICAL_ID_NE_DISPLAY_LABEL_GUARD`. O rotulo nunca e chave primaria."""

    def test_cinco_rotulos_um_id(self):
        t = _mildiou()
        rotulos = set(mc.resolver_rotulo(t, l)['TEXT'] for l in mc.LINGUAS)
        self.assertGreater(len(rotulos), 1, 'os rotulos precisam mesmo diferir')
        self.assertEqual(set(mc.resolver_rotulo(t, l)['TERM_ID'] for l in mc.LINGUAS),
                         {'PLASVI'})

    def test_termo_sem_id_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.termo('', 'ISSUE', labels={'es': 'Mildiu de la vid'})

    def test_o_indice_guarda_o_id_e_nao_o_rotulo(self):
        for x in mc.indexar([], [_mildiou()]):
            self.assertEqual(x['CANONICAL_ID'], 'PLASVI')


class TestGuardActiveIngredientSobreviveAoRotulo(unittest.TestCase):
    """`ACTIVE_INGREDIENT_ID_SURVIVES_LABEL_TRANSLATION_GUARD`.

    CORRECAO: eu tinha posto ACTIVE_INGREDIENT entre as identidades imutaveis, o que
    obrigaria a mostrar a grafia francesa a um leitor italiano. A invariancia e do ID.
    """

    def test_ingrediente_ativo_saiu_das_identidades_imutaveis(self):
        self.assertNotIn('ACTIVE_INGREDIENT', mc.IDENTIDADES_IMUTAVEIS)
        self.assertIn('ACTIVE_INGREDIENT_ID', mc.ENTIDADES_COM_ID_E_ROTULO)

    def test_usar_ingrediente_como_identidade_imutavel_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            _entidade(identidades={'ACTIVE_INGREDIENT_ID': 'prothioconazole'})

    def test_o_id_sobrevive_a_tres_grafias(self):
        t = mc.termo('CAS-178928-70-6', 'MOLECULE',
                     labels={'fr': 'prothioconazole', 'es': 'protioconazol',
                             'it': 'protioconazolo', 'en': 'prothioconazole'})
        textos = set(mc.resolver_rotulo(t, l)['TEXT'] for l in ('fr', 'es', 'it'))
        self.assertEqual(len(textos), 3, 'as tres grafias sao mesmo diferentes')
        self.assertEqual(set(mc.resolver_rotulo(t, l)['TERM_ID'] for l in ('fr', 'es', 'it')),
                         {'CAS-178928-70-6'})


class TestGuardCitacaoOriginalPreservada(unittest.TestCase):
    """`ORIGINAL_QUOTE_PRESERVED_WHEN_TRANSLATED_GUARD`."""

    def test_a_citacao_original_sai_em_toda_lingua(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'texto es', 'MACHINE', '2026-08-30',
                              translated_quote='la presion de mildiu sigue alta')
        for lang in ('fr', 'es', 'it', 'en', 'pt'):
            self.assertEqual(mc.montar_exibicao(e, lang)['ORIGINAL_QUOTE'], QUOTE_FR)

    def test_a_traducao_nao_substitui_a_original(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'texto es', 'MACHINE', '2026-08-30',
                              translated_quote='outra coisa')
        v = mc.montar_exibicao(e, 'es')
        self.assertEqual(v['QUOTE_DISPLAYED'], 'outra coisa')
        self.assertEqual(v['ORIGINAL_QUOTE'], QUOTE_FR)
        self.assertNotEqual(v['QUOTE_DISPLAYED'], v['ORIGINAL_QUOTE'])

    def test_citacao_saiu_das_identidades_imutaveis(self):
        self.assertNotIn('SOURCE_QUOTE', mc.IDENTIDADES_IMUTAVEIS)
        with self.assertRaises(mc.ContratoViolado):
            _entidade(identidades={'SOURCE_QUOTE': 'x'})


class TestGuardCitacaoTraduzidaNaoEEvidencia(unittest.TestCase):
    """`TRANSLATED_QUOTE_NOT_ORIGINAL_EVIDENCE_GUARD`."""

    def test_citacao_traduzida_e_marcada_como_traducao(self):
        e = _entidade()
        mc.registrar_traducao(e, 'it', 'testo it', 'HUMAN', '2026-08-30',
                              translated_quote='la pressione resta alta')
        v = mc.montar_exibicao(e, 'it')
        self.assertTrue(v['QUOTE_IS_TRANSLATION'])
        self.assertFalse(v['QUOTE_IS_EVIDENCE'])

    def test_sem_citacao_traduzida_mostra_a_original_como_evidencia(self):
        e = _entidade()
        mc.registrar_traducao(e, 'it', 'testo it', 'MACHINE', '2026-08-30')
        v = mc.montar_exibicao(e, 'it')
        self.assertEqual(v['QUOTE_DISPLAYED'], QUOTE_FR)
        self.assertFalse(v['QUOTE_IS_TRANSLATION'])
        self.assertTrue(v['QUOTE_IS_EVIDENCE'])

    def test_na_lingua_de_origem_a_citacao_e_sempre_evidencia(self):
        v = mc.montar_exibicao(_entidade(), 'fr')
        self.assertTrue(v['QUOTE_IS_EVIDENCE'])


class TestGuardIconeOficialExisteFora(unittest.TestCase):
    """`OFFICIAL_DISEASE_ICON_EXISTS_EXTERNAL_NOT_MISSING_GUARD`.

    CORRECAO: eu escrevi PENDING_OFFICIAL_ICON, como se o ativo fosse desconhecido. Ele
    existe no design system do Claude Design. O casco V7 nao o carregar e outra coisa.
    """

    def test_o_ativo_nunca_e_declarado_ausente(self):
        i = mc.icone_da_doenca(mc.termo('PLASVI', 'ISSUE', labels={'en': 'x'}))
        self.assertEqual(i['ASSET'], 'EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM')
        for proibido in ('MISSING', 'PENDING_OFFICIAL_ICON', 'NOT_EXISTS'):
            self.assertNotIn(proibido, str(i['ASSET']))

    def test_os_tres_estados_sao_separados(self):
        i = mc.icone_da_doenca(mc.termo('PLASVI', 'ISSUE', labels={'en': 'x'}))
        self.assertEqual(i['BINDING'], 'NOT_IMPLEMENTED')
        self.assertEqual(i['CROSSWALK'], 'NOT_MEASURED')

    def test_a_regra_proibe_desenhar_substituto(self):
        i = mc.icone_da_doenca(mc.termo('PLASVI', 'ISSUE', labels={'en': 'x'}))
        self.assertIn('nao desenhar substituto', i['RULE'])

    def test_com_icone_mapeado_o_binding_muda_mas_o_ativo_nao(self):
        i = mc.icone_da_doenca(mc.termo('PLASVI', 'ISSUE', labels={'en': 'x'},
                                        adama_disease_icon_id='adama/disease/downy-mildew'))
        self.assertEqual(i['BINDING'], 'MAPPED')
        self.assertEqual(i['ASSET'], 'EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM')

    def test_cultura_nao_tem_icone_de_doenca(self):
        t = mc.termo('OLVEU', 'CROP', labels={'es': 'Olivo'},
                     scientific_name='Olea europaea', eppo_backed='YES')
        self.assertEqual(mc.icone_da_doenca(t)['BINDING'], 'NOT_APPLICABLE')


class TestGuardContratoNaoEAcervo(unittest.TestCase):
    """`CONTRACT_READY_NE_LEGACY_CORPUS_COMPLIANT_GUARD`.

    O contrato pode estar pronto com o acervo legado inteiro fora de conformidade — e
    esta. Misturar os selos venderia migracao que nao aconteceu.
    """

    def test_os_selos_vivem_em_blocos_diferentes(self):
        s = mc.selos()
        for bloco in ('CONTRACT_GUARD', 'CORPUS_AUDIT_RESULT', 'IMPLEMENTATION_STATE'):
            self.assertIn(bloco, s)

    def test_o_contrato_nao_afirma_conformidade_do_acervo(self):
        s = mc.selos()
        self.assertNotIn('SOURCE_LANGUAGE_PRESERVED', s['CONTRACT_GUARD'])
        self.assertEqual(s['CONTRACT_GUARD']['SOURCE_LANGUAGE_PRESERVATION_RULE'],
                         'PROVED_BY_TESTS')

    def test_o_acervo_legado_esta_declarado_nao_provado(self):
        a = mc.selos()['CORPUS_AUDIT_RESULT']
        self.assertEqual(a['LEGACY_LANGUAGE_FIELD_INTEGRITY'], 'NOT_PROVED')
        self.assertEqual(a['LEGACY_SOURCE_LANGUAGE_INTEGRITY'], 'NOT_PROVED')

    def test_artefato_e_registro_sao_numeros_diferentes(self):
        a = mc.selos()['CORPUS_AUDIT_RESULT']
        self.assertEqual(a['ARTIFACTS_WITH_LEGACY_LANGUAGE_DECLARATION'], '78/81')
        self.assertEqual(a['SOURCE_RECORDS_WITH_A_DECLARED_LANGUAGE_VALUE'], 0)
        self.assertEqual(a['SOURCE_RECORDS_SCANNED'], 5998)

    def test_indice_de_busca_nao_e_declarado_pronto(self):
        s = mc.selos()
        self.assertEqual(s['CONTRACT_GUARD']['CROSS_LANGUAGE_SEARCH_MODEL'], 'READY')
        self.assertEqual(s['IMPLEMENTATION_STATE']['CROSS_LANGUAGE_SEARCH_INDEX'],
                         'NOT_IMPLEMENTED')

    def test_nada_afirma_migracao_ou_traducao_em_massa(self):
        i = mc.selos()['IMPLEMENTATION_STATE']
        self.assertEqual(i['CORPUS_MIGRATION_EXECUTED'], 'NO')
        self.assertEqual(i['MASS_TRANSLATION_EXECUTED'], 'NO')
        self.assertEqual(i['CASCO_V7_MODIFIED'], 'NO')


if __name__ == '__main__':
    unittest.main()
