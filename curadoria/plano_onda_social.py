"""SOC-ONDA2 · PASSO 5 — o plano (SÓ PLANO) de uma onda social pelo orquestrador existente.

    py curadoria/plano_onda_social.py [--json SAIDA]

Não corre nada, não bate à rede, não escreve em livro. Para cada fonte social que a
PORTA aceita (`triagem_social`: rastro do dono + rota + âmbito do T9; as recusadas saem
com o motivo pelo nome em RECUSADAS_NA_PORTA) responde, pela ordem da casa (D28: o disparo é sempre
o orquestrador → executor; nada paralelo):

  1. o PORTÃO deixa-a entrar na coorte? (`collection_gate.avaliar`)
  2. o PEDIDO, montado EM PROCESSO (`pedido.Pedido`), resolve para `scrap-colheita`?
     — a frase da linha de comando junta os valores de `--filtro` ao texto e um
     endereço com «agricultural» virou T1 (medido no canário, IT-T5-163). A onda
     monta o pedido por dentro; o comando fica escrito só para quem o quiser ler.
  3. o executor CONSOME todos os filtros do contrato? (`receitas.filtros_consumidos`)
  4. `orquestrador.correr(pedido, so_plano=True)` devolve PLANO?

E escreve os buracos que o plano não fecha (onde a chave vive, a regra do nome do
documento na tabela do coletor), cada um com o dono.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "curadoria"))
import _gavetas  # noqa: E402,F401

import collection_gate as GATE   # noqa: E402
import lifecycle as LC           # noqa: E402
import receitas as REC           # noqa: E402
from pedido import Pedido        # noqa: E402

CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
EXECUTOR = "scrap-colheita"

BURACOS = {
    "CHAVE_YOUTUBE_SO_NO_GITHUB": (
        "a fase canal-youtube (API oficial) precisa de YOUTUBE_DATA_API_KEY, que so existe no "
        "GitHub Actions; sintonia-scrap.yml (fases canonicas) nao a injecta — a porta local "
        "responde CREDENTIAL_MISSING", "coordenador + engenheiro do Scrap (workflow)"),
    "DOCUMENT_ID_RULE_FORA_DA_TABELA": (
        "o Scrap le a regra do nome do documento em regras/italy_contracts.mjs (tabela do "
        "coletor); os contratos sociais do Curator nao estao la — o item entra com "
        "DOCUMENT_ID = NAO SEI (a identidade da plataforma, NATIVE_ID, vem inteira)",
        "CUR-PRONTA / coordenador (ponte livro do Curator -> tabela do coletor)"),
    "FRASE_DA_CLI_POLUI_O_ALVO": (
        "orquestrador.py junta os valores de --filtro a frase; um endereco com «agricultural» "
        "resolveu T1 em vez de T5. A onda monta o Pedido em processo",
        "dono do orquestrador (so documentado; esta onda contorna montando o Pedido)"),
}


# ── T9 SOCIAL-CATALOGO-AUTORIZADO (01/10): A PORTA LE O RASTRO, NAO A PALAVRA ──────────────────────
# Antes: `fontes_sociais` aceitava `STRATEGY == "SCRAP_FASE"` e devolvia [] sem dizer porque. Um feed de
# canal READY com rastro ficava fora; um SCRAP_FASE sem autorizacao entrava. Agora cada contrato social
# sai ACEITE ou RECUSADO com o motivo pelo nome. As regras sao as que ja existiam:
#   · a STRATEGY: o vocabulario do motor (`validar_contratos.STRATEGIES`);
#   · a rota: `rota_do_scrap_social.conferir` (SCRAP_FASE: o Scrap declara E a matriz diz ALLOWED) e
#     `validar_contratos.route_resolved` (o feed); a listagem do Instagram: `instagram_listar_permitido`;
#   · o rastro do dono: `ACQUISITION.AUTORIZACAO`, a decisao que o Curator escreve no contrato;
#   · o rastro da plataforma: `ROUTE_POLICY_STATUS` do contrato, quando existe;
#   · o estado: o livro do ciclo de vida (`lifecycle.estado_de`).
# O AMBITO e o da missao T9, com a resposta do dono a 01/10 — nao abre nada que as decisoes nao abram:
AMBITO = {
    "YOUTUBE": "so YOUTUBE_CHANNEL_FEED de canal em READY_FOR_COLLECTION (missao T9 a letra; dono, 01/10)",
    "LINKEDIN": "video-linkedin de pagina de ORGANIZACAO (D23; D24 pessoas). A fase traz MP4 e legenda: o dono "
                "aceitou a 01/10 (D23 autoriza video)",
    "INSTAGRAM": "so o Reel publico por URL directa (D22/D157); listagem e perfil NAO",
}
#: a decisao que o rastro do dono tem de citar, por plataforma (o primeiro termo de ACQUISITION.AUTORIZACAO)
DECISOES_DO_AMBITO = {"YOUTUBE": ("D17.4",), "LINKEDIN": ("D23", "D24"), "INSTAGRAM": ("D22",)}
#: as fases do Scrap que cabem no ambito (o canal-youtube nao: o YouTube do T9 e so o feed)
FASES_DO_AMBITO = {"video-linkedin", "captura-reel", "audio-reel", "transcricao-reel"}
FEED = "YOUTUBE_CHANNEL_FEED"
NAO_SOCIAIS = ("HTML_LINK_DISCOVERY", "STATIC_ENDPOINT")
#: os motivos de recusa, por precedencia: o primeiro que se aplica e o MOTIVO; os outros ficam em MOTIVOS
MOTIVOS_DA_PORTA = ("STRATEGY_DESCONHECIDA", "LISTAGEM_NAO_AUTORIZADA", "FORA_DO_AMBITO_AUTORIZADO",
                    "SEM_RASTRO_DE_AUTORIZACAO", "SEM_RASTRO_DE_POLITICA", "ROTA_NAO_PERMITIDA",
                    "ROTA_NAO_CONFERIDA", "ESTADO_NAO_READY")


def _decisao_citada(aq: dict) -> str | None:
    t = str(aq.get("AUTORIZACAO") or "").strip()
    return t.split()[0] if t else None


def _rastro_do_dono(plat: str | None, aq: dict) -> list[tuple[str, str]]:
    d, pede = _decisao_citada(aq), DECISOES_DO_AMBITO.get(plat or "", ())
    if not d:
        return [("SEM_RASTRO_DE_AUTORIZACAO", "o contrato nao cita decisao do dono (ACQUISITION.AUTORIZACAO "
                                              "vazio); %s pede %s" % (plat, "/".join(pede) or "NAO SEI"))]
    if d not in pede:
        return [("SEM_RASTRO_DE_AUTORIZACAO", "o contrato cita %s; %s pede %s" % (d, plat, "/".join(pede)))]
    return []


def _politica_do_contrato(c: dict) -> list[tuple[str, str]]:
    pol = c.get("ROUTE_POLICY_STATUS")
    if pol and pol != "ALLOWED":
        return [("ROTA_NAO_PERMITIDA", "ROUTE_POLICY_STATUS=%s (%s)" % (
            pol, c.get("ROUTE_POLICY_EVIDENCE") or "sem evidencia escrita"))]
    return []


#: SOCIAL-ONDA (02/10): o filtro em que as fases de Reel do Scrap recebem o endereco (`scrap_colheita.NOMEADOS`)
IG_FILTRO_URL = "url"


def _reel_por_url_directa(plat: str | None, aq: dict) -> list[tuple[str, str]]:
    """SOCIAL-ONDA (02/10): Instagram so o Reel por URL DIRECTA (D22/D157). Um endereco de perfil ou de conta e
    listagem — recusa com nome, mesmo que um dia o Curator tenha conferidor para as fases de Reel. A regra do que
    e um Reel e a que ja existia (`coleta/social_por_url_achado.especie_do_endereco`), nao uma nova."""
    if plat != "INSTAGRAM" or aq.get("FASE") not in FASES_DO_AMBITO:
        return []
    url = str((aq.get("FILTROS") or {}).get(IG_FILTRO_URL) or "").strip()
    if not url:
        return [("ROTA_NAO_CONFERIDA", "o contrato nao traz a URL directa do Reel (FILTROS.%s vazio)" % IG_FILTRO_URL)]
    sys.path.insert(0, str(RAIZ / "coleta"))
    import social_por_url_achado as SPA                                 # noqa: PLC0415
    esp = SPA.especie_do_endereco(url)
    if esp.get("ESPECIE") != "REEL":
        return [("LISTAGEM_NAO_AUTORIZADA", "FILTROS.%s=%s nao e URL directa de Reel (perfil ou listagem); "
                                            "D22/D157: so o Reel por URL directa" % (IG_FILTRO_URL, url))]
    return []


def _motivos_scrap_fase(c: dict, declarado) -> tuple[str | None, list]:
    import rota_do_scrap_social as RSS                                  # noqa: PLC0415
    aq = c.get("ACQUISITION") or {}
    fase = aq.get("FASE")
    dec = declarado(fase)
    plat = dec.get("PLATAFORMA") or aq.get("PLATFORM")
    m = []
    if dec.get("CAPACIDADE") and dec.get("CAPACIDADE") == declarado(RSS.IG_FASE_LISTAR).get("CAPACIDADE"):
        ok, porque = RSS.instagram_listar_permitido()
        if not ok:
            m.append(("LISTAGEM_NAO_AUTORIZADA", "fase %s lista a conta (%s); D157: so o Reel por URL directa"
                      % (fase, porque)))
    if plat not in AMBITO:
        m.append(("FORA_DO_AMBITO_AUTORIZADO", "plataforma %s fora do ambito do T9 (%s)"
                  % (plat, ", ".join(sorted(AMBITO)))))
    elif fase not in FASES_DO_AMBITO and not m:
        m.append(("FORA_DO_AMBITO_AUTORIZADO", "SCRAP_FASE/%s: %s — %s" % (fase, plat, AMBITO[plat])))
    m += _reel_por_url_directa(plat, aq) + _rastro_do_dono(plat, aq) + _politica_do_contrato(c)
    ok, porque = RSS.conferir(aq)
    if not ok:
        m.append(("ROTA_NAO_CONFERIDA", porque))
    return plat, m


def _motivos_feed(c: dict, estado_de) -> list:
    import validar_contratos as VC                                      # noqa: PLC0415
    aq = c.get("ACQUISITION") or {}
    m = _rastro_do_dono("YOUTUBE", aq)
    if not c.get("ROUTE_POLICY_STATUS"):
        m.append(("SEM_RASTRO_DE_POLITICA", "o contrato nao traz ROUTE_POLICY_STATUS"))
    m += _politica_do_contrato(c)
    ok, porque = VC.route_resolved(c)
    if not ok:
        m.append(("ROTA_NAO_CONFERIDA", porque))
    e = estado_de(c["SOURCE_ID"])
    if e != "READY_FOR_COLLECTION":
        m.append(("ESTADO_NAO_READY", "estado no livro do ciclo de vida: %s" % (e or "NAO SEI (fonte ausente)")))
    return m


def triagem_social(contratos: dict, *, estado_de=None) -> dict:
    """A porta social. {"ACEITES": [SOURCE_ID], "RECUSADAS": [{SOURCE_ID, PLATAFORMA, STRATEGY, FASE, MOTIVO,
    PORQUE, MOTIVOS}], "RECUSADAS_POR_MOTIVO", "POR_PLATAFORMA", "NAO_SOCIAIS": n}. Sem rede, sem escrita.
    `estado_de(source_id) -> estado`: o livro do ciclo de vida (por omissao o desta arvore); so e lido para feeds."""
    import validar_contratos as VC                                      # noqa: PLC0415
    import rota_do_scrap_social as RSS                                  # noqa: PLC0415
    if estado_de is None:
        import lifecycle as LC                                          # noqa: PLC0415
        livro = {}

        def estado_de(s):
            if not livro:
                livro.update(LC._ler_bruto())
            return LC.estado_de(s, livro)
    cache: dict = {}

    def declarado(fase):
        if fase not in cache:
            cache[fase] = RSS._declarado(fase) if fase else {"FASE_EXISTE": False}
        return cache[fase]
    aceites, recusadas, nao_sociais = [], [], 0
    for s, c in sorted(contratos.items()):
        aq = c.get("ACQUISITION") or {}
        st, plat = aq.get("STRATEGY"), None
        if st in NAO_SOCIAIS:
            nao_sociais += 1
            continue
        if st not in VC.STRATEGIES:
            m = [("STRATEGY_DESCONHECIDA", "ACQUISITION.STRATEGY=%r fora do motor (%s)"
                  % (st, ", ".join(sorted(VC.STRATEGIES))))]
        elif st == FEED:
            plat, m = "YOUTUBE", _motivos_feed(c, estado_de)
        else:
            plat, m = _motivos_scrap_fase(c, declarado)
        if not m:
            aceites.append(s)
            continue
        m = sorted(m, key=lambda x: MOTIVOS_DA_PORTA.index(x[0]))
        recusadas.append({"SOURCE_ID": s, "PLATAFORMA": plat, "STRATEGY": st, "FASE": aq.get("FASE"),
                          "MOTIVO": m[0][0], "PORQUE": m[0][1],
                          "MOTIVOS": [{"MOTIVO": a, "PORQUE": b} for a, b in m]})
    plats: dict = {}
    for s in aceites:
        c = contratos[s]
        aq = c["ACQUISITION"]
        p = "YOUTUBE" if aq.get("STRATEGY") == FEED else (declarado(aq.get("FASE")).get("PLATAFORMA")
                                                          or aq.get("PLATFORM"))
        plats.setdefault(p, {"ACEITES": 0, "RECUSADAS": 0})["ACEITES"] += 1
    for r in recusadas:
        plats.setdefault(r["PLATAFORMA"] or "NAO_SEI", {"ACEITES": 0, "RECUSADAS": 0})["RECUSADAS"] += 1
    return {"ACEITES": aceites, "RECUSADAS": recusadas,
            "RECUSADAS_POR_MOTIVO": dict(Counter(r["MOTIVO"] for r in recusadas)),
            "POR_PLATAFORMA": plats, "NAO_SOCIAIS": nao_sociais, "AMBITO": AMBITO}


def fontes_sociais(contratos: dict, *, estado_de=None) -> list[str]:
    """Os SOURCE_ID que a porta social aceita. Quem quiser o PORQUE das recusas le `triagem_social`."""
    return triagem_social(contratos, estado_de=estado_de)["ACEITES"]


# ── C2 (FREIO-SOCIAL, 26/09): O TETO DO PEDIDO NA ONDA NAO E O DO CONTRATO ──────
# O contrato LinkedIn escreve `teto: 2` (quantos videos por conta). Com 2 contas numa
# onda isso da 2 x (1 pagina + 2 posts) = 6 pedidos a linkedin.com — passa o teto D38.
# A onda pede `teto=1` por conta (2 x 2 = 4). O contrato nao muda: e a onda que decide
# quanto gasta, e escreve-o no pedido.
TETO_LINKEDIN_NA_ONDA = 1
CONTAS_LINKEDIN_POR_ONDA = 2
# D124 (dono, 27/09): o TETO_D38 = 5 fixo SAIU. O teto de cada dominio e o ORCAMENTO VIGENTE da politica
# adaptativa (`coleta/cortesia_adaptativa.py`), ou o manual declarado em SINTONIA_TETO_POR_HOST.
# (TETO_LINKEDIN_NA_ONDA = 1 fica: e a decisao C2 sobre quantos videos por conta, nao um teto de dominio.)


def teto_do_dominio(d: str) -> int:
    import os                                                       # noqa: PLC0415
    v = os.environ.get("SINTONIA_TETO_POR_HOST")
    if v:
        return int(v)
    sys.path.insert(0, str(RAIZ / "coleta"))
    import cortesia_adaptativa as CA                                # noqa: PLC0415 — o dono unico (D124)
    return CA.teto_vigente(d)


def pedido_de(c: dict, *, teto_linkedin: int | None = TETO_LINKEDIN_NA_ONDA) -> Pedido:
    aq = c["ACQUISITION"]
    f = {"fase": aq["FASE"], "fonte": c["SOURCE_ID"], "pais": "IT", "universo": c["TERRITORY"]}
    f.update({k: str(v) for k, v in (aq.get("FILTROS") or {}).items()})
    if aq.get("FASE") == "video-linkedin" and teto_linkedin is not None:
        f["teto"] = str(teto_linkedin)
    return Pedido(alvo=c["TERRITORY"], filtros=f)


def previsto_linkedin(teto: int) -> dict:
    """Pedidos por conta, LIDOS no codigo (adaptador_linkedin.video_da_pagina_publica):
    1 pagina + ate `teto` posts a linkedin.com; ate `teto` MP4 + ate `teto` legendas a licdn.com."""
    return {"linkedin.com": 1 + teto, "licdn.com": 2 * teto}


#: MEDIDO offline (SOCIAL-QUALIFICAR): 3 a youtube.com + 1 a googlevideo.com por video ate ~9,7 MiB (D41: um orcamento).
PREVISTO_YOUTUBE_VIDEO_CURTO = {"youtube.com": 4}


def rodadas(linhas: list[dict], *, teto_linkedin: int = TETO_LINKEDIN_NA_ONDA,
            contas_li: int = CONTAS_LINKEDIN_POR_ONDA) -> list[dict]:
    """As ondas da passagem A: ate `contas_li` contas LinkedIn + 1 canal YouTube por onda
    (dominios diferentes). Cada onda leva o PREVISTO por dominio e diz se cabe no teto do dominio (D124).
    Previsto e o maximo que o codigo pode pedir; o freio (`coleta/teto_da_onda.py`) trava o resto."""
    li = [l["SOURCE_ID"] for l in linhas if l.get("NA_ONDA") and l.get("FASE") == "video-linkedin"]
    yt = [l["SOURCE_ID"] for l in linhas if l.get("NA_ONDA") and l.get("FASE") in ("canal-youtube", "audio-youtube")]
    n = max((len(li) + contas_li - 1) // contas_li, len(yt))
    fora = []
    for i in range(n):
        contas = li[i * contas_li:(i + 1) * contas_li]
        canal = yt[i:i + 1]
        prev = {}
        for _ in contas:
            for d, k in previsto_linkedin(teto_linkedin).items():
                prev[d] = prev.get(d, 0) + k
        for _ in canal:
            for d, k in PREVISTO_YOUTUBE_VIDEO_CURTO.items():
                prev[d] = prev.get(d, 0) + k
        fora.append({"ONDA": i + 1, "LINKEDIN": contas, "YOUTUBE": canal, "PREVISTO_POR_DOMINIO": prev,
                     "CABE_NO_TETO": all(v <= teto_do_dominio(d) for d, v in prev.items())})
    return fora


def plano() -> dict:
    import orquestrador as ORQ
    contratos = {c["SOURCE_ID"]: c for c in json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    ctx = GATE._contexto()
    tri = triagem_social(contratos)
    linhas = []
    for s in tri["ACEITES"]:
        c = contratos[s]
        aq = c["ACQUISITION"]
        g = GATE.avaliar(s, **ctx)
        falta, executor, sobra, status = [], None, [], None
        if not g["COLLECTION_ELIGIBLE"]:
            falta.append("PORTAO:%s" % g["MOTIVO"])
        try:
            p = pedido_de(c)
            pl = REC.resolver(p)
            e = pl.executores[0] if pl.executores else {}
            executor = e.get("id")
            sobra = sorted(set(p.filtros) - REC.filtros_consumidos(e) - {"pais", "universo"}) if e else []
            status = ORQ.correr(p, so_plano=True)["STATUS"]
            if executor != EXECUTOR:
                falta.append("EXECUTOR:%s" % executor)
            if sobra:
                falta.append("FILTRO_NAO_CONSUMIDO:%s" % ",".join(sobra))
            if p.alvo != c["TERRITORY"]:
                falta.append("ALVO:%s" % p.alvo)
        except Exception as ex:                                   # noqa: BLE001
            falta.append("PEDIDO_RECUSADO:%s:%s" % (type(ex).__name__, str(ex)[:80]))
        buracos = []
        if aq.get("FASE") == "canal-youtube":
            buracos.append("CHAVE_YOUTUBE_SO_NO_GITHUB")
        buracos.append("DOCUMENT_ID_RULE_FORA_DA_TABELA")
        linhas.append({"SOURCE_ID": s, "TERRITORY": c["TERRITORY"], "FASE": aq.get("FASE"),
                       "ESTADO": LC.estado_de(s), "PORTAO": g["MOTIVO"], "READY_RULE": g["READY_RULE"],
                       "EXECUTOR": executor, "PLANO": status, "FALTA": falta, "BURACOS": buracos,
                       "NA_ONDA": not falta,
                       "PEDIDO_EM_PROCESSO": "Pedido(alvo=%r, filtros=%r)" % (
                           c["TERRITORY"], pedido_de(c).filtros if not any(
                               f.startswith("PEDIDO_RECUSADO") for f in falta) else None)})
    na_onda = [l for l in linhas if l["NA_ONDA"]]
    return {"DATASET": "SOC-ONDA2-PLANO-ONDA-SOCIAL-V1", "SO_PLANO": True,
            "FONTES_SOCIAIS_NO_LIVRO": len(linhas),
            "NA_ONDA": len(na_onda),
            "NA_ONDA_POR_FASE": dict(Counter(l["FASE"] for l in na_onda)),
            "FORA_POR_MOTIVO": dict(Counter(f.split(":")[0] + ":" + f.split(":")[1]
                                            for l in linhas for f in l["FALTA"])),
            "PORTA_SOCIAL": {k: tri[k] for k in ("RECUSADAS_POR_MOTIVO", "POR_PLATAFORMA", "NAO_SOCIAIS")},
            "RECUSADAS_NA_PORTA": tri["RECUSADAS"],
            "BURACOS": {k: {"O_QUE": v[0], "DONO": v[1]} for k, v in BURACOS.items()},
            "TETO_LINKEDIN_NA_ONDA": TETO_LINKEDIN_NA_ONDA,
            "RODADAS": rodadas(linhas),
            "LINHAS": linhas}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    r = plano()
    print(json.dumps({k: v for k, v in r.items() if k not in ("LINHAS", "BURACOS", "RECUSADAS_NA_PORTA")},
                     ensure_ascii=False, indent=1))
    for l in r["LINHAS"]:
        if l["NA_ONDA"]:
            print("  NA ONDA  %-11s %-4s %-15s -> %s (%s)" % (l["SOURCE_ID"], l["TERRITORY"], l["FASE"],
                                                            l["EXECUTOR"], l["PLANO"]))
    if a.json:
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
