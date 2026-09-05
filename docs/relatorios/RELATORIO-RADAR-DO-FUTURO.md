# Radar do Futuro, camada de exibição e handoff para o Design

`2026-08-30` · entrada `cc82d90` · 6 commits na principal + 2 na França · 422 testes OK

---

## A nova ferramenta, e por que ela vem primeiro

`RADAR DO FUTURO` responde *o que pode importar depois*. `RADAR` responde *o que está acontecendo*. A ordem no produto é essa, e há **uma única porta** entre os dois: `CURRENT_FIELD_CONFIRMATION`.

A régua tem seis estados e cada promoção exige evidência nova — nenhum tema sobe por releitura do que já está escrito:

`OBSERVED_TOPIC` → `SCIENTIFIC_SIGNAL` → `EMERGING_THEME` → `WATCHLIST_PRIORITY` → `ALMOST_RADAR_CASE` → `PROMOTED_TO_RADAR`

## MOMENTUM = NOT_KNOWN em todos os sete temas

E isso foi **medido**, não assumido. O `group_by` por ano do OpenAlex é a rota, e o orçamento está zerado. Testei o Crossref como alternativa: a busca dele é por relevância, não booleana — *"Lolium rigidum herbicide resistance"* devolve **790.707** resultados, e a faceta por ano descreve esse conjunto difuso, não o tema. **A faceta existe e não serve.**

Primeira captura é `BASELINE_ESTABLISHED`, nunca `GROWING`. Total acumulado não é tendência.

## O achado: o registro espanhol do vallico é monocultura de modo de ação

Duas consultas ao ROPF fecharam o tema mais forte da Espanha.

**`TRIGO × VALLICO`: 9 registros no país inteiro, e 8 são inibidores de ACCase** (6 clodinafop, 2 diclofop). Zero prosulfocarb, zero PSII no alvo declarado.

E o levantamento aleatório de 2012-13 mede **83% de resistência a ACCase na Cataluña** — contra 74% ainda suscetível em Castilla y León.

O herbicida de recurso que a literatura descreve existe na Espanha **só na categoria genérica**: 8 registros de prosulfocarb em `TRIGO × MONOCOTILEDÓNEAS`, **nenhum da ADAMA**. Um deles é o `AUROS` — exatamente o produto que o artigo de 2021 testou contra as populações resistentes. E **flufenacet, que o artigo aponta como a substância com atividade principal contra Lolium, tem zero registros** nesse par.

## Dois temas estão na lista para mostrar a régua funcionando

**Septoriose** é o contra-exemplo: é o par com **mais** ciência recente (55% desde 2023) e o campo **mais** quieto (segundo ano mais fraco de 15). Um motor que promovesse por volume de papers teria promovido esse — e teria errado.

**Xylella** é o maior agrupamento científico do quadro do olivar — 76 de 152 pesquisadores — e fica no estado 1. Volume não compra estado: é uma camada só.

O mesmo padrão se repete na Itália, e lá é ainda mais nítido: **trigo × Fusarium tem mais ciência que milho × micotoxina (243+78 contra 208) e fica num estado mais baixo**, porque tem uma camada só.

## Camada de exibição

29 regras em PT, EN e ES, cada uma com a regra semântica. A que mais importa: `EXPLICIT_SPECIES_RESPONSE = NONE` tem de **nomear o registro** como o lugar da ausência nas três línguas. *"A ADAMA não tem solução"* está na lista de proibições de tradução.

E a acentuação acontece **aqui e em nenhum outro lugar** — era essa a lacuna que o protótipo revelou.

## Handoff para o Claude Design

`DESIGN-DATA-CONTRACT-V1`: modelo de navegação com o Radar do Futuro antes do Radar, 8 tipos de página, 10 contratos de componente com regra dura, semântica de linha de produto **sem cor hex** — e um teste que reprova se aparecer hex na inteligência.

O aviso que mais importa: **`NÃO SEI`, `NOT_COLLECTED`, `NOT_KNOWN`, `AUSENTE_MEDIDO` e `NAO_TESTADO` são cinco coisas diferentes.** O pior erro possível é colapsar *"procurei e não há"* com *"não procurei"* — são o oposto uma da outra em esforço e em confiança.

## França

A escala fechou pelo Eurostat: 21 culturas medidas no lugar de 4 amostradas. Trigo mole 4.214,6 · oleaginosos 2.233,0 · cevada 1.808,5 · milho grão 1.593,9 · **uva 741,3** — a videira estava totalmente ausente antes.

O contraste com a Espanha não é de escala, é de **estrutura**: Espanha lidera por cevada mais olivar; França por trigo mais um bloco oleaginoso de 2,2 milhões de ha que a Espanha não tem.

Agreste ficou `BLOCKED_ON_TESTED_ROUTES`, e com um detalhe que vale registrar: o `data.gouv.fr` tem 28 conjuntos Agreste, e o único recurso da Statistique Agricole Annuelle é **um link de volta para o host bloqueado**.

## Um teste meu nasceu errado de novo, do mesmo jeito

Proibi a palavra "seguidores" no arquivo do `RESEARCHER_OUTLOOK` inteiro — e ela aparece justamente na frase que a proíbe. É o mesmo padrão do "23 safras". Corrigido para percorrer campo a campo e só aceitar o termo dentro de um campo de regra.

Três vezes agora. O padrão tem nome: **a proibição escrita no arquivo dispara a própria proibição.**
