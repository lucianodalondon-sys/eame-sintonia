# -*- coding: utf-8 -*-
"""A REGUA DE T10 TEM DE SABER DIZER QUE NAO.

    UMA REGRA QUE SO SABE DIZER SIM NAO E REGRA.

Antes desta missao, `admissao.PERGUNTAS_DO_UNIVERSO` conhecia cinco universos
— T3, T4, T5, T7 e T9 — e T10 nao estava la. A porta respondia, com toda a
educacao, «nao ha regra escrita do que conta como T10; sem regra, esta porta
nao inventa uma» → `NAO_SE_APLICA`, a 39 documentos italianos reais. A
educacao escondia que ninguem tinha escrito a pergunta.

O QUE ESTE FICHEIRO GUARDA
--------------------------
As QUATRO respostas, e nao so a boa:

    material valido        -> pode ser SIM
    material insuficiente  -> NAO_SEI      (um indicio nao promove)
    material incompativel  -> NAO          (prova POSITIVA de outro universo)
    material invalido      -> nao entra    (para antes, noutro portao)

E guarda tambem o que NAO pode voltar: os termos que sairam do lexico por
medicao, com o nome de cada um. Um termo que sai sem guarda volta na semana
seguinte, porque «parece obviamente de mercado».

⚠️ OS VALORES ESPERADOS ESTAO ESCRITOS A MAO, E NAO LIDOS DA ESTRUTURA QUE
ESTE FICHEIRO JULGA. Tres vezes na noite de 2026-09-21 o sobrevivente de um
red team nesta casa foi um teste que iterava a constante que verificava — um
teste assim passa depois de a constante ser apagada.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

#: Um documento minimo que passa os QUATRO portoes universais do estagio
#: DOCUMENTO (`legivel`, `origem`, `linhagem`, `identidade`). Sem isto, um
#: teste de universo mede o portao errado: foi assim que a primeira corrida do
#: medidor deu 85 `NAO_SEI` por `linhagem` e nao por vocabulario.
def documento(texto, **extra):
    item = {"artifact_type": "DERIVED",
            "source_id": "IT-T10-018",
            "parent_sha256": "a" * 64,
            "id": "obs:teste",
            "url": "https://exemplo.invalid/noticia",
            "texto": texto}
    item.update(extra)
    return item


# ── OS TEXTOS DO GABARITO, ESCRITOS A MAO ───────────────────────────────────
# Curtos de proposito: cada um existe para exercitar UM ramo, e o que esta la
# dentro le-se de uma vez.
MERCADO_CLARO = (
    "Le quotazioni dell'uva da tavola restano contenute e il prezzo medio "
    "della settimana scende ancora rispetto al 2025.")
MERCADO_UM_SO_INDICIO = (
    "L'azienda ha presentato il nuovo impianto di lavorazione durante la "
    "visita dei tecnici; il prezzo non e stato comunicato.")
PRAGA_CLARA = (
    "La peronospora e l'oidio hanno colpito i vigneti: i tecnici segnalano "
    "una forte infestazione e consigliano il monitoraggio delle trappole.")
NEM_UMA_COISA_NEM_OUTRA = (
    "La sede storica compie cinquant'anni e la famiglia racconta la propria "
    "storia in un libro fotografico.")


class OMaterialValidoPodeSerSim(unittest.TestCase):
    """SIM exige DOIS termos distintos. Um so nunca promove."""

    def test_dois_termos_de_mercado_dao_SIM(self):
        d = adm.decidir(documento(MERCADO_CLARO), "T10", corrida="T-T10")
        self.assertEqual(d.resultado, "SIM")
        self.assertEqual(d.regra, "pertence ao universo")
        # As palavras que promoveram ficam escritas. Um SIM sem prova e um
        # carimbo.
        achadas = set(d.evidencia.get("palavras") or [])
        self.assertIn("quotazion", achadas)
        self.assertIn("prezzo", achadas)

    def test_o_SIM_nao_e_automatico_do_universo(self):
        """⚠️ A REGRA PROIBIDA: `T10 -> SIM`.

        Um texto sem uma unica palavra de mercado, perguntado a T10, nao pode
        sair SIM por o universo ter regua.
        """
        d = adm.decidir(documento(NEM_UMA_COISA_NEM_OUTRA), "T10",
                        corrida="T-T10")
        self.assertNotEqual(d.resultado, "SIM")


class OMaterialInsuficienteDaNaoSei(unittest.TestCase):
    """Um indicio nao promove NEM rejeita."""

    def test_um_termo_so_da_NAO_SEI(self):
        d = adm.decidir(documento(MERCADO_UM_SO_INDICIO), "T10",
                        corrida="T-T10")
        self.assertEqual(d.resultado, "NAO_SEI")
        self.assertEqual(d.evidencia.get("sinais"), 1)

    def test_nenhum_termo_e_nenhum_outro_universo_da_NAO_SEI(self):
        """Vazio de vocabulario NAO e prova de que o item nao pertence."""
        d = adm.decidir(documento(NEM_UMA_COISA_NEM_OUTRA), "T10",
                        corrida="T-T10")
        self.assertEqual(d.resultado, "NAO_SEI")
        self.assertEqual(d.evidencia.get("achado_noutro"), None)


class OMaterialIncompativelDaNao(unittest.TestCase):
    """NAO so com prova POSITIVA de outro universo — nunca por ausencia."""

    def test_texto_de_praga_perguntado_a_T10_da_NAO(self):
        d = adm.decidir(documento(PRAGA_CLARA), "T10", corrida="T-T10")
        self.assertEqual(d.resultado, "NAO")
        self.assertIn("T3", d.evidencia.get("achado_noutro") or {})

    def test_o_mesmo_texto_perguntado_a_T3_da_SIM(self):
        """O par (item, universo) e que decide — nunca o item sozinho."""
        d = adm.decidir(documento(PRAGA_CLARA), "T3", corrida="T-T10")
        self.assertEqual(d.resultado, "SIM")


class OMaterialInvalidoNaoEntra(unittest.TestCase):
    """Para ANTES do universo, e a razao verdadeira fica no livro."""

    def test_sem_texto_para_no_portao_legivel(self):
        item = documento("")
        item.pop("texto")
        d = adm.decidir(item, "T10", corrida="T-T10")
        self.assertEqual(d.resultado, "NAO_SEI")
        self.assertEqual(d.regra, "legivel")

    def test_sem_pai_declarado_para_no_portao_linhagem(self):
        item = documento(MERCADO_CLARO)
        item.pop("parent_sha256")
        d = adm.decidir(item, "T10", corrida="T-T10")
        self.assertEqual(d.resultado, "NAO_SEI")
        self.assertEqual(d.regra, "linhagem")

    def test_sem_universo_declarado_da_NAO_SE_APLICA(self):
        """AUSENCIA DE UNIVERSO != UNIVERSO SEM REGUA."""
        d = adm.decidir(documento(MERCADO_CLARO), "", corrida="T-T10")
        self.assertEqual(d.resultado, "NAO_SE_APLICA")
        self.assertIn("UNIVERSO_NAO_DECLARADO", str(d.motivo))

    def test_universo_sem_regua_continua_a_dizer_que_nao_tem_regua(self):
        """T11 nao tem regua, e a porta continua a NAO inventar uma.

        Escrever T10 nao pode ter ensinado esta porta a responder por
        universos que ninguem escreveu.
        """
        # ERA `T1`; T1 ganhou regua (T1-JANELA, D29 — 1b059679). Mesmo ajuste
        # que o dono fez no teste irmao da fronteira (5bca8493): `T11`
        # continua sem regua, e a pergunta do teste fica a mesma.
        d = adm.decidir(documento(MERCADO_CLARO), "T11", corrida="T-T10")
        self.assertEqual(d.resultado, "NAO_SE_APLICA")
        self.assertIn("nao ha regra escrita", str(d.motivo))


class OLexicoNaoApodrece(unittest.TestCase):
    """As guardas do proprio lexico, medidas e nao opinadas."""

    #: Os termos que SAIRAM por medicao, com a palavra em que casavam. Quem os
    #: quiser de volta tem de apagar tambem a razao.
    EXPULSOS = {
        "dazi": "vive dentro de «redazione», que assina todas as paginas",
        "preco": "vive dentro de «spreco» e de «precoce»",
        "mercato": "casava no MENU do site em 40 de 85 documentos",
        "mercati": "casava no MENU do site em 34 de 85",
        "ingrosso": "casava na nuvem de etiquetas em 30 de 85",
        "grossist": "casava no menu de distribuicao em 31 de 85",
        "export": "casava no bloco «potrebbe interessarti anche»",
        "commercio": "dois de tres usos eram «camera/ministero del commercio»",
        "comercio": "mesma razao, do lado portugues",
        "industria": "nome de um SECTOR, nao um movimento de mercado",
        "atacado": "em portugues tambem e o particio de «atacar»",
        "soci": "casou em «sociale», «social» e «association» — nunca em «soci»",
    }

    def test_nenhum_termo_expulso_voltou_a_nenhum_universo(self):
        for termo, porque in self.EXPULSOS.items():
            for universo, lista in adm.PERGUNTAS_DO_UNIVERSO.items():
                with self.subTest(termo=termo, universo=universo):
                    self.assertNotIn(
                        termo, lista,
                        "«%s» voltou a %s. Ele saiu porque %s"
                        % (termo, universo, porque))

    def test_nenhum_termo_de_T10_cabe_dentro_de_outro_de_T10(self):
        """Uma forma dentro de outra da DOIS sinais a UMA palavra, e a regra
        dos SINAIS_MINIMOS deixa de valer sem ninguem dar por isso."""
        lista = adm.PERGUNTAS_DO_UNIVERSO["T10"]
        for a in lista:
            for b in lista:
                if a != b:
                    with self.subTest(a=a, b=b):
                        self.assertNotIn(a, b)

    def test_nenhum_termo_de_T10_colide_com_outro_universo(self):
        t10 = adm.PERGUNTAS_DO_UNIVERSO["T10"]
        for universo, lista in adm.PERGUNTAS_DO_UNIVERSO.items():
            if universo == "T10":
                continue
            for a in t10:
                for b in lista:
                    with self.subTest(universo=universo, a=a, b=b):
                        self.assertFalse(a in b or b in a,
                                         "«%s» (T10) e «%s» (%s) cruzam-se"
                                         % (a, b, universo))

    def test_a_regua_dos_sinais_continua_a_ser_dois(self):
        """Escrito a mao. Se alguem baixar para 1, este teste cai — e baixar
        para 1 e exactamente como uma regra passa a so saber dizer sim."""
        self.assertEqual(adm.SINAIS_MINIMOS, 2)

    def test_T10_tem_termos_das_duas_linguas_e_do_dono(self):
        """O Atlas e quem diz o que T10 e. Tres conceitos do escopo dele —
        precos, importacoes/exportacoes e commodities — tem de estar la."""
        lista = adm.PERGUNTAS_DO_UNIVERSO["T10"]
        self.assertIn("prezzo", lista)          # it
        self.assertIn("precos", lista)          # pt
        self.assertIn("commodity", lista)       # sem lingua
        self.assertIn("importazion", lista)
        self.assertIn("exportacoes", lista)

    def test_T10_e_um_codigo_que_o_Atlas_conhece(self):
        import territorios as terr
        self.assertTrue(terr.e_canonico("T10"))
        self.assertEqual(terr.nome("T10"), "MARKET / TRADE / INDUSTRY")


if __name__ == "__main__":
    unittest.main()
