#!/usr/bin/env python3
"""ACCESS METHOD NAO E ROUTE MEMBERSHIP. E: SOURCE 1:N ROUTES.

A versao anterior contava `provadas = 1` a mao e derivava «desconhecidas» de
`ACCESS_METHOD` — que e o que o CATALOGO diz, nao a rota que a fonte tem. E a
subtracao supunha que uma fonte pertence a exatamente uma estrada.
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'system-map', 'scripts'))
import _gavetas  # noqa: E402,F401
import censo_das_estradas_it as ce   # noqa: E402

GERADO = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.generated.json')


class AsPertencasSaoDerivadas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,
                        os.path.join(RAIZ, 'system-map', 'scripts',
                                     'censo_das_estradas_it.py')],
                       capture_output=True, text=True, cwd=RAIZ)
        with open(GERADO, encoding='utf-8') as f:
            cls.d = json.load(f)
        cls.regs = cls.d['ROUTE_MEMBERSHIPS']

    def test_o_hardcode_provadas_igual_1_nao_existe_mais(self):
        with open(os.path.join(RAIZ, 'system-map', 'scripts',
                               'censo_das_estradas_it.py'), encoding='utf-8') as f:
            codigo = ce._codigo_executavel(
                os.path.join(RAIZ, 'system-map', 'scripts',
                             'censo_das_estradas_it.py')) or f.read()
        self.assertNotIn('provadas = 1', codigo)

    def test_route_unknown_nao_deriva_de_ACCESS_METHOD(self):
        """A contagem tem de vir das pertencas, nao do que o catalogo descreve."""
        f = self.d['FONTES_IT']
        derivado = sum(1 for v in self.d['RESOLUCAO_POR_FONTE'].values()
                       if v['ROUTE_RESOLUTION_STATE'] in
                       ('ROUTE_UNKNOWN', 'REACHABLE_ROUTE_UNKNOWN'))
        self.assertEqual(f['SOURCES_ROUTE_UNKNOWN'], derivado)
        # E tem de DIVERGIR do proxy antigo: se batesse, seria o mesmo numero
        # com nome novo.
        self.assertNotEqual(f['SOURCES_ROUTE_UNKNOWN'],
                            f['PROXY_ANTIGO_ACCESS_METHOD_NAO_SEI'],
                            'a contagem voltou a ser ACCESS_METHOD disfarcado')

    def test_ARPAV_tem_mais_de_uma_membership(self):
        """SOURCE 1:N ROUTES — provado na fonte que tem as duas evidencias."""
        meus = [r for r in self.regs if r['SOURCE_ID'] == 'IT-T2-002']
        self.assertGreaterEqual(len(meus), 2)
        self.assertEqual({r['ROUTE_CLASS_ID'] for r in meus}, {'RC-1', 'RC-9'})
        self.assertTrue(all(r['STATE'] == 'PROVEN' for r in meus))
        self.assertEqual({r['ROLE'] for r in meus}, {'PRIMARY', 'HISTORICAL'})

    def test_uma_fonte_com_proven_e_candidate_continua_provada(self):
        for sid, v in self.d['RESOLUCAO_POR_FONTE'].items():
            if v['HAS_PROVEN_ROUTE'] and v['HAS_CANDIDATE_ROUTE']:
                self.assertEqual(v['ROUTE_RESOLUTION_STATE'], 'HAS_PROVEN_ROUTE', sid)

    def test_candidata_nunca_e_contada_como_provada(self):
        c = self.d['ROUTE_MEMBERSHIP_COUNTS']
        provadas = sum(1 for r in self.regs if r['STATE'] == 'PROVEN')
        self.assertEqual(c['TOTAL_PROVEN_MEMBERSHIPS'], provadas)
        for r in self.regs:
            if r['STATE'] == 'PROVEN':
                self.assertIn(r['PROOF_KIND'],
                              (ce.BUSCA_VIVA, ce.HISTORICO), r['SOURCE_ID'])

    def test_porta_de_entrada_nao_vira_rota(self):
        """ACCESS_OK e FRONT_DOOR_ACCESS. Nao e HTTP_DOCUMENT_ROUTE."""
        so_porta = [sid for sid, v in self.d['RESOLUCAO_POR_FONTE'].items()
                    if v['FRONT_DOOR_ACCESS'] and v['MEMBERSHIPS'] == 0]
        for sid in so_porta:
            self.assertEqual(
                self.d['RESOLUCAO_POR_FONTE'][sid]['ROUTE_RESOLUTION_STATE'],
                'REACHABLE_ROUTE_UNKNOWN', sid)

    def test_BLOCKED_nao_esconde_desconhecimento(self):
        """Curl recusado e impedimento de FERRAMENTA, nao de politica."""
        for sid, v in self.d['RESOLUCAO_POR_FONTE'].items():
            if v.get('TOOL_REFUSED'):
                self.assertNotEqual(v['ROUTE_RESOLUTION_STATE'], 'BLOCKED', sid)
                # A dica so faz sentido para quem ainda nao tem rota: uma fonte
                # que o ledger ja provou nao precisa de outro probe.
                if not v['HAS_PROVEN_ROUTE'] and not v['HAS_CANDIDATE_ROUTE']:
                    self.assertIn('agente comum', v['CHEAPEST_NEXT_PROOF'], sid)

    def test_toda_fonte_sem_rota_diz_o_que_falta(self):
        for sid, v in self.d['RESOLUCAO_POR_FONTE'].items():
            self.assertTrue(v['CHEAPEST_NEXT_PROOF'], sid)

    def test_o_canario_aponta_para_um_commit_que_existe(self):
        with open(os.path.join(RAIZ, 'system-map', 'data',
                               'estradas-it.model.json'), encoding='utf-8') as f:
            can = json.load(f)['CANARIO']
        r = subprocess.run(['git', 'cat-file', '-e', can['PROOF_REF'] + '^{commit}'],
                           capture_output=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0,
                         'o canario aponta para %s, que nao resolve'
                         % can['PROOF_REF'])

    def test_as_contagens_somam_o_total(self):
        f = self.d['FONTES_IT']
        self.assertEqual(f['SOURCES_WITH_PROVEN_ROUTE']
                         + f['SOURCES_WITH_ONLY_CANDIDATE_ROUTE']
                         + f['SOURCES_ROUTE_UNKNOWN']
                         + f['SOURCES_BLOCKED'], f['TOTAL'])

    def test_classe_nova_traz_motivo_material(self):
        with open(os.path.join(RAIZ, 'system-map', 'data',
                               'estradas-it.model.json'), encoding='utf-8') as f:
            modelo = json.load(f)
        for rc in modelo['ROUTE_CLASSES']:
            if rc['ID'] in ('RC-10', 'RC-11'):
                self.assertGreater(len(rc.get('MOTIVO_MATERIAL', '')), 80,
                                   '%s nasceu sem motivo material' % rc['ID'])

    def test_required_total_continua_desconhecido(self):
        self.assertEqual(self.d['ROUTE_CLASSES_REQUIRED_TOTAL'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main(verbosity=2)
