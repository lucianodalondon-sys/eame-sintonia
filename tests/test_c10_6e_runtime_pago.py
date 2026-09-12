#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.6E — UM UNICO RUNTIME PARA A COMUNICACAO PAGA.

A C10.6D deixou dois buracos nomeados. Este e o primeiro: parte da coleta de
comunicacao publica paga corre por um SEGUNDO runtime.

A pergunta desta missao era se dava para converge-lo HOJE, sem gastar. A
resposta e medida, e e nao — por uma razao precisa:

    A MATRIZ DECLARA A ESCADA. O ROTEADOR SO SABE SUBIR O PRIMEIRO DEGRAU.

Para `INSTAGRAM/FETCH_POST` a matriz declara DUAS rotas: a gratuita
`instagram_janela.py:embed`, que ela propria diz cobrir «os 12 mais recentes», e
a paga `apify:instagram-scraper`, com o motivo canonico ja escrito ao lado
(`FREE_ROUTE_INSUFFICIENT_CAPABILITY`). `mz.decisao()` devolve a primeira, e nao
ha como pedir a segunda. Converger hoje trocaria 30 dias por 12 itens.

    UM CAMINHO QUE MUDA O QUE COLHE NAO E O MESMO CAMINHO.

O que esta missao fez foi medir, provar a recusa, amarrar a identidade do
fornecedor a rota declarada, e tirar o silencio do caminho antigo.
"""
import ast
import io
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras',
          'orquestrador', 'pedido', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import comunicacao_coleta as cc   # noqa: E402
import falhas as fx               # noqa: E402
import scrap_registo as reg       # noqa: E402
import social_matriz as mz        # noqa: E402
import social_rotas as sr         # noqa: E402
reg.carregar_adaptadores()


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _codigo(rel):
    """O ficheiro sem docstring e sem comentario. Prosa nao e comportamento."""
    texto = _fonte(rel)
    arv = ast.parse(texto)
    prosa = {ast.get_docstring(n, clean=False) for n in ast.walk(arv)
             if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef))}
    prosa.discard(None)
    for p in prosa:
        texto = texto.replace(p, '')
    return re.sub(r'(?m)^\s*#.*$', '', texto)


class APoliticaContinuaIntocada(unittest.TestCase):
    """A missao SO OBEDECE. Uma missao que mexe na lei que a limita nao mediu nada."""

    def test_1_linkedin_continua_proibido_nas_duas_rotas(self):
        rotas = mz.MATRIZ['LINKEDIN']['FETCH_POST']
        self.assertEqual(len(rotas), 2)
        for r in rotas:
            self.assertEqual(r['PERMITIDA'], 'NAO', r['ROTA'])
            self.assertEqual(r['ESTADO'], 'ROUTE_NOT_ALLOWED', r['ROTA'])
        self.assertEqual(mz.decisao('LINKEDIN', 'FETCH_POST')['DECISAO'],
                         mz.NAO_PERMITIDA)

    def test_2_instagram_e_facebook_continuam_como_a_matriz_os_deixou(self):
        for plat, padrao, paga in (('INSTAGRAM', 'instagram_janela.py:embed',
                                    'apify:instagram-scraper'),
                                   ('FACEBOOK', 'graph:/{page-id}/posts',
                                    'apify:facebook')):
            with self.subTest(plataforma=plat):
                d = mz.decisao(plat, 'FETCH_POST')
                self.assertEqual(d['DECISAO'], mz.PERMITIDA_SIM)
                self.assertEqual(d['ROTA'], padrao)
                nomes = [r['ROTA'] for r in mz.MATRIZ[plat]['FETCH_POST']]
                self.assertIn(paga, nomes)


class ORoteadorSoSobeOPrimeiroDegrau(unittest.TestCase):
    """O achado que decide o veredito. Se isto passar a falhar, a casa mudou."""

    def test_3_a_rota_paga_declarada_nao_e_alcancavel(self):
        for plat in ('INSTAGRAM', 'FACEBOOK'):
            with self.subTest(plataforma=plat):
                rotas = mz.MATRIZ[plat]['FETCH_POST']
                pagas = [r for r in rotas
                         if r['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID')]
                self.assertTrue(pagas, 'a matriz deixou de declarar rota paga')
                escolhida = mz._rota_padrao(rotas)
                self.assertNotIn(escolhida, pagas,
                                 '%s: a rota paga passou a ser a padrao — a '
                                 'convergencia mudou de forma e este teste tem '
                                 'de ser remedido' % plat)

    def test_4_autorizar_gasto_nao_muda_a_rota_escolhida(self):
        """`permitir_pago` é um PORTÃO, não um seletor. Confundir os dois faria
        quem autoriza gasto pensar que escolheu a rota paga."""
        for plat in ('INSTAGRAM', 'FACEBOOK'):
            with self.subTest(plataforma=plat):
                _o, sem = sr.executar(platform=plat, capability='FETCH_POST',
                                      run_id='T-%s-1' % plat)
                _o, com = sr.executar(
                    platform=plat, capability='FETCH_POST', run_id='T-%s-2' % plat,
                    permitir_pago=True,
                    motivo_pago='FREE_ROUTE_INSUFFICIENT_CAPABILITY')
                self.assertEqual(sem['ROTA_ESCOLHIDA'], com['ROTA_ESCOLHIDA'])
                self.assertIsNone(com['MOTIVO_PAGO'],
                                  'o motivo passou a ser gravado numa rota gratis')

    def test_5_nao_ha_api_para_pedir_um_degrau(self):
        """A ausencia e o gap. Se alguem a fechar, esta sentinela avisa.

        Medido no dono da politica: nenhuma funcao publica devolve a escada de
        rotas viaveis, e `executar` nao aceita `rota=`.
        """
        publicas = [n.name for n in ast.walk(ast.parse(_fonte('leis/social_matriz.py')))
                    if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
        self.assertIn('decisao', publicas, 'a sonda perdeu o ficheiro da politica')
        self.assertNotIn('escada', publicas,
                         'a politica ganhou uma escada publica: o gap da C10.6E '
                         'fechou-se e o veredito tem de ser remedido')
        arv = ast.parse(_fonte('coleta/social_rotas.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == '_executar')
        nomes = [a.arg for a in fn.args.kwonlyargs]
        self.assertIn('permitir_pago', nomes, 'a sonda mede a funcao errada')
        self.assertNotIn('rota', nomes,
                         'o roteador passou a aceitar `rota=`: o gap fechou-se')


class OFornecedorTemUmDonoAmarrado(unittest.TestCase):

    def test_6_cada_ator_diz_que_rota_declarada_cumpre(self):
        self.assertEqual(sorted(cc.ATORES), sorted(cc.ROTA_DECLARADA_DO_ATOR))
        self.assertEqual(cc.conferir_atores(), [])

    def test_7_a_conferencia_morde_quando_a_matriz_muda(self):
        """Controlo negativo. Uma conferencia que so sabe dizer «sim» nao confere."""
        original = dict(cc.ROTA_DECLARADA_DO_ATOR)
        try:
            cc.ROTA_DECLARADA_DO_ATOR['INSTAGRAM'] = ('FETCH_POST', 'apify:inexistente')
            self.assertTrue(cc.conferir_atores(),
                            'a conferencia aceitou uma rota que a matriz nao declara')
            cc.ROTA_DECLARADA_DO_ATOR['INSTAGRAM'] = ('FETCH_POST',
                                                      'instagram_janela.py:embed')
            fora = cc.conferir_atores()
            self.assertTrue(any('deixou de ser paga' in x for x in fora),
                            'a conferencia aceitou um ator sobre rota GRATIS')
        finally:
            cc.ROTA_DECLARADA_DO_ATOR.clear()
            cc.ROTA_DECLARADA_DO_ATOR.update(original)

    def test_8_o_orquestrador_nao_conhece_fornecedor(self):
        """ORCHESTRATOR != COLLECTOR. Ele diz O QUE quer; o runtime decide COMO."""
        t = _codigo('orquestrador/orquestrador.py')
        for proibido in ('apify', 'harvestapi', 'instagram-scraper',
                         'facebook-posts', 'APIFY_TOKEN'):
            self.assertNotIn(proibido, t,
                             'o orquestrador passou a conhecer fornecedor: %s'
                             % proibido)


class OSegundoRuntimeNaoESilencioso(unittest.TestCase):

    def test_9_a_fase_paga_declara_que_nao_atravessa_a_casa(self):
        arv = ast.parse(_fonte('coleta/comunicacao_coleta.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'fase_posts')
        textos = [n.value for n in ast.walk(fn) if isinstance(n, ast.Constant)
                  and isinstance(n.value, str)]
        self.assertTrue(any('SEGUNDO_RUNTIME=' in x for x in textos),
                        'o caminho antigo voltou a correr em silencio')
        self.assertTrue(any('LIVE_PROOF_REQUIRED' in x for x in textos),
                        'a fase deixou de dizer que falta prova ao vivo')

    def test_10_a_declaracao_vem_antes_de_escolher_o_ator(self):
        arv = ast.parse(_fonte('coleta/comunicacao_coleta.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'fase_posts')
        aviso = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Constant)
                 and isinstance(n.value, str) and 'SEGUNDO_RUNTIME=' in n.value]
        ator = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Subscript)
                and getattr(n.value, 'id', None) == 'ATORES']
        self.assertTrue(aviso and ator)
        self.assertLess(min(aviso), max(ator),
                        'a declaracao passou a vir depois da escolha do ator')

    def test_11_o_youtube_continua_a_entrar_pela_casa(self):
        """O contraexemplo que prova que a convergencia É possível quando a
        capacidade está WIRED. A C3 fez isto para o YouTube."""
        self.assertIn('YOUTUBE', cc.CAPACIDADES_SCRAP)
        for papel, capacidade in cc.CAPACIDADES_SCRAP['YOUTUBE'].items():
            with self.subTest(papel=papel):
                r = reg.adaptador_de('YOUTUBE', capacidade)
                self.assertIsNotNone(r, capacidade)
                self.assertTrue(r['EXECUTA'] or r['ROTA'],
                                '%s deixou de ter rota' % capacidade)
        t = _codigo('coleta/comunicacao_coleta.py')
        self.assertIn('scrap_executor', t,
                      'o ramo canonico deixou de chamar o executor')


class ACapacidadeNaoEstaLigada(unittest.TestCase):
    """DECLARED CAPABILITY != WIRED CAPABILITY != OBSERVED FLOW."""

    def test_12_nenhuma_capacidade_de_post_pago_esta_wired(self):
        import scrap_capacidades as cap
        for plat in ('INSTAGRAM', 'FACEBOOK', 'LINKEDIN'):
            with self.subTest(plataforma=plat):
                nome = cap.pela_matriz(plat, 'FETCH_POST')
                if nome is None:
                    continue
                r = reg.adaptador_de(plat, nome)
                self.assertFalse(r and (r['EXECUTA'] or r['ROTA']),
                                 '%s/%s ficou WIRED: a convergencia avancou e o '
                                 'veredito da C10.6E tem de ser remedido'
                                 % (plat, nome))

    def test_13_o_portao_do_gasto_recusa_antes_de_qualquer_chamada(self):
        padrao = mz._rota_padrao(mz.MATRIZ['INSTAGRAM']['FETCH_COMMENTS'])
        self.assertEqual(padrao['CLASSE'], 'APIFY',
                         'a sonda mede uma capacidade que deixou de ser paga')
        _o, sem = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                              run_id='T-GATE')
        self.assertEqual(sem.get('ESTADO_ORIGINAL'), 'PAID_ROUTE_REFUSED')
        self.assertEqual(sem['ESTADO'], fx.traduzir('PAID_ROUTE_REFUSED'))
        self.assertEqual(sem['COST_USD'], 0.0)

    def test_14_motivo_de_gasto_fora_do_vocabulario_e_recusado(self):
        _o, r = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                            run_id='T-GATE-2', permitir_pago=True,
                            motivo_pago='a Apify ja estava configurada')
        self.assertEqual(r.get('ESTADO_ORIGINAL'), 'PAID_ROUTE_REFUSED')
        # controlo positivo: um motivo do vocabulario passa o portao
        _o, ok = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                             run_id='T-GATE-3', permitir_pago=True,
                             motivo_pago='FREE_ROUTE_UNAVAILABLE')
        self.assertNotEqual(ok.get('ESTADO_ORIGINAL'), 'PAID_ROUTE_REFUSED')


class ARunTemUmDonoSo(unittest.TestCase):
    """ONE CONCEPT → ONE OWNER, medido — e hoje ele nao esta cumprido."""

    def test_15_o_censo_dos_cunhadores_de_corrida_esta_escrito(self):
        """Tres sitios cunham RUN_ID. O documento desta missao nomeia os tres."""
        doc = _fonte('docs/sintonia-scrap/C10-6E-RUNTIME-PAGO-UM-SO.md')
        for sitio in ('orquestrador', 'scrap_executor', 'comunicacao_coleta'):
            self.assertIn(sitio, doc, 'o documento nao nomeia %s' % sitio)
        self.assertIn('RUN_DUAL_OWNERSHIP', doc)

    def test_16_o_recibo_nao_e_o_dono_da_corrida_canonica(self):
        """O RUN-MANIFEST continua a cunhar o proprio `RUN_ID`. Isto NAO foi
        corrigido nesta missao, e a sentinela existe para que o facto nao se
        perca — nao para o abencoar."""
        t = _codigo('orquestrador/orquestrador.py')
        self.assertIn('novo_run_id', t,
                      'o orquestrador deixou de cunhar: remedir a FASE 8')
        self.assertNotIn('collection_run', t,
                         'o orquestrador passou a ler a corrida canonica: o gap '
                         'fechou-se e o veredito tem de ser remedido')


class OContratoDaSaidaNaoSePerde(unittest.TestCase):
    """RAW != DERIVED. Um normalizado que nao aponta para o bruto e orfao."""

    def test_17_o_normalizado_aponta_para_o_RAW(self):
        arv = ast.parse(_fonte('coleta/comunicacao_coleta.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'normalizar')
        campos = {n.value for n in ast.walk(fn) if isinstance(n, ast.Constant)
                  and isinstance(n.value, str)}
        for obrigatorio in ('RAW_REFERENCE', 'RAW_COMPLETENESS',
                            'COLLECTION_RUN_ID', 'COLLECTION_PROVIDER'):
            self.assertIn(obrigatorio, campos,
                          'o normalizado perdeu %s: o item deixa de saber de que '
                          'bruto e de que corrida veio' % obrigatorio)

    def test_18_a_proveniencia_vem_do_manifesto_e_nao_do_item(self):
        """Um item que se auto-declara a corrida e um item que se assina sozinho."""
        fonte = _fonte('coleta/comunicacao_coleta.py')
        arv = ast.parse(fonte)
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'normalizar')
        trecho = ast.get_source_segment(fonte, fn) or ''
        self.assertIn("man.get('RAW_EVIDENCE_PATH'", trecho)
        self.assertIn("man.get('RUN_ID'", trecho)

    def test_19_o_normalizador_corre_sobre_bruto_preservado(self):
        """FASE 13: a comparacao de formato usa RAW guardado, nunca corrida nova."""
        import gzip
        import json
        caminho = os.path.join(RAIZ, 'data', 'samples', 'raw-paid',
                               'ES-T8-003-instagram-hashtags.raw.json.gz')
        self.assertTrue(os.path.exists(caminho),
                        'o RAW historico do Instagram sumiu; sem ele a FASE 13 '
                        'fica BLOCKED_ARTIFACT_GAP')
        with gzip.open(caminho, 'rt', encoding='utf-8') as f:
            bruto = json.load(f)
        self.assertTrue(bruto, 'o RAW preservado esta vazio')
        conta = {'ACCOUNT_HANDLE': 'x', 'ACCOUNT_URL': 'https://exemplo/x',
                 'COMPANY': 'EXEMPLO', 'COUNTRY': 'ES'}
        man = {'RUN_ID': 'HIST-ES-T8-003',
               'RAW_EVIDENCE_PATH': 'data/samples/raw-paid/'
                                    'ES-T8-003-instagram-hashtags.raw.json.gz',
               'RAW_COMPLETENESS': 'PRESERVED', 'COLLECTION_PROVIDER': 'APIFY'}
        item = cc.normalizar(bruto[0], conta, 'INSTAGRAM', 30, man)
        self.assertEqual(item['COLLECTION_RUN_ID'], 'HIST-ES-T8-003')
        self.assertEqual(item['RAW_REFERENCE'], man['RAW_EVIDENCE_PATH'])
        self.assertEqual(item['PLATFORM'], 'INSTAGRAM')
        self.assertNotEqual(item['POST_ID'], item['URL'],
                            'o identificador do item virou a URL')


class ORelatorioNaoPodeDizerQueProvou(unittest.TestCase):
    """CAN DO != DID DO. Nenhuma fixture desta missao vira prova de rota."""

    def test_20_o_documento_declara_que_a_rota_paga_nao_foi_provada(self):
        doc = _fonte('docs/sintonia-scrap/C10-6E-RUNTIME-PAGO-UM-SO.md')
        self.assertIn('PAID_ROUTE_RUNTIME_PROVEN = NO', doc,
                      'o documento passou a dizer que a rota paga foi provada, e '
                      'nesta missao nenhuma corrida paga aconteceu')
        self.assertIn('LIVE_PROOF_REQUIRED = YES', doc)
        self.assertIn('APIFY_RUNS = 0', doc)

    def test_21_o_pacote_da_prova_paga_nao_inventa_custo(self):
        doc = _fonte('docs/sintonia-scrap/C10-6E-RUNTIME-PAGO-UM-SO.md')
        self.assertIn('ESTIMATED_MAX_COST_USD   UNKNOWN_NEEDS_MEASUREMENT', doc,
                      'o pacote da prova paga ganhou um custo que ninguem mediu')
        self.assertIn('REAL_ROUTE_COST', doc)


if __name__ == '__main__':
    unittest.main(verbosity=2)
