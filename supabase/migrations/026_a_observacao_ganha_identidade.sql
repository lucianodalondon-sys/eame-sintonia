-- ═══════════════════════════════════════════════════════════════════════
-- 026 · A OBSERVAÇÃO GANHA IDENTIDADE — fases 7, 8 e 9, e nem uma a mais
--
-- A 025 separou o OBJETO da OBSERVAÇÃO. Faltava a observação saber DE QUEM e
-- DE QUE ela é: a cópia tem endereço, mas o facto não tinha nome.
--
--     CONTEÚDO ≠ CÓPIA ≠ OBSERVAÇÃO
--     sha256     storage_path   (run_id, source_id, document_key, sha256)
--
-- Plano fechado em docs/operacao/CIRURGIA-OBJETO-E-OBSERVACAO.md. A secção
-- executável é a **T · C-CORR-B5B2**; os blocos marcados REVOKED/SUPERSEDED
-- nas secções R e S NÃO são instruções e não estão aqui.
--
-- O QUE ESTA MIGRATION NÃO FAZ, E NÃO É ESQUECIMENTO
--
--     FASE 10   retirar `unique (raw_asset.storage_path)`   NÃO ENTRA
--     FASE 11   retirar `raw_asset.storage_path`            NÃO ENTRA
--
-- Depois desta migration continua verdadeiro que uma corrida NOVA sobre o
-- MESMO conteúdo ainda não entra: a trava física antiga continua de pé, e é
-- de propósito. As duas identidades convivem por um tempo.
--
--     NEW_RUN_SAME_CONTENT_RESOLVED = NO
--
-- NAO EXECUTADA EM PRODUCAO. Aplicada e conferida num PostgreSQL 16
-- descartavel, por `provas/objeto_e_observacao_no_postgres.py` — incluindo os
-- dois cenarios de concorrencia da fase 8 e a precondicao da sequencia.
-- Aplicar em producao continua a ser trabalho de outra missao, com
-- autorizacao propria.
-- ═══════════════════════════════════════════════════════════════════════


-- ── FASE 7 · AS COLUNAS, TODAS ANULÁVEIS E NENHUMA COM DEFAULT ─────────
--
-- `identity_state` nasce anulável porque `ADD COLUMN ... NOT NULL` sem
-- `DEFAULT` não corre sobre tabela povoada. A janela em que ele o é fecha na
-- fase 8, e fecha ANTES do índice da fase 9.
--
-- ⚠️ E NUNCA GANHA `DEFAULT`. O default seria a porta de fuga: com ele,
-- esquecer a coluna passaria a CLASSIFICAR a linha em silêncio. Sem ele,
-- esquecer a coluna é erro do banco — que é o que tem de ser.
alter table public.raw_asset
  add column if not exists source_id           text,
  add column if not exists document_key        text,
  add column if not exists document_key_basis  text,
  add column if not exists identity_state      text,
  add column if not exists attempts            integer,
  add column if not exists last_attempt_at     timestamptz;

comment on column public.raw_asset.source_id is
  'O CÓDIGO TEXTUAL da fonte na Collection — IT-T2-002. NÃO é fonte_externa.id, '
  'que é um surrogate indexado por URL, e NÃO se deriva de SOURCE_SLUG: o slug é '
  'endereço, e it-t2-002 não se reconverte em IT-T2-002 sem adivinhar.';

comment on column public.raw_asset.document_key is
  'O DOCUMENT_ID provado pelo contrato da fonte. Não existe queda para o hash: '
  'bytes iguais não provam unidade documental igual — a ADAMA publicou o mesmo '
  'PDF sob media/731 e media/6321. Sem identidade provada, fica NULL e o estado '
  'diz FORWARD_IDENTITY_UNPROVEN.';

comment on column public.raw_asset.document_key_basis is
  'SOURCE_DOCUMENT_ID, e mais nada. CONTENT_DERIVED foi REVOGADO na S.4.';

comment on column public.raw_asset.identity_state is
  'LEGACY_PRE_IDEMPOTENCY | FORWARD_IDENTIFIED | FORWARD_IDENTITY_UNPROVEN. '
  'NOT NULL e SEM DEFAULT depois da fase 8: omitir a coluna é erro, nunca uma '
  'classificação por omissão.';

comment on column public.raw_asset.attempts is
  'TELEMETRIA, e fora da chave de idempotência. Anulável de propósito: não se '
  'escreve 1 só porque houve sucesso — pode ter havido retry antes, e o coletor '
  'italiano deita fora o número no instante do sucesso.';

comment on column public.raw_asset.last_attempt_at is
  'TELEMETRIA. Mesma regra: sem prova, NULL. Não é CAPTURED_AT.';


