# SINTONIA EAME — IDEIAS E PENDÊNCIAS

Este arquivo existe para não perder ideias, necessidades futuras, decisões ainda não executadas e melhorias que surgirem durante o trabalho.

Ele NÃO substitui o KNOW-HOW.

- KNOW-HOW = o que já aprendemos, medimos e sabemos reproduzir.
- IDEIAS E PENDÊNCIAS = o que precisamos lembrar de construir, testar, decidir ou melhorar depois.

Regra de uso:

1. registrar a ideia no momento em que surgir;
2. não transformar automaticamente em missão urgente;
3. manter separadas `IDEIA`, `PENDÊNCIA`, `DECISÃO FUTURA` e `DÍVIDA MEDIDA`;
4. nunca marcar como feito sem evidência;
5. quando virar trabalho ativo, apontar branch/commit/missão;
6. quando fechar, mover para `CONCLUÍDO` com evidência ou remover apenas se houver histórico em outro owner canônico.

---

## ABERTO

### I-001 — Central de Operações / Coleta no Portal SINTONIA

**TIPO:** IDEIA / PRODUTO

Criar no Portal SINTONIA uma área de Operações / Coleta para acompanhar remotamente o funcionamento da Collection.

Deve permitir acompanhar, sem depender de terminal ou Claude:

- o que está sendo coletado agora;
- fonte e executor em uso;
- execução em nuvem ou máquina local;
- início/fim/duração da corrida;
- itens encontrados, novos, reutilizados e falhos;
- RAW preservados;
- DERIVED gerados;
- Admission por estado;
- READY produzidos;
- última coleta e próxima execução por fonte;
- custo externo da corrida;
- saúde da máquina local;
- erros de sessão/login;
- fila de transcrição;
- minutos de áudio processados;
- estado/ocupação da GPU;
- Stories encontrados e processados.

**LEI:** o painel deve mostrar métricas produzidas pelos owners reais da Collection. Não criar números ou estados apenas para preencher a interface.

**QUANDO:** depois de a Collection contar a verdade de forma canônica; casco/UI depois dos contratos e owners.

---

### I-002 — Arquitetura híbrida Cloud Control Plane + Local Edge Worker

**TIPO:** DECISÃO FUTURA / ARQUITETURA

Consolidar formalmente o SINTONIA como arquitetura híbrida.

**NUVEM / CONTROL PLANE**

Responsabilidades candidatas:

- agenda/orquestra jobs;
- mantém fila e estado;
- registra runs;
- recebe resultados;
- persiste dados canônicos;
- serve portal;
- expõe telemetria e saúde;
- detecta worker offline;
- coordena retry global conforme contrato da Collection.

**MÁQUINA LOCAL / EDGE WORKER**

Responsabilidades candidatas:

- browser local autenticado;
- sessões de plataformas que dependem de login;
- SINTONIA Scrap local;
- aquisição que depende da máquina local;
- processamento com GPU;
- ffmpeg;
- transcrição local;
- trabalhos pesados que forem comprovadamente mais eficientes localmente.

**LEI:** a máquina local é infraestrutura. Claude não deve ser dependência operacional da Collection.

---

### I-003 — Transcrição local por GPU

**TIPO:** IDEIA / OTIMIZAÇÃO

Medir e consolidar um owner de transcrição que possa rodar localmente usando GPU NVIDIA.

Candidato a medir: `faster-whisper`/Whisper com aceleração GPU.

Objetivo:

- reduzir custo variável de APIs de transcrição;
- acelerar processamento de vídeos/áudios;
- evitar upload desnecessário de mídia para terceiros;
- aproveitar máquina local 24/7;
- preservar ligação entre mídia/áudio/transcript.

**CONTRATO CONCEITUAL:**

`aquisição → RAW/preservação permitida → transformação/transcrição → DERIVED → estruturação → Admission → READY`

Transcrição pertence à Collection/transformação, não à Intelligence.

**NÃO ASSUMIR:** ferramenta canônica atual. Medir antes de declarar `faster-whisper` como owner oficial.

---

### I-004 — Política de mídia temporária para Stories

**TIPO:** DECISÃO FUTURA / CONTRATO

Para Stories sem texto nativo útil e com áudio:

`Story → vídeo temporário → extração de áudio → hash/proveniência → transcrição local → apagar vídeo temporário`

Preservar:

- Story ID;
- conta/source;
- URL quando disponível;
- publication time;
- observed time;
- collected time;
- texto nativo quando existir;
- áudio/hash quando necessário;
- transcript;
- proveniência.

Manter:

`ORIGINAL_VIDEO_RETAINED = NO`

`TEMP_VIDEO_FILES_REMAINING = 0`

Não inferir FACT_TIME a partir da publicação do Story.

---

### I-005 — Saúde do Edge Worker no Portal

**TIPO:** IDEIA / OBSERVABILIDADE

O Portal deve mostrar saúde da máquina local sem expor credenciais ou cookies.

Estados candidatos:

