# HIERARQUIA UNIVERSAL DA INFORMAÇÃO — contrato congelado

**Data:** 2026-09-06 · **Escopo:** `COUNTRY_SCOPE = ITALY` · **Projeto:** `SINTONIA_EAME_ITALY`
**Estado:** contrato de camadas. Não é schema, não é código, não é pipeline.

> Este documento congela **a hierarquia**, e só ela. Ele não inventa camada nova: a
> hierarquia foi recebida da missão e é transcrita aqui como contrato explícito, para que
> o schema (`PASSPORT-SCHEMA-UNIVERSAL.md`) tenha onde se apoiar.

---

## 1 · A HIERARQUIA

```
SOURCE / ITEM
   ↓
CONTENT
   ↓
CLAIM / FACT
   ↓
CONTEXT
   ↓
ENTITIES
   ↓
LINEAGE / INDEPENDENCE
   ↓
RELATIONSHIPS
   ↓
CROSSINGS
   ↓
INTELLIGENCE OBJECT
   ↓
CAPABILITY ROUTING
   ↓
CONSUMPTION
```

**A seta não é tempo. É dependência.** Uma camada não pode ser afirmada com mais força do
que a camada de que ela depende. É essa regra, e só ela, que impede um cruzamento de ser
mais confiante do que a leitura que o alimentou.

---

## 2 · O QUE CADA CAMADA RESPONDE

| camada | a pergunta que ela responde | o que ela **não** responde |
|---|---|---|
| `SOURCE / ITEM` | que unidade de informação é esta, e de onde ela veio? | se alguém a leu |
| `CONTENT` | o conteúdo existe, está preservado, e até onde foi lido? | o que ele diz |
| `CLAIM / FACT` | que afirmação foi extraída, e com que força de prova? | se ela é relevante |
| `CONTEXT` | sobre qual cultura, problema, lugar e tempo é a afirmação? | quem a fez |
| `ENTITIES` | que pessoas e organizações estão envolvidas, e com que identidade provada? | onde elas estão |
| `LINEAGE / INDEPENDENCE` | esta evidência é independente daquela, ou as duas copiam a mesma origem? | se elas concordam |
| `RELATIONSHIPS` | que relação provada existe entre dois objetos? | o que isso significa |
| `CROSSINGS` | o que aparece quando duas ou mais evidências independentes se encontram? | se alguém precisa disso |
| `INTELLIGENCE OBJECT` | que objeto de inteligência nasceu disso? | para quem ele serve |
| `CAPABILITY ROUTING` | quais capacidades podem consumir este objeto, e com que relevância? | se consumiram |
| `CONSUMPTION` | alguma capacidade consumiu de fato? | se foi útil |

---

## 3 · AS TRÊS LEIS DA HIERARQUIA

### Lei 1 · Nenhuma camada empresta força para a de baixo

`CONTENT_STATE = LEXICALLY_SCANNED` não autoriza `CLAIM` com prova forte. Um classificador
tocou o texto; ninguém o leu. A camada `CLAIM` herda o teto da camada `CONTENT`.

### Lei 2 · Camada pulada é camada `UNKNOWN`, nunca camada satisfeita

Se `ENTITIES` nunca foi resolvida, ela não vale `NOT_APPLICABLE`. Vale `UNKNOWN`. Pular por
conveniência e pular por inaplicabilidade produzem o mesmo silêncio, e é essa semelhança
que destrói a confiança.

### Lei 3 · `CROSSINGS` exige `LINEAGE / INDEPENDENCE` resolvida

Duas páginas que copiam o mesmo boletim **não são duas evidências**. Enquanto
`INDEPENDENCE_STATE` for `UNKNOWN`, um cruzamento entre dois itens pode ser calculado, mas
**não pode ser contado como convergência**. Esta é a lei que a missão anterior não tinha
como escrever, porque o campo não existia.

---

## 4 · TRÊS EIXOS QUE NÃO SÃO A MESMA COISA

O repositório já tinha duas ordenações antes desta. Elas **não competem** com a hierarquia
— medem coisas diferentes, e confundi-las é o erro que este parágrafo existe para evitar.

| eixo | o que ordena | onde vive |
|---|---|---|
| **HIERARQUIA** (este documento) | do que o item é **feito** — camadas de composição | `docs/passaporte/PASSPORT-HIERARCHY.md` |
| **ESCADA DE ESTÁGIOS** | o que **aconteceu** com o item — máquina de estados | `CONTRATO-DO-PASSAPORTE.md §2` |
| **FLUXO DE PRODUTO** | como a informação vira **uso** na ADAMA | `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` |

```
ESCADA     CAPTURE → NORMALIZATION → DEDUP → CONTENT_ACQUISITION
           → INTELLIGENCE_READING → CLAIM_EXTRACTION → ROUTING → CONSUMPTION

FLUXO      SOURCE → EVIDENCE → NORMALIZATION → CAPABILITY → CROSSING
           → QUESTION → ADAMA USE → TOOL CONCEPT → INFORMATION REQUIREMENTS
```

Um item pode estar **alto na escada e baixo na hierarquia**: `CURRENT_STAGE = CONSUMPTION`
com `LINEAGE / INDEPENDENCE = UNKNOWN` é exatamente isso, e é um estado legítimo — desde
que o cruzamento que o consumiu saiba que não pode contar convergência.

---

## 5 · O QUE ESTA HIERARQUIA **NÃO** AUTORIZA

- Não autoriza recalcular cruzamento nenhum. `CROSSINGS` está na hierarquia como **lugar
  reservado**, não como trabalho feito.
- Não autoriza criar capacidade nova. `CAPABILITY ROUTING` roteia para as capacidades que o
  projeto já reconhece, ou para `UNKNOWN_CAPABILITY`.
- Não autoriza ativar portão. `PASSPORT_REQUIRED` continua `NO`.
- Não substitui a escada de estágios nem o fluxo de produto. Acrescenta um terceiro eixo.

---

## 6 · A CAMADA QUE FALTAVA

Das onze camadas, a que **não existia em nenhuma forma** antes deste contrato é
`LINEAGE / INDEPENDENCE` no sentido de **independência entre fontes**.

O `LINEAGE_STATE` de `PASSPORT-1.0` (`ROOT` · `RESOLVED` · `BROKEN` · `UNKNOWN`) é
**parentesco de derivação** — responde *"esta transcrição é filha daquele vídeo?"*. Os
motivos gravados no próprio log provam a semântica:

```
671   "vídeo é raiz"
372   "post é raiz"
252   "vídeo é raiz; transcrição e comentário derivam dele"
991   "recostura por VIDEO_ID"
```

Nenhum desses motivos fala de independência. Parentesco e independência são perguntas
diferentes, e a segunda não tem campo. É a lacuna registrada em
`PASSPORT-FIELD-CENSUS.md`.
