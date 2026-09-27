# RUNBOOK-R7 — a rodada 7 das capacidades numa CÓPIA local da Sala

> **EXPERIMENTAL · NAO_PARA_CLIENTE.** Quem roda é o **coordenador**, na máquina dele, contra uma
> **CÓPIA** da Sala. Nunca a Sala canônica, nunca `SUPABASE_DB_URL`. A leitura é **só leitura**, com
> duas travas; o motor não abre banco nenhum (ele lê um arquivo).

```
MOTOR       motor/motor_das_capacidades.py        (CAP-WIN + CAP-SCI numa corrida G0/v4, regras D112)
EXPORT      motor/r7_export_da_copia.sql          (vista sala_de_espera_atual + raw_asset, read-only)
POTE        pacote/pote_intelligence_casco.py @ ce775ff5  (claude/intelligence-bridge-v2-7mngha)
PROVA E2E   provas/int_r7/export_numa_copia_descartavel.py  → provas/int_r7/E2E-COPIA-DESCARTAVEL.json
```

## 0 · Antes de começar

- Python 3 (`py` no Windows), `psql` (o mesmo que a Sala usa) e `git`.
- A árvore deste ramo, atualizada; e o commit do gerador do pote no clone:
  `git fetch origin claude/intelligence-bridge-v2-7mngha` (sem ele, o passo 4 responde **NAO SEI**, código 4).
- Uma **cópia** da Sala num Postgres local (restaurada de `backup_sala.cmd` / `pg_dump -Fc`, como no
  ensaio da 033). Chame o endereço dela de `SINTONIA_SALA_COPIA_DSN`.

## 1 · Confirmar que é a CÓPIA (e não a Sala)

```powershell
$env:SINTONIA_SALA_COPIA_DSN = "postgresql://postgres@127.0.0.1:<PORTA_DA_COPIA>/sala_italia"
psql -X -A -t -c "select current_database(), inet_server_port()" "$env:SINTONIA_SALA_COPIA_DSN"
```

Se a porta for a da Sala real (`54330` no ensaio da 033) ou o endereço for o da nuvem: **pare**.
Não use `SUPABASE_DB_URL` em nenhum passo deste runbook.

## 2 · Exportar a cópia — transação READ ONLY (duas travas)

Windows (PowerShell), a partir da raiz do repositório:

```powershell
New-Item -ItemType Directory -Force C:\tmp\r7 | Out-Null
$env:PGOPTIONS = "-c default_transaction_read_only=on -c standard_conforming_strings=on"
$env:PGCLIENTENCODING = "UTF8"
psql -X -q -A -t -v ON_ERROR_STOP=1 -c "begin transaction read only" -f motor\r7_export_da_copia.sql -c "commit" -o C:\tmp\r7\sala-r7.json "$env:SINTONIA_SALA_COPIA_DSN"
Remove-Item Env:PGOPTIONS
```

bash (mesmo comando):

```bash
mkdir -p /tmp/r7
PGOPTIONS="-c default_transaction_read_only=on -c standard_conforming_strings=on" PGCLIENTENCODING=UTF8 \
psql -X -q -A -t -v ON_ERROR_STOP=1 -c "begin transaction read only" -f motor/r7_export_da_copia.sql -c "commit" \
     -o /tmp/r7/sala-r7.json "$SINTONIA_SALA_COPIA_DSN"
```

- **Opções primeiro, DSN por último** (o `getopt` do Windows não permuta; ver `admissao/sala_de_espera.py`).
- `-o` e não `>`: o redirecionamento do PowerShell grava UTF-16.
- O arquivo traz `"READ_ONLY": "on"` — é o próprio banco dizendo que a transação era só de leitura.
  Se vier `off`, **não use o export**.
- Travas provadas num Postgres descartável com o esquema real (migrations 001..033): a mesma sessão
  **recusa** um `INSERT` (`cannot execute INSERT in a read-only transaction`) —
  `provas/int_r7/E2E-COPIA-DESCARTAVEL.json`, passo 4.

## 3 · Rodar o motor (uma corrida, duas capacidades)

```powershell
py motor\motor_das_capacidades.py C:\tmp\r7\sala-r7.json --hoje 2026-09-27 --source-head (git rev-parse HEAD) --saida C:\tmp\r7\MOTOR-R7.json
```

