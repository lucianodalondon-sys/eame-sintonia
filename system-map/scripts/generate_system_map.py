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
import glob
import ast
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
    """Devolve (passou, frase que explica em portugues comum).

    ATENCAO A DIRECAO. Desde que o `IMPORTS` passou a seguir o dado, «quem me
    importa» deixou de estar na ENTRADA e passou a estar na SAIDA: o codigo da
    biblioteca corre para dentro de quem a usa, e a seta vai no mesmo sentido.

    Enquanto estas regras nao acompanharam, o mapa dizia «Apify: biblioteca que
    ninguem importa» sobre uma peca com NOVE ligacoes de import. Uma regra
    escrita para a direcao antiga produz um status errado com a mesma cara de um
    status certo — e essa e a pior avaria que este ficheiro pode ter.
    """
    corre = any(e["type"] == "RUNS" for e in ent)
    # quem me importa: agora sai de mim para quem me usa
    importado = any(e["type"] == "IMPORTS" for e in sai)
    lido = (any(e["type"] == "READS" for e in ent)
            or any(e["type"] in ("READS", "IMPORTS") for e in sai))

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
        if any(e["type"] == "IMPORTS" for e in ent):
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
        # o READS ja vem virado: quem le o artefacto esta na SAIDA dele
        if sai:
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

# A FAMILIA VEM DA ZONA, NUNCA DA PECA. Uma peca que declara familia diferente
# da sua zona cria dois agrupamentos para a mesma coisa, e o mapa passa a ter
# duas respostas para «onde e que isto vive».
#
# ⚠️ ISTO ERA UM DICIONARIO LOCAL, e quatro cartoes gerados aqui escreviam
# `"family": "F-ESPERA"` a mao ao lado de `"territory": "Z-GUARDA"`. Enquanto a
# zona e os literais concordaram, ninguem notou; quando a Z-GUARDA passou para
# F-COLETA — porque guarda os donos do RAW e do DERIVED — os quatro ficaram a
# apontar para a familia antiga e o P2_PECA_TEM_FAMILIA reprovou. A regra ja
# estava escrita em comentario; passa a estar escrita em codigo.
FAMILIA_DA_ZONA = {"Z-PROVA": "F-INTELIGENCIA", "Z-GUARDA": "F-COLETA",
                   "Z-EXECUCAO": "F-COLETA", "Z-ACOES": "F-COLETA"}


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
       # ⚠️ O HEAD SAIU DAQUI, E NAO POR LIMPEZA.
       # `validate_system_map.py` remove o bloco PROVENANCE antes de comparar,
       # e diz porque: «HEAD e BRANCH mudam a cada commit; compara-los faria o
       # portao reprovar toda a gente, sempre». A regra esta certa e estava
       # incompleta — o mesmo carimbo vazava para dentro dos FACTOS deste
       # cartao, onde a remocao nao chega.
       #
       # O efeito era estrutural, nao cosmetico: commitar o mapa muda o HEAD,
       # o que invalida o mapa acabado de commitar. NAO HAVIA ESTADO EM QUE O
       # P1 PASSASSE depois de um commit — a arvore ficava suja para sempre, e
       # uma arvore permanentemente suja esconde a proxima mudanca a serio.
       #
       #     UM PORTAO ANTI-DRIFT QUE NENHUM COMMIT PODE SATISFAZER
       #     NAO MEDE DRIFT: MEDE O RELOGIO.
       #
       # A BRANCH fica, porque e o facto arquitetural — quem consome. O commit
       # e proveniencia, e continua inteiro em PROVENANCE.HEAD, que e onde o
       # validador ja sabe nao olhar.
       [f"branch {ramo}"],
       "Medido pelo proprio git desta arvore no momento em que o mapa foi gerado.",
       "o git prova a branch; o commit exacto vive em PROVENANCE.HEAD.",
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
# MENCIONAR UM CANAL NAO E USAR UM CANAL — e este erro ja me apanhou duas vezes.
# A primeira foi com o Supabase: um ficheiro que FALAVA do banco nos comentarios
# saiu marcado como quem grava nele. A segunda foi aqui: «Colher o YouTube»
# aparecia ligado ao INSTAGRAM porque o cabecalho do ficheiro compara os dois —
# «trinta por pagina, contra os DOZE do muro do Instagram». Isso e prosa, nao
# codigo.
#
#     UMA SETA FALSA E PIOR QUE UMA SETA EM FALTA.
#     A que falta faz perguntar. A falsa faz decidir errado.
#
# Por isso o padrao exige uma forma de USO — o endereco, a constante em
# maiusculas, o import ou a chamada — e nunca a palavra solta numa frase.
CANAIS = (
    ("V-YOUTUBE", "YOUTUBE",
     r"youtube\.com|youtu\.be|yt_dlp|\bYOUTUBE\b|youtube_\w+\s*\(|import\s+youtube",
     "Video publico: o que o canal do concorrente e o do sector poem no ar."),
    ("V-INSTAGRAM", "INSTAGRAM",
     r"instagram\.com|\bINSTAGRAM\b|instagram_\w+\s*\(|import\s+instagram",
     "A pagina publica: o que a marca publica para quem a segue."),
    ("V-LINKEDIN", "LINKEDIN",
     r"linkedin\.com|\bLINKEDIN\b|linkedin_\w+\s*\(|import\s+linkedin",
     "A pagina de empresa e a das pessoas: contratacao, evento, anuncio."),
    ("V-FACEBOOK", "FACEBOOK",
     r"facebook\.com|\bFACEBOOK\b|facebook_\w+\s*\(|import\s+facebook",
     "A pagina publica da marca, ainda viva em varios mercados agricolas."),
    ("V-HTTP", "PEDIDO HTTP DIRETO",
     r"requests\.(get|post|put|head)|httpx\.|urllib\.request|aiohttp",
     "O site aberto, sem plataforma pelo meio: base oficial, PDF, pagina, ficheiro."),
)


def sem_comentarios(texto: str) -> str:
    """Tira o que e prosa, para que so o codigo responda.

    COMENTARIOS **E** DOCSTRINGS. Achei que os comentarios chegavam, e nao
    chegam: os ficheiros desta casa explicam-se em docstrings longas, e uma
    delas tem um titulo em maiusculas —

        O YOUTUBE E MAIS BARATO QUE O INSTAGRAM, NAO MAIS CARO.

    — que passou por todos os filtros. A palavra estava em maiusculas, como uma
    constante, mas era so enfase. «Colher o YouTube» ficou ligado ao INSTAGRAM
    por causa de uma frase que compara os dois precos.

    Nao ha padrao esperto que distinga enfase de constante. O que resolve e
    tirar a prosa toda antes de procurar.
    """
    try:
        arvore = ast.parse(texto)
    except SyntaxError:
        arvore = None

    linhas = texto.splitlines()
    if arvore is not None:
        for no in ast.walk(arvore):
            if not isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                continue
            corpo = getattr(no, "body", None)
            if not corpo:
                continue
            primeiro = corpo[0]
            if (isinstance(primeiro, ast.Expr)
                    and isinstance(primeiro.value, ast.Constant)
                    and isinstance(primeiro.value.value, str)):
                de = primeiro.lineno - 1
                ate = (primeiro.end_lineno or primeiro.lineno)
                for k in range(de, min(ate, len(linhas))):
                    linhas[k] = ""

    fora = []
    for linha in linhas:
        fora.append("" if linha.lstrip().startswith("#") else linha.split("#", 1)[0])
    return "\n".join(fora)


def o_corte_do_pdf() -> tuple[list, list]:
    """O maior buraco medido da Italia, desenhado como buraco.

    O DESENHO QUE ISTO PRODUZ

        EVIDENCIA BRUTA (PDF)
                |
                v
        [ DERIVACAO DE TEXTO — AUSENTE ]   <- a tesoura
                x
        TEXTO QUE A MAQUINA LE
                |
                v
        VOCABULARIO / CLASSIFICACAO / PENEIRA

    POR QUE E UMA PECA E NAO UMA NOTA DE RODAPE

    Ate aqui o mapa dizia «corpus» e metia numa palavra so duas coisas que nao
    sao a mesma: o que esta GUARDADO e o que da para LER. Com uma palavra so,
    62,7 MB de PDF pareciam corpus farto, e o sistema parecia bem alimentado.

    Nao esta. 43 dos 49 PDF italianos nunca viraram texto. Os 6 que viraram,
    viraram a mao — nao ha codigo nenhum que o faca.

    E isto muda a ordem do trabalho: nao adianta melhorar palavras, peneira ou
    disparo enquanto a evidencia estiver fechada dentro do PDF. Nenhuma
    palavra, por melhor que seja, encontra texto que nao existe.

    CUIDADO COM A LINGUAGEM, QUE AQUI JA SE ERROU

    62,7 MB de PDF NAO e prova de milhoes de caracteres. Megabyte nao e
    caractere: um PDF de 6 MB tanto pode ser cinquenta paginas escritas como
    uma unica fotografia digitalizada. O numero antigo continua NAO REPRODUZIDO
    COMO TEXTO; o que esta provado e o acervo bruto, e escreve-se como acervo
    bruto.

    NOTA SOBRE O QUE O MAPA CONSEGUE VER

    O scanner ignora ficheiros binarios de proposito — nao sabe ler um PDF. Ou
    seja: os 49 documentos mais ricos da Italia sao INVISIVEIS para o mapa pela
    via normal. Este cartao existe para eles deixarem de o ser, e os numeros
    dele vem do censo, que os conta pelo disco.
    """
    f = DADOS / "corpus-it.generated.json"
    if not f.is_file():
        return [], []
    C = json.loads(f.read_text(encoding="utf-8"))
    B = C.get("ACERVO_EM_PDF") or {}
    T = C.get("TOTAIS") or {}

    n_pdf = B.get("OCORRENCIAS", 0)
    mb = B.get("MEGABYTES", 0)
    com = B.get("OCORRENCIAS_COM_DERIVACAO", 0)
    sem = B.get("OCORRENCIAS_SEM_DERIVACAO", 0)
    prosa = T.get("CORPO_DE_TEXTO_EM_CARACTERES", 0)
    # OCORRENCIA x CONTEUDO, medido pelo censo. Nao se recalcula aqui: duas
    # medicoes da mesma coisa divergem no primeiro dia (COL-LAW-501).
    OC = C.get("OCORRENCIA_E_CONTEUDO") or {}
    # CAMINHO nao e CAPTURA. Este cartao ja disse, em prosa, que os repetidos
    # eram «o mesmo documento em dois sitios» — palpite lido no nome da pasta.
    # Quem decide isso e o censo de identidade, pela prova de captura, e o que
    # aparece aqui e o VEREDITO dele, nunca uma frase escrita a mao.
    fi = DADOS / "identidade-it.generated.json"
    ID = ({} if not fi.is_file()
          else (json.loads(fi.read_text(encoding="utf-8"))
                .get("IDENTIDADE_DO_ARTEFATO") or {}))
    veredito = ID.get("VEREDITO") or {}
    frase_do_veredito = (
        " · ".join("%s: %d" % (k, v) for k, v in sorted(veredito.items()))
        or "NÃO MEDIDO")

    bruto = {
        "id": "C-IT-PDF-BRUTO", "name": "Evidência bruta em PDF (Itália)",
        "kind": "acervo", "icon": "▤",
        "territory": "Z-GUARDA", "family": FAMILIA_DA_ZONA["Z-GUARDA"],
        "status": CINZA, "ui_status": "gray", "proof": "git-measurement",
        "what": (f"{OC.get('OCORRENCIAS', n_pdf)} ocorrências de PDF italiano "
                 f"guardadas — boletins regionais, bilanci fitosanitari, "
                 f"diretrizes, {mb} MB. São "
                 f"{OC.get('CONTEUDOS_UNICOS', '?')} documentos diferentes: "
                 f"{OC.get('CONTEUDOS_COM_MAIS_DE_UM_CAMINHO', 0)} deles foram "
                 f"buscados mais de uma vez, e isso é REPETIÇÃO, não perda — "
                 f"nada sumiu."),
        "why_here": ("Enquanto o mapa dizia «corpus» numa palavra só, isto "
                     "parecia alimento do sistema. Separar o guardado do "
                     "legível foi o que permitiu ver — e fechar — o corte."),
        "files": [], "file_count": n_pdf,
        "facts": [
            f"OCORRÊNCIAS (caminhos no disco): {OC.get('OCORRENCIAS', n_pdf)}",
            f"CONTEÚDOS ÚNICOS (impressão digital): "
            f"{OC.get('CONTEUDOS_UNICOS', 'NÃO SEI')}",
            f"o mesmo conteúdo em mais de um caminho: "
            f"{OC.get('OCORRENCIAS_DE_CONTEUDO_REPETIDO', 0)} ocorrência(s), "
            f"em {OC.get('CONTEUDOS_COM_MAIS_DE_UM_CAMINHO', 0)} conteúdo(s)",
            f"PERDIDOS: {OC.get('PERDA', 'NÃO SEI')} — repetição NÃO é perda. "
            f"{OC.get('PORQUE_NAO_E_PERDA', '')}",
            f"tamanho em disco: {mb} MB",
            f"ocorrências COM derivação localizável: {com} de {n_pdf}",
            f"ocorrências SEM derivação: {sem}",
            f"derivados únicos que as servem: {B.get('DERIVADOS_UNICOS', 'NÃO SEI')} — uma derivação serve todas as "
            f"ocorrências do mesmo conteúdo",
            "caracteres dentro dos PDF: NÃO MEDIDO — abrir PDF é derivar, não medir",
            f"{mb} MB NÃO é prova de milhões de caracteres: megabyte não é caractere",
            "o antigo «milhões de caracteres» continua NÃO REPRODUZIDO COMO TEXTO",
        ]
        # Cada repeticao NOMEADA, e nao so contada. Um numero diz que ha
        # repeticao; a lista diz ONDE — e e a lista que impede alguem de
        # concluir, daqui a um mes, que «sumiram seis».
        + [f"repetido · {r['SHA256'][:12]}… em {len(r['CAMINHOS'])} caminhos: "
           + " | ".join(r["CAMINHOS"])
           for r in (OC.get("ONDE_SE_REPETE") or [])]
        # CAMINHO != CAPTURA, e o veredito vem medido, nunca escrito a mao.
        + [f"CAPTURAS DISTINTAS: {ID.get('CAPTURAS_DISTINTAS', 'NÃO SEI')} — "
           f"caminho diferente NÃO prova captura diferente, e SHA igual NÃO "
           f"prova a mesma captura",
           f"veredito dos grupos repetidos: {frase_do_veredito}",
           f"cópias SEM prova de captura em registo nenhum: "
           f"{ID.get('COPIAS_SEM_PROVA_DE_CAPTURA', 'NÃO SEI')} — G-40"]
        + [f"{g['SHA256'][:12]}… → {g['ESTADO']}: {g['PORQUE']}"
           for g in (ID.get("GRUPOS") or [])],
        "status_reason": (
            f"CINZENTO porque o mapa continua a não conseguir LER um PDF — o "
            f"scanner não abre ficheiro binário, e isso não mudou. O que mudou "
            f"é que já não precisa: o executor abriu-os e o texto vive ao lado, "
            f"como artefato próprio, esse sim legível e contado."),
        "evidence_text": ("system-map/data/corpus-it.generated.json → "
                          "ACERVO_EM_PDF + OCORRENCIA_E_CONTEUDO; "
                          "system-map/data/identidade-it.generated.json → "
                          "IDENTIDADE_DO_ARTEFATO"),
        "departments": ["ENGENHARIA"], "views": ["acervo", "infra", "audit"],
        "lane": "official", "legacy": False, "changed_since_declared": [],
        "inbound": [], "outbound": [],
    }

    # ── A SETA DO CORTE, DEPOIS DE O CORTE TER SIDO FECHADO ─────────────────
    # Esta seta dizia «DERIVACAO AUSENTE» e estava certa quando foi escrita. Ja
    # nao esta: a derivacao existe, correu, e produziu texto com pai para todos
    # os PDF que tinham camada de texto.
    #
    #     SETA DESATUALIZADA E PIOR QUE SETA NENHUMA.
    #     A que falta faz perguntar; a que mente faz confiar.
    #
    # O que sobra deste lado e o caminho ANTIGO, feito a mao: seis textos que
    # alguem escreveu sem deixar registo de como. Tres deles conseguem provar de
    # que PDF vieram; tres nao. Esse continua a ser um caminho por confirmar, e
    # e isso — e so isso — que a seta cinzenta passa a dizer.
    gp = DADOS / "golden-path-pdf.generated.json"
    maos = {}
    if gp.is_file():
        maos = (json.loads(gp.read_text(encoding="utf-8")).get("TEXTOS_A_MAO")
                or {})
    n_maos = maos.get("TOTAL", com)
    provados = maos.get("PARENT_PROVEN", 0)

    ligacoes = [{
        "from": "C-IT-PDF-BRUTO", "to": "C-IT-TEXTO-PESQUISAVEL",
        "type": "DERIVA_TEXTO_A_MAO", "kind": "expected",
        "status": CINZA, "evidence": [],
        "reason": (
            f"⚪ O CAMINHO ANTIGO, FEITO À MÃO. {n_maos} textos foram tirados de "
            f"PDF por uma pessoa, antes de haver contrato, sem registo de quem "
            f"nem de quando. Destes, {provados} conseguem provar de que PDF "
            f"vieram — o texto do ficheiro aparece mesmo dentro do documento. "
            f"Os outros {n_maos - provados} não: estar ao lado com o mesmo nome "
            f"é indício, não prova, e por isso o pai ficou NÃO SEI. "
            f"Fica cinzenta porque continua sem código que a sustente. O "
            f"caminho novo, esse, está desenhado a cheio: BRUTO → EXECUTOR → "
            f"TEXTO DERIVADO → PORTA."),
        "source": "system-map/data/golden-path-pdf.generated.json",
        "declared_by": "missao system-map-canonical-v1, fase 1 do data plane",
    }]
    return [bruto], ligacoes


