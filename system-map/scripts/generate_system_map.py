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
import re
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
FAM_TOPO, FAM_PAD = 60, 40      # a faixa da familia abraca as zonas dela


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
                      "family": "F-INTELIGENCIA",
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


def termos_de_busca() -> list:
    """As palavras que a coleta realmente digita, medidas por ."""
    f = DADOS / "sources.generated.json"
    return json.loads(f.read_text(encoding="utf-8"))["SEARCH_TERMS"] if f.exists() else []


def as_fontes() -> tuple[list, list]:
    """AS FONTES sao UMA peca, nao vinte e tres.

    Vinte e tres cartoes lado a lado nao respondem "de onde vem o dado?" — eles
    empurram a pergunta para depois de o leitor decorar vinte e tres nomes. O que
    interessa saber, de longe, e que existe UM sitio chamado AS FONTES. A lista
    inteira mora dentro dele, agrupada como esta casa ja a organiza:

        BASES OFICIAIS E ABERTAS   as fichas do atlas, por pais
        INSTAGRAM · LINKEDIN ·     as contas publicas do concorrente, por
        YOUTUBE · FACEBOOK         plataforma, com a autorizacao de cada uma

    Sao dois registos diferentes no repositorio, e continuam a ser — uma base
    regulatoria e uma pagina de Instagram sao fontes de naturezas diferentes. Mas
    para quem olha o mapa sao a mesma pergunta, e por isso aparecem no mesmo sitio.

    ESTE E O CAPITAL PARADO DA CASA. Consulta-se antes de coletar; nao se coleta
    para descobrir o que ja se sabe. E por isso tem porta de entrada propria: fonte
    nova que aparece no meio de uma coleta entra aqui, e so depois entra no fluxo.

    O ESTADO NAO E UMA MEDIA. Obedece a regra de sempre: verde exigiria que a
    maquina soubesse ir buscar sozinha em todas. Enquanto houver fonte sem contrato
    de busca, isto e amarelo — e o motivo diz quantas.
    """
    f = DADOS / "sources.generated.json"
    if not f.exists():
        return [], []
    S = json.loads(f.read_text(encoding="utf-8"))
    c, contas = S["COUNTS"], S.get("ACCOUNTS", {})

    marca = {"GREEN": "verificada, com exemplo real guardado",
             "YELLOW": "real, mas com atrito registrado",
             "RED": "verificada e descartada, com motivo escrito",
             "NAO SEI": "nao foi possivel verificar — NAO SEI"}

    grupos = [{
        "titulo": "BASES OFICIAIS E ABERTAS",
        "subtitulo": (f"{c['sources']} fichas no atlas · {c['with_contract']} com "
                      f"contrato de busca escrito"),
        "porque": ("Registro publico, dado aberto, base regulatoria, estatistica e "
                   "ciencia. Fonte que nao depende de ninguem ter postado."),
        "onde": S["PROVENANCE"]["ATLAS"],
        "itens": [{
            "id": x["source_id"], "nome": x["name"], "pais": x["country"],
            "assunto": f"{x['territory']} · {x['territory_name']}",
            "estado": x["verdict"], "estado_texto": marca.get(x["verdict"], ""),
            "sabe_coletar": x["sabe_coletar"],
            "como_se_entra": (x.get("access_method") or "")[:180],
            "dono": x.get("owner", ""),
            "url": (x.get("url") or "").split()[0] if x.get("url") else "",
            "atualiza": (x.get("update_frequency") or "")[:90],
            "exemplo": (x.get("real_example") or "")[:300],
            "contrato": x.get("contract"),
        } for x in S["SOURCES"]],
    }]

    for plat, g in (contas.get("por_plataforma") or {}).items():
        grupos.append({
            "titulo": plat,
            "subtitulo": f"{g['total']} contas mapeadas · {g['autorizadas']} autorizadas a coletar",
            "porque": ("Pagina publica do concorrente. Estar na lista NAO e autorizacao: "
                       "so entra na coleta quem tem identidade PROVADA e e conta local do pais."),
            "onde": contas.get("file", ""),
            "itens": [{
                "id": (i.get("handle") or i.get("url", ""))[:60],
                "nome": f"{i['empresa']} · {i['pais']}",
                "pais": i["pais"], "assunto": "comunicacao publica",
                "estado": "GREEN" if i["autorizada"] else "NAO SEI",
                "estado_texto": ("autorizada a coletar" if i["autorizada"]
                                 else "fora da coleta — " + (i["porque"] or "sem motivo escrito")),
                "sabe_coletar": i["autorizada"], "url": i.get("url", ""),
                "como_se_entra": "rota paga Apify, so depois de o contrato do ator passar",
                "dono": i["empresa"], "atualiza": "", "exemplo": "", "contrato": None,
            } for i in g["contas"]],
        })

    sem_contrato = c["sources"] - c["with_contract"]
    motivo = (
        f"{c['sources']} bases oficiais com ficha e {contas.get('total', 0)} contas "
        f"publicas mapeadas. Mas so {c['with_contract']} das bases tem contrato de "
        f"busca escrito: nas outras {sem_contrato}, hoje so uma pessoa consegue ir "
        f"la — a maquina nao. Enquanto isso for verdade, isto nao pode ser verde."
    )
    arquivos = [S["PROVENANCE"]["ATLAS"], S["PROVENANCE"]["CONTRATOS"]]
    if contas.get("file"):
        arquivos.append(contas["file"])

    no = {
        "id": "C-AS-FONTES", "name": "AS FONTES", "kind": "fonte", "icon": "◫",
        "territory": "Z-FONTES", "family": "F-COLETA",
        "status": AMARELO if sem_contrato else VERDE,
        "ui_status": "yellow" if sem_contrato else "green",
        "proof": "document",
        "what": (f"O capital parado da casa: {c['sources']} bases oficiais e abertas, "
                 f"mais {contas.get('total', 0)} contas publicas do concorrente em "
                 f"{len(contas.get('por_plataforma') or {})} plataformas. Consulta-se "
                 f"antes de coletar."),
        "why_here": ("Nada existe no SINTONIA sem passar por aqui primeiro. Uma fonte so "
                     "entra depois de alguem a abrir, olhar o que ela entrega e guardar "
                     "evidencia disso — e coleta nenhuma comeca sem consultar o que ja "
                     "esta aqui."),
        "files": [a for a in arquivos if (RAIZ / a).is_file()],
        "facts": [f"bases oficiais com ficha: {c['sources']}",
                  f"dessas, a maquina sabe buscar sozinha: {c['with_contract']}",
                  f"contas publicas mapeadas: {contas.get('total', 0)}",
                  f"dessas, autorizadas a coletar: {contas.get('autorizadas', 0)}",
                  f"palavras de busca medidas no codigo: {c['search_terms']}",
                  f"enderecos que o codigo realmente chama: {c['endpoints']}"],
        "status_reason": motivo,
        "evidence_text": "",
        "departments": [], "views": ["acervo"], "lane": "official", "legacy": False,
        "changed_since_declared": [], "inbound": [], "outbound": [],
        "groups": grupos,
        "header_claim": S.get("HEADER_CLAIM"),
        "runs": S.get("COLETAS_FEITAS"),
        "memoria": S.get("MEMORIA_DA_COLETA"),
        "intake": S.get("INTAKE"),
    }
    no["file_count"] = len(no["files"])

    # A seta para quem vai la buscar. Uma so por componente de destino, com todas
    # as linhas de contrato que a provam empilhadas dentro.
    ligacoes = []
    for x in S["SOURCES"]:
        k = x.get("contract")
        if not k:
            continue
        for cand in re.findall(r"scripts/[\w./-]+\.(?:py|sh|mjs)",
                               k.get("retrieval_method", "")):
            if (RAIZ / cand).is_file():
                ligacoes.append({
                    "to_file": cand, "source_id": x["source_id"],
                    "evidence": {"file": CONTRATOS_REL, "line": k["evidence"]["line"],
                                 "snippet": f"{x['source_id']} RETRIEVAL_METHOD "
                                            f"{k['retrieval_method'][:90]}"},
                })
    return [no], ligacoes


CONTRATOS_REL = "docs/operacao/CONTRATOS-DAS-FONTES-EAME.md"

# O NOME DA FERRAMENTA E ITALIANO PORQUE O PORTAL E ITALIANO. Quem abre a tela
# le «Radar delle Opportunita», e trocar isso no mapa obrigaria a pessoa a
# traduzir de cabeca toda vez que passasse de um ecra para o outro. Entao o
# cartao mostra os dois: o nome que esta la, e o que ele quer dizer.
#
# ISTO E TRADUCAO MINHA, NAO MEDICAO. E a unica linha deste ficheiro que nao
# saiu do repositorio — esta aqui em cima, curta, para se poder discordar dela
# sem procurar.
EM_PORTUGUES = {
    "meeting": "Radar das Oportunidades",
    "future": "Arquivo de sinais",
    "windows": "Janelas de Cultura",
    "market": "Pulso de Mercado",
    "voices": "Vozes do Campo",
    "competitors": "Concorrencia",
    "science": "Inteligencia Cientifica",
    "portfolio": "Portfolio",
    "archive": "Arquivo",
    "sources": "Registo das fontes",
    "field": "Rede Comercial de Campo",
}


