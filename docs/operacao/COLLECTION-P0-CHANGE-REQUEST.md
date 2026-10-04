# COLLECTION P0 CHANGE REQUEST — a espécie e a estrutura do facto agrícola morrem na última porta

```
ABERTO_POR    C-INT-AGRO-BENCH-01   (research, nao-invasiva)
PARA          O DONO DA COLLECTION
MEDIDO_EM     2026-09-13
BASE          claude/raw-observation-identity-3jbwco @ f888776d
INSTRUMENTO   provas/auditoria_agro_fronteira.py    (reproduzivel, nao escreve nada)
ESTADO        P0_COLLECTION_CHANGE_REQUIRED = YES
```

> **ESTA MISSÃO NÃO CONSERTOU NADA.** Zero runtime, zero migration, zero
> alteração de `admissao/`, zero Bíblia, zero System Map, zero Portal.
> `ONE CONCEPT → ONE OWNER`: quem conserta a Collection é o dono da Collection.
> Isto é a medição, entregue inteira.

---

## A DEFINIÇÃO QUE ISTO TEM DE SATISFAZER

> *«Um P0 existe quando a Collection actual DESTRÓI ou deixa de preservar
> informação fornecida pela fonte que será indispensável à Intelligence e que
> não pode ser reconstruída defensavelmente depois.»*

As três condições, verificadas uma a uma, mais abaixo.

---

## 1 · WHAT IS LOST

### 1.1 · A ESPÉCIE DA EVIDÊNCIA — e é o mais grave

Esta casa **declara a espécie da evidência antes de qualquer execução**, no
contrato de fonte, em 13 fontes italianas, com leis escritas ao lado:

```
IT-T2-001  AGROCLIMATIC_SIGNAL          LEI: "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE"
IT-T2-002  AGROCLIMATIC_SIGNAL          LEI: idem
IT-T2-004  AGROCLIMATIC_SIGNAL
IT-T3-002  TECHNICAL_GUIDELINE + OBSERVED_FIELD_SIGNAL pontual
IT-T3-005  OBSERVED_FIELD_SIGNAL + COOPERATIVE_GUIDANCE
IT-T3-008  OBSERVED_FIELD_SIGNAL + TECHNICAL_GUIDELINE (separar por bloco)
IT-T3-010  OBSERVED_FIELD_SIGNAL + COOPERATIVE_GUIDANCE
IT-T3-011  OFFICIAL_ORGANIZATION_REGISTRY  LEI: "REGISTRY != FIELD_SIGNAL"
IT-T4-001  REGULATORY_AUTHORIZATION
IT-T1-001  SERIE_OFICIAL_DE_PRODUCAO
IT-T5-002  TECHNICAL_GUIDELINE          LEI: "TECHNICAL_GUIDELINE != CURRENT_FIELD_SIGNAL"
IT-T7-002  OFFICIAL_ORGANIZATION_REGISTRY
IT-T9-008  COMPANY_CLAIM                LEI: "COMPANY_CLAIM != REGULATORY_FACT"
```

**Nenhuma destas classes, e nenhuma destas leis, atravessa a fronteira.**

Medido (`ataque F`):

```
contrato comum `ingresso.PARA_A_PORTA` ......... 10 nomes, nenhum e EVIDENCE_CLASS
contrato de saida `pronto_para_inteligencia` ... 12 campos, nenhum e EVIDENCE_CLASS
```

Do lado da Intelligence, um boletim agroclimático da ARPAE e um relato de campo
da ARIF são **o mesmo objecto**: `TEXTO`.

```
A CASA ESCREVEU «AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE», POS UM TESTE A
GUARDA-LA, E DEPOIS ENTREGOU OS DOIS A INTELLIGENCE COMO A MESMA COISA.
```

### 1.2 · A ESTRUTURA DO FACTO

Um facto agronómico descartável, com 39 campos, passado pelo caminho real:

```
campos na entrada .......... 39
campos no READY ............ 12
PERDIDOS ................... 30
```

```
active_substance · active_substance_cas · bbch · claim_id · confidence_level ·
crop · crop_eppo · denominator · design_prevalence · diagnostic_method · doi ·
method · method_sensitivity · nuts · object · parent_artifact_id ·
phenological_stage · predicate · problem · problem_eppo · product ·
published_at · registration_id · sample_size · scale · subject ·
target_population · unit · url · value
```

