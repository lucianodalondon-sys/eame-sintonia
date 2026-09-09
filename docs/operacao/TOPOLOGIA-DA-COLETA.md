# TOPOLOGIA DA COLETA — o pente-fino, cartão a cartão e aresta a aresta

```
MISSAO      C-TOPOLOGY-1
BRANCH      claude/collection-topology-census-v1
BASE        collection b4310443  ·  system-map ffa9fb9b (lente read-only)
DATA        2026-09-09
VEREDITO    C-TOPOLOGY-1 = PASS
```

> **Todo número aqui é reproduzível.** O comando está ao lado. Um número sem
> comando não entrou.
>
> ```bash
> python3 system-map/scripts/censo_da_topologia.py
> python3 system-map/scripts/validate_system_map.py
> ```

---

## 1 · O QUE O UTILIZADOR VIA, E O QUE ERA

O Luciano abriu o mapa e viu sete coisas. Nenhuma era o que parecia.

| o que se via | o que era |
|---|---|
| cards sem ligação | **26 órfãos falsos por vista** — os vizinhos viviam noutra lente. No grafo inteiro, zero órfãos. |
| mais de um SINTONIA SCRAP | **quatro papéis distintos** com nomes que só divergiam no FIM do rótulo — e um quinto que estava no disco e não no mapa |
| cards fora da ordem do fluxo | a ordem era **alfabética por id**, e as zonas pela ordem de declaração. A ADMISSÃO aparecia **antes** do dono do RAW |
| cards atravessando etapas | a **Z-GUARDA** — onde vivem os donos do RAW e do DERIVED — estava na família «A ESPERA» |
| ligados directamente à Intelligence | 150 arestas, e **zero levam dado**. 78 são provas que MEDEM a coleta |
| edges difíceis de explicar | as **seis únicas** arestas `UNKNOWN` do mapa eram a esteira inteira |
| peças de função pouco clara | 24 sem chamador de runtime, das quais **9 são CLI documentado** e **3 ninguém corre** |

---

## 2 · OS NÚMEROS

```
CARTOES_AUDITADOS            104 de 104        (100%)
ARESTAS_AUDITADAS            532 de 532        (100%)

F-COLETA                      49  ->  64
F-ESPERA                      13  ->   1       (a Z-GUARDA saiu; o READY entrou)

SEM_LIGACAO verdadeiros                2       dois armazéns, terminais legítimos
ORFAOS_FALSOS_POR_VISTA               26
SEM_LIGACAO_INEXPLICADOS               0

DUPLICATE_LABELS                       0
COLISOES_DE_PREFIXO                    7       a maior: «A prova de...» ×7, toda em Z-PROVA

DIRECT_INTELLIGENCE_EDGES            150
  PROOF 78 · READ 38 · CODE 14 · RULE 12 · CONTROL 8
  DATA                                 0       nenhum dado salta a porta
UNEXPLAINED_DIRECT_EDGES               0

ENTRYPOINTS                           52
ALCANCADOS_POR_UMA_CORRIDA            60
SEM_CHAMADOR_DE_RUNTIME               24  (9 CLI documentado)
NINGUEM_CORRE                          3

NEW_FAILURES                           0
PRODUCTION_MUTATION                    0
```

---

## 3 · A ESTEIRA, DA ESQUERDA PARA A DIREITA

Derivada das `ETAPAS` canónicas — `medidas/rastro_da_coleta.ETAPAS` e
`leis/telemetria.ETAPAS_DA_COLETA` concordam palavra por palavra.

```
BIBLIA → ENTRADA → PEDIDO → ORQUESTRADOR → CANDIDATAS → FONTES
       → EXECUCAO → VEICULOS → FERRAMENTAS → ACOES
       → GUARDA (RAW · DERIVED) → ADMISSAO → ESPERA (READY)
       ────────────────────────────────────────────────────────
       apoio:  REGRAS · REGUAS · MEDIDAS · PROVA
```

| etapa | dono | ficheiro |
|---|---|---|
| REQUEST | `C-PEDIDO` | `pedido/pedido.py` |
| ROUTE | `C-ORQUESTRADOR` | `orquestrador/orquestrador.py` |
| ACQUISITION | `C-SCRAP-SOCIAL` e irmãos | `coleta/social_*.py` |
| RAW | `C-DONO-DA-ESCRITA` | `guarda/preservar_coleta.py` |
| DERIVED | `C-DONO-DO-DERIVADO` | `guarda/preservar_derivado.py` |
| STRUCTURED | **5 escritores, nenhum dono único** | gap `STRUCTURED_SEM_DONO_LIGADO` |
| ADMISSION | `C-ADMISSAO` | `admissao/admissao.py` |
| READY | `C-READY` | `admissao.pronto_para_inteligencia()` |
| INTELLIGENCE | **nenhum consumidor** | gap `READY_SEM_CONSUMIDOR` |

---

## 4 · SINTONIA SCRAP — o dossiê

Cinco peças, cinco papéis. Nenhuma é duplicata.

