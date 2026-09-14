# -*- coding: utf-8 -*-
"""A INTERFACE DE REVISAO NAO PODE DECIDIR, NEM ADIANTAR A RESPOSTA.

Esta pagina existe para uma pessoa que nao le italiano conseguir rever 53
documentos. Ela falha de tres maneiras, e as tres sao silenciosas:

    1. a traducao insinua o rotulo, e a pessoa concorda com a traducao;
    2. o original desaparece, e a traducao vira o dado;
    3. o que a maquina ja «achava» aparece ao lado da pergunta.

    DISPLAY_TRANSLATION != EVIDENCE
    HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT

Estes testes leem o HTML gerado — nao precisam de navegador.
"""
import importlib.util
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "ui_t3", os.path.join(RAIZ, "provas", "ui_revisao_t3_ptbr.py"))
ui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ui)

PAGINA = os.path.join(RAIZ, ui.HTML)


def _sem_espaco(t):
    """Compara o CSS e o JS sem espacos NEM quebras de linha.

    A primeira versao tirava so os espacos, e falhava em toda a
    regra que ocupa duas linhas — reprovando codigo certo.
    """
    return re.sub(r"\s+", "", t)


class OsDadosDaPagina(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = ui.dados()

    def test_sao_os_53_documentos_do_pacote(self):
        pacote = ui._json(ui.PENDENTE)["ITENS"]
        self.assertEqual(len(self.d), 53)
        self.assertEqual([x["DOC_SHA256"] for x in self.d],
                         [x["DOC_SHA256"] for x in pacote])

    def test_nenhum_documento_repetido(self):
        shas = [x["DOC_SHA256"] for x in self.d]
        self.assertEqual(len(shas), len(set(shas)))

    def test_traducao_presente_nos_53(self):
        for x in self.d:
            with self.subTest(item=x["ITEM_ID"]):
                p = x["DISPLAY_TRANSLATION_PTBR"]
                self.assertTrue(p["TITLE"].strip())
                self.assertTrue(p["OPENING"].strip())

    def test_original_preservado_nos_53(self):
        for x in self.d:
            with self.subTest(item=x["ITEM_ID"]):
                o = x["ORIGINAL_EVIDENCE"]
                self.assertTrue(o["TITLE"].strip())
                self.assertTrue(o["OPENING"].strip())

    def test_o_original_e_o_do_pacote_sem_uma_letra_mudada(self):
        pacote = {i["DOC_SHA256"]: i["EVIDENCE"]
                  for i in ui._json(ui.PENDENTE)["ITENS"]}
        for x in self.d:
            with self.subTest(item=x["ITEM_ID"]):
                self.assertEqual(x["ORIGINAL_EVIDENCE"], pacote[x["DOC_SHA256"]])

    def test_a_traducao_nao_e_igual_ao_original(self):
        """Se fossem iguais, ninguem traduziu nada."""
        iguais = [x for x in self.d
                  if x["DISPLAY_TRANSLATION_PTBR"]["OPENING"]
                  == x["ORIGINAL_EVIDENCE"]["OPENING"]]
        self.assertEqual(iguais, [], "ha fichas por traduzir")

    def test_a_traducao_nao_opina(self):
        proibidas = ("provavelmente", "claramente um", "trata-se de um boletim",
                     "alta confiança", "confiança", "sugerido", "é t3",
                     "pertence a t3", "não é t3", "classificação")
        for x in self.d:
            texto = json.dumps(x["DISPLAY_TRANSLATION_PTBR"],
                               ensure_ascii=False).lower()
            for frase in proibidas:
                with self.subTest(item=x["ITEM_ID"], frase=frase):
                    self.assertNotIn(frase, texto)

    def test_nenhum_campo_de_rotulo_viaja_na_pagina(self):
        bruto = json.dumps(self.d, ensure_ascii=False)
        for k in ("REVIEWER_A", "REVIEWER_B", "AGREEMENT", "FINAL_LABEL",
                  "T3_SIM", "T3_NAO", "T3_AMBIGUO"):
            with self.subTest(campo=k):
                self.assertNotIn('"%s"' % k, bruto)


class OHtmlNaoAdiantaAResposta(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(PAGINA, encoding="utf-8") as f:
            cls.html = f.read()

    def test_o_ficheiro_versionado_bate_com_o_gerador(self):
        self.assertEqual(self.html, ui.construir(),
                         "o HTML saiu de sincronia. Regenere: "
                         "py provas/ui_revisao_t3_ptbr.py --escrever")

    def test_nenhum_campo_proibido_aparece(self):
        for k in ui.PROIBIDOS_NO_HTML:
            with self.subTest(campo=k):
                self.assertNotIn(k, self.html)

    def test_nao_ha_sugestao_nem_confianca(self):
        baixo = self.html.lower()
        for palavra in ("provavelmente_t3", "likely_t3", "suggested_label",
                        "confidence", "probabilidade de t3"):
            with self.subTest(palavra=palavra):
                self.assertNotIn(palavra, baixo)

    def test_quatro_opcoes_e_so_quatro(self):
        self.assertEqual(len(ui.BOTOES), 4)
        self.assertEqual([b[0] for b in ui.BOTOES],
                         ["T3_SIM", "T3_NAO", "T3_AMBIGUO",
                          "EVIDENCIA_INSUFICIENTE"])
        achados = set(re.findall(r'data-l="([A-Z3_]+)"', self.html))
        self.assertEqual(achados, {b[0] for b in ui.BOTOES})

    def test_nenhuma_resposta_vem_preenchida(self):
        """⚠️ A primeira versao deste teste procurava `aria-pressed="true"` no
        ficheiro inteiro — e acendia no SELETOR CSS que pinta o botao escolhido.

            UM TESTE QUE NAO DISTINGUE O SELETOR DA MARCACAO
            REPROVA CODIGO CERTO E ENSINA A DESLIGA-LO.

        O que importa provar e outra coisa: nao ha botao NENHUM ja escrito no
        HTML. Todos nascem em JavaScript, e o estado de cada um vem de
        `localStorage`, que comeca vazio.
        """
        # O corpo ESTATICO e o que esta entre <body> e o primeiro <script>.
        # Tudo o resto ou e estilo, ou sao os dados, ou e o JavaScript que
        # constroi a ficha a partir do que a pessoa gravou.
        estatico = self.html.split("<body>", 1)[1].split("<script", 1)[0]
        self.assertNotIn("button", estatico,
                         "ha um botao escrito no corpo estatico do HTML; "
                         "devia ser construido a partir do `localStorage`")
        self.assertIn('id="palco"', estatico)
        self.assertIn("r.LABEL===b[0]", self.html.replace(" ", ""))
        self.assertIn("respostas=ler()", self.html.replace(" ", ""))

    def test_guarda_progresso_no_navegador(self):
        self.assertIn("localStorage", self.html)
        self.assertIn("sintonia.t3.revisao.v1", self.html)
        self.assertIn("DOC_SHA256", self.html)

    def test_exporta_json(self):
        self.assertIn("sintonia.t3-human-review-results/1", self.html)
        self.assertIn("T3-HUMAN-REVIEW-RESULTS-V1.json", self.html)
        self.assertIn("ORIGINAL_EVIDENCE", self.html)

    def _funcao(self, nome):
        """O corpo de uma funcao do script, para nao testar por string solta."""
        i = self.html.index("function %s(" % nome)
        j = self.html.index("\n}", i)
        return self.html[i:j].replace(" ", "")

    def test_completo_exige_53_de_53(self):
        """⚠️ A primeira versao procurava `feitas()===DOCS.length` no ficheiro
        inteiro. Essa expressao aparece DUAS vezes — e a mutacao que trocava a
        do `baixar()` por `feitas()>0` passava, porque a outra continuava la.

            UM TESTE QUE PROCURA UMA STRING QUE APARECE DUAS VEZES
            SO PROVA QUE A OUTRA NAO MUDOU.

        Agora le o corpo do `baixar()`, que e quem decide o STATUS.
        """
        baixar = self._funcao("baixar")
        self.assertIn("constcompleto=feitas()===DOCS.length", baixar)
        self.assertIn('completo?"COMPLETE":"INCOMPLETE"', baixar)
        self.assertIn("completo?newDate().toISOString():null", baixar)
        self.assertIn("TOTAL_EXPECTED:DOCS.length", baixar)

    def test_nao_fabrica_razao_humana(self):
        self.assertIn("HUMAN_REASON:null", self.html.replace(" ", ""))

    def test_avisa_sobre_o_nome_do_ficheiro_uma_vez(self):
        self.assertEqual(self.html.count("não determinam a resposta"), 1)

    def test_avisa_que_o_json_ainda_nao_e_gabarito(self):
        self.assertIn("precisa passar pela validação do SINTONIA", self.html)

    def test_nao_escreve_em_ficheiro_do_projeto(self):
        for proibido in ("T3-HUMAN-REVIEW-PENDING-V1.json",
                         "LIVRO-DE-DECISOES", "PERGUNTAS_DO_UNIVERSO"):
            with self.subTest(alvo=proibido):
                if proibido == "T3-HUMAN-REVIEW-PENDING-V1.json":
                    # so pode aparecer como PROCEDENCIA no JSON exportado
                    self.assertIn("SOURCE_PACKET", self.html)
                else:
                    self.assertNotIn(proibido, self.html)

    def test_abre_sem_servidor_e_sem_rede(self):
        self.assertNotIn("<script src=", self.html)
        self.assertNotIn("http://localhost", self.html)
        for fora in ("cdn.", "googleapis", "unpkg", "jsdelivr", "fetch("):
            with self.subTest(rede=fora):
                self.assertNotIn(fora, self.html)

    def test_serve_em_ecra_pequeno(self):
        self.assertIn('name="viewport"', self.html)
        self.assertIn("min-height:60px", self.html.replace(" ", ""))

    def test_nada_empurra_a_pagina_para_o_lado(self):
        """O titulo de um CSV e a linha de cabecalho: 200 caracteres sem um
        unico espaco. Sem isto o `h2` arrasta a PAGINA INTEIRA para a direita,
        e foi assim que a primeira versao chegou ao revisor.

            UM TITULO QUE NAO QUEBRA NAO E UM PROBLEMA DE ESTILO.
            E UMA PAGINA QUE NAO SE LE.
        """
        css = _sem_espaco(self.html.split("</style>", 1)[0])
        self.assertIn("h2{font-size:20px;line-height:1.3;margin:0014px;"
                      "overflow-wrap:anywhere}", css)
        self.assertIn("overflow-wrap:anywhere;font-size:15px}", css)
        self.assertIn("html,body{overflow-x:clip}", css)
        self.assertIn("ul.sinaisli{overflow-wrap:anywhere}", css)

    def test_documento_com_linhas_rola_por_dentro(self):
        css = _sem_espaco(self.html.split("</style>", 1)[0])
        self.assertIn(".trecho.tabela{white-space:pre;overflow-x:auto", css)
        # e a decisao e pela FORMA do texto, nao pelo assunto
        self.assertIn(r"functiontabela(t){return(t||'').indexOf('\n')>=0;}",
                      _sem_espaco(self.html))

    def test_primeira_linha_sem_forma_de_titulo_nao_e_gritada(self):
        self.assertIn("h2.cru{font-size:14px",
                      _sem_espaco(self.html.split("</style>", 1)[0]))
        self.assertIn(r"functioncru(t){return(t||'').split(/\s+/)"
                      r".some(w=>w.length>40);}", _sem_espaco(self.html))

    def test_os_dois_csv_sao_os_que_disparam_as_duas_regras(self):
        """Medido, nao suposto: quais fichas caem em cada regra de forma."""
        d = ui.dados()
        crus = [x for x in d
                if any(len(w) > 40 for w in
                       x["DISPLAY_TRANSLATION_PTBR"]["TITLE"].split())]
        tabelas = [x for x in d
                   if "\n" in x["DISPLAY_TRANSLATION_PTBR"]["OPENING"]]
        self.assertEqual(sorted(x["DOCUMENT_TYPE"] for x in crus), ["CSV", "CSV"])
        self.assertEqual(sorted(x["DOCUMENT_TYPE"] for x in tabelas),
                         ["CSV", "CSV"])


class NadaFoiRotuladoNemAlterado(unittest.TestCase):

    def test_o_pacote_continua_vazio(self):
        p = ui._json(ui.PENDENTE)
        self.assertEqual(p["AUTO_LABELS_ASSIGNED"], 0)
        for i in p["ITENS"]:
            self.assertEqual(i["FINAL_LABEL"], "NOT_RUN")

    def test_a_traducao_declara_que_nao_e_evidencia(self):
        t = ui._json(ui.TRADUCAO)
        self.assertEqual(t["AUTO_LABELS_ASSIGNED"], 0)
        self.assertEqual(len(t["TRADUCOES"]), 53)
        self.assertIn("DISPLAY_TRANSLATION != EVIDENCE", t["REGRA"])

    def test_a_porta_nao_mudou(self):
        import admissao as adm
        self.assertEqual(sorted(adm.PERGUNTAS_DO_UNIVERSO),
                         ["T3", "T4", "T7", "T9"])


if __name__ == "__main__":
    unittest.main()
