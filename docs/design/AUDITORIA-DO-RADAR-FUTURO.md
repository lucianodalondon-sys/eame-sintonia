# Auditoria do Radar Futuro · o que ele faz hoje, medido

> Medição, não conserto. Nada foi alterado no Radar Futuro por esta auditoria.
> Cada afirmação abaixo foi verificada contra o ficheiro que a sustenta e passou
> por refutação adversarial independente; onde a refutação venceu, o número
> corrigido está escrito e o errado está nomeado.

---

## 0 · A primeira descoberta: «Radar Futuro» são DUAS coisas

E o próprio repositório já sabe disso. `italia-portale/audit/casa-gate.mjs:428`
tem um portão chamado `ONE_SURFACE_NAME_ONE_POPULATION`, e o comentário que o
justifica (`:410-413`) diz:

> «O menu chamava «Radar Futuro» a três registos IT-FUT- do pacote V21, e a casa
> chama «Radar Futuro» aos 45 ITFC. … **Intersecção de IDs: ZERO nos dois
> casos.** Dois universos disjuntos com o mesmo nome, a um clique da primeira
> dobra.»

O portão fez o seu trabalho: a vista do portal foi renomeada para *Archivio
segnali*, e «Radar Futuro» ficou reservado aos 44 ITFC de `casa.html`. Mas
qualquer resposta sobre «o motor do Radar Futuro» que não diga **de qual** está
a falar sai errada. São três superfícies.

| | superfície | população | onde vive |
|---|---|---|---|
| **A** | RADAR FUTURO canónico | 45 ITFC (44 renderizáveis) | `casa.html` |
| **B** | Archivio segnali | 3 `IT-FUT-` | `portale.html` |
| **C** | régua diagnóstica | 980 candidatos lidos | `audit/future-ruler.mjs` |

---

## 1 · `FUTURE_RADAR_OWNER`

```
FUTURE_RADAR_OWNER =
  A · italia-portale/client/upstream/IT-FUTURO-HANDOFF-LINHA-B-V1.json
      (DONO DO JULGAMENTO — congelado a montante, FORA deste repositório)
      + scripts/it_casa_dados.py  (EMPACOTADOR, nunca juiz)
  B · scripts/v21_ingest_b.py:384-387  (NORMALIZADOR de pass-through)
  C · italia-portale/audit/future-ruler.mjs  (RÉGUA, que se recusa a promover)
```

**Não existe, neste repositório, código que gere um caso futuro.** O handoff
declara-o na própria lei:

> `LEI` = «este handoff **NÃO recalcula julgamento nenhum**. Empacota o que já
> está congelado.»
> `CONGELAMENTO` = `707b684 · registo corrigido em 9560823`

E `it_casa_dados.py` **falha fechado** se discordar: `:550-552` levanta erro se
`len(ledger) != RF['RENDERABLE']`; `:556-558` se `PREPARAR`/`MONITORAR` não
baterem. Isso é uma virtude, não um defeito — só não é um motor.

---

## 2 · De onde nascem os casos futuros

**A ·** Nascem já julgados. Os 45 chegam com veredito completo:
44 em `LIMITACOES_POR_SINAL` (`ESTADO` / `ACAO` / `AVISO_OBRIGATORIO` /
`PORTFOLIO` / `LACUNAS`) e o 45.º já em `EXCLUIDOS`
(`{"ID":"ITFC-027","ESTADO":"DERRUBADO"}`). A cadeia que os produziu
(CANDIDATOS → JULGADOS → FICHAS → SINAIS → HANDOFF) **não está aqui**:
`UPSTREAM-PINS.json` aponta para a branch `sprint/publicacao-unica-5855cad`, e
este repositório só confere o SHA.

**B ·** Pass-through. `v21_ingest_b.py:384-387` lê
`FUTURE-RADAR/future-signals.json` do handoff anterior e passa `None` para data,
`[]` para alvo e região, `'NAO_SEI'` para escopo. O julgamento de maturidade
(`EMERGING_THEME`, `SCIENTIFIC_SIGNAL`) é literal em
`data/samples/ITALY-RADAR-DO-FUTURO-V1.json`, ficheiro que se declara *«derivado,
SOMENTE de leitura da branch claude/sintonia-italy-pilot-b1l401 via git show»*.

