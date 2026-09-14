# SEÇÃO PARA O KNOW-HOW CANÔNICO — TAXONOMIA T1–T12

> **Este ficheiro é a seção escrita em forma final**, pronta a entrar em
> `SINTONIA-EAME-KNOW-HOW.md`. Não é um resumo nem um delta a traduzir: é o
> texto, na voz do know-how, com o número de seção deixado em branco de
> propósito — leia o porquê em **POR QUE O NÚMERO ESTÁ EM BRANCO**, mais abaixo.
>
> **Origem:** missão `TAXONOMIA-T1-T12`, branch
> `claude/italy-agricultural-sources-discovery-dfba81`, base `08e590a7`,
> 2026-09-14.

---

## POR QUE O NÚMERO ESTÁ EM BRANCO

A missão mandava atualizar o know-how canônico e **não** deixar um delta como
substituto. Fui aplicar, e medi primeiro. O que encontrei impede a aplicação
segura, e isto é achado, não desculpa:

```
SINTONIA-EAME-KNOW-HOW.md existe em 20 branches.
Nenhuma delas é a branch-base dos PRs (claude/sintonia-eame-repo-setup-xccfob).
Não existe `main` neste repositório.
```

Pior: as cinco cabeças mais recentes são **todas de 2026-09-14** e cada uma
declara uma "última atualização material" diferente:

| branch | última seção que ela declara |
|---|---|
| `claude/sintonia-local-runner-514cdc` *(local, não enviada)* | **§117** — promover é uma edição em vários sítios |
| `origin/claude/control-plane-intelligence-night-v2` | **§117** — a mesma |
| `origin/claude/italy-source-isolation-jb6wed` | **§118** — conhecer uma fonte e autorizar uma fonte |
| `origin/claude/intelligence-object-model-v1` | **§118** — um mundo fechado torna invisível apagar |
| `origin/claude/intelligence-system-map-audit-v1` | **§119** — um mapa que mostra a máquina e esconde… |
| `origin/claude/intelligence-pilot-v1` | **§120** — a Collection mediu certo contra a foto |

**§118 já está ocupado por duas seções diferentes.** Escrever a minha em
qualquer uma das cabeças criaria a sexta bifurcação, e escolher uma delas seria
exatamente o erro que esta missão veio desfazer: eleger uma verdade por ela
parecer melhor, sem prova de que é a oficial.

Então o número fica em branco, e a aplicação é uma decisão de gente:

```
COMO APLICAR — três passos, nenhum automático
  1 · decidir qual cabeça do know-how é a canônica (isso é decisão do Luciano,
      e é uma missão própria: reconciliar 20 cópias)
  2 · dar a esta seção o próximo número livre NESSA cabeça
  3 · atualizar a linha «Última atualização material» do cabeçalho dela
```

⚠️ **O mesmo defeito que esta seção descreve está a acontecer com o próprio
know-how.** A taxonomia tinha duas listas; o know-how tem vinte cópias e cinco
cabeças. A diferença é que a taxonomia agora tem dono, e o know-how não.

---

## § — UM CÓDIGO T, DOIS SIGNIFICADOS: O ROTULO MENTIU, A IDENTIDADE NÃO

### O QUÊ

Entre **07/09/2026 e 14/09/2026**, `T5` significou duas coisas ao mesmo tempo
nesta casa:

```
docs/fontes/ATLAS-DE-FONTES-EAME.md   T5 = SCIENCE
pedido/pedido.py                      T5 = "Preco e mercado"
system-map/scripts/scan_sources.py    T5 = "Preco e mercado"
```

Não era um código. Eram **seis de doze**:

| código | no atlas (lei) | na deriva (código) |
|---|---|---|
| `T5` | SCIENCE | Preço e mercado |
| `T6` | RESEARCHERS | Comércio e distribuição |
| `T7` | TECHNICAL NETWORK | Ciência e ensaio |
| `T10` | MARKET / TRADE / INDUSTRY | Política e subsídio |
| `T11` | EVENTS | Solo e água |
| `T12` | POLICY / AGRICULTURAL ENVIRONMENT | Substância ativa |
| `T13` | DISTRIBUTION *(ocupante, sem definição)* | Outro |

`T1`, `T2`, `T3`, `T4`, `T8` e `T9` diziam a mesma coisa nas duas. Foi isso que
tornou a divergência invisível: metade concordava.

### O EFEITO, MEDIDO NUM PEDIDO

```
«colete materiais de pesquisadores»  ->  T7
T7 no atlas  =  TECHNICAL NETWORK  =  agrónomos, consultores, cooperativas
```

O pedido pedia **pesquisador** e mandava buscar **consultor**. Sem erro nenhum
a aparecer: o código resolvia, o executor corria, o manifesto gravava. Uma
corrida real ficou assim gravada — `XX-T7-2026-09-07-193646`, actor
`coleta/corpus_pesquisador.py`, a buscar OpenAlex e ORCID, que é `T5`/`T6`.

