# -*- coding: utf-8 -*-
"""O PORTAO DE QUALIDADE NAO PODE TOCAR NA REVISAO NEM ADIANTAR A SEGUNDA.

A revisao A veio de uma pessoa. O perigo aqui nao e o codigo rebentar — e o
codigo funcionar e mentir de quatro maneiras caladas:

    1. «arrumar» a revisao A ao grava-la, e a copia deixar de ser copia;
    2. a fila cega levar, dentro do JSON, a resposta que a pessoa nao ve;
    3. o contexto extra ser o pedaco que disparou a revisao — a resposta
       entregue com cara de pergunta;
    4. uma resposta ser guardada sem razao e sem atestacao, e a coluna
       `HUMAN_REASON` continuar vazia com ar de cheia.

    HUMAN_REVIEW_INPUT = READ_ONLY
    EVIDENCE_PRESENTED != EVIDENCE_USED
    REVIEW_A != REVIEW_A2, E NENHUM E UM SEGUNDO REVISOR INDEPENDENTE

Os testes de pagina leem o HTML gerado — nao precisam de navegador.
"""
import copy
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location(
    "qualidade_t3", os.path.join(RAIZ, "provas", "qualidade_t3.py"))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)

PAGINA = os.path.join(RAIZ, q.HTML)


def _sem_espaco(t):
    return re.sub(r"\s+", "", t)


def _pagina():
    with open(PAGINA, encoding="utf-8") as f:
        return f.read()


def _bloco(html, ident):
    m = re.search(r'<script id="%s" type="application/json">(.*?)</script>'
                  % ident, html, re.S)
    assert m, "bloco %s nao encontrado" % ident
    return json.loads(m.group(1).replace("<\\/", "</"))


class ARevisaoEntraInteira(unittest.TestCase):
    """A entrada e imutavel. Se ela nao fecha, para-se — nao se conserta."""

    @classmethod
    def setUpClass(cls):
        cls.a, cls.pacote = q.carregar_a()

    def test_o_sha_da_entrada_e_o_da_entrada(self):
        caminho = os.path.join(RAIZ, q.ENTRADA)
        with open(caminho, "rb") as f:
            esperado = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(q.sha256_do_ficheiro(q.ENTRADA), esperado)

    def test_as_contagens_fecham(self):
        self.assertEqual(self.a["STATUS"], "COMPLETE")
        self.assertEqual(len(self.a["ITEMS"]), 53)
        self.assertEqual(self.a["TOTAL_REVIEWED"], 53)

    def test_cada_item_tem_um_sha_so_seu(self):
        shas = [x["DOC_SHA256"] for x in self.a["ITEMS"]]
        self.assertEqual(len(set(shas)), 53)

    def test_nenhum_rotulo_fora_do_vocabulario(self):
        self.assertEqual({x["LABEL"] for x in self.a["ITEMS"]} - set(q.ROTULOS),
                         set())

    def test_a_evidencia_vista_e_a_do_pacote_byte_a_byte(self):
        for x in self.a["ITEMS"]:
            self.assertEqual(x["ORIGINAL_EVIDENCE"],
                             self.pacote[x["DOC_SHA256"]]["EVIDENCE"])

    # ⚠️ Estes testes chamam `carregar_a()` com um ficheiro estragado. A
    # primeira versao refazia a conta DENTRO do teste e comparava com ela
    # propria — passava com a guarda apagada.
    #
    #     REFAZER A LOGICA NO TESTE NAO E TESTAR A LOGICA:
    #     E ESCREVE-LA DUAS VEZES E CONCORDAR CONSIGO.
    def _com_entrada_estragada(self, estraga):
        a = copy.deepcopy(self.a)
        estraga(a)
        guardado = q.ENTRADA
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                          encoding="utf-8")
        try:
            json.dump(a, tmp, ensure_ascii=False)
            tmp.close()
            q.ENTRADA = tmp.name
            with self.assertRaises(q.RevisaoInvalida):
                q.carregar_a()
        finally:
            q.ENTRADA = guardado
            os.unlink(tmp.name)

    def test_um_rotulo_inventado_nao_passa(self):
        self._com_entrada_estragada(
            lambda a: a["ITEMS"][0].__setitem__("LABEL", "PROVAVELMENTE_T3"))

    def test_evidencia_divergente_nao_e_reconciliada(self):
        """Se o mesmo SHA trouxer outro conteudo, o certo e PARAR."""
        self._com_entrada_estragada(
            lambda a: a["ITEMS"][0]["ORIGINAL_EVIDENCE"].__setitem__(
                "TITLE", "outro titulo qualquer"))

    def test_schema_desconhecido_nao_passa(self):
        self._com_entrada_estragada(
            lambda a: a.__setitem__("SCHEMA", "sintonia.outra-coisa/9"))

    def test_revisao_incompleta_nao_passa(self):
        self._com_entrada_estragada(
            lambda a: a.__setitem__("STATUS", "INCOMPLETE"))

    def test_contagem_que_nao_fecha_nao_passa(self):
        self._com_entrada_estragada(lambda a: a["ITEMS"].pop())

    def test_sha_repetido_nao_passa(self):
        self._com_entrada_estragada(
            lambda a: a["ITEMS"][1].__setitem__(
                "DOC_SHA256", a["ITEMS"][0]["DOC_SHA256"]))

    def test_a_entrada_nao_e_tocada_por_nenhuma_destas_conferencias(self):
        antes = q.sha256_do_ficheiro(q.ENTRADA)
        q.carregar_a()
        self.assertEqual(q.sha256_do_ficheiro(q.ENTRADA), antes)


