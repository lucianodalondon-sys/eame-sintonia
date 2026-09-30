#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KNOW HOW VIVO v1 — `knowhow`: registrar, consolidar, indexar, buscar.

Especificacao unica: KNOW-HOW-VIVO-ARQUITETURA-v1 (coordenador, 30/09/2026).
Ordem do dono: «PROMOCAO AUTOMATICA POR CRITERIOS», K1–K8.

    AGENTE TRABALHA → MEMORY EVENT → consolidador → CANDIDATO_A_KNOW_HOW
        → K1–K8 → ACTIVE / REFORCO / BLOQUEADO / CONFLITO_* / RELACIONADO
        → indice → o proximo agente recupera

UM de cada, e todos aqui:

    formato de evento     MEMORY_EVENT/1                  validar_evento()
    repositorio           know-how/vivo/                  Config
    consolidador          knowhow consolidar              consolidar_candidato()
    regra                 K1–K8, uma funcao por K         k1_origem() … k8_aprendizado()
    indice                know-how/vivo/INDICE.json       indexar()  (DERIVADO)
    porta de recuperacao  knowhow buscar "<termos>"       buscar()

O que este programa NUNCA faz:
  - escrever num evento existente (1 evento = 1 ficheiro, `open(..., "x")`);
  - tocar em SINTONIA-EAME-KNOW-HOW.md (so o LE, para o inventario e a busca);
  - inventar o texto de um aprendizado (quem propoe escreve; aqui so se julga);
  - apagar genealogia (SUPERSEDED marca, nao apaga).

Uso:
    py know-how/vivo/knowhow.py registrar --arquivo ev.json
    py know-how/vivo/knowhow.py registrar --agente coordenador --area OPERACAO \
        --tags ramo,servico --especie FATO_MEDIDO --fato "..." --evidencia "git ..." \
        --confianca GIT_MEDIDO --status ABERTO
    py know-how/vivo/knowhow.py importar --jsonl <EVENTOS-LAB.jsonl>
    py know-how/vivo/knowhow.py consolidar [--candidato cand.json]
    py know-how/vivo/knowhow.py indexar
    py know-how/vivo/knowhow.py buscar "data publicação" [--area X] [--max N] [--json]
    py know-how/vivo/knowhow.py substituir KH-0001 --por KH-0002 --evento MEM-...
