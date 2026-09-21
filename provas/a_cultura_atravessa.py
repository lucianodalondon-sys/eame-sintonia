#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""A CULTURA ATRAVESSA — onde se perde, e a rederivação que a recupera.

    MISSAO   C-CROP-E2E-V1
    NATUREZA cirurgia sobre os 5 itens IT-T3 da Sala. NETWORK = OFF.

A PERGUNTA
----------
O piloto da Sala (R2) contou: 5 de 5 boletins IT-T3 com a cultura ESCRITA no
texto e sem campo onde pousar — `CROP_LOST_IN_DERIVATION = 100%`. Este
ficheiro responde a duas perguntas, por item, e nunca por média:

    1. EM QUE ETAPA a cultura se perde?         (FASE 1 · medir)
    2. os bytes JÁ GUARDADOS chegam para a
       recuperar, sem recoletar nada?           (FASE 5 · rederivar)

O QUE ELE FAZ, E O QUE NÃO FAZ
------------------------------
    LÊ      `sala_de_espera`, `raw_asset`, `derived_artifact`, o armazém local.
    DERIVA  com `--gravar`, chama `coleta/executor_secoes_por_cultura.derivar_um`
            sobre os bytes que já estão no armazém — pelo DONO da escrita
            (`guarda/preservar_derivado.py`), nunca por SQL próprio.
    NÃO     cria observação (`raw_asset`), NÃO cria corrida (`collection_run`),
            NÃO duplica bytes no armazém, NÃO abre rede, NÃO toca na Sala.

A REFERÊNCIA CANÓNICA
---------------------
A Sala não ganha coluna `crop`, e a razão é de grão: um boletim de Salerno
tem DOZE culturas; a cultura é da SECÇÃO, não do item. O contrato READY
(COL-LAW-043) fica intacto. O que a Intelligence segue é o ponteiro que a
Sala já carrega:

    sala.item_id = "derived:N"
      → derived_artifact.id = N            (o texto que a porta julgou)
      → derived_artifact.parent_sha256     (os bytes do original)
      → derived_artifact WHERE kind = TABLE_EXTRACTION
                            AND producer = secoes-por-cultura
      → storage_path no armazém            (as secções, com cultura e âncora)

COMO CORRER
-----------
    set SINTONIA_SALA_DSN=postgresql://...        (nunca em argv)
    set SINTONIA_PSQL_EXE=C:/.../psql.exe
    py provas/a_cultura_atravessa.py --armazem <raiz do armazém operacional>
    py provas/a_cultura_atravessa.py --armazem <raiz> --gravar
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import executor_secoes_por_cultura as sec  # noqa: E402
import admissao  # noqa: E402
from guarda.memoria_postgres import MemoriaPostgres  # noqa: E402
from guarda.preservar_coleta import ArmazemLocal, sha256  # noqa: E402
from guarda import preservar_derivado as pd  # noqa: E402

MISSAO = "C-CROP-E2E-V1"
FAMILIA = "IT-T3"
NAO_SEI = "NAO SEI"
NAO_SE_APLICA = "NAO_SE_APLICA"

COLS_SALA = ("run_id", "ordem", "item_id", "raw_observation_id", "source_id",
             "universo", "estagio", "texto_sha256", "texto_chars", "texto")
COLS_RAW = ("id", "run_id", "source_id", "sha256", "storage_path", "media_type",
            "bytes")
COLS_DER = ("id", "raw_asset_id", "parent_sha256", "kind", "producer",
            "producer_version", "sha256", "storage_path", "media_type", "bytes")


def _q(v):
    return "'" + str(v).replace("'", "''") + "'"


