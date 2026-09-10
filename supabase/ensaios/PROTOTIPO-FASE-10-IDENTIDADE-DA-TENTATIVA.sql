-- ═══════════════════════════════════════════════════════════════════════
-- PROTÓTIPO DA FASE 10 — E ELE NÃO É UMA MIGRATION.
--
--     NÃO EXECUTADA EM PRODUCAO
--     NAO E MIGRATION · NAO ENTRA NO LIVRO-RAZAO · NAO E APLICADA POR NINGUEM
--
-- Vive em `supabase/ensaios/` de propósito. O aplicador da casa
-- (`motor/cadeia_canonica.sh`) varre `supabase/migrations/*.sql` e mais nada;
-- um ficheiro aqui não pode ser aplicado por engano, e é por isso que a
-- preparação escreve aqui em vez de escrever uma `027` que ficaria à espera.
--
--     PROTOTIPO QUE MORA NA PASTA DAS MIGRATIONS E UMA MIGRATION
--     QUE AINDA NAO FOI APLICADA. E ISSO NAO E UM PROTOTIPO.
--
-- O NÚMERO QUE A FASE 10 VAI USAR, quando for autorizada: `027`. Medido, e não
-- assumido — 026 é o maior no repositório, o maior no livro-razão do vivo e o
-- maior em TODAS as branches remotas (varridas uma a uma).
--
-- O QUE ISTO PROPÕE, E PORQUÊ
-- ---------------------------
-- Depois da 026 a observação tem estado, e a idempotência forward tem índice.
-- Falta a espécie: `unique (raw_asset.storage_path)` continua de pé, e enquanto
-- estiver, duas observações no mesmo endereço são UMA.
--
--     OBSERVAÇÃO   um facto sobre o mundo, com corrida e hora
--     OBJETO       uma cópia guardada, com endereço
--
-- Uma corrida nova que reencontra o mesmo documento faz uma observação NOVA.
-- Hoje ela é recusada — medido em `provas/a_lei_da_fase_10.py`, caso `C2`:
--
--     C2_A_OBSERVACAO_NOVA_ENTRA = NAO
--     C2_QUEM_A_IMPEDE           = raw_asset_storage_path_key
--
-- ⚠️ A ORDEM NÃO É NEGOCIÁVEL, E É POR ISSO QUE ISTO NÃO É APLICÁVEL HOJE.
-- O passo 1 abaixo faz `on conflict (storage_path)` DEIXAR DE PLANEAR — não
-- de correr: de planear. Medido:
--
--     H_ON_CONFLICT_STORAGE_PATH_DEIXA_DE_PLANEAR = SIM
--     erro: there is no unique or exclusion constraint matching the
--           ON CONFLICT specification
--
-- Quem depende disso hoje, contado no repositório:
--
--     supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql   138 inserts
--     guarda/catalogo_importar.py                               1 emissor
--     .github/workflows/supabase-raw-roundtrip.yml              1 emissor
--     .github/workflows/supabase-fichas-adama.yml               1 emissor
--
-- Os quatro estão atrás de `guarda/trava_do_escritor_antigo.sh` desde a
-- `C-PREP-026`, e a trava recusa-os num banco pós-026. Logo eles não partem
-- em produção — mas continuam no repositório a dizer uma lei que deixou de
-- valer, e isso é dívida, não segurança.
-- ═══════════════════════════════════════════════════════════════════════

begin;

-- ── PASSO 1 · o endereço deixa de ser identidade ────────────────────────
-- `ACCESS EXCLUSIVE` na tabela inteira. Medido: um escritor a meio de uma
-- transacção põe este DDL à espera, e ele só passa depois do `commit` dele
-- (`L5_O_DDL_ESPERA_PELO_ESCRITOR = 1`). Numa tabela de 252 linhas isso é
-- instantâneo; a espera é pelo LOCK, não pelo tamanho.
alter table public.raw_asset
  drop constraint raw_asset_storage_path_key;

-- ── PASSO 2 · a identidade da TENTATIVA, para quem não tem a do documento ──
-- Sem isto, o `FORWARD_IDENTITY_UNPROVEN` fica sem chave nenhuma e duplica
-- sem limite — medido em `H_O_UNPROVEN_DUPLICA_SEM_LIMITE = SIM` e outra vez,
-- com duas sessões concorrentes, em `L2_DUAS_SESSOES_DUPLICAM_O_UNPROVEN = 2`.
--
-- A CHAVE FOI ESCOLHIDA POR MEDIÇÃO, e não por gosto. Cinco candidatas
-- passaram pelos mesmos cinco cenários, cada uma instalada como índice a
-- sério (`provas/a_lei_da_fase_10.py`, parte E):
--
--     K1 (run, fonte, sha256)              REPROVADA — junta o caso ADAMA
--     K3 (fonte, sha256)                   REPROVADA — apaga a corrida nova
--     K2 (run, fonte, endereço)            APROVADA
--     K4 (run, fonte, endereço, sha256)    APROVADA
--
-- K1 morre no contraexemplo que esta casa mediu nos 195 objectos italianos: a
-- ADAMA publicou o MESMO PDF em `media/731` e em `media/6321`. Dois factos
-- sobre o mundo, um conteúdo só. Uma chave derivada do conteúdo faz deles um.
--
--     O CONTEUDO NAO E O DOCUMENTO. NUNCA FOI.
--
-- Entre K2 e K4 fica K4: `sha256` não separa nada que o endereço já não
-- separe HOJE, mas o endereço escrito na linha PODE divergir do endereço do
-- objecto que ela aponta (medido:
-- `F_O_ENDERECO_DA_LINHA_PODE_DIVERGIR_DO_OBJETO = SIM`), e nesse dia o
-- `sha256` é a única coisa na chave que ainda fala do conteúdo.
create unique index raw_tentativa_sem_prova_idx
  on public.raw_asset (run_id, source_id, storage_path, sha256)
  where identity_state = 'FORWARD_IDENTITY_UNPROVEN';

