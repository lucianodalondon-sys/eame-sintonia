#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA IDENTIDADE DE DONO DE FONTE — SOURCE_OWNER

    O FACTO É A ENTIDADE. A CHAVE É DO CATÁLOGO.
    NÃO SE PROMOVE A CHAVE PARA FECHAR UM GATE.

Decidido em 2026-09-16 (know-how §127-5b.2): o SINTONIA ainda NÃO tem uma
identidade canónica estável para o dono de uma fonte. O Atlas — registo
canónico — escreve o dono pela ENTIDADE, pelo nome. `IT-OWN-*` é a chave do
catálogo candidato `candidatas/ITALY-SOURCE-MASTER-V1.json`: serve para cruzar
com ele, e não é identidade.

Estas provas existem para que ninguém volte a:

  · chamar «canónico» ou «legado» a uma chave IT-OWN-*;
  · inventar um alias de dono (OWNER_ID_LEGACY existiu 2 commits e foi retirado);
  · fazer uma peça de runtime depender de um id de dono que não existe;
  · apagar a história das chaves que já foram usadas.

Corre como os outros testes desta casa:  py tests/test_source_owner_identity.py
"""
import glob
import io
import json
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ATLAS = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
MASTER = os.path.join(RAIZ, "candidatas", "ITALY-SOURCE-MASTER-V1.json")
CONTRATOS = os.path.join(RAIZ, "regras", "italy_contracts.mjs")
MANIFESTOS = sorted(glob.glob(os.path.join(RAIZ, "data", "samples",
                                           "IT-SOURCE-SAMPLES", "*", "MANIFEST.json")))

#: As palavras que fingem uma identidade canónica de dono que não existe.
PALAVRAS_PROIBIDAS = ("OWNER_ID_LEGACY", "CANONICAL_OWNER_ID", "LEGACY_OWNER_ID",
                      "OWNER_IDS_LEGACY")

#: As gavetas onde o dado corre. Nenhuma pode exigir um id de dono.
GAVETAS_DE_RUNTIME = ("coleta/", "admissao/", "pedido/", "leis/", "guarda/",
                      "supabase/", "orquestrador/", "ferramentas/")


def _texto(caminho):
    with io.open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _json(caminho):
    return json.loads(_texto(caminho))


def _ficha(texto, source_id):
    i = texto.index("SOURCE_ID:                    " + source_id)
    return texto[i:i + 6000]


class ODonoEAEntidadeAChaveEDoCatalogo(unittest.TestCase):

    def test_o_atlas_identifica_o_dono_pelo_nome_e_nao_por_id(self):
        """168 de 176 fichas escrevem só o nome. Oito fichas recentes com
        «(IT-OWN-…)» não fazem lei para as outras — e o glossário diz o que o
        parêntese é."""
        texto = _texto(ATLAS)
        donos = re.findall(r"^SOURCE_OWNER:\s+(.+)$", texto, re.M)
        self.assertGreater(len(donos), 100, "o atlas nao devolveu fichas")
        com_chave = [d for d in donos if re.search(r"\(\w+-OWN-", d)]
        self.assertLess(len(com_chave), len(donos) / 4,
                        "a chave do catalogo candidato espalhou-se pelo atlas: "
                        "%d de %d fichas" % (len(com_chave), len(donos)))
        glossario = texto[texto.index("## FICHA OBRIGATÓRIA DA FONTE"):][:3000]
        self.assertIn("chave do catálogo candidato", glossario)
        self.assertIn("NÃO é identidade canónica", glossario)

    @staticmethod
    def _campo_proibido(texto):
        """O nome de um campo proibido USADO COMO CAMPO, ou None.

        A menção histórica («um campo OWNER_ID_LEGACY existiu … e foi retirado»)
        é permitida; um campo com esse nome — `"OWNER_ID_LEGACY":` num JSON ou
        `OWNER_ID_LEGACY:` num .mjs / numa ficha — não."""
        for palavra in PALAVRAS_PROIBIDAS:
            if re.search(r'["\']?%s["\']?\s*:' % palavra, texto):
                return palavra
        return None

    def test_o_detector_de_campo_proibido_dispara_quando_deve(self):
        """CONTROLO POSITIVO. Uma asserção negativa que nunca foi vista a
        disparar pode estar a passar por vazio. Aqui ela dispara sobre as
        três grafias reais — JSON, .mjs e ficha — e cala-se sobre a menção
        histórica."""
        self.assertEqual("OWNER_ID_LEGACY", self._campo_proibido('{"OWNER_ID_LEGACY": "x"}'))
        self.assertEqual("OWNER_ID_LEGACY", self._campo_proibido('OWNER_ID_LEGACY: "IT-OWN-X",'))
        self.assertEqual("OWNER_ID_LEGACY",
                         self._campo_proibido("SOURCE_OWNER: A\n   OWNER_ID_LEGACY: IT-OWN-X\n"))
        self.assertEqual("CANONICAL_OWNER_ID", self._campo_proibido('"CANONICAL_OWNER_ID": "y"'))
        self.assertIsNone(self._campo_proibido(
            "um campo OWNER_ID_LEGACY existiu entre e060bc55 e d376c268 e foi retirado"))
        self.assertIsNone(self._campo_proibido('"OWNER_ID": "IT-OWN-040"'))

    def test_nenhuma_peca_ativa_chama_a_chave_de_canonica_ou_legada(self):
        """As palavras que fingem identidade não podem aparecer como CAMPO em
        nenhuma peça viva: Atlas, MASTER, manifestos, contratos."""
        for caminho in [ATLAS, MASTER, CONTRATOS] + MANIFESTOS:
            achado = self._campo_proibido(_texto(caminho))
            self.assertIsNone(achado, "%s usa %s como campo"
                              % (os.path.relpath(caminho, RAIZ), achado))

    def test_nenhuma_gaveta_de_runtime_depende_de_um_id_de_dono(self):
        """Se um dia o runtime precisar de SOURCE_OWNER_STABLE_ID, abre-se um
        contrato. Até lá, IT-OWN-* não entra na máquina."""
        ficheiros = subprocess.run(["git", "-C", RAIZ, "ls-files"],
                                   capture_output=True, text=True).stdout.split("\n")
        intrusos = []
        for f in ficheiros:
            if not f.startswith(GAVETAS_DE_RUNTIME):
                continue
            if not f.endswith((".py", ".mjs", ".js", ".sql")):
                continue
            if f == "regras/italy_contracts.mjs":
                continue  # contrato de ACESSO: carrega a chave, não depende dela
            try:
                if "IT-OWN-" in _texto(os.path.join(RAIZ, f)):
                    intrusos.append(f)
            except (OSError, UnicodeDecodeError):
                continue
        self.assertEqual([], intrusos, "runtime a depender de id de dono: %s" % intrusos)

    def test_toda_chave_de_dono_usada_no_master_tem_registo_no_master(self):
        """A chave é do catálogo: dentro dele, resolve sempre. (Fora dele —
        manifestos e contratos — 11 chaves nomeadas ainda não resolvem: dívida
        declarada em §127-5b.2, medida aqui sem ser escondida.)"""
        d = _json(MASTER)
        registadas = {o["OWNER_ID"] for o in d["owners"]}
        self.assertEqual(len(registadas), len(d["owners"]), "OWNER_ID duplicado no MASTER")
        usadas = {s["OWNER_ID"] for s in d["sources"]}
        self.assertEqual(set(), usadas - registadas,
                         "fonte do MASTER aponta para chave sem registo")
        # a dívida, medida e não escondida
        por_fonte = {s["SOURCE_ID"]: s["OWNER_ID"] for s in d["sources"]}
        divergentes = []
        for m in MANIFESTOS:
            j = _json(m)
            chave = j.get("OWNER_ID")
            if chave and por_fonte.get(j.get("SOURCE_ID")) and chave != por_fonte[j["SOURCE_ID"]]:
                divergentes.append(j["SOURCE_ID"])
        self.assertEqual(11, len(divergentes),
                         "a divida dos manifestos mudou de tamanho sem missao propria: %s"
                         % sorted(divergentes))
        self.assertIn("IT-T2-002", divergentes, "a ARPAV foi alinhada — AU9 perde o controlo negativo")


class AAdamaEUmCasoEscritoNaoUmaExcecao(unittest.TestCase):
    """IT-T9-008: a entidade é o facto; as duas chaves são história."""

    ENTIDADE = "ADAMA Italia S.r.l."
    CHAVE = "IT-OWN-040"
    CHAVE_ANTERIOR = "IT-OWN-ADAMA-IT"

    def test_a_entidade_e_a_mesma_em_todo_o_lado(self):
        ficha = _ficha(_texto(ATLAS), "IT-T9-008")
        self.assertRegex(ficha, r"SOURCE_OWNER:\s+ADAMA Italia S\.r\.l\.")
        d = _json(MASTER)
        dono = next(o for o in d["owners"] if o["OWNER_ID"] == self.CHAVE)
        self.assertEqual(self.ENTIDADE, dono["OWNER_CANONICAL_NAME"])
        man = _json(os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES",
                                 "IT-T9-008", "MANIFEST.json"))
        self.assertEqual(self.ENTIDADE, man["OWNER_CANONICAL_NAME"])
        self.assertEqual("ADAMA Italia", man["OWNER_NAME_AS_CAPTURED"],
                         "o nome capturado foi apagado — NOME CAPTURADO != IDENTIDADE, mas fica")
        bloco = _texto(CONTRATOS)
        bloco = bloco[bloco.index('"IT-T9-008": {'):][:1500]
        self.assertIn('OWNER: "%s"' % self.ENTIDADE, bloco)

    def test_a_chave_esta_alinhada_e_a_anterior_continua_escrita(self):
        d = _json(MASTER)
        fonte = next(s for s in d["sources"] if s["SOURCE_ID"] == "IT-T9-008")
        dono = next(o for o in d["owners"] if o["OWNER_ID"] == self.CHAVE)
        self.assertEqual(self.CHAVE, fonte["OWNER_ID"])
        self.assertIn(self.CHAVE_ANTERIOR, json.dumps(dono),
                      "a chave anterior sumiu da historia do registo")
        self.assertFalse(any(o["OWNER_ID"] == self.CHAVE_ANTERIOR for o in d["owners"]),
                         "a chave anterior virou registo proprio — dois donos para uma entidade")
        man = _json(os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES",
                                 "IT-T9-008", "MANIFEST.json"))
        self.assertEqual(self.CHAVE, man["OWNER_ID"])
        self.assertIn(self.CHAVE_ANTERIOR, json.dumps(man))
        self.assertEqual("9f56e17877efe44f086c65efb9e4910f138b8273a0eaedc70842ac697f1218c6",
                         man["FILES"][0]["SHA256"], "a amostra mudou de bytes")
        bloco = _texto(CONTRATOS)
        bloco = bloco[bloco.index('"IT-T9-008": {'):][:1500]
        self.assertIn('OWNER_ID: "%s"' % self.CHAVE, bloco)
        self.assertIn(self.CHAVE_ANTERIOR, bloco)
        self.assertNotIn('OWNER_ID: "%s"' % self.CHAVE_ANTERIOR, bloco)

    def test_a_fonte_nao_foi_tocada(self):
        """Dono de fonte não tem identidade canónica; FONTE tem. IT-T9-008 e
        os seus legados continuam exactamente como a decisão §127 os deixou."""
        mapa = _json(os.path.join(RAIZ, "referencia", "adama", "SOURCE-ID-MAP.json"))["RECORDS"]
        legados = {m["LEGACY_SOURCE_ID"]: m["CANONICAL_SOURCE_ID"] for m in mapa}
        self.assertEqual("IT-T9-008", legados.get("IT-ADAMA-CATALOG"))
        self.assertEqual("IT-T9-008", legados.get("SRC_ADAMA_COM"))
        self.assertIn("SOURCE_ID:                    IT-T9-008", _texto(ATLAS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
