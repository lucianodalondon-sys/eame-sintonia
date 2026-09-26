-- 037 · A SALA DIZ QUAL VIDEO E O MESMO — PROPOSTA (MAESTRO-SOCIAL, 26/09). NAO APLICAR SEM O DONO DA SALA.
--
-- PORQUE: a ARPA Valle d'Aosta partilhou um video do ISPRA (medido, canario de 24/09): dois POSTS,
-- dois itens na Sala, o MESMO video (`urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ`). O Scrap ja
-- carimba cada unidade com `VIDEO_IDENTITY` e, no segundo, `MESMO_VIDEO_QUE`
-- (`leis/identidade_do_video.py`). A Sala nao tinha onde o guardar, e a Inteligencia contava dois.
--
-- PORQUE NAO SEM MIGRACAO (medido na 033): o caderno de revisoes (`sala_de_espera_revisao`) so aceita
-- uma lista fechada de campos (`revisao_so_de_campo_revisivel`: tempo, lugar, completude, chaves) e a
-- identidade NAO se reve (e o que pousou). Os campos json que existem (`fato`, `tempo_lugar_evidencia`,
-- `janela_declarada`, `completude_tempo_lugar`) dizem OUTRA coisa; por o video la dentro era misturar.
--
-- O QUE FAZ: uma tabela AO LADO (como a gaveta da 033) — NENHUMA coluna nova em `sala_de_espera`, a
-- impressao das corridas nao muda, nada do que ja pousou e tocado. So acrescenta.
--
--   · uma linha por item da Sala COM identidade de video CONHECIDA. UNKNOWN NAO FUNDE: um item sem
--     identidade nao tem linha (a regra do formato recusa `NAO SEI`).
--   · `mesmo_video_que` null = este item e o primeiro visto com este video; objeto = diz de quem e
--     (SOURCE_ID, RUN_ID, DOCUMENT_ID, POST do primeiro).
--   · so acrescenta: UPDATE/DELETE recusados (como as revisoes da 033).
--   · `sala_de_espera_videos` (vista): um video, uma linha, com quantos itens o trazem.
--
-- ONDE ESTA: supabase/propostas/ (FORA de supabase/migrations: nenhuma Sala, descartavel ou real, a aplica sozinha).
-- Aprovada, passa para supabase/migrations/ e o desfazer para supabase/desfazer/.
-- DESFAZER: supabase/propostas/037_desfazer.sql. ENSAIO: provas/migracao_037_ensaio_descartavel.py.

create table if not exists public.sala_de_espera_video (
  run_id               text        not null,
  ordem                integer     not null,
  video_identity       text        not null,
  video_identity_basis text        not null,
  mesmo_video_que      jsonb,
  registado_em         timestamptz not null default now(),
  primary key (run_id, ordem),
  foreign key (run_id, ordem) references public.sala_de_espera (run_id, ordem)
    on delete restrict,
  constraint video_identity_conhecida check (
    video_identity ~ '^(YOUTUBE:[A-Za-z0-9_-]{11}|LINKEDIN:urn:li:digitalmediaAsset:[A-Za-z0-9_-]+)$'),
  constraint video_identity_diz_de_onde check (length(btrim(video_identity_basis)) > 0),
  constraint mesmo_video_que_e_objeto check (
    mesmo_video_que is null or (jsonb_typeof(mesmo_video_que) = 'object'
                                and mesmo_video_que ?& array['SOURCE_ID', 'RUN_ID']))
);

create index if not exists sala_de_espera_video_por_video_idx
  on public.sala_de_espera_video (video_identity);

comment on table public.sala_de_espera_video is
  'O video de cada item social da Sala (identidade CONHECIDA; UNKNOWN nao tem linha) e, se ja visto, '
  'de quem e (mesmo_video_que). So acrescenta. Escritor: admissao/video_na_sala.py. Proposta 037.';

create or replace function public.sala_de_espera_video_so_acrescenta()
returns trigger language plpgsql as $$
begin
  raise exception 'SALA_VIDEO_SO_ACRESCENTA: % recusado em sala_de_espera_video. '
    'A identidade do video e o que pousou: nao se edita nem se apaga.', tg_op;
end $$;

do $$
begin
  if not exists (select 1 from pg_trigger where tgname = 'sala_de_espera_video_nao_muda') then
    create trigger sala_de_espera_video_nao_muda
      before update or delete on public.sala_de_espera_video
      for each row execute function public.sala_de_espera_video_so_acrescenta();
  end if;
end $$;

create or replace view public.sala_de_espera_videos as
  select video_identity,
         count(*)                                        as itens,
         count(*) filter (where mesmo_video_que is null) as primeiros,
         min(registado_em)                               as visto_primeiro_em
    from public.sala_de_espera_video
   group by video_identity;

comment on view public.sala_de_espera_videos is
  'Um video, uma linha: quantos itens da Sala trazem o MESMO video (partilhas incluidas). Proposta 037.';
