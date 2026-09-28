#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOCIAL-ATE-A-SALA · D — a ENTRADA POR URL ACHADO: reel e post LinkedIn achados -> pedido do Scrap.

    py coleta/social_por_url_achado.py --plano --achados=<POSTS-PARA-O-SCRAP.jsonl> --saida=<PLANO.json>
    py coleta/social_por_url_achado.py --plano ... --registar --copia       (candidatas numa COPIA da fila)
    py coleta/social_por_url_achado.py --plano ... --registar --vivo        (no vivo: SO com curadoria/PARAR.flag)
    py coleta/social_por_url_achado.py --anexar --plano=<PLANO.json> --linha=<n> --run-id=<RUN_ID>

POR QUE EXISTE (buracos 2 e 6 do estudo do coordenador, 27/09)
--------------------------------------------------------------
O Instagram nao lista os Reels de uma conta a partir de um datacenter
(`instagram.profile.discovery` = PARTIAL / ROUTE_NOT_ALLOWED), e o perfil de uma pessoa no
LinkedIn fecha (999). O que ABRE e a publicacao pelo endereco: o Reel (D22) e o post (D23
organizacao; D24 pessoa). Quem acha esses enderecos e a BUSCA (D93) ou uma PESSOA (D94) — e
a linha da busca (`coleta/linha_busca.py`, ramo `linha-busca-v1`) ja os separa num ficheiro
proprio, `POSTS-PARA-O-SCRAP.jsonl`, com a proveniencia inteira. Este ficheiro le ESSE
formato (URL + PROVENIENCIA{ESPECIE, CONSULTA, MOTOR, POSICAO, INSTANTE...}) e diz, a cada
endereco, o que o Scrap pode pedir:

    REEL                -> fase `captura-reel`  (filtro `url`)
    POST DE ORGANIZACAO -> fase `video-linkedin` (filtro `pagina` = a pagina da organizacao)

E NAO E UM SEGUNDO COLETOR: nao sai para a rede, nao corre o Scrap, nao escreve na Sala. Monta
o pedido e a proveniencia; quem corre e o orquestrador (D28), com a VPN IT, pelo coordenador.

A IDENTIDADE DESCE DO LIVRO, NUNCA DA URL
-----------------------------------------
    URL NAO E SOURCE_ID. HANDLE NAO E SOURCE_ID.

O SOURCE_ID da conta/organizacao vem dos livros do Curator (contratos, registo de alocacao) ou
de uma candidata da fila que ja o ganhou. Conta sem SOURCE_ID: entra como CANDIDATA pela porta
canonica (`candidatas/fonte_nova.registar`) e o pedido ESPERA — nada se inventa. Conta que o
endereco nao diz (um `/reel/<codigo>` nao nomeia quem publicou; um `/posts/<vanity>_...` nao
diz se o autor e organizacao ou pessoa): NAO SEI, e nao se regista nenhuma conta adivinhada.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

VIVOS = ("source-curator-service-v1", "ponte-viva")
PARAR = RAIZ / "curadoria" / "PARAR.flag"
QUEM = "coleta/social_por_url_achado.py"

# ── as duas especies de proveniencia (D93 busca · D94 pessoa) e o que cada uma TEM de trazer ──
ACHADO_POR_BUSCA, ACHADO_POR_PESSOA = "ACHADO_POR_BUSCA", "ACHADO_POR_PESSOA"
EXIGIDO = {
    # o formato da linha da busca (`linha_busca.colher_um` -> POSTS-PARA-O-SCRAP.jsonl)
    ACHADO_POR_BUSCA: ("CONSULTA", "MOTOR", "POSICAO", "INSTANTE"),
    # quem achou, onde, quando — os mesmos tres de `fonte_nova.registar` (QUEM_VIU/ONDE_VIU)
    ACHADO_POR_PESSOA: ("QUEM", "ONDE", "INSTANTE"),
}
RE_INSTANTE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")

