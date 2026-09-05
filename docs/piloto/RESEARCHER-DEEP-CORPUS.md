# CORPUS PROFUNDO DO PESQUISADOR — primeiro lote

`DATASET_OWNER = RESEARCHER_CORPUS_EAME` · referência **2026-08-30** · janela desde
**2019-01-01** · `APIFY_RUNS = 0` · `COST_USD = 0` · nenhum runner de missão bloqueante
foi ocupado.

Artefatos: [`RESEARCHER-CORPUS-EAME-V1.json`](../../data/samples/RESEARCHER-CORPUS-EAME-V1.json)
· [`EXPERT-DIRECTORY-EAME-V1.json`](../../data/samples/EXPERT-DIRECTORY-EAME-V1.json)
· código em [`scripts/corpus_pesquisador.py`](../../scripts/corpus_pesquisador.py).

Esta missão é **auxiliar e não bloqueante**. Ela não reabre
`TECHNICAL_PERSON_SENSOR = NOT_PROVED`, não tenta provar que YouTube pessoal é fonte
diária, e não amplia o universo de pessoas. O universo é fechado nos **12 já provados**.

---

## Dois erros medidos no caminho — e o que eles custariam se não tivessem caído

Ficam registrados porque os dois produziriam número bonito e falso.

**1 · A prova que aprovava tudo.** A primeira versão tratou "o ORCID aparece na autoria
da obra" como prova de pessoa. Resultado: **763 de 763 aprovadas**. Prova que aprova tudo
não é prova. O OpenAlex **herda** o ORCID do perfil do autor e o carimba em toda obra
atribuída àquele id — inclusive numa página final de revista de ciências humanas
(*"Pages de fin"*, no Cairn.info) atribuída a Frédéric Suffert. A prova passou a exigir
evidência escrita **naquela obra**: ou o DOI está na lista de obras do ORCID da própria
pessoa, ou a autoria daquela obra declara a instituição já provada.

**2 · "crete" dentro de "secreted".** A busca de país comparava pedaço de string. Vinte
e dois materiais saíram com `COUNTRY_OF_FACT = GR`; **vinte e um** eram artigos de efetor
fúngico onde a palavra encontrada era *secreted*. Depois da correção para palavra
inteira, sobrou **1** — o único que realmente nomeia a Grécia. Um relatório que dissesse
"22 materiais na Grécia" teria posto a Grécia num mapa por causa de um verbo.

---

## A · 12 pesquisadores tentados

Todos os 12 com `IDENTITY_PROVED` ou `IDENTITY_PROVED_COUNTRY_SINGLE_SOURCE` no
`SPEAKER-UNIVERSE-PILOT-V1`. O 13º (`Lukas Meile`, `IDENTITY_PARTIAL_COUNTRY_PAST`)
ficou de fora — identidade parcial não vira acervo.

Falhas de fonte: **0** em 36 chamadas.

## B · identidades e canais públicos confirmados

O ORCID devolve o que a **própria pessoa** declarou. Dez das doze declaram obras lá;
**duas** declaram endereço público:

| pessoa | obras declaradas no ORCID | canais/páginas declarados |
|---|---:|---|
| Jesús Mercado‐Blanco | 245 | página do grupo no CSIC · perfil IOBC‑WPRS |
| Frédéric Suffert | 0 | página pessoal INRAE · página do projeto CAW · Twitter/X `@wheatpath` |
| Blanca B. Landa | 463 | — |
| Antonio Logrieco | 177 | — |
| Massimo Blandino | 128 | — |
| F. Quaglino | 99 | — |
| Andrea Sánchez‐Vallet | 49 | — |
| Thierry C. Marcel | 43 | — |
| François Delmotte | 41 | — |
| Nicola Mori | 27 | — |
| Cristian Carrasco‐López | 15 | — |
| Isabelle D. Mazet | 0 | — |

**10 de 12 não declaram nenhum endereço público.** Isso é coerente com o
`SENSOR-PILOT`: a rota "canal pessoal" é magra por natureza, não por má coleta.

## C · materiais coletados

**763** materiais únicos. Destes, **582** passam nas duas portas e valem como evidência.

## D · materiais por tipo (só os 582)

`PEER_REVIEWED_PAPER` 426 · `PREPRINT` 115 · `OTHER_TECHNICAL_PUBLICATION` 34 ·
`BOOK_CHAPTER` 6 · `REVIEW` 1.

**Zero** apresentação de congresso, webinar, vídeo institucional, post e entrevista. A
rota de paper não devolve esses tipos — e este lote não usou nenhuma outra rota. É
ausência de coleta, não ausência do mundo.

