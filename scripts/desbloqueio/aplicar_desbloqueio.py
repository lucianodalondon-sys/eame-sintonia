"""PACOTE DE DESBLOQUEIO G1 — aplica-se UMA vez, no cutover, sobre o livro corrente.

    py scripts/desbloqueio/aplicar_desbloqueio.py --livro=<italy_contracts_curator.json>
                                                   --tabela=<italy_contracts_onboarded.json>
                                                   [--escrever] [--ledger=<ficheiro .jsonl>]
                                                   [--rota-scrap=SOC2]   # bloco 4

Sem --escrever: so relatorio (antes/depois por SOURCE_ID). Com --escrever: grava os
dois livros e acrescenta ao ledger uma linha por alteracao (MISSAO, PROVA, AT).

DOIS LIVROS, DOIS DONOS DO CAMPO:
  livro   = contratos do Curator. O pacote so muda ACQUISITION.LINK_PATTERN e
            ACQUISITION.INDEX_URL, pelas PROPOSTA-RECEITAS-V1/V2 (6-PREP-d, G0).
  tabela  = contratos do coletor (regras/italy_contracts_onboarded.json). O coletor
            usa a SUA copia da aquisicao. Uma fonte so entra, ou so muda de aquisicao,
            com um canario ROUTE_PROVEN com EXACTAMENTE a aquisicao que fica:
              · as rotas provadas pela M3 (ROTAS-ELEGIVEIS-V1.json), pela regra da
                propria peca da M3 (curadoria/onboardar_rotas_provadas.py): mesma
                aquisicao, e um documento = uma fonte (duplicadas ficam de fora);
              · o canario do G1 (scripts/desbloqueio/CANARIO-DESBLOQUEIO-V1.json).
            A linha da tabela e construida pela `linha_da_tabela` da peca da M3.

CADA ALTERACAO SO SE APLICA SE A PROVA AINDA BATER, senao SALTA com motivo:
  · o valor actual no livro e o ANTES da proposta (senao o livro mudou depois da prova);
  · sha256 de cada pagina guardada = o do manifesto da recolha;
  · o padrao novo casa TODAS as materias confirmadas e NENHUMA das 109 capas do
    GABARITO-CAPA-V1, e passa o guarda contra padrao generico (6-PREP-d);
  · um INDEX_URL novo tem a pagina buscada (sha conferido) e >= 10 links com forma
    de materia confirmada.

INVARIANTES (se falhar um, NADA e escrito, exit 4):
  nunca muda TERRITORY/grupo T nem SOURCE_ID · nunca retira fonte (D5 e do dono) ·
  no livro so mudam os dois campos acima · na tabela so se acrescenta linha ou se
  muda ACQUISITION.
IDEMPOTENTE: correr duas vezes = 0 alteracoes na segunda (a segunda so ve JA_APLICADA).

BLOCO 2 — CATALOGO (D9, 23/09, bot Luciano por delegacao do dono): as linhas MUDAR_PARA_Tx
e RETIRAR_DO_UNIVERSO da PROPOSTA-CATALOGO-V1 (origin/catalogo-proposta-v1), SO com prova
integra (cada ficheiro existe em disco e o sha256 bate). UNKNOWN e MANTER intocados.
  · MUDAR   muda TERRITORY (o SOURCE_ID nao muda: e identidade) e guarda CATALOGO_D9 com
            o universo anterior. E a UNICA excepcao ao «nunca muda grupo T», so para estas linhas.
  · RETIRAR marca ESTADO_CATALOGO = RETIRADA_POR_DECISAO, reversivel. NUNCA apaga.
            Se a prova tiver uma noticia SINTONIA_RELEVANT = YES, vale a D2 (REROUTE): SALTA.
  · a tabela do coletor recebe a mesma marca/universo, se a fonte la estiver.
  · ledger com DECISAO = D9.

BLOCO 4 — ROTA DO SCRAP (SOC2, D17.4), so com --rota-scrap=SOC2: as fontes YouTube do livro
passam a nomear a fase canal-youtube do Scrap; a tabela do coletor ganha COLETADO_POR. So com
prova de identidade (canal do livro = tabela, IDENTITY_MATCH = YES, um canal = uma fonte) e com
o Scrap a declarar HOJE a rota. Nunca muda SOURCE_ID, grupo T, BATCH_ID nem o canal.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
HOME = Path.home()
MISSAO = "G1-DESBLOQUEIO-COORTE"
# A proposta de catalogo que o coordenador conferiu (87 accoes com prova, 23/09).
# Nao e um REF fixo de leitura — le-se pelo nome da branch —, e so a referencia
# contra a qual o pacote AVISA se a branch tiver andado.
CATALOGO_CONFERIDO = "0644a916"
CAMPOS_DO_LIVRO = ("LINK_PATTERN", "INDEX_URL")
MANIFESTOS = [HOME / "detector-capa-gabarito" / "MANIFESTO.json",
              HOME / "receitas-paginas" / "MANIFESTO.json",
              HOME / "coorte-paginas" / "MANIFESTO.json",
              # K1: as paginas do gabarito de controlo LD2 e da recolha LD2 — a V4 prova
              # receitas com elas; o sha256 confere-se aqui como o das outras.
              HOME / "ld2-controlo" / "MANIFESTO.json",
              HOME / "ld2-paginas" / "MANIFESTO.json"]
INDICES = HOME / "receitas-paginas" / "indices" / "MANIFESTO-INDICES.json"
FAMILIA_MINIMA_DO_INDICE = 10


class InvarianteQuebrado(Exception):
    pass


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _da_arvore_ou_da_m3(rel: str) -> tuple[str, str]:
    f = RAIZ / rel
    if f.exists():
        return f.read_text(encoding="utf-8"), "arvore"
    r = subprocess.run(["git", "show", f"origin/rotas-elegiveis-v1:{rel}"], cwd=RAIZ, capture_output=True)
    if r.returncode:
        raise SystemExit(f"FALTA {rel} (nem na arvore nem em origin/rotas-elegiveis-v1)")
    return r.stdout.decode("utf-8"), "origin/rotas-elegiveis-v1"


def peca_onboarding():
    """A peca da M3, sem copia: da arvore (depois da M5) ou por git show (antes)."""
    src, origem = _da_arvore_ou_da_m3("curadoria/onboardar_rotas_provadas.py")
    m = types.ModuleType("onboardar_rotas_provadas")
    m.__file__ = str(RAIZ / "curadoria" / "onboardar_rotas_provadas.py")
    sys.path.insert(0, str(RAIZ / "curadoria"))
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m, origem


def guarda():
    sys.path.insert(0, str(RAIZ / "scripts" / "receitas"))
    import censo_e_proposta as CP  # noqa: E402
    return CP.e_generico


# ── AS PROVAS ───────────────────────────────────────────────────────────────
def paginas_guardadas() -> dict:
    """URL -> (ficheiro, sha256 do manifesto). So o que foi recolhido e ficou em disco."""
    out = {}
    for mf in MANIFESTOS:
        if mf.exists():
            for p in _json(mf)["PAGINAS"]:
                out.setdefault(p["URL"], (mf.parent / p["FICHEIRO"], p["SHA256"]))
    return out


def sha_confere(url: str, guardadas: dict) -> str | None:
    """None se a pagina guardada existe e o sha256 bate; senao o motivo."""
    if url not in guardadas:
        return f"prova indisponivel: a pagina {url} nao esta guardada"
    f, sha = guardadas[url]
    if not f.exists():
        return f"prova indisponivel: o ficheiro de {url} nao existe ({f.name})"
    real = hashlib.sha256(f.read_bytes()).hexdigest()
    if real != sha:
        return f"prova adulterada: sha256 de {url} = {real[:12]} != manifesto {sha[:12]}"
    return None


def capas_do_gabarito() -> list[str]:
    g = _json(RAIZ / "scripts" / "detector_capa" / "GABARITO-CAPA-V1.json")
    return [p["URL"] for p in g["PAGINAS"] if p["VEREDITO"] == "CAPA"]


def provar_padrao(p: dict, livro_c: dict, guardadas: dict, capas: list[str], e_generico) -> str | None:
    novo = p["DEPOIS"]
    try:
        rx = re.compile(novo)
    except re.error as ex:
        return f"padrao nao compila: {ex}"
    mats = p["PROVA"].get("MATERIAS_CONFIRMADAS") or []
    if not mats:
        return "sem materia confirmada na prova"
    for m in mats:
        e = sha_confere(m, guardadas)
        if e:
            return e
        if not rx.match(m):
            return f"o padrao novo ja nao casa a materia {m}"
    presas = [c for c in capas if rx.match(c)]
    if presas:
        return f"o padrao novo casa {len(presas)} capa(s) do gabarito, ex. {presas[0]}"
    g = e_generico(novo, livro_c["ACQUISITION"].get("INDEX_URL", ""), [], [])
    if g:
        return f"guarda: {g}"
    return None


def provar_indice(sid: str, p: dict) -> str | None:
    if not INDICES.exists():
        return "prova indisponivel: MANIFESTO-INDICES.json nao existe"
    linhas = {l["SOURCE_ID"]: l for l in _json(INDICES)}
    l = linhas.get(sid)
    if not l or l.get("URL") != p["DEPOIS"] or not l.get("FICHEIRO"):
        return "prova indisponivel: a pagina candidata nao foi buscada"
    f = Path(l["FICHEIRO"])
    if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != l.get("SHA256"):
        return "prova adulterada ou em falta: sha256 da pagina candidata"
    if int(p["PROVA"].get("LINKS_COM_FORMA_DE_MATERIA_CONFIRMADA", 0)) < FAMILIA_MINIMA_DO_INDICE:
        return f"prova fraca: < {FAMILIA_MINIMA_DO_INDICE} links com forma de materia"
    return None


def catalogo_d9() -> dict:
    """A PROPOSTA-CATALOGO-V1: da arvore (depois da M5) ou de origin/catalogo-proposta-v1."""
    f = RAIZ / "curadoria" / "PROPOSTA-CATALOGO-V1.json"
    if f.exists():
        return _json(f)
    r = subprocess.run(["git", "show", "origin/catalogo-proposta-v1:curadoria/PROPOSTA-CATALOGO-V1.json"],
                       cwd=RAIZ, capture_output=True)
    if r.returncode:
        raise SystemExit("FALTA a PROPOSTA-CATALOGO-V1 (D9): nem na arvore nem em origin/catalogo-proposta-v1")
    return json.loads(r.stdout.decode("utf-8"))


def prova_integra(provas: list[dict]) -> str | None:
    """D9: prova integra = cada ficheiro existe em disco e o sha256 bate."""
    if not provas:
        return "sem prova"
    for p in provas:
        f = Path(p.get("FICHEIRO", ""))
        if not f.exists():
            return f"prova indisponivel: {f.name} nao existe"
        if hashlib.sha256(f.read_bytes()).hexdigest() != p.get("SHA256"):
            return f"prova adulterada: sha256 de {f.name}"
    return None


# ── O PLANO ────────────────────────────────────────────────────────────────
def propostas() -> list[tuple[str, dict]]:
    vistas, out = set(), []
    for nome in ("PROPOSTA-RECEITAS-V1.json", "PROPOSTA-RECEITAS-V2.json",
                 "PROPOSTA-RECEITAS-V3.json",    # V3 = aditamento LD2
                 "PROPOSTA-RECEITAS-V4.json"):   # V4 = K1: fontes dos 2 gabaritos
        f = RAIZ / "curadoria" / nome
        if not f.exists():
            continue
        for l in _json(f)["FONTES"]:
            for p in l["PROPOSTAS"]:
                chave = (l["SOURCE_ID"], p["CAMPO"])
                if chave in vistas:
                    continue
                vistas.add(chave)
                out.append((nome, dict(p, SOURCE_ID=l["SOURCE_ID"])))
    return out


def planear(livro: dict, tabela: dict, *, guardadas=None, capas=None, e_generico=None,
            m3=None, canario=None, peca=None, catalogo=None,
            livro_bot: dict | None = None, d10: str | None = None,
            rota_scrap: bool = False, declarado: dict | None = None) -> dict:
    guardadas = paginas_guardadas() if guardadas is None else guardadas
    capas = capas_do_gabarito() if capas is None else capas
    e_generico = guarda() if e_generico is None else e_generico
    peca = peca_onboarding()[0] if peca is None else peca
    if m3 is None:
        m3 = json.loads(_da_arvore_ou_da_m3("curadoria/ROTAS-ELEGIVEIS-V1.json")[0])
    if canario is None:
        f = AQUI / "CANARIO-DESBLOQUEIO-V1.json"
        canario = _json(f) if f.exists() else {"LINHAS": []}

    L = {c["SOURCE_ID"]: c for c in livro["FONTES"]}
    T = {c["SOURCE_ID"]: c for c in tabela["FONTES"]}
    novo_livro = copy.deepcopy(L)
    acoes = []

    # 1) receitas no livro do Curator
    for origem, p in propostas():
        sid, campo = p["SOURCE_ID"], p["CAMPO"].split(".", 1)[1]
        a = {"LIVRO": "livro", "SOURCE_ID": sid, "CAMPO": p["CAMPO"], "ANTES": p.get("ANTES"),
             "DEPOIS": p["DEPOIS"], "ORIGEM": origem}
        c = novo_livro.get(sid)
        if campo not in CAMPOS_DO_LIVRO:
            acoes.append(dict(a, ACAO="SALTA", PORQUE=f"campo {campo} fora do que o pacote muda"))
            continue
        if not c:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="a fonte nao esta no livro"))
            continue
        actual = c["ACQUISITION"].get(campo)
        if actual == p["DEPOIS"]:
            acoes.append(dict(a, ACAO="JA_APLICADA"))
            continue
        if actual != p.get("ANTES"):
            acoes.append(dict(a, ACAO="SALTA", PORQUE="o livro mudou depois da prova (o valor actual nao e o ANTES)"))
            continue
        e = (provar_padrao(p, c, guardadas, capas, e_generico) if campo == "LINK_PATTERN"
             else provar_indice(sid, p))
        if e:
            acoes.append(dict(a, ACAO="SALTA", PORQUE=e))
            continue
        c["ACQUISITION"][campo] = p["DEPOIS"]
        acoes.append(dict(a, ACAO="APLICA", PROVA=p.get("PROVA", {}).get("MATERIAS_CONFIRMADAS")
                          or p.get("PROVA", {}).get("PAGINA_BUSCADA")))

    # 2) a tabela do coletor: so com canario da aquisicao que fica
    nova_tabela = copy.deepcopy(T)

    def aq(c):
        return (c["ACQUISITION"].get("INDEX_URL"), c["ACQUISITION"].get("LINK_PATTERN"))
    provas = []
    for l in m3["LINHAS"]:
        if l.get("VEREDITO") == "ROUTE_PROVEN":
            provas.append(("M3", l, (l.get("INDEX_URL"), l.get("LINK_PATTERN")), m3.get("GERADO_EM", "NAO SEI")))
    for l in canario["LINHAS"]:
        if l.get("VEREDITO") == "ROUTE_PROVEN":
            k = l["ACQUISITION_PROVADA"]
            provas.append(("G1", l, (k.get("INDEX_URL"), k.get("LINK_PATTERN")), canario.get("GERADO_EM", "NAO SEI")))
    dono_do_doc = {}
    for _, l, _, _ in provas:
        dono_do_doc.setdefault(l["CANARIO"]["URL"], l["SOURCE_ID"])
    tratadas = set()
    for quem, l, provada, quando in sorted(provas, key=lambda x: x[0] != "G1"):   # G1 (mais recente) primeiro
        sid = l["SOURCE_ID"]
        if sid in tratadas:
            continue
        a = {"LIVRO": "tabela", "SOURCE_ID": sid, "CAMPO": "ACQUISITION", "ORIGEM": f"canario {quem} {quando[:10]}"}
        c = novo_livro.get(sid)
        if not c:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="a fonte nao esta no livro do Curator"))
            continue
        if c.get("ESTADO_CATALOGO") == "RETIRADA_POR_DECISAO" and sid not in T:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="RETIRADA_POR_DECISAO (D9): nao entra na tabela"))
            continue
        if provada != aq(c):
            acoes.append(dict(a, ACAO="SALTA", PORQUE=f"o canario {quem} provou OUTRA aquisicao que nao a que fica no livro"))
            continue
        tratadas.add(sid)
        if dono_do_doc.get(l["CANARIO"]["URL"]) != sid:
            acoes.append(dict(a, ACAO="SALTA", PORQUE=f"DUPLICADA: o mesmo documento ja e de {dono_do_doc[l['CANARIO']['URL']]} (decisao de identidade)"))
            continue
        linha = peca.linha_da_tabela(c, l, quando)
        linha["EVIDENCE"] = ("curadoria/ROTAS-ELEGIVEIS-V1.json" if quem == "M3"
                             else "scripts/desbloqueio/CANARIO-DESBLOQUEIO-V1.json")
        if sid not in nova_tabela:
            nova_tabela[sid] = linha
            acoes.append(dict(a, ACAO="APLICA", ANTES=None, DEPOIS=linha["ACQUISITION"], PROVA=l["CANARIO"]["URL"]))
        elif aq(nova_tabela[sid]) == provada:
            acoes.append(dict(a, ACAO="JA_APLICADA"))
        else:
            antes = nova_tabela[sid]["ACQUISITION"]
            nova_tabela[sid] = dict(nova_tabela[sid], ACQUISITION=c["ACQUISITION"],
                                    SONDAGEM=linha["SONDAGEM"], EVIDENCE=linha["EVIDENCE"],
                                    ONBOARDED_BY=linha["ONBOARDED_BY"] + " · aquisicao actualizada pelo G1")
            acoes.append(dict(a, ACAO="APLICA", ANTES=antes, DEPOIS=c["ACQUISITION"], PROVA=l["CANARIO"]["URL"]))
    # fontes da tabela cuja receita o PACOTE poe no livro sem canario novo: a tabela
    # fica com a velha. Compara-se o LIVRO com a TABELA — nao o livro antes/depois
    # desta passagem —, senao o aviso desaparecia na 2.a passagem com a divergencia
    # ainda la (medido pelo coordenador em 23/09: 16 linhas na 1.a, 14 na 2.a).
    com_receita = {p["SOURCE_ID"] for _, p in propostas()
                   if p["CAMPO"].split(".", 1)[1] in CAMPOS_DO_LIVRO}
    for sid, t in T.items():
        if sid in com_receita and sid in novo_livro and sid not in tratadas \
                and aq(t) != aq(novo_livro[sid]):
            acoes.append({"LIVRO": "tabela", "SOURCE_ID": sid, "CAMPO": "ACQUISITION", "ACAO": "SALTA",
                          "PORQUE": "a receita do livro difere da tabela e nao ha canario dessa aquisicao: a tabela fica"})

    # 3) BLOCO 2 — catalogo (D9)
    autorizadas_d9 = set()
    if catalogo is None:
        catalogo = catalogo_d9()
    def _d9_tabela(sid, mud, a):
        """A marca/universo da D9 na tabela do coletor, com relatorio igual nas
        duas passagens: APLICA se a tabela ainda nao a tem, JA_APLICADA se tem."""
        if sid not in nova_tabela:
            return
        if all(nova_tabela[sid].get(k) == v for k, v in mud.items()):
            acoes.append(dict(a, LIVRO="tabela", ACAO="JA_APLICADA"))
            return
        nova_tabela[sid] = dict(nova_tabela[sid], **copy.deepcopy(mud))
        acoes.append(dict(a, LIVRO="tabela", ACAO="APLICA", PROVA="a mesma do livro"))

    for l in catalogo.get("LINHAS", []):
        accao = l.get("ACCAO", "")
        if not (accao.startswith("MUDAR_PARA_T") or accao == "RETIRAR_DO_UNIVERSO"):
            continue
        sid = l["SOURCE_ID"]
        a = {"LIVRO": "livro", "SOURCE_ID": sid, "CAMPO": "CATALOGO", "DECISAO": "D9",
             "ORIGEM": "PROPOSTA-CATALOGO-V1", "ANTES": l.get("UNIVERSO_ACTUAL"), "DEPOIS": accao}
        c = novo_livro.get(sid)
        if not c:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="a fonte nao esta no livro"))
            continue
        e = prova_integra(l.get("PROVA") or [])
        if e:
            acoes.append(dict(a, ACAO="SALTA", PORQUE=e))
            continue
        if accao.startswith("MUDAR_PARA_T"):
            alvo = accao.rsplit("_", 1)[1]
            if c.get("TERRITORY") == alvo:
                acoes.append(dict(a, ACAO="JA_APLICADA"))
                autorizadas_d9.add(sid)
                _d9_tabela(sid, {"TERRITORY": alvo, "CATALOGO_D9": c.get("CATALOGO_D9")}, a)
                continue
            if c.get("TERRITORY") != l.get("UNIVERSO_ACTUAL"):
                acoes.append(dict(a, ACAO="SALTA", PORQUE="o universo actual nao e o da proposta (o livro mudou)"))
                continue
            mud = {"TERRITORY": alvo,
                   "CATALOGO_D9": {"DECISAO": "D9", "ACCAO": accao, "UNIVERSO_ANTERIOR": c.get("TERRITORY"),
                                   "PORQUE": l.get("PORQUE"), "REVERSIVEL": True}}
        else:
            if any(str(p.get("ROTULO", "")).split("/")[-1] == "YES" for p in l.get("PROVA") or []):
                acoes.append(dict(a, ACAO="SALTA",
                                  PORQUE="D2: a prova tem noticia SINTONIA_RELEVANT=YES — REROUTE, nao retirar"))
                continue
            if c.get("ESTADO_CATALOGO") == "RETIRADA_POR_DECISAO":
                acoes.append(dict(a, ACAO="JA_APLICADA"))
                autorizadas_d9.add(sid)
                if sid in T:
                    _d9_tabela(sid, {"ESTADO_CATALOGO": "RETIRADA_POR_DECISAO",
                                     "CATALOGO_D9": c.get("CATALOGO_D9")}, a)
                continue
            mud = {"ESTADO_CATALOGO": "RETIRADA_POR_DECISAO",
                   "CATALOGO_D9": {"DECISAO": "D9", "ACCAO": accao, "PORQUE": l.get("PORQUE"),
                                   "REVERSIVEL": True, "NOTA": "pode voltar pelo circuito do Curator"}}
        c.update(copy.deepcopy(mud))
        autorizadas_d9.add(sid)
        acoes.append(dict(a, ACAO="APLICA", PROVA=[p.get("SHA256") for p in l.get("PROVA") or []]))
        if accao == "RETIRAR_DO_UNIVERSO" and sid in nova_tabela and sid not in T:
            # o bloco 1 acabou de a por na tabela; a D9 retira-a no mesmo pacote:
            # nao entra (a tabela nao perde nada que ja tivesse).
            del nova_tabela[sid]
            for x in acoes:
                if x["LIVRO"] == "tabela" and x["SOURCE_ID"] == sid and x["ACAO"] == "APLICA":
                    x["ACAO"], x["PORQUE"] = "SALTA", "D9 retira-a neste mesmo pacote: nao entra na tabela"
            continue
        _d9_tabela(sid, mud, a)

    # 4) BLOCO 4 — A ROTA DO SCRAP PARA OS CANAIS YOUTUBE (SOC2, D17.4)
    autorizadas_scrap = set()
    if rota_scrap:
        acoes_scrap, autorizadas_scrap = rota_do_scrap(novo_livro, nova_tabela, T, declarado)
        acoes.extend(acoes_scrap)

    livro_out = dict(livro, FONTES=[novo_livro[c["SOURCE_ID"]] for c in livro["FONTES"]])
    ordem = [c["SOURCE_ID"] for c in tabela["FONTES"]] + [s for s in nova_tabela if s not in T]
    tabela_out = dict(tabela, FONTES=[nova_tabela[s] for s in ordem])
    invariantes(livro, livro_out, tabela, tabela_out, autorizadas_d9, autorizadas_scrap)
    out = {"ACOES": acoes, "LIVRO": livro_out, "TABELA": tabela_out}

    # 4) BLOCO 3 — CONTRATO UNICO (D10)
    if livro_bot is not None:
        bot_out, acoes_bot = contrato_unico(novo_livro, livro_bot, provas, dono_do_doc, d10)
        acoes.extend(acoes_bot)
        out["LIVRO_BOT"] = bot_out
    return out


# ── BLOCO 3 — CONTRATO UNICO (D10, 23/09, bot Luciano por delegacao do dono) ────
#
# ⚠️ DOIS DONOS DO MESMO CONTRATO (B2). As 8 elegiveis tinham, no livro do bot, um
# contrato diferente do que o portao le; e a prova viva T02077 pediu ao bot que
# re-medisse IT-T5-041 e ele respondeu «sem contrato». A D10 escolheu a OPCAO A:
# o contrato AFINADO do portao passa a ser O contrato, e so entra no livro do bot
# por esta porta — com a mesma lei do resto do pacote:
#
#   · so com canario ROUTE_PROVEN (M3 ou G1) de EXACTAMENTE a aquisicao que fica,
#     e um documento = uma fonte (duplicadas ficam de fora);
#   · a ORIGEM fica escrita no contrato (de onde veio a rota, quando foi provada,
#     por que canario) e no ledger (DECISAO = D10);
#   · muda-se SO a ACQUISITION e acrescenta-se CONTRATO_UNICO. Nunca se acrescenta
#     nem se retira fonte: uma fonte que o bot nao tem (IT-T5-041) nao entra aqui
#     — volta, se voltar, como candidata nova pelo Curator (D10, condicao 4);
#   · sem prova: SALTA, e pela regra da B2 a fonte sai do portao (D10: vale C);
#   · tudo na mesma passagem: nunca dois contratos para a mesma fonte ao mesmo tempo;
#   · a OPCAO B existe no codigo pela simetria, mas so aplica com prova da
#     aquisicao do bot — medido a 23/09: 0 de 9 tinham.
#
# O bloco NAO promove: um contrato que muda fica por re-medir (CONTRATO_UNICO.
# PRECISA_DE_REMEDIR), e e o bot, com os quatro passos, quem decide (D10, cond. 2).
CAMPOS_DO_CONTRATO_UNICO = ("ACQUISITION", "CONTRATO_UNICO")
# As 7 que a D10 decidiu (DECISOES-DONO-2026-09-23, linha 72): as elegiveis de 23/09
# com contrato diferente no bot. IT-T5-041 NAO esta aqui: o bot nao a tem, e a D10
# manda-a sair (condicao 4). Outra fonte com dois contratos e decisao nova, nao esta.
D10_FONTES = frozenset({"IT-T10-018", "IT-T10-022", "IT-T5-049", "IT-T7-017",
                        "IT-T7-033", "IT-T7-042", "IT-T7-043"})


def _aq(c: dict) -> tuple:
    a = (c or {}).get("ACQUISITION") or {}
    return (a.get("INDEX_URL"), a.get("LINK_PATTERN"))


def _origem(c: dict) -> dict:
    rp = (c or {}).get("ROUTE_PROVENANCE") or {}
    return {"MISSAO": rp.get("MISSAO") or "NAO SEI", "FERRAMENTA": rp.get("FERRAMENTA") or "NAO SEI",
            "PROVADO_EM": rp.get("PROVADO_EM") or rp.get("INTEGRADO_EM") or "NAO SEI",
            "LISTAGEM": rp.get("LISTAGEM") or ((c or {}).get("ACQUISITION") or {}).get("INDEX_URL")}


def contrato_unico(livro_portao: dict, livro_bot: dict, provas: list, dono_do_doc: dict,
                   d10: str | None) -> tuple[dict, list]:
    """Iguala, com prova, o contrato do bot ao do portao (A) ou o inverso (B).
    Devolve (livro do bot depois, accoes). So o livro do bot e escrito aqui."""
    B = {c["SOURCE_ID"]: c for c in livro_bot["FONTES"]}
    novo_bot = copy.deepcopy(B)
    acoes, autorizadas = [], set()
    por_sid = {}
    for quem, l, provada, quando in provas:
        por_sid.setdefault(l["SOURCE_ID"], []).append((quem, l, provada, quando))
    for sid in sorted(set(livro_portao) & set(B)):
        p, b = livro_portao[sid], novo_bot[sid]
        a = {"LIVRO": "bot", "SOURCE_ID": sid, "CAMPO": "ACQUISITION", "DECISAO": "D10",
             "ORIGEM": "CONTRATO_UNICO"}
        if json.dumps(p.get("ACQUISITION"), sort_keys=True) == json.dumps(b.get("ACQUISITION"), sort_keys=True):
            if (b.get("CONTRATO_UNICO") or {}).get("DECISAO") == "D10":
                acoes.append(dict(a, ACAO="JA_APLICADA"))
            continue
        if sid not in D10_FONTES:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="dois contratos para a fonte, mas fora das 7 da D10: "
                                                       "decisao nova do dono, nao deste pacote"))
            continue
        if d10 not in ("A", "B"):
            acoes.append(dict(a, ACAO="SALTA", PORQUE="dois contratos para a fonte e sem D10 dada: o pacote nao escolhe"))
            continue
        vence = p
        if d10 == "B":
            acoes.append(dict(a, ACAO="SALTA", PORQUE="OPCAO B: esta porta so escreve no livro do bot; "
                                                       "o contrato do portao muda pelo bloco 1 (receitas)"))
            continue
        certas = [x for x in por_sid.get(sid, []) if x[2] == _aq(vence)]
        if not certas:
            acoes.append(dict(a, ACAO="SALTA", ANTES=b.get("ACQUISITION"), DEPOIS=vence.get("ACQUISITION"),
                              PORQUE="sem canario ROUTE_PROVEN da aquisicao que ficaria — D10: vale C "
                                     "(a fonte sai do portao pela regra da B2)"))
            continue
        quem, l, _, quando = certas[0]
        if dono_do_doc.get(l["CANARIO"]["URL"]) != sid:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="DUPLICADA: o documento do canario e de %s"
                              % dono_do_doc[l["CANARIO"]["URL"]]))
            continue
        antes = b.get("ACQUISITION")
        novo_bot[sid] = dict(b, ACQUISITION=copy.deepcopy(vence["ACQUISITION"]), CONTRATO_UNICO={
            "DECISAO": "D10", "OPCAO": "A", "APLICADO_EM": agora(),
            "ORIGEM": dict(_origem(vence), BANCADA="ponte-curador-v1 (livro do portao)"),
            "PROVA": {"CANARIO": quem, "QUANDO": quando, "DOCUMENTO": l["CANARIO"]["URL"]},
            "ACQUISITION_ANTERIOR": antes,
            "PRECISA_DE_REMEDIR": True,
            "NOTA": "contrato novo: o bot re-mede (4 passos + canario) antes de voltar a ser elegivel"})
        autorizadas.add(sid)
        acoes.append(dict(a, ACAO="APLICA", ANTES=antes, DEPOIS=vence["ACQUISITION"],
                          PROVA=l["CANARIO"]["URL"]))
    bot_out = dict(livro_bot, FONTES=[novo_bot[c["SOURCE_ID"]] for c in livro_bot["FONTES"]])
    invariantes_do_bot(livro_bot, bot_out, autorizadas)
    return bot_out, acoes


# ── BLOCO 4 — A ROTA DO SCRAP PARA OS CANAIS YOUTUBE (SOC2, D17.4) ─────────────
#
# As 50 fontes YouTube que o Curator contratou apontam para o FEED do canal
# (`YOUTUBE_CHANNEL_FEED`), que esta em `Disallow` e que a matriz do Scrap marca
# ROUTE_NOT_ALLOWED; a tabela do coletor aponta-as para `CANAL_PUBLICO_YOUTUBE_V1`,
# um adapter JS que nao existe nesta arvore. A propria nota do contrato dizia:
# «so a ROTA de aquisicao tem de mudar antes de coletar. Rota permitida por medir:
# playlistItems.list». Este bloco faz essa mudanca, e so essa:
#
#   · livro do Curator: a ACQUISITION passa a nomear a fase `canal-youtube` do
#     Scrap (`rota_do_scrap_youtube.acquisition`), e os campos que descreviam o
#     FEED passam a descrever essa rota; o anterior fica em ROTA_DO_SCRAP;
#   · tabela do coletor: ACRESCENTA `COLETADO_POR` (executor, fase, filtro). A
#     ACQUISITION do motor fica como esta — e o que o motor le, e os testes do
#     motor fixam-na; `COLETADO_POR` e que diz que nao e ele quem colhe;
#   · SO com prova: o canal do livro = o da tabela = SOURCE_NATIVE_ID, a sondagem
#     da tabela diz IDENTITY_MATCH = YES, o canal e de UMA so fonte na casa, e o
#     Scrap declara HOJE a rota (fase, capacidade, filtro, matriz ALLOWED);
#   · nunca muda SOURCE_ID, TERRITORY, BATCH_ID nem o canal; nunca acrescenta nem
#     retira fonte; ledger com DECISAO = D17.4.
#
# O bloco NAO promove: a fonte continua no estado em que o livro de estado a tem
# (RECONCILIATION_REQUIRED / CONTRACT_READY_ROUTE_BLOCKED). Quem a leva a READY e
# o circuito, com o canario do Scrap.
CAMPOS_DA_ROTA_DO_SCRAP = ("ACQUISITION", "IDENTITY", "DOCUMENT_DATE_FIELD", "EXPECTED_FAILURES",
                           "FAIL_CLOSED_RULE", "FALLBACK", "NEGATIVE_CONTROL", "ROUTE_POLICY_STATUS",
                           "ROUTE_POLICY_EVIDENCE", "ROUTE_POLICY_NOTE", "ROTA_DO_SCRAP",
                           "SOURCE_CONTRACT_HASH")
MISSAO_SCRAP = "SOC2-CURATOR-YOUTUBE"


def _rsy():
    sys.path.insert(0, str(RAIZ / "curadoria"))
    import rota_do_scrap_youtube as RSY
    return RSY


def _hash_do_contrato(c: dict) -> str:
    """A formula do worker ao contratar (a mesma de integrar_gate_de_detalhe)."""
    sys.path.insert(0, str(RAIZ / "curadoria"))
    import escrever_contratos as EC
    d = {k: v for k, v in c.items() if k != "SOURCE_CONTRACT_HASH"}
    d["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
    return EC.hash_do_contrato(d)


def coletado_por(canal: str, declarado: dict) -> dict:
    RSY = _rsy()
    return {"EXECUTOR": RSY.EXECUTOR, "FASE": RSY.FASE, "FILTROS": {RSY.FILTRO: canal},
            "CAPACIDADE": RSY.CAPACIDADE, "ROTA": declarado.get("ROTA"),
            "DECISAO": "D17.4", "MISSAO": MISSAO_SCRAP,
            "ACQUISITION_DO_MOTOR": ("inerte: o coletor JS nao colhe esta fonte; quem a colhe "
                                     "e o Scrap pela fase acima")}


def rota_do_scrap(novo_livro: dict, nova_tabela: dict, tabela_antes: dict,
                  declarado: dict | None = None) -> tuple[list, set]:
    """Muda `novo_livro` e `nova_tabela` no sitio. Devolve (accoes, autorizadas)."""
    sys.path.insert(0, str(RAIZ / "curadoria"))
    import escrever_contratos as EC
    RSY = _rsy()
    declarado = RSY.o_que_o_scrap_declara() if declarado is None else declarado
    livro_antes = {s: copy.deepcopy(c) for s, c in novo_livro.items()}
    acoes, autorizadas = [], set()
    for sid in sorted(novo_livro):
        c = novo_livro[sid]
        aq = c.get("ACQUISITION") or {}
        if aq.get("STRATEGY") not in ("YOUTUBE_CHANNEL_FEED", RSY.STRATEGY):
            continue
        canal = aq.get("CHANNEL_ID")
        a = {"LIVRO": "livro", "SOURCE_ID": sid, "CAMPO": "ACQUISITION", "DECISAO": "D17.4",
             "ORIGEM": MISSAO_SCRAP}
        t = nova_tabela.get(sid)
        porque = None
        if not RSY.RE_CANAL.match(canal or ""):
            porque = "CHANNEL_ID invalido no livro: %r" % canal
        elif c.get("SOURCE_NATIVE_ID") != canal:
            porque = "o SOURCE_NATIVE_ID do livro nao e o CHANNEL_ID da aquisicao"
        elif not t:
            porque = "a fonte nao esta na tabela do coletor: a identidade nao foi sondada la"
        elif t.get("SOURCE_NATIVE_ID") != canal or (t.get("ACQUISITION") or {}).get("CHANNEL_ID") != canal:
            porque = "o canal da tabela nao e o do livro"
        elif (t.get("SONDAGEM") or {}).get("IDENTITY_MATCH") != "YES":
            porque = "a sondagem da tabela nao provou a identidade do canal (IDENTITY_MATCH != YES)"
        else:
            donos = RSY.canal_conhecido(canal, tabela={"FONTES": list(tabela_antes.values())},
                                        livro={"FONTES": list(livro_antes.values())})
            if donos != [sid]:
                porque = "o canal esta ligado a %s: colisao de identidade, decisao humana" % donos
        if porque:
            acoes.append(dict(a, ACAO="SALTA", PORQUE=porque))
            continue
        nova_aq = RSY.acquisition(canal, declarado)
        ok, porque_rota = RSY.conferir(nova_aq, declarado)
        if not ok:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="o Scrap nao declara a rota hoje: %s" % porque_rota))
            continue
        autorizadas.add(sid)
        # livro
        if aq == nova_aq:
            acoes.append(dict(a, ACAO="JA_APLICADA"))
        else:
            molde = EC.contrato_youtube_scrap({"SOURCE_ID": sid, "NOME": c.get("NAME") or c.get("OWNER") or sid,
                                               "TERRITORY": c["TERRITORY"],
                                               "URL": c.get("CANONICAL_ENTRY_URL")}, canal, declarado)
            antes = {k: copy.deepcopy(c.get(k)) for k in CAMPOS_DA_ROTA_DO_SCRAP if k in c}
            for k in ("ACQUISITION", "IDENTITY", "DOCUMENT_DATE_FIELD", "EXPECTED_FAILURES",
                      "FAIL_CLOSED_RULE", "FALLBACK", "NEGATIVE_CONTROL"):
                c[k] = copy.deepcopy(molde[k])
            c["ROUTE_POLICY_STATUS"] = "ALLOWED"
            c["ROUTE_POLICY_EVIDENCE"] = ("leis/social_matriz.py decisao(YOUTUBE, INCREMENTAL) = ALLOWED · "
                                          + porque_rota)
            c["ROUTE_POLICY_NOTE"] = ("a rota e a fase %s do Scrap (API oficial); o feed continua em "
                                      "Disallow e nao e usado" % RSY.FASE)
            c["ROTA_DO_SCRAP"] = {"DECISAO": "D17.4", "MISSAO": MISSAO_SCRAP, "APLICADO_EM": agora(),
                                  "ANTES": antes, "PRECISA_DE_CANARIO_DO_SCRAP": True,
                                  "NOTA": "nao promove: o canario desta rota e uma colheita do Scrap"}
            c["SOURCE_CONTRACT_HASH"] = _hash_do_contrato(c)
            acoes.append(dict(a, ACAO="APLICA", ANTES=aq, DEPOIS=nova_aq, PROVA=porque_rota))
        # tabela
        b = {"LIVRO": "tabela", "SOURCE_ID": sid, "CAMPO": "COLETADO_POR", "DECISAO": "D17.4",
             "ORIGEM": MISSAO_SCRAP}
        cp = coletado_por(canal, declarado)
        if t.get("COLETADO_POR") == cp:
            acoes.append(dict(b, ACAO="JA_APLICADA"))
        else:
            nova_tabela[sid] = dict(t, COLETADO_POR=cp)
            acoes.append(dict(b, ACAO="APLICA", ANTES=t.get("COLETADO_POR"), DEPOIS=cp,
                              PROVA="IDENTITY_MATCH=YES em %s" % (t.get("SONDAGEM") or {}).get("SONDADO_EM")))
    return acoes, autorizadas


def invariantes_do_bot(antes: dict, depois: dict, autorizadas: set) -> None:
    """No livro do bot: as mesmas fontes, pela mesma ordem; so as autorizadas mudam, e
    so em ACQUISITION e CONTRATO_UNICO. Grupo T e SOURCE_ID nunca."""
    A = [c["SOURCE_ID"] for c in antes["FONTES"]]
    D = [c["SOURCE_ID"] for c in depois["FONTES"]]
    if A != D:
        raise InvarianteQuebrado("o livro do bot ganhou, perdeu ou reordenou fontes")
    for a, d in zip(antes["FONTES"], depois["FONTES"]):
        a2, d2 = copy.deepcopy(a), copy.deepcopy(d)
        if a2 == d2:
            continue
        if a["SOURCE_ID"] not in autorizadas:
            raise InvarianteQuebrado(f"{a['SOURCE_ID']}: mudou no livro do bot sem autorizacao D10")
        for k in CAMPOS_DO_CONTRATO_UNICO:
            a2.pop(k, None)
            d2.pop(k, None)
        if a2 != d2:
            raise InvarianteQuebrado(f"{a['SOURCE_ID']}: mudou no livro do bot um campo alem da aquisicao")


def invariantes(livro_a: dict, livro_d: dict, tab_a: dict, tab_d: dict,
                autorizadas_d9=frozenset(), autorizadas_scrap=frozenset()) -> None:
    """Nunca muda grupo T nem outro campo — EXCEPTO as linhas do catalogo que a D9
    autorizou e cuja prova bateu: essas podem mudar TERRITORY, ESTADO_CATALOGO e
    CATALOGO_D9, e mais nada."""
    A = {c["SOURCE_ID"]: c for c in livro_a["FONTES"]}
    D = {c["SOURCE_ID"]: c for c in livro_d["FONTES"]}
    if set(A) != set(D):
        raise InvarianteQuebrado("o livro ganhou ou perdeu fontes")
    for s in A:
        a, d = copy.deepcopy(A[s]), copy.deepcopy(D[s])
        if s in autorizadas_d9:
            for k in ("TERRITORY", "ESTADO_CATALOGO", "CATALOGO_D9"):
                a.pop(k, None)
                d.pop(k, None)
        if s in autorizadas_scrap:
            # o canal e a identidade nao mudam; o resto dos campos da ROTA muda
            if (A[s].get("SOURCE_NATIVE_ID") != D[s].get("SOURCE_NATIVE_ID")
                    or A[s]["ACQUISITION"].get("CHANNEL_ID") != D[s]["ACQUISITION"].get("CHANNEL_ID")):
                raise InvarianteQuebrado(f"{s}: o bloco da rota do Scrap mudou o canal")
            for k in CAMPOS_DA_ROTA_DO_SCRAP:
                a.pop(k, None)
                d.pop(k, None)
        if a.get("TERRITORY") != d.get("TERRITORY"):
            raise InvarianteQuebrado(f"{s}: grupo T mudou")
        for k in CAMPOS_DO_LIVRO:
            a.get("ACQUISITION", {}).pop(k, None)
            d.get("ACQUISITION", {}).pop(k, None)
        if a != d:
            raise InvarianteQuebrado(f"{s}: mudou um campo do livro que o pacote nao pode mudar")
    TA = {c["SOURCE_ID"]: c for c in tab_a["FONTES"]}
    TD = {c["SOURCE_ID"]: c for c in tab_d["FONTES"]}
    # Na tabela do coletor o bloco 4 so ACRESCENTA `COLETADO_POR`: a aquisicao do
    # motor, a identidade e o resto da linha ficam como estavam.
    for s in TA:
        if s in TD and TA[s] != TD[s]:
            a2 = {k: v for k, v in TA[s].items() if k != "COLETADO_POR"}
            d2 = {k: v for k, v in TD[s].items() if k != "COLETADO_POR"}
            if s in autorizadas_scrap and a2 != d2 and s not in autorizadas_d9:
                raise InvarianteQuebrado(f"{s}: o bloco da rota do Scrap mudou a tabela alem de COLETADO_POR")
            if s not in autorizadas_scrap and TA[s].get("COLETADO_POR") != TD[s].get("COLETADO_POR"):
                raise InvarianteQuebrado(f"{s}: COLETADO_POR mudou sem autorizacao do bloco 4")
    if not set(TA) <= set(TD):
        raise InvarianteQuebrado("a tabela perdeu fontes")
    for s in TA:
        if s not in autorizadas_d9 and TA[s].get("TERRITORY") != TD[s].get("TERRITORY"):
            raise InvarianteQuebrado(f"{s}: grupo T mudou na tabela")
    for s in set(TD) - set(TA):
        if s in A and TD[s].get("TERRITORY") != D[s].get("TERRITORY"):
            raise InvarianteQuebrado(f"{s}: linha nova na tabela com grupo T diferente do livro")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    livro_p, tab_p = Path(arg["livro"]), Path(arg["tabela"])
    ledger = Path(arg.get("ledger", livro_p.parent / "DESBLOQUEIO-LEDGER-V1.jsonl"))
    livro, tabela = _json(livro_p), _json(tab_p)
    if not (RAIZ / "curadoria" / "PROPOSTA-CATALOGO-V1.json").exists():
        h = subprocess.run(["git", "rev-parse", "--short=8", "origin/catalogo-proposta-v1"], cwd=RAIZ,
                           capture_output=True, text=True).stdout.strip()
        print(f"CATALOGO D9 lido de origin/catalogo-proposta-v1 @ {h or 'NAO SEI'}")
        if h and not h.startswith(CATALOGO_CONFERIDO):
            print(f"AVISO: a branch andou desde o head conferido ({CATALOGO_CONFERIDO}); "
                  f"confirmar com o coordenador antes de --escrever", file=sys.stderr)
    bot_p = Path(arg["livro-bot"]) if "livro-bot" in arg else None
    livro_bot = _json(bot_p) if bot_p else None
    try:
        plano = planear(livro, tabela, livro_bot=livro_bot, d10=arg.get("d10"),
                        rota_scrap=arg.get("rota-scrap") == "SOC2")
    except InvarianteQuebrado as ex:
        print(f"INVARIANTE QUEBRADO — nada escrito: {ex}", file=sys.stderr)
        return 4
    from collections import Counter
    for a in plano["ACOES"]:
        print(f"{a['ACAO']:12s} {a['LIVRO']:6s} {a['SOURCE_ID']:11s} {a['CAMPO']:28s} {a.get('PORQUE', '')[:90]}")
    c = Counter((a["LIVRO"], a["ACAO"]) for a in plano["ACOES"])
    print("RESUMO", dict(c))
    if "--escrever" in argv:
        aplicadas = [a for a in plano["ACOES"] if a["ACAO"] == "APLICA"]
        if aplicadas:
            # cada livro so e reescrito se tem alteracao sua: o bloco 3 sozinho nao
            # reescreve (e reformata) os livros do portao e do coletor.
            if any(a["LIVRO"] in ("livro", "tabela") for a in aplicadas):
                livro_p.write_text(json.dumps(plano["LIVRO"], ensure_ascii=False, indent=1), encoding="utf-8")
                tab_p.write_text(json.dumps(plano["TABELA"], ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")
            if bot_p and any(a["LIVRO"] == "bot" for a in aplicadas):
                bot_p.write_text(json.dumps(plano["LIVRO_BOT"], ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")
            with ledger.open("a", encoding="utf-8") as f:
                for a in aplicadas:
                    f.write(json.dumps({"MISSAO": MISSAO, "AT": agora(), **{k: a.get(k) for k in (
                        "LIVRO", "SOURCE_ID", "CAMPO", "ANTES", "DEPOIS", "ORIGEM", "PROVA", "DECISAO")}},
                        ensure_ascii=False) + "\n")
        print(f"ESCRITO: {len(aplicadas)} alteracao(oes) · ledger {ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
