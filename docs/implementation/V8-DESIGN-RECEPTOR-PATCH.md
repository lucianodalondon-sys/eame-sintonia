# V8 · PATCH DE RECEPÇÃO PARA O CLAUDE DESIGN

**Data:** 2026-08-31 · lista fechada · **nenhum redesenho pedido**

> **Para quem lê primeiro:** o casco passou no visual. Esta lista não muda uma cor, um
> espaçamento ou uma hierarquia. Ela pede **campo onde hoje há rótulo**, **estado onde hoje
> há booleano** e **handler onde hoje há botão desenhado**.

**Por que não editei o HTML:** o casco é um export do Claude Design. Editar à mão criaria um
fork que o próximo export destruiria em silêncio. Toda mudança sai como patch.

---

## REGRA QUE ATRAVESSA TUDO

**Um receptor, dois backends.** Não construir tela de GitHub e tela de Supabase. A UI recebe
**entidade canônica**; o adapter decide de onde veio. O componente de proveniência é o
mesmo; só o rótulo do campo muda.

**Credencial nunca no frontend.** `SERVICE_ROLE_KEY`, secret e token não atravessam
receptor.

---

## P1 · ENVELOPE DE CARGA — em todo bloco que hoje é `hasX` / `noX`

**Hoje:** `hasObjects`/`noObjects`, `hasChanges`/`noChanges`, `hasKnown`/`noKnown`,
`objHasHistory`/`objNoHistory`. Dois estados: cheio ou vazio.

**Pedido:** um campo `loadState` por bloco, com oito valores, mais `noDataReason`.

```
UNWIRED ............ existe e nunca foi ligado
LOADING ............ requisição em curso
READY .............. tem dado
EMPTY_VALID ........ a fonte respondeu e vazio é a resposta certa
NOT_STARTED ........ a rota existe, declarada, e a coleta não começou
NOT_AVAILABLE ...... a fonte não oferece — não é lacuna nossa
BLOCKED ............ um guard recusou; o motivo é obrigatório
ERROR_FAIL_CLOSED .. falhou; declara, nunca degrada para vazio
```

**Por que importa:** hoje uma lista vazia por falta de ligação e uma lista vazia por
resultado legítimo desenham igual. O portal já sabe dizer *"nenhuma mudança desde o freeze —
silêncio é informação"*. Precisa saber dizer também *"isto nunca foi ligado"* e *"isto deu
erro"* — que são coisas diferentes e hoje se parecem.

**Os textos de vazio que já existem em `emptyStates` continuam certos.** Eles cobrem
`EMPTY_VALID`. Faltam os outros sete.

---

## P2 · ENVELOPE DE PROVENIÊNCIA — na gaveta e em todo card

**Hoje:** um campo de texto, `PROVENIÊNCIA: "hash / commit — slot"`.

**Pedido:** um objeto com discriminador.

```
sourceBackend: "GITHUB"     → repository · path · commitSha · hash · sourceId · asOfDate
sourceBackend: "SUPABASE"   → schema · tableOrView · primaryKey · snapshotId
                              capturedAt · sourceId · asOfDate
```

Uma linha de rótulos por campo, no mesmo estilo dos sete campos atuais da gaveta. **O
componente é o mesmo nos dois casos.**

---

## P3 · GAVETA POR OBJETO

**Hoje:**

```js
openDrawer: () => this.set({ drawerOpen: true })
o.evidence:  () => this.set({ drawerOpen: true })
```

Nenhum id. `drawerClaim` e `drawerFields` são chaves de topo, iguais para todos.

**Pedido:** a gaveta recebe `objectId`, `hoseId` e `evidenceId`; `drawerClaim` e
`drawerFields` passam a vir do objeto que a abriu.

**Sem isso, `EVIDENCE_DRAWER_TRACES_ALL_HOSES` não pode ser `YES` em nenhuma versão.**

---

## P4 · GAVETA MULTILÍNGUE — ligar o que já está desenhado

**Hoje:** os rótulos `TRECHO ORIGINAL` e `IDIOMA DA FONTE` existem sem valor ligado. O corpo
é um parágrafo estático explicando a política. Os botões **"Ver original"** e **"Mostrar
tradução"** não têm `sc-camel-on-click`.

**Pedido:** ligar seis campos e dois handlers.

```
canonicalEntityId · sourceLanguage · displayLanguage
originalText · translatedText · translationProvenance

showOriginal()  ·  showTranslation()
```

`sourceLanguage` aceita `pt · en · es · fr · it · MULTILINGUAL · UNKNOWN` — vocabulário
fechado. **`UNKNOWN` é o valor mais comum e é o valor correto:** dos registros medidos, 283
em 5.998 têm o campo de língua e **zero** têm valor declarado.

**Sem `originalText` não renderiza tradução.** Nunca a tradução sozinha — a política já está
escrita na própria gaveta.

> Este é o item mais importante da lista. Um botão que parece clicável e não faz nada é a
> mesma armadilha do *ranking de recorrência* do V7.

---

