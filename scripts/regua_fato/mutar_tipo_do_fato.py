#!/usr/bin/env python3
"""REGUA-DO-TIPO-DE-FATO · teste de mutacao do classificador (leis/tipo_do_fato.py).

Cada mutante estraga UMA regra numa COPIA (pasta temporaria; a arvore nao e tocada) e corre
tests/test_tipo_do_fato.py contra ela. So conta como MORTO se um teste FALHOU por assercao; erro de
execucao nao prova nada.

    py scripts/regua_fato/mutar_tipo_do_fato.py      -> escreve MUTACAO-TIPO-DO-FATO-V1.json ao lado
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ALVO = "leis/tipo_do_fato.py"

MUTANTES = [
    ("M1_MENU_CONTA", "regra 1: reprova se a pagina inteira (menu/rodape) for lida como corpo",
     [('c = "\\n".join(l for l in FT.corpo(texto).splitlines() if _nao_e_grito(l))',
       'c = "\\n".join(l for l in str(texto or "").splitlines() if _nao_e_grito(l))')]),
    ("M2_MAIUSCULAS_CONTAM", "regra 1: reprova se a linha de menu em MAIUSCULAS contar",
     [("return not letras or sum(ch.isupper() for ch in letras) / len(letras) < 0.6", "return True")]),
    ("M3_SEM_PALAVRA_INTEIRA", "regra 2: reprova se «gelateria» contar como «gelata»",
     [('_BORDA_A, _BORDA_Z = r"(?<![0-9a-zà-ÿ])", r"(?![0-9a-zà-ÿ])"', '_BORDA_A, _BORDA_Z = r"", r""')]),
    ("M4_CONCEITO_CONTA_VARIAS_VEZES", "regra 2: reprova se o mesmo conceito repetido somar sinais",
     [("            out.append(m.group(0))", "            out.extend(x.group(0) for x in rx.finditer(texto))")]),
    ("M5_UM_CONCEITO_CHEGA", "regra 2: reprova se um so conceito bastar",
     [("MINIMO_DE_CONCEITOS = 2", "MINIMO_DE_CONCEITOS = 1")]),
    ("M6_RACCOLTA_NUA", "reprova se «raccolta dei dati» contar como colheita",
     [('PRODUCAO: (r"raccolto",', 'PRODUCAO: (r"raccolt[oa]",')]),
    ("M7_RESA_NUA", "reprova se «resa possibile» contar como rendimento",
     [(r'r"res[ae]\s+(?:medi[ae]|per', r'r"res[ae](?:\s*|\s+medi[ae]|per')]),
    ("M8_EVENTO_SEM_AGRO", "regra 3: reprova se evento fora do agro virar evento tecnico",
     # sem o `agro = …` o mutante rebentava em agro[0] (erro, nao falha): nao provava nada
     [("    if m and agro:", "    if m:\n        agro = agro or ['(nenhuma)']")]),
    ("M9_AVISO_ACADEMICO_E_EVENTO", "regra 3: reprova se aviso de exame virar evento tecnico",
     [("    if m and _RE_ACADEMICO.search(abertura):", "    if False:")]),
    ("M10_NEGOCIO_SEM_AGRO", "regra 4: reprova se empresa fora do agro virar negocio agro",
     [("if len(agro) < AGRO_PARA_NEGOCIO or len(conceitos[NEGOCIO]) < MINIMO_NEGOCIO:",
       "if len(conceitos[NEGOCIO]) < MINIMO_NEGOCIO:")]),
    ("M11_NEGOCIO_COM_POUCO", "regra 4: reprova se duas palavras de negocio chegarem",
     [("if len(agro) < AGRO_PARA_NEGOCIO or len(conceitos[NEGOCIO]) < MINIMO_NEGOCIO:",
       "if len(agro) < AGRO_PARA_NEGOCIO:")]),
    ("M12_EMPATE_DECIDE", "regra 5: reprova se o empate escolher um tipo",
     [("fortes[0][0] > fortes[1][0]", "fortes[0][0] >= fortes[1][0]")]),
    ("M13_TITULO_E_NAO_FACTO", "regra 6: reprova se um titulo solto virar «nao e facto»",
     [(' and ev["LINHAS_DE_CORPO"] >= LINHAS_PARA_NAO_FATO:', ":")]),
    ("M14_SEM_CORPO_E_NAO_FACTO", "regra 1: reprova se texto sem corpo virar «nao e facto» em vez de NAO_SEI",
     [('        return {"fact_kind": NAO_SEI, "fact_kind_basis": "NAO_SEI · o texto não tem corpo',
       '        return {"fact_kind": NAO_FATO, "fact_kind_basis": "NAO_SEI · o texto não tem corpo')]),
    ("M15_CAMPO_ACEITA_LUGAR_DE_EVENTO", "D62: reprova se o lugar de evento virar lugar de praga",
     [("        aceita = (FT.CAMPO,)", "        aceita = (FT.CAMPO, FT.EVENTO)")]),
    ("M16_EVENTO_FICA_COM_O_LUGAR_DO_CAMPO", "D62: reprova se o evento tecnico ficar com o lugar da praga",
     [("        aceita = (FT.EVENTO,)", "        return r")]),
    ("M17_BASE_SEM_PORQUE", "reprova se a troca de lugar nao ficar explicada na base",
     [('"%s · o facto é %s: o lugar %s não é lugar deste facto"', '"%s%s%s"')]),
]


def correr(pasta):
    p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_tipo_do_fato"], cwd=pasta,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ult = [l for l in p.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return p.returncode, " | ".join(ult)


def main():
    orig = (RAIZ / ALVO).read_text(encoding="utf-8")
    res = {"DATASET": "MUTACAO-TIPO-DO-FATO-V1", "ALVO": ALVO,
           "ALVO_SHA256": hashlib.sha256(orig.encode("utf-8")).hexdigest(), "MUTANTES": []}
    with tempfile.TemporaryDirectory(prefix="mut-tipo-") as tmp:
        tmp = Path(tmp)
        for d in ("leis", "tests"):
            shutil.copytree(RAIZ / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        rc, linha = correr(tmp)
        res["SEM_MUTANTE"] = {"RC": rc, "SAIDA": linha}
        if rc != 0:
            print("o original ja falha:", linha)
            sys.exit(2)
        for nome, regra, trocas in MUTANTES:
            s = orig
            for a, b in trocas:
                if s.count(a) != 1:
                    raise SystemExit("mutante %s: trecho aparece %d vezes: %r" % (nome, s.count(a), a[:60]))
                s = s.replace(a, b)
            (tmp / ALVO).write_text(s, encoding="utf-8")
            shutil.rmtree(tmp / "leis" / "__pycache__", ignore_errors=True)
            comp = subprocess.run([sys.executable, "-c", "import ast,sys;ast.parse(open(sys.argv[1],encoding='utf-8').read())",
                                   str(tmp / ALVO)], capture_output=True, text=True)
            rc, linha = correr(tmp)
            morto = rc != 0 and comp.returncode == 0 and "FAILED (failures=" in linha
            res["MUTANTES"].append({"MUTANTE": nome, "REGRA": regra, "COMPILA": comp.returncode == 0,
                                    "RC": rc, "SAIDA": linha, "RESULTADO": "MORTO" if morto else "SOBREVIVEU"})
            print("%-38s %s  %s" % (nome, "MORTO" if morto else "SOBREVIVEU", linha))
        (tmp / ALVO).write_text(orig, encoding="utf-8")
    res["MORTOS"] = sum(m["RESULTADO"] == "MORTO" for m in res["MUTANTES"])
    res["TOTAL"] = len(res["MUTANTES"])
    out = Path(__file__).with_name("MUTACAO-TIPO-DO-FATO-V1.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mortos %d de %d -> %s" % (res["MORTOS"], res["TOTAL"], out.name))
    sys.exit(0 if res["MORTOS"] == res["TOTAL"] else 1)


if __name__ == "__main__":
    main()