E o detalhe que torna isto um defeito e não uma escolha: **o código já reconhece
a espécie `FATO`.**

```python
# admissao/admissao.py
MARCAS_DE_FATO = ("claim_id", "subject", "predicate", "fact_id")
def estagio(item): ...   # devolve FATO, DOCUMENTO ou ESTAGIO_DESCONHECIDO
```

A porta pergunta a um facto as perguntas de facto — e depois entrega-o como se
fosse um documento. `claim_id`, `subject`, `predicate` e `object` entram, são
lidos, decidem a régua aplicada, **e não saem**.

```
O SISTEMA SABE O QUE E UM CLAIM. O CONTRATO DE SAIDA NAO TEM ONDE O POR.
```

### 1.3 · O CONTEXTO AGRONÓMICO ESTRUTURADO

```
23 campos agronomicos testados
 0 com chave propria no READY
 6 aparecem apenas DENTRO da frase, por acaso de o texto os conter
```

E isto apesar de a casa **ter** as tabelas:

```
public.crop   (codigo, nome_es, mapa_id_cultivo, eppo_code)
public.issue  (codigo, nome_es, classe DISEASE|PEST|WEED|..., eppo_code)
public.crop_issue
public.registro_regulatorio (pais, registration_id, ..., fonte_versao na chave)
public.registro_uso (registro_id, crop_id, issue_id, substancia)
```

### 1.4 · O TEMPO DO FACTO — três defeitos, e são três

```
B1  `_tem_quando` responde «TEM TEMPO DO FATO» a um item cujo unico tempo e
    `published_at`.
    Medido:  _tem_quando({"published_at": "2026-06-30"})
             -> ('SIM', 'tem tempo do fato', {'quando': '2026-06-30'})
    COL-LAW-031: «FACT_TIME = PUBLISHED_AT E PROIBIDO. Nao por conveniencia,
                  nao por omissao, NAO POR FALLBACK.»
    Ja registado como violacao viva (gap G-01 / defeito C-001). Continua viva,
    e agora tambem no estagio FATO — o estagio a que a pergunta SE APLICA.

B2  A evidencia dessa resposta NAO chega ao livro de decisoes.
    `decidir()` devolve so a evidencia da ULTIMA pergunta.
    Medido:  evidencia no livro = {"palavras": [...], "estagio": "FATO"}
             a chave "quando" nao la esta.
    COL-LAW-042 exige `evidence`. Esta la — e nao e a que prova a passagem.

B3  O campo generico `data` vira `FACT_TIME` no contrato de saida.
    `pronto_para_inteligencia`: item.get("fact_time") or item.get("data")
    Medido:  com `data` = "2026-06-30"  ->  READY.FACT_TIME = "2026-06-30"
    `data` nao declara de que tempo e. Um coletor que la ponha a data do
    documento produz um FACT_TIME falso, carimbado como facto.
```

### 1.5 · `ITEM_ID = "?"`

```
item com `source_id`, sem `id` e sem `url`  ->  READY.ITEM_ID = '?'
```

`COL-LAW-034`: *«`"?"` e a string vazia **NÃO DEVEM** ser usados como
identidade.»*

### 1.6 · A ROTA REAL NÃO PREENCHE NEM OS 12

```
coleta/rota_forward_documento.py::item_para_a_porta poe 9 nomes no item:
  SOURCE_ID · ARTIFACT_TYPE · PARENT_SHA256 · PARENT_ARTIFACT_ID ·
  id · texto · url · captured_at · raw_asset_id

FACT_TIME      -> nao esta.  Sai «NAO SEI» por construcao.
FACT_LOCATION  -> nao esta.  Sai «NAO SEI» por construcao.
SOURCE_LOCATION-> nao esta.  Sai «NAO SEI» por construcao.
```

Três dos doze campos do contrato canónico saem vazios **não porque a fonte não
saiba**, mas porque o item não os carrega.

---

## 2 · WHERE IT IS LOST

Dois sítios, e são dois donos diferentes do mesmo problema:

