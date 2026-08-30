#!/usr/bin/env python3
"""Provas de que um portao nao pode ser declarado READY por quem escreve o texto.

A contradicao que originou este arquivo foi publicada por nos: o mesmo
relatorio disse LOCATION_CONTRACT_COMPLETE = NO e EAME_COLLECTION_ENTRY_GATE
= READY. Nenhum teste pegou, porque o estado do portao era uma FRASE.

Aqui o estado e DERIVADO. E o teste mais importante deste arquivo nao e o
que confere o resultado de hoje: e o que impede a saida facil de amanha —
tirar a familia que incomoda da lista do portao e colher READY.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import portoes_eame as P                                          # noqa: E402


class TestOEstadoEDerivado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = P.monta()

    def test_o_portao_da_coleta_cobre_a_familia_da_localizacao(self):
        """A saida facil, fechada.

        Bastaria tirar LOCALIZACAO_CONFERENCIA da lista do portao da coleta
        para ele virar READY sem que nenhuma lacuna fosse resolvida. Este
        teste existe para que essa edicao reprove.
        """
        fam = P.PORTOES['EAME_COLLECTION_ENTRY_GATE']['FAMILIAS']
        for exigida in ('LOCALIZACAO', 'LOCALIZACAO_CONFERENCIA'):
            self.assertIn(exigida, fam,
                          'tirar %s do portao da COLETA seria escolher o escopo '
                          'depois de ver o resultado' % exigida)

    def test_a_resposta_sobre_localizacao_bate_com_a_lista(self):
        """Dizer YES e nao pôr a familia na lista seria duas respostas."""
        resp = self.d['LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE']
        na_lista = 'LOCALIZACAO_CONFERENCIA' in \
            P.PORTOES['EAME_COLLECTION_ENTRY_GATE']['FAMILIAS']
        self.assertEqual(resp == 'YES', na_lista,
                         'a frase e a lista discordam sobre o mesmo fato')

    def test_ready_exige_toda_cicatriz_coberta_em_proved(self):
        for nome, p in self.d['PORTOES'].items():
            with self.subTest(portao=nome):
                if p['ESTADO'] == 'READY':
                    self.assertEqual([], p['BLOQUEADORES'],
                                     '%s READY com bloqueador' % nome)
                else:
                    self.assertTrue(p['BLOQUEADORES'],
                                    '%s PARTIAL sem dizer o que o bloqueia' % nome)

    def test_todo_bloqueador_diz_o_que_falta_e_o_que_fazer(self):
        for nome, p in self.d['PORTOES'].items():
            for b in p['BLOQUEADORES']:
                with self.subTest(portao=nome, cicatriz=b['ID']):
                    self.assertTrue((b['GAP'] or '').strip(), 'bloqueador sem GAP')
                    self.assertTrue((b['ACAO_MINIMA'] or '').strip(),
                                    'bloqueador sem acao minima')

    def test_o_portao_da_coleta_nao_tem_bloqueador_pendente(self):
        """Este teste ja afirmou PARTIAL, e afirmava certo na epoca.

        As cinco cicatrizes de FACT LOCATION fecharam na 018, e o portao
        passou a READY pela DERIVACAO — nenhuma cicatriz foi promovida para
        que isso acontecesse. O que o teste guarda agora e a coerencia: se
        houver bloqueador, o estado nao pode ser READY, e vice-versa.
        """
        p = self.d['PORTOES']['EAME_COLLECTION_ENTRY_GATE']
        self.assertEqual([], p['BLOQUEADORES'])
        self.assertEqual('READY', p['ESTADO'])

    def test_o_portao_do_catalogo_nao_depende_das_lacunas_de_localizacao(self):
        """Nao por conveniencia: um registro regulatorio nao tem lugar de fato."""
        fam = P.PORTOES['CATALOG_IMPORT_ENGINEERING_GATE']['FAMILIAS']
        self.assertNotIn('LOCALIZACAO_CONFERENCIA', fam)
        self.assertEqual('READY',
                         self.d['PORTOES']['CATALOG_IMPORT_ENGINEERING_GATE']['ESTADO'])

    def test_os_contratos_tambem_sao_derivados(self):
        """LOCATION_CONTRACT_COMPLETE era uma FRASE, e por isso pode dizer YES
        ao lado de uma lacuna aberta. Agora ele sai da mesma matriz."""
        c = self.d['CONTRATOS']['LOCATION_CONTRACT_COMPLETE']
        self.assertEqual('YES', c['COMPLETO'])
        self.assertEqual([], c['ABERTAS'])
        for nome, v in self.d['CONTRATOS'].items():
            with self.subTest(contrato=nome):
                self.assertEqual(v['COMPLETO'] == 'YES', not v['ABERTAS'],
                                 '%s afirma COMPLETO e lista cicatriz aberta' % nome)

    def test_o_contrato_da_localizacao_cobre_as_duas_familias(self):
        self.assertEqual(['LOCALIZACAO', 'LOCALIZACAO_CONFERENCIA'],
                         P.CONTRATOS['LOCATION_CONTRACT_COMPLETE'],
                         'tirar uma familia daqui daria YES sem resolver nada')

    def test_os_cinco_que_acabaram_de_fechar_continuam_proved(self):
        """Controle. Nada desta rodada pode ter reaberto os cinco."""
        from cicatrizes_brasil import monta as mc
        por_id = {c['ID']: c for c in mc()['CICATRIZES']}
        for cid in ('BR-14', 'BR-16', 'BR-19', 'BR-20', 'BR-21'):
            with self.subTest(cicatriz=cid):
                self.assertEqual('PROVED', por_id[cid]['EAME_STATUS'])

    def test_todo_portao_pronto_diz_o_que_ele_NAO_cobre(self):
        """A primeira versao deste teste proibia o nome abrangente de estar
        READY. Isso era certo enquanto ele era PARTIAL, e virou regra errada
        quando ele passou: proibir um nome nao e uma lei, e READY legitimo
        num nome abrangente e READY. O que continua valendo e que um portao
        pronto tem de dizer onde a promessa dele termina."""
        for n, p in self.d['PORTOES'].items():
            if p['ESTADO'] != 'READY':
                continue
            with self.subTest(portao=n):
                self.assertTrue(p['O_QUE_ELE_NAO_COBRE'].strip(),
                                'portao READY sem dizer o que ele NAO cobre')
                self.assertTrue(p['O_QUE_ELE_COBRE'].strip())


class TestMutacoes(unittest.TestCase):
    """Suite verde em cima de logica quebrada nao prova nada."""

    def test_uma_cicatriz_de_localizacao_reaberta_derruba_o_portao_da_coleta(self):
        """A mutacao que importa agora que tudo esta PROVED.

        A anterior tirava a familia da lista e conferia se o portao virava
        READY — e perdeu os dentes no momento em que as cinco fecharam:
        com tudo PROVED, tirar a familia nao muda nada. Esta poe a mao no
        estado de uma cicatriz, que e o que o portao le de verdade.
        """
        import cicatrizes_brasil as C
        alvo = [c for c in C.CICATRIZES if c['ID'] == 'BR-30'][0]
        antes = alvo['EAME_STATUS']
        alvo['EAME_STATUS'] = 'PARTIAL'
        try:
            d = P.monta()
            self.assertEqual('PARTIAL',
                             d['PORTOES']['EAME_COLLECTION_ENTRY_GATE']['ESTADO'],
                             'reabrir uma cicatriz de FACT LOCATION nao derrubou o '
                             'portao da coleta — entao ele nao a estava lendo')
            self.assertEqual('NO',
                             d['CONTRATOS']['LOCATION_CONTRACT_COMPLETE']['COMPLETO'])
            # E o portao do CATALOGO nao se move: e a prova de que os dois
            # portoes sao mesmo diferentes, e nao dois nomes do mesmo estado.
            self.assertEqual('READY',
                             d['PORTOES']['CATALOG_IMPORT_ENGINEERING_GATE']['ESTADO'],
                             'a lacuna de lugar do fato derrubou o portao do catalogo: '
                             'entao ele nunca foi um portao separado')
        finally:
            alvo['EAME_STATUS'] = antes
        self.assertEqual('READY',
                         P.monta()['PORTOES']['EAME_COLLECTION_ENTRY_GATE']['ESTADO'])

    def test_raw_aberto_nunca_deixa_import_virar_yes(self):
        """A trava que esta missao pediu, nos DOIS caminhos que a burlariam.

        Caminho 1: os numeros dizem que faltam assets. Caminho 2: os numeros
        estao certos e alguem escreve ESTADO='CLOSED' num arquivo. Nenhum
        dos dois pode abrir o portao — e o segundo e o mais facil de fazer
        sem querer, porque nao exige mentir sobre nenhum numero.
        """
        real = P.raw_es
        casos = [
            ('faltam assets no bucket',
             dict(ALREADY_PRESENT_VERIFIED=185, FAILED_WITH_REASON=11,
                  DO_PLANO_AUSENTES=11, ESTADO='OPEN_EXTERNAL_REPAIR')),
            ('ESTADO diz CLOSED e os numeros dizem que nao',
             dict(ALREADY_PRESENT_VERIFIED=185, FAILED_WITH_REASON=11,
                  DO_PLANO_AUSENTES=11, ESTADO='CLOSED')),
            ('ha orfaos no bucket',
             dict(ORFAOS_NO_BUCKET=3, ESTADO='CLOSED')),
            ('um hash divergente',
             dict(HASH_MISMATCH=1, ESTADO='CLOSED')),
        ]
        try:
            for nome, mudanca in casos:
                with self.subTest(caso=nome):
                    P.raw_es = lambda m=mudanca: dict(real(), **m)
                    d = P.monta()
                    self.assertEqual('NO', d['IMPORT_CAN_BE_NEXT_MISSION'],
                                     'RAW aberto deixou IMPORT virar YES: %s' % nome)
                    self.assertNotEqual('CLOSED', d['RAW_PRESERVATION_GATE']['ESTADO'])
                    self.assertTrue(d['PORQUE_NAO_IMPORTAR'])
        finally:
            P.raw_es = real
        # E, com o raw de verdade, ele volta a YES — sem isso os quatro casos
        # acima estariam verdes so porque a conta diz NAO para tudo.
        self.assertEqual('YES', P.monta()['IMPORT_CAN_BE_NEXT_MISSION'])

    def test_o_artefato_discordando_de_si_mesmo_falha_fechado(self):
        """ESTADO e os numeros sao dois donos da mesma verdade. Quando
        discordam, o portao nao escolhe o mais conveniente: ele para."""
        real = P.raw_es
        P.raw_es = lambda: dict(real(), ESTADO='OPEN_EXTERNAL_REPAIR')
        try:
            g = P.monta()['RAW_PRESERVATION_GATE']
            self.assertEqual('DIVERGENTE', g['ESTADO'])
            self.assertTrue(g['DIVERGENCIA'])
            self.assertEqual('NO', P.monta()['IMPORT_CAN_BE_NEXT_MISSION'],
                             'divergencia no artefato deixou o portao abrir')
        finally:
            P.raw_es = real

    def test_o_catalogo_partial_tambem_barra_o_import(self):
        """IMPORT exige os DOIS. Sem isto, o raw fechado abriria sozinho."""
        import cicatrizes_brasil as C
        alvo = [c for c in C.CICATRIZES if c['ID'] == 'BR-13'][0]
        antes = alvo['EAME_STATUS']
        alvo['EAME_STATUS'] = 'PARTIAL'
        try:
            d = P.monta()
            self.assertEqual('PARTIAL',
                             d['PORTOES']['CATALOG_IMPORT_ENGINEERING_GATE']['ESTADO'])
            self.assertEqual('NO', d['IMPORT_CAN_BE_NEXT_MISSION'])
            self.assertEqual('CLOSED', d['RAW_PRESERVATION_GATE']['ESTADO'],
                             'o raw nao devia mudar: o defeito e do outro lado')
        finally:
            alvo['EAME_STATUS'] = antes
        self.assertEqual('YES', P.monta()['IMPORT_CAN_BE_NEXT_MISSION'])


class TestORawEEstrangeiro(unittest.TestCase):
    """O raw da Espanha e medicao de OUTRA maquina. Nao pode virar nossa."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(RAIZ, 'data', 'samples', 'RAW-GATE-ES.json'),
                  encoding='utf-8') as f:
            cls.r = json.load(f)
        cls.d = P.monta()

    def test_a_conta_fecha_no_denominador(self):
        self.assertEqual(self.r['EXPECTED'],
                         self.r['ALREADY_PRESENT_VERIFIED'] + self.r['FAILED_WITH_REASON'],
                         'os 12 falhos tem arquivo, bytes e sha256: eles PERTENCEM '
                         'ao denominador. Tira-los seria melhorar a taxa apagando o resto')

    def test_declara_que_nao_foi_verificado_daqui(self):
        self.assertEqual('NO', self.r['VERIFICADO_DAQUI'])
        self.assertEqual('EXTERNA', self.r['PROVA'])
        self.assertTrue(self.r['PORQUE_NAO_VERIFICADO_DAQUI'].strip())

    def test_as_tentativas_estao_todas_registradas(self):
        """Tres medicoes, e nem todas concordam. Guardar so a melhor seria escolher.

        A 2a mediu UM a menos que a 1a. A 3a e de outra especie — inventario
        do bucket em vez de contagem de envio — e por isso nao "corrige" as
        outras: responde outra pergunta. As tres ficam.
        """
        t = self.r['DUAS_TENTATIVAS']
        self.assertGreaterEqual(len(t), 3)
        self.assertLess(t[1]['VERIFIED'], t[0]['VERIFIED'],
                        'a segunda tentativa mediu menos, e isso e o registro')
        self.assertIn('INVENT', t[2]['quando'].upper())

    def test_o_diagnostico_externo_tem_causa_nomeada(self):
        """"12 falharam" nao e diagnostico. "HTTP 400 InvalidKey por caractere
        nao-ASCII na object key" e — e e reparavel e verificavel."""
        d = self.r['DIAGNOSTICO_ISOLADO']
        self.assertEqual(400, d['HTTP'])
        self.assertEqual('InvalidKey', d['ERROR'])
        self.assertTrue(d['CAUSA'].strip())

    def test_zero_orfaos_e_uma_medicao_e_nao_um_silencio(self):
        self.assertEqual(0, self.r['ORFAOS_NO_BUCKET'])
        self.assertTrue(self.r['PORQUE_ZERO_ORFAOS_IMPORTA'].strip())

    def test_o_estado_fechou_e_a_conta_fecha_com_ele(self):
        """Este teste ja afirmou OPEN_EXTERNAL_REPAIR, e afirmava certo.

        O operador rodou `storage_preservar.py --enviar --so-ausentes` na
        maquina espanhola e o ultimo asset entrou. O que o teste guarda e a
        coerencia: FECHADO so pode ser YES quando os numeros fecham.
        """
        g = self.d['RAW_PRESERVATION_GATE']
        self.assertEqual('YES', g['FECHADO'])
        self.assertEqual('CLOSED', g['ESTADO'])
        self.assertEqual(g['EXPECTED'], g['VERIFIED'])
        self.assertEqual(0, g['FAILED'])
        self.assertEqual(0, g['ORFAOS_NO_BUCKET'])
        self.assertEqual('NO', g['EXTERNAL_DIAGNOSIS_IN_PROGRESS'])

    def test_fechado_nao_quer_dizer_que_esta_branch_enviou(self):
        """CLOSED aqui e "recebido como prova externa", nao "medido daqui"."""
        g = self.d['RAW_PRESERVATION_GATE']
        self.assertEqual('NO', g['VERIFICADO_DAQUI'])
        self.assertEqual('NO', g['ESTA_BRANCH_EXECUTOU_O_UPLOAD'])
        self.assertEqual('EXTERNA', g['PROVA'])

    def test_o_caminho_ate_zero_nao_foi_apagado(self):
        """12 -> 11 -> 0. Guardar so o final faria o fechamento parecer que
        sempre esteve fechado, e as duas causas medidas sumiriam com ele."""
        h = self.r['OS_12_FALHOS']
        self.assertEqual(0, h['QUANTOS_AGORA'])
        self.assertIn('12', h['HISTORICO'])
        self.assertGreaterEqual(len(h['CAUSAS_MEDIDAS']), 2,
                                'as causas eram duas: object key nao-ASCII e o '
                                'limite de tamanho do bucket')
        self.assertEqual(4, len(self.r['DUAS_TENTATIVAS']))

    def test_o_import_yes_diz_o_que_ele_nao_significa(self):
        self.assertEqual('YES', self.d['IMPORT_CAN_BE_NEXT_MISSION'])
        self.assertIn('PRÓXIMA', self.d['O_QUE_YES_SIGNIFICA'])
        self.assertIsNone(self.d['PORQUE_NAO_IMPORTAR'])

    def test_nenhum_documento_corrente_ainda_afirma_zero_enviado(self):
        """A frase 'zero enviado' era FALSA: 184 estavam la e verificados.

        O campo que PROIBE a frase contem a frase — e um teste ingenuo
        reprovaria justamente na regra. Por isso a busca pula campos cujo
        NOME diz que sao regra, e a testemunha falsa e montada em tempo de
        execucao, para nao existir literalmente no corpus procurado.
        """
        def e_campo_de_regra(nome):
            n = nome.upper()
            return any(m in n for m in ('PORQUE', 'NUNCA', 'NAO_', 'REGRA', 'O_QUE_ISTO_NAO'))

        def varre(obj, caminho=''):
            achados = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if e_campo_de_regra(k):
                        continue
                    achados += varre(v, caminho + '.' + k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    achados += varre(v, '%s[%d]' % (caminho, i))
            elif isinstance(obj, str):
                if 'ZERO' in obj.upper() and 'ENVIAD' in obj.upper():
                    achados.append(caminho)
            return achados

        for artefato in ('RAW-GATE-ES.json', 'PORTOES-EAME.json'):
            with self.subTest(artefato=artefato):
                p = os.path.join(RAIZ, 'data', 'samples', artefato)
                with open(p, encoding='utf-8') as f:
                    self.assertEqual([], varre(json.load(f)),
                                     '%s ainda afirma envio zero' % artefato)

        # A testemunha: montada agora, para provar que a varredura acha algo.
        falsa = {'ESTADO': ' '.join(['zero', 'enviado', 'dos', '196'])}
        self.assertEqual(['.ESTADO'], varre(falsa),
                         'a varredura nao acha nem quando a frase esta la')


if __name__ == '__main__':
    unittest.main()
