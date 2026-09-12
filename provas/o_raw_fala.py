#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ETAPA RAW DEIXA DE SER MUDA — e a passagem aponta para a observação.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/o_raw_fala.py

O QUE ESTA PROVA EXISTE PARA FECHAR
-----------------------------------
`G-RAW-01`, medido em `system-map/data/buracos.generated.json`:

    RAW_FORWARD_NAO_EMITE
    "guarda/preservar_coleta.py escreve `raw_asset` e nao emite rastro"

A etapa corria e era muda. E não era por falta de vocabulário: `RAW` já estava
em `telemetria.ETAPAS_DA_COLETA`, e `diagnostico.da_etapa('RAW', ...)` já lhe
dava código. Estava tudo escrito menos a linha.

Pior do que calada: DERIVED declarava `edge_from = 'RAW'`. A seta estava
desenhada dos dois lados, e só um lado tinha linha.

    UMA ETAPA QUE PERSISTE MAS NAO EMITE RASTRO EXISTE NO BANCO,
    E NAO EXISTE PARA A RECONCILIACAO OPERACIONAL.

Numa coleta grande é isso que separa cinco coisas diferentes que, sem rastro,
têm todas o mesmo aspeto — nenhum:

    RAW_EXECUTED · RAW_NOT_RUN · RAW_ERROR · RAW_LOST · RAW_REUSED

O QUE ELA FAZ
-------------
Uma corrida real, contra PostgreSQL 16 descartável, pela PORTA DE PRODUÇÃO —
`coleta/ingresso.receber()`, que `provas/o_encanamento_tem_uma_porta.py` prova
ser o único chamador de `preservar()` na casa. Depois pergunta AO BANCO.

    O LEDGER DECLARA. O BANCO MEDE. E SO O SEGUNDO E PROVA.

O QUE ELA NAO PROVA
-------------------
Não prova produção: nada aqui toca Supabase. Não prova READY. Não resolve
`G-TEL-01` — a política para quando a própria telemetria falha continua a ser
a que já era, e esta prova MEDE-A em vez de lhe inventar outra.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import _gavetas  # noqa: E402,F401

import coleta_checkpoint as cc                          # noqa: E402
import rastro_da_coleta as rastro                       # noqa: E402
import telemetria as tel                                # noqa: E402
from coleta import ingresso as ing                      # noqa: E402
from guarda.preservar_coleta import sha256              # noqa: E402

# A cadeia de migrations vem do DISCO. Uma lista à mão envelhece calada, e esta
# prova nasce depois de a `028` existir — quando nascer a `029`, ela aplica-a
# sem que ninguém se lembre dela. A `008` fica de fora: ela não constrói
# esquema, VERIFICA o que as outras construíram.
_SO_VERIFICA = ("008",)
RUN = "RUN-RAW-FALA"
FONTE = "IT-T2-002"


def _cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    return [f.split("_", 1)[0] for f in sorted(os.listdir(pasta))
            if f.endswith(".sql") and f.split("_", 1)[0] not in _SO_VERIFICA]


MIGRATIONS = _cadeia_de_migrations()

fora = []


REBENTOU = []


def porta(itens, **kw):
    """`ing.receber`, e a excecao vira MEDICAO em vez de matar a prova.

    ⚠️ MEDIDO NA MUTACAO: cinco mutantes — o `raw_asset_id` com um caminho
    dentro, um `run_id` sem corrida, o rastro a falar antes de persistir —
    faziam o banco recusar, a excecao subia daqui e a prova morria a meio.
    Ela nao reprovava: CALAVA-SE. E um `?` no lugar do veredito le-se, de
    longe, como se nada tivesse acontecido.

        UMA PROVA QUE NAO CONSEGUE DIZER `FAIL`
        NAO ESTA A APROVAR: ESTA A CALAR-SE.

    O que rebentou fica registado e reprova no fim, com o nome de quem foi.
    """
    try:
        return ing.receber(itens, **kw)
    except Exception as erro:                                # noqa: BLE001
        REBENTOU.append("%s: %s" % (kw.get("corrida", {}).get("RUN_ID", "?"),
                                    str(erro)[:140]))
        return {"RAW": None, "RECUSAS": [], "ACEITES": []}