| cartão | papel | ficheiros |
|---|---|---|
| `C-SINTONIA-SCRAP` | despacho de **aquisição** (24 fases) | `.github/workflows/sintonia-scrap.yml` |
| `C-SCRAP-ROTA` | despacho de **rota e sessão** (`auth_mode`) | `.github/workflows/scrap-social.yml` |
| `C-SCRAP-SOCIAL` | **executor** | `coleta/social_*.py`, `youtube_oficial.py` |
| `C-SCRAP-GUARDA` | **guarda** de credencial e sessão | `guarda/social_guarda.py`, `social_sessao.py` |
| `C-SCRAP-LEIS` | **regras** — a taxonomia da falha | `leis/falhas.py`, `fundacao_da_coleta.py`, `social_matriz.py` |

`C-SCRAP-ROTA` **não existia no mapa**: o validador só exige dono para
ficheiros de código, e um `.yml` passava. Eram dois botões no repositório e um
no mapa.

### Onde o SCRAP entra na coleta — e onde ele não entra

```
SCRAP → conteudo · conteudo_visto_em · comentario     (escreve)
SCRAP → raw_asset                                      NÃO ESCREVE
```

Medido: `coleta/social_persistencia.py` escreve as três tabelas de conteúdo e
**não** escreve `raw_asset`. Os únicos escritores de `raw_asset` são
`guarda/preservar_coleta.py`, `guarda/catalogo_importar.py` e
`guarda/memoria_descartavel.py`, e o SCRAP não chama nenhum.

O próprio código já dizia, em `coleta/social_scrap.py:668`: *«PILOT_PROOF, não
OPERATIONAL_STORAGE. O dono forward do G-42 (Storage + raw_asset) NÃO recebeu
estes bytes.»*

O que faltava era um **nome que uma máquina lesse**: `SCRAP_RAW_NAO_RECEBIDO`,
agora em `coleta/social_envelope.py`, guardado por três casos em
`tests/test_politica_da_coleta.py`.

> **A rota social não atravessa RAW.** Ligá-la é decisão de arquitetura — muda
> o que se preserva, quanto custa e o que passa a ser reproduzível. Esta missão
> nomeia; não decide.

---

## 5 · A FRONTEIRA COM A INTELLIGENCE

**150 arestas atravessam. Zero levam dado.**

```
PROOF     78     provas que MEDEM a coleta
READ      38
CODE      14     imports
RULE      12     leis consultadas
CONTROL    8
DATA       0
```

136 das 150 vão para **Z-PROVA**. O que parecia «a coleta a falar com a
inteligência» é, quase todo, **a coleta a ser medida** — porque o território
das provas está na família da inteligência.

As três que o mapa mostrava como DATA eram falsas, e todas pela mesma causa:
a regra que promove a ligação de uma ferramenta de PREPARO a DATA disparava
sem olhar para o outro topo, e apanhava um censo que LÊ o `.py` da ferramenta
e uma lei que ela CONSULTA.

> **UMA PROVA QUE ME MEDE NÃO ESTÁ NO MEU CAMINHO.**
> **UMA REGRA QUE EU CONSULTO NÃO VIAJA COMIGO.**

Guardado por `T5b_nenhum_dado_salta_a_porta_para_a_inteligencia`, com uma
lista `TRAVESSIAS_AUTORIZADAS` vazia. Ele não exige zero para sempre: exige
que, se um dado passar a atravessar, alguém venha declarar a lei que o
autoriza. Mutação de red team (`RAW → Inteligência` sem contrato): reprova.

---

## 6 · O QUE CONTINUA ABERTO

| gap | estado | de quem é |
|---|---|---|
| `READY_SEM_CONSUMIDOR` | aberto, visível no cartão `C-READY` | arquitetura / Intelligence |
| `SCRAP_RAW_NAO_RECEBIDO` | aberto, nomeado | decisão de arquitetura |
| `STRUCTURED_SEM_DONO_LIGADO` | aberto | herdado do C-FINAL |
| `RAW_FORWARD_NAO_EMITE` | aberto | herdado |
| `ADMISSION_SEM_DONO_LIGADO` | aberto | herdado |
| `CHANNEL_IDENTITY_NOT_RESOLVED` | aberto | **decisão humana**: `IT-OWN-003` ou `IT-OWN-ARPAV` |
| `TELEMETRY_FAILURE_SEM_POLITICA` | aberto | herdado |
| rehome `regras/sensor_coleta.py` → `coleta/` | registado | mudança de código, não de mapa |

**Uma prova do mapa continua vermelha, e a reprovação é dela:**
`regua_que_carimba_nao_e_regua_que_mede` usa «tem seta para uma zona de acção»
para separar carimbar de medir. Nos quatro casos testados as setas são
`IMPORTS`, e a dependência vai ao contrário do desenho. Não foi afrouxada.

---

## 7 · PARA A LINHA DO SYSTEM MAP

1. **Z-PROVA (33 cartões) e Z-REGUAS (11) estão em `F-INTELIGENCIA`.** São
   provas e regras que servem a COLETA. Dar-lhes faixa própria é decisão de
   representação, e a representação é vossa. É a causa de 90 das 150 arestas
   que atravessam a fronteira.
2. **26 cartões são órfãos falsos por vista.** A correcção é alinhar as vistas
   de quem já fala entre si, não criar ligações.
3. Sete colisões de prefixo, a maior «A prova de...» ×7.

---

## 8 · O QUE NÃO FOI TOCADO

```
INTELLIGENCE_FUNCIONAL     NAO
PORTAL                     NAO
SECURITY                   NAO
VERCEL_PRODUCTION          NAO
SUPABASE_PRODUCTION        NAO
```