Todos aceitam --raiz <worktree> (onde vive know-how/vivo/).
"""
import argparse
import datetime as _dt
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO_DO_PROGRAMA = os.path.dirname(os.path.dirname(AQUI))
CASA = os.path.expanduser("~")
NOME_LEGADO = "SINTONIA-EAME-KNOW-HOW.md"

# ════════════════════════════════════════════════════════════════════════════
# §3 · VOCABULARIO FECHADO (v1) — um dicionario so, usado por tudo
# ════════════════════════════════════════════════════════════════════════════
AREAS = ("COLETA", "SCRAP", "FONTES", "SALA", "INTELLIGENCE", "CASCO", "LAB",
         "OPERACAO", "GIT_ARVORE", "KNOW_HOW", "SEGURANCA", "DATAS_TEMPO", "LUGAR")
ESPECIES = ("FATO_MEDIDO", "DECISAO", "RELATO", "HIPOTESE", "INFERENCIA")
TAGS_BASE = ("arvore", "ramo", "ff", "servico", "instalacao",
             "data", "publicacao", "fact_time", "lugar",
             "g0", "produtor", "c8", "pote", "preview",
             "mutante", "teste", "lock",
             "fonte", "coorte", "canario", "raw", "sala")

# Como cada TAG aparece no texto (ja sem acento e em minusculas). Serve para
# derivar TAGS de um evento importado, para o K5, o K7 e a busca: UMA lista.
TERMOS = {
    "arvore": [r"\barvores?\b", r"\bworktrees?\b"],
    "ramo": [r"\bramos?\b", r"\bbranch(es)?\b"],
    "ff": [r"\bff\b", r"\bfast.?forward\b"],
    "servico": [r"\bservico\b", r"\bproducao\b", r"\boperaciona(l|is)\b"],
    "instalacao": [r"\binstala(r|do|da|dos|das|cao|coes|ndo)?\b", r"\binstalou\b"],
    "data": [r"\bdatas?\b"],
    "publicacao": [r"\bpublicac(ao|oes)\b", r"\bpublished(_at|_time)?\b",
                   r"\bpublication(_time)?\b"],
    "fact_time": [r"\bfact.?time\b", r"\bdata do fac?to\b", r"\btempo do fac?to\b",
                  r"\bdata dos fac?tos\b"],
    "lugar": [r"\blugar(es)?\b", r"\bfact.?location\b", r"\bsource.?location\b",
              r"\blocal do fac?to\b"],
    "g0": [r"\bg0\b"],
    "produtor": [r"\bprodutor(es)?\b"],
    "c8": [r"\bc8\b"],
    "pote": [r"\bpotes?\b"],
    "preview": [r"\bpreview\b"],
    "mutante": [r"\bmutantes?\b", r"\bmutac(ao|oes)\b"],
    "teste": [r"\btestes?\b"],
    "lock": [r"\block\b", r"\block.?pesado\b", r"\btravas?\b"],
    "fonte": [r"\bfontes?\b"],
    "coorte": [r"\bcoortes?\b"],
    "canario": [r"\bcanari(o|os)\b"],
    "raw": [r"\braw\b", r"\bbrutos?\b"],
    "sala": [r"\bsala\b"],
}
_TERMOS_RE = {t: re.compile("|".join(ps)) for t, ps in TERMOS.items()}

# Sinonimos da BUSCA (§3). A chave e a frase ja normalizada.
SINONIMOS = {
    "branch": ["ramo", "arvore"],
    "branches": ["ramo", "arvore"],
    "data publicacao": ["publicacao", "data", "published_at"],
    "arvores branches operacionais": ["arvore", "ramo", "servico", "ff"],
}

# Area do legado, derivada das TAGS (o legado nao traz area). Sem tag → None.
AREA_POR_TAG = (("fact_time", "DATAS_TEMPO"), ("publicacao", "DATAS_TEMPO"),
                ("data", "DATAS_TEMPO"), ("lugar", "LUGAR"),
                ("ramo", "GIT_ARVORE"), ("arvore", "GIT_ARVORE"),
                ("ff", "GIT_ARVORE"), ("sala", "SALA"), ("fonte", "FONTES"))

# Quem pode DECIDIR (K2): o dono ou o coordenador, e sempre com a referencia D-n.
AGENTES_DECISORES = ("dono", "dono-real", "luciano-real", "coordenador",
                     "sintonia-coordenador")

OBRIGATORIOS = ("SCHEMA", "ID", "DATA", "AGENTE_ORIGEM", "AREA", "TAGS", "ESPECIE",
                "FATO", "EVIDENCIA", "CONFIANCA", "STATUS")
ID_EVENTO = re.compile(r"^MEM-[A-Z0-9]+-\d{8}-\d{2,}$")
ID_CANDIDATO = re.compile(r"^(KH-C\d+|KHC-\d{8}-\d{2,})$")
ID_KH = re.compile(r"^KH-\d{4,}$")

RESULTADOS = ("ACTIVE", "REFORCO", "BLOQUEADO", "CONFLITO_KNOW_HOW",
              "CONFLITO_DE_AUTORIDADE", "RELACIONADO_A_AUTORIDADE")

# K5 — o limiar declarado. Semelhanca = cosseno TF-IDF (termos normalizados +
# TAGS do vocabulario), sem vector DB, sobre o texto SEM blocos de codigo.
# Medido em 30/09 nos 2 casos do dono contra o legado real:
#     KH-C2 (novo)   → o mais proximo e LEG-§59.8 com 0.121   (abaixo)
#     KH-C1 (existe) → LEG-§222.2 com 0.158                   (acima)
# A folga e curta (~0.02 de cada lado): um limiar e uma medida, nao um oraculo.
LIMIAR_K5 = 0.14
# K6 — «o mesmo alvo»: um KH ACTIVE com semelhanca acima disto e comparado
# frase a frase; abaixo, nao e o mesmo assunto.
LIMIAR_ALVO_K6 = 0.30
# Busca: fica so quem tiver pelo menos esta fracao da nota do primeiro.
CORTE_RELATIVO_BUSCA = 0.35


class Recusa(Exception):
    """A porta recusou: evento invalido, ID ja existente, pedido sem base."""


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACAO — onde vivem as coisas (§0)
# ════════════════════════════════════════════════════════════════════════════
class Config:
    def __init__(self, raiz=None, repo=None, legado=None, handoff=None,
                 decisoes=None, raizes_evidencia=None, raizes_de_procura=None):
        self.repo = os.path.abspath(repo or REPO_DO_PROGRAMA)
        self.raiz = os.path.abspath(raiz or self.repo)
        self.vivo = os.path.join(self.raiz, "know-how", "vivo")
        if legado is None:
            legado = os.path.join(self.raiz, NOME_LEGADO)
            if not os.path.exists(legado):
                legado = os.path.join(self.repo, NOME_LEGADO)
        self.legado = legado
        self.handoff = handoff or os.path.join(CASA, "auditoria-madrugada", "HANDOFF-VIVO.md")
        self.decisoes = decisoes or os.path.join(
            CASA, "auditoria-madrugada", "DECISOES-DONO-2026-09-23.md")
        # Onde um caminho RELATIVO citado como evidencia pode estar. Os eventos
        # do LAB citam a partir de %LOCALAPPDATA%/hermes («profiles/...»), de
        # %LOCALAPPDATA% («Temp/...») e da casa («auditoria-madrugada/...»).
        local = os.path.join(CASA, "AppData", "Local")
        self.raizes_evidencia = raizes_evidencia or [
            self.raiz, self.repo, CASA, os.path.join(local, "hermes"), local]
        # Onde um caminho sem raiz reconhecivel e PROCURADO pelo sufixo
        # (profundidade limitada; so conta se houver UM so resultado).
        self.raizes_de_procura = raizes_de_procura or [
            os.path.join(local, "hermes", "profiles", "sintonia-lab", "lab", "estudos"),
            os.path.join(CASA, "auditoria-madrugada")]

    def pasta(self, *p):
        return os.path.join(self.vivo, *p)


# ════════════════════════════════════════════════════════════════════════════
# TEXTO — normalizar, conceitos, termos
# ════════════════════════════════════════════════════════════════════════════
def normalizar(s):
    # «≠» decompoe-se em «=» + um risco por cima: sem esta troca, tirar os acentos
    # transformava «data no texto ≠ data do fato» em «data no texto = data do fato».
    s = (s or "").replace("≠", " != ")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def conceitos(texto):
    """As TAGS do vocabulario que o texto menciona, com a contagem."""
    n = normalizar(texto)
    out = {}
    for tag, rx in _TERMOS_RE.items():
        k = len(rx.findall(n))
        if k:
            out[tag] = k
    return out


STOP = set("""
a o os as um uma uns umas de do da dos das em no na nos nas por pelo pela pelos
pelas para pra com sem sob sobre entre ate apos ante e ou nem mas que se so ja
nao sim ele ela eles elas isso isto aquilo este esta estes estas esse essa esses
essas seu sua seus suas meu minha nosso nossa lhe lhes quem qual quais quando onde
como porque porque pois mais menos muito muita muitos muitas pouco todo toda todos
todas cada outro outra outros outras mesmo mesma ser sao era foi foram tem ter tinha
ha havia esta estao estava vai vao pode podem deve devem the and for not are was
""".split())
KEEP_CURTOS = {"ff", "g0", "c8", "d1"}


def _radical(t):
    if len(t) <= 4:
        return t
    for suf, rep in (("coes", "cao"), ("oes", "ao"), ("ais", "al"), ("eis", "el"),
                     ("res", "r"), ("s", "")):
        if t.endswith(suf):
            return t[: -len(suf)] + rep
    return t


def termos(texto):
    n = re.sub(r"[^a-z0-9_]+", " ", normalizar(texto))
    out = []
    for t in n.split():
        if t in STOP or (len(t) < 3 and t not in KEEP_CURTOS):
            continue
        out.append(_radical(t))
    return out


def bolsa(texto, peso_titulo=None):
    """Termos + TAGS (como pseudo-termos «#tag»), contados."""
    b = {}
    for t in termos(texto):
        b[t] = b.get(t, 0) + 1
    for tag, k in conceitos(texto).items():
        b["#" + tag] = b.get("#" + tag, 0) + k
    if peso_titulo:
        for t, k in bolsa(peso_titulo).items():
            b[t] = b.get(t, 0) + 2 * k
    return b


# ════════════════════════════════════════════════════════════════════════════
# JSON — escrever sem nunca pisar
# ════════════════════════════════════════════════════════════════════════════
def _dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def escrever_novo(caminho, obj):
    """Cria o ficheiro; se ja existir, FileExistsError. Nunca sobrescreve."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "x", encoding="utf-8", newline="\n") as f:
        f.write(_dump(obj))


def reescrever(caminho, obj):
    """So para ficheiros DERIVADOS ou para marcar um KH (REFORCOS/SUPERSEDED)."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = f"{caminho}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(_dump(obj))
    os.replace(tmp, caminho)


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def agora_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


# ════════════════════════════════════════════════════════════════════════════
# §2 · MEMORY_EVENT/1
# ════════════════════════════════════════════════════════════════════════════
def _data_com_fuso(v):
    try:
        d = _dt.datetime.fromisoformat(str(v))
    except ValueError:
        return False
    return d.tzinfo is not None


def validar_evento(ev):
    """Lista de problemas; vazia = valido. Cada problema nomeia o campo."""
    erros = []
    if not isinstance(ev, dict):
        return ["o evento tem de ser um objecto JSON"]
    for campo in OBRIGATORIOS:
        v = ev.get(campo)
        if v is None or (isinstance(v, (str, list)) and not v):
            erros.append(f"falta o campo obrigatorio {campo}")
    if ev.get("SCHEMA") and ev["SCHEMA"] != "MEMORY_EVENT/1":
        erros.append(f"SCHEMA deve ser MEMORY_EVENT/1, veio {ev['SCHEMA']!r}")
    if ev.get("ID") and not ID_EVENTO.match(str(ev["ID"])):
        erros.append(f"ID fora do formato MEM-<AGENTE>-<AAAAMMDD>-<NN>: {ev['ID']!r}")
    if ev.get("DATA") and not _data_com_fuso(ev["DATA"]):
        erros.append(f"DATA tem de ser ISO com fuso: {ev['DATA']!r}")
    if ev.get("AREA") and ev["AREA"] not in AREAS:
        erros.append(f"AREA fora do vocabulario fechado: {ev['AREA']!r} (validas: {', '.join(AREAS)})")
    if ev.get("ESPECIE") and ev["ESPECIE"] not in ESPECIES:
        erros.append(f"ESPECIE fora do vocabulario: {ev['ESPECIE']!r} (validas: {', '.join(ESPECIES)})")
    if "TAGS" in ev and ev["TAGS"]:
        if not isinstance(ev["TAGS"], list):
            erros.append("TAGS tem de ser uma lista")
        elif not any(t in TAGS_BASE for t in ev["TAGS"]):
            erros.append(f"TAGS precisa de pelo menos uma tag do vocabulario ({', '.join(TAGS_BASE)})")
    if "EVIDENCIA" in ev and ev["EVIDENCIA"] and not isinstance(ev["EVIDENCIA"], list):
        erros.append("EVIDENCIA tem de ser uma lista")
    if ev.get("FATO") is not None and not isinstance(ev.get("FATO"), str):
        erros.append("FATO tem de ser texto")
    return erros


def sigla_do_agente(agente):
    a = re.split(r"[\s(]", str(agente).strip())[0].lower()
    if a.startswith("sintonia-"):
        a = a[len("sintonia-"):]
    return re.sub(r"[^A-Z0-9]", "", a.upper()) or "AGENTE"


def registrar(cfg, ev):
    """Grava UM evento novo. Devolve o ID. Nunca escreve num ficheiro existente."""
    ev = dict(ev)
    ev.setdefault("SCHEMA", "MEMORY_EVENT/1")
    if not ev.get("DATA"):
        ev["DATA"] = agora_iso()
    pedido_id = ev.get("ID")
    if not pedido_id:
        ev["ID"] = "MEM-AGENTE-00000000-00"          # so para validar o resto
    erros = validar_evento(ev)
    if erros:
        raise Recusa("evento recusado, nada gravado: " + "; ".join(erros))
    pasta = cfg.pasta("eventos")
    os.makedirs(pasta, exist_ok=True)
    if pedido_id:
        try:
            escrever_novo(os.path.join(pasta, pedido_id + ".json"), ev)
        except FileExistsError:
            raise Recusa(f"ja existe um evento com o ID {pedido_id}; nada foi sobrescrito")
        return pedido_id
    dia = str(ev["DATA"])[:10].replace("-", "")
    prefixo = f"MEM-{sigla_do_agente(ev['AGENTE_ORIGEM'])}-{dia}-"
    n = 1
    while True:
        ev["ID"] = f"{prefixo}{n:02d}"
        try:
            escrever_novo(os.path.join(pasta, ev["ID"] + ".json"), ev)
            return ev["ID"]
        except FileExistsError:
            n += 1


def tags_derivadas(ev):
    texto = " ".join(str(ev.get(k) or "") for k in
                     ("TIPO", "FATO", "IMPACTO", "CAUSA", "RESOLUCAO"))
    c = conceitos(texto)
    return sorted(c, key=lambda t: (-c[t], t))


def importar(cfg, caminho_jsonl):
    """Importa eventos JSONL TAL COMO ESTAO (§2). So acrescenta SCHEMA,
    IMPORTADO_DE e — se faltarem — TAGS/AREA. Idempotente."""
    with open(caminho_jsonl, "rb") as f:
        linhas = f.read().split(b"\n")
    feitos = []
    for i, bruto in enumerate(linhas, 1):
        bruto = bruto.rstrip(b"\r")
        if not bruto.strip():
            continue
        original = json.loads(bruto.decode("utf-8"))
        ev = dict(original)
        acrescentado = []
        if "SCHEMA" not in ev:
            ev["SCHEMA"] = "MEMORY_EVENT/1"
            acrescentado.append("SCHEMA")
        if not ev.get("TAGS"):
            ev["TAGS"] = tags_derivadas(ev)
            acrescentado.append("TAGS")
        if not ev.get("AREA"):
            raise Recusa(f"linha {i}: sem AREA, e a importacao nao inventa area")
        ev["IMPORTADO_DE"] = {
            "CAMINHO": os.path.abspath(caminho_jsonl).replace("\\", "/"),
            "LINHA": i,
            "SHA256_DA_LINHA": hashlib.sha256(bruto).hexdigest(),
            "ACRESCENTADO": acrescentado,
        }
        destino = cfg.pasta("eventos", f"{ev.get('ID')}.json")
        if os.path.exists(destino):
            ja = ler(destino)
            if (ja.get("IMPORTADO_DE") or {}).get("SHA256_DA_LINHA") == ev["IMPORTADO_DE"]["SHA256_DA_LINHA"]:
                feitos.append((ev["ID"], "JA_IMPORTADO"))
                continue
            raise Recusa(f"{ev['ID']} ja existe com outro conteudo; nada sobrescrito")
        erros = validar_evento(ev)
        if erros:
            raise Recusa(f"linha {i} ({ev.get('ID')}): " + "; ".join(erros))
        escrever_novo(destino, ev)
        feitos.append((ev["ID"], "IMPORTADO"))
    return feitos


def carregar_eventos(cfg):
    pasta = cfg.pasta("eventos")
    out = {}
    if os.path.isdir(pasta):
        for n in sorted(os.listdir(pasta)):
            if n.endswith(".json"):
                try:
                    ev = ler(os.path.join(pasta, n))
                except (ValueError, OSError):
                    continue
                out[ev.get("ID", n[:-5])] = ev
    return out


# ════════════════════════════════════════════════════════════════════════════
# O LEGADO — inventario das seccoes (§6), sem nunca escrever no ficheiro
# ════════════════════════════════════════════════════════════════════════════
_CACHE = {}


def _chave_ficheiro(p):
    st = os.stat(p)
    return (os.path.abspath(p), st.st_mtime_ns, st.st_size)


RX_TOPO = re.compile(r"^# (§)?(\d+)(\.)?\s*(?:·\s*)?(.*)$")
RX_SUB_NM = re.compile(r"^## (\d+)[.\-](\d+)\s*(?:·\s*)?(.*)$")
RX_SUB_N = re.compile(r"^## (\d+)\s*·\s*(.*)$")
# As tres formas medidas no legado: «SUPERADA — ver §109.7», «CORRIGIDO PELO §139»
# e «ESTADO = SUPERSEDED em …» (esta sem alvo).
RX_SUPERADO = re.compile(
    r"(superad[oa]s?|supersed\w*|corrigid[oa]s?|substitu[ií]d[oa]s?)\s*[—:,-]?\s*"
    r"(?:pel[oa]s?|por|by|ver)\s+(?:o\s+|a\s+)?§\s?(\d+(?:\.\d+)?)", re.I)
RX_ESTADO_SUPERSEDED = re.compile(r"ESTADO\s*=\s*SUPERSEDED", re.I)
RX_CITA = re.compile(r"§\s?(\d+(?:\.\d+)?)")
RX_ENT = re.compile(r"\bD\d{1,3}\b|`[^`\n]{3,60}`|\b[A-Z][A-Z0-9]+(?:[_-][A-Z0-9]+)+\b")


def secoes_do_legado(caminho):
    """Lista de seccoes: `# §N`/`# N.` e as filhas `## N.M`/`## n ·`.
    Blocos de codigo (```) nao contam como cabecalho."""
    chave = ("legado", _chave_ficheiro(caminho))
    if chave in _CACHE:
        return _CACHE[chave]
    with open(caminho, encoding="utf-8") as f:
        linhas = f.read().split("\n")
    cabec = []
    cerca = False
    pai = None
    for i, l in enumerate(linhas, 1):
        if l.lstrip().startswith("```"):
            cerca = not cerca
            continue
        if cerca:
            continue
        m = RX_TOPO.match(l)
        if m and l.startswith("# "):
            pai = m.group(2)
            cabec.append({"nivel": 1, "id": f"LEG-§{pai}", "linha": i,
                          "titulo": m.group(4).strip() or l[2:].strip(), "original": l[2:].strip()})
            continue
        if pai is None:
            continue
        m = RX_SUB_NM.match(l)
        # «## 43.1» sob o §43 e filha; «## 2026-09-09» sob o §40 e uma data (medido:
        # os 2 unicos «## N.M» cujo N nao e o do pai sao essas duas datas).
        if m and m.group(1) == pai:
            num = f"{m.group(1)}.{m.group(2)}"
            cabec.append({"nivel": 2, "id": f"LEG-§{num}", "linha": i,
                          "titulo": m.group(3).strip(), "original": l[3:].strip(), "pai": pai})
            continue
        m = RX_SUB_N.match(l)
        if m:
            cabec.append({"nivel": 2, "id": f"LEG-§{pai}.{m.group(1)}", "linha": i,
                          "titulo": m.group(2).strip(), "original": l[3:].strip(), "pai": pai})
    total = len(linhas)
    while total > 1 and linhas[total - 1] == "":
        total -= 1
    # IDs repetidos (duas filhas «## 1 ·» sob o mesmo pai, por exemplo) ganham a
    # linha como sufixo — o ID continua estavel enquanto o ficheiro nao mudar ali.
    vistos = {}
    for c in cabec:
        vistos[c["id"]] = vistos.get(c["id"], 0) + 1
    for c in cabec:
        if vistos[c["id"]] > 1:
            c["id"] = f"{c['id']}@L{c['linha']}"
    secoes = []
    for k, c in enumerate(cabec):
        fim = total
        for d in cabec[k + 1:]:
            if d["nivel"] <= c["nivel"]:
                fim = d["linha"] - 1
                break
        # a introducao do pai acaba na primeira filha
        fim_proprio = fim
        if c["nivel"] == 1:
            for d in cabec[k + 1:]:
                if d["nivel"] == 1:
                    break
                fim_proprio = d["linha"] - 1
                break
        while fim > c["linha"] and linhas[fim - 1].strip() in ("", "---"):
            fim -= 1
        while fim_proprio > c["linha"] and linhas[fim_proprio - 1].strip() in ("", "---"):
            fim_proprio -= 1
        texto = "\n".join(linhas[c["linha"] - 1:fim])
        proprio = "\n".join(linhas[c["linha"] - 1:fim_proprio])
        secoes.append(dict(c, fim=fim, fim_proprio=fim_proprio, texto=texto, proprio=proprio,
                           proprio_sem_codigo=_sem_codigo(proprio), tem_filhas=fim_proprio != fim))
    _CACHE[chave] = secoes
    return secoes


LINGUAGENS_DE_CODIGO = ("python", "py", "json", "sql", "bash", "sh", "js", "javascript",
                        "yaml", "yml", "powershell", "ps1", "mjs", "html", "css")


def _sem_codigo(texto):
    """Tira os blocos de PROGRAMA (```python, ```bash, ```json…): codigo nao e texto
    de conhecimento — uma variavel `pronto` fazia a §102.4 parecer-se com «Pronto
    no ramo nao e funcionando». Os blocos sem linguagem (ou ```text) ficam: o
    legado usa-os para escrever as leis em destaque (medido: 2063 cercas sem
    linguagem e 106 `text`, contra 17 de programa)."""
    out, dentro, codigo = [], False, False
    for l in texto.split("\n"):
        s = l.strip()
        if s.startswith("```"):
            if not dentro:
                dentro, codigo = True, s[3:].strip().lower() in LINGUAGENS_DE_CODIGO
            else:
                dentro, codigo = False, False
            continue
        if not codigo:
            out.append(l)
    return "\n".join(out)


def _entidades(texto, maximo=12):
    cont = {}
    for m in RX_ENT.findall(texto):
        cont[m] = cont.get(m, 0) + 1
    return [e for e, _ in sorted(cont.items(), key=lambda x: (-x[1], x[0]))[:maximo]]


def _tags_de(titulo, corpo):
    c_tit = conceitos(titulo)
    c_corpo = conceitos(corpo)
    n = max(1, len(termos(corpo)))
    densas = {t for t, k in c_corpo.items() if k >= 3 and k / n >= 0.01}
    return sorted(set(c_tit) | densas)


def _area_das_tags(tags):
    for t, a in AREA_POR_TAG:
        if t in tags:
            return a
    return None


# ════════════════════════════════════════════════════════════════════════════
# CANDIDATOS, CONHECIMENTO, REFORCOS
# ════════════════════════════════════════════════════════════════════════════
def carregar_candidatos(cfg):
    pasta = cfg.pasta("candidatos")
    out = {}
    if os.path.isdir(pasta):
        for n in sorted(os.listdir(pasta)):
            if n.endswith(".json"):
                c = ler(os.path.join(pasta, n))
                out[c["ID"]] = c
    return out


def carregar_conhecimento(cfg):
    pasta = cfg.pasta("conhecimento")
    out = {}
    if os.path.isdir(pasta):
        for n in sorted(os.listdir(pasta)):
            if n.endswith(".json"):
                k = ler(os.path.join(pasta, n))
                out[k["ID"]] = k
    return out


def reforcos_do_legado(cfg):
    """Os REFORCOS de uma seccao legada vivem nos candidatos (a fonte) e sao
    projectados no SECOES.json a cada indexacao — o derivado nunca e a fonte."""
    out = {}
    for c in carregar_candidatos(cfg).values():
        if c.get("RESULTADO") == "REFORCO" and str(c.get("ALVO", "")).startswith("LEG-"):
            out.setdefault(c["ALVO"], []).append({
                "CANDIDATO": c["ID"], "TITULO": c.get("TITULO"), "TEXTO": c.get("TEXTO"),
                "EVENTOS": c.get("EVENTOS", []), "DATA": c.get("CONSOLIDADO_EM")})
    return out


def _unidades(cfg):
    """O que o K5/K6 e a busca comparam: seccoes-folha do legado (a introducao do
    pai conta a parte) + KH do Know How vivo. Cada linha de texto pertence a UMA."""
    unid = []
    reforcos = reforcos_do_legado(cfg)
    eventos = None
    if os.path.exists(cfg.legado):
        for s in secoes_do_legado(cfg.legado):
            extra = ""
            tags_ref = set()
            for r in reforcos.get(s["id"], []):
                extra += "\n" + (r.get("TITULO") or "") + "\n" + (r.get("TEXTO") or "")
                if eventos is None:
                    eventos = carregar_eventos(cfg)
                for e in r.get("EVENTOS", []):
                    tags_ref |= set((eventos.get(e) or {}).get("TAGS") or [])
                tags_ref |= set(conceitos((r.get("TITULO") or "") + " " + (r.get("TEXTO") or "")))
            corpo = s["proprio_sem_codigo"]
            unid.append({"ID": s["id"], "TIPO": "LEGADO", "TITULO": s["titulo"],
                         "TEXTO": corpo + extra, "STATUS": None, "SECAO": s,
                         "TAGS": sorted(set(_tags_de(s["titulo"], corpo)) | tags_ref),
                         "REFORCOS": reforcos.get(s["id"], [])})
    for k in carregar_conhecimento(cfg).values():
        unid.append({"ID": k["ID"], "TIPO": "KH", "TITULO": k.get("TITULO", ""),
                     "TEXTO": k.get("TEXTO", ""), "STATUS": k.get("STATUS"),
                     "TAGS": k.get("TAGS", []), "KH": k, "REFORCOS": k.get("REFORCOS", [])})
    return unid


def _bolsa_da_unidade(u):
    if u["TIPO"] != "LEGADO":
        return bolsa(u["TEXTO"], peso_titulo=u["TITULO"])
    chave = ("bolsa", u["ID"], hashlib.sha1(u["TEXTO"].encode("utf-8")).hexdigest())
    if chave not in _CACHE:
        _CACHE[chave] = bolsa(u["TEXTO"], peso_titulo=u["TITULO"])
    return _CACHE[chave]


def _vetores(unid):
    bolsas = [_bolsa_da_unidade(u) for u in unid]
    df = {}
    for b in bolsas:
        for t in b:
            df[t] = df.get(t, 0) + 1
    n = len(bolsas)
    idf = {t: math.log((n + 1) / (d + 0.5)) for t, d in df.items()}
    return bolsas, idf


def _cosseno(b1, b2, idf, idf_omissao):
    def v(b):
        return {t: (1 + math.log(k)) * idf.get(t, idf_omissao) for t, k in b.items()}
    a, c = v(b1), v(b2)
    num = sum(a[t] * c[t] for t in a if t in c)
    den = math.sqrt(sum(x * x for x in a.values())) * math.sqrt(sum(x * x for x in c.values()))
    return num / den if den else 0.0


def semelhantes(cfg, texto, titulo="", so_active=True, top=5):
    unid = [u for u in _unidades(cfg)
            if not so_active or u["TIPO"] == "LEGADO" or u["STATUS"] == "ACTIVE"]
    if not unid:
        return []
    bolsas, idf = _vetores(unid)
    idf_omissao = math.log(len(unid) + 1)
    alvo = bolsa(texto, peso_titulo=titulo)
    notas = [(_cosseno(alvo, b, idf, idf_omissao), u) for b, u in zip(bolsas, unid)]
    notas.sort(key=lambda x: (-x[0], x[1]["ID"]))
    return notas[:top]


# ════════════════════════════════════════════════════════════════════════════
# §5 · K1–K8 — um modulo, uma funcao por K. Cada uma devolve
#      (VEREDITO, MOTIVO, EXTRA). ACTIVE so se as oito derem PASS.
# ════════════════════════════════════════════════════════════════════════════
PASS, FAIL, NAO_SEI = "PASS", "FAIL", "NAO_SEI"


def k1_origem(cand, ctx):
    evs = cand.get("EVENTOS") or []
    if not evs:
        return FAIL, "o candidato nao cita nenhum evento (texto orfao)", {}
    faltas = []
    for e in evs:
        ev = ctx["eventos"].get(e)
        if ev is None:
            faltas.append(f"{e}: nao existe em eventos/")
            continue
        for campo in ("AGENTE_ORIGEM", "DATA", "EVIDENCIA"):
            if not ev.get(campo):
                faltas.append(f"{e}: sem {campo}")
    if faltas:
        return FAIL, "; ".join(faltas), {}
    return PASS, f"{len(evs)} evento(s) com origem, data e evidencia: {', '.join(evs)}", {}


def _decisao_conta(ev):
    agente = re.split(r"[\s(]", str(ev.get("AGENTE_ORIGEM", "")).strip().lower())[0]
    texto = " ".join([str(ev.get("FATO") or "")] + [str(x) for x in ev.get("EVIDENCIA") or []])
    return agente in AGENTES_DECISORES and bool(re.search(r"\bD\d{1,4}\b", texto))


def base_do_candidato(cand, ctx):
    """Os eventos que podem sustentar conhecimento: FATO_MEDIDO, e DECISAO que conta."""
    evs = [ctx["eventos"][e] for e in cand.get("EVENTOS") or [] if e in ctx["eventos"]]
    medidos = [e for e in evs if e.get("ESPECIE") == "FATO_MEDIDO"]
    decisoes = [e for e in evs if e.get("ESPECIE") == "DECISAO" and _decisao_conta(e)]
    return medidos, decisoes


def k2_tipo(cand, ctx):
    evs = [ctx["eventos"][e] for e in cand.get("EVENTOS") or [] if e in ctx["eventos"]]
    if not evs:
        return FAIL, "nenhum evento para classificar", {}
    sem = [e.get("ID") for e in evs if e.get("ESPECIE") not in ESPECIES]
    if sem:
        return FAIL, f"ESPECIE vazia ou fora do vocabulario em {', '.join(map(str, sem))}", {}
    medidos, decisoes = base_do_candidato(cand, ctx)
    especies = sorted({e["ESPECIE"] for e in evs})
    if medidos:
        return PASS, f"{len(medidos)} FATO_MEDIDO ({', '.join(e['ID'] for e in medidos)}); especies: {', '.join(especies)}", {}
    if decisoes:
        return PASS, f"DECISAO do dono/coordenador com D-n: {', '.join(e['ID'] for e in decisoes)}", {}
    return FAIL, (f"so {', '.join(especies)}: RELATO/HIPOTESE/INFERENCIA nunca vira fato, "
                  "e DECISAO so conta do dono ou do coordenador com D-n"), {}


# ── K3 · evidencia ──────────────────────────────────────────────────────────
COMANDOS = ("git", "ls", "py", "python", "python3", "node", "wc", "grep", "cat",
            "sha256sum", "curl", "pytest", "npm", "npx", "psql", "rg", "find")
RX_SHA = re.compile(r"\b[0-9a-f]{7,40}\b")
RX_EXT = re.compile(r"\.[A-Za-z0-9]{1,8}$")
_GIT_CACHE = {}


def _commit_existe(repo, sha):
    k = (repo, sha)
    if k not in _GIT_CACHE:
        r = subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"],
                           capture_output=True)
        _GIT_CACHE[k] = r.returncode == 0
    return _GIT_CACHE[k]


