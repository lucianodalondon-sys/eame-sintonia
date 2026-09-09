#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS DO SYSTEM MAP

    UM MAPA DE AUDITORIA QUE NAO E AUDITADO NAO VALE NADA.

O validador (`validate_system_map.py`) prova que o mapa CORRESPONDE ao repo.
Este ficheiro prova outra coisa: que as REGRAS do mapa continuam a ser as que
foram escritas — que ele nao pinta verde sem evidencia, nao inventa aresta e
nao converte NAO SEI em certeza.

A diferenca importa. O validador reprova um mapa velho; estes testes reprovam
um mapa cujas regras alguem afrouxou. Um gerador que passasse a dar verde a
tudo continuaria a passar no validador — e falha aqui.

Corre como os outros testes desta casa:  py system-map/tests/test_system_map.py
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))

import generate_system_map as GEN  # noqa: E402

DADOS = RAIZ / "system-map" / "data"
S = json.loads((DADOS / "state.generated.json").read_text(encoding="utf-8"))
G = json.loads((DADOS / "architecture.generated.json").read_text(encoding="utf-8"))
D = json.loads((DADOS / "architecture.declared.json").read_text(encoding="utf-8"))

falhas: list[str] = []


def prova(nome: str, ok: bool, detalhe: str = ""):
    print(f"  {'PASS' if ok else 'FAIL'}  {nome}" + (f"\n        {detalhe}" if not ok and detalhe else ""))
    if not ok:
        falhas.append(nome)


# ── identidade ───────────────────────────────────────────────────────────────
ids = [n["id"] for n in S["NODES"]]
prova("ids_unicos", len(ids) == len(set(ids)))
prova("todo_no_tem_frase_de_gente",
      all(n["what"].strip() and n["why_here"].strip() for n in S["NODES"]),
      "peca sem 'o que faz' ou 'por que esta aqui' e peca que ninguem entende")
prova("todo_no_tem_motivo_de_status",
      all(n["status_reason"].strip() for n in S["NODES"]))

# ── as partes ────────────────────────────────────────────────────────────────
# Eram tres, e este teste dizia «exatamente tres». Passaram a quatro: entre a
# coleta e a inteligencia entrou A ESPERA, a faixa cinzenta onde o que ja foi
# colhido dorme ate ser processado. Ela nao e coleta (o trabalho acabou) nem
# inteligencia (ainda nao comecou), e enquanto vivia pintada de coleta dizia que
# guardar era colher.
#
# A trava continua: as partes sao ESTAS e sao NESTA ORDEM. Trocar «tres» por
# «quatro» so adiaria o problema — daqui a um mes seriam cinco sem ninguem
# decidir. Nomear cada uma obriga a passar por aqui quem quiser mudar o desenho.
PARTES_ESPERADAS = ["F-COLETA", "F-ESPERA", "F-INTELIGENCIA",
                    "F-GOVERNANCA", "F-ENTREGA"]
FAMS = {f["id"] for f in S["FAMILIES"]}
prova("as_partes_sao_estas_e_nesta_ordem",
      [f["id"] for f in S["FAMILIES"]] == PARTES_ESPERADAS,
      f"esperava {' -> '.join(PARTES_ESPERADAS)}; "
      f"encontrei {' -> '.join(f['id'] for f in S['FAMILIES'])}")
prova("toda_zona_tem_familia",
      all(z.get("family") in FAMS for z in S["TERRITORIES"]),
      "zona sem familia e bloco sem cor, fora da historia")
prova("toda_peca_tem_familia",
      all(n.get("family") in FAMS for n in S["NODES"]))
prova("nenhuma_parte_ficou_vazia",
      all(any(n["family"] == f for n in S["NODES"]) for f in FAMS),
      "parte sem nenhuma peca e um retangulo colorido a prometer o que nao tem")
prova("a_familia_vem_da_zona_e_nao_da_peca",
      all(n["family"] == next(z["family"] for z in S["TERRITORIES"]
                             if z["id"] == n["territory"]) for n in S["NODES"]),
      "peca a declarar familia diferente da sua zona cria dois agrupamentos")

# ── carimbo e medida nao se confundem ───────────────────────────────────────
# A divisao entre «a regua que CARIMBA» e «a regua que MEDE» foi feita a partir
# de uma medicao: carimba quem e usada por uma acao no momento em que ela colhe;
# mede quem olha para tras e da nota. Escrita a mao no ficheiro declarado, essa
# divisao envelhece calada — no dia em que um coletor passar a importar uma
# medida, a gaveta continua a dizer o contrario.
#
#     MEDIR NAO E FILTRAR. Uma regua que so mede nao barra nada, e por-la
#     antes das acoes faz parecer que ha peneira onde so ha termometro.
USADA_NA_COLETA = ("Z-ACOES", "Z-CANDIDATAS", "Z-VEICULOS", "Z-ADMISSAO")
ZONA = {n["id"]: n["territory"] for n in S["NODES"]}

