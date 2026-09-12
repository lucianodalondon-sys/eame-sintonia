# -*- coding: utf-8 -*-
"""B1 — A ITALIA ENTRA PELA PORTA CANONICA, E O BANCO VE-A ENTRAR.

O QUE ESTE FICHEIRO PROVA
-------------------------
Antes desta missao a Italia colhia e nao entrava. O livro tinha 144
observacoes, o armazem tinha os PDFs, e `raw_asset` tinha ZERO linhas
italianas: entre o coletor e a porta nao havia peca nenhuma.

    T-04 orquestrador  ->  T-06 registo  ->  coleta/italy_executor.py
      ->  coleta/italy_pilot_collect.mjs  ->  colheita SO desta corrida
      ->  coleta/ingresso.py  ->  guarda/preservar_coleta.py
      ->  collection_run + raw_asset

SEM REDE, SEM CUSTO, E COM UM BANCO QUE MORRE NO FIM
----------------------------------------------------
Nao ha uma unica chamada de rede aqui. Os bytes sao INJECTADOS por `forcarBuf`,
que e o mecanismo que o proprio coletor ja declara para correr sem ir a fonte —
e nao um modo seco inventado para o teste passar. O `--dry` que o cabecalho do
coletor prometia **nunca existiu**, e foi apagado em vez de fingido.

O banco e `MemoriaDescartavel`, SQLite em memoria, que nasce e morre em cada
caso. O livro e o armazem do coletor vao para uma raiz temporaria via
`ITALY_OPS_ROOT` — as 144 observacoes reais nao sao tocadas.

⚠️ O QUE ESTE FICHEIRO **NAO** PROVA, E FICA DITO
-------------------------------------------------
Um unico salto do caminho nao e exercido com bytes reais: o `subprocess.run`
que corre `node` dentro de `italy_executor.correr_coletor`. Correr o coletor
de verdade sem rede so daria observacoes de falha, e correr o coletor COM rede
esta proibido nesta prova. Esse salto e provado ao nivel do COMANDO — que o
T-04 monta, com o `RUN_ID` la dentro, antes de chamar seja quem for.

    PROVADO COM BYTES   as quatro traducoes do adapter, a porta, o dono do RAW
    PROVADO SO O COMANDO  a chamada do Node
"""
import ast
import io
import json
import os
import shutil
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import ingresso as ing                     # noqa: E402
import italy_executor as adapter           # noqa: E402
import orquestrador as orq                 # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402
from pedido import de_uma_frase            # noqa: E402
from receitas import EXECUTORES            # noqa: E402

FONTE = "IT-T2-002"
BALCAO = os.path.join(RAIZ, "data", "colheita", "italia")

# ── OS BYTES QUE NUNCA VAO A REDE ──────────────────────────────────────────
# Um PDF com o que a IDENTIDADE da fonte precisa de ler: a assinatura `%PDF` e
# a `/CreationDate`, que e de onde sai `ARPAV:Z{NN}:{AAAAMMDDHHMMSS}`. Nada
# mais e inventado — o que o coletor nao conseguir ler destes bytes, ele dira
# que nao sabe.
def _driver(run_id: str, marca: str) -> str:
    """O Node que corre o coletor COM OS BYTES NA MAO.

    Ele nao substitui o coletor nem o imita: importa-o e chama a mesma
    `executarRodada` que a rota canonica chama, com o mesmo `runId`. A unica
    diferenca e `forcarBuf`, que e onde os bytes entram sem haver rede.
    """
    return """
import { executarRodada } from "%s/coleta/italy_pilot_collect.mjs";
// UMA ZONA, UM DOCUMENTO, BYTES PROPRIOS. As quatro zonas do piloto sao quatro
// boletins diferentes; dar-lhes os mesmos bytes faria o armazem guardar UM
// objecto e o teste aplaudir um resultado que a realidade nao produz.
const bytesDaZona = (_fonte, alvo) => Buffer.concat([
  Buffer.from("%%PDF-1.4\\n/CreationDate (D:%s+02'00')\\n", "latin1"),
  Buffer.alloc(4096, "%s"),
  Buffer.from(`\\n%% zona ${alvo.zone}\\n%%%%EOF\\n`, "latin1")]);
const r = await executarRodada({
  runId: "%s", apenas: ["%s"], forcarBuf: bytesDaZona, nota: "prova b1" });
console.log(JSON.stringify(r.resumo));
""" % (RAIZ.replace("\\", "/"), marca[1], marca[0], run_id, FONTE)