# ── os enderecos: so publicacoes. Perfil nao e item (NAME != PROFILE != PERSON, D94-b) ──────────
RE_REEL = re.compile(r"^https?://(?:www\.)?instagram\.com/(?:(?P<handle>[A-Za-z0-9_.]+)/)?"
                     r"(?P<tipo>reel|reels|p|tv)/(?P<codigo>[A-Za-z0-9_-]{5,})/?(?:[?#].*)?$", re.I)
RE_POST_LI = re.compile(r"^https?://(?:[a-z]{2,3}\.)?linkedin\.com/posts/(?P<vanity>[A-Za-z0-9%._-]+?)_"
                        r"[^/?#]*?activity-(?P<act>\d{16,20})", re.I)
RE_UPDATE_LI = re.compile(r"^https?://(?:[a-z]{2,3}\.)?linkedin\.com/feed/update/urn:li:activity:"
                          r"(?P<act>\d{16,20})", re.I)
RE_CONTA_IG = re.compile(r"instagram\.com/([A-Za-z0-9_.]+)/?$", re.I)
RE_CONTA_LI_ORG = re.compile(r"linkedin\.com/company/([^/?#]+)", re.I)
RE_CONTA_LI_PESSOA = re.compile(r"linkedin\.com/(?:in|pub)/([^/?#]+)", re.I)
NAO_SAO_CONTAS = {"reel", "reels", "p", "tv", "explore", "stories", "accounts"}


def especie_do_endereco(url: str) -> dict:
    """→ {ESPECIE: REEL | POST_LINKEDIN | NAO_E_PUBLICACAO, ...}. Puro, sem rede."""
    u = (url or "").strip()
    m = RE_REEL.match(u)
    if m:
        h = (m.group("handle") or "").lower()
        return {"ESPECIE": "REEL", "CODIGO": m.group("codigo"),
                "CONTA_NO_ENDERECO": h if h and h not in NAO_SAO_CONTAS else None}
    m = RE_POST_LI.match(u)
    if m:
        return {"ESPECIE": "POST_LINKEDIN", "ACTIVITY_ID": m.group("act"),
                "VANITY": m.group("vanity").lower()}
    m = RE_UPDATE_LI.match(u)
    if m:
        return {"ESPECIE": "POST_LINKEDIN", "ACTIVITY_ID": m.group("act"), "VANITY": None}
    return {"ESPECIE": "NAO_E_PUBLICACAO",
            "PORQUE": "nao e reel nem post LinkedIn: perfil, pagina ou outra plataforma (NAME != PROFILE != "
                      "PERSON: um perfil nao e item e so vira candidata com prova)"}


def falta_na_proveniencia(p: dict | None) -> list[str]:
    """O que falta a proveniencia para o item poder dizer de onde veio. Vazio = inteira."""
    p = p or {}
    esp = p.get("ESPECIE")
    if esp not in EXIGIDO:
        return ["ESPECIE (%r nao e %s nem %s)" % (esp, ACHADO_POR_BUSCA, ACHADO_POR_PESSOA)]
    falta = [k for k in EXIGIDO[esp] if not str(p.get(k) if p.get(k) is not None else "").strip()]
    if esp == ACHADO_POR_BUSCA and "POSICAO" not in falta:
        try:
            if int(p["POSICAO"]) < 1:
                falta.append("POSICAO (< 1)")
        except (TypeError, ValueError):
            falta.append("POSICAO (nao e numero)")
    if "INSTANTE" not in falta and not RE_INSTANTE.match(str(p["INSTANTE"])):
        falta.append("INSTANTE (sem forma de instante ISO)")
    return falta


