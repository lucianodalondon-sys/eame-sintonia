#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATILHO DO PREVIEW — correcao do dono (28/09 ~20:37), missao L3, item 3:
«PUBLICACAO AUTOMATICA NO PREVIEW (autorizada: EXCECAO E2E CONTROLADA EM PREVIEW = AUTORIZADA; PRODUCAO
continua bloqueada; ENDERECO OFICIAL = NAO). O Casco nao pode ler pasta incompleta.»

    python3 portoes/publicar_preview_da_pasta.py --modo preview     # le a ENTREGA (curadoria/esteira/intelligence/PARA-O-CASCO)
    python3 portoes/publicar_preview_da_pasta.py --pasta <.../PARA-O-CASCO-R9> --modo preview
    python3 portoes/publicar_preview_da_pasta.py --raiz  <.../intelligence-experimental> --modo preview
    python3 portoes/publicar_preview_da_pasta.py --raiz  <...> --so-conferir      # diz o que faria

Este ficheiro NAO publica nada por conta propria e NAO e um segundo publicador: confere que a pasta que a
Intelligence entregou esta COMPLETA e chama `publicar_portal_sozinho.main` (D126) com o pote PARA_CLIENTE
dela. Todas as conferencias (C0..C6, a volta sozinha, o registo) continuam as do publicador.

O SINAL DE COMPLETUDE NAO E INVENTADO AQUI
------------------------------------------
Medido em 28/09 nas seis pastas de entrega da Intelligence (PARA-O-CASCO-R2, R4, R5, R6, R7, R9): todas
trazem um MANIFESTO e um SHA256SUMS.txt, e o SHA256SUMS lista o proprio manifesto. Na R9 o manifesto e a
ultima coisa que o montador escreve (montar_r9.py) e o SHA256SUMS vem depois, cobrindo-o. Por isso:

    PASTA COMPLETA  =  SHA256SUMS.txt bem formado e terminado,
                       TODA linha confere (byte relido, sha256 igual),
                       ele lista UM MANIFESTO*.json,
                       o manifesto aponta um pote PARA_CLIENTE que o SHA256SUMS tambem lista,
                       e o sha do pote no manifesto e o sha do ficheiro.

O manifesto vem em duas formas, as duas medidas: a da R9 (`POTES.PARA_CLIENTE.ARQUIVO`) e a do disparador da
Intelligence L2 (`POTE.ARQUIVO`, um pote so — provas/l2/PARA-O-CASCO.md no ramo claude/l2-disparador-v1). Nas duas,
`RESULT_STATE` tem de ser DONE ou REUSED.

A ENTREGA (aviso do coordenador, 28/09): a Intelligence deixa de escrever italia-portale/client/sintonia-pote.js; a
entrega e SO `curadoria/esteira/intelligence/PARA-O-CASCO/` (POTE.json + MANIFESTO.json + SHA256SUMS.txt), trocada
INTEIRA por `os.replace`. E o default deste gatilho. Durante a troca a pasta pode nao existir: isso e INCOMPLETA.

CONGELAR: o pote conferido e COPIADO para uma pasta temporaria e o sha e medido OUTRA VEZ na copia; e a copia que
vai ao publicador. Sem isto a Intelligence podia trocar a pasta entre a conferencia e a leitura do publicador, e ia
ao ar um pote que ninguem conferiu.

Nada de PRONTO.txt: seria um protocolo paralelo a um sinal que ja existe. Qualquer falta = INCOMPLETA, e
uma pasta incompleta nao e lida (nem o pote dela e aberto pelo publicador).

O QUE ISTO NAO FAZ
------------------
- nao escolhe objetos nem reescreve o pote (quem libera e a Intelligence, objeto por objeto);
- nao publica em producao: `--modo producao` e recusado AQUI, antes do publicador (a producao continua
  bloqueada por decisao do dono, e a sua porta e o publicador chamado a mao com o veredito do LAB);
- nao se agenda sozinho. «Automatico» = uma passagem idempotente sobre a raiz; quem a repete (o agendador
  da maquina) e decisao do coordenador. Uma pasta ja no ar da NADA_A_PUBLICAR pelo proprio publicador.

A RODADA (D156, coordenador 29/09 — «o publicar_preview_da_pasta.py precisa rodar SOZINHO»)
--------------------------------------------------------------------------------------------
    python3 portoes/publicar_preview_da_pasta.py --rodada --estado <pasta> [--pasta <entrega>]

