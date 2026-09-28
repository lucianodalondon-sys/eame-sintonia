-- DESFAZER 038 · A SALA GUARDA O PRECO DECLARADO (proposta myfruit, 28/09).
-- So retira o que a 038 acrescentou. `sala_de_espera` nao e tocada (a 038 nao lhe mexeu).
drop view if exists public.sala_de_espera_precos;
drop trigger if exists sala_de_espera_preco_nao_muda on public.sala_de_espera_preco;
drop trigger if exists sala_de_espera_preco_nao_esvazia on public.sala_de_espera_preco;
drop table if exists public.sala_de_espera_preco;
drop function if exists public.sala_de_espera_preco_so_acrescenta();
