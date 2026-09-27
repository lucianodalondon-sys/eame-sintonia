# DAILY KNOW-HOW — 2026-09-13 — COL-E7 / CONTRATO CANÔNICO DO TEXTO

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável da missão `COL-E7-01`; não cria um segundo KNOW-HOW, não substitui `SINTONIA-EAME-KNOW-HOW.md`, a Bíblia, contratos, código, runtime ou provas executáveis.

## CONTEXTO MEDIDO

```text
REPO = lucianodalondon-sys/eame-sintonia
KNOW_HOW_BRANCH = claude/sintonia-eame-know-how-v1
KNOW_HOW_HEAD_BEFORE = 82790f52d9199482e3ad289e9f133b08f06d4ddc
LAST_MOTHER_SECTION = §106
E7_BRANCH = claude/collection-e7-text-contract-0qk2gr
E7_HEAD = c504ca975076d1c4b848e262d3a5bf61ff6e1654
E7_REPORT = docs/relatorios/COL-E7-01-CONTRATO-DO-TEXTO.md
```

O §104.6 já registra a lei madura de que **passar texto é passar espécie, não só valor**. Este delta não repete essa lei. Registra apenas o que apareceu ao fechar a aresta E7.

## DELTA DURÁVEL — CANDIDATO A §107 NA CONSOLIDAÇÃO DA MÃE

### 1 · ANTES DE INVENTAR VOCABULÁRIO, PROCURAR O DONO NO GIT INTEIRO

O E7 começou com a aparência de que faltava um contrato de espécie textual na Collection. A medição mostrou outra coisa: `regras/proveniencia.py` já governava esse conceito na linha do SCRAP/C6, enquanto a linha da Collection não carregava o bloco correspondente.

```text
LEI AUSENTE != LEI INEXISTENTE.
A LEI PODE ESTAR DO OUTRO LADO DA CERCA.
```

**Por quê:** inventar um novo vocabulário local teria criado dois donos do mesmo conceito e violado `ONE CONCEPT -> ONE OWNER`.

**Consequência:** antes de criar enum, contrato ou owner novo, procurar o conceito no Git inteiro e provar se já existe um dono canônico noutra linhagem.

### 2 · UM TOKEN COM DOIS SIGNIFICADOS É UMA COLISÃO, NÃO UM ACORDO

`CAPTION` era usado com sentidos incompatíveis: em um caminho significava texto escrito pelo autor; em outro, legenda nativa da plataforma.

```text
DOIS SIGNIFICADOS NUM TOKEN NÃO SÃO UM VOCABULÁRIO.
```

**Por quê:** nomes iguais mascaram espécies diferentes e fazem ataques reais parecerem equivalências legítimas.

**Consequência:** quando o mesmo token responde a duas perguntas, separar os conceitos e renomear; não acrescentar exceções ao consumidor.

### 3 · NOME SEM PAR NUM VOCABULÁRIO SIMÉTRICO PODE DENUNCIAR EIXOS COLAPSADOS

A C6 possuía nomes como `NATIVE_CAPTION_ORIGINAL`, `NATIVE_CAPTION_TRANSLATED` e `ASR_LOCAL`. O ASR traduzido não tinha nome possível. Isso revelou que dois eixos estavam comprimidos num valor único.

A forma canônica medida no E7 separa:

```text
TEXT_KIND     = AUTHOR_TEXT | NATIVE_CAPTION | TRANSCRIPT | ASR | PAGE_TEXT | DOCUMENT_TEXT | UNKNOWN
TEXT_RELATION = ORIGINAL | TRANSLATED | UNKNOWN
```

**Por quê:** uma combinação válida que não cabe no vocabulário acaba promovida ao nome "mais parecido" e perde procedência.

**Consequência:** quando combinações legítimas deixam buracos assimétricos, verificar se há mais de um eixo escondido no mesmo enum.

### 4 · INVARIANTE CRÍTICA PRECISA GUARDAR OS DOIS SENTIDOS

A primeira guarda protegia apenas:

```text
UNKNOWN -> NOT_DECLARED
```

mas ainda permitia o inverso perigoso:

```text
NOT_DECLARED -> AUTHOR_TEXT
```

A promoção silenciosa entrava por esse lado.

```text
ESPÉCIE CONHECIDA <-> ALGUÉM A DECLAROU.
```

**Por quê:** uma implicação única protege quem admite não saber, mas não protege quem passa a afirmar sem prova.

**Consequência:** invariantes de identidade/procedência que representam equivalência precisam ser testadas nas duas direções.

### 5 · UMA GUARDA INALCANÇÁVEL É CÓDIGO MORTO, NÃO PROTEÇÃO

Uma guarda contra `INFERRED_FROM_TEXT` estava depois de uma lista fechada que já recusava o valor. Logo, nunca executava.

```text
GUARDA QUE NUNCA CORRE NÃO GUARDA NADA.
```