def em_bom_portugues(x: dict, ligado: list) -> str:
    """O «o que faz» do cartao, escrito em portugues a partir do que foi MEDIDO.

    O texto do contrato esta em ingles e e longo. Colar esse paragrafo no cartao
    dava uma coisa que quase ninguem desta casa consegue ler de relance — e um
    mapa que so se le com dicionario ao lado nao esta a informar ninguem.

    Traduzir a mao seria pior: criava uma segunda versao do contrato, que
    envelhece sozinha e passa a dizer o que o contrato ja nao diz.

    Entao nao se traduz. Escreve-se do zero, so com numeros medidos, e as
    palavras originais do contrato ficam guardadas ao lado, em ingles, como
    prova — quem quiser conferir tem-nas inteiras.
    """
    n_real = sum(1 for c in ligado if c["tipo"] == "REAL")
    n_can = sum(1 for c in ligado if c["tipo"] == "CANONICO")
    n_fix = sum(1 for c in ligado if c["tipo"] == "FIXTURE")
    pt = EM_PORTUGUES.get(x["vista"], "")

    if not ligado:
        return (f"«{x['nome']}»" + (f" — em portugues, {pt}." if pt else ".")
                + " NAO SEI de onde vem o que ela mostra: nao ha contrato de bloco"
                  " escrito para esta tela, e sem isso nao da para dizer que dado"
                  " esta por baixo dos numeros que ela poe no ecra.")

    partes = []
    if n_real:
        partes.append(f"{n_real} de dado real, com procedencia")
    if n_can:
        partes.append(f"{n_can} de dado real com a lei da casa aplicada")
    if n_fix:
        partes.append(f"{n_fix} escrita a mao, para a tela nao ficar vazia")
    # camada que este mapa ainda nao sabe classificar tambem CONTA. Sem esta
    # linha, «Polso di Mercato» dizia «bebe de 1 camada de dado:» e acabava a
    # frase ali — um cartao a contar uma coisa e a nao dizer qual.
    n_ns = len(ligado) - n_real - n_can - n_fix
    if n_ns:
        partes.append(f"{n_ns} que este mapa ainda nao sabe classificar — NAO SEI "
                      f"se e real ou escrita a mao")

    frase = (f"«{x['nome']}»" + (f" — em portugues, {pt}." if pt else ".")
             + f" Bebe de {len(ligado)} camada(s) de dado: " + "; ".join(partes) + ".")
    if x.get("registos_citados"):
        frase += (" O contrato cita estes tamanhos de dado real por baixo: "
                  + ", ".join(str(n) for n in x["registos_citados"]) + " registos.")
    if n_fix and (n_real or n_can):
        frase += (" Como ha real e escrito a mao na mesma tela, e a tela nao diz "
                  "qual e qual, quem olha nao consegue separar os dois.")
    return frase


# ── OS VEICULOS: POR ONDE SE VAI ────────────────────────────────────────────
# Tres coisas diferentes estavam a viver na mesma gaveta, e o nome dela era o de
# uma delas so:
#     FERRAMENTA  com QUE se viaja   Apify, o navegador, a transcricao
#     VEICULO     por ONDE se vai    YouTube, Instagram, LinkedIn, Facebook
#     ACAO        o que se FAZ la    colher o YouTube, baixar os rotulos
#
# A gaveta chamava-se «OS VEICULOS» e la dentro nao havia um unico veiculo: as
# oito pecas eram todas acoes. E o canal — o veiculo de verdade — nao existia no
# mapa de todo. Nao dava para perguntar «o que e que nos fazemos dentro do
# YouTube?», porque o YouTube nao estava la.
#
# Estes cartoes nao sao escritos a mao: nascem de procurar o canal dentro do
# codigo de cada acao, e cada seta carrega o ficheiro e a linha onde ele aparece.
CANAIS = (
    ("V-YOUTUBE", "YOUTUBE", r"youtube|yt_dlp|youtu\.be",
     "Video publico: o que o canal do concorrente e o do sector poem no ar."),
    ("V-INSTAGRAM", "INSTAGRAM", r"instagram",
     "A pagina publica: o que a marca publica para quem a segue."),
    ("V-LINKEDIN", "LINKEDIN", r"linkedin",
     "A pagina de empresa e a das pessoas: contratacao, evento, anuncio."),
    ("V-FACEBOOK", "FACEBOOK", r"facebook",
     "A pagina publica da marca, ainda viva em varios mercados agricolas."),
    ("V-HTTP", "PEDIDO HTTP DIRETO", r"requests\.|httpx|urllib\.request|aiohttp",
     "O site aberto, sem plataforma pelo meio: base oficial, PDF, pagina, ficheiro."),
)


def os_veiculos(comps: list, dono: dict, G: dict) -> tuple[list, list]:
    """Um cartao por canal, e uma seta de cada acao para o canal que ela usa.

    O ESTADO DIZ SE ALGUEM USA O CANAL, nao se o canal funciona. Verde e «ha
    acao que vai por aqui, e ha linha de codigo que prova». Sem nenhuma acao a
    usa-lo, o canal fica em NAO SEI — que e a verdade: esta declarado e ninguem
    passa por ele.
    """
    import re as _re
    acoes = [c for c in comps if c.get("territory") == "Z-ACOES"]
    nos, ligacoes = [], []

    # ── O QUE UM CANAL RECEBE ────────────────────────────────────────────────
    # Um canal nao recebe dado — recebe A LISTA DE ONDE IR. Sem ela, «colher o
    # YouTube» nao quer dizer nada: colher o YouTube de quem?
    #
    # Essa lista ja existe medida: 44 contas publicas do concorrente, agrupadas
    # por plataforma, cada uma com identidade provada ou rejeitada e o motivo
    # escrito. Enquanto o canal nao a mostrava, ele parecia nascer do nada — e a
    # pergunta «e o que ele recebe?» nao tinha resposta no mapa.
    contas_por_plataforma = {}
    f_fontes = DADOS / "sources.generated.json"
    if f_fontes.is_file():
        _S = json.loads(f_fontes.read_text(encoding="utf-8"))
        contas_por_plataforma = (_S.get("ACCOUNTS") or {}).get("por_plataforma") or {}
        ficheiro_das_contas = (_S.get("ACCOUNTS") or {}).get("file", "")

    for vid, nome, padrao, o_que in CANAIS:
        rx = _re.compile(padrao, _re.I)
        quem, provas = [], []
        for a in acoes:
            for f in a.get("_files", []):
                cam = RAIZ / f
                if not cam.is_file():
                    continue
                try:
                    linhas = cam.read_text(encoding="utf-8", errors="replace").splitlines()
                except OSError:
                    continue
                achou = next(((i, l) for i, l in enumerate(linhas, 1)
                              if rx.search(l) and not l.strip().startswith("#")), None)
                if achou:
                    quem.append(a["id"])
                    provas.append({"acao": a["id"], "veiculo": vid,
                                   "file": f, "line": achou[0],
                                   "snippet": achou[1].strip()[:150]})
                    break

        # ── E O QUE ENTRA POR AQUI, VAI PARAR ONDE? ──────────────────────
        # O cartao dizia «recebe de 3 acoes, envia para ninguem», e isso lia-se
        # como um beco sem saida — como se o canal engolisse o que capta.
        #
        # O canal nao guarda nada, e nunca guardou: quem guarda e a acao que
        # passa por ele. Mas dizer «envia para ninguem» e pior do que nao dizer
        # nada, porque parece uma medicao e e so uma consequencia de o canal nao
        # ser uma peca que escreve.
        #
        # Entao mede-se o que interessa: para cada acao que sai por este canal,
        # ONDE e que ela larga o que trouxe. Nao se inventa seta — a seta
        # continua a ser da acao, que e quem realmente escreve. O canal apenas
        # passa a saber responder a pergunta.
        destinos = []
        for aid in sorted(set(quem)):
            for f in next((c.get("_files", []) for c in comps if c["id"] == aid), []):
                for x in (G.get("ESCRITAS_EM_PASTA") or {}).get(f, []):
                    # duas acoes podem encher a MESMA pasta; o destino e um so
                    ja = {d.get("_chave") for d in destinos}
                    if x["pasta"] not in ja:
                        destinos.append({
                            "_chave": x["pasta"],
                            "acao": aid, "ficheiro": x["pasta"] + "/  (pasta inteira)",
                            "prova": {"file": f, "line": x["line"],
                                      "snippet": f"escreve em {x['constante']}"}})
            for e in G["FILE_EDGES"]:
                if (e["type"] == "WRITES" and dono.get(e["from_file"]) == aid
                        and e["to_file"] not in {d.get("_chave") for d in destinos}):
                    destinos.append({
                        "_chave": e["to_file"],
                        "acao": aid, "ficheiro": e["to_file"],
                        "prova": {"file": e["from_file"],
                                  "line": e.get("line") or 1,
                                  "snippet": e.get("snippet", "")[:120]},
                    })

        # as contas desta plataforma — o que entra no canal antes de sair dele
        plat = nome.split(" ")[0].upper()
        c_plat = contas_por_plataforma.get(plat) or {}
        recebe = {
            "de": "C-AS-FONTES",
            "contas": c_plat.get("total", 0),
            "autorizadas": c_plat.get("autorizadas", 0),
            "ficheiro": ficheiro_das_contas if contas_por_plataforma else "",
            "exemplos": [x.get("handle") for x in (c_plat.get("contas") or [])
                         if x.get("autorizada")][:5],
        } if c_plat else None

        nos.append({
            "id": vid, "name": nome, "kind": "veiculo", "icon": "◈",
            "territory": "Z-VEICULOS", "family": "F-COLETA",
            "status": VERDE if quem else CINZA,
            "ui_status": "green" if quem else "gray",
            "proof": "git-measurement",
            "what": (f"{o_que} Hoje {len(quem)} acao(oes) da coleta passam por aqui."
                     if quem else
                     f"{o_que} Hoje NENHUMA acao passa por aqui."),
            "why_here": ("E por onde a coleta sai de casa. Separar o canal da acao "
                         "permite fazer a pergunta que antes nao tinha onde ser feita: "
                         "o que e que nos fazemos, exatamente, dentro deste canal?"),
            "files": [],
            "facts": ([f"contas publicas mapeadas neste canal: {recebe['contas']}",
                       f"dessas, autorizadas a coletar: {recebe['autorizadas']}"]
                      if recebe else [])
                     + [f"acoes da coleta que passam por aqui: {len(quem)}"]
                     + [f"prova: {p['file']}:{p['line']}" for p in provas[:5]],
            "status_reason": (
                f"{len(quem)} acao(oes) chamam este canal, e cada uma tem ficheiro e "
                f"linha que o prova." if quem else
                "NAO SEI: o canal esta descrito aqui, mas nenhuma acao da coleta o "
                "chama no codigo de hoje. Ou nao se usa, ou usa-se por um caminho "
                "que este mapa ainda nao ve."),
            "evidence_text": "", "departments": [], "views": ["acervo"],
            "lane": "official", "legacy": False, "changed_since_declared": [],
            "inbound": [], "outbound": [], "file_count": 0,
            "o_que_recebe": recebe,
            "o_que_entra_vai_para": destinos,
            # QUEM SAI POR AQUI E NAO DIZ ONDE GUARDA. E a pergunta «o que o
            # YouTube colhe vai pra onde?» aplicada acao a acao: das quatro que
            # saem por ali, duas declaram um destino e duas nao. Sem esta linha,
            # o cartao mostrava os destinos das duas e ficava calado sobre as
            # outras — o que da a impressao de que estao todas cobertas.
            "saem_daqui_sem_destino": sorted(
                a for a in set(quem)
                if a not in {d["acao"] for d in destinos}),
            "nao_guarda_nada": (
                "Um canal nao guarda nada — ele so deixa passar. Quem guarda e a "
                "acao que sai por aqui, e e por isso que este cartao nao tem seta "
                "de saida: a seta e dela, nao dele. Abaixo estao os sitios onde o "
                "que entra por este canal acaba por ficar."
                if destinos else
                "Um canal nao guarda nada — ele so deixa passar. E NAO SEI onde "
                "acaba o que entra por aqui: nenhuma das acoes que o usam declara, "
                "no codigo, um ficheiro onde escreve o que trouxe."),
        })
        ligacoes += provas
        if recebe and recebe["contas"] and recebe["ficheiro"]:
            ligacoes.append({
                "acao": "C-AS-FONTES", "veiculo": vid, "entrega_lista": True,
                "file": recebe["ficheiro"], "line": 1,
                "snippet": (f"{recebe['contas']} conta(s) de {plat} em ficha, "
                            f"{recebe['autorizadas']} autorizada(s) a coletar"),
            })
    return nos, ligacoes


