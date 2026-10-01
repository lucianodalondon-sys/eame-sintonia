# COLETA-CONTINUA — a coleta como SERVIÇO do vivo, agendada por FONTE (D86)

> ⚠️ **D124 (dono, 27/09) — LOTE8-INTEGRA:** o teto fixo **5 pedidos/domínio/24 h deixou de ser regra**. Nasceu como tamanho de um teste (D7), nunca foi medido contra site nenhum; a regra passa a ser teto ADAPTATIVO com freio pelo SINAL medido do site (429, 403 novo, 503, Retry-After, desafio), em construção por outra equipe (`nuvem-teto-adaptativo-v1`). Até lá o 5 fica no código como **FREIO TEMPORÁRIO** (bot Luciano) — não reescrito neste lote. Onde este documento diz «o teto», leia «o freio temporário». Ver `SINTONIA-EAME-KNOW-HOW.md` §222.

Missão COLETA-CONTINUA-SERVICO (27/09). Ramo `claude/coleta-continua-servico-dm3efk`, sobre a produção
`18461b92`. **Sem rede, sem Sala, nada instalado, nenhum livro vivo tocado.**

> D86 (dono, 26/09): «o sintonia no futuro não vai parar de rodar coleta 24 horas por dia» · item 4: a coleta
> contínua como serviço do vivo, **estendendo `rodadas.py`/supervisor, sem arquitetura paralela** · D86-b rodízio
> entre famílias · D86-c linhas por canal em paralelo.

## O problema, medido (NOITE-20260927-2023, 27/09 20:25)

`rodadas.py` agrupa as fontes em rodadas fixas e só corre uma rodada quando **todos** os domínios dela estão
livres há 24 h (D79). Da R4 à R15 **todas** têm `edagricole.it` (e R4–R5 `cia.it`). A R3 fechou (2 fontes,
10 pedidos) e as 12 rodadas restantes ficaram presas até 28/09 20:24 — **inclusive as fontes delas que não são
de edagricole/cia**. Na prática, 1 rodada por dia. E nada relançava o disparador sozinho.

## O que foi feito

| peça | ficheiro | o quê |
|---|---|---|
| o agendador por fonte | `ferramentas/big_collection/coleta_continua.py` (`escolher`) | a cada ciclo, pela **ordem do plano** que o `rodadas.planear` já fez (justa/rendimento, T5 no fim), corre as fontes cujos domínios estão **todos** livres; as outras **esperam**, com a hora em que abrem |
| o serviço | o mesmo (`ciclo`, `main --um-ciclo/--servico`) | um ciclo = RAM → escolha → portão IT → backup → robô → ondas → portão IT → PROVA-TETO → relatório → reconciliação → robô de volta → livro de ciclos |
| o ensaio a seco | `ferramentas/big_collection/ensaio_coleta_continua.py` → `onda4/ENSAIO-COLETA-CONTINUA.json` | o plano real das 15 rodadas, os dois agendadores lado a lado, 0 rede |
| os testes | `tests/test_coleta_continua.py` (50) | servidor em 127.0.0.1 que **conta**; onda falsa que **reserva** no livro de 24 h como o transporte |
| a mutação | `provas/coleta_continua_mutacao.py` → `provas/COLETA-CONTINUA-MUTACAO.json` | 29 defeitos plantados, 29 mortos |

**Nada de coletor novo.** Cada linha corre pelo **mesmo** `onda_web.py --correr --fontes=… --saida=<base>/CICLO-NNNN/<LINHA>`
(`rodadas.onda_real`), entre o **mesmo** portão (`rodadas.portao_real`), com a **mesma** PROVA-TETO
(`provas/prova_teto_dominio.py`, importada), o **mesmo** relatório (`rodadas.relatorio_real`), a **mesma**
janela (`rodadas.ultima_visita_por_dominio`: livros das ondas + recibos) e o **mesmo** contador multicanal
(`coleta/reserva_24h.py`). `rodadas.py` **não foi alterado** (os 24 mutantes dele continuam a valer).

### Quando uma fonte está livre (o freio NÃO muda)

Uma fonte só corre se, para **cada** domínio que ela toca (inclui o do redireccionamento, ex. georgofili.info → .it):

