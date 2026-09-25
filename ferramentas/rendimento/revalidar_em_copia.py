# -*- coding: utf-8 -*-
"""MICRO-PRONTO · revalidar READY_LEGACY pelo caminho CANONICO do Curator — numa COPIA.

O caminho canonico (curadoria/ready_split.py:291 `remedir`): a fonte READY_LEGACY
passa a CANARY_PENDING (o READY antigo fica no livro, append-only) e ganha a
tarefa VALIDATE_ROUTE; o worker valida a rota, enfileira o CANARY, e so promove
READY se a regua de HOJE passar na promocao (worker.py, «UM SO CANARIO PROMOVE»:
ready_split.passos_da_promocao). Nada e promovido a mao.

Este script so corre numa copia (git archive do vivo + livros copiados por cima):
  1. recusa se a copia apontar para o bot vivo;
  2. chama RS.remedir(ids) na copia;
  3. deixa na fila DA COPIA so as tarefas destas fontes (o resto da fila do vivo
     iria a rede por outras fontes: nao e desta prova);
  4. corre W.correr ate nao haver tarefa elegivel;
  5. escreve, por fonte: estado antes/depois, a ultima razao do livro e as provas.

Uso: py ferramentas/rendimento/revalidar_em_copia.py --copia C:/rend/copia-micro
        --ids IT-T3-002,IT-T3-010,IT-T2-002 --saida X.json
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main(argv):
    copia = Path(argv[argv.index("--copia") + 1]).resolve()
    ids = argv[argv.index("--ids") + 1].split(",")
    saida = Path(argv[argv.index("--saida") + 1])
    if "source-curator-service-v1" in str(copia).replace("\\", "/"):
        print("RECUSO: a copia aponta para o bot vivo")
        return 2
    sys.path.insert(0, str(copia / "curadoria"))
    import fila as F            # noqa: E402
    import lifecycle as LC      # noqa: E402
    import worker as W          # noqa: E402
    import ready_split as RS    # noqa: E402
    import collection_gate as G  # noqa: E402
    for p in (F.FILA, LC.LIVRO, W.CONTRATOS, W.EVIDENCIA):
        assert Path(p).resolve().is_relative_to(copia), p

    def retrato():
        est = LC.snapshot()
        return {s: {"ESTADO": est.get(s), "PORTAO": {k: v for k, v in G.avaliar(s, **G._contexto()).items()
                                                     if k in ("STATE", "READY_RULE", "COLLECTION_ELIGIBLE", "MOTIVO", "PORQUE")}}
                for s in ids}

    antes = retrato()
    feitas = RS.remedir(ids, motivo=("MICRO-PRONTO 25/09: revalidar READY_LEGACY pelas regras atuais "
                                     "(decisao do coordenador; so na copia)"))
    q = json.loads(Path(F.FILA).read_text(encoding="utf-8"))
    total = len(q["TAREFAS"])
    q["TAREFAS"] = [t for t in q["TAREFAS"] if t.get("SOURCE_ID") in ids]
    Path(F.FILA).write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
    print("fila da copia: %d tarefas -> %d (so estas fontes)" % (total, len(q["TAREFAS"])))

    passos = []
    for _ in range(12):
        feitos = W.correr(pausa=1.0, verboso=True)
        passos += [{k: f.get(k) for k in ("SOURCE_ID", "TASK_TYPE", "RESULTADO", "DETALHE", "MOTIVO") if k in f}
                   for f in feitos]
        if not feitos:
            break

    ev = json.loads(Path(W.EVIDENCIA).read_text(encoding="utf-8"))["PROVAS"]
    provas = {s: [p for p in ev if p["SOURCE_ID"] == s][-4:] for s in ids}
    livro = json.loads(Path(LC.LIVRO).read_text(encoding="utf-8"))
    linhas = livro.get("TRANSICOES") or livro.get("LINHAS") or livro.get("EVENTOS") or []
    ultimas = {s: [l for l in linhas if l.get("SOURCE_ID") == s][-3:] for s in ids}
    d = {"DATASET": "MICRO-PRONTO-REVALIDAR-EM-COPIA-V1",
         "MEDIDO_EM": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "COPIA": str(copia), "CAMINHO_CANONICO": "curadoria/ready_split.py:291 remedir -> VALIDATE_ROUTE -> CANARY -> promocao pela regua de hoje (worker.py)",
         "REMEDIR": feitas, "ANTES": antes, "DEPOIS": retrato(), "PASSOS_DO_WORKER": passos,
         "ULTIMAS_LINHAS_DO_LIVRO": ultimas, "PROVAS": provas}
    saida.write_text(json.dumps(d, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    for s in ids:
        print(s, antes[s]["ESTADO"], "->", d["DEPOIS"][s]["ESTADO"], "|", d["DEPOIS"][s]["PORTAO"].get("MOTIVO"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
