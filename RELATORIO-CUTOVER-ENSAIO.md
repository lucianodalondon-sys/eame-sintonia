# RELATÓRIO — X1 · ENSAIO GERAL DO CUTOVER (só em cópia)

23/09/2026 · bancada `abastecimento-bot-v1` · branch `cutover-ensaio-v1` · Opus 5.5.
Serviços vivos **só lidos**. Collection não correu. Nada na Sala. Rede cortada na cópia
(`HTTP(S)_PROXY=http://127.0.0.1:9`). Clone `C:/x1` apagado no fim.

Entregáveis: **`CUTOVER-RUNBOOK.md`** (para o coordenador executar) ·
`ferramentas/cutover/CUTOVER-ENSAIO-V1.json` (prova) · `ferramentas/cutover/medir_cutover.py`
e `passos_do_cutover.py` (+ 11 testes em `tests/test_medir_cutover.py`).

## O alvo mexeu três vezes durante o ensaio

| ensaio | HEAD da linha | o que se correu |
|---|---|---|
| 1 | `5a16d077` + as 6 pontas juntas no clone | junção, suíte, SWITCH_PLAN inteiro, bot+worker+observador reais |
| 2 | `fe61a34b` (FINAL da 3.ª passagem) | SWITCH_PLAN à letra (pára no passo 6) e pela ordem corrigida |
| 3 | `8d2344bd` (4.ª passagem: + R1/R2 + Q1) | ordem corrigida, medidores, 7b |
| 4 | `e752c3da` (D15, por empurrar) | só os livros de candidatas e alocação |

`origin/unificacao-v1` = `8d2344bd` às 06:56. O runbook manda medir o FINAL_HEAD na hora.

## Seis defeitos do SWITCH_PLAN, cada um provado

1. **O passo 4 escreve dentro do corte.** `--livro-bot=<corte>/italy_contracts_curator.json`
   muda um ficheiro cujo sha256 está no `CORTE.json`; no passo 6 a reconciliação recusa o
   corte (`CORTE DO SERVICO RECUSADO`, rc 3). Correcção: cópia fora do corte.
2. **`unir_livros_do_servico` não trata candidatas nem alocação.** A viva tem 430
   candidatas e 302 SOURCE_ID que a linha não tem (0 ao contrário). O `git checkout -- .`
   da troca deitava-os fora, e 302 números voltariam a ser atribuídos. Correcção:
   `passos_do_cutover.py 5b`, que copia a viva **só se ela contém a linha**, seguido das
   correcções idempotentes da linha (D13, D15, PAÍS). Medido em `e752c3da`: o resultado é
   a viva mais exactamente as 75 decididas (6 CAPABILITY_BLOCK, 69 POLICY_BLOCK), com as 76
   correcções de país da viva intactas. Juntar com «a linha vence» dava o mesmo hoje, mas
   apagaria uma promoção escrita pela viva depois da última passagem; foi rejeitado.
3. **A marca D10 perde-se.** O pacote G1 marca `CONTRATO_UNICO` no livro do bot (a cópia),
   mas a união escolhe o contrato da ponte, sem a marca: 6/6 perdidas. Correcção:
   `passos_do_cutover.py 5c`, só onde a aquisição é igual.
4. **As fontes da D10 ficam presas sem tarefa.** A reconciliação despromove-as para
   CANARY_PENDING (DONO_DO_CONTRATO), e o REVALIDAR da B3 só olha READY. Ninguém as volta a
   medir. **São 7, não 6**: o ensaio 3 achou IT-T5-049, que não tem marca e fica presa na
   mesma. Os ensaios 1 e 2 tinham-na esquecido. Correcção: `passos_do_cutover.py 7b`, com
   o bot parado; o medidor B4 passa de PARAR a OK.
5. **O portão não dá ~16, dá 29.** 19 → 29: +21 pela régua B2, −11 (8 ESTADO_NAO_READY e
   3 RETIRADA_POR_DECISAO da D9). O briefing esperava da B2 +20/−8: bate a menos de 1, e as
   3 a mais são as retiradas da D9. O «~16» do plano é que não bate. Causa provável, **não
   provada**: a M5 mediu sem o estado mais recente do bot.
6. **O observador não tem `--lane`.** Relançado a partir da linha lê a pasta viva, que é o
   que se quer. Mas a worktree de onde corre passa a ser a casa viva da ponte: se for
   `unificacao-v1`, a M5 não pode continuar a trabalhar lá.

## Medidas (ENTREGA)

- **MERGE_ENSAIO**: 7 junções, 111 ficheiros em conflito. 102 ficaram com o lado da base
  (gerados, que a cadeia regera). 5 ficaram com os dois lados (know-how). 4 foram à mão,
  por significado: `supervisor.py` (os dois: PID tri-estado da M2e **e** PID tem de ser
  python), `test_supervisor.py` (a `Isolado` da base), `architecture.declared.json`
  (união das listas), `aplicar_desbloqueio.py` (a ponta B3 inteira).