# ── os livros (lidos; a escrita so pela porta) ─────────────────────────────────────────────
def _ler(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else {}


def livros(raiz: Path = RAIZ) -> dict:
    """Os livros de identidade da MESMA arvore (nunca os de outra: os CAND-ids colidem)."""
    return {"CONTRATOS": _ler(raiz / "curadoria" / "italy_contracts_curator.json"),
            "ALLOC": _ler(raiz / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"),
            "FILA": _ler(raiz / "candidatas" / "FONTES-CANDIDATAS.json")}


def _sid_da_candidata(cid: str, alloc: dict) -> str | None:
    for n in alloc.get("NOVAS") or []:
        if n.get("CANDIDATE_ID") == cid:
            return n.get("SOURCE_ID")
    return None


def fonte_da_conta(plataforma: str, conta: str, lv: dict) -> dict:
    """→ {SOURCE_IDS: [...], CANDIDATAS: [{CANDIDATA_ID, SOURCE_ID, URL, TIPO_DE_CONTA}]}.

    LinkedIn: o slug de `/company/` nos contratos e no registo (`SOURCE_NATIVE_ID`). Instagram:
    o handle no contrato (`INSTAGRAM_HANDLE`). Nos dois, a fila pelo endereco da conta.
    """
    conta = (conta or "").lower().strip("/@ ")
    sids, cands = set(), []
    for c in lv["CONTRATOS"].get("FONTES") or []:
        aq = c.get("ACQUISITION") or {}
        chave = aq.get("LINKEDIN_SLUG") if plataforma == "LINKEDIN" else aq.get("INSTAGRAM_HANDLE")
        if chave and str(chave).lower().strip("/@ ") == conta:
            sids.add(c["SOURCE_ID"])
    if plataforma == "LINKEDIN":
        for n in lv["ALLOC"].get("NOVAS") or []:
            if n.get("SOURCE_NATIVE_ID_KIND") == "LINKEDIN_ORG_SLUG" and \
                    (n.get("SOURCE_NATIVE_ID") or "").lower() == conta:
                sids.add(n["SOURCE_ID"])
    for c in lv["FILA"].get("CANDIDATAS") or []:
        if c.get("TIPO") != plataforma:
            continue
        url = c.get("URL") or ""
        if plataforma == "INSTAGRAM":
            m, tipo = RE_CONTA_IG.search(url), "CONTA"
        else:
            m, tipo = RE_CONTA_LI_ORG.search(url), "ORGANIZACAO"
            if not m:
                m, tipo = RE_CONTA_LI_PESSOA.search(url), "PESSOA"
        if m and m.group(1).lower().strip("/") == conta:
            sid = c.get("SOURCE_ID") or _sid_da_candidata(c["CANDIDATA_ID"], lv["ALLOC"])
            cands.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "SOURCE_ID": sid, "URL": url,
                          "ESTADO": c.get("ESTADO"), "TIPO_DE_CONTA": tipo})
            if sid:
                sids.add(sid)
    return {"SOURCE_IDS": sorted(sids), "CANDIDATAS": cands}


def _territorio(sid: str) -> str | None:
    m = re.match(r"^[A-Z]{2}-(T\d+)-\d+$", sid or "")
    return m.group(1) if m else None


def _pedido(sid: str, filtros: dict) -> dict:
    """Os filtros do `Pedido` do orquestrador (como `maestro_social.pedido_da_fonte`)."""
    t = _territorio(sid)
    return {"alvo": t, "filtros": dict(filtros, fonte=sid, pais="IT", universo=t)}


def conta_declarada(achado: dict, plataforma: str) -> tuple[str | None, str | None]:
    """A conta que o ACHADO diz (campo CONTA, visto no resultado ou pela pessoa). → (conta, tipo)."""
    v = str(achado.get("CONTA") or "").strip()
    if not v:
        return None, None
    if plataforma == "INSTAGRAM":
        m = RE_CONTA_IG.search(v)
        return ((m.group(1) if m else v).lower().strip("/@ "), "CONTA")
    m = RE_CONTA_LI_ORG.search(v)
    if m:
        return m.group(1).lower().strip("/"), "ORGANIZACAO"
    m = RE_CONTA_LI_PESSOA.search(v)
    if m:
        return m.group(1).lower().strip("/"), "PESSOA"
    return None, None   # um nome solto nao diz se e organizacao ou pessoa