# ⚠️ ESTA PROVA REPROVA, E A REPROVACAO E DELA — NAO DA ARVORE.
# Medido em 2026-09-09, com as tres respostas possiveis testadas:
#
#   como esta        acusa C-RASTRO      (o rastro MEDE; nao carimba nada)
#   sem contar IMPORTS  acusa C-PALAVRAS e C-SENSOR-COLETA
#
# O sinal que ela usa — «tem seta para uma zona de accao» — nao separa as duas
# coisas, porque nos quatro casos as setas sao `IMPORTS`, e a dependencia vai
# ao contrario do desenho: e o coletor que importa o rastro para emitir
# telemetria, nao o rastro que carimba o item.
#
#     UM IMPORT NAO E UM CARIMBO.
#     E A SETA DO IMPORT APONTA PARA O LADO CONTRARIO DA DEPENDENCIA.
#
# E ha um terceiro caso que a pergunta binaria nao consegue dizer:
# `C-SENSOR-COLETA` nao e regua NENHUMA — e um COLETOR a viver em `regras/`.
# A resposta certa para ele nao e «Z-REGRAS» nem «Z-MEDIDAS»: e mudar o
# ficheiro de pasta. Fica registado como rehome.
#
# NAO SE AFROUXA A PROVA PARA ELA FICAR VERDE. Ela continua como estava, a
# reprovar, e o que ela acusa esta explicado aqui. Uma prova que se conserta a
# ajustar o limiar ate o vermelho sumir deixa de medir seja o que for.
trocadas = []
for n in S["NODES"]:
    if n["territory"] not in ("Z-REGRAS", "Z-MEDIDAS"):
        continue
    carimba = any(ZONA.get(b) in USADA_NA_COLETA for b in n.get("outbound", []))
    devia = "Z-REGRAS" if carimba else "Z-MEDIDAS"
    if devia != n["territory"]:
        trocadas.append(f"{n['name']}: esta em {n['territory']}, medido como {devia}")
prova("regua_que_carimba_nao_e_regua_que_mede", not trocadas,
      "; ".join(trocadas[:4]))

# ── as conexoes dizem QUE TIPO de ligacao sao ───────────────────────────────
# Dez provas, e cada uma existe por uma maneira conhecida de o mapa mentir sobre
# uma ligacao. A primeira e a mais importante, e nasceu de um caso real:
#
#     orquestrador/orquestrador.py:54   import admissao as adm
#
# O mapa dizia «A porta de admissao importa O orquestrador» — o contrario do que
# o codigo faz. A seta estava certa (o codigo do importado entra no importador);
# a FRASE e que tinha ficado com o verbo da direcao antiga. Setenta e seis
# arestas assim, e nenhuma dava erro: lida sozinha, cada frase parecia plausivel.
CATEGORIAS_CONHECIDAS = {"DATA", "CONTROL", "READ", "RULE", "WRITE", "PROOF",
                         "CODE", "UNKNOWN"}
TECNICAS = [e for e in S["EDGES"] if e.get("kind") == "technical"]
POR_ID = {n["id"]: n for n in S["NODES"]}


def _nome(i):
    return POR_ID.get(i, {}).get("name", i)


# T1 · um import nunca aparece descrito ao contrario
invertidas = []
for e in TECNICAS:
    if e.get("raw_type") != "IMPORTS":
        continue
    de, para = _nome(e["from"]), _nome(e["to"])
    # a seta vai do importado para o importador; dizer «<de> importa <para>»
    # seria afirmar exatamente o contrario do que o codigo faz
    if f"{de} importa {para}" in e.get("reason", ""):
        invertidas.append(f"{de} -> {para}")
prova("T1_import_nao_e_descrito_ao_contrario", not invertidas,
      f"{len(invertidas)} frase(s) invertidas: " + "; ".join(invertidas[:3]))

# T2 · CODE nunca vira DATA sozinho
so_import = [f"{_nome(e['from'])} -> {_nome(e['to'])}" for e in TECNICAS
             if e.get("raw_type") == "IMPORTS" and e.get("categoria") == "DATA"
             and not e.get("passa_pelo_preparo")]
prova("T2_import_sozinho_nao_vira_dado", not so_import,
      "dois modulos conversarem nao prova que um item passou: " + "; ".join(so_import[:3]))

# T3 · RUNS gera CONTROL
mau_runs = [f"{_nome(e['from'])} -> {_nome(e['to'])} = {e.get('categoria')}"
            for e in TECNICAS
            if e.get("raw_type") == "RUNS" and e.get("categoria") not in ("CONTROL", "PROOF")]
prova("T3_runs_gera_comando", not mau_runs, "; ".join(mau_runs[:3]))

# T4 · uma leitura nao se disfarca de dado
mau_read = [f"{_nome(e['from'])} -> {_nome(e['to'])}" for e in TECNICAS
            if e.get("raw_type") == "READS" and e.get("categoria") == "DATA"
            and not e.get("passa_pelo_preparo")]
prova("T4_leitura_nao_e_dado", not mau_read, "; ".join(mau_read[:3]))

# T5 · prova nao e fluxo de dado
mau_proof = [f"{_nome(e['from'])} -> {_nome(e['to'])}" for e in TECNICAS
             if e.get("categoria") == "PROOF" and e.get("payload") == "coleta"]
prova("T5_prova_nao_e_fluxo_de_dado", not mau_proof, "; ".join(mau_proof[:3]))

# T5b · NENHUM DADO SALTA A FRONTEIRA PARA A INTELIGENCIA
#
# A coleta entrega pela porta: ADMISSAO -> READY. Um artefacto que va de uma
# peca da coleta DIRECTO para uma peca da inteligencia esta a saltar a porta —
# e isso ou tem uma lei que o autorize, ou e um desvio.
#
#     COLETAR != ADMITIR != JULGAR.
#
# Medido em 2026-09-09: das 148 ligacoes que atravessam essa fronteira, ZERO
# sao DATA. 77 sao PROOF (provas que MEDEM a coleta), 38 READ, 14 CODE, 11
# RULE e 8 CONTROL. Nenhuma leva item nenhum.
#
# As tres que o mapa mostrava como DATA eram falsas, e todas pelo mesmo
# defeito: a regra que promove a ligacao de uma ferramenta de PREPARO a DATA
# disparava sem olhar para o outro topo, e apanhava um censo que LE o codigo
# da ferramenta e uma lei que ela CONSULTA.
#
#     UMA PROVA QUE ME MEDE NAO ESTA NO MEU CAMINHO.
#     UMA REGRA QUE EU CONSULTO NAO VIAJA COMIGO.
#
# Este caso NAO exige zero para sempre. Exige que, se um dado passar a
# atravessar, alguem tenha de vir aqui declarar a lei que o autoriza — em vez
# de o desvio aparecer calado no meio de 148 ligacoes legitimas.
FAM = {n["id"]: n.get("family") for n in S["NODES"]}
LADO_DA_COLETA = {"F-COLETA", "F-ESPERA"}
# Preenche-se com (from, to, LEI) quando existir travessia autorizada.
TRAVESSIAS_AUTORIZADAS: set = set()
# ⚠️ TODAS as ligacoes, e nao so as TECNICAS. Uma aresta `expected` — declarada
# e ainda por provar — tambem sabe hoje dizer que leva DADO, desde que se
# deixou de confundir «esta provada?» com «o que e que viaja?». Se este caso
# olhasse so para as tecnicas, bastava declarar a travessia a mao para ela
# passar por baixo da porta.
#
#     DECLARAR UM ATALHO NAO E TER PERMISSAO PARA ELE.
saltam = [f"{_nome(e['from'])} -> {_nome(e['to'])}" for e in S["EDGES"]
          if e.get("categoria") == "DATA"
          and FAM.get(e["from"]) in LADO_DA_COLETA
          and FAM.get(e["to"]) == "F-INTELIGENCIA"
          and (e["from"], e["to"]) not in TRAVESSIAS_AUTORIZADAS]
