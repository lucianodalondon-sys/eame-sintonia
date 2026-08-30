#!/usr/bin/env python3
"""
Provas da FRANÇA — o red team escrito como teste, contra o dado francês real.

Cada classe aqui é um ataque da lista da missão. O critério não é "o código roda":
é **este atalho consegue fabricar um fato francês que ninguém autorizou?**

Os ataques que a missão nomeou, e onde cada um está:

     1 catálogo presente → registro .............. Crosswalk
     2 titular estrangeiro → registro não francês . TitularNaoDecidePais
     3 mesmo nome → mesmo registro ................ Crosswalk
     4 cultura citada → cultura autorizada ........ OrigemDaCultura
     5 lista de culturas × lista de alvos ......... SemProdutoCartesiano
     6 dose → alvo ................................ IdentificadorDeUso
     7 brochura → rótulo .......................... EspecieDocumental
     8 caminho → identidade ....................... ChaveDeStorage
     9 registro → disponibilidade comercial ....... RegistradoNaoEVendido
    11 evidência ES/IT → FR ....................... PaisNaoSeMistura
    12 nova captura → novo registro ............... CapturaNaoERegistro
"""
import os
import sys
import unicodedata
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import adama_fr as fr                                           # noqa: E402

EPHY = os.path.join(ROOT, 'data', 'raw', 'FR', 'anses-ephy')
TEM_DADO = os.path.isfile(os.path.join(EPHY, 'produits_utf8.csv'))
precisa_dado = unittest.skipUnless(
    TEM_DADO, 'E-Phy não baixado: rode `python scripts/ephy_fr.py --baixar`')


class IdentificadorDeUso(unittest.TestCase):
    """Ataque 6: dose → alvo. O identificador francês diz quando NÃO há alvo."""

    def test_tres_pedacos_e_par_ancorado_pela_autoridade(self):
        u = fr.usage_id('Vigne*Trt Part.Aer.*Mildiou(s)')
        self.assertEqual(u['KIND'], fr.TIPO_COM_ALVO)
        self.assertEqual(u['CROP'], 'Vigne')
        self.assertEqual(u['ISSUE'], 'Mildiou(s)')
        self.assertTrue(u['IS_ANCHORED_PAIR'])

    def test_dois_pedacos_nao_tem_alvo_e_nao_ganha_um(self):
        """215 das 582 linhas ADAMA são assim. Preencher aqui fabrica autorização."""
        u = fr.usage_id('Blé*Désherbage')
        self.assertEqual(u['KIND'], fr.TIPO_SEM_ALVO)
        self.assertEqual(u['CROP'], 'Blé')
        self.assertEqual(u['TREATMENT'], 'Désherbage')
        self.assertIsNone(u['ISSUE'])
        self.assertFalse(u['IS_ANCHORED_PAIR'])

    def test_o_tratamento_do_meio_nao_vira_alvo(self):
        """`Trt Part.Aer.` é COMO se aplica, não CONTRA o quê."""
        u = fr.usage_id('Vigne*Trt Part.Aer.*Black rot')
        self.assertNotEqual(u['ISSUE'], 'Trt Part.Aer.')
        self.assertEqual(u['TREATMENT'], 'Trt Part.Aer.')

    def test_mais_de_tres_pedacos_ainda_termina_no_alvo(self):
        u = fr.usage_id('Vigne*Trt Part.Aer.*Sol*Mildiou(s)')
        self.assertEqual(u['CROP'], 'Vigne')
        self.assertEqual(u['ISSUE'], 'Mildiou(s)')
        self.assertEqual(u['TREATMENT'], 'Trt Part.Aer.*Sol')

    def test_vazio_e_ilegivel_nao_viram_par(self):
        for ruim in ('', None, '   ', 'Vigne'):
            with self.subTest(entrada=repr(ruim)):
                u = fr.usage_id(ruim)
                self.assertFalse(u['IS_ANCHORED_PAIR'])
                self.assertIsNone(u['ISSUE'])


