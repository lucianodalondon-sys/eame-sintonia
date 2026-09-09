#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DA IMPRESSAO DA ARVORE-FONTE

    UMA LISTA DE EXCLUSAO QUE NINGUEM CONFERE E UMA PORTA DAS TRASEIRAS COM UM
    COMENTARIO BONITO POR CIMA.

A impressao so vale se a lista de `EXCLUIDO` for exactamente o que a cadeia
escreve. Excluir de MAIS e o erro perigoso: um ficheiro que alimenta o mapa e
fica de fora da impressao pode mudar sem a mover, e a tela ficaria VERDE sobre um
mapa que ja nao e o daquela arvore. Por isso estas provas nao leem a lista — elas
CORREM A CADEIA e vao ver o que ela mexeu.

As mutacoes correm sempre num clone descartavel. Uma prova que suja a arvore de
quem a corre e uma prova que muda aquilo que mede.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import impressao_da_arvore as IMP  # noqa: E402

CADEIA = json.loads((RAIZ / "system-map" / "scripts" / "CADEIA-DO-MAPA.json")
                    .read_text(encoding="utf-8"))
LEI = CADEIA["IMPRESSAO_DA_ARVORE"]

falhas: list[str] = []


def prova(id_: str, ok: bool, detalhe: str = ""):
    print(f"  {'PASS' if ok else 'FAIL':4s}  {id_:46s}{'' if ok else '  ' + detalhe}")
    if not ok:
        falhas.append(f"{id_}: {detalhe}")


def correr(cmd, cwd, entrada=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          input=entrada, encoding="utf-8")


def clone() -> Path:
    d = Path(tempfile.mkdtemp(prefix="impressao-"))
    r = correr(["git", "clone", "-q", "--no-hardlinks", "--shared",
                str(RAIZ), str(d / "r")], cwd=str(d))
    if r.returncode != 0:
        raise SystemExit(f"clone falhou: {r.stderr[:300]}")
    return d / "r"


def impressao_ali(raiz: Path, do_indice=True) -> str:
    """A MESMA lei, corrida noutra arvore. Sem segunda formula."""
    argv = ["-c", (
        "import sys,json;sys.path.insert(0,'system-map/scripts');"
        "import impressao_da_arvore as I;"
        f"print(I.{'do_indice' if do_indice else 'do_disco'}()[0])")]
    r = correr([sys.executable, *argv], cwd=str(raiz))
    if r.returncode != 0:
        raise SystemExit(f"impressao falhou em {raiz}: {r.stderr[-400:]}")
    return r.stdout.strip()


# ── 1 · AS DUAS LEITURAS DIZEM O MESMO ───────────────────────────────────────
# Uma le o disco (quem gera), a outra le o indice (quem implanta). Se elas
# divergissem, a prova de pertenca seria um numero que so bate por sorte.
disco, n_disco, ausentes = IMP.do_disco()
indice, n_indice = IMP.do_indice()
prova("as_duas_leituras_medem_o_mesmo_numero_de_ficheiros", n_disco == n_indice,
      f"disco={n_disco} indice={n_indice}")
sujo = correr(["git", "status", "--porcelain"], cwd=str(RAIZ)).stdout.strip()
if sujo:
    prova("arvore_limpa_para_comparar_disco_com_indice", True,
          "(saltada: arvore com trabalho por commitar)")
else:
    prova("disco_e_indice_dao_a_mesma_impressao", disco == indice,
          f"{disco[:12]} != {indice[:12]}")
prova("nenhum_ficheiro_rastreado_falta_ao_disco", not ausentes,
      f"{len(ausentes)} ausente(s)")

# ── 2 · A LISTA DE EXCLUSAO E EXACTAMENTE O QUE A CADEIA ESCREVE ─────────────
# Corre a cadeia inteira num clone e olha para o que ela mexeu. Excluir de menos
# da alarme falso; excluir de MAIS da verde falso, e verde falso e o unico erro
# que esta lei nao pode cometer.
r = clone()
for passo in CADEIA["REGERAR"]:
    x = correr([sys.executable, passo], cwd=str(r))
    if x.returncode != 0:
        prova(f"a_cadeia_corre_no_clone[{passo}]", False, x.stderr[-300:])
        break
else:
    prova("a_cadeia_corre_no_clone", True)
    mexidos = {ln[3:] for ln in
               correr(["git", "status", "--porcelain"], cwd=str(r)).stdout.splitlines()
               if ln.strip()}
    fora = {m for m in mexidos if not IMP.excluido(m)}
    prova("a_cadeia_nao_escreve_fora_da_lista_de_exclusao", not fora,
          f"escreveu fora: {sorted(fora)[:6]}")
    # E o contrario: nome na lista que ninguem escreve e exclusao a mais.
    inuteis = [e for e in LEI["EXCLUIDO"]
               if not any(m == e or m.startswith(e) for m in mexidos)
               and not any(str(p.relative_to(r)).startswith(e)
                           for p in r.rglob("*") if p.is_file())]
    prova("nenhum_nome_excluido_sem_ninguem_o_escrever", not inuteis,
          f"exclusao a mais: {inuteis}")

