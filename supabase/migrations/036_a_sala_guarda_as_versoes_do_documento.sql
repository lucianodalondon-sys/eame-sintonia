-- ═══════════════════════════════════════════════════════════════════════
-- 036 · A SALA GUARDA AS VERSÕES DO DOCUMENTO — SÓ ACRESCENTA
--
-- NÃO EXECUTADA NA SALA REAL. Preparada e ensaiada em Postgres descartável
-- (DEDUP-DOC, 26/09). O número é 036 porque a D79 reservou 034 (lápide) e
-- 035 (TEMPO_LUGAR).
--
-- D79 (bot Luciano, 26/09 03:45): «o document_key mantém UM documento lógico,
-- mas mudança REAL de conteúdo acrescenta uma VERSÃO no caderno só-acrescenta;
-- bytes iguais não criam versão.» Resposta do coordenador sobre ONDE: tabela
-- nova, porque o caderno da 033 (`sala_de_espera_revisao`) só aceita 8 campos
-- (`revisao_so_de_campo_revisivel`) e mudá-lo seria trocar uma trava.
--
--     A LINHA ORIGINAL NÃO MUDA. A VERSÃO NOVA É UMA LINHA NOVA NESTE CADERNO.
--     NÃO HÁ UPDATE, NÃO HÁ DELETE, NÃO HÁ TRUNCATE.
--
-- «Mudança real» (decisão do coordenador): o texto comparado com o MESMO
-- extrator (producer + producer_version + parameters_hash do derivado). Se o
-- extrator mudou, re-extrai-se a versão anterior a partir do RAW com o extrator
-- novo; se não der, NÃO SEI — não cria versão, fica no recibo. Quem decide é
-- `admissao/versao_do_documento.py`; quem escreve é
-- `admissao/sala_de_espera.py::pousar` (escritor único).
--
-- Só CREATE. Nada existente é alterado.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.sala_de_espera_versao (
  -- a LINHA da Sala que é o documento lógico (a primeira que pousou)
  run_id              text        not null,
  ordem               integer     not null,
  versao              integer     not null check (versao >= 2),
  -- de onde veio a versão nova
  veio_da_corrida     text        not null,
  item_id             text        not null,
  raw_observation_id  bigint,
  texto               text        not null,
  -- a prova de que mudou: o derivado anterior e o novo, e como se comparou
  derivado_anterior   text        not null,
  como_se_comparou    text        not null check (como_se_comparou in (
                        'MESMO_EXTRATOR', 'REEXTRAIDO_DO_RAW')),
  registada_em        timestamptz not null default now(),
  primary key (run_id, ordem, versao),
  foreign key (run_id, ordem) references public.sala_de_espera (run_id, ordem)
    on delete restrict,
  constraint a_mesma_versao_nao_entra_duas_vezes unique (run_id, ordem, item_id),
  constraint versao_tem_texto check (length(btrim(texto)) > 0)
);

comment on table public.sala_de_espera_versao is
  'Versões de um documento que JÁ está na Sala (D79). A versão 1 é a própria linha '
  'de sala_de_espera; aqui entram a 2, a 3... SO ACRESCENTA (gatilho recusa '
  'UPDATE/DELETE/TRUNCATE). Escritor único: admissao/sala_de_espera.py::pousar.';

create or replace function public.sala_de_espera_versao_so_acrescenta()
returns trigger language plpgsql as $$
begin
  raise exception 'SALA_VERSAO_SO_ACRESCENTA: % recusado em sala_de_espera_versao. '
    'Uma versão não se edita nem se apaga: escreve-se outra.', tg_op;
end $$;

do $$
begin
  if not exists (select 1 from pg_trigger
                 where tgname = 'sala_de_espera_versao_nao_muda') then
    create trigger sala_de_espera_versao_nao_muda
      before update or delete on public.sala_de_espera_versao
      for each row execute function public.sala_de_espera_versao_so_acrescenta();
  end if;
  if not exists (select 1 from pg_trigger
                 where tgname = 'sala_de_espera_versao_nao_esvazia') then
    create trigger sala_de_espera_versao_nao_esvazia
      before truncate on public.sala_de_espera_versao
      for each statement execute function public.sala_de_espera_versao_so_acrescenta();
  end if;
end $$;
