#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R9 PELO CAMINHO CANONICO (D158) — a mesma Sala, sem mao humana.

    py provas/d158/r9_pelo_caminho_canonico.py [--saida <ficheiro.json>]

A PERGUNTA
----------
A corrida R9 liberou DOIS objetos. Eles existem porque as afirmacoes, os trechos, a data e
o lugar foram ESCRITOS A MAO num script. A pergunta e uma so:

    O PRODUTOR DE AFIRMACOES REENCONTRA, SOZINHO, AQUELES DOIS TRECHOS —
    E RECUSA O SINAL DE DOCUMENTO INTEIRO QUE A PROPRIA R9 JA RECUSAVA?

O CAMINHO, TODO ELE OFICIAL
---------------------------
    copia so-leitura da Sala   →   corte (um item, um endereco)
    →  PRODUTOR (leis/afirmacao_do_documento.py)        ← a peca nova da D158
    →  MOTOR OFICIAL (motor/motor_das_capacidades.rodar)  ← o livro, a LINEAGE, o RUN_ID
    →  GERADOR OFICIAL (pacote/pote_intelligence_casco.py)
    →  FISCAL (conferir_pote + pacote/validar_pote_v2.py)

`PARA-O-CASCO-R9/montar_r9.py` NAO e importado, NAO e lido como entrada e NAO produz nada
aqui. O oraculo entra so no fim, e so para COMPARAR: o pote que a R9 escreveu a mao.

⚠️⚠️ O QUE ESTE FICHEIRO NAO E — LEIA ANTES DE O USAR PARA QUALQUER OUTRA COISA
------------------------------------------------------------------------------
NAO E PRODUTO. NAO E CAMINHO DE INTEGRACAO. E uma MEDICAO, e so isso, e nada daqui deve
ser instalado, agendado nem chamado por outra peca.

Este ficheiro escreve `ESPECIE = SINAL` e `ESPECIE_DITA_POR = INTELLIGENCE` nos objetos
que monta. ISSO E DELE, NAO DO PRODUTOR. O produtor NUNCA escreve ESPECIE — «ESPECIE» esta
em `afirmacao_do_documento.CAMPOS_PROIBIDOS`, e uma afirmacao que a traga e RECUSADA
inteira com o motivo `PRODUTOR_DECIDIU_LIBERACAO`. Aqui ela existe porque o contrato do
POTE a exige para um objeto atravessar, e a medicao precisa de um objeto para chegar ao
fiscal. Num caminho de integracao a verdadeiro, quem diz a especie e a Intelligence.

As TRES decisoes que este harness toma, e que o produtor nao toma:
    · em que compartimento poisar um claim (`COMPARTIMENTO`);
    · quais os claims que valem um objeto (`tem_prova_completa`);
    · a ESPECIE e quem a disse (`objeto_da_afirmacao`).

Ligar o MOTOR a ler afirmacoes e o passo seguinte, e e da INTELLIGENCE — o G0 e o motor
nao sao tocados aqui, nem devem ser (CONTRATO-CONSUMO-AFIRMACOES §4 · INT-LAW-030/031).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ, RAIZ / "leis", RAIZ / "motor", RAIZ / "pacote", RAIZ / "admissao"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _gavetas                                  # noqa: E402,F401
import afirmacao_do_documento as AD              # noqa: E402
import tempo_da_afirmacao as TA                  # noqa: E402
import motor_das_capacidades as MOTOR            # noqa: E402
import porta_da_referencia as PORTA              # noqa: E402
import pote_intelligence_casco as POTE           # noqa: E402

#: A copia SO-LEITURA que a corrida R9 exportou. So se LE.
COPIA_DA_R9 = Path(r"C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
                   r"/EXPD78-R9-20260928T155047Z/copia/SALA_ATUAL.json")
#: O ORACULO — o pote que a R9 escreveu a mao. So entra na comparacao, no fim.
ORACULO = Path(r"C:/Users/London1/sintonia-sala-italia/intelligence-experimental"
               r"/PARA-O-CASCO-R9/POTE-R9-PARA_CLIENTE.json")
