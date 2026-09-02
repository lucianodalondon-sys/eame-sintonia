-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 021
-- O FATO PUBLICADO POR TERCEIRO — que não é medição nossa, e não pode
-- morar em `observacao`
--
-- `observacao` (migration 005) é MEDIÇÃO NOSSA sobre corpus: exige
-- `base_denominador` e `base_descricao`, porque uma contagem sem denominador
-- foi o erro que o Brasil pagou. Está certo para o que ela é.
--
-- Mas «o trigo duro ocupa 1.134.227 hectares na Itália» não é medição nossa.
-- É fato que o ISTAT publicou. Não tem denominador de amostra — tem FONTE e
-- DATA. Enfiá-lo em `observacao` obrigaria a inventar um denominador, e
-- inventar denominador é exatamente o que o denominador existe para impedir.
--
--     MEDIÇÃO NOSSA E FATO DE TERCEIRO SÃO COISAS DIFERENTES.
--     Misturá-las faz o portal não saber mais quem afirmou o quê.
--
-- Esta migration cria as cinco famílias que a missão LAST-MILE trouxe e que
-- o banco não tinha lugar para receber:
--
--   estatistica_agricola     área, produção, rendimento — o PESO da cultura
--   mercado_observacao       preço, custo, outlook
--   clima_observacao         chuva, temperatura, seca — ⚠️ CONDIÇÃO, não doença
--   boletim_fitossanitario   o boletim como documento, com fase declarada
--   sinal_regulatorio_futuro não-renovação, Artigo 21, revisão pendente
--   evento_setorial          feira, congresso, campo prova
--
-- AS QUATRO LEIS QUE VIRAM COLUNA E TRAVA AQUI
--
--   1. CLASSE TEMPORAL DECLARADA — CURRENT, OUTLOOK e HISTORICAL nunca se
--      misturam. O demo mostrou azeite de Salerno a €630 como preço corrente;
--      a cotação era de 2015. Sem coluna obrigatória, isso volta.
--
--   2. NÍVEL GEOGRÁFICO DECLARADO — boletim provincial NÃO representa a
--      região. Cinco documentos provinciais da Campânia não são «a Campânia».
--      O nível é coluna, e a view de cobertura conta separado.
--
--   3. CLIMA É CONDIÇÃO — chuva não é presença de doença, não é incidência
--      de praga, não é perda. `o_que_nao_prova` é NOT NULL nessa tabela, e
--      só nela, porque é a única onde a tentação é automática.
--
--   4. PRORROGAÇÃO NÃO É RENOVAÇÃO — e ato que ESTENDE prazo não decide
--      nada. O tipo do sinal é enum, e `decisao_tomada` é boolean explícito.
--
-- NÃO EXECUTADA AQUI. Aplicador: `scripts/cadeia_canonica.sh`.
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- CLASSE TEMPORAL — a lei nº 1, virando tipo.
-- ─────────────────────────────────────────────────────────────────────
create type classe_temporal as enum ('CURRENT', 'OUTLOOK', 'HISTORICAL');

-- ─────────────────────────────────────────────────────────────────────
-- NÍVEL GEOGRÁFICO DO FATO — a lei nº 2.
-- AREAL é o nível que faltava e que o Brasil não tinha: «Metapontino» e
-- «Litorale veneziano» são áreas de trabalho do serviço técnico, não
-- unidades administrativas. Sem este nível, elas seriam gravadas como
-- «Basilicata» e «Veneto», e a cobertura pareceria completa.
-- ─────────────────────────────────────────────────────────────────────
create type nivel_geografico as enum (
  'EUROPEU', 'NACIONAL', 'MACROAREA', 'REGIONAL', 'PROVINCIAL', 'AREAL', 'NAO_SEI'
);

