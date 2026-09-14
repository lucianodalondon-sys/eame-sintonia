# EMENDA CONSTITUCIONAL V1.1 → V1.2 — apêndice G da Bíblia

**Data:** 2026-09-08 · **HEAD antes:** `73e7270` · **Ramo:** `claude/biblia-canonica-da-coleta`

> A COL-LAW-069 manda que nenhuma lei mude em silêncio. Este ficheiro é o registro da
> emenda, e o censo que a sustenta é o
> [apêndice F](CENSO-DA-INFRAESTRUTURA.md) — medido **antes** de qualquer lei ser escrita.

```
VERSION BEFORE   V1.1    78 leis
VERSION AFTER    V1.2   100 leis   (+22)
LEIS APAGADAS    0
LEIS RENUMERADAS 0
```

---

## AS DUAS PARTES NOVAS

| # | nome | parte | leis |
|---|---|---|---|
| **1** | **A INFRAESTRUTURA** — GitHub e Supabase ganham papel canônico | PARTE XVIII | `COL-LAW-301` … `316` (16) |
| **2** | **O PLANO DE REFERÊNCIA** — o contexto estável ganha nome | PARTE XIX | `COL-LAW-401` … `406` (6) |

`3xx` é a infraestrutura; `4xx` é a referência. Nenhum número anterior mudou.

---

## AS 16 LEIS DA INFRAESTRUTURA

| LAW_ID | nome | ORIGEM | IT |
|---|---|---|---|
| `COL-LAW-301` | Infraestrutura não é autoridade semântica | `ARCHITECTURAL_DECISION` | `IMPLEMENTED` |
| `COL-LAW-302` | O GitHub guarda a engenharia | `EXISTING_SINTONIA_LAW` | `IMPLEMENTED` |
| `COL-LAW-303` | O GitHub não é banco operacional | `ENGINEERING_PRINCIPLE` | `ABSENT` |
| `COL-LAW-304` | O Supabase é a memória operacional | `ARCHITECTURAL_DECISION` | `PARTIAL` |
| `COL-LAW-305` | O Supabase guarda; não julga | `ARCHITECTURAL_DECISION` | `IMPLEMENTED` |
| `COL-LAW-306` | Ninguém escreve no canônico por conhecer a tabela | `EXISTING_SINTONIA_LAW` | `IMPLEMENTED` |
| `COL-LAW-307` | A corrida se liga à engenharia que a produziu | `CONSOLIDATED_FROM_MULTIPLE` | `PARTIAL` |
| `COL-LAW-308` | Migration versionada, e ficheiro não é estado aplicado | `EXISTING_SINTONIA_LAW` | `IMPLEMENTED` |
| `COL-LAW-309` | O GitHub Actions é execução, não orquestrador | `ARCHITECTURAL_DECISION` | `IMPLEMENTED` |
| `COL-LAW-310` | Agenda não é política de coleta | `CONSOLIDATED_FROM_MULTIPLE` | `IMPLEMENTED` |
| `COL-LAW-311` | Bytes não são metadata | `EXISTING_SINTONIA_LAW` | `PARTIAL` |
| `COL-LAW-312` | Segredo não atravessa | `EXISTING_SINTONIA_LAW` | `IMPLEMENTED` |
| `COL-LAW-313` | Ambiente faz parte da identidade da corrida | `ENGINEERING_PRINCIPLE` | `NOT_APPLICABLE` |
| `COL-LAW-314` | Deploy não decide qual dado é verdade | `ARCHITECTURAL_DECISION` | `IMPLEMENTED` |
| `COL-LAW-315` | Conceito não é implementação física | `ENGINEERING_PRINCIPLE` | `IMPLEMENTED` |
| `COL-LAW-316` | O mapa mostra responsabilidade, não schema | `ARCHITECTURAL_DECISION` | `PARTIAL` |

## AS 6 LEIS DO PLANO DE REFERÊNCIA

| LAW_ID | nome | ORIGEM | IT |
|---|---|---|---|
| `COL-LAW-401` | Dado de referência não é configuração | `ENGINEERING_PRINCIPLE` | `ABSENT` |
| `COL-LAW-402` | Abastecer referência também é coleta | `ARCHITECTURAL_DECISION` | `ABSENT` |
| `COL-LAW-403` | Toda referência declara a sua autoridade | `ENGINEERING_PRINCIPLE` | `ABSENT` |
| `COL-LAW-404` | Conferir não é mudar | `CONSOLIDATED_FROM_MULTIPLE` | `ABSENT` |
| `COL-LAW-405` | A referência tem história | `ENGINEERING_PRINCIPLE` | `ABSENT` |
| `COL-LAW-406` | A definição é da engenharia; os registros são da memória | `ARCHITECTURAL_DECISION` | `ABSENT` |