#: O dia da corrida R9 — o «hoje» que o motor precisa de receber declarado.
HOJE = date(2026, 9, 28)
NAO_SEI = POTE.NAO_SEI

#: DECISAO DO HARNESS (nao do produtor): em que compartimento poisar um claim. O `archive`
#: e o unico compartimento cujo contrato TEM chave para o tempo e o lugar DO FACTO
#: (`FACT_TIME`, `FACT_LOCATION`); o `windows`, onde a R9 pos os dois objetos a mao, nao
#: tem — foi o defeito #4 que a medicao da L2 ja tinha registado.
COMPARTIMENTO = "archive"


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ════════════════════════════════════════════════════════════════════════════
# 1 · O CORTE — um ITEM_ID, um endereco
# ════════════════════════════════════════════════════════════════════════════
def cortar(linhas: list) -> tuple:
    """O corte vigente: por ITEM_ID repetido fica o pouso MAIS RECENTE. O motor exige-o
    (`rodar`: «ITEM_ID repetido no corte: nao serve de endereco da prova»)."""
    por_item = {}
    for l in linhas:
        iid = str(l.get("item_id"))
        anterior = por_item.get(iid)
        if anterior is None or str(l.get("pousado_em") or "") > str(anterior.get("pousado_em") or ""):
            por_item[iid] = l
    dentro = [l for l in linhas if l is por_item.get(str(l.get("item_id")))]
    fora = [{"ITEM_ID": l.get("item_id"), "RUN_ID": l.get("run_id"), "ORDEM": l.get("ordem"),
             "POUSADO_EM": str(l.get("pousado_em"))}
            for l in linhas if l is not por_item.get(str(l.get("item_id")))]
    return dentro, fora


# ════════════════════════════════════════════════════════════════════════════
# 2 · O OBJETO QUE LEVA UMA AFIRMACAO AO POTE
# ════════════════════════════════════════════════════════════════════════════
def _um(v):
    """Uma chave do pote leva UM valor. Lista vira texto declarado; nunca se escolhe um."""
    if isinstance(v, list):
        return " ; ".join(str(x) for x in v) if v else NAO_SEI
    return NAO_SEI if v in (None, "", "UNKNOWN", TA.NAO_EXISTE) else v


def _entidades_de(af: dict, tipo: str) -> dict:
    """As entidades de UM tipo, juntas no formato que a chave do compartimento aceita."""
    es = [e for e in (af.get("ENTIDADES") or []) if e.get("TIPO") == tipo]
    nomes = [e["VALOR_NORMALIZADO"] for e in es if e.get("VALOR_NORMALIZADO") not in (None, NAO_SEI)]
    fonte = next((e["ENTITY_SOURCE"] for e in es if e.get("ENTITY_SOURCE") != "UNKNOWN"), "UNKNOWN")
    return {"VALOR": nomes, "ENTITY_SOURCE": fonte}


