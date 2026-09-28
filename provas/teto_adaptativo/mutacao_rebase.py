"""D124-REBASE · o ataque: cada defeito plantado, um de cada vez, numa COPIA — e os testes tem de o apanhar.

    python3 provas/teto_adaptativo/mutacao_rebase.py [--ref=HEAD] [--so=NOME,NOME]

A copia sai de `git archive <ref>` (o repositorio nao e tocado). Cada mutante troca UM trecho exacto de um
ficheiro; um trecho que nao exista uma vez so falha alto (NAO_APLICOU: um mutante que nao muda nada nao prova
nada). Cada mutante corre SO os testes que o devem apanhar (a lista vai no resultado). MORTO = algum reprova.
Resultado em `provas/teto_adaptativo/MUTACAO-REBASE.json`.

Os da missao: teto infinito · orcamento ignorado · Crawl-delay ignorado (Python E Node) · robots PROIBE
ignorado · egresso IT ignorado. E os que o rebase abriu: sinais so pelo %header, livro D90 ilegivel / nao
migrado, sem livro = 40, sonda sempre ligada, pausa/Retry-After ignorados no agendador, livro so pelo nome
antigo, robots de 24 h sem janela (ReferenceError), janela D79 ligada por omissao — e as ancoras de mutacao
da producao que este rebase moveu (coleta continua, FEED-LIGADO, freio social), agora sobre o codigo novo.
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
PY, MJS, JS = "coleta/cortesia_adaptativa.py", "coleta/cortesia_adaptativa.mjs", "coleta/italy_pilot_collect.mjs"
CC, SONDA, MOTOR = "ferramentas/big_collection/coleta_continua.py", "ferramentas/big_collection/sonda_ligacao_sites.mjs", \
    "regras/motor_de_rota.mjs"


def U(*mods):
    return [sys.executable, "-m", "unittest"] + ["tests.%s" % m for m in mods]


T_REBASE = U("test_teto_adaptativo_rebase")
T_CC = U("test_coleta_continua")
T_CA = U("test_cortesia_adaptativa")
T_NODE = ["node", "provas/teto_adaptativo/transporte_rebase_local.mjs"]
T_FEED_LOCAL = ["node", "provas/scrap_evolucao/feed_ligado_local.mjs"]
T_FEED = ["node", "regras/feed_discovery_test.mjs"]
T_FREIO = U("test_freio_social", "test_teto_dominio", "test_dedup_video_social", "test_plano_onda_social_c2")

MUTANTES = [
    # ── os da missao ──────────────────────────────────────────────────────────────────────────────────
    ("M01_NODE_TETO_INFINITO", JS, "export const tetoDe = host => CORTESIA.cfg.TETO_POR_HOST\n",
     "export const tetoDe = host => Infinity ?? CORTESIA.cfg.TETO_POR_HOST\n", [T_NODE]),
    ("M02_PY_TETO_INFINITO", PY, "    cabem_24h = max(0, nivel - gasto)\n", "    cabem_24h = 10 ** 9\n", [T_CA]),
    ("M03_CC_ORCAMENTO_IGNORADO", CC, "            if g + p > nivel:\n", "            if False:\n", [T_REBASE, T_CC]),
    ("M04_PY_ORCAMENTO_IGNORADO", PY, '            elif e["CABEM_24H"] <= 0:\n', "            elif False:\n", [T_CA]),
    ("M05_NODE_ORCAMENTO_IGNORADO", MJS, "      else if (e.CABEM_24H <= 0) [porque, ate]",
     "      else if (false) [porque, ate]", [T_FEED_LOCAL, T_REBASE]),
    ("M06_PY_CRAWL_DELAY_IGNORADO", PY, '    pausa = max(float(k["PAUSA_S"]), crawl)\n', '    pausa = float(k["PAUSA_S"])\n',
     [T_REBASE]),
    ("M07_NODE_CRAWL_DELAY_IGNORADO_EM_UMAIDA", JS,
     "const minimo = Math.max(CORTESIA.cfg.PAUSA_S ?? CA.classeDe(dominio24h(host))[1].PAUSA_S, crawlDelay || 0) * 1000;",
     "const minimo = Math.max(CORTESIA.cfg.PAUSA_S ?? CA.classeDe(dominio24h(host))[1].PAUSA_S, 0) * 1000;", [T_NODE]),
    ("M08_NODE_CRAWL_DELAY_IGNORADO_NA_COTA", MJS, "  const pausa = Math.max(Number(k.PAUSA_S), crawl);",
     "  const pausa = Number(k.PAUSA_S);", [T_CA]),
    ("M09_NODE_ROBOTS_PROIBE_IGNORADO", JS, '  if (rb.estado === "LIDO" && !robotsPermite(rb.grupos, u.pathname + u.search))',
     "  if (false)", [T_NODE]),
    ("M10_EGRESSO_IT_ANTES_IGNORADO", CC, '    if not reg["EGRESSO_ANTES"].get("PASSA"):\n', "    if False:\n", [T_CC]),
    ("M11_EGRESSO_IT_DEPOIS_IGNORADO", CC, '    if not reg["EGRESSO_DEPOIS"].get("PASSA"):\n', "    if False:\n", [T_CC]),
    # ── o que o rebase abriu ──────────────────────────────────────────────────────────────────────────
    ("M12_NODE_SINAIS_SEM_O_FICHEIRO_D", JS, "      const lidos = cabecalhosDaResposta(cab);",
     "      const lidos = {};", [T_NODE]),
    ("M13_PY_LIVRO_D90_ILEGIVEL", PY, "    if e_livro_antigo(texto):\n        return eventos_do_livro_antigo(texto)\n", "",
     [T_REBASE, T_CC]),
    ("M14_NODE_LIVRO_D90_ILEGIVEL", MJS, "  if (eLivroAntigo(texto)) return eventosDoLivroAntigo(texto);\n", "", [T_REBASE]),
    ("M15_PY_LIVRO_D90_NAO_MIGRA", PY, "            migrar_livro_antigo(f)  ", "            pass  ", [T_REBASE]),
    ("M16_NODE_LIVRO_D90_NAO_MIGRA", MJS, "  if (existsSync(f) && eLivroAntigo(cabecaDe(f))) migrarLivroAntigo(f);", "",
     [T_REBASE]),
    ("M17_PY_D90_QTD_IGNORADA", PY, '        for _ in range(r["QTD"]):\n', "        for _ in range(1):\n", [T_REBASE]),
    ("M18_NODE_SEM_LIVRO_VALE_40", JS,
     "  ?? (livro24h() ? CA.tetoVigente(dominioRegistavel(host)) : CA.tetoSemLivro(dominioRegistavel(host)));",
     "  ?? CA.tetoVigente(dominioRegistavel(host));", [T_NODE]),
    ("M19_SONDA_SEMPRE_LIGADA", CC, '    if not isinstance(m, dict) or m.get("LIGADA") is not True:\n', "    if False:\n",
     [T_REBASE]),
    ("M20_SONDA_SEM_O_CASO_PAUSADO", SONDA, "    else if (pedB.length !== 0) porque", "    else if (false) porque",
     [T_REBASE]),
    ("M21_SONDA_NAO_CONTA_AS_RESERVAS", SONDA, "    else if (resA.length !== pedA.length) porque",
     "    else if (false) porque", [T_REBASE]),
    ("M22_CC_PAUSA_E_RETRY_AFTER_IGNORADOS", CC, "            if bloq > t:  ", "            if False:  ", [T_REBASE]),
    ("M23_CC_LIVRO_SO_PELO_NOME_ANTIGO", CC, '        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(livro_24h)\n', "", [T_CC]),
    ("M24_NODE_ROBOTS_24H_SEM_JANELA", JS, "const JANELA_24H_S = 24 * 3600;\n", "", [T_NODE, T_FEED_LOCAL]),
    ("M25_CC_JANELA_D79_LIGADA_POR_OMISSAO", CC, 'janela_h=24 if "--janela-24h" in argv else None)',
     "janela_h=24)", [T_REBASE]),
    ("M26_CC_TETO_DO_CICLO_SEM_O_GASTO_24H", CC, "            if g + orcamento.get(dd, 0) + p > nivel:",
     "            if orcamento.get(dd, 0) + p > nivel:", [T_REBASE]),
    # ── as ancoras da producao que o rebase moveu (o mesmo defeito, no codigo novo) ───────────────────
    ("P01_CC_M01_DOMINIO_BLOQUEADO_PASSA", CC, "if janela_h and v and agora_utc < v + timedelta(hours=janela_h):",
     "if False:", [T_CC]),
    ("P02_CC_M02_TETO_6_NO_CICLO", CC, "if g + orcamento.get(dd, 0) + p > nivel:",
     "if g + orcamento.get(dd, 0) + p > nivel + 1:", [T_CC]),
    ("P03_CC_M04_LINHAS_SEM_ORCAMENTO_PARTILHADO", CC, "orcamento=orcamento, max_fontes=max_fontes, janela_h=janela_h)",
     "orcamento={}, max_fontes=max_fontes, janela_h=janela_h)", [T_CC]),
    ("P04_CC_M17_TETO_24H_IGNORADO", CC, "if g + p > nivel:", "if False:", [T_CC]),
    ("P05_FEED_O_FEED_NAO_CONTA", JS, "  if (livro24h()) {\n    let r;",
     "  if (livro24h() && !/\\/feed\\/?$/.test(url)) {\n    let r;", [T_FEED_LOCAL]),
    ("P06_FEED_O_CONDICIONAL_NAO_RESERVA", JS, "  if (livro24h()) {\n    let r;",
     "  if (livro24h() && !condicional?.cabecalhos?.length) {\n    let r;", [T_FEED_LOCAL]),
    ("P07_FEED_D40_O_ITEM_COM_CORPO_OCUPA_LUGAR", MOTOR,
     "const aPedir = escolherAlvosD40(semCorpo, classificar, nomeDe, alvosPorFonte);",
     "const aPedir = escolherAlvosD40([...comCorpo, ...semCorpo], classificar, nomeDe, alvosPorFonte);", [T_FEED]),
    ("P08_FREIO_O_6_PASSA", "coleta/teto_da_onda.py", "    t_dom = teto(host)\n", "    t_dom = teto(host) + 1\n", [T_FREIO]),
    ("P09_FREIO_A_RODADA_DIZ_QUE_CABE_SEMPRE", "curadoria/plano_onda_social.py",
     '                     "CABE_NO_TETO": all(v <= teto_do_dominio(d) for d, v in prev.items())})\n',
     '                     "CABE_NO_TETO": True})\n', [T_FREIO]),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta, comandos):
    env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", NODE_DISABLE_COMPILE_CACHE="1",
               HTTPS_PROXY="http://127.0.0.1:9", HTTP_PROXY="http://127.0.0.1:9")
    cods, cauda = [], []
    for c in comandos:
        try:
            r = subprocess.run(c, cwd=pasta, env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=1800)
            rc, saida = r.returncode, r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            rc, saida = "TIMEOUT", ""
        cods.append(rc)
        falhas = re.findall(r"^(?:FAIL|ERROR): (\w+)", saida, re.M) + re.findall(r"^\s+FALHA (\S+)", saida, re.M)
        cauda.append("%s rc=%s falhas=%s" % (" ".join(c[-1:] if c[0] == "node" else c[3:]), rc, falhas[:6]))
    return (0 if all(x == 0 for x in cods) else 1), cauda


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    so = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--so=")), None)
    base = tempfile.mkdtemp(prefix="rebase-mutacao-")
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
    with open(os.path.join(RAIZ, "provas", "teto_adaptativo", "MUTACAO-REBASE.json"), "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=1)
    print("D124-REBASE MUTACAO:", out["RESUMO"])
    return 0 if mortos == len(out["MUTANTES"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
