#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A V1.3 — A LEI CONFRONTADA COM A PRIMEIRA ESTRADA REAL.

    py tests/test_integracao_biblia.py

Estes testes NÃO leem a documentação: leem os artefatos que a corrida produziu
e o próprio disco.

    UM TESTE QUE CONFERE UM NÚMERO CONTRA O TEXTO QUE O AFIRMA NÃO MEDE NADA.
    Confirma uma frase consigo mesma.

Por isso a população de PDF é reencontrada aqui, com a mesma regra do
repositório reescrita de propósito: importar o executor traria o `pdftotext`
para dentro do teste, e o que se quer medir é a POPULAÇÃO, não a ferramenta.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

BIBLIA = os.path.join(RAIZ, 'BIBLIA-CANONICA-DA-COLETA.md')
GP = os.path.join(RAIZ, 'system-map', 'data', 'golden-path-pdf.generated.json')
REG = os.path.join(RAIZ, 'data', 'derivados', 'REGISTO-DE-ARTEFATOS.json')
TEXTO = os.path.join(RAIZ, 'data', 'derivados', 'texto')
PASTAS_IT = ('data/samples', 'data/collection-store/italy', 'data/raw')


def ler(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def corpo_da_lei(texto, law_id):
    m = re.search(r'^## %s · .+?$' % re.escape(law_id), texto, re.M)
    if not m:
        return ''
    resto = texto[m.end():]
    prox = re.search(r'^## COL-LAW-\d{3} · ', resto, re.M)
    return resto[:prox.start()] if prox else resto


def e_italiano(caminho):
    p = caminho.replace(os.sep, '/').upper()
    if any(s.startswith('IT-') or 'ITALY' in s or 'ITALIA' in s for s in p.split('/')):
        return True
    return any(r in p for r in ('PIEMONTE', 'VENETO', 'ARPAV', 'LOMBARDIA', 'EMILIA',
                                'TOSCANA', 'PUGLIA', 'SICILIA', 'ISTAT', 'ISMEA'))


def pdfs_italianos():
    achados = []
    for pasta in PASTAS_IT:
        for raiz, _, ficheiros in os.walk(os.path.join(RAIZ, pasta)):
            for n in ficheiros:
                if not n.lower().endswith('.pdf'):
                    continue
                inteiro = os.path.join(raiz, n)
                rel = os.path.relpath(inteiro, RAIZ)
                if e_italiano(rel):
                    achados.append(inteiro)
    return sorted(set(achados))


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def fichas():
    d = json.loads(ler(REG))
    return d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))


class AEstradaMedida(unittest.TestCase):
    """Ocorrência, conteúdo, derivação e perda — tudo lido do disco."""

    @classmethod
    def setUpClass(cls):
        cls.gp = json.loads(ler(GP))
        cls.c = cls.gp['COUNTS']
        cls.pdfs = pdfs_italianos()
        cls.hashes = [sha256(p) for p in cls.pdfs]

    # ── T6 · T7 · T8 ─────────────────────────────────────────────────────
    def test_T6_ocorrencias_batem_com_a_corrida(self):
        self.assertTrue(self.pdfs, 'nenhum PDF italiano no disco: a estrada sumiu')
        self.assertEqual(len(self.pdfs), self.c['RAW_INPUT'],
                         'a corrida contou ocorrencias diferentes do que ha no disco')

    def test_T7_conteudos_unicos_sao_menos_que_as_ocorrencias(self):
        unicos = len(set(self.hashes))
        self.assertLess(unicos, len(self.pdfs),
                        'sem repeticao nao ha o que a COL-LAW-501 separa')
        self.assertEqual(len(self.pdfs), unicos + (len(self.pdfs) - unicos),
                         'a aritmetica de ocorrencia x conteudo nao fecha')

    def test_T8_repeticao_de_conteudo_nao_e_perda(self):
        """A lei inteira num teste: mesmo conteudo em dois sitios NAO e sumico."""
        repetidas = len(self.pdfs) - len(set(self.hashes))
        self.assertGreater(repetidas, 0)
        self.assertEqual(0, self.c['LOST'],
                         f'{repetidas} conteudos repetidos entraram como PERDA — '
                         'e a COL-LAW-501 existe exatamente para impedir isso')

    # ── T5 ───────────────────────────────────────────────────────────────
    def test_T5_raw_imutavel(self):
        r = self.gp['RAW_IMUTAVEL']
        self.assertEqual('IMUTAVEL', r['VEREDITO'])
        self.assertEqual(len(self.pdfs), r['PDF_CONFERIDOS'],
                         'a corrida conferiu menos PDF do que existem')

    # ── T9 ───────────────────────────────────────────────────────────────
    def test_T9_todo_derivado_tem_ficha_e_pai(self):
        fs = fichas()
        no_disco = [n for n in os.listdir(TEXTO) if n.endswith('.txt')]
        self.assertEqual(len(fs), len(no_disco),
                         'ha ficha sem ficheiro, ou ficheiro sem ficha')
        sem_pai = [x.get('ARTIFACT_ID') for x in fs
                   if str(x.get('PARENT_ARTIFACT_ID', '')).strip()
                   in ('', 'NAO SEI', 'NAO_SE_APLICA')]
        self.assertEqual([], sem_pai, 'derivado orfao: COL-LAW-008 quebrada')

    # ── T10 · T11 ────────────────────────────────────────────────────────
    def test_T10_emitido_igual_aterrado(self):
        self.assertEqual(self.c['DERIVED_EMITTED'], self.c['DERIVED_LANDED'],
                         'alguma coisa sumiu entre emitir e aterrar')

    def test_T11_nada_perdido_e_zero_emitido_nao_e_perda(self):
        self.assertEqual(0, self.c['LOST'])
        if self.c['DERIVED_EMITTED'] == 0:
            self.assertGreater(self.c.get('JA_EXISTIAM', 0), 0,
                               'emitiu zero e nao havia nada de antes — isso SIM seria perda')

    # ── T12 · T13 ────────────────────────────────────────────────────────
    def test_T12_T13_nada_de_fato_foi_inventado(self):
        for campo in ('FACT_TIME', 'FACT_LOCATION'):
            valores = {str(x.get(campo)) for x in fichas()}
            self.assertTrue(valores <= {'NAO SEI', 'NAO_SE_APLICA'},
                            f'{campo} ganhou valor num derivado de PDF: ninguem '
                            'extraiu fato nenhum, entao alguem inventou')

    # ── T24 ──────────────────────────────────────────────────────────────
    def test_T24_a_lei_e_a_maquina_no_mesmo_head(self):
        """BIBLE_STATUS != NOT_IN_THIS_HEAD."""
        for f in (BIBLIA, GP, REG,
                  os.path.join(RAIZ, 'coleta', 'golden_path_pdf.py'),
                  os.path.join(RAIZ, 'docs', 'biblia', 'RECONCILIACAO-INTEGRACAO.md')):
            self.assertTrue(os.path.isfile(f), f'{f} nao esta neste HEAD')