class TitularNaoDecidePais(unittest.TestCase):
    """Ataque 2: titular estrangeiro → registro não é francês."""

    def test_entidade_holandesa_com_registro_frances_conta(self):
        self.assertTrue(fr.e_do_grupo('ADAMA Agriculture B.V.'))
        self.assertTrue(fr.e_do_grupo('ADAMA FRANCE SAS'))

    def test_o_pais_vem_do_registro_e_nao_do_titular(self):
        e = fr.escopo_de_pais({'HOLDER': 'ADAMA Agriculture B.V.'})
        self.assertEqual(e['REGISTRATION_COUNTRY'], 'FR')
        self.assertEqual(e['PORTFOLIO_COUNTRY'], 'FR')
        self.assertFalse(e['HOLDER_IS_FRENCH_ENTITY'])

    def test_quem_nao_e_do_grupo_fica_de_fora(self):
        for outro in ('BAYER SAS', 'SYNGENTA FRANCE SAS', 'BASF FRANCE', ''):
            with self.subTest(titular=outro):
                self.assertFalse(fr.e_do_grupo(outro))

    def test_acento_no_titular_nao_esconde_o_grupo(self):
        self.assertTrue(fr.e_do_grupo('Adama Agriculture Bénélux'))

    @precisa_dado
    def test_o_filtro_ingenuo_perderia_registro_frances_de_verdade(self):
        """Medido: 267 do grupo, e 266 se filtrar por `ADAMA FRANCE SAS` exato."""
        todos = fr.registro_medido()
        so_fr = [p for p in todos if fr.dobra(p['HOLDER']).strip() == 'ADAMA FRANCE SAS']
        self.assertGreater(len(todos), len(so_fr))
        perdidos = [p for p in todos if p not in so_fr]
        self.assertTrue(all(p['COUNTRY'] == 'FR' for p in perdidos))


class RegistradoNaoEVendido(unittest.TestCase):
    """Ataque 9: registro → disponibilidade. E a armadilha do número 267."""

    @precisa_dado
    def test_registrado_algum_dia_nao_e_autorizado_hoje(self):
        c = fr.censo()
        self.assertEqual(c['REGULATORY_PRODUCTS_EVER'], 267)
        self.assertEqual(c['REGULATORY_PRODUCTS_AUTHORIZED'], 72)
        self.assertGreater(c['REGULATORY_PRODUCTS_WITHDRAWN'],
                           c['REGULATORY_PRODUCTS_AUTHORIZED'])

    @precisa_dado
    def test_o_recorte_de_autorizados_nao_traz_retirado_nenhum(self):
        vivos = fr.registro_medido(so_autorizados=True)
        self.assertEqual(len(vivos), 72)
        self.assertTrue(all(p['STATE'] == fr.AUTORIZADO for p in vivos))

    @precisa_dado
    def test_autorizado_sem_uso_publicado_nao_vira_zero_silencioso(self):
        """Dois AMMs autorizados não têm linha de uso. Isso é um fato, não um bug."""
        c = fr.censo()
        self.assertEqual(len(c['AMMS_AUTHORIZED_WITHOUT_USE']), 2)


class SemProdutoCartesiano(unittest.TestCase):
    """Ataque 5: lista de culturas × lista de alvos.

    Foi assim que a Itália quase fabricou autorização. Na França o par vem
    amarrado — e a prova é que o número de pares ancorados é MUITO menor do que
    a multiplicação das duas listas.
    """

    @precisa_dado
    def test_pares_ancorados_sao_muito_menos_que_o_produto_das_listas(self):
        usos = fr.usos_medidos({p['REGISTRATION_ID'] for p in fr.registro_medido()})
        culturas = {u['CROP'] for u in usos if u['CROP']}
        alvos = {u['ISSUE'] for u in usos if u['ISSUE']}
        ancorados = {(u['CROP'], u['ISSUE']) for u in usos if u['IS_ANCHORED_PAIR']}
        self.assertEqual(len(ancorados), 161)
        self.assertLess(len(ancorados), len(culturas) * len(alvos) / 10)

    @precisa_dado
    def test_nenhum_par_ancorado_nasce_de_linha_sem_alvo(self):
        usos = fr.usos_medidos({p['REGISTRATION_ID'] for p in fr.registro_medido()})
        for u in usos:
            if u['KIND'] == fr.TIPO_SEM_ALVO:
                self.assertIsNone(u['ISSUE'])
                self.assertFalse(u['IS_ANCHORED_PAIR'])

    @precisa_dado
    def test_cultura_com_dose_e_sem_alvo_continua_sem_alvo(self):
        """Ataque 6 contra o dado real: há dose e não há alvo. A dose não completa o par."""
        usos = fr.usos_medidos({p['REGISTRATION_ID'] for p in fr.registro_medido()})
        com_dose_sem_alvo = [u for u in usos if u['DOSE'] and not u['IS_ANCHORED_PAIR']]
        self.assertGreater(len(com_dose_sem_alvo), 0)
        self.assertTrue(all(u['ISSUE'] is None for u in com_dose_sem_alvo))


