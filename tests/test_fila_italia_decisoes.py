#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA DECISAO DA FILA ITALIANA

    UMA FILA DECIDIDA POR UMA REGUA QUE NINGUEM CONSEGUE RE-CORRER
    E UMA FILA DECIDIDA POR OPINIAO.

Estas provas nao se contentam em ler o ficheiro de saida. A maior parte delas
volta a chamar `decidir()` com casos construidos a mao — incluindo casos que
TEM de continuar a ser recusados — porque uma regra que so sabe dizer «nao
recuso nada» passaria num teste de uma face e seria inutil.

Duas faces, sempre:

    face A   429 / muro de login / titulo generico  ->  a recusa e' revogada
    face B   motivo com prova que o sustenta        ->  a recusa FICA

Corre como os outros testes desta casa:  py tests/test_fila_italia_decisoes.py
"""
import hashlib
import json
import os
import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
sys.path.insert(0, str(RAIZ / "leis"))

import decidir_fila_italia as D          # noqa: E402
import fonte_do_atlas as ATLAS           # noqa: E402
import reconciliar_fichas_orfas as REC   # noqa: E402
import xlsx_simples as XL                # noqa: E402

FILA = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
ATLAS_MD = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
AMOSTRAS = RAIZ / "data" / "samples" / "IT-SOURCE-SAMPLES"

#: Medido em 2026-09-15 nesta branch. Se mudar, tem de mudar com motivo escrito.
POPULACAO_ESPERADA = 257
FILA_ESPERADA = 241
RECONCILIADAS = 13


def _fila():
    return json.loads(FILA.read_text(encoding="utf-8"))


#: D24 (24/09): a prova oficial de identidade de um perfil de pessoa, como a porta a
#: escreve na NOTA (P4b: «PROVA_IDENTIDADE=<url>»; P5b: «IDENTIDADE: a pagina oficial
#: da pessoa <url>»). Sem uma destas, um perfil social continua POLICY_BLOCK.
_PROVA_D24 = re.compile(r"(PROVA_IDENTIDADE=|IDENTIDADE: a pagina oficial da pessoa )https?://\S+")


def _tem_prova_d24(c):
    return bool(_PROVA_D24.search(c.get("NOTA") or ""))


def _violacoes_d24(d, sociais):
    """IDs que quebram a regra D24: social sem prova fora do POLICY_BLOCK, ou POLICY_BLOCK nao social."""
    return [c["CANDIDATA_ID"] for c in d["CANDIDATAS"]
            if (c["TIPO"] in sociais and not _tem_prova_d24(c) and c["ESTADO"] != "POLICY_BLOCK")
            or (c["ESTADO"] == "POLICY_BLOCK" and c["TIPO"] not in sociais)]


#: D13 (23/09, DECISOES-DONO-2026-09-23 linha 116, bot Luciano por delegacao do
#: dono): «a nota "o que falta" NAO e lei». Estas provas medem a DECISAO da fila
#: de 14/09 — a qualificacao de 14/09, decidida por decidir_fila_italia.py e
#: carimbada DECIDIDA_EM = 2026-09-15. E esse grupo, e so esse, que elas olham.
#: As candidatas que a discovery trouxe depois sao outra populacao: contam-se e
#: ficam a vista (TestAsNovasContamSeEFicamAVista), sem nota inventada.
DECIDIDA_EM_DA_COORTE = "2026-09-15"


def _coorte(d=None):
    d = d or _fila()
    return [c for c in d["CANDIDATAS"] if c.get("DECIDIDA_EM") == DECIDIDA_EM_DA_COORTE]


def _novas(d=None):
    d = d or _fila()
    return [c for c in d["CANDIDATAS"] if c.get("DECIDIDA_EM") != DECIDIDA_EM_DA_COORTE]


class TestAFilaFoiDecididaEDizPorque(unittest.TestCase):

    def test_a_fila_tem_as_241_e_nenhuma_ficou_sem_decisao(self):
        d = _fila()
        coorte = _coorte(d)
        self.assertEqual(len(coorte), FILA_ESPERADA)
        self.assertEqual(d["TOTAL"], len(d["CANDIDATAS"]), "o TOTAL da fila nao conta as linhas dela")
        for c in coorte:
            with self.subTest(candidata=c["NOME"][:40]):
                self.assertIn(c["ESTADO"], set(d["ESTADOS"]),
                              "estado fora do vocabulario declarado pela propria fila")
                self.assertTrue((c.get("PORQUE") or "").strip(),
                                "linha na fila sem porque escrito")
                self.assertTrue((c.get("EVIDENCIA") or "").strip(),
                                "linha na fila sem evidencia escrita")
                self.assertEqual(c.get("DECIDIDA_EM"), "2026-09-15")

    def test_em_analise_diz_sempre_o_que_falta(self):
        """EM_ANALISE sem «o que falta» e' limbo com outro nome."""
        coorte = _coorte()
        self.assertEqual(len(coorte), FILA_ESPERADA)
        for c in coorte:
            if c["ESTADO"] == "EM_ANALISE":
                with self.subTest(candidata=c["NOME"][:40]):
                    self.assertTrue((c.get("O_QUE_FALTA") or "").strip())

    def test_a_fila_nao_emite_source_id(self):
        """A fila e' a fila. Quem emite identidade e' o atlas."""
        for c in _fila()["CANDIDATAS"]:
            with self.subTest(candidata=c["NOME"][:40]):
                self.assertIsNone(c.get("SOURCE_ID"),
                                  "uma candidata saiu da fila com SOURCE_ID atribuido")

    def test_recusada_traz_sempre_o_motivo_no_campo_proprio(self):
        for c in _fila()["CANDIDATAS"]:
            if c["ESTADO"] == "RECUSADA":
                with self.subTest(candidata=c["NOME"][:40]):
                    self.assertTrue((c.get("MOTIVO_DA_RECUSA") or "").strip())