# ── ONDE PARA O QUE SAI DAQUI: GIT OU SUPABASE ──────────────────────────────
# Esta casa tem dois sitios onde uma coisa pode ficar depois de pronta, e sao
# muito diferentes:
#
#     GIT       fica um ficheiro no repositorio. Tem historico: da para ver
#               quem mudou o que e quando, e da para voltar atras.
#     SUPABASE  fica uma linha no banco. E consultavel e cresce sem limite,
#               mas o que estava la ontem nao se recupera olhando o commit.
#
# Nao saber qual dos dois foi usado e o que faz alguem procurar durante uma hora
# um numero que esta no outro lado. Por isso cada cartao passa a dizer.
#
# E DE PROPOSITO QUE ISTO NAO VIRA CARTAO NOVO. Dois cartoes «GIT» e «SUPABASE»
# com trinta e duas setas cada seriam um novelo por cima do mapa, e a pergunta
# «para onde vai o que sai desta peca?» ficaria mais dificil, nao mais facil.
# Fica uma marca pequena no cartao, e a prova no painel de quem clicar.
# PROCURAR A PALAVRA «supabase» NAO SERVE, e esta linha existe por causa disso.
# A primeira versao marcou o «Gerador do System Map» como quem escreve no banco.
# Ele nao escreve la nada — apenas FALA sobre o banco, nestes comentarios aqui em
# cima. Um ficheiro que MENCIONA o banco e um ficheiro que GRAVA no banco sao
# coisas opostas, e confundi-las poe uma etiqueta errada justamente na peca que
# existe para nao haver etiquetas erradas.
#
# Agora so conta o que e mesmo uma chamada: importar o cliente do banco, cria-lo,
# ou ir buscar ao ambiente a chave de acesso.
RE_SUPABASE = re.compile(
    r"(?:^|\s)(?:import|from)\s+(?:supabase|psycopg)"
    r"|require\(\s*['\"]@?supabase"
    r"|create_client\s*\("
    r"|(?:os\.environ|os\.getenv|process\.env)[^\n]{0,24}SUPABASE",
    re.I)


def onde_para_o_que_sai(nos: list, produz: dict, rastreados: set,
                        G: dict, dono: dict) -> None:
    """Marca em cada peca se o que ela produz fica no git, no banco, ou nos dois."""
    for n in nos:
        destinos, provas = [], []

        # BANCO: a peca fala com o Supabase no proprio codigo dela.
        for f in n["files"]:
            cam = RAIZ / f
            if not cam.is_file():
                continue
            try:
                linhas = cam.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            achou = next(((i, l) for i, l in enumerate(linhas, 1)
                          if RE_SUPABASE.search(l) and not l.strip().startswith("#")),
                         None)
            if achou:
                destinos.append("SUPABASE")
                provas.append({"onde": "SUPABASE", "file": f, "line": achou[0],
                               "snippet": achou[1].strip()[:150]})
                break

        # GIT: um artefato que ela escreve esta versionado no repositorio.
        # Duas fontes, e as DUAS sao precisas. `produz` so guarda o que ficou sem
        # dono; o mapa do proprio mapa escreve `state.generated.json`, que esta
        # fora do censo de proposito — e por isso dizia «nao larga nada» estando
        # a escrever o ficheiro que voce esta a ver agora.
        escritos = set(produz.get(n["id"], []))
        for e in G["FILE_EDGES"]:
            if e["type"] == "WRITES" and dono.get(e["from_file"]) == n["id"]:
                escritos.add(e["to_file"])
        feitos = sorted(a for a in escritos if a in rastreados)
        if feitos:
            destinos.append("GIT")
            for a in feitos[:4]:
                provas.append({"onde": "GIT", "file": a, "line": 1,
                               "snippet": "ficheiro versionado que esta peca escreve"})

        n["destino"] = destinos
        n["destino_prova"] = provas
        if destinos:
            n["destino_texto"] = ("O que sai daqui fica em: " + " e ".join(
                {"GIT": "GIT (ficheiro com historico no repositorio)",
                 "SUPABASE": "SUPABASE (linha no banco, sem historico de commit)"}[d]
                for d in destinos) + ".")
        elif produz.get(n["id"]):
            n["destino_texto"] = ("Esta peca escreve ficheiro, mas nenhum deles esta "
                                  "versionado no repositorio: e trabalho que so existe "
                                  "na maquina de quem correu.")
        else:
            # DIZER «nao larga nada» E DIZER DE MAIS. O «Gerador do System Map»
            # escreve o proprio ficheiro do mapa — mas esse ficheiro esta fora do
            # censo de proposito, para o mapa nao se medir a si mesmo e nunca
            # chegar a um resultado estavel. Entao a frase honesta nao e «nao
            # larga nada»: e «eu nao vi nada sair», que sao coisas diferentes.
            n["destino_texto"] = (
                "Este mapa nao viu nada sair desta peca — nem ficheiro guardado no "
                "git, nem linha gravada no banco. Ou ela so le, decide ou mostra, "
                "ou o que ela escreve fica fora do censo (como os proprios ficheiros "
                "do mapa, deixados de fora para o mapa nao se medir a si mesmo).")


def as_ferramentas() -> tuple[list, list]:
    """UMA PECA POR FERRAMENTA DA TELA, e cada uma diz o que esta ligado nela HOJE.

    Quem abre o portal ve onze ferramentas e, dentro delas, numeros: 17 oportunidades,
    173 produtos, 1114 no arquivo. O que a tela nao diz e DE ONDE VEM CADA NUMERO — e
    essa e a unica pergunta que muda a decisao de quem olha.

    Este repositorio ja tem a resposta escrita, nos contratos de bloco, e ela e dura.
    O contrato do Radar das Oportunidades abre assim:

        «Today the Opportunity Radar is 100% legacy fixture (...) only one is real
         (...) The real backing is 3 records in ITALY_INGEST.OPPORTUNITIES.»

    Seventeen na tela. Tres reais por baixo. A tela nao avisa.

    Por isso o estado aqui NAO mede se a ferramenta funciona — mede se ela e honesta
    sobre a propria origem:

        REAL       verde     tudo o que aparece tem procedencia
        MISTURA    amarelo   dado real e dado escrito a mao na mesma tela, sem aviso
        SO FIXTURE amarelo   tudo escrito a mao; a tela ilustra, nao informa
        NAO SEI    cinza     o contrato nao nomeia camada nenhuma

    MISTURA e amarelo, nao verde, e a razao e simples: uma tela que mistura sem dizer
    qual e qual nao esta a informar — esta a ilustrar com numero em cima, que e a
    forma mais cara de enganar alguem, porque parece medicao.
    """
    f = DADOS / "casco.generated.json"
    if not f.exists():
        return []
    C = json.loads(f.read_text(encoding="utf-8"))

    cor = {"REAL": (VERDE, "green"), "MISTURA": (AMARELO, "yellow"),
           "SO FIXTURE": (AMARELO, "yellow"), "NAO SEI": (CINZA, "gray")}
    publica = C.get("CAMADAS_PUBLICADAS", {})

    nos, ligacoes = [], []
    for ordem, x in enumerate(C["FERRAMENTAS"]):
        est, ui = cor.get(x["de_onde_vem"], (CINZA, "gray"))
        fich = [a for a in x["ficheiros"] if (RAIZ / a).is_file()]
        nome_menu = x["prova_do_nome"]["file"]
        if not fich and (RAIZ / nome_menu).is_file():
            # sem contrato, o unico facto provado e que ela existe no menu
            fich = [nome_menu]
        if not fich:
            est, ui = CINZA, "gray"

        # o que esta ligado nela hoje — camada a camada, com o ficheiro que a publica
        ligado = [{
            "camada": nome,
            "tipo": c["tipo"],
            "o_que_e": c["o_que_e"],
            "publicada_em": publica.get(nome, []),
            "prova": c.get("prova"),
        } for nome, c in sorted(x["camadas"].items(),
                                key=lambda kv: (kv[1]["tipo"] != "REAL", kv[0]))]

        factos = [f"aparece no menu do portal como «{x['nome']}»",
                  f"contratos de bloco que a descrevem: {len(x['blocos'])}",
                  f"camadas de dado ligadas a ela: {len(ligado)}"]
        for t in ("REAL", "CANONICO", "FIXTURE"):
            n = sum(1 for c in ligado if c["tipo"] == t)
            if n:
                factos.append(f"dessas, {t.lower()}: {n}")
        if x.get("registos_citados"):
            factos.append("registos citados pelo contrato: "
                          + ", ".join(str(n) for n in x["registos_citados"]))
        if x.get("confianca"):
            factos.append(f"confianca declarada no contrato: {x['confianca']}")
        if x.get("tecido_comum"):
            factos.append("contratos que a tocam mas falam de varias telas: "
                          + str(len(x["tecido_comum"])))

        motivo = x["leitura"]
        if x.get("confissoes"):
            motivo += " " + " · ".join(x["confissoes"]) + "."
        if not fich:
            motivo = "NAO SEI: nao encontrei o contrato de bloco desta ferramenta."

        nos.append({
            "id": "C-TELA-" + x["vista"].upper(),
            "name": x["nome"],
            "kind": "tela", "icon": "▤",
            "territory": "Z-TELAS", "family": "F-ENTREGA",
            # a ordem e a do menu do portal, nao a alfabetica: e assim que a
            # pessoa as ve, e um mapa que reordena o que ela conhece obriga-a a
            # procurar duas vezes.
            "ordem": ordem,
            "status": est, "ui_status": ui, "proof": "document",
            "what": em_bom_portugues(x, ligado),
            "nome_em_portugues": EM_PORTUGUES.get(x["vista"], ""),
            # as palavras do contrato ficam inteiras, em ingles, como estao
            # escritas. Sao a prova; nao se reescreve prova.
            "texto_do_contrato": x["resumo"],
            "why_here": ("E uma das ferramentas que a pessoa abre no portal. Existe "
                         "para responder uma pergunta de negocio — e so vale a "
                         "resposta se der para dizer de onde veio cada numero."),
            "files": fich,
            "facts": factos,
            "status_reason": motivo,
            "evidence_text": x["o_que_alimenta"][:600],
            "departments": [], "views": ["entrega"], "lane": "official",
            "legacy": False, "changed_since_declared": [],
            "inbound": [], "outbound": [],
            "de_onde_vem": x["de_onde_vem"],
            "ligado_nela": ligado,
            "tecido_comum": x.get("tecido_comum") or [],
            "riscos": x.get("riscos") or [],
            "perguntas_abertas": x.get("perguntas_abertas") or [],
            "file_count": len(fich),
        })

        # A SETA: de quem publica a camada, para a ferramenta que a bebe. A prova
        # e a linha do contrato onde a camada aparece pelo nome.
        for c in ligado:
            for ficheiro in c["publicada_em"]:
                if c.get("prova"):
                    ligacoes.append({"to_file": ficheiro, "node": nos[-1]["id"],
                                     "evidence": c["prova"]})

    return nos, ligacoes  # na ordem do menu, que e a ordem que a pessoa ve




