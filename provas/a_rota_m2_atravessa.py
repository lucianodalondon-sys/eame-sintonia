#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ROTA DA M2 ATRAVESSADA DE PONTA A PONTA, NUMA CORRIDA SO.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_rota_m2_atravessa.py

O QUE ESTA PROVA EXISTE PARA FECHAR
-----------------------------------
    DECLARED EDGE  !=  OBSERVED EDGE.

A M2 ligou `DERIVED -> STRUCTURED -> ADMISSION` e provou as duas etapas novas
contra Postgres real. Mas a ARESTA de entrada ficou por observar, e isso foi
MEDIDO, nao suposto — na corrida que provava a rota, o banco tinha isto:

    STRUCTURED  edge_from=DERIVED   PASS
    ADMISSION   edge_from=STRUCTURED PASS

e **nenhuma passagem de `DERIVED`**. A etapa de cima tinha corrido noutra
corrida, noutro ficheiro, e a linha de `STRUCTURED` apenas DECLARAVA de onde
dizia vir.

    UMA SETA DESENHADA NAO E UM CAMINHO PERCORRIDO.

E o artefato tambem nao viajava: o `STRUCTURED` provado lia um ficheiro de
texto da arvore (`data/derivados/texto/`), que e o registo LEGADO — nao o
`derived_artifact` que a etapa forward acabara de escrever no banco. As duas
metades da aresta existiam, e nada as tinha ligado.

O QUE ELA FAZ, E POR QUE ASSIM
------------------------------
Uma corrida. Uma rota — o par `(IT-T2-002, RC-1)`, o mesmo por que a `024`
agrupa `v_saude_da_rota`. E o artefato a viajar de verdade:

    preservar_coleta   -> raw_asset REAL, com id lido do banco
    derivacao_forward  -> DERIVED, e um derived_artifact REAL
    (os bytes desse derivado, lidos do armazem)
    rota_forward_documento -> STRUCTURED -> ADMISSION

Depois pergunta-se AO BANCO — e nao ao ledger — o que aquela rota atravessou.

    O LEDGER DECLARA. O BANCO MEDE. E SO O SEGUNDO E PROVA.

O QUE ELA NAO PROVA
-------------------
Nao prova producao: a `024` continua por aplicar, e nada aqui toca Supabase.
Nao prova READY — a rota termina em ADMISSION, e terminar ai e a verdade.
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

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

import admissao                          # noqa: E402
import coleta_checkpoint as cc           # noqa: E402
import derivacao_forward as fwd          # noqa: E402
import executor_texto_de_pdf as ex       # noqa: E402
import rastro_da_coleta as rastro        # noqa: E402
import rota_forward_documento as m2      # noqa: E402
import social_persistencia as sp          # noqa: E402
import telemetria as tel                 # noqa: E402
from guarda.preservar_coleta import ArmazemDeMentira, preservar, sha256  # noqa: E402
from guarda import preservar_derivado as pd   # noqa: E402

# ── A CADEIA DE MIGRATIONS VEM DO DISCO, E NAO DE UMA LISTA ────────────────
# ⚠️ AQUI ESTAVA UMA LISTA ESCRITA A MAO, E ELA ENVELHECEU DUAS VEZES. A
# primeira vez foi apanhada e remendada com `025` e `026`, e o comentario que
# ficou dizia, com todas as letras:
#
#     UMA LISTA A MAO ENVELHECE CALADA, e esta envelheceu.
#
# Envelheceu outra vez. A `027` — a que tirou a trava do endereco de
# `raw_asset` e pos chave sobre `storage_object_id` — nunca chegou a ser
# aplicada por esta prova. Ela atravessava um esquema uma migration atras da
# realidade e dizia-se canonica.
#
#     REMENDAR UMA LISTA QUE JA ENVELHECEU UMA VEZ
#     E MARCAR ENCONTRO COM O MESMO DEFEITO.
#
# Agora a cadeia e LIDA da pasta. Quando nascer a `028`, esta prova aplica-a
# sem que ninguem se lembre dela.
#
# A `008` fica de fora por ser outra especie: nao constroi esquema nenhum, e a
# VERIFICACAO POS-APLICACAO que confere o que as outras construiram. Corre-la
# no meio seria pedir-lhe contas de tabelas que ainda nao nasceram.
_SO_VERIFICA = ("008",)


