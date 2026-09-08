#!/usr/bin/env python3
"""O MAPA TEM DE SER DERIVADO DA MEDICAO, NAO DA PROSA.

A versao anterior publicava «2 CLOSED» porque uma pessoa escreveu 2. Estes
casos existem para que nenhum estado operacional volte a nascer de uma frase.

    OWNER EXISTS != OWNER CONNECTED.
    CODE EXISTS != ROUTE CLOSED.
    LIVE SCHEMA != COLLECTION CLOSED.
    CANDIDATE != PROVEN.
"""
import copy
import json
import os
import re
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
MODELO = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.model.json')
MAPA = os.path.join(RAIZ, 'docs', 'operacao',
                    'MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md')


def gerar():
    subprocess.run([sys.executable, os.path.join(RAIZ, 'system-map', 'scripts',
                                                 'censo_das_estradas_it.py')],
                   capture_output=True, text=True, cwd=RAIZ)
    with open(GERADO, encoding='utf-8') as f:
        return json.load(f)


class OsEstadosSaoCalculados(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = gerar()
        cls.rotas = {r['ROUTE_CLASS_ID']: r for r in cls.d['ROUTE_CLASSES']}

    def _com_modelo(self, muda):
        """Roda `rotas_medidas()` com o modelo alterado, sem tocar o ficheiro."""
        with open(MODELO, encoding='utf-8') as f:
            original = f.read()
        modelo = json.loads(original)
        muda(modelo)
        with open(MODELO, 'w', encoding='utf-8') as f:
            json.dump(modelo, f, ensure_ascii=False)
        try:
            return {r['ROUTE_CLASS_ID']: r for r in ce.rotas_medidas()}
        finally:
            with open(MODELO, 'w', encoding='utf-8') as f:
                f.write(original)

    # ── T1 ────────────────────────────────────────────────────────────────
    def test_T1_owner_sem_edge_real_nao_fecha(self):
        """O caso que reprovou a RC-1: `importar_italia.py` existe e nao se liga."""
        rc1 = self.rotas['RC-1']
        st = rc1['STEPS']['STRUCTURED']
        self.assertTrue(st['OWNER_EXISTS'], 'o ficheiro do dono existe')
        self.assertFalse(st['CONNECTED_TO_ROUTE'],
                         'ele nao consome derived_artifact — a aresta nao existe')
        self.assertIn('STRUCTURED', rc1['STEPS_BLOQUEANDO'])
        self.assertFalse(rc1['ARCHITECTURE_CLOSED'])

    # ── T2 ────────────────────────────────────────────────────────────────
    def test_T2_admission_existente_sem_caller_nao_fecha(self):
        adm = self.rotas['RC-1']['STEPS']['ADMISSION']
        self.assertTrue(adm['OWNER_EXISTS'])
        self.assertFalse(adm['CONNECTED_TO_ROUTE'])
        self.assertIn('ADMISSION', self.rotas['RC-1']['STEPS_BLOQUEANDO'])

    # ── T3 ────────────────────────────────────────────────────────────────
    def test_T3_RAW_ausente_nao_fecha(self):
        self.assertIn('RAW', self.rotas['RC-5']['STEPS_BLOQUEANDO'])
        self.assertFalse(self.rotas['RC-5']['ARCHITECTURE_CLOSED'])

    def test_T3b_NOT_APPLICABLE_sem_razao_nao_vale(self):
        """N/A e resposta legitima — mas so com motivo escrito."""
        def tira_a_razao(m):
            for rc in m['ROUTE_CLASSES']:
                if rc['ID'] == 'RC-1':
                    rc['STEPS']['CHECKPOINT'].pop('NOT_APPLICABLE_REASON')
        rotas = self._com_modelo(tira_a_razao)
        self.assertIn('CHECKPOINT', rotas['RC-1']['STEPS_BLOQUEANDO'],
                      'N/A sem razao passou como etapa resolvida')

    # ── T4 ────────────────────────────────────────────────────────────────
    def test_T4_live_schema_sozinho_nao_fecha_coleta(self):
        rc5 = self.rotas['RC-5']
        self.assertEqual(rc5['STEPS']['STRUCTURED']['STATE'], 'LIVE_SCHEMA')
        self.assertTrue(rc5['STEPS']['STRUCTURED']['CONNECTED_TO_ROUTE'])
        self.assertFalse(rc5['ARCHITECTURE_CLOSED'],
                         'SQL estruturado live virou rota de coleta fechada')

    # ── T5 e T6 ───────────────────────────────────────────────────────────
    def test_T5_candidata_nao_conta_como_provada(self):
        f = self.d['FONTES_IT']
        self.assertEqual(f['SOURCE_ROUTE_PROVEN'], 1)
        self.assertEqual(f['SOURCE_ROUTE_PROVEN'] + f['SOURCE_ROUTE_CANDIDATE']
                         + f['SOURCE_ROUTE_UNKNOWN'], f['TOTAL'])

    def test_T6_as_51_desconhecidas_nao_viram_provadas(self):
        f = self.d['FONTES_IT']
        self.assertEqual(f['SOURCE_ROUTE_UNKNOWN'], 51)
        self.assertLess(f['SOURCE_ROUTE_PROVEN'], 40,
                        'descricao virou prova de route class')

    # ── T7 e T8 ───────────────────────────────────────────────────────────
    def test_T7_as_contagens_vem_do_JSON_gerado(self):
        for chave in ('ROUTE_CLASSES_ARCHITECTURE_CLOSED', 'ROUTE_CLASSES_OBSERVED',
                      'ROUTE_CLASSES_DB_TESTED', 'ROUTE_CLASSES_BLOCKED',
                      'ROUTE_CLASSES_DEBT'):
            self.assertIn(chave, self.d)
            self.assertIsInstance(self.d[chave], list)

    def test_T8_o_markdown_nao_contradiz_o_estado_gerado(self):
        """Numero no texto que discorde do JSON e o defeito que originou tudo."""
        with open(MAPA, encoding='utf-8') as f:
            texto = f.read()
        pares = [
            ('ARCHITECTURE_CLOSED', len(self.d['ROUTE_CLASSES_ARCHITECTURE_CLOSED'])),
            ('OBSERVED', len(self.d['ROUTE_CLASSES_OBSERVED'])),
            ('DB_TESTED', len(self.d['ROUTE_CLASSES_DB_TESTED'])),
            ('BLOCKED', len(self.d['ROUTE_CLASSES_BLOCKED'])),
            ('SOURCE_ROUTE_UNKNOWN', self.d['FONTES_IT']['SOURCE_ROUTE_UNKNOWN']),
            ('SOURCE_ROUTE_PROVEN', self.d['FONTES_IT']['SOURCE_ROUTE_PROVEN']),
            ('ROUTE_CLASSES_MODELED', self.d['ROUTE_CLASSES_MODELED']),
        ]
        for rotulo, valor in pares:
            achado = re.search(r'`%s`\s*\|\s*\*\*(\d+)\*\*' % rotulo, texto)
            self.assertIsNotNone(achado, 'o mapa nao publica %s' % rotulo)
            self.assertEqual(int(achado.group(1)), valor,
                             '%s: markdown=%s gerado=%s'
                             % (rotulo, achado.group(1), valor))

    def test_T8b_nenhuma_linha_da_matriz_afirma_fechada_a_mais(self):
        """Contra a AFIRMACAO, nao contra a palavra.

        A primeira versao deste teste proibia a string «2 CLOSED» no ficheiro —
        e reprovava o mapa por CITAR o erro antigo para explica-lo. Apagar a
        memoria do erro nao e consertar o erro. O que nao pode existir e uma
        LINHA DE ESTRADA afirmando FECHADA que o JSON nao sustenta.
        """
        with open(MAPA, encoding='utf-8') as f:
            linhas = [l for l in f.read().split('\n')
                      if l.startswith('| **RC-')]
        afirmadas = {l.split('·')[0].replace('| **', '').strip()
                     for l in linhas if '| SIM |' in l}
        self.assertEqual(sorted(afirmadas),
                         sorted(self.d['ROUTE_CLASSES_ARCHITECTURE_CLOSED']),
                         'a matriz do mapa afirma fechamento que o censo nao mede')

    # ── T9 ────────────────────────────────────────────────────────────────
    def test_T9_CODE_nunca_e_promovido_a_OBSERVED(self):
        for rid, r in self.rotas.items():
            for nome, st in r['STEPS'].items():
                if st['STATE'] == 'CODE':
                    self.assertFalse(st.get('PROOF_REF'),
                                     '%s/%s diz CODE e carrega prova de execucao'
                                     % (rid, nome))
                if st['STATE'] == 'OBSERVED':
                    self.assertTrue(st.get('PROOF_REF'),
                                    '%s/%s diz OBSERVED sem apontar a prova'
                                    % (rid, nome))

    def test_T9b_o_orquestrador_e_medido_e_nao_lembrado(self):
        orq = self.d['ORQUESTRADOR']
        self.assertTrue(orq['EXISTE'],
                        'o mapa anterior dizia que nao existia; o ficheiro esta la')
        self.assertIsNotNone(orq.get('EXECUTORES_ALCANCADOS'))

    def test_T9c_total_de_classes_necessarias_continua_UNKNOWN(self):
        self.assertEqual(self.d['ROUTE_CLASSES_REQUIRED_TOTAL'], 'UNKNOWN')

    def test_T9d_todo_estado_pertence_ao_vocabulario_da_casa(self):
        for r in self.d['ROUTE_CLASSES']:
            for nome, st in r['STEPS'].items():
                self.assertIn(st['STATE'], ce.ESTADOS, '%s/%s' % (r['ROUTE_CLASS_ID'], nome))


if __name__ == '__main__':
    unittest.main(verbosity=2)
