#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DE UM DONO SO PARA A CADEIA DO MAPA — G5.

    python3 system-map/tests/test_uma_cadeia_um_dono.py

O manifesto declarava sete passos. O workflow corria vinte. E os DOIS jobs do
mesmo ficheiro corriam listas diferentes: `mapa` corria dezanove scripts,
`regras` corria sete — e ninguem comparava as duas.

    DOIS SITIOS COM A LISTA DOS PASSOS NAO SAO UMA LISTA REPETIDA:
    SAO DUAS CADEIAS, E UMA DELAS ESTA SEMPRE ERRADA SEM NINGUEM SABER.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    UNIVERSO     o que e EXECUTADO vem da maquina — workflows, build, npm —
                 e nunca de uma lista escrita aqui
    GOVERNANCA   tudo o que e executado esta declarado no manifesto
    SEM MORTOS   tudo o que esta declarado e executado por alguem
    SEM SEGUNDA  nenhum consumidor mantem lista propria, em YAML, JS, Python
                 ou array de shell
    EXTERNOS     o que a COLETA produz continua da COLETA
    FRONTEIRA    o G6 nao foi comecado: a ordem e a escrita, e ninguem a deriva

O QUE ELE NAO CONFERE, E PORQUE
-------------------------------
Nao confere se a ORDEM esta certa. Esta errada em dezanove sitios, e isso esta
medido e declarado — e o `G6`. G5 responde «quem diz quais passos existem»,
nao «em que ordem devem correr».

    NAO CODIFICAR NUMERO ESPERADO DE PASSOS. O UNIVERSO VEM DA MAQUINA.
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import cadeia_do_mapa as CAD                               # noqa: E402

FALHAS = []


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome + ("" if ok else "  " + str(porque)[:320]))
    if not ok:
        FALHAS.append(nome)


def texto(rel):
    f = RAIZ / rel
    return f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""


# ── 1 · O UNIVERSO, MEDIDO NA MAQUINA ─────────────────────────────────────
# Todo comando que corre um ficheiro do System Map, em qualquer sitio que o
# projecto execute: workflows do GitHub e scripts do npm (que e o que a Vercel
# corre). A expressao apanha comandos COMPOSTOS — `a && b` — porque esconder
# uma execucao atras de um `&&` era a maneira mais barata de fugir a esta prova.
ALVO = re.compile(r"(?:python3?|node)\s+(system-map/(?:scripts|tests)/[\w./-]+\.(?:py|mjs|js))")


def executado_por_workflow() -> dict:
    fora = {}
    for f in sorted((RAIZ / ".github" / "workflows").glob("*.yml")):
        for m in ALVO.finditer(f.read_text(encoding="utf-8")):
            fora.setdefault(m.group(1), set()).add(f.name)
    return fora


def executado_pelo_build() -> dict:
    fora = {}
    pkg = json.loads(texto("package.json") or "{}")
    for nome, cmd in (pkg.get("scripts") or {}).items():
        for m in ALVO.finditer(cmd):
            fora.setdefault(m.group(1), set()).add("package.json:" + nome)
    return fora


WF = executado_por_workflow()
BUILD = executado_pelo_build()
EXECUTADO = {}
for d in (WF, BUILD):
    for k, v in d.items():
        EXECUTADO.setdefault(k, set()).update(v)

# O corredor e o veiculo, nao um passo: ele nao mede nem escreve nada — corre o
# que o manifesto diz. Contar o veiculo como carga faria a prova exigir que ele
# se declarasse a si proprio.
CORREDOR = "system-map/scripts/correr_a_cadeia.py"
EXECUTADO.pop(CORREDOR, None)

# ⚠️ O CORREDOR EXPANDE UMA CATEGORIA. Procurar so nomes literais dava «vinte e
# dois passos mortos» — e a causa era esta prova, nao o manifesto: o workflow
# deixou de NOMEAR a cadeia, que era exactamente o objectivo.
#
#     UMA PROVA QUE SO VE NOMES LITERAIS DEIXA DE VER
#     ASSIM QUE ALGUEM FAZ A COISA CERTA.
#
# Resolver a invocacao pelo manifesto nao e circular: e ler o que a maquina
# corre («corredor REGERAR») e perguntar ao dono o que isso significa — que e o
# que o proprio runner faz em producao.
INVOCA = re.compile(re.escape(CORREDOR) + r"\s+(--listar\s+)?([A-Z_]+)")


