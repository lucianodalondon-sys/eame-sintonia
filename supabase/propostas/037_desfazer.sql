-- DESFAZER 037 · A SALA DIZ QUAL VIDEO E O MESMO (proposta MAESTRO-SOCIAL, 26/09).
-- So retira o que a 037 acrescentou. `sala_de_espera` nao e tocada (a 037 nao lhe mexeu).
drop view if exists public.sala_de_espera_videos;
drop trigger if exists sala_de_espera_video_nao_muda on public.sala_de_espera_video;
drop table if exists public.sala_de_espera_video;
drop function if exists public.sala_de_espera_video_so_acrescenta();