class TestAsNovasContamSeEFicamAVista(unittest.TestCase):
    """D13 (2): as candidatas que chegaram depois de 14/09 continuam contadas e a
    vista como «ainda nao sabemos» — nem prontas nem recusadas por omissao — e a
    nota nao se inventa para encher."""

    def test_toda_a_fila_e_contada_coorte_mais_novas(self):
        d = _fila()
        self.assertEqual(len(_coorte(d)) + len(_novas(d)), d["TOTAL"])
        self.assertGreater(len(_novas(d)), 0, "nao ha novas: esta prova passaria por vazio")

    def test_nova_sem_nota_fica_em_ainda_nao_sabemos(self):
        for c in _novas():
            if (c.get("O_QUE_FALTA") or "").strip():
                continue
            with self.subTest(candidata=c["CANDIDATA_ID"]):
                self.assertIn(c["ESTADO"], ("CANDIDATA", "EM_ANALISE", "RECUSADA", "CAPABILITY_BLOCK"))
                self.assertNotEqual(c["ESTADO"], "PROMOVIDA", "promovida sem nota nem prova")
                self.assertIsNone(c.get("SOURCE_ID"))

    def test_nenhuma_nota_generica_de_enchimento(self):
        """PROIBIDO (D13): a mesma frase copiada para varias novas nao e nota, e enchimento."""
        from collections import Counter
        notas = Counter((c.get("O_QUE_FALTA") or "").strip() for c in _novas())
        notas.pop("", None)
        self.assertEqual([n for n, k in notas.items() if k > 1], [])


class TestSemCapacidadeNaoERecusa(unittest.TestCase):
    """D13 (3): rede social sem capacidade e CAPABILITY_BLOCK, nao RECUSADA."""

    def test_nenhuma_recusa_por_falta_de_capacidade(self):
        d = _fila()
        self.assertIn("CAPABILITY_BLOCK", d["ESTADOS"])
        for c in d["CANDIDATAS"]:
            with self.subTest(candidata=c["CANDIDATA_ID"]):
                if c["ESTADO"] == "RECUSADA":
                    self.assertNotIn("CAPABILITY_BLOCK", c.get("MOTIVO_DA_RECUSA") or "")
                if c["ESTADO"] == "CAPABILITY_BLOCK":
                    self.assertTrue((c.get("MOTIVO_DO_BLOQUEIO") or "").strip())


