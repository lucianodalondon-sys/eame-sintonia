# CAP-SCI — A CAPACIDADE CIENTÍFICA MÍNIMA DA INTELLIGENCE

```text
MISSAO      CAP-SCI (Bíblia §34 CAP-SCI · INT-LAW-070..077/102 · mapa do dono §35)
BASE        motor G0/v4 (a5db06c4) + insumos 0d39f27
CODIGO      motor/capacidade_cientifica.py            (peça C-INT-CAP-SCI, Z-MOTOR)
TESTES      tests/test_capacidade_cientifica.py        (49 testes)
FIXTURE     tests/dados/cap-sci/SINTETICO-ESTUDOS-CAP-SCI.json   SINTETICO: true
MUTACAO     provas/_mutantes_cap_sci.py                (peça C-PROVA-CAP-SCI-MUTACAO)
ESTADO      IMPLEMENTED · provado em fixture SINTÉTICA · NÃO corrido sobre os 100 da Sala
```

> **Não é biblioteca de papers.** A pergunta é a do dono (§35): *que conhecimento
> científico novo pode alterar uma decisão agronómica ou estratégica?* — com que
> força, aplicável a quê, replicado por quem.

## 1 · O que entra, e o que nunca entra

- Entra **só** o livro de uma corrida G0/v4 fechada (`DONE`/`REUSED`) e os itens
  que ela consumiu. Só é julgado o item cuja `LINEAGE` deixa disponível
  `LEITURA_ATEMPORAL_DE_CAPACIDADE`; o resto sai em `FORA` com o motivo
  (`capacidade_cientifica.py:696`).
- **Identidade só do READY.** Campo fora de `CAMPOS_READY` é **recusado**
  (`IDENTIDADE_DE_FORA_DO_READY`), não ignorado; item não `PRONTO` é recusado
  (`:209`). DOI, TRIAL, DATASET, cultura, problema, molécula, método, n,
  autores, instituições, espécie e resultado vêm **só** do envelope `FATO`
  (`:84`, `:234`); dois nomes da mesma chave que discordam ficam **conflito →
  NÃO SEI** (INT-LAW-084).
- **O TEXTO não é lido.** Título e resumo são para o humano; extrair deles
  seria cunhar facto (COL-LAW-202).
- **Local do estudo** = `FACT_LOCATION` com base (`:276`). Afiliação,
  `SOURCE_LOCATION` e país da revista nunca (INT-LAW-102, `:105`).
- **Período do estudo** = `FACT_TIME` com base e com ano (`:291`). Publicação
  nunca (INT-LAW-100).

## 2 · O julgamento por estudo (`julgar_estudo`, `:403`)

| eixo | regra |
|---|---|
| **FORÇA** (`:343`) | decomposta: DESENHO (vocabulário fechado `:131`) + N. Sem método → `NAO SEI` (não «fraca»). Sem n → no máximo `FRACA`. `n < 4` (`N_PEQUENO`, `:159`) → `INDICATIVA`. Revisão/meta-análise → `NAO_APLICAVEL` e fora da replicação (INT-LAW-072). |
| **APLICABILIDADE** | `CULTURA · PROBLEMA · MOLECULA · LOCAL · PERIODO`, cada um PROVADO ou não, e `FALTA` escrita. `COMPLETA` / `PARCIAL` / `TEMA_NAO_PROVADO`. |
| **ESPÉCIE** (`:118`) | a que o **estudo declara**: `SCIENTIFIC_RESULT`, `MODEL_RULE`, `RESISTANCE`. Não declarada → NÃO SEI, mesmo com «resistance» no texto. |
| **LEITURA** (`:181`, `:373`) | vocabulário fechado. Negativo forte → `NAO_DEMONSTROU_EFEITO_NESTAS_CONDICOES`; pequeno → `INDICIO_A_CONFIRMAR`; resistência sem local/período → `…_LOCAL_OU_PERIODO_NAO_PROVADO`. |

**Estudo pequeno nunca vira «o produto não funciona».** Essa leitura **não
existe** no vocabulário, e `_vigiar_leituras_proibidas` (`:758`) rebenta o livro
se `O_PRODUTO_NAO_FUNCIONA`, `MOLECULA_INEFICAZ` ou `RESISTENCIA_GENERALIZADA`
aparecerem em qualquer ponto. Todo estudo sai com
`NAO_E: INCIDENCIA_DE_CAMPO · RESULTADO_DO_PRODUTO · FINDING`.

## 3 · Independência e replicação (`:478`, `:535`)

