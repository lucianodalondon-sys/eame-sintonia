#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O VALIDADOR do pote v2 unico — POTE_INTELLIGENCE_CASCO/v2 (missao POTE-V2-UNICO).

    python3 pacote/validar_pote_v2.py <pote.json | italia-portale/client/sintonia-pote.js>

Duas perguntas, nesta ordem, e o pote so passa se as duas disserem que sim:

    1. FORMA  — o pote tem a forma do schema
                (docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json)?
    2. LEI    — `conferir_pote` (pacote/pote_intelligence_casco.py, o dono) aprova?

O schema e lido com um verificador PROPRIO e pequeno (type, const, enum,
required, properties, additionalProperties-como-schema, items, minItems,
minLength, not, $ref local): o repositorio nao traz a biblioteca jsonschema, e
este ficheiro nao a pede. Uma palavra do schema que ele nao conhece reprova —
nunca e ignorada em silencio.

Sai 0 = PASSA · 1 = REPROVA · 2 = uso errado / ficheiro ilegivel.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import pote_intelligence_casco as P  # noqa: E402

SCHEMA = Path(os.path.dirname(HERE)) / "docs" / "intelligence" / "pote-v2" / "POTE_INTELLIGENCE_CASCO-v2.schema.json"
#: As palavras do schema que este verificador sabe ler. Outra qualquer = reprova.
PALAVRAS = {"$schema", "$id", "$defs", "$ref", "title", "description", "type", "const", "enum", "required",
            "properties", "additionalProperties", "items", "minItems", "minLength", "not"}
_TIPOS = {"object": dict, "array": list, "string": str, "boolean": bool}


def carregar_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _tipo_ok(v, t) -> bool:
    if t == "boolean":
        return isinstance(v, bool)
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    return isinstance(v, _TIPOS[t])


def forma(dado, schema: dict | None = None, raiz: dict | None = None, onde: str = "$") -> list:
    """As violacoes de FORMA. Lista vazia = o pote tem a forma do schema."""
    schema = carregar_schema() if schema is None else schema
    raiz = schema if raiz is None else raiz
    v = []
    desconhecidas = set(schema) - PALAVRAS
    if desconhecidas:
        return [f"{onde}: o schema usa palavra que este verificador nao le: {sorted(desconhecidas)}"]
    if "$ref" in schema:
        alvo = raiz
        for parte in schema["$ref"].lstrip("#/").split("/"):
            alvo = alvo[parte]
        return forma(dado, alvo, raiz, onde)
    if "type" in schema and not _tipo_ok(dado, schema["type"]):
        return [f"{onde}: devia ser {schema['type']}"]
    if "const" in schema and dado != schema["const"]:
        v.append(f"{onde}: devia ser {schema['const']!r}, e {dado!r}")
    if "enum" in schema and dado not in schema["enum"]:
        v.append(f"{onde}: {dado!r} fora de {schema['enum']}")
    if "not" in schema and not forma(dado, schema["not"], raiz, onde):
        v.append(f"{onde}: {dado!r} e o que o schema proibe")
    if "minLength" in schema and isinstance(dado, str) and len(dado) < schema["minLength"]:
        v.append(f"{onde}: texto vazio")
    if isinstance(dado, dict):
        for k in schema.get("required", []):
            if k not in dado:
                v.append(f"{onde}: falta {k}")
        props = schema.get("properties", {})
        for k, sub in props.items():
            if k in dado:
                v += forma(dado[k], sub, raiz, f"{onde}.{k}")
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict):
            for k in dado:
                if k not in props:
                    v += forma(dado[k], extra, raiz, f"{onde}.{k}")
    if isinstance(dado, list):
        if len(dado) < schema.get("minItems", 0):
            v.append(f"{onde}: precisa de pelo menos {schema['minItems']}")
        if "items" in schema:
            for i, x in enumerate(dado):
                v += forma(x, schema["items"], raiz, f"{onde}[{i}]")
    return v


def validar(pote) -> list:
    """FORMA + LEI. Lista vazia = passa."""
    v = forma(pote)
    return v + [f"LEI: {x}" for x in P.conferir_pote(pote)]


def ler_ficheiro(caminho: Path):
    """Um .json, ou o .js que o casco carrega (`window.SINTONIA_POTE = {...};`)."""
    texto = caminho.read_text(encoding="utf-8")
    if caminho.suffix == ".js":
        marca = "window." + P.NOME_DO_GLOBAL + " = "
        i = texto.find(marca)
        if i < 0:
            raise ValueError(f"{caminho} nao define {marca.strip()}")
        texto = texto[i + len(marca):].rstrip().rstrip(";")
    return json.loads(texto)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 pacote/validar_pote_v2.py <pote.json|sintonia-pote.js>")
        return 2
    try:
        pote = ler_ficheiro(Path(argv[0]))
    except (OSError, ValueError) as e:
        print(f"ILEGIVEL: {e}")
        return 2
    v = validar(pote)
    for x in v[:60]:
        print("  -", x)
    if v:
        print(f"REPROVA · {len(v)} violacao(oes) · {P.CONTRATO}")
        return 1
    n = sum(len(e["OBJETOS"]) for e in pote["COMPARTIMENTOS"].values())
    print(f"PASSA · {P.CONTRATO} · corrida {pote['INTELLIGENCE_RUN_ID']} · {n} objetos · "
          f"{len(pote['RECUSADOS'])} recusados · compatibilidade lida: {len(pote['LEITURA_DE_COMPATIBILIDADE'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
