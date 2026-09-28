#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINHA-BUSCA — a coleta ASSUNTO-PRIMEIRO dentro da Collection canonica (D93, 27/09).

A casa e FONTE-PRIMEIRO: uma fonte sobe seis degraus antes de a primeira pagina dela ser colhida. O Google
e ASSUNTO-PRIMEIRO: pergunta-se o assunto e vem a pagina. Esta linha faz o segundo SEM segunda Collection:
  DISCOVER  a consulta num motor de busca (COL-LAW-207) -> endereco, posicao, instante
  FETCH     UMA pagina por resultado, pelo transporte canonico (`coleta/scrap_http.buscar_bytes`: robots vivo,
            D91; teto por dominio no livro do `coleta/teto_da_onda`, <= 5/24 h; saltos vigiados)
  RAW       os bytes com sha256 + a proveniencia ACHADO_POR_BUSCA (consulta, motor, posicao, instante) e o
            ESTADO DA FONTE NO MOMENTO (D93.2)
  CANDIDATA o dominio do publicador entra pela porta canonica (`candidatas/fonte_nova.registar`)
  PORTAO    `curadoria/collection_gate.avaliar_achado_por_busca` — o ponto que exigia fonte aprovada (D93)
  ADMISSION a normal: `orquestrador.item_documental_para_a_porta` + `admissao.decidir` + `pronto_para_inteligencia`
  SALA      `sala_de_espera.pousar` (so com --pousar, e so com a Sala canonica activa)

    py coleta/linha_busca.py --plano [--r3=<LACUNAS-PARA-A-COLETA-R3.json>] --saida=<pasta>
    py coleta/linha_busca.py --medir-motores --autorizado --saida=<pasta>
    py coleta/linha_busca.py --buscar --autorizado --motor=<M> --consultas=<CONSULTAS.json> --n=4 --saida=<pasta>
    py coleta/linha_busca.py --diagnosticar-cse --autorizado [--sem-portao-it] --saida=<pasta>   (1 chamada)
    py coleta/linha_busca.py --buscar --autorizado --sem-portao-it --motor=GOOGLE_CSE ...   (no Actions, sem VPN)
    py coleta/linha_busca.py --colher --autorizado --resultados=<RESULTADOS.json> --fila=<fila> --saida=<pasta> [--pousar]
    py coleta/linha_busca.py --ensaio --resultados=<fixture> --paginas=<pasta de bytes> --fila=<COPIA> --saida=<pasta>
    py coleta/linha_busca.py --marcar --saida=<pasta> --fila=<fila>      (D93.4: fonte recusada depois -> itens marcados)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

sys.path.insert(0, str(RAIZ / "ferramentas" / "linha_busca"))
sys.path.insert(0, str(RAIZ / "curadoria"))
import api_oficial as API                                             # noqa: E402
import consultas as CQ                                                # noqa: E402
import motores as MO                                                  # noqa: E402

