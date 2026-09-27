#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MESMA GARANTIA, CONTRA POSTGRES DE VERDADE — e num que morre no fim.

POR QUE ISTO EXISTE
-------------------
`tests/test_preservar_coleta_no_banco.py` prova a reconciliação contra um banco
real, mas SQLite. As travas que interessam são as mesmas — `storage_path`
único, `sha256` não único, `run_id` obrigatório com chave estrangeira — só que
SQLite não é Postgres, e dizer «provado no banco» sem dizer **qual** seria
esconder metade da frase.

Este ficheiro corre os mesmos cenários contra **Postgres 16**, com a
`migration 001` ORIGINAL aplicada — enum `run_status` incluído, que o SQLite
teve de traduzir para um `CHECK`. Ele corre no workflow `banco-descartavel.yml`,
num contentor que nasce e morre dentro do próprio job.

    DB_TESTED (SQLITE)                    é o que a bateria local prova
    POSTGRES16_FOUNDATION_SCHEMA_TESTED   é o que este ficheiro acrescenta

E o nome é longo de propósito. Aqui aplica-se **só a migration 001**: as
002–021 não entram, e chamar a isto «o esquema atual provado» seria dizer mais
do que se mediu. Alargar o escopo não é o assunto — não superestimar a prova é.

A TRAVA CONTRA O ACIDENTE
-------------------------
Este é o único ficheiro desta missão que fala com um banco a sério. Por isso
ele **recusa-se a arrancar** se a ligação não for descartável. E a trava não
procura pedaços de texto: ela **decompõe a URL** e exige que o `hostname` seja
exatamente local E que o banco esteja na lista curta dos descartaveis. Um
dedo enganado a
apontar para produção não passa daqui.

Não usa driver instalado: fala pelo `psql`, que o runner já tem. Instalar um
pacote global só para um teste passar continua proibido.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from guarda.preservar_coleta import (  # noqa: E402
    METADATA_CONFLICT, NEW_RUN_SAME_STORAGE_PATH, PRESERVED_AND_REGISTERED, RUN_ID_CONFLICT,
    UPLOAD_PENDING_METADATA, ArmazemDeMentira, Memoria,
    caminho_do_objeto, preservar, sha256)

MIGRACAO = os.path.join(RAIZ, "supabase", "migrations",
                        "001_fundacao_geografia_e_proveniencia.sql")
# 025 acrescenta uma trava A `raw_asset`, e esta prova escreve linhas dessa
# tabela. Prova-la sobre a 001 sozinha seria prova-la contra um esquema que
# esta casa ja nao tem.
# E a 026 acrescenta a IDENTIDADE da observacao, que o writer passou a
# escrever: sem ela, o SQL deste dono nomeia colunas que nao existem.
MIGRACAO_025 = os.path.join(RAIZ, "supabase", "migrations",
                            "025_o_objeto_ganha_casa.sql")
MIGRACAO_026 = os.path.join(RAIZ, "supabase", "migrations",
                            "026_a_observacao_ganha_identidade.sql")

# ── A TRAVA E O ADAPTADOR MUDARAM DE CASA — 2026-09-17 ─────────────────────
# ⚠️ ISTO ERA O ÚNICO ADAPTADOR POSTGRES COMPLETO DESTA CASA, E ERA PROVA.
# O runtime não o podia importar, e não importava: a porta CLI do orquestrador
# corria sem memória, e o replay canário pelo workflow real (run 35215565657,
# know-how §132) mediu o preço. A implementação genérica vive agora em
# `guarda/memoria_postgres.py`; a trava que decompõe a URL, em
# `guarda/banco_descartavel.py`. Esta prova IMPORTA de lá — nunca o contrário.
#
#     PROVA NÃO É RUNTIME. PROVAS → IMPLEMENTAÇÃO CANÓNICA. NUNCA RUNTIME → PROVAS.
#
# Os nomes antigos continuam a existir aqui (`_e_descartavel`, `HOSTS_LOCAIS`,
# `BANCOS_PERMITIDOS`, `_lit`, `MemoriaPostgres`) porque outras provas e
# testes os importam por este caminho. São o MESMO objeto, não uma cópia.
from guarda.banco_descartavel import (  # noqa: E402
    BANCOS_PERMITIDOS, HOSTS_LOCAIS, e_descartavel as _e_descartavel)
from guarda.memoria_postgres import (  # noqa: E402
    MemoriaPostgres as _MemoriaPostgresCanonica, lit as _lit)