- **SUITE_UNIDA**: curadoria 545/548 → **548/548** depois de dois defeitos de junção (10:
  `test_decisao_semantica` escrevia o pulso real; 11: 4 peças declaradas duas vezes). A
  M5 achou os mesmos dois. `tests/` 4578/4855: 82 vermelhos contra 79 da base; os 3 novos,
  por nome, ficaram verdes depois das correcções, corridos um a um. **A `tests/` inteira não
  foi re-corrida depois das correcções.**
- **LIVROS_COPIA**: corte duplo a 30 s, sha256 no `CORTE.json` de cada pasta (lista na
  prova, `LIVROS_COPIA_CORTE_2`). Por exemplo: ledger do serviço `c720385616f0455d…` (2441
  transições); ledger da ponte `aba06704d626cdc6…`.
- **PORTAO**: 19 → 29 (ver defeito 5). As 46 retiradas foram todas recusadas.
- **UM_WORKER**: o diário mostra um lançamento de cada vez. O worker (PID 18060) fez 6
  VALIDATE_ROUTE → RETRY «robots não pode ser lido» (sem rede, como devia), fez 2 voltas e
  saiu ocioso, rc 0. O `pos` do medidor lê isto do diário.
- **RETIRADA**: 46/46 recusadas com `RETIRADA_POR_DECISAO`.
- **PASS_PARCIAL**: só pelos testes (`test_um_so_canario_promove`, 2 OK). Nenhuma volta
  sem rede o produz.
- **REVALIDAR**: o automático dá 0 (ver defeito 4). O manual (7b) enfileira 7.
- **QUARENTENA**: a Q1 está em `8d2344bd`, ligada **só na porta da admissão**, não no
  portão. `test_politica_nao_sei` 6/6 OK. Não foi exercitada (NADA NA SALA).
- **V1_COM_REGUA** (fontes READY_CURRENT; iguais nos ensaios 1 e 2):

  | gabarito | regra | capa que passa | matéria barrada | quarentena | notícias retidas |
  |---|---|---|---|---|---|
  | original (5 fontes) | ACTUAL | 6/8 | 0/1 | 1/9 | 0/1 |
  | original | V1 só índice | **2/8** | 0/1 | 1/9 | 0/1 |
  | controlo (10 fontes) | ACTUAL | 6/11 | 1/7 | 5/18 | 0/7 |
  | controlo | V1 só índice | **1/11** | 1/7 | 1/18 | 0/7 |

  A V1 deixa passar menos capas, sem barrar mais matérias, nos dois gabaritos. ⚠️ O
  original só tem **1 notícia**: esse lado prova pouco.
- **TEMPO_PARADO**: ≈ **4,5 a 5 min** com o mapa depois do relançamento; ≈ 10 min com o
  mapa antes (+245 s +73 s). O mais pesado é a reconciliação (114 s em `8d2344bd`) e as
  três fotografias (~95 s).

## O que fica a pesar, e não é do cutover

- **Paradas sem tarefa**: 440 estados não-finais sem tarefa no bot vivo antes, 517 na
  linha unida depois (433 CONTRACTED_CANARY_FAILED já estavam paradas). Só as 7 da D10
  são do cutover. O resto é o problema geral de quem volta a medir o que falhou.
- **706 transições só no livro da ponte viva** (sem commit): a reconciliação re-deriva 688.
  As outras 18 (10 CANARY_PENDING, 5 com estado fora do vocabulário, 3 READY) não; o estado
  final difere em 94/906 fontes, todas por dado mais recente do bot ou pela despromoção
  DONO_DO_CONTRATO.
- **O medidor B2 conta IDs, não conteúdo.** Não vê uma correcção desfeita. Quem a apanha é
  a comparação do ensaio 4, e o runbook manda correr as correcções depois do 5b.

## Provas dos medidores (lei da mutação)

`__pycache__` limpo, `py -B`, diff de cada mutante mostrado, 11 testes:
10 mutantes, **10 mortos**. Os 3 do `medir_cutover` (ignora tarefa aberta · corte alterado
passa · lados trocados); 3 do 5c/7b (5c sem conferir aquisição · 7b sobre todas as fontes
· 5c escreve sem `--escrever`); 4 do 5b (não confere a linha · alocação só por presença ·
escreve mesmo com PARAR · escreve sem `--escrever`). Na primeira versão do 5b (a que
juntava, depois rejeitada), o mutante «escreve mesmo com PARAR» **sobreviveu**; ganhou um
teste e morreu. Esse teste passou para a versão final.
