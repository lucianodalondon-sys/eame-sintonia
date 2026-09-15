# CONTRATO — IT · ADAMA REFERENCE

> **Quem é autoridade para quê.** Nenhum consumidor desta casa deve ter de
> escolher entre o pacote `research/…-deep/` e o `HANDOFF-V2.1.zip`. Essa
> escolha acabou aqui, e foi feita campo a campo, não pacote a pacote.

```
CASA        referencia/adama/
CONSTRUTOR  fontes/adama_referencia.py
LEI DE BASE COL-LAW-206 (três identidades) · COL-LAW-034 (lei de identidade)
NASCEU EM   2026-09-15 · FASE 1C-2
```

---

## A TABELA DE AUTORIDADE

| conceito | ficheiro que MANDA | quantos | chave | de onde vem a prova |
|---|---|---:|---|---|
| **PRODUCT MASTER** | `PRODUCT-MASTER.json` | 51 | `ADAMA_PRODUCT_ID` | catálogo público + registo |
| **PORTFOLIO** | `PORTFOLIO.json` | 51 | `ADAMA_PRODUCT_ID` | `…-deep/PRODUCTS-COMMERCIAL.json` |
| **REGISTRATIONS** | `REGISTRATIONS.json` | 602 | `REGISTRATION_NUMBER` | `…-deep/PRODUCTS-REGULATORY.json` |
| **LABEL DOCUMENTS** | `LABEL-DOCUMENTS.json` | 141 | `DOCUMENT_ID` (sha256) | `…-deep/LABEL-MANIFEST.json` |
| **AUTHORIZED USES** | `AUTHORIZED-USES.json` | 2.030 | `USE_ID` | V2.1 `PRODUCT-RELATIONSHIPS.json` |
| **DOSES** | `DOSES.json` | 163 rótulos · 839 linhas | `REGISTRATION_NUMBER` | `data/samples/IT-DOSE-ROTULO/` |
| **ACTIVE INGREDIENTS** | `ACTIVE-INGREDIENTS.json` | 122 | `ACTIVE_INGREDIENT_ID` | `…-deep/ACTIVE-INGREDIENTS.json` |
| **PRODUTO × SUBSTÂNCIA** | `PRODUCT-ACTIVE-INGREDIENTS.json` | 203 | `RELATION_ID` | V2.1 `PRODUCT-ACTIVE-INGREDIENTS.json` |
| **SNAPSHOTS** (regulatório) | `SNAPSHOTS.json` | 3 | `SNAPSHOT_ID` | os três, declarados |
| **SNAPSHOTS DO CATÁLOGO** | `CATALOG-SNAPSHOTS.json` | 2 | `SNAPSHOT_ID` | `IT-ADAMA-CATALOG`, observado |
| **MEMBERSHIP OBSERVADA** | `PORTFOLIO-OBSERVATIONS.json` | 102 | `OBSERVATION_ID` | uma linha por produto × foto |
| **DRIFT DO PORTFOLIO** | `PORTFOLIO-DRIFT.json` | 1 | `SNAPSHOT_BEFORE`+`_NOW` | diff das duas fotos |
| **VOCABULÁRIO DE FONTE** | `SOURCE-ID-MAP.json` | 2 | `LEGACY_SOURCE_ID` | Atlas da FASE 1B |

**Os pacotes de origem não foram apagados nem movidos.** Continuam onde estavam,
e cada linha desta casa diz em `PROVENANCE.PROVING_ARTIFACT` de qual veio.

---

## `ADAMA_PRODUCT_ID` — O QUE ELE É, E O QUE ELE NÃO PODE SER

```
ADAMA-P-0001 … ADAMA-P-0051
```

É o `SINTONIA_STABLE_ID` da **COL-LAW-206** aplicado ao produto. Não é lei nova:
a lei já existia, e esta casa passou a cumpri-la para uma entidade que ainda não
a tinha.

```
SOURCE_NATIVE_ID     o id que a fonte dá        →  REGISTRATION_NUMBER (Ministero)
SINTONIA_STABLE_ID   o nosso, e não muda        →  ADAMA_PRODUCT_ID
CANONICAL_URL        um endereço — que muda     →  CATALOG_URL
```

