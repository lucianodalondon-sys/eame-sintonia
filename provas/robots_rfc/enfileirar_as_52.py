"""D39 (3): DEPOIS de instalar, re-medir pelo leitor novo as fontes cuja leitura muda (as 52 da medicao
com rede relida pelo leitor D39, provas/robots_rfc/ROBOTS-COM-REDE-D39.json -> MUDAM), pela PORTA CANONICA da fila
(`fila.enfileirar`, idempotente por SOURCE_ID + TASK_TYPE aberto).

  · tarefa: VALIDATE_ROUTE (a etapa que le o robots; o canario nao o le)
  · primeiro as READY de fachada (prioridade 85, acima do REPAIR 80); as outras com 57.
    Medido: 8 das 9 entram; IT-T11-005 (simei.it) esta READY mas o contrato so vive na tabela do
    coletor — fica FORA, para o dono (importar o contrato antes, ou rever o READY)
  · fontes sem contrato no livro do robo (so na tabela do coletor) nao entram: VALIDATE_ROUTE
    sem contrato e bloqueada pelo worker — ficam listadas
  · recusa correr se o leitor instalado nao for o da D39 (re-medir com o leitor velho nao mede nada)
  · por omissao SO MOSTRA; escreve na fila so com --aplicar

⚠️ Efeito a saber: uma fonte READY cuja VALIDATE_ROUTE passe (o site mudou entretanto) desce a
CANARY_PENDING e volta a canariar — a promocao so volta pela regua. Pela medicao de 25/09, as 9
READY fecham todas.
uso (no servico, depois de instalar): py provas/robots_rfc/enfileirar_as_52.py [--aplicar]"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "coleta"))
import fila as F              # noqa: E402
import lifecycle as LC        # noqa: E402
import robots_rfc9309 as RR   # noqa: E402

MEDICAO = Path(__file__).with_name("ROBOTS-COM-REDE-D39.json")
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
PRIORIDADE_READY, PRIORIDADE_RESTO = 85, 57


def plano():
    if "D39" not in RR.VERSAO:
        sys.exit("RECUSA: o leitor instalado e %s — instale a D39 antes de re-medir" % RR.VERSAO)
    mudam = json.loads(MEDICAO.read_text(encoding="utf-8"))["MUDAM"]
    contratos = {c["SOURCE_ID"] for c in json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    estados = LC.snapshot()
    entra, fora = [], []
    for x in mudam:
        sid = x["SOURCE_ID"]
        if sid not in contratos:
            fora.append((sid, "sem contrato no livro do robo (so na tabela do coletor)"))
            continue
        ready = estados.get(sid) == LC.READY_FOR_COLLECTION
        entra.append({"SOURCE_ID": sid, "ESTADO_HOJE": estados.get(sid), "READY": ready,
                      "PRIORIDADE": PRIORIDADE_READY if ready else PRIORIDADE_RESTO,
                      "MOTIVO": ("D39 re-medir robots (medido 25/09: leitura antiga %s, leitor D39 %s — %s)"
                                 % ("permitida" if x["ANTIGO"] else "proibida",
                                    "permitida" if x["NOVO_D39"] else "proibida", x["REGRA_D39"][:60]))})
    entra.sort(key=lambda e: (-e["PRIORIDADE"], e["SOURCE_ID"]))
    return mudam, entra, fora


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="escreve na fila (sem isto so mostra)")
    a = ap.parse_args()
    mudam, entra, fora = plano()
    print("medicao: %d mudam · entram %d (READY primeiro: %d) · fora %d"
          % (len(mudam), len(entra), sum(e["READY"] for e in entra), len(fora)))
    for e in entra:
        print("  %-11s %-28s p=%d  %s" % (e["SOURCE_ID"], e["ESTADO_HOJE"], e["PRIORIDADE"], e["MOTIVO"][:90]))
    for sid, porque in fora:
        print("  FORA %-11s %s" % (sid, porque))
    if not a.aplicar:
        print("SO MOSTREI. Para escrever na fila: --aplicar")
        return 0
    for e in entra:
        t = F.enfileirar(e["SOURCE_ID"], F.VALIDATE_ROUTE, priority=e["PRIORIDADE"], motivo=e["MOTIVO"])
        print("  fila %s %s %s" % (t["TASK_ID"], e["SOURCE_ID"], t["STATUS"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
