#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O VOCABULARIO UNICO v1 — praga, cultura e lugar com CODIGO + ALIAS + VERSAO.

    MISSAO   POTES-UM-CARTAO (D125, dono 27/09 ~21:40: «potes, aprovo»), ordem §11.3 passo 1 de
             docs/lab/IDENTIDADE-CRUZAMENTO.md. D104.3: o dono do vocabulario e UM registro.
    ESPECIE  MOTOR (Z-MOTOR) — vocabulario da Intelligence. NAO E COLETA. NAO TOCA REDE.

    python3 motor/vocabulario_unico.py            # imprime a tabela (codigo, aliases, versao, impressao)

NAO INVENTA TERMO NENHUM
------------------------
Este ficheiro nao tem uma unica palavra agronomica escrita a mao. Ele COMPOE, em tempo de execucao, o que
o repositorio ja declara (uma lista copiada seriam duas verdades):

    cultura  motor/cruzamentos_max.py:CULTURAS_ROTULO (copia guardada por teste do leitor de rotulos,
             coleta/rotulos_ler.py) + :GRUPOS_DO_LEITOR + :PALAVRAS_DE_GRUPO
             + leis/boletim_do_campo.py:CULTURAS/FORMAS (plural -> singular)
    praga    motor/cruzamentos_max.py:ALVOS_CANON + leis/boletim_do_campo.py:MESMO_PROBLEMA
             (a lista declarada de sinonimos; «nao e EPPO» — por isso aqui nao ha codigo EPPO)
    lugar    leis/fato_local.py:REGIOES/PROVINCIAS (o gazetteer declarado, «cobertura declarada, nao
             presumida»)

AS TRES REGRAS QUE O VOCABULARIO SEGURA (red team RT05/RT06/RT07, IDENTIDADE-CRUZAMENTO §9)
------------------------------------------------------------------------------------------
    1. GRUPO != ESPECIE. «drupacee» e CROP_GRUPO:DRUPACEE e nunca vira CROP:PESCO; e a chave do leitor que
       junta varias culturas (CUCURBITACEE = melone|zucchina|...) NAO junta na identidade: o codigo leva a
       forma da especie (CROP:CUCURBITACEE/MELONE != CROP:CUCURBITACEE/ZUCCHINA).
    2. Ambiguo = NAO SEI. «mosca» sozinho nao e praga nenhuma; «vite e olivo» nao e uma cultura.
    3. Sinonimo so por lista declarada: «bactrocera oleae» = «mosca delle olive» = «mosca dell'olivo».

Trocar qualquer lista acima muda a IMPRESSAO; trocar de VERSAO e migracao explicita (INT-LAW-216).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

from boletim_do_campo import CULTURAS as CULTURAS_BOLETIM, FORMAS, nome_do_problema   # noqa: E402  (leis/)
from fato_local import REGIOES, PROVINCIAS                                            # noqa: E402  (leis/)

VERSAO = "VOCAB-v1"
NAO_SEI = "NAO SEI"


def dobrar(s) -> str:
    """minusculas, sem acento, espacos simples. `leis/boletim_do_campo.py` dobra igual."""
    t = "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", t.replace("’", "'")).strip()


def _leitor():
    """As listas do leitor de rotulos. Importadas na hora (o motor dos cruzamentos importa este ficheiro)."""
    import cruzamentos_max as XM   # noqa: E402  (motor/)
    return XM


# ── CULTURA ──────────────────────────────────────────────────────────────────
def _forma(n: str) -> str:
    return FORMAS.get(n, n)


def cultura(nome):
    """`nome` -> CODIGO (`CROP:...` / `CROP_GRUPO:...`) ou None (= NAO SEI: ausente, desconhecida ou ambigua)."""
    n = dobrar(nome)
    if not n or n == dobrar(NAO_SEI):
        return None
    XM = _leitor()
    # 1. a palavra de GRUPO que os rotulos escrevem («Pomacee (melo, pero)») e um grupo, sempre.
    if n in XM.PALAVRAS_DE_GRUPO:
        return "CROP_GRUPO:" + n.upper().replace(" ", "_")
    # 2. a chave do leitor de rotulos — uma so; duas = ambiguo.
    chaves = sorted({k for k, rx in XM._RX_CULTURA_ROTULO if rx.search(n)})
    forma = _forma(n)
    no_boletim = forma in CULTURAS_BOLETIM or n in CULTURAS_BOLETIM
    if len(chaves) > 1:
        return None
    if len(chaves) == 1:
        k = chaves[0]
        if k not in XM.GRUPOS_DO_LEITOR:
            return "CROP:" + k
        # chave que junta varias culturas: a identidade leva a ESPECIE escrita (so do vocabulario do boletim)
        return ("CROP:%s/%s" % (k, forma.upper().replace(" ", "_"))) if no_boletim else None
    # 3. cultura que so o boletim conhece (carciofo, nocciolo...): o termo do boletim e o codigo.
    return ("CROP:" + forma.upper().replace(" ", "_")) if no_boletim else None


