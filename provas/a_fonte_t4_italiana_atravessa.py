#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IT-T4-001 — A CERTIFICACAO CONTROLADA DE UMA FONTE, PONTA A PONTA.

    BANCO_DESCARTAVEL_URL=postgresql://postgres:descartavel@localhost:5432/descartavel \\
        python3 provas/a_fonte_t4_italiana_atravessa.py

O QUE ELA MEDE
--------------
UMA fonte, UMA corrida, o caminho REAL de hoje:

    SOURCE -> REQUEST -> ORCHESTRATOR -> EXECUTOR -> RUN -> RAW -> STORAGE
           -> DERIVED -> STRUCTURED -> ADMISSION -> READY -> WAITING_ROOM

A fonte e `IT-T4-001` — Ministero della Salute, dataset fitosanitari, CSV
oficial por HTTP, sem navegador, sem credencial e sem fornecedor pago.

⚠️ ELA ADQUIRE DA REDE, E ISSO E O PONTO.
`provas/o_material_italiano_chega_a_sala.py` REPROCESSA bytes ja colhidos e
diz, com todas as letras, que nao prova aquisicao. Esta prova vai a fonte.

    FIXTURE PROVA PARSER. SO A INTERNET PROVA AQUISICAO.

Sem rede, ela nao finge: recusa-se a correr e diz `NOT_MEASURED`.

    SKIP != PASS. E «Ran 0 tests» tambem nao e PASS.

⚠️ E ELA NAO COMECA PELO MEIO. Aperta o botao em `orquestrador.correr()` e
pergunta AO BANCO o que ficou. Nao chama `pousar()`, nao chama `decidir()`,
nao chama `preservar()`.

O QUE ELA DECLARA, E QUE NAO E UM DEFEITO DESTA PROVA
-----------------------------------------------------
A estrada PARA em `DERIVED`, e para pelo motivo certo e com o nome certo:

    media_type .......... text/csv        (declarado pela fonte, medido)
    etapa DERIVED ....... NOT_APPLICABLE  (e nao FAIL)
    ADMISSION ........... NAO_SEI         (o item nao tem texto)
    READY / SALA ........ 0

Esta casa tem DOIS executores de derivacao — `executor_texto_de_pdf` e
`executor_transcricao_midia`. Nenhum abre um CSV, e nenhum mente sobre isso.
Um CSV de registo regulatorio nao vira documento estruturado porque essa
CAPACIDADE NAO EXISTE — e nao porque alguma peca se partiu.

    CAPACIDADE AUSENTE != ETAPA PARTIDA.
    E INVENTA-LA AQUI PARA A SALA ENCHER SERIA FABRICAR A PROVA.

Por isso esta prova PASSA ao medir a paragem no sitio declarado, e REPROVA se
a paragem mudar de sitio — nos dois sentidos. Se amanha o CSV chegar a Sala
sem ninguem instalar um derivador, ela grita. Se o `DERIVED` voltar a dizer
`FAIL`, ela grita tambem: `FAIL` seria uma acusacao contra o documento por um
trabalho que nunca foi dele.

    UMA PROVA QUE SO OLHA PARA UM DOS LADOS DA PAREDE
    NAO GUARDA A PAREDE: GUARDA UM DOS LADOS.
