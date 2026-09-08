#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CANÁRIO — uma captura italiana nova, do princípio ao fim.

O QUE ISTO PROVA, E O QUE NÃO USA
---------------------------------
    NÃO SE USA HISTÓRIA VELHA PARA PROVAR CAMINHO NOVO.

Nada aqui parte de um ficheiro no disco, de um SHA do ledger, ou dos 43
derivados históricos. A cadeia inteira nasce de **um GET real, hoje**:

    FONTE REAL → RUN REAL → RAW REAL → STORAGE REAL → raw_asset REAL
    → EXECUTOR REAL → WRITER REAL → derived_artifact REAL → READBACK REAL

UMA unidade. Uma fonte, um documento, uma corrida.

OS PORTÕES
----------
Cada etapa tem portão, e portão fechado **para**. Não se conserta produção no
improviso, e não se avança «só para ver o resto».

O CANDIDATO
-----------
O boletim agrometeorológico da ARPAV (Veneto), zona 01. Escolhido por três
razões medidas, não por conveniência:

  · a `SOURCE_URL` está provada no ledger italiano, com recibo;
  · o ficheiro é **rolante** — a ARPAV reescreve-o a cada semana. Isso
    torna a captura de hoje genuinamente nova, e não uma cópia do que já
    existia;
  · `raw_asset` italiano em produção é **zero**, medido no pré-voo, portanto
    não há hipótese de colisão com um byte já preservado.