def o_armazem_sem_livro() -> tuple[list, list]:
    """O armazem italiano no Supabase: bytes presentes, memoria operacional nao.

    POR QUE ESTE CARTAO EXISTE

    O mapa dizia, por omissao, «a Italia nao esta no Supabase». Deixou de ser
    verdade: ha 195 objetos sob o prefixo IT/ e 80,7 MB de bytes la dentro. E
    nao ha uma unica linha de `raw_asset` ou `collection_run` a reclama-los.

        BYTES PRESENTES  !=  PROVENIENCIA OPERACIONAL COMPLETA

    E POR QUE ELE NAO PODE FICAR VERDE

    A tentacao seria pinta-lo de verde — «os bytes estao preservados, otimo».
    Seria a leitura mais perigosa possivel: um armazem cheio com o livro de
    entrada em branco parece saude e e o contrario. Este cartao fica AMARELO
    por construcao, e diz porque no proprio texto.

    E OS NUMEROS DELE NAO SAO OBSERVED

    Esta sessao nao tem credencial do banco. As contagens vieram de uma leitura
    do coordenador, e o cartao carrega o estado EXTERNAL_LIVE_MEASUREMENT com o
    nome de quem mediu. Recado de terceiro pode estar certo e continuar nao
    sendo prova nossa.
    """
    f = DADOS / "armazem-it.generated.json"
    if not f.is_file():
        return [], []
    A = json.loads(f.read_text(encoding="utf-8"))
    L = A.get("LACUNA_DO_ARMAZEM") or {}
    P = A.get("PROCEDENCIA_NO_GIT") or {}
    Q = A.get("QUEM_ESCREVEU") or {}
    D = A.get("DOIS_ACERVOS") or {}
    if not L or L.get("MEDICAO_EXTERNA") == "AUSENTE":
        return [], []

    objetos = L.get("ITALY_STORAGE_OBJETOS", "NÃO SEI")
    mb = round((L.get("ITALY_STORAGE_BYTES") or 0) / 1_000_000, 1)
    tres = L.get("TRES_CONTAGENS") or {}
    C = A.get("A_CONTA_FECHA") or {}

    no = {
        "id": "C-ARMAZEM-IT-SEM-LIVRO",
        "name": "Armazém italiano no Supabase (sem livro de entrada)",
        "kind": "acervo", "icon": "▤",
        "territory": "Z-GUARDA", "family": FAMILIA_DA_ZONA["Z-GUARDA"],
        # AMARELO POR CONSTRUCAO. Nao ha caminho por onde este cartao fique
        # verde enquanto houver objeto sem dono declarado.
        "status": AMARELO, "ui_status": "yellow",
        "proof": "external-live-measurement",
        "what": (
            f"{objetos} objetos italianos guardados no bucket `raw`, {mb} MB — e "
            f"ZERO linhas de `raw_asset` e ZERO de `collection_run` a dizer quem "
            f"os trouxe. Os bytes estão lá; o livro de entrada está em branco."),
        "why_here": (
            "O mapa deixava passar «a Itália não está no Supabase». Está — só "
            "que pela metade, e é a metade que não aparece que engana. Bytes "
            "presentes NÃO É procedência operacional completa."),
        "files": [], "file_count": 0,
        "facts": [
            f"ESTADO DA MEDIÇÃO: {L.get('ESTADO_DA_MEDICAO')} — medido por "
            f"{L.get('MEDIDO_POR')} em {L.get('MEDIDO_EM')}, NÃO por esta sessão",
            f"por quê: {L.get('PORQUE_NAO_E_OBSERVED')}",
            f"STORAGE IT: {objetos} objetos · {L.get('ITALY_STORAGE_BYTES')} bytes",
        ]
        + [f"prefixo {p['PREFIXO']}: {p['OBJETOS']} objeto(s)"
           for p in (L.get("ITALY_STORAGE_POR_PREFIXO") or [])]
        + [
            "IT/ é PREFIXO DE OBJETO, não pasta — o Storage não tem diretórios",
            f"RAW_ASSET IT: {L.get('ITALY_RAW_ASSET_LINHAS')}",
            f"COLLECTION_RUN IT: {L.get('ITALY_COLLECTION_RUN_LINHAS')}",
            f"LACUNA: {L.get('LACUNA')} — G-42",
            f"quem enviou os bytes: {(Q.get('PASSO_1_ENVIA_OS_BYTES') or {}).get('FERRAMENTA')}, "
            f"que vive {(Q.get('PASSO_1_ENVIA_OS_BYTES') or {}).get('ONDE_VIVE')}",
            f"quem devia escrever a memória: {(Q.get('PASSO_2_ESCREVE_A_MEMORIA') or {}).get('FERRAMENTA')} "
            f"— e está preso à Espanha pela própria escrita do ficheiro",
            f"importações italianas que existem: "
            f"{', '.join(Q.get('IMPORTACOES_ITALIANAS_QUE_EXISTEM') or []) or 'nenhuma'}; "
            f"dessas, que falam do bruto: "
            f"{len(Q.get('DESSAS_QUE_FALAM_DO_BRUTO') or [])}",
            f"classificação: {Q.get('CLASSIFICACAO')}",
            f"A PROCEDÊNCIA PERDEU-SE? {L.get('A_PROCEDENCIA_PERDEU_SE')}",
            f"a corrida, essa: {L.get('RUN_HISTORICA')}",
            f"e por isso: {L.get('NAO_RETROCRIAR')}",
            f"AS TRÊS CONTAGENS — manifesto "
            f"{tres.get('DOCUMENTOS_NO_MANIFESTO')} · conteúdos únicos "
            f"{tres.get('CONTEUDOS_UNICOS_NO_MANIFESTO')} · objetos DOCUMENT "
            f"{tres.get('OBJETOS_DOCUMENT_NO_ARMAZEM')} · "
            f"{tres.get('ESTADO')} ({tres.get('FORCA_DA_PROVA')})",
            f"como se explicam: {tres.get('COMO_SE_EXPLICAM')}",
            f"objetos previstos pelo manifesto: "
            f"{C.get('OBJETOS_PREVISTOS_PELO_MANIFESTO')} · medidos no armazém: "
            f"{C.get('OBJETOS_MEDIDOS_NO_ARMAZEM')} · batem: {C.get('BATE')}",
            f"por que a prova não é FULL_SHA256_MATCH: "
            f"{C.get('PORQUE_NAO_E_FULL_SHA256_MATCH')}",
            f"algum byte perdido? {C.get('BYTE_PERDIDO')}",]
        + [f"repetido · {g['SHA256'][:12]}… — {g['REGISTOS']} registos, "
           f"{g['URLS_DISTINTAS']} URL(s) → {g['OBJETOS_PREVISTOS']} objeto(s): "
           f"{g['PORQUE']} ({', '.join(g['PRODUTOS'])})"
           for g in (C.get("GRUPOS_REPETIDOS") or [])]
        + [
            f"documentos com procedência recuperável no Git: "
            f"{P.get('PROCEDENCIA_RECUPERAVEL')} de {P.get('DOCUMENTOS_DECLARADOS')}",
            f"OS 43 DO GOLDEN PATH ESTÃO AQUI? {D.get('JA_NO_ARMAZEM')} de "
            f"{D.get('GOLDEN_PATH_CONTEUDOS')} — são DOIS ACERVOS diferentes, "
            f"medidos por impressão digital e não por nome de ficheiro",
        ],
        "status_reason": (
            f"AMARELO, e não verde, de propósito. Os {objetos} objetos estão "
            f"preservados — e um armazém cheio com o livro de entrada em branco "
            f"PARECE saúde e é o contrário. Enquanto houver objeto sem linha que "
            f"o reclame, este cartão não tem caminho para ficar verde."),
        "evidence_text": ("system-map/data/armazem-it.generated.json → "
                          "LACUNA_DO_ARMAZEM + QUEM_ESCREVEU + DOIS_ACERVOS; "
                          "data/samples/SUPABASE-LIVE-MEDICAO-EXTERNA.json"),
        "departments": ["ENGENHARIA"], "views": ["acervo", "infra", "audit"],
        "lane": "official", "legacy": False, "changed_since_declared": [],
        "inbound": [], "outbound": [],
        "source": "system-map/data/armazem-it.generated.json",
        "declared_by": "missao reconciliar-o-supabase-real",
    }

    return [no], []


def _onde_esta(caminho: str, agulha: str) -> dict:
    """A linha onde aquilo esta HOJE, com o texto que la esta hoje.

    Prova escrita a mao envelhece em silencio: o ficheiro muda, o numero fica,
    e o portao nao acusa nada porque a linha continua a existir.
    """
    try:
        linhas = (RAIZ / caminho).read_text(encoding="utf-8",
                                            errors="replace").splitlines()
    except OSError:
        linhas = []
    for i, l in enumerate(linhas, 1):
        if agulha in l:
            return {"file": caminho, "line": i, "snippet": l.strip()[:160]}
    return {"file": caminho, "line": 1,
            "snippet": f"NAO ENCONTRADO NESTE FICHEIRO: {agulha}"}