def _limpar_token(t):
    t = t.strip("()[]{},;«»\"'`|")
    t = re.sub(r":[0-9][0-9,\-]*$", "", t)
    return t


def _procurar_sufixo(raiz, sufixo, profundidade=4):
    achados = []
    sufixo = sufixo.replace("\\", "/").lower()
    base = raiz.rstrip("/\\")
    for dirpath, dirnames, filenames in os.walk(base):
        nivel = dirpath[len(base):].count(os.sep)
        if nivel >= profundidade:
            dirnames[:] = []
        for fn in filenames:
            p = os.path.join(dirpath, fn).replace("\\", "/")
            if p.lower().endswith("/" + sufixo):
                achados.append(p)
    return achados


def resolver_caminho(cfg, token, irmaos=()):
    """Devolve (caminho_resolvido | None, como)."""
    t = token.replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", t) or t.startswith("/"):
        return (t, "ABSOLUTO") if os.path.exists(t) else (None, "ABSOLUTO")
    for r in list(irmaos) + list(cfg.raizes_evidencia):
        p = os.path.join(r, t)
        if os.path.exists(p):
            return p.replace("\\", "/"), f"RAIZ {r}"
    if "/" in t:
        for r in cfg.raizes_de_procura:
            if os.path.isdir(r):
                ach = _procurar_sufixo(r, t)
                if len(ach) == 1:
                    return ach[0], f"PROCURA {r}"
                if len(ach) > 1:
                    return None, f"AMBIGUO ({len(ach)} em {r})"
    return None, "NAO_ACHADO"


