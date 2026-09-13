#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DO CONTRATO DE ENTRADA E SAIDA POR PASSO — G4.

    python3 system-map/tests/test_cadeia_declara_io.py

O manifesto passou a dizer, por passo, o que ele LE e o que ele ESCREVE. Uma
declaracao que ninguem confere e uma opiniao com sintaxe de JSON.

    DECLARED DEPENDENCY != OBSERVED DEPENDENCY.
    E UMA DECLARACAO QUE NAO SE CONSEGUE DESMENTIR NAO E UM CONTRATO.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    FORMA        todo passo tem STEP_ID unico, EXECUTABLE que existe,
                 INPUTS e OUTPUTS, e nenhum caminho vazio
    VOCABULARIO  todo KIND e um dos quatro, e cada um traz o que lhe compete
    PRODUTOR     entrada gerada aponta para quem a produz — e quando o produtor
                 nao esta neste manifesto, diz FORA_DO_MANIFESTO em vez de mentir
    CODIGO       a declaracao e conferida contra o CODIGO REAL, de duas formas
                 independentes: a AST (o que o codigo NOMEIA) e uma corrida
                 instrumentada num clone (o que o codigo ABRIU)
    NEGATIVOS    cada regra corrida contra um defeito fabricado
    FRONTEIRA    o G5 e o G6 continuam por fazer, e a prova reprova se alguem
                 os comecar aqui por acidente

O QUE ESTE FICHEIRO NAO CONFERE, E PORQUE
-----------------------------------------
O espiao ve o processo dele, nao os subprocessos. `validate_system_map.py`
corre quatro geradores como subprocesso; as escritas DELES nao aparecem aqui, e
e por isso que o manifesto declara `NAO_MATERIALIZA` em vez de OUTPUTS vazios
sem explicacao. Isto e LIMITATION declarada, nao cobertura fingida.
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
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import cadeia_do_mapa as CAD                              # noqa: E402

FALHAS = []


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome + ("" if ok else "  " + str(porque)[:300]))
    if not ok:
        FALHAS.append(nome)


PASSOS = CAD.todos_os_passos()
REGERAR = CAD.passos()


def texto(rel) -> str:
    """O conteudo, ou vazio se o ficheiro nao existe.

    UM PORTAO QUE REBENTA COM TRACEBACK NAO E MELHOR DO QUE UM QUE MENTE:
    OS DOIS OBRIGAM QUEM LE A ADIVINHAR.

    O executavel em falta ja tem guarda com nome (`o_executavel_existe_no_disco`).
    As seccoes seguintes nao devem rebentar por cima dela — se rebentassem, o
    veredito passava a ser uma pilha de chamadas e o nome do defeito perdia-se.
    """
    f = RAIZ / rel
    return f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""

print("=" * 70)
print("O CONTRATO DE IO DA CADEIA — %d passos" % len(PASSOS))
print("=" * 70)

# ── 1 · FORMA ──────────────────────────────────────────────────────────────
prova("o_manifesto_declara_o_schema_novo",
      CAD.CADEIA["SCHEMA"] == "sintonia.system-map.cadeia/2",
      CAD.CADEIA["SCHEMA"])
ids = [p.get("STEP_ID") for p in PASSOS]
prova("todo_passo_tem_STEP_ID", all(ids), ids)
prova("STEP_ID_nao_repete", len(ids) == len(set(ids)),
      [i for i in ids if ids.count(i) > 1])
prova("todo_passo_tem_EXECUTABLE", all(p.get("EXECUTABLE") for p in PASSOS))
faltam = [p["EXECUTABLE"] for p in PASSOS if not (RAIZ / p["EXECUTABLE"]).exists()]
prova("o_executavel_existe_no_disco", not faltam, faltam)
prova("todo_passo_tem_INPUTS", all("INPUTS" in p for p in PASSOS))
prova("todo_passo_tem_OUTPUTS", all("OUTPUTS" in p for p in PASSOS))
prova("nenhum_passo_tem_INPUTS_vazio",
      all(p["INPUTS"] for p in PASSOS),
      [p["STEP_ID"] for p in PASSOS if not p["INPUTS"]])

