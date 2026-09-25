# ONDA2-G3 — o teto por domínio na onda (D38), o congelamento e o disparador da 2.ª onda

Ramo `onda2-g3-v1`, nascido de `7cdb7ea4` (produção: R1 + FILA-ÚNICA + T1). Nada instalado, nada
disparado, nenhum pedido de rede de coleta. Medido em 25/09/2026, entre 02:50 e 03:15 (BRT).

## 1. O disjuntor por domínio (D38)

**Onde vive:** no dono único do teto, o transporte `coleta/italy_pilot_collect.mjs` (`baixar()` → `umaIda()`).
Não há uma segunda cópia da regra: o disparador pergunta ao transporte qual é o domínio.

- **Domínio registável:** `dominioRegistavel(host)` junta `cia.it`, `www.cia.it` e `sub.cia.it`.
  - Nesta casa não havia normalização de domínio, só `siteDe`, que tira o `www.`. Também não há
    Public Suffix List instalada (nem tldextract, nem publicsuffix2).
  - A regra usa as duas últimas etiquetas, salvo os sufixos de dois níveis declarados em
    `SUFIXOS_DE_DOIS_NIVEIS`: `gov.it`, `edu.it`, as regiões italianas da PSL, `co.uk` e outros.
  - Quando a regra não conhece o sufixo, **junta mais** (fica mais apertada) e nunca mais larga.
    Exemplo: `x.provincia.it` conta com `provincia.it`.
- **Pela onda inteira:** quem conduz a onda nomeia um livro em `SINTONIA_TETO_ONDA`. O transporte
  soma nele os pedidos por domínio de **todas** as corridas: todas as fontes e todos os processos,
  com trinco e renomeação.
  - A variável passa sozinha de processo em processo: disparador → orquestrador → executor → `node`.
  - Sem livro, vale o de sempre (uma corrida), mas já contando por domínio.
- **Ao chegar a 5:** os pedidos seguintes desse domínio **não saem** e ficam com o motivo
  `TETO_DOMINIO`. Uma recusa da cortesia não é observação nem falha: `FAILED` fica em 0.
- **Livro ilegível:** falha alto (`TETO_ONDA_ILEGIVEL`) em vez de recomeçar do zero.
- **Resumo da corrida:** passa a registar `TETO_CONTA_POR`, `PEDIDOS_POR_DOMINIO` e `LIVRO_DA_ONDA`.

**Provas:**
- `provas/teto_dominio_local.mjs` → `tests/test_teto_dominio.py`: **7/0**. É o curl de verdade contra
  um servidor em 127.0.0.1, e é o servidor que conta.
  - D1: 5 corridas em `*.cia.test` somam **5** pedidos.
  - D2: o livro diz `{"cia.test": 5}`.
  - D3: as 4 corridas seguintes fazem **0** pedidos, com `TETO_DOMINIO`, e 0 FAILED.
  - D4: `outro.test` não é afetado.
  - D5: sem livro, cada corrida tem os seus 5, e é por isso que o disparador tem de nomear o livro.
  - D6: livro ilegível falha alto.
  - D7: a regra do domínio.
- `tests/test_cortesia_no_transporte.py` (A5): **continua verde**.
- **Mutação** (`provas/teto_dominio_mutacao.py`, numa cópia por `git archive`): **7/7 mortos**
  (`provas/TETO-DOMINIO-MUTACAO.json`). ⚠️ O M1 morre porque a prova rebenta (o livro nunca é
  criado), e não por uma verificação; fica declarado.

### Interface do contador (D40: para a bancada CAPA-MATERIA/ALVOS-NOVOS, `capa-materia-v1`)

**Um ponto só.** O contador vive em `umaIda()` (`coleta/italy_pilot_collect.mjs`), que é a única saída
para uma fonte. **Todo pedido HTTP conta**, venha de onde vier: `robots.txt`, **índice**, matérias,
saltos de redireccionamento e retentativas. O corte é absoluto: `tetoAtingido()` é perguntado em
`licenca()` / `robotsDaOrigem()` / retentativa, **antes** de cada ida.

O que a escolha de alvos («1.º alvo não coletado + até 3 novos por fonte») **pode** usar, só leitura:

| Export | Para quê |
|---|---|
| `dominioRegistavel(host)` | a chave do teto (`cia.it` = `www.cia.it` = `sub.cia.it`) |
| `lerLivroDaOnda()` | `{dominio: pedidos já gastos na onda}` (vazio sem onda; ilegível rebenta) |
| `motivoDoTeto()` | `"TETO_DOMINIO"` com onda, `"TETO_POR_HOST"` sem onda |
| `CORTESIA_PADRAO.TETO_POR_HOST` / `SINTONIA_TETO_POR_HOST` | o teto (5) |

