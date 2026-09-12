# DAILY KNOW-HOW — 2026-09-12 — COLLECTION / STRUCTURED DOCUMENTAL

Este arquivo pertence à trilha canônica `know-how/daily/` e registra somente o delta durável desta decisão. Não cria um segundo owner de arquitetura; Bíblia, contratos, schema/runtime e `SINTONIA-EAME-KNOW-HOW.md` continuam com seus papéis canônicos.

## CONTEXTO MEDIDO

```text
REPO = lucianodalondon-sys/eame-sintonia
COLLECTION_BRANCH = claude/collection-v1-operational-close
COLLECTION_HEAD = bd5ad9c06c3e1d6cab44f561f7cdaaac3ecebecd
FIRST_LOST_EDGE = DERIVED -> STRUCTURED
MATERIAL_LINEAGE = IMPLEMENTED
MIGRATION = 029
MIGRATION_LIVE = NOT_APPLIED
```

No HEAD medido, a Collection atravessa na mesma história até `DERIVED`. O primeiro edge perdido continua `DERIVED -> STRUCTURED`.

A causa medida não é ausência total de identidade de canal. Há três conceitos diferentes:

```text
SCHEMA_OWNER       = EXISTE   — public.origem/public.canal, migration 002
RUNTIME_RESOLVER   = EXISTE   — canal_canonico lê e nunca cria
IDENTITY_CREATOR   = NÃO PROVADO / AUSENTE no fluxo atual
```

Além disso, `public.conteudo` exige simultaneamente `canal_id` e `content_id`, e ambos pertencem ao regime de identidade nativa de plataforma definido pelas migrations 002/003.

## DECISÃO DURÁVEL

Para uma fonte documental não social / não-plataforma, como uma agência pública que publica boletins PDF no próprio sítio:

```text
SOURCE      = organização/fonte canônica que publica ou mantém
ENDPOINT    = endereço técnico onde se acessa o material
ARTIFACT    = objeto efetivamente preservado
CANAL       = NOT_APPLICABLE quando não há identidade nativa de canal
CHANNEL_ID  = NOT_APPLICABLE quando a plataforma não emite tal identidade
DOCUMENT_ID = valor nativo comprovado pela fonte; sem prova, UNKNOWN/NULL
```

Escolha arquitetural: **OPÇÃO B**.

`public.conteudo` não deve ser forçado a servir de casa para documentos sem identidade nativa de plataforma por meio de IDs inventados ou constraints afrouxadas apenas para fazer a estrada passar.

## POR QUÊ

A decisão preserva leis já canônicas:

- `SOURCE != ENDPOINT != ROUTE != EXECUTOR != DISCOVERED ITEM != ARTIFACT`;
- `CHANNEL_ID` não é nome, handle, URL, domínio ou perfil;
- `SHA256` identifica bytes, não documento, canal ou observação;
- `SOURCE_ID` identifica a fonte, não o canal nem o documento;
- `DOCUMENT_ID` só existe quando a própria fonte consegue prová-lo;
- ausência de identidade continua `UNKNOWN` / `NOT_APPLICABLE`, nunca preenchimento sintético.

A ARPAV é o exemplo explícito da Bíblia: a organização é `SOURCE`, a URL do boletim é `ENDPOINT` e o PDF preservado é `ARTIFACT`. Converter URL/domínio/SOURCE_ID/SHA em `channel_id` ou `content_id` fabricaria identidade.

A opção C — apenas tornar `conteudo.canal_id` nulável — também não resolve o contrato, porque `conteudo.content_id` continua sendo identidade nativa de plataforma e a unicidade atual continua modelando `(canal_id, content_id)`.

## PROIBIÇÕES

Nunca fabricar `CHANNEL_ID`, `CONTENT_ID` ou `DOCUMENT_ID` a partir de:

```text
URL
domínio
SOURCE_ID
slug
filename
SHA256
storage_path
timestamp
nome da organização
```

`web` existir no enum de plataforma não autoriza transformar um site próprio em canal com identidade sintética.

