-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 010
-- CATÁLOGO PÚBLICO DO FABRICANTE — a terceira afirmação, com casa própria.
--
-- Já existiam duas casas e nenhuma delas serve para esta:
--
--   registro_regulatorio      o que o Estado autorizou. Fonte: MAPA/ROPF.
--   disponibilidade_comercial se está sendo vendido. Fonte: medição comercial.
--   ── e faltava ──
--   catálogo público          o que o FABRICANTE publica no site dele.
--
-- Enfiar o catálogo público em qualquer uma das duas criaria um segundo dono da
-- mesma afirmação, e dois donos divergem. A lei que separa as três:
--
--   PUBLIC CATALOG PRESENCE  !=  REGULATORY FACT  !=  COMMERCIAL AVAILABILITY
--
-- Presença em catálogo prova que a página existe. Não prova registro, não prova
-- venda, não prova estoque, não prova prioridade interna do fabricante.
--
-- POR QUE TANTO CHECK
--
-- As leis desta missão não sobrevivem como comentário. Um par cultivo×agente sem
-- âncora de linha é exatamente o produto cartesiano que a seção 8 proíbe — então
-- a âncora é NOT NULL, e o cartesiano deixa de ser possível de inserir. Mesma
-- ideia para as outras: a regra vira constraint, não recomendação.
--
-- NÃO EXECUTADA.
-- ═══════════════════════════════════════════════════════════════════════


-- ─────────────────────────────────────────────────────────────────────
-- 1 · A CAPTURA
--
-- Uma linha por leitura do catálogo de um fabricante num país. É ela que
-- separa CAPTURED_AT de IMPORTED_AT: os bytes foram capturados numa hora,
-- e importados noutra, possivelmente dias depois. Colapsar as duas apagaria
-- a idade real do dado.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_captura (
  id                bigserial primary key,
  run_id            text not null references public.collection_run(run_id) on delete restrict,
  pais              pais not null,
  fabricante        text not null,                 -- ADAMA
  catalogo_url      text not null,
  capturado_em      timestamptz not null,          -- quando os BYTES foram lidos do site
  importado_em      timestamptz not null default now(),  -- quando entraram AQUI
  metodo_de_captura text not null,                 -- 'NAVEGADOR_LOCAL', 'HTTP_DIRETO'...
  fonte_versao      text not null,                 -- carimbo da versão da fonte
  rule_version      text not null,
  total_no_catalogo integer not null,
  enumeracao_completa boolean not null,
  e_baseline        boolean not null,
  CONSTRAINT captura_unica_por_fonte
    UNIQUE (pais, fabricante, fonte_versao),
  CONSTRAINT importar_nao_pode_ser_antes_de_capturar
    CHECK (importado_em >= capturado_em)
);
comment on table public.catalogo_captura is
  'Uma leitura do catálogo público de um fabricante. e_baseline = TRUE significa '
  'PRIMEIRA captura comparável: baseline NÃO é evento de mudança. Produto novo, '
  'lançamento e produto removido só existem entre DUAS capturas comparáveis; '
  'derivar qualquer um deles de uma captura só é inventar linha do tempo.';
comment on column public.catalogo_captura.importado_em is
  'DIFERENTE de capturado_em de propósito. Se um dia forem iguais por acidente, a '
  'idade real do dado se perde e ninguém percebe.';


