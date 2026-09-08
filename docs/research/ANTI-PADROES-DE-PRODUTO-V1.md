# ANTI-PADRÕES DE PRODUTO — SINTONIA EAME V1

**Objetivo:** impedir que crescimento de dados ou acabamento visual seja confundido com crescimento de valor.

## 1. Catálogo principal

| Anti-padrão | Por que é perigoso no SINTONIA | Regra de defesa |
|---|---|---|
| DATA DUMP | transforma coleta em produto | dado precisa chegar a uma decision question ou camada de evidência |
| DASHBOARD THEATER | charts dão aparência de controle sem próxima ação | todo painel precisa responder `SO WHAT / WHAT CAN I DO?` |
| TOO MANY NUMBERS | exige interpretação do usuário e esconde prioridade | acima da dobra só números que mudam decisão |
| TECHNICAL LANGUAGE FIRST | Sales/RTV precisa traduzir antes de agir | plain-language call primeiro, detalhe técnico on-demand |
| SOURCES DOMINATE SCREEN | prova ocupa o espaço da decisão | evidence state visível + drawer a um clique |
| SOURCE HIDDEN | resumo vira impossível de auditar | cada claim material deve chegar ao original |
| SOURCE AS UI HERO | bibliografia substitui inteligência | fonte sustenta a call, não é a call |
| ACTION HIDDEN | usuário entende mas não encaminha | uma primary action visível por card |
| FALSE URGENCY | tudo parece importante e mata confiança | urgency deriva de janela/deadline/state transition |
| FAKE PREDICTION | weak signal vira futuro afirmado | Future usa horizon, triggers, strengthen/weaken, unknown |
| ONE MAGIC SCORE | mistura dimensões não equivalentes | mostrar fatores separados e explicáveis |
| TOOL PER DATASET | menus crescem conforme fontes | ferramenta nasce de decision question, não do dataset |
| TOOL PER DEPARTMENT | cria verdades paralelas | one intelligence product → N role projections |
| CHART WITHOUT SO-WHAT | usuário precisa descobrir sozinho por que olhar | Market/other charts precisam declarar decisão afetada |
| LONG AI SUMMARY | troca data dump por text dump | 3s/30s/3min progressive disclosure |
| ALL CARDS LOOK IDENTICAL | apaga diferenças epistemológicas | família visual comum, semântica específica por produto |
| EVERYTHING IS AN ALERT | produz alert fatigue e despriorização | alert somente em mudança material de action state |
| EVERYTHING IS A TOOL | governança/evidência vira menu de usuário | reclassificar foundational/supporting/delivery layers |
| PDF AS DATABASE DUMP | exporta complexidade e congela contexto | brief curado + snapshot/version + link para verdade atual |

---

## 2. Anti-padrões específicos do SINTONIA

### CALENDAR-AS-PHENOLOGY

**Erro:** tratar calendário esperado como observação do estádio real.

**Consequência:** Opportunity parece mais preciso que a evidência.

**Defesa:** `CALENDAR DATE ≠ OBSERVED PHENOLOGY`; marcar estimated/observed separadamente.

### PRODUCT-ON-CROP-AS-SOLUTION

**Erro:** concluir que um produto resolve o problema porque é usado naquela cultura.

**Consequência:** cria falsa oportunidade comercial.

**Defesa:** precisa haver ligação comprovada entre problema/target e resposta ADAMA, respeitando label.

### FIELD-VOICE-AS-INCIDENCE

**Erro:** volume de fala/post/vídeo vira ocorrência agronômica.

**Consequência:** social attention é promovida a fato.

**Defesa:** Field Voice = signal/sensor/lead; incidence exige evidência apropriada.

### SOURCE-LOCATION-AS-FACT-LOCATION

**Erro:** usar país/região do autor/fonte como local do acontecimento.

**Defesa:** manter `SOURCE_LOCATION` e `FACT_LOCATION` separados; ausência = UNKNOWN.

### PUBLICATION-TIME-AS-FACT-TIME

**Erro:** data do post/paper vira data do acontecimento.

**Defesa:** publication/observation/collection/fact time são campos distintos.

### REGULATORY-DEADLINE-MIXING

**Erro:** prazo de substância/concorrente ou status regulatório europeu aparece como se fosse prazo do produto ADAMA.

**Defesa:** vínculo explícito produto/substância/owner e label truth antes de qualquer call.

### APPROVED-FACT-AS-OPPORTUNITY

**Erro:** um fato regulatório positivo por si só vira oportunidade.

**Defesa:** Opportunity exige problema + tempo + geografia + resposta ADAMA + evidência de relevância.

### MODEL-CONFIDENCE-AS-TRUTH

**Erro:** badge de confidence cria aparência de probabilidade calibrada.

**Defesa:** explicar confidence in what, evidence maturity, coverage, contradiction e freshness.

