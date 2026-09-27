# FRENTE 2 — A PONTE CORRE SOZINHA

**Lane:** `ponte-curador-v1` · **Modelo:** `claude-opus-5` · **2026-09-22**

---

## ENTREGA

```
PONTE_ENTRY_POINT        curadoria/ponte_automatica.py:servir()  (ciclo próprio)
                         → uma_volta() → reconciliar_livros.censo/aplicar
BOT_BOOK_TRANSPORT       DISCO, por snapshot atómico (sha256) — NÃO Git
WHO_COMMITS_BOT_BOOK     NINGUÉM, e é de propósito (ver abaixo)
IDEMPOTENT_NOOP_PROVEN   YES  (20 voltas sem novidade → 0 escritas)
FAILURE_VISIBLE          YES  (FALHAS_CONSECUTIVAS · ULTIMO_ERRO · backoff · DEGRADADO)
LIVE_PROMOTION_CROSSED   YES  — IT-TEST-001 (decisão real, travessia autónoma)
LIVE_DEMOTION_CROSSED    NO   — exige tocar em produção: é decisão do dono
TEST_RESIDUE             0    (conferido nos 5 ficheiros dos dois lados)
SUPERVISOR_PID_BEFORE    48212
SUPERVISOR_PID_AFTER     48212  (vivo, nunca tocado — zero kills, zero PARAR.flag)
NEW_FAILURES             0
SYSTEM_MAP_CHECK         PASS  (IMPRESSAO_DO_CARIMBO = IGUAL)
PONTE_AUTONOMA_PROVADA   PARTIAL  (o caminho, ao vivo; os extremos do portão, em bancada)
OBSERVER_RUNNING_AS_SERVICE  YES  (PID 14960, filho do Orca, não da sessão)
```

### `PONTE_AUTONOMA_PROVADA = PARTIAL`, e a contagem separada

| o que | REAL (produção) | SIMULADO (bancada) |
|---|---|---|
| a ponte corre sem ninguém mandar | **✅ sim** | — |
| a ponte corre como **serviço**, fora da sessão | **✅ sim** (PID 14960) | — |
| transporte disco→ponte com ficheiro inteiro | **✅ sim** | ✅ |
| decisão nova do bot atravessa até ao portão | **✅ sim** (`IT-TEST-001`) | ✅ |
| idempotência (sem decisão → zero escritas) | **✅ sim** | ✅ |
| falha visível, com backoff, sem derrubar | ✅ (guardas) | ✅ |
| **ENTRA** na lista de elegíveis | ❌ não | ✅ (Frente 1) |
| **SAI** da lista de elegíveis | ❌ não | ✅ (Frente 1) |

É `PARTIAL` e não `YES` porque **o caminho está provado ao vivo, mas os dois
extremos do portão só estão provados em bancada**. Digo-o assim em vez de
arredondar para cima.

---

## 1 · OS 5 FACTOS, REMEDIDOS — dois não confirmaram

Detalhe em `curadoria/FRENTE2-FACTOS-REMEDIDOS.md`.

**FACTO 1 — não confirmou.** O briefing dizia «supervisor vivo, PID 110748».
Medido: **o PID não existia**. Tinha morrido ~5 min depois de arrancar, a meio
de um tick normal, sem erro e sem `PARAR.flag`, deixando o lock órfão.
Causa, dada depois pelo coordenador: fora lançado como **processo de fundo da
sessão dele**, e a sessão levou-o atrás (`exit -15`). **Não houve defeito no
supervisor.** Relançado em terminal próprio: PID `48212`.

**FACTO 4 — confirmou, e é o elo.** 1275 transições no disco contra 1270 no
commit: **5 decisões reais invisíveis** para quem lê pelo Git. Último commit do
bot: 3 h 40 antes.
*Correcção menor:* os sujos de **conteúdo** eram 3 livros; `supervisor.py` e
`telemetria.py` apareciam no `git status` mas com **diff vazio** — mudou-lhes a
data, não o código.

**Factos 2, 3 e 5 confirmaram** (sem combustível · ruído de realimentação ·
lanes divergentes). Só registados — não são escopo.

---

## 2 · AS TRÊS DECISÕES DE DESENHO, COM O CUSTO DITO

### A · ONDE — processo próprio, não hook no supervisor do bot

| opção | porque não / porque sim |
|---|---|
| hook no supervisor do service | **não.** O `supervisor.py` das duas lanes difere em **175 linhas** (+98/−77), a lane do bot tem 20 commits próprios, e o processo **nem estava vivo** para ser instrumentado. Enxertar código desta lane lá era o merge cego que o briefing proíbe. |
| **processo próprio que lê a lane do bot** | **sim.** Desacoplado, não toca na lane viva, e **sobrevive ao bot morrer** — e o bot morre calado. |

