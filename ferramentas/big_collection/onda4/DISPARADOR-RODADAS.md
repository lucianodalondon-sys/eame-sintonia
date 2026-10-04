# DISPARADOR-RODADAS — a 4.ª onda em rodadas, uma a uma

Missão DISPARADOR-RODADAS (coordenador, 26/09 03:33). Ramo `rodadas-v1`, nascido de `c2-juiz-v1`
(`b91e7661`, que já está sobre o vivo `83de0ccd`). Sem rede real, sem coleta, sem Sala, nada
instalado. **Falta só o mapa** (a INTEGRA regera).

## D79 (bot Luciano, 26/09 03:45): 1 rodada por janela móvel de 24 h

- **Ligada por omissão** no `--correr` (só `--sem-janela-24h` a desliga). Uma rodada só corre quando
  **todos** os seus domínios estão há mais de 24 h sem pedido. Senão PARA com `JANELA_24H` e `ABRE_EM`,
  sem egresso e sem onda (0 pedidos).
- A hora de cada domínio vem **dos livros**: cada `TETO-ONDA.json` debaixo de `--livros-do-dia` (por
  omissão, a pasta-mãe de `--base`) e o `ONDA-WEB-ESTADO.json` ao lado. Hora = instante do RUN_ID (UTC)
  **+ a duração da corrida** (`SEGUNDOS`), para contar do fim. Sem estado, vale a hora da última
  escrita do livro, para todos os domínios dele.
- **Medido com os livros reais** (`--so-plano --livros-do-dia=~/sintonia-sala-italia/ondas`): a
  rodada 1 abre em **26/09 22:58:33 UTC = 19:58:33 (-03)**, 24 h depois de a última fonte da 3.ª onda
  ter acabado. É mais apertado do que «depois de 19:34» (o início da 3.ª onda), porque a janela é
  por domínio e conta do fim de cada corrida. As rodadas 2+ mostram hoje uma hora mais cedo, mas
  isso é só hoje: quando a 1 correr, voltam a fechar 24 h (partilham domínios; testado).

### Defeito meu, consertado na mesma passagem

Com `--teto-dia`, as fontes ADIADAS de uma rodada **perdiam-se**: a rodada fechava sem elas. Agora a
rodada fica **INCOMPLETA** (com `FALTAM`) e a retoma corre **só** as que faltam, na mesma onda
(`--retomar`, o mesmo livro). As `FEITAS` não se repetem.

## O que é

`ferramentas/big_collection/rodadas.py`: o laço que faltava para correr uma onda que não cabe no
teto (D38: 5 pedidos por domínio **por onda**). Cada rodada é uma **onda própria**, com pasta nova
(`<base>/RODADA-NN`) e livro do teto novo, corrida pelo mesmo `onda_web.py --correr --fontes=...`
de hoje. O disparador não pede nada à rede: quem pede é o `onda_web`, como sempre.

```
py ferramentas/big_collection/rodadas.py --so-plano --base=<pasta> --historico=<onda2>,<onda3> [--teto-dia=N]
py ferramentas/big_collection/rodadas.py --correr --sha256=<coorte congelada> --base=<pasta>
      --historico=<onda2>,<onda3> [--rodada=N] [--teto-dia=N] [--livros-do-dia=<pasta das ondas>]
```

### O plano

A coorte oficial pela **ordem justa** do `onda_web` (`so_plano`: quem nunca foi atendido primeiro),
partida em rodadas em que nenhum domínio passa de 5 pedidos **previstos**. Previsto = o máximo medido
nas ondas do `--historico`; sem medida, 5. Gravado **uma vez** em `<base>/RODADAS-PLANO.json`, com o
sha256 da coorte: uma retoma com outra coorte recusa (`PLANO_DE_OUTRA_COORTE`). `--correr` recusa
coorte não congelada (`COORTE_NAO_CONGELADA`) **antes** de qualquer pedido. Isso foi medido na cópia.