def a_sala_de_espera() -> tuple[list, list]:
    """O READY — o que a coleta produz, e que ninguem ainda le.

    POR QUE ESTE CARTAO E GERADO, E NAO DECLARADO

    O READY nao e um ficheiro. E uma FUNCAO (`admissao.pronto_para_inteligencia`),
    um CONTRATO (COL-LAW-043, 11 campos fixos) e uma FRONTEIRA — e o ficheiro que
    o contem ja tem dono (`C-ADMISSAO`, que cobre `admissao/admissao.py`).
    Declara-lo como peca com gaveta propria obrigaria a tirar aquele ficheiro do
    dono que ja o tem, e o mapa proibe dois donos para um ficheiro.

    E NAO SE CRIA `ready.py` PARA TER CARTAO. Isso ja foi recusado, e com razao:
    inventar um modulo para um cartao ficar verde e a doenca, nao o conserto.

    Entao ele nasce da MEDICAO, como o cartao do derivado. Os numeros vem de
    `provas/a_fronteira_da_coleta.py`, que le a lei, chama o dono e conta quem
    produz e quem consome. Nada aqui esta escrito a mao.

    E ELE NAO PODE FICAR VERDE

        CONTRATO EXISTE  nao e  ALGUEM ENTREGA
        ALGUEM ENTREGA   nao e  ALGUEM RECOLHE

    Enquanto ninguem ler esta saida, o cartao mostra o buraco com nome. Uma
    porta por onde ninguem passa nao e uma porta: e uma parede com macaneta.
    """
    f = DADOS / "fronteira.observada.json"
    if not f.is_file():
        return [], []
    F = json.loads(f.read_text(encoding="utf-8"))
    prod = F.get("PRODUTORES_EM_RUNTIME") or []
    cons = F.get("CONSUMIDORES") or []
    campos = F.get("CAMPOS_DO_CONTRATO") or []
    batem = F.get("LEI_E_CODIGO_BATEM")

    # AMARELO POR CONSTRUCAO enquanto nao houver consumidor. Nao ha caminho por
    # onde este cartao fique verde sem alguem do outro lado ler a saida — e
    # pinta-lo de verde faria toda a gente concluir que a fronteira ja funciona.
    no = {
        "id": "C-READY", "name": "READY · o que a coleta entrega",
        "kind": "acervo", "icon": "◈",
        "territory": "Z-ESPERA", "family": "F-ESPERA",
        "status": AMARELO if not cons else VERDE,
        "ui_status": "yellow" if not cons else "green",
        "proof": "git-measurement",
        "lane": "official", "legacy": False, "changed_since_declared": [],
        "files": [], "file_count": 0, "departments": ["ENGENHARIA"],
        # ⚠️ AS MESMAS VISTAS DA ADMISSAO, e nao mais.
        # Com `audit` aqui e so `acervo` na porta, o READY ficava sozinho na
        # vista de auditoria — nao por nao ter ligacao, mas por o vizinho dela
        # nao estar la. Um cartao orfao por ausencia do OUTRO e um orfao falso,
        # e manda procurar um buraco que nao existe.
        "views": ["acervo"], "inbound": [], "outbound": [],
        "evidence_text": "provas/a_fronteira_da_coleta.py",
        "what": (
            f"O contrato de saida da coleta: {len(campos)} campos fixos, "
            f"declarados na {F.get('LEI')} e devolvidos por "
            f"{F.get('DONO')}. A inteligencia recebe isto e mais nada — nao "
            f"sabe que raspador trouxe, nem que remendo foi preciso. "
            f"Produtores em runtime: {len(prod)}. Consumidores: {len(cons)}."),
        "why_here": (
            "A faixa «A ESPERA» define-se como «o que ja passou por toda a "
            "coleta e ainda nao entrou na inteligencia» — que e o READY, "
            "palavra por palavra. Ela estava ocupada pela Z-GUARDA, que guarda "
            "os donos do RAW e do DERIVED (etapas 5 e 6 das nove, provadas em "
            "provas/a_rota_m2_atravessa.py A3 e A4) e portanto e COLETA. A "
            "sala de espera existia no mapa com os inquilinos errados, e o "
            "inquilino certo nao tinha cartao nenhum."),
        "facts": [
            f"a lei e o codigo declaram os mesmos campos: "
            f"{'SIM' if batem else 'NAO'} ({len(campos)} campos)",
            f"produtores em runtime: {', '.join(prod) if prod else 'NENHUM'}"
            + (" — e e um CLI, nao um workflow" if prod else ""),
            f"consumidores: {', '.join(cons) if cons else 'NENHUM'}",
            f"destino declarado {F.get('DESTINO')} existe: "
            f"{'SIM' if F.get('DESTINO_EXISTE') else 'NAO'}",
        ],
        "status_reason": (F.get("GAP_PORQUE") or "a fronteira tem consumidor."),
        "gap": F.get("GAP"),
        "produces": [],
    }
    ligacoes = [
        {"from": "C-ADMISSAO", "to": "C-READY", "type": "PRODUZ",
         "kind": "technical", "status": VERDE, "payload": "dado",
         "categoria": "DATA",
         "reason": (
             "quem passa a porta com SIM sai por `pronto_para_inteligencia()`, "
             "no mesmo ficheiro — e so quem passa: a funcao levanta erro para "
             "qualquer outro resultado."),
         # A LINHA PROCURA-SE, NAO SE ESCREVE. Isto estava fixo em 391 com um
         # `snippet` que eu proprio tinha redigido — e a funcao mudou de sitio.
         # A linha 391 e hoje uma linha em branco: o mapa apontava a prova mais
         # importante da fronteira para o nada, e nenhum portao reparava porque
         # a linha EXISTE (so nao diz nada).
         #
         #     UMA PROVA QUE APONTA PARA UMA LINHA EM BRANCO
         #     NAO E UMA PROVA.
         "evidence": [_onde_esta("admissao/admissao.py",
                                 "def pronto_para_inteligencia")]},
    ]
    return [no], ligacoes


def a_casa_do_derivado() -> tuple[list, list]:
    """A tabela do derivado — DESENHADA E PROVADA, e nao aplicada.

    POR QUE ESTE CARTAO E GERADO, E NAO DECLARADO

    Uma TABELA nao e um ficheiro. Declara-la como peca com uma gaveta propria
    obrigaria a tirar a migration do dono que ja a tem (`C-SUPABASE`, que cobre
    `supabase/**`) — e uma peca sem ficheiro nenhum fica VERMELHA, com razao: o
    mapa nao consegue distinguir «conceito» de «codigo que sumiu».

    Entao este cartao nasce da MEDICAO, como o do armazem. Os numeros dele vem
    do censo das derivacoes; nenhum esta escrito aqui.

    E ELE NAO PODE FICAR VERDE

        DESIGNED e DB_TESTED  nao sao  LIVE_APPLIED.

    Enquanto a migration nao correr em producao e nenhuma linha existir, este
    cartao e ALVO. Pintar de verde uma casa que ainda nao foi construida e a
    maneira mais rapida de alguem concluir que o trabalho ja foi feito.
    """
    f = DADOS / "derivacoes.generated.json"
    if not f.is_file():
        return [], []
    D = json.loads(f.read_text(encoding="utf-8"))
    P = D.get("PRODUTORES") or {}
    A = D.get("ACERVO_DERIVADO") or {}
    L = D.get("O_PAI_CANONICO") or {}

    migracao = "supabase/migrations/022_o_derivado_ganha_casa.sql"
    existe = (RAIZ / migracao).is_file()

    no = {
        "id": "C-DERIVED-ARTIFACT",
        "name": "ALVO · a casa do derivado (migration 022)",
        "kind": "acervo", "icon": "▷",
        "territory": "Z-GUARDA", "family": FAMILIA_DA_ZONA["Z-GUARDA"],
        # ✅ VERDE, E SO AGORA. Ate 08/09/2026 este cartao era ALVO: a tabela
        # existia no papel e nao em producao. Nesse dia a 022 foi aplicada, o
        # esquema foi lido de volta objeto a objeto, e o primeiro derivado
        # italiano nasceu por um caminho canonico. CAN DO passou a DID DO —
        # com recibo, nao com promessa.
        # O mapa so aceita verde sem ligacao quando a peca diz em que MEDICAO se
        # apoia. Aqui apoia-se em duas, ambas no Git: o censo das derivacoes e o
        # recibo do canario. Nao e verde por o ficheiro existir.
        "status": VERDE, "ui_status": "green", "proof": "git-measurement",
        "what": (
            f"A tabela onde vive o que NOS produzimos a partir do bruto. "
            f"Uma linha e UM artefato, de UM bruto, por UMA ferramenta numa "
            f"VERSAO, com UNS parametros, numa POSICAO da serie. Medidos hoje: "
            f"{P.get('PRODUTORES_DE_DERIVADO', '?')} produtores de derivado e "
            f"{A.get('DERIVADOS', '?')} derivacoes reais."),
        "why_here": (
            "RAW nao e DERIVED. Acrescentar um `parent_sha256` ao `raw_asset` "
            "seria mais curto e apagaria essa lei dentro da tabela chamada "
            "«bruto» — uma tabela que se chama bruto com filhos la dentro mente "
            "para todo leitor futuro."),
        "files": [], "file_count": 0,
        "facts": [
            f"a migration existe no repositorio: {'SIM' if existe else 'NAO'} — {migracao}",
            "DESIGNED sim · IMPLEMENTED sim · DB_TESTED sim · LIVE_APPLIED SIM "
            "(08/09/2026, APPLIED_SET={022}, readback 30 provas) · OBSERVED SIM",
            "primeiro derivado italiano: derived_artifact id=1, pai raw_asset "
            "890, texto-de-pdf v1, 4968 bytes — nascido de uma captura NOVA, "
            "nao de historia velha",
            "e o retry deu REUSED, sem upload novo e sem linha nova, com o "
            "byte conferido no armazem",
            f"produtores medidos: {P.get('PRODUTORES_MEDIDOS', '?')}, e so "
            f"{P.get('PRODUTORES_DE_DERIVADO', '?')} sao de especie DERIVED_ARTIFACT",
            f"por especie: {P.get('POR_ESPECIE')}",
            "a legenda que o YouTube entrega com o video e RAW_CAPTURE, NAO "
            "derivado — nos nao a produzimos, e mete-la aqui declararia uma "
            "linhagem que nao existe",
            f"ferramentas de derivacao: "
            f"{', '.join(x for x in (P.get('FERRAMENTAS_DE_DERIVACAO') or []) if x)}",
            f"derivacoes reais hoje: {A.get('DERIVADOS')} · por tipo: {A.get('POR_TIPO')}",
            f"chaves de derivacao distintas: {A.get('CHAVES_DE_DERIVACAO_DISTINTAS')}",
            "IDENTIDADE = (parent_sha256, kind, producer, producer_version, "
            "parameters_hash, serie_posicao). O sha256 identifica BYTES, nao "
            "linhagem — duas rotas podem chegar aos mesmos bytes",
            f"legado: {L.get('DERIVADOS_EXISTENTES')} derivados, "
            f"{L.get('LINHAS_DE_RAW_ASSET_IT')} linhas de raw_asset IT, "
            f"{L.get('LIGAVEIS_HONESTAMENTE')} ligaveis honestamente — "
            f"{L.get('CLASSE')}",
            f"e por isso: {L.get('O_QUE_SE_FAZ')}",
            A.get("O_TEMPO_DO_PAI_NAO_SE_INVENTA", ""),
        ],
        "status_reason": (
            "VERDE porque a 022 foi APLICADA em producao e o esquema foi lido "
            "de volta objeto a objeto, e porque um produtor real escreveu a "
            "primeira linha — uma captura italiana nova, nao um byte historico. "
            "O verde e do CANARIO: uma unidade. As outras fontes, o OCR e os "
            "43 historicos continuam de fora."),
        "evidence_text": ("system-map/data/derivacoes.generated.json; "
                          "data/samples/SUPABASE-LIVE-MEDICAO-EXTERNA.json → "
                          "CANARIO_FORWARD_2026_09_08; "
                          "supabase/migrations/022_o_derivado_ganha_casa.sql"),
        "departments": ["ENGENHARIA"], "views": ["infra", "audit"],
        "lane": "official", "legacy": False, "changed_since_declared": [],
        "inbound": [], "outbound": [],
        "source": "system-map/data/derivacoes.generated.json",
        "declared_by": "missao a-casa-do-derivado",
    }
    return [no], []


