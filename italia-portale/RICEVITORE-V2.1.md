# SINTONIA ITALIA · O RECEPTOR, DEPOIS DE RECEBER

Este documento descrevia o que o portal aceitaria quando o V2.1 chegasse.
O V2.1 chegou. Agora descreve o que ele aceitou, e por onde.

    BUILD_ID ingerido   V21-99226fbb90dcdbc2
    data de referência  2026-09-02

---

## O caminho, inteiro

```
build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/
        │
        │  scripts/site_v21_ingest.py      ← escolhe O QUE atravessa
        ▼
client/italy-handoff-v21.js               window.ITALY_HANDOFF_V21
        │
        │  italy-app-model.js              ← dá FORMA ao que atravessou
        ▼
ITALY_APP_MODEL ──► PORTAL
```

Duas camadas, e a divisão entre elas é a coisa que este documento existe para
explicar.

**O ingest escolhe.** Ele é uma lista de permissão, campo a campo. Fato passa;
prosa de pesquisa não embarca; onde a fonte escreveu e não há par IT/EN
aprovado, atravessa `CAMPO__PT_ONLY: true` sem o texto — a dívida continua
contada, o português não viaja até o navegador do cliente italiano.

**O modelo dá forma.** É ele que resolve cultura, avversità, região e data,
porque é lá que os resolvedores e o relógio único já moram. Dois lugares
resolvendo cultura é como duas telas passam a discordar sobre a mesma videira.

    O INGEST DECIDE O QUE ATRAVESSA. O MODELO DECIDE QUE FORMA TEM.

O contrato do receptor prometia `adapt: (r) => r` — que o pacote entregaria
linhas já na forma das telas. Ele não entrega, e não deve: publica o próprio
contrato canônico, e é isso que permite fundir duas missões de pesquisa. A
tradução de um contrato no outro está escrita em `V21(família, adapt)`, ao lado
do adaptador de fixture que ela substitui, para que os dois possam ser lidos um
contra o outro.

## O que entrou, medido

| família | agora | antes |
|---|---:|---:|
| `productRelationships` · duplas de uso de rótulo | **2.030** | 236 |
| `productsRegulatory` | **163** | 163 |
| `productsCommercial` | **51** | 44 |
| `activeIngredients` · substância como entidade | **53** | — |
| `productActiveIngredients` | **203** | — |
| `opportunities` · do motor | **43** | 3 |
| `fieldBulletins` · boletins regionais | **133** | — |
| `cropEconomics` | **2.978** | — |
| `regulatoryFutureFacts` | **47** | — |
| `clientSafeCrossings` | **19** | 0 |
| `agrometConditions` | **44** | 0 |
| `competitorActivities` | **577** | 503 |
| `marketObservations` | **157** | 77 |
| `publicVoices` | **79** | 17 |
| `sources` · linhas entregues | **191** | 31 |
| `cropWindows` · canônicas | 29 | 29 |

`cropWindows` não muda: as 7 linhas que o pacote chama `CROP-WINDOWS.json` são
os mesmos `IT-WIN-001..007` que sempre alimentaram `currentFieldSignals`, e as
29 janelas auditadas continuam vindo do contrato canônico. Trocar 29 janelas
por 7 leituras porque dois arquivos têm nomes parecidos teria sido a perda mais
cara possível.

`cropEconomicWeight` (35 culturas) deixou de vir da fixture: é recontado das
2.030 duplas. **CULTURAS = 35** e **ALVOS = 78** são o vocabulário do próprio
corpus de rótulos, medido, não uma lista digitada.

`competitorActivities` traz **577** registros, e não os 561 que a tela mostrava:
os 16 que faltavam não eram duplicados, eram uma SEGUNDA FORMA da mesma família
— NOTAS DE OBSERVAÇÃO, sem anunciante nem plataforma, carregando no lugar um par
já traduzido de «o que prova» e «o que não prova». A lista de campos admitidos
conhecia só a primeira forma. Dos 577, **569 são publicáveis** e **8 continuam
`QA_UNREVIEWED`**: vivem no corpus, não sustentam uma afirmação. A tela mostra
569 e diz por que o denominador é 569, porque um número certo dentro de uma
frase errada continua sendo uma frase errada.

`sources` entrega **191** linhas, que são **189 fontes reais** mais **2
`SOURCE_SENTINEL`** (`SRC_NAO_DECLARADA` e `SRC_DESCONHECIDA`). Sentinela é a
marca de que a fonte não foi declarada — contá-la como fonte seria transformar
uma ausência em acervo. O portal conta 189.

## As oportunidades, e como se dizem

> **Estes números seguem a cadeia canônica.** O pacote deste build foi
> reconstruído em `claude/opportunity-commercial-priority-v1` `b3935bd`
> (`BUILD_ID V21-358954754db5ea2f`), e os anteriores ficam ao lado para que a
> diferença se leia em vez de se adivinhar:
>
> ```
> V21-99226fbb90dcdbc2   37 · 9 verificadas · 28 a validar · 17 rebaixadas
> V21-358954754db5ea2f   43 · 33 verificadas · 10 a validar · 4 rebaixadas
> ```

