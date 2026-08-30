"""
RED TEAM DO CATÁLOGO ITALIANO — os dez ataques da missão, contra dado real.

Não são hipóteses: cada um é um defeito que a Espanha já pagou. Aqui eles são
disparados contra os 163 registros ADAMA medidos no Ministero della Salute, antes
de qualquer censo — que é a única hora em que corrigir ainda é barato.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import adama_it as ai  # noqa: E402


class Ataque1_PresenteViraRegistrado(unittest.TestCase):
    """Estar no catálogo não prova registro."""

    def setUp(self):
        self.reg = ai.registro_medido()

    def test_produto_do_catalogo_sem_numero_nao_fecha_registro(self):
        r = ai.cruzar({'PRODUCT_NAME': 'PRODUTO QUE NAO EXISTE'}, self.reg)
        self.assertEqual(r['STATE'], ai.LOCAL_PRESENT_NOT_PROVED)
        self.assertIsNone(r['REGISTRATION_ID'])

    def test_ausencia_de_casamento_nao_vira_NOT_REGISTERED(self):
        """NOT_REGISTERED exige o banco dizer ausência, não eu não achar."""
        r = ai.cruzar({'PRODUCT_NAME': 'INEXISTENTE'}, self.reg)
        self.assertNotEqual(r['STATE'], ai.NOT_REGISTERED)
        self.assertIn('NÃO é NOT_REGISTERED', r['WHY'])

    def test_com_numero_valido_fecha_e_diz_por_que(self):
        alvo = self.reg[0]
        r = ai.cruzar({'PRODUCT_NAME': alvo['PRODUCT'],
                       'REGISTRATION_ID': alvo['REGISTRATION_ID']}, self.reg)
        self.assertEqual(r['STATE'], ai.LOCAL_REGISTERED)
        self.assertEqual(r['MATCHED_BY'], 'REGISTRATION_ID')
        self.assertEqual(r['REGISTRATION_EVIDENCE'], 'IT-T4-001')


class Ataque2_HomonimoFunde(unittest.TestCase):
    """NOME IGUAL ≠ MESMO REGISTRO."""

    def setUp(self):
        self.reg = ai.registro_medido()

    def test_os_163_nomes_medidos_sao_todos_distintos(self):
        """Medido, não presumido — e é por isso que o ataque precisa de um
        homônimo sintético para exercitar o caminho do conflito."""
        nomes = [ai._chave_nome(r['PRODUCT']) for r in self.reg]
        self.assertEqual(len(nomes), len(set(nomes)))

    def test_nome_que_cobre_dois_registros_vira_conflito(self):
        """O caminho existe e morde, mesmo sem homônimo no dado real de hoje —
        um registro novo amanhã pode criar um, e o portão tem de estar pronto."""
        alvo = self.reg[0]
        gemeo = dict(alvo, REGISTRATION_ID='999001')
        r = ai.cruzar({'PRODUCT_NAME': alvo['PRODUCT']}, self.reg + [gemeo])
        self.assertEqual(r['STATE'], ai.REGISTRATION_CONFLICT)
        self.assertEqual(len(r['CANDIDATE_REGISTRATION_IDS']), 2)
        self.assertIn('999001', r['CANDIDATE_REGISTRATION_IDS'])

    def test_nome_unico_da_candidato_e_nao_identidade(self):
        nomes = {}
        for r in self.reg:
            nomes.setdefault(ai._chave_nome(r['PRODUCT']), []).append(r)
        unico = next(v[0] for v in nomes.values() if len(v) == 1)
        r = ai.cruzar({'PRODUCT_NAME': unico['PRODUCT']}, self.reg)
        self.assertEqual(r['STATE'], ai.LOCAL_PRESENT_NOT_PROVED)
        self.assertIsNone(r['REGISTRATION_ID'])
        self.assertEqual(r['CANDIDATE_REGISTRATION_ID'], unico['REGISTRATION_ID'])

    def test_numero_que_nao_existe_e_conflito_e_nao_silencio(self):
        r = ai.cruzar({'PRODUCT_NAME': 'X', 'REGISTRATION_ID': '999999'}, self.reg)
        self.assertEqual(r['STATE'], ai.REGISTRATION_CONFLICT)


class Ataque3_CulturaCitadaViraAutorizada(unittest.TestCase):

    def test_nenhuma_relacao_de_cultura_do_registro_e_uso_autorizado(self):
        for p in ai.registro_medido():
            for r in ai.relacoes_de_cultura(p):
                self.assertFalse(r['IS_AUTHORIZED_USE'], p['PRODUCT'])
                self.assertIn(r['RELATION_ORIGIN'], ai.ORIGENS_CULTURA)

    def test_cultura_de_rotacao_nao_se_mistura_com_cultura_citada(self):
        p = next(x for x in ai.registro_medido() if x.get('CROP_TERMS_ROTATION_ONLY'))
        origens = {r['CROP']: r['RELATION_ORIGIN'] for r in ai.relacoes_de_cultura(p)}
        for c in p['CROP_TERMS_ROTATION_ONLY']:
            self.assertEqual(origens[c], ai.CROP_ROTATION_ONLY)

    def test_o_estado_AUTHORIZED_existe_e_ninguem_o_recebe_de_graca(self):
        self.assertIn(ai.CROP_REGULATORY, ai.ORIGENS_CULTURA)
        usados = {r['RELATION_ORIGIN'] for p in ai.registro_medido()
                  for r in ai.relacoes_de_cultura(p)}
        self.assertNotIn(ai.CROP_REGULATORY, usados)


class Ataque4_DoencaColaEmTodasAsCulturas(unittest.TestCase):
    """O defeito espanhol: termo de praga na página atribuído a tudo."""

    def test_nenhum_par_cultura_alvo_e_formado_sem_ancora(self):
        for p in ai.registro_medido():
            r = ai.pares_cultura_alvo(p)
            self.assertEqual(r['PAIRS'], [], p['PRODUCT'])
            self.assertEqual(r['STATE'], 'NOT_RECONSTRUCTED_FROM_SOURCE')

    def test_o_produto_cartesiano_seria_grande_e_por_isso_e_perigoso(self):
        """A prova de que a recusa não é irrelevante: mede o que teria sido criado."""
        total = 0
        for p in ai.registro_medido():
            r = ai.pares_cultura_alvo(p)
            total += r['CROPS_AVAILABLE'] * r['ISSUES_AVAILABLE']
        self.assertGreater(total, 500,
                           'se o cartesiano fosse pequeno, a recusa seria decorativa')
        self.assertEqual(sum(len(ai.pares_cultura_alvo(p)['PAIRS'])
                             for p in ai.registro_medido()), 0)


class Ataque5_DoseCriaAlvo(unittest.TestCase):

    def test_nao_existe_rota_que_promova_dose_a_par_cultura_alvo(self):
        with open(ai.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertIn('DOSE ≠ CROP_ISSUE_PAIR', fonte)
        self.assertNotIn('def dose_para_par', fonte)


class Ataque6_PdfPromocionalViraLabel(unittest.TestCase):

    def test_a_etichetta_e_reconhecida_pela_rota_oficial(self):
        p = ai.registro_medido()[0]
        self.assertEqual(ai.tipo_de_documento(p['LABEL_URL']), ai.ETICHETTA)

    def test_todas_as_163_etiquetas_sao_tipadas_como_etichetta(self):
        for p in ai.registro_medido():
            self.assertEqual(ai.tipo_de_documento(p['LABEL_URL']), ai.ETICHETTA,
                             p['PRODUCT'])

    def test_brochura_e_ficha_nao_viram_rotulo(self):
        casos = {'brochure-goltix-2026.pdf': ai.BROCHURE,
                 'depliant_mais.pdf': ai.BROCHURE,
                 'scheda-tecnica-goltix.pdf': ai.SCHEDA_TECNICA,
                 'scheda_di_sicurezza_goltix.pdf': ai.SCHEDA_SICUREZZA,
                 'MSDS_goltix_it.pdf': ai.SCHEDA_SICUREZZA,
                 'catalogo-adama-2026.pdf': ai.CATALOGO_PDF,
                 'volantino.pdf': ai.LEAFLET,
                 'qualquer-coisa.pdf': ai.DOC_OUTRO}
        for nome, esperado in casos.items():
            self.assertEqual(ai.tipo_de_documento(nome), esperado, nome)

    def test_a_ordem_dos_padroes_protege_a_ficha_de_seguranca(self):
        """"scheda di sicurezza" contém "scheda": sem ordem, viraria técnica."""
        self.assertEqual(ai.tipo_de_documento('scheda di sicurezza.pdf'),
                         ai.SCHEDA_SICUREZZA)


class Ataque7_PathViraIdentidade(unittest.TestCase):

    def test_a_chave_de_storage_nao_e_a_identidade_do_produto(self):
        k1 = ai.storage_key('IT', '002732', ai.ETICHETTA, 'a.pdf')
        k2 = ai.storage_key('IT', '002732', ai.SCHEDA_TECNICA, 'a.pdf')
        self.assertNotEqual(k1, k2)
        self.assertTrue(k1.startswith('IT/002732/'))

    def test_nomes_com_a_mesma_forma_normalizada_dao_a_mesma_chave(self):
        import unicodedata
        composto = unicodedata.normalize('NFC', 'Perícia.pdf')
        decomposto = unicodedata.normalize('NFD', 'Perícia.pdf')
        self.assertNotEqual(composto, decomposto)
        self.assertEqual(ai.storage_key('IT', '1', ai.ETICHETTA, composto),
                         ai.storage_key('IT', '1', ai.ETICHETTA, decomposto))

    def test_nomes_diferentes_que_saneiam_igual_nao_colidem(self):
        a = ai.storage_key('IT', '1', ai.ETICHETTA, 'a b.pdf')
        b = ai.storage_key('IT', '1', ai.ETICHETTA, 'a/b.pdf')
        self.assertNotEqual(a, b)

    def test_a_chave_nao_faz_url_decode_silencioso(self):
        k = ai.storage_key('IT', '1', ai.ETICHETTA, 'nome%20com%20espaco.pdf')
        self.assertIn('20', k)

    def test_a_extensao_e_preservada(self):
        for ext in ('.pdf', '.docx', '.xlsx'):
            self.assertTrue(ai.storage_key('IT', '1', ai.ETICHETTA, 'x' + ext)
                            .endswith(ext), ext)

    def test_sem_registro_a_chave_ainda_e_deterministica(self):
        k = ai.storage_key('IT', None, ai.BROCHURE, 'x.pdf')
        self.assertIn('SEM-REGISTRO', k)
        self.assertEqual(k, ai.storage_key('IT', None, ai.BROCHURE, 'x.pdf'))


class Ataque8_NovaCapturaCriaRegistro(unittest.TestCase):

    def test_duas_capturas_do_mesmo_registro_sao_um_registro(self):
        a = ai.captura('002732', 'IT-T4-001', '2026-08-30')
        b = ai.captura('002732', 'IT-T4-001', '2026-09-15')
        self.assertNotEqual(a['CAPTURE_KEY'], b['CAPTURE_KEY'])
        self.assertEqual(a['REGISTRATION_KEY'], b['REGISTRATION_KEY'])

    def test_a_identidade_regulatoria_e_pais_mais_numero(self):
        self.assertEqual(ai.captura('002732', 'X', 'v')['REGISTRATION_KEY'],
                         ('IT', '002732'))

    def test_fonte_diferente_tambem_e_so_outra_captura(self):
        a = ai.captura('002732', 'IT-T4-001', 'v1')
        b = ai.captura('002732', 'IT-ADAMA-CATALOG', 'v1')
        self.assertEqual(a['REGISTRATION_KEY'], b['REGISTRATION_KEY'])


class Ataque9_ItaliaRecebeEvidenciaEspanhola(unittest.TestCase):

    def test_toda_chave_de_registro_carrega_IT(self):
        for p in ai.registro_medido()[:20]:
            self.assertEqual(ai.captura(p['REGISTRATION_ID'], 'x', 'v')
                             ['REGISTRATION_KEY'][0], 'IT')

    def test_o_titular_NAO_decide_o_pais_do_portfolio(self):
        """O ataque encontrou o contrário do que eu esperava, e o contrário é o
        fato: só 85 dos 163 registros italianos têm titular italiano. Os outros
        78 são de ADAMA AGAN, MAKHTESHIM e DEUTSCHLAND — e são registros
        ITALIANOS do mesmo jeito."""
        prods = ai.registro_medido()
        italianos = [p for p in prods if 'ITALIA' in (p.get('HOLDER') or '').upper()]
        self.assertLess(len(italianos), len(prods))
        self.assertEqual(len(prods) - len(italianos), 78)
        for p in prods:
            e = ai.escopo_de_pais(p)
            self.assertEqual(e['PORTFOLIO_COUNTRY'], 'IT')
            self.assertEqual(e['REGISTRATION_COUNTRY'], 'IT')

    def test_filtrar_por_titular_italiano_descartaria_quase_metade(self):
        """A prova de que a distinção não é acadêmica."""
        prods = ai.registro_medido()
        perdidos = sum(1 for p in prods
                       if not ai.escopo_de_pais(p)['HOLDER_IS_ITALIAN_ENTITY'])
        self.assertGreater(perdidos / len(prods), 0.45)

    def test_a_distribuicao_medida_de_titulares_esta_registrada(self):
        self.assertEqual(sum(ai.HOLDER_ENTITIES_MEASURED.values()), 163)
        self.assertIn('ADAMA AGAN LTD', ai.HOLDER_ENTITIES_MEASURED)
        with open(ai.__file__, encoding='utf-8') as fh:
            self.assertIn('HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY', fh.read())

    def test_nenhuma_fonte_espanhola_aparece_no_contrato_italiano(self):
        with open(ai.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        for proibido in ('ES-T4-001', 'ES-ADAMA', 'nuestras-soluciones',
                         "COUNTRY = 'ES'"):
            self.assertNotIn(proibido, fonte, proibido)

    def test_a_lei_mae_esta_escrita(self):
        self.assertIn('PORTFÓLIO GLOBAL ≠ PORTFÓLIO LOCAL ITÁLIA', ai.__doc__)


class Ataque10_RawPresenteComBytesErrados(unittest.TestCase):
    """RAW PRESENCE ≠ RAW CONTENT VERIFIED."""

    def test_o_gate_exige_hash_conferido_e_nao_so_presenca(self):
        import adama_it_raw as rw
        g = rw.gate(esperado=3, remoto_presente=3, remoto_ausente=0, orfaos=0,
                    falhos=0, hash_conferido=0, hash_divergente=0)
        self.assertEqual(g['STATE'], 'OPEN')
        self.assertIn('CONTENT_HASH_CHECKED', g['WHY'])

    def test_presenca_completa_com_um_hash_divergente_nao_fecha(self):
        import adama_it_raw as rw
        g = rw.gate(esperado=3, remoto_presente=3, remoto_ausente=0, orfaos=0,
                    falhos=0, hash_conferido=3, hash_divergente=1)
        self.assertEqual(g['STATE'], 'OPEN')

    def test_so_fecha_com_tudo_conferido(self):
        import adama_it_raw as rw
        g = rw.gate(esperado=3, remoto_presente=3, remoto_ausente=0, orfaos=0,
                    falhos=0, hash_conferido=3, hash_divergente=0)
        self.assertEqual(g['STATE'], 'CLOSED')

    def test_5xx_nao_e_objeto_nao_preservado(self):
        import adama_it_raw as rw
        r = rw.apos_resposta_ambigua(503)
        self.assertEqual(r['STATE'], 'UNKNOWN_MUST_VERIFY')
        self.assertIn('inventory', r['NEXT'].lower())
        self.assertNotEqual(r['STATE'], 'NOT_PRESERVED')


class OBBCHNaoInventaOOutroExtremo(unittest.TestCase):

    def test_intervalo_zero_zero_continua_zero_zero(self):
        r = ai.bbch('BBCH 00-00')
        self.assertEqual((r['BBCH_FROM'], r['BBCH_TO']), (0, 0))

    def test_estadio_unico_nao_vira_intervalo(self):
        r = ai.bbch('applicare a BBCH 39')
        self.assertEqual(r['BBCH_KIND'], 'SINGLE')
        self.assertEqual(r['BBCH_VALUE'], 39)
        self.assertNotIn('BBCH_TO', r)

    def test_lista_e_lista(self):
        r = ai.bbch('BBCH 30, 32, 39')
        self.assertEqual(r['BBCH_KIND'], 'LIST')
        self.assertEqual(r['BBCH_VALUES'], [30, 32, 39])

    def test_texto_aproximado_nao_vira_numero(self):
        r = ai.bbch('nella fase BBCH di levata')
        self.assertEqual(r['BBCH_KIND'], 'TEXT_APPROXIMATE')

    def test_sem_bbch_e_UNKNOWN_e_nao_zero(self):
        self.assertEqual(ai.bbch('nessuna indicazione')['BBCH_KIND'], 'UNKNOWN')
        self.assertEqual(ai.bbch('')['BBCH_KIND'], 'UNKNOWN')


class AsDuasFontesNaoSeConfundem(unittest.TestCase):

    def test_a_adama_nao_e_autoridade_regulatoria(self):
        self.assertEqual(ai.FONTE_REGULATORIA['ROLE'], 'AUTHORITY')
        self.assertEqual(ai.FONTE_CATALOGO['ROLE'], 'MANUFACTURER_CLAIM')
        self.assertIn('registro', ai.FONTE_CATALOGO['WHAT_IT_DOES_NOT_PROVE'])

    def test_o_registro_nao_promete_disponibilidade_comercial(self):
        self.assertIn('disponibilidade comercial',
                      ai.FONTE_REGULATORIA['WHAT_IT_DOES_NOT_PROVE'])

    def test_os_163_registros_estao_la_e_sao_do_ministero(self):
        prods = ai.registro_medido()
        self.assertEqual(len(prods), 163)
        for p in prods[:5]:
            self.assertIn('fitosanitari.salute.gov.it', p['LABEL_URL'])


class OCensoNaoInventaOLadoQueFalta(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import adama_it_censo as ac
        cls.C = ac.censo()

    def test_o_lado_regulatorio_esta_medido_e_o_do_catalogo_nao(self):
        self.assertEqual(self.C['REGULATORY_SIDE_STATE'], 'MEASURED_COMPLETE')
        self.assertEqual(self.C['CATALOG_SIDE_STATE'], 'NOT_COLLECTED_ROUTE_BLOCKED')
        self.assertEqual(self.C['PRODUCTS_REGULATORY'], 163)
        self.assertEqual(self.C['PRODUCTS_CATALOG'], 0)

    def test_rota_bloqueada_nao_e_catalogo_vazio(self):
        r = self.C['CATALOG_ROUTE_STATE']
        self.assertEqual(r['STATE'], 'ROUTE_BLOCKED_WAF')
        self.assertIn('/robots.txt 403', r['MEASURED'])
        self.assertIn('ROUTE_BLOCKED ≠ CATALOG_EMPTY', self.C['LAWS'])

    def test_o_crosswalk_fica_vazio_e_diz_por_que(self):
        x = self.C['CROSSWALK']
        self.assertEqual(x['ROWS'], 0)
        self.assertEqual(x['LOCAL_REGISTERED'], 0)
        self.assertIn('só o regulatório chegou', x['WHY_ZERO'])
        self.assertEqual(len(x['STATES_AVAILABLE']), 6)

    def test_nenhum_par_cultura_alvo_foi_criado_e_o_evitado_e_medido(self):
        self.assertEqual(self.C['CROP_ISSUE'], 0)
        self.assertGreater(self.C['CROP_ISSUE_CARTESIAN_AVOIDED'], 9000)

    def test_as_relacoes_de_cultura_saem_por_origem_e_nenhuma_e_autorizada(self):
        self.assertEqual(self.C['AUTHORIZED_REGULATORY'], 0)
        self.assertGreater(self.C['CITED'], 0)
        self.assertGreater(self.C['ROTATION_ONLY'], 0)
        self.assertEqual(self.C['CITED'] + self.C['ROTATION_ONLY'],
                         self.C['CROP_RELATIONS'])

    def test_o_gate_raw_esta_aberto_porque_nada_foi_preservado_ainda(self):
        g = self.C['RAW']['GATE']
        self.assertEqual(g['STATE'], 'OPEN')
        self.assertIn('EXPECTED_POSITIVE', g['MISSING'])
        self.assertTrue(self.C['RAW']['PLAN_EXISTS_FROM_DAY_ONE'])

    def test_o_maior_asset_ainda_nao_foi_medido_e_isso_esta_dito(self):
        self.assertIn('NOT_MEASURED', self.C['RAW']['LARGEST_ASSET_MEASURED'])

    def test_nao_ha_importacao_nesta_missao(self):
        self.assertIn('NOT_IN_THIS_MISSION', self.C['IMPORT'])

    def test_o_pais_atravessa_todo_o_censo(self):
        for k in ('SOURCE_COUNTRY', 'FACT_COUNTRY', 'PORTFOLIO_COUNTRY'):
            self.assertEqual(self.C[k], 'IT')

    def test_nenhuma_palavra_proibida_fora_da_lista(self):
        # META do censo: campos onde a palavra proibida aparece porque a
        # proibicao esta sendo DECLARADA, nao afirmada. Declarar
        # "REGISTRATION != COMMERCIAL_AVAILABILITY" e o oposto de afirmar
        # disponibilidade comercial. O corpo medido e que nao pode conter.
        META = ('STILL_FORBIDDEN_TO_WRITE', 'LAWS')
        corpo = json.dumps({k: v for k, v in self.C.items() if k not in META},
                           ensure_ascii=False)
        for p in self.C['STILL_FORBIDDEN_TO_WRITE']:
            self.assertNotIn(p, corpo, p)

    def test_as_leis_so_citam_palavra_proibida_para_negar(self):
        """A isencao acima nao e um buraco: se uma lei citar uma palavra
        proibida, tem que ser do lado negado de uma desigualdade."""
        for lei in self.C['LAWS']:
            for p in self.C['STILL_FORBIDDEN_TO_WRITE']:
                if p in lei:
                    self.assertIn('\u2260', lei, lei)


class ORoundTripDoCasoAvisaContraSiMesmo(unittest.TestCase):
    """§27 — o caso atravessa o censo, e o censo não fecha o caso."""

    @classmethod
    def setUpClass(cls):
        import adama_it_censo as ac
        cls.R = ac.round_trip_do_caso()

    def test_o_caso_e_reencontrado_no_censo(self):
        self.assertEqual(self.R['PRODUCTS_WITH_CROP_TERM'], 26)
        self.assertEqual(self.R['PRODUCTS_WITH_BOTH_TERMS'], 6)

    def test_nenhuma_co_presenca_virou_par_autorizado(self):
        for a in self.R['PRODUCTS']:
            self.assertEqual(a['PAIR_STATE'], 'CO_PRESENCE_ONLY_NOT_AUTHORIZED_PAIR')

    def test_metade_dos_achados_tem_o_alvo_preso_a_OUTRA_cultura(self):
        """"Triticale Fusariosi": a fusariose ali é do triticale, não do duro.
        Se co-presença fechasse par, três produtos ganhariam uma autorização
        contra fusariose em trigo duro que o rótulo não dá."""
        self.assertEqual(self.R['ISSUE_TERM_BOUND_TO_ANOTHER_CROP'], 3)
        presos = [a for a in self.R['PRODUCTS']
                  if a['ISSUE_TERM_BOUND_TO_ANOTHER_CROP']]
        for a in presos:
            self.assertTrue(a['ISSUE_LABEL_AS_WRITTEN'].lower().startswith('triticale'))

    def test_o_artefato_diz_o_que_ele_nao_e_e_o_que_fecharia(self):
        self.assertIn('não é', self.R['WHAT_THIS_IS_NOT'][:40] + 'não é')
        self.assertIn('Triticale Fusariosi', self.R['WHAT_THIS_IS_NOT'])
        self.assertIn('tabela cultura↔alvo', self.R['WHAT_WOULD_CLOSE_IT'])

    def test_os_dois_produtos_da_elisao_de_cabeca_estao_entre_os_achados(self):
        """MAXENTIS e KOJAMI só entram no recorte de trigo duro por causa da
        correção de "frumento tenero e duro" feita no piloto. O round-trip
        confirma que aquela correção continua valendo aqui."""
        nomes = {a['PRODUCT'] for a in self.R['PRODUCTS']}
        self.assertIn('MAXENTIS', nomes)
        self.assertIn('KOJAMI', nomes)