-- ─────────────────────────────────────────────────────────────────────
-- 2 · O PRODUTO
--
-- Note o que esta tabela NÃO tem: coluna de disponibilidade comercial.
-- Não é esquecimento. Se existisse, alguém preencheria 'SIM' porque o
-- produto está no catálogo — e essa é exatamente a inferência proibida.
-- Disponibilidade tem dono desde a 009: public.disponibilidade_comercial.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto (
  id                bigserial primary key,
  captura_id        bigint not null references public.catalogo_captura(id) on delete cascade,
  pais              pais not null,
  product_id        text not null,                 -- ADAMA-ES-<hash12>, estável
  nome_publicado    text not null,
  categoria         text not null check (categoria in (
                      'CONTROL_DE_MALAS_HIERBAS',   -- WEED CONTROL
                      'CONTROL_DE_ENFERMEDADES',    -- DISEASE CONTROL
                      'CONTROL_DE_PLAGAS',          -- PEST CONTROL
                      'MEJORA_DE_CULTIVOS',         -- CROP ENHANCEMENT
                      'NAO_SEI')),
  pagina_url        text not null,
  registration_id   text,                          -- NULL = a ficha não publica
  formulacao        text,
  composicao_texto  text,                          -- o que a ficha escreve, cru
  presenca_catalogo_publico text not null default 'YES'
                      check (presenca_catalogo_publico in ('YES','NAO_SEI')),
  nivel_evidencia   text not null default 'OBSERVED_ON_MANUFACTURER_PAGE'
                      check (nivel_evidencia = 'OBSERVED_ON_MANUFACTURER_PAGE'),
  raw_asset_id      bigint references public.raw_asset(id) on delete set null,
  CONSTRAINT produto_unico_por_captura UNIQUE (captura_id, product_id),
  CONSTRAINT presenca_no_catalogo_nao_e_prova_de_registro
    CHECK (presenca_catalogo_publico <> 'YES' OR true)
);
comment on table public.catalogo_produto is
  'O que o FABRICANTE publica. NÃO tem coluna de disponibilidade comercial de '
  'propósito: para os 56 produtos da captura ES de 2026-08-30, '
  'CURRENT_COMMERCIAL_AVAILABILITY é NAO_SEI, e quem quiser afirmar outra coisa '
  'precisa medir e escrever em public.disponibilidade_comercial, com fonte.';
comment on column public.catalogo_produto.categoria is
  'Categoria SEMÂNTICA publicada pelo fabricante. É daqui que o Design System '
  'deriva cor — a cor não mora aqui. HEX no banco de inteligência viraria um '
  'segundo dono do que já é decisão de marca.';
comment on column public.catalogo_produto.registration_id is
  'NULL significa A FICHA NÃO PUBLICA. Não significa produto sem registro: '
  'TRINITY PACK é um pack e não tem número único, e isso é diferente de ausência.';


-- ─────────────────────────────────────────────────────────────────────
-- 3 · DOCUMENTO
--
-- 147 referências, 138 bytes preservados, 9 links mortos. A trava aqui é a que
-- impede o erro mais caro: link falho virar "documento inexistente" ou, pior,
-- virar raw_asset preservado que não existe.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_documento (
  id              bigserial primary key,
  produto_id      bigint not null references public.catalogo_produto(id) on delete cascade,
  document_id     text not null,
  tipo            text not null check (tipo in (
                    'ADAMA_COMMERCIAL_LABEL','SDS','TECHNICAL_SHEET','REGISTRATION_SHEET',
                    'BROCHURE','CATALOG','GUIDE','TRIAL_DOCUMENT','OTHER_TECHNICAL_DOCUMENT')),
  tipo_evidencia  text not null,                   -- o que casou, e onde
  prova_de_que_e_documento text not null,          -- EXTENSAO_NA_URL, MIME_DECLARADO...
  url             text not null,
  pagina_origem   text not null,
  nome_arquivo    text,
  data_visivel    text,
  http_status     text,
  download_state  text not null check (download_state in
                    ('DOWNLOADED','FAILED','DUPLICATE_CONTENT','NOT_ATTEMPTED')),
  motivo_da_falha text,
  bytes           bigint,
  sha256          char(64),
  media_type      text,
  raw_asset_id    bigint references public.raw_asset(id) on delete restrict,
  CONSTRAINT documento_unico_por_produto UNIQUE (produto_id, document_id),

  -- Preservado exige as três provas juntas. Sem isto, "preservei" viraria opinião.
  CONSTRAINT preservado_exige_bytes_hash_e_asset
    CHECK (download_state <> 'DOWNLOADED'
           OR (bytes IS NOT NULL AND sha256 IS NOT NULL AND raw_asset_id IS NOT NULL)),

  -- LINK FALHO != DOCUMENTO INEXISTENTE. Ele fica na tabela, com o código do
  -- erro, e NUNCA aponta para raw_asset — porque não há bytes para apontar.
  CONSTRAINT falha_nao_vira_bytes_preservados
    CHECK (download_state <> 'FAILED'
           OR (raw_asset_id IS NULL AND motivo_da_falha IS NOT NULL
               AND http_status IS NOT NULL))
);
comment on constraint falha_nao_vira_bytes_preservados on public.catalogo_produto_documento is
  'Os 9 links que a ADAMA publica para PDFs do MAPA hoje devolvem 404, e dois '
  'daqueles domínios nem resolvem. Isso é link podre do fabricante, não ausência '
  'de documento — e não pode virar raw_asset nem sumir da contagem.';


