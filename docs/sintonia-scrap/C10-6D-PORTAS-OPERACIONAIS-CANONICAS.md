# C10.6D — AS PORTAS OPERACIONAIS ENTRAM PELA CASA CERTA

`C10_6D_OPERATIONAL_ENTRYPOINT_CONVERGENCE = PARTIAL_CAPABILITY_GAPS`

> As sete portas de aquisição que corriam implementação direta acabaram: três
> passaram a entrar pelo boundary canônico e quatro passaram a **recusar alto**,
> com o motivo escrito. Nenhuma fase de julgamento, de operação ou de validação
> foi fabricada como Collection para o número baixar.
>
> ```
> UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO.
> ```
>
> Ficam **dois** buracos nomeados, e nenhum deles é um bypass silencioso.

---

## 1 · A PERGUNTA, E A RESPOSTA MEDIDA

«Das invocações vivas dos workflows, quais executam Collection de verdade, e
quais delas conseguem passar pelo runtime canônico sem perder semântica,
política, proveniência, identidade, custo e comportamento?»

O número de partida do briefing era 15. **Não era 15.** O censo estrutural —
YAML parseado, nunca grep de prosa — mediu:

```
LIVE_INVOCATIONS_BEFORE           = 109
LIVE_INVOCATIONS_AFTER            = 101

COLLECTION_DIRECT_BYPASSES_BEFORE =   7
COLLECTION_DIRECT_BYPASSES_AFTER  =   0      ← o portão principal da missão

COLLECTION_SECOND_RUNTIME_BEFORE  =   1
COLLECTION_SECOND_RUNTIME_AFTER   =   1      ← nomeado no §6

NON_COLLECTION_DIRECT_INVOCATIONS =  95
UNKNOWN_INVOCATIONS               =   0
```

### O que decidiu tudo

Nenhuma das seis implementações que os workflows corriam direto importa
`leis/social_matriz.py`. Seis portas de produção, e nenhuma perguntava à dona da
decisão se podia.

E a pergunta, quando finalmente foi feita, respondeu **não** em quatro casos.

---

## 2 · O CENSO NÃO DECIDE A ESPÉCIE PELO DIRETÓRIO

A primeira volta deste censo filtrava por prefixo — `coleta/`, `ferramentas/`,
`admissao/` — e por isso **não via** `orquestrador/orquestrador.py`, que é
exactamente uma porta de Collection.

```
UM CENSO QUE DECIDE A ESPÉCIE PELO DIRETÓRIO MEDE A ÁRVORE, NÃO A CASA.
```

A segunda volta classificava pelo MÓDULO, e `coleta/instagram_coleta.py` faz
cinco coisas: `contratos` lê o schema do ator com `APIFY_RUNS = 0`, `liquidar`
lê a fatura depois, e `bio`/`posts`/`reels`/`comentarios` gastam. Classificar o
módulo contava duas ferramentas de leitura como aquisição.

```
UM MÓDULO QUE FAZ CINCO COISAS TEM CINCO ESPÉCIES,
E O CENSO MEDE A QUE FOI PEDIDA.
```

A terceira volta lia só a **primeira** etiqueta de um ramo `a|b|c)`. O ramo
`contratos|plano|semaforo|liquidar)` é um ramo com quatro fases, e o comando
dele é `... "${{ inputs.fase }}"`: guardar só `contratos` fazia o censo
perguntar a espécie de uma fase e responder pelas outras três.

Só a quarta volta mede a casa.

---

## 3 · A TABELA DE MAPEAMENTO

| fase | implementação que corria | espécie medida | destino na C10.6D |
|---|---|---|---|
| `janela` | `instagram_janela.py tudo` | COLLECTION_DISCOVER | **canônica** · `instagram.profile.discovery` |
| `janela-perfis` | `instagram_janela.py perfis` | COLLECTION_DISCOVER | **canônica** · camada `perfis` |
| `janela-objetos` | `instagram_janela.py objetos` | COLLECTION_DISCOVER | **canônica** · camada `objetos` |
| `diario` | `instagram_diario.py rodar` | COLLECTION_DISCOVER | **recusa** · nenhuma capacidade declara a unidade «conta × dia» |
| `yt-canais` · `yt-objetos` | `youtube_janela.py` | COLLECTION_DISCOVER | **recusa** · rota `PUBLIC_BROWSER` não declarada em `YOUTUBE/INCREMENTAL` |
| `yt-legendas` | `youtube_janela.py legendas` | COLLECTION_DERIVED | **recusa** · `timedtext` é `ROUTE_NOT_ALLOWED` desde a C5 |
| `yt-alvos` · `yt-transcrever` | `youtube_transcrever.py` | COLLECTION_FETCH | **recusa** · a matriz não declara capacidade de BYTES para YouTube |
| `bio` · `posts` · `reels` · `comentarios` | ramo `*)` → `instagram_coleta.py` | COLLECTION_FETCH (PAGO) | **recusa** · rota paga sem capacidade registada |
| `diario-fila` | `instagram_diario.py fila` | COLLECTION_SUPPORT | CLI própria, legítima |
| `diario-noticia` | `instagram_diario.py noticia` | OPERATIONAL_CONTROL | CLI própria, legítima |
| `portao-pessoal` | `instagram_pessoal.py estado` | OPERATIONAL_CONTROL | CLI própria, legítima |
| `yt-relevancia` · `yt-calibrar` | `youtube_relevancia.py` | JUDGMENT_OR_RELEVANCE | CLI própria, legítima |
| `contratos` · `plano` | `instagram_coleta.py` | VALIDATION_TOOL | CLI própria, legítima |
| `semaforo` · `liquidar` | `instagram_coleta.py` | OPERATIONAL_CONTROL | CLI própria, legítima |