### Cada rodada, sempre nesta ordem

| passo | o quê | se falhar |
|---|---|---|
| 1 | portão de egresso IT, consenso de 3 (`superficie/rede.py --portao-de-egresso IT --sem-cache`) | **PARA** sem pedir nada (`EGRESSO_ANTES`) |
| 2 | teto diário, **só com `--teto-dia=N`**: soma dos `TETO-ONDA.json` de HOJE | a fonte cujo domínio passaria N fica **ADIADA**; rodada vazia → **PARA** (`TETO_DIA`, retomar amanhã) |
| 3 | a onda: `onda_web.py --correr --sha256 --fontes=<da rodada> --saida=<base>/RODADA-NN` | — |
| 4 | portão de egresso IT depois | **PARA** (`EGRESSO_DEPOIS`) |
| 5 | **PROVA-TETO** da rodada: o código de `provas/prova_teto_dominio.py`, **importado** (um só dono), sobre `runs.ndjson` | FAIL (>5) ou NAO_SEI → **PARA TUDO** |
| 6 | com `--teto-dia`: o dia inteiro, depois da rodada | acima de N → **PARA** (`TETO_DIA_ULTRAPASSADO`) |
| 7 | relatório: `micro_coleta.py relatorio --estado=<RODADA-NN>/ONDA-WEB-ESTADO.json` | registado; não fecha a rodada sozinho |
| 8 | a onda saiu com código ≠ 0 ou com disjuntor (`PAROU`) | **PARA** (`ONDA_PAROU`) |

Só depois disto a rodada fica `FECHADA` em `<base>/RODADAS-ESTADO.json`.

    UMA RODADA SÓ FECHA COM A PROVA INDEPENDENTE. O CONTADOR QUE CORTA NÃO É O QUE CONFERE.

### Retoma e `--rodada=N`

- Correr de novo começa na **primeira rodada que não fechou**. As FECHADAS não se repetem.
- Uma rodada PARADA a meio retoma **a mesma onda** (`--retomar`, o mesmo livro): os pedidos já
  feitos continuam a contar para o teto dessa rodada.
- `--rodada=N` corre só essa (útil para 1 rodada por dia).
- `--teto-dia` **por omissão está desligado**: sem ele, o comportamento é o do `onda_web` de hoje
  (medido: com livros de hoje já a 5, sem `--teto-dia` a rodada corre igual).

## Provas (sem rede real)

- `tests/test_rodadas.py`: **29/29** (21 + 7 da janela + 1 da rodada incompleta). Um **servidor HTTP em 127.0.0.1 conta** os pedidos por `Host`
  (a.test com 3 fontes de 5, b.test, c.test com duas fontes de 2). A onda falsa faz o que o
  transporte faz: lê e soma o livro da onda, não passa de 5 por domínio, escreve a linha em
  `runs.ndjson` com `CORTESIA.PEDIDOS_POR_HOST`. Cobre:
  - plano: 3 rodadas; limiar exato (3+2 cabe, 3+3 não); sem medida vale 5; o máximo medido;
  - contra o servidor: as 3 rodadas fecham, o servidor nunca vê mais de 5 por domínio numa rodada
    (total a.test 15, b.test 2, c.test 4), uma pasta e um livro por rodada, relatório com `--estado=`;
  - paragens: transporte avariado (acima de 5) → `PROVA_TETO_FAIL` e a rodada seguinte não corre;
    linha em falta → `PROVA_TETO_NAO_SEI`; egresso antes falha → **0 pedidos** ao servidor; egresso
    depois falha; onda com código de erro; plano de outra coorte;
  - retoma: não repete a fechada, retoma a parada com o mesmo livro, `--rodada=N`, rodada inexistente;
  - teto diário: desligado não muda nada; adia o domínio que já gastou hoje; soma as rodadas do
    próprio dia; livro de outro dia não conta; limiar exato.
