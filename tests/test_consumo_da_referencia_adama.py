"""A Intelligence lê a referência da ADAMA sem virar dona dela.

O que estes testes protegem não é a leitura — ler é fácil. É a **fronteira de
escrita**: o dia em que alguém achar mais prático cunhar um id de produto aqui
dentro, porque «é só para o cruzamento», e a casa passar a ter duas respostas
para a pergunta «que produto é este?».

    QUEM PODE ESCREVER A IDENTIDADE ACABA POR ESCREVE-LA.
"""
import ast
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "provas"))

from consumo_da_referencia_adama import (   # noqa: E402
    AUTORIDADE, CONTRATO, DONO_DO_PRODUCT_ID, MODULOS_DA_INTELLIGENCE,
    NAO_SEI_DELES, medir)


def ficheiro(rel):
    return os.path.join(RAIZ, rel.replace("/", os.sep))


class AReferenciaEstaLegivel(unittest.TestCase):

    def test_a_casa_existe_e_abre(self):
        r = medir()
        self.assertEqual(CONTRATO, r["CONTRATO"])
        self.assertEqual(9, len(r["TABELA"]))

    def test_cada_ficheiro_tem_a_chave_que_o_contrato_diz_que_manda(self):
        """Se falhar, `medir()` já levantou `LeiViolada` com o nome da chave."""
        for t in medir()["TABELA"]:
            self.assertGreater(t["LINHAS"], 0, t["FICHEIRO"])

    def test_a_contagem_declarada_bate_com_as_linhas_contadas(self):
        """`COUNT` é uma promessa. Contar é conferi-la.

        Um ficheiro que diz 602 e traz 600 não é um ficheiro com dois a menos:
        é um ficheiro cujo número deixou de poder ser citado.
        """
        for t in medir()["TABELA"]:
            if t["DECLARADO"] is None:
                continue
            self.assertEqual(t["DECLARADO"], t["LINHAS"],
                             f"{t['FICHEIRO']}: COUNT nao bate com as linhas")

    def test_os_51_produtos_tem_id_unico(self):
        r = medir()
        self.assertEqual(51, r["PRODUTOS"])
        self.assertTrue(r["IDS_UNICOS"], "dois produtos com o mesmo ID")


class ANaoCunhaIdentidade(unittest.TestCase):
    """INT-LAW-031 — a Intelligence não cunha identidade upstream."""

    def test_o_dono_do_product_id_nao_e_esta_casa(self):
        self.assertEqual("referencia/adama/PRODUCT-MASTER.json",
                         DONO_DO_PRODUCT_ID)
        self.assertTrue(os.path.exists(ficheiro(DONO_DO_PRODUCT_ID)))

    def test_a_prova_declara_se_a_si_propria_como_consumidor(self):
        r = medir()
        self.assertEqual("CONSUMIDOR", r["PAPEL_DA_INTELLIGENCE"])
        self.assertFalse(r["CUNHA_IDENTIDADE"])
        self.assertFalse(r["COPIA_DADOS"])

    def test_a_lista_de_modulos_declarados_aponta_para_ficheiros_que_existem(self):
        """Uma lista que envelhece em silêncio deixa de guardar o que promete."""
        sumidos = [m for m in MODULOS_DA_INTELLIGENCE
                   if not os.path.exists(ficheiro(m))]
        self.assertEqual([], sumidos,
                         "declarados como da Intelligence, mas nao existem: %s"
                         % sumidos)

    def test_nenhum_modulo_da_intelligence_escreve_em_referencia(self):
        """Medido na árvore, não prometido no comentário.

        Procura escrita real — `open(..., 'w'/'a')`, `write_text`, `json.dump`
        — em módulos da Intelligence que nomeiem a casa da ADAMA.

        ⚠️ Só os DECLARADOS. `provas/` guarda também o red team do dono da
        referência, que escreve lá por direito — ver `MODULOS_DA_INTELLIGENCE`.
        """
        escritores = []
        for rel in MODULOS_DA_INTELLIGENCE:
            p = ficheiro(rel)
            txt = open(p, encoding="utf-8", errors="replace").read()
            if "referencia/adama" not in txt and "referencia\", \"adama" not in txt:
                continue
            for no in ast.walk(ast.parse(txt, filename=p)):
                if not isinstance(no, ast.Call):
                    continue
                alvo = getattr(no.func, "attr", None) or \
                    getattr(no.func, "id", None)
                if alvo in ("write_text", "dump", "writelines", "write"):
                    escritores.append(f"{rel}:{no.lineno} {alvo}()")
                elif alvo == "open":
                    modos = [a.value for a in no.args[1:]
                             if isinstance(a, ast.Constant)]
                    if any("w" in str(m) or "a" in str(m) for m in modos):
                        escritores.append(f"{rel}:{no.lineno} open(w)")
        self.assertEqual([], escritores,
                         "a Intelligence escreve onde so devia ler: %s"
                         % escritores)

    def test_o_red_team_do_dono_continua_a_poder_escrever(self):
        """O contrapeso do teste acima: a regra não pode virar uma proibição
        universal.

        Se um dia o red team da referência deixar de escrever, não é limpeza:
        é o ataque por mutação a ter sido desligado, e catorze provas a passar
        por não fazerem nada.
        """
        p = ficheiro("provas/red_team_adama_referencia.py")
        if not os.path.exists(p):
            self.skipTest("o red team do dono nao esta nesta arvore")
        self.assertNotIn("provas/red_team_adama_referencia.py",
                         MODULOS_DA_INTELLIGENCE,
                         "o red team do dono foi reclamado pela Intelligence")
        txt = open(p, encoding="utf-8", errors="replace").read()
        self.assertIn("def escrever", txt,
                      "o red team perdeu a escrita: o ataque por mutacao "
                      "deixou de acontecer")

    def test_nao_nasceu_um_segundo_ficheiro_de_identidade_de_produto(self):
        """Não pode haver uma cópia da referência dentro da Intelligence."""
        proibidos = []
        for pasta in ("provas", "motor", "controle", "docs/intelligence",
                      "research/intelligence"):
            base = ficheiro(pasta)
            for raiz, _, nomes in os.walk(base) if os.path.isdir(base) else []:
                if "__pycache__" in raiz:
                    continue
                for n in nomes:
                    if n in AUTORIDADE:
                        proibidos.append(os.path.join(raiz, n))
        self.assertEqual([], proibidos,
                         "copia da referencia dentro da Intelligence: %s"
                         % proibidos)