def ler_sala_t3(memoria):
    u"""Os itens IT-T3 da Sala, com a impressão do texto medida NO BANCO."""
    return memoria._linhas(
        "select run_id, ordem, item_id, raw_observation_id, source_id, universo, "
        "estagio, encode(sha256(convert_to(texto,'UTF8')),'hex'), length(texto), "
        "replace(encode(convert_to(texto,'UTF8'),'base64'), E'\\n', '') "
        "from public.sala_de_espera where source_id like %s "
        "order by source_id, pousado_em" % _q(FAMILIA + "%"), COLS_SALA)


def _texto(linha):
    import base64
    return base64.b64decode(linha["texto"].replace("\n", "")).decode("utf-8")


def raw_por_id(memoria, raw_id):
    linhas = memoria._linhas(
        "select id, run_id, source_id, sha256, storage_path, media_type, bytes "
        "from public.raw_asset where id = %d" % int(raw_id), COLS_RAW)
    return linhas[0] if linhas else None


def derivado_por_id(memoria, derived_id):
    linhas = memoria._linhas(
        "select id, raw_asset_id, parent_sha256, kind, producer, producer_version, "
        "sha256, storage_path, media_type, bytes from public.derived_artifact "
        "where id = %d" % int(derived_id), COLS_DER)
    return linhas[0] if linhas else None


def irmao_de_seccoes(memoria, parent_sha256):
    u"""A derivação de secções deste original, se existir. É ESTA a referência
    que a Intelligence segue — a mesma consulta vive em
    `provas/o_piloto_da_sala.py::ler_secoes_por_cultura`."""
    linhas = memoria._linhas(
        "select id, raw_asset_id, parent_sha256, kind, producer, producer_version, "
        "sha256, storage_path, media_type, bytes from public.derived_artifact "
        "where parent_sha256 = %s and kind = %s and producer = %s "
        "order by id desc limit 1"
        % (_q(parent_sha256), _q(sec.KIND), _q(sec.EXECUTOR_ID)), COLS_DER)
    return linhas[0] if linhas else None


def id_do_derivado(item_id):
    m = re.match(r"^derived:(\d+)$", str(item_id or ""))
    return int(m.group(1)) if m else None


def contagens(memoria):
    return {t: memoria.contar(t) for t in
            ("raw_asset", "collection_run", "storage_object", "derived_artifact",
             "sala_de_espera", "participacao_na_derivacao")}


def sala_tem_coluna_crop(memoria):
    n = memoria._valor(
        "select count(*) from information_schema.columns where table_name = "
        "'sala_de_espera' and column_name in ('crop','cultura','crop_key')")
    return int(n) > 0


def ready_tem_campo_crop():
    u"""O contrato READY, perguntado ao dono e não a um documento."""
    d = admissao.Decisao(item="x", resultado=admissao.SIM, regra="r", versao="1",
                         motivo="m", universo="T3", corrida="c") \
        if hasattr(admissao, "Decisao") else None
    if d is None:
        return NAO_SEI
    campos = admissao.pronto_para_inteligencia({"id": "x", "texto": "t"}, d).keys()
    return any(k.upper() in ("CROP", "CULTURA", "CROP_KEY") for k in campos)


