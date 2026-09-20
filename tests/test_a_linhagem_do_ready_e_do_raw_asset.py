#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UM `raw_asset`, UM `READY` — a linhagem não se multiplica na re-observação.

A LEI, LIDA DO DONO E NÃO INFERIDA
-----------------------------------
`BIBLIA-CANONICA-DA-COLETA.md`, secção «`RAW_OBSERVATION_ID` — a linhagem viaja,
e viaja uma vez só»:

    RAW_OBSERVATION_ID = raw_asset.id. Ausente: NAO SEI. **Nunca** derivado de
    sha256, URL, storage_path, filename ou RUN_ID.

        TER RAW != O READY CONSEGUIR PROVAR QUAL RAW É O SEU.

E `raw_asset` é uma linha por OBJECTO GUARDADO (`supabase/migrations/001`):
`id bigserial primary key`, `storage_path text not null unique`.

O QUE ISSO IMPLICA, E É O QUE ESTE FICHEIRO PROVA
--------------------------------------------------
Uma re-observação que **não guarda objecto novo** não cria `raw_asset` novo.
Logo não tem `RAW_OBSERVATION_ID` próprio. Logo **não origina um segundo
READY** — porque o READY que dela sairia teria a linhagem do mesmo bruto.

    UM `raw_asset` -> UM `RAW_OBSERVATION_ID` -> UM `READY`.

⚠️ ISTO NÃO É DEDUPLICAR POR `DOCUMENT_ID`.
`DOCUMENT_ID` é o nome do documento no mundo; não é identidade de observação
bruta, e usá-lo aqui seria a segunda identidade que esta casa proíbe. O que se
lê é o campo que a PRÓPRIA COLETA escreve — `RAW_OBJECT_CREATED` — e que diz,
sem interpretação, se houve objecto guardado.

⚠️ E AS DUAS OBSERVAÇÕES CONTINUAM A EXISTIR.
`SEEN_AGAIN` é um facto verdadeiro: alguém foi lá e o documento continuava
igual. Ela permanece no livro e permanece nos recibos. O que não acontece é
nascer um segundo READY de um bruto que nunca foi guardado duas vezes.

    NÃO SE APAGA HISTÓRIA. DEIXA-SE DE CONTAR DUAS VEZES O MESMO BRUTO.
