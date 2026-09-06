#!/usr/bin/env python3
"""
alvo_literal.py — o texto do ALVO de uma linha de dose existe no documento?

O red team provou uma FUSAO real: em 008259 a linha publicada como
    Soia | "Nottue defogliatrici (allo scoperto) tentredine" | 420-800 g/ha
junta a cauda de uma linha ("...altica, meligete e tentredine", 420-800) com o
texto de outra ("Nottue defogliatrici (allo scoperto)", 400-500). A quimera
recebeu a dose da primeira: 800 contra 500 autorizados.

ESTE MODULO NAO DETECTA FUSAO. Ele mede uma coisa mais fraca e verificavel: se
o texto do alvo aparece LITERALMENTE no texto do rotulo. E publica o estado.

Por que nao detecta fusao, escrito aqui para nao virar promessa:

  * o teste literal sobre o texto da pagina inteira acusa 180 das 839 linhas, e
    a maioria e ALVO QUEBRADO EM COLUNA, nao fusao: numa etichetta de tres
    colunas, "Cemiostoma, litocollete (prima della comparsa delle mine ed in
    presenza di uova mature della 1a generazione), carpocapsa" chega ao
    pdftotext -layout intercalado com texto das colunas vizinhas. Separar os
    dois casos exige reconstruir o texto POR COLUNA, que este modulo nao faz;

  * a heuristica "o alvo contem outro alvo inteiro do mesmo rotulo" acusa 86
    linhas e erra em cheio nas legitimas: `Pomacee x "Dysaphis spp., Eriosoma
    spp., Aphis spp."` e um alvo multiplo verdadeiro que apenas TERMINA com
    outro alvo usado noutra linha. Uma regra que condena esse par condena a
    propria etichetta;

  * tentei tambem ancorar primeira e ultima palavra do alvo pelos fios
    desenhados: 629 linhas conferiveis, ZERO acusacoes, porque a banda y do
    extrator nao contem as duas pontas do alvo fundido. O detector nao
    detectava o caso que existe.

Entao: nenhuma linha e rebaixada por este modulo. Ele emite
TARGET_TEXT_NOT_FOUND_LITERALLY, que a tela mostra como estado de leitura, e
diz na cara que nao sabe separar quebra de coluna de fusao. Rebaixar 180 linhas
por um teste que nao distingue os dois casos apagaria uso verdadeiro; nao dizer
nada esconderia a fusao provada. O estado e a resposta honesta entre as duas.
"""
import argparse, json, os, re, subprocess, sys, unicodedata


def nrm(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def texto(reg, pdfs, cache):
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, f"{reg}.txt")
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        pdf = os.path.join(pdfs, f"{reg}.pdf")
        if not os.path.exists(pdf):
            return None
        try:
            subprocess.run(["pdftotext", "-layout", pdf, alvo], check=True,
                           capture_output=True, timeout=180)
        except Exception:
            return None
    return open(alvo, encoding="utf-8", errors="replace").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pdfs", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--cache", default="/tmp/tetotxt")
    ap.add_argument("--out", default="v1/dados/ALVO-LITERAL.json")
    a = ap.parse_args()

    d = json.load(open(a.doses, encoding="utf-8"))
    ver, achados = {}, []
    n_ok = n_nao = n_sem = 0
    cache = {}
    for lab in d["LABELS"]:
        reg = lab["REGISTRATION_ID"]
        if reg not in cache:
            t = texto(reg, a.pdfs, a.cache)
            cache[reg] = nrm(t) if t else None
        t = cache[reg]
        for i, r in enumerate(lab.get("ROWS") or []):
            chave = f"{reg}#{i}"
            alvo = nrm(r.get("TARGET"))
            if t is None or len(alvo) < 8:
                ver[chave] = "TARGET_TEXT_NOT_CHECKED"; n_sem += 1; continue
            if alvo in t:
                ver[chave] = "TARGET_TEXT_FOUND_LITERALLY"; n_ok += 1
            else:
                ver[chave] = "TARGET_TEXT_NOT_FOUND_LITERALLY"; n_nao += 1
                achados.append({"REGISTRATION_ID": reg, "PRODUCT": lab.get("PRODUCT"),
                                "ROW_INDEX": i, "CROP": r.get("CROP"),
                                "TARGET": r.get("TARGET"),
                                "DOSE_PER_HECTARE": r.get("DOSE_PER_HECTARE"),
                                "DOSE_PER_HECTARE_UNIT": r.get("DOSE_PER_HECTARE_UNIT")})
    saida = {
        "DATASET": "V1-ALVO-LITERAL",
        "RULE_ID": "R-13",
        "O_QUE_ISTO_E": "o texto do alvo da linha de dose aparece literalmente no texto do rotulo",
        "O_QUE_ISTO_NAO_E": ("NAO e um detector de fusao de linha. Nao separa alvo quebrado em "
                             "coluna de alvo fundido, e por isso NAO rebaixa nenhuma linha"),
        "FUSION_DETECTOR": "NOT_IMPLEMENTED",
        "FUSION_PROVEN_EXAMPLE": ('008259: "Nottue defogliatrici (allo scoperto) tentredine" com '
                                  'dose 420-800 g/ha; na etichetta sao duas linhas distintas, e a '
                                  'de Nottue vale 400-500'),
        "WHY_NOT_IMPLEMENTED": ("tres tentativas medidas: teste literal acusa 180/839 e a maioria "
                                "e quebra de coluna; heuristica de conteudo acusa 86 e condena "
                                "alvo multiplo legitimo (Pomacee x Dysaphis/Eriosoma/Aphis); "
                                "ancoragem por fios nas duas pontas do alvo acusa ZERO porque a "
                                "banda do extrator nao contem as duas pontas do alvo fundido"),
        "ROWS_FOUND_LITERALLY": n_ok,
        "ROWS_NOT_FOUND_LITERALLY": n_nao,
        "ROWS_NOT_CHECKED": n_sem,
        "VERDICT": ver,
        "NOT_FOUND": achados,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  alvos: literais {n_ok} | NAO literais {n_nao} | nao conferiveis {n_sem} "
          f"(nenhuma linha rebaixada por este modulo)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
