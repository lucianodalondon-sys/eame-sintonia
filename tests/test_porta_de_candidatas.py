#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA PORTA DE ENTRADA DE FONTE NOVA

    UMA PORTA QUE ESCREVE NA FILA ERRADA E PIOR DO QUE NAO TER PORTA.

A porta (`candidatas/fonte_nova.py`) aceitava a candidata, dizia `NA_FILA=...` e
gravava num ficheiro que nenhuma autoridade lia. Quem registasse uma fonte via-a
desaparecer em silencio — o pior modo de falhar, porque parece sucesso.

Estes testes NAO se contentam em ler a constante. Uma constante certa com um
comportamento errado continua a perder candidatas. Por isso a maior parte destas
provas copia a porta para um diretorio temporario, corre-a a serio e vai ver
ONDE os bytes caíram.

Nada aqui toca na fila real do repositorio.

Corre como os outros testes desta casa:  py tests/test_porta_de_candidatas.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PORTA = RAIZ / "candidatas" / "fonte_nova.py"
FILA_CANONICA = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"

# O caminho que a porta usou por engano depois de o script mudar de gaveta.
# Continua aqui de proposito: e' o defeito que estes testes existem para impedir.
FILA_FANTASMA = ("data", "samples", "FONTES-CANDIDATAS.json")


def carregar_porta():
    """Importa a porta real, sem a correr."""
    spec = importlib.util.spec_from_file_location("fonte_nova_sob_teste", PORTA)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Sandbox:
    """Uma copia descartavel da gaveta `candidatas/`.

    A porta ancora-se em `__file__`, por isso basta copiar o script e a fila para
    um diretorio temporario: tudo o que ela escrever cai la' dentro.
    """

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()
        self.raiz = Path(self._td.name) / "repo"
        (self.raiz / "candidatas").mkdir(parents=True)
        self.porta = self.raiz / "candidatas" / "fonte_nova.py"
        self.fila = self.raiz / "candidatas" / "FONTES-CANDIDATAS.json"
        shutil.copy2(PORTA, self.porta)
        shutil.copy2(FILA_CANONICA, self.fila)
        return self

    def __exit__(self, *a):
        self._td.cleanup()

    def registar(self, cwd=None, **campos):
        """Corre a porta de verdade, por subprocesso, como uma pessoa a correria."""
        args = [sys.executable, str(self.porta)]
        for chave, valor in campos.items():
            args += [f"--{chave.replace('_', '-')}", valor]
        return subprocess.run(args, capture_output=True, text=True,
                              cwd=str(cwd) if cwd else str(self.raiz))

    def total(self):
        if not self.fila.exists():
            return None
        return json.loads(self.fila.read_text(encoding="utf-8")).get("TOTAL")

    def candidatas(self):
        return json.loads(self.fila.read_text(encoding="utf-8"))["CANDIDATAS"]

    @property
    def fantasma(self):
        return self.raiz.joinpath(*FILA_FANTASMA)


VALIDA = dict(tipo="BASE_OFICIAL", pais="IT", nome="Fonte de teste",
              url="https://exemplo-de-teste.invalid/", para_que="provar a porta",
              quem_viu="teste automatizado")