def categorias_invocadas() -> dict:
    fora = {}
    for f in sorted((RAIZ / ".github" / "workflows").glob("*.yml")):
        for m in INVOCA.finditer(f.read_text(encoding="utf-8")):
            if not m.group(1):
                fora.setdefault(m.group(2), set()).add(f.name)
    pkg = json.loads(texto("package.json") or "{}")
    for nome, cmd in (pkg.get("scripts") or {}).items():
        for m in INVOCA.finditer(cmd):
            if not m.group(1):
                fora.setdefault(m.group(2), set()).add("package.json:" + nome)
    return fora


CATEGORIAS_CORRIDAS = categorias_invocadas()
for cat, onde in CATEGORIAS_CORRIDAS.items():
    if cat in CAD.CATEGORIAS:
        for e in CAD.executaveis_de(cat):
            EXECUTADO.setdefault(e, set()).update(
                "%s (via corredor %s)" % (o, cat) for o in onde)

# E o PUBLICADOR tambem corre a cadeia: ele le o manifesto e executa REGERAR e
# VALIDAR. Quem e executado por ele e executado.
if "system-map/scripts/publicar_no_deploy.mjs" in EXECUTADO:
    for cat in ("REGERAR", "VALIDAR"):
        for e in CAD.executaveis_de(cat):
            EXECUTADO.setdefault(e, set()).add("publicar_no_deploy.mjs")

DECLARADO = {}
for cat in CAD.CATEGORIAS:
    for e in CAD.executaveis_de(cat):
        DECLARADO.setdefault(e, set()).add(cat)

print("=" * 74)
print("UM DONO SO PARA A CADEIA — universo medido na maquina")
print("=" * 74)
print("  executado  : %d ficheiros (%d workflows + %d npm)"
      % (len(EXECUTADO), len(WF), len(BUILD)))
print("  declarado  : %d ficheiros em %d categorias"
      % (len(DECLARADO), len(CAD.CATEGORIAS)))

prova("ha_execucoes_para_medir", bool(EXECUTADO),
      "sem universo medido, tudo o que vem a seguir passa por vazio")
prova("ha_declaracoes_para_comparar", bool(DECLARADO))

# ── 2 · GOVERNANCA NOS DOIS SENTIDOS ──────────────────────────────────────
nao_declaradas = sorted(set(EXECUTADO) - set(DECLARADO))
prova("nenhuma_execucao_do_mapa_fica_por_declarar", not nao_declaradas,
      "%d: %s" % (len(nao_declaradas), nao_declaradas[:6]))

nao_executados = sorted(set(DECLARADO) - set(EXECUTADO))
# Um passo declarado que ninguem corre nao e automaticamente um defeito — mas
# tem de o DIZER. Os tres regeneradores a mao dizem-no, e dizem porque.
a_mao = {p["EXECUTABLE"] for p in CAD.passos_a_mao()}
mudos = [e for e in nao_executados if e not in a_mao]
prova("nenhum_passo_declarado_esta_morto_sem_razao", not mudos,
      "%d declarados que ninguem corre e nao explicam porque: %s" % (len(mudos), mudos[:6]))
prova("os_passos_a_mao_dizem_que_sao_a_mao",
      all(p.get("EXECUTADO_POR") == "MAO" for p in CAD.passos_a_mao())
      and bool(CAD.CADEIA.get("PORQUE_REGERAR_A_MAO")),
      "sem EXECUTADO_POR e sem razao, «a mao» seria so uma gaveta para esconder")
prova("e_ha_mesmo_regeneradores_que_ninguem_corre", bool(a_mao & set(nao_executados)),
      "se deixassem de existir, esta prova passava a nao medir nada — e a divida "
      "desaparecia sem ninguem a fechar")

faltam = [e for e in DECLARADO if not (RAIZ / e).exists()]
prova("todo_executavel_declarado_existe", not faltam, faltam)

# ── 3 · O CORREDOR E QUEM CORRE A CADEIA ──────────────────────────────────
wf = texto(".github/workflows/system-map.yml")
prova("o_workflow_corre_a_cadeia_pelo_corredor", CORREDOR in wf,
      "sem o corredor, a lista volta para o YAML")