class OrigemDaCultura(unittest.TestCase):
    """Ataque 4: cultura citada → cultura autorizada."""

    def test_as_tres_origens_sao_distintas(self):
        self.assertEqual(len(set(fr.ORIGENS_CULTURA)), 3)
        self.assertIn(fr.CROP_REGULATORY, fr.ORIGENS_CULTURA)

    @precisa_dado
    def test_uso_do_ephy_e_sempre_regulatorio_nunca_citado(self):
        usos = fr.usos_medidos({p['REGISTRATION_ID'] for p in fr.registro_medido()})
        self.assertTrue(all(u['RELATION_ORIGIN'] == fr.CROP_REGULATORY for u in usos))


class EspecieDocumental(unittest.TestCase):
    """Ataque 7: brochura → rótulo. O rótulo é ato administrativo; a brochura vende."""

    def test_brochura_nunca_vira_etiqueta(self):
        for nome in ('brochure-produit.pdf', 'plaquette_vigne.pdf',
                     'depliant-2026.pdf'):
            with self.subTest(nome=nome):
                self.assertEqual(fr.tipo_de_documento(nome), fr.BROCHURE)

    def test_a_etiqueta_e_reconhecida(self):
        self.assertEqual(fr.tipo_de_documento('etiquette-NEMO-2090024.pdf'),
                         fr.ETIQUETTE)

    def test_ficha_de_seguranca_nao_e_ficha_tecnica(self):
        self.assertEqual(fr.tipo_de_documento('FDS_EXTASE_GOLD.pdf'),
                         fr.FICHE_SECURITE)
        self.assertEqual(fr.tipo_de_documento('fiche-technique-backpack.pdf'),
                         fr.FICHE_TECHNIQUE)

    def test_pdf_desconhecido_nao_ganha_especie_por_generosidade(self):
        self.assertEqual(fr.tipo_de_documento('document-2026.pdf'), fr.DOC_OUTRO)


