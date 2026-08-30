-- ═══════════════════════════════════════════════════════════════════════
-- EAME SINTONIA — MIGRATION 017
-- O QUE A CONFERÊNCIA DE LOCALIZAÇÃO ACHOU
--
-- A rodada anterior fechou o contrato de localização e o marcou completo.
-- Esta rodada o conferiu contra dez cicatrizes brasileiras mais novas, e o
-- contrato NÃO passou inteiro. Seis lacunas ficaram registradas na matriz;
-- quatro delas são falta de modelagem e continuam abertas, DECLARADAS.
--
-- Duas produziam RESPOSTA ERRADA, e por isso são corrigidas aqui:
--
--   I · PUBLISHED_AT != FACT_TIME
--       f_relevancia_ao_caso tratava a data de PUBLICAÇÃO como se fosse a
--       data do FATO. Publicado depois do fim da janela do caso devolvia
--       UNRELATED — e um documento publicado em setembro pode perfeitamente
--       relatar um fato de junho. O defeito é meu, da 015.
--
--   B · PLACE_MENTION != FACT_LOCATION
--       a 015 escreve que CITADO é "o balde mais fraco, e lá ele é filtro
--       de leitura, nunca fonte nova" — e a trava deixa CITADO sustentar
--       sozinho o lugar do fato. O comentário e a trava discordavam.
--
-- NÃO EXECUTADA em Supabase. PostgreSQL 16 local e descartável.
-- ═══════════════════════════════════════════════════════════════════════

-- ── I · a data de publicação não é a data do fato ─────────────────────
-- O que muda: publicado DEPOIS do fim da janela deixa de ser UNRELATED.
-- Sem tempo do fato, a publicação não desqualifica o conteúdo — ela só
-- deixa de sustentá-lo, e isso se chama CONTEXT_ONLY.
--
-- Publicado ANTES do início da janela continua RETROSPECTIVE, e esse é o
-- único sentido em que a data de publicação decide algo: um documento não
-- relata o futuro. A inferência vale numa direção só.
create or replace function public.f_relevancia_ao_caso(
  p_conteudo_crop_issue bigint, p_crop text, p_issue text, p_pais pais,
  p_janela_inicio date default null, p_janela_fim date default null)
returns table (relevancia text, porque text) language sql stable as $$
  select case
    when cc.relacao = 'COOCORRENCIA_TEXTUAL' then 'CONTEXT_ONLY'
    when c.codigo is distinct from p_crop     then 'UNRELATED'
    when i.codigo is distinct from p_issue    then 'UNRELATED'
    when gf.pais is not null and gf.pais <> p_pais then 'UNRELATED'
    when gf.pais is null                      then 'CONTEXT_ONLY'
    -- Um documento não relata o futuro: publicado antes do início da
    -- janela, o que ele conta é anterior a ela.
    when p_janela_inicio is not null and ct.publicado_em is not null
         and ct.publicado_em::date < p_janela_inicio then 'RETROSPECTIVE'
    -- Publicado depois do FIM da janela não diz nada sobre quando o fato
    -- aconteceu. Antes devolvia UNRELATED, e era resposta errada.
    when p_janela_fim is not null and ct.publicado_em is not null
         and ct.publicado_em::date > p_janela_fim then 'CONTEXT_ONLY'
    -- Lugar do fato sustentado só por MENÇÃO não é sinal exato do caso.
    when ct.fact_geografia_origem = 'CITADO' then 'CONTEXT_ONLY'
    when cc.relacao in ('ESPECTRO_DE_PRODUTO') then 'CONTEXT_ONLY'
    else 'EXACT_SIGNAL'
  end,
  case
    when cc.relacao = 'COOCORRENCIA_TEXTUAL'
      then 'só apareceram juntos no texto — coocorrência não é ocorrência'
    when c.codigo is distinct from p_crop
      then 'cultura errada: ' || coalesce(c.codigo,'NAO_SEI') || ' != ' || p_crop
    when i.codigo is distinct from p_issue
      then 'problema errado: ' || coalesce(i.codigo,'NAO_SEI') || ' != ' || p_issue
    when gf.pais is not null and gf.pais <> p_pais
      then 'o fato é de outro país: ' || gf.pais::text || ' != ' || p_pais::text
    when gf.pais is null
      then 'sem lugar do fato sustentado — serve de contexto, não de sinal do caso'
    when p_janela_inicio is not null and ct.publicado_em is not null
         and ct.publicado_em::date < p_janela_inicio
      then 'publicado antes da janela do caso (' || ct.publicado_em::date::text
           || '): um documento não relata o futuro'
    when p_janela_fim is not null and ct.publicado_em is not null
         and ct.publicado_em::date > p_janela_fim
      then 'publicado depois da janela (' || ct.publicado_em::date::text
           || '), e o TEMPO DO FATO não é conhecido — a data de publicação não '
              'desqualifica o conteúdo, apenas não o sustenta'
    when ct.fact_geografia_origem = 'CITADO'
      then 'o lugar do fato está sustentado por MENÇÃO — o nome do lugar aparece '
           'no texto, e mencionar não é afirmar que o fato foi ali'
    when cc.relacao = 'ESPECTRO_DE_PRODUTO'
      then 'lista de rótulo é espectro de produto, não ocorrência observada'
    else 'cultura, problema, país e janela conferem, com evidência escrita'
  end
  from public.conteudo_crop_issue cc
  join public.conteudo ct  on ct.id = cc.conteudo_id
  join public.crop_issue ci on ci.id = cc.crop_issue_id
  join public.crop  c on c.id = ci.crop_id
  join public.issue i on i.id = ci.issue_id
  left join public.geografia gf on gf.id = ct.fact_geografia_id
 where cc.id = p_conteudo_crop_issue;