E o que a tarefa agendada SINTONIA-CASCO-PREVIEW corre a cada 10 min (portoes/casco_preview.cmd). Uma rodada:
  1. PARAR na pasta de estado          -> PARADO, nada acontece (a bandeira de desligar);
  2. a TRAVA de instancia unica          -> se outra rodada corre, OCUPADO, nada acontece;
  3. a ENTREGA nao existe                -> AUSENTE (a meio da troca, ou nunca entregue): nada;
  4. a ASSINATURA (sha de SHA256SUMS.txt + MANIFESTO*.json) e a ja tratada -> IGUAL: nada;
  5. COMPLETA -> publica no PREVIEW a copia congelada; se o publicador aceita, e o novo ULTIMO BOM;
  6. INCOMPLETA, ou o publicador reprovou -> RECUSADA: o ULTIMO BOM volta ao ar com o motivo no envelope
     (o casco o diz SO em /debug/intelligence-pot — B3), e o pote servido nao muda.
Cada rodada escreve uma linha em RODADAS.ndjson (T0 = hora do SHA256SUMS da entrega, T1 = fim da publicacao).
Nunca producao: o modo e so ensaio/preview, e o CANONICAL_HOST nunca e destino (a regra da guarda L1).

PREVIEW-ATUAL.json (pedido do LAB, 29/09): o pote so existe na URL do DEPLOYMENT (o CANONICAL_HOST da 404 para
/sintonia-pote-publicado.js). A cada deployment novo a rodada grava, num ficheiro estavel (--preview-atual), a URL,
o id, e os DOIS sha do pote — ditos pelo nome, porque sao diferentes com o mesmo conteudo:
    POTE_SHA256_CANONICO   sha256 do JSON canonico (chaves ordenadas, compacto, UTF-8) = o POTE_SHA256 do envelope no ar
    POTE_SHA256_FICHEIRO   sha256 dos bytes do POTE.json da entrega = o SHA256_ARQUIVO do MANIFESTO / SHA256SUMS

SAIDAS: 0 publicado / nada a publicar / so conferir · 1 bloqueado pelo publicador · 4 uso errado ·
        5 nenhuma entrega completa, ou o pote mudou durante a leitura (nada foi chamado) · outros = os do publicador
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RAIZ = Path(os.path.dirname(HERE))
ENTREGA = RAIZ / "curadoria" / "esteira" / "intelligence" / "PARA-O-CASCO"
ESTADOS_BONS = ("DONE", "REUSED")