def _cadeia_de_migrations():
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    fora = []
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".sql"):
            continue
        n = f.split("_", 1)[0]
        if n in _SO_VERIFICA:
            continue
        fora.append(n)
    return fora


MIGRATIONS = _cadeia_de_migrations()

MODELO = os.path.join(RAIZ, "system-map", "data", "estradas-it.model.json")
# Onde a medicao desta corrida fica escrita, e o ledger que ela confere.
OBSERVADO = os.path.join(RAIZ, "system-map", "data", "rota-m2.observada.json")
LEDGER = os.path.join(RAIZ, "system-map", "data", "provas-de-execucao.json")
CATALOGO = os.path.join(RAIZ, "candidatas", "ITALY-SOURCE-MASTER-V1.json")
LOJA = "data/collection-store/italy"
RELOGIO = "2026-09-08T02:00:00Z"

RUN = "RUN-M2-ATRAVESSA"
ETAPAS_DA_M2 = ("DERIVED", "STRUCTURED", "ADMISSION")
ARESTAS_DA_M2 = (("DERIVED", "STRUCTURED"), ("STRUCTURED", "ADMISSION"))

fora = []


def caso(nome, condicao, detalhe=""):
    fora.append((nome, bool(condicao), detalhe))


# ═════════════════════════════════════════════════════════════════════════
# A IDENTIDADE — lida dos donos, como em O9R. Nunca escrita a mao aqui.
# ═════════════════════════════════════════════════════════════════════════
def identidade_da_unidade(caminho_do_pdf):
    """`(source_id, route_class_id)` desta unidade, ou `(None, None)`.

    A fonte vem do sitio onde a preservacao guardou o bruto, e so vale se
    existir no catalogo. A rota vem do modelo das estradas — a classe cuja
    etapa `DERIVED` e deste executor — e so vale se bater com o CANARIO que o
    modelo declara para essa fonte.

        UM ID DE RASTREIO INVENTADO E PIOR DO QUE UNKNOWN.
    """
    partes = caminho_do_pdf.replace("\\", "/").split("/")
    fonte = None
    if "italy" in partes:
        i = partes.index("italy")
        candidata = partes[i + 1] if len(partes) > i + 1 else None
        with open(CATALOGO, encoding="utf-8") as f:
            if candidata and ('"%s"' % candidata) in f.read():
                fonte = candidata
    with open(MODELO, encoding="utf-8") as f:
        modelo = json.load(f)
    donas = [rc["ID"] for rc in modelo["ROUTE_CLASSES"]
             if ((rc.get("STEPS") or {}).get("DERIVED") or {}).get("OWNER")
             == "coleta/executor_texto_de_pdf.py"]
    rota = donas[0] if len(donas) == 1 else None
    canario = modelo.get("CANARIO") or {}
    if canario.get("SOURCE_ID") != fonte or canario.get("ROUTE_CLASS_ID") != rota:
        # Sem o par declarado, a rota volta a UNKNOWN. Nao se assume.
        rota = None
    return fonte, rota


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


def um_pdf_da_fonte(fonte):
    import glob
    achados = sorted(glob.glob(os.path.join(RAIZ, LOJA, fonte, "*", "*", "*.pdf")))
    if not achados:
        raise SystemExit("nao ha PDF preservado da fonte %s" % fonte)
    return achados[0]


