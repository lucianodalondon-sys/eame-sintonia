#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS PROVAS DO AUDIO PUBLICO DO YOUTUBE — o que NAO pode ser confundido.

Nasceu do §149. A casa passou a ter, na mesma plataforma, quatro coisas que se
parecem e nao sao:

    dados oficiais (Data API)   descoberta, canal, metadata, comentarios
    legenda nativa              rota PAGA, 25% de falha ja paga  -> PARTIAL
    audio publico               bytes do som, com SHA e ASR      -> PROVEN
    media/video                 os bytes audiovisuais            -> BLOCKED

Este ficheiro existe para que uma capacidade nao herde o carimbo da vizinha.
Nenhuma prova aqui precisa de rede.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap    # noqa: E402
import social_matriz as mz         # noqa: E402

OFICIAIS = ('youtube.search', 'youtube.channel.discovery',
            'youtube.video.metadata', 'youtube.comments')
AUDIO = 'youtube.public_audio'
CAPTION = 'youtube.native_caption'
MEDIA = 'youtube.media'


class AAudioNaoPromoveNada(unittest.TestCase):
    """Uma prova de AUDIO nao e prova de VIDEO, de CAPTION nem de DADOS."""

    def test_1_audio_PROVEN_nao_faz_media_PROVEN(self):
        """AUDIO_ONLY != VIDEO. O som foi adquirido; o video, nunca."""
        self.assertEqual(cap.estado(AUDIO), cap.PROVEN)
        self.assertEqual(cap.estado(MEDIA), cap.BLOCKED,
                         'a prova de audio promoveu `youtube.media` — ela significa '
                         'os bytes audiovisuais, e o video nao foi adquirido')
        self.assertFalse(cap.promete_resultado(MEDIA))

    def test_2_audio_PROVEN_nao_faz_caption_PROVEN(self):
        """CAPTION != TRANSCRIPT. A legenda continua na rota paga, com 25% de falha."""
        self.assertEqual(cap.estado(AUDIO), cap.PROVEN)
        self.assertEqual(cap.estado(CAPTION), cap.PARTIAL)
        self.assertNotEqual(cap.estado(CAPTION), cap.PROVEN)

    def test_3_caption_PARTIAL_nao_faz_audio_PARTIAL(self):
        """O estado de uma nao se propaga a outra, em nenhum sentido."""
        self.assertEqual(cap.estado(CAPTION), cap.PARTIAL)
        self.assertEqual(cap.estado(AUDIO), cap.PROVEN)

    def test_4_dados_oficiais_nao_fazem_audio_PROVEN(self):
        """OFFICIAL_DATA != AUDIO. As quatro oficiais sao PROVEN e nao tocam som.

        Se as quatro bastassem, `youtube.public_audio` nao precisaria de existir
        — e ela existe exatamente porque a API nao entrega bytes de audio.
        """
        for c in OFICIAIS:
            self.assertEqual(cap.estado(c), cap.PROVEN, c)
        self.assertTrue(cap.existe(AUDIO))
        self.assertNotIn(AUDIO, OFICIAIS)
        # E a prova do audio nao e a prova das oficiais.
        self.assertNotEqual(cap.prova(AUDIO), cap.prova(OFICIAIS[0]))

    def test_5_media_nao_volta_a_prometer_por_causa_do_audio(self):
        """A vigia que trava o regresso: media BLOCKED nao promete resultado."""
        self.assertIn(cap.BLOCKED, cap.SEM_PROMESSA)
        self.assertFalse(cap.promete_resultado(MEDIA))
        self.assertEqual(cap.onde(MEDIA), (cap.LOCAL, cap.DATACENTER_BLOCKED))


class CadaUmaTemProvaPropria(unittest.TestCase):
    """§147: estado de capability ancora na prova que mediu AQUELA rota."""

    def test_6_a_prova_do_audio_aponta_para_o_documento_do_audio(self):
        self.assertEqual(cap.prova(AUDIO),
                         'docs/sintonia-scrap/C13-YOUTUBE-PUBLIC-AUDIO.md')

    def test_7_a_prova_do_caption_e_o_gate_que_a_mediu_e_nao_o_censo(self):
        """O censo conta actors e custo; quem mediu esta rota foi o C5."""
        self.assertEqual(cap.prova(CAPTION),
                         'docs/sintonia-scrap/C5-YOUTUBE-TRANSCRIPT-ROUTE-GATE.md')
        self.assertNotEqual(cap.prova(CAPTION),
                            'docs/sintonia-scrap/CENSO-DOS-ACTORS-E-CUSTO-V1.md')

    def test_8_as_provas_do_youtube_sao_tres_documentos_distintos(self):
        """Nenhuma capacidade do YouTube herda a prova de outra."""
        p_audio, p_caption, p_oficial = cap.prova(AUDIO), cap.prova(CAPTION), cap.prova(OFICIAIS[0])
        self.assertEqual(len({p_audio, p_caption, p_oficial}), 3)

    def test_9_toda_prova_citada_pelas_capacidades_do_youtube_existe_no_disco(self):
        """Ponteiro de prova pendurado e o defeito que o §147 descreve.

        Um estado que aponta para um ficheiro inexistente nao pode ser
        conferido por ninguem — e um carimbo sem testemunha.
        """
        vistas = {}
        for n in [x for x in cap.DECLARADAS if x.startswith('youtube.')]:
            p = cap.prova(n)
            vistas.setdefault(p, []).append(n)
        self.assertTrue(vistas, 'nenhuma capacidade do YouTube declarada')
        for p, nomes in vistas.items():
            with self.subTest(prova=p, capacidades=nomes):
                self.assertTrue(os.path.exists(os.path.join(RAIZ, p)),
                                '%s cita prova inexistente: %s' % (nomes, p))


