"""
RED TEAM DO CATÁLOGO PÚBLICO ADAMA ITALIA — quinze ataques contra dado real.

Diferente do red team do registro (`test_adama_it.py`), este atira contra o que
foi trazido do site pelo Chrome com janela: 10 páginas de produto e 29
documentos, capturados em `data/raw/IT/adama-website/`.

Três dos ataques nasceram de defeitos MEUS, encontrados durante a amostra e
corrigidos antes do censo:

  · o número `0037584/22` do Budge saía cortado como `003758` — um número que a
    página não traz;
  · o Ministero grava `016312` e a ADAMA publica `16312`, e comparar como texto
    reprovava os oito produtos que têm número;
  · a coluna "Quando trattare la coltura" era classificada como CULTURA, porque
    a palavra "coltura" está escrita dentro dela — e a janela de aplicação saía
    zero tendo janela na fonte.

Cada um virou teste, que é o único jeito de um defeito não voltar.
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import adama_it as ai            # noqa: E402
import adama_it_catalogo as cat  # noqa: E402

ACERVO = os.path.join(RAIZ, 'data', 'raw', 'IT', 'adama-website')


def _tem_acervo(*nomes):
    return all(os.path.exists(os.path.join(ACERVO, n)) for n in nomes)


PRECISA_AMOSTRA = unittest.skipUnless(
    _tem_acervo('amostra-10.json', 'enumeracao.json'),
    'acervo da amostra ausente — a captura roda pelo Chrome com janela')


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ACERVO, 'amostra-10.json'), encoding='utf-8') as fh:
            cls.amostra = json.load(fh)['PRODUCTS']
        with open(os.path.join(ACERVO, 'enumeracao.json'), encoding='utf-8') as fh:
            cls.enum = json.load(fh)
        cls.reg = ai.registro_medido()
        cls.por_id, cls.por_nome = cat.indice_registro(cls.reg)


@PRECISA_AMOSTRA
class Ataque1_UrlDoSitemapViraProduto(Base):
    """URL no sitemap não é produto: é URL."""

    def test_toda_url_de_produto_foi_confirmada_abrindo_a_pagina(self):
        for p in self.amostra:
            self.assertTrue(p.get('PRODUCT_NAME'),
                            'URL virou produto sem nome: %s' % p['SOURCE_URL'])
            self.assertTrue(p.get('NODE_ID') or p.get('CANONICAL_URL'),
                            'sem identidade interna: %s' % p['SOURCE_URL'])

    def test_a_enumeracao_diz_que_nao_e_contagem_de_produto(self):
        self.assertIn('CATALOG_PRODUCTS', self.enum['WHAT_THIS_IS_NOT'])
        self.assertIn('identidade', self.enum['WHAT_THIS_IS_NOT'])


@PRECISA_AMOSTRA
class Ataque2_PresencaViraRegistro(Base):
    """Estar no catálogo não prova registro."""

    def test_produto_sem_numero_publicado_nao_fecha_registro(self):
        sem = [p for p in self.amostra if not p.get('REGISTRATION_ID_AS_WRITTEN')]
        self.assertTrue(sem, 'a amostra precisa de ao menos um sem número')
        for p in sem:
            r = cat.cruzar(p, self.por_id, self.por_nome)
            self.assertNotEqual(r['STATE'], ai.LOCAL_REGISTERED)
            self.assertNotEqual(r['STATE'], ai.NOT_REGISTERED)

    def test_ausencia_de_casamento_nunca_vira_NOT_REGISTERED(self):
        r = cat.cruzar({'PRODUCT_NAME': 'PRODUTO INEXISTENTE SA'},
                       self.por_id, self.por_nome)
        self.assertEqual(r['STATE'], ai.LOCAL_PRESENT_NOT_PROVED)
        self.assertIn('NÃO é NOT_REGISTERED', r['WHY'])


@PRECISA_AMOSTRA
class Ataque3_HolderEstrangeiroSaiDaItalia(Base):
    """HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY."""

    def test_casamento_nao_filtra_por_titular(self):
        casados = [cat.cruzar(p, self.por_id, self.por_nome) for p in self.amostra]
        fechados = [c for c in casados if c['STATE'] == ai.LOCAL_REGISTERED]
        self.assertTrue(fechados)
        titulares = {c.get('HOLDER') for c in fechados}
        self.assertTrue(any('ITALIA' not in (t or '').upper() for t in titulares),
                        'a amostra precisa exercitar titular não-italiano')

    def test_titular_nao_italiano_continua_no_universo_italiano(self):
        for p in self.amostra:
            c = cat.cruzar(p, self.por_id, self.por_nome)
            if c['STATE'] != ai.LOCAL_REGISTERED:
                continue
            escopo = ai.escopo_de_pais({'HOLDER': c.get('HOLDER')})
            self.assertEqual(escopo['PORTFOLIO_COUNTRY'], 'IT')
            self.assertEqual(escopo['REGISTRATION_COUNTRY'], 'IT')


@PRECISA_AMOSTRA
class Ataque4_NomeIgualViraMesmoRegistro(Base):
    """NOME IGUAL ≠ MESMO REGISTRO."""

    def test_casamento_so_por_nome_nunca_fecha_LOCAL_REGISTERED(self):
        alvo = self.reg[0]
        r = cat.cruzar({'PRODUCT_NAME': alvo['PRODUCT']}, self.por_id, self.por_nome)
        self.assertEqual(r['STATE'], ai.LOCAL_PRESENT_NOT_PROVED)
        self.assertEqual(r['MATCHED_BY'], 'NAME_ONLY')
        self.assertIsNotNone(r.get('CANDIDATE_REGISTRATION_ID'))

    def test_nome_que_cobre_dois_registros_vira_conflito_e_nao_funde(self):
        alvo = self.reg[0]
        reg = self.reg + [dict(alvo, REGISTRATION_ID='999002')]
        por_id, por_nome = cat.indice_registro(reg)
        r = cat.cruzar({'PRODUCT_NAME': alvo['PRODUCT']}, por_id, por_nome)
        self.assertEqual(r['STATE'], ai.REGISTRATION_CONFLICT)
        self.assertEqual(len(r['CANDIDATE_REGISTRATION_IDS']), 2)


@PRECISA_AMOSTRA
class Ataque5_CulturaCitadaViraAutorizada(Base):
    """CITED_CROP ≠ AUTHORIZED_CROP. O termo da página é um link de busca."""

    def test_as_culturas_da_pagina_sao_links_de_busca_do_site(self):
        vistos = 0
        for p in self.amostra:
            for c in p.get('CROPS') or []:
                vistos += 1
                self.assertIn('/search?', c['HREF'],
                              'cultura deixou de ser termo de navegação: %s' % c)
        self.assertGreater(vistos, 100)

    def test_o_censo_nao_declara_nenhuma_relacao_DECLARED(self):
        out = cat.censo()
        self.assertEqual(out['DECLARED_CROP_RELATIONS'], 0)
        self.assertGreater(out['CITED_CROP_RELATIONS'], 0)
        self.assertIn('links de busca', out['DECLARED_WHY'])


@PRECISA_AMOSTRA
class Ataque6_ListaDeCulturaVezesListaDeAlvo(Base):
    """CO_PRESENCE ≠ AUTHORIZED_PAIR — o produto cartesiano pela porta lateral."""

    def test_nenhum_par_nasce_de_listas_separadas(self):
        out = cat.censo()
        self.assertEqual(out['CROP_ISSUE_ANCHORED'], 0)
        self.assertGreater(out['CROP_ISSUE_CARTESIAN_AVOIDED'], 2000)

    def test_tabela_sem_coluna_de_alvo_nao_produz_par(self):
        for p in self.amostra:
            for t in p.get('TABLES') or []:
                r = cat.relacoes_da_tabela(t, p['SOURCE_URL'])
                if not r['HAS_ISSUE_COLUMN']:
                    self.assertEqual(r['CROP_ISSUE'], [])

    def test_par_so_nasce_quando_cultura_e_alvo_estao_na_mesma_linha(self):
        """Tabela sintética: a relação existe porque a linha a carrega."""
        t = {'TABLE_INDEX': 0, 'SECTION_TITLE': 'COME SI USA',
             'HEADER': ['Coltura', 'Avversità', 'Dose (l/ha)'],
             'ROWS': [['Frumento duro', 'Fusariosi', '1,5']]}
        r = cat.relacoes_da_tabela(t, 'http://x')
        self.assertEqual(len(r['CROP_ISSUE']), 1)
        self.assertEqual(r['CROP_ISSUE'][0]['CROP_AS_WRITTEN'], 'Frumento duro')
        self.assertEqual(r['CROP_ISSUE'][0]['RELATION_ORIGIN'], 'TABLE_ROW_SAME_LINE')
        self.assertEqual(r['CROP_ISSUE'][0]['ROW_INDEX'], 0)


@PRECISA_AMOSTRA
class Ataque7_DoseViraAlvo(Base):
    """DOSE ≠ CROP_ISSUE_PAIR."""

    def test_toda_relacao_de_dose_medida_e_de_cultura_e_nao_de_alvo(self):
        out = cat.censo()
        self.assertGreater(out['CROP_DOSE'], 0)
        for linha in out['CROP_DOSE_ROWS']:
            self.assertIn('CROP_AS_WRITTEN', linha)
            self.assertNotIn('ISSUE_AS_WRITTEN', linha)

    def test_dose_sem_coluna_de_cultura_nao_vira_relacao(self):
        t = {'TABLE_INDEX': 0, 'SECTION_TITLE': None,
             'HEADER': ['Epoca di applicazione', 'Dose totale p.f./ha'],
             'ROWS': [['pre-emergenza', '1.5 l/ha']]}
        r = cat.relacoes_da_tabela(t, 'http://x')
        self.assertEqual(r['CROP_DOSE'], [])
        self.assertIn('sem cultura', r['WHY_NO_RELATION'])


@PRECISA_AMOSTRA
class Ataque8_QualquerPdfViraEtichetta(Base):
    """LABEL ≠ DOCUMENT_TYPE. O conteúdo decide."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        caminho = os.path.join(ACERVO, 'documentos-amostra.json')
        with open(caminho, encoding='utf-8') as fh:
            cls.docs = [d for d in json.load(fh)['DOCUMENTS']
                        if d.get('STATE') == 'DOWNLOADED']

    def test_brochura_nao_vira_rotulo(self):
        for d in self.docs:
            t = cat.tipar_documento(d)
            if re.search(r'brochure|leaf', (d.get('ORIGINAL_FILENAME') or ''), re.I):
                self.assertNotEqual(t['DOCUMENT_TYPE'], cat.ETICHETTA,
                                    'peça de venda virou ato administrativo: %s'
                                    % d['ORIGINAL_FILENAME'])

    def test_rotulo_reconhecido_tem_a_frase_do_ato_no_conteudo(self):
        etichette = [d for d in self.docs
                     if cat.tipar_documento(d)['TYPE_FROM_CONTENT'] == cat.ETICHETTA]
        self.assertGreaterEqual(len(etichette), 5)

    def test_um_documento_pode_cobrir_varios_produtos(self):
        """ONE DOCUMENT ≠ ONE PRODUCT: a SDS do Lamdex cobre cinco marcas."""
        multi = [d for d in self.docs
                 if cat.tipar_documento(d)['COVERS_MULTIPLE_PRODUCTS']]
        self.assertTrue(multi, 'o acervo tem SDS multi-produto e ela sumiu')


