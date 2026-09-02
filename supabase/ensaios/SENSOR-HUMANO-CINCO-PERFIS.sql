-- ═══════════════════════════════════════════════════════════════════════
-- ENSAIO — NÃO É IMPORTAÇÃO. Banco DESCARTÁVEL.
--
-- AGGREGATOR / SOURCE / COLLECTOR ≠ HUMAN SENSOR PERSON.
--
-- No Brasil o agregador entrou como se fosse gente: um canal que republica
-- o que outros escreveram virou "pessoa que fala do campo", e a contagem
-- de vozes humanas subiu sem que uma única voz humana nova existisse.
-- Aqui os cinco casos que a missão exige viram cinco linhas, para que a
-- recusa seja EXECUTÁVEL e não uma frase num documento.
--
-- ⚠️ Tudo aqui é FICTÍCIO. Nenhum perfil, handle, pessoa ou organização
-- descreve alguém real. Nada pode entrar no banco canônico.
--
-- Os tipos NÃO são classificados por volume, por número de posts, por
-- quantidade de links nem por qualquer heurística fraca. Cada um traz a
-- EVIDÊNCIA escrita que sustenta a leitura da página — e o caso que não
-- tem evidência fica NOT_KNOWN, que é diferente de "não é pessoa".
-- ═══════════════════════════════════════════════════════════════════════

begin;

insert into public.pessoa (nome_exibicao, identidade_status)
select 'PESSOA DE ENSAIO — AGRÔNOMA', 'CANDIDATA'
 where not exists (select 1 from public.pessoa
                    where nome_exibicao='PESSOA DE ENSAIO — AGRÔNOMA');

insert into public.organizacao (nome_canonico, tipo)
select v.n, 'outro' from (values
  ('COOPERATIVA DE ENSAIO'),
  ('AGREGADOR DE ENSAIO'),
  ('BUSCADOR DE ENSAIO'),
  ('ORG DO PERFIL SEM FICHA')
) v(n)
 where not exists (select 1 from public.organizacao where nome_canonico = v.n);

-- Uma origem por dono. `origem_por_pessoa_idx` e `origem_por_organizacao_idx`
-- já garantem isso; aqui só não insistimos contra elas.
insert into public.origem (pessoa_id, rotulo)
select p.id, 'ORIGEM ENSAIO PESSOA' from public.pessoa p
 where p.nome_exibicao='PESSOA DE ENSAIO — AGRÔNOMA'
   and not exists (select 1 from public.origem o where o.pessoa_id = p.id);

insert into public.origem (organizacao_id, rotulo)
select g.id, 'ORIGEM ENSAIO ' || g.nome_canonico from public.organizacao g
 where g.nome_canonico in ('COOPERATIVA DE ENSAIO','AGREGADOR DE ENSAIO',
                           'BUSCADOR DE ENSAIO','ORG DO PERFIL SEM FICHA')
   and not exists (select 1 from public.origem o where o.organizacao_id = g.id);

-- ── OS CINCO CASOS ────────────────────────────────────────────────────
insert into public.canal
  (origem_id, plataforma, channel_id, handle, tipo_de_perfil, tipo_de_perfil_evidencia)
select o.id, v.plat, v.cid, v.handle, v.tipo, v.evid
  from (values
   -- 1 · pessoa legítima: página em primeira pessoa, com ficha de pessoa.
   ('ORIGEM ENSAIO PESSOA', 'web', 'ENSAIO-PERFIL-PESSOA', 'ensaio-pessoa',
    'PERSON_PROFILE',
    'A página se apresenta em primeira pessoa do singular, nomeia formação e '
    'local de trabalho, e o texto é assinado pelo mesmo nome do perfil.'),

   -- 2 · página institucional: fala como entidade, não como voz humana.
   ('ORIGEM ENSAIO COOPERATIVA DE ENSAIO', 'web', 'ENSAIO-PERFIL-ORG', 'ensaio-coop',
    'ORGANIZATION_PROFILE',
    'A página fala em primeira pessoa do plural pela entidade, traz CNPJ/NIF, '
    'endereço de sede e uma seção "quem somos". Não há autor individual.'),

   -- 3 · agregador: o conteúdo é de terceiros, republicado.
   ('ORIGEM ENSAIO AGREGADOR DE ENSAIO', 'web', 'ENSAIO-PERFIL-AGREGADOR', 'ensaio-agg',
    'AGGREGATOR',
    'Cada item traz crédito e link para o veículo de origem, e a própria página '
    'diz que reúne publicações de terceiros. Nenhum texto é assinado pela página.'),

   -- 4 · envelope de resultado de busca: SEARCH_HIT ≠ PERSON.
   ('ORIGEM ENSAIO BUSCADOR DE ENSAIO', 'web', 'ENSAIO-PERFIL-BUSCA', 'ensaio-serp',
    'SEARCH_RESULT_ENVELOPE',
    'O objeto é a página de resultados de uma consulta: traz a query, uma lista '
    'de links e trechos. Não é um perfil; é o resultado de ter perguntado.'),

   -- 5 · desconhecido: NÃO medimos. Sem evidência, e por isso sem declaração.
   ('ORIGEM ENSAIO ORG DO PERFIL SEM FICHA', 'web', 'ENSAIO-PERFIL-DESCONHECIDO',
    'ensaio-?', 'NOT_KNOWN', null)
  ) v(rotulo, plat, cid, handle, tipo, evid)
  join public.origem o on o.rotulo = v.rotulo
on conflict (plataforma, channel_id) do update
  set tipo_de_perfil = excluded.tipo_de_perfil,
      tipo_de_perfil_evidencia = excluded.tipo_de_perfil_evidencia;

-- ── O SEXTO CASO, que não estava na lista e existe mesmo assim ─────────
-- Página que É de pessoa, mas cuja origem aponta uma ORGANIZAÇÃO. As duas
-- condições do sensor humano são independentes: a leitura da página e a
-- ficha de quem cadastrou. Uma só não basta.
insert into public.canal
  (origem_id, plataforma, channel_id, handle, tipo_de_perfil, tipo_de_perfil_evidencia)
select o.id, 'web', 'ENSAIO-PERFIL-PESSOA-SEM-FICHA', 'ensaio-sem-ficha',
       'PERSON_PROFILE',
       'A página se apresenta em primeira pessoa do singular, mas a ficha de '
       'origem cadastrada aponta uma organização, não uma pessoa.'
  from public.origem o where o.rotulo='ORIGEM ENSAIO ORG DO PERFIL SEM FICHA'
on conflict (plataforma, channel_id) do update
  set tipo_de_perfil = excluded.tipo_de_perfil,
      tipo_de_perfil_evidencia = excluded.tipo_de_perfil_evidencia;

commit;
