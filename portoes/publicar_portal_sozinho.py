#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PORTAL PUBLICA SOZINHO — D126 (dono, 27/09 ~21:40): «portal publica sozinho».

    python3 portoes/publicar_portal_sozinho.py --pote <sintonia-pote.js|pote.json> --modo ensaio
    python3 portoes/publicar_portal_sozinho.py --pote italia-portale/client/sintonia-pote.js --modo producao

Quando sai um pote novo da Intelligence, este ficheiro monta o portal EXISTENTE com ele, corre TODAS as
conferencias e, se todas passam, publica. Depois de publicar, confere o que ficou NO AR; se reprovar,
volta sozinho a versao anterior e grava ALERTA. Cada publicacao guarda antes/depois (fotos + contagens +
o pote anterior com SHA) em PUBLICACOES/, fora do Git, para o dono ver depois.

A lei (o contrato) vive em portoes/PUBLICACAO-AUTOMATICA.json. Este ficheiro so a executa.

    UM PORTAO QUE SE PODE CONTORNAR E UMA SUGESTAO.
    NAO CONSEGUI MEDIR != MEDI E ESTA MAU — mas nao medir tambem nao autoriza.

O CAMINHO
---------
  C0  o POTE: forma+lei v2, promocao, D122, D123, nenhum objeto sem prova, nada cru, nada da demo
  --  ANTES: o que esta no ar (qual deployment, que SHA de pote serve, fotos e contagens)
  --  MONTAR: `git worktree` da arvore (o codigo), sem o pote
  C1  build-gate          (a proveniencia do artefacto V2.1)
  C2  deploy-surface      (o que sobe e o que se serve)
  C3  portao do release   (os tres jobs, lidos do workflow em release/canonical — nao copiados)
  --  ENVELOPE: o pote conferido e escrito em sintonia-pote-publicado.js, SO na copia
  C5  a copia com o pote, num navegador: contagem por tela = a do pote, sem os 43/44 antigos, SHA certo
  --  IMPLANTAR (so se tudo passou)
  C6  a mesma conferencia NO AR. Reprovou -> VOLTAR a anterior -> conferir a volta -> ALERTA

SAIDAS
------
  0  PUBLICADO, ou NADA_A_PUBLICAR (o pote no ar ja e este)
  1  BLOQUEADO — nada foi ao ar
  2  REVERTIDO — foi ao ar, reprovou no ar, e voltou sozinho a anterior (ALERTA)
  3  ALERTA_CRITICO — reprovou no ar e a volta NAO se provou
  4  uso errado / pote ilegivel
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = Path(os.path.dirname(HERE))
sys.path.insert(0, str(RAIZ))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import validar_pote_v2 as V2  # noqa: E402

CONTRATO_PATH = RAIZ / "portoes" / "PUBLICACAO-AUTOMATICA.json"
CANONICO_PATH = RAIZ / "system-map" / "CANONICAL-PUBLICATION.json"
FOTOGRAFO = RAIZ / "portoes" / "fotografar_portal.mjs"
NAO_SEI = "NAO SEI"
MARCA_EXPERIMENTAL = "EXPERIMENTAL · NAO_PARA_CLIENTE"
ENVELOPE = "SINTONIA_POTE_PUBLICADO/1"
GLOBAL = "SINTONIA_POTE_PUBLICADO"
MODOS = ("ensaio", "preview", "producao")
PUBLICADO, BLOQUEADO, REVERTIDO, CRITICO, USO = 0, 1, 2, 3, 4


def carregar_contrato(caminho: Path = CONTRATO_PATH) -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


