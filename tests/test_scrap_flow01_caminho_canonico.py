# -*- coding: utf-8 -*-
"""SCRAP-FLOW-01 — um fluxo operacional real atravessa o orquestrador canônico.

    MODULE CAN'T SPEND != FLOW IS CANONICAL.
    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

Vinte ataques. Todos têm de cair.
"""
import ast
import io
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('orquestrador', 'pedido', 'coleta', 'leis', 'regras', 'ferramentas',
           'medidas', 'guarda', 'tests', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import autorizacao_de_gasto as az                                 # noqa: E402
import ingresso as ing                                            # noqa: E402
import orquestrador as orq                                        # noqa: E402
import pedido as pd                                               # noqa: E402
import receitas as rec                                            # noqa: E402
import retorno_da_coleta as rc                                    # noqa: E402
import scrap_colheita as sc                                       # noqa: E402

WORKFLOW = '.github/workflows/sintonia-scrap.yml'
FONTE = 'IT-T9-001'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _sem_comentarios(texto):
    """O YAML sem a prosa. Uma sonda que lê comentários lê o que eu escrevi."""
    return '\n'.join(re.sub(r'(?<!\$)#.*$', '', l) for l in texto.splitlines())


def _so_codigo(texto):
    """A fonte SEM comentários nem docstrings.

    RT18 procurava «relevancia» no executor do SCRAP e apanhou o COMENTÁRIO que
    explica por que o modo desce até ao dono da compra — a frase que diz,
    precisamente, que quem julga relevância não é aquele ficheiro. É a quarta
    missão seguida com esta armadilha.

        UMA SONDA QUE LÊ A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA
        E CHAMA-LHE VIOLAÇÃO DA REGRA.
    """
    import tokenize
    fora, anterior = [], tokenize.INDENT
    for tok in tokenize.generate_tokens(io.StringIO(texto).readline):
        if tok.type == tokenize.COMMENT:
            continue
        if (tok.type == tokenize.STRING
                and anterior in (tokenize.INDENT, tokenize.NEWLINE,
                                 tokenize.NL, tokenize.DEDENT)):
            continue
        if tok.type not in (tokenize.NL, tokenize.NEWLINE):
            anterior = tok.type
        fora.append(tok.string)
    return '\n'.join(fora)


def _funcao(rel, nome):
    for no in ast.walk(ast.parse(_fonte(rel))):
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    raise AssertionError('%s não tem %s' % (rel, nome))


def _executor_da_fase(fase, fonte=FONTE):
    p = pd.de_uma_frase('colete concorrentes')
    p.filtros.update({'fase': fase, 'pais': 'IT'})
    if fonte:
        p.filtros['fonte'] = fonte
    return rec.resolver(p).executores[0]


# ══════════════════════════════════════════════════════════════════════════
# RT1–RT4 · O DISPARADOR PEDE; ELE NÃO CONDUZ
# ══════════════════════════════════════════════════════════════════════════
class ODisparadorPedeNaoConduz(unittest.TestCase):

    def test_rt01_a_fase_migrada_nao_chama_mais_o_script(self):
        """SELECTED_ENTRYPOINT_DIRECT_BYPASS = NO."""
        y = _sem_comentarios(_fonte(WORKFLOW))
        ramo = y[y.index('janela|janela-perfis|janela-objetos)'):]
        ramo = ramo[:ramo.index(';;')]
        self.assertIn('orquestrador/orquestrador.py', ramo)
        self.assertNotIn('social_scrap.py', ramo,
                         'a fase migrada voltou a chamar o script direto')

    def test_rt02_o_disparador_nao_conhece_ator_rota_nem_provider(self):
        """WORKFLOW É DISPARADOR. WORKFLOW NÃO É MOTOR."""
        y = _sem_comentarios(_fonte(WORKFLOW))
        ramo = y[y.index('janela|janela-perfis|janela-objetos)'):]
        ramo = ramo[:ramo.index(';;')]
        for proibido in ('instagram_janela', 'adaptador_', 'apify', 'COLLECT',
                         'scrap_executor', 'instagram.profile'):
            self.assertNotIn(proibido, ramo,
                             'o disparador passou a conhecer %s' % proibido)

    def test_rt03_o_pedido_nao_conhece_o_ator(self):
        """O request diz O QUE quer; quem escolhe COMO é o orquestrador."""
        e = _executor_da_fase('janela-perfis')
        p = pd.de_uma_frase('colete concorrentes')
        p.filtros.update({'fase': 'janela-perfis', 'fonte': FONTE})
        self.assertNotIn('actor', json.dumps(p.para_json()).lower())
        self.assertEqual(e['roda'], ['coleta/scrap_colheita.py'])

    def test_rt04_o_orquestrador_nao_conhece_instagram_nem_youtube(self):
        """Ele escolhe o executor; a plataforma é do SCRAP."""
        codigo = _so_codigo(_fonte('orquestrador/orquestrador.py'))
        for proibido in ('instagram', 'youtube', 'INSTAGRAM', 'YOUTUBE',
                         'apify', 'Apify'):
            self.assertNotIn(proibido, codigo,
                             'o orquestrador passou a conhecer %s' % proibido)


# ══════════════════════════════════════════════════════════════════════════
# RT5–RT7 · SUPORTE NÃO É OBSERVAÇÃO (COL-LAW-505)
# ══════════════════════════════════════════════════════════════════════════
class SuporteNaoEObservacao(unittest.TestCase):

    def _envelope(self, **kw):
        base = {'RUN_ID': 'R1', 'EXECUTOR_ID': 'e', 'EXECUTOR_VERSION': 'v',
                'ESTADO': rc.SUCCESS, 'COLHEITA': [], 'SUPORTE': [], 'ERROS': []}
        base.update(kw)
        return base

    def test_rt05_manifest_nao_vira_colheita(self):
        env = self._envelope(COLHEITA=[{'ESPECIE': rc.MANIFEST}])
        self.assertEqual(rc.so_o_que_entra(env), [])
        self.assertTrue(rc.conferir(env, RAIZ))

    def test_rt06_run_receipt_nao_vira_observacao(self):
        env = self._envelope(COLHEITA=[{'ESPECIE': rc.RUN_RECEIPT}])
        self.assertEqual(rc.so_o_que_entra(env), [])

    def test_rt06b_plan_e_catalog_tambem_nao(self):
        for especie in (rc.PLAN, rc.CATALOG, rc.ESPECIE_DESCONHECIDA):
            env = self._envelope(COLHEITA=[{'ESPECIE': especie}])
            self.assertEqual(rc.so_o_que_entra(env), [], especie)

    def test_rt07_quem_declara_envelope_e_lido_pela_especie(self):
        """Para um retorno DECLARADO, a espécie decide — nunca a heurística.

        ⚠️ E A HEURÍSTICA NÃO MORREU: ela continua a servir os quatro
        executores que ainda não declaram envelope, porque calá-los de uma vez
        seria migrar cinco caminhos numa missão que migra UM. O que mudou é que
        ela deixou de ser silenciosa — sai contada no recibo, com nome.

            UMA DÍVIDA MEDIDA É UMA DÍVIDA. UMA DÍVIDA CALADA É UM BUG.

        Esta sentinela guarda as duas metades: a espécie manda onde há
        envelope, e a adivinhação é declarada onde não há.
        """
        no = _funcao('orquestrador/orquestrador.py', 'a_colheita')
        corpo = ast.unparse(no)
        self.assertIn('so_o_que_entra', corpo,
                      'a porta deixou de ler a espécie declarada')
        # ⚠️ A DIVIDA QUE ESTA SENTINELA MEDIA FOI PAGA, E POR ISSO ELA MUDOU.
        # Ela exigia `_envelope_declarado` e `RETORNO_ADIVINHADO`: a
        # adivinhacao continuava viva para os executores que ainda nao
        # declaravam envelope, e o que se cobrava era que ela fosse CONTADA
        # em vez de silenciosa.
        #
        # Na linha funcional ela deixou de existir. `a_colheita` corre SEMPRE
        # `conferir()` + `so_o_que_entra()` sobre um envelope declarado, e nao
        # ha ramo que adivinhe — nem calado nem contado.
        #
        #     UMA DIVIDA PAGA NAO SE GUARDA: GUARDA-SE O QUE A SUBSTITUIU.
        #
        # A propriedade que sobrevive e mais forte: nao existe caminho de
        # adivinhacao nenhum. Se um voltar, esta linha reprova.
        self.assertIn('conferir', corpo,
                      'a colheita deixou de conferir o envelope')
        for adivinha in ('RETORNO_ADIVINHADO', 'isinstance(v, list)',
                         'next((v for v in d.values()'):
            self.assertNotIn(adivinha, corpo,
                             'a adivinhacao do retorno voltou ao caminho')

    def test_rt07b_o_executor_migrado_declara_envelope(self):
        # ⚠️ O CONCEITO E O MESMO; O NOME PASSOU A SER O DA CASA.
        # A receita do SCRAP dizia `envelope_em`; as outras cinco dizem
        # `retorno: {ESPECIE: caminho}`, que e a forma da COL-LAW-505 — ela
        # nomeia a ESPECIE do que volta, e nao so o sitio. O orquestrador le
        # `retorno`, e com o nome antigo ele corria o executor, nao encontrava
        # nada e seguia em frente, sem erro nenhum.
        #
        #     DOIS NOMES PARA O MESMO CONCEITO NAO SAO SINONIMOS:
        #     SAO UM CAMINHO QUE NINGUEM PERCORRE.
        e = _executor_da_fase('janela-perfis')
        self.assertTrue((e.get('retorno') or {}).get('ENVELOPE'),
                        'o executor do SCRAP deixou de declarar o retorno')

    def test_rt07b_quem_nao_declara_envelope_nao_entrega_colheita(self):
        """O LEGADO SÓ PODE DECLARAR SUPORTE."""
        env = rc.envelope_do_legado('R1', 'e', 'v',
                                    {'x': rc.COLHEITA}, RAIZ)
        self.assertEqual(env['COLHEITA'], [])
        self.assertTrue(env['ERROS'])
        self.assertEqual(env['SUPORTE'][0]['ESPECIE'], rc.ESPECIE_DESCONHECIDA)


# ══════════════════════════════════════════════════════════════════════════
# RT8–RT11 · IDENTIDADE NÃO SE FABRICA
# ══════════════════════════════════════════════════════════════════════════
class IdentidadeNaoSeFabrica(unittest.TestCase):

    def test_rt08_source_id_nao_nasce_de_url(self):
        """A fonte DESCE COM O PEDIDO. URL NÃO É SOURCE_ID."""
        objeto = {'URL': 'https://www.instagram.com/p/AAA/',
                  'SOURCE_ACCOUNT': 'basf_italia', 'PLATFORM': 'INSTAGRAM'}
        u = sc.unidade(objeto, run_id='R1', fonte=FONTE)
        self.assertEqual(u['SOURCE_ID'], FONTE)
        # e sem fonte, o adapter não inventa: não há unidade nenhuma
        no = _funcao('coleta/scrap_colheita.py', 'colher')
        corpo = ast.unparse(no)
        self.assertIn('if not fonte', corpo)
        self.assertNotIn("SOURCE_ACCOUNT", corpo)

    def test_rt09_document_id_nao_nasce_de_sha(self):
        u = sc.unidade({'URL': 'u'}, run_id='R1', fonte=FONTE)
        self.assertEqual(u['DOCUMENT_ID'], rc.NAO_SEI)
        mal = rc.conferir_unidade(dict(u, DOCUMENT_ID='a3f5c9d1e2b4',
                                       SHA256='a3f5c9d1e2b4'), 'R1', RAIZ)
        self.assertTrue(any('fabricado' in m for m in mal))

    def test_rt10_raw_observation_id_nao_nasce_de_caminho(self):
        """RAW_OBSERVATION_ID = raw_asset.id, e mais nada."""
        # ⚠️ A LEI E A MESMA; O MECANISMO QUE A CUMPRIA MUDOU.
        # Antes, o ingresso carimbava `RAW_OBSERVATION_ID: NAO_SEI_ID` num
        # segundo balde (`ENTRADOS`). Esse balde era uma SEGUNDA PORTA — so
        # uma das duas listas passava pelo tradutor do texto — e saiu na
        # integracao. O carimbo util viaja agora na unidade CANONICA.
        #
        # A propriedade que sobrevive e mais forte do que a antiga: o campo
        # nao e carimbado de todo nesta fronteira, porque quem o cunha e o
        # banco. Ele NAO esta na lista dos que atravessam.
        #
        #     RAW_OBSERVATION_ID = raw_asset.id, E MAIS NADA.
        import coleta.ingresso as _ing
        self.assertNotIn('RAW_OBSERVATION_ID', _ing.DA_FICHA_PARA_A_PORTA,
                         'a fronteira voltou a carimbar uma identidade que '
                         'ela nao cunha')
        no = _funcao('coleta/ingresso.py', 'receber')
        corpo = ast.unparse(no)
        for errado in ('RAW_OBSERVATION_ID": f.SHA256',
                       'RAW_OBSERVATION_ID": f.STORAGE_LOCATION',
                       "RAW_OBSERVATION_ID': f.SHA256",
                       "RAW_OBSERVATION_ID': f.STORAGE_LOCATION"):
            self.assertNotIn(errado, corpo)

    def test_rt11_o_estagio_atravessa_a_fronteira_do_ingresso(self):
        """O ITEM QUE SAI DO INGRESSO NÃO É O ITEM QUE ENTROU."""
        no = _funcao('orquestrador/orquestrador.py', 'correr')
        corpo = ast.unparse(no)
        # ⚠️ ANTES ESTA SENTINELA EXIGIA `ENTRADOS`, o segundo balde do SCRAP.
        # Ele saiu: duas listas a chegar a quem julga sao duas travessias, e
        # so uma passa pelo tradutor do texto — a observacao do SCRAP seria
        # julgada sem o contrato do texto aplicado.
        #
        #     UMA SEGUNDA LISTA PARA A ADMISSAO E UMA SEGUNDA PORTA.
        #
        # A lei nao mudou, e e a mesma frase do docstring: o item que sai do
        # ingresso nao e o item que entrou. O que se cobra agora e que quem
        # julga receba a unidade CANONICA — e nunca a lista original.
        self.assertIn('PARA_A_PORTA', corpo,
                      'a admissão voltou a receber a lista original')
        self.assertNotIn('pela_porta(itens', corpo)
        # E O FALLBACK AO LEGADO NAO VOLTA — SEJA QUAL FOR A GRAFIA DELE.
        #
        # ⚠️ ESTA LINHA JA FOI `assertNotIn('else itens', corpo)`, e o red team
        # da integracao atravessou-a a primeira: bastou escrever o MESMO
        # fallback de outra maneira.
        #
        #     `a_julgar = entrados if entrados else itens`   <- apanhado
        #     `julgar = ...get('PARA_A_PORTA') or itens`     <- NAO apanhado
        #
        # Sao a mesma lei quebrada, e a sentinela so conhecia uma das
        # escritas.
        #
        #     UMA SENTINELA QUE FIXA A GRAFIA GUARDA A GRAFIA.
        #     QUEM QUER GUARDAR A LEI TEM DE OLHAR PARA A LEI.
        #
        # A lei e esta: `itens` — a lista ORIGINAL do executor — nao pode
        # aparecer em lado nenhum da atribuicao de quem vai ser julgado. Por
        # isso a pergunta passou a ser feita sobre a ARVORE e nao sobre o
        # texto: qualquer `Name(id='itens')` dentro do valor atribuido a
        # `julgar` reprova, seja ele um `or`, um ternario, um `if/else`, um
        # `next(...)` ou o que alguem inventar a seguir.
        for _no in ast.walk(no):
            alvos = []
            if isinstance(_no, ast.Assign):
                alvos = [a for a in _no.targets
                         if isinstance(a, ast.Name) and a.id == 'julgar']
            elif isinstance(_no, ast.AugAssign) and \
                    isinstance(_no.target, ast.Name) and _no.target.id == 'julgar':
                alvos = [_no.target]
            if not alvos:
                continue
            nomes = {n.id for n in ast.walk(_no.value)
                     if isinstance(n, ast.Name)}
            self.assertNotIn(
                'itens', nomes,
                'o que vai a admissao voltou a poder ser a lista ORIGINAL '
                '(`itens`) do executor: %s. UMA SEGUNDA PORTA NAO PRECISA DE '
                'SER UMA LISTA NOVA — BASTA UM `or`.' % ast.unparse(_no))


# ══════════════════════════════════════════════════════════════════════════
# RT12–RT15 · OS CONTROLOS DE GASTO CONTINUAM NO CAMINHO
# ══════════════════════════════════════════════════════════════════════════
class OsControlosContinuam(unittest.TestCase):

    def test_rt12_a_guarda_de_gasto_continua_na_primitiva(self):
        no = _funcao('coleta/coletor.py', 'executar')
        corpo = ast.unparse(no)
        # A guarda passou a CONSUMIR, e nao so a validar — SCRAP-OWNER-01.
        self.assertIn('conferir_e_consumir', corpo)
        self.assertLess(corpo.index('conferir_e_consumir'), corpo.index('_curl'))

    def test_rt13_o_adapter_do_fluxo_nao_autoriza_gasto_nenhum(self):
        """Ele não constrói autorização, e a fase que corre é gratuita."""
        codigo = _so_codigo(_fonte('coleta/scrap_colheita.py'))
        for proibido in ('AUTORIZACAO_HUMANA', 'MAX_USD', 'VEREDITO',
                         'pode_comprar', 'autorizacao='):
            self.assertNotIn(proibido, codigo,
                             'o adapter passou a mexer em autorização: %s' % proibido)

    def test_rt14_o_teto_de_rede_e_o_financeiro_continuam_donos(self):
        import coletor as ct
        import scrap_http as http
        self.assertTrue(hasattr(http, 'orcamento_de_rede'))
        self.assertTrue(hasattr(ct, 'orcamento_financeiro'))
        # O nome da recusa convergiu na SCRAP-OWNER-01: `GastoRecusado`,
        # do dono unico. `coletor` re-exporta o antigo apontando para ele.
        self.assertIn(az.GastoRecusado, ct._recusas_nossas())
        self.assertIs(ct.SemAutorizacaoDeGasto, az.GastoRecusado)

    def test_rt15_a_politica_da_rota_continua_a_decidir(self):
        """ROUTE_ALLOWED continua a ser pergunta do roteador, não do fluxo."""
        codigo = _so_codigo(_fonte('coleta/scrap_colheita.py'))
        self.assertNotIn('permitido', codigo)
        self.assertNotIn('social_matriz', codigo)
        # A chamada mede-se na ÁRVORE: `_so_codigo` separa os tokens, e um
        # nome com ponto deixa de existir como texto contínuo.
        no = _funcao('coleta/scrap_colheita.py', 'colher')
        chamadas = {n.func.attr for n in ast.walk(no)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)}
        self.assertIn('COLLECT', chamadas,
                      'o adapter deixou de atravessar o executor do SCRAP')


