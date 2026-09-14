#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SALA SOBREVIVE AO PROCESSO — e o ficheiro nunca sobreviveu.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5432/sala \\
        python3 provas/a_sala_sobrevive_ao_processo.py

O QUE ESTA PROVA EXISTE PARA FECHAR
-----------------------------------
O `C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1` parou a primeira coleta real
italiana num portão bloqueante, e o portão tinha razão:

    git log --all -- 'data/samples/PRONTO-PARA-INTELIGENCIA'   ->   vazio

O READY era escrito no workspace do runner e ninguém o guardava. Nenhum
`git add`, nenhum `upload-artifact`, nenhum dono em banco — e o `checkout`
seguinte limpa o que não está versionado.

    MODULE EXISTS != FILE WRITTEN ON RUNNER != PERSISTED AFTER RUN.
    PROVA DENTRO DO PROCESSO != DURABILIDADE OPERACIONAL.

O QUE ELA MEDE, CONTRA POSTGRES 16 DE VERDADE
----------------------------------------------
    A. durabilidade       o READY sobrevive ao fim do processo que o escreveu
    B. idempotência       mesma corrida, mesmo conteúdo -> REUSED, sem duplicar
    C. conflito           mesma corrida, outro conteúdo -> não escreve NADA
    D. crash              morto antes, durante e depois — nunca meio READY
    E. concorrência       dois escritores, dois leitores, duas corridas
    F. cardinalidade      0, 1 e N unidades; admitidos e recusados misturados
    G. linhagem           READY -> RAW -> STORAGE -> bytes, e -> RUN -> SOURCE
    H. a retirada         WAITING -> CONSUMED, sem apagar e sem julgar
    I. red team           26 ataques, e nenhum sobrevive