| regra | de onde vem | se falhar |
|---|---|---|
| D79 — nenhum pedido ao domínio nas últimas 24 h | livros `TETO-ONDA.json` + `ONDA-WEB-ESTADO.json` debaixo de `--livros-do-dia`, e `RECIBO*.json` de `--recibos` | espera `JANELA_24H`, abre 24 h depois da última corrida |
| D90 — o livro multicanal de 24 h tem lugar | `--teto-24h` (o mesmo `SINTONIA_TETO_24H` que o transporte reserva) | espera `TETO_24H`, abre quando sai a reserva mais antiga |
| D38 — somando **todas as linhas** do ciclo, ≤ 5 previstos | o orçamento do ciclo, partilhado | espera `TETO_NO_CICLO` (a hora mostrada é agora + 24 h: estimativa) |

E ainda: quem **corta** em runtime é o transporte (reserva por pedido); quem **confere** é a PROVA-TETO sobre
`runs.ndjson` — **de todas as corridas do ciclo juntas** (duas linhas no mesmo domínio somam) **e** de todas as
corridas do serviço nas últimas 24 h.

    O AGENDADOR ESCOLHE; O TRANSPORTE CORTA; A PROVA CONFERE. TRÊS DONOS, NENHUM CONFIA NO OUTRO.

### As linhas (D86-b/c)

Cada linha tem o seu contador (`CICLOS`, `FONTES_TOTAL`, `PEDIDOS_TOTAL`, `PASSAGEM`, `FEITAS_NA_PASSAGEM`) e
**todas** partilham o orçamento de domínio do ciclo e o livro de 24 h. A linha que abre o ciclo **roda** de
ciclo para ciclo. `--paralelo` corre as ondas das linhas ao mesmo tempo.

**Uma linha só corre se estiver LIGADA ao contador de 24 h — medido no código, não declarado** (a chamada de
reserva existe no transporte dela). Nesta árvore, medido:

| linha | transporte | estado |
|---|---|---|
| SITES (sites/boletins, T2/T3/T5/T7/…) | `coleta/italy_pilot_collect.mjs` | **LIGADA** (medida pelo COMPORTAMENTO: `sonda_ligacao_sites.mjs`) |
| BUSCA (`linha_busca`) | `coleta/linha_busca.py` | **LIGADA** — reserva por outra porta (`linha_busca` → `scrap_http` → `teto_da_onda` → `cortesia_adaptativa`); o texto dentro de `linha_busca.py` nunca teve a chamada |
| CIENCIA (OpenAlex/Crossref/ORCID, D91) | `coleta/pesquisadores_t6.py` | **LIGADA** — passou a reservar em `_pedir()` (LIGACAO-4-LINHAS, 30/09); antes só lia o orçamento |
| SOCIAL (YouTube/social, freio social) | `coleta/teto_da_onda.py` | **LIGADA** — é o próprio freio: reserva no livro de 24 h via `cortesia_adaptativa.reservar_ou_esperar()` |
| PESQUISADORES T6 (páginas) | `ferramentas/seguir_pesquisadores/seguir.py` | **LIGADA** — o transporte mudou de sítio (`coleta/seguir.py` não existe nesta árvore) e passou a reservar no livro de 24 h (LIGACAO-4-LINHAS, 30/09) |

**LIGACAO-4-LINHAS (30/09).** As quatro linhas acima deixaram de ser medidas por TEXTO dentro do ficheiro do
transporte — o texto mentia nos dois sentidos (a BUSCA e a SOCIAL reservam por outra porta e ficavam
`ESPERA_LIGACAO`; e o inverso, «o texto lá, a chamada morta», também passava). Passou a medir-se o
COMPORTAMENTO, como a D124-REBASE já fazia para a SITES: `ferramentas/big_collection/sonda_ligacao_linha.py`
corre o transporte contra um livro da cortesia TEMPORÁRIO e um egresso FECHADO e mede o livro — a linha está
LIGADA quando (A) escreveu a RESERVA antes de o pedido tentar a rede e (B) NÃO reserva quando o domínio está
PAUSADO. A CIENCIA e a PESQUISADORES ganharam a reserva que nao tinham; nenhuma tem contador próprio.

