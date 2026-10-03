# A POLÍTICA DOS DOIS ARMAZÉNS

**C-PLAN-B3** · decisão, zero implementação · ramo `claude/raw-observation-identity-3jbwco`
· HEAD `ac46a6ec`

> Nada foi implementado. Zero alteração em `coleta/`, `guarda/`, `orquestrador/`, `pedido/`,
> `supabase/migrations/`, `tests/` e `system-map/`. Zero rede, zero escrita em banco de
> produção, zero escrita no acervo real. As medições correram contra `MemoriaDescartavel` e
> `ArmazemLocal` apontado para um `tmpdir` que morreu no fim.

---

## 0 · A CORREÇÃO QUE ABRE ESTE DOCUMENTO

O C-IMPL-B1 entregou esta frase, escrita por mim:

> *«Os bytes são os mesmos, e o armazém endereça por sha: a segunda corrida REUSA o objecto
> em vez de criar outro.»*

**Está errada, e a medição está abaixo.** A segunda corrida não reusa: ela **conflita**, o
banco não recebe uma linha sequer, e a própria `collection_run` dela nunca chega a existir.

O que enganou foi a contagem. `raw_asset` tinha 4 linhas antes e 4 depois, e eu li isso como
reuso. Contagem igual tem duas causas possíveis, e elas são opostas:

```
CONTAGEM NÃO AUMENTOU
  ├── REUSE CORRETO        o objeto já existia, e a corrida aproveitou-o
  └── ESCRITA IMPEDIDA     havia conflito, e nada foi gravado
```

Chamar o segundo de primeiro é o erro mais caro deste sistema, porque ele faz uma falha
parecer um acerto.

---

## A · OS TRÊS LUGARES, MEDIDOS SEPARADAMENTE

Não são dois. São três, e cada um responde a uma pergunta diferente.

| # | lugar | o que guarda | autoridade sobre |
|---|---|---|---|
| 1 | `data/collection-ledger/italy/observations.ndjson` | história de observação | saúde e cadência da fonte |
| 2 | `data/collection-store/italy/` | bytes | **nada — e é esse o problema** |
| 3 | `guarda/preservar_coleta.py` → `Armazem` | bytes | o RAW canónico |

### 1 · O LIVRO DE OBSERVAÇÃO

```
144 observações · 6 corridas · 35 conteúdos distintos · 35 documentos distintos
```

Ele já vive a relação que o banco não sabe representar: **144 observações para 35
conteúdos**. Um documento visto seis vezes é seis observações e um conteúdo, e o livro
escreve isso sem esforço porque é append-only e não tem chave única nenhuma.

Ele **não é reconstruível**. Guarda `HEALTH_STATE`, `CADENCE_STATE`, `PARSE_ERROR`,
`DISCOVERY_DEGRADED`, `OBSERVATION_RESULT` — coisas que nenhum armazém de bytes conhece.
Apagá-lo perderia a única memória de que uma fonte adoeceu.

> **O livro não vira armazém. O armazém não vira livro.**

### 2 · O STORE ITALIANO — a medição que decide tudo

```
RAW_PATH distintos no livro      35
  que existem nesta árvore       10
  que apontam para C:/…          25   ← uma máquina Windows que não é este repositório
observações sem RAW_PATH        109   ← as SEEN_AGAIN de antes do B1
```

Os 25 apontam para `C:/eame-sintonia-ops/data/collection-store/italy/…`. **O livro guarda
caminhos absolutos da máquina que correu a coleta.** De outra máquina, aqueles bytes não
existem — e o caminho não diz que não existem, diz um endereço que não abre.

```
UM ARQUIVO QUE SÓ ABRE NA MÁQUINA QUE O ESCREVEU NÃO É UM ARQUIVO.
É UMA PASTA PESSOAL COM NOME DE INSTITUIÇÃO.
```

Dos 35 conteúdos que o livro diz ter preservado, esta árvore alcança 10. Não é um arquivo
incompleto por acidente de commit: é um arquivo que **nunca teve como estar completo**,
porque o endereço é local e a coleta corre em duas casas.

### 3 · O ARMAZÉM CANÓNICO

`guarda/preservar_coleta.py` é o único escritor de RAW desta casa, e endereça assim:

```
PAÍS / FONTE / TIPO / <sha16>-<id-nativo>-<nome>
```