**NÃO deriva de** número de registo · posição de linha · nome comercial · hash de
snapshot · nome de ficheiro · país. É emitido em série, **append-only**, e um ID
emitido **nunca muda, nunca se recicla e nunca se renumera** — nem quando o
produto sai do catálogo.

### Por que não tem `IT` dentro

O identificador anterior era `IT-PRODUCT-0045`. Parece identidade de produto e é
**o número da linha do registo italiano**. Levá-lo para Espanha obrigaria a
renumerar tudo, e o mesmo produto teria RG diferente por país.

```
A IDENTIDADE É DO PRODUTO. O PAÍS É PROVA DE PRESENÇA, E É ATRIBUTO.
```

Por isso `COUNTRY_SCOPE: ["IT"]` ao lado. Quando Espanha entrar: **se houver
prova** de que é o mesmo produto, reutiliza-se o ID e acrescenta-se `ES`; **se
não houver**, nasce outro ID e a reconciliação fica por fazer, declarada. Nunca
se afirma que um produto italiano é o mesmo produto espanhol sem prova.

### Como ele sobrevive a uma regeneração

Por `IDENTITY_ANCHORS` — o conjunto de coisas observadas que apontam para aquele
produto. Âncora nova acrescenta-se; o ID fica.

```
A ÂNCORA É COMO SE RECONHECE. NÃO É O QUE SE É.
```

É por isso que a âncora pode ser um endereço — que a COL-LAW-206 proíbe como
*identidade* — sem violar a lei.

---

## AS CINCO ENTIDADES, E POR QUE NÃO SE FUNDEM

```
PRODUTO  ≠  REGISTO  ≠  DOCUMENTO  ≠  USO AUTORIZADO  ≠  SUBSTÂNCIA ACTIVA
```

**Medido, não assumido:**

- **`017995`** é UMA autorização (`HIGHCARD`, ADAMA AGAN LTD, vence 28/02/2028)
  vendida sob **DOIS nomes de catálogo**: `Highcard®` e
  `Max-Ace® Rice Cropping Solution`. Não é duplicata, não é erro, não é
  transferência de titular. São duas ofertas comerciais da mesma autorização.
  O registo escreve `ADAMA_PRODUCT_ID: "MULTIPLE"` e lista as duas em
  `ADAMA_PRODUCT_IDS`. **Fundi-las apagaria um produto.**
- **`REGISTRATION → LABEL_USES`** é 1:N real: 102 registos, de 1 a **92** pares,
  média 19,9. E **61 registos do V2.1 têm zero** pares.
- **560 autorizações não têm produto de catálogo.** São reais, são ADAMA, e
  escrevem `ADAMA_PRODUCT_ID: "UNKNOWN"` — nunca um palpite.

### As cinco entidades legais ADAMA não se fundem

```
ADAMA ITALIA S.R.L.  ·  ADAMA MAKHTESHIM LTD  ·  ADAMA AGAN LTD
ADAMA DEUTSCHLAND GMBH  ·  ADAMA IRVITA N.V.
```

O titular é facto do registo. Fundi-los numa «ADAMA» apagaria quem responde
legalmente por cada autorização.

---

## O NOME: OBSERVADO E CANÓNICO, NUNCA UM NO LUGAR DO OUTRO

O símbolo `®` chegou a montante transformado na letra `R` — e **só no V2.1**, que
é o que o Portal serve. O pacote `…-deep/` já trazia o nome certo.

| o que o V2.1 publica | o que o registo tem | `NAME_STATE` |
|---|---|---|
| `NIMRODR 250 EW` | `NIMROD 250 EW` | `SIMBOLO_REGISTADO_LIDO_COMO_LETRA_R` |
| `APYZAR WG` | `APYZA WG` | idem |
| `COSAYRR 200 SC` | `COSAYR 200 SC` | idem |
| `GOLTIXR TOP 0` | `GOLTIX TOP` | idem — **dois** defeitos: o R e um zero pendurado |
| `FULLPAGER RICE CROPPING SOLUTION` | `FULLPAGE …` | idem |

**A trava:** `NIMRODR` só vira `NIMROD®` porque **`NIMROD` existe sozinho no
registo**. Sem isso não se transforma — `STOPPER P` e `TRIMMER 50 WG` acabam em R
por direito próprio e ficam intactos.

