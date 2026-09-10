# -*- coding: utf-8 -*-
"""B2 — O COLETOR DIZ O QUE PRODUZIU, EM VEZ DE DEIXAR ADIVINHAR.

A PERGUNTA QUE ESTE FICHEIRO FECHA
----------------------------------
Uma observacao RAW preservada nao dizia, em lado nenhum, QUE CONCEITO ela
materializou. Quem viesse a seguir teria de deduzir — do PDF, do MIME, da
extensao, do nome da fonte — e deduzir isso e adivinhar com cara de medida.

    RESOLVED_STRUCTURED_TARGET = SOURCE_DOCUMENT

O carimbo tem UMA razao, e ela nao e o formato do ficheiro: o coletor acabou de
materializar uma IDENTIDADE DOCUMENTAL. `DOCUMENT_ID` e `DOCUMENT_VERSION_ID`
com valor real sao a prova; sem eles, o campo nao existe.

    ALVO AUSENTE != ALVO DESCONHECIDO != ALVO NENHUM

E ausente e mesmo AUSENTE. `null`, `UNKNOWN` e `NAO SEI` nao entram aqui: um
campo que so aceita um CONCEPT_ID nao e sitio para uma confissao.

O QUE ESTE FICHEIRO NAO PROVA, PORQUE NAO EXISTE AINDA
------------------------------------------------------
Nao ha validacao `RESOLVED ∈ ALLOWED`: a permissao por fonte esta decidida na
A5.2 e nao esta instalada. Nao ha `STRUCTURED_TARGET_NOT_RESOLVED` no T-32. Nao
ha ponte para o dono do estruturado. Nada disso e desta missao.

Reusa a bancada offline do B1 — mesma fonte, mesmos bytes injetados, mesma
raiz temporaria, zero rede.
"""
import io
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "tests"))
import _gavetas  # noqa: E402,F401

import italy_executor as adapter                            # noqa: E402
from test_italia_na_porta_canonica import CasoB1, FONTE     # noqa: E402

ALVO = "RESOLVED_STRUCTURED_TARGET"
SOURCE_DOCUMENT = "SOURCE_DOCUMENT"
COLETOR = os.path.join(RAIZ, "coleta", "italy_pilot_collect.mjs")

# Os campos que a observacao valida ja trazia ANTES do B2, medidos na arvore em
# `cf326fa4`. Existem aqui para uma coisa so: provar que o B2 ACRESCENTOU, e nao
# mexeu. Uma lista escrita a mao envelhece — esta e curta e o teste diz quando.
ANTES_DO_B2 = {
    "BYTES", "CADENCE_STATE", "CAPTURED_AT", "COLLECTION_RUN_STARTED_AT",
    "DECLARED_FREQUENCY", "DISCOVERY_DEGRADED", "DOCUMENT_ID",
    "DOCUMENT_VERSION_ID", "EXPECTED_NEXT_UPDATE", "FACT_TIME", "HEALTH_STATE",
    "MIME_ASSINATURA", "OBSERVATION_RESULT", "OBSERVED_FREQUENCY",
    "PARSE_ERROR", "RAW_OBJECT_CREATED", "RAW_PATH",
    "RAW_PRESERVED_BEFORE_PARSE", "RAW_SHA256", "RUN_ID", "SOURCE_DATE",
    "SOURCE_DATE_ISO", "SOURCE_ID", "SOURCE_URL", "parse",
}


class CasoB2(CasoB1):
    """A mesma bancada do B1, mais um coletor que pode receber bytes sem data."""

    def coletar_sem_identidade(self, run_id):
        """Bytes que sao PDF de verdade e NAO dizem quando foram gerados.

        E o caminho mais barato ate `IDENTITY_FAILED`: a assinatura `%PDF` passa
        na validacao de bytes, e `identidade()` nao encontra `/CreationDate`,
        que e de onde sai `ARPAV:Z{NN}:{AAAAMMDDHHMMSS}`. Nenhuma infraestrutura
        nova, e nenhuma ida a rede.
        """
        driver = """
import { executarRodada } from "%s";
const semData = () => Buffer.concat([
  Buffer.from("%%PDF-1.4\\n/Title (boletim sem data de geracao)\\n", "latin1"),
  Buffer.alloc(4096, "z"),
  Buffer.from("\\n%%%%EOF\\n", "latin1")]);
const r = await executarRodada({
  runId: "%s", apenas: ["%s"], forcarBuf: semData, nota: "prova b2 negativa" });
console.log(JSON.stringify(r.resumo));
""" % (COLETOR.replace("\\", "/"), run_id, FONTE)
        r = subprocess.run(["node", "--input-type=module", "-e", driver],
                           cwd=RAIZ, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.strip().splitlines()[-1])