# ── O POTE ───────────────────────────────────────────────────────────────────
def sha_do_pote(pote: dict) -> str:
    """O SHA do pote: o JSON canonico (chaves ordenadas, UTF-8, sem espacos). O mesmo pote da o mesmo SHA
    em qualquer maquina, e e o que o envelope carrega para a conferencia no ar."""
    txt = json.dumps(pote, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def ler_pote(caminho) -> dict:
    return V2.ler_ficheiro(Path(caminho))


def _objetos(pote):
    for k, e in (pote.get("COMPARTIMENTOS") or {}).items():
        for o in (e or {}).get("OBJETOS") or []:
            yield k, o


def _sabido(v) -> bool:
    return v is not None and v != "" and v != NAO_SEI


def linha(ident, ok, detalhe, nota=None):
    """ok: True = PASS, False = FAIL. Uma conferencia que nao conseguiu medir e False (fail-closed)."""
    d = {"ID": ident, "PASS": bool(ok), "DETALHE": detalhe if isinstance(detalhe, list) else [detalhe]}
    if nota:
        d["NOTA"] = nota
    return d


def conferir_pote(pote: dict, contrato: dict, modo: str, veredito_lab=None, armazem=None) -> list:
    """C0 — o pote, antes de montar seja o que for. Devolve linhas; qualquer FAIL bloqueia.

    veredito_lab: o dict do veredito do LAB (ou None). armazem: a porta do armazem com os bytes do RAW
    (guarda/preservar_coleta.Armazem) ou None — em producao, None = a da raiz SINTONIA_ARMAZEM_RAIZ."""
    L = []
    # 1 · a forma e a lei do contrato unico (o validador do pote v2 — schema + conferir_pote)
    v = V2.validar(pote)
    L.append(linha("C0_POTE_V2_FORMA_E_LEI", not v, v[:12] or ["PASSA · POTE_INTELLIGENCE_CASCO/v2"]))

    # 2 · nenhum objeto sem prova ate ao RAW
    sem = []
    for k, o in _objetos(pote):
        provas = o.get("PROVA") or []
        if not provas:
            sem.append(f"{k}/{o.get('OBJETO_ID')}: sem PROVA")
        for p in provas:
            for c in ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "DOCUMENT_ID"):
                if not _sabido((p or {}).get(c)):
                    sem.append(f"{k}/{o.get('OBJETO_ID')}: prova sem {c}")
    L.append(linha("C0_NENHUM_OBJETO_SEM_PROVA", not sem, sem[:12] or ["todo objeto tem prova ITEM -> RAW -> FONTE -> DOCUMENTO"]))

    # 3 · D123 — caso -> produto -> bula: toda OPORTUNIDADE diz o produto e a prova de autorizacao (bula)
    d123 = []
    for k, o in _objetos(pote):
        if o.get("ESPECIE") == "OPORTUNIDADE":
            ch = o.get("CHAVES") or {}
            for c, nome in (("ADAMA_PRODUCT_ID", "produto"), ("AUTHORIZATION_EVIDENCE_ID", "bula")):
                if not _sabido(ch.get(c)):
                    d123.append(f"{k}/{o.get('OBJETO_ID')}: oportunidade sem {nome} ({c} = {ch.get(c, 'ausente')})")
    L.append(linha("C0_D123_CASO_PRODUTO_BULA", not d123, d123[:12] or ["toda oportunidade leva produto e bula"]))

    # 4 · D122 — evento (facto presente sobre o futuro) so com data
    d122 = []
    for k, o in _objetos(pote):
        if o.get("ESPECIE") == "FATO_PRESENTE_SOBRE_O_FUTURO":
            ft = (o.get("CHAVES") or {}).get("FACT_TIME")
            if not (isinstance(ft, str) and re.match(r"^\d{4}-(0[1-9]|1[0-2])(-\d{2})?\b", ft)):
                d122.append(f"{k}/{o.get('OBJETO_ID')}: evento sem data (FACT_TIME = {ft!r})")
    L.append(linha("C0_D122_EVENTO_SO_COM_DATA", not d122, d122[:12] or ["todo evento tem data"]))

    # 5 · nada de dado cru
    regra = contrato["NADA_DE_DADO_CRU"]
    proibidas, limite = set(regra["CHAVES_PROIBIDAS"]), int(regra["MAIOR_TEXTO"])
    cru = []

    def anda(x, onde):
        if len(cru) > 20:
            return
        if isinstance(x, dict):
            for kk, vv in x.items():
                if str(kk).upper() in proibidas:
                    cru.append(f"{onde}.{kk}: chave de dado cru")
                anda(vv, f"{onde}.{kk}")
        elif isinstance(x, list):
            for i, vv in enumerate(x):
                anda(vv, f"{onde}[{i}]")
        elif isinstance(x, str) and len(x) > limite:
            cru.append(f"{onde}: texto de {len(x)} caracteres (> {limite})")
    anda(pote, "$")
    L.append(linha("C0_NADA_DE_DADO_CRU", not cru, cru[:12] or ["nenhuma chave de dado cru, nenhum texto > %d" % limite]))

    # 6 · nada da demo — um pote sintetico nunca vai a producao
    demo = contrato["NADA_DA_DEMO"]
    achados = []
    if pote.get(demo["CAMPO"]) is True:
        achados.append(f"{demo['CAMPO']} = true")
    ids = [o.get("OBJETO_ID") for _, o in _objetos(pote)] + [pote.get("INTELLIGENCE_RUN_ID")]
    ids += [p.get("ITEM_ID") for _, o in _objetos(pote) for p in (o.get("PROVA") or [])]
    for i in ids:
        if isinstance(i, str) and i.upper().startswith(tuple(x.upper() for x in demo["PREFIXOS_DE_ID"])):
            achados.append(f"id de demo/sintetico: {i}")
            break
    if modo == "producao":
        L.append(linha("C0_NADA_DA_DEMO", not achados, achados or ["corrida real, nenhum id de demo"]))
    else:
        L.append(linha("C0_NADA_DA_DEMO", True, achados or ["corrida real, nenhum id de demo"],
                       nota=("SINTETICO — aceite so em %s; em producao reprova" % modo) if achados else None))

    # 7 · a promocao de um pote EXPERIMENTAL
    prom = contrato["REGRA_DE_PROMOCAO"]
    experimental = pote.get("MARCA") == MARCA_EXPERIMENTAL or pote.get("NAO_PARA_CLIENTE") is True
    aprovada = (prom.get("ESTADO") == "APROVADA_PELO_DONO" and _sabido(prom.get("APROVADA_POR"))
                and _sabido(prom.get("APROVADA_EM")))
    if not experimental:
        L.append(linha("C0_PROMOCAO", True, ["pote sem marca EXPERIMENTAL"]))
    elif modo == "producao":
        L.append(linha("C0_PROMOCAO", aprovada,
                       [f"pote {MARCA_EXPERIMENTAL}; regra de promocao {prom.get('ESTADO')}"
                        + ("" if aprovada else " — so o dono a aprova (portoes/PUBLICACAO-AUTOMATICA.json)")]))
    else:
        L.append(linha("C0_PROMOCAO", True, [f"regra de promocao {prom.get('ESTADO')}"],
                       nota=f"{modo}: nao e publicacao ao cliente; em producao a regra tem de estar APROVADA_PELO_DONO"))

    # 8-10 · as tres conferencias da liberacao (decisao do dono de 28/09 — REGRA_DE_PROMOCAO.AS_SEIS_CONDICOES)
    for ident, ok, det in (conferir_liberacao(pote, prom),
                           conferir_veredito_do_lab(pote, prom, veredito_lab),
                           conferir_raw_no_armazem(pote, prom, armazem, modo)):
        if modo == "producao":
            L.append(linha(ident, ok, det))
        else:
            L.append(linha(ident, True, det, nota=None if ok else
                           f"{modo}: nao e publicacao ao cliente — em producao ESTA conferencia reprova"))
    return L


# ── A LIBERACAO (decisao do dono, 28/09) ─────────────────────────────────────
def conferir_liberacao(pote: dict, prom: dict):
    """Condicao 1: cada OBJETO traz a marca de liberacao da Intelligence. A marca do pote nao conta."""
    reg = prom["LIBERACAO_POR_OBJETO"]
    campo, valor = reg["CAMPO"], reg["VALOR_QUE_LIBERA"]
    objs = list(_objetos(pote))
    if not objs:
        return "C0_LIBERADO_PARA_CLIENTE", False, ["pote sem objetos: nada a liberar"]
    nao = [f"{k}/{o.get('OBJETO_ID')}: {campo} = {o.get(campo, 'ausente')!r}" for k, o in objs
           if o.get(campo) != valor]
    return ("C0_LIBERADO_PARA_CLIENTE", not nao,
            nao[:12] + ([f"... e mais {len(nao) - 12}"] if len(nao) > 12 else []) if nao
            else [f"{len(objs)} de {len(objs)} objetos {campo} = {valor}"])


def conferir_veredito_do_lab(pote: dict, prom: dict, veredito):
    """Condicao 3: o LAB aprovou o preview DESTE pote (o SHA dele e o deste pote)."""
    if not isinstance(veredito, dict):
        return "C0_VEREDITO_DO_LAB", False, ["sem veredito do LAB (--veredito-lab)"]
    sha = sha_do_pote(pote)
    falta = []
    if veredito.get("VEREDITO") != "APROVADO":
        falta.append(f"VEREDITO = {veredito.get('VEREDITO')!r} (precisa APROVADO)")
    if veredito.get("POTE_SHA256") != sha:
        falta.append(f"veredito de outro pote: {str(veredito.get('POTE_SHA256'))[:12]} != {sha[:12]}")
    if not _sabido(veredito.get("PREVIEW")):
        falta.append("veredito sem PREVIEW")
    if not (isinstance(veredito.get("CRITERIO"), str) and re.fullmatch(r"[0-9a-f]{64}", veredito["CRITERIO"])):
        falta.append(f"CRITERIO nao e o sha256 do criterio congelado do LAB (= {veredito.get('CRITERIO')!r})")
    return ("C0_VEREDITO_DO_LAB", not falta,
            falta or [f"LAB APROVADO para o pote {sha[:12]} · preview {veredito['PREVIEW']} · criterio {veredito['CRITERIO']}"])


