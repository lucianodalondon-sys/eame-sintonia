#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.6C — A DURABILIDADE É DO RUNTIME COMUM, NÃO DE UM ADAPTER.

A C10.6B provou o estado durável na cadeia de Reel, e provou-o LÁ: era o
adaptador do Instagram que abria a RUN, ligava o checkpoint e passava o relator.
O censo desta missão mediu o que isso valia para o resto da casa:

    WIRED_CAPABILITIES = 13 · COM DURABILIDADE = 3 · SEM = 10

    UMA INFRAESTRUTURA COMUM NÃO É PROVADA POR UM ÚNICO ADAPTER USANDO-A.

O BOUNDARY, E POR QUE É ESTE
------------------------------
`coleta/scrap_executor.py :: COLLECT` é o ponto mais alto que (1) conhece a
execução real, (2) não inventa semântica de plataforma, (3) é por onde toda
capacidade canônica passa, (4) chama os donos em vez de os duplicar, e (5) só
escreve a etapa que ele próprio atravessa — o `CHECK`.

    NÃO SE FABRICA ETAPA. QUEM NÃO ATRAVESSOU NÃO RELATA.

O QUE FICOU DO LADO DO ADAPTER
--------------------------------
Uma coisa só, e é a única que ele podia dizer: o que é uma unidade de trabalho
da sua plataforma.

    A UNIDADE DE TRABALHO É O QUE SÓ O DONO DA PLATAFORMA SABE DIZER.
    O RESTO DA DURABILIDADE É DA CASA.

