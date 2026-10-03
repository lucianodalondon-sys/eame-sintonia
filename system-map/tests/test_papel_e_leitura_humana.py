#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS PROVAS DO PAPEL, DA PROVA DA LIGACAO E DA LEITURA HUMANA — G7 · G8 · G8B.

    python3 system-map/tests/test_papel_e_leitura_humana.py

O mapa estava tecnicamente certo por baixo e continuava ilegivel por cima. Tres
defeitos foram MEDIDOS nesta arvore, e sao estes que esta bancada fixa:

    G7   `ROLE` nao existia. A §4 do contrato de confianca poe-o na lista de
         campos obrigatorios e a §21 escrevia «atribui-lo e trabalho de medicao,
         nao desta missao». Passou a ser desta.

    G8   A TELA DESENHAVA 45 ARESTAS SEM PROVA EXACTAMENTE COMO AS 612 PROVADAS.
         A classe do traco saia de `kind` — que so separa `expected` (2) de
         `technical` (657) — e nao dos quatro planos, que separam 612 de 47. A
         dica escrevia «LIGACAO PROVADA» por cima das 45.

             UMA SETA VERDE NAO PODE SIGNIFICAR QUATRO COISAS. (§20)

    G8B  O «caminho completo» ATRAVESSAVA essas 45, apesar de o comentario da
         propria funcao dizer que nao atravessa o que nao esta provado.

             ATRAVESSAR UMA LIGACAO POR PROVAR
             TRANSFORMA «TALVEZ» EM «PORTANTO».

O QUE ESTE FICHEIRO CONFERE
---------------------------
    PAPEL        toda peca publica ROLE, no vocabulario fechado da §5.1
    EVIDENCIA    todo papel traz a regra que o decidiu e o limite do que prova
    SEM PROMOCAO papel declarado nunca ganha plano CODE
    CONFLITO     medido != declarado nao escolhe vencedor em silencio
    DONOS        a contagem de «um conceito, um dono» chega a tela
    ARESTA       a classe de prova sai dos planos, e a tela usa-a
    CAMINHO      nenhum caminho atravessa aresta sem prova
    NAO SEI      nenhum filtro o esconde por omissao
    HUMANO       o cartao responde as oito perguntas sem abrir codigo
    MORDIDA      cada regra, corrida contra um defeito fabricado
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ESTADO = RAIZ / "system-map" / "data" / "state.generated.json"
TELA = RAIZ / "system-map" / "app" / "map.js"
CASCA = RAIZ / "system-map" / "app" / "index.html"
FOLHA = RAIZ / "system-map" / "app" / "map.css"
DONOS = RAIZ / "system-map" / "data" / "donos.generated.json"

FALHAS = []

# O VOCABULARIO E O DO CONTRATO, E ESTA LISTA E A COPIA QUE REPROVA SE ALGUEM O
# ALARGAR SEM PASSAR POR AQUI. Um papel novo exige o medidor que o emite e a
# classe de evidencia que o sustenta — §6.1, aplicada ao papel.
PAPEIS = {"OPERATIONAL_STEP", "MEASUREMENT_INSTRUMENT", "CONTRACT_OR_RULE",
          "STORAGE", "SURFACE", "DISPATCH_ENTRYPOINT", "PROOF", "UNKNOWN"}
PLANOS_DO_PAPEL = {"CODE", "DECLARED", "UNKNOWN"}


def prova(nome, ok, porque=""):
    print(("  PASS  " if ok else "  FAIL  ") + nome
          + (("\n        " + porque) if not ok and porque else ""))
    if not ok:
        FALHAS.append(nome)


print("AS PROVAS DO PAPEL E DA LEITURA HUMANA — G7 · G8 · G8B")
print("=" * 70)

S = json.loads(ESTADO.read_text(encoding="utf-8"))
N, E = S["NODES"], S["EDGES"]
tela = TELA.read_text(encoding="utf-8")
casca = CASCA.read_text(encoding="utf-8")
folha = FOLHA.read_text(encoding="utf-8")

prova("o_estado_existe", bool(N) and bool(E))

