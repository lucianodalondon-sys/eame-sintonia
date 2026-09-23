#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS DUAS PORTAS DO SCRAP — o PEDIDO e a OPERAÇÃO não podem discordar.

    py -m unittest tests.test_as_duas_portas_do_scrap

Uma capability ligada à Collection passa por DUAS portas, e cada uma tem o seu
dono:

    PORTA DO PEDIDO    `coleta/scrap_colheita.py::FASES/NOMEADOS`
                       + `pedido/receitas.py::serve_fases`
    PORTA OPERACIONAL  `.github/workflows/*.yml` — o `case` que escolhe o que
                       corre, e o `recusar` que diz que não

Elas já discordaram, e as duas maneiras de discordar foram medidas:

    · fase que existe em `FASES` e não está em `serve_fases` → o orquestrador
      não a sabe pedir: silêncio, zero objetos, sem erro (§154);
    · fase que existe nas duas e não tem ramo no workflow → `FASE_DESCONHECIDA`
      (exit 2): o caminho existe e ninguém o pode disparar de CI;
    · ramo que RECUSA uma fase que a matriz permite → a recusa é texto datado,
      e envelhece mais depressa do que a decisão (era o caso de
      `yt-alvos|yt-transcrever`).

    DUAS PORTAS A DISCORDAR SOBRE A MESMA ROTA É DEFEITO, NÃO POLÍTICA.

O QUE ESTE FICHEIRO PROVA
--------------------------
1. toda fase do PEDIDO tem ramo na porta operacional (nenhuma cai no `*)`);
2. a MATRIZ manda nas duas: fase cuja rota a matriz permite entra por ramo
   canónico; fase cuja rota a matriz recusa tem ramo de RECUSA — e o motivo
   cita o nome que a matriz deu (`ROUTE_NOT_ALLOWED`), não um sinónimo;
3. `yt-legendas` continua recusada E a matriz continua a recusar o `timedtext`
   (a recusa e a lei apontam para o mesmo lado);
4. nenhuma recusa repete o texto datado que dizia «a matriz nao declara
   capacidade de BYTES para YOUTUBE» — falso desde 2026-09-19;
5. a chave da API oficial entra SÓ nas fases cujo adaptador a lê — derivado do
   REGISTO (o dono), nunca de uma lista escrita à mão neste teste;
6. o `CHECK` não discorda da matriz (SOC1): nunca diz que consegue o que a
   matriz recusa, e nunca recusa por política o que a matriz permite;
7. o `DOCUMENT_ID` que o CONTRATO declara é materializado — e, quando o molde
   não fecha, continua `NAO SEI` com o motivo escrito.

