# COLETA-CONTINUA — a coleta como serviço do vivo, 24 horas por dia (D86)

Ordem do dono (D86, `auditoria-madrugada/DECISOES-DONO-2026-09-23.md`): «o sintonia no futuro não vai parar
de rodar coleta 24 horas por dia, já se organize pra isso». **Desenho, não código.** Ramo
`coleta-continua-v1` sobre o vivo `dc0de726`. Sem rede, nada instalado. Os números são medidos (fonte
dita), e o que não se mediu diz NÃO SEI.

## 1. O que a noite de hoje ensinou (medido)

- **A rodada é a unidade errada.** O plano das 15 rodadas mete uma fonte de edagricole.it em **cada**
  rodada (edagricole tem 15 das 64 fontes). Com a janela de 24 h por domínio (D79), depois da R1 as
  R3–R15 ficam **todas** presas até ao dia seguinte, porque todas têm edagricole (e a R3–R5 também
  cia.it). Resultado: com rodadas, corre **1 por dia**. A unidade certa é a **fonte**, e a regra é **por
  domínio**.
- A janela já existe e está provada: `rodadas.ultima_visita_por_dominio` (ondas + recibos de outras
  missões + todos os domínios que a fonte toca) e `janela_fechada`. A ordem pelo rendimento também:
  `prioridade_do_rendimento`. O serviço **reutiliza** estas peças, não as copia.

## 2. O serviço: uma volta curta, repetida (sem arquitetura paralela)

**Onde vive:** um verbo novo no `ferramentas/big_collection/rodadas.py`, `--continuo --uma-volta`, que o
**agendador do Windows** chama a cada 15 min. É o mesmo mecanismo da tarefa `\SINTONIA-Italy-ForwardOnly`
que já existe. Não há um segundo supervisor nem um segundo coletor. A volta chama o `onda_web.py
--correr --fontes=<UMA>` de hoje, que chama o `micro_coleta` e o orquestrador de sempre.

**Porque uma volta curta e não um processo eterno:** hoje o PC reiniciou duas vezes (09:47 e ~10:20).
Uma volta sem estado em memória recomeça sozinha na tarefa seguinte. Tudo o que importa está nos livros.

**Uma volta, por ordem (a mesma do RODADA1-ROTEIRO, mas para UMA fonte):**

| # | passo | se falhar |
|---|---|---|
| 1 | trinco da volta (`COLETA-CONTINUA.lock`, com PID e hora; órfão > 30 min = aviso, não se apaga sozinho) | sai calado (outra volta a correr) |
| 2 | travões: `COLETA-CONTINUA-PARADA.flag` existe → sai; RAM livre < 5 GB → sai **sem** latch (tenta na próxima); `LOCK-PRIORIDADE.txt` de outro dono → sai | ver secção 4 |
| 3 | **escolher a próxima fonte** (`proxima_fonte`, função pura): da coorte congelada, as fontes cujos **todos** os domínios estão há ≥ 24 h sem pedido; entre elas, a de menor classe de prioridade (rendimento) e, no empate, a atendida há mais tempo (ordem justa) | nenhuma livre → sai, anota `NADA_LIVRE_ATE=<mais cedo>` |
| 4 | portão IT de consenso, `--sem-cache`, cache nova | **latch** (§4) |
| 5 | backup, se o último tiver mais de 24 h (§5) | **latch** |
| 6 | a corrida: `onda_web.py --correr --fontes=<SID> --saida=<ONDAS>/CONTINUA/<AAAAMMDD>/<HHMMSS>-<SID>`, com um livro do teto novo | o disjuntor da onda → latch |
| 7 | portão IT depois | **latch** |
| 8 | prova-teto independente da volta (`provas/prova_teto_dominio.py`) **e** do dia (soma dos livros das últimas 24 h por domínio ≤ 5) | FAIL ou NAO_SEI → **latch** |
| 9 | reconciliar a Sala, só SELECT (as funções do NOITE-CONTINUA, que bateram na 3.ª onda: raw 76 = 76, sala 14 = 14) | não bate → **latch** |
| 10 | uma linha em `<ONDAS>/CONTINUA/CONTINUA-<AAAAMMDD>.ndjson`: fonte, domínios, pedidos, docs novos, Sala antes/depois, portões, prova, porquê | — |

