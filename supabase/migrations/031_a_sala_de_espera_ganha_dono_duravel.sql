-- ═══════════════════════════════════════════════════════════════════════
-- 031 · A SALA DE ESPERA GANHA DONO DURÁVEL — e a fila deixa de morrer com o job
--
-- ── O FACTO NOVO QUE ABRIU ESTA MIGRATION ─────────────────────────────────
--
-- A `ADR-SALA-DE-ESPERA-V1` escolheu o sistema de ficheiros, e escolheu bem
-- para o que sabia: zero consumidores, uma unidade por corrida, nenhuma
-- consulta declarada. O que ela não sabia é que ninguém tinha perguntado o
-- seguinte — e a primeira coleta real a sério perguntou:
--
--     quando o runner acabar, onde é que o READY fica?
--
-- Medido em `C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1`, contra o repositório
-- inteiro e não contra uma suposição:
--
--     git log --all -- 'data/samples/PRONTO-PARA-INTELIGENCIA'   ->  vazio
--
-- Nunca, em ramo nenhum, um ficheiro da Sala foi versionado. Nenhum workflow
-- lhe faz `git add`; o `sintonia-scrap.yml` até RECUSA qualquer caminho fora de
-- `INSTAGRAM|YOUTUBE|SCRAP`. Nenhum `upload-artifact` o apanha. E o próximo
-- `actions/checkout` limpa o que não está versionado.
--
--     MODULE EXISTS != FILE WRITTEN ON RUNNER != PERSISTED AFTER RUN.
--     PROVA DENTRO DO PROCESSO != DURABILIDADE OPERACIONAL.
--
-- Isto não revoga a ADR-V1: ela própria escreveu `BACKEND_CHANGE_ALLOWED_LATER
-- = YES` e pediu `PROVA DE NECESSIDADE`. A prova chegou.
--
-- ── POR QUE POSTGRES, E NÃO OUTRA COISA ───────────────────────────────────
--
--   GIT          `P-011 · GIT NÃO É BANCO OPERACIONAL`. Um commit por execução
--                faz do histórico a memória da fila. Recusado pela casa, e a
--                recusa já está escrita.
--   ARTEFATO     retenção de 30 dias, declarada no próprio workflow:
--                `WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE`.
--   STORAGE      guarda BYTES. A Sala não tem bytes — tem uma FILA com estado,
--                unicidade e transição. Um bucket não tem `unique`, não tem
--                transação e não sabe recusar a segunda escrita divergente.
--   POSTGRES     tem as quatro coisas que esta fila exige e que só ele dá aqui:
--                unicidade, transação, chave estrangeira e consulta.
--
-- E não se inventa armazém: `raw_asset` e `storage_object` continuam donos dos
-- bytes. A Sala guarda o PONTEIRO, e é só isso que ela tem de guardar.
--
--     A MENOR IDENTIDADE QUE FECHA A ESTRADA É A CERTA.
--
-- ── A FILA É POR ITEM, E NÃO POR CORRIDA ──────────────────────────────────
--
-- O ficheiro da V1 era por corrida: `<RUN_ID>.json` com N unidades lá dentro.
-- Isso chegava para pousar e não chega para RETIRAR: um item processado tem de
-- deixar de aparecer nos pendentes sem levar os irmãos com ele.
--
--     UMA FILA QUE SÓ SABE FALAR DA CORRIDA INTEIRA NÃO É UMA FILA.
--
-- ⚠️ E A CHAVE NÃO PODE SER `(run_id, item_id)`. Foi a primeira tentativa, e
-- medi-la matou-a: `admissao.decidir()` constrói `ITEM_ID` assim —
--
--     str(item.get("id") or item.get("url") or "?")
--
-- `"?"` é um valor real e alcançável. Dois itens admitidos sem `id` e sem `url`
-- na mesma corrida trazem AMBOS `ITEM_ID = "?"`, e uma chave primária ali
-- deitaria um deles fora — em silêncio, com `on conflict do nothing`, ou com um
-- erro que o operador leria como defeito do banco.
--
--     ITEM_ID NÃO É IDENTIDADE GARANTIDA DENTRO DA CORRIDA.
--     DESCOBRIR ISSO A APAGAR UMA LINHA É DESCOBRIR TARDE DEMAIS.
--
-- A chave é `(run_id, ordem)`: a posição no CONJUNTO que a corrida pousou. Ela
-- não é fabricada de URL, caminho, hash nem owner — é a ordem declarada pelo
-- próprio pouso, e é estável porque a mesma corrida com conteúdo diferente não
-- chega a escrever (dá `RUN_ID_CONFLICT`). `item_id` continua guardado e
-- indexado; o que ele NÃO é, aqui, é endereço.
--
-- ── E A CORRIDA CONTINUA A NÃO PODER CONTAR DUAS HISTÓRIAS ────────────────
--
-- `corrida_sha256` é a impressão do CONJUNTO que a corrida pousou — os mesmos
-- bytes canónicos que a V1 comparava ficheiro a ficheiro. Com ela, as duas
-- respostas da V1 sobrevivem à mudança de casa, e sem heurística:
--
--     mesma corrida, mesma impressão      ->  REUSED       (retry legítimo)
--     mesma corrida, impressão diferente  ->  RUN_ID_CONFLICT, e não se escreve
--
-- ── O QUE ESTA MIGRATION NÃO FAZ ──────────────────────────────────────────
--
-- Não decide relevância. Não sabe o que é KEEP, TEMP ou DISCARD. `CONSUMED` diz
-- «saiu da fila», e mais nada — quem o pôs lá fica registado, o veredito não,
-- porque o veredito é da Intelligence e a Intelligence é outra missão.
--
--     COLLECTION TERMINA NA SALA. A SALA NÃO JULGA.
--
-- E não apaga: o item retirado continua na tabela, com a hora e o autor. Uma
-- fila que apaga o que entregou não é auditável.
--
-- ── ESTADO ────────────────────────────────────────────────────────────────
--
--     NÃO EXECUTADA
--
-- Esta migration é uma PROPOSTA. Ela foi aplicada, medida e atacada contra
-- PostgreSQL 16 DESCARTÁVEL — que nasce e morre com a bateria — e nunca contra
-- o banco de produção. O pacote de aplicação vive em
-- `docs/operacao/C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1.md`, e a aplicação é
-- uma decisão explícita e separada, hoje bloqueada por `RESTORE_NOT_PROVEN`.
--
--     DESIGNED != DB_TESTED != LIVE.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.sala_de_espera (
  -- ── A IDENTIDADE, E ELA JÁ EXISTIA NO CONTRATO READY ────────────────
  -- `CORRIDA` e `ITEM_ID` da COL-LAW-043. Nada aqui é derivado de URL,
  -- caminho, filename, hash nem owner.
  run_id              text   not null
                      references public.collection_run(run_id) on delete restrict,
  -- A posição no conjunto que esta corrida pousou. É o ENDEREÇO da linha.
  ordem               integer not null
                      constraint ordem_nao_e_negativa check (ordem >= 0),
  -- O `ITEM_ID` do contrato READY. Guardado e indexado, mas NÃO é endereço:
  -- ele é o nome que a FONTE deu ao item, e duas fontes podem dar o mesmo.
  --
  -- ⚠️ ESTE COMENTÁRIO DIZIA «ele pode valer `"?"`», e isso deixou de ser
  -- verdade em `C-COL-PRESERVE-FACTS-V1`: a porta ganhou a pergunta
  -- `identidade` e um item sem `id` e sem `url` já não passa (COL-LAW-034).
  -- A chave continua a ser `(run_id, ordem)` — curar o sintoma não promove o
  -- campo a chave.
  item_id             text   not null,

  -- ── A LINHAGEM, E ELA É UM PONTEIRO ─────────────────────────────────
  -- `RAW_OBSERVATION_ID = raw_asset.id`. A chave estrangeira é a trava: um
  -- READY que aponte para uma observação que não existe NÃO entra.
  --
  -- ⚠️ NULO QUER DIZER `NAO SEI`, e é um valor legítimo — o próprio
  -- `admissao.pronto_para_inteligencia()` escreve `NAO SEI` quando a rota
  -- não trouxe a observação. Fabricá-la a partir do `sha256`, da URL ou do
  -- `RUN_ID` seria pior do que não a ter.
  --
  -- ⚠️ E ELA PODE APONTAR PARA OUTRA CORRIDA, DE PROPÓSITO. A corrida que
  -- ADMITE não é forçosamente a que CAPTUROU — a `029` e a `030` já o
  -- disseram sobre a passagem que estrutura. Uma trava a exigir
  -- `raw_asset.run_id = sala.run_id` proibiria um caso legítimo, e por isso
  -- ela não existe aqui. O que se exige é que a observação EXISTA.
  raw_observation_id  bigint references public.raw_asset(id) on delete restrict,

  -- ── O CORPO DO CONTRATO READY ───────────────────────────────────────
  -- `ESTADO` não tem coluna: é a constante `PRONTO_PARA_INTELIGENCIA`, e o
  -- dono dela é `admissao.pronto_para_inteligencia()`. Guardar uma constante
  -- em cada linha seria pôr o nome do contrato dentro do dado, livre para
  -- divergir do contrato.
  universo            text not null,
  texto               text not null,
  source_id           text not null,
  -- Estes quatro carregam `NAO SEI` como TEXTO, e é essa a forma que o
  -- contrato entrega. Traduzi-los para NULL aqui criaria duas maneiras de
  -- dizer a mesma ausência.
  source_location     text not null,
  fact_location       text not null,
  fact_time           text not null,
  captured_at         text not null,
  admitido_por        text not null,

  -- ── A IMPRESSÃO DO CONJUNTO QUE ESTA CORRIDA POUSOU ─────────────────
  -- Igual em todas as linhas da mesma corrida. É ela que distingue o retry
  -- legítimo do conflito, sem heurística e sem comparar campo a campo.
  corrida_sha256      char(64) not null
                      constraint corrida_sha_tem_formato
                      check (corrida_sha256 ~ '^[0-9a-f]{64}$'),

  -- ── A FILA ──────────────────────────────────────────────────────────
  -- ⚠️ O NOME É `estado_da_fila` E NÃO `estado`. O contrato READY já tem um
  -- campo chamado `ESTADO`, e ele vale `PRONTO_PARA_INTELIGENCIA`. Duas
  -- coisas diferentes com o mesmo nome é como se lê a errada.
  estado_da_fila      text not null default 'WAITING'
                      constraint estado_da_fila_e_um_dos_dois
                      check (estado_da_fila in ('WAITING', 'CONSUMED')),
  pousado_em          timestamptz not null default now(),
  consumido_em        timestamptz,
  consumido_por       text,

  primary key (run_id, ordem),

  -- Um READY sem fonte seria um texto órfão com cara de registo.
  constraint ready_declara_a_fonte
    check (length(btrim(source_id)) > 0),
  constraint ready_declara_o_universo
    check (length(btrim(universo)) > 0),

  -- ⚠️ RETIRAR É UM ACTO COM AUTOR E COM HORA, OU NÃO É UM ACTO.
  -- Sem isto, `update ... set estado_da_fila='CONSUMED'` deixaria a fila a
  -- dizer que alguém levou o item, sem dizer quem nem quando — e a auditoria
  -- da retirada seria uma palavra.
  constraint consumo_diz_quem_e_quando
    check (estado_da_fila <> 'CONSUMED'
           or (consumido_em is not null
               and consumido_por is not null
               and length(btrim(consumido_por)) > 0)),

  -- E o contrário: quem ainda espera não pode ter carimbo de saída.
  constraint quem_espera_nao_tem_carimbo_de_saida
    check (estado_da_fila <> 'WAITING'
           or (consumido_em is null and consumido_por is null))
);

