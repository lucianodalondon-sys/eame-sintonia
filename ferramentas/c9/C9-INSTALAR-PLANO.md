# C9-INSTALAR-PLANO — o C9-IDIOMA sobre o vivo ce28040c — 25/09/2026

Ramo **`c9-sobre-ce28-v1`** — instalar a **ponta do ramo** (o SHA de «PRONTO»; conferir com `git rev-parse origin/c9-sobre-ce28-v1`); o mapa é regerado no último commit do ramo, depois deste plano = produção `ce28040c` + `origin/c9-idioma-v1` (`bcefc6d9`). **NÃO instalado.**
Sem rede HTTP; Sala real **só lida** (`PGOPTIONS=-c default_transaction_read_only=on`, DSN do ficheiro, nunca impressa);
nenhum RAW tocado; o vivo não foi tocado (só leitura dos livros para a cópia).

## EM PALAVRAS SIMPLES

O C9 conserta duas coisas no relatório da micro-coleta. **(1)** O detector de língua não reconhecia notícias
italianas curtas e dizia «não sei». **(2)** Pedido pela linha de comando, o relatório não recebia as corridas,
e por isso dois critérios reprovavam sempre, mesmo quando estava tudo certo. Juntei o C9 à produção de hoje **sem
nenhum conflito de código**. Numa cópia fiel do vivo, o relatório das **38 corridas da 3.ª onda** passa de **6 para
8 critérios aprovados em 9**: **C1** (a saída foi pela Itália) e **C3** (o portão aprovava a fonte na hora) passam a
**PASS**. O único que falta, o C2, espera leitura humana — já era assim. Os testes do C9 passam (9/9) e os 3
vermelhos que aparecem já existem na produção. A instalação é um avanço direto (ff-only) e não mexe em nenhum livro.

## 1 · A junção

| | resultado |
|---|---|
| `git merge --no-ff origin/c9-idioma-v1` sobre `ce28040c` | conflitos **só em 15 ficheiros gerados do mapa** (ficou a versão da produção; refeitos pela cadeia) · **0 de código** |
| código do C9 no ramo | `scripts/micro_coleta/micro_coleta.py`, `tests/test_c9_idioma.py`, `.gitattributes` **iguais byte a byte** aos do `c9-idioma-v1` |
| ff-only sobre `ce28040c` | **SIM** (`ce28040c` é antepassado do ramo) |
| livros (16) que o ramo muda no Git | **0** |

## 2 · Testes por NOME, ramo × produção pura (`ce28040c`)

`tests/test_c9_idioma.py` · `test_micro_coleta_instrumento` · `test_ensaio_offline_micro` · `test_micro_rede_real`
(listas em `TESTES-RAMO.txt` e `TESTES-PRODUCAO.txt`).

| | ramo | produção |
|---|---|---|
| `test_c9_idioma` | **9/9 OK** | (não existe) |
| vermelhos, por nome | 3 | **os mesmos 3** → herdados |

Os 3 herdados: `test_ensaio_offline_micro.TestServidorECurl.test_https_com_host_original_serve_os_bytes`,
`…test_o_que_nao_foi_gravado_da_404_e_fica_registado`,
`test_micro_coleta_instrumento.TestFiltroAusenteFalhaAlto.test_relatorio_e_dados_da_3b_desencontrados_rebentam`.

## 3 · Ensaio — relatório das corridas da 3.ª onda (`ensaio/`, script `ensaio_c9.sh`)

Cópia = worktree destacada no HEAD do vivo `ce28040c` + os 16 livros do disco (foto). Estado da onda:
`C:/Users/London1/sintonia-sala-italia/ondas/ONDA3-WEB-20260925-1934/ONDA-WEB-ESTADO.json` → **38 RUN_IDs**.

| critério | ANTES (produção, `relatorio --run-id=…×38`) | DEPOIS (C9, `… --estado=<ONDA-WEB-ESTADO.json>`) |
|---|---|---|
| **C1 · egresso IT por corrida** | **FAIL** — 0 corridas medidas | **PASS** — 38 medidas, **38 × IT/IT** |
| **C3 · portão no instante** | **FAIL** — 0 medidas | **PASS** — 38 medidas, **38 × ELIGIBLE** |
| C2 · matéria ≠ capa | PENDENTE_HUMANO (7 capas do juiz) | igual |
| C4 · proveniência · C5 · FACT_TIME/LOCATION · C6 · zero bypass · C8 · duas perguntas | PASS | igual |
| C9 · idioma | PASS (it 70 · en 3 · NÃO SEI 2) | PASS (**it 72** · en 3 · NÃO SEI 0) |
| **total** | **6 de 9** | **8 de 9** |

