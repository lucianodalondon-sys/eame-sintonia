#!/usr/bin/env python3
"""
test_portoes.py — checa mecanicamente os portoes que a missao exige.

Nao substitui o red team humano/agente: cobre so o que da para verificar por
programa, que e justamente onde um humano cansa e deixa passar.
"""
import json, os, re, subprocess, sys
from collections import Counter

R = []
def ok(g, d=""):  R.append({"GATE": g, "STATE": "PASS", "DETALHE": d}); print(f"  PASS  {g}  {d}")
def fail(g, d):   R.append({"GATE": g, "STATE": "FAIL", "DETALHE": d}); print(f"  FAIL  {g}  {d}")

PAY = json.load(open("v1/dados/CASCO-PAYLOAD.json", encoding="utf-8"))
OBJ = PAY["objects"]
HTML = open("v1/casco/label-intelligence.html", encoding="utf-8").read()
REGRAS = open("v1/inteligencia/REGRAS.md", encoding="utf-8").read()
JS = open("v1/casco/app.js", encoding="utf-8").read()

# A lista de referencia vem do proprio casco, para os dois nunca divergirem.
UNK = set(re.findall(r"'(NOT_[A-Z_]+|UNKNOWN)'", JS.split("const isUnk")[0]))

# --- 1. nenhuma ACTION emitida
acoes = {o["ACTION"] for o in OBJ}
if acoes == {"NOT_EMITTED_BY_THIS_TOOL"}:
    ok("UNPROVED_ACTION_ROUTING", f"nenhum objeto emite ACTION ({len(OBJ)} objetos)")
else:
    fail("UNPROVED_ACTION_ROUTING", f"ACTION com valores {acoes}")

# --- 2. todo roteamento aponta uma regra que EXISTE em REGRAS.md
ids = set(re.findall(r"`(C-\d\d|R-\d\d|N-\d\d|T-\d\d|G-\d\d)`", REGRAS))
faltando, semrule = set(), 0
for o in OBJ:
    for r in o["CAPABILITY_ROUTING"]:
        if not r.get("RULE_ID"):
            semrule += 1
        elif r["RULE_ID"] not in ids:
            faltando.add(r["RULE_ID"])
if semrule == 0 and not faltando:
    ok("ROUTING_RULE_EXISTS", f"todo roteamento aponta uma das {len(ids)} regras declaradas")
else:
    fail("ROUTING_RULE_EXISTS", f"{semrule} sem regra; ids inexistentes: {faltando}")

# --- 3. implicacao de negocio nunca afirmada
bi = {o["POTENTIAL_BUSINESS_IMPLICATION"] for o in OBJ}
ok("BUSINESS_IMPLICATION_GATED", f"todos NOT_PROVED") if bi == {"NOT_PROVED"} \
    else fail("BUSINESS_IMPLICATION_GATED", f"valores {bi}")

# --- 4. PHI nunca emitido
if not any(o["OBJECT_TYPE"] == "PHI_CHANGE" for o in OBJ):
    ok("PHI_GATE_G02", "nenhum PHI_CHANGE emitido, coerente com PHI_PROVED = 0")
else:
    fail("PHI_GATE_G02", "PHI_CHANGE emitido sem PHI provado")

# --- 5. RTV nunca RELEVANT
rtv = Counter(r["ROUTING_STATE"] for o in OBJ for r in o["CAPABILITY_ROUTING"]
              if r["CAPABILITY_ID"] == "COMMERCIAL_RTV")
ok("COMMERCIAL_GATE_G01", f"RTV sempre {dict(rtv)}") if set(rtv) == {"NOT_RELEVANT"} \
    else fail("COMMERCIAL_GATE_G01", f"RTV com estados {dict(rtv)}")

# --- 6. toda afirmacao material tem rota para fonte
sem = []
for o in OBJ:
    tem_doc = any(str(o.get(k, "")) not in UNK and o.get(k) for k in
                  ("SOURCE_DOCUMENT_AFTER", "SOURCE_DOCUMENT_BEFORE"))
    tem_loc = str(o.get("EVIDENCE_LOCATION", "")) not in UNK
    tem_url = bool(o.get("SOURCE_URL"))
    if not (tem_doc and tem_loc and tem_url):
        sem.append({"id": o["INTELLIGENCE_OBJECT_ID"], "tipo": o["OBJECT_TYPE"],
                    "doc": tem_doc, "loc": tem_loc, "url": tem_url})
