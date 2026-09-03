# IT-T4-001 · O registro italiano contra o V2.1

> Avaliação da evidência regulatória vinda da branch `claude/adama-italia-scrape-qov10l`
> (`docs/adama/PORTFOLIO-ADAMA-ITALIA.md`, dado em `data/samples/IT-T4-001/`).
>
> **Nada aqui foi escrito à mão.** Todo número sai de
> `scripts/v21_adama_registro_validar.py`, que reconta dos arquivos a cada execução.
> Para conferir: `python3 scripts/v21_adama_registro_validar.py`

Fonte: Ministero della Salute — Banca dati dei prodotti fitosanitari,
arquivo `PROD_FTS_6_20260831.csv`, versão do dado `20260831`, lido em `2026-09-02`.

---

## 1 · A validação crítica: o que "vivo" quer dizer

O relatório diz **163 autorizações vivas hoje**. O número é verdadeiro. A palavra
**"hoje" não é.**

A definição está no código do coletor, não na prosa:

```python
VIVOS = ("Autorizzato", "Ri-registrato", "Rinnovato")
vivo = r["stato_amministrativo"].startswith(VIVOS)
```

`vivo` lê **um único campo** — o estado administrativo — e **nunca abre a data de
validade**. Por isso um produto pode estar `vivo=true` com a validade vencida.

### A resposta, entre as cinco hipóteses levantadas

| Hipótese | Veredito | O que mede |
|---|---|---|
| estado administrativo | **É ISTO** | o campo publicado no registro |
| validade formal da autorização | não | 15 dos 163 já venceram |
| estado de publicação da base | em parte | é o estado publicado, e ele atrasa |
| período de carência | **não** | 0 dos 15 tem decreto de revogação |
| erro de classificação do coletor | **no rótulo, não na extração** | o campo é lido fielmente; chamá-lo de "vivo hoje" é que não se sustenta |

### Como se prova que é atraso, e não carência

| Medição | Resultado |
|---|---|
| Existe estado `Scaduto` no registro? | sim, **14** registros |
| Validade mais recente entre os `Scaduto` | **2011-06-12** — 5.559 dias antes do CSV |
| Validade mais antiga entre os "vivos" | **2026-08-15** |
| Há sobreposição entre as duas faixas? | **não** |
| Os 15 vencidos têm decreto de revogação? | **0 de 15** |
| Controlo: os 425 `Revocato` têm decreto? | **424 de 425** |

O maquinário de revogação funciona — 424 de 425 têm data de decorrência. Ele
simplesmente **não foi aplicado** aos 15. E o estado `Scaduto` só aparece em
registros vencidos há mais de quinze anos. Logo o registro **não move um produto
para vencido quando a data passa**; ele espera um ato administrativo.

> **ESTADO ADMINISTRATIVO ≠ VALIDADE FORMAL.**
> O registro diz quem não foi revogado. Não diz quem está válido hoje.

**Não publicar `CURRENTLY AUTHORIZED` / `ACTIVE` a partir deste campo.** O próprio
dataset já traz a camada certa no campo `camada`: `REGISTERED PRESENCE`. A prosa
do relatório é que contradiz o dado.

### São 15, não 3

O pedido citava ANTERLEX, BADGER 45% WG e BLAISE ULTRA. São **15**:

| Validade | Nº registo | Produto | Estado administrativo |
|---|---|---|---|
| 2026-08-15 | 013899 | DAUPHIN 45 | Ri-registrato |
| 2026-08-15 | 015232 | CUSTODIA ULTRA | Autorizzato |
| 2026-08-15 | 015629 | BADGER 45% WG | Ri-registrato |
| 2026-08-15 | 015630 | CARSON 45% WG | Ri-registrato |
| 2026-08-15 | 017358 | BLAISE ULTRA | Autorizzato |
| 2026-08-15 | 017688 | ANTERLEX | Autorizzato |
| 2026-08-15 | 017689 | MOXYL MK | Autorizzato |
| 2026-08-15 | 017690 | VANTEX | Autorizzato |
| 2026-08-31 | 008259 | LAMDEX EXTRA | Ri-registrato |
| 2026-08-31 | 013402 | LUMA-KL | Ri-registrato |
| 2026-08-31 | 013560 | FORZA | Ri-registrato |
| 2026-08-31 | 013590 | NINJA | Ri-registrato |
| 2026-08-31 | 015275 | DURAVIS | Autorizzato |
| 2026-08-31 | 017687 | ELTIRA | Autorizzato |
| 2026-08-31 | 018111 | ARRODIM | Autorizzato Art. 34 Reg. 1107/2009 |

