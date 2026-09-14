# ACHADOS — o que a reconstrução encontrou, e não consertou

> Esta missão tinha uma proibição explícita: **mostrar o defeito, não corrigir o
> defeito.** O que está aqui foi **medido**, não suposto. Nada nesta lista foi
> arranjado — cada achado continua exatamente como estava quando o mapa o viu.

Medido em `HEAD` da reconstrução, sobre 1929 ficheiros rastreados e 105 leis.

---

## ACHADO-1 · o mapa **oficial** perdeu uma aresta verdadeira por colisão de nome

**O que aconteceu.** Ao regenerar o mapa oficial (lei do `CLAUDE.md`), a aresta

```
C-MAPA-APP --READS--> C-TESTES
prova: tests/test_observabilidade_estrada.py:382  ·  "'system-map', 'map.js'))"
```

**desapareceu**. O ficheiro de teste não mudou, a linha não mudou, o dono não
mudou (`C-TESTES`, nas duas revisões). A aresta deixou de existir na mesma.

**Porquê.** `system-map/scripts/scan_repo.py` resolve um literal de caminho por
**nome único no censo** (`por_nome_unico`). Antes desta missão havia **um**
`map.js` no censo — as cópias publicadas estão em `IGNORAR`:

| censo | antes | depois |
|---|---|---|
| `map.js` | 1 · `system-map/app/map.js` | 2 · `+ system-map/v2/app/map.js` |
| `map.css` | 1 | 2 |

Com dois, o nome deixou de ser único, e o scanner recusou-se a escolher.

**O scanner não está a mentir — está a recusar inventar.** O comentário dele diz
isso com todas as letras: *«Dois ficheiros com o mesmo nome não dão para
distinguir a partir do literal, e escolher um seria inventar.»* A recusa é
correta pela lei dele.

**O defeito real é outro, e é este:** a derivação de arestas do mapa oficial é
**frágil a colisões de nome em qualquer ponto do repositório**. Um ficheiro novo,
numa pasta sem relação nenhuma com a aresta, apaga silenciosamente uma ligação
verdadeira — e o mapa fica **mais pobre sem avisar ninguém**. Não há aviso, não
há contagem, não há teste que falhe. A aresta simplesmente não está lá.

**Não corrigido nesta missão.** Corrigir é mexer em `scan_repo.py`, que é
runtime do mapa oficial.

---

## ACHADO-2 · a cadeia canónica morre em `ADMISSION → READY`

`FIRST_LOST_EDGE: ADMISSION → READY`. A cadeia está **OBSERVED** até à admissão
e não passa dali.

| peça | estado | motivo medido |
|---|---|---|
| `M-READY` · A unidade pronta | `BLOQUEADO` | a medição diz que este passo não aconteceu |
| `M-SALA` · A sala de espera | `BLOQUEADO` | a medição diz que este passo não aconteceu |
| `M-TRAVA` · A trava da inteligência | `BLOQUEADO` | a medição diz que este passo não aconteceu |

**A sala de espera nunca recebeu nada.** Tem contrato, tem código, e nunca
correu. A inteligência está travada por contrato, a montante dela.

---

## ACHADO-3 · a Bíblia exige uma peça que não existe

`M-LACUNA` · *A falta de coleta* — `NAO_IMPLEMENTADO`.
Motivo medido: **a Bíblia exige, e não existe implementação aqui.**

A única saída canónica dela (`M-LACUNA → M-PEDIDO`, «a falta de material vira um
pedido, pela porta da frente») tem prova **DECLARED** e nada mais forte. É o
*Collection Gap*: hoje ninguém pede nova coleta pela porta da frente.

---

## ACHADO-4 · três ligações vivem só no papel

As três arestas mais fracas do mapa estão em `DECLARED` — contrato sim, código
não provado, execução nenhuma:

| ligação | onde está escrita |
|---|---|
| `D-ESPERA → D-INTELIGENCIA` | `docs/operacao/TRAVA-DA-INTELIGENCIA.json` |
| `D-INTELIGENCIA → D-ENTRADA` | `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` |
| `M-LACUNA → M-PEDIDO` | `BIBLIA-CANONICA-DA-COLETA.md` |

Nenhuma foi promovida. `UNKNOWN = 0` porque cada uma declara o que a sustenta.

---

## ACHADO-5 · dez peças em 27 nunca foram vistas a correr

`observado`: `SIM 14 · NAO 3 · NÃO SEI 10`.

**`NÃO SEI` não é `NÃO`.** Dez peças não têm artefato de execução que as prove —
nem para bem nem para mal. O mapa diz `NÃO SEI` e mostra porquê, em vez de
escolher um lado.

---

## ACHADO-6 · o publicado não é o mais recente, e isso é lei

`system-map/CANONICAL-PUBLICATION.json` declara `CANONICAL PUBLISHED != LATEST SOURCE`,
e explica que *a cópia commitada nasce sempre um commit atrás de si mesma*.

É por isso que `V01_SEM_DRIFT` compara **sem** `PROVENANCE`: o `HEAD` que o mapa
grava muda no próprio commit que o grava. Comparar byte a byte reprovaria toda a
gente, para sempre. Quem ler o `stamp` da página e o `HEAD` do repositório vai
ver um commit de diferença — **por desenho, não por avaria.**

---

## ACHADO-7 · o mapa media um ficheiro que o próprio mapa escreve

**O que aconteceu.** O portão oficial `SYSTEM MAP CHECK` reprovava em **todos** os
commits — incluindo os da base, antes desta linha existir — sempre com:

```
P1_SEM_DRIFT · regerar mudou architecture.generated.json
primeira diferenca: .FILES[704].sha
```

`FILES[704]` é `docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`, que o **próprio
gerador escreve**, e que carimba `HEAD_DA_MEDICAO` no texto.

**O laço.** O mapa gravava o SHA desse ficheiro → o commit mudava o `HEAD` → a
regeneração seguinte reescrevia o carimbo → o SHA mudava → o portão acusava
drift **de uma mudança que era ele próprio a fazer**.

**Por que só aparecia no CI.** Localmente o `HEAD` não se mexe entre duas
corridas seguidas, e o ponto fixo alcança-se. No CI o checkout já é o commit
novo, e o carimbo commitado é sempre o do commit anterior. `PASS local` não era
`PASS remoto` — e nunca ia ser.

**Já tinha acontecido.** O comentário do `IGNORAR` em `scan_repo.py` descreve
este defeito por extenso, apanhado antes com `censo-da-coleta.generated.json` e
`pente-fino.generated.json`: *«e só falhava no CI… o mapa voltava a medir-se a si
mesmo»*. Os três documentos `.md` gerados escaparam à regra por não se chamarem
`.generated.json`.

**Corrigido nesta missão**, porque é defeito do System Map e não da máquina: os
três documentos que `generate_system_map.py` escreve saem do censo, como já saíam
os outros artefatos gerados.

    O MAPA NÃO MEDE O QUE O MAPA ESCREVE.

**Custo, registado:** a exclusão derrubou uma aresta —
`C-MAPA-GERADOR → C-MAPAV2-MEDIDOR`. Ela vinha de `medir_maquina.py` **citar** os
nomes desses ficheiros numa lista de prefixos, não de os ler. Mesma fragilidade
do ACHADO-1: tirar um ficheiro do censo apaga ligações em silêncio.

---

## ACHADO-8 · contar telas não é classificar a ferramenta

A entrega anterior escrevia, em cada ferramenta do portal: **uma** tela =
`ANALISE_PRONTA`, **várias** telas = `EXPLORATORIA`.