pct = round(100.0 * (len(OBJ) - len(sem)) / len(OBJ), 1)
ok("MATERIAL_CLAIMS_WITH_EVIDENCE", f"{pct}% ({len(OBJ)-len(sem)}/{len(OBJ)})") if not sem \
    else fail("MATERIAL_CLAIMS_WITH_EVIDENCE", f"{pct}% — {len(sem)} sem rota completa: {sem[:3]}")

# --- 7. nenhum "-" / "N/A" significando desconhecido no HTML renderizado
suspeitos = re.findall(r"<td[^>]*>\s*(?:-|N/A|n/a|none|null|undefined)\s*</td>", HTML)
ok("UNKNOWN_HIDDEN_OR_FILLED", "nenhuma celula com traco/N-A no template") if not suspeitos \
    else fail("UNKNOWN_HIDDEN_OR_FILLED", f"{len(suspeitos)} celulas suspeitas")

# --- 8. o token de ignorancia e renderizado com o proprio nome
if 'class="unknown"' in HTML and "NOT_KNOWN" in HTML:
    ok("UNKNOWN_VISIBLE", "tokens de ignorancia renderizados com nome proprio")
else:
    fail("UNKNOWN_VISIBLE", "nao encontrei o estilo/token de desconhecido")

# --- 9. expiry nunca vira withdrawal
proibido = ["stop selling", "pare de vender", "retirar do mercado", "withdrawn",
            "queda de demanda", "demand drop", "stock risk", "risco de estoque",
            "reduza estoque", "fora do mercado"]

# UMA excecao, declarada e literal. REGRAS.md secao 5 obriga a glosa
#   ACT_NOW aqui significa "olhe hoje", nunca "pare de vender"
# e sem ela a unica frase imperativa em ingles do produto viaja sem contrato.
# Proibir a frase ate dentro da propria negacao dela deixaria a ferramenta sem
# poder dizer o que ela NAO esta dizendo. A excecao e so esta: a glosa e
# recortada do HTML e o resto do documento continua sob a regra inteira. Se a
# glosa sumir, isto FALHA — nao passa por omissao.
GLOSA = ("aqui significa\n  &ldquo;olhe hoje&rdquo;, nunca &ldquo;pare de vender&rdquo;")
GLOSA_RENDER = 'aqui significa\n  “olhe hoje”, nunca “pare de vender”'
corpo = HTML
achou_glosa = 0
for g in (GLOSA, GLOSA_RENDER):
    achou_glosa += corpo.count(g)
    corpo = corpo.replace(g, " [GLOSA_ACT_NOW] ")
if not achou_glosa:
    fail("EXPIRY_AS_WITHDRAWAL", "a glosa obrigatoria de ACT_NOW ('olhe hoje', nunca "
                                 "'pare de vender') nao esta na interface")
    proibido = []
achou = [p for p in proibido if p in corpo.lower()]
ok("EXPIRY_AS_WITHDRAWAL",
   f"nenhuma frase de retirada/demanda/estoque fora da glosa obrigatoria "
   f"({achou_glosa} ocorrencia(s) da glosa)") if achou_glosa and not achou \
    else fail("EXPIRY_AS_WITHDRAWAL", f"frases encontradas: {achou}")

# --- 10. parser failure nunca apresentado como ausencia regulatoria
if "PARSER_FAILURE != REGULATORY_ABSENCE" in HTML:
    ok("PARSER_FAILURE_AS_ABSENCE", "a lei aparece na interface onde o estado de leitura e mostrado")
else:
    fail("PARSER_FAILURE_AS_ABSENCE", "a lei nao esta visivel na interface")

# --- 11. isolamento: nada fora de v1/ e pilot-label-intelligence/
dif = subprocess.run(["git", "diff", "--name-only", "df3a4fd..HEAD"],
                     capture_output=True, text=True).stdout.split()
fora = [f for f in dif if not (f.startswith("v1/") or f.startswith("pilot-label-intelligence/"))]
ok("ISOLATION", f"{len(dif)} arquivos, todos dentro de v1/ e pilot/") if not fora \
    else fail("ISOLATION", f"arquivos fora do escopo: {fora}")

# --- 12. canonical intocada POR ESTA MISSAO
#
# A versao anterior deste portao fixava o head de canonical numa constante
# (bdb57cf) e passava enquanto ele nao mudasse. Ele mudou: canonical avancou
# para 10af4a7 com tres commits que NAO sao meus — outra sessao trabalhou nela
# enquanto esta missao rodava. O portao antigo teria transformado o trabalho
# legitimo de outra pessoa num alarme desta missao, e um portao que dispara por
# um fato que nao e sobre mim nao mede o que promete medir.
#
# O que esta missao pode afirmar e so isto: nenhum commit meu esta em canonical.
# E o que este portao passa a medir, com git, e nao com uma constante.
ls = subprocess.run(["git", "ls-remote", "origin", "refs/heads/sintonia/canonical"],
                    capture_output=True, text=True).stdout.split()