**Todo o Plano de Referência é `ABSENT`, e isso é a medição, não pessimismo:** não existe
tabela de referência, política de atualização nem dono declarado. É `TARGET` inteiro.

---

## AS DUAS SURPRESAS DA MEDIÇÃO

> A missão mandava procurar produtores escrevendo direto no Supabase, e tratar isso como o
> problema. **A medição encontrou o contrário.**

### 1 · Bypass para dentro do Supabase: **ZERO**

7 caminhos de escrita medidos, **7 canônicos**. O padrão da casa é:

```
artefato → gerador → .sql VERSIONADO → GitHub Actions (que tem o segredo) → Supabase
```

E não é disciplina: é **arquitetura acidental que deu certo**. A credencial só existe como
segredo do runner, então ninguém *consegue* escrever direto. A COL-LAW-306 escreve como lei
o que a casa já fazia por necessidade.

### 2 · O bypass real é ao contrário — para dentro do **Git**

`coleta/italy_recurrent_collect.mjs:144` grava recibo, 144 observações **e 12 MB de bytes**
em `data/collection-ledger` e `data/collection-store`, enquanto `collection_run`,
`raw_asset` e o bucket `raw` existem, estão provados por round-trip, e ficam vazios.

É a fratura da **C-002** vista pela infraestrutura: **duas memórias operacionais para a
mesma pergunta.** A espanhola é o banco; a italiana é o Git.

**Registrado como G-30. Não corrigido:** missão constitucional.

---

## O QUE NÃO VIROU LEI NOVA — 4 emendas absorvidas

| emenda do briefing | absorvida por | por quê |
|---|---|---|
| Supabase Storage tratado separadamente | **COL-LAW-311** | «bytes ≠ metadata» já decide onde cada coisa mora; o bucket é a implementação de hoje, e a lei não decreta implementação |
| `SCHEMA REAL ≠ SCHEMA ESPERADO` como lei própria | **COL-LAW-308** | os três estados e o `INFRASTRUCTURE_DRIFT` cabem inteiros na lei da migration |
| System Map consumindo GitHub **e** Supabase | **COL-LAW-102** + **COL-LAW-111** | as quatro verdades já dizem de onde vem cada nível; a camada de observabilidade já é definida como normalizadora, não dona |
| `REFERENCE AS-OF` como lei própria | **COL-LAW-405** | é a consequência direta de `VALID_FROM`/`VALID_TO`; separá-la daria duas leis para uma ideia |

**Superseded:** nenhuma. **Nenhuma lei da V1 ou da V1.1 foi tocada.**

---

## O QUE NÃO FOI CRIADO — de propósito

Nenhuma tabela criada, alterada ou removida. Nenhuma migration. Nenhum bucket. Nenhum dado
movido. Nenhum byte migrado. Nenhum writer alterado. Nenhum workflow funcional tocado.
Nenhuma credencial lida ou escrita. Nenhuma integração instalada.

**E nenhuma caixa «GitHub» foi desenhada no System Map.** O motivo é a própria lei: cada peça
do mapa já vive no GitHub, e desenhar uma avenida para ele seria exatamente a seta inventada
que a COL-LAW-048 proíbe. O que o mapa passa a dizer é o **papel** — nas peças que
efetivamente são a infraestrutura.

---

## IMPACTO NA MATRIZ DA ITÁLIA

| | V1 | V1.1 | **V1.2** |
|---|---:|---:|---:|
| leis medidas | 48 | 78 | **100** |
| `IMPLEMENTED` | 21 | 24 | **34** |
| `PARTIAL` | 23 | 42 | **46** |
| `ABSENT` | 4 | 11 | **18** |
| `NOT_APPLICABLE` | 0 | 1 | **2** |
| `UNKNOWN` | 0 | 0 | **0** |

**`IMPLEMENTED` subiu 10 de uma vez** — e não porque alguém programou hoje. É a infraestrutura
que **já estava certa e não tinha lei que a reconhecesse**: o SQL auditável antes de correr,
o segredo que só existe no runner, o pré-voo da migration, a varredura de credencial no que
é publicado.

> **Escrever a lei depois de medir tem este efeito: parte do trabalho já estava feito, e
> ninguém sabia dizer que estava.**
