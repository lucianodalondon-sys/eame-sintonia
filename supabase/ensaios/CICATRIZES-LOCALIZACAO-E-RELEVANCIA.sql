-- ═══════════════════════════════════════════════════════════════════════
-- ENSAIO — NÃO É IMPORTAÇÃO. Banco DESCARTÁVEL.
--
-- Os cinco casos de localização e os quatro de relevância que a missão
-- exige, montados com o mínimo necessário para exercê-los.
--
-- ⚠️ Todo conteúdo aqui é FICTÍCIO e existe só para exercer o mecanismo.
-- Não descreve pessoa, canal, ocorrência ou publicação real. Nenhuma linha
-- pode entrar no banco canônico — há regressão que reprova se `ENSAIO-` sair
-- de supabase/ensaios/.
--
-- O caso A é a cicatriz italiana escrita como dado: um pesquisador de
-- Foggia (Puglia) falando de ocorrência observada na Toscana. Foggia não
-- pode virar o lugar do fato.
-- ═══════════════════════════════════════════════════════════════════════

begin;

insert into public.geografia (pais, regiao, provincia) values
 ('IT','Puglia','Foggia'),
 ('IT','Toscana',null),
 ('IT',null,null),
 ('ES','Andalucía','Jaén')
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

-- ── OS CINCO CASOS DE LOCALIZAÇÃO ─────────────────────────────────────
insert into public.conteudo
 (canal_id, run_id, tipo, content_id, titulo, publicado_em, hash_conteudo,
  source_geografia_id, fact_geografia_id, fact_geografia_origem,
  fact_geografia_evidencia, rule_version)
