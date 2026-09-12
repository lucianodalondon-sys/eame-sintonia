#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.6B — O RUN SOBREVIVE AO PROCESSO.

A C10.6 provou que a cadeia de Reel aguenta um `os._exit()`: o RAW preservado é
reusado, o retry consulta `leis/falhas.py`, o parcial não é publicado. Ficou
`PARTIAL` por um motivo só:

    RUN_STATE_PERSISTENCE = NOT_IMPLEMENTED

O processo seguinte sabia ler a GAVETA. E uma gaveta diz o que EXISTE, nunca o
que ACONTECEU.

    UM FICHEIRO NO DISCO É UM RESULTADO. NÃO É UMA EXECUÇÃO.

TRÊS GRÃOS, TRÊS DONOS
------------------------
    RUN         `public.collection_run`     UMA execução de um ator
    CHECKPOINT  `public.checkpoint_coleta`  a UNIDADE DE TRABALHO
    RASTRO      `public.etapa_da_corrida`   uma passagem de etapa numa tentativa

A migration 016 escreve a relação: «o checkpoint é a UNIDADE DE TRABALHO, e ela
pode atravessar várias execuções. Por isso collection_run aponta para cá, e não
o contrário.»

    RUN != CHECKPOINT.  UM CHECKPOINT, VÁRIAS RUNS.

