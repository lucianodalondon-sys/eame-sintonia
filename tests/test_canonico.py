#!/usr/bin/env python3
"""
Provas de consistência dos documentos canônicos.

Um estado antigo não pode sobreviver num documento canônico e contradizer o estado
final. Estes testes comparam o que os documentos DECLARAM com o que eles CONTÊM.
"""
import json, os, re, unittest
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'docs')

MARCADOR = re.compile(r'<!--/?M:?[A-Z0-9_]*-->')


def rd(*p):
    """Lê um documento canônico, removendo os marcadores de sincronização.

    `<!--M:NOME-->98<!--/M-->` é andaime de `scripts/metricas_canonicas.py --sync`.
    Para quem lê o documento — e para estes testes — o que existe ali é o número.
    """
    with open(os.path.join(D, *p), encoding='utf-8') as f:
        return MARCADOR.sub('', f.read())

FONTES = rd('fontes', 'ATLAS-DE-FONTES-EAME.md')
CAPS = rd('capacidades', 'ATLAS-DE-CAPACIDADES-EAME.md')
CRUZ = rd('cruzamentos', 'MATRIZ-DE-CRUZAMENTOS-EAME.md')
FERR = rd('ferramentas', 'CATALOGO-DE-FERRAMENTAS-EAME.md')
CASOS = rd('apresentacao', 'CASOS-PARA-APRESENTACAO.md')

SOURCE_ID = re.compile(r'^SOURCE_ID:\s+(\S[^\n#]*)', re.M)


def source_ids():
    """Todos os SOURCE_IDs reais, expandindo fichas que cobrem mais de uma fonte."""
    ids = set()
    for m in SOURCE_ID.finditer(FONTES):
        raw = m.group(1).strip()
        if raw.startswith('#') or '<' in raw:      # linha de template
            continue
        raw = re.sub(r'\(.*?\)', '', raw)
        for part in re.split(r'[·/]', raw):
            part = part.strip()
            if re.fullmatch(r'(EU|FR|ES|IT)-T\d{1,2}-\d{3}', part):
                ids.add(part)
    # fontes testadas que só aparecem em tabela de "não alcançadas"
    for m in re.finditer(r'\|\s*((?:EU|FR|ES|IT)-T\d{1,2}-\d{3})\s*\|', FONTES):
        ids.add(m.group(1))
    return ids


