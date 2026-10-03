#!/usr/bin/env python3
"""
O CONTRATO DE PERSISTENCIA SOCIAL, provado contra um PostgreSQL 16 real.

Roda contra um Postgres DESCARTAVEL. Sem ele, o teste e PULADO — nunca fingido.
Aponte `BANCO_DESCARTAVEL_URL` para um banco com as migrations 001..016 e a 023
aplicadas.

    COMMENT_ID NAO E COMMENT_TEXT.
    REPLY NAO E TOP-LEVEL.
    SEEN NAO E PERSISTED.
    CHECKPOINT SO ANDA DEPOIS DA PROVA ESTAR GUARDADA.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401
import coleta_checkpoint as cc          # noqa: E402
import social_persistencia as sp        # noqa: E402

DSN = os.environ.get('BANCO_DESCARTAVEL_URL') or ''


def comentario(externo, texto, parent=None, autor='UCautor'):
    """Um envelope de comentario como o executor o produz."""
    return {'NATIVE_ID': externo, 'TEXT': texto, 'PUBLISHED_AT': 'UNKNOWN',
            'PLATFORM': 'YOUTUBE',
            'RAW': {'COMMENT_ID': externo, 'PARENT_ID': parent,
                    'IS_REPLY': parent is not None,
                    'AUTHOR_CHANNEL_ID': autor,
                    'AUTHOR_DISPLAY_NAME': 'Nome Visivel Que Nao Se Usa'}}


@unittest.skipUnless(DSN, 'sem BANCO_DESCARTAVEL_URL — nao se finge banco')
class BaseComCadeia(unittest.TestCase):
    """Cada teste comeca com a cadeia de identidade montada e as tabelas limpas."""

    CANAL = 'UCLqKnJJf6VBExBf5qp8N74w'

    @classmethod
    def setUpClass(cls):
        cls.banco = cc.Banco(DSN)

    @classmethod
    def tearDownClass(cls):
        """⚠️ LIMPAR AO ENTRAR NAO E LIMPAR AO SAIR.

        Esta suite montava a cadeia de identidade no `setUp` e nunca a desfazia.
        Quem corresse a seguir encontrava `organizacao`, `origem` e `canal` que
        nao eram seus — e `provas/a_autoridade_da_fonte.py` (AU8), que mede que
        MEDIR a autoridade nao escreve identidade nenhuma, dava FAIL por lixo
        alheio.

            TEST PASSES ALONE != TEST IS SAFE.

        A ordem e a das dependencias, e nao a alfabetica.
        """
        for sql in (
            "delete from public.comentario",
            "delete from public.conteudo_visto_em",
            "delete from public.conteudo",
            "delete from public.checkpoint_coleta",
            "delete from public.canal where channel_id = '%s'" % cls.CANAL,
            "delete from public.origem where rotulo = 'ORIGEM-DE-TESTE'",
            "delete from public.organizacao where nome_canonico = 'ORG-DE-TESTE'",
            "delete from public.collection_run where run_id like 'RUN-%'",
        ):
            try:
                cls.banco.executa(sql)
            except Exception:                                # noqa: BLE001
                pass

    def setUp(self):
        b = self.banco
        b.executa("delete from public.comentario")
        b.executa("delete from public.conteudo_visto_em")
        b.executa("delete from public.conteudo")
        b.executa("delete from public.checkpoint_coleta")
        b.executa("delete from public.canal")
        b.executa("delete from public.origem")
        b.executa("delete from public.organizacao")
        b.executa("delete from public.collection_run")
        b.executa("insert into public.organizacao (nome_canonico) values ('ORG-DE-TESTE')")
        b.executa("insert into public.origem (rotulo, organizacao_id) select 'ORIGEM-DE-TESTE', id"
                  " from public.organizacao where nome_canonico='ORG-DE-TESTE'")
        b.executa("insert into public.canal (origem_id, plataforma, channel_id, tipo_de_perfil)"
                  " select id, 'youtube', '%s', 'NOT_KNOWN' from public.origem"
                  " where rotulo='ORIGEM-DE-TESTE'" % self.CANAL)
        self._run('RUN-1')
        self.canal_id = sp.canal_canonico(b, platform='YOUTUBE', channel_id=self.CANAL)

    def _run(self, run_id):
        self.banco.executa(
            "insert into public.collection_run (run_id, platform, source_country,"
            " started_at, status, rule_version) values ('%s','YOUTUBE','IT',now(),"
            "'rodando','v1') on conflict do nothing" % run_id)

    def _video(self, content_id='ezRyN8vLVvc', run_id='RUN-1'):
        return sp.persistir_video(self.banco, canal_id=self.canal_id, run_id=run_id,
                                  content_id=content_id, texto_canonico='titulo|desc',
                                  raw_durou=True)


# ═══════════════════════════════════════════════════════════════════════════
# C1..C5 — A IDENTIDADE DO COMENTARIO
# ═══════════════════════════════════════════════════════════════════════════
class IdentidadeDoComentario(BaseComCadeia):

    def test_C1_dois_grazie_com_ids_diferentes_sao_dois(self):
        v = self._video()
        r = sp.persistir_comentarios(
            self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
            comentarios=[comentario('COMMENT-A', 'Grazie!', autor='UCum'),
                         comentario('COMMENT-B', 'Grazie!', autor='UCoutro')])
        self.assertEqual(r['INSERIDOS'], 2, 'duas pessoas foram colapsadas numa')
        n = self.banco.executa("select count(*) from public.comentario")[0][0]
        self.assertEqual(int(n), 2)

    def test_C2_mesmo_id_reencontrado_nao_duplica(self):
        v = self._video()
        for _ in range(2):
            r = sp.persistir_comentarios(
                self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
                comentarios=[comentario('COMMENT-A', 'Grazie!')])
        self.assertEqual(r['JA_EXISTIAM'], 1)
        n = self.banco.executa("select count(*) from public.comentario")[0][0]
        self.assertEqual(int(n), 1)

    def test_C3_texto_divergente_no_mesmo_id_nao_sobrescreve_em_silencio(self):
        v = self._video()
        sp.persistir_comentarios(self.banco, conteudo_id=v['CONTEUDO_ID'],
                                 run_id='RUN-1',
                                 comentarios=[comentario('COMMENT-A', 'Grazie!')])
        r = sp.persistir_comentarios(self.banco, conteudo_id=v['CONTEUDO_ID'],
                                     run_id='RUN-1',
                                     comentarios=[comentario('COMMENT-A', 'Grazie mille!')])
        self.assertEqual(len(r['TEXTO_DIVERGIU']), 1, 'a divergencia passou calada')
        self.assertEqual(r['TEXTO_DIVERGIU'][0]['STATE'], sp.TEXTO_DIVERGIU)
        guardado = self.banco.executa(
            "select texto from public.comentario where externo_id='COMMENT-A'")[0][0]
        self.assertEqual(guardado, 'Grazie!', 'sobrescreveu sem ninguem decidir')

    def test_C4_id_diferente_com_hash_igual_coexistem(self):
        v = self._video()
        sp.persistir_comentarios(
            self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
            comentarios=[comentario('COMMENT-A', 'Grazie!'),
                         comentario('COMMENT-B', 'Grazie!')])
        linhas = self.banco.executa(
            "select count(distinct externo_id), count(distinct hash_conteudo)"
            " from public.comentario")
        self.assertEqual(linhas[0][0], '2', 'dois IDs')
        self.assertEqual(linhas[0][1], '1', 'um hash — e mesmo assim duas linhas')

    def test_C5_hash_conteudo_continua_sendo_hash_do_texto(self):
        v = self._video()
        sp.persistir_comentarios(self.banco, conteudo_id=v['CONTEUDO_ID'],
                                 run_id='RUN-1',
                                 comentarios=[comentario('COMMENT-A', 'Grazie!')])
        do_banco = self.banco.executa(
            "select hash_conteudo, encode(sha256('Grazie!'), 'hex')"
            " from public.comentario where externo_id='COMMENT-A'")[0]
        self.assertEqual(do_banco[0], do_banco[1],
                         'o hash deixou de ser o hash do texto')
        self.assertNotIn('COMMENT-A', do_banco[0])


# ═══════════════════════════════════════════════════════════════════════════
# P1..P5 — A THREAD DENTRO DO BANCO
# ═══════════════════════════════════════════════════════════════════════════
class ThreadNoBanco(BaseComCadeia):

    def test_P1_top_level_tem_pai_nulo(self):
        v = self._video()
        sp.persistir_comentarios(self.banco, conteudo_id=v['CONTEUDO_ID'],
                                 run_id='RUN-1',
                                 comentarios=[comentario('C1', 'topo')])
        pai = self.banco.executa(
            "select coalesce(parent_externo_id,'(NULL)') from public.comentario"
            " where externo_id='C1'")[0][0]
        self.assertEqual(pai, '(NULL)')

    def test_P2_reply_aponta_para_o_topo_certo(self):
        v = self._video()
        sp.persistir_comentarios(
            self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
            comentarios=[comentario('C1', 'topo'),
                         comentario('C1.R1', 'resposta', parent='C1')])
        pai = self.banco.executa(
            "select parent_externo_id from public.comentario"
            " where externo_id='C1.R1'")[0][0]
        self.assertEqual(pai, 'C1')

    def test_P3_duas_replies_da_mesma_thread_continuam_duas(self):
        v = self._video()
        sp.persistir_comentarios(
            self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
            comentarios=[comentario('C1', 'topo'),
                         comentario('C1.R1', 'igual', parent='C1'),
                         comentario('C1.R2', 'igual', parent='C1')])
        n = self.banco.executa(
            "select count(*) from public.comentario where parent_externo_id='C1'")[0][0]
        self.assertEqual(int(n), 2, 'duas respostas com o mesmo texto viraram uma')

    def test_P4_reply_sem_pai_persistido_nao_vira_top_level(self):
        v = self._video()
        r = sp.persistir_comentarios(
            self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
            comentarios=[comentario('C9.R1', 'orfa', parent='C9-NAO-GRAVADO')])
        pai = self.banco.executa(
            "select parent_externo_id from public.comentario"
            " where externo_id='C9.R1'")[0][0]
        self.assertEqual(pai, 'C9-NAO-GRAVADO', 'a resposta foi promovida a topo')
        self.assertEqual(len(r['PAIS_NAO_PERSISTIDOS']), 1)
        self.assertEqual(r['PAIS_NAO_PERSISTIDOS'][0]['STATE'], sp.PAI_NAO_PERSISTIDO)

    def test_P5_a_thread_se_reconstroi_so_pelo_banco(self):
        v = self._video()
        sp.persistir_comentarios(
            self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
            comentarios=[comentario('C1', 'topo'),
                         comentario('C1.R1', 'r1', parent='C1'),
                         comentario('C1.R2', 'r2', parent='C1'),
                         comentario('C2', 'outro topo')])
        arv = sp.thread_do_conteudo(self.banco, conteudo_id=v['CONTEUDO_ID'])
        self.assertEqual(len(arv['TOP_LEVEL']), 2)
        c1 = [t for t in arv['TOP_LEVEL'] if t['EXTERNO_ID'] == 'C1'][0]
        self.assertEqual(sorted(r['EXTERNO_ID'] for r in c1['RESPOSTAS']),
                         ['C1.R1', 'C1.R2'])
        self.assertEqual(arv['ORFAS'], [])

    def test_P6_um_comentario_nao_pode_responder_a_si_mesmo(self):
        v = self._video()
        with self.assertRaises(RuntimeError):
            sp.persistir_comentarios(
                self.banco, conteudo_id=v['CONTEUDO_ID'], run_id='RUN-1',
                comentarios=[comentario('C1', 'circulo', parent='C1')])


# ═══════════════════════════════════════════════════════════════════════════
# I1..I5 — IDENTIDADE DE CANAL E DE PESSOA
# ═══════════════════════════════════════════════════════════════════════════
class IdentidadeDeCanal(BaseComCadeia):

    def test_I1_channel_id_sem_origem_e_recusa_explicita(self):
        cid, recusa = sp.exigir_canal(self.banco, platform='YOUTUBE',
                                      channel_id='UC-NUNCA-VISTO')
        self.assertIsNone(cid)
        self.assertEqual(recusa['STATE'], sp.CANAL_NAO_RESOLVIDO)

    def test_I2_nao_cria_pessoa_pelo_handle(self):
        antes = self.banco.executa("select count(*) from public.pessoa")[0][0]
        sp.exigir_canal(self.banco, platform='YOUTUBE',
                        channel_id='UC-riccardocastaldi')
        depois = self.banco.executa("select count(*) from public.pessoa")[0][0]
        self.assertEqual(antes, depois, 'criou pessoa a partir de um handle')

    def test_I3_nao_cria_organizacao_pelo_titulo_do_canal(self):
        antes = self.banco.executa("select count(*) from public.organizacao")[0][0]
        sp.exigir_canal(self.banco, platform='YOUTUBE', channel_id='UC-Syngenta-Italy')
        depois = self.banco.executa("select count(*) from public.organizacao")[0][0]
        self.assertEqual(antes, depois, 'criou organizacao a partir de um titulo')

    def test_I4_canal_ja_resolvido_deixa_o_conteudo_entrar(self):
        v = self._video()
        self.assertEqual(v['STATE'], 'OK')
        self.assertTrue(v['INSERIU_CONTEUDO'])

    def test_I5_handle_muda_e_o_canal_continua_o_mesmo(self):
        antes = sp.canal_canonico(self.banco, platform='YOUTUBE', channel_id=self.CANAL)
        self.banco.executa("update public.canal set handle='@nome-novo'"
                           " where channel_id='%s'" % self.CANAL)
        depois = sp.canal_canonico(self.banco, platform='YOUTUBE', channel_id=self.CANAL)
        self.assertEqual(antes, depois)
        n = self.banco.executa("select count(*) from public.canal")[0][0]
        self.assertEqual(int(n), 1, 'mudar o handle criou um canal novo')

    def test_I6_o_autor_e_pseudonimizado_e_o_nome_visivel_nunca_entra(self):
        v = self._video()
        sp.persistir_comentarios(self.banco, conteudo_id=v['CONTEUDO_ID'],
                                 run_id='RUN-1',
                                 comentarios=[comentario('C1', 'oi', autor='UCpessoa')])
        h = self.banco.executa(
            "select autor_hash from public.comentario where externo_id='C1'")[0][0]
        self.assertEqual(len(h), 64)
        self.assertNotIn('UCpessoa', h)
        self.assertEqual(h, sp.autor_hash('UCpessoa', platform='YOUTUBE'),
                         'o pseudonimo nao e estavel')
        tudo = self.banco.executa("select texto || coalesce(autor_hash,'')"
                                  " from public.comentario")[0][0]
        self.assertNotIn('Nome Visivel', tudo)

    def test_I7_sem_channel_id_do_autor_o_hash_e_ausencia_nao_invencao(self):
        self.assertIsNone(sp.autor_hash(None, platform='YOUTUBE'))
        self.assertIsNone(sp.autor_hash('UNKNOWN', platform='YOUTUBE'))

    def test_I8_o_pseudonimo_e_platform_scoped(self):
        """O MESMO numero em duas plataformas NAO e a mesma pessoa."""
        y = sp.autor_hash('12345', platform='YOUTUBE')
        i = sp.autor_hash('12345', platform='INSTAGRAM')
        self.assertNotEqual(y, i, 'dois autores viraram um so por terem o mesmo id')
        self.assertEqual(y, sp.autor_hash('12345', platform='youtube'),
                         'a plataforma tem de ser normalizada, senao o mesmo '
                         'autor vira duas pessoas por causa de maiuscula')

    def test_I9_nao_ha_identidade_de_pessoa_entre_plataformas(self):
        """CROSS-PLATFORM PERSON ID nao existe, e nao pode nascer por acidente."""
        pares = [('YOUTUBE', 'X1'), ('INSTAGRAM', 'X1'), ('LINKEDIN', 'X1')]
        hashes = {sp.autor_hash(n, platform=p) for p, n in pares}
        self.assertEqual(len(hashes), 3, 'plataformas diferentes colapsaram')
        # E a concatenacao nao pode colidir entre pares diferentes.
        self.assertNotEqual(sp.autor_hash('TUBEA1', platform='YOU'),
                            sp.autor_hash('A1', platform='YOUTUBE'))


# ═══════════════════════════════════════════════════════════════════════════
# S1..S10 — A ORDEM DA PERSISTENCIA
# ═══════════════════════════════════════════════════════════════════════════
class OrdemDaPersistencia(BaseComCadeia):

    def test_S3_api_respondeu_mas_RAW_nao_durou_e_conteudo_nao_entra(self):
        r = sp.persistir_video(self.banco, canal_id=self.canal_id, run_id='RUN-1',
                               content_id='vid-sem-raw', texto_canonico='t',
                               raw_durou=False)
        self.assertEqual(r['STATE'], sp.RAW_NAO_DUROU)
        n = self.banco.executa("select count(*) from public.conteudo")[0][0]
        self.assertEqual(int(n), 0, 'conteudo entrou sem RAW durado')

    def test_S5_conteudo_entrou_e_known_passa_a_enxergar(self):
        self.assertEqual(
            sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                  content_ids=['ezRyN8vLVvc']), set())
        self._video()
        self.assertEqual(
            sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                  content_ids=['ezRyN8vLVvc']), {'ezRyN8vLVvc'})

    def test_S6_retry_da_mesma_unidade_nao_duplica_conteudo(self):
        self._video()
        self._video()
        n = self.banco.executa("select count(*) from public.conteudo")[0][0]
        self.assertEqual(int(n), 1)

    def test_S7_nova_run_reencontra_e_observa_sem_novo_conteudo(self):
        self._video(run_id='RUN-1')
        self._run('RUN-2')
        r = self._video(run_id='RUN-2')
        self.assertTrue(r['REOBSERVACAO'])
        self.assertFalse(r['INSERIU_CONTEUDO'])
        conteudos = self.banco.executa("select count(*) from public.conteudo")[0][0]
        vistos = self.banco.executa("select count(*) from public.conteudo_visto_em")[0][0]
        self.assertEqual(int(conteudos), 1, 'AA: dois runs criaram dois conteudos')
        self.assertEqual(int(vistos), 2, 'AB: a reobservacao nao foi registrada')

    def test_S9_visto_mas_nao_persistido_nao_conta_como_conhecido(self):
        """SEEN NAO E PERSISTED — o incremental nao pode parar num video visto."""
        vistos_na_api = ['vid-A', 'vid-B', 'vid-C']
        sp.persistir_video(self.banco, canal_id=self.canal_id, run_id='RUN-1',
                           content_id='vid-A', texto_canonico='t', raw_durou=True)
        conhecidos = sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                           content_ids=vistos_na_api)
        self.assertEqual(conhecidos, {'vid-A'})
        self.assertNotIn('vid-B', conhecidos, 'video so VISTO virou KNOWN')


# ═══════════════════════════════════════════════════════════════════════════
# OS DOIS CRASHES
# ═══════════════════════════════════════════════════════════════════════════
class CrashERetomada(BaseComCadeia):

    def test_crash_depois_do_RAW_e_antes_do_conteudo_nao_marca_KNOWN(self):
        """RAW guardado, processo morre. O video NAO pode ser considerado KNOWN."""
        # A corrida chegou a preservar o bruto e morreu antes de `persistir_video`.
        conhecidos = sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                           content_ids=['ezRyN8vLVvc'])
        self.assertEqual(conhecidos, set(),
                         'RAW sozinho fez o video parecer colhido')
        # A execucao seguinte reencontra e TERMINA a persistencia.
        r = self._video()
        self.assertTrue(r['INSERIU_CONTEUDO'])
        self.assertEqual(
            sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                  content_ids=['ezRyN8vLVvc']), {'ezRyN8vLVvc'})

    def test_crash_depois_do_conteudo_e_antes_do_checkpoint_nao_duplica(self):
        """Conteudo entrou, processo morre antes do checkpoint. Retry e seguro."""
        primeiro = self._video()
        # Nenhum checkpoint avancou. A execucao seguinte refaz a unidade inteira.
        segundo = self._video()
        self.assertEqual(segundo['CONTEUDO_ID'], primeiro['CONTEUDO_ID'])
        self.assertFalse(segundo['INSERIU_CONTEUDO'])
        n = self.banco.executa("select count(*) from public.conteudo")[0][0]
        self.assertEqual(int(n), 1, 'o retry duplicou o conteudo')



# ═══════════════════════════════════════════════════════════════════════════
# S1, S2, S4, S8, S10 — A CADEIA INTEIRA COM O CHECKPOINT CANONICO
# ═══════════════════════════════════════════════════════════════════════════
class CadeiaComCheckpoint(BaseComCadeia):
    """RAW -> CONTEUDO -> COMENTARIO -> e SO ENTAO o checkpoint anda."""

    IDENTIDADE = ('PLATFORM', 'CHANNEL_ID', 'CAPABILITY')

    def _entrada(self, janela='2026-09-08'):
        return {'PLATFORM': 'YOUTUBE', 'CHANNEL_ID': self.CANAL,
                'CAPABILITY': 'INCREMENTAL', 'JANELA': janela}

    def test_S1_sem_checkpoint_a_API_nao_e_chamada(self):
        """A trava e ANTES do gasto: sem linha aberta, o ator nem roda."""
        chamou = []

        def trabalho(_u):
            chamou.append(1)
            return [], 'OK'

        h = cc.hash_da_entrada(self._entrada())
        pode, porque, _cid, _r = cc.pode_gastar(self.banco, 'YOUTUBE:%s' % self.CANAL, h)
        self.assertFalse(pode)
        self.assertEqual(porque, cc.SEM_CHECKPOINT)
        self.assertEqual(chamou, [], 'a API foi chamada sem checkpoint aberto')

    def test_S2_com_checkpoint_aberto_a_API_e_permitida(self):
        chamou = []

        def trabalho(_u):
            chamou.append(1)
            return [{'CONTENT_ID': 'vid-1'}], 'OK'

        r = cc.executar_unidade(
            self.banco, target='YOUTUBE:%s' % self.CANAL, entrada=self._entrada(),
            actor='youtube-data-api-v3', platform='YOUTUBE', unidade='u1',
            trabalho=trabalho,
            persistir=lambda itens, _u: len(itens),
            campos_da_identidade=self.IDENTIDADE)
        self.assertEqual(chamou, [1])
        self.assertEqual(r['STATE'], cc.UNIDADE_FEITA)

    def test_S4_RAW_durou_mas_conteudo_falhou_e_o_checkpoint_nao_anda(self):
        def persistir_que_falha(_itens, _u):
            raise RuntimeError('o writer de conteudo caiu depois do RAW')

        with self.assertRaises(RuntimeError):
            cc.executar_unidade(
                self.banco, target='YOUTUBE:%s' % self.CANAL, entrada=self._entrada(),
                actor='youtube-data-api-v3', platform='YOUTUBE', unidade='u1',
                trabalho=lambda _u: ([{'CONTENT_ID': 'vid-1'}], 'OK'),
                persistir=persistir_que_falha,
                campos_da_identidade=self.IDENTIDADE)
        feitas = self.banco.executa(
            "select unidades_feitas, itens_persistidos from public.checkpoint_coleta")[0]
        self.assertEqual(feitas[0], '0', 'o checkpoint avancou sem conteudo salvo')
        self.assertEqual(feitas[1], '0')
        n = self.banco.executa("select count(*) from public.conteudo")[0][0]
        self.assertEqual(int(n), 0)

    def test_S8_newest_until_known_para_no_PERSISTIDO(self):
        """A varredura para no primeiro video que EXISTE no banco — nao no visto."""
        sp.persistir_video(self.banco, canal_id=self.canal_id, run_id='RUN-1',
                           content_id='vid-antigo', texto_canonico='t', raw_durou=True)
        # A API devolve do mais novo para o mais velho.
        da_api = ['vid-novo-1', 'vid-novo-2', 'vid-antigo', 'vid-mais-antigo']
        conhecidos = sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                           content_ids=da_api)
        novos = []
        for v in da_api:
            if v in conhecidos:
                break
            novos.append(v)
        self.assertEqual(novos, ['vid-novo-1', 'vid-novo-2'])
        self.assertNotIn('vid-mais-antigo', novos, 'passou do ponto de parada')

    def test_S10_o_checkpoint_so_anda_depois_do_persistido(self):
        """A ORDEM, medida: quando o checkpoint avanca, o conteudo JA esta la."""
        ordem = []

        def persistir(itens, _u):
            for it in itens:
                sp.persistir_video(self.banco, canal_id=self.canal_id,
                                   run_id='RUN-1', content_id=it['CONTENT_ID'],
                                   texto_canonico='t', raw_durou=True)
            n = self.banco.executa("select count(*) from public.conteudo")[0][0]
            ordem.append(('persistiu', int(n)))
            return len(itens)

        r = cc.executar_unidade(
            self.banco, target='YOUTUBE:%s' % self.CANAL, entrada=self._entrada(),
            actor='youtube-data-api-v3', platform='YOUTUBE', unidade='u1',
            trabalho=lambda _u: ([{'CONTENT_ID': 'vid-1'}], 'OK'),
            persistir=persistir, campos_da_identidade=self.IDENTIDADE)
        feitas = self.banco.executa(
            "select unidades_feitas from public.checkpoint_coleta")[0][0]
        ordem.append(('checkpoint', int(feitas)))
        self.assertEqual(ordem, [('persistiu', 1), ('checkpoint', 1)])
        self.assertEqual(r['ITENS_PERSISTIDOS'], 1)

    def test_S10b_a_mesma_unidade_nao_e_paga_duas_vezes(self):
        def trabalho(_u):
            return [{'CONTENT_ID': 'vid-1'}], 'OK'

        for _ in range(1):
            cc.executar_unidade(
                self.banco, target='YOUTUBE:%s' % self.CANAL, entrada=self._entrada(),
                actor='youtube-data-api-v3', platform='YOUTUBE', unidade='u1',
                trabalho=trabalho, persistir=lambda i, _u: len(i),
                campos_da_identidade=self.IDENTIDADE)
        chamou = []
        r = cc.executar_unidade(
            self.banco, target='YOUTUBE:%s' % self.CANAL, entrada=self._entrada(),
            actor='youtube-data-api-v3', platform='YOUTUBE', unidade='u1',
            trabalho=lambda u: (chamou.append(1), ([], 'OK'))[1],
            persistir=lambda i, _u: len(i),
            campos_da_identidade=self.IDENTIDADE)
        self.assertEqual(r['STATE'], cc.JA_CONCLUIDO)
        self.assertEqual(chamou, [], 'pagou a mesma unidade duas vezes')



# ═══════════════════════════════════════════════════════════════════════════
# V1..V6 — ON CONFLICT DO NOTHING SEM COMPARACAO NAO E IDEMPOTENCIA
# ═══════════════════════════════════════════════════════════════════════════
# Reproduzido em Postgres real antes de corrigido: RUN-A grava VIDEO-1 com
# corpo AAA; RUN-B reencontra VIDEO-1 com corpo BBB e o writer devolvia
# `STATE=OK, REOBSERVACAO=True` sem NUNCA ter olhado o hash que estava la. O
# titulo novo entrava calado e a unica pista de que o mundo mudou sumia.
#
#     IDENTIDADE IGUAL + CONTEUDO OBSERVADO DIFERENTE
#     NAO E REOBSERVACAO SAUDAVEL SILENCIOSA.
class ConteudoReencontrado(BaseComCadeia):

    CORPO_A = None      # preenchido no setUp, via o dono da serializacao

    def setUp(self):
        super().setUp()
        self._run('RUN-2')
        self._run('RUN-3')
        self.CORPO_A = sp.corpo_canonico(titulo='Titolo A', descricao='descrizione')
        self.CORPO_B = sp.corpo_canonico(titulo='Titolo A EDITADO', descricao='descrizione')

    def _grava(self, run_id, corpo):
        return sp.persistir_video(self.banco, canal_id=self.canal_id, run_id=run_id,
                                  content_id='VIDEO-1', texto_canonico=corpo,
                                  raw_durou=True)

    # ── V1 ────────────────────────────────────────────────────────────────
    def test_V1_mesmo_content_id_e_mesmo_hash_e_reobservacao_saudavel(self):
        self.assertEqual(self._grava('RUN-1', self.CORPO_A)['STATE'], 'OK')
        r = self._grava('RUN-2', self.CORPO_A)
        self.assertEqual(r['STATE'], sp.REOBSERVADO)
        self.assertTrue(r['REOBSERVACAO'])
        self.assertFalse(r['INSERIU_CONTEUDO'])

    # ── V2 ────────────────────────────────────────────────────────────────
    def test_V2_mesmo_content_id_com_hash_diferente_nao_e_OK_silencioso(self):
        self._grava('RUN-1', self.CORPO_A)
        r = self._grava('RUN-2', self.CORPO_B)
        self.assertEqual(r['STATE'], sp.CONTEUDO_DIVERGIU)
        self.assertNotEqual(r['STATE'], 'OK')
        self.assertNotEqual(r['STATE'], sp.REOBSERVADO)
        self.assertNotEqual(r['HASH_NO_BANCO'], r['HASH_OBSERVADO'])
        self.assertIn('GAP', r, 'o gap do schema tem de viajar com o estado')

    # ── V3 ────────────────────────────────────────────────────────────────
    def test_V3_divergencia_nao_sobrescreve_a_linha_antiga(self):
        self._grava('RUN-1', self.CORPO_A)
        antes = self.banco.executa(
            "select hash_conteudo from public.conteudo where content_id='VIDEO-1'")[0][0]
        r = self._grava('RUN-2', self.CORPO_B)
        depois = self.banco.executa(
            "select hash_conteudo from public.conteudo where content_id='VIDEO-1'")[0][0]
        self.assertEqual(antes, depois, 'a linha antiga foi sobrescrita em silencio')
        self.assertFalse(r['SOBRESCREVEU'])

    # ── V4 ────────────────────────────────────────────────────────────────
    def test_V4_conteudo_visto_em_nao_transforma_drift_em_sucesso(self):
        """A observacao E registada — a corrida viu mesmo. Mas nao vira OK."""
        self._grava('RUN-1', self.CORPO_A)
        r = self._grava('RUN-2', self.CORPO_B)
        vistos = self.banco.executa(
            "select count(*) from public.conteudo_visto_em")[0][0]
        self.assertEqual(int(vistos), 2, 'a procedencia da observacao se perdeu')
        self.assertEqual(r['STATE'], sp.CONTEUDO_DIVERGIU,
                         'a linha de observacao fez o drift parecer sucesso')

    # ── V5 ────────────────────────────────────────────────────────────────
    def test_V5_known_continua_significando_content_id_persistido(self):
        self._grava('RUN-1', self.CORPO_A)
        self._grava('RUN-2', self.CORPO_B)     # drift nao apaga o conhecido
        self.assertEqual(
            sp.conteudo_conhecido(self.banco, canal_id=self.canal_id,
                                  content_ids=['VIDEO-1', 'VIDEO-2']),
            {'VIDEO-1'})

    # ── V6 ────────────────────────────────────────────────────────────────
    def test_V6_crash_retry_continua_idempotente(self):
        primeiro = self._grava('RUN-1', self.CORPO_A)
        segundo = self._grava('RUN-1', self.CORPO_A)      # retry da MESMA run
        terceiro = self._grava('RUN-2', self.CORPO_A)     # e de outra
        self.assertEqual(segundo['CONTEUDO_ID'], primeiro['CONTEUDO_ID'])
        self.assertEqual(terceiro['CONTEUDO_ID'], primeiro['CONTEUDO_ID'])
        n = self.banco.executa("select count(*) from public.conteudo")[0][0]
        self.assertEqual(int(n), 1)

    def test_V7_o_corpo_canonico_tem_dono_e_versao(self):
        """Dois chamadores com serializacoes diferentes inventariam drift falso."""
        self.assertTrue(sp.CORPO_VERSAO.startswith('v'))
        self.assertIn(sp.CORPO_VERSAO, sp.corpo_canonico(titulo='t', descricao='d'))
        # Contadores que mudam sozinhos NAO entram no corpo — se entrassem, todo
        # reencontro de um video vivo viraria CONTENT_DRIFT.
        self.assertEqual(sp.corpo_canonico(titulo='t', descricao='d'),
                         sp.corpo_canonico(titulo='t', descricao='d'))
        self.assertNotEqual(sp.corpo_canonico(titulo='t', descricao='d'),
                            sp.corpo_canonico(titulo='t2', descricao='d'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
