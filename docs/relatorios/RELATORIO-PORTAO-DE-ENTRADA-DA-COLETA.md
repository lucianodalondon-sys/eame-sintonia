# O PORTÃO DE ENTRADA DA COLETA — os cinco PARTIALs fechados, e seis lacunas novas abertas

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-collection-es`
**Base:** `5a6114b` · **Banco:** PostgreSQL 16.13 local e descartável. **Supabase de produção não foi tocado.**

> **Este relatório foi corrigido depois de publicado.** A primeira versão continha uma
> contradição (`EAME_COLLECTION_ENTRY_GATE = READY` ao lado de
> `LOCATION_CONTRACT_COMPLETE = NO`) e um número falso (*"zero enviado dos 196"*). As duas
> correções estão nas seções **I** e **K**, com o erro original à vista. Nenhuma cicatriz
> mudou de estado para acomodá-las.

Esta rodada tinha uma tarefa: fechar os cinco PARTIALs reais do *collection entry gate*.
Os cinco fecharam, com testemunha executável. E a conferência de localização, que era
para ser um spot-check de confirmação, **rebaixou um contrato que a rodada anterior tinha
dado por completo**. As duas coisas estão neste relatório, nessa ordem, porque foi nessa
ordem que aconteceram.

---

## A · O QUE FOI FEITO

| | |
|---|---|
| PARTIALs fechados | **5** — BR-14 · BR-16 · BR-19 · BR-20 · BR-21 |
| Lacunas novas, abertas pela conferência | **5** — BR-26 · BR-30 · BR-31 · BR-32 · BR-34 |
| Defeitos meus, achados e corrigidos | **5** — índice duplicado (016) · `pode::text` · `UNRELATED` por data de publicação (015) · **ZERO publicado onde a resposta era NÃO MEDIDO** · **`READY` contraditório com `LOCATION = NO`** |
| Migrations novas | 016, 017 |
| Afirmações SQL | **118** (45 calendário · 19 captura · 33 cicatrizes · 21 coleta) |
| Mutações | **12**, todas pegaram |
| Testes Python | **<!--M:TEST_COUNT_CURRENT-->729<!--/M-->**, todos verdes |
| Apify gasto | **0,00 USD** |

## B · REUSO, NÃO SEGUNDA IMPLEMENTAÇÃO

`scripts/apify_pool.py`, `apify_contrato.py` e `apify_recuperar.py` vieram **portados
verbatim** de `origin/claude/sintonia-italy-pilot-b1l401`, cada um com uma nota de
`PROVENIÊNCIA` no topo dizendo de onde veio. Nada foi reescrito. O que a aba principal
acrescentou é uma camada **acima** deles — `scripts/coleta_checkpoint.py` —, e é por isso
que `apify_pool` continua sem saber que existe um banco de dados.

O que a Itália já provava e não foi refeito: `APIFY_TOKEN_POOL`, o parser de credencial,
a rotação, a preservação do RAW pago, `RUN_ID` · `DATASET_ID` · `INPUT_HASH`, custo por
rodada, recuperação read-only, `UNKNOWN_SCHEMA`, `PARSER_MISS ≠ NOT_FOUND` e
`SEARCH_HIT ≠ PERSON`.

## C · BR-19 e BR-20 · a guarda antes do gasto

`checkpoint_coleta` (016) carrega os nove campos mínimos: `collection_target`,
`input_hash`, `actor`, `started_at`, `estado`, `pool_position`, `run_id`, `dataset_id` e
`ultima_unidade` — mais `unidades_feitas` e `itens_persistidos`, que são o progresso.
`pode_gastar()` responde **NÃO por padrão**, com motivo:

```
SEM_CHECKPOINT_NAO_GASTEI          não há linha aberta para este alvo
JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES  já foi feito; refazer é gasto puro
CHECKPOINT_ENCERRADO_ABRIR_OUTRO   a linha existe e está fechada
CHECKPOINT_ABERTO                  pode gastar, e a retomada começa daqui
```

`PROCESS_CRASH ≠ LOST_COLLECTION` porque o progresso mora no banco, não na memória do
processo. **Mutação:** removida a guarda, o teste pega uma chamada paga que teria
acontecido — `MUT4 K1 PEGOU`.

## D · BR-21 · pool e retomada, provados de A a H

`tests/test_coleta_resiliente.py` roda o ciclo inteiro contra o banco, com o ator sendo
uma função Python — **custo real zero, caminho até o banco idêntico ao de produção**:

| | |
|---|---|
| **A** token 1 coleta 2 de 5 unidades | ✅ |
| **B** o parcial é persistido antes de acabar a chave | ✅ |
| **C** o token esgota | ✅ |
| **D** o checkpoint registra onde parou | ✅ |
| **E** o processo morre | ✅ (o teste descarta o objeto e abre outro) |
| **F** o token 2 assume e chama **só** `u3 u4 u5` | ✅ |
| **G** zero duplicata viva, mesmo com item repetido | ✅ 10 itens, 0 perdidos |
| **H** a identidade não depende do token | ✅ `CHECKPOINT_STATE = CONCLUIDO` |

`UNKNOWN_FAILURE` **não rotaciona**, de propósito: uma falha não identificada não pode
queimar o pool inteiro. E o pool é **resiliência, não volume** — o teto de itens do alvo
não muda ao trocar de chave.

## E · BR-14 · a identidade não carrega a rodada

Aqui a rodada anterior estava **errada no diagnóstico**. Ela registrou "falta a trava de
identidade". A trava existia desde a 003: `conteudo_canal_id_content_id_key`,
`UNIQUE (canal_id, content_id)`. A 016 chegou a criar um índice novo com as mesmas duas
colunas — um **segundo dono da mesma lei** — e o banco recusou a duplicata na primeira
execução do teste.

O que faltava não era a trava. Era **o caminho produtivo provado passando por ela**. Isso
agora existe, e `conteudo_visto_em` guarda a segunda vez que vimos o mesmo item: duas
rodadas, duas observações, **um** conteúdo.

`TOKEN`, `RUN_ID`, `DATASET_ID` e `CAPTURED_AT` nunca entram na identidade — e há um teste
que lê a definição real da constraint e procura os quatro nomes lá dentro.

## F · BR-16 · `AGGREGATOR ≠ HUMAN_VOICE`

`canal.tipo_de_perfil` com cinco estados, **evidência escrita obrigatória** para qualquer
declaração, e `NOT_KNOWN` como padrão. Nenhuma classificação sai de volume, de contagem de
seguidores ou de heurística fraca — `'INFLUENCER'` é recusado pelo vocabulário, e é
justamente o rótulo que sairia de contar seguidores.

| caso | admissível | porquê |
|---|---|---|
| pessoa legítima | **sim** | `ADMISSIVEL` |
| página institucional | não | `ORGANIZACAO_NAO_E_VOZ_HUMANA` |
| agregador | não | `AGGREGATOR_NAO_E_HUMAN_SENSOR` |
| envelope de busca | não | `SEARCH_HIT_NAO_E_PESSOA` |
| desconhecido | não | `TIPO_DE_PERFIL_NAO_MEDIDO` |
| perfil de pessoa **sem** ficha de pessoa | não | `PERFIL_DE_PESSOA_SEM_FICHA_DE_PESSOA` |

O sexto caso não estava na lista da missão e existe mesmo assim: ler a página e cadastrar
a origem são **dois atos**, e um só não basta.

## G · A CONFERÊNCIA DE LOCALIZAÇÃO — o que ela custou

Dez cicatrizes brasileiras mais novas passadas por cima do contrato já fechado. **Ele
fechava cinco das dez.**

| | cicatriz | veredito |
|---|---|---|
| A | `BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT` | **PARTIAL** — só duas das quatro existem |
| B | `PLACE_MENTION ≠ FACT_LOCATION` | **PROVED** *após correção na 017* |
| C | evidência específica do lugar | PROVED |
| D | proveniência do **valor** | PROVED |
| E | 0..N lugares de fato | **ABSENT** — `fact_geografia_id` é uma coluna |
| F | `GEO_PRECISION` | **PARTIAL** — a escada para em `PROVINCIA` |
| G | `TERRITORIAL_LIST ≠ FACT_LIST` | **PARTIAL** — existe no eixo do produto, não no da geografia |
| H | `OCCURRENCE ≠ INCIDENCE` | PROVED |
| I | `PUBLISHED_AT ≠ FACT_TIME` | **PARTIAL** *após correção na 017* |
| J | etiqueta de lugar da plataforma ≠ fato | PROVED |

### As duas que davam resposta ERRADA, e foram consertadas

**I.** `f_relevancia_ao_caso`, escrita por mim na 015, devolvia `UNRELATED` para conteúdo
publicado **depois** do fim da janela do caso — tratando data de publicação como data do
fato. Um documento de setembro pode perfeitamente relatar um fato de junho. Agora devolve
`CONTEXT_ONLY`, e o motivo diz que o tempo do fato não é conhecido. Publicado **antes** do
início continua `RETROSPECTIVE`, porque documento não relata o futuro: a data de publicação
decide numa direção só.

**B.** A 015 **escreve** que `CITADO` é "o balde mais fraco, e lá ele é filtro de leitura,
nunca fonte nova" — e a trava deixava `CITADO` sustentar o lugar do fato sozinho, sem que
nada a jusante soubesse. O comentário e a trava discordavam. `CITADO` continua registrável
(mencionado e não-medido são respostas diferentes) e deixou de passar despercebido:
`v_conteudo_localizacao` agora publica `fact_sustentado_apenas_por_mencao` e
`fact_forca_da_sustentacao`, e a relevância rebaixa lugar mencionado a `CONTEXT_ONLY`.

### As quatro que NÃO foram consertadas, e por quê

`BASE/OPERATING/INFLUENCE` colapsados · `0..N` lugares de fato · a escada de precisão ·
lista territorial. Todas exigem **modelagem nova**, e reabrir a modelagem de localização na
véspera do portão de importação é exatamente o que a missão proíbe. Estão na matriz com
`MINIMAL_ACTION` e o momento certo de cada uma — nenhuma delas é antes da importação do
catálogo espanhol, que é **registro, não ocorrência**.

`LOCATION_CONTRACT_COMPLETE` saiu de **YES** e foi para **NO**. Manter o YES teria sido
mover a régua.

## H · SENSOR HUMANO · o que NÃO foi feito

Nenhuma coleta. Nenhum gasto Apify. Nenhum LinkedIn, Instagram, YouTube ou Meta. Os seis
perfis do ensaio são **fictícios** e existem só para exercer a recusa.

## I · O GATE DO RAW ESPANHOL — prova EXTERNA, e o número que eu publiquei estava errado

> **CORREÇÃO.** A primeira versão desta seção dizia `RAW_ASSETS = NOT_MEASURED` e o
> veredito dizia *"zero enviado dos 196"*. **Era falso.** Não porque a medição tenha
> mudado depois: porque eu escrevi ZERO onde a resposta honesta era NÃO MEDIDO DAQUI.
> `SOURCE FAILURE ≠ ZERO` é lei deste repositório, e eu a violei na direção mais fácil de
> não perceber — não medir e publicar zero soa cauteloso, e é uma afirmação sobre o mundo
> igual a qualquer outra. A medição real da máquina espanhola:

```
EXPECTED                     196
ALREADY_PRESENT_VERIFIED     184
FAILED_WITH_REASON            12
HASH_MISMATCH                  0
CONFLICT                       0
                             ────
                       184 + 12 = 196   a conta fecha

