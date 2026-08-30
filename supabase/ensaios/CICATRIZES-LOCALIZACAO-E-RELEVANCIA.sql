-- ═══════════════════════════════════════════════════════════════════════
-- ENSAIO — NÃO É IMPORTAÇÃO. Banco DESCARTÁVEL.
--
-- Os casos de localização e relevância, montados com o mínimo necessário
-- para exercê-los. Reescrito na 018, quando o lugar do fato deixou de ser
-- uma coluna de `conteudo` e passou a ser a tabela `conteudo_lugar`.
--
-- ⚠️ Todo conteúdo aqui é FICTÍCIO e existe só para exercer o mecanismo.
-- Não descreve pessoa, canal, ocorrência ou publicação real. Nenhuma linha
-- pode entrar no banco canônico — há regressão que reprova se `ENSAIO-` sair
-- de supabase/ensaios/.
--
-- Os casos NÃO foram inventados para ficarem bonitos. Cada um é a FORMA de
-- um falso positivo já medido — no Brasil ou na Itália —, vestida com dado
-- fictício. Onde a forma veio do Brasil, o comentário diz; onde veio da
-- Itália, também. Fabricar um caso fácil quando já existe contraexemplo
-- medido seria escolher o adversário.
-- ═══════════════════════════════════════════════════════════════════════

begin;

insert into public.geografia (pais, regiao, provincia) values
 ('IT','Puglia','Foggia'),
 ('IT','Toscana',null),
 ('IT',null,null),
 ('ES','Andalucía','Jaén'),
 -- Toscana com três províncias: o caso dos 0..N lugares do fato.
 ('IT','Toscana','Grosseto'),
 ('IT','Toscana','Siena'),
 ('IT','Toscana','Arezzo'),
 -- Bergamo: a cicatriz italiana literal. Sede de empresa lida como foco.
 ('IT','Lombardia','Bergamo'),
 -- Torino e Piacenza: contexto de instituição e de palestrante.
 ('IT','Piemonte','Torino'),
 ('IT','Emilia-Romagna','Piacenza')
on conflict do nothing;

-- Município: o degrau que a escada não tinha antes da 018.
insert into public.geografia (pais, regiao, provincia, municipio)
values ('IT','Toscana','Grosseto','Manciano')
on conflict do nothing;

-- SOURCE_GEOGRAPHY != ADMIN_GEOGRAPHY. "l'Ovest" é um lugar e não é uma
-- unidade administrativa. Guardá-lo inteiro é o oposto de aproximá-lo para
-- a província mais parecida.
insert into public.geografia (pais, especie, nome_da_fonte)
values ('IT','DEFINIDA_PELA_FONTE','l''Ovest'),
       ('IT','ZONA_AGRONOMICA','areale cerealicolo del nord')
on conflict do nothing;

insert into public.organizacao (nome_canonico, tipo)
select 'ORG DE ENSAIO','outro'
 where not exists (select 1 from public.organizacao where nome_canonico='ORG DE ENSAIO');
insert into public.origem (organizacao_id, rotulo)
select id, 'ORIGEM DE ENSAIO' from public.organizacao where nome_canonico='ORG DE ENSAIO'
   and not exists (select 1 from public.origem where rotulo='ORIGEM DE ENSAIO');
insert into public.canal (origem_id, plataforma, channel_id, handle)
select o.id, 'web', 'ENSAIO-CANAL-01', 'ensaio'
  from public.origem o where o.rotulo='ORIGEM DE ENSAIO'
on conflict do nothing;

insert into public.collection_run
 (run_id, platform, actor, source_country, started_at, status, item_count_raw,
  cost_usd, cost_method, rule_version) values
 ('ENSAIO-RUN-CICATRIZ','web','ensaio','IT','2026-08-01T00:00:00Z','concluida',
  4, null, null, 'ensaio-v1'),
 -- Ator executou, item voltou, RAW não existe. É o defeito italiano como dado.
 ('ENSAIO-RUN-PAGO-SEM-BRUTO','apify','ator/ensaio','IT','2026-08-02T00:00:00Z','concluida',
  120, 3.5, 'PLATAFORMA_USAGE_TOTAL', 'ensaio-v1'),
 -- Rodada que não trouxe item: não há o que preservar, e isso NÃO é defeito.
 ('ENSAIO-RUN-VAZIA','apify','ator/ensaio','IT','2026-08-03T00:00:00Z','vazia',
  0, 0.4, 'PLATAFORMA_USAGE_TOTAL', 'ensaio-v1')