def _armazem_da_raiz():
    from guarda.preservar_coleta import ArmazemLocal, VARIAVEL_DA_RAIZ  # noqa: E402 — so em producao
    raiz = (os.environ.get(VARIAVEL_DA_RAIZ) or "").strip()
    if not raiz:
        raise RuntimeError(f"{VARIAVEL_DA_RAIZ} nao declarada: nao sei onde esta o armazem")
    return ArmazemLocal(raiz)


def conferir_raw_no_armazem(pote: dict, prom: dict, armazem, modo: str):
    """Condicao 4: cada PROVA leva ao arquivo original — o byte e LIDO no armazem e o sha256 recalculado bate."""
    sha_c, lugar_c = prom["RAW_NO_ARMAZEM"]["CAMPOS_DA_PROVA"]
    provas = [(k, o, p) for k, o in _objetos(pote) for p in (o.get("PROVA") or [])]
    if not provas:
        return "C0_RAW_CONFERIDO_NO_ARMAZEM", False, ["nenhuma prova para conferir"]
    if armazem is None and modo == "producao":
        try:
            armazem = _armazem_da_raiz()
        except Exception as e:  # noqa: BLE001 — fail-closed
            return "C0_RAW_CONFERIDO_NO_ARMAZEM", False, [str(e)]
    mal, vistos = [], {}
    for k, o, p in provas:
        onde = f"{k}/{o.get('OBJETO_ID')}"
        sha, lugar = (p or {}).get(sha_c), (p or {}).get(lugar_c)
        if not (isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha)):
            mal.append(f"{onde}: prova sem {sha_c} (= {sha!r})")
            continue
        if not _sabido(lugar):
            mal.append(f"{onde}: prova sem {lugar_c}")
            continue
        if armazem is None:
            mal.append(f"{onde}: armazem nao disponivel neste modo — nao conferido")
            continue
        if lugar not in vistos:
            try:
                vistos[lugar] = hashlib.sha256(armazem.ler(lugar)).hexdigest()
            except Exception as e:  # noqa: BLE001 — byte ausente = nao prova
                vistos[lugar] = f"ILEGIVEL ({type(e).__name__})"
        if vistos[lugar] != sha:
            mal.append(f"{onde}: {lugar} no armazem da {vistos[lugar][:16]} != {sha_c} {sha[:16]}")
    return ("C0_RAW_CONFERIDO_NO_ARMAZEM", not mal,
            mal[:12] or [f"{len(provas)} provas, {len(vistos)} arquivos originais relidos no armazem, sha256 bate"])


def envelope(pote: dict, sha: str, contrato: dict, modo: str, arvore: str) -> dict:
    prom = contrato["REGRA_DE_PROMOCAO"]
    return {"CONTRATO": ENVELOPE, "POTE_SHA256": sha, "INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID"),
            "MODO": modo, "ARVORE": arvore,
            "PUBLICADO_EM": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "PROMOCAO": {"ESTADO": prom.get("ESTADO"), "APROVADA_POR": prom.get("APROVADA_POR"),
                         "REGRA": "portoes/PUBLICACAO-AUTOMATICA.json#REGRA_DE_PROMOCAO"},
            "POTE": pote}


def js_do_envelope(env: dict) -> str:
    return ("/* D126 · pote PUBLICADO — escrito por portoes/publicar_portal_sozinho.py SO na copia implantada. */\n"
            f"window.{GLOBAL} = " + json.dumps(env, ensure_ascii=False) + ";\n")


def ler_envelope_js(texto: str):
    """O envelope de um sintonia-pote-publicado.js servido. None = o lugar vazio (null) ou ilegivel."""
    marca = "window." + GLOBAL + " = "
    i = texto.rfind(marca)          # a ultima: um comentario pode citar a forma do envelope
    if i < 0:
        return None
    corpo = texto[i + len(marca):].strip().rstrip(";").strip()
    if corpo.startswith("window." + GLOBAL):
        return None
    try:
        v = json.loads(corpo)
    except ValueError:
        return None
    return v if isinstance(v, dict) else None


def contagem_esperada(pote: dict, contrato: dict) -> dict:
    """Por TELA, quantos objetos do pote ela tem de desenhar — calculado do pote, aqui, e nao pelo leitor do
    casco (que e quem esta a ser conferido). Tela -> compartimento pelas VISTAS_DO_CASCO do proprio pote."""
    C = pote.get("COMPARTIMENTOS") or {}
    esp = {}
    for k, e in C.items():
        for v in (e or {}).get("VISTAS_DO_CASCO") or []:
            esp.setdefault(v, len((e or {}).get("OBJETOS") or []))
    for v, k in contrato["TELAS"]["ROTA_PARA_COMPARTIMENTO_SEM_VISTA"].items():
        e = C.get(k) or {}
        if v not in esp and e and not (e.get("OBJETOS") or []) and e.get("PORQUE_VAZIO"):
            esp[v] = 0
    if "meeting" in esp:
        esp["inicio"] = esp["meeting"]
    return esp


