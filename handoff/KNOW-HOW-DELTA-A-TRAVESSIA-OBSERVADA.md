# DELTA PARA O KNOW-HOW CANÓNICO — A TRAVESSIA OBSERVADA, E O EXECUTOR QUE SE ESCOLHE POR TABELA

```
ORIGEM            C-SYSTEM-MAP-COLLECTION-TRUTH-V1
BRANCH            claude/system-map-collection-truth-v1
BASE              claude/system-map-g7-g8-visual-clarity-v1 @ 85a24528
KNOW_HOW_MEDIDO   claude/sintonia-eame-know-how-v1 @ d64d8124   (medido 2026-09-14)
ÚLTIMA SECÇÃO     §116.6   (medida agora, não herdada)
NÚMERO DESTA      **por atribuir** — quem integrar escolhe o primeiro livre
```

> **OS DOIS DELTAS ANTERIORES ATERRARAM.** Medido em `d64d8124`: `UM CONSUMIDOR
> ANTES DO PRODUTOR` (3 ocorrências) e `O PAPEL VEM DA EVIDÊNCIA` (1) já estão
> no ficheiro. O `G6` e o `G7` fecharam. Este delta não os repete nem os reescreve.

Esta missão não tem autorização para escrever na branch do know-how. O que segue
é o delta, no formato dela.

---

## ⚠️ ESTE DELTA **CORRIGE** UMA FRASE QUE JÁ LÁ ESTÁ

O know-how, na secção dos quatro planos, deixou uma pergunta em aberto — e
deixou-a **bem**, porque na altura era verdade:

> «Fica por saber o comportamento de `OBSERVED` quando houver travessia
> observada por par de cartões: hoje o ledger observa **ficheiros de executor**,
> não arestas, e duas peças de 160 estão observadas.»
> — `SINTONIA-EAME-KNOW-HOW.md`, linha 7747

**A resposta existe, e já existia no repositório quando a pergunta foi escrita.**
Quem integrar deve emendar essa frase, e não só acrescentar por baixo: deixada
como está, ela continua a autorizar a linha fixa que esta missão veio tirar.

---

## O QUE MUDOU

O gerador do System Map escrevia, numa linha só, em **todas** as arestas:

```python
lig["OBSERVED"] = NAO_SEI
```

e a tela publicava ao lado, em comentário: `OBSERVADA — 0 hoje, e é a verdade`.

Não era a verdade. `system-map/data/provas-de-execucao.json` guardava, para
`coleta/rota_forward_documento.py`:

```
ARESTAS_OBSERVADAS  [[DERIVED, STRUCTURED], [STRUCTURED, ADMISSION]]
DONOS               DERIVED    -> coleta/derivacao_forward.py
                    STRUCTURED -> coleta/social_persistencia.py
                    ADMISSION  -> admissao/admissao.py
RUN_UNICO           RUN-M2-E2E
```

Um par de **etapas** com o **dono de cada uma** escrito ao lado **é** um par de
cartões. Falta só resolver o ficheiro para a peça que o tem — e o mapa já sabia
fazer isso, porque é como ele atribui tudo o resto.

### A LEI

```
ZERO POR OMISSÃO NÃO É PRUDÊNCIA:
É UMA CONTAGEM ERRADA COM CARA DE HUMILDADE.
```

Um plano que se escreve por linha fixa deixa de ser um plano e passa a ser uma
decoração. E o pior dos casos não é o que promove de mais — esse alguém apanha,
porque dói. É o que promove de menos: ninguém reclama de um mapa modesto, e a
única prova forte que a casa tinha ficou cinco dias invisível.

**COROLÁRIO, e este é o que se leva para a próxima:** quando um campo é escrito
por constante, a pergunta não é «está certo?» — é **«quem é que voltaria a medir
isto?»**. Se a resposta for «ninguém», o campo já está errado, e só falta o dia.

---

## A SEGUNDA LEI — O EXECUTOR QUE SE ESCOLHE POR TABELA

O achado `COL-015` escreveu que `ORQUESTRADOR → EXECUÇÃO` estava **CORTADO**, e
que o mapa mostrava o corte «em vez de o completar com seta inventada». A
intenção estava certíssima. A medição é que estava errada.