# Um OUTPUT vazio e legitimo — mas so com a razao escrita. Um passo que nao
# materializa nada e diferente de um passo a quem se esqueceram os outputs.
sem_saida_sem_razao = [p["STEP_ID"] for p in PASSOS
                       if not p["OUTPUTS"] and not p.get("NAO_MATERIALIZA")]
prova("passo_sem_OUTPUTS_explica_porque", not sem_saida_sem_razao, sem_saida_sem_razao)

vazios = [(p["STEP_ID"], e) for p in PASSOS for e in p["INPUTS"] + p["OUTPUTS"]
          if "PATH" in e and not str(e["PATH"]).strip()]
prova("nenhum_caminho_declarado_e_vazio", not vazios, vazios[:3])

# ── 2 · VOCABULARIO ────────────────────────────────────────────────────────
maus = [(p["STEP_ID"], e.get("KIND")) for p in PASSOS
        for e in p["INPUTS"] + p["OUTPUTS"] if e.get("KIND") not in CAD.KINDS]
prova("todo_KIND_esta_no_vocabulario", not maus, maus[:4])
prova("o_vocabulario_distingue_fonte_de_gerado",
      CAD.TRACKED_SOURCE_TREE in CAD.KINDS and CAD.GENERATED_ARTIFACT in CAD.KINDS)
sem_path = [(p["STEP_ID"], e) for p in PASSOS for e in p["INPUTS"] + p["OUTPUTS"]
            if e["KIND"] != CAD.TRACKED_SOURCE_TREE and not e.get("PATH")]
prova("toda_entrada_nomeada_traz_PATH", not sem_path, sem_path[:3])
sem_regra = [(p["STEP_ID"], e.get("ORIGEM")) for p in PASSOS
             for e in CAD.entradas(p, CAD.TRACKED_SOURCE_TREE)
             if not (e.get("ORIGEM") and e.get("PADRAO") and e.get("FILTRO_DONO"))]
prova("toda_arvore_declara_origem_padrao_e_dono_do_filtro", not sem_regra, sem_regra[:3])
prova("toda_entrada_e_saida_diz_PORQUE",
      all(e.get("PORQUE") for p in PASSOS for e in p["INPUTS"] + p["OUTPUTS"]
          if e["KIND"] != CAD.CANONICAL_MANIFEST or e.get("PORQUE")))

# ── 3 · O DONO DO FILTRO EXISTE MESMO NO CODIGO ────────────────────────────
# `FILTRO_DONO` nomeia ficheiro e simbolo. Se o simbolo nao existe la, a
# declaracao aponta para o vazio — e uma regra sem dono e uma regra sem nada.
ruins = []
for p in PASSOS:
    for e in CAD.entradas(p, CAD.TRACKED_SOURCE_TREE):
        ficheiro = e["FILTRO_DONO"].split("·")[0].strip()
        simbolos = [s.strip() for s in e["FILTRO_DONO"].split("·")[1].split(",")]
        txt = texto(ficheiro)
        for s in simbolos:
            alvo = s.split("(")[0].strip().strip('"')
            if alvo and alvo not in txt:
                ruins.append((p["STEP_ID"], ficheiro, alvo))
prova("o_dono_do_filtro_existe_no_ficheiro_que_ele_nomeia", not ruins, ruins[:4])

# ── 4 · PRODUTOR ───────────────────────────────────────────────────────────
sem_prod = [(p["STEP_ID"], e["PATH"]) for p in PASSOS
            for e in CAD.entradas(p, CAD.GENERATED_ARTIFACT) if not e.get("PRODUCER")]
prova("toda_entrada_gerada_nomeia_o_produtor", not sem_prod, sem_prod[:3])

mentiras = []
for p in PASSOS:
    for e in CAD.entradas(p, CAD.GENERATED_ARTIFACT):
        real = CAD.quem_produz(e["PATH"])
        if e["PRODUCER"] == CAD.FORA_DO_MANIFESTO:
            if real is not None:
                mentiras.append((p["STEP_ID"], e["PATH"], "diz FORA mas %s produz" % real))
        elif real != e["PRODUCER"]:
            mentiras.append((p["STEP_ID"], e["PATH"], "diz %s, produz %s" % (e["PRODUCER"], real)))
prova("o_produtor_declarado_e_quem_produz_mesmo", not mentiras, mentiras[:4])