**O nome errado não se apaga.** Fica em `OBSERVED_NAMES` com `MAPS_TO_CANONICAL`
e a razão, porque quem chegar com `APYZAR WG` na mão tem de encontrar o produto:

```
APAGAR O NOME ERRADO NÃO CONSERTA QUEM O TEM NA MÃO.
```

### Onde o conserto vivia antes

Em `italia-portale/audit/product-identity.mjs`, que já chamava à falha o nome
certo — *«un'assenza **FABBRICATA** — il registro li contiene, con un'altra
ortografia»*. Mas era a **camada de apresentação**. Quem lesse os dados sem
passar pelo site apanhava o defeito inteiro.

Os **15** produtos que aquele ficheiro nomeia resolvem agora todos na
referência, com o número de registo: **0 perdidos**. O Portal **não foi tocado**
nesta missão — ele continua a fazer o seu reparo, que agora é redundante, e
retirá-lo é decisão da casa dele.

---

## AS TRÊS FOTOGRAFIAS — NENHUMA VIRA LIXO

| `SNAPSHOT_ID` | observado | ADAMA | `CURRENT` | por que fica |
|---|---|---:|---|---|
| `PROD_FTS_6_20260824` | 24/08 | 163 | não | **os 2.030 usos foram lidos contra esta foto.** Descartá-la tornaria os 2.030 pares afirmações sem data |
| `PROD_FTS_6_20260831` | 31/08 | 602 | **SIM** | população maior e posterior |
| `PROD_FTS_6_20260907` | 07/09 | 602 | não | bruto integral (17.695 linhas), **ainda não derivado**. Usado aqui só para conferir |

⚠️ **O bruto de 07/09 confirma a foto de 31/08 linha a linha: 602 de 602, zero
entradas e zero saídas.** É verificação independente de que a população
regulatória canónica está certa — e de que continuava certa uma semana depois.

Derivar o 07/09 é missão própria. Aqui ele fica declarado como
`RAW_PRESENT_NOT_DERIVED`, não escondido.

### A foto do catálogo não é a foto do Ministero

As três de cima são todas da fonte `IT-T4-001`. O **catálogo comercial** é outra
fonte, e até 15/09/2026 não tinha foto nenhuma: o `PORTFOLIO.json` nasceu do
catálogo observado a **30/08** e escrevia `PROVENANCE.SNAPSHOT_ID =
PROD_FTS_6_20260831` — a data do vizinho regulatório, de outro dia e de outra fonte.

```
A DATA DO REGISTO NÃO É A DATA DO CATÁLOGO.
```

| `SNAPSHOT_ID` | observado | produtos | `CURRENT` |
|---|---|---:|---|
| `CAT_ADAMA_IT_20260830` | 30/08 | 51 | não — reconstruída da evidência que já existia |
| `CAT_ADAMA_IT_20260915` | 15/09 | 51 | **SIM** |

O valor herdado errado **não se apagou**: vive em
`REGULATORY_SNAPSHOT_ID_INHERITED`, ao lado do que o corrige.

⚠️ **Entre as duas fotos: 0 entradas, 0 saídas, 0 campos alterados em 51
produtos.** A leitura completa está em
[`RELATORIO-DRIFT-CATALOGO-2026-09-15.md`](RELATORIO-DRIFT-CATALOGO-2026-09-15.md).

### Ausência é membership, nunca destruição

`PORTFOLIO-OBSERVATIONS.json` diz quem foi **visto** em cada foto. Produto que
deixe de aparecer no catálogo sai da foto — **nunca** do Product Master:

```
PRESENT_IN_CATALOG_SNAPSHOT   estava lá naquele dia
ABSENT_FROM_CATALOG_SNAPSHOT  não estava. NÃO significa descontinuado,
                              NÃO significa apagado.
```

O vocabulário é fechado, e o estado de ausência existe **antes** de ser preciso —
hoje as 102 observações são todas `PRESENT`.

---

## AS DUAS DATAS QUE ERAM UMA SÓ

No V2.1, `REFERENCE_DATE == EXPIRY` em **163 de 163** registos, com valores até
`2040-10-31`. Um campo chamado «data de referência» que guarda o **futuro** faz
quem o leia concluir que o dado está fresco por mais catorze anos.

