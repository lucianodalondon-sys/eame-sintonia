#!/usr/bin/env python3
"""
A integração do YouTube com o checkpoint CANÔNICO, provada contra a migration 016.

Roda contra um Postgres DESCARTÁVEL. Sem ele, o teste é PULADO — nunca fingido.
Aponte `BANCO_DESCARTAVEL_URL` para um banco com as migrations aplicadas.

    CHECKPOINT EXISTS != CHECKPOINT USED.
    SEEN != PERSISTED.
    PERSIST FIRST, THEN ADVANCE CHECKPOINT.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import coleta_checkpoint as cc      # noqa: E402
import youtube_oficial as yt        # noqa: E402

DSN = os.environ.get('BANCO_DESCARTAVEL_URL') or ''


@unittest.skipUnless(DSN, 'sem BANCO_DESCARTAVEL_URL — nao se finge banco')
class TestCheckpointCanonicoDeVerdade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.banco = cc.Banco(DSN)
        cls.banco.executa("delete from public.checkpoint_coleta")

    def setUp(self):
        self.banco.executa("delete from public.checkpoint_coleta")

    def _entrada(self, canal, janela):
        """A ENTRADA REAL da unidade. A janela entra: amanhã é outra unidade."""
        return {'PLATFORM': 'YOUTUBE', 'CHANNEL_ID': canal,
                'CAPABILITY': 'INCREMENTAL', 'JANELA': janela}

    def _rodar(self, canal, janela, itens, persistidos=None, explode=False):
        vistos = {'n': 0}

        def trabalho(_unidade):
            vistos['n'] += 1
            if explode:
                raise RuntimeError('a rede caiu no meio')
            return itens, 'OK'

        def persistir(its, _unidade):
            return len(its) if persistidos is None else persistidos

        r = cc.executar_unidade(
            self.banco, target='YOUTUBE/%s' % canal, entrada=self._entrada(canal, janela),
            actor='youtube-data-api-v3', platform='YOUTUBE', unidade=canal,
            trabalho=trabalho, persistir=persistir,
            campos_da_identidade=yt.CAMPOS_DA_IDENTIDADE, pais='IT')
        r['CHAMADAS_A_API'] = vistos['n']
        return r

    def _linha(self, canal):
        """(estado, feitas, persistidos, ultima_unidade), com os numeros ja em int.

        O marcador final `.` existe pela mesma razao que `pode_gastar` usa um:
        `ultima_unidade` e NULL enquanto a unidade nao avanca, e campo final vazio
        SOME no recorte do psql. Em vez de contar colunas, a consulta garante que
        a ultima nunca e vazia — a solucao ja era do dono, so foi reusada.
        """
        r = self.banco.executa(
            "select estado, unidades_feitas, itens_persistidos, "
            "coalesce(ultima_unidade,''), '.' "
            "from public.checkpoint_coleta where collection_target = %s"
            % cc._lit('YOUTUBE/%s' % canal))
        if not r:
            return None
        estado, feitas, persistidos, ultima, _m = r[0]
        return estado, int(feitas), int(persistidos), (ultima or None)

    # ── A ─────────────────────────────────────────────────────────────────
    def test_A_sem_checkpoint_a_api_nao_e_chamada(self):
        """`pode_gastar` sobre uma unidade CONCLUIDA recusa antes de gastar."""
        self._rodar('UCa', '2026-09-08', [{'id': 'v1'}])
        r = self._rodar('UCa', '2026-09-08', [{'id': 'v1'}])
        self.assertEqual(r['STATE'], cc.JA_CONCLUIDO)
        self.assertEqual(r['CHAMADAS_A_API'], 0,
                         'gastou quota numa unidade ja concluida')

    # ── B ─────────────────────────────────────────────────────────────────
    def test_B_checkpoint_aberto_permite_a_chamada(self):
        r = self._rodar('UCb', '2026-09-08', [{'id': 'v1'}, {'id': 'v2'}])
        self.assertEqual(r['STATE'], cc.UNIDADE_FEITA)
        self.assertEqual(r['CHAMADAS_A_API'], 1)
        self.assertIsNotNone(self._linha('UCb'))

    # ── C e D ─────────────────────────────────────────────────────────────
    def test_C_visto_mas_nao_persistido_nao_avanca_o_contador(self):
        """`itens_persistidos` conta o que foi SALVO, nunca o que voltou."""
        self._rodar('UCc', '2026-09-08', [{'id': 'v%d' % i} for i in range(5)],
                    persistidos=0)
        estado, feitas, persistidos, _u = self._linha('UCc')
        self.assertEqual(persistidos, 0, 'contou item que ninguem salvou')
        self.assertEqual(feitas, 1)

    def test_D_persistencia_concluida_avanca(self):
        self._rodar('UCd', '2026-09-08', [{'id': 'v1'}, {'id': 'v2'}, {'id': 'v3'}])
        estado, feitas, persistidos, ultima = self._linha('UCd')
        self.assertEqual(persistidos, 3)
        self.assertEqual(estado, 'CONCLUIDO')
        self.assertEqual(ultima, 'UCd')

    # ── E e F ─────────────────────────────────────────────────────────────
    def test_E_crash_antes_de_persistir_deixa_a_unidade_por_fazer(self):
        with self.assertRaises(RuntimeError):
            self._rodar('UCe', '2026-09-08', [{'id': 'v1'}], explode=True)
        estado, feitas, persistidos, _u = self._linha('UCe')
        self.assertEqual(feitas, 0, 'checkpoint andou sem ninguem ter salvo nada')
        self.assertEqual(persistidos, 0)
        self.assertEqual(estado, 'PARCIAL')
        # E a proxima tentativa PODE gastar — PARCIAL nao e CONCLUIDO.
        r = self._rodar('UCe', '2026-09-08', [{'id': 'v1'}])
        self.assertEqual(r['CHAMADAS_A_API'], 1, 'a unidade nao voltou a ser tentada')
        self.assertEqual(r['STATE'], cc.UNIDADE_FEITA)

    def test_F_reencontro_e_idempotente_pela_identidade(self):
        """Mesma entrada -> mesmo input_hash -> mesma linha. Nao duplica."""
        self._rodar('UCf', '2026-09-08', [{'id': 'v1'}])
        n = self.banco.executa(
            "select count(*) from public.checkpoint_coleta where collection_target=%s"
            % cc._lit('YOUTUBE/UCf'))
        self.assertEqual(int(n[0][0]), 1)

    # ── G e H ─────────────────────────────────────────────────────────────
    def test_G_mesma_unidade_nao_gasta_duas_vezes(self):
        self._rodar('UCg', '2026-09-08', [{'id': 'v1'}])
        r = self._rodar('UCg', '2026-09-08', [{'id': 'v1'}])
        self.assertEqual(r['STATE'], cc.JA_CONCLUIDO)

    def test_H_nova_janela_abre_novo_checkpoint(self):
        """O monitoramento de amanha NAO pode ficar preso no de hoje."""
        self._rodar('UCh', '2026-09-08', [{'id': 'v1'}])
        r = self._rodar('UCh', '2026-09-09', [{'id': 'v2'}])
        self.assertEqual(r['STATE'], cc.UNIDADE_FEITA,
                         'a janela nova ficou bloqueada por JA_CONCLUIDO')
        self.assertEqual(r['CHAMADAS_A_API'], 1)
        n = self.banco.executa(
            "select count(*) from public.checkpoint_coleta where collection_target=%s"
            % cc._lit('YOUTUBE/UCh'))
        self.assertEqual(int(n[0][0]), 2, 'duas janelas, dois checkpoints')

    # ── I ─────────────────────────────────────────────────────────────────
    def test_I_run_id_nao_muda_a_identidade(self):
        """RUN_ID e CAPTURED_AT nao entram na identidade — a lei ja existia."""
        ok, ruins = cc.identidade_valida(yt.CAMPOS_DA_IDENTIDADE)
        self.assertTrue(ok, ruins)
        h1 = cc.hash_da_entrada(self._entrada('UCi', '2026-09-08'))
        h2 = cc.hash_da_entrada(self._entrada('UCi', '2026-09-08'))
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, cc.hash_da_entrada(self._entrada('UCi', '2026-09-09')))

    # ── J ─────────────────────────────────────────────────────────────────
    def test_J_known_vem_do_persistido_nunca_do_visto(self):
        """`conteudo_persistido` le `public.conteudo` — linha so existe se foi salva."""
        conhecidos = cc.conteudo_persistido(self.banco, platform='YOUTUBE',
                                            external_ids=['vX', 'vY'])
        self.assertEqual(conhecidos, set(),
                         'declarou conhecido um video que ninguem salvou')

    def test_J2_a_consulta_usa_a_coluna_que_existe(self):
        """Guarda contra o defeito real: `platform` nao existe em `canal`."""
        cols = self.banco.executa(
            "select column_name from information_schema.columns "
            "where table_name='canal' and column_name in ('plataforma','platform')")
        nomes = {c[0] for c in cols}
        self.assertIn('plataforma', nomes)
        self.assertNotIn('platform', nomes,
                         'o schema mudou: reveja conteudo_persistido()')


if __name__ == '__main__':
    unittest.main(verbosity=1)