A prova com Postgres, crash cross-adapter e concorrência vive em
`provas/runtime_comum_no_postgres.py`.
"""
import ast
import inspect
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import scrap_executor as sx       # noqa: E402
import scrap_registo as reg       # noqa: E402
import coleta_checkpoint as ck    # noqa: E402
import rastro_da_coleta as rastro  # noqa: E402
import falhas as fx               # noqa: E402
import telemetria as tel          # noqa: E402

reg.carregar_adaptadores()

ADAPTERS = ('adaptador_aberto', 'adaptador_facebook', 'adaptador_instagram',
            'adaptador_linkedin', 'adaptador_x', 'adaptador_youtube')


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def _sem_prosa(arv):
    return {ast.get_docstring(n, clean=False) for n in ast.walk(arv)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                              ast.ClassDef))}


class ODonoDaDurabilidadeEUmSo(unittest.TestCase):

    def test_1_nenhum_adapter_monta_a_propria_durabilidade(self):
        """M5/M3 — um adapter que abre a própria RUN é uma segunda casa."""
        for a in ADAPTERS:
            rel = 'coleta/%s.py' % a
            if not os.path.exists(os.path.join(RAIZ, rel)):
                continue
            arv = ast.parse(_fonte(rel))
            prosa = _sem_prosa(arv)
            maus = [n.value[:44] for n in ast.walk(arv)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and n.value not in prosa
                    and any(t in n.value for t in ('collection_run',
                                                   'checkpoint_coleta',
                                                   'etapa_da_corrida'))]
            self.assertEqual(maus, [], '%s fala SQL de durabilidade: %s' % (rel, maus))
            chamadas = [n for n in ast.walk(arv) if isinstance(n, ast.Call)
                        and getattr(n.func, 'attr', None) in
                        ('abrir_corrida', 'fechar_corrida', 'executar_unidade_duravel',
                         'abrir_execucao', 'avancar_checkpoint')]
            self.assertEqual(chamadas, [],
                             '%s voltou a montar a durabilidade por conta própria' % rel)

    def test_2_o_boundary_chama_os_donos_e_nao_os_reimplementa(self):
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        prosa = _sem_prosa(arv)
        maus = [n.value[:44] for n in ast.walk(arv)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and n.value not in prosa
                and any(t in n.value for t in ('insert into', 'update public.'))]
        self.assertEqual(maus, [], 'o executor passou a escrever SQL: %s' % maus)
        self.assertIn('abrir_execucao', _fonte('coleta/scrap_executor.py'),
                      'o executor deixou de chamar o dono da durabilidade')

    def test_3_o_vocabulario_continua_com_os_donos_dele(self):
        self.assertIs(rastro.ESTADOS, tel.ESTADOS_DE_ETAPA)
        self.assertIs(rastro.ETAPAS, tel.ETAPAS_DA_COLETA)
        self.assertFalse(hasattr(sx, 'ESTADOS_DE_ETAPA'))
        self.assertFalse(hasattr(sx, 'retentavel'))


class OBoundaryNaoInventa(unittest.TestCase):

    def test_4_o_executor_so_escreve_a_etapa_que_ele_atravessa(self):
        """M11 — uma etapa que não correu aqui não pode nascer aqui."""
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'COLLECT')
        abertas = []
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call) and getattr(n.func, 'attr', None) == 'abrir'
                    and n.args and isinstance(n.args[0], ast.Constant)):
                abertas.append(n.args[0].value)
        self.assertEqual(abertas, ['CHECK'],
                         'o boundary passou a nomear etapas que não são dele: %s'
                         % abertas)

    def test_4b_a_etapa_abre_antes_do_trabalho_dela(self):
        """M2 — abrir depois e abrir quando ja nao ha nada a testemunhar.

        Uma etapa que so nasce DEPOIS de o trabalho dela acabar nao testemunha
        morte nenhuma: quem morrer la dentro nao deixa linha. E a mesma lei da
        C10.6B, aplicada ao degrau que este ficheiro possui.

            ABRIR A ETAPA ANTES DO TRABALHO.
        """
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'COLLECT')
        abre = trabalho = None
        for i, no in enumerate(fn.body):
            texto = ast.dump(no)
            if abre is None and "attr='abrir'" in texto and "'CHECK'" in texto:
                abre = i
            if trabalho is None and "id='CHECK'" in texto:
                trabalho = i
        self.assertIsNotNone(abre, 'a etapa CHECK deixou de abrir')
        self.assertIsNotNone(trabalho, 'o CHECK deixou de correr')
        self.assertLess(abre, trabalho,
                        'a etapa CHECK passou a abrir DEPOIS de o CHECK correr')

    def test_5_um_portao_que_recusa_nao_falhou(self):
        """`FAIL` diria que o CHECK rebentou. Ele respondeu."""
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'COLLECT')
        estados = []
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and getattr(n.func, 'attr', None) == 'fechar':
                for a in ast.walk(n):
                    if isinstance(a, ast.Constant) and a.value in tel.ESTADOS_DE_ETAPA:
                        estados.append(a.value)
        self.assertIn('SKIPPED', estados,
                      'a recusa do CHECK voltou a ser contada como falha')
        self.assertIn('PASS', estados)
        # e não há código de diagnóstico para CHECK — porque CHECK não falha
        import diagnostico as dg
        self.assertIsNone(dg.da_etapa('CHECK'),
                          'nasceu um código de diagnóstico para uma etapa que responde')

    def test_6_a_unidade_de_trabalho_vem_do_adapter(self):
        """O executor não sabe o que é uma unidade do Instagram. Ele pergunta."""
        fonte = _fonte('coleta/scrap_executor.py')
        self.assertIn("'UNIDADE'", fonte,
                      'o boundary deixou de perguntar a unidade ao adaptador')
        arv = ast.parse(fonte)
        prosa = _sem_prosa(arv)
        maus = [n.value for n in ast.walk(arv)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and n.value not in prosa
                and ('/reel/' in n.value or 'INSTAGRAM/' in n.value)]
        self.assertEqual(maus, [],
                         'o executor passou a saber o nome da unidade de uma '
                         'plataforma: %s' % maus)

    def test_7_sem_banco_nada_muda(self):
        sig = inspect.signature(sx.COLLECT)
        self.assertIn('banco', sig.parameters)
        self.assertIsNone(sig.parameters['banco'].default,
                          'o executor passou a EXIGIR banco')


class OQueCadaCapacidadeDECLARA(unittest.TestCase):

    def test_8_so_quem_tem_unidade_retomavel_a_declara(self):
        """Fabricar checkpoint onde não há metade feita tranca a porta."""
        com, sem = [], []
        for (plat, capac), r in reg.registados().items():
            if not (r['EXECUTA'] or r['ROTA']):
                continue
            (com if r.get('UNIDADE') else sem).append('%s/%s' % (plat, capac))
        self.assertTrue(com, 'nenhuma capacidade declara unidade de trabalho')
        self.assertTrue(sem, 'TODAS declaram \u2014 e isso seria fabricar retomada')
        for x in com:
            self.assertTrue(x.startswith('INSTAGRAM/'),
                            'uma capacidade fora do Instagram passou a declarar '
                            'unidade sem que esta prova soubesse: %s' % x)

    def test_8b_quem_nao_tem_rota_nao_declara_unidade(self):
        """M10 — declarar unidade para capacidade sem rota e contar MODULE como FLOW.

        Um checkpoint para uma capacidade que nao corre e uma unidade de
        trabalho que ninguem vai fazer — e ela ficaria `ABERTO` para sempre,
        a dizer que ha trabalho em curso onde nao ha trabalho nenhum.

            DECLARED CAPABILITY != WIRED CAPABILITY != OBSERVED FLOW.
        """
        maus = []
        for (plat, capac), r in reg.registados().items():
            if r.get('UNIDADE') and not (r['EXECUTA'] or r['ROTA']):
                maus.append('%s/%s' % (plat, capac))
        self.assertEqual(maus, [],
                         'capacidade sem rota a declarar unidade de trabalho: %s'
                         % maus)

    def test_9_a_unidade_declarada_e_valida_para_o_dono_da_identidade(self):
        import adaptador_instagram as ad
        alvo, entrada, campos = ad.unidade_do_pedido(
            ident={'PLATFORM': 'INSTAGRAM', 'POST_ID': 'ABC'})
        self.assertEqual(alvo, 'INSTAGRAM/reel/ABC')
        ok, ruins = ck.identidade_valida(campos)
        self.assertTrue(ok, 'a unidade declarada tem campo proibido: %s' % ruins)
        self.assertNotIn('RUN_ID', entrada)

    def test_10_a_mesma_unidade_para_as_tres_capacidades_do_reel(self):
        """`capture`, `audio` e `transcribe` são pedidos sobre O MESMO Reel."""
        unidades = set()
        for c in ('instagram.reel.capture', 'instagram.reel.audio',
                  'instagram.reel.transcribe'):
            r = reg.adaptador_de('INSTAGRAM', c)
            self.assertIsNotNone(r.get('UNIDADE'), '%s não declara unidade' % c)
            alvo, _e, _ca = r['UNIDADE'](ident={'PLATFORM': 'INSTAGRAM',
                                                'POST_ID': 'X'})
            unidades.add(alvo)
        self.assertEqual(unidades, {'INSTAGRAM/reel/X'},
                         'as três capacidades deixaram de ver o mesmo Reel')


class OVereditoSobePelaLinguaDoDono(unittest.TestCase):

    def test_11_o_executor_recusa_palavra_que_falhas_nao_declara(self):
        with self.assertRaises(ValueError):
            sx._estado_da_corrida([1], {'CANONICAL_STATE': 'INVENTADO'}, ck)

    def test_12_zero_resultados_nao_e_falha_nem_sucesso_cheio(self):
        self.assertEqual(sx._estado_da_corrida([], {'CANONICAL_STATE': 'ZERO_RESULTS'},
                                               ck), ck.CORRIDA_VAZIA)
        self.assertEqual(sx._estado_da_corrida([1], {'CANONICAL_STATE': 'ITEM_ERROR'},
                                               ck), ck.CORRIDA_PARCIAL)
        self.assertFalse(fx.e_falha('ZERO_RESULTS'))

    def test_13_o_aceita_mede_a_assinatura_e_nao_supoe(self):
        def com(**kw):
            return None

        def sem(a, b=1):
            return None

        def explicita(a, etapa=None):
            return None
        self.assertTrue(sx._aceita(com, 'etapa'))
        self.assertFalse(sx._aceita(sem, 'etapa'))
        self.assertTrue(sx._aceita(explicita, 'etapa'))


class UmaExcecaoNuncaFechaComoSucesso(unittest.TestCase):
    """M4 — o pior fim possivel: a corrida rebenta e o banco diz que correu bem."""

    def test_15_o_ramo_de_excecao_fecha_em_falhou(self):
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'COLLECT')
        handlers = [h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)]
        self.assertTrue(handlers, 'o boundary deixou de apanhar a excecao')
        estados = []
        for h in handlers:
            for n in ast.walk(h):
                # SO `execucao.fechar(...)` — `relator.fechar(...)` fecha ETAPA,
                # que e outra coisa e tem outro vocabulario.
                if (isinstance(n, ast.Call)
                        and getattr(n.func, 'attr', None) == 'fechar'
                        and getattr(n.func.value, 'id', None) == 'execucao'
                        and n.args):
                    a = n.args[0]
                    estados.append(getattr(a, 'attr', None)
                                   or getattr(a, 'id', None)
                                   or getattr(a, 'value', None))
        self.assertTrue(estados, 'a excecao deixou de fechar a corrida')
        for e in estados:
            self.assertEqual(e, 'CORRIDA_FALHOU',
                             'uma excecao passou a fechar a corrida como %r' % e)
        # e a etapa aberta tambem fecha: quem esta VIVO nao deixa linha pendurada
        self.assertIn('abertas', ast.dump(handlers[0]),
                      'a excecao deixou de fechar as etapas que estavam abertas')


class NadaDeRelevanciaEntrouNoSCRAP(unittest.TestCase):
    """COLETAR != ADMITIR != JULGAR — e o executor faz o primeiro.

    ⚠️ ESTA SENTINELA MUDOU DE FORMA NA SCRAP-SR-02, E A RAZAO FICA ESCRITA.

    Ela lia o ficheiro INTEIRO a procura da palavra «relevancia», e apanhou um
    COMENTARIO — a frase que explica por que o modo desce ate ao dono da compra,
    e que diz, precisamente, que quem julga relevancia NAO e este ficheiro.

        UMA SONDA QUE LE A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA
        E CHAMA-LHE VIOLACAO DA REGRA.

    Passou a medir duas coisas mais fortes do que a palavra:

        1. o CODIGO, sem comentarios nem docstrings — onde um nome proibido
           so aparece se alguem o tiver escrito a serio;
        2. a ARVORE — nenhum import nem chamada ao dono da relevancia.

    A segunda e a que vale: proibir a palavra nunca impediu ninguem de escrever
    `import relevancia_da_fonte as r` e chamar `r.portao()`.
    """

    #: O dono de SOURCE_RELEVANCE vive noutra linhagem (SR-01). O executor nao
    #: o importa, nao o chama, e nao o reimplementa.
    DONOS_DA_RELEVANCIA = ('relevancia_da_fonte', 'admissao', 'adama_relevance')

    def _so_codigo(self, fonte):
        """→ a fonte SEM comentarios nem docstrings."""
        import io as _io
        import tokenize
        fora, anterior = [], tokenize.INDENT
        for tok in tokenize.generate_tokens(_io.StringIO(fonte).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if (tok.type == tokenize.STRING
                    and anterior in (tokenize.INDENT, tokenize.NEWLINE,
                                     tokenize.NL, tokenize.DEDENT)):
                continue        # docstring: a unica string que nasce sozinha
            if tok.type not in (tokenize.NL, tokenize.NEWLINE):
                anterior = tok.type
            fora.append(tok.string)
        return '\n'.join(fora)

    def test_14_o_boundary_nao_julga_o_item(self):
        codigo = self._so_codigo(_fonte('coleta/scrap_executor.py'))
        for proibido in ('SOURCE_SCORE', 'ITEM_RELEVANCE', 'T3_SCORE', 'T5_SCORE',
                         'T9_SCORE', 'relevancia'):
            self.assertNotIn(proibido, codigo,
                             'entrou julgamento tematico no executor: %s' % proibido)

    def test_14b_o_boundary_nao_importa_nem_chama_o_dono_da_relevancia(self):
        """Proibir a palavra nao impede o import. Esta le a ARVORE."""
        arv = ast.parse(_fonte('coleta/scrap_executor.py'))
        for no in ast.walk(arv):
            if isinstance(no, (ast.Import, ast.ImportFrom)):
                nomes = ([a.name for a in no.names] if isinstance(no, ast.Import)
                         else [no.module or ''])
                for m in nomes:
                    base = (m or '').split('.')[0]
                    self.assertNotIn(base, self.DONOS_DA_RELEVANCIA,
                                     'o executor importou o dono da relevancia: %s' % m)
            if isinstance(no, ast.Call):
                alvo = no.func
                nome = (alvo.attr if isinstance(alvo, ast.Attribute)
                        else getattr(alvo, 'id', None))
                self.assertNotIn(nome, ('portao', 'classificar', 'ler_livro',
                                        'estado_da_relevancia'),
                                 'o executor passou a julgar relevancia: %s' % nome)


if __name__ == '__main__':
    unittest.main(verbosity=2)