- Por tema (cultura × problema). Dois estudos caem no **mesmo grupo** se
  partilham ENSAIO, DATASET (INT-LAW-073), AUTOR ou INSTITUIÇÃO. Mesmo DOI =
  mesma obra (INT-LAW-072).
- O número é um **TETO**, e diz-se. Estudo sem nenhuma chave vai para
  `SEM_CHAVE_DE_INDEPENDENCIA` e o piso fica **NÃO SEI** — nunca conta como
  grupo independente (INT-LAW-280: não inferir independência).
- Replicação por (tema × molécula × direção): `REPLICADO_EM_GRUPOS_DISTINTOS_TETO`
  só com ≥2 grupos **com chave**. Replicação ausente é **declarada**.
  Direções opostas → `CONTRADICAO_COM`, nunca «a maioria ganha».
- Na fixture: três papers de folpet, dois do mesmo ensaio → **2 grupos, não 3**.

## 4 · Ligação estudo → produto ADAMA (`:622`)

Só quando **cultura + alvo + molécula** estão provados no `FATO`, contra
`referencia/adama` (ENTRADA B, só leitura, SHA-256 dos 4 livros no livro da
CAP-SCI), e só com registo `ADMIN_ACTIVE = true`. Igualdade exata após dobrar
caixa/acentos (INT-LAW-081: `vite da tavola` ≠ `VITE`). Aliases de molécula
**declarados** à mão (`:585`); `METALAXYL ≠ METALAXYL-M`.

| estado | quando |
|---|---|
| `CANDIDATE` | casa rótulo ativo, local e período provados |
| `PARTIAL` | casa rótulo ativo; falta local e/ou período |
| `RELACAO_SEM_ROTULO` | a ADAMA tem a molécula, nenhum rótulo ativo nesta cultura × alvo |
| `UNKNOWN_REFERENCIA` | a referência conhece o ativo e não o liga a produto — **nunca «a ADAMA não tem»** |
| `UNKNOWN_MOLECULA` | a molécula não está entre os ativos da referência |
| `NOT_POSSIBLE` | falta cultura, alvo ou molécula no estudo |

Regra de modelo **não** liga a produto. Toda ligação leva `NAO_PROVA`: é
temática — não diz que o estudo testou o produto, a formulação ou a dose.

**As 4 parciais do míldio** (pré-medição T6), reproduzidas contra a referência
real com estudos sintéticos: folpet e metalaxil-M → FOLPAN GOLD, SESTO GOLD;
cimoxanil → ANTERLEX, BADGER 45% WG, CARSON 45% WG, DAUPHIN 45, MOXYL MK,
VANTEX; fosetyl-Al → MOMENTUM PFNPE. Metalaxyl e deltamethrin →
`UNKNOWN_REFERENCIA`; fludioxonil em vite × botrite → `RELACAO_SEM_ROTULO`.
Batem com a pré-medição.

## 5 · O que NÃO se sabe (NÃO SEI declarado)

- **O registo T6 real não está nesta árvore.** Os números da Sala (cultura
  97/100, problema 96/100, molécula 4/100, local 26/100, período 10/100) **não
  foram reproduzidos aqui**. A CAP-SCI ainda não correu sobre eles.
- **Os nomes das chaves no `FATO` real do T6 não foram vistos.** `CHAVES_DO_FATO`
  aceita os nomes prováveis (EN/PT/IT); se o produtor usar outro, a chave sai
  `NAO SEI · AUSENTE_NO_FATO` — falha para o lado seguro, mas pode esconder
  dado que existe. Conferir na primeira corrida real.
- Resultado/direção e método **não têm campo** na Collection hoje (pré-medição
  §5.5). Sem eles a força sai `NAO SEI` e a leitura `SEM_LEITURA_RESULTADO_NAO_DECLARADO`
  — é o esperado, não defeito.
- A peça fica **PENDING** no mapa («ficheiro novo nunca lido por gente»). Não
  carimbei: `--stamp` é global e carimbaria ficheiros de ~140 outras peças sem
  leitura humana.

## 6 · Provas

- `python3 -m unittest tests.test_capacidade_cientifica -v` → 49 OK.
- `python3 provas/_mutantes_cap_sci.py` → **22/22 mortos**. Na primeira
  passagem viveram 3 (sem-chave virando grupo; ligação sem molécula; regra de
  modelo com molécula) → testes reforçados.
- `motor/` não importa `provas/` por nome nu: o vocabulário do READY chega pela
  corrida (`test_a_porta_cli_liga_o_banco` apanhou a primeira versão, que importava
  a espinha direto — consertado no código, o teste não foi tocado).
- Bateria inteira antes/depois e System Map: ver o relatório da entrega.
