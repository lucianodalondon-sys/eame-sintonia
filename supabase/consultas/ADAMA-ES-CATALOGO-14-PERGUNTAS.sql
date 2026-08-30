-- ═══════════════════════════════════════════════════════════════════════
-- AS 14 PERGUNTAS DA SEÇÃO 24 — respondidas POR QUERY, não lendo JSON.
--
-- Estado: as queries estão escritas e a resposta ESPERADA de cada uma está no
-- comentário, calculada a partir das mesmas linhas normalizadas que o importador
-- vai inserir. Elas ainda NÃO foram executadas contra o Postgres, porque não há
-- credencial nesta máquina — e "esperado" não é "medido".
--
-- Quando o banco existir:
--     psql "$SUPABASE_DB_URL" -f supabase/consultas/ADAMA-ES-CATALOGO-14-PERGUNTAS.sql
-- e cada resposta tem que bater com o comentário. Onde não bater, o import está
-- errado ou o artefato mudou — nos dois casos é achado, não detalhe.
--
-- Todas filtram pela captura, sempre. Sem isso, uma segunda captura do mesmo
-- catálogo somaria com a primeira e o número dobraria sem ninguém notar.
-- ═══════════════════════════════════════════════════════════════════════

\set captura '2026-08-30T03:19:24Z'

-- ── 1 · Quantos produtos o catálogo público ADAMA España tinha na captura?
-- ESPERADO: 56
select count(*) as produtos
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
where c.pais = 'ES' and c.fabricante = 'ADAMA' and c.fonte_versao = :'captura';


-- ── 2 · Quantos são Weed / Disease / Pest / Crop Enhancement?
-- ESPERADO: MALAS_HIERBAS 31 · ENFERMEDADES 16 · PLAGAS 8 · MEJORA 1  (soma 56)
select p.categoria, count(*) as n
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
where c.fonte_versao = :'captura'
group by p.categoria
order by n desc;


-- ── 3 · Quais produtos DECLARAM milho?
-- ESPERADO: 15 produtos
-- A regra inteira está no origem_declaracao. Trocar por "= qualquer" devolveria 35,
-- que é o número errado que esta separação existe para impedir.
select p.nome_publicado, p.categoria, p.registration_id
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
join public.catalogo_produto_cultivo cu on cu.produto_id = p.id
where c.fonte_versao = :'captura'
  and cu.rotulo_publicado in ('MAÍZ', 'MAÍZ DULCE')
  and cu.origem_declaracao = 'DECLARADO_NO_BLOCO_CULTIVOS'
group by p.nome_publicado, p.categoria, p.registration_id
order by p.categoria, p.nome_publicado;


-- ── 4 · Quais APENAS CITAM milho (e não declaram)?
-- ESPERADO: 20 produtos, e nenhum deles aparece na pergunta 3
select p.nome_publicado
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
join public.catalogo_produto_cultivo cu on cu.produto_id = p.id
where c.fonte_versao = :'captura'
  and cu.rotulo_publicado in ('MAÍZ', 'MAÍZ DULCE')
  and cu.origem_declaracao = 'CITADO_NO_CORPO_DA_PAGINA'
  and not exists (
        select 1 from public.catalogo_produto_cultivo d
        where d.produto_id = p.id
          and d.rotulo_publicado in ('MAÍZ', 'MAÍZ DULCE')
          and d.origem_declaracao = 'DECLARADO_NO_BLOCO_CULTIVOS')
group by p.nome_publicado
order by p.nome_publicado;


-- ── 5 · Quais produtos declaram olivar?
-- ESPERADO: 8
select p.nome_publicado, p.categoria
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
join public.catalogo_produto_cultivo cu on cu.produto_id = p.id
where c.fonte_versao = :'captura'
  and cu.rotulo_publicado = 'OLIVO'
  and cu.origem_declaracao = 'DECLARADO_NO_BLOCO_CULTIVOS'
group by p.nome_publicado, p.categoria
order by p.nome_publicado;


-- ── 6 · Quais declaram cereais de inverno?
-- ESPERADO: 15 produtos distintos (trigo 14 · cevada 14 · centeio 8 · triticale 6)
select p.nome_publicado,
       string_agg(distinct cu.rotulo_publicado, ', ' order by cu.rotulo_publicado) as cultivos
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
join public.catalogo_produto_cultivo cu on cu.produto_id = p.id
where c.fonte_versao = :'captura'
  and cu.rotulo_publicado in ('TRIGO', 'CEBADA', 'TRITICALE', 'CENTENO')
  and cu.origem_declaracao = 'DECLARADO_NO_BLOCO_CULTIVOS'
group by p.nome_publicado
order by p.nome_publicado;


-- ── 7 · Quais ingredientes ativos aparecem no catálogo?
-- ESPERADO: 50 textos distintos, em 73 ocorrências.
-- Note que se agrupa por texto_publicado, não por nome normalizado: a normalização
-- ainda não foi feita, e agrupar por um campo nulo devolveria uma linha só.
select s.texto_publicado, count(*) as produtos
from public.catalogo_produto_substancia s
join public.catalogo_produto p on p.id = s.produto_id
join public.catalogo_captura c on c.id = p.captura_id
where c.fonte_versao = :'captura'
group by s.texto_publicado
order by produtos desc, s.texto_publicado;