-- ── PASSO 3 · o passado não se reescreve ────────────────────────────────
-- Medido: hoje NADA no esquema impede um `update` de promover uma observação
-- SEM PROVA a IDENTIFICADA (`S3 · UPDATE que promove: ACEITE`). Isso diz, em
-- retrospectiva, que se sabia a chave quando não se sabia.
--
--     UMA OBSERVACAO E UM FACTO SOBRE UM MOMENTO.
--     UM FACTO SOBRE UM MOMENTO NAO MELHORA COM O TEMPO.
--
-- Quando uma corrida futura PROVAR a chave, ela escreve uma observação NOVA,
-- `FORWARD_IDENTIFIED`. A antiga fica como está: sem prova, porque não havia.
create or replace function public.o_estado_da_identidade_nao_recua()
returns trigger language plpgsql as $$
begin
  if old.identity_state is distinct from new.identity_state then
    raise exception 'FASE 10: o estado de identidade de uma observacao nao '
                    'se reescreve (% -> %). Uma corrida que PROVE a chave '
                    'escreve uma observacao nova.',
                    old.identity_state, new.identity_state;
  end if;
  return new;
end $$;

create trigger identidade_da_observacao_nao_recua
  before update on public.raw_asset
  for each row execute function public.o_estado_da_identidade_nao_recua();

commit;

-- ═══════════════════════════════════════════════════════════════════════
-- O QUE ESTE PROTÓTIPO **NÃO** RESOLVE, e por isso a fase 10 não está pronta
-- -----------------------------------------------------------------------
--
-- 1. `guarda/preservar_coleta.py` lê o banco ANTES de escrever, e lê POR
--    ENDEREÇO: `objeto_em(storage_path)` faz `linhas[0] if linhas else None`.
--    Com o `unique` de pé isso é uma linha. Sem ele são N, e a função escolhe
--    UMA em silêncio — a que o planeador devolver primeiro. Medido:
--    `J_OBJETO_EM_ENDERECO_DEIXA_DE_SER_UMA_LINHA = 2`.
--    Isto é código, não esquema. Nenhum `alter table` o cura.
--
-- 2. O `on conflict` do escritor não vê a linha SEM PROVA — o índice da fase 9
--    tem predicado `FORWARD_IDENTIFIED`, e a linha não o satisfaz. Medido:
--    `J_O_ON_CONFLICT_DO_ESCRITOR_NAO_VE_O_UNPROVEN = SIM`. O escritor precisa
--    de um segundo `on conflict`, contra o índice do passo 2.
--
-- 3. `attempts` e `last_attempt_at` nasceram na 026 e continuam SEM ESCRITOR.
--    Se a resposta a «a mesma tentativa outra vez» é contar tentativas numa
--    linha, alguém tem de as contar. Ninguém conta.
--
-- 4. O ENDEREÇO É FABRICADO quando a fonte não dá identificador nativo.
--    `coleta/ingresso.py:215` cai para `f.SHA256[:16]`, e aí o discriminante
--    do caminho passa a ser o próprio conteúdo. Medido pelo código de
--    produção, com dois ficheiros distintos de conteúdo igual e mesmo nome:
--
--        com id nativo   XX/…/0b5c068c31e225fe-media-731-FDS.pdf
--                        XX/…/0b5c068c31e225fe-media-6321-FDS.pdf   SEPARADOS
--        sem id nativo   XX/…/0b5c068c31e225fe-0b5c068c31e225fe-FDS.pdf
--                        XX/…/0b5c068c31e225fe-0b5c068c31e225fe-FDS.pdf  COLIDEM
--
--    O passo 2 põe o endereço numa chave. O endereço só vale o que vale o
--    discriminante — e este é inventado por nós quando a fonte cala. A cura é
--    a montante, em `ingresso.py`, e não neste ficheiro.
--
-- 5. Os quatro emissores de `on conflict (storage_path)` (138 inserts + 3
--    emissores) partem no PASSO 1. Estão travados, não estão curados.
--
-- 6. Dois workflows lêem `where storage_path = '…'` esperando UMA linha
--    (`supabase-raw-roundtrip.yml`, `supabase-fichas-adama.yml`). Com N
--    observações no mesmo endereço a comparação de shell deixa de fazer
--    sentido.
--
-- CONSEQUÊNCIA MEDIDA QUE NÃO É DEFEITO, MAS TEM DE SER DITA
-- ----------------------------------------------------------
-- A derivação é por CONTEÚDO (`derivacao_e_unica_por_regua` tem
-- `parent_sha256` na chave, não `raw_asset_id`). Com duas observações dos
-- mesmos bytes, a segunda NÃO tem filhos próprios — o segundo derivado é
-- recusado por `derivacao_e_unica_por_regua`. Isso está certo (derivar duas
-- vezes os mesmos bytes com a mesma régua daria o mesmo ficheiro), mas quem
-- ler «observação sem derivados» como falha vai ler mal.
--
--     READY_FOR_PHASE_10_LIVE = NO
-- ═══════════════════════════════════════════════════════════════════════