-- ─────────────────────────────────────────────────────────────────────
-- 4 · CULTIVO — a distinção que mais dói se for perdida
--
-- 594 DECLARADOS no bloco "Cultivos" da ficha + 123 apenas CITADOS no corpo do
-- texto = 717 relações. Somar os dois grupos como se fossem a mesma coisa dá
-- números inflados: no milho seriam 35 produtos onde há 15.
--
-- origem_declaracao é NOT NULL. Não existe relação de cultivo sem dizer de onde
-- veio, então o colapso silencioso é impossível.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_cultivo (
  id                bigserial primary key,
  produto_id        bigint not null references public.catalogo_produto(id) on delete cascade,
  rotulo_publicado  text not null,                 -- como a ADAMA escreveu
  crop_id           bigint references public.crop(id) on delete restrict,
  rotulo_oficial    text,                          -- rótulo MAPA que casou
  origem_declaracao text not null check (origem_declaracao in
                      ('DECLARADO_NO_BLOCO_CULTIVOS','CITADO_NO_CORPO_DA_PAGINA')),
  qualidade_do_casamento text not null,            -- EXACT_OFFICIAL_LABEL, FORMA_CURTA...
  par_derivavel     boolean not null default false,
  nivel_evidencia   text not null default 'OBSERVED_ON_MANUFACTURER_PAGE',
  CONSTRAINT cultivo_unico_por_produto_e_origem
    UNIQUE (produto_id, rotulo_publicado, origem_declaracao)
);
comment on column public.catalogo_produto_cultivo.origem_declaracao is
  'DECLARADO = a ADAMA lista este cultivo no bloco "Cultivos" da ficha. CITADO = '
  'a palavra aparece no texto (comparação, contexto, nota de rodapé). NUNCA somar '
  'os dois: portfólio por cultura usa só DECLARADO.';


-- ─────────────────────────────────────────────────────────────────────
-- 5 · AGENTE (praga, doença, erva)
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_agente (
  id                bigserial primary key,
  produto_id        bigint not null references public.catalogo_produto(id) on delete cascade,
  rotulo_publicado  text not null,
  issue_id          bigint references public.issue(id) on delete restrict,
  rotulo_oficial    text,
  qualidade_do_casamento text not null,
  par_derivavel     boolean not null default false,
  nivel_evidencia   text not null default 'OBSERVED_ON_MANUFACTURER_PAGE',
  CONSTRAINT agente_unico_por_produto UNIQUE (produto_id, rotulo_publicado)
);


-- ─────────────────────────────────────────────────────────────────────
-- 5.1 · TERMO AMBÍGUO — 212 deles, e nenhum resolvido por palpite
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_termo_ambiguo (
  id             bigserial primary key,
  produto_id     bigint not null references public.catalogo_produto(id) on delete cascade,
  eixo           text not null check (eixo in ('CROP','ISSUE')),
  termo_na_pagina text not null,
  rotulos_candidatos jsonb not null,
  porque         text not null,
  CONSTRAINT ambiguo_unico UNIQUE (produto_id, eixo, termo_na_pagina)
);
comment on table public.catalogo_termo_ambiguo is
  'Termo que casa mais de um rótulo oficial. Fica AQUI, listado, em vez de ser '
  'resolvido por fuzzy-match silencioso e entrar como se fosse certeza.';


