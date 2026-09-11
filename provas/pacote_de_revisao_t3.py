#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PACOTE DE REVISAO DE T3 — evidencia para uma PESSOA decidir.

    python3 provas/pacote_de_revisao_t3.py          # so mede e mostra
    python3 provas/pacote_de_revisao_t3.py --escrever

Sem rede, sem banco, sem recoleta. Nenhum rotulo e atribuido aqui.

    MACHINE_ASSIGNED_GROUND_TRUTH = PROIBIDO

Esta prova nao decide `T3 = SIM` nem `T3 = NAO`. Ela abre o documento, copia o
que la esta, e cala-se. Quem rotula e uma pessoa, e o campo dela esta vazio.

POR QUE O PACOTE TEM 46 FICHAS E NAO 27
----------------------------------------
O censo anterior encontrou 27 documentos que se auto-declaram fitossanitarios.
Eles foram encontrados por uma varredura de SEIS FRASES LITERAIS:

    'difesa integrata' 16 · 'servizio fitosanitario' 13 ·
    'bollettino fitosanitario' 12 · 'monitoraggio' 10 ·
    'difesa delle colture' 7 · 'u.o. fitosanitario' 6

Se o revisor visse SO esses 27 e marcasse SIM, todos os positivos do gabarito
conteriam uma dessas seis frases — e qualquer classificador baseado nelas
tiraria nota perfeita num gabarito que elas proprias escolheram.

    UM GABARITO CUJOS POSITIVOS FORAM SELECIONADOS POR UMA FRASE
    NAO MEDE UM CLASSIFICADOR: DEVOLVE-LHE A PROPRIA FRASE.

E o mesmo defeito que o censo mediu no livro de decisoes, com outro nome. Por
isso o pacote leva os 46 documentos do corpus, os 27 entre eles, **sem dizer
quais sao**. O revisor olha para documentos, nao para uma pre-selecao.

O QUE O PACOTE ESCONDE ATE A DECISAO, DE PROPOSITO
---------------------------------------------------
    a decisao atual de `PERGUNTAS_DO_UNIVERSO`
    o territorio declarado pela ficha da fonte
    quais dos 46 casaram a varredura

Tudo isso vive numa seccao `AUDIT_AFTER_REVIEW`, no fim, para comparar DEPOIS.

    HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT.