"""
from __future__ import annotations

import collections
import io
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "provas"))
import _gavetas                                        # noqa: E402,F401
import a_collection_preserva_o_fato as prova           # noqa: E402

LIVRO = os.path.join(RAIZ, "data", "collection-ledger", "italy",
                     "observations.ndjson")
SAIDA = os.path.join(RAIZ, "data", "derivados",
                     "A-COLLECTION-PRESERVA-O-FATO.json")


def _livro():
    with io.open(LIVRO, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


# ═════════════════════════════════════════════════════════════════════════════
class OLivroDizQuemGuardouBruto(unittest.TestCase):
    """Antes de usar o campo, provar que ele responde sempre e sem furos."""

    @classmethod
    def setUpClass(cls):
        cls.obs = _livro()

    def test_quem_criou_objecto_tem_caminho_e_quem_nao_criou_nao_tem(self):
        """`RAW_OBJECT_CREATED` e `RAW_PATH` respondem a DUAS perguntas.

        ⚠️ DECISAO DE LEI, escrita em 20/09/2026. Isto exigia
        `RAW_OBJECT_CREATED is True  <=>  RAW_PATH is not None`. Era a lei
        antiga: «os dois contam a mesma historia». O coletor deixou de a
        seguir de proposito (coleta/italy_pilot_collect.mjs, «NAO CRIEI O
        OBJECTO AGORA != NAO HA BYTES EM LADO NENHUM»): sem caminho numa
        SEEN_AGAIN, a porta de entrada preservava o JSON da observacao como se
        fosse o documento. A lei que vale e a do coletor — e ficou aqui, e nao
        num numero:

            RAW_OBJECT_CREATED  «esta corrida materializou o objecto?»
            RAW_PATH            «onde estao os bytes?»

        O que continua obrigatorio: criou => ha caminho; ha caminho => ha
        documento e ha bytes (sha); falhou => nem caminho nem criacao.
        """
        for o in self.obs:
            criou = o.get("RAW_OBJECT_CREATED") is True
            tem = o.get("RAW_PATH") is not None
            with self.subTest(doc=o.get("DOCUMENT_ID"),
                              result=o.get("OBSERVATION_RESULT")):
                if criou:
                    self.assertTrue(tem, "criou o objecto e nao diz onde")
                if tem:
                    self.assertTrue(o.get("DOCUMENT_ID"), "caminho sem documento")
                    self.assertTrue(o.get("RAW_SHA256"), "caminho sem impressao digital")
                    self.assertNotEqual(o.get("HEALTH_STATE"), "FAILED",
                                        "observacao FAILED com caminho de bytes")
                if o.get("HEALTH_STATE") == "FAILED" and not o.get("DOCUMENT_ID"):
                    self.assertFalse(criou)
                    self.assertFalse(tem)

    def test_reobservacao_nunca_guarda_objecto_novo(self):
        """`SEEN_AGAIN` é «fui lá e está igual» — não é uma captura nova.

        O invariante e sobre BYTES, nao sobre o disco desta arvore: uma
        reobservacao tem os MESMOS bytes (mesmo sha256) de uma observacao
        anterior do MESMO documento da MESMA fonte — nunca bytes novos com o
        nome de «visto outra vez». E, quando as duas apontam para ficheiro, e
        o mesmo ficheiro (mesmo nome).

        ⚠️ `RAW_OBJECT_CREATED` PODE ser True numa SEEN_AGAIN, e isso e
        verdade e nao defeito: o ledger e rastreado no Git e o armazem do
        coletor nao e inteiro; uma arvore nova conhece o documento pelo livro
        e nao tem os bytes no disco — e o coletor volta a materializa-los,
        com o MESMO sha. Medido em 20/09/2026 na Big Collection 2 (CAMPANIA
        SA-16-09, MINSALUTE 20260914). Exigir `False` aqui era exigir que o
        disco desta arvore fosse a fonte da verdade; a fonte da verdade e o
        sha.
        """
        vistas = {}
        for o in self.obs:
            chave = (o.get("SOURCE_ID"), o.get("DOCUMENT_ID"))
            if o.get("OBSERVATION_RESULT") == "SEEN_AGAIN":
                with self.subTest(doc=o.get("DOCUMENT_ID"), run=o.get("RUN_ID")):
                    anteriores = vistas.get(chave, [])
                    self.assertTrue(anteriores, "SEEN_AGAIN sem observacao anterior do mesmo documento")
                    shas = {a.get("RAW_SHA256") for a in anteriores}
                    self.assertIn(o.get("RAW_SHA256"), shas,
                                  "reobservacao com bytes que nenhuma anterior tinha: isso e NEW_DOCUMENT ou CHANGED_IN_PLACE")
                    if o.get("RAW_PATH"):
                        nomes = {os.path.basename(a["RAW_PATH"]) for a in anteriores
                                 if a.get("RAW_PATH") and a.get("RAW_SHA256") == o.get("RAW_SHA256")}
                        if nomes:
                            self.assertIn(os.path.basename(o["RAW_PATH"]), nomes,
                                          "reobservacao aponta para um ficheiro com outro nome")
            if o.get("DOCUMENT_ID") and o.get("RAW_SHA256"):
                vistas.setdefault(chave, []).append(o)

    def test_um_objecto_guardado_por_impressao_digital(self):
        """Os objectos guardados e as impressões digitais batem — POR CORRIDA.

        ⚠️ ISTO DIZIA «criados == shas distintos» sobre o livro inteiro. Era
        verdade enquanto cada sha so tinha sido materializado uma vez. Desde
        20/09/2026 o mesmo sha pode ser criado em duas corridas (arvore nova
        sem os bytes no disco — ver o teste anterior) e dois documentos de
        fontes diferentes podem ter bytes iguais. O invariante que autoriza
        «um objecto guardado = um raw_asset»: DENTRO de uma corrida, cada
        (fonte, sha) e criado no maximo uma vez, e todo objecto criado tem
        sha e caminho.
        """
        por_corrida = collections.defaultdict(list)
        for o in self.obs:
            if o.get("RAW_OBJECT_CREATED") is True:
                self.assertTrue(o.get("RAW_SHA256"), "objecto criado sem sha256")
                self.assertTrue(o.get("RAW_PATH"), "objecto criado sem caminho")
                por_corrida[o.get("RUN_ID")].append((o.get("SOURCE_ID"), str(o.get("RAW_SHA256")).lower()))
        self.assertTrue(por_corrida, "nenhum objecto criado no livro: o teste cegou")
        for run, chaves in por_corrida.items():
            with self.subTest(run=run):
                self.assertEqual(len(chaves), len(set(chaves)),
                                 "a mesma (fonte, sha) criada duas vezes na mesma corrida")


# ═════════════════════════════════════════════════════════════════════════════
class UmRawAssetUmReady(unittest.TestCase):
    """⚠️ ESTE É O TESTE QUE REPROVA EM `2dde8fed`.

    A prova emitia um READY por OBSERVAÇÃO admitida. Duas observações do mesmo
    bruto — uma que o guardou, outra que só confirmou — davam dois READY
    byte-a-byte iguais, ambos com `RAW_OBSERVATION_ID = NAO SEI`.
    """

    @classmethod
    def setUpClass(cls):
        cls.resumo = prova.correr()
        cls.ready = cls.resumo["READY"]
        cls.recibos = cls.resumo["RECIBOS"]

    def test_nenhum_ready_nasce_de_observacao_sem_bruto_guardado(self):
        """A pergunta canónica: de que `raw_asset` é este READY?

        Um READY vindo de observação com `RAW_OBJECT_CREATED = False` não sabe
        responder — e não é por lhe faltar o id, é por não haver bruto seu.
        """
        por_item = collections.defaultdict(list)
        for r in self.recibos:
            if r.get("ADMISSAO", {}).get("RESULTADO") == "SIM":
                por_item[r.get("DOCUMENT_ID")].append(r)
        for doc, rs in por_item.items():
            guardaram = [r for r in rs if r.get("RAW_OBJECT_CREATED") is True]
            with self.subTest(documento=doc):
                self.assertLessEqual(
                    len(guardaram), 1,
                    "dois objectos guardados para o mesmo documento")

    def test_um_ready_por_bruto_guardado_e_admitido(self):
        """A contagem sai da LEI, e não é um número escrito à mão.

        O esperado é derivado do próprio livro: quantos brutos guardados
        passaram a porta. Se amanhã a coleta guardar mais um, o esperado sobe
        sozinho — um número cravado aqui envelheceria em silêncio.
        """
        admitidos_com_bruto = {
            r.get("DOCUMENT_ID") for r in self.recibos
            if r.get("ADMISSAO", {}).get("RESULTADO") == "SIM"
            and r.get("RAW_OBJECT_CREATED") is True}
        self.assertEqual(len(admitidos_com_bruto), len(self.ready))

    def test_nenhum_par_de_ready_e_identico(self):
        """Dois READY iguais byte-a-byte são um bruto contado duas vezes."""
        vistos = collections.Counter(
            json.dumps(r, sort_keys=True, ensure_ascii=False)
            for r in self.ready)
        repetidos = [n for n, c in vistos.items() if c > 1]
        self.assertEqual([], repetidos, "READY duplicado byte-a-byte")

    def test_a_historia_das_duas_observacoes_sobrevive(self):
        """⚠️ O QUE NÃO PODE ACONTECER: a `SEEN_AGAIN` desaparecer.

        Ela é um facto — alguém foi lá e o documento continuava igual. O recibo
        dela fica, com a decisão da admissão que teve. Deixar de contar um
        bruto duas vezes não é apagar a segunda ida.
        """
        docs_no_livro = {o.get("DOCUMENT_ID") for o in _livro()
                         if o.get("OBSERVATION_RESULT") == "SEEN_AGAIN"}
        docs_nos_recibos = {r.get("DOCUMENT_ID") for r in self.recibos}
        for doc in docs_no_livro & docs_nos_recibos:
            with self.subTest(documento=doc):
                seen = [r for r in self.recibos
                        if r.get("DOCUMENT_ID") == doc
                        and r.get("RAW_OBJECT_CREATED") is False]
                self.assertTrue(
                    seen, "a re-observacao sumiu dos recibos: isso e apagar "
                          "historia, nao deduplicar linhagem")

    def test_a_contagem_de_observacoes_no_livro_nao_muda(self):
        """A prova só lê. O livro tem as observações todas, antes e depois."""
        self.assertEqual(175, len(_livro()))
        self.assertEqual(
            "YES — nada foi colhido, nenhuma observacao nova foi criada",
            self.resumo["SO_LEITURA"])


# ═════════════════════════════════════════════════════════════════════════════
class NenhumaIdentidadeNovaFoiInventada(unittest.TestCase):
    """A lei proíbe derivar `RAW_OBSERVATION_ID` de outra coisa qualquer."""

    @staticmethod
    def _codigo_sem_prosa(rel):
        """O que EXECUTA, sem comentário e sem docstring. → str.

        ⚠️ ESTE AUXILIAR NASCEU DE UM ERRO MEU, NA PRIMEIRA ESCRITA DESTE
        FICHEIRO. A versão anterior fazia `assertNotIn("RAW_OBSERVATION_ID =",
        fonte)` sobre o texto inteiro — e reprovava por causa da DOCSTRING que
        cita a lei: «a linhagem canónica continua a ser `RAW_OBSERVATION_ID =
        raw_asset.id`». O teste apanhou a frase que promete a regra, em vez do
        código que a cumpre.

            PROCURAR A PALAVRA NO FICHEIRO MEDE O QUE ESTÁ ESCRITO.
            A PERGUNTA ERA SOBRE O QUE EXECUTA.
        """
        import ast
        arvore = ast.parse(io.open(os.path.join(RAIZ, rel),
                                   encoding="utf-8").read())
        for no in ast.walk(arvore):
            if (isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant)
                    and isinstance(no.value.value, str)):
                no.value.value = ""
        return ast.unparse(arvore)

    def test_a_prova_nao_fabrica_raw_observation_id(self):
        """Quem escreve a linhagem é `admissao.pronto_para_inteligencia`.

        Ele lê `item["raw_asset_id"]` e, na ausência, escreve `NAO SEI`. Esta
        prova não pode ter opinião sobre isso.
        """
        codigo = self._codigo_sem_prosa("provas/a_collection_preserva_o_fato.py")
        for proibido in ("RAW_OBSERVATION_ID", "raw_observation_id",
                         "raw_asset_id"):
            self.assertNotIn(proibido, codigo,
                             "a prova esta a escrever a linhagem a mao")

    def test_nenhum_campo_de_identidade_paralela_nasceu(self):
        fonte = io.open(os.path.join(RAIZ, "provas",
                                     "a_collection_preserva_o_fato.py"),
                        encoding="utf-8").read()
        for inventado in ("document_identity", "canonical_document_id",
                          "dedupe_id", "ready_identity"):
            self.assertNotIn(inventado, fonte)

    def test_o_ready_continua_a_dizer_NAO_SEI_quando_nao_sabe(self):
        """Sem Postgres não há `raw_asset.id`, e a lei manda escrever `NAO SEI`.

        ⚠️ ISTO NÃO É O DEFEITO. É A LEI A SER CUMPRIDA. O defeito era emitir
        DOIS `NAO SEI` para o mesmo bruto.
        """
        resumo = prova.correr()
        for r in resumo["READY"]:
            self.assertEqual("NAO SEI", r["RAW_OBSERVATION_ID"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