> **Custo assumido:** há um segundo processo para manter de pé. E esse custo tem
> um nome, medido nesta missão: quem o lançar tem de o lançar como **serviço**,
> não como processo de fundo de uma sessão — senão morre com quem o lançou.

### B · TRANSPORTE — disco, por snapshot atómico

O Git é **correcto** contra meia-gravação e **cego** para a realidade: o bot
escreve no disco e não commita. Uma ponte automática que lê pelo Git atravessa
só o que alguém guardou à mão — troca «alguém corre a ponte» por «alguém faz
commit».

**Ficheiro inteiro sem cooperação de quem escreve:** lê os bytes, confirma que o
JSON fecha, **relê**, e exige bytes iguais nas duas leituras. Um ficheiro
apanhado a meio falha o parse ou muda de tamanho — nos dois casos, repete. O
`sha256` é **o corte lógico**.

### `WHO_COMMITS_BOT_BOOK = NINGUÉM`, de propósito

Era a saída óbvia e **não a tomei**: commitar automaticamente na lane de um
serviço a correr é escrever no repositório de outra pessoa, e isso é decisão do
dono, não de um observador. Com o snapshot, a pergunta deixa de se pôr — o
briefing autorizava esta via («snapshot atómico com corte lógico é aceitável se
provado») e é a que não pede permissão para nada.

### C · IDEMPOTÊNCIA — o silêncio é requisito, não optimização

Ao lado, medido: o supervisor grava `REALIMENTACAO` idêntico de 15 em 15 s
(~5.760/dia). Irmão do `DISCOVERY_HOOK_ERRO` (3.054 ocorrências, **uma**
mensagem). Aqui: **uma volta sem novidade não escreve linha nenhuma.**

### D · FALHA — visível, com backoff, e nunca derruba

`uma_volta()` **nunca levanta**. `FALHAS_CONSECUTIVAS`, `ULTIMO_ERRO`,
`ULTIMO_ERRO_EM` no estado; backoff até 600 s; `SAUDE = DEGRADADO` ao fim de 3.
Quando volta a ler, escreve `RECUPEROU` e zera o contador.

---

## 3 · A PROVA AO VIVO

O observador foi lançado **antes** de eu provocar nada (PID 122096, ciclo 10 s),
para que a travessia não pudesse ser atribuída a um comando meu.

```
23:02:09   o bot decide        IT-TEST-001  →  CONTRACTED_CANARY_FAILED
23:02:16   a ponte atravessa SOZINHA
           livro canónico 1549 → 1551, com proveniência
           (IMPORTADO_DE + RECONCILIACAO)
           a prova do bot viajou junto — PROVAS_IMPORTADAS: 1
23:02:17   o portão conhece-a:  UNKNOWN / ESTADO_NAO_READY
```

**Zero comandos manuais entre a decisão e o portão.** Oito segundos.

**Caso negativo, no mesmo período:** 22 voltas, 20 sem novidade → **0 linhas
escritas**. O diário ficou com 3 linhas (arranque + 2 travessias).

**Uma só tarefa, e mais nada tocado:** `T01155`, medido por conjunto de
`TASK_ID` antes (1057) e depois (1058), com as 1057 antigas todas presentes.

### `TEST_RESIDUE = 0`

Removido dos **cinco** ficheiros dos dois lados — fila, livro e provas do bot;
livro e provas canónicos — com escrita atómica e **sem parar o serviço** (a
tarefa já estava `DONE`). Conferido a zero em todos. O trabalho **real** que
atravessou ficou: as 5 `IT-T7-*` continuam no canónico.

### Porque é que `LIVE_DEMOTION_CROSSED = NO`

Das 8 elegíveis, o bot conhece **7 como `READY_FOR_COLLECTION`**. Provocar uma
despromoção real exigiria mandá-lo recanariar **uma fonte de produção**. Se
reprovasse, a despromoção seria verdadeira e **não removível**: apagá-la seria
apagar uma medição correcta; mantê-la seria alterar produção por causa de uma
demonstração.

> Fabricar a evidência do canário para uma fonte de teste resolvia a
> demonstração e envenenava o livro. **Uma prova que exige falsificar a prova
> não é uma prova.**

O mecanismo está provado em bancada (Frente 1, sentido `SAI`, mesmo código).
**Fica por fazer e é decisão sua** — o briefing previu esta paragem.

---

## 4 · O QUE FICOU, E O QUE FALTA

| ficheiro | o quê |
|---|---|
| `curadoria/ponte_automatica.py` | o observador: snapshot atómico, idempotência, falha visível, ciclo |
| `curadoria/test_ponte_automatica.py` | 9 guardas (RT-P1..P7) |
| `curadoria/FRENTE2-FACTOS-REMEDIDOS.md` | os 5 factos, remedidos |
| `curadoria/reconciliar_livros.py` | cache dos commits fixos: 1,56 s → 0,15 s |
| `SINTONIA-EAME-KNOW-HOW.md` | `§169`, 6 subsecções |

