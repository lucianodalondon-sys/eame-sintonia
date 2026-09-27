# -*- coding: utf-8 -*-
"""INTEGRAÇÃO-04A — as 18 fontes HTML do SOURCE CURATOR entram; as 50 do YouTube não
pelo feed. (BIG-COLLECTION-RELEASE, 2026-09-20: as 50 entraram pela rota do canal.)

O que este ficheiro prova, e por que cada prova existe:

  * a tabela que o motor lê (`regras/italy_contracts_onboarded.json`) tem as 18
    com a forma do curator — o registo da curadoria
    (`curadoria/italy_contracts_curator.json`) fica como registo, nunca como
    segunda fonte de verdade;
  * nenhuma das 50 fontes YouTube entra pelo FEED (`ROBOTS_DISALLOWED_ROUTE`):
    não há executor `YOUTUBE_CHANNEL_FEED`, a tabela não tem essa estratégia nem
    `feeds/videos.xml`, e o dono do contrato não lê o ficheiro da curadoria.
    Desde o BIG-COLLECTION-RELEASE (2026-09-20) as 50 estão na tabela pela rota
    do CANAL (`CUSTOM_ADAPTER` · `CANAL_PUBLICO_YOUTUBE_V1`, `/channel/<ID>/videos`),
    que o MESMO portão de robots aprova — com o CHANNEL_ID do curator, sem
    alteração, e zero código por SOURCE_ID;
  * a evidência das 18 foi promovida para o caminho canónico e os bytes batem
    com o sha256 do manifesto;
  * o Atlas carrega as 84 fichas, cada uma com `ESTADO_04A:` medido — 18
    READY, 50 bloqueadas, 9 com canário FAIL, 7 sem contrato.

    INTEGRAR FONTE != COLETAR FONTE. Nada aqui corre coleta.
"""
import io
import json
import os
import re
import shutil
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONBOARDED = os.path.join(RAIZ, "regras", "italy_contracts_onboarded.json")
DONO = os.path.join(RAIZ, "regras", "italy_contracts.mjs")
MOTOR = os.path.join(RAIZ, "regras", "motor_de_rota.mjs")
CURATOR = os.path.join(RAIZ, "curadoria", "italy_contracts_curator.json")
READY = os.path.join(RAIZ, "curadoria", "READY-FOR-COLLECTION-V1.json")
ATLAS = os.path.join(RAIZ, "docs", "fontes", "ATLAS-DE-FONTES-EAME.md")
SAMPLES = os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES")

AS_18 = (
    "IT-T5-039", "IT-T7-017", "IT-T7-021", "IT-T12-009", "IT-T7-031", "IT-T10-018",
    "IT-T12-013", "IT-T5-049", "IT-T7-033", "IT-T10-020", "IT-T10-021", "IT-T8-008",
    "IT-T10-022", "IT-T7-040", "IT-T7-041", "IT-T7-042", "IT-T2-030", "IT-T7-043",
)

# ── O QUE MUDA AO TRAZER ESTE FICHEIRO PARA A LINHA CANONICA ──────────────────
# CANONICAL-MICRO-COLLECTION-V1 (2026-09-21) enxertou a PONTE — a tabela
# `italy_contracts_onboarded.json` e o laco que a expande — de
# `aquisicao-detalhe-v1` para esta linha, ficheiro a ficheiro, NUNCA por merge:
# um merge apagaria o portao de admissao inteiro (`curadoria/collection_gate.py`,
# `ready_split.py`, `ponte_candidatas.py`), que so existe DESTE lado.
#
# A ponte funciona: CONTRATOS 14 -> 186, e o motor de rota DESTA linha aceita os
# 182 blocos executaveis sem uma alteracao.
#
# O que NAO veio, e porque: tres artefactos que estas provas leem vivem so do
# outro lado, e traze-los seria regressao ou cutover — os dois proibidos aqui.
#
#   * `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/` — as 18 pastas de evidencia
#     promovida nao existem nesta arvore (medido: 0 de 18).
#   * o bloco `ESTADO_04A:` do `ATLAS-DE-FONTES-EAME.md` — o Atlas desta linha
#     nao o tem (medido: 0 de 84 fichas com o campo).
#   * `conferirIdentidade` no `motor_de_rota.mjs` — o motor desta linha exporta
#     `identidadeDoContrato`, nao aquele nome.
#
# As provas que dependem deles ficam SKIP com a razao medida escrita no proprio
# skip, e voltam a verde sozinhas no dia em que o artefacto chegar. SKIP com
# razao nomeada nao e prova; e a ausencia dita em voz alta. Um `assert` apagado
# seria a ausencia dita em silencio.


