#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS EDICOES DO REGISTRO — duas edicoes do CSV do Ministero, e o que mudou entre elas.

    python3 coleta/it/edicoes_do_registro.py                       # as duas ultimas do livro
    python3 coleta/it/edicoes_do_registro.py --a=<csv> --b=<csv>   # duas edicoes nomeadas
    ... --pousar     emite os EVENTO_REGULATORIO pela porta e pousa-os na Sala

D116 + D117.1 (dono, 27/09). O registo oficial `IT-T4-001` (PROD_FTS_6_AAAAMMDD.csv)
e BIBLIOTECA DE REFERENCIA versionada: cada edicao guarda-se sem sobrescrever, a
diferenca entre duas edicoes calcula-se PRODUTO A PRODUTO, e cada mudanca
comprovada vira EVENTO REGULATORIO datado com a data que a fonte provar.

O QUE ESTA PECA RESOLVE, MEDIDO
-------------------------------
`docs/operacao/PRIMEIRA-COLETA-CONTROLADA-ITALIA-V1.md` (CW-01): «nenhum
derivador abre CSV — e capacidade ausente». O contrato de IT-T4-001 declara DUAS
granularidades (o ficheiro e a linha). Esta peca e a da LINHA: a unidade que
atravessa para a Intelligence nao e o CSV de 4,6 MB, e a mudanca de UM registo.

NADA AQUI E INVENTADO — A REGUA JA EXISTIA
------------------------------------------
`docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md` (29/08, caso ES-01717) ja dizia o
vocabulario, os campos obrigatorios e o portao de versao. Esta peca aplica-a ao
registo italiano, e nao cria tipo novo:

    CHANGE_TYPE   NEW_REGISTRATION · REGISTRATION_LEFT_THE_LIST · STATUS_CHANGE
                  HOLDER_CHANGE · COMPOSITION_CHANGE · DATE_CHANGE
                  REFERENCE_NAME_CHANGE · UNKNOWN_CHANGE
    PORTAO        `medidas/source_health.py::version_state` — so NEW_VERSION_CHANGED
                  autoriza emitir; BASELINE nunca e «nada mudou».

Os nomes que o dono pediu (NUMERO_REGISTRAZIONE, CAMPO, ANTES, DEPOIS, EDICAO)
viajam AO LADO dos da regua (REGISTRATION_ID, BEFORE, AFTER, SOURCE_VERSION_B).
Sao a mesma coisa: nenhum dos dois se calcula do outro, os dois copiam a linha.

O QUE UMA MUDANCA PROVA — E O QUE NAO PROVA
-------------------------------------------
    registo que SAIU do ficheiro      != revogacao. A revogacao prova-se pelo
                                        campo `stato_amministrativo`, e so por ele.
                                        Sair do ficheiro e REGISTRATION_LEFT_THE_LIST,
                                        com VERDICT UNRESOLVED.
    a data da mudanca                 = a que a FONTE escreve na linha
                                        (data_registrazione, data_decreto_revoca,
                                        data_decorrenza_revoca). Quando a linha
                                        nao data a mudanca, FACT_TIME = NAO SEI —
                                        a data da EDICAO e PUBLISHED_AT, nunca fato.
    cultura x alvo                    NAO ESTA no CSV (Atlas, IT-T4-001: «este
                                        arquivo nao traz cultura nem alvo»). Todo
                                        evento escreve CULTURA_ALVO = NAO SEI. Ler
                                        cultura do NOME do produto e proibido (D116).
    diferenca so de grafia            (pontuacao no titular, espacos/ordem na
                                        composicao) = UNKNOWN_CHANGE, vai a revisao
                                        e NAO vira evento (regua §6, HOLDER/COMPOSITION).