def conferir_telas(contagens: dict, pote: dict, sha: str, contrato: dict, rotulo: str) -> list:
    """C5/C6 — o que o navegador contou contra o que o pote diz. `contagens` e o CONTAGENS.json do fotografo."""
    esp = contagem_esperada(pote, contrato)
    telas = (contagens or {}).get("TELAS") or {}
    L = []
    if not contagens or not contagens.get("MEDICAO_COMPLETA"):
        L.append(linha(f"{rotulo}_MEDIDO", False, ["o navegador nao mediu todas as telas — nao medir nao autoriza"]))
    erros = []
    for t in contrato["TELAS"]["DO_POTE"]:
        m = telas.get(t)
        if not m:
            erros.append(f"{t}: nao medida")
            continue
        if m.get("HTTP") != 200:
            erros.append(f"{t}: HTTP {m.get('HTTP')}")
        if not m.get("POTE_NA_TELA"):
            erros.append(f"{t}: a tela nao desenha o pote")
        if m.get("POTE_RECUSADO"):
            erros.append(f"{t}: o casco recusou o pote")
        if not m.get("MARCA"):
            erros.append(f"{t}: sem a faixa do pote")
        if t in esp and m.get("POTE_OBJETOS") != esp[t]:
            erros.append(f"{t}: {m.get('POTE_OBJETOS')} objetos na tela, o pote tem {esp[t]}")
        if t not in esp:
            erros.append(f"{t}: o pote nao diz o que esta tela desenha")
        env = m.get("ENVELOPE") or {}
        if env.get("POTE_SHA256") != sha:
            erros.append(f"{t}: SHA servido {env.get('POTE_SHA256')} != {sha}")
    L.append(linha(f"{rotulo}_CONTAGEM_POR_TELA", not erros, erros[:15] or
                   [f"{len(contrato['TELAS']['DO_POTE'])} telas, cada uma com a contagem do pote e o SHA {sha[:12]}"]))

    # D122 — nenhum dos 43/44 antigos, nem cartao de legado, em tela nenhuma do portal (porta incluida)
    leg = []
    for t in contrato["TELAS"]["DO_POTE"] + contrato["TELAS"]["PORTA"]:
        m = telas.get(t) or {}
        for c in ("LEGADO_43_VISIVEIS", "LEGADO_44_VISIVEIS", "LEGADO_CARTOES"):
            if m.get(c) != 0:
                leg.append(f"{t}: {c} = {m.get(c)}")
        if t in contrato["TELAS"]["DO_POTE"] and not m.get("LEGADO_43_UNIVERSO"):
            leg.append(f"{t}: o universo dos 43 nao foi lido — o detector nao mediu")
        if t in contrato["TELAS"]["DO_POTE"] and m.get("OGGI_LEGADO") is not False:
            leg.append(f"{t}: a caixa «oggi» do pacote de 02/09 continua na barra (ou nao foi medida)")
    L.append(linha(f"{rotulo}_D122_LEGADO_ESCONDIDO", not leg, leg[:15] or ["nenhum dos 43 nem dos 44 antigos nas telas do portal"]))

    # D122 — a barra conta o pote (o numero do legado nao fica ao lado)
    nav = []
    for t in contrato["TELAS"]["DO_POTE"]:
        m = telas.get(t) or {}
        for v, n in (m.get("NAV") or {}).items():
            if v in esp and str(n) != str(esp[v]):
                nav.append(f"{t}: a barra diz {v}={n}, o pote tem {esp[v]}")
        if not m.get("NAV"):
            nav.append(f"{t}: barra nao medida")
    L.append(linha(f"{rotulo}_D122_BARRA_CONTA_O_POTE", not nav, sorted(set(nav))[:15] or ["cada voz da barra conta o compartimento do pote"]))

    # fora das rotas: medido e fotografado, dito — nao bloqueia (contrato: TELAS.FORA_DAS_ROTAS)
    for t, porque in contrato["TELAS"]["FORA_DAS_ROTAS"].items():
        m = telas.get(t) or {}
        L.append(linha(f"{rotulo}_FORA_DAS_ROTAS_{t.upper()}", True,
                       [f"{t}: 43 visiveis {m.get('LEGADO_43_VISIVEIS')}, 44 visiveis {m.get('LEGADO_44_VISIVEIS')}"],
                       nota="AVISO: " + porque if (m.get("LEGADO_43_VISIVEIS") or m.get("LEGADO_44_VISIVEIS")) else None))
    return L


# ── AS CONFERENCIAS QUE CORREM NA COPIA ──────────────────────────────────────
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def correr(cmd, cwd, timeout=2400, env=None):
    if isinstance(cmd, list) and cmd and shutil.which(cmd[0]):
        # no Windows `npm` e `npm.cmd`: sem isto o subprocess nao o acha e a conferencia morre por ferramenta
        cmd = [shutil.which(cmd[0])] + cmd[1:]
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, env=env, shell=isinstance(cmd, str))
        return p.returncode, ANSI.sub("", p.stdout + "\n" + p.stderr)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    except OSError as e:
        return None, f"NAO CORREU: {e}"


def falhas_do_run_mjs(saida: str):
    """Os portoes do portal que reprovaram, pelo ID, e se a corrida chegou ao fim (a linha 'N/M passing')."""
    fim = re.search(r"(\d+)/(\d+) passing", saida)
    ids = re.findall(r"^\s*FAIL\s+(\S+)\s", saida, re.M)
    return (fim is not None), sorted(set(ids))


def conferir_comando(ident, cmd, cwd, contrato, timeout=2400):
    rc, saida = correr(cmd, cwd, timeout)
    cauda = [l for l in saida.strip().splitlines() if l.strip()][-6:]
    texto = cmd if isinstance(cmd, str) else " ".join(cmd)
    if rc == 0:
        return linha(ident, True, [f"$ {texto} -> 0"] + cauda[-2:])
    if "audit/run.mjs" in texto and rc not in (None,):
        chegou, ids = falhas_do_run_mjs(saida)
        herdados = set(k for k in contrato["VERMELHOS_HERDADOS_DO_RELEASE"] if k != "PORQUE")
        novos = [i for i in ids if i not in herdados]
        if chegou and ids and not novos:
            return linha(ident, True, [f"$ {texto} -> {rc}: so vermelhos HERDADOS e declarados: {', '.join(ids)}"],
                         nota="INHERITED RED != NEW DEPLOY REGRESSION")
        return linha(ident, False, [f"$ {texto} -> {rc}", f"vermelhos novos: {novos or '(a corrida nao chegou ao fim)'}"] + cauda)
    return linha(ident, False, [f"$ {texto} -> {rc}"] + cauda)


def comandos_do_release(contrato, repo: Path = RAIZ):
    """Os `run:` dos tres jobs do portao do release, LIDOS do workflow em RELEASE_REF — nao copiados.
    Devolve (lista de (job, passo, comando), erro)."""
    try:
        import yaml  # noqa: WPS433
    except ImportError:
        return None, "DEPENDENCIA AUSENTE: PyYAML (pip install pyyaml) — nao consigo ler o portao do release"
    ref = contrato["RELEASE_REF"]
    rc, txt = correr(["git", "show", f"{ref}:.github/workflows/portao-do-release.yml"], repo, 60)
    if rc != 0:
        return None, f"nao consegui ler .github/workflows/portao-do-release.yml em {ref} (git fetch origin release/canonical?)"
    wf = yaml.safe_load(txt)
    fora = set(contrato["PASSOS_DE_FERRAMENTA_DO_RELEASE"])
    cmds = []
    for job, j in (wf.get("jobs") or {}).items():
        for st in j.get("steps") or []:
            if "run" in st and st.get("name") not in fora:
                for c in [x.strip() for x in str(st["run"]).splitlines() if x.strip() and not x.strip().startswith("#")]:
                    cmds.append((job, st.get("name"), c))
    if not cmds:
        return None, "o portao do release nao tem nenhum passo `run:` — nada a conferir e nao se aprova o vazio"
    return cmds, None


