#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D24 · O VIDEO DE PESSOA — o que a autorizacao escrita abriu, e o que NAO abriu.

    python -m unittest tests.test_d24_video_de_pessoa

O dono autorizou por escrito o VIDEO de pessoas do agro (D24,
`DECISOES-DONO-2026-09-23.md`). Este teste guarda as DUAS METADES da mesma
frase, e e isso que o distingue de um teste de permissao:

    o que ele AUTORIZOU  ->  o post PUBLICO de uma pessoa, com os tres eixos
    o que ele NAO ABRIU  ->  perfil, contatos, seguidores, mensagens,
                             comentarios de terceiros, ecra de login,
                             pontuacao de pessoa, tela de pessoas nomeadas

Zero rede: a trava e ESTATICA, e por isso pode ser provada sempre.
"""
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in ('coleta', 'leis', 'regras', 'pedido', 'provas', ''):
    sys.path.insert(0, os.path.join(RAIZ, g) if g else RAIZ)
import _gavetas  # noqa: E402,F401
import social_matriz as mz  # noqa: E402
import adaptador_linkedin as al  # noqa: E402

POST_DE_PESSOA = ('https://www.linkedin.com/posts/alberto-grimelli-85a72856_'
                  'lolivo-si-sposta-activity-7428520945017012224-OCSK')
POST_COM_VIDEO = ('https://www.linkedin.com/posts/celestino-dom%C3%ADnguez-infante-423b4957_'
                  'uplcorpiberia-activity-7445139302390382592-eYKi')


def _rotas(plat, cap):
    return mz.MATRIZ[plat][cap]


class AMatrizDizD24(unittest.TestCase):
    """As rotas novas existem, e declaram os TRES eixos juntos."""

    def test_1_as_rotas_de_pessoa_existem(self):
        esperado = {
            ('DISCOVER_ACCOUNT', 'linkedin:perfil-publico-de-pessoa'),
            ('DISCOVER_POST', al.ROTA_POST_PUBLICO),
            ('FETCH_VIDEO_BYTES', al.ROTA_VIDEO_BYTES_PESSOA),
            ('FETCH_TRANSCRIPT', al.ROTA_LEGENDA_PESSOA),
        }
        for cap, nome in sorted(esperado):
            rotas = [r for r in _rotas('LINKEDIN', cap) if r.get('ROTA') == nome]
            self.assertEqual(1, len(rotas), 'rota em falta: %s/%s (%s)' % ('LINKEDIN', cap, nome))
            r = rotas[0]
            self.assertEqual(al.LIMITE_DA_PESSOA, r['LIMITE'],
                             'a rota de pessoa tem de carregar o limite da pessoa')

    def test_2_a_lei_das_duas_frases(self):
        """A plataforma proibe e o dono autorizou: as duas frases, sempre juntas.

        Escrever só uma delas é a mentira desta rota — dizer «autorizado» sem
        dizer que a plataforma proíbe, ou dizer «proibido» escondendo que o
        dono assumiu o risco.
        """
        vistas = 0
        for cap in ('DISCOVER_ACCOUNT', 'DISCOVER_POST', 'FETCH_VIDEO_BYTES', 'FETCH_TRANSCRIPT'):
            for r in _rotas('LINKEDIN', cap):
                if r.get('LIMITE') != al.LIMITE_DA_PESSOA:
                    continue
                vistas += 1
                self.assertEqual('SIM', r['OWNER_AUTHORIZED'])
                self.assertEqual('DISALLOWED', r['PLATFORM_POLICY_STATUS'])
                self.assertIn('D24', r['NOTA'])
        self.assertEqual(4, vistas, 'as quatro rotas de pessoa declaram os eixos')

    def test_3_o_perfil_de_pessoa_esta_declarado_e_recusado(self):
        """A porta que a plataforma fechou nao fica em silencio.

        O D24 autorizou o VIDEO; mediu-se que a pagina de PERFIL responde 999
        com `authwall`. Uma autorizacao que nao diz o que a plataforma faz com
        o pedido nao serve para decidir nada — e por isso a recusa e uma LINHA
        do vocabulario, e nao um comentario.
        """
        rotas = [r for r in _rotas('LINKEDIN', 'DISCOVER_ACCOUNT')
                 if r.get('ROTA') == 'linkedin:perfil-publico-de-pessoa']
        self.assertEqual(1, len(rotas), 'a rota do perfil de pessoa tem de estar declarada')
        r = rotas[0]
        self.assertEqual('NAO', r['PERMITIDA'])
        self.assertEqual('BLOCKED', r['ESTADO'])
        self.assertIn('999', r['NOTA'])
        self.assertIn('authwall', r['NOTA'])

    def test_4_o_D24_nao_mexeu_na_rota_da_organizacao(self):
        """Efeito lateral é o que este teste existe para apanhar.

        A porta de ORGANIZACAO (D23) continua com o limite dela e o estado
        dela. Se o D24 tivesse passado por cima, este teste cairia.
        """
        r = [x for x in _rotas('LINKEDIN', 'FETCH_VIDEO_BYTES')
             if x.get('ROTA') == al.ROTA_VIDEO_BYTES][0]
        self.assertEqual('PUBLIC_ORG_VIDEO_ONLY', r['LIMITE'])
        self.assertEqual('PROVED', r['ESTADO'])
        self.assertIn('D23', r['NOTA'])


class ATravaSemRede(unittest.TestCase):
    """A prova mais barata é a que corre sempre: a recusa é ESTÁTICA."""

    def test_5_o_post_publico_de_pessoa_passa(self):
        url, ident = al._alvo_e_post_publico(POST_DE_PESSOA)
        self.assertEqual(POST_DE_PESSOA, url)
        self.assertEqual('7428520945017012224', ident)

    def test_6_o_post_de_pessoa_com_video_tambem_passa(self):
        _, ident = al._alvo_e_post_publico(POST_COM_VIDEO)
        self.assertEqual('7445139302390382592', ident)

    def test_7_o_perfil_de_pessoa_e_recusado_com_o_motivo_medido(self):
        with self.assertRaises(Exception) as c:
            al._alvo_e_post_publico('https://www.linkedin.com/in/alberto-grimelli-85a72856/')
        txt = str(c.exception)
        self.assertIn('PERFIL DE PESSOA', txt)
        self.assertIn('999', txt)
        self.assertIn('NAO se contorna', txt.strip().replace('NÃO se contorna', 'NAO se contorna'))

    def test_8_contatos_seguidores_mensagens_e_comentarios_ficam_fora(self):
        """O D24 autorizou o VIDEO, e nomeou estes quatro como fora.

        Cada um deles tem de morrer na trava ANTES da rede — e o teste mede a
        categoria, e nao so a excecao.
        """
        alvos = {
            'contato': 'https://www.linkedin.com/in/alberto-grimelli-85a72856/detail/contact-info/',
            'contato (overlay)': 'https://www.linkedin.com/overlay/contact-info/',
            'seguidores': 'https://www.linkedin.com/in/alberto-grimelli-85a72856/followers/',
            'conexoes': 'https://www.linkedin.com/in/alberto-grimelli-85a72856/connections/',
            'mensagens': 'https://www.linkedin.com/messaging/thread/1234/',
            'comentarios de terceiros': ('https://www.linkedin.com/feed/update/'
                                         'urn:li:activity:7428520945017012224/comments/'),
        }
        for nome, alvo in alvos.items():
            with self.assertRaises(Exception) as c:
                al._alvo_e_post_publico(alvo)
            self.assertIn('conteudo PESSOAL', str(c.exception),
                          'a recusa de %s tem de nomear a categoria' % nome)

    def test_9_o_ecra_de_login_para_e_registra(self):
        with self.assertRaises(Exception) as c:
            al._alvo_e_post_publico('https://www.linkedin.com/uas/login')
        txt = str(c.exception)
        self.assertIn('ecra de login', txt)
        self.assertIn('NAO contorna controlo de acesso', txt)

    def test_10_a_pagina_de_organizacao_e_porta_trocada_e_nao_alvo_proibido(self):
        """Um alvo na porta errada nao e um alvo proibido — e a recusa diz isso.

        Confundir as duas coisas faz um pedido legitimo parecer uma violacao, e
        faz uma violacao parecer um pedido mal escrito.
        """
        with self.assertRaises(ValueError) as c:
            al._alvo_e_post_publico('https://www.linkedin.com/company/image-line/')
        self.assertIn('ALVO_TROCADO_DE_PORTA', str(c.exception))
        # E nao e uma RotaNaoPermitida: alvo na porta errada nao e alvo proibido.
        self.assertNotIsInstance(c.exception, al.http.RotaNaoPermitida)

    def test_11_um_post_sem_video_nao_vira_video(self):
        """`cartoes_com_video` numa pagina sem `data-sources` devolve ZERO.

        É a fronteira entre «não tem vídeo» e «não consegui ler o vídeo»: sem
        esta prova, um parse falhado passaria por resultado da plataforma.
        """
        sem_video = '<html><body><div>post sem media</div><video></video></body></html>'
        self.assertEqual([], al.cartoes_com_video(sem_video))
        self.assertEqual([], al.cartoes_com_video(''))

    def test_12_o_cartao_do_post_de_pessoa_le_o_video_e_a_legenda(self):
        """A mesma tecnica da D23, medida no HTML que aquela pagina serve.

        Um `<video data-sources>` com `data-captions-url` tem de devolver UM
        cartao, com a identidade ligada por IDENTIDADE (o activity id dentro do
        endereco), e nunca por posicao.
        """
        html = (
            '<span>urn:li:activity:7445139302390382592</span>'
            '<a href="https://www.linkedin.com/posts/celestino-dom%C3%ADnguez-infante-423b4957_uplcorpiberia-'
            'activity-7445139302390382592-eYKi">ver</a>'
            '<video data-sources="[{&quot;src&quot;:&quot;https://dms.licdn.com/x/mp4-640p&quot;}]"'
            ' data-captions-url="https://dms.licdn.com/x/video-auto-caption-webvtt"'
            ' data-digitalmedia-asset-urn="urn:li:digitalmediaAsset:D4E05AQHdUfZSb0GSFA"'
            ' data-language="en"></video>')
        cartoes = al.cartoes_com_video(html)
        self.assertEqual(1, len(cartoes))
        c = cartoes[0]
        self.assertEqual('7445139302390382592', c['ACTIVITY_ID'])
        self.assertEqual('IDENTIDADE', c['LIGACAO'])
        self.assertTrue(c['VIDEO_RENDICOES'])
        self.assertTrue(c['CAPTION_URL'])
        # E, sem `urn` no documento, a identidade ainda desce do ENDERECO — e o
        # cartao DIZ por que via a ligou, em vez de a dar por certa.
        sem_urn = al.cartoes_com_video(
            '<a href="https://www.linkedin.com/posts/x_activity-7445139302390382592-eYKi">v</a>'
            '<video data-sources="[{&quot;src&quot;:&quot;https://dms.licdn.com/x/mp4-640p&quot;}]"></video>')
        self.assertEqual(1, len(sem_urn))
        self.assertEqual('7445139302390382592', sem_urn[0]['ACTIVITY_ID'])
        self.assertEqual('SO_URL', sem_urn[0]['LIGACAO'])


class OQueOD24NaoReabre(unittest.TestCase):
    """Os outros donos continuam a mandar no que e deles."""

    def test_16_o_estado_das_rotas_de_pessoa_vem_da_MEDICAO(self):
        """O estado não é etiqueta: é o resultado de uma medição, com número.

        As três rotas de pessoa estão `PROVED` porque o canário de 2026-09-23
        mediu um post público de PESSOA com MP4 e legenda. Rebaixar isto sem
        medição esconde o que se fez; promover sem medir inventa o que não se
        fez — e as duas coisas têm de fazer este teste MORRER.
        """
        for cap, nome in (('DISCOVER_POST', al.ROTA_POST_PUBLICO),
                          ('FETCH_VIDEO_BYTES', al.ROTA_VIDEO_BYTES_PESSOA),
                          ('FETCH_TRANSCRIPT', al.ROTA_LEGENDA_PESSOA)):
            r = [x for x in _rotas('LINKEDIN', cap) if x.get('ROTA') == nome][0]
            self.assertEqual('PROVED', r['ESTADO'], '%s/%s' % (cap, nome))
        # os números da medição vivem na própria nota, para quem audita
        nota = [x for x in _rotas('LINKEDIN', 'FETCH_VIDEO_BYTES')
                if x.get('ROTA') == al.ROTA_VIDEO_BYTES_PESSOA][0]['NOTA']
        self.assertIn('6 935 096', nota)
        self.assertIn('1 371', nota)

    def test_13_o_limite_nomeia_o_que_nao_permite(self):
        texto = mz.__dict__['LIMITES']  # existe
        self.assertIn('PUBLIC_PERSON_VIDEO_ONLY', texto)
        import inspect
        src = inspect.getsource(mz)
        bloco = src.split("'PUBLIC_PERSON_VIDEO_ONLY'")[0].rsplit('# ── O LIMITE DO VIDEO DE PESSOA', 1)[-1]
        for fora in ('CONTATOS', 'SEGUIDORES', 'MENSAGENS', 'COMENTARIOS DE',
                     'perfil privado', 'PERSONAL_SCORING'):
            self.assertIn(fora, bloco, 'o limite tem de dizer que %s fica fora' % fora)

    def test_14_os_limites_de_dado_pessoal_continuam_no_dono_deles(self):
        """O D24 autoriza COLETA; a tela de pessoas nomeadas e de outro dono.

        Este teste existe para impedir a leitura mais perigosa da autorizacao:
        «o dono autorizou, então tudo o que fala de pessoas está liberado».
        """
        p = os.path.join(RAIZ, 'docs', 'regras', 'LIMITES-DE-DADO-PESSOAL-EAME.md')
        with io.open(p, encoding='utf-8') as f:
            txt = f.read()
        self.assertIn('NAMED_RESEARCHER_PUBLIC_SCREEN = BLOCKED_PENDING_LEGAL_REVIEW', txt)
        self.assertIn('PERSONAL_SCORING               = PROHIBITED_FOR_CURRENT_PILOT', txt)
        self.assertIn('EMAIL', txt)
        # e a matriz declara isso mesmo, no proprio limite
        self.assertIn('NAMED_RESEARCHER_PUBLIC_SCREEN',
                      inspect_src(mz), 'o limite tem de nomear o que não reabre')

    def test_15_nenhuma_rota_de_conteudo_pessoal_foi_autorizada(self):
        """Varredura: nenhuma rota desta matriz carrega o limite da pessoa
        apontando para contato, seguidor, mensagem ou comentario."""
        proibidos = ('contact-info', 'followers', 'following', 'connections',
                     'messaging', 'comments')
        for plat, caps in mz.MATRIZ.items():
            if plat.startswith('_'):
                continue
            for cap, rotas in caps.items():
                if not isinstance(rotas, list):
                    continue
                for r in rotas:
                    if r.get('LIMITE') != 'PUBLIC_PERSON_VIDEO_ONLY':
                        continue
                    nome = str(r.get('ROTA') or '').lower()
                    for p in proibidos:
                        self.assertNotIn(p, nome,
                                         'rota de conteudo pessoal autorizada: %s' % nome)


# ══════════════════════════════════════════════════════════════════════════
# D24 TAMBÉM VALE NO INSTAGRAM — E A D22 JÁ TINHA ABERTO OS REELS
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ ESTE BLOCO NASCEU DE UMA CORREÇÃO DO COORDENADOR, e a correção estava
# certa: a primeira versão da D24 recusava o Reel de pessoa no Instagram com a
# justificação «a plataforma proíbe». Essa leitura colapsava os DOIS eixos num
# só — dizia a proibição e escondia quem tinha assumido o risco, que é
# exactamente o desenho que a casa já usava no áudio do YouTube (D17.4/C13) e no
# vídeo de organização do LinkedIn (D23), e que a **D22** já tinha aplicado aos
# Reels do Instagram.
#
#     UMA LEITURA DE UM EIXO SÓ NÃO É UMA DECISÃO: É METADE DELA.
#
# O que fica congelado aqui são os NÚMEROS medidos, e não uma promessa.
CANARIO_INSTAGRAM = {
    'ALVO': 'https://www.instagram.com/reel/DdW2PPWAqht/',
    'PESSOA': '@dr.agricultura — Alessandro Giglietti, dottore agronomo (IT)',
    'MEDIA_STATE': 'MEDIA_OK',
    'MEDIA_KIND': 'AUDIO',
    'AUDIO_ONLY_ACQUISITION': 'PROVEN',
    'BYTES': 696245,
    'SHA256': 'ea372eebbae1faac3bc6e745324f147371bbbbf6ab1075a341b7a17481bc48db',
    'CAPTION_TEXT_CHARS': 731,
    'EGRESSO': 'IT',
    'CUSTO_USD': 0.0,
}
MATRIZ_INSTAGRAM = 'INSTAGRAM/FETCH_TRANSCRIPT'


class AOutraPlataformaDaD24(unittest.TestCase):
    """O Instagram: a mesma D24, o mesmo limite, os mesmos dois eixos."""

    def test_16_o_instagram_declara_os_tres_eixos(self):
        # a linha da D24 procura-se pelo LIMITE: ao lado dela vive a da D22 (Reel por URL)
        r = [x for x in mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT']
             if x.get('LIMITE') == 'PUBLIC_PERSON_VIDEO_ONLY'][0]
        for eixo in mz.EIXOS:
            self.assertIn(eixo, r, 'falta o eixo %s no Instagram' % eixo)
        self.assertEqual('SIM', r['OWNER_AUTHORIZED'])
        self.assertEqual('DISALLOWED', r['PLATFORM_POLICY_STATUS'])
        self.assertEqual('PUBLIC_PERSON_VIDEO_ONLY', r['LIMITE'])

    def test_17_a_decisao_do_instagram_e_a_do_projeto_e_diz_quem_assumiu(self):
        d = mz.decisao('INSTAGRAM', 'FETCH_TRANSCRIPT')
        self.assertEqual(mz.PERMITIDA_SIM, d['DECISAO'])
        self.assertEqual('SIM', d['OWNER_AUTHORIZED'])
        self.assertEqual('DISALLOWED', d['PLATFORM_POLICY_STATUS'])

    def test_18_a_nota_carrega_os_numeros_medidos_e_o_nome_da_decisao(self):
        """A nota é a prova escrita: sem os números, a rota abre por narrativa."""
        nota = [x for x in mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT']
                if x.get('LIMITE') == 'PUBLIC_PERSON_VIDEO_ONLY'][0]['NOTA']
        self.assertIn('D22/D24', nota)
        self.assertIn('696 245', nota)
        self.assertIn(CANARIO_INSTAGRAM['SHA256'][:8], nota)
        self.assertIn('AUDIO', nota.upper(), 'a nota esqueceu a espécie adquirida')

    def test_19_o_perfil_de_pessoa_continua_FECHADO_nas_duas_plataformas(self):
        """A plataforma fecha a porta que fala da pessoa e abre a da publicação.

        Medido no LinkedIn (999/authwall) e no Instagram (muro de login na grade
        por HTTP). O que a D24 abriu foi o POST, e é isso que aqui se guarda.
        """
        r = [x for x in mz.MATRIZ['LINKEDIN']['DISCOVER_ACCOUNT']
             if x['ROTA'] == 'linkedin:perfil-publico-de-pessoa'][0]
        self.assertEqual('NAO', r['PERMITIDA'])
        self.assertEqual('BLOCKED', r['ESTADO'])
        # no Instagram, a rota da janela (descoberta) NÃO é autorizada:
        d = mz.decisao('INSTAGRAM', 'INCREMENTAL')
        self.assertNotEqual(mz.PERMITIDA_SIM, d['DECISAO'],
                            'a descoberta de perfil ganhou autorização por '
                            'efeito lateral da D24')

    def test_20_o_que_a_D24_nao_abre_esta_nomeado_na_nota(self):
        """O que NÃO abre está nomeado — e a lista tem dono.

        A NOTA da ROTA diz o que a rota faz (e que não se contorna muro); a
        `_NOTA` da PLATAFORMA diz o que a plataforma fecha. As duas juntas são a
        lista fechada: procurar num lado só faria o teste medir a minha memória
        do sítio, não a frase escrita.
        """
        rota = mz.MATRIZ['INSTAGRAM']['FETCH_TRANSCRIPT'][0]
        proibicoes = rota['NOTA'] + ' ' + mz.MATRIZ['INSTAGRAM']['_NOTA']
        for proibido in ('login', 'CONTATOS', 'SEGUIDORES', 'DM',
                         'COMENTÁRIOS DE TERCEIROS', 'PERSONAL_SCORING',
                         'NAMED_RESEARCHER_PUBLIC_SCREEN'):
            self.assertIn(proibido, proibicoes,
                          'a declaracao deixou de nomear %s' % proibido)

    def test_21_o_canario_congelado_e_reproduzivel_por_comando(self):
        """O canário vive em `provas/` e corre com um comando — sem ele, os
        números acima seriam folclore."""
        p = os.path.join(RAIZ, 'provas', 'canario_d24_reel_de_pessoa.py')
        self.assertTrue(os.path.exists(p), 'o canario do Instagram desapareceu')
        txt = io.open(p, encoding='utf-8').read()
        self.assertIn(CANARIO_INSTAGRAM['ALVO'], txt)
        self.assertIn('portao_de_egresso', txt,
                      'o canario deixou de medir o egresso antes e depois')
        self.assertIn("EGRESS_GATE_BEFORE", txt)
        self.assertIn("EGRESS_GATE_AFTER", txt)


def inspect_src(mod):
    import inspect
    return inspect.getsource(mod)


if __name__ == '__main__':
    unittest.main(verbosity=2)