Oito deles já estavam vencidos **na data de publicação do próprio CSV** (31/08).

---

## 2 · O cruzamento pedido

Chave de junção: **número de registo**, normalizado. Nunca por nome aproximado —
nome de produto repete entre titulares e muda de grafia entre fontes.

```
MATCHED EXISTING PRODUCTS = 163   (100% dos 163 "vivos"; 0 ficaram de fora)
NEW REGULATORY ENTITIES   = 439   (425 Revocato + 14 Scaduto) — nenhum deles vivo
CONFLICTS                 =   0   STATUS 0 · EXPIRY 0 · AUTHORIZATION_HOLDER 0
DUPLICATES                =   0   nos dois lados (163 e 602 números distintos)
EXPIRY-STATE CONFLICTS    =  15   e o V2.1 já carrega os mesmos 15
CORRECTIONS REQUIRED      =   4   ver §4
```

**Os 163 "vivos" são exatamente os 163 que o V2.1 já tem.** Casam um a um pelo
número de registo, com zero divergência em estado, validade e titular. Não é
evidência nova: é a **mesma evidência por outra porta** — o V2.1 veio do servlet
de etiqueta (`fitosanitari.salute.gov.it`), este veio do open data
(`dati.salute.gov.it`). Duas rotas independentes, mesmo resultado.

Isso tem valor, mas não o valor de "descoberta": vale como **corroboração de rota**.

O que é genuinamente novo são os **439 registros históricos**, que o V2.1 não tem —
o universo regulatório completo do grupo ADAMA, e não só a fatia viva.

---

## 3 · Um defeito no coletor novo: o separador

As 38 divergências aparentes de substância ativa **não são conflito de dado**.
São um bug:

```python
[s.strip() for s in r["sostanze_attive"].split("+") ...]   # o CSV separa com "|"
```

| | coletor novo | V2.1 |
|---|---|---|
| produtos vivos com substâncias coladas numa string | **38 de 163** | **0** |
| substâncias ativas distintas | 55 "combinações" — **22 delas são pares colados** | **53** |

`ACTIGAN DFF` sai como `['PENDIMETHALIN|DIFLUFENICAN']` — uma substância, em vez de
duas. **O V2.1 está certo e o coletor novo está errado.**

> ⚠️ **Não sobrescrever `ACTIVE_INGREDIENTS` do V2.1 com este campo.** Seria trocar
> o correto pelo errado. As "55 combinações de substância ativa" do relatório não
> são 55 substâncias — são 53.

Mais dois defeitos do coletor, menores mas reais:

- **`dias_ate_vencimento` usa `date.today()`.** Re-rodar amanhã muda o número sem
  que o dado tenha mudado. Os "64 vencendo em 180 dias" são função da hora em que
  se rodou, não da versão `20260831`.
- **`vencendo_em_180_dias` filtra `0 <= dias <= 180`.** Os 15 já vencidos têm dias
  negativo e são **silenciosamente descartados** — não aparecem em lugar nenhum do
  resumo. O risco maior é o que some primeiro.

---

## 4 · O que isto revelou dentro do V2.1

Este é o achado mais caro da avaliação, e ele não é sobre o artefato novo.

Como `STATUS` e `EXPIRY` casam perfeitamente nos 163, **o V2.1 carrega os mesmos 15
registros vencidos** — e os carrega assim:

| | |
|---|---|
| `PRODUCTS-REGULATORY` com `EXPIRY` < 2026-09-02 | **15 de 163** |
| desses, `CLIENT_SAFE=true` | **15** |
| `QA_STATUS` | `EVIDENCE_DOCUMENTED` nos 15 |
| desses, com `IN_PUBLIC_CATALOG_FLAG=true` | **2** (LAMDEX EXTRA, ARRODIM) |
| campo que avisa que a validade passou | **nenhum** |

Uma tela que filtre `CLIENT_SAFE=true` — que é a regra do README — mostra estes 15
como autorizados, ao lado de um `EVIDENCE_STATUS_WHY` que diz *"fato lido em
documento oficial, com fonte e data"*. Está tudo correto e ainda assim a leitura
que chega ao cliente é falsa, porque falta o campo que separa **estado
administrativo** de **validade na data de referência**.

