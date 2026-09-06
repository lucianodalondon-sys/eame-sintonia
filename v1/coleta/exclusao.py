#!/usr/bin/env python3
"""
exclusao.py — EXCLUSAO NAO E PERMISSAO.

Defeito medido, nao suposto. O leitor de uso reusado (it_rotulo_parser/3.4.0)
nao modela exclusao: nao ha campo de escopo negativo no esquema dele. Nas
etichettas 002983 (NIMROD) e 013405 (VERBUM EW) a unica ocorrencia da raiz
"cilieg" e dentro de "Pomodoro (ad esclusione di Pomodoro ciliegino)" — e o
leitor publicou CILIEGIO x OIDIO como uso AUTORIZADO. Sao dois erros somados:
    1. leu uma exclusao como permissao;
    2. leu "pomodoro ciliegino" (tomate cereja) como "ciliegio" (cerejeira),
       que e outra cultura.

Este modulo NAO conserta o parser de origem (canonical e somente leitura). Ele
reconcilia o que foi reusado contra a FONTE PRIMARIA — o PDF oficial que ja
esta em disco — e decide, por par, se a cultura tem atestado fora de toda
janela de exclusao do rotulo.

Estados emitidos:
  ATTESTED_OUTSIDE_EXCLUSION  a cultura aparece no texto do rotulo fora de
                              qualquer janela de exclusao. O par segue.
  CROP_ONLY_INSIDE_EXCLUSION  a cultura tem apoio textual DENTRO de uma janela
                              de exclusao e NENHUM fora dela. O unico motivo
                              pelo qual esta cultura foi lida e uma exclusao.
                              O par NAO pode ser exibido como uso autorizado.
  CROP_NAME_NOT_FOUND_IN_LABEL_TEXT
                              a raiz do nome nao aparece no rotulo nem dentro
                              nem fora de janela. Isto e diferenca de
                              vocabulario (o rotulo escreve "Grano", o leitor
                              normaliza para FRUMENTO), nao exclusao. O par
                              segue, marcado como nao conferido por este teste.
  NO_LABEL_TEXT               o PDF nao foi lido. Nao e ausencia de exclusao:
                              e ausencia de verificacao. (NOT_CHECKED)

E, independente disso, por rotulo:
  EXCLUSION_PRESENT_IN_LABEL  o rotulo tem pelo menos uma janela de exclusao.
                              Mesmo os pares que sobrevivem tem escopo mais
                              estreito que o nome da cultura sugere, e a tela
                              precisa mostrar a frase literal.

LEI ZERO: nada aqui apaga fato em silencio. Par retirado vai para uma lista
propria, com a frase literal do rotulo que o retirou.
"""
import argparse, glob, json, os, re, subprocess, sys, unicodedata
from collections import defaultdict

# Marcadores de exclusao em italiano. Lista fechada e medida sobre os 163
# rotulos oficiais em disco (contagem no cabecalho de EXCLUSAO.json).
#
# "salvo" foi MEDIDO e DESCARTADO: as 3 ocorrencias no corpus sao
# "miscibile ... salvo con quelli a reazione alcalina" (compatibilidade de
# calda, nao escopo de cultura), e a palavra em italiano tambem e adjetivo
# ("a salvo"). Marcador ambiguo retira uso real; melhor nao usa-lo e dizer
# que nao se usou.
MARCADORES = [
    "ad esclusione di", "a esclusione di", "con esclusione di", "esclusione di",
    "escluso", "esclusa", "esclusi", "escluse",
    "ad eccezione di", "a eccezione di", "fatta eccezione per", "eccezione di",
    "tranne", "eccetto",
]
MARCADOR_DESCARTADO = {
    "salvo": ("ambiguo em italiano (preposicao 'exceto' e adjetivo 'salvo'); "
              "as 3 ocorrencias medidas no corpus sao compatibilidade de calda, "
              "nao escopo de cultura")
}
RX_MARCADOR = re.compile(r"\b(" + "|".join(sorted(MARCADORES, key=len, reverse=True)) + r")\b")

# Fim da janela: ponto, ponto-e-virgula, dois-pontos, quebra de linha, ou uma
# corrida de 3+ espacos — que no texto de coluna do pdftotext -layout marca
# fronteira entre colunas. Virgula NAO fecha: depois do marcador vem lista
# ("tranne grossa radice, rafano, bietola rossa").
RX_FIM = re.compile(r"[.;:]|\n|   +")
JANELA_MAX = 200          # caracteres; corte duro para nao apagar a pagina toda
PREFIXO_MIN = 4           # prefixo comum minimo para considerar apoio textual


