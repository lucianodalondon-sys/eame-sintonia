# -*- coding: utf-8 -*-
"""SEGUIR-PESQUISADORES · 1) quem seguir, e por que ordem (D85). Sem rede.

    py ferramentas/seguir_pesquisadores/pessoas.py --mur=MUR-07-AGRI-05-DOCENTES.json \
        --t6=UNIDADES-T6.json --consulta2=CONSULTA2-MEDIDA.json --saida=PESSOAS-ORDENADAS.json [--n=60]

A IDENTIDADE vem da lista-mestra oficial (MUR «Cerca Università»: nome, universidade, setor). A OBRA
vem da T6 (589 trabalhos com afiliacao italiana; o par cultura x praga do casco CONFIRMADO NO TEXTO
em `NA_CONSULTA_E_NO_TEXTO`). Liga-se pessoa MUR <-> autor T6 por:
    sobrenome (inteiro) + inicial do nome + a MESMA universidade (nome do MUR -> nome no OpenAlex)
Nome sozinho nao identifica (D85: «Daniele» Bosco nao existe; e Domenico). Dois candidatos para a
mesma pessoa = AMBIGUO, e nao se funde.

PRIORIDADE (a missao: os ~60 do casco primeiro): quem tem obra RECENTE (>= 2024) com par do casco no
texto, ordenado por essas obras; depois as obras com par em qualquer ano; depois as recentes. A
contagem de obras NAO e nota de importancia (skill D85): so decide por quem se comeca.
"""
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RECENTE = "2024"

# nome do Ateneo no MUR -> pedacos que o nome da instituicao no OpenAlex tem de conter (minusculas)
ATENEU = {
    "BARI": ["bari"], "BASILICATA": ["basilicata"], "BOLOGNA": ["bologna"], "BRESCIA": ["brescia"],
    "CAMPANIA": ["campania", "vanvitelli"], "CATANIA": ["catania"], "CATTOLICA": ["cattolica", "sacred heart"],
    "FERRARA": ["ferrara"], "FIRENZE": ["florence", "firenze"], "FOGGIA": ["foggia"],
    "BOLZANO": ["bozen", "bolzano"], "MILANO": ["university of milan", "milano", "milan"],
    "MODENA": ["modena"], "MOLISE": ["molise"], "REGGIO CALABRIA": ["mediterranea", "reggio calabria"],
    "NAPOLI": ["naples federico", "federico ii"], "PADOVA": ["padua", "padova"], "PALERMO": ["palermo"],
    "PERUGIA": ["perugia"], "PISA": ["university of pisa", "universita di pisa"],
    "MARCHE": ["marche"], "SAPIENZA": ["sapienza"], "SALENTO": ["salento"], "SALERNO": ["salerno"],
    "SASSARI": ["sassari"], "SIENA": ["siena"], "SANT'ANNA": ["sant'anna", "sant’anna", "santanna"],
    "TERAMO": ["teramo"], "TORINO": ["turin", "torino"], "TRENTO": ["trento"], "TUSCIA": ["tuscia"],
    "UDINE": ["udine"], "VERONA": ["verona"],
}