```
[1]  admissao/admissao.py :: pronto_para_inteligencia   (linhas ~598-612)
     O funil. 12 chaves fixas. Tudo o resto e deitado fora AQUI.
     E deitado fora DEPOIS de ter sido lido e de ter decidido a regua.

[2]  coleta/rota_forward_documento.py :: item_para_a_porta   (linhas ~202-214)
     O item nasce com 9 nomes. FACT_TIME, FACT_LOCATION e SOURCE_LOCATION
     nunca la chegam, mesmo quando a unidade os tem.
```

E um terceiro, menor, mas que torna o primeiro invisível:

```
[3]  admissao/admissao.py :: decidir   (linhas ~434-454)
     So a evidencia da ULTIMA pergunta e guardada. A prova de que o portao
     temporal passou por uma data de publicacao nao existe em lado nenhum.
```

⚠️ **Nota de justiça para `ingresso.py`.** O tradutor do contrato comum **não** é
o culpado: `para_a_porta` documenta que *«o que nao esta no mapa viaja
intacto»*, e cumpre-o. Campos agronómicos **passam** por ele até `decidir`. Eles
morrem no funil de saída, não na tradução.

---

## 3 · WHY INTELLIGENCE NEEDS IT

Detalhe em
[`research/intelligence/AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md`](../../research/intelligence/AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md).
Em uma tabela:

| sem isto | a Intelligence não pode |
|---|---|
| espécie da evidência | distinguir clima favorável de ocorrência · registo de alegação · guideline de sinal actual — os quatro erros mais caros do agro |
| cultura/problema (EPPO) | cruzar nada com nada; toda a junção vira semelhança textual, que a `COL-LAW-034` proíbe |
| método · unidade · escala | comparar dois valores; somar; dizer «aumentou» |
| denominador | afirmar prevalência ou ausência (EFSA · ISPM 8) |
| `claim_id` / sujeito-predicado | ligar suporte e contradição a alguma coisa (`INT-LAW-032`, `INT-LAW-033`) |
| DOI / identidade de ensaio | medir independência; sem ela, três papers de um ensaio contam três |
| `registration_id` | ligar achado a rótulo, e rótulo a portfólio |
| `FACT_TIME` verdadeiro | dizer se a janela ainda está aberta (`INT-LAW-104`) |

E a prova mais dura de que isto é necessário vem **do próprio schema desta
casa**:

```sql
-- migration 005, camada analitica
create table public.observacao (
  crop_issue_id ..., geografia_id ..., camada ..., periodo_inicio/fim ...,
  valor numeric, unidade text,
  base_denominador numeric NOT NULL,
  base_descricao   text    NOT NULL,
  rule_version     text    NOT NULL
);
comment: 'Obrigatório. O Brasil já travava isso em termos_medicoes...'
```

```
A TABELA DE DESTINO EXIGE DENOMINADOR, UNIDADE, CAMADA E PAR CULTURA-PROBLEMA.
O CONTRATO DE ENTREGA DA COLLECTION NAO CARREGA NENHUM DOS QUATRO.
E ELA NAO TEM WRITER DE RUNTIME — SO UMA FIXTURE.

Uma coluna NOT NULL sem fonte a montante tem dois destinos:
nunca ser preenchida, ou ser preenchida com um numero inventado.
```

---

## 4 · EXTERNAL BENCHMARK EVIDENCE

| exigência | autoridade externa |
|---|---|
| medição = **trait × method × scale** | **Crop Ontology**: *«uma variável fenotípica é a combinação de um trait, um método e uma escala»* · **MIAPPE 1.1**: a variável observada descreve *«como a medição foi feita»*, com método e unidade |
| ausência exige denominador | **EFSA**, guidelines de inquéritos: **design prevalence** + **população-alvo** + **sensibilidade do método** (eficácia de amostragem × sensibilidade de diagnóstico) + nível de confiança |
| ausência tem cinco espécies | **ISPM 8 (IPPC)**: *pest not recorded · pest free area · pest records invalid · pest no longer present · pest eradicated* |
| identidade do organismo é estável, o nome não | **EPPO**: *«quando… um nome científico muda, o código EPPO permanece o mesmo»* |
| a base de dados não é a autoridade | **EU Pesticides Database**: *«It has no legal value»*; o oficial é o Jornal Oficial |
| o uso de PPP tem seis eixos | **EPPO PP 1/248 (3)**: *«um uso deve ser descrito por uma combinação de elementos e dos seus códigos EPPO»* |
| o que se observa ≠ como se observa | **Cropwise Protector** separa fenómeno (praga, doença, pressão) de característica (contagem por planta, % de infestação, nível de pressão) |
| sinal ≠ achado | **EFSA Horizon Scanning**: 392 pragas identificadas 2017-2024, **27** voltaram a aparecer |