ESTES TESTES SÃO DE CONTRATO, NÃO DE BANCO
--------------------------------------------
A prova com Postgres real, crash real e processo novo corre em
`provas/run_duravel_no_postgres.py` e está no `banco-descartavel`. O que fica
aqui é o que se pode medir sem banco: a forma do contrato, os donos, as travas —
e a garantia de que a cadeia continua a correr SEM instrumentação nenhuma.
"""
import ast
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import coleta_checkpoint as ck      # noqa: E402
import rastro_da_coleta as rastro   # noqa: E402
import telemetria as tel            # noqa: E402
import falhas as fx                 # noqa: E402
import reel_transcricao as rt       # noqa: E402
import adaptador_instagram as ad    # noqa: E402


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


class OsDonosNaoSeMisturam(unittest.TestCase):
    """FASE 1 — três conceitos, três donos, e nenhum segundo dono novo."""

    def test_1_o_dono_do_rastro_e_quem_escreve_etapa_da_corrida(self):
        # O checkpoint CHAMA o dono do rastro; não escreve `etapa_da_corrida`.
        fonte = _fonte('coleta/coleta_checkpoint.py')
        arv = ast.parse(fonte)
        prosa = {ast.get_docstring(n, clean=False) for n in ast.walk(arv)
                 if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))}
        sql = [n.value for n in ast.walk(arv)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)
               and 'etapa_da_corrida' in n.value and n.value not in prosa]
        self.assertEqual(sql, [], 'o dono do checkpoint passou a escrever SQL do '
                                  'rastro: %s' % sql)
        # e o dono do rastro escreve mesmo
        self.assertIn('public.etapa_da_corrida', _fonte('medidas/rastro_da_coleta.py'))

    def test_2_o_reel_nao_escreve_sql_nenhum(self):
        for rel in ('ferramentas/reel_transcricao.py', 'coleta/adaptador_instagram.py'):
            arv = ast.parse(_fonte(rel))
            prosa = {ast.get_docstring(n, clean=False) for n in ast.walk(arv)
                     if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))}
            maus = [n.value for n in ast.walk(arv)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and n.value not in prosa
                    and any(t in n.value for t in ('checkpoint_coleta',
                                                   'collection_run',
                                                   'etapa_da_corrida'))]
            self.assertEqual(maus, [], '%s passou a falar SQL com o banco: %s'
                                       % (rel, maus))

    def test_3_nao_nasceu_checkpoint_paralelo(self):
        """A proibição principal: nenhum state JSON, nenhum sqlite, nenhum v2."""
        proibidos = ('scrap_checkpoint.json', 'scrap_state.json', 'run_state.json',
                     'checkpoint_v2.py', 'scrap_checkpoint.py', 'reel_checkpoint.py')
        achados = []
        for raiz, dirs, fich in os.walk(RAIZ):
            dirs[:] = [d for d in dirs if d not in
                       ('node_modules', '.git', '__pycache__', 'BASELINE', 'data')]
            for f in fich:
                if f in proibidos:
                    achados.append(os.path.relpath(os.path.join(raiz, f), RAIZ))
        self.assertEqual(achados, [], 'nasceu um segundo dono durável: %s' % achados)

    def test_4_o_vocabulario_continua_a_ter_um_dono(self):
        self.assertIs(rastro.ESTADOS, tel.ESTADOS_DE_ETAPA)
        self.assertIs(rastro.ETAPAS, tel.ETAPAS_DA_COLETA)
        # e o dono da pergunta «retentar adianta?» não mudou
        self.assertTrue(hasattr(fx, 'retentavel'))
        self.assertFalse(hasattr(ck, 'retentavel'))
        self.assertFalse(hasattr(rastro, 'retentavel'))


class ACadeiaCorreSemInstrumento(unittest.TestCase):
    """Instrumentar não pode ser condição para funcionar."""

    def test_5_o_relator_mudo_responde_a_tudo(self):
        mudo = rt._SEM_RELATO
        self.assertIsNone(mudo.abrir('FETCH'))
        self.assertIsNone(mudo.fechar(None, 'PASS'))
        self.assertIsNone(ck.SEM_RELATO.abrir('RAW', input_grain='X'))

    def test_6_transcrever_reel_aceita_nao_receber_relator(self):
        import inspect
        sig = inspect.signature(rt.transcrever_reel)
        self.assertIn('etapa', sig.parameters)
        self.assertIsNone(sig.parameters['etapa'].default,
                          'o relator passou a ser obrigatório')

    def test_7_o_adaptador_so_usa_banco_quando_lhe_dao_um(self):
        import inspect
        sig = inspect.signature(ad.capturar_reel)
        self.assertIn('banco', sig.parameters)
        self.assertIsNone(sig.parameters['banco'].default)


class OContratoDaUnidadeDeTrabalho(unittest.TestCase):
    """FASE 9 — a identidade não pode conhecer a execução que a corre."""

    def test_8_a_identidade_recusa_o_que_muda_entre_execucoes(self):
        for proibido in ('RUN_ID', 'token', 'dataset_id', 'captured_at',
                         'pool_position'):
            ok, ruins = ck.identidade_valida(('PLATFORM', 'EXTERNAL_ID', proibido))
            self.assertFalse(ok, '%s entrou na identidade' % proibido)
            self.assertIn(proibido, ruins)
        ok, _ = ck.identidade_valida(ad.CAMPOS_DA_IDENTIDADE)
        self.assertTrue(ok, 'a identidade do Reel foi recusada pelo próprio dono')

    def test_9_a_unidade_de_trabalho_do_reel_e_o_reel(self):
        alvo, entrada = ad.unidade_de_trabalho(
            {'PLATFORM': 'INSTAGRAM', 'POST_ID': 'ABC123'})
        self.assertEqual(alvo, 'INSTAGRAM/reel/ABC123')
        self.assertEqual(entrada['EXTERNAL_ID'], 'ABC123')
        self.assertNotIn('RUN_ID', entrada)
        # duas execuções do mesmo reel dão o MESMO hash — é isso que faz a
        # retomada existir
        self.assertEqual(ck.hash_da_entrada(entrada),
                         ck.hash_da_entrada(dict(entrada)))


class ACorridaNaoSeFechaSozinha(unittest.TestCase):

    def test_10_rodando_nao_fecha_execucao_nenhuma(self):
        class BancoFalso:
            def __init__(self):
                self.sql = []

            def executa(self, s, *a):
                self.sql.append(s)
                return [['1']]

        b = BancoFalso()
        with self.assertRaises(ValueError):
            ck.fechar_corrida(b, run_id='R', status=ck.CORRIDA_ABERTA)
        with self.assertRaises(ValueError):
            ck.fechar_corrida(b, run_id='R', status='inventado')
        self.assertEqual(b.sql, [], 'uma recusa não pode escrever no banco')

    def test_11_a_copia_do_enum_esta_declarada_como_copia(self):
        self.assertEqual(ck.CORRIDA_ESTADOS,
                         ('rodando', 'concluida', 'vazia', 'parcial', 'falhou'))
        self.assertTrue(hasattr(ck, 'corrida_estados_do_banco'),
                        'não há como conferir a cópia contra o banco')


class ZeroResultadosNaoEErro(unittest.TestCase):
    """`ERROR != REJECTED != UNKNOWN != NOT_RUN != REUSED`."""

    def test_12_zero_results_e_um_estado_canonico(self):
        self.assertIn('ZERO_RESULTS', fx.ESTADOS)
        self.assertFalse(fx.e_falha('ZERO_RESULTS'),
                         'ouvir e não haver fala virou falha')

    def test_13_a_cadeia_fecha_derived_em_zero_results_e_nao_em_fail(self):
        arv = ast.parse(_fonte('ferramentas/reel_transcricao.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'transcrever_reel')
        texto = ast.dump(fn)
        self.assertIn("'ZERO_RESULTS'", texto,
                      'a cadeia deixou de distinguir «não havia fala» de erro')

    def test_14_reuso_nao_e_aquisicao_no_rastro(self):
        """FETCH que reusou bytes não pode contar como `passed`."""
        arv = ast.parse(_fonte('ferramentas/reel_transcricao.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'transcrever_reel')
        texto = ast.dump(fn)
        self.assertIn("'SKIPPED'", texto)
        self.assertIn('reused', texto)


class OQueACadeiaCHAMAAOSEUPROPRIOESTADO(unittest.TestCase):
    """As traduções que decidem o estado durável, medidas na árvore.

    Cada uma delas é um sítio onde uma palavra trocada faz o banco guardar
    outra história — e nenhuma dá erro ao ser trocada.
    """

    def _fn(self, rel, nome):
        arv = ast.parse(_fonte(rel))
        return next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                    and n.name == nome)

    def test_17_a_unidade_falha_quando_a_transcricao_falha(self):
        """M5 — «DERIVED existe» não pode fechar a unidade como feita."""
        fn = self._fn('coleta/adaptador_instagram.py', '_com_durabilidade')
        texto = ast.dump(fn)
        self.assertIn("'REQUESTED_EMPTY'", texto,
                      'o adaptador deixou de distinguir «não havia fala»')
        self.assertIn("'RAW'", texto,
                      'o adaptador deixou de exigir pai preservado')
        # e `falhou` tem de depender de alguma coisa — um literal fixo aqui
        # seria a unidade a fechar-se sempre do mesmo jeito
        atrib = [n for n in ast.walk(fn) if isinstance(n, ast.Assign)
                 and any(getattr(t, 'id', None) == 'falhou' for t in n.targets)]
        self.assertTrue(atrib, 'a decisão de falha sumiu do adaptador')
        for a in atrib:
            self.assertNotIsInstance(a.value, ast.Constant,
                                     'a unidade passou a ter um veredito fixo')

    def test_18_o_403_do_ytdlp_nao_e_retentavel(self):
        """M9 — o dono do retry é `leis/falhas.py`, e o mapa respeita-o."""
        for marca, esperado, retenta in (('403', 'BLOCKED', False),
                                         ('404', 'SOURCE_GONE', False),
                                         ('429', 'RATE_LIMITED', True),
                                         ('500', 'SOURCE_UNAVAILABLE', True),
                                         ('timed out', 'TRANSIENT_NETWORK_ERROR', True)):
            with self.subTest(sinal=marca):
                lido = rt.estado_do_ytdlp('ERROR: HTTP Error %s aconteceu' % marca)
                self.assertEqual(lido, esperado)
                self.assertIn(lido, fx.ESTADOS,
                              'a cadeia inventou um estado que o dono não declara')
                self.assertEqual(fx.retentavel(lido), retenta)

    def test_19_um_fetch_que_nao_trouxe_bytes_fecha_em_FAIL(self):
        """M11 — a etapa que não conseguiu nada não pode aparecer `PASS`."""
        fn = self._fn('ferramentas/reel_transcricao.py', 'transcrever_reel')
        # o ramo do FETCH sem caminho tem de fechar FAIL. Mede-se na arvore:
        # procura-se a chamada `rel.fechar(_e_fetch, ...)` cujo estado e FAIL.
        estados = []
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call)
                    and getattr(n.func, 'attr', None) == 'fechar'
                    and n.args and getattr(n.args[0], 'id', None) == '_e_fetch'):
                estados.append(n.args[1].value if isinstance(n.args[1], ast.Constant)
                               else '?')
        self.assertIn('FAIL', estados,
                      'o FETCH deixou de ter um ramo de falha: %s' % estados)
        self.assertIn('SKIPPED', estados, 'o reuso deixou de ser SKIPPED')
        self.assertIn('PASS', estados, 'a aquisicao real deixou de ser PASS')
        self.assertEqual(len(estados), 3,
                         'o FETCH passou a ter %d ramos; a lei tem tres: '
                         'reusou, foi buscar, nao conseguiu' % len(estados))

    def test_20_a_ligacao_run_checkpoint_e_escrita_e_nao_suposta(self):
        """M8 — a corrida tem de APONTAR para a unidade de onde nasceu."""
        fn = self._fn('coleta/coleta_checkpoint.py', 'executar_unidade_duravel')
        texto = ast.dump(fn)
        self.assertIn('checkpoint_id', texto,
                      'a corrida deixou de nomear o checkpoint ao nascer')
        self.assertIn('ligar_ao_checkpoint', texto,
                      'a ligacao explicita sumiu; sobra so o valor do insert, '
                      'e um insert que colida com `do nothing` nao a escreve')


class OAvancoEDeUmSo(unittest.TestCase):
    """FASE 22 — a condição e a escrita viajam na MESMA instrução."""

    def test_15_o_avanco_e_condicional(self):
        arv = ast.parse(_fonte('coleta/coleta_checkpoint.py'))
        fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
                  and n.name == 'avancar_checkpoint')
        sql = ' '.join(n.value for n in ast.walk(fn)
                       if isinstance(n, ast.Constant) and isinstance(n.value, str))
        self.assertIn("estado <> 'CONCLUIDO'", sql,
                      'o avanço deixou de ser um compare-and-set')
        self.assertIn('returning', sql,
                      'sem `returning` ninguém sabe se ganhou')

    def test_16_o_leitor_do_banco_nao_le_a_conversa_do_psql(self):
        arv = ast.parse(_fonte('coleta/coleta_checkpoint.py'))
        cls = next(n for n in ast.walk(arv) if isinstance(n, ast.ClassDef)
                   and n.name == 'Banco')
        argv = [n.value for n in ast.walk(cls)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn('-q', argv,
                      'sem `-q` o psql imprime `UPDATE 0` e o leitor devolve-o '
                      'como se fosse uma linha de resultado')


if __name__ == '__main__':
    unittest.main(verbosity=2)