-- ─────────────────────────────────────────────────────────────────────
-- 6 · O PAR CULTIVO × AGENTE — só o que nasceu de UMA linha
--
-- A âncora é NOT NULL, e é isso que torna o cartesiano impossível: uma relação
-- inventada a partir de "lista de cultivos" × "lista de agentes" não tem índice
-- de tabela nem índice de linha para declarar, então não entra.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_cultivo_agente (
  id                bigserial primary key,
  produto_id        bigint not null references public.catalogo_produto(id) on delete cascade,
  cultivo_rotulo    text not null,
  agente_rotulo     text not null,
  crop_id           bigint references public.crop(id)  on delete restrict,
  issue_id          bigint references public.issue(id) on delete restrict,

  -- ÂNCORA OBRIGATÓRIA
  par_origem        text not null check (par_origem = 'SAME_TABLE_ROW'),
  ancora_secao      text not null,
  ancora_tabela     integer not null,
  ancora_linha      integer not null,
  ancora_texto      text not null,

  dose              text,
  bbch_de           text,
  bbch_ate          text,
  n_aplicacoes      text,
  intervalo_dias    text,
  volume_calda      text,
  prazo_seguranca   text,

  -- OS DOIS NÍVEIS, LADO A LADO. Confirmar no MAPA não apaga que a origem é
  -- afirmação do fabricante; guarda-se a cadeia inteira.
  nivel_evidencia_fabricante text not null default 'MANUFACTURER_TECHNICAL_CLAIM'
                      check (nivel_evidencia_fabricante = 'MANUFACTURER_TECHNICAL_CLAIM'),
  confirmacao_mapa  text not null default 'ADAMA_ONLY_NOT_TESTED' check (confirmacao_mapa in
                      ('ADAMA_CLAIM_MAPA_CONFIRMED','ADAMA_CLAIM_MAPA_NOT_CONFIRMED',
                       'ADAMA_ONLY_NOT_TESTED','AMBIGUOUS','NOT_TESTED')),
  mapa_id_cultivo   integer,
  mapa_id_plaga     integer,
  mapa_registros_no_par integer,
  mapa_registro_casado text,
  mapa_titular      text,
  mapa_estado       text,
  mapa_servidor_ts  text,
  nivel_evidencia_final text not null check (nivel_evidencia_final in
                      ('MANUFACTURER_TECHNICAL_CLAIM','REGULATORY_FACT')),

  CONSTRAINT par_unico_por_produto UNIQUE (produto_id, cultivo_rotulo, agente_rotulo),

  -- Confirmado exige a prova que o confirmou. "O MAPA confirmou" sem os ids da
  -- consulta é uma frase, não uma confirmação.
  CONSTRAINT confirmado_exige_os_ids_da_consulta
    CHECK (confirmacao_mapa <> 'ADAMA_CLAIM_MAPA_CONFIRMED'
           OR (mapa_id_cultivo IS NOT NULL AND mapa_id_plaga IS NOT NULL
               AND mapa_registros_no_par IS NOT NULL AND mapa_registro_casado IS NOT NULL)),

  -- Só sobe para FATO REGULATÓRIO quem foi confirmado. E quem foi confirmado
  -- não pode continuar rotulado como mero claim.
  CONSTRAINT fato_regulatorio_so_com_confirmacao
    CHECK ((nivel_evidencia_final = 'REGULATORY_FACT')
           = (confirmacao_mapa = 'ADAMA_CLAIM_MAPA_CONFIRMED'))
);
comment on table public.catalogo_produto_cultivo_agente is
  'SÓ o par que nasceu de UMA linha de tabela. A âncora NOT NULL é o que impede '
  'o produto cartesiano: relação derivada de duas listas independentes não tem '
  'linha de origem para declarar e não entra.';


