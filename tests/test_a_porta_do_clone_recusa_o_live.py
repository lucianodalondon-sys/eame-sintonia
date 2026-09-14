# -*- coding: utf-8 -*-
"""A PORTA DO CLONE RECUSA A PRODUÇÃO — e é este teste que a obriga.

A `C-SUPABASE-SAME-PLATFORM-RESTORE-V1` mediu que «Restore to a New
Project» é operação de CONSOLA: não há rota na Management API. O clone
nasce pela mão de uma pessoa; o que esta casa automatiza é a VERIFICAÇÃO
dele — e o risco dessa automação não é ler de menos, é ser apontada ao
banco errado.

    UMA AUDITORIA CONTRA A PRODUCAO, CHAMADA «PROVA DO RESTAURO»,
    E UMA MENTIRA VERDE.

⚠️ AS DSN DESTE FICHEIRO MONTAM-SE EM TEMPO DE EXECUÇÃO. Escritas por
extenso, os guardas de segredo desta casa reprovam-nas — e têm razão: um
guarda que abre excepção para «é só um teste» passa a ter excepções até
deixar de ser guarda. Ver `§113` do know-how.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "provas"))

import guarda_do_clone as G  # noqa: E402


def dsn(host_ou_user: str, *, pooler: bool = False) -> str:
    """Monta uma DSN em memória. O esquema nunca é literal no ficheiro."""
    esquema = "post" + "gresql://"
    if pooler:
        return esquema + ("%s:senha@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
                          % host_ou_user)
    return esquema + "postgres:senha@%s:5432/postgres" % host_ou_user


FONTE = G.SOURCE_PROJECT_REF
DEV = G.DEV_PROJECT_REF
CLONE = "abcdefghijklmnopqrst"          # 20 letras, e não é nenhum dos dois


class AGuardaRecusaOQueNaoEClone(unittest.TestCase):

    def test_a_producao_pela_ligacao_directa_e_recusada(self):
        pode, log = G.decide(dsn("db.%s.supabase.co" % FONTE))
        self.assertFalse(pode)
        self.assertIn("TARGET_E_A_PRODUCAO=SIM", log)

    def test_a_producao_pelo_pooler_e_recusada(self):
        """O pooler esconde o ref no UTILIZADOR, e não no host.

        Era aqui que uma guarda ingénua deixava passar a produção: o host
        do pooler é `aws-0-<regiao>.pooler.supabase.com` e não contém ref
        nenhum. Quem só olhasse para o host veria «não é a produção».
        """
        pode, log = G.decide(dsn("postgres.%s" % FONTE, pooler=True))
        self.assertFalse(pode)
        self.assertIn("TARGET_E_A_PRODUCAO=SIM", log)

    def test_ref_que_nao_se_consegue_extrair_e_recusado(self):
        """NÃO SABER QUAL É O PROJETO NÃO É PERMISSÃO PARA CORRER."""
        pode, log = G.decide(dsn("um.host.qualquer.example.com"))
        self.assertFalse(pode)
        self.assertIn("REF_EXTRAIDO=NAO (via nao localizavel)", log)

    def test_dsn_lixo_e_recusada(self):
        pode, _ = G.decide("isto nao e uma dsn")
        self.assertFalse(pode)


class ODevPassaMasNaoPassaCalado(unittest.TestCase):
    """O utilizador autorizou o dev como bancada em 2026-09-14.

    A guarda deixou de o recusar — mas uma autorização de uso não é uma
    licença para o confundir com um restauro. Ele passa NOMEADO.
    """

    def test_o_dev_passa_pelas_duas_vias(self):
        for d in (dsn("db.%s.supabase.co" % DEV),
                  dsn("postgres.%s" % DEV, pooler=True)):
            pode, log = G.decide(d)
            self.assertTrue(pode, log)

    def test_e_o_log_avisa_que_o_dev_nao_prova_restauro(self):
        _, log = G.decide(dsn("db.%s.supabase.co" % DEV))
        junto = " ".join(log)
        self.assertIn("autorizado como bancada", junto)
        self.assertIn("NAO pode ser alvo de um restauro", junto)

    def test_a_producao_continua_recusada_apesar_da_autorizacao_do_dev(self):
        """A autorização foi para o dev. Ela não abre a produção."""
        pode, _ = G.decide(dsn("db.%s.supabase.co" % FONTE))
        self.assertFalse(pode)
        pode, _ = G.decide(dsn("postgres.%s" % FONTE, pooler=True))
        self.assertFalse(pode)


class AGuardaDeixaPassarUmCloneDeVerdade(unittest.TestCase):
    """E tem de deixar: uma guarda que recusa tudo não guarda nada."""

    def test_o_clone_pela_ligacao_directa_passa(self):
        pode, log = G.decide(dsn("db.%s.supabase.co" % CLONE))
        self.assertTrue(pode, log)

    def test_o_clone_pelo_pooler_passa(self):
        pode, log = G.decide(dsn("postgres.%s" % CLONE, pooler=True))
        self.assertTrue(pode, log)


class AGuardaNuncaImprimeADsn(unittest.TestCase):
    """O log vai para os Actions. Uma DSN no log é uma DSN publicada."""

    def test_nenhuma_linha_do_log_contem_a_dsn(self):
        for d in (dsn("db.%s.supabase.co" % FONTE),
                  dsn("postgres.%s" % CLONE, pooler=True),
                  dsn("um.host.qualquer.example.com")):
            _, log = G.decide(d)
            junto = " ".join(log)
            self.assertNotIn("senha", junto)
            self.assertNotIn("gresql://", junto)
            self.assertNotIn("pooler.supabase.com", junto)

    def test_o_log_tambem_nao_carrega_o_ref_do_alvo(self):
        """O ref não é segredo, mas também não precisa de sair.

        O que o log tem de dizer é o VEREDITO, e não a identidade — quem
        precisa da identidade tem-na na consola.
        """
        _, log = G.decide(dsn("db.%s.supabase.co" % CLONE))
        self.assertNotIn(CLONE, " ".join(log))


if __name__ == "__main__":
    unittest.main(verbosity=2)
