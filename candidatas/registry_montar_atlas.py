#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTAR O ATLAS RECONCILIADO — escreve UM ficheiro, o que ja' era o dono.

    docs/fontes/ATLAS-DE-FONTES-EAME.md

Nao cria ATLAS-V2, nem MASTER-ATLAS, nem REGISTRY-V2. Um conceito, um dono.

DE ONDE VEM CADA FICHA, E POR QUE
---------------------------------
A `italy-source-qualification-v1` e' a BASE MATERIAL por COMPLETUDE MEDIDA —
o atlas dela tem 204 das 255 identidades, e o atlas desta linha tem 64 que
estao todas contidas nela (perda zero ao adota-la). Nao e' autoridade nova: a
autoridade e' o caminho do ficheiro, que nao muda.

    qualification   204 fichas   base material
    cool-dijkstra     3 fichas   IT-T10-001/002/003 — as vencedoras das 3
                                 colisoes, com cerca e evidencia
    passport-tags     7 fichas   inclui IT-T4-002, exclusiva daquela linha
    master JSON      41 fichas   identidades sem ficha em atlas nenhum
    ────────────────────────────
                    255

ZERO IDENTIDADE NOVA
--------------------
`SOURCE_IDS_CREATED = 0`. Tudo o que entra aqui JA FOI EMITIDO alguma vez. A
BMTI, o comercio exterior novo do ISTAT e qualquer outra fonte sem numero
ficam em NEEDS_SOURCE_REGISTRATION — nomeadas, e sem identidade.
"""

import collections
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "candidatas"))
ATLAS = RAIZ / "docs" / "fontes" / "ATLAS-DE-FONTES-EAME.md"
PROVA = RAIZ / "build" / "source-registry-reconciliation"
ID = re.compile(r"\b(?:IT|ES|FR|EU|XX|PT|DE)-T\d{1,2}-\d{3}\b")

from registry_censo import (ler as ler_emissor, expandir_faixas,   # noqa: E402
                            sem_parenteses)

CENSO = json.loads((PROVA / "censo.json").read_text(encoding="utf-8"))
CLAS = json.loads((PROVA / "classificacao.json").read_text(encoding="utf-8"))

QUAL = "origin/claude/italy-source-qualification-v1"
COOL = "origin/claude/cool-dijkstra-4agznu"
PASS = "origin/claude/passport-tags-italy-v1"
CAM = "docs/fontes/ATLAS-DE-FONTES-EAME.md"

# ── AS CINCO DECISOES HUMANAS, escritas como dado e nao como codigo ────────
DECISOES = {
 "IT-T4-001": dict(
   fica="Ministero della Salute — Fitosanitari, elenco dei prodotti "
        "fitosanitari autorizzati (dati.salute.gov.it)",
   nao="ARPAV",
   nota="⚠️ MEDIDO DEPOIS DA DECISAO: este numero NUNCA esteve em disputa. As "
        "duas linhas que o declaram — qualification e cool-dijkstra — dizem "
        "AMBAS «Ministero della Salute». A «afirmacao ARPAV» era defeito do "
        "meu leitor, que extraia IDs de toda a cerca da ficha e fazia um "
        "numero mencionado herdar os campos de outra. A decisao confirma o "
        "que o atlas ja dizia em 28 versoes."),
 "ES-T4-005": dict(
   fica="MAPA — Registro Oficial de Productos Fitosanitarios: UMA fonte, "
        "DUAS rotas (mapa.gob.es/.../sanidad-vegetal e "
        "servicio.mapa.gob.es/regfiweb)",
   nao="um segundo SOURCE_ID para separar as duas rotas",
   nota="⚠️ TAMBEM NAO ERA COLISAO. A ficha `ES-T4-003` declara "
        "`SUPERSEDED_BY: ES-T4-005`, e o meu leitor tratava essa REFERENCIA "
        "CRUZADA como declaracao de identidade — atribuindo a 005 os campos "
        "da 003. URL nao e' identidade: SAME_SOURCE_MULTIPLE_ROUTES."),
 "IT-T10-001": dict(
   fica="ARPAV — Vendite fitosanitari (open data) + Rapporto annuale, "
        "ambito Veneto",
   nao="ISMEA (que ja' e' IT-T10-007, confirmado) e ISTAT Distribuzione "
       "(que e' IT-T10-003)",
   nota="colisao REAL: o atlas com cerca e evidencia dizia ARPAV; o "
        "ITALY-SOURCE-MASTER-V1.json, sem cerca e sem evidencia, reclamava o "
        "numero para a ISMEA. A decisao segue a prova."),
 "IT-T10-002": dict(
   fica="OpenStreetMap, via Overpass API + Nominatim (licenca ODbL, "
        "atribuicao obrigatoria)",
   nao="BMTI",
   nota="colisao REAL, resolvida pela evidencia preservada. ⚠️ E fica uma "
        "pendencia DE OUTRA NATUREZA, que NAO toca a identidade: "
        "TERRITORY_FIT_REVIEW — o OSM em T10 (MARKET/TRADE/INDUSTRY) e' "
        "estranho a leitura, e SOURCE_ID emitido nao se reclassifica por "
        "estetica."),
 "IT-T10-003": dict(
   fica="ISTAT — Distribuzione per uso agricolo dei prodotti fitosanitari "
        "(endpoint SDMX 101_22_DF_DCSP_FITOSANITARI_1)",
   nao="ISTAT commercio estero / coeweb",
   nota="colisao REAL. ⚠️ E a rota que perdeu o numero esta ENCERRADA: o "
        "`coeweb.istat.it` fechou em 30/09/2025 e o servico passou para "
        "`esploradati.istat.it/coeweb`. O comercio exterior nao recebe "
        "identidade aqui — fica em NEEDS_SOURCE_REGISTRATION."),
}

SEM_IDENTIDADE = [
 dict(nome="BMTI — Borsa Merci Telematica Italiana, analisi di mercato cereali",
      rota="https://www.bmti.it",
      porque="reclamava IT-T10-002 no ITALY-SOURCE-MASTER-V1.json, sem cerca e "
             "sem evidencia. O numero ficou com o OpenStreetMap, que tem as "
             "duas coisas.",
      falta="SOURCE provada · OWNER provado · rota atual provada · exemplo "
            "real · dedupe · proximo numero contra ESTE atlas reconciliado"),
 dict(nome="ISTAT — commercio estero agroalimentare (import/export)",
      rota="https://esploradati.istat.it/coeweb  (a antiga "
           "www.coeweb.istat.it ENCERROU em 30/09/2025)",
      porque="reclamava IT-T10-003, que ficou com a Distribuzione per uso "
             "agricolo. A fonte existe e a rota mudou; a identidade nao se "
             "emite nesta missao.",
      falta="idem, mais a prova da rota nova"),
]


def g(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True,
                           encoding="utf-8", errors="replace").stdout


def fichas_de(ref):
    """{SOURCE_ID: texto do bloco} — lendo CERCAS, como o scanner as le.

    ⚠️ O SCANNER E EU LIAMOS COISAS DIFERENTES, e por isso eu criei fichas
    redundantes. Ele percorre TODAS as cercas ``` que tenham uma linha
    `SOURCE_ID:`, qualquer que seja o nivel do titulo acima. Eu partia o texto
    em blocos `#### ` — e as fichas que vivem sob `### ` (como a de T11 ·
    EVENTS, na linha 1243 do atlas da qualification) ficavam invisiveis para
    mim e visiveis para ele. Resultado: duplicata que a trava apanhou.

    Dois leitores da mesma coisa sao duas verdades. Agora leio cercas.
    """
    t = g("show", f"{ref}:{CAM}")
    linhas = t.splitlines()
    fora, dentro, campos, inicio = {}, False, [], 0
    for n, cru in enumerate(linhas):
        if cru.strip().startswith("```"):
            if dentro:
                decl = "\n".join(campos)
                m = re.search(r"^SOURCE_ID:\s*(.+?)\s*$", decl, re.M)
                if m:
                    alvo = sem_parenteses(m.group(1).split("#")[0])
                    ids = list(dict.fromkeys(ID.findall(alvo)
                                             + expandir_faixas(alvo)))
                    # o bloco inteiro: do titulo acima da cerca ate ao fim dela
                    topo = inicio
                    while topo > 0 and not linhas[topo].lstrip().startswith("#"):
                        topo -= 1
                    bloco = "\n".join(linhas[topo:n + 1]).rstrip()
                    for x in ids:
                        fora[x] = bloco
                dentro, campos = False, []
            else:
                dentro, campos, inicio = True, [], n
            continue
        if dentro:
            campos.append(cru)
    return fora, t


def ficha_do_json(i, rec):
    """Ficha honesta a partir do JSON historico: o que ha, e NAO SEI no resto."""
    def v(*ks):
        for k in ks:
            x = rec.get(k)
            if isinstance(x, str) and x.strip():
                return x.strip()
        return "NÃO SEI"
    nome = v("SOURCE_NAME")
    titulo = f"#### {i} · {nome if nome != 'NÃO SEI' else '(nome não declarado)'}"
    campos = [
        ("SOURCE_ID", i),
        ("SOURCE_NAME", nome),
        ("SOURCE_OWNER", v("SOURCE_OWNER", "OWNER", "OWNER_ID")),
        ("COUNTRY", v("COUNTRY") if v("COUNTRY") != "NÃO SEI" else "ITALY"),
        ("TERRITORY", v("TERRITORY") if v("TERRITORY") != "NÃO SEI"
         else i.split("-")[1]),
        ("SOURCE_TYPE", v("SOURCE_TYPE")),
        ("URL", v("URL")),
        ("ACCESS_METHOD", v("ACCESS_METHOD")),
        ("REGION", v("REGION")),
        ("CROPS", v("CROPS")),
        ("TOPICS", v("TOPICS")),
        ("UPDATE_FREQUENCY", v("UPDATE_FREQUENCY")),
        ("HISTORICAL_DEPTH", v("HISTORICAL_DEPTH")),
        ("REAL_EXAMPLE", "nenhum preservado"),
        ("VERDICT", "NÃO SEI — ficha reconciliada de registo histórico"),
        ("RECONCILIADA_DE", "candidatas/ITALY-SOURCE-MASTER-V1.json "
                            "(identidade já emitida; nenhum número novo)"),
    ]
    larg = max(len(k) for k, _ in campos) + 2
    corpo = "\n".join(f"{k}:{' ' * (larg - len(k))}{val}" for k, val in campos)
    aviso = (
        "\n> **Ficha reconciliada, não descoberta.** Esta identidade foi emitida "
        "no registo histórico `ITALY-SOURCE-MASTER-V1.json` e nunca teve ficha "
        "em nenhum Atlas. Entra aqui **para não se perder** — o número está "
        "gasto e não pode ser reatribuído. Os campos são os que o registo "
        "histórico declarava; o que ele não dizia fica `NÃO SEI`, e não se "
        "preenche por plausibilidade.\n")
    return f"{titulo}\n\n```\n{corpo}\n```\n{aviso}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    uniao = set(CENSO["UNIAO"])
    f_qual, t_qual = fichas_de(QUAL)
    f_cool, _ = fichas_de(COOL)
    f_pass, _ = fichas_de(PASS)
    f_meu, t_meu = fichas_de("HEAD")

    print(f"base qualification : {len(f_qual)} fichas · {len(t_qual)} chars")
    print(f"cool-dijkstra      : {len(f_cool)}")
    print(f"passport           : {len(f_pass)}")
    print(f"atlas desta linha  : {len(f_meu)} (contidos na base: "
          f"{len(set(f_meu) & set(f_qual))})")
    perdidos = set(f_meu) - set(f_qual)
    if perdidos:
        print(f"  ⚠️ {len(perdidos)} desta linha NAO estao na base: {sorted(perdidos)}")

    # ── 1 · o texto base, com as 3 vencedoras substituidas/inseridas ──────
    texto = t_qual.rstrip()
    montagem = collections.Counter()
    tenho = set(f_qual)
    montagem["qualification"] = len(tenho)

    novas = []
    for i in ("IT-T10-001", "IT-T10-002", "IT-T10-003"):
        if i in tenho:                       # substituir pela vencedora
            texto = texto.replace(f_qual[i], f_cool[i])
            montagem["substituida_por_cool"] += 1
        else:
            novas.append((i, f_cool[i], "cool-dijkstra"))
            tenho.add(i)
            montagem["cool-dijkstra"] += 1

    for i in sorted(set(f_pass) - tenho):
        novas.append((i, f_pass[i], "passport-tags"))
        tenho.add(i)
        montagem["passport-tags"] += 1
    for i in sorted(set(f_meu) - tenho):
        novas.append((i, f_meu[i], "esta linha"))
        tenho.add(i)
        montagem["esta-linha"] += 1

    # ── 2 · as que so' existem no JSON historico ──────────────────────────
    mj = json.loads((RAIZ / "candidatas" /
                     "ITALY-SOURCE-MASTER-V1.json").read_text(encoding="utf-8"))
    por_id = {}

    def andar(o):
        if isinstance(o, dict):
            s = o.get("SOURCE_ID")
            if isinstance(s, str) and ID.fullmatch(s.strip()):
                por_id.setdefault(s.strip(), {}).update(
                    {k: v for k, v in o.items() if isinstance(v, str)})
            for v in o.values():
                andar(v)
        elif isinstance(o, list):
            for v in o:
                andar(v)
    andar(mj)

    faltam = sorted(uniao - tenho)
    for i in faltam:
        novas.append((i, ficha_do_json(i, por_id.get(i, {})), "master JSON"))
        tenho.add(i)
        montagem["master-JSON"] += 1

    # ── 3 · o cabecalho da reconciliacao e as secoes de pendencia ────────
    hoje = date.today().isoformat()
    orfaos = CLAS["FANTASMAS"]
    cab = f"""