on conflict do nothing;

-- ── OS CONTEÚDOS ──────────────────────────────────────────────────────
-- O lugar da FONTE continua sendo coluna: um conteúdo tem uma fonte. O
-- lugar do FATO saiu daqui na 018, porque um conteúdo tem 0..N deles.
insert into public.conteudo
 (canal_id, run_id, tipo, content_id, titulo, publicado_em, hash_conteudo,
  source_geografia_id, rule_version)
select c.id, 'ENSAIO-RUN-CICATRIZ', v.tipo::tipo_conteudo, v.cid, v.titulo,
       v.pub::timestamptz, v.hash, gs.id, 'ensaio-v1'
  from (values
   ('ENSAIO-A','artigo','fonte em Foggia relata ocorrência na Toscana','2026-06-01T00:00:00Z',
    repeat('a',64),'Foggia'),
   ('ENSAIO-B','artigo','fonte em Foggia, sem lugar do fato','2026-06-02T00:00:00Z',
    repeat('b',64),'Foggia'),
   ('ENSAIO-C','artigo','ocorrência nomeando Jaén','2026-06-03T00:00:00Z',
    repeat('c',64),'Foggia'),
   ('ENSAIO-D','artigo','ocorrência na Itália, região não dita','2026-06-04T00:00:00Z',
    repeat('d',64),'Foggia'),
   ('ENSAIO-E','artigo','ocorrência com o lugar apenas mencionado','2026-06-05T00:00:00Z',
    repeat('e',64),'Foggia'),
   -- F · TRÊS lugares do fato num só documento. A forma brasileira: vários
   -- municípios reais no mesmo texto, e o sistema ficava com o primeiro.
   ('ENSAIO-F','artigo','campioni positivi de Grosseto, Siena e Arezzo','2026-06-06T00:00:00Z',
    repeat('f',64),'Foggia'),
   -- G · a sede lida como foco. Bergamo aparecia três vezes num artigo real
   -- italiano e não era recusada por lei nenhuma: era invisível.
   ('ENSAIO-G','artigo','empresa com sede em Bergamo fala de foco em Grosseto',
    '2026-06-07T00:00:00Z', repeat('g',64),'Foggia'),
   -- H · lista territorial ECONÔMICA. A forma brasileira mais cara.
   ('ENSAIO-H','artigo','atuamos em Torino, Piacenza e Bergamo','2026-06-08T00:00:00Z',
    repeat('h',64),'Foggia'),
   -- I · zona definida pela fonte. "l'Ovest" não é unidade administrativa.
   ('ENSAIO-I','artigo','pressão relatada no Ovest','2026-06-09T00:00:00Z',
    repeat('i',64),'Foggia'),
   -- J · tempo do fato retrospectivo: publicado em 2026, fato na safra 2025.
   ('ENSAIO-J','artigo','publicado em fevereiro de 2026 sobre a stagione 2025',
    '2026-02-13T00:00:00Z', repeat('j',64),'Foggia'),
   -- K · lugar que o gazetteer não conhece. NÃO é "não é um lugar".
   ('ENSAIO-K','artigo','foco constatado numa localidade fora da lista',
    '2026-06-11T00:00:00Z', repeat('k',64),'Foggia'),
   -- L · município: o degrau novo da escada.
   ('ENSAIO-L','artigo','foco constatado no comune di Manciano','2026-06-12T00:00:00Z',
    repeat('l',64),'Foggia'),
   -- M · amostras positivas. Sustentam OCORRÊNCIA, não incidência.
   ('ENSAIO-M','artigo','amostras positivas provenientes de Siena','2026-06-13T00:00:00Z',
    repeat('m',64),'Foggia')
  ) as v(cid,tipo,titulo,pub,hash,fonte)
  join public.canal c on c.channel_id='ENSAIO-CANAL-01'
  join public.geografia gs on gs.pais='IT' and gs.provincia=v.fonte
on conflict do nothing;