class MemoriaPostgres(_MemoriaPostgresCanonica):
    """A porta canónica, com a trava DESTA prova à entrada.

    O adaptador não decide se o banco é descartável — quem compõe decide.
    Aqui quem compõe é a prova, e a prova recusa-se a arrancar contra
    qualquer coisa que não prove ser local e descartável. Um dedo enganado a
    apontar para produção não passa daqui.
    """

    def __init__(self, url):
        if not _e_descartavel(url):
            raise SystemExit(
                "RECUSADO: '%s' nao parece um banco descartavel local. "
                "Esta prova nunca corre contra producao." % url)
        super().__init__(url)


# ─────────────────────────────────────────────────────────────────────────
# OS CENÁRIOS — os mesmos do banco local, contra o motor de verdade
# ─────────────────────────────────────────────────────────────────────────
A, B = b"o conteudo A", b"o conteudo B"
FIM = "2026-09-08T00:05:00Z"


def _corrida(run_id="IT-PG-0001", **extra):
    d = {"RUN_ID": run_id, "PLATFORM": "local", "ACTOR": "teste",
         "ACTOR_VERSION": "1", "SOURCE_COUNTRY": "IT", "MISSION": "prova",
         "STARTED_AT": "2026-09-08T00:00:00Z", "RULE_VERSION": "1",
         "CAPTURE_METHOD": "HTTP_GET"}
    d.update(extra)
    return d


def _pousar_outro_conteudo(banco, caminho, sha, doc, bytes_=1,
                           run_id="IT-PG-A"):
    """Outro escritor poe OUTRO conteudo no mesmo endereco.

    Troca a COPIA e a OBSERVACAO juntas, porque desde a 026 elas nao podem
    discordar: a chave estrangeira composta recusa `raw_asset.sha256 = H1` a
    apontar para um objeto de `H2`. Apagar e reescrever e o unico caminho que
    respeita a trava — e o cenario continua a ser o mesmo.
    """
    banco.aplicar(
        "delete from public.raw_asset where storage_path = '%s';\n"
        "delete from public.storage_object where storage_path = '%s';\n"
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256) values ('%s','application/pdf',1,'%s');\n"
        "insert into public.raw_asset (run_id, storage_path, media_type, bytes, "
        "sha256, captured_at, storage_object_id, identity_state, source_id, "
        "document_key, document_key_basis) select '%s','%s',"
        "'application/pdf',%d,'%s','2026-09-08T00:00:00Z', o.id,"
        "'FORWARD_IDENTIFIED','IT-T2-002','%s','SOURCE_DOCUMENT_ID' "
        "from public.storage_object o where o.storage_path = '%s';"
        % (caminho, caminho, caminho, sha, run_id, caminho, bytes_, sha,
           doc, caminho))


def _art(nome, dados, nativo):
    return {"COUNTRY": "IT", "SOURCE_SLUG": "fonte-de-teste",
            # 026: SOURCE_ID canonico e DOCUMENT_ID provado pelo contrato.
            "SOURCE_ID": "IT-T2-002", "DOCUMENT_ID": "ARPAV:Z07:%s" % nativo,
            "ARTIFACT_KIND": "DOCUMENT", "NAME": nome,
            "SOURCE_NATIVE_ID": nativo, "SHA256": sha256(dados),
            "BYTES": len(dados), "MEDIA_TYPE": "application/pdf",
            "CAPTURED_AT": "2026-09-08T00:00:00Z",
            "SOURCE_URL": "https://exemplo.it/%s" % nativo}


def _bytes_de(obj):
    return {sha256(A): A, sha256(B): B}[obj["SHA256"]]


def _correr(banco, artefatos, run=None, armazem=None):
    return preservar(run or _corrida(), artefatos, armazem or ArmazemDeMentira(),
                     _bytes_de, memoria=banco, terminou_em=FIM)