E o artefato que o mapa publica dizia, em `docs/fontes/INDICE-DE-FONTES.md`:

```
EU-T10-001 | Agri-food Data Portal (cereal prices) | T10 · Politica e subsidio
ES-T5-002  | OpenAlex, recorte espanhol            | T5  · Preco e mercado
EU-T12-001 | CELLAR — camada de política agrícola   | T12 · Substancia ativa
```

Três rótulos, três mentiras — e cada uma delas legível por qualquer pessoa que
abrisse o índice.

### POR QUÊ — a parte que vale guardar

O `pedido/pedido.py` trazia este comentário, escrito por cima da lista errada:

> *«NAO E UMA LISTA INVENTADA. Sao os territorios que o atlas de fontes ja usa…
> Inventar aqui uma segunda lista de assuntos criaria duas verdades sobre a
> mesma pergunta.»*

Dizia, e não eram. O `scan_sources.py` fazia o mesmo de outra maneira: a linha
49 declara `ATLAS = "docs/fontes/ATLAS-DE-FONTES-EAME.md"` — ele **lê** o atlas —
e três linhas abaixo guardava a sua própria tabela de nomes, contraditória.

```
UM FICHEIRO QUE SE DECLARA FIEL A UMA LEI E A CONTRADIZ É PIOR
DO QUE UM QUE INVENTA A SUA: QUEM LÊ ACREDITA NELE.
```

Nenhum dos dois se apresentava como taxonomia nova. Logo eram **deriva, não
revisão** — e foi esse o argumento que decidiu quem manda, não a data do
commit. A deriva era **mais recente** que o atlas (07/09 contra 28/08). Se o
critério fosse "o código mais novo ganha", a casa teria adotado a lista errada.

### A PROVA DE QUE O ATLAS É QUE MANDA

Quatro degraus, nenhum por argumento de autoridade:

1. `AGENTS.md` (354-361) põe o atlas como a morada de uma fonte **REGISTADA** —
   é lá que a ficha nasce, e a ficha traz o campo `TERRITORY`.
2. O atlas é o único sítio que dá a cada código um **nome e um escopo**, e o
   único que declara a convenção de `SOURCE_ID`: `T1..T12`.
3. Os dois ficheiros divergentes **apontam para o atlas** no próprio comentário.
4. Os `SOURCE_ID` já emitidos foram cunhados com o significado do atlas. Medido
   ficha a ficha, não por amostragem:

```
EU-T10-001  Agri-food Data Portal, preços de cereais     -> MERCADO       T10 ✓
ES-T7-001..027  imprensa técnica e associações agrárias   -> REDE TÉCNICA  T7  ✓
IT-T11-001 feira EIMA · FR-T11-001 Vinitech-SIFEL         -> EVENTOS       T11 ✓
EU-T12-001  CELLAR, camada de política agrícola           -> POLÍTICA      T12 ✓
EU-T5-001 / ES-T5-002  OpenAlex                           -> CIÊNCIA       T5  ✓
```

```
O ROTULO ESTAVA ERRADO. A IDENTIDADE, NÃO.
NENHUM SOURCE_ID PRECISOU MUDAR — E NENHUM MUDOU.
```

Essa foi a medição que tornou a correção segura. Sem ela, a arrumação da lista
teria parecido exigir renomear identidades — e `SOURCE_ID` não se recicla.

### SUBSTÂNCIA ATIVA NÃO É UM TERRITÓRIO

A deriva tinha `T12 = "Substância ativa"`. O atlas põe substância ativa **dentro
de T4**, e escreve a separação obrigatória:

> *EU ACTIVE SUBSTANCE* e *NATIONAL PRODUCT AUTHORIZATION* são camadas distintas
> de T4 e não podem ser misturadas.

Uma substância aprovada na UE não implica produto autorizado em Itália. Promover
a camada a território apagava essa separação — e `T12` é POLÍTICA.

O mesmo vale para `T11`: a deriva chamava-o "Solo e água". No atlas, solo e água
são parte de **T2** (`CLIMATE / WATER / SOIL`), e `T11` é EVENTS.

### T13 — O OCUPANTE QUE O ATLAS CONTRADIZ

O atlas contradiz-se, e a contradição é real:

- o cabeçalho diz **"OS 12 TERRITÓRIOS"**;
- a convenção de `SOURCE_ID` diz **`T1..T12`**;
- e o **corpo** do atlas tem a secção `### T13 · DISTRIBUTION — FRANCE`, com
  ficha completa e evidência guardada para `FR-T13-001`, mais `ES-T13-001` e
  `IT-T13-001` em `NÃO SEI`.

Decisão tomada, e o motivo:

```
T13 fica como OCUPANTE SEM DEFINIÇÃO NA LISTA.
  · não é território canônico  ->  valido("T13") é False
  · não se pede               ->  um pedido com T13 é recusado com o motivo
  · não se apaga              ->  os três SOURCE_ID continuam intactos
  · o mapa sabe NOMEÁ-LO      ->  "DISTRIBUTION (ocupante legado, fora dos 12)"
```

