"""SOC2 · A ROTA DO SCRAP PARA UM CANAL YOUTUBE, VISTA DO LADO DO CURATOR.

O Curator NAO colhe YouTube e NAO decide se a rota e permitida. Quem colhe e o
SCRAP (fase `canal-youtube`, executor `scrap-colheita`); quem decide a rota e a
matriz do Scrap (`leis/social_matriz.py`), autorizada pelo dono tal como o Scrap
a declara (D17.4). Este ficheiro so LE essas duas coisas — nunca as escreve — e
diz ao Curator tres coisas:

    acquisition(channel_id)   o bloco ACQUISITION que um contrato escreve para
                              nomear a rota do Scrap (STRATEGY = SCRAP_FASE);
    conferir(aq)              se esse bloco ainda bate com o que o Scrap declara
                              HOJE (fase existe, pede a capacidade certa, recebe
                              `canal_id`, e a matriz diz ALLOWED);
    canal_conhecido(uc)       se esse canal ja tem SOURCE_ID na casa.

    O CURATOR NOMEIA A ROTA; O SCRAP E QUE A CORRE; A MATRIZ E QUE A PERMITE.

⚠️ SOURCE_ID != CHANNEL_ID. O canal e a identidade da PLATAFORMA; o SOURCE_ID e
a do projeto. Um canal que ja tem SOURCE_ID NUNCA recebe um segundo: a casa
ficaria com duas fontes a colher o mesmo canal, e a Sala com tudo em dobro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

STRATEGY = "SCRAP_FASE"
EXECUTOR = "scrap-colheita"
FASE = "canal-youtube"
PLATAFORMA = "YOUTUBE"
CAPACIDADE = "youtube.channel.discovery"
FILTRO = "canal_id"
AUTORIZACAO = "D17.4 (DECISOES-DONO-2026-09-23): rotas do YouTube tal como o Scrap as declara"

RE_CANAL = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
RE_CANAL_NA_URL = re.compile(r"youtube\.com/channel/(UC[A-Za-z0-9_-]{22})(?:[/?#]|$)")

TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
LIVRO = RAIZ / "curadoria" / "italy_contracts_curator.json"
ALLOCATION = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
# Os contratos escritos a mao (IT-T8-001 Agronotizie) vivem so no .mjs.
CONTRATOS_MJS = RAIZ / "regras" / "italy_contracts.mjs"
RE_CHAVE_MJS = re.compile(r'^\s*"(IT-T\d+-\d{3})":\s*\{', re.M)


def _caminhos():
    for p in ("coleta", "leis", "admissao", "regras", "ferramentas", "medidas",
              "guarda", "pedido", "orquestrador", ""):
        q = str(RAIZ / p) if p else str(RAIZ)
        if q not in sys.path:
            sys.path.append(q)


def channel_id_da_url(url: str) -> str | None:
    """O channel_id SO quando o endereco o traz escrito (`/channel/UC…`).

    `@handle`, `/user/`, `/c/` e playlist NAO se resolvem aqui: resolver pede a
    API (`channels.list forHandle`), com chave e rede. Adivinhar pelo nome seria
    fabricar identidade."""
    m = RE_CANAL_NA_URL.search(url or "")
    return m.group(1) if m else None


def o_que_o_scrap_declara() -> dict:
    """→ a leitura de hoje: a fase, a capacidade que ela pede, os filtros, e a
    decisao da matriz. Levanta se o Scrap deixou de declarar a fase."""
    _caminhos()
    import scrap_colheita as sc
    import scrap_capacidades as cap
    import social_matriz as mz
    linha = sc.FASES.get(FASE)
    if not linha:
        return {"FASE_EXISTE": False}
    plat, capac = linha[0], linha[1]
    d = mz.decisao(plat, cap.da_matriz(capac) or "")
    return {"FASE_EXISTE": True, "PLATAFORMA": plat, "CAPACIDADE": capac,
            "FILTROS": dict(sc.NOMEADOS.get(FASE) or {}),
            "DECISAO": d.get("DECISAO"), "ROTA": d.get("ROTA"), "CLASSE": d.get("CLASSE")}


def acquisition(channel_id: str, declarado: dict | None = None) -> dict:
    declarado = o_que_o_scrap_declara() if declarado is None else declarado
    return {
        "STRATEGY": STRATEGY,
        "EXECUTOR": EXECUTOR,
        "FASE": FASE,
        "PLATFORM": PLATAFORMA,
        "CAPACIDADE": CAPACIDADE,
        "CHANNEL_ID": channel_id,
        "FILTROS": {FILTRO: channel_id},
        "ROTA_DECLARADA_PELO_SCRAP": declarado.get("ROTA"),
        "AUTORIZACAO": AUTORIZACAO,
    }


def conferir(aq: dict, declarado: dict | None = None) -> tuple[bool, str]:
    """O bloco ainda bate com o Scrap de HOJE? Sem rede, sem gasto."""
    if (aq or {}).get("STRATEGY") != STRATEGY:
        return False, "STRATEGY nao e %s" % STRATEGY
    ch = aq.get("CHANNEL_ID") or ""
    if not RE_CANAL.match(ch):
        return False, "CHANNEL_ID invalido: %r" % ch
    if (aq.get("FILTROS") or {}).get(FILTRO) != ch:
        return False, "FILTROS.%s nao e o CHANNEL_ID do contrato" % FILTRO
    if aq.get("EXECUTOR") != EXECUTOR or aq.get("FASE") != FASE:
        return False, "executor/fase fora da rota do Scrap: %s/%s" % (aq.get("EXECUTOR"), aq.get("FASE"))
    d = o_que_o_scrap_declara() if declarado is None else declarado
    if not d.get("FASE_EXISTE"):
        return False, "o Scrap deixou de declarar a fase %s" % FASE
    if (d.get("PLATAFORMA"), d.get("CAPACIDADE")) != (PLATAFORMA, CAPACIDADE):
        return False, "a fase %s pede %s/%s, nao %s/%s" % (
            FASE, d.get("PLATAFORMA"), d.get("CAPACIDADE"), PLATAFORMA, CAPACIDADE)
    if FILTRO not in (d.get("FILTROS") or {}):
        return False, "a fase %s ja nao recebe o filtro %s" % (FASE, FILTRO)
    if d.get("DECISAO") != "ALLOWED":
        return False, "a matriz do Scrap diz %s para esta rota" % d.get("DECISAO")
    if aq.get("ROTA_DECLARADA_PELO_SCRAP") != d.get("ROTA"):
        return False, ("o Scrap declara hoje a rota %s e o contrato foi escrito para %s"
                       % (d.get("ROTA"), aq.get("ROTA_DECLARADA_PELO_SCRAP")))
    return True, "rota do Scrap: %s · %s · ALLOWED" % (FASE, d.get("ROTA"))


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _no_mjs(channel_id: str, texto: str) -> set:
    """O SOURCE_ID do bloco `"IT-Tx-nnn": {` mais proximo ANTES de cada ocorrencia
    do canal no .mjs dos contratos escritos a mao."""
    out = set()
    chaves = [(m.start(), m.group(1)) for m in RE_CHAVE_MJS.finditer(texto)]
    for m in re.finditer(re.escape(channel_id), texto):
        antes = [sid for pos, sid in chaves if pos < m.start()]
        if antes:
            out.add(antes[-1])
    return out


def canal_conhecido(channel_id: str, *, tabela=None, livro=None, alloc=None,
                    mjs: str | None = None) -> list[str]:
    """→ os SOURCE_ID que ja ligam este canal (tabela do coletor, livro do Curator,
    registo de alocacao). Mais de um e colisao de identidade — quem chama decide."""
    tabela = _ler(TABELA) if tabela is None else tabela
    livro = _ler(LIVRO) if livro is None else livro
    alloc = _ler(ALLOCATION) if alloc is None else alloc
    if mjs is None:
        mjs = CONTRATOS_MJS.read_text(encoding="utf-8") if CONTRATOS_MJS.exists() else ""
    achados = _no_mjs(channel_id, mjs)
    for c in (tabela.get("FONTES") or []) + (livro.get("FONTES") or []):
        aq = c.get("ACQUISITION") or {}
        if channel_id in (c.get("SOURCE_NATIVE_ID"), aq.get("CHANNEL_ID")):
            achados.add(c["SOURCE_ID"])
    for n in alloc.get("NOVAS") or []:
        if n.get("SOURCE_NATIVE_ID") == channel_id:
            achados.add(n["SOURCE_ID"])
    return sorted(achados)
