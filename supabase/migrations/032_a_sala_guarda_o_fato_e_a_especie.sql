-- ═══════════════════════════════════════════════════════════════════════
-- 032 · A SALA GUARDA O FATO E A ESPÉCIE — sete campos que já eram medidos
--
-- ── O FACTO NOVO QUE ABRIU ESTA MIGRATION ─────────────────────────────────
--
-- A `031` deu à Sala de Espera os doze campos do contrato `READY`
-- (COL-LAW-043). Estavam certos, e estavam incompletos — e a prova disso está
-- escrita na PRÓPRIA COL-LAW-043, três parágrafos abaixo da lista:
--
--     «O alvo é: QUEM disse O QUÊ sobre QUE CULTURA e QUE PROBLEMA, ONDE,
--      QUANDO, DE QUE PAPEL e COM QUE EVIDÊNCIA.»
--
-- Dos oito, a lista de doze respondia três. A lei contradizia-se a si própria,
-- e o «isto e mais nada» venceu na prática.
--
-- Medido no caminho real desta árvore, com um facto agronómico de 25 campos:
--
--     campos na entrada .... 25
--     campos no READY ...... 12
--     perdidos ............. 20, entre eles `claim_id`, `subject`,
--                            `predicate`, `crop_eppo`, `problem_eppo`,
--                            `method`, `unit`, `scale`, `denominator`,
--                            `doi`, `registration_id`
--
-- E o detalhe que faz disto um defeito e não uma escolha: **a porta já sabia
-- que aquilo era um facto**. `admissao.MARCAS_DE_FATO` lê `claim_id`,
-- `subject`, `predicate` e `fact_id`; `estagio()` devolve `FATO`; e a régua
-- aplicada MUDA por causa disso. Os campos entram, são lidos, decidem — e não
-- saíam.
--
--     O SISTEMA SABE O QUE É UM CLAIM.
--     O CONTRATO DE SAÍDA NÃO TINHA ONDE O PÔR.
--
-- ── OS SETE, E O DONO DE CADA UM ANTES DESTA MIGRATION ────────────────────
--
--   estagio                          admissao.estagio()          (COL-LAW-502)
--   published_at                     ingresso.FRONTEIRA_TRANSPORTA
--   observed_at                      ingresso.FRONTEIRA_TRANSPORTA
--   fact_time_basis                  o livro do coletor italiano, 175 linhas
--   fact_location_basis              leis/artefato.py::conferir  (já exigia)
--   source_declared_evidence_class   regras/italy_contracts.mjs  (13 de 13)
--   fato                             admissao.MARCAS_DE_FATO
--
-- NENHUM É UM CONCEITO NOVO. São conceitos que esta casa declarava ANTES de
-- qualquer execução e que morriam nesta fronteira.
--
--     RUNTIME SABE != O SISTEMA GUARDA.
--
-- ── O QUE ESTA MIGRATION NÃO FAZ ──────────────────────────────────────────
--
-- Não preenche nada. Não extrai claim de texto nenhum — extracção de claim é
-- `TARGET` na COL-LAW-202 e continua a NÃO existir nesta casa. Não infere
-- lugar, não infere tempo, não cunha código EPPO. Ausência continua a chegar
-- como `NAO SEI`, e `NAO SEI` continua a não ser `NAO`.
--
-- ── ADITIVA, E POR ISSO SEGURA PARA QUEM JÁ LÁ ESTÁ ───────────────────────
--
-- As sete colunas nascem com `default` e `not null`. Uma linha escrita pela
-- `031` — se existir — passa a ter `NAO SEI` nos seis textos e a palavra
-- `"NAO_SE_APLICA"` no facto. Isso é a verdade sobre ela: ninguém mediu aqueles
-- campos quando ela entrou, e dizer `NAO SEI` é o que o contrato manda dizer.
--
--     UM DEFAULT QUE DECLARA AUSÊNCIA != UM DEFAULT QUE INVENTA VALOR.
--
-- ═══════════════════════════════════════════════════════════════════════
--
--     NÃO EXECUTADA
--
-- Esta migration é uma PROPOSTA, pela mesma disciplina da `031`. Ela foi
-- aplicada e medida contra PostgreSQL DESCARTÁVEL, e nunca contra o banco de
-- produção. A aplicação é uma decisão explícita e separada.
--
--     DESIGNED != DB_TESTED != LIVE.
-- ═══════════════════════════════════════════════════════════════════════

-- ── A ESPÉCIE DA COISA ───────────────────────────────────────────────────
-- `DOCUMENTO` relata; `FATO` afirma. Medi-los com a mesma régua é o erro que a
-- COL-LAW-502 veio impedir, e a jusante não havia como saber qual era qual.
-- A lista é FECHADA porque `admissao.estagio()` só devolve estes três — e uma
-- coluna de texto livre aqui deixaria a Intelligence a adivinhar.
alter table public.sala_de_espera
  add column if not exists estagio text not null default 'ESTAGIO_DESCONHECIDO';

do $$
begin
  if not exists (select 1 from pg_constraint
                 where conname = 'estagio_e_um_dos_tres') then
    alter table public.sala_de_espera
      add constraint estagio_e_um_dos_tres
      check (estagio in ('DOCUMENTO', 'FATO', 'ESTAGIO_DESCONHECIDO'));
  end if;
end $$;

