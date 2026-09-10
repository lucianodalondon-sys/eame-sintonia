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
            for run, disc, sha, nom in escritas:
                corrida(url, run)
                p = "IT/f/OBSERVATION/%s-p%s-%s.pdf" % (sha[:16], disc, nom)
                observa(url, run, p, sha, "ARPAV", None,
                        "FORWARD_IDENTITY_UNPROVEN")
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
                            " ".join("S%d " % i for i in range(1, 6))))
    # As duas que sobrevivem à ADAMA são as duas que NÃO derivam a identidade
    # do conteúdo. Se um dia isto mudar, é porque a lei mudou — e tem de doer.
    _e(fora, "E_CANDIDATAS_APROVADAS", ",".join(aprovadas),
       "K2_RUN_FONTE_ENDERECO,K4_RUN_FONTE_ENDERECO_SHA")
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

    print()
    for nome, detalhe in fora:
        print("  FAIL %-52s %s" % (nome, detalhe))
    print("\nA_LEI_DA_FASE_10_DB_TESTED=%s%s" % (
        "PASS" if not fora else "FAIL",
        "" if not fora else " · reprovou: " + ", ".join(n for n, _ in fora)))
    # Estas duas linhas são o veredicto da preparação, e não mudam por ela ter
    # corrido bem: medir a lei não é instalá-la.
    print("PHASE_10_INSTALADA=NAO — esta prova nao altera migration nenhuma.")
    print("UNPROVEN_TEM_CHAVE_NO_ESQUEMA=NAO — e por isso o veredicto e NO.")
    return 0 if not fora else 1


if __name__ == "__main__":
    sys.exit(main())