prod_ausente = [(p["STEP_ID"], e["PATH"]) for p in PASSOS
                for e in CAD.entradas(p, CAD.GENERATED_ARTIFACT)
                if not (RAIZ / e["PRODUCER_EXECUTABLE"]).exists()]
prova("o_executavel_do_produtor_existe", not prod_ausente, prod_ausente[:3])

# ⚠️ O KIND NAO E DECORACAO: E A DIFERENCA QUE O CONTRATO EXISTE PARA GUARDAR.
#
# Um ataque do red team trocou `GENERATED_ARTIFACT` por `TRACKED_SOURCE_FILE`
# numa entrada real — e passou em tudo. O caminho existia, era mesmo lido, a AST
# confirmava-o: so a PALAVRA mudava. E com ela desaparecia a unica coisa que o
# G6 vai precisar de ler: que aquele ficheiro nasce de OUTRO PASSO.
#
#     CHAMAR FONTE A UM ARTEFATO GERADO NAO APAGA A DEPENDENCIA:
#     APAGA A CAPACIDADE DE A VER.
#
# Duas regras fecham-no, e nenhuma delas precisa de uma lista escrita a mao:
# o que e SAIDA de alguem e GERADO em todo o lado; e o KIND de um caminho nao
# pode mudar conforme o passo que o le.
SAIDAS = {s["PATH"] for p in PASSOS for s in CAD.saidas(p)}
disfarcados = [(p["STEP_ID"], e["PATH"], e["KIND"]) for p in PASSOS for e in p["INPUTS"]
               if e.get("PATH") in SAIDAS and e["KIND"] != CAD.GENERATED_ARTIFACT]
prova("o_que_e_saida_de_um_passo_e_GERADO_em_todo_o_lado", not disfarcados,
      disfarcados[:4])

kinds = {}
for p in PASSOS:
    for e in p["INPUTS"] + p["OUTPUTS"]:
        if e.get("PATH"):
            kinds.setdefault(e["PATH"], set()).add(e["KIND"])
bifronte = {k: sorted(v) for k, v in kinds.items() if len(v) > 1}
prova("o_mesmo_caminho_tem_sempre_o_mesmo_KIND", not bifronte, bifronte)

# Dois passos nao podem reclamar a mesma saida sem explicacao.
donos = {}
for p in PASSOS:
    for s in CAD.saidas(p):
        donos.setdefault(s["PATH"], []).append(p["STEP_ID"])
disputados = {k: v for k, v in donos.items() if len(v) > 1}
prova("nenhuma_saida_tem_dois_donos", not disputados, disputados)

# ── 5 · A DIVIDA DO G5, PRESERVADA E NAO ABSORVIDA ────────────────────────
# Os treze scripts que o workflow corre e o manifesto nao declara continuam
# fora. G4 mede-os; trazê-los para dentro e o G5.
CI = texto(".github/workflows/system-map.yml")
import re
no_ci = re.findall(r"python3 (system-map/scripts/[a-z_]+\.py)", CI)
declarados = set(CAD.executaveis()) | set(CAD.executaveis_de_validar())
fora = sorted(set(no_ci) - declarados)
DIV = CAD.CADEIA["FORA_DESTE_MANIFESTO"]
declarada_fora = sorted(DIV["ONZE_CENSOS"] + DIV["CENSO_DA_TOPOLOGIA"]
                        + DIV["PORTAO_POS_COMMIT"])
prova("a_divida_do_G5_esta_declarada_no_manifesto_e_nao_num_numero_aqui",
      fora == declarada_fora,
      "workflow-menos-manifesto=%s · declarado=%s"
      % (sorted(set(fora) - set(declarada_fora)), sorted(set(declarada_fora) - set(fora))))
prova("a_divida_declarada_diz_porque_fica_fora", bool(DIV.get("PORQUE_FICAM_FORA")))
prova("o_manifesto_nao_engoliu_os_treze", len(CAD.passos()) == 7,
      "%d passos em REGERAR — se subiu, o G5 entrou por acidente" % len(CAD.passos()))
prova("ha_entradas_geradas_com_produtor_fora_do_manifesto",
      any(e.get("PRODUCER") == CAD.FORA_DO_MANIFESTO
          for p in PASSOS for e in CAD.entradas(p, CAD.GENERATED_ARTIFACT)),
      "o gerador le artefatos dos treze; esconder isso seria fingir que a "
      "divida do G5 nao existe")

