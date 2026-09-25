# INSTALAÇÃO-2 · plano de instalação (numerado)

Ramo `instalacao-2-v1`, a partir do vivo `origin/servico-20260923-0923` @ `e5cd691f`
(PACOTE-TEMPO-LUGAR instalado; a Sala real já tem a 033 e 468 revisões). **NÃO instalado.**

## O que entra (sem as 4 chaves)

| peça | ramo @ SHA | o que traz | toca |
|---|---|---|---|
| C9-IDIOMA | `c9-idioma-v1` @ `bcefc6d9` | a MICRO confere a língua do texto colhido | `scripts/micro_coleta/micro_coleta.py` |
| TRAVA-CONTAR (D59) | `trava-contar-v1` @ `3d9aae46` | medidores da trava contam as corridas pelo livro operacional | `system-map/scripts/censo_das_estradas_it.py`, `censo_do_congelamento.py`, `ferramentas/big_collection/onda_web.py`, `resumo_da_onda.py`, `scripts/trava_contar/` |
| REROUTE (D66) | `reroute-d2-v1` @ `ac5e882b` | **só anota**: o item que a gaveta da fonte recusa é perguntado às outras gavetas com régua; `destinos_para_a_sala()` devolve **sempre `[]`** (pouso desligado); só T1/T2 poderiam receber quando se ligar | `admissao/admissao.py`, `curadoria/entrada_final.py`, `ferramentas/reroute/` |

**Sem migração. Sem livro.** Nenhuma das três muda um livro do robô (`curadoria/*.json` operacionais,
`candidatas/`, `data/collection-ledger/`): só código, testes e provas (`data/derivados/TRAVA-MEDIDORES-V1/`,
`ferramentas/*/` resumos). O `.gitattributes` ganha 1 linha (`tests/dados/c9-idioma/** -text`, as amostras
do C9 comparadas por sha256) — não toca ficheiro nenhum do vivo.

**Fica FORA:** 4 chaves (`nuvem-quatro-chaves-sala-v1` @ `6d68dce3`) — conflito de código em
`admissao/admissao.py` (220 linhas) e `admissao/sala_de_espera.py` (leitura POSICIONAL de colunas: um índice
errado grava/lê a coluna errada sem erro) e ainda traz a sua própria 033. À espera do rebase sobre `e5cd691f`
(`auditoria-madrugada/AVISO-INSTALACAO-2-QUATRO-CHAVES.txt`).

## Provas

**Juntas** (`e5cd691f` → `2ddae874`): 0 conflitos de código nas três; só gerados do mapa.

**Testes** na árvore da instalação-2, rede fechada (proxy 127.0.0.1:9):
c9_idioma 9/9 · entrada_final 6/6 · os_medidores_da_trava_veem 23/23 · reroute_d2 10/10 · trava_contar 20/20 ·
e o que já está instalado continua verde: tempo_e_lugar_atravessa 43/43 · fato_do_texto 44/44 ·
a_linhagem_do_ready 13/13 · tempo_e_lugar_da_publicacao 42/42 · retorno_nao_diz_success_na_falha 7/7.

**Ensaio em cópia fiel + Postgres descartável com a cópia da Sala** (`i2_ensaio.sh`, sob LOCK-PESADO e ≥5 GB):
ver secção «Ensaio» abaixo.

## Plano de instalação (numerado)

Git Bash nesta máquina; `VIVA=$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1`;
`S=$HOME/sintonia-sala-italia`. Nada corre sem LOCK-PESADO livre e ≥5 GB.

1. **Pré-condições.** A MICRO de verificação acabou (não se instala com corrida a meio);
   `git -C $VIVA rev-parse HEAD` = `e5cd691f…`. Outro → PARAR (o vivo andou; refazer as junções).
2. **Parar o robô** (`CUTOVER-RUNBOOK.md` passo 1): `PARAR.flag`; a consulta de processos não devolve
   `supervisor|worker|ponte_automatica`.
3. **Fotografia antes** (guardar em ficheiro com hora):
   `git -C $VIVA status --short` (os livros operacionais sujos são normais — anotar a lista);
   `sha256sum` de cada ficheiro dessa lista;
   Sala, SÓ LEITURA (`PGOPTIONS=-c default_transaction_read_only=on`):
   `select count(*) from sala_de_espera` · `select max(versao) from schema_migracao` (= `033`) ·
   `select count(*) from sala_de_espera_revisao` (= 468 ou mais, se a MICRO pousou).
4. **Guardar antes de mexer** (regra da máquina): `git -C $VIVA diff > antes.patch` e, só se houver ficheiros de
   CÓDIGO sujos, `git -C $VIVA stash push -m instalacao-2-<hora>` (os livros ficam onde estão).
5. **Instalar o código:** `git -C $VIVA fetch origin instalacao-2-v1` e
   `git -C $VIVA merge --ff-only <SHA entregue>`. Tem de ser fast-forward sobre `e5cd691f`; se o git recusar
   por um ficheiro sujo em comum → PARAR (nenhuma das três toca livros; se tocar, é outra coisa).
6. **Testes no vivo**, rede fechada:
   `py -m unittest tests.test_c9_idioma tests.test_reroute_d2 tests.test_trava_contar tests.test_entrada_final tests.test_tempo_e_lugar_atravessa tests.test_fato_do_texto tests.test_a_linhagem_do_ready`
   → todos OK. (`tests.test_os_medidores_da_trava_veem` demora ~5 min; correr se houver tempo.)
7. **Livros iguais:** `git -C $VIVA status --short` = a lista do passo 3, e os `sha256sum` iguais.
   Diferente → PARAR e ir ao desfazer.
8. **Mapa:** `py system-map/scripts/correr_a_cadeia.py VALIDAR` no vivo → `SYSTEM_MAP_CHECK=PASS`,
   carimbo IGUAL (o ramo entrega o mapa regerado).
9. **Sala intacta** (só leitura): as três contagens do passo 3 iguais. A instalação-2 não escreve na Sala.
10. **Religar o robô** (`CUTOVER-RUNBOOK.md` passos 8/10). Na próxima MICRO: o relatório traz a verificação de
    língua do C9; e `py scripts/trava_contar/medir_a_n.py` (só leitura) conta a corrida.

### Desfazer

Só código (não há migração nem livro): robô parado; guardar `git status`/`git diff` e um stash com nome;
`git -C $VIVA reset --keep e5cd691f`; `VALIDAR` do mapa; religar. A Sala não precisa de nada.

## Ensaio

(preenchido quando `i2_ensaio.sh` acabar)

## EM PALAVRAS SIMPLES

- Três consertos pequenos, só de programa: a MICRO passa a conferir a língua do texto; os medidores da trava
  contam as corridas certas; e o robô começa a **anotar** quando uma notícia recusada numa gaveta serviria
  noutra — só anota, não muda nada de sítio.
- Não mexe no banco da Sala nem nos livros do robô. Para voltar atrás basta repor o programa anterior.
- As 4 chaves ficam para depois: o conserto delas bate no mesmo sítio do que já foi instalado e tem de ser
  refeito pela equipa delas.
