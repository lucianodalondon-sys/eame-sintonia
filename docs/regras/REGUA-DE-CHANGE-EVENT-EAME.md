# RÉGUA DE CHANGE EVENT — o que é uma mudança, e o que ela prova

**Data:** 2026-08-29 · **Nasce de:** `ES-01717 · MAXENTIS → SORATEL MAX`

> Duas versões da mesma fonte diferem. **Isso não é um sinal de mercado.**
> É uma diferença entre dois documentos, até que se diga qual campo mudou e o quê,
> exatamente, isso prova.

---

## 1 · A CAPACIDADE, DITA COM PRECISÃO

**`CHANGE DETECTION THROUGH VERSIONED PUBLIC DATA`**

Comparar duas versões arquivadas do **mesmo** documento público e emitir um evento por
campo que difere.

| o que ela é | o que ela **não** é |
|---|---|
| detecção **retrospectiva**: vê a mudança porque as duas pontas foram guardadas | previsão. O DATA CLOCK **não previu** nada |
| alcance = o intervalo entre as versões que temos | vigilância contínua. Entre `28/05/2025` e `26/08/2026` há **15 meses** e **uma** observação |
| datação da **observação** | datação do **fato**. Sabemos quando *vimos*, não quando *ocorreu* |

**Por que a fonte não substitui o arquivo — medido:** o ROPF publica apenas o **último**
trâmite de cada produto, não o histórico. Das cinco renomeações confirmadas entre as duas
versões, **só o ES-01717 ainda exibe `MODIFICACION NOMBRE`**; nos outros quatro o campo já
foi sobrescrito por um trâmite posterior:

| registro | mudança confirmada | trâmite que o registro exibe **hoje** |
|---|---|---|
| **ES-01717** | MAXENTIS → SORATEL MAX | `MODIFICACION NOMBRE` (28/07/2026) — ainda visível |
| ES-00792 | ATILA → TANKE 360 | `PERIODO DE GRACIA POR ETIQUETA ANTIGUA` (19/11/2025) |
| 21506 | CODIMUR → CODIMUR-F | `NOTIFICACION DE UN CAMBIO NO SIGNIFICATIVO` (23/06/2026) |
| 24998 | FENOVA S → FENOVA SUPER | `PRÓRROGA DE AUTORIZACIÓN` (20/08/2025) |
| 25498 | LBG → LBG-01F34 | `NOTA SIMPLE PREPARADO` (10/04/2026) |

> **Quatro das cinco mudanças já seriam invisíveis hoje.** O arquivo não é redundância da
> fonte: em quatro casos de cinco, é a **única** rota.

---

## 2 · TIPOS DE CHANGE EVENT

Toda diferença recebe **um** tipo. Nenhuma diferença é publicada sem tipo.

| CHANGE_TYPE | o que mudou | detectável hoje? | prova disponível |
|---|---|---|---|
| `REFERENCE_NAME_CHANGE` | nome do produto de referência, mesmo registro | **SIM — provado** | 5 confirmados entre `28/05/2025` e `26/08/2026` |
| `NEW_COMMON_DENOMINATION` | uma marca nova sobre uma autorização existente | **SIM — provado** | 156 eventos |
| `REMOVED_COMMON_DENOMINATION` | uma marca deixou de constar | **SIM — provado** | 30 eventos |
| `NEW_REGISTRATION` | registro que não existia na versão anterior | **SIM — provado** | 83 registros só na versão B |
| `REGISTRATION_LEFT_THE_LIST` | registro que saiu da lista | **SIM — provado** | 38 registros só na versão A |
| `STATUS_CHANGE` | Vigente ↔ Cancelado | **POSSÍVEL, não provado** | o export do ROPF traz `Estado`; falta uma **segunda** versão arquivada do export |
| `HOLDER_CHANGE` | mudou o titular | **POSSÍVEL, não provado** | idem — `Titular` está no export; falta a segunda versão |
| `COMPOSITION_CHANGE` | mudou o formulado | **POSSÍVEL, não provado** | idem — `Formulado` está no export |
| `DATE_CHANGE` | caducidade, renovação, limite de venda | **POSSÍVEL, não provado** | idem — as datas estão no export |
| `MANUFACTURER_CHANGE` | mudou o fabricante ou a planta | **POSSÍVEL, não provado** | `fabricante`/`fabrica` só vêm da ficha individual, um pedido por registro |
| `UNKNOWN_CHANGE` | diferença que nenhum tipo acima explica | — | obrigatório quando o parser não decide |