-- ── OS LUGARES ────────────────────────────────────────────────────────
-- Cada linha traz a própria proveniência: VALUE_PROVENANCE, não
-- ROW_PROVENANCE. O conteúdo tem uma fonte; cada LUGAR tem a sua evidência.
insert into public.conteudo_lugar
 (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
  tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
select ct.id, v.lugar, g.id, v.estado, v.papel, v.tipo, v.origem, v.evid, v.ancora,
       'ensaio-v1'
  from (values
   -- A · fato na Toscana, escrito. A fonte é de Foggia e continua sendo.
   ('ENSAIO-A','Toscana','IT','Toscana',null,null,'RESOLVIDO','FACT','FIELD_OBSERVATION',
    'ESCRITO','o texto afirma: "ocorrência observada em campos da Toscana"','osservata'),
   -- C · província nomeada
   ('ENSAIO-C','Jaén','ES','Andalucía','Jaén',null,'RESOLVIDO','FACT','FIELD_OBSERVATION',
    'ESCRITO','o texto afirma: "en la provincia de Jaén"','observada'),
   -- D · país conhecido, região não dita, e o lugar veio de menção
   ('ENSAIO-D','Italia','IT',null,null,null,'RESOLVIDO','FACT','REGIONAL_STATEMENT',
    'CITADO','o texto diz apenas "in Italia"','diffusione in'),
   -- E · menção sustentando o fato: o balde mais fraco
   ('ENSAIO-E','Toscana','IT','Toscana',null,null,'RESOLVIDO','FACT','OTHER',
    'CITADO','o nome da Toscana aparece no texto; o texto não afirma que o fato foi ali',
    'citato'),
   -- F · TRÊS lugares do fato. Nenhum é "o" lugar.
   ('ENSAIO-F','Grosseto','IT','Toscana','Grosseto',null,'RESOLVIDO','FACT',
    'DIAGNOSTIC_SAMPLE','ESCRITO','"campioni positivi provenienti da Grosseto, Siena e Arezzo"',
    'campioni positivi'),
   ('ENSAIO-F','Siena','IT','Toscana','Siena',null,'RESOLVIDO','FACT',
    'DIAGNOSTIC_SAMPLE','ESCRITO','"campioni positivi provenienti da Grosseto, Siena e Arezzo"',
    'campioni positivi'),
   ('ENSAIO-F','Arezzo','IT','Toscana','Arezzo',null,'RESOLVIDO','FACT',
    'DIAGNOSTIC_SAMPLE','ESCRITO','"campioni positivi provenienti da Grosseto, Siena e Arezzo"',
    'campioni positivi'),
   -- G · Bergamo é SEDE. Grosseto é o fato. As duas no mesmo documento.
   ('ENSAIO-G','Bergamo','IT','Lombardia','Bergamo',null,'RESOLVIDO','MENCAO_APENAS',null,
    'DA_FONTE','"azienda con sede a Bergamo" — endereço da entidade','sede'),
   ('ENSAIO-G','Grosseto','IT','Toscana','Grosseto',null,'RESOLVIDO','FACT','CONFIRMED_FOCUS',
    'ESCRITO','"focolaio constatato a Grosseto"','constatato'),
   -- H · lista econômica. Três lugares, nenhum fato.
   ('ENSAIO-H','Torino','IT','Piemonte','Torino',null,'RESOLVIDO','LISTA_TERRITORIAL',null,
    'LISTA_TERRITORIAL','"operiamo in Torino, Piacenza e Bergamo" — área de atuação','operiamo'),
   ('ENSAIO-H','Piacenza','IT','Emilia-Romagna','Piacenza',null,'RESOLVIDO','LISTA_TERRITORIAL',
    null,'LISTA_TERRITORIAL','"operiamo in Torino, Piacenza e Bergamo" — área de atuação','operiamo'),
   ('ENSAIO-H','Bergamo','IT','Lombardia','Bergamo',null,'RESOLVIDO','LISTA_TERRITORIAL',null,
    'LISTA_TERRITORIAL','"operiamo in Torino, Piacenza e Bergamo" — área de atuação','operiamo'),
   -- L · município: a escada chega mais fundo quando a evidência chega junto
   ('ENSAIO-L','Manciano','IT','Toscana','Grosseto','Manciano','RESOLVIDO','FACT',
    'CONFIRMED_FOCUS','ESCRITO','"focolaio constatato nel comune di Manciano"','constatato'),
   -- M · amostra positiva: ocorrência, não incidência
   ('ENSAIO-M','Siena','IT','Toscana','Siena',null,'RESOLVIDO','FACT','DIAGNOSTIC_SAMPLE',
    'ESCRITO','"campioni positivi provenienti da Siena"','campioni positivi')
  ) as v(cid,lugar,pais,reg,prov,mun,estado,papel,tipo,origem,evid,ancora)
  join public.conteudo ct on ct.content_id = v.cid
  join public.geografia g on g.pais = v.pais::pais and g.especie='ADMIN'
       and g.regiao is not distinct from v.reg
       and g.provincia is not distinct from v.prov
       and g.municipio is not distinct from v.mun
on conflict do nothing;

-- I · a zona definida pela fonte, que não tem província nenhuma
insert into public.conteudo_lugar
 (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
  tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
select ct.id, 'l''Ovest', g.id, 'RESOLVIDO', 'FACT', 'REGIONAL_STATEMENT',
       'ESCRITO', '"pressione rilevata nell''Ovest" — recorte da própria fonte',
       'rilevata', 'ensaio-v1'
  from public.conteudo ct, public.geografia g
 where ct.content_id='ENSAIO-I' and g.nome_da_fonte='l''Ovest'
on conflict do nothing;

-- K · NOT_IN_GAZETTEER != NOT_A_PLACE. O nome fica; a resolução não existe.
insert into public.conteudo_lugar
 (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
  tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
select ct.id, 'Roccalbegna', null, 'NAO_ESTA_NO_GAZETTEER', 'FACT', 'CONFIRMED_FOCUS',
       'ESCRITO', '"focolaio constatato a Roccalbegna" — a nossa lista não tem este comune',
       'constatato', 'ensaio-v1'
  from public.conteudo ct where ct.content_id='ENSAIO-K'
on conflict do nothing;

-- J · o tempo do fato, separado da data da publicação
update public.conteudo set
  fact_tempo_texto = 'stagione 2025',
  fact_tempo_resolucao = 'SEASON',
  fact_tempo_evidencia = 'o texto diz "durante la stagione 2025 sono stati osservati"',
  fact_tempo_origem = 'AMARRADO_AO_ACONTECIMENTO'
 where content_id = 'ENSAIO-J';

insert into public.conteudo_lugar
 (conteudo_id, lugar_texto, geografia_id, estado_do_lugar, papel,
  tipo_de_evidencia, origem_do_dado, evidencia, ancora, rule_version)
select ct.id, 'Grosseto', g.id, 'RESOLVIDO', 'FACT', 'FIELD_OBSERVATION',
       'ESCRITO', '"osservati a Grosseto durante la stagione 2025"', 'osservati', 'ensaio-v1'
  from public.conteudo ct, public.geografia g
 where ct.content_id='ENSAIO-J' and g.pais='IT' and g.provincia='Grosseto'
   and g.municipio is null
on conflict do nothing;

-- ── AS QUATRO ESPÉCIES DE LUGAR DO SUJEITO ────────────────────────────
-- O caso obrigatório: pesquisador baseado em Foggia, instituição atuando
-- nacionalmente, audiência italiana — e o fato em Grosseto, que é do
-- conteúdo e não dele. Os quatro coexistem sem sobrescrita.
insert into public.pessoa (nome_exibicao, identidade_status)
select 'PESQUISADOR DE ENSAIO', 'CANDIDATA'
 where not exists (select 1 from public.pessoa where nome_exibicao='PESQUISADOR DE ENSAIO');
insert into public.origem (pessoa_id, rotulo)
select p.id, 'ORIGEM ENSAIO PESQUISADOR' from public.pessoa p
 where p.nome_exibicao='PESQUISADOR DE ENSAIO'
   and not exists (select 1 from public.origem o where o.pessoa_id = p.id);

insert into public.origem_lugar
 (origem_id, geografia_id, papel, origem_do_dado, evidencia, rule_version)
select o.id, g.id, v.papel, v.od, v.evid, 'ensaio-v1'
  from (values
   ('BASE','Foggia','DECLARADO_NO_PERFIL',
    'o perfil declara "Foggia, Puglia" no campo de localização'),
   ('OPERATING',null,'ESCRITO_NO_TEXTO',
    'a bio diz que a instituição atua em todo o território nacional'),
   ('INFLUENCE',null,'ESCRITO_NO_TEXTO',
    'a audiência declarada pela plataforma é italiana')
  ) as v(papel,prov,od,evid)
  join public.origem o on o.rotulo='ORIGEM ENSAIO PESQUISADOR'
  join public.geografia g on g.pais='IT' and g.especie='ADMIN'
       and g.provincia is not distinct from v.prov
       and g.regiao is not distinct from (case when v.prov='Foggia' then 'Puglia' end)
       and g.municipio is null
on conflict do nothing;

-- ── RELEVÂNCIA · as cicatrizes italianas como dado ────────────────────
insert into public.crop (codigo) values ('ENSAIO_CROP_A'),('ENSAIO_CROP_B')
on conflict do nothing;
insert into public.issue (codigo, classe) values
 ('ENSAIO_ISSUE_A','DISEASE'),('ENSAIO_ISSUE_B','PEST') on conflict do nothing;
insert into public.crop_issue (crop_id, issue_id)
select c.id, i.id from public.crop c, public.issue i
 where c.codigo like 'ENSAIO_CROP_%' and i.codigo like 'ENSAIO_ISSUE_%'
on conflict do nothing;

insert into public.conteudo_crop_issue (conteudo_id, crop_issue_id, relacao, evidencia, sinal, rule_version)
select ct.id, ci.id, v.rel, v.ev, v.sinal, 'ensaio-v1'
  from (values
   ('ENSAIO-A','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'o texto afirma a ocorrência do problema naquela cultura','EXACT_SIGNAL'),
   ('ENSAIO-A','ENSAIO_CROP_B','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'ocorrência declarada, mas em outra cultura','NAO_SEI'),
   ('ENSAIO-A','ENSAIO_CROP_A','ENSAIO_ISSUE_B','OCORRENCIA_DECLARADA',
    'ocorrência declarada, mas de outro problema','NAO_SEI'),
   ('ENSAIO-C','ENSAIO_CROP_A','ENSAIO_ISSUE_A','COOCORRENCIA_TEXTUAL',
    'os dois termos aparecem no mesmo parágrafo, sem afirmação','NAO_SEI'),
   ('ENSAIO-B','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'ocorrência declarada, sem lugar do fato sustentado','NAO_SEI'),
   ('ENSAIO-D','ENSAIO_CROP_A','ENSAIO_ISSUE_A','ESPECTRO_DE_PRODUTO',
    'o problema aparece na lista de espectro do rótulo','NAO_SEI'),
   ('ENSAIO-E','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'ocorrência declarada; o lugar do fato veio de menção, não de afirmação','NAO_SEI'),
   ('ENSAIO-F','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'amostras positivas de três províncias','NAO_SEI'),
   ('ENSAIO-G','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'foco constatado; a sede da empresa aparece no mesmo texto','NAO_SEI'),
   ('ENSAIO-H','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'lista de atuação comercial, sem acontecimento','NAO_SEI'),
   ('ENSAIO-J','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'observação de campo na safra anterior à publicação','NAO_SEI'),
   ('ENSAIO-M','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'amostras positivas de uma província','NAO_SEI')
  ) as v(cid,crop,issue,rel,ev,sinal)
  join public.conteudo ct on ct.content_id = v.cid
  join public.crop c on c.codigo = v.crop
  join public.issue i on i.codigo = v.issue
  join public.crop_issue ci on ci.crop_id = c.id and ci.issue_id = i.id
on conflict do nothing;

-- ── TENTATIVAS · o mundo, a instalação e nós ──────────────────────────
insert into public.tentativa_de_coleta (run_id, alvo, estado, motivo, observado_em, rule_version) values
 ('ENSAIO-RUN-CICATRIZ','lugar declarado no perfil X','RESPONDEU_SEM_O_CAMPO',
  'o mundo respondeu e o perfil não declara lugar','2026-08-01T01:00:00Z','ensaio-v1'),
 ('ENSAIO-RUN-CICATRIZ','lugar declarado no perfil Y','LOGIN_WALL',
  'a plataforma exigiu conta — ninguém chegou a perguntar','2026-08-01T01:05:00Z','ensaio-v1'),
 ('ENSAIO-RUN-CICATRIZ','lugar declarado no perfil Z','NAO_TESTADO',
  'a rota não foi executada nesta rodada','2026-08-01T01:10:00Z','ensaio-v1'),
 ('ENSAIO-RUN-CICATRIZ','lugar declarado no perfil W','SEM_CHECKPOINT_NAO_GASTEI',
  'a nossa trava barrou antes de gastar','2026-08-01T01:15:00Z','ensaio-v1')
on conflict do nothing;

commit;
