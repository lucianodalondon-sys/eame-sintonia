"""
Provas da prova pequena. Nenhuma toca a rede; nenhuma usa chave real.

O que precisa ficar preso aqui:
  · o teto de DOIS nomes está no código, não na intenção;
  · a entrada conferida contra o contrato é a MESMA que vai para a execução;
  · "voltou alguém" nunca é "voltou quem eu pedi";
  · a mesma pessoa para consultas diferentes derruba a prova.
"""
import gzip
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import apify_contrato as ac      # noqa: E402
import linkedin_prova_busca as pb  # noqa: E402
import linkedin_schema as ls     # noqa: E402

# O contrato REAL de harvestapi~linkedin-profile-search-by-name, lido de graca
# em 2026-08-30 (run 33320039453). Copiado do que o ator publica, nao inventado:
# uma fixture inventada provaria a minha ideia do contrato, nao o contrato.
SCHEMA_BUSCA = {
    'type': 'object',
    'required': ['profileScraperMode'],
    'properties': {
        'currentCompanies': {'type': 'array'}, 'currentJobTitles': {'type': 'array'},
        'firstName': {'type': 'string', 'prefill': 'Satya'},
        'lastName': {'type': 'string', 'prefill': 'Nadella'},
        'industryIds': {'type': 'array'}, 'locations': {'type': 'array'},
        'maxItems': {'type': 'integer'}, 'maxPages': {'type': 'integer'},
        'pastCompanies': {'type': 'array'}, 'schools': {'type': 'array'},
        'strictSearch': {'type': 'boolean'},
        'profileScraperMode': {'type': 'string', 'prefill': 'Full',
                               'enum': ['Short', 'Full', 'Full + email search']},
    },
}


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
        self.assertIn('entrada_modelo = entrada_de(lista[0])', fonte)   # conferida
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

    def test_o_campo_obrigatorio_do_contrato_real_esta_na_entrada(self):
        """profileScraperMode e obrigatorio — medido no contrato em 2026-08-30.

        Sem ele a entrada seria recusada pelo portao, e a prova nunca rodaria.
        """
        self.assertIn('profileScraperMode', pb.entrada_de(pb.NOMES[0]))
        self.assertIn(pb.MODO, ('Short', 'Full'))

    def test_a_prova_nunca_pede_busca_de_email(self):
        """'Full + email search' colheria e-mail de quem nao pediu nada a ninguem.

        A pergunta desta missao — as vozes humanas acrescentam sinal de campo? —
        se responde com nome, titulo e instituicao. Endereco pessoal nao entra.
        """
        self.assertNotEqual(pb.MODO, pb.MODO_PROIBIDO)
        for alvo in pb.NOMES:
            self.assertNotIn(pb.MODO_PROIBIDO, pb.entrada_de(alvo).values())

    def test_a_prova_nao_filtra_por_local_nem_por_empresa(self):
        """Filtrar transformaria 'declarou outro pais' em NOT_FOUND.

        NOT_FOUND != DOES NOT EXIST. A comparacao com instituicao e feita depois,
        do meu lado, sobre o que voltou.
        """
        e = pb.entrada_de(pb.NOMES[0])
        self.assertNotIn('locations', e)
        self.assertNotIn('currentCompanies', e)

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

    # Contrato PROFILE_DETAIL_V1_BASIC_INFO. `location.full` e o campo real —
    # a versao anterior desta fixture escrevia `location.country`, que o parser
    # nao le, e o teste passava assim mesmo porque a leitura da prova era outra.
    # Duas leituras deixavam uma fixture errada de pe.
    ITEM = {'basic_info': {'fullname': 'Pasquale De Vita',
                           'headline': 'Ricercatore — CREA',
                           'profile_url': 'https://www.linkedin.com/in/exemplo',
                           'location': {'full': 'Roma, Italy',
                                        'country_code': 'IT'}},
            'experience': [{'company': 'CREA', 'title': 'Ricercatore'}]}

    # Contrato PROFILE_SEARCH_V1_SHORT — a forma REAL medida em 2026-08-30
    # (run 33320142206). Nao tem basic_info, e o titulo se chama `position`.
    ITEM_BUSCA = {'id': 'ACoAAA', 'linkedinUrl': 'https://www.linkedin.com/in/exemplo',
                  'location': {'linkedinText': 'Foggia, Puglia, Italia'},
                  'name': 'Pasquale De Vita', 'position': 'Ricercatore presso CREA',
                  'publicIdentifier': 'exemplo'}

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

    def test_o_contrato_de_BUSCA_e_lido_pelo_campo_certo(self):
        """`position`, nao `headline`. Ler o campo errado devolveria NAO SEI
        para um titulo que estava la — o mesmo defeito dos 8 runs, de novo."""
        i = pb.identidade(self.ITEM_BUSCA)
        self.assertEqual(i['SCHEMA'], ls.SCHEMA_BUSCA_V1)
        self.assertEqual(i['NAME'], 'Pasquale De Vita')
        self.assertEqual(i['HEADLINE'], 'Ricercatore presso CREA')
        self.assertIn('Foggia', i['PROFILE_DECLARED_LOCATION'])
        self.assertTrue(i['FACT_LOCATION'].startswith('NOT_KNOWN'))

    def test_os_dois_contratos_do_mesmo_fornecedor_nao_se_confundem(self):
        self.assertEqual(ls.detectar_schema(self.ITEM), ls.SCHEMA_V1)
        self.assertEqual(ls.detectar_schema(self.ITEM_BUSCA), ls.SCHEMA_BUSCA_V1)
        self.assertNotEqual(ls.SCHEMA_V1, ls.SCHEMA_BUSCA_V1)

    def test_sobrenome_abreviado_pela_plataforma_e_um_terceiro_estado(self):
        """"Pasquale D." voltou de verdade. Nao e outra pessoa nem e a mesma."""
        self.assertTrue(pb.nome_truncado('Pasquale D.'))
        self.assertFalse(pb.nome_truncado('Pasquale De Vita'))
        self.assertFalse(pb.nome_truncado('Sarp Tecimer'))
        # e continua NAO batendo: truncado nao vira confirmado por conveniencia
        self.assertFalse(pb.bate_o_nome('Pasquale De Vita', 'Pasquale D.'))

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