O que ela **NÃO** deve fazer:
- **não somar** nem escrever no livro. Só `umaIda()` gasta (`gastarNaOnda` não é exportado de propósito);
- **não ter** outro contador nem outro teto. Pode *planear* com `5 − gasto` (por exemplo, não
  escolher 3 matérias quando só sobram 2 pedidos depois do índice), mas quem corta é o transporte;
- **não contar à parte o pedido do índice.** Ele já está no mesmo contador. Numa fonte nova, o
  orçamento típico é `robots (1) + índice (1) + até 3 matérias = 5`.

Um alvo que o teto corta volta como `DEFERRED_BY_COURTESY` com `MOTIVO=TETO_DOMINIO`. Não vai ao
livro de observações e fica desconhecido para a onda seguinte (ADIADO ≠ NUNCA).

## 2. Congelar (G3) e o disparador

- **`--congelar`** trazido de `origin/coorte-unica-v1` (`2d605ef6`) por cherry-pick, **sem conflito**.
  Ele exige `--instalacao=<commit>` e `--demotion=<ref B5>`, e grava `ESTADO=CONGELADA`. A coorte
  commitada na produção (a medição de 23/09 20:57) passa a dizer honestamente `ESTADO: PROVISORIA`.
- **Disparador novo `ferramentas/big_collection/onda_web.py`.** O `bc5_big_collection.py` fica como
  registo da 1.ª onda, com uma trava: só corre com `SINTONIA_BC5_REPLAY=1`.
  - lê a coorte do **lugar oficial** `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json` e
    confere que o disco é o do commit (`git show HEAD:`);
  - para `--correr`, exige `--sha256=` igual ao do commit e `ESTADO=CONGELADA`. O
    `C:\bc\COORTE-BIG-COLLECTION.json` deixa de ser lido;
  - abre um **livro novo por onda** (`<saida>/TETO-ONDA.json`) e recusa reaproveitar o de outra onda
    (`--retomar` só para a mesma);
  - a fonte cujo domínio já gastou 5 **não corre** (`TETO_DOMINIO`), e isso não conta para as
    «3 FAILED seguidas»;
  - disjuntor novo: domínio acima de 5 no livro da onda → PARA TUDO. Os 7 disjuntores da BC5 ficam;
  - `--so-plano`: sem rede e sem Sala.
- **Testes:** `tests/test_onda_web.py` **12/0**. **Mutação** (`provas/onda_web_mutacao.py`): **8/8 mortos**
  (`provas/ONDA-WEB-MUTACAO.json`).

## 3. O ensaio numa cópia fiel do vivo

- Clone de `onda2-g3-v1` em `C:/onda2/g3`, com os 14 livros vivos de `source-curator-service-v1`
  (@ `7cdb7ea4`) copiados às 03:10. A lista e os sha256 estão em `ENSAIO-G3-FOTO-DOS-LIVROS.txt`.
- **O plano do runbook agora:** READY 167 (eram 145 às 02:10, porque a R1 está a andar), elegíveis 57
  (eram 39), **PRONTAS 18, as mesmas**. As 18 elegíveis novas estão **todas SEM_CONTRATO_DE_COLETA**:
  12 web (T2 ×5, T3, T5 ×5, T7) e 6 T8/T12. Até alguém as registar na tabela do coletor, a coorte
  não cresce (`ENSAIO-G3-PLANO-MICRO-COLETA.json`).
- **Congelada na cópia, a título de ensaio,** com `--instalacao=ENSAIO-onda2-g3-v1 --demotion=ENSAIO-sem-B5`
  e commit só na cópia: sha256 `729aa26f…` (`ENSAIO-G3-COORTE-CONGELADA-NA-COPIA.json`).
- **`onda_web.py --so-plano`** (`ENSAIO-G3-ONDA-WEB-SO-PLANO.json`):
  - coorte CONGELADA, `PODE_CORRER=true`;
  - **correm 15 de 18**; saltam por `TETO_DOMINIO` IT-T7-121, IT-T7-123 e IT-T7-135 (cia.it);
    IT-T7-118 corre parcial (IT-T7-112 gasta 3, sobram 2);
  - **máximo por domínio: 5**, e **total previsto: 43 pedidos** (a 1.ª onda gastou 54);
  - previsão por fonte = o que a 1.ª onda gastou.
- ⚠️ **O custo do D38:** das 5 fontes do cia.it, só 1 e meia recebem pedidos por onda. É a regra do dono,
  a funcionar; a ordem da coorte decide quais. Rodar a ordem entre ondas é uma decisão que fica em aberto.

## O que NÃO fiz
Não instalei, não disparei, não congelei nada fora da cópia, não mexi no vivo. Não registei contratos
para as 12 elegíveis web sem contrato.