-- ═══════════════════════════════════════════════════════════════════════
-- 1 · ESTATÍSTICA AGRÍCOLA — o peso econômico da cultura
-- ═══════════════════════════════════════════════════════════════════════
create table if not exists public.estatistica_agricola (
  id                bigserial primary key,
  fonte_id          bigint not null references public.fonte_externa(id) on delete restrict,
  crop_id           bigint references public.crop(id) on delete set null,
  crop_literal      text not null,          -- como a FONTE escreve. Nunca traduzido.
  geografia_id      bigint references public.geografia(id),
  geografia_literal text not null,          -- «Emilia-Romagna», «ITD5», «Nord-Est»
  nivel             nivel_geografico not null,
  ano               int not null,
  indicador         text not null check (indicador in
                    ('SUPERFICIE_HA','PRODUCAO_Q','PRODUCAO_T','RENDIMENTO_T_HA',
                     'SUPERFICIE_EM_PRODUCAO_HA','PARTICIPACAO_NACIONAL_PCT')),
  valor             numeric not null,
  unidade           text not null,
  classe            classe_temporal not null,
  -- ⚠️ Derivado por NÓS ou publicado pela FONTE? A distinção é o objeto.
  derivado_por_nos  boolean not null default false,
  formula_derivacao text,
  source_url        text not null,
  dataset_codigo    text,                   -- «IT1:101_1015(1.0)»
  publicado_em      date,
  capturado_em      timestamptz not null default now(),
  o_que_nao_prova   text not null,
  UNIQUE NULLS NOT DISTINCT (fonte_id, crop_literal, geografia_literal, ano, indicador)
);
comment on table public.estatistica_agricola is
  'Área, produção e rendimento publicados por fonte oficial. Serve para o '
  'portal separar «praga em 200 ha» de «praga em 200 mil ha». NÃO diz nada '
  'sobre presença de praga, uso de defensivo, tamanho de mercado ou receita.';
comment on column public.estatistica_agricola.derivado_por_nos is
  'O rendimento do ISTAT foi CALCULADO por nós (produção/área), porque o cubo '
  'não publica resa. E o denominador é a área TOTAL, não a área em produção — '
  'que veio vazia em 100% das linhas. Para olivo e vite, que têm plantas '
  'jovens dentro da área total, esse rendimento é um PISO, não a produtividade '
  'do talhão produtivo. Sem esta coluna, um piso vira fato.';
comment on column public.estatistica_agricola.crop_literal is
  'Como a fonte escreve. O canônico é o `crop_id`, e ele pode ser NULL: não '
  'saber mapear é melhor do que mapear errado.';

-- A trava da lei nº 1 aplicada ao caso concreto que o ISTAT trouxe:
-- o cubo publica «2026» com produção para oliveira, uva e milho — culturas
-- colhidas de setembro a dezembro — num arquivo de 28/07/2026. Não pode ser
-- colheita observada. Ano futuro ou corrente exige classe declarada.
alter table public.estatistica_agricola drop constraint if exists
  ano_incompleto_nao_e_historico;
alter table public.estatistica_agricola add constraint
  ano_incompleto_nao_e_historico check (
    ano < extract(year from now())::int or classe <> 'HISTORICAL'
  );
comment on constraint ano_incompleto_nao_e_historico on public.estatistica_agricola is
  'O ano corrente ainda não fechou o ciclo. Marcá-lo HISTORICAL afirmaria uma '
  'colheita que ainda não aconteceu.';

-- ═══════════════════════════════════════════════════════════════════════
-- 2 · MERCADO
-- ═══════════════════════════════════════════════════════════════════════
create table if not exists public.mercado_observacao (
  id                bigserial primary key,
  fonte_id          bigint not null references public.fonte_externa(id) on delete restrict,
  crop_id           bigint references public.crop(id) on delete set null,
  crop_literal      text not null,
  praca             text,                   -- «Bologna», «Verona», NULL = nacional
  geografia_id      bigint references public.geografia(id),
  nivel             nivel_geografico not null,
  indicador         text not null,          -- PRECO, PRODUCAO, IMPORT, EXPORT, ESTOQUE, CUSTO
  valor_texto       text not null,          -- ⚠️ como a fonte publica: «€237,00»
  valor_numerico    numeric,                -- nosso parse, pode ser NULL
  unidade           text not null,
  qualidade         text,                   -- «Carnaroli», «frumento tenero n.3»
  periodo_inicio    date not null,
  periodo_fim       date not null,
  classe            classe_temporal not null,
  serie_parada_desde date,                  -- ⚠️ a praça que não cota mais
  citacao_literal   text,
  source_url        text not null,
  publicado_em      date,
  capturado_em      timestamptz not null default now(),
  o_que_nao_prova   text not null,
  UNIQUE NULLS NOT DISTINCT (fonte_id, crop_literal, praca, indicador, qualidade,
                             periodo_inicio, periodo_fim)
);
comment on column public.mercado_observacao.valor_texto is
  'O que a fonte publica, LITERAL. O EC Agri-food Data Portal devolve preço '
  'como TEXTO («€237,00»), e converter cedo perde a vírgula decimal italiana. '
  'O numérico é nosso parse e pode falhar — o literal, não.';
