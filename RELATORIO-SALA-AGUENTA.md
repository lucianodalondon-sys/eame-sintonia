# SALA-AGUENTA · a Sala de Espera aguenta a 2.ª onda? — 25/09/2026

Branch `sala-aguenta-v1`, a partir da produção `servico-20260923-0923 @ 5ba9647e`. **NÃO instalado.**
Sem rede de coleta. Postgres descartável local (`orca/pgtmp`, peça `Bancada` de
`provas/a_porta_cli_liga_o_banco.py`), desligado e apagado depois de cada corrida
(`PORTO_VIVO=False, CLUSTER_SOBROU=False`).

## Em palavras simples

O vermelho não era a Sala a perder dados: era a prova da Sala **impedida de começar**. O workflow
dá-lhe um banco chamado `sala`, e a trava de segurança (que só deixa escrever em bancos com nomes
de uma lista curta) não tinha esse nome. A prova recusava-se, saía com código 2, e o job ficava
vermelho sem medir nada. Com o nome na lista, a prova corre inteira e passa: **91 de 91 casos,
30 ataques, 0 sobreviventes**. E uma onda de 60 itens (com repetição, onda seguinte e processo
morto a meio) deu **0 duplicados e 0 perdas**.

## 0 · Qual é o teste

A missão chama-lhe «c10_4b». O `tests/test_c10_4b_um_caminho_so.py` é outra coisa (o caminho único
da transcrição de Reels do Instagram) e está **verde** na base (`_bateria_BASE.json`). O vermelho da
Sala é o **passo 2b5 do `banco-descartavel.yml`** — «a sala de espera sobrevive ao processo que a
escreveu» (`provas/a_sala_sobrevive_ao_processo.py`), registado no HANDOFF (24/09 03:00) como
«falha em TODAS as branches desde 13/09 (último sucesso feb635e2 13/09) — herdado».

## 1 · O erro e a linha

Corrido na produção 5ba9647e, como no workflow (banco próprio `sala`):

```
RC 2
RECUSADO: o endereco nao prova ser descartavel (banco fora da lista descartavel). Esta prova ESCREVE.
```

- `provas/a_sala_sobrevive_ao_processo.py:79-84` → `guarda/banco_descartavel.porque_nao_e_descartavel`
- `guarda/banco_descartavel.py:113` → `if banco not in BANCOS_PERMITIDOS: return "banco fora da lista descartavel"`
- `BANCOS_PERMITIDOS = ("descartavel", "derivado", "social", "objeto")` — sem `sala`.

## 2 · Classificação: **(B) teste/configuração desatualizados por decisão já tomada**

| data | commit | o que aconteceu |
|---|---|---|
| 13/09 | feb635e2 | último verde do job — **o passo 2b5 ainda não existia** |
| 14/09 | caaf6311 | nasce o passo 2b5, com `create database sala;` |
| 17/09 | 497093a7 | a trava passa a ter UM dono (`guarda/banco_descartavel.py`) com lista de PERMISSÃO; `derivado`, `social` e `objeto` (os bancos próprios dos outros passos) estão lá — **`sala` não** |

De 17/09 até hoje a causa está **provada** (a recusa acima, reproduzida). Entre 14/09 e 17/09 o job
já podia estar vermelho por outra causa (houve consertos nessas datas: `e087d985` o texto por stdin
em UTF-8, `f8447492` a DSN no fim) — **NÃO SEI**: exigiria os logs do CI.

**Não é (A):** com um nome permitido, na mesma árvore, a prova corre inteira e passa:

```
CASOS=91 · PASS=91 · FAIL=0
RED_TEAM_ATTACKS=30 · RED_TEAM_SURVIVORS=0
SALA_SOBREVIVE_AO_PROCESSO=PASS
```

Entre os casos: `READY_PERSISTS_AFTER_PROCESS_EXIT / NEW_PROCESS / BACKEND_RECONNECT`,
`SAME_RUN_SAME_READY = REUSED`, «o retry não duplicou», crash antes do commit = `PARTIAL_INVISIBLE`,
crash depois do commit = a linha fica e o retry reencontra-a, dois writers ao mesmo tempo:
`DUPLICATES = 0`, `SILENT_CONFLICTS = 0`, `DIRTY_READS = 0`, `CROSS_RUN_CONTAMINATION = 0`.