def classificar_evidencia(cfg, ev):
    """Cada item da EVIDENCIA (e de COMMITS) → forte, fraco, ou caminho inexistente."""
    itens = []
    irmaos = []
    brutos = [("EVIDENCIA", str(x)) for x in ev.get("EVIDENCIA") or []] + \
             [("COMMITS", str(x)) for x in ev.get("COMMITS") or []]
    # primeira volta: caminhos com barra (dao as pastas «irmas» dos nomes soltos)
    for campo, item in brutos:
        s = item.strip()
        primeiro = s.split()[0] if s.split() else ""
        reg = {"CAMPO": campo, "ITEM": item, "FORTE": False, "PROVAS": [], "INEXISTENTES": [],
               "NAO_CONFERIDOS": []}
        if re.match(r"^https?://", s):
            reg["NAO_CONFERIDOS"].append("URL (nao conferida offline)")
        elif primeiro.lower() in COMANDOS and campo == "EVIDENCIA":
            reg["FORTE"] = True
            reg["PROVAS"].append(f"COMANDO {primeiro}")
        else:
            for tok in s.split():
                tok = _limpar_token(tok)
                if "/" in tok.replace("\\", "/") and RX_EXT.search(tok) and "*" not in tok:
                    p, como = resolver_caminho(cfg, tok)
                    if p:
                        reg["FORTE"] = True
                        reg["PROVAS"].append(f"CAMINHO {tok} → {p}")
                        irmaos.append(os.path.dirname(p))
                    else:
                        reg["INEXISTENTES"].append(f"{tok} ({como})")
        for sha in RX_SHA.findall(s.lower()):
            if _commit_existe(cfg.repo, sha):
                reg["FORTE"] = True
                reg["PROVAS"].append(f"COMMIT {sha}")
        itens.append(reg)
    # segunda volta: nomes soltos («AB-DETECCAO-V1.json») ao lado dos que ja se acharam
    for reg in itens:
        if reg["PROVAS"] and reg["FORTE"]:
            continue
        s = reg["ITEM"].strip()
        if re.match(r"^https?://", s) or (s.split() and s.split()[0].lower() in COMANDOS):
            continue
        for tok in s.split():
            tok = _limpar_token(tok)
            if "/" not in tok and RX_EXT.search(tok) and re.match(r"^[\w.\-]+$", tok) \
                    and not re.match(r"^\d", tok):
                p, como = resolver_caminho(cfg, tok, irmaos=irmaos)
                if p:
                    reg["FORTE"] = True
                    reg["PROVAS"].append(f"NOME {tok} → {p}")
                else:
                    reg["NAO_CONFERIDOS"].append(f"nome solto {tok} (sem pasta; nao conferido)")
    return itens


def k3_evidencia(cand, ctx):
    cfg = ctx["cfg"]
    evs = [ctx["eventos"][e] for e in cand.get("EVENTOS") or [] if e in ctx["eventos"]]
    medidos, decisoes = base_do_candidato(cand, ctx)
    base_ids = {e["ID"] for e in (medidos or decisoes)}
    detalhe, inexistentes, fortes = {}, [], []
    for ev in evs:
        itens = classificar_evidencia(cfg, ev)
        detalhe[ev["ID"]] = itens
        for it in itens:
            inexistentes += [f"{ev['ID']}: {x}" for x in it["INEXISTENTES"]]
            if it["FORTE"] and ev["ID"] in base_ids:
                fortes.append(f"{ev['ID']}: {it['PROVAS'][0]}")
    if inexistentes:
        return FAIL, "caminho citado que nao existe: " + "; ".join(inexistentes), {"DETALHE": detalhe}
    if not fortes:
        return FAIL, ("nenhuma evidencia forte (commit que existe, comando git/runtime, "
                      "caminho que existe) num evento FATO_MEDIDO/DECISAO"), {"DETALHE": detalhe}
    return PASS, f"{len(fortes)} evidencia(s) forte(s); ex.: {fortes[0]}", {"DETALHE": detalhe}


# ── K4 · durabilidade ───────────────────────────────────────────────────────
MOMENTANEO = [r"\bas \d{1,2}(:|h)\d{2}\b", r"\b\d{1,2}:\d{2}\b", r"\bagora\b",
              r"\bneste momento\b", r"\bhoje\b", r"\bocupad[ao]s?\b", r"\bem curso\b",
              r"\bem execucao\b", r"\besta (a )?rodar\b", r"\besta rodando\b",
              r"\bpor enquanto\b"]
REGRA_GERAL = [r"\bsempre\b", r"\bnunca\b", r"\bquando\b", r"\btoda vez\b", r"\bcada vez\b",
               r"\bantes de\b", r"\bdepois de\b", r"\benquanto\b", r"\bem qualquer\b",
               r"\bso (\w+ ){0,6}(se|quando)\b", r"≠", r"!=", r"\bnao vira\b"]


def k4_durabilidade(cand, ctx):
    n = normalizar((cand.get("TITULO") or "") + " . " + (cand.get("TEXTO") or ""))
    marcas = [p for p in MOMENTANEO if re.search(p, n)]
    if not marcas:
        return PASS, "sem marca de estado momentaneo", {}
    geral = [p for p in REGRA_GERAL if re.search(p, n)]
    if geral:
        return PASS, "tem marca momentanea, mas dentro de uma regra geral", {"MARCAS": marcas}
    return FAIL, ("estado momentaneo sem regra geral (" +
                  ", ".join(re.search(p, n).group(0) for p in marcas) +
                  "): nao sera util numa missao futura"), {}


