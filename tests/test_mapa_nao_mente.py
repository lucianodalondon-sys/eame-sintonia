#!/usr/bin/env python3
"""SM1..SM7 — o mapa nao pode ficar vermelho por cegueira.

    EXISTE NO DISCO  !=  RASTREADO PELO GIT  !=  NAO EXISTE.

O QUE ACONTECEU
---------------
`scan_repo.py` lista com `git ls-files` — so o que ja foi `git add`ado. Um
ficheiro acabado de escrever existe no disco e nao esta la. O gerador via a
lista vazia e publicava «declarado no mapa e nao existe no repositorio».

E nao era um caso isolado: MEDIDO, `C-CENSO-DONOS` nasceu com a mesma frase no
commit que o criou (`a9979c2c`), e `C-CENSO-OBSERVABILIDADE` no dele
(`0552424a`). **Toda peca nova nascia falsamente partida e curava-se sozinha no
commit seguinte** — uma mentira que desaparece antes de alguem a investigar.

E o `SYSTEM_MAP_CHECK` dava `PASS` na mesma, por duas cegueiras empilhadas:
a `P4` compara o gerado com o gerado (o inventario tambem sai do `git
ls-files`), e itera a lista RESOLVIDA — que numa peca acusada de inexistente
esta vazia. Zero ficheiros iterados, prova passa.

    GENERATED == EXPECTED GENERATOR OUTPUT
    NAO E
    GENERATED == REAL FILE EXISTENCE.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "system-map", "scripts"))
import validate_system_map as v  # noqa: E402

ESTADO = os.path.join(RAIZ, "system-map", "data", "state.generated.json")
DECLARADO = os.path.join(RAIZ, "system-map", "data",
                         "architecture.declared.json")
NUNCA = "provas/zz_ficheiro_que_nunca_existiu.py"


def _json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class SM1_CaminhoRealNuncaViraBroken(unittest.TestCase):
    """Um caminho que EXISTE no disco nao pode ser dado por inexistente, mesmo
    que esteja fora do censo geral."""

    def test_a_guarda_apanha_quem_diz_broken_com_o_ficheiro_no_disco(self):
        achadas = v.mentiras_sobre_existencia(
            {"COMPONENTS": [{"id": "X", "files": ["provas/o_mapa_nao_mente.py"]}]},
            {"X": {"status": "BROKEN"}}, RAIZ)
        self.assertTrue(achadas, "guarda cega: o ficheiro esta no disco")

    def test_a_guarda_aceita_glob_e_nao_so_caminho_literal(self):
        achadas = v.mentiras_sobre_existencia(
            {"COMPONENTS": [{"id": "X", "files": ["provas/*.py"]}]},
            {"X": {"status": "BROKEN"}}, RAIZ)
        self.assertTrue(achadas)


class SM2_CaminhoInexistenteContinuaBroken(unittest.TestCase):
    """⚠️ A correcao nao pode afrouxar a prova que ja funcionava."""

    def test_a_guarda_poupa_o_broken_legitimo(self):
        achadas = v.mentiras_sobre_existencia(
            {"COMPONENTS": [{"id": "X", "files": [NUNCA]}]},
            {"X": {"status": "BROKEN"}}, RAIZ)
        self.assertEqual(achadas, [], "guarda dispara a esmo")

    def test_a_guarda_nao_acusa_quem_nao_esta_broken(self):
        for estado in ("PROVEN", "PENDING", "UNKNOWN"):
            self.assertEqual(
                v.mentiras_sobre_existencia(
                    {"COMPONENTS": [{"id": "X",
                                     "files": ["provas/o_mapa_nao_mente.py"]}]},
                    {"X": {"status": estado}}, RAIZ),
                [], estado)


class SM3_SM4_AsDuasPecasDoAchado(unittest.TestCase):
    """As duas pecas que o achado externo nomeou. Uma estava mesmo errada; a
    outra ja era vista — e a diferenca importa."""

    def test_SM3_censo_da_observabilidade_existe(self):
        self.assertTrue(os.path.exists(os.path.join(
            RAIZ, "system-map", "scripts", "censo_da_observabilidade.py")))

    def test_SM4_fluxo_no_seco_existe(self):
        self.assertTrue(os.path.exists(os.path.join(
            RAIZ, "provas", "fluxo_no_seco.py")))

    def test_nenhuma_das_duas_esta_broken_hoje(self):
        nos = {n["id"]: n for n in _json(ESTADO)["NODES"]}
        for pid in ("C-CENSO-OBSERVABILIDADE", "C-FLUXO-NO-SECO"):
            if pid in nos:
                self.assertNotEqual(nos[pid]["status"], "BROKEN", pid)


class SM5_SM6_ExcluirDoCensoNaoEInexistir(unittest.TestCase):
    """⚠️ A DISTINCAO OBRIGATORIA.

    `system-map/` e excluido do censo para o mapa nao se medir a si proprio
    como produto. Isso NAO autoriza dizer «o ficheiro nao existe»."""

    def test_SM5_nenhuma_peca_de_system_map_esta_broken(self):
        nos = _json(ESTADO)["NODES"]
        maus = [n["id"] for n in nos
                if n["status"] == "BROKEN"
                and any(f.startswith("system-map/") for f in n.get("files", []))]
        self.assertEqual(maus, [])

    def test_SM6_o_estado_gerado_nao_afirma_inexistencia_de_nada_real(self):
        """A prova de fogo, sobre o estado REAL de hoje."""
        self.assertEqual(
            v.mentiras_sobre_existencia(
                _json(DECLARADO),
                {n["id"]: n for n in _json(ESTADO)["NODES"]},
                RAIZ),
            [])


class SM7_AGuardaExisteEEChamada(unittest.TestCase):
    """A guarda tem de estar LIGADA ao portao, nao so escrita."""

    def test_a_prova_esta_no_validador(self):
        with open(os.path.join(RAIZ, "system-map", "scripts",
                               "validate_system_map.py"), encoding="utf-8") as f:
            fonte = f.read()
        corpo = "\n".join(l for l in fonte.splitlines()
                          if not l.strip().startswith("#"))
        self.assertIn("P4_NAO_MENTIR_SOBRE_EXISTENCIA", corpo)
        self.assertIn("mentiras_sobre_existencia(", corpo)

    def test_a_guarda_e_uma_funcao_pura_e_por_isso_testavel(self):
        """⚠️ ELA ESTA SEPARADA DA `main()` DE PROPOSITO.

        O validador REGENERA o estado antes de o validar (P1, anti-drift). A
        primeira tentativa de a testar injectava a mentira no ficheiro e corria
        o validador — e deu PASS, porque a regeneracao apagava a injecção antes
        de a guarda a ver.

        Uma guarda que so pode ser exercitada pelo caminho que a apaga e uma
        guarda que ninguem consegue provar que morde."""
        self.assertTrue(callable(v.mentiras_sobre_existencia))
        self.assertEqual(
            v.mentiras_sobre_existencia({"COMPONENTS": []}, {}, RAIZ), [])


class OVocabularioNaoCresceuSemPrecisar(unittest.TestCase):
    """REUSE FIRST: a correcao nao inventou um quinto estado.

    Medido: um estado novo custaria mexer em `VALIDOS`, no gerador, na tela, na
    copia servida e na documentacao. `UNKNOWN` ja diz o certo — o scanner
    genuinamente nao consegue provar nada sobre a peca — e a razao escrita
    explica que e do Git, nao do disco."""

    def test_continuam_a_ser_quatro(self):
        self.assertEqual(v.VALIDOS, {"PROVEN", "PENDING", "BROKEN", "UNKNOWN"})

    def test_todo_status_do_estado_e_valido(self):
        for n in _json(ESTADO)["NODES"]:
            self.assertIn(n["status"], v.VALIDOS, n["id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