PODEM_SER_NOMEADOS = set(CAD.executaveis_de("OUTRAS_EXECUCOES")) | {CORREDOR}
listados = sorted({m.group(1) for m in ALVO.finditer(wf)} - PODEM_SER_NOMEADOS)
prova("o_workflow_nao_lista_passos_da_cadeia", not listados,
      "%s — REGERAR/VALIDAR/PORTOES sao corridos pelo corredor, nunca nomeados" % listados)

# E O BUILD OBEDECE A MESMA LEI. Ele estava de fora desta pergunta, e um
# `npm run build` que corresse tres scripts a mao passava por aqui sem tocar em
# nada — «cadeia reduzida silenciosa» e exactamente o nome disso.
no_build = sorted(set(BUILD) - PODEM_SER_NOMEADOS)
prova("o_build_nao_lista_passos_da_cadeia", not no_build,
      "%s — a Vercel corre a mesma cadeia, pelo mesmo manifesto" % no_build)

# ── 4 · NENHUMA SEGUNDA LISTA, EM LINGUA NENHUMA ──────────────────────────
# Nao basta o workflow deixar de listar: uma funcao com a mesma lista dentro
# seria o mesmo defeito com outra sintaxe.
#
#     UM HELPER PODE LER O MANIFESTO. NAO PODE SABER A LISTA DE COR.
# A BUSCA E POR FICHEIRO, NAO POR EXTENSAO ESCOLHIDA A DEDO. Um `for s in a b c`
# dentro de um `.sh` e uma cadeia tao segunda como um array em JS, e a primeira
# versao desta lista nao olhava para `.sh` nenhum.
SUSPEITOS = [f for f in RAIZ.rglob("*")
             if f.is_file() and "__pycache__" not in str(f)
             and f.suffix in (".py", ".mjs", ".js", ".sh", ".yml", ".yaml", ".json")
             and (str(f.relative_to(RAIZ)).startswith(("system-map/", ".github/"))
                  or f.name == "package.json")
             and f.name != "CADEIA-DO-MAPA.json"
             # `architecture.declared.json` diz QUE FICHEIROS PERTENCEM A QUE
             # CARTAO. Nomeia varios scripts da cadeia, e isso nao e uma cadeia:
             # e posse de ficheiro por peca, outro conceito e outro dono. A
             # excepcao e por NOME e esta escrita — uma excepcao sem razao seria
             # a porta das traseiras que esta prova existe para fechar.
             and f.name != "architecture.declared.json"
             and not f.name.endswith(".generated.json")]
TODOS = set(DECLARADO)
segundas = []
for f in SUSPEITOS:
    rel = f.relative_to(RAIZ).as_posix()
    if rel == "system-map/tests/test_uma_cadeia_um_dono.py":
        continue          # este ficheiro FALA da lista; nao a guarda
    t = f.read_text(encoding="utf-8", errors="replace")
    # ⚠️ CONTAR MENCOES APANHA QUEM CITA, NAO QUEM GUARDA A LISTA. A primeira
    # versao acusou `reconciliacao_do_universo.py`, que nomeia scripts como
    # OWNER de cada numero, e um teste que mapeia artefato -> produtor. Nenhum
    # deles tem uma cadeia dentro.
    #
    #     UMA LISTA E UM LITERAL DE SEQUENCIA. UMA MENCAO E UMA FRASE.
    #
    # Em Python pergunta-se a arvore sintatica; em YAML/JS, a um array escrito.
    da_cadeia = set(CAD.executaveis_de("REGERAR"))
    if f.suffix == ".py":
        try:
            arv = ast.parse(t)
        except SyntaxError:
            continue
        def elementos(no):
            """Os ELEMENTOS da sequencia — e de uma sequencia aninhada.

            Nao desce a valores de dicionario: `{"OWNER": "scan_repo.py"}` e uma
            ATRIBUICAO, nao um passo numa lista. Descer la dentro acusava um
            ficheiro que atribui dono a cada numero que publica, e nao guarda
            cadeia nenhuma.
            """
            for e in getattr(no, "elts", []):
                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                    yield e.value
                elif isinstance(e, (ast.List, ast.Tuple, ast.Set)):
                    yield from elementos(e)

        for n in ast.walk(arv):
            if not isinstance(n, (ast.List, ast.Tuple, ast.Set)):
                continue
            dentro = set(elementos(n))
            if len(dentro & da_cadeia) >= 3:
                segundas.append((rel, sorted(dentro & da_cadeia)[:3]))
                break
    elif f.suffix in (".sh",):
        # num shell a «lista» e uma sequencia de palavras num `for ... in`
        for linha in t.splitlines():
            if len({e for e in da_cadeia if e in linha}) >= 3:
                segundas.append((rel, "sequencia em shell"))
                break
    else:
        for bloco in re.findall(r"[\[(][^\[\]()]{0,4000}[\])]", t, re.S):
            if len({e for e in da_cadeia if e in bloco}) >= 3:
                segundas.append((rel, "array literal"))
                break