# ══════════════════════════════════════════════════════════════════════════
# RT16–RT20 · A PROVA NÃO PODE MEDIR-SE A SI PRÓPRIA
# ══════════════════════════════════════════════════════════════════════════
class AProvaNaoSeMedeASiPropria(unittest.TestCase):

    def test_rt16_o_falso_e_um_ficheiro_so_e_e_o_cliente_do_mundo(self):
        """Só o cliente do navegador é falso — nada acima dele."""
        prova = _fonte('provas/o_fluxo_canonico_do_scrap.py')
        self.assertIn("'coleta', 'instagram_janela.py'", prova)
        for real in ('orquestrador', 'scrap_executor', 'ingresso', 'admissao'):
            self.assertNotIn("shutil.copy2(SHIM, os.path.join(destino, '%s'" % real,
                             prova)

    def test_rt17_a_admissao_nao_e_mockada(self):
        no = _funcao('orquestrador/orquestrador.py', 'pela_porta')
        corpo = ast.unparse(no)
        self.assertIn('adm.decidir', corpo)

    def test_rt18_nenhum_classificador_tematico_entrou_no_scrap(self):
        """SCRAP colhe. Quem julga tema é a admissão, na fronteira dela."""
        for rel in ('coleta/scrap_colheita.py', 'coleta/scrap_executor.py'):
            codigo = _so_codigo(_fonte(rel))
            for proibido in ('T2', 'T3', 'T7', 'T9', 'keyword', 'relevancia',
                             'SOURCE_SCORE'):
                self.assertNotIn(proibido, codigo,
                                 '%s ganhou julgamento temático: %s' % (rel, proibido))

    def test_rt19_a_prova_nao_escreve_no_acervo(self):
        """Uma prova que deixa colheita na árvore mede o que ela própria pôs."""
        prova = _fonte('provas/o_fluxo_canonico_do_scrap.py')
        self.assertIn('tempfile.mkdtemp', prova)
        self.assertIn('shutil.rmtree(base', prova)
        self.assertFalse(os.path.exists(os.path.join(RAIZ, 'IDAS-AO-MUNDO.json')))

    def test_rt20_as_sondas_do_yaml_nao_leem_a_propria_prosa(self):
        """UMA SONDA QUE LÊ A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA."""
        bruto = _fonte(WORKFLOW)
        limpo = _sem_comentarios(bruto)
        self.assertIn('social_scrap.py', bruto)      # a prosa fala dele
        ramo = limpo[limpo.index('janela|janela-perfis'):]
        self.assertNotIn('social_scrap.py', ramo[:ramo.index(';;')])