**Repare no que não está no endereço: a corrida.** É deliberado e está certo — o endereço é
do conteúdo, não da vez em que o vimos. É essa escolha que torna possível *uma cópia, N
observações*, e é também ela que colide com a chave da tabela, como a secção D mostra.

⚠️ **Medido de passagem, e registado para outra missão:** a observação italiana não declara
país, e por isso o objeto canónico dela cai em `XX/it-t2-002/DOCUMENT/…` e não em `IT/…`. O
adapter não inventa o país, o que está certo; ninguém o declara, o que não está. Não é
pergunta do B3.

---

## B · QUEM É O DONO DOS BYTES

```
CANONICAL_RAW_PERSISTENCE_OWNER = guarda/preservar_coleta.py
```

Provado contra o código: `provas/o_encanamento_tem_uma_porta.py` fecha
`P11_um_so_caminho_de_producao_chama_o_raw` e `P3_nenhum_coletor_preserva_por_fora`, e as
duas passam hoje.

O coletor adquire os bytes e precisa de os segurar antes da porta — não há como não segurar,
porque a lei desta casa é preservar antes de interpretar. Mas segurar não é possuir:

```
COLLECTOR_ACQUIRES_BYTES  ≠  COLLECTOR_OWNS_CANONICAL_RAW
```

Quem adquire tem os bytes por um instante. Quem é dono responde por eles para sempre. São
responsabilidades de durações diferentes, e confundi-las é como chamar de proprietário quem
segurou a chave enquanto o dono estacionava.

---

## C · A CLASSIFICAÇÃO

```
ITALY_COLLECTION_STORE_CURRENT_CLASS  =  SECONDARY_ARCHIVE
ITALY_COLLECTION_STORE_TARGET_CLASS   =  ACQUISITION_LANDING
```

Ele **nasceu** como landing: o coletor grava ali antes de qualquer parse. Virou arquivo por
omissão, e a omissão tem nome: **ninguém escreveu o fim da vida dele.** É versionado no Git,
nunca é limpo, e — desde o B1 — guarda os mesmos bytes que o armazém canónico guarda.

Medido, para o mesmo conteúdo, depois de a preservação canónica fechar:

```
conteúdo único                     1
cópias físicas do mesmo conteúdo   2
   XX/it-t2-002/DOCUMENT/b65bfc29c9dba0c5-b65bfc29c9dba0c5-agro_01.pdf
   data/collection-store/italy/IT-T2-002/ARPAV_Z01/v1_x/agro_01.pdf
linhas em raw_asset                1
```

```
SECOND_CANONICAL_RAW_ARCHIVE_ALLOWED = NO
```

Não há explicação comprovável para o contrário. Dois arquivos permanentes do mesmo conceito
divergem — não *podem* divergir, **divergem**, porque nada os obriga a concordar. E no dia
em que divergirem, ninguém sabe qual está certo: é o problema de duas verdades no mesmo
endereço, um andar acima.

---

## D · O CONFLITO DE IDENTIDADE, MEDIDO

O dono do RAW compara, ao reencontrar o mesmo `storage_path`:

```python
IDENTIDADE_DO_OBJETO = ("run_id", "sha256", "bytes", "captured_at", "source_url")
```

E a tabela declara, na migration 001:

```sql
storage_path   text not null unique
run_id         text not null references public.collection_run(run_id)
```

O endereço não carrega a corrida; a **linha** carrega. Logo o mesmo conteúdo, na corrida
seguinte, cai no mesmo endereço com outro `run_id`. Medido, com `MemoriaDescartavel`:

| cenário | `RUN_STATE` | `REUSED_METADATA` | `CONFLITOS_DE_OBJETO` | `collection_run` gravada |
|---|---|---|---|---|
| retry — mesma corrida, mesmos bytes | `COMPLETE` | 1 | 0 | sim |
| nova corrida, mesmos bytes, mesmo `captured_at` | `PARTIAL` | 0 | 1 · `run_id` | **não** |
| nova corrida, mesmos bytes, `captured_at` do dia seguinte | `PARTIAL` | 0 | 1 · `run_id`, `captured_at` | **não** |

```
CURRENT_STORAGE_MODEL_SUPPORTS 1 STORAGE OBJECT → N OBSERVATIONS  =  NO
```

O retry funciona exatamente como a C-PLAN-0 decidiu. A **segunda corrida** é que não tem
como ser representada: ela não é um retry, é uma observação nova do mesmo conteúdo, e o
modelo atual só tem lugar para uma.