A EDICAO ANTIGA NUNCA SE APAGA
------------------------------
O bruto de cada edicao ja e imutavel no armazem (`coleta/italy_pilot_collect.mjs::
guardarRaw` nao reescreve ficheiro existente). A biblioteca das edicoes NAO e um
segundo indice: le-se do livro canonico (`observations.ndjson`), uma entrada por
DOCUMENT_ID. O que esta peca escreve — o diff de um par — escreve-se em criacao
exclusiva: o mesmo par com o mesmo conteudo e JA_ESTAVA; com conteudo diferente
levanta `DiffEmConflito` e nao toca no que la estava.

O CAMINHO ATE A SALA E O CANONICO
---------------------------------
Cada evento vira um item FATO (`fact_id`/`subject`/`predicate`) e passa pela porta
de sempre: `admissao.decidir(item, "T4")` -> `admissao.pronto_para_inteligencia` ->
`sala_de_espera.pousar`. Esta peca nao tem porta propria nem sala propria.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import source_health as sh  # noqa: E402 — o portao de versao da regua de change event

SOURCE_ID = "IT-T4-001"
NAO_SEI = "NAO SEI"
UNIVERSO = "T4"
CONTRATO = "EDICOES_DO_REGISTRO/v1"
REGUA = "docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md"

#: As colunas que o contrato de IT-T4-001 exige (`EXPECTED_COLUMNS`). Falta uma = FAILED.
COLUNAS_OBRIGATORIAS = ("num_registrazione", "denominazione_prodotto", "ragione_sociale",
                        "data_registrazione", "data_scadenza_autorizzazione", "sostanze_attive")
CHAVE = "num_registrazione"
NOME_DA_EDICAO = re.compile(r"PROD_FTS_6_(\d{4})(\d{2})(\d{2})\.csv$")

# O campo -> o CHANGE_TYPE da regua. O que nao esta aqui e UNKNOWN_CHANGE.
TIPO_DO_CAMPO = {
    "denominazione_prodotto": "REFERENCE_NAME_CHANGE",
    "ragione_sociale": "HOLDER_CHANGE",
    "sostanze_attive": "COMPOSITION_CHANGE",
    "contenuto_per_100g_di_prodotto": "COMPOSITION_CHANGE",
    "stato_amministrativo": "STATUS_CHANGE",
    "data_registrazione": "DATE_CHANGE",
    "data_scadenza_autorizzazione": "DATE_CHANGE",
    "data_decreto_revoca": "DATE_CHANGE",
    "data_decorrenza_revoca": "DATE_CHANGE",
}
#: Os tipos que viram EVENTO_REGULATORIO. UNKNOWN_CHANGE nunca (regua §5.1).
TIPOS_QUE_EMITEM = ("NEW_REGISTRATION", "REGISTRATION_LEFT_THE_LIST", "STATUS_CHANGE",
                    "HOLDER_CHANGE", "COMPOSITION_CHANGE", "DATE_CHANGE",
                    "REFERENCE_NAME_CHANGE")
CULTURA_ALVO = ("NAO SEI — o CSV do registro nao traz cultura nem alvo; so a bula "
                "(etichetta) os traz (D117.1). Nunca se infere do nome do produto (D116).")


class EdicaoInvalida(Exception):
    """A edicao existe e nao serve: coluna obrigatoria em falta, chave repetida."""


class DiffEmConflito(Exception):
    """O mesmo par de edicoes ja tem um diff guardado com OUTRO conteudo.

    Nada foi escrito. Sobrescrever apagaria a historia de uma comparacao que ja
    aconteceu — a mesma lei da Sala: UMA RUN_ID NAO CONTA DUAS HISTORIAS.
    """


# ── LER UMA EDICAO ─────────────────────────────────────────────────────────
def edicao_do_nome(nome: str):
    """`PROD_FTS_6_20260914.csv` -> `2026-09-14`. Sem o padrao -> None (nunca um palpite)."""
    m = NOME_DA_EDICAO.search(os.path.basename(nome or ""))
    return "%s-%s-%s" % m.groups() if m else None