**Não é (C) puro:** o ambiente não mudou; mudou a trava e o workflow não acompanhou.

## 3 · Risco para a 2.ª onda — medido com 60 itens (1.ª onda: Sala 66 → 69)

Postgres descartável novo; READY feito pelo DONO do contrato (`admissao.pronto_para_inteligencia`),
pousado pela porta real (`sala_de_espera.pousar`):

| cena | estado | linhas |
|---|---|---|
| 60 itens de uma vez | PASSED (0,49 s) | 60 |
| a MESMA corrida repete o lote | REUSED | 60 |
| corrida NOVA vê os mesmos 60 documentos (onda seguinte) | REUSED | 60 · chaves (item, universo) repetidas = 0 |
| processo morto depois de pousar 30; a corrida é refeita | REUSED | 90 (as 30 já estavam; 0 duplicadas) |
| final | — | **90 = esperado 90**, 0 repetidas |

O caminho que o 2b5 guarda (`sala_de_espera.pousar` no backend POSTGRES) **é o que a onda exerce**
a cada documento admitido. Idempotência medida: mesmo item 2× = 1 registo, também entre corridas.

## 4 · O conserto (mínimo, declarado) — NÃO instalado

| ficheiro | muda |
|---|---|
| `guarda/banco_descartavel.py` | `BANCOS_PERMITIDOS` ganha `sala` (comentário datado: o 2b5, a 497093a7, o padrão de `derivado`/`social`/`objeto`) |
| `tests/test_persistencia_operacional.py` | a lista exacta passa a ter `sala` — mudança DECLARADA na docstring; `sala_italia` continua fora (teste ao lado) |
| `tests/test_a_porta_cli_liga_o_banco.py` | teto 4 → 5, declarado; `sala_italia` entra na lista de proibidos |
| `tests/test_preservar_coleta_no_banco.py` | teto 4 → 5, declarado; `sala_italia` entra na lista de proibidos |
| `tests/test_os_bancos_do_workflow_passam_a_trava.py` (novo, 5) | cada `create database X` e cada `BANCO_DESCARTAVEL_URL` do workflow tem de passar a trava; `sala_italia`/`salas`/`sala2`/remota continuam fora — é o teste que teria apanhado isto a 17/09 |

- O nome compara-se **inteiro** e o host tem de ser **local**: a Sala operacional desta máquina
  (`54330/sala_italia`) e qualquer banco remoto continuam recusados.
- **Depois do conserto, o 2b5 exactamente como o workflow (banco `sala`): 91/91 PASS.**
- Testes: novo 5/5; `test_persistencia_operacional` 14/14; `test_preservar_coleta_no_banco` e
  `test_a_porta_cli_liga_o_banco` com os **mesmos 2 vermelhos de base, por nome** (antes e depois):
  `test_o_raw_tem_um_caller_e_e_a_porta_canonica` (separador `\` do Windows) e
  `test_a_porta_cli_escreve_no_banco_descartavel` (prova CLI contra Postgres real, rc 1 na base).
  **NEW_FAILURES_BY_NAME = 0** nestes ficheiros.
- **Mutação 3/3 mortos** (cópias isoladas): tirar `sala` da lista; meter `sala_italia`; comparar o nome
  por prefixo.

## Plano de instalação (o coordenador instala)

1. Juntar `sala-aguenta-v1` na linha instalada (conflito esperado só nos `*.generated.json` → regerar
   pela cadeia).
2. Correr o job `postgres-descartavel` do `banco-descartavel.yml`: o passo 2b5 deve ficar verde
   (`SALA_SOBREVIVE_AO_PROCESSO=PASS`); se ficar vermelho por outra linha, é a causa de 14–17/09 que
   aqui ficou NÃO SEI.
3. Rollback: reverter o commit (só a lista e os testes mudam; nenhum dado).

## Fora do âmbito, visto

Dois Postgres descartáveis de OUTRA sessão continuavam vivos (`ytmd-copia`, `ytmd-prova2`, 01:50 e
01:58, missão YT-METADADOS). Não lhes toquei.

Provas fora do Git, com sha256: `C:/Users/London1/auditoria-madrugada/SALA-AGUENTA-PROVAS-SHA256.txt`.
