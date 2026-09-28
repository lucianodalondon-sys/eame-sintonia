#!/usr/bin/env python3
"""RED TEAM DA GUARDA DE CREDENCIAL — as formas que ESTE projecto usa.

A guarda nasceu no SCRAP e cobria cookie e cabecalho. O censo de seguranca
acrescentou as chaves de plataforma que o SINTONIA realmente usa. Esta prova
existe para que nenhuma delas se perca numa refactorizacao silenciosa.

    SECURITY TOOL EXISTS != SECURITY CONTROL WORKS.

Nenhuma credencial real e usada. Todas as formas sao MONTADAS EM TEMPO DE
EXECUCAO, a partir de pedacos, e nunca escritas na arvore versionada — porque

    FIXTURE WITH SECRET SHAPE IS SECRET TO THE SCANNER,

e uma fixture commitada faria a propria guarda acusar o repositorio para sempre.

    python3 -m unittest tests.test_security_secret_shapes -v
"""
import importlib.util, os, pathlib, unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("social_guarda", RAIZ / "guarda" / "social_guarda.py")
guarda = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guarda)


def monta(*partes):
    """Junta a forma so aqui dentro. Em disco, nunca existe inteira."""
    return "".join(partes)


class FormasDeSegredo(unittest.TestCase):

    def _casa(self, texto):
        for nome, padrao in guarda.CONTEUDO_PROIBIDO:
            m = padrao.search(texto)
            if m and guarda._valor_e_segredo(m.group(0)) \
                    and not guarda._linha_declara_falso(texto, m.start()):
                return nome
        return None

    def _pega(self, texto, esperado):
        achado = self._casa(texto)
        self.assertIsNotNone(achado, f"a guarda nao viu: {esperado}")
        self.assertIn(esperado.split()[0].lower(), achado.lower(),
                      f"viu, mas classificou como {achado!r} em vez de {esperado!r}")

    def _ignora(self, texto, porque):
        self.assertIsNone(self._casa(texto), f"falso positivo: {porque}")

    # ── as formas que este projecto usa ───────────────────────────────────
    def test_chave_supabase(self):
        self._pega('K = "' + monta("sb_", "secret_", "A" * 24) + '"', "chave Supabase")

    def test_token_de_acesso_supabase(self):
        self._pega("t=" + monta("sbp_", "a1b2c3d4" * 5), "token")

    def test_token_github(self):
        self._pega("t=" + monta("ghp_", "A1b2C3d4" * 4 + "abcd"), "token GitHub")

    def test_token_github_fine_grained(self):
        self._pega("t=" + monta("github_pat_", "A1b2C3d4e5" * 4), "token GitHub")

    def test_token_apify(self):
        self._pega("t=" + monta("apify_api_", "Ab1" * 10), "token Apify")

    def test_chave_google(self):
        self._pega("k=" + monta("AIza", "Sy" + "Ab1cD2" * 6), "chave de API Google")

    def test_chave_aws(self):
        self._pega("k=" + monta("AKIA", "ABCDEFGHIJKLMNOP"), "chave de acesso AWS")

    def test_chave_privada(self):
        self._pega(monta("-----BEGIN ", "RSA ", "PRIVATE KEY-----"), "chave privada")

    def test_json_web_token(self):
        self._pega("h=" + monta("eyJ", "hbGciOiJIUzI1NiJ9", ".", "eyJzdWIiOiIxIn0", ".", "c2lnbmF0dXJh"),
                   "JSON Web Token")

    def test_dsn_remoto(self):
        self._pega(monta("postgresql://", "utilizador", ":", "K7x2Pq9Lm4", "@", "db.remoto.acme-corp.net:5432/p"),
                   "DSN")

    def test_cabecalho_authorization(self):
        self._pega("Authorization: Bearer " + monta("A1b2C3d4", "E5f6G7h8"), "Authorization")

    def test_cookie(self):
        self._pega("Cookie: " + monta("sessionid=", "A1b2C3d4E5f6"), "cabeçalho")

    # ── e o que NAO pode ser acusado ──────────────────────────────────────
    def test_referencia_a_variavel_nao_e_segredo(self):
        self._ignora("Authorization: Bearer $SUPABASE_SECRET_KEY",
                     "referencia a variavel e o jeito CERTO de escrever")

    def test_expressao_de_workflow_nao_e_segredo(self):
        self._ignora("SUPABASE_SECRET_KEY: ${{ secrets.SUPABASE_SECRET_KEY }}",
                     "expressao de workflow nao carrega valor")

    def test_dsn_local_descartavel_nao_e_segredo(self):
        self._ignora(monta("postgresql://", "postgres:postgres", "@localhost:5432/descartavel"),
                     "banco que nasce e morre no job; a senha e visivel de proposito")

    def test_dsn_de_127_nao_e_segredo(self):
        self._ignora(monta("postgresql://", "p:x", "@127.0.0.1:5432/d"), "loopback")

    def test_valor_declarado_falso_nao_e_segredo(self):
        self._ignora("FAKE_JWT = '" + monta("eyJ", "hbGciOiJIUzI1NiJ9", ".", "eyJzdWIiOiIxIn0", ".", "c2lnbmF0dXJh") + "'",
                     "a constante declara-se falsa a quem le e a guarda ao mesmo tempo")

    def test_marcador_de_redaccao_nao_e_segredo(self):
        self._ignora("Cookie: <REDIGIDO pela guarda>",
                     "redigir a origem nao pode virar um achado novo")

    # ── O NOME DO PARAMETRO NAO E A CHAVE (corrigido em 2026-09-28) ───────
    # Medido em `servico-20260923-0923` @ `a2aa73f4`: `coleta/pesquisadores_t6.py`
    # linha 733 monta a query string — `url += '&api_key=' + quote(chave)` — e a
    # guarda acusava AQUELA linha. O padrao antigo nao excluia a quebra de linha
    # da classe do valor, logo o «valor» comecava em `&api_key=` e so parava na
    # aspa seguinte, SETE LINHAS ABAIXO, dentro de uma docstring.
    #
    #     UM PADRAO QUE ATRAVESSA A LINHA ACUSA O CODIGO QUE MONTA A URL.
    #
    # O falso positivo nao era cosmetico: o passo `0` do `scrap-social` morria
    # antes do passo `1`, e NENHUMA fase da linha de producao chegava a correr —
    # o passo `0a` dizia `SCRAP_CODE_PRESENT=YES` e a fase ficava `skipped`.
    #
    #     UM PORTAO QUE FALHA PELA RAZAO ERRADA ENSINA A IGNORAR O PORTAO.
    #
    # As duas faces ficam aqui: a linha legitima que NAO casa, e a chave escrita
    # de verdade, numa linha continua, que CONTINUA a casar. Sem a segunda, esta
    # correcao seria um afrouxamento sem contraprova.
    def test_parametro_da_query_nao_e_chave(self):
        codigo = (
            "def _pedir(url, chave=None):\n"
            "    if chave:\n"
            "        url += '&" + monta("api_", "key=") + "' + urllib.parse.quote(chave)\n"
            "    return CP._get(url)\n"
            "\n"
            "\n"
            "def rodada_com_rede(n, saida, pausa=PAUSA, chave_openalex=None):\n"
            '    """UMA rodada, <= TETO_POR_DOMINIO pedidos em cada dominio."""\n'
        )
        self._ignora(codigo, "montar `api_key=` na query nao e escrever a chave")

    def test_chave_literal_numa_linha_continua_a_casar(self):
        self._pega(monta("api_", "key = '", "AKfycByA1b2C3d4E5f6") + "'",
                   "chave de API literal")

    def test_o_ficheiro_da_falsa_acusacao_continua_limpo(self):
        """A contraprova no ficheiro REAL, e nao numa forma parecida.

        `coleta/pesquisadores_t6.py` e de outro dono e nao foi alterado: quem
        estava errado era a guarda. Este teste morre se a guarda voltar a
        acusa-lo. Ele vive na linha de producao, por isso um ramo sem ele nao
        pode responder por ele — e o `skip` diz isso em voz alta, em vez de
        fingir um verde que nao mediu nada.
        """
        alvo = RAIZ / "coleta" / "pesquisadores_t6.py"
        if not alvo.is_file():
            self.skipTest("coleta/pesquisadores_t6.py nao existe nesta ref")
        self.assertEqual(guarda.varrer(["coleta/pesquisadores_t6.py"], "TESTE"), [],
                         "a guarda voltou a acusar codigo legitimo")

    # ── O MARCADOR DE CAMINHO TINHA EXCEPCAO E NAO TINHA PROVA ────────────
    # `CONTEUDO_PROIBIDO` isenta `[A-Z]:\Users\(?!<)` desde sempre, e
    # `social_sessao.redigir()` escreve `<CAMINHO-LOCAL>` nesse lugar. O cookie
    # tinha as duas faces provadas; o caminho tinha ZERO. Quando o SECURITY
    # CLOSURE saneou `docs/operacao/ORCA-CONTROL-ROOM-ITALIA.md`, passou a
    # DEPENDER dessa isencao — e uma isencao de que alguem depende sem prova
    # e a proxima a ser apagada sem ninguem dar por ela.
    #
    #     UMA ISENCAO SEM PROVA NAO E UMA REGRA: E UM HABITO.
    #
    # As formas continuam MONTADAS em tempo de execucao, como o resto deste
    # ficheiro: ele NAO esta em `PERMITIDOS`, logo um caminho pessoal escrito
    # inteiro aqui faria a guarda acusar a propria prova, para sempre.
    def test_caminho_pessoal_windows(self):
        self._pega(monta("C:", "\\", "Users", "\\", "Fulano", "\\", "orca"),
                   "caminho pessoal Windows")

    def test_caminho_pessoal_de_outra_conta_tambem(self):
        self._pega(monta("D:", "\\", "users", "\\", "outra.conta", "\\", "tmp"),
                   "caminho pessoal Windows")

    def test_marcador_de_caminho_local_nao_e_segredo(self):
        self._ignora(monta("00  <CAMINHO-LOCAL>", "\\", "orca", "\\", "workspaces"),
                     "e o que redigir() escreve; acusa-lo obrigaria a apagar a linha")

    def test_caminho_sem_perfil_de_utilizador_nao_e_segredo(self):
        self._ignora(monta("05  C:", "\\", "eame-sintonia", "\\", ".claude", "\\", "worktrees"),
                     "nao passa pelo perfil de ninguem: nao carrega nome de conta")