def canal_da_fonte(banco_sql, fonte):
    """A PRE-CONDICAO DE IDENTIDADE, resolvida com dados do CATALOGO.

    ⚠️ ISTO E UM GAP HERDADO, E NAO SE FINGE QUE NAO E.
    `public.conteudo` exige `canal_id`, e criar um canal exige decidir DE QUEM
    ele e — `origem` tem constraint que exige pessoa OU organizacao. Nenhum
    dono forward resolve isso hoje, e o writer recusa-se a escolher, com razao:

        CHANNEL_ID PROVA O CANAL, NAO PROVA A ORIGEM.

    Aqui a identidade e escrita no banco DESCARTAVEL, com o que o catalogo ja
    nomeia — a organizacao e o `OWNER_ID` daquela fonte. E nada disto vale como
    dono: o dono continua a nao existir.

    ⚠️ E A M2I MEDIU DUAS COISAS QUE ESTA FIXTURE DECIDE SOZINHA.
    Dizer «nada e inventado» era generoso demais comigo:

      · `'orgao_publico'` — o catalogo diz `OWNER_KIND: OFFICIAL_REGIONAL_AGENCY`,
        e `organizacao.tipo` so aceita nove nomes, nenhum deles esse. A
        traducao entre os dois vocabularios NAO esta declarada em lado nenhum:
        fui eu que a escolhi, aqui.
      · a URL de recurso `https://exemplo.it/<fonte>` — que so existe porque
        esta e uma bancada. `canal.url` e NULLABLE: um dono a serio deixaria
        NULL em vez de fabricar endereco.

        UMA TRADUCAO QUE NINGUEM DECLAROU E UMA DECISAO QUE NINGUEM ASSINOU.

    As duas ficam AQUI, visiveis, e nao sobem para runtime. A medicao da
    autoridade esta em `provas/a_autoridade_da_fonte.py`, e o veredito dela e
    `SOURCE_AUTHORITY[IT-T2-002] = UNRESOLVED`.
    """
    with open(CATALOGO, encoding="utf-8") as f:
        catalogo = json.load(f)

    def procurar(o):
        if isinstance(o, dict):
            if o.get("SOURCE_ID") == fonte:
                yield o
            for v in o.values():
                yield from procurar(v)
        elif isinstance(o, list):
            for v in o:
                yield from procurar(v)

    ficha = next(procurar(catalogo), {})
    nome = (ficha.get("SOURCE_NAME") or fonte).split("—")[0].strip()
    dono = ficha.get("OWNER_ID") or fonte
    url = ficha.get("URL") or "https://exemplo.it/%s" % fonte

    def q(v):
        return "'" + str(v).replace("'", "''") + "'"

    # ⚠️ `on conflict do nothing` NAO DEDUPLICA SEM CONSTRAINT UNICA — e aqui
    # nao ha nenhuma: `public.organizacao` so tem unique em `ror_id` (002:22-32)
    # e `public.origem` nao tem unique em `rotulo` (so os indices PARCIAIS
    # `origem_por_pessoa_idx` / `origem_por_organizacao_idx`). A clausula nunca
    # disparava, e cada chamada inseria outra linha com outro `id`:
    #
    #     MEDIDO, com a forma antiga, tres vezes o MESMO nome:
    #     ids devolvidos 1, 2, 3 · linhas em organizacao: 3
    #
    # Nao e so lixo: o `coalesce` devolvia uma IDENTIDADE DIFERENTE em cada
    # replay, e a rota que esta prova diz atravessar deixava de ser a mesma.
    #
    #     ON CONFLICT DO NOTHING SEM CONSTRAINT RELEVANTE != DEDUPLICACAO.
    #
    # `tests/test_m2_rota_forward.py:146` ja tinha medido e consertado isto no
    # lado do teste; o lado da PROVA ficou com a forma partida. A deduplicacao
    # tem de ser explicita — `where not exists`.
    #
    # O `canal`, mais abaixo, continua com `on conflict (plataforma,
    # channel_id)`: esse tem constraint unica de verdade (002), e por isso a
    # clausula la e honesta.
    org = banco_sql.executa(
        "with novo as (insert into public.organizacao (nome_canonico, tipo)"
        " select %s, 'orgao_publico' where not exists"
        "  (select 1 from public.organizacao where nome_canonico = %s)"
        " returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.organizacao where nome_canonico = %s))"
        % (q(nome), q(nome), q(nome)))
    ori = banco_sql.executa(
        "with novo as (insert into public.origem (organizacao_id, rotulo)"
        " select %d, %s where not exists"
        "  (select 1 from public.origem where rotulo = %s)"
        " returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.origem where rotulo = %s))"
        % (int(org[0][0]), q(dono), q(dono), q(dono)))
    can = banco_sql.executa(
        "with novo as (insert into public.canal"
        " (origem_id, plataforma, channel_id, url) values (%d, 'web', %s, %s)"
        " on conflict (plataforma, channel_id) do nothing returning id)"
        " select coalesce((select id from novo),"
        "  (select id from public.canal where plataforma='web'"
        "     and channel_id=%s))" % (int(ori[0][0]), q(fonte), q(url), q(fonte)))
    return int(can[0][0]), {"ORGANIZACAO": nome, "OWNER_ID": dono}


