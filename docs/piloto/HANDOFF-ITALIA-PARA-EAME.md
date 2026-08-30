# HANDOFF ITÁLIA → SINTONIA EAME

`COUNTRY = IT` · estado em **2026-08-30** · branch `claude/sintonia-italy-pilot-b1l401`

> Este documento entrega a Itália à sessão principal. **Não cria relação Espanha × Itália.**
> Declara apenas o que é comparável, e por quê. `CROSS_MARKET_RELATION = NOT_TESTED`.

---

## A · ITALY_COUNTRY_STATE

A Itália responde perguntas italianas sozinha. Cinco camadas medidas, todas com rota
reproduzível e evidência preservada:

| Camada | Fonte | Estado |
|---|---|---|
| REGULATÓRIO nacional | `IT-T4-001` Ministero — CSV/JSON/XML aberto | **GREEN** |
| RÓTULO oficial | `IT-T4-001-ETICHETTA` — servlet + PDF | **GREEN**, 163/163 |
| ESCALA nacional e regional | `IT-T1-001` ISTAT SDMX + `EU-T1-001` Eurostat | **GREEN** |
| CAMPO regional | `IT-T3-002/003/006` Vêneto, Lombardia, ERSA FVG | **GREEN** |
| NORMA regional | `IT-T3-LOTTA` decretos de lotta obbligatoria | **GREEN** |
| CIÊNCIA | `IT-T5-001` OpenAlex dirigido | **GREEN** |
| SITE do fabricante | `IT-T9-001` adama.com | **BLOQUEADA** — 403 de WAF |

**Custo acumulado das duas rodadas italianas: US$ 0,00.** Nenhuma rota paga.

---

## B · ITALY_REGULATORY

```
ITALY_REGISTRATIONS_TOTAL      17.695
ITALY_CURRENT_AUTHORIZED        3.712
ITALY_DISTINCT_HOLDERS            576

ADAMA_GROUP_IT_CORE               602 registros · 163 vigentes · 53 substâncias ativas
ADAMA_IT_LEGAL_ENTITY             240 registros ·  85 vigentes · 36 substâncias
ADAMA_IT_ADJACENT                  31 registros ·   0 vigentes  (ambiguidade imaterial)

EXPIRING_180D                      58
EXPIRING_CALENDAR_6M               71     ← a convenção muda a resposta em 13 registros
EXPIRING_CALENDAR_12M             104
EXPIRED_BUT_ACTIVE_STATUS           8     REGULATORY_STATUS_LAG / INVESTIGATE
OFFICIAL_LABELS                163/163    100 %
```

**A identidade do titular não é uma string.** Cinco razões sociais declaram, no próprio
campo `indirizzo_sede_amministrativa`, a sede `C/O ADAMA ITALIA S.R.L., VIA ZANICA 19,
GRASSOBBIO`. Isso é evidência publicada pela fonte. Duas outras que *parecem* do grupo
ficam fora, contadas à parte, e somam zero vigentes.

---

## C · ITALY_PORTFOLIO

O rótulo oficial trouxe o que o CSV não tem: `Coltura × Patogeno × Dose × Intervallo ×
N° max applicazioni` + grupo HRAC/FRAC/IRAC.

```
CATEGORIA (163 vigentes)   DISERBANTE 77 · FUNGICIDA 46 · INSETTICIDA 16 ·
                           DISERBANTE-ANTIDOTO 13 · outros 11
FUNGICIDA                  metade cita VIDEIRA · ZERO citam MILHO
MILHO                      36 produtos — 24 herbicidas · 9 inseticidas · 0 fungicidas
MODE_OF_ACTION             declarado em 36 % dos rótulos (fail closed, não permissivo)
```

---

## D · ITALY_CASES — `ITALY-HERO-CASES-V1`