"""
import hashlib
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_censo", os.path.join(RAIZ, "provas", "censo_corpus_rotulado_admission.py"))
censo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(censo)

PACOTE = "docs/operacao/T3-REVIEW-PACKET-V1.md"
PENDENTE = "data/samples/T3-HUMAN-REVIEW-PENDING-V1.json"

# Os quatro estados que o revisor pode escrever. `NOT_RUN` e o unico que esta
# prova escreve, e escreve-o em todos.
ESTADOS = ("T3_SIM", "T3_NAO", "T3_AMBIGUO", "EVIDENCIA_INSUFICIENTE")
NAO_CORRIDO = "NOT_RUN"


# ── EXTRACAO · COPIAR, NUNCA INTERPRETAR ───────────────────────────────────
def _limpo(texto):
    texto = re.sub(r"<script[^>]*>.*?</script>", " ", texto,
                   flags=re.S | re.I)
    texto = re.sub(r"<style[^>]*>.*?</style>", " ", texto, flags=re.S | re.I)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = texto.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"[ \t ]+", " ", texto)


def _linhas(texto):
    return [l.strip() for l in _limpo(texto).splitlines() if l.strip()]


def titulo(caminho, texto):
    """A primeira linha com substancia. NAO e um resumo: e a linha que la esta."""
    for l in _linhas(texto):
        if len(l) >= 8 and not re.fullmatch(r"[\W\d_]+", l):
            return l[:200]
    return "(o documento nao abre com nenhuma linha legivel)"


def abertura(caminho, texto, n=900):
    """O comeco do documento, literal, so com espacos normalizados."""
    if caminho.endswith(".csv"):
        # Numa tabela, a abertura util e o cabecalho e as primeiras linhas.
        ls = texto.splitlines()
        return "\n".join(ls[:6])[:n]
    return " ".join(_linhas(texto))[:n]


# As frases que a varredura do censo procurou. Ficam aqui porque a prova tem de
# poder DIZER como os 27 foram escolhidos — nao para rotular nada.
VARREDURA_DO_CENSO = censo.SE_DECLARAM["T3"]


def autodescricao(texto):
    """O trecho LITERAL em que o documento diz o que e, ou NONE.

        SELF_DESCRIPTION != LABEL

    Isto e uma citacao com contexto, para a pessoa ler. Nao e uma conclusao, e
    a prova nao conta quantas apanhou para inferir coisa nenhuma.
    """
    plano = " ".join(_linhas(texto))[:1500]
    baixo = plano.lower()
    achados = []
    for frase in VARREDURA_DO_CENSO:
        i = baixo.find(frase)
        if i >= 0:
            achados.append(plano[max(0, i - 40):i + len(frase) + 60].strip())
    return achados


def cabecalhos(texto, limite=8):
    """Linhas curtas em maiusculas — os titulos de seccao, como estao."""
    fora = []
    for l in _linhas(texto)[:200]:
        if 3 <= len(l) <= 70 and l.upper() == l and re.search(r"[A-ZÀ-Ý]", l):
            if l not in fora:
                fora.append(l)
        if len(fora) >= limite:
            break
    return fora


def familia(caminho):
    return censo.familia_de(caminho)


def lingua_declarada(source_id):
    """So o que o MANIFESTO declara. Adivinhar a lingua seria julgar."""
    p = os.path.join(RAIZ, "data", "samples", "IT-SOURCE-SAMPLES",
                     source_id, "MANIFEST.json")
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("ORIGINAL_LANGUAGE", "NAO SEI")
    return "NAO SEI"


def _linhagem_pai(caminho):
    pais = censo._linhagem().get(caminho, [])
    return pais[0] if pais else "(o proprio documento e o bruto)"


# ── A ORDEM · NEUTRA E REPRODUZIVEL ────────────────────────────────────────
# Nao por «mais provavel T3», nao por pasta (que agruparia publicadores), nao
# pela ordem em que eu os encontrei. Por hash do caminho: estavel entre
# corridas e sem relacao nenhuma com o conteudo.
def _ordem(caminho):
    return hashlib.sha256(caminho.encode()).hexdigest()


def construir():
    """Puro: nao escreve nada. Devolve as fichas e a auditoria."""
    gabarito = censo._gabarito_t2()
    caminhos = sorted((c for c, _e, _w in gabarito), key=_ordem)
    varridos = set(censo.material_que_se_declara(gabarito)["T3"])

    fichas, auditoria = [], []
    for caminho in caminhos:
        absoluto = os.path.join(RAIZ, caminho)
        revisavel = os.path.isfile(absoluto)
        texto = censo._ler(caminho) if revisavel else ""
        source_id = censo.fonte_de(caminho)
        ficha = {
            "ITEM_ID": caminho.split("/")[-1],
            "SOURCE_ID": source_id,
            "PUBLISHER": censo.publicador_de(caminho),
            "CONTENT_PATH": caminho,
            "PARENT_ARTIFACT": _linhagem_pai(caminho),
            "DOCUMENT_TYPE": familia(caminho),
            "LANGUAGE": lingua_declarada(source_id),
            "REVIEWABLE": "YES" if revisavel else "NO",
            "BYTES": os.path.getsize(absoluto) if revisavel else 0,
            "EVIDENCE": {
                "TITLE": titulo(caminho, texto) if revisavel else "",
                "OPENING": abertura(caminho, texto) if revisavel else "",
                "SELF_DESCRIPTION": autodescricao(texto) if revisavel else [],
                "SECTION_HEADERS": cabecalhos(texto) if revisavel else [],
            },
            "REVIEWER_A": {"LABEL": NAO_CORRIDO, "REASON": None,
                           "EVIDENCE": None},
            "REVIEWER_B": {"LABEL": NAO_CORRIDO, "REASON": None,
                           "EVIDENCE": None},
            "AGREEMENT": NAO_CORRIDO,
            "FINAL_LABEL": NAO_CORRIDO,
        }
        fichas.append(ficha)
        # Tudo o que nao pode ser visto antes da decisao vive so aqui.
        auditoria.append({
            "ITEM_ID": ficha["ITEM_ID"],
            "CASOU_A_VARREDURA_DO_CENSO": caminho in varridos,
            "TERRITORIO_DA_FICHA_DA_FONTE": _territorio(source_id),
            "DECISAO_ATUAL_DA_PORTA_PARA_T3": _decisao_no_livro(
                ficha["ITEM_ID"]),
        })
    return fichas, auditoria


def _territorio(source_id):
    m = re.match(r"IT-(T\d+)-\d+", source_id or "")
    return m.group(1) if m else "NAO SEI"


_LIVRO = None


def _decisao_no_livro(item_id):
    """O que a porta JA disse sobre T3 para este item — medido, nao assumido."""
    global _LIVRO
    if _LIVRO is None:
        _LIVRO = censo._json("data/samples/LIVRO-DE-DECISOES.json")["DECISOES"]
    linhas = [d for d in _LIVRO
              if d["universo"] == "T3" and item_id in str(d.get("item", ""))]
    if not linhas:
        return "NENHUMA — nao ha decisao de T3 no livro para este item"
    return "; ".join(f"{d['resultado']} ({d['regra']} v{d['versao']})"
                     for d in linhas)


# ── O PROTOCOLO QUE O REVISOR LE ───────────────────────────────────────────
# Nao e uma lei nova, e NAO vai para `PERGUNTAS_DO_UNIVERSO`. E a instrucao de
# como preencher a ficha, e usa a definicao canonica que ja existe:
#     T3 = Praga e doenca   (pedido/pedido.py :: ALVOS)
PROTOCOLO = """\
**A definicao e a que ja existe, e nao se inventa outra:** `T3 = Praga e doenca`
(`pedido/pedido.py :: ALVOS`).