SOMAS = "SHA256SUMS.txt"
LINHA_SOMA = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")
MODOS_PERMITIDOS = ("ensaio", "preview")
SEM_PASTA, USO = 5, 4


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def conferir_pasta(pasta) -> dict:
    """A pasta esta completa? Devolve {COMPLETA, MOTIVOS, POTE, MANIFESTO, INTELLIGENCE_RUN_ID, SHA256_POTE}.
    COMPLETA so com zero motivos. Nao abre o pote para o julgar: isso e do publicador (C0)."""
    pasta = Path(pasta)
    out = {"PASTA": str(pasta), "COMPLETA": False, "ESTADO": "INCOMPLETA", "MOTIVOS": [], "POTE": None, "MANIFESTO": None,
           "INTELLIGENCE_RUN_ID": None, "SHA256_POTE": None}
    M = out["MOTIVOS"]
    somas = pasta / SOMAS
    if not somas.is_file():
        M.append(f"sem {SOMAS}")
        return out
    bruto = somas.read_bytes()
    if not bruto.endswith(b"\n"):
        M.append(f"{SOMAS} nao termina em fim de linha (pode estar a meio de ser escrito)")
        return out
    listados = {}
    for n, ln in enumerate(bruto.decode("utf-8", "replace").splitlines(), 1):
        ln = ln.rstrip("\r")
        if not ln.strip():
            continue
        m = LINHA_SOMA.match(ln)
        if not m:
            M.append(f"{SOMAS} linha {n} mal formada")
            continue
        sha, nome = m.group(1), m.group(2)
        alvo = (pasta / nome).resolve()
        if not alvo.is_file():
            M.append(f"{nome}: listado e ausente")
            continue
        if _sha(alvo) != sha:
            M.append(f"{nome}: sha256 diferente do {SOMAS}")
            continue
        listados[alvo] = sha
    if not listados and not M:
        M.append(f"{SOMAS} vazio")
    if M:
        return out
    manifestos = [p for p in listados if p.parent == pasta.resolve() and re.fullmatch(r"MANIFESTO[^/\\]*\.json", p.name)]
    if len(manifestos) != 1:
        M.append(f"{SOMAS} lista {len(manifestos)} MANIFESTO*.json desta pasta (tem de ser 1)")
        return out
    man_p = manifestos[0]
    try:
        man = json.loads(man_p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        M.append(f"{man_p.name} ilegivel: {e}")
        return out
    out["MANIFESTO"] = str(man_p)
    if not isinstance(man, dict) or man.get("RESULT_STATE") not in ESTADOS_BONS:
        M.append(f"{man_p.name}: RESULT_STATE {man.get('RESULT_STATE') if isinstance(man, dict) else None} "
                 f"nao e {' / '.join(ESTADOS_BONS)}")
        return out
    # forma L2 (um pote so: POTE) ou forma R9 (POTES.PARA_CLIENTE)
    pc = man.get("POTE") if isinstance(man.get("POTE"), dict) else (man.get("POTES") or {}).get("PARA_CLIENTE")
    if not isinstance(pc, dict) or not pc.get("ARQUIVO"):
        # a pasta ESTA inteira (as somas conferem); so nao ha nada liberado para cliente nela
        out["ESTADO"] = "SEM_POTE_PARA_CLIENTE"
        M.append(f"{man_p.name} nao aponta um pote (POTE.ARQUIVO nem POTES.PARA_CLIENTE.ARQUIVO)")
        return out
    pote_p = (pasta / pc["ARQUIVO"]).resolve()
    if pote_p not in listados:
        M.append(f"{pc['ARQUIVO']}: o pote PARA_CLIENTE nao esta no {SOMAS}")
        return out
    if pc.get("SHA256_ARQUIVO") != listados[pote_p]:
        M.append(f"{pc['ARQUIVO']}: SHA256_ARQUIVO do manifesto != sha do ficheiro")
        return out
    out.update(COMPLETA=True, ESTADO="COMPLETA", POTE=str(pote_p), SHA256_POTE=listados[pote_p],
               INTELLIGENCE_RUN_ID=man.get("INTELLIGENCE_RUN_ID"))
    return out


def congelar_pote(c: dict, destino: Path) -> Path | None:
    """Copia o pote conferido para `destino` e mede o sha OUTRA VEZ na copia. None = mudou desde a conferencia."""
    destino.mkdir(parents=True, exist_ok=True)
    copia = destino / Path(c["POTE"]).name
    try:
        shutil.copyfile(c["POTE"], copia)
    except OSError:
        return None
    return copia if _sha(copia) == c["SHA256_POTE"] else None


def escolher(raiz) -> tuple[dict | None, list]:
    """Na raiz, as pastas PARA-O-CASCO-*: todas conferidas, e a completa mais recente (pelo SHA256SUMS, o
    ultimo ficheiro que a entrega escreve). Devolve (escolhida ou None, todas as conferencias)."""
    todas = []
    for d in sorted(Path(raiz).glob("PARA-O-CASCO-*")):
        if d.is_dir():
            c = conferir_pasta(d)
            c["QUANDO"] = (d / SOMAS).stat().st_mtime if (d / SOMAS).is_file() else None
            todas.append(c)
    completas = [c for c in todas if c["COMPLETA"]]
    return (max(completas, key=lambda c: c["QUANDO"]) if completas else None), todas


# ── A RODADA (D156) ─────────────────────────────────────────────────────────
TRAVA_VELHA_S = 3 * 3600          # uma publicacao demora ~30 min; 3 h sem soltar = processo morto
TENTATIVAS_POR_ASSINATURA = 2     # uma falha do transporte tenta de novo; um vermelho fixo nao gira para sempre


def _agora() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def assinatura(pasta: Path) -> str | None:
    """O sha do que a Intelligence assina: SHA256SUMS.txt + MANIFESTO*.json (nome e bytes). None = nada assinado."""
    pasta = Path(pasta)
    partes = sorted([pasta / SOMAS] + list(pasta.glob("MANIFESTO*.json")))
    partes = [x for x in partes if x.is_file()]
    if not partes:
        return None
    h = hashlib.sha256()
    for x in partes:
        h.update(x.name.encode() + b"\0" + x.read_bytes() + b"\0")
    return h.hexdigest()


def _ler(p: Path, vazio):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return vazio


def _escrever(p: Path, dado):
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(dado, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def _registo_mais_novo(registro: Path, desde: float):
    """O REGISTO.json que o publicador escreveu nesta rodada (o mais novo depois de `desde`)."""
    novos = [r for r in Path(registro).glob("*/*/REGISTO.json") if r.stat().st_mtime >= desde]
    return max(novos, key=lambda r: r.stat().st_mtime) if novos else None


def _publicar_de_verdade(pote: Path, modo: str, registro: Path, entrega: dict | None, estado: Path):
    """-> (rc, REGISTO dict ou None). O publicador D126, tal e qual; so acrescenta o que se diz da entrega."""
    import publicar_portal_sozinho as P  # noqa: PLC0415
    args = ["--pote", str(pote), "--modo", modo, "--registro", str(registro)]
    if entrega:
        ej = estado / "ENTREGA-A-DIZER.json"
        _escrever(ej, entrega)
        args += ["--entrega-json", str(ej)]
    inicio = _dt.datetime.now().timestamp() - 1
    rc = P.main(args)
    reg = _registo_mais_novo(registro, inicio)
    return rc, (_ler(reg, None) if reg else None)


def _motivos_do_publicador(reg: dict | None) -> list:
    if not reg:
        return ["o publicador nao deixou registo"]
    maus = [l.get("ID") for l in reg.get("CONFERENCIAS") or [] if not l.get("PASS")]
    return ["o publicador reprovou: " + ", ".join(maus)] if maus else ["o publicador acabou em " + str(reg.get("ESTADO"))]


def _destino_proibido(modo: str) -> str | None:
    """A regra da guarda L1 (leis/fundacao_da_coleta.py no ramo claude/l1-governanca-preview-v1): so preview, e o
    endereco do produto (CANONICAL_HOST) nunca. Aqui o modo producao nao existe; o implantador do preview publica
    num endereco de deployment, nunca no CANONICAL_HOST (VercelCLI.url_no_ar)."""
    if modo not in MODOS_PERMITIDOS:
        return f"modo {modo!r}: so {' / '.join(MODOS_PERMITIDOS)} — a producao continua bloqueada"
    return None


def gravar_preview_atual(destino, reg: dict | None, pote: Path, sha_ficheiro: str, entrega: dict | None) -> dict | None:
    """O endereco do preview que acabou de ir ao ar, num ficheiro estavel para o LAB. Escrita atomica."""
    if not destino or not reg or not (reg.get("IMPLANTADO") or {}).get("URL"):
        return None
    import publicar_portal_sozinho as P  # noqa: PLC0415
    dado = json.loads(Path(pote).read_text(encoding="utf-8"))
    url = reg["IMPLANTADO"]["URL"].rstrip("/")
    atual = {"URL": url, "DEPLOYMENT_ID": reg["IMPLANTADO"].get("ID"), "DEBUG": url + "/debug/intelligence-pot",
             "POTE_SHA256_CANONICO": P.sha_do_pote(dado), "POTE_SHA256_FICHEIRO": sha_ficheiro,
             "SHA_NO_AR_E_O": "POTE_SHA256_CANONICO (o envelope /sintonia-pote-publicado.js)",
             "INTELLIGENCE_RUN_ID": dado.get("INTELLIGENCE_RUN_ID"),
             "DEMO_OU_LIVE": "DEMO" if dado.get("CORRIDA_SINTETICA") is True else "LIVE",
             "ENTREGA": (entrega or {}).get("ESTADO", "ACEITE"), "MOTIVOS_DA_RECUSA": (entrega or {}).get("MOTIVOS"),
             "ARVORE": (reg.get("ARVORE") or {}).get("COMMIT"), "PUBLICADO_EM": reg.get("FIM"), "GRAVADO_EM": _agora(),
             "PRODUCAO": "INTOCADA — so preview; o CANONICAL_HOST nao serve este pote"}
    _escrever(Path(destino), atual)
    return atual


def rodada(entrega: Path, estado: Path, modo: str = "preview", publicar=None, preview_atual=None) -> dict:
    """Uma volta do agendador. Devolve a linha que fica em RODADAS.ndjson."""
    estado = Path(estado)
    estado.mkdir(parents=True, exist_ok=True)
    publicar = publicar or _publicar_de_verdade
    linha = {"INICIO": _agora(), "ENTREGA": str(entrega), "MODO": modo}

    def fim(decisao, **extra):
        linha.update(extra, DECISAO=decisao, FIM=_agora())
        with open(estado / "RODADAS.ndjson", "a", encoding="utf-8") as f:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
        return linha

    proibido = _destino_proibido(modo)
    if proibido:
        return fim("RECUSADO_DESTINO", MOTIVOS=[proibido])
    if (estado / "PARAR").exists():
        return fim("PARADO", MOTIVOS=["bandeira PARAR presente: nada e publicado"])
    trava = estado / "TRAVA.lock"
    try:
        fd = os.open(trava, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        idade = _dt.datetime.now().timestamp() - trava.stat().st_mtime
        if idade < TRAVA_VELHA_S:
            return fim("OCUPADO", MOTIVOS=[f"outra rodada corre ha {int(idade)} s"])
        trava.unlink()
        linha["TRAVA_VELHA_REMOVIDA_S"] = int(idade)
        fd = os.open(trava, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, f"{os.getpid()} {_agora()}".encode())
    os.close(fd)
    try:
        E = _ler(estado / "ESTADO.json", {})
        entrega = Path(entrega)
        if not entrega.is_dir():
            return fim("AUSENTE", MOTIVOS=["a pasta de entrega nao existe (a meio da troca, ou nunca entregue)"])
        ass = assinatura(entrega)
        linha["ASSINATURA"] = ass
        somas = entrega / SOMAS
        linha["T0"] = (_dt.datetime.fromtimestamp(somas.stat().st_mtime, _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                       if somas.is_file() else None)
        if ass is not None and ass == E.get("ULTIMA_ASSINATURA"):
            return fim("IGUAL")
        tentativas = E.get("TENTATIVAS", {}) if E.get("TENTATIVAS_DE") == ass else {}
        registro = estado / "PUBLICACOES"
        c = conferir_pasta(entrega)
        linha["CONFERENCIA"] = {"ESTADO": c["ESTADO"], "MOTIVOS": c["MOTIVOS"], "SHA256_POTE": c["SHA256_POTE"],
                                "INTELLIGENCE_RUN_ID": c["INTELLIGENCE_RUN_ID"]}
        motivos = list(c["MOTIVOS"])
        if c["COMPLETA"]:
            guardado = estado / "POTES" / c["SHA256_POTE"]
            pote = congelar_pote(c, guardado)
            if not pote:
                return fim("MUDOU_DURANTE_A_LEITURA", MOTIVOS=["o pote mudou entre a conferencia e a copia: tenta na proxima"])
            rc, reg = publicar(pote, modo, registro, None, estado)
            linha.update(RC=rc, DEPLOYMENT=(reg or {}).get("IMPLANTADO"), T1=_agora(), FIM_DO_PUBLICADOR=(reg or {}).get("FIM"))
            if rc == 0:
                linha["PREVIEW_ATUAL"] = gravar_preview_atual(preview_atual, reg, pote, c["SHA256_POTE"], None)
                E.update(ULTIMA_ASSINATURA=ass, TENTATIVAS_DE=None, TENTATIVAS={},
                         ULTIMO_BOM={"SHA256_POTE_FICHEIRO": c["SHA256_POTE"], "POTE": str(pote),
                                     "INTELLIGENCE_RUN_ID": c["INTELLIGENCE_RUN_ID"],
                                     "DEPLOYMENT": (reg or {}).get("IMPLANTADO"), "QUANDO": (reg or {}).get("FIM")},
                         ULTIMA_ENTREGA={"ESTADO": "ACEITE", "QUANDO": _agora(), "ASSINATURA": ass})
                _escrever(estado / "ESTADO.json", E)
                return fim("PUBLICADA")
            motivos = _motivos_do_publicador(reg)
        # RECUSADA: o pote servido NAO muda; o ultimo bom volta com o motivo (so o debug o diz)
        dizer = {"ESTADO": "RECUSADA", "QUANDO": _agora(), "MOTIVOS": motivos[:6], "ASSINATURA": ass}
        bom = E.get("ULTIMO_BOM") or {}
        if not bom.get("POTE") or not Path(bom["POTE"]).is_file():
            E.update(ULTIMA_ASSINATURA=ass, ULTIMA_ENTREGA=dizer)
            _escrever(estado / "ESTADO.json", E)
            return fim("RECUSADA_SEM_ULTIMO_BOM", MOTIVOS=motivos,
                       NOTA="nada no ar a manter: o motivo fica so neste registo")
        rc, reg = publicar(Path(bom["POTE"]), modo, registro, dizer, estado)
        linha.update(RC=rc, DEPLOYMENT=(reg or {}).get("IMPLANTADO"), T1=_agora(), FIM_DO_PUBLICADOR=(reg or {}).get("FIM"),
                     POTE_MANTIDO=bom.get("INTELLIGENCE_RUN_ID"))
        if rc == 0:
            linha["PREVIEW_ATUAL"] = gravar_preview_atual(preview_atual, reg, Path(bom["POTE"]),
                                                          bom.get("SHA256_POTE_FICHEIRO"), dizer)
        tentativas[ass or "-"] = tentativas.get(ass or "-", 0) + 1
        if rc == 0 or tentativas[ass or "-"] >= TENTATIVAS_POR_ASSINATURA:
            E.update(ULTIMA_ASSINATURA=ass, TENTATIVAS_DE=None, TENTATIVAS={}, ULTIMA_ENTREGA=dizer)
        else:
            E.update(TENTATIVAS_DE=ass, TENTATIVAS=tentativas)
        _escrever(estado / "ESTADO.json", E)
        return fim("RECUSADA_DITA" if rc == 0 else "RECUSADA_NAO_DITA", MOTIVOS=motivos)
    finally:
        try:
            trava.unlink()
        except OSError:
            pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gatilho do preview: pasta completa -> publicador D126.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pasta", help="uma pasta de entrega (default: a ENTREGA curadoria/esteira/intelligence/PARA-O-CASCO)")
    g.add_argument("--raiz", help="a pasta que contem as PARA-O-CASCO-*: escolhe a completa mais recente")
    ap.add_argument("--modo", default="preview", help="ensaio | preview (producao e recusada aqui)")
    ap.add_argument("--so-conferir", action="store_true", help="so diz o que faria; nao chama o publicador")
    ap.add_argument("--registro", default=None)
    ap.add_argument("--arvore", default="HEAD")
    ap.add_argument("--host-ensaio", default=None)
    ap.add_argument("--rodada", action="store_true", help="D156: uma volta do agendador (PARAR, trava, assinatura, registo)")
    ap.add_argument("--estado", default=None, help="a pasta de estado da rodada (ESTADO.json, RODADAS.ndjson, PARAR)")
    ap.add_argument("--preview-atual", default=None, help="ficheiro estavel com a URL do ultimo preview (para o LAB)")
    a = ap.parse_args(argv)
    if a.modo not in MODOS_PERMITIDOS:
        print(f"RECUSADO: modo {a.modo!r}. Este gatilho so publica em {' / '.join(MODOS_PERMITIDOS)}; "
              "a producao continua bloqueada (correcao do dono 28/09) e nao passa por aqui.")
        return USO
    if a.rodada:
        if not a.estado or a.raiz:
            print("uso: --rodada exige --estado <pasta> (e aceita --pasta; --raiz nao)")
            return USO
        r = rodada(Path(a.pasta or ENTREGA), Path(a.estado), a.modo, preview_atual=a.preview_atual)
        print(json.dumps(r, ensure_ascii=False))
        return 0 if r["DECISAO"] not in ("RECUSADA_NAO_DITA",) else 1
    if not a.raiz:
        todas = [conferir_pasta(a.pasta or ENTREGA)]
        escolhida = todas[0] if todas[0]["COMPLETA"] else None
    else:
        escolhida, todas = escolher(a.raiz)
    for c in todas:
        print(f"  {c['ESTADO']:21} {Path(c['PASTA']).name}" + ("" if c["COMPLETA"] else "  · " + " · ".join(c["MOTIVOS"][:3])))
    if not escolhida:
        print("NADA_A_CHAMAR: nenhuma entrega completa (pote conferido pelo MANIFESTO e pelo SHA256SUMS) — o publicador nao foi chamado; o que esta no ar nao muda.")
        return SEM_PASTA
    print(f"ESCOLHIDA {Path(escolhida['PASTA']).name} · {escolhida['INTELLIGENCE_RUN_ID']} · "
          f"pote {Path(escolhida['POTE']).name} sha256 {escolhida['SHA256_POTE'][:12]}")
    if a.so_conferir:
        return 0
    gelo = Path(tempfile.mkdtemp(prefix="pote-congelado-"))
    try:
        pote = congelar_pote(escolhida, gelo)
        if not pote:
            print("MUDOU_DURANTE_A_LEITURA: o pote nao e o que foi conferido — o publicador nao foi chamado.")
            return SEM_PASTA
        import publicar_portal_sozinho as P  # so aqui: conferir uma pasta nao precisa do publicador
        args = ["--pote", str(pote), "--modo", a.modo, "--arvore", a.arvore]
        if a.registro:
            args += ["--registro", a.registro]
        if a.host_ensaio:
            args += ["--host-ensaio", a.host_ensaio]
        return P.main(args)
    finally:
        shutil.rmtree(gelo, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