-- A pergunta que a fila existe para responder: «o que está à espera?».
-- Parcial de propósito: o índice só carrega o que ainda espera, e não cresce
-- com o histórico do que já saiu.
create index if not exists sala_pendentes_idx
  on public.sala_de_espera (pousado_em)
  where estado_da_fila = 'WAITING';

-- Quem pergunta «o que esta corrida pousou?» — e quem procura por `ITEM_ID`
-- sabendo que ele pode devolver mais do que uma linha.
create index if not exists sala_por_corrida_idx
  on public.sala_de_espera (run_id, item_id);

-- Quem volta da observação ao que dela se admitiu.
create index if not exists sala_por_observacao_idx
  on public.sala_de_espera (raw_observation_id)
  where raw_observation_id is not null;

comment on table public.sala_de_espera is
  'A Sala de Espera: onde a unidade READY pousa e espera pela Intelligence. '
  'Dono unico em codigo: admissao/sala_de_espera.py. Collection TERMINA aqui; '
  'esta tabela NAO julga relevancia e nao conhece KEEP/TEMP/DISCARD.';

comment on column public.sala_de_espera.item_id is
  'O ITEM_ID do contrato READY. NAO e endereco: admissao.decidir() devolve "?" '
  'quando o item nao traz id nem url, e dois itens assim na mesma corrida '
  'repetem-no. O endereco da linha e (run_id, ordem).';

comment on column public.sala_de_espera.raw_observation_id is
  'RAW_OBSERVATION_ID = raw_asset.id (COL-LAW-043). NULO = NAO SEI. Nunca '
  'derivado de sha256, URL, storage_path, filename ou RUN_ID. PODE apontar '
  'para observacao de OUTRA corrida: quem admite nao e forcosamente quem capturou.';

comment on column public.sala_de_espera.corrida_sha256 is
  'A impressao do CONJUNTO que a corrida pousou. Mesma impressao = REUSED; '
  'impressao diferente na mesma corrida = RUN_ID_CONFLICT, e nao se escreve nada. '
  'UMA RUN_ID NAO PODE CONTAR DUAS HISTORIAS.';

comment on column public.sala_de_espera.estado_da_fila is
  'WAITING | CONSUMED. CONSUMED quer dizer «saiu da fila», e mais nada — o '
  'VEREDITO sobre o item e da Intelligence, e nao mora aqui. A linha NAO e '
  'apagada ao ser consumida: uma fila que apaga o que entregou nao e auditavel.';

comment on constraint consumo_diz_quem_e_quando on public.sala_de_espera is
  'RETIRAR E UM ACTO COM AUTOR E COM HORA, OU NAO E UM ACTO.';
