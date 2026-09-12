-- ═══════════════════════════════════════════════════════════════════════
-- 027 · A OBSERVAÇÃO DEIXA DE SER O ENDEREÇO — a fase 10, e nem uma a mais
--
-- A 025 separou o OBJETO da OBSERVAÇÃO. A 026 deu identidade à observação.
-- E as duas deixaram de pé, de propósito, a trava que voltava a juntá-las:
--
--     unique (raw_asset.storage_path)
--
-- Enquanto ela existir, DUAS OBSERVAÇÕES NO MESMO ENDEREÇO SÃO UMA — e isso
-- contradiz a espécie que as duas migrations anteriores escreveram.
--
--     OBSERVAÇÃO   um facto sobre o mundo, com corrida e hora
--     OBJETO       uma cópia guardada, com endereço
--
-- Uma corrida nova que reencontra o mesmo documento faz uma OBSERVAÇÃO NOVA.
-- Medido antes desta migration, em `provas/a_lei_da_fase_10.py`, caso `C2`:
--
--     C2_A_OBSERVACAO_NOVA_ENTRA = NAO
--     C2_QUEM_A_IMPEDE           = raw_asset_storage_path_key
--
-- A LEI QUE ESTA MIGRATION MATERIALIZA NÃO NASCE AQUI. Ela foi medida na
-- `C-PREP-PHASE-10` e o runtime foi preparado na `C-CLOSE-PHASE-10-BLOCKERS`.
-- A secção executável é a **X** de docs/operacao/CIRURGIA-OBJETO-E-OBSERVACAO.md;
-- as secções anteriores contêm blocos REVOKED/SUPERSEDED que NÃO são
-- instruções e não estão aqui.
--
-- O QUE ESTA MIGRATION NÃO FAZ, E NÃO É ESQUECIMENTO
--
--     FASE 11   retirar a COLUNA `raw_asset.storage_path`      NÃO ENTRA
--
-- O endereço deixa de ser IDENTIDADE e continua a ser ENDEREÇO. A coluna fica,
-- e nada aqui a antecipa: a chave da fase 10 já não depende dela — foi escolhida
-- assim exactamente para que a fase 11 não tenha de a desfazer.
--
-- E O QUE CONTINUA VERDADEIRO, PORQUE NADA AQUI LHE TOCA
--
--     RAW_OBSERVATION_ID = raw_asset.id      nenhum id muda
--     LEGACY continua LEGACY                 o corte da 026 fica como está
--     SOURCE_ID não se reconstrói            nenhum `update` de identidade aqui
--     DOCUMENT_ID não se deriva de sha/path/URL
--     FORWARD_IDENTIFIED mantém a chave da 026
--     storage_object continua dono do objeto físico
--
-- NAO EXECUTADA EM PRODUCAO. Aplicada e conferida num PostgreSQL 16
-- descartavel, pelo aplicador canonico da casa (`motor/cadeia_canonica.sh`),
-- sobre um acervo com a FORMA do vivo — 252 observacoes legadas, ids esparsos
-- ate 890, corte instalado. Aplicar em producao continua a ser trabalho de
-- outra missao, com autorizacao propria: `C-LIVE-PHASE-10`.
-- ═══════════════════════════════════════════════════════════════════════


-- ── FASE 10a · O ENDEREÇO DEIXA DE SER IDENTIDADE DA OBSERVAÇÃO ────────
--
-- `ACCESS EXCLUSIVE` na tabela inteira, e é o que se quer: enquanto esta
-- transacção corre, nenhum escritor entra. Não há um instante em que o
-- endereço já não trave e a chave da tentativa ainda não exista — as três
-- fases estão na MESMA transacção, e o aplicador da casa corre o ficheiro
-- com `--single-transaction`.
--
--     UMA MIGRATION ENTRA INTEIRA, OU NAO ENTRA.
--
-- Numa tabela de 252 linhas a espera é pelo LOCK, nunca pelo tamanho.
--
-- `if exists` para que uma segunda corrida não rebente. O livro-razão já
-- impede a reaplicação; isto é o cinto por baixo dos suspensórios, e custa
-- uma palavra.
alter table public.raw_asset
  drop constraint if exists raw_asset_storage_path_key;


