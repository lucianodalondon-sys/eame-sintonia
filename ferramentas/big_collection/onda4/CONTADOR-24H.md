# CONTADOR-24H — o contador multicanal atómico (D90, prioridade 1 da COLETA-CONTINUA)

Estudo do bot Luciano (D90, `auditoria-madrugada/ESTUDO-ORQUESTRACAO-24H-LUCIANO.md` §2.2): «não encontrei prova de
uma **reserva atómica compartilhada** entre todas as linhas… até a reserva global passar num teste concorrente…
apenas uma linha de rede ativa por vez». Ramo `contador-24h-v1`, sobre o vivo `dc0de726` e **já junto com o vivo novo `554c1ec1`** (LOTE 3, 26/09 22:25; junção sem conflito). Sem rede, nada
instalado. **Falta só o mapa.**

## O defeito que isto fecha (medido no código do vivo)

O transporte web (`coleta/italy_pilot_collect.mjs`) **perguntava** `tetoAtingido()` (lê o livro) e só **depois**
gastava (`gastarNaOnda`, sob trinco). A pergunta ficava **fora** do trinco. Dois processos no mesmo domínio liam
ambos «4» e ambos pediam. Além disso, o livro era **por onda**: duas linhas em ondas diferentes não se viam.

## A interface

```
RESERVAR(domínio_registável, quantidade, janela=24 h, run_id) -> RESERVADO | ADIADO_ATE | FAIL | UNKNOWN
```

| onde | como |
|---|---|
| Python | `coleta/reserva_24h.py::reservar(host, qtd, run_id=, linha=)` · CLI `py coleta/reserva_24h.py <host> [qtd] [run_id] [linha]` |
| Node (o transporte web) | `reservar24h(host, qtd, {runId, linha})` em `coleta/italy_pilot_collect.mjs`, e **cada pedido** passa por ela em `umaIda()` antes de sair |
| o livro | `SINTONIA_TETO_24H` = um JSON `{"RESERVAS": [{DOMINIO, QTD, EM, RUN_ID, LINHA}]}`, janela móvel de 24 h |
| o trinco | `<livro>.trinco` (um directório: mkdir é atómico), **o mesmo** para Python e Node, que assim se excluem um ao outro |
| a regra | ≤ 5 (`SINTONIA_TETO_POR_HOST`) por domínio registável nas últimas 24 h; `googlevideo.com` e `ytimg.com` gastam de `youtube.com` (D41) |

- **RESERVADO**: a reserva foi escrita (quem, quando, quanto). Só então o pedido sai.
- **ADIADO_ATE**: não cabe. `ATE` = o instante UTC em que cabe (sai a reserva mais antiga). O pedido **não sai**.
  No transporte vira a recusa `TETO_24H` (não é falha: `retry_permitido=false`).
- **FAIL**: sem livro (`SINTONIA_TETO_24H` vazio) ou pedido inválido. Não se pede.
- **UNKNOWN**: livro ilegível (JSON partido **ou** JSON sem `RESERVAS[]`) ou trinco preso > 10 s. **Nunca** é tratado
  como vazio, e o livro não é reescrito.
- Sem `SINTONIA_TETO_24H` no ambiente, o transporte comporta-se **exatamente como antes** (os testes do teto por onda
  e da cortesia dão o mesmo resultado que no vivo).
- `rodadas.py --teto-24h=<livro>` põe o livro no ambiente da onda (herdado por `onda_web` → orquestrador → executor → node).

## Provas (sem rede)

- `tests/test_contador_24h.py` **20/20** (sobre `554c1ec1`):
  - a regra: 5 passam e a 6.ª fica adiada com a hora certa; janela móvel; www/sub juntos; googlevideo gasta de
    youtube; quantidade maior do que sobra; quem gastou fica registado;
  - FAIL sem livro e com pedido inválido; UNKNOWN com JSON partido, com JSON sem `RESERVAS`, e com trinco preso;
    o trinco é libertado;
  - **16 processos Python** a correr ao mesmo tempo no mesmo domínio (48 pedidos): **exatamente 5 RESERVADO**;
  - **Python e Node ao mesmo tempo** no mesmo livro: exatamente 5;
  - o gémeo Node: livro ilegível = UNKNOWN; a mesma regra do Python;
  - **a linha social** (freio): pára no 6.º com `TETO_24H` (e googlevideo gasta de youtube); **web e social somam no
    mesmo livro** (3 do transporte Node + 2 do freio, o 3.º do freio é recusado); sem o livro, o freio é o de antes.