# ── K5 · nao duplicado ──────────────────────────────────────────────────────
def k5_nao_duplicado(cand, ctx):
    viz = semelhantes(ctx["cfg"], cand.get("TEXTO") or "", cand.get("TITULO") or "")
    if not viz:
        return NAO_SEI, "indice vazio: nao ha com que comparar (nem legado, nem KH)", {}
    lista = [{"ID": u["ID"], "SEMELHANCA": round(s, 4), "TITULO": u["TITULO"][:90]} for s, u in viz]
    melhor_s, melhor = viz[0]
    # O proponente pode apontar o alvo (o LAB fez a sua checagem de duplicata).
    # A pista so ESCOLHE entre alvos que a medida ja poe acima do limiar: nunca
    # transforma um candidato novo em reforco, nem um reforco em novo.
    propostos = [a for a in (cand.get("ALVO_PROPOSTO") or []) if isinstance(a, str)]
    if propostos:
        todos = semelhantes(ctx["cfg"], cand.get("TEXTO") or "", cand.get("TITULO") or "",
                            top=100000)
        nota = {u["ID"]: s for s, u in todos}
        conferidos = sorted(((nota.get(a, 0.0), a) for a in propostos), reverse=True)
        for s, a in conferidos:
            if s >= LIMIAR_K5:
                return "DUPLICADO", (f"equivale a {a} — alvo proposto por quem propos, conferido "
                                     f"pela medida ({s:.3f} >= limiar {LIMIAR_K5}); o mais "
                                     f"proximo sem pista e {melhor['ID']} ({melhor_s:.3f})"), \
                    {"ALVO": a, "VIZINHOS": lista,
                     "ALVO_PROPOSTO_CONFERIDO": [{"ID": x, "SEMELHANCA": round(y, 4)}
                                                 for y, x in conferidos]}
    if melhor_s >= LIMIAR_K5:
        return "DUPLICADO", (f"equivale a {melhor['ID']} «{melhor['TITULO'][:70]}» "
                             f"(semelhanca {melhor_s:.3f} >= limiar {LIMIAR_K5})"), \
            {"ALVO": melhor["ID"], "VIZINHOS": lista}
    return PASS, (f"nenhum equivalente: o mais proximo e {melhor['ID']} "
                  f"({melhor_s:.3f} < limiar {LIMIAR_K5})"), {"VIZINHOS": lista}


# ── K6 · nao contraditorio ──────────────────────────────────────────────────
NEGADORES = ("nao", "nunca", "sem", "nem", "jamais")


def _polaridades(texto):
    """termo → conjunto de polaridades com que aparece (True = negado)."""
    ts = re.sub(r"[^a-z0-9_]+", " ", normalizar(texto)).split()
    out = {}
    for i, t in enumerate(ts):
        if t in STOP or t in NEGADORES or len(t) < 3:
            continue
        neg = any(ts[j] in NEGADORES for j in range(max(0, i - 3), i))
        out.setdefault(_radical(t), set()).add(neg)
    return out


def k6_nao_contraditorio(cand, ctx):
    viz = [(s, u) for s, u in semelhantes(ctx["cfg"], cand.get("TEXTO") or "",
                                          cand.get("TITULO") or "", top=10)
           if u["TIPO"] == "KH" and u["STATUS"] == "ACTIVE" and s >= LIMIAR_ALVO_K6]
    if not viz:
        return PASS, "nenhum KH ACTIVE sobre o mesmo alvo", {}
    novo = _polaridades(cand.get("TEXTO") or "")
    for s, u in viz:
        velho = _polaridades(u["TEXTO"])
        opostos = sorted(t for t in set(novo) & set(velho)
                         if len(novo[t]) == 1 and len(velho[t]) == 1 and novo[t] != velho[t])
        ambos = sorted(t for t in set(novo) & set(velho) if len(novo[t] | velho[t]) > 1
                       and t not in opostos)
        if opostos:
            return FAIL, (f"nega {u['ID']} (semelhanca {s:.3f}): polaridade oposta em "
                          f"{', '.join(opostos)}"), {"ALVO": u["ID"]}
        if ambos and s < LIMIAR_K5:
            return NAO_SEI, (f"{u['ID']} e parecido ({s:.3f}) e a polaridade de "
                             f"{', '.join(ambos)} e ambigua: na duvida, conflito"), {"ALVO": u["ID"]}
    return PASS, f"mesma direcao que {viz[0][1]['ID']} (sem negacao oposta)", {}


# ── K7 · autoridade ─────────────────────────────────────────────────────────
MARCAS_NEG = r"(≠|!=|=/=|\bnao vira\b|\bnunca vira\b|\bnao e\b|\bnunca e\b|\bnao substitui\b|\bnao conta como\b|\bnao vale como\b)"
MARCAS_POS = r"(\bvira\b|\bconta como\b|\bvale como\b|\bserve (de|como)\b|\bsubstitui\b|\bpassa a ser\b|(?<![!=<>])=(?!=))"
DELIM = r"[;:.,()\[\]«»\"|\n—]"


def _lados(frase, rx_marca):
    """[(lado_esquerdo, lado_direito, marca)] para cada marca na frase."""
    out = []
    partes = re.split(rx_marca, frase)
    # re.split com grupo devolve [txt, marca, (subgrupos...), txt, ...]
    blocos = [p for p in partes if p is not None]
    seq = []
    for p in blocos:
        if re.fullmatch(rx_marca, p or ""):
            seq.append(("M", p))
        elif p and not re.fullmatch(r"\s*(de|como)\s*", p):
            seq.append(("T", p))
    for i, (tipo, v) in enumerate(seq):
        if tipo == "M" and 0 < i < len(seq) - 1 and seq[i - 1][0] == "T" and seq[i + 1][0] == "T":
            esq = re.split(DELIM, seq[i - 1][1])[-1]
            dir_ = re.split(DELIM, seq[i + 1][1])[0]
            out.append((esq, dir_, v))
    return out


def regras_de_autoridade(cfg):
    """As regras «X ≠ Y» / «X nao vira Y» das fontes de autoridade, com fonte:linha.
    Devolve (regras, fontes_lidas, fontes_em_falta)."""
    fontes = []
    agents = os.path.join(cfg.repo, "AGENTS.md")
    fontes.append(("AGENTS.md", agents, "LEIS"))
    r = subprocess.run(["git", "-C", cfg.repo, "ls-files"], capture_output=True, text=True,
                       encoding="utf-8")
    for p in sorted(r.stdout.splitlines()):
        base = p.rsplit("/", 1)[-1]
        if re.match(r"^BIBLIA-.*\.md$", base) or re.match(r"^CONTRATO-.*\.md$", base):
            fontes.append((p, os.path.join(cfg.repo, p), "TUDO"))
    fontes.append((cfg.decisoes.replace("\\", "/"), cfg.decisoes, "DECISOES"))
    chave = ("autoridade", tuple((f[1], _chave_ficheiro(f[1]) if os.path.exists(f[1]) else None)
                                 for f in fontes))
    if chave in _CACHE:
        return _CACHE[chave]
    regras, lidas, falta = [], [], []
    for nome, caminho, modo in fontes:
        if not os.path.exists(caminho):
            falta.append(nome)
            continue
        lidas.append(nome)
        with open(caminho, encoding="utf-8", errors="replace") as f:
            linhas = f.read().split("\n")
        dentro = modo != "LEIS"
        dnum = None
        for i, l in enumerate(linhas, 1):
            if modo == "LEIS":
                if l.startswith("## "):
                    dentro = "LEIS DO SINTONIA QUE O MAPA NAO PODE VIOLAR" in normalizar(l).upper()
                if not dentro:
                    continue
            if modo == "DECISOES":
                m = re.match(r"^## (D\d+)\b", l)
                if m:
                    dnum = m.group(1)
            n = normalizar(l)
            if not re.search(MARCAS_NEG, n):
                continue
            for esq, dir_, marca in _lados(n, MARCAS_NEG):
                ce, cd = set(conceitos(esq)), set(conceitos(dir_))
                if ce and cd and ce != cd:
                    regras.append({"FONTE": f"{nome}:{i}" + (f" ({dnum})" if dnum else ""),
                                   "ESQ": sorted(ce), "DIR": sorted(cd),
                                   "TEXTO": l.strip()[:200]})
    res = (regras, lidas, falta)
    _CACHE[chave] = res
    return res


def relacoes_do_candidato(texto):
    n = normalizar(texto)
    out = []
    for esq, dir_, _ in _lados(n, MARCAS_NEG):
        out.append((set(conceitos(esq)), set(conceitos(dir_)), "NEG"))
    # positivas: so nas partes da frase sem marca negativa
    for pedaco in re.split(MARCAS_NEG, n):
        if pedaco is None or re.fullmatch(MARCAS_NEG, pedaco):
            continue
        for esq, dir_, _ in _lados(pedaco, MARCAS_POS):
            if re.search(r"\b(nao|nunca|jamais)\s*$", esq):
                out.append((set(conceitos(esq)), set(conceitos(dir_)), "NEG"))
            else:
                out.append((set(conceitos(esq)), set(conceitos(dir_)), "POS"))
    return [r for r in out if r[0] or r[1]]


def k7_autoridade(cand, ctx):
    regras, lidas, falta = regras_de_autoridade(ctx["cfg"])
    if falta:
        return NAO_SEI, ("nao consegui ler a autoridade: " + ", ".join(falta) +
                         " — sem ela nao se promove"), {}
    texto = (cand.get("TITULO") or "") + " . " + (cand.get("TEXTO") or "")
    todos = set(conceitos(texto))
    rels = relacoes_do_candidato(cand.get("TEXTO") or "")
    contraria, cobre = [], []
    for rg in regras:
        e, d = set(rg["ESQ"]), set(rg["DIR"])
        for (ce, cd, pol) in rels:
            toca = (ce | cd) & (e | d)
            if not toca:
                continue
            cruza = (ce & e and cd & d) or (ce & d and cd & e)
            if pol == "POS" and cruza:
                contraria.append(rg)
            elif pol == "NEG" and (todos & e) and (todos & d):
                cobre.append(rg)
    if contraria:
        return "CONTRARIA", ("contraria " + "; ".join(f"{r['FONTE']} «{r['TEXTO'][:90]}»"
                                                     for r in contraria[:3])), \
            {"AUTORIDADE": contraria}
    if cobre:
        return "COBERTO", ("ja coberto por " + "; ".join(f"{r['FONTE']} «{r['TEXTO'][:90]}»"
                                                        for r in cobre[:3])), \
            {"AUTORIDADE": cobre}
    return PASS, (f"nenhuma regra de autoridade sobre os conceitos do candidato "
                  f"({', '.join(sorted(todos)) or 'nenhum do vocabulario'}); "
                  f"{len(regras)} regras lidas de {len(lidas)} fontes"), {}