---

## RECONCILIAÇÃO DO REGISTO DE IDENTIDADE — {hoje}

> **Este Atlas passou a conter a população inteira de `SOURCE_ID` já emitida
> pelo SINTONIA.** Antes, a identidade estava repartida entre este ficheiro em
> várias linhas de trabalho e o registo histórico
> `candidatas/ITALY-SOURCE-MASTER-V1.json`. O censo que sustenta esta
> reconciliação está em `build/source-registry-reconciliation/`.

```
identidades emitidas, no total              {len(uniao)}
    delas italianas                         {len([x for x in uniao if x.startswith('IT-')])}
SOURCE_ID criados nesta reconciliação       0
identidades perdidas                        0
colisões de identidade sem resolução        0
```

**De onde veio cada ficha** — por completude medida, nunca por a linha «vencer»:

| origem | fichas | por que |
|---|---:|---|
| `italy-source-qualification-v1` | {montagem['qualification']} | tinha 204 das 255; as 64 desta linha estão todas contidas nela |
| `cool-dijkstra-4agznu` | {montagem['substituida_por_cool'] + montagem['cool-dijkstra']} | as três fichas vencedoras do T10, com cerca e evidência |
| `passport-tags-italy-v1` | {montagem['passport-tags']} | inclui `IT-T4-002`, exclusiva daquela linha |
| `ITALY-SOURCE-MASTER-V1.json` | {montagem['master-JSON']} | identidades emitidas que nunca tiveram ficha |

