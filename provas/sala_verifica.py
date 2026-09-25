#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SALA-VERIFICA — verificacao INDEPENDENTE da 033 na Sala real. So SELECT.

Tres perguntas, e nenhuma escreve nada:

  1  Para 15 itens da vista `sala_de_espera_atual`: a publicacao, o lugar da
     fonte, a data e o lugar do facto estao certos e com a BASE certa —
     conferidos CONTRA O BRUTO guardado (sha256 conferido), com codigo
     DIFERENTE do que os produziu:
       · data da pagina: o medidor do ponto 1 (`provas/tempo_e_lugar_medir.py`),
         e nao `executor_texto_de_html.tempo_de_publicacao` que a gravou;
       · texto: tirado outra vez do bruto (HTML sem etiquetas; PDF por
         `pdftotext`), e nao a coluna `texto` da Sala;
       · o TRECHO da base tem de estar no texto do bruto, e o VALOR no trecho.
  2  As linhas originais de `sala_de_espera` nao mudaram: as 24 colunas de
     antes da 033, byte a byte, contra o dump so-leitura de 25/09 13:58.
  3  Os gatilhos recusam UPDATE/DELETE/TRUNCATE — pela DEFINICAO (catalogo), sem
     executar escrita nenhuma.

A ligacao ao banco e forcada a so-leitura (`default_transaction_read_only`):
se o banco aceitar uma escrita nesta sessao, e porque a sessao nao e so-leitura
— e isso e verificado ANTES de tudo, com `SHOW`.

    py provas/sala_verifica.py --dump <sala-real-copia.dump> --livros "<glob;glob>"
        --raizes "<r1;r2>" --saida <out.json>