head_canon = ls[0] if ls else "NOT_KNOWN"
subprocess.run(["git", "fetch", "-q", "origin",
                "refs/heads/sintonia/canonical:refs/remotes/origin/sintonia/canonical"],
               capture_output=True, text=True)
meus = subprocess.run(["git", "log", "--format=%H", "df3a4fd..HEAD"],
                      capture_output=True, text=True).stdout.split()
alcancaveis = subprocess.run(
    ["git", "rev-list", "origin/sintonia/canonical"], capture_output=True, text=True).stdout.split()
vazou = sorted(set(meus) & set(alcancaveis))
if vazou:
    fail("CANONICAL_TOUCHED", f"{len(vazou)} commit(s) desta missao estao em canonical: "
                              f"{[c[:8] for c in vazou]}")
else:
    ok("CANONICAL_TOUCHED",
       f"nenhum dos {len(meus)} commits desta missao esta em canonical "
       f"(head de canonical agora: {head_canon[:8]}, movido por outra sessao)")

# --- 12b. o reuso continua ancorado no ARQUIVO, nao no branch
#
# canonical mover nao pode mudar o que esta ferramenta leu. A ancora do reuso e
# o sha256 do arquivo de pares, gravado em EXCLUSAO.json e conferido pelo
# payload a cada build.
_exc = json.load(open("v1/dados/EXCLUSAO.json", encoding="utf-8"))
_cam = _exc.get("PAIRS_PATH", "")
if os.path.exists(_cam):
    import hashlib
    with open(_cam, "rb") as _fh:
        _s = hashlib.sha256(_fh.read()).hexdigest()
    ok("REUSE_ANCHORED_ON_FILE_HASH",
       f"arquivo de pares confere ({_s[:12]}), {_exc['PAIRS_COUNT']} pares") \
        if _s == _exc.get("PAIRS_SHA256") \
        else fail("REUSE_ANCHORED_ON_FILE_HASH",
                  f"o arquivo de pares mudou: {_exc.get('PAIRS_SHA256','?')[:12]} -> {_s[:12]}")
else:
    fail("REUSE_ANCHORED_ON_FILE_HASH", f"arquivo de pares nao esta em {_cam}")

# --- 13. cobertura nunca publicada como numero unico
cov = PAY["coverage"]
ok("COVERAGE_NOT_SINGLE_NUMBER", f"{len(cov)} coberturas separadas") if len(cov) >= 6 \
    else fail("COVERAGE_NOT_SINGLE_NUMBER", f"so {len(cov)} coberturas")

# --- 14. o filtro de ruido passa
r = subprocess.run(["python3", "v1/testes/test_ruido.py"], capture_output=True, text=True)
ok("FALSE_CHANGE_NOISE_TEST", "11 testes adversariais passam") if r.returncode == 0 \
    else fail("FALSE_CHANGE_NOISE_TEST", "a suite de ruido falhou")

# --- 15. EXCLUSAO NAO E PERMISSAO (R-10)
exc = json.load(open("v1/dados/EXCLUSAO.json", encoding="utf-8"))
publicados = {(p["reg"], u["crop"], u["target"]) for p in PAY["products"] for u in p["uses"]}
vazou = [(w["REGISTRATION_ID"], w["CROP"], w["TARGET"]) for w in exc["RETIRADOS"]
         if (w["REGISTRATION_ID"], w["CROP"], w["TARGET"]) in publicados]
sem_prova = [w for w in exc["RETIRADOS"] if not w.get("EXCLUSION_TEXT")]
if vazou:
    fail("EXCLUSION_IS_NOT_PERMISSION", f"cultura retirada ainda publicada como uso: {vazou}")
elif sem_prova:
    fail("EXCLUSION_IS_NOT_PERMISSION", f"{len(sem_prova)} retiradas sem a frase do rotulo")
else:
    ok("EXCLUSION_IS_NOT_PERMISSION",
       f'{exc["PARES_RETIRADOS"]} par(es) retirado(s), cada um com a frase literal do rotulo; '
       f'{exc["LABELS_WITH_CROP_SCOPE_EXCLUSION"]} rotulos tem janela de exclusao '
       f'que fala de cultura (de {exc["LABELS_WITH_ANY_EXCLUSION_MARKER"]} com algum marcador)')