def planear_um(achado: dict, lv: dict, vistos: set) -> dict:
    """UM achado → a linha do plano. Puro: nao escreve, nao sai para a rede."""
    url = str(achado.get("URL") or "").strip()
    prov = dict(achado.get("PROVENIENCIA") or {})
    linha = {"URL": url, "PROVENIENCIA": prov, "UNIVERSO": achado.get("UNIVERSO"),
             "CORRIDA_DA_BUSCA": achado.get("CORRIDA")}
    falta = falta_na_proveniencia(prov)
    if falta:
        linha.update(ESTADO="REJEITADO", PORQUE="PROVENIENCIA_INCOMPLETA: falta %s" % ", ".join(falta))
        return linha
    esp = especie_do_endereco(url)
    linha["ENDERECO"] = esp
    if esp["ESPECIE"] == "NAO_E_PUBLICACAO":
        linha.update(ESTADO="NAO_E_ITEM", PORQUE=esp["PORQUE"])
        return linha
    alvo = ("IG", esp["CODIGO"]) if esp["ESPECIE"] == "REEL" else ("LI", esp["ACTIVITY_ID"])
    if alvo in vistos:
        linha.update(ESTADO="DUPLICADO", PORQUE="o mesmo %s ja esta neste plano (outra consulta/posicao)" % alvo[1])
        return linha
    vistos.add(alvo)
    plataforma = "INSTAGRAM" if esp["ESPECIE"] == "REEL" else "LINKEDIN"
    conta, tipo = conta_declarada(achado, plataforma)
    no_endereco = esp.get("CONTA_NO_ENDERECO") if plataforma == "INSTAGRAM" else esp.get("VANITY")
    if conta and no_endereco and conta != no_endereco:
        linha.update(ESTADO="CONTA_EM_CONFLITO",
                     PORQUE="o achado diz %r e o endereco diz %r: identidade a conferir por humano"
                            % (conta, no_endereco))
        return linha
    conta = conta or no_endereco
    linha["CONTA"] = conta
    if not conta:
        linha.update(ESTADO="CONTA_NAO_SEI",
                     PORQUE=("o endereco /reel/<codigo> nao nomeia quem publicou e o achado nao traz CONTA: "
                             "o SOURCE_ID nao se tira da URL (URL NAO E SOURCE_ID)") if plataforma == "INSTAGRAM"
                     else "o endereco do post nao nomeia o autor e o achado nao traz CONTA")
        return linha
    fonte = fonte_da_conta(plataforma, conta, lv)
    linha["IDENTIDADE"] = fonte
    if len(fonte["SOURCE_IDS"]) > 1:
        linha.update(ESTADO="IDENTIDADE_EM_COLISAO",
                     PORQUE="a conta %r liga a %d fontes (%s): decisao humana"
                            % (conta, len(fonte["SOURCE_IDS"]), ", ".join(fonte["SOURCE_IDS"])))
        return linha
    if plataforma == "LINKEDIN":
        pessoa = tipo == "PESSOA" or any(c["TIPO_DE_CONTA"] == "PESSOA" for c in fonte["CANDIDATAS"])
        if pessoa:
            linha.update(ESTADO="BLOQUEADO_POR_DECISAO",
                         PORQUE=("post de PESSOA: a rota existe (`adaptador_linkedin.video_de_post_publico`, D24) "
                                 "mas NAO tem fase no Scrap, e a D37 tirou-lhe a cobertura do robots — "
                                 "decisao do dono. A pessoa fica como pista, nao como item."))
            return linha
        if not fonte["SOURCE_IDS"] and tipo != "ORGANIZACAO":
            # o vanity do /posts/ nao diz se e /company/ ou /in/: registar um dos dois seria adivinhar
            linha.update(ESTADO="CONTA_NAO_SEI",
                         PORQUE=("o autor %r nao e fonte nem candidata, e o endereco do post nao diz se e "
                                 "organizacao (/company/) ou pessoa (/in/): sem CONTA no achado nao se regista "
                                 "nenhuma das duas" % conta))
            return linha
    if not fonte["SOURCE_IDS"]:
        cand = next((c for c in fonte["CANDIDATAS"]), None)
        linha.update(ESTADO="ESPERA_SOURCE_ID",
                     CANDIDATA_ID=(cand or {}).get("CANDIDATA_ID"),
                     A_REGISTAR=None if cand else _ficha_de_candidata(plataforma, conta, url, prov),
                     PORQUE=("a conta %r ja e a candidata %s (%s) e ainda nao tem SOURCE_ID: o pedido espera o "
                             "QUALIFY" % (conta, cand["CANDIDATA_ID"], cand.get("ESTADO")) if cand else
                             "a conta %r nao e fonte nem candidata: entra como CANDIDATA pela porta canonica "
                             "(fonte_nova.registar) e o pedido espera o QUALIFY" % conta))
        return linha
    sid = fonte["SOURCE_IDS"][0]
    if plataforma == "INSTAGRAM":
        filtros = {"fase": "captura-reel", "url": url}
        alvo_d = {"CODIGO": esp["CODIGO"]}
        decisao = "D22 (Reel por URL directa)"
    else:
        filtros = {"fase": "video-linkedin", "pagina": "https://www.linkedin.com/company/%s/" % conta, "teto": 2}
        alvo_d = {"ACTIVITY_ID": esp["ACTIVITY_ID"], "POST_URL": url,
                  "LIMITE": ("a pagina da organizacao serve so os posts RECENTES: se o post achado nao estiver "
                             "entre eles a corrida nao o traz — `--anexar` mede ALVO_NA_COLHEITA")}
        decisao = "D23 (video de pagina publica de ORGANIZACAO)"
    linha.update(ESTADO="PEDIDO", SOURCE_ID=sid, FASE=filtros["fase"], PEDIDO=_pedido(sid, filtros),
                 ALVO_ACHADO=alvo_d, DECISAO_DO_DONO=decisao,
                 OWNER_AUTHORIZED="SIM", EXECUTOR="scrap-colheita (orquestrador, D28)")
    return linha


