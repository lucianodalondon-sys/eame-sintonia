# BACKLOG VIVO — SINTONIA EAME

## Para que este arquivo existe

Este arquivo guarda **coisas que precisamos fazer, decidir, medir ou implementar e que não podem ser esquecidas**.

Ele NÃO substitui o know-how.

- **Know-how** = o que aprendemos e queremos preservar como conhecimento.
- **Backlog Vivo** = o que ainda precisamos fazer ou verificar.

Este arquivo também NÃO é uma autoridade de arquitetura. Uma ideia aqui só vira contrato, owner, régua ou implementação quando passar pela missão correta e for medida.

## Regra de uso

Cada novo item deve entrar com:

- `STATUS`
- `ÁREA`
- `O QUE FALTA`
- `POR QUE IMPORTA`
- `DEPENDÊNCIAS`
- `COMO SABER QUE FECHOU`

Estados permitidos:

- `IDEIA`
- `PRECISA_MEDIR`
- `PLANEJAR`
- `PRONTO_PARA_EXECUTAR`
- `EM_EXECUCAO`
- `FEITO`
- `DESCARTADO`

Nunca apagar um item concluído. Mover para `FEITO` e registrar a evidência/commit quando existir.

---

# ITENS ABERTOS

## BV-001 — Arquitetura híbrida Cloud + Local Edge Worker

**STATUS:** PLANEJAR  
**ÁREA:** Infraestrutura / Collection

**O QUE FALTA**

Formalizar o modelo híbrido em que a nuvem coordena estado, filas, dados e portal, enquanto uma máquina local ligada 24/7 executa tarefas que ganham com GPU, browser autenticado, sessão local ou processamento pesado.

Modelo desejado, ainda não declarado como implementação fechada:

```text
NUVEM
- portal
- fila / agenda
- estado das corridas
- Supabase / dados centrais
- telemetria
- distribuição de jobs

MÁQUINA LOCAL 24/7
- SINTONIA Scrap local
- browser/sessões autenticadas
- ffmpeg
- GPU
- transcrição local
- processamento pesado quando fizer sentido
```

**POR QUE IMPORTA**

Evita pagar nuvem/API por tarefas que podem ser muito mais rápidas e baratas na GPU local e permite rotas que dependem de sessão autenticada.

**DEPENDÊNCIAS**

Collection canônica, executor registry, fila de jobs, telemetria e segurança de credenciais locais.

**COMO SABER QUE FECHOU**

Existe contrato claro Cloud ↔ Local Worker, heartbeat, job idempotency, fila, resultado, erro e comportamento quando a máquina fica offline.

---

## BV-002 — Local Worker não pode depender do Claude

**STATUS:** PLANEJAR  
**ÁREA:** Infraestrutura / Collection

**O QUE FALTA**

Garantir que o serviço local do SINTONIA rode sozinho como infraestrutura permanente.

Claude pode estar instalado/logado na mesma máquina, mas Collection, Scrap e transcrição não podem depender de Claude aberto, créditos disponíveis ou uma sessão de agente ativa.

**POR QUE IMPORTA**

Coleta precisa ser previsível e continuar funcionando mesmo se Claude estiver indisponível.

**DEPENDÊNCIAS**

BV-001.

**COMO SABER QUE FECHOU**

Desligar Claude não interrompe coleta, browser local, transcrição, heartbeat nem entrega de resultados.

---

## BV-003 — Transcrição local por GPU

**STATUS:** PRECISA_MEDIR  
**ÁREA:** Collection / DERIVED

**O QUE FALTA**

Escolher e tornar canônico o transcritor local acelerado por GPU.

Hipótese forte a medir: `faster-whisper`/Whisper com GPU NVIDIA/CUDA.

A transcrição deve ser uma transformação da Collection, não responsabilidade do coletor da fonte.

Fluxo conceitual:

```text
AQUISIÇÃO
→ RAW
→ extração de áudio quando necessária
→ transcrição GPU
→ DERIVED/transcript
→ STRUCTURED
→ ADMISSION
→ READY
```

**POR QUE IMPORTA**

Testes locais indicaram vantagem relevante de velocidade e custo em relação a transcrição paga em nuvem.

**DEPENDÊNCIAS**

T-61 Transcrição, T-30 DERIVED, Local Edge Worker.

**COMO SABER QUE FECHOU**

Benchmark reproduzível mede velocidade, custo, qualidade, uso de GPU e fallback; um owner canônico é escolhido e o transcript preserva vínculo/proveniência com a evidência original.

---

## BV-004 — Stories: vídeo temporário → áudio → transcrição → apagar vídeo

