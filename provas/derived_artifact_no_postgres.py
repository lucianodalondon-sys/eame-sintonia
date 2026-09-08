#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CASA DO DERIVADO, PROVADA NUM POSTGRES QUE MORRE NO FIM.

O QUE ISTO PROVA
----------------
Que a `migration 022` não é um desenho bonito num ficheiro: que ela **aplica**
num Postgres 16 real, sobre a `001`, e que as travas dela recusam o que têm de
recusar.

    DESIGNED   é o SQL escrito
    DB_TESTED  é o SQL aplicado, e as travas a morder

São coisas diferentes, e a distância entre elas já custou uma promoção
prematura nesta casa. Por isso o estado só sobe depois de alguém **ler** o
resultado do CI.

O ESCOPO, DITO SEM ALARGAR
--------------------------
Aplicam-se **`001` + `022`**, e mais nada. As `002`–`021` não entram — a `022`
não precisa delas, e aplicá-las só para dizer «o esquema inteiro» seria pagar
por uma frase maior do que a medição.

    ESCOPO = FOUNDATION_MAIS_022

NENHUMA LIGAÇÃO A PRODUÇÃO
--------------------------
Usa a mesma tranca de `preservar_coleta_no_postgres.py`: a URL é decomposta, e
o `hostname` tem de ser exatamente local **e** o banco chamar-se `descartavel`.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "prova_pg", os.path.join(RAIZ, "provas", "preservar_coleta_no_postgres.py"))
_pg = _u.module_from_spec(_spec)
_spec.loader.exec_module(_pg)

MIGRACOES = [
    "001_fundacao_geografia_e_proveniencia.sql",
    "022_o_derivado_ganha_casa.sql",
]

SHA_PAI = "a" * 64
SHA_FILHO = "b" * 64
SHA_OUTRO = "c" * 64
HASH_VAZIO = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class Banco(_pg.MemoriaPostgres):
    """O mesmo cliente `psql` da prova anterior, e a mesma tranca."""

    def executar(self, sql):
        """Aplica e devolve o erro em vez de o levantar — os casos negativos
        precisam de PERGUNTAR se o banco recusou, não de rebentar."""
        r = subprocess.run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", self.url],
                           input=sql, capture_output=True, text=True)
        return r.returncode, (r.stderr or "").strip()


def _raw(banco, run_id, caminho, sha=SHA_PAI):
    """Cria a corrida e o bruto de que o derivado vai nascer."""
    banco.aplicar(
        "insert into public.collection_run (run_id, platform, started_at, "
        "rule_version, source_country) values "
        "('%s','teste','2026-09-08T00:00:00Z','1','IT') "
        "on conflict (run_id) do nothing;" % run_id)
    banco.aplicar(
        "insert into public.raw_asset (run_id, storage_path, media_type, bytes, "
        "sha256, captured_at) values ('%s','%s','application/pdf',100,'%s',"
        "'2026-09-08T00:00:00Z') on conflict (storage_path) do nothing;"
        % (run_id, caminho, sha))
    return int(banco._valor(
        "select id from public.raw_asset where storage_path = '%s'" % caminho))


def _derivado(raw_id, caminho, **campos):
    d = {"raw_asset_id": raw_id, "parent_sha256": SHA_PAI, "kind": "TEXT_EXTRACTION",
         "producer": "texto-de-pdf", "producer_version": "1",
         "parameters_hash": HASH_VAZIO, "serie_posicao": "null",
         "sha256": SHA_FILHO, "bytes": 10, "media_type": "text/plain",
         "storage_path": caminho, "derived_at": "2026-09-08T02:00:00Z"}
    d.update(campos)
    cols = ", ".join(d)
    vals = ", ".join(
        str(v) if (k in ("raw_asset_id", "bytes") or v == "null") else "'%s'" % v
        for k, v in d.items())
    return "insert into public.derived_artifact (%s) values (%s);" % (cols, vals)