O motor gera 43. Trinta e três passam com o método declarado ao lado; 10 são
candidatas. Todas as 43 são `CLIENT_SAFE=false`, e isso não foi afrouxado para
levantar um número: uma oportunidade é leitura nossa sobre fatos de terceiros.

```
IT   OPPORTUNITÀ SINTONIA · CONVERGENZA VERIFICATA       33
     DA VALIDARE                                         10
EN   SINTONIA OPPORTUNITY · VERIFIED CONVERGENCE         33
     TO VALIDATE                                         10
```

Pode-se apresentar **43 rilevate · 33 convergenze verificate · 10 da validare**.
Não se apresenta 43 como confirmadas — `H4` recusa a frase.

⚠️ `RENDERABLE_WITH_METHOD` **não é mais sinônimo de publicável.** Neste build o
motor emite uma catraca própria, `PUBLICATION_STATE`: **5 PUBLISHABLE · 38
VALIDATION_REQUIRED**. As duas perguntas separaram-se, e o radar ordena pela
segunda — porque publicado atrás de um botão não é publicado.

O próprio pacote escreve `OPPORTUNITY_LABEL_IT = «OPPORTUNITÀ CONFERMATA»`.
Essa palavra não é embarcada e não é usada: *confirmada* é o que um motor chama
um caso que passou nos seus portões, e não é o que um cliente deve ler ao lado
de um cartão cuja evidência é uma convergência que nós desenhamos.

`CLIENT_SAFE`, `RENDERABLE_WITH_METHOD`, `EVIDENCE_DERIVED` e os portões
bloqueadores são contabilidade do motor. São lidos para ESCOLHER o rótulo e
depois removidos do objeto — não são propriedades dele, então nenhum binding e
nenhum painel de depuração pode pô-los diante de um cliente.

    UMA PROPRIEDADE QUE VOCÊ APAGA NÃO PODE SER RENDERIZADA POR ACIDENTE.

O red team **rebaixa, não apaga**: os 4 casos que ele derrubou estão todos
dentro dos 43, como candidatos, porque «da validare» é exatamente o que são. O
que ele proíbe não é mostrá-los — é chamá-los de verificados.

## O que a régua garante agora

```
node audit/run.mjs        64 verificações estruturais, sem navegador
node audit/v21-gate.mjs    4 verificações sobre o que EMBARCOU
node audit/browser.mjs     7 verificações no Chromium de verdade
node audit/acceptance.mjs  o relatório inteiro, medido
```

`H1` afirmava que o V2.1 **não** tinha sido ingerido — era um alarme contra uma
migração pela metade. A migração aconteceu, e um alarme que sobrevive àquilo
contra o que alarmava vira ruído. Hoje `H1` cobra o oposto: que o pacote esteja
dentro, identificado, e que cada família diga ter sido construída a partir dele.

`V4` faz a pergunta que nenhuma das outras faz: *o pacote embarcado é mais velho
que a lei que o governa?* A lista de marcadores de língua decide o que atravessa
a fronteira, então é entrada tanto quanto o pacote. Medido: tirar um único
marcador ambíguo mudou 16 das 26 famílias. A assinatura da lista viaja dentro do
arquivo gerado; se ela divergir, `V4` falha e diz o comando.

## A precedência


```
CANONICAL  >  REAL_SOURCE  >  REAL_DERIVED  >  SYNTHETIC_DEMO  >  DEMO_SCENARIO
```

`build(família, candidatos)` percorre os candidatos nessa ordem e fica com o
**primeiro que produzir registros**. Quando o V2.1 entregar uma tabela real, ela
ganha sozinha — sem editar view nenhuma.

## Como plugar o V2.1

Uma linha. No topo de `italy-app-model.js`, o registro de fontes já tem o lugar:

```js
const RAW = {
  HANDOFF_V21: window.ITALY_HANDOFF_V21 || null,   // ← aqui
  CANON: window.ITALY_CANONICAL || {},
  ...
};
```

Publique `window.ITALY_HANDOFF_V21 = { referenceDate, <família>: [...], ... }`
antes de `italy-app-model.js` carregar. Toda família já procura o V2.1 primeiro,
com precedência `CANONICAL`.

## As famílias que o receptor aceita

Vazio é resposta válida. Nenhuma delas é preenchida com registro inventado.

| família | hoje | fonte de hoje |
|---|---:|---|
| `productsRegulatory` | 163 | registro fitossanitário italiano |
| `productsCommercial` | 44 | catálogo comercial público reconstruído |
| `productRelationships` | 236 | auditoria de rótulo + registro nacional |
| `cropWindows` | 29 | contrato canônico auditado |
| `currentFieldSignals` | 7 | leituras de campo por cultura × avversità |
| `cropEconomicWeight` | 17 | alcance no corpus de rótulos |
| `marketObservations` | 77 | EU Agri-food Data Portal, semanal |
| `competitorActivities` | 503 | comunicação pública observada |
| `scienceRecords` | 88 | registros científicos com fonte resolvível |
| `researchers` | 60 | identidades de pesquisa |
| `resistance` | 34 | casos italianos confirmados |
| `publicVoices` | 17 | vozes públicas de campo |
| `publicChannels` | 30 | canais públicos italianos |
| `regulatoryFuture` | 163 | vencimento de autorização |
| `agrometConditions` | **0** | **não existe tabela a montante** |
| `futureEvents` | 18 | eventos do setor |
| `opportunities` | 3 | convergências a montante |
| `futureSignals` | 3 | sinais com evidência rastreável |
| `sources` | 31 | registro de fontes |
| `events` | 18 | alias de `futureEvents` |
| `news` | 8 | notícia e mídia técnica |
| `relationships` | 9 | apenas relações declaradas |
| `clientSafeCrossings` | **0** | **não existe tabela a montante** |

