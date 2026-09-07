#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · GERADOR

Junta duas coisas que nunca podem virar uma so:

    architecture.generated.json   o que a MAQUINA mediu no repositorio
    architecture.declared.json    o que o HUMANO declarou (nome, frase, departamento)

e produz `state.generated.json`, que e o que a tela le.

    DECLARACAO NAO PROMOVE A VERDE.

O humano pode escrever que A alimenta B. Se o scanner nao achou linha nenhuma
provando, a aresta aparece como EXPECTED, em cinza, com o motivo escrito. O
contrario tambem vale: o scanner pode achar um import que ninguem declarou —
ele entra no mapa na mesma, porque e um fato.

COMO O STATUS NASCE
-------------------
Nao ha escolha. Ha regra, e ela e diferente por tipo de peca, porque exigir a
mesma prova de um teste e de um artefacto seria exigir o impossivel de um deles:

    VERDE     a prova propria do tipo passou E a descricao humana ainda vale
    AMARELO   existe e esta ligado, mas falta a prova propria do tipo
              (ou o ficheiro mudou depois de a descricao ter sido carimbada)
    VERMELHO  foi declarado e nao existe no repositorio
    CINZA     existe e nada aponta para ele, nem ele aponta para nada — NAO SEI

VERDE NUNCA SIGNIFICA "O FICHEIRO EXISTE". Existir e o minimo para nao ser
vermelho, nao um motivo para ser verde.