class CasoB1(unittest.TestCase):
    """Cada caso tem a sua raiz temporaria, o seu banco e o seu balcao."""

    def setUp(self):
        import tempfile
        # A raiz temporaria vive DENTRO do repositorio de proposito: o caminho
        # que o coletor escreve tem de ser relativo a mesma arvore que a porta
        # le, senao os bytes existem e ninguem lhes chega.
        self.ops = tempfile.mkdtemp(prefix=".prova-b1-", dir=os.path.join(RAIZ, "data"))
        self.addCleanup(shutil.rmtree, self.ops, True)
        os.environ["ITALY_OPS_ROOT"] = self.ops
        self.addCleanup(os.environ.pop, "ITALY_OPS_ROOT", None)
        self.addCleanup(shutil.rmtree, BALCAO, True)
        # ⚠️ O ARMAZEM LOCAL ESCREVE MESMO. `pela_entrada` cria um
        # `ing.ArmazemLocal(RAIZ)`, e o dono do RAW enderecа por
        # `PAIS/FONTE/TIPO/...`. A observacao italiana nao declara pais — o
        # adapter nao o inventa — e por isso ela cai em `XX/`. Deixar isso na
        # arvore faria o censo do corpus contar bytes de teste como acervo, e
        # foi exactamente o que aconteceu na primeira execucao desta prova.
        for pasta in ("XX",):
            if not os.path.exists(os.path.join(RAIZ, pasta)):
                self.addCleanup(shutil.rmtree, os.path.join(RAIZ, pasta), True)
        self.banco = MemoriaDescartavel()
        self.addCleanup(self.banco.fechar)
        self.rede = 0

    # ── as duas metades do caminho ─────────────────────────────────────────
    def coletar(self, run_id, marca=("a", "20260903160930")):
        r = subprocess.run(["node", "--input-type=module", "-e", _driver(run_id, marca)],
                           cwd=RAIZ, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.strip().splitlines()[-1])

    def livro(self):
        p = os.path.join(self.ops, adapter.LIVRO)
        if not os.path.isfile(p):
            return []
        return [json.loads(l) for l in io.open(p, encoding="utf-8") if l.strip()]

    def pela_rota(self, run_id):
        """Adapter -> colheita -> a_colheita do T-04 -> porta -> dono do RAW."""
        resumo = adapter.colher(run_id, ops_root=self.ops)
        e = EXECUTORES["T2"][0]
        itens, notas = orq.a_colheita(e)
        recibo = {"RUN_ID": run_id, "PLATFORM": "HTTP direto",
                  "ACTOR": "coleta/italy_executor.py", "ACTOR_VERSION": "adapter-v1",
                  "SOURCE_COUNTRY": "IT", "STARTED_AT": "2026-09-10T00:00:00Z"}
        entrada = orq.pela_entrada(itens, recibo, memoria=self.banco)
        return resumo, itens, notas, entrada


