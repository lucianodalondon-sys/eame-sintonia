#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O G0 POR AFIRMACAO — a unidade do G0 passa a poder ser o CLAIM, e nao so o ITEM.

    DIRETIVA-G0-POR-AFIRMACAO (Intelligence owner, 29/09) · CONTRATO-CONSUMO-AFIRMACOES (D158, §1-§3, §5-B)

O DEFEITO (medido pelo dono): o G0 (`corrida_da_inteligencia.portao_g0`) avalia o FACT_TIME do DOCUMENTO.
Uma afirmacao com tempo proprio provado herdava o bloqueio de um documento sem tempo unico, e a prova dela
era recusada no pote por «ITEM_ID ... tem G0 = BLOQUEADO_EM_G0». O portao em si nao esta errado: a unidade
e que estava. Este modulo acrescenta a unidade CLAIM ao lado da unidade ITEM, e nao toca na do item.

O QUE ENTRA
-----------
UM artefato opcional, `AFIRMACOES_DA_SALA/v1`, produzido pela Collection (o produtor, COL-LAW-202) a partir da
MESMA copia so-leitura da Sala. E lido e NUNCA recalculado: a Intelligence nao completa, nao corrige e nao cunha
nada (contrato §0) — o CLAIM_ID e o do produtor. Sem o artefato, nada deste modulo corre, e a corrida e byte a
byte a de sempre.

O QUE ELE FAZ
-------------
1. CONFERIR cada afirmacao contra o item (RECUSADA, com o motivo no livro, fora da LINEAGE — sem prova ate ao RAW
   nao e evidencia, contrato §3): CLAIM_ID presente; o produtor nao decidiu liberacao nem especie; ITEM_ID,
   RAW_OBSERVATION_ID e SOURCE_ID iguais aos do item; RAW_SHA256 igual ao do item (lido do raw_asset, D-GER-2);
   `texto[INICIO:FIM] == TRECHO` do EVIDENCE_SPAN.
2. `portao_g0_da_afirmacao(af, item)`: D1-D4 do `portao_g0`, aplicados ao FACT_TIME da AFIRMACAO e ao dia de
   captura do ITEM, mais o papel (so ACONTECIMENTO e facto), a origem (as QUATRO do §5-B; LITERAL exige o BASIS
   dentro do EVIDENCE_SPAN), o BASIS literal no texto (a publicacao nao vira facto por falta de base propria), e o
   tempo que a classe exige (§2). RELATIVO_D63 passa, mas nunca serve ACT_NOW.
3. O LIVRO: uma entrada da LINEAGE por CLAIM_ID (a forma de sempre + CLAIM_ID, G0_DA_AFIRMACAO, G0_DO_ITEM); a
   entrada do item fica la, igual. Duas afirmacoes com o mesmo TRECHO_SHA256 no mesmo item contam UMA vez; a
   segunda fica visivel, com DUPLICATA_DE. Os sinais das afirmacoes vao para SINAIS_DAS_AFIRMACOES, com
   SIGNAL_ID derivado de run_id + CLAIM_ID.

⚠️ Este ficheiro e NOVO de proposito: `corrida_da_inteligencia.versao_do_codigo()` sela o proprio ficheiro e
entra na identidade da corrida. Mexer la mudaria o INTELLIGENCE_RUN_ID — e o pote — mesmo sem afirmacoes.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import corrida_da_inteligencia as CI

NAO_SEI = CI.NAO_SEI
CONTRATO_DO_ARTEFATO = "AFIRMACOES_DA_SALA/v1"
CONTRATO_DA_AFIRMACAO = "AFIRMACAO/v1"
PASSOU, BLOQUEADO = "PASSOU", CI.BLOQUEADO_EM_G0
#: §1 · o papel que e facto (o produtor so o escreve em FACT_TIME com este papel; a Intelligence confere)
PAPEL_QUE_E_FACTO = "ACONTECIMENTO"
#: §5-B · as QUATRO origens distinguiveis do FACT_TIME. So LITERAL tem o BASIS dentro do trecho.
LITERAL = "LITERAL"
RELATIVO_D63 = "RELATIVO_D63"
ORIGENS = (LITERAL, "CABECALHO_D147", "RELATIVA_ANCORADA_D149", RELATIVO_D63)
#: §1 · o vocabulario fechado da classe; NAO SEI e aceite como valor e BLOQUEIA (§2)
CLAIM_KINDS = ("ALERTA_EVENTO", "CIENCIA_FICHA", "PRECO", "REGULATORIO", "RECOMENDACAO")
#: §2 · o tempo que cada classe exige (o nome do campo da afirmacao; varios = basta um)
TEMPO_DA_CLASSE = {"ALERTA_EVENTO": ("FACT_TIME",), "PRECO": ("MARKET_PERIOD",),
                   "REGULATORIO": ("VALIDITY", "ACT_TIME"), "RECOMENDACAO": ("VALIDITY",),
                   "CIENCIA_FICHA": ()}