comment on column public.mercado_observacao.serie_parada_desde is
  'Preenchido quando a praça deixou de cotar. O azeite de Salerno aparecia a '
  '€630 no demo como se fosse corrente; a cotação é de 2015. Uma série parada '
  'mantém o último valor e parece atual.';

-- ═══════════════════════════════════════════════════════════════════════
-- 3 · CLIMA — a lei nº 3
-- ═══════════════════════════════════════════════════════════════════════
create table if not exists public.clima_observacao (
  id                bigserial primary key,
  fonte_id          bigint not null references public.fonte_externa(id) on delete restrict,
  geografia_id      bigint references public.geografia(id),
  geografia_literal text not null,
  nivel             nivel_geografico not null,
  estacao           text,                   -- nome da estação, quando houver
  variavel          text not null check (variavel in
                    ('CHUVA_MM','TEMPERATURA_C','TEMPERATURA_MAX_C','TEMPERATURA_MIN_C',
                     'UMIDADE_PCT','UMIDADE_DO_SOLO','INDICE_DE_SECA','ANOMALIA',
                     'EVAPOTRANSPIRACAO','OUTRA')),
  valor             numeric,
  valor_texto       text,
  unidade           text,
  periodo_inicio    date not null,
  periodo_fim       date not null,
  classe            classe_temporal not null,
  source_url        text not null,
  publicado_em      date,
  capturado_em      timestamptz not null default now(),
  -- ⚠️ NOT NULL só aqui. É a única tabela onde a inferência errada é automática.
  o_que_nao_prova   text not null,
  UNIQUE NULLS NOT DISTINCT (fonte_id, geografia_literal, estacao, variavel,
                             periodo_inicio, periodo_fim)
);
comment on table public.clima_observacao is
  'CLIMA É CONDIÇÃO. Não é presença de doença, não é incidência de praga, não '
  'é perda de produtividade. Chuva não «causa» peronospora numa tela — ela '
  'descreve um ambiente onde a peronospora é possível, e isso é outra frase.';
alter table public.clima_observacao drop constraint if exists
  clima_nao_afirma_doenca;
alter table public.clima_observacao add constraint
  clima_nao_afirma_doenca check (length(o_que_nao_prova) > 30);
comment on constraint clima_nao_afirma_doenca on public.clima_observacao is
  'A ressalva tem de ser escrita, não deixada em branco nem preenchida com '
  '«n/a». Trinta caracteres é o piso de uma frase de verdade.';

-- ═══════════════════════════════════════════════════════════════════════
-- 4 · BOLETIM FITOSSANITÁRIO — a lei nº 2
-- ═══════════════════════════════════════════════════════════════════════
create table if not exists public.boletim_fitossanitario (
  id                 bigserial primary key,
  fonte_id           bigint not null references public.fonte_externa(id) on delete restrict,
  titulo             text not null,
  numero             text,
  publicado_em       date not null,
  geografia_id       bigint references public.geografia(id),
  geografia_literal  text not null,
  nivel              nivel_geografico not null,
  crops_declaradas   text[] not null default '{}',
  -- ⚠️ a cultura foi DECLARADA pelo boletim, ou DEDUZIDA por nós das avversità?
  crop_declarada     boolean not null,
  fase_declarada     text,                  -- literal, no idioma da fonte
  avversita_citadas  text[] not null default '{}',
  orientacao         text,
  citacao_literal    text,
  source_url         text not null,
  classe             classe_temporal not null,
  capturado_em       timestamptz not null default now(),
  UNIQUE (fonte_id, titulo, publicado_em)
);
comment on column public.boletim_fitossanitario.nivel is
  'BOLETIM PROVINCIAL NÃO REPRESENTA A REGIÃO. Em 02/09/2026, 21 dos boletins '
  'novos eram provinciais ou de areal: a Campânia são cinco documentos '
  'separados, a Basilicata cobre só o Metapontino, o Trentino só a província '
  'de Trento — e o Sudtirol, maior área de maçã da Itália, ficou sem fonte.';
comment on column public.boletim_fitossanitario.crop_declarada is
  'FALSE quando a cultura foi deduzida das avversità citadas, e não escrita '
  'pelo boletim. Doze dos 73 boletins do pacote anterior estavam assim.';