class OCaminhoEstaLigado(CasoB1):
    """1..6 · o T-04 sabe chamar a Italia, e o RUN_ID nasce antes de tudo."""

    def test_1_o_registo_conhece_a_italia(self):
        ids = [x["id"] for x in EXECUTORES.get("T2", [])]
        self.assertIn("italia-recorrente", ids)

    def test_2_o_pedido_em_portugues_chega_ao_executor_italiano(self):
        p = de_uma_frase("colete clima da italia")
        self.assertEqual(p.alvo, "T2")
        recibo = orq.correr(p, seco=True)
        self.assertEqual(recibo["ACTOR"], "coleta/italy_executor.py")

    def test_3_o_comando_leva_a_fonte_declarada_e_o_run_id(self):
        recibo = orq.correr(de_uma_frase("colete clima da italia"), seco=True)
        self.assertIn(FONTE, recibo["COMANDO"])
        self.assertIn("--run-id=%s" % recibo["RUN_ID"], recibo["COMANDO"])

    def test_4_o_run_id_e_cunhado_ANTES_de_o_executor_correr(self):
        """Prova de ORDEM, no proprio codigo — nao de resultado.

        Um `RUN_ID` cunhado depois do `subprocess.run` continuaria a parecer
        certo em qualquer recibo. O que estava errado era a ORDEM, e e a ordem
        que se mede.
        """
        fonte = io.open(os.path.join(RAIZ, "orquestrador", "orquestrador.py"),
                        encoding="utf-8").read()
        arvore = ast.parse(fonte)
        corpo = next(n for n in ast.walk(arvore)
                     if isinstance(n, ast.FunctionDef) and n.name == "correr")
        mint = [n.lineno for n in ast.walk(corpo)
                if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "novo_run_id"]
        chamada = [n.lineno for n in ast.walk(corpo)
                   if isinstance(n, ast.Call)
                   and getattr(getattr(n.func, "value", None), "id", "") == "subprocess"]
        self.assertTrue(mint and chamada)
        self.assertLess(max(mint), min(chamada),
                        "o RUN_ID continua a nascer depois de o executor correr")

    def test_5_o_coletor_recusa_correr_sem_corrida(self):
        r = subprocess.run(["node", "coleta/italy_pilot_collect.mjs"],
                           cwd=RAIZ, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 2)
        self.assertIn("NAO cunha corrida", r.stderr)

    #: Quem PEDE a corrida, e desde quando. `recebe_run_id` e opt-in, e a lei
    #: que esta sentinela guarda e «ninguem passa a recebe-la sem a pedir».
    #:
    #: ⚠️ A LISTA CRESCEU NA SCRAP-FLOW-01, E CRESCER NAO E O MESMO QUE MUDAR.
    #: `scrap-colheita` nasce com o campo declarado, e nasce por causa dele: o
    #: adapter do SCRAP NAO pode cunhar corrida, ou a corrida do orquestrador e
    #: a da coleta eram duas. Um executor ANTIGO que ganhasse o campo em
    #: silencio e que era o defeito — e continua a ser reprovado.
    #:
    #:     UM EXECUTOR NOVO QUE PEDE A CORRIDA NAO E UM EXECUTOR ANTIGO
    #:     QUE PASSOU A RECEBE-LA.
    PEDEM_A_CORRIDA = ("italia-recorrente", "scrap-colheita")

    def test_6_nenhum_executor_antigo_mudou_de_linha_de_comando(self):
        for universo, lista in EXECUTORES.items():
            for e in lista:
                if e["id"] in self.PEDEM_A_CORRIDA:
                    continue
                self.assertNotIn("recebe_run_id", e,
                                 "%s/%s passou a receber corrida sem a pedir"
                                 % (universo, e["id"]))


