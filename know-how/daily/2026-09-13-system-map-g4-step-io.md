# DAILY KNOW-HOW — 2026-09-13 — SYSTEM MAP G4 / INPUTS E OUTPUTS DECLARADOS

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável da missão `C-SYSTEM-MAP-G4-DECLARED-STEP-IO-V1`; não cria um segundo KNOW-HOW e não substitui `SINTONIA-EAME-KNOW-HOW.md`, o contrato de confiança, o manifesto, o código, o runtime ou as provas.

## CONTEXTO MEDIDO

```text
REPO = lucianodalondon-sys/eame-sintonia
BRANCH = claude/system-map-g4-declared-step-io-v1
HEAD = 8fd37059b7ae29e18f230e880f0afcaa4d22a02d
MANIFEST = system-map/scripts/CADEIA-DO-MAPA.json
SCHEMA = sintonia.system-map.cadeia/2
SYSTEM_MAP_CHECK = PASS
MAP_RULES_CHECK = PASS
COLETA_CHECK = PREEXISTING_FAIL
TRUST = DEGRADED
```

G4 não fechou G5 nem G6. O manifesto ainda declara a dívida `FORA_DESTE_MANIFESTO`; o ciclo `PENTE_FINO_DA_COLETA -> state.generated.json <- GENERATE_SYSTEM_MAP` está declarado, não corrigido.

## DELTA DURÁVEL

### 1 · INPUT/OUTPUT DECLARADO PRECISA SER CONFERIDO CONTRA O CÓDIGO E CONTRA O QUE ABRE DE VERDADE

A declaração do manifesto não é prova por si só. G4 usou duas testemunhas de sentidos opostos: análise estática para saber o que o código nomeia e execução instrumentada para saber o que ele realmente abriu/escreveu.

```text
DECLARED IO != OBSERVED IO
AST ENXERGA O QUE O CÓDIGO NOMEIA.
EXECUÇÃO ENXERGA O QUE O PROCESSO TOCOU.
UMA SÓ NÃO SUBSTITUI A OUTRA.
```

Consequência: contratos de I/O do mapa devem ser verificáveis por evidência independente, e divergência vira falha ou `UNKNOWN/LIMITATION`, nunca ajuste manual do JSON.

### 2 · UM ARTEFATO GERADO PODE SER INPUT REAL DE UM PASSO ANTERIOR NA ORDEM — ESCONDER ISSO NÃO REMOVE O CICLO

`PENTE_FINO_DA_COLETA` lê `state.generated.json`, produzido depois por `GENERATE_SYSTEM_MAP`. G4 declarou essa dependência explicitamente.

```text
CICLO DECLARADO != CICLO RESOLVIDO.
```

Consequência: G6 deve resolver ordem/ciclo; G4 só torna a dívida visível. Reordenar em G4 teria misturado medição com correção.

### 3 · MIGRAR O FORMATO DO MANIFESTO EXIGE MIGRAR TODOS OS CONSUMIDORES, INCLUSIVE QUEM PARECE “ISENTO”

`REGERAR` passou de strings para objetos, mas `VALIDAR` ainda era iterado cru pelo publicador. O Python recebeu `[object Object]`. A falha não derrubou o processo porque o publicador captura o validador para manter o portal no ar.

```text
QUEM É ISENTO DE UMA GUARDA PRECISA DE OUTRA, NÃO DE NENHUMA.
```

Consequência: mudança de schema do owner único exige inventário de todos os leitores e guardas estruturais específicas para qualquer exceção legítima.

### 4 · SAÍDA TRUNCADA NÃO É VEREDITO

A leitura local cortou a linha antes de `SYSTEM_MAP_CHECK=FAIL` e mostrou apenas o prefixo verde.

```text
LER UM PREFIXO DA SAÍDA != LER O VEREDITO.
```

Consequência: provas e diagnósticos devem ler campo/exit status completo ou a fonte primária; nunca concluir estado de uma linha truncada.

### 5 · UM HARNESS DE MUTAÇÃO PODE MATAR O REPOSITÓRIO EM VEZ DO MUTANTE

Um ataque moveu `scan_casco.py`; a limpeza apagou a cópia movida e destruiu o arquivo real. Doze “mortes” anteriores eram falsos positivos.

```text
MUTANTE EXECUTADO != MUTANTE VÁLIDO.
LIMPEZA DO HARNESS TAMBÉM É CÓDIGO SOB PROVA.
```

Consequência: cada mutante precisa provar que a mutação foi aplicada no alvo certo e que o teardown restaura exatamente o estado inicial antes de contabilizar morte/sobrevivência.

### 6 · DÍVIDA DE OWNER DEVE SER UM CONJUNTO MEDIDO, NÃO UM NÚMERO CONGELADO

O workflow executa passos que o manifesto ainda não governa. G4 registrou os caminhos em `FORA_DESTE_MANIFESTO` e a prova compara a lista ao workflow real.

```text
CHAIN_SINGLE_OWNER = VIOLATED
```

Consequência: G5 deve eliminar a diferença por propriedade de conjunto. Trocar `13` por outro número não fecha owner único.

## PROVA

No HEAD `8fd37059b7ae29e18f230e880f0afcaa4d22a02d`:

```text
SYSTEM MAP CHECK = PASS
MAP RULES CHECK = PASS
COLETA CHECK = PREEXISTING_FAIL
21 ataques/mutantes reportados = 0 sobreviventes
TRUST = DEGRADED
G5_IMPLEMENTED = NO
G6_IMPLEMENTED = NO
SECOND_OWNER_CREATED = NO
```

O manifesto `/2` declara `STEP_ID`, `EXECUTABLE`, `INPUTS` e `OUTPUTS`/`NAO_MATERIALIZA`, inclusive produtores fora do manifesto e a dependência cíclica conhecida.

## O QUE NÃO MUDA

- System Map continua observador, não autoridade arquitetural.
- G4 não unifica a cadeia; isso é G5.
- G4 não reordena a cadeia nem corrige o ciclo; isso é G6.
- `DEGRADED` não vira `PASS` por fechar uma dívida isolada.
- A falha da Collection continua fora da responsabilidade do mapa.

## PRÓXIMO PASSO MÍNIMO

G5: trazer para o owner canônico todos os executáveis que o workflow executa e que ainda estão em `FORA_DESTE_MANIFESTO`, preservando a distinção entre passos da cadeia e o portão pós-commit. Não fazer ordenação topológica nem corrigir o ciclo de G6.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