# (14) UM SEGUNDO MANIFESTO RECONHECE-SE PELA FORMA, NAO PELO NOME. Guardar uma
# lista de nomes proibidos so apanha quem escolher um nome da lista.
rivais = []
for f in sorted((RAIZ / "system-map" / "scripts").rglob("*.json")):
    if f.name == "CADEIA-DO-MAPA.json":
        continue
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        continue
    if isinstance(d, dict) and set(d) & {"REGERAR", "VALIDAR", "STEPS", "CHAIN", "PIPELINE"}:
        rivais.append(f.relative_to(RAIZ).as_posix())
prova("nao_nasceu_um_segundo_manifesto_da_cadeia", not rivais, rivais)

prova("nenhum_ficheiro_guarda_a_lista_da_cadeia_de_cor", not segundas,
      "%s — tres ou mais passos nomeados no mesmo sitio e uma segunda cadeia" % segundas)

# ── 5 · OS EXTERNOS CONTINUAM EXTERNOS ────────────────────────────────────
ext = {x["PATH"]: x for x in CAD.produtores_externos()}
prova("os_produtores_externos_estao_declarados", bool(ext), "nenhum declarado")
sequestrados = [p for p in ext
                if CAD.quem_produz(p) is not None]
prova("nenhum_produtor_externo_foi_sequestrado_para_a_cadeia", not sequestrados,
      "%s — o mapa CONSOME; traze-lo para ca criaria um dono falso" % sequestrados)
sem_dono = [p for p, x in ext.items() if not x.get("DONO") or not x.get("PORQUE")]
prova("todo_externo_diz_de_quem_e_e_porque", not sem_dono, sem_dono)
usados = {e["PATH"] for p in CAD.todos_os_passos() for e in p["INPUTS"]
          if e.get("PRODUCER") == "EXTERNAL_PRODUCER"}
prova("todo_EXTERNAL_PRODUCER_usado_esta_na_lista_dos_externos",
      not (usados - set(ext)), sorted(usados - set(ext)))

# ── 6 · CADA CATEGORIA TEM CONTRATO, E ELES NAO SE CONFUNDEM ──────────────
portoes = CAD.portoes_pos_commit()
prova("o_portao_pos_commit_esta_governado", bool(portoes))
for g in portoes:
    prova("o_portao_[%s]_nao_finge_ser_passo_de_regeracao" % g["STEP_ID"],
          g["EXECUTABLE"] not in CAD.executaveis_de("REGERAR")
          and g["EXECUTABLE"] not in CAD.executaveis_de("VALIDAR")
          and not g.get("OUTPUTS") and bool(g.get("NAO_MATERIALIZA")),
          "um portao que se declara passo mente sobre o contrato dele")
    prova("o_portao_[%s]_diz_quando_corre" % g["STEP_ID"],
          g.get("QUANDO") == "DEPOIS_DO_COMMIT" and bool(g.get("ARGUMENTOS")),
          "o argumento vive no manifesto; no YAML seria a segunda lista a voltar "
          "pela porta dos parametros")

provas_decl = CAD.outras_execucoes("PROVA")
prova("as_provas_estao_governadas", bool(provas_decl))
prova("nenhuma_prova_se_declara_produtora",
      all(not x.get("OUTPUTS") and x.get("NAO_MATERIALIZA") for x in provas_decl),
      "uma prova produz veredito, nao mapa")

ids = [x["STEP_ID"] for x in CAD.todas_as_execucoes()]
prova("STEP_ID_e_unico_em_todo_o_manifesto", len(ids) == len(set(ids)),
      [i for i in ids if ids.count(i) > 1])
