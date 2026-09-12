# C10.8B-R — O BRUTO PAGO NÃO MORRE NO CHECKOUT

`C10_8B_R = PASS`

> A C10.8B-LIVE pagou por 59.743 bytes e o job seguinte não os encontrou.
> Agora um RAW escrito num job é recuperado noutra máquina pela identidade da
> corrida, com o SHA-256 recalculado, e reprocessado sem tocar no provider.
>
> E o pacote diz de si próprio que **não** é preservação forward canônica.
>
> ```
> APIFY_RUNS = 0 · PROVIDER_START_POSTS = 0 · PAID_USD = 0
> ```

---

## 1 · QUATRO ESTADOS QUE CABIAM NA PALAVRA «PRESERVADO»

```
RAW CAPTURADO NO PROCESSO
  != RAW QUE SOBREVIVE AO JOB
  != RAW DEVOLVIDO PARA INVESTIGAÇÃO
  != PRESERVAÇÃO FORWARD CANÔNICA.
```

A C10.8B-LIVE tinha o primeiro e chamava-lhe `PRESERVED`. O `.gitignore` ignora
`data/samples/**/*.gz`, o `actions/checkout` limpa o que o `.gitignore` ignora,
e o `SHA-256` sobreviveu a apontar para uma coisa que já não existia.

Esta missão fecha o **terceiro**, e só ele. O quarto continua por fazer, e está
escrito assim dentro de cada pacote.

---

## 2 · PRIMEIRO PROCURAR O DONO, DEPOIS ESCREVER

Antes de inventar mecanismo, a busca por `upload-artifact`, `download-artifact`,
`artifact` e `retention` no repositório inteiro.

```
EXISTING_JOB_TO_JOB_EVIDENCE_OWNER = YES  (metade)
```

| o que existia | onde | estado |
|---|---|---|
| `actions/upload-artifact@v4` | `.github/workflows/scrap-social.yml:376` | vivo |
| dono Python do inventário + SHA | `coleta/social_scrap.py::_raw_do_piloto` | vivo |
| `UPLOAD STEP SUCCESS != ARTIFACT EXISTS` | mesmo ficheiro | já lei |
| `actions/download-artifact` | **nenhum workflow** | ausente |

Faltava a metade da volta.

```
GUARDAR SEM NUNCA TER IDO BUSCAR NÃO É GUARDAR. É ESPERAR.
```

Por isso não nasceu módulo novo. A evidência passou a viver em quem já
inventaria RAW com SHA — `coleta/social_scrap.py` — e o que se acrescentou foi
`evidencia_publicar`, `evidencia_recuperar` e o `download-artifact` que nunca
existiu.

```
ONE CONCEPT → ONE OWNER.
```

---

## 3 · O BURACO QUE NINGUÉM VIA: O INVENTÁRIO NÃO CONHECIA O BRUTO PAGO

`coleta/coletor.py` grava o bruto pago com gzip e SHA próprios. Ele é o dono
daquele formato e **não** passa por `social_envelope.guardar_raw`. Só que quem
embala a evidência lê `social_envelope.produzidos()`.

```
O QUE O INVENTÁRIO NÃO VÊ NÃO ATRAVESSA A FRONTEIRA DO JOB.
```

O bruto mais caro da casa era o único invisível para o transporte. `coletor`
passou a registá-lo; `social_envelope.registar_produzido` anota, e mais nada —
não copia, não comprime, não normaliza.

---

## 4 · A FRONTEIRA, ATRAVESSADA DE FACTO

Não bastava subir e descer no mesmo processo Python: era isso que a C10.8B-LIVE
já fazia quando perdeu os bytes. `.github/workflows/scrap-evidencia.yml` põe
dois jobs em **duas máquinas**, com um artefato do Actions no meio.