def _inteiro(v):
    """O valor como inteiro, ou `None` — e nunca uma excecao.

    Uma prova que levanta a meio nao reprova: cala-se. E um silencio no meio
    de uma medicao le-se como aprovacao de tudo o que vinha a seguir.
    """
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for n in MIGRATIONS:
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + "_")]
        r = subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-q", "-f",
                            os.path.join(pasta, achados[0])],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FALHOU a aplicar %s\n%s" % (achados[0], r.stderr[:900]))
            raise SystemExit(1)
    return len(MIGRATIONS)


def um_pdf_preservado():
    """Bytes REAIS do corpo italiano preservado. Nada aqui é fabricado."""
    import glob
    achados = sorted(glob.glob(os.path.join(
        RAIZ, "data", "collection-store", "italy", FONTE, "*", "*", "*.pdf")))
    if not achados:
        raise SystemExit("nao ha PDF preservado da fonte %s" % FONTE)
    return achados[0]


def corrida(run_id=RUN, quando="2026-09-08T00:00:00Z"):
    return {"RUN_ID": run_id, "PLATFORM": "HTTP direto",
            "ACTOR": "coleta/italy_executor.py", "ACTOR_VERSION": "adapter-v1",
            "SOURCE_COUNTRY": "IT", "RULE_VERSION": "1", "STARTED_AT": quando,
            "MISSION": "o RAW fala", "CAPTURE_METHOD": "HTTP_GET"}


def abrir_corrida(sql, run_id):
    """`etapa_da_corrida.run_id` tem chave para `collection_run`.

    A corrida não se inventa aqui: quem a abre é o dono do RAW quando preserva.
    Esta linha existe porque a prova precisa da corrida ANTES, para os casos
    negativos em que nada chega a ser preservado.
    """
    sql.executa(
        "insert into public.collection_run (run_id, platform, actor,"
        " actor_version, source_country, rule_version, started_at, status)"
        " values ('%s','HTTP direto','coleta/italy_executor.py','adapter-v1',"
        "'IT','1','2026-09-08T00:00:00Z','rodando')"
        " on conflict (run_id) do nothing" % run_id)