### A metade do trabalho que foi NÃO fazer

`yt-relevancia` pergunta «vale a pena esta fonte?». Registá-la como capacidade
de aquisição fazia o número de bypasses cair de uma vez — e punha juízo temático
dentro da coleta.

```
COLETAR != ADMITIR != JULGAR.
FABRICAR CAPACIDADE PARA BAIXAR O NÚMERO DE BYPASSES É MENTIR COM MÉTRICA.
```

---

## 4 · O RAMO QUE NINGUÉM RECLAMAVA

O `case` do `sintonia-scrap.yml` terminava em:

```sh
*)  PYTHONIOENCODING=utf-8 $PY coleta/instagram_coleta.py "${{ inputs.fase }}" ;;
```

Oito fases caíam ali, e **quatro delas são pagas**.

```
UMA PORTA QUE ACEITA O QUE NINGUÉM LISTOU É UMA PORTA QUE NINGUÉM MEDIU.
```

O ramo de omissão passou a `exit 2` com o nome da fase desconhecida. As 22 fases
oferecidas têm ramo próprio; nenhuma cai no vazio.

---

## 5 · O PORTÃO QUE FALTAVA NA SEGUNDA PORTA

O censo encontrou uma porta de Collection **fora** do `sintonia-scrap.yml`:
`comunicacao-publica.yml` corre `orquestrador/orquestrador.py`, que corre
`coleta/comunicacao_coleta.py`.

Para o YouTube isso já entrava pelo `scrap_executor.COLLECT`. Para as outras
três plataformas ia direto ao ator pago — e a política diz:

```
INSTAGRAM/FETCH_POST   ALLOWED
FACEBOOK/FETCH_POST    ALLOWED
LINKEDIN/FETCH_POST    ROUTE_NOT_ALLOWED   ← nas DUAS rotas declaradas
```

A rota paga do LinkedIn funcionava. Funcionar não é o mesmo que poder:

```
UMA ROTA QUE FUNCIONA NÃO É UMA ROTA PERMITIDA.
```

`fase_posts` passa a perguntar a `leis/social_matriz.py` **antes** de escolher o
ator — não depois, porque perguntar com o ator já escolhido é conferir o bilhete
depois da viagem. `NOT_DECLARED` também não passa: não declarado não é proibido,
mas para uma rota que gasta também não é permissão.

---

## 6 · OS DOIS BURACOS QUE FICAM, NOMEADOS

### 6.1 · O segundo runtime de Collection

```
PHASE                 comunicacao-publica.yml · fase `posts` · INSTAGRAM e FACEBOOK
OLD_IMPLEMENTATION    orquestrador/orquestrador.py → coleta/comunicacao_coleta.py
MISSING_CAPABILITY    nenhuma — INSTAGRAM/FETCH_POST e FACEBOOK/FETCH_POST estão DECLARADAS
MISSING_CONTRACT      a rota paga não está WIRED no registo de capacidades, e o
                      orquestrador tem recibo próprio (RUN-MANIFEST), admissão
                      própria e proveniência própria
WHAT_WOULD_BE_REQUIRED  registar a rota `apify:instagram-scraper` como capacidade
                      com rota; reconciliar RUN-MANIFEST com `collection_run`;
                      provar a equivalência de formato do artefato. As três
                      exigem execução PAGA, que esta missão não autoriza.
```

Isto **não** é um bypass direto: o orquestrador não é uma implementação, é um
segundo coordenador. Por isso o número dele vive numa linha própria.

```
UM BYPASS DIRETO É UMA PORTA QUE CORRE A IMPLEMENTAÇÃO.
UM SEGUNDO RUNTIME É OUTRA COISA, E CONTA-SE NOUTRA LINHA.
```

### 6.2 · As quatro fases de medição dentro da CLI canônica

O alcance de cada fase da CLI foi medido **por chamada**, com o grafo indexado
por `(módulo, função)` — porque um grafo indexado só por nome junta dois donos
com o mesmo nome, e nesta casa há `main` em quase todo o ficheiro.

```
FASES_DA_CLI               = 16
FASES_QUE_ALCANCAM_COLLECT =  3   (coletar, cutover, youtube-oficial)
FASES_QUE_NAO_ALCANCAM     = 13   (9 não adquirem nada; 4 adquirem)
```