-- ── FASE 7 · AS TRAVAS, INSTALADAS `NOT VALID` ─────────────────────────
-- Valem já para o que vier a seguir; a validação sobre o que já lá estava é
-- da fase 8, depois de o legado estar classificado.
do $$
begin
  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.raw_asset'::regclass
                    and conname = 'estado_de_identidade_tem_vocabulario') then
    alter table public.raw_asset
      add constraint estado_de_identidade_tem_vocabulario
      check (identity_state in ('LEGACY_PRE_IDEMPOTENCY',
                                'FORWARD_IDENTIFIED',
                                'FORWARD_IDENTITY_UNPROVEN')) not valid;
  end if;

  -- ⚠️ ESCRITO COMO «= LEGADO or fonte real», E NÃO COMO «<> FORWARD_*».
  -- A diferença decide o futuro: assim, qualquer estado que venha a nascer cai
  -- DENTRO da exigência de fonte real. Só o legado — o único com licença para
  -- não ter identidade — fica de fora, e fica de fora POR NOME.
  --
  --     «não sei qual documento»  !=  «não sei que fonte pedi»
  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.raw_asset'::regclass
                    and conname = 'fonte_real_em_qualquer_estado_forward') then
    alter table public.raw_asset
      add constraint fonte_real_em_qualquer_estado_forward
      check (identity_state = 'LEGACY_PRE_IDEMPOTENCY'
             or (source_id is not null and btrim(source_id) <> ''
                 and upper(btrim(source_id)) not in
                     ('NAO SEI','NAO_SEI','NÃO SEI','NAO_SE_APLICA',
                      'UNKNOWN','NOT_KNOWN'))) not valid;
  end if;

  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.raw_asset'::regclass
                    and conname = 'forward_identificado_exige_identidade') then
    alter table public.raw_asset
      add constraint forward_identificado_exige_identidade
      check (identity_state <> 'FORWARD_IDENTIFIED'
             or (document_key is not null and btrim(document_key) <> ''
                 and upper(btrim(document_key)) not in
                     ('NAO SEI','NAO_SEI','NÃO SEI','NAO_SE_APLICA',
                      'UNKNOWN','NOT_KNOWN')
                 and document_key_basis is not null)) not valid;
  end if;

  -- Uma confissão preenchida é pior do que um campo vazio quando há índice em
  -- cima: `source_id = 'NAO SEI'` juntaria observações de fontes diferentes
  -- debaixo de uma palavra que quer dizer «não sei qual».
  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.raw_asset'::regclass
                    and conname = 'forward_sem_prova_nao_finge_chave') then
    alter table public.raw_asset
      add constraint forward_sem_prova_nao_finge_chave
      check (identity_state <> 'FORWARD_IDENTITY_UNPROVEN'
             or (document_key is null and document_key_basis is null)) not valid;
  end if;

  -- CONTENT_DERIVED não é «a base com a chave errada»: é o valor que não
  -- existe. Por isso o check não olha para `document_key` — olhar sugeriria
  -- que há uma forma certa de o escrever.
  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.raw_asset'::regclass
                    and conname = 'base_da_chave_tem_vocabulario') then
    alter table public.raw_asset
      add constraint base_da_chave_tem_vocabulario
      check (document_key_basis is null
             or document_key_basis = 'SOURCE_DOCUMENT_ID') not valid;
  end if;
end $$;


-- ── FASE 7b · A OBSERVAÇÃO E A CÓPIA TÊM DE FALAR DO MESMO CONTEÚDO ────
--
-- A 025 ligou a observação ao objeto por uma chave estrangeira SIMPLES, para
-- `storage_object(id)`. Com ela, isto entrava:
--
--     raw_asset.sha256 = H1   ->   storage_object.sha256 = H2
--
-- A FK passava (o objeto existe) e o CHECK de formato passava (H1 tem cara de
-- sha). A linha ficava a dizer duas coisas ao mesmo tempo.
--
-- ESTA CASA JÁ APANHOU ESTE DEFEITO UMA VEZ. Está escrito na 022, sobre o
-- derivado: «FK EXISTIR NÃO BASTA». O conserto é o mesmo padrão.
--
-- E o `unique (id, sha256)` NÃO torna `sha256` único no objeto: dois objetos
-- podem carregar os mesmos bytes, e o caso ADAMA é exactamente esse.
do $$
begin
  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.storage_object'::regclass
                    and conname = 'objeto_id_e_sha_juntos') then
    alter table public.storage_object
      add constraint objeto_id_e_sha_juntos unique (id, sha256);
  end if;

  -- MATCH SIMPLE (o padrão): com `storage_object_id` nulo a chave não é
  -- cobrada, e é isso que se quer — uma observação NÃO PRESERVADA não tem
  -- cópia para apontar. `sha256` é NOT NULL desde a 001, logo o único nulo
  -- possível é o do lado do objeto.
  if not exists (select 1 from pg_constraint
                  where conrelid = 'public.raw_asset'::regclass
                    and conname = 'a_observacao_e_a_copia_falam_do_mesmo_conteudo') then
    alter table public.raw_asset
      add constraint a_observacao_e_a_copia_falam_do_mesmo_conteudo
      foreign key (storage_object_id, sha256)
      references public.storage_object(id, sha256) on delete restrict not valid;
  end if;
