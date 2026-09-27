# AUDITORIA DA FILA ITALIANA — 2026-09-15

> **Nenhuma coleta correu nesta missão.** Nenhum `SOURCE_ID` foi emitido. Nenhum byte novo
> entrou na árvore. Tudo o que está aqui saiu de prova que já estava versionada no dia 14.

```
CANDIDATAS_MEDIDAS            381
JA_REGISTADAS_NO_ATLAS        140
FILA_RESTANTE                 241        ← bate com o checkpoint da missão
  EM_ANALISE                  241
  RECUSADA                      0
RECUSAS_ANTERIORES_REVOGADAS   25
FICHAS_NOVAS_NO_ATLAS          13        ← reconciliação, não promoção
SOURCE_ID_EMITIDOS              0
POPULACAO_SOURCE_ID           257        antes 257, depois 257
```

Quem re-mede: `py candidatas/decidir_fila_italia.py` (não escreve nada sem `--escrever`).

---

## 1 · O QUE SE DECIDIU, E COM QUE RÉGUA

A régua não foi inventada nesta missão. Foi lida nas **140 fontes italianas que já estão
no atlas** — porque uma régua nova aplicada só às que faltam faz duas classes de fonte com
o mesmo nome.

Cada uma das 140 tem, no seu manifesto, um `REAL_EXAMPLE` que é **um item próprio da
fonte**, não a página de entrada:

```
EXAMPLE_URL · TIPO_ITEM · TITULO · HTTP_STATUS · CONTENT_TYPE
BYTES_LIDOS · SHA256_DO_QUE_FOI_LIDO · DATA_VISIVEL
```

A sonda que qualificou as 381 no dia 14 não tem nada disto. Ela declara o próprio limite,
por escrito, em todas as 381 linhas:

```
sonda HTTP read-only (GET limitado, payload nao preservado)
```

Ela abriu o endereço da fonte, leu o título da página e parou. Isso prova, e prova bem,
**três coisas**: que o endereço responde, quem é o dono, e que o país é a Itália. Não prova
a quarta, que é a que o atlas exige para escrever uma ficha:

> **«O ENDEREÇO RESPONDE» NÃO É «A FONTE ENTREGA ISTO».**
>
> É a diferença entre saber que uma loja existe e saber o que ela vende.

Por isso **as 241 ficam em `EM_ANALISE`**, cada uma com o que está provado e com a frase
exata do que falta — que é, em todas elas, a mesma coisa: abrir **um** item.

Promover as 241 com `REAL_EXAMPLE` em branco teria posto no atlas 241 linhas a dizer
«fonte registada» sem ninguém ter aberto um único item. E, a partir daí, a palavra
REGISTADA deixaria de significar o que significa nas 140 que já lá estão.

---

## 2 · AS 25 RECUSAS DE 14/09 NÃO SE SUSTENTAM

A qualificação do dia 14 recusou 25 fontes. **As 25 foram revogadas hoje**, e voltaram a
`EM_ANALISE`. O motivo é o mesmo nas 25, e está escrito na lei do próprio atlas, no
cabeçalho do `VERDICT`:

> **Nunca converter «não consegui verificar» em RED.**

O que a prova citada realmente dizia, lida linha a linha na folha de sonda dessas mesmas 25:

| o que a recusa invocava | quantas | o que isso é, de facto |
|---|---|---|
| `HTTP 429` + `THIN_BODY` | 12 | o pedido foi travado por ritmo. Ninguém leu a página. |
| `PLATFORM_GENERIC_TITLE` | 10 | o título lido era «Facebook» / «Instagram» — o muro de login. |
| «duplicata real de …0221» | 3 | ver o quadro 2b, abaixo. |

E há um facto que decide a questão sozinho: **a camada de validação tinha dado `PASS` às
25**, com `REJECTION_REASON` vazia. A recusa nasceu depois, numa camada que já não estava a
olhar para a prova.

Mais: a própria nota de descoberta, guardada em cada uma dessas candidatas, já dizia o que
ia acontecer — *«a plataforma não permite prova direta a partir do datacenter (medido:
Facebook devolve 200 para página inventada, Instagram devolve 429 para tudo)»*. O aviso
estava escrito **antes** da recusa, no mesmo ficheiro.

### 2b · Três donos diferentes fundidos num só, pelo muro de login

Três páginas de LinkedIn de **três organizações distintas** foram declaradas duplicatas
umas das outras:

| fonte | identificador estável, que estava na mesma folha |
|---|---|
| FreshPlaza Italia | `linkedin.com/company/1602695` |
| Koppert Italia | `linkedin.com/company/24658052` |
| Libera Università di Bolzano — Sc. agrarie | `linkedin.com/company/833389` |

O endereço canónico guardado para as três — e para a quarta, o CNR — era o mesmo:
`https://www.linkedin.com/login`. É a página para onde o LinkedIn atira quem não está
autenticado.

> **DEDUPLICAR PELO ENDEREÇO FINAL FUNDE TODA A PLATAFORMA NUM SÓ DONO.**

O identificador que distingue as três sem ambiguidade estava na coluna ao lado,
`URL_TESTADA`, o tempo todo.

---

## 3 · TREZE FONTES COM PROVA GUARDADA QUE O ATLAS NÃO MOSTRAVA

O defeito inverso ao da fila, e mais caro.