# ── 3 · GUARDAR O MAPA REGERADO NAO MOVE A IMPRESSAO ─────────────────────────
# Este e o defeito que a impressao veio fechar: o carimbo do commit anterior. Se
# guardar a saida movesse a impressao, ela teria o MESMO defeito com outro nome.
antes = impressao_ali(r)
correr(["git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"], cwd=str(r))
correr(["git", "-c", "user.email=t@t", "-c", "user.name=t",
        "commit", "-q", "-m", "so as saidas da cadeia"], cwd=str(r))
depois = impressao_ali(r)
prova("guardar_o_mapa_regerado_nao_move_a_impressao", antes == depois,
      f"{antes[:12]} -> {depois[:12]}")

# ── 4 · MEXER NUMA FONTE MOVE A IMPRESSAO ────────────────────────────────────
# A prova simetrica. Uma impressao que nunca se move nao mede nada.
alvo = r / "AGENTS.md"
alvo.write_text(alvo.read_text(encoding="utf-8") + "\n<!-- mutacao -->\n",
                encoding="utf-8")
correr(["git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"], cwd=str(r))
prova("mexer_numa_fonte_move_a_impressao", impressao_ali(r) != depois,
      "editar AGENTS.md deixou a impressao igual")

# ── 5 · O `.vercelignore` NAO TOCA NA IMPRESSAO ──────────────────────────────
# A razao de tudo isto: o contentor da Vercel recebe a arvore mutilada e ainda
# assim tem de saber que arvore esta a implantar. Medido numa build real: 1126
# de 1504 ficheiros ausentes do disco, indice intacto.
correr(["git", "-c", "user.email=t@t", "-c", "user.name=t", "checkout", "-q", "--", "."],
       cwd=str(r))
correr(["git", "-c", "user.email=t@t", "-c", "user.name=t", "reset", "-q", "--hard"],
       cwd=str(r))
inteira = impressao_ali(r)
apagados = 0
for nome in ["build", "data", "docs", "handoff", "research", "prototype",
             "supabase", "scripts", "tests", ".github"]:
    d = r / nome
    if d.exists():
        apagados += sum(1 for _ in d.rglob("*") if _.is_file())
        shutil.rmtree(d)
prova("a_simulacao_apagou_mesmo_ficheiros_do_disco", apagados > 100,
      f"so {apagados} ficheiro(s) apagado(s): a simulacao nao simulou nada")
ausentes_agora = len(correr(["git", "ls-files", "--deleted"], cwd=str(r))
                     .stdout.split("\n")) - 1
prova("o_indice_sobrevive_ao_apagamento_do_disco", ausentes_agora > 100,
      f"{ausentes_agora} ausente(s) — o git devia continuar a conhece-los")
prova("arvore_mutilada_da_a_mesma_impressao_da_arvore_inteira",
      impressao_ali(r) == inteira,
      "o contentor da Vercel nao conseguiria provar que arvore implanta")

# ── 6 · O LADO NODE E O LADO PYTHON DIZEM O MESMO NUMERO ─────────────────────
# Nao ha maneira de correr uma formula so nos dois sitios: quem gera le o disco
# antes de o commit existir, quem implanta le o indice sem o disco. O que NAO
# pode divergir e a formula, e por isso ela vive em `CADEIA-DO-MAPA.json` e isto
# corre as duas contra a mesma arvore.
x = correr(["node", "system-map/scripts/publicar_no_deploy.mjs"], cwd=str(r))
art = r / "italia-portale" / "client" / "system-map" / CADEIA["ARTEFATO_DE_DEPLOY"]
if not art.exists():
    prova("o_publicador_escreve_o_artefato_no_clone", False, x.stderr[-300:])
else:
    d = json.loads(art.read_text(encoding="utf-8"))
    prova("node_e_python_calculam_a_mesma_impressao",
          d.get("SOURCE_TREE_FINGERPRINT") == impressao_ali(r),
          f"node={str(d.get('SOURCE_TREE_FINGERPRINT'))[:12]} "
          f"python={impressao_ali(r)[:12]}")
    prova("o_artefato_separa_a_impressao_da_arvore_da_do_mapa",
          "SOURCE_TREE_FINGERPRINT" in d and "MAP_SOURCE_TREE_FINGERPRINT" in d
          and "MAP_BELONGS_TO_DEPLOYED_TREE" in d,
          "publicar so o veredito esconde de onde ele veio")

shutil.rmtree(r.parent, ignore_errors=True)