class TestContagens(unittest.TestCase):
    """O número declarado tem de ser o número real."""

    def test_fontes_placar_bate_com_o_declarado(self):
        topo = re.search(r'\*\*(\d+) fontes registradas\*\* \((\d+) GREEN, (\d+) YELLOW, (\d+) NÃO SEI\)', FONTES)
        self.assertIsNotNone(topo, 'cabeçalho do atlas de fontes sem contagem declarada')
        tot = re.search(r'\| \*\*Total\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|', FONTES)
        self.assertIsNotNone(tot, 'placar sem linha de Total')
        g, y, r, ns, t = (int(x) for x in tot.groups())
        self.assertEqual(int(topo.group(1)), t, 'cabeçalho e placar discordam no total')
        self.assertEqual(int(topo.group(2)), g, 'cabeçalho e placar discordam em GREEN')
        self.assertEqual(int(topo.group(3)), y, 'cabeçalho e placar discordam em YELLOW')
        self.assertEqual(int(topo.group(4)), ns, 'cabeçalho e placar discordam em NÃO SEI')
        self.assertEqual(g + y + r + ns, t, 'as parcelas do placar não somam o total')

    def test_linhas_por_pais_somam_o_total(self):
        """Um total certo com linhas erradas continua sendo um documento errado."""
        linhas = re.findall(r'^\| (EUROPE|FRANCE|SPAIN|ITALY) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$',
                            FONTES, re.M)
        self.assertEqual(4, len(linhas), 'placar sem as quatro linhas de recorte')
        tot = re.search(r'\| \*\*Total\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|', FONTES)
        alvo = [int(x) for x in tot.groups()]
        for col in range(5):
            soma = sum(int(l[col + 1]) for l in linhas)
            with self.subTest(coluna=('GREEN', 'YELLOW', 'RED', 'NÃO SEI', 'Total')[col]):
                self.assertEqual(alvo[col], soma,
                                 'as linhas por país não somam a linha de Total')
        for l in linhas:
            with self.subTest(pais=l[0]):
                self.assertEqual(int(l[5]), sum(int(x) for x in l[1:5]),
                                 f'a linha de {l[0]} não soma o próprio total')

    def test_total_de_fontes_bate_com_os_source_ids_reais(self):
        self.assertEqual(len(source_ids()),
                         int(re.search(r'\| \*\*Total\*\* \| .*?\| \*\*(\d+)\*\* \|$', FONTES, re.M).group(1)),
                         'o total declarado não bate com os SOURCE_IDs presentes no documento')

    def test_capacidades_declaradas_batem_com_as_fichas(self):
        secoes = re.findall(r'^### (CAP-\d+)', CAPS, re.M)
        comprovadas = len(re.findall(r'^CONFIDENCE:\s+COMPROVADO', CAPS, re.M))
        declarado = int(re.search(r'\*\*(\d+) capacidades COMPROVADAS\*\*', CAPS).group(1))
        placar = int(re.search(r'\| COMPROVADO \| (\d+) \|', CAPS).group(1))
        self.assertEqual(len(secoes), len(set(secoes)), 'há CAP duplicado')
        self.assertEqual(declarado, placar, 'cabeçalho e placar de capacidades discordam')
        self.assertEqual(declarado, comprovadas,
                         'o número declarado não bate com as fichas CONFIDENCE: COMPROVADO')

    def test_casos_declarados_batem_com_as_secoes_e_a_tabela(self):
        secoes = re.findall(r'^### (CASE-\d+)', CASOS, re.M)
        linhas = re.findall(r'^\| (CASE-\d+)', CASOS, re.M)
        declarado = int(re.search(r'\*\*(\d+) casos registrados\*\*', CASOS).group(1))
        self.assertEqual(sorted(secoes), sorted(linhas),
                         'a tabela de casos e as seções não listam os mesmos CASE_ID')
        self.assertEqual(declarado, len(secoes), 'número de casos declarado ≠ seções existentes')

    def test_ferramentas_declaradas_batem_com_as_fichas(self):
        fichas = re.findall(r'^### (.+?) — `(.+?)`', FERR, re.M)
        declarado = int(re.search(r'\*\*(\d+) fichas\*\*', FERR).group(1))
        self.assertEqual(declarado, len(fichas), 'número de fichas de ferramenta declarado ≠ real')


class TestCruzamentos(unittest.TestCase):
    """A tabela de candidatos não pode contradizer a ficha do cruzamento."""

    def classes(self):
        out = {}
        for m in re.finditer(r'^### (X-\d+)[^\n]*\n(.*?)(?=^### |\Z)', CRUZ, re.M | re.S):
            c = re.search(r'^CLASS:\s+(.+)$', m.group(2), re.M)
            if c:
                out.setdefault(m.group(1), []).append(
                    re.sub(r'[*`]', '', c.group(1)).split('—')[0].split('(')[0].strip())
        return out

    def test_placar_de_cruzamentos_bate(self):
        cl = {k: v[0] for k, v in self.classes().items()}
        cont = Counter(cl.values())
        for classe, chave in [('COMPROVADO', 'COMPROVADO'), ('PARCIAL', 'PARCIAL'),
                              ('NÃO COMPÕE', 'NÃO COMPÕE')]:
            m = re.search(rf'\| {re.escape(chave)} \| (\d+) \|', CRUZ)
            self.assertIsNotNone(m, f'placar sem linha para {chave}')
            self.assertEqual(cont[classe], int(m.group(1)),
                             f'placar de {chave} não bate com as fichas CLASS:')

    def test_tabela_de_candidatos_nao_contradiz_a_ficha(self):
        cl = {k: v[0] for k, v in self.classes().items()}
        for m in re.finditer(r'^\| (X-\d+) \| [^|]+ \| (.+?) \|$', CRUZ, re.M):
            xid, txt = m.group(1), re.sub(r'[*]', '', m.group(2))
            if xid not in cl:
                continue
            with self.subTest(cruzamento=xid):
                self.assertIn(cl[xid].split()[0], txt,
                              f'{xid}: a tabela diz "{txt}" mas a ficha diz "{cl[xid]}"')

    def test_x001_nao_afirma_mais_que_falta_disease_alert(self):
        """O componente DISEASE existe desde T3; o motivo antigo não pode sobreviver."""
        linha = re.search(r'^\| X-001 \|.*$', CRUZ, re.M).group(0)
        self.assertNotIn('falta DISEASE ALERT', linha,
                         'estado antigo de X-001 sobreviveu na tabela de candidatos')


