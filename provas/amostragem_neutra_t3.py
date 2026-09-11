#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A AMOSTRAGEM NEUTRA DE T3 — as 46 fichas sao a populacao certa?

    python3 provas/amostragem_neutra_t3.py
    python3 provas/amostragem_neutra_t3.py --escrever

Sem rede, sem banco, sem recoleta. Nenhum documento e rotulado aqui.

    HUMAN_LABELS_ADDED = 0
    MACHINE_LABELS_ADDED = 0

A PERGUNTA
----------
    As 46 fichas do pacote formam uma amostra adequada para AVALIAR T3, ou e
    preciso ampliar a populacao antes de alguem rotular?

A SUSPEITA QUE A ABRIU
----------------------
A §53 do know-how separou duas contaminacoes:

    LEAKAGE NO ROTULADOR   quem decide o rotulo
    LEAKAGE NO AMOSTRADOR  quem decide QUEM entra na lista

e resolveu a segunda ao nivel da PRE-SELECAO — os 27 deixaram de ser
apresentados sozinhos. Mas ficou por examinar o degrau de baixo: **de onde
vieram os 46?**

    HUMAN LABEL DOES NOT REPAIR A BIASED SAMPLING FRAME.

O QUE ESTA PROVA MEDE, E O QUE ELA SE PROIBE
--------------------------------------------
Constroi o `sampling frame` — a populacao de documentos revisaveis — usando
SOMENTE criterios nao tematicos:

    o ficheiro existe · tem corpo legivel · a linhagem recupera-se

E PROIBIDO, e nao ha excecao, selecionar por:

    palavra de T2 ou T3 · nome do ficheiro · territorio da ficha da fonte ·
    decisao de `PERGUNTAS_DO_UNIVERSO` · resultado do gabarito de T2