select c.id, 'ENSAIO-RUN-CICATRIZ', v.tipo::tipo_conteudo, v.cid, v.titulo,
       v.pub::timestamptz, v.hash, gs.id, gf.id, v.origem, v.evid, 'ensaio-v1'
  from (values
   -- A · a fonte é de Foggia e o fato é da Toscana
   ('ENSAIO-A','artigo','fonte em Foggia relata ocorrência na Toscana','2026-06-01T00:00:00Z',
    repeat('a',64),'IT','Puglia','Foggia','IT','Toscana',null,'ESCRITO',
    'o texto afirma: "ocorrência observada em campos da Toscana"'),
   -- B · a fonte tem lugar, o fato não tem
   ('ENSAIO-B','artigo','fonte em Foggia, sem lugar do fato','2026-06-02T00:00:00Z',
    repeat('b',64),'IT','Puglia','Foggia',null,null,null,null,null),
   -- C · o fato nomeia a província
   ('ENSAIO-C','artigo','ocorrência nomeando Jaén','2026-06-03T00:00:00Z',
    repeat('c',64),'IT','Puglia','Foggia','ES','Andalucía','Jaén','ESCRITO',
    'o texto afirma: "en la provincia de Jaén"'),
   -- D · país conhecido, região desconhecida
   ('ENSAIO-D','artigo','ocorrência na Itália, região não dita','2026-06-04T00:00:00Z',
    repeat('d',64),'IT','Puglia','Foggia','IT',null,null,'CITADO',
    'o texto diz apenas "in Italia"')
  ) as v(cid,tipo,titulo,pub,hash,sp,sr,spv,fp,fr,fpv,origem,evid)
  join public.canal c on c.channel_id='ENSAIO-CANAL-01'
  left join public.geografia gs on gs.pais=v.sp::pais
        and gs.regiao is not distinct from v.sr and gs.provincia is not distinct from v.spv
  left join public.geografia gf on gf.pais=v.fp::pais
        and gf.regiao is not distinct from v.fr and gf.provincia is not distinct from v.fpv
 where v.fp is null or gf.id is not null;

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
   -- sinal exato: cultura, problema, país e evidência escrita
   ('ENSAIO-A','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'o texto afirma a ocorrência do problema naquela cultura','EXACT_SIGNAL'),
   -- RIGHT_CLASS + WRONG_CROP: mesma classe de problema, cultura errada
   ('ENSAIO-A','ENSAIO_CROP_B','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'ocorrência declarada, mas em outra cultura','NAO_SEI'),
   -- RIGHT_CROP + WRONG_ISSUE
   ('ENSAIO-A','ENSAIO_CROP_A','ENSAIO_ISSUE_B','OCORRENCIA_DECLARADA',
    'ocorrência declarada, mas de outro problema','NAO_SEI'),
   -- só apareceram juntos no texto — o balde mais fraco
   ('ENSAIO-C','ENSAIO_CROP_A','ENSAIO_ISSUE_A','COOCORRENCIA_TEXTUAL',
    'os dois termos aparecem no mesmo parágrafo, sem afirmação','NAO_SEI'),
   -- fato sem lugar sustentado: serve de contexto
   ('ENSAIO-B','ENSAIO_CROP_A','ENSAIO_ISSUE_A','OCORRENCIA_DECLARADA',
    'ocorrência declarada, sem lugar do fato sustentado','NAO_SEI'),
   -- lista de rótulo: espectro, não ocorrência
   ('ENSAIO-D','ENSAIO_CROP_A','ENSAIO_ISSUE_A','ESPECTRO_DE_PRODUTO',
    'o problema aparece na lista de espectro do rótulo','NAO_SEI')
  ) as v(cid,crop,issue,rel,ev,sinal)
  join public.conteudo ct on ct.content_id = v.cid
  join public.crop c on c.codigo = v.crop
  join public.issue i on i.codigo = v.issue
  join public.crop_issue ci on ci.crop_id = c.id and ci.issue_id = i.id
on conflict do nothing;

-- ── O QUE A CONFERÊNCIA DE LOCALIZAÇÃO EXIGIU (017) ───────────────────
-- ENSAIO-E existe para exercer PLACE_MENTION != FACT_LOCATION num caso que
-- de outro modo seria sinal exato: cultura certa, problema certo, país
-- certo, ocorrência declarada — e o lugar do fato sustentado só por MENÇÃO.
insert into public.conteudo
 (canal_id, run_id, tipo, content_id, titulo, publicado_em, hash_conteudo,
  source_geografia_id, fact_geografia_id, fact_geografia_origem,
  fact_geografia_evidencia, rule_version)
select c.id, 'ENSAIO-RUN-CICATRIZ', 'artigo'::tipo_conteudo, 'ENSAIO-E',
       'ocorrência declarada com o lugar apenas mencionado',
       '2026-06-05T00:00:00Z'::timestamptz, repeat('e',64),
       gs.id, gf.id, 'CITADO',
       'o nome da Toscana aparece no texto; o texto não afirma que o fato foi ali',
       'ensaio-v1'
  from public.canal c
  join public.geografia gs on gs.pais='IT' and gs.provincia='Foggia'
  join public.geografia gf on gf.pais='IT' and gf.regiao='Toscana'
                          and gf.provincia is null
 where c.channel_id='ENSAIO-CANAL-01'
on conflict do nothing;

insert into public.conteudo_crop_issue
 (conteudo_id, crop_issue_id, relacao, evidencia, sinal, rule_version)
select ct.id, ci.id, 'OCORRENCIA_DECLARADA',
       'ocorrência declarada; o lugar do fato veio de menção, não de afirmação',
       'NAO_SEI', 'ensaio-v1'
  from public.conteudo ct
  join public.crop c on c.codigo='ENSAIO_CROP_A'
  join public.issue i on i.codigo='ENSAIO_ISSUE_A'
  join public.crop_issue ci on ci.crop_id=c.id and ci.issue_id=i.id
 where ct.content_id='ENSAIO-E'
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
  'a nossa trava barrou antes de gastar','2026-08-01T01:15:00Z','ensaio-v1');

commit;
