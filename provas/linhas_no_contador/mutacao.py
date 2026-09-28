"""LINHAS-NO-CONTADOR · o ataque: cada defeito plantado, um de cada vez, numa COPIA — e os testes tem de o apanhar.

    python3 provas/linhas_no_contador/mutacao.py [--ref=HEAD] [--so=NOME,NOME]

A copia sai de `git archive <ref>` (o repositorio nao e tocado). Cada mutante troca UM trecho exacto de um
ficheiro; um trecho que nao exista uma vez so falha alto (NAO_APLICOU: um mutante que nao muda nada nao prova
nada). Cada mutante corre SO os testes que o devem apanhar. MORTO = algum reprova.
Resultado em `provas/linhas_no_contador/MUTACAO.json`.

Os da missao: linha sem reserva (CIENCIA, BUSCA-API, SOCIAL-YouTube, SOCIAL/BUSCA-scrap, e a porta) · reserva
depois do pedido · social abre Instagram (e o contador por cima do robots) · API acima do limite publicado ·
portao_real PASSA fixo. E os que esta missao abriu: a ligacao por texto de volta, a sonda sempre ligada ou sem
um dos casos, a linha ligada sem onda a correr, o gemeo Node a ler as APIs de outra maneira.
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
from concurrent.futures import ThreadPoolExecutor

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORTA, CA_PY, CA_MJS = "coleta/reserva_24h.py", "coleta/cortesia_adaptativa.py", "coleta/cortesia_adaptativa.mjs"
T6, API, YT, TETO, HTTP = ("coleta/pesquisadores_t6.py", "ferramentas/linha_busca/api_oficial.py",
                           "coleta/youtube_oficial.py", "coleta/teto_da_onda.py", "coleta/scrap_http.py")
POL, MZ, ROD = "regras/POLITICA-CORTESIA-ADAPTATIVA.json", "leis/social_matriz.py", "ferramentas/big_collection/rodadas.py"
CC, SONDA = "ferramentas/big_collection/coleta_continua.py", "ferramentas/big_collection/sonda_ligacao_linhas.py"


def U(*mods):
    return [sys.executable, "-m", "unittest"] + ["tests.%s" % m for m in mods]


T_LNC = U("test_linhas_no_contador")
T_LIG = U("test_coleta_continua.Linhas")
T_T6 = U("test_pesquisadores_t6")
T_CA = U("test_cortesia_adaptativa")

RESERVA = ("    r = _CA.reservar_ou_esperar(host, run_id=run_id, linha=linha, crawl_delay_s=crawl_delay_s,\n"
           "                                espera_max_s=espera_max_s, url=url)\n")

MUTANTES = [
    # ── linha sem reserva ─────────────────────────────────────────────────────────────────────────────
    ("M01_PORTA_PEDE_SEM_RESERVA", PORTA, RESERVA, '    r = {"ESTADO": "RESERVADO", "DOMINIO": host}\n', [T_LNC, T_LIG]),
    ("M02_PORTA_IGNORA_O_ADIADO", PORTA, '    if r["ESTADO"] != "RESERVADO":\n        return r, None\n    _PORTA',
     '    if False:\n        return r, None\n    _PORTA', [T_LNC, T_LIG]),
    ("M03_CIENCIA_CROSSREF_POR_FORA", T6, "\n        d, err = _get_no_contador(url_crossref(lote))\n",
     "\n        d, err = CP._get(url_crossref(lote))\n", [T_T6]),
    ("M04_CIENCIA_OPENALEX_POR_FORA", T6, "        url += '&api_key=' + urllib.parse.quote(chave)\n    return _get_no_contador(url)\n",
     "        url += '&api_key=' + urllib.parse.quote(chave)\n    return CP._get(url)\n", [T_T6]),
    ("M05_BUSCA_API_SEM_RESERVA", API, "    if not CA.livro():\n        return _pedir_um(url, cabecalhos, timeout)[:3]\n",
     "    if True:\n        return _pedir_um(url, cabecalhos, timeout)[:3]\n", [T_LIG, T_LNC]),
    ("M06_SOCIAL_YOUTUBE_SEM_RESERVA", YT, "    if not CA.livro():\n        return json.loads(_http_um(url)",
     "    if True:\n        return json.loads(_http_um(url)", [T_LIG, T_LNC]),
    ("M07_SOCIAL_SCRAP_SEM_RESERVA_NA_CORTESIA", TETO, "    if ca.livro():\n        # D124: a reserva",
     "    if False:\n        # D124: a reserva", [T_LIG]),
    ("M08_SCRAP_NAO_RESERVA_O_PEDIDO", HTTP,
     "            teto.reservar(host, url=req.full_url, quem='scrap_http', crawl_delay_s=_crawl_delay(req.full_url))",
     "            pass", [T_LIG]),
    ("M09_SCRAP_A_PORTA_TAPA_OUTRO_DOMINIO", PORTA, "        return k is not None and _CA.dominio_do_pedido(host, url) == k",
     "        return k is not None", [T_LNC]),
    # ── reserva depois do pedido ──────────────────────────────────────────────────────────────────────
    ("M10_PORTA_RESERVA_DEPOIS_DO_PEDIDO", PORTA, RESERVA,
     "    _cedo = tuple(fazer())\n    fazer = lambda: _cedo\n" + RESERVA, [T_LNC, T_LIG]),
    ("M11_PORTA_NAO_REGISTA_A_RESPOSTA", PORTA,
     "    _CA.registrar_resposta(host, int(st or 0), dict(cab or {}), marcas=marcas, url=url, corpo=corpo,",
     "    (lambda *a, **k: None)(host, int(st or 0), dict(cab or {}), marcas=marcas, url=url, corpo=corpo,",
     [T_LNC, T_LIG]),
    ("M12_PORTA_NAO_REGISTA_A_FALHA", PORTA,
     "        _CA.registrar_resposta(host, int(getattr(ex, \"code\", 0) or 0),",
     "        (lambda *a, **k: None)(host, int(getattr(ex, \"code\", 0) or 0),", [T_LNC, T_LIG]),
    # ── social abre Instagram / o contador por cima da politica ───────────────────────────────────────
    ("M13_SOCIAL_ABRE_INSTAGRAM", MZ, "              owner_authorized='SIM', platform_policy='NOT_MEASURED',",
     "              owner_authorized='SIM', platform_policy='ALLOWED',", [T_LNC]),
    ("M14_ORCAMENTO_LIVRE_PASSA_POR_CIMA_DO_ROBOTS", HTTP,
     "    ok, motivo = permitido(url)\n    if not ok:\n        raise RotaNaoPermitida('%s · %s' % (motivo, url))\n    h = {",
     "    ok, motivo = True, 'o contador tem lugar'\n    if not ok:\n        raise RotaNaoPermitida('%s · %s' % (motivo, url))\n    h = {",
     [T_LNC]),
    # ── API acima do limite publicado ─────────────────────────────────────────────────────────────────
    ("M15_API_CSE_ACIMA_DAS_100", POL, '"googleapis.com/customsearch": {"LIMITE_PUBLICADO_24H": 100, "ORCAMENTO_24H": 100,',
     '"googleapis.com/customsearch": {"LIMITE_PUBLICADO_24H": 100, "ORCAMENTO_24H": 1000,', [T_LNC]),
    ("M16_API_CSE_E_YOUTUBE_NO_MESMO_ORCAMENTO", CA_PY, "    if url and isinstance(rotas, list):",
     "    if False and isinstance(rotas, list):", [T_LNC]),
    ("M17_API_YOUTUBE_ACIMA_DAS_10000", POL, '"googleapis.com/youtube": {"LIMITE_PUBLICADO_24H": 10000, "ORCAMENTO_24H": 10000,',
     '"googleapis.com/youtube": {"LIMITE_PUBLICADO_24H": 10000, "ORCAMENTO_24H": 20000,', [T_LNC]),
    ("M18_API_NAO_SEI_COMECA_NO_DERIVADO", POL,
     '"crossref.org": {"LIMITE_PUBLICADO_24H": "NAO_SEI", "ORCAMENTO_INICIAL_24H": 5,',
     '"crossref.org": {"LIMITE_PUBLICADO_24H": "NAO_SEI", "ORCAMENTO_INICIAL_24H": 432000,', [T_LNC]),
    ("M19_API_PUBLICADA_DOBRA", CA_PY, '"DOBRA": bool(a.get("DOBRA", api["DOBRA"]))}', '"DOBRA": True}', [T_LNC, T_CA]),
    ("M20_NODE_LE_A_API_DE_OUTRA_MANEIRA", CA_MJS, "    const ini = a.ORCAMENTO_INICIAL_24H ?? a.ORCAMENTO_24H;",
     "    const ini = a.ORCAMENTO_24H;", [T_LNC]),
    # ── portao_real ───────────────────────────────────────────────────────────────────────────────────
    ("M21_PORTAO_REAL_PASSA_FIXO", ROD, '    return {"PASSA": r.returncode == 0,', '    return {"PASSA": True,', [T_LNC]),
    ("M22_PORTAO_REAL_SEM_IT", ROD, '"--portao-de-egresso", "IT",\n', '"--portao-de-egresso", "XX",\n', [T_LNC]),
    # ── a ligacao por comportamento ───────────────────────────────────────────────────────────────────
    ("M23_CC_O_TEXTO_LIGA_OUTRA_VEZ", CC, '        return {"LIGADA": False, "PORQUE": "SEM_SONDA:',
     '        return {"LIGADA": True, "PORQUE": "SEM_SONDA:', [T_LIG]),
    ("M24_SONDA_SEMPRE_LIGADA", SONDA, '    return {"LIGADA": not falhas,', '    return {"LIGADA": True,', [T_LIG]),
    ("M25_SONDA_NAO_CONTA_AS_RESERVAS", SONDA, "            elif len(res) != len(pedA):", "            elif False:", [T_LNC]),
    ("M26_SONDA_SEM_A_ORDEM", SONDA, "            elif not ordem:", "            elif False:", [T_LNC]),
    ("M27_SONDA_SEM_O_CASO_PAUSADO", SONDA, "            elif pedB:", "            elif False:", [T_LNC]),
    ("M28_SONDA_SEM_O_CASO_DO_SINAL", SONDA, "            elif len(sinais) < 2 or len(pedS) != 2:",
     "            elif False:", [T_LNC]),
    ("M29_CC_LINHA_SEM_ONDA_ENTRA_NO_CICLO", CC, '        if decl is not None and not decl.get("ONDA"):',
     "        if False:", [T_LNC]),
    ("M30_CC_PESQUISADORES_NO_CAMINHO_ERRADO", CC, '"TRANSPORTE": "ferramentas/seguir_pesquisadores/seguir.py"',
     '"TRANSPORTE": "coleta/seguir.py"', [T_LIG]),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta, comandos):
    env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9", NO_PROXY="127.0.0.1,localhost")
    cods, cauda = [], []
    for c in comandos:
        try:
            r = subprocess.run(c, cwd=pasta, env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=1800)
            rc, saida = r.returncode, r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            rc, saida = "TIMEOUT", ""
        cods.append(rc)
        falhas = re.findall(r"^(?:FAIL|ERROR): (\w+)", saida, re.M)
        cauda.append("%s rc=%s falhas=%s" % (" ".join(c[3:]), rc, falhas[:6]))
    return (0 if all(x == 0 for x in cods) else 1), cauda


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    so = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--so=")), None)
    base = tempfile.mkdtemp(prefix="linhas-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}
    alvo = [m for m in MUTANTES if so is None or m[0] in so]
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        todos = []
        for m in alvo:
            for c in m[4]:
                if c not in todos:
                    todos.append(c)
        cod, cauda = correr(limpa, todos)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": cauda}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base:\n" + "\n".join(cauda))

        def um(m):
            nome, f_alvo, de, para, comandos = m
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, f_alvo)
            with open(f, encoding="utf-8", newline="") as h:
                s = h.read().replace("\r\n", "\n")
            if s.count(de) != 1:
                shutil.rmtree(pasta, ignore_errors=True)
                return {"MUTANTE": nome, "ALVO": f_alvo, "ESTADO": "NAO_APLICOU", "OCORRENCIAS": s.count(de)}
            with open(f, "w", encoding="utf-8", newline="\n") as h:
                h.write(s.replace(de, para))
            c, cauda = correr(pasta, comandos)
            shutil.rmtree(pasta, ignore_errors=True)
            return {"MUTANTE": nome, "ALVO": f_alvo, "ESTADO": "MORTO" if c != 0 else "VIVO", "QUEM_APANHOU": cauda}
        with ThreadPoolExecutor(int(os.environ.get("MUTACAO_TRABALHADORES", "3"))) as ex:
            for r in ex.map(um, alvo):
                out["MUTANTES"].append(r)
                print("%-46s %s" % (r["MUTANTE"], r["ESTADO"]), flush=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
    out["RESUMO"] = "%d/%d mortos" % (mortos, len(out["MUTANTES"]))
    with open(os.path.join(RAIZ, "provas", "linhas_no_contador", "MUTACAO.json"), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("LINHAS-NO-CONTADOR MUTACAO:", out["RESUMO"])
    return 0 if mortos == len(out["MUTANTES"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