def conferencias_do_codigo(copia: Path, contrato: dict) -> list:
    """C1, C2, C3 — o CODIGO, na copia montada, antes do envelope."""
    L = [conferir_comando("C1_BUILD_GATE", ["node", "italia-portale/audit/build-gate.mjs"], copia, contrato, 600),
         conferir_comando("C2_DEPLOY_SURFACE", ["node", "italia-portale/audit/deploy-surface.mjs"], copia, contrato, 600)]
    cmds, erro = comandos_do_release(contrato)
    if erro:
        return L + [linha("C3_RELEASE", False, [erro])]
    for job, passo, c in cmds:
        L.append(conferir_comando(f"C3_RELEASE · {job} · {c[:60]}", c, copia, contrato, 3600))
    return L


# ── O SERVIDOR LOCAL (a copia montada, e o anfitriao do ENSAIO) ─────────────
def _handler(raiz_fn):
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def translate_path(self, caminho):
            base = Path(raiz_fn())
            rel = caminho.split("?", 1)[0].split("#", 1)[0]
            rel = urllib.request.url2pathname(rel).lstrip("/\\")
            alvo = (base / rel) if rel else (base / "index.html")
            # cleanUrls, como na Vercel: /portale -> portale.html
            if not alvo.exists() and not alvo.suffix and alvo.with_suffix(".html").exists():
                alvo = alvo.with_suffix(".html")
            try:
                alvo.resolve().relative_to(base.resolve())
            except ValueError:
                return str(base / "__fora__")
            return str(alvo)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()
    return H


class Servidor:
    """Serve uma pasta (ou a pasta que `raiz_fn()` disser a cada pedido) em 127.0.0.1, porta livre."""

    def __init__(self, raiz_fn):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.porta = s.getsockname()[1]
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", self.porta), _handler(raiz_fn))
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()
        self.url = f"http://127.0.0.1:{self.porta}"

    def fechar(self):
        self.srv.shutdown()
        self.srv.server_close()


# ── O FOTOGRAFO ──────────────────────────────────────────────────────────────
def achar_playwright() -> Path | None:
    """O playwright-core que os portoes usam: o da raiz (npm install), ou o que vem com o playwright global."""
    cand = [RAIZ / "node_modules" / "playwright-core"]
    rc, raiz_g = correr(["npm", "root", "-g"], RAIZ, 60)
    if rc == 0 and raiz_g.strip():
        g = Path(raiz_g.strip().splitlines()[0])
        cand += [g / "playwright-core", g / "playwright" / "node_modules" / "playwright-core"]
    for c in cand:
        if (c / "package.json").exists():
            return c
    return None


def ligar_playwright(destino: Path) -> bool:
    pw = achar_playwright()
    if not pw:
        return False
    nm = destino / "node_modules"
    nm.mkdir(parents=True, exist_ok=True)
    alvo = nm / "playwright-core"
    if not alvo.exists():
        try:
            alvo.symlink_to(pw, target_is_directory=True)
        except OSError:
            # Windows sem modo de programador nao cria symlink: copia-se (e so a copia montada, descartavel)
            shutil.copytree(pw, alvo)
    return True


