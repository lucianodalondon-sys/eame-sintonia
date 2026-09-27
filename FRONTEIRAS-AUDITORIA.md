# FRONTEIRAS-AUDITORIA — know-how, Italian Agro Brain e Bíblias (D109)

Auditoria **só de leitura** (coordenação 12:58; regra do dono D109, `auditoria-madrugada/REGRA-KNOWHOW-BRAIN-BIBLIAS.md`).
Lido no vivo **`2ef6fef8`** por `git show` — **nenhum dos três documentos foi alterado**. Ramo `fronteiras-auditoria-v1`.
Lista inteira, linha a linha: `data/derivados/FRONTEIRAS-AUDITORIA/MISTURAS.json` (gerada por `varrer.py.txt`).

```
CONTENT_CLASSIFICATION (esta entrega)
KNOW_HOW = NO · ITALIAN_AGRO_BRAIN = NO · BIBLE_CHANGE = NO · HANDOFF_ONLY = YES (é um relatório de auditoria)
```

## 0. Como se mediu, e o que a medida não prova
- Três padrões **declarados** no `varrer.py.txt`: (1) cabeçalho ou parágrafo normativo («LEI», «REGRA», «DEVE»,
  «NUNCA», «PROIBIDO», «OBRIGATÓRIO», «CANÓNICO»); (2) termo agronómico (organismos, doenças, eventos de campo,
  culturas, preços, nomes da lista de pesquisadores do dono), com gravidade maior se a linha tem valor ou data de campo;
  (3) marca de diário (MEDIDO, data, commit, bug, «nesta missão», «hoje», SHA).
- **É uma heurística para ler, não um veredito.** Cada linha abaixo foi lida à mão na parte que a tabela mostra; as
  restantes estão no JSON. Um padrão errado custou uma volta: o `\b` escrito pelo terminal virou caractere invisível
  e a primeira passada não achou nada (armadilha já registada) — refeita com o editor.
- O coordenador mediu **67** cabeçalhos normativos no know-how; a minha regra dá **62 cabeçalhos + 4 parágrafos
  «A REGRA.» = 66**. A diferença é o padrão (não sei o exato dele); não muda a conclusão.

| documento (linhas) | mistura | achados |
|---|---|---|
| `SINTONIA-EAME-KNOW-HOW.md` (22 491) | norma dentro do know-how | 66 (≈20 de facto normativas — secção 1) |
| | dado agronómico | **3**, todos exemplos técnicos (secção 2) |
| `BIBLIA-CANONICA-DA-COLETA.md` (3 015) | diário / medição / estado dentro da lei | 98 linhas marcadas → **≈40 blocos reais** (secção 3) |
| | dado agronómico | **1** (exemplo de normalização) |
| `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` (2 489) | diário / medição / estado | 51 linhas → **§29, §31, §33 e 5 blocos «medido»** |
| | dado agronómico | **3** (exemplo de normalização) |

**Gravidade:** ALTA = regra oficial do sistema que vive fora da Bíblia (ou dado agronómico dado como facto numa Bíblia) ·
MÉDIA = diário/medição/estado dentro da Bíblia, ou regra do sistema duplicada no know-how · BAIXA = título de lição com
forma de regra, regra de **método de trabalho** (que é know-how legítimo: «formas corretas de operar»), ou termo
agronómico usado como exemplo técnico.

## 1. KNOW-HOW com secções normativas