RAW_PRESERVATION_GATE = OPEN_EXTERNAL_REPAIR
```

> **FECHOU DEPOIS.** O operador rodou `storage_preservar.py --enviar --so-ausentes` na
> máquina espanhola e os 196 entraram: `RAW_PRESERVATION_GATE = CLOSED`. Os números acima
> ficam porque eram o que se sabia nesta rodada — o estado corrente é derivado em
> `data/samples/PORTOES-EAME.json`.

**Os 12 pertencem ao denominador.** Cada um tem `ARQUIVO_LOCAL`, `BYTES` e `SHA256`:
existem, foram baixados e foram conferidos. O que falhou foi o **envio**, não a obtenção.
Tirá-los do denominador melhoraria a taxa apagando o problema.

Modo de falha visível: a maioria HTTP 400; ao menos o `NEPTUNE web.pdf` com HTTP 520. **O
retry não melhorou** — e as duas tentativas ficam registradas porque a segunda mediu **um a
menos** que a primeira (185/11 → 184/12). Guardar só a melhor das duas seria escolher o
número que agrada; a diferença de 1 é parte do diagnóstico, e está em aberto.

O diagnóstico dos 12 corre **na máquina local espanhola**. Não foi tentado reparo daqui, e
nada aqui foi verificado daqui: este ambiente não tem credencial de Supabase, e recontar
daqui produziria zero — que é exatamente o defeito que esta seção corrige.

Artefato: `data/samples/RAW-GATE-ES.json`.

## J · MIGRATIONS

```
001–007 · 009 · 010–012 · 013 · [014 reservada] · 015 · 016 · 017 · 008 por último
```

Montadas do zero num banco vazio nesta rodada: **15 migrations, todas ok**, `008` conferindo
no fim (`migrations 001-017 conferidas: 30 tabelas`). O **014 continua vago de propósito** —
é o catálogo, e vem da branch paralela.

## K · VEREDITO — reconciliado

> **CORREÇÃO.** A primeira versão desta seção publicou
> `EAME_COLLECTION_ENTRY_GATE = READY` **e** `LOCATION_CONTRACT_COMPLETE = NO` no mesmo
> bloco. As duas não podem ser verdade juntas: o portão se chama entrada da **COLETA**, e
> toda coleta que produz documento produz documento com lugar de fato.
>
> O erro não foi de medição — as cicatrizes estavam medidas certo, e **nenhuma mudou de
> estado para desfazer a contradição**. Foi de **nome**: um nome estava fazendo dois
> trabalhos. A engenharia de importar o catálogo regulatório e a entrada da coleta em geral
> não são o mesmo portão, e o segundo não estava pronto.

```
LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE   YES