-- A cobertura, contada com honestidade: só nível regional conta como região.
create or replace view public.v_cobertura_fitossanitaria as
select g.pais,
       coalesce(b.geografia_literal, 'NAO_SEI') as lugar,
       b.nivel,
       count(*)                                                as boletins,
       max(b.publicado_em)                                     as mais_recente,
       count(*) filter (where b.classe = 'CURRENT')            as correntes,
       bool_or(b.nivel = 'REGIONAL')                           as tem_nivel_regional
from public.boletim_fitossanitario b
left join public.geografia g on g.id = b.geografia_id
group by g.pais, b.geografia_literal, b.nivel;
comment on view public.v_cobertura_fitossanitaria is
  'Cobertura por LUGAR e por NÍVEL, separados. Somar provincial com regional '
  'produziria «19 de 20 regiões cobertas» quando muitas são um município.';

-- ═══════════════════════════════════════════════════════════════════════
-- 5 · SINAL REGULATÓRIO FUTURO — a lei nº 4
-- ═══════════════════════════════════════════════════════════════════════
create type tipo_sinal_regulatorio as enum (
  'PRORROGACAO_DE_APROVACAO',     -- estende prazo. NÃO decide renovação.
  'PROJETO_DE_NAO_RENOVACAO',     -- rascunho em consulta
  'NAO_RENOVACAO_DECIDIDA',
  'RENOVACAO_DECIDIDA',
  'REVISAO_ARTIGO_21',            -- reexame por novo dado, ex. classificação CLP
  'RESTRICAO_NOVA',
  'APROVACAO_NOVA',
  'CONCLUSAO_EFSA_PENDENTE',
  'REUNIAO_AGENDADA'
);

create table if not exists public.sinal_regulatorio_futuro (
  id                 bigserial primary key,
  fonte_id           bigint not null references public.fonte_externa(id) on delete restrict,
  tipo               tipo_sinal_regulatorio not null,
  substancia_literal text not null,
  substancia_id      bigint references public.substancia_ativa(id) on delete set null,
  geografia          text not null default 'UE',
  o_que              text not null,
  quando             date,
  janela             text,                  -- «3 meses», «até 03/09/2026»
  -- ⚠️ a lei nº 4, virando coluna: prorrogação NÃO é decisão.
  decisao_tomada     boolean not null,
  ato_ou_documento   text,                  -- «Reg. (UE) 2024/1206», ata do SCoPAFF
  citacao_literal    text,
  source_url         text not null,
  publicado_em       date,
  confianca          text not null check (confianca in ('ALTA','MEDIA','BAIXA')),
  por_que_pode_importar text not null,
  o_que_nao_prova    text not null,
  capturado_em       timestamptz not null default now(),
  UNIQUE NULLS NOT DISTINCT (fonte_id, tipo, substancia_literal, quando)
);
comment on column public.sinal_regulatorio_futuro.decisao_tomada is
  'PRORROGAÇÃO NÃO É RENOVAÇÃO. Em 02/09/2026, 39 das 50 substâncias do '
  'portfólio italiano estavam em aprovação PRORROGADA — já venceu uma vez e '
  'foi esticada por ato de procedimento enquanto a renovação é avaliada. '
  'Nenhuma dessas é decisão. Sem esta coluna, o portal transforma prazo '
  'esticado em «vai sair do mercado».';
comment on column public.sinal_regulatorio_futuro.por_que_pode_importar is
  'Obrigatório e separado do fato. NÃO converter evento regulatório em '
  'oportunidade comercial automaticamente — é a regra do §5 da missão.';

-- ═══════════════════════════════════════════════════════════════════════
-- 6 · EVENTO SETORIAL
-- ═══════════════════════════════════════════════════════════════════════
create table if not exists public.evento_setorial (
  id                 bigserial primary key,
  fonte_id           bigint not null references public.fonte_externa(id) on delete restrict,
  nome               text not null,
  organizador        text,
  data_inicio        date not null,
  data_fim           date,
  cidade             text,
  geografia_id       bigint references public.geografia(id),
  tema               text,
  crops              text[] not null default '{}',
  -- ⚠️ participação NUNCA se infere de edição passada.
  empresas_declaradas text[] not null default '{}',
  participacao_fonte text,                  -- onde a participação foi publicada
  source_url         text not null,
  capturado_em       timestamptz not null default now(),
  UNIQUE (nome, data_inicio)
);
comment on column public.evento_setorial.empresas_declaradas is
  'Só entra empresa cuja participação a PRÓPRIA FONTE publica para ESTA '
  'edição. Participação futura nunca se infere de participação passada — '
  'se a ADAMA esteve em 2026, isso não diz nada sobre 2027.';