| linha | secção | o que é | casa correta | gravidade |
|---|---|---|---|---|
| 449 | «# 8. LEIS OPERACIONAIS DA COLLECTION QUE NÃO PODEM SER ESQUECIDAS» | lista de leis do sistema (`RAW != DERIVED…`, `ONE CONCEPT → ONE OWNER`…) que a Bíblia já tem | BÍBLIA (ficam lá); no know-how, só o ponteiro | **ALTA** (duas cópias da mesma lei divergem) |
| 19062 | «A SEGUNDA CORRIDA DO CANÁRIO É GATE OBRIGATÓRIO ANTES DA BIG COLLECTION» | gate do sistema escrito como obrigação | BÍBLIA (se é regra oficial) ou contrato de gate | **ALTA** — NAO SEI se a Bíblia a tem; confirmar |
| 168 | «Lei operacional do mapa» | regra do mapa (a Bíblia tem `COL-LAW-046/047`) | BÍBLIA; know-how com o aprendizado | MÉDIA (duplicação) |
| 1279 | «26. MANIFESTO CANÓNICO DOS CARDS» | texto canónico (já marcado SUPERSEDED) | histórico no know-how; nada canónico | MÉDIA |
| 2616 · 3144 · 3206 · 4014 · 9648 · 13036 · 13286 · 13417 · 13773 · 21782 | «AS TRÊS REGRAS DO TRADUTOR», «uma regra de método nova», «A REGRA GERAL», «A regra que fica», «DUAS LEIS DE FIAÇÃO» | regras aprendidas; parte é método (know-how), parte pode ser regra do sistema | ler uma a uma: método → fica; regra do sistema → Bíblia/contrato | MÉDIA |
| 2124 | «44. LEI DO NÚMERO CITADO NUM DOCUMENTO HUMANO» | regra de **método** para relatórios | KNOW-HOW (é forma de operar) — trocar «LEI» por «regra de trabalho» | BAIXA |
| 84 | «1. REGRA-MÃE DO SINTONIA» («NÃO SUPOR. MEDIR.») | método de trabalho | KNOW-HOW | BAIXA |
| 4038 | «58.7 · ONDE A LEI FICOU, E POR QUÊ NÃO NA BÍBLIA» | decisão já documentada de pôr a regra num contrato | nenhuma mudança | BAIXA |
| 20040 · 21263 · 21301 · 22435 | parágrafos «**A REGRA.**» (telemetria, cutover, observador) | decisões de engenharia/operação | KNOW-HOW | BAIXA |
| 18690 · 19156 · 7736 · 8513 · 8569 · 9486 · 19453 · 14093 · 14243 · 17223 · (≈30 mais) | títulos de lição com «NUNCA»/«LEI» («`UNKNOWN` NUNCA É `NEVER`…») | lição com forma de regra | KNOW-HOW (é lição) | BAIXA — não é mistura |

## 2. Dado agronómico fora do Brain

| arquivo:linha | trecho | leitura | casa correta | gravidade |
|---|---|---|---|---|
| know-how:2843 | «`climatologia` está nos boletins de VITE…» | exemplo de classificação de fonte | know-how (exemplo) | BAIXA |
| know-how:2858 | «U.O. Fitosanitario — Bollettino n. 20 VITE → **T3**» | título de boletim como caso de teste | know-how (exemplo) | BAIXA |
| know-how:2930 | «os boletins da ARIF Puglia … só depois trazem *Bactrocera*» | forma do PDF (sinótico antes da praga) → caso AMBÍGUO | know-how, sem o organismo («a praga») | BAIXA |
| Coleta:1811 | `ORIGINAL "frumento tenero"` (COL-LAW-203) | exemplo de valor original × normalizado | Bíblia (exemplo da regra) | BAIXA |
| Intelligence:522 · 523 · 527 | `VITE` · `VITE DA VINO` · `VITE DA TAVOLA` (INT-LAW-081) | exemplo de equivalência de conceito | Bíblia (exemplo da regra) | BAIXA |

**No vivo, o know-how e as Bíblias quase não têm dado agronómico** — só exemplos técnicos. O risco estava nos
**ramos por instalar**: a minha própria `lei-pesquisadores-v1` trazia séries de monitorização, organismos, a lista de
docentes e medições do dia nas Bíblias e na §222; **já limpo** (`78dd6790`). Os outros ramos por instalar **não foram
auditados** (NAO SEI).

