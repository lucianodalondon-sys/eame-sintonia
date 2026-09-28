# TETO-ADAPTATIVO-REBASE — D124 instalável sobre a produção `a2aa73f`

> Missão do dono (D124-REBASE, 28/09): a entrega `claude/adaptive-collection-ceiling-i3n4jh @ 163237d` (feita
> sobre `b273660`) foi **reprovada** por um verificador independente sobre a produção
> `servico-20260923-0923 @ a2aa73f42001783f4e66d436cfc94cea4a912c14` (48 commits à frente). Isto corrige
> exatamente o que ele mediu, e nada mais.

Branch: `claude/adaptive-ceiling-rebase-3ghtm0` · base: `a2aa73f` · a linha é **fast-forward** sobre a base.

## 1 · Rebase

`git rebase origin/servico-20260923-0923`. Conflitos reais, resolvidos juntando as duas coisas (o FEED-LIGADO não
perde nada):

| ficheiro | FEED-LIGADO (produção) | D124 (entrega) | junto |
|---|---|---|---|
| `coleta/italy_pilot_collect.mjs` (5 blocos) | contadores `ROBOTS_DO_LIVRO_24H`/`CONDICIONAL_ENVIADO`/`NAO_MODIFICADO_304`; `umaIda(…, condicional)` com `-H` validadores e `-D`; `buscar = baixar(u, 2, {condicional})` | `recuo`/`sinais`; `registarResposta`; timeout (curl 28) = marca; `alvosPorFonteD124` | os dois; o `-D` passou a ir em **todo** pedido (item 4) |
| `regras/motor_de_rota.mjs` (1 bloco) | item com corpo do feed à parte (`comCorpo`/`semCorpo`) | `alvosPorFonte` | `escolherAlvosD40(semCorpo, …, alvosPorFonte)` (`regras/motor_de_rota.mjs:783`) |
| gerados, `INDICE-DE-FONTES`, `CENSO-DAS-LIGACOES`, `LEIA-ANTES-DE-COLETAR` | — | — | os da produção, **regerados pela cadeia** no fim |
| `architecture.declared.json` | texto da coleta contínua | texto do D124 | os dois no mesmo `what` |

**Quebra semântica achada no rebase (não estava na lista):** o FEED-LIGADO usa `JANELA_24H_S` no robots de 24 h
(`robotsDoLivro24h`/`guardarRobots24h`); a D124 tinha apagado essa constante com o contador antigo → a 2.ª corrida com
livro rebentava com `ReferenceError`. De volta em `coleta/italy_pilot_collect.mjs:453`; provado por R8 e pelo mutante M24.

## 2 · As quebras semânticas do verificador

**(a) `coleta_continua.py` não importava** (`AttributeError: module 'rodadas' has no attribute 'TETO'`).
Portado para a cortesia adaptativa (`ferramentas/big_collection/coleta_continua.py`):
- livro = eventos da cortesia (`reservas_24h`, `:177`); teto de cada domínio = **orçamento vigente**
  (`CA.dobrar_eventos`) ou `SINTONIA_TETO_POR_HOST` (manual); fecha o domínio quando `gasto_24h + previstos >
  orçamento` (`TETO_24H`, com a hora exata: `quando_cabem`, `:191`) e quando `gasto_24h + ciclo + previstos >
  orçamento` (`TETO_NO_CICLO`); **pausa de 24 h e Retry-After fecham** até à hora do livro (`:233`);
- a janela D79 **só com `--janela-24h`** (como `rodadas.py` desde a D124);
- a onda herda o livro pelos **dois** nomes (`SINTONIA_TETO_24H` e `SINTONIA_CORTESIA_LIVRO`, `:536`): o novo manda,
  e um só partia o contador em dois;
- a PROVA-TETO do ciclo e das 24 h usa o orçamento que esteve em vigor (reproduzido do livro).

**(b) A linha SITES exigia o texto `reservar24h(host, 1)`.** Agora é medida pelo **comportamento**:
`ferramentas/big_collection/sonda_ligacao_sites.mjs` corre o `baixar()` do transporte (`baixarParaSonda`,
`coleta/italy_pilot_collect.mjs:891`) contra um servidor em 127.0.0.1 com um livro temporário: **A** cada pedido que chega
ao servidor tem RESERVA antes e RESPOSTA depois; **B** um domínio que o livro diz PAUSADO recebe 0 pedidos.
`medir_ligacao` usa a sonda quando a linha a declara (`coleta_continua.py:114-140`). Um transporte com o texto certo
mas sem reservar → NÃO ligada (teste). Custo: ~0,2 s por ciclo.

