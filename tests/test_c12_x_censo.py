#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C12 — O QUE O CENSO DO X MEDIU, E QUE NAO PODE MUDAR EM SILENCIO.

O X e a plataforma onde esta casa declara mais capacidade PROVADA e tem menos
colheita. Quatro capacidades marcadas PROVEN/PARTIAL, zero rotas ligadas, zero
objectos preservados, zero contas no lote congelado.

    CAN DO != DID DO != MAY DO.

Estes testes NAO tocam a rede e NAO aprovam nada. Eles fixam a medicao para que
quem mudar um destes numeros tenha de o dizer.
"""
import glob
import io
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('leis', 'coleta', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import social_matriz as mz          # noqa: E402
import scrap_capacidades as cap     # noqa: E402
import scrap_registo as reg         # noqa: E402
import scrap_executor as scrap      # noqa: E402
import scrap_fornecedores as forn   # noqa: E402

reg.carregar_adaptadores()

PROVADAS = ('x.direct_post', 'x.media', 'x.metrics', 'x.native_caption')


class OXDeclaraCapacidadeESemRota(unittest.TestCase):

    def test_as_quatro_provadas_continuam_sem_caminho(self):
        # Se uma delas ganhar rota, e porque alguem decidiu colher X. Essa
        # decisao nao pode entrar por omissao: tem de partir este teste.
        for n in PROVADAS:
            self.assertIn(cap.estado(n), ('PROVEN', 'PARTIAL'), n)
            self.assertFalse(reg.tem_caminho('X', n),
                             '%s ganhou rota. O host responde `Disallow: /` — '
                             'isto precisa de decisao escrita, nao de um import.' % n)

    def test_o_check_diz_a_verdade_sobre_cada_uma(self):
        for n in PROVADAS:
            v = scrap.CHECK('X', n)
            self.assertFalse(v['CAN'])
            self.assertEqual(v['STATE'], 'DECLARED_WITHOUT_ROUTE')

    def test_a_unica_com_politica_e_a_que_a_casa_nao_sabe_fazer(self):
        # A inversao e o achado: a politica existe onde a capacidade nao existe.
        self.assertEqual(cap.estado('x.discovery'), 'UNKNOWN')
        self.assertFalse(cap.promete_resultado('x.discovery'))
        self.assertEqual(cap.da_matriz('x.discovery'), 'SEARCH_KEYWORD')
        self.assertEqual(mz.decisao('X', 'SEARCH_KEYWORD')['DECISAO'], mz.PERMITIDA_SIM)

    def test_as_quatro_provadas_nao_tem_linha_de_politica_nenhuma(self):
        # `NOT_DECLARED` nao e permissao. Ninguem pode ser recusado por uma
        # linha que nao foi escrita — e ninguem pode ser autorizado por ela.
        for n in PROVADAS:
            self.assertIsNone(cap.da_matriz(n),
                              '%s ganhou traducao para a matriz sem decisao' % n)


class OXNaoTemColheitaNenhuma(unittest.TestCase):

    def test_nenhum_ficheiro_preservado_declara_plataforma_X(self):
        marcados = []
        for p in glob.glob(os.path.join(RAIZ, 'data', '**', '*.json'), recursive=True):
            try:
                t = io.open(p, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            if re.search(r'"PLATFORM"\s*:\s*"X"|"platform"\s*:\s*"x"', t):
                marcados.append(os.path.relpath(p, RAIZ))
        self.assertEqual(marcados, [],
                         'apareceu colheita de X preservada; o censo da C12 '
                         'mediu zero e o documento tem de ser refeito')

    def test_o_lote_congelado_continua_sem_conta_de_X(self):
        import json
        p = os.path.join(RAIZ, 'data', 'samples', 'COMPETITOR-PUBLIC-COMM',
                         'CONTAS-V1.json')
        if not os.path.exists(p):
            self.skipTest('o lote congelado nao esta nesta arvore')
        contas = json.load(io.open(p, encoding='utf-8')).get('ACCOUNTS') or []
        self.assertTrue(contas, 'o lote veio vazio; a sonda mediria zero por engano')
        self.assertEqual([c for c in contas if (c.get('PLATFORM') or '').upper() == 'X'], [])

    def test_ha_contas_de_X_descobertas_e_elas_nao_sao_colheita(self):
        # DESCOBRIR != BUSCAR. Guardar as duas separadas e o que impede o
        # relatorio de dizer que a casa colhe X.
        pat = re.compile(r'(?:twitter\.com|x\.com)/'
                         r'(?!i/|intent|share|home|search|hashtag)([A-Za-z0-9_]{2,15})\b')
        handles = set()
        for p in glob.glob(os.path.join(RAIZ, 'data', '**', '*.json'), recursive=True):
            try:
                t = io.open(p, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            handles.update(h.lower() for h in pat.findall(t))
        self.assertTrue(handles,
                        'a sonda deixou de encontrar os enderecos descobertos; '
                        'zero aqui mede a sonda, nao o repositorio')


class OXNaoTemFornecedorPagoLigado(unittest.TestCase):

    def test_nunca_houve_actor_de_apify_para_o_X(self):
        atores = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if not f.endswith('.py'):
                    continue
                # O PROPRIO TESTE CARREGA O PADRAO QUE PROCURA. Esta casa ja foi
                # mordida por isto: uma pasta temporaria chamada `c10-apify-`
                # fez o teste do «sem Apify» encontrar-se a si mesmo.
                #
                #     UMA SONDA QUE SE ENCONTRA A SI PROPRIA MEDE A SONDA.
                if os.path.abspath(os.path.join(raiz, f)) == os.path.abspath(__file__):
                    continue
                t = io.open(os.path.join(raiz, f), encoding='utf-8',
                            errors='replace').read()
                if re.search(r'apify[^\n]{0,40}(twitter|[^a-z]x[^a-z]scraper)', t, re.I):
                    atores.append(os.path.relpath(os.path.join(raiz, f), RAIZ))
        self.assertEqual(atores, [], 'nasceu um actor pago de X')

    def test_a_ferramenta_que_provou_continua_declarada_como_fornecedor(self):
        self.assertIn('LOCAL_GALLERY_DL', forn.CONHECIDOS)
        self.assertNotIn('LOCAL_GALLERY_DL', forn.PAGOS)


if __name__ == '__main__':
    unittest.main(verbosity=2)