def _sha256(caminho: str) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_edicao(caminho: str) -> dict:
    """`{num_registrazione: linha}` — falha fechada, como o contrato manda."""
    with open(caminho, "rb") as f:
        bruto = f.read()
    try:
        texto = bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = bruto.decode("latin-1")
    leitor = csv.DictReader(io.StringIO(texto, newline=""), delimiter=";")
    faltam = [c for c in COLUNAS_OBRIGATORIAS if c not in (leitor.fieldnames or [])]
    if faltam:
        raise EdicaoInvalida("%s: faltam colunas obrigatorias %s — FAILED (contrato IT-T4-001)"
                             % (os.path.basename(caminho), faltam))
    linhas = {}
    for n, l in enumerate(leitor, start=2):
        chave = (l.get(CHAVE) or "").strip()
        if not chave:
            raise EdicaoInvalida("%s: linha %d sem %s" % (os.path.basename(caminho), n, CHAVE))
        if chave in linhas:
            raise EdicaoInvalida("%s: %s %s repetido — a chave deixou de identificar"
                                 % (os.path.basename(caminho), CHAVE, chave))
        linhas[chave] = {k: (v or "").strip() for k, v in l.items() if k is not None}
    return linhas


def versao(caminho: str, edicao: str = None, captured_at: str = None) -> dict:
    """A ponta de uma comparacao, nos campos que a regua exige (arquivo + data + SHA-256)."""
    return {"ARQUIVO": os.path.basename(caminho),
            "CAMINHO": os.path.relpath(caminho, RAIZ) if os.path.isabs(caminho) else caminho,
            "VERSION_DATE": edicao or edicao_do_nome(caminho) or NAO_SEI,
            "SHA256": _sha256(caminho),
            "CAPTURED_AT": captured_at or NAO_SEI}


# ── NORMALIZACOES QUE A REGUA MANDA FAZER ANTES DE COMPARAR ───────────────
def _titular_normalizado(v: str) -> str:
    """HOLDER_CHANGE: «exigir que a diferenca nao seja so pontuacao» (regua §6)."""
    return re.sub(r"[^0-9A-Z]+", "", (v or "").upper())


def _composicao_normalizada(v: str) -> str:
    """COMPOSITION_CHANGE: «normalizar espacos e ordenar componentes» (regua §6)."""
    partes = [re.sub(r"\s+", " ", p).strip().upper() for p in re.split(r"\+|;", v or "")]
    return " + ".join(sorted(p for p in partes if p))


NORMALIZA = {"ragione_sociale": _titular_normalizado,
             "sostanze_attive": _composicao_normalizada}


def data_iso(v: str):
    """`15/09/2026` -> `2026-09-15`. `-`, vazio ou ilegivel -> None."""
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", (v or "").strip())
    return "%s-%s-%s" % (m.group(3), m.group(2), m.group(1)) if m else None


# ── A DATA QUE A FONTE PROVA ───────────────────────────────────────────────
def _tempo_do_fato(tipo: str, campo: str, linha_nova: dict):
    """(FACT_TIME, basis). Nunca a data da edicao: essa e PUBLISHED_AT."""
    if tipo == "NEW_REGISTRATION":
        d = data_iso(linha_nova.get("data_registrazione"))
        if d:
            return d, "data_registrazione da propria linha, na edicao nova"
    if tipo == "STATUS_CHANGE" and (linha_nova.get("stato_amministrativo") or "").lower().startswith("revoc"):
        for c in ("data_decreto_revoca", "data_decorrenza_revoca"):
            d = data_iso(linha_nova.get(c))
            if d:
                return d, "%s da propria linha, na edicao nova" % c
    return None, ("a linha nao data esta mudanca: sabe-se so que ocorreu entre as "
                  "duas edicoes (NAO SEI; a data da edicao e PUBLISHED_AT, nao fato)")