CATALOG_IMPORT_ENGINEERING_GATE   READY     16/16 cicatrizes PROVED
EAME_COLLECTION_ENTRY_GATE        PARTIAL   30/35 cicatrizes PROVED
    bloqueia  BR-26  BASE / OPERATING / INFLUENCE colapsados
    bloqueia  BR-30  fact_geografia_id é 0..1, e o mundo é 0..N
    bloqueia  BR-31  a escada de precisão para em PROVINCIA
    bloqueia  BR-32  TERRITORIAL_LIST no eixo da geografia
    bloqueia  BR-34  falta o TEMPO DO FATO como campo

LOCATION_CONTRACT_COMPLETE        NO
ANALYTICAL_UNIT_CONTRACT_COMPLETE YES
RESILIENCE_CONTRACT_COMPLETE      YES
  BR-14 PROVED · BR-16 PROVED · BR-19 PROVED · BR-20 PROVED · BR-21 PROVED

RAW_PRESERVATION_GATE             OPEN_EXTERNAL_REPAIR   → hoje CLOSED
  EXPECTED 196 · VERIFIED 184 · FAILED 12 · HASH_MISMATCH 0

IMPORT_CAN_BE_NEXT_MISSION        NO                     → hoje YES
```

**Por que `CATALOG_IMPORT_ENGINEERING_GATE` não herda as lacunas de localização.** Não é
conveniência de escopo: um **registro regulatório não tem lugar de fato**. O país de um
registro é o Estado que registrou, e isso é lado da FONTE. As quatro lacunas abertas são
todas do lugar do FATO, em `conteudo` — tabela que a importação do catálogo não escreve.

**Por que o portão da coleta não pode ser READY.** Porque ele cobre a coleta que escreve
`conteudo`, e é exatamente ali que as quatro lacunas moram. Chamar isso de READY faria
`READY` significar "o EAME inteiro pode coletar", que é falso.

Nada disso é decidido por este texto. `scripts/portoes_eame.py` **deriva** o estado de cada
portão das cicatrizes de que ele depende, e `tests/test_portoes_eame.py` fecha a saída
fácil: tirar a família da localização da lista do portão da coleta o faria virar READY sem
resolver nada — e há um teste que reprova essa edição, e uma mutação que confirma que o
teste tem dentes.

**Nada foi importado. Nada foi aplicado no Supabase. A instrução era parar aqui.**