**A distinção que importa:** `provado` = já emitimos o evento a partir de duas versões que
temos. `possível` = o campo existe e é comparável, e **só falta o tempo passar** com o
arquivamento ligado. Nenhuma linha "possível" pode ser apresentada como capacidade
existente.

---

## 3 · CAMPOS OBRIGATÓRIOS DE UM CHANGE EVENT

Um evento sem estes campos não é publicável:

```
ENTITY              qual das sete entidades do MODELO DE IDENTIDADE mudou
REGISTRATION_ID     a chave que sobrevive à mudança
CHANGE_TYPE         um da tabela acima
BEFORE              valor na versão A (ou null, se é criação)
AFTER               valor na versão B (ou null, se é remoção)
SOURCE_VERSION_A    arquivo + data da versão + SHA-256
SOURCE_VERSION_B    arquivo + data da versão + SHA-256
OBSERVED_DATE       quando NÓS comparamos — não quando o fato ocorreu
VERDICT             CONFIRMED · REFUTED · UNRESOLVED
```

### A verificação é obrigatória, e reprova eventos

O detector de renomeação propôs **10** candidatos. A regra de verificação — *`AFTER` tem de
ser igual ao nome atual no ROPF (fonte independente do PDF) **e** `BEFORE` não pode ser
apenas `AFTER` com sobra de prefixo* — reprovou metade:

| veredito | n | exemplo |
|---|---|---|
| `CONFIRMED` | **5** | `ES-01717` MAXENTIS → SORATEL MAX |
| `REFUTED_PARSER_OVERCAPTURE` | 2 | `23738` "DIPEL® DFNU" → "DIPEL® DF" — o "NU" veio do nome da concessionária |
| `UNRESOLVED` | 3 | `ES-00304` "FOSIKA" → "FOSIKAS" — o "S" veio da linha seguinte |

> **Metade dos eventos brutos era artefato do próprio leitor.** Um radar que publicasse
> diferenças sem verificação estaria certo em 50% dos alarmes.

---

## 4 · O QUE UMA MUDANÇA DE REGISTRO PROVA — E O QUE NÃO PROVA

`SORATEL MAX` substituir `MAXENTIS` no produto de referência do ES-01717 prova
**exatamente uma coisa**:

> **`OFFICIAL RECORD NAME CHANGED`** — o nome do produto de referência no registro oficial
> espanhol mudou entre 28/05/2025 e 26/08/2026, e o número de registro não mudou.

**Sozinho, não prova nenhuma destas:**

| leitura proibida | por quê |
|---|---|
| relançamento comercial | o registro não diz o que foi ao mercado, nem quando |
| estratégia de marca | intenção não está em campo de registro |
| reposicionamento de mercado | não há variável de mercado no documento |
| mudança de vendas | o registro não tem volume nem preço |
| alinhamento de portfólio entre países | é **hipótese** — o nome `SORATEL` também existe na Itália (018175) e na Espanha (ES-01665), com composições diferentes. Coincidência de nome não é decisão de portfólio |
| mudança de titular, composição ou status | **medido: nenhum dos três mudou** |

**FACT · INTERPRETATION · ACTION** (conforme `REGUA-DE-ALERTA-EAME.md`):

```
FACT            o nome do produto de referência do ES-01717 mudou de MAXENTIS para
                SORATEL MAX entre duas versões do documento oficial; titular,
                fabricante, composição e status permanecem os mesmos.
INTERPRETATION  um radar que acompanhe MARCA teria emitido dois eventos falsos
                ("MAXENTIS saiu", "SORATEL MAX entrou"). Nenhum ocorreu.
ACTION          indexar por REGISTRATION_ID; tratar nome como atributo versionado.
NÃO É AÇÃO      nada sobre concorrência, canal, preço ou lançamento.
```

---

## 5 · REGRA DE ALARME PARA CHANGE EVENTS

Herda os portões de `REGUA-DE-ALERTA-EAME.md` e acrescenta dois:

1. **Portão do tipo.** `UNKNOWN_CHANGE` **nunca** alerta. Vai para revisão.
2. **Portão do leitor.** Um evento cujo `BEFORE` ou `AFTER` foi produzido por parser sem
   âncora externa **nunca** alerta — foi assim que dois dos dez candidatos se revelaram
   artefato.

E mantém a proibição central: **um change event descreve o registro, não o mercado.** A
palavra `mercado` não pode aparecer no texto de um alerta cuja única evidência é uma
diferença entre duas versões de um documento regulatório.

---

**EVIDÊNCIA:** `data/samples/CHANGE-EVENTS-es-2025-2026.json`
(SHA-256 das duas versões, os 10 candidatos, os vereditos e a regra de verificação)