-- ─────────────────────────────────────────────────────────────────────
-- RLS: mesma postura das migrations anteriores. Leitura para o papel de
-- leitura, escrita só pelo carregador.
-- ─────────────────────────────────────────────────────────────────────
do $$
declare t text;
begin
  foreach t in array array['fonte_externa','fonte_acesso_teste','estatistica_agricola',
                           'mercado_observacao','clima_observacao',
                           'boletim_fitossanitario','sinal_regulatorio_futuro',
                           'evento_setorial']
  loop
    execute format('alter table public.%I enable row level security', t);
  end loop;
end $$;

-- ═══════════════════════════════════════════════════════════════════════
-- 7 · A ÁREA DE ESPERA — e por que ela não é um depósito
-- ═══════════════════════════════════════════════════════════════════════
-- A missão LAST-MILE trouxe 97 registros cujo destino JÁ EXISTE no banco:
-- vozes vão para `pessoa` + `origem` + `conteudo`; concorrente vai para
-- `organizacao` + `conteudo`; catálogo vai para `catalogo_produto`; janela de
-- herbicida vai para `issue_window`. Essas tabelas têm travas próprias, e
-- várias foram escritas para impedir erros específicos do Brasil.
--
-- Enfiar 97 linhas nelas sem ler cada trava produziria dado que passa no
-- insert e mente na consulta — que é pior do que dado que não entrou.
--
--     DADO NA ÁREA DE ESPERA É DADO QUE CHEGOU E AINDA NÃO FOI COLOCADO.
--     DADO FORÇADO NA TABELA ERRADA É DADO QUE MENTE EM SILÊNCIO.
--
-- ⚠️ O QUE IMPEDE ISTO DE VIRAR DEPÓSITO
--
-- `destino_pretendido` é NOT NULL e é ENUM. Não se aceita registro sem saber
-- para onde ele vai. E a view `v_espera_envelhecendo` mostra o que está
-- parado há mais de 30 dias — porque área de espera sem prazo é gaveta.
-- ─────────────────────────────────────────────────────────────────────
create type destino_de_normalizacao as enum (
  'pessoa_e_origem',        -- vozes identificadas
  'organizacao_e_conteudo', -- comunicação de concorrente
  'catalogo_produto',       -- ficha comercial
  'issue_window',           -- janela de aplicação
  'estatistica_agricola',
  'mercado_observacao',
  'crop_issue',
  'NAO_SEI'
);

create table if not exists public.lastmile_registro_pendente (
  id                  bigserial primary key,
  missao              text not null,
  bloco               text not null,
  destino_pretendido  destino_de_normalizacao not null,
  crop_literal        text,
  geografia_literal   text,
  o_que               text not null,
  valor_texto         text,
  unidade             text,
  periodo             text,
  classe              classe_temporal not null,
  citacao_literal     text,
  source_url          text not null,
  publicado_em        date,
  confianca           text,
  o_que_nao_prova     text not null,
  exige_rota_italiana boolean not null default false,
  chegou_em           timestamptz not null default now(),
  normalizado_em      timestamptz,
  normalizado_para_id bigint,
  UNIQUE NULLS NOT DISTINCT (missao, bloco, source_url, o_que)
);
comment on table public.lastmile_registro_pendente is
  'Registro externo que CHEGOU com proveniência completa e ainda não foi '
  'colocado na tabela de destino. Não é rascunho e não é lixo: é dado real '
  'esperando o mapeamento correto. `destino_pretendido` é obrigatório — não '
  'se aceita registro sem saber para onde ele vai.';
comment on column public.lastmile_registro_pendente.o_que_nao_prova is
  'Obrigatório aqui como em toda tabela de fato externo. Um registro que '
  'perde a ressalva no caminho chega ao destino sem ela.';

create or replace view public.v_espera_envelhecendo as
select destino_pretendido, bloco, count(*) as parados,
       min(chegou_em) as mais_antigo,
       (now()::date - min(chegou_em)::date) as dias_parado
from public.lastmile_registro_pendente
where normalizado_em is null
group by destino_pretendido, bloco
order by min(chegou_em);
comment on view public.v_espera_envelhecendo is
  'Área de espera sem prazo é gaveta. Esta view existe para que o que está '
  'parado apareça, e não para que fique confortável.';

alter table public.lastmile_registro_pendente enable row level security;
