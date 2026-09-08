# ETAPA 2.6 — OS SEIS VEREDITOS

> Medido em 07/09/2026, no ramo `claude/system-map-canonical-v1`.
> Tudo aqui é refazível. Cada número tem, ao lado, o comando que o produz.
> Nada foi coletado, nada foi gasto, nenhum país fora da Itália foi alterado.

---

## COMO LER ISTO

Seis perguntas, seis respostas. Cada resposta é uma de três coisas:

| | o que quer dizer |
|---|---|
| **PROVADO** | foi medido, e o comando que o mede está escrito aqui |
| **CORRIGIDO** | estava errado, foi consertado, e há prova que impede voltar |
| **NÃO SEI** | não foi possível medir. Fica assim, escrito, e não vira palpite |

O «NÃO SEI» não é uma falha. É a resposta honesta quando não há como medir, e
tirá-lo do papel foi o que já custou caro nesta casa: um número entrou como
verdade porque parecia alto, e semanas depois descobriu-se que metade dele
media outra coisa.

---

## VEREDITO 1 — O VOCABULÁRIO DE BUSCA DA ITÁLIA

**CORRIGIDO.**

O vocabulário que a Itália usa para *procurar* tem 68 termos. Deles, 11 eram
espanhóis ou franceses, e viviam em dois pacotes chamados «lote A» e «lote B».

Esses dois pacotes tinham sido tirados do menu do GitHub. Parecia resolvido, e
não estava: quem corresse o ficheiro pela linha de comando recebia-os na mesma
— e o lote A era o valor **automático**, o que vinha quando ninguém escolhia
nada.

> **Esconder o botão não é proteção. É arrumação.**

Agora existe uma porta única no código, `casos_do_lote()`. Ela olha o país de
cada recorte, deixa passar só o italiano, e **diz em voz alta** o que recusou.
O automático passou do lote A para o lote C, que é 100 % italiano.

Nada foi apagado: os recortes espanhóis e franceses continuam guardados, com os
seus termos, para se poder repetir uma coleta antiga e comparar.

```bash
py provas/testa_coleta_canonica.py
```
Provas T2, T4, T5, T6, T7.

---

## VEREDITO 2 — A SAÍDA DE EMERGÊNCIA

**PROVADO que a rota italiana não a alcança.**

Ficou uma saída: quem quiser mesmo correr um lote estrangeiro escreve
`--fora-do-escopo`. Isso é legítimo numa ferramenta genérica — mas não pode ser
uma porta lateral do fluxo italiano.

> **Uma exceção que qualquer caminho consegue pedir não é exceção: é a regra.**

Medido: nenhum botão do GitHub a pede, nenhum ficheiro das gavetas da rota
italiana (`coleta/`, `admissao/`, `orquestrador/`, `pedido/`, `leis/`,
`regras/`) a pede, e numa corrida normal ela está fechada. A palavra só pode
aparecer em dois sítios — a ferramenta onde a saída vive, e as provas que a
testam. Qualquer outro sítio faz a prova cair.

Provas T9, T10, T11.

---

## VEREDITO 3 — A LEI DA AUSÊNCIA NA PORTA DE ADMISSÃO

**CORRIGIDO.**

A peneira dizia **NÃO** sempre que não encontrava nenhuma palavra conhecida.
Com um vocabulário incompleto, isso transforma cada buraco do dicionário numa
rejeição com ar de julgamento — e a coleta encolhe sozinha sem ninguém ter
decidido encolhê-la.

```text
SEM MATCH  ≠  NÃO
SEM MATCH  →  NÃO_SEI
```

Agora a porta só diz NÃO quando tem prova positiva: o item fala claramente de
outro mundo, e a decisão mostra qual. Sem palavra nenhuma, diz NÃO_SEI.

A versão da regra subiu de `1` para `2`, o que permite reabrir só o que a
versão antiga rejeitou por ausência, sem mexer no resto.

Provas L1, L2, L3, L4.

---

## VEREDITO 4 — QUANTO A PENEIRA APANHA

**PROVADO como cobertura. O acerto continua NÃO SEI.**

O vocabulário italiano da porta passou de 0 para 29 palavras. Isso conta
palavras, não acertos — um dicionário grande não prova que a porta acerta, do
mesmo modo que ter muitas ferramentas não prova que a casa está construída.

Medido sobre itens reais: dos **49 itens italianos que têm texto de verdade**
nesta árvore,

| decisão | quantos |
|---|---:|
| SIM | 42 (85,7 %) |
| NÃO_SEI | 7 (14,3 %) |
| NÃO | 0 |