# ── PRAGA ────────────────────────────────────────────────────────────────────
def praga(nome):
    """`nome` -> `PEST:<chave do leitor>` ou None. Sinonimos so pela lista MESMO_PROBLEMA."""
    n = dobrar(nome)
    if not n or n == dobrar(NAO_SEI):
        return None
    n = dobrar(nome_do_problema(n))
    XM = _leitor()
    chaves = sorted({k for k, rx in XM._RX_ALVO if rx.search(n)})
    return ("PEST:" + chaves[0]) if len(chaves) == 1 else None


# ── LUGAR ────────────────────────────────────────────────────────────────────
_PROV = {dobrar(p): "PLACE:IT-PROV:" + dobrar(p).upper().replace(" ", "_") for p in PROVINCIAS}
_REG = {dobrar(r): "PLACE:IT-REG:" + dobrar(r).upper().replace(" ", "_") for r in REGIOES}
_PAIS = {"italia": "PLACE:IT", "italy": "PLACE:IT"}
_NIVEL = {"PROV": 0, "REG": 1, "PAIS": 2}


def lugar(texto):
    """O lugar que o TEXTO sustentou, no nivel MAIS FINO (D112). None = NAO SEI.

    Pedacos separados por «;» ou «,». Dois lugares diferentes no nivel mais fino = ambiguo = None.
    A hierarquia (Lecce dentro de Puglia) serve para VISTA, nunca para chave: aqui nada sobe de nivel.
    """
    achados = []
    for pedaco in re.split(r"[;,]", str(texto or "")):
        p = dobrar(pedaco)
        if p in _PROV:
            achados.append(("PROV", _PROV[p]))
        elif p in _REG:
            achados.append(("REG", _REG[p]))
        elif p in _PAIS:
            achados.append(("PAIS", _PAIS[p]))
    if not achados:
        return None
    fino = min(_NIVEL[n] for n, _ in achados)
    codigos = sorted({c for n, c in achados if _NIVEL[n] == fino})
    return codigos[0] if len(codigos) == 1 else None


# ── A TABELA, a versao e a impressao ─────────────────────────────────────────
def termos() -> dict:
    """{CODIGO: {TIPO, ALIASES, ORIGEM}} — a tabela inteira, derivada das listas do repo."""
    XM = _leitor()
    out = {}

    def por(codigo, tipo, alias, origem):
        if codigo:
            e = out.setdefault(codigo, {"TIPO": tipo, "ALIASES": [], "ORIGEM": origem})
            if alias not in e["ALIASES"]:
                e["ALIASES"].append(alias)
    for c in list(CULTURAS_BOLETIM) + list(FORMAS):
        por(cultura(c), "CULTURA", c, "leis/boletim_do_campo.py + motor/cruzamentos_max.py:CULTURAS_ROTULO")
    for g in XM.PALAVRAS_DE_GRUPO:
        por(cultura(g), "CULTURA_GRUPO", g, "motor/cruzamentos_max.py:PALAVRAS_DE_GRUPO")
    for k, rx in XM.ALVOS_CANON:
        out.setdefault("PEST:" + k, {"TIPO": "PRAGA", "ALIASES": ["re:" + rx], "ORIGEM": "motor/cruzamentos_max.py:ALVOS_CANON"})
    for rx, nome in __import__("boletim_do_campo").MESMO_PROBLEMA:
        cod = praga(nome)
        if cod:
            out[cod]["ALIASES"].append("MESMO_PROBLEMA:" + rx)
    for d, cod in list(_PROV.items()) + list(_REG.items()) + list(_PAIS.items()):
        por(cod, "LUGAR", d, "leis/fato_local.py:PROVINCIAS/REGIOES")
    for e in out.values():
        e["ALIASES"] = sorted(e["ALIASES"])
    return dict(sorted(out.items()))


def impressao() -> str:
    return hashlib.sha256(json.dumps(termos(), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def carimbo() -> str:
    """O que viaja em cada chave: a versao e a impressao curta da tabela que a produziu."""
    return "%s@%s" % (VERSAO, impressao()[:12])


def main() -> int:
    t = termos()
    for cod, e in t.items():
        print("%-44s %-14s %s" % (cod, e["TIPO"], " | ".join(e["ALIASES"][:4])))
    print("%s · %d termos · impressao %s" % (VERSAO, len(t), impressao()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
