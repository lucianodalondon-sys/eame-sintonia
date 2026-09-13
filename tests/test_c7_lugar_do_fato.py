#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DA C7 — o nome do lugar tem de estar ESCRITO.

A peneira de assunto trunca a palavra de propósito: é assim que `diserbo`
apanha `diserbato`. Para NOME PRÓPRIO a mesma virtude é ruína, porque nome
truncado não vira o mesmo nome — vira outro.

    _raizes('la rioja')  ->  ['rio']   ->  septoriose, fusariosi, periodo

Medido neste corpus: 37 dos 59 lugares declarados casavam assim. A beterraba
(`barbabietole`) virava Toledo, «beaucoup» virava Beauce, e o nome próprio
`Francesco` virava França.

    PENEIRA DE ASSUNTO TRUNCA PORQUE A IDEIA SOBREVIVE A CONJUGACAO.
    NOME PROPRIO NAO SOBREVIVE A TRUNCAGEM.

E a lei que a C7 não pode revogar ao consertar:

    NORMALIZAR != STEMMING.
"""
import ast
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, 'regras'), os.path.join(RAIZ, 'coleta'),
          os.path.join(RAIZ, 'leis'), os.path.join(RAIZ, 'ferramentas')):
    sys.path.insert(0, p)
import _gavetas              # noqa: E402,F401
import proveniencia as pv    # noqa: E402
import sensor_medir as sm    # noqa: E402


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _func(rel, nome):
    """A função tal como ela está na ÁRVORE — não no texto do ficheiro.

    Sentinela que lê texto cru mede o texto. Já custou duas provas nesta casa.
    """
    for no in ast.walk(ast.parse(_fonte(rel))):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    raise AssertionError('%s não tem %s()' % (rel, nome))


# ══════════════════════════════════════════════════════════════════════════
class T1a5OQueNaoPodeMaisCasar(unittest.TestCase):
    """Os cinco contraexemplos obrigatórios, e os que o censo encontrou depois."""

    #: cada um vem de uma ocorrência REAL no acervo, não de imaginação minha
    FALSOS = [
        ('Periodico olivo 1 Maggio 2026', 'periodico → rio'),
        ('calendario fitosanitario', 'calendario → rio'),
        ('various periods prior to harvest', 'period/prior → rio'),
        ('superior', 'superior → rio'),
        ('scenarios', 'scenarios → rio'),
        ('septoriose du ble', 'septoriose → rio — o nome da DOENCA'),
        ('fusariosi del frumento', 'fusariosi → rio'),
        ('barbabietole da zucchero', 'barbabietole → tole — a BETERRABA'),
        ('beaucoup de pluie cette annee', 'beaucoup → beau'),
        ('davvero interessante, grazie', 'davvero → vero'),
        ('ricordo bene quel anno', 'ricordo → cordo'),
        ('ho parlato con Francesco ieri', 'Francesco → fran — o NOME DA PESSOA'),
        ('marciume del grappolo', 'marciume → marc'),
        ('ca marche tres bien', 'ça marche → marc — a cicatriz original da lista'),
        ('il decespugliatore nuovo', 'decespugliatore → pugl'),
        ('mercado del aceite de oliva', 'mercado → cad'),
        ('campanella in fiore', 'campanella → campan'),
    ]

    def test_nenhum_falso_positivo_do_censo_sobrevive(self):
        for texto, porque in self.FALSOS:
            with self.subTest(texto=texto):
                pais, nome = sm.lugar_do_fato(texto)
                self.assertEqual(
                    sm.NAO_SEI, pais,
                    'o texto %r nao nomeia lugar nenhum (%s) e saiu %s/%s'
                    % (texto, porque, pais, nome))
                self.assertIsNone(nome)

    def test_o_idioma_nunca_foi_lugar(self):
        """`italiana` contém `italia` e continua a não ser o lugar do facto.

        COUNTRY_OF_PERSON != COUNTRY_OF_FACT, e gentílico fala da pessoa.
        """
        for texto in ('tecnica italiana', 'grano italiano', 'un collega abruzzese',
                      'varieta siciliana', 'cuisine francaise'):
            with self.subTest(texto=texto):
                self.assertEqual(sm.NAO_SEI, sm.lugar_do_fato(texto)[0])


# ══════════════════════════════════════════════════════════════════════════
class T6a10OQueTEMDeContinuarACasar(unittest.TestCase):
    """Consertar recall para zero também seria conserto — e seria perda."""

    POSITIVOS = [
        ('La Rioja', 'ES', 'la rioja'),
        ('Verona', 'IT', 'verona'),
        ('Trentino', 'IT', 'trentino'),
        ('Champagne', 'FR', 'champagne'),
        ('Bordeaux', 'FR', 'bordeaux'),
        ('Val de Loire', 'FR', 'val de loire'),
        ('Alto Adige', 'IT', 'alto adige'),
        ('Le Marche', 'IT', 'le marche'),
        ('Regione Marche', 'IT', 'regione marche'),
        ('Cotes du Rhone', 'FR', 'cotes du rhone'),
    ]

    def test_lugar_explicitamente_escrito_continua_a_casar(self):
        for texto, pais, lugar in self.POSITIVOS:
            with self.subTest(texto=texto):
                self.assertEqual((pais, lugar), sm.lugar_do_fato(texto))

    def test_dentro_de_uma_frase_inteira(self):
        """Lugar no meio do texto, não só sozinho."""
        casos = [
            ('Flavescenza dorata: diffusione nel territorio veneto', 'IT'),
            ('Le vin de Champagne face au mildiou', 'FR'),
            ('El olivar de La Rioja y el repilo', 'ES'),
        ]
        for texto, pais in casos:
            with self.subTest(texto=texto):
                self.assertEqual(pais, sm.lugar_do_fato(texto)[0])


# ══════════════════════════════════════════════════════════════════════════
class T11a14OContratoDoCasamento(unittest.TestCase):

    def test_t11_acento_e_caixa_nao_quebram(self):
        """Grafia da mesma palavra cai na normalização — isso é NORMALIZAR."""
        for a, b in (('Córdoba', 'cordoba'), ('ANDALUCÍA', 'andalucia'),
                     ('Sicília', 'sicilia'), ('CHAMPAGNE', 'champagne')):
            with self.subTest(par=(a, b)):
                self.assertEqual(sm.lugar_do_fato(b), sm.lugar_do_fato(a))

    def test_t12_palavra_maior_que_contem_o_token_nao_casa(self):
        """A fronteira é dos dois lados — prefixo e sufixo."""
        for texto in ('veronese', 'aipoverona', 'italiano', 'cadena',
                      'grancordoba', 'lamurciana'):
            with self.subTest(texto=texto):
                self.assertEqual(sm.NAO_SEI, sm.lugar_do_fato(texto)[0])

    def test_t13_frase_multiword_tem_de_estar_mesmo_presente(self):
        """`rioja` sozinho não é `la rioja` declarado; e a ordem importa."""
        self.assertEqual(sm.NAO_SEI, sm.lugar_do_fato('rioja')[0])
        self.assertEqual(sm.NAO_SEI, sm.lugar_do_fato('rioja la')[0])
        self.assertEqual(sm.NAO_SEI, sm.lugar_do_fato('adige alto')[0])
        self.assertEqual('ES', sm.lugar_do_fato('la rioja')[0])

    def test_t13b_so_o_espaco_e_elastico(self):
        """Quebra de linha e espaço duplo não apagam um lugar escrito."""
        for texto in ('la\nrioja', 'la  rioja', 'la\trioja', 'alto\nadige'):
            with self.subTest(texto=repr(texto)):
                self.assertNotEqual(sm.NAO_SEI, sm.lugar_do_fato(texto)[0])

    def test_t14_a_geografia_nao_faz_stemming(self):
        """A prova que fecha o defeito: nenhuma raiz truncada casa.

        Para CADA lugar declarado, a raiz que `_raizes` produziria não pode,
        sozinha, casar o lugar. Se casar, o stemming voltou.
        """
        for pais, nomes in sm.LUGARES.items():
            for nome in nomes:
                raizes = sm._raizes(nome)
                if [r for r in raizes] == [x for x in sm._n(nome).split()]:
                    continue          # nada foi truncado — nada a provar aqui
                with self.subTest(lugar=nome):
                    self.assertFalse(
                        sm._nomeia_lugar(' '.join(raizes), nome),
                        'a raiz %s casou o lugar %r — o stemming voltou'
                        % (raizes, nome))

    def test_pontuacao_ao_lado_nao_impede(self):
        for texto in ('(Verona)', 'Verona,', '«Champagne»', 'Verona.', '#Trentino'):
            with self.subTest(texto=texto):
                self.assertNotEqual(sm.NAO_SEI, sm.lugar_do_fato(texto)[0])

    def test_hifen_separa_tokens(self):
        """`Emilia-Romagna` nomeia Emília: o hífen é fronteira, não letra."""
        self.assertEqual('IT', sm.lugar_do_fato('Emilia-Romagna')[0])


# ══════════════════════════════════════════════════════════════════════════
class T26SentinelaEstrutural(unittest.TestCase):
    """A prova que impede o defeito de voltar pela mesma porta."""

    def test_lugar_do_fato_nao_chama_o_matcher_de_assunto(self):
        """Lida da ÁRVORE: geografia não pode voltar a depender de `_tem`."""
        fn = _func('regras/sensor_medir.py', 'lugar_do_fato')
        chamadas = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        for proibida in ('_tem', '_perto', '_raizes'):
            self.assertNotIn(
                proibida, chamadas,
                'lugar_do_fato() voltou a chamar %s() — esse e o matcher de '
                'ASSUNTO, que trunca de proposito' % proibida)
        self.assertIn('_nomeia_lugar', chamadas,
                      'lugar_do_fato() tem de passar pelo matcher geografico')

    def test_o_matcher_geografico_nao_trunca(self):
        """`_nomeia_lugar` não pode conter fatia de palavra nem chamar `_raizes`."""
        fn = _func('regras/sensor_medir.py', '_nomeia_lugar')
        chamadas = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        self.assertNotIn('_raizes', chamadas)
        fatias = [n for n in ast.walk(fn) if isinstance(n, ast.Subscript)
                  and isinstance(n.slice, ast.Slice)]
        self.assertEqual([], fatias,
                         'o matcher geografico corta palavra — isso e stemming')

    def test_a_fronteira_e_a_mesma_da_casa(self):
        """A regra não foi inventada aqui: veio de `leis/fato_local.py`.

        Duas fronteiras diferentes para a mesma pergunta são duas leis.
        """
        nossa = _fonte('regras/sensor_medir.py')
        dele = _fonte('leis/fato_local.py')
        regra = r'(?<![0-9a-z])%s(?![0-9a-z])'
        self.assertIn(regra, nossa, 'a fronteira da C7 nao e a da casa')
        self.assertIn(regra, dele, 'leis/fato_local.py mudou de regra')


# ══════════════════════════════════════════════════════════════════════════
class T15a18OQueACSeteNaoPodeTerMexido(unittest.TestCase):

    def test_t15_o_gate_de_especie_da_c6_continua_de_pe(self):
        fn = _func('regras/sensor_medir.py', 'medir')
        chamadas = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
        self.assertIn('pv.serve_para_original', chamadas,
                      'o portao da especie da C6 saiu de medir()')
        self.assertFalse(pv.serve_para_original(pv.NAO_SEI))
        self.assertTrue(pv.serve_para_original(pv.ASR_LOCAL))
        self.assertTrue(pv.serve_para_original(pv.NATIVE_CAPTION_ORIGINAL))
        self.assertFalse(pv.serve_para_original(pv.NATIVE_CAPTION_TRANSLATED))

    def test_t16_t17_o_matcher_de_assunto_ficou_intacto(self):
        """`_raizes`/`_perto`/`_tem` são de OUTROS contratos, não medidos aqui."""
        base = subprocess.run(
            ['git', 'show', 'dab574b9:regras/sensor_medir.py'],
            cwd=RAIZ, capture_output=True, text=True)
        if base.returncode:
            self.skipTest('o head da C6 nao esta alcancavel neste clone')
        antes = ast.parse(base.stdout)
        agora = ast.parse(_fonte('regras/sensor_medir.py'))

        def corpo(arv, nome):
            for n in ast.walk(arv):
                if isinstance(n, ast.FunctionDef) and n.name == nome:
                    return ast.unparse(n)
            return None

        for f in ('_raizes', '_perto', '_tem', 'classificar_conteudo',
                  'classificar_comentario', '_n'):
            with self.subTest(funcao=f):
                self.assertEqual(corpo(antes, f), corpo(agora, f),
                                 '%s() mudou — a C7 so podia mexer na geografia' % f)

    def test_t16b_as_constantes_do_assunto_nao_mudaram(self):
        self.assertEqual(5, sm.PISO_DA_RAIZ)
        self.assertEqual(18, sm.JANELA_DE_PALAVRAS)

    def test_t18_a_c7_nao_escreveu_no_bruto(self):
        r = subprocess.run(['git', 'status', '--short', '--', 'data/raw'],
                           cwd=RAIZ, capture_output=True, text=True)
        self.assertEqual('', r.stdout.strip(),
                         'data/raw mudou, e a correcao e em DERIVED')

    def test_os_outros_dois_lugares_nao_foram_tocados(self):
        """`comunicacao_classificar` e `v21_traducao_trava` têm listas próprias.

        Medido: nenhuma das duas tem este defeito. Mexer nelas seria alterar
        contrato que esta missão não mediu.
        """
        base = subprocess.run(['git', 'diff', '--name-only', 'dab574b9', '--',
                               'coleta/comunicacao_classificar.py',
                               'motor/v21_traducao_trava.py'],
                              cwd=RAIZ, capture_output=True, text=True)
        if base.returncode:
            self.skipTest('o head da C6 nao esta alcancavel neste clone')
        self.assertEqual('', base.stdout.strip(),
                         'a C7 tocou num lexico que nao mediu')


# ══════════════════════════════════════════════════════════════════════════
class TArtefatoDerivado(unittest.TestCase):
    """Se o derivado foi regenerado, ele tem de bater com a régua de hoje."""

    MEDICAO = os.path.join(RAIZ, 'data', 'samples', 'SENSOR-PILOT', 'MEDICAO.json')

    def _medicao(self):
        if not os.path.exists(self.MEDICAO):
            self.skipTest('MEDICAO.json nao existe')
        with io.open(self.MEDICAO, encoding='utf-8') as f:
            return json.load(f)

    def test_nenhuma_evidencia_publicada_e_de_raiz_truncada(self):
        """O campo diz «o texto nomeia X» — então X tem de estar no texto."""
        d = self._medicao()
        maus = []
        for v in d.get('VIDEOS_ITEMS') or []:
            lugar = v.get('COUNTRY_OF_FACT')
            if lugar in (None, sm.NAO_SEI):
                continue
            ev = v.get('COUNTRY_OF_FACT_EVIDENCE') or ''
            nome = ev.split('"')[1] if '"' in ev else None
            if not nome:
                continue
            texto = sm._n('%s %s' % (v.get('TITLE'), v.get('DESCRIPTION')))
            if not sm._nomeia_lugar(texto, nome):
                maus.append((v.get('EXTERNAL_ID'), nome, (v.get('TITLE') or '')[:40]))
        self.assertEqual([], maus[:8],
                         '%d registos publicados dizem nomear um lugar que o '
                         'texto nao escreve' % len(maus))


if __name__ == '__main__':
    unittest.main(verbosity=2)
