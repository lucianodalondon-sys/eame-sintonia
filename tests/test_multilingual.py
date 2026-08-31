# -*- coding: utf-8 -*-
"""Provas do CONTRATO MULTILINGUE.

Um contrato que so existe em documento nao impede nada. Estas provas existem para que
as sete regras REPROVEM quando alguem as quebrar — inclusive eu, daqui a tres semanas.

Nada aqui traduz de verdade: os textos sao fixture. MASS_TRANSLATION_EXECUTED = NO.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import multilingual_contract as mc  # noqa: E402


def _entidade():
    """Um boletim frances real em forma, fictício em conteúdo."""
    return mc.content_entity(
        content_id='CE-FR-0001',
        original_language='fr',
        original_text="Vigne : la pression mildiou reste forte dans le Bordelais.",
        source={'SOURCE_ID': 'FR-T3-BSV', 'URL': 'https://exemplo.fr/bsv/2026-08'},
        published_at='2026-08-14',
        fact_country='FR',
        nao_traduziveis={
            'PRODUCT_COMMERCIAL_NAME': 'MAXENTIS',
            'COMPANY_NAME': 'ADAMA France S.A.S.',
            'TRADEMARK': 'MAXENTIS',
            'ACTIVE_INGREDIENT': 'prothioconazole',
            'SCIENTIFIC_NAME': 'Plasmopara viticola',
            'REGISTRATION_ID': '2230815',
            'SOURCE_QUOTE': "la pression mildiou reste forte",
        })


class TestSourceLanguage(unittest.TestCase):
    """1 · SOURCE_LANGUAGE nunca muda por causa de traducao."""

    def test_traduzir_para_quatro_linguas_nao_mexe_na_origem(self):
        e = _entidade()
        antes = (e['SOURCE_LANGUAGE'], e['ORIGINAL_TEXT'], e['ORIGINAL_TEXT_HASH'])
        for lang in ('es', 'it', 'en', 'pt'):
            mc.registrar_traducao(e, lang, 'texto em %s' % lang, 'MACHINE', '2026-08-30')
        depois = (e['SOURCE_LANGUAGE'], e['ORIGINAL_TEXT'], e['ORIGINAL_TEXT_HASH'])
        self.assertEqual(antes, depois)
        self.assertEqual(e['SOURCE_LANGUAGE'], 'fr')

    def test_uma_traducao_espanhola_nao_torna_a_fonte_espanhola(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'La presion de mildiu sigue alta.',
                              'MACHINE', '2026-08-30')
        v = mc.montar_exibicao(e, 'es')
        self.assertEqual(v['ORIGINAL_LANGUAGE'], 'fr')
        self.assertEqual(v['TRANSLATED_FROM'], 'fr')

    def test_traduzir_para_a_propria_lingua_e_recusado(self):
        e = _entidade()
        with self.assertRaises(mc.ContratoViolado):
            mc.registrar_traducao(e, 'fr', 'x', 'MACHINE', '2026-08-30')


class TestUmObjetoVariasLinguas(unittest.TestCase):
    """2 · Um objeto, varias linguas — nunca varios objetos."""

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


class TestNormalizacaoDeLingua(unittest.TestCase):
    """O acervo tem 15 grafias para 5 linguas. O portao fecha isso sem apagar o caso."""

    def test_grafias_reais_do_acervo(self):
        casos = {
            'ES': ('es', 'OK'), 'es': ('es', 'OK'), 'EN': ('en', 'OK'),
            'pt': ('pt', 'OK'), 'FR': ('fr', 'OK'), 'IT': ('it', 'OK'),
        }
        for entrada, esperado in casos.items():
            self.assertEqual(mc.normalizar_lingua(entrada), esperado, entrada)

    def test_multilingue_nao_e_lingua(self):
        for v in ('multi', 'FR/ES', 'FR/ES/IT', 'FR/ES/IT/EN', 'ES / EN', 'EN / FR',
                  'FR/IT', 'en (majoritario)'):
            self.assertEqual(mc.normalizar_lingua(v)[1], 'MULTI', v)

    def test_desconhecido_falha_fechado(self):
        self.assertEqual(mc.normalizar_lingua('klingon')[1], 'UNKNOWN')
        self.assertEqual(mc.normalizar_lingua(None)[1], 'UNKNOWN')
        with self.assertRaises(mc.ContratoViolado):
            mc.content_entity('X', 'klingon', 't', {})

    def test_multi_e_aceito_como_estado_e_nao_como_lingua(self):
        e = mc.content_entity('X', 'FR/ES', 'texto', {'SOURCE_ID': 'S'})
        self.assertIsNone(e['SOURCE_LANGUAGE'])
        self.assertEqual(e['SOURCE_LANGUAGE_STATE'], 'MULTI')


class TestOntologia(unittest.TestCase):
    """3 · A identidade do objeto nao muda com a lingua."""

    def _mildiou(self):
        return mc.termo('VENTOL' if False else 'PLASVI', 'ISSUE',
                        labels={'es': 'Mildiu de la vid', 'fr': 'Mildiou de la vigne',
                                'en': 'Grapevine downy mildew'},
                        scientific_name='Plasmopara viticola',
                        aliases={'es': ['mildiu'], 'fr': ['mildiou']})

    def test_o_id_nao_muda_com_o_rotulo(self):
        t = self._mildiou()
        ids = set(mc.resolver_rotulo(t, l)['TERM_ID'] for l in mc.LINGUAS)
        self.assertEqual(ids, {'PLASVI'})

    def test_rotulos_diferentes_por_lingua(self):
        t = self._mildiou()
        self.assertEqual(mc.resolver_rotulo(t, 'fr')['TEXT'], 'Mildiou de la vigne')
        self.assertEqual(mc.resolver_rotulo(t, 'es')['TEXT'], 'Mildiu de la vid')

    def test_fallback_e_declarado_nunca_silencioso(self):
        t = self._mildiou()
        r = mc.resolver_rotulo(t, 'it')     # nao ha rotulo italiano
        self.assertEqual(r['FALLBACK'], 'SCIENTIFIC_NAME')
        self.assertEqual(r['TEXT'], 'Plasmopara viticola')

    def test_nunca_devolve_vazio(self):
        t = mc.termo('XXXX1', 'ISSUE', labels={})
        r = mc.resolver_rotulo(t, 'pt')
        self.assertTrue(r['TEXT'])
        self.assertEqual(r['FALLBACK'], 'TERM_ID')

    def test_rotulo_fora_do_vocabulario_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.termo('X', 'ISSUE', labels={'de': 'Falscher Mehltau'})

    def test_tipo_desconhecido_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.termo('X', 'ALGO', labels={'en': 'x'})


class TestIconeDeDoenca(unittest.TestCase):
    """ADAMA_DISEASE_ICON_ID — vinculo planejado, nunca inventado."""

    def test_issue_sem_icone_fica_pendente_e_nao_generico(self):
        t = mc.termo('PLASVI', 'ISSUE', labels={'en': 'downy mildew'})
        i = mc.icone_da_doenca(t)
        self.assertIsNone(i['ICON'])
        self.assertEqual(i['STATE'], 'PENDING_OFFICIAL_ICON')
        self.assertIn('nao criar icone generico', i['RULE'])

    def test_issue_com_icone_oficial_fica_bound(self):
        t = mc.termo('PLASVI', 'ISSUE', labels={'en': 'x'},
                     adama_disease_icon_id='adama/icon/disease/downy-mildew')
        self.assertEqual(mc.icone_da_doenca(t)['STATE'], 'BOUND')

    def test_cultura_nao_tem_icone_de_doenca(self):
        t = mc.termo('OLVEU', 'CROP', labels={'es': 'Olivo'},
                     scientific_name='Olea europaea')
        self.assertEqual(mc.icone_da_doenca(t)['STATE'], 'NOT_APPLICABLE')


class TestEvidencia(unittest.TestCase):
    """4 · TRANSLATED_EVIDENCE != ORIGINAL_EVIDENCE."""

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
            self.assertIn('ORIGINAL_LANGUAGE', v)

    def test_sem_traducao_mostra_o_original_e_nao_vazio(self):
        e = _entidade()
        v = mc.montar_exibicao(e, 'pt')      # nunca traduzido
        self.assertEqual(v['DISPLAY_TEXT'], e['ORIGINAL_TEXT'])
        self.assertEqual(v['QUALITY_STATE'], 'SOURCE_ORIGINAL')
        self.assertIsNone(v['TRANSLATED_FROM'])


class TestNaoTraduziveis(unittest.TestCase):
    """5 · Identificador nao se traduz."""

    def test_identidade_identica_em_todas_as_linguas(self):
        e = _entidade()
        for lang in ('es', 'it', 'en'):
            mc.registrar_traducao(e, lang, 'texto %s' % lang, 'MACHINE', '2026-08-30')
        base = mc.montar_exibicao(e, 'fr')
        for lang in ('es', 'it', 'en', 'pt'):
            v = mc.montar_exibicao(e, lang)
            for campo in mc.NAO_TRADUZIVEIS:
                self.assertEqual(v[campo], base[campo], '%s mudou em %s' % (campo, lang))

    def test_a_lista_cobre_os_sete_identificadores(self):
        for c in ('PRODUCT_COMMERCIAL_NAME', 'COMPANY_NAME', 'TRADEMARK',
                  'ACTIVE_INGREDIENT', 'SCIENTIFIC_NAME', 'REGISTRATION_ID',
                  'SOURCE_QUOTE'):
            self.assertIn(c, mc.NAO_TRADUZIVEIS)

    def test_campo_fora_da_lista_e_recusado(self):
        with self.assertRaises(mc.ContratoViolado):
            mc.content_entity('X', 'fr', 't', {}, nao_traduziveis={'TITULO': 'x'})


class TestProveniencia(unittest.TestCase):
    """9 · Nao afirmar qualidade humana quando nao houve revisao."""

    def test_maquina_nao_declara_revisao_humana_sozinha(self):
        e = _entidade()
        with self.assertRaises(mc.ContratoViolado):
            mc.registrar_traducao(e, 'es', 'x', 'HUMAN', '2026-08-30',
                                  quality_state='MACHINE_TRANSLATED')

    def test_metodo_maquina_cai_em_machine_translated(self):
        e = _entidade()
        t = mc.registrar_traducao(e, 'es', 'x', 'MACHINE', '2026-08-30')
        self.assertEqual(t['QUALITY_STATE'], 'MACHINE_TRANSLATED')

    def test_maquina_revisada_por_pessoa_pode_subir(self):
        e = _entidade()
        t = mc.registrar_traducao(e, 'es', 'x', 'MACHINE', '2026-08-30',
                                  quality_state='HUMAN_REVIEWED')
        self.assertEqual(t['QUALITY_STATE'], 'HUMAN_REVIEWED')

    def test_fonte_que_publica_na_lingua_tem_estado_proprio(self):
        e = _entidade()
        t = mc.registrar_traducao(e, 'en', 'x', 'SOURCE_PROVIDED', '2026-08-30')
        self.assertEqual(t['QUALITY_STATE'], 'SOURCE_PROVIDED_TRANSLATION')

    def test_toda_traducao_responde_as_seis_perguntas(self):
        e = _entidade()
        t = mc.registrar_traducao(e, 'es', 'x', 'MACHINE', '2026-08-30')
        for c in ('TRANSLATION_LANGUAGE', 'TRANSLATION_METHOD', 'TRANSLATION_VERSION',
                  'TRANSLATED_AT', 'QUALITY_STATE', 'CONTENT_ID'):
            self.assertIn(c, t)


class TestCacheEVersao(unittest.TestCase):
    """10 · TRANSLATE_ONCE / STORE / VERSION / REUSE."""

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
        e = _entidade()
        self.assertEqual(mc.precisa_retraduzir(e, 'it')[0], 'MISSING')


class TestBusca(unittest.TestCase):
    """6 · Busca em qualquer lingua chega ao MESMO objeto canonico."""

    def _idx(self):
        e = _entidade()
        mc.registrar_traducao(e, 'es', 'La presion de mildiu sigue alta en Burdeos.',
                              'MACHINE', '2026-08-30')
        mc.registrar_traducao(e, 'it', 'La pressione di peronospora resta alta.',
                              'MACHINE', '2026-08-30')
        t = mc.termo('PLASVI', 'ISSUE',
                     labels={'es': 'Mildiu de la vid', 'fr': 'Mildiou de la vigne',
                             'it': 'Peronospora della vite'},
                     scientific_name='Plasmopara viticola',
                     aliases={'es': ['mildiu'], 'it': ['peronospora']})
        return mc.indexar([e], [t])

    def test_busca_em_espanhol_acha_material_originalmente_frances(self):
        r = mc.buscar(self._idx(), 'mildiu')
        self.assertIn('CE-FR-0001', r)
        self.assertIn('PLASVI', r)

    def test_busca_em_italiano_acha_o_mesmo_objeto(self):
        r = mc.buscar(self._idx(), 'peronospora')
        self.assertIn('CE-FR-0001', r)

    def test_nome_cientifico_atravessa_todas_as_linguas(self):
        r = mc.buscar(self._idx(), 'Plasmopara viticola')
        self.assertIn('PLASVI', r)
        self.assertIn('CE-FR-0001', r)   # esta no campo SCIENTIFIC_NAME da entidade

    def test_identificador_acha_sem_depender_de_lingua(self):
        r = mc.buscar(self._idx(), 'MAXENTIS')
        self.assertIn('CE-FR-0001', r)
        caminhos = [x['PATH'] for x in r['CE-FR-0001']]
        self.assertTrue(any(p.startswith('IDENTIFIER:') for p in caminhos))

    def test_o_caminho_do_achado_e_declarado(self):
        """O caminho importa: achar pelo ID e uma confianca; pelo texto traduzido, outra."""
        conhecidos = ('ORIGINAL_TEXT', 'TRANSLATED_TEXT', 'ONTOLOGY_LABEL',
                      'ALIAS', 'SCIENTIFIC_NAME')
        idx = self._idx()
        vistos = set()
        for busca in ('mildiu', 'MAXENTIS', 'Plasmopara', 'peronospora'):
            for achados in mc.buscar(idx, busca).values():
                for a in achados:
                    self.assertIn('PATH', a)
                    ok = a['PATH'] in conhecidos or a['PATH'].startswith('IDENTIFIER:')
                    self.assertTrue(ok, 'caminho nao declarado: %r' % a['PATH'])
                    vistos.add(a['PATH'].split(':')[0])
        # o teste so vale se tiver exercido caminhos DIFERENTES, inclusive identificador
        self.assertIn('IDENTIFIER', vistos)
        self.assertTrue(len(vistos) >= 3, 'exercitou poucos caminhos: %s' % vistos)

    def test_um_indice_nao_um_acervo_por_lingua(self):
        idx = self._idx()
        ids = set(x['CANONICAL_ID'] for x in idx)
        self.assertEqual(ids, {'CE-FR-0001', 'PLASVI'})


if __name__ == '__main__':
    unittest.main()