## P5 · `OBJECT_ID` EM TODO OBJETO

**Hoje:** `RAW` tem `id: 'OBJ-01'` na camada de dados, e o id **não sobe** para o markup —
`mk()` não o inclui.

**Pedido:** `objectId` em todo card, todo detalhe, toda ação, todo ponto de mapa e todo
evento de timeline.

Sem isso nada pode ser referenciado: a gaveta não sabe de quem veio, a ação não sabe a que
objeto pertence, o mapa não sabe que ponto desenhar.

---

## P6 · CONVERGÊNCIA — quatro campos por perna

**Hoje:** `convLegs[].family` é um rótulo livre (`'FAMÍLIA CAMPO'`) e `INDEPENDÊNCIA:
INDEPENDENTE` é texto dentro de `fields[]`.

**Pedido:**

```
propositionId
convergenceKind:  PHENOMENON_CONVERGENCE | IDENTITY_CONVERGENCE | CONTEXTUAL_ALIGNMENT
por perna:
  signalFamily        um dos oito: TERRITORIAL · SCIENCE_RESEARCHER · NATIONAL_REGISTRY
                      TRADEMARK · META_PAID_ADS · CREATOR · FIELD_HISTORICAL
                      COMPETITOR_PUBLIC_COMM
  evidenceId
  independenceState   INDEPENDENT | DEPENDENT | NOT_PROVED
  dependencyRelation  quando DEPENDENT: tipo + alvo
                      SOURCE_DEPENDENCY · OBSERVATION_DEPENDENCY · ENTITY_DEPENDENCY
                      DERIVATION_DEPENDENCY · SEMANTIC_DEPENDENCY · INDEPENDENT_SOURCE
```

**`dependencyRelation` é o campo mais importante do patch inteiro.** Duas dependências reais
precisam ficar visíveis:

```
H3 → H4   DERIVATION_DEPENDENCY   a perna Meta da cadeia É o anúncio da Meta
H5 → H1   SOURCE_DEPENDENCY       o RAIF é publicador dos dois lados
```

Sem ele, duas pernas que são a mesma evidência vista de outro ângulo desenham como
`MULTI SIGNAL`. **Cinco das seis convergências da versão anterior eram esse erro.**

Visualmente: uma linha ligando as duas pernas, com o tipo da relação. **Nada mais muda** — a
lei já está certa na tela.

---

## P7 · TIMELINE — cinco campos

**Hoje:** `date: '23 ABR'` é rótulo de exibição. Faltam id, data real e os dois estados.

```
eventId · eventAt (ISO) · sourceId · observationId · stateBefore · stateAfter
```

`eventAtResolution` já existe como `res` — **manter**. `kind` já cobre `EVENT_TYPE` e
`changed` cobre `WHAT_CHANGED` — **manter os dois**.

O tipo `VAZIO TEMPORAL` está certo e não muda: o vazio é um evento.

---

## P8 · MAPA DE CULTURAS — receber objeto, não só país

**Hoje:** coroplética de país (`ESP` · `ITA` · `FRA`), com três buracos honestamente
declarados em `mapHoles`.

**Pedido:** uma lista de pontos, cada um com:

```
objectId · objectType · attentionState · country · region
localityOrGeometry · geoResolution · crop
geoResolution: COUNTRY | NUTS2 | PROVINCE | MUNICIPALITY | LOCALITY_TEXT | POINT | NOT_KNOWN
```

**`mapHoles` fica exatamente como está.** É a melhor parte do componente: o mapa declara que
não tem geometria e não pinta mancha por estimativa. **Sem `geoResolution` o ponto não é
desenhado** — localidade em texto nunca vira coordenada por geocodificação silenciosa.

---

## P9 · MAPA DE AÇÕES — três campos

**Hoje:** `kind` já carrega os três tipos canônicos com outros nomes.

```
BUSINESS → BUSINESS_DECISION   INVESTIGATION → INVESTIGATION   SYSTEM → SYSTEM_DECISION
```

**Pedido:** `objectId`, `actionType` com o nome canônico, e **`evidenceBasis`** — a lista de
`evidenceId` que sustenta a ação.

**Regra em código, não em texto fixo:** `evidenceBasis` vazio → a linha renderiza
`SEM AÇÃO DEFENSÁVEL AINDA`. Hoje o casco garante isso por frase escrita; precisa garantir
por campo.

---

## P10 · H8 — receptor de conta local de concorrente, na tela Fontes

**Hoje:** `sources[]` tem cinco slots genéricos (regulatória, científica, campo, mercado,
clima). Nenhum é conta de empresa. O estado `NÃO INICIADA` **existe na paleta** e não é
usado em Fontes.

**Pedido:** uma linha de fonte por conta, com:

```
accountId · companyName · platform · countryScope · pageRole
contentCollectionStage: NOT_STARTED | RUNNING | PARTIAL | COMPLETE
routeState · identityResolvedAt
```

**Hoje o valor é `NOT_STARTED`, e a rota precisa aparecer assim mesmo.** Rota conhecida,
identidade resolvida, coleta não iniciada — que não é vazio, não é erro, e **não é silêncio
da empresa**.

