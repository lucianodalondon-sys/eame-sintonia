# KNOW-HOW DAILY — CENSO DA INTELLIGENCE — 2026-09-13

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável produzido pelo censo I-CENSUS-01. Não cria segundo KNOW-HOW, não substitui `SINTONIA-EAME-KNOW-HOW.md`, não é Bíblia e não é fonte de estado corrente. Para estado corrente, medir novamente Git/código/runtime/provas.

## PROVA DE ORIGEM

Censo medido em `claude/funny-hypatia-y7ho5s` e persistido no commit `dc0adf040c1b6476799d76b3f22c0121475f39f1` em `docs/operacao/CENSO-DA-INTELLIGENCE.md`.

`main` medido no censo e revalidado após a entrega: `f437ff1140fa97484ca9695b341fbe9ca0a9f050`.

## DELTA DURÁVEL

### 1. Collection chega a READY, mas a Intelligence existente não consome essa fronteira

O censo mediu que `admissao/admissao.py` produz o estado `PRONTO_PARA_INTELIGENCIA`, porém os mecanismos atuais de Intelligence não o leem. Também não foi encontrado motor atual lendo `guarda/`, `data/collection-store` ou `data/collection-ledger` como entrada de Intelligence.

Consequência durável:

```text
COLLECTION READY ≠ INTELLIGENCE INPUT CONNECTED
```

A existência da Sala de Espera e do estado READY não prova a existência da borda `SALA DE ESPERA → INTELLIGENCE`.

### 2. O motor de Intelligence existe, mas existência + testes de regra não provam cadeia operacional

O censo mediu código substancial de Intelligence, cadeia/orquestração e suites verdes de regra. Ao mesmo tempo, nenhuma automação medida executa os motores de ponta a ponta nesta linhagem e a cadeia V2.1 possui trava deliberada de linhagem.

Consequência durável:

```text
ENGINE EXISTS ≠ ENGINE RUNS
RULE TESTS PASS ≠ END-TO-END INTELLIGENCE OBSERVED
WIRED ≠ RAN ≠ PROVEN
```

### 3. A entrada histórica da Intelligence é artefato/linha de build, não a fronteira canônica da Collection

Os motores medidos esperam `data/samples/` e/ou `build/.../DESIGN-INGEST`; a pasta de entrada principal não existe nesta árvore e está fora do fluxo canônico medido da Sala de Espera.

Consequência: antes de integrar ou criar novos motores, a arquitetura precisa resolver explicitamente o contrato de entrada da Intelligence a partir de material admitido. A solução concreta ainda NÃO foi desenhada nem autorizada por este censo.

### 4. Portal pode exibir Intelligence sem que a árvore atual consiga reproduzi-la

O censo encontrou superfícies e artefatos reais servidos ao portal, mas também arquivos de dados sem produtor medido nesta árvore e um artefato grande órfão que não é carregado por páginas medidas.

Consequência durável:

```text
PORTAL SHOWS RESULT ≠ CURRENT TREE CAN REPRODUCE RESULT
STATIC SNAPSHOT ≠ INTELLIGENCE ENGINE
```

Reprodutibilidade precisa fazer parte da prova de qualquer capacidade de Intelligence.

### 5. Label Intelligence atual é separável em DATA / ANALYSIS / UI; mecanismo recalculável não foi provado

O censo mediu dados de labels, uma análise humana congelada e UI que aplica os veredictos. Não mediu mecanismo que refaça automaticamente a análise/crossing.

Consequência durável:

```text
LABEL DATA ≠ LABEL ANALYSIS ≠ LABEL INTELLIGENCE ENGINE ≠ LABEL UI
```

Não chamar a UI ou a tabela congelada de motor de Intelligence.

### 6. CROSSING existe; SIGNAL e FINDING ainda não possuem owner conceitual provado nesta árvore

O censo encontrou `CROSSING` como mecanismo/conceito implementado. `SIGNAL` e `FINDING`, nesta árvore medida, aparecem como nomes de campos e não como conceitos arquiteturais com owner/schema/store próprios. `COLLECTION_GAP` não foi encontrado em código.