# --- 15b. todo token NOT_* emitido tem de ser reconhecido como ignorancia
#
# A lista UNK do casco era uma enumeracao e ficou para tras: quando a coleta
# passou a emitir NOT_COLLECTED, val() tratou o token como valor comum e a ficha
# publicou <a href="NOT_COLLECTED">abrir no Ministero</a>. Agora a lista e
# conferida contra o que o payload realmente emite.
def tokens_do_payload(o, achados):
    if isinstance(o, dict):
        for v in o.values():
            tokens_do_payload(v, achados)
    elif isinstance(o, list):
        for v in o:
            tokens_do_payload(v, achados)
    elif isinstance(o, str) and re.fullmatch(r"NOT_[A-Z_]+", o):
        achados.add(o)
    return achados

emitidos = tokens_do_payload(PAY, set())
# NOT_RELEVANT nao e ignorancia: e a decisao da regra C-05. Declarado no casco
# em DECISOES, e repetido aqui de proposito — os dois lados tem de concordar.
emitidos -= set(re.findall(r"'(NOT_[A-Z_]+)'", JS.split("const isUnk")[0].split("const DECISOES")[-1]))
declarados = set(re.findall(r"'(NOT_[A-Z_]+)'", JS.split("const isUnk")[0]))
orfaos = sorted(emitidos - declarados)
ok("IGNORANCE_TOKENS_DECLARED",
   f"{len(emitidos)} tokens NOT_* emitidos, todos na lista do casco") if not orfaos \
    else fail("IGNORANCE_TOKENS_DECLARED", f"tokens emitidos e nao declarados: {orfaos}")

# --- 15c. nenhum link no HTML aponta para um token de ignorancia
maus = re.findall(r'href="(NOT_[A-Z_]+)"', HTML)
ok("NO_LINK_TO_IGNORANCE_TOKEN", "nenhum href para token de ignorancia") if not maus \
    else fail("NO_LINK_TO_IGNORANCE_TOKEN", f"{len(maus)} link(s) para {set(maus)}")

# --- 15d. TODA CONSTANTE QUE SE DIZ MEDIDA E RECONTADA AQUI.
#
# Achado da rodada 4, e desta vez o defeito era do proprio autor das regras:
# a lista SUCESSAO de R-10b declarava "coltura in successione" com 8
# ocorrencias, e o marcador ocorre ZERO vezes no acervo — o numero tinha sido
# copiado do plural. E RESTRICOES_FORA_DA_TABELA declarava "non superare" em 50
# rotulos, que e a contagem do padrao SIMPLIFICADO; com o `(?!le seguenti dosi
# per ettaro)` que o codigo realmente usa, sao 45.
#
# Um comentario que diz "medido" e nao foi conferido e PIOR do que nenhum
# comentario: ele desliga a desconfianca de quem le. Entao nenhuma dessas
# constantes volta a envelhecer em silencio — este portao reconta todas contra
# os 163 rotulos a cada execucao.
import unicodedata as _ud


def _sa(t):
    t = _ud.normalize("NFD", str(t or ""))
    return "".join(c for c in t if _ud.category(c) != "Mn").lower()


def _textos(cache, sufixo=".txt"):
    out = {}
    if os.path.isdir(cache):
        for f in sorted(os.listdir(cache)):
            if f.endswith(sufixo) and f.count(".") == 1:
                out[f[: -len(sufixo)]] = re.sub(
                    r"\s+", " ", _sa(open(os.path.join(cache, f), encoding="utf-8",
                                          errors="replace").read()))
    return out


_div = []
_conferidas = 0
sys.path.insert(0, "v1/coleta")
sys.path.insert(0, "v1/inteligencia")
try:
    from exclusao import SUCESSAO
    _fl = _textos("/tmp/leiturafluxo")
    if not _fl:
        _div.append("SUCESSAO: sem texto em ordem de leitura para recontar")
    for _m, _n in SUCESSAO:
        _c = sum(t.count(_m) for t in _fl.values())
        _conferidas += 1
        if _c != _n:
            _div.append(f"SUCESSAO {_m!r}: declarado {_n}, medido {_c}")
except Exception as _e:
    _div.append(f"SUCESSAO nao pode ser recontada: {_e}")