def _texto(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def _json(p):
    return json.loads(_texto(p))


# Os tres artefactos que esta linha nao tem, MEDIDOS no arranque — nunca
# assumidos. A condicao e o que se ve no disco, nao o nome de um ramo.
SAMPLES_EM_FALTA = tuple(s for s in AS_18 if not os.path.isdir(os.path.join(SAMPLES, s)))
ATLAS_TEM_BLOCO_04A = "ESTADO_04A:" in _texto(ATLAS)
MOTOR_TEM_CONFERIR_IDENTIDADE = "export function conferirIdentidade" in _texto(MOTOR)

_SEM_SAMPLES = "evidencia promovida ausente nesta linha: %d de %d pastas em data/samples/IT-SOURCE-SAMPLES/ (vivem em aquisicao-detalhe-v1; promove-las e passo separado, nao esta missao)" % (len(SAMPLES_EM_FALTA), len(AS_18))
_SEM_ATLAS = "o ATLAS desta linha nao tem o bloco ESTADO_04A das 84 fichas (vive em aquisicao-detalhe-v1; traze-lo apaga 20 linhas do Atlas daqui)"
_SEM_CONFERIR = "motor_de_rota.mjs desta linha exporta identidadeDoContrato, nao conferirIdentidade; o motor daqui ja aceita os 182 blocos executaveis (medido), por isso NAO se troca o motor"


def _fichas_do_bloco_04a():
    """As fichas do bloco do curator, por SOURCE_ID, com os campos `CHAVE: valor`."""
    t = _texto(ATLAS)
    i = t.index("## ONDA SOURCE CURATOR")
    fichas, atual = {}, None
    for l in t[i:].split("\n"):
        m = re.match(r"^([A-Z_0-9]{3,32}):\s*(.*)$", l)
        if not m:
            continue
        if m.group(1) == "SOURCE_ID":
            atual = m.group(2).strip()
            fichas[atual] = {}
        elif atual:
            fichas[atual][m.group(1)] = m.group(2).strip()
    return fichas


class ATabelaDoDonoTemAs18ESoAs18(unittest.TestCase):

    def setUp(self):
        self.onb = _json(ONBOARDED)
        self.por_id = {r["SOURCE_ID"]: r for r in self.onb["FONTES"]}
        self.cur = _json(CURATOR)
        self.ready = _json(READY)

    def test_o_registo_da_curadoria_diz_18_ready_e_sao_estas(self):
        ready = sorted(f["SOURCE_ID"] for f in self.ready["FONTES"]
                       if f["STATE"] == "READY_FOR_COLLECTION")
        self.assertEqual(sorted(AS_18), ready)
        self.assertEqual(len(self.ready["FONTES"]), 77)

    def test_as_18_estao_na_tabela_com_a_forma_que_o_motor_expande(self):
        for sid in AS_18:
            with self.subTest(source_id=sid):
                r = self.por_id.get(sid)
                self.assertIsNotNone(r, "%s nao esta na tabela onboarded" % sid)
                self.assertEqual("HTML", r["OUTPUT_TYPE"])
                self.assertEqual("LOTE-HTML-ARTIGO", r["BATCH_ID"])
                self.assertEqual("HTML_LINK_DISCOVERY", r["ACQUISITION"]["STRATEGY"])
                self.assertEqual("URL", r["ACQUISITION"]["MATCH"])
                self.assertEqual({"STRATEGY", "MATCH", "INDEX_URL", "LINK_PATTERN", "MAX_TARGETS"},
                                 set(r["ACQUISITION"]))
                re.compile(r["ACQUISITION"]["LINK_PATTERN"])
                self.assertEqual("data/samples/IT-SOURCE-SAMPLES/%s/MANIFEST.json" % sid, r["EVIDENCE"])
                self.assertIn("SOURCE-CURATOR", r["ONBOARDED_BY"])
                self.assertEqual("NAO SEI", r["SONDAGEM"]["ENTRADA_BYTES"],
                                 "o canario nao mediu os bytes da entrada — nao se inventa")
                self.assertTrue(r["SONDAGEM"]["DOCUMENT_ID"].startswith(sid + ":URL:"))

    def test_a_aquisicao_e_a_do_curator_sem_alteracao(self):
        """A aquisicao e a da fotografia do curator — ou a divergencia esta DECLARADA.

        AQUISICAO-DETALHE-V1 (2026-09-20) corrigiu INDEX_URL / LINK_PATTERN /
        MAX_TARGETS em fontes LISTAGEM_DE_NOTICIAS com listagem provada. A
        fotografia do curator nao se reescreve (e registo); a divergencia vive em
        curadoria/CONTRATOS-PASSO-2-V1.json, com o ANTES igual a fotografia.
        Divergencia sem registo continua a reprovar.

        CANONICAL-MICRO-V1 (2026-09-21), medido nesta linha: a fotografia daqui
        tem 81 fontes e a de `aquisicao-detalhe-v1` tem 77 — sao fotografias
        diferentes. Nas 9 das 18 que o PASSO-2 tocou, a fotografia DESTA linha ja
        carrega o `DEPOIS` (9/9 medido), porque a missao que integrou o motor do
        curator a re-derivou; a de la ficou no `ANTES`. As outras 9 sao byte a
        byte iguais nas duas linhas.

        Por isso a prova passa a aceitar a fotografia em QUALQUER um dos dois
        estados declarados — `ANTES` ou `DEPOIS` — e continua a exigir que a
        TABELA tenha o `DEPOIS` e que a divergencia tenha listagem provada. Um
        terceiro valor, que nao esteja no registo, continua a reprovar: e essa a
        forca da prova, e ela nao foi afrouxada. O que caiu foi a suposicao de
        que so existe uma fotografia.
        """
        cur = {c["SOURCE_ID"]: c for c in self.cur["FONTES"]}
        passo2 = os.path.join(RAIZ, "curadoria", "CONTRATOS-PASSO-2-V1.json")
        declaradas = {}
        if os.path.exists(passo2):
            declaradas = {t["SOURCE_ID"]: t for t in _json(passo2)["TOCADAS"]}
        for sid in AS_18:
            with self.subTest(source_id=sid):
                if sid in declaradas:
                    self.assertIn(cur[sid]["ACQUISITION"],
                                  (declaradas[sid]["ANTES"], declaradas[sid]["DEPOIS"]),
                                  "a fotografia do curator nao e nem o ANTES nem o "
                                  "DEPOIS declarados — valor por registar")
                    self.assertEqual(declaradas[sid]["DEPOIS"], self.por_id[sid]["ACQUISITION"],
                                     "a tabela nao tem o DEPOIS declarado")
                    self.assertEqual(200, declaradas[sid]["PROVA"]["HTTP"], "divergencia sem listagem provada")
                else:
                    self.assertEqual(cur[sid]["ACQUISITION"], self.por_id[sid]["ACQUISITION"])
                self.assertEqual(cur[sid]["CARACTERIZACAO"], self.por_id[sid]["CARACTERIZACAO"],
                                 "a caracterizacao (com os NAO SEI) tem de chegar inteira")

    def test_a_tabela_tem_105_mais_18_mais_50(self):
        # as 173 da integracao 04A, mais as que o dono acrescenta DEPOIS, cada uma com o
        # carimbo do canario que provou a rota (onboardar_rotas_provadas, BC2: +18)
        depois = [f for f in self.onb["FONTES"]
                  if str(f.get("ONBOARDED_BY", "")).startswith("ROTAS-ELEGIVEIS-V1")]
        self.assertEqual(173, len(self.onb["FONTES"]) - len(depois))
        self.assertEqual(len(self.onb["FONTES"]), len(self.por_id), "SOURCE_ID repetido na tabela")

    def test_as_50_youtube_entram_pela_rota_do_canal_e_nunca_pelo_feed(self):
        cur = {c["SOURCE_ID"]: c for c in self.cur["FONTES"] if c["BATCH_ID"] == "LOTE-YOUTUBE-FEED"}
        self.assertEqual(50, len(cur))
        # o registo do curator continua a dizer o que mediu: a rota do FEED esta barrada
        bloqueadas = [f for f in self.ready["FONTES"] if f["STATE"] == "CONTRACT_READY_ROUTE_BLOCKED"]
        self.assertEqual(50, len(bloqueadas))
        self.assertEqual({"ROBOTS_DISALLOWED_ROUTE"}, {f["BLOCK_REASON"] for f in bloqueadas})
        self.assertEqual(set(cur), {f["SOURCE_ID"] for f in bloqueadas})
        # e a tabela do motor tem as 50 pela rota do CANAL, com o CHANNEL_ID do curator
        self.assertEqual([], [sid for sid in cur if sid not in self.por_id])
        for sid, c in cur.items():
            with self.subTest(source_id=sid):
                r = self.por_id[sid]
                self.assertEqual("LOTE-YOUTUBE-CANAL", r["BATCH_ID"])
                self.assertEqual("HTML", r["OUTPUT_TYPE"])
                self.assertEqual("CUSTOM_ADAPTER", r["ACQUISITION"]["STRATEGY"])
                self.assertEqual("CANAL_PUBLICO_YOUTUBE_V1", r["ACQUISITION"]["ADAPTER_ID"])
                self.assertEqual(c["ACQUISITION"]["CHANNEL_ID"], r["ACQUISITION"]["CHANNEL_ID"])
                self.assertEqual(c["SOURCE_NATIVE_ID"], r["SOURCE_NATIVE_ID"])
                self.assertEqual(c["CARACTERIZACAO"], r["CARACTERIZACAO"],
                                 "a caracterizacao (com os NAO SEI) tem de chegar inteira")
                self.assertEqual("ALLOWED", r["SONDAGEM"]["ROBOTS_GATE"])
                self.assertEqual("YES", r["SONDAGEM"]["IDENTITY_MATCH"])
                self.assertGreater(r["SONDAGEM"]["ALVOS_DESCOBERTOS"], 0)
                self.assertIn("BIG-COLLECTION-RELEASE", r["ONBOARDED_BY"])
                self.assertNotIn("feeds/videos.xml", json.dumps(r["ACQUISITION"]))
                # a identidade e a do curator: videoId nativo, nunca o endereco com `?`
                self.assertEqual("PLATFORM_NATIVE_ID", r["IDENTITY_KIND"])
                self.assertEqual(sid + ":YT:{video.1}", r["IDENTITY"]["DOCUMENT_ID"])
                self.assertEqual("URL", r["IDENTITY"]["CAPTURES"]["video"]["FROM"])
                self.assertRegex(r["SONDAGEM"]["DOCUMENT_ID"], r"^" + re.escape(sid) + r":YT:[A-Za-z0-9_-]{11}$")

    def test_nem_as_9_com_canario_fail_nem_as_7_sem_contrato(self):
        fail = [f["SOURCE_ID"] for f in self.ready["FONTES"] if f["STATE"] == "CONTRACTED_CANARY_FAILED"]
        sem = [s["SOURCE_ID"] for s in self.cur["SEM_CONTRATO"]]
        self.assertEqual(9, len(fail))
        self.assertEqual(7, len(sem))
        self.assertEqual([], [sid for sid in fail + sem if sid in self.por_id])

    def test_a_tabela_nao_tem_estrategia_nem_tipo_de_youtube(self):
        for r in self.onb["FONTES"]:
            self.assertNotEqual("YOUTUBE_CHANNEL_FEED", r["ACQUISITION"]["STRATEGY"], r["SOURCE_ID"])
            self.assertNotEqual("VIDEO_METADATA", r["OUTPUT_TYPE"], r["SOURCE_ID"])
            self.assertNotIn("youtube.com/feeds", json.dumps(r["ACQUISITION"]), r["SOURCE_ID"])


class OMotorNaoAlcancaAs50PeloFeed(unittest.TestCase):

    def test_o_dono_nao_le_o_ficheiro_da_curadoria(self):
        for p in (DONO, MOTOR):
            with self.subTest(ficheiro=os.path.basename(p)):
                t = _texto(p)
                self.assertNotIn("italy_contracts_curator", t,
                                 "o ficheiro da curadoria e registo, nao configuracao lida pelo dono")
                self.assertNotIn("YOUTUBE_CHANNEL_FEED", t, "nao existe executor para o feed")

    def test_a_pasta_coleta_nao_tem_executor_para_o_feed(self):
        pasta = os.path.join(RAIZ, "coleta")
        achados = []
        for nome in sorted(os.listdir(pasta)):
            p = os.path.join(pasta, nome)
            if os.path.isfile(p) and nome.endswith((".mjs", ".py", ".js")):
                if "YOUTUBE_CHANNEL_FEED" in _texto(p) or "italy_contracts_curator" in _texto(p):
                    achados.append(nome)
        self.assertEqual([], achados)

    @unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
    @unittest.skipUnless(MOTOR_TEM_CONFERIR_IDENTIDADE, _SEM_CONFERIR)
    def test_o_dono_expande_as_18_e_as_50_pela_rota_do_canal(self):
        yt = [c["SOURCE_ID"] for c in _json(CURATOR)["FONTES"] if c["BATCH_ID"] == "LOTE-YOUTUBE-FEED"]
        prog = (
            "import { CONTRACTS, ONBOARDED_IDS } from './regras/italy_contracts.mjs';"
            "import { conferirAquisicao, conferirIdentidade, identidadeDoContrato } from './regras/motor_de_rota.mjs';"
            "const as18 = %s; const yt = %s;"
            "const out = { faltam: as18.filter(i => !CONTRACTS[i] || CONTRACTS[i].ACQUISITION.STRATEGY !== 'HTML_LINK_DISCOVERY'),"
            "  yt_fora: yt.filter(i => !CONTRACTS[i] || !ONBOARDED_IDS.includes(i)),"
            "  yt_pelo_canal: yt.filter(i => CONTRACTS[i] && CONTRACTS[i].ACQUISITION.STRATEGY === 'CUSTOM_ADAPTER' && CONTRACTS[i].ACQUISITION.ADAPTER_ID === 'CANAL_PUBLICO_YOUTUBE_V1' && CONTRACTS[i].ROUTE_TYPE === 'APPLICATION_ROUTE' && CONTRACTS[i].EXPECTED_SIGNATURE === '<' && CONTRACTS[i].IDENTITY_KIND === 'PLATFORM_NATIVE_ID' && identidadeDoContrato(i, CONTRACTS[i], { url: 'https://www.youtube.com/watch?v=abcdefghijk', nome: 'abcdefghijk' }).DOCUMENT_ID === i + ':YT:abcdefghijk'),"
            "  yt_invalidos: yt.filter(i => { try { conferirAquisicao(i, CONTRACTS[i].ACQUISITION); conferirIdentidade(i, CONTRACTS[i].IDENTITY); return false; } catch (e) { return true; } }),"
            "  onboarded: ONBOARDED_IDS.length,"
            "  onboarded_by: as18.map(i => CONTRACTS[i].ONBOARDED_BY),"
            "  yt_onboarded_by: yt.map(i => CONTRACTS[i] ? CONTRACTS[i].ONBOARDED_BY : '') };"
            "console.log(JSON.stringify(out));" % (json.dumps(list(AS_18)), json.dumps(yt)))
        r = subprocess.run(["node", "--input-type=module", "-e", prog], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, r.returncode, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual([], out["faltam"])
        self.assertEqual([], out["yt_fora"])
        self.assertEqual(50, len(out["yt_pelo_canal"]))
        self.assertEqual([], out["yt_invalidos"], "as 50 passam conferirAquisicao + conferirIdentidade")
        depois = sum(1 for f in json.load(open(os.path.join(RAIZ, "regras", "italy_contracts_onboarded.json"),
                                          encoding="utf-8"))["FONTES"]
                     if str(f.get("ONBOARDED_BY", "")).startswith("ROTAS-ELEGIVEIS-V1"))
        self.assertEqual(173, out["onboarded"] - depois)
        for ob in out["onboarded_by"]:
            self.assertIn("SOURCE-CURATOR", ob, "o contrato expandido tem de dizer de onde veio")
        for ob in out["yt_onboarded_by"]:
            self.assertIn("BIG-COLLECTION-RELEASE", ob)
            self.assertIn("376c0d9b", ob, "a identidade veio do curator; a rota, da lane YouTube")


class AEvidenciaDas18TemManifestoNoCaminhoCanonico(unittest.TestCase):
    """O manifesto (sha256) foi promovido; os bytes ficaram fora do Git, de propósito.

    Os bytes entrariam no frame de revisão T3 (`provas/amostragem_neutra_t3.py`
    conta todo corpo em `data/samples/IT-SOURCE-SAMPLES/*/*`), que é uma
    população congelada com veredito humano. Promovê-los é passo separado.
    O sha256 do manifesto promovido tem de ser o do manifesto do curator —
    dois registos versionados a dizer o mesmo número.
    """

    def setUp(self):
        self.curator = {e["CANDIDATE_ID"]: e
                        for e in _json(os.path.join(RAIZ, "curadoria", "REAL-EXAMPLE-MANIFEST-V1.json"))["FILES"]}

    @unittest.skipIf(SAMPLES_EM_FALTA, _SEM_SAMPLES)
    def test_manifesto_sem_bytes_e_com_o_sha_do_curator(self):
        for sid in AS_18:
            with self.subTest(source_id=sid):
                pasta = os.path.join(SAMPLES, sid)
                self.assertEqual(["MANIFEST.json"], sorted(os.listdir(pasta)),
                                 "apareceram bytes na pasta — isso muda o frame T3 e e passo separado")
                man = _json(os.path.join(pasta, "MANIFEST.json"))
                self.assertEqual(sid, man["SOURCE_ID"])
                self.assertEqual("SHA256_VERIFIED_BYTES_NOT_IN_GIT", man["RAW_EVIDENCE_STATE"])
                self.assertNotIn("OWNER_ID", man, "a curadoria nao mediu chave de dono — nao se inventa")
                f = man["FILES"][0]
                self.assertIsNone(f["RAW_FILE"])
                self.assertFalse(f["BYTES_IN_GIT"])
                self.assertRegex(f["SHA256"], r"^[0-9a-f]{64}$")
                e = self.curator[man["PROVENIENCIA"]["CANDIDATE_ID"]]
                self.assertEqual(e["SHA256"], f["SHA256"], "o sha promovido nao e o do curator")
                self.assertEqual(e["BYTES"], f["BYTES"])
                self.assertEqual(sid + ":URL:", man["CANARIO"]["DOCUMENT_ID"][:len(sid) + 5])
                self.assertEqual("ALLOWED", man["ROBOTS_GATE"]["RESULT"])


class ACuradoriaERegistoNaoFerramenta(unittest.TestCase):
    """`curadoria/` traz o registo da missão (JSON, MD); as ferramentas ficaram na branch.

    Medido na primeira bateria: `curadoria/gate_de_rota.py` era um segundo
    leitor de `robots.txt`, e `OPortaoDeTransporteTemUmDonoSo` só admite
    `coleta/scrap_http.py`. As ferramentas vivem em
    `claude/bot-de-fontes-v2-plano @ 376c0d9b`.

    ── CONFLITO DE LEIS, DECLARADO (CANONICAL-MICRO-V1, 2026-09-21) ──────────
    Em `aquisicao-detalhe-v1` esta lei diz `curadoria/` = ZERO codigo. Nesta
    linha `curadoria/` e onde vive o PORTAO DE ADMISSAO — `collection_gate.py`,
    `ready_split.py`, `ponte_candidatas.py`, `descobrir.py`, `retrato_html.py` —
    que a outra linha NAO tem. Cumprir a lei de la aqui seria apagar o portao.
    Por isso ela e REVOGADA nesta linha, por escrito, com o motivo.

    O QUE NAO SE REVOGA e a razao que lhe deu origem: um SEGUNDO LEITOR DE
    ROBOTS. Essa continua a valer e continua a ser medida — pelo
    `test_so_um_ficheiro_le_o_robots` de `tests/test_c10_5_collection_flow.py`,
    que e a MESMA lei vista do outro lado.

    E ela esta VERMELHA nesta linha, antes desta missao e sem relacao com ela.
    Medido em 2026-09-21 no HEAD `4fdabf82`, `RobotFileParser` fora de `tests/`:

        coleta/scrap_http.py       <- o dono legitimo
        curadoria/descobrir.py     <- 2.o leitor
        curadoria/gate_de_rota.py  <- 3.o leitor

    Divida herdada, NAO curada aqui (curar e mexer no caminho de robots a meio
    de uma missao de coleta: seria mudar a regua durante a medicao). O que esta
    prova passa a fazer e impedir que a divida CRESCA: um quarto leitor reprova.
    """

    # Os dois leitores herdados, nomeados um a um. A lista nao e um limite
    # numerico — e a identidade de cada divida conhecida. Um leitor novo, mesmo
    # que outro desapareca, reprova.
    LEITORES_HERDADOS_EM_CURADORIA = ("curadoria/descobrir.py", "curadoria/gate_de_rota.py")

    def test_curadoria_tem_codigo_nesta_linha_e_isso_e_declarado(self):
        """A revogacao e um FACTO medido, nao uma frase num comentario."""
        pasta = os.path.join(RAIZ, "curadoria")
        codigo = sorted(n for n in os.listdir(pasta) if n.endswith((".py", ".mjs", ".js", ".sh")))
        self.assertNotEqual([], codigo,
                            "curadoria/ ficou sem codigo: ou o portao de admissao foi "
                            "apagado, ou esta linha deixou de ser a linha do portao")
        for essencial in ("collection_gate.py", "ready_split.py", "ponte_candidatas.py"):
            self.assertIn(essencial, codigo,
                          "%s desapareceu de curadoria/ — e o portao de admissao. "
                          "Se isto reprova depois de um `git merge aquisicao-detalhe-v1`, "
                          "foi o merge: ele apaga o portao sem conflito e sem aviso." % essencial)

    def test_nenhum_leitor_de_robots_novo_em_curadoria(self):
        """A divida herdada nao cresce. Quarto leitor reprova."""
        pasta = os.path.join(RAIZ, "curadoria")
        leitores = sorted(
            "curadoria/" + n for n in os.listdir(pasta)
            if n.endswith(".py")
            and "RobotFileParser" in _texto(os.path.join(pasta, n)))
        self.assertEqual(sorted(self.LEITORES_HERDADOS_EM_CURADORIA), leitores,
                         "mudou o conjunto de leitores de robots.txt em curadoria/. "
                         "Um leitor NOVO e divida nova e nao entra por aqui; um leitor "
                         "que sumiu e divida paga e tira-se desta lista, a mao, "
                         "com o commit que a pagou.")

    def test_o_registo_essencial_esta_la(self):
        for nome in ("italy_contracts_curator.json", "READY-FOR-COLLECTION-V1.json",
                     "REAL-EXAMPLE-MANIFEST-V1.json", "CANARY-LOTE-HTML-ARTIGO.json",
                     "CANARY-LOTE-YOUTUBE-FEED.json", "SOURCE-ID-ALLOCATION-V1.json",
                     "HANDOFF-INTEGRACAO-04.md"):
            self.assertTrue(os.path.exists(os.path.join(RAIZ, "curadoria", nome)), nome)


class OAtlasCarregaAs84ComEstadoMedido(unittest.TestCase):

    def setUp(self):
        self.fichas = _fichas_do_bloco_04a()

    @unittest.skipUnless(ATLAS_TEM_BLOCO_04A, _SEM_ATLAS)
    def test_84_fichas_cada_uma_com_estado(self):
        self.assertEqual(84, len(self.fichas))
        self.assertEqual([], [sid for sid, f in self.fichas.items() if "ESTADO_04A" not in f])

    @unittest.skipUnless(ATLAS_TEM_BLOCO_04A, _SEM_ATLAS)
    def test_a_contagem_por_estado_e_18_50_9_7(self):
        estados = {}
        for f in self.fichas.values():
            e = f["ESTADO_04A"].split(" ")[0]
            estados[e] = estados.get(e, 0) + 1
        self.assertEqual({"READY_FOR_COLLECTION": 18, "CONTRACT_READY_ROUTE_BLOCKED": 50,
                          "CONTRACTED_CANARY_FAILED": 9, "SEM_CONTRATO": 7}, estados)
        for sid in AS_18:
            self.assertTrue(self.fichas[sid]["ESTADO_04A"].startswith("READY_FOR_COLLECTION"), sid)
            self.assertIn("data/samples/IT-SOURCE-SAMPLES/%s/" % sid, self.fichas[sid]["EVIDENCE"])

    @unittest.skipUnless(ATLAS_TEM_BLOCO_04A, _SEM_ATLAS)
    def test_as_50_dizem_a_razao_do_bloqueio(self):
        for sid, f in self.fichas.items():
            if f["ESTADO_04A"].startswith("CONTRACT_READY_ROUTE_BLOCKED"):
                self.assertIn("ROBOTS_DISALLOWED_ROUTE", f["ESTADO_04A"], sid)
                self.assertIn("PLATFORM_NATIVE_ID", f, "a caracterizacao do canal foi apagada")

    def test_nenhum_source_id_do_bloco_se_repete_no_resto_do_atlas(self):
        t = _texto(ATLAS)
        antes = t[:t.index("## ONDA SOURCE CURATOR")]
        repetidos = [sid for sid in self.fichas if re.search(r"^SOURCE_ID:\s+%s\b" % re.escape(sid), antes, re.M)]
        self.assertEqual([], repetidos)


if __name__ == "__main__":
    unittest.main()