@PRECISA_AMOSTRA
class Ataque9_PathViraIdentidade(Base):
    """PATH ≠ IDENTITY — o catálogo serve produto sob dois prefixos."""

    def test_o_catalogo_usa_dois_prefixos_de_rota(self):
        self.assertEqual(sorted(self.enum['PATH_PREFIXES']),
                         ['prodotti', 'prodotti-adama'])

    def test_identidade_vem_do_no_do_site_e_nao_da_pasta(self):
        for p in self.amostra:
            self.assertEqual(cat.identidade(p), p.get('NODE_ID') or p.get('CANONICAL_URL'))
            self.assertNotIn('/prodotti', str(cat.identidade(p)))

    def test_duas_urls_com_o_mesmo_no_contam_um_produto_so(self):
        out = cat.censo()
        self.assertLessEqual(out['CATALOG_PRODUCTS'], out['CATALOG_PRODUCT_PAGES'])


@PRECISA_AMOSTRA
class Ataque10_RegistroViraDisponibilidade(Base):
    """REGISTRATION ≠ COMMERCIAL_AVAILABILITY."""

    def test_o_artefato_se_proibe_de_escrever_disponibilidade(self):
        out = cat.censo()
        self.assertIn('COMMERCIAL_AVAILABILITY', out['STILL_FORBIDDEN_TO_WRITE'])
        self.assertIn('DISCONTINUED', out['STILL_FORBIDDEN_TO_WRITE'])
        self.assertIn('REGISTRATION ≠ COMMERCIAL_AVAILABILITY', out['LAWS'])

    def test_nenhum_produto_carrega_campo_de_disponibilidade(self):
        out = cat.censo()
        for p in out['PRODUCTS']:
            for proibido in ('AVAILABLE', 'IN_STOCK', 'DISCONTINUED', 'PRICE'):
                self.assertFalse(any(proibido in k for k in p),
                                 'campo proibido em %s' % p['PRODUCT_NAME'])


