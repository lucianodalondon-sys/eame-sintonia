"""Une os livros da curadoria que a ponte e o servico escreveram (missao 5, passo 3).

    py ferramentas/unificacao/unir_livros_do_servico.py <ponte> <servico> [--escrever] [--relatorio F]

Nunca se escolhe um lado inteiro: cada livro une-se pela CHAVE dele. A mesma
chave com conteudo diferente nos dois lados e CONFLITO — fica o valor da
ponte (a base decidida pelo dono) e a entrada vai para o relatorio, com os
dois valores, para ser resolvida pela prova. Nada se apaga.

  BRIDGE-LEDGER-V1.PROCESSADAS     chave CANDIDATA_ID
  DISCOVERY-VISITED.VISITADOS      chave dominio
  DISCOVERY-VISITED.REJEITADOS     chave dominio (visitado vence rejeitado? nao:
                                   um dominio pode estar nos dois; cada dicionario une-se sozinho)
  LIFECYCLE-EVIDENCE-V1.PROVAS     chave EVIDENCE_REF
  italy_contracts_curator.FONTES   chave SOURCE_ID
  READY-BATCHES-V1.LOTES           chave READY_BATCH_ID (lote e registo historico;
                                   id igual e conteudo diferente = conflito)

Ficam FORA desta ferramenta, e porque:
  LIFECYCLE-LEDGER-V1  append-only: fica o da ponte; o do servico entra pela
                       reconciliar_livros.py (o bot e testemunha, nao juiz).
  LIFECYCLE-QUEUE-V1   fila operacional do worker: ver unir_fila().
  READY-SOURCES-V1     derivado: regera-se com interface_collection.py.
  DISCOVERY-PROOF-V1   relatorio da ULTIMA corrida da discovery, nao livro.
"""
import argparse
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CUR = "curadoria/"


def ler(ref, nome):
    p = subprocess.run(["git", "show", "%s:%s%s" % (ref, CUR, nome)], cwd=str(RAIZ), capture_output=True)
    if p.returncode != 0:
        return None
    return json.loads(p.stdout)


# Campos de PROVENIENCIA que a ponte anotou ao importar do bot (RECONCILIACAO-V1).
# Uma entrada que so difere neles e o mesmo facto com o carimbo de quem o trouxe:
# fica a da ponte (que tem o carimbo), e nao e conflito.
SO_PROVENIENCIA = {"IMPORTADO_DE"}


def _mesmo_facto(a, b) -> bool:
    if not (isinstance(a, dict) and isinstance(b, dict)):
        return False
    dif = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    return bool(dif) and dif <= SO_PROVENIENCIA and all(k in a for k in dif)


def _uniao_dict(a: dict, b: dict, onde: str, conflitos: list) -> tuple[dict, int]:
    out, novos = dict(a), 0
    for k, v in b.items():
        if k not in out:
            out[k] = v
            novos += 1
        elif out[k] != v and not _mesmo_facto(out[k], v):
            conflitos.append({"LIVRO": onde, "CHAVE": k, "PONTE": out[k], "SERVICO": v})
    return out, novos


def _uniao_lista(a: list, b: list, chave: str, onde: str, conflitos: list) -> tuple[list, int]:
    idx = {x[chave]: i for i, x in enumerate(a)}
    out, novos = list(a), 0
    for x in b:
        k = x[chave]
        if k not in idx:
            idx[k] = len(out)
            out.append(x)
            novos += 1
        elif out[idx[k]] != x and not _mesmo_facto(out[idx[k]], x):
            conflitos.append({"LIVRO": onde, "CHAVE": k, "PONTE": out[idx[k]], "SERVICO": x})
    return out, novos