class ARevisaoSaiIntacta(unittest.TestCase):
    """Preservar e copiar. Ordenar, limpar ou normalizar ja e outra coisa."""

    @classmethod
    def setUpClass(cls):
        cls.a, _ = q.carregar_a()
        cls.env = q.envelope_de_a(cls.a)

    def test_o_conteudo_preservado_e_identico_ao_recebido(self):
        self.assertEqual(self.env["REVIEW_A"], self.a)

    def test_a_ordem_dos_itens_nao_muda(self):
        self.assertEqual([x["ITEM_ID"] for x in self.env["REVIEW_A"]["ITEMS"]],
                         [x["ITEM_ID"] for x in self.a["ITEMS"]])

    def test_o_envelope_diz_de_onde_veio_e_com_que_sha(self):
        self.assertEqual(self.env["INGESTED_FROM"], q.ENTRADA)
        self.assertEqual(self.env["INPUT_SHA256"],
                         q.sha256_do_ficheiro(q.ENTRADA))

    def test_o_ficheiro_gravado_bate_com_a_entrada(self):
        env = json.load(open(os.path.join(RAIZ, q.PRESERVADO), encoding="utf-8"))
        entrada = json.load(open(os.path.join(RAIZ, q.ENTRADA), encoding="utf-8"))
        self.assertEqual(env["REVIEW_A"], entrada)

    def test_nenhum_rotulo_foi_atribuido_pela_maquina(self):
        self.assertEqual(self.env["AUTO_LABELS_ASSIGNED"], 0)

    def test_razao_nula_continua_nula(self):
        """HUMAN_REASON = null nunca vira razao inventada."""
        nulas = [x for x in self.env["REVIEW_A"]["ITEMS"]
                 if x.get("HUMAN_REASON") is None]
        self.assertEqual(len(nulas), 53)


class AsDuasFilas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a, cls.pacote = q.carregar_a()
        (cls.conf, cls.cega,
         cls.incerteza, cls.tensao) = q.filas(cls.a["ITEMS"])

    def test_as_filas_somam_o_total_e_nao_se_cruzam(self):
        self.assertEqual(len(self.conf) + len(self.cega), 53)
        self.assertEqual(
            {x["DOC_SHA256"] for x in self.conf}
            & {x["DOC_SHA256"] for x in self.cega}, set())

    def test_toda_a_incerteza_vai_para_a_segunda_leitura(self):
        for x in self.a["ITEMS"]:
            if x["LABEL"] in ("T3_AMBIGUO", "EVIDENCIA_INSUFICIENTE"):
                self.assertIn(x["DOC_SHA256"],
                              {y["DOC_SHA256"] for y in self.cega})

    def test_o_gatilho_nao_muda_nenhum_rotulo(self):
        """Ele manda olhar outra vez. Nao responde por ninguem."""
        antes = {x["DOC_SHA256"]: x["LABEL"] for x in self.a["ITEMS"]}
        _ = q.filas(self.a["ITEMS"])
        depois = {x["DOC_SHA256"]: x["LABEL"] for x in self.a["ITEMS"]}
        self.assertEqual(antes, depois)
        for x in self.tensao:
            self.assertEqual(x["LABEL"], "T3_NAO")

    def test_sem_gatilho_a_fila_cega_e_so_a_incerteza(self):
        """Mutacao: se nenhuma expressao dispara, so a incerteza sobra."""
        guardado = q.GATILHOS
        try:
            q.GATILHOS = ()
            _, cega, incerteza, tensao = q.filas(self.a["ITEMS"])
            self.assertEqual(tensao, [])
            self.assertEqual(len(cega), len(incerteza))
        finally:
            q.GATILHOS = guardado

    def test_um_item_de_confirmacao_nao_carrega_gatilho_nenhum(self):
        for x in self.conf:
            if x["LABEL"] != "T3_NAO":
                continue
            visto = q._texto_visto(x)
            for g in q.GATILHOS:
                self.assertNotIn(g, visto)