def _ficha_de_candidata(plataforma: str, conta: str, url: str, prov: dict) -> dict:
    """Os argumentos EXACTOS de `fonte_nova.registar` para a conta que publicou (nada inventado)."""
    como = ("consulta «%s», motor %s, posicao %s, %s" % (prov.get("CONSULTA"), prov.get("MOTOR"),
                                                          prov.get("POSICAO"), prov.get("INSTANTE"))
            if prov.get("ESPECIE") == ACHADO_POR_BUSCA else
            "achado por %s em %s, %s" % (prov.get("QUEM"), prov.get("ONDE"), prov.get("INSTANTE")))
    if plataforma == "INSTAGRAM":
        nome, endereco, decisao = "@%s — Instagram" % conta, "https://www.instagram.com/%s/" % conta, "D22"
    else:
        nome, endereco, decisao = "%s — LinkedIn" % conta, "https://www.linkedin.com/company/%s/" % conta, "D23"
    return {"tipo": plataforma, "pais": "NAO SEI", "nome": nome, "url": endereco,
            "para_que": "conta que publicou %s achado (%s): candidata a fonte social (%s/D93/D94)"
                        % ("um reel" if plataforma == "INSTAGRAM" else "um post", prov.get("ESPECIE"), decisao),
            "quem_viu": QUEM, "onde_viu": url,
            "nota": ("%s: %s. PROVA_IDENTIDADE=NAO SEI (NAME != PROFILE != PERSON: a conta so vira fonte com o "
                     "site oficial a apontar para ela). PAIS_PROVA=NAO SEI" % (prov.get("ESPECIE"), como))}


def planear(achados: list[dict], lv: dict | None = None) -> dict:
    lv = lv if lv is not None else livros()
    vistos: set = set()
    linhas = [planear_um(a, lv, vistos) for a in achados]
    from collections import Counter
    return {"DATASET": "SOCIAL-POR-URL-ACHADO-V1", "GERADO_EM": datetime.now().astimezone().isoformat(
            timespec="seconds"), "QUEM": QUEM,
            "RESUMO": dict(Counter(l["ESTADO"] for l in linhas)), "LINHAS": linhas}


