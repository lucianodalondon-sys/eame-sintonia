#!/usr/bin/env python3
"""
Provas de disciplina sobre as evidências preservadas e sobre o protótipo.

Não testam "o código funciona". Testam o que a missão exige que seja verdade:
proveniência, identidade, data, país, idioma, ausência de mistura entre países e
ausência de mistura entre a camada EU ACTIVE SUBSTANCE e a camada NATIONAL
PRODUCT AUTHORIZATION.

    python3 -m unittest discover -s tests -v
"""
import json, os, re, glob, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
PORTAL = os.path.join(ROOT, 'prototype', 'portal', 'index.html')

def samples():
    return sorted(glob.glob(os.path.join(SAMPLES, '**', '*.json'), recursive=True))

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
LAYERS = {'EU ACTIVE SUBSTANCE', 'NATIONAL PRODUCT AUTHORIZATION', 'NATIONAL — EXCEPCIONAL (art.53)'}
COUNTRY_OF = {'FR': 'FRANCE', 'ES': 'SPAIN', 'IT': 'ITALY', 'EU': 'EUROPEAN UNION'}


class TestProveniencia(unittest.TestCase):
    """Toda amostra precisa dizer de onde veio e quando foi capturada."""

    def test_existe_amostra(self):
        self.assertTrue(samples(), 'nenhuma amostra preservada em data/samples/')

    def test_toda_amostra_declara_origem(self):
        faltando = []
        for p in samples():
            d = load(p)
            if not isinstance(d, dict):
                continue
            tem = any(k in d for k in ('source', 'SOURCE', 'sources', 'SOURCE_ID', 'note'))
            if not tem:
                faltando.append(os.path.relpath(p, ROOT))
        self.assertEqual([], faltando, f'amostras sem declaração de origem: {faltando}')

    def test_toda_amostra_declara_data_de_captura(self):
        faltando = []
        for p in samples():
            d = load(p)
            if not isinstance(d, dict):
                continue
            v = d.get('captured_at') or d.get('CAPTURED_AT')
            if not v or not DATE.match(str(v)):
                faltando.append(os.path.relpath(p, ROOT))
        self.assertEqual([], faltando, f'amostras sem captured_at em AAAA-MM-DD: {faltando}')


class TestCamadaRegulatoria(unittest.TestCase):
    """A mistura entre a camada da UE e a camada nacional é o erro mais grave de T4."""

    def test_layer_declarada_e_valida(self):
        for p in samples():
            d = load(p)
            if not isinstance(d, dict):
                continue
            layer = d.get('layer') or d.get('REGULATORY_LAYER')
            if layer is not None:
                with self.subTest(arquivo=os.path.relpath(p, ROOT)):
                    self.assertIn(layer, LAYERS, f'camada regulatória desconhecida: {layer!r}')

    def test_amostra_da_ue_nao_afirma_autorizacao_nacional(self):
        p = os.path.join(SAMPLES, 'EU-T4-001', 'evidence-32026R1696.json')
        if not os.path.exists(p):
            self.skipTest('amostra EU-T4-001 ausente')
        d = load(p)
        self.assertEqual('EU ACTIVE SUBSTANCE', d.get('REGULATORY_LAYER'))
        proibidos = ('numero AMM', 'num_registrazione', 'titulaire', 'ragione_sociale')
        texto = json.dumps(d, ensure_ascii=False)
        for k in proibidos:
            self.assertNotIn(k, texto,
                             f'amostra de ato da UE não pode carregar campo nacional {k!r}')

    def test_cruzamento_eu_nacional_declara_as_duas_fontes(self):
        p = os.path.join(SAMPLES, 'X-006-eu-cas-to-ephy.json')
        if not os.path.exists(p):
            self.skipTest('amostra X-006 ausente')
        d = load(p)
        self.assertEqual('CAS number', d.get('key'), 'a chave do cruzamento precisa estar declarada')
        self.assertIn('EU-T4-001', d.get('sources', []))
        self.assertIn('FR-T4-001', d.get('sources', []))
        # o limite precisa estar medido, nunca implícito
        self.assertLess(d['acts_with_extractable_cas'], d['acts_tested'],
                        'a cobertura parcial do CAS precisa continuar registrada')