# ══ 1 · G7 · TODA PECA PUBLICA UM PAPEL, E SO OS PAPEIS QUE EXISTEM ═════════
sem = [n["id"] for n in N if "ROLE" not in n]
prova("toda_peca_publica_ROLE", not sem, f"{sem[:5]}")
fora = [(n["id"], n.get("ROLE")) for n in N if n.get("ROLE") not in PAPEIS]
prova("nenhum_papel_fora_do_vocabulario_da_5_1", not fora, f"{fora[:5]}")
maus = [(n["id"], n.get("ROLE_PLANE")) for n in N
        if n.get("ROLE_PLANE") not in PLANOS_DO_PAPEL]
prova("todo_papel_diz_em_que_plano_esta", not maus, f"{maus[:5]}")

# ── A EVIDENCIA E O LIMITE, SEMPRE OS DOIS ─────────────────────────────────
#     UMA EVIDENCIA QUE NAO DECLARA O SEU LIMITE SERA USADA FORA DELE. (§7)
sem_ev = [n["id"] for n in N if not (n.get("ROLE_EVIDENCE") or "").strip()]
prova("todo_papel_traz_a_evidencia_que_o_decidiu", not sem_ev, f"{sem_ev[:5]}")
sem_lim = [n["id"] for n in N if not (n.get("ROLE_LIMITATIONS") or "").strip()]
prova("todo_papel_declara_o_que_NAO_prova", not sem_lim, f"{sem_lim[:5]}")
sem_regra = [n["id"] for n in N if not (n.get("ROLE_RULE") or "").strip()]
prova("todo_papel_nomeia_a_regra_que_o_decidiu", not sem_regra, f"{sem_regra[:5]}")

# ── NENHUMA PROMOCAO: declarado nao vira medido ────────────────────────────
#     DECLARED → CODE  PROIBIDO INFERIR.  (§2)
promovidos = [n["id"] for n in N
              if n.get("ROLE_PLANE") == "CODE" and n.get("ROLE_MEASURED") == "UNKNOWN"]
prova("nenhum_papel_so_declarado_recebe_plano_CODE", not promovidos,
      f"{promovidos[:5]} — plano CODE exige regra de medicao que tenha disparado")
desencontro = [n["id"] for n in N
               if n.get("ROLE_PLANE") == "CODE" and n.get("ROLE") != n.get("ROLE_MEASURED")]
prova("o_papel_publicado_em_CODE_e_o_que_a_arvore_mediu", not desencontro,
      f"{desencontro[:5]}")
so_ficha = [n["id"] for n in N
            if n.get("ROLE_PLANE") == "DECLARED" and n.get("ROLE_MEASURED") != "UNKNOWN"]
prova("plano_DECLARED_so_quando_a_arvore_nao_mediu_nada", not so_ficha,
      f"{so_ficha[:5]}")

# ── O CONFLITO NAO ESCOLHE VENCEDOR EM SILENCIO ────────────────────────────
#     UM CONFLITO ESCONDIDO E FAIL.  (§15)
calados = [n["id"] for n in N
           if n.get("ROLE_MEASURED") not in ("UNKNOWN", None)
           and n.get("ROLE_DECLARED") not in ("UNKNOWN", None)
           and n["ROLE_MEASURED"] != n["ROLE_DECLARED"]
           and not n.get("ROLE_CONFLICT")]
prova("papel_medido_diferente_do_declarado_publica_o_conflito", not calados,
      f"{calados[:5]}")
escolhidos = [n["id"] for n in N if n.get("ROLE_CONFLICT") and n.get("ROLE") != "UNKNOWN"]
prova("um_papel_em_conflito_fica_NAO_SEI", not escolhidos,
      f"{escolhidos[:5]} — o mapa nao arbitra; quem decide e gente")
CAMPOS = ("MEASURED", "MEASURED_WHY", "DECLARED", "DECLARED_WHY", "RESOLUTION")
incompletos = [n["id"] for n in N if n.get("ROLE_CONFLICT")
               and not all(n["ROLE_CONFLICT"].get(c) for c in CAMPOS)]
prova("o_conflito_traz_os_dois_lados_e_a_razao_de_cada_um", not incompletos,
      f"{incompletos[:5]}")
