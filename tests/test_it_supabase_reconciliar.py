#!/usr/bin/env python3
"""
Provas da reconciliação do lote italiano que já está no Supabase.

O que estes testes protegem é a CONTABILIDADE, não o número. Um crosswalk permissivo
produz uma fila de leitura pequena e uma sensação boa — e é exatamente isso que o teste
tem de conseguir reprovar.

As provas vivem em branches de trabalho. Quando os blobs não estão no clone, o teste
DECLARA que pulou e por quê: pular em silêncio seria pior do que falhar.
"""
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'it_supabase_reconciliar.py')

_spec = importlib.util.spec_from_file_location('it_reconciliar', SCRIPT)
rec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rec)


def _provas_presentes():
    try:
        rec.carregar('PRESERVACAO_RELATORIO')
        return True
    except rec.Recusado:
        return False


PROVAS = _provas_presentes()
SEM_PROVAS = ('as provas estão em branches de trabalho e não estão neste clone; '
              'rode `git fetch --all` para exercitar estes testes')


@unittest.skipUnless(PROVAS, SEM_PROVAS)
class Reconciliacao(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.relatorio, cls.plano, cls.linhas, cls.sombras, cls.conta = rec.montar()

    def test_contabilidade_fecha_no_lote(self):
        self.assertEqual(self.conta['TOTAL'], rec.RAW_EXPECTED)
        self.assertEqual(self.conta['TOTAL_ACCOUNTED'], rec.RAW_EXPECTED)
        self.assertEqual(sum(self.conta['POR_BALDE'].values()), rec.RAW_EXPECTED)
        self.assertEqual(sum(self.conta['POR_TRIAGEM'].values()), rec.RAW_EXPECTED)

    def test_baldes_sao_disjuntos(self):
        # cada item tem UM balde. Somar o mesmo item em dois lugares fecharia a conta
        # por acidente, que é o defeito que a contabilidade existe para impedir.
        self.assertEqual(len(self.linhas), rec.RAW_EXPECTED)
        for r in self.linhas:
            self.assertIn(r['BALDE'], rec.BALDES)

    def test_unknown_e_zero_e_isso_e_uma_afirmacao(self):
        # UNKNOWN > 0 não é um estado: é o crosswalk admitindo que não olhou.
        self.assertEqual(self.conta['POR_BALDE']['UNKNOWN'], 0)

    def test_consumido_exige_as_duas_provas(self):
        for r in self.linhas:
            if r['BALDE'] == 'ALREADY_CONSUMED':
                self.assertEqual(r['CONTENT_READ_STATE'], 'READ', r['OBJETO'])
                self.assertTrue(r['FATO_DERIVADO'], r['OBJETO'])
                self.assertTrue(r['FATO_DERIVADO'].get('ONDE'), r['OBJETO'])

    def test_nao_consumido_exige_motivo(self):
        for r in self.linhas:
            if r['BALDE'] == 'KNOWN_NOT_CONSUMED':
                self.assertTrue(r['RECUSA_DECLARADA'], r['OBJETO'])
                self.assertTrue(r['RECUSA_DECLARADA'].get('PARSE_BLOCKER'), r['OBJETO'])

    def test_todo_item_que_nao_concluiu_tem_proxima_acao(self):
        # motivo sem próxima ação é desculpa — a lei do Passaporte, exercida aqui.
        for r in self.linhas:
            if r['TRIAGE'] != 'KEEP':
                self.assertTrue(r['NEXT_ACTION'], r['OBJETO'])

    def test_toda_citacao_aponta_para_uma_fonte_declarada(self):
        for r in self.linhas:
            self.assertTrue(r['EVIDENCIA'], r['OBJETO'])
            for e in r['EVIDENCIA']:
                self.assertIn(e['FONTE'], rec.FONTES_POR_NOME, r['OBJETO'])
                self.assertTrue(e['DETALHE'], r['OBJETO'])

    def test_chave_fraca_nao_vira_identidade(self):
        # PRODUCT_URL e ORIGINAL_FILENAME não podem aparecer como base de identidade.
        for r in self.linhas:
            self.assertTrue(r['IDENTITY_BASIS'].startswith('SUPABASE:%s:' % rec.BUCKET))
            self.assertIn(r['OBJETO'], r['IDENTITY_BASIS'])

    def test_quase_cobertura_nunca_vira_leitura(self):
        # 118 documentos da ADAMA carregam o mesmo numero de registro de um rotulo do
        # Ministero que a casa leu — e sao outro arquivo. Somar os dois declararia uma
        # cobertura que nao existe. Este teste e o que impede essa soma.
        vizinhos = [r for r in self.linhas
                    if any(e['TIPO'] == 'MESMO_REGISTRO_OUTRO_ARQUIVO'
                           for e in r['EVIDENCIA_DE_CONTEXTO'])]
        self.assertTrue(vizinhos)
        for r in vizinhos:
            self.assertNotEqual(r['BALDE'], 'ALREADY_CONSUMED', r['OBJETO'])
            self.assertNotEqual(r['CONTENT_READ_STATE'], 'READ', r['OBJETO'])
            for e in r['EVIDENCIA_DE_CONTEXTO']:
                self.assertIn('FRACA', e['CHAVE'])

    def test_contexto_nao_entra_na_lista_de_evidencia(self):
        # EVIDENCIA sustenta veredicto; EVIDENCIA_DE_CONTEXTO nunca sustenta. Misturar as
        # duas listas seria deixar chave fraca decidir balde pela porta dos fundos.
        for r in self.linhas:
            for e in r['EVIDENCIA']:
                self.assertNotIn('TIPO', e, r['OBJETO'])

    def test_varredura_lexica_nao_e_leitura(self):
        varridos = [r for r in self.linhas if r['CONTENT_READ_STATE'] == 'LEXICALLY_SCANNED']
        self.assertTrue(varridos)
        for r in varridos:
            # o contrato: LEXICALLY_SCANNED nunca satisfaz INTELLIGENCE_READING.
            self.assertEqual(r['BALDE'], 'KNOWN_NOT_CONSUMED', r['OBJETO'])
            self.assertIsNone(r['FATO_DERIVADO'], r['OBJETO'])
            self.assertTrue(r['VARREDURA_LEXICA'], r['OBJETO'])
        for s in self.sombras:
            if s['ESTADOS']['CONTENT_READ_STATE'] == 'LEXICALLY_SCANNED':
                self.assertEqual(s['CURRENT_STAGE'], 'INTELLIGENCE_READING', s['ITEM_ID'])

    def test_leitura_nova_e_zero_e_o_porque_esta_escrito(self):
        self.assertEqual(self.conta['ACTUALLY_READ_NOW'], 0)
        self.assertEqual(self.conta['OBJECT_BYTES_AVAILABLE_IN_THIS_ENVIRONMENT'], 0)
        self.assertIn('data/raw', self.conta['POR_QUE_ZERO_LEITURA_NOVA'])

    def test_sombra_usa_o_vocabulario_fechado_do_passaporte(self):
        # A sombra imita PASSPORT-1.0. Um valor fora do vocabulário aqui viraria, no dia
        # da entrada, um estado que o Passaporte recusaria na selagem.
        vocab = {
            'RAW_STATE': ('PRESERVED', 'NOT_PRESERVED', 'ERROR', 'UNKNOWN'),
            'NORMALIZATION_STATE': ('NORMALIZED', 'PENDING', 'ERROR', 'UNKNOWN'),
            'DEDUP_STATE': ('UNIQUE', 'DUPLICATE', 'PENDING', 'UNKNOWN'),
            'CONTENT_STATE': ('AVAILABLE', 'REQUESTED_EMPTY', 'NOT_TESTED', 'ABSENT', 'ERROR', 'UNKNOWN'),
            'CONTENT_READ_STATE': ('READ', 'LEXICALLY_SCANNED', 'NOT_READ', 'UNKNOWN'),
            'IDENTITY_STATE': ('PROVED', 'PLAUSIBLE', 'NOT_PROVED', 'NOT_APPLICABLE', 'UNKNOWN'),
            'CLAIM_STATE': ('EXTRACTED', 'NO_USABLE_CLAIM', 'NOT_APPLICABLE', 'PENDING', 'UNKNOWN'),
            'GEOGRAPHY_STATE': ('PROVED', 'NOT_KNOWN', 'NOT_APPLICABLE', 'UNKNOWN'),
            'TIME_STATE': ('PROVED', 'RELATIVE_ONLY', 'NOT_KNOWN', 'UNKNOWN'),
            'CROP_STATE': ('DECLARED', 'NOT_KNOWN', 'NOT_APPLICABLE', 'UNKNOWN'),
            'ISSUE_STATE': ('DECLARED', 'NOT_KNOWN', 'NOT_APPLICABLE', 'UNKNOWN'),
            'LINEAGE_STATE': ('ROOT', 'RESOLVED', 'BROKEN', 'UNKNOWN'),
            'INTELLIGENCE_STATE': ('PRODUCED', 'NOT_APPLICABLE', 'PENDING', 'UNKNOWN'),
            'ROUTING_STATE': ('ROUTED', 'NOT_APPLICABLE', 'PENDING', 'UNKNOWN'),
            'CONSUMPTION_STATE': ('CONSUMED', 'READY_NOT_CONSUMED', 'BLOCKED',
                                  'ORPHAN_INTELLIGENCE', 'PENDING', 'UNKNOWN'),
        }
        self.assertEqual(len(self.sombras), rec.RAW_EXPECTED)
        for s in self.sombras:
            self.assertEqual(sorted(s['ESTADOS']), sorted(vocab))
            for campo, valor in s['ESTADOS'].items():
                self.assertIn(valor, vocab[campo], '%s.%s' % (s['ITEM_ID'], campo))
            self.assertIn(s['CURRENT_STAGE'], rec.ESCADA)
            self.assertIn(s['TRIAGE'], ('KEEP', 'DEFER', 'REJECT_WITH_REASON', 'ERROR'))

    def test_a_escada_nao_tem_degrau_sem_regra(self):
        # Um degrau sem regra colocaria um item com defeito num estagio adiantado, em
        # silencio. O modulo ja recusa carregar nesse caso; aqui a prova fica visivel.
        self.assertEqual(set(rec.PASSOU), set(rec.ESCADA))
        self.assertEqual(len(rec.ESCADA), 8)

    def test_a_sombra_nao_se_declara_passaporte(self):
        for s in self.sombras:
            self.assertNotIn('SEALED', s)
            self.assertEqual(s['CLAIMS'], [])
            self.assertEqual(s['ROUTES'], [])
            # consumo é pergunta da Inteligência; esta missão para na porta dela.
            self.assertEqual(s['ESTADOS']['CONSUMPTION_STATE'], 'PENDING')

    def test_e_deterministico(self):
        # RECONCILED_AT é constante declarada: rodar de novo amanhã não pode mudar o
        # artefato sem que nada tenha mudado no acervo.
        _, _, linhas2, sombras2, conta2 = rec.montar()
        self.assertEqual(json.dumps(self.linhas, sort_keys=True),
                         json.dumps(linhas2, sort_keys=True))
        self.assertEqual(json.dumps(self.sombras, sort_keys=True),
                         json.dumps(sombras2, sort_keys=True))
        self.assertEqual(conta2['TOTAL_ACCOUNTED'], rec.RAW_EXPECTED)


class Artefatos(unittest.TestCase):
    """O que está gravado tem de bater com o que é derivado agora."""

    def _ler(self, nome):
        caminho = os.path.join(rec.SAIDA, nome)
        if not os.path.exists(caminho):
            self.skipTest('%s ainda não foi gerado' % nome)
        with open(caminho, encoding='utf-8') as fh:
            return json.load(fh)

    def test_o_pacote_declara_que_nao_mudou_nada(self):
        p = self._ler('IT-195-COLLECTION-PACKAGE.json')
        for campo in ('SUPABASE_CHANGED', 'CANONICAL_CHANGED', 'INTELLIGENCE_CHANGED',
                      'PORTAL_CHANGED'):
            self.assertIs(p[campo], False, campo)

    def test_reject_vazio_vem_com_o_porque(self):
        p = self._ler('IT-195-COLLECTION-PACKAGE.json')
        self.assertEqual(p['REJECT_WITH_REASON'], [])
        self.assertTrue(p['POR_QUE_REJECT_ESTA_VAZIO'])

    def test_o_pacote_fecha_no_mesmo_total(self):
        p = self._ler('IT-195-COLLECTION-PACKAGE.json')
        self.assertEqual(p['UNIT_COUNT'], rec.RAW_EXPECTED)
        soma = (len(p['KEEP']) + len(p['DEFER']) + len(p['REJECT_WITH_REASON'])
                + len(p['ERROR']))
        self.assertEqual(soma, rec.RAW_EXPECTED)

    def test_a_evidencia_de_control_plane_nao_se_declara_canonica(self):
        cp = self._ler('CONTROL-PLANE-EVIDENCE-CANDIDATE.json')
        self.assertIs(cp['CANONICAL'], False)
        for c in cp['CANDIDATOS']:
            self.assertIn(c['RELIABILITY'], ('MEDIDO', 'DECLARADO', 'INFERIDO'))
            self.assertTrue(c['EVIDENCE'])

    def test_o_passaporte_nao_foi_ativado(self):
        s = self._ler('IT-195-PRE-PASSAPORTE-SOMBRA.json')
        self.assertIs(s['PASSPORT_ACTIVATED'], False)
        self.assertFalse(os.path.exists(os.path.join(ROOT, 'data', 'passaporte', 'EVENTOS.jsonl')))


if __name__ == '__main__':
    unittest.main()
