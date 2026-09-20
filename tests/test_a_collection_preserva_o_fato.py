#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A COLLECTION PRESERVA O QUE JÁ SABE — e continua a não saber o que não sabe.

Estes testes são o RED TEAM da missão `C-COL-PRESERVE-FACTS-V1`, escritos para
derrubar a solução e não para a aplaudir. Cada um deles falhava ANTES da missão,
e o comentário diz o que foi medido.

    A PERGUNTA QUE ELES GUARDAM:
    a Collection preserva os factos e as identidades que já existem no material,
    SEM fabricar o que não existe?

⚠️ E metade deles guarda a SEGUNDA metade da pergunta. Um teste que só verifica
que os campos vêm cheios ensina o código a enchê-los — e um campo cheio de
palpite é pior do que um campo vazio, porque ninguém o vai procurar.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ⚠️ O PREÂMBULO É O DA CASA, E ISTO CUSTOU UM ERRO DE COLETA.
# `from admissao import admissao` funciona quando este ficheiro corre sozinho, e
# REBENTA na suíte inteira: outro teste já pôs `admissao/` em `sys.path` pelas
# gavetas, e aí o nome `admissao` passa a resolver para o MÓDULO e não para o
# pacote. O resultado é `ImportError: cannot import name 'admissao' from
# 'admissao'`, que só aparece quando a suíte corre junta.
#
#     UM IMPORT QUE DEPENDE DE QUEM CORREU ANTES NÃO É UM IMPORT: É UMA APOSTA.
for g in (RAIZ, os.path.join(RAIZ, "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas  # noqa: E402,F401
import admissao  # noqa: E402
import sala_de_espera as espera  # noqa: E402
from coleta import ingresso  # noqa: E402
from coleta import rota_forward_documento as rota  # noqa: E402
from leis import artefato as art  # noqa: E402
from leis import fato_local as fl  # noqa: E402
import motor.normalize_agro as agro  # noqa: E402

#: Um texto que passa a régua do universo T3 — dois termos distintos. Serve de
#: veículo; nenhum teste aqui mede a régua do universo.
TEXTO_T3 = ("Bollettino fitosanitario: peronospora della vite, trappole con "
            "catture rilevate")

NAO_SEI = art.NAO_SEI


def _ready(item, universo="T3"):
    d = admissao.decidir(item, universo, corrida="teste")
    if d.resultado != admissao.SIM:
        raise AssertionError("o item nao passou a porta: %s · %s"
                             % (d.resultado, d.motivo))
    return admissao.pronto_para_inteligencia(item, d)


def _facto(**extra):
    """Um item no estágio `FATO`, com o mínimo para atravessar a porta.

    ⚠️ A ÂNCORA DE TEMPO É O CAMPO GENÉRICO `data`, E É DE PROPÓSITO.
    A porta exige ALGUMA âncora de tempo a um facto, e este helper precisa de
    uma. `data` é a única que serve aqui sem contaminar as medições: ela
    admite, e NÃO vira `FACT_TIME` nem entra no envelope do facto. Pôr
    `fact_time` tornaria todo teste de «isto continua `NAO SEI`» inútil, e pôr
    `published_at` faria o mesmo ao teste que mede `PUBLISHED_AT`.
    """
    base = {"id": "it-1", "texto": TEXTO_T3, "source_id": "IT-T3-002",
            "claim_id": "CL-1", "data": "2026-01-01"}
    base.update(extra)
    return base


class OTempoDoFatoNaoSePreenche(unittest.TestCase):
    """RT-COL-01 · RT-COL-03 — as duas maneiras medidas de fabricar `FACT_TIME`."""

    def test_caso_1_publication_time_existe_e_fact_time_nao(self):
        """A data de PUBLICAÇÃO não é a data do facto. Nunca foi, e já foi.

        Medido antes: `_tem_quando({"published_at": ...})` respondia «tem tempo
        do fato» e o contrato de saída carimbava-a como `FACT_TIME`.
        """
        r = _ready(_facto(published_at="2026-06-30"))
        self.assertEqual(NAO_SEI, r["FACT_TIME"])
        self.assertEqual("2026-06-30", r["PUBLISHED_AT"])

    def test_caso_5_campo_generico_data_nao_promove(self):
        """RT-COL-03 · o campo `data` não declara DE QUE TEMPO é.

        Medido nesta árvore, antes:

            pronto_para_inteligencia({"data": "2026-06-30"})
            -> FACT_TIME = "2026-06-30"

        Um coletor põe em `data` a data que tem — a do documento. Isso produzia
        um `FACT_TIME` falso, carimbado como facto, sem ninguém escolher.
        """
        r = _ready(_facto(data="2026-06-30"))
        self.assertEqual(NAO_SEI, r["FACT_TIME"])

    def test_o_gate_continua_a_admitir_por_ancora_e_diz_qual(self):
        """APERTAR O TRANSPORTE NÃO É APERTAR A PORTA.

        Corrigir o transporte e, de caminho, passar a recusar quem só tem data
        de publicação seria encolher a coleta sem ninguém ter decidido isso.
        """
        _, _, ev = admissao._tem_quando({"data": "2026-06-30"})
        self.assertEqual("TIME_UNDECLARED", ev["que_tempo"])
        self.assertEqual(NAO_SEI, ev["fact_time"])

    def test_caso_3_os_dois_tempos_sobrevivem_separados(self):
        r = _ready(_facto(fact_time="2026-06-02", published_at="2026-06-30"))
        self.assertEqual("2026-06-02", r["FACT_TIME"])
        self.assertEqual("2026-06-30", r["PUBLISHED_AT"])

    def test_rt_col_14_ausencia_nao_vira_vazio_nem_zero(self):
        """`NAO SEI` com espaço — e é essa a palavra que a Sala lê como NULL.

        A constante `admissao.NAO_SEI` vale `"NAO_SEI"` COM UNDERSCORE e é um
        RESULTADO da porta, não uma ausência. Trocar uma pela outra faz a
        ausência virar a string `"NAO_SEI"`, que o banco guardaria como valor
        medido. Este teste existe porque esta troca já foi feita.
        """
        r = _ready(_facto())
        for campo in ("FACT_TIME", "FACT_LOCATION", "SOURCE_LOCATION",
                      "PUBLISHED_AT", "OBSERVED_AT", "FACT_TIME_BASIS"):
            self.assertEqual(NAO_SEI, r[campo], campo)
            self.assertNotIn(r[campo], ("", 0, None, "NAO_SEI"))


class OLugarDoFatoNaoSePreenche(unittest.TestCase):
    """RT-COL-02 — `SOURCE_LOCATION` não é `FACT_LOCATION`."""

    def test_caso_2_source_location_existe_e_fact_location_nao(self):
        r = _ready(_facto(source_location="Bari"))
        self.assertEqual("Bari", r["SOURCE_LOCATION"])
        self.assertEqual(NAO_SEI, r["FACT_LOCATION"])

    def test_caso_4_os_dois_lugares_sobrevivem_separados(self):
        r = _ready(_facto(source_location="Bari", fact_location="Puglia"))
        self.assertEqual("Bari", r["SOURCE_LOCATION"])
        self.assertEqual("Puglia", r["FACT_LOCATION"])

    def test_o_ambito_do_documento_nao_e_o_lugar_do_fato(self):
        """Medido contra o boletim REAL `IT-T3-002`, e ele passava.

            "BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO"
            -> FACT_LOCATION = Salerno, com trecho e âncora

        `bollettino` é âncora positiva e governava `Salerno`. Só que aquele
        título diz PARA QUE PROVÍNCIA o boletim é — é o âmbito do documento, e
        não o sítio de um acontecimento.
        """
        aceitas, recusadas = fl.localizacoes_do_fato(
            "BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO")
        self.assertEqual([], [a["FACT_LOCATION"] for a in aceitas])
        self.assertIn("Salerno", [r["PLACE"] for r in recusadas])

    def test_o_nome_de_uma_instituicao_nao_e_um_acontecimento(self):
        """`osservatorio` É UM ÓRGÃO. `osservato` É UM ACONTECIMENTO.

        Medido contra o notiziario REAL da ARIF, `IT-T3-008`: a âncora
        `osservat[oaie]` casava DENTRO de `Osservatorio` — `_ancoras()` não
        exigia fronteira de palavra, e `mencoes()`, logo acima dela, exigia.
        """
        aceitas, _ = fl.localizacoes_do_fato(
            "comunicati ufficiali dell'Osservatorio Fitosanitario della "
            "Regione Puglia")
        self.assertEqual([], aceitas)

    def test_e_a_ancora_verdadeira_continua_a_valer(self):
        """Apertar não pode ser cegar: o caso legítimo tem de continuar a passar."""
        aceitas, _ = fl.localizacoes_do_fato("sintomi osservati in Puglia")
        self.assertEqual(["Puglia"], [a["FACT_LOCATION"] for a in aceitas])


class OFatoNaoSeEsmaga(unittest.TestCase):
    """RT-COL-04 · RT-COL-05 — o facto de N campos que saía com 12."""

    CAMPOS_DO_FATO = ("claim_id", "subject", "predicate", "object", "crop",
                      "crop_eppo", "problem", "problem_eppo", "method", "unit",
                      "scale", "denominator", "phenological_stage", "doi",
                      "registration_id", "active_substance")

    def test_nenhum_campo_do_fato_se_perde(self):
        item = _facto(**{c: "v-%s" % c for c in self.CAMPOS_DO_FATO})
        r = _ready(item)
        self.assertEqual(admissao.FATO, r["ESTAGIO"])
        for campo in self.CAMPOS_DO_FATO:
            self.assertIn(campo, r["FATO"], campo)
            self.assertEqual("v-%s" % campo, r["FATO"][campo])

    def test_um_documento_nao_ganha_envelope_vazio(self):
        """`{}` diria «olhei e não havia». A verdade é «não se aplica».

        COL-LAW-201: um documento RELATA, não é o facto.
        """
        r = _ready({"id": "d", "texto": TEXTO_T3, "source_id": "S",
                    "artifact_type": "DERIVED", "parent_sha256": "ab"})
        self.assertEqual(admissao.DOCUMENTO, r["ESTAGIO"])
        self.assertEqual(art.NAO_SE_APLICA, r["FATO"])

    def test_o_envelope_nao_duplica_quem_ja_tem_campo_proprio(self):
        """ONE CONCEPT → ONE OWNER, e um campo copiado é meio dono.

        `fact_time` dentro do envelope seria uma segunda porta para o mesmo
        valor, livre para divergir do campo `FACT_TIME` a partir do dia em que
        um dos dois mudasse.
        """
        r = _ready(_facto(fact_time="2026-06-02", source_location="Bari",
                          published_at="2026-06-30", data="2026-01-01"))
        for proibido in ("fact_time", "source_location", "published_at",
                         "data", "texto", "id", "source_id"):
            self.assertNotIn(proibido, r["FATO"], proibido)

    def test_o_envelope_tem_ordem_canonica(self):
        """A impressão da corrida assina BYTES. Ordem instável = conflito falso."""
        a = _ready(_facto(zebra="z", alfa="a", meio="m"))["FATO"]
        b = _ready(_facto(meio="m", zebra="z", alfa="a"))["FATO"]
        self.assertEqual(list(a), list(b))
        self.assertEqual(sorted(a), list(a))

    def test_a_collection_nao_extrai_claim_do_texto(self):
        """COL-LAW-202: extracção de claim é `TARGET`, e NÃO existe nesta casa.

        Um texto cheio de agronomia, sem marcas de facto declaradas, continua a
        ser um documento. Preservar o que chegou não é adivinhar o que devia ter
        chegado.
        """
        r = _ready({"id": "x", "texto": TEXTO_T3, "source_id": "S",
                    "artifact_type": "DERIVED", "parent_sha256": "ab"})
        self.assertEqual(art.NAO_SE_APLICA, r["FATO"])


class AEspecieDaEvidenciaAtravessa(unittest.TestCase):
    """RT-COL-06 — a espécie probatória sumia no READY."""

    def test_a_especie_declarada_pela_fonte_chega_intacta(self):
        r = _ready(_facto(source_declared_evidence_class="AGROCLIMATIC_SIGNAL"))
        self.assertEqual("AGROCLIMATIC_SIGNAL",
                         r["SOURCE_DECLARED_EVIDENCE_CLASS"])

    def test_o_nome_do_campo_nao_deixa_confundir_declarado_com_medido(self):
        """DECLARADO PELA FONTE != MEDIDO NO DOCUMENTO.

        Um campo chamado `EVIDENCE_CLASS` seria lido como a espécie DESTE
        documento, medida. Não é: é a expectativa de quem publica, e é texto
        livre — medido, os contratos dizem coisas como «OBSERVED_FIELD_SIGNAL +
        TECHNICAL_GUIDELINE (separar por bloco)».
        """
        self.assertIn("SOURCE_DECLARED_EVIDENCE_CLASS", espera.CAMPOS_READY)
        self.assertNotIn("EVIDENCE_CLASS", espera.CAMPOS_READY)

    def test_dois_documentos_de_especies_diferentes_deixam_de_ser_iguais(self):
        clima = _ready(_facto(id="a",
                              source_declared_evidence_class="AGROCLIMATIC_SIGNAL"))
        campo = _ready(_facto(id="b",
                              source_declared_evidence_class="OBSERVED_FIELD_SIGNAL"))
        self.assertNotEqual(clima["SOURCE_DECLARED_EVIDENCE_CLASS"],
                            campo["SOURCE_DECLARED_EVIDENCE_CLASS"])


class AIdentidadeNaoSeFabrica(unittest.TestCase):
    """RT-COL-07 — `ITEM_ID = "?"`."""

    def test_um_item_sem_endereco_nao_passa_a_porta(self):
        """COL-LAW-034: `"?"` e a string vazia NÃO DEVEM ser identidade.

        Medido antes: um item com `source_id`, sem `id` e sem `url`, passava e
        chegava à Sala com `ITEM_ID = '?'`. Dois assim na mesma corrida ficavam
        com a mesma morada — e `sala_de_espera.ItemAmbiguo` já existia por isso.
        """
        d = admissao.decidir({"texto": TEXTO_T3, "source_id": "S",
                              "fact_time": "2026-01-01", "claim_id": "c"}, "T3")
        self.assertEqual(admissao.NAO_SEI, d.resultado)
        self.assertEqual("identidade", d.regra)
        self.assertNotEqual("?", d.item)

    def test_source_id_nao_serve_de_identidade_do_item(self):
        """A fonte é de QUEM PUBLICA. O item é o item."""
        r, _, _ = admissao._tem_identidade({"source_id": "IT-T3-002"})
        self.assertEqual(admissao.NAO_SEI, r)

    def test_a_url_serve_e_o_id_serve(self):
        self.assertEqual(admissao.SIM, admissao._tem_identidade({"id": "x"})[0])
        self.assertEqual(admissao.SIM,
                         admissao._tem_identidade({"url": "https://x"})[0])

    def test_a_rota_canonica_nao_e_afectada(self):
        """Apertar a porta não pode partir a estrada que já corria."""
        item = rota.item_para_a_porta(
            {"CONTENT_ID": "c1", "TEXTO": TEXTO_T3, "SOURCE_ID": "S",
             "ARTIFACT_TYPE": "DERIVED", "PARENT_SHA256": "ab"})
        self.assertEqual("c1", item["id"])
        self.assertEqual(admissao.SIM, admissao._tem_identidade(item)[0])


class ARotaRealTransportaOQueADeclarouTransportar(unittest.TestCase):
    """RT-COL-15 — a estrada que dizia `NAO SEI` por construção."""

    UNIDADE = {"CONTENT_ID": "CAMPANIA:SA:02-09-2026", "TEXTO": TEXTO_T3,
               "SOURCE_ID": "IT-T3-002", "ARTIFACT_TYPE": "DERIVED",
               "PARENT_SHA256": "ab", "RAW_ASSET_ID": 77,
               "CAPTURED_AT": "2026-09-07",
               "SOURCE_LOCATION": "Napoli", "PUBLISHED_AT": "2026-09-02",
               "FACT_LOCATION_BASIS": "sem ancora de acontecimento",
               "SOURCE_DECLARED_EVIDENCE_CLASS": "TECHNICAL_GUIDELINE"}

    def test_o_que_a_fronteira_declara_chega_a_porta(self):
        item = rota.item_para_a_porta(self.UNIDADE)
        self.assertEqual("Napoli", item["source_location"])
        self.assertEqual("2026-09-02", item["published_at"])
        self.assertEqual("TECHNICAL_GUIDELINE",
                         item["source_declared_evidence_class"])

    def test_todo_nome_que_a_fronteira_transporta_tem_par_no_tradutor(self):
        """DECLARAR QUE ATRAVESSA != TER POR ONDE ATRAVESSAR.

        Um nome em `FRONTEIRA_TRANSPORTA` sem entrada em `PARA_A_PORTA` chega
        do outro lado em MAIÚSCULAS, e a porta lê minúsculas: o valor fica no
        item a ser lido por ninguém.
        """
        sem_par = [n for n in ingresso.FRONTEIRA_TRANSPORTA
                   if n not in ingresso.PARA_A_PORTA]
        self.assertEqual([], sem_par)

    def test_o_que_a_unidade_nao_traz_continua_nao_sei(self):
        """Transportar não é preencher."""
        r = _ready(rota.item_para_a_porta(self.UNIDADE))
        self.assertEqual(NAO_SEI, r["FACT_TIME"])
        self.assertEqual(NAO_SEI, r["FACT_LOCATION"])
        self.assertEqual(77, r["RAW_OBSERVATION_ID"])


class OLivroGuardaAProvaDeCadaPortao(unittest.TestCase):
    """RT-COL-05 (segunda metade) — a evidência era só a da ÚLTIMA pergunta."""

    def test_a_prova_do_portao_temporal_fica_escrita(self):
        """Medido antes: a chave `quando` não estava no livro.

        Um item que atravessava por uma data de PUBLICAÇÃO chegava ao livro com
        `{"palavras": [...], "estagio": "FATO"}`, e não havia em sítio nenhum a
        prova de que o tempo do facto continuava por saber.

            COL-LAW-042 exige `evidence`. Ela estava lá, e NÃO era a que
            provava a passagem.
        """
        d = admissao.decidir(_facto(published_at="2026-06-30"), "T3")
        portoes = d.evidencia["portoes"]
        self.assertEqual("PUBLICATION_TIME", portoes["tempo do fato"]["que_tempo"])
        self.assertEqual(NAO_SEI, portoes["tempo do fato"]["fact_time"])

    def test_todos_os_portoes_que_responderam_estao_no_livro(self):
        d = admissao.decidir(_facto(published_at="2026-06-30"), "T3")
        perguntados = [n for n, _ in admissao.perguntas_do_estagio(admissao.FATO)]
        for nome in perguntados + ["pertence ao universo"]:
            self.assertIn(nome, d.evidencia["portoes"], nome)

    def test_os_portoes_nao_se_achatam_uns_nos_outros(self):
        """Dois portões podem chamar `quando` a coisas diferentes."""
        d = admissao.decidir(_facto(published_at="2026-06-30"), "T3")
        self.assertIsInstance(d.evidencia["portoes"]["legivel"], dict)
        self.assertIn("caracteres", d.evidencia["portoes"]["legivel"])


class AIdentidadeDoProblemaSoComAutoridade(unittest.TestCase):
    """RT-COL-08 · RT-COL-09 · RT-COL-13 — o `ISSUE_ID` fabricado."""

    @classmethod
    def setUpClass(cls):
        cls.dic = agro.es_dict()

    def _codigos(self, texto):
        return [m["ISSUE_EPPO"]
                for m in agro.mencoes_de_problema(texto, self.dic)]

    def test_nome_exacto_conhecido_e_confirmado(self):
        self.assertEqual(["POLYBO"], self._codigos("Lobesia botrana"))

    def test_nome_parecido_nao_e_equivalente(self):
        """RT-COL-09 · `botranax` não é `botrana`.

        Nenhum `SequenceMatcher` aqui: um `ratio()` alto entre dois nomes de
        espécie é a maneira mais rápida de cunhar um código que ninguém reabre.
        """
        self.assertEqual([], self._codigos("Lobesia botranax na vinha"))
        self.assertEqual([], self._codigos("xLobesia botrana colado"))

    def test_um_rotulo_de_gaveta_nao_e_um_taxon(self):
        """Medido a FALHAR na primeira versão desta função.

            mencoes_de_problema("malas hierbas no campo")  ->  3WEEDT

        `"Malas hierbas"` tem o FEITIO de um binómio — maiúscula, minúscula,
        duas palavras. O que o denuncia não é o feitio: é a tabela do MAPA
        repetir o nome comum na coluna científica quando não tem nome
        científico nenhum.
        """
        self.assertEqual([], self._codigos("malas hierbas no campo"))

    def test_nome_comum_italiano_nao_cunha_codigo(self):
        """Não há autoridade italiano→EPPO nesta árvore. `UNKNOWN`, e ponto.

        Cunhar por semelhança com o espanhol seria junção por semelhança
        textual — que a COL-LAW-034 proíbe.
        """
        self.assertEqual([], self._codigos("peronospora della vite"))

    def test_o_termo_original_fica_preservado(self):
        """COL-LAW-203: NORMALIZAÇÃO NÃO DESTRÓI O VALOR ORIGINAL."""
        m = agro.mencoes_de_problema("Lobesia botrana", self.dic)[0]
        self.assertEqual("Lobesia botrana", m["TERMO_ORIGINAL"])
        self.assertIn("RULE_VERSION", m)
        self.assertIn("AUTORIDADE", m)

    def test_uma_mencao_nao_e_uma_ocorrencia(self):
        """RT-COL-10 · um índice que LISTA trinta pragas não afirma trinta focos."""
        m = agro.mencoes_de_problema("Lobesia botrana", self.dic)[0]
        self.assertEqual(agro.ISSUE_MENTION, m["ESPECIE_DO_ACHADO"])
        self.assertNotEqual(agro.ISSUE_OCCURRENCE, m["ESPECIE_DO_ACHADO"])

    def test_a_falta_de_autoridade_fica_contavel(self):
        """NOT_IN_AUTHORITY != NOT_A_PROBLEM.

        Sem isto, um boletim cheio de `peronospora` sai com zero menções e
        parece um documento sem problema nenhum.
        """
        s = agro.termos_sem_autoridade("peronospora della vite", ("peronospora",))
        self.assertEqual("UNKNOWN", s[0]["ISSUE_EPPO"])
        self.assertEqual("peronospora", s[0]["TERMO_ORIGINAL"])

    def test_texto_vazio_nao_inventa_nada(self):
        self.assertEqual([], agro.mencoes_de_problema("", self.dic))


class OContratoDeSaidaTemUmDonoSo(unittest.TestCase):
    """RT-COL-17 — a mudança de contrato não pode partir o documento comum."""

    def test_a_sala_e_o_dono_declaram_os_mesmos_campos(self):
        r = _ready(_facto())
        self.assertEqual(tuple(r), espera.CAMPOS_READY)

    def test_um_documento_comum_nao_agronomico_continua_a_passar(self):
        """Nenhum campo novo é obrigatório para quem não é agro."""
        r = _ready({"id": "generico", "texto": TEXTO_T3, "source_id": "S",
                    "artifact_type": "DERIVED", "parent_sha256": "ab"})
        self.assertEqual("PRONTO_PARA_INTELIGENCIA", r["ESTADO"])
        self.assertEqual(art.NAO_SE_APLICA, r["FATO"])

    def test_a_sala_aceita_o_que_a_admissao_produz(self):
        espera._conferir_unidades([_ready(_facto()),
                                   _ready(_facto(id="b", crop="vite"))])

    def test_a_sala_recusa_um_ready_da_versao_antiga(self):
        """Um READY de 12 campos já não cumpre o contrato, e tem de gritar."""
        velho = {c: "x" for c in espera.CAMPOS_READY
                 if c not in ("ESTAGIO", "FATO", "FACT_TIME_BASIS",
                              "FACT_LOCATION_BASIS", "PUBLISHED_AT",
                              "OBSERVED_AT", "SOURCE_DECLARED_EVIDENCE_CLASS")}
        velho["ESTADO"] = "PRONTO_PARA_INTELIGENCIA"
        with self.assertRaises(ValueError):
            espera._conferir_unidades([velho])


class OReprocessamentoNaoFabricaColheita(unittest.TestCase):
    """RT-COL-11 · RT-COL-15 · RT-COL-16 · RT-COL-18 — contra material REAL."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(RAIZ, "provas"))
        import a_collection_preserva_o_fato as prova  # noqa: E402
        cls.prova = prova
        cls.r = prova.correr()

    def test_rt_col_18_isto_corre_sobre_material_real_e_nao_sobre_fixture(self):
        """⚠️ A GUARDA MAIS IMPORTANTE DESTE FICHEIRO.

        Um teste que passa numa fixture e falha em material real não mede nada —
        e esta missão tem a prova disso: **duas** recusas certas só apareceram
        contra os documentos verdadeiros. Nenhuma fixture que eu escrevesse teria
        contido `«dell'Osservatorio Fitosanitario della Regione Puglia»`, porque
        eu não sabia que esse era o problema.

            UMA FIXTURE MEDE O QUE QUEM A ESCREVEU JÁ SABIA.
        """
        self.assertGreater(self.r["OBSERVACOES_NO_LIVRO"], 100)
        self.assertGreater(self.r["COM_TEXTO_DERIVADO_NESTA_ARVORE"], 0)
        self.assertGreater(self.r["ADMITIDOS"], 0)

    def test_rt_col_11_nenhuma_observacao_nova_e_fabricada(self):
        """Reprocessar é olhar outra vez para o MESMO bruto.

        Fingir uma colheita nova seria inventar uma corrida que não houve. A
        prova declara-o, e aqui mede-se: o livro do coletor tem de sair da
        travessia com exactamente o mesmo número de linhas com que entrou.
        """
        antes = len(self.prova.observacoes())
        self.prova.correr()
        self.assertEqual(antes, len(self.prova.observacoes()))
        self.assertEqual("YES — nada foi colhido, nenhuma observacao nova foi criada",
                         self.r["SO_LEITURA"])

    def test_cada_unidade_aponta_para_o_bruto_de_onde_nasceu(self):
        """Linhagem: o `RAW_SHA256` do recibo é o da observação do livro."""
        # `.get`, e não `[]`: nem toda a observação do livro tem bytes. 31 das
        # 175 são falhas de transporte — `curl: (56) CONNECT tunnel failed` — e
        # uma observação que nunca recebeu bytes não tem `RAW_SHA256`. Isso é
        # uma medição, não um buraco no livro.
        shas = {o.get("RAW_SHA256") for o in self.prova.observacoes()}
        self.assertTrue(self.r["RECIBOS"])
        for recibo in self.r["RECIBOS"]:
            self.assertIn(recibo["RAW_SHA256"], shas)

    def test_rt_col_16_toda_normalizacao_diz_por_que_regra_passou(self):
        """Regra nova não pode mexer em material antigo sem deixar rasto."""
        for recibo in self.r["RECIBOS"]:
            self.assertEqual(self.prova.VERSAO_DO_REPROCESSAMENTO,
                             recibo["RULE_VERSION"])
            for m in recibo["ISSUE"]["MENCOES_COM_AUTORIDADE"]:
                self.assertIn("RULE_VERSION", m)
                self.assertIn("AUTORIDADE", m)

    def test_o_tempo_e_o_lugar_do_fato_continuam_NAO_SEI_e_dizem_porque(self):
        """⚠️ A METADE QUE IMPORTA. Preencher não era o objectivo.

        O livro do coletor **já tinha medido** que não sabe o tempo do facto, e
        escreveu a razão em 175 observações. O que mudou não é o valor: é essa
        frase chegar ao outro lado.
        """
        for pronto, recibo in zip(self.r["READY"], self.r["RECIBOS"]):
            self.assertEqual(NAO_SEI, pronto["FACT_TIME"])
            self.assertEqual(NAO_SEI, pronto["FACT_LOCATION"])
            self.assertNotEqual(NAO_SEI, pronto["FACT_TIME_BASIS"])
            self.assertNotEqual(NAO_SEI, pronto["FACT_LOCATION_BASIS"])
            self.assertTrue(recibo["FACT_TIME"]["BASE"])

    def test_a_fronteira_recusa_ficar_calada_sobre_o_que_nao_atravessou(self):
        """`ingresso.conferir_fronteira` mede a travessia; não a adivinha."""
        # ⚠️ ISTO EXIGIA `SOURCE_LOCATION` transportado em TODOS os recibos —
        # verdade enquanto so as sete fontes do piloto (todas com sede no
        # gazetteer) tinham texto nesta arvore. Uma fonte cujo contrato declara
        # um lugar que o gazetteer nao cobre («Terlano (BZ)», IT-T3-011) sai
        # honestamente NAO SEI, e NAO SEI nao se transporta — transporta-se a
        # BASE. O invariante: transportado <=> valor conhecido; quando nao e,
        # a razao esta escrita e o campo nao esta em falta.
        for recibo in self.r["RECIBOS"]:
            fronteira = recibo["FRONTEIRA"]
            with self.subTest(doc=recibo.get("DOCUMENT_ID"), fonte=recibo.get("SOURCE_ID")):
                self.assertEqual([], fronteira["EXIGIDOS_EM_FALTA"])
                lugar = recibo["SOURCE_LOCATION"]
                if lugar["VALOR"] != NAO_SEI:
                    self.assertIn("SOURCE_LOCATION", fronteira["TRANSPORTADOS"])
                else:
                    self.assertNotIn("SOURCE_LOCATION", fronteira["TRANSPORTADOS"])
                    self.assertTrue(lugar.get("BASE"), "NAO SEI sem razao escrita")

    def test_o_que_o_contrato_de_fonte_nao_prova_sai_NAO_SEI(self):
        """`node` pode não existir na máquina — e aí a resposta é `NAO SEI`.

        Nunca um valor de reserva. Este teste aceita as duas realidades e
        recusa a terceira: um valor inventado.
        """
        from regras import contratos_de_fonte as cdf
        for sid, esperado in (("IT-T9-008", NAO_SEI),   # "site nacional"
                              ("IT-T5-002", NAO_SEI)):  # comune fora do gazetteer
            self.assertEqual(esperado,
                             cdf.lugar_declarado_pela_fonte(sid)["VALOR"])
        napoli = cdf.lugar_declarado_pela_fonte("IT-T3-002")
        if cdf.declarados():
            self.assertEqual("Napoli", napoli["VALOR"])
            self.assertIn("gazetteer", napoli["BASE"])
        else:
            self.assertEqual(NAO_SEI, napoli["VALOR"])


if __name__ == "__main__":
    unittest.main()