Estas provas leem o YAML e o registo — a ESTRUTURA. A prova de execução de uma
fase é a corrida real, que exige o runner e não cabe num unittest.
"""
import io
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ("coleta", "leis", "ferramentas", "regras", "pedido", "orquestrador"):
    sys.path.insert(0, os.path.join(RAIZ, _g))
sys.path.insert(0, RAIZ)

import contratos_de_fonte as cf          # noqa: E402
import scrap_capacidades as cap          # noqa: E402
import scrap_colheita as SC              # noqa: E402
import scrap_executor as sx              # noqa: E402
import scrap_registo as reg              # noqa: E402
import social_matriz as mz               # noqa: E402

WF = os.path.join(RAIZ, ".github", "workflows", "sintonia-scrap.yml")

#: O texto datado que este ficheiro existe para não deixar voltar. Ele dizia
#: que a matriz não declara capacidade de BYTES para o YouTube — e a matriz
#: declara `FETCH_AUDIO_BYTES` (PERMITIDA=SIM, decisão do dono) desde
#: 2026-09-19. Uma recusa com este texto dentro é uma afirmação falsa assinada
#: pela casa.
TEXTO_DATADO = "nao declara capacidade de BYTES"

#: O nome do dono da política. Não se escreve o valor à mão em sítio nenhum
#: deste ficheiro: ele é lido de `leis/social_matriz.py`.
RECUSA_DA_MATRIZ = mz.NAO_PERMITIDA


def _texto():
    with io.open(WF, encoding="utf-8") as f:
        return f.read()


def _yaml():
    import yaml
    return yaml.safe_load(_texto())


def _passos():
    return _yaml()["jobs"]["coleta"]["steps"]


def _passo(prefixo):
    for s in _passos():
        if str(s.get("name", "")).startswith(prefixo):
            return s
    raise AssertionError("passo «%s» nao existe no workflow" % prefixo)


def _ramos(corpo):
    """`{fase: (tipo, corpo)}` — o `case` da porta operacional, lido.

    `tipo` ∈ CANONICO (entra pelo orquestrador) · RECUSA (`recusar`) · OUTRO
    (roda uma implementação que não é Collection, como `yt-alvos`).
    """
    m = re.search(r"\bcase\s+\"\$\{\{\s*inputs\.fase\s*\}\}\"\s+in\n(.*?)\nesac",
                  corpo, re.S)
    assert m, "o case da porta operacional nao foi encontrado"
    dentro = m.group(1)
    fora = {}
    cortes = [(x.start(), x.group(1)) for x in
              re.finditer(r"^\s+([A-Za-z0-9_|*.-]+)\)\s*$", dentro, re.M)]
    for i, (pos, etiqueta) in enumerate(cortes):
        fim = cortes[i + 1][0] if i + 1 < len(cortes) else len(dentro)
        corpo_ramo = dentro[pos:fim]
        # O ramo de omissao (`*`) nao usa `recusar`: ele escreve
        # `FASE_DESCONHECIDA` e sai com 2. E a mesma resposta, por outra porta.
        if "recusar " in corpo_ramo or ("FASE_DESCONHECIDA" in corpo_ramo
                                        and "exit 2" in corpo_ramo):
            tipo = "RECUSA"
        elif "orquestrador/orquestrador.py" in corpo_ramo:
            tipo = "CANONICO"
        else:
            tipo = "OUTRO"
        for fase in etiqueta.split("|"):
            fora[fase] = (tipo, corpo_ramo)
    return fora


def _ramos_do_workflow():
    return _ramos(_passo("6 ·")["run"])


def _grossa(fase):
    """(plataforma, capacidade, capacidade grossa, decisão da matriz)."""
    plat, capacidade = SC.FASES[fase][0], SC.FASES[fase][1]
    grosso = cap.da_matriz(capacidade)
    return plat, capacidade, grosso, (mz.decisao(plat, grosso) if grosso else None)


class TodaFaseDoPedidoTemRamo(unittest.TestCase):
    """PORTAL 1 · nenhuma fase do pedido cai no `*` (FASE_DESCONHECIDA)."""

    def test_1_nenhuma_fase_do_pedido_cai_no_ramo_de_omissao(self):
        ramos = _ramos_do_workflow()
        soltas = [f for f in sorted(SC.FASES) if f not in ramos]
        self.assertEqual([], soltas,
                         "estas fases existem no PEDIDO e nao tem ramo na "
                         "porta operacional: %s" % ", ".join(soltas))

    def test_2_o_ramo_de_omissao_continua_a_recusar(self):
        """O `*)` não pode voltar a aceitar o que ninguém listou."""
        tipo, corpo = _ramos_do_workflow()["*"]
        self.assertEqual("RECUSA", tipo)
        self.assertIn("FASE_DESCONHECIDA", corpo)
        self.assertIn("exit 2", corpo)


class AMatrizMandaNasDuasPortas(unittest.TestCase):
    """PORTAL 2 · o que a matriz permite entra; o que ela recusa, não entra."""

    def test_3_fase_permitida_entra_pela_porta_canonica(self):
        ramos = _ramos_do_workflow()
        for fase in sorted(SC.FASES):
            _plat, _c, _g, d = _grossa(fase)
            if not d or d["DECISAO"] != mz.PERMITIDA_SIM:
                continue
            self.assertEqual(
                "CANONICO", ramos[fase][0],
                "a matriz PERMITE %s e a porta operacional nao a manda ao "
                "orquestrador" % fase)

    def test_4_fase_recusada_pela_matriz_tem_ramo_de_recusa(self):
        ramos = _ramos_do_workflow()
        for fase in sorted(SC.FASES):
            plat, capacidade, grosso, d = _grossa(fase)
            if not d or d["DECISAO"] != RECUSA_DA_MATRIZ:
                continue
            tipo, corpo = ramos[fase]
            self.assertEqual(
                "RECUSA", tipo,
                "a matriz RECUSA %s (%s/%s) e a porta operacional corre-a na "
                "mesma" % (fase, plat, grosso))
            self.assertIn(grosso, corpo,
                          "a recusa de %s nao nomeia a capacidade grossa que a "
                          "matriz recusou" % fase)
            self.assertIn(RECUSA_DA_MATRIZ, corpo,
                          "a recusa de %s nao usa o NOME que a matriz deu "
                          "(%s) — um sinonimo inventado aqui seria uma segunda "
                          "verdade sobre a mesma politica"
                          % (fase, RECUSA_DA_MATRIZ))

    def test_5_yt_legendas_continua_recusado_e_a_matriz_concorda(self):
        """A recusa e a lei apontam para o mesmo lado — e as duas sobrevivem."""
        tipo, corpo = _ramos_do_workflow()["yt-legendas"]
        self.assertEqual("RECUSA", tipo)
        self.assertIn("timedtext", corpo)
        rotas = [r for r in mz.MATRIZ["YOUTUBE"]["FETCH_TRANSCRIPT"]
                 if r["ROTA"] == "timedtext"]
        self.assertEqual(1, len(rotas), "a matriz deixou de declarar timedtext")
        self.assertNotEqual(mz.PERMITIDA_SIM, rotas[0]["PERMITIDA"])
        self.assertEqual("ROUTE_NOT_ALLOWED", rotas[0]["ESTADO"])

    def test_6_nenhuma_recusa_repete_o_texto_datado(self):
        for fase, (tipo, corpo) in sorted(_ramos_do_workflow().items()):
            if tipo != "RECUSA":
                continue
            self.assertNotIn(
                TEXTO_DATADO, corpo,
                "a recusa de %s voltou a afirmar que a matriz nao declara "
                "capacidade de BYTES para o YOUTUBE — falso desde 2026-09-19"
                % fase)

    def test_7_o_audio_do_youtube_tem_porta_e_nao_recusa(self):
        """A decisão do dono (D17.4) chega à porta operacional, pelo nome."""
        tipo, corpo = _ramos_do_workflow()["audio-youtube"]
        self.assertEqual("CANONICO", tipo)
        self.assertIn("--filtro video=", corpo)
        d = mz.decisao("YOUTUBE", "FETCH_AUDIO_BYTES")
        self.assertEqual(mz.PERMITIDA_SIM, d["DECISAO"])
        self.assertEqual("yt-dlp:public_audio", d["ROTA"])


class AChaveEntraSoOndeEUsada(unittest.TestCase):
    """PORTAL 3 · a credencial entra nas fases cujo adaptador a lê — e só nelas.

    A lista NÃO se escreve aqui: ela é derivada do REGISTO. Quem sabe se uma
    fase precisa da chave é a sonda do adaptador que a serve, e é ela que se lê.

        UM SEGREDO SÓ ENTRA ONDE É NECESSÁRIO.
    """

    def _fases_que_leem_a_chave(self):
        reg.carregar_adaptadores()
        import adaptador_youtube as ay
        fora = set()
        for fase in SC.FASES:
            plat, capacidade = SC.FASES[fase][0], SC.FASES[fase][1]
            r = reg.adaptador_de(plat, capacidade) or {}
            if r.get("PRONTO") is ay.pronto_para_api:
                fora.add(fase)
        return fora

    def test_8_a_lista_do_workflow_e_a_do_registo(self):
        esperado = self._fases_que_leem_a_chave()
        self.assertTrue(esperado, "nenhuma fase le a chave — a medicao falhou")
        env = _passo("6 ·").get("env") or {}
        import youtube_oficial as yt
        self.assertIn(yt.ENV_CHAVE, env,
                      "a chave que o dono le (%s) nao entra na porta "
                      "operacional" % yt.ENV_CHAVE)
        expr = str(env[yt.ENV_CHAVE])
        dentro = set(re.findall(r'"([a-z0-9-]+)"', expr))
        self.assertEqual(esperado, dentro,
                         "a porta operacional da a chave a fases que nao a "
                         "leem, ou a nega a quem a le. registo=%s · workflow=%s"
                         % (sorted(esperado), sorted(dentro)))

    def test_9_a_chave_nao_entra_no_audio_local(self):
        """`audio-youtube` é rota local: dar-lhe a chave seria alargar a
        superfície de um segredo a quem não o usa."""
        self.assertNotIn("audio-youtube", self._fases_que_leem_a_chave())
        env = _passo("6 ·").get("env") or {}
        expr = str(list(env.values())[0])
        self.assertNotIn('"audio-youtube"', expr)


class OCheckNaoDiscordaDaMatriz(unittest.TestCase):
    """SOC1 · o portão do executor consulta a lei, e o nome do estado é dela.

        CHECK('INSTAGRAM','instagram.reel.transcribe') -> CAN_COLLECT_NOW
        mz.decisao('INSTAGRAM','FETCH_TRANSCRIPT')     -> ROUTE_NOT_ALLOWED

    As duas linhas eram verdade ao mesmo tempo no HEAD de 2026-09-23. O
    roteador consultava a matriz e recusava — nada saía — mas o PORTÃO dizia
    que sim, e um portão que diz sim a quem a lei recusa não é um portão.
    """

    def test_10_o_check_nunca_diz_que_consegue_o_que_a_matriz_recusa(self):
        reg.carregar_adaptadores()
        medidos = 0
        for nome, (plat, _e, _a, _p, _pr, grosso) in sorted(cap.DECLARADAS.items()):
            if not grosso:
                continue
            d = mz.decisao(plat, grosso)
            if d["DECISAO"] != RECUSA_DA_MATRIZ:
                continue
            v = sx.CHECK(plat, nome)
            self.assertFalse(v["CAN"],
                             "%s/%s: a matriz recusa (%s) e o CHECK diz que "
                             "consegue" % (plat, nome, d["DECISAO"]))
            medidos += 1
        self.assertGreater(medidos, 0, "nenhuma capacidade recusada — medicao vazia")

    def test_10b_quando_a_politica_e_quem_fecha_o_nome_e_o_da_matriz(self):
        """Dois portões em série, e o NOME de quem fechou diz qual foi.

        Se o estado medido não promete, quem fecha é o portão do estado
        (`CAPABILITY_STATE_PROMISES_NOTHING`) — e isso é a resposta certa, não
        um defeito. Mas quando a capacidade promete resultado E tem caminho,
        não sobra portão nenhum antes da política: aí o estado tem de ser o
        NOME do dono da política, e não um sinónimo inventado aqui.
        """
        reg.carregar_adaptadores()
        medidos = 0
        for nome, (plat, _e, _a, _p, _pr, grosso) in sorted(cap.DECLARADAS.items()):
            if not grosso:
                continue
            if mz.decisao(plat, grosso)["DECISAO"] != RECUSA_DA_MATRIZ:
                continue
            if not (cap.promete_resultado(nome) and reg.tem_caminho(plat, nome)):
                continue
            v = sx.CHECK(plat, nome)
            self.assertEqual(RECUSA_DA_MATRIZ, v["STATE"],
                             "%s/%s: o estado do CHECK tem de ser o NOME do "
                             "dono da politica" % (plat, nome))
            self.assertIn(grosso, v["WHY"])
            medidos += 1
        self.assertGreater(medidos, 0)

    def test_11_o_check_nunca_recusa_por_politica_o_que_a_matriz_permite(self):
        reg.carregar_adaptadores()
        for nome, (plat, _e, _a, _p, _pr, grosso) in sorted(cap.DECLARADAS.items()):
            if not grosso:
                continue
            d = mz.decisao(plat, grosso)
            if d["DECISAO"] != mz.PERMITIDA_SIM:
                continue
            v = sx.CHECK(plat, nome)
            self.assertNotEqual(
                RECUSA_DA_MATRIZ, v["STATE"],
                "%s/%s: a matriz PERMITE e o CHECK recusa por politica"
                % (plat, nome))

    def test_12_o_check_expoe_a_decisao_da_matriz(self):
        """Expor não é decorar: sem os três campos, um leitor por máquina lê o
        `CAN` e não sabe QUE lei estava em vigor quando ele foi escrito."""
        reg.carregar_adaptadores()
        vistos = 0
        for nome, (plat, _e, _a, _p, _pr, grosso) in sorted(cap.DECLARADAS.items()):
            if not grosso:
                continue
            v = sx.CHECK(plat, nome)
            for campo in ("MATRIZ_CAPABILITY", "MATRIZ_DECISAO",
                          "MATRIZ_PORQUE", "MATRIZ_ROTA"):
                self.assertIn(campo, v, "%s/%s sem %s" % (plat, nome, campo))
            self.assertEqual(grosso, v["MATRIZ_CAPABILITY"])
            self.assertEqual(mz.decisao(plat, grosso)["DECISAO"],
                             v["MATRIZ_DECISAO"])
            vistos += 1
        self.assertGreater(vistos, 0)

    def test_13_a_decisao_da_matriz_chega_ao_collect_sem_abrir_corrida(self):
        """A recusa acontece no PORTÃO — antes de RUN, checkpoint e etapa."""
        objetos, trace = sx.COLLECT(platform="INSTAGRAM",
                                    capability="instagram.profile.discovery",
                                    run_id="DUAS-PORTAS")
        self.assertEqual([], objetos)
        self.assertEqual(RECUSA_DA_MATRIZ, trace.get("RESULT"))
        self.assertEqual(RECUSA_DA_MATRIZ, trace["CHECK"]["STATE"])


class ODocumentIdVemDoContrato(unittest.TestCase):
    """PORTAL 4 · a identidade que o CONTRATO declara é materializada.

        regras/italy_contracts.mjs::IT-T8-001
            DOCUMENT_ID_RULE = "AGRONOTIZIE:YT:{VIDEO_ID}  —  o video_id …"

    E `scrap_colheita.unidade()` respondia `NAO SEI` a todos, porque nenhum
    owner materializava a regra. Não era honestidade: era identidade por ligar.
    """

    FONTE = "IT-T8-001"
    VIDEO = "7Ps4g3juOIU"

    def _objeto(self, **muda):
        o = {"OBJECT_KIND": "PUBLIC_AUDIO", "MEDIA_KIND": "AUDIO",
             "VIDEO_ID": self.VIDEO,
             "SOURCE_URL": "https://www.youtube.com/watch?v=%s" % self.VIDEO,
             "CONTENT_TYPE": "audio/wav",
             "AUDIO_REFERENCE": "/tmp/nao-existe.wav"}
        o.update(muda)
        return o

    def test_14_o_contrato_declara_o_molde_e_o_owner_le(self):
        regra = cf.regra_do_documento(self.FONTE)
        self.assertIn("{VIDEO_ID}", regra)
        self.assertEqual("AGRONOTIZIE:YT:{VIDEO_ID}", cf.molde_do_documento(self.FONTE))

    def test_15_a_unidade_materializa_o_document_id(self):
        u = SC.unidade(self._objeto(), run_id="DUAS-PORTAS", fonte=self.FONTE)
        self.assertEqual("AGRONOTIZIE:YT:%s" % self.VIDEO, u["DOCUMENT_ID"])
        self.assertIn("MATERIALIZADO_PELO_CONTRATO_DE_FONTE", u["DOCUMENT_ID_BASE"])

    def test_16_sem_o_valor_o_document_id_continua_NAO_SEI_com_motivo(self):
        """Molde que não fecha não devolve meio id: devolve NÃO SEI e diz qual
        falta. Meio id entra no acervo com a cara de facto."""
        u = SC.unidade(self._objeto(VIDEO_ID=None), run_id="X", fonte=self.FONTE)
        self.assertEqual("NAO SEI", u["DOCUMENT_ID"])
        self.assertIn("MOLDE_INCOMPLETO", u["DOCUMENT_ID_BASE"])
        self.assertIn("VIDEO_ID", u["DOCUMENT_ID_BASE"])

    def test_17_uma_confissao_nao_preenche_um_molde(self):
        """`VIDEO_ID = NAO SEI` produziria `AGRONOTIZIE:YT:NAO SEI` — um id
        fabricado com a cara de dado."""
        u = SC.unidade(self._objeto(VIDEO_ID="NAO SEI"), run_id="X",
                       fonte=self.FONTE)
        self.assertEqual("NAO SEI", u["DOCUMENT_ID"])

    def test_18_o_id_nao_vem_do_sha_nem_do_caminho_nem_da_url(self):
        o = self._objeto()
        u = SC.unidade(o, run_id="X", fonte=self.FONTE)
        self.assertNotIn("AUDIO_REFERENCE", u["DOCUMENT_ID"])
        self.assertNotIn("youtube.com", u["DOCUMENT_ID"])
        self.assertNotIn("wav", u["DOCUMENT_ID"])

    def test_19_a_fonte_sem_regra_continua_NAO_SEI(self):
        u = SC.unidade(self._objeto(), run_id="X", fonte="IT-NAO-EXISTE-999")
        self.assertEqual("NAO SEI", u["DOCUMENT_ID"])
        self.assertIn("nao declara DOCUMENT_ID_RULE", u["DOCUMENT_ID_BASE"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
