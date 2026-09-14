#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DA ORDEM E DO CICLO ATRASADO — G6.

    python3 system-map/tests/test_ordem_por_dependencia.py
    python3 system-map/tests/test_ordem_por_dependencia.py --sem-clone

O G5 provou que existe UMA lista dona da cadeia. Faltava provar que essa cadeia
corre na ordem certa — e ela nao corria. Tres consumidores corriam antes do seu
produtor, e nenhum deles dava erro: cada um abria um ficheiro que EXISTIA, o da
rodada anterior.

    UM CONSUMIDOR ANTES DO PRODUTOR NAO FALHA:
    ELE RESPONDE DA RODADA PASSADA.

E por isso que isto nao se apanha a correr a cadeia: ela fica verde na mesma. So
se apanha comparando o que cada passo DIZ que le com o sitio onde ele corre.

O QUE ESTE FICHEIRO CONFERE
---------------------------
    ORDEM       a ordem sai do grafo, e o ficheiro esta escrito nessa ordem
    GRAFO       toda entrada gerada sabe dizer quem a escreve
    CICLOS      cada ciclo tem classe, e a classe e defendida com prova
    LEI         a lei do ciclo atrasado responde as cinco perguntas dela
    FRESCURA    um atraso que o grafo NAO explica chama-se defeito
    MAO         quem nao e automatizado diz porque, e o porque foi medido
    RECUSA      corredor e publicador recusam-se a correr ordem contraditoria
    CONVERGE    mexe-se numa fonte e a cadeia assenta: a 2a e a 3a passagem
                dao o mesmo conteudo, e a 1a nao — que e o atraso a ver-se

O QUE ELE NAO CONFERE, E PORQUE
-------------------------------
Nao repete o contrato de IO (`test_cadeia_declara_io.py`) nem a lei de um dono
so (`test_uma_cadeia_um_dono.py`). Uma prova que confere tudo outra vez nao e
mais forte: e mais uma copia a envelhecer ao lado das outras.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import cadeia_do_mapa as CAD                               # noqa: E402
import impressao_da_arvore as IMPRESSAO                    # noqa: E402

MANIFESTO = RAIZ / "system-map/scripts/CADEIA-DO-MAPA.json"
FALHAS = []


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome
          + ("" if ok else "  " + str(porque)[:320]))
    if not ok:
        FALHAS.append(nome)