| Caso | Convergência | Horizonte |
|---|---:|---|
| `IT-HERO-001` videira × flavescência (vetor *Scaphoideus titanus*) × **Vêneto** + Lombardia | **5/5** | MONITORAR AGORA + PRÓXIMO CICLO |
| `IT-HERO-002` milho × piralide/*Diabrotica* × **FVG** (sinal) e vale do Pó (escala) | **5/5** | MONITORAR AGORA + PREPARAR |
| `IT-HERO-003` portfólio × calendário de vencimentos × nacional | 3/5 | **AGIR AGORA** |
| `IT-DEMO-001` oliveira × *Bactrocera* × Vêneto | — | **não é caso** — ver abaixo |

**`IT-DEMO-001` fica registrado como demonstração de capacidade, não como caso.** Tem o
sinal de campo mais fino do país (11 sub-áreas nomeadas, 3–6 %, 26/08/2026) e duas coisas
que o desqualificam: o Vêneto tem **0,5 %** da oliveira italiana, e **nenhum** dos 163
rótulos nomeia *Bactrocera oleae*.

---

## E · ITALY_WINDOWS

```
IT-HERO-001  APPLICATION_WINDOW   CLOSED_FOR_2026   (obrigatórias, junho/2026)
             MONITORING_WINDOW    OPEN              (sintoma foliar, ago–set)
             NEXT_CYCLE           TO_BE_CONFIRMED · PREPARE_BY 2027-05-31

IT-HERO-002  APPLICATION_WINDOW   OPEN_BUT_NARROW   (só semeadura tardia e 2º raccolto)
             MONITORING_WINDOW    OPEN              (armadilhas + ovaturas)
             NEXT_CYCLE           ANCHORED_BY_SOURCE

IT-HERO-003  APPLICATION_WINDOW   NOT_APPLICABLE
             MONITORING_WINDOW    OPEN              (próxima versão do open data)

TODOS        COMMERCIAL_CLOCK     NÃO SEI — e nenhuma ação proposta depende dele
```

**As duas janelas do caso da videira não coincidem, e é a distinção mais cara desta
branch.** A que está aberta é de reconhecimento de sintoma; a de aplicação ao vetor
fechou em junho. Tratá-las como uma só fabricaria urgência.

---

## F · ITALY_ACTIONS

| Área | Ação | Horizonte |
|---|---|---|
| REGULATORY / PORTFOLIO | revisar as 71 autorizações que vencem em 6 meses, com atenção às 7 de 31/08 e às 13 concentradas em 2027-02-28 | **AGIR AGORA** |
| REGULATORY / PORTFOLIO | investigar as 8 vigentes com vencimento passado (`STATUS_LAG`) | **AGIR AGORA** |
| MARKET DEVELOPMENT | monitorar sintoma de flavescência no Vêneto (ago–set) | MONITORAR AGORA |
| MARKET DEVELOPMENT | acompanhar o pico de ovideposição de piralide no FVG, com o limiar publicado | MONITORAR AGORA |
| SCIENCE | cluster de micotoxina em milho — 208 trabalhos, autores com ORCID e atividade em 2026 | PREPARAR |
| MARKETING | material técnico de manejo de resistência com os grupos HRAC/IRAC do próprio rótulo | PREPARAR |
| MARKET DEVELOPMENT | preparar o ciclo 2027 da flavescência antes de 31/05 | PLANEJAR PRÓXIMO CICLO |
| COMMERCIAL | **nada a propor** — sem dado interno, qualquer ação seria fabricada | — |

---

## F.1 · A INVERSÃO DA COBERTURA — o achado estrutural da rodada

A camada pública de sinal de campo italiana **não** é proporcional à área da cultura, e a
inversão foi medida em duas culturas ao mesmo tempo:

| | publica | fatia | não publica | fatia |
|---|---|---:|---|---:|
| Oliveira | Vêneto (28 boletins) | 0,5 % | Puglia | 31,2 % |
| Milho | Friuli-VG (10 boletins) | 6,7 % | Vêneto + Lombardia | 48,2 % |

A Puglia declara, no próprio portal agrometeo, que desde **11/04/2018** a seção de
fitopatologia **não é mais redigida** — competência em transferência para a ARIF, ainda
descrita como em curso. O sinal migrou para organizações de produtores.

**Consequência de produto, e ela vale para qualquer país:** todo sinal de campo tem de ser
publicado junto com a **fatia da cultura que representa**. Os dois hero cases italianos
carregam `SIGNAL_REGION_PCT_NATIONAL` por causa disto.

Artefato: `data/samples/IT-T3-LOTTA/IT-cobertura-campo-vs-area.json`

---

## G · ITALY_UNKNOWNS

1. **Renovação** de cada autorização que vence após 24/08/2026 — o open data ainda está
   na versão `PROD_FTS_6_20260824`; a próxima publicação resolve.
2. **Datas de 2027** da lotta obbligatoria — fixadas a cada ano por monitoramento.
3. **Campo nas três maiores regiões de milho** — Vêneto e Lombardia (48,2 %) foram medidas
   e **não** publicam boletim de milho; Piemonte (23,4 %) ficou `NOT_OBTAINED` porque a
   *bacheca* é renderizada por JavaScript.
4. **Campo em Calabria e Sicilia para oliveira** (31,1 % somadas) — não medidas. A Puglia
   (31,2 %) foi medida e não publica desde 2018.
5. **Catálogo comercial** — `adama.com` bloqueado; os ~52 produtos seguem `UNVERIFIED_INPUT`.
6. **Voz social** — não coletada, por decisão de ordem.
7. **Concorrentes** — não abertos.

---

## H · ITALY_COMPARABLE_DIMENSIONS

O que a Itália entrega numa forma que **poderia** ser comparada, quando a Espanha tiver o
equivalente medido. Isto é uma lista de dimensões, **não** um cruzamento.

| Dimensão | Itália tem | Comparável se a Espanha tiver |
|---|---|---|
| `REGULATORY_EXPIRY` por titular e data | sim — 163 vigentes, calendário completo | o mesmo recorte de titular, com convenção de janela declarada |
| `CROP × TARGET` de rótulo oficial | sim — 163/163 rótulos | rota equivalente de rótulo (o ROPF espanhol traz EPPO) |
| `MODE_OF_ACTION` declarado | sim — HRAC/FRAC/IRAC em 36 % | extração equivalente, com a mesma disciplina fail-closed |
| `MANDATORY_CONTROL_CALENDAR` | sim — flavescência, 2 regiões, com datas | equivalente espanhol de lucha obligatoria |
| `FIELD_SIGNAL` datado e sub-regional | sim — vite, olivo, mais | RAIF já é isso na Andaluzia |
| `CROP_AREA` regional | sim — ISTAT + Eurostat, validados entre si | MAPA ou Eurostat, com a mesma vintage de NUTS |
| `SUBSTÂNCIA` normalizada | parcial | já existe do lado espanhol |

**Candidatos anotados:** milho · cereais de inverno · videira × doença · e por molécula —
folpet, tebuconazol, azoxistrobina, glifosato, nicosulfurom, lambda-cialotrina aparecem
nos dois registros.

**`CROSS_MARKET_RELATION = NOT_TESTED` · `CROSS_MARKET_READY = NO`.**

---

## I · ARMADILHAS QUE A SESSÃO PRINCIPAL HERDA

Cada uma custou uma medição errada primeiro. Reabrir sem evidência nova é refazer o erro.

```
SYMPTOM WINDOW        ≠ APPLICATION WINDOW
READ FAILURE          ≠ NO LABEL              (14 ausentes → 0, só com espera)
NOT_FOUND             ≠ DOES NOT EXIST        (o milho tinha boletim; eu li a página errada)
SIGNAL QUALITY        ≠ REGIONAL WEIGHT       (melhor sinal, 0,5 % da cultura)
HOLDER STRING         ≠ ORGANIZATION
REGISTRATION          ≠ COMMERCIAL CATALOG
GENERIC TARGET        ≠ SPECIFIC TARGET
ROTATION CLAUSE       ≠ AUTHORIZED USE
NUTS 2006             ≠ NUTS 2021             (ISTAT × Eurostat: some o vale do Pó)
180 DAYS              ≠ 6 CALENDAR MONTHS     (13 autorizações de diferença)
STATUS FIELD          ≠ EXPIRY INTERPRETATION (atraso medido: ≥ 9 dias)
ENCRYPTED PDF         ≠ EMPTY DOCUMENT
COVERAGE UP           ≠ QUALITY UP            (MoA: 55 % errado → 36 % certo)
```

---

## J · O QUE PERSISTIR QUANDO HOUVER SUPABASE

`SUPABASE_PERSISTENCE = PENDING` — não há credencial neste ambiente e não se fingiu
persistência. A convenção `IT/<source>/<run>/<asset>` já está gravada em cada registro de
rótulo. Ordem sugerida:

1. `IT-T4-001-portfolio-rotulo.json` — o gêmeo regulatório, é o ativo mais reutilizável
2. `IT-T4-001-etichette-manifest.json` + os 163 PDFs (33,8 MB, Storage, não Git)
3. `IT-T3-LOTTA/…` — o calendário normativo
4. `IT-T1-001-istat-area-regional.json` — a geografia
5. `ITALY-HERO-CASES-V1.json` — o pacote de casos