- `--hoje` é o «agora» declarado (a CAP-WIN nunca lê o relógio escondido). Use o dia da rodada.
- `--source-head` é o commit da árvore que roda o motor; sem ele sai `NAO SEI` à vista.
- A linha final (stderr) resume: `corrida IR-… · objetos {…} · nao enviados N · requisitos N`.

## 4 · Passar pelo gerador do pote v2

Enquanto o pote não estiver instalado neste ramo (outra equipe o unifica em `nuvem-pote-v2-unico-v1`),
o gerador de **verdade** roda direto do commit `ce775ff5`, sem cópia:

```powershell
py provas\int_r7\aceite_pelo_gerador.py C:\tmp\r7\MOTOR-R7.json C:\tmp\r7\POTE-R7.json
```

Quando o pote estiver instalado, o comando do próprio pote (POTE-UNICO.md §3) aceita o mesmo arquivo:

```powershell
py pacote\pote_intelligence_casco.py C:\tmp\r7\MOTOR-R7.json italia-portale\client\sintonia-pote.js
```

## 5 · O que cada capacidade deve devolver — fixture SINTÉTICA ARIF/APOL + estudos

A fixture é `tests/dados/int-r7/SINTETICO-R7-SALA-EXPORT.json` (**SINTÉTICA**: frases curtas do desenho
CAP-WIN R5, alteradas de propósito; o limite 10% do ARIF, a mudança de recomendação e o Gargano DEDUZIDO
são **inventados** para provar a D112). Ensaio antes da cópia real:

```powershell
py motor\motor_das_capacidades.py tests\dados\int-r7\SINTETICO-R7-SALA-EXPORT.json --hoje 2026-09-27 --source-head SINT --saida C:\tmp\r7\MOTOR-FIXTURE.json
```

**CAP-WIN — mosca-da-oliveira (olivo × Bactrocera oleae × Puglia)** — `tests.test_motor_das_capacidades` R1

| campo | tem de sair |
|---|---|
| WINDOW_DEFINED / tipo | YES · `THRESHOLD_WINDOW` |
| WINDOW_OPEN_NOW | `NO` · método `FONTE_DECLARA_SOGLIA_NAO_ATINGIDA` |
| estado temporal | `CURRENT` (hoje 27/09, fatos até 20/09, N=30 herdado do V21) |
| apoios | observação: 2 redes provadas (APOL, ARIF); regra conta **1** |
| resultado | **`NO_DEFENSIBLE_ACTION_YET`** — «monitorizar; a condição de intervenção não está satisfeita e a fonte declara que o tratamento não se justifica» |
| oportunidades | nenhuma |
| ARIF 38 Gargano (região `DA_FONTE`, subárea `DEDUZIDO`) | `NOT_POSSIBLE` + requisito `REGION_EM_CAMPO` (D112a) |

**D112 — relações no mesmo par**

| relação | tem de sair |
|---|---|
| `MESMA_REDACAO` | APOL (IT-T3-010): BR, LE, TA → **3 aplicações / 1 instituição** (conta como 1 apoio) |
| `DIVERGENT` | 4-5% (APOL) × 10% (ARIF) → contradição **UNRESOLVED**; o sistema não escolhe |
| `TEMPORAL_CHANGE` | ARIF 37 («non si ritiene giustificato») → ARIF 38 («intensificare il monitoraggio») — **não prova mudança no campo** |

**CAP-SCI — estudos** — `tests.test_motor_das_capacidades` R2 (estudo **nunca** vira incidência de campo:
nenhum estudo entra numa janela, e o portão da saída reprova se entrar)

| estudo | espécie | força | aplicabilidade | leitura |
|---|---|---|---|---|
| EST-01 (ensaio randomizado, n=8, Puglia ESCRITO, 2023) | `SCIENTIFIC_RESULT` | `FORTE` | `COMPLETA` | `SUSTENTA_EFEITO_NESTAS_CONDICOES` |
| EST-02 (mesmo ensaio, n=3, local = afiliação `DA_FONTE`) | `SCIENTIFIC_RESULT` | `INDICATIVA` | `PARCIAL` (falta LOCAL) | `INDICIO_A_CONFIRMAR` |
| EST-03 (monitoramento, resistência, sem local) | `RESISTANCE` | `FRACA` | `PARCIAL` (falta LOCAL) | `RESISTENCIA_OBSERVADA_LOCAL_OU_PERIODO_NAO_PROVADO` |

