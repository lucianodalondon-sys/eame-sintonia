#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOLETIM-POR-SECAO · teste de mutacao (D18/D19). Sem rede.

Cada mutante estraga UMA regra numa COPIA da arvore (pasta temporaria; a arvore nao e tocada) e corre
tests/test_boletim_por_secao.py contra ela. So conta MORTO quando um teste FALHA por assert (erro de execucao
nao prova nada). Mutante que sobrevive = o teste nao guarda a regra.

    py scripts/lugar_fato/mutar_boletim_por_secao.py   -> escreve MUTACAO-BOLETIM-POR-SECAO-V1.json ao lado
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TESTE = "tests/test_boletim_por_secao.py"
BC, FT, AD = "leis/boletim_do_campo.py", "leis/fato_do_texto.py", "admissao/admissao.py"

MUTANTES = [
    ("M01_SECAO_DO_DOCUMENTO", "D18: a afirmacao herda a 1.a secao do documento, nao a sua", BC,
     'secao = next((s for s in reversed(todas) if s["INICIO"] <= inicio < s["FIM"]), None)',
     'secao = todas[0] if todas else None'),
    # LOTE6-INTEGRA (declarado): desde que o lugar passa pela trava da lei (`_trava_do_lugar`, COL-LAW-032), so
    # promover o cabecalho visual no extrator ficou mutante EQUIVALENTE (a lei devolve UNRESOLVED; medido: M02
    # sobreviveu com o teste OK). O defeito real do extrator e os DOIS juntos — promover E desligar a trava.
    ("M02_CABECALHO_VISUAL_VIRA_FATO", "o cabecalho so na imagem vira FACT_LOCATION (com a trava da lei desligada)",
     BC, [('        lugar = {"VALOR": UNRESOLVED, "LOCATION_SOURCE": VISUAL_HEADER_CANDIDATE,',
           '        lugar = {"VALOR": candidato["ROTULO_NA_IMAGEM"], "LOCATION_SOURCE": VISUAL_HEADER_CANDIDATE,'),
          ("    lugar = _trava_do_lugar(lugar)\n", "")], None),
    ("M03_SEM_CORTE_DE_SECAO", "o paragrafo atravessa rotulo/troca de secao", BC,
     "    for rx in (_RE_CORTE_DE_PARAGRAFO, _RE_ROTULO):", "    for rx in ():"),
    ("M04_SEM_ENTIDADE_CONCORRENTE", "titulo diz A, paragrafo diz B, e fica A", BC,
     "            if concorrentes:", "            if False:"),
    ("M05_PARAGRAFO_INTEIRO", "a janela do paragrafo vai ate ao inicio da secao", BC,
     "    comeco = comecos[-2] if len(comecos) >= 2 else 0", "    comeco = 0"),
    ("M06_SO_A_PRIMEIRA_PRAGA_DO_TRECHO", "o trecho com duas pragas guarda so uma (C05)", BC,
     '        return {"VALOR": no_trecho, "ENTITY_SOURCE": SPAN,', '        return {"VALOR": no_trecho[:1], "ENTITY_SOURCE": SPAN,'),
    ("M07_EXPRESSAO_SEM_NOME_VIRA_PONTO", "«zone irrigue … di tutti comprensori» vira lugar resolvido (C08)", BC,
     '"VALOR": expr if nomeado else UNRESOLVED,', '"VALOR": expr,'),
    ("M08_EXCLUSAO_RESOLVE", "«TERRITORIO ESCLUSO X» vira o lugar X", BC,
     "    if _RE_EXCLUSAO.search(c):", "    if False:"),
    ("M09_TITULO_VENCE_O_TRECHO", "o titulo passa a frente do nome escrito no trecho", BC,
     '    if no_trecho:\n        return {"VALOR": no_trecho,',
     '    if no_trecho and not (titulos_da_secao or titulos_do_doc):\n        return {"VALOR": no_trecho,'),
    ("M10_DOCUMENTO_VENCE_A_SECAO", "o titulo do documento passa a frente do titulo da secao", BC,
     "((SECTION_TITLE, titulos_da_secao), (DOCUMENT_TITLE, titulos_do_doc))",
     "((DOCUMENT_TITLE, titulos_do_doc), (SECTION_TITLE, titulos_da_secao))"),
    ("M11_RODAPE_NAO_FECHA_A_SECAO", "o anexo depois do rodape herda o comprensorio", BC,
     "        if aberta and (_RE_FIM_DE_PAGINA.match(l) or", "        if False and (_RE_FIM_DE_PAGINA.match(l) or"),
    ("M12_CABECALHO_PARTIDO_NAO_JUNTA", "«COMPRENSORIO - LE - PIANURA» + «SALENTINA SUD» fica pela metade", BC,
     '                cab = cab + " " + prox.strip()', "                cab = cab"),
    ("M13_REPETICAO_CONTA_INSTITUICOES", "o mesmo paragrafo em 3 secoes conta 3 instituicoes (C07)", BC,
     '"INSTITUICOES_INDEPENDENTES": 1 if lidas else 0', '"INSTITUICOES_INDEPENDENTES": len(lidas)'),
    ("M14_AFIRMACAO_COM_BARRA_LATERAL", "D19: ler_afirmacao le a manchete vizinha como contexto", BC,
     "    t = _ft().sem_vizinhos(texto)           # D19", "    t = str(texto or '')           # D19"),
    ("M15_BOLETIM_COM_BARRA_LATERAL", "D19: ler_boletim abre secao de cultura na manchete vizinha", BC,
     "    texto = _ft().sem_vizinhos(texto)        # D19", "    texto = str(texto or '')        # D19"),
    ("M16_MESMA_CULTURA_VAZIA", "«oliveto» no paragrafo concorre com «olivo» do titulo (C02)", BC,
     'MESMA_CULTURA = {"oliveto": "olivo",', 'MESMA_CULTURA = {"_": "olivo",'),
    ("M17_SEM_MARGARONIA", "o vocabulario perde a margaronia (C05)", BC,
     '    r"margaronia", r"palpita', '    r"(?!x)xmargaronia", r"palpita'),
    ("M18_CORPO_COM_BARRA_LATERAL", "D19: o corpo do texto le a barra lateral (Basilicata)", FT,
     "    texto = sem_vizinhos(texto)\n    fica = []", "    fica = []"),
    ("M19_ROTULO_VIZINHO_CEGO", "D19: «Ultime notizie» deixa de ser rotulo de bloco vizinho", FT,
     '_RE_ROTULO_VIZINHO = re.compile(r"^\\s*(?:%s)', '_RE_ROTULO_VIZINHO = re.compile(r"(?!x)x^\\s*(?:%s)'),
    ("M20_TITULO_DA_CHAVE_COM_VIZINHOS", "D19: a 1.a linha da chave de cultura e a manchete vizinha", AD,
     '    texto = FT.sem_vizinhos(str(item.get("texto") or ""))', '    texto = str(item.get("texto") or "")'),
    ("M21_SEM_JANELA_DO_PARAGRAFO", "o contexto do paragrafo deixa de existir (C09 SA-03)", BC,
     "    no_paragrafo = t[comeco:inicio]", "    no_paragrafo = ''"),
]