class APortaEscreveNaFilaCanonica(unittest.TestCase):
    """O caminho — medido no comportamento, nao no texto da constante."""

    def test_a_fila_vive_na_mesma_gaveta_que_a_porta(self):
        fila = Path(carregar_porta().FILA)
        self.assertEqual(PORTA.parent, fila.parent,
                         "a porta e a fila tem de viver na mesma gaveta: uma porta que "
                         "escreve noutra pasta perde a candidata em silencio")
        self.assertEqual(FILA_CANONICA.resolve(), fila.resolve(),
                         f"a fila canonica e {FILA_CANONICA.relative_to(RAIZ)} — "
                         "AGENTS.md, a Biblia COL-LAW-053, scan_sources.py e o indice "
                         "apontam todos para la'")

    def test_registar_poe_a_candidata_na_fila_canonica(self):
        with Sandbox() as s:
            self.assertEqual(0, s.total())
            r = s.registar(**VALIDA)
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual(1, s.total(), "a candidata nao chegou a' fila canonica")

    def test_a_porta_nao_cria_uma_segunda_fila(self):
        """O defeito original: escrever em data/samples/, que ninguem le'."""
        with Sandbox() as s:
            s.registar(**VALIDA)
            self.assertFalse(s.fantasma.exists(),
                             f"apareceu uma segunda fila em {'/'.join(FILA_FANTASMA)} — "
                             "duas filas sao duas verdades, e a segunda envelhece calada")
            self.assertFalse((s.raiz / "data").exists(),
                             "a porta criou a arvore data/ que nao lhe pertence")

    def test_o_caminho_nao_depende_do_diretorio_de_trabalho(self):
        """Correr a porta de outro sitio nao pode mudar a fila."""
        with Sandbox() as s:
            with tempfile.TemporaryDirectory() as outro:
                r = s.registar(cwd=outro, **VALIDA)
                self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual(1, s.total(),
                             "correr a porta de outro diretorio escreveu noutro sitio")
            self.assertFalse(s.fantasma.exists())

    def test_existe_uma_unica_fila_operacional_no_repositorio(self):
        achadas = [p for p in RAIZ.rglob("FONTES-CANDIDATAS.json")
                   if ".git" not in p.parts]
        self.assertEqual([FILA_CANONICA], achadas,
                         f"mais do que uma fila no repositorio: "
                         f"{[str(p.relative_to(RAIZ)) for p in achadas]}")


class APortaNaoFabricaIdentidade(unittest.TestCase):
    """SOURCE_ID e' identidade canonica: nasce no atlas, nao na fila."""

    def test_a_candidata_nasce_sem_source_id(self):
        with Sandbox() as s:
            s.registar(**VALIDA)
            linha = s.candidatas()[0]
            self.assertIn("SOURCE_ID", linha)
            self.assertIsNone(linha["SOURCE_ID"],
                              "a porta fabricou um SOURCE_ID — identidade canonica nao "
                              "nasce de URL, slug, hash nem sequencial")
            self.assertEqual("CANDIDATA", linha["ESTADO"],
                             "o que entra pela porta e' candidata, nunca fonte")

    def test_o_identificador_da_fila_nao_e_um_source_id(self):
        with Sandbox() as s:
            s.registar(**VALIDA)
            linha = s.candidatas()[0]
            self.assertTrue(linha["CANDIDATA_ID"].startswith("CAND-"),
                            "o id da fila tem de ser obviamente da fila")
            self.assertNotRegex(linha["CANDIDATA_ID"], r"^[A-Z]{2}-T\d{1,2}-\d+$",
                                "o id da fila esta' a imitar um SOURCE_ID do atlas")