O CARIMBO (--stamp)
-------------------
Grava em DECLARED_BLOBS o SHA de cada ficheiro no momento em que um humano leu
e declarou aquele componente. Depois disso, se o ficheiro mudar, o gerador
rebaixa o componente para AMARELO com o motivo "mudou depois da declaracao".
E o unico mecanismo que impede verde velho de sobreviver a mudanca.
"""

import fnmatch
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "system-map" / "data"
GERADO = DADOS / "architecture.generated.json"
DECLARADO = DADOS / "architecture.declared.json"
ESTADO = DADOS / "state.generated.json"

VERDE, AMARELO, VERMELHO, CINZA = "PROVEN", "PENDING", "BROKEN", "UNKNOWN"


def carregar(p: Path) -> dict:
    if not p.exists():
        print(f"FALTA={p.relative_to(RAIZ)} · corra scan_repo.py primeiro", file=sys.stderr)
        raise SystemExit(2)
    return json.loads(p.read_text(encoding="utf-8"))


def casa(caminho: str, padrao: str) -> bool:
    """`**` cobre subpasta; `*` sozinho nao atravessa barra.

    fnmatch trata `*` como coringa que come `/` tambem, o que faria
    `italia-portale/client/*.html` capturar ficheiro de subpasta que nao e
    daquele componente. Por isso o caso sem `**` e comparado segmento a segmento.
    """
    if "**" in padrao:
        return fnmatch.fnmatch(caminho, padrao.replace("**", "*"))
    if padrao.count("/") != caminho.count("/"):
        return False
    return fnmatch.fnmatch(caminho, padrao)


# ─────────────────────────────────────────────────────────────────────────────
# A prova exigida de cada tipo de peca
# ─────────────────────────────────────────────────────────────────────────────
def prova_do_tipo(kind: str, ent: list, sai: list, tem_teste: bool) -> tuple[bool, str]:
    """Devolve (passou, frase que explica em portugues comum)."""
    corre = any(e["type"] == "RUNS" for e in ent)
    importado = any(e["type"] == "IMPORTS" for e in ent)
    lido = any(e["type"] in ("READS", "IMPORTS") for e in ent)

    if kind in ("engine", "chain"):
        if corre:
            return True, "algum workflow ou a cadeia canonica manda rodar isto."
        if importado:
            return True, "outra peca do sistema importa isto para funcionar."
        if tem_teste:
            return True, "existe teste que exercita isto."
        return False, "existe, mas nada no repositorio manda rodar nem importa — pode estar desligado."

    if kind == "contract":
        if tem_teste:
            return True, "existe teste que exercita esta lei."
        if importado:
            return True, "o motor importa esta lei para decidir."
        return False, "e uma lei sem prova executavel apontando para ela."

    if kind == "gate":
        if corre or importado:
            return True, "esta no caminho: alguem o chama antes de publicar."
        if any(e["type"] == "IMPORTS" for e in sai):
            return False, "importa coisas, mas ninguem o chama — portao fora do caminho nao guarda nada."
        return False, "portao que ninguem chama."

    if kind == "library":
        # LER conta tanto quanto IMPORTAR. O extrato do Design System nao e
        # `import`ado por ninguem: as paginas o puxam com <link href>. Exigir
        # `IMPORTS` marcava de amarelo uma peca que esta provadamente em uso —
        # regra errada produz status errado com a mesma cara de status certo.
        if lido:
            return True, "outras pecas importam ou carregam isto."
        return False, "biblioteca que ninguem importa nem carrega."

    if kind == "workflow":
        if any(e["type"] == "RUNS" for e in sai):
            return True, "este workflow manda rodar script do repositorio."
        return False, "workflow que nao chama nenhum script deste repositorio."

    if kind == "test":
        if sai:
            return True, "o teste aponta para codigo real do repositorio."
        return False, "teste que nao toca em nada do repositorio."

    if kind == "surface":
        if lido or sai:
            return True, "a superficie carrega dado ou codigo do repositorio."
        return False, "superficie sem ligacao provada com o dado que deveria mostrar."

    if kind == "artifact":
        if lido:
            return True, "algum portao ou pagina le este artefacto."
        return False, "artefacto que ninguem le — pode ser sobra."

    return False, "tipo de peca sem regra de prova definida."


# ─────────────────────────────────────────────────────────────────────────────
# O DESENHO — calculado aqui, nunca na tela
# ─────────────────────────────────────────────────────────────────────────────
# A tela recebe x e y prontos. E de proposito: layout calculado no browser muda
# com a largura da janela, e duas pessoas a olhar o mesmo commit veriam mapas
# diferentes. Aqui e deterministico — mesmo estado, mesmo desenho, sempre.
#
# O ESPACO E O QUE TORNA A LIGACAO LEGIVEL. Cartoes encostados fazem as setas
# passar por cima uns dos outros e o mapa deixa de responder a unica pergunta
# que interessa: o que liga a o que. Por isso as folgas abaixo sao largas, e o
# mundo fica grande — para isso ha pan, zoom e minimapa.
NO_L, NO_A = 285, 132          # tamanho do cartao
GAP_Y, GAP_X = 190, 130         # entre cartoes: respiro para a seta passar
ZONA_PAD, ZONA_CAB = 60, 110    # margem interna e cabecalho da zona
ZONA_GAP = 300                 # entre zonas: a fronteira tem de se ver
TOPO = 190


def linhagem() -> list:
    """As pecas da zona LINHAGENS E DONOS.

    Nao sao codigo: sao FACTOS sobre quem manda. E por isso nao podem ser
    inventadas nem escritas a mao. Vem de dois sitios que se podem apontar:

      · `italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json`, onde o proprio
        repositorio declara qual e a linhagem geradora, o commit dela e o
        BUILD_ID esperado — e diz, por escrito, que a inteligencia tem UM dono;
      · o `git` desta arvore, para a branch e o HEAD de quem esta a consumir.

    Se o contrato desaparecer, esta zona fica com o que o git prova e nada mais.
    NAO SEI e melhor do que um dono inventado.
    """
    contrato = RAIZ / "italia-portale" / "audit" / "CANONICAL-PACKAGE-CONTRACT.json"
    saida = []

    def no(id_, nome, tipo, icon, status, what, why, files, evidence, reason,
           proof="document"):
        # PROOF diz QUE TIPO de prova sustenta esta peca. As de codigo provam-se
        # por aresta; estas nao — um facto sobre quem manda nao e importado por
        # ninguem. Ou vem de um DOCUMENTO nomeado e versionado, ou vem de uma
        # MEDICAO do proprio git. O campo obriga a dizer qual, e o validador
        # recusa verde sem um dos dois. "Eu sei" nao e um valor aceite.
        reais = [f for f in files if (RAIZ / f).exists()]
        factos = [f for f in files if f not in reais]
        saida.append({"id": id_, "name": nome, "kind": tipo, "icon": icon,
                      "facts": factos, "proof": proof,
                      "territory": "Z-LINEAGE", "status": status,
                      "ui_status": {"PROVEN": "green", "PENDING": "yellow",
                                    "BROKEN": "red", "UNKNOWN": "gray"}[status],
                      "what": what, "why_here": why, "files": reais,
                      "file_count": len(reais), "status_reason": reason,
                      "evidence_text": evidence, "departments": ["ENGENHARIA"],
                      "views": ["lineage", "official"], "lane": "official",
                      "legacy": False, "changed_since_declared": [],
                      "inbound": [], "outbound": []})

    def git_(*a):
        return subprocess.run(["git", "-C", str(RAIZ), *a], capture_output=True,
                              text=True, encoding="utf-8", errors="replace").stdout.strip()

    ramo, head = git_("rev-parse", "--abbrev-ref", "HEAD"), git_("rev-parse", "HEAD")
    no("lineage_consumer", "Linha que consome (esta arvore)", "branch consumidora", "B",
       VERDE,
       "E a branch onde este mapa foi medido. Ela consome inteligencia; nao e dona do gerador.",
       "Separar consumidor de gerador impede que a linha do portal reescreva inteligencia com uma cadeia atrasada.",
       [f"branch {ramo}", f"HEAD {head}"],
       "Medido pelo proprio git desta arvore no momento em que o mapa foi gerado.",
       "o git prova a branch e o commit; nao ha aqui nada declarado a mao.",
       proof="git-measurement")

    if not contrato.exists():
        no("lineage_generator", "Linha geradora", "branch geradora", "A", CINZA,
           "Quem e o dono do pacote canonico.", "A inteligencia tem um dono so.",
           [], "", "⚪ NAO SEI: o contrato canonico nao esta nesta arvore.")
        return saida

    C = json.loads(contrato.read_text(encoding="utf-8"))
    G = C.get("CANONICAL_GENERATOR", {})
    rel = "italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json"
    no("lineage_generator", "Linha geradora canonica", "branch geradora", "A", VERDE,
       f"E o dono do pacote canonico: {G.get('LINHAGEM', '?')}.",
       G.get("PORQUE", "A inteligencia tem um dono so."),
       [f"branch {G.get('LINHAGEM', '?')}", f"COMMIT {G.get('COMMIT', '?')}", rel],
       f"{rel} declara esta linhagem como CANONICAL_GENERATOR.",
       "o proprio repositorio declara este dono, por escrito, num contrato versionado.")
    no("lineage_package", "Pacote canonico esperado", "artefato", "◫", VERDE,
       f"O unico BUILD_ID que pode atravessar para o site: {C.get('EXPECTED_BUILD_ID', '?')}.",
       "Um pacote que nao prova a sua identidade nao chega ao cliente.",
       [f"EXPECTED_BUILD_ID {C.get('EXPECTED_BUILD_ID', '?')}", rel],
       C.get("PORQUE_FAIL_CLOSED", "")[:200],
       "esta escrito no contrato e o portao da build recusa qualquer outro.")
    stale = C.get("STALE_KNOWN_BUILD_IDS", {})
    if stale:
        no("lineage_stale", f"Safras atrasadas conhecidas ({len(stale)})", "artefato vencido",
           "✕", AMARELO,
           "Pacotes que ja existiram e que o portao reconhece para RECUSAR.",
           "Saber o nome do errado e o que permite recusa-lo. Sem esta lista, uma safra velha passava com cara de nova.",
           [f"{k} — {v[:70]}" for k, v in stale.items()] + [rel],
           "cada um destes BUILD_IDs esta nomeado no contrato como conhecido-e-recusado.",
           "existem e estao barrados de proposito — nao e defeito, e memoria.")
    return saida


def desenhar(zonas: list, nos: list) -> tuple[list, list, int, int]:
    """Coloca cada peca numa coluna, e cada zona lado a lado, da esquerda para a
    direita — que e a direcao em que o dado corre: fonte → motor → pacote → tela."""
    por_zona: dict[str, list] = {z["id"]: [] for z in zonas}
    for n in nos:
        por_zona.get(n["territory"], []).append(n)

    x = ZONA_GAP
    caixas = []
    for z in zonas:
        membros = sorted(por_zona[z["id"]], key=lambda n: n["id"])
        # Zonas grandes ganham colunas em vez de virarem uma tira infinita.
        cols = 1 if len(membros) <= 5 else (2 if len(membros) <= 12 else 3)
        linhas = -(-len(membros) // cols) if membros else 1
        larg = ZONA_PAD * 2 + cols * NO_L + (cols - 1) * GAP_X
        alt = ZONA_CAB + ZONA_PAD * 2 + linhas * NO_A + max(0, linhas - 1) * GAP_Y
        for i, n in enumerate(membros):
            n["x"] = x + ZONA_PAD + (i % cols) * (NO_L + GAP_X)
            n["y"] = TOPO + ZONA_CAB + ZONA_PAD + (i // cols) * (NO_A + GAP_Y)
        caixas.append({**z, "x": x, "y": TOPO, "w": larg, "h": alt, "count": len(membros)})
        x += larg + ZONA_GAP

    altura = max(c["y"] + c["h"] for c in caixas) + ZONA_GAP
    for c in caixas:
        c["h"] = altura - TOPO - ZONA_GAP  # todas as zonas com a mesma altura
    return caixas, nos, x, altura


def construir(estado: dict) -> None:
    """Publica a app dentro do que a Vercel serve, numa rota SEPARADA.

    `vercel.json` serve `italia-portale/client`. Por isso o mapa vai para
    `italia-portale/client/system-map/` e sai em `/system-map/` — ao lado da
    experiencia do cliente, nunca dentro dela, e reutilizando o deploy que ja
    existe em vez de criar infraestrutura paralela.

    O `.vercelignore` continua a barrar /build /data /docs /handoff. O que sai
    daqui e so nome de ficheiro, ligacao e status: nenhum dado de cliente,
    nenhum segredo, nenhum conteudo de pacote.
    """
    destino = RAIZ / "italia-portale" / "client" / "system-map"
    destino.mkdir(parents=True, exist_ok=True)
    # Os ficheiros sao NOMEADOS, e nao varridos da pasta. Varrer copiava em
    # silencio o que la estivesse — um rascunho, uma sobra — e faltava em
    # silencio o que nao estivesse. Nomear falha alto quando falta.
    for nome in ("system-map/app/index.html", "system-map/app/map.js",
                 "system-map/app/map.css"):
        origem = RAIZ / nome
        if not origem.exists():
            print(f"FALTA={nome} · a app esta incompleta", file=sys.stderr)
            raise SystemExit(2)
        shutil.copyfile(origem, destino / Path(nome).name)
    (destino / "state.generated.json").write_text(
        json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
def main_uma_vez(stamp: bool) -> int:
    G, D = carregar(GERADO), carregar(DECLARADO)

    arquivos = {f["path"]: f for f in G["FILES"]}
    comps = D["COMPONENTS"]

    # ── 1 · que ficheiro pertence a que componente ───────────────────────────
    # Um ficheiro so pode ter UM dono. Dois donos seria duas verdades sobre a
    # mesma linha de codigo. O primeiro que reivindica fica com ele, e o
    # validador reprova conflito.
    dono: dict[str, str] = {}
    conflitos: list[dict] = []
    for c in comps:
        c["_files"] = []
        fora = c.get("exclude", [])
        for padrao in c["files"]:
            for caminho in arquivos:
                if any(casa(caminho, x) for x in fora):
                    continue  # pertence a outro componente, declarado a mao
                if casa(caminho, padrao):
                    if caminho in dono and dono[caminho] != c["id"]:
                        conflitos.append({"file": caminho, "claimed_by": [dono[caminho], c["id"]]})
                        continue
                    dono[caminho] = c["id"]
                    c["_files"].append(caminho)
        c["_files"] = sorted(set(c["_files"]))

    # ── 2 · arestas de ficheiro sobem para arestas de componente ─────────────
    # Cada aresta de componente carrega TODAS as linhas que a provam. E o que
    # responde "por que existe esta seta?" com dedo apontado, nao com opiniao.
    ligacoes: dict[tuple, dict] = {}
    for e in G["FILE_EDGES"]:
        a, b = dono.get(e["from_file"]), dono.get(e["to_file"])
        if not a or not b or a == b:
            continue
        chave = (a, b, e["type"])
        alvo = ligacoes.setdefault(chave, {
            "from": a, "to": b, "type": e["type"], "payload": e["payload"],
            "kind": "technical", "status": VERDE,
            "reason": "", "evidence": [],
        })
        alvo["evidence"].append(e["evidence"])

    for lig in ligacoes.values():
        n = len(lig["evidence"])
        verbo = {"IMPORTS": "importa", "READS": "le", "WRITES": "escreve em",
                 "RUNS": "manda rodar"}.get(lig["type"], lig["type"].lower())
        de = next(c["name"] for c in comps if c["id"] == lig["from"])
        para = next(c["name"] for c in comps if c["id"] == lig["to"])
        lig["reason"] = (f"{de} {verbo} {para}. Provado por {n} "
                         f"linha{'s' if n > 1 else ''} de codigo.")
        lig["evidence"] = sorted(lig["evidence"], key=lambda x: (x["file"], x["line"]))[:12]

    # ── 3 · arestas declaradas que a maquina NAO provou ──────────────────────
    for d in D.get("EXPECTED_EDGES", []):
        chave = (d["from"], d["to"], d["type"])
        if chave in ligacoes:
            ligacoes[chave]["declared_reason"] = d.get("reason", "")
            continue
        ligacoes[chave] = {
            **d, "kind": "expected", "status": CINZA, "evidence": [],
            "reason": (d.get("reason", "") +
                       "  ⚪ NAO SEI: isto foi declarado por gente, e o scanner nao "
                       "achou nenhuma linha de codigo que prove."),
        }

    # ── 4 · status de cada componente ────────────────────────────────────────
    blobs_declarados = D.get("DECLARED_BLOBS", {})
    novos_blobs: dict[str, str] = {}
    nos = []
    for c in comps:
        fs = c["_files"]
        ent = [l for l in ligacoes.values() if l["to"] == c["id"] and l["kind"] == "technical"]
        sai = [l for l in ligacoes.values() if l["from"] == c["id"] and l["kind"] == "technical"]
        tem_teste = any(l["from"] == "C-TESTES" or l["from"] == "C-MAPA-TESTES" for l in ent)

        for f in fs:
            novos_blobs[f] = arquivos[f]["sha"]

        if not fs:
            status, motivo = VERMELHO, ("declarado no mapa e nao existe no repositorio: "
                                        f"nenhum ficheiro casa com {', '.join(c['files'])}.")
        elif not ent and not sai:
            status, motivo = CINZA, ("⚪ NAO SEI. Os ficheiros existem, mas nada no "
                                     "repositorio aponta para eles e eles nao apontam para "
                                     "nada. Nao da para provar o que isto faz hoje.")
        else:
            passou, frase = prova_do_tipo(c["kind"], ent, sai, tem_teste)
            status, motivo = (VERDE, frase) if passou else (AMARELO, frase)

        # ── o carimbo: descricao velha nao segura verde ──────────────────────
        mudou = sorted(f for f in fs
                       if f in blobs_declarados and blobs_declarados[f] != arquivos[f]["sha"])
        nunca = [f for f in fs if f not in blobs_declarados] if blobs_declarados else []
        if status == VERDE and (mudou or nunca):
            status = AMARELO
            if mudou:
                motivo = (f"{motivo}  Mas {len(mudou)} ficheiro(s) mudaram depois de a "
                          "descricao ter sido conferida — precisa de releitura humana.")
            else:
                motivo = (f"{motivo}  Mas ha {len(nunca)} ficheiro(s) novos que nunca foram "
                          "lidos por gente.")

        nos.append({
            "id": c["id"], "name": c["name"], "territory": c["territory"],
            "kind": c["kind"], "what": c["what"], "why_here": c["why_here"],
            "departments": c.get("departments", []),
            "legacy": bool(c.get("legacy")),
            # ── campos que a tela consome, no vocabulario dela ──────────────
            # verde/amarelo/vermelho/cinza e a leitura humana; PROVEN/PENDING/
            # BROKEN/UNKNOWN e a leitura da maquina. Sao a MESMA decisao, dita
            # duas vezes — a traducao mora aqui e nao no browser, para nao haver
            # um segundo sitio onde alguem possa mudar o significado de verde.
            "ui_status": {"PROVEN": "green", "PENDING": "yellow",
                          "BROKEN": "red", "UNKNOWN": "gray"}[status],
            "icon": c.get("icon", "●"),
            "views": sorted(set(c.get("views", []))
                            | set(next(t.get("views", []) for t in D["TERRITORIES"]
                                       if t["id"] == c["territory"]))),
            "lane": "legacy" if c.get("legacy") else "official",
            "files": fs, "file_count": len(fs),
            "status": status, "status_reason": motivo,
            "changed_since_declared": mudou,
            "inbound": sorted({l["from"] for l in ent}),
            "outbound": sorted({l["to"] for l in sai}),
        })

    # ── 5 · o que o mapa NAO cobre — dito na cara, nao escondido ─────────────
    orfaos_de_codigo = sorted(p for p, f in arquivos.items()
                              if f["code_dir"] and f["readable"] and p not in dono)
    nao_reivindicados = sorted(p for p in arquivos if p not in dono)

    nos = nos + linhagem()
    zonas, nos, mundo_w, mundo_h = desenhar(D["TERRITORIES"], nos)

    # INVENTARIO: os ficheiros rastreados, agrupados pela pasta de topo. E o que
    # responde "o mapa esta a olhar para o meu repositorio todo?" sem obrigar
    # ninguem a acreditar na palavra do mapa.
    inventario: dict[str, list] = {}
    for caminho in sorted(arquivos):
        grupo = caminho.split("/")[0] if "/" in caminho else "(raiz)"
        inventario.setdefault(grupo, []).append(caminho)

    estado = {
        "SCHEMA": "sintonia.system-map.state/1",
        "WORLD": {"w": mundo_w, "h": mundo_h},
        "INVENTORY": inventario,
        "PROVENANCE": G["PROVENANCE"],
        "TERRITORIES": zonas,
        "DEPARTMENTS": D["DEPARTMENTS"],
        "NODES": sorted(nos, key=lambda n: n["id"]),
        "EDGES": sorted(ligacoes.values(), key=lambda l: (l["from"], l["to"], l["type"])),
        "BUSINESS_EDGES": D.get("BUSINESS_EDGES", []),
        "UNCLAIMED_CODE_FILES": orfaos_de_codigo,
        "UNCLAIMED_FILES_COUNT": len(nao_reivindicados),
        "OWNERSHIP_CONFLICTS": conflitos,
    }

    st = [n["status"] for n in nos]
    et = [l["status"] for l in estado["EDGES"]]
    estado["COUNTS"] = {
        "components": len(nos),
        "components_proven": st.count(VERDE), "components_pending": st.count(AMARELO),
        "components_broken": st.count(VERMELHO), "components_unknown": st.count(CINZA),
        "edges": len(estado["EDGES"]),
        "edges_proven": et.count(VERDE), "edges_unknown": et.count(CINZA),
        "business_edges": len(estado["BUSINESS_EDGES"]),
        "files_tracked": G["COUNTS"]["files_tracked"],
        "files_covered": len(dono),
        "files_code_unclaimed": len(orfaos_de_codigo),
    }

    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    construir(estado)

    if stamp:
        D["DECLARED_BLOBS"] = dict(sorted(novos_blobs.items()))
        for c in D["COMPONENTS"]:
            c.pop("_files", None)
        DECLARADO.write_text(json.dumps(D, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"CARIMBO=OK · {len(novos_blobs)} ficheiros carimbados como lidos por gente")
        # SEGUNDA PASSAGEM, ate ao ponto fixo. Carimbar MUDA a entrada do calculo:
        # um ficheiro que nao tinha carimbo deixa de segurar a peca em amarelo.
        # Sem esta passagem o estado escrito seria o de ANTES do carimbo, e a
        # proxima corrida do validador acusaria drift sobre uma mudanca que ja
        # tinha acontecido — o portao a reprovar por um trabalho ja feito.
        # (E o mesmo ponto fixo que `v21_cadeia.sh` mede no BUILD_ID.)
        #
        # E preciso RE-ESCANEAR antes: `architecture.declared.json` e uma ENTRADA
        # medida pelo scanner, e o carimbo acabou de a reescrever. Sem este passo
        # o mapa ficaria a citar o SHA da versao anterior do proprio ficheiro que
        # o carimbo mudou — e o validador acusaria drift no commit seguinte.
        subprocess.run([sys.executable, str(Path(__file__).with_name("scan_repo.py"))],
                       check=True, capture_output=True)
        return main_uma_vez(stamp=False)

    c = estado["COUNTS"]
    print(f"MAPA=OK · HEAD={estado['PROVENANCE']['HEAD'][:8]} · pecas={c['components']} "
          f"(🟢{c['components_proven']} 🟡{c['components_pending']} "
          f"🔴{c['components_broken']} ⚪{c['components_unknown']}) "
          f"· ligacoes={c['edges']} · cobertura={c['files_covered']}/{c['files_tracked']} ficheiros")
    return 0


def main() -> int:
    return main_uma_vez(stamp="--stamp" in sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