class OsTresEixosNaoSeColapsam(unittest.TestCase):
    """TECNICAMENTE FUNCIONA != O DONO AUTORIZOU != A PLATAFORMA PERMITE."""

    def test_10_a_matriz_nao_declara_audio_e_isso_nao_e_permissao(self):
        """`FETCH_AUDIO` nao existe na matriz: ausencia de decisao, nao licenca."""
        d = mz.decisao('YOUTUBE', 'FETCH_AUDIO')
        self.assertNotEqual(d['DECISAO'], 'ALLOWED',
                            'a matriz passou a autorizar audio sem linha escrita')
        self.assertEqual(d['DECISAO'], 'NOT_DECLARED')

    def test_11_a_capacidade_de_audio_reivindica_UM_dono_grosso_e_um_so(self):
        """⚠️ ESTE TESTE JA EXIGIU `None`, E O `None` ERA O GAP.

        Enquanto a matriz nao tinha porta grossa para audio, a resposta certa era
        `None` — e o teste vigiava isso. A porta passou a existir
        (`FETCH_AUDIO_BYTES`, com os tres eixos declarados), entao o `None`
        deixou de ser verdade. A vigia nao se apaga: reancora-se.

            ONE CONCEPT -> ONE OWNER. E o dono grosso e UM.

        ⚠️ C14-C · E O CONCEITO E `PLATAFORMA + GROSSA`, NAO A GROSSA SOZINHA.

        Segunda reancoragem, pelo mesmo motivo de fundo: a lista percorria
        `cap.DECLARADAS` inteira e exigia que so o YouTube reivindicasse
        `FETCH_AUDIO_BYTES`. Isso valia enquanto ele era o unico veiculo com
        audio publico autorizado; com o Instagram a ganhar a SUA porta (C14), a
        asercao passou a proibir o que a casa ja faz em 8 outras portas grossas
        partilhadas.

            `mz.decisao(platform, capability)` PEDE AS DUAS CHAVES.
            INSTAGRAM/FETCH_AUDIO_BYTES != YOUTUBE/FETCH_AUDIO_BYTES:
            rotas diferentes, executores diferentes, gates diferentes.

        O dono UNICO continua exigido — dentro da plataforma. Um segundo
        `youtube.*` sobre a mesma porta reprova, que e a avaria real que este
        teste sempre quis apanhar.
        """
        self.assertEqual(cap.da_matriz(AUDIO), 'FETCH_AUDIO_BYTES')
        plataforma = cap.DECLARADAS[AUDIO][0]
        donos = [n for n, linha in cap.DECLARADAS.items()
                 if cap.da_matriz(n) == 'FETCH_AUDIO_BYTES' and linha[0] == plataforma]
        self.assertEqual(donos, [AUDIO],
                         'a porta grossa de %s ganhou um segundo dono' % plataforma)
        # E a porta de OUTRA plataforma nao e esta: chaves distintas, rotas
        # distintas. Se um dia colapsarem numa so, isto reprova.
        self.assertNotEqual(mz.decisao('INSTAGRAM', 'FETCH_AUDIO_BYTES')['ROTA'],
                            mz.decisao(plataforma, 'FETCH_AUDIO_BYTES')['ROTA'],
                            'duas plataformas colapsaram na mesma rota de audio')

    def test_12_o_estado_do_audio_nao_vem_da_matriz(self):
        """A matriz responde «esta rota pode ser usada?»; o registry, «correu?».

        Os dois donos continuam separados, e prova-se com um caso vivo: a matriz
        pode fechar uma rota sem que a capacidade tecnica deixe de existir. O
        estado da CAPACIDADE le-se de `scrap_capacidades`; o da ROTA, da matriz.
        """
        self.assertEqual(cap.estado(AUDIO), cap.PROVEN)
        # a matriz tem a rota, e ela diz coisas que o registry nao diz
        d = mz.decisao('YOUTUBE', 'FETCH_AUDIO_BYTES')
        self.assertEqual(d['PLATFORM_POLICY_STATUS'], 'DISALLOWED')
        self.assertEqual(cap.estado(AUDIO), cap.PROVEN)   # e isso nao a bloqueia
        # e a capacidade nao promete rota nenhuma: ela promete RESULTADO.
        self.assertTrue(cap.promete_resultado(AUDIO))


class OVocabularioEUmSo(unittest.TestCase):
    def test_13_o_nome_segue_a_convencao_pontuada(self):
        self.assertIn('.', AUDIO)
        self.assertTrue(AUDIO.startswith('youtube.'))
        self.assertTrue(cap.conferir(AUDIO))

    def test_14_nao_ha_sinonimo_concorrente_para_audio_do_youtube(self):
        """Um conceito, um dono — sem `youtube.audio`, `youtube.audio_stream` e afins."""
        audio_do_youtube = [n for n in cap.DECLARADAS
                            if n.startswith('youtube.') and 'audio' in n]
        self.assertEqual(audio_do_youtube, [AUDIO],
                         'sinonimo concorrente criado: %s' % audio_do_youtube)


if __name__ == '__main__':
    unittest.main(verbosity=2)