class ADeduplicacaoOperacional(unittest.TestCase):
    """A mesma fonte escrita de duas maneiras nao pode virar duas candidatas."""

    def test_a_mesma_url_nao_cria_segunda_candidata(self):
        with Sandbox() as s:
            s.registar(**VALIDA)
            s.registar(**VALIDA)
            self.assertEqual(1, s.total(),
                             "registar a mesma fonte duas vezes criou duas linhas")

    def test_variacoes_de_grafia_reutilizam_a_candidata_existente(self):
        """Exatamente as variacoes que `normalizar()` promete tratar — nem mais."""
        porta = carregar_porta()
        base = "https://www.exemplo-de-teste.invalid/"
        variantes = ["http://www.exemplo-de-teste.invalid/",
                     "https://exemplo-de-teste.invalid",
                     "HTTPS://WWW.Exemplo-De-Teste.invalid/"]
        for v in variantes:
            with self.subTest(variante=v):
                self.assertEqual(porta.normalizar(base), porta.normalizar(v))
        with Sandbox() as s:
            s.registar(**dict(VALIDA, url=base))
            for v in variantes:
                s.registar(**dict(VALIDA, url=v))
            self.assertEqual(1, s.total(),
                             "uma variacao de grafia abriu uma candidata nova")

    def test_url_diferente_continua_a_criar_candidata_nova(self):
        """O contrato de dedupe nao pode alargar-se em silencio."""
        with Sandbox() as s:
            s.registar(**VALIDA)
            s.registar(**dict(VALIDA, url="https://exemplo-de-teste.invalid/outra-coisa"))
            self.assertEqual(2, s.total(),
                             "dois enderecos diferentes foram colapsados num so'")

    def test_o_tracking_nao_e_removido_pela_normalizacao(self):
        """Medido, nao desejado: `normalizar()` nao promete limpar parametros."""
        porta = carregar_porta()
        self.assertNotEqual(porta.normalizar("https://exemplo.it/"),
                            porta.normalizar("https://exemplo.it/?utm_source=x"),
                            "a normalizacao passou a remover tracking — o contrato de "
                            "dedupe cresceu sem ninguem decidir isso")

    def test_caveat_a_normalizacao_dobra_tambem_o_caminho(self):
        """CAVEAT MEDIDO, deixado de proposito como esta'.

        `normalizar()` faz `.lower()` no endereco inteiro, logo dobra tambem o
        CAMINHO. Em servidores onde o caminho e' sensivel a maiusculas, `/a` e
        `/A` podem ser dois recursos diferentes e aqui viram uma so candidata.

        Este teste NAO exige que isso mude: exige que continue visivel. Se
        alguem corrigir a normalizacao, este teste cai e obriga a decidir — em
        vez de a dedupe mudar de significado em silencio.
        """
        porta = carregar_porta()
        self.assertEqual(porta.normalizar("https://exemplo.it/a"),
                         porta.normalizar("https://exemplo.it/A"),
                         "a normalizacao deixou de dobrar o caminho: o contrato de "
                         "dedupe mudou e precisa de ser decidido, nao herdado")


class APortaRecusaEntradaInvalida(unittest.TestCase):
    """Recusar tem de deixar a fila exatamente como estava."""

    def _recusa(self, **campos):
        with Sandbox() as s:
            antes = s.fila.read_bytes()
            r = s.registar(**campos)
            self.assertNotEqual(0, r.returncode, f"aceitou entrada invalida: {campos}")
            self.assertEqual(antes, s.fila.read_bytes(), "a fila mudou numa recusa")
            self.assertFalse(s.fantasma.exists())

    def test_tipo_inexistente(self):
        self._recusa(**dict(VALIDA, tipo="PESQUISADOR"))

    def test_pais_inexistente(self):
        self._recusa(**dict(VALIDA, pais="XX"))

    def test_campo_obrigatorio_vazio(self):
        for campo in ("nome", "url", "para_que", "quem_viu"):
            with self.subTest(campo=campo):
                self._recusa(**dict(VALIDA, **{campo: "   "}))


class NenhumaAutoridadeApontaParaAFilaFantasma(unittest.TestCase):
    """Se alguem reintroduzir o caminho antigo, isto reprova."""

    def test_o_codigo_nao_volta_a_apontar_para_data_samples(self):
        fonte = PORTA.read_text(encoding="utf-8")
        # A linha de codigo — nao o comentario que explica o defeito.
        codigo = "\n".join(l for l in fonte.splitlines()
                           if not l.lstrip().startswith("#"))
        self.assertNotIn('"data"', codigo,
                         "a porta voltou a derivar o caminho da raiz do repositorio")
        self.assertNotIn("data/samples", codigo)

    def test_as_autoridades_continuam_a_apontar_para_candidatas(self):
        autoridades = {
            "AGENTS.md": "candidatas/FONTES-CANDIDATAS.json",
            "system-map/scripts/scan_sources.py": 'FILA = "candidatas/FONTES-CANDIDATAS.json"',
            "docs/fontes/INDICE-DE-FONTES.md": "candidatas/FONTES-CANDIDATAS.json",
        }
        for ficheiro, esperado in autoridades.items():
            with self.subTest(autoridade=ficheiro):
                texto = (RAIZ / ficheiro).read_text(encoding="utf-8")
                self.assertIn(esperado, texto,
                              f"{ficheiro} deixou de apontar para a fila canonica — "
                              "se a lei mudou, esta correcao tem de ser remedida")


if __name__ == "__main__":
    unittest.main(verbosity=2)