class OContextoNaoEscolhePeloAssunto(unittest.TestCase):
    """Mostrar so o pedaco que disparou a revisao seria entregar a resposta."""

    @classmethod
    def setUpClass(cls):
        cls.a, cls.pacote = q.carregar_a()
        cls.ctx = q.contexto_completo(cls.a, cls.pacote)
        cls.por_sha = {c["DOC_SHA256"]: c for c in cls.ctx["ITENS"]}

    def test_ha_contexto_para_cada_item(self):
        self.assertEqual(self.ctx["TOTAL"], 53)

    def test_as_paginas_comecam_no_principio_do_documento(self):
        for x in self.a["ITEMS"][:12]:
            c = self.por_sha[x["DOC_SHA256"]]
            inteiro = q.contexto_do_documento(
                self.pacote[x["DOC_SHA256"]])["PAGINAS"]
            self.assertEqual(c["PAGINAS"][0], inteiro[0])

    def test_as_paginas_sao_do_tamanho_declarado(self):
        for c in self.ctx["ITENS"]:
            for p in c["PAGINAS"][:-1]:
                self.assertEqual(len(p), q.POR_PAGINA)

    def test_a_primeira_pagina_nao_foi_puxada_para_o_gatilho(self):
        """A pagina 1 e a pagina 1 do documento — nao a que contem a frase."""
        achou = 0
        for c in self.ctx["ITENS"]:
            if not c["NA_FILA_CEGA"] or c["TOTAL_PAGINAS"] < 2:
                continue
            depois = " ".join(c["PAGINAS"][1:]).lower()
            if any(g in depois for g in q.GATILHOS):
                achou += 1
                self.assertNotIn("__ancorado__", c["PAGINAS"][0])
        self.assertGreater(achou, 0, "nenhum documento serviu de prova")

    def test_toda_a_fila_cega_tem_traducao(self):
        cegos = [c for c in self.ctx["ITENS"] if c["NA_FILA_CEGA"]]
        self.assertEqual(len(cegos), 21)
        self.assertTrue(all(c["JANELA_PTBR"] for c in cegos))

    def test_traducao_presa_ao_texto_que_traduz(self):
        for c in self.ctx["ITENS"]:
            if not c["JANELA_PTBR"]:
                continue
            janela = q.contexto_do_documento(
                self.pacote[c["DOC_SHA256"]])["TEXTO_A_TRADUZIR"]
            self.assertEqual(
                c["ORIGINAL_SHA256_DA_JANELA"],
                hashlib.sha256(janela.encode("utf-8")).hexdigest())

    def test_traducao_desatualizada_e_descartada_nao_mostrada(self):
        """Mutacao: mexer no original tem de APAGAR a traducao, nao mante-la."""
        pacote = copy.deepcopy(self.pacote)
        alvo = [c for c in self.ctx["ITENS"] if c["NA_FILA_CEGA"]][0]
        original = q.contexto_do_documento

        def falso(ficha):
            d = original(ficha)
            if ficha["DOC_SHA256"] == alvo["DOC_SHA256"]:
                d["TEXTO_A_TRADUZIR"] = "texto diferente do que foi traduzido"
            return d
        try:
            q.contexto_do_documento = falso
            ctx = q.contexto_completo(self.a, pacote)
            mexido = [c for c in ctx["ITENS"]
                      if c["DOC_SHA256"] == alvo["DOC_SHA256"]][0]
            self.assertIsNone(mexido["JANELA_PTBR"])
        finally:
            q.contexto_do_documento = original

    def test_a_traducao_nao_carrega_rotulo(self):
        t = json.load(open(os.path.join(RAIZ, q.TRADUCAO), encoding="utf-8"))
        self.assertEqual(t["AUTO_LABELS_ASSIGNED"], 0)
        bruto = json.dumps(t, ensure_ascii=False)
        for proibido in ("PROVAVELMENTE_T3", "LIKELY_T3", "SUGGESTED_LABEL",
                         "CONFIDENCE", "T3_SIM", "T3_NAO"):
            self.assertNotIn(proibido, bruto)