end $$;

comment on constraint objeto_id_e_sha_juntos on public.storage_object is
  'Não é regra nova: (id, sha256) já era único porque id é chave primária. '
  'Existe para que raw_asset possa exigir, por chave estrangeira COMPOSTA, que '
  'o objeto apontado por ID e o conteúdo declarado por SHA sejam o MESMO. '
  'NÃO torna sha256 único: dois objetos com os mesmos bytes continuam legais.';


-- ═══════════════════════════════════════════════════════════════════════
-- FASE 8 · FECHAR O LEGADO — NUMA JANELA SÓ, E SOB LOCK
--
-- Tudo num `DO` porque um bloco `DO` é UMA instrução: não há janela entre
-- classificar e `SET NOT NULL`, e o lock é largado só no fim, aconteça o que
-- acontecer.
--
-- O CORTE NÃO É UM RELÓGIO, E ISSO FOI MEDIDO
--
--     A proposta anterior usava `created_at < corte`. Reprovou em PostgreSQL
--     16.13: `now()` é `transaction_timestamp()`, logo uma transação aberta
--     ANTES do corte carrega a hora de abertura para dentro de um INSERT feito
--     DEPOIS dele, e a linha futura declara-se legado com a trava a aplaudir.
--     `clock_timestamp()` também não salva — a coluna tem DEFAULT, e quem
--     escreve escolhe o valor.
--
--         UM RELÓGIO QUE A LINHA CARREGA NÃO DATA A LINHA CONTRA ELA PRÓPRIA.
--
--     O corte é o SURROGATE: um número que já não pode ser sorteado outra vez.
-- ═══════════════════════════════════════════════════════════════════════
do $$
declare
  seq         text;
  ultimo      bigint;
  chamada     boolean;
  incremento  bigint;
  proximo     bigint;
  corte       bigint;
  restantes   bigint;