⚠️ **Não existe Italian Agro Brain no vivo** (nenhum ficheiro nem secção com esse nome em `2ef6fef8`). O conhecimento
agronómico medido vive hoje em relatórios de missão e `data/derivados/` (séries, limiares, listas de pessoas) — sem casa
canónica.

## 3. Bíblias com diário, medição do dia ou estado de implementação

**Bíblia da Coleta — blocos que são diário/estado, não regra** (linha · marca):
334 «ESTADO HONESTO» · 356 «MEDIDO» · 498 «ESTADO HONESTO» · 546 «MEDIDO» · 633 «MEDIDO, e é o caso que obriga a lei» ·
754 «POR QUÊ, medido» · 927 «DECISÃO EM ABERTO» · 1138–1258 (COL-LAW-043: medição com um facto de 25 campos) · 1230
«Medido contra PostgreSQL 16» · 1359 «ESTADO HONESTO» · 1620 «MEDIDO» · 1772 «defeito C-001» · 1989 «MEDIDO» · 2119
«MEDIDO» · 2198 «não foi implementada nesta missão» · 2251 «MEDIDO» · 2280 «VIOLAÇÃO VIVA, medida hoje» · 2285 «NADA FOI
MIGRADO NESTA MISSÃO» · 2337 · 2371 · 2397 · 2419 · 2438 · 2471 · 2488 · 2504 «MEDIDO» · 2559 «Medido: o Reference Plane
NÃO EXISTE hoje» · 2662 «NENHUMA TABELA FOI CRIADA NESTA MISSÃO» · 2718–2720 «MEDIDO … estava errada» · 2764 «MEDIDO» ·
2778 «não foi corrigido nesta missão» · 2807 · 2818 · 2843 · 2855 «NÃO IMPLEMENTADO NESTA MISSÃO» · 2892 «MEDIDO.
2026-09-11» · 2921 «NÃO IMPLEMENTADO NESTA MISSÃO».

| tipo | casa correta | gravidade |
|---|---|---|
| «MEDIDO, e é o caso que obriga a lei» (≈25 blocos) | a **regra** fica; a medição vai para o diário de decisões / know-how, com ponteiro | MÉDIA |
| «ESTADO HONESTO», «VIOLAÇÃO VIVA», «não implementado nesta missão» (≈12) | estado de implementação → **matriz de conformidade** (`docs/biblia/CONFORMIDADE-ITALIA.md`, que já existe para isto) | MÉDIA |
| «DECISÃO EM ABERTO» (927) | diário / handoff até ser decidida | MÉDIA |
| cabeçalho (`EFFECTIVE_FROM`, `HEAD_AO_CONGELAR`) e histórico constitucional | **fica** — a COL-LAW-069 exige versão e histórico | não é mistura |

**Bíblia da Intelligence:**

| linhas | o quê | casa correta | gravidade |
|---|---|---|---|
| 1301–1357 (§29) | origem das leis: benchmarks com caminhos em `research/` | referência curta fica; o estudo é SINTONIA LAB | MÉDIA |
| 1379–1422 (§31) | registo da promoção (datas, 9/9 PASS) | diário de decisões | MÉDIA |
| 1460–1606 (§33) | vereditos históricos e o corrente | **o corrente fica** (o portão `controle/portao_do_controle.py` exige um só `VEREDITO = CORRENTE`); os históricos → diário | MÉDIA — mexer exige mudar o portão |
| 1624 · 1788 · 1921 · 2031 · 2335 | «caso medido hoje», «Medido:», «Bloqueio medido», «Medido em…», «a medição … a 2026-09-14» | estado → conformidade / know-how | MÉDIA |
| 2438–2458 (§37.4) | as leis recusadas e porquê | diário (é razão, não regra) | BAIXA |

## 4. O bloco

