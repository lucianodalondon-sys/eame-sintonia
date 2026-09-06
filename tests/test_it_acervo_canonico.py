"""O universo `UNIVERSE_ACERVO_IT` so existe enquanto dois leitores concordarem.

Tres leitores do mesmo universo deram 141, 101 e 164. Nenhum estava a mentir:
estavam a medir coisas diferentes, e a diferenca nao aparecia em lado nenhum
porque nao havia teste que a mostrasse. Estes testes sao esse lado nenhum.

Cada teste guarda uma das causas que foram PROVADAS na reconciliacao, para que
volte a doer se alguem a reintroduzir:

  · o separador de caminho nao pode mudar o resultado
  · familia nao e pais
  · fonte nao e assunto
  · documento agregado vale 1 e nao desaparece
  · a camada de metodo nao entra no que ela propria mede
  · quem mede nao escreve

Sem pytest neste ambiente: `unittest`, biblioteca padrao.

    py -3 -m unittest tests.test_it_acervo_canonico -v
"""
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RAIZ, 'scripts')
REGISTO_REL = os.path.join('data', 'samples', 'IT-PORTAL-V1', 'IT-ACERVO-CHAVES-V1.json')


def _fonte(ficheiro):
    with open(os.path.join(SCRIPTS, ficheiro), encoding='utf-8') as f:
        return f.read()


def _modulo(nome, ficheiro):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(SCRIPTS, ficheiro))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LEITOR_A = _modulo('leitor_a_t', 'it_acervo_leitor_a.py')
LEITOR_B = _modulo('leitor_b_t', 'it_acervo_leitor_b.py')
PORTAO = _modulo('convergencia_t', 'it_acervo_convergencia.py')

LEITORES = (('A', LEITOR_A), ('B', LEITOR_B))


# ── uma arvore de brincar, para nao mexer no acervo de verdade ───────────────

class ArvoreDeTeste:
    """Constroi um `data/` minimo num sitio temporario."""

    def __init__(self, chaves_conhecidas=('ITENS',)):
        self.raiz = tempfile.mkdtemp(prefix='acervo-it-')
        self.escreve(REGISTO_REL.replace(os.sep, '/'),
                     {'DATASET': 'IT-ACERVO-CHAVES-V1', 'N': len(chaves_conhecidas),
                      'CHAVES': list(chaves_conhecidas)})

    def escreve(self, rel, doc):
        caminho = os.path.join(self.raiz, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False)
        return caminho

    def impressao_da_arvore(self):
        """sha256 de tudo o que esta em `data/` — para provar que nada mudou."""
        h = hashlib.sha256()
        base = os.path.join(self.raiz, 'data')
        for pasta, _, nomes in os.walk(base):
            for n in sorted(nomes):
                p = os.path.join(pasta, n)
                h.update(os.path.relpath(p, base).replace(os.sep, '/').encode())
                with open(p, 'rb') as f:
                    h.update(hashlib.sha256(f.read()).digest())
        return h.hexdigest()

    def limpa(self):
        shutil.rmtree(self.raiz, ignore_errors=True)


class BaseArvore(unittest.TestCase):
    def setUp(self):
        self.t = ArvoreDeTeste()

    def tearDown(self):
        self.t.limpa()

    def le_os_dois(self, raiz=None):
        raiz = raiz or self.t.raiz
        return LEITOR_A.ler(raiz), LEITOR_B.ler(raiz)


# ── 1 · ficheiro novo que satisfaz a regra ENTRA ─────────────────────────────