class ChaveDeStorage(unittest.TestCase):
    """Ataque 8: caminho → identidade."""

    A = 'a' * 64
    B = 'b' * 64

    def test_mesmo_nome_e_conteudos_diferentes_nao_colidem(self):
        """A cicatriz francesa: 29 PDFs distintos chamados "download.pdf".

        A rota `/media/NNNN/download?attachment` da o mesmo nome a dezenas de
        documentos, e quatro fichas do AMM 2240001 apontam para PDFs diferentes.
        Com chave por NOME, o ultimo upload apagaria os outros sem erro nenhum.
        O teste de colisao do plano RAW pegou isso antes de qualquer upload.
        """
        a = fr.storage_key('FR', '2240001', fr.DOC_OUTRO, 'download.pdf', self.A)
        b = fr.storage_key('FR', '2240001', fr.DOC_OUTRO, 'download.pdf', self.B)
        self.assertNotEqual(a, b)

    def test_mesmo_conteudo_cai_sempre_no_mesmo_lugar(self):
        """Duas capturas do mesmo arquivo sao um objeto so, nao dois."""
        a = fr.storage_key('FR', '1', fr.BROCHURE, 'x.pdf', self.A)
        b = fr.storage_key('FR', '1', fr.BROCHURE, 'x.pdf', self.A)
        self.assertEqual(a, b)

    def test_nfc_faz_o_mesmo_nome_dar_a_mesma_chave(self):
        """Acento composto e decomposto sao o MESMO nome. Em frances isso e comum."""
        composto = unicodedata.normalize('NFC', 'Etiquette Blé.pdf')
        decomposto = unicodedata.normalize('NFD', 'Etiquette Blé.pdf')
        # Sem esta linha o teste vira vazio no dia em que alguem "arrumar" as
        # duas strings digitando as duas do mesmo jeito no editor.
        self.assertNotEqual(composto, decomposto)
        self.assertEqual(
            fr.storage_key('FR', '2090024', fr.ETIQUETTE, composto, self.A),
            fr.storage_key('FR', '2090024', fr.ETIQUETTE, decomposto, self.A))

    def test_sem_o_sha_do_conteudo_a_chave_e_recusada(self):
        """Um valor padrao aqui faria a protecao sumir em quem esqueceu de passa-lo."""
        for ruim in (None, '', 'curto'):
            with self.subTest(sha=repr(ruim)):
                with self.assertRaises(ValueError):
                    fr.storage_key('FR', '1', fr.BROCHURE, 'x.pdf', ruim)

    def test_a_extensao_sobrevive(self):
        self.assertTrue(fr.storage_key('FR', '1', fr.ETIQUETTE, 'x.pdf', self.A)
                        .endswith('.pdf'))

    def test_o_nome_sai_saneado_e_o_original_nao_vive_na_chave(self):
        """Nada de URL-decode nem de espaco: o nome original mora no metadata."""
        k = fr.storage_key('FR', '1', fr.BROCHURE, 'a%20b (2026).pdf', self.A)
        self.assertNotIn('%20', k)
        self.assertNotIn(' ', k)

    def test_o_pais_abre_a_chave_e_nao_se_mistura(self):
        self.assertTrue(fr.storage_key('FR', '1', fr.ETIQUETTE, 'x.pdf', self.A)
                        .startswith('FR/'))

    def test_sem_amm_a_chave_diz_que_nao_tem(self):
        self.assertIn('SEM-AMM',
                      fr.storage_key('FR', None, fr.BROCHURE, 'x.pdf', self.A))


class CapturaNaoERegistro(unittest.TestCase):
    """Ataque 12: nova captura → novo registro."""

    def test_duas_capturas_do_mesmo_amm_sao_um_registro_so(self):
        a = fr.captura('2090024', 'FR-T4-001', '2026-08-25')
        b = fr.captura('2090024', 'FR-T4-001', '2026-09-01')
        self.assertNotEqual(a['CAPTURE_KEY'], b['CAPTURE_KEY'])
        self.assertEqual(a['REGISTRATION_KEY'], b['REGISTRATION_KEY'])

    def test_a_identidade_do_registro_e_pais_mais_amm(self):
        self.assertEqual(fr.captura('2090024', 'x', 'y')['REGISTRATION_KEY'],
                         ('FR', '2090024'))