begin
  -- O CORTE CONGELA-SE UMA VEZ E NUNCA MAIS. Recalculá-lo numa segunda corrida
  -- desta migration legitimaria como «legado» tudo o que entrou entretanto.
  if exists (select 1 from pg_constraint
              where conrelid = 'public.raw_asset'::regclass
                and conname = 'legado_e_anterior_ao_corte') then
    raise notice 'B5B fase 8 JA CORRIDA — o corte do legado nao se recalcula.';
    return;
  end if;

  -- 1 · FECHAR A PORTA. `ACCESS EXCLUSIVE` conflitua com o `ROW EXCLUSIVE` que
  --     todo INSERT toma, e é o mesmo que os ALTER seguintes iriam tomar de
  --     qualquer maneira. Tomá-lo UMA VEZ no topo evita a subida de lock a
  --     meio da transação, que é onde nascem deadlocks.
  lock table public.raw_asset in access exclusive mode;

  -- 2 · A PRECONDIÇÃO DA SEQUÊNCIA, MEDIDA SOB O LOCK
  --
  --     «A sequência só anda para a frente» NÃO chega. Se um restauro ou uma
  --     escrita manual deixou a sequência ATRÁS do maior id existente, o
  --     próximo id natural cairia dentro do conjunto congelado — e o corte
  --     deixaria de significar «anterior à lei».
  --
  --     Aqui NÃO se conserta a sequência. Mexer nela para caber a migration
  --     seria consertar o instrumento para a medição dar certo. FAIL CLOSED.
  seq := pg_get_serial_sequence('public.raw_asset', 'id');
  if seq is null then
    raise exception
      'B5B FAIL CLOSED: raw_asset.id nao tem sequencia identificavel. Sem ela '
      'nao se prova que um id futuro cai fora do corte do legado.';
  end if;

  select seqincrement into incremento
    from pg_sequence where seqrelid = seq::regclass;
  if incremento is null or incremento <= 0 then
    raise exception
      'B5B FAIL CLOSED: a sequencia % tem incremento %, que nao garante '
      'numeros crescentes.', seq, incremento;
  end if;

  -- `is_called` é a metade que `pg_sequences.last_value` sozinho não dá: com
  -- ele falso, o PRÓXIMO valor é o próprio `last_value`, e não `last + inc`.
  execute format('select last_value, is_called from %s', seq)
     into ultimo, chamada;
  proximo := case when chamada then ultimo + incremento else ultimo end;

  select coalesce(max(id), 0) into corte from public.raw_asset;

  if proximo <= corte then
    raise exception
      'B5B FAIL CLOSED: o proximo id natural (%) nao e maior que o corte do '
      'legado (%). A sequencia % ficou atras da tabela, e um INSERT futuro '
      'poderia nascer dentro do conjunto congelado como legado. Corrigir a '
      'sequencia e decisao humana, fora desta migration.',
      proximo, corte, seq;
  end if;

  -- 3 · CLASSIFICAR. Tudo o que existe neste instante é anterior à lei.
  --     NÃO se preenche source_id, document_key nem basis por inferência:
  --     `adama-website` é uma ORGANIZAÇÃO e não um código de fonte, e
  --     `media/<n>` não é DOCUMENT_ID sem contrato que o prove.
  update public.raw_asset
     set identity_state = 'LEGACY_PRE_IDEMPOTENCY'
   where identity_state is null;

  -- 4 · A TRAVA, COM LITERAL CONSTANTE. Sem função, sem relógio, sem nada que
  --     possa devolver outra resposta amanhã.
  execute format(
    'alter table public.raw_asset add constraint legado_e_anterior_ao_corte '
    'check (identity_state <> %L or id <= %s) not valid',
    'LEGACY_PRE_IDEMPOTENCY', corte);

  -- 5 · VALIDAR TUDO, agora que o legado tem nome
  execute 'alter table public.raw_asset validate constraint legado_e_anterior_ao_corte';
  execute 'alter table public.raw_asset validate constraint estado_de_identidade_tem_vocabulario';
  execute 'alter table public.raw_asset validate constraint fonte_real_em_qualquer_estado_forward';
  execute 'alter table public.raw_asset validate constraint forward_identificado_exige_identidade';
  execute 'alter table public.raw_asset validate constraint forward_sem_prova_nao_finge_chave';
  execute 'alter table public.raw_asset validate constraint base_da_chave_tem_vocabulario';
  execute 'alter table public.raw_asset validate constraint a_observacao_e_a_copia_falam_do_mesmo_conteudo';

  -- 6 · FECHAR O ESTADO. Sem DEFAULT, e é isso que faz do esquecimento um erro.
  execute 'alter table public.raw_asset alter column identity_state set not null';

  select count(*) into restantes
    from public.raw_asset where identity_state is null;
  if restantes <> 0 then
    raise exception 'B5B FAIL CLOSED: % linha(s) ficaram sem estado.', restantes;
  end if;

  raise notice 'B5B fase 8: LEGACY_CUTOFF_ID = % · proximo id natural = % · sequencia = %',
               corte, proximo, seq;
end $$;

comment on constraint legado_e_anterior_ao_corte on public.raw_asset is
  'LEGADO É UM FACTO SOBRE QUANDO A LINHA NASCEU, não uma etiqueta escolhível. '
  'O número foi congelado sob ACCESS EXCLUSIVE e é um literal: nenhuma linha '
  'futura o alcança pelo caminho natural, porque nenhum emissor desta casa '
  'escreve raw_asset.id — a sequência é que o dá, e ela só anda para a frente.';


-- ── FASE 9 · O ÍNDICE ÚNICO PARCIAL DA IDENTIDADE FORWARD ──────────────
--
-- Quatro colunas, e nem uma a mais. `storage_path`, `source_url`,
-- `captured_at` e `DOCUMENT_VERSION_ID` NÃO entram: um retry da mesma corrida
-- pode trazer outra hora e outra URL e continua a ser a MESMA observação.
--
-- Exclui por ESTADO, e nunca por «onde o campo é nulo». Excluir por nulo
-- deixaria uma observação forward escapar da proteção por esquecimento;
-- excluir por estado obriga a linha a DECLARAR-SE, e nenhum esquecimento
-- declara nada. Dentro do predicado as quatro colunas são todas não-nulas:
-- `run_id` e `sha256` desde a 001, `source_id` e `document_key` pelos checks
-- acima — por isso `NULLS NOT DISTINCT` não muda um único resultado e não entra.
create unique index if not exists raw_identidade_forward_idx
  on public.raw_asset (run_id, source_id, document_key, sha256)
  where identity_state = 'FORWARD_IDENTIFIED';

comment on index public.raw_identidade_forward_idx is
  'A CHAVE DE IDEMPOTÊNCIA: (RUN_ID, SOURCE_ID, DOCUMENT_KEY, CONTENT_SHA256). '
  'Retry da mesma corrida = mesma chave = mesma observação. Corrida NOVA = chave '
  'nova = observação nova — que ainda NÃO entra fisicamente, porque '
  'unique (raw_asset.storage_path) continua de pé e só cai na fase 10.';