Consequência: a Bíblia candidata pode definir a direção desejada, mas não se deve retroativamente declarar esses conceitos como já implementados.

```text
DESIRED CONCEPT ≠ EXISTING IMPLEMENTATION
```

### 7. Gerador canônico de Intelligence possui conflito de autoridade

O censo mediu que `motor/v21_cadeia.sh` e `italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json` apontam para geradores/linhagens diferentes; o contrato ainda classifica como stale uma safra associada ao gerador mencionado pela cadeia.

Consequência: o gerador canônico permanece INDETERMINADO até arbitragem por autoridade/prova. Não escolher por nome de branch, idade ou conveniência.

### 8. Reorganização de diretórios e evolução de lógica ocorreram em linhas diferentes

A árvore atual usa `motor/`, enquanto linhagens geradoras históricas relevantes mantêm grande parte da Intelligence em `scripts/`. O censo mediu também divergência substantiva de conteúdo, não apenas renomeação.

Consequência:

```text
PATH DRIFT + LOGIC DRIFT = INTEGRATION RISK
```

Não integrar Intelligence por cópia de diretórios ou contagem de commits. É necessário reconciliar conceito, owner, comportamento e prova.

### 9. System Map precisa continuar distinguindo topologia de execução observada

O censo confirmou que um card/edge verde `WIRED` pode ser interpretado visualmente como se a cadeia tivesse rodado. Para motores e cadeias, a leitura operacional precisa distinguir no mínimo declaração/ligação/execução/prova e, quando aplicável, estado impedido por fence/linhagem.

Consequência:

```text
WIRED GREEN ≠ RAN GREEN
```

O mapa observa a máquina; não deve promover ligação para execução.

### 10. A Bíblia V0.2 deve ser reconciliada contra este censo antes de promoção

Existe uma Bíblia de Engenharia da Intelligence V0.2 candidata em `research/intelligence-bible-engineering-v1`. Este censo mede a máquina existente. Os dois artefatos têm papéis diferentes:

- Bíblia candidata: como a Intelligence deve funcionar;
- Censo: o que existe/está ligado/rodou na fotografia medida.

Consequência: antes de promoção canônica ou implementação estrutural, reconciliar `DESIRED` vs `MEASURED`, sem alterar o censo para fazê-lo combinar com a Bíblia e sem alterar a Bíblia para fingir capacidade existente.

## ORDEM DERIVADA PARA A PRÓXIMA DECISÃO

Este censo NÃO autoriza implementação automática.

Antes de criar a borda `SALA DE ESPERA → INTELLIGENCE`, deve haver missão específica de contrato/arquitetura que:

1. releia Bíblia da Collection, Bíblia candidata de Intelligence, contratos e este censo;
2. preserve o owner da Admission/READY em Collection;
3. defina sem duplicação o primeiro contrato consumível pela Intelligence;
4. prove lineage da observação/claim admitido até a unidade de execução da Intelligence;
5. não bypass Collection com `data/samples`, snapshot manual ou pasta de build ad hoc;
6. reconcilie ou isole os geradores históricos conflitantes;
7. tenha teste negativo que prove que material não admitido não entra na Intelligence;
8. tenha prova executável de um item admitido sendo consumido sem produzir ainda julgamento analítico inventado.

A implementação concreta permanece `NOT_DESIGNED / NOT_AUTHORIZED` até essa missão.

## FECHAMENTO

O QUE mudou → o estado real da Intelligence foi medido com profundidade; o principal gap é a ausência de uma borda observada entre READY/Sala de Espera e os motores existentes.

POR QUÊ → sem essa medição, seria fácil confundir motor existente, testes verdes, snapshots de portal e Intelligence operacional.

PROVA → `docs/operacao/CENSO-DA-INTELLIGENCE.md` @ `dc0adf040c1b6476799d76b3f22c0121475f39f1`.

CONSEQUÊNCIA → não construir novo motor por enquanto; primeiro reconciliar Bíblia candidata com a máquina medida e desenhar/provar o contrato de entrada canônico da Intelligence.

KNOW_HOW_DELTA = ATUALIZADO

HARD STOP
