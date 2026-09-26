#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PESQUISADORES-T6: as consultas, o teto, a unidade do contrato T6, a deduplicacao, a prova
da pessoa e a regra do QUALIFY. Tudo SEM REDE (o transporte e trocado por um que falha)."""
import os
import sys
import unittest
from urllib.parse import parse_qs, urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'curadoria'))
import pesquisadores_t6 as T6          # noqa: E402
import atribuir_source_id as ASI       # noqa: E402

NS = T6.NAO_SEI


def inv(frase):
    """Frase → indice invertido do OpenAlex."""
    out = {}
    for i, p in enumerate(frase.split()):
        out.setdefault(p, []).append(i)
    return out


def obra(doi, titulo, resumo='', autores=None, data='2024-05-01', tipo='article'):
    return {'id': 'https://openalex.org/W' + doi.replace('/', '').replace('.', ''),
            'doi': 'https://doi.org/' + doi if doi else None, 'title': titulo,
            'publication_date': data, 'type': tipo,
            'abstract_inverted_index': inv(resumo) if resumo else None,
            'primary_location': {'source': {'type': 'journal'}},
            'authorships': autores if autores is not None else [autor('A1', 'Ana Rossi', 'IT', '0000-0001-0000-0001')]}


def autor(aid, nome, pais, orcid=None, inst='Universita X'):
    return {'author': {'id': 'https://openalex.org/' + aid, 'display_name': nome,
                       'orcid': ('https://orcid.org/' + orcid) if orcid else None},
            'institutions': [{'display_name': inst, 'country_code': pais, 'ror': None}]}


class SemRede(unittest.TestCase):
    def setUp(self):
        self._get = T6.CP._get

        def proibido(*a, **k):
            raise AssertionError('pedido a rede num teste')
        T6.CP._get = proibido

    def tearDown(self):
        T6.CP._get = self._get


class Consultas(SemRede):
    def test_doze_pares_uma_consulta_cada_com_filtro_de_pessoa_italiana(self):
        qs = T6.consultas()
        self.assertEqual(len(qs), 12)
        self.assertEqual(len({q['PAR'] for q in qs}), 12)
        for q in qs:
            u = urlparse(q['URL'])
            self.assertEqual(u.netloc, 'api.openalex.org')
            p = parse_qs(u.query)
            self.assertIn('institutions.country_code:it', p['filter'][0])
            self.assertIn('from_publication_date:2019-01-01', p['filter'][0])
            self.assertEqual(p['per-page'], ['200'])
            self.assertIn('doi', p['select'][0])

    def test_o_teto_de_cinco_por_dominio_nunca_e_passado(self):
        pl = T6.plano_de_rodadas(n_dois=81, n_pessoas=11)
        self.assertEqual(pl['PEDIDOS_POR_DOMINIO'],
                         {'api.openalex.org': 12, 'api.crossref.org': 3, 'pub.orcid.org': 11})
        self.assertEqual(pl['RODADAS_POR_DOMINIO'],
                         {'api.openalex.org': 3, 'api.crossref.org': 1, 'pub.orcid.org': 3})
        self.assertEqual(T6.TETO_POR_DOMINIO, 5)

    def test_um_pedido_ao_crossref_leva_varios_doi(self):
        u = T6.url_crossref(['10.1/a', '10.1/b'])
        self.assertIn('doi%3A10.1%2Fa%2Cdoi%3A10.1%2Fb', u)


class Respostas(SemRede):
    def test_http_200_com_corpo_de_orcamento_nao_e_zero_trabalhos(self):
        ok, porque = T6.resposta_valida({'error': 'Rate limit exceeded',
                                         'message': 'Insufficient budget'})
        self.assertFalse(ok)
        self.assertIn('FALHA_ORCAMENTO', porque)
        self.assertEqual(T6.resposta_valida({'meta': {}, 'results': []}), (True, ''))


class Unidade(SemRede):
    def test_afiliacao_italiana_nao_e_local_do_estudo(self):
        u = T6.unidade(obra('10.1/x', 'Plasmopara viticola in grapevine leaves',
                            'We studied downy mildew resistance genes.'), {'vite x peronospora'})
        self.assertTrue(u['AUTORES'][0]['AFILIACAO_ITALIANA_NESTA_OBRA'])
        self.assertEqual(u['LOCAL_DO_ESTUDO_ESCRITO'], NS)

    def test_regiao_nomeada_no_resumo_e_local_escrito_com_o_termo(self):
        u = T6.unidade(obra('10.1/x', 'Flavescence doree in vineyards',
                            'Surveys were carried out in Piedmont vineyards.'), set())
        self.assertEqual([(l['VALOR'], l['TERMO'], l['ORIGEM']) for l in u['LOCAL_DO_ESTUDO_ESCRITO']],
                         [('Piemonte', 'piedmont', 'ESCRITO')])

    def test_publicacao_nunca_vira_periodo_e_decada_nao_e_periodo(self):
        u = T6.unidade(obra('10.1/x', 'Scaphoideus titanus control', 'In the 1990s the vector spread.',
                            data='2023-01-17'), set())
        self.assertEqual(u['PERIODO_DO_ESTUDO'], NS)
        self.assertEqual(u['PUBLICADO_EM'], '2023-01-17')
        u = T6.unidade(obra('10.1/x', 'Vectors in vineyards', 'Samples were collected during 2021–2022 in Italy.'),
                       set())
        self.assertEqual([(p['DE'], p['ATE']) for p in u['PERIODO_DO_ESTUDO']], [('2021', '2022')])

    def test_consulta_nao_e_prova(self):
        # a consulta vite x peronospora trouxe-o, mas o texto so fala de botrite
        u = T6.unidade(obra('10.1/x', 'Botrytis cinerea on grapevine', ''), {'vite x peronospora'})
        self.assertEqual(u['CONSULTAS_QUE_O_TROUXERAM'], ['vite x peronospora'])
        self.assertEqual(u['NA_CONSULTA_E_NO_TEXTO'], [])
        self.assertEqual([p['VALOR'] for p in u['PROBLEMA']], ['botrite'])

    def test_orcid_do_indice_nao_e_prova_ate_o_proprio_orcid_declarar_o_doi(self):
        us = [T6.unidade(obra('10.1/x', 'Downy mildew of grapevine'), set())]
        self.assertEqual(us[0]['AUTORES'][0]['PROVA_DA_PESSOA'], 'SO_INDICE')
        T6.provar_pessoas(us, {'0000-0001-0000-0001': {'10.1/outro'}})
        self.assertEqual(us[0]['AUTORES'][0]['PROVA_DA_PESSOA'], 'ORCID_LIDO_SEM_ESTE_DOI')
        T6.provar_pessoas(us, {'0000-0001-0000-0001': {'10.1/x'}})
        self.assertEqual(us[0]['AUTORES'][0]['PROVA_DA_PESSOA'], 'ORCID_AUTODECLARADO')

    def test_molecula_so_do_lexico_e_o_resto_nao_sei(self):
        self.assertGreaterEqual(len(T6.MOLECULAS), 100)
        u = T6.unidade(obra('10.1/x', 'Deltamethrin against Scaphoideus titanus in vineyards'), set())
        self.assertEqual([m['VALOR'] for m in u['MOLECULA']], ['deltamethrin'])
        u = T6.unidade(obra('10.1/x', 'A new molecule XYZ-123 against Scaphoideus titanus'), set())
        self.assertEqual(u['MOLECULA'], NS)

    def test_dataset_escrito_no_resumo_vira_dataset_id(self):
        u = T6.unidade(obra('10.1/x', 'Late blight of tomato', 'Data: 10.5281/zenodo.12345 are public.'), set())
        self.assertEqual(u['DATASET_ID'][0]['ID'], '10.5281/zenodo.12345')


class Deduplicar(SemRede):
    def test_mesma_obra_em_duas_consultas_e_uma_unidade(self):
        w = obra('10.1/x', 'Botrytis cinerea on grapevine and tomato')
        us, gs = T6.deduplicar([(w, 'vite x botrite'), (w, 'pomodoro x botrite')])
        self.assertEqual(len(us), 1)
        self.assertEqual(us[0]['CONSULTAS_QUE_O_TROUXERAM'], ['pomodoro x botrite', 'vite x botrite'])

    def test_preprint_e_artigo_ficam_os_dois_num_grupo_provavel(self):
        a = obra('10.1016/a', 'Mating-type locus of Plasmopara viticola')
        b = obra('10.1101/b', 'Mating-type locus of plasmopara viticola', tipo='preprint')
        us, gs = T6.deduplicar([(a, 'vite x peronospora'), (b, 'vite x peronospora')])
        self.assertEqual(len(us), 2)                       # UNKNOWN nao funde
        self.assertEqual(gs, [{'ESTADO': 'PROVAVEL_MESMA_OBRA', 'POR': 'mesmo titulo + autor em comum',
                               'DOIS': ['10.1016/a', '10.1101/b']}])

    def test_mesmo_dataset_e_ensaio_provado(self):
        r = 'Field data are at 10.5281/zenodo.777 for grapevine.'
        a = obra('10.1/a', 'Downy mildew epidemics, part one', r)
        b = obra('10.1/b', 'Downy mildew fungicide timing, part two', r)
        _, gs = T6.deduplicar([(a, 'vite x peronospora'), (b, 'vite x peronospora')])
        self.assertIn({'ESTADO': 'ENSAIO_PROVADO', 'POR': '10.5281/zenodo.777', 'DOIS': ['10.1/a', '10.1/b']}, gs)


class Pessoas(SemRede):
    def test_coautor_estrangeiro_nao_vira_pesquisador_italiano_e_a_ordem_e_alfabetica(self):
        w = obra('10.1/x', 'Downy mildew of grapevine', autores=[
            autor('A2', 'Zeno Bianchi', 'IT'), autor('A3', 'Jean Martin', 'FR'), autor('A1', 'Ada Verdi', 'IT')])
        us, _ = T6.deduplicar([(w, 'vite x peronospora')])
        self.assertEqual([p['NOME'] for p in T6.pessoas(us)], ['Ada Verdi', 'Zeno Bianchi'])


class Crossref(SemRede):
    def test_orcid_depositado_prova_a_obra_sem_rebaixar_o_autodeclarado(self):
        us = [T6.unidade(obra('10.1/x', 'Downy mildew', autores=[
            autor('A1', 'Ana', 'IT', '0000-0001-0000-0001'), autor('A2', 'Bia', 'IT', '0000-0002-0000-0002'),
            autor('A3', 'Caio', 'IT', '0000-0003-0000-0003')]), set())]
        T6.provar_pessoas(us, {'0000-0001-0000-0001': {'10.1/x'}})
        resp = {'message': {'items': [{'DOI': '10.1/X', 'author': [   # sintetico: nenhum real gravado
            {'ORCID': 'http://orcid.org/0000-0001-0000-0001', 'authenticated-orcid': False},
            {'ORCID': 'https://orcid.org/0000-0002-0000-0002', 'authenticated-orcid': True},
            {'ORCID': 'http://orcid.org/0000-0003-0000-0003', 'authenticated-orcid': False}]}]}}
        self.assertEqual(T6.provar_por_crossref(us, resp), {'OK': True, 'DOIS_CONFIRMADOS': 1})
        self.assertEqual([a['PROVA_DA_PESSOA'] for a in us[0]['AUTORES']],
                         ['ORCID_AUTODECLARADO', 'ORCID_NO_DEPOSITO_AUTENTICADO', 'ORCID_NO_DEPOSITO_DO_EDITOR'])
        self.assertFalse(T6.provar_por_crossref(us, {'status': 'failed'})['OK'])


class EnsaioOffline(SemRede):
    def test_as_respostas_gravadas_atravessam_sem_rede(self):
        r = T6.ensaio()
        self.assertEqual(r['RESPOSTAS_INVALIDAS'], [])
        self.assertEqual(r['UNIDADES_DEPOIS_DE_DEDUPLICAR'], 21)
        self.assertEqual(r['CAMPOS_PREENCHIDOS']['DOI'], 21)
        self.assertEqual(r['PLANO_SE_FOSSE_REDE']['RODADAS_POR_DOMINIO']['api.openalex.org'], 3)
        for p in r['PESSOAS']:
            self.assertTrue(p['INSTITUICOES_ITALIANAS'], p['NOME'])
        # o controlo negativo (Delmotte, INRAE) nao entra como pesquisador italiano
        self.assertNotIn('https://openalex.org/A5088752812', [p['OPENALEX_ID'] for p in r['PESSOAS']])


class Qualify(unittest.TestCase):
    def test_registo_orcid_e_t6_com_ou_sem_instituicao_no_nome(self):
        u = 'https://orcid.org/0000-0003-2089-1026'
        self.assertEqual(ASI.territorio_de({'NOME': 'Andrea Lentini', 'URL': u})[0], 'T6')
        self.assertEqual(ASI.territorio_de({'NOME': 'Andrea Lentini (Università di Sassari)', 'URL': u})[0], 'T6')

    def test_o_resto_nao_muda(self):
        self.assertEqual(ASI.territorio_de({'NOME': 'Università di Sassari', 'URL': 'https://www.uniss.it'})[0], 'T5')
        self.assertEqual(ASI.territorio_de({'NOME': 'Mario', 'URL': 'https://orcid.org/'})[0], 'NAO SEI')


if __name__ == '__main__':
    unittest.main()