```python
# pedido/receitas.py
EXECUTORES = {"T7": [{"id": "corpus-pesquisador",
                      "roda": ["coleta/corpus_pesquisador.py", "coletar"], ...}], ...}

# orquestrador/orquestrador.py
comando = list(e["roda"])
subprocess.run([sys.executable, *comando], ...)
```

Cinco alvos, cinco executores, e o orquestrador corre o que a tabela declara.
O `scan_repo.py` nunca viu nenhum deles — e não por ser mau:

```
O EXECUTOR QUE SE ESCOLHE POR TABELA
NÃO APARECE A QUEM SÓ LÊ `import`.
```

O nome do executor vive **dentro de uma lista de dados**. Um casador de imports
pode ser perfeito e continuar cego a isto. **Um scanner de código mede o que o
código NOMEIA; um registo de configuração tem de ser lido por quem sabe que ele
é um registo.** Onde houver despacho por tabela — receitas, rotas, plugins,
`entry_points` — há uma classe inteira de arestas que nenhum scanner de imports
vai encontrar, e o mapa vai chamar-lhe «cortado» com toda a confiança.

**E a aresta que daí nasce é `CODE`, nunca `OBSERVED`:** `--so-plano` devolve o
plano *antes* do `subprocess`. Ninguém mediu a corrida. `CAN DO ≠ DID DO` não
afrouxa por a prova ser boa.

---

## A TERCEIRA — UMA CORRIDA NÃO PROVA UMA LINHA

Apanhado pela guarda `rotulo_narrativo_nunca_recebe_CODE_YES`, do próprio
repositório, contra o autor desta missão.

Ao marcar a evidência de corrida com `SUPPORTS = YES` — o que está certo: ela
*sustenta* a afirmação — ela passou a contar também para `CODE`, porque o
gerador contava `CODE` a partir de «evidência que sustenta». Resultado: uma
aresta narrativa (`ALIMENTA`, que não tem medidor estático nenhum) ficou
`CODE = YES` por causa de um recibo de PostgreSQL.

```
UMA CORRIDA PROVA QUE ACONTECEU.
NÃO PROVA QUE HÁ UMA LINHA QUE A PERMITE — E SÃO PLANOS DIFERENTES POR ISSO.
```

O estado honesto, e é o mais informativo que o mapa tem hoje:

```
DECLARED  UNKNOWN    CODE  UNKNOWN    OBSERVED  YES    PROVEN  YES (no plano OBSERVED)
```

`OBSERVED` **sem** `CODE` lê-se: *aconteceu, e nenhuma análise estática to teria
dito*. Não é uma inconsistência — é a medida de quanto a análise estática não
alcança.

---

## A QUARTA — «NÃO SEI QUEM A CORRE» E «SÓ O TESTE A CORRE» SÃO RESPOSTAS DIFERENTES

O cartão respondia «Recebe de — ninguém» a um botão que uma **pessoa** carrega, e
respondia o mesmo a uma peça que só a sua própria prova põe a andar.

```
UMA ENTRADA EXTERNA NÃO É UM BURACO.
Chamar-lhe buraco gasta a atenção que os buracos a sério precisam.
```

Sete respostas medidas, e nenhuma é o silêncio: `PECA_INTERNA` ·
`EXTERNO_MANUAL` · `EXTERNO_AGENDADO` · `EXTERNO_EVENTO` ·
`CANAL_ABERTO_POR_ROTA` · `SO_A_PROVA_A_CORRE` · `NAO_SE_ATIVA` · `NAO_SEI` com
o motivo escrito.

E `SO_A_PROVA_A_CORRE` foi o que revelou o achado maior da missão: **a única rota
forward da coleta com travessia observada ponta-a-ponta é corrida só pela sua
própria prova.** A estrada está provada; o trânsito não.

**COMO SE SABE QUEM É «PROVA»:** pelo **território declarado** (`Z-PROVA`), nunca
pelo prefixo do nome. A primeira versão usou `categoria == PROOF` e falhou — essa
categoria exige `kind == test` de um dos lados, e das 45 peças de `Z-PROVA` só
**seis** o são; as outras são censos e instrumentos.
`TERRITÓRIO É FACTO DECLARADO. PREFIXO DE NOME É PALPITE.`

---

## A QUINTA — UM ATAQUE QUE APANHA O CASO BOM NÃO ENCONTROU UM DEFEITO