def medir_item(memoria, armazem, linha, gravar):
    u"""FASE 1 por item: as sete presenças, e a etapa em que a cultura se perde.

    Nenhuma média. Cada item responde por si, e «não assumir que todos
    quebram no mesmo ponto» é literalmente o que esta função faz.
    """
    texto = _texto(linha)
    raw = raw_por_id(memoria, linha["raw_observation_id"]) \
        if linha.get("raw_observation_id") else None
    did = id_do_derivado(linha["item_id"])
    der = derivado_por_id(memoria, did) if did else None
    caminho = raw["storage_path"] if raw else None
    bytes_locais = bool(caminho) and armazem.existe(caminho)
    sha_bate = None
    if bytes_locais:
        sha_bate = sha256(armazem.ler(caminho)) == raw["sha256"]

    # O texto QUE A SALA TEM, secionado. É a medição «o cabeçalho sobreviveu
    # à extração?» — feita sobre o que a porta julgou, não sobre bytes novos.
    s_sala = sec.seccionar(texto)
    r = s_sala["RESUMO"]
    no_texto = ("SIM" if r["EXPLICIT"] else
                ("SO_CONTEXTO" if r["CONTEXT_ONLY"] else "NAO"))
    na_tabela = "SIM" if any(
        x["STATUS"] == sec.EXPLICIT and x["KIND"] in (sec.SECTION_HEADER, sec.TABLE_TITLE)
        for x in s_sala["SECOES"]) else "NAO"

    # Nos bytes: só se pode afirmar sobre bytes que EXISTEM localmente.
    if not bytes_locais:
        nos_bytes = "NAO SEI — bytes ausentes do armazém local (dívida §161); a rede está fechada"
    elif not sha_bate:
        nos_bytes = "NAO SEI — o ficheiro local não bate com o sha256 do raw_asset"
    else:
        s_bytes, estado, _e, _m = sec.extrair(armazem.caminho_local(caminho))
        if s_bytes is None:
            nos_bytes = "NAO SEI — sem camada de texto (%s)" % estado
        elif s_bytes["RESUMO"]["EXPLICIT"]:
            nos_bytes = "SIM — cabeçalho de cultura na camada de texto"
        elif s_bytes["RESUMO"]["CONTEXT_ONLY"]:
            nos_bytes = ("NAO SEI — a camada de texto só tem menções; o cabeçalho "
                         "é gráfico (ARIF: ícone 124x129) e esta casa não faz OCR")
        else:
            nos_bytes = "NAO — nem cabeçalho nem menção na camada de texto"

    irmao = irmao_de_seccoes(memoria, raw["sha256"]) if raw else None
    no_derivado = "SIM" if irmao else "NAO"

    # Onde se perde — por item, e com o motivo escrito.
    if not raw:
        perda = "NAO SEI — a Sala não aponta para observação"
    elif r["EXPLICIT"] and not irmao:
        perda = ("STRUCTURED — o cabeçalho sobreviveu ao TEXT_EXTRACTION e nenhuma "
                 "derivação o lia; a tabela virou texto corrido e ninguém ligou "
                 "cabeçalho a bloco")
    elif r["EXPLICIT"] and irmao:
        perda = "RECUPERADA — a derivação de secções existe e a Intelligence a alcança"
    elif not bytes_locais:
        perda = ("DERIVED (por inferência) — o texto da Sala mostra o padrão ARIF "
                 "sem cabeçalho; os bytes não estão cá para confirmar")
    else:
        perda = ("DERIVED — o cabeçalho não está na camada de texto (ícone); o "
                 "TEXT_EXTRACTION nunca o teve, e sem OCR ninguém o terá")

    return {
        "SOURCE_ID": linha["source_id"],
        "RUN_ID": linha["run_id"], "ORDEM": int(linha["ordem"]),
        "ITEM_ID": linha["item_id"],
        "RAW_ASSET_ID": int(linha["raw_observation_id"]) if linha.get("raw_observation_id") else NAO_SEI,
        "RAW_SHA256": raw["sha256"] if raw else NAO_SEI,
        "STORAGE_OBJECT_PATH": caminho or NAO_SEI,
        "DERIVED_ID": did or NAO_SEI,
        "DERIVED_TEXT_SHA256": der["sha256"] if der else NAO_SEI,
        "SALA_ID": {"RUN_ID": linha["run_id"], "ORDEM": int(linha["ordem"])},
        "SALA_TEXTO_SHA256": linha["texto_sha256"],
        "SALA_TEXTO_CHARS": int(linha["texto_chars"]),
        "BYTES_LOCAIS": bytes_locais,
        "BYTES_SHA_BATE": sha_bate,
        "CROP_PRESENT_IN_BYTES": nos_bytes,
        "CROP_PRESENT_IN_EXTRACTED_TEXT": no_texto,
        "CROP_PRESENT_IN_TABLE_STRUCTURE": na_tabela,
        "CROP_PRESENT_IN_DERIVED": no_derivado,
        "CROP_PRESENT_IN_ADMISSION": "NAO_SE_APLICA — o READY não tem campo de cultura; o grão é a secção",
        "CROP_PRESENT_IN_SALA": "NAO_SE_APLICA — sem coluna; a Sala aponta por item_id=derived:N",
        "CROP_VISIBLE_TO_INTELLIGENCE": ("SIM — pela referência canónica (irmão %s)" % irmao["id"]
                                         if irmao else "NAO — ainda não há derivação de secções"),
        "CROP_LOSS_STAGE": perda,
        "SECOES_NO_TEXTO_DA_SALA": {k: r[k] for k in ("SECOES", "EXPLICIT", "CONTEXT_ONLY",
                                                     "UNKNOWN", "CROPS_EXPLICIT",
                                                     "CROPS_CONTEXT_ONLY")},
        "IRMAO_SECOES": ({"DERIVED_ID": irmao["id"], "STORAGE_PATH": irmao["storage_path"]}
                         if irmao else None),
    }