- **`T3_SIM`** — o documento, **pelo proprio conteudo**, apresenta-se ou trata
  substancialmente de praga, doenca, fitossanidade, defesa fitossanitaria ou do
  manejo desse problema.
- **`T3_NAO`** — o documento pertence claramente a outro assunto e so menciona
  praga ou doenca de passagem.
- **`T3_AMBIGUO`** — os dois assuntos sao substanciais. Nao desempate para
  arrumar o numero: ambiguo e um resultado.
- **`EVIDENCIA_INSUFICIENTE`** — o trecho disponivel nao chega para decidir.
  Isto nao e falha do revisor: e informacao sobre o pacote.

Escreva sempre o **MOTIVO** e a **EVIDENCIA USADA** — que trecho, que linha. Um
rotulo sem razao escrita nao serve de gabarito, e esta casa ja mediu porque.
"""


def markdown(fichas, auditoria):
    L = []
    A = L.append
    total = len(fichas)
    A("# PACOTE DE REVISAO HUMANA — `T3 = Praga e doenca`")
    A("")
    A("> **Este ficheiro esta a espera de uma pessoa.** Nenhum rotulo aqui foi")
    A("> atribuido por maquina, e nenhum sera.")
    A(">")
    A("> ```")
    A("> AUTO_LABELS_ASSIGNED = 0")
    A("> HUMAN_REVIEW_REQUIRED = YES")
    A("> ```")
    A(">")
    A("> Isto **nao e** o gabarito de T3. E o pacote que permite construi-lo.")
    A("")
    A("---")
    A("")
    A("## COMO PREENCHER")
    A("")
    A(PROTOCOLO)
    A("")
    A("## O QUE ESTE PACOTE ESCONDE DE SI, E PORQUE")
    A("")
    A("Ate voce decidir, este ficheiro **nao lhe mostra**:")
    A("")
    A("- a decisao atual da porta (`PERGUNTAS_DO_UNIVERSO`);")
    A("- o territorio declarado pela ficha da fonte;")
    A("- quais destes documentos casaram a varredura que os trouxe para aqui.")
    A("")
    A("Tudo isso esta na seccao `AUDIT_AFTER_REVIEW`, **no fim**, para comparar")
    A("depois. A ordem de apresentacao e por hash do caminho — nao por")
    A("publicador, nao por pasta, e nao por «mais parecido com T3».")
    A("")
    A("```")
    A("HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT.")
    A("```")
    A("")
    A("## TRES ARMADILHAS QUE ESTE CORPUS TEM DE VERDADE")
    A("")
    A("Nao sao hipoteses: foram medidas nesta arvore.")
    A("")
    A("**1 · O NOME DO FICHEIRO NAO E PROVA SOBRE O CONTEUDO.** O campo")
    A("`PARENT` mostra o caminho do original porque a procedencia faz parte da")
    A("ficha — mas **seis** documentos deste pacote tem no nome")
    A("«Fitosanitari», «Agrometeorologico» ou «Meteorologico» e **cinco deles**")
    A("nao dizem nada disso na abertura. Decida pelo corpo.")
    A("")
    A("**2 · O MESMO PUBLICADOR PRODUZ ASSUNTOS DIFERENTES.** A ARPAV publica")
    A("«Meteo Veneto» e tambem «U.O. Fitosanitario — VITE». Ver o nome da")
    A("instituicao nao adianta a resposta.")
    A("")
    A("**3 · HA DOCUMENTOS QUE SAO AS DUAS COISAS.** Alguns abrem com paginas")
    A("de analise meteorologica e so depois tratam da praga. Para esses existe")
    A("`T3_AMBIGUO`, e usa-lo e a resposta certa — nao uma desistencia.")
    A("")
    A("**Um aviso sobre tabelas.** Ficheiros muito grandes (CSV) aparecem com")
    A("as primeiras linhas apenas. Se isso nao chegar, a resposta e")
    A("`EVIDENCIA_INSUFICIENTE` — nao um palpite.")
    A("")
    A("**E por isso que sao %d fichas e nao 27.** O censo achou 27 documentos"
      % total)
    A("que se auto-declaram fitossanitarios, e achou-os com seis frases")
    A("literais. Se este pacote levasse so esses 27, todo positivo do gabarito")
    A("conteria uma dessas frases — e qualquer classificador baseado nelas")
    A("tiraria nota perfeita num gabarito que elas escolheram. Os 27 estao aqui")
    A("dentro, **sem marca nenhuma**, no meio dos outros.")
    A("")
    A("---")
    A("")
    for i, f in enumerate(fichas, 1):
        e = f["EVIDENCE"]
        A(f"## ITEM {i:02d} / {total}")
        A("")
        A("```")
        A(f"ITEM_ID        {f['ITEM_ID']}")
        A(f"SOURCE_ID      {f['SOURCE_ID']}")
        A(f"PUBLISHER      {f['PUBLISHER']}")
        A(f"CONTENT_PATH   {f['CONTENT_PATH']}")
        A(f"PARENT         {f['PARENT_ARTIFACT']}")
        A(f"DOCUMENT_TYPE  {f['DOCUMENT_TYPE']}   BYTES {f['BYTES']}")
        A(f"LANGUAGE       {f['LANGUAGE']}")
        A(f"REVIEWABLE     {f['REVIEWABLE']}")
        A("```")
        A("")
        A("**TITULO**")
        A("")
        A(f"> {e['TITLE'] or '(sem corpo — REVIEWABLE = NO)'}")
        A("")
        A("**ABERTURA DO DOCUMENTO**")
        A("")
        A("```text")
        A(e["OPENING"] or "(sem corpo)")
        A("```")
        A("")
        A("**AUTO-DESCRICAO ENCONTRADA** (trecho literal · nao e um rotulo)")
        A("")
        if e["SELF_DESCRIPTION"]:
            for t in e["SELF_DESCRIPTION"]:
                A(f"- «…{t}…»")
        else:
            A("- NONE")
        A("")
        A("**OUTROS SINAIS VISIVEIS** (linhas do documento, sem interpretacao)")
        A("")
        if e["SECTION_HEADERS"]:
            for h in e["SECTION_HEADERS"]:
                A(f"- `{h}`")
        else:
            A("- NONE")
        A("")
        A("**DECISAO HUMANA**")
        A("")
        A("| | REVIEWER_A | REVIEWER_B |")
        A("|---|---|---|")
        for est in ESTADOS:
            A(f"| `{est}` | [ ] | [ ] |")
        A("")
        A("```")
        A("MOTIVO_A          ______________________________________________")
        A("EVIDENCIA_USADA_A ______________________________________________")
        A("")
        A("MOTIVO_B          ______________________________________________")
        A("EVIDENCIA_USADA_B ______________________________________________")
        A("")
        A("AGREEMENT    [ ] AGREEMENT   [ ] DISAGREEMENT   [x] NOT_RUN")
        A("FINAL_LABEL  ____________________  (UNRESOLVED se A != B)")
        A("```")
        A("")
        A("---")
        A("")
    A("## AUDIT_AFTER_REVIEW")
    A("")
    A("> **NAO LEIA ANTES DE DECIDIR.** Esta seccao existe para comparar a")
    A("> decisao humana com o que a maquina e a ficha da fonte diziam — e essa")
    A("> comparacao so vale se a decisao humana nascer primeiro.")
    A("")
    A("| ITEM_ID | casou a varredura | territorio da FICHA DA FONTE | decisao atual da porta para T3 |")
    A("|---|:--:|:--:|---|")
    for a in auditoria:
        A(f"| `{a['ITEM_ID']}` | {'SIM' if a['CASOU_A_VARREDURA_DO_CENSO'] else 'nao'} "
          f"| {a['TERRITORIO_DA_FICHA_DA_FONTE']} "
          f"| {a['DECISAO_ATUAL_DA_PORTA_PARA_T3']} |")
    A("")
    A("Nenhuma destas tres colunas e verdade sobre o documento:")
    A("")
    A("- a **varredura** e uma busca por seis frases;")
    A("- o **territorio da ficha** ja foi medido a discordar do documento tres")
    A("  vezes (ARPAV publica T2 e T3; `IT-T5-003` declara «Preco e mercado» e")
    A("  entrega «Bilancio Fitosanitario»; `IT-T7-002` declara «Ciencia» e")
    A("  entrega uma lista administrativa);")
    A("- a **decisao da porta** e a saida do mecanismo que se quer substituir.")
    A("")
    A("```")
    A("ROTULO EXISTE            != ROTULO CONFIAVEL")
    A("KEYWORD_DERIVED          != GABARITO")
    A("SOURCE TERRITORY         != DOCUMENT UNIVERSE")
    A("```")
    return "\n".join(L) + "\n"


def main():
    fichas, auditoria = construir()
    varridos = sum(1 for a in auditoria if a["CASOU_A_VARREDURA_DO_CENSO"])
    revisaveis = [f for f in fichas if f["REVIEWABLE"] == "YES"]
    publ = sorted({f["PUBLISHER"] for f in fichas} - {"NAO SEI"})
    fontes = sorted({f["SOURCE_ID"] for f in fichas} - {"NAO SEI"})
    rotulados = [f for f in fichas
                 if f["REVIEWER_A"]["LABEL"] != NAO_CORRIDO
                 or f["REVIEWER_B"]["LABEL"] != NAO_CORRIDO
                 or f["FINAL_LABEL"] != NAO_CORRIDO]

    print("PACOTE DE REVISAO DE T3")
    print("=" * 74)
    print(f"  T3_CANDIDATES (varredura do censo)   {varridos}")
    print(f"  FICHAS NO PACOTE                     {len(fichas)}")
    print(f"  REVIEWABLE = YES                     {len(revisaveis)}")
    print(f"  REVIEWABLE = NO                      {len(fichas) - len(revisaveis)}")
    print(f"  PUBLISHERS                           {len(publ)}")
    print(f"  SOURCES                              {len(fontes)}")
    print(f"  DOCUMENT_FAMILIES                    "
          f"{sorted({f['DOCUMENT_TYPE'] for f in fichas})}")
    print(f"\n  AUTO_LABELS_ASSIGNED                 {len(rotulados)}")
    print(f"  sem auto-descricao encontrada        "
          f"{sum(1 for f in fichas if not f['EVIDENCE']['SELF_DESCRIPTION'])}")
    com = sum(1 for f in fichas if f["EVIDENCE"]["SELF_DESCRIPTION"])
    print(f"  com auto-descricao encontrada        {com}")
    if com != varridos:
        print(f"\n  NOTA: {com} != {varridos} de proposito. A varredura do censo")
        print("  olha os primeiros 600 caracteres; a extracao de evidencia olha")
        print("  1500, porque o objetivo dela e dar MAIS para a pessoa ler.")
        print("  Nenhum dos dois numeros e um rotulo.")

    if "--escrever" in sys.argv:
        with open(os.path.join(RAIZ, PACOTE), "w", encoding="utf-8") as f:
            f.write(markdown(fichas, auditoria))
        with open(os.path.join(RAIZ, PENDENTE), "w", encoding="utf-8") as f:
            json.dump({
                "SCHEMA": "sintonia.t3-human-review-pending/1",
                "O_QUE_ISTO_E":
                    "Fichas a espera de rotulagem HUMANA para T3. NAO e o "
                    "gabarito. Nenhum rotulo foi atribuido por maquina, e "
                    "`REVIEWER_A`, `REVIEWER_B` e `FINAL_LABEL` estao todos "
                    "em NOT_RUN de proposito.",
                "COMO_REFAZER": "py provas/pacote_de_revisao_t3.py --escrever",
                "ESTADOS_PERMITIDOS": list(ESTADOS) + [NAO_CORRIDO],
                "AUTO_LABELS_ASSIGNED": 0,
                "ITENS": fichas,
            }, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"\n  escrito: {PACOTE}")
        print(f"  escrito: {PENDENTE}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
