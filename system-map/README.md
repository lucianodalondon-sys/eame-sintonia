# SINTONIA SYSTEM MAP

O mapa navegável da arquitetura real do SINTONIA EAME.

**A lei está em [`../AGENTS.md`](../AGENTS.md).** Este ficheiro explica como a
coisa funciona por dentro.

---

## PARA QUE SERVE

Para entender o sistema **sem saber programar**. Passando o rato numa peça,
aparece o que ela faz, por que existe, de onde recebe, para onde envia, o status
e o motivo do status — em português comum. Clicando, abre o detalhe todo: os
ficheiros reais, as ligações com a linha de código que as prova, os
departamentos atendidos e a fonte de cada declaração.

É um instrumento permanente de arquitetura e auditoria. Não é documentação
decorativa, e não é uma segunda verdade: se ele e o repositório discordarem,
quem está errado é ele, e o CI reprova.

---

## OS COMANDOS

```bash
py system-map/scripts/generate_system_map.py    # regerar (scan + estado + build)
py system-map/scripts/validate_system_map.py    # validar (13 provas, falha fechado)
py system-map/tests/test_system_map.py          # provar que as regras não afrouxaram
py system-map/scripts/scan_repo.py              # só medir o repositório
```

Em Linux e no CI, `python3` em vez de `py`. Sem dependências: só biblioteca
padrão, de propósito — um mapa de arquitetura que precisa de pacote de terceiro
para ser gerado tem uma dependência que ele próprio não consegue explicar.

Para ver localmente (o `fetch` do estado precisa de um servidor, não de
`file://`):

```bash
python3 -m http.server -d italia-portale/client 8080
```

e abra `http://localhost:8080/system-map/`.

---

## AS PEÇAS

```
system-map/
  README.md                        este ficheiro
  app/                             a TELA — só renderiza, não sabe nada
    index.html  map.js  map.css     (a casca do protótipo aprovado, sem factos dentro)
  data/
    architecture.declared.json     o que o HUMANO declara (nome, frase, departamento)
    architecture.generated.json    o que a MÁQUINA mede (ficheiros, imports, chamadas)
    state.generated.json           o resultado: peças, ligações, status  ← a tela lê isto
  scripts/
    scan_repo.py                   lê o repositório e devolve factos
    generate_system_map.py         junta medido + declarado, calcula status, publica a app
    validate_system_map.py         o dente da lei — roda no CI
  tests/
    test_system_map.py             provas das regras do mapa
```

O resultado publicável é copiado para `italia-portale/client/system-map/`, que
é o que a Vercel serve (`vercel.json` → `outputDirectory`). Essa pasta é
**derivada**: não se edita lá, edita-se em `app/` e regera-se.

---

## A SEPARAÇÃO QUE SUSTENTA TUDO

```
architecture.generated.json     MEDIDO    ficheiro, import, chamada, workflow, artefato, SHA
architecture.declared.json      DECLARADO nome, o que faz, por que existe, departamento
```

**Declaração não promove a verde.** Um humano pode escrever que A alimenta B; se
o scanner não achou linha nenhuma que prove, a ligação aparece a tracejado, em
cinza, com `⚪ NÃO SEI` escrito. O contrário também vale: o scanner pode achar um
import que ninguém declarou, e ele entra no mapa na mesma — porque é um facto.

Relação **técnica** e relação de **negócio** vivem em listas separadas.
`A importa B` e `A serve o Comercial` são factos de naturezas diferentes, e
misturá-los faz o segundo herdar a credibilidade do primeiro sem a merecer.
Departamento só entra com `source`, `reason` e `declared_by` — nunca inferido
do nome do ficheiro.

---

## COMO O STATUS NASCE

Não há escolha; há regra, e ela é diferente por tipo de peça (`prova_do_tipo()`
no gerador), porque exigir de um teste a mesma prova que de um artefato seria
exigir o impossível de um deles.

| | | |
|---|---|---|
| 🟢 | `PROVEN` | a prova própria do tipo passou, e a descrição humana ainda vale |
| 🟡 | `PENDING` | existe e está ligada, mas falta a prova do tipo — ou mudou depois da última leitura humana |
| 🔴 | `BROKEN` | declarada no mapa e ausente do repositório |
| ⚪ | `UNKNOWN` | **NÃO SEI** — existe, e nada aponta para ela nem ela aponta para nada |

**Verde nunca significa "o ficheiro existe".**

### O carimbo — por que o verde não envelhece

`DECLARED_BLOBS` guarda o SHA de cada ficheiro no momento em que uma pessoa leu
e declarou aquela peça. Quando o ficheiro muda, a descrição humana passa a estar
**potencialmente desatualizada** e a peça cai sozinha para 🟡, dizendo qual
ficheiro mudou. Volta a 🟢 quando alguém relê e recarimba:

```bash
py system-map/scripts/generate_system_map.py --stamp
```

Recarimbar sem reler é o único jeito de mentir neste sistema.

---

## AS TRÊS PARTES

O mapa lê-se em três palavras, da esquerda para a direita:

```
COLETA  →  INTELIGÊNCIA  →  ENTREGA
```

Cada parte é uma faixa colorida, e dentro dela ficam os blocos com o detalhe.
De longe vê-se a história inteira; aproximando, vê-se onde exatamente na história
cada peça está.

**COLETA** · 13 peças — Trazer para dentro o que existe la fora. Nada no SINTONIA comeca sem passar por aqui.