**Consequência:** além de testar que a regra existe, provar que existe um caminho executável que a alcança. Regra escrita e regra exercida são propriedades diferentes.

### 6 · "O PRIMEIRO DA LISTA" É UMA POLÍTICA IMPLÍCITA

Quando várias unidades de texto chegam e só uma alimenta quem julga, escolher a primeira já é uma regra — apenas não documentada.

O E7 provou a necessidade de seleção explícita e registrável, preservando a preferência por original antes de tradução e escrevendo a razão da escolha no item.

```text
ORDEM ACIDENTAL DE LISTA != POLÍTICA CANÔNICA.
```

**Consequência:** toda seleção entre N candidatos precisa de regra explícita, determinística e observável.

### 7 · CAMPO QUE VIAJA NÃO PASSA A PERTENCER À FICHA

A tentativa de colocar `TEXT_UNITS` numa lista de metadados do artefato confundia trânsito com ownership.

```text
POR ONDE PASSA != DE QUEM É.
```

**Por quê:** a ficha descreve o artefato; o conteúdo viaja pelo item. Mover o campo para a lista errada mudaria a semântica só para facilitar transporte.

**Consequência:** quando um campo precisa atravessar uma fronteira, preservar o owner e ajustar a travessia — não reclassificar o campo por conveniência.

### 8 · A TRAVESSIA COMUM VIVE ONDE TODAS AS ROTAS PASSAM

Uma versão intermediária aplicava a escolha textual em uma função usada pela rota social, mas não pela rota documental. Isso produziria duas Collections semanticamente diferentes na mesma porta.

```text
UMA TRAVESSIA, UM TRADUTOR, NA FRONTEIRA COMUM.
```

**Consequência:** normalizações contratuais compartilhadas devem viver no ponto comum de todas as rotas que entregam ao mesmo consumidor; não em um adapter específico.

## PROVA

No `E7_HEAD = c504ca975076d1c4b848e262d3a5bf61ff6e1654`, o relatório canônico da missão registra:

```text
TEXT_CONTRACT_OWNER_COUNT = 1
E1..E7 = PASS
TEXT_KIND_LOSS = 0
JUDGMENT_CHANGED = NO
174 vereditos reais byte a byte iguais
RED_TEAM = 15 ataques · 0 sobreviventes
MUTATION = 6 eixos · 0 sobreviventes
NEW_FAILURES = 0
SYSTEM_MAP_CHECK = PASS
REAL_NETWORK = 0
PAID_USD = 0
```

A admissão continuou lendo `item['texto']`; o julgamento não foi relaxado para acomodar o novo contrato.

## O QUE NÃO MUDA

Este delta **não** altera a ordem canônica do projeto. Continua válida a decisão já registrada:

```text
FECHAR COLLECTION
-> integrar capacidades de aquisição, incluindo SCRAP
-> provar integração
-> big collection
-> reconciliar/auditar/admitir/popular Sala de Espera
-> Intelligence
-> Intelligence Tools / Validation
-> Portal/Casco
```

Também não declara que o SCRAP já está integrado. O E7 fecha o contrato de texto na branch da missão; integração na linha funcional e a ponte do mapper SCRAP continuam sendo missões separadas e precisam de prova própria.

## RISCO RESTANTE

- o E7 ainda precisa ser integrado sobre o HEAD funcional real da Collection sem perder correções posteriores;
- o mapper do SCRAP ainda precisa atravessar `TEXT_UNITS` pela ponte canônica;
- `PASS` no E7 não prova o E2E do SCRAP até a Sala de Espera;
- qualquer integração deve preservar `UNKNOWN` em vez de promover espécie sem prova.

## FECHAMENTO

1. **O que mudou?** Ficaram registrados os aprendizados duráveis descobertos ao fechar o contrato E7, sem duplicar o §104.6.
2. **Por quê?** São regras reutilizáveis sobre ownership, vocabulário, invariantes, seleção e fronteiras que outras abas podem voltar a enfrentar.
3. **Qual a prova?** `COL-E7-01` no HEAD `c504ca975076d1c4b848e262d3a5bf61ff6e1654`, relatório `docs/relatorios/COL-E7-01-CONTRATO-DO-TEXTO.md` e suas provas/red team/mutações.
4. **O que não mudou?** Bíblia, Admission, SCRAP branch, LIVE, Intelligence e Portal não são alterados por este registro.
5. **O que continua desconhecido?** O HEAD funcional final da Collection após a missão atualmente em andamento e, portanto, o diff real de integração do E7.
6. **Qual risco restou?** Integrar E7 ou SCRAP por atalho e recriar dois owners ou perder espécie/procedência.
7. **Bíblia/contrato precisa mudar?** Não há prova de necessidade neste delta; o contrato E7 já vive no código/provas da missão.
8. **Próximo passo mínimo?** Aguardar o HARD STOP da missão atual da Collection, medir o HEAD real e então integrar E7 antes da ponte SCRAP.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