class OQueProduziuUmDocumentoDizQueProduziu(CasoB2):
    """1..3 · identidade documental real, carimbo presente."""

    def test_1_a_observacao_valida_declara_SOURCE_DOCUMENT(self):
        self.coletar("B2-PROVA-0001")
        for o in self.livro():
            self.assertEqual(o.get(ALVO), SOURCE_DOCUMENT, o.get("SOURCE_URL"))

    def test_2_o_carimbo_anda_colado_a_identidade_que_o_justifica(self):
        self.coletar("B2-PROVA-0002")
        o = self.livro()[0]
        self.assertEqual(o["DOCUMENT_ID"], "ARPAV:Z01:20260903160930")
        self.assertTrue(o["DOCUMENT_VERSION_ID"].startswith("v1_"))
        self.assertEqual(o[ALVO], SOURCE_DOCUMENT)

    def test_3_o_carimbo_nao_e_deduzido_do_formato(self):
        """O coletor nao pergunta ao PDF, ao MIME nem ao nome da fonte.

        Se perguntasse, a observacao SEM identidade — que tambem e `%PDF`, e
        tambem e de `IT-T2-002` — sairia carimbada. Ela nao sai.
        """
        self.coletar_sem_identidade("B2-PROVA-0003")
        o = self.livro()[0]
        # Chegar a IDENTITY_FAILED prova que os bytes passaram na validacao de
        # assinatura: quem nao e `%PDF` para antes, em BYTE_VALIDATION_FAILED.
        self.assertEqual(o["OBSERVATION_RESULT"], "IDENTITY_FAILED")
        self.assertEqual(o["SOURCE_ID"], FONTE)
        self.assertTrue(o["SOURCE_URL"].endswith(".pdf"))
        self.assertNotIn(ALVO, o)


class SemIdentidadeNaoHaAlvo(CasoB2):
    """4..6 · o que falhou nao promete nada."""

    def test_4_IDENTITY_FAILED_nao_recebe_alvo(self):
        self.coletar_sem_identidade("B2-PROVA-0004")
        obs = self.livro()
        self.assertEqual(len(obs), 4)
        for o in obs:
            self.assertEqual(o["OBSERVATION_RESULT"], "IDENTITY_FAILED")
            self.assertIsNone(o.get("DOCUMENT_ID"))
            self.assertNotIn(ALVO, o)

    def test_5_ausente_e_ausente_e_nao_uma_confissao_disfarcada(self):
        """`null`, `UNKNOWN` e `NAO SEI` nao sao CONCEPT_ID."""
        self.coletar_sem_identidade("B2-PROVA-0005")
        self.coletar("B2-PROVA-0005b")
        for o in self.livro():
            if ALVO in o:
                self.assertEqual(o[ALVO], SOURCE_DOCUMENT)
            self.assertNotIn(o.get(ALVO, "<ausente>"),
                             (None, "null", "UNKNOWN", "NAO SEI", "NÃO SEI", ""))

    def test_6_o_vocabulario_deste_corte_tem_um_valor_so(self):
        self.coletar("B2-PROVA-0006")
        self.coletar_sem_identidade("B2-PROVA-0006b")
        valores = {o[ALVO] for o in self.livro() if ALVO in o}
        self.assertEqual(valores, {SOURCE_DOCUMENT})


class VoltarAVerNaoEDeixarDeSerDocumento(CasoB2):
    """7..8 · reobservacao continua documental."""

    def test_7_SEEN_AGAIN_continua_a_declarar_SOURCE_DOCUMENT(self):
        self.coletar("B2-PROVA-D1")
        self.coletar("B2-PROVA-D2")
        segundas = [o for o in self.livro() if o["RUN_ID"] == "B2-PROVA-D2"]
        self.assertEqual(len(segundas), 4)
        for o in segundas:
            self.assertEqual(o["OBSERVATION_RESULT"], "SEEN_AGAIN")
            self.assertTrue(o["DOCUMENT_ID"] and o["DOCUMENT_VERSION_ID"])
            self.assertEqual(o[ALVO], SOURCE_DOCUMENT)

    def test_8_as_duas_observacoes_continuam_a_ser_duas(self):
        """Documento ja visto nao e documento nenhum, e nao se colapsam."""
        self.coletar("B2-PROVA-E1")
        self.coletar("B2-PROVA-E2")
        obs = self.livro()
        self.assertEqual(len(obs), 8)
        self.assertEqual(len({o["RUN_ID"] for o in obs}), 2)
        self.assertEqual(len({o["DOCUMENT_VERSION_ID"] for o in obs}), 4)