def cenarios(banco):
    """Os casos A–L, cada um na sua corrida e com o seu próprio arranjo.

    A versão anterior encadeava tudo na mesma corrida e usava `and`/`or`
    soltos — um caso podia dar PASS por causa do estado deixado pelo anterior.
    Aqui cada caso monta o que precisa e **declara o que observou**, para que um
    PASS nunca seja um acaso herdado.

    Devolve `(nome, passou, detalhe)`.
    """
    fora = []

    def caso(nome, condicao, detalhe=""):
        fora.append((nome, bool(condicao), detalhe))

    # ── A · B · C — o caminho feliz, contado no próprio Postgres ─────────
    run_a = _corrida("IT-PG-A")
    arm_a = ArmazemDeMentira()
    r = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                run=run_a, armazem=arm_a)
    caso("A_dois_objetos_planeados", r["PLANO"]["OBJETOS_PLANEADOS"] == 2,
         "planeados=%s" % r["PLANO"]["OBJETOS_PLANEADOS"])
    caso("B_o_SELECT_confirma_duas_linhas",
         r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"] == 2,
         "observadas=%s contar=%d" % (
             r["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"],
             banco.contar("raw_asset")))
    pos = r["CONFERENCIA_POS_ESCRITA"] or {}
    caso("B2_os_campos_batem_apos_a_escrita",
         pos.get("POST_WRITE_METADATA_MATCH") == 2 and not pos.get("DIVERGENTES"),
         "match=%s divergentes=%s" % (pos.get("POST_WRITE_METADATA_MATCH"),
                                      len(pos.get("DIVERGENTES") or [])))
    linha_a = banco.corrida("IT-PG-A") or {}
    caso("C_a_corrida_termina_concluida_no_postgres",
         r["RUN_STATE"] == "COMPLETE" and linha_a.get("status") == "concluida"
         and r["PENDENCIA"] == PRESERVED_AND_REGISTERED,
         "run_state=%s status=%s" % (r["RUN_STATE"], linha_a.get("status")))
    caso("C2_finished_at_gravado_e_diferente_do_started_at",
         bool(linha_a.get("finished_at"))
         and linha_a.get("finished_at") != linha_a.get("started_at"),
         "started=%s finished=%s" % (linha_a.get("started_at"),
                                     linha_a.get("finished_at")))

    # ── D · E — retry idêntico ───────────────────────────────────────────
    r2 = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                 run=run_a, armazem=arm_a)
    caso("D_retry_nao_duplica",
         banco.contar("raw_asset") == 2 and banco.contar("collection_run") == 1,
         "raw=%d run=%d" % (banco.contar("raw_asset"),
                            banco.contar("collection_run")))
    caso("E_reencontro_identico_e_REUSED",
         r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"] == 2
         and not r2["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"],
         "reused=%s" % r2["JA_EXISTIA_NO_BANCO"]["REUSED_METADATA"])

    # ── F — mesmo caminho, outro sha256 ──────────────────────────────────
    # ⚠️ DESDE A 026 AS DUAS ESPECIES NAO PODEM DISCORDAR. A versao anterior
    # deste caso mexia so no `sha256` da observacao — e isso agora e recusado
    # pela chave estrangeira COMPOSTA, que e exactamente a trava que se queria.
    # O cenario real («outro escritor pos outro conteudo neste endereco») troca
    # as DUAS: a copia e a observacao. Trocar so uma nunca foi o cenario; era
    # um atalho que o esquema antigo deixava passar.
    antes_de_f = banco.objetos_da_corrida("IT-PG-A")[0]
    caminho = antes_de_f["storage_path"]
    _pousar_outro_conteudo(banco, caminho, "f" * 64, "DOC:OUTRO")
    r3 = _correr(banco, [_art("a.pdf", A, "11"), _art("b.pdf", B, "22")],
                 run=run_a, armazem=arm_a)
    caso("F_sha_divergente_e_METADATA_CONFLICT",
         r3["PENDENCIA"] == METADATA_CONFLICT and r3["RUN_STATE"] == "PARTIAL",
         "pendencia=%s" % r3["PENDENCIA"])
    # E devolve-se a linha ORIGINAL — a dela, nao a de outro caminho. Repor
    # com a identidade errada colidiria com o indice parcial da fase 9, que e
    # exactamente o que ele existe para fazer.
    _pousar_outro_conteudo(banco, caminho, antes_de_f["sha256"],
                           antes_de_f["document_key"],
                           int(antes_de_f["bytes"]))

    # ── G — mesmo caminho reclamado por OUTRA corrida ────────────────────
    r4 = _correr(banco, [_art("a.pdf", A, "11")],
                 run=_corrida("IT-PG-G"), armazem=arm_a)
    # 026: divergir SO na corrida ganhou nome proprio. E na preparacao da fase
    # 10 deixou de ser CONFLITO: a observacao e legitima, a escrita e TENTADA,
    # e quem a recusa e a trava fisica no banco — nao uma decisao em Python.
    #
    #     O ESCRITOR DEIXOU DE CARREGAR A TRAVA DO ESQUEMA DENTRO DE SI.
    #
    # A `PENDENCIA` continua a dizer o nome certo, porque foi mesmo ela que
    # mordeu; o que mudou e QUEM decidiu.
    notas_g = r4["JA_EXISTIA_NO_BANCO"]["OBSERVACOES_NOVAS_EM_ENDERECO_OCUPADO"]
    caso("G_outra_corrida_no_mesmo_caminho_e_NEW_RUN_SAME_STORAGE_PATH",
         r4["PENDENCIA"] == NEW_RUN_SAME_STORAGE_PATH
         and r4["RUN_STATE"] == "PARTIAL"
         and not r4["JA_EXISTIA_NO_BANCO"]["CONFLITOS_DE_OBJETO"]
         and notas_g and notas_g[0]["TIPO"] == NEW_RUN_SAME_STORAGE_PATH
         and not r4["MEMORIA"]["APLICADA"],
         "pendencia=%s notas=%d" % (r4["PENDENCIA"], len(notas_g)))

    # ── J — mesmo run_id, identidade congelada diferente ─────────────────
    r5 = _correr(banco, [_art("j.pdf", B, "jj")],
                 run=_corrida("IT-PG-A", ACTOR_VERSION="2"),
                 armazem=ArmazemDeMentira())
    caso("J_run_id_com_outra_identidade_e_RUN_ID_CONFLICT",
         r5["PENDENCIA"] == RUN_ID_CONFLICT and r5["RUN_STATE"] == "PARTIAL",
         "pendencia=%s" % r5["PENDENCIA"])

    # ── H — o SQL corre inteiro e grava a MENOS, sem erro nenhum ─────────
    # Encenado: a mao que aplica deixa cair um `insert`. E o que o
    # `on conflict do nothing` faz de verdade — corre, devolve sucesso, e o
    # banco fica com menos linhas do que se pediu. Se a reconciliacao viesse do
    # numero ESPERADO, isto passava como sucesso.
    original = banco.aplicar
    estado = {"engolir": True}

    def engolir_um_insert(sql):
        if estado["engolir"] and "insert into public.raw_asset" in sql:
            estado["engolir"] = False
            ficam, caiu = [], False
            for linha in sql.splitlines():
                if linha.startswith("insert into public.raw_asset") and not caiu:
                    caiu = True
                    continue
                ficam.append(linha)
            sql = "\n".join(ficam) + "\n"
        original(sql)

    banco.aplicar = engolir_um_insert
    arm_h = ArmazemDeMentira()
    r6 = _correr(banco, [_art("h1.pdf", A, "h1"), _art("h2.pdf", B, "h2")],
                 run=_corrida("IT-PG-H"), armazem=arm_h)
    banco.aplicar = original
    caso("H_grava_a_menos_e_a_reconciliacao_reprova",
         r6["MEMORIA"]["APLICADA"] and r6["MEMORIA"]["LINHAS_ESPERADAS"] == 2
         and r6["MEMORIA"]["LINHAS_OBSERVADAS"] == 1
         and r6["RUN_STATE"] == "PARTIAL"
         and "reconciliacao_observada" in r6["COMPLETION_BASIS"]["FALTOU"],
         "esperadas=%s observadas=%s estado=%s" % (
             r6["MEMORIA"]["LINHAS_ESPERADAS"],
             r6["MEMORIA"]["LINHAS_OBSERVADAS"], r6["RUN_STATE"]))
    caso("H2_a_corrida_fica_rodando_no_banco",
         (banco.corrida("IT-PG-H") or {}).get("status") == "rodando",
         "status=%s" % (banco.corrida("IT-PG-H") or {}).get("status"))
    caso("K_o_byte_fica_preservado_apos_falha_de_memoria",
         len(arm_h.objetos) == 2, "objetos=%d" % len(arm_h.objetos))

    # ── L — recuperação: correr outra vez faz SÓ o que falta ─────────────
    envios_antes = arm_h.envios
    r7 = _correr(banco, [_art("h1.pdf", A, "h1"), _art("h2.pdf", B, "h2")],
                 run=_corrida("IT-PG-H"), armazem=arm_h)
    caso("L_recuperacao_sem_duplicar_byte_nem_linha",
         arm_h.envios == envios_antes and r7["RUN_STATE"] == "COMPLETE"
         and (banco.corrida("IT-PG-H") or {}).get("status") == "concluida",
         "envios=%d->%d estado=%s" % (envios_antes, arm_h.envios,
                                      r7["RUN_STATE"]))

    # ── I — as linhas entram, mas o fecho da corrida falha ───────────────
    def recusar_o_fecho(sql):
        if "update public.collection_run" in sql:
            raise IOError("o banco recusou o fecho")
        original(sql)

    banco.aplicar = recusar_o_fecho
    r8 = _correr(banco, [_art("i1.pdf", A, "i1")],
                 run=_corrida("IT-PG-I"), armazem=ArmazemDeMentira())
    banco.aplicar = original
    caso("I_metadata_entra_mas_fecho_falha_nao_da_COMPLETE",
         r8["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"] == 1
         and r8["RUN_STATE"] == "PARTIAL"
         and "banco_diz_concluida" in r8["COMPLETION_BASIS"]["FALTOU"]
         and not r8["AS_DUAS_CASAS_CONCORDAM"],
         "observadas=%s estado=%s pendencia=%s" % (
             r8["RECONCILIACAO"]["LINHAS_OBSERVADAS_NO_BANCO"],
             r8["RUN_STATE"], r8["PENDENCIA"]))

    # ── CORRIDA CONCORRENTE — contagem certa, conteúdo errado ────────────
    # A janela entre a leitura previa e o nosso insert. Se a reconciliacao
    # fosse so contagem, isto passava — e a corrida fechava sobre um conteudo
    # que nao e o nosso.
    art_r = _art("race.pdf", A, "rr")
    caminho_r = caminho_do_objeto(art_r)

    def intruso_entra_no_meio(sql):
        if "insert into public.raw_asset" in sql:
            banco.aplicar = original
            original("insert into public.collection_run "
                     "(run_id, platform, started_at, rule_version) values "
                     "('IT-PG-INTRUSA','x','2026-01-01T00:00:00Z','1') "
                     "on conflict (run_id) do nothing;")
            # 025: o intruso escreve as DUAS especies. No esquema novo nao
            # ha como escrever so uma — e a encenacao fica mais realista, nao
            # menos: quem chega primeiro ao endereco fica com a copia.
            original("insert into public.storage_object (storage_path, "
                     "media_type, bytes, sha256) values "
                     "('%s','application/pdf',999,'%s') "
                     "on conflict (storage_path) do nothing;"
                     % (caminho_r, "e" * 64))
            # 026: o intruso tambem declara identidade — nao ha caminho para
            # escrever sem ela, e e por isso que a encenacao continua a valer.
            original("insert into public.raw_asset (run_id, storage_path, "
                     "media_type, bytes, sha256, captured_at, "
                     "storage_object_id, identity_state, source_id, "
                     "document_key, document_key_basis) "
                     "select 'IT-PG-INTRUSA','%s',"
                     "'application/pdf',999,'%s','2026-01-01T00:00:00Z', o.id,"
                     "'FORWARD_IDENTIFIED','IT-INTRUSA','DOC:INTRUSA',"
                     "'SOURCE_DOCUMENT_ID' "
                     "from public.storage_object o where o.storage_path = '%s';"
                     % (caminho_r, "e" * 64, caminho_r))
        original(sql)

    banco.aplicar = intruso_entra_no_meio
    r9 = _correr(banco, [art_r], run=_corrida("IT-PG-RACE"),
                 armazem=ArmazemDeMentira())
    banco.aplicar = original
    quantas = len(banco.objetos_da_corrida("IT-PG-INTRUSA"))
    caso("RACE_contagem_certa_conteudo_errado_e_apanhado",
         quantas == 1 and r9["RUN_STATE"] == "PARTIAL"
         and r9["PENDENCIA"] == METADATA_CONFLICT
         and "campos_batem_apos_escrita" in r9["COMPLETION_BASIS"]["FALTOU"],
         "linhas_do_intruso=%d estado=%s pendencia=%s" % (
             quantas, r9["RUN_STATE"], r9["PENDENCIA"]))

    # ── FINISHED_AT — sem hora declarada, o relógio é o do banco ─────────
    r10 = preservar(_corrida("IT-PG-TEMPO"), [_art("t.pdf", B, "tt")],
                    ArmazemDeMentira(), _bytes_de, memoria=banco,
                    terminou_em=None)
    linha_t = banco.corrida("IT-PG-TEMPO") or {}
    caso("TEMPO_finished_at_nunca_herda_started_at",
         r10["RUN_STATE"] == "COMPLETE" and bool(linha_t.get("finished_at"))
         and linha_t.get("finished_at") != linha_t.get("started_at"),
         "started=%s finished=%s" % (linha_t.get("started_at"),
                                     linha_t.get("finished_at")))

    # ── AS TRAVAS DO ESQUEMA REAL ────────────────────────────────────────
    try:
        # A COPIA E CRIADA E LIGADA DE PROPOSITO: sem ela, a 025 tambem
        # recusaria, e este caso passaria pelo motivo errado — provando a trava
        # nova em vez da que tem no nome. Aqui so falta a corrida.
        banco.aplicar(
            "insert into public.storage_object (storage_path, media_type, "
            "bytes, sha256) values ('x/y','application/pdf',1,'%s') "
            "on conflict (storage_path) do nothing;" % ("a" * 64))
        banco.aplicar(
            "insert into public.raw_asset (run_id, storage_path, media_type, "
            "bytes, sha256, captured_at, storage_object_id) "
            "select 'NAO-EXISTE','x/y','application/pdf',1,'%s',"
            "'2026-09-08T00:00:00Z', o.id from public.storage_object o "
            "where o.storage_path = 'x/y';" % ("a" * 64))
        caso("run_id_obrigatorio_com_chave_estrangeira", False,
             "o banco ACEITOU byte sem corrida")
    except Exception as erro:                          # noqa: BLE001
        # Qualquer recusa serve, e o motor decide o tipo: o Postgres chega aqui
        # como IOError (o adaptador embrulha o stderr do psql), o SQLite como
        # IntegrityError. Apanhar so um tipo faria o ENSAIO LOCAL rebentar em
        # vez de reprovar — e um ensaio que rebenta nao ensina nada.
        caso("run_id_obrigatorio_com_chave_estrangeira", True,
             type(erro).__name__)

    linhas = banco.objetos_da_corrida("IT-PG-A")
    caso("storage_path_unico_e_sha256_nao",
         len({x["storage_path"] for x in linhas}) == len(linhas)
         and len(linhas) >= 2, "linhas=%d" % len(linhas))

    return fora


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not url:
        print("BANCO_DESCARTAVEL_URL nao definido · NOT_RUN — esta prova so corre no "
              "workflow banco-descartavel.yml, contra um Postgres que morre "
              "no fim do job.")
        # ⚠️ NOT_RUN NAO E PASS, E O CODIGO DE SAIDA TEM DE O DIZER.
        #
        # Isto devolvia 0. Sem a variavel de ambiente a prova nao aplicava
        # migration nenhuma, nao falava com banco nenhum, e saia com o codigo
        # do sucesso — de modo que um workflow a que alguem tirasse o bloco
        # `env:` ficava verde para sempre sem nunca ter tocado no Postgres.
        #
        #     UM TESTE QUE PASSA PORQUE NAO CONSEGUIU MEDIR
        #     E PIOR DO QUE TESTE NENHUM.
        #
        # Nao vira FAIL: nao ha defeito nenhum provado. Vira NOT_RUN, que e uma
        # terceira coisa, com o codigo de saida 2 — o mesmo que
        # `provas/a_autoridade_da_fonte.py` ja usa. Uma casa, um vocabulario.
        return 2
    banco = MemoriaPostgres(url)
    for caminho in (MIGRACAO, MIGRACAO_025, MIGRACAO_026):
        with open(caminho, encoding="utf-8") as f:
            banco.aplicar(f.read())
    print("migrations 001 e 025 ORIGINAIS aplicadas num Postgres 16 descartavel.")
    print("ESCOPO DA PROVA: POSTGRES16_FOUNDATION_SCHEMA_TESTED — 001 + 025.")
    print("Isto NAO e o esquema LIVE inteiro: as migrations 002-024 nao foram")
    print("aplicadas aqui, e alargar isso nao e o assunto desta correcao.")

    resultados = cenarios(banco)
    for nome, passou, detalhe in resultados:
        print("  %-4s %-46s %s" % ("PASS" if passou else "FAIL", nome, detalhe))
    reprovados = [n for n, p, _ in resultados if not p]
    # O NOME DA PROVA E O ESCOPO DELA. `POSTGRES_DESCARTAVEL` dizia onde correu
    # e calava o que cobriu — e o que cobriu e so a migration 001.
    print("\nPOSTGRES16_FOUNDATION_SCHEMA_TESTED=%s · %d caso(s)%s" % (
        "PASS" if not reprovados else "FAIL", len(resultados),
        "" if not reprovados else " · reprovados: " + ", ".join(reprovados)))
    return 1 if reprovados else 0


if __name__ == "__main__":
    sys.exit(main())
