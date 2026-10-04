#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CANÁRIO DA ROTA DO HTML — bytes reais, banco descartável, ZERO rede.

    CAPABILITY EXISTS != EDGE EXISTS.

`coleta/texto_fonte.py::limpar()` extraía texto de HTML muito antes desta
missão e **ninguém a chamava** no código de produção. Medido a 2026-09-21:
46 observações reais paravam em `DERIVED` com `MISSING_ROUTE` — não porque a
etapa não se aplicasse, mas porque nenhum executor declarava `text/html`.

Este canário prova a rota INTEIRA numa execução, com os bytes que o armazém
já tem no disco:

    RAW (text/html)  ->  ingresso.executor_para  ->  executor_texto_de_html
                     ->  guarda/preservar_derivado  ->  derived_artifact
                     ->  admissao.decidir

O QUE ELE NÃO FAZ
-----------------
Não vai à rede. Não toca na Sala operacional. O banco é
`guarda/memoria_descartavel.MemoriaDescartavel` — SQLite em memória, morre no
fim. O armazém é `ArmazemDeMentira` — um dicionário.

⚠️ E O CANÁRIO NÃO CHAMA O EXECUTOR PELO NOME. Ele chama
`derivacao_forward.correr()` com a espécie declarada na unidade, e deixa a
ESCOLHA acontecer. Um canário que importasse `executor_texto_de_html` e lhe
chamasse `derivar_um` provaria que a ferramenta funciona — e é exactamente
isso que já se sabia antes desta missão.

    UM CANÁRIO QUE ESCOLHE O EXECUTOR NÃO PROVA A ROTA:
    PROVA A FERRAMENTA, QUE NUNCA ESTEVE EM CAUSA.

CORRER
------
    py provas/a_rota_do_html_atravessa.py
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
import ingresso as ing  # noqa: E402

from coleta import derivacao_forward as deriv  # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira  # noqa: E402

# ── O CANÁRIO, ESCOLHIDO E NÃO SORTEADO ─────────────────────────────────────
# O mais pequeno dos 46 (38 117 bytes), de `IT-T5-049`. Pequeno de propósito:
# um canário grande esconde no tempo de corrida os defeitos que ele devia
# mostrar. A identidade vem do censo da última milha
# (`medidas/COORTE-MICRO-COLLECTION-V1.json`), e não de um `glob` no disco —
# `PATH != IDENTITY`.
CANARIO = {
    "RAW_ASSET_ID": "1118",
    "SOURCE_ID": "IT-T5-049",
    "UNIVERSO": "T5",
    "RUN_ID": "IT-T5-2026-09-21-192807-551e1a130e552533",
    "SHA256": "70ae4c4a6eed" ,                       # prefixo do caminho
    "LOCAL_FILE": ("data/collection-store/italy/IT-T5-049/"
                   "IT-T5-049_URL_it_notizie_welcome-day-1/"
                   "v1_70ae4c4a6eed/welcome-day-1.html"),
    "DETAIL_URL": "https://www.unito.it/it/notizie/welcome-day-1",
    "CAPTURED_AT": "2026-09-21T19:28:07Z",
}

RELOGIO = lambda: "2026-09-21T23:00:00Z"              # noqa: E731
CORRIDA = "CANARIO-HTML-V1"


def _sha_do_ficheiro(caminho):
    import hashlib
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def montar_o_pai(banco, sha, caminho_no_armazem, bytes_):
    """A linha `raw_asset` do canário, no banco descartável.

    ⚠️ ISTO NÃO É A COLETA. A observação REAL já existe no Postgres canónico
    (`raw_asset 1118`), e este canário não lhe toca. O que se recria aqui é o
    PAI mínimo que o dono do derivado exige por chave estrangeira, com o
    `media_type` que a coleta mediu de verdade: `text/html`.
    """
    banco.aplicar(
        "insert into public.collection_run (run_id, platform, started_at, "
        "rule_version, source_country) values ('%s','t','%s','1','IT') "
        "on conflict (run_id) do nothing;"
        % (CORRIDA, CANARIO["CAPTURED_AT"]))
    banco.aplicar(
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('%s','text/html',%d,'%s') "
        "on conflict (storage_path) do nothing;"
        % (caminho_no_armazem, bytes_, sha))
    banco.aplicar(
        "insert into public.raw_asset (run_id, storage_path, media_type, "
        "bytes, sha256, captured_at, storage_object_id, identity_state, "
        "source_id, document_key, document_key_basis) "
        "select '%s','%s','text/html',%d,'%s','%s', o.id, "
        "'FORWARD_IDENTIFIED','%s','DOC:%s','SOURCE_DOCUMENT_ID' "
        "from public.storage_object o where o.storage_path = '%s';"
        % (CORRIDA, caminho_no_armazem, bytes_, sha, CANARIO["CAPTURED_AT"],
           CANARIO["SOURCE_ID"], sha[:12], caminho_no_armazem))
    return int(banco.con.execute(
        "select id from raw_asset where storage_path = ?",
        (caminho_no_armazem,)).fetchone()[0])