def registar_candidatas(plano: dict) -> list[dict]:
    """Escreve pela PORTA CANONICA as contas A_REGISTAR. Idempotente (a porta devolve a que ja existe)."""
    import fonte_nova as FN                                          # noqa: PLC0415
    feitas = []
    for l in plano["LINHAS"]:
        f = l.get("A_REGISTAR")
        if not f:
            continue
        c = FN.registar(f["tipo"], f["pais"], f["nome"], f["url"], f["para_que"], f["quem_viu"],
                        f["onde_viu"], f["nota"])
        l["CANDIDATA_ID"] = c["CANDIDATA_ID"]
        feitas.append({"CANDIDATA_ID": c["CANDIDATA_ID"], "URL": c["URL"], "ESTADO": c["ESTADO"]})
    return feitas


def anexar(linha: dict, run_id: str, balcao: Path | None = None) -> dict:
    """Depois da corrida: a proveniencia do achado ao lado do ENVELOPE, e se o alvo veio na colheita."""
    balcao = Path(balcao or RAIZ / "data" / "colheita" / "scrap") / str(run_id)
    env_p = balcao / "ENVELOPE.json"
    env = json.loads(env_p.read_text(encoding="utf-8")) if env_p.exists() else {}
    alvo = (linha.get("ALVO_ACHADO") or {})
    chave = alvo.get("CODIGO") or alvo.get("ACTIVITY_ID")
    col = env.get("COLHEITA") if isinstance(env.get("COLHEITA"), list) else []
    veio = any(chave and chave in json.dumps(it.get("OBSERVACAO") or {}, ensure_ascii=False) for it in col)
    saida = {"RUN_ID": run_id, "SOURCE_ID": linha.get("SOURCE_ID"), "URL": linha.get("URL"),
             "PROVENIENCIA": linha.get("PROVENIENCIA"), "ALVO_ACHADO": alvo,
             "ALVO_NA_COLHEITA": ("NAO SEI (sem envelope desta corrida)" if not env else
                                  "SIM" if veio else "NAO")}
    balcao.mkdir(parents=True, exist_ok=True)
    (balcao / "PROVENIENCIA-DO-ACHADO.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1),
                                                         encoding="utf-8")
    return saida


def _ler_achados(p: Path) -> list[dict]:
    texto = Path(p).read_text(encoding="utf-8")
    if Path(p).suffix == ".jsonl":
        return [json.loads(l) for l in texto.splitlines() if l.strip()]
    d = json.loads(texto)
    return d if isinstance(d, list) else d.get("ACHADOS") or []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plano", nargs="?", const=True)
    ap.add_argument("--achados")
    ap.add_argument("--saida")
    ap.add_argument("--registar", action="store_true")
    ap.add_argument("--copia", action="store_true")
    ap.add_argument("--vivo", action="store_true")
    ap.add_argument("--anexar", action="store_true")
    ap.add_argument("--linha", type=int)
    ap.add_argument("--run-id", dest="run_id")
    a = ap.parse_args(argv)
    if a.anexar:
        plano = json.loads(Path(a.plano).read_text(encoding="utf-8"))
        print(json.dumps(anexar(plano["LINHAS"][a.linha], a.run_id), ensure_ascii=False, indent=1))
        return 0
    if not a.achados:
        ap.error("--achados e obrigatorio com --plano")
    plano = planear(_ler_achados(Path(a.achados)))
    if a.registar:
        no_vivo = any(v in str(RAIZ).replace("\\", "/") for v in VIVOS)
        if no_vivo and not (a.vivo and PARAR.exists()):
            print("RECUSADO: no vivo so com --vivo E o bot parado (%s presente)" % PARAR.name)
            return 2
        if not no_vivo and not a.copia:
            print("RECUSADO: fora do vivo, declare --copia")
            return 2
        plano["CANDIDATAS_REGISTADAS"] = registar_candidatas(plano)
    print(json.dumps(plano["RESUMO"], ensure_ascii=False))
    if a.saida:
        Path(a.saida).write_text(json.dumps(plano, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