# ══════════════════════════════════════════════════════════════════════════
# RT21–RT28 · E O CAMINHO CORRE MESMO — NÃO SÓ NA ÁRVORE
# ══════════════════════════════════════════════════════════════════════════
class OCaminhoCorreMesmo(unittest.TestCase):
    """⚠️ ESTA CLASSE NASCEU DE SEIS MUTANTES QUE SOBREVIVERAM.

    As sentinelas acima leem a ÁRVORE, e a árvore não sabe se o caminho anda.
    Tirar o executor do registo, deixar o adapter cunhar a própria corrida,
    repor a heurística, mandar o item original à admissão — nenhuma delas mudava
    uma linha que as sondas de estrutura olhassem, e todas partiam o fluxo.

        LER A ÁRVORE PROVA QUE A PEÇA EXISTE.
        SÓ CORRER PROVA QUE A ARESTA EXISTE.

    Por isso esta corre o caminho inteiro, numa cópia da árvore, com UM ficheiro
    falso: o cliente do navegador.
    """

    @classmethod
    def setUpClass(cls):
        import shutil
        import tempfile
        sys.path.insert(0, os.path.join(RAIZ, 'provas'))
        import o_fluxo_canonico_do_scrap as prova
        cls.prova = prova
        cls.base = tempfile.mkdtemp(prefix='flow01-t-')
        cls.arvore = os.path.join(cls.base, 'arvore')
        os.makedirs(cls.arvore)
        prova.arvore_com_o_falso(cls.arvore)
        cls.recibo, cls.env, cls.idas = prova.correr_fluxo(cls.arvore, FONTE)
        cls.recibo0, cls.env0, _ = prova.correr_fluxo(cls.arvore, None)
        cls._shutil = shutil

    @classmethod
    def tearDownClass(cls):
        cls._shutil.rmtree(cls.base, ignore_errors=True)

    def test_rt21_a_corrida_atravessa_o_orquestrador_ate_ao_fim(self):
        self.assertEqual(self.recibo.get('STATUS'), 'SUCCESS', self.recibo)
        self.assertEqual(self.recibo.get('ACTOR'), 'coleta/scrap_colheita.py')

    def test_rt22_o_run_id_tem_um_dono_so(self):
        """RUN != PROVIDER RUN. E o canônico nasce no orquestrador."""
        self.assertTrue(self.recibo.get('RUN_ID'))
        self.assertEqual(self.env.get('RUN_ID'), self.recibo.get('RUN_ID'),
                         'o adapter cunhou uma segunda corrida')

    def test_rt23_o_cliente_do_mundo_foi_chamado_e_era_falso(self):
        self.assertTrue(self.idas, 'o executor nunca chegou ao cliente')

    def test_rt24_a_colheita_declarada_atravessa_o_ingresso(self):
        self.assertGreater(len(self.env.get('COLHEITA') or []), 0)
        self.assertEqual(self.recibo.get('COLHEITA_ENCONTRADA'),
                         len(self.env['COLHEITA']))
        ing = self.recibo.get('INGRESSO') or {}
        self.assertGreater(ing.get('PRESERVADOS') or 0, 0, ing)

    def test_rt25_a_admissao_recebeu_o_item_que_saiu_do_ingresso(self):
        """O estágio atravessa a fronteira, ou a porta não aconteceu."""
        adm = self.recibo.get('ADMISSAO') or {}
        self.assertTrue(adm, 'a admissão não correu')
        self.assertEqual(adm.get('itens'), len(self.env['COLHEITA']))
        # ⚠️ O TAMANHO NÃO CHEGA: a lista original e a que saiu da porta têm o
        # mesmo tamanho e o mesmo aspecto. O que as separa é o carimbo.
        #
        # O carimbo mudou de sitio, e nao de existencia. Ele vivia num segundo
        # balde (`ENTRADOS` -> `COM_CARIMBO_DA_PORTA`), que era uma segunda
        # porta; agora viaja na unidade CANONICA, que e a unica que chega a
        # quem julga. Cobra-se no sitio onde ele esta.
        unidades = (self.recibo.get('INGRESSO') or {}).get('PARA_A_PORTA') or []
        self.assertEqual(len(unidades), adm.get('itens'),
                         'a admissão julgou uma lista que não é a da porta')
        self.assertTrue(all(u.get('ARTIFACT_ID') for u in unidades),
                        'a unidade chegou a quem julga SEM o que a porta '
                        'provou sobre ela — a porta não aconteceu')
        self.assertTrue(adm.get('por_resultado'), adm)

    def test_rt26_o_suporte_nunca_atravessou(self):
        especies = {u.get('ESPECIE') for u in (self.env.get('SUPORTE') or [])}
        self.assertIn(rc.RUN_RECEIPT, especies)
        self.assertEqual(self.recibo.get('COLHEITA_ENCONTRADA'),
                         len(self.env['COLHEITA']),
                         'suporte entrou na conta da colheita')

    def test_rt27_sem_fonte_nao_ha_colheita_e_o_porque_fica_escrito(self):
        self.assertEqual(len(self.env0.get('COLHEITA') or []), 0)
        self.assertTrue(self.env0.get('PORQUE_ZERO_COLHEITA'))
        self.assertFalse(self.recibo0.get('COLHEITA_ENCONTRADA'))

    def test_rt28_o_envelope_que_quebra_o_contrato_nao_entrega(self):
        """Um envelope com colheita sem fonte provada NÃO passa."""
        mau = dict(self.env, COLHEITA=[{'ESPECIE': rc.COLHEITA,
                                        'SOURCE_ID': '', 'DOCUMENT_ID': '',
                                        'PAYLOAD': {'ONDE': '',
                                                    'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}}])
        self.assertTrue(rc.conferir(mau, RAIZ))
        # ⚠️ A LEI E A MESMA; A MORADA E QUE MUDOU.
        # O envelope passou a viver numa pasta POR CORRIDA, e a fixture
        # escrevia no sitio antigo. O leitor resolvia para a pasta da corrida,
        # encontrava o envelope BOM, e o caso mau nunca chegava a ser lido —
        # a sentinela passava a guardar outra coisa sem dizer nada.
        #
        #     UMA FIXTURE NA MORADA ERRADA NAO TESTA O CASO MAU:
        #     TESTA O CASO BOM, COM O NOME DO MAU.
        e = dict(_executor_da_fase('janela-perfis'),
                 retorno={'ENVELOPE': 'data/colheita/scrap/ENVELOPE.json'})
        caminho = os.path.join(self.arvore, rc.endereco_do_envelope(
            'data/colheita/scrap/ENVELOPE.json', self.env['RUN_ID']))
        original = None
        if os.path.isfile(caminho):
            with io.open(caminho, encoding='utf-8') as f:
                original = f.read()
        try:
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with io.open(caminho, 'w', encoding='utf-8') as f:
                f.write(json.dumps(mau, ensure_ascii=False))
            antes, orq.RAIZ = orq.RAIZ, __import__('pathlib').Path(self.arvore)
            try:
                itens, notas = orq.a_colheita(e, self.env['RUN_ID'])
            finally:
                orq.RAIZ = antes
            self.assertEqual(itens, [], 'um envelope inválido entregou itens')
                # ⚠️ A RECUSA E A MESMA; A PALAVRA MUDOU.
            # Esta linha prendia o literal `CONTRATO`. A recusa canonica desta
            # arvore diz `ENVELOPE_INVALIDO`, e diz mais do que dizia: nomeia o
            # campo em falta e o porque. Prender a palavra faria a sentinela
            # reprovar uma recusa MELHOR do que a que ela foi escrita para exigir.
            #
            #     UMA GUARDA QUE PRENDE A PALAVRA REPROVA A MELHORIA.
            #     O QUE SE COBRA E QUE A RECUSA SEJA DITA, E COM MOTIVO.
            #
            # O que nao se afrouxa: a nota tem de NOMEAR o que faltou. Uma recusa
            # sem motivo continua a reprovar aqui.
            self.assertTrue(notas.strip(), 'a recusa foi silenciosa')
            self.assertIn('SOURCE_ID', notas,
                          'a recusa nao diz o que faltou')
        finally:
            if original is not None:
                with io.open(caminho, 'w', encoding='utf-8') as f:
                    f.write(original)


class APonteDoTextoTemQuemAGuarde(unittest.TestCase):
    """A LINHA QUE ESTA INTEGRACAO EXISTE PARA ATERRAR, E QUE NINGUEM VIGIAVA.

    ⚠️ ESTA CLASSE NASCEU DE UM SOBREVIVENTE DO RED TEAM. Dois ataques
    cortaram a ponte do texto no adapter do SCRAP — um pondo `[]` no lugar
    dela, outro trocando-a por um `fora['texto'] = objeto.get('TEXT')` cru — e
    NENHUM teste desta arvore reprovou.

        A LINHA MAIS IMPORTANTE DE UMA INTEGRACAO PODE SER TAMBEM
        A MENOS VIGIADA: ELA E NOVA, E O QUE E NOVO AINDA NAO TEM INIMIGOS.

    O segundo ataque e o perigoso, e por isso ha uma asserção so para ele: o
    texto CONTINUA a chegar a porta, e por isso a admissao continua a dizer
    SIM. Nada fica vermelho. O que se perde e a ESPECIE — legenda de autor e
    fala reconhecida por maquina passam a viajar no mesmo campo,
    indistinguiveis, que e exactamente a soma que a casa proibe.

        CAPTION != TRANSCRIPT. E UM ATAQUE QUE NAO PINTA NADA DE VERMELHO
        E O UNICO QUE CHEGA A PRODUCAO.
    """

    ADAPTER = 'coleta/scrap_colheita.py'

    def _unidade(self):
        no = _funcao(self.ADAPTER, 'unidade')
        self.assertIsNotNone(no, 'o mapeador `unidade` desapareceu do adapter')
        return no

    def test_a_ponte_chama_o_DONO_do_vocabulario_do_texto(self):
        """E chama-o pelo nome dele, e nao por uma copia local da regra."""
        corpo = ast.unparse(self._unidade())
        self.assertIn('unidades_do_envelope', corpo,
                      'o adapter deixou de chamar o dono das unidades de '
                      'texto (`regras/proveniencia.py`). TRADUZIR NOME E '
                      'FORMA E TRABALHO DE ADAPTER; DECIDIR O QUE O TEXTO E, '
                      'NAO E.')
        self.assertIn('CAMPO_DAS_UNIDADES', corpo,
                      'o campo canonico do texto deixou de ser escrito')

    def test_o_adapter_nao_decide_a_especie_por_conta_propria(self):
        """Nenhuma palavra do vocabulario do texto nasce dentro do adapter.

        Reescrever `NATIVE_CAPTION` aqui seria um SEGUNDO dono da mesma lei —
        e dois donos divergem no dia em que alguem acrescentar a quinta
        especie a um deles.
        """
        fonte = io.open(os.path.join(RAIZ, self.ADAPTER),
                        encoding='utf-8').read()
        arvore = ast.parse(fonte)
        literais = {n.value for n in ast.walk(arvore)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        for palavra in ('NATIVE_CAPTION', 'AUTHOR_TEXT', 'TRANSCRIPT', 'ASR',
                        'ORIGINAL', 'TRANSLATED'):
            self.assertNotIn(
                palavra, literais,
                'o adapter escreveu `%s` a mao: o vocabulario do texto tem UM '
                'dono, e e `regras/proveniencia.py`.' % palavra)

    def test_o_texto_nao_atravessa_por_fora_do_contrato(self):
        """O atalho cru — `fora['texto'] = ...` — nao volta.

        Ele funciona, e e esse o problema: o texto chega, a porta diz SIM, e a
        especie fica para tras sem ninguem reparar.
        """
        for no in ast.walk(self._unidade()):
            if not isinstance(no, ast.Assign):
                continue
            for alvo in no.targets:
                if (isinstance(alvo, ast.Subscript)
                        and isinstance(alvo.slice, ast.Constant)
                        and str(alvo.slice.value).lower() in
                        ('texto', 'text', 'texto_especie', 'texto_lingua')):
                    self.fail(
                        'o adapter voltou a escrever o texto a mao (%s). A '
                        'travessia do texto e do contrato, e a escolha de qual '
                        'texto vai a porta e de `ingresso.para_a_porta`.'
                        % ast.unparse(no))

    def test_a_unidade_que_sai_traz_as_unidades_de_texto(self):
        """E a prova de comportamento, e nao so de forma.

        As duas de cima leem codigo; esta corre o mapeador com um envelope que
        DECLARA especie, e exige que ela chegue inteira do outro lado. Uma
        prova de forma sozinha cai no dia em que a forma mudar e a lei ficar.
        """
        import proveniencia as pv
        import scrap_colheita as sc
        objeto = {
            'PLATFORM': 'INSTAGRAM', 'NATIVE_ID': 'X1',
            'URL': 'https://exemplo.invalido/p/X1/',
            'CONTENT_TYPE': 'POST', 'TEXT': 'uma legenda',
            'TEXT_UNITS': [{
                'TEXT_UNIT_ID': 'TU-1', 'TEXT': 'uma legenda',
                'TEXT_KIND': 'NATIVE_CAPTION',
                'TEXT_KIND_BASIS': 'DECLARED_BY_PROVIDER',
                'TEXT_RELATION': 'ORIGINAL', 'LANGUAGE': 'it',
                'TRANSLATED_FROM_TEXT_UNIT_ID': None,
                'LINEAGE': {'RAW_OBSERVATION_ID': 'UNKNOWN',
                            'SOURCE_ARTIFACT': 'https://exemplo.invalido/p/X1/',
                            'DERIVATION_METHOD': 'UNKNOWN',
                            'TOOL': 'UNKNOWN', 'MODEL': 'UNKNOWN'}}],
        }
        fora = sc.unidade(objeto, run_id='RUN-TESTE', fonte='IT-T9-001')
        unidades = fora.get(pv.CAMPO_DAS_UNIDADES) or []
        self.assertEqual(1, len(unidades),
                         'a unidade de texto nao atravessou o adapter')
        u = unidades[0]
        self.assertEqual('NATIVE_CAPTION', u.get('TEXT_KIND'),
                         'a ESPECIE declarada perdeu-se na travessia')
        self.assertEqual('ORIGINAL', u.get('TEXT_RELATION'),
                         'a RELACAO declarada perdeu-se na travessia')
        self.assertEqual('it', u.get('LANGUAGE'),
                         'a LINGUA declarada perdeu-se na travessia')

    def test_o_desconhecido_atravessa_desconhecido(self):
        """E a outra metade: o que ninguem declarou nao sobe de categoria.

        Sem esta, a de cima passaria numa implementacao que carimbasse
        `NATIVE_CAPTION` em tudo — e isso seria pior do que perder a especie.

            AUSENCIA PROMOVIDA A DECLARACAO E UMA MENTIRA COM FORMA DE DADO.
        """
        import proveniencia as pv
        import scrap_colheita as sc
        fora = sc.unidade({'PLATFORM': 'INSTAGRAM', 'NATIVE_ID': 'X2',
                           'URL': 'https://exemplo.invalido/p/X2/',
                           'CONTENT_TYPE': 'POST', 'TEXT': 'sem especie',
                           'LANGUAGE': 'it'},
                          run_id='RUN-TESTE', fonte='IT-T9-001')
        u = (fora.get(pv.CAMPO_DAS_UNIDADES) or [{}])[0]
        self.assertEqual(pv.TEXTO_DESCONHECIDO, u.get('TEXT_KIND'))
        self.assertEqual(pv.NOT_DECLARED, u.get('TEXT_KIND_BASIS'))
        # E A LINGUA DA PUBLICACAO NAO E A LINGUA DO TEXTO: o envelope declara
        # `LANGUAGE: it` para a OBSERVACAO, e isso nao diz nada sobre a lingua
        # daquele texto. O E7 tem sentinela propria para esta lei; aqui cobra-se
        # que a travessia do SCRAP nao a contorne.
        self.assertEqual(pv.TEXTO_DESCONHECIDO, u.get('LANGUAGE'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