`IT-FUT-003` não tem `LEGACY_ID` e não nasce de tema nenhum: não existe
`FT-IT-003` no repositório, e `THEMES_COUNT` é 2. **De onde ele veio: NÃO SEI.**

---

## 3 · `FUTURE_RADAR_INPUT_FAMILIES` e `FUTURE_RADAR_MISSING_FAMILIES`

```
FUTURE_RADAR_INPUT_FAMILIES
  A · ZERO das 26 famílias do acervo.
      it_casa_dados.py abre 9 ficheiros; famílias de inteligência entre eles: 0.
      Alimentam o bloco RADAR_FUTURO: 2 (o handoff + IT-TOP3-SENSORES-V1).
  B · 2  —  FUTURE-SIGNALS (3 registos) e SOURCES (189).
  C · 13 chaves de coleção lidas pela régua.

FUTURE_RADAR_MISSING_FAMILIES  (para a superfície A, que é «o» Radar Futuro)
  ACTIVE-INGREDIENTS · AGROMET-CONDITIONS · CLIENT-SAFE-CROSSINGS ·
  COMPETITOR-ACTIVITIES · CROP-ECONOMIC-WEIGHT · CROP-WINDOWS ·
  CURRENT-FIELD-SIGNALS · EVENTS · FUTURE-EVENTS · FUTURE-SIGNALS ·
  MARKET-OBSERVATIONS · NEWS · PRODUCT-ACTIVE-INGREDIENTS ·
  PRODUCT-RELATIONSHIPS · PRODUCTS-COMMERCIAL · PRODUCTS-REGULATORY ·
  PUBLIC-CHANNELS · PUBLIC-VOICES · REGULATORY-FUTURE ·
  REGULATORY-FUTURE-FACTS · RELATIONSHIPS · RESEARCHERS · RESISTANCE ·
  SCIENCE · SOURCES              ... isto é, TODAS.
  + fora do pacote: o corpus SENSOR-PILOT (vídeo/transcrição) e o censo
    IT-CATALOGO.

FUTURE_RADAR_FULL_ACERVO_SCAN = NÃO
```

### A régua lê, e depois mata com uma constante

`future-ruler.mjs` carrega 980 candidatos. **737 deles — 75,2% — são
descartados por um literal `false` escrito no código, não pelos seus dados**:

| coleção | registos | como morre |
|---|---:|---|
| `competitorActivities` | 577 | `decisional: false` |
| `scienceRecords` | 88 | idem |
| `agrometConditions` | 44 | `touchesAdama: false`, `decisional: false` |
| `regulatoryFuture` | 28 | `decisional: false` |

Ler uma coleção e matá-la com uma constante é pior do que não a ler: parece
consulta e não é.

> **UMA FAMÍLIA CARREGADA E MORTA POR CONSTANTE NÃO FOI CONSULTADA.
> FOI CITADA.**

E `EVENTS` (40 registos) viaja até ao browser sem um único leitor: é a única das
26 famílias do pacote sem gancho `V21()` em `italy-app-model.js`.

---

## 4 · Como ele determina os oito campos

**Superfície A — os 44 cartões renderizáveis:**

| campo | presente em |
|---|---|
| data | **0 / 44** — o campo não existe |
| janela | **0 / 44** — há um literal de coleção, `ORIZZONTE: 'PROSSIMA_CAMPAGNA'`, escrito à mão em `it_casa_dados.py:811` |
| antecedência | **0 / 44** |
| região | **0 / 44** |
| cultura | **0 / 44** |
| problema/alvo | **0 / 44** |
| produto ADAMA (nome) | **0 / 44** — só códigos de classe |
| departamento | **0 / 44** — `REPARTO` pertence às oportunidades correntes, não a esta superfície |

O produto ADAMA existe apenas como vocabulário fechado:
`PORTFOLIO_PAR_ADAMA` YES 22 · NO 19 · UNKNOWN 3;
`CLASSE` MEDIDO_EXISTE 20 · MEDIDO_ZERO 16 · CEGO_SEM_CLASSE 3 ·
DECLARADO_UNKNOWN 3 · EVIDENCIA_CONGELADA 2;
`ROTA` permitida 36 · proibida 8.