**Não corrigido nesta missão.**

---

## E · O QUE O TESTE DO B1 PROVAVA

```
TEST_18_PROVES_REUSE = NO
```

Ele afirma duas coisas, e as duas continuam verdadeiras enquanto a segunda corrida é
inteiramente recusada:

```python
self.assertEqual(entrada["PRESERVADOS"], 4)          # aceites NA PORTA, não linhas no banco
self.assertEqual(self.banco.contar("raw_asset"), antes)
```

Sonda no cenário exato dele:

```
PRESERVADOS na 2ª corrida : 4        ← o teste exige 4, e tem 4
raw_asset antes / depois  : 4 / 4    ← o teste exige iguais, e são iguais
RUN_STATE 1ª corrida      : COMPLETE
RUN_STATE 2ª corrida      : PARTIAL  ← o teste não olha
collection_run da 2ª      : False    ← o teste não olha
linhas da 2ª corrida      : 0        ← o teste não olha
```

`PRESERVADOS` conta o que a **porta** aceitou, não o que o **banco** gravou. Duas perguntas
com nomes parecidos, e o teste respondia à mais fácil.

> **Um teste que só conta não prova reuso. Ele prova que o número não mudou —
> e um número que não muda pode ser saúde ou pode ser paralisia.**

O conserto do teste é trabalho de quem implementar esta política, e o critério fica escrito
aqui: quem afirmar `REUSED` tem de ler `RUN_STATE`, `REUSED_METADATA` e
`CONFLITOS_DE_OBJETO`, e não a contagem.

---

## F · SEEN_AGAIN — A POLÍTICA ESCOLHIDA

A pergunta: se o landing deixar de ser permanente, como é que uma reobservação chega à porta
sem perder o acesso aos bytes?

O que a observação **já** traz hoje, medido: `SOURCE_ID`, `SOURCE_URL`, `DOCUMENT_ID`,
`DOCUMENT_VERSION_ID`, `RAW_SHA256`, `RUN_ID`, `CAPTURED_AT`, `RESOLVED_STRUCTURED_TARGET` —
e, desde o B1, `RAW_PATH` também nas `SEEN_AGAIN`.

| | A · landing permanente | B · landing temporário + lookup pelo coletor | **C · não retransmitir; a casa referencia o conteúdo canónico** | D · já suportada hoje |
|---|---|---|---|---|
| dono duplicado | **SIM** | **SIM** — o coletor passa a ler o armazém | NÃO | — |
| observação nova preservada | sim | sim | sim | **NÃO** |
| byte duplicado | **SIM, para sempre** | não | não | não |
| proveniência preservada | sim | sim | sim | — |
| exige schema | não | não | **SIM** | — |
| exige callback do RAW para o coletor | não | **SIM** | NÃO | — |

```
SEEN_AGAIN_TARGET_POLICY = C
```

**A** é o que temos, e é o segundo arquivo que a regra proíbe. **B** inverte a dependência:
o coletor passaria a precisar de ler o armazém canónico, e quem adquire volta a mandar em
quem guarda. **D** não existe: a porta, hoje, quando não encontra o ficheiro, preserva o
JSON da observação **como se fossem os bytes do documento**, e não diz que o fez.

**C** é a única que mantém cada dono no seu lugar. A observação chega declarando o conteúdo
pelo `RAW_SHA256`; o dono do RAW reconhece que aquele conteúdo já é canónico e **regista uma
observação nova apontando para o mesmo objeto**, sem reenviar um byte. O coletor não sabe
onde o armazém guarda, e continua sem precisar de saber.

```
NEW_RUN_SAME_CONTENT_TARGET_BEHAVIOR
    NEW OBSERVATION  ·  SAME CONTENT  ·  SAME STORAGE OBJECT
```

---

## G · A VIDA DO LANDING

```
NASCE          quando o coletor traz os bytes, ANTES de qualquer parse
QUEM ESCREVE   o coletor, e só ele
QUEM PODE LER  o coletor (para a própria reobservação) e a porta (para entregar ao dono)
               ninguém cita o landing como endereço de registo
DEIXA DE SER   quando a preservação canónica daquele conteúdo fechou COM PROVA
NECESSÁRIO
SEGURO REMOVER só depois de CANONICAL_BYTES_EXIST + CANONICAL_SHA_MATCH
               + a observação daquela corrida reconciliada na memória canónica
QUEM PROVA     o dono do RAW, relendo do armazém e refazendo o hash —
               `conferir_os_bytes()` já faz exatamente isto
```

