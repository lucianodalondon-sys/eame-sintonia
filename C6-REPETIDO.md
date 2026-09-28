# C6-REPETIDO — o C6 passa a conhecer a fusão da Sala por documento

Missão `nuvem-c6-repetido-v1` · 28/09/2026 · ramo `claude/c6-repetido-dedup-doc-9eqszm`, nascido de
`e24139702` (`servico-20260923-0923`, o vivo). **NÃO feito merge. NÃO instalado.** Produção, Sala real,
coleta e VPN **não tocadas**: tudo abaixo correu em cópia de código, com banco falso ou num Postgres
descartável criado e destruído na hora.

## ESTADO

```
C6_FALSO_ALARME_58_1243        CORRIGIDO NO CÓDIGO (PASS no caso reconstruído, banco falso E esquema real)
FRONTEIRAS (reprovam)          outro universo · identidade não provada · SIM que não pousou · SALA_SEM_SIM
MUTAÇÃO                        10/10 mortos
BATERIA POR NOME               0 sumidas · 1 nova antes da regeração = o carimbo do System Map (re-medida depois: ver §4)
SYSTEM MAP                     regerado pela cadeia no commit final; --conferir-carimbo: ver relato do commit final
INSTALADO                      NÃO (decisão do coordenador; nada a migrar — só Python, só SELECT)
```

## O que mudou (só o critério)

`scripts/micro_coleta/micro_coleta.py`:

- **`fusoes_na_sala`** (`:569`, novo). Para os SIM do livro que **não pousaram** nesta corrida, pergunta à
  Sala (só `SELECT`) duas coisas:
  - **FUNDIDO_POR_ITEM** — o mesmo `item_id` está na Sala noutra corrida, **no mesmo universo** da decisão.
  - **FUNDIDO_POR_DOCUMENTO** — o bruto do item e o bruto de uma linha da Sala **noutra corrida** têm o mesmo
    `(source_id, document_key)`, **os dois `FORWARD_IDENTIFIED`**, e a linha está **no mesmo universo**. É a
    condição do SQL da Sala (`admissao/sala_de_espera.py:817-828`, 2.º `not exists`), igual.
  - O SQL faz só a **junção** (mesma fonte e chave, outra corrida). A identidade e o universo **não** vão no
    `WHERE`: vêm na resposta e quem os exige é o Python (`:606`, `:608`, `:610`). Assim o «NÃO SEI» fica
    visível com motivo, e a exigência é testável (e mutável).
- **`C6_ZERO_BYPASS`** (`:740`): `SIM_FORA_DA_SALA` passa a ser só o SIM que não pousou **e** não foi
  fundido — **só este reprova**. Novos campos, ao lado: `FUNDIDO_POR_ITEM` e `FUNDIDO_POR_DOCUMENTO`
  (`"derived:1243->derived:58"`), `PROVA_DA_FUSAO` (linha da Sala que recebeu: item, run_id, universo, raw
  dos dois lados, source_id, document_key) e `SIM_FORA_DA_SALA_PORQUE` (`NAO_POUSOU`,
  `IDENTIDADE_NAO_PROVADA …`, `LINHA_DA_SALA_SEM_IDENTIDADE_PROVADA …`, `MESMO_DOCUMENTO_OUTRO_UNIVERSO …`).
- **`SALA_SEM_SIM_NO_LIVRO`**: intocado, continua a reprovar (teste e mutante M09).
- **MUDANÇA DECLARADA na contagem** (`:811`): `SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA` era só o item que
  pousou nas duas corridas pelo `item_id`. Agora = **pousou nas duas + fundido por item + fundido por
  documento**, e as três parcelas vão em `SALA_JA_NA_SALA_PARCELAS`. Incluí também a fusão por item (a missão
  pedia a por documento): era o mesmo ponto cego — a Sala já barrava o item repetido desde `f2d5217b` e a
  contagem nunca o via. `SALA_DUPLICADOS_EXEMPLOS` passa a listar os fundidos também.

`onda_web.py` **não mudou**: continua a parar em `C6_BYPASS` quando `C6_ZERO_BYPASS.PASSA is False`.

## EVIDÊNCIA

### 1 · Testes novos — `tests/test_c6_repetido.py` (14)

Banco falso que **faz as junções** do SQL (raw por fonte+chave, Sala pelo raw, outra corrida) e **não**
filtra identidade nem universo.

```
$ python3 -m unittest tests.test_c6_repetido
Ran 14 tests in 0.036s
OK
```

