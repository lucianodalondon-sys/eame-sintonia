-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 006
-- REGISTRO REGULATÓRIO + RLS.
--
-- O ROPF espanhol tem 3.084 registros e 262 titulares, e já é coletado por
-- scripts/mapa_regfi.py. Aqui ele ganha casa consultável — hoje a pergunta
-- "quais culturas a ADAMA cobre e com que exposição de expiry" exige
-- carregar JSON inteiro na memória.
--
-- RLS herda a decisão brasileira: bruto e custo não são do cliente.
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════

create table public.registro_regulatorio (
  id                bigserial primary key,
  pais              pais not null,
  registration_id   text not null,            -- ES-00849
  nome_comercial    text,
  titular           text not null,
  formulado         text,
  estado            text not null,            -- Vigente / Cancelado
  fecha_caducidad   date,
  fecha_limite_venta date,
  fecha_inscripcion date,
  fonte             text not null,
  fonte_versao      text not null,            -- timestamp do servidor MAPA
  raw_asset_id      bigint references public.raw_asset(id) on delete set null,
  capturado_em      timestamptz not null,
  UNIQUE (pais, registration_id, fonte_versao)
);
create index reg_titular_idx on public.registro_regulatorio (titular, estado);
create index reg_expiry_idx  on public.registro_regulatorio (fecha_caducidad);
comment on column public.registro_regulatorio.fonte_versao is
  'A versão da fonte faz parte da chave: o mesmo registro em duas capturas '
  'são duas linhas. Status atual NÃO apaga a história — é assim que '
  'CHANGE-EVENTS existe.';
comment on column public.registro_regulatorio.fecha_caducidad is
  'EXPIRY != WITHDRAWAL. Vencimento de autorização não é retirada de mercado.';

create table public.registro_uso (
  id             bigserial primary key,
  registro_id    bigint not null references public.registro_regulatorio(id) on delete cascade,
  crop_id        bigint references public.crop(id)  on delete restrict,
  issue_id       bigint references public.issue(id) on delete restrict,
  substancia     text,
  -- nulls not distinct: crop_id, issue_id e substancia são nuláveis.
  UNIQUE NULLS NOT DISTINCT (registro_id, crop_id, issue_id, substancia)
);

-- ══════════════════════════════════════════════════════════════════════
-- RLS em TODAS as tabelas. Mesma regra do Brasil.
-- ══════════════════════════════════════════════════════════════════════
alter table public.geografia            enable row level security;
alter table public.collection_run       enable row level security;
alter table public.raw_asset            enable row level security;
alter table public.organizacao          enable row level security;
alter table public.pessoa               enable row level security;
alter table public.pessoa_identificador enable row level security;
alter table public.afiliacao            enable row level security;
alter table public.origem               enable row level security;
alter table public.canal                enable row level security;
alter table public.conteudo             enable row level security;
alter table public.transcricao          enable row level security;
alter table public.comentario           enable row level security;
alter table public.crop                 enable row level security;
alter table public.issue                enable row level security;
alter table public.crop_issue           enable row level security;
alter table public.conteudo_crop_issue  enable row level security;
alter table public.observacao           enable row level security;
alter table public.derivacao            enable row level security;
alter table public.derivacao_observacao enable row level security;
alter table public.resposta_registrada  enable row level security;
alter table public.lacuna_candidata     enable row level security;
alter table public.registro_regulatorio enable row level security;
alter table public.registro_uso         enable row level security;

-- Bastidor: execução, custo e bruto são matéria-prima e contabilidade nossa.
-- Comentário idem: mesmo pseudonimizado, é bruto de terceiros.
-- (as policies concretas dependem de public.eh_admin(), criada no schema de
--  acesso — por isso ficam na 007, junto das views.)