class ArvoreReal(unittest.TestCase):
    def test_a_arvore_versionada_continua_sem_credencial(self):
        """Nao e um teste de unidade: e a medicao, e ela corre a cada commit.
        NOT DETECTED != IMPOSSIBLE TO EXIST — mas nao detectar todos os dias
        vale mais do que nao ter detectado uma vez."""
        achados = guarda.varrer(guarda.rastreados(), "RASTREADO")
        reais = [a for a in achados if a[1].split(":")[0] not in guarda.DIVIDA_CONHECIDA]
        self.assertEqual(reais, [], "credencial nova na arvore versionada")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class RedaccaoEmTempoDeExecucao(unittest.TestCase):
    """SECRET NOT IN GIT != SECRET CANNOT LEAK AT RUNTIME.

    Sao duas perguntas e por isso sao duas provas. A guarda de credencial olha
    a arvore; esta olha o que um programa IMPRIME quando alguma coisa corre mal.
    Um traceback com um DSN dentro vaza tao bem como um ficheiro commitado.

    A prova em si e do SCRAP e e CONSUMIDA, nao copiada — nao ha segundo
    redactor. Mas consumi-la pelo nome exacto da classe seria uma coupling
    frágil: no dia em que o SCRAP reorganizasse os seus testes, o SECURITY CHECK
    ficaria vermelho por uma razao que nao e uma regressao de seguranca.

        UM PORTAO QUE FALHA PELA RAZAO ERRADA ENSINA A IGNORAR O PORTAO.

    Entao procura-se a prova pelo CONTRATO — o que ela promete — e nao pela
    morada. Se ela desaparecer, a mensagem diz isso, e nao outra coisa.
    """

    CONTRATO = ("segredo", "preflight")

    def _encontrar(self):
        import unittest as _u
        achadas = []
        for mod in ("tests.test_youtube_antidrift",):
            try:
                suite = _u.defaultTestLoader.loadTestsFromName(mod)
            except Exception as e:                      # pragma: no cover
                self.fail(f"nao foi possivel carregar {mod}: {e}")
            for t in _u.defaultTestLoader.suiteClass(suite):
                for caso in t:
                    nome = caso.id().rsplit(".", 1)[-1]
                    if all(p in nome for p in self.CONTRATO):
                        achadas.append(caso)
        return achadas

    def test_a_prova_de_redaccao_existe(self):
        achadas = self._encontrar()
        self.assertTrue(achadas,
                        "a prova de redaccao em tempo de execucao desapareceu. "
                        "Ela e do SCRAP e o SECURITY CHECK consome-a: se mudou de "
                        "nome, actualize o CONTRATO; se foi apagada, ha um controlo "
                        "de seguranca a menos e nao um teste a menos.")

    def test_a_prova_de_redaccao_passa(self):
        import unittest as _u
        suite = _u.TestSuite(self._encontrar())
        r = _u.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0).run(suite)
        self.assertTrue(r.wasSuccessful(),
                        f"o segredo vaza em tempo de execucao: {r.failures or r.errors}")