**(c) O livro vivo `TETO-24H.json` (`{"RESERVAS": [...]}`) era ILEGÍVEL.** Agora (Python e Node, mesma regra):
- **leitura compatível**: cada reserva antiga vira `QTD` eventos RESERVA com o mesmo `EM` e conta no gasto de 24 h como
  contava (`coleta/cortesia_adaptativa.py:139-200`, `.mjs:44-95`);
- **migração** no 1.º escrito, sob o trinco: o ficheiro passa a ndjson; o original fica em `TETO-24H.json.D90.json`;
- `py coleta/cortesia_adaptativa.py --migrar <livro>` (idempotente: 2.ª vez = `JA_NDJSON`);
- D90 **malformado** continua UNKNOWN e nada se escreve. Nenhuma resposta é inventada.

**O `.cmd` (`C:/Users/London1/sintonia-sala-italia/coleta_continua.cmd`) — NÃO foi editado. Não precisa de mudar.**
A linha que ele já tem continua certa:
```
   --teto-24h=%SI%\TETO-24H.json >> %O%\COLETA-CONTINUA\servico.log 2>&1
```
O que **não** fazer: `set SINTONIA_CORTESIA_LIVRO=` para **outro** ficheiro (a instalação antiga do
`TETO-ADAPTATIVO.md` sugeria `data\cortesia\LIVRO-CORTESIA.ndjson` — seriam dois contadores). Se quiser o nome novo no
ambiente, aponte-o para o **mesmo**: `set SINTONIA_CORTESIA_LIVRO=%SI%\TETO-24H.json`. Opcional, antes de religar:
`py coleta\cortesia_adaptativa.py --migrar %SI%\TETO-24H.json`. Os bilhetes do Scrap Engineer vão para
`%SI%\ALERTAS-SCRAP-ENGINEER.ndjson` (ao lado do livro).

## 3 · Testes que prendiam a entrega — ajustes DECLARADOS (D124)

| ficheiro | o que mudou | porquê |
|---|---|---|
| `provas/cortesia_http_local.mjs` + `tests/test_cortesia_no_transporte.py` | C3 exige a pausa da **classe SITE** (5 s, lida do JSON); C4b declara a pausa de 1 s que o Crawl-delay 3 vence; C5/C13 medem o 5 como `SEM_LIVRO`; **novo C4c: Crawl-delay 7 > 5 s**; limiar 30→31 | D124: pausa e teto vêm da política |
| `tests/test_coleta_continua.py` | teto manual 5, janela ligada no helper, a onda falsa **regista a resposta** (1 de cada vez), pausa da classe a 0 numa cópia da política, ambiente limpo entre testes | D124: mesma mecânica, número declarado |
| `provas/scrap_evolucao/feed_ligado_local.mjs` | orçamento inicial 5 declarado numa cópia da política; reservas contadas nos eventos | D124: o livro de 24 h é o da cortesia |
| `tests/test_cortesia_adaptativa.py`, `tests/test_contador_24h.py` | `'{"RESERVAS": []}'` sai da lista de ilegíveis; entra o D90 **malformado** `'{"RESERVAS": 3}'` | era o próprio defeito (c) |
| `provas/coleta_continua_mutacao.py`, `mutantes_feed_ligado.py`, `_mutantes_freio_social.py` | âncoras movidas para o código novo (mesmo defeito, mesmo sítio) | o texto mudou; provadas mortas em P01–P09 |

Nenhuma asserção afrouxada. **Herdada, não tocada:** `cortesia_http_local` C5 «as 3 que ficaram de fora são adiadas
pelo teto» falha **igual na base `a2aa73f`** (o D40 corta em 3 alvos antes do teto) → `test_cortesia_no_transporte`
continua vermelho como na base: base 29 ok/1 falha → agora 31 ok/1 falha (a mesma).