# ── K8 · aprendizado, nao incidente ─────────────────────────────────────────
FORMA_DE_REGRA = [r"≠", r"!=", r"\bnao (e|vira|conta|garante|substitui|prova|basta|pode)\b",
                  r"\bnunca\b", r"\bsempre\b", r"\bso (\w+ ){0,6}(se|quando)\b",
                  r"\bsomente (\w+ ){0,6}(se|quando)\b", r"\bantes de\b", r"\bdeve(m)?\b",
                  r"\bt[eê]m (de|que)\b", r"\bprecisa(m)?\b", r"\bexige(m)?\b"]
IMPERATIVOS = set("""
meca mede medir espere esperar use usar confira conferir leia ler releia reler tipar tipe
trate tratar pergunte perguntar registre registe registar registrar verifique verificar
prove provar compare comparar separe separar guarde guardar corra correr instale instalar
evite evitar faca fazer declare declarar escreva escrever pare parar marque marcar conte
contar consulte consultar olhe olhar procure procurar solte soltar avise avisar confie
confiar rode rodar
""".split())
NARRACAO = [r"\b(foi|foram|fez|fizeram|commitou|mediu|disse|passaram|passou|aconteceu|"
            r"ficou|chegou|recusou|apagou|rodou|correu|deu|virou|caiu)\b"]
DATAS_NO_TEXTO = r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b|\b20\d\d-\d\d-\d\d\b"


def k8_aprendizado(cand, ctx):
    n = normalizar(cand.get("TEXTO") or "")
    forma = [p for p in FORMA_DE_REGRA if re.search(p, n)]
    oracoes = [o.strip().split() for o in re.split(r"[;:.]", n) if o.strip()]
    imp = [o[0] for o in oracoes if o and o[0] in IMPERATIVOS]
    narra = [m.group(0) for p in NARRACAO for m in re.finditer(p, n)]
    datas = re.findall(DATAS_NO_TEXTO, n)
    if not forma and not imp:
        return FAIL, ("sem forma de regra (imperativo, «X ≠ Y», «so … quando …», nunca/sempre)"
                      + (f"; narracao: {', '.join(narra[:3])}" if narra else "")), {}
    if narra and datas:
        return FAIL, f"narracao com preterito e data ({', '.join(narra[:2])}; {len(datas)} data(s))", {}
    return PASS, "forma de regra: " + ", ".join((imp and [f"imperativo «{imp[0]}»"] or []) +
                                                [re.search(p, n).group(0) for p in forma][:3]), {}


ORDEM_K = ("k1_origem", "k2_tipo", "k3_evidencia", "k4_durabilidade",
           "k5_nao_duplicado", "k6_nao_contraditorio", "k7_autoridade", "k8_aprendizado")


def avaliar(cand, ctx):
    """Corre K1–K8 (pelo NOME, para o corredor de mutantes poder desligar um)."""
    k = {}
    for i, nome in enumerate(ORDEM_K, 1):
        ver, mot, extra = globals()[nome](cand, ctx)
        k[f"K{i}"] = dict({"VEREDITO": ver, "MOTIVO": mot}, **(extra or {}))
    return k


def decidir(k):
    """Precedencia: autoridade contrariada escala; KH contrariado escala; qualquer
    falha de K1–K4/K8 (ou NAO_SEI) bloqueia; coberto por autoridade relaciona;
    duplicado reforca; so as oito PASS promovem."""
    v = {n: k[n]["VEREDITO"] for n in k}
    if v["K7"] == "CONTRARIA":
        return "CONFLITO_DE_AUTORIDADE", "K7"
    if v["K6"] in (FAIL, NAO_SEI):
        return "CONFLITO_KNOW_HOW", "K6"
    for n in ("K1", "K2", "K3", "K4", "K8"):
        if v[n] != PASS:
            return "BLOQUEADO", n
    if v["K7"] == NAO_SEI:
        return "BLOQUEADO", "K7"
    if v["K5"] == NAO_SEI:
        return "BLOQUEADO", "K5"
    if v["K7"] == "COBERTO":
        return "RELACIONADO_A_AUTORIDADE", "K7"
    if v["K5"] == "DUPLICADO":
        return "REFORCO", "K5"
    if all(x == PASS for x in v.values()):
        return "ACTIVE", None
    return "BLOQUEADO", next(n for n, x in v.items() if x != PASS)


# ════════════════════════════════════════════════════════════════════════════
# §4 · CONSOLIDADOR
# ════════════════════════════════════════════════════════════════════════════
def _proximo_kh(cfg, kh):
    pasta = cfg.pasta("conhecimento")
    os.makedirs(pasta, exist_ok=True)
    n = 1 + max([int(x[3:-5]) for x in os.listdir(pasta) if re.match(r"^KH-\d+\.json$", x)] or [0])
    while True:
        kh["ID"] = f"KH-{n:04d}"
        try:
            escrever_novo(os.path.join(pasta, kh["ID"] + ".json"), kh)
            return kh["ID"]
        except FileExistsError:
            n += 1


def _area_do_candidato(cand, eventos):
    if cand.get("AREA") in AREAS:
        return cand["AREA"]
    cont = {}
    for e in cand.get("EVENTOS") or []:
        a = (eventos.get(e) or {}).get("AREA")
        if a:
            cont[a] = cont.get(a, 0) + 1
    return sorted(cont.items(), key=lambda x: (-x[1], x[0]))[0][0] if cont else None


def _handoff(cfg, cand):
    linha = (f"- {agora_iso()} · KNOW-HOW-VIVO · {cand['RESULTADO']} · candidato {cand['ID']} "
             f"«{(cand.get('TITULO') or '')[:80]}» · alvo {cand.get('ALVO') or '—'} · "
             f"{cand['K'][cand['DECIDIDO_POR']]['MOTIVO'][:160]} · ficheiro "
             f"know-how/vivo/candidatos/{cand['ID']}.json · decide: coordenador\n")
    os.makedirs(os.path.dirname(os.path.abspath(cfg.handoff)), exist_ok=True)
    with open(cfg.handoff, "a", encoding="utf-8", newline="\n") as f:
        f.write(linha)


def consolidar_candidato(cfg, cand):
    """Julga UM candidato (texto escrito por quem propoe + eventos) e grava o
    resultado com o motivo por K. Devolve o registo do candidato."""
    cand = dict(cand)
    for campo in ("TEXTO", "EVENTOS"):
        if campo not in cand:
            raise Recusa(f"candidato sem {campo}")
    if not cand.get("ID"):
        dia = _dt.date.today().strftime("%Y%m%d")
        cand["ID"] = None
        n = 1
        while os.path.exists(cfg.pasta("candidatos", f"KHC-{dia}-{n:02d}.json")):
            n += 1
        cand["ID"] = f"KHC-{dia}-{n:02d}"
    if not ID_CANDIDATO.match(cand["ID"]):
        raise Recusa(f"ID de candidato fora do formato (KH-C<n> ou KHC-AAAAMMDD-NN): {cand['ID']}")
    destino = cfg.pasta("candidatos", cand["ID"] + ".json")
    if os.path.exists(destino):
        raise Recusa(f"o candidato {cand['ID']} ja foi consolidado; nada reescrito")
    cand.setdefault("TITULO", (cand["TEXTO"] or "")[:80])
    cand["SCHEMA"] = "CANDIDATO_A_KNOW_HOW/1"
    ctx = {"cfg": cfg, "eventos": carregar_eventos(cfg)}
    k = avaliar(cand, ctx)
    resultado, por = decidir(k)
    cand.update({"K": k, "RESULTADO": resultado, "DECIDIDO_POR": por,
                 "CONSOLIDADO_EM": agora_iso(),
                 "REGRA": "K1–K8 (KNOW-HOW-VIVO-ARQUITETURA-v1 §5); promocao sem mao humana"})
    if resultado == "REFORCO":
        cand["ALVO"] = k["K5"]["ALVO"]
    elif resultado == "CONFLITO_KNOW_HOW":
        cand["ALVO"] = k["K6"].get("ALVO")
    elif resultado in ("RELACIONADO_A_AUTORIDADE", "CONFLITO_DE_AUTORIDADE"):
        cand["AUTORIDADE"] = k["K7"]["AUTORIDADE"]
        cand["ALVO"] = cand["AUTORIDADE"][0]["FONTE"]
    if resultado == "ACTIVE":
        eventos = ctx["eventos"]
        tags = set()
        for e in cand["EVENTOS"]:
            tags |= set((eventos.get(e) or {}).get("TAGS") or [])
        tags |= set(conceitos(cand["TITULO"] + " " + cand["TEXTO"]))
        kh = {"SCHEMA": "KNOW_HOW/1", "ID": None, "TITULO": cand["TITULO"],
              "TEXTO": cand["TEXTO"], "AREA": _area_do_candidato(cand, eventos),
              "TAGS": sorted(t for t in tags if t in TAGS_BASE) + sorted(t for t in tags if t not in TAGS_BASE),
              "ENTIDADES": _entidades(cand["TEXTO"]), "STATUS": "ACTIVE",
              "VALIDADE": "ATE_SER_SUBSTITUIDO (SUPERSEDED por DECISAO)",
              "ORIGEM": {"CANDIDATO": cand["ID"], "EVENTOS": cand["EVENTOS"],
                         "PROPOSTO_POR": cand.get("PROPOSTO_POR"),
                         "PROMOVIDO_EM": cand["CONSOLIDADO_EM"],
                         "PROMOVIDO_POR": "knowhow consolidar — K1–K8 todos PASS"},
              "RELACOES": [], "REFORCOS": []}
        cand["KH"] = _proximo_kh(cfg, kh)
    escrever_novo(destino, cand)
    if resultado == "REFORCO" and ID_KH.match(str(cand["ALVO"])):
        p = cfg.pasta("conhecimento", cand["ALVO"] + ".json")
        kh = ler(p)
        kh.setdefault("REFORCOS", []).append({"CANDIDATO": cand["ID"], "EVENTOS": cand["EVENTOS"],
                                              "TEXTO": cand["TEXTO"], "DATA": cand["CONSOLIDADO_EM"]})
        reescrever(p, kh)
    if resultado.startswith("CONFLITO_"):
        _handoff(cfg, cand)
    return cand


def consolidar(cfg, candidato=None):
    """Sem candidato: um CANDIDATO por evento que traga APRENDIZADO_PROPOSTO e ainda
    nao tenha candidato. Com candidato: julga-o. Depois reindexa."""
    feitos = []
    if candidato is not None:
        feitos.append(consolidar_candidato(cfg, candidato))
    else:
        citados = set()
        for c in carregar_candidatos(cfg).values():
            citados |= set(c.get("EVENTOS") or [])
        for eid, ev in carregar_eventos(cfg).items():
            if ev.get("APRENDIZADO_PROPOSTO") and eid not in citados:
                feitos.append(consolidar_candidato(cfg, {
                    "TITULO": ev["APRENDIZADO_PROPOSTO"][:80],
                    "TEXTO": ev["APRENDIZADO_PROPOSTO"], "EVENTOS": [eid],
                    "PROPOSTO_POR": ev.get("AGENTE_ORIGEM"),
                    "ORIGEM_DO_TEXTO": f"APRENDIZADO_PROPOSTO de {eid}"}))
    if feitos:
        indexar(cfg)
    return feitos


