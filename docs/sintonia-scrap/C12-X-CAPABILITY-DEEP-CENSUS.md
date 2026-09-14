# C12 — CENSO PROFUNDO DA CAPACIDADE NO X

    X_CAPABILITY_CENSUS = COMPLETO
    X_COLLECTION_TODAY  = NENHUMA

O X é a plataforma onde esta casa declara mais capacidade **provada** e tem
menos **colheita**. Este censo mede a distância entre as duas, e nomeia o que
está no meio.

---

## 1. O NÚMERO QUE ABRE O CENSO

```
objetos do X preservados nesta árvore ......................  0
contas de X no lote congelado de concorrentes ..............  0
capacidades x.* com rota ligada ............................  0   (de 5 declaradas)
capacidades x.* declaradas PROVEN ou PARTIAL ...............  4
linhas de política que decidem sobre essas quatro ..........  0
```

Quatro capacidades que a casa diz ter provado, e nenhuma delas tem quem a
execute nem quem a autorize.

    CAN DO ≠ DID DO ≠ MAY DO. São três perguntas, e o X responde sim à
    primeira, não à segunda, e silêncio à terceira.

---

## 2. O QUE A CASA DECLARA, MEDIDO NO REGISTO

| capacidade | estado medido | tem rota? | promete resultado? | o que o `CHECK` responde |
|---|---|---|---|---|
| `x.direct_post` | `PROVEN` | não | sim | `DECLARED_WITHOUT_ROUTE` |
| `x.media` | `PROVEN` | não | sim | `DECLARED_WITHOUT_ROUTE` |
| `x.metrics` | `PROVEN` | não | sim | `DECLARED_WITHOUT_ROUTE` |
| `x.native_caption` | `PARTIAL` | não | sim | `DECLARED_WITHOUT_ROUTE` |
| `x.discovery` | `UNKNOWN` | não | **não** | `CAPABILITY_STATE_PROMISES_NOTHING` |

E a inversão que salta à vista quando se põe a política ao lado:

| capacidade | estado | decisão da política |
|---|---|---|
| `x.direct_post` · `x.media` · `x.metrics` · `x.native_caption` | `PROVEN` / `PARTIAL` | **sem tradução para a matriz — nenhuma decisão existe** |
| `x.discovery` | `UNKNOWN` | `ALLOWED` |

    A POLÍTICA EXISTE EXATAMENTE ONDE A CAPACIDADE NÃO EXISTE, E A CAPACIDADE
    É ALEGADA EXATAMENTE ONDE A POLÍTICA NÃO EXISTE.

Ninguém pode ser recusado por uma linha que não foi escrita. As quatro
capacidades provadas não são «permitidas» — são **não decididas**, e
`NOT_DECLARED` não é permissão.

---

## 3. O `robots` DOS TRÊS HOSTS, LIDO AGORA

O portão de transporte desta casa lê o `robots.txt` vivo, com o `User-Agent`
real. Medido nesta máquina:

| host | bytes | bloco `User-agent: *` | veredito |
|---|---|---|---|
| `x.com` | 2 678 | `Disallow: /` | **barra tudo** |
| `cdn.syndication.twimg.com` | 26 | `Disallow: /` | **barra tudo** |
| `pbs.twimg.com` | 43 | `Disallow:` *(vazio)* | **permite tudo** |

O agente `SintoniaScrap` não aparece nomeado em nenhum dos três, portanto cai
sempre no `*`.

### E aqui está o achado do censo

O benchmark anterior registou «o `robots.txt` do X» como `DISALLOW_ALL`, num
bloco só. São **três hosts**, e um deles permite.

| capacidade provada | host que a serve | robots |
|---|---|---|
| `x.media` | `pbs.twimg.com` | **permite** |
| `x.direct_post` | `x.com` | barra |
| `x.metrics` | `x.com` | barra |
| `x.native_caption` | `x.com` | barra |

A metade permitida é a **busca dos bytes**. E o endereço desses bytes só existe
dentro do objeto que vive no host que barra.

    UMA METADE PERMITIDA QUE SÓ SE ALCANÇA PELA METADE PROIBIDA NÃO É MEIA
    CAPACIDADE. É NENHUMA.

Isto é o inverso exato do LinkedIn. Lá, a metade permitida é a **descoberta** —
saber QUEM existe, colhido de fora do linkedin.com — e ela sozinha já serve ao
negócio. Aqui a metade permitida é a busca, e ela sozinha não serve a nada,
porque não se busca o que não se sabe existir.

---

## 4. AS 21 CONTAS QUE A CASA JÁ DESCOBRIU SEM TOCAR NO X

Medido por varredura do que está preservado: **21 handles distintos**, em 12
ficheiros, nenhum colhido do x.com.

```
@agrocienciauy   @agronotizie   @fao   @basfagsolutions   @basf_agro_au
@agriculteuraujo  @aragontv  @alvelal_4r  @avlexisdotcom  @condavision
@elcampo_atv  @essaludperu  @factorhumus  @helloxfarm   … e mais 7
```