def unir(ponte: str, servico: str) -> tuple[dict, dict]:
    escrever, rel, conflitos = {}, {}, []

    def dicts(nome, campos):
        a, b = ler(ponte, nome), ler(servico, nome)
        d = dict(a)
        for c in campos:
            d[c], n = _uniao_dict(a[c], b[c], "%s.%s" % (nome, c), conflitos)
            rel["%s.%s" % (nome, c)] = {"PONTE": len(a[c]), "SERVICO": len(b[c]),
                                         "SO_DO_SERVICO": n, "UNIDO": len(d[c])}
        escrever[nome] = d

    def listas(nome, campo, chave):
        a, b = ler(ponte, nome), ler(servico, nome)
        d = dict(a)
        d[campo], n = _uniao_lista(a[campo], b[campo], chave, "%s.%s" % (nome, campo), conflitos)
        rel["%s.%s" % (nome, campo)] = {"PONTE": len(a[campo]), "SERVICO": len(b[campo]),
                                         "SO_DO_SERVICO": n, "UNIDO": len(d[campo])}
        escrever[nome] = d
        return d

    dicts("BRIDGE-LEDGER-V1.json", ["PROCESSADAS"])
    dicts("DISCOVERY-VISITED.json", ["VISITADOS", "REJEITADOS"])
    listas("LIFECYCLE-EVIDENCE-V1.json", "PROVAS", "EVIDENCE_REF")
    c = listas("italy_contracts_curator.json", "FONTES", "SOURCE_ID")
    c["TOTAL"] = len(c["FONTES"])
    lt = listas("READY-BATCHES-V1.json", "LOTES", "READY_BATCH_ID")
    # Um lote e um registo historico: o mesmo numero com fontes diferentes sao
    # DOIS lotes que existiram. O do servico entra com numero novo e o antigo ao lado.
    for x in [c for c in conflitos if c["LIVRO"] == "READY-BATCHES-V1.json.LOTES"]:
        n = dict(x["SERVICO"])
        prox = max(int(y["READY_BATCH_ID"].rsplit("-", 1)[1]) for y in lt["LOTES"]) + 1
        n["READY_BATCH_ID"] = "READY-BATCH-%03d" % prox
        n["UNIFICACAO"] = {"MISSAO": "UNIFICACAO-V1", "ERA_NO_SERVICO": x["CHAVE"]}
        lt["LOTES"].append(n)
        x["RESOLVIDO"] = "os dois ficam: o do servico passa a %s" % n["READY_BATCH_ID"]
    lt["PROXIMO"] = max([int(x["READY_BATCH_ID"].rsplit("-", 1)[1]) for x in lt["LOTES"]] + [0]) + 1
    lt["READY_BATCHES_CREATED"] = len(lt["LOTES"])

    fila, rel_fila = unir_fila(ponte, servico)
    escrever["LIFECYCLE-QUEUE-V1.json"] = fila
    rel["LIFECYCLE-QUEUE-V1.TAREFAS"] = rel_fila
    rel["CONFLITOS"] = len(conflitos)
    rel["CONFLITOS_POR_LIVRO"] = {}
    for x in conflitos:
        rel["CONFLITOS_POR_LIVRO"][x["LIVRO"]] = rel["CONFLITOS_POR_LIVRO"].get(x["LIVRO"], 0) + 1
    rel["LISTA_DE_CONFLITOS"] = conflitos
    return escrever, rel


def unir_fila(ponte: str, servico: str) -> tuple[dict, dict]:
    """A fila e do worker que corre, e o worker que corre e o do servico.

    Os TASK_ID das duas filas foram alocados do mesmo contador a partir de 98:
    o mesmo numero e outra tarefa. Por isso nao se une por TASK_ID. Fica a fila
    do servico, e cada tarefa da ponte que o servico NAO conhece por
    (SOURCE_ID, TASK_TYPE) e ainda esta por fazer entra no fim, com TASK_ID
    novo e a origem ao lado. Tarefa DONE/FAILED so da ponte fica no git da
    ponte (e historia, nao trabalho). Na troca do servico, o coordenador
    substitui esta fila pelo corte final da fila viva e reaplica esta regra.
    """
    a, b = ler(ponte, "LIFECYCLE-QUEUE-V1.json"), ler(servico, "LIFECYCLE-QUEUE-V1.json")
    conhecidas = {(t["SOURCE_ID"], t["TASK_TYPE"]) for t in b["TAREFAS"]}
    base_ids = {t["TASK_ID"] for t in b["TAREFAS"]}
    out = dict(b)
    out["TAREFAS"] = list(b["TAREFAS"])
    prox = int(b["PROXIMO_ID"])
    entradas, historia = [], []
    for t in a["TAREFAS"]:
        if (t["SOURCE_ID"], t["TASK_TYPE"]) in conhecidas:
            continue
        if t["STATUS"] in ("DONE", "FAILED", "BLOCKED"):
            historia.append((t["TASK_ID"], t["SOURCE_ID"], t["TASK_TYPE"], t["STATUS"]))
            continue
        n = dict(t)
        n["TASK_ID"] = "T%05d" % prox
        while n["TASK_ID"] in base_ids:
            prox += 1
            n["TASK_ID"] = "T%05d" % prox
        prox += 1
        n["UNIFICACAO"] = {"MISSAO": "UNIFICACAO-V1", "ORIGEM": "ponte", "TASK_ID_NA_PONTE": t["TASK_ID"]}
        out["TAREFAS"].append(n)
        entradas.append((t["TASK_ID"], n["TASK_ID"], t["SOURCE_ID"], t["TASK_TYPE"], t["STATUS"]))
    out["PROXIMO_ID"] = prox
    return out, {"PONTE": len(a["TAREFAS"]), "SERVICO": len(b["TAREFAS"]),
                 "DA_PONTE_POR_FAZER_ACRESCENTADAS": entradas,
                 "DA_PONTE_SO_HISTORIA_NAO_COPIADAS": historia, "UNIDO": len(out["TAREFAS"])}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ponte"), ap.add_argument("servico")
    ap.add_argument("--escrever", action="store_true")
    ap.add_argument("--relatorio")
    a = ap.parse_args()
    esc, rel = unir(a.ponte, a.servico)
    print(json.dumps({k: v for k, v in rel.items() if k != "LISTA_DE_CONFLITOS"}, ensure_ascii=True, indent=1)[:4000])
    if a.relatorio:
        Path(a.relatorio).write_text(json.dumps(rel, indent=1, ensure_ascii=False), encoding="utf-8")
    if a.escrever:
        for nome, d in esc.items():
            (RAIZ / CUR / nome).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                                           encoding="utf-8", newline="\n")