- **`provas/contador_24h_local.mjs` — o teste adversarial pedido (8/8).** Cada executor é um **processo Node
  próprio** a correr o **transporte real** (`executarRodada`, curl) contra um servidor em 127.0.0.1 que **conta**.
  Os executores partilham só o livro de 24 h, **sem livro de onda**, que é o caso que o teto antigo não via:
  - **A1** dois executores **concorrentes** no mesmo domínio → o servidor viu **5** pedidos (reservas dos dois
    run_ids, intercaladas); o livro tem exatamente esses 5; o perdedor recebeu `TETO_24H` (recusa, não falha);
  - **A2** o executor seguinte, com o domínio esgotado → **0 pedidos ao servidor** (ADIADO sem pedir), e a
    corrida acaba normalmente;
  - **A3** um executor Python e um Node, concorrentes, no mesmo domínio → ≤ 5; livro = servidor;
  - **A4** outro domínio não é afetado.
- **Mutação** `provas/contador_24h_mutacao.py` **12/12 mortos** (`provas/CONTADOR-24H-MUTACAO.json`): teto folgado ·
  sem trinco · livro ilegível vira vazio · janela ignorada · googlevideo separado · reserva não escrita · o
  transporte não reserva · Node sem trinco · Node com livro ilegível vazio · Node com teto folgado · **o freio social não reserva · o freio social ignora o ADIADO**. Dois mutantes
  sobreviveram à primeira passagem (livro JSON válido sem `RESERVAS`, em Python e em Node): eram buracos dos meus
  testes. Acrescentei os testes e os dois morreram.
- **Regressão sobre `554c1ec1`** (sem `SINTONIA_TETO_24H`): `test_freio_social` 11/11, `test_maestro_social` 12/12,
  `test_baixador_social` 4/4, `test_teto_dominio` OK, `teto_dominio_local` 10/10, `test_corrida_abortada`
  OK, `test_onda_web` 17/17, `test_rodadas` 38/38. `test_cortesia_no_transporte` falha **no C5**, e falha igual no
  vivo `dc0de726` sem esta mudança (29/1 nos dois): é de base, não é desta entrega.

## As outras linhas: onde cada uma se liga (nenhuma está no vivo; cada uma está no seu ramo)

Uma linha só pode pôr pedidos na rede com **uma reserva por pedido** neste mesmo livro. O ponto de ligação de cada uma:

| linha | ramo | onde reservar | como |
|---|---|---|---|
| sites / boletins (`rodadas.py` → `onda_web` → transporte) | **este** | `umaIda()` | **feito** |
| social (Scrap, yt-dlp) | **este** (o freio entrou no vivo com o LOTE 3) | `coleta/teto_da_onda.py::reservar()`, **antes** do livro da onda | **feito**: com `SINTONIA_TETO_24H`, reserva primeiro no livro comum (`linha=SOCIAL`); não reservado = recusa `TETO_24H` registada + `TetoDaOnda`; sem o livro, o freio é o de antes |
| páginas de pesquisadores | `seguir-pesquisadores-v1` | `Transporte._pedir()` (`seguir.py:134`), antes do `urlopen` (robots incluído) | idem, `linha="PESQUISADORES"`; recusa = `PENDENTE` (o motivo que o `seguir` já usa) |
| PDFs de monitorização | `micro-prova-lote2b-v1` | o `buscar` que `ler_pdf_monitorizacao.correr()` recebe | embrulhar o `buscar` com a reserva, `linha="PDF"` |
| lista mestra / APIs científicas | `lista-mestra-v1`, `pesquisadores-t6-v1` | os transportes que ela usa: `T6.CP._get` e `T6._pedir` | reservar no transporte T6, `linha="CIENCIA"` |

**Até cada linha estar ligada a este livro e instalada, vale o estudo: só UMA linha de rede de cada vez.**

## EM PALAVRAS SIMPLES

- Antes, cada programa de coleta tinha o seu próprio caderno de visitas. Dois programas visitando o mesmo site
  ao mesmo tempo podiam, juntos, passar de 5 visitas, porque um não via o caderno do outro.
- Agora há **um só caderno para todos**. Antes de cada visita, o programa **reserva** a vaga no caderno, com
  cadeado. Se não houver vaga, ele não visita e anota «volta às tantas horas».
- Testei com dois programas **de verdade**, rodando ao mesmo tempo contra um site falso que conta as visitas:
  o site recebeu exatamente 5, nunca 6. O programa que chegou depois não visitou nada.
- Testei também o contrário: estraguei o código de 10 jeitos diferentes, e os testes pegaram os 10.
- A coleta de sites **e a das redes sociais** já usam o caderno novo. Os pesquisadores, os PDFs e as APIs
  precisam de uma linha de código cada um, nos seus ramos. Até lá, a regra é uma coleta pela internet de cada vez.
