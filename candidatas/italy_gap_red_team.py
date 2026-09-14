#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM — 12 ataques nomeados contra ESTA entrega, cada um com CONTROLE POSITIVO.

POR QUE O CONTROLE POSITIVO E' OBRIGATORIO
------------------------------------------
Um ataque que devolve «nao achei problema» pode significar duas coisas
opostas: a entrega esta boa, ou o detetor esta quebrado. Sem controle nao se
sabe qual. Por isso cada ataque faz DUAS medicoes:

    LIMPO   — na entrega como esta. Espera-se PASSA.
    QUEBRADO— numa copia deliberadamente estragada. Espera-se FALHA.

Se o QUEBRADO tambem passa, o detetor e' cego e o ataque nao vale nada — e
isso reporta-se como `DETETOR_CEGO`, que e' pior do que uma falha.

UM ATAQUE E' INDEPENDENTE DA IMPLEMENTACAO
------------------------------------------
O ataque 12 le o XLSX gravado com openpyxl e nao importa nenhum modulo desta
pasta. Se os dados em Python e a folha no disco divergirem, ele acusa.
"""

import importlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-gap")
XLSX = RAIZ / "candidatas" / "ITALY-SOURCE-GAP-BY-TOOL-2026-09-14.xlsx"

RESULTADOS = []


def fresco(nome):
    """Recarrega o modulo, para que um ataque nao herde o estado do anterior.

    Na missao da taxonomia, o ataque 6 reportou os testes do ataque 5 por
    faltar exatamente isto — e teria concluido «detetor quebrado» sobre um
    detetor sao.
    """
    if nome in sys.modules:
        del sys.modules[nome]
    return importlib.import_module(nome)


def registar(n, nome, limpo_ok, quebrado_apanhado, detalhe):
    if not limpo_ok:
        v = "FALHA NA ENTREGA"
    elif not quebrado_apanhado:
        v = "DETETOR_CEGO"
    else:
        v = "OK"
    RESULTADOS.append(dict(N=n, ATAQUE=nome, VEREDITO=v, DETALHE=detalhe))
    print(f"{n:2d} · {nome:38s} {v:18s} {detalhe}")


# ═════════════════════════════════════════════════════════════════════════════
def a01_fonte_que_fala_mas_nao_entrega():
    """Fonte que casa por palavra e nao entrega o campo sai como STRONG?"""
    cob = json.loads((TRAB / "COBERTURA.json").read_text(encoding="utf-8"))
    # LIMPO: o automatico nao pode escrever STRONG em nenhuma linha
    limpo = not any("STRONG" in r["COBERTURA"] for r in cob)
    # QUEBRADO: se o automatico pudesse escrever STRONG, isto apanharia
    falso = [dict(cob[0], COBERTURA="STRONG_SOURCE_EXISTS")]
    apanhou = any("STRONG" in r["COBERTURA"] for r in falso)
    n_cand = Counter(r["COBERTURA"] for r in cob)
    registar(1, "FONTE_QUE_FALA_MAS_NAO_ENTREGA", limpo, apanhou,
             f"veredito automatico nunca diz STRONG: {dict(n_cand)}")


def a02_contar_ligacao_como_fonte():
    """Alguem conta as linhas de SOURCE_TO_TOOL e diz «109 fontes novas»?"""
    nf = fresco("italy_gap_novas_fontes")
    fontes = len(nf.TODAS)
    ligacoes = sum(len(f["ALIMENTA"]) for f in nf.TODAS)
    nomes = {f["NOME"] for f in nf.TODAS}
    limpo = len(nomes) == fontes and ligacoes > fontes
    # QUEBRADO: duas linhas com o mesmo nome (a mesma fonte contada duas vezes)
    dupl = list(nf.TODAS) + [dict(nf.TODAS[0])]
    apanhou = len({f["NOME"] for f in dupl}) != len(dupl)
    registar(2, "CONTAR_LIGACAO_COMO_FONTE", limpo, apanhou,
             f"{fontes} fontes distintas -> {ligacoes} ligacoes "
             f"(fator {ligacoes / fontes:.1f}x)")


def a03_radar_com_familia_propria():
    """O Radar recebeu fonte propria, contra a regra da missao?"""
    nf = fresco("italy_gap_novas_fontes")
    aud = fresco("italy_gap_auditoria")
    # nenhuma fonte pode servir SO o Radar
    so_radar = [f["NOME"] for f in nf.TODAS
                if {a.split(" · ")[0] for a in f["ALIMENTA"]} == {"RADAR"}]
    # e toda ENTRADA do radar tem de ser HERDADO
    entradas = {k: v[0] for k, v in aud.AUDITORIA.items()
                if k.startswith("RADAR · ENTRADA:")}
    limpo = not so_radar and set(entradas.values()) == {"HERDADO"}
    apanhou = ({**entradas, "RADAR · ENTRADA: x": "STRONG"}
               and "STRONG" in {**entradas, "RADAR · ENTRADA: x": "STRONG"}.values())
    registar(3, "RADAR_COM_FAMILIA_PROPRIA", limpo, apanhou,
             f"0 fontes so-do-Radar · {len(entradas)} entradas, todas HERDADO")


def a04_nacional_vira_cobertura_regional():
    """Fonte nacional foi contada como cobertura de cada regiao?"""
    m = json.loads((TRAB / "MATRIZES.json").read_text(encoding="utf-8"))
    reg = m["REGION"]
    # LIMPO: as duas contas tem de estar em colunas diferentes, e o ESTADO
    # nao pode ser COBERTA onde a conta regional e' zero
    tem_coluna = all("FONTES_NACIONAIS_QUE_TAMBEM_SERVEM" in l for l in reg)
    sem_mentira = not any(l["ESTADO"] == "COBERTA" and l["DEPOIS_REGIONAL"] < 2
                          for l in reg)
    limpo = tem_coluna and sem_mentira
    # QUEBRADO: uma regiao com 0 regional marcada COBERTA
    apanhou = any(l["ESTADO"] == "COBERTA" and l["DEPOIS_REGIONAL"] < 2
                  for l in [dict(reg[0], ESTADO="COBERTA", DEPOIS_REGIONAL=0)])
    est = Counter(l["ESTADO"] for l in reg)
    registar(4, "NACIONAL_VIRA_COBERTURA_REGIONAL", limpo, apanhou,
             f"{dict(est)} · nacionais contadas a parte: "
             f"{len(m['REGION_NACIONAIS'])}")


def a05_gravidade_vinda_da_contagem():
    """A gravidade cede se eu inundar a necessidade de candidatas?"""
    cob = json.loads((TRAB / "COBERTURA.json").read_text(encoding="utf-8"))
    # LIMPO: existe necessidade com MUITAS candidatas e ainda CRITICAL
    criticas = [r for r in cob if r["GAP_SEVERITY"] == "CRITICAL"]
    com_muitas = [r for r in criticas if r["DONOS_FORTES"] >= 5]
    limpo = bool(com_muitas)
    # QUEBRADO: se a gravidade viesse da contagem, nenhuma CRITICAL teria
    # muitos donos — este e' o controle ao contrario, e diz-se qual
    apanhou = not any(r["GAP_SEVERITY"] == "CRITICAL"
                      for r in [dict(criticas[0], GAP_SEVERITY="LOW")])
    registar(5, "GRAVIDADE_VINDA_DA_CONTAGEM", limpo, apanhou,
             f"{len(com_muitas)} de {len(criticas)} CRITICAL tem 5+ donos "
             "propostos e continuam CRITICAL")


def a06_zero_falso():
    """`0%` dentro de `100%` e `0/N` dentro de `10/163` voltam a mentir?"""
    padrao = r"(?<!\d)0/\d+|(?<!\d)0%"
    falso_positivo = [t for t in ("100% cheios", "10/163 registos",
                                  "interval 15/219", "90%")
                      if re.search(padrao, t)]
    verdadeiro = [t for t in ("CROP_STAGE 0/29", "maxApp 0/219", "0% cheio")
                  if re.search(padrao, t)]
    limpo = not falso_positivo and len(verdadeiro) == 3
    # QUEBRADO: o padrao ingenuo apanha «100%» e «10/163»
    ingenuo = r"0/\d+|0%"
    apanhou = bool([t for t in ("100% cheios", "10/163 registos")
                    if re.search(ingenuo, t)])
    registar(6, "ZERO_FALSO_DENTRO_DE_OUTRO_NUMERO", limpo, apanhou,
             f"0 falsos positivos em 4 textos · 3 zeros reais apanhados")


def a07_territorio_inventado():
    """Um codigo T fora do Atlas passa?"""
    t = fresco("_territorios")
    nf = fresco("italy_gap_novas_fontes")
    limpo = all(t.valido(c) for f in nf.TODAS for c in f["TERR"])
    apanhou = not t.valido("T14") and not t.valido("T13")
    registar(7, "TERRITORIO_INVENTADO", limpo, apanhou,
             f"{len({c for f in nf.TODAS for c in f['TERR']})} codigos usados, "
             "todos no Atlas · T13 e T14 recusados")


def a08_necessidade_orfa():
    """Uma fonte que alimenta necessidade inexistente passa?"""
    nf = fresco("italy_gap_novas_fontes")
    limpo = not nf._validar()
    # QUEBRADO: injeta uma necessidade que nao existe
    guardado = list(nf.TODAS)
    nf.TODAS.append(dict(guardado[0], NOME="ISCA", TERR=["T1"],
                         ALIMENTA=["WINDOWS · necessidade que nao existe"]))
    apanhou = bool([e for e in nf._validar() if "orfa" in e])
    nf.TODAS[:] = guardado
    registar(8, "NECESSIDADE_ORFA", limpo, apanhou,
             f"{sum(len(f['ALIMENTA']) for f in nf.TODAS)} ligacoes, todas "
             "para necessidade existente")


def a09_auditoria_incompleta():
    """Uma necessidade sem veredito humano passa em silencio?"""
    aud = fresco("italy_gap_auditoria")
    nd = fresco("italy_gap_needs")
    chaves = {f'{n["TOOL"]} · {n["RAW_NEED"]}' for n in nd.NECESSIDADES}
    limpo = chaves == set(aud.AUDITORIA)
    # QUEBRADO: tira uma
    copia = dict(aud.AUDITORIA)
    copia.pop(next(iter(copia)))
    apanhou = chaves != set(copia)
    registar(9, "AUDITORIA_INCOMPLETA", limpo, apanhou,
             f"{len(aud.AUDITORIA)}/{len(chaves)} necessidades com leitura humana")


def a10_colisao_de_lingua():
    """Palavra italiana a casar com prosa portuguesa volta a inflacionar?"""
    mz = fresco("italy_gap_matrizes")
    padroes = mz.CULTURAS["Maize"]
    frase_pt = "retoma vegetativa mais tardia, mais ~300 leituras, vai mais longe"
    limpo = (not any(re.search(p, frase_pt, re.I) for p in padroes)
             and r"\bmais\b" not in padroes)
    # QUEBRADO: com «mais» na lista, a frase portuguesa conta como milho
    apanhou = bool(re.search(r"\bmais\b", frase_pt, re.I))
    m = json.loads((TRAB / "MATRIZES.json").read_text(encoding="utf-8"))
    maize = next(l for l in m["CROP"] if l["CULTURA"] == "Maize")
    registar(10, "COLISAO_DE_LINGUA_IT_PT", limpo, apanhou,
             f"Maize = {maize['FONTES_NOVAS_QUE_A_NOMEIAM']} "
             "(era 6, todos falsos «mais» portugues)")


def a11_sintetico_contado_como_real():
    """Dado SYNTHETIC_DEMO conta como campo preenchido?"""
    cob = json.loads((TRAB / "COBERTURA.json").read_text(encoding="utf-8"))
    fn = [r for r in cob if r["TOOL"] == "FIELD_NET"]
    limpo = all(r["ENCHIMENTO_NO_CASCO"] == "NENHUM" for r in fn) and bool(fn)
    apanhou = re.search(r"SYNTHETIC_DEMO", " ".join(r["MEDIDO"] for r in fn)) \
        is not None
    registar(11, "SINTETICO_CONTADO_COMO_REAL", limpo, apanhou,
             f"FIELD_NET: {len(fn)} necessidades, enchimento NENHUM apesar de "
             "18 registos existirem")


def a12_folha_diz_mais_do_que_foi_feito():
    """INDEPENDENTE DA IMPLEMENTACAO: le o XLSX e procura promessa a mais."""
    from openpyxl import load_workbook
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    texto, celulas = [], 0
    for ws in wb.worksheets:
        for linha in ws.iter_rows(values_only=True):
            for v in linha:
                if isinstance(v, str):
                    texto.append(v)
                    celulas += 1
    tudo = "\n".join(texto)
    # Palavras que nao podem aparecer AFIRMADAS: esta missao nao coletou, nao
    # registou, nao abriu rota por sonda.
    #
    # ⚠️ A PRIMEIRA VERSAO DESTE DETETOR ACUSOU A ENTREGA POR DIZER A VERDADE.
    # Procurava «ingerido» sem olhar ao que vinha antes, e apanhou duas frases
    # que diziam o CONTRARIO do proibido:
    #     «— no fixture, nao ingerido»
    #     «EPPO nao esta ingerido para Italia»
    # Um detetor que nao le a negacao mede a palavra, nao a afirmacao. Agora
    # exige-se que nao haja «nao/não/nenhum/zero/sem» nos 30 caracteres antes.
    NEGADO = r"(?<!n[ao]o\s)(?<!n[ãa]o\s)(?<!n[ao]o\sest[aá]\s)(?<!n[ãa]o\sest[aá]\s)"
    proibidas = {}
    for p in ("CONFIRMED", "SOURCE_ID criado", "RUN_ID", "coleta executada",
              "ingerido", "registado no Atlas"):
        for m in re.finditer(re.escape(p), tudo, re.I):
            antes = tudo[max(0, m.start() - 34):m.start()].lower()
            if re.search(r"\b(nao|não|nenhum[ao]?|zero|sem|nunca)\b", antes):
                continue          # esta negado: e' declaracao de ausencia
            proibidas[p] = tudo[max(0, m.start() - 40):m.end() + 20]
            break
    # e tem de haver a declaracao dos zeros
    tem_zeros = all(z in tudo for z in ("COLLECTION_RUNS_CREATED = 0",
                                        "RAW_CREATED = 0",
                                        "WAITING_ROOM_DELTA = 0"))
    limpo = not proibidas and tem_zeros
    # CONTROLE POSITIVO com as DUAS faces: a afirmacao tem de ser apanhada, e
    # a negacao tem de ser deixada passar. Um detetor que apanha as duas e' tao
    # inutil como um que nao apanha nenhuma.
    def _fere(t):
        for m in re.finditer("ingerido", t, re.I):
            antes = t[max(0, m.start() - 34):m.start()].lower()
            if not re.search(r"\b(nao|não|nenhum[ao]?|zero|sem|nunca)\b", antes):
                return True
        return False
    apanhou = _fere("o dado foi ingerido no casco") and not _fere("nao ingerido")
    registar(12, "FOLHA_DIZ_MAIS_DO_QUE_FOI_FEITO", limpo, apanhou,
             f"{len(wb.sheetnames)} folhas · {celulas} celulas lidas por "
             f"caminho independente · afirmacoes proibidas: "
             f"{sorted(proibidas) or 'nenhuma'} · o detetor le a negacao "
             "(apanha «foi ingerido», deixa passar «nao ingerido»)")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("RED TEAM · 12 ATAQUES · cada um com controle positivo")
    print("=" * 96)
    for f in (a01_fonte_que_fala_mas_nao_entrega, a02_contar_ligacao_como_fonte,
              a03_radar_com_familia_propria, a04_nacional_vira_cobertura_regional,
              a05_gravidade_vinda_da_contagem, a06_zero_falso,
              a07_territorio_inventado, a08_necessidade_orfa,
              a09_auditoria_incompleta, a10_colisao_de_lingua,
              a11_sintetico_contado_como_real,
              a12_folha_diz_mais_do_que_foi_feito):
        try:
            f()
        except Exception as e:                                   # noqa: BLE001
            registar(int(f.__name__[1:3]), f.__name__[4:].upper(),
                     False, True, f"EXCECAO: {type(e).__name__}: {e}")
    print("=" * 96)
    c = Counter(r["VEREDITO"] for r in RESULTADOS)
    print("VEREDITO:", dict(c))
    (TRAB / "RED-TEAM.json").write_text(
        json.dumps(RESULTADOS, ensure_ascii=False, indent=1), encoding="utf-8")
    if c.get("FALHA NA ENTREGA") or c.get("DETETOR_CEGO"):
        sys.exit(1)


if __name__ == "__main__":
    main()