# ── 7 · O NOME DO PORTAO VIVE NUM SITIO SO ───────────────────────────────────
# A tela procura o portao do mapa por NOME na API do GitHub. Se o workflow e o
# manifesto disserem nomes diferentes, a tela procura um portao que nao existe e
# cai para UNKNOWN sem ninguem perceber porque.
js = (RAIZ / "system-map" / "app" / "map.js").read_text(encoding="utf-8")
portao = CADEIA.get("PORTAO_DO_MAPA") or {}
wf = (RAIZ / portao.get("WORKFLOW", ".github/workflows/system-map.yml"))
texto = wf.read_text(encoding="utf-8") if wf.exists() else ""
prova("o_manifesto_declara_o_portao_do_mapa", bool(portao.get("NOME")))
prova("o_workflow_usa_o_nome_declarado",
      f"name: {portao.get('NOME')}" in texto,
      f"«{portao.get('NOME')}» nao aparece em {portao.get('WORKFLOW')}")
prova("o_job_declarado_existe_no_workflow",
      f"\n  {portao.get('JOB')}:\n" in texto,
      f"job «{portao.get('JOB')}» nao existe")
def _comandos(bloco: str) -> str:
    """So o que CORRE. Comentario nao e comando — e a guarda apanhou-me nisto.

    A primeira versao olhava para o bloco inteiro e reprovou porque o comentario
    do passo 1 NOMEIA `test_system_map.py` ao explicar quem confere a lista da
    cadeia. Explicar quem confere e o trabalho de um comentario.

        MENCIONAR NAO E CORRER. A segunda vez que isto me apanha nesta missao.
    """
    return "\n".join(l for l in bloco.split("\n")
                     if not l.lstrip().startswith("#"))


bloco_do_mapa = _comandos(texto.split(f"\n  {portao.get('JOB')}:\n")[-1]
                          .split("\n  regras:\n")[0].split("\n  coleta:\n")[0])
prova("o_portao_do_mapa_nao_corre_as_provas_da_coleta",
      "padrao_da_coleta.py" not in bloco_do_mapa,
      "um veredito sobre duas perguntas nao responde a nenhuma")
# O PORTAO QUE A TELA LE SO PODE RESPONDER PELA FRESCURA. Se um dia alguem lhe
# acrescentar uma prova de qualidade — as regras, o pacote, o segredo — o
# veredito volta a misturar duas perguntas e a tela volta a pintar BROKEN por
# uma coisa que nao e proveniencia. Foi exactamente o que aconteceu, medido no
# GitHub: passos 1, 2 e 2b verdes, e o job vermelho no passo 4.
for intruso in ("test_system_map.py", "test_freshness.mjs",
                "test_impressao_da_arvore.py", "publicar_no_deploy.mjs"):
    prova(f"o_portao_da_frescura_nao_carrega[{intruso}]",
          intruso not in bloco_do_mapa,
          "o veredito que a tela le so pode responder pela frescura")
regras = CADEIA.get("PORTAO_DAS_REGRAS") or {}
prova("o_portao_das_regras_existe_e_esta_declarado",
      bool(regras.get("NOME")) and f"name: {regras.get('NOME')}" in texto,
      "separar sem declarar deixaria as provas a correr sem ninguem as ler")
bloco_das_regras = _comandos(texto.split(f"\n  {regras.get('JOB')}:\n")[-1].split("\n  coleta:\n")[0])
for exigido in ("test_system_map.py", "test_freshness.mjs",
                "test_impressao_da_arvore.py", "publicar_no_deploy.mjs"):
    prova(f"as_provas_separadas_continuam_a_correr[{exigido}]",
          exigido in bloco_das_regras,
          "SEPARAR NAO E DESLIGAR: a prova tem de continuar a reprovar a build")
prova("a_tela_mostra_o_portao_das_regras",
      "MAP_RULES_GATE_NAME" in js,
      "esconder o portao das regras seria comprar o verde com silencio")
# ⚠️ A PRIMEIRA VERSAO DESTA PROVA PROCURAVA O NOME NO FICHEIRO INTEIRO, e
# reprovou por causa de um COMENTARIO — a lista dos factos separados nomeia
# «SYSTEM MAP CHECK» como texto, e nomear e o trabalho de um comentario. O
# defeito a apanhar e outro: o nome ESCRITO COMO LITERAL no codigo, que e a
# segunda copia capaz de divergir do manifesto sem ninguem reparar.
#
#     MENCIONAR NAO E CODIFICAR. Uma guarda que nao separa as duas coisas
#     ensina a apagar o comentario, que e o oposto do que se quer.
literais = [f"{a}{portao.get('NOME')}{a}" for a in ("'", '"', "`")]
prova("a_tela_nao_traz_o_nome_do_portao_como_literal",
      not any(x in js for x in literais),
      "o nome tem de viajar no artefato, nao ser uma segunda copia no browser")
prova("a_tela_le_o_nome_do_portao_do_artefato",
      "MAP_GATE_NAME" in js,
      "sem isto a tela nao sabe por que portao perguntar")

print()
if falhas:
    print(f"TESTES_IMPRESSAO=FAIL · {len(falhas)} reprovada(s): "
          + ", ".join(f.split(':')[0] for f in falhas))
    raise SystemExit(1)
print("TESTES_IMPRESSAO=PASS · a impressao mede a arvore, e a lista confere-se sozinha")
