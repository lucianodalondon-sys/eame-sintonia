-- ═══════════════════════════════════════════════════════════════════════
-- 034 · A LÁPIDE DA RETENÇÃO — o byte sai, a proveniência fica
-- ═══════════════════════════════════════════════════════════════════════
--
-- D79 (coordenador, 26/09 03:45): esta migração existia como `033_a_lapide_da_retencao.sql` em seis
-- ramos (canais-pessoas-v1, pessoas-agro-v1, reparo-fontes-v1, retencao-youtube-v1,
-- youtube-canario-v1, youtube-pronto-v1) — as seis com o MESMO conteúdo (blob e4358c75, commit
-- c80c4229, 23/09). Nenhuma entra como 033: a 033 da Sala (a base, as chaves e as revisões) já está
-- aplicada. Entra como 034, com o corpo INALTERADO (só esta nota e o número mudaram), e ganha o seu
-- desfazer (`supabase/desfazer/034_desfazer.sql`). Ensaiada junto com a 035 numa cópia da Sala.
--
-- D20 (DECISOES-DONO-2026-09-23, bot Luciano por delegação do dono): os
-- metadados que vêm da YouTube Data API (título, descrição, contagens,
-- listas, comentários) só podem ficar guardados até 30 dias — depois,
-- renovar ou apagar. É a regra III.E.4 das Developer Policies; o texto dela,
-- com endereço, data e sha256, está em candidatas/PROVA-TERMOS-SOC1-V1.json.
--
-- A casa nunca apagou nada, e com razão: `raw_asset` não reescreve a
-- identidade da observação (027) e o derivado aponta-lhe com
-- `on delete restrict` (022). APAGAR A LINHA seria apagar a prova de que a
-- coisa existiu, de quem a trouxe e quando. Por isso a regra cumpre-se de
-- outra maneira:
--
--     O BYTE SAI. A LINHA FICA, COM `preserved = false` E O MOTIVO.
--     E ESTA TABELA DIZ, POR ESCRITO, O QUE SAIU, QUANDO E PORQUÊ.
--
-- Uma lápide por ficheiro apagado (`storage_path` único): o do raw, e o de
-- cada derivado dele. O `sha256` que aqui fica é o do que EXISTIA — prova de
-- que se apagou aquilo, e não outra coisa.
--
-- O ÁUDIO LOCAL NÃO ENTRA (D20): `yt-dlp:public_audio` e a transcrição dele
-- não são dados da API. A regra está no vocabulário fechado de `regra`, e o
-- dono que escreve aqui (`guarda/retencao_youtube_api.py`) só lê observações
-- cuja rota prova ser `youtube-data-api-v3:*`.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.lapide_de_retencao (
  id                   bigserial primary key,
  raw_asset_id         bigint not null
                       references public.raw_asset(id) on delete restrict,
  derived_artifact_id  bigint
                       references public.derived_artifact(id) on delete restrict,
  storage_path         text   not null unique,
  sha256               char(64) not null
                       constraint lapide_sha256_hex check (sha256 ~ '^[0-9a-f]{64}$'),
  bytes                bigint,
  regra                text   not null
                       constraint lapide_regra_conhecida
                       check (regra in ('YOUTUBE_API_III_E_4_30D')),
  motivo               text   not null
                       constraint lapide_motivo_conhecido
                       check (motivo in ('PRAZO_VENCIDO', 'RENOVADA')),
  rota                 text   not null
                       constraint lapide_so_da_api
                       check (rota like 'youtube-data-api-v3:%'),
  captured_at          timestamptz not null,
  apagado_em           timestamptz not null default now(),
  prova                text   not null
);

create index if not exists lapide_raw_idx on public.lapide_de_retencao (raw_asset_id);

comment on table public.lapide_de_retencao is
  'D20 · III.E.4: um registo por ficheiro apagado pela regra dos 30 dias da '
  'YouTube Data API. A linha de raw_asset fica (preserved=false + motivo); '
  'esta tabela guarda o que saiu (storage_path, sha256, bytes), quando e porque. '
  'Escritor unico: guarda/retencao_youtube_api.py. Audio local nao entra.';