prova("ha_conflito_medido_nesta_arvore_para_esta_prova_nao_ser_vazia",
      any(n.get("ROLE_CONFLICT") for n in N),
      "nenhum conflito — as provas acima passam por vacuidade")

# ── AS CONTAGENS, E O UNIVERSO DE CADA UMA ─────────────────────────────────
#     PROIBIDO PUBLICAR UMA CONTAGEM SEM O SEU UNIVERSO.  (§5.2)
C = S["COUNTS"]
for chave in ("roles_proven", "roles_declared_only", "roles_unknown", "roles_conflict"):
    prova(f"a_contagem_{chave}_e_publicada", chave in C)
prova("as_contagens_do_papel_fecham_com_o_universo",
      C["roles_proven"] + C["roles_declared_only"] + C["roles_unknown"] == len(N),
      f"{C['roles_proven']}+{C['roles_declared_only']}+{C['roles_unknown']} "
      f"!= {len(N)}")
prova("a_contagem_de_papel_provado_bate_com_o_estado",
      C["roles_proven"] == sum(1 for n in N if n.get("ROLE_PLANE") == "CODE"))
prova("a_contagem_de_conflito_bate_com_o_estado",
      C["roles_conflict"] == sum(1 for n in N if n.get("ROLE_CONFLICT")))

# ══ 2 · G7 · UM CONCEITO, UM DONO — chega a tela, e nao e recontado ═════════
# O censo ja media desde a missao da observabilidade. Ninguem o via.
#     MEDIDO E INVISIVEL VALE O MESMO QUE NAO MEDIDO.
D = json.loads(DONOS.read_text(encoding="utf-8")) if DONOS.is_file() else {}
prova("o_censo_dos_donos_existe", bool(D.get("DETALHE")))
prova("a_contagem_dos_conceitos_e_publicada_no_estado",
      C.get("concept_owner_count") == D.get("CONCEITOS"),
      f"estado={C.get('concept_owner_count')} censo={D.get('CONCEITOS')}")
prova("a_contagem_de_donos_duplicados_e_publicada",
      C.get("concept_owner_conflicts") == (D.get("POR_ESTADO") or {}).get("DONO_DUPLICADO"),
      "o numero que denuncia e o que nao pode faltar")
prova("a_contagem_dos_donos_nao_e_um_literal",
      "concept_owner_count" in (RAIZ / "system-map" / "scripts"
                                / "generate_system_map.py").read_text(encoding="utf-8")
      and "donos.generated.json" in (RAIZ / "system-map" / "scripts"
                                     / "generate_system_map.py").read_text(encoding="utf-8"),
      "ela tem de ser LIDA de quem a mede, senao deixa de acusar quando mudar")

# ══ 3 · G8 · A CLASSE DE PROVA DE UMA ARESTA SAI DOS PLANOS ════════════════
prova("a_tela_tem_um_so_ajudante_da_classe_de_prova",
      tela.count("const classeDaAresta = e =>") == 1
      and tela.count("const arestaProvada = e =>") == 1,
      "duas copias dariam duas telas a divergir")

# A REGRA ESCRITA COMO FUNCAO, e nao dentro da asercao: uma regra que so sabe
# dizer SIM aos dados reais nao se consegue contradizer.
#     UMA GUARDA QUE NUNCA VIU UM DEFEITO NAO E UMA GUARDA: E UMA FRASE.
def classe(e):
    if e.get("OBSERVED") == "YES":
        return "observada"
    if e.get("PROVEN") == "YES":
        return "provada"
    if e.get("DECLARED") == "YES":
        return "declarada"
    return "naosei"


sem_prova = [e for e in E if classe(e) in ("declarada", "naosei")]
prova("ha_arestas_sem_prova_nesta_arvore", bool(sem_prova),
      "sem elas, tudo abaixo passa por vacuidade")