def linhas_raw(sql, run_id):
    return sql.executa(
        "select etapa, estado, coalesce(raw_asset_id::text,'<NULL>'),"
        " coalesce(source_id,'<NULL>'), input_count, output_count,"
        " passed, rejected, error_count, not_run_count, unknown_count, reused,"
        " unaccounted_input, coalesce(diagnostic_code,'<NULL>')"
        " from public.etapa_da_corrida"
        " where run_id = '%s' and etapa = 'RAW' order by id" % run_id)


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("SEM BANCO DESCARTAVEL — e SKIP != PASS.")
        print("RAW_FALA=NOT_MEASURED")
        return 2

    print("=" * 70)
    print("A ETAPA RAW FALA — %d migrations, ate a %s" % (len(MIGRATIONS),
                                                          MIGRATIONS[-1]))
    aplicar_migrations(url)
    sql = cc.Banco(url)
    banco = ing.MemoriaDescartavel(url) if hasattr(ing, "MemoriaDescartavel") \
        else None
    if banco is None:
        import importlib.util as _u
        _spec = _u.spec_from_file_location(
            "prova_pg", os.path.join(RAIZ, "provas",
                                     "preservar_coleta_no_postgres.py"))
        _pg = _u.module_from_spec(_spec)
        _spec.loader.exec_module(_pg)
        banco = _pg.MemoriaPostgres(url)

    caso("R0_o_vocabulario_ja_tinha_a_etapa",
         "RAW" in tel.ETAPAS_DA_COLETA,
         "RAW em telemetria.ETAPAS_DA_COLETA: nada de novo foi inventado")

    # ── A PASSAGEM REAL, PELA PORTA DE PRODUCAO ──────────────────────────
    pdf = um_pdf_preservado()
    rel = os.path.relpath(pdf, RAIZ)
    # ⚠️ O ITEM E UM SO, E ESCRITO UMA VEZ SO.
    # A versao anterior repetia-o a mao para o retry e esquecia-lhe o
    # `SOURCE_URL` — e entao o «retry» era OUTRO item, que gerava OUTRA
    # observacao. A prova media dois itens e chamava-lhes um.
    #
    #     DOIS DICIONARIOS PARECIDOS NAO SAO O MESMO ITEM.
    item = {"SOURCE_ID": FONTE,
            "SOURCE_URL": "https://www.arpa.veneto.it/%s" % os.path.basename(pdf),
            "STORAGE_LOCATION": rel}
    # ⚠️ A PASSAGEM PODE REBENTAR, E ISSO E UMA MEDICAO — NAO UM ACIDENTE.
    # MEDIDO na mutacao: um `raw_asset_id` com um caminho dentro, ou um
    # `run_id` sem corrida, fazem o banco recusar e a excecao sobe. Se ela
    # subisse daqui, a prova morria sem veredito — e um mutante que faz a
    # prova rebentar passaria por sobrevivente.
    r = porta([dict(item)],
              corrida=corrida(), armazem=ing.ArmazemLocal(RAIZ),
              memoria=banco, raiz=RAIZ, banco_do_rastro=sql)
    r = r or {"RAW": None}

    obs = (r["RAW"] or {}).get("RAW_OBSERVATIONS") or []
    raw_id = obs[0]["RAW_OBSERVATION_ID"] if len(obs) == 1 else None
    no_banco = sql.executa(
        "select id, run_id, coalesce(source_id,'<NULL>'), sha256, storage_path"
        " from public.raw_asset where run_id = '%s'" % RUN)
    caso("R1_a_observacao_e_real_e_o_id_veio_do_banco",
         len(no_banco) == 1 and raw_id == int(no_banco[0][0]),
         "raw_asset.id=%s" % raw_id)

    trilhos = linhas_raw(sql, RUN)
    caso("R2_a_etapa_RAW_deixou_linha",
         len(trilhos) == 1, "linhas de RAW nesta corrida: %d" % len(trilhos))
    # ⚠️ UMA PROVA QUE REBENTA NAO DA VEREDITO, E `?` NAO E `FAIL`.
    # MEDIDO na mutacao: quatro mutantes — a porta cala-se, o rastro usa
    # outro RUN_ID, o rastro fala antes de persistir, o storage_path vira
    # identidade — faziam esta prova levantar `ValueError` a meio, e ela
    # morria sem dizer nada. O mutante passava por SOBREVIVENTE.
    #
    #     UMA PROVA QUE NAO CONSEGUE DIZER `FAIL`
    #     NAO ESTA A APROVAR: ESTA A CALAR-SE.
    #
    # `<VAZIO>` e a ausencia com nome, e ela reprova como qualquer outro
    # valor errado — sem interromper as perguntas que vem a seguir.
    t = trilhos[0] if trilhos else ["<VAZIO>"] * 14
    caso("R3_a_linha_aponta_para_ESTA_observacao",
         _inteiro(t[2]) is not None and raw_id is not None
         and _inteiro(t[2]) == raw_id,
         "etapa_da_corrida.raw_asset_id=%s · raw_asset.id=%s" % (t[2], raw_id))
    caso("R4_a_linha_e_da_MESMA_corrida",
         len(no_banco) == 1 and no_banco[0][1] == RUN,
         "run_id=%s nas duas casas" % RUN)
    caso("R5_o_estado_e_PASS_e_a_conta_fecha",
         t[1] == "PASS" and _inteiro(t[12]) == 0,
         "estado=%s · unaccounted_input=%s" % (t[1], t[12]))
    caso("R6_a_fonte_e_a_declarada_e_nao_uma_inferida",
         t[3] == FONTE and no_banco[0][2] == FONTE,
         "source_id=%s no rastro e na observacao" % t[3])

    # ⚠️ A IDENTIDADE NAO E O SHA E NAO E O ENDERECO.
    sha, caminho = no_banco[0][3], no_banco[0][4]
    # ⚠️ `t[2] not in caminho` ERA O TESTE ERRADO, e passava por acaso ao
    # contrario: o id e `1`, e `1` cabe dentro de quase qualquer caminho. Um
    # teste de substring responde a pergunta «estas letras aparecem?», e a
    # pergunta e «este valor foi DERIVADO daquele?».
    #
    #     PROCURAR LETRAS ONDE SE DEVIA COMPARAR ESPECIES
    #     E CONFERIR UM PASSAPORTE PELAS LETRAS QUE APARECEM NELE.
    #
    # A pergunta certa responde-se pela ESPECIE: o id e o surrogate que o banco
    # cunhou, e nem o sha nem o endereco cabem na coluna que o recebe.
    tipo = sql.executa(
        "select data_type from information_schema.columns"
        " where table_name = 'etapa_da_corrida'"
        " and column_name = 'raw_asset_id'")
    caso("R7_o_id_da_passagem_nao_e_o_sha_nem_o_endereco",
         t[2] != sha and t[2] != caminho and t[2] != sha[:16]
         and tipo and tipo[0][0] == "bigint",
         "raw_asset_id=%s (%s) · sha256=%s… · storage_path=%s"
         % (t[2], tipo[0][0] if tipo else "?", sha[:12], caminho))

    # ── O QUE ESTAVA A JUSANTE CONTINUA A CORRER ─────────────────────────
    depois = sql.executa(
        "select etapa, estado from public.etapa_da_corrida"
        " where run_id = '%s' order by id" % RUN)
    caso("R8_a_passagem_seguinte_nao_foi_partida",
         [x[0] for x in depois] == ["RAW"],
         "esta corrida so passou por RAW, e a linha dela existe: %s"
         % [x[0] for x in depois])

    # ═══════════════════════════════════════════════════════════════════
    # OS CASOS NEGATIVOS — cada um é uma maneira de mentir, e nenhuma passa
    # ═══════════════════════════════════════════════════════════════════
    print("\nOS CASOS NEGATIVOS")

    # A · RAW falha ANTES de persistir → nao pode haver rastro de sucesso.
    run_a = RUN + "-A"
    abrir_corrida(sql, run_a)
    r_a = porta([dict(item)],
                      corrida=corrida(run_a), armazem=ing.ArmazemLocal(RAIZ),
                      memoria=None, raiz=RAIZ, banco_do_rastro=sql)
    t_a = linhas_raw(sql, run_a)
    caso("N_A_falha_antes_de_persistir_nao_da_sucesso",
         len(t_a) == 1 and t_a[0][1] != "PASS" and t_a[0][2] == "<NULL>",
         "estado=%s · raw_asset_id=%s"
         % (t_a[0][1] if t_a else "?", t_a[0][2] if t_a else "?"))
    caso("N_A2_e_a_falha_tem_codigo",
         len(t_a) == 1 and t_a[0][13] != "<NULL>",
         "diagnostic_code=%s" % (t_a[0][13] if t_a else "?"))

    # B · RAW nao e executado → nao pode aparecer como executado.
    # ⚠️ O ITEM TEM DE SER RECUSADO PELA PORTA, e nao pelo dono do RAW: esse
    # segundo caso CORREU. Confundi-los daria NOT_RUN a uma etapa que correu.
    run_b = RUN + "-B"
    abrir_corrida(sql, run_b)
    porta([{}], corrida=corrida(run_b),
                armazem=ing.ArmazemLocal(RAIZ), memoria=banco, raiz=RAIZ,
                banco_do_rastro=sql)
    t_b = linhas_raw(sql, run_b)
    caso("N_B_o_que_nao_correu_diz_NOT_RUN_e_nao_FAIL",
         len(t_b) == 1 and t_b[0][1] == "NOT_RUN" and t_b[0][2] == "<NULL>",
         "estado=%s · ERROR != NOT_RUN" % (t_b[0][1] if t_b else "?"))

    # B2 · e RECUSAR nao e FALHAR: a etapa que correu e recusou tudo nao e uma
    # etapa avariada. Marca-la FAIL mandava consertar a peca errada.
    # ⚠️ AQUI NAO SE ABRE A CORRIDA A MAO, e a razao foi MEDIDA: abrindo-a,
    # `preservar()` encontrava-a com campos que ELE nao escreveu e dava
    # `RUN_ID_CONFLICT` — e a etapa saia FAIL por causa da bancada, nao do
    # codigo. Quem preserva e que abre a corrida.
    #
    #     UMA BANCADA QUE ESCREVE O QUE O DONO ESCREVERIA
    #     MEDE A BANCADA.
    run_b2 = RUN + "-B2"
    porta([{"STORAGE_LOCATION": rel}], corrida=corrida(run_b2),
                armazem=ing.ArmazemLocal(RAIZ), memoria=banco, raiz=RAIZ,
                banco_do_rastro=sql)
    t_b2 = linhas_raw(sql, run_b2)
    caso("N_B2_recusar_nao_e_falhar_e_a_recusa_conta_se",
         len(t_b2) == 1 and t_b2[0][1] == "PASS" and _inteiro(t_b2[0][7]) == 1
         and t_b2[0][2] == "<NULL>" and _inteiro(t_b2[0][12]) == 0,
         "estado=%s · rejected=%s · sem observacao nomeada"
         % (t_b2[0][1] if t_b2 else "?", t_b2[0][7] if t_b2 else "?"))

    # C · SOURCE_ID ausente → a telemetria nao o fabrica.
    caso("N_C_sem_fonte_provada_o_rastro_nao_a_inventa",
         ing._fonte_provada([{"SOURCE_ID": "NAO SEI"}]) is None
         and ing._fonte_provada([{"SOURCE_ID": ""}]) is None
         and ing._fonte_provada([{}]) is None,
         "NAO SEI / vazio / ausente → NULL, e nunca um id")

    # D · storage_path com identidade aparente → nao e usada.
    caso("N_D_o_endereco_nao_vira_identidade",
         ing._fonte_provada([{"STORAGE_LOCATION":
                              "data/collection-store/italy/IT-T2-002/x.pdf"}])
         is None,
         "o caminho traz `IT-T2-002` e a fonte sai NULL na mesma")

    # E · duas fontes na mesma passagem → a linha nao escolhe uma.
    caso("N_E_duas_fontes_nao_viram_uma",
         ing._fonte_provada([{"SOURCE_ID": "IT-T2-002"},
                             {"SOURCE_ID": "IT-T2-009"}]) is None,
         "escolher uma delas faria a passagem falar por meia coleta")

    # F · N != 1 observacoes → a linha nao nomeia nenhuma, e as contagens falam.
    caso("N_F_com_N_diferente_de_um_a_linha_nao_nomeia_observacao",
         ing._a_observacao_desta_passagem(
             {"RAW_OBSERVATIONS": [{"RAW_OBSERVATION_ID": 1},
                                   {"RAW_OBSERVATION_ID": 2}]}) is None
         and ing._a_observacao_desta_passagem({"RAW_OBSERVATIONS": []}) is None,
         "zero e N>1 saem NULL: um id emprestado nao e um id errado, e outra"
         " observacao")

    # G · so a etapa RAW nomeia a observacao.
    negou = False
    try:
        rastro.registrar(sql, run_id=RUN, etapa="DERIVED", estado="PASS",
                         raw_asset_id=raw_id)
    except ValueError:
        negou = True
    caso("N_G_outra_etapa_nao_assina_a_observacao_do_RAW", negou,
         "DERIVED a apontar para raw_asset e assinar o trabalho da anterior")

    # ═══════════════════════════════════════════════════════════════════
    # RETRY · REUSE · NOVA OBSERVACAO — quatro coisas, e nenhuma colapsa
    # ═══════════════════════════════════════════════════════════════════
    print("\nRETRY, REUSO E OBSERVACAO NOVA")

    # RETRY · a MESMA corrida outra vez. A linha anterior FICA, e a nova nasce
    # noutra tentativa. Apagar a que falhou apagaria a evidencia do conserto.
    porta([dict(item)],
                corrida=corrida(), armazem=ing.ArmazemLocal(RAIZ),
                memoria=banco, raiz=RAIZ, banco_do_rastro=sql)
    t_r = sql.executa(
        "select tentativa, estado, reused, passed from public.etapa_da_corrida"
        " where run_id = '%s' and etapa = 'RAW' order by tentativa" % RUN)
    caso("Y1_o_retry_nao_apaga_a_tentativa_anterior",
         len(t_r) == 2 and [_inteiro(x[0]) for x in t_r] == [0, 1],
         "tentativas na mesma corrida: %s" % [x[0] for x in t_r])
    # ⚠️ O RASTRO REFLETE O DONO — NAO REDESENHA A IDEMPOTENCIA.
    # Esta prova nao decide se um retry devia reutilizar: ela confere que o
    # que o rastro diz e o que o dono FEZ. Quem foi reaproveitado sai de
    # `passed`, ou a mesma linha cai em dois baldes e a conta abre um buraco
    # NEGATIVO.
    conta = sql.executa(
        "select tentativa, passed, reused, unaccounted_input"
        " from public.etapa_da_corrida"
        " where run_id = '%s' and etapa = 'RAW' order by tentativa" % RUN)
    caso("Y2_o_reencontro_conta_se_como_REUSED_e_nao_como_PASSED_novo",
         len(conta) == 2 and _inteiro(conta[1][2]) == 1
         and _inteiro(conta[1][1]) == 0,
         "tentativa 1: reused=%s passed=%s"
         % (conta[1][2] if len(conta) > 1 else "?",
            conta[1][1] if len(conta) > 1 else "?"))
    caso("Y2b_e_nenhuma_tentativa_abre_buraco_na_conta",
         bool(conta) and all(_inteiro(x[3]) == 0 for x in conta),
         "unaccounted_input por tentativa: %s" % [x[3] for x in conta])

    # NOVA CORRIDA, MESMOS BYTES · o contrato da fase 10 (migration 027) diz
    # que isto e uma OBSERVACAO NOVA. Os dois rastros tem de apontar para
    # observacoes DISTINTAS — o mesmo byte visto duas vezes sao dois factos.
    run_n = RUN + "-N"
    porta([dict(item)],
                corrida=corrida(run_n, "2026-09-09T00:00:00Z"),
                armazem=ing.ArmazemLocal(RAIZ), memoria=banco, raiz=RAIZ,
                banco_do_rastro=sql)
    t_n = linhas_raw(sql, run_n)
    alvo_1, alvo_n = t[2], (t_n[0][2] if t_n else "<NULL>")
    caso("Y3_mesmos_bytes_noutra_corrida_sao_OUTRA_observacao",
         alvo_n != "<NULL>" and alvo_n != alvo_1,
         "raw_asset_id: corrida 1 = %s · corrida 2 = %s" % (alvo_1, alvo_n))
    shas = sql.executa(
        "select count(distinct sha256), count(distinct id)"
        " from public.raw_asset where run_id in ('%s','%s')" % (RUN, run_n))
    caso("Y4_e_os_bytes_sao_os_MESMOS_e_isso_nao_as_junta",
         _inteiro(shas[0][0]) == 1 and _inteiro(shas[0][1]) == 2,
         "sha256 distintos=%s · observacoes=%s — SHA IDENTIFICA BYTES,"
         " NAO OBSERVACAO" % (shas[0][0], shas[0][1]))

    # ── A POLITICA DE FALHA DA PROPRIA TELEMETRIA, MEDIDA E NAO INVENTADA ──
    class BancoQueParte:
        def executa(self, _sql):
            raise RuntimeError("o rastro caiu")

    subiu = False
    try:
        ing.receber([dict(item)],
                    corrida=corrida(RUN + "-TEL"),
                    armazem=ing.ArmazemLocal(RAIZ), memoria=banco, raiz=RAIZ,
                    banco_do_rastro=BancoQueParte())
    except Exception:                                        # noqa: BLE001
        subiu = True
    ficou = sql.executa("select count(*) from public.raw_asset"
                        " where run_id = '%s'" % (RUN + "-TEL"))
    caso("T1_a_falha_do_rastro_SOBE_como_ja_subia", subiu,
         "politica ATUAL preservada · G-TEL-01 continua divida declarada")
    caso("T2_e_o_bruto_preservado_FICA",
         _inteiro(ficou[0][0]) == 1,
         "falha de telemetria != falha de RAW: a observacao nao se apaga")

    caso("Z_nenhuma_passagem_rebentou_a_meio_da_medicao", not REBENTOU,
         "; ".join(REBENTOU) or "todas as passagens deram veredito")

    print("=" * 70)
    for nome, ok, detalhe in fora:
        print("  %-4s %-56s %s" % ("PASS" if ok else "FALHA", nome, detalhe))
    veredito = all(ok for _n, ok, _d in fora)
    print("=" * 70)
    print("RAW_FALA=%s" % ("PASS" if veredito else "FAIL"))
    print("  o que isto prova: a etapa RAW deixa passagem observavel, e a")
    print("  passagem aponta para a OBSERVACAO que ela produziu.")
    print("  o que NAO prova: producao, READY, nem politica nova para")
    print("  G-TEL-01 — essa foi MEDIDA, e continua a ser a que ja era.")
    return 0 if veredito else 1


if __name__ == "__main__":
    raise SystemExit(main())
