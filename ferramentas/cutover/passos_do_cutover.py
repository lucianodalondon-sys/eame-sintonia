"""Passos 5b, 5c e 7b do cutover — os tres que o SWITCH_PLAN nao tem e o ensaio X1 provou.

    py ferramentas/cutover/passos_do_cutover.py 5b --extras CORTE/servico-extras [--escrever]
    py ferramentas/cutover/passos_do_cutover.py 5c --livro-bot COPIA [--escrever]
    py ferramentas/cutover/passos_do_cutover.py 7b [--escrever]

Correm na RAIZ da worktree unificada (curadoria/ relativo). Sem --escrever so contam.

5b — os dois livros que unir_livros_do_servico nao trata. A viva tem linhas que a linha
     nao tem (ensaio: 430 candidatas, 302 SOURCE_ID) e o git checkout da troca deita-as
     fora (302 numeros voltariam a ser atribuidos). A viva e a dona destes livros (a ponte
     de candidatas promove, o alocador atribui): COPIA-SE a viva, e SO se ela contem a
     linha — cada CANDIDATA_ID e cada SOURCE_ID da linha tem de estar na viva (o SOURCE_ID
     igual); senao PARAR, porque alguem escreveu na linha o que a viva nao sabe.
     DEPOIS do 5b correr as correccoes idempotentes da linha (D13, D15, PAIS): a copia
     desfaz as que a linha fez nas linhas comuns (75 em e752c3da) e elas repoem-nas.
     Medido em e752c3da: copia+correccoes = viva + as 75 decididas, 76/76 PAIS da viva
     intactos. Juntar com «a linha vence» dava o mesmo hoje, mas apagaria uma PROMOVIDA
     escrita pela viva depois da ultima passagem.

5c — levar a marca CONTRATO_UNICO (D10) do livro do bot (a COPIA fora do corte que o
     pacote G1 marcou) para o livro unido, SO onde a ACQUISITION e igual. A uniao pos o
     contrato da ponte sem a marca: ensaios 1-3 perderam 6/6. Idempotente.

7b — enfileirar VALIDATE_ROUTE para TODAS as fontes da D10 cujo ultimo estado e
     CANARY_PENDING e que nao tem tarefa aberta. A reconciliacao despromove-as
     (DONO_DO_CONTRATO) e o REVALIDAR (B3) so olha READY: ninguem as re-mede. O ensaio 3
     provou que «as 6 marcadas» nao chega: IT-T5-049 nao tem marca e fica presa na mesma.
     Com o bot PARADO (a fila e do bot). Idempotente: quem ja tem tarefa aberta nao entra.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import medir_cutover as M  # noqa: E402

MOTIVO_7B = "re-medir: contrato novo ou despromovida pela reconciliacao (D10) — passo 7b do cutover"


def candidatas_fora_da_viva(linha: dict, viva: dict) -> list[str]:
    """CANDIDATA_IDs da linha que a viva nao tem (vazio = a copia nao perde linhas)."""
    tem = {r["CANDIDATA_ID"] for r in viva["CANDIDATAS"]}
    return sorted(r["CANDIDATA_ID"] for r in linha["CANDIDATAS"] if r["CANDIDATA_ID"] not in tem)


def alocacao_contida(linha: dict, viva: dict) -> list[str]:
    """SOURCE_IDs da linha que faltam na viva ou la estao diferentes (vazio = pode copiar)."""
    v = {r["SOURCE_ID"]: r for r in viva.get("NOVAS", [])}
    return sorted(r["SOURCE_ID"] for r in linha.get("NOVAS", []) if v.get(r["SOURCE_ID"]) != r)


def passo_5b(raiz: Path, extras: Path, escrever: bool) -> dict:
    pares = [(raiz / "candidatas" / "FONTES-CANDIDATAS.json", extras / "FONTES-CANDIDATAS.json"),
             (raiz / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json", extras / "SOURCE-ID-ALLOCATION-V1.json")]
    (lc, vc), (la, va) = [(json.loads(a.read_text(encoding="utf-8")), b.read_bytes()) for a, b in pares]
    viva_c, viva_a = json.loads(vc.decode("utf-8")), json.loads(va.decode("utf-8"))
    fora_c, fora_a = candidatas_fora_da_viva(lc, viva_c), alocacao_contida(la, viva_a)
    r = {"PASSO": "5b",
         "CANDIDATAS": {"LINHA": len(lc["CANDIDATAS"]), "VIVA": len(viva_c["CANDIDATAS"]), "FORA_DA_VIVA": fora_c},
         "ALOCACAO": {"LINHA": len(la.get("NOVAS", [])), "VIVA": len(viva_a.get("NOVAS", [])), "FORA_DA_VIVA": fora_a},
         "VEREDITO": "OK" if not (fora_c or fora_a) else "PARAR", "ESCRITO": 0,
         "A_SEGUIR": "aplicar_d13_capacidade.py --escrever; aplicar_d15_politica.py --escrever; "
                     "corrigir_pais_das_candidatas.py --aplicar (as que existirem no FINAL_HEAD)"}
    if escrever and r["VEREDITO"] == "OK":
        for (dst, _), b in zip(pares, (vc, va)):
            dst.write_bytes(b)
        r["ESCRITO"] = 2
    return r


def marcas_a_levar(unido: list, bot: list) -> list[str]:
    """SOURCE_IDs cuja marca CONTRATO_UNICO do bot entra no unido (aquisicao igual)."""
    b = {c["SOURCE_ID"]: c for c in bot}
    out = []
    for c in unido:
        o = b.get(c["SOURCE_ID"])
        if (o and o.get("CONTRATO_UNICO") and not c.get("CONTRATO_UNICO")
                and json.dumps(c.get("ACQUISITION"), sort_keys=True)
                == json.dumps(o.get("ACQUISITION"), sort_keys=True)):
            out.append(c["SOURCE_ID"])
    return out


def passo_5c(raiz: Path, livro_bot: Path, escrever: bool) -> dict:
    p = raiz / "curadoria" / "italy_contracts_curator.json"
    U = json.loads(p.read_text(encoding="utf-8"))
    B = json.loads(livro_bot.read_text(encoding="utf-8"))["FONTES"]
    levar = marcas_a_levar(U["FONTES"], B)
    if escrever and levar:
        b = {c["SOURCE_ID"]: c for c in B}
        for c in U["FONTES"]:
            if c["SOURCE_ID"] in levar:
                c["CONTRATO_UNICO"] = b[c["SOURCE_ID"]]["CONTRATO_UNICO"]
        p.write_text(json.dumps(U, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"PASSO": "5c", "LEVADAS": levar, "ESCRITO": len(levar) if escrever else 0}


def passo_7b(raiz: Path, escrever: bool) -> dict:
    cur = raiz / "curadoria"
    trans = json.loads((cur / "LIFECYCLE-LEDGER-V1.json").read_text(encoding="utf-8"))["TRANSICOES"]
    tarefas = json.loads((cur / "LIFECYCLE-QUEUE-V1.json").read_text(encoding="utf-8"))["TAREFAS"]
    presas = M.presas_sem_tarefa(trans, tarefas, M.D10)
    feitas = []
    if escrever and presas:
        sys.path.insert(0, str(cur))
        import fila as F
        for s in presas:
            t = F.enfileirar(s, F.VALIDATE_ROUTE, priority=55, motivo=MOTIVO_7B)
            feitas.append([s, t["TASK_ID"], t["STATUS"]])
    return {"PASSO": "7b", "PRESAS": presas, "ENFILEIRADAS": feitas}


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    escrever = "--escrever" in a
    raiz = Path.cwd()
    if a and a[0] == "5b" and "--extras" in a:
        r = passo_5b(raiz, Path(a[a.index("--extras") + 1]), escrever)
    elif a and a[0] == "5c" and "--livro-bot" in a:
        r = passo_5c(raiz, Path(a[a.index("--livro-bot") + 1]), escrever)
    elif a and a[0] == "7b":
        r = passo_7b(raiz, escrever)
    else:
        print(__doc__)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 2 if r.get("VEREDITO") == "PARAR" else 0


if __name__ == "__main__":
    sys.exit(main())