# ── UMA SETA SO PARA TRES COISAS DIFERENTES ────────────────────────────────
# O mapa desenhava com o mesmo traco «o dado corre daqui para ali», «esta peca
# e feita com aquela» e «aquela manda esta correr». Sao relacoes de naturezas
# diferentes, e misturadas produzem o novelo que faz a corrente da coleta
# desaparecer: de 316 setas, 108 nao sao caminho de dado nenhum.
#
# Quem pergunta «depois das fontes vem o que?» quer seguir O DADO. As outras
# duas sao verdadeiras e uteis, mas respondem a outra pergunta — e mostradas ao
# mesmo tempo, com o mesmo peso, tapam a resposta.
NATUREZA_DA_SETA = {
    "READS": "FLUXO",       # o conteudo daquilo entra aqui
    "ENTREGA_A_LISTA": "FLUXO",  # as fontes dizem ao canal onde ir
    "WRITES": "FLUXO",      # isto sai daqui e vai para ali
    "FEEDS": "FLUXO",       # a camada de dado alimenta a tela
    "VIAJA_POR": "FLUXO",   # a coleta sai por este canal
    "IMPORTS": "MONTAGEM",  # esta peca e construida com aquela
    "RUNS": "DISPARO",      # aquela manda esta correr
}

def desenhar(zonas: list, nos: list, familias: list) -> tuple[list, list, list, int, int]:
    """Coloca cada peca numa coluna, e cada zona lado a lado, da esquerda para a
    direita — que e a direcao em que o dado corre: fonte → motor → pacote → tela."""
    por_zona: dict[str, list] = {z["id"]: [] for z in zonas}
    for n in nos:
        por_zona.get(n["territory"], []).append(n)

    x = ZONA_GAP
    caixas = []
    for z in zonas:
        # peca com ordem propria (as ferramentas do portal) respeita-a; o resto
        # fica por id, que e estavel entre geracoes.
        membros = sorted(por_zona[z["id"]],
                         key=lambda n: (n.get("ordem", 10**6), n["id"]))
        # Zonas grandes ganham colunas em vez de virarem uma tira infinita.
        cols = 1 if len(membros) <= 5 else (2 if len(membros) <= 12 else 3)
        linhas = -(-len(membros) // cols) if membros else 1
        larg = ZONA_PAD * 2 + cols * NO_L + (cols - 1) * GAP_X
        alt = ZONA_CAB + ZONA_PAD * 2 + linhas * NO_A + max(0, linhas - 1) * GAP_Y
        for i, n in enumerate(membros):
            n["x"] = x + ZONA_PAD + (i % cols) * (NO_L + GAP_X)
            n["y"] = TOPO + ZONA_CAB + ZONA_PAD + (i // cols) * (NO_A + GAP_Y)
        caixas.append({**z, "x": x, "y": TOPO, "w": larg, "h": alt,
                       "count": len(membros)})
        x += larg + ZONA_GAP

    altura = max(c["y"] + c["h"] for c in caixas) + ZONA_GAP
    for c in caixas:
        c["h"] = altura - TOPO - ZONA_GAP  # todas as zonas com a mesma altura

    # A FAIXA DA FAMILIA. E ela que faz COLETA -> INTELIGENCIA -> ENTREGA ler-se
    # de longe, quando as letras da zona ja sao pequenas demais para ler. Cada
    # faixa abraca as zonas da sua familia, do inicio da primeira ao fim da
    # ultima — nao ha faixa desenhada a mao, e por isso ela nunca pode descrever
    # um agrupamento que ja nao existe.
    faixas = []
    for f in familias:
        minhas = [c for c in caixas if c["family"] == f["id"]]
        if not minhas:
            continue
        x0 = min(c["x"] for c in minhas) - FAM_PAD
        x1 = max(c["x"] + c["w"] for c in minhas) + FAM_PAD
        faixas.append({**f, "x": x0, "y": FAM_TOPO, "w": x1 - x0,
                       "h": altura - FAM_TOPO - ZONA_GAP + FAM_PAD,
                       "zones": [c["id"] for c in minhas],
                       "count": sum(c["count"] for c in minhas)})
    return caixas, nos, faixas, x, altura


def indice_de_fontes() -> None:
    """Escreve `docs/fontes/INDICE-DE-FONTES.md` — a porta de entrada das fontes.

    O ATLAS tem 1.353 linhas e e onde a ficha de cada fonte vive por inteiro. Ele
    esta certo assim: ficha e para ser lida com calma. O que faltava era a porta —
    uma pagina que responde "quantas fontes, de que paises, quais e que a maquina
    sabe buscar sozinha" sem obrigar ninguem a percorrer as 1.353.

    Este ficheiro e GERADO. Nao se edita a mao: edita-se o atlas e regera-se. Por
    isso ele nunca fica a discordar da fonte de onde saiu — que e exatamente o
    defeito que o proprio indice denuncia no cabecalho do atlas.
    """
    f = DADOS / "sources.generated.json"
    if not f.exists():
        return
    S = json.loads(f.read_text(encoding="utf-8"))
    c = S["COUNTS"]
    L = ["# ÍNDICE DE FONTES — SINTONIA EAME", "",
         "> **Este ficheiro é gerado.** Não o edite à mão: edite",
         "> [`ATLAS-DE-FONTES-EAME.md`](ATLAS-DE-FONTES-EAME.md) ou",
         "> [`CONTRATOS-DAS-FONTES-EAME.md`](../operacao/CONTRATOS-DAS-FONTES-EAME.md)",
         "> e rode `py system-map/scripts/generate_system_map.py`.", "",
         "O atlas guarda a ficha inteira de cada fonte. Esta página é só a porta de",
         "entrada: quantas fontes existem, de que países, e quais delas a máquina já",
         "sabe buscar sozinha.", "", "---", "",
         "## O NÚMERO", "",
         f"| | |", "|---|---|",
         f"| fichas completas no atlas | **{c['sources']}** |",
         f"| dessas, com contrato de busca escrito | **{c['with_contract']}** |",
         f"| palavras de busca medidas no código | **{c['search_terms']}** em {c['search_term_groups']} grupos |",
         f"| endereços que o código realmente chama | **{c['endpoints']}** |", ""]

    if S.get("HEADER_CLAIM", {}).get("divergencia"):
        h = S["HEADER_CLAIM"]
        L += ["> ### ⚠ O cabeçalho do atlas e as fichas não batem", ">",
              f"> O cabeçalho do atlas diz **{h['total']} fontes registradas**",
              f"> (linha {h['line']}). Fichas completas, com `SOURCE_ID` válido, há",
              f"> **{h['fichas_completas']}**. Faltam **{h['divergencia']}**.", ">",
              "> As fontes que faltam podem existir de verdade — mas sem ficha, ninguém",
              "> consegue saber o que elas têm. Isto não é corrigido automaticamente:",
              "> é decisão de gente escrever as fichas ou acertar o contador.", ""]

    k = S.get("INTAKE") or {}
    if k.get("escada"):
        L += ["---", "", "## A ESCADA — o que uma fonte tem de subir", "",
              "A distância entre os degraus é o trabalho que falta fazer. Subir exige",
              "gente: nenhum degrau se sobe sozinho.", "",
              "| # | degrau | o que é | quantas | mora em | sobe como |",
              "|---|---|---|---|---|---|"]
        for dg in k["escada"]:
            q = "—" if dg["quantas"] is None else f"**{dg['quantas']}**"
            L.append(f"| {dg['degrau']} | **{dg['nome']}** | {dg['o_que_e']} | {q} "
                     f"| `{dg['onde']}` | {dg['sobe_como']} |")
        L += ["", "### A porta de entrada", "",
              f"Fonte nova entra por `{k['porta']}` — na mão, ou de dentro de uma coleta",
              "que tropeçou nela. **O que entra é candidata, nunca fonte.**", "",
              "```bash",
              "py candidatas/fonte_nova.py --tipos          # os tipos aceites",
              "py candidatas/fonte_nova.py --listar         # a fila, agrupada por tipo",
              "py candidatas/fonte_nova.py \\",
              "    --tipo BASE_OFICIAL --pais ES --nome \"...\" --url https://... \\",
              "    --para-que \"para que serve\" --quem-viu voce --onde-viu \"onde viu\"",
              "```", "",
              f"Hoje há **{len(k.get('candidatas', []))}** candidata(s) na fila,",
              f"em `{k.get('fila_file', '')}`.", "",
              "`--para-que` é obrigatório de propósito: fonte sem uso declarado vira",
              "entulho — daqui a seis meses ninguém sabe por que ela foi anotada.", ""]

    contas = S.get("ACCOUNTS") or {}
    if contas.get("por_plataforma"):
        L += ["---", "", "## CONTAS PÚBLICAS, POR PLATAFORMA", "",
              f"Registradas em `{contas['file']}`.",
              "**Estar na lista não é autorização:** só entra na coleta quem tem",
              "identidade PROVADA e é conta local do país.", "",
              "| plataforma | mapeadas | autorizadas a coletar |", "|---|---|---|"]
        for plat, g in contas["por_plataforma"].items():
            aviso = " ⚠" if g["autorizadas"] == 0 else ""
            L.append(f"| **{plat}** | {g['total']} | {g['autorizadas']}{aviso} |")
        L += ["", f"Total: **{contas['total']}** contas, **{contas['autorizadas']}** autorizadas.", ""]

    L += ["---", "", "## A DIFERENÇA QUE IMPORTA", "",
          "| | |", "|---|---|",
          "| **fonte registrada** | alguém abriu, olhou e guardou um exemplo real |",
          "| **fonte com contrato** | a **máquina** sabe ir lá sozinha, sabe o que esperar de volta e o que fazer quando quebrar |", "",
          "A distância entre as duas é o trabalho que falta fazer. Uma fonte sem",
          "contrato só funciona enquanto a pessoa que a descobriu estiver por perto.",
          "", "---", "", "## POR PAÍS", ""]

    por_pais: dict[str, list] = {}
    for x in S["SOURCES"]:
        por_pais.setdefault(x["country"], []).append(x)

    marca = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴", "NAO SEI": "⚪"}
    for pais in sorted(por_pais):
        itens = sorted(por_pais[pais], key=lambda x: x["source_id"])
        com = sum(1 for x in itens if x["sabe_coletar"])
        L += [f"### {pais} · {len(itens)} fontes · {com} com contrato de busca", "",
              "| id | fonte | assunto | estado | a máquina busca? |",
              "|---|---|---|---|---|"]
        for x in itens:
            L.append(f"| `{x['source_id']}` | {x['name'][:58]} "
                     f"| {x['territory']} · {x['territory_name']} "
                     f"| {marca.get(x['verdict'], '⚪')} {x['verdict']} "
                     f"| {'sim' if x['sabe_coletar'] else '**não**'} |")
        L.append("")

    termos = S.get("SEARCH_TERMS", [])
    if termos:
        L += ["---", "", "## AS PALAVRAS USADAS NA BUSCA", "",
              "Na língua do país, sempre. Buscar em inglês devolve literatura",
              "internacional, não a conversa técnica local.", ""]
        for t in termos:
            L += [f"### `{t['file']}:{t['line']}` · {t['total_palavras']} palavras", "",
                  "| grupo | palavras |", "|---|---|"]
            for g in t["grupos"]:
                L.append(f"| `{g['grupo']}` | {' · '.join(g['palavras'])} |")
            L.append("")

    L += ["---", "", "Veja também: o mesmo conteúdo, navegável e ligado ao código que",
          "faz a coleta, no **System Map** em `/system-map/` (bloco **COLETA**).", ""]

    destino = RAIZ / "docs" / "fontes" / "INDICE-DE-FONTES.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(chr(10).join(L), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# DE QUE PAIS E CADA PECA — medido, nunca adivinhado
# ─────────────────────────────────────────────────────────────────────────────
# O repositorio e italiano: 447 ficheiros de Italia contra 76 de Espanha. Mas nada
# no mapa dizia isso, e por isso uma peca espanhola sentava-se ao lado de uma
# italiana com a mesma cara.
#
#     NAO MISTURAR PAISES SO E POSSIVEL SE DER PARA VER DE QUE PAIS CADA COISA E.
#
# O pais sai da CONVENCAO QUE O PROPRIO ATLAS ESCREVE — «<PAIS>-<TERRITORIO>-<seq>»
# — aplicada aos ficheiros que a peca toca, e ao nome das pastas de trabalho. Nao
# e adivinhacao a partir do nome do script: e a convencao da casa, escrita, a ser
# lida.
#
# Peca sem marca de pais nenhuma fica TRANSVERSAL — que e a verdade sobre ela, e
# nao um pais escolhido a sorte.
MARCA_PAIS = re.compile(
    r"(?:^|/|-)(EU|FR|ES|IT)-|(?:^|/)(italy|italia|spain|espana|france|francia)[-_.]",
    re.I)
TRADUZ_PAIS = {"IT": "ITALIA", "ITALY": "ITALIA", "ES": "ESPANHA", "SPAIN": "ESPANHA",
               "ESPANA": "ESPANHA", "FR": "FRANCA", "FRANCE": "FRANCA",
               "FRANCIA": "FRANCA", "EU": "EUROPA"}


def pais_de(caminho: str) -> str | None:
    m = MARCA_PAIS.search(caminho)
    if not m:
        return None
    return TRADUZ_PAIS.get((m.group(1) or m.group(2)).upper())


# A prateleira de pais: `<gaveta>/es/…`, `tests/es/…`. E a convencao desta casa
# para guardar codigo de um pais, e e o sinal mais forte que existe — mais forte
# do que o nome do ficheiro.
PRATELEIRA_PAIS = re.compile(r"(?:^|/)(es|it|fr)/", re.I)


def pais_do_codigo(caminho: str) -> str | None:
    """De que pais e ESTE ficheiro — pela prateleira onde vive ou pelo nome."""
    m = PRATELEIRA_PAIS.search(caminho)
    if m:
        return TRADUZ_PAIS.get(m.group(1).upper())
    return pais_de(caminho)


def paises_das_pecas(nos: list, G: dict, dono: dict) -> None:
    """De que pais e cada peca — e de que pais e o dado que ela ja tocou.

    SAO DUAS PERGUNTAS DIFERENTES, E MISTURA-LAS DEU UM ERRO CARO.

    Antes, contava-se tudo junto: os ficheiros da peca MAIS todo o artefato que
    ela le ou escreve. O resultado foi que «O motor de buscar», «O banco onde o
    dado fica guardado» e a «Suite de testes» apareciam no mapa como pecas
    ESPANHOLAS — treze ao todo. Nao sao. Sao a maquina comum da casa; ficaram
    marcadas assim porque o dado que passou por elas ate hoje foi espanhol.

    A diferenca importa muito, porque a pergunta seguinte e «entao tira a
    Espanha daqui» — e obedecer a isso teria apagado do mapa o motor, o banco e
    os testes. Um rotulo errado nao e um detalhe de cor: e o que faz uma decisao
    ruim parecer obvia.

    Agora sao dois campos separados:
        pais         de quem e o CODIGO — a prateleira onde ele vive
        paises_dado  que dado ela ja tocou, e quantas vezes (informacao, nao
                     identidade: um banco que guardou dado espanhol continua a
                     ser o banco, nao uma peca espanhola)
    """
    proprio: dict[str, dict] = {}
    do_dado: dict[str, dict] = {}
    sem_bandeira: dict[str, int] = {}
    for n in nos:
        c = proprio.setdefault(n["id"], {})
        for f in n["files"]:
            p = pais_do_codigo(f)
            if p:
                c[p] = c.get(p, 0) + 1
            else:
                # ficheiro sem bandeira e a maquina comum, e VOTA. Sem isto,
                # cinco ficheiros espanhois entre quarenta e tres faziam «O
                # banco onde o dado fica guardado» virar uma peca espanhola.
                sem_bandeira[n["id"]] = sem_bandeira.get(n["id"], 0) + 1
    for e in G["FILE_EDGES"]:
        for lado, outro in (("from_file", "to_file"), ("to_file", "from_file")):
            d = dono.get(e[lado])
            if not d:
                continue
            p = pais_do_codigo(e[outro])
            if p:
                c = do_dado.setdefault(d, {})
                c[p] = c.get(p, 0) + 1

    for n in nos:
        c = proprio.get(n["id"], {})
        n["paises"] = dict(sorted(c.items(), key=lambda x: -x[1]))
        n["paises_dado"] = dict(sorted(do_dado.get(n["id"], {}).items(),
                                       key=lambda x: -x[1]))
        # UMA PECA SO E DE UM PAIS SE A MAIORIA DO CODIGO DELA FOR DESSE PAIS.
        # O codigo sem bandeira conta como maquina comum e vota — e quase sempre
        # ganha, que e o certo: a casa e uma so, e os paises sao inquilinos dela.
        # Empate nao vira escolha: vira TRANSVERSAL, que e o que ele e.
        comum = sem_bandeira.get(n["id"], 0)
        if not c:
            n["pais"] = "TRANSVERSAL"
        else:
            top = max(c.values())
            donos = [k for k, v in c.items() if v == top]
            n["pais"] = (donos[0] if len(donos) == 1 and top > comum
                         else "TRANSVERSAL")


def entregue_a_inteligencia(nos: list, G: dict, dono: dict, produz: dict) -> None:
    """Para cada peca da coleta: o que ela produz JA CHEGOU a inteligencia?

        O QUE JA PASSOU NAO PODE FICAR PRESO NA COLETA.

    Um artefato que a coleta produziu e que a inteligencia ja le esta ENTREGUE:
    cumpriu o seu caminho. Um que ninguem do outro lado le esta PARADO — pode ser
    porque ainda nao chegou a vez dele, pode ser porque foi esquecido, e a
    diferenca entre as duas coisas so aparece quando alguem conta.

    Medido, nao declarado: um artefato esta entregue quando existe uma aresta
    provada dele para uma peca de INTELIGENCIA ou de ENTREGA.
    """
    fam = {n["id"]: n["family"] for n in nos}
    # quem le cada ficheiro
    leem: dict[str, set] = {}
    for e in G["FILE_EDGES"]:
        if e["type"] not in ("READS", "IMPORTS"):
            continue
        quem = dono.get(e["from_file"])
        if quem:
            leem.setdefault(e["to_file"], set()).add(quem)

    for n in nos:
        if n.get("family") != "F-COLETA":
            continue
        arte = produz.get(n["id"], [])
        entregues, parados = [], []
        for a in arte:
            destinos = {d for d in leem.get(a, set()) if fam.get(d) != "F-COLETA"}
            (entregues if destinos else parados).append(a)
        n["entregue_a_inteligencia"] = sorted(entregues)
        n["parado_na_coleta"] = sorted(parados)


NOS_PARA_ACHADO: list = []


def _rastreados() -> set:
    """Que ficheiros o git conhece. E o que separa «guardado» de «so na maquina»."""
    r = subprocess.run(["git", "-C", str(RAIZ), "ls-files"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return set(r.stdout.split()) if r.returncode == 0 else set()


def achados(arquivos: dict) -> list:
    """FACTOS que o mapa nota sozinho e que ninguem pediu para ele notar.

    Nao sao opiniao nem alerta inventado: cada um sai de duas medicoes que ja
    existem, postas lado a lado. Uma medicao sozinha nao diz nada; duas juntas,
    as vezes, dizem tudo.

    O primeiro nasceu de uma pergunta do dono do sistema — «porque coisa de
    catalogo espanhol esta na Italia?» — e a resposta foi que nao esta: o codigo
    espanhol e espanhol. O que ha e uma saida so, e o nome dela e italiano.
    """
    saida = []

    f = DADOS / "sources.generated.json"
    if f.exists():
        S = json.loads(f.read_text(encoding="utf-8"))
        paises = S["COUNTS"]["by_country"]
        # O que e publicado sai do `vercel.json`, que e contrato, e nao do nome
        # de nenhum ficheiro. Inferir pais pelo nome do ficheiro seria
        # exatamente o que este mapa proibe.
        vj = RAIZ / "vercel.json"
        servido = ""
        if vj.exists():
            servido = json.loads(vj.read_text(encoding="utf-8")).get("outputDirectory", "")
        # o repositorio, por pais — a marca de pais no proprio caminho
        marca = re.compile(r"(?:^|/|-)(EU|FR|ES|IT)-|(?:^|/)"
                           r"(italy|italia|spain|espana|france|francia)[-_.]", re.I)
        traduz = {"IT": "ITALIA", "ITALY": "ITALIA", "ES": "ESPANHA",
                  "SPAIN": "ESPANHA", "FR": "FRANCA", "FRANCE": "FRANCA",
                  "FRANCIA": "FRANCA", "EU": "EUROPA", "ESPANA": "ESPANHA"}
        obra: dict[str, int] = {}
        for caminho in arquivos:
            m = marca.search(caminho)
            if m:
                k = (m.group(1) or m.group(2)).upper()
                k = traduz.get(k, k)
                obra[k] = obra.get(k, 0) + 1
        total = sum(obra.values())

        if obra and paises:
            maior = max(obra, key=obra.get)
            saida.append({
                "id": "onde-o-trabalho-esta-versus-onde-se-procurou",
                "titulo": (f"O trabalho e de {maior.title()}. A procura de fontes "
                           f"foi noutro sitio."),
                "texto": (
                    "O REPOSITORIO, por pais: "
                    + " · ".join(f"{k} {v} ficheiros ({round(100*v/total)}%)"
                                 for k, v in sorted(obra.items(), key=lambda x: -x[1]))
                    + ". O ATLAS DE FONTES, por pais: "
                    + " · ".join(f"{k} {v}" for k, v in paises.items())
                    + f". E o unico diretorio publicado e «{servido}»."),
                "porque_importa": (
                    "O atlas conta o que foi PROCURADO; o repositorio conta o que foi "
                    f"FEITO. Confundir os dois faz um exercicio de descoberta parecer o "
                    f"corpo do trabalho. {maior.title()} tem {obra[maior]} ficheiros e "
                    f"{paises.get(maior, 0)} fontes com ficha — a obra esta muito a frente "
                    f"do acervo que a sustenta."),
                "evidencia": ["vercel.json", "docs/fontes/ATLAS-DE-FONTES-EAME.md"],
            })

    fs = DADOS / "sources.generated.json"
    if fs.exists():
        S2 = json.loads(fs.read_text(encoding="utf-8"))
        F = S2.get("COLETAS_FEITAS") or {}
        c2 = S2["COUNTS"]
        R = S2.get("RECONCILIACAO") or {}
        if R.get("so_no_master_italiano"):
            saida.append({
                "id": "duas-listas-de-fontes",
                "titulo": (f"{len(R['so_no_master_italiano'])} fontes foram levantadas "
                           f"em Italia e nunca ganharam ficha no atlas."),
                "texto": R["leitura"],
                "porque_importa": (
                    "O levantamento italiano tem campos que o atlas nao tem — o dono "
                    "normalizado, o papel da fonte, e o melhor de todos: o que ela NAO "
                    "prova. Mas nasceu ao lado do atlas, e nao dentro dele. Duas listas "
                    "a responder «que fontes temos» sao duas verdades, e a segunda "
                    "envelhece calada."),
                "evidencia": [S2["PROVENANCE"]["ATLAS"],
                              "candidatas/ITALY-SOURCE-MASTER-V1.json"],
            })
        if S2.get("COLETADAS_SEM_FICHA"):
            saida.append({
                "id": "a-coleta-mais-feita-e-a-menos-documentada",
                "titulo": "A coleta mais feita é a menos documentada.",
                "texto": (
                    f"{', '.join(S2['COLETADAS_SEM_FICHA'])} aparecem no atlas apenas "
                    f"como linha de tabela, sem ficha — sem nome, sem método de acesso, "
                    f"sem evidência. E são justamente as mais coletadas: "
                    f"{len([r for r in F.get('corridas', []) if r['fonte'] in S2['COLETADAS_SEM_FICHA']])} "
                    f"das {F.get('total', 0)} corridas registadas foram buscar a estas."),
                "porque_importa": (
                    "Sem ficha, ninguém sabe como se volta lá: por que porta se entra, "
                    "o que se espera de volta, o que fazer quando quebrar. A próxima "
                    "pessoa refaz a descoberta do zero — e paga por ela outra vez."),
                "evidencia": [S2["PROVENANCE"]["ATLAS"], F.get("ficheiro", "")],
            })
        if F.get("total") and c2.get("fontes_nunca_coletadas"):
            paises = " · ".join(f"{k} {v}" for k, v in F["por_pais"].items())
            saida.append({
                "id": "quase-nenhuma-fonte-foi-coletada",
                "titulo": (f"{c2['fontes_nunca_coletadas']} fontes nunca foram "
                           f"coletadas. Todas as corridas foram num país só."),
                "texto": (
                    f"Há {F['total']} corridas registadas, e o país delas é: {paises}. "
                    f"Elas trouxeram {F['trouxe_total']} itens e {F['sobrou_total']} "
                    f"atravessaram a régua. As outras {c2['fontes_nunca_coletadas']} "
                    f"fontes com ficha nunca foram buscadas — existem no acervo e nunca "
                    f"produziram nada."),
                "porque_importa": (
                    "Uma fonte registada e nunca coletada é trabalho de descoberta que "
                    "ainda não virou dado. E um acervo que só foi exercitado num país "
                    "não provou que funciona nos outros."),
                "evidencia": [F.get("ficheiro", "")],
            })

    # ── a lei do Brasil, medida ficheiro a ficheiro ──────────────────────────
    # Data e lugar so valem se estiverem NO MOMENTO DA COLETA — depois e tarde,
    # porque o dado ja entrou sem eles. E o lugar de onde o DOCUMENTO veio nao e
    # o lugar onde o FACTO aconteceu: por isso sao dois campos, e nao um.
    grava = re.compile(r"open\(|json\.dump|write_text")
    sem_carimbo, com_lei = [], []
    for f in (sorted((RAIZ / "coleta").glob("*.py")) if (RAIZ / "coleta").is_dir() else []):
        t = f.read_text(encoding="utf-8", errors="replace")
        if not grava.search(t):
            continue
        rel = f"coleta/{f.name}"
        if "SOURCE_LOCATION" in t and "FACT_LOCATION" in t:
            com_lei.append(rel)
        if not any(c in t for c in ("SOURCE_LOCATION", "FACT_LOCATION",
                                    "CAPTURED_AT", "PUBLICATION_DATE", "FACT_DATE")):
            sem_carimbo.append(rel)

    parados = sorted({a for n in NOS_PARA_ACHADO for a in n.get("parado_na_coleta", [])})
    if parados:
        saida.append({
            "id": "parado-na-coleta",
            "titulo": f"{len(parados)} artefatos da coleta nunca chegaram a inteligencia.",
            "texto": ("A coleta produziu-os e ninguem do outro lado os le: "
                      + " · ".join(a.split("/")[-1] for a in parados[:8])
                      + (f" … e mais {len(parados)-8}" if len(parados) > 8 else "")),
            "porque_importa": (
                "O que ja passou para a inteligencia nao deve ficar preso na coleta — e "
                "o que nunca passou tem de aparecer, porque pode ser que ainda nao "
                "chegou a vez dele, ou pode ser que foi esquecido. A diferenca entre as "
                "duas coisas so aparece quando alguem conta."),
            "evidencia": parados[:6],
        })

    if sem_carimbo:
        saida.append({
            "id": "coleta-sem-data-nem-lugar",
            "titulo": f"{len(sem_carimbo)} coletores gravam registo sem data nem lugar.",
            "texto": (
                f"{len(com_lei)} coletores separam SOURCE_LOCATION de FACT_LOCATION — a "
                f"lei que o Brasil ensinou: o lugar de onde o documento veio nao e o "
                f"lugar onde o fato aconteceu. Mas estes gravam sem carimbo nenhum: "
                + " · ".join(f.replace("coleta/", "") for f in sem_carimbo)),
            "porque_importa": (
                "Data e lugar so valem se forem postos NO MOMENTO DA COLETA. Depois e "
                "tarde: o dado ja entrou sem eles, e ninguem consegue recuperar quando "
                "foi visto nem de onde o fato e. O que entra sem carimbo nao volta a ter."),
            "evidencia": sem_carimbo[:6],
        })

    return saida


def leia_antes_de_coletar(estado: dict) -> None:
    """Escreve `regras/LEIA-ANTES-DE-COLETAR.md` — a porta unica das reguas.

        TODA MISSAO DE COLETA COMECA A PROCURAR AS REGUAS.

    E cada uma procura num sitio diferente: uma acha `proveniencia.py`, outra acha
    a regra de coleta externa, outra nao acha nada e reinventa a lei — e a lei
    reinventada nunca e igual a que ja existia.

    Este ficheiro e GERADO do mapa: lista TODA peca que e regra da coleta, o que
    ela manda, e o ficheiro onde ela vive. Nao se edita a mao. Se uma regra nova
    entrar no mapa, ela aparece aqui na proxima geracao; se alguem a apagar, ela
    desaparece daqui — e nao fica um paragrafo orfao a mandar em ninguem.

    O CI compara este ficheiro com o que o repositorio produz hoje. Uma porta de
    entrada desatualizada e pior que nenhuma: quem a le acredita nela.
    """
    zonas = {z["id"]: z for z in estado["TERRITORIES"]}
    regras = [n for n in estado["NODES"]
              if n["territory"] in ("Z-REGRAS",) and n["kind"] in ("contract", "gate")]
    ferramentas = [n for n in estado["NODES"] if n["territory"] == "Z-FERRAMENTAS"]
    fontes = [n for n in estado["NODES"] if n["territory"] == "Z-FONTES"]

    L = ["# LEIA ANTES DE COLETAR", "",
         "> **Este ficheiro é gerado do System Map.** Não o edite à mão: edite a peça",
         "> em `system-map/data/architecture.declared.json` e rode",
         "> `py system-map/scripts/generate_system_map.py`.", "",
         "Toda missão de coleta começa procurando as réguas. Elas estão todas aqui,",
         "e o caminho de cada uma é onde ela realmente vive.", "",
         "---", "", "## ANTES DE QUALQUER COISA: CONSULTE O ACERVO", "",
         "O acervo de fontes é **capital parado** — consulta-se antes de coletar. Não se",
         "coleta para descobrir o que já se sabe.", ""]
    for n in sorted(fontes, key=lambda x: x["name"]):
        L.append(f"- **{n['name']}** — {n['what']}")
        for f in n["files"][:3]:
            L.append(f"  - `{f}`")
    L += ["", "```bash",
          "py candidatas/fonte_nova.py --listar     # a fila de fontes candidatas",
          "py candidatas/fonte_nova.py --tipos      # os tipos aceites",
          "```", "",
          "**Fonte nova entra pela porta, e o que entra é candidata — nunca fonte.**",
          "Fonte nasce quando alguém a abre, olha o que ela entrega e guarda evidência.",
          "", "---", "", "## AS RÉGUAS DA COLETA", "",
          "Cada uma vale no **momento em que o dado entra**. Depois é tarde.", ""]

    for n in sorted(regras, key=lambda x: x["name"]):
        L += [f"### {n['name']}", "",
              f"{n['what']}", "",
              f"*Por que existe:* {n['why_here']}", "",
              "| | |", "|---|---|",
              f"| estado | {n['status']} — {n['status_reason']} |"]
        for f in n["files"]:
            L.append(f"| onde vive | `{f}` |")
        L.append("")

    L += ["---", "", "## COM O QUE SE VAI", ""]
    for n in sorted(ferramentas, key=lambda x: x["name"]):
        L.append(f"- **{n['name']}** — {n['what']}")
    L += ["", "---", "", "## O PADRÃO, E O CHÃO QUE NÃO DESCE", "",
          "```bash", "py regras/padrao_da_coleta.py", "```", "",
          "Dez regras medidas a cada corrida do CI. Ele **não** exige que esteja tudo",
          "certo hoje — exige **não piorar**. Um coletor novo sem carimbo de data faz",
          "o número subir, e o portão reprova nomeando o ficheiro.", "",
          "O que todo registo de coleta tem de carregar:", "",
          "| campo | por quê |", "|---|---|",
          "| `RAW_SHA256` | testemunho não é prova |",
          "| `CAPTURED_AT` | quando eu vi |",
          "| `FACT_TIME` | quando aconteceu — **não é o mesmo** |",
          "| `SOURCE_LOCATION` / `FACT_LOCATION` | de onde veio o documento ≠ onde o fato é |",
          "| `CADENCE_STATE` | sem ela, fonte morta parece fonte quieta |",
          "| `EGRESS_IP` | por onde a requisição saiu |",
          "| `ITEM_COUNT_RAW` → `NORMALIZED` | o que veio, e o que atravessou a régua |",
          "| `COST_USD` | mesmo quando é zero — medido ≠ ausente |", "",
          "---", "", "## AS LEIS QUE NÃO SE QUEBRAM", "",
          "- **NÃO SEI continua NÃO SEI.** Registrar desconhecido é resultado válido.",
          "- **Ausência não é ausência no mundo.** «Não encontrámos nesta leitura»,",
          "  nunca «não existe».",
          "- **Lista vazia é FALHA, não zero.** A diferença entre «não há» e «não",
          "  consegui ver» é a diferença entre um relatório e uma mentira.",
          "- **`HTTP 200` não basta.** Há 200 com página de erro: status bom, corpo lixo.",
          "- **Endereço errado nosso não é bloqueio da fonte.**",
          "  `ROUTE_NOT_FOUND ≠ SOURCE_BLOCKED`.",
          "- **Estado de porta não é veredito.**",
          "  `ACCESS_CLASSIFICATION ≠ ANALYTIC_VERDICT`.",
          "- **Número digitado à mão mente.** Contagem é calculada, nunca digitada.",
          "- **Teste que nunca viu vermelho não é teste.**", "",
          "---", "",
          f"Gerado de {len(regras)} réguas, {len(ferramentas)} ferramentas e "
          f"{len(fontes)} peças de fonte declaradas no mapa.", ""]

    destino = RAIZ / "regras" / "LEIA-ANTES-DE-COLETAR.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(chr(10).join(L), encoding="utf-8")


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
    # As pecas GERADAS (as fontes, a linhagem) tem de existir antes do mapa de
    # donos: sem isso, nenhuma seta consegue apontar para elas.
    gerados = linhagem()
    fontes, lig_fontes = as_fontes()
    gerados += fontes
    telas, lig_telas = as_ferramentas()
    gerados += telas

    dono: dict[str, str] = {f: g["id"] for g in gerados for f in g["files"]}
    conflitos: list[dict] = []
    for c in comps:
        c["_files"] = []
        fora = c.get("exclude", [])
        for padrao in c["files"]:
            for caminho in arquivos:
                if any(casa(caminho, x) for x in fora):
                    continue  # pertence a outro componente, declarado a mao
                if dono.get(caminho, "").startswith(("C-AS-FONTES", "C-TELA-", "lineage_")):
                    continue  # ja e de uma peca gerada; nao se reivindica por cima
                if casa(caminho, padrao):
                    if caminho in dono and dono[caminho] != c["id"]:
                        conflitos.append({"file": caminho, "claimed_by": [dono[caminho], c["id"]]})
                        continue
                    dono[caminho] = c["id"]
                    c["_files"].append(caminho)
        c["_files"] = sorted(set(c["_files"]))

    # ── 1b · o artefato pertence a quem o escreve ────────────────────────────
    # Duas passagens: um artefato pode ser escrito por um script que so ganhou
    # dono na primeira volta.
    produz: dict[str, list] = {}
    for _ in range(2):
        for e in G["FILE_EDGES"]:
            if e["type"] != "WRITES":
                continue
            autor = dono.get(e["from_file"])
            if autor and e["to_file"] not in dono:
                dono[e["to_file"]] = autor
                produz.setdefault(autor, []).append(e["to_file"])

    veiculos, lig_veiculos = os_veiculos(comps, dono, G)
    gerados += veiculos

    # ── 2 · arestas de ficheiro sobem para arestas de componente ─────────────
    # Cada aresta de componente carrega TODAS as linhas que a provam. E o que
    # responde "por que existe esta seta?" com dedo apontado, nao com opiniao.
    ligacoes: dict[tuple, dict] = {}
    for e in G["FILE_EDGES"]:
        a, b = dono.get(e["from_file"]), dono.get(e["to_file"])
        if not a or not b or a == b:
            continue
        # A SETA SEGUE O DADO, NAO A DEPENDENCIA.
        #
        # `pacote_camadas.py` LE o corpus dos pesquisadores. Escrita como esta no
        # codigo, a seta sai do pacote e aponta para o corpus — e ao ler o mapa
        # ficava «o corpus RECEBE DE o pacote», que e o contrario do que acontece:
        # o dado sai do corpus e vai para o pacote.
        #
        # Um mapa de processo tem de responder "para onde isto vai". Por isso a
        # leitura e virada: quem foi lido ALIMENTA quem leu. `IMPORTS` e `RUNS`
        # ficam como estao — ali a seta e mesmo de dependencia: quem importa
        # depende de quem e importado, e quem manda rodar manda mesmo.
        if e["type"] == "READS":
            a, b = b, a
        chave = (a, b, e["type"])
        alvo = ligacoes.setdefault(chave, {
            "from": a, "to": b, "type": e["type"], "payload": e["payload"],
            "natureza": NATUREZA_DA_SETA.get(e["type"], "FLUXO"),
            "kind": "technical", "status": VERDE,
            "reason": "", "evidence": [],
        })
        alvo["evidence"].append(e["evidence"])

    for lig in ligacoes.values():
        n = len(lig["evidence"])
        verbo = {"IMPORTS": "importa", "READS": "alimenta", "WRITES": "escreve em",
                 "RUNS": "manda rodar", "RETRIEVED_BY": "e buscada por"}.get(
                     lig["type"], lig["type"].lower())
        nomes = {c["id"]: c["name"] for c in comps}
        nomes.update({g["id"]: g["name"] for g in gerados})
        de, para = nomes.get(lig["from"], lig["from"]), nomes.get(lig["to"], lig["to"])
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
            # A faixa: `official` e a rota de hoje, `legacy` ficou para tras, e
            # `futuro` foi construido, provado, e esta guardado a espera do seu
            # momento. Uma peca cujos ficheiros vivem TODOS numa prateleira de
            # pais (`<gaveta>/es/`) e, por construcao, de um pais so — e enquanto
            # esse pais nao for o da rota, ela e projeto futuro, e nao legado.
            # Enterrar como legado o que so esta a espera custa caro.
            "lane": (c.get("lane") or ("legacy" if c.get("legacy") else
                     ("futuro" if c["_files"] and all(
                         len(f.split("/")) > 2 and f.split("/")[1] in ("es", "fr", "eu")
                         for f in c["_files"]) else "official"))),
            "family": next(t["family"] for t in D["TERRITORIES"]
                           if t["id"] == c["territory"]),
            "files": fs, "file_count": len(fs),
            "status": status, "status_reason": motivo,
            "changed_since_declared": mudou,
            "produces": sorted(set(produz.get(c["id"], []))),
            "inbound": sorted({l["from"] for l in ent}),
            "outbound": sorted({l["to"] for l in sai}),
        })

    # ── 5 · o que o mapa NAO cobre — dito na cara, nao escondido ─────────────
    orfaos_de_codigo = sorted(p for p, f in arquivos.items()
                              if f["code_dir"] and f["readable"] and p not in dono)
    nao_reivindicados = sorted(p for p in arquivos if p not in dono)

    nos = nos + gerados

    # As setas de cada peca, calculadas de uma vez para TODAS — declaradas e
    # geradas. Enquanto isto vivia dentro do laco dos componentes declarados, as
    # pecas geradas ficavam eternamente a dizer «recebe: ninguem», mesmo tendo
    # nove ligacoes medidas. Um cartao que diz «ninguem» quando ha nove e pior
    # que um cartao em branco: em branco, quem le pergunta.

    paises_das_pecas(nos, G, dono)
    entregue_a_inteligencia(nos, G, dono, produz)
    NOS_PARA_ACHADO[:] = nos

    # A fonte aponta para o componente que a busca. A prova e a linha do contrato
    # que NOMEIA o script — a mesma regra de sempre: sem linha, sem seta.
    dono_de = dict(dono)
    for lf in lig_fontes:
        alvo = dono_de.get(lf["to_file"])
        if not alvo:
            continue
        chave = ("C-AS-FONTES", alvo, "RETRIEVED_BY")
        alvo_lig = ligacoes.setdefault(chave, {
            "from": chave[0], "to": alvo, "type": "RETRIEVED_BY",
            "payload": "coleta", "natureza": "FLUXO",
            "kind": "technical", "status": VERDE,
            "reason": "", "evidence": [],
        })
        alvo_lig["evidence"].append(lf["evidence"])
    # ── A SETA DO CANAL ESTAVA AO CONTRARIO ─────────────────────────────────
    # Ela ia da acao PARA o canal, e por isso o canal era o fim da linha: o
    # cartao do YouTube nao tinha para onde apontar, e o caminho da coleta
    # morria ali. Perguntado tres vezes «o que o YouTube colhe vai pra onde?»,
    # o mapa nao tinha como responder com uma seta — so com texto.
    #
    # A regra desta casa e: A SETA SEGUE O DADO. E o dado nao vai para o
    # YouTube — VEM DE LA. A acao chama o canal (isso e controlo), mas o que
    # atravessa a linha e a coleta, e ela corre no sentido contrario:
    #
    #     YOUTUBE  ->  Colher o YouTube  ->  o ficheiro onde ela guarda
    #
    # Com a seta virada, o canal deixa de ser um beco e passa a ser o INICIO do
    # caminho — que e o que ele realmente e. A mesma linha de codigo prova as
    # duas leituras; a diferenca e qual delas o mapa desenha, e o mapa desenha
    # o dado.
    nome_da_peca = {c["id"]: c["name"] for c in comps}
    for lv in lig_veiculos:
        # AS FONTES entregam ao canal a lista de onde ir. E a unica coisa que um
        # canal recebe, e sem ela «colher o YouTube» nao quer dizer nada:
        # colher o YouTube de quem?
        if lv.get("entrega_lista"):
            chave = ("C-AS-FONTES", lv["veiculo"], "ENTREGA_A_LISTA")
            alvo_lig = ligacoes.setdefault(chave, {
                "from": "C-AS-FONTES", "to": lv["veiculo"], "type": "ENTREGA_A_LISTA",
                "payload": "contas", "natureza": "FLUXO",
                "kind": "technical", "status": VERDE,
                "reason": ("AS FONTES entregam a este canal a lista de contas a "
                           "visitar, com a identidade de cada uma provada ou "
                           "rejeitada e o motivo escrito."),
                "evidence": [],
            })
            alvo_lig["evidence"].append(
                {k: lv[k] for k in ("file", "line", "snippet")})
            continue
        chave = (lv["veiculo"], lv["acao"], "VIAJA_POR")
        alvo_lig = ligacoes.setdefault(chave, {
            "from": lv["veiculo"], "to": lv["acao"], "type": "VIAJA_POR",
            "payload": "coleta", "natureza": "FLUXO",
            "kind": "technical", "status": VERDE,
            "reason": (f"O que sai deste canal entra em "
                       f"«{nome_da_peca.get(lv['acao'], lv['acao'])}», que e quem o "
                       f"chama e quem guarda o que ele devolve."),
            "evidence": [],
        })
        alvo_lig["evidence"].append({k: lv[k] for k in ("file", "line", "snippet")})

    # Quem PUBLICA a camada aponta para a ferramenta que a bebe. E a resposta
    # visual a pergunta "o que esta ligado no Radar hoje?" — com a linha do
    # contrato que nomeia a camada por baixo de cada seta.
    for lt in lig_telas:
        origem = dono_de.get(lt["to_file"])
        if not origem or origem == lt["node"]:
            continue
        chave = (origem, lt["node"], "FEEDS")
        alvo_lig = ligacoes.setdefault(chave, {
            "from": origem, "to": lt["node"], "type": "FEEDS",
            "payload": "dado", "natureza": "FLUXO",
            "kind": "technical", "status": VERDE,
            "reason": "", "evidence": [],
        })
        if lt["evidence"] not in alvo_lig["evidence"]:
            alvo_lig["evidence"].append(lt["evidence"])
    for chave, l in ligacoes.items():
        if l["type"] == "FEEDS" and not l["reason"]:
            nome_alvo = next((n["name"] for n in nos if n["id"] == l["to"]), l["to"])
            l["reason"] = (f"O contrato de bloco de «{nome_alvo}» nomeia, em "
                           f"{len(l['evidence'])} linha(s), a camada de dado que "
                           f"esta peca publica.")
    for chave, l in ligacoes.items():
        if l["type"] == "RETRIEVED_BY" and not l["reason"]:
            nome_alvo = next((c["name"] for c in comps if c["id"] == l["to"]), l["to"])
            quantas = len({e["snippet"].split()[0] for e in l["evidence"]})
            l["reason"] = (f"{quantas} fonte(s) declaram, no contrato de busca, que "
                           f"quem vai la buscar e «{nome_alvo}».")
    tecnicas = [l for l in ligacoes.values() if l["kind"] == "technical"]
    for n in nos:
        n["inbound"] = sorted({l["from"] for l in tecnicas if l["to"] == n["id"]})
        n["outbound"] = sorted({l["to"] for l in tecnicas if l["from"] == n["id"]})

    # A PASTA E UM DESTINO, mesmo quando o nome do ficheiro e uma variavel.
    # Sem isto, dois coletores que enchem uma pasta inteira apareciam a «nao
    # escrever nada» — e um cartao que diz isso sobre uma peca que guarda e pior
    # que um cartao vazio: parece medicao, e e ponto cego.
    em_pasta = G.get("ESCRITAS_EM_PASTA") or {}
    for n in nos:
        pastas = []
        for f in n.get("files", []):
            for x in em_pasta.get(f, []):
                if x["pasta"] not in [q["pasta"] for q in pastas]:
                    pastas.append({"pasta": x["pasta"],
                                   "prova": {"file": f, "line": x["line"],
                                             "snippet": f"escreve em {x['constante']}"}})
        n["escreve_na_pasta"] = pastas

    onde_para_o_que_sai(nos, produz, _rastreados(), G, dono)

    zonas, nos, faixas, mundo_w, mundo_h = desenhar(
        D["TERRITORIES"], nos, D["FAMILIES"])

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
        "ACHADOS": achados(arquivos),
        "SEARCH_TERMS": termos_de_busca(),
        "PROVENANCE": G["PROVENANCE"],
        "FAMILIES": faixas,
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
    leia_antes_de_coletar(estado)
    indice_de_fontes()

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
        for passo in ("scan_repo.py", "scan_sources.py"):
            subprocess.run([sys.executable, str(Path(__file__).with_name(passo))],
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
