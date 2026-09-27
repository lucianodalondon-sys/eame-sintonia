#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SINTONIA LAB · MISSAO-05 · RED TEAM EXECUTAVEL da regra de identidade proposta (IDENT-v0-LAB).

    ESPECIE   estudo do LAB. NAO e motor, NAO e pote, NAO e importado por nada. So corre sozinho:
                  python3 docs/lab/identidade-cruzamento/redteam_identidade.py            # 17 casos
                  python3 docs/lab/identidade-cruzamento/redteam_identidade.py --mutar    # 9 mutantes
    O QUE PROVA  que a regra de docs/lab/IDENTIDADE-CRUZAMENTO.md (sec. 1-4) junta o que deve e separa o
              que deve, nos casos do red team (sec. 9), e que cada guarda da regra e NECESSARIA: com --mutar,
              cada guarda e desligada uma de cada vez e pelo menos um caso tem de reprovar (mutante morto).
    VOCABULARIO  v0 PROVISORIO, o mesmo da POC (docs/lab-insumos/missao05/poc_identidade.py:54-67). O dono do
              vocabulario e o registro canonico (D104.3), nao este ficheiro.
"""
import hashlib
import re
import sys
import unicodedata

NAO_SEI = "NAO SEI"
M = set()  # mutantes ligados (vazio = regra proposta)


def dobrar(s):
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c)).lower()


def chave_substancia(s):  # motor/cruzamentos_max.py:260 @399e79f8 (TAU-FLUVALINATE = TAUFLUVALINATE; METALAXYL != METALAXYL-M)
    s = re.sub(r"[^A-Z0-9]", "", dobrar(s).upper())
    return re.sub(r"M$", "", s) if "M4_SUBSTANCIA_AGRESSIVA" in M else s


CULTURA = {"vite": "CROP:VITE", "uva": "CROP:VITE", "olivo": "CROP:OLIVO", "ulivo": "CROP:OLIVO",
           "pesco": "CROP:PESCO", "drupacee": "CROP_GRUPO:DRUPACEE", "pomacee": "CROP_GRUPO:POMACEE"}
MEMBRO_DO_GRUPO = {"CROP_GRUPO:DRUPACEE": "CROP:PESCO"}  # so o mutante M2 usa isto
MESMO_PROBLEMA = [(r"mosca dell['’ ]*oliv[ao]|mosca delle olive|bactrocera oleae", "PEST:EPPO:DACUOL"),
                  (r"ceratitis capitata|mosca mediterranea|mosca della frutta", "PEST:EPPO:CERTCA")]
LUGAR = {"lecce": ("PROV", "IT-PROV:LE"), "brindisi": ("PROV", "IT-PROV:BR"), "puglia": ("REG", "IT-REG:PUGLIA")}
PAI = {"IT-PROV:LE": "IT-REG:PUGLIA", "IT-PROV:BR": "IT-REG:PUGLIA"}


def cultura(n):
    c = CULTURA.get(dobrar(n).strip())
    return MEMBRO_DO_GRUPO.get(c, c) if "M2_GRUPO_VIRA_MEMBRO" in M else c


def praga(n):
    n = re.sub(r"\s+", " ", dobrar(n).strip())
    return next((c for r, c in MESMO_PROBLEMA if re.fullmatch(r, n)), None)  # «mosca» sozinho = None = NAO SEI


def lugar(txt):
    """So o que o TEXTO sustentou (D112); nivel mais fino. None = NAO SEI (nunca a morada da fonte)."""
    achados = [LUGAR[dobrar(x).strip()] for x in str(txt or "").split(";") if dobrar(x).strip() in LUGAR]
    if not achados:
        return None
    achados.sort(key=lambda t: {"PROV": 0, "REG": 1}[t[0]])
    cod = achados[0][1]
    return PAI.get(cod, cod) if "M3_SOBE_PARA_REGIAO" in M else cod


def campanha(fact_time, published_at=None):
    """Campanha agricola do FACTO. Publicacao NAO e fact time (INT-LAW-100) — so o mutante M9 a usa."""
    src = fact_time if fact_time not in (None, NAO_SEI) else (published_at if "M9_PUBLICACAO_VIRA_FACTO" in M else None)
    m = re.search(r"(20\d\d)", str(src or ""))
    return m.group(1) if m else None


FAMILIAS = {"F1_ROTULO_X_SUBSTANCIA_CITADA": ("JURISDICAO", "AI", "CROP"),
            "F2_PORTFOLIO_MATCH": ("JURISDICAO", "CROP", "TARGET"),
            "F4_JANELA_CULTURA_PRAGA": ("CROP", "TARGET", "LUGAR", "CAMPANHA"),
            "F5_FUTURO": ("TARGET", "LUGAR", "HORIZONTE")}


def chave(familia, slots, doc):
    partes = [familia + "/v1"]
    if "M8_EDICAO_NA_CHAVE" in M and slots.get("_EDICAO"):
        partes.append("EDICAO=" + slots["_EDICAO"])
    for s in FAMILIAS[familia]:
        v = slots.get(s)
        if v in (None, "", NAO_SEI):
            v = "NAO_SEI" if "M1_NAO_SEI_JUNTA" in M else "NAO_SEI@" + doc
        partes.append("%s=%s" % (s, v))
    k = "|".join(partes)
    return "XQ-" + hashlib.sha256(k.encode()).hexdigest()[:16]


def evidencia(item):
    """Identidade da EVIDENCIA = documento (raw_document_key; senao SHA do conteudo), nunca o item da Sala."""
    if "M5_EVIDENCIA_POR_ITEM" in M:
        return "ITEM:" + item["item_id"]
    return item.get("raw_document_key") or "SHA:" + item["raw_sha256"][:16]


def independentes(provas):
    """INT-LAW-071/092: conta ORIGINADORES distintos; mesmo documento conta 1 vez."""
    campo = "source_id" if "M6_INDEPENDENCIA_POR_SOURCE_ID" in M else "originador"
    return len({p[campo] for p in {evidencia(p): p for p in provas}.values()})


def relacao(a, b):
    """Duas leituras de estado da MESMA pergunta. INT-LAW-079: mesma origem em periodos diferentes =
    TEMPORAL_CHANGE; origens diferentes = DIVERGENT (contradicao UNRESOLVED); nunca 'CONFLITANTE' por defeito."""
    if a["estado"] == b["estado"]:
        return "CONCORDA"
    if "M7_TUDO_E_CONFLITO" in M:
        return "CONFLITANTE"
    if a["originador"] == b["originador"] and a["periodo"] != b["periodo"]:
        return "TEMPORAL_CHANGE_IN_RECOMMENDATION"
    return "DIVERGENT_RECOMMENDATIONS/CONTRADICTION_UNRESOLVED"


# ── os casos: (nome, funcao que devolve True se a regra se comportou como o red team exige) ────────────
F1, F2, F4, F5 = "F1_ROTULO_X_SUBSTANCIA_CITADA", "F2_PORTFOLIO_MATCH", "F4_JANELA_CULTURA_PRAGA", "F5_FUTURO"
FOLPET_VITE = {"JURISDICAO": "IT", "AI": "AI:" + chave_substancia("folpet"), "CROP": cultura("vite")}


def janela(txt_lugar, ft, doc, pub=None, alvo="mosca dell'olivo"):
    return chave(F4, {"CROP": cultura("olivo"), "TARGET": praga(alvo), "LUGAR": lugar(txt_lugar),
                      "CAMPANHA": campanha(ft, pub)}, doc)


CAMPANIA_2X = [{"item_id": "a", "raw_sha256": "f" * 64, "originador": "REG-CAMPANIA", "source_id": "IT-T3-002"},
               {"item_id": "b", "raw_sha256": "f" * 64, "originador": "REG-CAMPANIA", "source_id": "IT-T3-002"}]

CASOS = [
    ("RT01 lugares diferentes nao juntam (Lecce x Brindisi, mesma praga/campanha)",
     lambda: janela("Puglia ; Lecce", "2026-09-07/2026-09-13", "d1") != janela("Puglia ; Brindisi", "2026-09-07/2026-09-13", "d2")),
    ("RT02 niveis diferentes nao juntam (provincia LE x regiao Puglia)",
     lambda: janela("Puglia ; Lecce", "2026-09-10", "d1") != janela("Puglia", "2026-09-10", "d2")),
    ("RT03 'zona costiera' nao resolvida nao junta com outra nao resolvida",
     lambda: janela("zona costiera", "2026-09-10", "d1") != janela("zona costiera", "2026-09-10", "d2")),
    ("RT04 NAO SEI != NAO SEI: tau-fluvalinato ARIF n.37 x n.38 (cultura NAO SEI, POTE-R7 real) ficam 2",
     lambda: chave(F1, {"JURISDICAO": "IT", "AI": "AI:TAUFLUVALINATE", "CROP": None}, "ARIF:SETTIMANALE:2026:N37")
     != chave(F1, {"JURISDICAO": "IT", "AI": "AI:TAUFLUVALINATE", "CROP": None}, "ARIF:SETTIMANALE:2026:N38")),
    ("RT05 cultura generica nao vira especifica (drupacee x pesco)",
     lambda: chave(F2, {"JURISDICAO": "IT", "CROP": cultura("drupacee"), "TARGET": praga("ceratitis capitata")}, "d1")
     != chave(F2, {"JURISDICAO": "IT", "CROP": cultura("pesco"), "TARGET": praga("ceratitis capitata")}, "d2")),
    ("RT06 praga de nome parecido nao junta (mosca dell'olivo x mosca della frutta); 'mosca' sozinho = NAO SEI",
     lambda: praga("mosca dell'olivo") != praga("mosca della frutta") and praga("mosca") is None),
    ("RT07 sinonimos juntam (bactrocera oleae = mosca delle olive = mosca dell'olivo)",
     lambda: len({janela("Puglia ; Lecce", "2026-09-10", "d%d" % i, alvo=a) for i, a in
                  enumerate(["bactrocera oleae", "mosca delle olive", "Mosca dell’olivo"])}) == 1),
    ("RT08 grafias da mesma substancia juntam (TAU-FLUVALINATE = tau fluvalinate)",
     lambda: chave_substancia("TAU-FLUVALINATE") == chave_substancia("tau fluvalinate")),
    ("RT09 substancias diferentes de nome parecido nao juntam (METALAXYL x METALAXYL-M)",
     lambda: chave_substancia("metalaxyl") != chave_substancia("metalaxyl-m")),
    ("RT10 edicao nova da bula NAO cria pergunta nova (fica no ID; muda a AVALIACAO)",
     lambda: chave(F1, dict(FOLPET_VITE, _EDICAO="MINSALUTE_20260907"), "d1")
     == chave(F1, dict(FOLPET_VITE, _EDICAO="MINSALUTE_20261007"), "d1")),
    ("RT11 setembro x outubro na F1 = mesma pergunta (o boletim e prova, nao chave)",
     lambda: chave(F1, FOLPET_VITE, "boletim-set") == chave(F1, FOLPET_VITE, "boletim-out")),
    ("RT12 campanhas diferentes = episodios diferentes (olivo x mosca LE 2026 x 2027)",
     lambda: janela("Lecce", "2026-09-10", "d1") != janela("Lecce", "2027-09-10", "d2")),
    ("RT13 publicacao nao e fact time: sem FACT_TIME a campanha e NAO SEI e nao junta",
     lambda: janela("Lecce", None, "d1", pub="2026-09-20") != janela("Lecce", "2026-09-10", "d2")),
    ("RT14 previsao x facto nunca juntam (F5 futuro x F4 janela com os mesmos slots)",
     lambda: chave(F5, {"TARGET": praga("mosca dell'olivo"), "LUGAR": lugar("Lecce"), "HORIZONTE": "2026"}, "d1")
     != janela("Lecce", "2026-09-10", "d1")),
    ("RT15 mesmo boletim entrado 2x na Sala (Campania SA 16-09, mesmo raw_sha256) = 1 evidencia, 1 independente",
     lambda: len({evidencia(p) for p in CAMPANIA_2X}) == 1 and independentes(CAMPANIA_2X) == 1),
    ("RT16 mesma instituicao em 3 distritos/3 SOURCE_ID = 1 fonte independente (D111)",
     lambda: independentes([{"item_id": str(i), "raw_sha256": str(i) * 64, "originador": "REG-TOSCANA",
                             "source_id": "IT-T3-0%d" % i} for i in (1, 2, 3)]) == 1),
    ("RT17 tratar -> nao tratar da mesma origem em semanas seguidas = TEMPORAL_CHANGE, nao contradicao",
     lambda: relacao({"estado": "NO", "originador": "ARIF", "periodo": "n.38"},
                     {"estado": "YES", "originador": "ARIF", "periodo": "n.39"}) == "TEMPORAL_CHANGE_IN_RECOMMENDATION"
     and relacao({"estado": "NO", "originador": "ARIF", "periodo": "n.38"},
                 {"estado": "YES", "originador": "APOL", "periodo": "n.38"}).startswith("DIVERGENT")),
]

MUTANTES = ["M1_NAO_SEI_JUNTA", "M2_GRUPO_VIRA_MEMBRO", "M3_SOBE_PARA_REGIAO", "M4_SUBSTANCIA_AGRESSIVA",
            "M5_EVIDENCIA_POR_ITEM", "M6_INDEPENDENCIA_POR_SOURCE_ID", "M7_TUDO_E_CONFLITO",
            "M8_EDICAO_NA_CHAVE", "M9_PUBLICACAO_VIRA_FACTO"]


def correr():
    return [nome for nome, f in CASOS if not f()]


def main():
    M.clear()
    falhas = correr()
    for nome, _ in CASOS:
        print(("REPROVA " if nome in falhas else "passa   ") + nome)
    print("REGRA IDENT-v0-LAB: %d/%d casos passam" % (len(CASOS) - len(falhas), len(CASOS)))
    rc = 1 if falhas else 0
    if "--mutar" in sys.argv:
        vivos = []
        for mut in MUTANTES:
            M.clear()
            M.add(mut)
            mortos_por = correr()
            print("%-32s %s" % (mut, ("MORTO por " + ", ".join(n.split()[0] for n in mortos_por)) if mortos_por else "VIVO"))
            if not mortos_por:
                vivos.append(mut)
        M.clear()
        print("MUTANTES: %d plantados, %d mortos, %d vivos" % (len(MUTANTES), len(MUTANTES) - len(vivos), len(vivos)))
        rc = rc or (1 if vivos else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main())
