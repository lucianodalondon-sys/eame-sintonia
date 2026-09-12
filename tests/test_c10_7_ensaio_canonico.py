#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.7 — O ENSAIO CANONICO DE CAPACIDADE.

A ferramenta recusava tudo o que ainda nao tinha provado, e isso esta certo para
producao. So que nao havia forma de provar coisa nenhuma por dentro:

    NOT_EXECUTED → o CHECK recusa → para deixar de o ser tem de correr uma vez
    → corre por um script lateral → alguem «integra» → nasce um bypass.

    UMA FERRAMENTA QUE RECUSA TUDO O QUE AINDA NAO PROVOU
    FAZ NASCER TODA CAPACIDADE NOVA FORA DELA.

Duas capacidades estao nesse ciclo HOJE, com adaptador ligado e politica
permitida. E o `piloto` do `social_scrap.py` — que a C10.6D mediu a saltar o
boundary — e o script lateral que o ciclo ja produziu.

O conserto e um TERCEIRO EIXO no mesmo executor, e a unica diferenca entre os
dois modos e o portao epistemologico da CAPABILITY_STATE.

    TRIAL NAO SOBRESCREVE POLICY.
    TRIAL NAO AUTORIZA GASTO.
    TRIAL_ELIGIBLE != PRODUCTION_READY.
    TRIAL PASSADO != CAPACIDADE PROVADA.