def substituir(cfg, kh_a, kh_b, evento_id):
    """SUPERSEDED so por DECISAO explicita (§4). Nunca apaga."""
    ev = carregar_eventos(cfg).get(evento_id)
    if not ev or ev.get("ESPECIE") != "DECISAO" or not _decisao_conta(ev):
        raise Recusa(f"{evento_id}: substituir exige um evento DECISAO do dono ou do "
                     "coordenador com referencia D-n")
    pa, pb = cfg.pasta("conhecimento", kh_a + ".json"), cfg.pasta("conhecimento", kh_b + ".json")
    if not (os.path.exists(pa) and os.path.exists(pb)):
        raise Recusa("os dois KH tem de existir")
    a, b = ler(pa), ler(pb)
    if a.get("STATUS") != "ACTIVE" or b.get("STATUS") != "ACTIVE":
        raise Recusa("so se substitui um KH ACTIVE por outro KH ACTIVE")
    quando = agora_iso()
    a.update({"STATUS": "SUPERSEDED", "SUBSTITUIDO_POR": kh_b,
              "SUBSTITUICAO": {"EVENTO": evento_id, "DATA": quando}})
    b.update({"SUBSTITUI": kh_a, "SUBSTITUICAO": {"EVENTO": evento_id, "DATA": quando}})
    reescrever(pa, a)
    reescrever(pb, b)
    indexar(cfg)
    return a, b


# ════════════════════════════════════════════════════════════════════════════
# §6 · INDICE — derivado e regeravel
# ════════════════════════════════════════════════════════════════════════════
def _rel(cfg, p):
    try:
        return os.path.relpath(p, cfg.raiz).replace("\\", "/")
    except ValueError:
        return p.replace("\\", "/")


def indexar(cfg):
    secoes = secoes_do_legado(cfg.legado) if os.path.exists(cfg.legado) else []
    reforcos = reforcos_do_legado(cfg)
    nome_legado = os.path.basename(cfg.legado)
    with open(cfg.legado, "rb") as f:
        sha_legado = hashlib.sha256(f.read()).hexdigest()
    lista = []
    for s in secoes:
        sup = RX_SUPERADO.search(s["proprio"])
        num = s["id"][len("LEG-§"):].split("@")[0]
        estado = RX_ESTADO_SUPERSEDED.search(s["proprio"])
        propria_sup = bool((sup and sup.group(2) != num) or estado)
        rel = sorted({f"LEG-§{x}" for x in RX_CITA.findall(s["texto"]) if x != num},
                     key=lambda x: [int(p) if p.isdigit() else 0 for p in re.split(r"[§.]", x)[1:]])
        tags = _tags_de(s["titulo"], s["proprio"])
        reg = {"ID": s["id"], "TITULO": s["titulo"], "TITULO_ORIGINAL": s["original"],
               "NIVEL": s["nivel"], "LINHA_INICIO": s["linha"], "LINHA_FIM": s["fim"],
               "SHA256": hashlib.sha256(s["texto"].encode("utf-8")).hexdigest(),
               "STATUS": "SUPERSEDED" if propria_sup else "ACTIVE",
               "TAGS": tags, "RELACOES": rel[:40]}
        if propria_sup:
            reg["SUPERSEDED_INFERIDO"] = True
            if sup and sup.group(2) != num:
                reg["SUPERSEDED_POR_INFERIDO"] = f"LEG-§{sup.group(2)}"
            reg["SUPERSEDED_TRECHO"] = (sup.group(0) if sup and sup.group(2) != num
                                        else estado.group(0))[:120]
        if s["id"] in reforcos:
            reg["REFORCOS"] = reforcos[s["id"]]
        lista.append(reg)
    doc_sec = {"SCHEMA": "LEGADO_SECOES/1", "FONTE": nome_legado, "FONTE_SHA256": sha_legado,
               "NOTA": ("DERIVADO de SINTONIA-EAME-KNOW-HOW.md (nunca alterado). Regerar com "
                        "`knowhow indexar`. REFORCOS vem de candidatos/; SUPERSEDED por regex "
                        "(«superado/corrigido pelo §X») e marcado SUPERSEDED_INFERIDO."),
               "TOTAL": len(lista), "TOTAL_TOPO": sum(1 for x in lista if x["NIVEL"] == 1),
               "SECOES": lista}
    reescrever(cfg.pasta("legado", "SECOES.json"), doc_sec)

    itens = []
    eventos = carregar_eventos(cfg)
    for reg, s in zip(lista, secoes):
        tags = set(reg["TAGS"])
        for r in reg.get("REFORCOS", []):
            for e in r["EVENTOS"]:
                tags |= set((eventos.get(e) or {}).get("TAGS") or [])
            tags |= set(conceitos((r.get("TITULO") or "") + " " + (r.get("TEXTO") or "")))
        tags = sorted(tags)
        itens.append({"ID": reg["ID"], "TITULO": reg["TITULO"], "AREA": _area_das_tags(tags),
                      "TAGS": tags, "ENTIDADES": _entidades(s["proprio"]),
                      "STATUS": reg["STATUS"], "VALIDADE": "LEGADO (vale ate ser superado)",
                      "ORIGEM": f"{nome_legado} (legado canonico)",
                      "RELACOES": reg["RELACOES"] + ([reg["SUPERSEDED_POR_INFERIDO"]]
                                                     if reg.get("SUPERSEDED_POR_INFERIDO") else []),
                      "CAMINHO": f"{nome_legado}:{reg['LINHA_INICIO']}-{reg['LINHA_FIM']}",
                      "REFORCOS": [{"CANDIDATO": r["CANDIDATO"], "TITULO": r["TITULO"],
                                    "EVENTOS": r["EVENTOS"]} for r in reg.get("REFORCOS", [])]})
    for k in carregar_conhecimento(cfg).values():
        if k.get("STATUS") not in ("ACTIVE", "SUPERSEDED"):
            continue
        rel = list(k.get("RELACOES") or [])
        for campo in ("SUBSTITUI", "SUBSTITUIDO_POR"):
            if k.get(campo):
                rel.append(f"{campo}:{k[campo]}")
        itens.append({"ID": k["ID"], "TITULO": k.get("TITULO"), "AREA": k.get("AREA"),
                      "TAGS": k.get("TAGS", []), "ENTIDADES": k.get("ENTIDADES", []),
                      "STATUS": k["STATUS"], "VALIDADE": k.get("VALIDADE"),
                      "ORIGEM": k.get("ORIGEM"), "RELACOES": rel,
                      "CAMINHO": f"know-how/vivo/conhecimento/{k['ID']}.json",
                      "REFORCOS": [{"CANDIDATO": r.get("CANDIDATO"), "EVENTOS": r.get("EVENTOS")}
                                   for r in k.get("REFORCOS", [])]})
    relacionados = [{"CANDIDATO": c["ID"], "TITULO": c.get("TITULO"), "TEXTO": c.get("TEXTO"),
                     "RESULTADO": c["RESULTADO"], "ALVO": c.get("ALVO"), "EVENTOS": c.get("EVENTOS"),
                     "AREA": _area_do_candidato(c, eventos),
                     "TAGS": sorted(set(conceitos((c.get("TITULO") or "") + " " + (c.get("TEXTO") or "")))),
                     "AUTORIDADE": [{"FONTE": x["FONTE"], "TEXTO": x["TEXTO"]}
                                    for x in c.get("AUTORIDADE") or []]}
                    for c in carregar_candidatos(cfg).values()
                    if c.get("RESULTADO") in ("RELACIONADO_A_AUTORIDADE",)]
    doc = {"SCHEMA": "KNOW_HOW_INDICE/1",
           "NOTA": "DERIVADO e regeravel (`knowhow indexar`): KH ACTIVE/SUPERSEDED + seccoes legadas.",
           "LEGADO_SHA256": sha_legado, "TOTAL": len(itens), "ITENS": itens,
           "RELACIONADOS_A_AUTORIDADE": relacionados}
    reescrever(cfg.pasta("INDICE.json"), doc)
    return doc


# ════════════════════════════════════════════════════════════════════════════
# §7 · PORTA DE RECUPERACAO
# ════════════════════════════════════════════════════════════════════════════
def _consulta(termos_txt):
    """(conceitos do vocabulario, termos livres). Os sinonimos do §3 expandem a
    frase em conceitos; um termo que ja virou conceito nao conta duas vezes."""
    n = re.sub(r"\s+", " ", re.sub(r"[/,;]+", " ", normalizar(termos_txt))).strip()
    conc = set(conceitos(n))
    for frase, exp in SINONIMOS.items():
        if re.search(r"\b" + re.escape(frase) + r"\b", n):
            for x in exp:
                if x in TAGS_BASE:
                    conc.add(x)
                # «published_at» ja e um dos termos do conceito «publicacao»
    livres = []
    for t in n.split():
        if conceitos(t) or any(re.search(r"\b" + re.escape(t) + r"\b", f) for f in SINONIMOS):
            continue
        livres += termos(t)
    return conc, set(livres)


# Na busca, a «data» inclui a data do fato: FACT_TIME e uma data. (So na busca:
# as TAGS continuam as do vocabulario.)
FAMILIA_NA_BUSCA = {"data": ("fact_time",)}


def _rx_da_chave(k):
    if k.startswith("#"):
        c = k[1:]
        return re.compile("|".join([_TERMOS_RE[c].pattern] +
                                   [_TERMOS_RE[f].pattern for f in FAMILIA_NA_BUSCA.get(c, ())]))
    return None


def _unidades_da_busca(cfg, indice):
    unid = [u for u in _unidades(cfg) if u["ID"] in indice]
    # o que foi RELACIONADO a uma autoridade tambem se recupera — aponta para a lei
    for r in ler(cfg.pasta("INDICE.json")).get("RELACIONADOS_A_AUTORIDADE", []):
        aut = r.get("AUTORIDADE") or []
        unid.append({"ID": r["CANDIDATO"], "TIPO": "RELACIONADO", "TITULO": r.get("TITULO") or "",
                     "TEXTO": (r.get("TEXTO") or "") + "\n" + "\n".join(a.get("TEXTO", "") for a in aut),
                     "STATUS": r["RESULTADO"], "TAGS": r.get("TAGS", []),
                     "ITEM": {"ID": r["CANDIDATO"], "TITULO": r.get("TITULO"), "STATUS": r["RESULTADO"],
                              "AREA": r.get("AREA"), "TAGS": r.get("TAGS", []),
                              "CAMINHO": " · ".join(a["FONTE"] for a in aut[:3]) or r.get("ALVO"),
                              "REFORCOS": [], "RELACOES": [a["FONTE"] for a in aut]}})
    return unid