```
KNOW_HOW_BOUNDARY            = UNCLEAR
ITALIAN_AGRO_BRAIN_BOUNDARY  = UNCLEAR
BIBLE_BOUNDARY               = UNCLEAR

CURRENT_MIXUPS_FOUND =
  KNOW-HOW   66 marcas normativas; ≈20 reais: 2 ALTA (§8 leis operacionais da Collection, l.449;
             gate do canário, l.19062), ≈13 MÉDIA (regra do mapa, manifesto dos cards, «regras que ficam»),
             o resto BAIXA (método de trabalho e títulos de lição). Dado agronómico: 3 exemplos técnicos (BAIXA).
  COLETA     ≈40 blocos de diário/estado dentro das leis (MEDIDO · ESTADO HONESTO · nesta missão), MÉDIA;
             1 exemplo agronómico (BAIXA).
  INTEL      §29 benchmarks, §31 registo de promoção, §33 vereditos históricos, 5 blocos «medido» — MÉDIA;
             3 exemplos agronómicos (BAIXA).
  BRAIN      a casa não existe no vivo: o conhecimento agronómico vive em relatórios e data/derivados.

CHANGES_NEEDED =
  1. Criar a casa do ITALIAN AGRO BRAIN (nome, dono, formato) antes de mover qualquer dado para ela.
  2. Know-how §8 (l.449): trocar a lista de leis por ponteiros para a Bíblia; confirmar se o gate do canário
     (l.19062) é regra oficial — se sim, Bíblia/contrato; se não, reescrever como lição.
  3. Bíblia da Coleta: tirar os blocos MEDIDO/ESTADO para o diário e a matriz de conformidade, deixando a
     regra e um ponteiro — em lote, com o validador (valida_biblia.py) e os testes da Bíblia a verde.
  4. Bíblia da Intelligence: §31 e os vereditos históricos de §33 para o diário; §29 reduzida a referência —
     só depois de ajustar o portão do controlo, que lê o bloco CORRENTE.
  5. Em todas as missões: o gate CONTENT_CLASSIFICATION antes de escrever (já aplicado na LEI-PESQUISADORES).

DOCUMENTS_AFFECTED =
  SINTONIA-EAME-KNOW-HOW.md · BIBLIA-CANONICA-DA-COLETA.md · BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md ·
  docs/decisoes/DIARIO-DE-DECISOES.md (recebe) · docs/biblia/CONFORMIDADE-ITALIA.md (recebe) ·
  controle/portao_do_controle.py (se §33 mudar) · Italian Agro Brain (a criar)

NEXT_SAFE_STEP =
  Decisão do dono: onde vive o Italian Agro Brain. Enquanto não houver, NÃO mover dado agronómico —
  mover sem casa é perder. Primeiro passo que se pode fazer já, sem risco: no know-how, trocar a §8 (l.449)
  por ponteiros para as leis da Bíblia (1 secção, só texto, validador da Bíblia não é tocado).
```

## EM PALAVRAS SIMPLES
- **O que fiz:** li os três documentos grandes da casa — o caderno de aprendizados (know-how), a regra da coleta e a
  regra da inteligência — e marquei onde uma coisa está na gaveta errada. **Não mudei nada** neles.
- **O que achei:**
  - O **caderno de aprendizados tem regras dentro.** A mais séria é uma lista de "leis que não podem ser esquecidas",
    que repete as leis da Bíblia — duas cópias da mesma regra acabam discordando. E uma "obrigação" (fazer duas vezes o
    teste de coleta antes da coleta grande) que não sei se está na Bíblia.
  - As **Bíblias têm diário dentro:** cerca de 40 trechos do tipo "medimos isto no dia tal" ou "isto não foi feito
    nesta missão". Isso é história; a Bíblia devia guardar só a regra.
  - **Quase não há dado de agricultura** no caderno nem nas Bíblias — só exemplos (a palavra "vite", "frumento tenero").
    O perigo estava na minha própria entrega de ontem, que eu já limpei.
  - **O "cérebro do agro italiano" ainda não existe** como documento. Os dados de campo estão espalhados por relatórios.
- **O que muda para você:** decidir onde vai morar esse "cérebro". Até lá, é mais seguro não mexer nos dados de
  agricultura, porque mudar de lugar sem ter o lugar novo é perder.