if __name__ == '__main__':
    unittest.main(verbosity=2)


PILOTO = os.path.join(D, 'piloto')


def piloto(*p):
    # marcadores de sincronizacao do ledger sao invisiveis para asercao de conteudo,
    # igual em rd(). Sem isto, um numero que ganha dono no ledger quebra o teste que
    # verifica o proprio numero.
    with open(os.path.join(PILOTO, *p), encoding='utf-8') as f:
        return MARCADOR.sub('', f.read())


class TestNumerosEntreDocumentos(unittest.TestCase):
    """Um case não pode dizer 8 produtos e outro documento dizer 7.

    Estes testes procuram o MESMO número em documentos diferentes. Se um for
    corrigido e o outro não, o teste reprova — que é exatamente o objetivo.
    """

    DOCS = {}

    @classmethod
    def setUpClass(cls):
        cls.DOCS = {
            'casos': CASOS,
            'pacote': piloto('PACOTE-DE-MATERIA-PRIMA-EAME.md'),
            'design': piloto('ENTRADA-PARA-CLAUDE-DESIGN.md'),
            'benchmark': piloto('ASK-SINTONIA-BENCHMARK.md'),
            'source_pack': piloto('SOURCE-PACK-PILOTO.md'),
            'claims': piloto('O-QUE-PODEMOS-DIZER.md'),
            'identidade': rd('regras', 'MODELO-DE-IDENTIDADE-EAME.md'),
            'change': rd('regras', 'REGUA-DE-CHANGE-EVENT-EAME.md'),
            'freeze': rd('descoberta', 'FREEZE-DA-BASE-DO-PILOTO.md'),
            'operacao': rd('operacao', 'PROVA-DE-RECORRENCIA-MISSAO-08.md'),
            'corrente': rd('piloto', 'EXTERNAL-ONLY-BUSINESS-CASE.md'),
        }

    def _todos_dizem(self, docs, padrao, rotulo):
        for nome in docs:
            with self.subTest(documento=nome, valor=rotulo):
                self.assertRegex(self.DOCS[nome], padrao,
                                 f'{nome} não confirma "{rotulo}"')

    def test_produtos_prothioconazol_franca(self):
        self._todos_dizem(['pacote', 'design'], r'\b77\b', '77 produtos FR')

    def test_produtos_prothioconazol_italia(self):
        self._todos_dizem(['pacote', 'design'], r'\b85\b', '85 produtos IT')

    def test_adama_tres_na_franca_cinco_na_italia(self):
        for nome in ('pacote', 'design'):
            with self.subTest(documento=nome):
                self.assertRegex(self.DOCS[nome], r'ADAMA[^\n]{0,12}3\b|3 produtos|`ADAMA 3`',
                                 'não confirma 3 produtos ADAMA na França')
                self.assertRegex(self.DOCS[nome], r'ADAMA[^\n]{0,12}5\b|5 produtos|`ADAMA 5`',
                                 'não confirma 5 produtos ADAMA na Itália')

    def test_os_cinco_produtos_italianos_sao_nomeados_igual(self):
        nomes = ('MAGANIC', 'MAXENTIS', 'AVASTEL', 'SORATEL', 'KOJAMI')
        for doc in ('pacote', 'benchmark'):
            for n in nomes:
                with self.subTest(documento=doc, produto=n):
                    self.assertIn(n, self.DOCS[doc], f'{doc} não cita {n}')

    def test_benchmark_placar_identico_em_todo_lugar(self):
        """O placar declarado vem do JSON, não de um número escrito à mão."""
        with open(os.path.join(ROOT, 'data', 'samples',
                               'ASK-SINTONIA-benchmark.json'), encoding='utf-8') as f:
            tot = json.load(f)['totals']
        ans, ref = tot['ANSWERABLE'], tot['CORRECT REFUSAL']
        self.assertEqual(tot.get('WRONG ANSWER', 0), 0, 'o benchmark tem resposta errada')
        for nome in ('pacote', 'design', 'benchmark'):
            with self.subTest(documento=nome):
                self.assertRegex(self.DOCS[nome], rf'\b{ans}\b', f'placar: {ans} respondidas')
                self.assertRegex(self.DOCS[nome], rf'\b{ref}\b', f'placar: {ref} recusadas')
                self.assertRegex(self.DOCS[nome], r'\b0\b', 'placar: 0 erradas')

    def test_es01717_tratado_com_as_entidades_certas(self):
        """A concessionária nunca pode aparecer como titular."""
        casos = self.DOCS['casos']
        self.assertIn('ES-01717', casos)
        self.assertRegex(casos, r'(?i)concession[áa]ria',
                         'o case não distingue concessionária de titular')
        for linha in re.findall(r'^#{1,4} .*$', casos, re.M) + re.findall(r'^\|.*$', casos, re.M):
            with self.subTest(linha=linha[:60]):
                self.assertNotRegex(linha, r'(?i)Syngenta.{0,24}titular',
                                    'declara a Syngenta como titular do registro')

    def test_titular_e_fabricante_espanhois_estao_em_fonte_primaria(self):
        """MISSÃO 07: a ficha oficial foi lida. O que era ressalva virou fato.

        O teste anterior exigia a palavra "secundária" nestes documentos. Ele foi
        substituído, não apagado: a ressalva tinha de cair quando a fonte abrisse, e o
        que passa a ser obrigatório é o oposto — que a atribuição esteja marcada como
        PRIMÁRIA e que o erro da fonte secundária continue registrado.
        """
        for nome in ('casos', 'pacote', 'identidade'):
            with self.subTest(documento=nome):
                self.assertRegex(self.DOCS[nome], r'(?i)prim[áa]ria',
                                 'a atribuição de titular não está marcada como primária')
        self.assertIn('ADAMA Agricultural Solutions Ltd.', self.DOCS['identidade'],
                      'o fabricante primário não está na ficha de identidade')
        self.assertIn('MAKHTESHIM', self.DOCS['identidade'],
                      'o erro da fonte secundária foi apagado em vez de registrado')

    def test_o_modelo_de_identidade_mantem_papeis_distintos(self):
        """ROLE_A != ROLE_B mesmo quando VALUE_A == VALUE_B — e isso é medido."""
        ident = self.DOCS['identidade']
        for entidade in ('REGISTRATION_ID', 'REFERENCE_PRODUCT', 'REFERENCE_HOLDER',
                         'MANUFACTURER', 'COMMON_DENOMINATION', 'CONCESSIONAIRE'):
            with self.subTest(entidade=entidade):
                self.assertIn(entidade, ident, f'a entidade {entidade} sumiu do modelo')
        self.assertRegex(ident, r'ROLE_A\s*≠\s*ROLE_B',
                         'a regra de papéis distintos não está escrita')
        self.assertIn('165', ident, 'a medida da coincidência de papel não está declarada')

    def test_as_frases_retiradas_na_missao_07_nao_reaparecem(self):
        """2,45x e "metade do mercado" caíram. Títulos e tabelas não podem afirmá-las.

        Uma linha que **declara a retirada** é registro, não afirmação — e o registro é
        obrigatório (ver o teste seguinte). Por isso a linha que contém "retirad..." é
        pulada: ela existe justamente para dizer que a frase não vale mais.
        """
        alvo = re.compile(r'(?i)(2,45\s*[x×]|metade do mercado|50,7\s*%)')
        registro = re.compile(r'(?i)retirad[ao]')
        for nome, txt in self.DOCS.items():
            for linha in (re.findall(r'^#{1,4} .*$', txt, re.M)
                          + re.findall(r'^\|.*$', txt, re.M)):
                if registro.search(linha):
                    continue
                with self.subTest(documento=nome, linha=linha[:60]):
                    self.assertNotRegex(linha, alvo, 'uma frase retirada voltou como afirmação')

    def test_a_retirada_da_frase_do_mercado_continua_registrada(self):
        self.assertRegex(self.DOCS['claims'], r'(?i)retirado na MISS[ÃA]O 07',
                         'a retirada de "2,45x o mercado" sumiu do registro')

    def test_denominacoes_batem_com_a_amostra_medida(self):
        """Os números publicados vêm do arquivo de medida, não da memória."""
        with open(os.path.join(ROOT, 'data', 'samples',
                               'ES-T4-004-denominaciones-medida.json'), encoding='utf-8') as f:
            m = json.load(f)
        pares = [(m['DENOMINATION_ROWS'], '1.786'),
                 (m['DISTINCT_REGISTRATIONS_LISTED'], '720'),
                 (m['IN_FORCE_WITH_MORE_THAN_ONE'], '363')]
        for valor, escrito in pares:
            with self.subTest(valor=valor):
                self.assertEqual(f'{valor:,}'.replace(',', '.'), escrito,
                                 'a amostra mudou e o documento não')
                self.assertIn(escrito, self.DOCS['casos'],
                              f'CASE-015 não publica {escrito}')

    def test_a_regua_de_change_event_separa_provado_de_possivel(self):
        regua = self.DOCS['change']
        self.assertRegex(regua, r'(?i)POSS[ÍI]VEL, n[ãa]o provado',
                         'a régua não separa o que é detectável hoje do que só é possível')
        self.assertRegex(regua, r'(?i)OFFICIAL RECORD NAME CHANGED',
                         'a régua não diz o que a renomeação prova')
        for proibido in ('relançamento comercial', 'estratégia de marca'):
            with self.subTest(leitura=proibido):
                self.assertIn(proibido, regua, f'a régua não proíbe "{proibido}"')

    def test_o_total_de_testes_declarado_vem_da_suite(self):
        """O número de provas não pode ser escrito à mão.

        A MISSÃO 06 declarou 38/38 num commit e 37/37 num relatório, e a suíte tinha 37.
        Nenhum dos dois números era derivado. Este teste conta a suíte de verdade e
        exige que o documento de congelamento diga esse número.
        """
        suite = unittest.defaultTestLoader.discover(os.path.dirname(os.path.abspath(__file__)))
        n = suite.countTestCases()
        # O documento escreve o milhar com ponto, e e assim que o `--sync` o escreve.
        # Exigir `1309` cru reprovava um documento CERTO que publicava `1.309`: o teste
        # cobrava um formato que o dono do numero nunca produz. `FORMATO != VALOR`.
        escrito = f'{n:,}'.replace(',', r'\.')
        self.assertRegex(self.DOCS['corrente'], rf'TESTES_REAIS\s*=\s*{escrito}\b',
                         f'o documento CORRENTE não declara TESTES_REAIS = {n:,}'.replace(',', '.'))

    def test_o_numero_da_missao_08_e_historico(self):
        """91 é o que a MISSÃO 08 mediu. Reescrever seria apagar o registro."""
        self.assertRegex(self.DOCS['operacao'],
                         r'TESTES_REAIS \(MISSÃO 08, histórico\)\s*=\s*91\b',
                         'o número da MISSÃO 08 saiu do seu próprio documento')

    def test_o_numero_congelado_na_v1_e_historico_e_nao_muda(self):
        """CURRENT ≠ HISTORICAL, aplicado ao próprio repositório.

        A v1 foi congelada com 43 provas. Acrescentar provas depois **não** reescreve
        o que a v1 era — reescrever seria exatamente o erro que a régua de change event
        proíbe. Por isso o número corrente mora no documento de operação e o número da
        v1 fica onde está, rotulado como histórico.
        """
        self.assertRegex(self.DOCS['freeze'], r'TESTES_REAIS \(v1, histórico\)\s*=\s*43\b',
                         'o número da v1 saiu do documento de congelamento')

    def test_cobertura_das_normalizacoes(self):
        for nome in ('pacote', 'design'):
            with self.subTest(documento=nome):
                self.assertIn('82,1', self.DOCS[nome], 'cobertura de substância (82,1%)')
                self.assertIn('23,5', self.DOCS[nome], 'cobertura agronômica (23,5%)')

    def test_total_de_source_ids_coerente_com_o_atlas(self):
        n = len(source_ids())
        for nome in ('design',):
            with self.subTest(documento=nome):
                self.assertRegex(self.DOCS[nome], rf'`?{n}`? SOURCE_IDs',
                                 f'o pacote de design não diz {n} SOURCE_IDs')

    def test_a_cronologia_competitiva_foi_mesmo_retirada(self):
        """Se a leitura caiu no red team, não pode sobreviver como AFIRMAÇÃO.

        O registro histórico da retirada (uma citação do que se escreveu antes) é
        obrigatório e não pode ser confundido com a afirmação: por isso o teste olha
        os TÍTULOS e as linhas de tabela, onde uma frase vale como declaração, e não
        a prosa, onde ela pode estar sendo citada para ser desmentida.
        """
        alvo = re.compile(r'(?i)(18 meses|registrou primeiro)')
        for nome, txt in self.DOCS.items():
            titulos = re.findall(r'^#{1,4} .*$', txt, re.M)
            linhas = re.findall(r'^\|.*$', txt, re.M)
            for linha in titulos + linhas:
                with self.subTest(documento=nome, linha=linha[:60]):
                    self.assertNotRegex(linha, alvo,
                                        'a cronologia competitiva reapareceu como afirmação')

    def test_a_retirada_continua_registrada(self):
        """A queda tem de ficar preservada — não se reescreve a história."""
        self.assertRegex(self.DOCS['casos'], r'(?i)RETIRADA',
                         'o registro da leitura retirada desapareceu do documento')

    def test_nenhum_documento_afirma_derivacao_legal_das_datas(self):
        """A frase pode existir DENTRO da negação — o que não pode é ser afirmada.

        Mesma lógica do teste anterior: títulos e linhas de tabela declaram; a prosa
        pode citar para desmentir. E exigimos que a negação continue presente.
        """
        proibido = re.compile(r'(?i)data italiana (é|e) (juridicamente )?derivada')
        for nome, txt in self.DOCS.items():
            for linha in re.findall(r'^#{1,4} .*$', txt, re.M) + re.findall(r'^\|.*$', txt, re.M):
                with self.subTest(documento=nome, linha=linha[:60]):
                    self.assertNotRegex(linha, proibido,
                                        'afirma derivação legal entre as datas')
        self.assertRegex(self.DOCS['casos'], r'(?i)DERIVAÇÃO LEGAL = NÃO SEI',
                         'a recusa explícita da derivação legal desapareceu')