**A autoridade não mudou.** Continua a ser este caminho de ficheiro. A
`qualification` foi base **material**, não autoridade nova.

### AS CINCO DECISÕES DE IDENTIDADE

"""
    for i, d in DECISOES.items():
        cab += (f"**`{i}`** é **{d['fica']}**.\n\n"
                f"Não é: {d['nao']}.\n\n"
                f"{d['nota']}\n\n")

    cab += """### O QUE NÃO RECEBEU IDENTIDADE, E CONTINUA NOMEADO

`NEEDS_SOURCE_REGISTRATION` — fontes reais que perderam a disputa por um número
e **não** recebem número novo nesta reconciliação:

"""
    for s in SEM_IDENTIDADE:
        cab += (f"- **{s['nome']}** · `{s['rota']}`\n"
                f"  - por que: {s['porque']}\n"
                f"  - falta, antes de poder receber identidade: {s['falta']}\n")

    cab += f"""
### IDENTIDADES GASTAS SEM FICHA — `SPENT_NO_RECORD`

{len(orfaos)} números são **usados pelo sistema** (ficheiros de amostra, runs,
relatórios) e **nunca foram declarados em ficha nenhuma**. Não são perda desta
reconciliação: são um buraco anterior a ela.

> ⚠️ **Estes números estão gastos.** Reatribuí-los faria as referências
> existentes apontar para a fonte nova. Registar a ficha que falta é trabalho
> de outra missão — aqui eles ficam **reservados e visíveis**.

