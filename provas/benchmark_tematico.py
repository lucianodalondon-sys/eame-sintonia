#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RUNNER CEGO — baseline e candidatos, o mesmo corpus, o mesmo gate.

    python3 provas/benchmark_tematico.py --ensaio      (fixtures, sem corpus)
    python3 provas/benchmark_tematico.py --avaliar     (UMA vez, irreversivel)

    O RUNNER NAO SABE QUAL E O FAVORITO.
    Ele corre todos pela mesma ordem, com o mesmo adaptador, e entrega os
    numeros ao gate JA CONGELADO. Nao ha condicao nova para aprovar ninguem.

A IRREVERSIBILIDADE, DITA ANTES DE ACONTECER
---------------------------------------------
`--avaliar` abre o conjunto de avaliacao. Depois disso:

    EVALUATION_EXPOSED = YES

e nenhum candidato pode ser mexido com base no que se viu. Falhar aqui e
falhar a V1 — nao se faz V1.1 na mesma janela.
"""
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta import ingresso as ing  # noqa: E402


def _mod(nome, ficheiro):
    spec = importlib.util.spec_from_file_location(
        nome, os.path.join(RAIZ, "provas", ficheiro))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


gate = _mod("_gate_bm", "gate_de_aceitacao_tematica.py")
impl = _mod("_impl_bm", "implementacoes_candidatas.py")
espec = _mod("_espec_bm", "candidatos_tematicos.py")

GABARITO = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"
REGISTO = "data/derivados/REGISTO-DE-ARTEFATOS.json"
SAIDA = "data/derivados/BENCHMARK-TEMATICO-V1.json"
UNIVERSO = "T3"


def _json(c):
    with open(os.path.join(RAIZ, c), encoding="utf-8") as f:
        return json.load(f)


def sha_do_ficheiro(c):
    with open(os.path.join(RAIZ, c), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ══════════════════════════════════════════════════════════════════════════
# 1 · O BASELINE — a porta de hoje, chamada a serio
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ ELE NAO E CANDIDATO. Entra como CONTROLO, e entra INTACTO: a
# `admissao.decidir` real, a mesma que o orquestrador corre.
DA_FICHA = (ing.DO_COLETOR + ing.DA_FICHA_PARA_A_PORTA
            + ("FACT_TIME", "PUBLISHED_AT", "COLLECTED_AT"))


class Baseline:
    CANDIDATE_ID = "BASELINE-ADMISSION-ACTUAL"
    DETERMINISTICO = True

    def classificar(self, item):
        bruto = {k: v for k, v in (item.get("_ficha") or {}).items()
                 if k in DA_FICHA and v not in ing.NAO_E_AFIRMACAO}
        if item.get("_source_id") not in ing.NAO_E_AFIRMACAO:
            bruto.setdefault("SOURCE_ID", item["_source_id"])
        pronto = ing.para_a_porta(bruto)
        pronto["id"] = item.get("id")
        pronto["texto"] = item.get("texto") or ""
        return adm.decidir(pronto, UNIVERSO)


def mecanismos():
    """Baseline mais candidatos, por ordem alfabetica do id.

    A ORDEM NAO E DE PREFERENCIA. E alfabetica, de proposito, para o runner
    nao carregar uma opiniao dentro da sequencia.
    """
    fora = {Baseline.CANDIDATE_ID: Baseline()}
    for cid in sorted(impl.CANDIDATOS_VIVOS):
        fora[cid] = impl.CANDIDATOS_VIVOS[cid]()
    return dict(sorted(fora.items()))


# ══════════════════════════════════════════════════════════════════════════
# 2 · A CORRIDA
# ══════════════════════════════════════════════════════════════════════════
# As chaves de evidencia que o artefato guarda. `palavras` e `achado_noutro`
# sao as da porta de hoje; `termos`/`conceitos` sao as dos candidatos. Guardar
# a evidencia nao e decoracao: e ela que permite medir, mais abaixo, se uma
# decisao binaria assenta num casamento que a regra nao pretendia.
EVIDENCIA_QUE_VIAJA = ("palavras", "termos", "conceitos", "nomes", "andar",
                       "achado_noutro", "estagio", "negados")


def correr(mecanismo, itens):
    """Uma linha por item. A saida crua viaja intacta."""
    linhas = []
    for it in itens:
        try:
            d = mecanismo.classificar(it)
            cru, motivo, ev = d.resultado, d.motivo, d.evidencia
        except Exception as e:                              # noqa: BLE001
            cru, motivo, ev = adm.ERRO, "%s: %s" % (type(e).__name__, e), {}
        linhas.append({"DOC_SHA256": it["_sha"], "ITEM_ID": it["id"],
                       "RAW_OUTPUT": cru, "MOTIVO": motivo[:200],
                       "EVIDENCIA": {k: v for k, v in ev.items()
                                     if k in EVIDENCIA_QUE_VIAJA}})
    return linhas


def por_grupo(linhas, grupos, rotulos):
    """As previsoes agregadas por OBSERVACAO, com a regra do gate.

    Um grupo so tem previsao binaria quando TODOS os seus documentos deram a
    MESMA previsao binaria — a regra ja estava escrita no gate, e aqui ela e
    reusada, nao reinventada.
    """
    saco = {}
    for l in linhas:
        saco.setdefault(grupos[l["DOC_SHA256"]], []).append(l)
    fora = []
    for g, membros in sorted(saco.items()):
        previsoes = sorted({m["RAW_OUTPUT"] for m in membros})
        rot = {rotulos[m["DOC_SHA256"]] for m in membros}
        if len(rot) > 1:
            continue                      # grupo misto nao se colapsa
        fora.append({"GRUPO": g, "TAMANHO": len(membros),
                     "HUMAN_LABEL": rot.pop(), "PREVISOES": previsoes,
                     "ITEM_IDS": sorted(m["ITEM_ID"] for m in membros)})
    return fora


def metricas(grupos_lin, linhas, dependencia_substring):
    """Traduz para as metricas que o gate JA espera. Nenhuma inventada."""
    from fractions import Fraction
    pos = [g for g in grupos_lin if g["HUMAN_LABEL"] == "T3_SIM"]
    neg = [g for g in grupos_lin if g["HUMAN_LABEL"] == "T3_NAO"]

    def prev(g):
        return gate.previsao_do_grupo(g["PREVISOES"])

    tp = sum(1 for g in pos if prev(g) == "SIM")
    fn = sum(1 for g in pos if prev(g) == "NAO")
    tn = sum(1 for g in neg if prev(g) == "NAO")
    fp = sum(1 for g in neg if prev(g) == "SIM")
    total = len(grupos_lin)
    binarias = tp + fn + tn + fp
    passa = sum(1 for g in grupos_lin
                if prev(g) is not None
                and ((prev(g) == "SIM") == (g["HUMAN_LABEL"] == "T3_SIM")))
    erros = sum(1 for g in grupos_lin if "ERRO" in g["PREVISOES"])
    return {
        "POSITIVE_CAPTURE_RATE": Fraction(tp, len(pos)) if pos else Fraction(0),
        "EXPLICIT_FALSE_NEGATIVE": fn,
        "SPECIFICITY": Fraction(tn, len(neg)) if neg else Fraction(0),
        "PRECISION_T3": Fraction(tp, tp + fp) if (tp + fp) else Fraction(0),
        "DECISION_COVERAGE": Fraction(binarias, total),
        "GROUP_PASS_RATE": Fraction(passa, total),
        "ERROR": erros,
        # ⚠️ ISTO E MEDIDO, NAO DECLARADO. A primeira versao desta funcao
        # escrevia 0 porque «C1 e C2 casam por palavra inteira por
        # construcao». Verdade — e mesmo assim uma constante escrita a mao
        # nao mede nada, e o baseline passaria pelo mesmo caminho a receber
        # o mesmo zero.
        #
        #     UM NUMERO QUE NAO OLHOU PARA O DOCUMENTO
        #     NAO E UMA MEDICAO: E UMA OPINIAO COM CARA DE METRICA.
        "FALSE_SUBSTRING_OUTCOME_DEPENDENCY": len(dependencia_substring),
        "_DIAG": {"TP": tp, "FN": fn, "TN": tn, "FP": fp,
                  "GRUPOS": total, "POSITIVOS": len(pos),
                  "NEGATIVOS": len(neg), "BINARIAS": binarias,
                  "SEM_BINARIA": total - binarias, "PASSA": passa,
                  "SAIDAS": dict(Counter(l["RAW_OUTPUT"] for l in linhas)),
                  "DECISOES_SO_EM_CASAMENTO_FALSO": dependencia_substring},
    }


# ══════════════════════════════════════════════════════════════════════════
# 3 · O CASAMENTO QUE A REGRA NAO PRETENDIA — medido, por mecanismo
# ══════════════════════════════════════════════════════════════════════════
# O gate exige KNOWN_FALSE_SUBSTRING_OUTCOME_DEPENDENCY = 0, e exige-o de
# TODOS. Nao ha caminho curto para os candidatos: eles passam pela mesma sonda
# que apanhou `lancio` dentro de `bilancio` na baseline.
import re as _re  # noqa: E402  (so a sonda usa regex; os mecanismos tem o seu)

CHAVES_DE_TERMO = ("palavras", "termos", "conceitos", "nomes")


def _termos_da_linha(linha):
    """Os termos que o mecanismo DIZ terem produzido a decisao."""
    fora = []
    ev = linha.get("EVIDENCIA") or {}
    for k in CHAVES_DE_TERMO:
        fora += [str(t) for t in (ev.get(k) or [])]
    for _u, termos in (ev.get("achado_noutro") or {}).items():
        fora += [str(t) for t in termos]
    return fora


def _so_como_pedaco(termo, texto):
    """A palavra existe no texto, mas NUNCA sozinha."""
    t = termo.lower()
    if t not in texto:
        return False
    return not _re.search(r"(?<![a-zà-ÿ0-9])%s(?![a-zà-ÿ0-9])" % _re.escape(t),
                          texto)


def dependencia_de_casamento_falso(linhas, texto_por_sha):
    """Decisoes BINARIAS cujos termos TODOS so aparecem dentro de outra palavra.

    Uma decisao inteiramente assente num casamento falso esta certa por
    acidente quando bate com o humano. Dar-lhe credito seria premiar a moeda
    ao ar.
    """
    fora = []
    for l in linhas:
        if l["RAW_OUTPUT"] not in (adm.SIM, adm.NAO):
            continue
        termos = _termos_da_linha(l)
        if not termos:
            continue
        texto = (texto_por_sha.get(l["DOC_SHA256"]) or "").lower()
        falsos = [t for t in termos if _so_como_pedaco(t, texto)]
        if len(falsos) == len(termos):
            fora.append({"ITEM_ID": l["ITEM_ID"], "SAIDA": l["RAW_OUTPUT"],
                         "TERMOS": sorted(set(termos))[:8]})
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 4 · CARREGAR OS ITENS — o corpo inteiro, sem escolher trecho
# ══════════════════════════════════════════════════════════════════════════
class BenchmarkInvalido(Exception):
    pass


def _corpo(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return f.read().decode("utf-8", "replace")


def carregar_itens():
    """Um item por documento do gabarito, na mesma forma para TODOS.

    ⚠️ O item leva `_ficha` e `_source_id` porque a porta de hoje precisa
    deles para sequer chegar a pergunta tematica. Os candidatos recebem o
    MESMO dicionario e ha teste que prova que nenhum deles olha para esses
    campos — dar a mesma entrada a todos e o que torna a corrida comparavel;
    o que cada um LE e propriedade dele, e esta provada noutro sitio.
    """
    doc = _json(GABARITO)
    gt = doc["GROUND_TRUTH"]
    if len(gt) != 36:
        raise BenchmarkInvalido("o gabarito tem %d itens, nao 36" % len(gt))
    if doc.get("AUTO_LABELS_ASSIGNED") != 0:
        raise BenchmarkInvalido("o gabarito declara rotulos de maquina")
    reg = {a["STORAGE_LOCATION"]: a for a in _json(REGISTO)["ARTEFATOS"]}
    itens, rotulos = [], {}
    for x in sorted(gt, key=lambda y: y["ITEM_ID"]):
        ficha = reg.get(x["BODY_PATH"], {})
        itens.append({"id": ficha.get("ARTIFACT_ID") or x["ITEM_ID"],
                      "texto": _corpo(x["BODY_PATH"]),
                      "_sha": x["DOC_SHA256"], "_ficha": ficha,
                      "_source_id": x.get("SOURCE_ID")})
        rotulos[x["DOC_SHA256"]] = x["LABEL"]
    maus = set(rotulos.values()) - {"T3_SIM", "T3_NAO"}
    if maus:
        raise BenchmarkInvalido("rotulo fora do binario: %s" % sorted(maus))
    return doc, itens, rotulos


def agrupamento(doc):
    """O agrupamento vem do GABARITO. Nunca das previsoes.

    Reagrupar depois de ver o score e escolher o grupo que da jeito.
    """
    pares = doc.get("NEAR_DUPLICATES", {}).get("PARES")
    if pares is None:
        raise BenchmarkInvalido("o gabarito nao traz agrupamento canonico")
    pai = {x["DOC_SHA256"]: x["DOC_SHA256"] for x in doc["GROUND_TRUTH"]}

    def raiz(x):
        while pai[x] != x:
            x = pai[x]
        return x
    for p in pares:
        ra, rb = raiz(p["A"]), raiz(p["B"])
        if ra != rb:
            pai[ra] = rb
    return {s: raiz(s) for s in pai}


# ══════════════════════════════════════════════════════════════════════════
# 5 · O ENSAIO — provar o runner SEM abrir o conjunto de avaliacao
# ══════════════════════════════════════════════════════════════════════════
# O gate diz RUNNER_TESTED = YES antes de EVALUATION_EXPOSED = YES. A ordem
# nao e burocracia: um runner por testar transforma um defeito de encanamento
# na reprovacao de um candidato, e a corrida cega so acontece uma vez.
#
#     UM ERRO NO RUNNER SO E BARATO ENQUANTO O CORPUS ESTA FECHADO.
ENSAIO = [
    # (id, texto, rotulo de mentira, grupo de mentira)
    ("e1", "Monitoraggio di Lobesia botrana e Plasmopara viticola su vite",
     "T3_SIM", "g1"),
    ("e2", "Segnalazione di Lobesia botrana e Plasmopara viticola nel vigneto",
     "T3_SIM", "g1"),
    ("e3", "Erwinia amylovora e Venturia inaequalis nei frutteti",
     "T3_SIM", "g2"),
    ("e4", "Bilancio di previsione e rendiconto finanziario dell ente",
     "T3_NAO", "g3"),
    ("e5", "", "T3_NAO", "g4"),
]


def itens_de_ensaio():
    itens, rotulos, grupos = [], {}, {}
    for i, (iid, texto, rot, g) in enumerate(ENSAIO):
        sha = hashlib.sha256(("ensaio/%s" % iid).encode()).hexdigest()
        itens.append({"id": iid, "texto": texto, "_sha": sha,
                      "_ficha": {}, "_source_id": None})
        rotulos[sha], grupos[sha] = rot, g
    return itens, rotulos, grupos


def ensaio():
    """Corre tudo em fixtures e verifica as PROPRIEDADES do runner.

    Nao verifica quem ganha — em cinco frases inventadas isso nao significaria
    nada. Verifica que o encanamento existe e nao mente.
    """
    itens, rotulos, grupos = itens_de_ensaio()
    textos = {i["_sha"]: i["texto"] for i in itens}
    falhas = []
    todos = mecanismos()
    if Baseline.CANDIDATE_ID not in todos:
        falhas.append("o baseline nao entrou na corrida")
    for f in espec.CANDIDATOS:
        cid = f["CANDIDATE_ID"]
        if cid in impl.CANDIDATOS_VIVOS and cid not in todos:
            falhas.append("%s esta implementado e nao entrou na corrida" % cid)
    for cid, m in todos.items():
        linhas = correr(m, itens)
        if len(linhas) != len(itens):
            falhas.append("%s devolveu %d linhas para %d itens"
                          % (cid, len(linhas), len(itens)))
        fora = {l["RAW_OUTPUT"] for l in linhas} - set(adm.RESULTADOS)
        if fora:
            falhas.append("%s falou fora da lingua da porta: %s"
                          % (cid, sorted(fora)))
        # determinismo: a mesma entrada duas vezes, a mesma saida
        if getattr(m, "DETERMINISTICO", False):
            de_novo = correr(m, itens)
            if [l["RAW_OUTPUT"] for l in de_novo] != [l["RAW_OUTPUT"]
                                                      for l in linhas]:
                falhas.append("%s diz-se deterministico e mudou de resposta"
                              % cid)
        gl = por_grupo(linhas, grupos, rotulos)
        if len(gl) != len({grupos[i["_sha"]] for i in itens}):
            falhas.append("%s perdeu grupos na agregacao" % cid)
        dep = dependencia_de_casamento_falso(linhas, textos)
        met = metricas(gl, linhas, dep)
        em_falta = [n for n, _o, _l in gate.CONDICOES if n not in met]
        if em_falta:
            falhas.append("faltam metricas que o gate exige: %s" % em_falta)
        try:
            gate.avaliar_gate(met)
        except gate.MetricaEmFalta as e:
            falhas.append("o gate recusou as metricas de %s: %s" % (cid, e))
    # O ensaio tem de conseguir apanhar o defeito historico: `bilancio`
    # contem `lancio`, e um mecanismo de substring cru acenderia nele.
    marca = dependencia_de_casamento_falso(
        [{"RAW_OUTPUT": adm.SIM, "ITEM_ID": "e4", "DOC_SHA256":
          itens[3]["_sha"], "EVIDENCIA": {"palavras": ["lancio"]}}], textos)
    if len(marca) != 1:
        falhas.append("a sonda de casamento falso nao apanha `lancio` em "
                      "`bilancio` — ela esta cega e mediria zero sempre")
    return falhas


# ══════════════════════════════════════════════════════════════════════════
# 6 · A AVALIACAO CEGA — uma vez, e ja nao se desfaz
# ══════════════════════════════════════════════════════════════════════════
def _veredito(cid, met, resultado_do_gate, disponivel):
    """PASS / FAIL / BLOCKED. Nao existe «quase passou».

    Um candidato que nao pode correr neste ambiente nao e um reprovado: e um
    NAO MEDIDO. Chamar-lhe FAIL seria transformar a falta do ambiente em
    julgamento sobre a hipotese — e ela continua por testar.
    """
    if not disponivel:
        return "BLOCKED_NOT_RUNNABLE_IN_THIS_ENVIRONMENT"
    return "PASS" if resultado_do_gate["VEREDICTO"] == "PASS" else "FAIL"


def avaliar():
    doc, itens, rotulos = carregar_itens()
    grupos = agrupamento(doc)
    textos = {i["_sha"]: i["texto"] for i in itens}
    todos = mecanismos()
    fora = []
    for cid, m in todos.items():
        disponivel = (m.disponivel() if hasattr(m, "disponivel") else True)
        linhas = correr(m, itens)
        gl = por_grupo(linhas, grupos, rotulos)
        dep = dependencia_de_casamento_falso(linhas, textos)
        met = metricas(gl, linhas, dep)
        resultado = gate.avaliar_gate({k: v for k, v in met.items()
                                       if not k.startswith("_")})
        if not disponivel:
            # ⚠️ UM MECANISMO QUE NAO CORREU NAO TEM METRICAS — TEM SINTOMAS
            # DO AMBIENTE. Sem credencial, C3 devolve 36 ERRO, e o gate
            # calcula obedientemente «6 de 8 condicoes em falha». Esse numero
            # nao mede a hipotese: mede a falta da chave.
            #
            #     GUARDAR O NUMERO AO LADO DA PALAVRA «BLOCKED»
            #     E DEIXAR A PALAVRA PARA QUEM LER O RODAPE.
            #
            # Este defeito apareceu ao ESCREVER O RELATO — a tabela pos C3 a
            # reprovar em seis condicoes e a dizer-lhe BLOCKED na mesma linha.
            resultado = {
                "NOT_MEASURED": "YES",
                "PORQUE": ("o mecanismo nao corre neste ambiente; qualquer "
                           "metrica aqui seria um retrato da credencial em "
                           "falta e nao do mecanismo"),
                "THEMATIC_GATE_PASS": False,
                "GATE_NAO_FOI_APLICADO": (
                    "e nao foi aplicado de proposito: aplicar um gate a uma "
                    "corrida que nao aconteceu produz um FAIL com cara de "
                    "julgamento"),
            }
            met = {"_DIAG": {"NOT_MEASURED": "YES",
                             "SAIDAS": met["_DIAG"]["SAIDAS"]}}
        fora.append({
            "CANDIDATE_ID": cid,
            "PAPEL": ("CONTROL" if cid == Baseline.CANDIDATE_ID
                      else "CANDIDATE"),
            "RUNNABLE_HERE": "YES" if disponivel else "NO",
            "VEREDITO": _veredito(cid, met, resultado, disponivel),
            "GATE": resultado,
            "METRICAS": {k: _leg(v) for k, v in met.items()
                         if not k.startswith("_")} or "NOT_MEASURED",
            "DIAGNOSTICO": met["_DIAG"],
            "LINHAS": linhas,
            "GRUPOS": gl,
        })
    return doc, fora


def _leg(v):
    """Fraccao legivel sem perder o valor exacto."""
    from fractions import Fraction
    if isinstance(v, Fraction):
        return {"FRACAO": "%d/%d" % (v.numerator, v.denominator),
                "DECIMAL": round(float(v), 4)}
    return v


def artefato(doc, resultados):
    vencedores = [r["CANDIDATE_ID"] for r in resultados
                  if r["PAPEL"] == "CANDIDATE" and r["VEREDITO"] == "PASS"]
    bloqueados = [r["CANDIDATE_ID"] for r in resultados
                  if r["VEREDITO"].startswith("BLOCKED")]
    return {
        "SCHEMA": "sintonia.thematic-benchmark/1",
        "O_QUE_ISTO_E": (
            "Uma corrida cega: a porta de hoje como CONTROLO e os candidatos "
            "congelados, sobre o mesmo gabarito, contra o mesmo gate ja "
            "congelado. Nenhum limiar foi tocado para este resultado."),
        "UNIVERSE": UNIVERSO,
        "EVALUATION_EXPOSED": "YES",
        "O_QUE_EXPOSED_SIGNIFICA": (
            "O conjunto de avaliacao foi aberto e os resultados individuais "
            "foram vistos. A partir daqui nenhum parametro de nenhum "
            "candidato pode mudar com base neles: seria treinar no conjunto "
            "de avaliacao com outro nome."),
        "CANDIDATE_SET_VERSION": espec.CANDIDATE_SET_VERSION,
        "CANDIDATE_SET_SHA256": espec.impressao_do_conjunto(espec.CANDIDATOS),
        "GATE_SHA256": sha_do_ficheiro(
            "provas/gate_de_aceitacao_tematica.py"),
        "IMPLEMENTATIONS_SHA256": sha_do_ficheiro(
            "provas/implementacoes_candidatas.py"),
        "GROUND_TRUTH_SHA256": sha_do_ficheiro(GABARITO),
        "GATE_THRESHOLD_CHANGED": "NO",
        "GROUND_TRUTH_CHANGED": "NO",
        "TRAINING_ON_EVALUATION_SET": "NO",
        "ADMISSION_CHANGED": "NO",
        "O_QUE_ISTO_NAO_AUTORIZA": (
            "Nada entra em producao por causa deste ficheiro. Um PASS aqui e "
            "um PASS de AVALIACAO; a porta continua a ser a de hoje ate uma "
            "decisao explicita, escrita no diario."),
        "RUN_ORDER": [r["CANDIDATE_ID"] for r in resultados],
        "A_ORDEM_E_ALFABETICA": (
            "e nao de preferencia — o runner nao carrega um favorito."),
        "WINNER": vencedores[0] if len(vencedores) == 1 else (
            "NONE" if not vencedores else "AMBIGUOUS_MULTIPLE_PASS"),
        "WINNERS": vencedores,
        "NONE_E_RESULTADO": (
            "Se nenhum candidato passa, o resultado e NONE e nao «o melhor "
            "dos que correram». O gate nao tem segundo lugar."),
        "BLOCKED": bloqueados,
        "BLOCKED_NAO_E_FAIL": (
            "Um candidato que nao pode correr neste ambiente fica por "
            "testar. Nao reprovou: nao foi medido."),
        "RESULTS": [{k: v for k, v in r.items() if k != "LINHAS"}
                    for r in resultados],
        "RAW_LINES": {r["CANDIDATE_ID"]: r["LINHAS"] for r in resultados},
        "GENERATED_BY": "provas/benchmark_tematico.py --avaliar",
    }


# ══════════════════════════════════════════════════════════════════════════
# 7 · O RELATO
# ══════════════════════════════════════════════════════════════════════════
def relatar(art):
    print("\n  BENCHMARK TEMATICO T3 — corrida cega")
    print("  " + "─" * 66)
    print("  gabarito ....... %s" % art["GROUND_TRUTH_SHA256"][:16])
    print("  conjunto ....... %s  (%s)" % (art["CANDIDATE_SET_SHA256"][:16],
                                           art["CANDIDATE_SET_VERSION"]))
    print("  gate ........... %s  ·  GATE_THRESHOLD_CHANGED = %s"
          % (art["GATE_SHA256"][:16], art["GATE_THRESHOLD_CHANGED"]))
    print("  ordem .......... %s" % ", ".join(art["RUN_ORDER"]))
    for r in art["RESULTS"]:
        d = r["DIAGNOSTICO"]
        print("\n  %-28s %-10s %s" % (r["CANDIDATE_ID"], r["PAPEL"],
                                      r["VEREDITO"]))
        if r["RUNNABLE_HERE"] == "NO":
            print("      nao corre neste ambiente — por testar, nao reprovado")
            print("      gate NAO aplicado: sem corrida nao ha o que medir")
            continue
        print("      TP %-3d FN %-3d TN %-3d FP %-3d   sem previsao binaria: %d"
              % (d["TP"], d["FN"], d["TN"], d["FP"], d["SEM_BINARIA"]))
        print("      saidas cruas: %s" % d["SAIDAS"])
        for l in r["GATE"]["LINHAS"]:
            print("      %s %-46s %s %s  (medido %s)"
                  % ("·" if l["PASSA"] else "✗", l["CONDICAO"],
                     l["OPERADOR"], l["LIMIAR"], l["MEDIDO"]))
    print("\n  " + "─" * 66)
    print("  WINNER = %s" % art["WINNER"])
    if art["BLOCKED"]:
        print("  BLOCKED = %s" % ", ".join(art["BLOCKED"]))
    print("  ADMISSION_CHANGED = %s  ·  GROUND_TRUTH_CHANGED = %s"
          % (art["ADMISSION_CHANGED"], art["GROUND_TRUTH_CHANGED"]))
    print()


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "--ensaio"
    if modo == "--ensaio":
        falhas = ensaio()
        for f in falhas:
            print("  ✗ %s" % f)
        print("\n  RUNNER_TESTED = %s   (%d mecanismos, %d fixtures)"
              % ("YES" if not falhas else "NO", len(mecanismos()), len(ENSAIO)))
        print("  EVALUATION_EXPOSED = NO — o ensaio nao abriu o gabarito.\n")
        return 0 if not falhas else 1
    if modo == "--avaliar":
        doc, resultados = avaliar()
        art = artefato(doc, resultados)
        caminho = os.path.join(RAIZ, SAIDA)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(art, f, ensure_ascii=False, indent=2, sort_keys=False)
            f.write("\n")
        relatar(art)
        print("  escrito: %s\n" % SAIDA)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
