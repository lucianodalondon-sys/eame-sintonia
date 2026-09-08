# MAPA DE FECHAMENTO DA COLETA ITALIANA

**Censo READ-ONLY** · 2026-09-08 · ramo `claude/italia-biblia-integracao-v1`

> **Zero escritas em produção.** 0 DDL, 0 `INSERT`/`UPDATE`/`DELETE`, 0 upload, 0 chamada de
> API paga, 0 chamada Apify, 0 corrida nova. **Inteligência: intocada.**

---

## A PERGUNTA QUE PAROU O AVANÇO

Provámos **uma** estrada de ponta a ponta — a ARPAV. E aí a pergunta certa deixou de ser
«qual é a próxima fonte?» e passou a ser:

> ## PROVAR UMA FONTE NÃO PROVA UMA ESTRADA.
> ## MAS PROVAR UMA ESTRADA PODE POUPAR TRINTA CANÁRIOS.

Sem saber quantas cadeias operacionais diferentes existem, «a segunda fonte» tanto pode ser a
prova de uma estrada nova como a repetição da que já está provada.

---

## A · O QUE SE MEDIU

```
54  fontes italianas no registo mestre
 3  com veredito             (1 GREEN · 2 YELLOW)
51  com veredito NÃO SEI     ← a rota delas é desconhecida
 7  com prova de coleta no ledger
```

**A família da fonte sai do `access_method` declarado.** Onde ele não foi provado, fica
`NAO_SEI` — e é a esmagadora maioria. Um palpite ali faria o mapa parecer pronto.

| família | fontes |
|---|---:|
| `NAO_SEI` | **51** |
| `OFFICIAL_HTTP_DOCUMENT` | 1 |
| `STATIC_HTML` | 1 |
| `OUTRA` | 1 |

### Os executores, e a lacuna que eles denunciam

```
18  executores medidos em Python (saem para fora e trazem algo)
 4  coletores em JavaScript      (a estrada italiana recorrente)
 4  DECLARADOS em pedido/receitas.py
```

**18 medidos, 4 declarados.** O que não está declarado **não passa pelo orquestrador**: corre
por chamada directa, com o chamador a conhecer o nome do ficheiro do coletor. É a **G-05**, e
o mapa mostra-a de corpo inteiro.

E os quatro coletores `.mjs` — os da estrada italiana que realmente correu 6 vezes — **não
aparecem em nenhuma das duas listas**: o censo de Python não os vê, e a receita não os
declara.

---

## B · AS SETE ESTRADAS

| ID | estrada | fontes | RAW | RUN | DERIVED | STRUCTURED | ADMISSION | custo | estado |
|---|---|---:|---|---|---|---|---|---|---|
| **RC-01** | Documento oficial por HTTP | 2 | ✅ dono | ✅ dono | ✅ dono | ❌ | ❌ | grátis | **`OBSERVED`** |
| **RC-02** | Coletor recorrente italiano | 7 | ⚠️ Git | ⚠️ Git | ❌ | ❌ | ❌ | grátis | `CODE` |
| **RC-03** | API oficial de plataforma | — | ❌ | ficheiro | ✅ Whisper | ❌ | ❌ | quota | `CODE` |
| **RC-04** | Sessão de navegador | — | ❌ | ficheiro | ✅ Whisper | ❌ | ❌ | grátis¹ | `CODE` |
| **RC-05** | Rota paga (Apify) | — | ficheiro | ficheiro | ❌ | só ES | ❌ | **PAGO** | `CODE` |
| **RC-06** | Conjunto regulatório | — | ❌ | SQL à mão | n/a | ✅ SQL | ❌ | grátis | `LIVE_SCHEMA` |
| **RC-07** | Corpus científico | — | ❌ | ficheiro | n/a | ❌ | ❌ | grátis | `CODE` |

¹ grátis mas depende da sessão da máquina do operador — não é reproduzível no CI.

### Nenhuma estrada está `CLOSED`. Nem a que foi observada.

`COLLECTION_ROUTE_CLOSED` exige doze condições. A **RC-01** — a única `OBSERVED` — falha em
duas:

```
❌ persistência estruturada     o texto existe e nada o guarda como registo
❌ admissão ligada              o texto existe e ninguém o julga
```

> **O documento chega, é preservado, é derivado — e para.** A cadeia tem um fim que não é uma
> porta: é um beco.

### E o `checkpoint` da RC-01 é `NÃO SE APLICA`, de propósito

É um download único por documento; não há cursor a guardar. **Criar checkpoint aqui só para
pintar um quadrado verde seria inventar estado** — e estado inventado é a coisa que esta casa
passou seis missões a remover.

---

## C · OS PROBLEMAS QUE O MAPA TORNOU VISÍVEIS

### 1 · A estrada que mais correu é a que menos dono tem

A **RC-02** — 6 corridas, 144 observações, 7 fontes — escreve **tudo no Git**: a loja dos
bytes, o ledger das observações e o registo das corridas. É a **P-011** viva, e não usa
nenhum dos donos canónicos que as últimas missões construíram.

**A estrada com mais quilómetros é a que está mais longe da fundação.**

### 2 · Apify não é rota por omissão — mas ninguém consegue provar que não é

A **COL-LAW-019** exige cinco campos que justifiquem a escalada para rota paga
(`WHY_PAID_ROUTE`, `CHEAPER_ROUTE_ATTEMPTED`, …). Eles **não existem em ficheiro nenhum**.
Sem eles, «Apify é fallback» é uma intenção, não uma regra.