---

## 5 · INTERNAL EXECUTABLE PROOF

```bash
python3 provas/auditoria_agro_fronteira.py          # relatorio
python3 provas/auditoria_agro_fronteira.py --json   # o mesmo, em JSON
```

Seis ataques, todos contra `admissao/admissao.py` real, com casos descartáveis,
sem escrever na Sala de Espera e sem tocar no livro de decisões.

```
A  39 -> 12, 30 perdidos, estagio reconhecido como FATO
B  `published_at` abre o portao; a evidencia nao chega ao livro;
   `data` vira FACT_TIME
C  0 de 23 campos agronomicos com chave propria
D  RAW_OBSERVATION_ID ✅ preservado · claim_id, doi, registration_id,
   crop_eppo, problem_eppo perdidos · ITEM_ID pode sair '?'
E  o mesmo facto, mesmo EPPO, duas redaccoes -> SIM vs NAO_SEI
F  contrato comum: 10 nomes, 0 agronomicos · rota forward: 9 nomes,
   sem FACT_TIME nem FACT_LOCATION
```

E a prova de que a matéria-prima **existe** e é desperdiçada:

```
data/samples/X-007-canonical-agro-dictionary.json
  105 pares ORIGINAL -> EPPO verificados contra a EPPO Global Database,
  com MATCH_TYPE e EVIDENCE.
  Nenhum deles tem por onde chegar a Intelligence.
```

---

## 6 · AS TRÊS CONDIÇÕES DO P0, VERIFICADAS

```
[1] A FONTE FORNECE?
    SIM. A especie da evidencia e declarada no contrato de fonte, por fonte,
    antes da execucao. O par cultura-problema existe em `crop`/`issue` com
    `eppo_code`. O registo tem `registration_id` e `fonte_versao`. O DOI vem
    quando a fonte o da.

[2] A INTELLIGENCE PRECISA?
    SIM, e de forma indispensavel — sem a especie da evidencia, os quatro erros
    agricolas mais caros tornam-se indistinguiveis.

[3] NAO E RECONSTRUIVEL DEFENSAVELMENTE DEPOIS?
    SIM, NAO E.
    A especie da evidencia NAO ESTA NO DOCUMENTO: esta no contrato da fonte.
    Nenhuma releitura do texto a recupera. Um LLM que a adivinhe esta a
    fabrica-la — e seria uma opiniao semantica a substituir uma declaracao
    de autoridade escrita antes da coleta.

    => P0_COLLECTION_CHANGE_REQUIRED = YES
```

---

## 7 · MINIMAL CONTRACT CHANGE

⚠️ **Isto é o mínimo que a medição sustenta, e não é um desenho.** O
`§30` do enunciado proíbe inflar o READY sem prova, e este pedido **não**
propõe os 30 campos.

### O que a medição sustenta como necessário

```
A  UM CAMPO, E E O QUE FALTA A TODAS AS ESPECIES:
   EVIDENCE_CLASS  — ja existe no contrato de fonte, ja e obrigatorio la,
                     ja tem teste a guarda-lo. So precisa de viajar.

B  UM ENDERECO, E NAO 30 CAMPOS:
   O READY precisa de conseguir APONTAR para uma unidade estruturada
   com identidade propria — exactamente como ja aponta para o RAW por
   `RAW_OBSERVATION_ID`.
   A `COL-LAW-202` ja desenha o modelo (`ARTIFACT ──evidence_for──► CLAIM`)
   e ja o marca `IT: ABSENT`.
   A `COL-LAW-043` ja tem o precedente e a lei da forma:
       «A MENOR IDENTIDADE QUE FECHA A ESTRADA E A CERTA.»

C  TRES CONSERTOS QUE NAO ACRESCENTAM CAMPO NENHUM:
   C1  `_tem_quando` deixa de aceitar `published_at` como tempo do FACTO.
       Nao e campo novo: e cumprir a COL-LAW-031 e fechar o gap G-01.
   C2  `pronto_para_inteligencia` deixa de promover o campo generico `data`
       a FACT_TIME.
   C3  `ITEM_ID` nunca sai `"?"` — COL-LAW-034.

D  UM CONSERTO DE ROTA, SEM MEXER NO CONTRATO:
   `item_para_a_porta` passa a por FACT_TIME, FACT_LOCATION e SOURCE_LOCATION
   no item quando a unidade os tem. Os campos JA EXISTEM no contrato de saida.
```