#: §0 · o produtor nunca decide isto; trazer um destes = PRODUTOR_DECIDIU_LIBERACAO, e a afirmacao cai inteira
CAMPOS_PROIBIDOS = ("LIBERADO", "LIBERACAO", "LIBERADO_POR", "LIBERADO_NA_CORRIDA", "CONFERENCIA_DE_LIBERACAO",
                    "NAO_PARA_CLIENTE", "ESPECIE", "USO")
PROVENIENCIA_DA_AFIRMACAO = ("CLAIM_ID", "ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID", "RAW_SHA256")
#: §5-C (BLK-1) · a contagem de concorrentes que o PRODUTOR declara (a Intelligence nao le o texto para isto):
#: campo -> (o valor que ela guarda, o motivo da recusa). Contagem > 1 com valor != NAO SEI = recusa; sem contagem
#: (ou nao inteira) = recusa com PRODUTOR_SEM_CONTAGEM_DE_CONCORRENTES.
CONCORRENTES = {"TEMPOS_NO_TRECHO": ("FACT_TIME", "TEMPOS_CONCORRENTES"),
                "LUGARES_NO_TRECHO": ("FACT_LOCATION", "LUGARES_CONCORRENTES")}
SEM_CONTAGEM = "PRODUTOR_SEM_CONTAGEM_DE_CONCORRENTES"


