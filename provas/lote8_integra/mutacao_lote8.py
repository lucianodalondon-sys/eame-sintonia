"""LOTE8-INTEGRA · mutacao das JUNCOES (o que so existe com os ramos juntos).

    python3 provas/lote8_integra/mutacao_lote8.py [--ref=HEAD]

A copia sai de `git archive <ref>` (o repositorio nao e tocado). Cada mutante troca UM trecho exacto de
um ficheiro (trecho que nao aparece exactamente uma vez falha alto), corre os testes que devem apanha-lo
e repoe o ficheiro. MORTO = algum dos testes sai com codigo != 0. Resultado em
provas/lote8_integra/MUTACAO-JUNCOES-LOTE8.json.

As suites proprias de cada ramo correm-se a parte (ver LOTE8-INTEGRA.md §5); aqui so as juncoes.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = os.path.join(RAIZ, "provas", "lote8_integra", "MUTACAO-JUNCOES-LOTE8.json")
PORTA = "motor/porta_da_referencia.py"
ACERVO = "pacote/acervo_na_intelligence.py"
T_PORTA = ["-m", "unittest", "tests.test_porta_unica_referencia.J_Lote8LigacaoHerdaOGrao", "tests.test_ligacao_adama"]
T_ACERVO = ["-m", "unittest", "tests.test_lote8_juncoes.J_Acervo", "tests.test_acervo_na_intelligence"]
T_BUSCA = ["-m", "unittest", "tests.test_lote8_juncoes.J_Busca"]
T_LINHAS = ["-m", "unittest", "tests.test_lote8_juncoes.J_Linhas"]
T_P6 = ["node", "tests/test_pote_no_casco.mjs"]
T_PARIDADE = ["node", "regras/paridade_test.mjs"]

ANC_FALTAS = 'FALTAS = ("CULTURA", "PROBLEMA", "SUBSTANCIA", "REFERENCIA")\n'

# (nome, ficheiro, de, para, testes, preparo)
MUTANTES = [
    ("G1_ligacao_redefine_o_grao_igual", PORTA, ANC_FALTAS,
     ANC_FALTAS + 'NIVEIS_QUE_AUTORIZAM = ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA")\n'
                  'DECLARACAO_DE_PRODUTO = "DECLARACAO_DE_PRODUTO"\n', T_PORTA, None),
    ("G2_ligacao_redefine_o_grao_com_declaracao", PORTA, ANC_FALTAS,
     ANC_FALTAS + 'NIVEIS_QUE_AUTORIZAM = ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA", "DECLARACAO_DE_PRODUTO")\n',
     T_PORTA, None),
    ("G3_ligacao_com_lista_propria_de_niveis", PORTA,
     'fortes = {r: [u for u in us if u.get("LINK_LEVEL") in NIVEIS_QUE_AUTORIZAM] for r, us in por_reg.items()}',
     'fortes = {r: [u for u in us if u.get("LINK_LEVEL") in ("LINHA_DA_TABELA", "BLOCO_DA_CULTURA")] '
     'for r, us in por_reg.items()}', T_PORTA, None),
    ("A1_acervo_sem_a_porta_no_ctx", ACERVO,
     '"REF": ref,   # REF: o motor liga', '"REF_": ref,   # REF: o motor liga', T_ACERVO, None),
    ("A2_concorrente_sem_ligacao", ACERVO,
     '            "LIGACAO_ADAMA": a.get("LIGACAO_ADAMA") or PORTA.ligacao_adama(ref, {"VEM_DE": {}})}))',
     '            }))', T_ACERVO, None),
    ("A3_mercado_com_ligacao_feita_a_mao", ACERVO,
     '"LIGACAO_ADAMA": PORTA.ligacao_adama(ctx["REF"], {"VEM_DE": {}})}',
     '"LIGACAO_ADAMA": {"ESTADO": "NAO_SEI", "FALTA": ["CULTURA"]}}', T_ACERVO, None),
    ("A4_voz_sem_a_porta_aberta", ACERVO,
     'ex = VOZ.extrair(doc, referencia=ctx["REF"])', 'ex = VOZ.extrair(doc)', T_ACERVO, None),
    ("A5_arquivo_perde_a_ligacao", ACERVO,
     'for c in ("LOCATION_SOURCE", "LIGACAO_ADAMA"):', 'for c in ("LOCATION_SOURCE",):', T_ACERVO, None),
    ("B1_busca_sem_a_conta_no_reel", "coleta/linha_busca.py",
     r'instagram\.com/([A-Za-z0-9_.]+/)?(p|reel|reels|tv)/', r'instagram\.com/(p|reel|reels|tv)/', T_BUSCA, None),
    ("L1_linha_entra_so_por_o_ficheiro_existir", "ferramentas/big_collection/coleta_continua.py",
     'if linha["CHAMADA"] not in f.read_text(encoding="utf-8", errors="replace"):', 'if False:', T_LINHAS, None),
    ("D1_download_do_alvo_antes_da_decisao", "coleta/italy_pilot_collect.mjs",
     "      const decisao = decidirSobreDetalhe(alvo.url, {",
     "      await baixar(alvo.url); const decisao = decidirSobreDetalhe(alvo.url, {", T_PARIDADE, None),
    ("D2_download_condicional_antes_da_decisao", "coleta/italy_pilot_collect.mjs",
     "      const decisao = decidirSobreDetalhe(alvo.url, {",
     "      await baixar(alvo.url, 2, { condicional: true }); const decisao = decidirSobreDetalhe(alvo.url, {",
     T_PARIDADE, None),
    ("P6_volta_ao_split_por_LF_com_checkout_CRLF", "tests/test_pote_no_casco.mjs",
     "'.vercelignore'), 'utf8').split(/\\r?\\n/);", "'.vercelignore'), 'utf8').split('\\n');", T_P6, "CRLF_VERCELIGNORE"),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta, testes):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    cmd = testes if testes[0] == "node" else [sys.executable] + testes
    r = subprocess.run(cmd, cwd=pasta, env=env, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=1800)
    return r.returncode, r.stderr + r.stdout


def preparar(pasta, preparo):
    """Devolve a funcao que desfaz o preparo."""
    if preparo != "CRLF_VERCELIGNORE":
        return lambda: None
    f = os.path.join(pasta, ".vercelignore")
    orig = open(f, "rb").read()
    open(f, "wb").write(orig.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))   # o checkout do Windows
    return lambda: open(f, "wb").write(orig)


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="lote8-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "SEM_MUTANTE": {}, "MUTANTES": []}
    try:
        copia(ref, base)
        for nome, alvo, de, para, testes, preparo in MUTANTES:     # a copia limpa passa em cada conjunto
            chave = " ".join(testes) + (" +" + preparo if preparo else "")
            if chave in out["SEM_MUTANTE"]:
                continue
            desfaz = preparar(base, preparo)
            cod, cauda = correr(base, testes)
            desfaz()
            out["SEM_MUTANTE"][chave] = cod
            if cod != 0:
                raise SystemExit("a copia limpa nao passa em %s — o ataque nao tem base:\n%s" % (chave, cauda[-2000:]))
        for nome, alvo, de, para, testes, preparo in MUTANTES:
            f = os.path.join(base, alvo)
            orig = open(f, encoding="utf-8", newline="").read()
            if orig.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes em %s" % (nome, orig.count(de), alvo))
            open(f, "w", encoding="utf-8", newline="").write(orig.replace(de, para))
            desfaz = preparar(base, preparo)
            try:
                cod, cauda = correr(base, testes)
            finally:
                desfaz()
                open(f, "w", encoding="utf-8", newline="").write(orig)
            morto = cod != 0
            m = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\w+)", cauda, re.M) + re.findall(r"^FAIL: (P\d+[^\n]*)", cauda, re.M) + re.findall(r"^\s*FALHA (.+)$", cauda, re.M)
                           + re.findall(r"^(\w*Error): ", cauda, re.M)))
            out["MUTANTES"].append({"MUTANTE": nome, "ALVO": alvo, "MORTO": morto, "CODIGO": cod,
                                    "APANHADO_POR": m[:8], "CAUDA": None if morto else cauda[-800:]})
            print(nome, "MORTO" if morto else "SOBREVIVEU", m[:3], flush=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    with open(SAIDA, "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("LOTE8 JUNCOES: %d/%d mortos" % (out["MORTOS"], out["TOTAL"]))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    sys.exit(main())
