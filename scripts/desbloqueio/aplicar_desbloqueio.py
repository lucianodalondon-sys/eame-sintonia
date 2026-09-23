"""PACOTE DE DESBLOQUEIO G1 — aplica-se UMA vez, no cutover, sobre o livro corrente.

    py scripts/desbloqueio/aplicar_desbloqueio.py --livro=<italy_contracts_curator.json>
                                                   --tabela=<italy_contracts_onboarded.json>
                                                   [--escrever] [--ledger=<ficheiro .jsonl>]

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
            m3=None, canario=None, peca=None, catalogo=None) -> dict:
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

    livro_out = dict(livro, FONTES=[novo_livro[c["SOURCE_ID"]] for c in livro["FONTES"]])
    ordem = [c["SOURCE_ID"] for c in tabela["FONTES"]] + [s for s in nova_tabela if s not in T]
    tabela_out = dict(tabela, FONTES=[nova_tabela[s] for s in ordem])
    invariantes(livro, livro_out, tabela, tabela_out, autorizadas_d9)
    return {"ACOES": acoes, "LIVRO": livro_out, "TABELA": tabela_out}


def invariantes(livro_a: dict, livro_d: dict, tab_a: dict, tab_d: dict,
                autorizadas_d9=frozenset()) -> None:
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
        if a.get("TERRITORY") != d.get("TERRITORY"):
            raise InvarianteQuebrado(f"{s}: grupo T mudou")
        for k in CAMPOS_DO_LIVRO:
            a.get("ACQUISITION", {}).pop(k, None)
            d.get("ACQUISITION", {}).pop(k, None)
        if a != d:
            raise InvarianteQuebrado(f"{s}: mudou um campo do livro que o pacote nao pode mudar")
    TA = {c["SOURCE_ID"]: c for c in tab_a["FONTES"]}
    TD = {c["SOURCE_ID"]: c for c in tab_d["FONTES"]}
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
    try:
        plano = planear(livro, tabela)
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
            livro_p.write_text(json.dumps(plano["LIVRO"], ensure_ascii=False, indent=1), encoding="utf-8")
            tab_p.write_text(json.dumps(plano["TABELA"], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            with ledger.open("a", encoding="utf-8") as f:
                for a in aplicadas:
                    f.write(json.dumps({"MISSAO": MISSAO, "AT": agora(), **{k: a.get(k) for k in (
                        "LIVRO", "SOURCE_ID", "CAMPO", "ANTES", "DEPOIS", "ORIGEM", "PROVA", "DECISAO")}},
                        ensure_ascii=False) + "\n")
        print(f"ESCRITO: {len(aplicadas)} alteracao(oes) · ledger {ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