### OBSERVATION-AS-FORECAST

**Erro:** sinal observado é estendido para trajetória futura sem modelo/evidência.

**Defesa:** Future separa observed signal, hypothesis, forecast/model e trigger.

### FORECAST-AS-FACT

**Erro:** saída de modelo/DSS vira acontecimento certo.

**Defesa:** horizon, dependency e uncertainty sempre preservados.

### AGGREGATION-WITHOUT-DECISION

**Erro:** `157 Market Pulse` parece valor porque existem 157 linhas.

**Defesa:** só promover a hero card quando existe decisão/papel possivelmente afetado.

### MOBILE-AS-SHRUNK-DESKTOP

**Erro:** portal responsivo é tratado como experiência de campo.

**Defesa:** RTV mobile brief é workflow próprio: understand → ask → suggest → limitation → evidence → share.

### BRIEF-AS-NEW-TRUTH

**Erro:** PDF/email cria texto/fato não existente no intelligence product.

**Defesa:** brief é projection versionada da mesma verdade.

### CROSS-LINK-BY-KEYWORD

**Erro:** ferramentas se “ligam” porque compartilham palavras.

**Defesa:** cross-link deve usar objetos/IDs/relações governadas e declarar tipo de relação.

### OLD-DOC-AS-CURRENT

**Erro:** documentação histórica é tratada como estado atual sem medir branch/HEAD/source owner.

**Defesa:** sempre registrar ref/commit/as-of da baseline.

### DEMO-AS-CANONICAL

**Erro:** fixture/demo sustenta decisão real porque está visível.

**Defesa:** provenance class explícita; `DEMO ≠ CANONICAL`; demo não sobe por aparência.

---

## 3. Anti-padrões de Opportunity

- ordenar por `score` universal;
- ordenar por data de criação em vez de time-to-act;
- chamar tudo que é “interessante” de opportunity;
- esconder que produto/target/label link é desconhecido;
- confundir prep window com action/application window;
- CTA genérico `View details` quando a ação necessária é conhecida;
- mostrar 20 cards no mesmo estado sem agrupamento temporal.

## 4. Anti-padrões de Future

- paper said → it will happen;
- horizonte fixo arbitrário 3/6 meses para tudo;
- probability badge sem calibração;
- só evidência favorável;
- weak signal sem kill condition;
- futuro sem `who should prepare`.

## 5. Anti-padrões de Science

- lista de papers como homepage;
- paper count como maturity;
- journal prestige como conclusão;
- pesquisadores famosos como substituto de replicação/evidência;
- summary que remove boundary conditions;
- ausência de contrary evidence;
- “recent” confundido com “decision-relevant”.

## 6. Anti-padrões de Market

- commodity chart sem decisão;
- preço subiu = demanda ADAMA subirá;
- import/export change = sales opportunity automática;
- misturar crop economics, trade, weather e news num score;
- card sem crop/geography/as-of;
- market data stale sem sinalização.

## 7. Anti-padrões de Field Voices

- raw comment wall;
- sentiment universal;
- likes/views = agronomic relevance;
- creator location = fact location;
- 15 posts repetidos contados como 15 sinais independentes;
- fonte anônima tratada igual a técnico/órgão/field report;
- clustering que apaga vozes contrárias.

## 8. Anti-padrões de Portfolio / Label

- Portfolio = catálogo promocional;
- produto aparece relevante sem target/problem link;
- label excerpt sem versão/país/data;
- competitor registered use tratado como ADAMA use;
- changed label sem mostrar `what changed`;
- uma única página tentando ser catálogo, verdade regulatória e opportunity ao mesmo tempo.

## 9. Anti-padrões de alerts/delivery

- alert por toda nova fonte;
- mesma cadência para RTV e Leadership;
- push sem why now;
- digest com tudo que mudou;
- “urgent” manual sem deadline/window;
- PDF sem as-of/version;
- WhatsApp text sem link/evidence boundary;
- notification que exige abrir três telas para entender a ação.

## 10. Checklist de red-team de uma nova superfície

Antes de chamar algo de tool:

1. Qual decisão real ela melhora?
2. Quem decide?
3. Que informação produz que nenhuma outra owner produz?
4. Quais objetos consome?
5. É source of truth, intelligence product, view, supporting layer ou delivery projection?
6. O que aparece em 3 segundos?
7. Qual é a primary action?
8. Como o UNKNOWN aparece?
9. Qual é o owner do tempo e da geografia?
10. Como chega à evidência?
11. Qual transição merece alerta?
12. Qual métrica de valor não é engagement?
13. Se removermos o menu, a capacidade continua existindo em outra owner?
14. Existe dataset-as-tool disfarçado?
15. Existe demo-as-truth disfarçado?

Se a decision question não existir, **não criar ferramenta**.