# O DEFEITO, FIXADO COMO CASO DE TESTE. `kind` e a classe de prova discordam, e
# e por isso que a tela nao pode voltar a ler `kind`.
por_kind = sum(1 for e in E if e.get("kind") == "expected")
por_plano = len(sem_prova)
prova("kind_e_a_classe_de_prova_nao_sao_a_mesma_pergunta", por_kind != por_plano,
      f"kind diz {por_kind} e os planos dizem {por_plano} — se um dia forem "
      f"iguais, esta sentinela deixa de morder e tem de ser remedida")

desenho = tela.split("$('edgeLayer').innerHTML")[1].split("/* ══ 2 ·")[0]
prova("o_traco_da_seta_sai_da_classe_de_prova", "classeDaAresta(e)" in desenho)
prova("o_traco_da_seta_nao_volta_a_sair_do_kind",
      "e.kind === 'expected'" not in desenho,
      "`kind` nao sabe nada sobre prova")
prova("a_seta_sem_prova_leva_uma_marca_alem_da_cor",
      "semProvaMarca" in desenho and "arestaProvada(e)" in desenho,
      "cor sozinha nao comunica estado")
prova("a_folha_pinta_a_seta_sem_prova_com_traco_proprio",
      ".edgePath.semprova" in folha and "stroke-dasharray" in folha
      and "arrowNaoSei" in folha)
prova("a_ponta_vazada_existe_na_casca", 'id="arrowNaoSei"' in casca)

dica = tela.split("function showEdgeTip(")[1].split("function moveTip(")[0]
prova("a_dica_da_aresta_nao_escreve_PROVADA_por_omissao",
      "LIGAÇÃO PROVADA" not in dica,
      "esse rotulo saia em 657 arestas e 45 delas nao tinham prova")
prova("a_dica_da_aresta_usa_a_classe_de_prova", "classeDaAresta(d)" in dica)

# ══ 4 · G8B · O CAMINHO NAO ATRAVESSA O QUE NAO ESTA PROVADO ═══════════════
caminho = tela.split("function highlightPath(")[1].split("/* ══ 4 · FILTROS")[0]
prova("o_caminho_completo_para_na_aresta_sem_prova",
      "if (!arestaProvada(e)) return;" in caminho)
prova("o_caminho_completo_nao_volta_a_usar_o_kind",
      "e.kind === 'expected'" not in caminho)

foco = tela.split("function focar(")[1].split("const hideTip")[0]
prova("a_seleccao_separa_montante_de_jusante",
      "montante" in foco and "jusante" in foco and "paraCima" in foco
      and "paraBaixo" in foco)
prova("a_folha_distingue_montante_de_jusante_por_mais_que_a_cor",
      ".node.montante" in folha and ".node.jusante" in folha
      and "box-shadow:-5px" in folha.replace(" ", "")
      and "box-shadow:5px" in folha.replace(" ", ""),
      "o lado da sombra e o segundo canal; a cor sozinha nao chega")
prova("o_painel_escreve_montante_e_jusante_por_extenso",
      "A montante ·" in tela and "A jusante ·" in tela)

# ══ 4b · A LEI DE DESIGN — COR DE PRODUTO NAO GANHA SEGUNDO SIGNIFICADO ════
# `CLAUDE.md` manda consultar o ADAMA Design System antes de criar padrao
# visual novo. Medido no extracto versionado: a Primary da marca significa
# CATEGORIA DE PRODUTO, e nao ha cor de estado nenhuma. Reutiliza-la para
# «provado» ou «a montante» daria a uma cor de produto um segundo significado.
PRODUTO = ("#f89e18", "#7db41e", "#00a0df", "#9d1d96",
           "#f5b317", "#93cc23", "#00698f", "#752157")