# ── 5b · UM SO DONO, E UM SO LEITOR POR RUNTIME ───────────────────────────
# Um segundo ficheiro a declarar dependencias seria uma segunda verdade, e duas
# verdades divergem no dia em que alguem so mexe numa.
CONCORRENTES = ["CADEIA-V2.json", "DEPENDENCIAS.json", "pipeline.json",
                "graph.json", "manifest-final.json", "CADEIA-IO.json",
                "pipeline-dependencies.json", "map-build-graph-v2.json"]
achados = [n for n in CONCORRENTES
           if list(RAIZ.rglob(n)) and not any("node_modules" in str(x)
                                              for x in RAIZ.rglob(n))]
prova("nao_nasceu_um_segundo_dono_da_cadeia", not achados, achados)

# E quem CONSOME a cadeia tem de passar pelo leitor. Um consumidor que volte a
# abrir a lista com as proprias maos e um segundo interprete do formato.
LEITORES = {"system-map/scripts/cadeia_do_mapa.py",
            "system-map/scripts/publicar_no_deploy.mjs"}
# ⚠️ PROCURAR O TEXTO NAO CHEGA, E ISTO FOI MEDIDO DUAS VEZES. A primeira
# versao procurava a string e apanhou-se a si propria; a segunda montou a
# agulha e apanhou `test_system_map.py`, que a tem DENTRO DE ASPAS para
# conferir o publicador. Nenhum dos dois le a lista: os dois FALAM dela.
#
#     UM TESTE QUE PROCURA TEXTO NAO DISTINGUE QUEM USA DE QUEM CITA.
#
# Quem USA subscreve o dicionario. Isso ve-se na arvore sintatica, e so la.
cruus = []
for f in sorted(RAIZ.glob("system-map/**/*.py")):
    rel = f.relative_to(RAIZ).as_posix()
    if rel in LEITORES or "__pycache__" in rel:
        continue
    try:
        arv = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    for n in ast.walk(arv):
        if (isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
                and n.value.id == "CADEIA" and isinstance(n.slice, ast.Constant)
                and n.slice.value in ("REGERAR", "VALIDAR")):
            cruus.append("%s:%d" % (rel, n.lineno))
for f in sorted(RAIZ.glob("system-map/**/*.mjs")):
    rel = f.relative_to(RAIZ).as_posix()
    if rel in LEITORES:
        continue
    if "CADEIA" + ".REGERAR" in f.read_text(encoding="utf-8", errors="replace"):
        cruus.append(rel)
prova("nenhum_consumidor_le_a_lista_crua", not cruus, cruus)

# E os dois leitores — um por runtime — tem de devolver a MESMA lista.
js = texto("system-map/scripts/publicar_no_deploy.mjs")
prova("o_leitor_javascript_existe_e_le_o_EXECUTABLE",
      "function executaveisDaCadeia()" in js and "p.EXECUTABLE" in js,
      "o publicador tem de ler a forma nova")
prova("o_leitor_javascript_cobre_REGERAR_e_VALIDAR",
      "function executaveisDeValidar()" in js,
      "as duas listas tem a mesma forma; migrar so uma deixa a outra a passar "
      "o OBJECTO do passo ao python")

# ⚠️ O PUBLICADOR E O LEITOR, LOGO ESTA ISENTO DA GUARDA DA LISTA CRUA — E FOI
# NESSE BURACO QUE O DEFEITO ENTROU. Ele iterava `CADEIA.VALIDAR` directamente e
# entregava o objecto do passo ao python:
#
#     python3: can't open file '.../[object Object]'
#
# E nao caiu: o publicador apanha a falha do validador de proposito, para nao
# derrubar o portal. O `rc` ficou 0 e o veredito foi parar ao FIM da linha.
#
#     QUEM E ISENTO DE UMA GUARDA PRECISA DE OUTRA, E NAO DE NENHUMA.
#
# Dentro do leitor, o acesso cru so pode viver nas funcoes de leitura — nunca
# num laco que corre processos.
import re as _re
lacos = _re.findall(r"for\s*\(\s*const\s+\w+\s+of\s+(CADEIA\.\w+)\s*\)", js)
prova("o_publicador_nao_itera_a_lista_crua", not lacos,
      "%s — tem de passar pelo leitor, senao entrega o objecto ao python" % lacos)