@PRECISA_AMOSTRA
class Ataque11_DomViraFatoSemAncora(Base):
    """Toda afirmação diz onde foi observada."""

    def test_toda_relacao_de_tabela_carrega_linha_e_secao(self):
        out = cat.censo()
        linhas = out['CROP_DOSE_ROWS'] + out['CROP_ISSUE_ROWS'] + out['APPLICATION_WINDOW_ROWS']
        self.assertTrue(linhas)
        for r in linhas:
            self.assertIn('PRODUCT_URL', r)
            self.assertIn('ROW_INDEX', r)
            self.assertIn('COLUMN_HEADER', r)

    def test_o_numero_de_registro_guarda_o_texto_de_onde_saiu(self):
        for p in self.amostra:
            if p.get('REGISTRATION_ID_AS_WRITTEN'):
                self.assertIn('registrazione',
                              (p['REGISTRATION_ANCHOR_TEXT'] or '').lower())


@PRECISA_AMOSTRA
class Ataque12_SessaoViraEvidencia(Base):
    """SESSION ≠ EVIDENCE — cookie e perfil não entram no acervo."""

    def test_o_acervo_nao_guarda_estado_volatil_do_navegador(self):
        proibidos = ('cookie', 'history', 'login data', 'local storage',
                     'devtools', 'chrome-profile')
        for pasta, _, arquivos in os.walk(ACERVO):
            for a in arquivos:
                baixo = os.path.join(pasta, a).lower()
                for p in proibidos:
                    self.assertNotIn(p, baixo, 'estado de sessão no acervo: %s' % a)

    def test_a_captura_registra_o_navegador_sem_registrar_a_sessao(self):
        with open(os.path.join(ACERVO, 'amostra-10.json'), encoding='utf-8') as fh:
            d = json.load(fh)
        ctx = d['BROWSER_CONTEXT']
        self.assertEqual(ctx['HEADED'], 'YES')
        self.assertEqual(ctx['PROFILE_KIND'], 'IT')
        self.assertNotIn('COOKIES', ctx)


@PRECISA_AMOSTRA
class Ataque13_EvidenciaEspanholaViraItaliana(Base):
    """Nenhum asset ES/FR pode sustentar fato italiano."""

    def test_todo_arquivo_do_acervo_vive_sob_IT(self):
        with open(os.path.join(ACERVO, 'indice-captura.json'), encoding='utf-8') as fh:
            indice = json.load(fh)
        self.assertTrue(indice)
        for url, linha in indice.items():
            self.assertEqual(linha['COUNTRY'], 'IT')
            self.assertIn('data/raw/IT/', linha['LOCAL_FILE'])

    def test_toda_url_capturada_e_do_escopo_italiano(self):
        with open(os.path.join(ACERVO, 'indice-captura.json'), encoding='utf-8') as fh:
            indice = json.load(fh)
        for url in indice:
            self.assertTrue(url.startswith('https://www.adama.com/'), url)
            self.assertFalse(re.search(r'/(espana|spain|france|deutschland)/', url), url)

    def test_o_censo_carrega_pais_em_todos_os_eixos(self):
        out = cat.censo()
        for campo in ('SOURCE_COUNTRY', 'FACT_COUNTRY', 'PORTFOLIO_COUNTRY'):
            self.assertEqual(out[campo], 'IT')


@PRECISA_AMOSTRA
class Ataque14_Http403ViraCatalogoVazio(Base):
    """ROUTE_BLOCKED ≠ CATALOG_EMPTY, e headless é rota bloqueada."""

    def test_o_censo_declara_a_rota_como_headed_only(self):
        out = cat.censo()
        self.assertEqual(out['BROWSER_ROUTE']['STATE'], 'HEADED_ONLY')
        self.assertIn('403', out['BROWSER_ROUTE']['CURL'])
        self.assertIn('Access Denied', out['BROWSER_ROUTE']['HEADLESS'])

    def test_o_catalogo_bloqueado_nao_saiu_como_vazio(self):
        out = cat.censo()
        self.assertGreater(out['CATALOG_PRODUCTS'], 0)
        self.assertIn('ROUTE_BLOCKED ≠ CATALOG_EMPTY', out['LAWS'])

    def test_a_lista_de_documentos_proibida_pelo_robots_fica_declarada(self):
        out = cat.censo()
        self.assertIn('*/ajax/', out['ROBOTS']['DISALLOWS_USED'])
        self.assertIn('pode haver mais', out['ROBOTS']['CONSEQUENCE'])
        comrota = [p for p in out['PRODUCTS']
                   if p['ALL_DOCUMENTS_ROUTE_STATE'] == 'ROBOTS_DISALLOWED']
        self.assertTrue(comrota)