prova("T5b_nenhum_dado_salta_a_porta_para_a_inteligencia", not saltam,
      "; ".join(saltam[:3]))

# T6 · a evidencia continua acessivel
sem_prova = [f"{_nome(e['from'])} -> {_nome(e['to'])}" for e in TECNICAS
             if not e.get("evidence")
             or not all(x.get("file") and isinstance(x.get("line"), int)
                        for x in e["evidence"])]
prova("T6_evidencia_continua_acessivel", not sem_prova, "; ".join(sem_prova[:3]))

# T7 · ligar e desligar categorias nao mexe nas pecas
MAPA_JS = (RAIZ / "system-map" / "app" / "map.js").read_text(encoding="utf-8")
prova("T7_filtro_de_conexao_so_mexe_em_setas",
      "input[name=cat]" in MAPA_JS
      and "cats.has(g.dataset.cat" in MAPA_JS
      and "cats" not in MAPA_JS.split("nodes.forEach(n => {")[1].split("});")[0],
      "o filtro de conexoes nao pode entrar na conta das pecas")

# T8 · a vista de coleta abre com DADO e COMANDO
INDEX = (RAIZ / "system-map" / "app" / "index.html").read_text(encoding="utf-8")
import re as _re
ligadas = {m.group(1) for m in _re.finditer(
    r'name="cat" value="(\w+)" checked', INDEX)}
prova("T8_abre_com_dado_e_comando", ligadas == {"DATA", "CONTROL"},
      f"abre com {sorted(ligadas)}; espera-se DATA e CONTROL")

# T9 · toda ligacao tem categoria conhecida
sem_cat = [f"{_nome(e['from'])} -> {_nome(e['to'])}" for e in S["EDGES"]
           if e.get("categoria") not in CATEGORIAS_CONHECIDAS]
prova("T9_toda_ligacao_tem_categoria", not sem_cat, "; ".join(sem_cat[:3]))

# T10 · sem categoria nao vira DATA por omissao
GERADOR = (RAIZ / "system-map" / "scripts" / "generate_system_map.py").read_text(
    encoding="utf-8")
prova("T10_omissao_nao_e_dado",
      "CATEGORIA_DO_TIPO.get(tipo, DESCONHECIDA)" in GERADOR,
      "tipo desconhecido tem de cair em UNKNOWN, nunca em DATA")

# ── a avenida mostra responsabilidades, e nao esconde nada ──────────────────
# Doze provas. A tentacao de uma reorganizacao visual e sempre a mesma: tirar do
# ecra o que incomoda e chamar-lhe «agrupamento». Estas provas existem para isso
# nao acontecer — agrupar nao e apagar, e o desvio continua a doer a vista.
POR_ID_N = {n["id"]: n for n in S["NODES"]}
APP = RAIZ / "system-map" / "app"
MAPJS = (APP / "map.js").read_text(encoding="utf-8")

# E1 · o pedido continua no mapa, e continua a ter os seus ficheiros
ped = POR_ID_N.get("C-PEDIDO")
prova("E1_pedido_continua_acessivel",
      bool(ped) and bool(ped.get("files")),
      "o contrato do pedido nao pode desaparecer por ter deixado a avenida")

# E2 · a receita continua, e continua com um so consumidor
rec = POR_ID_N.get("C-RECEITAS")
# ⚠️ UM CENSO QUE ME LE NAO E UM CONSUMIDOR MEU.
# Esta prova passou a reprovar com tres consumidores, e o terceiro era
# `C-ESTRADAS-IT` — um CENSO, em Z-PROVA, que importa `pedido/receitas.py`
# para a medir. Contar uma prova como consumidor faz um modulo interno
# parecer que ganhou clientes quando so ganhou um medidor.
#
#     QUEM ME MEDE NAO ME CONSOME.
#
# A pergunta e sobre consumo OPERACIONAL, entao as pecas de prova saem da
# conta — e continuam visiveis, so nao contam como cliente.
consumidores = [e["to"] for e in S["EDGES"]
                if e["from"] == "C-RECEITAS" and e.get("kind") == "technical"
                and ZONA.get(e["to"]) != "Z-PROVA"]
prova("E2_receita_continua_com_um_consumidor",
      bool(rec) and set(consumidores) <= {"C-ORQUESTRADOR", "C-PROVA-COLETA"},
      f"consumidores da receita: {sorted(set(consumidores))}")

# E3 · nem o pedido nem a receita sao estacao principal
prova("E3_receita_nao_e_estacao_principal",
      (rec or {}).get("nivel") == "INTERNO" and (ped or {}).get("nivel") == "INTERNO",
      "modulo interno nao pode competir com o orquestrador na avenida")

