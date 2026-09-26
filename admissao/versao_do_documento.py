#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTEÚDO DESTE DOCUMENTO MUDOU DE VERDADE? — D79 (26/09).

A Sala guarda UM documento lógico por (source_id, document_key, universo). Quando
chega outra observação do mesmo documento, esta função responde se ela é uma
VERSÃO NOVA (entra no caderno `sala_de_espera_versao`, migração 036) ou a mesma
coisa outra vez (não entra nada).

    BYTES IGUAIS NÃO CRIAM VERSÃO.
    TEXTO COMPARA-SE COM O MESMO EXTRATOR — NUNCA ENTRE EXTRATORES DIFERENTES.
    SE NÃO DÁ PARA COMPARAR, É NÃO SEI: NÃO CRIA VERSÃO, FICA NO RECIBO.

O «extrator» é a receita inteira do derivado: `producer` + `producer_version` +
`parameters_hash`. Medido na Sala real (26/09): o derivado 66 e o 1060 da
IT-T9-011 dizem os dois `texto-de-html` versão 1, mas a receita mudou
(parâmetros vazios → `TEXT_OWNER = coleta/texto_fonte.py::limpar`) sem subir a
versão. Comparar só pela versão chamaria «versão nova» a uma troca de receita.

Re-extrair (extrator mudou) precisa de duas coisas que a Sala não tem e não
copia: os BYTES do RAW anterior (`armazem.ler(storage_path)`) e o EXTRATOR que
fez o derivado novo (`extratores[producer](bytes, media_type)`, devolvendo
`(texto, producer_version, parameters_hash)`). Quem chama `pousar` e os tem,
passa-os. Sem eles, a resposta é NAO_SEI — declarada, nunca adivinhada.
"""
import hashlib

IGUAL = "IGUAL"
MUDOU = "MUDOU"
NAO_SEI = "NAO_SEI"

MESMO_EXTRATOR = "MESMO_EXTRATOR"
REEXTRAIDO_DO_RAW = "REEXTRAIDO_DO_RAW"

#: As colunas que se leem de cada derivado (e do RAW que é o pai dele).
_COLUNAS = ("id", "producer", "producer_version", "parameters_hash", "sha256",
            "parent_sha256", "storage_path_raw", "media_type_raw")


def _derivado_id(item_id):
    """`derived:<n>` → n. Qualquer outra forma → None (não se inventa)."""
    s = str(item_id or "")
    if not s.startswith("derived:"):
        return None
    try:
        return int(s[len("derived:"):])
    except ValueError:
        return None


def ler_derivados(consultar, sep, ids):
    """{id: {coluna: valor}} para os derivados pedidos. `consultar` é o da Sala."""
    ids = sorted({i for i in ids if i is not None})
    if not ids:
        return {}
    linhas = consultar(
        "select d.id, d.producer, d.producer_version, d.parameters_hash, d.sha256, "
        "d.parent_sha256, r.storage_path, r.media_type "
        "from public.derived_artifact d join public.raw_asset r on r.id = d.raw_asset_id "
        "where d.id in (%s)" % ", ".join(str(int(i)) for i in ids))
    out = {}
    for l in linhas:
        c = dict(zip(_COLUNAS, l.split(sep)))
        out[int(c["id"])] = c
    return out


def decidir(anterior, novo, armazem=None, extratores=None):
    """Compara o derivado ANTERIOR (a última versão na Sala) com o NOVO.

    `anterior` e `novo` são linhas de `ler_derivados` (ou None se não existem).
    Devolve `{"ESTADO": IGUAL|MUDOU|NAO_SEI, "COMO": ..., "MOTIVO": ...}`.
    """
    if anterior is None or novo is None:
        return {"ESTADO": NAO_SEI, "COMO": None,
                "MOTIVO": "derivado anterior ou novo nao encontrado em derived_artifact"}
    if anterior["id"] == novo["id"]:
        return {"ESTADO": IGUAL, "COMO": None, "MOTIVO": "o mesmo derivado"}
    if anterior["parent_sha256"] == novo["parent_sha256"]:
        return {"ESTADO": IGUAL, "COMO": None, "MOTIVO": "bytes do RAW iguais"}
    receita = ("producer", "producer_version", "parameters_hash")
    if all(anterior[k] == novo[k] for k in receita):
        if anterior["sha256"] == novo["sha256"]:
            return {"ESTADO": IGUAL, "COMO": MESMO_EXTRATOR,
                    "MOTIVO": "bytes do RAW mudaram, texto igual com o mesmo extrator"}
        return {"ESTADO": MUDOU, "COMO": MESMO_EXTRATOR,
                "MOTIVO": "texto diferente com o mesmo extrator"}
    # ── o extrator mudou: re-extrair a versão anterior com o extrator NOVO ──
    extrator = (extratores or {}).get(novo["producer"])
    if extrator is None:
        return {"ESTADO": NAO_SEI, "COMO": None,
                "MOTIVO": "extrator mudou (%s/%s/%s -> %s/%s/%s) e nao ha extrator %r "
                          "para re-extrair" % (anterior["producer"], anterior["producer_version"],
                                               anterior["parameters_hash"][:8], novo["producer"],
                                               novo["producer_version"],
                                               novo["parameters_hash"][:8], novo["producer"])}
    if armazem is None:
        return {"ESTADO": NAO_SEI, "COMO": None,
                "MOTIVO": "extrator mudou e nao ha armazem para ler o RAW anterior"}
    try:
        dados = armazem.ler(anterior["storage_path_raw"])
    except Exception as ex:                      # o RAW pode nao estar preservado
        return {"ESTADO": NAO_SEI, "COMO": None,
                "MOTIVO": "RAW anterior ilegivel no armazem: %s" % str(ex)[:120]}
    if not dados:
        return {"ESTADO": NAO_SEI, "COMO": None, "MOTIVO": "RAW anterior vazio no armazem"}
    try:
        texto, versao, parametros_hash = extrator(dados, anterior["media_type_raw"])
    except Exception as ex:
        return {"ESTADO": NAO_SEI, "COMO": None,
                "MOTIVO": "re-extracao falhou: %s" % str(ex)[:120]}
    if (versao, parametros_hash) != (novo["producer_version"], novo["parameters_hash"]):
        return {"ESTADO": NAO_SEI, "COMO": None,
                "MOTIVO": "o extrator disponivel nao e o que fez o derivado novo "
                          "(%s/%s vs %s/%s)" % (versao, str(parametros_hash)[:8],
                                                novo["producer_version"],
                                                novo["parameters_hash"][:8])}
    if texto is None:
        return {"ESTADO": NAO_SEI, "COMO": None, "MOTIVO": "re-extracao nao devolveu texto"}
    sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    if sha == novo["sha256"]:
        return {"ESTADO": IGUAL, "COMO": REEXTRAIDO_DO_RAW,
                "MOTIVO": "re-extraido com o extrator novo: texto igual"}
    return {"ESTADO": MUDOU, "COMO": REEXTRAIDO_DO_RAW,
            "MOTIVO": "re-extraido com o extrator novo: texto diferente"}