def objeto_da_afirmacao(af: dict, ref) -> dict:
    """A afirmacao no contrato do compartimento. NADA e acrescentado ao que ela ja diz."""
    p = af["PROVENIENCIA"]
    cultura = _entidades_de(af, "CULTURA")
    praga = _entidades_de(af, "PRAGA_OU_DOENCA")
    prova = {"ITEM_ID": p["ITEM_ID"], "RAW_OBSERVATION_ID": p["RAW_OBSERVATION_ID"],
             "SOURCE_ID": p["SOURCE_ID"], "DOCUMENT_ID": p["DOCUMENT_ID"],
             "CORRIDA_UPSTREAM": p["RUN_ID"], "URL": p["URL"],
             "PUBLISHED_AT": p["PUBLISHED_AT"], "COLHIDO_EM": p["COLHIDO_EM"],
             "FACT_TIME": af["FACT_TIME"]["VALOR"],
             # D-GER-2: a identidade do byte vem do banco (raw_asset), nunca calculada
             "RAW_SHA256": p["RAW_SHA256"], "RAW_STORAGE_PATH": p["RAW_STORAGE_PATH"],
             # COL-LAW-202: o claim leva o EVIDENCE_SPAN consigo
             "ASSERTION_ID": af["ASSERTION_ID"], "TRECHO": af["TRECHO_LITERAL"],
             "TRECHO_SHA256": af["TRECHO_SHA256"],
             "OFFSET": {"INICIO": af["POSICAO"]["INICIO"], "FIM": af["POSICAO"]["FIM"]},
             "ANCORA_DA_SECAO": af["POSICAO"]["SECAO"]["CABECALHO"],
             "FACT_TIME_ROLE": {k: af["FACT_TIME_ROLE"][k] for k in ("PAPEL", "ORIGEM", "BASIS")},
             "FACT_LOCATION_TRECHO": af["FACT_LOCATION"]["TRECHO"]}
    # ⚠️ ESPECIE e ESPECIE_DITA_POR sao DESTE HARNESS, nao da afirmacao: o contrato do pote
    # exige-os para um objeto atravessar. O produtor nao os escreve (CAMPOS_PROIBIDOS).
    o = {"OBJETO_ID": af["ASSERTION_ID"], "ESPECIE": POTE.SINAL,
         "ESPECIE_DITA_POR": "INTELLIGENCE", "ESTADO": POTE.ESTADO_TRANSPORTAVEL,
         "CHAVES": {"CROP_ID": _um(cultura["VALOR"]), "ISSUE_ID": _um(praga["VALOR"]),
                    # REGION_ID e uma IDENTIDADE do casco; a afirmacao da o LUGAR, nao o id.
                    # Cunha-lo aqui seria a Intelligence a fabricar identidade (INT-LAW-031).
                    "REGION_ID": NAO_SEI,
                    "FACT_LOCATION": af["FACT_LOCATION"]["VALOR"],
                    "FACT_TIME": af["FACT_TIME"]["VALOR"]},
         "PROVA": [prova],
         "LOCATION_SOURCE": af["FACT_LOCATION"]["LOCATION_SOURCE"],
         "PORQUE": ("uma AFIRMACAO do item %s: o trecho texto[%d:%d], com o tempo (%s, origem %s) e "
                    "o lugar (%s) provados no proprio trecho ou no cabecalho da seccao dele"
                    % (p["ITEM_ID"], af["POSICAO"]["INICIO"], af["POSICAO"]["FIM"],
                       af["FACT_TIME_ROLE"]["PAPEL"], af["FACT_TIME_ROLE"]["ORIGEM"],
                       af["FACT_LOCATION"]["LOCATION_SOURCE"])),
         "CONTRADIZ": NAO_SEI,
         "INCERTEZA": ("afirmacao de UMA fonte, lida por regra; contradicao NAO MEDIDA. "
                       "A Collection nao diz o que ela significa."),
         "LIGACAO_ADAMA": PORTA.ligacao_adama(ref, {})}
    # COL-LAW-221 · ENTITY_SOURCE responde «de onde veio o NOME da entidade». Sem entidade
    # no claim, a pergunta nao se aplica, e o campo nao viaja. Com entidade, viaja o valor
    # da lei — e nunca um valor inventado.
    fonte_da_entidade = next((r["ENTITY_SOURCE"] for r in (cultura, praga)
                              if r["ENTITY_SOURCE"] != "UNKNOWN"), None)
    if fonte_da_entidade:
        o["ENTITY_SOURCE"] = fonte_da_entidade
    return o


def com_entity_source_da_lei(o: dict, af: dict) -> dict:
    """A MESMA saida, com o ENTITY_SOURCE da COL-LAW-221 SEMPRE escrito — inclusive UNKNOWN.

    Serve para medir o conflito D-GER-1 (defeito #8): a lei da entidade escreve UNKNOWN, e
    o fiscal do pote deste ramo so aceita «NAO SEI» como ignorancia. Nao se contorna: mede-se."""
    r = dict(o)
    r["ENTITY_SOURCE"] = _entidades_de(af, "CULTURA")["ENTITY_SOURCE"]
    return r