---

## P11 · H7 — portão como campo, e a lista dentro do objeto

**Dois pedidos separados.**

**a) O portão precisa ser campo.** Hoje `Só aparece como especialista do problema quando a
expertise no problema estiver provada` é uma **frase acima da lista**. Prosa não bloqueia
renderização.

```
identityProved · issueExpertiseProved · gdprTreatmentState
```

`issueExpertiseProved = false` → a pessoa pode aparecer como **pessoa relacionada**, nunca
como autoridade no problema. `NOT_MEASURABLE ≠ NOT_PROVED`.

**b) A lista devia estar no objeto.** Hoje `experts` renderiza no **Radar**, fora de
qualquer objeto — e um portão por objeto não tem onde ser exercido. A camada Pessoas
pertence ao `PHENOMENON_CASE`.

**Sem ordem e sem ranking continua.** Recorrência, seguidores e número de artigos não são
autoridade — isso já está certo e não muda.

---

## P12 · TRÊS SUBRECEPTORES NOVOS

Blocos novos, no estilo dos que já existem. Cada um é hoje **um chip de estado** e precisa
virar **um lugar onde chega dado**.

### `SCIENCE_PUBLICATION_EVIDENCE` — camada Ciência do `PHENOMENON_CASE`

```
publicationId · title · publishedAt · venue · authors
relationToIssueAsDeclared · peerReviewedState · sourceLanguage · sourceId
```

**Não roteie H7 para cá.** H7 entrega **pessoa**; esta camada precisa do **trabalho**. Sem
publicação ligada ao issue, o bloco mostra `EMPTY_VALID` com o motivo — **nunca herda a
lista de pessoas para parecer cheio**.

### `LOCAL_ADAMA_PORTFOLIO_CONTEXT` — camada Portfólio local

```
country · crop · issue · registeredResponseState
adamaProductRefs · registrationRefs · labelAuthorizesTargetState · sourceId
```

**Não roteie H2 para cá.** H2 carrega o prazo de um registro de **qualquer titular**. A
pergunta aqui é outra: *a ADAMA tem resposta registrada para este alvo neste país?*

### `FIELD_VOICE_OBSERVED` — dentro do bloco `voices`

```
observationId · entityId · entityKind · platform · observedAt
country · cropMentioned · regionMentioned · originalText · sourceLanguage
relationToIssueState · gdprTreatmentState
```

A separação `PERSON CREATOR` / `FARM BUSINESS` **fica como está** — está certa. O que falta
é o que a pessoa disse.

---

## P13 · H6 — `ENTRY_PATH` instrumentado

```
entryPath: FROM_ATTENTION_OBJECT | FROM_CROP_REGION_SEARCH
```

E a rota de busca `cultura + região` precisa existir como caminho — hoje `voices` só é
alcançável de dentro do objeto.

**Sem `ENTRY_PATH` não há promoção a ferramenta.** A arbitragem decidiu que Creator vira
ferramenta ou não **com o dado de uso**, não com estética. Sem o campo, a decisão nunca pode
ser tomada.

`rowCount` e `entityCount` viajam sempre juntos — a inflação medida foi de **2,6×**.

---

## O QUE O PATCH **NÃO** PEDE

```
nenhuma cor nova · nenhuma hierarquia nova · nenhuma tela nova
nenhum componente redesenhado · nenhum score · nenhum ranking
nenhum dashboard de Meta · nenhum dashboard regulatório · nenhum audit dashboard
nenhuma navegação primária de Creator
```

Os nove componentes que o veredito visual aprovou **ficam como estão**. E o que já está
certo continua: composição modular por tipo, vazio temporal como evento, `mapHoles`,
localidade da fonte ≠ localidade do fato, single signal legítimo, alinhamento contextual que
não soma, `SEM AÇÃO DEFENSÁVEL AINDA`, latência `NÃO MEDIDA`.

---

## ORDEM SUGERIDA

**Sugestão, não instrução.** Os quatro primeiros destravam todos os outros.

```
1  P1  envelope de carga        sem os oito estados, H8 não pode existir
2  P2  envelope de proveniência sem ele, nada é rastreável
3  P5  OBJECT_ID                sem id, nada é referenciável
4  P3  gaveta por objeto        fecha a cadeia até a evidência
5  P4  gaveta multilíngue       liga o que já está desenhado
6  P6  DEPENDENCY_RELATION      impede a convergência falsa
7  P9  EVIDENCE_BASIS           impede ação sem evidência
8  P10 H8                       a única mangueira sem receptor nenhum
9  P12 três subreceptores       impedem três roteamentos errados
10 P7 · P8 · P11 · P13          completam o resto
```

Quando os treze estiverem no casco:

```
HOSES_WITH_COMPLETE_RECEIVER = 9/9
CASCO_RECEPTOR_READY = YES
READY_TO_WIRE_REAL_DATA = YES
```

E aí — e só aí — a próxima rodada liga dado real.