Isto é a regra do `CONTADOR-24H.md`: «até cada linha estar ligada a este livro, só UMA linha de rede de cada vez».
Estar LIGADA **não basta** para a linha correr: cada uma precisa também de uma função de candidatas e de onda
(hoje só a SITES tem — as outras ficam `NADA_ELEGIVEL`, que é a resposta certa: não há material para elas neste
ciclo). **Não fiz isso aqui: é mexer no coletor de cada linha, fora do escopo.**

### O robô de fontes

Só se para quando **há fontes a correr** (vai-se gravar na Sala): `curadoria/PARAR.flag`, e confirma-se **no SO**
(`supervisor.ler_estado_servico`) que parou. No fim — corra bem, pare, ou rebente — tira a flag e relança
`curadoria/supervisor.py`, e confirma no SO que voltou. Se a flag já lá estava (outro o parou), **não se toca**.
Se o robô estava parado, fica parado. Sem fontes elegíveis, o robô **não é tocado** (nem backup, nem portão).

### Para sozinho — e fica PARADO até `--rearmar`

| porquê | quando |
|---|---|
| `RAM_ABAIXO_DE_5GB` / `RAM_NAO_SEI` | antes de tudo (a regra da LOCK-PESADO) |
| `LIVRO_24H_NAO_SEI` | livro de 24 h ilegível, ou sem `--teto-24h` |
| `EGRESSO_ANTES` / `EGRESSO_DEPOIS` | portão IT (consenso de 3) |
| `BACKUP_SEM_PROVA_VALE` | `scripts/micro_coleta/provar_backup_da_sala.py` sem `PROVA_VALE: true` |
| `ROBO_NAO_SEI` / `ROBO_NAO_PAROU` / `ROBO_NAO_VOLTOU` | o SO não confirma |
| `PROVA_TETO_FAIL` / `PROVA_TETO_NAO_SEI` / `PROVA_TETO_24H_*` | a prova independente |
| `ONDA_PAROU_<LINHA>` | a onda saiu com código ≠ 0 ou disjuntor |
| `RECONCILIACAO_FAIL` / `_NAO_SEI` | o delta da Sala ≠ as linhas destas corridas (`collection_run`, `raw_asset`, `sala_de_espera`, só SELECT) |
| `ERRO_NO_CICLO` | qualquer excepção (o robô é religado na mesma) |
| `PORTAO_DA_FONTE_NAO_SEI` | o portão da Collection (`collection_gate.avaliar`) não respondeu: sem veredito não se oferece fonte nenhuma |

O estado fica em `<base>/COLETA-CONTINUA-ESTADO.json` → `PAROU`. Os ciclos seguintes recusam (`JA_PARADO`) até
alguém ler e rearmar, dizendo o que viu.

**ADENDO-PARADA (01/10).** Medido no ciclo 146 (vivo `eac885db3`): o agendador deu `IT-T8-051` à onda dos SITES; o
portão da onda recusou (`GATE:ESTADO_NAO_READY`); 0 corridas, 0 pedidos; a prova-teto deu `NAO_SEI` sobre
`RUN_IDS=[]` e o serviço PAROU por nada. Duas mudanças:

1. O agendador pergunta ao **mesmo** portão que a onda usa (`onda_web.py --correr` → `micro_coleta.plano` →
   `collection_gate.avaliar`), no instante do ciclo. Fonte que ele não admite não vai à onda: fica em `ESPERAM` com
   `PORQUE=FONTE_NAO_READY`, `ESTADO_LIDO`, `MOTIVO_DO_PORTAO` e `PORQUE_DO_PORTAO`. A passagem da linha acaba com
   as admitidas (senão uma recusada prendia a linha em `NADA_ELEGIVEL` para sempre). Linha sem candidatas não
   pergunta ao portão: não há nada a oferecer.
2. Ciclo **sem corrida e sem pedido** — estado de cada onda gravado, nenhuma fonte `CORREU`, nenhum `RUN_ID`, livro
   da onda ausente ou a 0 — dá `PROVA_TETO_CICLO=NADA_A_PROVAR` e **não** para. A prova de 24 h corre na mesma se
   houve corridas nas últimas 24 h. Uma corrida, um pedido, um livro ilegível ou um estado em falta = a prova corre
   como antes e para.