**STATUS:** PLANEJAR  
**ÁREA:** Collection / Stories

**O QUE FALTA**

Fechar a rota local de Stories sem Apify e sem retenção do vídeo original.

Regra desejada:

```text
Story
→ texto nativo útil? preservar texto + metadados
→ senão, se houver áudio/vídeo:
   vídeo temporário
   → extrair áudio
   → hash/proveniência
   → transcrição local
   → apagar vídeo em finally
```

Para conteúdo visual-only sem texto/áudio: `VISUAL_ONLY`; OCR não entra automaticamente.

**POR QUE IMPORTA**

Story é efêmero e a coleta precisa acontecer enquanto o conteúdo está disponível, sem transformar retenção de mídia em requisito permanente.

**DEPENDÊNCIAS**

SINTONIA Scrap local, sessão autenticada, BV-003.

**COMO SABER QUE FECHOU**

Prova viva com `APIFY_CALLS=0`, `PAID_API_CALLS=0`, vídeo temporário removido, transcript/áudio preservado conforme contrato e dedupe em segunda execução.

---

## BV-005 — Central de Operações / Coleta no Portal

**STATUS:** PLANEJAR  
**ÁREA:** Portal / Operações

**O QUE FALTA**

Criar uma área do Portal SINTONIA onde seja possível acompanhar a Collection sem depender de terminal, GitHub ou Claude.

A tela deve mostrar pelo menos:

- o que está rodando agora;
- fonte;
- executor;
- execução em nuvem ou local;
- início/fim/duração;
- itens encontrados;
- novos/reutilizados;
- RAW gerados;
- DERIVED gerados;
- Admission por estado;
- READY gerados;
- falhas e motivo;
- custo conhecido / `NÃO SEI` quando não medido;
- saúde de cada fonte;
- saúde do Local Worker;
- fila de transcrição;
- minutos de áudio processados;
- uso/estado da GPU;
- sessão autenticada/challenge/offline quando aplicável;
- última e próxima corrida prevista.

Cada corrida deve ter uma ficha própria e rastro verificável.

**POR QUE IMPORTA**

O operador precisa saber “o que está acontecendo agora” sem olhar o System Map.

**DEPENDÊNCIAS**

Collection precisa primeiro produzir telemetria verdadeira e owners canônicos para os números.

**COMO SABER QUE FECHOU**

Uma corrida real pode ser acompanhada ponta a ponta no portal e todos os números visíveis têm owner/evidência.

---

## BV-006 — Separar claramente System Map, Operações e Intelligence

**STATUS:** PLANEJAR  
**ÁREA:** Produto / Portal

**O QUE FALTA**

Manter três perguntas em superfícies diferentes:

```text
SYSTEM MAP
“Como o SINTONIA está montado e quem liga em quem?”

OPERAÇÕES / COLETA
“O que está rodando, coletando, falhando e custando agora?”

INTELLIGENCE
“O que descobrimos, cruzamos, julgamos e recomendamos?”
```

**POR QUE IMPORTA**

Evita transformar o mapa arquitetural em dashboard operacional ou misturar coleta com análise.

**DEPENDÊNCIAS**

BV-005 e futura camada de Intelligence.

**COMO SABER QUE FECHOU**

Cada informação tem uma única casa e não há dashboards duplicando a mesma autoridade.

---

## BV-007 — Claude local como agente de Intelligence, depois da Collection

**STATUS:** IDEIA  
**ÁREA:** Intelligence

**O QUE FALTA**

Desenhar futuramente como Claude, logado na máquina local, participa da camada de Intelligence.

Claude NÃO participa da operação normal da Collection.

Possível responsabilidade futura:

- ler READY/evidências autorizadas;
- cruzar materiais;
- propor claims/hipóteses/julgamentos;
- produzir análises;
- trabalhar sob contratos e gates de Intelligence;
- deixar rastro do que recebeu e do que produziu.

**POR QUE IMPORTA**

Permite usar o agente como cérebro analítico sem transformar IA em infraestrutura básica de coleta.

**DEPENDÊNCIAS**

Collection chegando honestamente a READY e contratos de Intelligence fechados.

**COMO SABER QUE FECHOU**

Existe contrato READY → Intelligence → resultado, auditável, e desligar Claude não afeta Collection.

---

## BV-008 — Interface READY → Intelligence

**STATUS:** IDEIA  
**ÁREA:** Collection / Intelligence Boundary

**O QUE FALTA**

Projetar somente depois de READY estar fechado:

- como Intelligence recebe um READY;
- fila/consumer;
- acknowledgement;
- retry;
- versão do contrato;
- evidência e estado epistêmico preservados;
- rastro da leitura;
- resposta/resultado ligado ao READY original.