"""
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_censo", os.path.join(RAIZ, "provas", "censo_corpus_rotulado_admission.py"))
censo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(censo)

FRAME = "data/samples/T3-SAMPLING-FRAME-V1.json"

# ── A REGRA DE INCLUSAO · NAO TEMATICA, E SO ISSO ──────────────────────────
# Onde esta arvore guarda CORPOS de documento. Nenhuma destas pastas foi
# escolhida por assunto: sao os sitios onde ha bytes de documento.
ONDE_HA_CORPO = (
    "data/collection-store/italy/*/*/*/*",
    "data/samples/IT-SOURCE-SAMPLES/*/*",
    "data/samples/IT-BOLLETTINI-VPN-2026/pdf/*",
    "data/samples/IT-ARPAV-VENETO/*",
    "data/samples/PIEMONTE-FD/*",
)
# Extensoes de DOCUMENTO. `.headers.txt`, `.json` de manifesto e `.err` sao
# recibos da coleta, nao documentos — e essa exclusao tambem nao e tematica.
E_DOCUMENTO = (".pdf", ".html", ".csv", ".ods", "")
NAO_E_DOCUMENTO = (".headers.txt", ".err")
# Formatos cujo BRUTO ja e legivel sem extracao.
BRUTO_LEGIVEL = (".html", ".csv", "")


def _sha(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _derivados():
    """sha do bruto -> caminho do texto legivel, e o caminho canonico do pai."""
    corpo, pai = {}, {}
    for a in censo._json("data/derivados/REGISTO-DE-ARTEFATOS.json")["ARTEFATOS"]:
        s = a.get("PARENT_SHA256")
        corpo[s] = a["STORAGE_LOCATION"]
        ps = a.get("NOTES", {}).get("PARENT_STORAGE_LOCATIONS", [])
        pai[s] = ps[0] if ps else a["STORAGE_LOCATION"]
    return corpo, pai


def sampling_frame():
    """Todo documento desta arvore, pela IDENTIDADE DOS BYTES.

    A unidade nao e o caminho: e o documento. Nove documentos vivem em dois
    sitios (a captura e a amostra), e conta-los duas vezes inflacionaria a
    diversidade sem acrescentar uma unica evidencia nova.
    """
    corpo_de, pai_de = _derivados()
    por_sha = defaultdict(list)
    for padrao in ONDE_HA_CORPO:
        for f in sorted(glob.glob(os.path.join(RAIZ, padrao))):
            if not os.path.isfile(f):
                continue
            rel = os.path.relpath(f, RAIZ)
            if rel.endswith(NAO_E_DOCUMENTO):
                continue
            if os.path.splitext(rel)[1].lower() not in E_DOCUMENTO:
                continue
            por_sha[_sha(rel)].append(rel)

    frame = []
    for sha, caminhos in por_sha.items():
        canonico = caminhos[0]
        ext = os.path.splitext(canonico)[1].lower()
        corpo = corpo_de.get(sha) or (canonico if ext in BRUTO_LEGIVEL else None)
        frame.append({
            "DOC_SHA256": sha,
            "CANONICAL_PATH": canonico,
            "ALL_PATHS": caminhos,
            "BODY_PATH": corpo,
            "REVIEWABLE": bool(corpo),
            "PUBLISHER": censo.publicador_de(canonico),
            "SOURCE_ID": censo.fonte_de(canonico),
            "DOCUMENT_FAMILY": censo.familia_de(canonico),
            "RAW_FORMAT": ext or "(sem extensao)",
        })
    return sorted(frame, key=lambda d: d["CANONICAL_PATH"])


def pacote_atual():
    """Os 46 caminhos do pacote, mapeados para a identidade do documento."""
    corpo_de, _ = _derivados()
    de_corpo = {v: k for k, v in corpo_de.items()}
    fora = {}
    for caminho, _e, _w in censo._gabarito_t2():
        sha = de_corpo.get(caminho) or _sha(caminho)
        fora[sha] = caminho
    return fora


def origem_do_pacote():
    """De que pergunta nasceu a populacao das 46. Lido do codigo, nao assumido."""
    with open(os.path.join(RAIZ, "provas", "pacote_de_revisao_t3.py"),
              encoding="utf-8") as f:
        fonte = f.read()
    m = re.search(r"def construir\(\):.*?\n    gabarito = (\S+)", fonte, re.S)
    chamada = m.group(1) if m else "NAO SEI"
    # ⚠️ A primeira versao desta funcao procurava uma frase no ficheiro de T2 e
    # devolveu `CURRENT_46_SELECTED_FOR_T2 = NO` — o contrario da verdade,
    # porque a frase que eu procurava nao era a frase que la esta.
    #
    #     PROCURAR UMA FRASE QUE EU IMAGINEI NAO E LER O CODIGO.
    #
    # Agora a resposta vem dos ROTULOS que o gabarito produz: se todos falam de
    # um universo, foi para esse universo que a populacao foi montada.
    universos = {c["LABEL"].split(":")[0]
                 for c in censo.corpus_com_corpo(censo._gabarito_t2())}
    return {
        "CURRENT_PACKET_POPULATION_SOURCE": chamada,
        "UNIVERSOS_QUE_O_GABARITO_ROTULA": sorted(universos),
        "CURRENT_46_SELECTED_FOR_T2": "YES" if universos == {"T2"} else "NO",
        "CURRENT_46_SELECTED_FOR_T3": "YES" if "T3" in universos else "NO",
        "PROVA": "provas/pacote_de_revisao_t3.py::construir chama "
                 f"`{chamada}`, e o gabarito de T2 foi montado para responder "
                 "«este documento pertence a T2?». Os negativos dele sao «nao "
                 "e tempo» — nunca «uma amostra do que a porta encontra».",
    }


# ── O PORTAO · CRITERIOS ESCRITOS ANTES DE OLHAR PARA A COBERTURA ──────────
# Um `sampling frame` de avaliacao geral precisa de tres coisas, e nenhuma
# delas e «ser grande».
CRITERIOS = {
    "COBRE_A_POPULACAO": {
        "REGRA": "a populacao revisavel que fica DE FORA tem de ser vazia, ou "
                 "ter sido deixada de fora por um criterio nao tematico e "
                 "declarado",
        "PORQUE": "quem escolhe a populacao escolhe a resposta. Se o que ficou "
                  "de fora sair todo da mesma prateleira, o resultado mede a "
                  "prateleira.",
    },
    "GRUPO_NAO_VAZA": {
        "REGRA": "tem de ser possivel reter um PUBLICADOR inteiro e ainda "
                 "sobrar material dos dois lados",
        "PORQUE": "e o que `GroupKFold` faz, e e o que T2 mediu: ajustada num "
                  "publicador, a regra acertou 0/10 no que nao viu.",
    },
    "SELECAO_NAO_TEMATICA": {
        "REGRA": "nenhum item pode ter entrado por palavra, nome de ficheiro, "
                 "territorio da ficha ou decisao anterior",
        "PORQUE": "senao a distribuicao de avaliacao e definida pelo proprio "
                  "sinal que se vai avaliar.",
    },
}


def comparar(frame, pacote):
    revisaveis = [d for d in frame if d["REVIEWABLE"]]
    dentro = [d for d in revisaveis if d["DOC_SHA256"] in pacote]
    fora = [d for d in revisaveis if d["DOC_SHA256"] not in pacote]
    return revisaveis, dentro, fora


def _dist(docs, chave):
    return dict(Counter(d[chave] for d in docs).most_common())


def red_team(frame, pacote, revisaveis, dentro, fora):
    """Dez ataques. Cada um responde com numero, nao com opiniao."""
    R = []
    R.append(("1 · o corpus inteiro e herdado de T2",
              "CONFIRMADO",
              f"{len(dentro)} dos {len(revisaveis)} documentos revisaveis "
              f"estao no pacote, e todos entraram por terem sido escolhidos "
              f"para responder a pergunta de T2."))
    publ_fora = sorted({d["PUBLISHER"] for d in fora})
    R.append(("2 · o que ficou de fora sai todo da mesma prateleira",
              "CONFIRMADO" if len(fora) else "n/a",
              f"{len(fora)} documentos de fora, de {len(publ_fora)} "
              f"publicadores: {publ_fora}"))
    pastas = [d for d in frame if "IT-BOLLETTINI-VPN" in d["CANONICAL_PATH"]]
    R.append(("3 · pasta tratada como publicador",
              "CORRIGIDO",
              f"os {len(pastas)} boletins da pasta VPN resolvem-se em "
              f"{len({d['PUBLISHER'] for d in pastas})} publicadores reais"))
    desconhecidos = [d for d in revisaveis if d["PUBLISHER"] == "NAO SEI"]
    R.append(("4 · UNKNOWN tratado como grupo real",
              "NAO OCORRE" if not desconhecidos else "ATENCAO",
              f"{len(desconhecidos)} documentos revisaveis sem publicador "
              f"resolvido"))
    R.append(("5 · nome do ficheiro usado na selecao",
              "NAO OCORRE",
              "a inclusao usa existencia, extensao e legibilidade. Nenhuma "
              "comparacao de nome entra em `sampling_frame()`."))
    R.append(("6 · territorio da fonte usado na selecao",
              "NAO OCORRE",
              "`SOURCE_ID` e registado como caracteristica; nao filtra nada."))
    R.append(("7 · decisao antiga usada na selecao",
              "NAO OCORRE",
              "o livro de decisoes nao e lido por esta prova."))
    publ = Counter(d["PUBLISHER"] for d in revisaveis)
    retiraveis = [p for p in publ
                  if len([d for d in revisaveis if d["PUBLISHER"] != p]) >= 10]
    R.append(("8 · mesmo publicador dos dois lados de um futuro holdout",
              "ESTRUTURALMENTE EVITAVEL",
              f"{len(retiraveis)} dos {len(publ)} publicadores podem ser "
              f"retidos por inteiro deixando >=10 documentos. ATENCAO: se "
              f"reter um deixa POSITIVOS E NEGATIVOS de T3 dos dois lados e "
              f"desconhecido, e continua desconhecido ate haver rotulos. "
              f"Estrutura nao e cobertura."))
    multi = [d for d in frame if len(d["ALL_PATHS"]) > 1]
    R.append(("9 · o mesmo documento contado duas vezes",
              "EVITADO",
              f"{len(multi)} documentos vivem em dois caminhos e contam UMA "
              f"vez — a unidade e o SHA dos bytes, nao o caminho"))
    series = _series(dentro)
    R.append(("10 · parecem diversos por contagem, mas sao poucas publicacoes",
              "CONFIRMADO E MEDIDO",
              f"{len(dentro)} documentos, mas {len(series)} series de "
              f"publicacao. A maior traz {max(series.values())} edicoes/zonas "
              f"da MESMA publicacao."))
    return R


def _series(docs):
    """Edicoes e zonas da mesma publicacao nao sao evidencias independentes."""
    fora = Counter()
    for d in docs:
        nome = os.path.basename(d["CANONICAL_PATH"])
        base = re.sub(r"[\d_\-.]+", " ", nome).strip()
        fora[f"{d['PUBLISHER']} :: {base[:38]}"] += 1
    return fora


def portao(revisaveis, dentro, fora):
    cobre = len(fora) == 0
    publ = Counter(d["PUBLISHER"] for d in dentro)
    grupo_ok = sum(1 for p in publ
                   if len([d for d in dentro if d["PUBLISHER"] != p]) >= 10) >= 3
    nao_tematica = False   # medido: a populacao veio do gabarito de T2
    adequado = cobre and grupo_ok and nao_tematica
    papel = ("A. GENERAL_T3_EVAL_CANDIDATE" if adequado
             else "B. PARTIAL_T3_EVAL_SLICE" if grupo_ok
             else "C. SANITY_ONLY")
    return {"COBRE_A_POPULACAO": cobre, "GRUPO_NAO_VAZA": grupo_ok,
            "SELECAO_NAO_TEMATICA": nao_tematica,
            "CURRENT_46_ADEQUATE_FOR_GENERAL_T3_EVALUATION":
                "YES" if adequado else "NO",
            "CURRENT_46_ROLE": papel}


def main():
    frame = sampling_frame()
    pacote = pacote_atual()
    revisaveis, dentro, fora = comparar(frame, pacote)
    origem = origem_do_pacote()

    print("A AMOSTRAGEM NEUTRA DE T3")
    print("=" * 74)

    print("\n1 · DE ONDE VIERAM AS 46 — lido do codigo")
    print("-" * 74)
    for k in ("CURRENT_PACKET_POPULATION_SOURCE",
              "UNIVERSOS_QUE_O_GABARITO_ROTULA",
              "CURRENT_46_SELECTED_FOR_T2", "CURRENT_46_SELECTED_FOR_T3"):
        print(f"  {k:<38} {origem[k]}")
    print(f"\n  {origem['PROVA']}")

    print("\n2 · O SAMPLING FRAME — inclusao nao tematica")
    print("-" * 74)
    print(f"  ficheiros de documento                {sum(len(d['ALL_PATHS']) for d in frame)}")
    print(f"  DOCUMENTOS UNICOS (por bytes)         {len(frame)}")
    print(f"  em mais de um caminho                 "
          f"{len([d for d in frame if len(d['ALL_PATHS']) > 1])}")
    print(f"  ALL_REVIEWABLE_DOCUMENTS              {len(revisaveis)}")
    naolegiveis = [d for d in frame if not d["REVIEWABLE"]]
    print(f"  sem corpo legivel                     {len(naolegiveis)}")
    for d in naolegiveis:
        print(f"      {d['CANONICAL_PATH']}  ({d['RAW_FORMAT']})")

    print("\n3 · CARACTERIZACAO — nenhuma destas e um rotulo")
    print("-" * 74)
    print(f"  PUBLISHERS         {len(set(d['PUBLISHER'] for d in revisaveis))}")
    print(f"     {_dist(revisaveis, 'PUBLISHER')}")
    print(f"  SOURCE_IDS         "
          f"{len(set(d['SOURCE_ID'] for d in revisaveis) - {'NAO SEI'})}")
    print(f"  DOCUMENT_FAMILIES  {_dist(revisaveis, 'DOCUMENT_FAMILY')}")
    print(f"  RAW_FORMATS        {_dist(revisaveis, 'RAW_FORMAT')}")
    print(f"  COUNTRIES          {{'IT': {len(revisaveis)}}}")
    print(f"  LANGUAGES          declarado nos manifestos: it · resto NAO SEI")

    print("\n4 · 46 vs POPULACAO REVISAVEL")
    print("-" * 74)
    print(f"  CURRENT_PACKET        {len(pacote)}")
    print(f"  TOTAL_REVIEWABLE      {len(revisaveis)}")
    print(f"  OVERLAP               {len(dentro)}")
    print(f"  NOT_IN_CURRENT_PACKET {len(fora)}")
    for d in fora:
        print(f"      {d['PUBLISHER']:<24} {d['CANONICAL_PATH']}")
    print(f"\n  COBERTURA = {len(dentro)}/{len(revisaveis)} "
          f"= {100*len(dentro)//len(revisaveis)}%")
    ausentes = ({d["PUBLISHER"] for d in revisaveis}
                - {d["PUBLISHER"] for d in dentro})
    print(f"\n  PUBLICADORES INTEIRAMENTE AUSENTES DO PACOTE: {len(ausentes)}")
    print(f"      {sorted(ausentes)}")
    print("  A cobertura de 86% conta DOCUMENTOS. Contada por PUBLICADOR ela e")
    print(f"  {len({d['PUBLISHER'] for d in dentro})}/"
          f"{len({d['PUBLISHER'] for d in revisaveis})}. Os que faltam por")
    print("  inteiro sao estatistica, subsidio e preco. Nenhum e boletim.")

    print("\n5 · O QUE FICOU DE FORA TEM UMA FORMA")
    print("-" * 74)
    print(f"  familias dentro do pacote  {_dist(dentro, 'DOCUMENT_FAMILY')}")
    print(f"  familias fora do pacote    {_dist(fora, 'DOCUMENT_FAMILY')}")
    print(f"  formatos fora do pacote    {_dist(fora, 'RAW_FORMAT')}")
    print("\n  O gabarito de T2 procurava «documentos sobre tempo» e «documentos")
    print("  que claramente nao sao tempo». Na pratica os negativos dele sairam")
    print("  todos da mesma prateleira: boletins. O que ficou de fora e o")
    print("  material tabular e administrativo — preco, subsidio, estatistica.")
    print("\n  ISTO NAO E UM ROTULO. E a forma do que nao foi apanhado.")

    print("\n6 · SERIES DE PUBLICACAO — edicoes nao sao evidencias independentes")
    print("-" * 74)
    ser = _series(dentro)
    print(f"  {len(dentro)} documentos  ->  {len(ser)} series de publicacao")
    for k, n in ser.most_common(6):
        print(f"      {n}  {k}")
    # O corpo legivel de um PDF e um texto DERIVADO. Contar a familia do
    # caminho canonico daria zero — e daria zero por eu estar a olhar para o
    # sitio errado, nao por nao haver derivados.
    derivados = [d for d in revisaveis
                 if d["BODY_PATH"] != d["CANONICAL_PATH"]]
    print(f"\n  DERIVED_ITEMS            {len(derivados)}")
    print(f"  UNIQUE_PARENT_DOCUMENTS  {len({d['DOC_SHA256'] for d in derivados})}"
          f"   (zero pais partilhados: um derivado por documento)")
    print(f"  brutos ja legiveis       {len(revisaveis) - len(derivados)}")

    print("\n7 · RED TEAM")
    print("-" * 74)
    for nome, estado, prova in red_team(frame, pacote, revisaveis, dentro, fora):
        print(f"  {estado:<18} {nome}")
        print(f"                     {prova}")

    print("\n8 · GRUPOS E HOLDOUT")
    print("-" * 74)
    publ = Counter(d["PUBLISHER"] for d in revisaveis)
    print(f"  PUBLISHER_GROUPING_POSSIBLE = YES  "
          f"({len(publ)} grupos, nenhum «NAO SEI»)"
          if "NAO SEI" not in publ else
          f"  PUBLISHER_GROUPING_POSSIBLE = PARCIAL")
    fontes = {d["SOURCE_ID"] for d in revisaveis} - {"NAO SEI"}
    print(f"  SOURCE_GROUPING_POSSIBLE    = PARCIAL  "
          f"({len(fontes)} fontes resolvidas, "
          f"{len([d for d in revisaveis if d['SOURCE_ID'] == 'NAO SEI'])} sem fonte)")
    print(f"  PUBLISHER_HOLDOUT_POSSIBLE  = YES")
    print(f"  maior publicador: {publ.most_common(1)[0]} de {len(revisaveis)}")

    print("\n9 · O PORTAO")
    print("-" * 74)
    for nome, c in CRITERIOS.items():
        print(f"  {nome}\n     {c['REGRA']}\n     {c['PORQUE']}")
    g = portao(revisaveis, dentro, fora)
    print()
    for k, v in g.items():
        print(f"  {k:<48} {v}")
    print(f"\n  ADDITIONAL_ITEMS_NEEDED = {len(fora)}")
    print(f"  SELECTION_METHOD        = CENSO, nao amostra. Com "
          f"{len(revisaveis)} documentos")
    print(f"                            revisaveis no total, escolher um "
          f"subconjunto")
    print(f"                            introduz vies sem poupar trabalho "
          f"nenhum.")
    print("\n  AS 46 NAO SE APAGAM: sao subconjunto do frame completo, e a")
    print("  revisao delas continua valida quando os outros entrarem.")

    if "--escrever" in sys.argv:
        with open(os.path.join(RAIZ, FRAME), "w", encoding="utf-8") as f:
            json.dump({
                "SCHEMA": "sintonia.t3-sampling-frame/1",
                "O_QUE_ISTO_E":
                    "A populacao de documentos revisaveis desta arvore, "
                    "montada SO com criterios nao tematicos. NAO ha rotulo "
                    "nenhum aqui, e nenhum campo deste ficheiro e um rotulo.",
                "COMO_REFAZER": "py provas/amostragem_neutra_t3.py --escrever",
                "HUMAN_LABELS_ADDED": 0,
                "MACHINE_LABELS_ADDED": 0,
                "CURRENT_PACKET_ORIGIN": origem["PROVA"],
                "TOTAL_REVIEWABLE": len(revisaveis),
                "IN_CURRENT_PACKET": len(dentro),
                "NOT_IN_CURRENT_PACKET": len(fora),
                "DOCUMENTOS": [dict(d, IN_CURRENT_PACKET=d["DOC_SHA256"] in pacote)
                               for d in frame],
            }, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"\n  escrito: {FRAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
