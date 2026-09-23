#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATILHO DE FILA BAIXA — quando as candidatas acabam, dize-lo pelo nome.

    FINGIR SERVICO INFINITO E PIOR DO QUE DIZER QUE FALTA.

O Source Curator consome candidatas; quem as produz e a Discovery (o motor
vive em source-discovery-v1, 56d037b3 — NAO e integrado aqui, por ordem).
Este ficheiro nao descobre nada: mede quantas candidatas ainda podem virar
trabalho automatico pelo caminho provado, compara com um nivel minimo, e
emite `DISCOVERY_NEEDED` quando o nivel e cruzado.

O QUE CONTA COMO «CANDIDATA POR PROCESSAR»
------------------------------------------
So o que a cadeia consegue avancar SEM humano e SEM capacidade nova:

    HTML nunca caracterizadas, e que nao sao endpoint de fonte existente
        (NUNCA_CARACTERIZADAS.HTML_NOVAS)
  + caracterizadas com NEEDS_MORE_SAMPLING (a amostra e que faltou)

Nao conta: as sociais (fora de escopo, dono proprio), as CAPABILITY_BLOCK
(dono SCRAP ENGINEER), as SEM_TERRITORIO (decisao humana, NAO SEI deliberado)
e as que ja tem contrato. Contar essas faria a fila parecer cheia de trabalho
que ninguem aqui consegue fazer.

    CANDIDATE_LOW_WATERMARK = 20
    Uma leva de caracterizacao anda a 10-30 fontes; 20 e «uma leva de
    reserva». E escolha com razao escrita, nao medida — se a cadencia real
    mostrar outro numero, muda-se aqui, num sitio so.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import baldes_das_candidatas as B  # noqa: E402
import fila as F                   # noqa: E402

SAIDA = RAIZ / "curadoria" / "DISCOVERY-SIGNAL-V1.json"

CANDIDATE_LOW_WATERMARK = 20
DISCOVERY_PRODUCER = {"LANE": "source-discovery-v1", "COMMIT_MEDIDO": "56d037b3",
                      "NOTA": "produtor existe noutra bancada; este sinal e o consumidor a pedir"}


def _qualify_ja_tentadas() -> set:
    """CANDIDATE_IDs que já tiveram uma tarefa QUALIFY (qualquer resultado).

    Uma fonte cujo QUALIFY BLOQUEOU (território NAO SEI) não vai avançar
    automaticamente — não conta como backlog accionável. Só as que ainda
    não foram tentadas (sem tarefa QUALIFY nenhuma) representam trabalho real.
    """
    try:
        d = F._ler()
    except Exception:
        return set()
    return {t["SOURCE_ID"] for t in d["TAREFAS"] if t["TASK_TYPE"] == F.QUALIFY}


def medir(baldes: dict | None = None, watermark: int = CANDIDATE_LOW_WATERMARK) -> dict:
    b = baldes if baldes is not None else B.calcular()
    n = b["NUNCA_CARACTERIZADAS"]

    # HTML_NOVAS: só conta as que ainda não tiveram QUALIFY (nenhum resultado).
    # As que tiveram QUALIFY BLOQUEADO não vão avançar sozinhas — não são backlog.
    html_novas_ids = set(n.get("HTML_NOVAS_IDS", []))
    tentadas = _qualify_ja_tentadas()
    html_actionable = len(html_novas_ids - tentadas)

    mais_amostra = b["CARACTERIZADAS_NAO_READY_PORQUE"].get("NEEDS_MORE_SAMPLING", 0)
    backlog = html_actionable + mais_amostra
    needed = backlog < watermark
    return {
        "DATASET": "DISCOVERY-SIGNAL-V1",
        "LEI": ("o Curator nao finge servico infinito: quando o que ainda pode virar "
                "trabalho automatico cai abaixo do nivel, DISCOVERY_NEEDED fica escrito, "
                "com os numeros ao lado. Nao ha motor de descoberta aqui."),
        "MEDIDO_EM": datetime.now(timezone.utc).isoformat(),
        "UNIVERSO_DESTA_ARVORE": b["UNIVERSO_DESTA_ARVORE"],
        "CANDIDATE_LOW_WATERMARK": watermark,
        "CANDIDATE_BACKLOG": backlog,
        "CANDIDATE_BACKLOG_COMPOSICAO": {"HTML_NUNCA_CARACTERIZADAS_NOVAS": html_actionable,
                                         "NEEDS_MORE_SAMPLING": mais_amostra},
        "FORA_DO_BACKLOG": {"SOCIAL_FORA_DE_ESCOPO": n["SOCIAL"],
                            "HTML_QUALIFY_BLOQUEADO": len(html_novas_ids & tentadas),
                            "CAPABILITY_BLOCK": b["TOTAIS"]["COM_SOURCE_ID_SEM_CONTRATO"]
                            + b["CARACTERIZADAS_NAO_READY_PORQUE"].get("CAPABILITY_BLOCK", 0),
                            "SEM_TERRITORIO": b["TOTAIS"]["SEM_TERRITORIO"],
                            "JA_COM_CONTRATO": b["TOTAIS"]["JA_COM_CONTRATO"]},
        "DISCOVERY_NEEDED": needed,
        "DISCOVERY_SIGNAL": "DISCOVERY_NEEDED" if needed else "DISCOVERY_NOT_NEEDED",
        "DISCOVERY_PRODUCER": DISCOVERY_PRODUCER,
    }


def escrever(r: dict | None = None) -> dict:
    r = r or medir()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return r


def main() -> int:
    r = escrever()
    print("CANDIDATE_BACKLOG        %d  (%s)" % (r["CANDIDATE_BACKLOG"],
                                                 json.dumps(r["CANDIDATE_BACKLOG_COMPOSICAO"])))
    print("CANDIDATE_LOW_WATERMARK  %d" % r["CANDIDATE_LOW_WATERMARK"])
    print("DISCOVERY_SIGNAL         %s" % r["DISCOVERY_SIGNAL"])
    print("escrito: %s" % SAIDA.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
