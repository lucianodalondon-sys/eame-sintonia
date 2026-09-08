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
PARTES_ESPERADAS = ["F-COLETA", "F-ESPERA", "F-INTELIGENCIA", "F-ENTREGA"]
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

# E2 · a receita continua, e so o orquestrador DECIDE a partir dela
#
#     LER PARA CONTAR NAO E CONSUMIR PARA DECIDIR.
#
# A lei aqui e que a escolha de rota nao se espalhe: quem decide qual executor
# corre e o orquestrador, e mais ninguem. Um censo que abre o ficheiro para
# CONTAR quantos executores estao declarados nao decide nada — e foi essa
# medicao que denunciou a G-05 (18 executores medidos, 4 declarados). Proibi-la
# seria proibir medir a propria lacuna.
#
# A distincao NAO fica no nome da peca: fica provada em E2b, que exige que quem
# so conta nao IMPORTE a receita. Sem isso, esta lista seria uma porta larga.
# SAO TRES ESPECIES, E NAO DUAS. Escrevi duas primeiro e o teste apanhou-me:
# `testa_coleta_canonica.py` IMPORTA a receita e chama o `resolver` — e faz
# bem, e a prova de que a resolucao funciona. Nao e «so contar».
#
#     DECIDE   escolhe qual executor corre.            Um so.
#     PROVA    importa e chama, para provar que resolve.
#     CONTA    abre como TEXTO, para medir. Nao importa.
rec = POR_ID_N.get("C-RECEITAS")
DECIDEM = {"C-ORQUESTRADOR"}
PROVAM = {"C-PROVA-COLETA"}
SO_CONTAM = {"C-CENSO-ESTRADAS-IT"}
consumidores = [e["to"] for e in S["EDGES"]
                if e["from"] == "C-RECEITAS" and e.get("kind") == "technical"]
prova("E2_receita_continua_com_um_consumidor",
      bool(rec) and set(consumidores) <= (DECIDEM | PROVAM | SO_CONTAM),
      f"consumidores da receita: {sorted(set(consumidores))}")

# E2b · quem so conta, nao importa
_ficheiros_que_so_contam = []
for _id in SO_CONTAM:
    _p = POR_ID_N.get(_id) or {}
    _ficheiros_que_so_contam += [f for f in (_p.get("files") or [])
                                 if f.endswith(".py")]
_importam = []
for _f in _ficheiros_que_so_contam:
    _cam = RAIZ / _f
    if not _cam.is_file():
        continue
    for _linha in _cam.read_text(encoding="utf-8").splitlines():
        _nu = _linha.strip()
        if _nu.startswith(("import ", "from ")) and "receitas" in _nu:
            _importam.append(_f)
prova("E2b_quem_so_conta_nao_importa_a_receita",
      not _importam,
      f"importam a receita: {sorted(set(_importam))}")

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

print()
if falhas:
    print(f"TESTES_SYSTEM_MAP=FAIL · {len(falhas)} reprovada(s): {', '.join(falhas)}")
    raise SystemExit(1)
print("TESTES_SYSTEM_MAP=PASS")
