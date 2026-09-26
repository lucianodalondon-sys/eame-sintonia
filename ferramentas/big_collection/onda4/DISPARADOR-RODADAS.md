# DISPARADOR-RODADAS — a 4.ª onda em rodadas, uma a uma

Missão DISPARADOR-RODADAS (coordenador, 26/09 03:33). Ramo `rodadas-v1`, nascido de `c2-juiz-v1`
(`b91e7661`, que já está sobre o vivo `83de0ccd`). Sem rede real, sem coleta, sem Sala, nada
instalado. **Falta só o mapa** (a INTEGRA regera).

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

- `tests/test_rodadas.py`: **21/21**. Um **servidor HTTP em 127.0.0.1 conta** os pedidos por `Host`
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
- **Mutação** (`provas/rodadas_mutacao.py`, cópia por `git archive`): **13/13 mortos**
  (`provas/RODADAS-MUTACAO.json`): sem prova-teto, NAO_SEI fecha, sem egresso antes, sem egresso
  depois, plano `>=` em vez de `>`, retoma repete fechadas, retoma abre onda nova, teto diário
  ignorado, livros de qualquer dia, código da onda ignorado, aceita outra coorte, pasta única,
  relatório sem estado.
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
- Existe uma trava opcional **por dia** (por exemplo, no máximo 10 visitas por site por dia). Ela vem
  **desligada**, para não mudar nada do que funciona hoje. Ligar é decisão do dono.
- Tudo foi testado com um servidor falso, dentro desta máquina, que conta as visitas. Nenhum site de
  verdade foi visitado. Nada foi instalado.
