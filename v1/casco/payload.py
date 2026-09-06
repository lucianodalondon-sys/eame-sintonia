#!/usr/bin/env python3
"""
payload.py — monta o que o CASCO consome. O casco nunca abre PDF nem CSV.

Le o COLLECTION_PACKAGE (coleta) e os INTELLIGENCE_OBJECTS (inteligencia) e
devolve um unico JSON enxuto para a interface. Se um campo nao existe na fonte,
ele viaja como NOT_KNOWN / NOT_PRESENT / NOT_PROVED ate a tela — a interface nao
tem permissao de inventar o que a coleta nao trouxe.
"""
import argparse, csv, datetime, hashlib, json, os, re, sys, unicodedata
from collections import Counter

# A lista de pares vinha de sintonia/canonical, que nao esta neste repositorio e
# nao esta acessivel a esta sessao. `v1/fonte/pares_reconstruir.py` a remonta a
# partir de EXCLUSAO.json + CASCO-PAYLOAD.json, e `v1/fonte/pares_conferir.py`
# prova que a esteira chega ao mesmo lugar: R-10 identico nas 2928 chaves e os
# 2926 pares publicados identicos nos 9 campos. Medido tambem no fim da linha —
# o HTML remontado por este caminho tem o sha256 7e4ea2a7b445fafa..., o mesmo
# que o arbitro do red team 3 julgou.
PARES = "v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json"


def limpa(v):
    """O CSV oficial imprime "-" para celula vazia: isso e ausencia declarada."""
    v = str(v or "").strip()
    return "NOT_PRESENT" if v in ("-", "", "--") else v


def iso(s):
    s = (s or "").strip()
    if not s or s == "-":
        return "NOT_PRESENT"
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return "NOT_PARSED"