def correr():
    fora = {"CANARIO": CANARIO, "REDE": "nenhuma", "ESCREVE_NA_SALA": False}
    caminho = os.path.join(RAIZ, CANARIO["LOCAL_FILE"])

    # ── 0 · HTML_RAW — os bytes existem, e são o que a coleta disse ─────────
    fora["HTML_RAW"] = {
        "FICHEIRO_EXISTE": os.path.isfile(caminho),
        "BYTES": os.path.getsize(caminho) if os.path.isfile(caminho) else 0,
    }
    if not fora["HTML_RAW"]["FICHEIRO_EXISTE"]:
        fora["VEREDICTO"] = "FAIL: os bytes do canario nao estao no disco"
        return fora
    sha = _sha_do_ficheiro(caminho)
    fora["HTML_RAW"]["SHA256"] = sha
    fora["HTML_RAW"]["MEDIA_TYPE_DECLARADO"] = "text/html"

    # ── 1 · A ESCOLHA, feita pelo dono da pergunta ──────────────────────────
    # ⚠️ Esta é a linha que valia MISSING_ROUTE. Antes desta missão devolvia
    # `None`, e `None` fazia `derivacao_forward` cair no executor de PDF.
    escolhido = ing.executor_para("text/html")
    fora["ROUTE_CHOICE"] = {
        "PERGUNTA": 'ingresso.executor_para("text/html")',
        "EXECUTOR_ID": getattr(escolhido, "EXECUTOR_ID", None),
        "MODULO": getattr(escolhido, "__name__", None),
        # As outras duas espécies não podem ter mudado de dono.
        "PDF_CONTINUA": getattr(ing.executor_para("application/pdf"),
                                "EXECUTOR_ID", None),
        "VIDEO_CONTINUA": getattr(ing.executor_para("video/mp4"),
                                  "EXECUTOR_ID", None),
    }

    # ── 2 · A DERIVAÇÃO, pelo RUNNER — sem nomear o executor ────────────────
    banco = MemoriaDescartavel()
    armazem = ArmazemDeMentira()
    try:
        no_armazem = "IT/unito/DOCUMENT/%s-canario-welcome-day.html" % sha[:16]
        with open(caminho, "rb") as fh:
            armazem.enviar(no_armazem, fh.read(), "text/html")
        pai = montar_o_pai(banco, sha, no_armazem,
                           fora["HTML_RAW"]["BYTES"])

        unidade = {"RAW_ASSET_ID": pai,
                   "PDF": caminho,          # o nome do campo é histórico
                   "MEDIA_TYPE": "text/html",
                   "SOURCE_ID": CANARIO["SOURCE_ID"],
                   "CAPTURED_AT": CANARIO["CAPTURED_AT"]}

        recibo = deriv.correr([unidade], banco_do_rastro=None,
                              run_id=CORRIDA, armazem=armazem, memoria=banco,
                              source_id=CANARIO["SOURCE_ID"],
                              route_class_id=None, relogio=RELOGIO)
        resultado = (recibo.get("RESULTADOS") or [{}])[0]
        linha = resultado.get("LINHA") or {}

        # ── 3 · TEXT_OUTPUT · NONEMPTY_TEXT ────────────────────────────────
        texto = ""
        if linha.get("storage_path") in armazem.objetos:
            texto = armazem.ler(linha["storage_path"]).decode("utf-8")
        fora["TEXT_OUTPUT"] = {
            "PORTA": resultado.get("PORTA"),
            "EXECUTOR_QUE_CORREU": resultado.get("EXECUTOR_ID"),
            "KIND": linha.get("kind"),
            "MEDIA_TYPE": linha.get("media_type"),
            "STORAGE_PATH": linha.get("storage_path"),
            "BALDES": recibo.get("BALDES"),
        }
        fora["NONEMPTY_TEXT"] = {
            "CARACTERES": len(texto),
            "CARACTERES_SEM_BRANCOS": len("".join(texto.split())),
            "PRIMEIROS_120": texto[:120].replace("\n", " "),
        }

        # ── 4 · PROVENANCE_PRESERVED ───────────────────────────────────────
        # O pai por ID e o pai por SHA têm de ser o MESMO pai, e o `producer`
        # tem de ser quem realmente correu. Os valores são LIDOS da linha que
        # o dono escreveu e releu — não são os que o canário pediu.
        unidade_de_texto = resultado.get("TEXT_UNIT") or {}
        lin = (unidade_de_texto.get("LINEAGE") or {})
        # ⚠️ A RECEITA LÊ-SE DO BANCO, E NÃO DO RECIBO EM MEMÓRIA. O que
        # sobrevive ao processo é a linha; um recibo que concorda consigo
        # próprio não prova persistência nenhuma.
        guardado = banco.con.execute(
            "select parameters, producer, producer_version, kind, media_type "
            "from derived_artifact where storage_path = ?",
            (linha.get("storage_path"),)).fetchone()
        receita = json.loads(guardado["parameters"]) if guardado else {}
        participacoes = banco.con.execute(
            "select count(*) from participacao_na_derivacao "
            "where first_seen_derivation_run_id = ?", (CORRIDA,)).fetchone()[0]
        fora["PROVENANCE_PRESERVED"] = {
            "RECEITA_NO_BANCO": receita,
            "PARTICIPACOES_ESCRITAS": participacoes,
            "raw_asset_id": linha.get("raw_asset_id"),
            "PAI_ESPERADO": pai,
            "parent_sha256": linha.get("parent_sha256"),
            "SHA_DO_PAI_NO_DISCO": sha,
            "producer": linha.get("producer"),
            "producer_version": linha.get("producer_version"),
            "TEXT_KIND": resultado.get("TEXT_KIND"),
            "TEXT_RELATION": resultado.get("TEXT_RELATION"),
            "DERIVATION_METHOD": lin.get("DERIVATION_METHOD"),
            "TOOL": lin.get("TOOL"),
            "LANGUAGE": unidade_de_texto.get("LANGUAGE"),
            "LINHAS_NO_BANCO": banco.contar("derived_artifact"),
        }

        # ── 5 · ADMISSION_RECEIVES_OUTPUT ──────────────────────────────────
        # O item é montado como a rota canónica o monta: o texto que a
        # derivação ACABOU de produzir, lido do armazém pelo `storage_path` da
        # linha — e não um texto que veio de outro sítio.
        item = ing.para_a_porta({"SOURCE_ID": CANARIO["SOURCE_ID"],
                                 "ARTIFACT_TYPE": "DERIVED",
                                 "PARENT_SHA256": linha.get("parent_sha256")})
        item.update({"id": "obs:%s" % CANARIO["RAW_ASSET_ID"],
                     "texto": texto,
                     "url": CANARIO["DETAIL_URL"],
                     "captured_at": CANARIO["CAPTURED_AT"],
                     "raw_asset_id": CANARIO["RAW_ASSET_ID"]})
        d = adm.decidir(item, CANARIO["UNIVERSO"], corrida=CORRIDA)
        # E o MESMO item sem o texto — para o contraste ser medido, e não
        # afirmado: é exactamente o que a porta recebia antes desta rota.
        sem_texto = dict(item)
        sem_texto.pop("texto")
        d_antes = adm.decidir(sem_texto, CANARIO["UNIVERSO"], corrida=CORRIDA)
        fora["ADMISSION_RECEIVES_OUTPUT"] = {
            "COM_TEXTO": {"resultado": d.resultado, "regra": d.regra,
                          "motivo": str(d.motivo)[:200],
                          "estagio": (d.evidencia or {}).get("estagio")},
            "SEM_TEXTO_COMO_ERA_ANTES": {"resultado": d_antes.resultado,
                                         "regra": d_antes.regra,
                                         "motivo": str(d_antes.motivo)[:160]},
        }
    finally:
        banco.fechar()

    fora["VEREDICTO"] = veredicto(fora)
    return fora