### O livro de ciclos — `<base>/CICLOS.ndjson`

Uma linha por ciclo: `INICIO`/`FIM`, `RAM_LIVRE_GB`, por linha as `FONTES`, `CORRERAM`, `PEDIDOS`, `RUN_IDS`,
`DOCS_NOVOS` (raw_asset destas corridas), `SALA_ANTES`/`SALA_DEPOIS`, `ESPERAM` (cada uma com os domínios fechados
e o `ABRE_EM`), `PROXIMO_A_ABRIR`, as duas PROVA-TETO, a reconciliação, o robô antes/depois, e `PARA`.

## O ensaio a seco (0 rede) — `onda4/ENSAIO-COLETA-CONTINUA.json`

**Origem, dita:** o plano é o do documento commitado `ORDEM-RENDIMENTO-ONDA4.md` (as 15 rodadas, fonte a fonte).
Os livros vivos **não estão no repositório**; os de hoje foram **reconstruídos do relato** NOITE-20260927-2023:
R1–R3 fechadas, a R3 (edagricole.it 5 + cia.it 5) acabou 27/09 20:24 (-03). **NÃO SEI:** as horas de R1/R2
(não mudam R4–R15: os domínios delas lá são só edagricole/cia, que a R3 fecha mais tarde) e os recibos das
outras missões (VOZES, MICRO-PROVA, T6). Agora = 27/09 20:25 (-03).

- **Disparador por rodada:** as 12 rodadas por fechar (R4–R15) param todas em `JANELA_24H`. **0 ondas.**
- **Agendador por fonte, agora:** 4 fontes, 20 pedidos, que o disparador deixou presas:

| fonte | domínio | pedidos | rodada do plano | classe |
|---|---|---|---|---|
| IT-T5-080 | crea.gov.it | 5 | 11 | T5 institucional |
| IT-T5-187 | enea.it | 5 | 13 | T5 institucional |
| IT-T5-025 | santannapisa.it | 5 | 15 | T5 institucional (D) |
| IT-T5-160 | cnr.it | 5 | 15 | T5 institucional (D) |

- **Quando abre cada domínio** (as 20 que esperam):

| domínio | abre (UTC) | = Brasília | porquê | fontes à espera |
|---|---|---|---|---|
| edagricole.it | 28/09 23:24 | 28/09 20:24 | JANELA_24H (R3) | 12 (uma por dia: 5 por fonte = o teto) |
| cia.it | 28/09 23:24 | 28/09 20:24 | JANELA_24H (R3) | 2 |
| crea.gov.it | ~28/09 23:25 | ~28/09 20:25 | TETO_NO_CICLO (24 h depois deste ciclo) | 4 |
| enea.it | ~28/09 23:25 | ~28/09 20:25 | TETO_NO_CICLO | 2 |

- ⚠️ **CNR (IT-T5-160)** entra agora. A mensagem de 26/09 10:13 dizia «sem CNR/Coldiretti/ANGA/Unaprol» e o
  `ORDEM-RENDIMENTO-ONDA4.md` deixou «tirar a CNR da 4.ª onda» como **decisão do coordenador**. O serviço não a
  toma: corre o plano. Se a decisão for tirá-la, é tirá-la do plano/coorte antes de ligar.
- **Com os livros reais** (na máquina do coordenador, 0 rede):
  ```
  py ferramentas\big_collection\ensaio_coleta_continua.py --plano=%O%\ONDA4-RODADAS\RODADAS-PLANO.json ^
     --estado-rodadas=%O%\ONDA4-RODADAS\RODADAS-ESTADO.json --livros-do-dia=%O% ^
     --recibos=%SI%\vozes-agronomos,%SI%\micro-prova,%SI%\pesquisadores-t6
  ```
  grava `%O%\ENSAIO-COLETA-CONTINUA.json`. **Correr isto antes de ligar** e conferir a lista.

## D124-REBASE (28/09) — o que mudou por baixo do serviço

A cortesia adaptativa (D124) entrou por baixo deste serviço. **O `.cmd` não precisa de mudar**:

- `--teto-24h=%SI%\TETO-24H.json` continua a ser o livro. No formato antigo (`{"RESERVAS": [...]}`) é **lido** (cada
  reserva conta no gasto de 24 h como contava) e **migrado** para ndjson no primeiro pedido, sob o trinco; o
  original fica em `%SI%\TETO-24H.json.D90.json`. Para migrar à mão antes de ligar:
  `py coleta\cortesia_adaptativa.py --migrar %SI%\TETO-24H.json`. Um livro malformado continua `LIVRO_24H_NAO_SEI`.
- O teto de cada domínio é o **orçamento vigente** da política (`regras/POLITICA-CORTESIA-ADAPTATIVA.json`: SITE 40/24 h,
  sobe sem sinal, recua no sinal), somando o gasto de 24 h e todas as linhas do ciclo; `SINTONIA_TETO_POR_HOST=5` no
  ambiente volta ao 5 manual. Pausa de 24 h e Retry-After fecham o domínio até à hora que o livro diz.
- A janela D79 (1 visita por domínio por 24 h) **só com `--janela-24h`**, como em `rodadas.py` desde a D124.
- A linha SITES só corre se a **sonda** (`sonda_ligacao_sites.mjs`) provar, contra um servidor local, que o transporte
  reserva antes de cada pedido e não pede a um domínio pausado — nunca pelo texto da chamada.

## Instalar e ligar (Windows, no vivo)

Pré-requisitos: este ramo instalado no vivo; a coorte da 4.ª onda congelada (`eb7b6ab7…`, já está);
**não correr mais `rodadas.py --correr` depois de ligar** (o serviço semeia as feitas do `RODADAS-ESTADO.json`
uma vez, no 1.º ciclo; o disparador e o serviço ao mesmo tempo contariam as feitas em dois sítios).

**1. O ficheiro de arranque** (fora do repo, porque leva a DSN): `%SI%\coleta_continua.cmd`

```
@echo off
cd /d %USERPROFILE%\orca\workspaces\eame-sintonia\source-curator-service-v1
set O=%USERPROFILE%\sintonia-sala-italia\ondas
set SI=%USERPROFILE%\sintonia-sala-italia
set SINTONIA_SALA_BACKEND=POSTGRES
set /p SINTONIA_SALA_DSN=<%SI%\SALA_DSN.txt
set SINTONIA_COLLECTION_DSN=%SINTONIA_SALA_DSN%
set SINTONIA_PSQL_EXE=%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe
set SINTONIA_ARMAZEM_RAIZ=%SI%\armazem
set BANCO_DESCARTAVEL_URL=
py ferramentas\big_collection\coleta_continua.py --um-ciclo ^
   --sha256=eb7b6ab75056cff37b892cb7e9e59a553f6b9048ff8a5db961c532e643f0b9e4 ^
   --base=%O%\COLETA-CONTINUA ^
   --plano=%O%\ONDA4-RODADAS\RODADAS-PLANO.json --estado-rodadas=%O%\ONDA4-RODADAS\RODADAS-ESTADO.json ^
   --historico=%O%\ONDA2-WEB-20260925-0812\ONDA-WEB-ESTADO.json,%O%\ONDA3-WEB-20260925-1934\ONDA-WEB-ESTADO.json ^
   --livros-do-dia=%O% ^
   --recibos=%SI%\vozes-agronomos,%SI%\micro-prova,%SI%\pesquisadores-t6 ^
   --teto-24h=%SI%\TETO-24H.json >> %O%\COLETA-CONTINUA\servico.log 2>&1
```

**2. Um ciclo à mão, primeiro** (vê o que ele faz): `%SI%\coleta_continua.cmd`, depois
`py ferramentas\big_collection\coleta_continua.py --estado --base=%O%\COLETA-CONTINUA` e a última linha de
`%O%\COLETA-CONTINUA\CICLOS.ndjson`.