SE O PDF NÃO TIVER CAMADA DE TEXTO
----------------------------------
`NEEDS_OCR`, e a missão fecha com o RAW observado e o derivado não. **Isso não
é falha** — é o resultado honesto, e OCR é outra missão.
"""
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.portas_live import (  # noqa: E402
    ArmazemSupabase, MemoriaSupabase, buscar, e_pdf)
from guarda.preservar_coleta import preservar  # noqa: E402

# ── O CANDIDATO, E A SUA PROVA ────────────────────────────────────────
FONTE = {
    "SOURCE_ID": "IT-T2-002",
    "SOURCE_SLUG": "arpav-veneto",
    "SOURCE_URL": "https://www.arpa.veneto.it/risorse/data-agrometeo/"
                  "agrometeo/32zone/agro_01.pdf",
    "PROVA_DA_URL": ("data/collection-ledger/italy/observations.ndjson — a "
                     "mesma URL, com recibo de captura anterior"),
    "COUNTRY_SCOPE": "IT",
    "CAPTURE_METHOD": "HTTP_GET",
    "ARTIFACT_KIND": "DOCUMENT",
    "NOME": "agro_01.pdf",
    # ⚠️ TEMPO DE CAPTURA NAO E TEMPO DO FATO. O boletim nao data a
    # observacao de campo dentro do documento, e por isso o tempo do fato
    # fica UNKNOWN — nao se usa a hora do download no lugar dele.
    "FACT_TIME": "UNKNOWN",
    "PORQUE_FACT_TIME_UNKNOWN": ("o documento nao data a observacao de campo. "
                                 "COLLECTED_AT e quando NOS fomos buscar."),
}

RULE_VERSION = "1"
ACTOR = "canario-forward-it"
ACTOR_VERSION = "1"
MISSION = "GOLDEN_PATH_FORWARD_CANARY"

resultado = {"FONTE": FONTE, "PORTOES": [], "PRODUCTION_WRITES": {
    "DDL": 0, "collection_run": 0, "raw_asset": 0, "derived_artifact": 0,
    "storage_raw": 0, "storage_derived": 0}}


def portao(nome, ok, detalhe=""):
    resultado["PORTOES"].append({"PORTAO": nome, "PASSOU": bool(ok),
                                 "DETALHE": detalhe})
    print("  %-4s %-46s %s" % ("PASS" if ok else "FAIL", nome, detalhe))
    return bool(ok)


def parar(porque):
    resultado["PAROU_EM"] = porque
    print("\nPARAR: %s" % porque)
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str))
    return 1


def main():
    banco = MemoriaSupabase()
    armazem = ArmazemSupabase()

    # ── ANTES ────────────────────────────────────────────────────────
    antes = {
        "collection_run_IT": banco.contar("collection_run",
                                          "source_country='IT'"),
        "raw_asset_total": banco.contar("raw_asset"),
        "derived_artifact": banco.contar("derived_artifact"),
    }
    resultado["ANTES"] = antes
    print("=== ANTES ===\n  %s\n" % antes)

    # ── FASE 5 · A CAPTURA AO VIVO ───────────────────────────────────
    print("=== CAPTURA ===")
    r = buscar(FONTE["SOURCE_URL"])
    sha = hashlib.sha256(r["BYTES"]).hexdigest()
    recibo = {k: v for k, v in r.items() if k != "BYTES"}
    recibo["SHA256"] = sha
    resultado["RECIBO_DA_CAPTURA"] = recibo
    print("  %s" % json.dumps(recibo, ensure_ascii=False))

    if not portao("http_200", r["HTTP_STATUS"] == 200, str(r["HTTP_STATUS"])):
        return parar("a fonte nao devolveu 200")
    if not portao("bytes_nao_vazios", r["TAMANHO"] > 0, str(r["TAMANHO"])):
        return parar("vieram zero bytes")
    # A ASSINATURA REAL, nao o que o servidor declarou: um desafio de bot
    # devolve 200 com HTML por dentro.
    if not portao("e_mesmo_um_pdf", e_pdf(r["BYTES"]), r["BYTES"][:5].decode(
            "latin-1")):
        return parar("o que voltou nao e um PDF")

    # O SHA DE HOJE contra o do ledger — so para REGISTAR, nunca para decidir.
    historico = "f88c89d73d6a132a1c1ec6e87aadd893dd1f1028425dcf0fc4ffb37ab29170af"
    resultado["SHA_HISTORICO_DO_LEDGER"] = historico
    resultado["CAPTURA_E_NOVA"] = sha != historico
    print("  captura nova (sha != ledger): %s" % (sha != historico))

    # ── FASES 6 e 7 · A CORRIDA E O BRUTO, PELO DONO ─────────────────
    print("\n=== RUN + RAW (dono G-42) ===")
    agora = datetime.now(timezone.utc)
    run_id = "IT-CANARY-%s" % agora.strftime("%Y%m%dT%H%M%SZ")
    corrida = {"RUN_ID": run_id, "PLATFORM": "http", "ACTOR": ACTOR,
               "ACTOR_VERSION": ACTOR_VERSION, "MISSION": MISSION,
               "SOURCE_COUNTRY": "IT",
               "STARTED_AT": agora.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "RULE_VERSION": RULE_VERSION,
               "CAPTURE_METHOD": FONTE["CAPTURE_METHOD"]}
    artefato = {"COUNTRY": "IT", "SOURCE_SLUG": FONTE["SOURCE_SLUG"],
                "ARTIFACT_KIND": FONTE["ARTIFACT_KIND"],
                "NAME": FONTE["NOME"], "SOURCE_NATIVE_ID": FONTE["SOURCE_ID"],
                "SHA256": sha, "BYTES": r["TAMANHO"],
                "MEDIA_TYPE": "application/pdf",
                "CAPTURED_AT": r["COLLECTED_AT"],
                "SOURCE_URL": FONTE["SOURCE_URL"]}

    saida = preservar(corrida, [artefato], armazem, lambda o: r["BYTES"],
                      memoria=banco,
                      terminou_em=datetime.now(timezone.utc).strftime(
                          "%Y-%m-%dT%H:%M:%SZ"))
    resultado["RUN"] = {k: v for k, v in saida.items() if k != "SQL"}
    print("  RUN_STATE=%s PENDENCIA=%s" % (saida["RUN_STATE"],
                                           saida.get("PENDENCIA")))
    if saida["ENVIO"]["NOVOS"]:
        resultado["PRODUCTION_WRITES"]["storage_raw"] = len(
            saida["ENVIO"]["NOVOS"])
    if saida["MEMORIA"]["APLICADA"]:
        resultado["PRODUCTION_WRITES"]["collection_run"] = 1
        resultado["PRODUCTION_WRITES"]["raw_asset"] = \
            saida["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"] or 0

    if not portao("run_state_COMPLETE", saida["RUN_STATE"] == "COMPLETE",
                  str(saida["COMPLETION_BASIS"]["FALTOU"])):
        return parar("o RAW nao fechou — nao se deriva por cima de um buraco")

    linha_raw = banco.objeto_em(saida["RECONCILIACAO"] and
                                banco.objetos_da_corrida(run_id)[0]
                                ["storage_path"])
    raw_id = int(banco._valor(
        "select id from public.raw_asset where storage_path = '%s'"
        % linha_raw["storage_path"]))
    resultado["RAW"] = {"raw_asset_id": raw_id, **linha_raw}

    ok = (portao("raw_sha_bate_com_a_captura", linha_raw["sha256"] == sha)
          and portao("raw_bytes_bate", int(linha_raw["bytes"]) == r["TAMANHO"])
          and portao("objeto_esta_no_armazem",
                     armazem.existe(linha_raw["storage_path"]))
          and portao("sha_no_armazem_bate",
                     hashlib.sha256(armazem.ler(
                         linha_raw["storage_path"])).hexdigest() == sha)
          and portao("collection_run_IT_subiu_1",
                     banco.contar("collection_run", "source_country='IT'")
                     == antes["collection_run_IT"] + 1))
    if not ok:
        return parar("o portao do RAW nao fechou")
    resultado["RAW_FORWARD_OBSERVED"] = True

    # ── FASE 8 · A DERIVAÇÃO, PELO EXECUTOR E PELO WRITER ────────────
    print("\n=== DERIVACAO (executor + writer) ===")
    import coleta.executor_texto_de_pdf as ex
    if not ex.ha_ferramenta():
        resultado["DERIVED_FORWARD_OBSERVED"] = False
        resultado["MOTIVO"] = "EXECUTOR_UNAVAILABLE"
        print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str))
        return 0

    pdf = os.path.join(tempfile.mkdtemp(), FONTE["NOME"])
    with open(pdf, "wb") as f:
        f.write(r["BYTES"])

    d = ex.derivar_um(raw_id, pdf, armazem, banco)
    resultado["DERIVACAO"] = {k: v for k, v in d.items() if k != "SQL"}
    print("  ESTADO=%s" % d["ESTADO"])

    if d["ESTADO"] == "SEM_DERIVADO":
        # RESULTADO HONESTO, NAO FALHA. O RAW ficou observado; o texto nao
        # existe porque o documento nao tem camada de texto.
        resultado["DERIVED_FORWARD_OBSERVED"] = False
        resultado["MOTIVO"] = d.get("MOTIVO_DO_EXECUTOR")
        resultado["NEXT"] = "OCR em missao futura"
        print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str))
        return 0

    if not portao("primeira_derivacao_INSERTED", d["ESTADO"] == "INSERTED",
                  d.get("PORQUE", "")[:80]):
        return parar("a derivacao nao entrou")

    linha = d["LINHA_ESCRITA"]
    resultado["PRODUCTION_WRITES"]["derived_artifact"] = 1
    resultado["PRODUCTION_WRITES"]["storage_derived"] = 1 if d["NOVO_UPLOAD"] else 0

    ok = (portao("derived_raw_asset_id_bate", int(linha["raw_asset_id"]) == raw_id)
          and portao("derived_parent_sha_bate", linha["parent_sha256"] == sha)
          and portao("pais_veio_do_pai",
                     linha["storage_path"].startswith("IT/"),
                     linha["storage_path"][:32])
          and portao("derived_objeto_no_armazem",
                     armazem.existe(linha["storage_path"]))
          and portao("derived_sha_no_armazem_bate",
                     hashlib.sha256(armazem.ler(
                         linha["storage_path"])).hexdigest() == linha["sha256"])
          and portao("derived_at_existe", bool(linha["derived_at"]),
                     linha["derived_at"]))
    if not ok:
        return parar("o portao do DERIVADO nao fechou")
    resultado["DERIVED_FORWARD_OBSERVED"] = True

    # ── FASE 9 · O RETRY CONTROLADO ──────────────────────────────────
    # A MESMA derivacao, sobre o MESMO bruto. Nenhum segundo GET: o retry e
    # da derivacao, nao da captura.
    print("\n=== RETRY (mesma derivacao, mesmo bruto) ===")
    linhas_antes = banco.contar("derived_artifact")
    d2 = ex.derivar_um(raw_id, pdf, armazem, banco)
    resultado["RETRY"] = {k: v for k, v in d2.items() if k != "SQL"}
    print("  ESTADO=%s" % d2["ESTADO"])
    portao("retry_e_REUSED", d2["ESTADO"] == "REUSED", d2["ESTADO"])
    portao("retry_sem_upload_novo", not d2.get("NOVO_UPLOAD"))
    portao("retry_sem_linha_nova",
           banco.contar("derived_artifact") == linhas_antes)
    portao("retry_conferiu_o_byte_no_armazem",
           d2.get("BYTES_CONFERIDOS_NO_ARMAZEM") is True)

    # ── FASE 11 · DEPOIS ─────────────────────────────────────────────
    resultado["DEPOIS"] = {
        "collection_run_IT": banco.contar("collection_run",
                                          "source_country='IT'"),
        "raw_asset_total": banco.contar("raw_asset"),
        "derived_artifact": banco.contar("derived_artifact"),
    }
    resultado["DELTA_DESTA_MISSAO"] = {
        "collection_run_IT": resultado["DEPOIS"]["collection_run_IT"]
                             - antes["collection_run_IT"],
        "raw_asset": resultado["DEPOIS"]["raw_asset_total"]
                     - antes["raw_asset_total"],
        "derived_artifact": resultado["DEPOIS"]["derived_artifact"]
                            - antes["derived_artifact"],
    }
    resultado["LEGADO_TOCADO"] = False
    resultado["HISTORICOS_MIGRADOS"] = 0

    reprovados = [p["PORTAO"] for p in resultado["PORTOES"] if not p["PASSOU"]]
    print("\n=== CANARIO=%s ===" % ("PASS" if not reprovados else "FAIL"))
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str))
    return 1 if reprovados else 0


if __name__ == "__main__":
    sys.exit(main())