class TestOsTermosProibemEProvamSe(unittest.TestCase):
    """D15 (23/09, DECISOES-DONO-2026-09-23 linha 144): LinkedIn e Instagram ficam
    POLICY_BLOCK — nem pronta, nem recusada, nem em analise — e a prova e o trecho
    dos termos, com endereco e data. O 429 da sonda de 14/09 fica so como historico:
    429 e «demasiados pedidos», nao «proibido»."""

    SOCIAIS = ("LINKEDIN", "INSTAGRAM")

    # ⚠️ ATUALIZADO PELA D24 (dono real, 24/09 ~12:55, por escrito): perfis de PESSOAS
    # do agro sao autorizados. Um perfil LinkedIn/Instagram de pessoa COM prova oficial
    # de identidade (D21/D24: pagina ou CV oficial que liga a pessoa ao perfil, escrita
    # na NOTA pela porta) pode ser candidata normal. SEM essa prova continua
    # POLICY_BLOCK, como antes da D24 — e este guarda morre se um escapar.
    def test_todas_as_sociais_sem_prova_d24_estao_em_policy_block(self):
        d = _fila()
        self.assertIn("POLICY_BLOCK", d["ESTADOS"])
        sociais = [c for c in d["CANDIDATAS"] if c["TIPO"] in self.SOCIAIS]
        sem_prova = [c for c in sociais if not _tem_prova_d24(c)]
        self.assertGreater(len(sem_prova), 0, "nao ha sociais sem prova: esta prova passaria por vazio")
        for c in sem_prova:
            with self.subTest(candidata=c["CANDIDATA_ID"]):
                self.assertEqual(c["ESTADO"], "POLICY_BLOCK")
                self.assertFalse(c.get("MOTIVO_DA_RECUSA"))
                self.assertIsNone(c.get("SOURCE_ID"))
        self.assertEqual(_violacoes_d24(d, self.SOCIAIS), [])

    def test_o_guarda_morre_se_um_perfil_sem_prova_escapa(self):
        import copy
        d = copy.deepcopy(_fila())
        alvo = next(c for c in d["CANDIDATAS"]
                    if c["TIPO"] in self.SOCIAIS and not _tem_prova_d24(c) and c["ESTADO"] == "POLICY_BLOCK")
        alvo["ESTADO"] = "CANDIDATA"
        self.assertEqual(_violacoes_d24(d, self.SOCIAIS), [alvo["CANDIDATA_ID"]])

    def test_o_guarda_morre_se_a_prova_d24_desaparece(self):
        import copy
        d = copy.deepcopy(_fila())
        abertos = [c for c in d["CANDIDATAS"]
                   if c["TIPO"] in self.SOCIAIS and c["ESTADO"] != "POLICY_BLOCK"]
        self.assertGreater(len(abertos), 0, "nao ha perfis D24 abertos: esta prova passaria por vazio")
        abertos[0]["NOTA"] = "sem prova"
        self.assertEqual(_violacoes_d24(d, self.SOCIAIS), [abertos[0]["CANDIDATA_ID"]])

    def test_a_prova_e_o_trecho_dos_termos_e_nunca_o_429(self):
        import hashlib
        for c in _fila()["CANDIDATAS"]:
            if c["ESTADO"] != "POLICY_BLOCK":
                continue
            with self.subTest(candidata=c["CANDIDATA_ID"]):
                ev = c.get("EVIDENCIA_POLITICA") or {}
                for campo in ("URL", "EM_VIGOR", "LIDO_EM", "TRECHO", "FICHEIRO", "SHA256"):
                    self.assertTrue((ev.get(campo) or "").strip(), campo)
                self.assertTrue(ev["URL"].startswith("https://"))
                self.assertTrue((c.get("EVIDENCIA") or "").startswith("TERMOS https://"))
                self.assertNotIn("429", c.get("EVIDENCIA") or "")
                pagina = RAIZ / ev["FICHEIRO"]
                self.assertEqual(hashlib.sha256(pagina.read_bytes()).hexdigest(), ev["SHA256"])

    def test_a_proxima_expansao_people_social_e_contada(self):
        # D24: a conta ja nao e «POLICY_BLOCK == todas as sociais». E: todo POLICY_BLOCK
        # e social, e toda social sem prova D24 e POLICY_BLOCK (_violacoes_d24 vazio).
        d = _fila()
        n = sum(1 for c in d["CANDIDATAS"] if c["ESTADO"] == "POLICY_BLOCK")
        abertos = sum(1 for c in d["CANDIDATAS"] if c["TIPO"] in self.SOCIAIS and c["ESTADO"] != "POLICY_BLOCK")
        self.assertEqual(_violacoes_d24(d, self.SOCIAIS), [])
        self.assertEqual(n + abertos, sum(1 for c in d["CANDIDATAS"] if c["TIPO"] in self.SOCIAIS))
        print("PROXIMA_EXPANSAO_PEOPLE_SOCIAL = %d · PERFIS_D24_COM_PROVA_ABERTOS = %d" % (n, abertos))