**CORRECTIONS REQUIRED:**

1. `PRODUCTS-REGULATORY` precisa de dois campos novos: `ADMINISTRATIVE_STATE_IS_LIVE`
   e `VALIDITY_EXPIRED_AT_REFERENCE`, com `REFERENCE_DATE` pinada na versão do dado.
2. Os 15 não devem perder `CLIENT_SAFE` — o fato *é* documentado. Devem ganhar a
   ressalva que hoje falta. **Rebaixar não é a correção; a correção é dizer a
   verdade inteira.**
3. `REGULATORY-FUTURE` hoje tem 28 registros e **nenhum** cita número de registo.
   Os 64 vencimentos nos próximos 180 dias existem no V2.1 (medidos: 64 com
   `EXPIRY` entre 2026-09-02 e 2027-03-01) e não estão ligados a essa coleção.
4. A contagem de substâncias ativas do relatório novo (55) não deve entrar em
   lugar nenhum: são 53.

---

## 5 · O que entra, e como

O payload validado está em
`data/samples/IT-T4-001/IT-T4-001-enriquecimento-validado.json`, carimbado
`QA_STATUS: QA_UNREVIEWED` e `CLIENT_SAFE: false` — porque ainda não foi aplicado
nem conferido registro a registro. **O portão vale para o que nós mesmos
produzimos, ou não é regra.**

Enriquecimento que é ganho real (não está no V2.1):

| Campo | Cobertura nos 163 |
|---|---|
| `CONCENTRATION_PER_100G` | **162/163** — o V2.1 tem **0/163** |
| `REGISTERED_AT` (data de registo) | 163/163 |
| `FORMULATION_CODE` | 163/163 |
| `PARALLEL_IMPORT` | 163/163 |
| `HAZARD_STATEMENTS` | 83/163 |
| universo histórico (`Revocato`/`Scaduto`) | **439 registros novos** |

> ⚠️ **A concentração também vem separada por `|`, e emparelha posição a posição
> com as substâncias ativas.** `ACTIGAN DFF` traz
> `['PENDIMETHALIN','DIFLUFENICAN']` e `35.6 g|3.6 g` — 35,6 g do primeiro,
> 3,6 g do segundo. Emparelhar sem contar troca a dosagem de um ativo pela do
> outro. Por isso o payload carrega `CONCENTRATION_SEGMENTS` e o booleano
> `CONCENTRATION_PAIRS_WITH_ACTIVES`, medido registro a registro:
> **595 emparelham · 1 não emparelha · 6 sem concentração**.
> O que não emparelha é `018176 EDAPTIS` — 3 substâncias declaradas
> (MEFENPYR DIETHYL, MESOSULFURON-METHYL, PINOXADEN) e só 2 concentrações. Fica
> marcado como não-emparelhável em vez de emparelhado no chute.
>
> **EMPARELHAR SEM CONTAR É ADIVINHAR COM CARA DE PRECISÃO.**


### As leis que este dado não pode atravessar

- **UNIVERSO REGULATÓRIO ≠ CATÁLOGO COMERCIAL PÚBLICO.** São 163 autorizações
  administrativas e 51 produtos no catálogo. Nenhum dos dois sobrescreve o outro,
  e a interseção não é assumida.
- **TITULAR DE AUTORIZAÇÃO ≠ VENDEDOR.**
- **VENCIMENTO FUTURO ≠ OPORTUNIDADE COMERCIAL.** Os 64 vencimentos entram como
  entrada de `REGULATORY-FUTURE`, nunca como `OPPORTUNITIES` — que segue com 3
  registros e nenhum client-safe.
- **FONTE BLOQUEADA ≠ FONTE INEXISTENTE.** O site da ADAMA responde 403 por
  Akamai; o portfólio veio do registro que a empresa alimenta por lei. Rota
  fechada, evidência aberta.

### O que continua sem saber

- **cultura e alvo** — não estão neste dataset; vivem na *etichetta* de cada
  produto. Nada aqui infere cultura.
- **volume, preço, participação e prioridade interna** — nenhuma fonte pública
  sustenta.
- **a regra do atraso** — o atraso do `Scaduto` é observável, mas o Ministero não
  publica quando move um registro.