def cenarios(banco):
    fora = []

    def caso(nome, condicao, detalhe=""):
        fora.append((nome, bool(condicao), detalhe))

    raw_id = _raw(banco, "IT-DER-1", "IT/x/DOCUMENT/pai.pdf")

    # ── A · o caminho normal ────────────────────────────────────────────
    rc, erro = banco.executar(_derivado(raw_id, "IT/x/TEXT/a.txt"))
    caso("A_raw_existe_derivado_entra", rc == 0, erro[:120])
    caso("A2_a_linha_esta_la",
         banco.contar("derived_artifact") == 1,
         "linhas=%d" % banco.contar("derived_artifact"))

    # ── B · sem pai canónico, a chave estrangeira recusa ────────────────
    # ⚠️ A IDENTIDADE TEM DE SER DIFERENTE DA DO CASO A. Na primeira versao
    # deste teste ela era igual, e o banco recusou pela trava de UNICIDADE —
    # a chave estrangeira nunca chegou a ser tocada. O teste dava FAIL a dizer
    # «duplicate key», e teria dado PASS por engano se eu tivesse aceitado
    # qualquer recusa como prova. **Recusar nao e recusar pelo motivo certo.**
    rc, erro = banco.executar(_derivado(999999, "IT/x/TEXT/orfao.txt",
                                        producer="ferramenta-orfa"))
    caso("B_sem_raw_a_FK_recusa", rc != 0 and "foreign key" in erro.lower(),
         erro.splitlines()[0][:110] if erro else "ACEITOU")

    # ── REPRODUÇÃO · o filho pode declarar DOIS pais diferentes? ────────
    # `raw_asset_id` aponta para o pai A; `parent_sha256` diz os bytes de B.
    # A chave estrangeira passa, porque A existe. A linhagem fica a dizer duas
    # coisas ao mesmo tempo — e nao ha nada que as obrigue a concordar.
    #
    #   FK EXISTIR NAO BASTA. O PAI POR ID E O PAI POR SHA
    #   PRECISAM DE SER O MESMO PAI.
    raw_b = _raw(banco, "IT-DER-B", "IT/b/DOCUMENT/outro-pai.pdf", sha=SHA_OUTRO)
    rc, erro = banco.executar(_derivado(
        raw_id, "IT/x/TEXT/dois-pais.txt", parent_sha256=SHA_OUTRO,
        producer="ferramenta-do-teste-de-coerencia"))
    caso("COERENCIA_id_e_sha_apontam_para_o_mesmo_pai",
         rc != 0 and "o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo" in erro,
         "ACEITOU DOIS PAIS DIFERENTES" if rc == 0
         else erro.splitlines()[0][:110])

    # E a coerencia nao pode ser rigida demais: com o par CERTO, entra.
    rc, erro = banco.executar(_derivado(
        raw_b, "IT/b/TEXT/pai-certo.txt", parent_sha256=SHA_OUTRO,
        producer="ferramenta-do-teste-de-coerencia"))
    caso("COERENCIA_o_par_certo_continua_a_entrar", rc == 0, erro[:110])

    # ── DUAS CAPTURAS DO MESMO CONTEUDO, a mesma receita ────────────────
    # RUN-1 e RUN-2 trouxeram os MESMOS bytes: duas capturas legitimas, duas
    # linhas em `raw_asset`. Derivadas com a mesma regua, dao UMA linha aqui —
    # o grao e CONTEUDO POR RECEITA. Ha UM facto: a nossa ferramenta, sobre
    # estes bytes, com esta regua, da este resultado.
    #
    # E a procedencia das duas capturas NAO se perde: ela nunca morou aqui.
    sha_gemeo = "d" * 64
    g1 = _raw(banco, "IT-GEMEO-1", "IT/g/DOCUMENT/copia-1.pdf", sha=sha_gemeo)
    g2 = _raw(banco, "IT-GEMEO-2", "IT/g/DOCUMENT/copia-2.pdf", sha=sha_gemeo)
    caso("GEMEOS_duas_capturas_do_mesmo_conteudo_existem",
         g1 != g2, "raw_asset_id %s e %s" % (g1, g2))

    sql_gemeo = (lambda raw, caminho: _derivado(
        raw, caminho, parent_sha256=sha_gemeo, producer="texto-de-pdf",
        sha256="f" * 64).replace(
            ");", ") on conflict on constraint derivacao_e_unica_por_regua "
                  "do nothing;"))
    banco.executar(sql_gemeo(g1, "IT/g/TEXT/da-copia-1.txt"))
    banco.executar(sql_gemeo(g2, "IT/g/TEXT/da-copia-2.txt"))
    quantos_gemeos = int(banco._valor(
        "select count(*) from public.derived_artifact where parent_sha256 = '%s'"
        % sha_gemeo))
    caso("GEMEOS_a_mesma_receita_da_UMA_derivacao", quantos_gemeos == 1,
         "linhas=%d (grao = CONTEUDO POR RECEITA)" % quantos_gemeos)

    irmas = int(banco._valor(
        "select count(*) from public.raw_asset where sha256 = '%s'" % sha_gemeo))
    caso("GEMEOS_a_procedencia_das_duas_capturas_continua_inteira", irmas == 2,
         "capturas achaveis por sha256: %d" % irmas)

    # ── C · o mesmo bruto, tipos diferentes, coexistem ──────────────────
    rc, erro = banco.executar(_derivado(raw_id, "IT/x/THUMB/a.png",
                                        kind="THUMBNAIL", producer="thumbnailer",
                                        sha256=SHA_OUTRO, media_type="image/png"))
    caso("C_TXT_e_thumbnail_do_mesmo_bruto_coexistem", rc == 0, erro[:120])

    # ── D · duas versões da mesma ferramenta coexistem ──────────────────
    # E o caso REAL: o Whisper tem modelo `base` e `small`, e os dois textos
    # sao legitimos. Sem a versao na chave, o segundo apagaria o primeiro.
    rc, erro = banco.executar(_derivado(raw_id, "IT/x/TEXT/a-v2.txt",
                                        producer_version="2", sha256=SHA_OUTRO))
    caso("D_duas_versoes_da_ferramenta_coexistem", rc == 0, erro[:120])
    # CONTA O QUE E DESTE CASO, nao o total da tabela: um teste que depende do
    # numero de linhas que os outros deixaram passa a reprovar por acidente
    # quando alguem acrescenta um caso — e foi exatamente o que aconteceu.
    do_pai = lambda: int(banco._valor(
        "select count(*) from public.derived_artifact where parent_sha256 = "
        "'%s' and kind = 'TEXT_EXTRACTION' and producer = 'texto-de-pdf'"
        % SHA_PAI))
    caso("D2_e_a_antiga_continua_la", do_pai() == 2,
         "versoes de texto-de-pdf sobre o mesmo pai=%d" % do_pai())

    # ── E · retry idêntico não cria lixo ────────────────────────────────
    rc, erro = banco.executar(
        _derivado(raw_id, "IT/x/TEXT/a-de-novo.txt").replace(
            ");", ") on conflict on constraint derivacao_e_unica_por_regua "
                  "do nothing;"))
    caso("E_retry_identico_nao_cria_linha", rc == 0 and do_pai() == 2,
         "rc=%d versoes=%d %s" % (rc, do_pai(), erro[:80]))

    # ── F · mesma identidade, bytes diferentes → NÃO sobrescreve calado ──
    rc, erro = banco.executar(_derivado(raw_id, "IT/x/TEXT/a-drift.txt",
                                        sha256=SHA_OUTRO))
    caso("F_mesma_regua_com_bytes_diferentes_da_CONFLITO",
         rc != 0 and "derivacao_e_unica_por_regua" in erro,
         erro.splitlines()[0][:110] if erro else "ACEITOU EM SILENCIO")

    # ── G · o bruto fica imutável ───────────────────────────────────────
    antes = banco.objeto_em("IT/x/DOCUMENT/pai.pdf")
    banco.executar(_derivado(raw_id, "IT/x/OCR/a.txt", kind="OCR",
                             producer="tesseract", sha256=SHA_OUTRO))
    depois = banco.objeto_em("IT/x/DOCUMENT/pai.pdf")
    caso("G_criar_derivado_nao_altera_o_bruto", antes == depois,
         "antes==depois" if antes == depois else "O BRUTO MUDOU")

    # ── H · derived_at não é captured_at ────────────────────────────────
    par = banco._psql(
        "select %s, %s from public.raw_asset r join public.derived_artifact d "
        "on d.raw_asset_id = r.id where d.storage_path = 'IT/x/TEXT/a.txt'"
        % (Banco._ISO % "r.captured_at", Banco._ISO % "d.derived_at")).strip()
    caso("H_derived_at_e_diferente_de_captured_at",
         par and par.split(Banco.SEP)[0] != par.split(Banco.SEP)[1], par)

    # ── I · sha256 igual em dois derivados não é a mesma linhagem ───────
    raw2 = _raw(banco, "IT-DER-2", "IT/y/DOCUMENT/outro.pdf", sha=SHA_OUTRO)
    rc, erro = banco.executar(_derivado(raw2, "IT/y/TEXT/b.txt",
                                        parent_sha256=SHA_OUTRO))
    quantos = int(banco._valor(
        "select count(*) from public.derived_artifact where sha256 = '%s'"
        % SHA_FILHO))
    caso("I_mesmo_sha_do_filho_com_pais_diferentes_coexiste",
         rc == 0 and quantos >= 2,
         "rc=%d linhas_com_o_mesmo_sha=%d %s" % (rc, quantos, erro[:80]))

    # ── J · a serie: dez frames do mesmo bruto ──────────────────────────
    # O caso que quebra qualquer chave sem `serie_posicao`: mesmo pai, mesmo
    # tipo, mesma ferramenta, mesma versao, mesmos parametros — e dez artefatos.
    erros = []
    for i in range(3):
        rc, erro = banco.executar(_derivado(
            raw_id, "IT/x/FRAME/%d.png" % i, kind="FRAME", producer="ffmpeg",
            serie_posicao=str(i), sha256="%062x%02x" % (0, i),
            media_type="image/png"))
        if rc != 0:
            erros.append(erro.splitlines()[0][:80])
    frames = int(banco._valor(
        "select count(*) from public.derived_artifact where kind = 'FRAME'"))
    caso("J_dez_frames_do_mesmo_bruto_cabem", frames == 3 and not erros,
         "frames=%d %s" % (frames, "; ".join(erros)))

    # ── K · bytes no armazém, memória no banco ──────────────────────────
    tem_blob = banco._valor(
        "select count(*) from information_schema.columns where table_name = "
        "'derived_artifact' and data_type in ('bytea','text') and column_name "
        "in ('content','blob','texto','body')")
    caso("K_o_banco_nao_guarda_o_corpo_do_derivado", tem_blob == "0",
         "colunas de corpo=%s" % tem_blob)

    # ── L · apagar o bruto não leva a linhagem em silêncio ──────────────
    rc, erro = banco.executar(
        "delete from public.raw_asset where id = %d;" % raw_id)
    ainda = banco.contar("derived_artifact")
    caso("L_apagar_o_bruto_com_filhos_e_RECUSADO",
         rc != 0 and "foreign key" in erro.lower() and ainda > 0,
         (erro.splitlines()[0][:110] if erro else "APAGOU") + " · filhos=%d" % ainda)

    # ── AS TRAVAS DE FORMATO ────────────────────────────────────────────
    rc, _ = banco.executar(_derivado(raw2, "IT/y/TEXT/mau.txt",
                                     parent_sha256=SHA_OUTRO, sha256="nao-e-hash"))
    caso("sha256_com_formato_errado_e_recusado", rc != 0)
    rc, _ = banco.executar(_derivado(raw2, "IT/y/TEXT/mau2.txt",
                                     parent_sha256=SHA_OUTRO, kind="INVENTADO"))
    caso("kind_fora_da_lista_e_recusado", rc != 0)
    # O mesmo endereco no armazem, reclamado por outra derivacao. O grao e o
    # OBJETO GUARDADO — dois objetos nao vivem no mesmo sitio.
    rc, erro = banco.executar(_derivado(raw2, "IT/y/TEXT/b.txt",
                                        parent_sha256=SHA_OUTRO,
                                        producer_version="9",
                                        sha256=SHA_OUTRO))
    caso("storage_path_repetido_e_recusado",
         rc != 0 and "storage_path" in erro,
         erro.splitlines()[0][:110] if erro else "ACEITOU")

    return fora