-- ─────────────────────────────────────────────────────────────────────
-- 7 · CULTIVO × DOSE — parecido com o par, e NÃO é o par
--
-- A tabela dominante da ADAMA España é CULTIVO × DOSIS, sem coluna de agente.
-- Isso é dose por cultivo: evidência real, e não par. Estar em tabela SEPARADA
-- é o que impede a soma errada — não existe coluna de agente aqui para alguém
-- preencher depois "só para completar".
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_cultivo_dose (
  id                bigserial primary key,
  produto_id        bigint not null references public.catalogo_produto(id) on delete cascade,
  cultivo_rotulo    text not null,
  crop_id           bigint references public.crop(id) on delete restrict,
  dose              text not null,
  dose_unidade_origem text not null check (dose_unidade_origem in
                      ('CELULA_DA_LINHA','CABECALHO_DA_TABELA')),
  bbch_de           text,
  bbch_ate          text,
  volume_calda      text,
  n_aplicacoes      text,
  intervalo_dias    text,
  prazo_seguranca   text,
  ancora_secao      text not null,
  ancora_tabela     integer not null,
  ancora_linha      integer not null,
  ancora_texto      text not null,
  par_derivavel     boolean not null default false,
  porque_nao_ha_par text not null,
  nivel_evidencia   text not null default 'MANUFACTURER_TECHNICAL_CLAIM',
  CONSTRAINT dose_unica_por_produto_e_cultivo UNIQUE (produto_id, cultivo_rotulo, ancora_tabela, ancora_linha),
  CONSTRAINT dose_sem_agente_nunca_e_par CHECK (par_derivavel = false)
);
comment on constraint dose_sem_agente_nunca_e_par on public.catalogo_produto_cultivo_dose is
  'Por construção: a linha declara cultivo e dose e NÃO nomeia agente. Cruzar com '
  'agente citado noutro ponto da página é o cartesiano da seção 8.';


-- ─────────────────────────────────────────────────────────────────────
-- 8 · JANELA DE APLICAÇÃO
--
-- Só entram as janelas publicadas. Ausência NÃO é linha com CLOSED nem NONE:
-- é linha que não existe, e a contagem diz quantas foram publicadas.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_janela_aplicacao (
  id             bigserial primary key,
  produto_id     bigint not null references public.catalogo_produto(id) on delete cascade,
  cultivo_rotulo text,
  agente_rotulo  text,
  bbch_de        text,
  bbch_ate       text,
  n_aplicacoes   text,
  intervalo_dias text,
  marcadores     jsonb not null default '[]'::jsonb,
  ancora_secao   text not null,
  ancora_texto   text not null,
  nivel_evidencia text not null default 'MANUFACTURER_TECHNICAL_CLAIM'
);
comment on table public.catalogo_produto_janela_aplicacao is
  'Ausência de janela é AUSÊNCIA DE PUBLICAÇÃO, não janela fechada. Nunca inserir '
  'linha CLOSED/NONE para "completar" produto sem janela publicada. A leitura dos '
  'rótulos em PDF poderá acrescentar; até lá, o que não está aqui é NÃO PUBLICADO.';


-- ─────────────────────────────────────────────────────────────────────
-- 9 · SUBSTÂNCIA ATIVA — fonte e normalização convivem
--
-- A ADAMA escreve "Pendimentalina" numa ficha e "Pendimetalina" noutra, e
-- "FLUXAPIROSAD" onde a denominação comum é fluxapyroxad. Corrigir em silêncio
-- esconderia que a fonte é inconsistente com ela mesma. As duas colunas ficam.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_substancia (
  id                bigserial primary key,
  produto_id        bigint not null references public.catalogo_produto(id) on delete cascade,
  texto_publicado   text not null,                 -- exatamente como a ficha escreve
  nome_normalizado  text,                          -- NULL = ainda não normalizado
  regra_normalizacao text,
  concentracao      text,
  concentracao_unidade text,
  codigo_formulacao text,
  ambiguo           boolean not null default false,
  nivel_evidencia   text not null default 'OBSERVED_ON_MANUFACTURER_PAGE',
  CONSTRAINT substancia_unica_por_produto UNIQUE (produto_id, texto_publicado),
  CONSTRAINT normalizar_exige_dizer_a_regra
    CHECK (nome_normalizado IS NULL OR regra_normalizacao IS NOT NULL)
);
comment on column public.catalogo_produto_substancia.texto_publicado is
  'NUNCA sobrescrever com a forma normalizada. É a prova de que a fonte escreveu '
  'assim, e é o que permite achar depois que ela se contradiz entre fichas.';