**Testes novos:** `tests/test_teto_adaptativo_rebase.py` (24) e `provas/teto_adaptativo/transporte_rebase_local.mjs`
(9 casos, **independente** do módulo vermelho): R1 robots PROÍBE (sem livro e com livro) · R2 Crawl-delay 6 > 5 s ·
R3/R4 429+Retry-After e `cf-mitigated` lidos do `-D` · **R5 com um curl que devolve `%header{}` VAZIO (imita o 7.83)** ·
R6 sem livro = 5 · R7 o `-w` não pede `%header{}` e todo pedido leva `-D` · R8 robots de 24 h na 2.ª corrida.
Em Windows R5/R7 dizem NÃO_SE_APLICA (o `execFile` não corre o curl de imitação); o resto corre.

## 4 · curl 7.83 (item 4) e 5 · sem livro (item 5)

- `umaIda` grava os cabeçalhos com `-D` em **todo** pedido (`coleta/italy_pilot_collect.mjs:556`); Retry-After e
  `cf-mitigated` saem desse ficheiro (`:577`, leitor único `cabecalhosDaResposta`, `:599`, último bloco = o do servidor);
  os validadores ETag/Last-Modified do FEED-LIGADO saem do mesmo leitor. O `-w` só pede código, tipo e destino.
- Sem livro, o teto por corrida é `SEM_LIVRO.TETO_POR_CORRIDA = MINIMO_24H` (SITE 5, PLATAFORMA 2), declarado em
  `regras/POLITICA-CORTESIA-ADAPTATIVA.json:10`, lido por `tetoDe` (`coleta/italy_pilot_collect.mjs:466`) e pelos gêmeos
  (`teto_sem_livro` / `tetoSemLivro`). Com livro vale o orçamento vigente.

## 6 · Provas

**Bateria Python por nome** (`provas/int_r7/bateria_por_nome.py`, rede fechada, 3 trabalhadores nos dois lados):

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `a2aa73f` | 330 | 7434 | 131 |
| depois `8bbdfd6` | 332 | 7506 | 131 |

**Novas: 0. Sumidas: 0.** (`provas/teto_adaptativo/BATERIA-BASE-a2aa73f.json`, `BATERIA-DEPOIS-8bbdfd6.json`.)
**Bateria Node** (`provas/lote8_integra/bateria_node_por_nome.py`): 11 ficheiros, **idênticos** à base
(`italy_contract_test` 82 falhas e `verificar_a_tela` rc=1 nos dois lados). `NODE-BASE-a2aa73f.json`/`NODE-DEPOIS-8bbdfd6.json`.
Depois de `8bbdfd6` entrou só um teste (ciclo em loopback, `e951c96`) e este relatório: `test_teto_adaptativo_rebase`
24/24 e `test_coleta_continua` 50/50 na cabeça final.

**Mutação** (`provas/teto_adaptativo/mutacao_rebase.py`, cópia por `git archive`, sobre `8bbdfd6`): **35/35 mortos**
(`MUTACAO-REBASE.json`). Os da missão: teto infinito (Node M01, Python M02) · orçamento ignorado (agendador M03, Python
M04, Node M05) · Crawl-delay ignorado (Python M06, Node `umaIda` M07, Node cota M08) · robots PROÍBE ignorado (M09, morto
pelo módulo novo) · egresso IT ignorado (antes M10, depois M11). Os do rebase: sinais sem `-D` (M12), D90 ilegível /
não migra / QTD ignorada (M13–M17), sem livro = 40 (M18), sonda sempre ligada / sem caso B / sem contar reservas
(M19–M21), pausa e Retry-After ignorados no agendador (M22), livro só pelo nome antigo (M23), robots 24 h sem janela
(M24), janela D79 ligada por omissão (M25), teto do ciclo sem o gasto de 24 h (M26), e as âncoras de produção movidas
(P01–P09). Uma rodada intermédia deu 34/35: o M05 sobreviveu (o transporte pré-verifica e ninguém perguntava ao
`reservar` do gêmeo Node) → teste novo `OOrcamentoEsgotadoNosDois` → morto.

**Coleta contínua:** `import coleta_continua` num processo limpo = OK; **1 ciclo a seco pelo CLI** (`--ensaio-a-seco`,
com o livro D90 real no formato antigo, que não é escrito) e **1 ciclo inteiro em loopback** (servidor 127.0.0.1,
portão, backup, robô, prova-teto do ciclo e 24 h pelo orçamento vigente, reconciliação; o livro D90 migra) — PASS.

