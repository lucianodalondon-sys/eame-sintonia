#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CAMINHO FORWARD CONTA-SE — contra um PostgreSQL 16 que morre no fim.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/o_forward_conta_se.py

O QUE ESTA PROVA EXISTE PARA DISTINGUIR
---------------------------------------
    LEGACY_REPLAY_INSTRUMENTED  !=  CANONICAL_FORWARD_INSTRUMENTED.

O `O9` ligou a telemetria a `executor_texto_de_pdf.correr()` — que varre os PDF
historicos da arvore do Git e escreve um JSON. Aquilo prova que o cano leva
agua. Nao prova que a ESTRADA CANONICA forward emite, porque a estrada canonica
nao passa por ali: ela vai de `raw_asset` real, no banco, ate `derived_artifact`
real, no banco, pelo dono da escrita.

    UM REPLAY DE ARQUIVO PODE PROVAR QUE O SENSOR FUNCIONA
    E NAO PROVAR QUE ELE ESTA NA ESTRADA.

Aqui corre a estrada:

    collection_run  ->  raw_asset  ->  derivacao_forward.correr()
                    ->  executor_texto_de_pdf.derivar_um()
                    ->  guarda/preservar_derivado.py
                    ->  derived_artifact
                    ->  medidas/rastro_da_coleta.py  ->  etapa_da_corrida

OS NOVE CASOS
-------------
    F1  a cadeia canonica aplica-se num Postgres real, ate a 024
    F2  a corrida e REAL: o `run_id` referencia `collection_run`, e o banco
        recusa um `run_id` que nao exista — a chave estrangeira nao se contorna
    F3  o `raw_asset_id` e REAL, lido do banco, e a linhagem fecha no filho
    F4  a identidade da unidade e PROVADA, e nao inventada
    F5  a contabilidade fecha: UNACCOUNTED_INPUT = 0
    F6  o forward termina em DERIVED, e nao inventa READY
    F7  a falha injectada: DERIVED FAIL, item ERROR, codigo do registry
    F8  a telemetria nao muda o que e produzido
    F9  falha de telemetria nao e falha de coleta — e o que hoje acontece
        fica MEDIDO, com o buraco declarado

