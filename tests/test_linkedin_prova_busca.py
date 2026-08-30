"""
Provas da prova pequena. Nenhuma toca a rede; nenhuma usa chave real.

O que precisa ficar preso aqui:
  · o teto de DOIS nomes está no código, não na intenção;
  · a entrada conferida contra o contrato é a MESMA que vai para a execução;
  · "voltou alguém" nunca é "voltou quem eu pedi";
  · a mesma pessoa para consultas diferentes derruba a prova.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import apify_contrato as ac      # noqa: E402
import linkedin_prova_busca as pb  # noqa: E402
import linkedin_schema as ls     # noqa: E402

SCHEMA_BUSCA = {'type': 'object', 'required': ['firstName'],
                'properties': {'firstName': {'type': 'string'},
                               'lastName': {'type': 'string'},
                               'maxItems': {'type': 'integer'}}}


class OTetoEDoCodigo(unittest.TestCase):

    def test_a_prova_e_de_no_maximo_dois_nomes(self):
        self.assertLessEqual(pb.TETO_NOMES, 2)
        self.assertLessEqual(len(pb.NOMES[:pb.TETO_NOMES]), 2)

    def test_os_nomes_da_prova_saem_dos_oito_ja_identificados(self):
        """Nenhum nome NOVO entra por aqui."""
        import linkedin_sensores as sn
        oito = {a['NAME'] for a in sn.ALVOS}
        for a in pb.NOMES:
            self.assertIn(a['NAME'], oito)


class OPortaoDoContratoNaoEDecorativo(unittest.TestCase):

    def test_a_entrada_conferida_e_a_entrada_executada(self):
        """Se fossem duas entradas diferentes, o portão aprovaria uma e gastaria outra.

        Não conto chamadas — contagem quebra a cada edição inocente. Provo o que
        importa: os dois pontos do arquivo que produzem entrada chamam a MESMA
        função, e ela é determinística para o mesmo alvo.
        """
        with open(pb.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertIn('entrada_modelo = entrada_de(NOMES[0])', fonte)   # conferida
        self.assertIn('entrada = entrada_de(alvo)', fonte)              # executada
        self.assertEqual(pb.entrada_de(pb.NOMES[0]), pb.entrada_de(pb.NOMES[0]))

    def test_nenhum_dicionario_de_entrada_e_montado_fora_de_entrada_de(self):
        """Um literal solto com firstName/searchQuery driblaria o portão."""
        with open(pb.__file__, encoding='utf-8') as fh:
            corpo = fh.read().split('def entrada_de', 1)[1].split('def esqueleto', 1)[0]
        with open(pb.__file__, encoding='utf-8') as fh2:
            resto = fh2.read()
        fora = resto.replace(corpo, '')
        for campo in ("'firstName'", "'searchQuery'", "'profileUrl'"):
            self.assertNotIn(campo, fora, campo)

    def test_a_entrada_pretendida_satisfaz_o_contrato_do_ator_de_busca(self):
        props, req = ac.campos_do_schema(SCHEMA_BUSCA)
        r = ac.conferir(props, req, pb.entrada_de(pb.NOMES[0]))
        self.assertEqual(r['STATE'], ac.CONTRACT_MATCH)

    def test_a_entrada_dos_8_runs_perdidos_seria_recusada(self):
        """searchQuery contra este contrato: campo inexistente, gasto recusado."""
        props, req = ac.campos_do_schema(SCHEMA_BUSCA)
        r = ac.conferir(props, req, {'searchQuery': 'Pasquale De Vita CREA', 'maxItems': 3})
        self.assertIn(r['STATE'], (ac.CONTRACT_FIELD_UNKNOWN, ac.CONTRACT_REQUIRED_MISSING))
        self.assertNotEqual(r['STATE'], ac.CONTRACT_MATCH)


class QuemVoltou(unittest.TestCase):

    def test_nome_bate_quando_prenome_e_sobrenome_aparecem(self):
        self.assertTrue(pb.bate_o_nome('Pasquale De Vita', 'Pasquale De Vita'))
        self.assertTrue(pb.bate_o_nome('Nicola Pecchioni', 'Dr. Nicola Pecchioni'))

    def test_o_consultor_de_ciberseguranca_nao_bate_com_nenhum_dos_dois(self):
        """O item que voltou 8 vezes. Se batesse aqui, a prova seria cega."""
        for pedido in ('Pasquale De Vita', 'Nicola Pecchioni'):
            self.assertFalse(pb.bate_o_nome(pedido, 'Sarp Tecimer'))

    def test_sobrenome_igual_e_prenome_diferente_nao_bate(self):
        self.assertFalse(pb.bate_o_nome('Nicola Pecchioni', 'Marco Pecchioni'))

    def test_vazio_nunca_bate(self):
        for a, b in (('', 'x'), ('x', ''), (None, 'x'), ('x', None)):
            self.assertFalse(pb.bate_o_nome(a, b))


class ALeituraDoRaw(unittest.TestCase):

    ITEM = {'basic_info': {'fullname': 'Pasquale De Vita',
                           'headline': 'Ricercatore — CREA',
                           'profile_url': 'https://www.linkedin.com/in/exemplo',
                           'location': {'country': 'Italy'}},
            'experience': [{'company': 'CREA', 'title': 'Ricercatore'}]}

    def test_o_esqueleto_descreve_a_forma_sem_publicar_valor(self):
        e = pb.esqueleto(self.ITEM)
        self.assertEqual(e['basic_info'], 'object')
        self.assertEqual(e['basic_info.fullname'], 'str')
        self.assertEqual(e['experience'], 'array[1]')
        self.assertEqual(e['experience[].company'], 'str')
        texto = json.dumps(e, ensure_ascii=False)
        self.assertNotIn('Pasquale', texto)
        self.assertNotIn('linkedin.com/in/exemplo', texto)

    def test_a_identidade_le_o_nivel_de_aninhamento_certo(self):
        """O bug que custou os 8 runs foi ler o nivel errado. Fica preso aqui."""
        i = pb.identidade(self.ITEM)
        self.assertEqual(i['NAME'], 'Pasquale De Vita')
        self.assertTrue(i['PROFILE_URL'].startswith('https://'))

    def test_local_declarado_no_perfil_nunca_vira_fato_geografico(self):
        i = pb.identidade(self.ITEM)
        self.assertIn('Italy', i['PROFILE_DECLARED_LOCATION'])
        self.assertTrue(i['FACT_LOCATION'].startswith('NOT_KNOWN'))

    def test_item_sem_a_forma_conhecida_nao_vira_pessoa(self):
        i = pb.identidade({'algo': 'outro'})
        self.assertEqual(i['NAME'], 'NÃO SEI')
        self.assertEqual(ls.detectar_schema({'algo': 'outro'}), ls.UNKNOWN_SCHEMA)


class OVeredito(unittest.TestCase):

    def test_o_veredito_e_sobre_a_rota_e_nunca_sobre_o_campo(self):
        with open(pb.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertIn('ROUTE_PROVED', fonte)
        self.assertIn('PROVA DE ROTA ≠ MEDIDA DE SINAL', pb.__doc__)
        # Nenhum veredito deste arquivo pode afirmar sinal medido.
        for proibido in ('HUMAN_SENSOR_LAYER_PROVED', 'SIGNAL_MEASURED',
                         'ITALY OPPORTUNITY'):
            self.assertNotIn(proibido, fonte)


if __name__ == '__main__':
    unittest.main()