exes = [x["EXECUTABLE"] for x in CAD.todas_as_execucoes()]
prova("nenhum_executavel_aparece_em_duas_categorias",
      len(exes) == len(set(exes)), [e for e in exes if exes.count(e) > 1])

# ── 7 · O G6 NAO FOI COMECADO ─────────────────────────────────────────────
regerar = CAD.passos()
i_pente = next(i for i, p in enumerate(regerar) if p["STEP_ID"] == "PENTE_FINO_DA_COLETA")
i_ger = next(i for i, p in enumerate(regerar) if p["STEP_ID"] == "GENERATE_SYSTEM_MAP")
prova("o_ciclo_do_pente_fino_continua_por_fechar", i_pente < i_ger,
      "o passo %d continua a ler o que o passo %d escreve — e isso e o G6"
      % (i_pente + 1, i_ger + 1))

# E a divida do ciclo cresceu com o G5, porque agora ve-se inteira.
pos = {p["STEP_ID"]: i for i, p in enumerate(regerar)}
atrasados = []
for p in regerar:
    for e in p["INPUTS"]:
        alvo = None
        if e["KIND"] == "GENERATED_ARTIFACT" and e.get("PRODUCER") in pos:
            alvo = [e["PRODUCER"]]
        elif e.get("INCLUI_GERADOS"):
            alvo = [x for x in e["INCLUI_GERADOS"] if x in pos]
        for a in alvo or []:
            if pos[a] > pos[p["STEP_ID"]]:
                atrasados.append((p["STEP_ID"], a))
prova("a_divida_do_ciclo_esta_a_vista_e_medida", bool(atrasados),
      "%d dependencias atrasadas, em %d passos — declaradas, nao escondidas"
      % (len(atrasados), len({a for a, _ in atrasados})))

corredor = texto(CORREDOR)

# (19) O CORREDOR NAO PODE NOMEAR EXECUTAVEL NENHUM — declarado ou nao.
# Ele e o veiculo: tudo o que corre vem do manifesto. Um
# `subprocess.run([... "mudar_gaveta.py"])` la dentro seria uma execucao que
# nenhum consumidor ve e nenhum manifesto governa — a segunda cadeia mais barata
# de todas, porque cabe numa linha.
#
# A primeira versao so procurava executaveis DECLARADOS, e por isso nao via
# justamente o caso perigoso: esconder ali um script que ninguem declarou.
#
#     PROCURAR SO O QUE JA ESTA DECLARADO E NAO PROCURAR O QUE SE ESCONDE.
escondidos = sorted(set(re.findall(r"system-map/(?:scripts|tests)/[\w./-]+\.(?:py|mjs|js)",
                                   corredor)) - {CORREDOR})   # ele nomeia-se no `uso:`
prova("o_corredor_nao_nomeia_executavel_nenhum", not escondidos,
      "%s — quem corre a cadeia le-a; nomear e saber de cor" % escondidos)

# ── 8 · OS CONSUMIDORES PASSAM PELO LEITOR ────────────────────────────────
# Estas tres guardas nasceram no G4 e eu apaguei-as sem querer ao reescrever uma
# seccao inteira do ficheiro dele. Vivem aqui agora, que e onde pertencem: o G5
# e a missao de «um dono», e um consumidor que reconstroi a lista e o defeito
# que ela existe para apanhar.
#
#     UMA GUARDA APAGADA NUMA REESCRITA NAO DEIXA BURACO A VISTA:
#     DEIXA UM TESTE VERDE COM MENOS PERGUNTAS.
js = texto("system-map/scripts/publicar_no_deploy.mjs")
prova("o_leitor_javascript_cobre_REGERAR_e_VALIDAR",
      "function executaveisDaCadeia()" in js and "function executaveisDeValidar()" in js,
      "as duas listas tem a mesma forma; migrar so uma deixa a outra a entregar "
      "o OBJECTO do passo ao python")
# ⚠️ CONTAR ACESSOS AO MANIFESTO ERA A PERGUNTA ERRADA. Derivar a exclusao
# precisa de ler `CADEIA.REGERAR` para lhe tirar os OUTPUTS — e isso nao e
# reconstruir a cadeia, e usa-la. A primeira versao contava ocorrencias e
# reprovou a derivacao que este mesmo G5 introduziu.
#
#     O QUE NAO PODE SER COPIADO E A LISTA DE QUEM CORRE.
#     LER O QUE CADA PASSO PRODUZ E OUTRA PERGUNTA.
#
# Quem distribui EXECUTAVEIS sao as duas funcoes de leitura, e mais ninguem.
entrega = [m for m in re.finditer(r"\.EXECUTABLE", js)]
corpos = "".join(re.findall(
    r"function executaveis(?:DaCadeia|DeValidar)\(\)\s*\{[^}]*\}", js))
