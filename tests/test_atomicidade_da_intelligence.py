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

#: O tronco de onde esta integracao partiu. Tudo o que estas provas chamam de
#: «nao alterado» e medido contra ele, e nao contra a memoria de ninguem.
TRONCO = "dc00583d01ac6312fa6fa83195d936199eaa3d12"

#: O ultimo dos cinco commits que trouxeram autoridades. Ate aqui, so pode
#: haver ficheiros ACRESCENTADOS — e e o que a prova mede.
FIM_DA_INTEGRACAO = "a8b56448009661c12216d265465d02289c15c8e0"


def git(*a):
    return subprocess.check_output(["git"] + list(a), cwd=RAIZ, text=True,
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
        """O V2 gravado não pode envelhecer em silêncio."""
        p = ficheiro("docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V2.json")
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

        `provas/espinha_da_intelligence.py` traz uma cópia declarada dos 12
        campos de `admissao.pronto_para_inteligencia()`. Na branch onde nasceu,
        `admissao/` não existia e a cópia não tinha contra o que ser conferida.
        Aqui tem.

            UMA COPIA QUE NINGUEM PODE CONFERIR NAO E UMA COPIA: E UMA CRENCA.
        """
        from admissao import decidir, pronto_para_inteligencia
        from espinha_da_intelligence import CAMPOS_DO_READY
        item = {"id": "ATOM-1", "texto": "Ensaio de campo publicado com DOI",
                "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
        d = decidir(item, "T7", corrida="atomicidade")
        real = pronto_para_inteligencia(item, d)
        self.assertEqual(sorted(CAMPOS_DO_READY), sorted(real),
                         "a copia declarada derivou do contrato real")

    def test_nenhum_campo_agronomico_atravessa_a_fronteira_real(self):
        from admissao import decidir, pronto_para_inteligencia
        from espinha_da_intelligence import CAMPOS_QUE_NAO_ATRAVESSAM
        item = {"id": "ATOM-2", "texto": "Ensaio de campo publicado com DOI",
                "source_id": "IT-T7-001", "fact_time": "2026-05-02",
                "evidence_species": "OBSERVED_FIELD_SIGNAL",
                "method": "inspecao_visual", "denominator": 400}
        d = decidir(item, "T7", corrida="atomicidade")
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


class P12_AIntegracaoNaoTocouCollectionRuntime(unittest.TestCase):
    """P12 · nenhum runtime de Collection foi modificado pela integração."""

    PASTAS_DA_COLLECTION = ("coleta/", "admissao/", "guarda/", "leis/",
                            "orquestrador/", "fontes/", "supabase/",
                            "migrations/")

    def _tocados_desde_o_tronco(self):
        return [l for l in git("diff", "--name-only", TRONCO, "HEAD").splitlines()
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
        diff = git("diff", TRONCO, "HEAD", "--",
                   self.ESPELHO_DO_MAPA + "state.generated.json")
        entram = {l for l in diff.splitlines()
                  if l.startswith("+") and '"id":' in l}
        saem = {l for l in diff.splitlines()
                if l.startswith("-") and '"id":' in l}
        so_entram = {l[1:].strip() for l in entram} - {l[1:].strip() for l in saem}
        so_saem = {l[1:].strip() for l in saem} - {l[1:].strip() for l in entram}
        self.assertEqual(set(), so_saem, "o mapa perdeu pecas: %s" % so_saem)
        self.assertEqual(
            {'"id": "C-INT-ESPINHA",', '"id": "C-INT-ARBITRAGEM",'}, so_entram,
            "o mapa ganhou peca que esta missao nao declarou: %s" % so_entram)

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

    #: O que PODE ser modificado depois da integracao, e porque. Cada entrada e
    #: uma saida de gerador canonico. Nao ha aqui nenhum ficheiro de logica.
    REGENERADO_POR_CADEIA_CANONICA = (
        "system-map/data/",                        # a cadeia do mapa
        "italia-portale/client/system-map/",       # o espelho da mesma cadeia
    )
    REGENERADO_PELO_LEDGER = (
        "HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md",
        "docs/apresentacao/PILOTO-CLASSIFICACAO.md",
        "docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md",
        "docs/piloto/EXTERNAL-ONLY-BUSINESS-CASE.md",
        "docs/piloto/O-QUE-PODEMOS-DIZER.md",
        "docs/piloto/PACOTE-DE-MATERIA-PRIMA-EAME.md",
        "docs/piloto/VEREDITO-M10-HANDOFF.md",
        "docs/relatorios/RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA.md",
    )

    def test_tudo_o_que_foi_modificado_tem_gerador_com_nome(self):
        """Nenhum ficheiro mudou por edicao a mao.

        Um ficheiro gerado que alguem editou a mao e indistinguivel de um
        gerado — ate ao dia em que o gerador corre outra vez e apaga a edicao.
        """
        saida = git("diff", "--name-status", TRONCO, "HEAD")
        modificados = [l.split("\t", 1)[1] for l in saida.splitlines()
                       if l and l[0] in ("M", "D")]
        orfaos = [f for f in modificados
                  if not f.startswith(self.REGENERADO_POR_CADEIA_CANONICA)
                  and f not in self.REGENERADO_PELO_LEDGER]
        self.assertEqual([], orfaos,
                         "modificado sem gerador que o explique: %s" % orfaos)

    def test_nenhum_gerado_foi_editado_a_mao(self):
        """O `.declared.json` e fonte; os `.generated.json` sao saida.

        Esta prova mede que a declaracao mudou (foi la que eu escrevi) e que
        os gerados mudaram COM ela — nunca sem.
        """
        saida = git("diff", "--name-only", TRONCO, "HEAD")
        tocados = set(saida.splitlines())
        self.assertIn("system-map/data/architecture.declared.json", tocados,
                      "declarei pecas novas e a FONTE nao mudou")
        self.assertIn("system-map/data/architecture.generated.json", tocados,
                      "a fonte mudou e o gerado nao: a cadeia nao correu")


if __name__ == "__main__":
    unittest.main(verbosity=2)