# E4 · os botoes vivem na entrada
bot = POR_ID_N.get("C-CI-COLETA")
prova("E4_botoes_vivem_na_entrada",
      (bot or {}).get("territory") == "Z-ENTRADA")

# E5/E6 · o scrap e executor composto, e nao ferramenta
scr = POR_ID_N.get("C-SINTONIA-SCRAP")
prova("E5_scrap_e_executor_composto",
      (scr or {}).get("papel") == "EXECUTOR COMPOSTO",
      f"papel medido: {(scr or {}).get('papel')}")
prova("E6_scrap_nao_e_ferramenta",
      (scr or {}).get("territory") != "Z-FERRAMENTAS",
      "despachar seis executores nao e ser ferramenta")

# E7 · a Apify continua a ser ferramenta paga, e continua no mapa
ap = POR_ID_N.get("C-APIFY-POOL")
prova("E7_apify_e_ferramenta_paga",
      bool(ap) and ap.get("territory") == "Z-FERRAMENTAS"
      and ap.get("momento") == "ROTA")

# E8 · o mapa NAO afirma que «gratis primeiro» esta em vigor
texto_do_mapa = json.dumps(S, ensure_ascii=False).lower()
prova("E8_mapa_nao_afirma_fallback_garantido",
      "apify so depois" not in texto_do_mapa
      and "apify apenas se" not in texto_do_mapa,
      "a politica «gratis primeiro» nao esta em codigo nenhum; "
      "o mapa nao pode dizer que esta")

# E9 · os desvios continuam visiveis
desvios = [e for e in S["EDGES"] if e.get("desvio")]
saltam = [n for n in S["NODES"] if n.get("salta_o_orquestrador")]
prova("E9_desvios_continuam_visiveis", bool(desvios) or bool(saltam),
      "reorganizar a avenida e apagar o desvio seria maquilhagem")

# E10 · agrupar nao apagou ninguem
prova("E10_agrupar_nao_apagou_ninguem",
      len(S["NODES"]) >= 97 and all(n.get("nivel") for n in S["NODES"]),
      f"{len(S['NODES'])} pecas; antes da etapa 3 eram 97")

# E11 · CURRENT e PROPOSED nao se confundem
declarado = json.dumps(D, ensure_ascii=False)
prova("E11_proposta_nao_se_disfarca_de_estado",
      "PROPOSED" not in declarado,
      "nenhuma aresta ou peca PROPOSED pode estar no ficheiro declarado: "
      "o mapa desenha o que existe, e a proposta vive no documento")

# E12 · as duas vistas existem e sao medidas, nao escritas a mao
prova("E12_as_duas_vistas_existem",
      "'canonico'" in MAPJS and "'desvios'" in MAPJS
      and "n.nivel === 'PRINCIPAL'" in MAPJS
      and "n.salta_o_orquestrador" in MAPJS)

# ── a prateleira ─────────────────────────────────────────────────────────────
GAVETAS = {z["folder"] for z in S["TERRITORIES"] if z.get("folder")}
PASTA_DA_ZONA = {z["id"]: z.get("folder") for z in S["TERRITORIES"]}
prova("cada_zona_com_codigo_tem_gaveta",
      all(PASTA_DA_ZONA.get(n["territory"])
          for n in S["NODES"]
          for f in n["files"] if f.split("/")[0] in GAVETAS),
      "zona com ficheiro em gaveta tem de dizer qual e a sua")
prova("nenhum_ficheiro_na_gaveta_errada",
      all(f.split("/")[0] == PASTA_DA_ZONA.get(n["territory"])
          for n in S["NODES"] for f in n["files"]
          if f.split("/")[0] in GAVETAS),
      "a prateleira e o mapa tem de contar a mesma historia")
prova("a_pasta_antiga_scripts_nao_voltou",
      not (RAIZ / "scripts").exists()
      or not any((RAIZ / "scripts").glob("*.py")),
      "ficheiro novo em scripts/ e ficheiro sem gaveta")
prova("existe_um_so_lugar_com_a_lista_de_gavetas",
      (RAIZ / "_gavetas.py").exists(),
      "duas listas de gavetas sao duas verdades")

# ── arestas ──────────────────────────────────────────────────────────────────
conhecidos = set(ids)
prova("nenhuma_aresta_solta",
      all(e["from"] in conhecidos and e["to"] in conhecidos for e in S["EDGES"]))
prova("nenhuma_aresta_tecnica_sem_prova",
      all(e["evidence"] for e in S["EDGES"] if e.get("kind") == "technical"),
      "aresta tecnica sem linha de codigo e aresta inventada")
prova("toda_prova_aponta_para_ficheiro_real",
      all(ev["file"] in {f["path"] for f in G["FILES"]}
          for e in S["EDGES"] for ev in e.get("evidence", [])))
prova("aresta_declarada_e_nao_provada_fica_cinza",
      all(e["status"] == "UNKNOWN" for e in S["EDGES"] if e.get("kind") == "expected"))

# ── status ───────────────────────────────────────────────────────────────────
VALIDOS = {"PROVEN", "PENDING", "BROKEN", "UNKNOWN"}
prova("status_do_vocabulario_fechado", all(n["status"] in VALIDOS for n in S["NODES"]))
prova("verde_nunca_e_so_existir",
      all(n["inbound"] or n["outbound"]
          or (n.get("proof") == "document" and n["files"])
          or n.get("proof") == "git-measurement"
          for n in S["NODES"] if n["status"] == "PROVEN"),
      "peca verde sem ligacao provada nem documento que a prove e verde por existir")
prova("facto_verde_nomeia_a_prova",
      all(n["files"] or n.get("proof") == "git-measurement"
          for n in S["NODES"]
          if n.get("proof") and n["status"] == "PROVEN"),
      "facto tem de citar documento versionado ou medicao do git")