-- ─────────────────────────────────────────────────────────────────────
-- 10 · MODO DE AÇÃO — código de verdade, não a palavra seguinte
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_modo_acao (
  id            bigserial primary key,
  produto_id    bigint not null references public.catalogo_produto(id) on delete cascade,
  esquema       text not null check (esquema in ('HRAC','FRAC','IRAC')),
  codigo        text not null,
  nivel_evidencia text not null default 'MANUFACTURER_TECHNICAL_CLAIM',
  CONSTRAINT modo_acao_unico UNIQUE (produto_id, esquema, codigo),

  -- Código é MAIÚSCULO e curto. Sem isto, "FRAC Grupo", "HRAC como" e
  -- "IRAC Grupo" entram como código — foi o que aconteceu na primeira leitura.
  CONSTRAINT codigo_de_moa_tem_forma_de_codigo
    CHECK (codigo ~ '^[A-Z0-9]{1,4}(/[A-Z0-9]{1,4})?$')
);


-- ─────────────────────────────────────────────────────────────────────
-- 11 · CLAIM — três classes, e nenhuma vira fato sozinha
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_claim (
  id            bigserial primary key,
  produto_id    bigint not null references public.catalogo_produto(id) on delete cascade,
  claim_id      text not null,
  classe        text not null check (classe in (
                  'MANUFACTURER_TECHNICAL_CLAIM',
                  'MANUFACTURER_COMMERCIAL_CLAIM',
                  'MANUFACTURER_REGULATORY_STATEMENT')),
  texto         text not null,
  secao         text,
  cultivo_rotulo text,
  agente_rotulo text,
  CONSTRAINT claim_unico_por_produto UNIQUE (produto_id, claim_id)
);
comment on table public.catalogo_produto_claim is
  'Claim é o que o FABRICANTE afirma. Não existe coluna para promover claim a '
  'fato: para virar fato regulatório é preciso confirmação oficial, e ela mora '
  'em catalogo_produto_cultivo_agente, com os ids da consulta ao MAPA.';


-- ─────────────────────────────────────────────────────────────────────
-- 12 · TECNOLOGIA E RELAÇÃO ENTRE PRODUTOS
--
-- Só o que o fabricante MARCOU (®/™) e disse na ficha. Compartilhar molécula
-- não cria relação; aparecer só na home não cria tecnologia de produto.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_produto_tecnologia (
  id             bigserial primary key,
  produto_id     bigint not null references public.catalogo_produto(id) on delete cascade,
  nome           text not null,
  marcador       text not null check (marcador in ('®','™')),
  porque_entrou  text not null,
  nivel_evidencia text not null default 'MANUFACTURER_TECHNICAL_CLAIM',
  CONSTRAINT tecnologia_unica UNIQUE (produto_id, nome)
);

create table public.catalogo_produto_relacao (
  id                 bigserial primary key,
  produto_id         bigint not null references public.catalogo_produto(id) on delete cascade,
  produto_relacionado_id bigint not null references public.catalogo_produto(id) on delete cascade,
  nome_relacionado   text not null,
  tipo               text not null check (tipo in (
                       'MENTIONED_ON_PAGE','COMPLEMENTS','ALTERNATIVE','SEQUENTIAL_PROGRAM',
                       'TANK_MIX','SAME_TECHNOLOGY_PLATFORM','REPLACES','RENAMED_FROM')),
  frase_que_sustenta text,
  nivel_evidencia    text not null default 'OBSERVED_ON_MANUFACTURER_PAGE',
  CONSTRAINT relacao_unica UNIQUE (produto_id, produto_relacionado_id, tipo),
  CONSTRAINT produto_nao_se_relaciona_consigo CHECK (produto_id <> produto_relacionado_id),

  -- Qualquer tipo mais específico que "foi citado" exige a frase que sustenta.
  -- Sem isto, "cita HERBOLEX" viraria "recomendado com HERBOLEX" sem que a
  -- página tenha dito isso em lugar nenhum.
  CONSTRAINT tipo_especifico_exige_frase
    CHECK (tipo = 'MENTIONED_ON_PAGE' OR frase_que_sustenta IS NOT NULL)
);


