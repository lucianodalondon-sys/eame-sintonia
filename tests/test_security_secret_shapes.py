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