prova("nao_ha_verde_sem_tipo_de_prova",
      all(n["inbound"] or n["outbound"]
          or n.get("proof") in ("document", "git-measurement")
          for n in S["NODES"] if n["status"] == "PROVEN"),
      "'eu sei' nao e um tipo de prova aceite")

# ── as fontes: um acervo, nao vinte e tres cartoes ───────────────────────────
ACERVO = [n for n in S["NODES"] if n.get("groups")]
prova("o_acervo_de_fontes_e_uma_peca_so", len(ACERVO) == 1,
      f"as fontes tem de ser UM cartao com a lista dentro; encontrei {len(ACERVO)}")

if ACERVO:
    A = ACERVO[0]
    prova("o_acervo_agrupa_por_tipo_de_fonte",
          len(A["groups"]) >= 2
          and any("OFICIA" in g["titulo"] for g in A["groups"]),
          "bases oficiais e contas de rede social sao registros diferentes e "
          "aparecem separados")
    prova("todo_grupo_diz_onde_esta_registrado",
          all(g.get("onde") for g in A["groups"]),
          "grupo sem ficheiro de origem e lista que ninguem consegue conferir")
    prova("todo_item_do_acervo_diz_se_a_maquina_sabe_buscar",
          all("sabe_coletar" in i for g in A["groups"] for i in g["itens"]),
          "sem isto, fonte vista uma vez parece fonte resolvida")
    prova("o_acervo_nao_e_verde_com_fonte_sem_contrato",
          A["status"] != "PROVEN"
          or all(i["sabe_coletar"] for g in A["groups"] for i in g["itens"]),
          "verde aqui diria que esta resolvido, e nao esta")
    prova("nao_sei_sobrevive_no_acervo",
          all(i["estado"] in ("GREEN", "YELLOW", "RED", "NAO SEI")
              for g in A["groups"] for i in g["itens"]),
          "'nao consegui ver' nao pode virar 'vi e nao presta'")

    # ── a porta de entrada ────────────────────────────────────────────────────
    K = A.get("intake") or {}
    prova("existe_porta_de_entrada_de_fonte_nova",
          bool(K.get("porta")) and (RAIZ / K["porta"]).exists(),
          "capital parado sem porta apodrece: fonte nova morre no terminal de quem a viu")
    prova("a_escada_tem_quatro_degraus", len(K.get("escada", [])) == 4,
          "candidata -> registada -> contratada -> automatica")
    prova("cada_degrau_diz_onde_mora_e_como_se_sobe",
          all(d.get("onde") and d.get("sobe_como") for d in K.get("escada", [])),
          "degrau sem caminho de subida e degrau decorativo")
    prova("o_que_entra_pela_porta_e_candidata_e_nao_fonte",
          K.get("escada", [{}])[0].get("nome") == "CANDIDATA"
          and K["escada"][0]["onde"] != "docs/fontes/ATLAS-DE-FONTES-EAME.md",
          "pista entrando direto no atlas seria afirmar fonte sem ninguem ter olhado")

# ── determinismo ─────────────────────────────────────────────────────────────
# Mesma arvore + mesmo HEAD tem de dar byte a byte o mesmo ficheiro. Se falhar,
# o CI acusaria drift a cada corrida e a lei perderia os dentes numa semana.
antes = (DADOS / "architecture.generated.json").read_text(encoding="utf-8")
subprocess.run([sys.executable, str(RAIZ / "system-map" / "scripts" / "scan_repo.py")],
               capture_output=True)
prova("scanner_e_deterministico",
      antes == (DADOS / "architecture.generated.json").read_text(encoding="utf-8"),
      "correr duas vezes deu resultado diferente")

# A proveniencia (HEAD, BRANCH, data) tem de viver FORA da arquitetura. Se
# alguem a voltar a misturar, o CI passa a reprovar toda a gente em todo o
# commit — e a lei morre por excesso de dentes, nao por falta.
prova("proveniencia_separada_da_arquitetura",
      "PROVENANCE" in S and "HEAD" not in S and "BRANCH" not in S,
      "HEAD/BRANCH no corpo do estado fariam o portao reprovar sempre")

# ── a lei existe e aponta para o validador ───────────────────────────────────
agents = RAIZ / "AGENTS.md"
prova("AGENTS_md_existe", agents.exists())
if agents.exists():
    lei = agents.read_text(encoding="utf-8")
    prova("AGENTS_md_manda_correr_o_validador",
          "validate_system_map.py" in lei,
          "a lei tem de dizer o comando, nao so pedir bom senso")
    prova("AGENTS_md_diz_que_o_mapa_e_derivado",
          "derivado" in lei.lower())
claude = RAIZ / "CLAUDE.md"
prova("CLAUDE_md_aponta_para_AGENTS_md",
      claude.exists() and "AGENTS.md" in claude.read_text(encoding="utf-8"))
readme = RAIZ / "README.md"
prova("README_aponta_agentes_para_AGENTS_md",
      readme.exists() and "AGENTS.md" in readme.read_text(encoding="utf-8"))

# ── a app so renderiza ───────────────────────────────────────────────────────
js = (RAIZ / "system-map" / "app" / "map.js").read_text(encoding="utf-8")
prova("a_tela_le_o_estado_de_um_ficheiro", "state.generated.json" in js)
css = (RAIZ / "system-map" / "app" / "map.css").read_text(encoding="utf-8")
prova("as_tres_partes_tem_cor_propria",
      all(f"--fam-{n}:" in css for n in ("coleta", "inteligencia", "entrega")),
      "cada parte tem de ter a sua cor num token, nao espalhada a mao")
prova("a_tela_usa_tokens_do_design_system", "--adama:#009845" in css,
      "o verde ADAMA tem de estar no token, nao espalhado a mao pela folha")