```
{chr(10).join('  ' + ' · '.join(orfaos[k:k + 6]) for k in range(0, len(orfaos), 6))}
```

### PENDÊNCIA QUE NÃO TOCA IDENTIDADE — `TERRITORY_FIT_REVIEW`

- **`IT-T10-002`** (OpenStreetMap) vive em T10 · MARKET / TRADE / INDUSTRY, e a
  leitura estranha o encaixe. **A identidade não muda por isso.** `SOURCE_ID`
  emitido não se reclassifica por estética — quem quiser mover o território
  abre uma decisão própria, com o custo das referências medido antes.

### O QUE ESTA RECONCILIAÇÃO NÃO FEZ

- **não criou nenhum `SOURCE_ID`** — nem para a BMTI, nem para o comércio
  exterior do ISTAT, nem para a ARPAV (que já tem o seu);
- **não apagou nenhum número**, nem os de veredito negativo: um ID de fonte
  morta continua gasto;
- **não preencheu buracos de sequência.** Há 4 territórios com buraco, e
  buraco de sequência não é defeito: é identidade que foi gasta e retirada;
- **não declarou nenhum `DERIVA_DE`.** Medido: nenhum par da população prova
  «mesma fonte, dois números». Os candidatos eram membros da faixa
  `ES-T7-001..027` (27 fontes distintas numa ficha) e casos de **mesmo dono,
  fontes diferentes** — `IT-T10-004` é o registo do vinho e `IT-T10-005` o do
  azeite, ambos do ICQRF;