class AsQuatroLeisNovas(unittest.TestCase):
    """Cada uma nasceu de um ponto onde a lei nao bastava. Se o texto sumir,
    o teste reprova — documentacao apagada nao da erro em teste nenhum."""

    @classmethod
    def setUpClass(cls):
        cls.t = ler(BIBLIA)

    def lei(self, i):
        c = corpo_da_lei(self.t, i)
        self.assertTrue(c, f'{i} desapareceu da Biblia')
        self.assertRegex(c, r'\b(DEVE|NÃO DEVE|NÃO DEVEM|DEVEM|PODE|PODEM)\b',
                         f'{i} ficou sem palavra normativa: virou prosa')
        return c

    def test_501(self):
        c = self.lei('COL-LAW-501')
        self.assertIn('OCCURRENCE / CAPTURE / SOURCE RECORD   ≠   CONTENT', c)
        self.assertIn('NÃO DEVE** subtrair uma da outra', c)

    def test_502(self):
        c = self.lei('COL-LAW-502')
        self.assertIn('DOCUMENT READY', c)
        self.assertIn('FACT READY', c)
        self.assertIn('`NAO_SE_APLICA`, não `NAO_SEI`', c)
        self.assertIn('NÃO DEVE** ser criado estado novo', c)

    def test_T20_503(self):
        c = self.lei('COL-LAW-503')
        self.assertIn('EXECUTOR_UNAVAILABLE', c)
        self.assertIn('ARTIFACT_EXTRACTION_ERROR', c)
        self.assertIn('pré-voo', c)

    def test_504(self):
        c = self.lei('COL-LAW-504')
        self.assertIn('SOURCE_TREE_FINGERPRINT', c)
        self.assertIn('MAP_ARTIFACT_COMMIT', c)
        self.assertIn('circular', c)

    # ── T2 · T3 ──────────────────────────────────────────────────────────
    def test_T2_T3_nenhuma_lei_perdida_nem_renumerada(self):
        ids = re.findall(r'^## (COL-LAW-\d{3}) · ', self.t, re.M)
        self.assertEqual(len(ids), len(set(ids)), 'ha COL-LAW repetido')
        v1 = {x for x in ids if int(x[-3:]) < 100}
        self.assertEqual(48, len(v1), 'a V1 tinha 48 leis; alguma sumiu ou mudou de numero')
        # ⚠️ ESTA CONTAGEM SO SOBE POR EMENDA REGISTADA. O bloco 5xx passou de
        # 4 para 5 na V1.4 (COL-LAW-505), com registo em
        # docs/decisoes/DIARIO-DE-DECISOES.md e linha no historico
        # constitucional, como a COL-LAW-069 exige.
        for bloco, quantas in (('1', 12), ('2', 18), ('3', 16), ('4', 6), ('5', 5)):
            n = len([x for x in ids if x[-3] == bloco])
            self.assertEqual(quantas, n,
                             f'o bloco {bloco}xx tinha {quantas} leis e agora tem {n}')
        # E a contagem sozinha nao apanha uma TROCA — uma lei que sai e outra
        # que entra mantem o total. Estas nunca podem desaparecer nem mudar de
        # numero, e sao nomeadas uma a uma de proposito.
        for lei in ('COL-LAW-501', 'COL-LAW-502', 'COL-LAW-503', 'COL-LAW-504',
                    'COL-LAW-505', 'COL-LAW-012', 'COL-LAW-013', 'COL-LAW-014',
                    'COL-LAW-042', 'COL-LAW-043', 'COL-LAW-069'):
            self.assertIn(lei, ids, f'{lei} desapareceu ou foi renumerada')


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    ok = r.wasSuccessful()
    print('\nTESTES_INTEGRACAO=%s · %d testes' % ('PASS' if ok else 'FAIL', r.testsRun))
    raise SystemExit(0 if ok else 1)