## CONSEQUÊNCIA DE IMPLEMENTAÇÃO

Antes de criar schema novo, medir no HEAD funcional:

```text
DOCUMENT_STRUCTURED_OWNER = EXISTING | ABSENT | UNKNOWN
```

Se `EXISTING`, reutilizar o owner canônico.

Se `ABSENT`, criar somente a menor casa STRUCTURED documental necessária para o cenário canário real, com lineage explícita a `derived_artifact` e proveniência de RUN/SOURCE, sem inventar identidade global de documento.

Se `UNKNOWN`, parar e medir; não criar um segundo owner por conveniência.

Depois da implementação mínima, reexecutar imediatamente `provas/o_pedido_atravessa.py` e continuar pelo novo `FIRST_LOST_EDGE`.

## REGRA DE ESCOPO PARA O FECHAMENTO DA COLLECTION

A partir daqui, a Collection entra em modo **TEST -> FIRST LOST EDGE -> FIX MÍNIMO -> RETEST**.

Só implementar um achado se ele:

1. impedir `REQUEST -> WAITING_ROOM` na mesma história; ou
2. fizer a história perder/fabricar identidade, proveniência ou estado.

Todo o resto vira backlog.

Débitos já conhecidos que permanecem não bloqueantes salvo nova prova:

- resultado individual por item sem owner durável;
- `ROUTE_CLASS_ID = UNKNOWN`;
- derivado em `NAO_SEI/`;
- telemetria/custo perfeitos;
- backfill histórico.

## O QUE NÃO ESTÁ AUTORIZADO

```text
SCRAP_INTEGRATION = NO
BIG_COLLECTION = NO
INTELLIGENCE = NO
PORTAL = NO
LIVE_MIGRATION = NO
SYSTEM_MAP_STRUCTURAL_WORK = NO
```

A ordem permanece:

```text
FECHAR COLLECTION CORE
-> integrar aquisição/SCRAP
-> provar integração
-> coleta grande
-> reconciliar/auditar/admitir/popular Sala de Espera
-> Intelligence
```

## PROVA / REFERÊNCIAS

- `BIBLIA-CANONICA-DA-COLETA.md`, especialmente COL-LAW-009;
- `supabase/migrations/002_identidade_pessoa_org_canal.sql`;
- `supabase/migrations/003_conteudo_documento_video_transcricao.sql`;
- `coleta/social_persistencia.py`;
- `provas/o_pedido_atravessa.py`;
- branch `claude/collection-v1-operational-close` no HEAD `bd5ad9c06c3e1d6cab44f561f7cdaaac3ecebecd`.

## FECHAMENTO

1. **O que mudou?** Foi tomada a decisão humana que bloqueava `DERIVED -> STRUCTURED`: documento não-plataforma não recebe canal/IDs sintéticos; `CANAL/CHANNEL_ID = NOT_APPLICABLE` quando o conceito não existe.
2. **Por quê?** O schema atual de `canal/conteudo` modela identidade nativa de plataforma; URL, domínio, SOURCE_ID e SHA não provam essa identidade.
3. **Qual a prova?** Bíblia COL-LAW-009, migrations 002/003, writer social e E2E no HEAD acima.
4. **O que não mudou?** `public.conteudo`, Collection downstream, SCRAP, Intelligence, Portal e LIVE não foram alterados por esta decisão.
5. **O que continua desconhecido?** Se já existe no HEAD funcional uma casa STRUCTURED documental adequada; precisa medir antes de criar uma.
6. **Risco restante?** Criar uma segunda casa documental apesar de owner existente, ou voltar a fabricar IDs para fazer teste passar.
7. **Bíblia precisa mudar?** Não há evidência de necessidade: COL-LAW-009 já sustenta a decisão.
8. **Contrato precisa mudar?** Somente se existir contrato global dizendo `STRUCTURED = public.conteudo`; isso precisa ser medido.
9. **Próximo passo mínimo?** Medir `DOCUMENT_STRUCTURED_OWNER`; reutilizar se existir, criar o mínimo se ausente, e rerodar o E2E imediatamente.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