try:
    # Marcadores de exclusao MEDIDOS E NAO USADOS. Duas afirmacoes, e as duas sao
    # reconferidas: em quantos rotulos cada forma ocorre, e que nenhuma das
    # janelas que elas abrem nomeia uma cultura publicada como uso autorizado.
    # A segunda e a que importa: se um rotulo novo trouxer "non applicare su
    # pomodoro", este portao cai e alguem tem de decidir se o marcador entra.
    from exclusao import (MARCADORES_CANDIDATOS_NAO_USADOS, RX_FIM, JANELA_MAX,
                          sem_acento as _sa_exc)
    _pares_j = json.load(open("v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json",
                              encoding="utf-8"))["PAIRS"]
    _regs_j = {x["REGISTRATION_ID"] for x in _pares_j}
    _tx = {}
    for _r in sorted(_regs_j):
        _f = os.path.join("/tmp/exclusao-txt", f"{_r}.txt")
        if os.path.exists(_f):
            _tx[_r] = _sa_exc(open(_f, encoding="utf-8", errors="replace").read())
    _pub = {p_["reg"]: sorted({u["crop"] for u in p_.get("uses", [])})
            for p_ in json.load(open("v1/dados/CASCO-PAYLOAD.json",
                                     encoding="utf-8"))["products"]}
    if not _tx:
        _div.append("MARCADORES NAO USADOS: sem texto em /tmp/exclusao-txt para recontar")
    _nomeia = 0
    for _m, _n in MARCADORES_CANDIDATOS_NAO_USADOS:
        _rx = re.compile(r"\b" + re.escape(_m) + r"\b")
        _rr = [_r for _r, _t in _tx.items() if _rx.search(_t)]
        _conferidas += 1
        if len(_rr) != _n:
            _div.append(f"MARCADOR NAO USADO {_m!r}: declarado {_n} rotulos, medido {len(_rr)}")
        for _r in _rr:
            for _mm in _rx.finditer(_tx[_r]):
                _j = _mm.end()
                _fim = RX_FIM.search(_tx[_r], _j)
                _jan = re.sub(r"\s+", " ", _tx[_r][_mm.start():min(
                    _fim.start() if _fim else len(_tx[_r]), _j + JANELA_MAX)])
                for _c in _pub.get(_r, []):
                    _ps = [q for q in _sa_exc(_c).split("_") if len(q) >= 4]
                    if _ps and all(re.search(r"\b" + re.escape(q), _jan) for q in _ps):
                        _nomeia += 1
                        _div.append(f"MARCADOR NAO USADO {_m!r} em {_r}: a janela nomeia "
                                    f"{_c}, que a ferramenta publica como uso autorizado")
                        break
    _conferidas += 1
except Exception as _e:
    _div.append(f"MARCADORES NAO USADOS nao pode ser recontado: {_e}")
try:
    from teto_dose import RESTRICOES_FORA_DA_TABELA
    _lay = _textos("/tmp/tetotxt")
    if not _lay:
        _div.append("RESTRICOES: sem texto -layout para recontar")
    for _p, _nome, _n in RESTRICOES_FORA_DA_TABELA:
        _c = sum(1 for t in _lay.values() if re.search(_p, t, re.I))
        _conferidas += 1
        if _c != _n:
            _div.append(f"RESTRICAO {_nome!r}: declarado {_n}, medido {_c}")
except Exception as _e:
    _div.append(f"RESTRICOES nao pode ser recontada: {_e}")

ok("MEASURED_CONSTANTS_ARE_MEASURED",
   f"{_conferidas} constantes que se dizem medidas foram recontadas contra o texto dos "
   f"rotulos em disco (163 PDFs; 128 deles no acervo de pares)") \
    if not _div else fail("MEASURED_CONSTANTS_ARE_MEASURED", " | ".join(_div))