class TestNaoSeRecusaOQueNinguemLeu(unittest.TestCase):
    """O atlas: «Nunca converter "nao consegui verificar" em RED.»"""

    def _linha(self, http="200", flags="", canonico="https://www.exemplo.it/",
               testado="https://www.exemplo.it/"):
        return ({"NOME": "Fonte de teste", "URL": testado},
                {"HTTP_STATUS": http, "URL_CANONICAL": canonico,
                 "URL_ORIGINAL": testado, "EVIDENCE": "prova",
                 "OWNER_MATCH": "PROVED_DIRECT", "ITALY_SCOPE_PROVED": "SIM",
                 "QUALIFICATION_GATE": "REJECT", "QUALIFICATION_SCORE": "10",
                 "UPDATE_SCORE": "3", "URL_STATUS": "CANONICAL"},
                {"FLAGS": flags, "VALIDATION_RESULT": "PASS",
                 "URL_TESTADA": testado, "URL_FINAL": canonico,
                 "VALIDATION_METHOD": "sonda HTTP read-only (GET limitado, "
                                      "payload nao preservado)"})

    # ---------------------------------------------------- face A · revogar
    def test_429_nao_recusa(self):
        c, q, v = self._linha(http="429", flags="HTTP_429,THIN_BODY")
        d = D.decidir(c, q, v, {"REASON": "sem utilidade agricola", "EVIDENCE": "x"}, None)
        self.assertEqual(d["DECISION"], "EM_ANALISE")
        self.assertIn("REVOGADA", d["WHY"])

    def test_titulo_da_plataforma_nao_recusa(self):
        c, q, v = self._linha(flags="PLATFORM_GENERIC_TITLE")
        d = D.decidir(c, q, v, {"REASON": "sem utilidade agricola", "EVIDENCE": "x"}, None)
        self.assertEqual(d["DECISION"], "EM_ANALISE")

    def test_muro_de_login_no_endereco_nao_recusa(self):
        c, q, v = self._linha(canonico="https://www.linkedin.com/login")
        d = D.decidir(c, q, v, {"REASON": "duplicata real de X", "EVIDENCE": "x"}, None)
        self.assertEqual(d["DECISION"], "EM_ANALISE")
        self.assertIn("muro de login", d["WHY"])

    # ---------------------------------------------------- face B · manter
    def test_recusa_com_prova_que_a_sustenta_FICA_recusa(self):
        """Sem esta, a regra seria «nunca recuso nada» — e isso nao e' regra."""
        c, q, v = self._linha(http="200", flags="")
        d = D.decidir(c, q, v,
                      {"REASON": "o dono declara que a pagina foi descontinuada",
                       "EVIDENCE": "aviso no proprio site, lido em 2026-09-14"}, None)
        self.assertEqual(d["DECISION"], "RECUSADA")
        self.assertEqual(d["STATUS"], "RECUSADA")

    def test_as_25_recusas_de_14_09_estao_todas_revogadas_na_fila(self):
        revogadas = [c for c in _fila()["CANDIDATAS"]
                     if "REVOGADA" in (c.get("PORQUE") or "")]
        self.assertEqual(len(revogadas), 25)
        for c in revogadas:
            with self.subTest(candidata=c["NOME"][:40]):
                # D13 (3): CAPABILITY_BLOCK nao e recusa — e o estado de uma fonte
                # boa sem capacidade. A revogacao de 14/09 continua cumprida.
                if c["ESTADO"] == "CAPABILITY_BLOCK":
                    self.assertTrue((c.get("MOTIVO_DO_BLOQUEIO") or "").strip())
                    continue
                # D15: os termos da plataforma proibem — POLICY_BLOCK com o trecho
                # dos termos como prova, nunca a sonda de 429 que a revogacao desfez.
                if c["ESTADO"] == "POLICY_BLOCK":
                    self.assertTrue((c.get("EVIDENCIA_POLITICA") or {}).get("TRECHO"))
                    self.assertNotIn("429", c.get("EVIDENCIA") or "")
                    continue
                self.assertEqual(c["ESTADO"], "EM_ANALISE")

    def test_nenhuma_recusa_viva_assenta_em_429_ou_muro(self):
        for c in _fila()["CANDIDATAS"]:
            if c["ESTADO"] != "RECUSADA":
                continue
            with self.subTest(candidata=c["NOME"][:40]):
                prova = (c.get("EVIDENCIA") or "").upper()
                self.assertNotIn("429", prova)
                self.assertNotIn("PLATFORM_GENERIC_TITLE", prova)
                self.assertNotIn("THIN_BODY", prova)


