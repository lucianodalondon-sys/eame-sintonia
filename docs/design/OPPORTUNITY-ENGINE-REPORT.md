# O motor de oportunidades · V1

> Todo numero aqui sai de `scripts/v21_oportunidades.py`, que roda no passo 5e da
> cadeia e reconta do proprio pacote a cada build.
> `BUILD_ID` desta leitura: `V21-99226fbb90dcdbc2`

## 1 · O que havia antes

Nada. `OPPORTUNITIES.json` trazia **tres fichas escritas a mao**, importadas
inteiras do handoff anterior (`LEGACY_CASE_ID: IT-HERO-001/002/003`), e a
evidencia delas era prosa — *"ver 01-DESIGN-READY/MARKET-PULSE/"*. Nenhum ID
canonico, nenhuma regra, nenhum portao, nenhuma pontuacao.

As tres `CLIENT_SAFE=false` nao eram regra estrita demais: eram o portao a
funcionar sobre `PROVENANCE: REAL_DERIVED`. E nasceram antes de existirem 2.030
pares de rotulo, 53 substancias ativas e 47 fatos regulatorios europeus.

> **FICHA ESCRITA A MAO NAO E MOTOR: E LEMBRANCA DE UMA LEITURA.**

Diagnostico: **conceitualmente errada e cega para a evidencia ja presente.**

## 2 · A lei do client-safe, que nao foi afrouxada

Uma oportunidade e **leitura nossa** sobre fatos de terceiros. Vale aqui a mesma
regra que ja governa os cruzamentos — e ela vale porque vale para o que nos
mesmos produzimos:

```
CLIENT_SAFE = false, em TODAS as 37.
RENDERABLE_WITH_METHOD = true nas 9 confirmadas.
```

Cada apoio citado em `EVIDENCE_IDS` passou pelo portao. A **juncao** nao passa, e
por isso vai a tela com o metodo declarado ao lado. Aumentar a contagem
rebaixando isso teria sido trocar a regra pelo numero.

## 3 · O resultado

| | |
|---|---:|
| **OPPORTUNITA CONFERMATA** · confirmed | **9** |
| **OPPORTUNITA DA VALIDARE** · to validate | **28** |
| total | 37 |
| duplicados colapsados | 40 |
| derrubados pelo red team | 17 |
| IDs de evidencia distintos citados | 515 |

### Por arquetipo
- `O1_FIELD_PRESSURE` — **11**
- `O2_MARKET_MOMENT` — **7**
- `O3_RESISTANCE_MOA` — **1**
- `O4_COMPETITIVE_OPENING` — **9**
- `O5_REGULATORY_PREPARATION` — **7**
- `O6_SCIENCE_TO_FIELD` — **2**

### Por estado
- `ACT_NOW` — **3**
- `FUTURE_PREPARATION` — **9**
- `PREPARE_NOW` — **6**
- `TO_VALIDATE` — **19**

### Por estado de produto
- `RELATED_PORTFOLIO` — **1**
- `VERIFIED_LABEL_MATCH` — **36**

## 4 · O que bloqueia, medido

- `RED_TEAM` — 17
- `A_GEOGRAFIA` — 7
- `C_TEMPO` — 7
- `F_PROCEDENCIA` — 3
- `D_PROBLEMA` — 2

O portao que mais bloqueia e o do **tempo**, e a causa e honesta: so 2 das 35
culturas de rotulo tem janela de aplicacao declarada, e as sete janelas do pacote
sao prosa (*"FECHADA — as janelas obrigatorias terminaram em junho"*). Onde nao ha
janela defensavel, `WINDOW = UNKNOWN` — nao se inventa uma.

Mas nao saber a janela de aplicacao **nao e** nao saber se o sinal e de hoje: o
boletim tem data, e `SIGNAL_DATE` a expoe ao lado. As duas coisas convivem, e o
portao C aceita qualquer uma.

## 5 · O red team so derruba

Nove perguntas, cada uma um defeito que este projeto ja cometeu: artefato de
fonte unica, geografia promovida, preco de processado virando mercado da cultura,
data regulatoria virando urgencia, comunicacao virando participacao de mercado,
resistencia documentada virando incidencia corrente, portfolio virando
verificacao de rotulo, artigo virando presenca no campo, voz virando incidencia.

**17 casos** foram rebaixados por ele. Nenhum foi confirmado por ele —
o red team nao confirma; so derruba.

## 6 · O que este motor nao faz

- Nao infere demanda de revenda, sell-in, estoque, pedido nem pipeline interno.
- Nao transforma data regulatoria em risco: O5 nasce `FUTURE_PREPARATION`.
- Nao junta por texto: toda evidencia entra por ID canonico.
- Nao cria cartao novo para a mesma situacao — a identidade e deterministica
  (`arquetipo + cultura + alvo + geografia + janela`), e 40
  registros adicionais **reforcaram** casos existentes em vez de multiplica-los.
- Nao persegue numero: se a evidencia nao converge, o arquetipo devolve zero.