# --- 15e. o NOME DA CULTURA publicado e uma palavra do documento
#
# Recontagem INDEPENDENTE: este portao nao le CULTURA-NOMEADA.json nem confia no
# veredito de R-21. Ele reabre o texto dos 163 PDFs, reconstroi as raizes e faz
# as duas perguntas por conta propria:
#
#   (a) todo par que R-14 ABSOLVEU tem a raiz do nome da cultura em alguma
#       palavra do documento? Ate a rodada 4 a resposta era nao para 13 pares,
#       absolvidos pela raiz do TITULO DO GRUPO ("ORTICOLE (... FAGIOLINO ...)",
#       "Grano tenero e duro") — a geometria provava que o titulo e o alvo
#       dividem uma celula, nao que a cultura estava no grupo;
#   (b) todo uso publicado com selo FATO tem o nome da cultura escrito?
#
# E um CONTROLE NEGATIVO fecha o portao: 018270 FAGIOLO tem de continuar sendo
# pego. Portao que so sabe dizer "passou" nao mede nada.
_cn = []
_conf_cn = 0
try:
    _cache = "/tmp/nomecache"

    def _rad(w):
        w = re.sub(r"[^a-z]", "", _sa(w))
        if len(w) >= 5:
            r_ = re.sub(r"h?[aeiou]$", "", w)
            if len(r_) >= 4:
                return r_
        return w

    _doc = {}
    if os.path.isdir(_cache):
        for _f in sorted(os.listdir(_cache)):
            if _f.endswith(".txt") and _f.count(".") == 2:
                _reg = _f.split(".")[0]
                _t = _sa(open(os.path.join(_cache, _f), encoding="utf-8",
                              errors="replace").read())
                _doc.setdefault(_reg, set()).update(_rad(w) for w in re.findall(r"[a-z]+", _t))
    if not _doc:
        _cn.append("sem texto em /tmp/nomecache para recontar o nome da cultura")
    else:
        _pv = json.load(open("v1/dados/PARES-FIOS-CHECK.json", encoding="utf-8"))["VERDICT"]
        _pares = json.load(open("v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json",
                                encoding="utf-8"))["PAIRS"]
        _ord, _pego = {}, set()
        for _x in _pares:
            _reg = _x["REGISTRATION_ID"]
            _i = _ord[_reg] = _ord.get(_reg, -1) + 1
            _raizes = _doc.get(_reg)
            if _raizes is None:
                continue
            _partes = [q for q in (_sa(t) for t in str(_x["CROP"]).split("_")) if len(q) >= 4]
            _tem = bool(_partes) and all(_rad(q) in _raizes for q in _partes)
            if not _tem:
                _pego.add(f"{_reg}#{_i}")
            _conf_cn += 1
            if not _tem and _pv.get(f"{_reg}#{_i}") == "PAIR_CONSISTENT_WITH_RULES":
                _cn.append(f"R-14 absolveu {_reg}#{_i} ({_x['CROP']}) e o documento nao "
                           f"escreve esse nome")
        if "018270#10" not in _pego:
            _cn.append("CONTROLE NEGATIVO FALHOU: 018270#10 (FAGIOLO, a etichetta escreve "
                       "FAGIOLINO) nao foi pego pela recontagem — o portao parou de medir")
        _pl = json.load(open("v1/dados/CASCO-PAYLOAD.json", encoding="utf-8"))
        for _p in _pl["products"]:
            for _u in _p.get("uses", []):
                if _u.get("fact") and _u.get("crop_name") == "CROP_NAME_NOT_IN_LABEL":
                    _cn.append(f"{_p['reg']} {_u['crop']}x{_u['target']} tem selo FATO com "
                               f"nome de cultura ausente do rotulo")
except Exception as _e:
    _cn.append(f"nome da cultura nao pode ser reconferido: {_e}")

ok("CROP_NAME_IS_THE_LABEL_WORD",
   f"{_conf_cn} pares reconferidos contra o texto dos PDFs; nenhuma absolvicao de R-14 e "
   f"nenhum selo FATO se apoia em nome de cultura que o documento nao escreve "
   f"(controle negativo 018270 FAGIOLO pego)") \
    if not _cn else fail("CROP_NAME_IS_THE_LABEL_WORD", " | ".join(_cn[:6]))

# --- 15f. o teste do alvo da linha de dose nao tem buraco silencioso
#
# R-13 tinha um portao `len(alvo) < 8` sem motivo escrito, e ele calava 71
# linhas de dose como TARGET_TEXT_NOT_CHECKED. NOT_CHECKED e um token honesto
# quando o teste nao se aplica; nao e honesto quando o teste foi desligado por
# um numero que ninguem justificou. Este portao reconta as linhas caladas.
_ac = []
try:
    _als = json.load(open("v1/dados/ALVO-LITERAL.json", encoding="utf-8"))
    _dos = json.load(open("pilot-label-intelligence/demo/IT-DOSES.json", encoding="utf-8"))
    _semtexto = {l["REGISTRATION_ID"] for l in _dos["LABELS"]
                 if not os.path.exists(f"pilot-label-intelligence/labels/pdf/"
                                       f"{l['REGISTRATION_ID']}.pdf")}
    _mudo = [k for k, v in _als["VERDICT"].items()
             if v == "TARGET_TEXT_NOT_CHECKED" and k.split("#")[0] not in _semtexto]
    if _mudo:
        _cn_ex = ", ".join(_mudo[:5])
        _ac.append(f"{len(_mudo)} linhas de dose com PDF em disco saem NOT_CHECKED ({_cn_ex})")
    if _als.get("ROWS_FOUND_LITERALLY", 0) + _als.get("ROWS_NOT_FOUND_LITERALLY", 0) \
            != len(_als["VERDICT"]) - _als.get("ROWS_NOT_CHECKED", 0):
        _ac.append("as contagens de R-13 nao fecham com o proprio VERDICT")
    if _als.get("ROWS_NOT_FOUND_LITERALLY", 0) == 0:
        _ac.append("R-13 parou de reprovar qualquer linha — o teste virou carimbo")