| teste | resultado |
|---|---|
| `test_caso_real_58_1243_mesmo_documento_passa` | PASS · `FUNDIDO_POR_DOCUMENTO=["derived:1243->derived:58"]`, prova: raw 2375 → raw 166, T5, `IT-T5-025`, `IT-T5-025:URL:it/news/progetto-innoflorenerg` |
| `test_a_contagem_ja_na_sala_passa_a_ver_a_fusao_por_documento` | `SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA=1` (era 0) |
| `test_mesmo_documento_outro_universo_reprova` | FAIL do C6 · `MESMO_DOCUMENTO_OUTRO_UNIVERSO (livro T7, Sala T5)` |
| `test_decisao_sem_universo_nao_funde` | FAIL do C6 |
| `test_raw_do_item_sem_identidade_provada_reprova` / `…_com_identidade_nula_reprova` | FAIL do C6 · `IDENTIDADE_NAO_PROVADA` |
| `test_raw_da_linha_da_sala_sem_identidade_provada_reprova` | FAIL do C6 |
| `test_sim_que_simplesmente_nao_pousou_reprova` | FAIL do C6 · `NAO_POUSOU` |
| `test_mesmo_documento_so_na_mesma_corrida_nao_e_fusao_de_outra_corrida` | FAIL do C6 |
| `test_sala_sem_sim_no_livro_continua_a_reprovar_mesmo_com_fusao` | FAIL do C6 (e a fusão continua listada) |
| `test_fundido_por_item_noutra_corrida_passa` / `test_mesmo_item_outro_universo_reprova` | PASS / FAIL |
| `test_so_select_e_o_run_id_passa_pela_forma` / `test_sem_sim_fora_nao_pergunta_nada_a_mais` | 2 perguntas, `select`, sem `;`; run_id com aspas → `ValueError`; sem SIM fora → 0 perguntas |

`tests/test_micro_coleta_instrumento.py`: o banco falso ganhou resposta vazia às duas perguntas novas (2 linhas);
nenhuma asserção mudou.

### 2 · O SQL novo contra o ESQUEMA REAL — `provas/c6_repetido/prova_sql_c6.py`

Postgres 16 descartável (`initdb` em pasta temporária), **34 migrations** pela cadeia canónica, pouso pela porta
real da Sala (`espera.pousar`, a DEDUP-DOC de verdade), `relatorio` com a consulta real (`MC.sql`, psql,
`default_transaction_read_only=on`). Saída inteira em `provas/c6_repetido/PROVA-SQL-C6.json`.

```
$ su postgres -c "python3 provas/c6_repetido/prova_sql_c6.py --pg-bin /usr/lib/postgresql/16/bin --saida -"
rc=0
REAL_58_1243               True  ['derived:2->derived:1'] {}                                            JA_NA_SALA=1
MESMO_DOC_OUTRO_UNIVERSO   False []  {'derived:4': 'MESMO_DOCUMENTO_OUTRO_UNIVERSO (livro T7, Sala T5)'} 0
RAW_NAO_FORWARD_IDENTIFIED False []  {'derived:5': 'NAO_POUSOU'}                                        0
SIM_NAO_POUSOU             False []  {'derived:6': 'NAO_POUSOU'}                                        0
MIGRATIONS {'CODIGO': 0, 'PASS': 34}
POUSOS R20 PASSED INSERIDAS 1 · R28 REUSED INSERIDAS 0 JA_NA_SALA_POR_OUTRA_CORRIDA 1
NAO_PROVADO_COM_CHAVE  RECUSADO_PELO_ESQUEMA forward_sem_prova_nao_finge_chave
VEREDITO PASS
```

(Na base descartável os ids nascem 1, 2, …: `derived:1` faz o papel de `derived:58`, `derived:2` o de `derived:1243`.)

### 3 · Mutação — `provas/c6_repetido/mutacao_c6.py` sobre `59199ff3`

Cópia por `git archive`; um mutante morre se um teste que passava na cópia limpa passa a falhar.
Saída em `provas/c6_repetido/MUTACAO-C6.json`.

| mutante | estado |
|---|---|
| M01 tirar `FORWARD_IDENTIFIED` do bruto do item | MORTO |
| M02 tirar `FORWARD_IDENTIFIED` da linha da Sala | MORTO |
| M03 tirar «mesmo universo» da fusão por documento | MORTO |
| M04 tirar «mesmo universo» da fusão por item | MORTO |
| M05 fusão por documento não tira do FORA | MORTO |
| M06 fusão por item não tira do FORA | MORTO |
| M07 contagem sem a fusão por documento | MORTO |
| M08 todo SIM que não pousou conta como fundido | MORTO |
| M09 `SALA_SEM_SIM_NO_LIVRO` deixa de reprovar | MORTO |
| M10 a prova aponta para o próprio item | MORTO |

