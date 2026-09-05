# HANDOFF — RADAR FUTURO ITÁLIA · 45 CANDIDATOS FECHADOS

Upstream. **Não é entrega ao Portal.** Não houve merge, cherry-pick, rebase,
ingestão, promoção nem deploy.

---

## O universo

**45**, e não 14. O artefacto `IT-FUTURO-NOVOS-CANDIDATOS-V1` declarou 14
aprovados porque o resultado do workflow voltou com 996 mil caracteres, eu li os
primeiros 170 mil e transcrevi só os vereditos dos quatro primeiros documentos.
Os 14 são subconjunto exacto dos 45 — nenhum falso, **31 em falta**. A errata
está gravada dentro do ficheiro errado; o certo vive em
`IT-FUTURO-JULGADOS-V1.json`, reconstruído do journal do workflow.

> Ausência de leitura virou ausência declarada — o mesmo erro que a auditoria dos
> rótulos passou a semana a desmontar, cometido por mim no artefacto ao lado.

## O resultado

```
TOTAL_CANDIDATES               45
FICHAS_COMPLETAS               45
REFUTACOES_SOBRE_FICHA_INTEIRA 45
SEM_FICHA                       0
SEM_REFUTACAO                   0

SINAL_COMPLETO                  4     ITFC-009 · ITFC-011 · ITFC-016 · ITFC-018
PARCIAL                        40
DERRUBADO                       1     ITFC-027
```

## O defeito de instrumento que quase falsificou tudo isto

A primeira montagem entregava a ficha ao refutador **dentro do prompt, cortada em
12.000 caracteres**. Medi: as fichas têm mediana de 27.289 caracteres e nenhuma
cabe. Como a ordem das chaves segue o esquema, o corte caía sempre no mesmo
sítio. Em `ITFC-021`, de 26.210 caracteres, o refutador via o título, o facto e a
confiança — e **nunca via** a janela, o portefólio, os seis departamentos, a acção,
o horizonte nem a autoavaliação.

Dos sete testes, só o primeiro corria sobre dados que ele tinha. Os outros
corriam sobre campos ausentes, e o esquema obrigava-o a responder na mesma: saiu
`JANELA_INVENTADA = NAO` e `PORTFOLIO_ERRADO = NAO` sobre campos que nunca lhe
chegaram.

> Um refutador que certifica o que não leu é pior do que nenhum: ele assina por
> baixo da coisa que devia apanhar.

**Correcção**: as fichas passaram a viver em `IT-FUTURO-FICHAS-V1.json` e cada
refutador lê a sua inteira do ficheiro. O esquema ganhou `LI_A_FICHA_INTEIRA`,
`CAMPOS_QUE_NAO_CONSEGUI_VER` e o valor `NAO AVALIAVEL` em cada teste. **Os quatro
vereditos truncados foram descartados e refeitos**, não aproveitados.

## Julgamento duplo, e o que ele mostrou

Os 6 que passaram foram entregues a um **segundo adversário independente**, que
não viu o veredito do primeiro e recebeu uma instrução diferente: *o seu trabalho
não é confirmar, é encontrar o que ele deixou passar*.

```
JULGADOS_DUAS_VEZES   6
CONCORDARAM           4     ITFC-009 · ITFC-011 · ITFC-016 · ITFC-018
DISCORDARAM           2     ITFC-006 · ITFC-029   (ambos SINAL_COMPLETO -> PARCIAL)
```

Regra aplicada, declarada antes de correr: **fica o veredito mais severo**.
Discordar para baixo é barato; discordar para cima exige provar, e nenhum dos dois
provou nada ao outro. Os quatro que sobreviveram a duas leituras independentes
deixam de ser opinião de um agente e passam a ser propriedade do documento.

O segundo adversário derrubou `ITFC-006` por uma razão que o primeiro não viu: a
lista de substâncias que a ficha atribuía à discussão de ticchiolatura pertence à
relação de Colletotrichum/GLS de outro relator — e a ficha construiu a hipótese
oposta à frase que está no mesmo parágrafo do mesmo ficheiro («*si è più spostato
l'uso di Captano e Fluazzinam … per avere la possibilità di impiegare una parte di
queste molecole DOPO la fase primaria*»). Inferência de sentido único com a
contra-prova ao lado.

## A que se devem as quedas

`IT-FUTURO-QUEDAS-V1.json` — 16 padrões nomeados por leitura dos 39 vereditos
inteiros, cada um com exemplo literal, separando **defeito da ficha** de **limite
do mundo**.