Os 7 NÃO_SEI são todos do mesmo ficheiro do Eurostat: texto de metodologia em
inglês, não conversa agronómica italiana. A porta ter dito «não sei» em vez de
«não» é a lei da ausência a funcionar.

⚠️ **Isto é cobertura, não precisão.** Mede quantos a peneira apanha. Para
saber se as 42 decisões estão **certas** era preciso alguém que leia italiano
marcar à mão o que devia passar, e essa lista não existe. Dizer que a precisão
é alta seria inventar.

```bash
py system-map/scripts/recall_da_porta_it.py
```
Prova T17.

---

## VEREDITO 5 — O CORPO ITALIANO

**CORRIGIDO, e o número antigo continua NÃO REPRODUZIDO.**

Os números «4.654 registos» e «7.088 caracteres» tinham sido contados à mão,
sem regra escrita, e não se repetiam. Conta que não se repete não é medida. A
contagem passou a viver em código:

| o que | quanto |
|---|---:|
| ficheiros italianos | 65 |
| linhas com identificador próprio | 763 |
| objetos dentro de listas | 12.020 |
| letras de prosa nas planilhas | 50.537 |
| ficheiros com alguma prosa | 28 de 65 |

Publicar «registos» sem dizer **qual** das duas contagens foi o que tornou o
número antigo impossível de repetir.

E quanto aos «milhões de caracteres»:

```text
ANTIGO “MILHÕES DE CARACTERES”
= NÃO REPRODUZIDO COMO TEXTO
```

```bash
py system-map/scripts/censo_do_corpus_it.py
```
Provas T1, T12, T13.

---

## VEREDITO 6 — O CORTE ENTRE O PDF E O TEXTO

**PROVADO. É o maior buraco medido da Itália.**

Procurando o número antigo, apareceu outra coisa — mais importante, e que tem
de ser escrita com as palavras certas:

```text
ACHADO NOVO COMPROVADO
= 49 PDFs italianos
= 62,7 MB de evidência bruta
= sem derivação textual localizada
```

**Não** está provado que ali dentro haja milhões de caracteres. Megabyte não é
caractere: um PDF de 6 MB tanto pode ser cinquenta páginas escritas como uma
única fotografia digitalizada. São dois factos separados e escrevem-se
separados.

| o que | quanto |
|---|---:|
| PDF italianos guardados | 49 |
| tamanho em disco | 62,7 MB |
| **PDF com texto derivado** | **6 / 49** |
| **PDF sem texto derivado** | **43 / 49** |
| letras já derivadas (ficheiros `.txt` à mão) | 48.730 |
| caracteres dentro dos PDF | **NÃO MEDIDO** |

Os 6 que têm texto foram feitos **à mão** — não há uma linha de código que
abra um PDF neste repositório.

O desenho, agora no mapa:

```text
EVIDÊNCIA BRUTA (PDF)
        ↓
[ DERIVAÇÃO DE TEXTO — AUSENTE ]   ✂
        ↓
TEXTO QUE A MÁQUINA LÊ
        ↓
VOCABULÁRIO / CLASSIFICAÇÃO / ADMISSÃO
```

> **Ter o documento não é ter o texto.**
> É a diferença entre ter o livro na estante e ter o livro lido.

E há um detalhe que torna isto pior: o leitor do mapa ignora ficheiros
binários de propósito — não sabe abrir um PDF. Ou seja, **os 49 documentos mais
ricos da Itália eram invisíveis para o mapa**. O cartão «Evidência bruta em PDF
(Itália)» existe para deixarem de o ser, e os seus números vêm do censo, que os
conta pelo disco.

**O que isto muda na ordem do trabalho:** não adianta melhorar palavras,
peneira ou disparo enquanto a evidência estiver fechada dentro do PDF. Nenhuma
palavra, por melhor que seja, encontra texto que não existe.

Provas T14, T15, T16.

---

## O QUE FICA POR FAZER, ESCRITO COMO DÍVIDA

| | o que falta | onde está registado |
|---|---|---|
| 1 | abrir os 43 PDF e guardar o texto | COL-023 |
| 2 | 3 ficheiros que prometem prosa e não têm | COL-024 |
| 3 | gabarito humano para medir precisão | COL-025 |
| 4 | `voz.pipeline_video()` testado e nunca corrido | COL-022 |

---

## O QUE NÃO FOI TOCADO

Espanha e França foram lidas para provar que não vazam, e mais nada. Medido no
próprio histórico: 33 ficheiros mudados nesta etapa, **zero** de outro país.

Prova T18.