class ACorridaEUmaSo(CasoB1):
    """7..9 · uma corrida, um RUN_ID, e so as observacoes dela."""

    def test_7_o_coletor_usa_a_corrida_que_recebeu(self):
        resumo = self.coletar("IT-T2-PROVA-0001")
        self.assertEqual(resumo["RUN_ID"], "IT-T2-PROVA-0001")
        self.assertTrue(all(o["RUN_ID"] == "IT-T2-PROVA-0001" for o in self.livro()))

    def test_8_a_colheita_traz_SO_esta_corrida_e_nao_o_livro_inteiro(self):
        self.coletar("IT-T2-PROVA-VELHA")
        self.coletar("IT-T2-PROVA-NOVA", marca=("b", "20260910101112"))
        livro = self.livro()
        self.assertEqual(len(livro), 8, "4 zonas x 2 corridas")
        resumo, itens, _, _ = self.pela_rota("IT-T2-PROVA-NOVA")
        self.assertEqual(resumo["OBSERVACOES_DESTA_CORRIDA"], 4)
        self.assertEqual(len(itens), 4)
        self.assertTrue(all(x["RUN_ID"] == "IT-T2-PROVA-NOVA" for x in itens))

    def test_9_o_balcao_e_JSON_e_nao_NDJSON(self):
        self.coletar("IT-T2-PROVA-0002")
        adapter.colher("IT-T2-PROVA-0002", ops_root=self.ops)
        d = json.loads(io.open(os.path.join(RAIZ, adapter.COLHEITA),
                               encoding="utf-8").read())
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 4)


class OsBytesQueEntramSaoOsDoDocumento(CasoB1):
    """10..12 · o que fica no armazem e o PDF, e nao o ficheiro de colheita."""

    def test_10_cada_observacao_aponta_para_os_bytes_dela(self):
        self.coletar("IT-T2-PROVA-0003")
        _, itens, _, _ = self.pela_rota("IT-T2-PROVA-0003")
        for x in itens:
            self.assertTrue(x.get("STORAGE_LOCATION", "").endswith(".pdf"), x)
            self.assertTrue(os.path.isfile(os.path.join(RAIZ, x["STORAGE_LOCATION"])))

    def test_11_quatro_zonas_dao_quatro_shas_diferentes(self):
        """O ficheiro de colheita e um so; as observacoes sao quatro.

        ⚠️ ESTE CASO E O QUE APANHAVA O DEFEITO ANTIGO: com o `_de` a servir de
        origem dos bytes, as quatro observacoes tinham o mesmo `sha256` — o do
        ficheiro de colheita — e o armazem guardava UMA linha em vez de quatro.
        """
        self.coletar("IT-T2-PROVA-0004")
        _, itens, _, entrada = self.pela_rota("IT-T2-PROVA-0004")
        fichas = [ing.ficha(x, corrida={"RUN_ID": "IT-T2-PROVA-0004"}, raiz=RAIZ)
                  for x in itens]
        self.assertEqual(len({f.SHA256 for f in fichas}), 4)
        self.assertEqual(entrada["PRESERVADOS"], 4)
        self.assertEqual(entrada["RECUSADOS"], 0)

    def test_12_o_adapter_nao_inventa_o_tempo_do_fato(self):
        """`UNKNOWN — o PDF nao expoe a data do fato` NAO e um instante."""
        self.coletar("IT-T2-PROVA-0005")
        bruta = self.livro()[0]
        self.assertTrue(str(bruta["FACT_TIME"]).startswith("UNKNOWN"))
        traduzida = adapter.traduzir(bruta)
        self.assertNotIn("FACT_TIME", traduzida)


class OBancoVeACorridaEntrar(CasoB1):
    """13..15 · collection_run e raw_asset, num banco descartavel."""

    def test_13_a_corrida_existe_no_banco_com_o_RUN_ID_do_T04(self):
        self.coletar("IT-T2-PROVA-0006")
        _, _, _, entrada = self.pela_rota("IT-T2-PROVA-0006")
        self.assertEqual(entrada["RUN_STATE"], "COMPLETE", entrada)
        self.assertIsNotNone(self.banco.corrida("IT-T2-PROVA-0006"))

    def test_14_ha_uma_linha_de_raw_asset_por_observacao(self):
        self.coletar("IT-T2-PROVA-0007")
        self.pela_rota("IT-T2-PROVA-0007")
        self.assertEqual(len(self.banco.objetos_da_corrida("IT-T2-PROVA-0007")), 4)

    def test_15_o_banco_nao_tinha_italia_antes_desta_corrida(self):
        self.assertEqual(self.banco.contar("raw_asset"), 0)
        self.coletar("IT-T2-PROVA-0008")
        self.pela_rota("IT-T2-PROVA-0008")
        self.assertEqual(self.banco.contar("raw_asset"), 4)