- **não reescreveu nenhuma branch** e não fez force-push.

---
"""

    # ── 4 · escrever ──────────────────────────────────────────────────────
    corpo_novo = "\n\n".join(t for _, t, _ in novas)
    final = texto + "\n" + cab + "\n" + corpo_novo + "\n"
    ATLAS.write_text(final, encoding="utf-8", newline="\n")

    # ── 5 · provar ────────────────────────────────────────────────────────
    # ⚠️ O VERIFICADOR TEM DE LER COMO O SCANNER, senao acusa perda que nao
    # existe. Ele lia blocos `#### ` e o `IT-T11-001` vive numa declaracao
    # agrupada sob `### ` — resultado: «LOST_SOURCE_IDS = 1» num atlas que
    # tinha a identidade toda. Tres leitores da mesma coisa deram tres
    # respostas; agora o montador, o verificador e o scanner leem CERCAS.
    #
    # E o dedupe DENTRO da ficha continua a ser preciso: `ES-T7-001..027` faz
    # o regex literal devolver `ES-T7-001` e a expansao devolve-o outra vez.
    # UMA ficha declara cada numero UMA vez; duplicata e' o mesmo numero em
    # DUAS fichas.
    f_final = {}
    t_final = ATLAS.read_text(encoding="utf-8")
    linhas_f = t_final.splitlines()
    dentro_f, campos_f = False, []
    for cru in linhas_f:
        if cru.strip().startswith("```"):
            if dentro_f:
                m = re.search(r"^SOURCE_ID:\s*(.+?)\s*$", "\n".join(campos_f),
                              re.M)
                if m:
                    alvo = sem_parenteses(m.group(1).split("#")[0])
                    for i in dict.fromkeys(ID.findall(alvo)
                                           + expandir_faixas(alvo)):
                        f_final[i] = f_final.get(i, 0) + 1
                dentro_f, campos_f = False, []
            else:
                dentro_f, campos_f = True, []
            continue
        if dentro_f:
            campos_f.append(cru)

    print()
    print("MONTAGEM:", dict(montagem))
    print(f"\natlas escrito: {len(t_final)} chars")
    print(f"identidades no atlas final: {len(f_final)}")
    print(f"populacao emitida:          {len(uniao)}")
    perdidas = uniao - set(f_final)
    extra = set(f_final) - uniao
    dobradas = {k: v for k, v in f_final.items() if v > 1}
    print(f"LOST_SOURCE_IDS = {len(perdidas)}  {sorted(perdidas)[:8]}")
    print(f"IDs a mais      = {len(extra)}  {sorted(extra)[:8]}")
    print(f"DUPLICADAS      = {len(dobradas)}  {dict(list(dobradas.items())[:6])}")
    json.dump({"MONTAGEM": dict(montagem), "NO_ATLAS": sorted(f_final),
               "PERDIDAS": sorted(perdidas), "EXTRA": sorted(extra),
               "DUPLICADAS": dobradas},
              open(PROVA / "atlas-final.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if perdidas or dobradas:
        sys.exit("!! o atlas nao fecha — nao se publica assim")


if __name__ == "__main__":
    main()