prova("so_as_funcoes_de_leitura_entregam_EXECUTABLE",
      len(entrega) == corpos.count(".EXECUTABLE"),
      "%d usos de .EXECUTABLE no ficheiro, %d dentro dos leitores"
      % (len(entrega), corpos.count(".EXECUTABLE")))
usos = re.findall(r"(?:for\s*\(\s*const\s+\w+\s+of\s+|)(CADEIA\.(?:REGERAR|VALIDAR))\s*(\.\w+|\))", js)
fora_do_leitor = [u for u in usos if u[1] not in (".map",)]
prova("o_publicador_nao_percorre_a_lista_crua", not fora_do_leitor,
      "%s — iterar ou mapear a lista fora do leitor e reconstrui-la" % fora_do_leitor)

# (22) O LEITOR TEM DE CONHECER TODAS AS CATEGORIAS QUE O MANIFESTO TEM.
# Tirar uma de `CATEGORIAS` nao apaga os passos: apaga-os DESTA PROVA, e o
# workflow continua a corre-los sem ninguem os comparar com nada.
#
#     UMA CATEGORIA QUE O LEITOR NAO CONHECE E UMA CADEIA SEM TESTEMUNHA.
NAO_SAO_CATEGORIA = {"SCHEMA", "NOTA", "PUBLICADO", "ARTEFATO_DE_DEPLOY",
                     "IMPRESSAO_DA_ARVORE", "PORTAO_DO_MAPA", "PORTAO_DAS_REGRAS",
                     "PORTAO_DA_COLETA", "PRODUTORES_EXTERNOS",
                     "PORQUE_REGERAR_A_MAO"}
no_manifesto = {k for k, v in CAD.CADEIA.items()
                if isinstance(v, list) and v and isinstance(v[0], dict)
                and "EXECUTABLE" in v[0]} - NAO_SAO_CATEGORIA
esquecidas = sorted(no_manifesto - set(CAD.CATEGORIAS))
prova("o_leitor_conhece_todas_as_categorias_do_manifesto", not esquecidas,
      "%s — categoria com executaveis que o leitor nao lista" % esquecidas)

# (25) E ESTA PROVA NAO PODE ESTAR PRESA A UM NUMERO. Se alguem escrever
# `len(DECLARADO) == 36`, ela passa a medir a data em que foi escrita.
#
#     UMA PROVA QUE COMPARA UM TOTAL COM UM LITERAL DEIXA DE DESCOBRIR O UNIVERSO:
#     PASSA A CONFIRMAR UMA LEMBRANCA.
_eu = ast.parse(texto("system-map/tests/test_uma_cadeia_um_dono.py"))
_presos = []
for n in ast.walk(_eu):
    if not isinstance(n, ast.Compare):
        continue
    esq = n.left
    if (isinstance(esq, ast.Call) and isinstance(esq.func, ast.Name)
            and esq.func.id == "len"
            and isinstance(esq.args[0], ast.Name)
            and esq.args[0].id in ("DECLARADO", "EXECUTADO", "TODOS")):
        for cmp_ in n.comparators:
            if isinstance(cmp_, ast.Constant) and isinstance(cmp_.value, int):
                _presos.append("linha %d" % n.lineno)
prova("esta_prova_nao_esta_presa_a_um_numero_de_passos", not _presos, _presos)

prova("o_corredor_nao_deriva_ordem",
      "topolog" not in corredor.lower() and ".sort(" not in corredor,
      "derivar ordem aqui seria o G6 implementado a socapa num corredor")

print()
print("=" * 74)
if FALHAS:
    print("UMA_CADEIA_UM_DONO=FAIL · %d prova(s) reprovada(s)" % len(FALHAS))
    for f in FALHAS:
        print("  ·", f)
    raise SystemExit(1)
print("UMA_CADEIA_UM_DONO=PASS · o manifesto governa %d execucoes, e nao ha segunda lista"
      % len(DECLARADO))