**Não re-corrido (declarado):** `provas/contador_24h_mutacao.py` (os 20 da entrega) e as mutações de produção inteiras
(`coleta_continua_mutacao.py`, FEED-LIGADO, freio social): só os mutantes cujas âncoras mudaram foram re-provados (P01–P09).

**System Map:** `correr_a_cadeia.py REGERAR` → `VALIDAR` = `SYSTEM_MAP_CHECK=PASS`; `impressao_da_arvore.py
--conferir-carimbo` = IGUAL (medido no commit final; o SHA final vai no relato, porque um commit não sabe o seu SHA).

## 7 · Instalar (coordenador) — fast-forward sobre `a2aa73f`

```bat
cd /d %USERPROFILE%\orca\workspaces\eame-sintonia\source-curator-service-v1
set O=%USERPROFILE%\sintonia-sala-italia\ondas
set SI=%USERPROFILE%\sintonia-sala-italia
type nul > %O%\COLETA-CONTINUA\PARAR-COLETA.flag
rem esperar o ciclo em curso acabar (sem COLETA-CONTINUA.trinco em %O%\COLETA-CONTINUA)
git rev-parse HEAD                                   & rem tem de dar a2aa73f42001783f4e66d436cfc94cea4a912c14
git fetch origin claude/adaptive-ceiling-rebase-3ghtm0
git merge --ff-only <SHA final do relato>
py -m unittest tests.test_teto_adaptativo_rebase tests.test_coleta_continua tests.test_cortesia_adaptativa
node ferramentas\big_collection\sonda_ligacao_sites.mjs            & rem tem de dizer "LIGADA":true
py coleta\cortesia_adaptativa.py --migrar %SI%\TETO-24H.json       & rem MIGRADO (ou JA_NDJSON)
py ferramentas\big_collection\coleta_continua.py --ensaio-a-seco --base=%O%\COLETA-CONTINUA ^
   --plano=%O%\ONDA4-RODADAS\RODADAS-PLANO.json --estado-rodadas=%O%\ONDA4-RODADAS\RODADAS-ESTADO.json ^
   --livros-do-dia=%O% --teto-24h=%SI%\TETO-24H.json
del %O%\COLETA-CONTINUA\PARAR-COLETA.flag
```
A tarefa `SINTONIA-COLETA-CONTINUA` continua a mesma (o `.cmd` não muda). Só `--ff-only`: se o HEAD do vivo não for
`a2aa73f`, parar e perguntar.

| | |
|---|---|
| **MEDIDO (aqui, sem internet)** | tudo o que está em §6, contra servidores em 127.0.0.1 e com curl 8.5 + um curl de imitação do 7.83 |
| **PREVISÃO** | que o curl 7.83 real do `System32` se comporta como a imitação (devolve `%header{}` vazio e grava `-D`); que a sonda corre no `cmd.exe` do vivo como corre aqui |
| **NÃO SEI** | o conteúdo atual do `TETO-24H.json` vivo (não o li); o `.cmd` vivo além do que `COLETA-CONTINUA.md` §1 diz |

## EM PALAVRAS SIMPLES

A mudança que deixava o SINTONIA bater mais vezes por dia em cada site foi feita em cima de uma versão antiga. Quando
alguém a tentou pôr por cima da versão que está a correr hoje, quatro coisas partiam: o robô que coleta de 30 em 30
minutos nem arrancava, ele achava que a linha dos sites estava desligada só porque uma frase do código mudou, não
conseguia ler o caderno onde já anota as visitas, e perdia os avisos dos sites a pedir calma porque o programa de
downloads do Windows é antigo. Agora a mudança está por cima da versão atual; o robô arranca e respeita o novo limite;
a linha dos sites é testada fazendo um pedido de verdade a um site de mentira; o caderno antigo é lido e convertido
sozinho, guardando uma cópia; os avisos dos sites são lidos de um ficheiro que qualquer versão do programa escreve; e
quem pede sem caderno fica no mínimo (5), não em 40. Nada disto mexeu nas regras de educação (robots, sem login, sem
disfarce). E o ficheiro que o Windows corre não precisa de mudar.