"""
import ast
import io
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import scrap_capacidades as cap    # noqa: E402
import scrap_executor as sx        # noqa: E402
import scrap_registo as reg        # noqa: E402
import social_matriz as mz         # noqa: E402
import social_rotas as sr          # noqa: E402
reg.carregar_adaptadores()


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _codigo(rel):
    texto = _fonte(rel)
    arv = ast.parse(texto)
    prosa = {ast.get_docstring(n, clean=False) for n in ast.walk(arv)
             if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef))}
    prosa.discard(None)
    for p in prosa:
        texto = texto.replace(p, '')
    return re.sub(r'(?m)^\s*#.*$', '', texto)


def _presas():
    """As capacidades que o ciclo prendia: nao prometem, e tem rota."""
    return [(v['PLATFORM'], n) for n, v in sx.CAPABILITIES().items()
            if not v['PROMISES_RESULT'] and v['HAS_ROUTE']
            and v['CAPABILITY_STATE'] not in sx.SEM_ENSAIO]


class AProducaoNaoMudou(unittest.TestCase):
    """A sentinela mais importante desta missao. Se ela cair, o ensaio virou
    atalho — e um atalho e exactamente o que ele existe para nao ser."""

    def test_1_normal_continua_a_recusar_o_que_nao_promete(self):
        recusadas = 0
        for nome, v in sx.CAPABILITIES().items():
            if v['PROMISES_RESULT']:
                continue
            with self.subTest(capacidade=nome):
                r = sx.CHECK(v['PLATFORM'], nome)
                self.assertFalse(r['CAN'], '%s passou em NORMAL' % nome)
                self.assertFalse(r['PRODUCTION_READY'])
                recusadas += 1
        self.assertGreaterEqual(recusadas, 5,
                                'a sonda nao encontrou capacidades sem promessa; '
                                'ela nao prova nada')

    def test_2_o_modo_por_omissao_e_NORMAL(self):
        """Uma assinatura cujo default e o modo permissivo e um atalho com outro
        nome. Medido nas duas funcoes."""
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        for alvo in ('CHECK', 'COLLECT'):
            with self.subTest(funcao=alvo):
                fn = next(n for n in ast.walk(arv)
                          if isinstance(n, ast.FunctionDef) and n.name == alvo)
                nomes = [a.arg for a in fn.args.kwonlyargs]
                self.assertIn('modo', nomes, '%s nao aceita modo' % alvo)
                i = nomes.index('modo')
                padrao = fn.args.kw_defaults[i]
                self.assertIsInstance(padrao, ast.Name)
                self.assertEqual(padrao.id, 'NORMAL',
                                 '%s passou a ter TRIAL por omissao' % alvo)

    def test_3_modo_desconhecido_levanta(self):
        for chamada in (lambda: sx.CHECK('MASTODON', 'mastodon.hashtag.search',
                                         modo='SEMPRE'),
                        lambda: sx.COLLECT(platform='MASTODON',
                                           capability='mastodon.hashtag.search',
                                           run_id='T', modo='SEMPRE')):
            with self.assertRaises(ValueError):
                chamada()


class OCicloEstavaFechado(unittest.TestCase):

    def test_4_ha_capacidade_presa_no_ciclo(self):
        """Se um dia nao houver nenhuma, esta missao deixou de ter objeto — e a
        sentinela avisa em vez de passar em silencio sobre o vazio."""
        presas = _presas()
        self.assertTrue(presas,
                        'nenhuma capacidade sem promessa tem rota ligada; '
                        'remedir a razao de existir do ensaio')
        for plat, nome in presas:
            with self.subTest(capacidade=nome):
                m = cap.da_matriz(nome)
                if m:
                    self.assertEqual(mz.decisao(plat, m)['DECISAO'],
                                     mz.PERMITIDA_SIM,
                                     '%s tem rota e a politica nao permite' % nome)

    def test_5_o_ensaio_alcanca_exactamente_essas(self):
        for plat, nome in _presas():
            with self.subTest(capacidade=nome):
                normal = sx.CHECK(plat, nome)
                ensaio = sx.CHECK(plat, nome, modo=sx.TRIAL)
                self.assertFalse(normal['CAN'])
                self.assertTrue(ensaio['CAN'], '%s nao entra em ensaio' % nome)
                self.assertEqual(ensaio['STATE'], sx.ELEGIVEL_PARA_ENSAIO)
                self.assertFalse(ensaio['PRODUCTION_READY'],
                                 '%s: o ensaio prometeu producao' % nome)


class OCheckNaoMente(unittest.TestCase):
    """FASE 17: nunca um `CAN = True` para duas coisas diferentes sem dizer qual."""

    def test_6_os_dois_eixos_vem_sempre_separados(self):
        for nome, v in sx.CAPABILITIES().items():
            for modo in (sx.NORMAL, sx.TRIAL):
                r = sx.CHECK(v['PLATFORM'], nome, modo=modo)
                with self.subTest(capacidade=nome, modo=modo):
                    self.assertIn('PRODUCTION_READY', r)
                    self.assertIn('TRIAL_ELIGIBLE', r)
                    self.assertEqual(r['EXECUTION_MODE'], modo)
                    if r['CAN']:
                        self.assertTrue(r['PRODUCTION_READY']
                                        or r['TRIAL_ELIGIBLE'])
                        self.assertEqual(r['STATE'] == sx.PODE,
                                         r['PRODUCTION_READY'],
                                         '%s: `CAN_COLLECT_NOW` e '
                                         'PRODUCTION_READY separaram-se' % nome)

    def test_7_producao_pronta_continua_a_dizer_PODE(self):
        prontas = [(v['PLATFORM'], n) for n, v in sx.CAPABILITIES().items()
                   if v['PRODUCTION_READY']]
        self.assertTrue(prontas, 'a sonda nao ve capacidade pronta nenhuma')
        for plat, nome in prontas:
            with self.subTest(capacidade=nome):
                r = sx.CHECK(plat, nome, modo=sx.TRIAL)
                # em ensaio, uma capacidade pronta continua a dizer PODE:
                # o ensaio nao a rebaixa.
                if r['CAN']:
                    self.assertEqual(r['STATE'], sx.PODE)


class APoliticaGanhaSempre(unittest.TestCase):

    def test_8_o_ensaio_nao_abre_rota_proibida(self):
        self.assertEqual(mz.decisao('LINKEDIN', 'FETCH_POST')['DECISAO'],
                         mz.NAO_PERMITIDA)
        gastos = []
        import scrap_http as http
        original = http.buscar
        http.buscar = lambda *a, **k: gastos.append(a) or '[]'
        try:
            _o, r = sr.executar(platform='LINKEDIN', capability='FETCH_POST',
                                run_id='T-POL')
        finally:
            http.buscar = original
        self.assertEqual(r['ESTADO'], 'ROUTE_NOT_ALLOWED')
        self.assertEqual(gastos, [], 'o ensaio chegou ao fornecedor')

    def test_9_o_executor_nao_conhece_o_eixo_do_gasto(self):
        """TRIAL nao e autorizacao de gasto, e a forma de o provar e que o
        executor nao tem como a conceder: quem decide gasto e o roteador."""
        t = _codigo('coleta/scrap_executor.py')
        for proibido in ('permitir_pago', 'motivo_pago', 'MOTIVOS_PAGOS'):
            self.assertNotIn(proibido, t,
                             'o executor passou a mexer no gasto: %s' % proibido)

    def test_10_a_rota_paga_continua_a_exigir_autorizacao(self):
        _o, r = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                            run_id='T-PAGO')
        self.assertEqual(r.get('ESTADO_ORIGINAL'), 'PAID_ROUTE_REFUSED')
        self.assertEqual(r['COST_USD'], 0.0)


class BlockedNaoViraExecutavel(unittest.TestCase):
    """FASE 14/15 — e a razao NAO e cautela, e um achado de modelo."""

    def test_11_blocked_recusa_tambem_em_ensaio(self):
        bloqueadas = [(v['PLATFORM'], n) for n, v in sx.CAPABILITIES().items()
                      if v['CAPABILITY_STATE'] == 'BLOCKED']
        self.assertTrue(bloqueadas, 'nao ha BLOCKED para medir')
        for plat, nome in bloqueadas:
            with self.subTest(capacidade=nome):
                r = sx.CHECK(plat, nome, modo=sx.TRIAL)
                self.assertFalse(r['CAN'])
                self.assertEqual(r['STATE'], sx.ENSAIO_RECUSADO)
                self.assertFalse(r['TRIAL_ELIGIBLE'])

    def test_12_a_conflacao_esta_registada_e_nao_corrigida(self):
        """O `BLOCKED` de `facebook.content` foi medido numa ROTA e num HOST, e
        a matriz declara a capacidade ALLOWED por outras duas rotas. Enquanto o
        estado disser duas coisas, ele nao entra em ensaio."""
        self.assertEqual(cap.estado('facebook.content'), 'BLOCKED')
        self.assertEqual(mz.decisao('FACEBOOK', 'FETCH_POST')['DECISAO'],
                         mz.PERMITIDA_SIM,
                         'a politica do Facebook mudou; remedir a FASE 15')
        rotas = [r['ROTA'] for r in mz.MATRIZ['FACEBOOK']['FETCH_POST']]
        self.assertNotIn('gallery-dl', ' '.join(rotas),
                         'a rota medida como BLOCKED entrou na matriz; remedir')
        doc = _fonte('docs/sintonia-scrap/C10-7-TRIAL-CANONICO-DE-CAPACIDADE.md')
        self.assertIn('CAPABILITY_ROUTE_STATE_CONFLATION = YES', doc,
                      'o achado de modelo deixou de estar registado')


class OEnsaioNaoPromoveEstado(unittest.TestCase):
    """CRITICO. Um ensaio que promove estado e uma medicao que se auto-assina."""

    def test_13_o_executor_nao_escreve_na_declaracao(self):
        t = _codigo('coleta/scrap_executor.py')
        for proibido in ("open(", "write_text", "json.dump", "DECLARADAS["):
            self.assertNotIn(proibido, t,
                             'o executor ganhou como escrever: %s' % proibido)

    def test_14_o_trace_carrega_a_prova_de_que_nao_promoveu(self):
        import scrap_http as http
        import social_envelope as env
        import shutil
        import tempfile
        gaveta = tempfile.mkdtemp(prefix='c107t-')
        raw, buscar = env.RAW_DIR, http.buscar
        env.RAW_DIR = gaveta
        http.buscar = lambda *a, **k: (
            '[{"id":"1","uri":"u","url":"u","created_at":"2026-09-01T10:00:00Z",'
            '"content":"<p>x</p>","account":{"acct":"a"}}]')
        try:
            antes = cap.estado('mastodon.account.incremental')
            _o, trace = sx.COLLECT(platform='MASTODON',
                                   capability='mastodon.account.incremental',
                                   run_id='T-TRIAL', modo=sx.TRIAL,
                                   instancia='exemplo.social', acct_id='1',
                                   limit=5)
        finally:
            env.RAW_DIR, http.buscar = raw, buscar
            shutil.rmtree(gaveta, ignore_errors=True)
        self.assertEqual(trace['EXECUTION_MODE'], sx.TRIAL)
        self.assertEqual(trace['CAPABILITY_STATE_BEFORE'], antes)
        self.assertEqual(trace['CAPABILITY_STATE_AFTER'], antes)
        self.assertEqual(cap.estado('mastodon.account.incremental'), antes)


class ATrilhaEAMesma(unittest.TestCase):
    """FASE 9 — a unica diferenca e o portao. Se nascer outra, isto avisa."""

    def test_15_o_modo_so_toca_o_portao_epistemologico(self):
        fonte = _fonte('coleta/scrap_executor.py')
        arv = ast.parse(fonte)
        for alvo in ('CHECK', 'COLLECT'):
            fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                      and n.name == alvo)
            trecho = ast.get_source_segment(fonte, fn) or ''
            # cada comparacao com o modo tem de estar perto do estado da
            # capacidade — nunca perto de rota, fornecedor ou gasto.
            for linha in trecho.splitlines():
                if 'modo ==' not in linha and 'modo not in' not in linha:
                    continue
                for proibido in ('ROTA', 'rota', 'provider', 'pago', 'CLASSE'):
                    self.assertNotIn(proibido, linha,
                                     '%s: o modo passou a decidir %s'
                                     % (alvo, proibido))

    def test_16_nao_nasceu_um_segundo_executor(self):
        proibidos = ('trial_executor.py', 'experimental_router.py',
                     'probe_runtime.py', 'scrap_v2.py', 'scrap_executor_v2.py')
        for raiz, dirs, fs in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('.git', 'node_modules', '__pycache__', 'BASELINE')]
            for f in fs:
                self.assertNotIn(f, proibidos,
                                 'nasceu um segundo runtime: %s' % f)

    def test_17_o_dono_do_caminho_continua_a_ser_um_so(self):
        t = _codigo('coleta/scrap_executor.py')
        self.assertIn('_despachar', t)
        self.assertEqual(t.count('def COLLECT'), 1,
                         'ha mais de uma COLLECT no executor')


class AIntrospeccaoConcordaComOsDonos(unittest.TestCase):

    def test_18_has_route_tem_um_dono_so(self):
        for nome, v in sx.CAPABILITIES().items():
            with self.subTest(capacidade=nome):
                self.assertEqual(v['HAS_ROUTE'],
                                 reg.tem_caminho(v['PLATFORM'], nome),
                                 '%s: a introspeccao e o registo discordam' % nome)

    def test_19_os_tres_eixos_estao_expostos(self):
        for nome, v in sx.CAPABILITIES().items():
            with self.subTest(capacidade=nome):
                self.assertIn('PROMISES_RESULT', v)
                self.assertIn('POLICY_DECISION', v)
                self.assertIn('TRIAL_ELIGIBLE', v)
                if v['CAPABILITY_STATE'] in sx.SEM_ENSAIO:
                    self.assertFalse(v['TRIAL_ELIGIBLE'])

    def test_20_a_introspeccao_nao_abre_ligacao(self):
        import scrap_http as http
        chamadas = []
        original = http.buscar
        http.buscar = lambda *a, **k: chamadas.append(a) or '[]'
        try:
            sx.CAPABILITIES()
        finally:
            http.buscar = original
        self.assertEqual(chamadas, [], 'CAPABILITIES passou a tocar a rede')


if __name__ == '__main__':
    unittest.main(verbosity=2)