```
LANDING_CAN_BE_REMOVED_BEFORE_CANONICAL_SHA_MATCH = NO
NUNCA APAGAR A ÚNICA CÓPIA DOS BYTES.
```

A terceira condição não é zelo a mais, é consequência direta da secção D: hoje uma corrida
em `METADATA_CONFLICT` não grava linha nenhuma. Apagar o landing depois de conferir só os
bytes deixaria a casa com o conteúdo guardado e **sem nenhuma observação daquela corrida** —
e sem o landing para reconstruir. Se a preservação canónica falhar, o landing fica, e a
corrida **não pode fingir `COMPLETE`**.

**Nenhuma limpeza é implementada nesta missão.** Aqui só se escreveu a lei.

---

## H · O QUE O BANCO VAI TER DE MUDAR

```
RAW_ASSET_CURRENT_GRAIN  =  o OBJETO DE STORAGE e a OBSERVAÇÃO, na mesma linha
RAW_ASSET_TARGET_GRAIN   =  a OBSERVAÇÃO

STORAGE_OBJECT_CURRENT_OWNER  =  raw_asset (pela unicidade de `storage_path`)
STORAGE_OBJECT_TARGET_OWNER   =  uma espécie própria, separada da observação
```

`storage_path unique` diz que a linha é um objeto de storage. `run_id not null` e
`captured_at` dizem que a linha é uma observação. **Uma linha, dois grãos** — e por isso a
segunda observação do mesmo conteúdo não cabe.

```
B3_REQUIRES_SCHEMA_CHANGE_LATER = YES
```

Natureza da mudança, e só a natureza:

1. **separar o objeto de storage da observação**, em duas espécies, como a migration 022 já
   fez para `RAW` e `DERIVED` — o precedente existe e a frase dele serve aqui: uma tabela
   que se chama bruto com filhos lá dentro mente para todo leitor futuro;
2. o **objeto de storage** identifica-se pelo endereço do conteúdo, e não conhece corrida
   nem hora de captura;
3. a **observação** identifica-se por um surrogate estável (`RAW_OBSERVATION_ID`, fechado na
   C-PLAN-0), carrega `RUN_ID`, `CAPTURED_AT` e `SOURCE_URL`, aponta para o objeto, e é
   idempotente por `(RUN_ID, SOURCE_ID, DOCUMENT_KEY, CONTENT_SHA256)`;
4. a unicidade sai de `storage_path` sozinho e passa a viver nos dois sítios certos: uma
   por objeto, outra por observação.

**Sem DDL. Sem número de migration. Sem implementação.**

---

## I · HISTÓRICO NÃO É FORWARD

```
HISTORICAL_POLICY
    as 144 observações do livro, os 10 objetos nesta árvore, os 25 em `C:/…` e
    os 195 objetos italianos do Storage:
        NÃO apagar · NÃO mover · NÃO migrar · NÃO fabricar corrida
    o livro é congelado como está, e continua a ser a única memória de que
    aquelas coletas aconteceram.
    ⚠️ Não afirmo relação entre `data/collection-store/italy/` e os 195 objetos
    `IT/adama-website/…`: são convenções de chave diferentes e aquisições
    diferentes, e não medi igualdade de artefato, caminho nem hash. Sem medida,
    sem afirmação.

FORWARD_POLICY
    UM arquivo canónico, que é o do dono do RAW.
    O store italiano vira landing, com fim de vida escrito.
    SEEN_AGAIN referencia o conteúdo já canónico; não reenvia byte.
    Uma cópia por conteúdo. N observações por cópia.
    Nada disto vale para o que já aconteceu.
```

---

## J · O QUE FICA DECIDIDO, EM UMA TELA

```
onde o byte NASCE        no coletor, no landing, antes de qualquer parse
onde ele pode ESPERAR    no landing, até a preservação canónica fechar com prova
onde ele fica PARA SEMPRE no armazém canónico, e em mais lado nenhum
quem é o DONO            guarda/preservar_coleta.py
como SEEN_AGAIN funciona  observação nova, mesmo conteúdo, mesmo objeto de storage
2 observações → 1 conteúdo  separando o grão do objeto do grão da observação
por que contagem == reuso  NÃO É: contagem igual também é escrita impedida,
                           e a medição da secção D mostra qual das duas
```

**Não implementado. Não iniciado o B4.**