Nomear não é canonizar. E a deriva chamava T13 de "Outro", que é outra coisa
ainda — por isso "outro" deixou de ser um alvo aceitável.

Migrar `FR-T13-001` exigiria quebrar a convenção de `SOURCE_ID` do próprio atlas
e mexer em três ficheiros de teste que travam a contagem
(`tests/test_handoff.py:112` · `assert SOURCE_ID_COUNT == 37`). É missão própria,
com dono de decisão.

### O CONSERTO — UMA LISTA, UM DONO, E O DONO É UM DOCUMENTO

```
docs/fontes/ATLAS-DE-FONTES-EAME.md · secção "OS 12 TERRITÓRIOS"   <- O DONO
        ^
        | lê a tabela, não guarda cópia
        |
   _territorios.py                                                <- o dono em código
        ^          ^              ^
        |          |              |
  pedido.py   scan_sources.py   os geradores de planilha
```

`_territorios.py` vive na **raiz**, pelo mesmo motivo e com o mesmo desenho de
`_gavetas.py` — que `AGENTS.md` já cita como precedente: *«`_gavetas.py` é o
único sítio com a lista das gavetas. O scanner do mapa lê-a de lá. Duas listas
seriam duas verdades.»*

Três decisões de desenho que valem repetir noutro lado:

1. **Ele não guarda a lista, lê-a.** Guardar uma cópia certa hoje é guardar uma
   cópia errada no dia em que o atlas mudar e ninguém se lembrar do ficheiro.
2. **Se o atlas não puder ser lido, ele levanta.** Não devolve cópia de
   emergência: cópia de emergência é exatamente como nasce a segunda verdade.
3. **Palavra ambígua avisa, não escolhe calada.** "produção" está no escopo de
   T1 e de T10, e o atlas escreve as duas; o pedido resolve para a primeira e
   devolve o aviso. Escolher em silêncio seria repetir o erro em pequeno.

### O QUE NÃO SE MEXEU, E POR QUÊ

```
SOURCE_ID       nenhum renomeado — identidade emitida não se recicla
RUN_ID          nenhum renomeado — é proveniência
relatório antigo  nenhum reescrito — log é história, e reescrevê-lo apagaria a
                  prova de que a deriva existiu
```

Uma corrida gravada ficou com significado errado —
`XX-T7-2026-09-07-193646`, `MISSION: "Ciencia e ensaio"`, alvo `T7`. Fica
**intacta e fixada num teste**, com o risco residual escrito: quem filtrar
"corridas de T7" esperando REDE TÉCNICA vai apanhar esta corrida de ciência. O
campo `MISSION` é o que torna a intenção recuperável.

### A PROVA — 26 testes, e um deles não confia na implementação

`tests/test_territorios.py`. O teste que segura a casa é o que **não importa**
`_territorios`: ele tem o seu próprio leitor do atlas, escrito no ficheiro de
teste, e compara os dois resultados. Se alguém puser uma cópia dentro do dono, o
teste reprova.

Mais uma tranca: `ESPERADO_EM_2026_09_14` é uma testemunha congelada dos doze
significados. Se o atlas mudar de verdade, o teste cai e alguém tem de olhar.
**Taxonomia não muda em silêncio.**

Red team: **12 ataques, 12 detectores a funcionar.** Cada ataque muta um
ficheiro real, corre a suíte e restaura. E o harness aprendeu duas lições no
caminho, que valem mais do que os ataques:

```
· um red team com estado sujo acusa inocente e absolve culpado
  (o ataque #6 reportou os testes do #5, e a conclusão errada seria
   «o detector não funciona»; era o harness a medir ficheiro não restaurado)

· um detector que falha FECHADO não produz linha "FAIL:"
  (apagar a secção do atlas faz o módulo levantar no import e a suíte
   nem carrega — o medidor lia isso como «não detetou», ao contrário)
```

E um defeito real no teste, encontrado pelo ataque #1: `git ls-files` sozinho só
lista o que já está no índice, então um ficheiro **novo** com uma segunda lista
passava invisível até ao commit. Passou a `--cached --others
--exclude-standard`. Um defeito que só aparece depois do commit é um defeito que
chega tarde.

### CONSEQUÊNCIA

```
Antes:  T5 significava SCIENCE para o atlas e "Preço e mercado" para o pedido.
Agora:  existe uma interpretação de T1–T12, e ela é a do atlas.
        Quem quiser mudá-la muda o atlas — e 26 testes avisam.
```

Corrigidos **2 ficheiros de código vivo** (`pedido/pedido.py`,
`system-map/scripts/scan_sources.py`), **2 geradores** que guardavam cópia
correta mas cópia, **2 descrições** do System Map — uma delas
(`C-PEDIDO`) era literalmente falsa antes desta correção, e passou a ser
verdadeira sem mudar de sentido.

**0** identidades renomeadas. **0** falhas novas na suíte (37 antes, 37 depois,
iguais por nome). **0** coletas corridas.