def a_estrada_do_pdf() -> tuple[list, list]:
    """A primeira estrada do plano de dados, desenhada a partir da corrida real.

    O DESENHO

        PDF BRUTO ──DATA──> EXECUTOR ──DATA──> TEXTO DERIVADO ──DATA──> PORTA
             │
             └── NEEDS_OCR  (so aparece se houver algum)

    A REGRA QUE MANDA AQUI

    Nada nestes cartoes e escrito a mao. Todos os numeros saem do ficheiro da
    reconciliacao, que e produzido pela corrida. Se a corrida nao aconteceu, os
    cartoes nao aparecem — e isso e de proposito:

        NAO SE AFIRMA «OBSERVADO» SEM TER HAVIDO UMA CORRIDA.

    Um mapa que mostra uma estrada que ninguem percorreu e pior que um mapa
    vazio, porque o vazio faz perguntar e o desenho falso faz confiar.

    E O QUE FICOU A FALTAR TAMBEM APARECE

    Os 49 textos existem e a porta viu-os todos — e todos ficaram em NAO SEI,
    porque nenhum diz quando o fato aconteceu. Isso e a estrada a funcionar: a
    porta recusou-se a adivinhar. O cartao mostra esse degrau em vez de o
    esconder atras de um numero bonito de cobertura.
    """
    f = DADOS / "golden-path-pdf.generated.json"
    if not f.is_file():
        return [], []
    R = json.loads(f.read_text(encoding="utf-8"))
    C = R["COUNTS"]
    maos = R.get("TEXTOS_A_MAO") or {}
    imut = R.get("RAW_IMUTAVEL") or {}

    admissao = {k[len("ADMISSION_"):]: v for k, v in C.items()
                if k.startswith("ADMISSION_") and k != "ADMISSION_SEEN"}
    resumo_adm = " · ".join(f"{k} {v}" for k, v in sorted(admissao.items()))
    total_derivado = C["DERIVED_LANDED"] + C.get("JA_EXISTIAM", 0)

    # ── OCORRENCIA x CONTEUDO, e a ENTRADA da derivacao ─────────────────────
    # Vem do censo, que e o dono desta medicao. Recalcular aqui daria duas
    # contas para a mesma pergunta — e a segunda envelhece calada.
    fc = DADOS / "corpus-it.generated.json"
    OC = (json.loads(fc.read_text(encoding="utf-8")).get("OCORRENCIA_E_CONTEUDO")
          or {}) if fc.is_file() else {}
    # O QUE ENTRA NA DERIVACAO E O CONTEUDO, NAO O CAMINHO. O executor nomeia o
    # derivado pela impressao digital do pai, entao dois caminhos com o mesmo
    # conteudo produzem UM derivado. E por isso que 49 ocorrencias dao 43
    # derivados sem que nada se perca.
    entrada_deriv = OC.get("CONTEUDOS_UNICOS", C["RAW_INPUT"])

    # ── A CORRIDA FECHOU? Derivado, nao afirmado ────────────────────────────
    # A COL-LAW-210 diz que COMPLETE exige fecho canonico. A corrida declara
    # SUCCESS. Sao duas perguntas, e a segunda mede-se procurando os campos do
    # fecho — se nenhum existe, nao ha fecho, e dizer COMPLETE seria inventar.
    # O FECHO PASSOU A SER MEDIDO PELA PROPRIA CORRIDA (G-38). Este calculo
    # fica como rede de seguranca para corridas ANTIGAS, que nao o declaram —
    # e e por isso que ele procura os campos em vez de confiar num rotulo.
    CAMPOS_DE_FECHO = ("RUN_STATE", "STATE_BEFORE", "STATE_AFTER",
                       "COMPLETION_BASIS", "GIT_COMMIT")
    tem_fecho = sorted(k for k in CAMPOS_DE_FECHO if R.get(k))
    fecho = {
        "ESTADO": "COMPLETE" if tem_fecho else "PARTIAL",
        "PORQUE": (
            "fecho declarado por " + ", ".join(tem_fecho) if tem_fecho else
            "nenhum campo de fecho canónico está preservado (procurados: "
            + ", ".join(CAMPOS_DE_FECHO) + "). Reconciliação sem perda e "
            "fecho da corrida são factos diferentes: LOST=0 não faz COMPLETE"),
    }

    # A FAMILIA VEM DA ZONA, NUNCA DA PECA. Uma peca que declara familia
    # diferente da sua zona cria dois agrupamentos para a mesma coisa, e o mapa
    # passa a ter duas respostas para «onde e que isto vive».
    comum = {
        "kind": "engine", "proof": "git-measurement",
        "files": [], "file_count": 0, "departments": ["ENGENHARIA"],
        "views": ["acervo", "infra", "audit"], "lane": "official",
        "legacy": False, "changed_since_declared": [],
        "inbound": [], "outbound": [], "evidence_text": f.name,
    }

    # O CARTAO DO EXECUTOR NAO NASCE AQUI.
    # O codigo dele e peca declarada (C-EXECUTOR-TEXTO-PDF), porque e
    # arquitetura: existe no disco, tem dono, tem ficheiro. O que nasce aqui e
    # so o que foi MEDIDO nesta corrida. Ter as duas coisas em cartoes
    # separados e o que permite distinguir CODIGO (existe) de OBSERVADO (esta
    # corrida usou) — e criar um segundo cartao para o executor seria a
    # «segunda verdade» que a Regra Zero proibe.

    derivado = {
        **comum,
        "id": "C-IT-TEXTO-DERIVADO", "name": "Texto derivado, com pai",
        "icon": "▤", "territory": "Z-GUARDA",
        "family": FAMILIA_DA_ZONA["Z-GUARDA"],
        "status": VERDE, "ui_status": "green",
        "what": (f"{total_derivado} textos tirados de PDF por máquina, cada um "
                 f"a saber de que original nasceu, com que executor, em que "
                 f"versão e a que horas."),
        # SEM NUMERO CRAVADO AQUI. Esta frase ja disse «43 de 49 PDF fechados»,
        # e ficou falsa no dia em que a derivacao correu — uma fotografia velha
        # com cara de medicao. O numero vive nos `facts`, que vem da medicao.
        "why_here": ("É o outro lado do corte que estava aberto: os PDF "
                     "estavam guardados e fechados. Agora têm texto, e o "
                     "texto sabe de que original nasceu."),
        "facts": [
            f"artefatos de texto com pai: {total_derivado}",
            f"emitidos nesta corrida: {C['DERIVED_EMITTED']}",
            f"guardados nesta corrida: {C['DERIVED_LANDED']}",
            f"já existiam (repetir não duplica): {C.get('JA_EXISTIAM', 0)}",
            f"PERDIDOS: {C['LOST']}",
            f"textos antigos feitos à mão: {maos.get('TOTAL', 0)} — "
            f"com pai provado {maos.get('PARENT_PROVEN', 0)}, "
            f"pai desconhecido {maos.get('PARENT_UNKNOWN', 0)}",
        ],
        "status_reason": (
            f"Cada artefato tem nome próprio, impressão digital, pai, "
            f"impressão digital do pai e versão de quem o fez. Perdidos: "
            f"{C['LOST']}."),
    }

    porta = {
        **comum,
        "id": "C-GOLDEN-PATH-PDF", "name": "A corrida · PDF até à porta",
        "icon": "◉", "territory": "Z-PROVA",
        "family": FAMILIA_DA_ZONA["Z-PROVA"],
        "status": AMARELO, "ui_status": "yellow",
        "what": (f"A conta desta corrida, do PDF guardado até à porta. "
                 f"{OC.get('OCORRENCIAS', C['RAW_INPUT'])} ocorrências → "
                 f"{entrada_deriv} documentos diferentes → {total_derivado} "
                 f"textos derivados → a porta viu {C['ADMISSION_SEEN']}: "
                 f"{resumo_adm or 'nenhuma decisão'}. "
                 f"PERDIDOS: {C['LOST']} · precisam de OCR: "
                 f"{C['RAW_NEEDS_OCR']} · erro de extração: "
                 f"{C['RAW_EXTRACTION_ERROR']}."),
        "why_here": ("Se a máquina fez e o mapa não consegue mostrar, a "
                     "engenharia ainda não terminou."),
        "facts": [
            f"RUN_ID: {R['RUN_ID']}",
            f"estado que a corrida declara: {R['STATUS']}",
            f"ESTADO DE FECHO: {R.get('RUN_STATE', 'NÃO SEI')} — "
            f"{(R.get('COMPLETION_BASIS') or {}).get('PORQUE', 'sem base declarada')}",
            f"rota: {R.get('ROUTE', 'NÃO SEI')} · executor "
            f"{R.get('EXECUTOR_ID', '?')} v{R.get('EXECUTOR_VERSION', '?')} · "
            f"pipeline v{R.get('PIPELINE_VERSION', '?')}",
            f"engenharia: commit {str(R.get('GIT_COMMIT', 'NÃO SEI'))[:10]} · "
            f"árvore limpa {R.get('GIT_TREE_CLEAN', 'NÃO SEI')} · "
            f"Bíblia {R.get('BIBLE_VERSION', 'NÃO SEI')}",
            f"ANTES: {R.get('STATE_BEFORE', 'NÃO SEI')}",
            f"DEPOIS: {R.get('STATE_AFTER', 'NÃO SEI')}",
            f"pré-voo: executor disponível "
            f"{(R.get('PREFLIGHT') or {}).get('EXECUTOR_AVAILABLE', 'NÃO SEI')} "
            f"({(R.get('PREFLIGHT') or {}).get('CAPACIDADE', '?')})",
            "PRONTIDÃO: esta estrada mede DOCUMENTO, não FATO. O tempo e o "
            "lugar do fato pertencem ao claim, e o claim ainda não é extraído "
            "(COL-LAW-502).",
            # A corrida diz SUCCESS. A COL-LAW-210 pergunta outra coisa: houve
            # FECHO canonico? Sao dois factos, e escrevem-se os dois — pintar
            # de COMPLETE porque LOST=0 seria confundir «nada se perdeu» com
            # «a corrida fechou».

            "",
            f"OCORRÊNCIAS de PDF: {OC.get('OCORRENCIAS', C['RAW_INPUT'])}",
            f"CONTEÚDOS ÚNICOS: {OC.get('CONTEUDOS_UNICOS', 'NÃO SEI')}",
            f"ocorrências do mesmo conteúdo: "
            f"{OC.get('OCORRENCIAS_DE_CONTEUDO_REPETIDO', 0)} — repetição, "
            f"NÃO perda",
            "",
            f"ENTRADA DA DERIVAÇÃO: {entrada_deriv}",
            f"DERIVADOS QUE EXISTEM: {total_derivado}",
            f"emitidos NESTA corrida: {C['DERIVED_EMITTED']} · "
            f"guardados NESTA corrida: {C['DERIVED_LANDED']} · "
            f"já existiam: {C.get('JA_EXISTIAM', 0)}",
            f"PERDIDOS: {C['LOST']} — medido entre etapas comparáveis "
            f"(entrada da derivação × derivados), nunca ocorrências menos "
            f"conteúdos",
            "",
            f"precisam de OCR: {C['RAW_NEEDS_OCR']}",
            f"erro de extração: {C['RAW_EXTRACTION_ERROR']}",
            f"a porta viu: {C['ADMISSION_SEEN']}",
            f"decisões: {resumo_adm or 'nenhuma'}",
            f"originais alterados: {len(imut.get('ALTERADOS') or [])} "
            f"({imut.get('VEREDITO', 'NAO SEI')})",
            "",
            # CUSTO: o que esta medido e a AUSENCIA de servico pago e de rede.
            # Isso nao e uma contabilidade financeira, e escrever «0 €» como se
            # fosse seria inventar precisao.
            f"rota paga usada: {R.get('ROTA_PAGA_USADA', 'NÃO SEI')} · "
            f"rede usada: {R.get('REDE_USADA', 'NÃO SEI')} · "
            f"OCR usado: {R.get('OCR_USADO', 'NÃO SEI')}",
            # O NUMERO SOZINHO MENTE. `0.0` sem base le-se como conta fechada.
            # Por isso o valor NUNCA aparece sem a base ao lado — e se a base
            # faltar, o mapa diz NAO SEI em vez de mostrar o numero.
            (f"custo: {R.get('COST_USD')} · base: {R.get('COST_BASIS')} · "
             f"contabilidade monetária: {R.get('COST_ACCOUNTING', 'NÃO SEI')}"
             if R.get("COST_BASIS") else
             "custo: NÃO SEI — há um valor, e ele não diz de onde vem. "
             "Um zero sem base lê-se como conta fechada."),
            "número de caracteres: NÃO CANÓNICO — não há regra de contagem "
            "escrita (a mesma pasta dá contas diferentes conforme a quebra de "
            "linha). Entra quando tiver contrato próprio.",
            "PRECISÃO: NÃO SEI — não há gabarito humano. Contar quantos "
            "passaram é COBERTURA, não acerto.",
        ],
        # A COR É DERIVADA, e diz respeito ao ESTÁGIO DOCUMENTAL — não ao fato.
        # Verde aqui significa «a estrada do documento fechou», nunca «os fatos
        # estão prontos»: o fato ainda não foi extraído, e dizer o contrário
        # seria a confusão que a COL-LAW-502 existe para impedir.
        "status_reason": (
            (f"A estrada DOCUMENTAL fechou: a corrida está "
             f"{R.get('RUN_STATE', fecho['ESTADO'])} "
             f"({(R.get('COMPLETION_BASIS') or {}).get('PORQUE', '')}), "
             f"{C['LOST']} perdidos, e a porta deu uma resposta com prova a "
             f"cada um dos {C['ADMISSION_SEEN']}: {resumo_adm}. "
             f"VERDE É DO DOCUMENTO, NÃO DO FATO — nenhum claim foi extraído, e "
             f"por isso nenhum fato está pronto. A extração é o estágio "
             f"seguinte, e ainda não existe.")
            if (R.get("RUN_STATE") == "COMPLETE" and not C["LOST"]) else
            (f"AMARELO: a corrida está {R.get('RUN_STATE', fecho['ESTADO'])} "
             f"({(R.get('COMPLETION_BASIS') or {}).get('PORQUE', fecho['PORQUE'])}) "
             f"e há {C['LOST']} perdidos. Reconciliação sem perda não é fecho de "
             f"corrida, e as duas coisas têm de estar certas.")),
    }
    if R.get("RUN_STATE") == "COMPLETE" and not C["LOST"]:
        porta["status"], porta["ui_status"] = VERDE, "green"

    nos = [derivado, porta]

    ligacoes = [
        {"from": "C-IT-PDF-BRUTO", "to": "C-EXECUTOR-TEXTO-PDF", "type": "DERIVA_TEXTO",
         "kind": "technical", "status": VERDE, "payload": "dado",
         "reason": (f"{OC.get('OCORRENCIAS', C['RAW_INPUT'])} ocorrências de "
                    f"PDF entram, e são {entrada_deriv} documentos diferentes: "
                    f"{OC.get('OCORRENCIAS_DE_CONTEUDO_REPETIDO', 0)} estão "
                    f"guardados em dois sítios. O executor nomeia o texto pela "
                    f"impressão digital do pai, então conteúdo repetido dá UM "
                    f"texto — e isso é REPETIÇÃO, não perda. O original não foi "
                    f"tocado: {imut.get('VEREDITO', 'NAO SEI')}."),
         "evidence": [{"file": "coleta/executor_texto_de_pdf.py", "line": 1,
                       "snippet": f"RUN {R['RUN_ID']} · "
                                  f"RAW_INPUT={C['RAW_INPUT']}"}]},
        {"from": "C-EXECUTOR-TEXTO-PDF", "to": "C-IT-TEXTO-DERIVADO",
         "type": "PRODUZ", "kind": "technical", "status": VERDE,
         "payload": "dado",
         "reason": (f"entraram {entrada_deriv} documentos, saíram "
                    f"{total_derivado} textos — cada um com pai e impressão "
                    f"digital do pai. PERDIDOS: {C['LOST']}. A conta é entre "
                    f"etapas comparáveis (documentos × textos), nunca "
                    f"ocorrências menos conteúdos."),
         "evidence": [{"file": "data/derivados/REGISTO-DE-ARTEFATOS.json",
                       "line": 1,
                       "snippet": f"{total_derivado} artefatos derivados"}]},
        {"from": "C-IT-TEXTO-DERIVADO", "to": "C-ADMISSAO", "type": "ALIMENTA",
         "kind": "technical", "status": VERDE, "payload": "dado",
         "reason": (f"A porta viu {C['ADMISSION_SEEN']} textos e decidiu: "
                    f"{resumo_adm or 'nada'}."),
         "evidence": [{"file": "coleta/golden_path_pdf.py", "line": 1,
                       "snippet": f"ADMISSION_SEEN={C['ADMISSION_SEEN']}"}]},
    ]

    # O RAMO DO OCR SO EXISTE SE HOUVER OCR POR FAZER. Desenhar um caminho
    # vazio seria mostrar um problema que nao existe — e um mapa que mostra
    # problemas imaginarios treina toda a gente a ignorar os avisos.
    if C["RAW_NEEDS_OCR"]:
        nos.append({
            **comum, "id": "C-IT-NEEDS-OCR", "name": "Por ler: precisa de OCR",
            "icon": "◍", "territory": "Z-GUARDA",
            "family": FAMILIA_DA_ZONA["Z-GUARDA"],
            "status": CINZA, "ui_status": "gray",
            "what": (f"{C['RAW_NEEDS_OCR']} PDF abriram bem e não tinham letra "
                     f"nenhuma por dentro: são fotografia de papel."),
            "why_here": ("NEEDS_OCR não é rejeição. É um trabalho que ainda "
                         "não foi feito."),
            "facts": [f"PDF sem camada de texto: {C['RAW_NEEDS_OCR']}",
                      "OCR NÃO está implementado — e não se desenha como se "
                      "estivesse"],
            "status_reason": ("NÃO SEI o que está escrito nestes. Precisam de "
                              "OCR, que não é parte desta missão."),
        })
        ligacoes.append({
            "from": "C-IT-PDF-BRUTO", "to": "C-IT-NEEDS-OCR",
            "type": "NEEDS_OCR", "kind": "technical", "status": CINZA,
            "payload": "dado",
            "reason": (f"{C['RAW_NEEDS_OCR']} dos {C['RAW_INPUT']} PDF não têm "
                       f"camada de texto. Trabalho por fazer, não rejeição."),
            "evidence": [{"file": "system-map/data/golden-path-pdf.generated.json",
                          "line": 1,
                          "snippet": f"RAW_NEEDS_OCR={C['RAW_NEEDS_OCR']}"}]})

    return nos, ligacoes