Dos 20 ataques do red team, dois «sobreviveram» na primeira corrida. Os dois
eram erro do ataque, não do mecanismo:

| ataque | o que ele media | o que estava errado |
|---|---|---|
| `dado_nao_vira_gatilho` | `categoria == CONTROL` nas arestas de ativação | `C-CI-MAPA --RUNS--> C-MAPA-TESTES` é controlo no **tipo** e prova na **categoria**. Apanhava três peças legítimas. |
| `storage_path_nao_vira_identidade` | um ficheiro que não é o dono da lei | o dono é `provas/objeto_e_observacao_no_postgres.py`, com `C_storage_path_e_unico_no_objeto` contra Postgres a sério |

```
UM ATAQUE QUE APANHA O CASO BOM NÃO ENCONTROU UM DEFEITO:
ENCONTROU UM ERRO SEU.
```

O segundo traz uma regra de método: **um red team que verifica uma lei de outro
dono confere que o dono existe e que a guarda continua escrita — nunca a
reimplementa.** Reimplementá-la cria uma segunda verdade sobre a mesma lei, e a
segunda diverge na primeira pressa.

---

## A SEXTA — UM CENSO ESCRITO À MÃO É UMA FOTOGRAFIA

A auditoria dos 64 cartões ia sair num relatório de missão. Um relatório de
missão nasce certo e **envelhece em silêncio**: no dia em que uma aresta muda,
ele continua a dizer o que dizia, e ninguém sabe qual dos dois está errado.

```
UM CENSO ESCRITO À MÃO É UMA FOTOGRAFIA.
UM CENSO DERIVADO É UM ESPELHO.
```

`docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md` passou a sair do **gerador**,
declarado como saída do `GENERATE_SYSTEM_MAP` em `CADEIA-DO-MAPA.json`. Sai da
mesma corrida que produz o estado — não há segunda medição, e por isso não há
segunda verdade.

---

## A SÉTIMA, E É A QUE MAIS CUSTA — O MAPA MEDE OUTRA ÁRVORE

A `REGRA ZERO` desta missão («não confie em estado herdado») pagou-se no primeiro
comando:

```
git merge-base origin/main <esta linha>   →  exit 1, SEM ANCESTRAL COMUM
```

E entre esta linha e a linha funcional da Collection:

```
base comum a93acfdf (2026-09-12 11:17)
  ├─ lado do MAPA        41 commits ·      0 linhas em coleta/ orquestrador/ pedido/
  └─ lado FUNCIONAL     822 commits · +10.759 linhas nessas gavetas
```

Nesta árvore **não existem** `coleta/scrap_executor.py`, `scrap_http.py`,
`scrap_colheita.py`, `adaptador_linkedin.py`, `adaptador_youtube.py`,
`adaptador_instagram.py` nem `eu_regulatorio_executor.py`.

```
UM MAPA PODE ESTAR PERFEITAMENTE CERTO
E ESTAR A DESCREVER UM SISTEMA QUE JÁ NÃO EXISTE.
```

A lei do espelho (`COL-LAW-046`) diz `SISTEMA REAL ⇄ SYSTEM MAP`. Ela não diz
**qual** sistema real — e com duas linhas paralelas de trabalho, essa omissão
deixa de ser teórica. **O mapa precisa de publicar de que LINHA foi gerado, e não
só de que commit.** Publicar o `HEAD` sem dizer que a linha diverge da funcional
é publicar uma precisão que engana.

Registado como `COL-034`. Esta missão **não** fez o merge: 822 commits contra 41
não é merge trivial, e o prompt manda parar antes disso, não improvisar.

---

## O QUE ISTO **NÃO** PROVA

- Não prova que a Collection funciona. Prova que **uma** travessia, de **um**
  documento italiano, atravessou três etapas num Postgres descartável.
- Não prova que o orquestrador correu os cinco executores. Prova que o código
  para os correr existe e está ligado ao registo.
- Não prova nada sobre a Collection de hoje — ver a sétima lei.
- `READY` continua a **nunca** ter sido produzido (`fronteira.observada.json`:
  `READY_PRODUZIDO = false`, `GAP = READY_NUNCA_PRODUZIDO`). Isso não mudou, e
  não era para mudar aqui.