$$;

comment on function public.f_relevancia_ao_caso is
  'PUBLISHED_AT != FACT_TIME. A data de publicação decide numa direção só: antes da '
  'janela é RETROSPECTIVE, porque documento não relata o futuro. Depois da janela NÃO '
  'é UNRELATED — sem tempo do fato, publicar tarde não desqualifica nada.';


-- ── B · menção não sustenta lugar do fato como afirmação ──────────────
-- A trava da 015 continua onde está: CITADO segue ADMISSÍVEL como registro,
-- porque proibi-lo apagaria a distinção entre "mencionado" e "não medido" —
-- e as duas são respostas diferentes. O que muda é que a menção deixa de
-- passar despercebida: ela vira coluna, à vista, e quem consome decide.
-- REPLAY-SAFE: esta view é redefinida por uma migration posterior, e
-- `create or replace` recusa reescrever view cuja forma mudou. O drop
-- faz cada migration ser dona inteira do objeto no ponto dela da cadeia.
drop view if exists public.v_conteudo_localizacao;
create view public.v_conteudo_localizacao with (security_invoker = on) as
select c.id as conteudo_id,
       gs.pais as source_country,
       coalesce(gs.provincia, gs.regiao, 'PAÍS') as source_place,
       gf.pais as fact_country,
       coalesce(gf.provincia, gf.regiao, 'PAÍS') as fact_place,
       c.fact_geografia_origem,
       c.fact_geografia_evidencia,
       public.precisao_da_geografia(c.fact_geografia_id) as fact_precision,
       c.fact_geografia_id is null as fact_location_desconhecido,
       gs.pais is distinct from gf.pais as fonte_e_fato_em_paises_diferentes,
       -- PLACE_MENTION != FACT_LOCATION, dito em voz alta.
       c.fact_geografia_id is not null and c.fact_geografia_origem = 'CITADO'
         as fact_sustentado_apenas_por_mencao,
       -- A força da sustentação, para que ninguém precise reconstruí-la.
       case when c.fact_geografia_id is null then 'NAO_SUSTENTADO'
            when c.fact_geografia_origem = 'ESCRITO' then 'AFIRMADO_NO_TEXTO'
            when c.fact_geografia_origem = 'CITADO'  then 'APENAS_MENCIONADO'
            else 'NAO_ADMISSIVEL' end as fact_forca_da_sustentacao
  from public.conteudo c
  left join public.geografia gs on gs.id = c.source_geografia_id
  left join public.geografia gf on gf.id = c.fact_geografia_id;

comment on view public.v_conteudo_localizacao is
  'SOURCE_LOCATION != FACT_LOCATION, e PLACE_MENTION != FACT_LOCATION. A menção '
  'continua podendo ser registrada — mencionado e não-medido são respostas '
  'diferentes —, mas nunca chega ao consumidor disfarçada de afirmação.';


-- ── O QUE ESTA MIGRATION NÃO CONSERTA ─────────────────────────────────
-- Quatro lacunas da conferência continuam ABERTAS, e ficam escritas aqui
-- para que ninguém as encontre por acidente depois:
--
--   A · BASE != OPERATING != INFLUENCE != FACT
--       conteudo tem source_geografia_id e fact_geografia_id, e mais nada.
--       Onde alguém está sediado, onde atua e até onde sua fala alcança são
--       três coisas, e as três colapsam em "a praça da fonte".
--
--   E · um conteúdo tem 0..N lugares de fato, não 0..1
--       fact_geografia_id é UMA coluna. Um documento que relata ocorrência
--       na Toscana E na Puglia não é representável hoje.
--
--   F · a escada de precisão para em PROVINCIA
--       precisao_da_geografia devolve PAIS/REGIAO/PROVINCIA/NOT_KNOWN. Não
--       há município, talhão nem coordenada, e não há nível supranacional.
--
--   G · TERRITORIAL_LIST != FACT_LIST no eixo da geografia
--       existe guarda no eixo do produto (ESPECTRO_DE_PRODUTO vira
--       CONTEXT_ONLY) e NÃO existe a equivalente no eixo do lugar: uma
--       lista de "regiões onde X está registrado" não tem como se declarar
--       lista territorial, e cada região dela se leria como lugar de fato.
--
-- Estão na matriz das cicatrizes como PARTIAL/ABSENT com a ação mínima.
-- Não foram consertadas porque reabrir a modelagem de localização na
-- véspera do portão de importação é exatamente o que a missão proíbe.