class Crosswalk(unittest.TestCase):
    """Ataques 1 e 3: presença no catálogo → registro; mesmo nome → mesmo registro."""

    REGISTRO = [
        {'REGISTRATION_ID': '2090024', 'PRODUCT': 'DIODE'},
        {'REGISTRATION_ID': '2150845', 'PRODUCT': 'BACKPACK'},
        {'REGISTRATION_ID': '9900121', 'PRODUCT': 'BACKPACK'},
    ]

    def test_amm_publicado_e_existente_fecha(self):
        r = fr.cruzar({'PRODUCT_NAME': 'DIODE', 'REGISTRATION_ID': '2090024'},
                      self.REGISTRO)
        self.assertEqual(r['STATE'], fr.LOCAL_REGISTERED)

    def test_presenca_no_catalogo_sozinha_nao_prova_registro(self):
        """Ataque 1. Estar na vitrine não é estar autorizado."""
        r = fr.cruzar({'PRODUCT_NAME': 'PRODUTO NOVO'}, self.REGISTRO)
        self.assertEqual(r['STATE'], fr.LOCAL_PRESENT_NOT_PROVED)
        self.assertIsNone(r['REGISTRATION_ID'])

    def test_ausencia_de_casamento_nunca_vira_NOT_REGISTERED(self):
        """Minha falta de casamento não é a autoridade dizendo que não existe."""
        r = fr.cruzar({'PRODUCT_NAME': 'PRODUTO NOVO'}, self.REGISTRO)
        self.assertNotEqual(r['STATE'], fr.NOT_REGISTERED)

    def test_nome_que_bate_com_dois_registros_e_conflito(self):
        """Ataque 3. Dois AMMs com o mesmo nome comercial: escolher é chutar."""
        r = fr.cruzar({'PRODUCT_NAME': 'BACKPACK'}, self.REGISTRO)
        self.assertEqual(r['STATE'], fr.REGISTRATION_CONFLICT)
        self.assertEqual(sorted(r['CANDIDATE_REGISTRATION_IDS']),
                         ['2150845', '9900121'])

    def test_nome_unico_vira_candidato_e_nao_identidade(self):
        r = fr.cruzar({'PRODUCT_NAME': 'DIODE'}, self.REGISTRO)
        self.assertEqual(r['STATE'], fr.LOCAL_PRESENT_NOT_PROVED)
        self.assertEqual(r['CANDIDATE_REGISTRATION_ID'], '2090024')
        self.assertIsNone(r['REGISTRATION_ID'])

    def test_amm_publicado_que_nao_existe_e_conflito(self):
        r = fr.cruzar({'PRODUCT_NAME': 'X', 'REGISTRATION_ID': '0000000'},
                      self.REGISTRO)
        self.assertEqual(r['STATE'], fr.REGISTRATION_CONFLICT)


class UmRegistroMuitosNomes(unittest.TestCase):
    """O achado da amostra de dez, e ele morde nos dois sentidos.

    AMM 2180260 é CARAKOL 3 no E-Phy, e o catálogo francês o vende como BALESTA
    e como GUSTO 3 — duas fichas, um registro. E cinco dos dez nomes de catálogo
    não são o nome registrado.
    """

    CARAKOL = {'REGISTRATION_ID': '2180260', 'PRODUCT': 'CARAKOL 3',
               'SECOND_NAMES': 'OPPOSUM | SURIKATE | GUSTO 3 | TASTE | ALFARO | BALESTA'}
    OUTRO = {'REGISTRATION_ID': '2240236', 'PRODUCT': 'AVASTEL', 'SECOND_NAMES': ''}

    def test_o_segundo_nome_encontra_o_registro(self):
        r = fr.cruzar({'PRODUCT_NAME': 'Balesta'}, [self.CARAKOL, self.OUTRO])
        self.assertEqual(r['CANDIDATE_REGISTRATION_ID'], '2180260')
        self.assertEqual(r['MATCHED_BY'], 'SECOND_NAME')
        self.assertEqual(r['CANDIDATE_REGISTERED_NAME'], 'CARAKOL 3')

    def test_segundo_nome_ainda_nao_e_registro_provado(self):
        """Achar pelo apelido não fecha identidade. Só o AMM fecha."""
        r = fr.cruzar({'PRODUCT_NAME': 'Balesta'}, [self.CARAKOL])
        self.assertEqual(r['STATE'], fr.LOCAL_PRESENT_NOT_PROVED)
        self.assertIsNone(r['REGISTRATION_ID'])

    def test_dois_nomes_do_mesmo_registro_nao_viram_conflito(self):
        """`set` de registros, não de nomes: um alvo alcançado duas vezes é um."""
        registro = [dict(self.CARAKOL, PRODUCT='BALESTA')]   # registrado E segundo
        r = fr.cruzar({'PRODUCT_NAME': 'BALESTA'}, registro)
        self.assertNotEqual(r['STATE'], fr.REGISTRATION_CONFLICT)

    def test_duas_fichas_com_o_mesmo_amm_sao_um_registro_so(self):
        """CATALOG_ENTRY ≠ REGISTRATION. Somar fichas contaria o mesmo duas vezes."""
        fichas = [{'PRODUCT_NAME': 'Balesta', 'REGISTRATION_ID': '2180260'},
                  {'PRODUCT_NAME': 'Gusto 3', 'REGISTRATION_ID': '2180260'}]
        ids = {fr.cruzar(f, [self.CARAKOL])['REGISTRATION_ID'] for f in fichas}
        self.assertEqual(len(fichas), 2)
        self.assertEqual(len(ids), 1)

    def test_a_razao_social_sai_do_titulo_e_o_produto_fica(self):
        for sujo, limpo in (('Balesta - ADAMA France sas', 'Balesta'),
                            ('Exelgrow - ADAMA France sas', 'Exelgrow'),
                            ('Banjo Extra - ADAMA France sas', 'Banjo Extra'),
                            ('Avastel', 'Avastel'),
                            ('Klartan Up', 'Klartan Up')):
            with self.subTest(titulo=sujo):
                self.assertEqual(fr.nome_comercial(sujo), limpo)

    def test_a_limpeza_nao_come_produto_que_se_chama_adama(self):
        """Só o sufixo de razão social sai. Nome que contém a palavra fica inteiro."""
        self.assertEqual(fr.nome_comercial('ADAMA Force'), 'ADAMA Force')

    def test_titulo_sujo_encontra_o_registro_que_o_sujo_perderia(self):
        reg = [{'REGISTRATION_ID': '2070185', 'PRODUCT': 'BANJO EXTRA',
                'SECOND_NAMES': ''}]
        sujo = fr.cruzar({'PRODUCT_NAME': 'Banjo Extra - ADAMA France sas'}, reg)
        self.assertEqual(sujo['CANDIDATE_REGISTRATION_ID'], '2070185')

    @precisa_dado
    def test_no_dado_real_ha_registro_com_varios_nomes_comerciais(self):
        reg = fr.registro_medido()
        muitos = [r for r in reg if len(fr.nomes_do_registro(r)) > 3]
        self.assertGreater(len(muitos), 0)