Livros iguais depois do merge e depois do relatório; desfazer (`reset --keep`): 0 ficheiros de código ≠ vivo,
HEAD = vivo.

## 4 · Mapa

Regerado pela cadeia sob a LOCK-PESADO (prioridade do coordenador, 26/09 00:58): `correr_a_cadeia.py REGERAR`
→ commit (o último do ramo, depois deste plano) → `VALIDAR` = **SYSTEM_MAP_CHECK=PASS**. **Carimbo igual:** a validação só reescreveu
`HEAD`/`HEAD_DA_MEDICAO` e `GENERATED_AT`/`GERADO_EM` em 6 ficheiros gerados — **0 linhas de conteúdo** —; esses
carimbos ficaram num stash com nome (`c9-carimbos-validar-*`), não no ramo. Peça nova declarada:
`C-C9-INSTALAR` (`ferramentas/c9/ensaio_c9.sh`, `c9-testes.sh`). ⚠️ Lição medida: mexer num ficheiro do ramo DEPOIS de regerar o mapa reprova a P1 (o mapa guarda o sha de cada ficheiro) — por isso o plano fecha-se antes do mapa.

## 5 · Plano de instalação (executa: o coordenador; um escritor no vivo)

```bash
VIVO=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
C9=<SHA de PRONTO = ponta de origin/c9-sobre-ce28-v1>
D=$(date +%Y%m%d-%H%M); CORTE=/c/cutover/c9-$D; mkdir -p $CORTE
LIVROS=$(git -C $VIVO --no-optional-locks status --short | grep '^ M' | awk '{print $2}' | tr '\n' ' ')
```

1. **Parar o robô** — `PARAR.flag`; esperar o supervisor sair (≤ 60 s); 0 processos `supervisor|worker|ponte_automatica|observador`. ⏱️
2. **Conferir o ponto de partida** — `git -C $VIVO rev-parse --short HEAD` TEM de dar **ce28040c** (senão PARAR) · `echo $LIVROS | wc -w` (16).
3. **Backup** — `for f in $LIVROS; do mkdir -p $CORTE/$(dirname $f); cp $VIVO/$f $CORTE/$f; done; (cd $CORTE && sha256sum $LIVROS > SHA256-ANTES.txt); git -C $VIVO rev-parse HEAD > $CORTE/HEAD-ANTES.txt`.
4. **O ramo não toca livros** — `git -C $VIVO fetch origin c9-sobre-ce28-v1 && git -C $VIVO diff --name-only HEAD $C9 -- $LIVROS | wc -l` → **0**.
5. **Merge** — `git -C $VIVO merge --ff-only $C9`.
6. **Livros iguais** — `(cd $VIVO && sha256sum $LIVROS) | diff - $CORTE/SHA256-ANTES.txt && echo LIVROS IGUAIS` 🛑 senão DESFAZER.
7. **Amostras sem conversão de linha** — `git -C $VIVO check-attr text tests/dados/c9-idioma/raw-1436-arpae-mare-balneabile.txt` → `text: unset`.
8. **Testes** — `cd $VIVO/tests && py -B -m unittest test_c9_idioma` (**9 OK**) · `py -B -m unittest -v test_micro_coleta_instrumento test_ensaio_offline_micro test_micro_rede_real` → só os **3 herdados** vermelhos (lista no §2).
9. **Mapa** — com a LOCK-PESADO: `py system-map/scripts/correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`, carimbo igual.
10. **Relatório da 3.ª onda (Sala só leitura)** — `py -B scripts/micro_coleta/micro_coleta.py relatorio --estado=C:/Users/London1/sintonia-sala-italia/ondas/ONDA3-WEB-20260925-1934/ONDA-WEB-ESTADO.json --saida=$CORTE/relatorio-onda3` → **C1 PASS · C3 PASS · 8 de 9**.
11. **Push** — `git -C $VIVO push origin HEAD:servico-20260923-0923`.
12. **Religar o robô** — `rm PARAR.flag`; supervisor pelo meio de sempre. ⏱️
13. **Daqui em diante**, o relatório de cada onda/MICRO pede-se com `--estado=<ONDA-WEB-ESTADO.json>` (sem ele, C1 e C3 continuam a reprovar por falta de dados, como antes).

**DESFAZER** (provado na cópia): `PARAR.flag` → `git -C $VIVO reset --keep $(cat $CORTE/HEAD-ANTES.txt)` → repor `$LIVROS` de `$CORTE`
→ `sha256sum` = `SHA256-ANTES.txt` → `rm PARAR.flag`. O C9 não escreve em livro nenhum (o relatório só escreve na pasta `--saida`).
Se o passo 11 já fez push: não forçar; o coordenador decide.