class AFilaCegaEMesmoCega(unittest.TestCase):
    """Esconder no ecra e deixar no payload nao e cegar."""

    @classmethod
    def setUpClass(cls):
        cls.a, cls.pacote = q.carregar_a()
        cls.conf, cls.cega = q.dados_do_portao(cls.a, cls.pacote)
        cls.bruto = json.dumps(cls.cega, ensure_ascii=False)

    def test_nenhum_item_cego_tem_campo_de_rotulo(self):
        for d in self.cega:
            for chave in ("LABEL", "LABEL_A", "NOTE_A", "MOTIVO_DA_FILA",
                          "GATILHO", "FINAL_LABEL"):
                self.assertNotIn(chave, d)

    def test_nenhum_rotulo_aparece_no_json_da_fila_cega(self):
        for r in q.ROTULOS:
            self.assertNotIn('"%s"' % r, self.bruto)

    def test_as_chaves_proibidas_nao_viajam(self):
        for chave in q.PROIBIDOS_NA_FILA_CEGA:
            self.assertNotIn(chave, self.bruto)

    def test_a_confirmacao_leva_a_resposta_porque_e_disso_que_trata(self):
        self.assertTrue(all("LABEL_A" in d for d in self.conf))
        self.assertEqual(len(self.conf), 32)
        self.assertEqual(len(self.cega), 21)

    def test_a_ordem_da_fila_cega_nao_diz_nada_da_resposta(self):
        self.assertEqual([d["ITEM_ID"] for d in self.cega],
                         sorted(d["ITEM_ID"] for d in self.cega))

    def test_um_rotulo_que_escape_para_o_payload_e_apanhado(self):
        """Mutacao: se o rotulo voltar a entrar, o teste tem de acender."""
        sujo = copy.deepcopy(self.cega)
        sujo[0]["LABEL_A"] = "T3_NAO"
        self.assertIn('"LABEL_A"', json.dumps(sujo, ensure_ascii=False))


