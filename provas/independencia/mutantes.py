"""INDEPENDENCIA-V1 — prova de mutacao. Planta UM defeito de cada vez, corre o teste da missao, e restaura os
BYTES originais (guardados em memoria, nunca `git checkout`). Um mutante que sobrevive e um buraco no teste.
uso: py -B provas/independencia/mutantes.py [saida.json]"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G, C, V = "motor/grafo_de_dependencia.py", "motor/corrida_da_inteligencia.py", "motor/v21_oportunidades.py"
MUTANTES = [
    ("M01 sha nao conta como documento", G, 'k.add("SHA:" + s.lower())', 'pass'),
    ("M02 endereco nao conta como documento", G, 'k.add("URL:" + e)', 'pass'),
    ("M03 documento_id ignorado", G, 'k.add("DOC:" + d)', 'pass'),
    ("M04 mesmo documento nao une a fonte", G, "            uf.unir(g[0], i)", "            pass"),
    ("M05 SOURCE_ID nao une", G, '        k.add("SID:" + str(s).strip())', '        pass'),
    ("M06 dominio vira host inteiro (subdominio = fonte nova)", G, "    return \".\".join(rot[-n:])",
     "    return \".\".join(rot)"),
    ("M07 convergencia pelo maximo (sem originador conta)", G, "    elif minimo >= 2:", "    elif maximo >= 2:"),
    ("M08 estrutural conta como fonte", G, "    estr = [e for e in evidencias if estrutural and estrutural(e)]\n"
     "    sinais = [e for e in evidencias if not (estrutural and estrutural(e))]",
     "    estr = [e for e in evidencias if estrutural and estrutural(e)]\n    sinais = list(evidencias)"),
    ("M09 fato desconhecido converge", G, '        if k == NAO_SEI and g["CONVERGENCE"] == CONVERGE:',
     '        if False:'),
    ("M10 fonte dominante pela menor", G, '    familias.sort(key=lambda f: (-f["SINAIS"], f["ORIGINADOR"]))',
     '    familias.sort(key=lambda f: (f["SINAIS"], f["ORIGINADOR"]))'),
    ("M11 republicacao declarada ignorada", G, '    dec = _primeiro(ev, CAMPOS_DE_ORIGINADOR)', '    dec = None'),
    ("M12 SOURCE_ID de plataforma volta a unir anunciantes", G,
     '    if base in ("DECLARADO", "PAGINA", "PLATAFORMA"):\n        return k, base', '    if False:\n        pass'),
    ("M12b doi.org volta a ser fonte", G, '    if end and dominio_registavel(end.partition("/")[0].split("?")[0]) in RESOLVEDORES:',
     '    if False:'),
    ("M12c instituicao ignorada no resolvedor", G, '            k.add("ORIG:instituicao/" + inst.lower())\n            return k, "INSTITUICAO"',
     '            pass'),
    ("M13 corrida nao marca a duplicata", C, '                por_id[c]["DUPLICATA_DE"] = d["MANTIDA"]', '                pass'),
    ("M14 corrida ignora o sha do item", C, "(GD.CAMPOS_DE_DOCUMENTO + GD.CAMPOS_DE_SHA",
     "(GD.CAMPOS_DE_DOCUMENTO"),
    ("M14b corrida ignora os campos de endereco do item", C, "+ GD.CAMPOS_DE_ENDERECO + GD.CAMPOS_DE_ORIGINADOR",
     "+ GD.CAMPOS_DE_ORIGINADOR"),
    ("M14c corrida ignora o originador declarado", C, "+ GD.CAMPOS_DE_ENDERECO + GD.CAMPOS_DE_ORIGINADOR",
     "+ GD.CAMPOS_DE_ENDERECO"),
    ("M14d corrida ignora a pagina do anunciante", C, "                       + GD.CAMPOS_DE_PAGINA)", ")"),
    ("M15 corrida ignora o fato", C, '                              "_FATO": chave_do_fato(item)})',
     '                              "_FATO": None})'),
    ("M16 V2.1 MULTI_SOURCE sem teto", V, "        dim = dict(dim, MULTI_SOURCE=min(declarado,",
     "        dim = dict(dim, MULTI_SOURCE=max(declarado,"),
    ("M17 V2.1 rotulo vira fonte", V, "    return GD.grafo(ev, lambda e: e.get('ENTITY_TYPE') in TIPOS_ESTRUTURAIS)",
     "    return GD.grafo(ev)"),
]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
res = []
for nome, f, de, para in MUTANTES:
    p = os.path.join(RAIZ, f)
    orig = open(p, "rb").read()
    txt = orig.decode("utf-8")
    eol = "\r\n" if "\r\n" in txt else "\n"
    txt = txt.replace("\r\n", "\n")
    if txt.count(de) != 1:
        res.append({"MUTANTE": nome, "ESTADO": "NAO_PLANTADO", "PORQUE": f"alvo aparece {txt.count(de)} vezes"})
        print(nome, "NAO_PLANTADO")
        continue
    try:
        open(p, "wb").write(txt.replace(de, para).replace("\n", eol).encode("utf-8"))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_independencia_de_fontes"], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=900)
    finally:
        open(p, "wb").write(orig)
    import re
    mortos = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", r.stderr, re.M)))
    res.append({"MUTANTE": nome, "FICHEIRO": f, "ESTADO": "MORTO" if r.returncode else "SOBREVIVEU",
                "TESTES_QUE_APANHARAM": mortos})
    print(nome, "MORTO" if r.returncode else "SOBREVIVEU", len(mortos))
if len(sys.argv) > 1:
    open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