## E · recência (contada de 2026-08-30)

`LAST_30D` 4 · `LAST_90D` 11 · `LAST_180D` 8 · `LAST_365D` 29 · `OLDER_ARCHIVE` 530.

**23 em 582 nos últimos 180 dias — 4%.** Nove em dez materiais são arquivo. Isso não os
desqualifica: arquivo bom explica mecanismo e dá contexto. Só não é sinal novo.

## F · materiais relevantes por recorte congelado

| recorte | materiais no recorte | prontidão |
|---|---:|---|
| IT-DURUM_WHEAT-FUSARIUM | 86 | ambos com material recente |
| IT-VINE-FLAVESCENCE | 54 | ambos com material recente |
| FR-CEREAL-SEPTORIA | 44 | Suffert recente · Marcel só arquivo |
| FR-VINE-DOWNY_MILDEW | 38 | Mazet recente · Delmotte só arquivo |
| ES-CEREAL-SEPTORIA | 21 | Sánchez‐Vallet recente · Carrasco‐López só arquivo |
| **ES-OLIVE-REPILO** | **0** | **os dois ficam em IDENTITY_ONLY** |

### O buraco do olivar, com nome

Nos 194 materiais dos dois pesquisadores de `ES-OLIVE-REPILO` desde 2019, a palavra
*repilo* — e também *Venturia oleaginea*, *Spilocaea oleagina* e *Fusicladium
oleagineum* — **aparece zero vez**. O assunto real deles é **Xylella fastidiosa**
(42 materiais de Blanca Landa) e verticilose.

Uma sonda diagnóstica de uma chamada mostra que a literatura de repilo existe: **74
obras no mundo desde 2019, com 25 autores de afiliação espanhola** — e nenhum deles é um
dos dois provados. Ou seja: o portão de identidade daquele recorte trouxe **gente de
oliveira**, não **gente de repilo**. Isso não invalida a identidade das duas pessoas;
invalida a suposição de que elas cobrem aquele par. É a correção mais barata disponível
para um segundo lote, e ela **não** foi executada aqui (a missão pediu profundidade, não
largura).

## G · papers / apresentações / vídeos / posts

Papers e preprints: 541. Apresentações: 0. Vídeos: 0. Posts: 0. Ver **D**.

## H · transcrições

**0.** Nenhum vídeo ou áudio foi coletado neste lote, então não houve o que transcrever.
A regra "classificar relevância antes de transcrever" não chegou a ser exercida.

## I · COUNTRY_OF_FACT

**174 em 582 (30%)** têm país do fato sustentado por trecho do próprio texto:
IT 78 · ES 32 · FR 31 · TN 11 · GB 7 · CH 3 · DE 2 · US 2 · AR 2 · BR 2 · GR 1 · PT 1 · CN 1.

Os outros 408 saem `NÃO SEI`. A afiliação do autor **nunca** foi promovida a país do
fato, e o idioma nunca decidiu nada. A Tunísia com 11 é o melhor exemplo de por que a lei
existe: são pesquisadores europeus escrevendo sobre campo tunisiano.

## J · CROP · K · ISSUE · L · CHAVE COMPLETA

`PROVED_CROP` 333 (57%) · `PROVED_ISSUE` 325 (56%) · **chave completa (país + cultura +
problema + data) 76 (13%)**.

## M · ORIGINAL_RESEARCH · N · EXPLICAÇÃO

Originalidade: `ORIGINAL_RESEARCH` 498 · `REVIEW_SYNTHESIS` 45 · `OTHER` 39.

Papel do material: `NEW_SCIENTIFIC_EVIDENCE` 181 · `METHOD_MECHANISM` 158 ·
`DISEASE_PEST_MONITORING` 143 · `MANAGEMENT_GUIDANCE` 50 · `REVIEW_SYNTHESIS` 45 ·
`EXPERIMENT_RESULT` 5.

Material de explicação para leigo (`EXPLANATION`, `PUBLIC_EXPERT_COMMENTARY`): **0** —
esse tipo mora em webinar, entrevista e post, e nenhum foi coletado.

## O · duplicação

**62 duplicados interceptados** na chave `DOI → id do OpenAlex`, sobre 825 registros
brutos: **7,5%**. São coautorias entre os 12 — o mesmo paper chegando por duas pessoas.
Ele entra **uma vez** e aparece nas duas fichas por referência, nunca contado duas vezes.

## P · exemplos de evidência (materiais dos últimos 180 dias, com chave forte)