prova("o_acesso_cru_vive_so_nas_funcoes_de_leitura",
      js.count("CADEIA.REGERAR") == 1 and js.count("CADEIA.VALIDAR") == 1,
      "REGERAR=%d VALIDAR=%d — uma ocorrencia cada, dentro do seu leitor"
      % (js.count("CADEIA.REGERAR"), js.count("CADEIA.VALIDAR")))

# ── 6 · A ORDEM NAO FOI MEXIDA (G6 CONTINUA POR FAZER) ────────────────────
ORDEM_G3 = ["system-map/scripts/scan_repo.py", "system-map/scripts/scan_sources.py",
            "system-map/scripts/scan_casco.py", "system-map/scripts/censo_da_coleta.py",
            "system-map/scripts/pente_fino_da_coleta.py",
            "system-map/scripts/censo_dos_buracos.py",
            "system-map/scripts/generate_system_map.py"]
prova("a_ordem_da_cadeia_e_a_mesma_que_antes_do_G4",
      CAD.executaveis() == ORDEM_G3,
      "G4 declara dependencia; ordenar por ela e o G6")
leitor = texto("system-map/scripts/cadeia_do_mapa.py")
prova("o_leitor_nao_ordena_nada",
      "sort" not in leitor and "topolog" not in leitor.lower(),
      "um sort dentro do leitor seria o G6 implementado a socapa")

# ── 7 · O CICLO DO PENTE FINO, DECLARADO ──────────────────────────────────
pente = CAD.por_id("PENTE_FINO_DA_COLETA")
ciclo = [e for e in CAD.entradas(pente, CAD.GENERATED_ARTIFACT)
         if e["PRODUCER"] == "GENERATE_SYSTEM_MAP"]
prova("o_pente_fino_declara_que_le_a_saida_do_gerador", bool(ciclo),
      "ele le state.generated.json, que nasce no passo 7 — esconder isso seria "
      "apagar a divida do G6 do sitio onde ela e visivel")
if ciclo:
    i_pente = CAD.executaveis().index(pente["EXECUTABLE"])
    i_ger = CAD.executaveis().index("system-map/scripts/generate_system_map.py")
    prova("e_o_ciclo_esta_mesmo_atrasado_na_ordem_actual", i_pente < i_ger,
          "o passo %d le o que o passo %d escreve" % (i_pente + 1, i_ger + 1))

# ── 8 · A DECLARACAO CONTRA O CODIGO — TESTEMUNHA 1: A AST ────────────────
# O que o codigo NOMEIA, lido da arvore sintatica. Nao depende do disco.


def nomeados(ficheiro) -> set:
    try:
        arv = ast.parse(texto(ficheiro))
    except SyntaxError:
        return set()
    return {n.value.strip() for n in ast.walk(arv)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and n.value.strip() and len(n.value) < 200}


def nomeia(ficheiro, alvo: str) -> bool:
    txt = nomeados(ficheiro)
    if alvo in txt:
        return True
    segs = [s for s in alvo.split("/") if s]
    return all(s in txt for s in segs) or segs[-1] in txt


