#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS DOZE PROVAS DA ATOMICIDADE — P1 a P12 de C-INT-ATOMICITY-01.

    python3 -m unittest tests.test_atomicidade_da_intelligence -v

Estas provas só são possíveis **nesta árvore**. Na branch onde a espinha nasceu,
metade delas não tinha ficheiro para abrir — e foi exactamente por isso que a
arbitragem anterior mediu bem e concluiu mal.

    O QUE ESTAS PROVAS GUARDAM
    --------------------------
    Que as autoridades coexistem, que cada uma tem UM caminho, que os
    contratos declarados batem com o codigo real, e que a integracao nao
    tocou runtime de Collection.

    O QUE ELAS NAO PROVAM
    ---------------------
    Que a Intelligence funciona. INTELLIGENCE_RUNTIME_IMPLEMENTED = NO.
"""
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "provas"))

import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
from arbitragem_da_intelligence import AUTORIDADES, medir  # noqa: E402

#: ⚠️ SAO DUAS PERGUNTAS, E ATE 2026-09-15 PARTILHAVAM UMA CONSTANTE SO.
#:
#:   1. «os CINCO commits de integracao so ACRESCENTARAM?» — um facto
#:      HISTORICO, sobre um intervalo fechado que nao volta a mudar. Mede-se
#:      de `TRONCO` a `FIM_DA_INTEGRACAO`, e esses dois nunca mais se mexem.
#:   2. «a Intelligence tocou Collection, migrations ou Portal?» — uma
#:      pergunta sobre HOJE, cujo denominador e o tronco em que esta linha
#:      assenta AGORA.
#:
#: Enquanto a Intelligence viveu no mesmo tronco, as duas respostas vinham do
#: mesmo commit e ninguem reparou que eram duas perguntas. A reconciliacao com
#: `claude/it-trunk-v1` afastou-as: medir a pergunta 2 contra `dc00583d`
#: passou a somar o trabalho INTEIRO do trunk ao que a prova chama «a
#: integracao tocou» — 22 ficheiros de Collection, 2 migrations e 29 do
#: Portal, nenhum deles escrito pela Intelligence. E `dc00583d` ja nem e
#: ancestral do trunk de hoje: as duas linhas divergiram, e a prova estava a
#: comparar duas casas em vez de dois dias.
#:
#:     UM DIFF CONTRA O TRONCO ERRADO NAO MEDE O QUE EU FIZ.
#:     MEDE O QUE ACONTECEU NO MUNDO DESDE QUE EU SAI DE CASA.
#:
#: Apontar ambas ao mesmo commit fazia uma mentir sempre que a outra ficasse
#: certa. Ficam separadas, com nome proprio.
#:
#:     DUAS PERGUNTAS COM DENOMINADORES DIFERENTES NAO PARTILHAM UMA CONSTANTE.

#: O tronco de onde a integracao das autoridades partiu. Historico, fixo.
TRONCO = "dc00583d01ac6312fa6fa83195d936199eaa3d12"

#: O tronco em que esta linha assenta HOJE, depois da reconciliacao com
#: `claude/it-trunk-v1`. Contra ele, as tres provas voltam a dizer o que sempre
#: quiseram dizer, e desta vez e verdade medida: zero ficheiros de Collection,
#: zero migrations, zero do Portal.
TRONCO_ACTUAL = "43553a651f8c330512c5989a78bc796739659331"

#: O ultimo dos cinco commits que trouxeram autoridades. Ate aqui, so pode
#: haver ficheiros ACRESCENTADOS — e e o que a prova mede.
FIM_DA_INTEGRACAO = "a8b56448009661c12216d265465d02289c15c8e0"


def git(*a):
    """⚠️ `encoding` EXPLICITO, E NAO O DA MAQUINA.

    Com `text=True` sozinho, o Python descodifica a saida do git na codificacao
    default do sistema — `cp1252` no Windows. O repositorio escreve UTF-8 (os
    nomes das pecas do mapa levam acento e emoji), e a leitura rebentava com
    `UnicodeDecodeError` a meio do diff do espelho. Nao era uma prova a
    reprovar: era a prova a nao conseguir correr, nesta maquina, sempre.

        UM TESTE QUE SO FALHA NUM SISTEMA OPERATIVO NAO ESTA A MEDIR O CODIGO.
    """
    return subprocess.check_output(["git"] + list(a), cwd=RAIZ, text=True,
                                   encoding="utf-8", errors="replace",
                                   stderr=subprocess.DEVNULL)


def ficheiro(*p):
    return os.path.join(RAIZ, *p)


class P1_TodasAsAutoridadesNaMesmaArvore(unittest.TestCase):
    """P1 · todas as autoridades existem na mesma árvore."""

    def test_as_quinze_autoridades_abrem(self):
        ausentes = {k: v for k, v in AUTORIDADES.items()
                    if not os.path.exists(ficheiro(v))}
        self.assertEqual({}, ausentes,
                         "CONTROL_PLANE_ATOMICITY = FAIL: %s" % sorted(ausentes))

    def test_as_seis_frentes_coexistem(self):
        """As seis que nenhum commit continha ao mesmo tempo, em 2026-09-14."""
        for nome in ("BIBLIA_INTELLIGENCE_V0.2", "MOTOR_V2_REQUISITOS",
                     "ARBITRAGEM_V1", "AUTHORITY_REGISTRY", "BENCHMARK_AGRO",
                     "KNOW_HOW_CANONICO"):
            self.assertTrue(os.path.exists(ficheiro(AUTORIDADES[nome])), nome)

    def test_a_medicao_declara_a_fotografia_em_que_correu(self):
        """Um censo sem fotografia declarada é um número sem denominador."""
        r = medir()
        self.assertIn("COMMIT", r["FOTOGRAFIA"])
        self.assertEqual("false", r["FOTOGRAFIA"]["SHALLOW"],
                         "árvore truncada: merge-base e grep mentem aqui")
        self.assertEqual("PASS", r["CONTROL_PLANE_ATOMICITY"])


class P2_UmCaminhoPorAutoridade(unittest.TestCase):
    """P2 · cada autoridade tem exatamente um caminho/owner reconhecido."""

    def test_ha_um_so_know_how(self):
        achados = [l for l in git("ls-files").splitlines()
                   if os.path.basename(l).upper().startswith("SINTONIA-EAME-KNOW-HOW")]
        self.assertEqual(["SINTONIA-EAME-KNOW-HOW.md"], achados,
                         "mais de um know-how na árvore: %s" % achados)

    def test_nao_ha_know_how_v2_master_nem_final(self):
        """⚠️ O alvo e o DOCUMENTO canonico, nao qualquer ficheiro dentro de
        `know-how/`. `SYNTHETIC-CENSUS-FINAL-CLOSURE.md` tem «FINAL» no nome e
        e uma peca legitima de censo — apanha-la seria medir a palavra em vez
        do conceito."""
        proibidos = [l for l in git("ls-files").splitlines()
                     if os.path.basename(l).upper().startswith("SINTONIA-EAME-KNOW-HOW")
                     and l != "SINTONIA-EAME-KNOW-HOW.md"]
        self.assertEqual([], proibidos, "know-how concorrente: %s" % proibidos)

    def test_ha_uma_so_biblia_por_dominio(self):
        biblias = sorted(l for l in git("ls-files").splitlines()
                         if os.path.basename(l).startswith("BIBLIA-")
                         and l.endswith(".md"))
        self.assertEqual(
            ["BIBLIA-CANONICA-DA-COLETA.md",
             "BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md"], biblias,
            "uma Bíblia por domínio, e só uma: %s" % biblias)

    def test_o_registo_de_autoridades_aponta_para_caminhos_que_existem(self):
        reg = json.load(open(ficheiro("controle/AUTORIDADES-CANONICAS.json"),
                             encoding="utf-8"))
        # ⚠️ Nem toda a autoridade do registo vive nesta arvore — algumas sao
        # ponteiros e outras estao declaradas noutras frentes. O que esta prova
        # exige e das DUAS da Intelligence que esta missao integrou.
        alvo = {"A-BIBLIA-ENG-INTELIGENCIA", "A-MOTOR-V2-REQUISITOS"}
        vistos = set()
        for a in reg["AUTHORITIES"]:
            if a["CARD_ID"] in alvo:
                vistos.add(a["CARD_ID"])
                self.assertTrue(
                    os.path.exists(ficheiro(a["CANONICAL_PATH"])),
                    "%s aponta para %s, que nao existe nesta arvore"
                    % (a["CARD_ID"], a["CANONICAL_PATH"]))
        self.assertEqual(alvo, vistos, "autoridade da Intelligence fora do registo")


class P3_ArbitragemCorreContraEstaArvore(unittest.TestCase):
    """P3 · a arbitragem roda contra a árvore integrada."""

    def test_a_re_arbitragem_corre_e_nao_encontra_conflito_de_dono(self):
        r = medir()
        conflitos = {k: v for k, v in r["CONCEITOS"].items()
                     if v["VERDICT"] == "CONFLICT"}
        self.assertEqual({}, conflitos, "conflito de dono: %s" % sorted(conflitos))

    def test_todo_modulo_dono_declarado_existe(self):
        r = medir()
        for nome, c in r["CONCEITOS"].items():
            if c["MODULO_DONO"]:
                self.assertTrue(c["MODULO_EXISTE"],
                                "%s aponta para %s, ausente" % (nome, c["MODULO_DONO"]))

    def test_o_resultado_escrito_bate_com_a_medicao_de_agora(self):
        """O resultado gravado não pode envelhecer em silêncio.

        ⚠️ Aponta para o V3 desde C-INT-NIGHT-01. O V2 ficou como a medição
        ANTES da decisão humana A/A, e `test_o_V2_fica_como_historia_e_nao_foi
        _reescrito` guarda-o nesse estado. O ficheiro VIVO é sempre o último.
        """
        p = ficheiro("docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json")
        gravado = json.load(open(p, encoding="utf-8"))
        agora = medir()
        self.assertEqual(sorted(gravado["CONCEITOS"]), sorted(agora["CONCEITOS"]))
        for k in agora["CONCEITOS"]:
            self.assertEqual(gravado["CONCEITOS"][k]["OWNER"],
                             agora["CONCEITOS"][k]["OWNER"], k)
            self.assertEqual(gravado["CONCEITOS"][k]["VERDICT"],
                             agora["CONCEITOS"][k]["VERDICT"], k)


class P4_CollectionGapNaoVoltaAFundirDoisDonos(unittest.TestCase):
    """P4 · `COLLECTION_GAP` não volta a fundir dois owners.

    O caso testemunha do enunciado, medido contra a árvore completa — que é
    onde a hipótese podia morrer, e não morreu.
    """

    VOCABULARIO_DA_COLLECTION = ("GAP_ID", "SATISFACTION_STATE", "COLLECT_NOW",
                                 "DO_NOT_COLLECT", "DEFER_UNKNOWN")

    def test_o_dono_do_gap_e_a_lei_da_gestao_da_coleta(self):
        import gestao_da_coleta as g
        self.assertEqual("GESTAO_DA_COLETA/v1", g.CONTRATO)
        self.assertIn("GAP_ID", g.CAMPOS_DA_FALTA)
        self.assertIn("SATISFACTION_STATE", g.CAMPOS_DA_FALTA)
        self.assertIn("COLLECT_NOW", g.DECISOES)

    def test_a_intelligence_nao_escreve_gap_decisao_nem_rota(self):
        for t in self.VOCABULARIO_DA_COLLECTION:
            try:
                saida = git("grep", "-l", "-I", "--", t, "--", "motor", "superficie")
            except subprocess.CalledProcessError:
                saida = ""
            self.assertEqual("", saida.strip(),
                             "a camada Intelligence toca %s em: %s" % (t, saida))

    def test_a_espinha_recusa_o_vocabulario_da_collection_em_codigo(self):
        from espinha_da_intelligence import PALAVRAS_QUE_O_REQUISITO_RECUSA
        for t in ("GAP_ID", "SATISFACTION_STATE", "DECISION", "ROTA", "EXECUTOR"):
            self.assertIn(t, PALAVRAS_QUE_O_REQUISITO_RECUSA)

    def test_o_requisito_da_intelligence_usa_os_campos_que_ja_tem_dono(self):
        """A Intelligence escreve a NECESSIDADE inteira, e nada da FALTA."""
        import gestao_da_coleta as g
        from espinha_da_intelligence import Requisito
        campos = set(Requisito.__dataclass_fields__)
        for c in g.CAMPOS_DA_NECESSIDADE:
            self.assertIn(c, campos,
                          "%s pertence a NECESSIDADE e sumiu do requisito" % c)

    def test_a_costura_entre_os_dois_donos_e_UM_campo_so(self):
        """⚠️ E a propria lei da Collection que a declara.

            CAMPOS_DA_NECESSIDADE ∩ CAMPOS_DA_FALTA = {REQUIREMENT_ID}

        A NECESSIDADE e de quem a declara; a FALTA e de quem a mede; e as duas
        tocam-se num identificador, e so nele. A divisao de `COLLECTION_GAP`
        em dois donos nao foi inventada pela Intelligence: ja estava desenhada
        em `GESTAO_DA_COLETA/v1`, a espera de um declarante que ela nao nomeia.

            UM CONTRATO COM UMA CHAVE ESTRANGEIRA PARA NINGUEM
            ESTA A DESCREVER UM DONO QUE AINDA NAO CHEGOU.
        """
        import gestao_da_coleta as g
        from espinha_da_intelligence import Requisito
        costura = set(g.CAMPOS_DA_NECESSIDADE) & set(g.CAMPOS_DA_FALTA)
        self.assertEqual({"REQUIREMENT_ID"}, costura)
        campos = set(Requisito.__dataclass_fields__)
        self.assertEqual({"REQUIREMENT_ID"}, campos & set(g.CAMPOS_DA_FALTA),
                         "o requisito atravessou a costura e escreveu FALTA")


class P5_P10_AEspinhaSobreviveAArvoreCompleta(unittest.TestCase):
    """P5–P10 · as decisões da espinha, re-medidas contra a árvore completa.

    As provas detalhadas vivem em `tests/test_espinha_da_intelligence.py`.
    Aqui mede-se o que só esta árvore permite: se o contrato COPIADO ainda
    bate com o contrato REAL.
    """

    def test_a_copia_do_contrato_ready_bate_com_o_contrato_real(self):
        """⚠️ A prova central da atomicidade.

        `provas/espinha_da_intelligence.py` traz uma cópia declarada dos 19
        campos de `admissao.pronto_para_inteligencia()`. Na branch onde nasceu,
        `admissao/` não existia e a cópia não tinha contra o que ser conferida.
        Aqui tem.

            UMA COPIA QUE NINGUEM PODE CONFERIR NAO E UMA COPIA: E UMA CRENCA.

        ⚠️ **O UNIVERSO DESTE ITEM ERA `T7`, E ESTAVA ERRADO.** Não é ajuste de
        teste para passar: o texto fala de *ensaio* e *DOI*, que é CIÊNCIA, e
        ciência é `T5` no Atlas — o dono da taxonomia. `T7` é TECHNICAL
        NETWORK. O léxico de ciência vivia em `T7` por uma quarta cópia da
        taxonomia que `admissao/admissao.py` corrigiu, e a porta passou a
        recusar o item **com prova a favor**: «fala claramente de outro
        universo (T5: doi, ensaio)».

            A PORTA NAO FICOU MAIS DURA. O ROTULO E QUE ESTAVA TROCADO.
        """
        from admissao import decidir, pronto_para_inteligencia
        from espinha_da_intelligence import CAMPOS_DO_READY
        item = {"id": "ATOM-1", "texto": "Ensaio de campo publicado com DOI",
                "source_id": "IT-T5-001", "fact_time": "2026-05-02"}
        d = decidir(item, "T5", corrida="atomicidade")
        self.assertEqual("SIM", d.resultado, d.motivo)
        real = pronto_para_inteligencia(item, d)
        self.assertEqual(sorted(CAMPOS_DO_READY), sorted(real),
                         "a copia declarada derivou do contrato real")

    def test_nenhum_campo_agronomico_atravessa_a_fronteira_real(self):
        from admissao import decidir, pronto_para_inteligencia
        from espinha_da_intelligence import CAMPOS_QUE_NAO_ATRAVESSAM
        item = {"id": "ATOM-2", "texto": "Ensaio de campo publicado com DOI",
                "source_id": "IT-T5-001", "fact_time": "2026-05-02",
                "evidence_species": "OBSERVED_FIELD_SIGNAL",
                "method": "inspecao_visual", "denominator": 400}
        d = decidir(item, "T5", corrida="atomicidade")
        self.assertEqual("SIM", d.resultado, d.motivo)
        real = pronto_para_inteligencia(item, d)
        atravessam = sorted(set(CAMPOS_QUE_NAO_ATRAVESSAM) & set(real))
        self.assertEqual([], atravessam,
                         "o bloqueio G0 caiu: %s ja atravessa. Sobe a regua."
                         % atravessam)

    def test_signal_e_finding_continuam_conceitos_diferentes(self):
        r = medir()
        self.assertIn("SIGNAL", r["CONCEITOS"])
        self.assertIn("FINDING / ANALYTIC_JUDGMENT", r["CONCEITOS"])
        self.assertNotEqual(
            r["CONCEITOS"]["SIGNAL"]["CURRENT_IMPLEMENTATION"],
            "IMPLEMENTED",
            "SIGNAL ganhou implementacao sem passar por missao nenhuma")

    def test_o_cruzamento_continua_sem_onde_escrever_julgamento(self):
        from espinha_da_intelligence import Cruzamento
        campos = set(Cruzamento.__dataclass_fields__)
        for proibido in ("APOIA", "CONTRADIZ", "SUPPORTS", "SUFICIENTE",
                         "CONCLUSAO", "VEREDITO"):
            self.assertNotIn(proibido, campos)

    def test_a_fila_de_validacao_continua_a_ser_projecao(self):
        from espinha_da_intelligence import Corrida, Hipotese
        self.assertNotIn("VALIDATION_QUEUE", dir(Corrida))
        self.assertIn("VALIDACAO", Hipotese.__dataclass_fields__,
                      "o estado tem de viver no objeto, nao numa fila")
        self.assertTrue(callable(Corrida.fila_de_validacao))

    def test_a_reversao_continua_a_preservar_historia(self):
        from espinha_da_intelligence import Evento, Historia
        self.assertTrue(Evento.__dataclass_params__.frozen)
        self.assertFalse(any(n in dir(Historia) for n in ("apagar", "editar",
                                                          "remover", "pop")))

    def test_os_dois_dominios_continuam_na_mesma_espinha(self):
        from espinha_da_intelligence import DOMINIOS, PacoteDeDominio
        self.assertEqual({"DOENCA", "REGULATORIO"}, set(DOMINIOS))
        for pacote in DOMINIOS.values():
            self.assertIsInstance(pacote, PacoteDeDominio)
            for valor in vars(pacote).values():
                self.assertFalse(callable(valor))


class P10b_ATravaDaInteligenciaContinuaAMorder(unittest.TestCase):
    """A excepcao que esta missao pediu a trava, paga com prova.

    Dois ficheiros foram declarados `INSTRUMENTOS` em
    `system-map/scripts/censo_do_congelamento.py`. Uma excepcao a um portao de
    outra frente so e legitima se for ESTREITA e VERIFICAVEL — senao e uma
    porta.

        UMA EXCEPCAO SEM PROVA E UM BURACO COM COMENTARIO BONITO.
    """

    #: A pergunta que `_especie` diz fazer: «este ficheiro CALCULA sinal, nota
    #: ou recomendacao?». Estes sao os verbos de quem calcula.
    VERBOS_DE_CALCULO = ("score", "pontuacao", "ranking", "recomend",
                         "priorizar", "classificar_sinal")

    def test_o_instrumento_de_arbitragem_nao_calcula_sinal_nota_nem_recomendacao(self):
        import arbitragem_da_intelligence as a
        publico = [n for n in dir(a) if not n.startswith("_") and callable(getattr(a, n))]
        for nome in publico:
            for verbo in self.VERBOS_DE_CALCULO:
                self.assertNotIn(verbo, nome.lower(),
                                 "o instrumento ganhou um calculo: %s" % nome)
        # e o que ele devolve e contagem, nunca juizo sobre o mundo
        r = a.medir()
        for c in r["CONCEITOS"].values():
            self.assertIsInstance(c["FICHEIROS_QUE_TOCAM"], int)
            self.assertNotIn("SCORE", c)
            self.assertNotIn("CONFIDENCE", c)

    def test_o_registo_de_autoridades_nao_carrega_dado_de_inteligencia(self):
        """Governanca diz QUEM manda, nunca O QUE foi descoberto."""
        reg = json.load(open(ficheiro("controle/AUTORIDADES-CANONICAS.json"),
                             encoding="utf-8"))
        for a in reg["AUTHORITIES"]:
            for proibido in ("SIGNAL_ID", "FINDING_ID", "OPPORTUNITY_ID",
                             "CROSSING_ID", "SCORE"):
                self.assertNotIn(proibido, json.dumps(a, ensure_ascii=False),
                                 "%s carrega dado de inteligencia" % a["CARD_ID"])

    def test_a_lista_de_instrumentos_continua_curta_e_declarada(self):
        """Qualquer nome a mais aparece no diff — e e essa a unica guarda."""
        sys.path.insert(0, ficheiro("system-map", "scripts"))
        import censo_do_congelamento as c
        self.assertEqual(6, len(c.INSTRUMENTOS),
                         "a lista de instrumentos cresceu: %s" % (c.INSTRUMENTOS,))
        self.assertIn("provas/arbitragem_da_intelligence.py", c.INSTRUMENTOS)
        self.assertIn("controle/AUTORIDADES-CANONICAS.json", c.INSTRUMENTOS)

    def test_a_espinha_NAO_pediu_excepcao_nenhuma(self):
        """⚠️ E a parte que mais importa: a maquina de estados continua debaixo
        da trava. Se ela avancar, a trava morde — e e para isso que ela existe.
        """
        sys.path.insert(0, ficheiro("system-map", "scripts"))
        import censo_do_congelamento as c
        self.assertNotIn("provas/espinha_da_intelligence.py", c.INSTRUMENTOS)


class P11_OSystemMapObservaAsAutoridades(unittest.TestCase):
    """P11 · o System Map consegue observar as autoridades integradas."""

    def test_o_mapa_tem_cadeia_canonica_nesta_arvore(self):
        self.assertTrue(os.path.exists(ficheiro("system-map", "data")))
        self.assertTrue(os.path.exists(ficheiro("system-map", "scripts")))

    def test_o_censo_do_controle_le_o_registo_integrado(self):
        """O portão do controle existe e aponta para o registo que integrámos."""
        self.assertTrue(os.path.exists(ficheiro("controle/censo_do_controle.py")))
        self.assertTrue(os.path.exists(ficheiro("controle/portao_do_controle.py")))
        self.assertTrue(os.path.exists(ficheiro("controle/AUTORIDADES-CANONICAS.json")))

    def test_nenhum_documento_diz_IMPLEMENTED_onde_so_ha_contrato(self):
        """⚠️ Ataque 11 do red team, guardado.

        O V2 e a única fonte do estado; ele deriva `IMPLEMENTED` só de módulo
        que existe. Um conceito sem módulo nunca pode sair daqui implementado.
        """
        r = medir()
        for nome, c in r["CONCEITOS"].items():
            if c["CURRENT_IMPLEMENTATION"] == "IMPLEMENTED":
                self.assertTrue(c["MODULO_EXISTE"],
                                "%s diz IMPLEMENTED sem modulo" % nome)


class P13_UmPortaoImportadoTemDeSerCorrivelAqui(unittest.TestCase):
    """⚠️ §115 do know-how, guardado.

    `C-INT-ATOMICITY-01` importou o portão do Control Plane e nunca o correu.
    A reprovação apareceu na missão seguinte, a bloquear a promoção da Bíblia.

        UM PORTAO QUE CHEGA COMO FICHEIRO E UM PORTAO QUE NINGUEM ABRE.
    """

    def test_o_portao_do_controle_corre_nesta_arvore(self):
        """Não exige que ele PASSE — exige que ele CORRA e diga um veredito."""
        r = subprocess.run([sys.executable, "controle/portao_do_controle.py"],
                           cwd=RAIZ, capture_output=True, text=True, timeout=600)
        self.assertIn("PORTAO_DO_CONTROLE=", r.stdout,
                      "o portao importado nao produz veredito nesta arvore")

    def test_o_censo_do_controle_escreve_o_gerado_que_o_mapa_le(self):
        self.assertTrue(os.path.exists(
            ficheiro("system-map/data/controle.generated.json")),
            "o censo do controle nunca correu: o mapa le um ficheiro que nao existe")
        self.assertIn("system-map/data/controle.generated.json",
                      git("ls-files", "system-map/data"),
                      "o gerado do controle existe no disco e nao no Git")

    @unittest.expectedFailure
    def test_o_chao_do_controle_descreve_ESTA_arvore(self):
        """⚠️ A causa de fundo do §115 — BLOQUEADOR DECLARADO, NAO REGRESSAO.

        Um tecto fixado noutra árvore não mede «piorou»: mede «é outra casa».

        Está marcado `expectedFailure` de propósito, e não silenciado: no dia
        em que `C-CTRL-FLOOR-01` re-fixar o chão aqui, o unittest reporta
        **unexpectedSuccess** — e essa é a notícia de que a promoção da Bíblia
        deixou de ter bloqueador.

            UM BLOQUEADOR SILENCIADO E UM BLOQUEADOR ESQUECIDO.
            UM BLOQUEADOR DECLARADO AVISA QUANDO DEIXA DE EXISTIR.
        """
        with open(ficheiro("controle/CHAO-DO-CONTROLE.json"),
                  encoding="utf-8") as f:
            chao = json.load(f)
        ancestral = subprocess.run(
            ["git", "merge-base", "--is-ancestor", chao["HEAD"], "HEAD"],
            cwd=RAIZ, capture_output=True).returncode == 0
        self.assertTrue(
            ancestral,
            "o chao do Control Plane foi fixado em %s, que NAO e ancestral "
            "desta arvore. O tecto descreve outra fotografia, e o portao esta "
            "a comparar duas casas em vez de dois dias. "
            "BLOQUEADOR da promocao da Biblia — ver "
            "research/intelligence/BIBLE-PROMOTION-GATE-REPORT-V1.md"
            % chao["HEAD"])


class P12_AIntegracaoNaoTocouCollectionRuntime(unittest.TestCase):
    """P12 · nenhum runtime de Collection foi modificado pela integração."""

    PASTAS_DA_COLLECTION = ("coleta/", "admissao/", "guarda/", "leis/",
                            "orquestrador/", "fontes/", "supabase/",
                            "migrations/")

    def _tocados_desde_o_tronco(self):
        return [l for l in git("diff", "--name-only", TRONCO_ACTUAL, "HEAD").splitlines()
                if l]

    def test_nenhuma_pasta_de_collection_foi_tocada(self):
        maus = [f for f in self._tocados_desde_o_tronco()
                if f.startswith(self.PASTAS_DA_COLLECTION)]
        self.assertEqual([], maus, "a integracao tocou Collection: %s" % maus)

    def test_nenhuma_migration_nova(self):
        """⚠️ Uma migration e um `.sql` numa pasta de migrations. Um documento
        chamado `INTELLIGENCE-MIGRATION-MAP-V1.md` e um mapa de migracao de
        CONCEITOS, e apanha-lo aqui seria confundir a palavra com a coisa."""
        maus = [f for f in self._tocados_desde_o_tronco()
                if f.endswith(".sql") or "/migrations/" in f]
        self.assertEqual([], maus, "migration na integracao: %s" % maus)

    #: O espelho do System Map mora dentro da pasta do Portal, e quem o escreve
    #: e a cadeia canonica do mapa (`.github/workflows/system-map.yml`), nao o
    #: Portal. Excluir DUAS moradas nao e abrir uma excepcao: e nomear o dono.
    ESPELHO_DO_MAPA = "italia-portale/client/system-map/"

    def test_nenhum_ficheiro_do_portal_foi_tocado(self):
        maus = [f for f in self._tocados_desde_o_tronco()
                if f.startswith(("italia-portale/", "prototype/"))
                and not f.startswith(self.ESPELHO_DO_MAPA)]
        self.assertEqual([], maus, "a integracao tocou o Portal: %s" % maus)

    def test_o_espelho_do_mapa_so_ganhou_as_pecas_declaradas(self):
        """⚠️ A excepcao acima tem de ser paga com uma prova mais dura.

        O espelho pode mudar — mas so pode GANHAR os componentes que esta
        missao declarou, e nao pode PERDER nenhum. Um gerador que apaga uma
        peca em silencio e indistinguivel de um que a atualiza.
        """
        diff = git("diff", TRONCO_ACTUAL, "HEAD", "--",
                   self.ESPELHO_DO_MAPA + "state.generated.json")
        entram = {l for l in diff.splitlines()
                  if l.startswith("+") and '"id":' in l}
        saem = {l for l in diff.splitlines()
                if l.startswith("-") and '"id":' in l}
        so_entram = {l[1:].strip() for l in entram} - {l[1:].strip() for l in saem}
        so_saem = {l[1:].strip() for l in saem} - {l[1:].strip() for l in entram}
        self.assertEqual(set(), so_saem, "o mapa perdeu pecas: %s" % so_saem)

        # ⚠️ ISTO JA FOI UMA LISTA LITERAL — e por isso reprovou sozinho.
        #
        # A primeira versao fixava `{C-INT-ESPINHA, C-INT-ARBITRAGEM}`, que era
        # o que estava declarado NAQUELA missao. A missao seguinte declarou
        # `C-INT-MODELO-OBJETOS` no sitio certo — na FONTE — regenerou pela
        # cadeia canonica, e este teste reprovou uma coisa correcta.
        #
        #     UMA ASSERCAO CERTA PRESA A UMA FOTOGRAFIA ANTIGA.
        #
        # E a sexta vez nesta casa. A defesa e deixar de fixar um VALOR e passar
        # a medir a PROPRIEDADE que o valor representava: o espelho so pode
        # ganhar pecas que a FONTE declara, e so desta faixa. Uma peca que
        # aparece no espelho sem estar declarada continua a reprovar — que e
        # exactamente o que esta prova existe para apanhar.
        with open(ficheiro("system-map/data/architecture.declared.json"),
                  encoding="utf-8") as fh:
                F = json.load(fh)
        # ⚠️ `"id":` NAO E SO DE PECA — e a segunda vez que esta prova tropeca na
        # forma do ficheiro em vez de na propriedade. O espelho declara
        # territorios e familias com a mesma chave, e a missao do mapa
        # acrescentou `Z-INT-LEI`: um territorio legitimo, declarado na FONTE,
        # que esta prova acusou de nao ser uma peca da Intelligence.
        #
        #     A PROPRIEDADE E «SO GANHA O QUE A FONTE DECLARA», E A FONTE
        #     DECLARA PECAS, TERRITORIOS E FAMILIAS.
        declarados = ({c["id"] for c in F["COMPONENTS"]}
                      | {t["id"] for t in F["TERRITORIES"]}
                      | {f["id"] for f in F.get("FAMILIES", [])})

        # ⚠️ E A SETIMA VEZ, E DESTA O VALOR FIXO ERA UM PREFIXO.
        #
        # A regra era `cid.startswith(("C-INT-", "Z-INT-"))`, e apanhou
        # `C-PROVA-AGRO-FRONTEIRA` — uma peca da Intelligence, declarada na
        # FONTE por esta faixa, que so tem a infelicidade de se chamar pelo
        # territorio onde mora (Z-PROVA) em vez do dominio que serve. O irmao
        # dela, `C-INT-MODELO-OBJETOS`, mora no MESMO territorio e passa, so
        # porque alguem lhe deu outro nome.
        #
        #     UM PREFIXO E UMA CONVENCAO DE NOME. NAO E UMA MEDICAO DE DONO.
        #
        # A propriedade que interessa nunca foi «chama-se C-INT»: e «esta faixa
        # ACRESCENTOU esta peca, e o tronco nao a tinha». Isso mede-se, e
        # continua a apanhar o ataque que a prova existe para apanhar — uma
        # peca que aparece no espelho sem alguem a ter declarado aqui.
        do_tronco = json.loads(git("show",
                                   TRONCO_ACTUAL + ":system-map/data/"
                                   "architecture.declared.json"))
        ja_no_tronco = ({c["id"] for c in do_tronco["COMPONENTS"]}
                        | {t["id"] for t in do_tronco["TERRITORIES"]}
                        | {f["id"] for f in do_tronco.get("FAMILIES", [])})
        desta_faixa = declarados - ja_no_tronco

        for linha in sorted(so_entram):
            cid = linha.split('"')[3]
            with self.subTest(peca=cid):
                self.assertIn(cid, declarados,
                              "o espelho ganhou algo que a FONTE nao declara")
                self.assertIn(cid, desta_faixa,
                              "o espelho ganhou uma peca que esta faixa nao "
                              "acrescentou — veio de onde?")

    def test_a_integracao_de_autoridades_so_acrescentou(self):
        """Ataques 1 e 14 do red team, guardados no sitio certo.

        Um `checkout <ref> -- <path>` de uma branch lateral pode enterrar uma
        versao mais nova sem aviso. Por isso os CINCO commits de integracao sao
        medidos sozinhos: neles, so pode haver 'A'.

        O que vem DEPOIS — mapa regenerado, numeros re-derivados — e outra
        categoria, e tem a sua propria prova a seguir.

            REGENERAR NAO E SOBRESCREVER. MAS SO SE ALGUEM SEPARAR AS DUAS.
        """
        saida = git("diff", "--name-status", TRONCO, FIM_DA_INTEGRACAO)
        maus = [l for l in saida.splitlines() if l and l[0] != "A"]
        self.assertEqual([], maus,
                         "a integracao de autoridades modificou ou apagou: %s" % maus)

    #: ⚠️ TRES CATEGORIAS, E NAO DUAS. A primeira versao desta prova tinha so
    #: «gerado» e «ledger», e apanhou as minhas proprias edicoes de FONTE —
    #: correctamente. Um ficheiro `.declared.json` e fonte; um `.generated.json`
    #: e saida; e um scanner que eu editei e fonte tambem. Meter os tres no
    #: mesmo saco tornaria a prova incapaz de ver uma edicao a mao dentro de um
    #: gerado, que e exactamente o que ela existe para ver.
    #:
    #:     O QUE E GERADO DECLARA-SE PELO SUFIXO, NAO PELA PASTA.
    REGENERADO_POR_CADEIA_CANONICA = (
        ".generated.json",                         # a cadeia do mapa e o espelho
    )

    #: Edicoes de FONTE que esta missao fez de proposito, uma a uma, com razao.
    #: Lista curta e visivel: qualquer nome a mais aparece no diff.
    EDITADO_NA_FONTE = {
        "system-map/data/architecture.declared.json":
            "declarei C-INT-ESPINHA e C-INT-ARBITRAGEM (§17: consertar na fonte)",
        "system-map/scripts/censo_do_congelamento.py":
            "declarei os dois INSTRUMENTOS da trava, pagos com P10b",

        #: ⚠️ ESTAS QUATRO NAO SAO DESTA FAIXA — sao do CLOSE WAVE / PASSO 1,
        #: a missao que integrou esta linha no trunk por fast-forward. Ficam
        #: aqui porque esta prova mede `TRONCO_ACTUAL..HEAD`, e depois da
        #: integracao o HEAD do trunk passou a conter os commits dela.
        #: A prova apanhou-as, e apanhou-as com razao: sao edicao a mao.
        #: Escreve-se a razao em vez de afrouxar a assercao.
        "data/samples/IT-SOURCE-SAMPLES/IT-T4-001/ID_6_Dataset_Fitosanitari_v2.0.pdf.headers.txt":
            "redigi 3 cabecalhos Set-Cookie com valor cru (tokens de sessao "
            "num repositorio publico); marcador ja usado em "
            "data/samples/ITALY-T3-005-MONITORAGGIO/headers.txt",
        "data/samples/IT-SOURCE-SAMPLES/IT-T4-001/PROD_FTS_6_20260907.csv.headers.txt":
            "redigi 3 cabecalhos Set-Cookie com valor cru; RAW e SHA256 do "
            "MANIFEST intactos — o manifesto cobre o payload, nao o header",
        "data/samples/IT-SOURCE-SAMPLES/IT-T5-002/91515.headers.txt":
            "redigi 3 cabecalhos Set-Cookie com valor cru (JSESSIONID e "
            "__cf_bm entre eles); o cabecalho existiu continua provado",
        "data/samples/IT-SOURCE-SAMPLES/IT-T7-002/"
        "ELENCO-OP-AOP-al-31-12-2025-agg-08-04-2026.ods.headers.txt":
            "redigi 3 cabecalhos Set-Cookie com valor cru (PHPSESSID entre "
            "eles); a guarda de credencial passou de 5 achados para 1",
    }
    #: ⚠️ ERA UMA LISTA DE OITO NOMES, E ADOECEU DA MESMA COISA QUE AS OUTRAS.
    #:
    #: O ledger (`pacote/metricas_canonicas.py --sync`) escreve em todo o
    #: ficheiro que tenha um marcador `<!--M:NOME-->`. A lista fixava OITO —
    #: os que tinham `TEST_COUNT_CURRENT` no dia em que foi escrita — e deixava
    #: de fora quatro que carregam `SOURCE_ID_COUNT` e sao regenerados pelo
    #: MESMO comando, pelo MESMO dono, na MESMA corrida.
    #:
    #:     O DONO NAO E A LISTA. O DONO E O MARCADOR, E ELE ESTA NO FICHEIRO.
    #:
    #: Passa a medir-se: tem marcador do ledger, e do ledger.
    MARCA_DO_LEDGER = "<!--M:"

    #: O que nao e `.generated.json`, nao tem marcador do ledger e nao e OUTPUT
    #: declarado da cadeia — mas TEM gerador, com nome. Lista curta, com razao,
    #: e cada linha e uma divida a resolver no sitio certo.
    GERADO_FORA_DA_CADEIA = {
        "data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json":
            "escrito por provas/o_censo_da_sala_de_espera.py (SAIDA, linha 55); "
            "o censo da Sala ainda nao e passo declarado da cadeia do mapa",
    }

    @staticmethod
    def _outputs_da_cadeia():
        """Os OUTPUTS que a propria cadeia declara. Nao e uma copia: e a fonte.

        `system-map/scripts/cadeia_do_mapa.py` ja diz, passo a passo, o que
        cada um escreve. Repetir a lista aqui seria o segundo sitio a
        divergir do primeiro.
        """
        import cadeia_do_mapa as CAD  # noqa: E402 — vive em system-map/scripts
        saidas = set()
        for grupo in (CAD.ordem_escrita(), CAD.passos_a_mao(),
                      CAD.passos_de_validar(), CAD.portoes_pos_commit(),
                      CAD.outras_execucoes()):
            for passo in grupo:
                for o in passo.get("OUTPUTS", []):
                    saidas.add(o["PATH"] if isinstance(o, dict) else o)
        return saidas

    def test_tudo_o_que_foi_modificado_tem_gerador_com_nome(self):
        """Nenhum ficheiro mudou por edicao a mao.

        Um ficheiro gerado que alguem editou a mao e indistinguivel de um
        gerado — ate ao dia em que o gerador corre outra vez e apaga a edicao.
        """
        saida = git("diff", "--name-status", TRONCO_ACTUAL, "HEAD")
        modificados = [l.split("\t", 1)[1] for l in saida.splitlines()
                       if l and l[0] in ("M", "D")]
        da_cadeia = self._outputs_da_cadeia()

        def tem_dono(f):
            if f.endswith(self.REGENERADO_POR_CADEIA_CANONICA):
                return True                      # o sufixo declara a saida
            if f in da_cadeia:
                return True                      # a cadeia declara-o como OUTPUT
            if f in self.GERADO_FORA_DA_CADEIA:
                return True                      # gerador com nome, escrito
            if f in self.EDITADO_NA_FONTE:
                return True                      # edicao de fonte, com razao
            caminho = ficheiro(f)
            if os.path.exists(caminho):
                with open(caminho, encoding="utf-8", errors="replace") as fh:
                    if self.MARCA_DO_LEDGER in fh.read():
                        return True              # o marcador diz quem escreve
            return False

        orfaos = [f for f in modificados if not tem_dono(f)]
        self.assertEqual([], orfaos,
                         "modificado sem gerador nem razao escrita: %s" % orfaos)

    def test_nenhum_gerado_foi_editado_a_mao(self):
        """O `.declared.json` e fonte; os `.generated.json` sao saida.

        Esta prova mede que a declaracao mudou (foi la que eu escrevi) e que
        os gerados mudaram COM ela — nunca sem.
        """
        saida = git("diff", "--name-only", TRONCO_ACTUAL, "HEAD")
        tocados = set(saida.splitlines())
        self.assertIn("system-map/data/architecture.declared.json", tocados,
                      "declarei pecas novas e a FONTE nao mudou")
        self.assertIn("system-map/data/architecture.generated.json", tocados,
                      "a fonte mudou e o gerado nao: a cadeia nao correu")


if __name__ == "__main__":
    unittest.main(verbosity=2)
