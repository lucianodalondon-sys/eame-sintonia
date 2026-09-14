# -*- coding: utf-8 -*-
"""A TRAVA DO NÚMERO COPIADO À MÃO.

`docs/operacao/CENSO-CARDS-SENSORES-V1.md` é a LEITURA humana de
`data/derivados/MATRIZ-CARDS-SENSORES-V1.json`. A leitura precisa de citar
números de que não é dona — um documento sem números não se lê, e um documento
que os reescreve cria um segundo dono de cada contagem.

    UM NUMERO COPIADO A MAO E UM NUMERO QUE VAI ENVELHECER EM SILENCIO.

A saída não é proibir a citação: é tornar a divergência barulhenta. Tudo o que
o documento cita vive em blocos assim, e este teste compara-os, um a um, com o
JSON:

    ```
    MEDIDO
    CARDS_TOTAL = 11
    ```

No dia em que o censo medir outra coisa, o documento reprova aqui em vez de
mentir em silêncio.
"""
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DOC = RAIZ / "docs" / "operacao" / "CENSO-CARDS-SENSORES-V1.md"
JSON = RAIZ / "data" / "derivados" / "MATRIZ-CARDS-SENSORES-V1.json"

RE_BLOCO = re.compile(r"```\s*\nMEDIDO\n(.*?)```", re.S)
RE_LINHA = re.compile(r"^([A-Z0-9_.]+)\s*=\s*(.+?)\s*$")


def citados():
    """(chave, valor, linha-no-documento) de cada número citado."""
    texto = DOC.read_text(encoding="utf-8")
    fora = []
    for bloco in RE_BLOCO.finditer(texto):
        antes = texto[:bloco.start(1)].count("\n") + 1
        for i, linha in enumerate(bloco.group(1).splitlines()):
            m = RE_LINHA.match(linha.strip())
            if m:
                fora.append((m.group(1), m.group(2), antes + i))
    return fora


def medido(d, chave):
    """Onde este número vive de verdade. Levanta KeyError se não vive em lado nenhum.

    ⚠️ A ORDEM DE BUSCA IMPORTA e não é cosmética: se uma chave existisse em
    dois sítios, este resolvedor escolheria um por sorteio e o teste passaria a
    verificar o número errado sem se queixar. Por isso ele procura em todos e
    RECUSA quando encontra mais de um.
    """
    achados = []
    partes = chave.split(".")
    for raiz in ("CONTAGENS", "A_FRONTEIRA", None):
        no = d[raiz] if raiz else d
        try:
            for p in partes:
                no = no[p]
        except (KeyError, TypeError):
            continue
        achados.append((raiz or "(topo)", no))
    for pr in d["AS_CINCO_PROVAS"]:
        if chave == "AS_CINCO_PROVAS." + pr["PROVA"]:
            achados.append(("AS_CINCO_PROVAS", pr["SENSORES"]))
    if not achados:
        raise KeyError(chave)
    if len({repr(v) for _, v in achados}) > 1:
        raise AssertionError(
            "%s vive em mais do que um sitio com valores diferentes: %s"
            % (chave, achados))
    return achados[0][1]


def como_texto(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, dict)):
        return str(len(v))
    return str(v)


class OsNumerosDoDocumentoSaoOsDoCenso(unittest.TestCase):

    def setUp(self):
        self.assertTrue(JSON.exists(), "corra system-map/scripts/censo_cards_sensores.py")
        self.d = json.loads(JSON.read_text(encoding="utf-8"))
        self.citados = citados()

    def test_o_documento_cita_alguma_coisa(self):
        """Sem esta, apagar todos os blocos `MEDIDO` faria o teste passar vazio."""
        self.assertGreaterEqual(
            len(self.citados), 20,
            "o documento deixou de citar o censo — ou os blocos MEDIDO mudaram "
            "de forma e esta trava ficou a verificar nada")

    def test_cada_numero_citado_existe_no_censo(self):
        for chave, _, linha in self.citados:
            with self.subTest(chave=chave):
                try:
                    medido(self.d, chave)
                except KeyError:
                    self.fail(
                        "%s:%d cita `%s`, que nao existe na matriz. Um numero "
                        "sem dono no JSON e um numero escrito a mao."
                        % (DOC.name, linha, chave))

    def test_cada_numero_citado_bate_com_o_censo(self):
        for chave, valor, linha in self.citados:
            with self.subTest(chave=chave):
                real = como_texto(medido(self.d, chave))
                self.assertEqual(
                    real, valor,
                    "%s:%d diz `%s = %s`; a matriz mede `%s`. O documento "
                    "envelheceu — corra o censo e actualize a leitura."
                    % (DOC.name, linha, chave, valor, real))

    def test_a_matriz_foi_gerada_do_head_desta_arvore(self):
        """Uma leitura de uma matriz velha e uma leitura de outro sistema."""
        self.assertEqual(len(self.d["PROVENANCE"]["HEAD"]), 40)
        self.assertEqual(self.d["SCHEMA"], "sintonia.censo-cards-sensores/1")


class AEscadaNaoEmprestaProva(unittest.TestCase):
    """As cinco provas descem. Se uma subisse, um degrau estaria a herdar o
    `YES` do anterior — que e exatamente o erro que este censo existe para
    nao cometer."""

    def test_as_cinco_provas_nunca_sobem(self):
        d = json.loads(JSON.read_text(encoding="utf-8"))
        escada = [(p["PROVA"], p["SENSORES"]) for p in d["AS_CINCO_PROVAS"]]
        self.assertEqual([p for p, _ in escada],
                         ["EXISTE", "CORRE", "RODOU", "PRODUZIU", "ENTROU"])
        for (a, va), (b, vb) in zip(escada, escada[1:]):
            self.assertLessEqual(
                vb, va, "%s (%d) e maior do que %s (%d): um degrau esta a "
                        "contar mais do que o anterior deixou passar"
                        % (b, vb, a, va))


class OEstadoDoCardNaoInventaProva(unittest.TestCase):
    """A escada de `ESTADO` ja terminou em `else ALIMENTADO_POR_REAL`, e isso
    dava «real» a qualquer tela cujas camadas nao fossem fixture — incluindo as
    que citam camada que ninguem classificou. Esta trava impede o regresso."""

    def test_nenhum_card_e_real_com_camada_por_classificar(self):
        d = json.loads(JSON.read_text(encoding="utf-8"))
        for c in d["CARDS"]:
            if "NAO SEI" in (c["TIPOS_DE_CAMADA"] or []):
                self.assertNotEqual(
                    c["ESTADO"], "ALIMENTADO_POR_REAL",
                    "%s tem camada de tipo `NAO SEI` e mesmo assim sai como "
                    "alimentado por real" % c["CARD_ID"])

    def test_nenhum_card_e_real_confessando_fixture(self):
        d = json.loads(JSON.read_text(encoding="utf-8"))
        for c in d["CARDS"]:
            if c["CONFISSOES"]:
                self.assertNotEqual(
                    c["ESTADO"], "ALIMENTADO_POR_REAL",
                    "%s tem %d confissao(oes) do proprio contrato e sai como "
                    "alimentado por real" % (c["CARD_ID"], c["CONFISSOES"]))


if __name__ == "__main__":
    unittest.main()