Vieram de descrições de vídeo do YouTube e de diretórios de peritos — ou seja,
**as próprias organizações publicaram o endereço delas noutro sítio**. É a
mesma rota de descoberta indireta que a C11 provou para o LinkedIn.

    URL DESCOBERTA NÃO É POST COLETADO. Zero ficheiros declaram `PLATFORM = X`.

Estas 21 contas são matéria-prima real de negócio — saber quem existe e onde —
e não custaram um pedido ao x.com.

---

## 5. A ROTA PAGA OFICIAL, E O QUE ELA CUSTA

| item | preço | estado nesta máquina |
|---|---|---|
| `Posts: Read` | US$ 0,005 por recurso | `CREDENTIAL_MISSING` |
| `User: Read` | US$ 0,010 por recurso | `CREDENTIAL_MISSING` |
| *Owned Reads* | US$ 0,001 por recurso | `CREDENTIAL_MISSING` |

Nenhuma variável de ambiente com marca de X ou Twitter existe neste ambiente —
medido sem imprimir valor nenhum. A matriz declara `SEARCH_KEYWORD` como
`PERMITIDA = SIM`, `OFFICIAL_API_PAID`, `CREDENTIAL_MISSING`. É a única linha de
política que o X tem, e é a única capacidade que a casa não sabe fazer.

E o custo de referência: mil posts por mês = **US$ 5,00**. Comparado com o preço
medido da Apify nesta casa (US$ 1,863 por mil itens), a rota oficial do X é
**2,7× mais cara por item** — e é a única permitida.

```
ZERO_APIFY ≠ ZERO_PAID_PROVIDER
```

No X o Apify já é zero e sempre foi: **nunca houve ator de X neste repositório**.
Isso não torna o X gratuito. Torna-o não-coletado.

---

## 6. A FERRAMENTA QUE PROVOU ESTÁ INSTALADA, E É ISSO QUE TORNA O CENSO ÚTIL

`gallery-dl 1.32.11` está em `/usr/local/bin`, e `LOCAL_GALLERY_DL` já é um nome
de fornecedor declarado nesta casa. Foi ele que devolveu o tweet completo,
deslogado, que sustenta três dos quatro `PROVEN`.

Ou seja: **tudo está no sítio menos as duas coisas que decidem** — uma rota no
registo e uma linha na política. E o censo mediu por que é que nenhuma das duas
deve ser escrita hoje: o host que serve o objeto responde `Disallow: /`.

    ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.

---

## 7. O QUE O `PROVEN` DO X REALMENTE SIGNIFICA

Os quatro `PROVEN` apoiam-se em `BENCHMARK-V1-FINAL.md`, que mediu **um objeto**:
o tweet `2064888809154551909` da Syngenta Argentina, de 2026-06-11.

Os bytes dessa medição **não foram preservados**. Não há artefato, não há
`SHA256`, não há `RAW`. A prova é um número num documento, não um ficheiro no
disco.

    CAN DO ≠ DID DO. «Provámos que conseguimos» e «temos isto guardado» são
    duas frases, e só a segunda alimenta inteligência.

Isto não invalida o `PROVEN` — a medição aconteceu e está datada. Mas põe-lhe o
tamanho certo: um objeto, uma vez, sem preservação.

---

## 8. O QUE ESTE CENSO NÃO FEZ

Não tocou no x.com. Não correu `gallery-dl`. Não pediu credencial. Não gastou um
dólar. Não alterou política, não ligou rota, não declarou capacidade nova. Não
mexeu em Admission, Collection, portal nem Bíblia.

As três únicas requisições de rede que fez foram aos `robots.txt` dos três hosts
— que é a requisição que todo agente tem o direito e o dever de fazer.

---

## 9. VEREDITO

```
X_OBJECTS_PRESERVED    = 0
X_ACCOUNTS_IN_LOT      = 0
X_HANDLES_DISCOVERED   = 21   (indirectos, nunca do x.com)
X_ROUTE_WIRED          = NO   (0 de 5 capacidades com caminho)
X_POLICY_DECLARED      = NO   (excepto SEARCH_KEYWORD, que é a que não sabemos fazer)
X_ROBOTS_X_COM         = DISALLOW_ALL
X_ROBOTS_SYNDICATION   = DISALLOW_ALL
X_ROBOTS_PBS_TWIMG     = ALLOW_ALL
X_OFFICIAL_API         = CREDENTIAL_MISSING · US$ 0,005 por post lido
ZERO_APIFY             = YES
X_TOOL_INSTALLED       = gallery-dl 1.32.11
```

**A pergunta que fica para gente, e não para código:** a casa mantém quatro
capacidades marcadas `PROVEN` para uma plataforma cujo host responde
`Disallow: /`, sem rota e sem decisão de política. Isso é honesto enquanto
ninguém confundir `PROVEN` com «colhemos». O censo existe para que essa confusão
não aconteça em silêncio.

O passo mínimo seguinte, se houver vontade, é **o barato e permitido**: as 21
contas descobertas já estão em casa e podem virar ficha de fonte sem um único
pedido ao x.com.
