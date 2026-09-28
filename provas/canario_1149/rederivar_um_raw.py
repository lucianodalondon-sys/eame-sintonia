#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RE-DERIVAR UM RAW SÓ, NUMA CÓPIA, PELA ESTRADA CANÓNICA — o canário 1149 (D131/D132).

    mesma página original -> derivação corrigida -> comparação -> o mesmo item reprocessado -> Sala

    py provas/canario_1149/rederivar_um_raw.py --dsn <copia> --raw-id 2272 --armazem <raiz> \
        --saida <pasta> [--aplicar] [--armazem-da-copia <pasta>] [--universo T5] [--livros "<glob;glob>"]

ESTE FICHEIRO NÃO DERIVA, NÃO JULGA E NÃO POUSA NADA. Ele chama, pela ordem da coleta real
(`orquestrador.correr`, que foi quem produziu o `derived:1149`), os donos que já existem:

    coleta/ingresso.unidades_para_a_derivacao   a unidade, a partir da linha REAL de raw_asset
    coleta/italy_executor.tempo_e_lugar         o recado de tempo e lugar da observação (DA-9)
    coleta/derivacao_forward.correr             executor por unidade -> executor_texto_de_html
                                                (limpar/3, versão 4) -> guarda/preservar_derivado
    orquestrador.pela_estruturacao              guarda/preservar_documento (documento_estruturado)
    orquestrador.item_documental_para_a_porta   o tradutor da rota documental (lê o fato do TEXTO)
    admissao.decidir / pronto_para_inteligencia a porta e o contrato READY
    sala_de_espera.pousar(armazem, extratores)  a Sala, com o decisor de versões (036) ligado

⚠️ PORQUE NÃO `rota_forward_documento.levar_a_espera()`: ela monta o READY com o tradutor da
rota M2 (`item_para_a_porta`, que NÃO lê o fato do texto) — o 1149 não veio por ali. Pousar por
ela daria um READY diferente do item que a porta julgou. O que se usa são os MESMOS três donos
que ela chama (decidir · pronto_para_inteligencia · pousar), com o item da rota documental.

O QUE ESTE RUNNER ACRESCENTA (e só isto): a trava de cópia, a corrida de reprocesso, a
leitura do antes, a previsão sem escrita, e o relatório. Nenhuma régua nova.

⚠️ A TRAVA (antes de abrir qualquer ligação):
    · a morada tem de ser local e sem desvio (`guarda/banco_descartavel` ou
      `guarda/banco_operacional` — os donos da pergunta);
    · a porta tem de estar ESCRITA e não ser a do vivo (5432, e 54330 = a Sala real);
    · o banco tem de ter a MARCA DE CÓPIA: `public._copia_descartavel` com ≥ 1 linha. Este
      runner NUNCA a cria — quem fez a cópia é que a marca (ver CANARIO-1149-REDERIVAR.md).
Sem as três, sai com código 2 e não escreve nada.

SEM `--aplicar`: só leituras (`select`) no banco e cálculos puros; o recibo diz o que FARIA.
COM `--aplicar`: escreve SÓ na cópia (collection_run, derived_artifact, documento_estruturado,
etapa_da_corrida e o que a Sala decidir) e no ARMAZÉM DA CÓPIA (`--armazem-da-copia`, por omissão
`<saida>/armazem-da-copia`: o RAW copiado, com o sha256 batido, e o derivado novo). O `--armazem`
original só é LIDO — um ficheiro.

⚠️ O ARMAZÉM DA CÓPIA ANDA COM A CÓPIA DO BANCO. Medido no teste: a 2.ª corrida com outra
`--saida` encontrou a linha do derivado v4 no banco e os bytes noutro sítio — o dono da escrita
respondeu STORAGE_MISSING («NAO e REUSED: nao ha o que reaproveitar»), e tinha razão. Quem corre
duas vezes na mesma cópia passa o MESMO `--armazem-da-copia`.

