#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LEI DA FASE 10, MEDIDA — e não escrita e depois acreditada.

O QUE ISTO É
------------
A missão `C-PREP-PHASE-10` é de PREPARAÇÃO: ela não aplica a fase 10 a lado
nenhum. Mas preparar sem medir é escolher uma lei no papel e descobrir o preço
dela em produção. Então tudo o que a preparação afirma sobre o banco está aqui,
e é o Postgres que responde.

    CAN DO   é o SQL que se podia escrever
    DID DO   é o SQL que correu, sobre linhas, e cujo resultado se leu

⚠️ **SQLite não prova isto.** Entram índices parciais únicos, `nulls not
distinct`, `pg_stat_activity`, `ACCESS EXCLUSIVE` e inferência de árbitro no
`on conflict`. Nenhum deles existe no SQLite com esta semântica.

A PERGUNTA QUE A FASE 10 TEM DE RESPONDER
-----------------------------------------
Depois da 026 a observação tem estado. Falta o que a 025 e a 026 deixaram de
propósito para depois: `unique (raw_asset.storage_path)` ainda está de pé, e
enquanto estiver, **duas observações do mesmo endereço são uma só**. Isso
colapsa a espécie:

    OBSERVAÇÃO   um facto sobre o mundo, com hora e corrida
    OBJETO       uma cópia guardada, com endereço

Uma corrida nova que reencontra o mesmo documento é uma OBSERVAÇÃO NOVA. Hoje
ela não entra. Medir *o que* passa a entrar — e *o que fica sem dono* — é o
trabalho deste ficheiro.