- `FONTES, COLETA E GUARDA` · 13 peças — De onde o dado entra, quem dispara a coleta e onde ele fica guardado entre uma corrida e outra

**INTELIGENCIA** · 27 peças — Transformar dado bruto em caso com dono, lugar e momento — e provar que a transformacao esta certa.

- `LINHAGENS E DONOS` · 4 peças — Qual branch decide, qual consome e qual pacote e o canonico. A inteligencia tem UM dono
- `REGUAS E LEIS` · 6 peças — As leis que decidem o que conta como verdade: procedencia, lugar do fato, tempo, relevancia, voz
- `MOTOR — CADEIA V2.1` · 8 peças — Onde o dado bruto vira caso. A ordem e lei, nao convencao
- `PROVAS E MEDICAO` · 9 peças — O que separa 'esta escrito' de 'esta provado'. Guarda as tres familias, e vive aqui porque provar e como o sistema sabe o que sabe

**ENTREGA** · 15 peças — Levar o que foi decidido ate quem precisa dele, sem deixar passar o que esta errado.

- `PACOTE CANONICO` · 3 peças — O artefato fechado que sai daqui. Derivado e reproduzivel — nunca dono da lei
- `FRONTEIRA E PORTOES` · 7 peças — O unico ponto por onde o pacote atravessa para a tela, e tudo o que impede coisa errada de atravessar
- `SUPERFICIES` · 5 peças — O que o cliente e a reuniao realmente veem. Apresenta decisao ja tomada; nao recalcula nada

**Toda zona pertence a uma das três.** Não há bloco a flutuar fora da história:
o validador reprova zona sem família (`P2_ZONA_TEM_FAMILIA`) e peça cuja família
não seja a da sua zona.

### A cor diz o assunto; a pastilha diz se funciona

| | |
|---|---|
| **família** (faixa e topo do bloco) | azul COLETA · verde INTELIGÊNCIA · laranja ENTREGA |
| **estado** (pastilha no cartão) | 🟢 provado · 🟡 pendência · 🔴 quebrado · ⚪ NÃO SEI |

As três cores vêm do BrandWell (Disease Control, ADAMA Green, Crop Enhancement)
porque são as cores da casa e distinguem-se bem — mas neste mapa carregam o
significado do **processo**, não de categoria de produto. Está escrito no topo de
`app/map.css` para ninguém ler um bloco azul e pensar "fungicida".

**LINHAGENS E DONOS** é a única zona que não é código. As peças dela são factos
sobre *quem manda*, e por isso cada uma declara em `proof` de onde vem a prova:

| `proof` | de onde vem |
|---|---|
| `document` | `italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json` — o repositório declarando por escrito qual é a linhagem geradora, o commit dela e o `BUILD_ID` esperado |
| `git-measurement` | o `git` desta árvore: branch e HEAD de quem está a consumir |

Um facto sobre quem manda não é importado por ninguém — exigir-lhe um `import`
seria exigir a prova errada. Mas *nenhum* tipo de prova é "eu sei": o validador
recusa peça de linhagem que não nomeie um dos dois (`P6_LINHAGEM_DIZ_A_PROVA`).

---

## DETERMINISMO

Mesma árvore + mesmo HEAD = **byte a byte** o mesmo ficheiro. Por isso
`GENERATED_AT` é a data do **commit**, nunca `datetime.now()`: um relógio dentro
do artefato faria o CI acusar drift a cada minuto, e a lei perderia os dentes
numa semana.

---

## O DESIGN SYSTEM

A tela carrega os tokens oficiais do ADAMA Design System de
`italia-portale/client/_ds/adama-brandwell/`. Nenhuma cor de marca é escrita à
mão.

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND   (só para a rampa de STATUS)
NEW_PATTERN_REQUIRED = YES
```

**Motivo:** o BrandWell não tem cor de erro. Tem quatro cores de *categoria de
produto* (laranja, verde, azul, roxo) e nenhuma delas significa "quebrado".
Pintar peça quebrada de roxo Pest Control daria a uma cor de marca um segundo
significado, e a partir daí nenhuma das duas leituras seria confiável. Por isso:

```
ZONA    → cor de marca ADAMA (--adama no topo corporativo, --earth no alternado)
ESTADO  → rampa própria de engenharia (--ok --warn --bad --unknown), na pastilha
```

Assim a marca continua a dizer *"que assunto é este"* e o estado continua a dizer
*"isto funciona?"*, sem os dois competirem pelo mesmo pixel. O único valor fora
do BrandWell é o vermelho de erro (`--bad: #c53b35`), no topo de `app/map.css`.

---

## MUDAR PELO MAPA — AINDA NÃO

A tela é **leitura**. Clicar nela não altera código. A arquitetura já está
preparada para um "solicitar alteração" futuro, mas a ordem nunca muda:

```
agente → implementação no repo → testes → commit → CI → mapa regenerado
```

Nunca `browser → desenha seta → vira verdade`.

---

## O QUE O MAPA NÃO COBRE

`state.generated.json` diz na cara, em `UNCLAIMED_FILES_COUNT`: os ficheiros de
**dado**, documento e evidência que nenhuma peça reivindica. É de propósito —
o mapa é da arquitetura, não do acervo. O que ele **exige** cobrir é o código:
`scripts/`, `italia-portale/audit/`, `tests/`, `system-map/`. Um ficheiro de
código sem peça no mapa reprova o CI (`P9_CODIGO_DECLARADO`).