@PRECISA_AMOSTRA
class Ataque15_PaginaDuplicadaViraProdutoDuplicado(Base):
    """Página é página; produto é nó. E o bloco "Altri prodotti" não contamina."""

    def test_o_bloco_de_produtos_relacionados_nao_vira_campo_do_produto(self):
        """A página traz o subtítulo de OUTROS produtos no bloco "Altri prodotti".
        O DOM salvo tem vários; o extrator tem de sair com UM — o do dono da
        página. Se este teste cair, um produto está vestindo a roupa do vizinho."""
        com_vizinhos = 0
        for p in self.amostra:
            caminho = os.path.join(RAIZ, p['LOCAL_FILE'].replace('/', os.sep))
            with open(caminho, encoding='utf-8') as fh:
                html = fh.read()
            n = len(re.findall(r'field--name-product-subtitle', html))
            if n > 1:
                com_vizinhos += 1
            sub = p.get('SUBTITLE') or ''
            self.assertLess(len(sub), 400,
                            'subtítulo de %s tem %d chars: engoliu o bloco vizinho'
                            % (p['PRODUCT_NAME'], len(sub)))
            for q in self.amostra:
                if q is p or not (q.get('SUBTITLE') or ''):
                    continue
                self.assertNotEqual(sub, q['SUBTITLE'],
                                    'dois produtos saíram com o mesmo subtítulo: '
                                    '%s e %s' % (p['PRODUCT_NAME'], q['PRODUCT_NAME']))
        self.assertGreaterEqual(
            com_vizinhos, 5,
            'nenhuma página tinha bloco vizinho — o ataque não exercitou nada')

    def test_contagem_de_produto_usa_identidade_e_nao_pagina(self):
        out = cat.censo()
        self.assertEqual(out['IDENTITY_BASIS'],
                         'NODE_ID do site, com canonical como reserva')
        self.assertEqual(out['CATALOG_PRODUCTS'],
                         len({cat.identidade(p) for p in self.amostra}))


# ─────────────────────── regressões: defeitos meus, achados na amostra
@PRECISA_AMOSTRA
class Regressao_ZeroAEsquerda(Base):
    """REGISTRATION_ID_FORMAT ≠ REGISTRATION_ID."""

    def test_o_ministero_grava_com_zero_e_a_adama_publica_sem(self):
        self.assertTrue(all(re.fullmatch(r'\d{6}', str(r['REGISTRATION_ID']))
                            for r in self.reg))
        publicados = [p['REGISTRATION_ID_AS_WRITTEN'] for p in self.amostra
                      if p.get('VISIBLE_REGISTRATION_ID')]
        self.assertTrue(any(not v.startswith('0') for v in publicados))

    def test_comparar_como_texto_reprovaria_o_casamento_verdadeiro(self):
        cru = {str(r['REGISTRATION_ID']) for r in self.reg}
        publicados = [p['REGISTRATION_ID_AS_WRITTEN'] for p in self.amostra
                      if p.get('VISIBLE_REGISTRATION_ID')]
        self.assertTrue(publicados)
        self.assertEqual([v for v in publicados if v in cru], [],
                         'se isto passar, o dado mudou e o teste precisa ser relido')

    def test_normalizado_o_casamento_fecha_e_diz_o_que_normalizou(self):
        fechados = [cat.cruzar(p, self.por_id, self.por_nome) for p in self.amostra]
        ok = [c for c in fechados if c['STATE'] == ai.LOCAL_REGISTERED]
        self.assertGreaterEqual(len(ok), 8)
        for c in ok:
            self.assertEqual(c['MATCHED_BY'], 'REGISTRATION_ID_NORMALIZED')
            self.assertIn('zeros à esquerda', c['NORMALIZATION'])


@PRECISA_AMOSTRA
class Regressao_NumeroCortadoNoMeio(Base):
    """O token vai inteiro, ou não vai."""

    def test_o_budge_guarda_o_numero_como_escrito(self):
        budge = [p for p in self.amostra if 'Budge' in (p.get('PRODUCT_NAME') or '')]
        self.assertTrue(budge, 'o Budge saiu da amostra e este defeito perde a prova')
        b = budge[0]
        self.assertEqual(b['REGISTRATION_ID_AS_WRITTEN'], '0037584/22')
        self.assertIsNone(b['VISIBLE_REGISTRATION_ID'])
        self.assertEqual(b['REGISTRATION_FORMAT_STATE'],
                         'PRESENT_BUT_NOT_MINISTERO_FORMAT')

    def test_token_fora_do_formato_nao_vira_id_comparavel(self):
        self.assertEqual(cat.id_ministero('0037584/22'),
                         (None, 'PRESENT_BUT_NOT_MINISTERO_FORMAT'))
        self.assertEqual(cat.id_ministero('16312'), ('16312', 'MINISTERO_LIKE'))
        self.assertEqual(cat.id_ministero('016312'), ('16312', 'MINISTERO_LIKE'))
        self.assertEqual(cat.id_ministero(None), (None, 'ABSENT'))


@PRECISA_AMOSTRA
class Regressao_QuandoTrattareLaColtura(Base):
    """A palavra "coltura" dentro de uma frase não faz da coluna uma cultura."""

    def test_a_coluna_de_tempo_e_tempo(self):
        self.assertEqual(cat.papel_da_coluna('Quando trattare la coltura'), 'TIMING')
        self.assertEqual(cat.papel_da_coluna('Colture'), 'CROP')
        self.assertEqual(cat.papel_da_coluna('Coltura'), 'CROP')
        self.assertEqual(cat.papel_da_coluna('Epoca di applicazione'), 'TIMING')

    def test_dose_ganha_de_tratamento_no_mesmo_cabecalho(self):
        self.assertEqual(
            cat.papel_da_coluna('n° massimo di trattamenti e dose totale massima'),
            'DOSE')

    def test_a_amostra_tem_janela_de_aplicacao_medida(self):
        out = cat.censo()
        self.assertGreater(out['APPLICATION_WINDOWS'], 0)

    def test_dose_sem_unidade_na_celula_pega_a_unidade_do_cabecalho(self):
        d = cat.dose_legivel('3 - 5', 'Dose prodotto (l/ha)')
        self.assertEqual(d['VALUE'], '3 - 5 l/ha')
        self.assertEqual(d['UNIT_FROM'], 'COLUMN_HEADER')
        self.assertIsNone(cat.dose_legivel('Impiegare in fase di accrescimento',
                                           'Indicazioni'))


