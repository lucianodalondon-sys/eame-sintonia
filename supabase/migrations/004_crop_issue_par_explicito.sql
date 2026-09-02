-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 004
-- CROP x ISSUE COMO PAR EXPLÍCITO.
--
-- Esta migration existe por causa de uma lei brasileira medida: "ferrugem"
-- não é uma pergunta; "ferrugem x soja" é. E um assunto pode ter N culturas,
-- então colapsar em cult_top perde informação de forma silenciosa.
--
-- No schema brasileiro o par não cabia: `fontes.culturas` é text[] mas
-- `documentos.cultura` é text singular, e ISSUE não existe como coluna em
-- lugar nenhum — vive só no léxico `termos.categoria`. Resultado: o par só
-- podia ser formado na camada analítica, longe da evidência.
--
-- Aqui o par é entidade de primeira classe, com vocabulário controlado
-- ancorado nas fontes espanholas (MAPA: 448 cultivos, 708 plagas) e no
-- dicionário canônico que o EAME já possui (X-007).
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

create table public.crop (
  id            bigserial primary key,
  codigo        text not null unique,       -- OLIVE, WHEAT, VINE
  nome_es       text,                       -- OLIVO, TRIGO, VID
  mapa_id_cultivo integer unique,           -- id real do ROPF (OLIVO=1972)
  eppo_code     text,
  UNIQUE (codigo)
);

create table public.issue (
  id            bigserial primary key,
  codigo        text not null unique,       -- REPILO, VERTICILLIUM, XYLELLA
  nome_es       text,
  classe        text not null check (classe in
                ('DISEASE','PEST','WEED','RESISTANCE','APPLICATION_TIMING','ABIOTIC','OTHER')),
  mapa_id_plaga integer unique,
  eppo_code     text
);

-- O PAR. Nunca derivado por coocorrência: precisa de relação defensável.
create table public.crop_issue (
  id          bigserial primary key,
  crop_id     bigint not null references public.crop(id)  on delete restrict,
  issue_id    bigint not null references public.issue(id) on delete restrict,
  UNIQUE (crop_id, issue_id)
);
comment on table public.crop_issue is
  'OLIVE x REPILO é a unidade. Nunca REPILO -> OLIVE só porque OLIVE '
  'apareceu mais vezes: isso é distribuição observada, não par declarado.';

-- Ligação evidência -> par, com a RELAÇÃO que a sustenta.
-- Coocorrência textual é um valor possível de `relacao`, e o mais fraco:
-- problema e cultura no mesmo documento NÃO prova problema na cultura.
-- Uma frase pode ser lista de espectro de um produto, não uma ocorrência.
create table public.conteudo_crop_issue (
  id             bigserial primary key,
  conteudo_id    bigint not null references public.conteudo(id) on delete cascade,
  crop_issue_id  bigint not null references public.crop_issue(id) on delete restrict,
  relacao        text not null check (relacao in
                 ('OCORRENCIA_DECLARADA',    -- o texto afirma o problema naquela cultura
                  'ENSAIO_OU_ESTUDO',        -- trabalho científico sobre o par
                  'RECOMENDACAO_TECNICA',
                  'ESPECTRO_DE_PRODUTO',     -- lista de rótulo — NÃO é ocorrência
                  'COOCORRENCIA_TEXTUAL')),  -- só apareceram juntos — o mais fraco
  evidencia      text not null,              -- o trecho que sustenta
  rule_version   text not null,
  UNIQUE (conteudo_id, crop_issue_id, relacao)
);
comment on column public.conteudo_crop_issue.relacao is
  'COOCORRENCIA_TEXTUAL e ESPECTRO_DE_PRODUTO NÃO autorizam afirmar que o '
  'problema ocorre na cultura. São candidatos, e o schema obriga a dizer qual é qual.';