class TestLimitesDeDadoPessoal(unittest.TestCase):
    """MISSAO 10C — P-008 segue aberta, e o produto tem de dizer isso sozinho.

    O risco aqui nao e coletar demais: e a proxima conta ler "os dados sao publicos" e
    concluir "entao esta conforme". PUBLICO nao e LICITO DE PROCESSAR.
    """

    def setUp(self):
        self.doc = rd('regras', 'LIMITES-DE-DADO-PESSOAL-EAME.md')

    def test_os_estados_estao_declarados(self):
        for estado in ('NAMED_RESEARCHER_PUBLIC_SCREEN = BLOCKED_PENDING_LEGAL_REVIEW',
                       'PERSONAL_SCORING               = PROHIBITED_FOR_CURRENT_PILOT',
                       'SENSITIVE_PERSONAL_DATA        = OUT_OF_SCOPE',
                       'EMAIL                          = OUT_OF_SCOPE',
                       'PHONE                          = OUT_OF_SCOPE',
                       'PRIVATE_CONTACT                = OUT_OF_SCOPE'):
            with self.subTest(estado=estado.split('=')[0].strip()):
                self.assertIn(estado, self.doc)

    def test_o_documento_recusa_ser_parecer_juridico(self):
        self.assertRegex(self.doc, r'(?i)N[ÃA]O é parecer jur[ií]dico')
        self.assertIn('PÚBLICO ≠ LÍCITO DE PROCESSAR', self.doc)

    def test_nenhum_documento_declara_conformidade_por_ser_publico(self):
        """A frase que nao pode existir em lugar nenhum."""
        proibido = re.compile(r'(?i)(gdpr|lgpd)\s+(resolvid|ok\b|conforme|aprovad)')
        for dp, _, fs in os.walk(D):
            for f in fs:
                if not f.endswith('.md'):
                    continue
                caminho = os.path.join(dp, f)
                with open(caminho, encoding='utf-8') as fh:
                    txt = fh.read()
                with self.subTest(documento=os.path.relpath(caminho, D)):
                    self.assertIsNone(proibido.search(txt),
                                      'documento declara conformidade juridica sem revisao')

    def test_a_fila_continua_not_tested_e_agora_tem_dois_motivos(self):
        fila = json.load(open(os.path.join(ROOT, 'data', 'samples',
                                           'RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json'),
                              encoding='utf-8'))
        entradas = next(v for v in fila.values() if isinstance(v, list) and v
                        and isinstance(v[0], dict))
        for e in entradas:
            for campo in ('PUBLIC_LINKEDIN_STATUS', 'PUBLIC_YOUTUBE_STATUS'):
                if campo in e:
                    self.assertEqual('NOT_TESTED', e[campo])