class ASegundaExecucao(CasoB1):
    """16..18 · voltar amanha nao inventa observacao nova nem perde os bytes."""

    def test_16_os_mesmos_bytes_dao_SEEN_AGAIN_e_nao_documento_novo(self):
        self.coletar("IT-T2-PROVA-D1")
        r2 = self.coletar("IT-T2-PROVA-D2")
        self.assertEqual(r2["contadores"]["SEEN_AGAIN"], 4)
        self.assertEqual(r2["contadores"]["NEW_DOCUMENTS"], 0)
        self.assertEqual(r2["contadores"]["RAW_OBJECTS_CREATED"], 0)

    def test_17_o_SEEN_AGAIN_continua_a_dizer_onde_os_bytes_estao(self):
        """⚠️ `RAW_PATH` era `null` em 109 das 144 observacoes reais.

        «nao criei o objecto agora» nao e «nao ha bytes em lado nenhum», e a
        porta, sem caminho, preservava o JSON em vez do documento.
        """
        self.coletar("IT-T2-PROVA-E1")
        self.coletar("IT-T2-PROVA-E2")
        segundas = [o for o in self.livro() if o["RUN_ID"] == "IT-T2-PROVA-E2"]
        self.assertEqual(len(segundas), 4)
        for o in segundas:
            self.assertEqual(o["OBSERVATION_RESULT"], "SEEN_AGAIN")
            self.assertFalse(o["RAW_OBJECT_CREATED"])
            self.assertTrue(str(o["RAW_PATH"]).endswith(".pdf"), o["RAW_PATH"])

    def test_18_a_segunda_corrida_nao_duplica_linhas_no_armazem(self):
        self.coletar("IT-T2-PROVA-F1")
        self.pela_rota("IT-T2-PROVA-F1")
        antes = self.banco.contar("raw_asset")
        self.coletar("IT-T2-PROVA-F2")
        _, _, _, entrada = self.pela_rota("IT-T2-PROVA-F2")
        self.assertEqual(entrada["PRESERVADOS"], 4)
        # Os bytes sao os mesmos, e o armazem enderecа por sha: a segunda
        # corrida REUSA o objecto em vez de criar outro.
        self.assertEqual(self.banco.contar("raw_asset"), antes)


class NadaDistoTocouARedeNemOAcervo(CasoB1):
    """19..21 · as travas do proprio teste."""

    def test_19_o_livro_real_com_as_144_observacoes_nao_foi_tocado(self):
        real = os.path.join(RAIZ, adapter.LIVRO)
        antes = os.path.getsize(real) if os.path.isfile(real) else 0
        self.coletar("IT-T2-PROVA-0009")
        self.pela_rota("IT-T2-PROVA-0009")
        depois = os.path.getsize(real) if os.path.isfile(real) else 0
        self.assertEqual(antes, depois)

    def test_20_com_bytes_injectados_o_egresso_e_NAO_SE_APLICA(self):
        """Nao e `NAO SEI`: a pergunta e que nao faz sentido.

        Medir o IP desta maquina quando nao houve ida a fonte registaria um
        endereco por onde nada passou — um numero com cara de medida.
        """
        resumo = self.coletar("IT-T2-PROVA-0010")
        self.assertEqual(resumo["EGRESS_IP"], "NAO_SE_APLICA")
        self.assertEqual(resumo["VPN_COUNTRY"], "NAO_SE_APLICA")

    def test_21_o_coletor_nao_promete_um_modo_seco_que_nao_tem(self):
        fonte = io.open(os.path.join(RAIZ, "coleta", "italy_pilot_collect.mjs"),
                        encoding="utf-8").read()
        tem_flag = '"--dry"' in fonte or "'--dry'" in fonte
        self.assertFalse(tem_flag, "ha um `--dry` a ser lido que nao existe")


if __name__ == "__main__":
    unittest.main(verbosity=2)