**3. Ligar — o Agendador de Tarefas relança-o a cada 30 min** (é isto que faltava: nada relançava o disparador):
```
schtasks /Create /TN "SINTONIA-COLETA-CONTINUA" /SC MINUTE /MO 30 /TR "%SI%\coleta_continua.cmd" /F
```
Um ciclo sem fontes livres não faz nada (não toca no robô) e sai. Dois ciclos não se sobrepõem (trinco
`COLETA-CONTINUA.trinco`; o segundo sai com código 3). Em alternativa, `--servico --intervalo-min=30` num terminal
deixa o laço no mesmo processo — mas se ele morrer ninguém o relança; por isso o recomendado é o agendador.

## Desligar

| como | efeito |
|---|---|
| `type nul > %O%\COLETA-CONTINUA\PARAR-COLETA.flag` | os próximos ciclos saem sem fazer nada (não é erro). Apagar a flag religa |
| `schtasks /Change /TN "SINTONIA-COLETA-CONTINUA" /DISABLE` | o Windows deixa de o chamar (`/ENABLE` religa) |
| `schtasks /Delete /TN "SINTONIA-COLETA-CONTINUA" /F` | remove |

Um ciclo **a meio** acaba o que começou (e religa o robô). Para o parar a meio: fechar o processo e, depois,
`del curadoria\PARAR.flag` + relançar o supervisor (passo 9 do `RODADA1-ROTEIRO.md`).

**Depois de um PARA:** ler `PAROU` (`--estado`) e a última linha de `CICLOS.ndjson`; resolver; então
`py ferramentas\big_collection\coleta_continua.py --rearmar --base=%O%\COLETA-CONTINUA --porque="<quem, o que viu, o que fez>"`.

## Provas (sem rede)

- `tests/test_coleta_continua.py` **50/50**. Servidor HTTP em 127.0.0.1 que **conta** por `Host`; a onda falsa
  reserva cada pedido no livro de 24 h com o `reserva_24h` real e escreve `runs.ndjson`, `TETO-ONDA.json`,
  `ONDA-WEB-ESTADO.json` e a Sala falsa. Cobre: domínio bloqueado espera e os outros seguem (e a contraprova: o
  `rodadas.correr_rodadas` com o mesmo plano para e não pede nada); 24 h depois abre; o ciclo seguinte vê o que o
  anterior visitou; 5+1 no mesmo domínio (6) não entra; limiar 3+2; livro de 24 h de outra linha fecha o domínio
  com a hora certa; domínio do redireccionamento; ordem do plano; feitas não voltam; passagem nova; duas linhas
  não somam 6; rodízio; contador por linha; linhas em paralelo; linha não ligada não corre; a ligação é medida
  pela chamada; portão antes (0 pedidos, robô intacto, sem backup) e depois; PARADO fica parado até rearmar;
  transporte avariado → PROVA_TETO_FAIL (o servidor viu 6); linha em falta → NAO_SEI; prova de 24 h apanha o que o
  ciclo não vê; RAM 4,9 / NÃO SEI / 5,0; backup sem PROVA_VALE; livro 24 h ilegível / ausente; onda com erro;
  reconciliação que não bate; interruptor; robô religado (também quando o ciclo para ou rebenta), sem fontes não é
  tocado, flag de outro não é tirada, parado fica parado, teimoso / não volta / NÃO SEI; o livro de ciclos; a seco
  não escreve; trinco; o ensaio gravado.
- **Mutação** `provas/coleta_continua_mutacao.py`: **29/29 mortos** (`provas/COLETA-CONTINUA-MUTACAO.json`). Os
  cinco pedidos: domínio bloqueado passa · teto 6 · portão IT pulado · duas linhas somando 6 (orçamento não
  partilhado) · robô deixado parado. Mais 24: robô parado quando o ciclo para, flag de outro tirada, robô que não
  pára ignorado, robô tocado sem fontes, portão depois, prova-teto ignorada, NAO_SEI fecha, prova 24 h ignorada,
  RAM ignorada, RAM NÃO SEI passa, backup ignorado, teto 24 h ignorado, livro ilegível vira vazio, parado não fica
  parado, linha não ligada corre, código da onda ignorado, reconciliação ignorada, só o domínio do plano, feitas
  repetem, rodízio parado, onda sem o livro de 24 h, ligação pelo nome, erro não para, interruptor ignorado.