class PaisNaoSeMistura(unittest.TestCase):
    """Ataque 11: evidência espanhola ou italiana fechando fato francês."""

    @precisa_dado
    def test_toda_linha_francesa_carrega_FR(self):
        for p in fr.registro_medido()[:50]:
            self.assertEqual(p['COUNTRY'], 'FR')
        usos = fr.usos_medidos({p['REGISTRATION_ID'] for p in fr.registro_medido()})
        self.assertTrue(all(u['COUNTRY'] == 'FR' for u in usos))

    def test_a_fonte_regulatoria_francesa_nao_e_a_espanhola_nem_a_italiana(self):
        self.assertEqual(fr.FONTE_REGULATORIA['SOURCE_ID'], 'FR-T4-001')
        self.assertNotIn('salute.gov.it', fr.FONTE_REGULATORIA['URL'])
        self.assertNotIn('mapa.gob.es', fr.FONTE_REGULATORIA['URL'])

    def test_o_catalogo_nao_e_autoridade_e_diz_isso_de_si_mesmo(self):
        self.assertEqual(fr.FONTE_CATALOGO['ROLE'], 'MANUFACTURER_CLAIM')
        self.assertEqual(fr.FONTE_REGULATORIA['ROLE'], 'REGULATORY_AUTHORITY')
        self.assertIn('registro', fr.FONTE_CATALOGO['WHAT_IT_DOES_NOT_PROVE'])