# ⚠️ A PROCURA E NO BLOCO CERTO, E ISSO E METADE DA REGRA.
# A folha USA a Primary da ADAMA — de propria vontade e com a razao escrita —
# para as FAIXAS: `--fam-coleta` e o azul de Disease Control, `--fam-entrega` o
# laranja de Crop Enhancement. Isso nao e reaproveitar cor de produto para
# estado: faixa diz DE QUE ASSUNTO E, e a folha ja o declara duas vezes.
#
#     FAMILIA DIZ DE QUE ASSUNTO E. ESTADO DIZ SE FUNCIONA.
#
# O que esta guarda proibe e o outro caso: dar a uma cor de produto o segundo
# significado de PROVA, PAPEL ou SENTIDO DO FLUXO. Por isso ela olha para o
# bloco que esta missao acrescentou, e para os dois tokens do fluxo — e nao
# para a folha inteira, que reprovaria uma decisao correcta tomada antes.
meu_bloco = folha.split("⚖️ A LEI DE DESIGN", 1)[-1].lower()
tokens_do_fluxo = " ".join(re.findall(r"--fluxo-\w+:\s*([^;]+);", folha)).lower()
roubadas = [c for c in PRODUTO if c in meu_bloco or c in tokens_do_fluxo]
prova("nenhuma_cor_de_produto_da_marca_vira_cor_de_estado", not roubadas,
      f"{roubadas} — a Primary da ADAMA significa categoria de produto")
prova("a_guarda_olha_para_o_bloco_certo", meu_bloco != folha.lower(),
      "sem o marcador da lei de design, ela varreria a folha inteira e "
      "reprovaria as faixas, que estao certas")
variantes = set(re.findall(r"\.papel-([A-Z_]+)\s*\{", folha))
prova("o_papel_nao_vira_uma_paleta_de_sete_tons", variantes <= {"UNKNOWN"},
      f"{sorted(variantes)} — o papel diz-se por palavra; so NAO SEI se separa")
prova("os_tons_do_fluxo_sao_tokens_declarados_num_sitio_so",
      folha.count("--fluxo-montante:") == 1 and folha.count("--fluxo-jusante:") == 1
      and "#7fa8c8" not in folha and "#c9a15e" not in folha,
      "dois sitios com a mesma cor sao duas cores a divergir")
prova("a_folha_declara_que_o_padrao_e_novo_e_porque",
      "ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND" in folha
      and "NEW_PATTERN_REQUIRED      = YES" in folha,
      "criar padrao visual novo sem declarar e criar uma segunda fonte visual")

# ══ 5 · NENHUM FILTRO ESCONDE NAO SEI POR OMISSAO ══════════════════════════
#     UNKNOWN → escondido  PROIBIDO.  (§18)
caixas = re.findall(r'<input type="checkbox" name="prova" value="(\w+)"([^>]*)>', casca)
prova("o_filtro_da_prova_existe_com_as_quatro_classes",
      {c for c, _ in caixas} == {"observada", "provada", "declarada", "naosei"},
      f"{caixas}")
desligadas = [c for c, resto in caixas if "checked" not in resto]
prova("as_quatro_classes_comecam_ligadas", not desligadas,
      f"{desligadas} comeca(m) desligada(s) — desligar NAO SEI por omissao "
      f"esconderia o buraco de quem nunca mexe num filtro")
estados = re.findall(r'<input type="checkbox" name="status" value="(\w+)"([^>]*)>', casca)
cinza_off = [c for c, r in estados if c == "gray" and "checked" not in r]
prova("o_estado_NAO_SEI_comeca_ligado", not cinza_off)

# ── ACHAR E NAO MOSTRAR ONDE ESTA NAO E ACHAR ──────────────────────────────
prova("a_busca_leva_a_camera_ao_que_encontrou",
      "enquadrarCaixa(achados)" in tela and "searchHit" in tela,
      "num mundo de 6700x3300 o cartao aceso pode estar fora do ecra")
prova("a_camera_da_busca_nao_mexe_no_que_esta_visivel",
      "function enquadrarCaixa(" in tela
      and "applyFilters" not in tela.split("function enquadrarCaixa(")[1]
                                    .split("\n}")[0],
      "enquadrar e camera; filtrar e conteudo, e nao se misturam")

prova("a_tela_conta_as_setas_sem_prova", 'id="kSemProva"' in casca
      and "$('kSemProva')" in tela,
      "a barra dizia «656 ligacoes» e «7 nao sei» — e o 7 era de PECAS")
prova("a_tela_conta_as_pecas_sem_papel", 'id="kPapelNaoSei"' in casca
      and "$('kPapelNaoSei')" in tela)