## As três regras que o pacote V2.1 precisa respeitar

### 1 · Prosa precisa vir aprovada nos dois idiomas

Medido neste pacote: 219 de 219 linhas de rótulo, 17 de 17 vozes, 34 de 34
mecanismos de resistência e 31 de 31 limitações de fonte trazem **nota de
pesquisa escrita em português**. Apontar a tela para o dado cru poria essa nota
na frente do cliente italiano.

Por isso `narrative(registro, 'CAMPO')` **nunca** devolve prosa crua:

| estado | quando | o que a tela mostra |
|---|---|---|
| `CLEAR` | existe `CAMPO_IT` / `CAMPO_EN` aprovado | o texto |
| `NOT_ESTABLISHED` | a fonte escreveu "NAO SEI" | "non noto" |
| `NOT_APPROVED_FOR_DISPLAY` | há prosa, sem versão aprovada | **nada** |

Hoje há **28 pares família/campo** em `NOT_APPROVED_FOR_DISPLAY`
(`AM.ingest.narrativeDebt` lista todos). Cada `CAMPO_IT` / `CAMPO_EN` que o V2.1
entregar acende um painel que hoje fica calado. **Nenhuma tela precisa mudar.**

Fato — data, enum, nome, número, URL, citação pública original — passa direto.

### 2 · Nome de cultura, avversità e região vêm resolvidos ou vêm crus, nunca meio

Seis vocabulários chegam hoje para a mesma coisa: `Grapevine` (canônico),
`VITE` (ingerido), `Videira` (oportunidade), `MAIS` (sinal), `VINE` (ciência),
`Vitis vinifera` (concorrência), e o genérico `colture`.

`cropResolve()` devolve `{ key, keys, label, scope, raw }`:

- `RESOLVED` — uma cultura canônica
- `MULTI` — a fonte nomeou várias de verdade ("grano duro e tenero")
- `GENERIC_TERM` — palavra de grupo. **Nunca vira cultura específica**:
  "cereali" não é "Wheat", e dizer que é inventa fato.
- `NOT_OBSERVED` / `UNMAPPED`

O termo publicado fica sempre em `cropRaw` / `issueRaw` / `regionRaw`, para nada
ficar sem rastro. Nenhum binding do template lê um `*Raw` — a verificação `PT3`
existe só para provar isso.

Se o V2.1 puder entregar a chave canônica junto do texto publicado, o mapeamento
declarado em `CROP_BY_*` / `ISSUE_PHRASE` deixa de ser necessário.

### 3 · O que não é observável de fora não é lacuna do Sintonia

Venda, estoque, pedido, pipeline e margem **não entram**, nem como campo vazio
"a preencher". Onde a pergunta é comercial e a resposta não é pública, a tela diz
**NON OSSERVABILE DA FONTI ESTERNE** — uma vez, não uma linha por sistema.

---

## O que a régua garante

`node audit/run.mjs` — 46 verificações sobre o pipeline de verdade, sem
navegador: a harness carrega os dados, instancia a própria classe do portal e
roda `renderVals()` para 26 telas em italiano e em inglês.

As que importam para quem for entregar o V2.1:

| | |
|---|---|
| `D1` | leituras da fixture que carregam fato = **0** |
| `M3` | as 23 famílias existem, vazias inclusive |
| `R1` | todo id cruzado resolve |
| `R2` | nenhum registro real cai em silêncio noutro |
| `PT1` `PT2` `PT3` | nenhuma prosa de pesquisa, nenhum vocabulário não resolvido |
| `MK1` `MK2` | todo prop que o template lê existe; toda lista é lista |
| `RT1` `RT2` | as 26 telas renderizam nos dois idiomas |

Sai com código 0 só quando todas passam. `node audit/acceptance.mjs` imprime o
relatório de aceitação inteiro, medido — nenhuma linha dele é digitada à mão.

---

## Uma ressalva que precisa ser dita

As três oportunidades e dois dos três sinais de futuro chegam marcados
`REAL_DERIVED` **pela própria fonte a montante** — são convergências derivadas,
não observações cruas. O painel de transparência mostra isso na coluna certa. É
uma distinção que o cliente merece ver, e não deve ser arredondada para "3
oportunidades reais".

E as 17 vozes públicas têm entre **1 e 13 anos** (a moda é 6–7 anos). O único
carimbo temporal que existe é o relativo do YouTube, e por isso a tela mostra
"≈ 6 anni fa" e nunca uma data de calendário.