def rederivar(memoria, armazem, medido, gravar):
    u"""FASE 5: SÓ os bytes que já existem. Um original → uma derivação; a
    segunda observação dos mesmos bytes REENCONTRA (REUSED), não duplica."""
    fora = []
    for m in medido:
        raw_id, caminho = m["RAW_ASSET_ID"], m["STORAGE_OBJECT_PATH"]
        if not m["BYTES_LOCAIS"] or not m["BYTES_SHA_BATE"]:
            fora.append({"RAW_ASSET_ID": raw_id, "ESTADO": "NAO_REDERIVADO",
                         "PORQUE": "bytes ausentes ou sem prova de identidade; "
                                   "sem rede não há como os obter"})
            continue
        if not gravar:
            s, estado, _e, _m = sec.extrair(armazem.caminho_local(caminho))
            fora.append({"RAW_ASSET_ID": raw_id, "ESTADO": "ENSAIO_SEM_GRAVAR",
                         "EXTRACAO": estado,
                         "RESUMO": s["RESUMO"] if s else None})
            continue
        r = sec.derivar_um(int(raw_id), armazem.caminho_local(caminho), armazem,
                           memoria, contexto_da_passagem=None)
        linha = r.get("LINHA_ESCRITA") or r.get("LINHA_EXISTENTE") or {}
        fora.append({"RAW_ASSET_ID": raw_id, "ESTADO": r.get("ESTADO"),
                     "PORQUE": r.get("PORQUE"),
                     "DERIVED_ID": linha.get("id"),
                     "STORAGE_PATH": linha.get("storage_path") or r.get("STORAGE_PATH"),
                     "NOVO_UPLOAD": r.get("NOVO_UPLOAD"),
                     "PARTICIPACAO": (r.get("PARTICIPACAO") or {}).get("ESTADO")})
    return fora


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--armazem", required=True, help="raiz do armazém operacional")
    ap.add_argument("--dsn", help="DSN da Sala; por omissão SINTONIA_SALA_DSN")
    ap.add_argument("--gravar", action="store_true",
                    help="escreve as derivações pelo dono canónico")
    ap.add_argument("--json", default=os.path.join(RAIZ, "data", "derivados",
                                                   "A-CULTURA-ATRAVESSA.json"))
    args = ap.parse_args()
    url = args.dsn or os.environ.get("SINTONIA_SALA_DSN") or ""
    if not url.strip():
        raise SystemExit("SINTONIA_SALA_DSN ausente (e --dsn não dado). Nada medido.")
    memoria = MemoriaPostgres(url)
    armazem = ArmazemLocal(args.armazem)

    antes = contagens(memoria)
    itens = ler_sala_t3(memoria)
    medido = [medir_item(memoria, armazem, l, args.gravar) for l in itens]
    rederivado = rederivar(memoria, armazem, medido, args.gravar)
    # Medir OUTRA VEZ, depois de gravar: o que a Intelligence vê agora.
    depois_itens = [medir_item(memoria, armazem, l, False) for l in itens] \
        if args.gravar else medido
    depois = contagens(memoria)

    recuperados = [m for m in depois_itens if m["IRMAO_SECOES"]
                   and m["SECOES_NO_TEXTO_DA_SALA"]["EXPLICIT"] > 0]
    unknown = [m for m in depois_itens if m["IRMAO_SECOES"]
               and m["SECOES_NO_TEXTO_DA_SALA"]["EXPLICIT"] == 0]
    falhados = [m for m in depois_itens if not m["IRMAO_SECOES"]]

    artefato = {
        "SCHEMA": "sintonia.collection.a-cultura-atravessa/1",
        "MISSAO": MISSAO,
        "GRAVAR": args.gravar,
        "NETWORK": "OFF — nenhum socket aberto por este processo; só psql local e disco",
        "T3_TOTAL": len(medido),
        "T3_REDERIVED": sum(1 for r in rederivado
                            if r["ESTADO"] in (pd.INSERTED, pd.REUSED, pd.REUSED_AFTER_RACE)),
        "T3_CROP_RECOVERED": len(recuperados),
        "T3_CROP_UNKNOWN": len(unknown),
        "T3_FAILED": len(falhados),
        "READY_TEM_CAMPO_CROP": ready_tem_campo_crop(),
        "SALA_TEM_COLUNA_CROP": sala_tem_coluna_crop(memoria),
        "REFERENCIA_CANONICA": (
            "sala.item_id=derived:N -> derived_artifact.id=N -> parent_sha256 -> "
            "derived_artifact(kind=%s, producer=%s) -> storage_path"
            % (sec.KIND, sec.EXECUTOR_ID)),
        "CONTAGENS_ANTES": antes,
        "CONTAGENS_DEPOIS": depois,
        "NEW_OBSERVATIONS_CREATED": depois["raw_asset"] - antes["raw_asset"],
        "NEW_COLLECTION_RUNS": depois["collection_run"] - antes["collection_run"],
        "NEW_STORAGE_OBJECTS": depois["storage_object"] - antes["storage_object"],
        "NEW_DERIVED_ARTIFACTS": depois["derived_artifact"] - antes["derived_artifact"],
        "SALA_ROWS_DELTA": depois["sala_de_espera"] - antes["sala_de_espera"],
        "FASE_1_ANTES": medido,
        "FASE_5_REDERIVACAO": rederivado,
        "FASE_6_DEPOIS": depois_itens,
    }
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(artefato, ensure_ascii=False, indent=1) + "\n")
    print("artefato: %s" % args.json)
    for k in ("T3_TOTAL", "T3_REDERIVED", "T3_CROP_RECOVERED", "T3_CROP_UNKNOWN",
              "T3_FAILED", "NEW_OBSERVATIONS_CREATED", "NEW_COLLECTION_RUNS",
              "NEW_STORAGE_OBJECTS", "NEW_DERIVED_ARTIFACTS", "SALA_ROWS_DELTA",
              "READY_TEM_CAMPO_CROP", "SALA_TEM_COLUNA_CROP"):
        print("%-26s = %s" % (k, artefato[k]))
    for m in depois_itens:
        print("  %s obs=%s  texto=%s  tabela=%s  derivado=%s  | %s"
              % (m["SOURCE_ID"], m["RAW_ASSET_ID"], m["CROP_PRESENT_IN_EXTRACTED_TEXT"],
                 m["CROP_PRESENT_IN_TABLE_STRUCTURE"], m["CROP_PRESENT_IN_DERIVED"],
                 m["CROP_LOSS_STAGE"][:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