def fotografar(base_url: str, saida: Path, ferramentas: Path, contrato: dict) -> dict | None:
    """Corre o fotografo (node) sobre `base_url`. Devolve o CONTAGENS.json, ou None se nem isso nasceu."""
    telas = contrato["TELAS"]["DO_POTE"] + contrato["TELAS"]["PORTA"] + list(contrato["TELAS"]["FORA_DAS_ROTAS"])
    saida.mkdir(parents=True, exist_ok=True)
    rc, txt = correr(["node", str(ferramentas / "fotografar_portal.mjs"), "--base", base_url, "--saida", str(saida),
                      "--telas", ",".join(telas)], ferramentas, 900)
    (saida / "FOTOGRAFO.log").write_text(txt, encoding="utf-8")
    f = saida / "CONTAGENS.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def sha_no_ar(base_url: str, timeout=30):
    """(status, sha) do pote que o endereco serve. sha None = o lugar vazio; status None = nao consegui medir."""
    try:
        req = urllib.request.Request(base_url.rstrip("/") + "/sintonia-pote-publicado.js",
                                     headers={"Cache-Control": "no-cache", "User-Agent": "sintonia-publicador"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            env = ler_envelope_js(r.read().decode("utf-8", "replace"))
            if env is None:
                return r.status, None
            pote = env.get("POTE")
            # o SHA declarado tem de ser o do pote que viaja com ele
            if not isinstance(pote, dict) or sha_do_pote(pote) != env.get("POTE_SHA256"):
                return r.status, "ENVELOPE_INCOERENTE"
            return r.status, env.get("POTE_SHA256")
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None


# ── OS IMPLANTADORES — a mesma interface para o ensaio e para a Vercel ──────
class Implantador:
    nome = "?"
    publica_de_verdade = False

    def atual(self) -> dict:           # o que esta no ar agora: {"ID", "URL"}
        raise NotImplementedError

    def implantar(self, copia: Path, prod: bool) -> dict:   # {"ID", "URL"}
        raise NotImplementedError

    def voltar(self, anterior: dict) -> bool:
        raise NotImplementedError

    def url_no_ar(self, novo: dict | None = None) -> str:
        raise NotImplementedError

    def fechar(self):
        pass


class EnsaioLocal(Implantador):
    """Um anfitriao LOCAL com deployments e um alias — nao sai da maquina. Serve o alias em 127.0.0.1, e
    voltar e repor o alias no deployment anterior. E o ensaio completo sem publicar de verdade."""
    nome = "ENSAIO_LOCAL"

    def __init__(self, pasta: Path):
        self.pasta = Path(pasta)
        (self.pasta / "deployments").mkdir(parents=True, exist_ok=True)
        self.alias = self.pasta / "ALIAS"
        self.srv = Servidor(lambda: self.pasta / "deployments" / (self._alias() or "__nenhum__"))

    def _alias(self):
        return self.alias.read_text(encoding="utf-8").strip() if self.alias.exists() else None

    def semear(self, pasta_cliente: Path, ident="ensaio-inicial"):
        """O que esta «no ar» antes do primeiro ensaio: uma copia do cliente, sem pote."""
        d = self.pasta / "deployments" / ident
        if not d.exists():
            shutil.copytree(pasta_cliente, d)
        if not self._alias():
            self.alias.write_text(ident, encoding="utf-8")

    def atual(self):
        a = self._alias()
        return {"ID": a, "URL": self.srv.url} if a else {}

    def implantar(self, copia, prod):
        ident = "ensaio-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        shutil.copytree(Path(copia) / "italia-portale" / "client", self.pasta / "deployments" / ident)
        self.alias.write_text(ident, encoding="utf-8")
        return {"ID": ident, "URL": self.srv.url}

    def voltar(self, anterior):
        if not anterior.get("ID") or not (self.pasta / "deployments" / anterior["ID"]).exists():
            return False
        self.alias.write_text(anterior["ID"], encoding="utf-8")
        return True

    def url_no_ar(self, novo=None):
        return self.srv.url

    def fechar(self):
        self.srv.fechar()


class VercelCLI(Implantador):
    """O CLI da Vercel ja logado na maquina do coordenador. NAO TESTADO nesta missao (o contentor nao tem o
    CLI nem credencial): cada comando esta no contrato, e qualquer saida que nao se consiga ler = FAIL."""
    nome = "VERCEL_CLI"
    publica_de_verdade = True

    def __init__(self, prod: bool):
        self.prod = prod
        self.bin = shutil.which("vercel")
        self.host = json.loads(CANONICO_PATH.read_text(encoding="utf-8"))["CANONICAL_HOST"]

    def _v(self, args, cwd=RAIZ, timeout=1800):
        if not self.bin:
            return None, "DEPENDENCIA AUSENTE: vercel CLI (npm i -g vercel; vercel login; vercel link)"
        return correr([self.bin] + args, cwd, timeout)

    def atual(self):
        rc, txt = self._v(["inspect", self.host], timeout=120)
        m = re.search(r"\b(dpl_[A-Za-z0-9]+)", txt or "")
        return {"ID": m.group(1), "URL": "https://" + self.host} if rc == 0 and m else {"ERRO": (txt or "")[-400:]}

    def implantar(self, copia, prod):
        link = RAIZ / ".vercel" / "project.json"
        if not link.exists():
            return {"ERRO": "projeto Vercel nao ligado nesta maquina (.vercel/project.json) — `vercel link`"}
        (Path(copia) / ".vercel").mkdir(exist_ok=True)
        shutil.copy2(link, Path(copia) / ".vercel" / "project.json")
        amb = "production" if prod else "preview"
        for a in (["pull", "--yes", f"--environment={amb}"], ["build"] + (["--prod"] if prod else [])):
            rc, txt = self._v(a, cwd=copia)
            if rc != 0:
                return {"ERRO": f"vercel {' '.join(a)} -> {rc}: {txt[-400:]}"}
        rc, txt = self._v(["deploy", "--prebuilt", "--archive=tgz"] + (["--prod"] if prod else []), cwd=copia)
        urls = re.findall(r"https://[A-Za-z0-9.-]+\.vercel\.app", txt or "")
        if rc != 0 or not urls:
            return {"ERRO": f"vercel deploy -> {rc}: {(txt or '')[-400:]}"}
        rc2, t2 = self._v(["inspect", urls[-1]], timeout=120)
        m = re.search(r"\b(dpl_[A-Za-z0-9]+)", t2 or "")
        return {"ID": m.group(1) if m else None, "URL": urls[-1]}

    def voltar(self, anterior):
        if not anterior.get("ID"):
            return False
        rc, _ = self._v(["rollback", anterior["ID"], "--yes"], timeout=600)
        return rc == 0

    def url_no_ar(self, novo=None):
        # producao: o endereco fixo do produto. preview: o endereco do proprio deployment.
        return ("https://" + self.host) if self.prod or not novo else novo.get("URL")


# ── O REGISTO ────────────────────────────────────────────────────────────────
def _escrever(p: Path, dado):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dado, ensure_ascii=False, indent=1), encoding="utf-8")


