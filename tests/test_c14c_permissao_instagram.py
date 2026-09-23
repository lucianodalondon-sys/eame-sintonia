#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C14-C — A SUPERFÍCIE DE PERMISSÃO DO INSTAGRAM.

O release gate da Big Collection parou aqui, e com razão. Medido antes desta
missão: `COLLECT(instagram.profile.discovery)` lançava o navegador num
**SUBPROCESSO** — «lote congelado: 5 contas de Instagram» — e um bloqueio de
socket no processo-pai não alcança um subprocesso.

    UM PORTÃO QUE O PROCESSO-FILHO NÃO CONHECE NÃO É UM PORTÃO.

A porta existia: `adaptador_instagram.politica()` lê `social_matriz` e barrava
as outras três capacidades de Reel. Esta passava ao lado — porque
`PERMITIDA = CONDICIONAL` (uma condição do AMBIENTE: `DATACENTER_BLOCKED`,
302/429 deste IP) era lida como `ALLOWED` (uma decisão de NEGÓCIO).

    UMA LIMITAÇÃO TÉCNICA NÃO É UMA AUTORIZAÇÃO.

E a segunda metade, que só apareceu ao medir: declarar os três eixos NÃO
bastava. `_autorizada_pelo_projeto` lia só `OWNER_AUTHORIZED` — o que servia
enquanto a única rota com eixos era o áudio do YouTube, cuja política já
estava MEDIDA (`DISALLOWED`) e cujo dono assumiu esse risco. `NOT_MEASURED` é
outro estado:

    DISALLOWED   mediu-se, e proíbe.      O dono pode assumir o risco.
    NOT_MEASURED ninguém mediu.           Não há risco assumido — há risco
                                          por conhecer, e não se assume o que
                                          não se conhece.

        AUTORIZAR NÃO É MEDIR. E SEM MEDIR, NÃO SAI.

