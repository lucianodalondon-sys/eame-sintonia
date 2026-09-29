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


# Segredo INVENTADO, para as fixtures da tabela do verificador. Montado em
# tempo de execucao pelo mesmo motivo que as outras formas deste ficheiro: este
# ficheiro NAO esta em `PERMITIDOS`, e uma linha de 16 caracteres junto a
# `api_key=` faria a guarda acusar a propria prova, para sempre.
SEG = monta('Zq7', 'Rb2Wn5', 'Tk8Lm3P')


class FormasDeSegredo(unittest.TestCase):

    def _casa(self, texto):
        # Usa o MESMO laco da guarda (`_varre_texto`), e nao uma copia.
        # A copia divergia: foi assim que os testes ficaram verdes enquanto a
        # guarda deixava um ficheiro INTEIRO cego — o verificador apanhou-o.
        nome, _ = guarda._varre_texto(texto)
        return nome

    def _pega(self, texto, esperado):
        achado = self._casa(texto)
        self.assertIsNotNone(achado, f"a guarda nao viu: {esperado}")
        self.assertIn(esperado.split()[0].lower(), achado.lower(),
                      f"viu, mas classificou como {achado!r} em vez de {esperado!r}")

    def _ignora(self, texto, porque):
        self.assertIsNone(self._casa(texto), f"falso positivo: {porque}")

    # ── A TABELA DO VERIFICADOR INDEPENDENTE (VERIF-GUARDA-5e05963d3) ─────
    # Oito formas que a candidata ANTERIOR deixava escapar, todas por a paridade
    # de aspas cruas disparar pelo motivo errado — apostrofo em prosa, aspa
    # escapada, aspa tripla, tipo de aspa trocado. E mais dois casos que exigem
    # a CONTINUACAO da busca depois de um casamento perdoado.
    #
    #     A FORMA SEM A SITUACAO NAO BASTA — e a SITUACAO SEM A CONTINUACAO
    #     TAMBEM NAO. Ficam os dois, porque os dois foram medidos.
    def test_m2_tres_aspas_antes(self):
        self._pega(monta("x = 'a'; y = 'b; api", "_key = '+", SEG, "'"), "chave de API")

    def test_m3_apostrofo_dentro_de_aspa_dupla(self):
        self._pega(monta('msg = "it\'s fine"; api', '_key = "+', SEG, '"'), "chave de API")

    def test_m4_aspa_dupla_dentro_de_aspa_simples(self):
        self._pega(monta('msg = \'a"b\'; api', '_key = "+', SEG, '"'), "chave de API")

    def test_m5_aspa_escapada_antes(self):
        self._pega(monta("msg = 'don\\'t'; api", '_key = "+', SEG, '"'), "chave de API")

    def test_m6_prosa_com_apostrofo(self):
        self._pega(monta("Don't forget: api", '_key="+', SEG, '"'), "chave de API")

    def test_m6b_prosa_com_apostrofo_E_segredo_partido_em_linhas(self):
        """O caso que obriga a VARREDURA DE LITERAIS a existir.

        Medido: sem este, trocar a varredura pela contagem crua de aspas NAO
        reprovava nada — os m2..m8 estavam protegidos pela condicao de linha, e
        a varredura ficava sem prova. Aqui as duas condicoes se cruzam:

            apostrofo em prosa (a contagem crua diz «impar, fecha»)
            + valor que atravessa a linha (a condicao de linha aceita)
            + valor com forma de codigo (o `+` do inicio)

        A contagem crua absolve; a varredura de literais ve que a aspa consumida
        e `"` dentro de um literal aberto com `'` — nao a que o fecha.
        """
        texto = monta("Don't forget: api", '_key = "+', "\n", SEG, '"')
        self._pega(texto, "chave de API")

    def test_m7_abertura_de_aspa_tripla(self):
        self._pega(monta('s = """api', '_key = "+', SEG, '"'), "chave de API")

    def test_m8_apostrofo_mais_chamada(self):
        self._pega(monta('msg = "it\'s"; api', '_key = "quote(', SEG, ')"'), "chave de API")

    def test_X_casamento_perdoado_nao_pode_cegar_o_ficheiro(self):
        """O achado GRAVE: a espuria na 1a linha e o segredo real na 2a.

        O primeiro casamento ENGOLIA o segredo verdadeiro dentro do proprio
        espaco — por isso retomar depois da ASPA CONSUMIDA, e nao depois do
        casamento, e o que decide se a guarda ve ou nao.
        """
        self._pega(monta("url += '&api", "_key=' + f(x)\n", "api", "_key = '", SEG, "'"),
                   "chave de API")

    def test_X_espuria_depois_do_segredo(self):
        self._pega(monta("api", "_key = '", SEG, "'\nurl += '&api", "_key=' + f(x)"),
                   "chave de API")

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

    # ── CÓDIGO NÃO É SEGREDO — SEM ENCOLHER O ALCANCE DO VALOR ────────────
    # Medido em produção (`servico-20260923-0923`), `coleta/pesquisadores_t6.py:747`.
    # O padrão encontra uma aspa depois de `api_key=`, mas é a aspa que FECHA o
    # nome, não a que ABRE o valor. A classe do valor atravessa então a linha e
    # o `\n`, e o que a guarda lê como «segredo» é um pedaço de CÓDIGO.
    #
    #     A ASPA QUE O PADRÃO ENCONTRA PODE SER A QUE FECHA O NOME.
    #
    # A cura NÃO é proibir o `\n` na classe — isso calaria o falso positivo e
    # cegaria a guarda para um segredo partido em linhas. É reconhecer que o
    # valor apanhado é uma EXPRESSÃO. Estes três testes são os que morrem se
    # alguém tirar esse reconhecimento.
    def test_concatenacao_de_codigo_nao_e_segredo(self):
        # Fiel à produção: o valor só para na aspa SEGUINTE, que vive linhas
        # abaixo. Foi assim que a guarda leu código como se fosse segredo.
        linha = monta("url += '&api", "_key=' + urllib.parse.", "quote(chave)\n",
                      "    return CP._get(url)\n", "    \"\"\"docstring\"\"\"")
        self._ignora(linha, "o valor e a CONCATENACAO de um pedaco de codigo, nao um literal")

    # ── PARIDADE COM A PRODUÇÃO: DOIS FALSOS POSITIVOS QUE JÁ EXISTIAM ────
    # A primeira versão desta cura prometia calar estas duas formas. Era
    # promessa a mais: MEDIDO contra a produção (`e24139702`), ela acusa as
    # duas. Alargar a exclusão para as calar seria exactamente a regressão que
    # o coordenador proíbe — deixar passar o que o detector de hoje apanha.
    #
    #     UM FALSO POSITIVO ANTIGO NÃO SE CONSERTA DE CARONA NUMA MISSÃO
    #     QUE PEDIU OUTRA COISA. Conserta-se a pedido próprio, com a guarda
    #     antiga como juiz — que é o que estes dois testes fixam.
    #
    # Ficam registados, e não escondidos: se alguém os quiser calar um dia,
    # o sítio é aqui, e o preço é dizer por que razão já não é regressão.
    def test_chamada_no_valor_e_apanhada_como_na_producao(self):
        self._pega("sessionid=" + monta("os.environ.", "get('SINTONIA_SID')"),
                   "sessionid")

    def test_f_string_e_apanhada_como_na_producao(self):
        self._pega("sessionid=" + monta("f\"{token_", "da_sessao}\""),
                   "sessionid")

    # ── E O ALCANCE CONTINUA INTEIRO ──────────────────────────────────────
    # A fixture é FALSA e declara-se falsa NO PRÓPRIO VALOR (`isto_nao_e_segredo`),
    # como manda a correção do house guard — mas o marcador vive na SEGUNDA
    # linha, e a isenção por linha olha a linha onde o casamento COMEÇA. Logo
    # não isenta. Se alguém encurtar a classe do valor para parar no `\n`, o
    # padrão deixa de casar e este teste reprova — que é precisamente o que
    # tem de acontecer.
    def test_segredo_partido_em_linhas_continua_a_ser_apanhado(self):
        texto = monta("api", "_key = \"", "Ab1Cd2Ef3Gh4Ij5K", "\n",
                      "isto_nao_e_segredo", "\"")
        self._pega(texto, "chave de API")

    def test_segredo_partido_com_aspas_simples_tambem(self):
        texto = monta("client", "_secret = '", "Zq7Wx8Yv9Ut0Sr1P", "\n",
                      "continua_aqui_o_valor", "'")
        self._pega(texto, "chave de API")

    def test_valor_que_apenas_contem_a_palavra_mais_abaixo(self):
        """O controle positivo do falso positivo original.

        A MESMA forma de produção, com o valor a ser um literal REAL em vez de
        uma concatenação: aqui a exclusão de código NÃO pode disparar.
        """
        texto = monta("api", "_key='", "Ab1Cd2Ef3Gh4Ij5K", "'")
        self._pega(texto, "chave de API")

    # ── A GUARDA ANTIGA É O JUÍZ: NADA PODE ESCAPAR QUE ELA APANHAVA ──────
    # A primeira versão desta cura reconhecia a FORMA do código e absolvia
    # tudo o que começasse por `+`, por `nome(` ou por `f"`. Medido contra a
    # guarda anterior, caso a caso, isso deixava escapar CINCO formas que ela
    # apanhava. Reconhecer a forma não chegava — era preciso reconhecer a
    # SITUAÇÃO: a aspa consumida é de FECHO, ou abre mesmo um valor?
    #
    #     UM SEGREDO QUE COMECA POR `+` CONTINUA A SER UM SEGREDO.
    #     EM BASE64, `+` É TÃO COMUM COMO QUALQUER OUTRA LETRA.
    #
    # Estes cinco são a lista, um a um. Se algum voltar a escapar, a cura
    # alargou outra vez.
    def test_segredo_que_comeca_por_mais(self):
        self._pega(monta("api", '_key="', "+Ab1Cd2Ef3Gh4Ij5K", '"'), "chave de API")

    def test_segredo_com_parenteses_no_valor(self):
        self._pega(monta("api", '_key="', "abc(def)ghijkl", '"'), "chave de API")

    def test_segredo_com_nome_e_parentese(self):
        self._pega("sessionid=" + monta("token", "(abc123456)"), "sessionid")

    def test_valor_que_so_parece_f_string(self):
        self._pega("sessionid=" + monta('f"', "nao_isto", '"'), "sessionid")

    def test_segredo_partido_em_linhas_comecando_por_mais(self):
        self._pega(monta("api", '_key="', "+Ab1Cd2Ef3Gh4Ij5K", "\n", "resto_do_segredo", '"'),
                   "chave de API")

    def test_a_concatenacao_continua_calada(self):
        """O contraponto: o falso positivo de produção TEM de continuar calado.

        Sem esta, os cinco acima poderiam ser "curados" desligando a exclusão —
        e aí a guarda voltava a gritar sobre código legítimo.
        """
        linha = monta("url += '&api", "_key=' + urllib.parse.", "quote(chave)\n",
                      "    return CP._get(url)\n", "    \"\"\"docstring\"\"\"")
        self._ignora(linha, "a aspa consumida FECHA o nome; o valor e codigo")


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