-- ── FASE 10b · A IDENTIDADE DA TENTATIVA ───────────────────────────────
--
-- Sem isto, a fase 10a abriria um buraco em vez de uma porta. O índice da
-- fase 9 tem predicado `FORWARD_IDENTIFIED`; uma observação SEM PROVA não o
-- satisfaz, e por isso ela não tinha chave nenhuma. Enquanto o endereço foi
-- único, era ELE que a segurava por acidente. Tirá-lo sem pôr isto deixaria
-- o `FORWARD_IDENTITY_UNPROVEN` a duplicar a cada retry — medido:
--
--     H_O_UNPROVEN_DUPLICA_SEM_LIMITE = SIM
--     L2_DUAS_SESSOES_DUPLICAM_O_UNPROVEN = 2
--
-- SEIS CANDIDATAS, DEZ CENÁRIOS, CADA UMA INSTALADA COMO ÍNDICE A SÉRIO:
--
--     K1 (run, fonte, sha256)              REPROVADA — junta o caso ADAMA
--     K3 (fonte, sha256)                   REPROVADA — apaga a corrida nova
--     K2 (run, fonte, endereço)            passa tudo, e MORRE na fase 11
--     K4 (run, fonte, endereço, sha256)    passa tudo, e MORRE na fase 11
--     K5 (run, fonte, objeto)              REPROVADA — sem objeto, não constrange
--     K6 (run, fonte, objeto, sha256)      APROVADA, com `nulls not distinct`
--
-- `K1` é a que qualquer um escreveria primeiro, e morre no contraexemplo que
-- esta casa MEDIU nos 195 objetos italianos: a ADAMA publicou o MESMO PDF em
-- `media/731` e em `media/6321`. Dois factos sobre o mundo, um conteúdo só.
--
--     O CONTEUDO NAO E O DOCUMENTO. NUNCA FOI.
--
-- ⚠️ E É `storage_object_id`, E NÃO `storage_path`. As duas separam os mesmos
-- casos hoje. A diferença é a fase 11, que retira o endereço de `raw_asset`:
-- uma chave construída sobre ele nasceria com dívida marcada. O objeto é a
-- espécie certa para responder «que cópia física foi esta».
--
-- ⚠️ `NULLS NOT DISTINCT` NÃO É AFINAÇÃO. Uma observação NÃO preservada tem
-- `storage_object_id` nulo — `preserved = false` é estado legítimo, e a trava
-- `preservado_aponta_para_a_copia` da 025 já o previa. Em Postgres dois nulos
-- são DISTINTOS num índice único: sem esta cláusula a chave deixaria passar
-- TODAS as tentativas não preservadas, em silêncio. `K5` reprova exactamente
-- nesse cenário, e a única diferença entre `K5` e `K6` aprovada é esta.
--
-- `if not exists` pela mesma razão do `if exists` acima.
create unique index if not exists raw_tentativa_sem_prova_idx
  on public.raw_asset (run_id, source_id, storage_object_id, sha256)
  nulls not distinct
  where identity_state = 'FORWARD_IDENTITY_UNPROVEN';


