#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATILHO DO PREVIEW — correcao do dono (28/09 ~20:37), missao L3, item 3:
«PUBLICACAO AUTOMATICA NO PREVIEW (autorizada: EXCECAO E2E CONTROLADA EM PREVIEW = AUTORIZADA; PRODUCAO
continua bloqueada; ENDERECO OFICIAL = NAO). O Casco nao pode ler pasta incompleta.»

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

Nada de PRONTO.txt: seria um protocolo paralelo a um sinal que ja existe. Qualquer falta = INCOMPLETA, e
uma pasta incompleta nao e lida (nem o pote dela e aberto pelo publicador).

O QUE ISTO NAO FAZ
------------------
- nao escolhe objetos nem reescreve o pote (quem libera e a Intelligence, objeto por objeto);
- nao publica em producao: `--modo producao` e recusado AQUI, antes do publicador (a producao continua
  bloqueada por decisao do dono, e a sua porta e o publicador chamado a mao com o veredito do LAB);
- nao se agenda sozinho. «Automatico» = uma passagem idempotente sobre a raiz; quem a repete (o agendador
  da maquina) e decisao do coordenador. Uma pasta ja no ar da NADA_A_PUBLICAR pelo proprio publicador.

SAIDAS: 0 publicado / nada a publicar / so conferir · 1 bloqueado pelo publicador · 4 uso errado ·
        5 nenhuma pasta completa com pote PARA_CLIENTE (nada foi chamado) · outros = os do publicador
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

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
    pc = ((man.get("POTES") or {}).get("PARA_CLIENTE")) if isinstance(man, dict) else None
    if not isinstance(pc, dict) or not pc.get("ARQUIVO"):
        # a pasta ESTA inteira (as somas conferem); so nao ha nada liberado para cliente nela
        out["ESTADO"] = "SEM_POTE_PARA_CLIENTE"
        M.append(f"{man_p.name} nao aponta um pote PARA_CLIENTE (POTES.PARA_CLIENTE.ARQUIVO)")
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gatilho do preview: pasta completa -> publicador D126.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pasta", help="uma pasta de entrega da Intelligence (PARA-O-CASCO-Rn)")
    g.add_argument("--raiz", help="a pasta que contem as PARA-O-CASCO-*: escolhe a completa mais recente")
    ap.add_argument("--modo", default="preview", help="ensaio | preview (producao e recusada aqui)")
    ap.add_argument("--so-conferir", action="store_true", help="so diz o que faria; nao chama o publicador")
    ap.add_argument("--registro", default=None)
    ap.add_argument("--arvore", default="HEAD")
    ap.add_argument("--host-ensaio", default=None)
    a = ap.parse_args(argv)
    if a.modo not in MODOS_PERMITIDOS:
        print(f"RECUSADO: modo {a.modo!r}. Este gatilho so publica em {' / '.join(MODOS_PERMITIDOS)}; "
              "a producao continua bloqueada (correcao do dono 28/09) e nao passa por aqui.")
        return USO
    if a.pasta:
        todas = [conferir_pasta(a.pasta)]
        escolhida = todas[0] if todas[0]["COMPLETA"] else None
    else:
        escolhida, todas = escolher(a.raiz)
    for c in todas:
        print(f"  {c['ESTADO']:21} {Path(c['PASTA']).name}" + ("" if c["COMPLETA"] else "  · " + " · ".join(c["MOTIVOS"][:3])))
    if not escolhida:
        print("NADA_A_CHAMAR: nenhuma pasta completa com pote PARA_CLIENTE — o publicador nao foi chamado.")
        return SEM_PASTA
    print(f"ESCOLHIDA {Path(escolhida['PASTA']).name} · {escolhida['INTELLIGENCE_RUN_ID']} · "
          f"pote {Path(escolhida['POTE']).name} sha256 {escolhida['SHA256_POTE'][:12]}")
    if a.so_conferir:
        return 0
    import publicar_portal_sozinho as P  # so aqui: conferir uma pasta nao precisa do publicador
    args = ["--pote", escolhida["POTE"], "--modo", a.modo, "--arvore", a.arvore]
    if a.registro:
        args += ["--registro", a.registro]
    if a.host_ensaio:
        args += ["--host-ensaio", a.host_ensaio]
    return P.main(args)


if __name__ == "__main__":
    sys.exit(main())