⚠️ O QUE ELA NÃO PROVA
-----------------------
Não prova produção: o banco é descartável e morre no fim. Não adquire nada —
nenhuma fonte, nenhuma rede de coleta, nenhum dólar. E não prova relevância:
`CONSUMED` diz «saiu da fila», e a Intelligence continua a ser outra missão.
"""
import hashlib
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in (RAIZ, os.path.join(RAIZ, "admissao"), os.path.join(RAIZ, "superficie")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas                                            # noqa: E402,F401

CASOS = []


def caso(nome, obtido, esperado):
    ok = obtido == esperado
    CASOS.append((ok, nome, obtido, esperado))
    return ok


# ═════════════════════════════════════════════════════════════════════════
# O BANCO DESCARTÁVEL — e a recusa de correr sobre qualquer outro
# ═════════════════════════════════════════════════════════════════════════

def _recusa_o_que_nao_e_descartavel(url):
    """⚠️ UMA PROVA QUE PODE APONTAR PARA PRODUÇÃO APONTA PARA PRODUÇÃO UM DIA.

    A mesma trava que `provas/preservar_coleta_no_postgres.py` já tinha: o
    endereço tem de ser visivelmente local. Não é zelo — é a diferença entre
    um teste e um incidente.
    """
    local = ("localhost" in url or "127.0.0.1" in url or "@postgres:" in url
             or url.startswith("postgresql:///"))
    if not local:
        print("RECUSADO: o endereco nao e visivelmente local. Esta prova ESCREVE.")
        raise SystemExit(2)


def _psql(url, sql, ler=True):
    cmd = ["psql", "-X", "-q", "-A", "-t", "-F", "\x1f", "-v", "ON_ERROR_STOP=1",
           url, "-c", sql]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return [l for l in r.stdout.splitlines() if l.strip()] if ler else None


def _preparar(url):
    """A cadeia canónica aplica as migrations. Nenhuma DDL escrita à mão aqui.

        MIGRATION SÓ PROVADA À MÃO É MIGRATION POR PROVAR.
    """
    r = subprocess.run(["bash", os.path.join(RAIZ, "motor", "cadeia_canonica.sh"),
                        "migrations", url], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:]); print(r.stderr[-2000:])
        raise SystemExit("a cadeia canonica nao aplicou")
    caso("a migration 031 aplica pela cadeia canonica",
         "MIGRATION_031=PASS" in r.stdout or "MIGRATION_031=SKIP" in r.stdout.replace(
             "MIGRATION_031=SKIP (ja no livro-razao) HASH=MATCH",
             "MIGRATION_031=SKIP"), True)
    _psql(url, "delete from public.sala_de_espera;", ler=False)


BYTES_REAIS = b"%PDF-1.4 bollettino di prova\n"
SHA_REAIS = hashlib.sha256(BYTES_REAIS).hexdigest()


def _semear(url):
    """Um RUN, um STORAGE OBJECT com bytes reais, e duas observações.

    A segunda observação nasce noutra corrida DE PROPÓSITO: a corrida que ADMITE
    não é forçosamente a que CAPTUROU, e há um ataque que mede isso.
    """
    _psql(url, """
      -- ⚠️ TODAS as corridas nascem aqui, e a razao e uma TRAVA REAL:
      -- `sala_de_espera.run_id` tem chave estrangeira para `collection_run`.
      -- Um READY de uma corrida que nunca existiu NAO ENTRA — e isso e
      -- `READY_WITHOUT_RUN = 0` garantido pelo esquema, e nao por disciplina.
      insert into public.collection_run (run_id, platform, started_at, rule_version)
      select r, 'prova', now(), 'v1' from unnest(array[
             'RUN-CAPTURA','RUN-ADMISSAO','RUN-OUTRA','RUN-EFEMERA',
             'RUN-CRASH-ANTES','RUN-CRASH-DEPOIS','RUN-METADE',
             'RUN-CONC-IGUAL','RUN-CONC-DIF','RUN-LEITURA','RUN-ZERO',
             'RUN-11','RUN-13','RUN-SEM-DSN','RUN-NUL']) as r
      on conflict (run_id) do nothing;
      insert into public.storage_object (storage_path, media_type, bytes, sha256)
      values ('prova/bollettino.pdf','application/pdf', %d, '%s')
      on conflict (storage_path) do nothing;
      insert into public.raw_asset
        (run_id, storage_path, media_type, bytes, sha256, captured_at,
         storage_object_id, identity_state, source_id)
      select 'RUN-CAPTURA','prova/bollettino.pdf','application/pdf', %d, '%s',
             now(), id, 'FORWARD_IDENTITY_UNPROVEN', 'IT-T7-001'
        from public.storage_object where storage_path = 'prova/bollettino.pdf'
         and not exists (select 1 from public.raw_asset
                          where storage_path = 'prova/bollettino.pdf');
    """ % (len(BYTES_REAIS), SHA_REAIS, len(BYTES_REAIS), SHA_REAIS), ler=False)
    return int(_psql(url, "select id from public.raw_asset "
                          "where storage_path='prova/bollettino.pdf'")[0])


def _ready(observacao, item_id="doc-1", texto="Ensaio de campo publicado com DOI",
           corrida="RUN-ADMISSAO"):
    """Um READY construído pelo DONO do contrato, nunca escrito à mão.

        UMA PROVA QUE FABRICA O CONTRATO PROVA A FABRICAÇÃO.
    """
    import admissao as adm
    item = {"id": item_id, "texto": texto, "source_id": "IT-T7-001",
            "fact_time": "2026-05-02", "raw_asset_id": observacao,
            "captured_at": "2026-05-03T00:00:00Z"}
    d = adm.decidir(item, "T5", corrida=corrida)
    if d.resultado != adm.SIM:
        raise SystemExit("a fixture deixou de ser admissivel: %s" % d.resultado)
    return adm.pronto_para_inteligencia(item, d)


# ═════════════════════════════════════════════════════════════════════════
# OS PROCESSOS FILHOS — a durabilidade só se mede com o processo morto
# ═════════════════════════════════════════════════════════════════════════

_FILHO = r"""
import os, sys
sys.path.insert(0, %(raiz)r); sys.path.insert(0, os.path.join(%(raiz)r, 'admissao'))
import _gavetas
import sala_de_espera as espera
import json
unidades = json.loads(%(unidades)r)
try:
    r = espera.pousar(%(run)r, unidades)
    print('OK:' + str(r['ESTADO']))
except espera.ConflitoDeCorrida:
    print('CONFLITO')
except Exception as e:
    print('ERRO:' + type(e).__name__)