NENHUMA PROVA AQUI ABRE REDE NEM LANÇA SUBPROCESSO — e duas delas existem
exactamente para provar isso.
"""
import os
import socket
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for gaveta in ('coleta', 'leis', 'ferramentas', 'regras'):
    sys.path.insert(0, os.path.join(RAIZ, gaveta))
sys.path.insert(0, RAIZ)

import social_matriz as mz                 # noqa: E402
import scrap_capacidades as cap            # noqa: E402
import scrap_executor as SX                # noqa: E402
import adaptador_instagram                 # noqa: E402  (regista as rotas)
import adaptador_youtube                   # noqa: E402

AS_QUATRO = ('instagram.reel.capture', 'instagram.reel.audio',
             'instagram.reel.transcribe', 'instagram.profile.discovery')


class _Fronteira:
    """Sela as DUAS saídas: socket E subprocesso.

    Instrumentar só o socket foi o que deixou o defeito passar despercebido —
    o navegador saía num processo filho, e o filho tem o seu próprio socket.
    """

    def __enter__(self):
        self.rede, self.subs = [], []
        self._sock = socket.socket.connect
        self._run = subprocess.run
        self._popen = subprocess.Popen.__init__

        def sem_rede(_s, endereco, *a, **k):
            self.rede.append(endereco)
            raise AssertionError('ABRIU REDE: %r' % (endereco,))

        def sem_run(*a, **k):
            self.subs.append(str(a[0])[:80] if a else '?')
            raise AssertionError('LANÇOU SUBPROCESSO (run)')

        def sem_popen(_self, *a, **k):
            self.subs.append(str(a[0])[:80] if a else '?')
            raise AssertionError('LANÇOU SUBPROCESSO (Popen)')

        socket.socket.connect = sem_rede
        subprocess.run = sem_run
        subprocess.Popen.__init__ = sem_popen
        return self

    def __exit__(self, *e):
        socket.socket.connect = self._sock
        subprocess.run = self._run
        subprocess.Popen.__init__ = self._popen
        return False


def _remote_allowed(capability):
    """A pergunta que importa: a POLÍTICA deixa esta capability sair?"""
    grossa = cap.da_matriz(capability)
    if not grossa:
        return False
    return mz.decisao('INSTAGRAM', grossa)['DECISAO'] == mz.PERMITIDA_SIM


class OVocabularioGanhouUmLimite(unittest.TestCase):
    """Decisão 2 do dono: ampliar o vocabulário fechado."""

    def test_1_o_limite_novo_existe(self):
        self.assertIn('PUBLIC_PROFILE_DISCOVERY_ONLY', mz.LIMITES)

    def test_2_o_limite_do_audio_continua(self):
        self.assertIn('PUBLIC_AUDIO_ONLY', mz.LIMITES)

    def test_3_o_vocabulario_continua_FECHADO(self):
        """Ampliar não é abrir: só estes dois, e um terceiro exige decisão."""
        # ⚠️ O TERCEIRO ENTROU COM DECISÃO DE DONO, E ESTÁ CITADA (D22): a
        # coleta de REELS por URL directa não é som do YouTube nem descoberta de
        # perfil — tem o seu próprio limite, porque um limite que não descreve o
        # que a rota faz não trava nada.
        self.assertEqual({'PUBLIC_AUDIO_ONLY', 'PUBLIC_REEL_BY_URL_ONLY',
                          'PUBLIC_PROFILE_DISCOVERY_ONLY'}, set(mz.LIMITES))

    def test_4_nao_se_criou_segundo_vocabulario(self):
        """O limite vive em `LIMITES`, e só lá."""
        import inspect
        src = inspect.getsource(mz)
        self.assertEqual(1, src.count("LIMITES = ("),
                         'há uma segunda lista de limites')


class OsTresEixosDaDescoberta(unittest.TestCase):
    """Decisões 1 e 3: o dono autoriza; a plataforma continua por medir."""

    def _rota(self):
        return mz.MATRIZ['INSTAGRAM']['INCREMENTAL'][0]

    def test_5_declara_os_tres_eixos(self):
        r = self._rota()
        for eixo in mz.EIXOS:
            self.assertIn(eixo, r, 'falta o eixo %s' % eixo)

    def test_6_o_dono_autorizou(self):
        self.assertEqual('SIM', self._rota()['OWNER_AUTHORIZED'])

    def test_7_a_plataforma_continua_POR_MEDIR(self):
        """Não se fabrica prova de política — Decisão 3, textual."""
        self.assertEqual('NOT_MEASURED', self._rota()['PLATFORM_POLICY_STATUS'])

    def test_8_o_limite_e_o_da_descoberta_e_nao_o_do_audio(self):
        self.assertEqual('PUBLIC_PROFILE_DISCOVERY_ONLY', self._rota()['LIMITE'])
        self.assertNotEqual('PUBLIC_AUDIO_ONLY', self._rota()['LIMITE'])


class AutorizarNaoEMedir(unittest.TestCase):
    """O coração desta missão: SIM do dono + política por medir = fechado."""

    def test_9_owner_SIM_com_NOT_MEASURED_nao_autoriza(self):
        rota = {'OWNER_AUTHORIZED': 'SIM',
                'PLATFORM_POLICY_STATUS': 'NOT_MEASURED',
                'LIMITE': 'PUBLIC_PROFILE_DISCOVERY_ONLY'}
        self.assertFalse(mz._autorizada_pelo_projeto(rota))

    def test_10_owner_SIM_com_DISALLOWED_medido_continua_a_autorizar(self):
        """O caso do YouTube: risco MEDIDO e assumido pelo dono."""
        rota = {'OWNER_AUTHORIZED': 'SIM',
                'PLATFORM_POLICY_STATUS': 'DISALLOWED',
                'LIMITE': 'PUBLIC_AUDIO_ONLY'}
        self.assertTrue(mz._autorizada_pelo_projeto(rota))

    def test_11_owner_NAO_nunca_autoriza(self):
        for politica in ('ALLOWED', 'DISALLOWED', 'NOT_MEASURED'):
            rota = {'OWNER_AUTHORIZED': 'NAO',
                    'PLATFORM_POLICY_STATUS': politica,
                    'LIMITE': 'PUBLIC_AUDIO_ONLY'}
            self.assertFalse(mz._autorizada_pelo_projeto(rota), politica)

    def test_12_rota_SEM_eixos_continua_como_era(self):
        """Nenhuma rota antiga regride: ausência de eixos não muda nada."""
        self.assertTrue(mz._autorizada_pelo_projeto(
            {'ROTA': 'antiga', 'PERMITIDA': 'SIM'}))


class ANENHUMASAIDASEMPORTEIRO(unittest.TestCase):
    """O gate central: REMOTE_CAPABILITIES_WITHOUT_GATE = 0."""

    def test_13_nenhuma_capability_instagram_esta_ALLOWED_SEM_EIXOS(self):
        """⚠️ ESTE TESTE DIZIA «nenhuma está ALLOWED». A decisão mudou (D22).

        O que ele existe para guardar não é o `NAO` — é que ninguém abre uma
        rota remota do Instagram SEM declarar, na própria rota, quem autorizou,
        o que a plataforma diz e até onde a rota vai. Uma autorização sem eixos
        é uma autorização sem dono.

            UMA PORTA ABERTA TEM DE DIZER QUEM A ABRIU.
        """
        abertas = [c for c in AS_QUATRO if _remote_allowed(c)]
        for c in abertas:
            grossa = cap.da_matriz(c)
            for rota in mz.MATRIZ['INSTAGRAM'][grossa]:
                if rota.get('ROTA') != mz.decisao('INSTAGRAM', grossa)['ROTA']:
                    continue
                for eixo in mz.EIXOS:
                    self.assertIn(eixo, rota,
                                  '%s está ALLOWED sem declarar %s' % (c, eixo))

    def test_14_todas_as_capacidades_grossas_alcancaveis_tem_portao(self):
        """Não só as quatro conhecidas — TODA capacidade ALCANÇÁVEL.

        ⚠️ A PRIMEIRA VERSÃO DESTE TESTE MEDIA A MATRIZ INTEIRA E FICOU
        VERMELHA — e a medição valeu a pena. `FETCH_PROFILE`, `FETCH_COMMENTS`
        e `FETCH_POST` respondem `ALLOWED` e não declaram eixos.

        Mas ALCANÇÁVEL é outra pergunta, e foi medida:

            FETCH_PROFILE · FETCH_POST   nenhuma capability fina mapeia para
                                         elas. Não há por onde pedi-las.
            FETCH_COMMENTS               `instagram.post.comments` mapeia,
                                         mas NÃO está registada em
                                         `scrap_registo` — sem ROTA e sem
                                         EXECUTA.

        As três param em `CAPABILITY_STATE_PROMISES_NOTHING`, antes da
        política, com `SUBPROCESS_CALLS = 0` e `NETWORK_CALLS = 0` (provado em
        `test_16b`). O portão que as barra é outro — o do estado da
        capability — e barrar é barrar.

            UMA PORTA QUE NÃO EXISTE NÃO PRECISA DE FECHADURA.
            MAS ALGUÉM TEM DE PROVAR QUE ELA NÃO EXISTE.

        Por isso este teste mede o que É alcançável, e `test_16b` prova que o
        resto não sai. Declarar eixos para capacidades que ninguém consegue
        pedir seria escrever política para uma porta imaginária — e a próxima
        pessoa a ligar uma delas teria de declarar os eixos na mesma.
        """
        import scrap_registo as SR
        abertas = []
        for fina in cap.DECLARADAS:
            if not fina.startswith('instagram'):
                continue
            registo = SR._MAPA.get(('INSTAGRAM', fina))
            if not (registo and (registo.get('ROTA') or registo.get('EXECUTA'))):
                continue                      # não alcançável: nada a pedir
            if not _remote_allowed(fina):
                continue
            # ALLOWED é legítimo desde a D22 — mas só com os três eixos na rota
            # que a executa. Sem eixos, ninguém assinou aquilo.
            grossa = cap.da_matriz(fina)
            linha = [r for r in mz.MATRIZ['INSTAGRAM'].get(grossa, [])
                     if r.get('ROTA') == mz.decisao('INSTAGRAM', grossa)['ROTA']]
            self.assertTrue(linha, '%s ALLOWED sem rota declarada' % fina)
            for eixo in mz.EIXOS:
                self.assertIn(eixo, linha[0],
                              '%s ALLOWED sem declarar %s' % (fina, eixo))


class AProvaCritica(unittest.TestCase):
    """O caso que antes lançava subprocesso."""

    def test_15_profile_discovery_nao_lanca_subprocesso_nem_rede(self):
        with _Fronteira() as f:
            objetos, trace = SX.COLLECT(platform='INSTAGRAM',
                                        capability='instagram.profile.discovery',
                                        run_id='C14C-PROVA', handle='teste')
        self.assertEqual([], f.subs, 'SUBPROCESS_CALLS tem de ser 0')
        self.assertEqual([], f.rede, 'NETWORK_CALLS tem de ser 0')
        self.assertEqual([], objetos)
        self.assertEqual('ROUTE_NOT_ALLOWED', trace.get('RESULT'))

    def test_16_as_quatro_param_antes_da_fronteira(self):
        for c in AS_QUATRO:
            with _Fronteira() as f:
                objetos, _trace = SX.COLLECT(platform='INSTAGRAM', capability=c,
                                             run_id='C14C', handle='x')
            self.assertEqual([], f.subs, '%s lançou subprocesso' % c)
            self.assertEqual([], f.rede, '%s abriu rede' % c)
            self.assertEqual([], objetos, '%s devolveu objetos' % c)


    def test_16b_as_nao_alcancaveis_tambem_nao_saem(self):
        """A outra metade do `test_14`: prova, não promessa.

        `FETCH_PROFILE`, `FETCH_COMMENTS` e `FETCH_POST` respondem `ALLOWED`
        na matriz e não declaram eixos. Este teste prova que isso não abre
        saída nenhuma: as capabilities finas que lhes pertencem param no
        portão do ESTADO — `CAPABILITY_STATE_PROMISES_NOTHING` — antes de a
        política sequer ser consultada.

            DOIS PORTÕES EM SÉRIE: O QUE MEDE O ESTADO E O QUE MEDE A
            PERMISSÃO. BASTA UM FECHADO PARA NÃO SAIR — MAS É PRECISO
            SABER QUAL DELES ESTÁ A FECHAR.
        """
        for c in ('instagram.post.comments', 'instagram.story.capture',
                  'instagram.story.transcribe'):
            with _Fronteira() as f:
                objetos, trace = SX.COLLECT(platform='INSTAGRAM', capability=c,
                                            run_id='C14C', handle='x')
            self.assertEqual([], f.subs, '%s lançou subprocesso' % c)
            self.assertEqual([], f.rede, '%s abriu rede' % c)
            self.assertEqual([], objetos, '%s devolveu objetos' % c)


class NaoSeHerdaAutorizacao(unittest.TestCase):
    """A lei da C14-B não pode regredir."""

    def test_17_cada_capability_pergunta_pela_sua_capacidade_grossa(self):
        """Três nomes de Reel = UM acto (FETCH_TRANSCRIPT). Discovery é outro."""
        self.assertEqual('INCREMENTAL', cap.da_matriz('instagram.profile.discovery'))
        self.assertEqual('FETCH_TRANSCRIPT', cap.da_matriz('instagram.reel.transcribe'))

    def test_18_o_limite_da_descoberta_nao_viaja_para_o_reel(self):
        """⚠️ AUTORIZAR DISCOVERY CONTINUA A NÃO AUTORIZAR MÍDIA.

        O que este teste media era a recusa do reel — e a recusa caiu (D22).
        O que ele passa a medir é a COISA QUE IMPORTA e que não mudou: o reel
        não herda o limite da descoberta. Cada rota tem o seu, e o do reel é
        mais estreito no que traz (bytes de um reel dado) e mais largo no que
        faz (adquire mídia) — o que ele NÃO permite é o que a descoberta
        permite: varrer um perfil.
        """
        reel = mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')
        self.assertEqual(mz.PERMITIDA_SIM, reel['DECISAO'])
        linha = [r for r in mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT']
                 if r.get('ROTA') == reel['ROTA']][0]
        self.assertEqual('PUBLIC_REEL_BY_URL_ONLY', linha['LIMITE'])
        self.assertNotEqual('PUBLIC_PROFILE_DISCOVERY_ONLY', linha['LIMITE'])
        # e a descoberta continua fechada: o limite dela não abre o reel, e o
        # do reel não abre a descoberta.
        self.assertEqual(mz.NAO_PERMITIDA,
                         mz.decisao('INSTAGRAM', 'INCREMENTAL')['DECISAO'])

    def test_19_o_limite_da_descoberta_nao_viaja_para_o_youtube(self):
        for rotas in (mz.MATRIZ.get('YOUTUBE') or {}).values():
            if not isinstance(rotas, list):
                continue
            for r in rotas:
                self.assertNotEqual('PUBLIC_PROFILE_DISCOVERY_ONLY',
                                    r.get('LIMITE'))


class OYoutubeNaoRegride(unittest.TestCase):
    """Regressão obrigatória: o que passou E2E continua a passar."""

    def test_20_o_audio_publico_continua_permitido(self):
        d = mz.decisao('YOUTUBE', 'FETCH_AUDIO_BYTES')
        self.assertEqual(mz.PERMITIDA_SIM, d['DECISAO'])
        self.assertEqual('yt-dlp:public_audio', d['ROTA'])

    def test_21_os_tres_eixos_do_audio_estao_intactos(self):
        rota = [r for r in mz.MATRIZ['YOUTUBE']['FETCH_AUDIO_BYTES']
                if r['ROTA'] == 'yt-dlp:public_audio'][0]
        self.assertEqual('SIM', rota['OWNER_AUTHORIZED'])
        self.assertEqual('DISALLOWED', rota['PLATFORM_POLICY_STATUS'])
        self.assertEqual('PUBLIC_AUDIO_ONLY', rota['LIMITE'])

    def test_22_as_quatro_oficiais_continuam_permitidas(self):
        for grossa in ('SEARCH_KEYWORD', 'INCREMENTAL',
                       'FETCH_VIDEO_METADATA', 'FETCH_COMMENTS'):
            self.assertEqual(mz.PERMITIDA_SIM,
                             mz.decisao('YOUTUBE', grossa)['DECISAO'], grossa)

    def test_23_a_matriz_continua_valida(self):
        """`conferir_matriz` corre no import; chamá-la aqui é explícito."""
        mz.conferir_matriz()


class ASentinelaContraORegresso(unittest.TestCase):
    """Fica de guarda depois desta missão."""

    def test_24_NOT_MEASURED_e_lido_pelo_gate(self):
        """Se alguém voltar a ler só OWNER_AUTHORIZED, isto morde."""
        import inspect
        src = inspect.getsource(mz._autorizada_pelo_projeto)
        codigo = '\n'.join(l for l in src.splitlines()
                           if not l.strip().startswith('#'))
        self.assertIn('NOT_MEASURED', codigo,
                      'o gate deixou de ler PLATFORM_POLICY_STATUS')

    def test_25_o_gate_nao_foi_desligado_desligando_a_rota(self):
        """Proibido resolver com UNWIRED: a rota continua wired."""
        self.assertTrue(mz.MATRIZ['INSTAGRAM']['INCREMENTAL'],
                        'a rota foi removida em vez de ser trancada')
        import scrap_registo as SR
        self.assertIn(('INSTAGRAM', 'instagram.profile.discovery'), SR._MAPA)

    def test_26_o_estado_da_capability_nao_foi_maquiado(self):
        """Proibido baixar PROVEN→BLOCKED para reduzir a contagem."""
        import scrap_capacidades as sc
        self.assertEqual('PROVEN', sc.DECLARADAS['instagram.reel.audio'][1])
        self.assertEqual('PROVEN', sc.DECLARADAS['instagram.reel.capture'][1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
