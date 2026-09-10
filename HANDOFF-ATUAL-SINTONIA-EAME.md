# HANDOFF ATUAL — SINTONIA EAME

**Atualizado em 2026-09-10.**

Este arquivo é o handoff operacional curto para retomar o trabalho sem reabrir decisões já fechadas. O repositório continua sendo a autoridade final: se este texto divergir do código, migrations, provas ou documentos canônicos, **o repositório vence** e a divergência deve ser reportada.

---

## 1. ONDE ESTAMOS AGORA

### Linha de trabalho ativa

- **Branch funcional:** `claude/raw-observation-identity-3jbwco`
- **HEAD observado no GitHub ao gerar este handoff:** `09277bf89c0d9a28324fa7681e437b5e5e094b67`
- **Último commit funcional antes da regeneração do mapa:** `cb8e0968c27ba48aeb88d9ee5151c0c852bc7c3d`
- `09277bf` é uma **regeneração mecânica da cadeia canônica do System Map** após `cb8e096`; não representa nova decisão arquitetural.

### Linha de know-how

- **Branch:** `claude/sintonia-eame-know-how-v1`
- Esta branch existe para preservar handoffs e know-how. **Não é a branch de implementação.**

### Foco atual

Estamos fechando a **fundação canônica da Collection**, especificamente a identidade entre:

`RUN → RAW OBSERVATION → STORAGE OBJECT → DERIVED → STRUCTURED → ADMISSION → READY`

O portal/casco não é o foco. A ordem permanece:

**réguas → coleta → ferramentas → casco por último**.

---

## 2. FUNDAÇÃO QUE NÃO DEVE SER REABERTA

Estas decisões estão fechadas e só podem ser reabertas diante de contraexemplo reproduzível ou incompatibilidade concreta do repositório:

1. `RAW_OBSERVATION_ID = raw_asset.id` surrogate estável.
2. `RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE OBJECT`.
3. `SHA256` identifica bytes/conteúdo, **não** observação.
4. `storage_path` identifica/endereço o storage object, **não** a observação.
5. Retry da **mesma RUN**, mesma fonte, mesmo documento e mesmos bytes deve reutilizar a observação lógica.
6. **Nova RUN** sobre o mesmo documento e os mesmos bytes deve criar **nova observação**.
7. `SOURCE_ID` é o código textual canônico da Collection, por exemplo `IT-T2-002`; **não** é `public.fonte_externa.id` bigint.
8. `DOCUMENT_KEY` só usa identidade documental quando o contrato da fonte realmente prova `DOCUMENT_ID`.
9. Hash **não é mais fallback silencioso de identidade documental**. A especificação mais recente revogou o antigo `CONTENT_DERIVED` como base válida de `DOCUMENT_KEY` para o estado identificado.
10. Histórico não pode ser “corrigido” inventando `SOURCE_ID`, `DOCUMENT_ID`, `DOCUMENT_KEY`, país, data ou qualquer outra identidade não provada.
11. `SOURCE_LOCATION ≠ FACT_LOCATION`.
12. `FACT_TIME ≠ PUBLICATION_TIME ≠ OBSERVED_TIME ≠ COLLECTED_TIME`.
13. Ausência continua `UNKNOWN/NÃO SEI`; nunca inferir silenciosamente.

---

## 3. B5 — OBJETO FÍSICO X OBSERVAÇÃO

O defeito original era estrutural: `raw_asset` dizia representar observação, mas `unique(storage_path)` o forçava a comportar-se como storage object.

### B5A — fases 1–6

Já implementadas por `supabase/migrations/025_o_objeto_ganha_casa.sql`.

O que ficou estabelecido:

- existe `public.storage_object`;
- `storage_object` tem grain de uma cópia física em um endereço;
- `storage_path` é chave única do storage object;
- `sha256` **não** é unique em storage object;
- `raw_asset.storage_object_id` liga observação ao objeto físico;
- `raw_asset.id` foi preservado;
- FK de derived para `raw_asset(id, sha256)` permaneceu intacta;
- `preserved=true` exige storage object ligado;
- writer recebeu adaptação mínima para criar/ligar storage object antes da observação.

**Importante:** B5A não resolveu nova RUN sobre o mesmo `storage_path`, porque `unique(raw_asset.storage_path)` ainda existe por desenho. Isso só pode ser removido depois de a identidade forward estar protegida.

---