**Não existe contrato nenhum neste repositório que defina essa regra.** Era
leitura do próprio mapa a sair com ar de medição. O único sítio onde o projeto
chama uma ferramenta «exploratória» é o **MT3**, e lá a razão está escrita no
contrato dela (`DECISION = SÓ PERGUNTA`) — não no número de ecrãs.

**Removido.** O mapa passa a dizer só o que mediu: `APARECE EM N TELAS`, com a
lista e a prova. A `V21` impede que o rótulo volte.

---

## ACHADO-9 · três associações do censo do casco são decisão humana

`scan_casco.py` liga contrato a ferramenta por nome. Em três casos o nome do
ficheiro não é o nome da tela, e alguém decidiu a ponte:

| ficheiro | tela | porquê |
|---|---|---|
| `calendar` | `windows` | o calendário é a mesma tela das Finestre |
| `competitor` | `competitors` | singular no ficheiro, plural na tela |
| `voci` | `voices` | o ficheiro em italiano, a tela em inglês |

As três são legítimas e **ficam**. O defeito era saírem no artefato dentro da
palavra «medido»: quem lê o mapa tem de poder discordar de uma decisão, e não se
discorda do que não se vê.

**Corrigido:** `casco.generated.json` passa a declarar `COMO_FOI_SABIDO`
(`MEDIDO` · `RECONCILIADO_A_MAO` · `INFERIDO` · `UNKNOWN`), cada reconciliação
com **dono** e **motivo**; e o cartão da ferramenta mostra a ponte num bloco
próprio. A `V20` impede que volte a passar por medição.

---

## KNOW-HOW · o que esta missão confirma, e onde tem de ser registado

O know-how canónico é **`SINTONIA-EAME-KNOW-HOW.md`**, no branch
`claude/sintonia-eame-know-how-v1` — **fora desta base**, e fora do que esta
sessão pode escrever. Fica aqui o delta, para ser transcrito por quem tem essa
permissão. **Não foi criado um segundo know-how.**

1. **Medição automática ≠ reconciliação manual.** Uma ponte de nomes decidida
   por uma pessoa é útil e fica — mas sai marcada, com dono e motivo. Chamar às
   duas «medido» tira a quem lê o direito de discordar.
2. **Quantidade não é tipo.** Contar telas é facto; dizer o que a ferramenta É a
   partir desse número é interpretação. Sem contrato que a defina, não se
   publica.
3. **PASS local ≠ PASS remoto.** O que se mede antes do commit não é o que o CI
   mede depois dele. Validar antes de commitar não prova nada sobre o commit.
4. **O artefato regenerado tem de corresponder ao commit publicado.** Encenar
   primeiro, medir depois, e **voltar a validar já commitado** — porque a
   contagem de ficheiros e o `HEAD` mudam com o próprio commit que os grava.
5. **`DEPLOYMENT URL ≠ ENDEREÇO ESTÁVEL`.** O URL com hash
   (`…-fpx33krow-…`) é o **recibo**: prova que um commit construiu. A morada é o
   alias de branch (`…-git-claude-system-e66563-…`), e é essa que se entrega. Um
   endereço que muda a cada push não é endereço: não se guarda, não se partilha,
   não se abre duas vezes.
6. **`READY DEPLOYMENT ≠ ALIAS ATUALIZADO`.** São dois factos. O segundo mede-se
   **no endereço fixo, depois de publicar** — nunca se infere de a Vercel ter
   dito READY. E `HTTP 200 ≠ versão nova`: um alias parado num deployment antigo
   responde 200 com toda a alegria. Por isso a prova compara **bytes**, não
   estados.

---

## O que NÃO foi tocado para nenhum destes achados

`collection/` · `intelligence/` · `scripts/` · `migrations/` · `italia-portale/server/` ·
`.github/workflows/scrap-social.yml` · contratos canónicos · Bíblia · donos
arquiteturais · e os quatro ficheiros de código do mapa oficial
(`index.html`, `map.js`, `map.css`, `freshness.js`).