-- ── OS OUTROS DOIS TEMPOS ────────────────────────────────────────────────
-- COL-LAW-031: `FACT_TIME != PUBLISHED_AT != OBSERVED_AT != COLLECTED_AT`.
-- A `031` guardava o primeiro e o último. Sem os do meio, «não sei quando o
-- facto foi» e «não sei nada sobre tempo» chegavam à Intelligence como a mesma
-- resposta — e não são a mesma resposta.
--
-- ⚠️ E ELES NÃO SE PROMOVEM. Nenhuma trava aqui copia um para o outro, e a
-- razão de existirem em colunas separadas é exactamente essa.
alter table public.sala_de_espera
  add column if not exists published_at text not null default 'NAO SEI';
alter table public.sala_de_espera
  add column if not exists observed_at  text not null default 'NAO SEI';

-- ── COMO SE SABE, E PORQUE NÃO SE SABE ───────────────────────────────────
-- `leis/artefato.py::conferir` JÁ reprovava um `FACT_LOCATION` preenchido «sem
-- dizer de onde saiu». A lei existia; o contrato de saída não tinha onde pôr a
-- resposta. E do outro lado, medido no livro italiano real: as 175 observações
-- escrevem, uma a uma, PORQUÊ o tempo do facto é desconhecido —
--
--     «UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao»
--
-- Essa frase é uma MEDIÇÃO, e morria na fronteira.
--
--     UM `UNKNOWN` COM RAZÃO É UMA MEDIÇÃO.
--     UM `UNKNOWN` SEM RAZÃO É INDISTINGUÍVEL DE DESLEIXO.
alter table public.sala_de_espera
  add column if not exists fact_time_basis     text not null default 'NAO SEI';
alter table public.sala_de_espera
  add column if not exists fact_location_basis text not null default 'NAO SEI';

-- ── A ESPÉCIE PROBATÓRIA, DECLARADA PELA FONTE ───────────────────────────
-- Os 13 contratos de fonte italianos declaram `EVIDENCE_CLASS` ANTES de
-- qualquer execução, com as leis escritas ao lado — `AGROCLIMATIC_SIGNAL !=
-- PEST_OCCURRENCE`, `COMPANY_CLAIM != REGULATORY_FACT`. Nenhuma atravessava: a
-- jusante, um boletim agroclimático da ARPAV e um relato de campo da ARIF eram
-- o MESMO objecto, `TEXTO`.
--
-- ⚠️ O NOME É LONGO DE PROPÓSITO, E A COLUNA É TEXTO LIVRE DE PROPÓSITO.
-- O valor é da FONTE, não do documento, e medido é prosa: «OBSERVED_FIELD_SIGNAL
-- + TECHNICAL_GUIDELINE (separar por bloco)». Uma lista fechada aqui seria eu a
-- decidir hoje, sem caso que obrigue, que espécies o agro tem direito a ter —
-- e `docs/operacao/STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md` §14.4 deixou
-- essa pergunta explicitamente em aberto.
--
--     DECLARADO PELA FONTE != MEDIDO NO DOCUMENTO.
alter table public.sala_de_espera
  add column if not exists source_declared_evidence_class text not null
  default 'NAO SEI';

-- ── O FACTO, QUANDO O ITEM É UM FACTO ────────────────────────────────────
-- ⚠️ `json`, E NÃO `jsonb`, E A DIFERENÇA NÃO É DE GOSTO.
-- `jsonb` reordena chaves e descarta duplicadas. `sala_de_espera.
-- impressao_da_corrida()` assina os BYTES do corpo, e é essa assinatura que
-- distingue um retry legítimo («já estava») de um conflito («esta corrida já
-- contou outra história»). Com `jsonb`, o MESMO conteúdo lido de volta daria
-- outra impressão, e um retry honesto seria acusado de conflito.
--
--     UMA IMPRESSÃO QUE MUDA NA VIAGEM NÃO É UMA IMPRESSÃO.
--
-- ⚠️ E A AUSÊNCIA É A PALAVRA `"NAO_SE_APLICA"`, ESCRITA COMO JSON.
-- Um documento não tem facto estruturado dentro: ele RELATA (COL-LAW-201).
-- Guardar `{}` diria «olhei e não havia», quando a verdade é «a pergunta não se
-- aplica a esta espécie de coisa». `null` diria uma terceira coisa ainda.
alter table public.sala_de_espera
  add column if not exists fato json not null default '"NAO_SE_APLICA"'::json;

-- ── A CONSULTA QUE A INTELLIGENCE VAI FAZER ──────────────────────────────
-- Ela não pergunta «dá-me tudo»: pergunta «dá-me os FACTOS que esperam».
-- Sem isto, essa pergunta varre a tabela inteira.
create index if not exists sala_de_espera_fato_a_espera
  on public.sala_de_espera (estagio)
  where estado_da_fila = 'WAITING';

comment on column public.sala_de_espera.estagio is
  'DOCUMENTO relata, FATO afirma (COL-LAW-502). Escrito por admissao.estagio(), '
  'nunca adivinhado aqui.';
comment on column public.sala_de_espera.fato is
  'O que o produtor declarou como facto, preservado TAL E QUAL, com chaves '
  'ordenadas. NAO e extraccao: a Collection nao extrai claim (COL-LAW-202, '
  'TARGET). "NAO_SE_APLICA" quando o estagio nao e FATO.';
comment on column public.sala_de_espera.source_declared_evidence_class is
  'A especie probatoria que o CONTRATO DE FONTE declara — nao a medida neste '
  'documento. Texto livre, e e da fonte. DECLARADO != MEDIDO.';
comment on column public.sala_de_espera.fact_time_basis is
  'Como se sabe o FACT_TIME, ou porque NAO se sabe. Um UNKNOWN com razao e uma '
  'medicao; sem razao e indistinguivel de desleixo.';