- **Regressão:** `test_rodadas`, `test_contador_24h`, `test_onda_web` OK (`rodadas.py` não foi tocado).
- **Bateria inteira por nome** (executor `provas/integra_noite/bateria_inteira_por_nome.py`, rede fechada, cópia
  limpa de cada commit; Linux, Python 3.11, node 22): base `18461b92` × ramo `6c80022d`
  (`provas/COLETA-CONTINUA-BATERIA-base-18461b9.json` / `…-ramo-6c80022.json`).

  | | base 18461b92 | ramo 6c80022d |
  |---|---|---|
  | ficheiros de teste | 393 | 394 (+ `test_coleta_continua.py`) |
  | testes corridos | 7.373 | 7.423 |
  | ficheiros vermelhos | 77 | 77 (os mesmos) |
  | falhas por nome | 338 (337 com os números do system-map normalizados) | 338 (337) |

  **337 herdadas · 0 consertadas · 0 novas.** (Neste ambiente Linux as falhas herdadas não são as 415 do
  LOTE4-FINAL, medido em Windows: a comparação vale só dentro da mesma máquina, base contra ramo.)

## O que NÃO faz (declarado)

- Não liga as linhas CIENCIA/SOCIAL/BUSCA/PESQUISADORES ao contador de 24 h, nem lhes dá função de candidatas/onda:
  é mexer no coletor de cada uma. Até lá corre **só a SITES**, e o serviço diz porquê em cada ciclo.
- Não testou o `RoboReal` (tasklist/`Popen` destacado) nem o `backup_real`/`reconciliar_real` contra o Windows e
  o Postgres reais: são as peças do roteiro, chamadas como lá; nos testes estão trocadas por falsos. **NÃO SEI**
  se o supervisor relançado sem janela (`DETACHED_PROCESS`) se comporta igual ao lançado pelo `Start-Process` do
  roteiro — confirmar no 1.º ciclo à mão (`supervisor.py --estado` → RUNNING).
- A hora `TETO_NO_CICLO` é uma estimativa (agora + 24 h); a verdadeira sai do livro depois do ciclo.
- Cada ciclo com fontes faz um backup completo com restauro (o `provar_backup_da_sala.py`): é pesado; com o
  agendador a 30 min e 1 domínio por dia a abrir, são poucos ciclos com fontes por dia.

## EM PALAVRAS SIMPLES

- Antes, as fontes andavam em **turmas fixas**. Se um único site da turma tinha sido visitado há menos de 24 horas,
  a turma inteira ficava parada — mesmo quem não tinha nada a ver com aquele site. Como o site edagricole.it está
  em todas as turmas que faltam, andava **uma turma por dia**.
- Agora cada fonte anda **sozinha**. A cada meia hora o programa olha a lista, na mesma ordem de antes, e manda
  coletar **só as fontes cujo site está livre**. As outras esperam, e ele anota a hora em que cada site libera.
- As regras de educação com os sites **não mudaram**: no máximo 5 visitas por site em 24 horas, somando todos os
  tipos de coleta, e o mesmo site não é visitado de novo antes de 24 horas.
- Testei com os dados de hoje, sem visitar nenhum site: o modo antigo deixava **tudo parado até amanhã às 20:24**;
  o novo já liberava **4 fontes agora** (crea, enea, santannapisa, cnr). Atenção: a CNR estava marcada como
  decisão sua — se for para tirar, tire antes de ligar.
- Antes de coletar ele confere a VPN da Itália, faz backup da Sala e para o robô; depois confere a VPN de novo,
  confere **por outro caderno** se nenhum site passou de 5 visitas, confere a Sala e **liga o robô de volta**.
- Se algo der errado (VPN, backup, contagem, memória abaixo de 5 GB, o robô não volta), ele **para sozinho e fica
  parado** até alguém olhar e mandar continuar.
- Para ligar: um comando no Agendador de Tarefas do Windows. Para desligar: criar um arquivo `PARAR-COLETA.flag`
  ou desativar a tarefa.
- Por enquanto só a coleta de **sites** entra no rodízio. As outras (ciência, redes sociais, pesquisadores, busca)
  ainda não usam o caderno comum de visitas; o programa vê isso sozinho e deixa-as de fora até estarem ligadas.
- Estraguei o programa de 29 jeitos diferentes, de propósito; os testes pegaram os 29.