# O que faz um ficheiro conseguir CHEGAR a um canal. Sem uma destas, ele nao
# fala com a rede — e entao nao pode ser a prova de que algo veio de la.
_io = __import__("io")
_tokenize = __import__("tokenize")
_RE_REDE = __import__("re").compile(
    r"urllib|requests\.|http\.client|urlopen|fetch\(|apify|yt_dlp|playwright"
    r"|navegador|cdp|curl", __import__("re").I)
_CACHE_REDE: dict = {}
_CACHE_CODIGO: dict = {}


_NOMES_DE_CANAL = ("YOUTUBE", "INSTAGRAM", "FACEBOOK", "LINKEDIN", "TIKTOK",
                   "MASTODON", "PODCAST", "X", "WEB", "API")


def _e_lista_de_canais(linha: str) -> bool:
    """Uma linha que nomeia TRES canais ou mais e um vocabulario, nao uma rota.

    Ninguem colhe do Facebook e do LinkedIn e do YouTube na mesma linha. Quem
    escreve os tres juntos esta a declarar uma LISTA — um tuplo de rotulos, um
    ciclo, um mapa de traducao.

    O sinal do ficheiro (`_fala_com_a_rede`) nao chega para este caso, porque
    a lista pode viver dentro de um modulo que fala com a rede por outras
    razoes: `coleta/social_scrap.py:205` e exactamente isso.

    Contraste que a regra preserva: `social_rotas.py:298` e
    `def youtube_buscar(...)` — UM canal, e uma funcao que o vai buscar.
    """
    import re as _r
    return sum(1 for c in _NOMES_DE_CANAL
               if _r.search(r"\b%s\b" % c, linha)) >= 3


_RE_NAO_ACONTECEU = __import__("re").compile(
    r"NOT_TESTED|NAO_VERIFICADO|NOT_RUN|NAO_RODOU|NAO_CORREU|NUNCA_RODOU"
    r"|PROIBID[AO]|RECUSAD[AO]|BLOQUEAD[AO]|SEM_ADAPTADOR|NOT_PRESERVED")


def _diz_que_nao_aconteceu(linha: str) -> bool:
    """A linha declara, ela propria, que aquela rota NAO foi exercida.

    ⚠️ QUARTA VOLTA, E A ULTIMA QUE E DECIDIVEL SEM ADIVINHAR.

    As tres regras anteriores olham para a FORMA da linha — quantos canais tem,
    se ha um dominio nu. Esta le o que a linha DIZ. Depois de excluida a tabela
    de hosts, as tres travessias de `C-CORPUS` caiam na linha seguinte:

        coleta/speaker_identidade.py:490
            {'LINKEDIN': 'NOT_TESTED', 'YOUTUBE': 'NOT_TESTED',

        O MAPA ESTAVA A DESENHAR UMA TRAVESSIA
        COM BASE NUMA LINHA QUE DIZ «NOT_TESTED».

    E a lei da casa ao contrario: `DECLARED != OBSERVED` e
    `ERROR != REJECTED != UNKNOWN != NOT_RUN`. Nenhum destes rotulos afirma
    passagem; todos afirmam o contrario. O que sobrevive continua a sobreviver:
    `'YOUTUBE': ('streamers~youtube-scraper', 'JA_RODOU_NESTA_CASA')` diz, na
    propria linha, que ja correu nesta casa.
    """
    return bool(_RE_NAO_ACONTECEU.search(linha))


_RE_HOST_NU = __import__("re").compile(
    r"""['"]([a-z0-9-]+(?:\.[a-z0-9-]+)+)['"]""")


def _e_tabela_de_hosts(linha: str) -> bool:
    """Uma linha que emparelha um DOMINIO com o nome do canal RECONHECE, nao colhe.

    ⚠️ TERCEIRA VOLTA DA MESMA LICAO, e a mais fina das tres.

        coleta/speaker_identidade.py:169-171
            ('linkedin.com', 'LINKEDIN'),
            ('youtube.com', 'YOUTUBE'), ('youtu.be', 'YOUTUBE'),
            ('instagram.com', 'INSTAGRAM'),

    Por causa destas tres linhas, `C-CORPUS` aparecia a receber do LinkedIn, do
    YouTube e do Instagram. Nao recebe: a tabela `HOSTS` existe para RECONHECER
    o dominio de uma URL que o proprio investigador declarou no campo
    `researcher-urls` do ORCID — o comentario por cima di-lo em voz alta,
    «nao e busca por nome, nao e scraping [...] e declaracao». A unica rede
    daquele ficheiro e `pub.orcid.org`.

    Os dois sinais anteriores nao chegam aqui: o ficheiro FALA com a rede (fala
    com o ORCID) e a linha nomeia UM canal so.

        COMPARAR UMA URL COM UM DOMINIO
        NAO E TER IDO BUSCAR ALGO A ESSE DOMINIO.

    O sinal que decide e o DOMINIO NU — `youtu.be`, sem esquema e sem caminho.
    Ninguem colhe de uma string dessas; compara-se com ela. As rotas a serio
    desta arvore nao se parecem com isso e ficam todas de pe: `import
    urllib.request`, `def youtube_buscar(...)`, `import instagram_pessoal`, e o
    mapa de atores `'YOUTUBE': ('streamers~youtube-scraper', ...)`, cujo lado
    direito e um id de ator e nao um dominio.
    """
    return bool(_RE_HOST_NU.search(linha))


def _so_o_codigo(caminho: str) -> str:
    """O ficheiro sem comentarios, sem docstrings e sem NENHUMA string.

    ⚠️ SEGUNDA VOLTA DA MESMA LICAO. A primeira excluiu o vocabulario que vive
    num modulo SEM rede. Esta exclui o vocabulario que vive num modulo que
    parece ter rede — e nao tem, porque a unica palavra de rede no ficheiro esta
    DENTRO DE ASPAS, e e o nome de um campo de relatorio:

        coleta/sensor_canal_identidade.py:224   'APIFY_RUNS': 0, 'COST_USD': 0,
        coleta/social_scrap.py:377              'APIFY_CHAMADA': False,

        UM CAMPO QUE REGISTA ZERO CHAMADAS A APIFY
        NAO E UMA CHAMADA A APIFY.

    E o contrario do que o mapa desenhava: por causa dessas duas linhas, o canal
    LINKEDIN aparecia ligado a `C-CORPUS` e a `C-SCRAP-SOCIAL`. A prova da
    segunda era `social_scrap.py:135` — `('LINKEDIN', 'FETCH_POST', {})` — uma
    linha do bloco ADVERSARIAL, cujo comentario diz «rotas que a matriz declara
    proibidas [...] TÊM que falhar». O mapa estava a desenhar como travessia
    exactamente a rota que aquele bloco existe para provar RECUSADA.

    Ficam de pe as chamadas a serio: `import apify_pool` e um NOME no codigo, e
    `urlopen(` tambem. Medido: dos 11 ficheiros que provavam um `VIAJA_POR`,
    NOVE mantem-se e DOIS caem — os dois de cima.
    """
    achado = _CACHE_CODIGO.get(caminho)
    if achado is None:
        try:
            texto = (RAIZ / caminho).read_text(encoding="utf-8", errors="replace")
            pedacos = [t.string for t in _tokenize.generate_tokens(
                _io.StringIO(texto).readline)
                if t.type not in (_tokenize.COMMENT, _tokenize.STRING)]
            achado = " ".join(pedacos)
        except (OSError, SyntaxError, IndentationError,
                _tokenize.TokenError, ValueError):
            # Nao dando para separar codigo de prosa, nao se finge que deu: o
            # ficheiro inteiro volta, e a regra de cima decide como antes.
            try:
                achado = (RAIZ / caminho).read_text(encoding="utf-8",
                                                    errors="replace")
            except OSError:
                achado = ""
        _CACHE_CODIGO[caminho] = achado
    return achado


