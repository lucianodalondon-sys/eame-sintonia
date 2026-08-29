#!/usr/bin/env python3
"""
Provas de que o NÚMERO PUBLICADO é o NÚMERO DERIVADO.

`tests/test_canonico.py` compara documentos entre si. Este compara documento contra
**dono**: `scripts/metricas_canonicas.py` deriva o valor da evidência, e cada documento
que publica aquele número tem de publicar exatamente esse valor.

O que isto impede, e já aconteceu três vezes: a suíte crescer de 25 para 91 provas e três
documentos continuarem dizendo 25; o atlas ir a 35 SOURCE_IDs e dois documentos ficarem em
31; a amostra cega dar 62,2%/77,8% e um documento publicar 62,5%/77,4%.

**Documento histórico não entra aqui.** Uma frase como *"na MISSÃO 06 havia 37 provas"* é
registro, não afirmação corrente — e reescrevê-la seria apagar a história. Os arquivos
listados em `HISTORICOS` são poupados.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from metricas_canonicas import build                            # noqa: E402

DOCS = os.path.join(ROOT, 'docs')

# Documentos que registram o passado. Um número antigo neles é evidência, não erro.
HISTORICOS = {
    'descoberta/FREEZE-DA-BASE-DO-PILOTO.md',
    'decisoes/DIARIO-DE-DECISOES.md',
    'descoberta/MISSAO-EAME-01.md',
    'descoberta/SEGUNDA-PASSAGEM-E-PRIORIZACAO.md',
    'descoberta/LACUNAS-E-VEREDITO-MISSAO-03.md',
    'operacao/PROVA-DE-RECORRENCIA-MISSAO-08.md',
}


def br(v):
    """Formata como os documentos escrevem: milhar com ponto, decimal com vírgula.

    Preserva a precisão que o dono guardou — 1,17 não pode virar 1,2 no caminho, senão
    o teste passa a exigir do documento um número que a evidência não tem.
    """
    if isinstance(v, float):
        return ('%g' % v).replace('.', ',')
    return f'{v:,}'.replace(',', '.')


# METRIC_ID -> documentos que publicam aquele número como afirmação CORRENTE
BINDINGS = {
    'TEST_COUNT_CURRENT': ['piloto/O-QUE-PODEMOS-DIZER.md',
                           'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                           'apresentacao/PILOTO-CLASSIFICACAO.md',
                           'ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md'],
    'SOURCE_ID_COUNT': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                        'piloto/SOURCE-PACK-PILOTO.md',
                        'apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md',
                        'apresentacao/MATRIZ-DE-PROVA-EAME.md'],
    'PILOT_SOURCE_COUNT': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                           'piloto/SOURCE-PACK-PILOTO.md'],
    'CRITICAL_SOURCE_COUNT': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                              'piloto/SOURCE-PACK-PILOTO.md'],
    'X006_USE_COVERAGE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                          'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                          'apresentacao/PILOTO-CLASSIFICACAO.md',
                          'apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md'],
    'X006_BLIND_SPELLING': ['apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md'],
    'X006_BLIND_USE': ['apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md'],
    'X007_USE_COVERAGE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md',
                          'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                          'apresentacao/PILOTO-CLASSIFICACAO.md'],
    'ES_ROPF_TOTAL': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ES_ROPF_ACTIVE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ES_ADAMA_ACTIVE': ['piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ASK_QUESTION_COUNT': ['piloto/ASK-SINTONIA-BENCHMARK.md',
                           'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md',
                           'piloto/ENTRADA-PARA-CLAUDE-DESIGN.md'],
    'ASK_ANSWERABLE': ['piloto/ASK-SINTONIA-BENCHMARK.md',
                       'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md'],
    'ASK_REFUSAL': ['piloto/ASK-SINTONIA-BENCHMARK.md',
                    'piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md'],
    'RAIF_HUELVA_COHORT_2023': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
    'RAIF_HUELVA_COHORT_2026': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
    'RAIF_CADIZ_COHORT_2026': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
    'RAIF_SEASONS_AVAILABLE': ['apresentacao/CASOS-PARA-APRESENTACAO.md'],
}


class TestDocumentoBateComODono(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.L = build()
        cls.cache = {}

    def doc(self, rel):
        if rel not in self.cache:
            with open(os.path.join(DOCS, rel), encoding='utf-8') as f:
                self.cache[rel] = f.read()
        return self.cache[rel]

    def test_todo_numero_publicado_vem_do_dono(self):
        for metric, docs in BINDINGS.items():
            valor = self.L[metric]['VALUE']
            alvo = br(valor)
            for rel in docs:
                with self.subTest(metrica=metric, documento=rel, valor=alvo):
                    self.assertNotIn(rel, HISTORICOS,
                                     'documento histórico não deve ser amarrado a valor corrente')
                    self.assertIn(alvo, self.doc(rel),
                                  f'{rel} não publica {metric} = {alvo} '
                                  f'(dono: {self.L[metric]["SOURCE"]})')

    def test_o_ledger_declara_dono_e_derivacao_para_toda_metrica(self):
        for mid, m in self.L.items():
            with self.subTest(metrica=mid):
                for campo in ('VALUE', 'UNIT', 'SOURCE', 'DERIVATION'):
                    self.assertIsNotNone(m[campo], f'{mid} sem {campo}')
                self.assertTrue(m['DERIVATION'].strip(), f'{mid} com derivação vazia')

    def test_metricas_espanholas_carregam_data_de_referencia(self):
        """Contagem de janela sem data de referência é número sem validade declarada."""
        for mid, m in self.L.items():
            if mid.startswith('ES_'):
                with self.subTest(metrica=mid):
                    self.assertEqual(m['REFERENCE_DATE'], '2026-08-29')

    def test_o_placar_da_matriz_de_prova_bate_com_a_propria_lista(self):
        matriz = self.doc('apresentacao/MATRIZ-DE-PROVA-EAME.md')
        for estado, mid in (('PROVED', 'DECK_PROVED'), ('PARTIAL', 'DECK_PARTIAL'),
                            ('UNPROVED', 'DECK_UNPROVED'),
                            ('NOT TESTABLE YET', 'DECK_NOT_TESTABLE')):
            linha = next((l for l in matriz.split('\n')
                          if l.startswith(f'| **{estado}**')), None)
            with self.subTest(estado=estado):
                self.assertIsNotNone(linha, f'linha {estado} sumiu do placar')
                declarado = int(re.sub(r'\D', '', linha.split('|')[2]))
                self.assertEqual(declarado, self.L[mid]['VALUE'],
                                 f'{estado}: o placar diz {declarado} e a lista ao lado '
                                 f'tem {self.L[mid]["VALUE"]} claims')

    def test_es_t4_005_esta_no_resumo_de_fontes_criticas(self):
        """A ficha marca CRITICAL; o resumo tem de listar a mesma coisa."""
        pack = self.doc('piloto/SOURCE-PACK-PILOTO.md')
        resumo = next((l for l in pack.split('\n') if l.startswith('**5 CRITICAL')
                       or re.match(r'\*\*\d+ CRITICAL', l)), '')
        for sid in self.L['CRITICAL_SOURCE_IDS']['VALUE']:
            with self.subTest(fonte=sid):
                self.assertIn(sid, resumo,
                              f'{sid} é CRITICAL na ficha e não aparece no resumo')

    def test_documentos_historicos_nao_sao_reescritos(self):
        """O passado fica. Estes documentos precisam continuar dizendo o que diziam."""
        freeze = self.doc('descoberta/FREEZE-DA-BASE-DO-PILOTO.md')
        self.assertIn('43', freeze, 'o total de provas da v1 sumiu do congelamento')
        self.assertIn('37/37', freeze, 'a reconciliação 37 vs 38 sumiu')