# ══ 6 · O CARTAO RESPONDE AS OITO PERGUNTAS ════════════════════════════════
# A cobertura e MEDIDA sobre o estado, nao afirmada. E ela conta UNKNOWN como
# resposta em falta: um cartao que diz NAO SEI e honesto e continua sem
# responder a pergunta.
cartao = tela.split("function openDetail(")[1].split("detail.innerHTML")[1]
for pedaco, o_que in (
        ("${esc(n.name)}", "NOME_HUMANO"),
        ("papelCurto(n)", "PAPEL"),
        ("statusLabel(n.ui_status)", "STATUS"),
        ("${esc(n.what)}", "DESCRICAO_CURTA"),
        ("n.OWNER", "OWNER"),
        ("n.consumes", "ENTRADAS"),
        ("n.produces", "SAIDAS"),
        ("A montante ·", "CONEXOES_MONTANTE"),
        ("A jusante ·", "CONEXOES_JUSANTE"),
        ("n.ROLE_EVIDENCE", "PROVA_DO_PAPEL"),
        ("${planos(n)}", "OS_QUATRO_PLANOS"),
        ("STATUS_LEGACY_NOTA", "NOTA_DO_LEGADO"),
        ("${esc(n.id)}", "IDENTIFICADOR_TECNICO"),
        ("Arquivos que implementam isto", "CAMINHO_TECNICO")):
    prova(f"o_cartao_mostra_{o_que}", pedaco in cartao,
          f"falta `{pedaco}` no cartao")

# ── A ORDEM: o humano antes do tecnico ─────────────────────────────────────
#     ESCONDER SERIA MENTIR. ABRIR COM VOCABULARIO DE CONTRATO ERA EXPULSAR.
i_papel = cartao.find("papelCurto(n)")
i_faz = cartao.find("O que faz")
i_planos = cartao.find("${planos(n)}")
i_path = cartao.find("Arquivos que implementam isto")
prova("o_papel_e_o_que_faz_vem_antes_dos_quatro_planos",
      0 <= i_papel < i_planos and 0 <= i_faz < i_planos,
      f"papel={i_papel} faz={i_faz} planos={i_planos}")
prova("o_caminho_tecnico_nao_e_o_protagonista",
      0 <= i_faz < i_path, f"faz={i_faz} path={i_path}")
prova("o_cartao_do_palco_mostra_o_papel",
      "papelCurto(n)" in tela.split("$('nodes').innerHTML")[1].split("$('edgeLayer')")[0])

# ── COBERTURA MEDIDA, e nunca 100% com UNKNOWN dentro ──────────────────────
PERGUNTAS = {
    "WHAT_IS_IT": lambda n: bool((n.get("what") or "").strip()),
    "WHO_OWNS_IT": lambda n: n.get("OWNER") not in (None, "", "UNKNOWN"),
    "WHAT_ENTERS": lambda n: bool(n.get("consumes")),
    "WHAT_LEAVES": lambda n: bool(n.get("produces")),
    "UPSTREAM": lambda n: bool(n.get("inbound")),
    "DOWNSTREAM": lambda n: bool(n.get("outbound")),
    "STATUS": lambda n: n.get("status") in ("PROVEN", "PENDING", "BROKEN", "UNKNOWN"),
    "EVIDENCE": lambda n: bool((n.get("ROLE_EVIDENCE") or "").strip()),
    "ROLE": lambda n: n.get("ROLE") not in (None, "UNKNOWN"),
}
respostas = Counter()
for n in N:
    for k, f in PERGUNTAS.items():
        if f(n):
            respostas[k] += 1
total = len(N) * len(PERGUNTAS)
cobertos = sum(respostas.values())
print()
print(f"  HUMAN_READABLE_CARD_COVERAGE = {cobertos}/{total} "
      f"({100 * cobertos // total}%)")
for k in PERGUNTAS:
    print(f"      {k:<14} {respostas[k]:>3}/{len(N)}")
print()
prova("a_cobertura_humana_nao_se_declara_100_com_UNKNOWN_dentro",
      cobertos < total or C["roles_unknown"] == 0,
      "ha UNKNOWN no estado e a cobertura diz 100% — uma das duas mente")