class AReleituraDoRawJaPago(unittest.TestCase):
    """Corrigir o MEU parser não pode custar dinheiro de novo.

    O bruto é gravado antes de qualquer interpretação exatamente para isto. Se a
    correção exigisse novo run, `DINHEIRO GASTO ≠ DADO PRESERVADO` viraria frase
    de efeito em vez de garantia.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.antigo = pb.RAW_DIR
        pb.RAW_DIR = self.dir

    def tearDown(self):
        pb.RAW_DIR = self.antigo
        shutil.rmtree(self.dir, ignore_errors=True)

    def _grava(self, nome_arquivo, itens):
        caminho = os.path.join(self.dir, nome_arquivo)
        with gzip.open(caminho, 'wt', encoding='utf-8') as fh:
            json.dump(itens, fh)

    def test_o_alvo_volta_do_nome_do_arquivo_e_nao_da_ordem_da_lista(self):
        self._grava('IT-LI-PROVA-Nicola-Pecchioni.raw.json.gz',
                    [{'name': 'Nicola Pecchioni', 'linkedinUrl': 'https://x/1',
                      'position': 'CREA'}])
        itens = pb.reler_raw()
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]['_ALVO'], 'Nicola Pecchioni')

    def test_a_releitura_nao_abre_execucao(self):
        with open(pb.__file__, encoding='utf-8') as fh:
            corpo = fh.read().split('def reler_raw', 1)[1].split('def ler_itens', 1)[0]
        self.assertNotIn('coletor.executar', corpo)
        self.assertNotIn('executar_com_pool', corpo)

    def test_raw_ilegivel_vira_estado_e_nunca_some(self):
        """Um .gz corrompido não pode virar 'esse nome não voltou nada'."""
        caminho = os.path.join(self.dir, 'IT-LI-PROVA-Alguem.raw.json.gz')
        with open(caminho, 'wb') as fh:
            fh.write(b'nao e gzip')
        itens = pb.reler_raw()
        self.assertEqual(len(itens), 1)
        self.assertIn('_RAW_UNREADABLE', itens[0])

    def test_sem_raw_nenhum_a_releitura_nao_inventa_resultado(self):
        self.assertEqual(pb.reler_raw(), [])

    def test_a_releitura_corrigida_le_o_titulo_que_o_parser_antigo_perdia(self):
        self._grava('IT-LI-PROVA-Pasquale-De-Vita.raw.json.gz',
                    [{'name': 'Pasquale De Vita', 'linkedinUrl': 'https://x/2',
                      'position': 'Ricercatore CREA',
                      'location': {'linkedinText': 'Foggia'}},
                     {'name': 'Pasquale D.', 'linkedinUrl': 'https://x/3',
                      'position': 'Altro'}])
        out = {}
        pb.ler_itens(pb.reler_raw(), out)
        estados = {x['NAME']: x for v in out['RETURNED_BY_NAME'].values() for x in v}
        self.assertEqual(estados['Pasquale De Vita']['HEADLINE'], 'Ricercatore CREA')
        self.assertEqual(estados['Pasquale De Vita']['NAME_STATE'], 'NAME_MATCHES')
        self.assertEqual(estados['Pasquale D.']['NAME_STATE'], 'TRUNCATED_BY_PLATFORM')

    def test_dois_retornos_que_batem_no_nome_e_so_um_e_a_pessoa(self):
        """Nome igual nao resolve; a instituicao no titulo resolve."""
        self._grava('IT-LI-PROVA-Nicola-Pecchioni.raw.json.gz',
                    [{'name': 'Nicola Pecchioni', 'linkedinUrl': 'https://x/4',
                      'position': 'Ricercatore CREA'},
                     {'name': 'Gian Nicola Pecchioni', 'linkedinUrl': 'https://x/5',
                      'position': 'Commerciante presso Bagni Aurelia'}])
        out = {}
        pb.ler_itens(pb.reler_raw(), out)
        self.assertEqual(out['NAMES_WITH_MORE_THAN_ONE_MATCH'], ['Nicola Pecchioni'])
        alvo = out['IDENTITY_BY_TARGET']['Nicola Pecchioni']
        self.assertEqual(alvo['STATE'], pb.IDENTITY_CONFIRMED)
        estados = {c['NAME']: c['IDENTITY_STATE'] for c in alvo['BY_CANDIDATE']}
        self.assertEqual(estados['Nicola Pecchioni'], pb.IDENTITY_CONFIRMED)
        self.assertEqual(estados['Gian Nicola Pecchioni'], pb.IDENTITY_MISMATCH)


class OTituloDecideEONomeNao(unittest.TestCase):
    """O achado que justifica este portao existir, preso como prova.

    Medido em 2026-08-30 sobre o RAW ja pago: a busca por "Pasquale De Vita"
    devolveu tres pessoas de nome igual — presidente da Unione Petrolifera,
    vendedor de esquadrias, diretor de TI. Nenhuma e o pesquisador do CREA.
    Um portao que parasse no nome teria promovido o presidente da associacao do
    petroleo a pesquisador de trigo duro.
    """

    ALVO = {'NAME': 'Pasquale De Vita',
            'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali'}

    def _estado(self, nome, titulo):
        return pb.conferir_identidade(self.ALVO, {'NAME': nome, 'HEADLINE': titulo})[0]

    def test_o_presidente_da_uniao_do_petroleo_nao_vira_pesquisador(self):
        self.assertEqual(
            self._estado('Pasquale De Vita', 'presidente presso Unione Petrolifera'),
            pb.IDENTITY_MISMATCH)

    def test_o_vendedor_de_esquadrias_tampouco(self):
        self.assertEqual(
            self._estado('Pasquale De vita', 'Mi chiamano il "Boss degli Infissi"'),
            pb.IDENTITY_MISMATCH)

    def test_o_diretor_de_ti_tampouco(self):
        self.assertEqual(
            self._estado('Pasquale De Vita', 'IT Director at Asl Avellino'),
            pb.IDENTITY_MISMATCH)

    def test_o_titulo_que_nomeia_a_instituicao_confirma(self):
        self.assertEqual(
            self._estado('Pasquale De Vita', 'Ricercatore presso CREA — Cerealicoltura'),
            pb.IDENTITY_CONFIRMED)

    def test_o_titulo_no_dominio_sem_instituicao_e_apenas_plausivel(self):
        """"Crop Genomics" e do ramo certo — e ainda assim nao prova quem e."""
        self.assertEqual(self._estado('Pasquale De Vita', 'Crop Genomics'),
                         pb.IDENTITY_PLAUSIBLE)

    def test_titulo_ausente_e_ignorancia_e_nao_divergencia(self):
        self.assertEqual(self._estado('Pasquale De Vita', ''), pb.IDENTITY_NOT_ENOUGH)
        self.assertEqual(self._estado('Pasquale De Vita', 'NÃO SEI'),
                         pb.IDENTITY_NOT_ENOUGH)

    def test_nome_truncado_e_ignorancia_e_nao_divergencia(self):
        self.assertEqual(self._estado('Pasquale D.', 'IT Director at Asl Avellino'),
                         pb.IDENTITY_NOT_ENOUGH)

    def test_todos_MISMATCH_nao_significa_que_a_pessoa_nao_exista(self):
        """Pedi cinco, vieram tres. O que nao veio nao foi negado."""
        self.assertEqual(pb.resolver_alvo([pb.IDENTITY_MISMATCH] * 3),
                         'NOT_FOUND_IN_RESULTS')
        self.assertEqual(pb.resolver_alvo([]), 'NOT_FOUND_IN_RESULTS')
        with open(pb.__file__, encoding='utf-8') as fh:
            self.assertIn('NOT_FOUND_IN_RESULTS ≠ NOT_ON_PLATFORM ≠ DOES_NOT_EXIST',
                          fh.read())

    def test_um_candidato_confirmado_vence_os_mismatches(self):
        self.assertEqual(
            pb.resolver_alvo([pb.IDENTITY_MISMATCH, pb.IDENTITY_CONFIRMED]),
            pb.IDENTITY_CONFIRMED)

    def test_plausivel_nunca_e_promovido_a_confirmado(self):
        self.assertEqual(
            pb.resolver_alvo([pb.IDENTITY_PLAUSIBLE, pb.IDENTITY_PLAUSIBLE]),
            pb.IDENTITY_PLAUSIBLE)


class OTetoDaMissaoNaoSobe(unittest.TestCase):
    """`--todos` mede mais dos MESMOS oito. Não descobre nome novo."""

    def test_a_prova_continua_sendo_de_dois(self):
        self.assertEqual(len(pb.alvos()), 2)

    def test_a_missao_inteira_sao_os_oito_ja_identificados(self):
        import linkedin_sensores as sn
        todos = pb.alvos(todos=True)
        self.assertEqual(len(todos), 8)
        self.assertLessEqual(len(todos), pb.TETO_ALVOS_MISSAO)
        oito = {a['NAME'] for a in sn.ALVOS}
        for a in todos:
            self.assertIn(a['NAME'], oito, 'nome novo entrou por esta porta')

    def test_nenhum_alvo_aparece_duas_vezes(self):
        nomes = [a['NAME'] for a in pb.alvos(todos=True)]
        self.assertEqual(len(nomes), len(set(nomes)))

    def test_todo_alvo_tem_entrada_valida_contra_o_contrato_real(self):
        props, req = ac.campos_do_schema(SCHEMA_BUSCA)
        for a in pb.alvos(todos=True):
            r = ac.conferir(props, req, pb.entrada_de(a))
            self.assertEqual(r['STATE'], ac.CONTRACT_MATCH, a['NAME'])

    def test_todo_alvo_carrega_instituicao_para_o_portao_de_identidade(self):
        """Sem instituição no alvo, CONFIRMED seria inalcançável e todo mundo
        cairia em PLAUSIBLE — o portão viraria enfeite."""
        for a in pb.alvos(todos=True):
            self.assertTrue(a.get('INSTITUTION'), a['NAME'])
            tokens = [w for w in a['INSTITUTION'].lower().split() if len(w) > 3]
            self.assertTrue(tokens, a['NAME'])