class TestOEnderecoLidoNaoEMetadeDoEndereco(unittest.TestCase):
    """O atlas parte URL longo em duas linhas. Meia chave nunca casa."""

    def test_o_leitor_junta_as_continuacoes(self):
        texto = ("SOURCE_ID:                    IT-T9-999\n"
                 "URL:                          https://www.exemplo.it/um/caminho-muito-\n"
                 "                              longo/que-continua-na-linha-seguinte\n"
                 "ACCESS_METHOD:                HTML\n")
        lidos = D.enderecos_do_atlas(texto)
        self.assertIn("exemplo.it/um/caminho-muito-longo/que-continua-na-linha-seguinte",
                      lidos)

    def test_um_campo_novo_nao_e_confundido_com_continuacao(self):
        texto = ("SOURCE_ID:                    IT-T9-998\n"
                 "URL:                          https://www.exemplo.it/\n"
                 "ACCESS_METHOD:                HTML\n")
        lidos = D.enderecos_do_atlas(texto)
        self.assertEqual(set(lidos), {"exemplo.it"})

    def test_o_atlas_real_le_se_sem_endereco_truncado(self):
        lidos = D.enderecos_do_atlas(ATLAS_MD.read_text(encoding="utf-8"))
        self.assertGreater(len(lidos), 100)
        for endereco in lidos:
            with self.subTest(endereco=endereco[:50]):
                self.assertFalse(endereco.endswith("-"),
                                 "endereco acaba em hifen — sinal de linha truncada")


#: O commit desta missao (15/09): «a fila italiana decidida, e as treze que o
#: atlas nao mostrava». As duas afirmacoes dela — ZERO identidades emitidas e ZERO
#: amostras novas — sao sobre ESTE commit contra o PAI dele, e nao sobre o total de
#: hoje. O total de hoje cresce com cada missao que regista fontes (344 em 23/09),
#: e prende-lo reprovava a missao de 15/09 por trabalho de outras. (A3, 23/09)
COMMIT_DA_MISSAO = "2f0863d1"


