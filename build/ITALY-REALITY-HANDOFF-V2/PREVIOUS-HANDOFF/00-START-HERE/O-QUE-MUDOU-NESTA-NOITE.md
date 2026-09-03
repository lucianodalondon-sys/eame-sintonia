# O QUE MUDOU NESTA NOITE — 02/09/2026, das 03h50 às 09h20

Se você já tem a versão anterior do pacote, leia só isto. Se é a primeira vez, comece pelo
`README-FIRST`.

---

## Em uma frase

**Os 163 rótulos foram lidos por dentro**, e isso derrubou a maior limitação do pacote,
criou duas camadas novas e desmentiu uma afirmação que estava no resumo executivo.

---

## 1 · A limitação mais cara encolheu

| | antes | agora |
|---|---|---|
| produtos com par cultura × alvo lido | 19 de 163 (**11,7%**) | **102 de 163 (62,6%)** |
| pares de uso lidos no rótulo | 219 | **2.030** |

⚠️ **Ela encolheu, não desapareceu.** 61 produtos seguem sem par lido, e para eles a frase
continua sendo *«não encontramos NESTA LEITURA»* — nunca *«a ADAMA não tem»*.

**Como:** a porta estava aberta o tempo todo. O `curl` recusa a resposta do servlet do
Ministero com `Header without colon` e devolve **0 bytes com HTTP 200**; o mesmo pedido
pelo `urllib` devolve **222 KB de PDF real**.

> **FERRAMENTA QUE RECUSA NÃO É PORTA FECHADA.**

O rótulo tem **três gramáticas**, não uma — tabela, bloco de cultura em prosa, e as duas
listas separadas do herbicida. Faltando as duas últimas, os rótulos mais valiosos do
acervo saíam com zero pares.

---

## 2 · Duas camadas novas no pacote

| arquivo | o que é | quantos |
|---|---|---:|
| `LABEL-USE/label-use-pairs.json` | o que o rótulo autoriza | 2.030 pares |
| `LABEL-USE/label-term-census.json` | ⭐ censo de termo nos **163** | 17 termos |
| `CONVERGENCE/convergence.json` | o encontro com a conversa | 38 + 78 + 282 |
| `RELATIONSHIPS/convergence-links.json` | o que cada convergência puxa | 38 |

E um documento: **`02-DEMO-STORIES_AS-CINCO-HISTORIAS.md`** — quais telas construir,
camada por camada, com os IDs exatos.

**Pacote: 1.688 → 3.756 objetos · 4.133 IDs · 87 arquivos · 0,79 MB.**

---

## 3 · ⛔ Uma afirmação do resumo executivo caiu

A versão anterior dizia que o corpus de vídeo **confirmava por rota independente** que
herbicida era a maior categoria da conversa italiana.

**Não confirmava.** Quando o acervo dobrou, herbicida caiu de 1º (21 de 46 pares) para 3º
(26 de 116) — não porque a Itália mudou de assunto, mas porque **abrimos recortes de melo,
olivo e pomodoro**.

> **O CORPUS É AMOSTRA DAS NOSSAS CONSULTAS, NÃO DO PAÍS.**

O peso de herbicida no portfólio (**91 de 163, 56%**) continua verdadeiro — vem do
**registro**, que é censo. E o censo de termos confirmou por outro caminho: `Echinochloa`
é o termo mais citado de todos, **42 de 163**.

---

## 4 · Metade dos pares da conversa era horta, não lavoura

A régua de pares ganhou o eixo de plateia. Resultado: **54 dos 116 pares** são
`SUSTENTADO_SO_POR_HORTA_DOMESTICA`.

O caso que provou: `POMODORO × PERONOSPORA` chegou com **29 documentos e 15 fontes** — o
terceiro mais forte. Separada a plateia: **15 de horta, 1 profissional**. Tomate de vaso.

⚠️ **E ele é o `IT-CONV-001`**, porque o array ordena por nível e contagem. Quem pegar «os
três primeiros» para o demo pega uma conversa de quintal em primeiro lugar. Por isso o
arquivo traz `RECOMMENDED_DEMO_ORDER`, que põe **a plateia antes da contagem**.

---

## 5 · O achado que só apareceu depois de ler os rótulos

Os **6 produtos** ADAMA que nomeiam *Scaphoideus titanus* — vetor da flavescência dourada,
de controle **obrigatório por lei em 5 regiões** — são os **6 de tau-fluvalinate**, e os
**6 vencem em 31/01/2027**, mesma data em que expira a aprovação europeia da substância.

E na história do arroz: os **6 herbicidas** para *Echinochloa* são todos «fop»
(inibidores de ACCase), e o **GIRE confirma resistência a ACCase em *Echinochloa* no arroz
italiano desde 2011**. ⚠️ Só o HIGHCARD declara o grupo no rótulo; para os outros 5 a
classificação é **nossa**, deduzida do princípio ativo.

---

## 6 · Uma luz verde que não media nada

A validação de referências órfãs usa uma **lista fechada** de prefixos de ID. As famílias
novas — `IT-LBL`, `IT-CONV`, `IT-NOREAD`, `IT-NOTALK`, `IT-CENSUS` — não estavam nela.
A validação devolvia **«0 órfãos» sem ter olhado** para a camada nova.

> **LUZ VERDE SÓ VALE PARA O QUE ELA OLHA.**

Corrigido. O zero agora significa alguma coisa.

---

## 7 · O que ficou de fora, e por quê

| pendência | estado |
|---|---|
| 61 rótulos sem par estruturado | leitura, não registro — a rota está documentada |
| `Bactrocera oleae` no portfólio | **0 de 163** por censo — ausência afirmável, com ressalva |
| ISMEA e ISTAT | bloqueadas pelo **nosso IP**, não pela fonte |
| Instagram, Facebook orgânico, X, TikTok, podcast | **sem porta** — «0 menções» seria mentira, não medição |
| nível 2 do sinal (proporção entre janelas) | `NAO_MEDIDO` — só existe uma janela |
| venda, share, estoque | dado interno, não conectado |