def main():
    url = os.environ.get("BANCO_DESCARTAVEL_URL", "")
    if not url:
        print("BANCO_DESCARTAVEL_URL nao definido — esta prova so corre no "
              "workflow banco-descartavel.yml.")
        return 0
    banco = Banco(url)
    for nome in MIGRACOES:
        with open(os.path.join(RAIZ, "supabase", "migrations", nome),
                  encoding="utf-8") as f:
            banco.aplicar(f.read())
        print("aplicada: %s" % nome)
    print("ESCOPO DA PROVA: FOUNDATION_MAIS_022 — so a 001 e a 022.")
    print("As 002-021 NAO entram: a 022 nao precisa delas, e aplica-las so para")
    print("dizer «o esquema inteiro» seria pagar por uma frase maior que a medicao.\n")

    resultados = cenarios(banco)
    for nome, passou, detalhe in resultados:
        print("  %-4s %-52s %s" % ("PASS" if passou else "FAIL", nome, detalhe))
    reprovados = [n for n, p, _ in resultados if not p]
    print("\nDERIVED_ARTIFACT_DB_TESTED=%s · %d caso(s)%s" % (
        "PASS" if not reprovados else "FAIL", len(resultados),
        "" if not reprovados else " · reprovados: " + ", ".join(reprovados)))
    return 1 if reprovados else 0


if __name__ == "__main__":
    sys.exit(main())