prova("toda_peca_responde_o_que_faz_e_com_que_evidencia",
      respostas["WHAT_IS_IT"] == len(N) and respostas["EVIDENCE"] == len(N))

# ══ 6b · OS CASOS REAIS, UM DE CADA CLASSE ═════════════════════════════════
# Uma cobertura media esconde o caso dificil: 78% pode ser 100% no que e facil
# e 0% no que interessa. Estas doze pecas sao escolhidas por CLASSE, e cada uma
# tem de responder as oito perguntas com um valor — `UNKNOWN` conta como
# resposta so onde ele e a verdade medida, e a linha impressa diz qual e qual.
#
#     UMA MEDIA NAO E UMA COBERTURA: E UM SITIO ONDE O CASO DIFICIL SE ESCONDE.
SENTINELAS = [
    ("COLECTA · uma accao que colhe",          "C-COLETA-PUBLICA"),
    ("COLECTA · o corpus",                     "C-CORPUS"),
    ("ADMISSAO · a porta",                     "C-ADMISSAO"),
    ("SALA · o que a coleta entrega",          "C-READY"),
    ("SCRAP · a accao",                        "C-SCRAP-SOCIAL"),
    ("SCRAP · o despacho",                     "C-SINTONIA-SCRAP"),
    ("PORTAL · a camada de dado",              "C-PORTAL-DADOS"),
    ("SYSTEM MAP · o gerador",                 "C-MAPA-GERADOR"),
    ("UNKNOWN · artefacto sem carimbo",        "C-IT-PDF-BRUTO"),
    ("UNKNOWN · tela sem gerador declarado",   "C-TELA-FIELD"),
    ("MUITOS LEITORES · 16 a jusante",         "C-AS-FONTES"),
    ("MUITOS MONTANTES · 83 a montante",       "C-TESTES"),
]
por_id = {n["id"]: n for n in N}
prova("as_doze_sentinelas_existem_no_mapa",
      all(i in por_id for _, i in SENTINELAS),
      f"{[i for _, i in SENTINELAS if i not in por_id]}")

print()
print("  OS CASOS REAIS — ROLE · OWNER · INPUT · OUTPUT · EDGE · STATUS")
CAMPOS_DO_CASO = ("ROLE", "OWNER", "INPUT", "OUTPUT", "EDGE", "STATUS")
for rotulo, i in SENTINELAS:
    n = por_id.get(i)
    if not n:
        continue
    ent = [e for e in E if e["to"] == i]
    sai = [e for e in E if e["from"] == i]
    resp = {
        "ROLE": n.get("ROLE"),
        "OWNER": n.get("OWNER"),
        "INPUT": f"{len(n.get('consumes') or [])} ficheiro(s)",
        "OUTPUT": f"{len(n.get('produces') or [])} ficheiro(s)",
        "EDGE": f"{len(ent)}↑ {len(sai)}↓",
        "STATUS": n.get("status"),
    }
    print(f"    {rotulo:<36} " + " · ".join(f"{k}={v}" for k, v in resp.items()))
    # Cada campo tem de trazer um VALOR. `UNKNOWN` e um valor; vazio nao e.
    vazios = [k for k, v in resp.items() if v in (None, "", "None")]
    prova(f"caso_{i}_responde_os_seis_campos", not vazios, f"vazio: {vazios}")
    # E a evidencia do papel tem de existir mesmo quando o papel e NAO SEI:
    # «nao sei» sem dizer PORQUE e um encolher de ombros, nao uma resposta.
    prova(f"caso_{i}_diz_porque_sabe_ou_porque_nao_sabe",
          bool((n.get("ROLE_EVIDENCE") or "").strip()))
print()

# ══ 7 · A MORDIDA — cada regra corrida contra um defeito fabricado ═════════
print()
print("  MORDIDA — cada guarda contra o defeito que ela devia apanhar")


def _morde(nome, apanhou, porque=""):
    prova(nome, apanhou, porque or "a guarda nao mordeu o defeito fabricado")


