# RED TEAM DO BENCHMARK AGRO — os 20 ataques

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    RED TEAM — tenta derrubar o proprio benchmark
MEDIDO_EM  2026-09-13
```

> Um ataque **SOBREVIVE** quando o benchmark não consegue derrubá-lo — e isso é
> uma limitação nossa, não uma vitória dele.
> Um ataque **CAI** quando há prova, externa ou medida aqui, que o desmente.
> Um ataque **CAI PARCIALMENTE** quando tem um núcleo verdadeiro que fica.

---

## 1 · «Knowledge graph é moda; uma tabela resolveria.»

```
VEREDITO  CAI PARCIALMENTE — e o nucleo verdadeiro fica, e e importante.
```

**O que é verdade:** nada nesta missão exige um banco de grafos. `GRAPH MODEL ≠
GRAPH DATABASE`. Os 8 cruzamentos instanciáveis hoje resolvem-se com tabelas e
chaves estrangeiras, e o schema desta casa já os tem
(`registro_regulatorio → registro_uso → crop/issue`).

**O que não é:** três relações do agro não são tabeláveis sem perda —
`SAME_ORIGIN` (transitiva, e é o que impede contar um ensaio três vezes),
`DEPENDS_ON` (percorrida em profundidade) e `AFFECTS` (substância → produtos →
usos → culturas, com profundidade variável).

```
A TABELA RESOLVE OS FACTOS. NAO RESOLVE A PERGUNTA «ESTAS DUAS EVIDENCIAS
SAO A MESMA?», QUE E TRANSITIVA POR NATUREZA.
E essa pergunta e a que separa intelligence de contagem.
```

---

## 2 · «EPPO sozinho resolve toda a identidade agrícola.»

```
VEREDITO  CAI — com prova executavel, desta casa.
```

`data/samples/X-007-canonical-agro-dictionary.json`, sobre 1 181 pares
(cultura, alvo) e 14 931 usos autorizados do E-Phy francês:

```
resolvido por codigo EPPO ...... 105 pares (8,9 %) · 3 509 usos (23,5 %)
excluindo termos de grupo FR ... 21,1 % dos pares · 43,8 % dos usos
GROUP ......................... 683 pares · 6 927 usos
AMBIGUOUS ..................... 131 pares · 2 111 usos
UNRESOLVED .................... 262 pares · 2 384 usos
```

E a razão estrutural, não conjuntural:

```
Ble x «Rouille(s)»                        -> PUCCRT **e** PUCCST
Cerisier x «Moniliose(s) et pourriture grise» -> GLOMCI **e** PHYTCC
40 de 105 resolvidos tem EPPO_CROP com CANONICAL_CROP = null (genero/agregado)
```

O EPPO é a resposta certa **à pergunta que ele responde** — identidade do
organismo, estável sob mudança taxonómica. Não responde a medição (Crop
Ontology), fase (BBCH), língua (AGROVOC), estudo (DOI) nem área administrativa
(NUTS).

```
O ROTULO FALA A LINGUA DO AGRICULTOR. O REGISTO FALA A LINGUA DO REGULADOR.
NENHUMA DAS DUAS E A LINGUA DA TAXONOMIA.
```

---

## 3 · «Texto + LLM basta; não precisamos de dados estruturados.»

```
VEREDITO  CAI.
```

Três razões, e a terceira é fatal.

1. **O que a fonte já estruturou, reparsear é perder.** A `IT-T4-001` entrega
   CSV com `num_registrazione`. A `IT-T3-005` entrega 139 pontos de
   monitorização com lat/lon/data. Passar isso por um LLM para o voltar a
   extrair é substituir um facto por uma estimativa.
2. **Método, escala e denominador não estão no texto.** Nenhum boletim escreve
   a sua design prevalence. Um LLM que a produza está a inventá-la.
3. **Não há auditoria, nem versão, nem reprocessamento.** A `COL-LAW-042`:
   *«A VERSÃO DA REGRA É O QUE PERMITE REPROCESSAR.»* Um prompt sem versão
   torna cada erro permanente.

E a `INT-LAW-160` já fecha: **LLM é mecanismo, não fonte factual.**

---

## 4 · «Publicação recente significa facto recente.»

```
VEREDITO  CAI — e continua a acontecer neste repositorio.
```

Externo: a EPPO distingue a data do artigo do Reporting Service da data do
registo de praga. A `COL-LAW-201` dá o exemplo: notícia publicada em Roma a
07/09 sobre uma geada em Bolonha a 03/09 — quatro valores verdadeiros ao mesmo
tempo.

Interno, medido hoje:

```
_tem_quando({"published_at": "2026-06-30"})
  -> ('SIM', 'tem tempo do fato', {'quando': '2026-06-30'})