except Exception as _e:
    _ac.append(f"R-13 nao pode ser reconferido: {_e}")

ok("TARGET_TEXT_TEST_HAS_NO_SILENT_HOLE",
   f"todas as linhas de dose com PDF em disco foram testadas por R-13; "
   f"{json.load(open('v1/dados/ALVO-LITERAL.json', encoding='utf-8'))['ROWS_NOT_FOUND_LITERALLY']} "
   f"continuam reprovadas, entao o teste ainda discrimina") \
    if not _ac else fail("TARGET_TEXT_TEST_HAS_NO_SILENT_HOLE", " | ".join(_ac))

# --- 15g. nenhuma prova de par veio de uma celula que o documento nao desenhou
#
# `celula()` fecha o lado que falta com a borda da pagina quando nao ha fio
# acima (ou abaixo) da palavra. Isso e escolha do codigo, nao traco do
# documento, e chega a fabricar "celulas" de 479 pt sobre prosa (77% da folha)
# que passam por celula_coerente. Recusar celula aberta apagaria 14 absolvicoes
# VERDADEIRAS — tabela sem borda de topo existe, e as 14 foram conferidas alvo
# a alvo contra o texto. Entao em vez de recusar, vigia-se.
#
# O limiar nao e inventado: e a MAIOR banda de uma celula FECHADA que provou um
# par neste mesmo acervo. Uma celula aberta maior que qualquer celula que o
# documento desenhou nao e uma celula.
_oc = []
try:
    _pf = json.load(open("v1/dados/PARES-FIOS-CHECK.json", encoding="utf-8"))
    _tetoc = _pf.get("CLOSED_CELL_MAX_BAND_PT", 0)
    _gordas = [w for w in _pf.get("OPEN_CELL_LIST", []) if w["BAND_PT"] > _tetoc]
    if _gordas:
        _oc.append(f"{len(_gordas)} absolvicao(oes) com celula de lado nao desenhado maior que "
                   f"a maior celula fechada do acervo ({_tetoc} pt): "
                   + ", ".join(f"{w['KEY']} {w['CROP']}x{w['TARGET']} {w['BAND_PT']}pt"
                               for w in _gordas[:4]))
    if _tetoc <= 0:
        _oc.append("CLOSED_CELL_MAX_BAND_PT nao foi medido: o portao nao tem contra o que comparar")
except Exception as _e:
    _oc.append(f"celulas abertas nao puderam ser reconferidas: {_e}")

ok("OPEN_CELL_DID_NOT_PROVE_A_PAIR",
   f"{json.load(open('v1/dados/PARES-FIOS-CHECK.json', encoding='utf-8'))['OPEN_CELL_ABSOLUTIONS']} "
   f"absolvicoes vieram de celula com um lado nao desenhado, a maior com "
   f"{json.load(open('v1/dados/PARES-FIOS-CHECK.json', encoding='utf-8'))['OPEN_CELL_MAX_BAND_PT']} pt "
   f"— abaixo da maior celula FECHADA do acervo "
   f"({json.load(open('v1/dados/PARES-FIOS-CHECK.json', encoding='utf-8'))['CLOSED_CELL_MAX_BAND_PT']} pt)") \
    if not _oc else fail("OPEN_CELL_DID_NOT_PROVE_A_PAIR", " | ".join(_oc))

# --- 15h. o arquivo de vereditos nao pode discordar de si mesmo
#
# A lente G leu PARES-FIOS-CHECK.json numa janela em que o COUNTS do cabecalho
# contava 13 pares numa categoria e o VERDICT os listava noutra. Foi corrida de
# escrita durante esta missao e nao defeito de regra — mas um artefato de dados
# que afirma dois numeros diferentes sobre si mesmo e indefensavel, e a unica
# forma de nunca mais precisar dessa explicacao e recontar.
_sc = []
try:
    for _arq, _cn in (("v1/dados/PARES-FIOS-CHECK.json", "COUNTS"),
                      ("v1/dados/ALVO-NOMEADO.json", "COUNTS"),
                      ("v1/dados/CULTURA-NOMEADA.json", "COUNTS")):
        _d = json.load(open(_arq, encoding="utf-8"))
        _real = Counter(_d["VERDICT"].values())
        if dict(_real) != dict(_d[_cn]):
            _so = {k: (_d[_cn].get(k), _real.get(k)) for k in set(_d[_cn]) | set(_real)
                   if _d[_cn].get(k) != _real.get(k)}
            _sc.append(f"{os.path.basename(_arq)}: cabecalho diz {_so} (declarado, medido)")
