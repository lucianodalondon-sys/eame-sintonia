"""D1 — a política canônica de CROP, testada onde ela pode falhar.

docs/regras/POLITICA-CANONICA-DE-CROP.md · RULE_VERSION CROP-D1-2026-09-05

Cada teste aqui corresponde a uma das quatro leis. Não são testes de cobertura: são as
armadilhas que custaram um merge bloqueado.
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import voz  # noqa: E402

VOCAB = {
    'VITE': r'\bvite\b',
    'PESCO': r'\bpesco\b',
    'PERO': r'\bpero\b',
    'MELO': r'\bmelo\b',
}


class TestUmaCultura(unittest.TestCase):
    def test_single_resolve_e_prova_a_primaria(self):
        r = voz.resolver_crop('difesa della vite in Veneto', VOCAB)
        self.assertEqual(r['CROP_ALL'], ['VITE'])
        self.assertEqual(r['CROP_CARDINALITY'], 'SINGLE')
        self.assertEqual(r['CROP_PRIMARY'], 'VITE')
        self.assertEqual(r['CROP_RESOLUTION_STATE'], 'RESOLVED')


class TestMultiplasCulturasReais(unittest.TestCase):
    """A lei central: pluralidade não é incerteza."""

    TEXTO = 'relazione su vite, pesco e pero nella stessa giornata'

    def test_todas_as_culturas_entram(self):
        r = voz.resolver_crop(self.TEXTO, VOCAB)
        self.assertEqual(r['CROP_ALL'], ['PERO', 'PESCO', 'VITE'])
        self.assertEqual(r['CROP_CARDINALITY'], 'MULTI')

    def test_multi_nao_vira_ambiguous(self):
        r = voz.resolver_crop(self.TEXTO, VOCAB)
        self.assertNotEqual(r['CROP_RESOLUTION_STATE'], 'AMBIGUOUS')
        self.assertEqual(r['CROP_RESOLUTION_STATE'], 'RESOLVED')

    def test_primaria_fica_unknown_sem_prova(self):
        r = voz.resolver_crop(self.TEXTO, VOCAB)
        self.assertEqual(r['CROP_PRIMARY'], 'UNKNOWN')

    def test_unknown_nao_e_ausencia_de_cultura(self):
        r = voz.resolver_crop(self.TEXTO, VOCAB)
        self.assertNotEqual(r['CROP_RESOLUTION_STATE'], 'NO_CROP')
        self.assertTrue(r['CROP_ALL'], 'CROP_ALL vazio faria UNKNOWN parecer ausência')


class TestOrdemDoVocabulario(unittest.TestCase):
    """DICTIONARY_ORDER != EVIDENCE. Trinta embaralhamentos, um só resultado."""

    TEXTO = 'vite, pesco e pero'

    def test_ordem_nao_muda_o_resultado_canonico(self):
        base = voz.resolver_crop(self.TEXTO, VOCAB)
        rnd = random.Random(1234)
        for _ in range(30):
            itens = list(VOCAB.items())
            rnd.shuffle(itens)
            r = voz.resolver_crop(self.TEXTO, dict(itens))
            self.assertEqual(r['CROP_ALL'], base['CROP_ALL'])
            self.assertEqual(r['CROP_PRIMARY'], base['CROP_PRIMARY'])
            self.assertEqual(r['CROP_CARDINALITY'], base['CROP_CARDINALITY'])
            self.assertEqual(r['CROP_RESOLUTION_STATE'], base['CROP_RESOLUTION_STATE'])

    def test_o_legado_SIM_muda_com_a_ordem_e_por_isso_nao_e_canonico(self):
        """Prova viva de por que first-match não pode ser fato canônico."""
        vistos = set()
        rnd = random.Random(99)
        for _ in range(30):
            itens = list(VOCAB.items())
            rnd.shuffle(itens)
            vistos.add(voz.resolver_crop(self.TEXTO, dict(itens))['CROP_LEGACY_FIRST'])
        self.assertGreater(len(vistos), 1, 'o legado deveria ser instável sob reordenação')


class TestAmbiguidadeReal(unittest.TestCase):
    """AMBIGUOUS é sobre mapeamento, não sobre quantidade."""

    def test_mesmo_termo_duas_culturas_e_ambiguo(self):
        r = voz.resolver_crop('il melo', {'MELO': r'\bmelo\b', 'MELO_COTOGNO': r'\bmelo\b'})
        self.assertEqual(r['CROP_RESOLUTION_STATE'], 'AMBIGUOUS')
        self.assertEqual(r['CROP_PRIMARY'], 'UNKNOWN')
        self.assertEqual(r['CROP_AMBIGUOUS_SPANS'], ['MELO+MELO_COTOGNO'])

    def test_termos_distintos_nao_sao_ambiguos(self):
        r = voz.resolver_crop('vite e pesco', VOCAB)
        self.assertEqual(r['CROP_RESOLUTION_STATE'], 'RESOLVED')
        self.assertEqual(r['CROP_AMBIGUOUS_SPANS'], [])


class TestSemCultura(unittest.TestCase):
    def test_no_crop_e_estado_proprio(self):
        r = voz.resolver_crop('convegno generale di apertura', VOCAB)
        self.assertEqual(r['CROP_ALL'], [])
        self.assertEqual(r['CROP_CARDINALITY'], 'NONE')
        self.assertEqual(r['CROP_RESOLUTION_STATE'], 'NO_CROP')


class TestEvidencia(unittest.TestCase):
    """Responder 'por que esta cultura entrou?' é obrigação, não extra."""

    def test_cada_cultura_carrega_a_prova(self):
        r = voz.resolver_crop('la vite e il pesco', VOCAB, fonte='TITLE+DESCRIPTION')
        self.assertEqual(len(r['CROP_EVIDENCE']), 2)
        for e in r['CROP_EVIDENCE']:
            self.assertIn(e['CROP_ID'], r['CROP_ALL'])
            self.assertTrue(e['MATCHED_TERM'])
            self.assertEqual(len(e['EVIDENCE_SPAN']), 2)
            self.assertEqual(e['EVIDENCE_SOURCE'], 'TITLE+DESCRIPTION')
            self.assertEqual(e['RULE_VERSION'], voz.REGRA_CROP_VERSAO)

    def test_o_span_aponta_para_o_texto_real(self):
        texto = 'la vite e il pesco'
        r = voz.resolver_crop(texto, VOCAB)
        for e in r['CROP_EVIDENCE']:
            i, f = e['EVIDENCE_SPAN']
            self.assertEqual(texto[i:f].lower(), e['MATCHED_TERM'].lower())


class TestUmaRegraVariosVocabularios(unittest.TestCase):
    """§8: a semântica é única; o que varia é o vocabulário."""

    def test_mesma_regra_em_vocabulario_italiano(self):
        it = voz.VOCAB_CROP_IT
        r = voz.resolver_crop('difesa della vite e del pesco', it)
        self.assertEqual(r['CROP_CARDINALITY'], 'MULTI')
        self.assertEqual(r['CROP_RESOLUTION_STATE'], 'RESOLVED')
        self.assertEqual(r['CROP_PRIMARY'], 'UNKNOWN')

    def test_marcar_assunto_usa_a_mesma_regra_com_vocab_injetado(self):
        reg = voz.marcar_assunto({'TITLE': 'la vite', 'DESCRIPTION': ''},
                                 vocab_crop=voz.VOCAB_CROP_IT)
        self.assertEqual(reg['CROP_CARDINALITY'], 'SINGLE')
        self.assertEqual(reg['CROP_RULE_VERSION'], voz.REGRA_CROP_VERSAO)


class TestFirstMatchNaoECanonico(unittest.TestCase):
    def test_legado_existe_mas_marcado_como_heuristica(self):
        r = voz.resolver_crop('vite e pesco', VOCAB)
        self.assertEqual(r['CROP_LEGACY_STATE'], 'LEGACY_HEURISTIC')
        self.assertNotEqual(r['CROP_LEGACY_STATE'], 'CANONICAL_FACT')


if __name__ == '__main__':
    unittest.main()