def versao() -> str:
    """A impressao deste ficheiro: entra na identidade da corrida SO quando ha afirmacoes."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


def _valor(bloco):
    """O VALOR de um bloco do produtor ({"VALOR": ...}) ou o proprio escalar."""
    return bloco.get("VALOR") if isinstance(bloco, dict) else bloco


def _ign(v) -> bool:
    return v is None or CI.e_ignorancia(v) or v == "NAO_EXISTE"


# ── 0 · o artefato ────────────────────────────────────────────────────────────
def indexar(artefato: dict) -> tuple:
    """-> ({(RUN_ID, ITEM_ID): [afirmacao, ...]}, carimbo). Le; nao recalcula nada."""
    if not isinstance(artefato, dict) or artefato.get("CONTRATO") != CONTRATO_DO_ARTEFATO:
        raise CI.LeiViolada("isto nao e um artefato %s" % CONTRATO_DO_ARTEFATO)
    idx, ids = {}, []
    for it in artefato.get("ITENS") or []:
        prov = it.get("PROVENIENCIA") or {}
        chave = (str(prov.get("RUN_ID")), str(prov.get("ITEM_ID")))
        for af in it.get("AFIRMACOES") or []:
            idx.setdefault(chave, []).append(af)
            ids.append(str(af.get("CLAIM_ID")))
    carimbo = {"CONTRATO": CONTRATO_DO_ARTEFATO, "AFIRMACOES": len(ids),
               "IMPRESSAO_DOS_CLAIM_ID": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
               "ENTRADA_DO_PRODUTOR": (artefato.get("ENTRADA") or {}).get("SHA256", NAO_SEI),
               "CODIGO_DO_G0_DA_AFIRMACAO": versao()}
    return idx, carimbo


# ── 1 · a conferencia (RECUSA: nao entra no livro como evidencia) ────────────
def conferir(af: dict, item: dict, raw_sha256, texto: str) -> list:
    """Os motivos de RECUSA desta afirmacao contra o seu item. Vazio = conferida."""
    m = []
    if not isinstance(af, dict):
        return ["AFIRMACAO_NAO_E_OBJETO"]
    if _ign(af.get("CLAIM_ID")):
        m.append("SEM_CLAIM_ID: o CLAIM_ID e cunhado pelo produtor, e a Intelligence nunca o cunha")
    if af.get("CONTRATO") != CONTRATO_DA_AFIRMACAO:
        m.append("CONTRATO %r nao e %s" % (af.get("CONTRATO"), CONTRATO_DA_AFIRMACAO))
    intrusos = [c for c in CAMPOS_PROIBIDOS if c in af]
    if intrusos:
        m.append("PRODUTOR_DECIDIU_LIBERACAO: " + ", ".join(intrusos))
    for c in ("ITEM_ID", "RAW_OBSERVATION_ID", "SOURCE_ID"):
        if _ign(af.get(c)) or str(af.get(c)) != str(item.get(c)):
            m.append("PROVENIENCIA: %s da afirmacao (%r) nao e o do item (%r)" % (c, af.get(c), item.get(c)))
    if _ign(raw_sha256):
        m.append("RAW_SHA256: o item nao traz o sha do raw_asset; nao ha como conferir o byte")
    elif af.get("RAW_SHA256") != raw_sha256:
        m.append("RAW_SHA256: o da afirmacao nao e o do item (raw_asset)")
    span = af.get("EVIDENCE_SPAN") if isinstance(af.get("EVIDENCE_SPAN"), dict) else {}
    a, b, trecho = span.get("INICIO"), span.get("FIM"), span.get("TRECHO")
    if not (isinstance(a, int) and isinstance(b, int) and isinstance(trecho, str) and 0 <= a < b):
        m.append("EVIDENCE_SPAN: sem INICIO/FIM/TRECHO")
    elif str(texto or "")[a:b] != trecho:
        m.append("EVIDENCE_SPAN: texto[%d:%d] nao e o TRECHO" % (a, b))
    return m


# ── 2 · o portao ──────────────────────────────────────────────────────────────
def _basis_literal(basis, texto: str) -> bool:
    return (isinstance(basis, dict) and isinstance(basis.get("INICIO"), int) and isinstance(basis.get("FIM"), int)
            and isinstance(basis.get("TRECHO"), str) and str(texto or "")[basis["INICIO"]:basis["FIM"]] == basis["TRECHO"])


def portao_g0_da_afirmacao(af: dict, item: dict, texto: str | None = None) -> tuple:
    """`(passou, o_que_falta)` para UMA afirmacao. D1-D4 como `portao_g0`, sobre o tempo DELA e a captura do ITEM."""
    falta = []
    classe = _valor(af.get("CLAIM_KIND"))
    if classe not in CLAIM_KINDS:
        falta.append("CLAIM_KIND:NAO_SEI")
    papel = (af.get("FACT_TIME_ROLE") or {}).get("PAPEL")
    origem = (af.get("FACT_TIME_ROLE") or {}).get("ORIGEM")
    ft_bloco = af.get("FACT_TIME") if isinstance(af.get("FACT_TIME"), dict) else {}
    ft = ft_bloco.get("VALOR")
    exige = TEMPO_DA_CLASSE.get(classe, ("FACT_TIME",))
    if not _ign(ft):
        # §1 · um FACT_TIME com valor so existe com o papel ACONTECIMENTO
        if papel != PAPEL_QUE_E_FACTO:
            falta.append("FACT_TIME:PAPEL_%s_NAO_E_FACTO" % papel)
        if origem not in ORIGENS:
            falta.append("FACT_TIME:ORIGEM_FORA_DO_CONTRATO")
        basis = ft_bloco.get("FACT_TIME_BASIS")
        if not isinstance(basis, dict) or _ign(basis.get("TRECHO")):
            falta.append("FACT_TIME:SEM_BASE")                                            # D2
        else:
            if texto is not None and not _basis_literal(basis, texto):
                falta.append("FACT_TIME:BASE_NAO_E_DO_TEXTO")
            span = af.get("EVIDENCE_SPAN") or {}
            if origem == LITERAL and not (isinstance(span.get("INICIO"), int) and isinstance(basis.get("INICIO"), int)
                                          and span["INICIO"] <= basis["INICIO"] and basis.get("FIM", 0) <= span.get("FIM", -1)):
                falta.append("FACT_TIME:LITERAL_COM_BASIS_FORA_DO_TRECHO")                # §5-B · C1
        tempo = CI.intervalo_do_tempo(ft)
        if tempo["ESTADO"] == "SEM_ANO":
            falta.append("FACT_TIME:SEM_ANO")                                             # D3
        elif tempo["ESTADO"] != "INTERVALO":
            falta.append("FACT_TIME:NAO_ANALISAVEL")
        else:
            captura = CI._dia_da_captura(item)
            if captura is None:
                falta.append("FACT_TIME:CAPTURA_DESCONHECIDA_FUTURO_NAO_EXCLUIDO")
            elif date.fromisoformat(tempo["INICIO"]) > captura:
                falta.append("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA")                     # D4
    elif "FACT_TIME" in exige:
        falta.append("FACT_TIME")                                                         # D1
    outros = [c for c in exige if c != "FACT_TIME"]
    if outros and all(_ign(_valor(af.get(c))) for c in outros):
        falta.append("TEMPO_DA_CLASSE:%s" % "|".join(outros))                            # §2
    falta += _concorrentes(af)                                                            # §5-C · BLK-1
    return (not falta), sorted(falta)


def _concorrentes(af: dict) -> list:
    """§5-C · mais de 1 tempo (ou lugar) no trecho e o valor nao e NAO SEI -> o valor pode ser de OUTRO facto
    («Europa 2004 ... Italia 2012» saiu 2004 + Italia). Sem a contagem, o G0 nao sabe e recusa."""
    falta = []
    for campo, (guarda, motivo) in CONCORRENTES.items():
        n = _valor(af.get(campo))
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            falta.append("%s:%s" % (SEM_CONTAGEM, campo))
        elif n > 1 and not _ign(_valor(af.get(guarda))):
            falta.append("%s:%s=%d" % (motivo, campo, n))
    return falta


def _estado(af, passou, falta) -> dict:
    ft = _valor(af.get("FACT_TIME"))
    t_falta = [m for m in falta if m.startswith("FACT_TIME")]
    estado = ("ANCORADO" if passou and not _ign(ft) else
              "FUTURO_EM_RELACAO_A_CAPTURA" if "FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA" in t_falta else
              "UNKNOWN_WINDOW")
    bloqueados = {} if estado == "ANCORADO" else {u: "FACT_TIME:" + estado for u in CI.USOS_QUE_EXIGEM_TEMPO}
    if (af.get("FACT_TIME_ROLE") or {}).get("ORIGEM") == RELATIVO_D63:
        # §1 · a relativa contada da publicacao rebaixa a precisao: nunca ACT_NOW
        bloqueados["ACT_NOW"] = RELATIVO_D63
    return {"TEMPORAL_STATE": estado, "PORQUE_TEMPO": sorted(t_falta),
            "USOS_BLOQUEADOS": bloqueados,
            "USOS_DISPONIVEIS": list(CI.USOS_SEM_TEMPO) + [u for u in CI.USOS_QUE_EXIGEM_TEMPO if u not in bloqueados]}


# ── 3 · o livro ───────────────────────────────────────────────────────────────
def aplicar(livro: dict, registos: list, raw: dict, idx: dict) -> dict:
    """Acrescenta ao livro as entradas por CLAIM_ID, as recusadas e os sinais das afirmacoes. -> contagens.

    A entrada do ITEM na LINEAGE nao muda (o seu G0 continua o do documento). Uma entrada de afirmacao tem sempre
    CLAIM_ID — e e por ele, e nao pelo par (corrida, item), que a prova de uma afirmacao se procura."""
    run_id = livro["INTELLIGENCE_RUN_ID"]
    do_item = {(str(l.get("CORRIDA_UPSTREAM")), str(l.get("ITEM_ID"))): l
               for l in livro["LINEAGE"] if "CLAIM_ID" not in l}
    recusadas, sinais, conta = [], [], {"RECEBIDAS": 0, "RECUSADAS": 0, "DUPLICADAS": 0, "PASSARAM_G0": 0,
                                        "BLOQUEADAS_EM_G0": 0, "SEM_ITEM_NO_CORTE": 0}
    vistos_itens = set()
    for r in registos:
        ready = r["READY"]
        ref = CI.referencia_do_item(ready)
        chave = (str(ready.get("CORRIDA")), str(ready.get("ITEM_ID")))
        vistos_itens.add(chave)
        afs = idx.get(chave) or []
        if not afs:
            continue
        linha_item = do_item.get((str(ref["CORRIDA_UPSTREAM"]), str(ref["ITEM_ID"]))) or {}
        raw_sha = (raw.get(str(ready.get("RAW_OBSERVATION_ID"))) or {}).get("RAW_SHA256")
        texto = str(ready.get("TEXTO") or "")
        trechos = {}
        for af in afs:
            conta["RECEBIDAS"] += 1
            motivos = conferir(af, ready, raw_sha, texto)
            if motivos:
                conta["RECUSADAS"] += 1
                recusadas.append({"CLAIM_ID": (af or {}).get("CLAIM_ID", NAO_SEI), "ITEM_ID": ref["ITEM_ID"],
                                  "CORRIDA_UPSTREAM": ref["CORRIDA_UPSTREAM"], "MOTIVOS": motivos})
                continue
            passou, falta = portao_g0_da_afirmacao(af, ready, texto)
            dup = trechos.get(af.get("TRECHO_SHA256") or (af.get("EVIDENCE_SPAN") or {}).get("SHA256"))
            ft = _valor(af.get("FACT_TIME"))
            entrada = {
                "CLAIM_ID": af["CLAIM_ID"], "ITEM_ID": ref["ITEM_ID"],
                "RAW_OBSERVATION_ID": ref["RAW_OBSERVATION_ID"], "SOURCE_ID": ref["SOURCE_ID"],
                "CORRIDA_UPSTREAM": ref["CORRIDA_UPSTREAM"],
                "G0": PASSOU if passou and dup is None else BLOQUEADO,
                "G0_FALTA": falta + (["DUPLICATA_DO_TRECHO"] if dup else []),
                "G0_DA_AFIRMACAO": PASSOU if passou and dup is None else BLOQUEADO,
                "G0_DO_ITEM": linha_item.get("G0", NAO_SEI),
                "INTAKE": "ADMITIDO_NA_CORRIDA",
                "FACT_TIME": NAO_SEI if _ign(ft) else ft,
                "FACT_TIME_ORIGEM": (af.get("FACT_TIME_ROLE") or {}).get("ORIGEM", NAO_SEI),
                "CLAIM_KIND": _valor(af.get("CLAIM_KIND")) or NAO_SEI,
                "PUBLICATION_TIME": _valor(af.get("PUBLISHED_AT")) or NAO_SEI,
                "PUBLICATION_TIME_NAO_E_FACT_TIME": True,
                "PROVENIENCIA": "COMPLETA",
                "DUPLICATA_DE": dup,
                **_estado(af, passou and dup is None, falta),
            }
            livro["LINEAGE"].append(entrada)
            if dup is not None:
                conta["DUPLICADAS"] += 1
                continue
            trechos[af.get("TRECHO_SHA256") or (af.get("EVIDENCE_SPAN") or {}).get("SHA256")] = af["CLAIM_ID"]
            if not passou:
                conta["BLOQUEADAS_EM_G0"] += 1
                continue
            conta["PASSARAM_G0"] += 1
            lugar = af.get("FACT_LOCATION") if isinstance(af.get("FACT_LOCATION"), dict) else {}
            sinais.append({
                "SIGNAL_ID": "SG-" + hashlib.sha256((run_id + "|" + str(af["CLAIM_ID"])).encode()).hexdigest()[:16],
                "CLAIM_ID": af["CLAIM_ID"], "ITEM_ID": ref["ITEM_ID"], "SOURCE_ID": ref["SOURCE_ID"],
                "RAW_OBSERVATION_ID": ref["RAW_OBSERVATION_ID"], "CORRIDA_UPSTREAM": ref["CORRIDA_UPSTREAM"],
                "CLAIM_KIND": entrada["CLAIM_KIND"],
                "FACT_TIME": entrada["FACT_TIME"],
                "FACT_TIME_BASIS": (af.get("FACT_TIME") or {}).get("FACT_TIME_BASIS"),
                "FACT_TIME_ORIGEM": entrada["FACT_TIME_ORIGEM"],
                "FACT_TIME_PRECISION": (af.get("FACT_TIME") or {}).get("FACT_TIME_PRECISION", NAO_SEI),
                "FACT_LOCATION": NAO_SEI if _ign(lugar.get("VALOR")) else lugar["VALOR"],
                "LOCATION_SOURCE": lugar.get("LOCATION_SOURCE", NAO_SEI),
                "FACT_LOCATION_PRECISAO": lugar.get("PRECISAO", NAO_SEI),
                "FACT_LOCATION_TRECHO": lugar.get("TRECHO"),
                "EVIDENCE_SPAN": af.get("EVIDENCE_SPAN"),
                "ENTIDADES": af.get("ENTIDADES") or [],
                "USOS_BLOQUEADOS": entrada["USOS_BLOQUEADOS"],
                "ESTADO": "SINAL", "REGRA": "G0_DA_AFIRMACAO/v1",
            })
    conta["SEM_ITEM_NO_CORTE"] = sum(len(v) for k, v in idx.items() if k not in vistos_itens)
    livro["AFIRMACOES_RECUSADAS"] = recusadas
    livro["SINAIS_DAS_AFIRMACOES"] = sinais
    livro["INTAKE_DAS_AFIRMACOES"] = conta
    return conta