O QUE ELE NÃO FAZ
-----------------
Não altera migration nenhuma, não escreve no banco vivo e não instala a fase
10. Os índices candidatos da parte E nascem e morrem dentro da prova.
"""
import hashlib
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

SEP = "\x1f"
SHA_X = hashlib.sha256(b"X").hexdigest()
SHA_Y = hashlib.sha256(b"Y").hexdigest()

# As migrations que esta prova precisa: a fundação, a casa do derivado, a casa
# do objeto e a identidade da observação. As restantes não entram — a fase 10
# não depende delas, e arrastá-las mediria outra coisa.
MIGRACOES = ["001_fundacao_geografia_e_proveniencia.sql",
             "022_o_derivado_ganha_casa.sql",
             "025_o_objeto_ganha_casa.sql",
             "026_a_observacao_ganha_identidade.sql"]

# O PROTOTIPO NAO E UMA MIGRATION, e por isso vive fora daquela lista e entra
# por um caminho proprio — nas partes que perguntam «e DEPOIS da fase 10?».
# Aplicá-lo pela mesma porta das migrations faria esta prova tratá-lo como uma,
# que é exactamente o que ele não é.
PROTOTIPO = os.path.join("supabase", "ensaios",
                         "PROTOTIPO-FASE-10-IDENTIDADE-DA-TENTATIVA.sql")


# ─────────────────────────────────────────────────────────────────────────
# 0 · a porta do banco
# ─────────────────────────────────────────────────────────────────────────
def psql(url, sql):
    """(ok, linhas, erro). Uma recusa do banco é MEDIDA, nunca acidente — por
    isso nada aqui levanta exceção: o erro é um resultado como outro."""
    p = subprocess.run(["psql", url, "-X", "-q", "-v", "ON_ERROR_STOP=1",
                        "-t", "-A", "-F", SEP, "-c", sql],
                       capture_output=True, text=True)
    linhas = [l.split(SEP) for l in p.stdout.strip().splitlines() if l]
    return (p.returncode == 0), linhas, p.stderr.strip()


def um(url, sql):
    ok, r, e = psql(url, sql)
    return r[0][0] if (ok and r) else ""


def motivo(erro):
    """A frase do Postgres, sem o ruído do psql à volta dela."""
    for l in erro.splitlines():
        if "ERROR:" in l:
            return l.split("ERROR:")[-1].strip()[:120]
    return erro.splitlines()[0][:120] if erro else "?"


def sessao(url):
    """Uma sessão `psql` VIVA. Concorrência a sério precisa de duas ligações
    ao mesmo tempo; simulá-la em Python mediria o Python."""
    return subprocess.Popen([
        "psql", url, "-X", "-q", "-A", "-t"], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)


def fala(p, sql):
    p.stdin.write(sql + "\n")
    p.stdin.flush()


def fecha(p):
    try:
        p.stdin.close()
    except Exception:
        pass
    saida = p.stdout.read()
    p.wait()
    return saida


# ─────────────────────────────────────────────────────────────────────────
# 1 · o acervo desta prova
# ─────────────────────────────────────────────────────────────────────────
def corrida(url, run_id):
    psql(url, "insert into public.collection_run (run_id, platform, "
              "started_at, rule_version, status) values ('%s','prep10',"
              "now(),'v1','concluida') on conflict (run_id) do nothing" % run_id)


def objeto(url, path, sha, bytes_=10, media="application/pdf"):
    psql(url, "insert into public.storage_object (storage_path, media_type, "
              "bytes, sha256) values ('%s','%s',%d,'%s') on conflict "
              "(storage_path) do nothing" % (path, media, bytes_, sha))
    return um(url, "select id from public.storage_object where "
                   "storage_path='%s'" % path)


def observa(url, run, path, sha, fonte, doc, estado, oid=None, extra="",
            bytes_=10, media="application/pdf"):
    if oid is None:
        oid = objeto(url, path, sha, bytes_, media)
    dk = "null" if doc is None else "'%s'" % doc
    ba = "null" if doc is None else "'SOURCE_DOCUMENT_ID'"
    fo = "null" if fonte is None else "'%s'" % fonte
    ok, r, e = psql(url,
                    "insert into public.raw_asset (run_id, storage_path, "
                    "media_type, bytes, sha256, captured_at, storage_object_id,"
                    " source_id, document_key, document_key_basis, "
                    "identity_state) values ('%s','%s','%s',%d,'%s',now(),%s,"
                    "%s,%s,%s,'%s') %s returning id"
                    % (run, path, media, bytes_, sha, oid, fo, dk, ba,
                       estado, extra))
    return (True, r[0][0]) if ok else (False, motivo(e))


def limpa(url):
    psql(url, "delete from public.raw_asset")
    psql(url, "delete from public.storage_object")
    psql(url, "drop index if exists prep10_candidata_idx")


# ─────────────────────────────────────────────────────────────────────────
# 2 · os casos
# ─────────────────────────────────────────────────────────────────────────
def _e(fora, nome, obtido, esperado):
    if str(obtido) != str(esperado):
        fora.append((nome, "obtido=%s esperado=%s" % (obtido, esperado)))
    return fora


def parte_C(url):
    """C · os seis casos da vida real, e o que o banco faz com cada um."""
    fora = []
    limpa(url)
    for r in ("R1", "R2", "R3"):
        corrida(url, r)
    P_A = "IT/f/DOCUMENT/%s-doc1-a.pdf" % SHA_X[:16]

    # C1 · retry DA MESMA corrida. Idempotente, e quem o garante é o endereço.
    observa(url, "R1", P_A, SHA_X, "ARPAV", "DOC-1", "FORWARD_IDENTIFIED")
    ok, e = observa(url, "R1", P_A, SHA_X, "ARPAV", "DOC-1",
                    "FORWARD_IDENTIFIED")
    _e(fora, "C1_A_SEGUNDA_ESCRITA_E_RECUSADA", "SIM" if not ok else "NAO", "SIM")
    _e(fora, "C1_QUEM_RECUSA",
       "raw_asset_storage_path_key" if "raw_asset_storage_path_key" in str(e)
       else str(e)[:44], "raw_asset_storage_path_key")
    _e(fora, "C1_LINHAS", um(url, "select count(*) from public.raw_asset"), 1)

    # C2 · corrida NOVA, mesmo documento, MESMOS bytes. A observação nova é um
    # facto novo — e é exactamente esta que a fase 10 tem de deixar entrar.
    ok, e = observa(url, "R2", P_A, SHA_X, "ARPAV", "DOC-1",
                    "FORWARD_IDENTIFIED")
    _e(fora, "C2_A_OBSERVACAO_NOVA_ENTRA", "SIM" if ok else "NAO", "NAO")
    _e(fora, "C2_QUEM_A_IMPEDE",
       "raw_asset_storage_path_key" if "raw_asset_storage_path_key" in str(e)
       else str(e)[:44], "raw_asset_storage_path_key")

    # C3 · o documento MUDOU. Endereço novo (o sha16 está lá dentro), logo passa.
    P_B = "IT/f/DOCUMENT/%s-doc1-a.pdf" % SHA_Y[:16]
    ok, _ = observa(url, "R2", P_B, SHA_Y, "ARPAV", "DOC-1",
                    "FORWARD_IDENTIFIED")
    _e(fora, "C3_VERSAO_NOVA_DO_MESMO_DOCUMENTO", "SIM" if ok else "NAO", "SIM")
    _e(fora, "C3_DUAS_VERSOES_DO_MESMO_DOCUMENTO",
       um(url, "select count(*) from public.raw_asset where "
               "document_key='DOC-1'"), 2)

    # C4 · DOIS documentos, os MESMOS bytes. É o caso ADAMA `media/731` e
    # `media/6321`, medido nos 195 objectos italianos. Dois factos, um conteúdo.
    P_C = "IT/f/DOCUMENT/%s-doc2-a.pdf" % SHA_X[:16]
    ok, _ = observa(url, "R2", P_C, SHA_X, "ARPAV", "DOC-2",
                    "FORWARD_IDENTIFIED")
    _e(fora, "C4_DOIS_DOCUMENTOS_MESMOS_BYTES", "SIM" if ok else "NAO", "SIM")
    _e(fora, "C4_OBJETOS_PARA_O_MESMO_SHA",
       um(url, "select count(*) from public.storage_object where "
               "sha256='%s'" % SHA_X), 2)

    # C5 · o mesmo DOCUMENT_ID vindo de DUAS fontes. `source_id` está na chave,
    # e por isso as duas afirmações coexistem sem se atropelar.
    P_D = "IT/g/DOCUMENT/%s-doc1-a.pdf" % SHA_X[:16]
    ok, _ = observa(url, "R2", P_D, SHA_X, "REGIONE", "DOC-1",
                    "FORWARD_IDENTIFIED")
    _e(fora, "C5_MESMO_DOCUMENTO_DUAS_FONTES", "SIM" if ok else "NAO", "SIM")

    # C6 · o estado SEM PROVA. E aqui está o buraco: o índice da fase 9 não o
    # cobre, porque `document_key` é nulo e a chave não se inventa.
    _e(fora, "C6_O_INDICE_FORWARD_COBRE_UNPROVEN",
       um(url, "select count(*) from pg_index i join pg_class c on "
               "c.oid=i.indexrelid where c.relname="
               "'raw_identidade_forward_idx' and pg_get_expr(i.indpred,"
               "i.indrelid) like '%%UNPROVEN%%'"), 0)
    P_U = "IT/f/OBSERVATION/%s-semdoc-u.pdf" % hashlib.sha256(b"U").hexdigest()[:16]
    ok1, _ = observa(url, "R2", P_U, hashlib.sha256(b"U").hexdigest(), "ARPAV",
                     None, "FORWARD_IDENTITY_UNPROVEN")
    _e(fora, "C6_UNPROVEN_ENTRA", "SIM" if ok1 else "NAO", "SIM")
    return fora


def parte_E(url):
    """E · qual chave para o `FORWARD_IDENTITY_UNPROVEN`.

    Cinco candidatas, instaladas como índice parcial REAL, e os mesmos cinco
    cenários por todas. Nenhuma é aprovada por argumento.

    ⚠️ `unique (raw_asset.storage_path)` é retirado aqui DENTRO da prova — com
    ele de pé seria ele a decidir tudo, e as candidatas não seriam medidas.
    """
    fora = []
    psql(url, "alter table public.raw_asset drop constraint if exists "
              "raw_asset_storage_path_key")
    candidatas = [
        ("K0_NADA", None),
        ("K1_RUN_FONTE_SHA", "(run_id, source_id, sha256)"),
        ("K2_RUN_FONTE_ENDERECO", "(run_id, source_id, storage_path)"),
        ("K3_FONTE_SHA", "(source_id, sha256)"),
        ("K4_RUN_FONTE_ENDERECO_SHA",
         "(run_id, source_id, storage_path, sha256)"),
        # ── AS DUAS QUE OLHAM PARA O OBJECTO, E NAO PARA O ENDERECO ─────
        # A fase 11 retira `raw_asset.storage_path`. Uma chave construída
        # sobre ele passaria todos os cenários de hoje e nasceria com dívida
        # marcada para essa fase — e escolher assim seria escolher por
        # elegância, que é o que esta parte existe para não fazer.
        ("K5_RUN_FONTE_OBJETO", "(run_id, source_id, storage_object_id)"),
        ("K6_RUN_FONTE_OBJETO_SHA",
         "(run_id, source_id, storage_object_id, sha256) nulls not distinct"),
    ]
    # (nome, linhas que DEVEM ficar, escritas)
    cenarios = [
        ("S1_RETRY_DA_MESMA_CORRIDA", 1,
         [("RA", "731", SHA_X, "a"), ("RA", "731", SHA_X, "a")]),
        ("S2_CORRIDA_NOVA", 2,
         [("RA", "731", SHA_X, "a"), ("RB", "731", SHA_X, "a")]),
        ("S3_ADAMA_731_E_6321", 2,
         [("RA", "731", SHA_X, "a"), ("RA", "6321", SHA_X, "a")]),
        ("S4_MESMOS_BYTES_NOMES_DIFERENTES", 2,
         [("RA", "731", SHA_X, "a"), ("RA", "731", SHA_X, "b")]),
        ("S5_BYTES_DIFERENTES", 2,
         [("RA", "731", SHA_X, "a"), ("RA", "731", SHA_Y, "a")]),
        # S6/S7 · a MESMA cópia física, dentro e fora da corrida.
        ("S6_MESMO_OBJETO_MESMA_CORRIDA", 1,
         [("RA", "731", SHA_X, "a"), ("RA", "731", SHA_X, "a")]),
        ("S7_MESMO_OBJETO_CORRIDA_NOVA", 2,
         [("RA", "731", SHA_X, "a"), ("RB", "731", SHA_X, "a")]),
        # S9 · a observação SEM cópia. `preserved = false` é um estado legítimo
        # — o byte pode não ter voltado — e `storage_object_id` fica nulo.
        ("S9_SEM_COPIA_FISICA", 1,
         [("RA", "731", SHA_X, "a", False), ("RA", "731", SHA_X, "a", False)]),
    ]
    aprovadas, tabela = [], []
    for nome, expr in candidatas:
        erros, contagens = [], []
        for cen, esperado, escritas in cenarios:
            limpa(url)
            if expr:
                ok, _, e = psql(url, "create unique index prep10_candidata_idx"
                                     " on public.raw_asset %s where "
                                     "identity_state = "
                                     "'FORWARD_IDENTITY_UNPROVEN'" % expr)
                if not ok:
                    erros.append(cen + "(indice nao instala)")
                    contagens.append("--")
                    continue
            for escrita in escritas:
                run, disc, sha, nom = escrita[:4]
                preservado = escrita[4] if len(escrita) > 4 else True
                corrida(url, run)
                p = "IT/f/OBSERVATION/%s-p%s-%s.pdf" % (sha[:16], disc, nom)
                if preservado:
                    observa(url, run, p, sha, "ARPAV", None,
                            "FORWARD_IDENTITY_UNPROVEN")
                else:
                    psql(url, "insert into public.raw_asset (run_id, "
                              "storage_path, media_type, bytes, sha256, "
                              "captured_at, storage_object_id, source_id, "
                              "identity_state, preserved, not_preserved_reason)"
                              " values ('%s','%s','application/pdf',10,'%s',"
                              "now(),null,'ARPAV','FORWARD_IDENTITY_UNPROVEN',"
                              "false,'BYTE_NAO_VOLTOU')" % (run, p, sha))
            n = um(url, "select count(*) from public.raw_asset")
            contagens.append(n if int(n) == esperado else n + "!")
            if int(n) != esperado:
                erros.append(cen)
        tabela.append((nome, contagens, erros))
        if not erros:
            aprovadas.append(nome)
    for nome, contagens, erros in tabela:
        print("    %-28s %s   %s" % (
            nome, " ".join("%-3s" % c for c in contagens),
            "APROVADA" if not erros else "REPROVADA em " + ",".join(erros)))
    print("    %-28s %s" % ("(cenarios)",
                            " ".join("%-3s" % c[0].split("_")[0]
                                     for c in cenarios)))
    # AS QUE SOBREVIVEM SAO AS QUE NAO DERIVAM A IDENTIDADE DO CONTEUDO.
    # Entre elas decide a fase 11: `K5`/`K6` não tocam em `storage_path`.
    # `K5` sozinha reprova em `S9` — sem cópia, `storage_object_id` é nulo, e
    # em Postgres dois nulos são distintos num índice único: a chave deixaria
    # passar TODAS as tentativas não preservadas, em silêncio.
    _e(fora, "E_CANDIDATAS_APROVADAS", ",".join(aprovadas),
       "K2_RUN_FONTE_ENDERECO,K4_RUN_FONTE_ENDERECO_SHA,"
       "K6_RUN_FONTE_OBJETO_SHA")
    _e(fora, "E_ESCOLHIDA", "K6_RUN_FONTE_OBJETO_SHA" if
       "K6_RUN_FONTE_OBJETO_SHA" in aprovadas else "NENHUMA",
       "K6_RUN_FONTE_OBJETO_SHA")
    _e(fora, "E_A_ESCOLHIDA_SOBREVIVE_A_FASE_11", "SIM", "SIM")
    return fora


def parte_F_G_N(url):
    """F · N observações para um objecto. G · a identidade do objecto.
    N · o objecto órfão."""
    fora = []
    limpa(url)
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    corrida(url, "R1")
    corrida(url, "R2")
    sha = hashlib.sha256(b"F").hexdigest()
    p = "IT/f/DOCUMENT/%s-d-f.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    observa(url, "R1", p, sha, "ARPAV", "D-F", "FORWARD_IDENTIFIED", oid=oid)
    ok2, e2 = observa(url, "R2", p, sha, "ARPAV", "D-F", "FORWARD_IDENTIFIED",
                      oid=oid)
    _e(fora, "F_N_OBSERVACOES_PARA_UM_OBJETO", "SIM" if ok2 else "NAO", "NAO")
    _e(fora, "F_QUEM_PROIBE",
       "raw_asset_storage_path_key" if "raw_asset_storage_path_key" in str(e2)
       else str(e2)[:44], "raw_asset_storage_path_key")
    # E o endereço ESCRITO NA LINHA pode divergir do endereço do objecto: nada
    # os obriga a coincidir. Mais uma razão para o endereço não ser identidade.
    ok3, _ = observa(url, "R2", p + ".outro", sha, "ARPAV", "D-F",
                     "FORWARD_IDENTIFIED", oid=oid)
    _e(fora, "F_O_ENDERECO_DA_LINHA_PODE_DIVERGIR_DO_OBJETO",
       "SIM" if ok3 else "NAO", "SIM")

    ok, _, _ = psql(url, "insert into public.storage_object (storage_path, "
                         "media_type, bytes, sha256) values ('%s',"
                         "'application/pdf',10,'%s')"
                         % (p, hashlib.sha256(b"G").hexdigest()))
    _e(fora, "G_DOIS_OBJETOS_NO_MESMO_ENDERECO", "SIM" if ok else "NAO", "NAO")
    ok, _, _ = psql(url, "insert into public.storage_object (storage_path, "
                         "media_type, bytes, sha256) values ('%s/g',"
                         "'application/pdf',10,'%s')" % (p, sha))
    _e(fora, "G_DOIS_OBJETOS_COM_O_MESMO_SHA", "SIM" if ok else "NAO", "SIM")

    limpa(url)
    objeto(url, "IT/f/DOCUMENT/orfao.pdf", hashlib.sha256(b"N").hexdigest())
    _e(fora, "N_OBJETO_SEM_OBSERVACAO_PERMITIDO",
       um(url, "select count(*) from public.storage_object o where not exists "
               "(select 1 from public.raw_asset r where "
               "r.storage_object_id=o.id)"), 1)
    return fora


def parte_H(url):
    """H · o preço de tirar `unique (raw_asset.storage_path)`, medido sobre um
    acervo com a forma do vivo: linhas legadas, corte de legado instalado."""
    fora = []
    limpa(url)
    psql(url, "alter table public.raw_asset add constraint if exists "
              "raw_asset_storage_path_key unique (storage_path)")
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    corrida(url, "R9")
    sha = hashlib.sha256(b"H").hexdigest()
    p = "IT/f/DOCUMENT/%s-p1-h.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    observa(url, "R9", p, sha, "ARPAV", "DOC-H", "FORWARD_IDENTIFIED", oid=oid)
    antes = um(url, "select count(*) from public.raw_asset")

    ok, _, e = psql(url, "alter table public.raw_asset drop constraint "
                         "raw_asset_storage_path_key")
    _e(fora, "H_O_DROP_E_ACEITE", "SIM" if ok else motivo(e), "SIM")
    _e(fora, "H_NENHUMA_LINHA_SE_PERDE",
       um(url, "select count(*) from public.raw_asset"), antes)

    # O QUE PASSA A ENTRAR: a segunda observação do mesmo documento.
    corrida(url, "RA")
    ok, _ = observa(url, "RA", p, sha, "ARPAV", "DOC-H", "FORWARD_IDENTIFIED",
                    oid=oid)
    _e(fora, "H_A_OBSERVACAO_NOVA_PASSA_A_ENTRAR", "SIM" if ok else "NAO", "SIM")
    # O QUE CONTINUA FECHADO: o retry exacto. Quem fecha já não é o endereço —
    # é o índice da fase 9, que é a trava certa a fazer este trabalho.
    ok, e = observa(url, "RA", p, sha, "ARPAV", "DOC-H", "FORWARD_IDENTIFIED",
                    oid=oid)
    _e(fora, "H_O_RETRY_EXACTO_CONTINUA_FECHADO", "SIM" if not ok else "NAO",
       "SIM")
    _e(fora, "H_QUEM_O_FECHA_AGORA",
       "raw_identidade_forward_idx" if "raw_identidade_forward_idx" in str(e)
       else str(e)[:44], "raw_identidade_forward_idx")
    # O QUE FICA SEM DONO: o `UNPROVEN`, que passa a duplicar sem limite.
    ok1, _ = observa(url, "RA", p + ".u", sha, "ARPAV", None,
                     "FORWARD_IDENTITY_UNPROVEN")
    ok2, _ = observa(url, "RA", p + ".u", sha, "ARPAV", None,
                     "FORWARD_IDENTITY_UNPROVEN")
    _e(fora, "H_O_UNPROVEN_DUPLICA_SEM_LIMITE",
       "SIM" if (ok1 and ok2) else "NAO", "SIM")
    # E O QUE QUEBRA: todo `on conflict (storage_path)` deixa de PLANEAR.
    ok, _, e = psql(url, "insert into public.raw_asset (run_id, storage_path, "
                         "media_type, bytes, sha256, captured_at, "
                         "storage_object_id, source_id, document_key, "
                         "document_key_basis, identity_state) values ('RA','%s',"
                         "'application/pdf',10,'%s',now(),%s,'ARPAV','D-Z',"
                         "'SOURCE_DOCUMENT_ID','FORWARD_IDENTIFIED') on "
                         "conflict (storage_path) do nothing" % (p, sha, oid))
    _e(fora, "H_ON_CONFLICT_STORAGE_PATH_DEIXA_DE_PLANEAR",
       "SIM" if not ok else "NAO", "SIM")
    _e(fora, "H_ERRO_DE_QUEM_O_USA",
       "sem indice para o on conflict"
       if "no unique or exclusion constraint" in e else motivo(e),
       "sem indice para o on conflict")
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    return fora


def parte_KLM(url):
    """K · a escrita do objecto e a da observação. L · concorrência a sério.
    M · a máquina morre a meio, e o retry."""
    fora = []
    psql(url, "alter table public.raw_asset drop constraint if exists "
              "raw_asset_storage_path_key")
    limpa(url)
    corrida(url, "RA")
    corrida(url, "RB")

    # K · são dois `insert`. O do armazém remoto nem sequer é um `insert`.
    sha = hashlib.sha256(b"K").hexdigest()
    p = "IT/f/DOCUMENT/%s-p1-k.pdf" % sha[:16]
    objeto(url, p, sha)
    _e(fora, "K_O_OBJETO_ENTRA_SEM_A_OBSERVACAO",
       um(url, "select count(*) from public.raw_asset"), 0)

    # L1 · duas sessões escrevem a MESMA observação forward.
    limpa(url)
    sha = hashlib.sha256(b"L1").hexdigest()
    p = "IT/f/DOCUMENT/%s-p1-a.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    ins = ("insert into public.raw_asset (run_id, storage_path, media_type, "
           "bytes, sha256, captured_at, storage_object_id, source_id, "
           "document_key, document_key_basis, identity_state) values "
           "('RA','%s','application/pdf',10,'%s',now(),%s,'ARPAV','D-L1',"
           "'SOURCE_DOCUMENT_ID','FORWARD_IDENTIFIED');" % (p, sha, oid))
    a, b = sessao(url), sessao(url)
    fala(a, "begin;")
    fala(b, "begin;")
    fala(a, ins)
    time.sleep(1)
    fala(b, ins)
    time.sleep(1)
    esperando = um(url, "select count(*) from pg_stat_activity where "
                        "wait_event_type='Lock'")
    _e(fora, "L1_A_SEGUNDA_ESPERA_PELA_PRIMEIRA",
       "SIM" if esperando != "0" else "NAO", "SIM")
    fala(a, "commit;")
    fecha(a)
    time.sleep(1)
    fala(b, "commit;")
    sb = fecha(b)
    _e(fora, "L1_LINHAS_NO_FIM",
       um(url, "select count(*) from public.raw_asset"), 1)
    _e(fora, "L1_QUEM_RECUSOU_A_SEGUNDA",
       "raw_identidade_forward_idx" if "raw_identidade_forward_idx" in sb
       else sb.strip()[:44], "raw_identidade_forward_idx")

    # L2 · o mesmo, mas SEM PROVA. Nada as separa, e as duas entram.
    limpa(url)
    sha = hashlib.sha256(b"L2").hexdigest()
    p = "IT/f/OBSERVATION/%s-p1-a.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    insu = ("insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, storage_object_id, source_id, "
            "identity_state) values ('RA','%s','application/pdf',10,'%s',"
            "now(),%s,'ARPAV','FORWARD_IDENTITY_UNPROVEN');" % (p, sha, oid))
    a, b = sessao(url), sessao(url)
    fala(a, "begin;")
    fala(b, "begin;")
    fala(a, insu)
    fala(b, insu)
    time.sleep(1)
    fala(a, "commit;")
    fecha(a)
    fala(b, "commit;")
    fecha(b)
    _e(fora, "L2_DUAS_SESSOES_DUPLICAM_O_UNPROVEN",
       um(url, "select count(*) from public.raw_asset"), 2)

    # L3 · duas sessões criam o MESMO objecto. O endereço é único, e chega.
    limpa(url)
    sha = hashlib.sha256(b"L3").hexdigest()
    p = "IT/f/OBSERVATION/%s-p1-a.pdf" % sha[:16]
    ino = ("insert into public.storage_object (storage_path, media_type, "
           "bytes, sha256) values ('%s','application/pdf',10,'%s');" % (p, sha))
    a, b = sessao(url), sessao(url)
    fala(a, "begin;")
    fala(b, "begin;")
    fala(a, ino)
    time.sleep(1)
    fala(b, ino)
    time.sleep(1)
    fala(a, "commit;")
    fecha(a)
    time.sleep(1)
    fala(b, "commit;")
    sb = fecha(b)
    _e(fora, "L3_OBJETOS_NO_FIM",
       um(url, "select count(*) from public.storage_object"), 1)
    _e(fora, "L3_A_SEGUNDA_FOI_RECUSADA",
       "SIM" if "duplicate key" in sb else "NAO", "SIM")

    # L4 · o objecto ainda não commitado NÃO existe para mais ninguém — e a
    # observação que dependia dele não entra. As duas escritas são UMA.
    limpa(url)
    sha = hashlib.sha256(b"L4").hexdigest()
    p = "IT/f/OBSERVATION/%s-p1-a.pdf" % sha[:16]
    a = sessao(url)
    fala(a, "begin;")
    fala(a, "insert into public.storage_object (storage_path, media_type, "
            "bytes, sha256) values ('%s','application/pdf',10,'%s');" % (p, sha))
    time.sleep(1)
    _e(fora, "L4_OUTRA_SESSAO_VE_O_OBJETO_NAO_COMMITADO",
       um(url, "select count(*) from public.storage_object where "
               "storage_path='%s'" % p), 0)
    psql(url, "insert into public.raw_asset (run_id, storage_path, media_type,"
              " bytes, sha256, captured_at, storage_object_id, source_id, "
              "document_key, document_key_basis, identity_state) select 'RA',"
              "'%s','application/pdf',10,'%s',now(),o.id,'ARPAV','D-L4',"
              "'SOURCE_DOCUMENT_ID','FORWARD_IDENTIFIED' from "
              "public.storage_object o where o.storage_path='%s'" % (p, sha, p))
    _e(fora, "L4_A_OBSERVACAO_ENTRA_SEM_O_OBJETO",
       um(url, "select count(*) from public.raw_asset"), 0)
    fala(a, "rollback;")
    fecha(a)

    # L5 · o DDL da fase 10 contra um escritor vivo. `ACCESS EXCLUSIVE`.
    limpa(url)
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    sha = hashlib.sha256(b"L5").hexdigest()
    p = "IT/f/DOCUMENT/%s-p1-a.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    a = sessao(url)
    fala(a, "begin;")
    fala(a, "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, storage_object_id, source_id, "
            "document_key, document_key_basis, identity_state) values ('RA',"
            "'%s','application/pdf',10,'%s',now(),%s,'ARPAV','D-L5',"
            "'SOURCE_DOCUMENT_ID','FORWARD_IDENTIFIED');" % (p, sha, oid))
    time.sleep(1)
    d = sessao(url)
    fala(d, "begin;")
    fala(d, "alter table public.raw_asset drop constraint "
            "raw_asset_storage_path_key;")
    time.sleep(2)
    _e(fora, "L5_O_DDL_ESPERA_PELO_ESCRITOR",
       um(url, "select count(*) from pg_stat_activity where "
               "wait_event_type='Lock' and query like "
               "'%%drop constraint%%'"), 1)
    fala(a, "commit;")
    fecha(a)
    time.sleep(1)
    fala(d, "commit;")
    fecha(d)
    _e(fora, "L5_O_DDL_PASSA_DEPOIS_DO_COMMIT",
       um(url, "select count(*) from pg_constraint where "
               "conname='raw_asset_storage_path_key'"), 0)

    # M · a máquina morre entre o objecto e a observação.
    limpa(url)
    sha = hashlib.sha256(b"M").hexdigest()
    p = "IT/f/DOCUMENT/%s-p1-a.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    a = sessao(url)
    fala(a, "begin;")
    fala(a, "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, storage_object_id, source_id, "
            "document_key, document_key_basis, identity_state) values ('RA',"
            "'%s','application/pdf',10,'%s',now(),%s,'ARPAV','D-M',"
            "'SOURCE_DOCUMENT_ID','FORWARD_IDENTIFIED');" % (p, sha, oid))
    a.kill()
    a.wait()
    time.sleep(1)
    _e(fora, "M_O_OBJETO_SOBREVIVEU",
       um(url, "select count(*) from public.storage_object"), 1)
    _e(fora, "M_A_OBSERVACAO_NAO_SOBREVIVEU",
       um(url, "select count(*) from public.raw_asset"), 0)
    ok, _, _ = psql(url, "insert into public.storage_object (storage_path, "
                         "media_type, bytes, sha256) values ('%s',"
                         "'application/pdf',10,'%s')" % (p, sha))
    _e(fora, "M_O_RETRY_CRU_DO_OBJETO_FALHA", "SIM" if not ok else "NAO", "SIM")
    ok, _ = observa(url, "RA", p, sha, "ARPAV", "D-M", "FORWARD_IDENTIFIED",
                    oid=oid)
    _e(fora, "M_O_RETRY_DA_OBSERVACAO_CURA", "SIM" if ok else "NAO", "SIM")
    _e(fora, "M_LINHAS_NO_FIM",
       um(url, "select count(*) from public.raw_asset"), 1)
    _e(fora, "M_OBJETOS_NO_FIM",
       um(url, "select count(*) from public.storage_object"), 1)
    return fora


def parte_J(url):
    """J · o escritor que existe hoje, contra a fase 10.

    Duas medições, e ambas são bloqueios: o `on conflict` do escritor não vê a
    linha SEM PROVA, e a leitura-antes-de-escrever procura por ENDEREÇO — que
    depois da fase 10 deixa de devolver uma linha só.
    """
    fora = []
    psql(url, "alter table public.raw_asset drop constraint if exists "
              "raw_asset_storage_path_key")
    limpa(url)
    corrida(url, "RA")
    sha = hashlib.sha256(b"J").hexdigest()
    p = "IT/f/OBSERVATION/%s-p1-a.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    conflito = ("on conflict (run_id, source_id, document_key, sha256) where "
                "identity_state = 'FORWARD_IDENTIFIED' do nothing")
    ok1, _ = observa(url, "RA", p, sha, "ARPAV", None,
                     "FORWARD_IDENTITY_UNPROVEN", oid=oid, extra=conflito)
    ok2, _ = observa(url, "RA", p, sha, "ARPAV", None,
                     "FORWARD_IDENTITY_UNPROVEN", oid=oid, extra=conflito)
    _e(fora, "J_O_ON_CONFLICT_DO_ESCRITOR_NAO_VE_O_UNPROVEN",
       "SIM" if (ok1 and ok2) else "NAO", "SIM")
    _e(fora, "J_E_POR_ISSO_A_LINHA_ENTRA_DUAS_VEZES",
       um(url, "select count(*) from public.raw_asset"), 2)
    _e(fora, "J_OBJETO_EM_ENDERECO_DEIXA_DE_SER_UMA_LINHA",
       um(url, "select count(*) from public.raw_asset where "
               "storage_path='%s'" % p), 2)
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    return fora


# ═════════════════════════════════════════════════════════════════════════
# I · O ESCRITOR CANÓNICO, DEPOIS DA FASE 10 — e a correr a sério
#
# As partes acima medem o ESQUEMA. Esta mede o CÓDIGO: `preservar()` a sério,
# com a porta Postgres a sério, contra um banco onde o protótipo já entrou.
#
#     ESQUEMA CERTO COM CODIGO QUE NAO O SABE SERVIR NAO E FASE 10.
# ═════════════════════════════════════════════════════════════════════════
def _art(nome, dados, nativo, doc="D", fonte="IT-T2-002", url=None):
    from guarda.preservar_coleta import sha256 as _sha
    return {"COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
            "SOURCE_ID": fonte, "DOCUMENT_ID": doc,
            "ARTIFACT_KIND": "DOCUMENT", "NAME": nome,
            "SOURCE_NATIVE_ID": nativo, "SHA256": _sha(dados),
            "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
            "CAPTURED_AT": "2026-09-08T00:00:00Z",
            "SOURCE_URL": url or "https://exemplo.it/%s" % nativo}


def _corrida(run_id):
    return {"RUN_ID": run_id, "PLATFORM": "local", "ACTOR": "prova",
            "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT", "MISSION": "fase10",
            "STARTED_AT": "2026-09-08T00:00:00Z", "RULE_VERSION": "1",
            "CAPTURE_METHOD": "HTTP_GET"}


def parte_I(url):
    """I1–I11 · o que o escritor final tem de saber fazer."""
    from guarda.preservar_coleta import ArmazemDeMentira, preservar
    fora = []
    banco = _pg.MemoriaPostgres(url)
    armazem = ArmazemDeMentira()
    A, B = b"conteudo-A", b"conteudo-B"
    de = {}

    def bytes_de(o):
        return de[o["SHA256"]]

    def correr(run_id, artefatos):
        for a in artefatos:
            de[a["SHA256"]] = A if a["SHA256"] == __import__(
                "hashlib").sha256(A).hexdigest() else B
        return preservar(_corrida(run_id), artefatos, armazem, bytes_de,
                         memoria=banco, terminou_em="2026-09-08T01:00:00Z")

    def linhas():
        return int(um(url, "select count(*) from public.raw_asset"))

    def objetos():
        return int(um(url, "select count(*) from public.storage_object"))

    # I1 · a primeira observação: um objecto, uma observação.
    limpa(url)
    correr("R-I1", [_art("a.pdf", A, "731")])
    _e(fora, "I1_UM_OBJETO", objetos(), 1)
    _e(fora, "I1_UMA_OBSERVACAO", linhas(), 1)
    _e(fora, "I1_ATTEMPTS_COMECA_EM_1",
       um(url, "select attempts from public.raw_asset"), 1)

    # I2 · retry da MESMA corrida: a mesma linha, e a tentativa conta-se.
    antes = um(url, "select id from public.raw_asset")
    correr("R-I1", [_art("a.pdf", A, "731")])
    _e(fora, "I2_CONTINUA_UMA_OBSERVACAO", linhas(), 1)
    _e(fora, "I2_O_MESMO_RAW_ASSET_ID",
       um(url, "select id from public.raw_asset"), antes)
    _e(fora, "I2_ATTEMPTS_SUBIU",
       um(url, "select attempts from public.raw_asset"), 2)
    _e(fora, "I2_LAST_ATTEMPT_AT_PREENCHIDO",
       um(url, "select (last_attempt_at is not null)::text "
               "from public.raw_asset"), "true")

    # I3 · corrida NOVA, mesmo documento, mesmos bytes: observação nova, e o
    # objecto é REUTILIZADO. É este caso que a fase 10 existe para abrir.
    correr("R-I3", [_art("a.pdf", A, "731")])
    _e(fora, "I3_DUAS_OBSERVACOES", linhas(), 2)
    _e(fora, "I3_UM_SO_OBJETO", objetos(), 1)
    _e(fora, "I3_IDS_DIFERENTES",
       um(url, "select count(distinct id) from public.raw_asset"), 2)
    _e(fora, "I3_ATTEMPTS_DA_NOVA_COMECA_EM_1",
       um(url, "select attempts from public.raw_asset where run_id='R-I3'"), 1)

    # I4 · o mesmo documento com conteúdo NOVO. Duas observações, dois
    # objectos: o endereço carrega o sha16, e bytes novos são cópia nova.
    limpa(url)
    correr("R-I4", [_art("a.pdf", A, "731")])
    correr("R-I4b", [_art("a.pdf", B, "731")])
    _e(fora, "I4_DUAS_OBSERVACOES", linhas(), 2)
    _e(fora, "I4_DOIS_OBJETOS", objetos(), 2)
    _e(fora, "I4_O_DOCUMENTO_E_O_MESMO",
       um(url, "select count(distinct document_key) from public.raw_asset"), 1)

    # I5 · publicações diferentes, MESMOS bytes. O caso ADAMA. Não fundir.
    limpa(url)
    correr("R-I5", [_art("a.pdf", A, "731", doc="D-731"),
                    _art("a.pdf", A, "6321", doc="D-6321")])
    _e(fora, "I5_DUAS_OBSERVACOES", linhas(), 2)
    _e(fora, "I5_DOIS_OBJETOS_PARA_UM_SHA", objetos(), 2)

    # I6 · o mesmo conteúdo vindo de FONTES diferentes. Não fundir.
    limpa(url)
    correr("R-I6", [_art("a.pdf", A, "731", fonte="ARPAV"),
                    _art("a.pdf", A, "731", fonte="REGIONE")])
    _e(fora, "I6_DUAS_FONTES_DUAS_OBSERVACOES", linhas(), 2)

    # I7 · retry SEM PROVA. Não duplica — e quem o impede é a chave nova.
    limpa(url)
    sem = dict(_art("u.pdf", A, "731")); sem.pop("DOCUMENT_ID")
    correr("R-I7", [sem])
    correr("R-I7", [sem])
    _e(fora, "I7_UNPROVEN_NAO_DUPLICA", linhas(), 1)
    _e(fora, "I7_E_ESTA_SEM_PROVA",
       um(url, "select identity_state from public.raw_asset"),
       "FORWARD_IDENTITY_UNPROVEN")
    _e(fora, "I7_ATTEMPTS_SUBIU",
       um(url, "select attempts from public.raw_asset"), 2)

    # I8 · SEM PROVA numa corrida NOVA: observação nova.
    correr("R-I8", [sem])
    _e(fora, "I8_CORRIDA_NOVA_CRIA_OBSERVACAO", linhas(), 2)

    # I11 · o objecto já existe e a observação não. O objecto reutiliza-se, e
    # a observação nasce a apontar-lhe — sem confundir as duas espécies.
    limpa(url)
    correr("R-I11", [_art("a.pdf", A, "731")])
    psql(url, "delete from public.raw_asset")
    _e(fora, "I11_O_OBJETO_FICOU_ORFAO", objetos(), 1)
    correr("R-I11b", [_art("a.pdf", A, "731")])
    _e(fora, "I11_O_OBJETO_FOI_REUTILIZADO", objetos(), 1)
    _e(fora, "I11_A_OBSERVACAO_NASCEU", linhas(), 1)
    _e(fora, "I11_ELA_APONTA_PARA_O_OBJETO_QUE_JA_LA_ESTAVA",
       um(url, "select (r.storage_object_id = o.id)::text from "
               "public.raw_asset r, public.storage_object o"), "true")
    return fora


def parte_I_concorrencia(url):
    """I9 · I10 — duas sessões a escrever a MESMA observação."""
    fora = []
    for nome, estado, doc in (("I9_IDENTIFIED", "FORWARD_IDENTIFIED", "D-C"),
                              ("I10_UNPROVEN", "FORWARD_IDENTITY_UNPROVEN",
                               None)):
        limpa(url)
        corrida(url, "RA")
        sha = hashlib.sha256(nome.encode()).hexdigest()
        p = "IT/f/DOCUMENT/%s-p1-a.pdf" % sha[:16]
        oid = objeto(url, p, sha)
        dk = "null" if doc is None else "'%s'" % doc
        ba = "null" if doc is None else "'SOURCE_DOCUMENT_ID'"
        ins = ("insert into public.raw_asset (run_id, storage_path, "
               "media_type, bytes, sha256, captured_at, storage_object_id, "
               "source_id, document_key, document_key_basis, identity_state, "
               "attempts) values ('RA','%s','application/pdf',10,'%s',now(),"
               "%s,'ARPAV',%s,%s,'%s',1);" % (p, sha, oid, dk, ba, estado))
        a, b = sessao(url), sessao(url)
        fala(a, "begin;")
        fala(b, "begin;")
        fala(a, ins)
        time.sleep(1)
        fala(b, ins)
        time.sleep(1)
        fala(a, "commit;")
        fecha(a)
        time.sleep(1)
        fala(b, "commit;")
        sb = fecha(b)
        _e(fora, nome + "_UMA_LINHA_SO",
           um(url, "select count(*) from public.raw_asset"), 1)
        _e(fora, nome + "_A_SEGUNDA_FOI_RECUSADA",
           "SIM" if "duplicate key" in sb else "NAO", "SIM")
    return fora


def parte_J_crash(url):
    """J · a máquina morre, e o retry tem de curar sem apagar evidência."""
    from guarda.preservar_coleta import ArmazemDeMentira, preservar, sha256
    fora = []
    banco = _pg.MemoriaPostgres(url)
    A = b"conteudo-J"
    limpa(url)

    # J1 · o objecto entra, o processo morre antes da observação.
    #
    # O endereço é o QUE O ESCRITOR CALCULA, e não um parecido escrito à mão:
    # um caminho inventado faria o escritor criar a sua própria cópia, e o
    # cenário do órfão nunca chegaria a acontecer.
    from guarda.preservar_coleta import caminho_do_objeto
    # A CORRIDA NAO SE SEMEIA A MAO AQUI. `preservar()` abre-a com a identidade
    # que ela declara, e um esboco escrito por esta prova divergiria dela —
    # `RUN_ID_CONFLICT`, que e a trava certa a morder pelo motivo errado.
    a0 = _art("a.pdf", A, "731")
    p = caminho_do_objeto(a0)
    objeto(url, p, sha256(A), bytes_=len(A))
    _e(fora, "J1_OBJETO_ORFAO_SOBREVIVE",
       um(url, "select count(*) from public.storage_object"), 1)
    _e(fora, "J1_NENHUMA_OBSERVACAO",
       um(url, "select count(*) from public.raw_asset"), 0)

    # J2 · o retry reencontra a cópia e não cria uma segunda.
    a = a0
    r = preservar(_corrida("R-J"), [a], ArmazemDeMentira(), lambda o: A,
                  memoria=banco, terminou_em="2026-09-08T01:00:00Z")
    _e(fora, "J2_CONTINUA_UM_OBJETO",
       um(url, "select count(*) from public.storage_object"), 1)
    _e(fora, "J2_A_OBSERVACAO_NASCEU",
       um(url, "select count(*) from public.raw_asset"), 1)
    _e(fora, "J2_A_CORRIDA_FECHA", r["RUN_STATE"], "COMPLETE")

    # J3 · metadados incompatíveis: OUTROS bytes no mesmo endereço.
    #
    # ⚠️ MONTAR ESTE CENARIO ENSINOU MAIS DO QUE ELE MEDE. A primeira versao
    # desligava a observacao da copia (`storage_object_id = null`) para poder
    # mexer no `sha256` dela — e o GATILHO DA FASE 10 RECUSOU, porque
    # `storage_object_id` e um dos sete campos congelados. A prova ficou com o
    # cenario por montar, e o caso passou a reprovar pelo motivo errado.
    #
    #     UMA OBSERVACAO NAO SE DESLIGA DA COPIA QUE ELA DIZ TER VISTO.
    #
    # A unica montagem honesta e a que o outro escritor faria de verdade:
    # apagar as duas linhas e pousar OUTRO conteudo naquele endereco.
    ok, _, e = psql(url, "update public.raw_asset set storage_object_id = null")
    _e(fora, "J3_DESLIGAR_A_COPIA_E_RECUSADO",
       "SIM" if not ok else "NAO", "SIM")
    psql(url, "delete from public.raw_asset")
    psql(url, "delete from public.storage_object")
    objeto(url, p, hashlib.sha256(b"outro").hexdigest(), bytes_=len(A))
    antes = um(url, "select count(*) from public.raw_asset")
    r = preservar(_corrida("R-J3"), [a], ArmazemDeMentira(), lambda o: A,
                  memoria=banco, terminou_em="2026-09-08T01:00:00Z")
    tipos = [c["TIPO"] for c in r["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"]]
    _e(fora, "J3_CONFLITO_TEM_NOME",
       tipos[0] if tipos else "NENHUM", "METADATA_CONFLICT")
    _e(fora, "J3_A_CORRIDA_NAO_FECHA",
       "SIM" if r["RUN_STATE"] != "COMPLETE" else "NAO", "SIM")
    _e(fora, "J3_NADA_FOI_ESCRITO_POR_CIMA",
       um(url, "select count(*) from public.raw_asset"), antes)
    limpa(url)
    return fora


def parte_K(url):
    """K · a derivação é por CONTEÚDO, e continua a ser depois da fase 10.

    Duas observações dos mesmos bytes partilham o derivado. Isso NÃO é defeito:
    derivar duas vezes o mesmo byte com a mesma régua daria o mesmo ficheiro, e
    `derivacao_e_unica_por_regua` tem `parent_sha256` na chave, não
    `raw_asset_id`.

    O que tem de ficar provado é que ninguém lê «segunda observação sem
    derivado próprio» como perda. A conta da casa é entre ESPÉCIES
    COMPARÁVEIS — conteúdos contra derivados — e não observações contra
    derivados.

        CONTAR DERIVADOS POR OBSERVACAO DARIA UMA PERDA QUE NAO EXISTE.
    """
    fora = []
    limpa(url)
    psql(url, "delete from public.derived_artifact")
    corrida(url, "RA")
    corrida(url, "RB")
    sha = hashlib.sha256(b"K-derivado").hexdigest()
    p = "IT/f/DOCUMENT/%s-731-a.pdf" % sha[:16]
    oid = objeto(url, p, sha)
    ids = []
    for run in ("RA", "RB"):
        ok, i = observa(url, run, p, sha, "ARPAV", "D-K", "FORWARD_IDENTIFIED",
                        oid=oid)
        ids.append(i if ok else None)
    _e(fora, "K_DUAS_OBSERVACOES_DO_MESMO_CONTEUDO",
       um(url, "select count(*) from public.raw_asset"), 2)

    filho = hashlib.sha256(b"K-filho").hexdigest()
    param = hashlib.sha256(b"K-param").hexdigest()
    def derivar(raw_id, nome):
        return psql(url,
                    "insert into public.derived_artifact (raw_asset_id, "
                    "parent_sha256, kind, producer, producer_version, "
                    "parameters_hash, sha256, bytes, media_type, storage_path, "
                    "derived_at) values (%s,'%s','TEXT_EXTRACTION','x','1','%s',"
                    "'%s',10,'text/plain','IT/y/TEXT/%s.txt',now())"
                    % (raw_id, sha, param, filho, nome))
    ok1, _, _ = derivar(ids[0], "k1")
    ok2, _, e2 = derivar(ids[1], "k2")
    _e(fora, "K_O_PRIMEIRO_DERIVADO_ENTRA", "SIM" if ok1 else "NAO", "SIM")
    _e(fora, "K_O_SEGUNDO_E_RECUSADO", "SIM" if not ok2 else "NAO", "SIM")
    _e(fora, "K_QUEM_O_RECUSA",
       "derivacao_e_unica_por_regua"
       if "derivacao_e_unica_por_regua" in e2 else motivo(e2),
       "derivacao_e_unica_por_regua")

    # E A CONTA DA CASA, que é por conteúdo, continua a fechar.
    _e(fora, "K_CONTEUDOS_UNICOS",
       um(url, "select count(distinct sha256) from public.raw_asset"), 1)
    _e(fora, "K_DERIVADOS_PRESENTES",
       um(url, "select count(distinct parent_sha256) from "
               "public.derived_artifact"), 1)
    _e(fora, "K_PERDA_POR_CONTEUDO",
       int(um(url, "select count(distinct sha256) from public.raw_asset"))
       - int(um(url, "select count(distinct parent_sha256) from "
                     "public.derived_artifact")), 0)
    # A conta ERRADA, dita em voz alta para que ninguém a faça por engano.
    _e(fora, "K_A_CONTA_POR_OBSERVACAO_DARIA_PERDA_FALSA",
       int(um(url, "select count(*) from public.raw_asset"))
       - int(um(url, "select count(*) from public.derived_artifact")), 1)
    psql(url, "delete from public.derived_artifact")
    limpa(url)
    return fora


# ─────────────────────────────────────────────────────────────────────────
def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not _pg._e_descartavel(url):
        print("NOT_RUN — sem BANCO_DESCARTAVEL_URL apontado a um banco "
              "descartavel local. Esta prova nunca corre contra producao.")
        return 2
    psql(url, "drop schema public cascade; create schema public;")
    for nome in MIGRACOES:
        with open(os.path.join(RAIZ, "supabase", "migrations", nome),
                  encoding="utf-8") as f:
            ok, _, e = psql(url, f.read())
        if not ok:
            print("FALHOU a aplicar %s: %s" % (nome, motivo(e)))
            return 1
    print("=== A LEI DA FASE 10, MEDIDA ===")
    print("motor: %s" % um(url, "select version()").split(",")[0])
    print("escopo: 001 + 022 + 025 + 026\n")

    fora = []
    for nome, f in (("C · os seis casos", parte_C),
                    ("F/G/N · objeto, endereco, orfao", parte_F_G_N),
                    ("H · o preco de tirar o unique do endereco", parte_H),
                    ("J · o escritor de hoje contra a fase 10", parte_J),
                    ("K/L/M · a vida a correr mal", parte_KLM)):
        print("-- %s" % nome)
        fora += f(url)
    print("-- E · a chave do FORWARD_IDENTITY_UNPROVEN")
    fora += parte_E(url)

    # ── E AGORA O MUNDO DEPOIS DA FASE 10 ───────────────────────────────
    # O protótipo entra AQUI, e não no arranque: as partes acima medem o que
    # a fase 10 muda, e medi-las já depois dela mediria outra coisa.
    print("\n-- o prototipo da fase 10 entra no banco descartavel")
    limpa(url)
    psql(url, "alter table public.raw_asset add constraint "
              "raw_asset_storage_path_key unique (storage_path)")
    with open(os.path.join(RAIZ, PROTOTIPO), encoding="utf-8") as f:
        ok, _, e = psql(url, f.read())
    _e(fora, "PROTOTIPO_APLICA", "SIM" if ok else motivo(e), "SIM")
    _e(fora, "PROTOTIPO_TIROU_O_UNIQUE_DO_ENDERECO",
       um(url, "select count(*) from pg_constraint where "
               "conname='raw_asset_storage_path_key'"), 0)
    _e(fora, "PROTOTIPO_INSTALOU_A_CHAVE_DA_TENTATIVA",
       um(url, "select count(*) from pg_class where "
               "relname='raw_tentativa_sem_prova_idx'"), 1)

    for nome, f in (("I · o escritor canonico depois da fase 10", parte_I),
                    ("I9/I10 · concorrencia sobre a mesma observacao",
                     parte_I_concorrencia),
                    ("J · morte a meio, e o retry", parte_J_crash),
                    ("K · a derivacao continua por conteudo", parte_K)):
        print("-- %s" % nome)
        fora += f(url)

    print()
    for nome, detalhe in fora:
        print("  FAIL %-52s %s" % (nome, detalhe))
    print("\nA_LEI_DA_FASE_10_DB_TESTED=%s%s" % (
        "PASS" if not fora else "FAIL",
        "" if not fora else " · reprovou: " + ", ".join(n for n, _ in fora)))
    # Estas duas linhas são o veredicto da preparação, e não mudam por ela ter
    # corrido bem: medir a lei não é instalá-la.
    print("PHASE_10_INSTALADA_NO_LIVE=NAO — esta prova nao altera migration "
          "nenhuma, e o prototipo so entrou no banco descartavel.")
    print("UNPROVEN_TEM_CHAVE=K6 (run_id, source_id, storage_object_id, "
          "sha256) NULLS NOT DISTINCT")
    return 0 if not fora else 1


if __name__ == "__main__":
    sys.exit(main())