**POR QUE IMPORTA**

Hoje `READY_SEM_CONSUMIDOR` é um gap legítimo. Não devemos criar consumidor fictício apenas para fechar o desenho.

**DEPENDÊNCIAS**

READY V2 e fechamento da Collection.

**COMO SABER QUE FECHOU**

Primeiro consumer real de Intelligence pode ser ligado sem alterar o contrato histórico da Collection.

---

## BV-009 — Heartbeat e saúde da máquina local

**STATUS:** PLANEJAR  
**ÁREA:** Infraestrutura / Observabilidade

**O QUE FALTA**

A nuvem precisa saber, sem abrir acesso manual à máquina:

- worker online/offline;
- última atividade;
- versão do worker;
- GPU disponível;
- fila local;
- espaço em disco;
- browser disponível;
- estado de sessão por fonte sem expor cookies/segredos;
- job atual;
- último erro.

**POR QUE IMPORTA**

Uma arquitetura híbrida sem observabilidade cria falhas silenciosas.

**DEPENDÊNCIAS**

BV-001.

**COMO SABER QUE FECHOU**

Desligar a máquina ou perder a sessão produz estado operacional claro no portal e nunca um falso `OK`.

---

## BV-010 — Segurança das sessões e segredos do Local Worker

**STATUS:** PLANEJAR  
**ÁREA:** Security / Local Worker

**O QUE FALTA**

Definir como browser profiles, cookies, tokens e credenciais locais ficam protegidos e como seu estado é reportado sem vazar o segredo.

Nunca publicar cookie/token no Git, log, telemetria ou portal.

**POR QUE IMPORTA**

O Local Worker terá acesso a sessões autenticadas e pode se tornar uma superfície crítica.

**DEPENDÊNCIAS**

BV-001 e Security Foundation.

**COMO SABER QUE FECHOU**

Há contrato de secret handling, redaction test e prova de que telemetria operacional não contém credenciais.

---

## BV-011 — Proveniência de registro regulatório: falta run_id

**STATUS:** PLANEJAR  
**ÁREA:** Collection / Structured / Proveniência

**O QUE FALTA**

`registro_regulatorio` existe como conceito/store canônico, mas o C-PLAN-A4 mediu que a tabela não carrega `run_id`.

**POR QUE IMPORTA**

Sem `run_id`, o registro estruturado perde uma ligação direta com a corrida que o produziu e enfraquece a proveniência ponta a ponta.

**DEPENDÊNCIAS**

Não bloqueia o primeiro slice `SOURCE_DOCUMENT`. Deve ser tratado na missão específica de proveniência/schema do conceito regulatório.

**COMO SABER QUE FECHOU**

Cada novo `REGULATORY_REGISTRATION` pode ser ligado deterministicamente à corrida que o produziu, com backfill/compatibilidade definidos para registros históricos.

---

## BV-012 — caption_source real fora do enum atual

**STATUS:** PRECISA_MEDIR  
**ÁREA:** Collection / Social / Transcrição

**O QUE FALTA**

O C-PLAN-A4 mediu 15 legendas cujo `caption_source` real aparece como `PLATFORM_CAPTIONS via Apify`, fora dos quatro valores atualmente aceitos pelo contrato/enum.

É preciso decidir com medição se existe um valor canônico equivalente, se o enum deve ganhar uma origem como `PLATFORM_FETCHED`, ou se os históricos precisam permanecer `NÃO SEI`.

**POR QUE IMPORTA**

Não podemos reclassificar silenciosamente a origem de uma legenda só para fazê-la caber no enum.

**DEPENDÊNCIAS**

Não bloqueia `SOURCE_DOCUMENT`. Tratar quando entrar o slice social/transcrição.

**COMO SABER QUE FECHOU**

Todas as legendas novas recebem `caption_source` válido e fiel à origem observada; os 15 históricos ficam classificados por evidência ou explicitamente `NÃO SEI`, sem inferência silenciosa.

---

# FEITOS

Nenhum item deste arquivo foi marcado como `FEITO` na criação inicial.

---

# REGRA FINAL

Este arquivo existe para impedir dois erros:

1. ter uma ideia importante durante uma missão e esquecê-la porque estava fora do escopo;
2. transformar toda boa ideia em uma nova missão imediatamente e perder o foco do trabalho atual.

A regra é:

> **IDEIA BOA FORA DO ESCOPO → REGISTRA AQUI → CONTINUA A MISSÃO ATUAL.**

Depois, quando chegar a hora certa, o item é medido, recebe owner, contrato e gate — ou é descartado honestamente.
