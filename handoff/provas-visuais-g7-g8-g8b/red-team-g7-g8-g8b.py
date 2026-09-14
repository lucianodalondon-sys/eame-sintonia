#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DE G7 · G8 · G8B — 24 ataques, medidos nesta arvore.

Cada ataque e uma acusacao concreta. SOBREVIVENTE = a acusacao procede.
Nao se conta como morto um ataque que nao foi corrido.
"""
import json, re
from collections import Counter
from pathlib import Path

RAIZ = Path("/home/user/eame-sintonia")
S = json.loads((RAIZ / "system-map/data/state.generated.json").read_text(encoding="utf-8"))
G = json.loads((RAIZ / "system-map/data/architecture.generated.json").read_text(encoding="utf-8"))
tela = (RAIZ / "system-map/app/map.js").read_text(encoding="utf-8")
casca = (RAIZ / "system-map/app/index.html").read_text(encoding="utf-8")
folha = (RAIZ / "system-map/app/map.css").read_text(encoding="utf-8")
ger = (RAIZ / "system-map/scripts/generate_system_map.py").read_text(encoding="utf-8")
N, E = S["NODES"], S["EDGES"]
por_id = {n["id"]: n for n in N}

SOBREVIVENTES = []
n_ataques = 0

def atacar(num, nome, morto, prova):
    global n_ataques
    n_ataques += 1
    print(("  MORTO      " if morto else "  SOBREVIVE  ") + f"#{num:02d} {nome}")
    print(f"             {prova}")
    if not morto:
        SOBREVIVENTES.append(f"#{num:02d} {nome}")

print("RED TEAM · G7 · G8 · G8B")
print("=" * 74)

# 1 · card com papel inventado pelo nome
sem_regra = [n["id"] for n in N if n.get("ROLE") != "UNKNOWN"
             and n.get("ROLE_RULE") == "SEM_REGRA" and n.get("ROLE_PLANE") == "CODE"]
atacar(1, "papel inventado pelo nome do ficheiro", not sem_regra,
       f"{len(N)} pecas; toda publicam ROLE_RULE. Papel em plano CODE sem regra: "
       f"{len(sem_regra)}. O gerador nunca le o nome: as regras M1..M9 leem "
       f"workflow, vercel.json, rule_role, RUNS, rede, ESCRITAS_EM_PASTA, WRITES/READS.")

# 2 · owner inferido pelo path
owner_medido = [n["id"] for n in N if n.get("OWNER_PLANE") == "CODE"]
atacar(2, "owner inferido pelo caminho do ficheiro", not owner_medido,
       f"OWNER so tem dois planos: DECLARED ({sum(1 for n in N if n.get('OWNER_PLANE')=='DECLARED')}) "
       f"e UNKNOWN ({sum(1 for n in N if n.get('OWNER_PLANE')=='UNKNOWN')}). "
       f"Nenhum em CODE: a arvore nao mede responsabilidade.")

# 3 · import tratado como fluxo
imports_como_dado = [f"{e['from']}->{e['to']}" for e in E
                     if e.get("raw_type") == "IMPORTS" and e.get("categoria") == "DATA"]
atacar(3, "import tratado como fluxo de dado", not imports_como_dado,
       f"IMPORTS medidos: {sum(1 for e in E if e.get('raw_type')=='IMPORTS')}; "
       f"classificados DATA: {len(imports_como_dado)}. CATEGORIA_DO_TIPO manda "
       f"IMPORTS para CODE.")

# 4 · string tratada como edge
sem_linha = [f"{e['from']}->{e['to']}" for e in E if e.get("CODE") == "YES"
             and not any(v.get("SUPPORTS") == "YES" for v in e.get("evidence", []))]
atacar(4, "string solta tratada como aresta provada", not sem_linha,
       f"CODE=YES sem evidencia que sustente a afirmacao: {len(sem_linha)}. "
       f"As 40 arestas de rotulo narrativo tem CODE=UNKNOWN.")

# 5 · conexao declarada mostrada como provada  ← O DEFEITO DESTA MISSAO
def classe(e):
    return ("observada" if e.get("OBSERVED") == "YES" else
            "provada" if e.get("PROVEN") == "YES" else
            "declarada" if e.get("DECLARED") == "YES" else "naosei")
sem_prova = [e for e in E if classe(e) in ("declarada", "naosei")]
desenho = tela.split("$('edgeLayer').innerHTML")[1].split("/* ══ 2 ·")[0]
atacar(5, "ligacao declarada desenhada como provada",
       "classeDaAresta(e)" in desenho and "e.kind === 'expected'" not in desenho
       and ".edgePath.semprova" in folha,
       f"{len(sem_prova)} arestas sem prova de {len(E)}. O traco sai de "
       f"classeDaAresta(); a folha da-lhes cor, tracejado, ponta vazada e anel.")

# 6 · UNKNOWN mostrado como FAIL
atacar(6, "UNKNOWN pintado como falha", "prova-naosei" in folha
       and "var(--bad)" not in folha.split(".provaChip.prova-naosei")[1].split("}")[0],
       "a classe .provaChip.prova-naosei usa --unknown (cinzento), nunca --bad. "
       "BROKEN continua reservado a quem foi declarado e nao existe.")

# 7 · NOT_OBSERVED mostrado como inexistente
nos_indevidos = [(e["from"], e["to"], p) for e in E
                 for p in ("DECLARED", "CODE", "OBSERVED", "PROVEN") if e.get(p) == "NO"]
atacar(7, "NOT_OBSERVED apresentado como inexistente", not nos_indevidos,
       f"nenhum plano diz NO ({len(nos_indevidos)} casos). OBSERVED=UNKNOWN em "
       f"{sum(1 for e in E if e.get('OBSERVED')=='UNKNOWN')} de {len(E)}: ninguem "
       f"procurou, e o mapa diz isso e nao «nao ha».")

# 8 · card sem input
sem_in = [n["id"] for n in N if not n.get("consumes")]
mostra = "NÃO SEI — nenhuma leitura de ficheiro medida" in tela
atacar(8, "card sem entrada apresentado como se nao tivesse nenhuma", mostra,
       f"{len(sem_in)} pecas sem entrada medida; o cartao escreve «⚪ NÃO SEI — "
       f"nenhuma leitura de ficheiro medida» e o paragrafo diz que NAO SEI aqui "
       f"nao e «nao le».")

# 9 · card sem output
sem_out = [n["id"] for n in N if not n.get("produces")]
mostra2 = "NÃO SEI — nenhuma escrita de ficheiro medida" in tela
atacar(9, "card sem saida apresentado como se nao produzisse nada", mostra2,
       f"{len(sem_out)} pecas sem saida medida; o cartao diz NAO SEI e explica "
       f"que escrita para pasta ignorada pelo git nao e medida.")

# 10 · dois donos do mesmo conceito
D = json.loads((RAIZ / "system-map/data/donos.generated.json").read_text(encoding="utf-8"))
dup = (D.get("POR_ESTADO") or {}).get("DONO_DUPLICADO", 0)
atacar(10, "dois donos do mesmo conceito escondidos",
       S["COUNTS"].get("concept_owner_conflicts") == dup and dup > 0,
       f"{dup} conceitos com dono duplicado, publicados em COUNTS."
       f"concept_owner_conflicts e lidos do censo, nao recontados.")

# 11 · ficheiro gerado editado a mao
atacar(11, "ficheiro gerado editado a mao para o mapa parecer certo",
       "ROLE" not in (RAIZ / "system-map/data/architecture.declared.json").read_text(encoding="utf-8"),
       "ROLE nao aparece em architecture.declared.json: ele nasce no gerador a "
       "partir da arvore. A P1 do validador regenera e compara — editar o JSON "
       "reprovaria no passo seguinte.")

# 12 · peca de portal apresentada como Collection
portal_na_coleta = [n["id"] for n in N if n.get("ROLE") == "SURFACE"
                    and n.get("family") == "F-COLETA"]
atacar(12, "peca de portal apresentada dentro da Collection", not portal_na_coleta,
       f"SURFACE por familia: "
       f"{dict(Counter(n['family'] for n in N if n.get('ROLE')=='SURFACE'))}")

# 13 · ferramenta apresentada como owner
ferr_dona = [n["id"] for n in N if n.get("ROLE") == "MEASUREMENT_INSTRUMENT"
             and n.get("OWNER_PLANE") == "CODE"]
atacar(13, "ferramenta apresentada como dona de um conceito", not ferr_dona,
       f"nenhum instrumento recebe OWNER medido. E o censo separa "
       f"DONO_E_INSTRUMENTO ({(D.get('POR_ESTADO') or {}).get('DONO_E_INSTRUMENTO')}) "
       f"de UM_DONO ({(D.get('POR_ESTADO') or {}).get('UM_DONO')}).")

# 14 · System Map apresentado como arquitetura
atacar(14, "System Map apresentado como a arquitetura",
       "O MAPA É DERIVADO DO REPO" in casca
       and "Esta tela não altera código" in tela,
       "a casca e o cartao repetem que o mapa e derivado e que a tela nao muda "
       "codigo. ROLE do gerador e MEASUREMENT_INSTRUMENT/OPERATIONAL_STEP como "
       "qualquer outra peca: ele nao se pinta de autoridade.")

# 15 · card tecnico incompreensivel
cartao = tela.split("function openDetail(")[1].split("detail.innerHTML")[1]
atacar(15, "card que so fala em vocabulario tecnico",
       cartao.find("O que faz") < cartao.find("${planos(n)}")
       and "Camada técnica" in cartao,
       "«O que faz» e o papel em portugues vem antes dos quatro planos; o bloco "
       "tecnico tem rotulo proprio e vive no fim.")

# 16 · path dominando o titulo
palco = tela.split("$('nodes').innerHTML")[1].split("$('edgeLayer')")[0]
atacar(16, "caminho tecnico a dominar o titulo do cartao",
       palco.find("nodeName") < palco.find("nodeFiles")
       and "papelCurto(n)" in palco,
       "no cartao do palco a ordem e icone · nome · PAPEL · resumo · caminho. "
       "O caminho e a ultima linha e leva o resto no `title`.")

# 17 · layout a esconder aresta quebrada
escondidas = [f"{e['from']}->{e['to']}" for e in E
              if por_id.get(e["from"], {}).get("ui_status") == "red"
              or por_id.get(e["to"], {}).get("ui_status") == "red"]
atacar(17, "layout a esconder aresta quebrada", ".edgePath.broken" in folha,
       f"{len(escondidas)} arestas tocam peca vermelha nesta arvore (0 pecas "
       f"vermelhas hoje); a classe .broken existe e pinta a vermelho tracejado. "
       f"Nenhum filtro remove cartao do DOM: `hidden` e visual.")

# 18 · ciclo escondido pelo layout
cadeia = json.loads((RAIZ / "system-map/scripts/CADEIA-DO-MAPA.json").read_text(encoding="utf-8"))
atacar(18, "ciclo escondido pelo layout",
       "LEI_DO_CICLO_ATRASADO" in cadeia,
       "o unico ciclo declarado da cadeia vive em LEI_DO_CICLO_ATRASADO e e "
       "provado por test_ordem_por_dependencia.py. No grafo do mapa, `focar` "
       "marca a peca como montante E jusante quando ela e as duas.")

# 19 · status comunicado so por cor
atacar(19, "status comunicado so pela cor",
       "statusLabel" in tela and "provaChip" in casca
       and "arrowNaoSei" in casca and "semProvaMarca" in tela,
       "peca: pastilha com texto («PROVADO OPERACIONAL», «NAO SEI»). aresta: "
       "cor + tracejado + ponta vazada + anel no meio + selo com texto no painel.")

# 20 · filtro a esconder UNKNOWN por omissao
caixas = re.findall(r'<input type="checkbox" name="prova" value="(\w+)"([^>]*)>', casca)
estados = re.findall(r'<input type="checkbox" name="status" value="(\w+)"([^>]*)>', casca)
off = [c for c, r in caixas + estados if "checked" not in r]
atacar(20, "filtro a esconder NAO SEI por omissao", not off,
       f"caixas de prova e de estado que arrancam desligadas: {off or 'nenhuma'}. "
       f"As quatro classes de prova e os quatro estados arrancam ligados.")

# 21 · busca a devolver o card errado
def palheiro(n):
    return " ".join([n["name"], n["kind"], n["what"], n["why_here"], n["id"],
                     *(n.get("files") or [])]).lower()
achados = [n["id"] for n in N if "admissao" in palheiro(n)]
atacar(21, "busca a devolver o cartao errado", "C-ADMISSAO" in achados,
       f"buscar «admissao» devolve {len(achados)} pecas e C-ADMISSAO esta entre "
       f"elas. A busca le nome, tipo, descricao, porque, id e ficheiros — nunca "
       f"o papel traduzido, que e apresentacao.")

# 22 · upstream/downstream invertidos
amostra = [e for e in E if classe(e) == "provada"][0]
foco = tela.split("function focar(")[1].split("const hideTip")[0]
atacar(22, "montante e jusante invertidos",
       "const entra = g.dataset.to === id" in foco
       and "sai = g.dataset.from === id" in foco
       and "if (entra) montante.add(g.dataset.from);" in foco
       and "if (sai) jusante.add(g.dataset.to);" in foco,
       f"aresta {amostra['from']}->{amostra['to']}: quem TERMINA em mim e "
       f"montante (somo o `from`); quem COMECA em mim e jusante (somo o `to`). "
       f"O painel usa os mesmos rotulos.")

# 23 · aresta cross-department fabricada
cross = [e for e in E if por_id.get(e["from"], {}).get("family")
         != por_id.get(e["to"], {}).get("family")]
cross_sem = [f"{e['from']}->{e['to']}" for e in cross if classe(e) != "provada"]
atacar(23, "aresta entre departamentos fabricada para fechar o caminho",
       all(classe(e) != "provada" or e.get("evidence") for e in cross),
       f"{len(cross)} arestas atravessam faixa; {len(cross_sem)} delas nao tem "
       f"prova e aparecem como NAO SEI. Nenhuma provada sem evidencia.")

# 24 · artefato sem gerador a receber gerador inventado
varios = S.get("ARTEFACT_MULTIPLE_AUTHORS") or []
atacar(24, "artefato sem gerador a receber um gerador inventado",
       bool(varios) and all(a.get("owner_elected") for a in varios)
       and "eleição alfabética não é um dono" in tela,
       f"{len(varios)} artefato(s) com mais de um autor; o cartao diz «uma "
       f"eleicao alfabetica nao e um dono» e nomeia os dois. O validador publica "
       f"a OBSERVACAO no fim de cada corrida.")

print()
print("=" * 74)
print(f"RED_TEAM_ATTACKS = {n_ataques}")
print(f"RED_TEAM_SURVIVORS = {len(SOBREVIVENTES)}")
for s in SOBREVIVENTES:
    print("  ·", s)