As quatro que adquirem sem atravessar o boundary são `youtube`,
`youtube-piloto`, `youtube-piloto-oneshot` e `piloto`. **Não** foram
convertidas, e isso é desenho: `youtube` existe para medir a API diretamente e
`youtube-oficial` existe para medir a MESMA API pelo executor. O par É a
medição — fazer as duas entrarem pela mesma porta apagava a pergunta que elas
respondem.

O que se corrigiu foi o silêncio. Cada uma passa a declarar-se na saída:

```
DESVIO_DECLARADO=youtube
  Esta fase ADQUIRE e NAO atravessa `scrap_executor.COLLECT`.
```

```
UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.
```

---

## 7 · A PROVA, CONTRA POSTGRES DESCARTÁVEL

`provas/portas_canonicas_no_postgres.py` parseia o `case` do YAML **final**,
extrai o comando que cada fase corre e executa o equivalente local.

```
WORKFLOW_COMMAND_TARGETS_CANONICAL_ENTRYPOINT = YES
DIRECT_IMPLEMENTATION_IN_WORKFLOW             = NO   (para toda fase Collection)

run_id = RD-JANELA
RUN        falhou
etapas     CHECK/PASS · DISCOVER/FAIL
rota       instagram_janela.py:grade
run durável YES

NAVEGADOR_INTERCEPTADO = 1     (a rota chegou à porta e parou lá)
SAIDA_DE_REDE_REAL     = 0
PORTAS_CANONICAS=PASS
```

O `DISCOVER/FAIL` é o resultado certo: o navegador está interceptado, a rota
chega à porta e para. Uma etapa que fica em `RUNNING` seria o defeito — e ficava,
até se descobrir que `social_rotas.executar` apanha a excepção e o `except` do
boundary nunca corre. A rota da janela fecha a própria etapa.

```
UMA EXECUÇÃO QUE MORREU NÃO ESCREVE O PRÓPRIO FIM.
```

---

## 8 · MUTAÇÃO, RED TEAM, REGRESSÃO

```
MUTANTS   = 13
SURVIVORS =  0

ATTACKS            = 32
POSITIVE_FINDINGS  =  0
RED_TEAM_RESULT    = PASS

TESTS_BEFORE = 2359   FAILURES_BEFORE = 23
TESTS_AFTER  = 2380   FAILURES_AFTER  = 21
NEW_FAILURES =  0

SYSTEM_MAP_CHECK = PASS
```

### O mutante que sobreviveu por defeito da bateria

M7 (classificar JUDGMENT como Collection) sobreviveu na primeira volta, e a
sentinela matava-o quando corrida à mão. A causa: o `pyc` valida por
`(mtime, tamanho)`, e as linhas que M6 e M7 acrescentam têm **exactamente** o
mesmo comprimento. Escritas no mesmo segundo, o mutante M7 foi medido contra o
bytecode de M6.

```
UMA BATERIA QUE MEDE O MUTANTE ERRADO NÃO MEDE NADA.
```

A bateria passa a apagar `__pycache__` antes de cada volta, e `troca()` passa a
confirmar que a mutação chegou ao disco.

### Os quatro defeitos de sonda do red team

A primeira volta deu 16 achados. Doze eram da sonda:

- `instagram_coleta.py` **acaba** em `py`. Sem fronteira à esquerda, a linha
  `for f in instagram_coleta.py instagram_janela.py` casa como se `py` fosse o
  interpretador e o ficheiro seguinte o alvo. Oito achados, todos esta linha.
- Dois ataques contavam qualquer fase, não só as que adquirem — e contar
  `diario-fila` como bypass era fabricar Collection ao contrário.
- Dois ataques liam MENÇÃO como INVOCAÇÃO: dois ficheiros que apenas
  **imprimem** o próprio nome numa linha de `uso:`.

```
UMA SONDA SEM FRONTEIRA À ESQUERDA VÊ UM INTERPRETADOR NO FIM DE UM NOME DE FICHEIRO.
MENÇÃO NÃO É INVOCAÇÃO.
```

E um achado era real: a prova desta missão não estava declarada no System Map.

---

## 9 · O QUE ESTA MISSÃO NÃO FEZ

- Não executou coleta real. `NETWORK_REAL = 0`, `APIFY_RUNS = 0`,
  `PAID_RUNS = 0`, `COST_USD = 0`.
- Não tocou LIVE. Todo o Postgres é descartável, migrations 001–026.
- Não criou migration, não criou checkpoint paralelo, não criou segunda
  telemetria, não criou `scrap_cli_v2.py` nem `collection_runner_v2.py`.
- Não alterou `social_matriz.py`, não autorizou rota, não mexeu em Admission,
  Source Relevance, Intelligence ou Portal.
- Não reabriu aquisição remota de Instagram: `INSTAGRAM/FETCH_TRANSCRIPT`
  continua `ROUTE_NOT_ALLOWED` e a rede continua em zero.
- Não apagou benchmark. `BLOCKED != RETIRED`: as fases que recusam continuam na
  lista de escolha, com o motivo na saída, porque uma fase que desaparece não
  ensina nada a quem a procurar amanhã.