def sem_acento(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def texto_do_rotulo(pdf, cache_dir):
    """pdftotext -layout, com cache. Devolve None se nao ha texto."""
    alvo = os.path.join(cache_dir, os.path.basename(pdf)[:-4] + ".txt")
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        os.makedirs(cache_dir, exist_ok=True)
        try:
            subprocess.run(["pdftotext", "-layout", pdf, alvo], check=True,
                           capture_output=True, timeout=120)
        except Exception:
            return None
    try:
        with open(alvo, encoding="utf-8", errors="replace") as fh:
            t = fh.read()
    except OSError:
        return None
    return t or None


def janelas(texto):
    """Janelas de exclusao do rotulo. Devolve [(inicio, fim, literal)].

    Se o marcador esta dentro de parenteses, a janela e o parenteses inteiro —
    e assim que "(ad esclusione di Pomodoro ciliegino)" se fecha sozinho.
    """
    t = sem_acento(texto)
    out = []
    for m in RX_MARCADOR.finditer(t):
        i, j = m.start(), m.end()
        # parenteses aberto antes do marcador, sem fechar no meio?
        ab = t.rfind("(", 0, i)
        if ab != -1 and t.find(")", ab, i) == -1:
            fe = t.find(")", j)
            # o comprimento que conta e o COLAPSADO. No texto de coluna do
            # pdftotext -layout, "(ad esclusione di" e "Pomodoro ciliegino)"
            # ficam em linhas diferentes com centenas de espacos entre eles:
            # medindo o bruto o parenteses parecia grande demais, a janela era
            # cortada na quebra de linha e "ciliegino" escapava para fora dela.
            if fe != -1 and len(re.sub(r"\s+", " ", t[ab:fe + 1])) <= JANELA_MAX:
                out.append((ab, fe + 1, texto[ab:fe + 1]))
                continue
        f = RX_FIM.search(t, j)
        fim = min(f.start() if f else len(t), j + JANELA_MAX)
        out.append((i, fim, texto[i:fim]))
    # funde janelas que se sobrepoem
    out.sort()
    fund = []
    for a, b, lit in out:
        if fund and a <= fund[-1][1]:
            fund[-1] = (fund[-1][0], max(fund[-1][1], b), fund[-1][2])
        else:
            fund.append((a, b, lit))
    return fund


def fora_das_janelas(texto, js):
    """O mesmo texto com cada janela de exclusao trocada por espacos."""
    t = list(sem_acento(texto))
    for a, b, _ in js:
        for k in range(a, min(b, len(t))):
            t[k] = " "
    return "".join(t)


RX_TOKEN = re.compile(r"[a-z]{3,}")


def apoia(parte, tok):
    """Apoio textual generoso: prefixo comum de PREFIXO_MIN letras.

    Generoso de proposito. Errar para o lado de ACHAR apoio so deixa o par
    sobreviver marcado; errar para o lado de NAO achar retiraria uso real.
    A retirada so acontece quando nao existe nenhum apoio em lugar nenhum
    fora das janelas.
    """
    n = 0
    for a, b in zip(parte, tok):
        if a != b:
            break
        n += 1
    return n >= PREFIXO_MIN


def atestada(crop, tokens):
    partes = [p for p in sem_acento(crop).split("_") if len(p) >= 3]
    if not partes:
        return False
    return any(apoia(p, t) for p in partes for t in tokens)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", required=True)
    ap.add_argument("--pdfs", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--cache", default="/tmp/exclusao-txt")
    ap.add_argument("--out", default="v1/dados/EXCLUSAO.json")
    a = ap.parse_args()

    pares = json.load(open(a.pares, encoding="utf-8"))["PAIRS"]
    por_reg = defaultdict(list)
    for p in pares:
        por_reg[p["REGISTRATION_ID"]].append(p)

    marcador_hits = defaultdict(int)
    rotulos, veredito, retirados, nao_achados = {}, {}, [], []
    for reg in sorted(por_reg):
        pdf = os.path.join(a.pdfs, f"{reg}.pdf")
        texto = texto_do_rotulo(pdf, a.cache) if os.path.exists(pdf) else None
        if texto is None:
            rotulos[reg] = {"LABEL_TEXT": "NOT_CHECKED", "EXCLUSION_WINDOWS": []}
            for i, _ in enumerate(por_reg[reg]):
                veredito[f"{reg}#{i}"] = "NO_LABEL_TEXT"
            continue
        js = janelas(texto)
        for _, _, lit in js:
            m = RX_MARCADOR.search(sem_acento(lit))
            if m:
                marcador_hits[m.group(1)] += 1
        tokens = set(RX_TOKEN.findall(fora_das_janelas(texto, js)))
        rotulos[reg] = {
            "LABEL_TEXT": "READ",
            "LABEL_PDF": pdf,
            "EXCLUSION_WINDOWS": [re.sub(r"\s+", " ", lit).strip() for _, _, lit in js],
        }
        for i, p in enumerate(por_reg[reg]):
            ok = atestada(p["CROP"], tokens)
            # Janelas que apoiam esta cultura. Uma janela pode ter sido medida
            # atravessando coluna e carregar prosa alheia no meio; mostramos a
            # MAIS CURTA, que e a frase real do rotulo, e dizemos quantas ha.
            dentro = sorted({re.sub(r"\s+", " ", lit).strip() for _, _, lit in js
                             if atestada(p["CROP"], set(RX_TOKEN.findall(sem_acento(lit))))},
                            key=len)
            if ok:
                veredito[f"{reg}#{i}"] = "ATTESTED_OUTSIDE_EXCLUSION"
                continue
            if not dentro:
                # Sem apoio em lugar nenhum: isto e vocabulario, nao exclusao.
                # Medido: FRUMENTO em 015232/017358/017824 — o rotulo escreve
                # "Grano". Retirar aqui apagaria uso real por diferenca de nome.
                # Nao inventamos sinonimo e nao retiramos: dizemos que nao
                # conferimos.
                veredito[f"{reg}#{i}"] = "CROP_NAME_NOT_FOUND_IN_LABEL_TEXT"
                nao_achados.append({"REGISTRATION_ID": reg, "PRODUCT": p.get("PRODUCT"),
                                    "CROP": p["CROP"], "TARGET": p["TARGET"]})
                continue
            veredito[f"{reg}#{i}"] = "CROP_ONLY_INSIDE_EXCLUSION"
            if True:
                retirados.append({
                    "REGISTRATION_ID": reg, "PRODUCT": p.get("PRODUCT"),
                    "CROP": p["CROP"], "TARGET": p["TARGET"],
                    "ROUTE": p.get("ROUTE"),
                    "CROP_AS_WRITTEN": p.get("CROP_AS_WRITTEN"),
                    "WHY": "CROP_ONLY_INSIDE_EXCLUSION",
                    "EXCLUSION_TEXT": dentro[0],
                    "EXCLUSION_WINDOWS_SUPPORTING": len(dentro),
                    "EXCLUSION_TEXT_ALL": dentro,
                    "PROOF": (f"a raiz da cultura {p['CROP']} nao ocorre em nenhum ponto do "
                              f"texto do rotulo fora de uma janela de exclusao"),
                    "LABEL_PDF": pdf,
                })

    n_ret = len(retirados)
    n_lab_ex = sum(1 for r in rotulos.values() if r["EXCLUSION_WINDOWS"])
    # Nomes de campo em portugues de proposito: "withdrawn" em ingles colide com
    # retirada DE MERCADO, que e justamente a conclusao que esta ferramenta nao
    # tem direito de emitir. Aqui o que foi retirado e um PAR DE USO da tela.
    saida = {
        "DATASET": "V1-EXCLUSAO",
        "O_QUE_ISTO_E": ("reconciliacao de cada par de uso reusado contra o texto do PDF "
                         "oficial, para separar exclusao de permissao"),
        "O_QUE_ISTO_NAO_E": ("nao e um leitor de rotulo novo, nao reescreve o parser de "
                             "origem e nao decide dose"),
        "RULE_ID": "R-10",
        "MARCADORES": MARCADORES,
        "MARCADOR_DESCARTADO": MARCADOR_DESCARTADO,
        "MARCADOR_OCORRENCIAS": dict(sorted(marcador_hits.items(), key=lambda kv: -kv[1])),
        "PREFIXO_MIN": PREFIXO_MIN,
        "PAIRS_CHECKED": len(pares),
        "LABELS_CHECKED": len(rotulos),
        "LABELS_WITH_EXCLUSION": n_lab_ex,
        "PARES_RETIRADOS": n_ret,
        "PAIRS_CROP_NAME_NOT_IN_LABEL_TEXT": len(nao_achados),
        "CROP_NAME_NOT_IN_LABEL_TEXT": nao_achados,
        "LABELS": rotulos,
        "VERDICT": veredito,
        "RETIRADOS": retirados,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  rotulos lidos {len(rotulos)} | com janela de exclusao {n_lab_ex} "
          f"| pares {len(pares)} | retirados {n_ret} "
          f"| nome fora do vocabulario do rotulo {len(nao_achados)}", file=sys.stderr)
    for r in retirados:
        print(f"    RETIRADO {r['REGISTRATION_ID']} {r['PRODUCT']:<14} "
              f"{r['CROP']} x {r['TARGET']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