except Exception as _e:
    _sc.append(f"cabecalhos nao puderam ser reconferidos: {_e}")

ok("COUNTS_MATCH_THEIR_OWN_VERDICTS",
   "os tres arquivos de veredito contam exatamente o que listam") \
    if not _sc else fail("COUNTS_MATCH_THEIR_OWN_VERDICTS", " | ".join(_sc))

# --- 15i. modulo que chama a geometria compartilhada ainda casa com a assinatura
#
# Esta missao QUEBROU R-15 e R-20 e os portoes nao viram: `celula()` ganhou um
# primeiro parametro em par_validar.py, e heranca_validar.py e
# cobertura_cultura.py continuaram chamando com a assinatura antiga. Os dois
# passaram a estourar TypeError na primeira linha util — e como os portoes leem
# o JSON JA GRAVADO, tudo continuou verde sobre um artefato velho.
#
# O portao le o codigo (ast) e confere o numero de argumentos de cada chamada as
# funcoes de geometria compartilhada contra a assinatura de verdade
# (inspect.signature). Nao roda os modulos — roda em milissegundos e pega a
# classe inteira de defeito.
_as = []
_chk = 0
try:
    import ast as _ast, inspect as _insp
    sys.path.insert(0, "pilot-label-intelligence/bin")
    import par_validar as _PV
    _alvos = {n: _insp.signature(getattr(_PV, n))
              for n in ("celula", "celula_coerente", "palavras", "radical", "raizes_alvo",
                        "raizes_cultura", "fios_da_coluna", "e_sublinhado")
              if hasattr(_PV, n)}
    for _f in sorted(os.listdir("v1/inteligencia")):
        if not _f.endswith(".py"):
            continue
        _cam = os.path.join("v1/inteligencia", _f)
        _src = open(_cam, encoding="utf-8").read()
        _imp = {n.asname or n.name
                for _n in _ast.walk(_ast.parse(_src))
                if isinstance(_n, _ast.ImportFrom) and _n.module == "par_validar"
                for n in _n.names}
        if not _imp:
            continue
        for _n in _ast.walk(_ast.parse(_src)):
            if not (isinstance(_n, _ast.Call) and isinstance(_n.func, _ast.Name)):
                continue
            _nome = _n.func.id
            if _nome not in _imp or _nome not in _alvos:
                continue
            # chamada com desempacotamento (`f(pg, *cel)`) nao tem aridade
            # estatica: a arvore nao sabe quantos elementos a tupla tem. Contar
            # o Starred como UM argumento acusaria chamada correta, e portao que
            # acusa o certo e pior que portao nenhum.
            if any(isinstance(_x, _ast.Starred) for _x in _n.args) or any(
                    k.arg is None for k in _n.keywords):
                continue
            _chk += 1
            _npos = len(_n.args)
            _nkw = {k.arg for k in _n.keywords if k.arg}
            try:
                _alvos[_nome].bind(*([None] * _npos), **{k: None for k in _nkw})
            except TypeError as _e:
                _as.append(f"{_f}:{_n.lineno} chama {_nome}() com {_npos} posicionais e a "
                           f"assinatura e {_alvos[_nome]} ({_e})")
except Exception as _e:
    _as.append(f"assinaturas nao puderam ser conferidas: {_e}")

ok("SHARED_GEOMETRY_CALLS_MATCH_SIGNATURE",
   f"{_chk} chamadas as funcoes de geometria de par_validar conferidas contra a assinatura "
   f"de verdade, em todos os modulos de v1/inteligencia") \
    if not _as else fail("SHARED_GEOMETRY_CALLS_MATCH_SIGNATURE", " | ".join(_as[:5]))

# --- 16. dose nunca escolhida entre candidatas discordantes
r = subprocess.run(["node", "v1/testes/test_casco.js"], capture_output=True, text=True)
if r.returncode == 0:
    linha = [l for l in r.stdout.splitlines() if "passaram" in l]
    ok("CASCO_RENDER_TEST", linha[0].strip() if linha else "a suite de render passa")
else:
    fail("CASCO_RENDER_TEST", "a suite de render do casco falhou:\n" + r.stdout[-800:])

falhas = [x for x in R if x["STATE"] == "FAIL"]
json.dump({"SUITE": "PORTOES-V1", "PASS": len(R) - len(falhas), "FAIL": len(falhas),
           "RESULTS": R}, open("v1/testes/RESULTADO-PORTOES.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n  {len(R)-len(falhas)}/{len(R)} portoes passam")
sys.exit(1 if falhas else 0)