def correr(raiz: Path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
               HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
    p = subprocess.run([sys.executable, TESTE], cwd=raiz, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    fim = [l for l in p.stderr.strip().splitlines() if l.strip()]
    return p.returncode, (fim[-1] if fim else "")


def main():
    res = {"DATASET": "MUTACAO-BOLETIM-POR-SECAO-V1", "TESTE": TESTE, "MUTANTES": []}
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t) / "arvore"
        shutil.copytree(RAIZ, tmp, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
        rc, linha = correr(tmp)
        res["SEM_MUTANTE"] = {"RC": rc, "SAIDA": linha}
        if rc != 0:
            print("o original ja falha:", linha)
            sys.exit(2)
        originais = {f: (tmp / f).read_text(encoding="utf-8") for f in (BC, FT, AD)}
        for nome, regra, alvo, a, b in MUTANTES:
            s = originais[alvo]
            for a1, b1 in (a if isinstance(a, list) else [(a, b)]):
                if s.count(a1) != 1:
                    raise SystemExit("mutante %s: trecho aparece %d vezes: %r" % (nome, s.count(a1), a1[:70]))
                s = s.replace(a1, b1)
            (tmp / alvo).write_text(s, encoding="utf-8")
            try:
                ast.parse(s)
                compila = True
            except SyntaxError:
                compila = False
            rc, linha = correr(tmp)
            morto = rc != 0 and compila and "FAILED (failures=" in linha
            res["MUTANTES"].append({"MUTANTE": nome, "REGRA": regra, "ALVO": alvo, "COMPILA": compila, "RC": rc,
                                    "SAIDA": linha, "RESULTADO": "MORTO" if morto else "SOBREVIVEU"})
            print("%-36s %s  %s" % (nome, "MORTO" if morto else "SOBREVIVEU", linha))
            (tmp / alvo).write_text(originais[alvo], encoding="utf-8")
    res["MORTOS"] = sum(m["RESULTADO"] == "MORTO" for m in res["MUTANTES"])
    res["TOTAL"] = len(res["MUTANTES"])
    out = Path(__file__).with_name("MUTACAO-BOLETIM-POR-SECAO-V1.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mortos %d de %d -> %s" % (res["MORTOS"], res["TOTAL"], out.name))
    sys.exit(0 if res["MORTOS"] == res["TOTAL"] else 1)


if __name__ == "__main__":
    main()