def buscar(cfg, termos_txt, area=None, maximo=8):
    """So o relevante. Com dois ou mais conceitos/termos na pergunta, o item tem de
    os ter JUNTOS — na mesma linha (ou na vizinha), ou no titulo/TAGS curadas — e
    nao so espalhados pelo texto («publicacoes» na linha 6 e «datas» na 33 nao e o
    tema «data de publicacao»). Nota = BM25 simples (titulo x3, bonus de TAG);
    fica quem tiver pelo menos CORTE_RELATIVO_BUSCA da nota do primeiro.
    Nunca imprime o legado: so ID, titulo, caminho:linhas e um trecho curto."""
    conc, livres = _consulta(termos_txt)
    chaves = ["#" + c for c in sorted(conc)] + sorted(livres)
    if not chaves:
        return []
    exigidos = min(2, len(chaves))
    indice_p = cfg.pasta("INDICE.json")
    if not os.path.exists(indice_p):
        indexar(cfg)
    indice = {i["ID"]: i for i in ler(indice_p)["ITENS"]}
    rx = {k: _rx_da_chave(k) for k in chaves}

    def presentes(texto_norm, toks):
        out = set()
        for k in chaves:
            if (rx[k].search(texto_norm) if rx[k] else k in toks):
                out.add(k)
        return out

    linhas = []
    for u in _unidades_da_busca(cfg, indice):
        it = u.get("ITEM") or indice[u["ID"]]
        tit, txt = normalizar(u["TITULO"]), normalizar(u["TEXTO"])
        tt, ti = termos(u["TEXTO"]), termos(u["TITULO"])
        c = {}
        for k in chaves:
            if rx[k]:
                tags = it.get("TAGS", [])
                c[k] = (len(rx[k].findall(txt)), len(rx[k].findall(tit)),
                        k[1:] in tags or any(f in tags for f in FAMILIA_NA_BUSCA.get(k[1:], ())))
            else:
                c[k] = (tt.count(k), ti.count(k), False)
        # juntos: numa janela de 3 linhas, ou no titulo + TAGS
        por_linha = [presentes(l, set(termos(l))) for l in txt.split("\n")]
        janela = max([len(set().union(*por_linha[max(0, i - 1):i + 2]))
                      for i in range(len(por_linha))] or [0])
        curado = {k for k in chaves if c[k][1] or c[k][2]}
        linhas.append((u, it, c, max(1, len(tt)), janela, curado))
    n = len(linhas) or 1
    df = {k: sum(1 for x in linhas if x[2][k][0] or x[2][k][1]) for k in chaves}
    media = sum(x[3] for x in linhas) / n
    k1, b = 1.2, 0.75
    notas = []
    for u, it, c, L, janela, curado in linhas:
        if area and it.get("AREA") != area:
            continue
        if it.get("STATUS") not in ("ACTIVE", "SUPERSEDED", "RELACIONADO_A_AUTORIDADE"):
            continue
        if janela < exigidos and len(curado) < exigidos:
            continue
        casou = [k for k in chaves if c[k][0] or c[k][1] or c[k][2]]
        s = 0.0
        for k in casou:
            corpo, titulo, tag = c[k]
            idf = math.log(1 + (n - df[k] + 0.5) / (df[k] + 0.5))
            tf = corpo + 3 * titulo
            s += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * L / media))
            if tag:
                s += 1.5 * idf
        notas.append((s, u, it, casou))
    notas.sort(key=lambda x: (-x[0], x[1]["ID"]))
    if not notas:
        return []
    topo = notas[0][0]
    out = []
    for s, u, it, casou in [x for x in notas if x[0] >= CORTE_RELATIVO_BUSCA * topo][:maximo]:
        out.append({"ID": it["ID"], "TITULO": it["TITULO"], "STATUS": it["STATUS"],
                    "TIPO": u["TIPO"], "AREA": it.get("AREA"), "TAGS": it.get("TAGS"),
                    "CAMINHO": it["CAMINHO"], "NOTA": round(s, 3), "CASOU": casou,
                    "TRECHO": _trecho(u, rx), "REFORCOS": it.get("REFORCOS", []),
                    "RELACOES": it.get("RELACOES", [])[:8]})
    return out


def _trecho(u, rx, largura=220):
    melhor, nota = "", -1
    for linha in u["TEXTO"].split("\n"):
        l = linha.strip()
        if not l or l.startswith("#") or l.startswith("```"):
            continue
        nl = normalizar(l)
        tl = set(termos(l))
        k = sum(len(r.findall(nl)) if r else (1 if t in tl else 0) for t, r in rx.items())
        if k > nota:
            melhor, nota = l, k
    return melhor[:largura] + ("…" if len(melhor) > largura else "")


# ════════════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════════════
def _cfg(a):
    return Config(raiz=a.raiz, repo=a.repo, legado=a.legado, handoff=a.handoff,
                  decisoes=a.decisoes)


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("--raiz", help="worktree onde vive know-how/vivo/ (omissao: este repo)")
    comum.add_argument("--repo", help="repositorio das leis e do git (omissao: o deste programa)")
    comum.add_argument("--legado", help="SINTONIA-EAME-KNOW-HOW.md a ler")
    comum.add_argument("--handoff", help="onde escrever a linha de CONFLITO_*")
    comum.add_argument("--decisoes", help="DECISOES-DONO-*.md (fonte de autoridade)")
    p = argparse.ArgumentParser(prog="knowhow", description=__doc__.split("\n")[1])
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("registrar", parents=[comum], help="grava UM evento novo")
    r.add_argument("--arquivo")
    r.add_argument("--id")
    r.add_argument("--agente")
    r.add_argument("--data")
    r.add_argument("--area")
    r.add_argument("--tags", help="lista separada por virgulas")
    r.add_argument("--especie")
    r.add_argument("--fato")
    r.add_argument("--evidencia", action="append")
    r.add_argument("--confianca")
    r.add_argument("--status")
    r.add_argument("--aprendizado", help="APRENDIZADO_PROPOSTO (texto K8)")

    i = sub.add_parser("importar", parents=[comum], help="importa eventos JSONL tal como estao")
    i.add_argument("--jsonl", required=True)

    c = sub.add_parser("consolidar", parents=[comum], help="julga candidatos com K1–K8")
    c.add_argument("--candidato", help="JSON com TEXTO, EVENTOS, TITULO, ID, PROPOSTO_POR")

    sub.add_parser("indexar", parents=[comum], help="regera legado/SECOES.json e INDICE.json")

    b = sub.add_parser("buscar", parents=[comum], help="devolve so o conhecimento relevante")
    b.add_argument("termos")
    b.add_argument("--area", choices=AREAS)
    b.add_argument("--max", type=int, default=8)
    b.add_argument("--json", action="store_true")

    s = sub.add_parser("substituir", parents=[comum], help="KH-a SUPERSEDED por KH-b (DECISAO)")
    s.add_argument("kh_a")
    s.add_argument("--por", required=True)
    s.add_argument("--evento", required=True)

    a = p.parse_args(argv)
    cfg = _cfg(a)
    try:
        if a.cmd == "registrar":
            if a.arquivo:
                with open(a.arquivo, encoding="utf-8") as f:
                    ev = json.load(f)
            else:
                ev = {}
            for campo, v in (("ID", a.id), ("AGENTE_ORIGEM", a.agente), ("DATA", a.data),
                             ("AREA", a.area), ("ESPECIE", a.especie), ("FATO", a.fato),
                             ("CONFIANCA", a.confianca), ("STATUS", a.status),
                             ("APRENDIZADO_PROPOSTO", a.aprendizado)):
                if v is not None:
                    ev[campo] = v
            if a.tags is not None:
                ev["TAGS"] = [t.strip() for t in a.tags.split(",") if t.strip()]
            if a.evidencia:
                ev["EVIDENCIA"] = a.evidencia
            eid = registrar(cfg, ev)
            print(f"REGISTRADO {eid} → {_rel(cfg, cfg.pasta('eventos', eid + '.json'))}")
        elif a.cmd == "importar":
            for eid, como in importar(cfg, a.jsonl):
                print(f"{como:13} {eid}")
        elif a.cmd == "consolidar":
            cand = None
            if a.candidato:
                with open(a.candidato, encoding="utf-8") as f:
                    cand = json.load(f)
            feitos = consolidar(cfg, cand)
            if not feitos:
                print("nada a consolidar (nenhum evento novo com APRENDIZADO_PROPOSTO)")
            for c_ in feitos:
                print(f"{c_['ID']} «{c_.get('TITULO')}» → {c_['RESULTADO']}"
                      + (f" → {c_['KH']}" if c_.get("KH") else "")
                      + (f" (alvo {c_['ALVO']})" if c_.get("ALVO") else ""))
                for kk, vv in c_["K"].items():
                    print(f"   {kk} {vv['VEREDITO']:9} {vv['MOTIVO'][:170]}")
        elif a.cmd == "indexar":
            d = indexar(cfg)
            sec = ler(cfg.pasta("legado", "SECOES.json"))
            print(f"INDEXADO {d['TOTAL']} itens · legado {sec['TOTAL']} seccoes "
                  f"({sec['TOTAL_TOPO']} de topo) · KH {d['TOTAL'] - sec['TOTAL']}")
        elif a.cmd == "buscar":
            res = buscar(cfg, a.termos, area=a.area, maximo=a.max)
            if a.json:
                print(json.dumps(res, ensure_ascii=False, indent=1))
            else:
                conc, tks = _consulta(a.termos)
                print(f"{len(res)} item(ns) para «{a.termos}» · conceitos: "
                      f"{', '.join(sorted(conc)) or '—'} · termos: {', '.join(sorted(tks)) or '—'}")
                for n_, x in enumerate(res, 1):
                    print(f"{n_}. {x['ID']} · {x['TITULO'][:100]} · {x['STATUS']} · {x['CAMINHO']}"
                          + ("  (candidato ligado a uma lei: a regra vale pela lei)"
                             if x["TIPO"] == "RELACIONADO" else ""))
                    for rf in x.get("REFORCOS") or []:
                        print(f"   reforço: {rf.get('CANDIDATO')} «{rf.get('TITULO') or ''}» "
                              f"({', '.join(rf.get('EVENTOS') or [])})")
                    if x["TRECHO"]:
                        print(f"   «{x['TRECHO']}»")
        elif a.cmd == "substituir":
            substituir(cfg, a.kh_a, a.por, a.evento)
            print(f"{a.kh_a} SUPERSEDED → SUBSTITUIDO_POR {a.por} (evento {a.evento})")
    except Recusa as e:
        print(f"RECUSADO: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
