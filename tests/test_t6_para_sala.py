#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T6-PARA-SALA: o executor de COLHEITA, a receita T6, e a medida/ordem por evidencia. Sem rede."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import _gavetas  # noqa: E402,F401
import retorno_da_coleta as rdc  # noqa: E402
import pesquisadores_t6 as T6  # noqa: E402
import pesquisadores_t6_executor as EX  # noqa: E402
from receitas import EXECUTORES  # noqa: E402


def inv(frase):
    out = {}
    for i, p in enumerate(frase.split()):
        out.setdefault(p, []).append(i)
    return out


def obra(doi, titulo, resumo, autores, data='2024-05-01'):
    return {'id': 'https://openalex.org/W' + doi.replace('/', '').replace('.', ''),
            'doi': 'https://doi.org/' + doi, 'title': titulo, 'publication_date': data, 'type': 'article',
            'abstract_inverted_index': inv(resumo), 'primary_location': {'source': {'type': 'journal'}},
            'authorships': autores}


def autor(aid, nome, pais, orcid=None, inst='Universita X'):
    return {'author': {'id': 'https://openalex.org/' + aid, 'display_name': nome,
                       'orcid': ('https://orcid.org/' + orcid) if orcid else None},
            'institutions': [{'display_name': inst, 'country_code': pais, 'ror': None}]}


class Pasta(unittest.TestCase):
    def setUp(self):
        self._get = T6.CP._get

        def proibido(*a, **k):
            raise AssertionError('pedido a rede num teste')
        T6.CP._get = proibido
        self.raiz = tempfile.mkdtemp(prefix='t6-raiz-')
        self.rod = os.path.join(self.raiz, 'rodadas')
        os.makedirs(self.rod)
        a = obra('10.1/a', 'Downy mildew of grapevine in Veneto',
                 'Plasmopara viticola field trial in Veneto vineyards during 2021-2022 seasons.',
                 [autor('A1', 'Ana Rossi', 'IT', '0000-0001-0000-0001'), autor('A2', 'Jean', 'FR')])
        b = obra('10.1/b', 'Botrytis cinerea on grapevine and tomato', 'Grey mould study.',
                 [autor('A1', 'Ana Rossi', 'IT', '0000-0001-0000-0001'), autor('A3', 'Bruno Verdi', 'IT')])
        self._grava('openalex-vite-peronospora.json', {'meta': {'count': 1}, 'results': [a]})
        self._grava('openalex-vite-botrite.json', {'meta': {'count': 1}, 'results': [b]})
        self._grava('openalex-pomodoro-botrite.json', {'meta': {'count': 1}, 'results': [b]})
        self._grava('FALHA-r1-openalex-melo-oidio.json', {'error': 'x', 'message': 'Insufficient budget'})
        self._grava('openalex-melo-carpocapsa.json', {'error': 'x', 'message': 'Insufficient budget'})

    def _grava(self, nome, d):
        with open(os.path.join(self.rod, nome), 'w', encoding='utf-8') as h:
            json.dump(d, h)

    def tearDown(self):
        T6.CP._get = self._get
        shutil.rmtree(self.raiz, ignore_errors=True)


class Executor(Pasta):
    def test_um_trabalho_por_doi_no_contrato_de_retorno_sem_rede(self):
        r = EX.colher('IT-T6-TESTE-1', self.rod, raiz=self.raiz)
        self.assertEqual(r['MAL'], [])
        self.assertEqual(r['COLHIDAS'], 2)                    # b aparece em 2 pares: 1 unidade
        env = T6._ler(os.path.join(self.raiz, r['DECLAROU_EM']))
        us = {u['DOCUMENT_ID']: u for u in env['COLHEITA']}
        self.assertEqual(sorted(us), ['10.1/a', '10.1/b'])
        b = us['10.1/b']
        self.assertEqual(b['SOURCE_ID'], 'EU-T5-001')
        self.assertEqual(b['T6']['CONSULTAS_QUE_O_TROUXERAM'], ['pomodoro x botrite', 'vite x botrite'])
        self.assertEqual(b['PAYLOAD']['ESTADO'], rdc.PRESENTE)
        with open(os.path.join(self.raiz, b['PAYLOAD']['ONDE']), 'rb') as h:
            self.assertEqual(hashlib.sha256(h.read()).hexdigest(), b['SHA256'])

    def test_publicacao_nao_vira_facto_e_o_local_escrito_fica_no_T6(self):
        r = EX.colher('IT-T6-TESTE-2', self.rod, raiz=self.raiz)
        env = T6._ler(os.path.join(self.raiz, r['DECLAROU_EM']))
        a = [u for u in env['COLHEITA'] if u['DOCUMENT_ID'] == '10.1/a'][0]
        self.assertEqual((a['FACT_TIME'], a['FACT_LOCATION']), ('NAO SEI', 'NAO SEI'))
        self.assertEqual(a['PUBLISHED_AT'], '2024-05-01')
        self.assertEqual(a['T6']['LOCAL_DO_ESTUDO_ESCRITO'][0]['VALOR'], 'Veneto')
        self.assertIn('Plasmopara', a['texto'])

    def test_resposta_de_erro_nao_entra_como_trabalho(self):
        self.assertEqual(len(EX.registos(self.rod)), 2)

    def test_sem_rodadas_e_falha_declarada_nao_zero_calado(self):
        r = EX.colher('IT-T6-TESTE-3', os.path.join(self.raiz, 'nao-existe'), raiz=self.raiz)
        self.assertEqual((r['ESTADO'], r['COLHIDAS']), (rdc.FAILED, 0))
        self.assertEqual(r['MAL'], [])

    def test_sem_corrida_recusa(self):
        with self.assertRaises(EX.SemCorrida):
            EX.colher('', self.rod, raiz=self.raiz)


class Receita(unittest.TestCase):
    def test_o_executor_T6_entra_a_frente_e_o_antigo_fica(self):
        ids = [e['id'] for e in EXECUTORES['T6']]
        self.assertEqual(ids[:2], ['pesquisadores-t6', 'corpus-pesquisador'])
        e = EXECUTORES['T6'][0]
        self.assertEqual(e['roda'], ['coleta/pesquisadores_t6_executor.py'])
        self.assertTrue(e['recebe_run_id'])
        self.assertIn('ENVELOPE', e['retorno'])


class MedirEOrdenar(Pasta):
    def test_medir_conta_e_nao_decide(self):
        m = T6.medir(self.rod)
        self.assertEqual(m['TRABALHOS_DEPOIS_DE_DEDUP_POR_DOI'], 2)
        self.assertEqual(m['OCORRENCIAS_TRABALHO_x_CONSULTA'], 3)
        self.assertEqual(m['CAMPOS']['LOCAL_DO_ESTUDO_ESCRITO'], 1)
        self.assertEqual(m['CAMPOS']['PERIODO_DO_ESTUDO'], 1)
        self.assertEqual(m['PESSOAS']['COM_AFILIACAO_IT_NUMA_OBRA'], 2)   # Jean (FR) nao conta

    def test_ordem_por_evidencia_e_cada_pessoa_uma_vez_no_top(self):
        o = T6.por_evidencia(self.rod, total=30)
        top = o['TOP_30']
        self.assertEqual([t['NOME'] for t in top], ['Ana Rossi', 'Bruno Verdi'])
        self.assertEqual(top[0]['PAR'], 'vite x peronospora')             # desempate: local escrito
        self.assertEqual(len({t['OPENALEX_ID'] for t in top}), len(top))
        self.assertNotIn('Jean', json.dumps(o))


if __name__ == '__main__':
    unittest.main()
