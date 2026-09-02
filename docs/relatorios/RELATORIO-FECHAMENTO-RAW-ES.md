# O RAW ESPANHOL FECHOU — e o portão de importação abriu sozinho

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-collection-es` · **Base:** `c92e273`
**Esta rodada não importou nada, não aplicou migration e não tocou o Supabase de produção.**

---

## A prova, e de quem ela é

O operador executou, **na máquina local espanhola**:

```
py scripts/storage_preservar.py --enviar --so-ausentes
```

```
REMOTE_BEFORE               195      DO_PLANO_PRESENTES_BEFORE   195
ALVOS_AUSENTES                1
REMOTE_AFTER                196      DO_PLANO                196/196
ORFAOS                        0

ASSETS_ESPERADOS            196
PRESERVADOS_E_VERIFICADOS   196
FALHOS                        0      HASH_MISMATCH             0
SEM_ESTADO_CONHECIDO          0

POR_ESTADO   ALREADY_PRESENT_VERIFIED 195 · VERIFIED 1
```

O último asset — `media 4466`, *Folleto AVASTEL fungicida para cereal.pdf* — entrou depois
que o **Global file size limit** do Supabase subiu de 50 MB para 200 MB.

**Esta branch não executou o upload.** `VERIFICADO_DAQUI = NO`,
`ESTA_BRANCH_EXECUTOU_O_UPLOAD = NO`. Este ambiente não tem credencial de Supabase; recontar
daqui produziria zero, que é o defeito que já cometi uma vez nesta série de rodadas.
`CLOSED` aqui significa **recebido como prova externa**, não medido daqui.

## As duas causas, e por que só a segunda aparece agora

O caminho dos falhos foi **12 → 11 → 0**, e os três números não se corrigem:

| medição | resultado |
|---|---|
| 1ª · contagem de envio | 185 verificados · 11 falhos |
| 2ª · contagem de envio | 184 verificados · 12 falhos |
| 3ª · **inventário do bucket** | 185 presentes · 11 ausentes · 0 órfãos |
| 4ª · **reenvio só dos ausentes** | 196 presentes · 0 ausentes · 0 órfãos |

E as causas eram **duas**, não uma:

1. `HTTP 400 InvalidKey` — object key com caractere não-ASCII.
2. **Global file size limit de 50 MB**, para o asset de maior tamanho.

A segunda só ficou visível depois que a primeira foi corrigida. Enquanto os 11 eram um
bloco, "InvalidKey" parecia explicar tudo — e explicava a maioria. O histórico fica no
artefato porque guardar só o zero final faria o fechamento parecer que sempre esteve
fechado, e as duas causas medidas sumiriam junto.

## O portão abriu por derivação, não por digitação

`IMPORT_CAN_BE_NEXT_MISSION` não foi escrito. Ele sai de `scripts/portoes_eame.py`:

```
IMPORT = (CATALOG_IMPORT_ENGINEERING_GATE == READY) AND (RAW fechado)
```

E o estado do RAW passou a ser **derivado dos números**, com o campo `ESTADO` do artefato
servindo só de conferência. Antes eles eram dois donos da mesma verdade — e a forma ruim
disso seria alguém escrever `ESTADO: "CLOSED"` num arquivo e o portão de importação abrir
sem que nenhum número tivesse mudado. Agora, quando os dois discordam, o estado vira
`DIVERGENTE` e **nada abre**: falha fechada.

`tests/test_portoes_eame.py` cobre os quatro caminhos que burlariam a trava — faltam assets;
`ESTADO` diz CLOSED e os números dizem que não; há órfãos no bucket; há um hash divergente —
e mais o caso inverso, em que o catálogo cai para PARTIAL com o RAW fechado. Cada um deles
tem de manter `IMPORT = NO`, e o teste confirma no fim que com o dado real ele volta a YES —
sem isso, os cinco estariam verdes só porque a conta diz NÃO para tudo.

## Estado canônico

```
35/35 cicatrizes                  PROVED
LOCATION_CONTRACT_COMPLETE        YES     (derivado)
CATALOG_IMPORT_ENGINEERING_GATE   READY   16/16
EAME_COLLECTION_ENTRY_GATE        READY   35/35

RAW_PRESERVATION_GATE             CLOSED
  EXPECTED 196 · PRESENT 196 · ABSENT 0 · ORPHANS 0 · FAILED 0 · HASH_MISMATCH 0
  prova EXTERNA · VERIFICADO_DAQUI = NO

IMPORT_CAN_BE_NEXT_MISSION        YES
```

`YES` significa que a **próxima** missão pode ser a importação. Não que esta rodada deva
importar, e não que a importação já tenha acontecido.

## Próxima missão recomendada

**IMPORTAÇÃO CONTROLADA DO CATÁLOGO ADAMA ESPAÑA.**

O que ela herda pronto: `CAPTURE ≠ REGISTRATION` com a chave de captura e a seleção
as-of; `NOME IGUAL ≠ MESMO REGISTRO`; o bruto dos 196 assets preservado e conferido; e a
regra de que a importação é SQL idempotente sobre chave natural.

O que ela **não** herda resolvido, e precisa decidir na hora: `ES-CASE-001` continua
**ABERTA**, e o PDF local do NEPTUNE só entra pelo fluxo preservado.

**Nada foi importado nesta rodada. A instrução era fechar o portão e parar.**