class FicheiroNovoEntra(BaseArvore):

    def test_ficheiro_italiano_novo_entra_nos_dois_leitores(self):
        self.t.escreve('data/samples/IT-CAMPO-V1/IT-NOVO.json',
                       {'COUNTRY': 'IT', 'ITENS': [{'a': 1}, {'a': 2}, {'a': 3}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertIn('data/samples/IT-CAMPO-V1/IT-NOVO.json', r['FILE_LIST'], nome)
            self.assertEqual(3, r['RECORDS'], nome)

    def test_o_separador_de_caminho_nao_pode_mudar_o_resultado(self):
        """A causa numero um dos 141 vs 69: `(^|/)IT-` nao casa com `\\`.

        Um ficheiro italiano ANINHADO tem de entrar em qualquer sistema. Com a
        regra antiga, no Windows este teste cai.
        """
        self.t.escreve('data/samples/IT-CONVEGNO-V2/falas/IT-FUNDO.json',
                       {'ITENS': [{'x': 1}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertIn('data/samples/IT-CONVEGNO-V2/falas/IT-FUNDO.json',
                          r['FILE_LIST'], nome)

    def test_fato_italiano_de_fonte_europeia_entra(self):
        """Fonte nao e assunto. Seis ficheiros de IT-MERCADO vem do Eurostat e
        falam da Italia; um filtro por SOURCE_LOCATION derrubava-os."""
        self.t.escreve('data/samples/MERCADO-UE/precos.json',
                       {'SOURCE_LOCATION': 'EUROPEAN UNION',
                        'FACT_LOCATION': 'PAIS - Italia',
                        'ITENS': [{'p': 1}, {'p': 2}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(1, r['FILES'], nome)
            self.assertEqual(2, r['RECORDS'], nome)


# ── 2 · ficheiro fora do escopo NAO entra ────────────────────────────────────

class FicheiroForaNaoEntra(BaseArvore):

    def test_ficheiro_nao_italiano_fica_fora(self):
        self.t.escreve('data/samples/ES-COISAS/documento.json',
                       {'COUNTRY': 'ES', 'ITENS': [{'a': 1}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(0, r['FILES'], nome)

    def test_familia_sem_pais_nao_torna_um_ficheiro_italiano(self):
        """A causa dos 29.694: `nuts2`, `RESEARCHER` e `COMPETITOR` sao assuntos,
        nao paises. Um ficheiro da UE inteira nao e acervo italiano."""
        self.t.escreve('data/samples/EU-T1-001-nuts2-crop-area.json',
                       {'SOURCE_LOCATION': 'EUROPEAN UNION',
                        'FACT_LOCATION': 'NUTS2 region',
                        'ITENS': [{'r': i} for i in range(500)]})
        self.t.escreve('data/samples/RESEARCHER-CORPUS-EAME-V1.json',
                       {'ITENS': [{'r': i} for i in range(70)]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(0, r['FILES'], nome)
            self.assertEqual(0, r['RECORDS'], nome)

    def test_ficheiro_fora_de_data_nem_e_visto(self):
        caminho = os.path.join(self.t.raiz, 'research', 'IT-SOLTO.json')
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump({'ITENS': [{'a': 1}]}, f)
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(0, r['FILES'], nome)


# ── 3 · chave nova desconhecida NAO some em silencio ─────────────────────────

class ChaveNovaNaoSome(BaseArvore):

    def test_chave_fora_do_registo_e_declarada_e_reprova(self):
        self.t.escreve('data/samples/IT-NOVO/IT-COISA.json',
                       {'CHAVE_QUE_NUNCA_EXISTIU': [{'a': 1}, {'a': 2}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(1, r['UNKNOWN_KEYS'], nome)
            u = r['UNKNOWN_COLLECTION_KEY'][0]
            self.assertEqual('CHAVE_QUE_NUNCA_EXISTIU', u['CHAVE'], nome)
            self.assertEqual('data/samples/IT-NOVO/IT-COISA.json', u['FICHEIRO'], nome)
            self.assertEqual(2, u['REGISTOS'], nome)
            # e os registos continuam no total: declarar nao e descartar
            self.assertEqual(2, r['RECORDS'], nome)
        self.assertEqual('NAO', PORTAO.veredicto(a, b)['ACERVO_PASSA_NO_PORTAO'])

    def test_documento_agregado_vale_um_e_nao_desaparece(self):
        """O leitor independente devolvia zero e DESCARTAVA o ficheiro: 45
        ficheiros italianos sumiam assim."""
        self.t.escreve('data/samples/IT-AGREGADO/IT-RESUMO.json',
                       {'TITULO': 'um resumo', 'NUMERO': 7})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(1, r['FILES'], nome)
            self.assertEqual(1, r['RECORDS'], nome)
            self.assertIn('__DOCUMENTO_UNICO__', r['PER_KEY'], nome)
            self.assertEqual(0, r['UNKNOWN_KEYS'], nome)   # chave da regra nao e cobrada

    def test_lista_de_raiz_sem_dicionarios_nao_vira_mil_registos(self):
        self.t.escreve('data/samples/IT-LISTA/IT-TEXTOS.json', ['a', 'b', 'c'] * 10)
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(0, r['RECORDS'], nome)
            self.assertIn('__VAZIO__', r['PER_KEY'], nome)


# ── 4 · leitor A e B divergem -> FAIL ────────────────────────────────────────

class DivergenciaReprova(BaseArvore):

    def test_arvores_diferentes_produzem_divergencia_e_veredicto_NAO(self):
        """Mutacao real: A le uma arvore, B le outra com um ficheiro a mais."""
        self.t.escreve('data/samples/IT-A/IT-UM.json', {'ITENS': [{'a': 1}]})
        outra = ArvoreDeTeste()
        try:
            outra.escreve('data/samples/IT-A/IT-UM.json', {'ITENS': [{'a': 1}]})
            outra.escreve('data/samples/IT-A/IT-DOIS.json', {'ITENS': [{'a': 2}]})
            a = LEITOR_A.ler(self.t.raiz)
            b = LEITOR_B.ler(outra.raiz)
            v = PORTAO.veredicto(a, b)
            self.assertEqual('NAO', v['INDEPENDENT_READERS_AGREE'])
            self.assertEqual('NAO', v['CANONICAL_RULE_PROVED'])
            self.assertEqual('NAO', v['UNIVERSE_ACERVO_IT_CANONICAL'])
            self.assertIsNone(v['CANONICAL_FILES'])
            dims = {d['DIMENSAO'] for d in v['DIVERGENCIAS']}
            self.assertIn('FILES', dims)
            self.assertIn('FINGERPRINT', dims)
        finally:
            outra.limpa()

    def test_o_comparador_nao_deixa_passar_uma_dimensao_diferente(self):
        base = {'FILES': 1, 'RECORDS': 1, 'COLLECTIONS': 1, 'UNKNOWN_KEYS': 0,
                'FINGERPRINT': 'x', 'FILE_LIST': ['f'], 'PER_KEY': {}, 'PER_FAMILY': {},
                'UNKNOWN_COLLECTION_KEY': [], 'ILEGIVEL': [],
                'INVARIANT_FAMILY_SUM_OK': True}
        for dimensao in PORTAO.DIMENSOES:
            torto = dict(base)
            torto[dimensao] = 'DIFERENTE'
            concordam, _ = PORTAO.comparar(base, torto)
            self.assertFalse(concordam, dimensao)


# ── 5 · input vazio -> FAIL ──────────────────────────────────────────────────

class EntradaVaziaReprova(BaseArvore):

    def test_acervo_sem_um_unico_ficheiro_italiano_reprova(self):
        a, b = self.le_os_dois()
        self.assertEqual(0, a['FILES'])
        v = PORTAO.veredicto(a, b)
        self.assertEqual('SIM', v['INDEPENDENT_READERS_AGREE'])   # concordam em zero
        self.assertEqual('NAO', v['ACERVO_PASSA_NO_PORTAO'])      # e zero reprova
        self.assertIn('ENTRADA_VAZIA', v['MOTIVOS_DE_REPROVACAO'])
        self.assertEqual('NAO', v['UNIVERSE_ACERVO_IT_CANONICAL'])


# ── 6 · fingerprint diferente -> FAIL ────────────────────────────────────────

class DigitalDiferenteReprova(BaseArvore):

    def test_mesmas_contagens_conteudo_diferente_ainda_reprova(self):
        """A prova de que a digital serve para alguma coisa: tudo igual em
        numero, um byte diferente, e o portao tem de cair."""
        self.t.escreve('data/samples/IT-X/IT-UM.json', {'ITENS': [{'v': 'primeiro'}]})
        gemea = ArvoreDeTeste()
        try:
            gemea.escreve('data/samples/IT-X/IT-UM.json', {'ITENS': [{'v': 'segundo'}]})
            a = LEITOR_A.ler(self.t.raiz)
            b = LEITOR_B.ler(gemea.raiz)
            self.assertEqual(a['FILES'], b['FILES'])
            self.assertEqual(a['RECORDS'], b['RECORDS'])
            self.assertEqual(a['COLLECTIONS'], b['COLLECTIONS'])
            self.assertNotEqual(a['FINGERPRINT'], b['FINGERPRINT'])
            v = PORTAO.veredicto(a, b)
            self.assertEqual('NAO', v['INDEPENDENT_READERS_AGREE'])
            self.assertEqual(['FINGERPRINT'], [d['DIMENSAO'] for d in v['DIVERGENCIAS']])
        finally:
            gemea.limpa()


# ── 7 · quem mede nao escreve ────────────────────────────────────────────────

class MedirNaoEscreve(BaseArvore):

    def test_os_leitores_nao_tocam_no_acervo_durante_a_medicao(self):
        self.t.escreve('data/samples/IT-Y/IT-UM.json', {'ITENS': [{'a': 1}]})
        antes = self.t.impressao_da_arvore()
        LEITOR_A.ler(self.t.raiz)
        LEITOR_B.ler(self.t.raiz)
        self.assertEqual(antes, self.t.impressao_da_arvore(),
                         'um leitor escreveu dentro de data/ enquanto media')

    def test_o_script_do_dono_escreve_e_por_isso_nao_e_instrumento_de_medicao(self):
        """Nao se corre o script do dono para medir: ele REGRAVA o artefacto que
        mede. Este teste nao o executa — le o codigo e prova a escrita.

        Se um dia ele deixar de escrever, este teste cai e alguem reavalia.
        """
        fonte = _fonte('it_acervo_inventario_v2.py')
        self.assertIn("open(SAIDA, 'w'", fonte,
                      'o dono ja nao escreve: rever o aviso da reconciliacao')

    def test_todo_medidor_tem_a_tranca_que_o_proibe_de_escrever_em_data(self):
        """A tranca e uma so linha, e tem de estar em todos os quatro."""
        for ficheiro in ('it_acervo_leitor_a.py', 'it_acervo_leitor_b.py',
                         'it_acervo_convergencia.py', 'it_acervo_reconciliar.py'):
            fonte = _fonte(ficheiro)
            self.assertIn("assert '/data/' not in", fonte, ficheiro)


# ── 8 · ficheiros gerados, pela regra explicita ──────────────────────────────

class FicheirosGerados(BaseArvore):

    def test_a_camada_de_metodo_nao_entra_no_que_ela_propria_mede(self):
        self.t.escreve('data/samples/IT-PORTAL-V1/IT-CONTRATO-NOVO.json',
                       {'COUNTRY': 'IT', 'ITENS': [{'a': i} for i in range(40)]})
        self.t.escreve('data/samples/IT-REAL/IT-DADO.json', {'ITENS': [{'a': 1}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(1, r['FILES'], nome)
            self.assertEqual(1, r['RECORDS'], nome)
            self.assertNotIn('data/samples/IT-PORTAL-V1/IT-CONTRATO-NOVO.json',
                             r['FILE_LIST'], nome)

    def test_o_universo_das_execucoes_nao_entra_no_do_acervo(self):
        self.t.escreve('data/runs/IT-CORRIDA/IT-RUN.json',
                       {'COUNTRY': 'IT', 'ITENS': [{'a': 1}, {'a': 2}]})
        a, b = self.le_os_dois()
        for nome, r in (('A', a), ('B', b)):
            self.assertEqual(0, r['FILES'], nome)


# ── 9 · o acervo de verdade ──────────────────────────────────────────────────

class AcervoReal(unittest.TestCase):

    def test_os_dois_leitores_concordam_no_acervo_deste_repositorio(self):
        a = LEITOR_A.ler(RAIZ)
        b = LEITOR_B.ler(RAIZ)
        concordam, divergencias = PORTAO.comparar(a, b)
        self.assertTrue(concordam, json.dumps(divergencias, ensure_ascii=False)[:2000])
        self.assertGreater(a['FILES'], 0)
        self.assertTrue(a['INVARIANT_FAMILY_SUM_OK'])

    def test_a_invariante_das_familias_vale_no_acervo_real(self):
        a = LEITOR_A.ler(RAIZ)
        self.assertEqual(sum(a['PER_FAMILY'].values()), sum(a['PER_KEY'].values()))

    def test_os_dois_leitores_nao_partilham_codigo(self):
        """Concordar por partilhar funcao nao prova regra nenhuma."""
        fa = _fonte('it_acervo_leitor_a.py')
        fb = _fonte('it_acervo_leitor_b.py')
        self.assertNotIn('it_acervo_leitor_b', fa)
        self.assertNotIn('it_acervo_leitor_a', fb)
        self.assertNotIn('import leitor', fa)
        self.assertNotIn('import leitor', fb)
        # e nao sao o mesmo ficheiro com outro nome
        self.assertNotEqual(hashlib.sha256(fa.encode()).hexdigest(),
                            hashlib.sha256(fb.encode()).hexdigest())


if __name__ == '__main__':
    unittest.main(verbosity=2)