**PLACAR 10/10.**

### 4 · Bateria por nome — `provas/int_r7/bateria_por_nome.py`, rede fechada, 3 trabalhadores, worktrees limpas

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `e24139702` | 332 | 7507 | 125 |
| depois `59199ff3` (código, **antes** de regerar o mapa) | 333 | 7521 | 126 |

```
$ python3 provas/int_r7/bateria_por_nome.py --comparar BATERIA-BASE-e2413970.json BATERIA-DEPOIS-59199ff3.json
ANTES   modulos=332 testes=7507 falhas=125
DEPOIS  modulos=333 testes=7521 falhas=126
NOVAS   1 ['test_o_controle_separa_lei_de_mencao.test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore']
SUMIDAS 0 []
MODULOS_SUMIDOS [] · MÓDULOS NOVOS ['test_c6_repetido'] · MÓDULOS COM MENOS TESTES [] 
```

**Sumidos: 0** (nenhum módulo sumiu, nenhum módulo corre menos testes; +14 = os do `test_c6_repetido`).
A **única nova** é o `M5_o_ponto_fixo…`, que chama `impressao_da_arvore.py --conferir-carimbo`: o código mudou e o
mapa ainda não tinha sido regerado — é o portão a fazer o seu trabalho, não uma regressão. Re-medido **depois** de
regerar pela cadeia, no commit final (ver o relato desse commit). As 2 falhas de `test_micro_coleta_instrumento`
(`test_fica_fora_da_3b…`, `test_relatorio_e_dados_da_3b…`) já estavam na base e continuam iguais.
Ficheiros: `provas/c6_repetido/BATERIA-BASE-e2413970.json`, `BATERIA-DEPOIS-59199ff3.json`.

## PROBLEMA

1. **A coleta contínua parou por um falso alarme.** O C6 perguntava «o SIM está na Sala?» só pelo `item_id`
   desta corrida. A Sala, desde a DEDUP-DOC (25/09), responde «já está?» também pelo DOCUMENTO — e
   fundiu `derived:1243` com `derived:58` corretamente. O C6 viu um SIM «perdido» e o disjuntor desligou a onda.
2. **A contagem mentia para baixo.** `SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA = 0` no relatório da passagem,
   com um item fundido. Agora conta, com as parcelas à vista.

## O QUE NÃO SEI

- **Não medi a Sala real.** O caso 58/1243 foi **reconstruído** com os números do coordenador (raw 2375, 166, 299;
  `IT-T5-025:URL:it/news/progetto-innoflorenerg`; T5; 20/09). Não vi as linhas reais. Depois de instalar, o
  primeiro relatório da passagem do ciclo 26 é que prova: esperado `C6_ZERO_BYPASS = PASS`,
  `FUNDIDO_POR_DOCUMENTO = ["derived:1243->derived:58"]`.
- **Fusão DENTRO da mesma corrida não é reconhecida** (3.º `not exists` do SQL da Sala: dois brutos do mesmo
  documento na mesma entrada → só o primeiro pousa). A missão pediu «noutra corrida»; esse SIM continua a
  reprovar o C6 como hoje (`test_mesmo_documento_so_na_mesma_corrida…`). Se acontecer, a onda para de novo em
  `C6_BYPASS` — seria outro falso alarme, a decidir pelo dono.
- **Bruto não provado com chave**: o esquema real já o recusa (`forward_sem_prova_nao_finge_chave`, medido na
  prova 2). `LEGACY_PRE_IDEMPOTENCY` com chave só existe abaixo do corte da 026 e não se fabrica num teste; o
  código exige `FORWARD_IDENTIFIED` literal dos dois lados, por isso um legado **não** funde — provado só
  pelo banco falso.
- **Universo vem do livro** (`universo` da decisão). Decisão sem `universo` → não funde (reprova). Se o livro
  real tiver decisões SIM antigas sem esse campo, elas continuam a reprovar.
- O custo das duas perguntas novas na Sala real não foi medido (só correm quando há SIM fora; junção por
  `source_id`/`document_key` e `raw_observation_id`, que a Sala já usa no pouso).

## EM PALAVRAS SIMPLES

A coleta parou porque o conferente achou que uma notícia aprovada tinha sumido.
Na verdade a Sala já tinha a mesma notícia desde 20/09 e, certo, não a guardou duas vezes.
Agora o conferente sabe disso e só grita quando uma notícia aprovada some de verdade.