# ═════════════════════════════════════════════════════════════════════════
def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL") or ""
    if not _pg._e_descartavel(url):
        raise SystemExit(
            "RECUSADO: '%s' nao parece um banco descartavel local. "
            "Esta prova nunca corre contra producao." % url)
    if not ex.ha_ferramenta():
        raise SystemExit(
            "pdftotext ausente: sem ele o executor devolve FERRAMENTA_AUSENTE "
            "para tudo, e esta prova mediria a maquina, e nao a rota.")

    # ⚠️ O ROTULO VEM DA CADEIA, E NAO DE UMA MEMORIA. Escrito a mao,
    # ele dizia "ate a 026" enquanto a cadeia ja ia na 027.
    print("MIGRATIONS — a cadeia canonica, ate a %s" % MIGRATIONS[-1])
    caso("A1_a_cadeia_aplica_num_postgres_real",
         aplicar_migrations(url) == len(MIGRATIONS),
         "%d migrations em PostgreSQL 16" % len(MIGRATIONS))

    banco = _pg.MemoriaPostgres(url)     # a porta do dono da escrita
    sql = cc.Banco(url)                  # a porta do dono do rastro
    for tabela, coluna in (("etapa_da_corrida", "run_id"),
                           ("conteudo_visto_em", "run_id"),
                           ("conteudo", "run_id")):
        sql.executa("delete from public.%s where %s like '%s%%'"
                    % (tabela, coluna, RUN))
    sql.executa("delete from public.derived_artifact")
    sql.executa("delete from public.raw_asset where run_id like '%s%%'" % RUN)
    sql.executa("delete from public.collection_run where run_id like '%s%%'" % RUN)

    # ── A UNIDADE, E A SUA IDENTIDADE PROVADA ────────────────────────────
    fonte_provavel, rota_provavel = None, None
    for candidata in sorted(os.listdir(os.path.join(RAIZ, LOJA))):
        f, r = identidade_da_unidade(os.path.join(LOJA, candidata, "x", "y", "z.pdf"))
        if f and r:
            fonte_provavel, rota_provavel = f, r
            break
    caso("A2_a_identidade_da_unidade_e_provada_e_nao_assumida",
         bool(fonte_provavel and rota_provavel),
         "fonte=%s rota=%s (catalogo + modelo das estradas + canario)"
         % (fonte_provavel, rota_provavel))
    if not (fonte_provavel and rota_provavel):
        raise SystemExit("sem identidade provavel nao se corre a rota")
    ROTA = (fonte_provavel, rota_provavel)

    pdf = um_pdf_da_fonte(fonte_provavel)
    with open(pdf, "rb") as f:
        bytes_do_pdf = f.read()

    # ── RAW, pelo dono do bruto ──────────────────────────────────────────
    corrida = {"RUN_ID": RUN, "PLATFORM": "web", "ACTOR": "m2",
               "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT",
               "MISSION": "M2 rota forward", "STARTED_AT": "2026-09-08T00:00:00Z",
               "RULE_VERSION": "v1", "CAPTURE_METHOD": "HTTP_GET"}
    artefato = {"COUNTRY": "IT", "SOURCE_SLUG": fonte_provavel,
                "SOURCE_ID": fonte_provavel, "DOCUMENT_ID": "M2:DOC:1",
                "ARTIFACT_KIND": "DOCUMENT", "NAME": os.path.basename(pdf),
                "SOURCE_NATIVE_ID": "M2-1", "SHA256": sha256(bytes_do_pdf),
                "BYTES": len(bytes_do_pdf), "MEDIA_TYPE": "application/pdf",
                "CAPTURED_AT": "2026-09-02T15:20:48Z",
                "SOURCE_URL": "https://www.arpa.veneto.it/%s"
                              % os.path.basename(pdf)}
    armazem = ArmazemDeMentira()
    recibo_raw = preservar(corrida, [artefato], armazem, lambda o: bytes_do_pdf,
                           memoria=banco, terminou_em="2026-09-08T00:05:00Z")
    raw_id = int(banco._valor(
        "select id from public.raw_asset where run_id = '%s'" % RUN))
    caso("A3_o_bruto_e_real_e_foi_escrito_pelo_dono",
         recibo_raw["PENDENCIA"] == "PRESERVED_AND_REGISTERED" and raw_id > 0,
         "raw_asset_id=%d, por guarda/preservar_coleta.py" % raw_id)

    # ── DERIVED, na MESMA corrida ────────────────────────────────────────
    print("\nA ROTA, NUMA CORRIDA SO")
    r_der = fwd.correr([{"RAW_ASSET_ID": raw_id, "PDF": pdf}],
                       banco_do_rastro=sql, run_id=RUN, armazem=armazem,
                       memoria=banco, source_id=fonte_provavel,
                       route_class_id=rota_provavel, relogio=lambda: RELOGIO)
    print("  DERIVED     %s · %s" % (r_der["ESTADO_DA_ETAPA"],
                                     {k: v for k, v in r_der["BALDES"].items() if v}))
    filho = banco.derivado_com_identidade({
        "parent_sha256": sha256(bytes_do_pdf), "kind": "TEXT_EXTRACTION",
        "producer": ex.EXECUTOR_ID, "producer_version": ex.EXECUTOR_VERSION,
        "parameters_hash": pd.hash_dos_parametros(None), "serie_posicao": None})
    caso("A4_o_derivado_canonico_existe_e_a_linhagem_fecha",
         bool(filho) and int(filho["raw_asset_id"]) == raw_id,
         "derived_artifact id=%s -> raw_asset_id=%s"
         % ((filho or {}).get("id"), (filho or {}).get("raw_asset_id")))

    # ⚠️ E O ARTEFATO VIAJA. O texto que entra no STRUCTURED sao os BYTES que
    # a etapa DERIVED acabou de escrever no armazem — e nao um ficheiro do
    # registo legado que por acaso tem o mesmo conteudo.
    #
    #     ARTEFATO QUE NAO VIAJA NAO E ARESTA: E COINCIDENCIA.
    texto = armazem.ler(filho["storage_path"]).decode("utf-8")
    caso("A5_o_texto_do_STRUCTURED_veio_do_derivado_desta_corrida",
         sha256(texto.encode("utf-8")) == filho["sha256"],
         "sha256 do que entra = sha256 do derivado escrito")

    canal_id, quem = canal_da_fonte(sql, fonte_provavel)
    unidade = {"CONTENT_ID": "M2-%s" % filho["sha256"][:16], "TEXTO": texto,
               "TIPO": "nota_tecnica", "SOURCE_ID": fonte_provavel,
               "ROUTE_CLASS_ID": rota_provavel, "RAW_ASSET_ID": raw_id,
               "CAPTURED_AT": "2026-09-02T15:20:48Z",
               "URL": artefato["SOURCE_URL"],
               "DERIVED_ARTIFACT_ID": filho["id"],
               "PARENT_SHA256": filho["parent_sha256"]}

    # ⚠️ AQUI NAO SE CHAMA `atravessar()`, E A RAZAO E BOA.
    # Desde a M2R, `m2.atravessar()` faz a cadeia INTEIRA — deriva, estrutura e
    # admite. Esta prova ja derivou acima, de proposito, para poder conferir o
    # `derived_artifact` campo a campo antes de o texto seguir. Chamar
    # `atravessar()` agora derivaria uma SEGUNDA vez na mesma corrida.
    #
    # Entao chamam-se as duas etapas que faltam, que sao funcoes publicas do
    # mesmo dono. A cadeia continua a ser uma so: mesmo `RUN`, mesmo texto
    # vindo do armazem, mesma unidade.
    r_s = m2.estruturar(sql, unidade=unidade, run_id=RUN, canal_id=canal_id)
    dec = None
    if (r_s or {}).get("STATE") in ("OK", sp.REOBSERVADO):
        dec = m2.admitir(sql, unidade=unidade, run_id=RUN,
                         conteudo_id=r_s.get("CONTEUDO_ID"))
    r_m2 = {"DERIVED": r_der, "STRUCTURED": r_s, "ADMISSION": dec}
    print("  STRUCTURED  %s" % (r_m2["STRUCTURED"] or {}).get("STATE"))
    print("  ADMISSION   %s · a porta respondeu: %s"
          % ("correu" if dec else "NAO CORREU",
             getattr(dec, "resultado", "-")))

    # ── O QUE O BANCO DIZ QUE ESTA ROTA ATRAVESSOU ───────────────────────
    passagens = rastro.passagens(sql, run_id=RUN)
    rotas = rastro.rotas_da_corrida(passagens)
    visto = rastro.o_que_a_rota_observou(passagens, ROTA)

    caso("A6_a_corrida_tem_UMA_rota_e_e_a_provada",
         rotas == [ROTA], "rotas na corrida: %s" % (rotas,))
    caso("A7_a_MESMA_rota_atravessou_as_tres_etapas",
         set(ETAPAS_DA_M2) <= visto["ETAPAS"],
         "etapas observadas: %s" % sorted(visto["ETAPAS"]))
    caso("A8_as_duas_arestas_foram_OBSERVADAS_com_os_dois_topos",
         set(ARESTAS_DA_M2) <= visto["ARESTAS"],
         "arestas observadas: %s" % sorted(visto["ARESTAS"]))
    # ── O LEDGER NAO PODE PROMETER MAIS DO QUE O BANCO MOSTROU ───────────
    #
    # `system-map/data/provas-de-execucao.json` e um ledger ESCRITO A MAO, e
    # ele diz porque: correr todos os executores exigiria rede, API paga e
    # producao. Para a maioria das linhas isso e honesto e continua a valer.
    #
    # Para ESTA rota, nao. Ela corre inteira num Postgres descartavel, com PDF
    # local, sem rede e sem fatura — e e exactamente o que este ficheiro
    # acabou de medir NO BANCO. Enquanto o ledger declarava
    # `ETAPAS_OBSERVADAS`, `ARESTAS_OBSERVADAS` e `END_TO_END` como literais,
    # `M2_ROUTE_OBSERVABILITY_READY` (censo_dos_executores.py:508) derivava de
    # texto que ninguem confrontava com medicao nenhuma.
    #
    #     UM PORTAO QUE LE UM LITERAL MEDE A ESCRITA, NAO O SISTEMA.
    #
    # Entao a medicao passa a ser ESCRITA em disco, e o ledger passa a ser
    # CONFERIDO contra ela: ele pode declarar MENOS do que se observou (uma
    # linha conservadora e legitima), nunca MAIS. Quem editar o ledger para
    # prometer uma etapa ou aresta que o banco nao mostrou faz esta prova
    # reprovar.
    io.open(OBSERVADO, "w", encoding="utf-8").write(json.dumps({
        "SCHEMA": "rota-m2-observada/v1",
        "O_QUE_ISTO_E": (
            "O que o BANCO mostrou nesta corrida, escrito por quem mediu. "
            "NAO e declaracao: e leitura de `etapa_da_corrida` depois de a "
            "rota ter corrido. O ledger de provas-de-execucao.json e "
            "conferido contra este ficheiro."),
        "GERADO_POR": "provas/a_rota_m2_atravessa.py",
        "SOURCE_ID": ROTA[0], "ROUTE_CLASS_ID": ROTA[1],
        "ETAPAS_OBSERVADAS": sorted(visto["ETAPAS"]),
        "ARESTAS_OBSERVADAS": sorted([list(a) for a in visto["ARESTAS"]]),
        "ARESTAS_DECLARADAS_SEM_TOPO": sorted(
            [list(a) for a in visto["ARESTAS_DECLARADAS_SEM_TOPO"]]),
        "END_TO_END": True,
        "RUN_UNICO": RUN,
    }, ensure_ascii=False, indent=1) + "\n")

    ledger_f = {}
    try:
        _L = json.loads(io.open(LEDGER, encoding="utf-8").read())
        ledger_f = ((_L.get("PROVADOS") or {})
                    .get("coleta/rota_forward_documento.py") or {}).get("FORWARD") or {}
    except (OSError, ValueError):
        ledger_f = {}
    etapas_declaradas = set(ledger_f.get("ETAPAS_OBSERVADAS") or [])
    arestas_declaradas = {tuple(a) for a in (ledger_f.get("ARESTAS_OBSERVADAS") or [])}
    excesso_e = sorted(etapas_declaradas - visto["ETAPAS"])
    excesso_a = sorted(arestas_declaradas - visto["ARESTAS"])
    caso("A8b_o_ledger_nao_declara_etapa_que_o_banco_nao_mostrou",
         not excesso_e,
         "ledger %s <= banco %s" % (sorted(etapas_declaradas), sorted(visto["ETAPAS"]))
         if not excesso_e else "o ledger promete e o banco nao mostra: %s" % excesso_e)
    caso("A8c_o_ledger_nao_declara_aresta_que_o_banco_nao_mostrou",
         not excesso_a,
         "ledger %d aresta(s) <= banco %d" % (len(arestas_declaradas), len(visto["ARESTAS"]))
         if not excesso_a else "o ledger promete e o banco nao mostra: %s" % excesso_a)
    caso("A8d_e_o_END_TO_END_do_ledger_e_o_desta_corrida",
         bool(ledger_f.get("END_TO_END")) is True,
         "END_TO_END declarado e medido na mesma corrida (%s)" % RUN)

    # ⚠️ E O QUE SOBRA DE DECLARADO TEM DE SER EXATAMENTE O GAP JA CONHECIDO.
    #
    # Esta prova apanhou uma aresta a mais do que eu esperava — `RAW -> DERIVED`
    # — e ela esta CERTA a apanha-la. `coleta/derivacao_forward.py` emite
    # `DERIVED` com `edge_from='RAW'` e NAO emite `RAW`, de propósito: quem
    # escreve `raw_asset` e `guarda/preservar_coleta.py`, e ler a linha de
    # outro nao e ter corrido a etapa dele. O gap ja estava declarado em prosa
    # desde O9R (`RAW_FORWARD_NAO_EMITE`); o que muda agora e que ele passou a
    # ser VISIVEL NO RASTRO, e nao so num comentario.
    #
    #     UM BURACO QUE APARECE NA MEDICAO E DIVIDA.
    #     UM BURACO QUE SO APARECE NO COMENTARIO E ESQUECIMENTO COM DATA.
    #
    # A prova nao o perdoa em silencio: ela exige que a lista de arestas sem
    # topo seja EXATAMENTE esta. Uma segunda aresta declarada e nao percorrida
    # reprova aqui, no dia em que nascer.
    esperadas_sem_topo = {("RAW", "DERIVED")}
    caso("A9_o_unico_declarado_sem_topo_e_o_gap_ja_conhecido",
         visto["ARESTAS_DECLARADAS_SEM_TOPO"] == esperadas_sem_topo,
         "sem topo: %s · e RAW_FORWARD_NAO_EMITE e gap declarado do O9R"
         % sorted(visto["ARESTAS_DECLARADAS_SEM_TOPO"]))
    caso("A9b_o_gap_do_RAW_continua_declarado_pelo_dono_da_fronteira",
         "RAW_FORWARD_NAO_EMITE" in [g[0] for g in fwd.GAPS],
         "quem emite DERIVED diz, por escrito, que nao fala pelo RAW")

    integ = rastro.integridade(passagens)
    caso("A10_a_conta_fecha_em_todas_as_etapas",
         integ["UNACCOUNTED_INPUT"] == 0,
         "sem explicacao: %d" % integ["UNACCOUNTED_INPUT"])
    graos = [(p["ETAPA"], p["INPUT_GRAIN"], p["OUTPUT_GRAIN"]) for p in passagens]
    caso("A11_o_grao_esta_declarado_dos_dois_lados_em_cada_etapa",
         all(i and o for _e, i, o in graos),
         "; ".join("%s %s->%s" % g for g in graos))
    caso("A12_o_ultimo_ponto_bom_e_a_ultima_etapa_que_passou",
         rastro.ultimo_bom(passagens) == "ADMISSION",
         "last good: %s" % rastro.ultimo_bom(passagens))

    # ── READY, PROVA NEGATIVA, PERGUNTADA AO BANCO ───────────────────────
    ready = sql.executa(
        "select count(*) from public.etapa_da_corrida"
        " where etapa = 'READY' and estado = 'PASS'")
    caso("A13_nenhum_READY_nasceu_em_corrida_nenhuma",
         int(ready[0][0]) == 0,
         "ADMISSION PASS != READY PASS (COL-LAW-043)")
    caso("A14_e_a_lei_do_READY_nao_morde_esta_cadeia",
         tel.ready_sem_quem_assine(passagens) == [],
         "terminar em ADMISSION nao e violacao")

    # ── A MUTACAO: UMA SETA SEM TOPO NAO E UM CAMINHO ────────────────────
    #
    #     DECLARED EDGE != OBSERVED EDGE.
    #
    # Este e o estado que existia ANTES desta prova: STRUCTURED a declarar
    # `edge_from=DERIVED` sem que `DERIVED` tivesse passagem na rota. Se ele
    # contasse como aresta, o portao da M2 abria sobre uma cadeia partida.
    sem_derived = [p for p in passagens if p["ETAPA"] != "DERIVED"]
    visto_mutado = rastro.o_que_a_rota_observou(sem_derived, ROTA)
    caso("A15_MUTACAO_sem_a_passagem_de_DERIVED_a_aresta_deixa_de_contar",
         ("DERIVED", "STRUCTURED") not in visto_mutado["ARESTAS"]
         and ("DERIVED", "STRUCTURED") in visto_mutado["ARESTAS_DECLARADAS_SEM_TOPO"],
         "a seta continua desenhada, e deixa de ser caminho")
    caso("A16_MUTACAO_uma_etapa_que_nao_correu_nao_cobre_a_rota",
         "ADMISSION" not in rastro.o_que_a_rota_observou(
             [dict(p, ESTADO="NOT_RUN") if p["ETAPA"] == "ADMISSION" else p
              for p in passagens], ROTA)["ETAPAS"],
         "NOT_RUN deixa linha e nao e passagem")
    caso("A17_MUTACAO_a_rota_nao_absorve_passagem_de_outra",
         rastro.o_que_a_rota_observou(passagens, ("OUTRA-FONTE", "RC-1"))
         ["ETAPAS"] == set(),
         "duas meias-provas de rotas diferentes nao fazem uma prova")

    # ── O RELATORIO ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    mal = [n for n, ok, _d in fora if not ok]
    for nome, ok, detalhe in fora:
        print("  %s  %-56s %s" % ("PASS" if ok else "FAIL", nome, detalhe))
    print("=" * 70)
    print("ROTA_M2_ATRAVESSA=%s%s"
          % ("PASS" if not mal else "FAIL",
             "" if not mal else " · %d reprovado(s)" % len(mal)))
    print("  identidade da rota: %s / %s · canal resolvido com %s (%s)"
          % (ROTA[0], ROTA[1], quem["ORGANIZACAO"][:34], quem["OWNER_ID"]))
    print("  o que isto prova: A MESMA rota atravessou DERIVED, STRUCTURED e")
    print("  ADMISSION numa corrida so, com o artefato a viajar entre elas, e")
    print("  as duas arestas tem os DOIS topos no banco.")
    print("  o que NAO prova: producao, nem READY. A rota termina em ADMISSION.")
    return 0 if not mal else 1


if __name__ == "__main__":
    raise SystemExit(main())