class CrosswalkNaoInfla(unittest.TestCase):

    REG = [{'REGISTRATION_ID': '2180260', 'PRODUCT': 'CARAKOL 3',
            'SECOND_NAMES': 'GUSTO 3 | BALESTA', 'STATE': 'AUTORISE'},
           {'REGISTRATION_ID': '2240236', 'PRODUCT': 'AVASTEL',
            'SECOND_NAMES': '', 'STATE': 'AUTORISE'}]

    def test_duas_fichas_de_um_amm_contam_um_registro(self):
        fichas = [{'PRODUCT_NAME': 'Balesta', 'REGISTRATION_ID_CLAIMED': '2180260'},
                  {'PRODUCT_NAME': 'Gusto 3', 'REGISTRATION_ID_CLAIMED': '2180260'}]
        c = fr.crosswalk(fichas, self.REG)
        self.assertEqual(c['CATALOG_ENTRIES'], 2)
        self.assertEqual(c['DISTINCT_REGISTRATIONS_BEHIND_CATALOG'], 1)

    def test_registrado_e_ausente_da_vitrine_e_contado(self):
        fichas = [{'PRODUCT_NAME': 'Balesta', 'REGISTRATION_ID_CLAIMED': '2180260'}]
        c = fr.crosswalk(fichas, self.REG)
        self.assertGreaterEqual(c['REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG'], 1)

    def test_ficha_com_registro_retirado_e_contada_e_nomeada(self):
        """A vitrine mostra 5 produtos com registro retirado. Isso precisa aparecer."""
        reg = [{'REGISTRATION_ID': '2200620', 'PRODUCT': 'SUNSET',
                'SECOND_NAMES': '', 'STATE': 'RETIRE', 'WITHDRAWN': '31/01/2025'}]
        c = fr.crosswalk([{'PRODUCT_NAME': 'Sunset',
                           'REGISTRATION_ID_CLAIMED': '2200620'}], reg)
        self.assertEqual(c['IN_CATALOG_BUT_REGISTRATION_WITHDRAWN'], 1)
        self.assertEqual(c['CATALOG_SHOWING_WITHDRAWN'][0]['WITHDRAWN'], '31/01/2025')

    def test_estar_na_vitrine_nao_prova_autorizacao_vigente(self):
        """LOCAL_REGISTERED diz que o AMM existe, não que ele vale hoje."""
        reg = [{'REGISTRATION_ID': '2200620', 'PRODUCT': 'SUNSET',
                'SECOND_NAMES': '', 'STATE': 'RETIRE', 'WITHDRAWN': '31/01/2025'}]
        c = fr.crosswalk([{'PRODUCT_NAME': 'Sunset',
                           'REGISTRATION_ID_CLAIMED': '2200620'}], reg)
        self.assertEqual(c['STATES'].get(fr.LOCAL_REGISTERED), 1)
        self.assertEqual(c['REGULATORY_AUTHORIZED'], 0)

    def test_amm_de_titular_de_fora_do_grupo_vira_conflito_e_nao_fato(self):
        """A ficha Milena publica um AMM da GLOBACHEM. Engolir isso inflaria o portfólio."""
        c = fr.crosswalk([{'PRODUCT_NAME': 'Milena',
                           'REGISTRATION_ID_CLAIMED': '2250282'}], self.REG)
        self.assertEqual(c['STATES'].get(fr.REGISTRATION_CONFLICT), 1)
        self.assertEqual(c['DISTINCT_REGISTRATIONS_BEHIND_CATALOG'], 0)

    def test_not_registered_fica_em_zero_e_explica(self):
        """Nunca por eliminação. Zero aqui é uma recusa, não uma contagem."""
        c = fr.crosswalk([{'PRODUCT_NAME': 'INEXISTENTE'}], self.REG)
        self.assertEqual(c['NOT_REGISTERED'], 0)
        self.assertIn('exige a autoridade', c['WHY_NOT_REGISTERED_ZERO'])


class CensoNaoMente(unittest.TestCase):

    @precisa_dado
    def test_o_catalogo_sai_nulo_e_nao_zero(self):
        """Zero diria "a ADAMA não apresenta nada na França". Nulo diz "não medi"."""
        c = fr.censo()
        self.assertIsNone(c['CATALOG_PRODUCTS'])
        self.assertIn('não foi medido', c['WHY_CATALOG_NULL'])

    @precisa_dado
    def test_as_somas_fecham(self):
        c = fr.censo()
        self.assertEqual(c['REGULATORY_PRODUCTS_AUTHORIZED']
                         + c['REGULATORY_PRODUCTS_WITHDRAWN'],
                         c['REGULATORY_PRODUCTS_EVER'])
        self.assertEqual(c['CROP_ISSUE_ANCHORED_ROWS']
                         + c['CROP_TREATMENT_NO_ISSUE_ROWS'],
                         c['USE_ROWS'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