- worker online/offline;
- heartbeat;
- versão do executor;
- Chrome presente;
- perfil presente;
- sessão autenticada / não autenticada / challenged / unknown;
- GPU disponível;
- fila local;
- último job aceito;
- último job concluído;
- último erro;
- espaço em disco;
- transcritor disponível.

Separar sempre:

`WORKER_OFFLINE ≠ SESSION_INVALID ≠ SOURCE_FAILURE ≠ JOB_FAILURE`

---

### I-006 — Claude na Intelligence, não como dependência da Collection

**TIPO:** DECISÃO FUTURA / FRONTEIRA

A máquina local poderá ter Claude/Claude Code disponível para a futura camada de Intelligence, mas:

- SINTONIA Scrap deve funcionar sem Claude;
- transcrição GPU deve funcionar sem Claude;
- Collection deve funcionar sem Claude;
- indisponibilidade, sessão ou créditos de Claude não podem parar coleta.

Na Intelligence, estudar depois como Claude consome READY/material autorizado, produz análises e devolve resultados auditáveis.

**FORA DE ESCOPO AGORA:** desenhar o contrato da Intelligence.

---

### I-007 — Scheduler híbrido nuvem ↔ worker local

**TIPO:** IDEIA / INFRAESTRUTURA

Precisamos de um mecanismo canônico para:

- publicar job;
- worker local buscar/receber job;
- reservar job sem duplicação;
- heartbeat/lease;
- timeout;
- resultado;
- retry global;
- retry local de transporte;
- idempotência;
- atualização de estado no portal.

Não definir tecnologia antes de medir o que já existe no repo.

**LEI:** Claude não é scheduler.

---

### I-008 — Custos cloud vs local

**TIPO:** PENDÊNCIA / MEDIÇÃO

Medir por tipo de tarefa:

- transcrição API vs GPU local;
- coleta cloud vs Edge Worker;
- custo de storage;
- custo de processamento;
- energia/amortização da máquina local;
- tempo de execução;
- tráfego/upload evitado.

Resultado deve ser medido por corrida/tarefa, não estimado como verdade.

---

### I-009 — Fila de transcrição e prioridade

**TIPO:** IDEIA / OPERAÇÃO

Quando houver volume real, avaliar fila de transcrição com prioridade por:

- Story efêmero;
- fonte crítica;
- reunião/evento recente;
- SLA de Collection;
- tamanho/duração;
- disponibilidade da GPU.

Não criar score mágico. A prioridade precisa ter política explícita.

---

### I-010 — Continuidade quando a máquina local estiver offline

**TIPO:** PENDÊNCIA / RESILIÊNCIA

Definir comportamento quando Edge Worker estiver offline.

Distinguir por rota:

- rota que pode esperar;
- rota com fallback cloud legítimo;
- rota sem fallback;
- Story que pode expirar antes da volta do worker.

Não introduzir fallback pago ou terceiro silenciosamente.

---

## DÍVIDAS JÁ MEDIDAS QUE NÃO PODEM SER ESQUECIDAS

Estas dívidas têm owner/missão própria e não devem virar melhorias oportunistas dentro de outra frente:

- `READY_SEM_CONSUMIDOR`;
- `SCRAP_RAW_NAO_RECEBIDO`;
- `STRUCTURED_SEM_DONO_LIGADO`;
- identidade RAW/schema: `storage_path` não pode continuar como identidade semântica;
- `raw_asset` precisa de SOURCE_ID no contrato futuro;
- `derived_artifact` precisa de RUN_ID no contrato futuro;
- READY precisa preservar estado epistêmico/evidência de FACT_TIME e FACT_LOCATION;
- T-04 deve ser o único cérebro da corrida;
- Admission precisa convergir de 3 callers runtime para 1;
- T-32 precisa atravessar espécies além do PDF sem transformar etapa não aplicável em bypass;
- `IT-T2-002` ainda depende da decisão `IT-OWN-003` vs `IT-OWN-ARPAV`;
- contratos de referência OpenAlex/ORCID ainda precisam ser escritos;
- segundo vocabulário de tipos de executores precisa convergir para um owner canônico;
- dez manifests históricos continuam com dívida de campos e não podem ser preenchidos por invenção.

---

## CONCLUÍDO

Nenhum item neste arquivo deve ser marcado como concluído sem branch/commit/prova.

---

## TEMPLATE PARA NOVAS ENTRADAS

```text
### I-XXX — Título

TIPO = IDEIA | PENDÊNCIA | DECISÃO FUTURA | DÍVIDA MEDIDA

POR QUE NÃO PODEMOS ESQUECER
...

O QUE PRECISA EXISTIR/FECHAR
...

DEPENDÊNCIAS
...

NÃO FAZER
...

QUANDO ENTRA
...

EVIDÊNCIA DE CONCLUSÃO
branch / commit / gate / medição
```

---

# PRINCÍPIO

Este arquivo é uma memória operacional do futuro do SINTONIA.

Ele existe para que uma boa ideia surgida durante outra missão não seja perdida, mas também não desvie a missão atual.

**REGISTRAR ≠ PRIORIZAR ≠ IMPLEMENTAR.**