class OAdapterTransportaEnaoCria(CasoB2):
    """9..11 · quem escreve e o coletor; quem leva e o adapter."""

    def test_9_o_carimbo_atravessa_o_adapter_inteiro(self):
        self.coletar("B2-PROVA-0009")
        _, itens, _, _ = self.pela_rota("B2-PROVA-0009")
        self.assertEqual(len(itens), 4)
        for x in itens:
            self.assertEqual(x[ALVO], SOURCE_DOCUMENT)

    def test_10_o_adapter_nao_conhece_o_nome_do_campo(self):
        """Se ele o soubesse escrever, saberia escreve-lo errado."""
        fonte = io.open(os.path.join(RAIZ, "coleta", "italy_executor.py"),
                        encoding="utf-8").read()
        self.assertNotIn(ALVO, fonte)
        self.assertNotIn(SOURCE_DOCUMENT, fonte)

    def test_11_o_dono_da_escrita_e_o_coletor(self):
        fonte = io.open(COLETOR, encoding="utf-8").read()
        self.assertIn(ALVO, fonte)
        self.assertIn('const SOURCE_DOCUMENT = "SOURCE_DOCUMENT";', fonte)


class ACOLETARECORRENTEHERDA(CasoB2):
    """12 · o caminho agendado nao constroi observacao propria."""

    def test_12_o_recorrente_delega_a_observacao_ao_coletor_base(self):
        fonte = io.open(os.path.join(RAIZ, "coleta", "italy_recurrent_collect.mjs"),
                        encoding="utf-8").read()
        self.assertIn("executarRodada", fonte)
        self.assertNotIn("const obs = {", fonte)
        self.assertNotIn(ALVO, fonte)


class OB2ACRESCENTOUEnaoMEXEU(CasoB2):
    """13..14 · a semantica do RAW ficou onde estava."""

    def test_13_a_observacao_ganhou_exactamente_um_campo(self):
        self.coletar("B2-PROVA-0013")
        agora = set(self.livro()[0])
        self.assertEqual(agora - ANTES_DO_B2, {ALVO})
        self.assertEqual(ANTES_DO_B2 - agora, set())

    def test_14_os_campos_do_RAW_continuam_a_dizer_o_mesmo(self):
        self.coletar("B2-PROVA-0014")
        o = self.livro()[0]
        self.assertEqual(o["RUN_ID"], "B2-PROVA-0014")
        self.assertEqual(o["OBSERVATION_RESULT"], "BASELINE_DOCUMENT")
        self.assertEqual(o["DOCUMENT_ID"], "ARPAV:Z01:20260903160930")
        self.assertEqual(o["DOCUMENT_VERSION_ID"],
                         "v1_" + o["RAW_SHA256"][:12])
        self.assertTrue(o["RAW_OBJECT_CREATED"])
        self.assertTrue(str(o["RAW_PATH"]).endswith("agro_01.pdf"))
        self.assertTrue(o["CAPTURED_AT"].endswith("Z"))


class NaoSeAntecipouNada(CasoB2):
    """15..17 · o que a missao proibiu continua por fazer."""

    def test_15_a_permissao_por_fonte_continua_por_instalar(self):
        fonte = io.open(os.path.join(RAIZ, "regras", "italy_contracts.mjs"),
                        encoding="utf-8").read()
        self.assertNotIn("ALLOWED_STRUCTURED_TARGETS", fonte)

    def test_16_o_coletor_nao_criou_uma_segunda_lista_de_conceitos(self):
        """Uma constante e o nome do que ele fez. Uma lista seria autoridade."""
        fonte = io.open(COLETOR, encoding="utf-8").read()
        self.assertEqual(fonte.count('const SOURCE_DOCUMENT ='), 1)
        self.assertNotIn("CONCEPTS = [", fonte)
        # A PROSA PODE NOMEAR A PERMISSAO; O CODIGO NAO PODE LE-LA. O comentario
        # que explica onde `ALLOWED_STRUCTURED_TARGETS` vive e util, e um teste
        # que proibisse a palavra proibiria a explicacao junto com o defeito.
        codigo = "\n".join(l.split("//")[0] for l in fonte.splitlines())
        self.assertNotIn("ALLOWED_STRUCTURED_TARGETS", codigo)

    def test_17_a_porta_do_RAW_nao_ganhou_autoridade_sobre_o_conceito(self):
        import ingresso as ing
        self.assertNotIn(ALVO, ing.DO_COLETOR)


if __name__ == "__main__":
    unittest.main(verbosity=2)