```
OBSERVED_AT   quando NÓS vimos      ← vem do snapshot
EXPIRY_DATE   quando a autorização acaba
```

Os dois campos existem, separados, em todos os 602 registos. **O valor antigo
não se perdeu** — `EXPIRY_DATE` é exactamente o que `REFERENCE_DATE` guardava.

---

## OS TRÊS ESTADOS QUE NÃO SE DERIVAM UM DO OUTRO

```
ADMIN_ACTIVE           o papel está activo?          facto da fonte
FORMAL_VALIDITY        a data já passou?             calculado contra o snapshot
CURRENTLY_MARKETABLE   pode vender hoje?             UNKNOWN nas 602
```

`CURRENTLY_MARKETABLE` é `UNKNOWN` para **todas**, e essa é a resposta honesta: o
dataset do Ministero não traz período de escoamento. Derivá-lo de
`ADMIN_ACTIVE` seria inventar.

---

## O VOCABULÁRIO DE FONTE FALA COM O ATLAS

```
SRC_FITOSANITARI_SALUTE_GOV_IT  →  IT-T4-001          (Ministero della Salute)
SRC_ADAMA_COM                   →  IT-ADAMA-CATALOG   (catálogo adama.com/italia)
```

`IT-T4-001` é a ficha do Ministero no `ATLAS-DE-FONTES-EAME.md` reconciliado na
FASE 1B. O identificador antigo **não se apaga**: vive em `SOURCE-ID-MAP.json` e
em `PROVENANCE.SOURCE_IDS_LEGACY`.

⚠️ O pacote `…-deep/` já usava `IT-T4-001` em 609 dos seus registos. Quem estava
fora da língua do Atlas era só o V2.1.

---

## EAME COMUM vs ADAPTADOR ITALIANO

### O que atravessa para Espanha e França

```
PRODUCT MASTER · PORTFOLIO RELATION · REGISTRATION · LABEL DOCUMENT
AUTHORIZED USE · ACTIVE INGREDIENT
ADAMA_PRODUCT_ID (sem país) · COUNTRY_SCOPE como atributo
PROVENANCE (SOURCE_IDS · PROVING_ARTIFACT · SNAPSHOT_ID)
OBSERVED_AT ≠ EXPIRY_DATE
ADMIN_ACTIVE ≠ FORMAL_VALIDITY ≠ CURRENTLY_MARKETABLE
OBSERVED_NAME ≠ CANONICAL_NAME, com a razão ao lado
substância activa como ENTIDADE · Reg. (UE) 540/2011 — transversal, não italiano
```

### O que é só da Itália

```
REGISTRATION_NUMBER no formato do Ministero (6 dígitos, zeros à esquerda)
AUTHORITY = Ministero della Salute
ADMIN_STATUS ∈ {Autorizzato, Ri-registrato, Rinnovato, Autorizzato con procedura zonale}
PROD_FTS_6_YYYYMMDD como versão
ETICHETTA · SCHEDA_DI_SICUREZZA · ESTENSIONE_USO
SOURCE_ID IT-T4-001 · IT-ADAMA-CATALOG
```

**Nenhum valor italiano virou lei EAME.** O formato do número, a autoridade e os
estados administrativos vivem nos dados, não no contrato.

---

## O QUE ESTA CASA **NÃO** DIZ

- **não diz** que um produto está à venda hoje — `CURRENTLY_MARKETABLE` é `UNKNOWN`;
- **não diz** dose para 142 dos 163 rótulos — diz `PARSE_STATE`, e
  `PARSER_FAILURE != REGULATORY_ABSENCE`;
- **não diz** o produto de 1.466 dos 2.030 usos autorizados — diz `UNKNOWN`,
  porque o registo deles não tem produto de catálogo;
- **não diz** que as 602 autorizações são 602 produtos. São 51 produtos e 602
  autorizações, e a diferença é informação, não erro.

---

## CONSUMIDORES

Nenhum foi alterado nesta missão. O Portal continua a ler o `DESIGN-INGEST` do
zip e a fazer o seu próprio reparo de nomes. Registado, não consertado —
`italia-portale/` é casa estacionada, e mexer nela era fora de escopo.
