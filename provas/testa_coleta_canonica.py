#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS PONTA A PONTA DA COLETA CANONICA.

    py provas/testa_coleta_canonica.py

Sete casos, e cada um existe porque a alternativa ja custou caro nesta casa ou
custa caro em qualquer casa. Nao sao testes de cobertura: sao as sete maneiras
conhecidas de este caminho mentir.

    1  o pedido em portugues chega ate ao fim
    2  item fora do universo: o bruto fica, a rejeicao fica escrita com motivo
    3  prova insuficiente da NAO_SEI, e nunca NAO
    4  falha de ferramenta da ERRO, e nunca REJEITADO
    5  o mesmo bruto vale para dois universos, com decisoes independentes
    6  trocar de executor nao muda uma linha em quem pede
    7  nada aponta para o que foi removido
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from pedido import de_uma_frase, Pedido, PedidoInvalido  # noqa: E402
from receitas import resolver  # noqa: E402
import orquestrador as orq  # noqa: E402
import admissao as adm  # noqa: E402

FALHAS = []


def prova(nome, ok, detalhe=""):
    print(f"  {'PASS' if ok else 'FALHA':5s}  {nome}" + (f"  — {detalhe}" if not ok and detalhe else ""))
    if not ok:
        FALHAS.append(nome)


# ── 1 · o pedido atravessa o caminho todo ───────────────────────────────────
p = de_uma_frase("colete materiais de pesquisadores")
prova("1_pedido_em_portugues_vira_alvo", p.alvo == "T7", f"deu {p.alvo}")
plano = resolver(p)
prova("1_plano_encontra_executor", plano.da_para_correr)
recibo = orq.correr(p, seco=True)
prova("1_corrida_devolve_recibo_com_versao",
      recibo["STATUS"] == "OK" and recibo["ACTOR_VERSION"] != "NOT_PRESERVED",
      str(recibo.get("ACTOR_VERSION")))
prova("1_recibo_diz_quem_correu_e_quando",
      all(recibo.get(k) for k in ("ACTOR", "STARTED_AT", "FINISHED_AT", "QUERY")))

item_bom = {"id": "e2e-1", "texto": "Ensaio de campo com DOI publicado",
            "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
d = adm.decidir(item_bom, "T7", corrida=recibo["RUN_ID"])
prova("1_item_bom_passa_a_porta", d.resultado == adm.SIM, d.motivo)
saida = adm.pronto_para_inteligencia(item_bom, d)
prova("1_saida_e_o_contrato_da_fronteira",
      saida["ESTADO"] == "PRONTO_PARA_INTELIGENCIA")
prova("1_a_saida_nao_cita_scraper_nem_api",
      not any(x in json.dumps(saida).lower()
              for x in ("scraper", "apify", "playwright", ".py", "requests")))

# ── 2 · fora do universo: o bruto fica, o nao fica escrito ──────────────────
fora = {"id": "e2e-2", "texto": "Promocao de tratores com desconto",
        "source_id": "IT-T9-004", "fact_time": "2026-05-03"}
d2 = adm.decidir(fora, "T7", corrida="e2e")
prova("2_item_fora_do_universo_e_NAO", d2.resultado == adm.NAO, d2.resultado)
prova("2_a_rejeicao_tem_motivo_escrito", len(d2.motivo) > 30)
prova("2_a_rejeicao_diz_a_regra_e_a_versao", bool(d2.regra) and bool(d2.versao))
prova("2_o_bruto_nao_foi_destruido", fora.get("texto") == "Promocao de tratores com desconto")

# ── 3 · sem prova nao vira nao ──────────────────────────────────────────────
sem_data = {"id": "e2e-3", "texto": "Ensaio com DOI", "source_id": "IT-T7-002"}
d3 = adm.decidir(sem_data, "T7")
prova("3_falta_de_prova_da_NAO_SEI", d3.resultado == adm.NAO_SEI, d3.resultado)
prova("3_NAO_SEI_nao_e_NAO", d3.resultado != adm.NAO)

sem_origem = {"id": "e2e-3b", "texto": "Ensaio", "fact_time": "2026-01-01"}
prova("3_item_sem_origem_da_NAO_SEI",
      adm.decidir(sem_origem, "T7").resultado == adm.NAO_SEI)

# ── 4 · falha de ferramenta nao e rejeicao ──────────────────────────────────
quebrado = {"id": "e2e-4", "erro_de_leitura": "TimeoutError",
            "source_id": "IT-T7-003", "fact_time": "2026-01-01"}
d4 = adm.decidir(quebrado, "T7")
prova("4_falha_de_ferramenta_da_ERRO", d4.resultado == adm.ERRO, d4.resultado)
prova("4_ERRO_nao_e_REJEITADO", d4.resultado != adm.NAO)
prova("4_o_erro_guarda_a_mensagem", "TimeoutError" in json.dumps(d4.evidencia))

# ── 5 · o mesmo bruto, dois universos, decisoes independentes ───────────────
ambiguo = {"id": "e2e-5",
           "texto": "Universidade apresenta ensaio de campo no lancamento do produto",
           "source_id": "IT-T7-004", "fact_time": "2026-02-02"}
dA = adm.decidir(ambiguo, "T7")
dB = adm.decidir(ambiguo, "T9")
prova("5_decisoes_sao_por_par_item_universo", dA.universo != dB.universo)
prova("5_ambos_avaliados_sem_se_atropelarem",
      dA.resultado in adm.RESULTADOS and dB.resultado in adm.RESULTADOS)
prova("5_relevancia_nao_e_booleano_no_item", "relevante" not in ambiguo)

# ── 6 · trocar o executor nao mexe em quem pede ─────────────────────────────
import receitas  # noqa: E402
antes = receitas.EXECUTORES["T7"][0]
receitas.EXECUTORES["T7"] = [dict(antes, id="outro-executor",
                                  roda=["coleta/outro_qualquer.py"])]
p6 = de_uma_frase("colete materiais de pesquisadores")   # o pedido e IGUAL
plano6 = resolver(p6)
prova("6_o_pedido_nao_mudou", p6.para_json() == p.para_json())
prova("6_o_plano_aponta_para_o_executor_novo",
      plano6.executores[0]["id"] == "outro-executor")
receitas.EXECUTORES["T7"] = [antes]

# ── 7 · nada aponta para o que foi removido ─────────────────────────────────
import subprocess  # noqa: E402
REMOVIDOS = (".github/workflows/adama-es-gate.yml",)
restos = []
for r in REMOVIDOS:
    saida_git = subprocess.run(["git", "-C", str(RAIZ), "grep", "-l", "-F", r],
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace").stdout
    # NAO CONTA quem guarda o proprio caminho por dever de oficio: o ficheiro
    # guardado (que E o caminho), a documentacao que explica a mudanca, o mapa
    # gerado (que descreve o repositorio) — e este teste, que tem de escrever o
    # nome para o poder procurar. Sem esta linha, o teste encontrava-se a si
    # mesmo e reprovava para sempre.
    restos += [l for l in saida_git.splitlines()
               if not l.startswith(("guarda/es/", "docs/", "AGENTS.md",
                                    "provas/testa_coleta_canonica.py",
                                    "system-map/data/", "italia-portale/client/"))]
prova("7_nada_aponta_para_o_que_saiu", not restos, ", ".join(restos[:3]))

print()
if FALHAS:
    print(f"COLETA_CANONICA=FALHA · {len(FALHAS)} reprovada(s): {', '.join(FALHAS)}")
    raise SystemExit(1)
print("COLETA_CANONICA=PASS · o caminho do pedido ate a inteligencia esta fechado")