# ───────────────────────────────── censo completo: os 51 contra os 163
PRECISA_CENSO = unittest.skipUnless(
    _tem_acervo('paginas-produto.json', 'documentos-censo.json'),
    'acervo do censo ausente')


@PRECISA_CENSO
class Censo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = cat.censo('paginas-produto.json', 'documentos-censo.json',
                            'CENSO_COMPLETO')

    def test_o_escopo_nao_e_sobrescrito_por_variavel_de_laco(self):
        """Regressão: `rotulo` era o parâmetro do escopo E uma variável do laço
        de documentos. O censo saía rotulado com o nome de um PDF, e o §18 nem
        rodava. Um nome reaproveitado apagou dois resultados em silêncio."""
        self.assertEqual(self.out['SCOPE'], 'CENSO_COMPLETO')

    def test_afirmacao_fora_do_recorte_nao_e_conflito(self):
        """CLAIM_OUTSIDE_MEASURED_REGISTRY ≠ REGISTRATION_CONFLICT.

        Conflito é evidência que se contradiz. Aqui a minha metade é que é
        menor: os 163 são a fatia ADAMA de um censo nacional de 17.695."""
        fora = [p for p in self.out['PRODUCTS']
                if p['CROSSWALK'].get('REASON') == 'CLAIM_OUTSIDE_MEASURED_REGISTRY']
        self.assertTrue(fora)
        for p in fora:
            self.assertEqual(p['CROSSWALK']['STATE'], ai.LOCAL_PRESENT_NOT_PROVED)
            self.assertIn('NÃO é conflito', p['CROSSWALK']['WHY'])
            self.assertIn('PROD_FTS', p['CROSSWALK']['WHAT_WOULD_CLOSE_IT'])

    def test_nenhum_produto_saiu_como_NOT_REGISTERED(self):
        for p in self.out['PRODUCTS']:
            self.assertNotEqual(p['CROSSWALK']['STATE'], ai.NOT_REGISTERED)

    def test_dois_produtos_do_catalogo_podem_dividir_um_registro(self):
        """CATALOG_PRODUCT ≠ REGISTRATION: a página de sistema herda o número
        do produto que a compõe."""
        div = self.out['CATALOG_PRODUCTS_SHARING_ONE_REGISTRATION']
        self.assertTrue(div, 'o caso Highcard/Max-Ace sumiu do dado')
        for rid, nomes in div.items():
            self.assertGreater(len(nomes), 1)

    def test_a_conta_dos_registros_fecha_sem_sobra(self):
        casados = self.out['DISTINCT_REGISTRATIONS_MATCHED']
        ausentes = self.out['REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG']['COUNT']
        self.assertEqual(casados + ausentes, self.out['REGULATORY_PRODUCTS'])
        self.assertLess(casados, self.out['CROSSWALK_STATES'][ai.LOCAL_REGISTERED] + 1)

    def test_ausencia_no_catalogo_nao_vira_descontinuado(self):
        a = self.out['REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG']
        self.assertTrue(a['CATALOG_ENUMERATION_COMPLETE'])
        for proibido in ('DISCONTINUED', 'UNAVAILABLE', 'NOT_SOLD', 'NOT_REGISTERED'):
            self.assertIn(proibido, a['WHAT_IT_DOES_NOT_MEAN'])

    def test_na_amostra_a_ausencia_nao_e_calculada(self):
        """§18: o número só existe com a enumeração fechada."""
        amostra = cat.censo()
        self.assertIsNone(amostra['REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG'])

    def test_documento_na_pagina_nao_e_documento_do_dono_da_pagina(self):
        """DOCUMENT_ON_PAGE ≠ DOCUMENT_OF_THAT_PRODUCT."""
        alheios = [d for d in self.out['DOCUMENTS']
                   if d['DOCUMENT_NAMES_ANOTHER_PRODUCT']]
        self.assertTrue(alheios, 'as páginas de sistema sumiram do dado')
        for d in alheios:
            self.assertEqual(d['ATTRIBUTION'], 'PRESENTED_ON_PAGE_OF_ANOTHER_PRODUCT')

    def test_o_censo_completo_nao_inventa_par_cultura_alvo(self):
        self.assertEqual(self.out['CROP_ISSUE_ANCHORED'], 0)
        self.assertGreater(self.out['CROP_ISSUE_CARTESIAN_AVOIDED'], 13000)
        self.assertEqual(self.out['CROP_ISSUE_ROWS'], [])

    def test_o_maior_asset_cabe_no_limite_do_storage(self):
        self.assertGreater(self.out['LARGEST_ASSET_BYTES'], 0)
        self.assertTrue(self.out['LARGEST_ASSET_WITHIN_LIMIT'])
        self.assertLess(self.out['LARGEST_ASSET_BYTES'], self.out['STORAGE_LIMIT_BYTES'])

    def test_todo_produto_do_censo_tem_rotulo_e_ficha_de_seguranca(self):
        por_tipo = self.out['DOCUMENTS_BY_TYPE']
        self.assertEqual(por_tipo[cat.ETICHETTA], self.out['CATALOG_PRODUCT_PAGES'])
        self.assertEqual(por_tipo[cat.SDS], self.out['CATALOG_PRODUCT_PAGES'])


# ─────────────────────────────────────────── preservação: os bytes, com prova
import adama_it_preservar as pres  # noqa: E402