class TestGeografia(unittest.TestCase):
    """SOURCE_LOCATION e FACT_LOCATION são coisas diferentes e não podem colapsar."""

    def test_source_e_fact_location_quando_declarados(self):
        vistos = 0
        for p in samples():
            d = load(p)
            if not isinstance(d, dict):
                continue
            if 'SOURCE_LOCATION' in d:
                vistos += 1
                with self.subTest(arquivo=os.path.relpath(p, ROOT)):
                    self.assertIn('FACT_LOCATION', d,
                                  'quem declara SOURCE_LOCATION precisa declarar FACT_LOCATION')
        self.assertGreater(vistos, 0, 'nenhuma amostra declara SOURCE_LOCATION')

    def test_sem_mistura_entre_paises(self):
        """Uma amostra nomeada FR-/ES-/IT- não pode afirmar fato de outro país."""
        for p in samples():
            base = os.path.basename(p)
            m = re.match(r'(FR|ES|IT)-T\d', base)
            if not m:
                continue
            d = load(p)
            if not isinstance(d, dict):
                continue
            fact = (d.get('FACT_LOCATION') or '').upper()
            if not fact:
                continue
            esperado = COUNTRY_OF[m.group(1)]
            with self.subTest(arquivo=base):
                outros = [c for k, c in COUNTRY_OF.items()
                          if c != esperado and c != 'EUROPEAN UNION' and c in fact]
                self.assertEqual([], outros,
                                 f'{base} declara fato em {outros}, mas é amostra de {esperado}')


class TestMultilingue(unittest.TestCase):
    """A evidência original nunca é substituída por tradução."""

    def test_idioma_original_declarado(self):
        vistos = 0
        for p in samples():
            d = load(p)
            if isinstance(d, dict) and 'ORIGINAL_LANGUAGE' in d:
                vistos += 1
        self.assertGreater(vistos, 0, 'nenhuma amostra declara ORIGINAL_LANGUAGE')

    def test_ato_da_ue_preserva_as_quatro_linguas(self):
        p = os.path.join(SAMPLES, 'EU-T4-001', 'evidence-32026R1696.json')
        if not os.path.exists(p):
            self.skipTest('amostra ausente')
        t = load(p)['TITLES']
        for lang in ('EN', 'FR', 'ES', 'IT'):
            with self.subTest(lang=lang):
                self.assertIn(lang, t)
                self.assertTrue(t[lang]['ORIGINAL_TEXT'], f'texto original de {lang} vazio')
                self.assertEqual(lang, t[lang]['ORIGINAL_LANGUAGE'])


class TestPrototipo(unittest.TestCase):
    """Nenhum bloco do protótipo pode existir sem estado, fonte e evidência."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(PORTAL):
            raise unittest.SkipTest('protótipo ainda não gerado')
        with open(PORTAL, encoding='utf-8') as f:
            cls.html = f.read()
        cls.blocos = re.findall(r'<section class="block">(.*?)</section>', cls.html, re.S)

    def test_existem_blocos(self):
        self.assertGreater(len(self.blocos), 0)

    def test_todo_bloco_tem_estado(self):
        for i, b in enumerate(self.blocos):
            with self.subTest(bloco=i):
                self.assertRegex(b, r'class="badge b-(real|derived|demo|concept)"',
                                 'bloco sem estado REAL/DERIVED/DEMO/CONCEPT')

    def test_todo_bloco_tem_fonte_e_evidencia(self):
        for i, b in enumerate(self.blocos):
            with self.subTest(bloco=i):
                self.assertIn('fonte:', b)
                self.assertIn('evidência:', b)

    def test_bloco_real_aponta_para_arquivo_existente(self):
        for i, b in enumerate(self.blocos):
            if 'b-concept' in b:
                continue  # CONCEPT não tem evidência, por definição
            m = re.search(r'evidência: <code>([^<]+)</code>', b)
            with self.subTest(bloco=i):
                self.assertIsNotNone(m, 'bloco sem caminho de evidência')
                caminho = m.group(1)
                if caminho.strip() in ('—', ''):
                    continue
                self.assertTrue(os.path.exists(os.path.join(ROOT, caminho)),
                                f'evidência inexistente: {caminho}')

    def test_bloco_concept_nao_se_apresenta_como_capacidade(self):
        for b in self.blocos:
            if 'b-concept' in b:
                self.assertRegex(b, r'(?i)(ainda não existe|não pode ser respondida|falta)',
                                 'bloco CONCEPT precisa dizer explicitamente o que falta')

    def test_blocos_de_cruzamento_carregam_aviso(self):
        """Todo bloco que junta clima e doença precisa avisar contra a leitura causal."""
        for b in self.blocos:
            if 'chuva' in b and ('míldio' in b.lower() or 'mildiu' in b.lower()):
                self.assertIn('Não conclua', b,
                              'bloco que cruza clima e doença sem aviso de causalidade')


if __name__ == '__main__':
    unittest.main(verbosity=2)