def _alerta(registro: Path, dado: dict):
    registro.mkdir(parents=True, exist_ok=True)
    with open(registro / "ALERTAS.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(dado, ensure_ascii=False) + "\n")


def _falhou(linhas):
    return [l["ID"] for l in linhas if not l["PASS"]]


def _imprimir(linhas):
    for l in linhas:
        print(f"  {'PASS' if l['PASS'] else 'FAIL'}  {l['ID']}" + (f"   [{l['NOTA']}]" if l.get("NOTA") else ""))
        if not l["PASS"]:
            for d in l["DETALHE"][:8]:
                print(f"        {d}")


# ── O CAMINHO INTEIRO ────────────────────────────────────────────────────────
class Publicador:
    """O caminho inteiro. As pecas que tocam o mundo (montar, conferir o codigo, fotografar, implantar)
    sao metodos, para a prova as poder trocar sem mexer na decisao."""

    def __init__(self, contrato, implantador: Implantador, registro: Path, modo: str, arvore: str = "HEAD",
                 espera_no_ar: int = 180, veredito_lab=None, armazem=None, veredito_arquivo=None):
        self.c, self.imp, self.registro, self.modo, self.arvore = contrato, implantador, Path(registro), modo, arvore
        self.veredito_lab, self.armazem = veredito_lab, armazem
        self.veredito_arquivo = veredito_arquivo   # {"ARQUIVO": caminho, "SHA256": sha dos bytes do ficheiro}
        self.espera = espera_no_ar
        self.tmp = None

    # peças trocaveis --------------------------------------------------------
    def montar(self) -> tuple:
        """(copia, ferramentas, commit) — um worktree da arvore, sem o pote, e a pasta do fotografo."""
        self.tmp = Path(tempfile.mkdtemp(prefix="sintonia-montagem-"))
        copia, ferr = self.tmp / "arvore", self.tmp / "ferramentas"
        rc, txt = correr(["git", "rev-parse", self.arvore], RAIZ, 60)
        if rc != 0:
            raise RuntimeError(f"arvore {self.arvore} nao existe: {txt[-200:]}")
        commit = txt.strip().splitlines()[0]
        rc, txt = correr(["git", "worktree", "add", "--detach", str(copia), commit], RAIZ, 600)
        if rc != 0:
            raise RuntimeError(f"git worktree add -> {rc}: {txt[-300:]}")
        ferr.mkdir(parents=True)
        shutil.copy2(FOTOGRAFO, ferr / "fotografar_portal.mjs")
        if not (ligar_playwright(ferr) and ligar_playwright(copia)):
            raise RuntimeError("DEPENDENCIA AUSENTE: playwright-core (npm install --no-save playwright-core)")
        return copia, ferr, commit

    def desmontar(self):
        if self.tmp:
            correr(["git", "worktree", "remove", "--force", str(self.tmp / "arvore")], RAIZ, 300)
            shutil.rmtree(self.tmp, ignore_errors=True)
            correr(["git", "worktree", "prune"], RAIZ, 60)

    def conferir_codigo(self, copia):
        return conferencias_do_codigo(copia, self.c)

    def escrever_envelope(self, copia, env):
        (Path(copia) / "italia-portale" / "client" / "sintonia-pote-publicado.js").write_text(
            js_do_envelope(env), encoding="utf-8")

    def construir(self, copia):
        """A build, como a Vercel a corre (prebuild = C1 outra vez, agora com o envelope)."""
        return conferir_comando("C1_BUILD_COM_O_POTE (npm run build)", ["npm", "run", "build"], copia, self.c, 1800)

    def conferir_montagem(self, copia, ferr, pote, sha, pasta):
        srv = Servidor(lambda: Path(copia) / "italia-portale" / "client")
        try:
            cont = fotografar(srv.url, pasta, ferr, self.c)
        finally:
            srv.fechar()
        return conferir_telas(cont, pote, sha, self.c, "C5_MONTAGEM"), cont

    def conferir_no_ar(self, url, ferr, pote, sha, pasta):
        """C6 — espera o SHA certo no ar (o alias demora), e depois a mesma conferencia de C5."""
        fim, st, s = time.time() + self.espera, None, None
        while True:
            st, s = sha_no_ar(url)
            if s == sha or time.time() >= fim:
                break
            time.sleep(5)
        L = [linha("C6_NO_AR_SHA", s == sha, [f"{url}/sintonia-pote-publicado.js -> HTTP {st}, SHA {s}"])]
        cont = fotografar(url, pasta, ferr, self.c)
        return L + conferir_telas(cont, pote, sha, self.c, "C6_NO_AR"), cont

    # a decisao ----------------------------------------------------------------
    def publicar(self, pote: dict, origem: str = "") -> int:
        agora = _dt.datetime.now()
        sha = sha_do_pote(pote)
        reg = self.registro / agora.strftime("%Y-%m-%d") / f"{agora.strftime('%H%M%S-%f')}-{sha[:8]}"
        R = {"D126": "portal publica sozinho", "MODO": self.modo, "IMPLANTADOR": self.imp.nome,
             "POTE": {"ORIGEM": origem, "POTE_SHA256": sha, "INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID"),
                      "CONTAGENS": {k: len((e or {}).get("OBJETOS") or []) for k, e in (pote.get("COMPARTIMENTOS") or {}).items()}},
             "INICIO": agora.isoformat(timespec="seconds"), "CONFERENCIAS": [], "AVISOS": [],
             "VEREDITO_DO_LAB": dict(self.veredito_arquivo or {"ARQUIVO": None, "SHA256": None},
                                     POTE_SHA256=(self.veredito_lab or {}).get("POTE_SHA256"),
                                     VEREDITO=(self.veredito_lab or {}).get("VEREDITO"),
                                     CRITERIO=(self.veredito_lab or {}).get("CRITERIO"))}
        ultima_p = self.registro / "ULTIMA-PUBLICACAO.json"
        ultima = json.loads(ultima_p.read_text(encoding="utf-8")) if ultima_p.exists() else None

        def fim(estado, rc):
            R["ESTADO"], R["FIM"] = estado, _dt.datetime.now().isoformat(timespec="seconds")
            _escrever(reg / "REGISTO.json", R)
            print(f"\n  {estado} · registo: {reg}")
            return rc

        print(f"\n  SINTONIA · O PORTAL PUBLICA SOZINHO (D126) · modo {self.modo} · pote {sha[:12]}")
        if self.modo == "producao" and not self.imp.publica_de_verdade:
            R["CONFERENCIAS"].append(linha("MODO", False, ["producao so com um implantador que publica de verdade"]))
            return fim("BLOQUEADO", BLOQUEADO)

        # C0 — o pote
        L0 = conferir_pote(pote, self.c, self.modo, self.veredito_lab, self.armazem)
        R["CONFERENCIAS"] += L0
        _imprimir(L0)
        if _falhou(L0):
            return fim("BLOQUEADO", BLOQUEADO)

        # ANTES — o que esta no ar
        anterior = self.imp.atual()
        url_antes = self.imp.url_no_ar()
        st_antes, sha_antes = sha_no_ar(url_antes)
        R["ANTERIOR"] = {"DEPLOYMENT": anterior, "URL": url_antes, "HTTP": st_antes, "POTE_SHA256_NO_AR": sha_antes,
                         "ULTIMA_PUBLICACAO_REGISTADA": (ultima or {}).get("POTE_SHA256")}
        if ultima and ultima.get("POTE_SHA256") != sha_antes:
            R["AVISOS"].append(f"DERIVA: a ultima publicacao registada ({(ultima.get('POTE_SHA256') or '')[:12]}) nao e o que "
                               f"esta no ar ({(sha_antes or 'nenhum pote')[:12]}) — outro deploy (ex.: merge em release/canonical)")
            _alerta(self.registro, {"QUANDO": agora.isoformat(timespec="seconds"), "TIPO": "DERIVA", "REGISTO": str(reg),
                                    "NO_AR": sha_antes, "REGISTADA": ultima.get("POTE_SHA256")})
        if sha_antes == sha and self.modo != "preview":
            print("  o pote no ar ja e este — nada a publicar")
            return fim("NADA_A_PUBLICAR", PUBLICADO)
        if self.modo == "producao" and not anterior.get("ID"):
            R["CONFERENCIAS"].append(linha("ANTES_ALVO_DE_VOLTA", False, [f"nao sei o que esta no ar: {anterior}"]))
            return fim("BLOQUEADO", BLOQUEADO)
        R["CONFERENCIAS"].append(linha("ANTES_ALVO_DE_VOLTA", bool(anterior.get("ID")) or self.modo == "preview",
                                       [f"volta para {anterior.get('ID')} ({url_antes})"]))

        try:
            try:
                copia, ferr, commit = self.montar()
            except Exception as e:  # noqa: BLE001 — fail-closed
                R["CONFERENCIAS"].append(linha("MONTAR", False, [str(e)]))
                return fim("BLOQUEADO", BLOQUEADO)
            R["ARVORE"] = {"REF": self.arvore, "COMMIT": commit}
            antes = fotografar(url_antes, reg / "ANTES", ferr, self.c)
            R["ANTES"] = {"PASTA": "ANTES", "MEDICAO_COMPLETA": bool(antes and antes.get("MEDICAO_COMPLETA"))}
            if self.modo == "producao" and not R["ANTES"]["MEDICAO_COMPLETA"]:
                R["CONFERENCIAS"].append(linha("ANTES_FOTOGRAFADO", False, ["sem o antes, o dono nao tem com que comparar"]))
                return fim("BLOQUEADO", BLOQUEADO)

            # C1 C2 C3 — o codigo, sem o pote
            Lc = self.conferir_codigo(copia)
            R["CONFERENCIAS"] += Lc
            _imprimir(Lc)
            if _falhou(Lc):
                return fim("BLOQUEADO", BLOQUEADO)

            # o envelope, a build, e C5 — a copia com o pote, num navegador
            env = envelope(pote, sha, self.c, self.modo, commit)
            self.escrever_envelope(copia, env)
            Lb = [self.construir(copia)]
            L5, cont5 = self.conferir_montagem(copia, ferr, pote, sha, reg / "MONTAGEM")
            R["CONFERENCIAS"] += Lb + L5
            _imprimir(Lb + L5)
            R["AVISOS"] += [l["NOTA"] for l in L0 + Lc + L5 if l.get("NOTA")]
            if _falhou(Lb + L5):
                return fim("BLOQUEADO", BLOQUEADO)

            # IMPLANTAR
            novo = self.imp.implantar(copia, prod=(self.modo != "preview"))
            R["IMPLANTADO"] = novo
            if not novo.get("ID") and not novo.get("URL"):
                R["CONFERENCIAS"].append(linha("IMPLANTAR", False, [str(novo.get("ERRO"))]))
                return fim("BLOQUEADO", BLOQUEADO)
            (reg / "POTE-PUBLICADO.js").write_text(js_do_envelope(env), encoding="utf-8")
            if ultima and ultima.get("POTE_JS") and Path(ultima["POTE_JS"]).exists():
                shutil.copy2(ultima["POTE_JS"], reg / "POTE-ANTERIOR.js")
            R["POTE_ANTERIOR"] = {"POTE_SHA256": (ultima or {}).get("POTE_SHA256") or sha_antes,
                                  "INTELLIGENCE_RUN_ID": (ultima or {}).get("INTELLIGENCE_RUN_ID"),
                                  "FICHEIRO": "POTE-ANTERIOR.js" if (reg / "POTE-ANTERIOR.js").exists() else None}

            # C6 — no ar
            url = self.imp.url_no_ar(novo)
            L6, cont6 = self.conferir_no_ar(url, ferr, pote, sha, reg / "DEPOIS")
            R["CONFERENCIAS"] += L6
            _imprimir(L6)
            if not _falhou(L6):
                if self.modo != "preview":
                    _escrever(ultima_p, {"POTE_SHA256": sha, "INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID"),
                                         "PUBLICADO_EM": R["INICIO"], "MODO": self.modo, "DEPLOYMENT": novo,
                                         "REGISTO": str(reg), "POTE_JS": str(reg / "POTE-PUBLICADO.js"),
                                         "CONTAGENS": R["POTE"]["CONTAGENS"], "ANTERIOR": R["POTE_ANTERIOR"]})
                return fim("PUBLICADO", PUBLICADO)

            # reprovou no ar: VOLTAR sozinho, e provar a volta
            if self.modo == "preview":
                _alerta(self.registro, {"QUANDO": R["INICIO"], "TIPO": "PREVIEW_REPROVADO", "REGISTO": str(reg)})
                return fim("PREVIEW_REPROVADO", REVERTIDO)
            voltou = self.imp.voltar(anterior)
            # A volta prova-se no AR, e por duas medidas: o deployment atras do endereco E o pote servido.
            # So o SHA nao chega — um deploy partido que serve o lugar vazio tem o mesmo SHA (nenhum) que um
            # anterior sem pote, e passaria por volta.
            depois = self.imp.atual()
            st_v, sha_v = sha_no_ar(self.imp.url_no_ar())
            provada = (bool(voltou) and depois.get("ID") == anterior.get("ID") and st_v == 200 and sha_v == sha_antes)
            R["VOLTA"] = {"PARA": anterior, "COMANDO_OK": bool(voltou), "NO_AR": depois, "HTTP": st_v,
                          "POTE_SHA256_NO_AR": sha_v, "ESPERADO": sha_antes, "PROVADA": provada}
            if provada:
                fotografar(self.imp.url_no_ar(), reg / "DEPOIS-DA-VOLTA", ferr, self.c)
            _alerta(self.registro, {"QUANDO": R["INICIO"], "TIPO": "REVERTIDO" if provada else "ALERTA_CRITICO",
                                    "REGISTO": str(reg), "FALHAS": _falhou(L6), "VOLTA": R["VOLTA"]})
            return fim("REVERTIDO" if provada else "ALERTA_CRITICO", REVERTIDO if provada else CRITICO)
        finally:
            self.desmontar()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="O portal publica sozinho (D126).")
    ap.add_argument("--pote", required=True, help="o pote da Intelligence (sintonia-pote.js ou .json)")
    ap.add_argument("--modo", choices=MODOS, required=True,
                    help="ensaio = anfitriao local; preview = Vercel sem --prod; producao = Vercel --prod")
    ap.add_argument("--arvore", default="HEAD", help="o codigo a publicar (ref do git)")
    ap.add_argument("--registro", default=str(RAIZ / "PUBLICACOES"))
    ap.add_argument("--host-ensaio", default=None, help="pasta do anfitriao local do ensaio")
    ap.add_argument("--veredito-lab", default=None, help="o veredito do LAB para ESTE pote (JSON) — exigido em producao")
    a = ap.parse_args(argv)
    try:
        pote = ler_pote(a.pote)
        veredito, veredito_arquivo = None, None
        if a.veredito_lab:
            vb = Path(a.veredito_lab).read_bytes()
            veredito = json.loads(vb.decode("utf-8"))
            veredito_arquivo = {"ARQUIVO": str(a.veredito_lab), "SHA256": hashlib.sha256(vb).hexdigest()}
    except (OSError, ValueError) as e:
        print(f"ILEGIVEL: {e}")
        return USO
    contrato = carregar_contrato()
    if a.modo == "ensaio":
        host = Path(a.host_ensaio or (Path(a.registro) / "_ensaio_host"))
        imp = EnsaioLocal(host)
        imp.semear(RAIZ / "italia-portale" / "client")
    else:
        imp = VercelCLI(prod=(a.modo == "producao"))
    try:
        return Publicador(contrato, imp, Path(a.registro), a.modo, a.arvore,
                          veredito_lab=veredito, veredito_arquivo=veredito_arquivo).publicar(pote, origem=str(a.pote))
    finally:
        imp.fechar()


if __name__ == "__main__":
    sys.exit(main())