def correr(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", timeout=2400, **kw)


MANIFESTO_COMO_ESTAVA = MANIFESTO.read_text(encoding="utf-8")


def com_manifesto(mudar, cmd, cwd=None):
    """Corre `cmd` com o manifesto MUTADO, e repoe-o sempre.

        LER O ORIGINAL ANTES DE MUTAR, E REPOR NO `finally`.
    Um arnes que perde o original nao esta a atacar o produto: esta a
    destrui-lo, e as mortes que reporta a seguir sao todas falsas.

    ⚠️ E O `finally` NAO CHEGA. Se o processo for morto a meio — timeout,
    Ctrl-C, o CI a cortar o job — o `finally` nao corre e o manifesto fica
    MUTADO no disco de trabalho. Aconteceu nesta missao: uma linha de INPUTS
    ficou apagada e foi para `git add`, e so a prova de IO a apanhou tres
    corridas depois.

        UM ARNES QUE SO REPOE QUANDO ACABA BEM
        DEIXA O ESTRAGO EXACTAMENTE NOS DIAS MAUS.

    Por isso o original e lido no arranque do modulo, e ha uma guarda no fim
    que compara o ficheiro com ele.
    """
    original = MANIFESTO.read_text(encoding="utf-8")
    try:
        d = json.loads(original)
        mudar(d)
        MANIFESTO.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        return correr(cmd, cwd or RAIZ)
    finally:
        MANIFESTO.write_text(original, encoding="utf-8")


LEITURA = ("import sys,json;sys.path.insert(0,'system-map/scripts');"
           "import cadeia_do_mapa as C;")

print("=" * 74)
print("A ORDEM DA CADEIA — %d passos, %d arestas"
      % (len(CAD.passos()), len(CAD.arestas())))
print("=" * 74)

# ── 1 · A ORDEM SAI DO GRAFO ──────────────────────────────────────────────
escrita = [p["STEP_ID"] for p in CAD.ordem_escrita()]
derivada = CAD.ordem_derivada()
prova("o_leitor_deriva_uma_ordem_total",
      sorted(derivada) == sorted(escrita) and len(derivada) == len(set(derivada)),
      "%d derivados para %d escritos" % (len(derivada), len(escrita)))
prova("a_ordem_escrita_e_a_ordem_derivada", escrita == derivada,
      [(i, a, b) for i, (a, b) in enumerate(zip(escrita, derivada), 1) if a != b])
prova("passos_devolve_a_ordem_derivada",
      [p["STEP_ID"] for p in CAD.passos()] == derivada)

pos = {s: i for i, s in enumerate(derivada)}
violacoes = [(a["PRODUTOR"], a["CONSUMIDOR"], a["ARTEFATO"]) for a in CAD.arestas()
             if a["CLASSE"] == CAD.NOMEADA
             and a["PRODUTOR"] in pos and a["CONSUMIDOR"] in pos
             and pos[a["PRODUTOR"]] >= pos[a["CONSUMIDOR"]]]
prova("NORMAL_DEPENDENCY_ORDER_VIOLATIONS_e_zero", not violacoes, violacoes)

# A ORDEM NAO PODE DEPENDER DE COMO O FICHEIRO ESTA ESCRITO. Se depender, ela e
# a lista a fingir-se de derivacao. Baralha-se a lista escrita e exige-se que a
# ordem continue a respeitar TODAS as arestas nomeadas.
#
#     UMA DERIVACAO QUE MUDA DE RESPOSTA CONFORME A SEMENTE
#     NAO ESTA A DERIVAR: ESTA A COPIAR COM UM PASSO EXTRA.
def baralhada(d):
    d["REGERAR"] = list(reversed(d["REGERAR"]))


r = com_manifesto(baralhada, [sys.executable, "-c", LEITURA + """
import json
o = C.ordem_derivada(); pos = {s: i for i, s in enumerate(o)}
mau = [(a['PRODUTOR'], a['CONSUMIDOR']) for a in C.arestas()
       if a['CLASSE'] == C.NOMEADA and a['PRODUTOR'] in pos and a['CONSUMIDOR'] in pos
       and pos[a['PRODUTOR']] >= pos[a['CONSUMIDOR']]]
print(json.dumps({'ORDEM': o, 'MAU': mau}))"""])
try:
    virada = json.loads(r.stdout.strip().splitlines()[-1])
except (ValueError, IndexError):
    virada = None
prova("com_a_lista_ao_contrario_a_ordem_continua_a_respeitar_o_grafo",
      bool(virada) and not virada["MAU"],
      (virada or {}).get("MAU", r.stderr[-200:]))
prova("e_a_lista_ao_contrario_da_mesmo_uma_ordem_diferente",
      bool(virada) and virada["ORDEM"] != derivada,
      "se desse a mesma, esta prova nao estava a mexer em nada")

# E `passos()` TEM DE ENTREGAR A DERIVADA, e nao a lista como esta no ficheiro.
# Com o manifesto certo as duas coincidem — de proposito — e por isso esta
# diferenca so se ve com o ficheiro escrito ao contrario.
#
#     DUAS COISAS IGUAIS HOJE NAO SAO A MESMA COISA:
#     SO SE SABE QUAL DELAS MANDA QUANDO ELAS DISCORDAM.
r = com_manifesto(baralhada, [sys.executable, "-c", LEITURA + """
import json
print(json.dumps([p['STEP_ID'] for p in C.passos()] == C.ordem_derivada()))"""])
prova("passos_entrega_a_derivada_mesmo_com_o_ficheiro_ao_contrario",
      r.stdout.strip().splitlines()[-1:] == ["true"],
      (r.stdout + r.stderr)[-200:])

# ── 2 · O GRAFO ESTA COMPLETO ─────────────────────────────────────────────
prova("UNRESOLVED_DEPENDENCIES_e_zero", not CAD.nao_resolvidas(),
      CAD.nao_resolvidas())
externas = [a for a in CAD.arestas() if a["CLASSE"] == CAD.EXTERNA]
prova("o_que_vem_de_fora_tem_dono_declarado",
      all(any(x["PATH"] == a["ARTEFATO"] and x.get("DONO")
              for x in CAD.produtores_externos()) for a in externas),
      "uma entrada sem produtor na cadeia so pode ficar em PRODUTORES_EXTERNOS")

# UMA DEPENDENCIA APONTADA A UM PASSO QUE NAO EXISTE TEM DE DOER.
# ⚠️ E NAO CHEGA OLHAR PARA AS ARESTAS. Um `INCLUI_GERADOS` com um nome
# inventado nao produz aresta nenhuma — o passo nao existe, logo nao tem saidas
# — e por isso passava por baixo de qualquer conferencia feita sobre o grafo.
#
#     UMA REFERENCIA QUE NAO GERA ARESTA NAO E INOFENSIVA:
#     E UMA DEPENDENCIA QUE DESAPARECEU EM SILENCIO.
ids = {p["STEP_ID"] for p in CAD.todas_as_execucoes()}
mortos = sorted({a["PRODUTOR"] for a in CAD.arestas()
                 if a["CLASSE"] != CAD.EXTERNA and a["PRODUTOR"] not in ids})
inventados = sorted({x for p in CAD.passos() + CAD.passos_a_mao() + CAD.passos_de_validar()
                     for e in CAD.entradas(p, CAD.TRACKED_SOURCE_TREE)
                     for x in (e.get("INCLUI_GERADOS") or []) if x not in ids})
prova("nenhuma_dependencia_aponta_para_passo_inexistente",
      not mortos and not inventados, mortos + inventados)

# CADA SAIDA TEM UM DONO SO. Dois produtores para o mesmo caminho e a segunda
# cadeia a nascer dentro do grafo.
donos = {}
for p in CAD.passos() + CAD.passos_a_mao():
    for s in CAD.saidas(p):
        donos.setdefault(s["PATH"], []).append(p["STEP_ID"])
duplos = {k: v for k, v in donos.items() if len(v) > 1}
prova("cada_artefato_tem_um_produtor_so", not duplos, duplos)

sem_saida = [p["STEP_ID"] for p in CAD.passos() if not CAD.saidas(p)]
prova("nenhum_passo_de_regeracao_deixa_de_produzir", not sem_saida,
      "%s — um passo sem saida nao compoe o mapa: ou e prova, ou e portao"
      % sem_saida)

# ── 3 · OS CICLOS TEM CLASSE ──────────────────────────────────────────────
ciclos = CAD.ciclos()
# ⚠️ SEM ISTO, TUDO O QUE VEM A SEGUIR E VACUO. Um `ciclos()` que devolvesse
# lista vazia passava as quatro provas seguintes sem medir nada — e o ciclo
# continuava la, sem classe e sem lei.
#
#     «NENHUM CICLO ESTA MAL CLASSIFICADO» E VERDADE TRIVIAL
#     QUANDO NAO HA CICLO NENHUM PARA CLASSIFICAR.
prova("o_ciclo_atrasado_existe_e_esta_declarado",
      any(c["CLASSE"] == "DELAYED_CYCLE" for c in ciclos),
      "a cadeia mede uma arvore onde ela propria escreve; se isto nao ve ciclo "
      "nenhum, e o grafo que esta cego")
prova("todo_ciclo_tem_classe_do_vocabulario",
      all(c["CLASSE"] in ("DELAYED_CYCLE", "BUG") for c in ciclos),
      [c["CLASSE"] for c in ciclos])
prova("UNCLASSIFIED_CYCLES_e_zero",
      not [c for c in ciclos if c["CLASSE"] not in ("DELAYED_CYCLE", "BUG")])
prova("nenhum_ciclo_e_BUG", not [c for c in ciclos if c["CLASSE"] == "BUG"],
      [c["MEMBROS"] for c in ciclos if c["CLASSE"] == "BUG"])
prova("todo_ciclo_atrasado_mostra_o_corte_no_tempo",
      all(c["CORTES_NO_TEMPO"] for c in ciclos if c["CLASSE"] == "DELAYED_CYCLE"),
      "sem corte declarado, «ciclo atrasado» e so uma palavra por cima de um ciclo")

# A PROVA DE QUE O ATRASO NAO SE ORDENA: existe uma varredura sobre si propria.
# Nenhuma permutacao poe um passo antes de si mesmo. Sem isto, «e estrutural»
# era opiniao; com isto, e aritmetica.
laco = [a for a in CAD.arestas()
        if a["CLASSE"] == CAD.VARREDURA and a["PRODUTOR"] == a["CONSUMIDOR"]]
prova("ha_uma_varredura_que_apanha_a_propria_saida", bool(laco),
      "%s" % sorted({a["CONSUMIDOR"] for a in laco}))

atrasados = CAD.atrasos()
prova("nenhuma_dependencia_NOMEADA_esta_atrasada",
      not [a for a in atrasados if a["CLASSE"] == CAD.NOMEADA],
      [(a["CONSUMIDOR"], a["PRODUTOR"]) for a in atrasados
       if a["CLASSE"] == CAD.NOMEADA])
prova("e_os_atrasos_que_restam_sao_todos_de_varredura",
      bool(atrasados) and all(a["CLASSE"] == CAD.VARREDURA for a in atrasados),
      "%d atrasos, %d de varredura"
      % (len(atrasados), sum(1 for a in atrasados if a["CLASSE"] == CAD.VARREDURA)))

# ── 4 · A LEI RESPONDE AS PERGUNTAS DELA ──────────────────────────────────
#     UMA LEI QUE NAO DIZ QUAL ARTEFATO, QUAL RODADA E PORQUE
#     NAO E UMA LEI: E UMA DESCULPA COM CABECALHO.
LEI = CAD.CADEIA.get("LEI_DO_CICLO_ATRASADO") or {}
for chave in ("QUE_ARTEFATO_E_ATRASADO", "QUE_VERSAO_E_LIDA",
              "PORQUE_PRECISA_DE_SER_ATRASADO",
              "COMO_SE_SABE_QUE_NAO_E_STALE_ACIDENTAL", "COMO_O_MAPA_COMUNICA"):
    prova("a_lei_do_ciclo_atrasado_responde[%s]" % chave,
          bool(LEI.get(chave)) and len("".join(LEI.get(chave))) > 80, chave)
prova("a_lei_da_ordem_esta_declarada_no_manifesto",
      bool((CAD.CADEIA.get("LEI_DA_ORDEM") or {}).get("REGRA")))
prova("a_lei_da_ordem_nomeia_o_dono_da_derivacao",
      "cadeia_do_mapa" in str((CAD.CADEIA.get("LEI_DA_ORDEM") or {}).get("DONO")))
prova("as_duas_classes_de_aresta_estao_escritas",
      set((CAD.CADEIA.get("LEI_DA_ORDEM") or {}).get("DUAS_CLASSES_DE_ARESTA") or {})
      >= {CAD.NOMEADA, CAD.VARREDURA})

# ── 5 · A DERIVACAO NAO SE DEIXA ENGANAR ──────────────────────────────────
# Um ciclo entre NOMEADAS nao pode ser ordenado nem calado: tem de rebentar.
def ciclo_nomeado(d):
    alvo = next(p for p in d["REGERAR"] if p["STEP_ID"] == "SCAN_REPO")
    alvo["INPUTS"].append({
        "KIND": "GENERATED_ARTIFACT",
        "PATH": "system-map/data/state.generated.json",
        "PRODUCER": "GENERATE_SYSTEM_MAP",
        "PRODUCER_EXECUTABLE": "system-map/scripts/generate_system_map.py",
        "PORQUE": "ataque: ciclo A->B->A entre nomeadas"})


r = com_manifesto(ciclo_nomeado, [sys.executable, "-c", LEITURA
                                  + "C.ordem_derivada()"])
prova("um_ciclo_entre_nomeadas_rebenta_em_vez_de_ser_ordenado",
      r.returncode != 0 and "CicloNomeado" in r.stderr,
      r.stderr[-200:] or r.stdout[-200:])

# Declarar VARREDURA uma dependencia que e pedida pelo nome e a fuga mais barata
# a esta lei. O que a fecha nao e uma proibicao: e a corrida — quem le pelo nome
# abre o ficheiro, e o contrato de IO ve-o a abrir.
def apagar_a_aresta(d):
    alvo = next(p for p in d["REGERAR"] if p["STEP_ID"] == "GENERATE_SYSTEM_MAP")
    alvo["INPUTS"] = [e for e in alvo["INPUTS"]
                      if e.get("PATH") != "system-map/data/sources.generated.json"]


r = com_manifesto(apagar_a_aresta,
                  [sys.executable, "system-map/tests/test_cadeia_declara_io.py"])
prova("apagar_uma_dependencia_real_e_apanhado_pela_corrida", r.returncode != 0,
      "o contrato de IO tem de acusar a leitura que ficou por declarar")

# Uma dependencia INVENTADA tambem tem de doer — senao qualquer um empurra um
# passo para onde quer, escrevendo uma aresta que nao existe.
def aresta_falsa(d):
    alvo = next(p for p in d["REGERAR"] if p["STEP_ID"] == "SCAN_CASCO")
    alvo["INPUTS"].append({
        "KIND": "GENERATED_ARTIFACT",
        "PATH": "system-map/data/topologia.generated.json",
        "PRODUCER": "CENSO_DA_TOPOLOGIA",
        "PRODUCER_EXECUTABLE": "system-map/scripts/censo_da_topologia.py",
        "PORQUE": "ataque: dependencia que nao existe"})


r = com_manifesto(aresta_falsa,
                  [sys.executable, "system-map/tests/test_cadeia_declara_io.py"])
prova("uma_dependencia_inventada_e_apanhada_pela_corrida", r.returncode != 0,
      "declarar uma entrada que o passo nunca abre tem de reprovar")

# ── 6 · A FRESCURA CLASSIFICA, E NAO PERDOA ───────────────────────────────
VOCABULARIO = ("CURRENT", "EXPECTED_PREVIOUS_CYCLE", "UNEXPECTED_STALE", "UNKNOWN")
OS_CARIMBADOS = ["system-map/data/censo-da-coleta.generated.json",
                 "system-map/data/pente-fino.generated.json",
                 "system-map/data/sources.generated.json",
                 "system-map/data/topologia.generated.json",
                 "system-map/data/architecture.generated.json"]
vistos = {}
for alvo in OS_CARIMBADOS:
    f = RAIZ / alvo
    if not f.is_file():
        continue
    prov = (json.loads(f.read_text(encoding="utf-8")).get("PROVENANCE") or {})
    v = IMPRESSAO.frescura_do_carimbo(prov)
    vistos[alvo] = v
    prova("a_frescura_classifica_o_ciclo[%s]" % Path(alvo).name,
          v.get("CLASSE_DO_CICLO") in VOCABULARIO, v.get("CLASSE_DO_CICLO"))

# UM ATRASO QUE O GRAFO NAO EXPLICA NAO PODE SER ACEITE COMO ESPERADO.
enganados = [a for a, v in vistos.items()
             if v.get("CLASSE_DO_CICLO") == "EXPECTED_PREVIOUS_CYCLE"
             and not (v.get("ENTRADAS_GERADAS_DE_OUTRA_ARVORE") or [])]
prova("UNEXPECTED_STALE_ACCEPTED_AS_EXPECTED_e_zero", not enganados, enganados)

# A CLASSE TEM DE VIR DO CONTRATO, E PROVA-SE TIRANDO O CONTRATO.
# Os tres regeneradores a mao estao velhos por contrato: nenhuma automacao os
# corre, e isso esta escrito. Tira-se-lhes a CLASSE_DE_EXECUCAO e o mesmo
# artefato tem de voltar a ser UNEXPECTED_STALE — senao a classe nao estava a
# ler o contrato, estava a decorar um nome.
#
#     UMA CLASSE QUE NAO MUDA QUANDO A DECLARACAO MUDA
#     NAO ESTA A CLASSIFICAR: ESTA A ETIQUETAR.
DERIVADO = "data/derivados/MATRIZ-CARDS-SENSORES-V1.json"
CLASSE = ("import sys,json;sys.path.insert(0,'system-map/scripts');"
          "import impressao_da_arvore as I;"
          "d=json.load(open(%r,encoding='utf-8'));"
          "print(I.frescura_do_carimbo(d.get('PROVENANCE') or {})"
          ".get('CLASSE_DO_CICLO'))" % DERIVADO)
if (RAIZ / DERIVADO).is_file():
    agora = correr([sys.executable, "-c", CLASSE], RAIZ).stdout.strip()
    prova("o_artefato_a_mao_esta_velho_por_contrato",
          agora in ("EXPECTED_PREVIOUS_CYCLE", "CURRENT"), agora)

    def sem_contrato(d):
        for x in d["REGERAR_A_MAO"]:
            x.pop("CLASSE_DE_EXECUCAO", None)

    sem = com_manifesto(sem_contrato, [sys.executable, "-c", CLASSE]).stdout.strip()
    prova("e_sem_a_classe_declarada_volta_a_ser_defeito",
          agora == "CURRENT" or sem == "UNEXPECTED_STALE",
          "com contrato: %s · sem contrato: %s" % (agora, sem))

# E OS DOIS CASOS DE DEFEITO TEM DE SER EXERCIDOS, e nao esperados do acaso.
# No ponto fixo nao ha artefacto STALE nenhum — logo, sem construir o caso, as
# duas linhas que decidem «isto e defeito» nunca correm, e uma mutacao que as
# apagasse passava sem ninguem dar por nada.
#
#     UMA GUARDA QUE SO CORRE QUANDO HA DEFEITO
#     NUNCA CORRE NUM REPOSITORIO SAUDAVEL.
falso = {"GENERATED_BY": "system-map/scripts/pente_fino_da_coleta.py"}
prova("arvore_mexida_sem_contrato_de_mao_e_sempre_defeito",
      IMPRESSAO.classe_do_ciclo(falso, False, False, True, []) == "UNEXPECTED_STALE",
      "a impressao exclui as saidas da cadeia: se a arvore mexeu, mexeu uma "
      "fonte, e nenhuma lei de ciclo cobre isso")
prova("entrada_gerada_velha_de_um_produtor_que_corre_antes_e_defeito",
      IMPRESSAO.classe_do_ciclo(
          falso, False, True, True,
          ["system-map/data/state.generated.json"]) == "UNEXPECTED_STALE",
      "o gerador corre ANTES do pente fino; se a saida dele chegou velha, o "
      "grafo nao explica nada")
prova("sem_carimbo_a_classe_e_UNKNOWN_e_nao_CURRENT",
      IMPRESSAO.frescura_do_carimbo(falso).get("CLASSE_DO_CICLO") == "UNKNOWN",
      IMPRESSAO.frescura_do_carimbo(falso))
prova("um_artefato_sem_PROVENANCE_nao_ganha_classe_boa",
      IMPRESSAO.frescura_do_carimbo({}).get("CLASSE_DO_CICLO") == "UNKNOWN")

# UM ARTEFATO QUE SO CARIMBA A ARVORE, COM A ARVORE MEXIDA, NAO PODE SER CURRENT.
# Este e o ramo curto da frescura — o dos artefactos sem INPUTS declarados — e
# no ponto fixo ele nunca corre com a arvore diferente. Sem o construir, uma
# mutacao que o pusesse a dizer CURRENT passava sem ninguem dar por nada.
so_arvore = IMPRESSAO.frescura_do_carimbo({"SOURCE_TREE_FINGERPRINT": "0" * 64})
prova("so_a_arvore_com_a_arvore_mexida_nunca_e_CURRENT",
      so_arvore["VEREDITO"] == "STALE"
      and so_arvore.get("CLASSE_DO_CICLO") != "CURRENT", so_arvore)

# E O ATRASO POR VARREDURA TEM DE APARECER ONDE ELE EXISTE.
# `SCAN_REPO` corre em primeiro e varre a arvore toda: as saidas de todos os
# passos seguintes caem no seletor dele. Se isto vier vazio, o unico sitio onde
# o atraso e comunicado ficou mudo.
atraso_scan = IMPRESSAO.atraso_por_varredura(
    {"GENERATED_BY": "system-map/scripts/scan_repo.py"})
prova("a_frescura_diz_o_atraso_por_varredura_de_quem_o_tem",
      bool(atraso_scan), atraso_scan)
prova("e_diz_NAO_SEI_quando_nao_sabe_quem_gerou",
      IMPRESSAO.atraso_por_varredura({"GENERATED_BY": "nao/existe.py"}) is None,
      "[] diria «nenhum»; a resposta certa e nao saber")

# ── 7 · QUEM NAO E AUTOMATIZADO DIZ PORQUE ────────────────────────────────
for p in CAD.passos_a_mao():
    c = CAD.classe_de_execucao(p)
    prova("o_regenerador_a_mao_tem_classe[%s]" % p["STEP_ID"],
          c in CAD.CLASSES_DE_EXECUCAO and c != CAD.DESCONHECIDO, c)
    prova("e_diz_porque[%s]" % p["STEP_ID"],
          c != CAD.MANUAL_BY_CONTRACT or len(p.get("PORQUE_MANUAL") or "") > 80,
          "MANUAL_BY_CONTRACT sem razao escrita e so «ninguem corre isto»")
    prova("e_nao_esta_UNREACHABLE_sem_dizer[%s]" % p["STEP_ID"],
          (RAIZ / p["EXECUTABLE"]).is_file() or c == CAD.UNREACHABLE,
          "o executavel nao existe e a classe nao diz UNREACHABLE")
prova("o_vocabulario_das_classes_esta_declarado",
      set(CAD.CADEIA.get("CLASSES_DE_EXECUCAO", {}).get("VOCABULARIO") or [])
      == set(CAD.CLASSES_DE_EXECUCAO))
prova("um_passo_a_mao_sem_classe_declarada_da_UNKNOWN",
      CAD.classe_de_execucao({"STEP_ID": CAD.passos_a_mao()[0]["STEP_ID"]})
      == CAD.DESCONHECIDO,
      "por omissao tem de dar UNKNOWN, nunca MANUAL")

# TODA A CATEGORIA QUE O MANIFESTO ANUNCIA TEM DE TER CORREDOR.
for categoria in CAD.CATEGORIAS:
    r = correr([sys.executable, "system-map/scripts/correr_a_cadeia.py",
                "--listar", categoria], RAIZ)
    prova("o_corredor_sabe_correr[%s]" % categoria, r.returncode == 0,
          r.stderr[-200:])

# ── 8 · ORDEM CONTRADITORIA E RECUSADA ────────────────────────────────────
def ordem_trocada(d):
    ordem = d["REGERAR"]
    i = next(k for k, p in enumerate(ordem) if p["STEP_ID"] == "PENTE_FINO_DA_COLETA")
    ordem.insert(0, ordem.pop(i))


r = com_manifesto(ordem_trocada, [sys.executable,
                                  "system-map/scripts/correr_a_cadeia.py",
                                  "--listar", "REGERAR"])
prova("o_corredor_recusa_uma_ordem_que_contradiz_as_dependencias",
      r.returncode != 0 and "contradiz" in (r.stderr + r.stdout),
      (r.stderr + r.stdout)[-200:])

# O PUBLICADOR TEM DE CONFERIR **E** DE AGIR. Ter a funcao e nao a ligar a
# decisao de regenerar seria a conferencia a existir para o teste e nao para a
# build.
js = (RAIZ / "system-map/scripts/publicar_no_deploy.mjs").read_text(encoding="utf-8")
prova("o_publicador_tambem_confere_a_ordem",
      "function violacoesDaOrdem()" in js and "LEI_DA_ORDEM" in js,
      "o lado JavaScript le a ordem escrita; sem conferencia, a build publica "
      "um mapa montado pela ordem errada e ninguem da por isso")
prova("e_a_conferencia_do_publicador_decide_mesmo_alguma_coisa",
      "} else if (violacoesDaOrdem().length) {" in js
      and "porqueNaoRegenerou" in js.split("violacoesDaOrdem().length) {")[1][:400],
      "a funcao existe mas nao trava a regeneracao: conferir sem recusar e so "
      "escrever a verdade num sitio onde ninguem a le")
r = correr([sys.executable, "system-map/scripts/correr_a_cadeia.py", "--listar",
            "REGERAR"], RAIZ)
prova("o_corredor_e_o_leitor_entregam_a_mesma_ordem",
      [l.strip() for l in r.stdout.splitlines() if l.strip()] == CAD.executaveis(),
      "se o corredor corresse outra ordem, a lei valia para o leitor e nao para "
      "quem corre")

# ── 8b · ESTA PROVA NAO PODE OLHAR SO PARA METADE ─────────────────────────
# Uma validacao parcial passa sempre: basta nao olhar para o sitio onde esta o
# defeito. O universo desta prova vem do manifesto, e nada aqui pode estar preso
# a um numero nem a uma fatia.
#
#     UMA PROVA QUE SE FIXA NUM NUMERO PROVA A DATA EM QUE FOI ESCRITA.
import ast as _ast                                                # noqa: E402
_meu = _ast.parse(Path(__file__).read_text(encoding="utf-8"))
_fatias = [n.lineno for n in _ast.walk(_meu)
           if isinstance(n, _ast.Subscript) and isinstance(n.slice, _ast.Slice)
           and isinstance(getattr(n, "value", None), _ast.Call)
           and isinstance(n.value.func, _ast.Attribute)
           and n.value.func.attr in ("arestas", "passos", "ciclos", "atrasos")]
prova("esta_prova_nao_corta_o_universo_em_fatias", not _fatias, _fatias)
# ⚠️ A PRIMEIRA VERSAO DESTA GUARDA APANHAVA `len(texto) > 80`. Ela procurava
# «len(...) comparado com inteiro» e por isso acusava as guardas que exigem
# prosa minima na lei — que nao tem numero de passos nenhum lá dentro.
#
#     UMA GUARDA QUE ACUSA A FORMA EM VEZ DO PERIGO
#     ENSINA QUEM A LE A DESLIGA-LA.
#
# O perigo e prender-se ao tamanho do UNIVERSO. E isso conhece-se pelo que esta
# dentro do `len()`: uma chamada ao leitor da cadeia.
_DO_UNIVERSO = ("passos", "arestas", "ciclos", "atrasos", "ordem_derivada",
                "ordem_escrita", "passos_a_mao", "todas_as_execucoes")
_presos = []
for n in _ast.walk(_meu):
    if not (isinstance(n, _ast.Compare) and isinstance(n.left, _ast.Call)
            and isinstance(n.left.func, _ast.Name) and n.left.func.id == "len"):
        continue
    dentro = n.left.args[0] if n.left.args else None
    nome = getattr(getattr(dentro, "func", None), "attr", None) \
        or getattr(getattr(dentro, "func", None), "id", None) \
        or getattr(dentro, "id", None)
    if nome not in _DO_UNIVERSO:
        continue
    for c in n.comparators:
        if isinstance(c, _ast.Constant) and isinstance(c.value, int):
            _presos.append(n.lineno)
prova("esta_prova_nao_esta_presa_a_um_numero_de_passos", not _presos, _presos)

if "--sem-clone" in sys.argv:
    prova("o_manifesto_ficou_como_estava",
          MANIFESTO.read_text(encoding="utf-8") == MANIFESTO_COMO_ESTAVA,
          "o arnes muta o manifesto; sem esta conferencia o estrago sai daqui "
          "silencioso")
    print()
    print("  (as provas de clone ficam de fora: corrida aninhada)")
    print("=" * 74)
    if FALHAS:
        print("ORDEM_POR_DEPENDENCIA=FAIL · %d prova(s)" % len(FALHAS))
        raise SystemExit(1)
    print("ORDEM_POR_DEPENDENCIA=PASS (sem clone)")
    raise SystemExit(0)

# ── 9 · CONVERGENCIA: DUAS PASSAGENS, O MESMO CONTEUDO ────────────────────
#     SE A SEGUNDA PASSAGEM MUDASSE ALGUMA COISA, O ATRASO DA VARREDURA
#     NAO ERA UM CICLO ATRASADO: ERA UMA CADEIA QUE NUNCA ASSENTA.
#
# O relogio nao conta, e isso DIZ-SE em vez de se esconder: BYTE_DETERMINISM e
# SEMANTIC_DETERMINISM sao duas perguntas, e so a segunda e que esta lei promete.
base = Path(tempfile.mkdtemp(prefix="g6-"))
try:
    alvo = base / "r"
    r = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--shared",
                        str(RAIZ), str(alvo)], capture_output=True, text=True)
    prova("o_clone_nasce", r.returncode == 0, r.stderr[-200:])
    for linha in subprocess.run(["git", "status", "--porcelain"], cwd=str(RAIZ),
                                capture_output=True, text=True).stdout.splitlines():
        caminho = linha[3:].strip().strip('"')
        o, dd = RAIZ / caminho, alvo / caminho
        if o.is_file():
            dd.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(o, dd)

    def limpar(x):
        if isinstance(x, dict):
            return {k: limpar(v) for k, v in x.items() if k != "GENERATED_AT"}
        if isinstance(x, list):
            return [limpar(v) for v in x]
        return x

    def retrato(raiz):
        """O conteudo de tudo o que a cadeia escreve, sem o relogio."""
        fora = {}
        for p in CAD.passos():
            for s in CAD.saidas(p):
                f = raiz / s["PATH"]
                if not f.is_file():
                    continue
                try:
                    fora[s["PATH"]] = json.dumps(
                        limpar(json.loads(f.read_text(encoding="utf-8"))),
                        sort_keys=True, ensure_ascii=False)
                except ValueError:
                    fora[s["PATH"]] = f.read_text(encoding="utf-8", errors="replace")
        return fora

    # ⚠️ CORRER DUAS VEZES SOBRE UMA ARVORE JA ASSENTE NAO PROVA CONVERGENCIA:
    # prova que um no-op e um no-op. E preciso MEXER primeiro — senao a segunda
    # passagem nao tinha nada para arrumar e a prova era vacua por construcao.
    #
    #     UMA PROVA DE CONVERGENCIA QUE COMECA NO PONTO FIXO
    #     MEDE O PONTO FIXO, NAO A CONVERGENCIA.
    zero = retrato(alvo)
    marca = alvo / "AGENTS.md"
    marca.write_text(marca.read_text(encoding="utf-8")
                     + "\n<!-- fonte mexida para medir a convergencia -->\n",
                     encoding="utf-8")

    corredor = ["python3", "system-map/scripts/correr_a_cadeia.py", "REGERAR"]
    r1 = correr(corredor, alvo)
    prova("RUN_1_corre", r1.returncode == 0, r1.stderr[-300:])
    a = retrato(alvo)
    r2 = correr(corredor, alvo)
    prova("RUN_2_corre", r2.returncode == 0, r2.stderr[-300:])
    b = retrato(alvo)
    r3 = correr(corredor, alvo)
    prova("RUN_3_corre", r3.returncode == 0, r3.stderr[-300:])
    c3 = retrato(alvo)

    # ⚠️ UMA PROVA DE IGUALDADE PRECISA DE UM CONTROLO POSITIVO. Sem ele, um
    # `retrato()` partido — que devolvesse sempre o mesmo — passava as duas
    # comparacoes de baixo sem medir coisa nenhuma.
    prova("o_retrato_ve_mudanca_quando_ha_mudanca", zero != a,
          "mexeu-se numa fonte e a cadeia correu; se o retrato nao mudou, ele "
          "nao esta a olhar para nada")

    # E AQUI MEDE-SE O CUSTO REAL DO ATRASO, em vez de se supor.
    # A varredura LE mesmo a rodada anterior — isso e estrutural e esta provado
    # pelo laco sobre si propria. Se isso produz ou nao diferenca no CONTEUDO e
    # outra pergunta, e a resposta hoje e NAO: os varredores dependem do
    # CONJUNTO (que ficheiros existem, de que especie), e nao do conteudo que os
    # passos seguintes reescrevem.
    #
    #     «O ATRASO EXISTE» E «O ATRASO CUSTA» SAO DUAS AFIRMACOES.
    #     MEDIR A PRIMEIRA E PUBLICAR A SEGUNDA E O ERRO DE SEMPRE.
    atrasou = sorted(k for k in a if a.get(k) != b.get(k))
    print("  NOTA  ATRASO_COM_EFEITO_OBSERVAVEL = %s%s"
          % ("SIM" if atrasou else "NAO", (" · " + str(atrasou[:3])) if atrasou else ""))
    mudaram = sorted(k for k in b if b.get(k) != c3.get(k))
    prova("SEMANTIC_DRIFT_ON_SECOND_RUN_e_zero", not mudaram, mudaram)
    prova("e_a_segunda_passagem_escreveu_mesmo",
          all((alvo / s["PATH"]).is_file()
              for p in CAD.passos() for s in CAD.saidas(p)
              if not s.get("NAO_MATERIALIZA")),
          "se nao escrevesse nada, a prova de cima era vacua")
finally:
    shutil.rmtree(base, ignore_errors=True)

# ── 10 · O ARNES NAO DEIXOU ESTRAGO ───────────────────────────────────────
prova("o_manifesto_ficou_como_estava",
      MANIFESTO.read_text(encoding="utf-8") == MANIFESTO_COMO_ESTAVA,
      "esta prova muta o manifesto para o atacar; se ele nao voltar ao que era, "
      "o estrago vai para o `git add` de quem correr isto a seguir")

print()
print("=" * 74)
if FALHAS:
    print("ORDEM_POR_DEPENDENCIA=FAIL · %d prova(s) reprovada(s)" % len(FALHAS))
    for f in FALHAS:
        print("  ·", f)
    raise SystemExit(1)
print("ORDEM_POR_DEPENDENCIA=PASS · a ordem sai do grafo, e o ciclo que resta tem nome")