### 3 · Metadado de artigo não é PDF preservado

Na **RC-07** a cadeia para no metadado. **Descoberto não é coletado**, e confundir os dois
faria o corpus científico parecer maior do que é.

### 4 · A legenda que a plataforma entrega não é derivado nosso

Na **RC-03**, o que o YouTube devolve é `RAW_CAPTURE` — nós não o produzimos. Está certo hoje
e é fácil de errar amanhã.

---

## D · A PERGUNTA DA SEGUNDA FONTE, RESPONDIDA

> ## A próxima missão **NÃO** é a segunda fonte.

**Porque só UMA outra fonte cabe hoje na RC-01** (`IT-T3-001`). As restantes 51 têm rota
`NÃO SEI` — não se sabe sequer que estrada usariam. Fazer um segundo canário na mesma estrada
provaria o que já está provado, e deixaria as 51 exactamente onde estão.

**A lacuna transversal é maior, e destrava mais.**

---

## E · OS CINCO MAIORES BURACOS, por quanto destravam

| # | buraco | destrava |
|---|---|---|
| **1** | **51 fontes sem rota conhecida** | tudo. Sem isto não se sabe quantas estradas faltam construir |
| **2** | **Nenhuma persistência estruturada, em nenhuma estrada** | fecha o fim de **todas** as 7 — hoje toda cadeia acaba num beco |
| **3** | **RC-02 escreve estado operacional no Git** | a estrada com mais quilómetros passa a usar os donos que já existem |
| **4** | **14 executores fora da receita** | a escolha de rota deixa de viver espalhada; mata a G-05 |
| **5** | **Admissão ligada a nenhuma estrada** | `COLLECTED → READY` deixa de ser promessa |

Ordenados por **quantas estradas desbloqueiam**, não por visibilidade no portal.

---

## F · A MENOR SEQUÊNCIA ATÉ `COLLECTION_FOUNDATION_CLOSED`

**Quatro missões.** Agrupadas por dono e por lei — não por fonte.

### M1 · Dar rota às 51 fontes sem rota
**Porquê:** é o buraco que bloqueia todos os outros. Enquanto 51 fontes forem `NÃO SEI`, não
se sabe quantas estradas faltam.
**Estradas:** todas · **Donos:** registo de fontes, `censo_das_estradas_it.py`
**Escreve produção:** não · **Custo:** leitura de metadados (`HEAD`), sem descarregar
**Pronta quando:** toda fonte IT tem `ROUTE_CLASS` atribuída **ou** `BLOCKED` com motivo
escrito. `NÃO SEI` continua permitido — mas com o que falta para o deixar de ser.

### M2 · Dar um fim às estradas: persistência estruturada + admissão
**Porquê:** hoje **nenhuma** das 7 tem fim. É o que impede qualquer uma de fechar, incluindo a
que já foi observada.
**Estradas:** as 7 · **Donos:** um escritor por espécie; `admissao/admissao.py`
**Escreve produção:** só no fim, um canário · **Custo:** nenhum
**Pronta quando:** a RC-01 vai de documento a `READY` com prova, e a RC-01 fecha.

### M3 · Trazer a RC-02 para os donos canónicos
**Porquê:** é a estrada com mais corridas e a que está mais longe da fundação — e é a P-011.
**Estradas:** RC-02 (7 fontes) · **Donos:** `preservar_coleta`, `preservar_derivado`
**Escreve produção:** sim, migração forward das fontes recorrentes · **Custo:** nenhum
**Pronta quando:** a coleta recorrente escreve em `collection_run`/`raw_asset` e o Git deixa de
receber estado operacional novo. **Sem apagar história.**

### M4 · Uma escolha de rota, num sítio só
**Porquê:** 14 executores fora da receita, e a regra do Apify sem os campos que a sustentam.
**Estradas:** todas · **Donos:** `pedido/receitas.py`, `orquestrador/orquestrador.py`
**Escreve produção:** não · **Custo:** nenhum
**Pronta quando:** todo executor está declarado, o orquestrador escolhe, e a escalada para
rota paga escreve os cinco campos da COL-LAW-019.

---

## G · A TRAVA DA INTELIGÊNCIA

```
COLLECTION_FOUNDATION_CLOSED != SIM  →  INTELLIGENCE_IMPLEMENTATION_BLOCKED
```

**Medido: zero áreas de inteligência implementadas neste repositório.** Não há pasta nem
módulo operacional — Field Voices e Opportunity Radar existem em documentos, não em código.

> **A trava é barata de segurar hoje, e é por isso que se escreve hoje** — não no dia em que
> já custar. Quando o andar de cima existe, ninguém volta a mexer na fundação: passam a haver
> telas que dependem dela como está.

**O que ela não impede:** ler código, preservar histórico, consertar defeito que ameace dados,
e medir o que a inteligência futura vai esperar da coleta.
**O que ela impede:** desenvolvimento novo, ligar sinais, pontuação, recomendação, alimentar o
portal.

Contrato em [`TRAVA-DA-INTELIGENCIA.json`](TRAVA-DA-INTELIGENCIA.json), com teste que reprova
se uma área de inteligência aparecer antes do fecho — e que confere que o estado declarado
bate com a medição.

**Critérios cumpridos: 5 de 14.** Faltam **9**.