ZERO PRODUCAO
-------------
A tranca e a de `preservar_coleta_no_postgres.py`, reutilizada: a URL e
decomposta, o `hostname` tem de ser exatamente local e o banco tem de estar na
lista curta dos descartaveis. Nao ha Supabase, nao ha rede de coleta, nao ha
migration aplicada em producao.
"""
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

import coleta_checkpoint as cc          # noqa: E402
import derivacao_forward as fwd         # noqa: E402
import diagnostico as dg                # noqa: E402
import executor_texto_de_pdf as ex      # noqa: E402
import falhas                           # noqa: E402
import rastro_da_coleta as rastro       # noqa: E402
import telemetria as tel                # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira, preservar, sha256  # noqa: E402
from guarda import preservar_derivado as pd    # noqa: E402

# A 008 e CONFERENCIA, nao criacao. A lista e a mesma de
# `provas/rastro_no_postgres.py` — duas listas divergiriam.
MIGRATIONS = ['001', '002', '003', '004', '005', '006', '007', '009', '010',
              '011', '012', '013', '014', '015', '016', '017', '018', '019',
              '020', '021', '022', '023', '024']

MODELO_DAS_ESTRADAS = os.path.join(RAIZ, "system-map", "data",
                                   "estradas-it.model.json")
CATALOGO_DE_FONTES = os.path.join(RAIZ, "candidatas",
                                  "ITALY-SOURCE-MASTER-V1.json")
LOJA = os.path.join("data", "collection-store", "italy")

RELOGIO = "2026-09-08T02:00:00Z"

fora = []


# ── O QUE ESTA CORRIDA NAO FECHA, DECLARADO ONDE SE LE POR MAQUINA ──────────
# Mesmo formato de `coleta/derivacao_forward.py`: (NOME, O_QUE_FALTA). O censo
# dos buracos le os dois por AST, e um buraco so vale se estiver aqui.
GAPS = (
    ("TELEMETRY_FAILURE_SEM_POLITICA",
     "A excecao do rastro SOBE por `derivacao_forward.correr()`. O artefato "
     "fica guardado — a coleta NAO falhou — mas quem chama perde o recibo, e "
     "um chamador desatento pode ler a excecao como corrida falhada. Nao ha "
     "politica escrita nesta casa para «o sensor partiu-se», e inventar uma "
     "aqui para fechar o teste seria escrever constituicao para passar num "
     "exame. Fica como divida com nome."),
)


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


# ═════════════════════════════════════════════════════════════════════════
# A IDENTIDADE DA UNIDADE — lida dos donos, nunca escrita a mao aqui
# ═════════════════════════════════════════════════════════════════════════
def route_class_do_executor(ficheiro_do_executor="coleta/executor_texto_de_pdf.py"):
    """A route class cuja etapa DERIVED e deste executor. Lida do modelo.

    ⚠️ NAO E `'RC-1'` ESCRITO AQUI. Se amanha o modelo mudar de dono, esta
    funcao devolve outra coisa, e a prova reprova em vez de continuar a afirmar
    uma estrada que ja nao e a dele.
    """
    with open(MODELO_DAS_ESTRADAS, encoding="utf-8") as f:
        modelo = json.load(f)
    achados = [rc["ID"] for rc in modelo["ROUTE_CLASSES"]
               if ((rc.get("STEPS") or {}).get("DERIVED") or {}).get("OWNER")
               == ficheiro_do_executor]
    return (achados[0] if len(achados) == 1 else None), modelo


def source_id_do_caminho(caminho):
    """O SOURCE_ID vem do sitio onde o bruto foi preservado, e e conferido.

    A loja da coleta e `data/collection-store/italy/<SOURCE_ID>/...`. Isso e uma
    EVIDENCIA, e nao uma adivinha: o caminho foi escrito pela preservacao. E
    ainda assim nao chega — o nome so vale se existir no catalogo de fontes, que
    e o dono. Se nao existir, a resposta e `None`.

        MADE-UP TRACEABILITY ID IS WORSE THAN UNKNOWN.
    """
    partes = caminho.replace("\\", "/").split("/")
    if LOJA.replace("\\", "/") not in caminho.replace("\\", "/"):
        return None
    i = partes.index("italy")
    candidato = partes[i + 1] if len(partes) > i + 1 else None
    with open(CATALOGO_DE_FONTES, encoding="utf-8") as f:
        catalogo = f.read()
    return candidato if candidato and ('"%s"' % candidato) in catalogo else None


# ═════════════════════════════════════════════════════════════════════════
# O ARRANJO — a corrida e o bruto, escritos pelos donos canonicos
# ═════════════════════════════════════════════════════════════════════════
def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for n in MIGRATIONS:
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        if not achados:
            raise SystemExit("migration %s nao encontrada" % n)
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, achados[0])],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s" % achados[0])
            print(r.stderr.strip()[:1200])
            raise SystemExit(1)
    return len(MIGRATIONS)


def um_pdf_da_loja():
    """Um PDF REAL, preservado, dos que a casa ja tem.

    Fabricar bytes de PDF a mao provaria que eu sei montar um PDF — nao que a
    cadeia funciona. Os documentos reais estao aqui e o `pdftotext` abre-os.
    """
    import glob
    achados = sorted(glob.glob(os.path.join(RAIZ, LOJA, "*", "*", "*", "*.pdf")))
    return achados


def preservar_um_bruto(banco, run_id, caminho, nativo, source_id):
    """A corrida e o bruto, pelo dono canonico do BRUTO.

    ⚠️ NAO SE ESCREVE `insert into raw_asset` aqui. Se esta prova escrevesse a
    linha a mao, ela estaria a provar o SQL dela propria — e nao o caminho que
    a casa corre. Quem escreve o bruto e `guarda/preservar_coleta.py`.
    """
    with open(caminho, "rb") as f:
        dados = f.read()
    corrida = {"RUN_ID": run_id, "PLATFORM": "local", "ACTOR": "o9r",
               "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT",
               "MISSION": "O9R forward", "STARTED_AT": "2026-09-08T00:00:00Z",
               "RULE_VERSION": "1", "CAPTURE_METHOD": "HTTP_GET"}
    artefato = {"COUNTRY": "IT", "SOURCE_SLUG": source_id or "NAO_SEI",
                "ARTIFACT_KIND": "DOCUMENT",
                "NAME": os.path.basename(caminho), "SOURCE_NATIVE_ID": nativo,
                "SHA256": sha256(dados), "BYTES": len(dados),
                "MEDIA_TYPE": "application/pdf",
                "CAPTURED_AT": "2026-09-08T00:00:00Z",
                "SOURCE_URL": "https://exemplo.it/%s" % nativo}
    armazem = ArmazemDeMentira()
    recibo = preservar(corrida, [artefato], armazem, lambda o: dados,
                       memoria=banco, terminou_em="2026-09-08T00:05:00Z")
    linha = banco._valor(
        "select id from public.raw_asset where run_id = '%s' and sha256 = '%s'"
        % (run_id, sha256(dados)))
    return int(linha), sha256(dados), recibo, armazem


# ═════════════════════════════════════════════════════════════════════════
def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL") or ""
    if not _pg._e_descartavel(url):
        raise SystemExit(
            "RECUSADO: '%s' nao parece um banco descartavel local. "
            "Esta prova nunca corre contra producao." % url)

    print("MIGRATIONS — a cadeia canonica, ate a 024")
    quantas = aplicar_migrations(url)
    caso("F1_a_cadeia_aplica_num_postgres_real", quantas == len(MIGRATIONS),
         "%d migrations aplicadas em PostgreSQL 16" % quantas)

    banco = _pg.MemoriaPostgres(url)      # a porta do dono da escrita
    sql = cc.Banco(url)                   # a porta do dono do rastro
    pdfs = um_pdf_da_loja()
    if len(pdfs) < 2:
        raise SystemExit("nao ha PDF real suficiente na loja da coleta")
    if not ex.ha_ferramenta():
        raise SystemExit(
            "pdftotext ausente: sem ele o executor devolve FERRAMENTA_AUSENTE "
            "para tudo, e esta prova mediria a maquina, nao a cadeia.")

    # Um banco que ja tenha corrido isto uma vez tem as linhas la. Um
    # descartavel comeca do zero; um reutilizado nao pode fazer um caso passar
    # por causa do estado alheio.
    sql.executa("delete from public.etapa_da_corrida where run_id like 'RUN-O9R%'")
    sql.executa("delete from public.derived_artifact")
    sql.executa("delete from public.raw_asset where run_id like 'RUN-O9R%'")
    sql.executa("delete from public.collection_run where run_id like 'RUN-O9R%'")

    # ── A IDENTIDADE, PROVADA ────────────────────────────────────────────
    rc, modelo = route_class_do_executor()
    src = source_id_do_caminho(pdfs[0])
    canario = modelo.get("CANARIO") or {}
    caso("F4a_route_class_id_vem_do_modelo_das_estradas", rc is not None,
         "%s (STEPS.DERIVED.OWNER = coleta/executor_texto_de_pdf.py, em "
         "system-map/data/estradas-it.model.json)" % rc)
    caso("F4b_source_id_existe_no_catalogo_de_fontes", src is not None,
         "%s (caminho da loja + candidatas/ITALY-SOURCE-MASTER-V1.json)" % src)
    caso("F4c_batem_com_o_canario_declarado_da_estrada",
         canario.get("ROUTE_CLASS_ID") == rc and canario.get("SOURCE_ID") == src,
         "canario do modelo: %s / %s" % (canario.get("SOURCE_ID"),
                                         canario.get("ROUTE_CLASS_ID")))
    caso("F4d_o_id_inventado_do_O9_nao_existe_em_lado_nenhum",
         "IT-PDF-ITALIANOS" not in open(CATALOGO_DE_FONTES, encoding="utf-8").read()
         and "IT-PDF-ITALIANOS" not in open(MODELO_DAS_ESTRADAS,
                                            encoding="utf-8").read(),
         "MADE-UP TRACEABILITY ID IS WORSE THAN UNKNOWN")

    # ── F2 · A CORRIDA E REAL, E A CHAVE ESTRANGEIRA NAO SE CONTORNA ─────
    RUN = "RUN-O9R-FORWARD"
    raw_id, sha_pai, recibo_raw, armazem = preservar_um_bruto(
        banco, RUN, pdfs[0], "O9R-1", src)
    linha_run = banco.corrida(RUN) or {}
    caso("F2a_collection_run_existe_no_banco", bool(linha_run),
         "run_id=%s status=%s" % (RUN, linha_run.get("status")))

    try:
        rastro.registrar(sql, run_id="RUN-QUE-NAO-EXISTE", etapa="DERIVED",
                         estado=rastro.PASS, input_grain="x", input_count=0)
        recusou = False
        porque = "o banco ACEITOU um run_id que nao existe"
    except Exception as e:                                   # noqa: BLE001
        recusou = "foreign key" in str(e).lower() or "violates" in str(e).lower()
        porque = str(e).strip().splitlines()[0][:110]
    caso("F2b_o_banco_recusa_run_id_que_nao_existe", recusou, porque)

    # ── F3 · O BRUTO E REAL ──────────────────────────────────────────────
    caso("F3a_raw_asset_id_veio_do_banco", isinstance(raw_id, int) and raw_id > 0,
         "raw_asset_id=%d, lido com SELECT depois da escrita" % raw_id)
    caso("F3b_o_bruto_foi_escrito_pelo_dono_canonico",
         recibo_raw["PENDENCIA"] == "PRESERVED_AND_REGISTERED",
         "guarda/preservar_coleta.py, %s"
         % recibo_raw["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"])

    # ── O CAMINHO BOM ────────────────────────────────────────────────────
    print("\nO CAMINHO FORWARD, A SERIO")
    recibo = fwd.correr(
        [{"RAW_ASSET_ID": raw_id, "PDF": pdfs[0]}],
        banco_do_rastro=sql, run_id=RUN, armazem=armazem, memoria=banco,
        source_id=src, route_class_id=rc, relogio=lambda: RELOGIO)
    print("  %s · entrada %d · sairam %d · baldes %s"
          % (recibo["ESTADO_DA_ETAPA"], recibo["ENTRADA"], recibo["SAIRAM"],
             {k: v for k, v in recibo["BALDES"].items() if v}))

    filho = banco.derivado_com_identidade({
        "parent_sha256": sha_pai, "kind": "TEXT_EXTRACTION",
        "producer": ex.EXECUTOR_ID, "producer_version": ex.EXECUTOR_VERSION,
        "parameters_hash": pd.hash_dos_parametros(None), "serie_posicao": None})
    caso("F3c_o_derivado_existe_no_banco", bool(filho),
         "derived_artifact id=%s" % (filho or {}).get("id"))
    caso("F3d_a_linhagem_fecha_no_pai_real",
         bool(filho) and int(filho["raw_asset_id"]) == raw_id
         and filho["parent_sha256"] == sha_pai,
         "raw_asset_id=%s parent_sha256=%s..."
         % ((filho or {}).get("raw_asset_id"),
            ((filho or {}).get("parent_sha256") or "")[:12]))
    caso("F3e_o_produtor_e_a_versao_ficaram_no_filho",
         bool(filho) and filho["producer"] == ex.EXECUTOR_ID
         and filho["producer_version"] == ex.EXECUTOR_VERSION
         and filho["pipeline_version"] == ex.PIPELINE_VERSION,
         "producer=%s v%s pipeline=%s" % ((filho or {}).get("producer"),
                                          (filho or {}).get("producer_version"),
                                          (filho or {}).get("pipeline_version")))
    caso("F3f_o_byte_esta_no_armazem_e_bate_com_o_sha",
         bool(filho) and armazem.existe(filho["storage_path"])
         and sha256(armazem.ler(filho["storage_path"])) == filho["sha256"],
         "storage_path=%s" % ((filho or {}).get("storage_path") or "")[:64])

    # ── F5 · A CONTABILIDADE, LIDA DE VOLTA DO BANCO ─────────────────────
    passagens = rastro.passagens(sql, run_id=RUN)
    integridade = rastro.integridade(passagens)
    caso("F5a_a_passagem_chegou_ao_banco", len(passagens) == 1,
         "%d passagem(ns) em etapa_da_corrida" % len(passagens))
    caso("F5b_UNACCOUNTED_INPUT_e_zero", integridade["UNACCOUNTED_INPUT"] == 0,
         "sem explicacao: %d" % integridade["UNACCOUNTED_INPUT"])
    p = passagens[0] if passagens else {}
    caso("F5c_a_conta_foi_fechada_pelo_BANCO_e_nao_por_nos",
         p.get("ACCOUNTED") == p.get("INPUT_COUNT"),
         "accounted=%s input=%s (coluna GERADA pela 024)"
         % (p.get("ACCOUNTED"), p.get("INPUT_COUNT")))
    caso("F5d_a_identidade_provada_ficou_na_linha",
         p.get("ETAPA") == "DERIVED" and p.get("EDGE_FROM") == "RAW",
         "etapa=%s edge_from=%s" % (p.get("ETAPA"), p.get("EDGE_FROM")))
    id_na_linha = sql.executa(
        "select coalesce(source_id,'-'), coalesce(route_class_id,'-')"
        " from public.etapa_da_corrida where run_id = '%s' limit 1" % RUN)
    caso("F5e_source_e_route_gravados_sao_os_provados",
         bool(id_na_linha) and id_na_linha[0][0] == src
         and id_na_linha[0][1] == rc,
         "source_id=%s route_class_id=%s" % (id_na_linha[0][0] if id_na_linha
                                             else "?",
                                             id_na_linha[0][1] if id_na_linha
                                             else "?"))

    # ── F6 · ONDE O FORWARD TERMINA DE VERDADE ───────────────────────────
    etapas = {x["ETAPA"] for x in passagens}
    caso("F6a_o_forward_termina_em_DERIVED", etapas == {"DERIVED"},
         "etapas emitidas: %s" % (sorted(etapas) or "nenhuma"))
    caso("F6b_nao_nasceu_READY_por_o_derivado_ter_sido_persistido",
         "READY" not in etapas,
         "DERIVED STORED != READY — persistir nao e julgar")
    caso("F6c_nao_nasceu_ADMISSION_nem_STRUCTURED",
         not ({"ADMISSION", "STRUCTURED"} & etapas),
         "STAGE EXISTS IN VOCABULARY != STAGE RAN")
    caso("F6d_a_lei_do_READY_nao_morde_esta_cadeia",
         tel.ready_sem_quem_assine(passagens) == [],
         "um forward que termina em DERIVED nao e violacao")

    # ⚠️ E A LEI TEM DE MORDER. Uma lei que passasse sempre seria
    # indistinguivel de uma lei desligada, por isso a violacao e FORJADA aqui
    # de proposito — em memoria, sem tocar no banco.
    forjado = passagens + [{"ETAPA": "READY", "ESTADO": "PASS"}]
    mordida = tel.ready_sem_quem_assine(forjado)
    caso("F6e_um_READY_forjado_e_apanhado_pela_lei",
         len(mordida) == 1 and mordida[0]["FALTA"] == "ADMISSION",
         (mordida[0]["PORQUE"] if mordida else "a lei NAO mordeu")[:96])
    caso("F6f_o_buraco_a_jusante_esta_declarado_e_nao_calado",
         {"STRUCTURED_SEM_DONO_LIGADO", "ADMISSION_SEM_DONO_LIGADO",
          "READY_NAO_TEM_DONO"} <= set(recibo["GAPS"]),
         "GAPS: %s" % ", ".join(recibo["GAPS"]))

    # ── F8 · A TELEMETRIA NAO MUDA O QUE E PRODUZIDO ─────────────────────
    #
    #     OUTPUT_FUNCTIONAL_CHANGED = NO.
    #
    # Mesma unidade, duas vezes: uma SEM rastro, outra COM. Entre as duas, a
    # linha do filho e apagada — isto e um banco descartavel, e apagar aqui e o
    # reset da bancada, nao uma operacao do sistema. Sem o reset a segunda
    # corrida daria REUSED, e REUSED nao compara producao com producao.
    print("\nINVARIANCIA — a mesma unidade, com e sem telemetria")
    sql.executa("delete from public.derived_artifact")
    arm_a = ArmazemDeMentira()
    fwd.correr([{"RAW_ASSET_ID": raw_id, "PDF": pdfs[0]}],
               banco_do_rastro=None, run_id=RUN, armazem=arm_a, memoria=banco,
               source_id=src, route_class_id=rc, relogio=lambda: RELOGIO)
    sem = banco.derivado_com_identidade({
        "parent_sha256": sha_pai, "kind": "TEXT_EXTRACTION",
        "producer": ex.EXECUTOR_ID, "producer_version": ex.EXECUTOR_VERSION,
        "parameters_hash": pd.hash_dos_parametros(None), "serie_posicao": None})
    caso("F8a_sem_telemetria_o_derivado_sai_igual",
         bool(sem) and bool(filho)
         and all(sem.get(c) == filho.get(c) for c in
                 ("parent_sha256", "kind", "producer", "producer_version",
                  "pipeline_version", "parameters_hash", "sha256", "bytes",
                  "media_type", "storage_path", "derived_at")),
         "sha256 %s... nos dois" % ((sem or {}).get("sha256") or "")[:12])
    caso("F8b_os_bytes_no_armazem_sao_os_mesmos",
         bool(sem) and arm_a.existe(sem["storage_path"])
         and arm_a.ler(sem["storage_path"]) == armazem.ler(filho["storage_path"]),
         "OUTPUT_FUNCTIONAL_CHANGED = NO")
    caso("F8c_sem_rastro_nao_nasceu_passagem_nenhuma",
         len(rastro.passagens(sql, run_id=RUN)) == 1,
         "continua 1 passagem: a corrida sem telemetria nao escreveu")

    # ── F7 · A FALHA INJECTADA, NO CAMINHO FORWARD ───────────────────────
    print("\nFALHA INJECTADA — no forward, e nao no relatorio")
    RUN_F = "RUN-O9R-FALHA"
    # ⚠️ A corrida NAO se cria a mao aqui: quem a cria e o dono do bruto, ao
    # preservar. Uma corrida inserida a mao com outra identidade faz o
    # `preservar` recusar com RUN_ID_CONFLICT — e com razao.
    # A falha e CONTROLADA e nao estraga ficheiro nenhum: um ficheiro que NAO e
    # PDF, entregue ao executor. O `pdftotext` recusa-o, e isso e um erro nosso
    # de execucao — nao uma propriedade do documento.
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(b"isto nao e um PDF, e o pdftotext vai dize-lo\n")
    tmp.close()
    raw_b, sha_b, _r, arm_b = preservar_um_bruto(banco, RUN_F, pdfs[1],
                                                 "O9R-2", src)
    recibo_f = fwd.correr(
        [{"RAW_ASSET_ID": raw_b, "PDF": pdfs[1]},
         {"RAW_ASSET_ID": raw_b, "PDF": tmp.name},
         {"RAW_ASSET_ID": 99999999, "PDF": pdfs[1]}],
        banco_do_rastro=sql, run_id=RUN_F, armazem=arm_b, memoria=banco,
        source_id=src, route_class_id=rc, relogio=lambda: RELOGIO)
    os.unlink(tmp.name)
    print("  %s · baldes %s" % (recibo_f["ESTADO_DA_ETAPA"],
                                {k: v for k, v in recibo_f["BALDES"].items() if v}))
    pf = rastro.passagens(sql, run_id=RUN_F)
    linha_f = pf[0] if pf else {}
    caso("F7a_a_etapa_diz_FAIL", linha_f.get("ESTADO") == "FAIL",
         "estado=%s" % linha_f.get("ESTADO"))
    caso("F7b_o_item_que_quebrou_conta_como_ERROR",
         linha_f.get("ERROR", 0) >= 2,
         "error=%s (ficheiro invalido + pai inexistente)" % linha_f.get("ERROR"))
    caso("F7c_o_item_bom_continua_a_passar", linha_f.get("PASSED", 0) == 1,
         "passed=%s — um erro nao contamina o vizinho" % linha_f.get("PASSED"))
    caso("F7d_o_codigo_vem_do_registry_de_diagnostico",
         linha_f.get("DIAGNOSTIC_CODE") == dg.DERIVATION_FAILED,
         "diagnostic_code=%s (leis/diagnostico.py)"
         % linha_f.get("DIAGNOSTIC_CODE"))
    estado_canonico = sql.executa(
        "select coalesce(canonical_state,'-') from public.etapa_da_corrida"
        " where run_id = '%s' limit 1" % RUN_F)
    caso("F7e_o_estado_canonico_vem_de_falhas_py",
         bool(estado_canonico) and estado_canonico[0][0] in falhas.ESTADOS,
         "canonical_state=%s (leis/falhas.py)"
         % (estado_canonico[0][0] if estado_canonico else "?"))
    caso("F7f_a_conta_fecha_mesmo_com_a_falha",
         rastro.integridade(pf)["UNACCOUNTED_INPUT"] == 0,
         "3 entram, 1 passa, 2 erram — e nenhum some")
    caso("F7g_last_good_aponta_o_ultimo_que_passou",
         bool(linha_f.get("LAST_GOOD_ARTIFACT")),
         "last_good=%s" % (linha_f.get("LAST_GOOD_ARTIFACT") or "")[:56])
    caso("F7h_nada_a_jusante_foi_marcado_NOT_RUN_sem_plano",
         linha_f.get("NOT_RUN", 0) == 0 and {x["ETAPA"] for x in pf} == {"DERIVED"},
         "NOT_RUN e «fazia parte do plano e nao chegou a vez» — nao havia plano")

    # ── F9 · FALHA DE TELEMETRIA != FALHA DE COLETA ──────────────────────
    print("\nFALHA DE TELEMETRIA — e o que hoje acontece de verdade")
    RUN_T = "RUN-O9R-RASTRO-MORTO"
    sql.executa(
        "insert into public.collection_run (run_id, platform, source_country,"
        " started_at, status, rule_version)"
        " values ('%s','local','IT',now(),'rodando','1')" % RUN_T)
    sql.executa("delete from public.derived_artifact")

    class BancoQueMorre:
        """O rastro parte. A coleta nao tem de partir com ele."""

        def executa(self, _sql):
            raise IOError("o rastro nao esta disponivel")

    arm_t = ArmazemDeMentira()
    rebentou = None
    try:
        fwd.correr([{"RAW_ASSET_ID": raw_id, "PDF": pdfs[0]}],
                   banco_do_rastro=BancoQueMorre(), run_id=RUN_T,
                   armazem=arm_t, memoria=banco, source_id=src,
                   route_class_id=rc, relogio=lambda: RELOGIO)
    except Exception as e:                                   # noqa: BLE001
        rebentou = str(e)
    derivado_apesar = banco.derivado_com_identidade({
        "parent_sha256": sha_pai, "kind": "TEXT_EXTRACTION",
        "producer": ex.EXECUTOR_ID, "producer_version": ex.EXECUTOR_VERSION,
        "parameters_hash": pd.hash_dos_parametros(None), "serie_posicao": None})
    caso("F9a_a_derivacao_aconteceu_antes_do_rastro_e_ficou_no_banco",
         bool(derivado_apesar),
         "derived_artifact id=%s, com o rastro morto"
         % (derivado_apesar or {}).get("id"))
    caso("F9b_nao_virou_falha_de_FONTE_nem_de_ROTA",
         not sql.executa(
             "select 1 from public.etapa_da_corrida where run_id = '%s'" % RUN_T),
         "nenhuma passagem de falha foi inventada para a rota %s" % rc)
    caso("F9c_a_saude_da_rota_nao_foi_manchada_por_um_sensor_partido",
         not sql.executa(
             "select 1 from public.v_saude_da_rota where route_class_id = '%s'"
             " and passagens_falha > 1" % rc),
         "OBSERVABILITY FAILURE != COLLECTION FAILURE")

    # ⚠️ O QUE ISTO **NAO** FECHA, E FICA DECLARADO.
    #
    # ⚠️ UM BURACO QUE SO EXISTE NUM `print` NAO EXISTE PARA NINGUEM.
    # Ele estava so aqui em baixo, em texto impresso, e por isso o mapa nao
    # conseguia desenha-lo: `derivacao_forward.py` declara os seus num tuplo
    # `GAPS` que se le por AST, e este ficava de fora da medicao por escrever a
    # mesma coisa de outra maneira.
    #
    #     DUAS MANEIRAS DE DECLARAR A MESMA COISA E UMA DELAS INVISIVEL.
    #
    # O tuplo la em cima e agora o dono; estes `print` continuam a existir para
    # quem le a corrida, mas ja nao sao o unico sitio onde o buraco vive.
    print("\n  GAP MEDIDO — %s" % GAPS[0][0])
    print("    Hoje a excecao do rastro SOBE por `derivacao_forward.correr()`:")
    print("    %s" % (rebentou or "nao subiu"))
    print("    O artefato ficou guardado — a coleta NAO falhou — mas quem")
    print("    chama perde o recibo, e um chamador desatento pode ler a")
    print("    excecao como corrida falhada. Nao ha politica escrita nesta")
    print("    casa para «o sensor partiu-se»; INVENTAR uma aqui para fechar")
    print("    o teste seria escrever constituicao para passar num exame.")
    print("    Fica como divida com nome.")

    # ── O RELATORIO ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    mal = [n for n, ok, _d in fora if not ok]
    for nome, ok, detalhe in fora:
        print("  %s  %-52s %s" % ("PASS" if ok else "FAIL", nome, detalhe))
    print("=" * 70)
    print("FORWARD_CONTA_SE=%s%s"
          % ("PASS" if not mal else "FAIL",
             "" if not mal else " · %d reprovado(s)" % len(mal)))
    print("  o que isto prova: a estrada canonica FORWARD emite, num Postgres")
    print("  16 real, com corrida real e raw_asset real — e termina em DERIVED,")
    print("  que e onde ela termina de verdade.")
    print("  o que NAO prova: producao. Nada aqui tocou Supabase, e a 024")
    print("  continua por aplicar em producao.")
    return 0 if not mal else 1


if __name__ == "__main__":
    raise SystemExit(main())