def _fala_com_a_rede(caminho: str) -> bool:
    """O ficheiro consegue, sequer, chegar a um canal?

    ⚠️ ISTO PINTAVA CARTOES DE VERDE SEM NINGUEM PASSAR POR ELES.
    `V-FACEBOOK` estava VERDE com «2 acoes da coleta passam por aqui», e uma
    das duas provas era:

        coleta/social_persistencia.py:75
            'FACEBOOK': 'facebook', 'X': 'x', 'WEB': 'web',

    um dicionario que traduz o nome da plataforma para o valor que o banco
    aceita. O ficheiro nao faz UMA chamada de rede.

        NOMEAR UMA PLATAFORMA NUM VOCABULARIO
        NAO E UM CANAL POR ONDE ALGO VIAJOU.

    A regra ja excluia PROSA — «o muro do Instagram» — ao exigir maiusculas. O
    que faltava era excluir VOCABULARIO, que vem em maiusculas tambem. O sinal
    que separa os dois nao esta na linha: esta no ficheiro. Quem nao consegue
    abrir uma ligacao nao pode testemunhar uma travessia.

    Medido: das 20 provas de `VIAJA_POR`, cinco vinham de ficheiros sem rede —
    quatro do mapa de nomes acima e uma de `coleta/filas.py`, que le uma lista
    ja versionada em `data/samples/`. As quinze restantes mantiveram-se.
    """
    v = _CACHE_REDE.get(caminho)
    if v is None:
        v = bool(_RE_REDE.search(_so_o_codigo(caminho)))
        _CACHE_REDE[caminho] = v
    return v


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
        # SEM «ignorar maiusculas», e de proposito. Com ela, o teste da constante
        # `INSTAGRAM` casava com a palavra «Instagram» no meio de uma frase — que
        # e exatamente o que ele existia para excluir. A regra so vale se
        # distinguir `PLATFORM = INSTAGRAM` de «o muro do Instagram».
        rx = _re.compile(padrao)
        quem, provas = [], []
        for a in acoes:
            for f in a.get("_files", []):
                cam = RAIZ / f
                if not cam.is_file():
                    continue
                try:
                    linhas = sem_comentarios(
                        cam.read_text(encoding="utf-8", errors="replace")).splitlines()
                except OSError:
                    continue
                # DOIS SINAIS, e cada um apanha o que o outro deixa passar.
                # O do FICHEIRO exclui o vocabulario que vive num modulo sem
                # rede (`social_persistencia.py`, o mapa de nomes para o
                # banco). O da LINHA exclui o vocabulario que vive DENTRO de
                # um modulo com rede — `social_scrap.py:205` e
                # `for plat in ('YOUTUBE','INSTAGRAM','TIKTOK','FACEBOOK',...)`,
                # um ciclo sobre uma lista, num ficheiro que fala com a rede
                # por outras razoes.
                if not _fala_com_a_rede(f):
                    continue
                achou = next(((i, l) for i, l in enumerate(linhas, 1)
                              if rx.search(l) and not _e_lista_de_canais(l)
                              and not _e_tabela_de_hosts(l)
                              and not _diz_que_nao_aconteceu(l)), None)
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
                     + [f"acoes da coleta que nomeiam este canal: {len(quem)}"]
                     + [f"prova: {p['file']}:{p['line']}" for p in provas[:5]],
            # O QUE ESTA LINHA PODE E O QUE NAO PODE DIZER. Ela mede uma coisa
            # so: o codigo daquela acao NOMEIA este canal, numa linha que nao e
            # vocabulario, nem tabela de dominios, nem rotulo a dizer que a rota
            # nao foi exercida. Isso e DECLARACAO, e nao passagem.
            #
            #     O CODIGO NOMEAR UM CANAL NAO E ALGO TER VINDO POR ELE.
            #
            # Dizer «cada uma tem ficheiro e linha que o prova» convidava a ler
            # como travessia observada aquilo que e, quando muito, rota
            # declarada. Quem quiser a travessia tem de a ver no rasto da
            # corrida, e nao no grep.
            "status_reason": (
                f"{len(quem)} acao(oes) NOMEIAM este canal no codigo, cada uma com "
                f"ficheiro e linha. Isto e rota DECLARADA: nao diz que algo passou "
                f"por aqui, so que o caminho esta escrito." if quem else
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
            "precisa_de_ferramenta": vid != "V-HTTP",
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
        # ── QUE FERRAMENTA ABRE ESTE CANAL ──────────────────────────────
        # O Instagram pode ser aberto pela rota paga OU pelo navegador, e ate
        # aqui o mapa nao dizia por qual — quem olhava tinha de adivinhar se
        # aquela coleta ia custar dinheiro. Mede-se no FICHEIRO onde o canal
        # aparece: se ali tambem se chama a Apify, e a Apify que o abre.
        # O PEDIDO HTTP DIRETO NAO PRECISA DE FERRAMENTA — e essa e a definicao
        # dele. Ele aparecia ligado a Apify e ao navegador porque a medicao e
        # feita POR FICHEIRO, e um coletor que usa varias rotas e varios canais
        # mistura tudo no mesmo texto. Ligar o HTTP direto a rota paga daria a
        # entender que aquela coleta custa dinheiro, quando nao custa.
        for fid, rxf in ({} if vid == "V-HTTP" else ROTAS_DO_CANAL).items():
            rf = _re.compile(rxf, _re.I)
            for pr in provas:
                cam = RAIZ / pr["file"]
                if not cam.is_file():
                    continue
                linhas = cam.read_text(encoding="utf-8", errors="replace").splitlines()
                achou = next(((i, l) for i, l in enumerate(linhas, 1)
                              if rf.search(l) and not l.strip().startswith("#")), None)
                if achou:
                    ligacoes.append({
                        "acao": fid, "veiculo": vid, "abre_o_canal": True,
                        "file": pr["file"], "line": achou[0],
                        "snippet": achou[1].strip()[:150]})
                    break

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




# ── AS SETE NATUREZAS DE UMA LIGACAO ───────────────────────────────────────
# O mapa desenhava tres: FLUXO, MONTAGEM, DISPARO. E duas delas saiam com o
# mesmo traco, o que punha «este modulo importa aquele» e «este workflow manda
# aquele correr» a parecer a mesma coisa. Sao relacoes de naturezas diferentes,
# e quem le nao tinha como as separar.
#
#     DATA     um item sai mesmo de uma peca e entra noutra
#     CONTROL  uma peca manda outra executar
#     READ     uma peca le artefato que outra produziu ou mantem
#     RULE     uma peca consulta uma lei/contrato para decidir
#     WRITE    uma peca guarda resultado num sitio (ficheiro, banco)
#     PROOF    um teste, auditoria ou medicao observa outra peca
#     CODE     dependencia tecnica pura: import, modulo partilhado
#     UNKNOWN  nao se conseguiu classificar — e fica NAO SEI, nunca DATA
#
# A REGRA MAIS IMPORTANTE DESTA TABELA E O QUE ELA PROIBE:
#
#     CODE NAO E DATA. READ NAO E DATA. CONTROL NAO E DATA. PROOF NAO E DATA.
#
# Dois modulos conversarem nao prova que um item passou de um para o outro. Um
# `import` prova que ha dependencia de codigo, e mais nada. Inventar DATA a
# partir de um import faz o mapa desenhar um caminho de dado que nunca existiu —
# e um caminho falso e pior que um caminho em falta, porque ninguem o procura.
DATA, CONTROL, READ, RULE = "DATA", "CONTROL", "READ", "RULE"
WRITE, PROOF, CODE, DESCONHECIDA = "WRITE", "PROOF", "CODE", "UNKNOWN"

CATEGORIAS = (DATA, CONTROL, READ, RULE, WRITE, PROOF, CODE, DESCONHECIDA)

# O tipo cru continua a existir e a ser guardado: e ele que carrega a evidencia.
# Isto e so a traducao para a linguagem visual — normalizacao, nao camada nova.
CATEGORIA_DO_TIPO = {
    # o item atravessa mesmo a linha, e ha evidencia da entrega
    "VIAJA_POR": DATA,          # a colheita vem do canal para a acao
    "FEEDS": DATA,              # a camada de dado alimenta a tela
    "ENTREGA_A_LISTA": DATA,    # as fontes entregam ao canal a lista de contas
    # ⚠️ ESTES QUATRO FALTAVAM, E ERAM A ESPINHA.
    # Sem traducao, caiam em UNKNOWN — e as SEIS unicas ligacoes UNKNOWN do mapa
    # inteiro eram exactamente a esteira da coleta:
    #
    #   PDF BRUTO -DERIVA_TEXTO-> EXECUTOR -PRODUZ-> TEXTO DERIVADO
    #             -ALIMENTA-> ADMISSAO -PRODUZ-> READY
    #
    # As 112 arestas de `import` estavam todas classificadas como CODE, com
    # cuidado. O caminho por onde o dado anda de verdade e que nao tinha nome.
    #
    #     O MAPA CLASSIFICOU OS IMPORTS E DEIXOU A ESTEIRA POR CLASSIFICAR.
    #
    # Quatro delas trazem `payload: dado` escrito pelo proprio gerador; e por
    # elas que o artefato viaja, uma etapa para a seguinte.
    "DERIVA_TEXTO": DATA,       # o bruto entra no executor e sai texto
    "DERIVA_TEXTO_A_MAO": DATA, # a mesma travessia, por rota manual
    "PRODUZ": DATA,             # a etapa produz o artefato da etapa seguinte
    "ALIMENTA": DATA,           # o artefato chega a etapa que o consome
    # ordem de execucao
    "RUNS": CONTROL,
    "ABRE_O_CANAL": CONTROL,    # e por esta ferramenta que se chega la
    # leitura e escrita
    "READS": READ,
    "WRITES": WRITE,
    "RETRIEVED_BY": READ,
    # dependencia de codigo
    "IMPORTS": CODE,
}

# Uma peca destas de um dos lados torna a ligacao PROOF, seja qual for o tipo
# cru: o que atravessa a linha e uma observacao, nao trabalho.
KINDS_QUE_PROVAM = {"test"}

# E uma leitura cujo OUTRO lado e uma lei nao e leitura de dado: e consulta de
# regra. A diferenca importa porque uma regra consultada nao carrega item — e
# quem procura o caminho do dado nao a quer no meio.
#
# MAS «LEI» E ONDE ELA MORA, NAO O QUE ALGUEM ESCREVEU NA FICHA DELA.
# A primeira versao usava `kind == "contract"`, e «O que a ADAMA sabe de si» saiu
# como RULE — quando ele e o CATALOGO comercial, um artefato de dado. Esta
# declarado como `contract` na ficha, e a regra herdou o engano em silencio.
#
# Uma lei desta casa vive numa das gavetas de lei. Isso e medido, nao declarado —
# e se alguem mover a peca, a classificacao acompanha sozinha.
ZONAS_DE_LEI = {"Z-REGRAS", "Z-MEDIDAS", "Z-REGUAS"}


def categoria_da_ligacao(tipo, no_de, no_para):
    """A natureza visual de uma ligacao. Nunca devolve DATA por omissao.

    A ordem das perguntas e a regra:
      1. algum dos lados prova? entao e PROOF, mesmo que o tipo cru seja outro
      2. e uma leitura de uma lei? entao e RULE, nao READ
      3. o tipo cru tem traducao? usa-se
      4. caso contrario UNKNOWN — e UNKNOWN e uma resposta, nao uma falha
    """
    kinds = {(no_de or {}).get("kind"), (no_para or {}).get("kind")}
    if kinds & KINDS_QUE_PROVAM:
        return PROOF
    if (tipo in ("READS", "IMPORTS")
            and (no_de or {}).get("territory") in ZONAS_DE_LEI):
        return RULE
    return CATEGORIA_DO_TIPO.get(tipo, DESCONHECIDA)

# ── AS FERRAMENTAS NAO SERVEM TODAS NO MESMO MOMENTO ────────────────────────
# «Apify» e «a fala vira texto» estavam na mesma gaveta com o mesmo peso, e nao
# fazem o mesmo trabalho nem na mesma altura:
#
#     ROTA     serve ANTES  — e como se chega ao canal
#     PREPARO  serve DEPOIS — e o que se faz com o que voltou, antes da peneira
#     DESPACHO nao e rota nem preparo — e o botao que manda tudo isto correr
#
# A transcricao e o caso que torna a diferenca obvia: ela baixa o video (rota) e
# transforma-o em texto (preparo) — e e ESSE TEXTO que a porta de admissao le.
# Sem ela, o item chega a porta sem uma palavra, e sai NAO_SEI. Chamar-lhe so
# «ferramenta» esconde que ela e um degrau do caminho, nao um acessorio.
# A ORDEM DESTA TABELA E A REGRA, e ja a tive errada duas vezes.
#
# Primeiro pus PREPARO a frente e o «SINTONIA SCRAP» virou preparo — porque o
# ficheiro dele menciona o transcritor. Ele nao transcreve: ele MANDA
# transcrever. Depois pus ROTA a frente e virou tudo rota, porque o transcritor
# tambem baixa o video e menciona a rota.
#
# A licao e a mesma nas duas: uma ferramenta que fala de varias etapas nao se
# classifica pela palavra que aparece — classifica-se pelo TRABALHO QUE ELA FAZ.
#     um workflow e um botao, diga ele o que disser la dentro
#     quem transcreve e PREPARO, mesmo que baixe o video para o fazer
#     so depois disso e que sobra a rota
MOMENTO_DA_FERRAMENTA = (
    ("DESPACHO", None,  # decidido pelo tipo de ficheiro, nao pelo conteudo
     "nao e rota nem preparo: e o botao que manda correr"),
    ("PREPARO", r"whisper|transcrev|pdf_peek|html_text|ods_peek|pdfplumber|PyPDF",
     "depois da coleta, sobre o que voltou — antes da peneira"),
    # sem : o heredoc que escreveu esta linha transformava a barra num
    # caractere de controlo invisivel, e a regra nunca casava com nada.
    ("ROTA", r"apify|playwright|selenium|chrome-devtools|[_./]cdp",
     "antes da coleta, para chegar ao canal"),
)

# So estas contam como ROTA para um canal. A transcricao TOCA o canal (baixa de
# la), mas nao e por ela que se decide ir — e por isso nao entra aqui.
ROTAS_DO_CANAL = {
    "C-APIFY-POOL": r"apify",
    "C-NAVEGADOR": r"playwright|selenium|cdp|navegador",
}


def momento_das_ferramentas(nos: list) -> None:
    """Diz, em cada ferramenta, QUANDO ela serve. Medido pelo que ela usa."""
    for n in nos:
        if n.get("territory") != "Z-FERRAMENTAS":
            continue
        texto = ""
        for f in n.get("files", []):
            cam = RAIZ / f
            if cam.is_file():
                texto += cam.read_text(encoding="utf-8", errors="replace")[:200000]
        so_workflow = all(f.endswith((".yml", ".yaml")) for f in n.get("files", []))
        for etiqueta, padrao, quando in MOMENTO_DA_FERRAMENTA:
            if padrao is None:
                if not (n.get("files") and so_workflow):
                    continue
            elif not re.search(padrao, texto, re.I):
                continue
            if True:
                n["momento"] = etiqueta
                n["momento_texto"] = quando
                break
        else:
            n["momento"] = "NAO SEI"
            n["momento_texto"] = ("NAO SEI quando esta ferramenta serve: nao usa "
                                  "rota conhecida nem trata o que voltou.")


# ── O PAPEL DE UMA PECA NO PLANO DE CONTROLO ────────────────────────────────
# «Escolhe executor» aparecia em tres pecas: a receita, o orquestrador e o
# SINTONIA SCRAP. A mesma pergunta — «como atender este pedido?» — respondida em
# tres sitios. Uma responsabilidade com tres donos nao tem dono.
#
# Isto nao consolida nada: so poe no cartao o que a peca REALMENTE faz, medido,
# para se poder ver a duplicacao em vez de a deduzir. A consolidacao e decisao
# de produto, e fica para depois de o modelo minimo ser aprovado.
#
#     ARQUIVO NAO E RESPONSABILIDADE. MODULO NAO E ESTACAO.
PAPEIS = (
    # (papel, o que quer dizer, o que tem de ser verdade)
    ("ORQUESTRADOR", "decide como atender o pedido, e assina a corrida",
     lambda m: m["chama_subprocesso"] and m["assina_recibo"]),
    ("EXECUTOR COMPOSTO", "corre varias fases e abre os portoes de cada uma",
     lambda m: m["e_workflow"] and m["executores_que_chama"] >= 3),
    ("BOTAO", "so dispara; nao decide nada",
     lambda m: m["e_workflow"]),
    ("POLITICA INTERNA", "decide, mas nao executa — e tem um so consumidor",
     lambda m: m["decide"] and not m["executa"] and m["consumidores"] <= 2),
    ("CONTRATO", "so representa e valida; nao executa nada",
     lambda m: m["valida"] and not m["executa"] and not m["decide"]),
)

RX_PAPEL = {
    "chama_subprocesso": r"subprocess\.run|os\.system",
    # ESCREVER o recibo, nao mencionar o ficheiro. `apify_contrato.py` fala do
    # RUN-MANIFEST numa frase e saiu classificado como ORQUESTRADOR — a mesma
    # armadilha do Supabase e do Instagram: mencionar nao e usar.
    "assina_recibo": r"guardar_recibo\(",
    "acessa_rede": r"requests\.(get|post)|httpx|urllib\.request|aiohttp",
    "grava": r"open\([^)]*['\"][wa]|write_text\(|json\.dump\(",
    # decidir e ter a TABELA de executores ou resolver um plano — nao e a
    # palavra «escolhe» solta numa linha
    "decide": r"EXECUTORES\b|resolver\(",
    "valida": r"raise \w*Invalid|PedidoInvalido",
}


def papel_das_pecas(nos: list) -> None:
    """Poe em cada peca do plano de controlo o papel que ela DESEMPENHA."""
    # SO O PLANO DE CONTROLO. Uma ferramenta nao tem «papel de controlo» — o
    # papel dela ja esta medido noutro sitio, e chama-se `momento` (ROTA,
    # PREPARO, DESPACHO). Perguntar a um leitor de PDF se ele e orquestrador
    # devolve NAO SEI, e esse NAO SEI nao ensina nada a ninguem.
    #
    # O despachante entra por ser o unico caso em que um workflow FAZ trabalho
    # de controlo: escolhe portoes e corre seis executores.
    no_controlo = {"Z-PEDIDO"}
    for n in nos:
        if n.get("territory") not in no_controlo and n.get("id") != "C-SINTONIA-SCRAP":
            continue
        ficheiros = n.get("files", [])
        texto = ""
        for f in ficheiros:
            cam = RAIZ / f
            if cam.is_file():
                bruto = cam.read_text(encoding="utf-8", errors="replace")
                texto += "\n".join(
                    "" if l.lstrip().startswith(("#", "//")) else l.split("#", 1)[0]
                    for l in bruto.splitlines())

        m = {k: bool(re.search(rx, texto, re.I)) for k, rx in RX_PAPEL.items()}
        m["e_workflow"] = bool(ficheiros) and all(
            f.endswith((".yml", ".yaml")) for f in ficheiros)
        m["executa"] = m["chama_subprocesso"] or m["acessa_rede"] or m["grava"]
        m["executores_que_chama"] = len(re.findall(
            r"(?:coleta|fontes|candidatas)/[A-Za-z0-9_-]+\.py", texto))
        m["consumidores"] = len(n.get("outbound", []))

        for papel, o_que_e, cabe in PAPEIS:
            if cabe(m):
                n["papel"] = papel
                n["papel_texto"] = o_que_e
                break
        else:
            n["papel"] = "NAO SEI"
            n["papel_texto"] = ("nao encaixa em nenhum papel conhecido do plano "
                                "de controlo — e isso e uma resposta, nao um erro")
        n["papel_medido"] = {k: v for k, v in m.items() if k != "consumidores"}


# ── A AVENIDA PRINCIPAL E AS RUAS DE DENTRO ────────────────────────────────
# O mapa era um diagrama de FICHEIROS: cada modulo virava uma caixa do mesmo
# tamanho, e a receita — que e politica interna do orquestrador, com um unico
# consumidor — competia visualmente com o orquestrador.
#
#     ARQUIVO NAO E RESPONSABILIDADE. MODULO NAO E ESTACAO.
#
# Estas zonas sao a avenida: as responsabilidades de topo da coleta. Tudo o
# resto continua no mapa, continua clicavel, continua no ficheiro gerado — mas
# sai da avenida. NADA DESAPARECE: agrupar nao e apagar, e uma peca escondida
# por conveniencia visual e uma peca que ninguem vai auditar.
AVENIDA = ("Z-ENTRADA", "Z-ORQUESTRADOR", "Z-EXECUCAO", "Z-ADMISSAO")

# Estas quatro fecham o caminho do controlo. Uma seta entre elas e canonica;
# uma seta que salta uma delas e um desvio, e o mapa tem de o mostrar em vez de
# o esconder — senao a reorganizacao vira maquilhagem.
CAMINHO_CANONICO = ("Z-ENTRADA", "Z-ORQUESTRADOR", "Z-EXECUCAO", "Z-ADMISSAO")


def nivel_das_pecas(nos: list) -> None:
    """PRINCIPAL na avenida, INTERNO no raio-X. Ninguem e removido."""
    for n in nos:
        n["nivel"] = "PRINCIPAL" if n.get("territory") in AVENIDA else "INTERNO"


def quem_salta_o_cerebro(nos: list) -> None:
    """Quem dispara trabalho sem passar pelo orquestrador. Medido na peca.

    A primeira versao so olhava para as SETAS que saem da entrada, e por isso
    nao via o caso maior: o SINTONIA SCRAP dispara seis executores e nao tem
    ligacao nenhuma com o orquestrador — nao ha seta para encontrar, e a
    ausencia de seta nao aparece a procurar setas.

        O DESVIO MAIS CARO E O QUE NAO DEIXA RASTO.

    Reorganizar a avenida sem mostrar isto seria maquilhagem: o desenho ficava
    certo e a casa continuava a funcionar por fora dele.
    """
    QUEM_DISPARA = {"BOTAO", "EXECUTOR COMPOSTO"}
    for n in nos:
        if n.get("papel") not in QUEM_DISPARA:
            continue
        toca_o_cerebro = "C-ORQUESTRADOR" in (
            set(n.get("inbound") or []) | set(n.get("outbound") or []))
        n["salta_o_orquestrador"] = not toca_o_cerebro
        n["salta_porque"] = ("" if toca_o_cerebro else
                             "dispara trabalho e nao tem ligacao nenhuma com o "
                             "orquestrador: a decisao de COMO atender esta aqui "
                             "dentro, e nao no unico sitio que devia decidi-la")


def desvios_do_controlo(ligacoes: dict, nos: list) -> list:
    """As setas que saltam o orquestrador — medidas, nao supostas.

    O modelo aprovado e ENTRADA -> ORQUESTRADOR -> EXECUCAO. Uma seta que sai da
    entrada e cai direto num executor, numa ferramenta ou num canal salta o
    cerebro: a decisao de COMO atender fica no botao.
    """
    zona = {n["id"]: n.get("territory") for n in nos}
    DEPOIS_DO_CEREBRO = {"Z-EXECUCAO", "Z-ACOES", "Z-FERRAMENTAS", "Z-VEICULOS"}
    fora = []
    for l in ligacoes.values():
        if l.get("kind") != "technical":
            continue
        de, para = zona.get(l["from"]), zona.get(l["to"])
        salta = (de == "Z-ENTRADA" and para in DEPOIS_DO_CEREBRO) or \
                (para == "Z-ENTRADA" and de in DEPOIS_DO_CEREBRO)
        if salta and l.get("categoria") in ("CONTROL", "CODE", "DATA", "READ"):
            l["desvio"] = True
            l["desvio_porque"] = (
                "sai da ENTRADA direto para a execucao, sem passar pelo "
                "ORQUESTRADOR: a decisao de COMO atender ficou no botao")
            fora.append(l)
    return fora


# ── QUE PALAVRAS A ITALIA RECEBE, E DE QUE LINGUA SAO ───────────────────────
# A busca foi corrigida e a porta ficou para tras: ela decidia sobre item
# ITALIANO com 28 palavras em PORTUGUES, e contra o unico texto italiano real
# desta arvore UMA casava. Isso nao dava NAO_SEI — dava «nao pertence a este
# universo». Uma peneira que fala outra lingua rejeita tudo com ar de quem julgou.
#
# O mapa tem de conseguir mostrar isto sem despejar mil palavras no ecra: por
# peca, quantas palavras, de que lingua, e quantas sao de pais que nao e o desta
# rota. NAO E UMA LISTA — E UM TERMOMETRO.
#
#     TERMO QUE EXISTE EM VARIAS LINGUAS NAO E CONTAMINACAO. `doi`, `orcid`,
#     `fungo`, `evento`, `decreto` valem em toda a parte. Contaminacao e o termo
#     EXCLUSIVO de outro pais numa rota que nao e dele.
SO_DE_UM_PAIS = {
    "ES": r"^(repilo|olivar|jornada|septoriosis|trigo|espanol)$",
    "FR": r"^(mildiou|septoriose|webinaire|vigne|ble|francais)$",
    "PT": r"^(estudo|pesquisa|revista|artigo|universidade|instituto|publicacao|"
          r"lancamento|campanha|produto|anuncio|autorizacao|rotulo|bula|praga|"
          r"doenca|inseto|infestacao|sintoma)$",
    "IT": r"^(studio|ricerca|rivista|articolo|universita|istituto|pubblicazione|"
          r"convegno|sperimentazione|tesi|lancio|campagna|prodotto|annuncio|"
          r"novita|fiera|autorizzazione|etichetta|foglietto|registrazione|"
          r"gazzetta|parassita|malattia|insetto|infestazione|sintomo|avversita|"
          r"patogeno|diserbo|infestanti|difesa|malattie|frumento|grano|melo|"
          r"pomodoro|riso|mais|olivo|vite|soia|bietola)$",
}

# Que papel cada lista tem. Confundir busca com admissao foi o erro: encontrar um
# material e decidir se ele serve sao perguntas diferentes, e podem — devem —
# ter vocabularios diferentes.
PAPEL_DO_VOCABULARIO = {
    "C-PALAVRAS": "BUSCA",
    "C-ADMISSAO": "ADMISSAO",
    "C-ROTULOS-CENSO": "BUSCA/EXTRACAO",
}

RX_LISTA = re.compile(r"^\s*([A-Z][A-Z0-9_]{3,})\s*=\s*[\[({]", re.M)


def vocabulario_das_pecas(nos: list) -> None:
    """Por peca: quantas palavras, de que lingua, e quantas sao de fora."""
    import ast as _ast
    compilados = {k: re.compile(v) for k, v in SO_DE_UM_PAIS.items()}

    for n in nos:
        listas = {}
        for f in n.get("files", []):
            cam = RAIZ / f
            if not cam.is_file() or cam.suffix != ".py":
                continue
            try:
                arv = _ast.parse(cam.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for no in _ast.walk(arv):
                if not isinstance(no, _ast.Assign) or len(no.targets) != 1:
                    continue
                alvo = no.targets[0]
                if not isinstance(alvo, _ast.Name) or not alvo.id.isupper():
                    continue
                palavras = [x.value.lower() for x in _ast.walk(no.value)
                            if isinstance(x, _ast.Constant)
                            and isinstance(x.value, str) and 2 < len(x.value) < 40]
                if len(palavras) >= 5:
                    listas.setdefault(alvo.id, []).extend(palavras)
        if not listas:
            continue

        todas = [w for v in listas.values() for w in v]
        por_lingua = {}
        for w in todas:
            for k, rx in compilados.items():
                if rx.match(w.split()[0] if " " in w else w):
                    por_lingua[k] = por_lingua.get(k, 0) + 1
                    break
        # a rota desta peca e a Italia; PT/ES/FR aqui sao de fora
        de_fora = {k: v for k, v in por_lingua.items() if k in ("ES", "FR")}
        n["vocabulario"] = {
            "papel": PAPEL_DO_VOCABULARIO.get(n["id"], "NAO SEI"),
            "listas": sorted(listas),
            "palavras": len(todas),
            "por_lingua": dict(sorted(por_lingua.items(), key=lambda x: -x[1])),
            "sem_marca_de_lingua": len(todas) - sum(por_lingua.values()),
            "de_outro_pais": sum(de_fora.values()),
            "de_outro_pais_quais": dict(sorted(de_fora.items())),
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
          "```bash", "py medidas/padrao_da_coleta.py", "```", "",
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
    #
    # E O ARTEFACTO COM DOIS AUTORES? A eleicao aqui e por ordem alfabetica, e
    # isso nunca se tinha notado porque so se via UM autor por artefacto — os
    # que escrevem por `pathlib` eram invisiveis para o censo (ver
    # `escritas_por_constante`). Assim que passaram a ver-se, o dono de
    # `data/samples/RUN-MANIFEST.json` mudou sozinho de C-PROCEDENCIA para
    # C-ESTRADA-PDF, sem ninguem ter mexido no repositorio.
    #
    #     UM DONO ELEITO POR ORDEM ALFABETICA NAO E UM DONO.
    #
    # Nao invento o dono certo: registo que ha mais de um, e quem sao. A escolha
    # e de gente, e enquanto nao for feita o mapa diz que nao esta feita.
    produz: dict[str, list] = {}
    autores: dict[str, set] = {}
    for _ in range(2):
        for e in G["FILE_EDGES"]:
            if e["type"] != "WRITES":
                continue
            autor = dono.get(e["from_file"])
            if not autor:
                continue
            autores.setdefault(e["to_file"], set()).add(autor)
            if e["to_file"] not in dono:
                dono[e["to_file"]] = autor
                produz.setdefault(autor, []).append(e["to_file"])

    varios_autores = [{"file": a, "written_by": sorted(p), "owner_elected": dono[a]}
                      for a, p in sorted(autores.items()) if len(p) > 1]

    veiculos, lig_veiculos = os_veiculos(comps, dono, G)
    gerados += veiculos

    pdf_nos, lig_pdf = o_corte_do_pdf()
    gerados += pdf_nos

    gp_nos, lig_gp = a_estrada_do_pdf()
    gerados += gp_nos
    lig_pdf += lig_gp

    arm_nos, lig_arm = o_armazem_sem_livro()
    gerados += arm_nos
    lig_pdf += lig_arm

    der_nos, lig_der = a_casa_do_derivado()
    gerados += der_nos
    lig_pdf += lig_der

    esp_nos, lig_esp = a_sala_de_espera()
    gerados += esp_nos
    lig_pdf += lig_esp

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
        # leitura e virada: quem foi lido ALIMENTA quem leu.
        #
        # E O IMPORT TAMBEM, e isto foi uma correcao. Ele ficava como esta no
        # codigo — importador para importado — e o mapa passava a ter DUAS
        # direcoes ao mesmo tempo: o READS a apontar para a frente, o IMPORTS
        # para tras. Quem seguia uma corrente batia numa seta ao contrario sem
        # aviso, e a leitura partia-se ali.
        #
        # «Colher o YouTube -> As palavras que a busca digita» era o exemplo:
        # lia-se como se o coletor entregasse palavras ao lexico, quando e o
        # lexico que lhe da as palavras. A seta certa e a que segue o que passa
        # na linha — e o que passa num import e o CODIGO do importado a entrar
        # no importador.
        #
        # `RUNS` fica como esta: ali nao passa nada: passa uma ordem, e a ordem
        # vai mesmo de quem manda para quem obedece.
        if e["type"] in ("READS", "IMPORTS"):
            a, b = b, a
        chave = (a, b, e["type"])
        alvo = ligacoes.setdefault(chave, {
            "from": a, "to": b, "type": e["type"], "payload": e["payload"],
            "raw_type": e["type"],
            "kind": "technical", "status": VERDE,
            "reason": "", "evidence": [],
        })
        alvo["evidence"].append(e["evidence"])

    for lig in ligacoes.values():
        n = len(lig["evidence"])
        # O VERBO TEM DE CONCORDAR COM A SETA, e era aqui que ele nao concordava.
        #
        # `IMPORTS` e virado de proposito — o codigo do importado entra no
        # importador — mas o verbo ficou o da direcao antiga. Resultado, em 76
        # arestas: a seta ia de A para B e a frase dizia «A importa B», quando o
        # que o codigo diz e que B importa A. Lida sozinha, cada frase parecia
        # plausivel; e por isso ninguem reparou.
        #
        #     VIRAR UMA SETA E MEIA MUDANCA. A OUTRA METADE E A FRASE.
        #
        # Agora o verbo e escolhido para a direcao GUARDADA, nao para a original.
        verbo = {
            "IMPORTS": "tem o seu codigo importado por",   # virado: importado -> importador
            "READS": "alimenta",                           # virado: lido -> leitor
            "WRITES": "escreve em",                        # nao virado
            "RUNS": "manda rodar",                         # nao virado
            "RETRIEVED_BY": "e buscada por",
        }.get(lig["type"], lig["type"].lower())
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
            # ⚠️ TRES COISAS QUE ESTA LINHA JA CONFUNDIU, E QUE NAO SAO A MESMA:
            #
            #     EXISTE NO DISCO  !=  RASTREADO PELO GIT  !=  NAO EXISTE
            #
            # O inventario `arquivos` vem de `scan_repo.py`, que lista com
            # `git ls-files` — so o que ja foi `git add`ado. Um ficheiro acabado
            # de escrever existe no disco e nao esta la.
            #
            # Em 08/09/2026 isto publicou, e commitou, uma frase FALSA:
            # C-CENSO-OBSERVABILIDADE saiu BROKEN com «declarado no mapa e nao
            # existe no repositorio», e o ficheiro estava no disco, a um
            # `git add` de distancia. Curou-se sozinho no commit seguinte — e e
            # por isso que era perigoso: uma mentira que desaparece antes de
            # alguem a investigar.
            #
            # Perguntar ao DISCO antes de acusar de inexistencia.
            no_disco = sorted(
                p for p in c["files"]
                if (RAIZ / p).exists()
                or glob.glob(str(RAIZ / p), recursive=True))
            if no_disco:
                status, motivo = CINZA, (
                    "⚪ NAO SEI. O ficheiro EXISTE no disco e ainda NAO esta "
                    "rastreado pelo Git; o scanner le `git ls-files`, por isso "
                    "ele nao entra no inventario e nada se prova sobre esta "
                    "peca ainda. Conserto: `git add " + " ".join(no_disco) +
                    "` e regerar. ISTO NAO E «nao existe».")
            else:
                status, motivo = VERMELHO, (
                    "declarado no mapa e nao existe no repositorio: "
                    f"nenhum ficheiro casa com {', '.join(c['files'])}. "
                    "Conferido tambem no disco: nao esta la.")
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
            "payload": "coleta",
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

    # O CORTE do PDF entra como aresta cinzenta: declarada pela medicao, e sem
    # uma linha de codigo que a prove — porque o passo nao existe. E exatamente
    # o que uma aresta cinzenta quer dizer.
    for lp in lig_pdf:
        ligacoes[(lp["from"], lp["to"], lp["type"])] = lp

    for lv in lig_veiculos:
        # AS FONTES entregam ao canal a lista de onde ir. E a unica coisa que um
        # canal recebe, e sem ela «colher o YouTube» nao quer dizer nada:
        # colher o YouTube de quem?
        if lv.get("abre_o_canal"):
            chave = (lv["acao"], lv["veiculo"], "ABRE_O_CANAL")
            alvo_lig = ligacoes.setdefault(chave, {
                "from": lv["acao"], "to": lv["veiculo"], "type": "ABRE_O_CANAL",
                "payload": "rota",
                "kind": "technical", "status": VERDE,
                "reason": ("E por esta ferramenta que se chega a este canal. Um "
                           "canal pode ter mais de uma rota — e saber qual e "
                           "saber se aquela coleta custa dinheiro. MEDIDO NO "
                           "MESMO FICHEIRO: um coletor que usa duas rotas e dois "
                           "canais aparece ligado aos quatro pares, e o mapa nao "
                           "consegue dizer qual rota serviu qual canal."),
                "evidence": [],
            })
            alvo_lig["evidence"].append(
                {k: lv[k] for k in ("file", "line", "snippet")})
            continue
        if lv.get("entrega_lista"):
            chave = ("C-AS-FONTES", lv["veiculo"], "ENTREGA_A_LISTA")
            alvo_lig = ligacoes.setdefault(chave, {
                "from": "C-AS-FONTES", "to": lv["veiculo"], "type": "ENTREGA_A_LISTA",
                "payload": "contas",
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
            "payload": "coleta",
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
            "payload": "dado",
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
    # A ferramenta so sabe QUANDO serve depois de medida — e a linha seguinte
    # depende disso. Ela corria depois, e por isso a reclassificacao nao via
    # preparo nenhum: o conjunto vinha sempre vazio, em silencio.
    momento_das_ferramentas(nos)
    papel_das_pecas(nos)
    vocabulario_das_pecas(nos)
    nivel_das_pecas(nos)
    quem_salta_o_cerebro(nos)

    # ── CADA LIGACAO GANHA A SUA CATEGORIA ──────────────────────────────────
    # Feito aqui, no fim, porque a categoria depende do TIPO das duas pecas —
    # e as pecas geradas (canais, telas, linhagem) so existem a esta altura.
    por_id = {n["id"]: n for n in nos}
    for l in ligacoes.values():
        if l["kind"] != "technical":
            l["categoria"] = PROOF if l.get("payload") == "negocio" else DESCONHECIDA
            continue
        l["categoria"] = categoria_da_ligacao(
            l["type"], por_id.get(l["from"]), por_id.get(l["to"]))

    # A FERRAMENTA DE PREPARO CARREGA O ITEM, e por isso a sua ligacao e DATA.
    # «SINTONIA SCRAP manda para o whisper» era CONTROL — e e — mas o que sai do
    # whisper e o TEXTO do item, e e esse texto que a porta de admissao le. Uma
    # peca que TRANSFORMA o item esta no caminho dele.
    #
    # Isto NAO e inferir DATA de um import: a prova e o que a ferramenta faz
    # (audio entra, texto sai), medido em `momento_das_ferramentas`.
    preparo = {n["id"] for n in nos if n.get("momento") == "PREPARO"}
    # ⚠️ MAS SO QUANDO O OUTRO LADO ESTA NO CAMINHO DO ITEM.
    #
    # A regra acima e boa e estava larga demais: disparava se QUALQUER um dos
    # topos fosse preparo, sem olhar para o outro. Medido, tres ligacoes
    # falsas — e eram justamente as unicas tres que o mapa apresentava como
    # DATA a atravessar a fronteira para a inteligencia:
    #
    #   C-TRANSCRICAO -> C-CENSO-DERIVACOES   um censo a LER o codigo dela
    #   C-LEITORES    -> C-CENSO-DERIVACOES   idem
    #   C-TRANSCRICAO -> C-SCRAP-LEIS         uma lei a ser CONSULTADA
    #
    # Um censo que mede a ferramenta nao recebe o item dela: recebe o texto do
    # ficheiro .py. E uma lei consultada nao carrega item nenhum.
    #
    #     UMA PROVA QUE ME MEDE NAO ESTA NO MEU CAMINHO.
    #     UMA REGRA QUE EU CONSULTO NAO VIAJA COMIGO.
    #
    # Sem esta guarda, o unico DATA que cruzava para a inteligencia era ruido —
    # e um falso atravessamento e pior do que nenhum, porque manda procurar um
    # desvio de dado onde so ha um `import`.
    por_id_ct = {n["id"]: n for n in nos}

    def _fora_do_caminho(i):
        n = por_id_ct.get(i) or {}
        return (n.get("territory") == "Z-PROVA"
                or n.get("territory") in ZONAS_DE_LEI
                or n.get("kind") in ("test", "contract"))

    for l in ligacoes.values():
        if l["kind"] != "technical":
            continue
        toca = (l["from"] in preparo or l["to"] in preparo)
        outro = l["to"] if l["from"] in preparo else l["from"]
        if toca and not _fora_do_caminho(outro):
            if l["categoria"] in (CODE, READ):
                l["categoria"] = DATA
                l["passa_pelo_preparo"] = True

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

    desvios = desvios_do_controlo(ligacoes, nos)

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
        "ARTEFACT_MULTIPLE_AUTHORS": varios_autores,
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