### O que este pedido explicitamente **NÃO** propõe

```
NAO  acrescentar 30 campos ao READY
NAO  acrescentar metodo, unidade, escala ou denominador — as fontes actuais
     NAO OS FORNECEM, e SOURCE_DOES_NOT_PROVIDE != COLLECTION_BUG
NAO  escolher como persistir a unidade estruturada
NAO  criar a extracao de claim (COL-LAW-202 e TARGET, e continua a se-lo)
NAO  mexer no lexico dos universos (e outro dono e outra missao)
```

---

## 8 · NON-GOALS

```
NAO e um pedido de funcionalidade de Intelligence.
NAO e um pedido para a Collection interpretar o que colhe.
NAO e um pedido para recolher outra vez — tudo isto ja foi colhido.
NAO e um redesenho da Sala de Espera, nem da sua morada.
NAO altera a COL-LAW-043 sem que o dono da Collection o decida:
    este documento MEDE o custo de ela ficar como esta.
```

---

## 9 · REGRESSION TEST

O instrumento desta missão **já é** o teste, e falha hoje:

```bash
python3 provas/auditoria_agro_fronteira.py
```

Os asserts que um conserto teria de fazer passar:

```
ATAQUE B  _tem_quando({"published_at": X}) != SIM
ATAQUE B  READY.FACT_TIME nunca nasce de `data` nem de `published_at`
ATAQUE B  a evidencia da pergunta do tempo esta no livro de decisoes
ATAQUE D  item sem `id` e sem `url` -> ITEM_ID != "?"
ATAQUE F  item_para_a_porta poe FACT_TIME/FACT_LOCATION quando a unidade os tem
ATAQUE A  EVIDENCE_CLASS declarada pela fonte aparece no READY
ATAQUE A  um item de estagio FATO conserva o endereco do seu claim
```

E um teste negativo, para o conserto não virar inflação:

```
O READY NAO GANHA CAMPO PARA O QUE A FONTE NAO DA.
metodo · unidade · escala · denominador · design prevalence · BBCH
continuam FORA, e continuam SOURCE_DOES_NOT_PROVIDE ate uma fonte os dar.
```

---

## 10 · PASS GATE

```
PASS quando, e so quando:

[1] `python3 provas/auditoria_agro_fronteira.py` corre e os sete asserts da §9
    passam;
[2] a especie da evidencia declarada pelo contrato de fonte chega a Sala de
    Espera, com o mesmo valor com que foi declarada;
[3] um item de estagio FATO consegue ser ligado, deterministicamente e sem
    heuristica, a unidade estruturada que o originou — como ja acontece com o
    RAW por `RAW_OBSERVATION_ID`;
[4] nenhuma data de publicacao, e nenhum campo generico, satisfaz a pergunta
    do tempo do facto — nem no portao, nem no contrato de saida;
[5] a cadeia canonica do System Map corre e devolve SYSTEM_MAP_CHECK=PASS;
[6] a COL-LAW-043 e a COL-LAW-031 ficam a dizer o mesmo que o codigo diz —
    hoje divergem, e enquanto divergirem o «isto e mais nada» vence na
    pratica e a lei fica a ser um comentario.
```

```
LEI QUE NINGUEM MEDE E COMENTARIO.
ESTA FICOU MEDIDA. FALTA DECIDIR O QUE SE FAZ COM A MEDICAO —
E ESSA DECISAO E DO DONO DA COLLECTION.
```
