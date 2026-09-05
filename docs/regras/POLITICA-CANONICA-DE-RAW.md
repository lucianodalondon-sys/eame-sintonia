# POLÍTICA CANÔNICA DE RAW — SINTONIA EAME

Regra única sobre onde vive o bruto de coleta. Fecha a colisão que bloqueou o
`CANARIO-LINHAGEM-CANONICA-01` e destrava a integração da casa.

**Data:** 2026-09-05 · **Estado:** CANÔNICA · **Escopo:** todo RAW de rota paga e de rota pública.

---

## Por que esta regra existe

Duas linhagens escreveram políticas opostas e deliberadas sobre a mesma coisa:

- uma ignora **só diretórios de bruto**, e avisa que um ignore global *"quebraria as missões 14 e 15 em silêncio"*;
- outra adiciona **exatamente esse ignore global** (`data/samples/**/*.gz`, `data/samples/**/*.raw.json`), porque *"um dos blobs .gz é 17% do pack inteiro"*.

**As duas estão certas sobre o próprio problema.** O pack cresce de forma permanente — medido:
gzip tem ratio 1,00 no pack e zero delta base, então cada versão nova entra pelo tamanho
integral, para sempre. E o bruto é **evidência**: apagá-lo do Git sem um lugar provado para
ele quebra a cadeia de prova que todo o projeto sustenta.

A regra abaixo não escolhe um lado. Ela impõe **ordem**: o bruto só sai do Git quando houver
prova de que chegou noutro lugar.

---

## A · RAW JÁ VERSIONADO — preservar

Os **61 blobs `.gz`** hoje versionados em `data/samples/raw-paid/` (60) e `data/samples/ES-T4-005/` (1)
(idênticos nas duas linhagens, verificado blob a blob — contagem feita com `git ls-files -z`, porque
`git ls-tree` aspa nomes com acento e um `grep` ingênuo devolve 51 em vez de 61):

- **preservar**; não remover;
- **não reescrever história** — o custo de reescrita é maior do que o que resolve;
- **não migrar retroativamente agora**.

## B · RAW PAGO FUTURO — destino preferencial

**OBJECT STORAGE IMUTÁVEL + MANIFESTO VERSIONADO NO GIT.**

O Git guarda o manifesto, nunca o peso. Manifesto mínimo, por objeto:

| campo | o que é |
|---|---|
| `RUN_ID` | execução que produziu o bruto |
| `COLLECTION_ID` | coleta a que pertence |
| `SOURCE_ID` | fonte declarada |
| `CAPTURED_AT` | quando foi capturado do mundo |
| `CONTENT_TYPE` | tipo do conteúdo bruto |
| `STORAGE_URI` | endereço imutável no Storage |
| `BYTES` | tamanho exato |
| `SHA256` | hash do objeto |
| `RAW_STATE` | estado de preservação |

Sem os nove campos, não há manifesto — e sem manifesto, o bruto não pode sair do Git.

## C · REGRA DE TRANSIÇÃO — a que destrava o canário

> **É PROIBIDO adicionar ignore global de `*.gz` ou `*.raw.json` sob `data/samples/`
> enquanto não existir prova de que o Storage funciona.**

O gate exige **os quatro**, provados, não afirmados:

```
STORAGE_UPLOAD   = PASS
STORAGE_READBACK = PASS
SHA256_MATCH     = PASS
MANIFEST_WRITTEN = PASS
```

**Até esse gate existir:** as rotas pagas atuais **permanecem autorizadas a versionar RAW**
nos caminhos que já têm política explícita. O bruto continua no Git porque ainda não há
outro lugar provado — não por preferência.

`STORAGE_MIGRATION_STATE = PENDENTE`

## D · HTML-BRUTO — regra escopada mantida

Os diretórios `data/samples/*-JANELA/html-bruto/` e `*-TRANSCRICOES/audio-cache/`
**continuam ignorados**, como já estavam. Motivo declarado e mantido: o HTML bruto é
evidência escrita no disco da máquina, com o caminho preservado em `RAW_HTML_PATH`; o
áudio é insumo descartável — a transcrição é que é o resultado.

Só um contrato novo e explícito muda isso.

---

## PORTÃO DE COLETA — preservação faz parte da entrega

```
PAID_RAW_PRESERVED = YES   ⟺   UPLOAD_OK ∧ READBACK_OK ∧ HASH_MATCH ∧ MANIFEST_OK
```

Se qualquer um falhar: **`COLLECTION_COMPLETE = NO`**.

> **Nenhuma coleta paga pode ser declarada entregue sem preservação.**
> Gastar dinheiro numa rota e perder o bruto é uma coleta que não aconteceu.

Esta missão fecha a **regra**, não a infraestrutura — mas a infraestrutura **já existe**, e a
medição está registrada na secção E abaixo. A regra acima não muda por causa disso: muda apenas
o que se sabe sobre o terreno.

---

## E · ESTADO MEDIDO DO TERRENO — 2026-09-05

Esta secção **não altera nenhuma regra acima**. Ela registra o que foi medido depois de a
política ter sido escrita, e corrige um pressuposto: o Storage não é hipótese futura.

### E.1 · A infraestrutura já existe

```
projeto Supabase ......... eame-sintonia
Storage .................. bucket privado `raw`
tabelas .................. public.raw_asset · public.collection_run · public.checkpoint_coleta
```

`public.raw_asset` já carrega os campos que o PORTÃO DE COLETA exige:
`run_id`, `storage_path`, `media_type`, `bytes`, `sha256`, `captured_at`, `source_url`,
`preserved`, `not_preserved_reason`.

```
STORAGE_EXISTS = SIM
```

**Consequência prática: não construir um segundo Storage nem um segundo manifesto operacional
antes de provar necessidade.** O dono canônico que a secção anterior dava por inexistente está lá.

### E.2 · Mas o contrato ainda não fecha

```
objetos no bucket `raw` .................................. 738
registros em public.raw_asset ............................ 251
objetos com par provado em raw_asset ..................... 251
objetos de Storage ainda sem par provado em raw_asset .... 487
```

```
RAW_CONTRACT_FULLY_RECONCILED = NÃO
```

**Sobre os 487, o que se pode e o que não se pode dizer.** Pode-se dizer apenas isto: são
objetos que existem no Storage e ainda **não têm par provado** em `raw_asset`. Não foram
medidos como perdidos, nem como novos, nem como inválidos, nem como duplicados — nenhuma
dessas leituras tem prova. A reconciliação item a item ainda não foi feita.

Enquanto `RAW_CONTRACT_FULLY_RECONCILED = NÃO`, a REGRA DE TRANSIÇÃO da secção C continua
integralmente em vigor e `STORAGE_MIGRATION_STATE` permanece **PENDENTE**: nenhum ignore
global de RAW entra, porque não há prova de que exista uma segunda cópia de cada objeto.

### E.3 · Contagem do RAW já versionado — método NUL-safe

```
git ls-files -z 'data/samples/**' | tr '\0' '\n' | grep -c '\.gz$'   ->  61
```

**61 blobs `.gz` versionados**, confirmando a contagem da secção A.

Registrado porque a armadilha é real e já custou uma medição errada nesta casa: `git ls-tree`
**aspa nomes com acento**, e um `grep` ingênuo sobre a sua saída devolve **51** em vez de 61 —
perde exatamente os dez ficheiros de sensores com nomes acentuados (Delmotte, Mercado-Blanco,
Sánchez-Vallet, Carrasco-López, Suffert). Qualquer contagem futura de RAW usa `ls-files -z`.

> **A contagem antiga de 51 não deve ser reintroduzida em documento nenhum.**