def veredicto(f):
    """Os cinco carimbos, cada um com o seu critério ESCRITO À MÃO.

    ⚠️ NENHUM DELES SE LÊ DA ESTRUTURA QUE ESTÁ A JULGAR. Três vezes nesta
    casa o sobrevivente do red team foi um teste que iterava a constante que
    verificava — por isso os valores esperados estão literais aqui.
    """
    checks = {
        "HTML_RAW": (f["HTML_RAW"]["FICHEIRO_EXISTE"]
                     and f["HTML_RAW"]["BYTES"] > 0),
        "ROUTE_CHOICE": (f["ROUTE_CHOICE"]["EXECUTOR_ID"] == "texto-de-html"
                         and f["ROUTE_CHOICE"]["PDF_CONTINUA"] == "texto-de-pdf"
                         and f["ROUTE_CHOICE"]["VIDEO_CONTINUA"]
                         == "transcricao-de-midia"),
        "TEXT_OUTPUT": (f["TEXT_OUTPUT"]["PORTA"] == "PASSED"
                        and f["TEXT_OUTPUT"]["KIND"] == "TEXT_EXTRACTION"
                        and f["TEXT_OUTPUT"]["MEDIA_TYPE"] == "text/plain"
                        and f["TEXT_OUTPUT"]["EXECUTOR_QUE_CORREU"]
                        == "texto-de-html"),
        "NONEMPTY_TEXT": f["NONEMPTY_TEXT"]["CARACTERES_SEM_BRANCOS"] > 0,
        "PROVENANCE_PRESERVED": (
            f["PROVENANCE_PRESERVED"]["raw_asset_id"]
            == f["PROVENANCE_PRESERVED"]["PAI_ESPERADO"]
            and f["PROVENANCE_PRESERVED"]["parent_sha256"]
            == f["PROVENANCE_PRESERVED"]["SHA_DO_PAI_NO_DISCO"]
            and f["PROVENANCE_PRESERVED"]["producer"] == "texto-de-html"
            and f["PROVENANCE_PRESERVED"]["TEXT_KIND"] == "PAGE_TEXT"
            and f["PROVENANCE_PRESERVED"]["TEXT_RELATION"] == "ORIGINAL"
            and f["PROVENANCE_PRESERVED"]["DERIVATION_METHOD"]
            == "EXTRACTED_FROM_DOCUMENT"
            and f["PROVENANCE_PRESERVED"]["TOOL"]
            == "coleta/texto_fonte.py::limpar"
            and f["PROVENANCE_PRESERVED"]["LANGUAGE"] == "UNKNOWN"
            and f["PROVENANCE_PRESERVED"]["LINHAS_NO_BANCO"] == 1
            # A receita persistida diz a espécie do texto sem que ninguém
            # tenha de ler o texto para a adivinhar.
            and f["PROVENANCE_PRESERVED"]["RECEITA_NO_BANCO"].get("TEXT_KIND")
            == "PAGE_TEXT"
            and f["PROVENANCE_PRESERVED"]["RECEITA_NO_BANCO"].get("TEXT_BASIS")
            == "DECLARED_BY_ROUTE"
            and f["PROVENANCE_PRESERVED"]["RECEITA_NO_BANCO"].get("TEXT_OWNER")
            == "coleta/texto_fonte.py::limpar"
            # A aresta (observação, derivado) ficou escrita — `RUNTIME SABE !=
            # O SISTEMA GUARDA`.
            and f["PROVENANCE_PRESERVED"]["PARTICIPACOES_ESCRITAS"] == 1),
        # ⚠️ O CARIMBO NÃO EXIGE `SIM`. Ele exige que a porta tenha JULGADO o
        # texto — ou seja, que a decisão já não seja a do portão `legivel`. Um
        # canário que exigisse `SIM` estaria a pedir à admissão que aprovasse,
        # e a admissão é um juízo, não um carimbo.
        "ADMISSION_RECEIVES_OUTPUT": (
            f["ADMISSION_RECEIVES_OUTPUT"]["COM_TEXTO"]["regra"] != "legivel"
            and f["ADMISSION_RECEIVES_OUTPUT"]["SEM_TEXTO_COMO_ERA_ANTES"]
            ["regra"] == "legivel"),
    }
    return {"CHECKS": checks,
            "PASS": all(checks.values()),
            "FALHARAM": [k for k, v in checks.items() if not v]}


def main():
    r = correr()
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    v = r.get("VEREDICTO") or {}
    return 0 if v.get("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