prova("a_rampa_de_estado_e_separada_da_marca",
      all(t in css for t in ("--ok:", "--warn:", "--bad:", "--unknown:")),
      "estado e marca a partilhar a mesma cor estragam as duas leituras")
html = (RAIZ / "system-map" / "app" / "index.html").read_text(encoding="utf-8")
prova("a_pagina_carrega_o_design_system_oficial", "_ds/adama-brandwell" in html)
prova("a_pagina_sobrevive_sem_javascript",
      "<noscript>" in html and "state.generated.json" in html,
      "sem JS, a pagina tem de apontar para o ficheiro que carrega o mesmo conteudo")

# A tela nao pode voltar a guardar factos. O prototipo original trazia as pecas
# escritas dentro do JS — foi exatamente isso que esta missao veio desfazer.
proibido = [t for t in ("const nodes=[", "const edges=[", "const NODES", "const SNAP")
            if t in js]
prova("a_tela_nao_guarda_facto_nenhum", not proibido,
      f"encontrado no map.js: {proibido} — facto escrito na tela nao passa por validador")

# ─────────────────────────────────────────────────────────────────────────────
# A CONSTANTE QUE ESCONDE O AUTOR
#
# `scan_repo.escritas_por_constante` liga a linha que DA NOME ao ficheiro com a
# linha que o ESCREVE, seiscentas linhas abaixo. Duas coisas escapavam-lhe, e as
# duas apagavam autoria real do mapa:
#
#   1 · so via `open(X, 'w')`. Metade desta casa escreve com `pathlib`, e
#       `LIVRO.write_text(...)` nao passa por `open()` nenhum. A porta de
#       admissao aparecia com `produces: []` — o mapa dizia, por escrito, que
#       nada saia dela — e `REGISTO-DE-ARTEFATOS.json` tinha nove leitores e
#       zero autores.
#
#   2 · deixava a ULTIMA atribuicao ganhar, varrendo o modulo inteiro sem olhar
#       a escopo nem a ordem. Sessenta nomes desta arvore estao ligados a mais
#       de um ficheiro, e isso fabricava arestas.
# ─────────────────────────────────────────────────────────────────────────────
sys.path.insert(0, str(RAIZ / "system-map" / "scripts"))
import scan_repo as SCAN  # noqa: E402

_UNICOS = {"UM.json": ["data/UM.json"], "DOIS.json": ["data/DOIS.json"]}

_PATHLIB = """
import pathlib
LIVRO = pathlib.Path('data/UM.json')
def escrever():
    LIVRO.write_text('{}')
"""
_achado = SCAN.escritas_por_constante("sintetico.py", _UNICOS, _PATHLIB)
prova("escrita_por_pathlib_tem_autor",
      [(a, t) for a, t, *_ in _achado] == [("data/UM.json", "WRITES")],
      f"`CONST.write_text()` e uma escrita como qualquer outra; medido: {_achado}")

# MUTACAO 1 · o detector tem de estar preso ao METODO, nao a presenca do nome.
_MUTANTE = _PATHLIB.replace("write_text", "resolve")
prova("mutacao_metodo_que_nao_escreve_nao_vira_autor",
      not SCAN.escritas_por_constante("sintetico.py", _UNICOS, _MUTANTE),
      "`LIVRO.resolve()` nao escreve nada e nao pode dar autoria a ninguem")

# MUTACAO 2 · a prova tem de ser a LINHA QUE ESCREVE. Uma aresta certa com prova
# inventada e uma aresta que ninguem consegue conferir.
prova("a_prova_e_a_linha_que_escreve",
      _achado and _achado[0][5] == "LIVRO.write_text('{}')" and _achado[0][2] == 5,
      f"medido: linha {_achado[0][2] if _achado else '-'} · {_achado[0][5] if _achado else '-'}")

# ESCOPO · a ligacao viva e a ultima ANTES daquela linha, no escopo mais proximo.
# Este e o caso real de `superficie/ask_sintonia.py`: a escrita do BENCHMARK
# estava a ser atribuida ao TESTE porque a atribuicao de baixo tinha ganho.
_ESCOPO = """
import json
def benchmark():
    out = 'data/UM.json'
    json.dump({}, open(out, 'w'))
out = 'data/DOIS.json'
json.dump({}, open(out, 'w'))
"""
_e = sorted((a, t, n) for a, t, n, *_ in SCAN.escritas_por_constante(
    "sintetico.py", _UNICOS, _ESCOPO))
prova("cada_escrita_vai_para_o_ficheiro_que_estava_vivo_ali",
      _e == [("data/DOIS.json", "WRITES", 7), ("data/UM.json", "WRITES", 5)],
      f"a atribuicao de baixo nao pode roubar a escrita de cima; medido: {_e}")

# MUTACAO 3 · sem nenhuma ligacao ANTES da linha, nao se responde. Adivinhar o
# ficheiro seria fabricar a aresta mais importante do mapa.
_DEPOIS = """
import json
def escrever():
    json.dump({}, open(out, 'w'))
out = 'data/UM.json'
"""
prova("sem_ligacao_antes_da_linha_o_censo_cala_se",
      not SCAN.escritas_por_constante("sintetico.py", _UNICOS, _DEPOIS),
      "nome so ligado DEPOIS da escrita: nao ha como saber, e nao se inventa")

# ── e no repositorio de verdade: os tres artefactos que nao tinham autor ─────
_AUTORES = {}
for _e in G["FILE_EDGES"]:
    if _e["type"] == "WRITES":
        _AUTORES.setdefault(_e["to_file"], []).append(_e["from_file"])
