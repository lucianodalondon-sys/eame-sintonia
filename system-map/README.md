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
py system-map/scripts/validate_system_map.py    # validar (15 provas, falha fechado)
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
    sources.generated.json         as fontes, os contratos, as contas e as palavras
    state.generated.json           o resultado: peças, ligações, status  ← a tela lê isto
  scripts/
    scan_repo.py                   lê o repositório e devolve factos
    scan_sources.py                lê o atlas de fontes, os contratos de busca,
                                   as contas públicas e as palavras usadas
    generate_system_map.py         junta medido + declarado, calcula status, publica a app
    validate_system_map.py         o dente da lei — roda no CI
    CADEIA-DO-MAPA.json            a ordem dos passos e o que é publicado
    publicar_no_deploy.mjs         corre no BUILD: regera, valida, e carimba o
                                   commit REALMENTE implantado
    verificar_deploy.py            depois do deploy: o URL público serve esse commit?
  app/
    freshness.js                   a lei de CURRENT · STALE · UNKNOWN · BROKEN
  tests/
    test_system_map.py             provas das regras do mapa
    test_freshness.mjs             provas de que verde exige as quatro provas
```

O resultado publicável é copiado para `italia-portale/client/system-map/`, que
é o que a Vercel serve (`vercel.json` → `outputDirectory`). Essa pasta é
**derivada**: não se edita lá, edita-se em `app/` e regera-se.

---

## O MAPA DIZ SE ESTÁ ATUAL — E NÃO FICA VERDE SEM PROVA

O mapa é a foto de **uma** árvore, e isso está certo. O que faltava era ele
conseguir dizer se aquela árvore é a mais nova da linha. Quatro factos, quatro
origens, e nenhum deriva do outro:

```
GENERATED FROM         state.generated.json → PROVENANCE.HEAD
DEPLOYED COMMIT        deployment.generated.json → DEPLOYED_COMMIT  (nasce no BUILD)
LATEST CANONICAL HEAD  API pública do GitHub, ao vivo
SYSTEM MAP CHECK       o veredito do validador, gravado no build
```

```
GENERATED  !=  DEPLOYED  !=  LATEST REMOTE
MAP VALID  !=  MAP CURRENT
COVERAGE   !=  FRESHNESS
```

`deployment.generated.json` **não se commita** e está no `.gitignore`: um ficheiro
dentro de um commit nunca pode conhecer o SHA desse commit. Se ele não existir no
que é servido, a tela diz `⚪ FRESHNESS UNKNOWN` — nunca verde.

⚠️ **Na Vercel, hoje, o estado é `⚪ UNKNOWN` e isso está certo.** Medido no log
de uma build real: `Removed 1125 ignored files defined in .vercelignore` — o
contentor recebe 311 dos 1338 ficheiros, e regenerar ali daria o mapa de uma
árvore mutilada. O publicador recusa-se a fazê-lo. **STALE continua a funcionar
na mesma**, porque staleness prova-se sozinha. Ver `AGENTS.md`.

**A regra que manda em todas:** ausência de prova de staleness não é prova de
current. A lei está em [`app/freshness.js`](app/freshness.js) e as provas em
[`tests/test_freshness.mjs`](tests/test_freshness.mjs). Os detalhes, incluindo
onde ficaria uma credencial se o repositório deixar de ser público, estão em
[`AGENTS.md`](../AGENTS.md).

---

## O ENDEREÇO

```
https://sintonia-eame-preview.vercel.app/system-map/
```

É este, e não muda. Nem quando há commit novo, nem quando há build nova, nem
quando a linha geradora muda de nome.

Os endereços longos da Vercel — `...-nsmkrrwth-london-creative.vercel.app`,
`...-git-claude-<branch>-...` — são **previews de engenharia**. Continuam a
existir e são úteis: é onde se testa antes de decidir. Não são o produto.

    PREVIEW URL      ≠  USER URL
    DEPLOYMENT URL   ≠  CANONICAL PRODUCT URL
    LATEST DEPLOYMENT ≠ APPROVED DEPLOYMENT

**Nunca entregar um URL de deployment ao dono do produto como se fosse o
endereço.** Qualquer handoff apresenta primeiro o endereço canónico; o URL do
deployment vive na secção técnica, mais abaixo, e não no topo.

O contrato legível por máquina está em
[`CANONICAL-PUBLICATION.json`](CANONICAL-PUBLICATION.json): o host, a rota, quem
é dono da publicação, que branches podem ser candidatas e o que tem de estar
provado antes de o alias mudar.

### Como uma versão nova chega lá

O projecto Vercel serve o **portal inteiro**, e não só o mapa. A branch de
produção é `release/canonical`: o que entra nela vai ao ar sozinho, e nada mais
vai.

```
commit  →  preview da branch de trabalho
        →  PR para release/canonical
        →  PROVENIENCIA · SYSTEM MAP CHECK · PORTAL REGRESSION CHECK
        →  merge
        →  o mesmo endereço de sempre, já com a versão nova
```

Ninguém empurra directamente para `release/canonical`. A conferência corre
**antes do merge** — o último momento em que reprovar ainda serve para alguma
coisa, porque depois do push já está no ar.

O portão está em
[`../.github/workflows/portao-do-release.yml`](../.github/workflows/portao-do-release.yml),
em três jobs separados. Os 73 portões do portal correm lá: enquanto a publicação
era um clique, um humano olhava; automatizar sem eles seria trocar um humano
atento por nada.

    A ROTA RESPONDER NÃO É A PÁGINA ESTAR INTEIRA.

**Falta uma coisa que não é código:** protecção de branch em
`release/canonical`, exigindo os três jobs e proibindo push directo.

    UM PORTÃO QUE SE PODE CONTORNAR É UMA SUGESTÃO.

### Pousar uma versão à mão (rollback, ou recurso)

[`scripts/portao_da_promocao.py`](scripts/portao_da_promocao.py) continua a
existir para quando for preciso trocar a versão sem passar pelo fluxo normal:

```bash
py system-map/scripts/portao_da_promocao.py \
    --candidato https://<deployment>.vercel.app \
    --commit    <sha> \
    --rollback  <id do deployment canónico actual>
```

Ele recusa quando a branch não tem autoridade, quando o commit servido não é o
esperado, quando o mapa servido foi gerado de outra árvore, e — a que custa caro
errar — quando alguma rota do portal piora ou algum recurso que o portal serve
hoje deixa de ser servido. A lista desses recursos não se escreve à mão: lê-se
do canónico servido no momento, por isso actualiza-se sozinha.

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