class ChaveDeStorage(unittest.TestCase):
    """PATH ≠ IDENTITY — e a chave ainda assim tem de ser segura e determinística."""

    def test_a_mesma_entrada_da_sempre_a_mesma_chave(self):
        a = pres.chave_de_storage('DOCUMENT', 'a' * 64, 'Etichetta.pdf')
        b = pres.chave_de_storage('DOCUMENT', 'a' * 64, 'Etichetta.pdf')
        self.assertEqual(a, b)
        self.assertTrue(a.startswith('IT/adama-website/DOCUMENT/'))

    def test_conteudo_diferente_cai_em_chave_diferente(self):
        """O sha16 no nome impede sobrescrita silenciosa de conteúdo diferente."""
        a = pres.chave_de_storage('DOCUMENT', 'a' * 64, 'x.pdf')
        b = pres.chave_de_storage('DOCUMENT', 'b' * 64, 'x.pdf')
        self.assertNotEqual(a, b)

    def test_acento_composto_e_decomposto_dao_a_mesma_chave(self):
        """Sem NFC antes de tudo, um arquivo vira duas chaves conforme a fonte."""
        composto = 'Etichettà.pdf'          # à em um code point
        decomposto = 'Etichettà.pdf'       # a + combinante
        self.assertNotEqual(composto, decomposto)
        self.assertEqual(pres.chave_de_storage('DOCUMENT', 'c' * 64, composto),
                         pres.chave_de_storage('DOCUMENT', 'c' * 64, decomposto))

    def test_nao_faz_url_decode_silencioso(self):
        """`%20` não vira espaço: decodificar muda a identidade do que foi baixado."""
        k = pres.chave_de_storage('DOCUMENT', 'd' * 64, 'SDS%20GOLTIX.pdf')
        self.assertNotIn('SDS GOLTIX', k)
        self.assertIn('SDS_20GOLTIX.pdf', k)

    def test_o_pais_esta_na_chave_e_nunca_e_ES_ou_FR(self):
        k = pres.chave_de_storage('DOCUMENT', 'e' * 64, 'x.pdf')
        self.assertTrue(k.startswith('IT/'))
        self.assertNotIn('/ES/', k)
        self.assertNotIn('/FR/', k)

    def test_nome_gigante_e_cortado_sem_perder_a_extensao(self):
        k = pres.chave_de_storage('DOCUMENT', 'f' * 64, 'a' * 400 + '.pdf')
        ultimo = k.split('/')[-1]
        self.assertTrue(ultimo.endswith('.pdf'))
        self.assertLessEqual(len(ultimo), 120)


@PRECISA_CENSO
class PlanoDePreservacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = pres.plano()

    def test_o_denominador_nao_e_inflado_com_lixo(self):
        self.assertEqual(set(self.p['POR_ESPECIE']),
                         {'PRODUCT_DOM', 'DOCUMENT', 'CAPTURE', 'MANIFEST'})
        for proibido in ('cache do navegador', 'CSS', 'fontes', 'cookies'):
            self.assertIn(proibido, self.p['O_QUE_NAO_ENTRA'])

    def test_nenhuma_chave_colide(self):
        self.assertEqual(self.p['COLISOES_DE_CHAVE'], {})
        self.assertEqual(self.p['RAW_EXPECTED'], self.p['OBJETOS_DISTINTOS'])

    def test_o_maior_asset_foi_medido_antes_do_lote(self):
        self.assertGreater(self.p['LARGEST_ASSET_BYTES'], 0)
        self.assertTrue(self.p['MAIOR_CABE_NO_LIMITE'])
        self.assertEqual(self.p['LIMITE_BYTES'], 200 * 1024 * 1024)

    def test_o_hash_do_plano_vem_do_disco_e_bate(self):
        """O manifesto diz o que foi baixado; o disco diz o que existe."""
        import hashlib
        for it in self.p['ITENS'][:5] + self.p['ITENS'][-5:]:
            caminho = os.path.join(RAIZ, it['ARQUIVO_LOCAL'].replace('/', os.sep))
            with open(caminho, 'rb') as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), it['SHA256'])

    def test_todo_item_do_plano_e_italiano(self):
        for it in self.p['ITENS']:
            self.assertEqual(it['COUNTRY'], 'IT')
            self.assertTrue(it['ARQUIVO_LOCAL'].startswith('data/raw/IT/'))
            self.assertTrue(it['OBJETO'].startswith('IT/'))

    def test_hash_igual_nao_apaga_procedencia(self):
        """Regressão: o rótulo do Highcard é linkado por DUAS páginas, e a
        versão anterior guardava só a última — a página DONA do documento
        sumia do manifesto.  MESMO CONTEÚDO ≠ MESMA PROCEDÊNCIA."""
        multi = [i for i in self.p['ITENS'] if i['PROVENANCE_COUNT'] > 1]
        self.assertTrue(multi, 'o caso Highcard/Max-Ace sumiu do plano')
        for i in multi:
            paginas = {o['PRODUCT_PAGE'] for o in i['PROVENANCE']}
            self.assertGreater(len(paginas), 1)
            for o in i['PROVENANCE']:
                for campo in ('SOURCE_URL', 'ORIGINAL_FILENAME', 'PRODUCT_PAGE',
                              'CONTENT_SHA256'):
                    self.assertIn(campo, o)

    def test_nenhum_link_de_documento_se_perde_entre_censo_e_plano(self):
        with open(os.path.join(ACERVO, 'documentos-censo.json'), encoding='utf-8') as fh:
            baixados = [d for d in json.load(fh)['DOCUMENTS']
                        if d.get('STATE') == 'DOWNLOADED']
        self.assertEqual(self.p['DOCUMENT_LINKS_TOTAL'], len(baixados))

    def test_a_cadeia_141_139_138_fica_escrita_e_nao_vira_erro(self):
        self.assertEqual(self.p['POR_ESPECIE']['DOCUMENT'], 139)
        self.assertGreater(self.p['OBJETOS_COM_CONTEUDO_REPETIDO'], 0)
        self.assertIn('hash igual não apaga origem',
                      self.p['PORQUE_CONTEUDO_REPETIDO_NAO_E_ERRO'])

    def test_o_plano_declara_qual_censo_esta_completo_e_qual_nao(self):
        self.assertTrue(self.p['PRODUCT_CENSUS_COMPLETE'])
        self.assertFalse(self.p['DOCUMENT_CENSUS_COMPLETE'])
        self.assertEqual(self.p['DOCUMENT_CENSUS_INCOMPLETE_REASON'],
                         'ROBOTS_DISALLOWS_AJAX_ROUTE')

    def test_nenhum_item_do_plano_veio_de_rota_proibida(self):
        for it in self.p['ITENS']:
            for o in it['PROVENANCE']:
                self.assertNotIn('/ajax/', o['SOURCE_URL'] or '')