def _mudanca(num, campo, antes, depois, tipo, a, b, linha_nova, veredito, nota=None):
    ft, basis = _tempo_do_fato(tipo, campo, linha_nova or {})
    m = {
        # os nomes do pedido do dono
        "NUMERO_REGISTRAZIONE": num, "CAMPO": campo, "ANTES": antes, "DEPOIS": depois,
        "EDICAO": b["VERSION_DATE"], "EDICAO_ANTERIOR": a["VERSION_DATE"],
        # os nomes da regua de change event (§3)
        "ENTITY": "REGISTRATION", "REGISTRATION_ID": num, "CHANGE_TYPE": tipo,
        "BEFORE": antes, "AFTER": depois,
        "SOURCE_VERSION_A": {k: a[k] for k in ("ARQUIVO", "VERSION_DATE", "SHA256")},
        "SOURCE_VERSION_B": {k: b[k] for k in ("ARQUIVO", "VERSION_DATE", "SHA256")},
        "VERDICT": veredito,
        "EMITE_EVENTO": tipo in TIPOS_QUE_EMITEM,
        "FACT_TIME": ft or NAO_SEI, "FACT_TIME_BASIS": basis,
        "PRODUTO": (linha_nova or {}).get("denominazione_prodotto") or NAO_SEI,
        "TITULAR": (linha_nova or {}).get("ragione_sociale") or NAO_SEI,
        "CULTURA_ALVO": CULTURA_ALVO,
    }
    if tipo == "STATUS_CHANGE" and (depois or "").lower().startswith("revoc"):
        m["SUBTIPO"] = "REVOGACAO"
        m["MOTIVO_DA_REVOGACAO"] = (linha_nova.get("motivo_della revoca") or NAO_SEI)
        m["DATA_DECORRENZA_REVOCA"] = data_iso(linha_nova.get("data_decorrenza_revoca")) or NAO_SEI
    if campo == "data_scadenza_autorizzazione":
        m["SUBTIPO"] = "VENCIMENTO_ALTERADO"
    if nota:
        m["NOTA"] = nota
    return m


# ── O DIFF ─────────────────────────────────────────────────────────────────
def comparar(caminho_a: str, caminho_b: str, *, captured_a=None, captured_b=None,
             observed_date=None) -> dict:
    """Duas edicoes -> `{ESTADO_DA_VERSAO, MUDANCAS[], ...}`. A mais antiga primeiro."""
    a = versao(caminho_a, captured_at=captured_a)
    b = versao(caminho_b, captured_at=captured_b)
    if NAO_SEI not in (a["VERSION_DATE"], b["VERSION_DATE"]) and a["VERSION_DATE"] > b["VERSION_DATE"]:
        raise ValueError("ordem trocada: %s e mais nova que %s" % (a["VERSION_DATE"], b["VERSION_DATE"]))
    estado = sh.version_state(fetch_ok=True, current_hash=b["SHA256"], previous_hash=a["SHA256"],
                              current_version=b["VERSION_DATE"], previous_version=a["VERSION_DATE"])
    fora = {"CONTRATO": CONTRATO, "SOURCE_ID": SOURCE_ID, "REGUA": REGUA,
            "SOURCE_VERSION_A": a, "SOURCE_VERSION_B": b, "ESTADO_DA_VERSAO": estado,
            "OBSERVED_DATE": observed_date or NAO_SEI, "MUDANCAS": []}
    if not sh.can_diff(estado):
        fora["PORQUE_SEM_MUDANCAS"] = ("portao de versao: %s nao autoriza emitir evento "
                                       "(nunca se le como «nada mudou»)" % estado)
        return fora
    va, vb = ler_edicao(caminho_a), ler_edicao(caminho_b)
    mud = []
    for num in sorted(set(va) | set(vb)):
        la, lb = va.get(num), vb.get(num)
        if la is None:
            mud.append(_mudanca(num, CHAVE, None, num, "NEW_REGISTRATION", a, b, lb, "CONFIRMED"))
            continue
        if lb is None:
            # Sair do ficheiro NAO e revogacao: o ficheiro inclui os revogados.
            mud.append(_mudanca(num, CHAVE, num, None, "REGISTRATION_LEFT_THE_LIST", a, b, la,
                                "UNRESOLVED",
                                nota="o registo deixou de constar do ficheiro; o proprio "
                                     "ficheiro lista os revogados, por isso sair dele NAO "
                                     "prova revogacao — confirmar antes de ler"))
            continue
        for campo in [c for c in lb if c != CHAVE] + [c for c in la if c not in lb]:
            antes, depois = la.get(campo), lb.get(campo)
            if antes == depois:
                continue
            tipo = TIPO_DO_CAMPO.get(campo, "UNKNOWN_CHANGE")
            norm = NORMALIZA.get(campo)
            if norm and norm(antes) == norm(depois):
                mud.append(_mudanca(num, campo, antes, depois, "UNKNOWN_CHANGE", a, b, lb,
                                    "UNRESOLVED",
                                    nota="difere so na grafia (%s normalizado igual): nao e %s"
                                         % (campo, tipo)))
                continue
            mud.append(_mudanca(num, campo, antes, depois, tipo, a, b, lb,
                                "CONFIRMED" if tipo != "UNKNOWN_CHANGE" else "UNRESOLVED"))
    fora["MUDANCAS"] = mud
    fora["TOTAIS"] = {t: sum(1 for m in mud if m["CHANGE_TYPE"] == t)
                      for t in TIPOS_QUE_EMITEM + ("UNKNOWN_CHANGE",)}
    fora["EVENTOS"] = sum(1 for m in mud if m["EMITE_EVENTO"])
    return fora