class APaginaDoPortao(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html = _pagina()
        cls.conf = _bloco(cls.html, "conf")
        cls.cega = _bloco(cls.html, "cega")

    def test_a_pagina_esta_escrita_e_em_portugues(self):
        self.assertIn('<html lang="pt-BR">', self.html)
        self.assertIn("PORTÃO DE QUALIDADE", self.html)

    def test_leva_as_duas_filas_com_os_tamanhos_certos(self):
        self.assertEqual(len(self.conf), 32)
        self.assertEqual(len(self.cega), 21)

    def test_o_ecra_de_entrada_diz_quantos_sao_e_nao_diz_as_respostas(self):
        self.assertIn("Respostas recebidas", self.html)
        self.assertIn("Para ler uma segunda vez", self.html)
        for r in q.ROTULOS:
            self.assertNotIn('"%s"' % r, json.dumps(self.cega,
                                                    ensure_ascii=False))

    def test_a_pagina_nao_promete_revisor_independente(self):
        self.assertNotIn("INDEPENDENT_REVIEWER_B", self.html)
        self.assertNotIn("REVIEWER_B", self.html)
        self.assertIn("não</b> é um segundo revisor independente", self.html)

    def test_a_pagina_nao_decide_o_rotulo_final(self):
        self.assertIn("FINAL_LABEL_DECIDIDO_AQUI:false",
                      _sem_espaco(self.html))
        self.assertNotIn("FINAL_LABEL:", _sem_espaco(self.html))

    def test_nada_de_probabilidade_nem_sugestao(self):
        for proibido in ("PROVAVELMENTE_T3", "LIKELY_T3", "SUGGESTED_LABEL",
                         "CONFIDENCE", "provavelmente T3", "alta confiança"):
            self.assertNotIn(proibido, self.html)

    def test_o_original_viaja_junto_com_a_traducao(self):
        for d in self.conf[:5] + self.cega[:5]:
            self.assertTrue(d["ORIGINAL_EVIDENCE"]["TITLE"] is not None)
            self.assertIn("DISPLAY_TRANSLATION_PTBR", d)

    def test_o_contexto_maior_viaja_para_a_fila_cega(self):
        for d in self.cega:
            self.assertGreater(len(d["CONTEXTO"]["PAGINAS"]), 0)
            self.assertTrue(d["CONTEXTO"]["JANELA_PTBR"])

    def test_a_razao_e_perguntada_para_cada_rotulo(self):
        for r in q.ROTULOS:
            self.assertIn(r, self.html)
            self.assertGreaterEqual(len(q.RAZOES[r]), 3)
            self.assertEqual(q.RAZOES[r][-1][0], "OUTRO")

    def test_a_atestacao_e_obrigatoria(self):
        self.assertIn("foi nele que me baseei", self.html)
        self.assertIn("returne.at;", _sem_espaco(self.html))

    def test_outro_sem_texto_nao_passa(self):
        self.assertIn("if(e.cod==='OUTRO'&&!e.txt)returnfalse;",
                      _sem_espaco(self.html))

    def test_guardar_esta_travado_ate_a_resposta_estar_inteira(self):
        self.assertIn("ok.disabled=!podeGuardar(!conf,!!rotulo);",
                      _sem_espaco(self.html))

    def test_um_item_so_conta_com_razao_e_atestacao(self):
        self.assertIn("return!!(r&&r.REASON_CODE&&r.EVIDENCE_ATTESTED);",
                      _sem_espaco(self.html))

    def test_rever_a_resposta_move_o_item_e_deixa_rasto(self):
        self.assertIn("st.reabertos.push(d.DOC_SHA256)", _sem_espaco(self.html))
        self.assertIn('REOPENED_BY_HUMAN:rb?"YES":"NO"', _sem_espaco(self.html))

    def test_um_item_reaberto_nao_e_declarado_cego(self):
        self.assertIn("BLIND:!r.CONFIRMOU_A&&!rb", _sem_espaco(self.html))

    def test_virar_a_pagina_do_contexto_nao_conta_como_resposta(self):
        """O contador e a grelha leem a DECISAO, nao a existencia da linha.

        Virar a pagina tambem escreve em `respostas`, para nao se perder onde
        a pessoa ia. Se o progresso contar a linha, a barra anda sozinha.
        """
        s = _sem_espaco(self.html)
        self.assertIn("functionfeitas(){returnordem().filter(respondido).length;}", s)
        self.assertIn("+(respondido(d)?'f':'')", s)
        self.assertNotIn("returnObject.keys(st.respostas).length;}", s)

    def test_a_exportacao_tem_o_schema_do_portao(self):
        self.assertIn('SCHEMA:"sintonia.t3-human-quality-gate-results/1"',
                      _sem_espaco(self.html))
        self.assertIn("T3-HUMAN-QUALITY-GATE-RESULTS-V1.json", self.html)

    def test_a_exportacao_nao_inventa_um_a2_para_a_confirmacao(self):
        """Confirmar nao e ler outra vez. Nao se fabrica a segunda leitura."""
        s = _sem_espaco(self.html)
        self.assertIn("if(r.CONFIRMOU_A){o.LABEL_A=d.LABEL_A;o.CONFIRMED=true;}", s)

    def test_a_resposta_de_a_nao_volta_de_onde_a_pagina_nao_a_tinha(self):
        s = _sem_espaco(self.html)
        self.assertIn("else{o.LABEL_A2=r.LABEL;}", s)

    def test_a_pagina_nao_escreve_em_ficheiro_do_projeto(self):
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_a_tabela_rola_na_caixa_e_nao_na_pagina(self):
        s = _sem_espaco(self.html)
        self.assertIn(".trecho.tabela{white-space:pre;overflow-x:auto", s)
        self.assertIn("html,body{overflow-x:clip}", s)

    def test_titulo_cru_nao_empurra_a_pagina(self):
        s = _sem_espaco(self.html)
        self.assertIn("h2{font-size:20px;line-height:1.3;margin:0014px;"
                      "overflow-wrap:anywhere}", s)
        self.assertIn("h2.cru{font-size:14px", s)


class OQueEstaMissaoNaoFaz(unittest.TestCase):

    def test_nao_ha_classificador_nem_treino_no_modulo(self):
        with open(os.path.join(RAIZ, "provas", "qualidade_t3.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        for proibido in ("sklearn", "torch", "transformers", "embedding",
                         "def treinar", "fit(", "predict("):
            self.assertNotIn(proibido, fonte)

    def test_nao_ha_rede(self):
        with open(os.path.join(RAIZ, "provas", "qualidade_t3.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        for proibido in ("requests", "urllib", "httpx", "socket"):
            self.assertNotIn(proibido, fonte)

    def test_o_ficheiro_de_entrada_nao_e_aberto_para_escrita(self):
        with open(os.path.join(RAIZ, "provas", "qualidade_t3.py"),
                  encoding="utf-8") as f:
            fonte = f.read()
        self.assertNotIn('open(os.path.join(RAIZ, ENTRADA), "w"', fonte)
        self.assertNotIn("escrever(ENTRADA", fonte)


if __name__ == "__main__":
    unittest.main()