```

A `COL-LAW-031` diz, em caixa alta, que isto é **proibido, inclusive por
fallback**. O ataque não sobrevive como argumento; sobrevive como **defeito**.

---

## 5 · «Três papers significam três evidências.»

```
VEREDITO  CAI.
```

MIAPPE e BrAPI existem precisamente para tornar visível a hierarquia
`investigation → study → observation unit`: réplicas pertencem ao desenho, não
são fontes novas. Um ensaio pode gerar vários papers; uma revisão que cita o
primário não é evidência adicional; um preprint e a versão publicada podem ser o
mesmo trabalho (`COL-LAW-218`).

```
GRAFO DE DEPENDENCIA ANTES DA CONVERGENCIA.
E as chaves sao: mesmo trial · mesmo dataset · mesmo grupo · um cita o outro.
```

---

## 6 · «Um boletim que não menciona doença prova ausência.»

```
VEREDITO  CAI — e ha vocabulario internacional para o dizer.
```

ISPM 8 distingue cinco espécies de ausência:

```
pest not recorded · pest free area · pest records invalid ·
pest no longer present · pest eradicated
```

Um boletim silencioso é, no máximo, `pest not recorded` — e mesmo isso exige
saber que o boletim **procurou**. A EFSA exige população-alvo, design
prevalence e sensibilidade do método para concluir liberdade de praga.

```
NOT_FOUND_IN_SCANNED_UNIVERSE != ZERO_PROVED.
E a COL-LAW-035 ja o dizia: AUSENCIA DE EVIDENCIA != EVIDENCIA DE AUSENCIA.
```

---

## 7 · «Clima favorável prova doença.»

```
VEREDITO  CAI — e a lei ja esta escrita no contrato da fonte.
```

`regras/italy_contracts.mjs`, fontes `IT-T2-001` e `IT-T2-002`:

```
EVIDENCE_CLASS: "AGROCLIMATIC_SIGNAL"
LEI:            "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE"
```

E o teste da casa faz cumprir: *«ARPAE e AGROCLIMATIC_SIGNAL, nao sinal de campo
de praga»*. O xarvio diz o mesmo do seu lado, com as suas palavras:
**favorabilidade meteorológica** é uma camada, o risco é outra.

⚠️ **Mas a lei não atravessa a fronteira.** `EVIDENCE_CLASS` não existe no READY.
O ataque cai como argumento e **sobrevive como risco de engenharia**.

---

## 8 · «Disease risk model prova incidência.»

```
VEREDITO  CAI.
```

`MODEL OUTPUT != FACT`. O xarvio declara produzir *«um índice para identificar e
prever o risco de eventos de infecção»* — prever não é constatar. A régua desta
missão separa `NIVEL 3 · RISCO MODELADO` de `NIVEL 4 · INCIDÊNCIA CONFIRMADA`,
e o salto entre eles exige denominador e método de diagnóstico.

---

## 9 · «Registo autorizado prova portfólio comercial.»

```
VEREDITO  CAI — e esta casa ja o escreveu em SQL, ha migrations.
```

```sql
-- migration 005
current_commercial_availability text not null default 'NAO_SEI'
-- comment: «Deliberadamente sem default: disponibilidade comercial
--           NAO se deduz de registro.»  (ver Neptune ES-00211)
```

E o caso inverso também existe: um registo caducado pode continuar a ser vendido
no período de escoamento (`fecha_limite_venta` é uma coluna separada de
`fecha_caducidad`, e o comentário diz `EXPIRY != WITHDRAWAL`).

---

## 10 · «Portfólio registado prova oportunidade de venda.»

```
VEREDITO  CAI — e e o ataque cuja queda define o limite comercial do SINTONIA.
```

Entre «temos uso autorizado» e «venda aqui» faltam, pela descrição do único
sistema que declara fazê-lo (DTN Farm Intelligence):

```
ligacao CAMPO -> OPERADOR DA TERRA · area · mix de culturas · inputs usados ·
historico de compra · territorio · CRM/ERP · potencial de compra
```

Nada disso é público. Os níveis A·B·C·D da oportunidade existem exactamente para
que esta queda seja visível no objecto e não só na discussão.

---

## 11 · «Social / field voice prova incidência local.»

```
VEREDITO  CAI.
```

Sem método e sem denominador, uma voz é `NIVEL 1` — relato. A própria CABI, que
opera clínicas formais com formulário e plant doctors treinados, regista que
*«os dados da clínica são muitas vezes incompletos»*. E a `COL-LAW-034` já tem a
cicatriz da identidade: três funcionários de FMC, UPL e BASF foram contados como
o canal da empresa porque o headline nomeia o empregador.

**Núcleo verdadeiro que fica:** voz de campo é input legítimo e valioso — o
xarvio aceita observação do utilizador para **melhorar o modelo**. É input, não
conclusão.

---

## 12 · «Preço subiu, portanto existe oportunidade ADAMA.»

```
VEREDITO  CAI.
```

Falta tudo o que torna uma variação um achado: base histórica (materialidade),
decisão afectada, e o limite de atribuição. AMIS e as EU Market Observatories
existem para **transparência de mercado**, não para decisão de tratamento. E o
preço do trigo e a decisão sobre septoriose vivem em cadeias causais diferentes.

```
DASHBOARD MACRO NAO VIRA INTELLIGENCE POR ESTAR NUM CARD.
```

---

## 13 · «Data futura significa Future Intelligence.»

```
VEREDITO  CAI — e revela um defeito no card `future`.
```

Uma data de caducidade é um **facto presente sobre o futuro**, vindo do
regulador, com autoridade máxima. Um sinal de horizon scanning é uma
possibilidade com ~7 % de sobrevivência medida. Pô-los no mesmo sítio faz o
segundo herdar a credibilidade do primeiro.

```
FACTO PRESENTE SOBRE O FUTURO != SINAL FRACO.
E O CARD `future` MISTURA-OS HOJE.
```

---

## 14 · «Score universal pode resumir tudo.»

```
VEREDITO  CAI PARCIALMENTE — e a parte que fica e a util.
```

**Cai** como número de decisão: `INT-LAW-093` (score não substitui
decomposição), `INT-LAW-094` (score alto não derrota gate duro).

**Fica** como bilhete de entrada: o PeMoScoring da EFSA é exactamente um score
— phi de −1 a +1 — e funciona porque (a) tem 15 critérios visíveis por trás,
(b) serve para **descartar**, não para concluir, e (c) é seguido de avaliação
formal para o que passa.

```
UM SCORE QUE DESCARTA E BARATO E HONESTO.
UM SCORE QUE CONCLUI E UM JULGAMENTO DISFARCADO DE NUMERO.
```

---

## 15 · «Mais fontes = mais confiança.»

```
VEREDITO  CAI — com numero externo.
```

392 pragas novas identificadas pela EFSA entre 2017 e 2024; **27** voltaram a
ser mencionadas. O volume de fontes não moveu a confiança: a **independência** e
a **persistência** moveram.

E a `COL-LAW-034` mede o mesmo pela negativa: 67 vozes técnicas verificadas, das
quais 16 falam de olivar. *«Quantidade não é representatividade.»*

---

## 16 · «READY com texto é suficiente porque o LLM pode reler.»

```
VEREDITO  CAI — com a medicao mais dura desta missao.
```

```
39 campos na entrada -> 12 no READY -> 30 perdidos
0 de 23 campos agronomicos com chave propria no READY
6 aparecem apenas DENTRO da frase, por acaso
```

Reler o texto não recupera:

- o que a fonte estruturou e a travessia deitou fora (`num_registrazione`,
  lat/lon, `crop_eppo`);
- o que nunca esteve no texto (método, denominador, população-alvo);
- a **espécie da evidência**, que vive no contrato da fonte e não no documento.

```
RELER O TEXTO NAO E LER UM CAMPO: E ADIVINHAR OUTRA VEZ O QUE A FONTE
JA TINHA DITO — COM UM SEGUNDO CEREBRO, SEM AUDITORIA E SEM VERSAO.
```

---

## 17 · «Se a Intelligence precisar, ela pode buscar directamente na Collection.»

```
VEREDITO  CAI — e ja existe em codigo, medido e classificado como defeito.
```

```
motor/normalize_agro.py:29   from eppo_gd import names as eppo_names
coleta/eppo_gd.py:28         https://gd.eppo.int/taxon/{code}   <- HTTP ao vivo
```

O censo da Intelligence classificou-o `SEVERITY = ARCHITECTURAL`:
`INTELLIGENCE → COLETOR DIRECTO`, sem passar por
`COLLECTION → SALA DE ESPERA → INTELLIGENCE`. E mediu que ninguém o percorre:

```
DIRECT_COLLECTION_PATHS   = 1  (existe em codigo)
EXERCIDOS POR ALGUMA ROTA = 0  (CAN DO != DID DO)
```

O ataque não é hipotético. É a descrição de um caminho que já lá está, e que a
casa já decidiu não andar.

---

## 18 · «Um modelo de fazenda pode ser transferido para intelligence regional.»

```
VEREDITO  CAI.
```

xarvio e Cropwise operam sobre **limite de talhão**, com variedade, data de
sementeira e meteorologia local. O JRC MARS opera sobre **grelha meteorológica
agregada a NUTS**, com juízo de analista. São dois objectos, duas escalas e duas
incertezas.

```
MODELO REGIONAL NAO DESCE A TALHAO.
OBSERVACAO DE TALHAO NAO SOBE A REGIAO SEM DENOMINADOR.
```

---

## 19 · «Output de modelo é facto.»

```
VEREDITO  CAI. (é o 8 generalizado, e vale para todos os domínios)
```

`INT-LAW-131`: `FORECAST != FACT`. E a literatura de 2026 acrescenta o que torna
a confusão cara: *«uma infecção precoce falhada, um alerta falso, um alerta
tardio e um valor de confiança mal calibrado têm consequências agronómicas
diferentes»* — e todos os quatro desaparecem quando a saída do modelo é tratada
como facto.

---

## 20 · «Human review transforma evidência fraca em facto.»

```
VEREDITO  CAI.
```

`INT-LAW-172` já o diz. O benchmark confirma **com o uso real do perito**: na
EFSA, o perito escolhe *«o resultado intermédio mais plausível, para evitar
pressupostos extremos»* — ou seja, é chamado para **não** exagerar. Na ISPM 8,
a autoridade pode declarar um registo **inválido**: o juízo humano retira
evidência, não a fabrica.

```
UM PERITO A CARIMBAR UM NIVEL 1 NAO PRODUZ UM NIVEL 4.
E UM PERITO A CARIMBAR UM ZERO SEM DENOMINADOR NAO PRODUZ AUSENCIA.
```

---

## PLACAR

```
CAEM POR COMPLETO ....... 18   2 3 4 5 6 7 8 9 10 11 12 13 15 16 17 18 19 20
CAEM PARCIALMENTE ....... 2    1 (knowledge graph) · 14 (score)
SOBREVIVEM COMO ARGUMENTO  0
```

---

## OS TRÊS QUE SOBREVIVEM COMO DEFEITO

Nenhum ataque sobreviveu como argumento. **Três sobreviveram como estado do
repositório**, que é pior:

```
#4   «publicacao recente = facto recente»
     -> `_tem_quando` aceita `published_at` como tempo do facto.
        E o campo generico `data` vira FACT_TIME no contrato de saida.

#7   «clima favoravel prova doenca»
     -> a lei existe no contrato da fonte e NAO ATRAVESSA a fronteira.
        Do lado da Intelligence, um boletim agroclimatico e um texto como
        outro qualquer.

#16  «READY com texto e suficiente»
     -> e o estado actual, medido: 0 de 23 campos agronomicos com chave propria.
```

```
UM ATAQUE QUE CAI NO ARGUMENTO E SOBREVIVE NO CODIGO
NAO FOI DERRUBADO. FOI ADIADO.
```

Os três estão no P0:
[`../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`](../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md).