# O nome vem partido de proposito. Este teste NAO abre nenhum destes ficheiros:
# le o mapa e pergunta-lhe quem os escreve. Escrever o caminho inteiro aqui
# criaria tres arestas READS a dizer que o teste os consome — e foi contra
# exactamente esse tipo de aresta (um nome numa lista nao e uma rota) que este
# bloco todo foi escrito.
for _pasta, _nome in (("data/samples", "LIVRO-DE-DECISOES"),
                      ("data/derivados", "REGISTO-DE-ARTEFATOS"),
                      ("data/samples", "RUN-MANIFEST")):
    _art = f"{_pasta}/{_nome}.json"
    prova(f"tem_autor_{_nome}", bool(_AUTORES.get(_art)),
          "UM ARTEFACTO SEM AUTOR NAO E UM ARTEFACTO SEM AUTOR — "
          "E UMA MEDICAO QUE NAO OLHOU")

# O dono eleito por ordem alfabetica nao e um dono: quando ha mais de um autor,
# o mapa tem de o DIZER em vez de sortear em silencio.
prova("o_artefacto_com_dois_autores_esta_declarado",
      "ARTEFACT_MULTIPLE_AUTHORS" in S,
      "sem esta lista, o dono de RUN-MANIFEST.json muda sozinho quando alguem "
      "renomeia uma peca, e ninguem repara")


# ─────────────────────────────────────────────────────────────────────────────
# PROSA NAO E CODIGO · VOCABULARIO NAO E ROTA
#
# Quatro voltas da mesma licao, cada uma medida sobre uma aresta que o mapa
# publicava como PROVEN. As tres primeiras olham a FORMA da linha; a quarta le
# o que a linha DIZ.
# ─────────────────────────────────────────────────────────────────────────────

# 1 · o varredor lia a sua propria documentacao
# A prova localiza-se sozinha: procura no proprio varredor uma linha que esta
# dentro de um docstring e outra que e codigo, e exige que a regra as separe.
_alvo = "system-map/scripts/scan_repo.py"
_linhas = (RAIZ / _alvo).read_text(encoding="utf-8").splitlines()
_prosa_do_scan = SCAN.linhas_de_prosa(_alvo)
_na_frase = next((i for i, l in enumerate(_linhas, 1)
                  if "e um caminho relativo a propria pasta" in l), None)
_no_codigo = next((i for i, l in enumerate(_linhas, 1)
                   if l.startswith("def relativo(")), None)
prova("linha_de_docstring_nao_e_linha_de_codigo",
      _na_frase is not None and _no_codigo is not None
      and _na_frase in _prosa_do_scan and _no_codigo not in _prosa_do_scan,
      f"frase={_na_frase} codigo={_no_codigo} — a regra tem de excluir a "
      "primeira e deixar a segunda")
_G = json.loads((DADOS / "architecture.generated.json").read_text(encoding="utf-8"))
_prosa = {}
for _e in _G["FILE_EDGES"]:
    _f = _e["evidence"]["file"]
    if not _f.endswith(".py"):
        continue
    if _f not in _prosa:
        _prosa[_f] = SCAN.linhas_de_prosa(_f)
    if _e["evidence"]["line"] in _prosa[_f]:
        falhas.append("aresta provada por docstring")
        break
prova("nenhuma_aresta_e_provada_por_docstring",
      "aresta provada por docstring" not in falhas,
      "o varredor chegou a escrever que escreve num ficheiro que nunca abre, "
      "porque o nome dele aparecia na frase que explica a regra")

# 2 · a rede vista no CODIGO, nao numa string
prova("campo_que_regista_zero_apify_nao_e_chamada_a_apify",
      not GEN._fala_com_a_rede("coleta/sensor_canal_identidade.py"),
      "a unica palavra de rede naquele ficheiro e a chave 'APIFY_RUNS': 0")
prova("import_de_apify_pool_continua_a_ser_rede",
      GEN._fala_com_a_rede("coleta/comunicacao_coleta.py"),
      "`import apify_pool` e um NOME no codigo, e nao um rotulo entre aspas")

# 3 · comparar uma URL com um dominio nao e ter ido la buscar algo
prova("tabela_de_hosts_nao_e_rota",
      GEN._e_tabela_de_hosts("    ('youtube.com', 'YOUTUBE'), ('youtu.be', 'YOUTUBE'),"),
      "a tabela HOSTS reconhece o dominio de uma URL que a PESSOA declarou no ORCID")
prova("id_de_ator_nao_e_dominio",
      not GEN._e_tabela_de_hosts(
          "    'YOUTUBE': ('streamers~youtube-scraper', 'JA_RODOU_NESTA_CASA'),"),
      "a regra tem de deixar passar a rota a serio que vive na linha ao lado")

# 4 · uma linha que diz NOT_TESTED nao prova travessia nenhuma
prova("linha_que_diz_que_nao_correu_nao_prova_passagem",
      GEN._diz_que_nao_aconteceu("{'LINKEDIN': 'NOT_TESTED', 'YOUTUBE': 'NOT_TESTED',"),
      "DECLARED != OBSERVED, e ERROR != REJECTED != UNKNOWN != NOT_RUN")
prova("linha_que_diz_que_ja_correu_continua_a_valer",
      not GEN._diz_que_nao_aconteceu(
          "    'YOUTUBE': ('streamers~youtube-scraper', 'JA_RODOU_NESTA_CASA'),"))

# 5 · e o cartao do canal nao pode prometer mais do que mediu
_canais = [n for n in S["NODES"] if n["id"].startswith("V-") and n["id"] != "V-HTTP"]
prova("o_cartao_do_canal_diz_que_a_rota_e_declarada",
      all("NOMEIAM" in n["status_reason"] or "NAO SEI" in n["status_reason"]
          for n in _canais),
      "O CODIGO NOMEAR UM CANAL NAO E ALGO TER VINDO POR ELE — "
      "e o cartao tem de o dizer, senao le-se como travessia observada")