def tem_prova_completa(af: dict) -> bool:
    """DECISAO DO HARNESS: que afirmacao vale um objeto. Tempo do FACTO + lugar do FACTO,
    os dois provados. Nao e liberacao (C8 e do dono): e o minimo para haver o que liberar."""
    return (af["FACT_TIME"]["VALOR"] not in (NAO_SEI, TA.NAO_EXISTE)
            and af["FACT_LOCATION"]["VALOR"] != NAO_SEI)


# ════════════════════════════════════════════════════════════════════════════
# 3 · A COMPARACAO COM O ORACULO
# ════════════════════════════════════════════════════════════════════════════
def ler_o_oraculo() -> list:
    """Os objetos que a R9 LIBEROU, com o trecho, o tempo e o lugar que a mao escreveu."""
    pote = json.loads(ORACULO.read_text(encoding="utf-8"))
    fora = []
    for comp, e in (pote.get("COMPARTIMENTOS") or {}).items():
        for o in e.get("OBJETOS") or []:
            p = (o.get("PROVA") or [{}])[0]
            chaves = o.get("CHAVES") or {}
            f = o.get("FORA_DO_CONTRATO") or {}
            fora.append({"COMPARTIMENTO": comp, "OBJETO_ID": o.get("OBJETO_ID"),
                         "ITEM_ID": p.get("ITEM_ID"), "TRECHO": p.get("TRECHO_DA_AFIRMACAO"),
                         "RAW_SHA256": p.get("RAW_SHA256"),
                         "FACT_TIME": chaves.get("FACT_TIME") or f.get("FACT_TIME"),
                         "FACT_LOCATION": chaves.get("FACT_LOCATION") or f.get("FACT_LOCATION"),
                         "LIBERACAO": o.get("LIBERACAO")})
    return fora


def _normal(s):
    return " ".join(str(s or "").split())


def comparar(manuais: list, automaticas: list) -> dict:
    """Objeto a objeto. Nada e forcado: quando difere, escreve-se o que cada lado diz."""
    linhas = []
    for m in manuais:
        alvo = _normal(m["TRECHO"])
        exacta = next((a for a in automaticas if _normal(a["TRECHO_LITERAL"]) == alvo), None)
        contida = exacta or next((a for a in automaticas
                                  if alvo and alvo in _normal(a["TRECHO_LITERAL"])), None)
        linha = {"MANUAL": m, "ENCONTRADA": bool(contida),
                 "TRECHO_IGUAL": bool(exacta),
                 "TRECHO_CONTIDO_NUM_TRECHO_MAIOR": bool(contida and not exacta)}
        if contida:
            linha["AUTOMATICA"] = {
                "ASSERTION_ID": contida["ASSERTION_ID"], "ITEM_ID": contida["PROVENIENCIA"]["ITEM_ID"],
                "TRECHO": contida["TRECHO_LITERAL"],
                "OFFSET": [contida["POSICAO"]["INICIO"], contida["POSICAO"]["FIM"]],
                "RAW_SHA256": contida["PROVENIENCIA"]["RAW_SHA256"],
                "FACT_TIME": contida["FACT_TIME"]["VALOR"],
                "FACT_TIME_ORIGEM": contida["FACT_TIME_ROLE"]["ORIGEM"],
                "FACT_TIME_BASIS": contida["FACT_TIME_ROLE"]["BASIS"],
                "FACT_LOCATION": contida["FACT_LOCATION"]["VALOR"],
                "FACT_LOCATION_SOURCE": contida["FACT_LOCATION"]["LOCATION_SOURCE"]}
            linha["MESMO_RAW_SHA256"] = m["RAW_SHA256"] == contida["PROVENIENCIA"]["RAW_SHA256"]
            linha["MESMO_FACT_TIME"] = m["FACT_TIME"] == contida["FACT_TIME"]["VALOR"]
            linha["MESMO_FACT_LOCATION"] = m["FACT_LOCATION"] == contida["FACT_LOCATION"]["VALOR"]
        linhas.append(linha)
    return {"POR_OBJETO": linhas,
            "R9_MANUAL": len(manuais),
            "ENCONTRADOS": sum(1 for x in linhas if x["ENCONTRADA"]),
            "MESMOS_TRECHOS": all(x["TRECHO_IGUAL"] for x in linhas) if linhas else False,
            "MESMOS_RAW_SHA256": all(x.get("MESMO_RAW_SHA256") for x in linhas) if linhas else False,
            "MESMOS_FACT_TIME": all(x.get("MESMO_FACT_TIME") for x in linhas) if linhas else False,
            "MESMOS_FACT_LOCATION": all(x.get("MESMO_FACT_LOCATION") for x in linhas) if linhas else False}