E o próprio handoff declara sete campos **obrigatórios** no cartão
(`F_DATA_DO_FATO`, `F_DATA_DA_PUBLICACAO`, `F_REGIAO`, `F_CULTURA`, `F_ALVO`,
`T_JANELA_DE_APLICACAO`, `T_BASE_DA_JANELA`) sob a lei *«um cartão a que falte
qualquer um destes não é renderizável»* — e **nenhum deles viaja no handoff**.
A lei está escrita; o campo não chegou.

**Superfície B — os 3 sinais:** data UNKNOWN 3/3 · janela UNKNOWN 3/3 ·
antecedência ausente 3/3 · região UNKNOWN 2/3 (`UE` em 1) · cultura resolvida
2/3 · alvo UNKNOWN 3/3.

---

## 5 · Casos futuros criados só por aritmética de datas

```
FUTURE_CASES_BASED_ONLY_ON_DATE_MATH = 19
   7  oportunidades O5_REGULATORY_PREPARATION
  12  registos de FUTURE-EVENTS (de 14)
```

**Os 7.** `scripts/v21_oportunidades.py:216-218` — `estado_temporal()` devolve
`FUTURE_PREPARATION` **na primeira linha**, por arquétipo, antes de ler `dias`
ou `tem_janela`. Nos 7: `SIGNAL_DATE` nulo, `WINDOW_STATE` UNKNOWN, e as quatro
famílias de evidência (`ACTIVE_INGREDIENT`, `LABEL_USE_RELATIONSHIP`,
`REGULATORY_FUTURE_FACT`, `REGULATORY_PRODUCT`) são **todas** de autorização.
**Zero registos que observem coisa alguma.** Seis dos 7 estão
`OPPORTUNITY_CONFIRMED` com zero portões bloqueantes.

**Os 12.** Datados `2026-09-02` — que é exatamente o dia de leitura do coletor
**e** o corte do futuro, admitido pelo `>=` em `v21_datas.py:91`. Nenhum dos 12
tem `DATE` ou `PERIOD` de topo: a data saiu por regex de prosa livre, no mesmo
ficheiro que promete *«Só campos declarados; prosa nunca vira data»*.

> **UMA DATA FUTURA SOZINHA NÃO CRIA UMA OPORTUNIDADE.**
> Aqui, doze vezes, o dia em que se leu virou a prova de que era futuro.

---

## 6 · Escolha de produto antes de varrer o portfólio

```
FUTURE_CASES_WITH_INCOMPLETE_ADAMA_SCAN = 14 de 44   (superfície A)
   8  PORTFOLIO_LIMITED, declarado pelo próprio handoff
   3  CEGO_SEM_CLASSE
   3  DECLARADO_UNKNOWN
   + 0/44 carregam sequer o NOME de um produto
```

Na superfície das oportunidades, o caminho futuro tem **três** pontos de corte,
não um: `produtos[:12]` (`:574`), `prods[:6] + rot[:4]` (`:776`) e a fusão
primeiro-fato-ganha (`:815-823`). **Os 7 casos futuros passam todos pelo corte
de `:776`**; 3 perdem portfólio na fusão (`MERGED_FROM` 38, 1, 1 — quarenta dos
47 fatos colapsados); e 1 perde provadamente um produto ao teto de 12
(videira/FOLPET, 13 → 12, **VINIFOL WDG** cai) enquanto
`NUMBERS.PRODUTOS_ADAMA` continua a dizer 13.

> **O CARTÃO DIZIA TREZE E MOSTRAVA DOZE.**

---

## 7 · Convergência entre fontes independentes

O contrato exige-a, e com todas as letras
(`RADAR-DO-FUTURO-CONTRACT-V1.json`, estado 2):

> `EXIGE`: «INDEPENDENT_LAYERS >= 2, de tipos diferentes — ciência, regulatório,
> campo, portfólio, norma ou rede técnica. **Duas publicações não são duas
> camadas.**»

**E esse número nunca atravessa para nada que se sirva.** `INDEPENDENT_LAYERS`
existe só no artefacto do analista (`ITALY-RADAR-DO-FUTURO-V1.json`: FT-IT-001 = 3,
FT-IT-002 = 1); está **ausente** do handoff a montante, do pacote V2.1, do
modelo e do ecrã. Quem o lê é um teste unitário sobre dados escritos à mão — e
mais ninguém.