class ONaoSeiDelesContinuaNaoSei(unittest.TestCase):
    """INT-LAW-112 — NÃO SEI não vira FALSO, nem vira AUSÊNCIA."""

    def test_o_vocabulario_de_ignorancia_esta_declarado(self):
        self.assertIn("UNKNOWN", NAO_SEI_DELES)
        self.assertIn("MULTIPLE", NAO_SEI_DELES)

    def test_unknown_e_multiple_existem_mesmo_nos_dados(self):
        """Se deixarem de existir, alguém os resolveu — e isso tem dono.

        `MULTIPLE` é o caso do registo 017995, vendido sob dois nomes. Se um
        dia vier um só, não é limpeza: é um produto apagado.
        """
        d = json.load(open(ficheiro("referencia/adama/REGISTRATIONS.json"),
                           encoding="utf-8"))
        valores = {r.get("ADAMA_PRODUCT_ID") for r in d["RECORDS"]}
        self.assertIn("UNKNOWN", valores,
                      "as 560 autorizacoes sem produto de catalogo sumiram")
        self.assertIn("MULTIPLE", valores,
                      "o registo com dois nomes comerciais sumiu")

    def test_currently_marketable_continua_unknown_em_todas(self):
        """A resposta honesta do dataset. Derivá-la seria inventar."""
        d = json.load(open(ficheiro("referencia/adama/REGISTRATIONS.json"),
                           encoding="utf-8"))
        vendaveis = {r.get("CURRENTLY_MARKETABLE") for r in d["RECORDS"]}
        self.assertEqual({"UNKNOWN"}, vendaveis,
                         "alguem derivou 'pode vender' de 'papel activo'")


class OQueAindaNaoDaParaFazer(unittest.TestCase):

    def test_o_cruzamento_declara_se_impossivel_e_diz_porque(self):
        """Uma impossibilidade sem motivo escrito vira, com o tempo, um bug."""
        r = medir()
        self.assertFalse(r["CRUZAMENTO_POSSIVEL_HOJE"])
        self.assertIn("SUBJECT_ID", r["PORQUE_NAO"])

    def test_o_motivo_bate_com_a_fronteira_medida_na_espinha(self):
        """O porquê não é uma frase: é uma consequência de um campo que falta.

        Quando `SUBJECT_ID` passar a atravessar, este teste falha — e é o
        sinal de que o cruzamento deixou de ser palpite.
        """
        from espinha_da_intelligence import (CAMPOS_DO_READY,
                                             CAMPOS_QUE_NAO_ATRAVESSAM)
        self.assertIn("SUBJECT_ID", CAMPOS_QUE_NAO_ATRAVESSAM)
        self.assertNotIn("SUBJECT_ID", CAMPOS_DO_READY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