def chave(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    for t in ("‐", "‑", "‒", "–", "—", "−", "-", ".", ",", "'", "’"):
        s = s.replace(t, " ")
    return " ".join(s.lower().split())


def ateneu_de(mur_ateneo: str) -> str | None:
    a = chave(mur_ateneo.replace("&quot;", ""))
    for k in ATENEU:
        if chave(k) in a:
            return k
    return None


def mesma_universidade(mur_ateneo: str, instituicoes: set) -> bool:
    k = ateneu_de(mur_ateneo)
    if not k:
        return False
    pedacos = ATENEU[k]
    return any(any(p in chave(i) for p in pedacos) for i in instituicoes)


def partir_nome_mur(cn: str) -> tuple[str, str]:
    """«ADDANTE Rocco» -> ('addante', 'rocco'); o sobrenome e o que vem em MAIUSCULAS."""
    ps = cn.split()
    sob = [p for p in ps if p.isupper() and len(p) > 1]
    nom = [p for p in ps if p not in sob]
    return chave(" ".join(sob)), chave(" ".join(nom))


def autores_t6(t6: dict) -> dict:
    P = defaultdict(lambda: {"OBRAS": 0, "RECENTES": 0, "PAR_TEXTO": 0, "PAR_TEXTO_RECENTE": 0,
                             "NOMES": set(), "ORCID": set(), "INSTITUICOES_IT": set(), "PARES": Counter(),
                             "DOIS_PAR_RECENTE": []})
    for u in t6["UNIDADES"]:
        rec = (u.get("PUBLICADO_EM") or "") >= RECENTE
        par = u.get("NA_CONSULTA_E_NO_TEXTO") or []
        for a in u["AUTORES"]:
            if not a.get("AFILIACAO_ITALIANA_NESTA_OBRA"):
                continue
            p = P[a["OPENALEX_ID"]]
            p["OBRAS"] += 1
            p["RECENTES"] += rec
            p["PAR_TEXTO"] += bool(par)
            if par and rec:
                p["PAR_TEXTO_RECENTE"] += 1
                p["DOIS_PAR_RECENTE"].append(u["DOI"])
            p["NOMES"].add(a["NOME"])
            if a.get("ORCID_NO_INDICE") not in (None, "", "NAO SEI"):
                p["ORCID"].add(a["ORCID_NO_INDICE"])
            for i in a.get("INSTITUICOES_NESTA_OBRA") or []:
                if i.get("PAIS") == "IT":
                    p["INSTITUICOES_IT"].add(i["NOME"])
            for x in par:
                p["PARES"][x] += 1
    return P


def casa_nome(sob: str, nom: str, nomes: set) -> bool:
    """O nome do autor tem o sobrenome inteiro no fim e a inicial do nome MUR no comeco."""
    for n in nomes:
        t = chave(n).split()
        if not t or not nom:
            continue
        s = sob.split()
        if len(t) > len(s) and t[-len(s):] == s and t[0][0] == nom[0]:
            return True
    return False


def montar(mur: list, t6: dict, consulta2: dict) -> list:
    P = autores_t6(t6)
    pessoas = []
    for m in mur:
        sob, nom = partir_nome_mur(m["Cognome e Nome"])
        cands = [oid for oid, p in P.items() if casa_nome(sob, nom, p["NOMES"])]
        mesmos = [oid for oid in cands if mesma_universidade(m["Ateneo"], P[oid]["INSTITUICOES_IT"])]
        if len(mesmos) == 1:
            ligacao, oid = "NOME+UNIVERSIDADE", mesmos[0]
        elif len(mesmos) > 1:
            ligacao, oid = "AMBIGUO", None
        elif cands:
            ligacao, oid = "SO_NOME_OUTRA_UNIVERSIDADE", None      # nao se funde
        else:
            ligacao, oid = "SEM_OBRA_NA_T6", None
        p = P.get(oid) if oid else None
        pessoas.append({
            "NOME": " ".join(m["Cognome e Nome"].split()), "UNIVERSIDADE": m["Ateneo"].replace("&quot;", '"'),
            "DEPARTAMENTO": m.get("Struttura di afferenza"), "CARGO": m.get("Fascia"),
            "SSD": m.get("SSD 2024"), "SSD2015": m.get("SSD2015"),
            "IDENTIDADE": "MUR (lista-mestra oficial)", "LIGACAO_T6": ligacao,
            "OPENALEX_ID": oid, "ORCID": sorted(p["ORCID"]) if p else [],
            "OBRAS_T6": p["OBRAS"] if p else 0, "RECENTES": p["RECENTES"] if p else 0,
            "PAR_DO_CASCO_NO_TEXTO": p["PAR_TEXTO"] if p else 0,
            "PAR_DO_CASCO_RECENTE": p["PAR_TEXTO_RECENTE"] if p else 0,
            "PARES": dict(p["PARES"].most_common(5)) if p else {},
            "DOIS_PAR_RECENTE": p["DOIS_PAR_RECENTE"][:5] if p else [],
            "CANDIDATOS_T6": len(cands),
        })
    # consulta2: as 5 pessoas pedidas pelo nome (com o estado que a medida deixou)
    for nome, c in (consulta2.get("PESSOAS") or {}).items():
        pessoas.append({"NOME": nome, "UNIVERSIDADE": "; ".join(sorted({i for x in c.get("CANDIDATOS") or [] for i in x.get("INSTITUICOES") or []}))[:200],
                        "IDENTIDADE": "CONSULTA2 (%s)" % c.get("ESTADO"), "LIGACAO_T6": c.get("ESTADO"),
                        "OPENALEX_ID": (c.get("IDS") or [None])[0] if c.get("ESTADO") == "RESOLVIDO" else None,
                        "ORCID": sorted({x.get("ORCID") for x in c.get("CANDIDATOS") or [] if x.get("ORCID") not in (None, "NAO SEI")}),
                        "OBRAS_T6": c.get("OBRAS", 0), "RECENTES": None,
                        "PAR_DO_CASCO_NO_TEXTO": c.get("COM_PAR_DO_CASCO_NO_TEXTO", 0), "PAR_DO_CASCO_RECENTE": None,
                        "ORGANISMOS_NO_TITULO": c.get("ORGANISMOS_EXTRA_NO_TITULO"), "CANDIDATOS_T6": len(c.get("CANDIDATOS") or [])})
    return pessoas


def ordenar(pessoas: list, n: int) -> list:
    def chave_ordem(p):
        return (p["LIGACAO_T6"] in ("NOME+UNIVERSIDADE", "RESOLVIDO"), p.get("PAR_DO_CASCO_RECENTE") or 0,
                p.get("PAR_DO_CASCO_NO_TEXTO") or 0, p.get("RECENTES") or 0, bool(p.get("ORCID")))
    ordem = sorted(pessoas, key=chave_ordem, reverse=True)
    for i, p in enumerate(ordem, 1):
        p["ORDEM"] = i
        if p["LIGACAO_T6"] in ("NOME+UNIVERSIDADE", "RESOLVIDO") and (p.get("PAR_DO_CASCO_RECENTE") or p.get("PAR_DO_CASCO_NO_TEXTO")):
            p["PORQUE"] = ("identidade oficial ligada a obra; %s obra(s) recente(s) com par do casco no texto (%s)"
                           % (p.get("PAR_DO_CASCO_RECENTE") or 0, ", ".join(list(p.get("PARES") or {})[:3]) or "ver T6"))
        elif p["LIGACAO_T6"] == "AMBIGUO":
            p["PORQUE"] = "AMBIGUO: mais de um autor T6 com o mesmo nome na mesma universidade — nao se funde"
        elif p["LIGACAO_T6"] == "SO_NOME_OUTRA_UNIVERSIDADE":
            p["PORQUE"] = "nome bate com autor T6 de OUTRA universidade — pode ser homonimo; nao se liga"
        else:
            p["PORQUE"] = "identidade oficial; sem obra do casco na T6 (nao quer dizer sem obra: a T6 so cobre as consultas do casco)"
        p["PRIORIDADE"] = i <= n and p["LIGACAO_T6"] in ("NOME+UNIVERSIDADE", "RESOLVIDO")
        if p["IDENTIDADE"].startswith("CONSULTA2") and p["LIGACAO_T6"] == "RESOLVIDO":
            # pedidas pelo NOME pelo dono (consulta2): entram alem dos n, com a identidade que a medida resolveu
            p["PRIORIDADE"] = True
            p["PORQUE"] = "pedida pelo nome (consulta2), identidade RESOLVIDA na medida; fora do MUR AGRI-05 (FEM/CNR/outros)"
    return ordem


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv[1:] if a.startswith("--") and "=" in a)
    ler = lambda k: json.loads(Path(arg[k]).read_text(encoding="utf-8"))   # noqa: E731
    pessoas = ordenar(montar(ler("mur"), ler("t6"), ler("consulta2")), int(arg.get("n", 60)))
    c = Counter(p["LIGACAO_T6"] for p in pessoas)
    prio = [p for p in pessoas if p["PRIORIDADE"]]
    Path(arg["saida"]).write_text(json.dumps({"DATASET": "SEGUIR-PESQUISADORES-PESSOAS", "RECENTE_DESDE": RECENTE,
                                              "LIGACOES": dict(c), "PRIORIDADE": len(prio), "PESSOAS": pessoas},
                                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("pessoas", len(pessoas), dict(c), "prioridade", len(prio),
          "com ORCID na prioridade", sum(1 for p in prio if p["ORCID"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