-- ── 8 · Quais códigos HRAC/FRAC/IRAC são explicitamente publicados?
-- ESPERADO: 12 distintos, em 17 ocorrências —
--   FRAC 3, 7, 29, M, M01 · HRAC 1, 2, 4, A, K1 · IRAC 1A, 3A
select m.esquema, m.codigo, count(*) as produtos
from public.catalogo_produto_modo_acao m
join public.catalogo_produto p on p.id = m.produto_id
join public.catalogo_captura c on c.id = p.captura_id
where c.fonte_versao = :'captura'
group by m.esquema, m.codigo
order by m.esquema, m.codigo;


-- ── 9 · Quais produtos casam exatamente com o ROPF?
-- ESPERADO: 41
select p.nome_publicado, x.registration_id_texto, x.evidencia
from public.catalogo_registro_crosswalk x
join public.catalogo_produto p on p.id = x.produto_id
join public.catalogo_captura c on c.id = x.captura_id
where c.fonte_versao = :'captura' and x.estado = 'MATCHED_EXACT'
order by p.nome_publicado;


-- ── 10 · Quais são ADAMA_SITE_ONLY?
-- ESPERADO: 12. Isto NÃO quer dizer "sem registro": quer dizer que esta captura não
-- conseguiu casar a ficha com um registro vigente do ROPF.
select p.nome_publicado, p.registration_id, x.evidencia
from public.catalogo_registro_crosswalk x
join public.catalogo_produto p on p.id = x.produto_id
join public.catalogo_captura c on c.id = x.captura_id
where c.fonte_versao = :'captura' and x.estado = 'ADAMA_SITE_ONLY'
order by p.nome_publicado;


-- ── 11 · Quais pares cultivo × problema são explicitamente publicados?
-- ESPERADO: 5, e exatamente 5. Cada um com âncora de linha.
select p.nome_publicado, r.cultivo_rotulo, r.agente_rotulo, r.dose,
       r.ancora_secao, r.ancora_tabela, r.ancora_linha
from public.catalogo_produto_cultivo_agente r
join public.catalogo_produto p on p.id = r.produto_id
join public.catalogo_captura c on c.id = p.captura_id
where c.fonte_versao = :'captura'
order by p.nome_publicado, r.cultivo_rotulo;


-- ── 12 · Quais deles foram confirmados pelo MAPA?
-- ESPERADO: 5 de 5, todos com nivel_evidencia_final = REGULATORY_FACT e com os ids
-- da consulta preenchidos. Confirmação sem os ids é frase, e o CHECK do schema recusa.
select p.nome_publicado, r.cultivo_rotulo, r.agente_rotulo,
       r.confirmacao_mapa, r.nivel_evidencia_final,
       r.mapa_id_cultivo, r.mapa_id_plaga, r.mapa_registros_no_par,
       r.mapa_registro_casado, r.mapa_titular, r.mapa_estado
from public.catalogo_produto_cultivo_agente r
join public.catalogo_produto p on p.id = r.produto_id
join public.catalogo_captura c on c.id = p.captura_id
where c.fonte_versao = :'captura'
order by r.confirmacao_mapa, p.nome_publicado;


-- ── 13 · Quais documentos de cada produto estão preservados?
-- ESPERADO HOJE: 0 preservados de 147 referências — nada foi enviado ao Storage
-- ainda. DEPOIS do upload: 138 preservados e 9 FAILED, que continuam FAILED.
-- A coluna preservado é derivada de raw_asset_id, não de opinião.
select p.nome_publicado,
       count(*)                                              as referencias,
       count(*) filter (where d.download_state = 'DOWNLOADED') as baixados,
       count(d.raw_asset_id)                                 as preservados,
       count(*) filter (where d.download_state = 'FAILED')    as links_falhos
from public.catalogo_produto_documento d
join public.catalogo_produto p on p.id = d.produto_id
join public.catalogo_captura c on c.id = p.captura_id
where c.fonte_versao = :'captura'
group by p.nome_publicado
order by p.nome_publicado;


-- ── 14 · Qual é CURRENT_COMMERCIAL_AVAILABILITY?
-- ESPERADO: NAO_SEI para os 56, e não por convenção — por CONSTRUÇÃO.
-- catalogo_produto não tem coluna de disponibilidade. A afirmação comercial mora em
-- public.disponibilidade_comercial, que nasce em NAO_SEI e exige fonte + data medida
-- para virar SIM ou NAO. Esta query junta as duas e mostra o vazio.
select p.nome_publicado,
       coalesce(dc.estado, 'NAO_SEI')            as current_commercial_availability,
       coalesce(dc.fonte, 'sem medicao comercial') as fonte
from public.catalogo_produto p
join public.catalogo_captura c on c.id = p.captura_id
left join public.disponibilidade_comercial dc
       on dc.pais = p.pais and dc.titular = 'ADAMA' and false  -- não há elo: é o ponto
where c.fonte_versao = :'captura'
order by p.nome_publicado;