%(depois)s
"""


def _filho(url, run, unidades, depois="", matar_em=None):
    codigo = _FILHO % {"raiz": RAIZ, "run": run,
                       "unidades": json.dumps(unidades, ensure_ascii=False),
                       "depois": depois}
    amb = dict(os.environ, SINTONIA_SALA_BACKEND="POSTGRES", SINTONIA_SALA_DSN=url)
    p = subprocess.Popen([sys.executable, "-c", codigo], env=amb,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if matar_em is not None:
        try:
            p.wait(timeout=matar_em)
        except subprocess.TimeoutExpired:
            p.kill()
    saida, _ = p.communicate()
    return p.returncode, (saida or "").strip()


def _uma_mao(url, run, unidades, fila):
    os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    os.environ["SINTONIA_SALA_DSN"] = url
    sys.path.insert(0, RAIZ); sys.path.insert(0, os.path.join(RAIZ, "admissao"))
    import sala_de_espera as espera
    try:
        fila.put(espera.pousar(run, unidades)["ESTADO"])
    except espera.ConflitoDeCorrida:
        fila.put("CONFLITO")
    except Exception as e:                                   # noqa: BLE001
        fila.put("ERRO:%s" % type(e).__name__)


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not url:
        print("BANCO_DESCARTAVEL_URL nao definido · NOT_RUN — esta prova so "
              "corre contra Postgres descartavel. NOT_RUN NAO E PASS.")
        return 0
    _recusa_o_que_nao_e_descartavel(url)
    _preparar(url)
    observacao = _semear(url)

    os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    os.environ["SINTONIA_SALA_DSN"] = url
    import sala_de_espera as espera

    # ⚠️ A MORADA DO REPO NAO E BANCADA DE PROVA — e isto foi MEDIDO, nao
    # previsto. A bateria de mutacao corre numa copia da arvore com `data/`
    # ligado por symlink a esta; o mutante que faz a sala cair para ficheiro
    # escreveu, por esse symlink, um `RUN-SEM-DSN.json` dentro do repositorio
    # de verdade — e ele chegou a aparecer no `git add`.
    #
    #     UMA PROVA QUE SUJA A ARVORE QUE MEDE DEIXOU DE SO MEDIR.
    #
    # A partir daqui o backend de ficheiro escreve SEMPRE numa bancada
    # descartavel. `MORADA_DO_REPO` fica guardada para o ataque 21, que e
    # justamente o que exige que ela continue vazia.
    MORADA_DO_REPO = espera.MORADA
    bancada = os.path.join(tempfile.mkdtemp(prefix="sala-prova-"), "espera")
    espera.MORADA = bancada

    pronta = _ready(observacao)
    caso("o READY tem os 12 campos da COL-LAW-043", len(pronta), 12)
    caso("e o dono do contrato pos la a observacao",
         pronta["RAW_OBSERVATION_ID"], observacao)

    # ── A · DURABILIDADE ───────────────────────────────────────────────
    # O processo que escreve MORRE. Só depois é que se pergunta.
    codigo, saida = _filho(url, "RUN-ADMISSAO", [pronta])
    caso("o processo que pousou terminou", codigo, 0)
    caso("e disse que pousou", saida, "OK:PASSED")
    lido = espera.ler("RUN-ADMISSAO")
    caso("READY_PERSISTS_AFTER_PROCESS_EXIT", lido is not None, True)
    caso("READY_PERSISTS_AFTER_NEW_PROCESS", lido["ITENS"][0], pronta)
    # A reconexão é um processo NOVO a abrir uma ligação NOVA: o `psql` de cada
    # chamada já é isso, e por isso não se encena um restart de servidor.
    caso("READY_PERSISTS_AFTER_BACKEND_RECONNECT",
         espera.ler("RUN-ADMISSAO")["ITENS"][0], pronta)

    # ── O FICHEIRO NÃO SOBREVIVE, E É POR ISSO QUE O CANÓNICO É OUTRO ──
    # Ataques 1, 2 e 20: workspace apagado, checkout novo, caminho local
    # tratado como persistência.
    sala_falsa = os.path.join(os.path.dirname(bancada), "sala-efemera")
    shutil.rmtree(sala_falsa, ignore_errors=True)
    try:
        espera.MORADA = sala_falsa
        amb = dict(os.environ); amb.pop("SINTONIA_SALA_BACKEND", None)
        os.environ["SINTONIA_SALA_BACKEND"] = "FICHEIRO"
        r = espera.pousar("RUN-EFEMERA", [pronta])
        caso("o backend de ficheiro declara-se NAO canonico", r["CANONICO"], False)
        existia = os.path.isfile(os.path.join(sala_falsa, "RUN-EFEMERA.json"))
        shutil.rmtree(sala_falsa, ignore_errors=True)      # = git clean -ffdx
        caso("ataque 1/2 · o ficheiro existia antes do checkout", existia, True)
        caso("ataque 1/2 · e desapareceu com o workspace",
             espera.ler("RUN-EFEMERA"), None)
        try:
            espera.exigir_canonica(); passou = True
        except espera.SalaIndisponivel:
            passou = False
        caso("ataque 20 · caminho local NAO passa por persistencia", passou, False)
        try:
            espera.listar_pendentes(); soube = True
        except espera.SalaIndisponivel:
            soube = False
        caso("o ficheiro admite que nao sabe dizer «pendente»", soube, False)
    finally:
        espera.MORADA = bancada
        os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    shutil.rmtree(sala_falsa, ignore_errors=True)

    # ── ATAQUE 21 · GIT NÃO É BANCO ────────────────────────────────────
    # O backend canónico não pode ter escrito UM ficheiro na morada do Git.
    n_ficheiros = 0
    if os.path.isdir(MORADA_DO_REPO):
        n_ficheiros = len(os.listdir(MORADA_DO_REPO))
    caso("ataque 21 · a morada do repo continua vazia (GIT NAO E BANCO)",
         n_ficheiros, 0)

    # ── B · IDEMPOTÊNCIA ───────────────────────────────────────────────
    caso("SAME_RUN_SAME_READY = REUSED",
         espera.pousar("RUN-ADMISSAO", [pronta])["ESTADO"], "REUSED")
    caso("ataque 5/19 · o retry nao duplicou",
         len(espera.ler("RUN-ADMISSAO")["ITENS"]), 1)
    caso("ataque 8 · e o banco tem UMA linha",
         int(_psql(url, "select count(*) from public.sala_de_espera "
                        "where run_id='RUN-ADMISSAO'")[0]), 1)

    # ── C · CONFLITO ───────────────────────────────────────────────────
    outra = dict(pronta, TEXTO="Outro ensaio, com DOI")
    try:
        espera.pousar("RUN-ADMISSAO", [outra]); levantou = False
    except espera.ConflitoDeCorrida:
        levantou = True
    caso("SAME_RUN_DIFFERENT_READY = CONFLICT", levantou, True)
    caso("ataque 7 · e o conflito NAO escreveu nada",
         espera.ler("RUN-ADMISSAO")["ITENS"], [pronta])

    # ── D · CRASH ──────────────────────────────────────────────────────
    # 1. morto ANTES de escrever — nada aparece.
    codigo, _ = _filho(url, "RUN-CRASH-ANTES", [dict(pronta, ITEM_ID="crash-1")],
                       depois="", matar_em=0.001)
    caso("ataque 3 · morto antes: PARTIAL_INVISIBLE",
         espera.ler("RUN-CRASH-ANTES") in (None,), True)
    # 2. morto DEPOIS de escrever e ANTES de devolver o recibo — a linha fica,
    #    e o retry reencontra-a como REUSED em vez de duplicar.
    u = dict(pronta, ITEM_ID="crash-2")
    _filho(url, "RUN-CRASH-DEPOIS", [u], depois="os._exit(9)")
    caso("ataque 4 · morto depois do commit: a linha ficou",
         espera.ler("RUN-CRASH-DEPOIS") is not None, True)
    caso("ataque 4 · e o retry reencontra-a",
         espera.pousar("RUN-CRASH-DEPOIS", [u])["ESTADO"], "REUSED")
    caso("ataque 19 · sem duplicar",
         int(_psql(url, "select count(*) from public.sala_de_espera "
                        "where run_id='RUN-CRASH-DEPOIS'")[0]), 1)
    # 3. a transação a meio: metade das unidades não pode ficar. Uma lista com
    #    uma unidade boa e outra a apontar para observação inexistente.
    ma = dict(pronta, ITEM_ID="metade-2", RAW_OBSERVATION_ID=999999)
    try:
        espera.pousar("RUN-METADE", [dict(pronta, ITEM_ID="metade-1"), ma])
        rebentou = False
    except Exception:                                         # noqa: BLE001
        rebentou = True
    caso("ataque 9 · READY sem RAW existente NAO entra", rebentou, True)
    # E a trava irmã: READY de uma corrida que nunca existiu também não entra.
    try:
        espera.pousar("RUN-QUE-NUNCA-EXISTIU", [dict(pronta, ITEM_ID="orfao")])
        orfao = True
    except espera.SalaIndisponivel:
        orfao = False
    caso("READY_WITHOUT_RUN = 0, pela chave estrangeira e nao por disciplina",
         orfao, False)
    caso("crash a meio da transacao: PARTIAL_INVISIBLE",
         int(_psql(url, "select count(*) from public.sala_de_espera "
                        "where run_id='RUN-METADE'")[0]), 0)

    # ── E · CONCORRÊNCIA ───────────────────────────────────────────────
    u_c = dict(pronta, ITEM_ID="conc")
    fila = multiprocessing.Queue()
    ps = [multiprocessing.Process(target=_uma_mao,
                                  args=(url, "RUN-CONC-IGUAL", [u_c], fila))
          for _ in range(2)]
    for p in ps: p.start()
    for p in ps: p.join(60)
    r2 = sorted(fila.get() for _ in range(2))
    caso("E-A · dois writers, mesmo conteudo: um pousa, outro reaproveita",
         r2, ["PASSED", "REUSED"])
    caso("E-A · DUPLICATES = 0",
         int(_psql(url, "select count(*) from public.sala_de_espera "
                        "where run_id='RUN-CONC-IGUAL'")[0]), 1)

    fila2 = multiprocessing.Queue()
    ps = [multiprocessing.Process(
              target=_uma_mao,
              args=(url, "RUN-CONC-DIF",
                    [dict(pronta, ITEM_ID="c-%d" % i, TEXTO="DOI numero %d" % i)],
                    fila2))
          for i in range(2)]
    for p in ps: p.start()
    for p in ps: p.join(60)
    r3 = sorted(fila2.get() for _ in range(2))
    caso("E-B · dois writers, conteudo diferente: um pousa, o outro e RECUSADO",
         r3, ["CONFLITO", "PASSED"])
    caso("E-B · SILENT_CONFLICTS = 0 (uma linha so)",
         int(_psql(url, "select count(*) from public.sala_de_espera "
                        "where run_id='RUN-CONC-DIF'")[0]), 1)

    fila3 = multiprocessing.Queue()
    ps = [multiprocessing.Process(
              target=_uma_mao,
              args=(url, "RUN-CAPTURA" if i == 0 else "RUN-OUTRA",
                    [dict(pronta, ITEM_ID="par-%d" % i)], fila3))
          for i in range(2)]
    for p in ps: p.start()
    for p in ps: p.join(60)
    r4 = sorted(fila3.get() for _ in range(2))
    caso("E-C · duas corridas ao mesmo tempo: as duas pousam",
         r4, ["PASSED", "PASSED"])
    caso("ataque 18 · CROSS_RUN_CONTAMINATION = 0",
         [espera.ler("RUN-CAPTURA")["ITENS"][0]["ITEM_ID"],
          espera.ler("RUN-OUTRA")["ITENS"][0]["ITEM_ID"]], ["par-0", "par-1"])
    # E-D · leitor durante escrita: nada de leitura suja. O leitor corre
    # enquanto dois escritores disputam a MESMA corrida.
    fila4 = multiprocessing.Queue()
    escritores = [multiprocessing.Process(
                      target=_uma_mao,
                      args=(url, "RUN-LEITURA", [dict(pronta, ITEM_ID="ler")], fila4))
                  for _ in range(2)]
    for p in escritores: p.start()
    vistos = set()
    for _ in range(40):
        v = espera.ler("RUN-LEITURA")
        vistos.add(0 if v is None else len(v["ITENS"]))
    for p in escritores: p.join(60)
    for _ in range(2): fila4.get()
    caso("E-D · DIRTY_READS = 0 (so 0 ou 1 unidade, nunca meio estado)",
         sorted(vistos) in ([0], [1], [0, 1]), True)
    caso("ataque 17 · stale read: a leitura seguinte ve o estado escrito",
         len(espera.ler("RUN-LEITURA")["ITENS"]), 1)

    # ── F · CARDINALIDADE ──────────────────────────────────────────────
    r0 = espera.pousar("RUN-ZERO", [])
    caso("ataque 15 · 0 admitidos nao cria READY falso", r0["ESTADO"], None)
    caso("ataque 15 · e nao cria linha nenhuma",
         int(_psql(url, "select count(*) from public.sala_de_espera "
                        "where run_id='RUN-ZERO'")[0]), 0)
    caso("0 admitidos: a corrida continua a existir no dono do RUN",
         int(_psql(url, "select count(*) from public.collection_run "
                        "where run_id='RUN-CAPTURA'")[0]), 1)
    ns = [dict(pronta, ITEM_ID="n-%d" % i, TEXTO="Ensaio %d com DOI" % i)
          for i in range(5)]
    _psql(url, "insert into public.collection_run (run_id, platform, started_at, "
               "rule_version) values ('RUN-N','prova', now(),'v1') "
               "on conflict do nothing;", ler=False)
    caso("N unidades pousam juntas",
         espera.pousar("RUN-N", ns)["UNIDADES"], 5)
    caso("e leem-se pela ordem em que pousaram",
         [x["ITEM_ID"] for x in espera.ler("RUN-N")["ITENS"]],
         ["n-%d" % i for i in range(5)])

    # Admitidos e recusados misturados: só o que a porta admitiu chega à sala.
    import admissao as adm
    _psql(url, "insert into public.collection_run (run_id, platform, started_at, "
               "rule_version) values ('RUN-MISTO','prova', now(),'v1') "
               "on conflict do nothing;", ler=False)
    brutos = [{"id": "bom", "texto": "Ensaio de campo publicado com DOI",
               "source_id": "IT-T7-001", "fact_time": "2026-05-02",
               "raw_asset_id": observacao},
              {"id": "mau", "texto": "receita de bolo", "source_id": "IT-T7-001",
               "fact_time": "2026-05-02", "raw_asset_id": observacao}]
    ds = [adm.decidir(b, "T5", corrida="RUN-MISTO") for b in brutos]
    aceites = [adm.pronto_para_inteligencia(b, d)
               for b, d in zip(brutos, ds) if d.resultado == adm.SIM]
    espera.pousar("RUN-MISTO", aceites)
    pendentes_misto = [p for p in espera.listar_pendentes()
                       if p["RUN_ID"] == "RUN-MISTO"]
    caso("ataque 14 · o item recusado NAO aparece como pendente",
         [p["ITEM_ID"] for p in pendentes_misto], ["bom"])

    # ── G · LINHAGEM ───────────────────────────────────────────────────
    linha = _psql(url, """
      select s.run_id, s.raw_observation_id, r.run_id, o.storage_path, o.sha256,
             r.source_id
        from public.sala_de_espera s
        join public.raw_asset r     on r.id = s.raw_observation_id
        join public.storage_object o on o.id = r.storage_object_id
       where s.run_id = 'RUN-ADMISSAO'
    """)[0].split("\x1f")
    caso("READY -> RAW", int(linha[1]), observacao)
    caso("RAW -> STORAGE -> bytes (sha confere)", linha[4], SHA_REAIS)
    caso("READY -> RUN", linha[0], "RUN-ADMISSAO")
    caso("READY -> SOURCE (declarado, nunca derivado da URL)",
         linha[5], "IT-T7-001")
    caso("ataque 10 · a observacao e de OUTRA corrida, e isso e legitimo e visivel",
         (linha[0], linha[2]), ("RUN-ADMISSAO", "RUN-CAPTURA"))
    caso("ataque 11 · nenhum READY aponta para storage inexistente",
         int(_psql(url, """
             select count(*) from public.sala_de_espera s
               join public.raw_asset r on r.id = s.raw_observation_id
              where r.storage_object_id is null""")[0]), 0)

    # ── H · A RETIRADA ─────────────────────────────────────────────────
    antes = [p for p in espera.listar_pendentes() if p["RUN_ID"] == "RUN-ADMISSAO"]
    caso("WAITING: o item esta na fila", len(antes), 1)
    caso("retirar devolve PASSED",
         espera.retirar("RUN-ADMISSAO", "doc-1", por="prova")["ESTADO"], "PASSED")
    depois = [p for p in espera.listar_pendentes() if p["RUN_ID"] == "RUN-ADMISSAO"]
    caso("WAITING -> NOT_WAITING: saiu de LIST_PENDING", len(depois), 0)
    caso("mas continua auditavel na sala",
         len(espera.ler("RUN-ADMISSAO")["ITENS"]), 1)
    carimbo = _psql(url, "select estado_da_fila, consumido_por, "
                         "consumido_em is not null from public.sala_de_espera "
                         "where run_id='RUN-ADMISSAO'")[0].split("\x1f")
    caso("e o carimbo diz quem e quando", carimbo, ["CONSUMED", "prova", "t"])
    caso("retirar outra vez e idempotente",
         espera.retirar("RUN-ADMISSAO", "doc-1", por="prova")["ESTADO"], "REUSED")
    caso("a sala NAO guarda veredito de relevancia",
         [c for c in _psql(url, "select column_name from information_schema.columns "
                                "where table_name='sala_de_espera'")
          if c.upper() in ("KEEP", "TEMP", "DISCARD", "RELEVANCIA", "VEREDITO")], [])

    # ── I · O RESTO DO RED TEAM ────────────────────────────────────────
    # 12 e 13 · o contrato READY tem 12 campos, e 11 não entra.
    onze = dict(pronta); onze.pop("CAPTURED_AT")
    try:
        espera.pousar("RUN-11", [onze]); entrou = True
    except ValueError:
        entrou = False
    caso("ataque 12 · READY com 11 campos NAO entra", entrou, False)
    treze = dict(pronta, EXTRA="a mais")
    try:
        espera.pousar("RUN-13", [treze]); entrou13 = True
    except ValueError:
        entrou13 = False
    caso("ataque 13 · READY com campo a mais tambem NAO entra", entrou13, False)

    # 16 · backend indisponível — e NÃO cai para ficheiro.
    guardado = os.environ.pop("SINTONIA_SALA_DSN")
    try:
        try:
            espera.pousar("RUN-SEM-DSN", [pronta]); caiu = True
        except espera.SalaIndisponivel:
            caiu = False
        caso("ataque 16 · sem DSN a sala falha ALTO", caiu, False)
        caso("ataque 16 · e NAO caiu para ficheiro",
             os.path.isfile(os.path.join(bancada, "RUN-SEM-DSN.json"))
             or os.path.isfile(os.path.join(MORADA_DO_REPO, "RUN-SEM-DSN.json")),
             False)
    finally:
        os.environ["SINTONIA_SALA_DSN"] = guardado

    # 22 · artefato temporário como fonte de verdade — o portão da sala recusa
    #      tudo o que não seja o backend canónico, e sai com código para que o
    #      passo seguinte do workflow não arranque.
    portao = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "admissao", "sala_de_espera.py"),
         "--portao"],
        capture_output=True, text=True,
        env=dict(os.environ, SINTONIA_SALA_BACKEND="POSTGRES",
                 SINTONIA_SALA_DSN=url))
    caso("ataque 22 · o portao da sala exige o backend CANONICO, nao artefato",
         (portao.returncode, "SALA_DE_ESPERA=PASS" in portao.stdout), (0, True))
    fechado = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "admissao", "sala_de_espera.py"),
         "--portao"],
        capture_output=True, text=True,
        env={k: v for k, v in os.environ.items()
             if k not in ("SINTONIA_SALA_BACKEND", "SINTONIA_SALA_DSN")})
    caso("ataque 22 · e SAI COM CODIGO quando a sala nao e canonica",
         (fechado.returncode, "SALA_DE_ESPERA=BLOCKED" in fechado.stdout),
         (1, True))

    # 23 · injeção de SQL pelo RUN_ID e pelo TEXTO.
    _psql(url, "insert into public.collection_run (run_id, platform, started_at, "
               "rule_version) values ('RUN-'';drop table public.sala_de_espera;--',"
               "'prova', now(),'v1') on conflict do nothing;", ler=False)
    mau = dict(pronta, ITEM_ID="inj", TEXTO="o' || (select 1) || '; drop table x;--")
    espera.pousar("RUN-';drop table public.sala_de_espera;--", [mau])
    caso("ataque 23 · a tabela sobreviveu a injecao pelo RUN_ID",
         int(_psql(url, "select count(*) from information_schema.tables "
                        "where table_name='sala_de_espera'")[0]), 1)
    caso("ataque 23 · e o texto voltou LETRA POR LETRA",
         espera.ler("RUN-';drop table public.sala_de_espera;--")["ITENS"][0]["TEXTO"],
         mau["TEXTO"])

    # 24 · NUL no texto.
    try:
        espera.pousar("RUN-NUL", [dict(pronta, ITEM_ID="nul", TEXTO="a\x00b")])
        passou_nul = True
    except ValueError:
        passou_nul = False
    caso("ataque 24 · NUL no texto e recusado antes do banco", passou_nul, False)

    # 25 e 26 · a retirada exige autor, e recusa endereço ambíguo.
    try:
        espera.retirar("RUN-N", "n-0", por="  "); sem_autor = True
    except ValueError:
        sem_autor = False
    caso("ataque 25 · retirar sem autor nao e retirar", sem_autor, False)
    _psql(url, "insert into public.collection_run (run_id, platform, started_at, "
               "rule_version) values ('RUN-AMBIGUO','prova', now(),'v1') "
               "on conflict do nothing;", ler=False)
    # `admissao.decidir()` devolve "?" quando o item nao traz id nem url.
    sem_id = [{"texto": "Ensaio um com DOI", "source_id": "IT-T7-001",
               "fact_time": "2026-05-02", "raw_asset_id": observacao},
              {"texto": "Ensaio dois com DOI", "source_id": "IT-T7-001",
               "fact_time": "2026-05-02", "raw_asset_id": observacao}]
    dois = [adm.pronto_para_inteligencia(b, adm.decidir(b, "T5", corrida="RUN-AMBIGUO"))
            for b in sem_id]
    caso("dois itens sem id trazem o MESMO ITEM_ID",
         [x["ITEM_ID"] for x in dois], ["?", "?"])
    espera.pousar("RUN-AMBIGUO", dois)
    caso("e os dois pousaram, sem nenhum ser deitado fora",
         len(espera.ler("RUN-AMBIGUO")["ITENS"]), 2)
    try:
        espera.retirar("RUN-AMBIGUO", "?", por="prova"); retirou = True
    except espera.ItemAmbiguo:
        retirou = False
    caso("ataque 26 · retirar por ITEM_ID ambiguo e RECUSADO", retirou, False)
    try:
        espera.retirar("RUN-N", "nao-existe", por="prova"); achou = True
    except espera.ItemDesconhecido:
        achou = False
    caso("retirar o que a sala nao tem e recusado", achou, False)

    # ── O VEREDITO ─────────────────────────────────────────────────────
    reprovados = [c for c in CASOS if not c[0]]
    print()
    for ok, nome, obtido, esperado in CASOS:
        print("  %-5s %s" % ("ok" if ok else "FALHA", nome))
        if not ok:
            print("          esperado: %r" % (esperado,))
            print("          obtido:   %r" % (obtido,))
    print()
    print("=" * 66)
    print("CASOS=%d · PASS=%d · FAIL=%d"
          % (len(CASOS), len(CASOS) - len(reprovados), len(reprovados)))
    ataques = len([c for c in CASOS if "ataque" in c[1]])
    print("RED_TEAM_ATTACKS=%d · RED_TEAM_SURVIVORS=%d"
          % (ataques, len([c for c in reprovados if "ataque" in c[1]])))
    print("SALA_SOBREVIVE_AO_PROCESSO=%s" % ("PASS" if not reprovados else "FAIL"))
    print("=" * 66)
    return 1 if reprovados else 0


if __name__ == "__main__":
    raise SystemExit(main())
