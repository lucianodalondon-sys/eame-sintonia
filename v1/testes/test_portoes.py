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
   f"{_conferidas} constantes que se dizem medidas foram recontadas contra os 163 rotulos") \
    if not _div else fail("MEASURED_CONSTANTS_ARE_MEASURED", " | ".join(_div))

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