def linha_do_registro(snapshots, snapshot_id, reg):
    """Le a linha bruta do produto no instantaneo oficial vigente.

    Um produto Revocato ou Scaduto sai do conjunto ATIVO, nao do arquivo. A
    ferramenta tinha a linha inteira em disco e mesmo assim escrevia
    "todos os campos abaixo sao NOT_KNOWN por falta de coleta". Nao era falta
    de coleta: era a ficha nao ter ido buscar o que ja estava coletado.
    """
    caminho = os.path.join(snapshots, snapshot_id + ".csv")
    if not os.path.exists(caminho):
        return None
    alvo = reg.strip().lstrip("0")
    with open(caminho, encoding="utf-8-sig", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            if (r.get("num_registrazione") or "").strip().lstrip("0") == alvo:
                return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pacote", default="v1/dados/COLLECTION-PACKAGE.json")
    ap.add_argument("--objetos", default="v1/dados/INTELLIGENCE-OBJECTS.json")
    ap.add_argument("--versoes", default="pilot-label-intelligence/registry/IT-REGISTRO-VERSOES.json")
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pares", default=PARES)
    ap.add_argument("--exclusao", default="v1/dados/EXCLUSAO.json")
    ap.add_argument("--snapshots", default="pilot-label-intelligence/registry/snapshots")
    ap.add_argument("--teto", default="v1/dados/TETO-DOSE.json")
    ap.add_argument("--cultura", default="v1/dados/DOSES-CULTURA-CHECK.json")
    ap.add_argument("--alvoliteral", default="v1/dados/ALVO-LITERAL.json")
    ap.add_argument("--parfios", default="v1/dados/PARES-FIOS-CHECK.json")
    ap.add_argument("--heranca", default="v1/dados/HERANCA-CHECK.json")
    ap.add_argument("--alvonome", default="v1/dados/ALVO-NOMEADO.json")
    ap.add_argument("--culturanome", default="v1/dados/CULTURA-NOMEADA.json")
    ap.add_argument("--prosa", default="v1/dados/PROSA-CENSO.json")
    ap.add_argument("--citacao", default="v1/dados/CITACAO-CHECK.json")
    ap.add_argument("--banda", default="v1/dados/BANDA-FIO-CHECK.json")
    ap.add_argument("--vigencia", default="v1/dados/VIGENCIA-ETICHETTA.json")
    ap.add_argument("--cobcultura", default="v1/dados/COBERTURA-CULTURA.json")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="v1/dados/CASCO-PAYLOAD.json")
    a = ap.parse_args()

    pkg = json.load(open(a.pacote, encoding="utf-8"))
    vig = (json.load(open(a.vigencia, encoding="utf-8"))["VERDICT"]
           if os.path.exists(a.vigencia) else {})
    io_ = json.load(open(a.objetos, encoding="utf-8"))
    vs = json.load(open(a.versoes, encoding="utf-8"))
    hoje = datetime.date.fromisoformat(a.hoje)

    # EXCLUSAO NAO E PERMISSAO. O leitor de uso reusado nao modela escopo
    # negativo: em 002983 e 013405 ele leu "Pomodoro (ad esclusione di Pomodoro
    # ciliegino)" e publicou CILIEGIO como cultura AUTORIZADA. v1/coleta/exclusao.py
    # reconcilia cada par contra o PDF oficial; aqui o veredito dele e obedecido.
    exc = json.load(open(a.exclusao, encoding="utf-8")) if os.path.exists(a.exclusao) else None
    if exc is None:
        raise SystemExit("EXCLUSAO.json ausente: sem ele o casco publicaria exclusao "
                         "como permissao. Rode v1/coleta/exclusao.py antes.")
    veredito = exc["VERDICT"]
    # A GUARDA do vinculo par<->veredito. Sem ela o casco confiava numa posicao.
    with open(a.pares, "rb") as _fh:
        _sha = hashlib.sha256(_fh.read()).hexdigest()
    if _sha != exc.get("PAIRS_SHA256"):
        raise SystemExit(
            f"EXCLUSAO.json foi calculado sobre outro arquivo de pares "
            f"(sha256 {exc.get('PAIRS_SHA256','?')[:12]} vs {_sha[:12]}). Os vereditos de "
            f"exclusao sao gravados por posicao: aplica-los a outra lista faria a retirada cair "
            f"no par errado. Rode v1/coleta/exclusao.py de novo.")
    # SF-07 · JANELA QUE E PREFIXO DE OUTRA INVERTE O ESCOPO.
    # Medido: 15 janelas em 5 rotulos da familia PIRIMOR sao "tranne spinacio",
    # prefixo de "tranne spinacio baby leaf e bietola da foglia baby leaf". A
    # curta e substring verbatim e mesmo assim mente — a etichetta exclui
    # espinafre BABY LEAF, nao espinafre. Fica so a mais longa.
    def _sem_prefixo(js):
        vistos = [w for w in js if w.get("QUOTABLE")]
        out = []
        for w in vistos:
            t = re.sub(r"\s+", " ", str(w.get("TEXT") or "")).strip().lower()
            if any(t != re.sub(r"\s+", " ", str(o.get("TEXT") or "")).strip().lower()
                   and re.sub(r"\s+", " ", str(o.get("TEXT") or "")).strip().lower().startswith(t)
                   for o in vistos):
                continue
            out.append(w)
        return out + [w for w in js if not w.get("QUOTABLE")]

    # So janela de ESCOPO DE CULTURA vai para a tela: as de compatibilidade de
    # calda e de numero de tratamentos nao dizem nada sobre cultura autorizada.
    janelas_por_reg = {r: _sem_prefixo(v.get("EXCLUSION_WINDOWS_CROP_SCOPE", []))
                       for r, v in exc["LABELS"].items()}
    retirado_por_reg = {}
    for w in exc["RETIRADOS"]:
        retirado_por_reg.setdefault(w["REGISTRATION_ID"], []).append(w)
    # a retirada precisa da URL oficial do documento, como toda outra afirmacao
    _url = {i["REGISTRATION_ID"]: i["PDF_URL"] for i in pkg["ITEMS"]}
    for _r, _ws in retirado_por_reg.items():
        for _w in _ws:
            _w["LABEL_URL"] = _url.get(_r, "NOT_KNOWN")

    # usos por produto (reuso apontado)
    # R-14 · o PAR DE USO tambem tem de sobreviver aos fios desenhados. Sem
    # isto, a rodada 3 do red team mediu 47 pares publicados como uso
    # autorizado que a etichetta nao autoriza — todos com o selo verde TABELA,
    # o mais forte da tela. R-11 tirava o NUMERO de TABACCO x CIMICI e deixava
    # de pe a AFIRMACAO DE USO, que e a mais fundamental das duas.
    pf = json.load(open(a.parfios, encoding="utf-8")) if os.path.exists(a.parfios) else None
    if pf is None:
        raise SystemExit("PARES-FIOS-CHECK.json ausente: sem ele o casco publica uso "
                         "autorizado que a etichetta contradiz. Rode "
                         "v1/inteligencia/par_validar.py antes.")
    vpar = pf["VERDICT"]

    # R-17 · o NOME do alvo esta escrito no rotulo, ou veio de taxonomia?
    # 256 pares publicam um nome que o documento nao escreve nenhuma vez.
    # Isto NAO os remove — `Cydia pomonella` e mesmo a carpocapsa — mas eles nao
    # podem receber o mesmo selo de quem volta ao papel palavra por palavra.
    an = json.load(open(a.alvonome, encoding="utf-8")) if os.path.exists(a.alvonome) else None
    if an is None:
        raise SystemExit("ALVO-NOMEADO.json ausente: sem ele o casco publica nome de alvo "
                         "vindo de taxonomia com a mesma cara de nome lido do rotulo. "
                         "Rode v1/inteligencia/alvo_nomeado.py")
    vnome = an["VERDICT"]
    # R-17 · o QUALIFICADOR que o nome curto do alvo joga fora. 756 pares: em
    # 85 deles a celula escreve "mosca bianca" e a tela publicava MOSCA, que e
    # outro inseto. O modulo nao acusa (distinguir "bianca" de "sensibili"
    # precisa de entomologia); publica a palavra ao lado, como crop_scope.
    vqual = an.get("QUALIFIER") or {}

    # R-21 · e o NOME DA CULTURA, que e a irma que faltava. 23 pares publicam
    # uma cultura cuja raiz nao existe em nenhuma palavra do documento:
    # ZUCCHINO de "zucca", FAGIOLO de "FAGIOLINO", FRUMENTO de "Grano tenero e
    # duro" e — o caso que sozinho justifica a regra — CILIEGIO tirado de
    # "Pomodoro (ad esclusione di Pomodoro ciliegino)", isto e, o nome de uma
    # arvore extraido de dentro da EXCLUSAO de um tomate.
    cn = json.load(open(a.culturanome, encoding="utf-8")) if os.path.exists(a.culturanome) else None
    if cn is None:
        raise SystemExit("CULTURA-NOMEADA.json ausente: sem ele o casco publica nome de "
                         "cultura que o documento nao escreve com a mesma cara de nome lido "
                         "do rotulo. Rode v1/inteligencia/cultura_nomeada.py")
    vcnome = cn["VERDICT"]

    # QUALIFICADORES DE ESCOPO que o nome normalizado perde. Medidos no acervo:
    # 575 pares publicados trazem um deles no CROP_AS_WRITTEN e nenhum chegava a
    # tela. "VITE da vino" nao e "VITE": um produto autorizado so em uva de vinho
    # aparecia sob o mesmo nome de um autorizado tambem em uva de mesa.
    RX_ESCOPO = re.compile(
        r"\b(da vino|da tavola|da zucchero|da foraggio|da olio|da granella|da seme|"
        r"da industria|dolce|in serra|uso in serra|pieno campo|sotto tunnel|in vivai|"
        r"baby leaf|da foglia|invernale|primaverile|per consumo fresco)\b", re.I)

    cit = json.load(open(a.citacao, encoding="utf-8")) if os.path.exists(a.citacao) else None
    # AUSENCIA DE REGISTRO NAO E APROVACAO, e aqui era.
    #
    # A leitura antiga era `DETAIL.get(chave, "QUOTE_VERBATIM")`, e DETAIL so
    # tem as citacoes REPROVADAS. As 163 QUOTE_TOO_SHORT_TO_CHECK e as 349
    # ROW_RECONSTRUCTED_FROM_CELLS nunca estiveram la e saiam na tela como
    # "Citacao do documento" — 512 selos por valor default. Pior, a chave era a
    # frase cortada em 200 caracteres, cortada no MODULO sobre o texto cru e
    # AQUI sobre o texto normalizado: as 35 citacoes longas nunca casavam e
    # tambem caiam no default, em silencio.
    #
    # Agora R-18 publica VERDICT com TODAS as citacoes, a chave e o sha1 da
    # frase normalizada, e o default e QUOTE_NOT_CHECKED — que e o que a
    # ferramenta sabe quando nao encontra o registro.
    _cit = (cit or {}).get("VERDICT") or {}

    def _chave_cit(familia, reg, txt):
        n = unicodedata.normalize("NFD", str(txt or ""))
        n = "".join(c for c in n if unicodedata.category(c) != "Mn").lower()
        n = re.sub(r"\s+", " ", n).strip()
        return f"{familia}|{reg}|" + hashlib.sha1(n.encode()).hexdigest()[:16]

    def _estado_cit(reg, familia, txt):
        if not cit:
            return "QUOTE_NOT_CHECKED"
        return _cit.get(_chave_cit(familia, reg, txt), "QUOTE_NOT_CHECKED")

    usos = {}
    contraditos_por_reg, rotacao_por_reg = {}, {}
    prova_par = {c["KEY"]: c for c in pf["CONTRADICTED"]}
    for w in exc.get("ROTACAO", []):
        rotacao_por_reg.setdefault(w["REGISTRATION_ID"], []).append(w)
    for _r, _ws in rotacao_por_reg.items():
        for _w in _ws:
            _w["LABEL_URL"] = _url.get(_r, "NOT_KNOWN")
    TAB = {"GEOMETRIC_TABLE", "MERGED_COLUMN_TABLE"}
    ordem = {}
    trio = exc.get("VERDICT_KEY_TRIPLE", {})
    for x in json.load(open(a.pares, encoding="utf-8"))["PAIRS"]:
        reg = x["REGISTRATION_ID"]
        i = ordem[reg] = ordem.get(reg, -1) + 1
        chave = f"{reg}#{i}"
        esperado = trio.get(chave)
        if esperado and esperado != [x["CROP"], x["TARGET"]]:
            raise SystemExit(
                f"vinculo de exclusao desalinhado em {chave}: EXCLUSAO.json diz "
                f"{esperado} e a lista de pares traz {[x['CROP'], x['TARGET']]}")
        est = veredito.get(chave, "NOT_CHECKED")
        if est == "CROP_ONLY_INSIDE_EXCLUSION":
            continue                      # nao entra na lista de usos autorizados
        if est == "CROP_ONLY_IN_ROTATION_RESTRICTION":
            continue                      # proibir de semear nao e autorizar a tratar
        # R-14 · par contradito pelos fios NAO entra em `uses`. Ele nao e
        # apagado: vai para a lista propria da ficha, com a prova geometrica.
        vp = vpar.get(chave, "PAIR_NOT_CHECKED")
        if vp == "PAIR_CONTRADICTED_BY_RULE":
            w = dict(prova_par.get(chave, {}))
            w["LABEL_URL"] = _url.get(reg, "NOT_KNOWN")
            contraditos_por_reg.setdefault(reg, []).append(w)
            continue
        _craw = str(x.get("CROP_AS_WRITTEN") or "")
        _esc = sorted({m.group(1).lower() for m in RX_ESCOPO.finditer(_craw)})
        _nome = vnome.get(chave, "TARGET_NAME_NOT_CHECKED")
        _cnome = vcnome.get(chave, "CROP_NAME_NOT_CHECKED")
        usos.setdefault(reg, []).append({
            "crop": x["CROP"], "target": x["TARGET"],
            "crop_raw": x.get("CROP_AS_WRITTEN"), "target_raw": x.get("TARGET_AS_WRITTEN"),
            # R-18 nas duas frases que a tela imprime com verbo de citacao ao
            # lado de cada par. Sao 2.873 de cada, e nenhuma tinha sido olhada:
            # medido, 1.408 celulas de cultura e 939 de alvo NAO sao literais —
            # a maioria por corte no meio de palavra, que e o extrator cortando
            # por comprimento e nao o rotulo escrevendo assim.
            "crop_raw_state": _estado_cit(reg, "PAIR_CROP_AS_WRITTEN", x.get("CROP_AS_WRITTEN")),
            "target_raw_state": _estado_cit(reg, "PAIR_TARGET_AS_WRITTEN",
                                            x.get("TARGET_AS_WRITTEN")),
            "page": x.get("PAGE") or "NOT_PRESERVED",
            "route": x.get("ROUTE"),
            "evidence": "TABLE_GEOMETRY" if x.get("ROUTE") in TAB else "TEXT_INFERENCE",
            "quote": "NOT_PRESERVED",
            "exclusion_check": est,
            "pair_check": vp,
            # AS TRES COLUNAS, E ELAS NUNCA SE COLAPSAM.
            #   proof       o par sobreviveu a um teste contra o documento?
            #   target_name o NOME DO ALVO publicado esta escrito no documento?
            #   crop_name   o NOME DA CULTURA publicado esta escrito no documento?
            # Um par so e FATO quando as tres fecham. Eram duas colunas e 1.274
            # fatos; a terceira nasceu de 23 pares em que a cultura publicada
            # nao e palavra nenhuma do documento.
            #
            # CROP_NAME_INFLECTED_IN_LABEL FECHA a coluna, e isto e uma decisao
            # com motivo medido: sao 31 pares em que a etichetta escreve
            # "cavoli" e a ferramenta publica CAVOLO. A palavra E a mesma, no
            # plural, e recusar por causa disso seria esconder fato verdadeiro
            # para a regra parecer severa. Ja "fagiolino" nao e "fagiolo" e
            # "zucca" nao e "zucchino": raiz diferente, palavra diferente.
            "proof": ("USE_PAIR_PROVEN_BY_TABLE_GEOMETRY"
                      if vp == "PAIR_CONSISTENT_WITH_RULES"
                      else "USE_PAIR_NOT_VERIFIED_BY_ANY_RULE"),
            "target_name": _nome,
            "crop_name": _cnome,
            "fact": (vp == "PAIR_CONSISTENT_WITH_RULES"
                     and _nome == "TARGET_NAME_LITERAL"
                     and _cnome in ("CROP_NAME_LITERAL", "CROP_NAME_INFLECTED_IN_LABEL")),
            "crop_scope": _esc,
            "target_scope": vqual.get(chave) or [],
        })

    # TETO POR CULTURA escrito fora da tabela (R-12) e CONFERENCIA DA CULTURA
    # da linha contra os fios desenhados (R-11). Sem os dois a tela publica
    # dose acima do que o proprio rotulo autoriza e dose atribuida a cultura
    # errada — os dois erros foram medidos, nao supostos.
    teto = json.load(open(a.teto, encoding="utf-8")) if os.path.exists(a.teto) else None
    cultura = json.load(open(a.cultura, encoding="utf-8")) if os.path.exists(a.cultura) else None
    if teto is None or cultura is None:
        raise SystemExit("TETO-DOSE.json e/ou DOSES-CULTURA-CHECK.json ausentes: sem eles o "
                         "casco publica dose acima do teto do rotulo e dose de outra cultura. "
                         "Rode v1/inteligencia/teto_dose.py e v1/inteligencia/cultura_validar.py")
    vc = cultura["VERDICT"]
    # R-15 · MAX. APLICACOES e INTERVALO herdados de celula mesclada
    her = json.load(open(a.heranca, encoding="utf-8")) if os.path.exists(a.heranca) else None
    if her is None:
        raise SystemExit("HERANCA-CHECK.json ausente: sem ele o casco publica o n.max da "
                         "linha vizinha como fato. Rode v1/inteligencia/heranca_validar.py")
    vmax, vint = her["VERDICT_MAX"], her["VERDICT_INTERVAL"]
    # R-18 · a ferramenta nao pode imprimir com o verbo "o rotulo escreve" nada
    # que nao esteja no rotulo. Medido: 68 celulas de dose citadas nao existem
    # contiguas em leitura nenhuma — sao montadas com pedaco de mais de uma
    # celula ("...ravanello, zucchino sedano", onde "sedano" e celula propria).
    prova_her = {}
    for c in her["CONTRADICTED"]:
        prova_her.setdefault(c["KEY"], {})[c["FIELD"]] = c
    alv = json.load(open(a.alvoliteral, encoding="utf-8")) if os.path.exists(a.alvoliteral) else None
    va = alv["VERDICT"] if alv else {}
    # R-22 · a banda que o extrator leu como UMA linha tem um fio desenhado por
    # dentro? 29 linhas tem, e nelas o numero publicado pode ser da linha de
    # baixo — em 018270 o unico "1" da regiao esta do outro lado do risco.
    bnd = json.load(open(a.banda, encoding="utf-8")) if os.path.exists(a.banda) else None
    if bnd is None:
        raise SystemExit("BANDA-FIO-CHECK.json ausente: sem ele o casco publica como dose de "
                         "uma linha um numero que esta do outro lado de um fio desenhado. "
                         "Rode v1/inteligencia/banda_fio.py")
    vb = bnd["VERDICT"]
    prova_banda = {c["KEY"]: c for c in bnd["CROSSED"]}

    # doses por produto, ja deduplicadas
    doses = {}
    if os.path.exists(a.doses):
        for lab in json.load(open(a.doses, encoding="utf-8"))["LABELS"]:
            seen, out = set(), []
            for _i, r in enumerate(lab.get("ROWS") or []):
                k = (r.get("CROP"), r.get("TARGET"), r.get("DOSE_CONCENTRATION"),
                     r.get("DOSE_PER_HECTARE"))
                if k in seen:
                    continue
                seen.add(k)
                out.append({
                    "crop_check": vc.get(f'{lab["REGISTRATION_ID"]}#{_i}', "NOT_CHECKED"),
                    "target_literal": va.get(f'{lab["REGISTRATION_ID"]}#{_i}', "TARGET_TEXT_NOT_CHECKED"),
                    "band_check": vb.get(f'{lab["REGISTRATION_ID"]}#{_i}',
                                         "DOSE_ROW_BAND_NOT_CHECKED"),
                    "band_proof": (prova_banda.get(f'{lab["REGISTRATION_ID"]}#{_i}') or {}
                                   ).get("PROOF", "NOT_APPLICABLE"),
                    "crop": r.get("CROP"), "target": r.get("TARGET"),
                    "crop_inherited": bool(r.get("CROP_INHERITED")),
                    "dose_conc": r.get("DOSE_CONCENTRATION"),
                    "unit_conc": r.get("DOSE_CONCENTRATION_UNIT"),
                    "dose_ha": r.get("DOSE_PER_HECTARE"),
                    "unit_ha": r.get("DOSE_PER_HECTARE_UNIT"),
                    "dose_ha_inherited": bool(r.get("DOSE_PER_HECTARE_INHERITED")),
                    "max_app": r.get("MAX_APPLICATIONS"),
                    "max_app_inherited": bool(r.get("MAX_APPLICATIONS_INHERITED")),
                    "max_check": vmax.get(f'{lab["REGISTRATION_ID"]}#{_i}', "MAX_NOT_CHECKED"),
                    "interval": r.get("APPLICATION_INTERVAL"),
                    "interval_check": vint.get(f'{lab["REGISTRATION_ID"]}#{_i}',
                                               "INTERVAL_NOT_CHECKED"),
                    "note_says": ((prova_her.get(f'{lab["REGISTRATION_ID"]}#{_i}', {})
                                   .get("MAX_APPLICATIONS") or {}).get("LABEL_NOTE")),
                    "note_max": ((prova_her.get(f'{lab["REGISTRATION_ID"]}#{_i}', {})
                                  .get("MAX_APPLICATIONS") or {}).get("LABEL_SAYS")),
                    "page": r.get("SOURCE_PAGE"),
                    "quote": r.get("SOURCE_QUOTE"),
                    "crop_cell_state": _estado_cit(lab["REGISTRATION_ID"], "DOSE_CROP_CELL",
                                                   r.get("CROP")),
                    "target_cell_state": _estado_cit(lab["REGISTRATION_ID"], "DOSE_TARGET_CELL",
                                                     r.get("TARGET")),
                    "quote_state": _estado_cit(lab["REGISTRATION_ID"], "DOSE_SOURCE_QUOTE",
                                               r.get("SOURCE_QUOTE")),
                    "rule_check": r.get("DOSE_RULE_CHECK", "NOT_CHECKED"),
                    "needs_review": bool(r.get("NEEDS_REVIEW")),
                    "rejected": r.get("DOSE_PER_HECTARE_REJECTED"),
                })
            doses[lab["REGISTRATION_ID"]] = {"rows": out, "state": lab.get("PARSE_STATE")}

    produtos = []
    for i in pkg["ITEMS"]:
        reg = i["REGISTRATION_ID"]
        try:
            dte = (datetime.date.fromisoformat(i["EXPIRY_RAW"]) - hoje).days
        except Exception:
            dte = "NOT_KNOWN"
        dz = doses.get(reg, {})
        produtos.append({
            "reg": reg, "name": i["PRODUCT_NAME_RAW"], "holder": i["HOLDER_RAW"],
            "status": i["STATUS_RAW"], "actives": i["ACTIVE_INGREDIENTS_RAW"],
            "formulation": i["FORMULATION_RAW"], "activity": i["ACTIVITY_RAW"],
            "registered_at": i["REGISTERED_AT"], "expiry": i["EXPIRY_RAW"], "dte": dte,
            "pdf_url": i["PDF_URL"], "pdf_sha": i["PDF_SHA256"], "pdf_bytes": i["PDF_BYTES"],
            "label_effective": i["LABEL_EFFECTIVE_AT"],
            "label_valid_from": i.get("LABEL_VALID_FROM", "NOT_CHECKED"),
            "label_valid_to": i.get("LABEL_VALID_TO", "NOT_CHECKED"),
            "label_validity_quote": i.get("LABEL_VALIDITY_QUOTE", "NOT_PRESENT"),
            # R-19 · NOT_PRESENT dizia "o rotulo nao declara vigencia" em 162
            # fichas. Medido: 112 rotulos escrevem "con validita dal <data>" e
            # 150 escrevem "Etichetta autorizzata con ..." — o leitor e que so
            # conhece a forma "valida dal X al Y", que existe em 1. Agora o
            # estado tem nome proprio e a frase vai junto.
            "label_validity_state": vig.get(reg, {}).get("STATE", "VALIDITY_NOT_CHECKED"),
            "label_validity_form": vig.get(reg, {}).get("FORM"),
            "label_validity_literal": vig.get(reg, {}).get("QUOTE"),
            "captured_at": i["CAPTURED_AT"],
            "snapshot": i["REGISTRY_SNAPSHOT_ID"], "snapshot_sha": i["REGISTRY_SNAPSHOT_SHA256"],
            "source_url": i["SOURCE_URL"], "run": i["COLLECTION_RUN_ID"],
            "states": i["READ_STATES"],
            "ceilings": teto["CEILINGS"].get(reg, []),
            "label_dose_notes_not_read": reg in teto["OTHER_DOSE_NOTES_NOT_READ"],
            # R-12b · a frase literal da restricao fora da tabela. Sem ela, o
            # NOT_PRESENT da coluna MAX. APLICACOES le-se "nao esta no rotulo"
            # quando esta, em negrito, na AVVERTENZA.
            "label_app_limit_notes": teto.get("APPLICATION_LIMIT_NOTES", {}).get(reg, []),
            "uses": usos.get(reg, []),
            "uses_retirados": retirado_por_reg.get(reg, []),
            "uses_contraditos": contraditos_por_reg.get(reg, []),
            "uses_rotacao": rotacao_por_reg.get(reg, []),
            "exclusion_windows": janelas_por_reg.get(reg, []),
            "doses": dz.get("rows", []),
            "dose_state": dz.get("state", "NOT_ATTEMPTED"),
            "text_chars": i["TEXT_CHARS"],
        })

    objetos = io_["OBJECTS_LIST"]

    # Um evento pode falar de registro que JA NAO esta no conjunto ativo — foi
    # revogado, venceu, ou saiu. Sem uma ficha para ele, o card cita um produto
    # que a ferramenta nao abre, e o usuario fica sem versao, titular e validade.
    ESTADOS = ("LABEL_DISCOVERED", "LABEL_DOWNLOADED", "TEXT_EXTRACTED", "LABEL_READ",
               "USE_ROWS_STRUCTURED", "DOSE_STRUCTURED", "PHI_STRUCTURED", "NEEDS_REVIEW")
    tem = {p["reg"] for p in produtos}
    faltando = {}
    for o in objetos:
        r = o.get("REGISTRATION_ID")
        if r and r not in tem:
            faltando.setdefault(r, o)
    for r, o in faltando.items():
        linha = linha_do_registro(a.snapshots, pkg["REGISTRY_SNAPSHOT_ID"], r)
        if linha is None:
            # Aqui sim: o registro nao esta no instantaneo vigente. NOT_KNOWN
            # por ausencia de linha, e a ficha diz isso e nao outra coisa.
            produtos.append({
                "reg": r, "name": o.get("PRODUCT_NAME") or "NOT_KNOWN",
                "holder": o.get("HOLDER") or "NOT_KNOWN",
                "status": "NOT_IN_SNAPSHOT",
                "actives": "NOT_KNOWN", "formulation": "NOT_KNOWN", "activity": "NOT_KNOWN",
                "registered_at": "NOT_KNOWN", "expiry": "NOT_KNOWN", "dte": "NOT_KNOWN",
                "pdf_url": "NOT_KNOWN", "pdf_sha": "NOT_KNOWN", "pdf_bytes": "NOT_KNOWN",
                "label_effective": "NOT_KNOWN",
                "captured_at": o.get("CAPTURED_AT", "NOT_KNOWN"),
                "snapshot": pkg["REGISTRY_SNAPSHOT_ID"],
                "snapshot_sha": pkg["REGISTRY_SNAPSHOT_SHA256"],
                "source_url": o.get("SOURCE_URL", "NOT_KNOWN"),
                "run": pkg["COLLECTION_RUN_ID"],
                "states": {k: False for k in ESTADOS},
                "uses": [], "uses_retirados": [], "exclusion_windows": [],
                "doses": [], "dose_state": "NOT_ATTEMPTED",
                "text_chars": "NOT_KNOWN",
                "out_of_active_set": True,
                "registry_row_read": False,
                "out_of_active_set_note": (
                    "este registro aparece no historico oficial mas NAO tem linha no "
                    "instantaneo vigente. Nao ha o que ler: os campos sao NOT_KNOWN por "
                    "ausencia de linha, nao por opiniao da ferramenta"),
            })
            continue
        venc = iso(linha.get("data_scadenza_autorizzazione"))
        try:
            dte = (datetime.date.fromisoformat(venc) - hoje).days
        except Exception:
            dte = "NOT_KNOWN"
        produtos.append({
            "reg": r,
            "name": limpa(linha.get("denominazione_prodotto")),
            "holder": limpa(linha.get("ragione_sociale")),
            "status": limpa(linha.get("stato_amministrativo")),
            "actives": limpa(linha.get("sostanze_attive")),
            "formulation": limpa(linha.get("descrizione_formulazione")),
            "activity": limpa(linha.get("attivita")),
            "registered_at": iso(linha.get("data_registrazione")),
            "expiry": venc, "dte": dte,
            "hazard": limpa(linha.get("indicazioni_di_pericolo")),
            "revoke_reason": limpa(linha.get("motivo_della revoca")),
            "revoke_decree": limpa(linha.get("data_decreto_revoca")),
            "revoke_effective": iso(linha.get("data_decorrenza_revoca")),
            # O ROTULO deste produto nao foi baixado. Isto e diferente de nao
            # existir: e NOT_COLLECTED, e a ficha tem de dizer qual dos dois e.
            "pdf_url": "NOT_COLLECTED", "pdf_sha": "NOT_COLLECTED",
            "pdf_bytes": "NOT_COLLECTED", "label_effective": "NOT_COLLECTED",
            # A data de captura e de um ARTEFATO. Para estes tres nao houve
            # captura de rotulo nenhuma: copiar a data do primeiro produto do
            # pacote seria atribuir a eles um ato que nao aconteceu.
            "captured_at": "NOT_COLLECTED",
            "registry_row_captured_at": pkg["ITEMS"][0]["CAPTURED_AT"] if pkg["ITEMS"] else "NOT_KNOWN",
            "snapshot": pkg["REGISTRY_SNAPSHOT_ID"],
            "snapshot_sha": pkg["REGISTRY_SNAPSHOT_SHA256"],
            "source_url": pkg["ITEMS"][0]["SOURCE_URL"] if pkg["ITEMS"] else "NOT_KNOWN",
            "run": pkg["COLLECTION_RUN_ID"],
            "states": dict({k: False for k in ESTADOS}, LABEL_DISCOVERED=False),
            "ceilings": [], "label_dose_notes_not_read": False,
            "uses": [], "uses_retirados": [], "exclusion_windows": [],
            "doses": [], "dose_state": "NOT_ATTEMPTED",
            "text_chars": "NOT_COLLECTED",
            "out_of_active_set": True,
            "registry_row_read": True,
            "out_of_active_set_note": (
                "este registro NAO esta no conjunto ativo do instantaneo vigente — o "
                "estado administrativo dele e \"" + limpa(linha.get("stato_amministrativo")) +
                "\". Sair do conjunto ativo nao e sair do arquivo: os campos de registro "
                "abaixo foram LIDOS da linha oficial deste produto no instantaneo "
                + pkg["REGISTRY_SNAPSHOT_ID"] + ". O que nao existe aqui e o ROTULO: "
                "nenhum PDF foi baixado para ele, entao uso, dose e PHI ficam "
                "NOT_COLLECTED — por falta de coleta, nao por ausencia no registro"),
        })
    # versoes do registro para a timeline
    versoes = [{"date": v["SNAPSHOT_DATE"], "id": v["VERSION_ID"], "sha": v["SHA256"],
                "bytes": v["BYTES"], "url": v["SOURCE_URL"],
                "republished": v.get("REPUBLISHED_UNCHANGED_ON", []),
                "adama_active": v["ADAMA_ACTIVE"], "total": v["PRODUCTS_TOTAL"]}
               for v in vs["VERSIONS"]]

    cov = pkg["COVERAGE"]
    payload = {
        "TOOL": "SINTONIA — LABEL INTELLIGENCE",
        "VERSION": "V1",
        "COUNTRY": "IT",
        "BUILT_AT": a.hoje,
        # A DATA DO DADO NAO E A DATA DO BUILD. O cabecalho dizia "dados de
        # 2026-09-06", que e o dia em que a ferramenta foi montada; o
        # instantaneo oficial mais novo e de 2026-08-31, e a mudanca mais nova
        # dentro dele e mais antiga ainda. Tres datas diferentes, uma so
        # impressa: era a errada.
        "DATA_DATE": versoes[-1]["date"] if versoes else "NOT_KNOWN",
        "DATA_SNAPSHOT_ID": pkg["REGISTRY_SNAPSHOT_ID"],
        "NEWEST_CHANGE_AT": max((o.get("DETECTED_AT") or "" for o in objetos
                                 if o.get("PROOF_STATE") == "PROVED"), default="") or "NOT_KNOWN",
        "RUN": pkg["COLLECTION_RUN_ID"],
        "RULESET_VERSION": io_["RULESET_VERSION"],
        "SOURCE_AUTHORITY": pkg["SOURCE_AUTHORITY"],
        "LICENSE": pkg["LICENSE"],
        "coverage": cov,
        "coverage_note": pkg["COVERAGE_NOTE"],
        "products": produtos,
        "objects": objetos,
        "versions": versoes,
        "history": {
            "snapshots": vs["SNAPSHOTS_DOWNLOADED"],
            "distinct": vs["DISTINCT_DOCUMENTS"],
            "window": f'{versoes[0]["date"]}..{versoes[-1]["date"]}',
            "raw_field_diffs": vs["FIELD_DIFFS_WITHOUT_NORMALISATION"],
            "normalised_field_diffs": vs["FIELD_DIFFS_WITH_NORMALISATION"],
            "noise": vs["SERIALIZATION_NOISE_SUPPRESSED"],
            "noise_pct": vs["NOISE_SHARE"],
            "true_changes": vs["CHANGE_EVENTS_REGULATORY"],
            "text_only": vs["CHANGE_EVENTS_TEXT_ONLY"],
        },
        "exclusion": {
            "rule": exc["RULE_ID"],
            "labels_checked": exc["LABELS_CHECKED"],
            "labels_with_crop_scope_exclusion": exc["LABELS_WITH_CROP_SCOPE_EXCLUSION"],
            "labels_with_any_marker": exc["LABELS_WITH_ANY_EXCLUSION_MARKER"],
            "prefix_match_only": exc["PAIRS_CROP_NAME_PREFIX_MATCH_ONLY"],
            "pairs_checked": exc["PAIRS_CHECKED"],
            "retirados": exc["PARES_RETIRADOS"],
            "name_not_in_label_text": exc["PAIRS_CROP_NAME_NOT_IN_LABEL_TEXT"],
            "markers": exc["MARCADOR_OCORRENCIAS"],
            "marker_dropped": exc["MARCADOR_DESCARTADO"],
            "marker_not_used": exc.get("EXCLUSION_MARKER_NOT_USED", {}),
            "marker_not_used_note": exc.get("EXCLUSION_MARKER_NOT_USED_NOTA", "NOT_KNOWN"),
            "list": exc["RETIRADOS"],
        },
        "reconciliation": (json.load(open("v1/BASELINE-RAW.json", encoding="utf-8"))
                           .get("RECONCILIATION_WITH_PUBLISHED")
                           if os.path.exists("v1/BASELINE-RAW.json") else
                           {"STATE": "NOT_CHECKED"}),
        "ceiling": {k: v for k, v in teto.items() if k != "CEILINGS"},
        "crop_check": {k: v for k, v in cultura.items() if k not in ("VERDICT", "CONTRADICTED")},
        "crop_check_list": cultura["CONTRADICTED"],
        "pair_check": {k: v for k, v in pf.items() if k not in ("VERDICT", "CONTRADICTED")},
        "band_check": {k: v for k, v in bnd.items() if k not in ("VERDICT", "CROSSED")},
        "target_name": {k: v for k, v in an.items()
                        if k not in ("VERDICT", "NOT_IN_LABEL", "QUALIFIER")},
        "crop_name": dict({k: v for k, v in cn.items() if k != "VERDICT"}),
        "citacao": ({k: v for k, v in cit.items() if k != "DETAIL"} if cit
                    else {"STATE": "NOT_CHECKED"}),
        "vigencia": ({k: v for k, v in json.load(open(a.vigencia, encoding="utf-8")).items()
                      if k != "VERDICT"} if os.path.exists(a.vigencia)
                     else {"STATE": "NOT_CHECKED"}),
        # R-20 · cobertura contada por CELULA DE CULTURA DESENHADA. O denominador
        # por ROTULO escondia o bloco que o leitor nao leu dentro do rotulo que
        # ele leu: 008259 conta como coberto com 184 pares e tem, na mesma
        # pagina, celulas cheias cujo nome nunca virou par.
        "coverage_crop_cell": ({k: v for k, v in
                                json.load(open(a.cobcultura, encoding="utf-8")).items()
                                if k not in ("BY_LABEL", "NOT_READ")}
                               if os.path.exists(a.cobcultura) else {"STATE": "NOT_MEASURED"}),
        "prose": ({k: v for k, v in json.load(open(a.prosa, encoding="utf-8")).items()
                   if k != "LINHAS"} if os.path.exists(a.prosa) else {"STATE": "NOT_MEASURED"}),
        "pair_check_list": pf["CONTRADICTED"],
        "inheritance_check": {k: v for k, v in her.items()
                              if k not in ("VERDICT_MAX", "VERDICT_INTERVAL", "CONTRADICTED")},
        "rotation": {"rule": "R-10b", "markers": exc.get("SUCESSAO_MARCADORES", {}),
                     "pairs": exc.get("PARES_EM_RESTRICAO_DE_SUCESSAO", 0),
                     "list": exc.get("ROTACAO", [])},
        "target_literal": ({k: v for k, v in alv.items() if k not in ("VERDICT", "NOT_FOUND")}
                           if alv else {"STATE": "NOT_CHECKED"}),
        "by_type": io_["BY_TYPE"],
        "by_proof": io_["BY_PROOF_STATE"],
        "by_window": io_["BY_TIME_WINDOW"],
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(payload, open(a.out, "w", encoding="utf-8"), ensure_ascii=False,
              separators=(",", ":"))
    print(f'  produtos {len(produtos)} | objetos {len(objetos)} | versoes {len(versoes)}',
          file=sys.stderr)
    print(f'  {os.path.getsize(a.out)/1024:.0f} KB -> {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
