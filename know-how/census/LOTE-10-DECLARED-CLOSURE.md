# SINTONIA EAME — KNOW HOW — LOTE 10

> Registro durável do fechamento do universo DECLARED da Collection no snapshot `572647dce8a38b8835aafa6f9e3e42d2652fbcd9`.

## RESULTADO

```text
LOTE_10_CLOSED = YES
DECLARED_COLLECTION_CENSUS_CLOSED = YES
SYNTHETIC_COLLECTION_CENSUS_CLOSED = NO
FULL_COLLECTION_CENSUS_CLOSED = NO

AUDITED_COLLECTION_NODES = 55 / 64
AUDITED_DECLARED = 54 / 54
AUDITED_SYNTHETIC = 1 / 10
REMAINING_DECLARED = 0
REMAINING_SYNTHETIC = 9
```

Cards auditados no lote:

```text
C-BIBLIA
C-ADAMA-IT
C-ADAMA-ES
C-BANCO-NO-SECO
C-CICATRIZES-BR
```

## LIÇÃO 1 — FECHAR DECLARED NÃO FECHA A COLLECTION

`54/54 DECLARED` significa que todas as responsabilidades declaradas foram medidas nesta fotografia. Ainda existem 9 nós sintéticos não auditados. Nunca publicar `FULL_COLLECTION_CENSUS_CLOSED` por confundir declared com universo visual.

## LIÇÃO 2 — GOVERNANÇA NÃO É ETAPA DA ESTEIRA

Quatro dos cinco cards deste lote satisfazem melhor a definição de governança/prova do que de Collection operacional:

```text
C-BIBLIA        -> GOVERNANCE
C-ADAMA-ES      -> OUTSIDE_COLLECTION / FUTURE HANDOFF
C-BANCO-NO-SECO -> PROOF / INFRASTRUCTURE
C-CICATRIZES-BR -> GOVERNANCE
```

`C-ADAMA-IT` é MIXED e contém tanto Collection de país quanto reference data reutilizável.

Regra reutilizável: família deve refletir responsabilidade real, não a pasta/zona histórica em que a peça acabou ficando.

## LIÇÃO 3 — BÍBLIA É AUTORIDADE DE GOVERNANÇA, NÃO COMPONENTE DE COLETA

A Bíblia define o que “coletar” significa, possui representação legível por máquina e é validada no CI, mas praticamente nenhuma lei é consultada por runtime para decidir. Runtime implementa a lei em código e normalmente só a cita em comentário/docstring.

Regra: `LAW AUTHORITY != RUNTIME COMPONENT`. Separar lei, registry derivado, conformidade por país, provas/censos e decision logs.

## LIÇÃO 4 — UMA LEI LEGÍVEL POR MÁQUINA PRECISA DE UMA ÚNICA INTERFACE CANÔNICA

Foram medidos dois caminhos para a máquina ler lei:

```text
BIBLIA.md -> valida_biblia.py -> docs/biblia/leis.json
BIBLIA.md -> a_fronteira_da_coleta.py -> parse direto do bloco markdown
```

Mesmo com hierarquia explícita entre texto e JSON, dois formatos de leitura criam risco de drift de contrato. Regra: consumidores devem depender de uma interface canônica, ou a segunda forma de parsing precisa ser explicitamente contratada e validada.

## LIÇÃO 5 — CARD DE PAÍS NÃO PODE ESCONDER REFERENCE DATA GLOBAL/EU

`C-ADAMA-IT` mistura catálogo comercial italiano, rótulos italianos, aprovação de substâncias pela UE, FRAC/HRAC/IRAC, derivados e QA.

Aprovação UE e classificação de modo de ação não são “ADAMA Itália”; são reference data EAME/global e devem ser reutilizadas entre países.

Regra para novo país: reusar o que é CORE/EAME; reexecutar somente catálogo/registro/rótulos locais. Não recolher novamente a mesma verdade europeia com outro nome de país.

## LIÇÃO 6 — ARTEFATO CONGELADO DE HANDOFF NÃO É RUNTIME VIVO

`C-ADAMA-ES` possui output observado, mas o gerador depende de um ref Git inexistente no snapshot e seu workflow está deliberadamente fora de `.github/workflows/`.

Regra: `OUTPUT_OBSERVED != GENERATOR_RUNTIME_ALIVE`. Projeto futuro/congelado precisa ser classificado como tal e não como gate operacional.

## LIÇÃO 7 — TEST DOUBLE PODE SER BOM SEM PROVAR PRODUÇÃO

`C-BANCO-NO-SECO` é um test double explícito. Ele simula a interface de escrita e parte da aritmética da migration, mas declara claramente o que não consegue provar sobre Postgres real.

Regra: um double é válido quando seu escopo é explícito e existe prova separada para comportamento de banco real. Nunca promover `DRY_TESTED` a `DB_TESTED`.

## LIÇÃO 8 — “CICATRIZES DO BRASIL” SÃO KNOW HOW CORE, NÃO REGRA LOCAL

As 35 cicatrizes medidas são princípios semânticos reutilizáveis; o Brasil aparece na proveniência dos casos, não na validade das regras.

Regra para expansão internacional: separar `APRENDIZADO_REUTILIZAVEL_SINTONIA` de `APRENDIZADO_LOCAL_PAIS`. Proveniência local não torna a lei local.

## LIÇÃO 9 — GENERATED FAMILY NÃO PODE SILENCIOSAMENTE CONTRADIZER DECLARED FAMILY

Foram encontrados componentes que declaram uma família literal incompatível com a família derivada da zona. O gerador prefere a regra nova e ignora o literal antigo sem reprovar.

Regra: quando declared e derived authority divergem, o sistema deve remover o campo obsoleto ou reprovar. Divergência silenciosa cria duas respostas para “onde esta peça vive?”.

## LIÇÃO 10 — GERAR SQL NÃO É ESCREVER NO BANCO

O Lote 10 reconfirmou a distinção já aprendida: encontrar `insert into` dentro de um gerador de texto SQL não prova escrita em banco. Autoridade de tabela deve ser medida pelo mecanismo efetivo de execução, não pela presença da string.

## LIÇÃO 11 — FECHAMENTO DO DECLARED É O PONTO CERTO PARA PARAR DE REABRIR CARDS

A partir de `AUDITED_DECLARED = 54/54`, o trabalho seguinte não deve continuar escolhendo novos declared cards. Primeiro auditar os 9 sintéticos restantes; só depois fazer consolidação transversal e desenhar a arquitetura-alvo.

Ordem preservada:

```text
CENSO DECLARED
-> CENSO SYNTHETIC
-> CONSOLIDACAO TRANSVERSAL
-> ARQUITETURA-ALVO
-> MIGRACAO / REFORMA
-> TESTE E2E
-> SYSTEM MAP COMO CONSEQUENCIA
```
