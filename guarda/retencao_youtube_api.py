#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D20 · A RETENÇÃO DE 30 DIAS DOS DADOS DA YOUTUBE DATA API — o dono que apaga.

    py guarda/retencao_youtube_api.py --checar            # a checagem diária (só lê)
    py guarda/retencao_youtube_api.py --varrer            # o que ia apagar (só lê)
    py guarda/retencao_youtube_api.py --varrer --aplicar  # apaga os bytes e deixa a lápide

    banco:   --url=… ou BANCO_DESCARTAVEL_URL. Um banco que NÃO é descartável só
             aceita `--aplicar` com `--operacional` escrito à mão.
    bytes:   --raiz=… (o armazém local; por omissão, a raiz do repositório,
             que é onde o `ArmazemLocal` do orquestrador escreve).

A REGRA
-------
Developer Policies III.E.4 (texto, URL, data e sha256 em
`candidatas/PROVA-TERMOS-SOC1-V1.json`): o que vem da API só se guarda até 30 dias;
depois, renovar ou apagar. D20 decidiu que a regra vale no acervo.

A casa NUNCA apagou nada — e continua a não apagar a PROVENIÊNCIA. O que sai é o
BYTE; a linha de `raw_asset` fica com `preserved = false` e o motivo, e a tabela
`lapide_de_retencao` (migração 033) guarda o que saiu, quando e porquê, com o sha256
do que existia. O texto que a observação levou para a Sala (`sala_de_espera.texto`)
e para as tabelas sociais (`conteudo.titulo/descricao`, `comentario.texto`) é o
mesmo dado da API, e sai com ela.

    O BYTE SAI. A LINHA FICA. A LÁPIDE DIZ O QUE SAIU.

O QUE CONTA COMO «DADO DA API»
------------------------------
Nenhuma coluna do banco guarda a rota. Ela vive DENTRO do byte guardado: o envelope
do Scrap traz `ROUTE` e `DISCOVERY_ROUTES` (`coleta/social_envelope.py`). Por isso:

  · candidata = observação `application/json`, ainda preservada, com mais de 30 dias;
  · só se apaga se o byte for lido, o sha256 bater com o da linha, e TODAS as rotas
    que ele declara forem `youtube-data-api-v3:*`;
  · byte ausente, sha diferente, rota mista ou nenhuma rota → NAO SEI: não se apaga,
    e a checagem diz quantos há. Não saber não autoriza apagar.

O ÁUDIO LOCAL NÃO ENTRA (D20). `yt-dlp:public_audio` guarda `audio/wav`, fora das
candidatas; e um envelope que declare essa rota nunca é «só API».

`30 dias` é estrito: com 30 dias exactos a observação ainda está no prazo; com mais,
venceu. `agora` entra por parâmetro — é assim que o ensaio forja 29, 30 e 31 dias.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "guarda"))

import banco_descartavel as BD          # noqa: E402
import preservar_coleta as PC           # noqa: E402

REGRA = "YOUTUBE_API_III_E_4_30D"
PRAZO = timedelta(days=30)
PREFIXO_DA_API = "youtube-data-api-v3:"
MARCA = "[APAGADO PELA REGRA DOS 30 DIAS DA YOUTUBE DATA API (D20 · III.E.4) EM %s]"

API = "API"
NAO_E_DA_API = "NAO_E_DA_API"
NAO_SEI = "NAO_SEI"
#: O MESMO byte (a mesma cópia no armazém) é também de uma observação ainda no
#: prazo: a cópia foi renovada com bytes iguais. Apagá-la apagaria o dado novo.
EM_USO_NO_PRAZO = "EM_USO_NO_PRAZO"