# ── GUARDAR SEM SOBRESCREVER ───────────────────────────────────────────────
def guardar_diff(resultado: dict, pasta: str) -> dict:
    """Criacao exclusiva. Igual = JA_ESTAVA. Diferente = DiffEmConflito, nada escrito."""
    a = resultado["SOURCE_VERSION_A"]["VERSION_DATE"]
    b = resultado["SOURCE_VERSION_B"]["VERSION_DATE"]
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "DIFF_%s__%s.json" % (a, b))
    corpo = json.dumps(resultado, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    try:
        fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        with open(caminho, encoding="utf-8") as f:
            if f.read() == corpo:
                return {"ESTADO": "JA_ESTAVA", "CAMINHO": caminho}
        raise DiffEmConflito("%s ja existe com outro conteudo; nada foi escrito" % caminho)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(corpo)
    return {"ESTADO": "GUARDADO", "CAMINHO": caminho}


# ── A BIBLIOTECA DAS EDICOES, LIDA DO LIVRO CANONICO ───────────────────────
def edicoes_do_livro(observacoes, raiz: str = RAIZ) -> list:
    """Uma entrada por DOCUMENT_ID de IT-T4-001, da mais antiga para a mais nova.

    Nenhuma edicao substitui outra: a chave e o DOCUMENT_ID (a data da edicao), e
    nao a fonte. `BYTES_NESTA_ARVORE` diz se o bruto esta aqui — o livro pode
    conhecer uma edicao cujos bytes vivem noutra maquina (NAO SEI, nao «ausente»).
    """
    ed = {}
    for o in observacoes:
        if o.get("SOURCE_ID") != SOURCE_ID or o.get("HEALTH_STATE") != "HEALTHY":
            continue
        doc = o.get("DOCUMENT_ID")
        if not doc:
            continue
        e = ed.setdefault(doc, {"DOCUMENT_ID": doc, "EDICAO": o.get("SOURCE_DATE_ISO") or NAO_SEI,
                                "RAW_SHA256": o.get("RAW_SHA256"), "RAW_PATH": None,
                                "PRIMEIRA_CAPTURA": o.get("CAPTURED_AT"),
                                "ULTIMA_CHECAGEM_OK": o.get("CAPTURED_AT")})
        if o.get("RAW_PATH") and not e["RAW_PATH"]:
            e["RAW_PATH"] = os.path.normpath(o["RAW_PATH"])
        cap = o.get("CAPTURED_AT")
        if cap and cap > (e["ULTIMA_CHECAGEM_OK"] or ""):
            e["ULTIMA_CHECAGEM_OK"] = cap
        if cap and cap < (e["PRIMEIRA_CAPTURA"] or cap):
            e["PRIMEIRA_CAPTURA"] = cap
    fora = sorted(ed.values(), key=lambda e: e["EDICAO"])
    for e in fora:
        e["BYTES_NESTA_ARVORE"] = bool(e["RAW_PATH"]) and os.path.isfile(os.path.join(raiz, e["RAW_PATH"]))
    return fora


# ── O EVENTO, PELA PORTA CANONICA ──────────────────────────────────────────
def item_do_evento(m: dict, observed_date: str = None) -> dict:
    """Uma mudanca que emite -> o item FATO que a porta de admissao julga.

    So COPIA: nenhum campo e calculado de outro que a mudanca nao trouxe.
    """
    fid = "%s:%s:%s:%s:%s>%s" % (SOURCE_ID, m["REGISTRATION_ID"], m["CHANGE_TYPE"],
                                 m["CAMPO"], m["EDICAO_ANTERIOR"], m["EDICAO"])
    # ⚠️ A PRIMEIRA LINHA NAO LEVA VALOR NENHUM, E ISSO E A D116 A MORDER.
    # A porta le a CULTURA do TITULO (a 1.a linha do texto, `admissao.
    # _cultura_fora_da_regua`). Medido nesta missao: com o nome do produto
    # na 1.a linha, `RAME VITE` saia da Sala com `CULTURA = ["vite"]` — cultura
    # inferida do NOME, que e exactamente o proibido. O nome, o titular e os
    # valores vao da 2.a linha para baixo, onde a leitura de cultura nao chega.
    texto = ("Registro dei prodotti fitosanitari (Ministero della Salute), registrazione n. %s: "
             "%s nel campo %s tra le edizioni %s e %s.\n"
             "prodotto %r · titolare %r · prima %r · dopo %r"
             % (m["REGISTRATION_ID"], m["CHANGE_TYPE"], m["CAMPO"], m["EDICAO_ANTERIOR"],
                m["EDICAO"], m["PRODUTO"], m["TITULAR"], m["ANTES"], m["DEPOIS"]))
    item = {k: v for k, v in m.items() if k not in ("FACT_TIME", "FACT_TIME_BASIS")}
    item.update({
        "id": fid, "fact_id": fid, "subject": "registrazione %s" % m["REGISTRATION_ID"],
        "predicate": m["CHANGE_TYPE"], "ESPECIE_DO_EVENTO": "EVENTO_REGULATORIO",
        "texto": texto, "source_id": SOURCE_ID,
        "source_location": "Roma", "source_location_basis": "contrato IT-T4-001: SOURCE_LOCATION_RULE",
        "fact_location": "ITALIA", "fact_location_basis": "contrato IT-T4-001: FACT_LOCATION_RULE (nacional)",
        "fact_time_basis": m["FACT_TIME_BASIS"],
        "published_at": m["EDICAO"],
        "published_at_basis": "data da edicao no nome do ficheiro PROD_FTS_6_AAAAMMDD",
        "source_declared_evidence_class": "REGULATORY_AUTHORIZATION",
    })
    if m["FACT_TIME"] != NAO_SEI:
        item["fact_time"] = m["FACT_TIME"]
    if observed_date:
        item["observed_at"] = observed_date
    return item


def run_id_do_diff(resultado: dict) -> str:
    """Deterministico: o mesmo par da a mesma corrida, e o retry e JA ESTAVA na Sala."""
    return "IT-T4-DIFF-%s-%s" % (resultado["SOURCE_VERSION_A"]["VERSION_DATE"].replace("-", ""),
                                 resultado["SOURCE_VERSION_B"]["VERSION_DATE"].replace("-", ""))


def emitir(resultado: dict, *, pousar: bool = False, escrever_livro: bool = False) -> dict:
    """Mudancas que emitem -> porta -> READY. Com `pousar`, pousa na Sala (backend do processo)."""
    import admissao as adm  # noqa: E402 — a porta canonica
    corrida = run_id_do_diff(resultado)
    prontos, recusados, decisoes = [], [], []
    for m in resultado["MUDANCAS"]:
        if not m["EMITE_EVENTO"]:
            continue
        item = item_do_evento(m, resultado.get("OBSERVED_DATE")
                              if resultado.get("OBSERVED_DATE") != NAO_SEI else None)
        d = adm.decidir(item, UNIVERSO, corrida=corrida)
        decisoes.append(d)
        if d.resultado == adm.SIM:
            prontos.append(adm.pronto_para_inteligencia(item, d))
        else:
            recusados.append({"ITEM": item["id"], "RESULTADO": d.resultado, "REGRA": d.regra,
                              "MOTIVO": d.motivo})
    fora = {"RUN_ID": corrida, "PRONTOS": prontos, "RECUSADOS": recusados, "SALA": None}
    if escrever_livro and decisoes:
        adm.escrever(decisoes)
    if pousar:
        import sala_de_espera as espera  # noqa: E402
        fora["SALA"] = espera.pousar(corrida, prontos)
    return fora


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    opc = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in argv if a.startswith("--") and "=" in a}
    ops = os.environ.get("ITALY_OPS_ROOT") or RAIZ
    if "--a" in opc and "--b" in opc:
        pa, pb, ca, cb = opc["--a"], opc["--b"], None, None
    else:
        livro = opc.get("--livro") or os.path.join(ops, "data", "collection-ledger", "italy",
                                                   "observations.ndjson")
        with open(livro, encoding="utf-8") as f:
            obs = [json.loads(l) for l in f if l.strip()]
        eds = edicoes_do_livro(obs, ops)
        print(json.dumps({"EDICOES_NO_LIVRO": eds}, ensure_ascii=False, indent=1))
        if len(eds) < 2:
            print("NOT ENOUGH VERSIONS: o livro conhece %d edicao(oes) de %s" % (len(eds), SOURCE_ID))
            return 1
        a, b = eds[-2], eds[-1]
        faltam = [e["DOCUMENT_ID"] for e in (a, b) if not e["BYTES_NESTA_ARVORE"]]
        if faltam:
            print("NAO SEI: o livro conhece %s, mas os bytes nao estao nesta arvore "
                  "(RAW_PATH ausente do disco). Nao se compara o que nao se tem." % faltam)
            return 1
        pa, pb = os.path.join(ops, a["RAW_PATH"]), os.path.join(ops, b["RAW_PATH"])
        ca, cb = a["PRIMEIRA_CAPTURA"], b["PRIMEIRA_CAPTURA"]
    import datetime as _dt
    r = comparar(pa, pb, captured_a=ca, captured_b=cb,
                 observed_date=_dt.datetime.now(_dt.timezone.utc).date().isoformat())
    g = guardar_diff(r, opc.get("--saida") or os.path.join(RAIZ, "data", "derivados", "IT-T4-001-EDICOES"))
    print(json.dumps({"ESTADO_DA_VERSAO": r["ESTADO_DA_VERSAO"], "TOTAIS": r.get("TOTAIS"),
                      "EVENTOS": r.get("EVENTOS", 0), "DIFF": g}, ensure_ascii=False, indent=1))
    if "--pousar" in argv:
        e = emitir(r, pousar=True, escrever_livro=True)
        print(json.dumps({"RUN_ID": e["RUN_ID"], "PRONTOS": len(e["PRONTOS"]),
                          "RECUSADOS": e["RECUSADOS"], "SALA": e["SALA"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