-- ── FASE 10c · A AFIRMAÇÃO DE IDENTIDADE NÃO SE REESCREVE ──────────────
--
-- Medido antes desta migration: NADA no esquema impedia um `update` de
-- promover uma observação sem prova a identificada, nem de lhe trocar a
-- fonte, a chave, a base da chave, a corrida, o conteúdo ou a cópia.
--
--     S3 · UPDATE que promove: ACEITE — o esquema NAO o proibe
--
-- Isso diz, em retrospectiva, que se sabia o que não se sabia.
--
--     UMA OBSERVACAO E UM FACTO SOBRE UM MOMENTO.
--     UM FACTO SOBRE UM MOMENTO NAO MELHORA COM O TEMPO.
--
-- Quando uma corrida futura PROVAR a chave, ela escreve uma observação NOVA,
-- `FORWARD_IDENTIFIED`. A antiga fica como está: sem prova, porque não havia.
--
-- OS CAMPOS CONGELADOS SÃO SETE, e a regra que os escolhe cabe numa frase:
-- **a afirmação de identidade, mais tudo o que as duas chaves de idempotência
-- usam.** Nada mais — congelar por medo fecharia o que tem de mudar.
--
--     identity_state  source_id  document_key  document_key_basis   a afirmação
--     run_id  sha256  storage_object_id                             as chaves
--
-- E `storage_path` NÃO ESTÁ NA LISTA. Essa ausência é a prova de coerência do
-- desenho inteiro: ele é ENDEREÇO, e um endereço pode mudar sem que o facto
-- mude. Se estivesse aqui, a fase 11 teria de o descongelar.
--
-- O QUE CONTINUA A PODER MUDAR, e tem de poder:
--     attempts · last_attempt_at          a contagem da tentativa
--     preserved · not_preserved_reason    o byte pode chegar depois
--     source_url · media_type · bytes · captured_at · storage_path
--
-- ⚠️ E NÃO HÁ PORTA DE FUGA POR DENTRO. Uma migration futura que precise
-- mesmo de tocar num destes campos tem de escrever
-- `alter table public.raw_asset disable trigger …` com todas as letras — o que
-- fica no ficheiro, no `sha256` dele e no livro-razão. Uma exceção silenciosa
-- dentro do gatilho seria a mesma coisa sem o registo.
create or replace function public.a_identidade_da_observacao_nao_se_reescreve()
returns trigger language plpgsql as $$
declare
  mudou text;
begin
  select string_agg(campo, ', ' order by campo) into mudou from (
    select 'identity_state' as campo
      where old.identity_state     is distinct from new.identity_state
    union all select 'source_id'
      where old.source_id          is distinct from new.source_id
    union all select 'document_key'
      where old.document_key       is distinct from new.document_key
    union all select 'document_key_basis'
      where old.document_key_basis is distinct from new.document_key_basis
    union all select 'run_id'
      where old.run_id             is distinct from new.run_id
    union all select 'sha256'
      where old.sha256             is distinct from new.sha256
    union all select 'storage_object_id'
      where old.storage_object_id  is distinct from new.storage_object_id
  ) t;
  if mudou is not null then
    raise exception 'FASE 10: a identidade da observacao % nao se reescreve '
                    '(tentou mudar: %). Uma corrida que PROVE outra coisa '
                    'escreve uma observacao NOVA.', old.id, mudou;
  end if;
  return new;
end $$;

-- `drop ... if exists` antes de criar: `create trigger` não tem `or replace`
-- em Postgres 16, e sem isto uma segunda corrida rebentava — no sítio errado,
-- e a dizer a coisa errada sobre a migration.
drop trigger if exists a_identidade_da_observacao_nao_se_reescreve
  on public.raw_asset;
create trigger a_identidade_da_observacao_nao_se_reescreve
  before update on public.raw_asset
  for each row
  execute function public.a_identidade_da_observacao_nao_se_reescreve();

comment on function public.a_identidade_da_observacao_nao_se_reescreve() is
  'FASE 10. Congela os SETE campos da afirmacao de identidade de uma '
  'observacao: os quatro que a declaram e os tres que as duas chaves de '
  'idempotencia usam. `storage_path` NAO esta entre eles de proposito — ele e '
  'endereco, e a fase 11 retira-o. Campos operacionais (attempts, '
  'last_attempt_at, preserved, not_preserved_reason, source_url, captured_at) '
  'continuam a poder mudar.';