mudos, sem_via = [], []
for p in PASSOS:
    for e in p["INPUTS"] + p["OUTPUTS"]:
        if e["KIND"] == CAD.TRACKED_SOURCE_TREE:
            continue
        # UMA LEITURA INDIRECTA CONTINUA A SER UMA LEITURA. Quando o passo nao
        # abre o ficheiro com as proprias maos — abre-o o modulo que ele importa
        # — a declaracao tem de dizer POR ONDE, e a testemunha vai la conferir.
        # Sem `VIA`, o caminho tinha de estar no proprio executavel; aceitar a
        # ausencia seria deixar passar «o codigo nunca fala disto».
        # UMA SAIDA CUJO NOME VEM DO MANIFESTO nao esta escrita no .py, e exigi-la
        # la seria exigir a coisa errada. Confere-se a PASTA no codigo e o NOME
        # na lista de onde ele vem.
        if e.get("DERIVADO_DE") == "PUBLICADO":
            nome = e["PATH"].rsplit("/", 1)[-1]
            pasta_ok = nomeia(p["EXECUTABLE"], e["PATH"].rsplit("/", 1)[0])
            if not (nome in CAD.CADEIA["PUBLICADO"] and pasta_ok):
                mudos.append((p["STEP_ID"], e["PATH"], "derivado de PUBLICADO"))
            continue
        onde = e.get("VIA") or p["EXECUTABLE"]
        if not nomeia(onde, e["PATH"]):
            mudos.append((p["STEP_ID"], e["PATH"], "via=%s" % (e.get("VIA") or "-")))
        if e.get("VIA"):
            # o VIA e um MODULO importado: confere-se pelo nome do import, que e
            # como o codigo o nomeia — o caminho nunca aparece num `import`.
            modulo = e["VIA"].rsplit("/", 1)[-1][:-3]
            if ("import %s" % modulo) not in texto(p["EXECUTABLE"]):
                sem_via.append((p["STEP_ID"], e["VIA"]))
prova("a_AST_confirma_todo_caminho_declarado", not mudos, mudos[:5])
prova("o_VIA_declarado_e_mesmo_importado_pelo_passo", not sem_via, sem_via[:4],)

# ── 9 · A DECLARACAO CONTRA O CODIGO — TESTEMUNHA 2: A CORRIDA ────────────
# A AST diz o que o codigo NOMEIA. So a corrida diz o que ele ABRIU. As duas
# erram de lados opostos: a AST acredita numa string que ninguem usa; a corrida
# nao ve o ficheiro que hoje nao existe. Juntas, fecham.
#
#     ANALISE ESTATICA PROVA CAN DO. SO A CORRIDA PROVA DID DO.
#
# Corre num CLONE DESCARTAVEL, com a arvore ja assente — medir a meio do ciclo
# mediria o ciclo, e nao o passo.

ESPIAO = r'''
import json, os, runpy, sys
RAIZ = os.path.realpath(os.getcwd())
LIDOS, ESCRITOS = set(), set()
def _rel(c):
    if isinstance(c, int) or (isinstance(c, str) and c.isdigit()):
        return None
    try:
        r = os.path.realpath(str(c))
    except (OSError, ValueError):
        return None
    if not r.startswith(RAIZ + os.sep):
        return None
    return os.path.relpath(r, RAIZ).replace(os.sep, "/")
def hook(ev, a):
    if ev == "open":
        p = _rel(a[0])
        if p is None:
            return
        esc = any(ch in a[1] for ch in "wxa+") if isinstance(a[1], str) else (
            bool(a[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)) if isinstance(a[2], int) else False)
        (ESCRITOS if esc else LIDOS).add(p)
    elif ev in ("os.rename", "os.replace"):
        for x in a[:2]:
            r = _rel(x)
            if r:
                ESCRITOS.add(r)
alvo, saida = sys.argv[1], sys.argv[2]
sys.argv = [alvo]
sys.addaudithook(hook)
rc = 0
try:
    runpy.run_path(alvo, run_name="__main__")
except SystemExit as x:
    rc = x.code if isinstance(x.code, int) else 0
except BaseException:
    rc = 99
# UM MODULO IMPORTADO SABE DIZER-SE: esta em sys.modules com __file__. Separar
# import de leitura andando na pilha nao funciona sob runpy — ha sempre um frame
# de importacao na ancestralidade, e uma tentativa anterior classificou TODAS as
# leituras como import por causa disso.
imp = set()
for m in list(sys.modules.values()):
    f = getattr(m, "__file__", None)
    if f:
        r = _rel(f)
        if r:
            imp.add(r); imp.add(r + "c")
fora = {alvo, saida}
lim = lambda s: sorted(x for x in s if x not in fora and "__pycache__" not in x
                       and x != "<unknown>")
json.dump({"RC": rc, "LIDOS": lim(LIDOS - ESCRITOS - imp),
           "ESCRITOS": lim(ESCRITOS)}, open(saida, "w"))
'''