| data | pessoa | cultura / problema | país do fato | material |
|---|---|---|---|---|
| 2026-08-14 | F. Quaglino | VINE / FLAVESCENCE | IT | genes efetores revelam diversidade genética oculta |
| 2026-04-30 | Isabelle D. Mazet | VINE / DOWNY_MILDEW | FR | desempenho de longo prazo de castas resistentes |
| 2026-05-25 | Massimo Blandino | MAIZE | IT | índice de seca para decisão de nitrogênio na safra |
| 2026-08-19 | Andrea Sánchez‐Vallet | CEREAL / SEPTORIA | NÃO SEI | enzima do patógeno degrada sinal imune da planta |
| 2026-08-01 | Nicola Mori | VINE / FLAVESCENCE | NÃO SEI | absorção foliar e eficácia de controle do vetor |

## Q · pesquisador → material → prontidão de caso

`READY_WITH_RECENT_MATERIAL` 7 · `READY_ARCHIVE_ONLY` 3 · `IDENTITY_ONLY` 2.

Cinco dos seis recortes já abrem com nome + material. Um (`ES-OLIVE-REPILO`) abre só com
nome.

## R · junções de convergência possíveis

O `EXPERT-DIRECTORY-EAME-V1` junta por `COUNTRY × CROP × ISSUE`. Onde a junção fecha hoje:

- **IT × VINE × FLAVESCENCE** — 54 materiais, dois pesquisadores, ambos recentes, e a
  maior massa de `COUNTRY_OF_FACT = IT` do acervo (78). É o recorte mais pronto.
- **FR × CEREAL × SEPTORIA** e **FR × VINE × DOWNY_MILDEW** — material forte e país do
  fato sustentado; a recência depende de uma pessoa em cada par.
- **IT × DURUM_WHEAT × FUSARIUM** — muito material, mas boa parte é **milho**, não trigo
  duro. A junção existe; o par exato é mais magro do que o volume sugere.

## S · o que isto acrescenta ao Expert Directory

Antes: nome, instituição, ORCID. Agora, abrindo um caso, dá para mostrar embaixo do nome
**o material, com data, DOI, tipo, papel e o trecho que sustentou cada campo** — e dizer
se ele é recente ou arquivo. Em cinco dos seis recortes isso já existe.

## T · o que isto NÃO prova

- **Não prova early signal.** Pesquisador publicou algo ≠ sinal. O material ainda tem que
  passar por `COUNTRY × CROP × ISSUE × TIME` + independência + convergência.
- **Não prova confirmação de campo.** Nenhum destes 582 é produtor relatando lavoura.
- **Não prova que estas pessoas falam publicamente hoje.** 10 de 12 não declaram canal.
- **Não prova cobertura do olivar espanhol.** Prova o contrário, com número.
- **Não prova o que o classificador diz.** `CROP`, `ISSUE`, `COUNTRY_OF_FACT` e o papel
  do material saem de **termo encontrado no texto**. Polissemia gera falso positivo e
  nenhum portão automático pega — cada campo carrega o trecho que o sustentou justamente
  para que a conferência seja humana. O caso "crete/secreted" é a prova de que isso
  acontece de verdade.
- **Não cobre 2018 para trás.** A janela começa em 2019, por decisão.

## U · execuções, itens, custo

36 chamadas HTTP gratuitas (24 ORCID + 12 OpenAlex) + 1 sonda diagnóstica. 825 registros
brutos → 763 únicos → 582 evidências. **0 execução Apify · US$ 0 · 0 runner ocupado.**

## V · entrega opcional para inteligência

`OPTIONAL_REFRESH_INPUT = READY`. O `EXPERT-DIRECTORY-EAME-V1` pode entrar como camada
**RESEARCHER / SCIENCE CONTEXT** do caso sem tocar em nenhum outro owner. Se o refresh
obrigatório vier antes, **não bloquear**: esta camada é aditiva e espera.

---

## Onde valeria aprofundar — medido, não achado

1. **Trocar as duas pessoas do `ES-OLIVE-REPILO`.** É o único recorte sem material, e
   já existem 25 autores espanhóis de repilo identificados. Rendimento esperado alto,
   custo zero (rota gratuita).
2. **Buscar apresentação e webinar por rota institucional** (página do lab, canal da
   universidade, sociedade científica). Hoje o acervo é 100% paper, e as perguntas
   "explicou o mecanismo?" e "há material que ajuda a explicar este caso para o cliente?"
   continuam sem resposta.
3. **Não aprofundar canal pessoal.** Duas pessoas declaram endereço público; uma delas é
   um Twitter/X. Nada aqui contradiz o `NOT_PROVED` — e insistir seria gastar para
   reconfirmar o que já foi medido.