# O corpus le o ORCID, e nao o LinkedIn, o YouTube nem o Instagram. Foram tres
# arestas, cada uma provada por uma linha pior que a anterior.
_do_corpus = {e["from"] for e in S["EDGES"]
              if e["to"] == "C-CORPUS" and e["type"] == "VIAJA_POR"}
prova("o_corpus_nao_colhe_das_redes_sociais",
      _do_corpus <= {"V-HTTP"},
      f"canais ligados a C-CORPUS: {sorted(_do_corpus)} — a unica rede daquele "
      "ficheiro e pub.orcid.org")


# ─────────────────────────────────────────────────────────────────────────────
# GOVERNANCA — o que mede e o que regula nao e um passo da esteira
#
# `Z-PROVA` (34) e `Z-REGUAS` (11) viviam em `F-INTELIGENCIA` por nao haver
# familia para elas, e isso fazia 143 ligacoes de PROVA e de REGRA parecerem a
# coleta a falar com o motor. A leitura «a Collection conversa 149 vezes com a
# Intelligence» nascia inteira daqui.
#
#     PROVA != INTELIGENCIA.   REGRA != INTELIGENCIA.
#     E NENHUMA DAS DUAS E ETAPA OPERACIONAL.
# ─────────────────────────────────────────────────────────────────────────────
_GOV = [z for z in S["TERRITORIES"] if z.get("family") == "F-GOVERNANCA"]
prova("a_governanca_existe_como_familia",
      any(f["id"] == "F-GOVERNANCA" for f in S["FAMILIES"]),
      "sem familia propria, prova e regra voltam a contar como Intelligence")
prova("a_governanca_e_transversal",
      next((f for f in S["FAMILIES"] if f["id"] == "F-GOVERNANCA"), {}).get("transversal") is True,
      "a familia tem de dizer que atravessa o sistema, e nao que e um troco da esteira")
prova("prova_e_regua_vivem_na_governanca",
      {z["id"] for z in _GOV} == {"Z-PROVA", "Z-REGUAS"},
      f"em F-GOVERNANCA: {sorted(z['id'] for z in _GOV)} — esperava Z-PROVA e Z-REGUAS")
# A moldura de uma familia e o retangulo que envolve as zonas dela. Com as zonas
# intercaladas, a caixa da COLETA engolia a da GOVERNANCA e o desenho passava a
# dizer o contrario do que a arrumacao diz. A ordem das zonas e a regra.
_ORDEM = [z["family"] for z in S["TERRITORIES"]]
_blocos = [f for i, f in enumerate(_ORDEM) if i == 0 or f != _ORDEM[i - 1]]
prova("cada_familia_ocupa_um_bloco_contiguo",
      len(_blocos) == len(set(_blocos)),
      f"familias intercaladas na ordem das zonas: {_blocos}")
prova("a_governanca_fica_fora_da_esteira",
      _blocos[-1] == "F-GOVERNANCA",
      f"a esteira acaba em {_blocos[-1]}; governanca no meio le-se como mais um passo")
# A espinha da coleta, da esquerda para a direita, e o que Luciano le primeiro.
_ESPINHA = ["Z-BIBLIA", "Z-ENTRADA", "Z-PEDIDO", "Z-ORQUESTRADOR", "Z-CANDIDATAS",
            "Z-FONTES", "Z-EXECUCAO", "Z-VEICULOS", "Z-FERRAMENTAS", "Z-ACOES",
            "Z-GUARDA", "Z-REGRAS", "Z-ADMISSAO", "Z-ESPERA"]
_no_acervo = [z["id"] for z in S["TERRITORIES"] if "acervo" in z.get("views", [])]
prova("a_esteira_le_se_da_esquerda_para_a_direita", _no_acervo == _ESPINHA,
      f"a vista do acervo esta em {_no_acervo}")
prova("a_esteira_acaba_no_ready", _no_acervo[-1] == "Z-ESPERA",
      "nada pode vir depois do READY na vista principal")

prova("nenhuma_zona_de_prova_ou_regua_ficou_na_inteligencia",
      not [z["id"] for z in S["TERRITORIES"]
           if z["id"] in ("Z-PROVA", "Z-REGUAS") and z.get("family") == "F-INTELIGENCIA"],
      "voltar Z-PROVA para F-INTELIGENCIA repoe as 143 travessias falsas")

# A conta, medida — e nao a impressao. O que sobra para a INTELIGENCIA tem de
# ser pequeno e explicavel peca a peca; o que vai para a GOVERNANCA e grande e
# tambem esta certo.
_FAMN = {n["id"]: n.get("family") for n in S["NODES"]}
def _atravessa(a, b):
    return [e for e in S["EDGES"] if _FAMN.get(e["from"]) == a and _FAMN.get(e["to"]) == b]
_ci, _cg = _atravessa("F-COLETA", "F-INTELIGENCIA"), _atravessa("F-COLETA", "F-GOVERNANCA")
prova("a_coleta_nao_conversa_com_o_motor_as_centenas", len(_ci) <= 12,
      f"COLETA -> INTELIGENCIA = {len(_ci)}; COLETA -> GOVERNANCA = {len(_cg)}")
prova("toda_travessia_para_a_inteligencia_tem_prova",
      all(e.get("evidence") for e in _ci),
      "uma travessia que sobra tem de conseguir dizer POR QUE existe")

# E o portao continua a valer: a mudanca de familia nao pode ter aberto porta.
prova("nenhum_dado_atravessa_para_a_inteligencia_depois_do_rehome",
      not [e for e in _ci if e.get("categoria") == "DATA"],
      "mudar a arrumacao nao pode criar autorizacao que nao existia")


print()
if falhas:
    print(f"TESTES_SYSTEM_MAP=FAIL · {len(falhas)} reprovada(s): {', '.join(falhas)}")
    raise SystemExit(1)
print("TESTES_SYSTEM_MAP=PASS")