# ── O BANCO ─────────────────────────────────────────────────────────────────
def _psql(url: str, sql: str) -> list[list[str]]:
    exe = os.environ.get("SINTONIA_PSQL_EXE") or "psql"
    r = subprocess.run([exe, "-X", "-q", "-A", "-t", "-F", "\x1f", "-v", "ON_ERROR_STOP=1",
                        "-f", "-", url], input=sql, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=BD.ambiente_sem_desvio()[0])
    if r.returncode != 0:
        raise RuntimeError("psql: %s" % r.stderr.strip()[:400])
    # `if l != ""` e nao `if l.strip()`: o separador \x1f E ESPACO para o Python
    # (`"\x1f".isspace()` da True), e uma linha so de campos vazios sumia calada.
    return [l.split("\x1f") for l in r.stdout.replace("\r", "").splitlines() if l != ""]


def _lit(v) -> str:
    if v is None:
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


def _instante(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")


# ── A ROTA LÊ-SE NO BYTE ────────────────────────────────────────────────────
def rotas_do_byte(dados: bytes) -> list[str]:
    """Todas as rotas que a observação declara, onde quer que o envelope as ponha."""
    try:
        j = json.loads(dados.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return []
    if not isinstance(j, dict):
        return []
    rotas = []
    for alvo in (j, j.get("OBSERVACAO") if isinstance(j.get("OBSERVACAO"), dict) else {}):
        if isinstance(alvo.get("ROUTE"), str):
            rotas.append(alvo["ROUTE"])
        if isinstance(alvo.get("DISCOVERY_ROUTES"), list):
            rotas.extend(r for r in alvo["DISCOVERY_ROUTES"] if isinstance(r, str))
    return sorted(set(rotas))


def classificar(dados: bytes) -> tuple[str, list[str]]:
    rotas = rotas_do_byte(dados)
    if not rotas:
        return NAO_SEI, rotas
    da_api = [r for r in rotas if r.startswith(PREFIXO_DA_API)]
    if da_api and len(da_api) == len(rotas):
        return API, rotas
    if da_api:
        return NAO_SEI, rotas          # rota mista: não se apaga o que não é só da API
    return NAO_E_DA_API, rotas


# ── A VARREDURA ─────────────────────────────────────────────────────────────
def _candidatas(url: str, limite: datetime) -> list[dict]:
    linhas = _psql(url, """
      select r.id, coalesce(so.storage_path, r.storage_path), r.sha256, r.bytes,
             r.captured_at, coalesce(r.source_id, ''), coalesce(r.document_key, '')
        from public.raw_asset r
        left join public.storage_object so on so.id = r.storage_object_id
       where r.preserved
         and r.media_type like 'application/json%'
         and r.captured_at < """ + _lit(_instante(limite)) + """::timestamptz
       order by r.id;""")
    return [{"ID": int(l[0]), "PATH": l[1], "SHA256": l[2].strip(), "BYTES": int(l[3]),
             "CAPTURED_AT": l[4], "SOURCE_ID": l[5], "DOCUMENT_KEY": l[6]} for l in linhas]


def _derivados(url: str, raw_id: int) -> list[dict]:
    return [{"ID": int(l[0]), "PATH": l[1], "SHA256": l[2].strip(), "BYTES": int(l[3])}
            for l in _psql(url, "select id, storage_path, sha256, bytes from public.derived_artifact "
                                "where raw_asset_id = %d order by id;" % raw_id)]


def _renovada(url: str, c: dict, limite: datetime) -> bool:
    """Há uma cópia MAIS NOVA, ainda no prazo, do mesmo documento da mesma fonte?"""
    if not (c["SOURCE_ID"] and c["DOCUMENT_KEY"]):
        return False
    r = _psql(url, "select count(*) from public.raw_asset where preserved and id <> %d "
                   "and source_id = %s and document_key = %s and captured_at >= %s::timestamptz;"
                   % (c["ID"], _lit(c["SOURCE_ID"]), _lit(c["DOCUMENT_KEY"]), _lit(_instante(limite))))
    return int(r[0][0]) > 0


def _em_uso_no_prazo(url: str, c: dict, limite: datetime) -> bool:
    r = _psql(url, "select count(*) from public.raw_asset r left join public.storage_object so "
                   "on so.id = r.storage_object_id where r.preserved and r.id <> %d "
                   "and coalesce(so.storage_path, r.storage_path) = %s and r.captured_at >= %s::timestamptz;"
                   % (c["ID"], _lit(c["PATH"]), _lit(_instante(limite))))
    return int(r[0][0]) > 0


def varrer(url: str, raiz: str = RAIZ, agora: datetime | None = None) -> list[dict]:
    """→ o veredicto de cada candidata. SÓ LÊ."""
    agora = agora or datetime.now(timezone.utc)
    limite = agora - PRAZO
    armazem = PC.ArmazemLocal(raiz)
    fora = []
    for c in _candidatas(url, limite):
        local = armazem.caminho_local(c["PATH"])
        if not local:
            fora.append(dict(c, VEREDICTO=NAO_SEI, PORQUE="o byte nao esta neste armazem"))
            continue
        with open(local, "rb") as fh:
            dados = fh.read()
        if hashlib.sha256(dados).hexdigest() != c["SHA256"]:
            fora.append(dict(c, VEREDICTO=NAO_SEI, PORQUE="o sha256 do byte nao e o da linha"))
            continue
        classe, rotas = classificar(dados)
        v = dict(c, VEREDICTO=classe, ROTAS=rotas, LOCAL=local)
        if classe == API and _em_uso_no_prazo(url, c, limite):
            v.update(VEREDICTO=EM_USO_NO_PRAZO,
                     PORQUE="a mesma copia e de outra observacao ainda no prazo")
            fora.append(v)
            continue
        if classe == API:
            v["MOTIVO"] = "RENOVADA" if _renovada(url, c, limite) else "PRAZO_VENCIDO"
            v["DERIVADOS"] = _derivados(url, c["ID"])
        else:
            v["PORQUE"] = ("rotas %s" % rotas) if rotas else "o byte nao declara rota"
        fora.append(v)
    return fora


def _sql_da_lapide(v: dict, agora: datetime) -> str:
    quando = _instante(agora)
    rota = next(r for r in v["ROTAS"] if r.startswith(PREFIXO_DA_API))
    prova = "sha256 do byte conferido antes de apagar; rotas no envelope: %s" % ", ".join(v["ROTAS"])
    marca = MARCA % quando[:10]
    partes = [
        "insert into public.lapide_de_retencao (raw_asset_id, derived_artifact_id, storage_path, sha256, "
        "bytes, regra, motivo, rota, captured_at, apagado_em, prova) values "
        "(%d, null, %s, %s, %d, %s, %s, %s, %s::timestamptz, %s::timestamptz, %s) "
        "on conflict (storage_path) do nothing;"
        % (v["ID"], _lit(v["PATH"]), _lit(v["SHA256"]), v["BYTES"], _lit(REGRA), _lit(v["MOTIVO"]),
           _lit(rota), _lit(v["CAPTURED_AT"]), _lit(quando), _lit(prova)),
    ]
    for d in v["DERIVADOS"]:
        partes.append(
            "insert into public.lapide_de_retencao (raw_asset_id, derived_artifact_id, storage_path, "
            "sha256, bytes, regra, motivo, rota, captured_at, apagado_em, prova) values "
            "(%d, %d, %s, %s, %d, %s, %s, %s, %s::timestamptz, %s::timestamptz, %s) "
            "on conflict (storage_path) do nothing;"
            % (v["ID"], d["ID"], _lit(d["PATH"]), _lit(d["SHA256"]), d["BYTES"], _lit(REGRA),
               _lit(v["MOTIVO"]), _lit(rota), _lit(v["CAPTURED_AT"]), _lit(quando),
               _lit("derivado da observacao %d; " % v["ID"] + prova)))
    partes += [
        "update public.raw_asset set preserved = false, not_preserved_reason = %s where id = %d;"
        % (_lit("%s: bytes apagados em %s (%s); lapide em lapide_de_retencao; sha256 do que "
                "existia fica nesta linha" % (REGRA, quando, v["MOTIVO"])), v["ID"]),
        "update public.sala_de_espera set texto = %s where raw_observation_id = %d;" % (_lit(marca), v["ID"]),
        "update public.comentario set texto = %s where conteudo_id in "
        "(select id from public.conteudo where raw_asset_id = %d);" % (_lit(marca), v["ID"]),
        "update public.conteudo set titulo = null, descricao = null where raw_asset_id = %d;" % v["ID"],
    ]
    return "\n".join(partes)


def aplicar(url: str, veredictos: list[dict], raiz: str = RAIZ,
            agora: datetime | None = None, apagar=os.remove) -> dict:
    """Primeiro a MEMÓRIA (uma transacção por observação), depois o BYTE.

    Se o byte não sair depois da lápide escrita, a checagem apanha-o
    (`LAPIDE_COM_BYTE_VIVO`): o erro fica visível, e não escondido atrás de uma
    linha que diz «preservado» sem o estar."""
    agora = agora or datetime.now(timezone.utc)
    armazem = PC.ArmazemLocal(raiz)
    feitas, falhas = [], []
    for v in veredictos:
        if v["VEREDICTO"] != API:
            continue
        _psql(url, "begin;\n%s\ncommit;" % _sql_da_lapide(v, agora))
        for caminho in [v["PATH"]] + [d["PATH"] for d in v["DERIVADOS"]]:
            local = armazem.caminho_local(caminho)
            try:
                if local:
                    apagar(local)
            except OSError as e:
                falhas.append({"PATH": caminho, "ERRO": str(e)[:200]})
        feitas.append({"RAW_ASSET_ID": v["ID"], "MOTIVO": v["MOTIVO"],
                       "FICHEIROS": 1 + len(v["DERIVADOS"])})
    return {"LAPIDES": feitas, "FALHAS_AO_APAGAR": falhas}


# ── A CHECAGEM DIÁRIA ───────────────────────────────────────────────────────
def checar(url: str, raiz: str = RAIZ, agora: datetime | None = None) -> dict:
    """PASS = nenhum dado da API com mais de 30 dias ainda guardado, e nenhuma lápide
    com o byte ainda no armazém. NAO_SEI = há observações antigas cuja rota não se
    consegue provar (byte fora deste armazém, sha diferente, rota mista)."""
    agora = agora or datetime.now(timezone.utc)
    vs = varrer(url, raiz, agora)
    vencidos = [v["ID"] for v in vs if v["VEREDICTO"] == API]
    nao_sei = [v["ID"] for v in vs if v["VEREDICTO"] == NAO_SEI]
    armazem = PC.ArmazemLocal(raiz)
    lapides = [l[0] for l in _psql(url, "select storage_path from public.lapide_de_retencao;")]
    vivas = [p for p in lapides if armazem.caminho_local(p)]
    estado = "FAIL" if (vencidos or vivas) else ("NAO_SEI" if nao_sei else "PASS")
    return {"RETENCAO_30D": estado, "MEDIDO_EM": _instante(agora),
            "DADOS_DA_API_VENCIDOS_AINDA_GUARDADOS": vencidos,
            "LAPIDES": len(lapides), "LAPIDE_COM_BYTE_VIVO": vivas,
            "NAO_SEI": nao_sei}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    url = arg.get("url") or os.environ.get("BANCO_DESCARTAVEL_URL")
    if not url:
        print("RETENCAO_30D=NOT_RUN · sem --url nem BANCO_DESCARTAVEL_URL")
        return 2
    raiz = arg.get("raiz", RAIZ)
    if "--checar" in argv:
        r = checar(url, raiz)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["RETENCAO_30D"] == "PASS" else 1
    vs = varrer(url, raiz)
    for v in vs:
        print("%-12s raw=%-6d %s %s" % (v["VEREDICTO"], v["ID"], v.get("MOTIVO", ""), v.get("PORQUE", "")))
    if "--aplicar" in argv:
        if not BD.e_descartavel(url) and "--operacional" not in argv:
            print("RECUSADO: o banco nao e descartavel; --aplicar exige --operacional escrito a mao")
            return 4
        print(json.dumps(aplicar(url, vs, raiz), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
