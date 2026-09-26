# -*- coding: utf-8 -*-
"""RECEITA-T8 (D48, bot Luciano, 25/09): o coletor de SITES também em T8, T9 e T12.

Medido a 25/09/2026 (FUNIL-RESTO): 22 fontes elegíveis de T8/T9/T12 eram páginas
web e ficavam `SEM_RECEITA_WEB` — T8 só tinha o executor social, T9 o de
comunicação pública e o social, T12 nenhum. Não era falta de fonte; era falta de
receita.

O que estes testes exigem:
  1. um pedido WEB de T8/T9/T12 (fonte nomeada, sem fase) resolve primeiro
     para o executor de sites (`coleta/italy_executor.py`);
  2. um pedido SOCIAL de T8/T9 (fase nomeada) e um pedido SEM filtros
     resolvem para o MESMO executor que resolviam sem este registo — nada muda
     para o YouTube nem para a comunicação pública;
  4. os outros universos não mudam: as MESMAS entradas, pela mesma ordem;
  5. o executor de sites em T8/T9/T12 NÃO inventa fonte (sem
     `filtros_por_omissao`): sem `--filtro fonte=` não há fonte nenhuma.

    TERRITORY != PLATFORM != ROUTE. Isto não diz «todo o T8 é web».
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "pedido"), RAIZ]

import _gavetas  # noqa: E402,F401
import receitas as R  # noqa: E402
from pedido import Pedido  # noqa: E402

WEB = "coleta/italy_executor.py"
SOCIAL = "coleta/scrap_colheita.py"


def _pedido(alvo, **filtros):
    return Pedido(alvo=alvo, filtros=dict(filtros))


def _primeiro(plano):
    return (plano.executores[0].get("roda") or [None])[0]


class OPedidoWebResolveParaOSites(unittest.TestCase):

    def test_t8_web(self):
        p = R.resolver(_pedido("T8", fonte="IT-T8-021", universo="T8", pais="IT"))
        self.assertEqual(_primeiro(p), WEB)

    def test_t9_web(self):
        p = R.resolver(_pedido("T9", fonte="IT-T9-021", universo="T9", pais="IT"))
        self.assertEqual(_primeiro(p), WEB)

    def test_t12_web(self):
        p = R.resolver(_pedido("T12", fonte="IT-T12-137", universo="T12", pais="IT"))
        self.assertEqual(_primeiro(p), WEB)


def _sem_o_de_sites(alvo, **filtros):
    """O mesmo pedido, resolvido como se o executor de sites NAO estivesse no universo."""
    antes = R.EXECUTORES[alvo]
    try:
        R.EXECUTORES[alvo] = [e for e in antes if WEB not in (e.get("roda") or [])]
        return R.resolver(_pedido(alvo, **filtros))
    finally:
        R.EXECUTORES[alvo] = antes


class OSocialNaoMuda(unittest.TestCase):
    """Um pedido SOCIAL resolve para o MESMO executor que resolvia sem o registo."""

    CASOS = (("T8", {"fase": "canal-youtube", "fonte": "IT-T8-001"}),
             ("T8", {"fase": "comentarios-youtube", "plataforma": "youtube"}),
             ("T9", {"fase": "canal-youtube", "plataforma": "youtube"}),
             ("T9", {"fase": "posts", "fonte": "IT-T9-001"}),
             ("T8", {}), ("T9", {}))

    def test_o_primeiro_executor_e_o_de_antes(self):
        for alvo, f in self.CASOS:
            com = R.resolver(_pedido(alvo, **f))
            sem = _sem_o_de_sites(alvo, **f)
            self.assertEqual(com.executores[0].get("id"), sem.executores[0].get("id"), (alvo, f))
            self.assertNotEqual(_primeiro(com), WEB, (alvo, f))

    def test_t8_youtube_continua_no_scrap(self):
        p = R.resolver(_pedido("T8", fase="canal-youtube", fonte="IT-T8-001"))
        self.assertEqual(_primeiro(p), SOCIAL)


class OResto(unittest.TestCase):

    # A fotografia de ANTES (integra-onda2-v1 @ d235c32a), tirada antes do registo.
    ANTES = {"T10": ["italia-recorrente"], "T2": ["italia-recorrente"],
             "T3": ["italia-recorrente", "eppo"],
             "T4": ["regulatorio-eu", "rotulos-oficiais", "italia-recorrente"],
             # T6-PARA-SALA (26/09): o executor de COLHEITA entrou a FRENTE, declarado;
             # o corpus-pesquisador (CATALOGO) fica.
             "T5": ["italia-recorrente"], "T6": ["pesquisadores-t6", "corpus-pesquisador"],
             "T7": ["italia-recorrente"], "T8": ["scrap-colheita"],
             "T9": ["comunicacao-publica", "scrap-colheita"]}

    def test_os_outros_universos_nao_mudam(self):
        for u, ids in self.ANTES.items():
            agora = [e.get("id") for e in R.EXECUTORES[u]]
            if u in ("T8", "T9"):
                self.assertEqual(agora[:len(ids)], ids, u)   # o de antes, pela mesma ordem, a frente
                self.assertEqual(agora[len(ids):], ["italia-recorrente"], u)
            else:
                self.assertEqual(agora, ids, u)
        self.assertEqual([e.get("id") for e in R.EXECUTORES["T12"]], ["italia-recorrente"])
        self.assertEqual(set(R.EXECUTORES), set(self.ANTES) | {"T12"})

    def test_t8_t9_t12_tem_o_executor_de_sites_uma_vez(self):
        for u in ("T8", "T9", "T12"):
            web = [e for e in R.EXECUTORES[u] if WEB in (e.get("roda") or [])]
            self.assertEqual(len(web), 1, u)

    def test_o_social_nao_saiu_de_t8_nem_de_t9(self):
        for u in ("T8", "T9"):
            self.assertTrue(any(SOCIAL in (e.get("roda") or []) for e in R.EXECUTORES[u]), u)

    def test_sem_fonte_inventada(self):
        for u in ("T8", "T9", "T12"):
            web = next(e for e in R.EXECUTORES[u] if WEB in (e.get("roda") or []))
            self.assertNotIn("filtros_por_omissao", web, u)
            self.assertEqual(web.get("argumentos_de_filtros"), ["fonte"], u)

    def test_o_micro_ve_a_receita(self):
        sys.path.insert(0, os.path.join(RAIZ, "scripts", "micro_coleta"))
        import micro_coleta as M  # noqa: PLC0415
        for u in ("T8", "T9", "T12"):
            self.assertIsNotNone(M.receita_web(u), u)


if __name__ == "__main__":
    unittest.main()