def _git_show(ref, caminho):
    import subprocess                                          # noqa: PLC0415
    r = subprocess.run(["git", "show", "%s:%s" % (ref, caminho.replace(os.sep, "/"))],
                       cwd=str(RAIZ), capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _populacao_no_commit(ref):
    """Os SOURCE_ID visiveis naquele commit: o Atlas e o outro emissor, lidos pela
    mesma funcao que le a arvore de hoje (ATLAS.populacao), sobre uma copia temporaria."""
    import shutil                                              # noqa: PLC0415
    import tempfile                                            # noqa: PLC0415
    t = tempfile.mkdtemp(prefix="populacao-")
    try:
        lidos = 0
        for rel in (ATLAS.ATLAS, ATLAS.MASTER_IT):
            b = _git_show(ref, rel)
            if b is not None:
                os.makedirs(os.path.join(t, os.path.dirname(rel)), exist_ok=True)
                with open(os.path.join(t, rel), "wb") as f:
                    f.write(b)
                lidos += 1
        if not lidos:
            raise unittest.SkipTest("sem historia git para %s" % ref)
        return ATLAS.populacao(t, recarregar=True)
    finally:
        shutil.rmtree(t, ignore_errors=True)


def _amostras_no_commit(ref):
    import subprocess                                          # noqa: PLC0415
    r = subprocess.run(["git", "ls-tree", "--name-only", ref,
                        "data/samples/IT-SOURCE-SAMPLES/"], cwd=str(RAIZ),
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise unittest.SkipTest("sem historia git para %s" % ref)
    return set(l for l in r.stdout.splitlines() if l.strip())


class TestAIdentidadeNaoSeMexeu(unittest.TestCase):

    def test_a_populacao_de_source_id_nao_mudou(self):
        """Esta missao registou 13 fontes e emitiu ZERO identidades novas:
        o conjunto de SOURCE_ID no commit dela e o do pai dela, e era 257."""
        na_missao = _populacao_no_commit(COMMIT_DA_MISSAO)
        antes = _populacao_no_commit(COMMIT_DA_MISSAO + "^")
        self.assertEqual(sorted(na_missao - antes), [], "a missao emitiu SOURCE_ID novos")
        self.assertEqual(sorted(antes - na_missao), [], "a missao apagou SOURCE_ID")
        self.assertEqual(len(na_missao), POPULACAO_ESPERADA)

    def test_nenhum_source_id_e_declarado_duas_vezes_no_atlas(self):
        texto = ATLAS_MD.read_text(encoding="utf-8")
        corpo = texto[texto.find(ATLAS.INICIO_DO_REGISTO):]
        vistos, repetidos = set(), []
        for m in re.finditer(r"^#### ((?:EU|FR|ES|IT)-T\d{1,2}-\d{3}) ", corpo, re.M):
            if m.group(1) in vistos:
                repetidos.append(m.group(1))
            vistos.add(m.group(1))
        self.assertEqual(repetidos, [], "ficha duplicada para o mesmo SOURCE_ID")

    def test_as_13_reconciliadas_tem_ficha_e_continuam_no_outro_emissor(self):
        texto = ATLAS_MD.read_text(encoding="utf-8")
        master = (RAIZ / "candidatas" / "ITALY-SOURCE-MASTER-V1.json") \
            .read_text(encoding="utf-8")
        for sid in ("IT-T2-001", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-008",
                    "IT-T3-010", "IT-T3-011", "IT-T5-002", "IT-T5-003", "IT-T7-002",
                    "IT-T9-002", "IT-T9-008", "IT-T10-002"):
            with self.subTest(fonte=sid):
                self.assertIn("#### %s · " % sid, texto, "ficha ausente do atlas")
                self.assertIn(sid, master, "o ID desapareceu do emissor que o cunhou")

    def test_nao_ha_prova_guardada_sem_ficha(self):
        """Se voltar a encher, alguem guardou prova e nao escreveu a ficha."""
        self.assertEqual(REC.orfas(), [], "prova guardada que o atlas nao mostra")


class TestAProvaEBytes(unittest.TestCase):
    """SHA256 declarado e nunca reconferido e' promessa, nao prova."""

    def test_os_23_ficheiros_das_13_reconciliadas_conferem_hoje(self):
        conferidos = 0
        for sid in ("IT-T2-001", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-008",
                    "IT-T3-010", "IT-T3-011", "IT-T5-002", "IT-T5-003", "IT-T7-002",
                    "IT-T9-002", "IT-T9-008", "IT-T10-002"):
            manifesto = json.loads((AMOSTRAS / sid / "MANIFEST.json")
                                   .read_text(encoding="utf-8"))
            for f in manifesto["FILES"]:
                caminho = AMOSTRAS / sid / f["RAW_FILE"]
                with self.subTest(ficheiro="%s/%s" % (sid, f["RAW_FILE"])):
                    self.assertTrue(caminho.is_file(), "ficheiro declarado e ausente")
                    self.assertEqual(
                        hashlib.sha256(caminho.read_bytes()).hexdigest(), f["SHA256"],
                        "os bytes em disco nao sao os que o manifesto declara")
                    conferidos += 1
        self.assertEqual(conferidos, 23)

    def test_o_verdict_das_duas_de_t9_e_yellow_porque_a_prova_e_extrato(self):
        """As duas de T9 nao guardam os bytes servidos. Nao podem ser GREEN."""
        texto = ATLAS_MD.read_text(encoding="utf-8")
        for sid in ("IT-T9-002", "IT-T9-008"):
            with self.subTest(fonte=sid):
                bloco = texto.split("#### %s · " % sid, 1)[1].split("```")[1]
                self.assertIn("YELLOW", bloco)
                self.assertIn("extrato do DOM", bloco)

    def test_uma_das_green_declara_os_bytes_servidos(self):
        texto = ATLAS_MD.read_text(encoding="utf-8")
        bloco = texto.split("#### IT-T2-001 · ", 1)[1].split("```")[1]
        self.assertIn("GREEN", bloco)
        self.assertIn("SHA256 reconferido", bloco)
        self.assertIn("data/samples/IT-SOURCE-SAMPLES/IT-T2-001/MANIFEST.json", bloco)

    def test_a_rota_de_saida_por_vpn_esta_declarada_em_todas_as_13(self):
        """Uma captura por IP italiano de VPN pode nao se repetir de outro IP."""
        texto = ATLAS_MD.read_text(encoding="utf-8")
        for sid in ("IT-T2-001", "IT-T3-011", "IT-T9-008"):
            with self.subTest(fonte=sid):
                bloco = texto.split("#### %s · " % sid, 1)[1].split("```")[1]
                self.assertIn("VPN", bloco.upper())


class TestOPlacarNaoSeContradiz(unittest.TestCase):

    def test_o_total_do_placar_e_a_soma_das_linhas(self):
        texto = ATLAS_MD.read_text(encoding="utf-8")
        linhas = re.findall(r"^\| (EUROPE|FRANCE|SPAIN|ITALY) \| (\d+) \| (\d+) \| "
                            r"(\d+) \| (\d+) \| (\d+) \|$", texto, re.M)
        self.assertEqual(len(linhas), 4, "o placar perdeu uma linha de pais")
        somas = [sum(int(l[i]) for l in linhas) for i in range(1, 6)]
        total = re.search(r"^\| \*\*Total\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| "
                          r"\*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|$",
                          texto, re.M)
        self.assertIsNotNone(total, "a linha Total do placar sumiu")
        self.assertEqual(somas, [int(total.group(i)) for i in range(1, 6)])
        self.assertEqual(somas[0] + somas[1] + somas[2] + somas[3], somas[4],
                         "GREEN+YELLOW+RED+NAO SEI nao da o total da linha")


class TestOLeitorDeXlsxLeAProva(unittest.TestCase):
    """A prova das 381 vive em .xlsx e esta maquina nao tem openpyxl."""

    def test_le_as_folhas_das_duas_pastas_de_prova(self):
        q = XL.folhas(RAIZ / "candidatas" / "ITALY-SOURCE-QUALIFICATION-2026-09-14.xlsx")
        self.assertEqual(q["QUALIFICACAO"], 382)     # 381 linhas + cabecalho
        self.assertEqual(q["REJECT"], 26)
        d = XL.folhas(RAIZ / "candidatas" / "ITALY-SOURCE-DISCOVERY-2026-09-14.xlsx")
        self.assertEqual(d["CADASTRO_FONTES"], 382)

    def test_celula_vazia_devolve_texto_vazio_e_nunca_none(self):
        linhas = XL.tabela(RAIZ / "candidatas" /
                           "ITALY-SOURCE-QUALIFICATION-2026-09-14.xlsx", "QUALIFICACAO")
        self.assertEqual(len(linhas), 381)
        for r in linhas[:50]:
            for k, v in r.items():
                with self.subTest(coluna=k):
                    self.assertIsInstance(v, str)

    def test_folha_inexistente_levanta_em_vez_de_devolver_vazio(self):
        """Devolver [] para folha errada e' o modo de falhar que parece sucesso."""
        with self.assertRaises(KeyError):
            XL.tabela(RAIZ / "candidatas" /
                      "ITALY-SOURCE-QUALIFICATION-2026-09-14.xlsx", "FOLHA_QUE_NAO_EXISTE")


class TestNadaDeColetaAconteceuAqui(unittest.TestCase):

    def test_o_decisor_nao_importa_rede(self):
        codigo = (RAIZ / "candidatas" / "decidir_fila_italia.py").read_text(
            encoding="utf-8")
        # Corta o cabecalho de documentacao: a palavra HTTP aparece la a
        # DESCREVER a sonda de outra missao, e proibir a palavra proibiria
        # tambem explicar porque nao se coletou.
        corpo = codigo.split('"""', 2)[-1]
        for proibido in ("import requests", "import urllib", "import http.client",
                         "urlopen", "socket."):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, corpo)

    def test_a_pasta_de_amostras_nao_cresceu_nesta_missao(self):
        """13 fichas novas e ZERO amostras novas: a prova ja estava toda ca.
        A pasta no commit da missao e a mesma do pai dela (155 ficheiros)."""
        na_missao = _amostras_no_commit(COMMIT_DA_MISSAO)
        antes = _amostras_no_commit(COMMIT_DA_MISSAO + "^")
        self.assertEqual(sorted(na_missao - antes), [], "a missao acrescentou amostras")
        self.assertEqual(len(na_missao), 155)


class TestCorrerDuasVezesNaoInventaAvistamentos(unittest.TestCase):
    """Decidir sobre uma candidata nao e' ter visto a candidata."""

    def test_nenhuma_linha_da_fila_foi_avistada_pelo_decisor(self):
        for c in _fila()["CANDIDATAS"]:
            vistas = c.get("VISTA_TAMBEM_POR") or []
            with self.subTest(candidata=c["NOME"][:40]):
                for v in vistas:
                    self.assertNotIn("decidir_fila_italia", v.get("quem", ""),
                                     "o decisor carimbou um avistamento que nunca "
                                     "aconteceu — ele le' folha de calculo, nao fontes")

    def test_o_decisor_so_bate_a_porta_para_quem_ainda_nao_esta_na_fila(self):
        codigo = (RAIZ / "candidatas" / "decidir_fila_italia.py").read_text(
            encoding="utf-8")
        self.assertIn("if normalizar(d[\"URL\"]) in ja_na_fila:", codigo,
                      "sem esta guarda, cada re-corrida acrescenta 241 avistamentos "
                      "falsos e o ficheiro cresce sem nada mudar")


if __name__ == "__main__":
    unittest.main(verbosity=2)