-- ─────────────────────────────────────────────────────────────────────
-- 13 · CROSSWALK CATÁLOGO × REGISTRO — relação, não fusão
--
-- 96 registros vigentes e 56 entradas de catálogo contam UNIDADES DIFERENTES.
-- Um produto pode ter vários registros; um registro pode não ter exposição
-- comercial. Por isso isto é uma tabela de RELAÇÃO e não uma coluna dentro de
-- catalogo_produto: fundir as duas entidades autorizaria a subtração 96−56.
-- ─────────────────────────────────────────────────────────────────────
create table public.catalogo_registro_crosswalk (
  id             bigserial primary key,
  captura_id     bigint not null references public.catalogo_captura(id) on delete cascade,
  produto_id     bigint references public.catalogo_produto(id) on delete cascade,
  registro_id    bigint references public.registro_regulatorio(id) on delete restrict,
  registration_id_texto text,
  estado         text not null check (estado in (
                   'MATCHED_EXACT','MATCHED_WITH_EVIDENCE','AMBIGUOUS',
                   'ADAMA_SITE_ONLY','ROPF_ONLY')),
  evidencia      text not null,

  -- Um lado sempre existe: ou é linha do catálogo, ou é linha do registro.
  CONSTRAINT crosswalk_tem_pelo_menos_um_lado
    CHECK (produto_id IS NOT NULL OR registro_id IS NOT NULL),

  -- Os quatro estados do lado catálogo exigem produto; ROPF_ONLY exige registro.
  CONSTRAINT estado_combina_com_o_lado_que_existe
    CHECK ((estado = 'ROPF_ONLY' AND produto_id IS NULL)
           OR (estado <> 'ROPF_ONLY' AND produto_id IS NOT NULL)),

  -- Nome comercial sozinho nunca fecha match. MATCHED_EXACT exige o número.
  CONSTRAINT match_exato_exige_numero_de_registro
    CHECK (estado <> 'MATCHED_EXACT' OR registration_id_texto IS NOT NULL)
);
comment on table public.catalogo_registro_crosswalk is
  'RELAÇÃO entre duas entidades que continuam separadas. Os quatro estados do '
  'lado catálogo (MATCHED_EXACT + MATCHED_WITH_EVIDENCE + AMBIGUOUS + '
  'ADAMA_SITE_ONLY) somam o total do catálogo — é essa partição que prova que '
  'cada número nasceu de classificar linha, e não de subtrair denominadores.';


-- ─────────────────────────────────────────────────────────────────────
-- 14 · ÍNDICES — as perguntas que a seção 24 faz
-- ─────────────────────────────────────────────────────────────────────
create index on public.catalogo_produto (captura_id, categoria);
create index on public.catalogo_produto (pais, product_id);
create index on public.catalogo_produto_cultivo (rotulo_oficial, origem_declaracao);
create index on public.catalogo_produto_cultivo (produto_id);
create index on public.catalogo_produto_agente (rotulo_oficial);
create index on public.catalogo_produto_documento (produto_id, tipo);
create index on public.catalogo_produto_documento (download_state);
create index on public.catalogo_produto_substancia (nome_normalizado);
create index on public.catalogo_registro_crosswalk (captura_id, estado);


-- ─────────────────────────────────────────────────────────────────────
-- 15 · RLS — mesma regra das outras tabelas (006)
-- ─────────────────────────────────────────────────────────────────────
alter table public.catalogo_captura                    enable row level security;
alter table public.catalogo_produto                    enable row level security;
alter table public.catalogo_produto_documento          enable row level security;
alter table public.catalogo_produto_cultivo            enable row level security;
alter table public.catalogo_produto_agente             enable row level security;
alter table public.catalogo_termo_ambiguo              enable row level security;
alter table public.catalogo_produto_cultivo_agente     enable row level security;
alter table public.catalogo_produto_cultivo_dose       enable row level security;
alter table public.catalogo_produto_janela_aplicacao   enable row level security;
alter table public.catalogo_produto_substancia         enable row level security;
alter table public.catalogo_produto_modo_acao          enable row level security;
alter table public.catalogo_produto_claim              enable row level security;
alter table public.catalogo_produto_tecnologia         enable row level security;
alter table public.catalogo_produto_relacao            enable row level security;
alter table public.catalogo_registro_crosswalk         enable row level security;