"""
import argparse
import datetime
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import contratos_de_fonte as cf  # noqa: E402
import tempo_e_lugar_medir as MEDIR  # noqa: E402

NS = "NAO SEI"
PSQL = os.environ.get("SINTONIA_PSQL_EXE") or "psql"
# os 15: um de cada caso (ver SALA-VERIFICA.md §1)
QUINZE = (1, 7, 36, 76, 77, 164, 169, 170, 174, 1331, 1333, 1406, 1415, 1450, 1466)
COLUNAS_032 = ("run_id, ordem, item_id, raw_observation_id, universo, texto, source_id, "
               "source_location, fact_location, fact_time, captured_at, admitido_por, "
               "corrida_sha256, estado_da_fila, pousado_em, consumido_em, consumido_por, "
               "estagio, published_at, observed_at, fact_time_basis, fact_location_basis, "
               "source_declared_evidence_class, fato")
MESES = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
         "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}


# ── o banco, so a ler ────────────────────────────────────────────────────
def _env():
    e = dict(os.environ)
    e["PGOPTIONS"] = "-c default_transaction_read_only=on"
    return e


def sql(consulta):
    r = subprocess.run([PSQL, "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                        "-c", consulta, os.environ["SINTONIA_SALA_DSN"]],
                       capture_output=True, text=True, encoding="utf-8", env=_env())
    if r.returncode:
        raise SystemExit("psql: %s" % r.stderr.strip()[:400])
    return r.stdout.rstrip("\n")


def copiar(consulta):
    r = subprocess.run([PSQL, "-X", "-q", "-v", "ON_ERROR_STOP=1",
                        "-c", "\\copy (%s) to stdout" % consulta,
                        os.environ["SINTONIA_SALA_DSN"]],
                       capture_output=True, env=_env())
    if r.returncode:
        raise SystemExit("psql copy: %s" % r.stderr.decode("utf-8", "replace")[:400])
    return r.stdout


# ── o bruto, e o texto dele ──────────────────────────────────────────────
def bytes_do_bruto(caminho_rel, sha, raizes):
    for raiz in raizes:
        for c in glob.glob(os.path.join(raiz, caminho_rel)):
            try:
                b = open(c, "rb").read()
            except OSError:
                continue
            if hashlib.sha256(b).hexdigest() == sha:
                return c, b
    return None, None


def texto_do_bruto(b, media):
    if "pdf" in media:
        # ⚠️ o pdftotext (xpdf 4.06) desta maquina NAO le do stdin: devolvia
        # vazio e o verificador dizia «trecho ausente do bruto». Ficheiro.
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(b)
        try:
            r = subprocess.run(["pdftotext", "-enc", "UTF-8", fh.name, "-"],
                               capture_output=True)
        finally:
            os.unlink(fh.name)
        return r.stdout.decode("utf-8", "replace")
    s = b.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return html.unescape(s)


def _norm(s):
    s = html.unescape(str(s or "")).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("«", "").replace("»", "")
    s = re.sub(r"[­]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def trechos_da_base(base):
    """Os «...» de uma base, sem as reticencias de corte."""
    return [t.strip(" .…") for t in re.findall(r"«([^»]{12,})»", base or "")]


def trecho_no_texto(trecho, texto_norm):
    t = _norm(trecho)
    if t and t in texto_norm:
        return True
    # o trecho pode ter sido cortado ou ter espacos diferentes: 3 pedacos de 6 palavras
    palavras = t.split()
    if len(palavras) < 8:
        return False
    pedacos = [" ".join(palavras[i:i + 6]) for i in (0, len(palavras) // 2 - 3, len(palavras) - 6)]
    return all(p in texto_norm for p in pedacos)


# ── as verificacoes, por campo ───────────────────────────────────────────
def _instante(v):
    try:
        d = datetime.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d.astimezone(datetime.timezone.utc) if d.tzinfo else d


def verificar_publicacao(item, b, obs, contratos):
    v, base = item["published_at"], item["published_at_basis"]
    sid = item["source_id"]
    if b is not None and "html" in item["media_type"]:
        meu = MEDIR.publicacao_html(b)          # o medidor do ponto 1, independente
        if v == NS:
            ok = not (meu and meu.get("ISO"))
            return {"OK": ok, "COMO": "HTML sem data legivel pelo medidor independente"
                    if ok else "o medidor independente ACHA data: %s" % meu}
        if not meu or not meu.get("TODAS"):
            return {"OK": False, "COMO": "a Sala tem %s e o medidor independente nao acha data" % v}
        alvo = _instante(v)
        iguais = [x for x in (meu.get("TODAS") or []) if _instante(x) == alvo
                  or str(x)[:10] == str(v)[:10]]
        familia = {"JSON-LD": "JSONLD", "meta": "META", "<time": "TIME"}
        base_ok = any(k in base and familia[k] in meu["BASE"] for k in familia)
        return {"OK": bool(iguais) and base_ok,
                "COMO": "medidor independente: %s %s; base da Sala «%s»"
                        % (meu["BASE"], meu.get("TODAS"), base[:60])}
    # PDF: a data da edicao vem do livro + contrato
    especie = (contratos.get(sid) or {}).get("DOCUMENT_DATE_KIND") or NS
    if v == NS:
        ok = not especie.upper().startswith("EDICAO") or not (obs or {}).get("SOURCE_DATE_ISO")
        return {"OK": ok, "COMO": "PDF; contrato DOCUMENT_DATE_KIND «%s»; livro SOURCE_DATE_ISO %s"
                % (especie[:40], (obs or {}).get("SOURCE_DATE_ISO"))}
    livro = (obs or {}).get("SOURCE_DATE_ISO")
    y, m, d = (v[:4], v[5:7], v[8:10])
    no_nome = bool(re.search(r"%s[-_./]%s" % (d, m), item["storage_path"]))
    return {"OK": livro == v and especie.upper().startswith("EDICAO") and "SOURCE_DATE_ISO" in base
                  and no_nome,
            "COMO": "livro %s · contrato «%s» · data no nome do bruto: %s" % (livro, especie[:30], no_nome)}


def verificar_sede(item, contratos):
    regra = (contratos.get(item["source_id"]) or {}).get("SOURCE_LOCATION_RULE") or NS
    v, base = item["source_location"], item["source_location_basis"]
    if v == NS:
        ok = regra.strip().upper().startswith(("NAO SEI", "NÃO SEI")) or regra == NS
        return {"OK": ok, "COMO": "contrato: «%s»" % regra[:60]}
    return {"OK": v in regra and base.startswith(cf.BASE_CONTRATO),
            "COMO": "contrato: «%s» · base «%s»" % (regra[:60], base[:30])}


def _dia(v):
    try:
        return datetime.date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def verificar_tempo(item, texto_norm, ev):
    v, base = item["fact_time"], item["fact_time_basis"]
    if v == NS:
        return {"OK": base.startswith(NS) or "NAO SEI" in base,
                "COMO": "NAO SEI com porque: «%s»" % base[:90]}
    trecho = ev.get("FACT_TIME_EVIDENCIA") if ev.get("FACT_TIME_EVIDENCIA") not in (
        None, NS, "NAO_SE_APLICA") else None
    trechos = [trecho] if trecho else trechos_da_base(base)
    no_bruto = [t for t in trechos if trecho_no_texto(t, texto_norm)]
    if base.startswith("RELATIVA_A_PUBLICACAO"):
        expr = ev.get("FACT_TIME_EXPRESSAO") or ""
        pub = _dia(item["published_at"])
        conta = None
        if pub and expr.lower().startswith("ieri"):
            conta = (pub - datetime.timedelta(days=1)).isoformat()
        elif pub and "settimana" in expr.lower() and "scors" in expr.lower():
            seg = pub - datetime.timedelta(days=pub.weekday() + 7)
            conta = "%s/%s" % (seg.isoformat(), (seg + datetime.timedelta(days=6)).isoformat())
        elif pub and expr.lower().startswith("oggi"):
            conta = pub.isoformat()
        return {"OK": bool(no_bruto) and conta is not None and v.startswith(conta[:10])
                      and (v == conta or v == conta[:10]),
                "COMO": "CALCULADA: «%s» a partir da publicacao %s = %s (Sala: %s) · trecho no bruto: %s"
                        % (expr, pub, conta, v, bool(no_bruto))}
    # data escrita: o valor (ou os seus numeros e mes) tem de estar no trecho
    # o leitor normaliza a forma («12 e 13 novembre» -> «12-13 novembre»): o que
    # tem de estar no trecho sao os NUMEROS e as PALAVRAS do valor
    pecas = [p for p in re.split(r"[^0-9a-zà-ù]+", _norm(v)) if p]
    no_trecho = any(all(re.search(r"(?<![0-9a-z])%s(?![0-9a-z])" % re.escape(p), _norm(t))
                        for p in pecas) for t in no_bruto)
    return {"OK": bool(no_bruto) and no_trecho,
            "COMO": "escrita: «%s» · trecho no bruto: %s · valor no trecho: %s"
                    % (v, bool(no_bruto), no_trecho)}


def verificar_lugar(item, texto_norm):
    v, base = item["fact_location"], item["fact_location_basis"]
    if v == NS:
        return {"OK": base.startswith(NS) or "NAO SEI" in base,
                "COMO": "NAO SEI com porque: «%s»" % base[:90]}
    lugares = [x.strip() for x in v.split(";")]
    blocos = [b for b in base.split(" ; ") if b.strip()]
    fora = []
    for lugar in lugares:
        prova = [t for bl in blocos for t in trechos_da_base(bl)
                 if _norm(lugar) in _norm(t) and trecho_no_texto(t, texto_norm)]
        fora.append((lugar, bool(prova)))
    return {"OK": all(ok for _, ok in fora),
            "COMO": "cada lugar no seu trecho, e o trecho no bruto: %s" % fora}


# ── 2 · as linhas originais ──────────────────────────────────────────────
def linhas_originais(dump):
    r = subprocess.run(["pg_restore", "-a", "-t", "sala_de_espera", "-f", "-", dump],
                       capture_output=True)
    # o pg_restore do Windows fecha as linhas com CRLF; sem isto, o «\.» que
    # fecha o bloco nao era reconhecido e contavam-se 8 linhas de outra seccao
    antes = r.stdout.replace(b"\r\n", b"\n").split(b"\n")
    i = next(k for k, l in enumerate(antes) if l.startswith(b"COPY public.sala_de_espera"))
    cab = antes[i].decode()
    linhas_antes = []
    for l in antes[i + 1:]:
        if l == b"\\.":
            break
        linhas_antes.append(l)
    cols_dump = [c.strip() for c in cab[cab.index("(") + 1:cab.index(")")].split(",")]
    agora = copiar("select %s from public.sala_de_espera order by run_id, ordem" % COLUNAS_032)
    linhas_agora = [l for l in agora.replace(b"\r\n", b"\n").split(b"\n") if l]
    # o dump pode estar noutra ordem de linhas: compara-se como conjuntos
    return {"COLUNAS_DO_DUMP_IGUAIS_AS_24": cols_dump == [c.strip() for c in COLUNAS_032.split(",")],
            "LINHAS_ANTES": len(linhas_antes), "LINHAS_AGORA": len(linhas_agora),
            "IGUAIS_BYTE_A_BYTE": sorted(linhas_antes) == sorted(linhas_agora),
            "SO_ANTES": len(set(linhas_antes) - set(linhas_agora)),
            "SO_AGORA": len(set(linhas_agora) - set(linhas_antes)),
            "SHA256_ANTES": hashlib.sha256(b"\n".join(sorted(linhas_antes))).hexdigest(),
            "SHA256_AGORA": hashlib.sha256(b"\n".join(sorted(linhas_agora))).hexdigest()}


# ── 3 · os gatilhos, pela definicao ──────────────────────────────────────
def gatilhos():
    defs = sql("select tgname || ' | ' || tgenabled::text || ' | ' || pg_get_triggerdef(oid) "
               "from pg_trigger where tgrelid = 'public.sala_de_espera_revisao'::regclass "
               "and not tgisinternal order by tgname").splitlines()
    corpo = sql("select prosrc from pg_proc where proname = 'sala_de_espera_revisao_so_acrescenta'")
    regras = sql("select count(*) from pg_rules where tablename = 'sala_de_espera_revisao'")
    eventos = " ".join(defs).upper()
    codigo = "\n".join(l for l in corpo.splitlines() if not l.strip().startswith("--"))
    return {
        "DEFINICOES": defs,
        "FUNCAO": corpo.strip(),
        # o Postgres escreve os eventos pela ordem dele («DELETE OR UPDATE»)
        "BEFORE_UPDATE_OR_DELETE_POR_LINHA": bool(re.search(
            r"BEFORE (DELETE OR UPDATE|UPDATE OR DELETE) ON PUBLIC\.SALA_DE_ESPERA_REVISAO "
            r"FOR EACH ROW", eventos)),
        "BEFORE_TRUNCATE_POR_INSTRUCAO": "BEFORE TRUNCATE" in eventos and "FOR EACH STATEMENT" in eventos,
        "LIGADOS_ORIGIN": all(" | O | " in d for d in defs) and len(defs) == 2,
        "A_FUNCAO_SO_LEVANTA": ("raise exception" in codigo.lower()
                                and "return" not in codigo.lower()),
        "REGRAS_NA_TABELA": regras,
    }


def main():
    ap = argparse.ArgumentParser()
    for a in ("--dump", "--livros", "--raizes", "--saida"):
        ap.add_argument(a, required=True)
    a = ap.parse_args()
    assert sql("show default_transaction_read_only") == "on", "a sessao NAO e so-leitura"

    fora = {"SESSAO_SO_LEITURA": True,
            "MIGRATION_033": sql("select resultado || ' ' || sha256 from schema_migracao "
                                 "where versao = '033'"),
            "MIGRATION_033_FICHEIRO": hashlib.sha256(open(glob.glob(os.path.join(
                RAIZ, "supabase", "migrations", "033_*.sql"))[0], "rb").read()).hexdigest()}
    vista = {x["obs"]: x for x in json.loads(sql(
        "select json_agg(json_build_object('run_id',a.run_id,'ordem',a.ordem,'obs',a.raw_observation_id,"
        "'source_id',a.source_id,'published_at',a.published_at,'published_at_basis',a.published_at_basis,"
        "'source_location',a.source_location,'source_location_basis',a.source_location_basis,"
        "'fact_time',a.fact_time,'fact_time_basis',a.fact_time_basis,'fact_location',a.fact_location,"
        "'fact_location_basis',a.fact_location_basis,'evidencia',a.tempo_lugar_evidencia,"
        "'revisoes',a.revisoes,'sha256',r.sha256,'storage_path',r.storage_path,'media_type',r.media_type)"
        " order by a.raw_observation_id, a.run_id) from sala_de_espera_atual a "
        "left join raw_asset r on r.id = a.raw_observation_id"))}
    livros = {}
    for padrao in a.livros.split(";"):
        for f in glob.glob(padrao):
            for l in open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if o.get("RAW_SHA256"):
                    livros.setdefault(o["RAW_SHA256"], o)
    contratos = cf.declarados()
    raizes = [x for x in a.raizes.split(";") if x]

    itens = []
    for obs_id in QUINZE:
        it = vista[obs_id]
        it["sha256"] = it["sha256"].strip()
        caminho, b = bytes_do_bruto(it["storage_path"], it["sha256"], raizes)
        texto = _norm(texto_do_bruto(b, it["media_type"])) if b is not None else ""
        ev = it["evidencia"] if isinstance(it["evidencia"], dict) else {}
        obs = livros.get(it["sha256"])
        r = {"OBS": obs_id, "SOURCE_ID": it["source_id"], "RUN_ID": it["run_id"],
             "ORDEM": it["ordem"], "REVISOES": it["revisoes"],
             "BRUTO": caminho or "NAO ACHADO (sha)", "LETRAS_DO_BRUTO": len(texto),
             "VALORES": {k: it[k] for k in ("published_at", "source_location", "fact_time",
                                            "fact_location")},
             "PUBLICACAO": verificar_publicacao(it, b, obs, contratos),
             "LOCAL_DA_FONTE": verificar_sede(it, contratos),
             "DATA_DO_FATO": verificar_tempo(it, texto, ev),
             "LOCAL_DO_FATO": verificar_lugar(it, texto)}
        itens.append(r)
    fora["ITENS"] = itens
    fora["RESUMO_MECANICO"] = {c: "%d/%d" % (sum(1 for x in itens if x[c]["OK"]), len(itens))
                               for c in ("PUBLICACAO", "LOCAL_DA_FONTE", "DATA_DO_FATO",
                                         "LOCAL_DO_FATO")}
    fora["LINHAS_ORIGINAIS"] = linhas_originais(a.dump)
    fora["GATILHOS"] = gatilhos()
    fora["VISTA_LE_A_ULTIMA"] = sql(
        "select (length(pg_get_viewdef('public.sala_de_espera_atual'::regclass)) - "
        "length(replace(lower(pg_get_viewdef('public.sala_de_espera_atual'::regclass)), "
        "'order by r.revisao desc', ''))) / length('order by r.revisao desc')")
    fora["REVISOES"] = {
        "TOTAL": sql("select count(*) from sala_de_espera_revisao"),
        "POR_VERSAO": sql("select string_agg(versao_do_extrator || '=' || n, ' ') from "
                          "(select versao_do_extrator, count(*) n from sala_de_espera_revisao "
                          "group by 1 order by 1) x"),
        "SEQUENCIAS_COM_BURACO": sql(
            "select count(*) from (select run_id, ordem, campo, max(revisao) m, count(*) n "
            "from sala_de_espera_revisao group by 1,2,3) x where m <> n"),
        "SEM_LINHA_NA_SALA": sql(
            "select count(*) from sala_de_espera_revisao r left join sala_de_espera s "
            "using (run_id, ordem) where s.run_id is null")}
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: fora[k] for k in ("MIGRATION_033", "MIGRATION_033_FICHEIRO",
                                           "RESUMO_MECANICO", "LINHAS_ORIGINAIS",
                                           "VISTA_LE_A_ULTIMA", "REVISOES")},
                     ensure_ascii=False, indent=1))
    g = fora["GATILHOS"]
    print(json.dumps({k: g[k] for k in g if k not in ("FUNCAO",)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