**Como se põe a correr:**

```bash
py curadoria/ponte_automatica.py --servir --intervalo 20
py curadoria/ponte_automatica.py --estado     # o que ela viu
```

### ✅ LANÇADO COMO SERVIÇO — e provado pela árvore de processos

Por decisão do dono, o observador está **a correr como serviço** desde
2026-09-22 20:33 local, em terminal Orca próprio
(`term_93a624a0-4249-4b4c-9a76-488547b2aa9e`, título
`PONTE-CURADOR-OBSERVADOR (servico)`), intervalo 20 s.

```
OBSERVER_PID        14960  (python.exe)
OBSERVER_INTERVAL   20 s
```

⚠️ **A prova de que é serviço não é o PID: é a ascendência.** Foi por não a
verificar que o supervisor do bot morreu hoje — estava pendurado na sessão de
quem o lançou, e caiu com ela.

```
OBSERVADOR : python(14960) <- py <- powershell <- Orca.exe(39696)
EU (claude): powershell <- bash <- bash <- bash <- claude.exe(118288)
                                              <- powershell <- Orca.exe(39696)
```

O observador pendura **directamente do Orca**, sem passar pela sessão do
agente. Quando esta sessão terminar, ele fica.

Aos 2 minutos de vida: `VOLTAS 32 · NOOPS 29 · SAUDE SAUDAVEL · FALHAS 0`, e o
diário ganhou **uma** linha (o arranque) — o silêncio a funcionar.

**Como se opera:**

```bash
py curadoria/ponte_automatica.py --estado     # o que ela viu
orca terminal list                            # onde ela corre
```

### Aberto, e não é escopo desta missão

1. **O bot está sem combustível** — 33 sementes esgotadas, 0 candidatas por
   qualificar, fila com 0 elegíveis (facto 2).
2. **Ruído de realimentação** — ~5.760 eventos/dia idênticos (facto 3).
3. **42 fontes presas** por `robots` ilegível que já se lê (Frente 1).
4. **`LIVE_DEMOTION_CROSSED`** — precisa da sua decisão.

---

## EM PALAVRAS SIMPLES

**A ponte estava construída, mas era uma ponte levadiça — e o guarda estava de
folga.** Só descia quando uma pessoa escrevia um comando.

Agora há um vigia. De 20 em 20 segundos olha para o caderno do robô e pergunta
uma coisa só: *mudou?* Se não mudou, **não faz nada e não escreve nada** — e
isso é de propósito. Ao lado, o robô escreve 5.760 vezes por dia a mesma frase
(«li 476, enfileirei 0»). Um caderno onde tudo se repete é um caderno onde não
se vê nada.

**O erro que estava escondido:** o vigia ia ver o caderno do robô à *fotocópia
arquivada*, não ao caderno de verdade. E o robô só manda fotocopiar de vez em
quando — a última tinha 3 horas e meia. Estavam lá **5 decisões que ninguém via**.
Agora o vigia lê o caderno mesmo, e tem um truque para não o apanhar a meio de
uma frase: lê, confere que a frase acaba, e **lê outra vez** para ver se nada
mudou entretanto.

**A prova.** Pus o vigia a trabalhar primeiro. Depois dei ao robô um trabalho de
mentira, marcado como teste. O robô examinou e disse «esta não presta». **Oito
segundos depois, sem eu mandar nada, essa decisão já estava do outro lado**, com
a nota de onde veio. Depois limpei o trabalho de mentira dos dois lados: não
ficou rasto nenhum.

**O que não fiz, e porquê.** Faltava mostrar o contrário: uma fonte que **já era
boa** deixar de ser. Para isso teria de mandar o robô reexaminar uma fonte **a
sério, das que estão em uso**. Se ele a reprovasse, a reprovação seria verdade —
e eu não poderia apagá-la depois (seria apagar uma coisa certa) nem deixá-la
(seria estragar o que está a funcionar por causa de uma demonstração).

Havia um atalho: inventar eu a prova de que a fonte era boa e depois inventar a
de que era má. **Isso é falsificar, e não se faz.** Fica à sua decisão.

**E uma coisa que aprendi hoje, à minha custa.** O robô tinha morrido — e não
por estar avariado: foi lançado «pendurado» numa sessão de trabalho, e quando
essa sessão acabou, levou-o atrás. O papel que diz quem manda continuava lá,
com o nome de um processo que já não existia. **Um papel a dizer que está tudo
bem não é o mesmo que estar tudo bem** — é preciso ir perguntar ao computador
se aquele processo ainda respira.