## 4. B5B — fases 7–9: ESTADO ATUAL

**Ainda não foram implementadas em migration/runtime.**

O commit funcional mais recente, `cb8e096`, foi uma correção da especificação contra PostgreSQL 16 descartável. Ele fechou três bloqueios que tinham aparecido na revisão:

### Bloqueio 1 — forward sem fonte real

Um estado forward não pode escapar carregando `source_id` sentinela como `NAO SEI`.

Regra corrigida: **todo estado que não seja `LEGACY_PRE_IDEMPOTENCY` precisa de fonte real**, usando o vocabulário de sentinelas já medido no repositório.

### Bloqueio 2 — `CONTENT_DERIVED`

A ordem antiga que aceitava `CONTENT_DERIVED` foi revogada/superseded. Não deixar duas regras executáveis contraditórias no documento.

### Bloqueio 3 — corte do legado por tempo

`created_at` foi reproduzido e **reprovou** como fronteira de legado, porque `now()` em PostgreSQL é `transaction_timestamp()` e uma transação antiga pode inserir depois do corte carregando um timestamp anterior.

A solução especificada e testada usa o surrogate:

- `ACCESS EXCLUSIVE` no início da fase de classificação;
- congela `max(raw_asset.id)` sob lock;
- ids até o corte recebem estado legado;
- writes concorrentes esperam ou são vistos antes do corte;
- depois a coluna de estado pode tornar-se obrigatória.

O commit reporta dois cenários concorrentes reproduzidos em PostgreSQL 16.13 e uma bateria final de **27 casos** com veredito esperado.

### Estado que continua aberto

`PHASE_10_UNPROVEN_GATE` continua **não resolvido**.

O índice parcial da fase 9 não protege observações `FORWARD_IDENTITY_UNPROVEN`. Hoje isso ainda não abre duplicação física porque `unique(raw_asset.storage_path)` permanece. Portanto:

- isso **não bloqueia automaticamente fases 7–9**;
- isso **bloqueia autorizar fase 10 sem uma decisão/prova adicional**.

Nunca confundir “B5B pronto para ser implementado” com “fase 10 autorizada”.

---

## 5. IDENTIDADE FORWARD — CONTRATO A PRESERVAR

### RUN_ID

- pertence à corrida criada pelo orquestrador antes do executor;
- o writer já recebe/persiste `run_id`;
- não criar segundo dono nem gerar novo RUN_ID no writer.

### SOURCE_ID

- autoridade = cadastro textual da Collection;
- exemplo: `IT-T2-002`;
- já existe upstream em `coleta/ingresso.py` / artefato de coleta;
- o gap medido era de **wiring** até o RAW writer, não de definição da identidade;
- nunca reconstruir SOURCE_ID a partir de URL, slug, owner, caminho ou `fonte_externa.id`.

### DOCUMENT_KEY

A especificação mais recente deve ser lida no documento canônico antes de implementar. Não ressuscitar uma regra revogada.

Princípio atual:

- documento identificado: identidade vem de `DOCUMENT_ID` semanticamente válido e provado pelo contrato da fonte;
- ausência de identidade documental provada não pode ser convertida silenciosamente em “documento identificado pelo hash”;
- estados forward precisam separar **identidade provada** de **identidade documental não provada**.

### Idempotência

Para observações forward identificadas, a distinção lógica continua baseada em:

`RUN + SOURCE + DOCUMENT + CONTENT`

Consequência essencial:

- mesma RUN + mesma identidade + mesmos bytes = retry/reuse;
- RUN diferente + mesma fonte/documento/bytes = observação diferente.

Mas **reconhecer chaves diferentes não significa ainda conseguir persistir as duas observações** enquanto `unique(raw_asset.storage_path)` existir.

---

## 6. SYSTEM MAP

Lei permanente:

- o mapa mostra o sistema; **não decide a arquitetura**;
- generated JSON é sempre mecânico;
- nunca editar `*.generated.json` à mão;
- nunca usar `--stamp` para mascarar árvore desatualizada;
- qualquer source tracked que altere a árvore exige regeneração pela cadeia canônica quando aplicável.

O HEAD `09277bf` regenerou a cadeia na ordem declarada:

`scan_repo → scan_sources → scan_casco → censo_da_coleta → pente_fino_da_coleta → censo_dos_buracos → generate_system_map`

