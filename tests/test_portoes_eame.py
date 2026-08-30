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

    def test_um_raw_gate_fechado_ainda_nao_bastaria_sozinho(self):
        """IMPORT exige o portao do catalogo E o raw. Nao um so."""
        real = P.raw_es
        P.raw_es = lambda: dict(real(), ALREADY_PRESENT_VERIFIED=196,
                                FAILED_WITH_REASON=0, ESTADO='CLOSED')
        try:
            self.assertEqual('YES', P.monta()['IMPORT_CAN_BE_NEXT_MISSION'],
                             'com o raw fechado e o catalogo READY, IMPORT deveria '
                             'poder ser SIM — se nao muda, a conta nao le o raw')
        finally:
            P.raw_es = real
        self.assertEqual('NO', P.monta()['IMPORT_CAN_BE_NEXT_MISSION'])


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

    def test_o_estado_nao_e_fechado_e_nem_finge_ser(self):
        g = self.d['RAW_PRESERVATION_GATE']
        self.assertEqual('NO', g['FECHADO'])
        self.assertEqual('OPEN_EXTERNAL_REPAIR', g['ESTADO'])
        self.assertEqual('YES', g['EXTERNAL_DIAGNOSIS_IN_PROGRESS'])

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