```
27  caem SÓ por defeito da ficha
11  caem pelas duas coisas ao mesmo tempo
```

Os três padrões `DA_FICHA` mais frequentes:

| n | padrão |
|---|---|
| 26 | o presente da fonte escrito como presente de hoje — a armadilha do «adesso» |
| 22 | aspas que não são aspas: ASR alisado, colchete que substitui em vez de completar |
| 17 | offset que não aponta para a frase que diz apontar |

E o mais frequente em absoluto é `DO_MUNDO`, em **38 das 39**: a campanha ou o
acto que o gatilho vigiava já correu sem ninguém olhar. As fontes são de Outubro
de 2025 a Maio de 2026 e a leitura é de Setembro de 2026. Isso não é defeito de
ninguém — é a idade do acervo, e é o argumento mais forte para a próxima recolha.

### Causa, pelos flags do refutador

```
DATA_DERRUBOU_OU_REBAIXOU        ITFC-027 · ITFC-037
JANELA_DERRUBOU_OU_REBAIXOU      nenhum
PORTFOLIO_DERRUBOU_OU_REBAIXOU   ITFC-027
OUTROS_REBAIXAMENTOS             39   (com motivo e defeitos íntegros no artefacto)
VEREDITOS_REBAIXADOS_POR_REFUTADOR  3   ITFC-006 · ITFC-007 · ITFC-030
```

### O refutador foi mole? **Não.**

Zero janelas inventadas e zero uniões maquiadas em 45 fichas podia ser moleza. Não
é, e prova-se com trabalho: em `ITFC-041` a ficha assinou «grep sistemático dos
doze meses… esta é a única ocorrência»; o refutador correu o grep, achou **14
ocorrências** e uma segunda janela de intervenção que a ficha nunca leu. Em
`ITFC-034` refez as doze contagens alegadas e **absolveu** por medição — «batem
TODAS ao número». Também sabe absolver, não só condenar.

O que explica os zeros é a instrução: desde o primeiro prompt, `NÃO SEI` com base
declarada era resposta certa e não defeito. Quem não precisa de inventar, não
inventa.

## A regra que ficou

> **Quem só verifica a data quando ela ajuda não está a verificar.**

`ITFC-027` caiu por isso: testou a validade do rótulo contra hoje («válido a
partir de 02/05/2026, portanto vivo hoje») e não testou a validade do estado da
praga contra hoje. Aplicou a prova só onde ela sustentava o sinal.

## Artefactos

| ficheiro | o que é |
|---|---|
| `IT-FUTURO-JULGADOS-V1.json` | os 76 julgamentos da régua, 45 aprovados, com `CAND_ID` estável |
| `IT-FUTURO-FICHAS-V1.json` | as 45 fichas operacionais inteiras |
| `IT-FUTURO-SINAIS-V1.json` | os 45 com veredito, causa, valor e mapa de acção |
| `IT-FUTURO-QUEDAS-V1.json` | os 16 padrões de queda, com exemplos |
| `TOP3-RADAR-FUTURO-ITALIA.md` | os três de maior valor, em linguagem de utilizador |
| `IT-FUTURO-NOVOS-CANDIDATOS-V1.json` | **errado**, mantido com errata dentro |

Scripts: `it_futuro_extrair_fichas.py`, `it_futuro_fichas.py`, `it_futuro_top3.py`.
Tudo reprodutível num contentor novo a partir do repositório e dos journals.

## Estado

```
READY_FOR_CANONICAL_REVIEW = SIM
READY_FOR_PORTAL           = NÃO
```

`SIM` na revisão canónica **não** significa `SIM` no portal. Isto é material
upstream para revisão humana, não uma carga pronta a ingerir. Três razões
concretas, e nenhuma delas se resolve na Linha B:

1. **Só 4 dos 45 são `SINAL_COMPLETO`**, e mesmo esses trazem defeitos de higiene
   listados pelo refutador que a redacção final tem de corrigir.
2. **Nenhum sinal é `AGIR_AGORA`.** 24 são `PREPARAR`, 21 `MONITORAR`. Um portal
   que os mostre como accionáveis hoje mente sobre o calendário.
3. **38 dos 39 têm o gatilho por responder** — a campanha de 2026 correu sem
   ninguém observar. Publicar sem isso resolvido é publicar um teste de
   falsificação em aberto.

Paro aqui.