**Uma fonte por volta** mantém cada volta curta (na 3.ª onda: 10–74 s por fonte), e o robô nunca espera.

## 3. Conviver com o robô de fontes, sem o PARAR horas

Medido no vivo (`dc0de726`), quem escreve em que livro:

| livro | robô (curadoria/*) | coleta (coleta/, admissao/, micro_coleta) |
|---|---|---|
| `curadoria/LIFECYCLE-*`, `READY-*`, `SOURCE-*`, `FONTES-CANDIDATAS` | **escreve** | **lê** (o portão da coleta) |
| `data/collection-ledger/italy/runs.ndjson`, `observations.ndjson` | não | **escreve** |
| `data/samples/LIVRO-DE-DECISOES.json` (Admissão) | não | **escreve** |
| a Sala (Postgres) e o armazém | não | **escreve** |
| `regras/italy_contracts_onboarded.json` | **escreve** (só ferramentas de onboarding: 8 ficheiros em `curadoria/`) | lê (e 4 ferramentas de ensaio) |

- **A leitura do portão é segura sem parar o robô.** O `LIFECYCLE-LEDGER` é escrito atomicamente
  (`curadoria/lifecycle.py::_gravar`: temporário, fsync, `os.replace`). Um leitor nunca apanha meio
  ficheiro.
- **Os outros livros do robô: NÃO SEI.** Só 8 de 147 ficheiros de `curadoria/` usam `os.replace`. Antes de
  instalar, medir quais dos livros que o portão lê são escritos sem troca atómica. Onde não for atómico,
  a volta lê com repetição (lê, espera 2 s, lê, compara o sha256) em vez de parar o robô.
- **O contrato do coletor** (`italy_contracts_onboarded.json`) é o único livro partilhado. O onboarding é
  manual. Proposta: o onboarding cria `ONBOARDING-EM-CURSO.flag`, e a volta salta enquanto existir.
- **O backup não precisa do robô parado.** O `pg_dump` lê uma fotografia consistente (MVCC do Postgres),
  e o robô não escreve na Sala.
- Conclusão: **`PARAR.flag` deixa de ser passo da coleta.** Fica para instalações e para o rollback.

## 4. Pára sozinha (latch), e quem a solta

| condição | ação |
|---|---|
| portão IT falha (antes ou depois) / VPN fora de IT | **latch** `COLETA-CONTINUA-PARADA.flag` com o porquê; nenhuma volta corre até uma pessoa apagar o ficheiro |
| prova-teto FAIL ou NAO_SEI (da volta ou do dia) | **latch** |
| backup falhado (`pg_dump` ≠ 0, ou `PROVA_VALE` falso na prova semanal) | **latch** |
| reconciliação não bate / disjuntor da onda (egresso, Sala desce, > 30 min, C6) | **latch** |
| 3 fontes seguidas FAILED | **latch** |
| RAM livre < 5 GB, Sala em baixo, LOCK-PRIORIDADE de outro | **salta a volta** (sem latch): tenta na próxima |

O latch é o mesmo mecanismo do `PARAR.flag`: um ficheiro com o porquê. Só se apaga à mão, com a decisão escrita.

## 5. Cadências

- **Backup da Sala:** `pg_dump -Fc` diário (a primeira volta depois das 00:00), 7 dias guardados, com
  sha256 e contagens. A **prova** do backup (restauro numa base descartável e md5 igual,
  `provar_backup_da_sala.py`) é **semanal**, porque é pesada e precisa da LOCK-PESADO. Hoje o roteiro faz a
  prova antes de cada rodada. Com dezenas de voltas por dia isso não cabe.
- **Intelligence:** uma vez por dia (06:00), sobre uma cópia da Sala, como a rodada 2 de hoje
  (EXPERIMENTAL / NAO_PARA_CLIENTE). O retorno dela (`R1-X-R2-E-FONTES.json`) volta a alimentar a
  `prioridade_do_rendimento` no dia seguinte.
- **Mapa:** o código do serviço entra pela cadeia do mapa como qualquer outro (peça `C-ONDA-WEB`).

## 6. Quanto rende por dia (com as 64 fontes de hoje)

Medido no plano instalado e na 3.ª onda (`ONDA3-WEB-20260925-1934`):

- **38 domínios** para 64 fontes. Os únicos com mais de uma fonte: edagricole.it 15 · cia.it 5 ·
  crea.gov.it 5 · enea.it 3 · arpacampania.it 2 · arpa.veneto.it 2.
- Com 1 fonte por domínio por 24 h: **até 38 corridas/dia e ~176 pedidos/dia** (máx. 5 por domínio).
- Rendimento na 3.ª onda: **2,0 docs novos por fonte** e **0,37 itens na Sala por fonte**. Projeção:
  **~76 docs novos/dia e ~14 itens na Sala/dia**.
  ⚠️ **NÃO SEI se aguenta.** A 3.ª onda veio ~11 h depois da 2.ª. Visitar a mesma fonte todos os dias
  pode dar sobretudo `SEEN_AGAIN` (já visto). A primeira semana mede a queda.
- **Ciclo completo:** 32 dos 38 domínios têm 1 fonte e são visitados **todos os dias**; edagricole.it
  leva **15 dias** para passar pelas 15 fontes; cia e crea 5 dias; enea 3.
- **Cada fonte nova** num domínio novo acrescenta +1 corrida/dia. Num domínio que já existe, alonga o
  ciclo dele. As candidatas da FILA-ÚNICA e os contratos novos entram quando a coorte for congelada de
  novo (a coorte continua a ser a única lista: G3).

## 7. O que falta construir (próxima missão, se aprovado)

1. `rodadas.proxima_fonte(...)` e `rodadas.uma_volta_continua(...)`, **puras** (como
   `supervisor.uma_volta_sup`): os testes chamam-nas e conferem a sequência.
2. `--continuo --uma-volta` no CLI, o latch, o trinco e o livro diário `CONTINUA-*.ndjson`.
3. Testes offline contra o servidor local (o arnês de `tests/test_rodadas.py` e de `ensaio_rodada.py`),
   com mutação: domínio ocupado não sai; latch não se solta sozinho; RAM baixa salta sem latch; a volta
   não deixa lock órfão; o teto do dia soma todas as voltas.
4. A tarefa do agendador (15 min) com o mesmo portão que a `\SINTONIA-Italy-ForwardOnly`.
5. **Medir antes de instalar:** a escrita atómica dos livros que o portão lê (§3); e a queda do
   rendimento com visitas diárias (§6).

## EM PALAVRAS SIMPLES

- Hoje a coleta roda em «rodadas», e isso trava: um site com muitas fontes (edagricole) segura todas
  as rodadas. Esta noite só dá para rodar uma.
- A proposta é rodar **uma fonte de cada vez**, a cada 15 minutos. Sempre a melhor fonte cujo site não
  foi visitado nas últimas 24 horas. Assim a coleta não para nunca, e nenhum site recebe mais de 5
  visitas por dia.
- O robô que procura fontes novas **não precisa mais parar**. Cada um escreve nos seus próprios
  cadernos. Só há um caderno em comum, e para esse existe um aviso de «estou mexendo».
- Se a VPN sair da Itália, se a contagem de visitas der errado ou se o backup falhar, a coleta **para
  sozinha** e só volta quando uma pessoa liberar.
- Com as 64 fontes de hoje, a conta dá **até 38 visitas por dia**, ~76 páginas novas e ~14 itens para a
  Sala. Mas isso ainda precisa ser confirmado na prática: visitar todo dia pode trazer menos novidade.
