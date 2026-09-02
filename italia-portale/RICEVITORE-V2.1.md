# SINTONIA ITALIA · O RECEPTOR

O que o portal aceita, e o que o próximo pacote de inteligência precisa entregar
para entrar sem reescrever nenhuma tela.

---

## O caminho, inteiro

```
HANDOFF V2.1 ─┐
CANONICAL     ├──► INGEST · VALIDATE · NORMALIZE ──► ITALY_APP_MODEL ──► TELA
REAL SOURCE   │         (italy-app-model.js)
FIXTURE DEMO ─┘
```

Uma tela **nunca** sabe qual missão de pesquisa produziu um registro. Ela lê uma
coleção normalizada e nada mais. Isso é o que permite trocar o dado sem tocar na
interface.

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
