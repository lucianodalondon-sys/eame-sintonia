#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RECONCILIAR O ESTADO CONTRA A ROTA DE HOJE.

    UM VEREDITO ENVELHECE QUANDO A PERGUNTA MUDA.

As 50 fontes YouTube foram marcadas CONTRACT_READY_ROUTE_BLOCKED porque
`feeds/videos.xml` esta em Disallow no robots vivo. Isso continua VERDADE —
sobre aquela rota. Entretanto a integracao pos-Big-Collection (5920d77d)
deu-lhes uma rota diferente, `CANAL_PUBLICO_YOUTUBE_V1`, que nao toca no
feed.

    O BLOQUEIO NAO FOI REVOGADO. FICOU A RESPONDER OUTRA PERGUNTA.

Este script NAO promove nada. Marca-as `RECONCILIATION_REQUIRED`, que e o
unico rotulo honesto: o estado que tinham foi medido contra uma rota que
ja nao e a rota, e ninguem mediu a nova a partir desta linha.

⚠️ PORQUE NAO CORRER JA O CANARIO DA ROTA NOVA AQUI:
o adaptador `CANAL_PUBLICO_YOUTUBE_V1` vive na arvore da integracao, nao
nesta. Correr o canario daqui mediria uma capacidade que esta branch nao
tem — e `CAPABILITY_PROVEN_BUT_NOT_IN_TRUNK` ja custou uma missao a esta
casa. A remedicao pertence a missao de integracao, que tem o adaptador.

    PROVADO NOUTRA ARVORE != DISPONIVEL NESTA.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import lifecycle as LC    # noqa: E402

# A ref da integracao, lida sem checkout e sem abrir a worktree do outro.
REF_INTEGRACAO = "source-curator-integration-v1"
TABELA = "regras/italy_contracts_onboarded.json"
SAIDA = RAIZ / "curadoria" / "LIFECYCLE-RECONCILIATION-V1.json"


def do_git(ref: str, caminho: str) -> str | None:
    try:
        return subprocess.run(["git", "show", "%s:%s" % (ref, caminho)],
                              cwd=str(RAIZ), capture_output=True, text=True,
                              check=True).stdout
    except subprocess.CalledProcessError:
        return None


def main() -> int:
    txt = do_git(REF_INTEGRACAO, TABELA)
    if txt is None:
        print("A tabela da integracao nao esta legivel desta arvore.")
        print("REF=%s  PATH=%s" % (REF_INTEGRACAO, TABELA))
        print("RECONCILIACAO = NAO_MEDIVEL (nao se inventa o estado do outro)")
        return 1

    tabela = json.loads(txt)
    linhas = tabela if isinstance(tabela, list) else \
        (tabela.get("FONTES") or tabela.get("CONTRATOS") or [])

    # Quem, na arvore da integracao, tem rota que NAO usa o feed proibido.
    rota_nova = {}
    for l in linhas:
        sid = l.get("SOURCE_ID")
        if not sid:
            continue
        s = json.dumps(l, ensure_ascii=False)
        if "CANAL_PUBLICO_YOUTUBE_V1" in s or l.get("ADAPTER_ID") == "CANAL_PUBLICO_YOUTUBE_V1":
            rota_nova[sid] = {
                "ADAPTER_ID": l.get("ADAPTER_ID"),
                "STRATEGY": l.get("STRATEGY"),
                "BATCH_ID": l.get("BATCH_ID"),
            }

    est = LC.snapshot()
    bloqueadas = {s for s, e in est.items()
                  if e == LC.CONTRACT_READY_ROUTE_BLOCKED}

    alvo = sorted(bloqueadas & set(rota_nova))
    orfas = sorted(bloqueadas - set(rota_nova))

    ref = "INTEGRACAO:%s@%s:%s" % (
        REF_INTEGRACAO,
        subprocess.run(["git", "rev-parse", "--short", REF_INTEGRACAO],
                       cwd=str(RAIZ), capture_output=True, text=True).stdout.strip(),
        TABELA)

    for sid in alvo:
        LC.registar(sid, LC.RECONCILIATION_REQUIRED,
                    ("bloqueio medido contra feeds/videos.xml; a integracao "
                     "deu rota nova %s, que nao usa o feed — remedir la"
                     % rota_nova[sid]["ADAPTER_ID"]),
                    evidence_ref=ref)

    d = {"DATASET": "LIFECYCLE-RECONCILIATION-V1",
         "LEI": ("nao se promove com dado obsoleto nem se condena por rota "
                 "morta. Remede-se onde o adaptador existe."),
         "GERADO_EM": LC.agora(),
         "REF_DA_INTEGRACAO": ref,
         "BLOQUEADAS_ANTES": len(bloqueadas),
         "COM_ROTA_NOVA_NA_INTEGRACAO": len(alvo),
         "SEM_ROTA_NOVA_CONTINUAM_BLOQUEADAS": len(orfas),
         "MARCADAS_RECONCILIATION_REQUIRED": alvo,
         "CONTINUAM_ROUTE_BLOCKED": orfas,
         "QUEM_REMEDE": ("a missao source-curator-integration-v1, que tem o "
                         "adaptador CANAL_PUBLICO_YOUTUBE_V1 na arvore dela"),
         "NAO_PROMOVIDAS": ("nenhuma. READY exige canario da rota de hoje, "
                            "e o adaptador nao existe nesta arvore.")}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    print("BLOQUEADAS_ANTES                = %d" % len(bloqueadas))
    print("COM_ROTA_NOVA_NA_INTEGRACAO     = %d" % len(alvo))
    print("SEM_ROTA_NOVA (continuam BLOCK) = %d" % len(orfas))
    print("PROMOVIDAS                      = 0  (nao se promove com dado velho)")
    print("\nFONTES = %s" % json.dumps(
        {k: v for k, v in LC.metricas().items() if v}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