# ════════════════════════════════════════════════════════════════════════════
# 4 · A CORRIDA
# ════════════════════════════════════════════════════════════════════════════
def gerar_o_pote(livro: dict, objetos: list, nome: str, destino: Path) -> dict:
    """O GERADOR OFICIAL, como CLI, tal como o gatilho o chama. Nada e adaptado a mao."""
    entrada = {k: v for k, v in livro.items() if k != "SIGNALS"}
    entrada["ITENS_POR_FERRAMENTA"] = {COMPARTIMENTO: objetos} if objetos else {}
    p_ent = destino / ("ENTRADA-%s.json" % nome)
    p_out = destino / ("POTE-%s.json" % nome)
    p_ent.write_text(json.dumps(entrada, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    r = subprocess.run([sys.executable, "pacote/pote_intelligence_casco.py", str(p_ent), str(p_out)],
                       cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1"))
    saida = {"GERADOR": "pacote/pote_intelligence_casco.py", "CODIGO": r.returncode,
             "STDERR": (r.stderr or "").strip()[-900:], "ENTRADA": p_ent.name, "OBJETOS_NA_ENTRADA": len(objetos)}
    if r.returncode != 0:
        saida["POTE"] = None
        saida["FISCAL"] = "o gerador recusou: nao ha pote"
        return saida
    pote = json.loads(p_out.read_text(encoding="utf-8"))
    v = POTE.conferir_pote(pote)
    val = subprocess.run([sys.executable, "pacote/validar_pote_v2.py", str(p_out)], cwd=str(RAIZ),
                         capture_output=True, text=True, encoding="utf-8",
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1"))
    saida.update({"POTE": p_out.name, "POTE_SHA256": sha(p_out),
                  "CONFERIR_POTE": "PASSA (0 violacoes)" if not v else v,
                  "VALIDAR_POTE_V2": "PASSA" if val.returncode == 0 else
                                     "REPROVA: " + (val.stdout or val.stderr).strip()[-600:],
                  "OBJETOS_NO_POTE": sum(len(e.get("OBJETOS") or [])
                                         for e in pote["COMPARTIMENTOS"].values()),
                  "RECUSADOS": [{"PORQUE": x.get("PORQUE"), "DETALHE": x.get("DETALHE"),
                                 "OBJETO_ID": x.get("OBJETO_ID")} for x in (pote.get("RECUSADOS") or [])][:20]})
    return saida


def campos_de_origem(destino: Path) -> dict:
    """O que o GERADOR OFICIAL escreveu em ENTITY_SOURCE / LOCATION_SOURCE nos dois potes.

    A pergunta e a do defeito #8 (D-GER-1): a COL-LAW-221 escreve `UNKNOWN` e o fiscal
    deste ramo so aceita «NAO SEI» como ignorancia. Aqui mede-se o que de facto acontece."""
    fora = {}
    for nome in ("AFIRMACOES", "ENTITY-SOURCE-DA-LEI"):
        p = destino / ("POTE-%s.json" % nome)
        if not p.exists():
            continue
        pote = json.loads(p.read_text(encoding="utf-8"))
        conta = {}
        for e in pote["COMPARTIMENTOS"].values():
            for o in e.get("OBJETOS") or []:
                for c in ("ENTITY_SOURCE", "LOCATION_SOURCE"):
                    chave = "%s=%r" % (c, o.get(c, "<ausente>"))
                    conta[chave] = conta.get(chave, 0) + 1
        fora[nome] = conta
    return fora


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent / "R9-PELO-CAMINHO-CANONICO.json"))
    ap.add_argument("--destino", default=None, help="onde escrever entradas e potes (por omissao, o TEMP)")
    a = ap.parse_args(argv)
    destino = Path(a.destino) if a.destino else Path(os.environ.get("TEMP", ".")) / "d158"
    destino.mkdir(parents=True, exist_ok=True)

    linhas = json.loads(COPIA_DA_R9.read_text(encoding="utf-8"))
    corte, fora = cortar(linhas)
    r = {"PERGUNTA": "o produtor reencontra sozinho os dois trechos que a R9 escreveu a mao?",
         "SALA": {"FICHEIRO": str(COPIA_DA_R9), "SHA256": sha(COPIA_DA_R9), "LINHAS": len(linhas),
                  "SO_LEITURA": True},
         "CORTE": {"DENTRO": len(corte), "FORA": len(fora), "REPETIDOS": fora}}

    # ── PRODUTOR ────────────────────────────────────────────────────────────
    todas, funil, reprovadas = [], {}, []
    for l in corte:
        saida = AD.afirmacoes_do_item(l)
        for k, n in saida["FUNIL"].items():
            funil[k] = funil.get(k, 0) + n
        for af in saida["AFIRMACOES"]:
            v = AD.conferir_afirmacao(af, l.get("texto") or "", raw_sha256=l.get("raw_sha256"))
            if v:
                reprovadas.append({"ASSERTION_ID": af["ASSERTION_ID"], "VIOLACOES": v})
            else:
                todas.append(af)
    com_prova = [af for af in todas if tem_prova_completa(af)]
    r["PRODUTOR"] = {"AFIRMACOES_GERADAS": len(todas), "REPROVADAS_NA_CONFERENCIA": len(reprovadas),
                     "COM_TEMPO_E_LUGAR_DO_FACTO": len(com_prova), "FUNIL": funil,
                     "ITENS_COM_AFIRMACAO_COM_PROVA": len({af["PROVENIENCIA"]["ITEM_ID"] for af in com_prova})}

    # ── MOTOR OFICIAL ───────────────────────────────────────────────────────
    envelope = {"EXPORT": MOTOR.EXPORT_DA_SALA, "LINHAS": corte,
                "CORTE": {"COPIA": COPIA_DA_R9.name, "SHA256": sha(COPIA_DA_R9), "READY": len(corte)},
                "ORIGEM": "copia so-leitura da corrida R9", "SINTETICO": False}
    ref = PORTA.abrir()
    livro = MOTOR.rodar(MOTOR.entrada_do_export(envelope), HOJE,
                        source_head="D158/produtor-de-afirmacoes", referencia=ref)
    r["MOTOR_OFICIAL"] = {"MODULO": "motor/motor_das_capacidades.py::rodar",
                          "INTELLIGENCE_RUN_ID": livro.get("INTELLIGENCE_RUN_ID"),
                          "RESULT_STATE": livro.get("RESULT_STATE"),
                          "SINAIS_DA_CORRIDA": len(((livro.get("CORRIDA") or {}).get("SIGNALS")) or []),
                          "SIGNALS_PARA_O_POTE": len(livro.get("SIGNALS") or []),
                          "OBJETOS_DO_MOTOR": {k: len(v) for k, v in
                                               (livro.get("ITENS_POR_FERRAMENTA") or {}).items()}}

    # ── GERADOR OFICIAL + FISCAL ────────────────────────────────────────────
    objetos = [objeto_da_afirmacao(af, ref) for af in com_prova]
    r["POTE_DAS_AFIRMACOES"] = gerar_o_pote(livro, objetos, "AFIRMACOES", destino)
    # o mesmo, com o ENTITY_SOURCE da lei sempre escrito: a medicao do conflito D-GER-1
    duros = [com_entity_source_da_lei(o, af) for o, af in zip(objetos, com_prova)]
    r["MEDICAO_DO_CONFLITO_D_GER_1"] = gerar_o_pote(livro, duros, "ENTITY-SOURCE-DA-LEI", destino)

    # ── O ORACULO, so agora ─────────────────────────────────────────────────
    manuais = ler_o_oraculo()
    r["R9_MANUAL"] = {"FICHEIRO": str(ORACULO), "SHA256": sha(ORACULO), "OBJETOS": manuais}
    r["COMPARACAO"] = comparar(manuais, todas)
    r["COMPARACAO"]["COMPARADO_CONTRA"] = ("todas as afirmacoes geradas (nao so as que tem prova "
                                           "completa): a pergunta e se o produtor ACHA o trecho")
    r["COMPARACAO"]["ENTRE_AS_COM_PROVA_COMPLETA"] = comparar(manuais, com_prova)["POR_OBJETO"]

    # ── CONTROLE · o mesmo produtor fora da R9 (o que prova que nao ha sobreajuste) ────
    itens_da_r9 = {m["ITEM_ID"] for m in manuais}
    fora_da_r9 = [af for af in com_prova if af["PROVENIENCIA"]["ITEM_ID"] not in itens_da_r9]
    r["CONTROLE_FORA_DA_R9"] = {
        "AFIRMACOES_COM_PROVA_COMPLETA": len(fora_da_r9),
        "ITENS": sorted({af["PROVENIENCIA"]["ITEM_ID"] for af in fora_da_r9}),
        "FONTES": sorted({af["PROVENIENCIA"]["SOURCE_ID"] for af in fora_da_r9}),
        "ORIGENS_DO_TEMPO": {o: sum(1 for af in fora_da_r9 if af["FACT_TIME_ROLE"]["ORIGEM"] == o)
                             for o in TA.ORIGENS},
        "AMOSTRA": [{"ITEM_ID": af["PROVENIENCIA"]["ITEM_ID"], "SOURCE_ID": af["PROVENIENCIA"]["SOURCE_ID"],
                     "TRECHO": af["TRECHO_LITERAL"][:220], "FACT_TIME": af["FACT_TIME"]["VALOR"],
                     "ORIGEM": af["FACT_TIME_ROLE"]["ORIGEM"],
                     "FACT_LOCATION": af["FACT_LOCATION"]["VALOR"]} for af in fora_da_r9[:12]]}

    # ── como o GERADOR OFICIAL escreveu os campos de origem (o conflito D-GER-1, medido) ──
    r["CAMPOS_DE_ORIGEM_NO_POTE"] = campos_de_origem(destino)

    # ── o sinal de documento inteiro que a R9 recusava ──────────────────────
    sinais = ((livro.get("CORRIDA") or {}).get("SIGNALS")) or []
    do_n38 = [s for s in sinais if str(s.get("ITEM_ID")) in {m["ITEM_ID"] for m in manuais}]
    r["SINAL_DE_DOCUMENTO_INTEIRO"] = [
        {"SIGNAL_ID": s.get("SIGNAL_ID"), "ITEM_ID": s.get("ITEM_ID"), "FACT_TIME": s.get("FACT_TIME"),
         "FACT_TIME_BASIS": s.get("FACT_TIME_BASIS"), "FACT_LOCATION": s.get("FACT_LOCATION"),
         "CHEGOU_AO_POTE": False,
         "PORQUE": "o motor deixa os sinais no livro; o pote so leva ITENS_POR_FERRAMENTA"}
        for s in do_n38]

    Path(a.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("CORTE", "PRODUTOR", "MOTOR_OFICIAL")}, ensure_ascii=False)[:1200])
    print(json.dumps(r["POTE_DAS_AFIRMACOES"], ensure_ascii=False)[:900])
    print(json.dumps({k: v for k, v in r["COMPARACAO"].items() if k != "POR_OBJETO"}, ensure_ascii=False))
    print("saida:", a.saida, "sha256", sha(a.saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
