#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUANTO ACERVO EXISTE, E EM QUE ESTADO — CENSO SO DE LEITURA.

    python3 provas/o_censo_do_acervo.py

A PERGUNTA
----------
    SE AMANHA SE PUSER A MAQUINA A TRABALHAR,
    QUE TAMANHO TEM A FILA QUE PODE CHEGAR A SALA DE ESPERA?

O QUE ESTA MEDICAO NAO FAZ, E E O QUE A DEFINE
-----------------------------------------------
Nao move nada. Nao promove nada. Nao admite nada. Nao reprocessa nada. Nao
abre corrida nenhuma.

    UM CENSO QUE MEXE NO QUE CONTA JA NAO ESTA A CONTAR.

E NAO INVENTA O QUE NAO CONSEGUE VER. O acervo operacional vive no banco
LIVE, e este ambiente nao tem credenciais dele. Entao o que e do banco sai
`NOT_MEASURED` com o motivo escrito, e o que esta em DISCO conta-se de
verdade.

    MEDIR O DISCO E MEDIR O DISCO.
    CHAMAR-LHE «O ACERVO» SERIA DIZER QUE NAO HA MAIS NADA.
"""
import io
import json
import os
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import retorno_da_coleta as rdc                             # noqa: E402

SAIDA = os.path.join("data", "derivados", "O-CENSO-DO-ACERVO.json")

LIVRO_IT = os.path.join("data", "collection-ledger", "italy",
                        "observations.ndjson")
CORRIDAS_IT = os.path.join("data", "collection-ledger", "italy", "runs.ndjson")
ARMAZEM_EU = os.path.join("data", "raw", "eu-regulatorio")
TEXTO = os.path.join("data", "derivados", "texto")

# Onde o banco LIVE responderia, se houvesse como lhe perguntar.
VARIAVEIS_DO_LIVE = ("SUPABASE_DB_URL", "SUPABASE_URL",
                     "SUPABASE_SERVICE_ROLE_KEY")


def _linhas(rel):
    caminho = os.path.join(RAIZ, rel)
    if not os.path.isfile(caminho):
        return []
    fora = []
    with io.open(caminho, encoding="utf-8", errors="replace") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            try:
                fora.append(json.loads(linha))
            except json.JSONDecodeError:
                fora.append({"_ILEGIVEL": True})
    return fora


def o_livro_italiano():
    """As observacoes que o coletor italiano ja preservou, por estado.

    ⚠️ ESTE LIVRO NAO E `raw_asset`. E o registo append-only do coletor, e as
    observacoes dele so viram `raw_asset` quando passam pelo ingresso
    canonico. Contar as duas coisas juntas daria um numero que nao existe em
    sitio nenhum.

        OBSERVADO PELO COLETOR != PRESERVADO PELA COLLECTION.
    """
    obs = _linhas(LIVRO_IT)
    corridas = _linhas(CORRIDAS_IT)
    com_bytes = [o for o in obs if o.get("RAW_PATH")]
    existe = 0
    for o in com_bytes:
        p = str(o.get("RAW_PATH") or "").lstrip("./")
        if p and os.path.isfile(os.path.join(RAIZ, p)):
            existe += 1
    fontes = Counter(str(o.get("SOURCE_ID") or "NAO SEI") for o in obs)
    return OrderedDict([
        ("OBSERVACOES_NO_LIVRO", len(obs)),
        ("ILEGIVEIS", sum(1 for o in obs if o.get("_ILEGIVEL"))),
        ("COM_CAMINHO_DE_BYTES", len(com_bytes)),
        ("COM_BYTES_MESMO_NA_ARVORE", existe),
        # ⚠️ A DIFERENCA NAO E ERRO: e o que esta declarado e nao esta ca.
        # `AUSENTE != ERRO` — a lei do payload ja o diz, e vale aqui.
        ("DECLARADOS_SEM_BYTES", len(com_bytes) - existe),
        ("CORRIDAS_NO_LIVRO", len(corridas)),
        ("POR_FONTE", OrderedDict(sorted(fontes.items()))),
    ])


def os_documentos_regulatorios():
    caminho = os.path.join(RAIZ, ARMAZEM_EU)
    if not os.path.isdir(caminho):
        return OrderedDict([("PDFS", 0), ("BONS", 0), ("TRUNCADOS", 0)])
    bons, maus = 0, 0
    for nome in sorted(os.listdir(caminho)):
        if not nome.endswith(".pdf"):
            continue
        with io.open(os.path.join(caminho, nome), "rb") as fh:
            cabeca = fh.read(4)
        if cabeca == b"%PDF":
            bons += 1
        else:
            maus += 1
    return OrderedDict([("PDFS", bons + maus), ("BONS", bons),
                        ("TRUNCADOS", maus)])


def as_colheitas_declaradas():
    """Envelopes em disco, e o que cada um declara.

    ⚠️ UM ENVELOPE EM DISCO NAO E UMA CORRIDA NO BANCO. Ele diz o que um
    executor produziu; se alguem leu isso, e outra pergunta — e e a do banco,
    que aqui nao se consegue fazer.
    """
    # ⚠️ O ATALHO DE SAIDA DEVOLVIA OUTRA FORMA, e isso rebentou a medicao.
    # Sem a pasta, devolvia `{"ENVELOPES": 0}` — sem as outras chaves — e quem
    # lia o resultado ia buscar uma que nao existia.
    #
    #     UMA FUNCAO QUE MUDA DE FORMA CONSOANTE O MUNDO
    #     OBRIGA QUEM A CHAMA A ADIVINHAR EM QUE MUNDO ESTA.
    #
    # Zero envelopes e uma RESPOSTA, e tem a mesma forma de qualquer outra.
    base = os.path.join(RAIZ, "data", "colheita")
    envelopes, unidades, por_estado = 0, 0, Counter()
    maus = []
    for pasta, _d, ficheiros in (os.walk(base) if os.path.isdir(base) else []):
        for nome in ficheiros:
            if not nome.startswith("RETORNO"):
                continue
            envelopes += 1
            caminho = os.path.join(pasta, nome)
            try:
                with io.open(caminho, encoding="utf-8") as fh:
                    env = json.load(fh)
            except Exception:                                # noqa: BLE001
                maus.append(os.path.relpath(caminho, RAIZ))
                continue
            por_estado[str(env.get("ESTADO") or "SEM_ESTADO")] += 1
            unidades += len(env.get("COLHEITA") or [])
            if rdc.conferir(env, RAIZ):
                maus.append(os.path.relpath(caminho, RAIZ))
    return OrderedDict([
        ("ENVELOPES", envelopes),
        ("UNIDADES_DECLARADAS_COMO_COLHEITA", unidades),
        ("POR_ESTADO", OrderedDict(sorted(por_estado.items()))),
        ("FORA_DO_CONTRATO", maus),
    ])


def o_que_o_banco_diria():
    """O que so o banco responde — e por que nao respondeu.

    ⚠️ `NOT_MEASURED` COM MOTIVO NAO E O MESMO QUE ZERO, e a diferenca custa
    uma decisao: zero manda coletar tudo; nao-medido manda ir ver.
    """
    tem = [v for v in VARIAVEIS_DO_LIVE if os.environ.get(v)]
    estados = ("RAW_ONLY", "RAW_WITH_STORAGE", "DERIVED", "STRUCTURED",
               "ADMISSION_DECIDED", "READY", "WAITING_ROOM", "ERROR",
               "UNKNOWN", "LEGACY_OUT_OF_FLOW", "REPROCESSABLE")
    return OrderedDict([
        ("MEDIDO", "NO"),
        ("PORQUE", "este ambiente nao tem credenciais do LIVE: %s ausentes"
                   % ", ".join(VARIAVEIS_DO_LIVE) if not tem else
                   "credenciais presentes mas a leitura nao foi feita"),
        ("VARIAVEIS_PRESENTES", tem),
        ("POR_ESTADO", OrderedDict((e, "NOT_MEASURED") for e in estados)),
        ("COMO_MEDIR",
         "com `SUPABASE_DB_URL` definida, contar por estado em `raw_asset`, "
         "`storage_object`, `derived_artifact`, `documento_estruturado` e no "
         "livro de decisoes — tudo com SELECT, sem escrever nada"),
    ])


def main():
    art = OrderedDict([
        ("PERGUNTA", "que tamanho tem a fila que pode chegar a Sala de "
                     "Espera?"),
        ("SO_LEITURA", "YES — nada foi movido, promovido, admitido ou "
                       "reprocessado"),
        ("EM_DISCO", OrderedDict([
            ("LIVRO_DO_COLETOR_ITALIANO", o_livro_italiano()),
            ("DOCUMENTOS_REGULATORIOS_EU", os_documentos_regulatorios()),
            ("COLHEITAS_DECLARADAS", as_colheitas_declaradas()),
            ("TEXTOS_JA_EXTRAIDOS",
             len([f for f in os.listdir(os.path.join(RAIZ, TEXTO))])
             if os.path.isdir(os.path.join(RAIZ, TEXTO)) else 0),
        ])),
        ("NO_BANCO_LIVE", o_que_o_banco_diria()),
        ("GENERATED_BY", "provas/o_censo_do_acervo.py"),
    ])

    livro = art["EM_DISCO"]["LIVRO_DO_COLETOR_ITALIANO"]
    print("\n  O CENSO DO ACERVO — so leitura")
    print("  " + "─" * 66)
    print("  LIVRO DO COLETOR ITALIANO")
    print("    observacoes no livro        %d" % livro["OBSERVACOES_NO_LIVRO"])
    print("    com caminho de bytes        %d" % livro["COM_CAMINHO_DE_BYTES"])
    print("    com bytes mesmo na arvore   %d"
          % livro["COM_BYTES_MESMO_NA_ARVORE"])
    print("    declarados e sem bytes      %d" % livro["DECLARADOS_SEM_BYTES"])
    print("    corridas no livro           %d" % livro["CORRIDAS_NO_LIVRO"])
    print("    por fonte                   %s"
          % dict(list(livro["POR_FONTE"].items())[:6]))
    reg = art["EM_DISCO"]["DOCUMENTOS_REGULATORIOS_EU"]
    print("\n  DOCUMENTOS REGULATORIOS (EU-T4-001)")
    print("    PDF preservados             %d (bons=%d truncados=%d)"
          % (reg["PDFS"], reg["BONS"], reg["TRUNCADOS"]))
    col = art["EM_DISCO"]["COLHEITAS_DECLARADAS"]
    print("\n  COLHEITAS DECLARADAS")
    print("    envelopes em disco          %d" % col["ENVELOPES"])
    print("    unidades declaradas         %d"
          % col["UNIDADES_DECLARADAS_COMO_COLHEITA"])
    print("    fora do contrato            %d" % len(col["FORA_DO_CONTRATO"]))
    print("\n  TEXTOS JA EXTRAIDOS           %d"
          % art["EM_DISCO"]["TEXTOS_JA_EXTRAIDOS"])
    print("\n  NO BANCO LIVE                 %s"
          % art["NO_BANCO_LIVE"]["MEDIDO"])
    print("    %s" % art["NO_BANCO_LIVE"]["PORQUE"])

    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with io.open(caminho, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(art, ensure_ascii=False, indent=2) + "\n")
    print("\n  escrito: %s\n" % SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
