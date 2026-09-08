# -*- coding: utf-8 -*-
"""A TRAVA DA INTELIGÊNCIA — a ordem antes da pressa.

    COLLECTION_FOUNDATION_CLOSED != SIM
    →
    INTELLIGENCE_IMPLEMENTATION_BLOCKED

POR QUE ISTO SE ESCREVE HOJE, E NÃO DEPOIS
------------------------------------------
Hoje não existe **nenhuma** área de inteligência implementada neste
repositório. A trava é barata de segurar — e é exatamente por isso que ela se
escreve agora, e não no dia em que já custar.

Construir interpretação sobre uma coleta que ainda não sabe guardar a verdade é
construir o andar de cima antes da fundação. E quando o andar de cima existe,
ninguém volta a mexer na fundação: passam a haver telas que dependem dela como
está.

O QUE ELA NÃO IMPEDE
--------------------
Ler o código, preservar histórico, consertar um defeito que ameace dados, e
medir o que a inteligência futura vai esperar da coleta. Impede
**desenvolvimento novo**.
"""
import json
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRATO = os.path.join(RAIZ, "docs", "operacao", "TRAVA-DA-INTELIGENCIA.json")
ESTRADAS = os.path.join(RAIZ, "system-map", "data", "estradas-it.generated.json")

# As pastas que uma implementação de inteligência ocuparia. Nenhuma existe
# hoje — medido. Se uma aparecer enquanto a coleta não fechar, este teste
# reprova, e o commit que a criou tem de explicar-se.
PASTAS_DE_INTELIGENCIA = ("inteligencia", "intelligence", "field_voices",
                          "field-voices", "opportunity", "oportunidade",
                          "sinais", "signals", "scoring", "recomendacao",
                          "recommendations")


def _json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


class ATravaExisteEDizOEstado(unittest.TestCase):

    def test_o_contrato_existe_e_declara_a_regra(self):
        c = _json(CONTRATO)
        self.assertIn("INTELLIGENCE_IMPLEMENTATION_BLOCKED", c["REGRA"])
        self.assertIn(c["COLLECTION_FOUNDATION_CLOSED"], ("SIM", "NAO"))

    def test_o_estado_do_contrato_bate_com_a_medicao(self):
        """O contrato não guarda uma opinião: ele aponta para o censo, e o
        censo é que decide. Se um dia divergirem, é porque alguém escreveu
        `SIM` à mão sem a medição o sustentar."""
        c = _json(CONTRATO)
        e = _json(ESTRADAS)
        fechadas = e["ESTRADAS"]["FECHADAS"]
        if c["COLLECTION_FOUNDATION_CLOSED"] == "SIM":
            self.assertGreater(fechadas, 0,
                               "diz FECHADO e nenhuma estrada fecha")
        else:
            self.assertEqual(c["COLLECTION_FOUNDATION_CLOSED"], "NAO")

    def test_a_trava_nao_impede_o_que_nao_deve_impedir(self):
        """Uma trava que impedisse consertar um defeito que ameaça dados seria
        pior do que o problema que resolve."""
        c = _json(CONTRATO)
        junto = " ".join(c["O_QUE_A_TRAVA_NAO_IMPEDE"]).lower()
        self.assertIn("ler", junto)
        self.assertIn("defeito", junto)
        self.assertIn("historico", junto)


class NadaDeInteligenciaComecouAindaBloqueada(unittest.TestCase):

    def _areas_existentes(self):
        achadas = []
        for raiz, pastas, _f in os.walk(RAIZ):
            partes = raiz.replace("\\", "/").split("/")
            if ".git" in partes or "node_modules" in partes:
                pastas[:] = []
                continue
            for p in list(pastas):
                if p.lower() in PASTAS_DE_INTELIGENCIA:
                    achadas.append(os.path.relpath(os.path.join(raiz, p), RAIZ))
        return achadas

    def test_nenhuma_area_de_inteligencia_apareceu(self):
        """A trava só vale se alguém a puder violar sem querer — e esta é a
        maneira mais provável: uma pasta nova, criada com boas intenções, antes
        de a fundação fechar."""
        c = _json(CONTRATO)
        if c["COLLECTION_FOUNDATION_CLOSED"] == "SIM":
            self.skipTest("a fundacao fechou; a trava deixa de morder")
        achadas = self._areas_existentes()
        self.assertEqual(
            achadas, [],
            "area de inteligencia criada antes de COLLECTION_FOUNDATION_CLOSED: "
            "%s" % achadas)

    def test_a_contagem_declarada_bate_com_o_disco(self):
        c = _json(CONTRATO)
        declarado = c["ESTADO_MEDIDO_HOJE"]["AREAS_DE_INTELIGENCIA_IMPLEMENTADAS"]
        self.assertEqual(declarado, len(self._areas_existentes()))


class OsCriteriosSaoContados(unittest.TestCase):

    def test_os_criterios_somam(self):
        """Cumpridos mais pendentes têm de dar o total. Um critério que
        desaparece da conta é um critério que ninguém vai fechar."""
        c = _json(CONTRATO)
        total = len(c["CRITERIOS_PARA_FECHAR"])
        self.assertEqual(len(c["QUAIS_JA_CUMPRIDOS"]) + len(c["QUAIS_FALTAM"]),
                         total)
        self.assertEqual(c["QUANTOS_CRITERIOS_JA_CUMPRIDOS"],
                         len(c["QUAIS_JA_CUMPRIDOS"]))

    def test_nenhum_criterio_e_dado_por_cumprido_sem_estar_na_lista(self):
        c = _json(CONTRATO)
        chaves = set(c["CRITERIOS_PARA_FECHAR"])
        self.assertTrue(set(c["QUAIS_JA_CUMPRIDOS"]) <= chaves)
        self.assertTrue(set(c["QUAIS_FALTAM"]) <= chaves)
        self.assertEqual(set(c["QUAIS_JA_CUMPRIDOS"]) & set(c["QUAIS_FALTAM"]),
                         set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