⚠️ A SALA PODE RECUSAR A LINHA NOVA, E ISSO É CANÓNICO. O RAW 2272 é o MESMO documento que já
lá está. A DEDUP-DOC (`sala_de_espera.pousar`) funde por documento; o decisor de versões (036)
responde IGUAL quando os bytes do RAW são os mesmos. O runner REPORTA; não força, não apaga, não
duplica. Se o RAW não tiver identidade provada (FORWARD_IDENTIFIED) e já houver linha dele no
universo, `pousar` gravaria uma 2.ª linha do MESMO bruto — o runner PARA antes de a chamar.
"""
import sys

sys.dont_write_bytecode = True

import socket  # noqa: E402


class _SemRede(socket.socket):
    def __init__(self, *a, **k):
        raise RuntimeError("REDE PROIBIDA: o reprocesso do canario e sem rede")

import argparse  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import uuid  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from urllib.parse import urlparse  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

from guarda.banco_descartavel import (  # noqa: E402
    AMBIENTE_QUE_MUDA_O_DESTINO, morada_sem_segredo, porque_nao_e_descartavel)
from guarda.banco_operacional import porque_nao_e_operacional  # noqa: E402

#: As portas do vivo. 5432 = a porta por omissão (uma morada sem porta cai nela);
#: 54330 = a Sala real (`scripts/micro_coleta/ensaio_offline.py`, `guarda/preservar_coleta.py`).
PORTAS_DO_VIVO = (5432, 54330)
#: A marca que só a cópia tem. Quem restaura o dump marca; este runner só lê.
MARCA_DE_COPIA = "public._copia_descartavel"
#: As variáveis que fariam um dono ligar-se a OUTRO banco que não a cópia.
COFRES_DE_OUTROS = ("SUPABASE_DB_URL", "SINTONIA_COLLECTION_DSN", "BANCO_DESCARTAVEL_URL")

MOTIVO = "REPROCESSO_CANARIO_1149"
ATOR = "provas/canario_1149/rederivar_um_raw.py"
#: As tabelas cujo tamanho prova o que se escreveu (antes x depois).
TABELAS = ("collection_run", "raw_asset", "storage_object", "derived_artifact",
           "documento_estruturado", "etapa_da_corrida", "sala_de_espera",
           "sala_de_espera_versao", "sala_de_espera_revisao")
NAO_SEI = "NAO SEI"


class NaoECopia(Exception):
    """O DSN não prova ser uma cópia descartável. Nada foi escrito."""


class Parado(Exception):
    """A estrada canónica não tem caminho para o passo seguinte. Diz-se, não se força."""


# ═════════════════════════════════════════════════════════════════════════
# A TRAVA
# ═════════════════════════════════════════════════════════════════════════

def porque_nao_e_copia(dsn) -> str:
    """O motivo da recusa PELA MORADA, ou `""`. Não abre ligação."""
    local = porque_nao_e_descartavel(dsn)
    if local:
        oper = porque_nao_e_operacional(dsn)
        if oper:
            return "morada recusada pelos donos (descartavel: %s; operacional: %s)" % (local, oper)
    porta = urlparse(dsn.strip()).port
    if porta is None:
        return "porta nao escrita: uma morada sem porta liga-se a 5432, a do vivo"
    if porta in PORTAS_DO_VIVO:
        return "porta %d e a do vivo (%s)" % (porta, ", ".join(map(str, PORTAS_DO_VIVO)))
    return ""


def isolar_o_ambiente(dsn):
    """Este processo passa a só conhecer a cópia. → as variáveis retiradas."""
    retiradas = [n for n in AMBIENTE_QUE_MUDA_O_DESTINO + COFRES_DE_OUTROS if n in os.environ]
    for n in retiradas:
        os.environ.pop(n, None)
    os.environ["SINTONIA_SALA_BACKEND"] = "POSTGRES"
    os.environ["SINTONIA_SALA_DSN"] = dsn
    return retiradas


def conferir_marca(banco):
    """A marca de cópia, lida. Levanta `NaoECopia` sem ela."""
    r = banco.executa("select to_regclass('%s') is not null" % MARCA_DE_COPIA)
    if not r or r[0][0] != "t":
        raise NaoECopia("o banco nao tem a marca de copia %s: este runner so corre numa copia "
                        "marcada por quem a restaurou" % MARCA_DE_COPIA)
    n = int(banco.executa("select count(*) from %s" % MARCA_DE_COPIA)[0][0])
    if n < 1:
        raise NaoECopia("%s existe e esta vazia: marca sem linha nao e marca" % MARCA_DE_COPIA)
    return n


# ═════════════════════════════════════════════════════════════════════════
# LEITURAS (só `select`)
# ═════════════════════════════════════════════════════════════════════════

def _lit(v):
    import sala_de_espera as espera                     # noqa: PLC0415 — o escape do dono
    return espera._lit(v)


COLS_RAW = ("id", "run_id", "storage_path", "media_type", "bytes", "sha256", "captured_at",
            "source_url", "source_id", "document_key", "identity_state")


def ler_raw(banco, raw_id):
    linhas = banco.executa(
        "select %s from public.raw_asset where id = %d"
        % (", ".join("coalesce(%s::text, '')" % c for c in COLS_RAW), int(raw_id)))
    if not linhas:
        return None
    return dict(zip(COLS_RAW, linhas[0]))


def fotografia(banco):
    """`{tabela: linhas}` — `NAO SEI` para a que não existe nesta cópia."""
    fora = {}
    for t in TABELAS:
        existe = banco.executa("select to_regclass('public.%s') is not null" % t)[0][0] == "t"
        fora[t] = int(banco.executa("select count(*) from public.%s" % t)[0][0]) if existe else NAO_SEI
    return fora


def derivados_do_raw(banco, raw_id):
    cols = ("id", "producer", "producer_version", "parameters_hash", "sha256", "storage_path")
    return [dict(zip(cols, l)) for l in banco.executa(
        "select %s from public.derived_artifact where raw_asset_id = %d order by id"
        % (", ".join("coalesce(%s::text, '')" % c for c in cols), int(raw_id)))]


def linhas_do_documento(banco, raw):
    """As linhas da Sala do MESMO bruto, ou do mesmo documento (se a identidade estiver provada).

    É a pergunta que a DEDUP-DOC faz, feita aqui só para LER e mostrar — a decisão continua a ser
    tomada por `pousar`, dentro da transação dela."""
    cond = "s.raw_observation_id = %d" % int(raw["id"])
    if raw["identity_state"] == "FORWARD_IDENTIFIED":
        cond += (" or s.raw_observation_id in (select r.id from public.raw_asset r where "
                 "r.identity_state = 'FORWARD_IDENTIFIED' and r.source_id = %s and "
                 "r.document_key = %s)" % (_lit(raw["source_id"]), _lit(raw["document_key"])))
    cols = ("run_id", "ordem", "item_id", "raw_observation_id", "universo", "estado_da_fila")
    return [dict(zip(cols, l)) for l in banco.executa(
        "select s.run_id, s.ordem::text, s.item_id, coalesce(s.raw_observation_id::text, ''), "
        "s.universo, s.estado_da_fila from public.sala_de_espera s where %s "
        "order by s.pousado_em, s.run_id, s.ordem" % cond)]


def versoes_de(banco, run_id, ordem):
    if banco.executa("select to_regclass('public.sala_de_espera_versao') is not null")[0][0] != "t":
        return NAO_SEI
    cols = ("versao", "item_id", "veio_da_corrida", "como_se_comparou")
    return [dict(zip(cols, l)) for l in banco.executa(
        "select versao::text, item_id, veio_da_corrida, coalesce(como_se_comparou, '') "
        "from public.sala_de_espera_versao where run_id = %s and ordem = %d order by versao"
        % (_lit(run_id), int(ordem)))]


def linha_atual(run_id, ordem):
    """A linha como a Intelligence a lê (vista `sala_de_espera_atual`), pelo dono da Sala."""
    import sala_de_espera as espera                     # noqa: PLC0415
    lida = espera.ler_atual(run_id) or {"ITENS": []}
    return next((u for u in lida["ITENS"] if u["ORDEM"] == int(ordem)), None)


# ═════════════════════════════════════════════════════════════════════════
# O QUE OS DONOS DIZEM (puro: nenhuma escrita)
# ═════════════════════════════════════════════════════════════════════════

def bytes_do_raw(armazem_original, raw):
    """Os bytes do RAW, só com o sha256 da linha. Nunca outro ficheiro."""
    caminho = os.path.join(armazem_original, raw["storage_path"])
    if not os.path.isfile(caminho):
        # a raiz declarada pode ser a pasta ACIMA de `XX/` (armazem operacional)
        achados = [c for c in glob.glob(os.path.join(armazem_original, "**",
                                                     os.path.basename(raw["storage_path"])),
                                        recursive=True)]
        caminho = next((c for c in achados if c.replace("\\", "/").endswith(
            raw["storage_path"].replace("\\", "/"))), None)
    if not caminho:
        raise Parado("o RAW %s nao esta em --armazem (%s)" % (raw["id"], raw["storage_path"]))
    dados = open(caminho, "rb").read()
    if hashlib.sha256(dados).hexdigest() != raw["sha256"]:
        raise Parado("o ficheiro do RAW %s no armazem nao tem o sha256 da linha" % raw["id"])
    return dados, caminho


def observacao_do_livro(padroes, sha):
    """A observação do coletor com este RAW_SHA256, pelo dono (`reprocessar_tempo_lugar`)."""
    if not padroes:
        return None
    import reprocessar_tempo_lugar as rtl               # noqa: PLC0415
    return rtl.livros_por_sha([p for p in padroes.split(";") if p]).get(sha)


def texto_em_resumo(texto, primeiras=40):
    import fato_do_texto as FT                           # noqa: PLC0415
    linhas = texto.split("\n") if texto else []
    return {"LINHAS": len(linhas), "CARACTERES": len(texto or ""),
            "CORPO_CARACTERES": len(FT.corpo(texto or "")),
            "PRIMEIRAS_%d_LINHAS" % primeiras: linhas[:primeiras]}


def item_para_a_porta(texto, raw, derivado_id, tempo_e_lugar, retrato):
    """O item que a rota documental leva à porta — pelo tradutor dela, sem mexer em nada."""
    import orquestrador as ORQ                          # noqa: PLC0415
    est = {"SOURCE_ID": raw["source_id"] or None, "TEXTO": texto,
           "DERIVED_ARTIFACT_ID": derivado_id, "RAW_ASSET_ID": int(raw["id"]),
           "PARENT_SHA256": raw["sha256"], "CAPTURED_AT": raw["captured_at"] or None,
           "TEMPO_E_LUGAR": dict(tempo_e_lugar or {}), "RETRATO_DO_DETECTOR": retrato,
           "SOURCE_URL": raw["source_url"] or None}
    return ORQ.item_documental_para_a_porta(est, source_id=raw["source_id"] or None)


def a_decisao(decisao, universo):
    import admissao as adm                               # noqa: PLC0415
    ev = dict(decisao.evidencia or {})
    return {"UNIVERSO": universo, "RESULTADO": decisao.resultado, "REGRA": decisao.regra,
            "MOTIVO": decisao.motivo, "VERSAO_DA_REGUA": decisao.versao,
            "PALAVRAS": ev.get("palavras", NAO_SEI),
            "A_REGUA": {"PERGUNTAS_DO_UNIVERSO": adm.PERGUNTAS_DO_UNIVERSO.get(universo, []),
                        "PALAVRA_INTEIRA": universo in adm.PALAVRA_INTEIRA,
                        "SINAIS_MINIMOS": adm.SINAIS_MINIMOS,
                        "DONO": "admissao/admissao.py::_do_universo"},
            "EVIDENCIA": ev}


def campos_do_fato(u):
    """FACT_TIME/FACT_LOCATION/PROBLEMA/CULTURA como a peça dona os deu. Só leitura."""
    if not u:
        return NAO_SEI
    j = u.get("JANELA_DECLARADA") or {}
    if isinstance(j, str):
        j = json.loads(j)
    prob, cult = j.get("PROBLEMA") or {}, j.get("CULTURA") or {}
    return {"PUBLISHED_AT": u.get("PUBLISHED_AT"), "PUBLISHED_AT_BASIS": u.get("PUBLISHED_AT_BASIS"),
            "PUBLISHED_AT_PRECISION": (u.get("TEMPO_LUGAR_EVIDENCIA") or {}).get(
                "PUBLISHED_AT_PRECISION", NAO_SEI),
            "FACT_TIME": u.get("FACT_TIME"), "FACT_TIME_BASIS": u.get("FACT_TIME_BASIS"),
            "FACT_LOCATION": u.get("FACT_LOCATION"),
            "FACT_LOCATION_BASIS": u.get("FACT_LOCATION_BASIS"),
            "PROBLEMA": {"VALOR": prob.get("VALOR", NAO_SEI), "PORQUE": prob.get("PORQUE"),
                         "CANDIDATOS": [c.get("NOME") for c in prob.get("CANDIDATOS") or []],
                         "DONO": prob.get("LEITOR") or prob.get("CONTRATO")},
            "CULTURA": {"VALOR": cult.get("VALOR", NAO_SEI), "VEIO_DE": cult.get("VEIO_DE")}}


def o_caminho_de_revisao():
    """O que a casa tem para «o texto derivado mudou», lido dos donos — não decidido aqui."""
    import sala_de_espera as espera                     # noqa: PLC0415
    return {
        "036_VERSAO_DO_DOCUMENTO": (
            "admissao/versao_do_documento.decidir: «BYTES IGUAIS NAO CRIAM VERSAO» — compara "
            "parent_sha256 ANTES da receita; o mesmo RAW re-derivado por outra regua sai IGUAL "
            "(«bytes do RAW iguais») e nao entra em sala_de_espera_versao"),
        "033_REVISAO": ("sala_de_espera.rever so aceita %s — `texto` NAO e revisivel (a trava do "
                        "banco `revisao_so_de_campo_revisivel` recusa-o)"
                        % sorted(espera.CAMPOS_REVISIVEIS)),
        "PUBLISHED_AT_TEM_CAMINHO": (
            "a PUBLICACAO sai dos BYTES da pagina (executor_texto_de_html.tempo_de_publicacao), nao "
            "do texto: `admissao/reprocessar_tempo_lugar.py --raizes <armazem> --aplicar` ja a "
            "revê pela 033 — para TODAS as linhas, e com FACT_* lidos do texto ANTIGO da linha"),
        "TEXTO_NAO_TEM_CAMINHO": ("nenhum dono leva «o mesmo RAW, texto derivado novo» a linha "
                                  "da Sala: DONO = NAO DEFINIDO"),
    }


# ═════════════════════════════════════════════════════════════════════════
# A ESTRADA
# ═════════════════════════════════════════════════════════════════════════

def novo_run_id():
    return "%s-%s-%s" % (MOTIVO, datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                         uuid.uuid4().hex[:8])


def correr(dsn, raw_id, armazem_original, saida, aplicar=False, universo=None, livros=None,
           armazem_da_copia=None):
    motivo = porque_nao_e_copia(dsn)
    if motivo:
        raise NaoECopia("RECUSADO: %s. Nada foi lido nem escrito." % motivo)
    armazem_da_copia = os.path.abspath(armazem_da_copia or os.path.join(saida, "armazem-da-copia"))
    o_original = os.path.abspath(armazem_original)
    try:
        dentro = os.path.commonpath([armazem_da_copia, o_original]) == o_original
    except ValueError:                                   # Windows: discos diferentes
        dentro = False
    if dentro:
        raise NaoECopia("RECUSADO: o armazem da copia (%s) fica dentro do --armazem original: o "
                        "original so se le" % armazem_da_copia)
    retiradas = isolar_o_ambiente(dsn)
    import coleta_checkpoint as cc                       # noqa: PLC0415
    banco = cc.Banco(dsn)
    marcas = conferir_marca(banco)

    import admissao as adm                               # noqa: PLC0415
    import derivacao_forward as deriv                    # noqa: PLC0415
    import ingresso as ing                               # noqa: PLC0415
    import italy_executor as ix                          # noqa: PLC0415
    import orquestrador as ORQ                           # noqa: PLC0415
    import sala_de_espera as espera                      # noqa: PLC0415
    import versao_do_documento as vdoc                   # noqa: PLC0415
    from coleta import executor_texto_de_html as H       # noqa: PLC0415
    from coleta.extratores_de_texto import registo as extratores  # noqa: PLC0415
    from guarda.memoria_postgres import MemoriaPostgres  # noqa: PLC0415
    from guarda.preservar_derivado import hash_dos_parametros  # noqa: PLC0415

    fora = {"MISSAO": "nuvem-canario-1149-rederivar-v1", "MOTIVO": MOTIVO, "APLICOU": bool(aplicar),
            "COPIA": {"MORADA": morada_sem_segredo(dsn), "MARCA": "%s (%d linha(s))"
                      % (MARCA_DE_COPIA, marcas), "AMBIENTE_RETIRADO": retiradas},
            "SEM_REDE": "socket.socket trocado por armadilha durante a corrida (main)"}
    raw = ler_raw(banco, raw_id)
    if raw is None:
        raise Parado("raw_asset %s nao existe nesta copia" % raw_id)
    fora["RAW"] = raw
    antes = fotografia(banco)
    fora["TABELAS_ANTES"] = antes

    # ── 1 · A MESMA PÁGINA ORIGINAL ─────────────────────────────────────
    dados, de_onde = bytes_do_raw(armazem_original, raw)
    fora["PAGINA_ORIGINAL"] = {"LIDA_DE": de_onde, "BYTES": len(dados),
                               "SHA256": raw["sha256"], "SHA256_CONFERE": True}

    # ── 2 · O ANTES: a linha da Sala e os derivados que já existem ──────
    linhas = linhas_do_documento(banco, raw)
    derivados_antes = derivados_do_raw(banco, raw_id)
    universos = [universo.upper()] if universo else sorted({l["universo"] for l in linhas})
    if len(universos) != 1:
        raise Parado("universo: %s. O universo vem do PEDIDO — sem linha na Sala, declare "
                     "--universo; com linhas em varios universos, corra um de cada vez."
                     % (universos or "nenhuma linha deste documento na Sala"))
    u = universos[0]
    na_sala = [l for l in linhas if l["universo"] == u]
    antes_linhas = [dict(l, LINHA=linha_atual(l["run_id"], l["ordem"]),
                         VERSOES=versoes_de(banco, l["run_id"], l["ordem"])) for l in na_sala]
    fora["ANTES"] = {
        "DERIVADOS_DO_RAW": derivados_antes,
        "LINHAS_NA_SALA": [dict({k: v for k, v in l.items() if k != "LINHA"},
                                TEXTO=texto_em_resumo((l["LINHA"] or {}).get("TEXTO", ""), 5),
                                CAMPOS_DO_FATO=campos_do_fato(l["LINHA"]))
                           for l in antes_linhas]}

    # ── 3 · A DERIVAÇÃO CORRIGIDA (puro: o que o executor v4 dá) ────────
    texto_novo, estado, erro, _ = H.extrair(dados, raw["media_type"] or "text/html")
    receita = H.receita()
    obs = observacao_do_livro(livros, raw["sha256"]) or {"SOURCE_ID": raw["source_id"]}
    tempo_e_lugar = ix.tempo_e_lugar(obs, dados)
    fora["RECADO_DE_TEMPO_E_LUGAR"] = {
        "DONO": "coleta/italy_executor.tempo_e_lugar",
        "OBSERVACAO_DO_LIVRO": "SIM" if "RAW_SHA256" in obs else
        "NAO — sem --livros so o contrato e a pagina; a confissao do coletor sobre FACT_TIME nao vem",
        "VALORES": tempo_e_lugar}
    previsto = {"producer": H.EXECUTOR_ID, "producer_version": H.EXECUTOR_VERSION,
                "parameters_hash": hash_dos_parametros(receita), "REGUA": receita["TEXT_RULE"],
                "sha256": hashlib.sha256((texto_novo or "").encode("utf-8")).hexdigest()
                if texto_novo else None, "parent_sha256": raw["sha256"],
                "ESTADO_DO_EXECUTOR": estado, "ERRO": erro}
    ja = MemoriaPostgres(dsn).derivado_com_identidade({
        "parent_sha256": raw["sha256"], "kind": H.KIND, "producer": H.EXECUTOR_ID,
        "producer_version": H.EXECUTOR_VERSION, "parameters_hash": previsto["parameters_hash"],
        "serie_posicao": None})
    if ja:
        bytes_ca = os.path.isfile(os.path.join(armazem_da_copia, ja["storage_path"]))
        previsto["NA_COPIA"] = "JA_EXISTE derived:%s (%s)" % (ja["id"], (
            "seria REUSED" if bytes_ca else "os bytes NAO estao em %s: o dono responderia "
            "STORAGE_MISSING — use o --armazem-da-copia da corrida que o escreveu" % armazem_da_copia))
    else:
        previsto["NA_COPIA"] = "NAO_EXISTE (seria INSERTED)"
    fora["DERIVACAO_PREVISTA"] = previsto
    if not texto_novo:
        raise Parado("o executor nao deu texto: %s" % erro)

    # ── 4 · A COMPARAÇÃO (puro: a porta, com o texto antigo e o novo) ───
    retrato = H._retrato(dados)
    texto_antigo = ((antes_linhas[0]["LINHA"] or {}).get("TEXTO") if antes_linhas else None)
    comparacao = {"TEXTO_NOVO": texto_em_resumo(texto_novo)}
    julgados = {}
    for nome, t in (("ANTIGO", texto_antigo), ("NOVO", texto_novo)):
        if not t:
            comparacao["DECISAO_" + nome] = NAO_SEI
            continue
        item = item_para_a_porta(t, raw, "NOVO" if nome == "NOVO" else "ANTIGO",
                                 tempo_e_lugar, retrato)
        d = adm.decidir(item, u, corrida="previsao %s" % MOTIVO)
        julgados[nome] = (item, d)
        comparacao["DECISAO_" + nome] = a_decisao(d, u)
    # os campos do fato do texto ANTIGO sao os da linha da Sala (ANTES), e nao se recalculam
    item, d = julgados["NOVO"]
    comparacao["CAMPOS_DO_FATO_NOVO"] = campos_do_fato(
        adm.pronto_para_inteligencia(item, d)) if d.resultado == adm.SIM else NAO_SEI
    if texto_antigo:
        comparacao["TEXTO_ANTIGO"] = texto_em_resumo(texto_antigo, 3)
    fora["COMPARACAO"] = comparacao

    # ── 5 · O QUE A SALA FARIA (leitura + o decisor de versões, puro) ───
    anterior = None
    if antes_linhas:
        ultimo = next((v["item_id"] for v in reversed(antes_linhas[0]["VERSOES"])),
                      None) if isinstance(antes_linhas[0]["VERSOES"], list) else None
        ultimo = ultimo or antes_linhas[0]["item_id"]
        anterior = vdoc.ler_derivados(lambda s: espera.backend()._consultar(s),
                                      espera._Postgres.SEP, [vdoc._derivado_id(ultimo)])
        anterior = next(iter(anterior.values()), None)
    novo_hipotetico = dict(previsto, id=None,
                           storage_path_raw=raw["storage_path"], media_type_raw=raw["media_type"])
    vd = vdoc.decidir(anterior, novo_hipotetico) if anterior else None
    duplicaria = bool(na_sala) and raw["identity_state"] != "FORWARD_IDENTIFIED"
    fora["SALA_PREVISTA"] = {
        "IDENTIDADE_DO_RAW": raw["identity_state"] or NAO_SEI,
        "LINHAS_DESTE_DOCUMENTO_NO_UNIVERSO": len(na_sala),
        "DEDUP_DOC": ("funde: o documento ja esta no universo %s e a identidade e provada "
                      "(FORWARD_IDENTIFIED) — a linha nova NAO entra" % u) if na_sala and not duplicaria
        else ("DUPLICARIA: a identidade do RAW nao e provada e o item_id e novo — pousar gravaria "
              "uma 2.a linha do MESMO bruto" if duplicaria else "documento novo neste universo: pousaria"),
        "VERSAO_036": vd or "sem linha anterior: nao ha versao a decidir",
        "CAMINHO_DE_REVISAO": o_caminho_de_revisao()}

    if not aplicar:
        fora["TABELAS_DEPOIS"] = fotografia(banco)
        fora["ESCREVEU"] = {t: 0 for t in TABELAS} if fora["TABELAS_DEPOIS"] == antes else "DIVERGE"
        fora["ESTADO"] = "SO_PREVISAO (sem --aplicar nao se escreve nada)"
        return fora

    # ══ --aplicar: escreve SÓ na cópia ═══════════════════════════════════
    run_id = novo_run_id()
    destino = os.path.join(armazem_da_copia, raw["storage_path"])
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if not os.path.isfile(destino):
        shutil.copyfile(de_onde, destino)
    fora["ARMAZEM_DA_COPIA"] = armazem_da_copia
    armazem = ing.ArmazemLocal(armazem_da_copia)
    memoria = MemoriaPostgres(dsn)
    cc.abrir_corrida(banco, run_id=run_id, platform="REPROCESSO", actor=ATOR,
                     actor_version=H.EXECUTOR_VERSION, mission=MOTIVO,
                     capture_method="SEM_REDE: RAW guardado, re-derivado numa copia",
                     rule_version=adm.VERSAO_DA_REGRA,
                     entrada={"RAW_ASSET_ID": int(raw_id), "MOTIVO": MOTIVO, "UNIVERSO": u})
    fora["CORRIDA"] = {"RUN_ID": run_id, "DONO": "coleta/coleta_checkpoint.abrir_corrida",
                       "PLATFORM": "REPROCESSO", "MISSION": MOTIVO}
    try:
        # DERIVED — a unidade pelo dono da porta, a derivação pelo runner canónico
        unidades, sem_bytes = ing.unidades_para_a_derivacao(
            {"RAW_OBSERVATIONS": [{"RAW_OBSERVATION_ID": int(raw_id),
                                   "STORAGE_PATH": raw["storage_path"],
                                   "MEDIA_TYPE": raw["media_type"] or None,
                                   "SOURCE_ID": raw["source_id"] or None,
                                   "SOURCE_URL": raw["source_url"] or None,
                                   "CAPTURED_AT": raw["captured_at"] or None}]},
            armazem, {int(raw_id): tempo_e_lugar})
        if not unidades:
            raise Parado("a porta nao fez unidade: %s" % sem_bytes)
        rd = deriv.correr(unidades, banco_do_rastro=banco, run_id=run_id, armazem=armazem,
                          memoria=memoria, source_id=raw["source_id"] or None)
        r0 = (rd.get("RESULTADOS") or [{}])[0]
        linha_d = r0.get("LINHA") or {}
        fora["DERIVADO_NOVO"] = {
            "PORTA": r0.get("PORTA"), "ESTADO": r0.get("ESTADO"), "EXECUTOR": r0.get("EXECUTOR_ID"),
            "ID": linha_d.get("id"), "ITEM_ID": "derived:%s" % linha_d.get("id"),
            "PRODUCER_VERSION": linha_d.get("producer_version"), "SHA256": linha_d.get("sha256"),
            "PAI_RAW_ASSET_ID": linha_d.get("raw_asset_id"),
            "PARENT_SHA256": linha_d.get("parent_sha256"),
            "PARAMETERS_HASH": linha_d.get("parameters_hash"),
            "STORAGE_PATH": linha_d.get("storage_path"), "RASTRO": rd.get("ESTADO_DA_ETAPA")}
        if r0.get("PORTA") not in ("PASSED", "REUSED"):
            raise Parado("a derivacao nao entregou: %s" % r0.get("PORQUE"))

        # STRUCTURED — pelo dono do documento estruturado, como na coleta real
        est = ORQ.pela_estruturacao(rd, run_id=run_id, armazem=armazem, memoria=memoria,
                                    source_id=raw["source_id"] or None)
        fora["ESTRUTURADO"] = {"DONO": est.get("DONO"), "RECUSADOS": est.get("RECUSADOS"),
                               "ESTADO": [e["ESTADO"] for e in est.get("ESTRUTURADOS") or []]}
        if not est.get("ESTRUTURADOS"):
            raise Parado("o STRUCTURED nao entregou: %s" % est.get("RECUSADOS"))
        e0 = est["ESTRUTURADOS"][0]
        fora["TEXTO_DERIVADO"] = texto_em_resumo(e0["TEXTO"])

        # ADMISSION — o item da rota documental, a porta decide
        item = ORQ.item_documental_para_a_porta(e0, source_id=raw["source_id"] or None)
        decisao = adm.decidir(item, u, corrida=run_id)
        fora["ADMISSAO"] = a_decisao(decisao, u)
        with open(os.path.join(saida, "DECISAO-%s.json" % run_id), "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump(fora["ADMISSAO"], fh, ensure_ascii=False, indent=1)
        if decisao.resultado != adm.SIM:
            fora["SALA"] = {"ESTADO": "NAO_CORREU", "PORQUE": "a porta respondeu %s: nada a pousar"
                            % decisao.resultado}
            raise Parado(fora["SALA"]["PORQUE"])
        pronta = adm.pronto_para_inteligencia(item, decisao)
        fora["CAMPOS_DO_FATO"] = campos_do_fato(pronta)

        # READY — a Sala. Antes: a trava contra a 2.ª linha do MESMO bruto.
        if duplicaria:
            fora["SALA"] = {"ESTADO": "NAO_CHAMADA", "DONO_DO_CAMINHO": "NAO DEFINIDO",
                            "PORQUE": fora["SALA_PREVISTA"]["DEDUP_DOC"]}
            raise Parado(fora["SALA"]["PORQUE"])
        recibo = espera.pousar(run_id, [pronta], armazem=armazem, extratores=extratores())
        depois_linhas = linhas_do_documento(banco, raw)
        prova = {"LINHAS_DO_DOCUMENTO_ANTES": len(na_sala),
                 "LINHAS_DO_DOCUMENTO_DEPOIS": len([l for l in depois_linhas if l["universo"] == u]),
                 "VERSOES_ANTES": [l["VERSOES"] for l in antes_linhas],
                 "VERSOES_DEPOIS": [versoes_de(banco, l["run_id"], l["ordem"]) for l in na_sala],
                 "LINHA_DA_CORRIDA_NOVA": [l for l in depois_linhas if l["run_id"] == run_id]}
        if recibo["ESTADO"] == espera.POUSOU:
            veredito = "POUSOU (linha nova: %s)" % prova["LINHA_DA_CORRIDA_NOVA"]
        elif recibo.get("JA_NA_SALA_POR_OUTRA_CORRIDA") not in (0, NAO_SEI, None):
            veredito = ("FUNDIDO_POR_DOCUMENTO: a versao nova do mesmo documento NAO ganha 2.a linha "
                        "(declarado em admissao/sala_de_espera.py, DEDUP-DOC)")
        else:
            veredito = "JA_ESTAVA"
        fora["SALA"] = {"RECIBO": recibo, "VEREDITO": veredito, "PROVA": prova,
                        "DONO_DO_CAMINHO_PARA_TEXTO_NOVO": (
                            "NAO DEFINIDO" if recibo["ESTADO"] != espera.POUSOU and not any(
                                v.get("ESTADO") == vdoc.MUDOU for v in recibo.get("VERSOES") or [])
                            else "a Sala guardou")}
        cc.fechar_corrida(banco, run_id=run_id, status=cc.CORRIDA_CONCLUIDA, item_count_raw=0)
        fora["ESTADO"] = "APLICADO_NA_COPIA"
    except Parado as p:
        cc.fechar_corrida(banco, run_id=run_id, status=cc.CORRIDA_PARCIAL, error=str(p))
        fora["ESTADO"] = "PARADO: %s" % p
    except Exception as ex:                              # noqa: BLE001
        cc.fechar_corrida(banco, run_id=run_id, status=cc.CORRIDA_FALHOU,
                          error="%s: %s" % (type(ex).__name__, ex))
        raise
    depois = fotografia(banco)
    fora["TABELAS_DEPOIS"] = depois
    fora["ESCREVEU"] = {t: (depois[t] - antes[t]) if isinstance(depois[t], int)
                        and isinstance(antes[t], int) else NAO_SEI for t in TABELAS}
    return fora


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dsn", required=True, help="a COPIA descartavel (nunca o vivo)")
    ap.add_argument("--raw-id", type=int, required=True)
    ap.add_argument("--armazem", required=True, help="raiz dos bytes guardados (so leitura)")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--armazem-da-copia", help="onde a copia guarda bytes (o MESMO em cada corrida "
                                               "na mesma copia); por omissao <saida>/armazem-da-copia")
    ap.add_argument("--universo", help="o do PEDIDO; por omissao, o da linha que ja esta na Sala")
    ap.add_argument("--livros", help="globs dos observations.ndjson do coletor, separados por ;")
    a = ap.parse_args(argv)
    os.makedirs(a.saida, exist_ok=True)
    # ⚠️ A ARMADILHA DA REDE VIVE SO DURANTE A CORRIDA. O psql e um processo filho: ela apanha
    # rede aberta POR ESTE processo (um leitor que fosse buscar a pagina), e e desfeita no fim
    # para quem importa este ficheiro (os testes) nao herdar um socket partido.
    socket_de_antes, socket.socket = socket.socket, _SemRede
    try:
        fora = correr(a.dsn, a.raw_id, a.armazem, a.saida, aplicar=a.aplicar,
                      universo=a.universo, livros=a.livros,
                      armazem_da_copia=a.armazem_da_copia)
    except NaoECopia as ex:
        print(json.dumps({"ESTADO": "RECUSADO", "PORQUE": str(ex)}, ensure_ascii=False))
        return 2
    except Parado as ex:
        print(json.dumps({"ESTADO": "PARADO", "PORQUE": str(ex)}, ensure_ascii=False))
        return 3
    finally:
        socket.socket = socket_de_antes
    nome = os.path.join(a.saida, "REDERIVAR-RAW-%d%s.json" % (a.raw_id, "" if a.aplicar else "-PREVISAO"))
    with open(nome, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: fora.get(k) for k in ("ESTADO", "APLICOU", "CORRIDA", "DERIVADO_NOVO",
                                              "ADMISSAO", "SALA", "ESCREVEU")},
                     ensure_ascii=False, indent=1, default=str)[:6000])
    print("recibo inteiro: %s" % nome)
    return 3 if str(fora.get("ESTADO", "")).startswith("PARADO") else 0


if __name__ == "__main__":
    sys.exit(main())