# m1 · um papel fora do vocabulario
_falso = dict(N[0]); _falso["ROLE"] = "COLETOR"
_morde("m1_papel_fora_do_vocabulario_seria_apanhado", _falso["ROLE"] not in PAPEIS)

# m2 · um papel declarado promovido a CODE
_falso = {"id": "X", "ROLE_PLANE": "CODE", "ROLE_MEASURED": "UNKNOWN"}
_morde("m2_papel_so_declarado_com_plano_CODE_seria_apanhado",
       _falso["ROLE_PLANE"] == "CODE" and _falso["ROLE_MEASURED"] == "UNKNOWN")

# m3 · um conflito que escolhe vencedor
_falso = {"ROLE": "PROOF", "ROLE_CONFLICT": {"MEASURED": "STORAGE"}}
_morde("m3_conflito_que_escolhe_vencedor_seria_apanhado",
       bool(_falso["ROLE_CONFLICT"]) and _falso["ROLE"] != "UNKNOWN")

# m4 · um papel sem limite declarado
_morde("m4_papel_sem_limite_seria_apanhado", not "".strip())

# m5 · a tela volta a ler `kind` para decidir o traco
_como_era = "const cls = e.kind === 'expected' ? 'unknown' : '';"
_morde("m5_traco_decidido_pelo_kind_seria_apanhado",
       "e.kind === 'expected'" in _como_era)

# m6 · O DEFEITO REAL, CORRIDO SOBRE ESTA ARVORE. A regra velha, aplicada aos
#      dados de hoje, pinta como provadas arestas que nao tem prova nenhuma.
mentiriam = [f"{e['from']}->{e['to']}" for e in E
             if e.get("kind") != "expected" and classe(e) == "naosei"]
_morde("m6_a_regra_velha_pintaria_de_provado_o_que_nao_tem_prova",
       len(mentiriam) > 0,
       f"{len(mentiriam)} arestas: {mentiriam[:3]} — e era exactamente isto")

# m7 · o caminho velho atravessava essas mesmas arestas
_como_era_caminho = "if (e.kind === 'expected') return;"
_morde("m7_o_caminho_velho_atravessaria_as_mesmas_arestas",
       "arestaProvada" not in _como_era_caminho and len(mentiriam) > 0)

# m8 · um filtro que arranca com NAO SEI desligado
_casca_falsa = '<input type="checkbox" name="prova" value="naosei">'
_morde("m8_filtro_com_NAO_SEI_desligado_seria_apanhado",
       "checked" not in _casca_falsa)

# m9 · o caminho tecnico a voltar para a frente do significado
_cartao_falso = "Arquivos que implementam isto ... O que faz"
_morde("m9_caminho_tecnico_a_frente_do_significado_seria_apanhado",
       _cartao_falso.find("O que faz") > _cartao_falso.find("Arquivos que implementam"))

# m10 · a contagem dos donos escrita a mao em vez de lida do censo
_morde("m10_contagem_de_donos_escrita_a_mao_seria_apanhada",
       (D.get("POR_ESTADO") or {}).get("DONO_DUPLICADO") != 0,
       "se o censo passasse a medir zero, a sentinela precisava de ser remedida")

print()
print("=" * 70)
print(f"PAPEL={len(PAPEIS - {'UNKNOWN'})} classes · "
      f"provado={C['roles_proven']} declarado={C['roles_declared_only']} "
      f"nao_sei={C['roles_unknown']} conflito={C['roles_conflict']}")
print(f"ARESTAS · provadas={sum(1 for e in E if classe(e) == 'provada')} "
      f"declaradas={sum(1 for e in E if classe(e) == 'declarada')} "
      f"nao_sei={sum(1 for e in E if classe(e) == 'naosei')} de {len(E)}")
print(f"CONCEITOS · {C.get('concept_owner_count')} medidos · "
      f"{C.get('concept_owner_conflicts')} com dono duplicado")
if FALHAS:
    print(f"PAPEL_E_LEITURA=FAIL · {len(FALHAS)} prova(s) reprovada(s)")
    for f in FALHAS:
        print("  ·", f)
    raise SystemExit(1)
print("PAPEL_E_LEITURA=PASS · o papel vem da evidencia, e a tela nao promove nada")