O commit registra que alguns artefatos gerados carregavam provenance antiga porque rodadas anteriores haviam executado apenas parte da cadeia. O conteúdo semântico não mudou; a provenance foi atualizada mecanicamente.

Não herdar o estado dos checks de memória. **Remeça os checks no HEAD atual.**

---

## 7. REGRAS DE TRABALHO PARA A PRÓXIMA ABA

- Antes de qualquer conclusão sobre estado: `fetch`, branch, HEAD, status, log.
- Separar **fato medido** de inferência.
- Sem base: `NÃO SEI / precisa medir`.
- Não abrir auditoria repo-wide sem bloqueio concreto.
- Missões pequenas: **medir → decidir/implementar → hard stop**.
- Não criar arquitetura paralela para resolver detalhe local.
- `ONE CONCEPT → ONE OWNER`.
- `COLETAR ≠ ADMITIR ≠ JULGAR`.
- `RAW ≠ DERIVED ≠ STRUCTURED ≠ ADMISSION ≠ READY`.
- `MODULE EXISTS ≠ EDGE EXISTS ≠ FLOW EXISTS`.
- `CAN DO ≠ DID DO`.
- `DECLARED EDGE ≠ OBSERVED EDGE`.
- `ERROR ≠ REJECTED ≠ UNKNOWN ≠ NOT_RUN ≠ REUSED`.
- Intelligence pode pedir Collection Gap; não chama collector diretamente.
- Cards do System Map refletem runtime real, não arquitetura desejada.
- Sem portal/frontend/deploy durante esta fundação, salvo ordem explícita do usuário.

---

## 8. PRÓXIMO PASSO EXATO

A próxima aba **não deve começar implementando fase 10**.

Primeiro deve revisar criticamente o estado final de `cb8e096` + regeneração `09277bf` e responder:

1. os três bloqueios realmente ficaram fechados no documento canônico sem ordem contraditória sobrevivente?
2. o estado forward não consegue escapar silenciosamente por `NULL`/sentinela?
3. a fronteira de legado por surrogate + lock está especificada de forma implementável e compatível com os writers reais?
4. `CONTENT_DERIVED` está realmente revogado em todos os trechos executáveis da especificação?
5. o `PHASE_10_UNPROVEN_GATE` está explicitamente preservado como bloqueio futuro, sem ser resolvido por suposição?
6. quais checks estão verdes/vermelhos no HEAD atual, separando falhas preexistentes de regressões desta linha?

Se e somente se não houver bloqueio real, a próxima missão bounded é:

**`C-IMPL-B5B — implementar apenas fases 7–9`**

Ainda sem fase 10, sem remoção de `unique(raw_asset.storage_path)`, sem fase 11, sem portal.

Depois da implementação B5B deve existir uma rodada separada de prova/revisão antes de qualquer autorização destrutiva.

---

## 9. COMO REVISAR ENTREGAS DO CLAUDE

Fluxo combinado:

1. Claude Opus 5 executa a missão bounded.
2. Revisão independente procura apenas bloqueios reais, sem redesenhar arquitetura.
3. Verificação no GitHub confirma branch, HEAD, diff, migrations, provas, mapa e checks.
4. Veredito final: **PASS / PARTIAL / FAIL**.
5. Só então emitir o próximo prompt inteiro.

Pontos de revisão prioritários nesta linha:

- estabilidade de `raw_asset.id`;
- compatibilidade dos writers;
- diferença entre retry e reobservação;
- impossibilidade de histórico inventar identidade;
- forward não escapar de constraints por NULL/sentinela;
- índice parcial não prometer mais do que protege;
- prova real em PostgreSQL descartável quando a semântica depende do banco;
- nenhuma fase posterior entrar escondida no mesmo commit.

---

## EM PALAVRAS FÁCEIS

Estamos consertando a fundação da coleta antes de voltar a crescer o sistema.

A casa já aprendeu que **o arquivo guardado e o momento em que vimos esse arquivo são duas coisas diferentes**. Agora falta dar uma identidade segura para as observações novas, sem mentir sobre as antigas.

A especificação das fases 7–9 acabou de passar por uma correção importante: não usar relógio para separar passado/futuro, não aceitar fonte falsa e não transformar hash em identidade documental por conveniência.

O próximo passo é **revisar isso no GitHub e, se estiver realmente fechado, implementar só as fases 7–9**. A trava antiga de `storage_path` continua no lugar. Tirar essa trava é fase 10 e ainda não está autorizada.