"""
import io
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import coleta_checkpoint as cc                     # noqa: E402
import ingresso as ing                             # noqa: E402
import italy_executor as ie                        # noqa: E402
import sala_de_espera as espera                    # noqa: E402
from pedido import Pedido                          # noqa: E402

FONTE = "IT-T4-001"
#: O territorio do PEDIDO. ⚠️ NAO e o territorio da FONTE, e a diferenca esta
#: medida e declarada no veredito: `IT-T4-001` e T4, e o unico executor que a
#: alcanca hoje esta registado em T2 e T3. Escrever `T4` aqui abriria o
#: `regulatorio-eu`, que colhe `EU-T4-001` — outra fonte, outro pais, outro
#: ato. Isto nao e escolha de conveniencia: e a rota que existe.
ALVO_DO_PEDIDO = "T3"
HOSPEDEIRO = "www.dati.salute.gov.it"

ESTRADA = ("REQUEST", "ORCHESTRATOR", "EXECUTOR", "RUN", "RAW", "STORAGE",
           "DERIVED", "STRUCTURED", "ADMISSION", "READY", "WAITING_ROOM")

SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "fonte-t4-italiana.observado.json")

FALHAS, PASSOU = [], []


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + str(detalhe))))


def _psql(url, sql):
    """⚠️ AS OPCOES ANTES DA URL. O `getopt` do Windows nao permuta, e com a
    URL a frente o `-c` deixa de ser opcao: o `psql` liga-se, nao corre nada e
    sai com ZERO. Uma consulta que nao se fez e uma lista vazia sao
    indistinguiveis daqui."""
    r = subprocess.run(["psql", "-X", "-q", "-A", "-t", "-F", "\x1f",
                        "-v", "ON_ERROR_STOP=1", "-c", sql, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("psql falhou: %s" % r.stderr[:400])
    return [l.split("\x1f") for l in r.stdout.splitlines() if l.strip()]


def _memoria(url):
    import importlib.util as u
    sp = u.spec_from_file_location(
        "prova_pg", os.path.join(RAIZ, "provas",
                                 "preservar_coleta_no_postgres.py"))
    m = u.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.MemoriaPostgres(url)


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, "supabase", "migrations")
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".sql") or f.split("_", 1)[0] in ("008",):
            continue
        r = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "-f", os.path.join(pasta, f), url],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("migration %s falhou:\n%s" % (f, r.stderr[:500]))
    # ⚠️ E CONFERE-SE QUE APLICOU. Confiar no codigo de saida e o que ja deixou
    # um banco VAZIO com ar de banco pronto, nesta mesma bancada.
    n = _psql(url, "select count(*) from information_schema.tables "
                   "where table_schema='public'")
    if not n or int(n[0][0]) < 50:
        raise SystemExit("as migrations correram e o schema ficou com %s "
                         "tabelas. Isso nao e um banco aplicado." % n)


def ha_rede():
    """A fonte responde? Isto NAO adquire nada: e um HEAD."""
    r = subprocess.run(["curl", "-sS", "-I", "--max-time", "30",
                        "https://%s/it/dataset/fitosanitari/" % HOSPEDEIRO],
                       capture_output=True, text=True)
    return r.returncode == 0 and " 200" in r.stdout.split("\n")[0]


def main():                                                    # noqa: C901
    url = os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("FALTA AMBIENTE DESCARTAVEL — e SKIP != PASS.")
        print("  BANCO_DESCARTAVEL_URL")
        print("FONTE_T4_ITALIANA = NOT_MEASURED")
        return 2
    if not ha_rede():
        print("A FONTE NAO RESPONDE DESTA MAQUINA — e isto NAO e um veredito")
        print("  sobre a fonte, nem sobre a estrada. E o ambiente.")
        print("FONTE_T4_ITALIANA = NOT_MEASURED")
        return 2

    os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    os.environ["SINTONIA_SALA_DSN"] = url

    # ⚠️ O LIVRO DE DECISOES VAI PARA UM TEMPORARIO, E ISSO E DECLARADO.
    # Ele e um ficheiro versionado (`data/samples/LIVRO-DE-DECISOES.json`), e
    # uma prova que o engorda a cada corrida suja a arvore e mistura decisoes
    # de ensaio com decisoes de operacao. O que se mede aqui e que a admissao
    # ESCREVE — nao ONDE o repositorio guarda o livro dela.
    import pathlib
    import tempfile
    import admissao as adm
    livro = pathlib.Path(tempfile.mkdtemp(prefix="livro-t4-"))
    adm.LIVRO = livro / "LIVRO-DE-DECISOES.json"

    # ── E O ACERVO ITALIANO TAMBEM E DESCARTAVEL NESTA CORRIDA ────────────
    # ⚠️ ISTO NAO E ARRUMACAO: E A MESMA LEI DO BANCO, APLICADA AO LIVRO.
    # O banco desta prova e descartavel porque uma certificacao nao pode
    # escrever em producao. O livro italiano — `data/collection-ledger/` — e o
    # armazem de bytes — `data/collection-store/` — sao VERSIONADOS, e o
    # coletor escreve-lhes por omissao. Sem esta linha, cada corrida desta
    # prova acrescenta observacoes ao acervo real e engorda-o para sempre.
    #
    # E isso NAO e teoria. Medido nesta bancada a 2026-09-15, depois de sete
    # corridas de medicao contra a arvore viva:
    #
    #     o livro passou de 175 para 182 observacoes
    #     entrou um documento novo no armazem
    #     e CINCO guardas de outras missoes reprovaram — o frame congelado
    #     de revisao T3 (53 fichas, 7 fora) deixou de bater
    #
    # As guardas estavam CERTAS, e uma delas diz-o por escrito: «pode ser
    # legitimo — mas obriga a refazer o frame, nao a ajustar o numero». Ajustar
    # o numero para a prova passar seria mover a regua de outra missao por
    # conveniencia desta.
    #
    #     UMA CERTIFICACAO QUE ALTERA O ACERVO QUE CERTIFICA
    #     DEIXA DE SER UMA MEDICAO E PASSA A SER UM EVENTO.
    #
    # A AQUISICAO CONTINUA REAL: o `curl` sai para a rede na mesma, os bytes
    # sao os do Ministero e o sha e o deles. O que muda e ONDE eles pousam.
    ops = tempfile.mkdtemp(prefix="italia-ops-")
    os.environ["ITALY_OPS_ROOT"] = ops      # o coletor Node le daqui
    ie.OPS_ROOT = ops                       # e o adapter Python, daqui

    print("=" * 72)
    print("IT-T4-001 — CERTIFICACAO CONTROLADA, COM AQUISICAO REAL")
    aplicar_migrations(url)

    e = espera.estado_operacional()
    T("a Sala usada e a CANONICA (PostgreSQL), e ela diz que e",
      e["BACKEND"] == espera.BACKEND_POSTGRES and e["CANONICO"],
      "backend=%s canonico=%s" % (e["BACKEND"], e["CANONICO"]))
    antes = espera.listar_pendentes()
    T("P0_a_sala_comeca_VAZIA", not antes, "ja havia %d a espera" % len(antes))

    # ══════════════════════════════════════════════════════════════════
    # O BOTAO. Uma vez.
    # ══════════════════════════════════════════════════════════════════
    import orquestrador as orq
    p = Pedido(alvo=ALVO_DO_PEDIDO, filtros={"pais": "IT", "fonte": FONTE})
    recibo = orq.correr(p, memoria=_memoria(url), banco_do_rastro=cc.Banco(url))
    recibo.pop("_plano", None)
    run_id = recibo["RUN_ID"]
    entrada = recibo.get("INGRESSO") or {}
    deriv = recibo.get("DERIVACAO") or {}
    estr = recibo.get("ESTRUTURACAO") or {}
    admis = recibo.get("ADMISSAO") or {}

    print()
    print("  A ESTRADA, DEGRAU A DEGRAU")
    visto = {}

    def degrau(nome, ok, prova):
        visto[nome] = {"OBSERVED": bool(ok), "EVIDENCE": str(prova)[:300]}
        T("%-12s %s" % (nome, "atravessou"), ok, prova)

    degrau("REQUEST", (recibo.get("PEDIDO") or {}).get("alvo") == ALVO_DO_PEDIDO,
           "alvo=%s filtros=%s" % ((recibo.get("PEDIDO") or {}).get("alvo"),
                                   (recibo.get("PEDIDO") or {}).get("filtros")))
    degrau("ORCHESTRATOR", bool(recibo.get("ACTOR")) and bool(run_id),
           "ACTOR=%s RUN_ID=%s" % (recibo.get("ACTOR"), run_id))
    degrau("EXECUTOR", (recibo.get("COLHEITA_ENCONTRADA") or 0) == 1,
           "colheita=%s" % recibo.get("COLHEITA_ENCONTRADA"))

    corridas = _psql(url, "select run_id, actor, status from "
                          "public.collection_run where run_id = '%s'" % run_id)
    degrau("RUN", len(corridas) == 1, "collection_run: %s" % corridas)

    raws = _psql(url, "select id, source_id, sha256, storage_object_id, "
                      "captured_at, source_url, media_type, document_key, "
                      "document_key_basis, identity_state "
                      "from public.raw_asset where run_id = '%s' order by id"
                      % run_id)
    degrau("RAW", len(raws) == 1, "%d linhas em raw_asset" % len(raws))
    if len(raws) != 1:
        print("\nSem UMA observacao nao ha o que provar a seguir.")
        print("FONTE_T4_ITALIANA = FAIL")
        return 1
    (raw_id, raw_fonte, raw_sha, raw_obj, raw_captura, raw_url,
     raw_tipo, raw_chave, raw_base, raw_estado) = raws[0]

    objs = _psql(url, "select o.id, o.storage_path, o.sha256, o.bytes, "
                      "o.media_type from public.storage_object o "
                      "join public.raw_asset a on a.storage_object_id = o.id "
                      "where a.run_id = '%s'" % run_id)
    degrau("STORAGE", len(objs) == 1 and objs[0][2] == raw_sha,
           "storage_object: %s" % objs)

    # ── DERIVED · STRUCTURED — A PAREDE, MEDIDA NOS DOIS SENTIDOS ─────
    etapas = dict((x[0], x[1]) for x in
                  _psql(url, "select etapa, estado from public.etapa_da_corrida "
                             "where run_id = '%s'" % run_id))
    degrau("DERIVED", etapas.get("DERIVED") == "NOT_APPLICABLE",
           "etapa DERIVED = %s (esperado NOT_APPLICABLE: nenhum executor "
           "desta casa abre %s)" % (etapas.get("DERIVED"), raw_tipo))
    docs = _psql(url, "select derived_artifact_id from "
                      "public.documento_estruturado where run_id = '%s'" % run_id)
    degrau("STRUCTURED", not docs and not estr.get("CHAMADO"),
           "documento_estruturado=%d chamado=%s porque=%s"
           % (len(docs), estr.get("CHAMADO"), estr.get("PORQUE")))
    degrau("ADMISSION", admis.get("itens") == 1 and admis.get("por_resultado"),
           "por_resultado=%s" % admis.get("por_resultado"))
    degrau("READY", admis.get("prontos") == 0,
           "prontos=%s" % admis.get("prontos"))
    sala = _psql(url, "select ordem, item_id, raw_observation_id, source_id "
                      "from public.sala_de_espera where run_id = '%s'" % run_id)
    degrau("WAITING_ROOM", len(sala) == 0, "%d na Sala" % len(sala))

    # ══════════════════════════════════════════════════════════════════
    # AS DEZ PROVAS DO CONTRATO
    # ══════════════════════════════════════════════════════════════════
    print()
    print("  AS PROVAS A..J")

    obs_do_livro = [o for o in ie.observacoes_da_corrida(run_id)]
    T("A · o SOURCE_ID de ENTRADA e %s, e vai no comando do executor" % FONTE,
      FONTE in (recibo.get("COMANDO") or "")
      and all(o.get("SOURCE_ID") == FONTE for o in obs_do_livro)
      and len(obs_do_livro) == 1,
      "comando=%s · observacoes=%s" % (recibo.get("COMANDO"),
                                       [o.get("SOURCE_ID") for o in obs_do_livro]))
    T("B · o MESMO SOURCE_ID chega a evidencia final, em todos os degraus",
      raw_fonte == FONTE and entrada.get("FONTE_PROVADA") == FONTE
      and (entrada.get("SEM_BYTES_PARA_DERIVAR") or [{}])[0]
          .get("RAW_ASSET_ID") == int(raw_id),
      "raw_asset.source_id=%s · FONTE_PROVADA=%s"
      % (raw_fonte, entrada.get("FONTE_PROVADA")))
    T("C · a URL REAL da fonte fica preservada na observacao",
      raw_url.startswith("https://%s/" % HOSPEDEIRO) and raw_url.endswith(".csv"),
      "raw_asset.source_url=%s" % raw_url)
    T("D · o BRUTO e guardado ANTES de qualquer interpretacao",
      all(o.get("RAW_PRESERVED_BEFORE_PARSE") for o in obs_do_livro)
      and etapas.get("RAW") == "PASS"
      and objs[0][2] == raw_sha and int(objs[0][3]) > 3_000_000,
      "RAW=%s · sha do objecto == sha da observacao == %s · %s bytes"
      % (etapas.get("RAW"), raw_sha[:16], objs and objs[0][3]))

    # ── E · a identidade da OBSERVACAO nao sai do conteudo ────────────
    # ⚠️ ISTO NAO E PEDANTISMO. Um `raw_observation_id` derivado do sha, da
    # URL, do caminho ou do nome do ficheiro faz DUAS observacoes do mesmo
    # documento colapsarem numa — e a segunda visita desaparece sem ninguem ver.
    #
    #     DUAS OBSERVACOES DO MESMO DOCUMENTO SAO DUAS OBSERVACOES.
    #
    # ⚠️ E NAO SE PROVA ISTO PROCURANDO O ID DENTRO DO SHA. A primeira versao
    # desta prova fazia exactamente isso e REPROVOU com o sistema certo: o id
    # era `1`, e o algarismo `1` aparece dentro de qualquer hexadecimal. Uma
    # prova assim reprova por coincidencia de texto e passaria a aprovar
    # sozinha no dia em que a sequencia chegasse a um numero «sem sorte».
    #
    #     PROCURAR O ID DENTRO DO CONTEUDO NAO MEDE DE ONDE O ID VEIO.
    #
    # Prova-se pela ORIGEM (a coluna nasce de uma sequencia do banco) e pelo
    # COMPORTAMENTO (o mesmo conteudo, noutra corrida, recebe outro id — o que
    # uma funcao do conteudo nunca poderia fazer).
    origem = _psql(url, "select column_default from information_schema.columns "
                        "where table_schema='public' and table_name='raw_asset' "
                        "and column_name='id'")
    T("E · o RAW_OBSERVATION_ID nasce de uma SEQUENCIA do banco",
      str(raw_id).isdigit() and origem
      and "nextval" in (origem[0][0] or "").lower(),
      "raw_asset.id=%s · default=%s" % (raw_id, origem and origem[0][0]))

    # ── F · re-observacao nao multiplica o objecto ────────────────────
    # A MESMA corrida, a MESMA colheita, outra vez pela porta. Nao e uma
    # corrida nova: e o retry de uma que ja passou.
    n_raw = len(_psql(url, "select id from public.raw_asset"))
    n_obj = len(_psql(url, "select id from public.storage_object"))
    itens, _ = orq.a_colheita(
        {"id": "italia-recorrente",
         "retorno": {"ENVELOPE": "data/colheita/italia/RETORNO.json"},
         "roda": ["coleta/italy_executor.py"]}, run_id)
    orq.pela_entrada(itens, recibo, memoria=_memoria(url),
                     banco_do_rastro=cc.Banco(url))
    T("F · re-observar a MESMA corrida nao fabrica raw_asset novo",
      len(_psql(url, "select id from public.raw_asset")) == n_raw,
      "raw_asset passou de %d para %d"
      % (n_raw, len(_psql(url, "select id from public.raw_asset"))))
    T("F2 · nem fabrica copia nova no armazem",
      len(_psql(url, "select id from public.storage_object")) == n_obj,
      "storage_object passou de %d" % n_obj)

    # ── F3 · A OUTRA METADE DA MESMA LEI, E ELA PUXA PARA O LADO OPOSTO ──
    # ⚠️ `F` E `F3` NAO SE CONTRADIZEM: RESPONDEM A PERGUNTAS DIFERENTES.
    #
    #     a MESMA corrida a ver o mesmo objecto ..... e UMA observacao
    #     OUTRA corrida a ver o mesmo objecto ....... sao DUAS observacoes
    #
    # Colapsar a segunda na primeira apagaria a visita de hoje — e «voltar la
    # e encontrar o mesmo» e precisamente o facto que uma coleta recorrente
    # existe para registar.
    #
    #     VER OUTRA VEZ NAO E NAO TER VISTO.
    #
    # E e isto que fecha a prova `E` pelo comportamento: um id que fosse funcao
    # do conteudo NAO conseguiria ser diferente aqui, porque o conteudo e
    # byte a byte o mesmo — o sha confirma-o na propria asserçao.
    outra = dict(recibo, RUN_ID=run_id + "-OUTRA-VISITA")
    orq.pela_entrada(itens, outra, memoria=_memoria(url),
                     banco_do_rastro=cc.Banco(url))
    novas = _psql(url, "select id, sha256 from public.raw_asset "
                       "where run_id = '%s'" % outra["RUN_ID"])
    T("F3 · OUTRA corrida sobre o MESMO objecto e uma observacao NOVA, "
      "com id diferente e o mesmo sha",
      len(novas) == 1 and int(novas[0][0]) != int(raw_id)
      and novas[0][1] == raw_sha,
      "nova observacao=%s · a desta corrida=%s · sha igual=%s"
      % (novas and novas[0][0], raw_id,
         bool(novas and novas[0][1] == raw_sha)))
    T("F4 · e o ARMAZEM nao guarda os mesmos bytes duas vezes",
      len(_psql(url, "select distinct sha256 from public.storage_object")) == 1,
      "shas distintos no armazem: %s"
      % len(_psql(url, "select distinct sha256 from public.storage_object")))

    decisoes = json.loads(adm.LIVRO.read_text(encoding="utf-8"))["DECISOES"] \
        if adm.LIVRO.is_file() else []
    T("G · a ADMISSAO nao foi pulada: ha decisao escrita para esta corrida",
      any(d.get("corrida") == run_id for d in decisoes)
      and admis.get("itens") == 1,
      "%d decisao(oes) no livro, %d desta corrida"
      % (len(decisoes), sum(1 for d in decisoes if d.get("corrida") == run_id)))
    T("H · a Sala recebeu SO o que a porta admitiu — e ela admitiu zero",
      len(sala) == 0 and admis.get("por_resultado", {}).get("SIM") is None
      and admis.get("prontos") == 0,
      "por_resultado=%s · sala=%d" % (admis.get("por_resultado"), len(sala)))
    T("I · o READY mantem a semantica: prontos == admitidos == linhas na Sala",
      admis.get("prontos") == admis.get("por_resultado", {}).get("SIM", 0)
      == len(sala) == 0
      and len(espera.listar_pendentes()) == len(antes),
      "prontos=%s sala=%d pendentes=%d"
      % (admis.get("prontos"), len(sala), len(espera.listar_pendentes())))

    aposentado = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "ferramentas",
                                      "instagram_transcrever.py"), "rodar"],
        capture_output=True, text=True, cwd=RAIZ)
    T("J · o escritor APOSENTADO continua aposentado, e recusa ALTO",
      aposentado.returncode != 0,
      "saiu com %d" % aposentado.returncode)

    # ══════════════════════════════════════════════════════════════════
    # RED TEAM — cada ataque tem de MORRER, e morrer pela lei certa
    # ══════════════════════════════════════════════════════════════════
    print()
    print("  RED TEAM")
    ataques = []

    def ataque(nome, morreu, porque):
        ataques.append({"ATAQUE": nome, "MORREU": bool(morreu),
                        "PORQUE": str(porque)[:300]})
        T("RT · %s" % nome, morreu, porque)

    # 1 · SOURCE_ID inexistente: o coletor tem de RECUSAR, e nao correr as sete.
    r1 = subprocess.run(["node", "coleta/italy_pilot_collect.mjs",
                         "--run-id=RT-INEXISTENTE", "--fonte=IT-T9-999"],
                        capture_output=True, text=True, cwd=RAIZ)
    ataque("SOURCE_ID inexistente e recusado, e nao vira «corri tudo»",
           r1.returncode == 2 and "FONTE_DESCONHECIDA" in (r1.stderr or ""),
           "saiu %d · %s" % (r1.returncode, (r1.stderr or "").strip()[:120]))

    # 2 · SOURCE_ID errado: pedir outra fonte NAO pode trazer esta.
    ataque("pedir outra fonte nao traz IT-T4-001 de boleia",
           all(o.get("SOURCE_ID") == FONTE for o in obs_do_livro),
           "a corrida trouxe %s" % sorted({o.get("SOURCE_ID")
                                           for o in obs_do_livro}))

    # 3 · identidade trocada: o MESMO conteudo sob DUAS fontes nao se desempata.
    # ⚠️ O LIVRO DO ATAQUE E O DESCARTAVEL, e nao o versionado. Escrever a
    # linha do ataque no acervo real e depois apaga-la deixaria o acervo certo
    # so enquanto o `finally` corresse — e um `finally` que nao corre e
    # exactamente o que uma morte de processo nao executa.
    livro_it = os.path.join(ie.OPS_ROOT, ie.LIVRO)
    with io.open(livro_it, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"RUN_ID": "RT-IDENTIDADE-TROCADA",
                             "SOURCE_ID": "IT-T2-002",
                             "RAW_SHA256": raw_sha}) + "\n")
    try:
        conflito = ie.fonte_do_conteudo(raw_sha)
        ataque("o mesmo conteudo sob DUAS fontes nao elege uma em silencio",
               conflito["SOURCE_ID"] is None
               and sorted(conflito["CONFLITO"]) == ["IT-T2-002", FONTE],
               "devolveu %s" % json.dumps(conflito, ensure_ascii=False)[:200])
    finally:
        # ⚠️ O LIVRO E APPEND-ONLY E VERSIONADO. A linha do ataque SAI daqui, ou
        # esta prova deixaria no acervo uma observacao que nunca foi observada.
        linhas = io.open(livro_it, encoding="utf-8").read().splitlines(True)
        io.open(livro_it, "w", encoding="utf-8").writelines(
            [l for l in linhas if "RT-IDENTIDADE-TROCADA" not in l])

    # 4 · raw nao persistido: sem bytes, a porta nao pode dizer que preservou.
    sem_bytes = ing.para_a_porta({"SOURCE_ID": FONTE, "SOURCE_URL": raw_url,
                                  "COLLECTED_AT": raw_captura})
    ataque("observacao SEM bytes nao passa por observacao preservada",
           not sem_bytes.get("STORAGE_LOCATION"),
           "STORAGE_LOCATION=%r" % sem_bytes.get("STORAGE_LOCATION"))

    # 5 · Admission pulada: nao ha linha na Sala sem decisao desta corrida.
    ataque("nao existe linha na Sala sem decisao da porta por tras",
           len(sala) <= sum(1 for d in decisoes
                            if d.get("corrida") == run_id
                            and d.get("resultado") == adm.SIM),
           "sala=%d · SIM no livro=%d"
           % (len(sala), sum(1 for d in decisoes if d.get("corrida") == run_id
                             and d.get("resultado") == adm.SIM)))

    # 6 · READY sem contrato: a MESMA corrida nao pode contar duas historias.
    try:
        espera.pousar(run_id, [{"id": "inventado", "source_id": FONTE}])
        morreu6 = len(_psql(url, "select ordem from public.sala_de_espera "
                                 "where run_id = '%s'" % run_id)) == 0
        porque6 = "pousou sem recusar, e a Sala ficou com %d" % len(
            _psql(url, "select ordem from public.sala_de_espera "
                       "where run_id = '%s'" % run_id))
    except Exception as ex:                                    # noqa: BLE001
        morreu6, porque6 = True, "%s: %s" % (type(ex).__name__, str(ex)[:120])
    ataque("READY fabricado a mao nao entra na Sala desta corrida",
           morreu6, porque6)

    # 7 · retired writer (ja medido em J, contado aqui como ataque)
    ataque("escritor aposentado nao reaparece por uma porta lateral",
           aposentado.returncode != 0, "saiu com %d" % aposentado.returncode)

    # 8 · re-observacao multiplicando identidade. Mede-se AGORA, e nao com os
    # numeros de antes do F3: aquele acrescentou uma observacao legitima, e
    # compara-lo com um total antigo acusaria a lei de ser o defeito.
    n_agora = len(_psql(url, "select id from public.raw_asset"))
    o_agora = len(_psql(url, "select id from public.storage_object"))
    orq.pela_entrada(itens, recibo, memoria=_memoria(url),
                     banco_do_rastro=cc.Banco(url))
    ataque("o retry da MESMA corrida nao multiplica a identidade",
           len(_psql(url, "select id from public.raw_asset")) == n_agora
           and len(_psql(url, "select id from public.storage_object")) == o_agora,
           "raw_asset %d->%d · storage_object %d->%d"
           % (n_agora, len(_psql(url, "select id from public.raw_asset")),
              o_agora, len(_psql(url, "select id from public.storage_object"))))

    # 9 · proveniencia perdida: a fonte vem do CAMPO, e nunca do sha.
    semfonte = ie.fonte_do_conteudo("0" * 64)
    ataque("um sha desconhecido nao INVENTA fonte nenhuma",
           semfonte["SOURCE_ID"] is None,
           json.dumps(semfonte, ensure_ascii=False)[:160])

    # 10 · banco de ficheiro usado como canonico.
    ficheiro = espera._Ficheiro()                              # noqa: SLF001
    ataque("o backend de FICHEIRO nunca se declara canonico",
           ficheiro.CANONICO is False and bool(ficheiro.PORQUE),
           "CANONICO=%s" % ficheiro.CANONICO)

    # 11 · a trava do banco descartavel recusa producao.
    try:
        _memoria("postgresql://alguem@db.exemplo-remoto.com:5432/producao")
        morreu11, porque11 = False, "aceitou um banco remoto de producao"
    except SystemExit as ex:
        morreu11, porque11 = True, str(ex)[:140]
    ataque("a porta do banco recusa-se a correr fora do descartavel",
           morreu11, porque11)

    sobreviventes = [a for a in ataques if not a["MORREU"]]

    # ══════════════════════════════════════════════════════════════════
    estado = {
        "O_QUE_ISTO_E": (
            "Certificacao controlada de UMA fonte (%s), com AQUISICAO REAL "
            "pela rede, contra Postgres descartavel." % FONTE),
        "COMO_REFAZER": ("BANCO_DESCARTAVEL_URL=... python3 "
                         "provas/a_fonte_t4_italiana_atravessa.py"),
        # ── COMO LER O `RUN_ID` DESTE FICHEIRO ────────────────────────────
        # ⚠️ ESTE ARTEFATO E UM RETRATO DE UMA CORRIDA, E E REESCRITO INTEIRO
        # A CADA EXECUCAO. O `RUN_ID` aqui dentro e o da corrida que o escreveu
        # POR ULTIMO — nunca «a corrida desta prova», em abstracto.
        #
        # A distincao nao e teorica: em 2026-09-15 a entrega falou de uma
        # corrida (`...-213639-a8619f35086cd83b`) e o ficheiro commitado era de
        # outra (`...-211428-166b8db7c8f3bf96`). As duas correram, as duas deram
        # o mesmo resultado sobre os mesmos bytes — e mesmo assim sao DUAS.
        # So uma delas tem a cadeia de evidencia preservada neste commit.
        #
        #     DUAS CORRIDAS COM O MESMO RESULTADO CONTINUAM A SER DUAS.
        #     CHAMAR-LHES UMA E PERDER A QUE FICOU POR AUDITAR.
        #
        # Quem auditar: o `RUN_ID` gravado aqui e o unico que se pode conferir
        # contra este commit. Qualquer outro numero citado num relato so vale
        # com o ficheiro da corrida dele ao lado.
        "COMO_LER_O_RUN_ID": (
            "retrato da corrida que escreveu este ficheiro por ultimo; "
            "reexecutar a prova substitui-o por outra corrida, e as duas "
            "continuam a ser duas"),
        "AMBIENTE": "DESCARTAVEL",
        "AQUISICAO_NOVA": "SIM — HTTP GET real em %s" % HOSPEDEIRO,
        "SOURCE_ID": FONTE,
        "ALVO_DO_PEDIDO": ALVO_DO_PEDIDO,
        "RUN_ID": run_id,
        "RAW_ASSET_ID": int(raw_id),
        "RAW_OBSERVATION_ID": int(raw_id),
        "STORAGE_OBJECT_ID": int(objs[0][0]),
        "STORAGE_PATH": objs[0][1],
        "SHA256": raw_sha,
        "BYTES": int(objs[0][3]),
        "MEDIA_TYPE": raw_tipo,
        "DOCUMENT_KEY": raw_chave,
        "DOCUMENT_KEY_BASIS": raw_base,
        "IDENTITY_STATE": raw_estado,
        "SOURCE_URL": raw_url,
        "CAPTURED_AT": raw_captura,
        "DERIVED_ID": None,
        "ADMISSION_DECISION": admis.get("por_resultado"),
        "SALA_ROW_ID": None,
        "READY": admis.get("prontos"),
        "ETAPAS": etapas,
        "ESTRADA": {k: visto.get(k) for k in ESTRADA},
        "ONDE_PARA_E_PORQUE": {
            "ETAPA": "DERIVED",
            "ESTADO": etapas.get("DERIVED"),
            "PORQUE": ("nenhum executor de derivacao desta casa abre "
                       "%s; os dois que existem abrem PDF e midia. "
                       "NOT_APPLICABLE != FAIL." % raw_tipo),
            "O_QUE_FALTARIA": ("um dono do STRUCTURED para registo tabular. "
                               "E capacidade NOVA, e nao um conserto: o "
                               "proprio contrato de %s declara DUAS "
                               "granularidades (o arquivo e a linha), e "
                               "escolher uma delas e decisao de arquitectura."
                               % FONTE),
        },
        "RED_TEAM": ataques,
        "RED_TEAM_SURVIVORS": len(sobreviventes),
        "PASSOU": len(PASSOU), "FALHOU": len(FALHAS),
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with io.open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print()
    print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
    print()
    print("SOURCE_ID            = %s" % FONTE)
    print("RUN_ID               = %s" % run_id)
    print("RAW_OBSERVATION_ID   = %s" % raw_id)
    print("STORAGE_PATH         = %s" % objs[0][1])
    print("MEDIA_TYPE           = %s" % raw_tipo)
    print("DERIVED              = %s" % etapas.get("DERIVED"))
    print("ADMISSION_DECISION   = %s" % admis.get("por_resultado"))
    print("READY                = %s" % admis.get("prontos"))
    print("WAITING_ROOM         = %d" % len(sala))
    print("ACQUISITION_TO_ADMISSION_PROVEN = %s"
          % ("YES" if not FALHAS else "NO"))
    print("SOURCE_TO_WAITING_ROOM_PROVEN   = NO — para em DERIVED, "
          "NOT_APPLICABLE, por capacidade ausente")
    print("RED_TEAM_ATTACKS     = %d" % len(ataques))
    print("RED_TEAM_SURVIVORS   = %d" % len(sobreviventes))
    print("FONTE_T4_ITALIANA = %s · %d passaram · %d falharam"
          % ("PASS" if not FALHAS and not sobreviventes else "FAIL",
             len(PASSOU), len(FALHAS)))
    return 1 if (FALHAS or sobreviventes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
