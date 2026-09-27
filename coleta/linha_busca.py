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
            corrida: str) -> dict:
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
           "RAW_ASSET_ID": None, "PARENT_SHA256": sha, "CAPTURED_AT": capturado, "TEMPO_E_LUGAR": tl,
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
def colher_um(r: dict, fila: Path, saida: Path, buscar, ledger: tuple, corrida: str) -> dict:
    import collection_gate as CG
    url = r["URL"]
    reg = {"URL": url, "PROVENIENCIA": {"ESPECIE": "ACHADO_POR_BUSCA", "CONSULTA": r["CONSULTA"],
                                        "CONSULTA_ID": r.get("CONSULTA_ID"), "MOTOR": r["MOTOR"],
                                        "ROTA_DO_MOTOR": r.get("ROTA_DO_MOTOR"), "POSICAO": r["POSICAO"],
                                        "INSTANTE": r["INSTANTE"]},
           "UNIVERSO": r.get("UNIVERSO"), "FERRAMENTA": r.get("FERRAMENTA"), "CORRIDA": corrida}
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
    feitos = []
    for r in resultados:
        reg = colher_um(r, fila, saida, buscar, ledger, corrida)
        feitos.append(reg)
        with open(saida / "LIVRO-LINHA-BUSCA.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({k: v for k, v in reg.items() if k != "READY"}, ensure_ascii=False) + "\n")
    prontos = [x["READY"] for x in feitos if x.get("READY")]
    recibo = None
    if pousar and prontos:
        import sala_de_espera as SE
        SE.exigir_canonica()                       # nunca cai para ficheiro: Sala canonica ou nada
        recibo = SE.pousar(corrida, prontos)
    (saida / ("READY-%s.json" % corrida)).write_text(json.dumps(prontos, ensure_ascii=False, indent=1) + "\n",
                                                    encoding="utf-8")
    return {"CORRIDA": corrida, "RESULTADOS": len(resultados), "ESTADOS": dict(Counter(x["ESTADO"] for x in feitos)),
            "ADMITIDAS": len(prontos), "POUSADAS": recibo, "ITENS": feitos}


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
            out.append({"CONSULTA_ID": q["CONSULTA_ID"], "MOTOR": motor, "ERRO": "%s: %s" % (type(e).__name__, str(e)[:200])})
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
        print(json.dumps({k: doc[k] for k in ("RESULTADOS", "ESTADOS", "ADMITIDAS")}, ensure_ascii=False))
        return 0
    if "--autorizado" not in argv:
        print("RECUSADO: este passo sai a rede; so com --autorizado (quem corre e o coordenador)")
        return 2
    if not portao_it(saida, "ANTES"):
        print("PAROU: portao de egresso nao e IT (antes)")
        return 3
    buscar = transporte_real(saida)
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
        qs = json.loads(Path(arg["consultas"]).read_text(encoding="utf-8"))[: int(arg.get("n", "4"))]
        rs = buscar_consultas(arg["motor"], qs, buscar, saida)
        (saida / "RESULTADOS.json").write_text(json.dumps(rs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(len([x for x in rs if x.get("URL")]), "resultados;", sum(1 for x in rs if x.get("ERRO")), "erros")
    elif "--colher" in argv:
        res = [x for x in json.loads(Path(arg["resultados"]).read_text(encoding="utf-8")) if x.get("URL")]
        res = res[: int(arg["max"])] if arg.get("max") else res
        doc = colher(res, Path(arg["fila"]), saida, buscar, pousar="--pousar" in argv, livro=arg.get("livro"))
        print(json.dumps({k: doc[k] for k in ("CORRIDA", "RESULTADOS", "ESTADOS", "ADMITIDAS", "POUSADAS")},
                         ensure_ascii=False, default=str))
    ok = portao_it(saida, "DEPOIS")
    print("portao IT depois:", "PASS" if ok else "NAO E IT")
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