- **Mutação** (`provas/rodadas_mutacao.py`, cópia por `git archive`): **18/18 mortos**
  (`provas/RODADAS-MUTACAO.json`): sem prova-teto, NAO_SEI fecha, sem egresso antes, sem egresso
  depois, plano `>=` em vez de `>`, retoma repete fechadas, retoma abre onda nova, teto diário
  ignorado, livros de qualquer dia, código da onda ignorado, aceita outra coorte, pasta única,
  relatório sem estado; e, da D79: janela ignorada, janela contada do início, incompleta fecha,
  retoma ignora as feitas, sem a hora do livro.
- **`--so-plano` na cópia com os livros vivos** (`onda4-plano-copia`, proxy morto): **15 rodadas,
  64 fontes, 301 pedidos previstos**, máx. 5 por domínio em todas. É o mesmo plano do `C2-ONDA4.md`.
  Saída: `auditoria-madrugada\RODADAS\so-plano\RODADAS-SO-PLANO.json`.

## O que NÃO faz (e fica declarado)

- **Não agenda.** «1 rodada por dia» é `--rodada=N` (ou `--teto-dia=5`) chamado uma vez por dia por
  quem conduz. O espaçamento continua decisão do dono.
- O teto diário conta os livros pela **data do ficheiro** (`TETO-ONDA.json` modificado hoje, hora
  local). Uma onda que atravesse a meia-noite conta toda no dia em que o livro foi escrito pela última vez.
- A previsão (`PREVISTOS`) só serve para **arrumar** as rodadas. Quem corta é o transporte
  (`umaIda()`), e quem confere é a PROVA-TETO. Uma fonte que peça mais do que o previsto é cortada
  pelo livro da própria rodada.
- A retoma de uma rodada PARADA no passo 1 (egresso antes) não abre onda: não havia livro, não há `--retomar`.

## O que precisa estar instalado antes de usar a sério

1. `c2-juiz-v1` (este ramo parte dele) e `rodadas-v1`.
2. A coorte da 4.ª onda **congelada** no ramo do vivo (`coorte_unica.py --congelar`).
3. A decisão do dono sobre o espaçamento (`--teto-dia`, ou 1 rodada por dia).

## EM PALAVRAS SIMPLES

- Antes, para visitar as 64 fontes sem passar de 5 visitas por site, era preciso digitar 15
  comandos à mão, um por rodada. Agora é **um comando só**, que corre as rodadas uma de cada vez.
- Antes de cada rodada, ele confere se a internet está saindo pela Itália. Se não estiver, para sem
  visitar nada. Depois de cada rodada, confere de novo.
- No fim de cada rodada, ele confere **por outro caderno** se algum site recebeu mais de 5 visitas.
  Se recebeu, ou se ele não conseguir saber, **para tudo**. É como um fiscal que não é o mesmo que
  bateu o ponto.
- Se parar no meio, ao correr de novo ele continua de onde parou, sem repetir o que já terminou.
- **Regra nova do dono (D79):** o mesmo site só é visitado de novo depois de 24 horas. O comando
  confere isso sozinho, lendo os cadernos das ondas anteriores. Pelos cadernos reais, a 1.ª rodada
  da 4.ª onda só pode começar em **26/09 às 19:58** (hora de Brasília), 24 horas depois de a 3.ª onda
  terminar. Se tentar antes, o comando para sem visitar nada e diz a hora em que libera.
- Consertei um erro meu: com a trava por dia ligada, fontes que ficavam para depois se perdiam.
  Agora ficam guardadas, e a próxima vez que o comando rodar, corre só essas.
- Existe uma trava opcional **por dia** (por exemplo, no máximo 10 visitas por site por dia). Ela vem
  **desligada**, para não mudar nada do que funciona hoje. Ligar é decisão do dono.
- Tudo foi testado com um servidor falso, dentro desta máquina, que conta as visitas. Nenhum site de
  verdade foi visitado. Nada foi instalado.
