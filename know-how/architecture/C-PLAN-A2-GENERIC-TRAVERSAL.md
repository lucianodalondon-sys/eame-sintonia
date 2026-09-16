# SINTONIA EAME — C-PLAN-A2 — TRAVESSIA GENÉRICA DA UNIDADE

> Registro durável do aprendizado da missão C-PLAN-A2. Não é a Bíblia e não implementa runtime.

## CHECKPOINT

```text
WORK_BRANCH = claude/raw-observation-identity-3jbwco
INITIAL_HEAD = 0958d514355ab183b4b979b79291aee57849c322
FINAL_HEAD = 1d707d31ea3142c51fcb7a073ccb291c0933ac27
RUNTIME_FILES_CHANGED = 0
MIGRATIONS_CHANGED = 0
DATABASE_MUTATIONS = 0
BIBLE_CHANGED = 0
SYSTEM_MAP_CHANGED = 0
```

O KNOWN HEAD fornecido à missão estava desatualizado; o remoto já continha outro documento. A sessão fez fast-forward e não force-push. Regra reutilizável: **head de missão é precondição a medir, não verdade a impor; trabalho concorrente deve ser preservado.**

## O CONTRATO GENÉRICO JÁ EXISTIA

A missão provou que o vocabulário necessário para uma travessia com etapas opcionais já existia antes dela:

- `leis/telemetria.py` declara sete estados de etapa, incluindo `NOT_APPLICABLE` com razão escrita;
- `leis/artefato.py` separa `NAO_SEI` de `NAO_SE_APLICA`;
- migration 024 já admite `NOT_APPLICABLE` no enum de estado de etapa.

O problema não era ausência de conceito. O T-32 atual simplesmente não fala o contrato inteiro: emite `FAIL` e `NOT_RUN`, mas não há writer de runtime para `NOT_APPLICABLE`.

Regra:

> Antes de inventar contrato novo, medir se a casa já possui o vocabulário e a semântica necessários. Muitas vezes o gap é de implementação/adoção, não de lei.

## DERIVED NÃO É OBRIGATÓRIO EM TODA ROTA

Resultado fechado:

```text
DERIVED_ALWAYS_REQUIRED = NO
STRUCTURED_ALWAYS_REQUIRED = YES como etapa conceitual
ERROR_CAN_ADVANCE = NO
NAO_SE_APLICA_CAN_ADVANCE = CONDITIONAL
```

Quando uma etapa não se aplica, a linhagem aponta para a **última etapa que realmente aconteceu**. Se não houve DERIVED:

```text
edge_from = RAW
parent = RAW observation id + content hash
```

Nunca fabricar `DERIVED_ID` para preencher desenho.

Regra:

> Etapa opcional ausente não cria artefato fantasma. A linhagem salta a etapa com `NOT_APPLICABLE` e preserva o último artefato verdadeiro.

## O T-32 ATUAL É UMA QUIMERA DE DUAS FORMAS

A missão encontrou um defeito estrutural importante em `coleta/rota_forward_documento.py`:

- a derivação de cima exige `unidade['PDF']`, portanto o runner é PDF-específico;
- a estruturação de baixo usa `public.conteudo`, cuja identidade exige `canal_id`, que por sua vez exige origem/pessoa/organização — forma de rede social.

O teste da M2 precisou inventar uma organização no banco descartável para um boletim documental caber nessa estrutura. O próprio teste registra `CHANNEL_IDENTITY_NOT_RESOLVED`.

Regra:

> Não reutilizar store/identidade de uma espécie de conteúdo como contrato universal só porque existe. Documento, social, tabular e mídia podem compartilhar a travessia, mas não precisam compartilhar o mesmo Structured owner/schema.

## QUATRO CLASSES DE UNIDADE

A sonda mediu quatro classes usando fixtures reais:

```text
A documento/PDF -> texto derivado
B publicação social com texto nativo
C legenda buscada na plataforma
D tabular normalizado
```

As quatro conseguem satisfazer estágio/linhagem na Admission atual quando declaram corretamente `artifact_type`; nenhuma precisa de pai inventado.

## CAPTION BUSCADA != TRANSCRIÇÃO DERIVADA

Achado importante:

```text
PLATFORM CAPTION FETCH = aquisição/RAW
MACHINE TRANSCRIPTION = derivação produzida por nós
```

As 15 “transcrições” reais medidas são legendas buscadas da plataforma. Ir buscar legenda é aquisição; não é uma derivação produzida pelo SINTONIA. O schema/ferramenta de machine transcription existe, mas artefatos reais de `TRANSCRIPTION` produzidos por máquina medidos nesta missão = 0.

Regra:

> Classificar pelo processo que gerou a unidade, não pelo formato textual final. Texto vindo pronto da fonte é RAW; texto produzido por Whisper é DERIVED/TRANSCRIPTION.

## ADMISSION — CONTRATO MÍNIMO MEDIDO

A missão fechou que o item mínimo para a pergunta de estágio/linhagem usa cinco campos básicos, com pai somente quando a unidade é derivada. Universo e corrida são argumentos da chamada, não precisam ser repetidos como campos apenas para a porta funcionar.

Regra:

> Pai é requisito epistemológico de DERIVED, não requisito burocrático de todo item.

## GAP DE NOT_APPLICABLE

O enum e a lei existem, mas não há coluna/contrato operacional comprovado para guardar a **razão** de `NOT_APPLICABLE`, nem trava simétrica à exigência de código/motivo em `FAIL`.

Antes de implementar travessia genérica, fechar:

```text
NOT_APPLICABLE_REASON_REQUIRED = YES
NOT_APPLICABLE_WITHOUT_REASON = invalid
```

Sem inventar migration até medir o schema-alvo correto.

## BLOQUEIO REAL PARA 3→1

A missão concluiu que a travessia genérica não é o principal bloqueio restante. O bloqueio é `STRUCTURED`:

- não existe owner único/global — e isso pode ser correto por conceito;
- o único caminho atual usado pelo T-32 estrutura como conteúdo social e exige canal;
- documento/tabular precisam de owner/schema estruturado compatível com a espécie.

Regra:

> `STRUCTURED` é etapa obrigatória, mas não precisa de uma tabela universal. Aplicar `ONE STRUCTURED CONCEPT → ONE OWNER` e deixar o runner despachar para o owner correto por espécie.

## T-61

A missão não encontrou `T-61` como card nesta fotografia de trabalho. Portanto:

```text
TRANSCRIPTION_POSITION_IN_PIPELINE = conceptually closed
T61_RUNTIME/CARD_IDENTITY = NÃO SEI nesta fotografia
```

Não promover ID de arquitetura-alvo a fato de runtime sem migração/declaration.

## PRÓXIMO PASSO

O próximo trabalho deve resolver **Structured dispatch/owners por espécie** e a persistência explícita da razão de `NOT_APPLICABLE`, mantendo a regra de uma única travessia e sem alterar Admission para fabricar lineage.

Só depois faz sentido implementar o 3→1 real e provar uma unidade não-PDF até Admission/READY.