Run [34707069109](https://github.com/lucianodalondon-sys/eame-sintonia/actions/runs/34707069109):

**JOB A** — runner `1000003887`

```
RAW_CAPTURED=YES
  SCRAP-EVID-34707069109.raw.json.gz   228.283 bytes  858fb594756b07c7…
  SCRAP-EVID-34707069109.raw.json      719.722 bytes  c5a47f13c6ccfcec…
RAW_READ_BACK=YES
EVIDENCE_TRANSFERRED=STAGED → YES
EVIDENCE_ARTIFACT_ID=10302640238
CANONICAL_FORWARD_PRESERVATION=NO
```

**JOB B** — runner `1000003889`, checkout limpo, nunca viu o ficheiro

```
WORKSPACE_RAW_BEFORE=ABSENT
RECOVERED=YES
SHA_MATCH=YES
  SCRAP-EVID-34707069109.raw.json.gz   228.283 bytes  match=YES
  SCRAP-EVID-34707069109.raw.json      719.722 bytes  match=YES
REPROCESS_ITEMS=20
REPROCESS_KEYS=['chars', 'transcript', 'url']
REPROCESS_NETWORK_USED=0
PROVIDER_CALLS=0
```

Vinte itens relidos e reprocessados numa máquina que nunca falou com a Apify.

```
RELER O QUE JÁ SE PAGOU NÃO É PAGAR OUTRA VEZ.
```

O job B **recusa-se** a correr se já tiver o ficheiro antes de o ir buscar:

```
UM JOB QUE JÁ TEM O FICHEIRO NÃO PROVA QUE O FOI BUSCAR.
```

---

## 5 · DUAS COISAS QUE A CONSTRUÇÃO REVELOU

### O `workflow_dispatch` não chega ao ramo onde o mecanismo nasce

Medido duas vezes, com o ficheiro já no remoto:

```
POST …/workflows/scrap-evidencia.yml/dispatches → 404 Not Found
```

`workflow_dispatch` só é disparável quando o ficheiro já vive no ramo padrão.

```
UM WORKFLOW QUE SÓ O RAMO PADRÃO PODE DISPARAR
NÃO PROVA NADA NO RAMO ONDE O MECANISMO FOI ESCRITO.
```

O conserto foi um `push` com filtro de caminhos: quando o mecanismo da evidência
muda, ele volta a provar-se. O `workflow_dispatch` ficou, e passa a servir
quando o ficheiro chegar ao ramo padrão.

### A sonda de segredo dava verde ao que não conseguia ler

A primeira versão lia os bytes do ficheiro. O bruto pago nasce **comprimido** —
um token dentro do gzip passaria inteiro.

```
UMA SONDA QUE NÃO DESCOMPRIME DÁ VERDE AO QUE NÃO CONSEGUE LER.
```

Agora descomprime e olha as duas formas. Um gzip ilegível devolve
`GZIP_ILEGIVEL`, e não «limpo».

---

## 6 · SEGREDO NÃO VIAJA, E A RECUSA NÃO APAGA EVIDÊNCIA

Seis termos são procurados nos bytes de cada ficheiro: `apify_api_`,
`Authorization:`, `Bearer `, `set-cookie`, `X-Api-Key`, `SUPABASE_SERVICE_ROLE`.

Encontrando um, `EvidenciaComSegredo` levanta e **nada é escrito** — nem pacote
meio feito, nem ficheiro redigido.

```
MELHOR FALHAR ALTO DO QUE REDIGIR EM SILÊNCIO:
apagar evidência para o pacote passar destrói a coisa que o pacote existe
para guardar.
```

---

## 7 · O QUE O PACOTE DIZ QUE NÃO É

Cada `MANIFESTO.json` carrega, ao lado dos SHA:

```
EVIDENCE_CLASS                   DIAGNOSTIC_JOB_TO_JOB
EVIDENCE_RETENTION               TEMPORARY
EVIDENCE_RETENTION_DAYS          30
CANONICAL_FORWARD_PRESERVATION   NO
```

```
WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE.
```

Trinta dias é retenção finita, e dizê-lo é metade do contrato. O dono forward
(Storage + `raw_asset`) **não** recebeu estes bytes, e o `RUN_ID` daqui **não**
é um `RAW_OBSERVATION_ID`. Nenhum `SOURCE_ID` ou `DOCUMENT_ID` foi fabricado.

A recuperação é pela identidade da corrida, e só por ela — não existe volta que
escolha «o último artefato»:

```
UM PACOTE DE OUTRA CORRIDA COM A MESMA CARA NÃO É ESTE PACOTE.
```

E o SHA do manifesto nunca é aceite sozinho:

```
UM SHA QUE SÓ VEM DO MANIFESTO NÃO PROVA OS BYTES.
```

---

## 8 · MEDIDO

```
APIFY_RUNS                        0
PROVIDER_START_POSTS              0
PAID_USD                          0.00
AUTHORIZED_NEW_SPEND_USD          0
NETWORK_USED_NO_REPROCESSAMENTO   0

JOB_A_RAW_CAPTURED                YES
JOB_A_ARTIFACT_ID                 10302640238
JOB_B_LOCAL_BEFORE                ABSENT
JOB_B_RECOVERED                   YES
SHA_MATCH                         YES
REPROCESS_ITEMS                   20

RED_TEAM_ATTACKS                  40
RED_TEAM_SURVIVORS                0
MUTATIONS                         14
MUTATION_SURVIVORS                0

CANONICAL_FORWARD_PRESERVATION    NO
EVIDENCE_RETENTION                TEMPORARY · 30 dias
```

---

## 9 · O QUE NÃO MUDOU

A rota `apify:transcricao` continua **`PARTIAL`**. Nada correu no provider, e
por isso nada há para promover nem para rebaixar.

```
PROVIDER REACHED != CAPABILITY DELIVERED.
```

O `.gitignore` não foi tocado: o Git continua a não ser object storage, e nenhum
`.gz`, vídeo, áudio ou dataset pago entrou na árvore. O pacote de evidência vive
em `.tmp/`, fora do acervo.

Collection, Admission, Intelligence e Portal não foram tocados.

---

## 10 · O QUE CONTINUA DESCONHECIDO

Os 59.743 bytes da C10.8B-LIVE **não voltam**. Eles já não existem, e este
mecanismo não os ressuscita — só garante que o próximo não se perde.

Por que a transcrição veio vazia naquela corrida continua sem resposta: deriva
do esquema de saída do ator, ou vídeo que perdeu as legendas. Responder exigiria
comprar outra vez, e isso não está autorizado.

---

## 11 · RISCO RESTANTE

A retenção é de 30 dias. Um bruto pago que ninguém investigue nesse prazo
desaparece do artefato — e continuará a desaparecer até o dono forward existir.

```
PRESERVAÇÃO COM PRAZO É PRESERVAÇÃO COM PRAZO, E NÃO PRESERVAÇÃO.
```

O trabalho que fecha isto é a camada forward da Collection, e ela **não** foi
começada aqui.