class PortaoRaw(unittest.TestCase):
    """RAW PRESENCE ≠ RAW CONTENT VERIFIED."""

    def _itens(self, n, estado, verificado):
        return [{'OBJETO': 'IT/x/%d' % i, 'ESTADO': estado,
                 **({'VERIFICACAO': 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'}
                    if verificado else {})} for i in range(n)]

    def test_presenca_sozinha_nao_fecha_o_portao(self):
        g = pres.portao(self._itens(3, 'UPLOADED', False), 3, {})
        self.assertEqual(g['STATE'], 'OPEN')
        self.assertIn('CONTENT_HASH_CHECKED_EQ_EXPECTED', g['MISSING'])

    def test_com_hash_conferido_o_portao_fecha(self):
        g = pres.portao(self._itens(3, 'VERIFIED', True), 3, {})
        self.assertEqual(g['STATE'], 'CLOSED')
        self.assertEqual(g['SHA_VERIFIED'], 3)

    def test_esperado_zero_nunca_fecha(self):
        g = pres.portao([], 0, {})
        self.assertEqual(g['STATE'], 'OPEN')
        self.assertIn('EXPECTED_POSITIVE', g['MISSING'])

    def test_hash_divergente_derruba_o_portao(self):
        itens = self._itens(2, 'VERIFIED', True)
        itens.append({'OBJETO': 'IT/x/9', 'ESTADO': 'FAILED_WITH_REASON',
                      'MOTIVO': 'HASH_MISMATCH: os bytes de volta não batem',
                      'VERIFICACAO': 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'})
        g = pres.portao(itens, 3, {})
        self.assertEqual(g['STATE'], 'OPEN')
        self.assertEqual(g['HASH_MISMATCH'], 1)
        self.assertIn('HASH_MISMATCH_ZERO', g['MISSING'])

    def test_objeto_remoto_que_ninguem_esperava_vira_orfao(self):
        g = pres.portao(self._itens(2, 'VERIFIED', True), 2,
                        {'IT/x/0': 1, 'IT/x/1': 1, 'IT/intruso': 1})
        self.assertEqual(g['ORPHANS'], 1)
        self.assertEqual(g['STATE'], 'OPEN')

    def test_byte_que_subiu_nao_conta_como_byte_preservado(self):
        """A oitava condição é de bytes: um objeto truncado passa por presente e
        por contado, e só não passa por aqui."""
        itens = [{'OBJETO': 'IT/x/0', 'ESTADO': 'VERIFIED', 'BYTES': 100,
                  'BYTES_DE_VOLTA': 100,
                  'VERIFICACAO': 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'},
                 {'OBJETO': 'IT/x/1', 'ESTADO': 'VERIFIED', 'BYTES': 100,
                  'BYTES_DE_VOLTA': 40,
                  'VERIFICACAO': 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'}]
        g = pres.portao(itens, 2, {})
        self.assertEqual(g['BYTES_EXPECTED'], 200)
        self.assertEqual(g['BYTES_VERIFIED_REMOTELY'], 140)
        self.assertEqual(g['STATE'], 'OPEN')
        self.assertIn('BYTES_VERIFIED_EQ_EXPECTED', g['MISSING'])

    def test_com_os_bytes_de_volta_completos_o_portao_fecha(self):
        itens = [{'OBJETO': 'IT/x/%d' % i, 'ESTADO': 'VERIFIED', 'BYTES': 10,
                  'BYTES_DE_VOLTA': 10,
                  'VERIFICACAO': 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'}
                 for i in range(3)]
        g = pres.portao(itens, 3, {})
        self.assertEqual(g['STATE'], 'CLOSED')
        self.assertEqual(g['BYTES_VERIFIED_REMOTELY'], g['BYTES_EXPECTED'])

    def test_sem_credencial_o_envio_recusa_e_diz_o_que_falta(self):
        antes = {k: os.environ.pop(k, None)
                 for k in ('SUPABASE_URL', 'SUPABASE_SECRET_KEY')}
        try:
            _, _, faltam = pres.autenticacao()
            self.assertEqual(sorted(faltam), ['SUPABASE_SECRET_KEY', 'SUPABASE_URL'])
        finally:
            for k, v in antes.items():
                if v is not None:
                    os.environ[k] = v


# ────────────────────── autenticação: a cicatriz do "Invalid Compact JWS"
FAKE_SECRET = 'sb_secret_' + 'z' * 40
FAKE_JWT = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
            'eyJyb2xlIjoic2VydmljZV9yb2xlIn0.' + 'a' * 43)


class FormatoDaChave(unittest.TestCase):
    """SECRET KEY ≠ JWT."""

    def test_classifica_pelo_prefixo_sem_decodificar(self):
        self.assertEqual(pres.classificar_chave(FAKE_SECRET), pres.NEW_SECRET_KEY)
        self.assertEqual(pres.classificar_chave(FAKE_JWT),
                         pres.LEGACY_SERVICE_ROLE_JWT)

    def test_chave_publica_e_anon_sao_recusadas(self):
        """Preservar exige escrita. Chave pública falharia no meio do lote."""
        for k in ('sb_publishable_' + 'y' * 30, 'anon', '', None, 'abc123'):
            self.assertEqual(pres.classificar_chave(k), pres.UNKNOWN_KEY_FORMAT)

    def test_formato_desconhecido_nao_produz_cabecalho(self):
        with self.assertRaises(ValueError):
            pres.cabecalhos('abc123', pres.UNKNOWN_KEY_FORMAT)


class CabecalhoDeAutenticacao(unittest.TestCase):
    """A · sb_secret_ nunca vira Authorization: Bearer sb_secret_..."""

    def test_chave_nova_vai_so_em_apikey(self):
        """O defeito medido: o Storage tira o "Bearer ", entrega a uma
        biblioteca JOSE, e ela rejeita antes de olhar permissão nenhuma."""
        h = pres.cabecalhos(FAKE_SECRET, pres.NEW_SECRET_KEY)
        self.assertEqual(h['apikey'], FAKE_SECRET)
        self.assertNotIn('Authorization', h)

    def test_nenhum_cabecalho_carrega_bearer_com_chave_nova(self):
        h = pres.cabecalhos(FAKE_SECRET, pres.NEW_SECRET_KEY)
        for valor in h.values():
            self.assertNotIn('Bearer', str(valor))

    def test_B_jwt_legado_continua_com_os_dois_cabecalhos(self):
        h = pres.cabecalhos(FAKE_JWT, pres.LEGACY_SERVICE_ROLE_JWT)
        self.assertEqual(h['apikey'], FAKE_JWT)
        self.assertEqual(h['Authorization'], 'Bearer ' + FAKE_JWT)

    def test_a_chave_nunca_e_transformada(self):
        for k, f in ((FAKE_SECRET, pres.NEW_SECRET_KEY),
                     (FAKE_JWT, pres.LEGACY_SERVICE_ROLE_JWT)):
            self.assertEqual(pres.cabecalhos(k, f)['apikey'], k)


class SegredoNaoVazaEmTexto(unittest.TestCase):
    """D · o segredo nunca aparece em stdout/stderr."""

    def test_o_saneador_remove_a_chave_inteira_e_os_pedacos(self):
        texto = 'falhou com %s no fim' % FAKE_SECRET
        limpo = pres.sem_segredo(texto, FAKE_SECRET)
        self.assertNotIn(FAKE_SECRET, limpo)
        self.assertNotIn(FAKE_SECRET[:12], limpo)
        self.assertNotIn(FAKE_SECRET[-12:], limpo)
        self.assertIn('<OMITIDO>', limpo)

    def test_o_canario_reprovado_nao_devolve_a_chave(self):
        prova = {'AUTH_CANARY': 'FAIL',
                 'MENSAGEM': pres.sem_segredo('erro com ' + FAKE_JWT, FAKE_JWT)}
        self.assertNotIn(FAKE_JWT, json.dumps(prova))

    def test_rodar_o_plano_nao_imprime_segredo(self):
        import contextlib
        import io
        antes = {k: os.environ.get(k) for k in ('SUPABASE_URL', 'SUPABASE_SECRET_KEY')}
        os.environ['SUPABASE_SECRET_KEY'] = FAKE_SECRET
        os.environ['SUPABASE_URL'] = 'https://exemplo.invalid'
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                url, key, faltam = pres.autenticacao()
                print('KEY_FORMAT =', pres.classificar_chave(key))
            self.assertNotIn(FAKE_SECRET, buf.getvalue())
            self.assertIn('NEW_SECRET_KEY', buf.getvalue())
        finally:
            for k, v in antes.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class CanarioTrancaOEnvio(unittest.TestCase):
    """E · canário reprovado impede QUALQUER PUT/POST de objeto."""

    def setUp(self):
        self.chamadas = []
        self._http_real = pres._http

        def espiao(url, key, metodo, caminho, dados=None, ctype=None,
                   timeout=300, formato=None):
            self.chamadas.append((metodo, caminho))
            return 0, b'nunca deveria ter sido chamado'
        pres._http = espiao

    def tearDown(self):
        pres._http = self._http_real

    def _item(self):
        return [{'OBJETO': 'IT/x/0', 'ARQUIVO_LOCAL': 'data/raw/IT/nao-existe',
                 'SHA256': 'a' * 64, 'BYTES': 1, 'MEDIA_TYPE': 'application/pdf',
                 'ESTADO': 'PENDING'}]

    def test_sem_prova_nenhuma_o_envio_nem_comeca(self):
        with self.assertRaises(pres.CanarioReprovado):
            pres.enviar(self._item(), 'https://x.invalid', FAKE_SECRET)
        self.assertEqual(self.chamadas, [], 'houve chamada HTTP sem canário')

    def test_canario_reprovado_nao_deixa_subir_byte(self):
        with self.assertRaises(pres.CanarioReprovado):
            pres.enviar(self._item(), 'https://x.invalid', FAKE_SECRET,
                        prova={'AUTH_CANARY': 'FAIL', 'HTTP': 400})
        self.assertEqual(self.chamadas, [])

    def test_F_canario_aprovado_deixa_o_pipeline_seguir(self):
        """Com arquivo de verdade no disco, o envio tem de CHEGAR ao POST.

        Sem isto o teste passaria por acidente — o item de mentira falha ao ler
        o arquivo e nunca alcança a rede, o que provaria nada."""
        import hashlib
        import tempfile
        corpo = b'evidencia italiana de mentira'
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False,
                                         dir=os.path.join(RAIZ, 'data', 'raw')) as fh:
            fh.write(corpo)
            caminho = fh.name
        try:
            item = [{'OBJETO': 'IT/adama-website/DOCUMENT/x.pdf',
                     'ARQUIVO_LOCAL': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
                     'SHA256': hashlib.sha256(corpo).hexdigest(),
                     'BYTES': len(corpo), 'MEDIA_TYPE': 'application/pdf',
                     'ESTADO': 'PENDING'}]
            pres.enviar(item, 'https://x.invalid', FAKE_SECRET, verificar=False,
                        prova={'AUTH_CANARY': 'PASS', 'HTTP': 200})
        finally:
            os.unlink(caminho)
        self.assertIn('POST', [m for m, _ in self.chamadas],
                      'com canário PASS o envio tinha de chegar ao POST')
        self.assertTrue(any('/storage/v1/object/' in c for _, c in self.chamadas))

    def test_o_canario_de_verdade_e_somente_leitura(self):
        pres._http = lambda *a, **k: (self.chamadas.append((a[2], a[3])) or (200, b'[]'))
        prova = pres.canario('https://x.invalid', FAKE_SECRET)
        self.assertEqual(prova['AUTH_CANARY'], 'PASS')
        self.assertEqual([m for m, _ in self.chamadas], ['GET'])
        self.assertIn('somente leitura', prova['OPERACAO'])

    def test_invalid_compact_jws_e_lido_como_recusa_de_autenticacao(self):
        corpo = (b'{"statusCode":"403","error":"Unauthorized",'
                 b'"message":"Invalid Compact JWS"}')
        pres._http = lambda *a, **k: (400, corpo)
        prova = pres.canario('https://x.invalid', FAKE_SECRET)
        self.assertEqual(prova['AUTH_CANARY'], 'FAIL')
        self.assertTrue(prova['AUTENTICACAO_RECUSADA'])
        self.assertIn('Invalid Compact JWS', prova['MENSAGEM'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