```
FUTURE_CASES_WITH_MULTISOURCE_CONVERGENCE
  A · 0 de 44 linhas carregam id, contagem de fonte ou de evidência.
      Por sinal: NÃO SEI — as fichas não estão neste repositório.
      Sabe-se que ITFC-016 e ITFC-018 saem do MESMO documento (D9rKf6p1YY0).
  B · 3 de 3 trazem 2 SOURCE_IDS distintos — mas IT-FUT-002 traz duas fontes
      enquanto o seu tema de origem declara INDEPENDENT_LAYERS 1 e CAMADAS
      ['ciencia']. Duas fontes, uma camada: é exatamente o que o contrato proíbe
      chamar de convergência.
  C · o quinto portão da régua, «PROVA RISOLVIBILE», é um teste de existência
      (>= 1), não de convergência: `c.gates.proof = !!c.sourced`.

  futureEvents      14/14 → 1 fonte cada
  regulatoryFuture  28/28 → 1 fonte cada
```

### Os quatro estados que o contrato pede

O contrato distingue os seis estados da régua de maturidade e proíbe as palavras
`PREDICTION`, `FORECAST`, `SCORE`. **Isso é honrado nas superfícies B e C.**
Na superfície A — a que se chama «Radar Futuro» — o vocabulário servido é outro
e mais pobre: `ESTADO` (PARCIAL 40 / SINAL_COMPLETO 4) e `ACAO` (PREPARAR 23 /
MONITORAR 21 / AGIR_AGORA 0). **Não há estado que distinga «facto futuro
confirmado» de «hipótese/monitorar»**, e não há `NÃO SEI` como estado — ele
existe só como contagem de prosa: 266 defeitos e 362 «não sabemos» declarados
em 44 linhas.

`AGIR_AGORA = 0` é decisão de regra, não falta de leitura, e o pacote di-lo:
*«nessuno di questi è un'opportunità di oggi: AGIRE ORA è zero per decisione
della riga»*. Isso é correto e deve continuar.

---

## 8 · Sinais por família, nos casos futuros

```
FUTURE_CASES_WITH_VIDEO_OR_TECHNICAL_SIGNAL = 3 de 44
   e apenas 1 é EXECUTABLE (2 são NOT_EXECUTABLE)

FUTURE_CASES_WITH_SCIENCE_SIGNAL
   A · 0 de 44   — não há campo de ciência na superfície
   B · 2 de 3    — FT-IT-001 e FT-IT-002 declaram SCIENCE_SIGNAL PRESENTE;
                   IT-FUT-003 não tem tema, logo NÃO SEI

FUTURE_CASES_WITH_COMPETITOR_SIGNAL = 0
   competitorActivities (577 registos) é lido pela régua e morto por
   `decisional: false`; não existe em A nem em B.
```

---

## 9 · Os portões

```
FUTURE_RADAR_CROSS_INTELLIGENCE_GATE = FAIL
```

Falha por três motivos, cada um provado acima:

1. A superfície canónica **não consulta família nenhuma do acervo** — não é que
   procure e não ache: não procura.
2. **737 registos** são carregados pela régua e mortos por constante, o que
   torna «não encontrado» indistinguível de «não olhei».
3. A convergência que o contrato exige (`INDEPENDENT_LAYERS >= 2`) **não é
   avaliada por nada que se sirva**; e onde há duas fontes, uma delas é a mesma
   camada.

E, deliberadamente, **não** falha por isto: `AGIR_AGORA = 0`, a recusa de
promover, e as palavras de previsão proibidas estão certas e devem ficar.

---

## 10 · O que esta auditoria NÃO prova

- Não prova que algum caso futuro esteja errado. Prova que 44 deles não trazem
  os campos com que se poderia julgá-los aqui.
- Não prova que a cadeia a montante não tenha consultado o acervo. **NÃO SEI**:
  as fichas não estão neste repositório, e o handoff só traz o veredito.
- Não prova que `IT-FUT-003` seja inválido. Prova que não se sabe de onde veio.
- Não mediu a superfície A campo a campo contra o acervo, porque a superfície A
  não tem campos de cultura, alvo, data ou região para cruzar. **Ausência de
  chave não é ausência de dado** — e também não é ausência medida.