def _correr(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def medir_em_clone():
    d = tempfile.mkdtemp(prefix="g4io-")
    raiz = os.path.join(d, "clone")
    r = _correr(["git", "clone", "-q", "--no-hardlinks", str(RAIZ), raiz], d)
    if r.returncode != 0:
        return None, "clone falhou: " + r.stderr[-200:]
    with open(os.path.join(raiz, "_espiao.py"), "w", encoding="utf-8") as fh:
        fh.write(ESPIAO)
    # assentar: as saidas da cadeia vivem dentro da impressao que ela carimba,
    # logo a primeira passagem muda a arvore que ela proria mediu. (G6)
    for _ in range(2):
        for exe in CAD.executaveis():
            _correr([sys.executable, exe], raiz)
    out = {}
    for p in PASSOS:
        nome = "_io_%s.json" % p["STEP_ID"]
        _correr([sys.executable, "_espiao.py", p["EXECUTABLE"], nome], raiz)
        f = os.path.join(raiz, nome)
        if not os.path.exists(f):
            return None, "o espiao nao deixou medicao para " + p["STEP_ID"]
        with open(f, encoding="utf-8") as fh:
            out[p["STEP_ID"]] = json.load(fh)
    rast = set(_correr(["git", "ls-files"], raiz).stdout.split())
    shutil.rmtree(d, ignore_errors=True)
    return (out, rast), None


import fnmatch  # noqa: E402

# A MEDICAO PODE SER REAPROVEITADA — E SO ENTRE MUTANTES DO MANIFESTO.
# Ela depende do CODIGO, nao da declaracao. Um mutante que mexe no manifesto
# nao muda uma leitura sequer, logo remedir seria pagar um minuto para obter o
# mesmo ficheiro. Um mutante que mexesse no CODIGO invalidava isto — e por isso
# a cache e explicita, por variavel de ambiente, e nunca o caminho normal.
CACHE = os.environ.get("G4_IO_CACHE")
if CACHE and os.path.exists(CACHE):
    with open(CACHE, encoding="utf-8") as fh:
        _c = json.load(fh)
    MED, erro = (_c["IO"], set(_c["RASTREADOS"])), None
else:
    MED, erro = medir_em_clone()
    if MED and CACHE:
        with open(CACHE, "w", encoding="utf-8") as fh:
            json.dump({"IO": MED[0], "RASTREADOS": sorted(MED[1])}, fh)
prova("a_medicao_de_runtime_correu_num_clone", MED is not None, erro)

if MED:
    IO, RASTREADOS = MED
    maus_rc = [s for s, d in IO.items() if d["RC"] != 0]
    prova("todo_passo_correu_sem_erro_no_clone", not maus_rc, maus_rc)

    # UM PASSO SEM MEDICAO NAO E UM PASSO VERIFICADO. Acontece quando o
    # STEP_ID muda, fica vazio, ou aparece um passo novo — e nesse caso as
    # conferencias seguintes nao tem sobre o que correr. Dize-lo com nome vale
    # mais do que rebentar com KeyError tres seccoes abaixo.
    sem_medida = [p["STEP_ID"] for p in PASSOS if p["STEP_ID"] not in IO]
    prova("todo_passo_do_manifesto_foi_medido", not sem_medida, sem_medida)
    MEDIDOS = [p for p in PASSOS if p["STEP_ID"] in IO]

    # V1 · toda entrada NOMEADA foi mesmo lida  → mata o INPUT INVENTADO
    inventadas = []
    for p in MEDIDOS:
        lidos = set(IO[p["STEP_ID"]]["LIDOS"])
        for e in p["INPUTS"]:
            if e["KIND"] == CAD.TRACKED_SOURCE_TREE:
                continue
            if e["PATH"] not in lidos:
                inventadas.append((p["STEP_ID"], e["PATH"]))
    prova("toda_entrada_declarada_foi_mesmo_lida", not inventadas, inventadas[:5])

    # V2 · toda saida declarada foi mesmo escrita  → mata o OUTPUT INVENTADO
    fantasmas = []
    for p in MEDIDOS:
        esc = set(IO[p["STEP_ID"]]["ESCRITOS"])
        for s in CAD.saidas(p):
            if s["PATH"] not in esc:
                fantasmas.append((p["STEP_ID"], s["PATH"]))
    prova("toda_saida_declarada_foi_mesmo_escrita", not fantasmas, fantasmas[:5])

    # V3 · toda escrita real esta declarada  → mata a ESCRITA ESCONDIDA
    escondidas = []
    for p in MEDIDOS:
        decl = {s["PATH"] for s in CAD.saidas(p)}
        for x in IO[p["STEP_ID"]]["ESCRITOS"]:
            if x.endswith(".a-escrever") or x.startswith("_io_"):
                continue
            if x not in decl:
                escondidas.append((p["STEP_ID"], x))
    prova("nenhuma_escrita_real_fica_por_declarar", not escondidas, escondidas[:5])

    # V4 · toda leitura real e EXPLICADA  → mata a LEITURA ESCONDIDA
    #      e o seletor tem de ser o que explica o varrimento, nao um `*` a cobrir
    #      tudo: quem declara arvore declara ORIGEM e PADRAO, e a prova confere
    #      que o que sobra cabe mesmo neles.
    orfas = []
    for p in MEDIDOS:
        nomeadas = {e["PATH"] for e in p["INPUTS"] if e["KIND"] != CAD.TRACKED_SOURCE_TREE}
        arvores = CAD.entradas(p, CAD.TRACKED_SOURCE_TREE)
        pads = [g for a in arvores for g in a["PADRAO"]]
        for x in IO[p["STEP_ID"]]["LIDOS"]:
            if x in nomeadas or x.startswith("_"):
                continue
            if not any(fnmatch.fnmatch(x, g) for g in pads):
                orfas.append((p["STEP_ID"], x))
    prova("toda_leitura_real_e_explicada_por_uma_entrada_declarada",
          not orfas, "%d orfas: %s" % (len(orfas), orfas[:5]))

    # V5 · O SELETOR NAO PODE SER MAIS LARGO DO QUE O QUE O PASSO VARRE.
    #      `*` so e honesto quando o passo enumera mesmo a arvore inteira — e um
    #      passo faz isso (SCAN_REPO, por `git ls-files`). Declarar `*` nos
    #      outros seria exactamente «a arvore toda como entrada generica».
    largos = []
    for p in MEDIDOS:
        for a in CAD.entradas(p, CAD.TRACKED_SOURCE_TREE):
            if a["PADRAO"] != ["*"]:
                continue
            if a.get("ORIGEM_ARTEFATO"):
                continue          # o `*` e sobre a lista do artefato, nao sobre o git
            varridos = len([x for x in IO[p["STEP_ID"]]["LIDOS"]])
            if varridos < len(RASTREADOS) * 0.8:
                largos.append((p["STEP_ID"], varridos, len(RASTREADOS)))
    prova("nenhum_passo_declara_a_arvore_toda_medindo_um_pedaco",
          not largos, largos)

    # E o numero que a declaracao publica tem de bater com o que se mediu.
    #     UM NUMERO DECLARADO QUE NINGUEM CONFERE E UMA LEMBRANCA.
    tortos = []
    for p in MEDIDOS:
        nomeadas = {e["PATH"] for e in p["INPUTS"] if e["KIND"] != CAD.TRACKED_SOURCE_TREE}
        varr = len([x for x in IO[p["STEP_ID"]]["LIDOS"]
                    if x not in nomeadas and not x.startswith("_")])
        for a in CAD.entradas(p, CAD.TRACKED_SOURCE_TREE):
            if abs(a["MEDIDO_VARRE"] - varr) > max(8, varr * 0.05):
                tortos.append((p["STEP_ID"], a["MEDIDO_VARRE"], varr))
    prova("o_MEDIDO_VARRE_declarado_bate_com_a_corrida", not tortos, tortos)

    # E O CICLO, MEDIDO E NAO SO DECLARADO: o pente fino leu mesmo o state.
    pf = IO["PENTE_FINO_DA_COLETA"]["LIDOS"]
    prova("a_corrida_confirma_o_ciclo_do_pente_fino",
          "system-map/data/state.generated.json" in pf,
          "se ele deixasse de o ler, a divida do G6 mudava — e isto avisaria")

print()
print("=" * 70)
if FALHAS:
    print("CADEIA_IO=FAIL · %d prova(s) reprovada(s)" % len(FALHAS))
    for f in FALHAS:
        print("  ·", f)
    raise SystemExit(1)
print("CADEIA_IO=PASS · cada passo declara o que le e o que escreve, e confere")
