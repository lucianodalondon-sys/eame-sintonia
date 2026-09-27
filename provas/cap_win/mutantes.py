#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DA CAP-WIN — planta UM defeito de cada vez em `motor/cap_win.py`,
corre `tests.test_cap_win`, e exige que ele REPROVE. Restaura os bytes originais
sempre (sem `git checkout`), e confere no fim que o ficheiro voltou igual.

    python3 provas/cap_win/mutantes.py          # grava provas/cap_win/MUTANTES.json

Um mutante que sobrevive e um teste que falta, nao um mutante mau.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = RAIZ / "motor" / "cap_win.py"
SAIDA = Path(__file__).resolve().parent / "MUTANTES.json"

#: (id, o que o defeito finge, texto original, texto mutante)
MUTANTES = [
 ("M1", "a soglia nao atingida deixa de ser NO (volta o defeito do V21)",
  'return NO, "FONTE_DECLARA_SOGLIA_NAO_ATINGIDA"',
  'return UNKNOWN, "FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE"'),
 ("M2", "a negacao deixa de desarmar o positivo",
  "if not _NEGACAO_ANTES.search(t[max(0, m.start() - 25):m.start()])", "if True"),
 ("M3", "o par passa a sair mesmo sem base (fabrica CROP_ID)",
  'return None, "VALOR sem BASE"', 'return str(v).strip(), base'),
 ("M4", "sem par em campo, o item entra na mesma (sem NOT_POSSIBLE)",
  "return (None if falta else par), falta", "return par, falta"),
 ("M5", "observacao sem tempo passa a responder «agora»",
  "elif not pode_agora:", "elif False:"),
 ("M6", "STALE passa a ser CURRENT (janela de outro ano vale como desta)",
  "if fim >= hoje - timedelta(days=n_dias):", "if True:"),
 ("M7", "ACT_NOW deixa de exigir 2 independentes provados",
  'obs["INDEPENDENTES_PROVADOS"] >= 2):', 'obs["INDEPENDENTES_PROVADOS"] >= 0) or True:'),
 ("M8", "ACT_NOW deixa de exigir 0 contradicoes",
  '    if contra:\n        porque.append', '    if False:\n        porque.append'),
 ("M9", "a contradicao deixa de ser detetada",
  "else CONTRADICTS,", "else SUPPORT,"),
 ("M10", "subareas diferentes passam a contradizer-se",
  'if NAO_SEI not in (a["SUBAREA"], b["SUBAREA"]) and a["SUBAREA"] != b["SUBAREA"]:',
  "if False:"),
 ("M11", "semanas que nao se tocam passam a comparar-se",
  'or not _sobrepoe(a["TIME_WINDOW"], b["TIME_WINDOW"]):', ':'),
 ("M12", "redes nao declaradas passam a contar como independentes",
  "if por_item and all(redes):", "if por_item:"),
 ("M13", "a regra partilhada volta a contar uma vez por originador",
  "        conta = 1\n", '        conta = orig_regra["INDEPENDENT_SOURCE_COUNT"]\n'),
 ("M14", "o ato administrativo vira janela agronomica",
  "AGRONOMICOS = (CALENDAR_WINDOW,", "AGRONOMICOS = (ADMINISTRATIVE_WINDOW, CALENDAR_WINDOW,"),
 ("M15", "o plural «soglie» deixa de definir janela",
  r'r"\bsogli[ae]\b"', r'r"\bsoglia\b"'),
 ("M16", "sem HOJE declarado, usa-se o relogio",
  "if not isinstance(hoje, date):", "if hoje is None:\n        hoje = date.today()\n    if False:"),
 ("M17", "o pre-filtro deixa de ser recusado",
  "if len(linhas) != len(itens):", "if False:"),
 ("M18", "a oracao que manda parar deixa de fechar a janela",
  "if parar and dec != NO:", "if False:"),
 ("M19", "o requisito deixa de nomear a regiao",
  "REQUISITO_DA_REGIAO if \"REGIAO_DO_FATO\" in m else REQUISITO_DO_PAR",
  "REQUISITO_DO_PAR"),
 ("M20", "o qualitativo passa a responder a limiar",
  'return UNKNOWN, "FRASE_QUALITATIVA_NAO_RESPONDE_CONDICAO_QUANTITATIVA"',
  'return NO, "FRASE_QUALITATIVA_NAO_RESPONDE_CONDICAO_QUANTITATIVA"'),
 ("M21", "a leitura perde o «nao tratar» do documento",
  "do_documento = sorted({r for r in (restritiva(o) for o in todas) if r})",
  "do_documento = []"),
 ("M22", "o livro de outra versao do G0 passa a ser lido",
  'livro.get("RULESET_VERSION") != CI.RULESET_VERSION or ', ""),
]


def main() -> int:
    original = ALVO.read_bytes()
    sha0 = hashlib.sha256(original).hexdigest()
    texto = original.decode("utf-8")
    fora = []
    try:
        for mid, finge, velho, novo in MUTANTES:
            n = texto.count(velho)
            if n != 1:
                fora.append({"ID": mid, "FINGE": finge, "ESTADO": f"NAO_PLANTADO (casou {n}x)"})
                continue
            ALVO.write_text(texto.replace(velho, novo), encoding="utf-8")
            p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_cap_win"],
                               cwd=RAIZ, capture_output=True, text=True, timeout=300)
            morto = p.returncode != 0
            quem = sorted({l.split()[1] for l in p.stderr.splitlines()
                           if l.startswith(("FAIL:", "ERROR:"))})
            fora.append({"ID": mid, "FINGE": finge,
                         "ESTADO": "MORTO" if morto else "SOBREVIVEU",
                         "APANHADO_POR": quem[:6]})
            ALVO.write_bytes(original)
    finally:
        ALVO.write_bytes(original)
    assert hashlib.sha256(ALVO.read_bytes()).hexdigest() == sha0, "o alvo nao voltou igual"
    mortos = sum(1 for m in fora if m["ESTADO"] == "MORTO")
    res = {"ALVO": "motor/cap_win.py", "ALVO_SHA256": sha0, "TESTE": "tests.test_cap_win",
           "PLANTADOS": len(fora), "MORTOS": mortos, "MUTANTES": fora}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for m in fora:
        print(f'{m["ID"]:4} {m["ESTADO"]:12} {m["FINGE"]}')
    print(f"\n{mortos}/{len(fora)} mortos")
    return 0 if mortos == len(fora) else 1


if __name__ == "__main__":
    sys.exit(main())