LINHA = "LINHA-BUSCA"
ROTA_DA_PAGINA = "HTTP coleta/scrap_http.buscar_bytes (robots vivo D91 + teto_da_onda + saltos vigiados)"


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def host_de(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def raiz_do_site(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    return "%s://%s/" % (p.scheme or "https", p.netloc)


# ---------------------------------------------------------------- a fonte: candidata pela porta canonica
def _ledger(fila: Path, livro: Path = None) -> tuple:
    """(CAND -> SOURCE_ID, SOURCE_ID -> ultimo estado) no livro do Curator da MESMA arvore da fila.

    ⚠️ Nunca o livro de OUTRA arvore por omissao: os CAND-ids de filas diferentes colidem (memoria
    cand-ids-colidem-entre-lanes), e um CAND-0002 de uma copia apontaria para a fonte de outro. Fila sem
    livro ao lado = sem ligacao a SOURCE_ID (a menos que `livro` seja dado de proposito)."""
    livro = Path(livro) if livro else fila.resolve().parents[1] / "curadoria" / "LIFECYCLE-LEDGER-V1.json"
    cand, est = {}, {}
    if not livro.exists():
        return cand, est
    import re
    for t in json.loads(livro.read_text(encoding="utf-8")).get("TRANSICOES", []):
        est[t.get("SOURCE_ID")] = t.get("NEW_STATE")
        if "QUALIFY" in (t.get("REASON") or ""):
            for c in re.findall(r"CAND-\d{4}", t["REASON"]):
                cand[c] = t["SOURCE_ID"]
    return cand, est


def fontes_por_host(fila: Path, cand_sid: dict) -> dict:
    """{host: {SOURCE_ID, ...}} — as fontes JA registadas (com SOURCE_ID do Curator) em cada host da fila."""
    out = {}
    for c in json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]:
        sid = c.get("SOURCE_ID") or cand_sid.get(c["CANDIDATA_ID"])
        if sid:
            out.setdefault(host_de(c["URL"]), set()).add((sid, c["CANDIDATA_ID"]))
    return out


def fonte_do_publicador(url: str, r: dict, fila: Path, ledger: tuple) -> dict:
    """O dominio entra como CANDIDATA pela porta canonica (ou ja la esta). Devolve a identidade e o estado.

    Se o host JA tem exatamente UMA fonte com SOURCE_ID, e ela: nao se cria uma segunda candidata para o
    mesmo publicador. Com varias (portal de regiao: agricultura, politica, fitossanitario...) nao se escolhe
    uma ao acaso: a raiz do dominio entra como candidata propria."""
    import fonte_nova as FN
    FN.FILA = fila
    h = host_de(url)
    ja = (ledger[2] if len(ledger) > 2 else {}).get(h) or set()
    if len(ja) == 1:
        sid, cid = next(iter(ja))
        return {"SOURCE_ID": sid, "CANDIDATA_ID": cid, "FONTE_ESTADO_NO_MOMENTO": ledger[1].get(sid) or "NAO SEI",
                "IDENTIDADE": "SOURCE_ID do Curator (unica fonte registada neste host)"}
    pais = "IT" if h.endswith(".it") else "NAO SEI"
    nota = ("LINHA-BUSCA (D93): dominio do publicador de uma pagina achada por busca. PAIS_PROVA=%s. "
            "ACHADO_POR_BUSCA: consulta «%s», motor %s, posicao %s, %s" % (
                "dominio .it (prova fraca: o dominio, nao o conteudo)" if pais == "IT" else "NAO SEI",
                r["CONSULTA"], r["MOTOR"], r["POSICAO"], r["INSTANTE"]))
    linha = FN.registar("ORGANIZACAO", pais, h, raiz_do_site(url),
                        "%s: publicou pagina achada pela consulta «%s» (%s) — candidata a fonte recorrente"
                        % (r.get("FERRAMENTA") or "casco", r["CONSULTA"], r.get("UNIVERSO") or "NAO SEI"),
                        LINHA, "%s posicao %s em %s: %s" % (r["MOTOR"], r["POSICAO"], r["INSTANTE"], url), nota)
    cand_sid, est_sid = ledger[0], ledger[1]
    sid = linha.get("SOURCE_ID") or cand_sid.get(linha["CANDIDATA_ID"])
    if sid:
        return {"SOURCE_ID": sid, "CANDIDATA_ID": linha["CANDIDATA_ID"],
                "FONTE_ESTADO_NO_MOMENTO": est_sid.get(sid) or linha["ESTADO"], "IDENTIDADE": "SOURCE_ID do Curator"}
    # D93: a fonte ainda CANDIDATA — a identidade canonica que a casa lhe deu e o CANDIDATA_ID (a porta
    # canonica registou-a; nada inventado). Quando o QUALIFY lhe der SOURCE_ID, o livro do Curator liga os dois.
    return {"SOURCE_ID": linha["CANDIDATA_ID"], "CANDIDATA_ID": linha["CANDIDATA_ID"],
            "FONTE_ESTADO_NO_MOMENTO": linha["ESTADO"], "IDENTIDADE": "CANDIDATA_ID (D93: fonte ainda candidata)"}


# ---------------------------------------------------------------- a Admission normal
def texto_de(dados: bytes, media_type: str) -> tuple:
    import executor_texto_de_html as H
    import extratores_de_texto as XT
    if dados[:5] == b"%PDF-" or "pdf" in (media_type or ""):
        texto, _, _ = XT._de_pdf(dados, "application/pdf")
        return texto or "", "application/pdf", None
    texto, estado, erro, _ = H.extrair(dados, media_type or "text/html")
    return (texto or ""), "text/html", (None if texto else "%s %s" % (estado, erro or ""))


def admitir(dados: bytes, media_type: str, url: str, fonte: dict, r: dict, sha: str, capturado: str,
            corrida: str, raw_asset_id: int = None) -> dict:
    import admissao as adm
    import executor_texto_de_html as H
    import italy_executor as ex
    import orquestrador as ORQ
    texto, especie, erro = texto_de(dados, media_type)
    if not texto.strip():
        return {"RESULTADO": "NAO_SEI", "REGRA": "legivel", "MOTIVO": "sem texto (%s)" % erro, "READY": None}
    obs = {"SOURCE_ID": fonte["SOURCE_ID"], "SOURCE_URL": url, "CAPTURED_AT": capturado}
    tl = ex.tempo_e_lugar(obs, dados)
    est = {"SOURCE_ID": fonte["SOURCE_ID"], "TEXTO": texto, "DERIVED_ARTIFACT_ID": "busca-%s" % sha[:16],
           "RAW_ASSET_ID": raw_asset_id, "PARENT_SHA256": sha, "CAPTURED_AT": capturado, "TEMPO_E_LUGAR": tl,
           "SOURCE_URL": url}
    if especie == "text/html":
        est["RETRATO_DO_DETECTOR"] = H._retrato(dados)
    item = ORQ.item_documental_para_a_porta(est, source_id=fonte["SOURCE_ID"])
    d = adm.decidir(item, r.get("UNIVERSO") or "NAO SEI", corrida=corrida)
    out = {"RESULTADO": d.resultado, "REGRA": d.regra, "MOTIVO": d.motivo, "ITEM_ID": d.item, "READY": None}
    if d.regra == "materia":
        # so para o relatorio: o que a pergunta do UNIVERSO diria se a da materia passasse (nao decide nada)
        u = r.get("UNIVERSO") or "NAO SEI"
        ru, mu, _ = adm._do_universo(item, u, adm.PERGUNTAS_DO_UNIVERSO.get(u, []))
        out["UNIVERSO_SE_A_MATERIA_PASSASSE"] = {"RESULTADO": ru, "MOTIVO": mu}
    if d.resultado == adm.SIM:
        out["READY"] = adm.pronto_para_inteligencia(item, d)
    return out


# ---------------------------------------------------------------- uma pagina, da busca a Sala
# ---------------------------------------------------------------- D94-b: o que NAO e pagina comum
# NAME != PROFILE != PERSON (COL-LAW-034). Um PERFIL social achado por busca nao e item (nao se colhe, nao se
# conta) e so vira candidata com prova (nome + instituicao + tema, ou a pagina oficial que aponta para a conta):
# vai para PISTAS-DE-CONTA. Um POST/video social e item, mas quem o colhe e o Scrap (a porta social canonica,
# D94.1-b; o LinkedIn so por URL de POST publico, medido 08:40): vai para POSTS-PARA-O-SCRAP. Nenhum dos dois
# faz da PLATAFORMA (linkedin.com, x.com...) uma candidata.
import re as _re                                                      # noqa: E402
# LOTE8-INTEGRA: o Reel tambem vem na forma instagram.com/<conta>/reel/<codigo> (a do transcritor e a que
# social_por_url_achado le). Sem a conta opcional no molde ele caia em PERFIL_SOCIAL -> PISTAS-DE-CONTA e
# nunca chegava ao Scrap. Medido na juncao (tests/test_lote8_juncoes.py::J_Busca).

POSTS = _re.compile(r"(linkedin\.com/(posts|feed/update|pulse)/|(//|\.)(x|twitter)\.com/[^/]+/status/\d+|"
                    r"instagram\.com/([A-Za-z0-9_.]+/)?(p|reel|reels|tv)/|facebook\.com/.+/(posts|videos)/|fb\.watch/|"
                    r"youtube\.com/(watch|shorts/)|youtu\.be/|tiktok\.com/@[^/]+/video/)", _re.I)
PLATAFORMAS = _re.compile(r"(^|\.)(linkedin\.com|x\.com|twitter\.com|instagram\.com|facebook\.com|fb\.watch|"
                          r"youtube\.com|youtu\.be|tiktok\.com|threads\.net|bsky\.app)$", _re.I)
LOGIN = _re.compile(r"(authwall|/login|/signin|/signup|/accedi|/uas/login|checkpoint/lg)", _re.I)
TITULO_DE_LOGIN = _re.compile(r"<title>[^<]*(sign ?up|log ?in|accedi|iscriviti|registrati|sign in)[^<]*</title>", _re.I)


def especie_do_resultado(url: str) -> str:
    if POSTS.search(url):
        return "POST_SOCIAL"
    if PLATAFORMAS.search(host_de(url)):
        return "PERFIL_SOCIAL"
    return "PAGINA"


def pagina_de_login(url_final: str, dados: bytes) -> bool:
    return bool(LOGIN.search(url_final or "") or TITULO_DE_LOGIN.search(dados[:20000].decode("utf-8", "replace")))


def colher_um(r: dict, fila: Path, saida: Path, buscar, ledger: tuple, corrida: str) -> dict:
    import collection_gate as CG
    url = r["URL"]
    reg = {"URL": url, "PROVENIENCIA": {"ESPECIE": "ACHADO_POR_BUSCA", "CONSULTA": r["CONSULTA"],
                                        "CONSULTA_ID": r.get("CONSULTA_ID"), "MOTOR": r["MOTOR"],
                                        "ROTA_DO_MOTOR": r.get("ROTA_DO_MOTOR"), "POSICAO": r["POSICAO"],
                                        "INSTANTE": r["INSTANTE"]},
           "UNIVERSO": r.get("UNIVERSO"), "FERRAMENTA": r.get("FERRAMENTA"), "CORRIDA": corrida}
    especie = especie_do_resultado(url)
    if especie != "PAGINA":
        perfil = especie == "PERFIL_SOCIAL"
        reg["ESTADO"] = "PERFIL_NAO_E_ITEM" if perfil else "POST_SOCIAL_PARA_O_SCRAP"
        reg["PORQUE"] = ("NAME != PROFILE != PERSON: a conta so vira candidata com prova (nome + instituicao + tema, "
                         "ou pagina oficial que aponta para ela); nao e item e nao se conta" if perfil else
                         "post/video de rede: quem o colhe e o Scrap (porta social canonica, D94); o snippet nao e o item")
        with open(saida / ("PISTAS-DE-CONTA.jsonl" if perfil else "POSTS-PARA-O-SCRAP.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"URL": url, "PROVENIENCIA": reg["PROVENIENCIA"], "UNIVERSO": r.get("UNIVERSO"),
                                 "CORRIDA": corrida}, ensure_ascii=False) + "\n")
        return reg
    fonte = fonte_do_publicador(url, r, fila, ledger)
    reg.update(fonte)
    reg["PROVENIENCIA"]["FONTE_ESTADO_NO_MOMENTO"] = fonte["FONTE_ESTADO_NO_MOMENTO"]
    portao = CG.avaliar_achado_por_busca(reg["PROVENIENCIA"], fonte["FONTE_ESTADO_NO_MOMENTO"])
    reg["PORTAO"] = {k: portao[k] for k in ("COLLECTION_ELIGIBLE", "MOTIVO", "PORQUE")}
    if not portao["COLLECTION_ELIGIBLE"]:
        reg["ESTADO"] = "PORTAO_RECUSOU"
        return reg
    try:
        dados, meta = buscar(url)
    except Exception as e:                                            # noqa: BLE001
        nome = type(e).__name__
        reg["ESTADO"] = ("ROBOTS_OU_ROTA_NAO_PERMITIDA" if nome in ("RotaNaoPermitida",) else
                         "TETO_DO_DOMINIO" if nome in ("TetoDoDominio", "TetoDaOnda") else "FALHA")
        reg["ERRO"] = "%s: %s" % (nome, str(e)[:200])
        return reg
    sha = hashlib.sha256(dados).hexdigest()
    if pagina_de_login((meta or {}).get("URL_FINAL") or url, dados):
        reg["ESTADO"] = "PAGINA_DE_LOGIN"
        reg["PORQUE"] = "muro de login/cadastro: nao e o conteudo (sem login, D88.2); nao se guarda nem se conta"
        return reg
    capturado = agora()
    pasta = saida / "armazem" / sha[:2]
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / sha).write_bytes(dados)
    raw = {"SHA256": sha, "BYTES": len(dados), "MEDIA_TYPE": (meta or {}).get("CONTENT_TYPE"),
           "STORAGE_PATH": "armazem/%s/%s" % (sha[:2], sha), "SOURCE_URL": url, "SOURCE_ID": fonte["SOURCE_ID"],
           "CANDIDATA_ID": fonte["CANDIDATA_ID"], "FONTE_ESTADO_NO_MOMENTO": fonte["FONTE_ESTADO_NO_MOMENTO"],
           "PROVENIENCIA": reg["PROVENIENCIA"], "ROTA_DA_PAGINA": ROTA_DA_PAGINA, "CAPTURED_AT": capturado,
           "CORRIDA": corrida}
    with open(saida / "RAW-LINHA-BUSCA.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(raw, ensure_ascii=False) + "\n")
    reg["RAW"] = {k: raw[k] for k in ("SHA256", "BYTES", "MEDIA_TYPE", "STORAGE_PATH", "CAPTURED_AT")}
    adm = admitir(dados, raw["MEDIA_TYPE"] or "", url, fonte, r, sha, capturado, corrida)
    reg["ADMISSION"] = {k: adm[k] for k in ("RESULTADO", "REGRA", "MOTIVO", "UNIVERSO_SE_A_MATERIA_PASSASSE") if k in adm}
    reg["ESTADO"] = "ADMITIDA" if adm["READY"] else "ADMISSION_%s" % adm["RESULTADO"]
    reg["READY"] = adm["READY"]
    return reg


def colher(resultados: list, fila: Path, saida: Path, buscar, *, pousar=False, corrida=None, livro=None) -> dict:
    corrida = corrida or "%s-%s" % (LINHA, datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    saida.mkdir(parents=True, exist_ok=True)
    cand_sid, est_sid = _ledger(fila, livro)
    ledger = (cand_sid, est_sid, fontes_por_host(fila, cand_sid))
    feitos, vistos = [], set()
    for r in resultados:
        chave = r["URL"].split("#")[0].rstrip("/").lower()
        if chave in vistos:
            # D94-b: o mesmo endereco achado por outra consulta/posicao nao e outro item, e nao se pede outra vez
            reg = {"URL": r["URL"], "ESTADO": "DUPLICADO_NA_CORRIDA", "CORRIDA": corrida,
                   "PROVENIENCIA": {"ESPECIE": "ACHADO_POR_BUSCA", "CONSULTA": r["CONSULTA"], "MOTOR": r["MOTOR"],
                                    "POSICAO": r["POSICAO"], "INSTANTE": r["INSTANTE"]}}
        else:
            vistos.add(chave)
            reg = colher_um(r, fila, saida, buscar, ledger, corrida)
        feitos.append(reg)
        with open(saida / "LIVRO-LINHA-BUSCA.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({k: v for k, v in reg.items() if k != "READY"}, ensure_ascii=False) + "\n")
    prontos = [x["READY"] for x in feitos if x.get("READY")]
    recibo = None
    if pousar and prontos:
        # A SALA SO RECEBE O QUE TEM RAW CANONICO: collection_run + raw_asset pela porta do dono
        # (`guarda/preservar_coleta`), e o READY refeito com o RAW_OBSERVATION_ID real. E o mesmo caminho
        # do `--repousar` (coleta/linha_busca_raw.py), sobre a pasta desta corrida.
        import linha_busca_raw as LR
        recibo = LR.repousar([saida], corrida=corrida, pousar=True)
    (saida / ("READY-%s.json" % corrida)).write_text(json.dumps(prontos, ensure_ascii=False, indent=1) + "\n",
                                                    encoding="utf-8")
    # D94-b: so conta item UNICO, ADMITIDO e com identidade provada (nunca perfil, snippet, duplicado ou login)
    unicos = {p["ITEM_ID"] for p in prontos if p.get("ITEM_ID") not in (None, "", "NAO SEI")}
    return {"CORRIDA": corrida, "RESULTADOS": len(resultados), "ESTADOS": dict(Counter(x["ESTADO"] for x in feitos)),
            "ADMITIDAS": len(prontos), "ITENS_UNICOS_ADMITIDOS": len(unicos), "POUSADAS": recibo, "ITENS": feitos}


# ---------------------------------------------------------------- D93.4: recusada depois -> marcada, nada se apaga
def marcar(saida: Path, fila: Path) -> list:
    q = {c["CANDIDATA_ID"]: c for c in json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]}
    livro = saida / "LIVRO-LINHA-BUSCA.jsonl"
    marcas, ja = [], set()
    if not livro.exists():
        return marcas
    linhas = [json.loads(l) for l in livro.read_text(encoding="utf-8").splitlines() if l.strip()]
    for l in linhas:
        if l.get("ESPECIE") == "MARCA_D93":
            ja.add((l["SHA256"], l["ESTADO_DA_FONTE"]))
    for l in linhas:
        c = q.get(l.get("CANDIDATA_ID") or "")
        sha = (l.get("RAW") or {}).get("SHA256")
        if c and sha and c["ESTADO"] in ("RECUSADA", "POLICY_BLOCK") and (sha, c["ESTADO"]) not in ja:
            m = {"ESPECIE": "MARCA_D93", "SHA256": sha, "ITEM_URL": l["URL"], "CANDIDATA_ID": c["CANDIDATA_ID"],
                 "ESTADO_DA_FONTE": c["ESTADO"], "MOTIVO_DA_RECUSA": c.get("MOTIVO_DA_RECUSA"), "MARCADO_EM": agora(),
                 "LEI": "D93.4: a fonte foi recusada depois; o item fica, marcado — a Intelligence pode ignora-lo"}
            marcas.append(m)
            ja.add((sha, c["ESTADO"]))
    with open(livro, "a", encoding="utf-8") as fh:
        for m in marcas:
            fh.write(json.dumps(m, ensure_ascii=False) + "\n")
    return marcas


# ---------------------------------------------------------------- rede (so --autorizado)
def portao_it(saida: Path, quando: str) -> bool:
    r = subprocess.run([sys.executable, str(RAIZ / "superficie" / "rede.py"), "--portao-de-egresso", "IT"],
                       capture_output=True, text=True, timeout=300)
    (saida / ("PORTAO-%s.txt" % quando)).write_text(r.stdout[-4000:] + r.stderr[-2000:], encoding="utf-8")
    return r.returncode == 0


def transporte_real(saida: Path):
    """O transporte canonico, com o livro do teto (24 h) nomeado. Um livro por dia, partilhavel entre linhas."""
    os.environ.setdefault("SINTONIA_TETO_ONDA", str(saida / ("TETO-%s.json" % datetime.now(timezone.utc).date())))
    import scrap_http as http

    def buscar(url, cabecalhos=None):
        return http.buscar_bytes(url, aceitar="text/html,application/pdf,application/json;q=0.9,*/*;q=0.5",
                                 cabecalhos=cabecalhos)
    return buscar


def buscar_consultas(motor: str, consultas: list, buscar, saida: Path) -> list:
    m = MO.MOTORES[motor]
    out = []
    for q in consultas:
        pedido = m["PEDIDO"](q["CONSULTA"])
        if not pedido:
            out.append({"CONSULTA_ID": q["CONSULTA_ID"], "MOTOR": motor, "ERRO": "sem chave do dono para esta API"})
            continue
        instante = agora()
        cab = dict(m.get("CABECALHOS") or {})
        if motor == "BRAVE_API":
            cab["X-Subscription-Token"] = os.environ.get("SINTONIA_BRAVE_KEY", "")
        try:
            corpo, meta = buscar(pedido, cab or None)
        except Exception as e:                                        # noqa: BLE001
            # a tesoura: o endereco da API leva a chave, e uma mensagem de erro pode repeti-lo
            out.append({"CONSULTA_ID": q["CONSULTA_ID"], "MOTOR": motor,
                        "ERRO": API.redigir("%s: %s" % (type(e).__name__, str(e)[:200]))})
            continue
        sha = hashlib.sha256(corpo).hexdigest()
        (saida / "serp").mkdir(parents=True, exist_ok=True)
        (saida / "serp" / sha).write_bytes(corpo)
        for i, u in enumerate(m["RESULTADOS"](corpo), 1):
            out.append(dict(q, MOTOR=motor, ROTA_DO_MOTOR=m["ROTA"], POSICAO=i, INSTANTE=instante, URL=u,
                            SERP_SHA256=sha))
    return out


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    saida = Path(arg.get("saida") or ".")
    saida.mkdir(parents=True, exist_ok=True)
    if "--plano" in argv:
        fams = CQ.familias_da_r3(arg["r3"]) if arg.get("r3") else []
        qs = CQ.prioridade(CQ.gerar(int(arg["mes"]) if arg.get("mes") else None,
                                    int(arg["ano"]) if arg.get("ano") else None, familias_r3=fams))
        (saida / "CONSULTAS.json").write_text(json.dumps(qs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(len(qs), "consultas; familias R3:", fams, "; as 4 primeiras:",
              [q["CONSULTA"] for q in qs[:4]])
        return 0
    if "--marcar" in argv:
        print(len(marcar(saida, Path(arg["fila"]))), "itens marcados (D93.4)")
        return 0
    if "--ensaio" in argv:
        pags = Path(arg["paginas"])
        idx = json.loads((pags / "PAGINAS.json").read_text(encoding="utf-8"))

        def falso(url, cab=None):
            p = idx.get(url)
            if p is None:
                raise RuntimeError("sem fixture para %s" % url)
            if p.get("ERRO"):
                cls = type(p["ERRO"], (Exception,), {})
                raise cls(p.get("PORQUE", ""))
            return (pags / p["FICHEIRO"]).read_bytes(), {"CONTENT_TYPE": p.get("CONTENT_TYPE", "text/html")}
        res = json.loads(Path(arg["resultados"]).read_text(encoding="utf-8"))
        doc = colher(res, Path(arg["fila"]), saida, falso, corrida="ENSAIO-" + LINHA, livro=arg.get("livro"))
        print(json.dumps({k: doc[k] for k in ("RESULTADOS", "ESTADOS", "ADMITIDAS", "ITENS_UNICOS_ADMITIDOS")}, ensure_ascii=False))
        return 0
    if "--autorizado" not in argv:
        print("RECUSADO: este passo sai a rede; so com --autorizado (quem corre e o coordenador)")
        return 2
    # BUSCA-NO-ACTIONS (27/09): a busca por API OFICIAL corre no GitHub Actions, sem VPN — a API nao precisa de
    # saida italiana. `--sem-portao-it` so vale para isso: diagnostico da API ou `--buscar` com motor API_OFICIAL.
    # PAGINAS nunca: o `--colher` e o `--medir-motores` continuam presos ao portao IT (e a esta maquina).
    sem_portao = "--sem-portao-it" in argv
    motor_api = MO.MOTORES.get(arg.get("motor", ""), {}).get("ROTA") == "API_OFICIAL"
    if sem_portao and not ("--diagnosticar-cse" in argv or ("--buscar" in argv and motor_api)):
        print("RECUSADO: --sem-portao-it so serve a busca por API oficial (--diagnosticar-cse, ou --buscar com "
              "motor API_OFICIAL); paginas colhem-se com o portao IT")
        return 2
    if "--diagnosticar-cse" in argv:
        d = API.diagnosticar_cse()
        (saida / "DIAGNOSTICO.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        for k in ("HTTP", "API_ATIVA", "CHAVE_PODE_USAR_A_API", "CX", "BUSCA_POSSIVEL", "PORQUE"):
            print("%-22s %s" % (k, API.redigir(d.get(k))))
        for i, passo in enumerate(d.get("O_QUE_O_DONO_FAZ") or [], 1):
            print("DONO %d: %s" % (i, passo))
        return 0 if d.get("BUSCA_POSSIVEL") == "SIM" else 4
    if not sem_portao and not portao_it(saida, "ANTES"):
        print("PAROU: portao de egresso nao e IT (antes)")
        return 3
    buscar = API.transporte() if ("--buscar" in argv and motor_api) else transporte_real(saida)
    if "--medir-motores" in argv:
        q = CQ.prioridade(CQ.gerar())[0]
        medida = {}
        for nome in ("DDG_HTML", "BING_HTML", "GOOGLE_HTML", "GOOGLE_CSE", "BRAVE_API"):
            rs = buscar_consultas(nome, [q], buscar, saida)
            medida[nome] = {"CONSULTA": q["CONSULTA"], "RESULTADOS": len([x for x in rs if x.get("URL")]),
                            "ERRO": next((x["ERRO"] for x in rs if x.get("ERRO")), None),
                            "PRIMEIROS": [x["URL"] for x in rs if x.get("URL")][:5]}
        (saida / "MOTORES-MEDIDOS.json").write_text(json.dumps(medida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({k: (v["RESULTADOS"], v["ERRO"]) for k, v in medida.items()}, ensure_ascii=False))
    elif "--buscar" in argv:
        n = int(arg.get("n", "4"))
        teto = API.QUOTA_DIA.get(arg["motor"])
        if teto is not None and not 1 <= n <= teto:
            print("RECUSADO: --n=%d fora da quota declarada de %s (1..%d consultas/dia)" % (n, arg["motor"], teto))
            return 2
        qs = json.loads(Path(arg["consultas"]).read_text(encoding="utf-8"))[:n]
        rs = buscar_consultas(arg["motor"], qs, buscar, saida)
        (saida / "RESULTADOS.json").write_text(json.dumps(rs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(len([x for x in rs if x.get("URL")]), "resultados;", sum(1 for x in rs if x.get("ERRO")), "erros")
    elif "--colher" in argv:
        res = [x for x in json.loads(Path(arg["resultados"]).read_text(encoding="utf-8")) if x.get("URL")]
        res = res[: int(arg["max"])] if arg.get("max") else res
        doc = colher(res, Path(arg["fila"]), saida, buscar, pousar="--pousar" in argv, livro=arg.get("livro"))
        print(json.dumps({k: doc[k] for k in ("CORRIDA", "RESULTADOS", "ESTADOS", "ADMITIDAS", "ITENS_UNICOS_ADMITIDOS", "POUSADAS")},
                         ensure_ascii=False, default=str))
    if sem_portao:
        return 0
    ok = portao_it(saida, "DEPOIS")
    print("portao IT depois:", "PASS" if ok else "NAO E IT")
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
