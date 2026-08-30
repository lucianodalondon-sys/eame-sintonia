#!/usr/bin/env python3
"""
RED TEAM FRANCÊS — os quinze atalhos, cada um como um teste que tenta passar.

Um atalho aqui não é preguiça de código: é uma frase que alguém vai escrever num
relatório porque ela é curta, verdadeira-parecida e cabe num slide. "A ADAMA tem
111 produtos na França" é assim. O trabalho destes testes é fazer cada frase
dessas cair antes de virar número publicado.

    1  111 fichas -> 111 registros
    2  nome de catálogo -> nome registrado
    3  site da ADAMA -> titular ADAMA
    4  site atual -> autorização vigente
    5  AMM de terceiro -> conflito automático
    6  culturas × alvos do site -> pares autorizados
    7  PDF "download" -> mesmo documento
    8  mesmo hash -> apagar procedência
    9  267 histórico -> portfólio atual
    10 72 ADAMA-held -> tudo que a ADAMA apresenta
    11 15 fora do catálogo -> descontinuado
    12 retirado -> indisponível comercialmente
    13 nome do arquivo -> tipo do documento
    14 nome da página -> identidade do produto
    15 AMM -> um nome comercial só
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import adama_fr as fr                                            # noqa: E402
import adama_fr_catalogo as cat                                  # noqa: E402
import adama_fr_documentos as doc                                # noqa: E402

EPHY = os.path.join(ROOT, 'data', 'raw', 'FR', 'anses-ephy', 'produits_utf8.csv')
MANIFESTO = os.path.join(ROOT, 'data', 'raw', 'FR', 'adama-website',
                         'MANIFESTO-CATALOGO.json')
TEM_EPHY = os.path.isfile(EPHY)
TEM_CATALOGO = os.path.isfile(MANIFESTO)

precisa_ephy = unittest.skipUnless(TEM_EPHY, 'E-Phy não baixado nesta máquina')
precisa_tudo = unittest.skipUnless(TEM_EPHY and TEM_CATALOGO,
                                   'E-Phy ou catálogo não coletados nesta máquina')


def fichas():
    with open(MANIFESTO, encoding='utf-8') as fh:
        return json.load(fh)['PRODUCTS']


def documentos():
    with open(MANIFESTO, encoding='utf-8') as fh:
        return json.load(fh)['DOCUMENTS']


# ══════════════════════════════════════════════════════════════════════════════

class A01_FichaNaoERegistro(unittest.TestCase):
    """111 fichas → 111 registros."""

    @precisa_tudo
    def test_o_catalogo_tem_menos_registros_do_que_fichas(self):
        c = fr.crosswalk()
        self.assertEqual(c['CATALOG_PUBLIC_PRESENTATIONS'], 111)
        self.assertEqual(c['CATALOG_DISTINCT_AMMS'], 63)
        self.assertLess(c['CATALOG_DISTINCT_AMMS'],
                        c['CATALOG_PUBLIC_PRESENTATIONS'])

    @precisa_tudo
    def test_as_somas_do_catalogo_fecham(self):
        """Se não fecham, algum AMM foi contado duas vezes ou sumiu."""
        c = fr.crosswalk()
        self.assertEqual(c['CATALOG_CURRENT_ADAMA_HELD_AMMS']
                         + c['CATALOG_CURRENT_THIRD_PARTY_HELD_AMMS']
                         + c['CATALOG_WITHDRAWN_AMMS']
                         + c['CATALOG_AMM_NOT_FOUND_IN_EPHY'],
                         c['CATALOG_DISTINCT_AMMS'])


class A02_NomeDeCatalogoNaoENomeRegistrado(unittest.TestCase):
    """Nome de catálogo → nome registrado."""

    @precisa_tudo
    def test_ha_ficha_cujo_nome_nao_e_o_nome_do_registro(self):
        indice = fr.registro_completo()
        divergentes = []
        for f in fichas():
            amm = f.get('REGISTRATION_ID_CLAIMED')
            r = indice.get(str(amm or ''))
            if r and fr._chave_nome(f['PRODUCT_NAME']) != fr._chave_nome(r['PRODUCT']):
                divergentes.append((f['PRODUCT_NAME'], r['PRODUCT']))
        self.assertGreater(len(divergentes), 0,
                           'se nenhum divergisse, casar por nome seria seguro — e não é')

    def test_o_segundo_nome_e_o_que_salva_o_casamento(self):
        reg = [{'REGISTRATION_ID': '2180260', 'PRODUCT': 'CARAKOL 3',
                'SECOND_NAMES': 'GUSTO 3 | BALESTA'}]
        r = fr.cruzar({'PRODUCT_NAME': 'Balesta'}, reg)
        self.assertEqual(r['MATCHED_BY'], 'SECOND_NAME')


class A03_SiteDaAdamaNaoETitularAdama(unittest.TestCase):
    """Site da ADAMA → titular ADAMA."""

    def test_terceiro_e_marcado_como_terceiro(self):
        indice = {'2250282': {'REGISTRATION_ID': '2250282', 'PRODUCT': 'HARNIKO',
                              'HOLDER': 'GLOBACHEM NV', 'STATE': 'AUTORISE',
                              'WITHDRAWN': ''}}
        r = fr.resolver_amm('2250282', indice)
        self.assertEqual(r['CLASS'], fr.CURRENT_THIRD_PARTY_HELD)
        self.assertEqual(r['ADAMA_HOLDER'], 'NO')

    @precisa_tudo
    def test_no_dado_real_existe_pelo_menos_um_terceiro(self):
        c = fr.crosswalk()
        self.assertGreaterEqual(c['CATALOG_CURRENT_THIRD_PARTY_HELD_AMMS'], 1)
        self.assertTrue(all(d['HOLDER'] for d in c['THIRD_PARTY_HELD_DETAIL']))


class A04_SiteAtualNaoEAutorizacaoVigente(unittest.TestCase):
    """Site atual → autorização vigente."""

    def test_ficha_publicada_com_registro_retirado_e_reconhecida(self):
        indice = {'2200620': {'REGISTRATION_ID': '2200620', 'PRODUCT': 'SUNSET',
                              'HOLDER': 'ADAMA FRANCE SAS', 'STATE': 'RETIRE',
                              'WITHDRAWN': '31/01/2025'}}
        r = fr.resolver_amm('2200620', indice)
        self.assertEqual(r['CLASS'], fr.WITHDRAWN_ADAMA_HELD)
        self.assertEqual(r['WITHDRAWAL_DATE'], '31/01/2025')

    @precisa_tudo
    def test_os_cinco_retirados_seguem_na_vitrine_e_saem_com_data(self):
        c = fr.crosswalk()
        self.assertEqual(c['IN_CATALOG_BUT_REGISTRATION_WITHDRAWN'], 5)
        for d in c['CATALOG_SHOWING_WITHDRAWN']:
            self.assertEqual(d['CATALOG_PRESENT'], 'YES')
            self.assertEqual(d['AUTHORIZATION_CURRENT'], 'NO')
            self.assertTrue(d['WITHDRAWAL_DATE'])


class A05_TerceiroNaoEConflito(unittest.TestCase):
    """AMM de terceiro → conflito automático. Este ataque JÁ passou uma vez.

    A primeira versão marcava a Milena como REGISTRATION_CONFLICT. O AMM saía do
    total e o catálogo aparecia com 62 registros distintos em vez de 63.
    """

    def test_presenca_no_catalogo_e_titularidade_alheia_coexistem(self):
        indice = {'2250282': {'REGISTRATION_ID': '2250282', 'PRODUCT': 'HARNIKO',
                              'HOLDER': 'GLOBACHEM NV', 'STATE': 'AUTORISE',
                              'WITHDRAWN': ''}}
        r = fr.resolver_amm('2250282', indice)
        self.assertNotEqual(r['CLASS'], fr.AMBIGUOUS_CONFLICT)
        self.assertTrue(r['E_PHY_FOUND'])

    @precisa_tudo
    def test_o_terceiro_entra_na_contagem_e_nao_some(self):
        c = fr.crosswalk()
        self.assertEqual(c['CATALOG_AMM_NOT_FOUND_IN_EPHY'], 0)
        self.assertEqual(c['BY_CLASS'].get(fr.AMBIGUOUS_CONFLICT, 0), 0)

    def test_amm_ausente_do_registro_nao_vira_NOT_REGISTERED(self):
        r = fr.resolver_amm('9999999', {})
        self.assertEqual(r['CLASS'], fr.AMM_NOT_FOUND_IN_EPHY)
        self.assertIn('NÃO é NOT_REGISTERED', r['WHY'])


class A06_ListasDoSiteNaoSaoPares(unittest.TestCase):
    """Culturas × alvos do site → pares autorizados."""

    @precisa_tudo
    def test_nenhum_par_nasce_do_catalogo(self):
        total = 0
        cartesiano = 0
        for f in fichas():
            p = f['CROP_ISSUE_PAIRS']
            total += len(p['PAIRS'])
            cartesiano += p['CARTESIAN_WOULD_BE']
        self.assertEqual(total, 0)
        self.assertGreater(cartesiano, 9000,
                           'o cartesiano evitado tem de ser grande, senão não havia risco')

    @precisa_tudo
    def test_a_fonte_do_par_e_declarada_e_e_o_ephy(self):
        c = fr.crosswalk()
        self.assertEqual(c['AUTHORISED_CROP_ISSUE_SOURCE'], 'E_PHY')
        self.assertEqual(c['CATALOG_CROP_ISSUE'], 'NOT_RECONSTRUCTED')


class A07_DownloadNaoEUmDocumentoSo(unittest.TestCase):
    """PDF "download" → mesmo documento."""

    def test_urls_diferentes_com_o_mesmo_basename_dao_arquivos_diferentes(self):
        a = cat.nome_local_documento('https://x/france/fr/media/2006/download?attachment')
        b = cat.nome_local_documento('https://x/france/fr/media/2331/download?attachment')
        self.assertNotEqual(a, b)

    def test_a_mesma_url_da_sempre_o_mesmo_arquivo(self):
        u = 'https://x/france/fr/media/2006/download?attachment'
        self.assertEqual(cat.nome_local_documento(u), cat.nome_local_documento(u))

    @precisa_tudo
    def test_cada_documento_tem_seu_proprio_arquivo_em_disco(self):
        """O defeito real: 153 referências viraram 100 arquivos, e 53 sumiram."""
        d = documentos()
        caminhos = [x['LOCAL_PATH'] for x in d if x.get('LOCAL_PATH')]
        self.assertEqual(len(caminhos), len(set(caminhos)))
        for c in caminhos:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, c)), c)


class A08_MesmoHashNaoApagaProcedencia(unittest.TestCase):
    """Mesmo hash → apagar procedência."""

    @precisa_tudo
    def test_documento_citado_por_varias_fichas_guarda_todas(self):
        d = documentos()
        varios = [x for x in d if (x.get('CATALOG_PAGE_COUNT') or 0) > 1]
        self.assertGreater(len(varios), 0)
        for x in varios:
            self.assertEqual(len(x['REFERENCED_BY']), x['CATALOG_PAGE_COUNT'])
            self.assertGreater(len(x['CATALOG_NAMES']), 0)

    @precisa_tudo
    def test_o_amm_da_ficha_e_o_amm_do_documento_ficam_separados(self):
        """Quem cita não é quem declara. São duas afirmações diferentes."""
        for x in documentos():
            self.assertIn('AMMS_FROM_REFERRING_PAGES', x)
            self.assertIn('AMMS_IN_DOCUMENT_TEXT', x)

    @precisa_tudo
    def test_documento_compartilhado_por_amms_diferentes_nao_finge_ter_dono(self):
        compartilhados = [x for x in documentos()
                          if len(x.get('AMMS_FROM_REFERRING_PAGES') or []) > 1]
        for x in compartilhados:
            self.assertEqual(x['RELATED_REGISTRATION'], 'PARTAGE')


class A09_HistoricoNaoEPortfolio(unittest.TestCase):
    """267 histórico → portfólio atual."""

    @precisa_ephy
    def test_o_267_inclui_195_retirados(self):
        c = fr.censo()
        self.assertEqual(c['REGULATORY_PRODUCTS_EVER'], 267)
        self.assertEqual(c['REGULATORY_PRODUCTS_AUTHORIZED'], 72)
        self.assertEqual(c['REGULATORY_PRODUCTS_WITHDRAWN'], 195)

    @precisa_ephy
    def test_o_recorte_vigente_nao_traz_retirado(self):
        for p in fr.registro_medido(so_autorizados=True):
            self.assertEqual(p['STATE'], fr.AUTORIZADO)


class A10_TitularNaoCobreTudoQueEApresentado(unittest.TestCase):
    """72 ADAMA-held → tudo que a ADAMA apresenta."""

    @precisa_tudo
    def test_ha_ficha_apresentada_pela_adama_fora_dos_72(self):
        c = fr.crosswalk()
        self.assertGreater(c['CATALOG_CURRENT_THIRD_PARTY_HELD_AMMS'], 0)

    @precisa_tudo
    def test_os_universos_sao_declarados_separados(self):
        c = fr.crosswalk()
        for k in ('CATALOG_PUBLIC_PRESENTATIONS', 'CATALOG_DISTINCT_AMMS',
                  'ADAMA_HELD_CURRENT_REGISTRATIONS'):
            self.assertIn(k, c)
        self.assertIn('universos', c['WHY_NOT_A_SINGLE_NUMBER'])

    @precisa_tudo
    def test_vitrine_mais_fora_da_vitrine_fecha_nos_72(self):
        c = fr.crosswalk()
        self.assertEqual(c['CATALOG_CURRENT_ADAMA_HELD_AMMS']
                         + c['CURRENT_ADAMA_HELD_NOT_OBSERVED_IN_PUBLIC_CATALOG'],
                         c['ADAMA_HELD_CURRENT_REGISTRATIONS'])


class A11_ForaDaVitrineNaoEDescontinuado(unittest.TestCase):
    """15 fora do catálogo → descontinuado."""

    @precisa_tudo
    def test_o_estado_e_nao_observado_e_nao_um_juizo(self):
        c = fr.crosswalk()
        self.assertEqual(c['CURRENT_ADAMA_HELD_NOT_OBSERVED_IN_PUBLIC_CATALOG'], 15)
        proibidas = ('DISCONTINUED', 'NOT_SOLD', 'INACTIVE', 'LOW_PRIORITY')
        for d in c['CURRENT_ADAMA_HELD_NOT_IN_CATALOG_DETAIL']:
            self.assertEqual(d['STATE'],
                             'CURRENT_ADAMA_HELD_NOT_OBSERVED_IN_PUBLIC_CATALOG')
            for p in proibidas:
                self.assertNotIn(p, json.dumps(d))


class A12_RetiradoNaoEIndisponivel(unittest.TestCase):
    """Retirado → indisponível comercialmente."""

    @precisa_tudo
    def test_nenhuma_saida_afirma_disponibilidade(self):
        c = fr.crosswalk()
        texto = json.dumps(c, ensure_ascii=False).upper()
        for p in ('AVAILABLE', 'IN_STOCK', 'SELLING', 'MARKET_SHARE',
                  'COMMERCIAL_PRIORITY'):
            self.assertNotIn(p, texto)

    def test_a_fonte_regulatoria_declara_o_que_nao_prova(self):
        naoprova = ' '.join(fr.FONTE_REGULATORIA['WHAT_IT_DOES_NOT_PROVE']).lower()
        self.assertIn('disponibilidade', naoprova)


class A13_NomeDoArquivoNaoEOTipo(unittest.TestCase):
    """Nome do arquivo → tipo do documento."""

    def test_a_mencao_legal_obrigatoria_nao_faz_folheto_virar_rotulo(self):
        """95 de 122 contêm a palavra `étiquette`. Nenhum vira rótulo por isso."""
        t = ("PRODUITS POUR LES PROFESSIONNELS : AVANT TOUTE UTILISATION, "
             "LISEZ L'ÉTIQUETTE ET LES INFORMATIONS CONCERNANT LE PRODUIT.")
        r = doc.tipar(t, doc.TEXTO_OK)
        self.assertNotEqual(r['DOC_TYPE'], doc.ETIQUETTE)
        self.assertEqual(r['DOC_TYPE'], doc.BROCHURE)

    def test_o_rotulo_exige_o_titular_da_autorizacao(self):
        t = ("Détenteur de l'autorisation : ADAMA France SAS. AMM n° 2240236. "
             "Usages autorisés. H302")
        self.assertEqual(doc.tipar(t, doc.TEXTO_OK)['DOC_TYPE'], doc.ETIQUETTE)

    def test_ficha_tecnica_exige_amm_e_tabela_de_usos(self):
        t = 'AVASTEL AMM n° 2240236 — usages autorisés : blé, orge. H302'
        self.assertEqual(doc.tipar(t, doc.TEXTO_OK)['DOC_TYPE'], doc.FICHE_TECHNIQUE)

    def test_texto_embaralhado_nao_ganha_tipo_por_generosidade(self):
        r = doc.tipar('\x00&\x00/\x00.', doc.TEXTO_EMBARALHADO, 'fonte sem mapa')
        self.assertEqual(r['DOC_TYPE'], doc.DESCONHECIDO)

    def test_desconhecido_e_outro_nao_sao_a_mesma_coisa(self):
        """UNKNOWN é "não li"; OTHER é "li, e não é nenhum tipo conhecido"."""
        self.assertNotEqual(doc.DESCONHECIDO, doc.OUTRO)
        lido = doc.tipar('texto qualquer sem sinal nenhum', doc.TEXTO_OK)
        self.assertEqual(lido['DOC_TYPE'], doc.OUTRO)

    @precisa_tudo
    def test_o_numero_de_desconhecidos_e_exato_e_nao_arredondado(self):
        r = doc.medir()
        self.assertEqual(r['UNKNOWN_DOCUMENT_TYPE'] + r['TYPED'], r['DOCUMENTS'])
        self.assertEqual(r['STATE'], 'PARTIAL_WITH_EXACT_UNKNOWN_COUNT')


class A14_NomeDaPaginaNaoEIdentidade(unittest.TestCase):
    """Nome da página → identidade do produto."""

    @precisa_tudo
    def test_o_titulo_bruto_e_guardado_junto_do_nome_derivado(self):
        for f in fichas():
            self.assertIn('PAGE_TITLE_RAW', f)
            self.assertIn('PRODUCT_NAME', f)

    def test_a_identidade_do_registro_e_pais_mais_amm_nunca_o_nome(self):
        c = fr.captura('2240236', 'FR-T4-001', '2026-08-25')
        self.assertEqual(c['REGISTRATION_KEY'], ('FR', '2240236'))

    def test_a_chave_de_storage_nao_e_identidade(self):
        """PATH ≠ IDENTITY: mesmo conteúdo, dois nomes, um objeto."""
        sha = 'c' * 64
        a = fr.storage_key('FR', '1', fr.BROCHURE, 'download.pdf', sha)
        b = fr.storage_key('FR', '1', fr.BROCHURE, 'download.pdf', sha)
        self.assertEqual(a, b)


class A15_UmAmmMuitosNomes(unittest.TestCase):
    """AMM → um nome comercial só."""

    @precisa_tudo
    def test_ha_amm_com_varias_fichas_no_catalogo(self):
        c = fr.crosswalk()
        muitos = [e for e in c['BY_AMM'] if e['CATALOG_PAGE_COUNT'] > 1]
        self.assertGreater(len(muitos), 0)
        maior = max(e['CATALOG_PAGE_COUNT'] for e in c['BY_AMM'])
        self.assertGreaterEqual(maior, 5)

    @precisa_ephy
    def test_o_registro_lista_os_segundos_nomes_e_eles_sao_usados(self):
        reg = {r['REGISTRATION_ID']: r for r in fr.registro_medido()}
        alvo = reg.get('2180260')
        if alvo:
            nomes = fr.nomes_do_registro(alvo)
            self.assertGreater(len(nomes), 3)
            self.assertIn('CARAKOL 3', nomes)


if __name__ == '__main__':
    unittest.main(verbosity=2)