Independência: EST-01 e EST-02 são o mesmo ensaio → **2 grupos (teto), não 3**. Replicação: nenhuma
afirmação replicada (declarado). Ligação ADAMA: nenhuma (`UNKNOWN_MOLECULA`/`UNKNOWN_REFERENCIA`).

**No pote v2:** `windows` 1 · `science` 2 · `future` 1 · `sources` 3; **1 recusado à vista**: EST-02
(`PROVA_INCOMPLETA — falta DOCUMENT_ID`: o RAW dele não tem `document_key`, e o motor não cunha).

## 6 · O contrato de saída (declarado)

`MOTOR_DAS_CAPACIDADES/v1` = o contrato de **entrada** do gerador `ce775ff5` (`adaptar()`), mais o que é
do motor:

```
INTELLIGENCE_RUN_ID   primeira chave (um pote é de UMA corrida)
SCHEMA · CONTRATO_DE_SAIDA_PARA · MARCA · SOURCE_HEAD · CORTE · RESULT_STATE · SINTETICA · HOJE
LINEAGE               a da corrida G0/v4, verbatim (o pote confere a prova contra ela)
SIGNALS []            os sinais ficam no livro (CORRIDA.SIGNALS): o pote recusaria sinal sem ferramenta
GAPS [] · REQUIREMENTS  CAP-WIN (FERRAMENTA=windows) + corrida
ITENS_POR_FERRAMENTA  windows · science · future · sources
  objeto  OBJETO_ID · ESPECIE (SINAL | FATO_PRESENTE_SOBRE_O_FUTURO | RENDIMENTO_DE_FONTE)
          ESTADO EXPERIMENTAL_CANDIDATE · CHAVES (as do pote + ENTITY_SOURCE, DA_FONTE,
          INTERPRETACAO_DO_SISTEMA, ESPECIE_DO_MOTOR → o pote as leva em FORA_DO_CONTRATO)
          PORQUE · CONTRADIZ · INCERTEZA
          PROVA [ ITEM_ID · CORRIDA_UPSTREAM · RAW_OBSERVATION_ID · SOURCE_ID · DOCUMENT_ID (raw_asset)
                  URL (raw_asset.source_url) · PUBLICADO_EM = PUBLISHED_AT (o mesmo campo do READY)
                  COLHIDO_EM (CAPTURED_AT) · FACT_TIME (o da corrida; nunca a publicação) ]
NAO_ENVIADOS_AO_POTE · TRIAGEM · D112 {REGRAS, LUGAR, RELACOES} · CAP_WIN · CAP_SCI · CORRIDA
```

- **Espécie:** o pote v2 não tem espécie para `ANALYTIC_JUDGMENT`. O juízo das capacidades viaja como
  `SINAL` (a única que não promete mais do que o juízo é) e a espécie do motor vai em
  `ESPECIE_DO_MOTOR`. Espécie nova é decisão do **dono do pote**.
- **`PUBLISHED_AT`:** o pote chama o campo `PUBLICADO_EM`; o motor escreve os dois com o **mesmo** valor
  (o portão da saída reprova se divergirem). O pote leva adiante só `PUBLICADO_EM`.
- **Prova só com `G0 = PASSOU`** (regra do pote, herdada da ponte v1): evidência de janela sem tempo
  fica em `EVIDENCIA_SEM_G0_FORA_DA_PROVA`, à vista.

## 7 · O que fica NÃO SEI

- **D112 não está escrita no repositório**: o texto aplicado é o verbatim da missão INT-R7-CAPS
  (`motor/motor_das_capacidades.py`, `D112`).
- «Sustentação explícita» = a origem do valor é `ESCRITO` ou `CITADO` (`leis/lugar_do_fato.py`). Se a
  Collection real não preenche `VEIO_DE` / `FACT_LOCATION_VEIO_DE`, **todo** lugar sai NAO SEI e toda
  janela vira `NOT_POSSIBLE` + `REGION_EM_CAMPO` — é a resposta certa, não defeito. Quantos preenchem na
  cópia real: **NAO SEI** até a rodada.
- Instituição = `SOURCE_ID`. Duas SOURCE_ID da mesma instituição contariam duas: NAO SEI até a Collection
  declarar.
- `PROBLEMA` e `SUBAREA` em `janela_declarada` continuam **propostos** (CAP-WIN.md).
- O pote real (`nuvem-pote-v2-unico-v1`) pode mudar o contrato; esta saída segue **ce775ff5**.
