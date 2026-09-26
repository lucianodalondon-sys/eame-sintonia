#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LISTA MESTRA (MUR): nome + universidade, nunca so o nome; a busca por pessoa com teto. Sem rede."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import lista_mestra_mur as L  # noqa: E402

MUR = [
    {'Fascia': 'Ordinario', 'Cognome e Nome': 'BOSCO Domenico', 'Ateneo': 'TORINO', 'SSD 2024': 'AGRI-05/A'},
    {'Fascia': 'Associato', 'Cognome e Nome': "ZAPPALA' Lucia", 'Ateneo': 'CATANIA', 'SSD 2024': 'AGRI-05/A'},
    {'Fascia': 'Associato', 'Cognome e Nome': 'ROSSI Mario', 'Ateneo': 'PADOVA', 'SSD 2024': 'AGRI-05/B'},
    {'Fascia': 'Ricercatore', 'Cognome e Nome': 'DE LUCA Anna Maria', 'Ateneo': 'BARI', 'SSD 2024': 'AGRI-05/B'},
    {'Fascia': 'Associato', 'Cognome e Nome': 'VITALE Alessandro', 'Ateneo': 'CATANIA', 'SSD 2024': 'AGRI-05/B'},
]


def autor(nome, inst):
    return {'NOME': nome, 'ORCID': 'NAO SEI', 'INST_IT': set(inst), 'OBRAS': 1, 'PARES': set(), 'PROVAS': set()}


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix='mur-')
        self.f = os.path.join(self.dir, 'mur.json')
        with open(self.f, 'w', encoding='utf-8') as h:
            json.dump(MUR, h)
        self.mur = L.ler_mur(self.f)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class Cruzar(Base):
    def test_nome_e_universidade_nunca_so_o_nome(self):
        autores = {
            'A1': autor('Domenico Bosco', ['University of Turin']),
            'A2': autor('Mario Rossi', ['University of Milan']),          # homonimo noutra universidade
            'A3': autor('A. M. De Luca', ['University of Bari Aldo Moro']),  # inicial + apelido composto
            'A4': autor('A. Vitale', ['University of Catania']),
            'A5': autor('Alessandro Vitale', ['Università di Catania']),   # o indice partiu-o: ficam os dois
            'A6': autor('Lucia Zappalà', ['University of Catania']),       # o MUR escreve «ZAPPALA'»
        }
        r = {p['MUR_NOME']: p for p in L.cruzar(self.mur, autores)}
        self.assertEqual((r['BOSCO Domenico']['ESTADO'], r['BOSCO Domenico']['OPENALEX_IDS']), ('MUR_E_OBRAS', ['A1']))
        self.assertEqual(r['ROSSI Mario']['ESTADO'], 'SO_NOME')
        self.assertEqual(r['ROSSI Mario']['OPENALEX_IDS'], [])
        self.assertEqual(r['DE LUCA Anna Maria']['ESTADO'], 'MUR_E_OBRAS')
        self.assertEqual((r['VITALE Alessandro']['ESTADO'], r['VITALE Alessandro']['OPENALEX_IDS']),
                         ('VARIOS_IDS', ['A4', 'A5']))
        self.assertEqual(r["ZAPPALA' Lucia"]['ESTADO'], 'MUR_E_OBRAS')

    def test_quem_nao_aparece_e_nao_encontrado_nao_zero(self):
        r = L.cruzar(self.mur, {})
        self.assertEqual({p['ESTADO'] for p in r}, {'NAO_ENCONTRADO'})

    def test_iris_diz_se_esta_provado_ou_a_confirmar(self):
        r = {p['ATENEO']: p for p in self.mur}
        self.assertEqual(r['TORINO']['IRIS_ESTADO'], 'PROVADO_NO_REPO')
        self.assertEqual(r['CATANIA']['IRIS_ESTADO'], 'A_CONFIRMAR')


class Busca(Base):
    def test_a_busca_orcid_leva_o_acento_e_so_liga_com_a_universidade(self):
        u = L.url_orcid_busca([p for p in self.mur if 'ZAPPALA' in p['APELIDO']])
        self.assertIn('Zappalà', parse_qs(urlparse(u).query)['q'][0])
        resp = {'expanded-result': [    # sintetico: nenhuma resposta real gravada na casa
            {'orcid-id': '0000-0001-1111-1111', 'given-names': 'Lucia', 'family-names': 'Zappalà',
             'institution-name': ['Università degli Studi di Catania']},
            {'orcid-id': '0000-0002-2222-2222', 'given-names': 'Lucia', 'family-names': 'Zappalà',
             'institution-name': ['Universidad de Sevilla']}]}
        r = L.ler_busca_orcid([p for p in self.mur if 'ZAPPALA' in p['APELIDO']], resp)
        self.assertEqual(list(r.values()), [['0000-0001-1111-1111']])

    def test_rodada_com_transporte_falso_teto_e_lotes(self):
        pedidos = []
        muitos = [{'Fascia': 'Associato', 'Cognome e Nome': 'NOME%03d Ana' % i, 'Ateneo': 'PADOVA',
                   'SSD 2024': 'AGRI-05/B'} for i in range(130)]
        f = os.path.join(self.dir, 'mur130.json')
        with open(f, 'w', encoding='utf-8') as h:
            json.dump(muitos, h)
        mur = L.ler_mur(f)
        rod = os.path.join(self.dir, 'rodadas')
        os.makedirs(rod)
        orig, orig_get = L.T6.CP._get, L.T6._pedir

        def falso(url, headers=None):
            pedidos.append(urlparse(url).netloc)
            if 'orcid' in urlparse(url).netloc:
                return {'expanded-result': [], 'num-found': 0}, None
            return {'meta': {}, 'results': []}, None
        L.T6.CP._get = falso
        L.T6._pedir = lambda url, chave=None: falso(url)
        try:
            r1 = L.rodada(1, mur, rod, os.path.join(self.dir, 's'), pausa=0)
            r2 = L.rodada(2, mur, rod, os.path.join(self.dir, 's'), pausa=0)
        finally:
            L.T6.CP._get, L.T6._pedir = orig, orig_get
        self.assertEqual(r1['PEDIDOS']['pub.orcid.org'], 5)        # 100 dos 130, em lotes de 20
        self.assertEqual(r2['PEDIDOS']['pub.orcid.org'], 2)        # os 30 que faltavam
        self.assertTrue(all(v <= 5 for v in r1['PEDIDOS'].values()))


if __name__ == '__main__':
    unittest.main()