`data/samples/IT-SOURCE-SAMPLES/` tinha 155 pastas de prova. **Treze** delas pertenciam a
`SOURCE_ID` que **nenhuma ficha do atlas mostrava**. O número existia (cunhado em
`candidatas/ITALY-SOURCE-MASTER-V1.json`), a prova bruta existia em disco com `SHA256`, e
faltava só a linha que liga as duas.

Enquanto isso durasse:

- quem contasse fontes pelo atlas contava **treze a menos**;
- quem contasse pela pasta de provas contava **treze a mais**;
- e o próprio atlas já avisa, na convenção de `SOURCE_ID`, que um número que desaparece
  daqui é um número que alguém **volta a emitir, sem que nada acuse**.

As treze passaram a ter ficha, na secção `RECONCILIAÇÃO` do atlas. **Os 23 ficheiros brutos
tiveram o `SHA256` reconferido contra os bytes em disco em 2026-09-15 — os 23 conferem.**

Onze são **GREEN** e duas são **YELLOW**, e a diferença está na prova:

| | prova | verdict |
|---|---|---|
| 11 fontes | os bytes que o próprio site serviu, guardados em disco | GREEN |
| `IT-T9-002` Bayer Italia · `IT-T9-008` ADAMA Italia | extrato do DOM lido por navegador — o manifesto declara que **não** são os bytes servidos | YELLOW |

Os sites da Bayer Italia e da ADAMA Italia devolvem `403` a `curl` do mesmo IP italiano.

⚠️ **Todas as treze capturas saíram por VPN comercial italiana (Proton AG, Milano).** Como
cada fonte responde a partir de um IP não italiano **não foi medido**. Está escrito em cada
uma das treze fichas, e não numa nota de rodapé.

Verificador permanente: `py candidatas/reconciliar_fichas_orfas.py --verificar` — tem de
devolver `ORFAS=0`. Se voltar a encher, alguém guardou prova e não escreveu a ficha.

---

## 4 · TRÊS DEFEITOS DE LEITURA QUE ESTA MISSÃO CORRIGIU NO CÓDIGO

**4.1 · O atlas parte URL longo em duas linhas.** Medido: 6 das 155 linhas `URL:`
continuam na linha seguinte, indentadas. Um leitor de `^URL:\s*(\S+)` fica com metade do
endereço — e meia chave nunca casa.

> **UM ENDEREÇO TRUNCADO NÃO DÁ ERRO. DÁ UMA FONTE DUPLICADA.**

Com o leitor truncado, a fila media 242; com o leitor certo, mede 241, e as fontes que
saíram estavam no atlas o tempo todo.

**4.2 · Vizinhança de domínio não é identidade, mas ignorá-la emite ID a dobrar.** Três
candidatas têm ficha no atlas **no mesmo domínio, por outra porta** — por exemplo
`unitus.it/it/dipartimento/dafne` na fila contra `unitus.it/dipartimenti/dafne/` da ficha
`IT-T5-014`. Não foram fundidas nem promovidas: levam um aviso escrito na linha da fila,
para que ninguém emita número novo antes de reconciliar. O atlas já tem o campo para isso e
chama-se `DERIVA_DE`.

**4.3 · A prova das 381 vive em `.xlsx` e esta máquina não tem `openpyxl`.**

> **PROVA QUE SÓ SE LÊ COM UMA DEPENDÊNCIA QUE NÃO ESTÁ INSTALADA É PROVA QUE, NA PRÁTICA,
> NINGUÉM LÊ.**

`candidatas/xlsx_simples.py` lê-a com a biblioteca padrão e mais nada.

---

## 5 · O DEGRAU SEGUINTE, E O QUE ELE AINDA NÃO SABE

`candidatas/ITALY-CONTRACT-CANDIDATES-2026-09-15.csv` — **116 fontes** já registadas no
atlas, com **rota provada** (um endereço que devolveu `200`, com o tipo do que voltou
escrito), e **sem contrato**. Hoje existem 5 contratos em todo o repositório, e só um é
italiano.

**Isto não é uma lista de promoção.** Rota provada é a matéria-prima de um contrato, não um
contrato. O que falta a todas as 116 é o que nenhuma rota consegue dizer sozinha: cadência,
o que fazer quando quebrar, que campos se esperam de volta, e quem responde. Está escrito
em coluna própria, em cada uma das 116.

A coluna `BYTES_GUARDADOS_EM_DISCO` separa as duas gerações de prova sem as misturar numa
média: **12** guardam os bytes servidos, **104** guardaram o resumo do item com o `SHA256`
do que foi lido. Por território: T5 33 · T1 23 · T2 22 · T3 13 · T10 12 · T9 5 · T12 4 ·
T7 3 · T11 1.

---

## 6 · O QUE ESTA MISSÃO **NÃO** FEZ

```
COLLECTION_CHANGED      NÃO
COLLECTION_RUNS         0
RAW_OBSERVATION_CRIADA  0
SALA_ALIMENTADA         NÃO
BIG_COLLECTION          não corrida
SOURCE_ID_EMITIDOS      0
AMOSTRAS_NOVAS          0   (a pasta tinha 155 antes e tem 155 depois)
MERGE_NO_TRUNK          NÃO
```

E uma coisa que **não** se decidiu, de propósito: se uma página de Facebook ou Instagram de
um consórcio de vinho serve ao SINTONIA. Pode muito bem não servir. Mas isso é uma decisão
editorial sobre a fonte, e tem de ser tomada com a fonte à frente — não a partir de um
`429`.
