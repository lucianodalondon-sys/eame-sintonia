# HANDOFF · DELTA DE KNOW-HOW §107

**Para aplicar em `claude/sintonia-eame-know-how-v1` →
`SINTONIA-EAME-KNOW-HOW.md`, a seguir ao `§106`.**

Este ficheiro vive aqui, e não lá, porque esta missão está presa ao seu ramo
(`claude/recovery-proof-before-live-v1`) e não tem autorização para escrever na
linha do know-how. Quem integrar leva o bloco abaixo tal como está.

```
ORIGEM      C-RECOVERY-PROOF-BEFORE-LIVE-V1
MEDIDO_EM   2026-09-13
BASE        claude/raw-observation-identity-3jbwco @ 903e1860
NAO_DUPLICA §106.8 — ali fica a DISTINCAO entre os dois rotulos;
            aqui fica o que se aprendeu ao EXERCER o restauro
```

---

# §107 · UM BACKUP QUE NUNCA VOLTOU NÃO É UM BACKUP — E PROVAR QUE ELE VOLTA EXIGE MATAR O ORIGINAL

O `§106.8` fixou a distinção: `BACKUP EXISTE ≠ RESTORE PROVADO`, e
`NOT_MEASURED ≠ NOT_PROVEN`. O que faltava era a outra metade: **como** se
exerce um restauro de forma que o verde não possa ser falso. Sete coisas
apareceram ao fazê-lo, e nenhuma delas se deduz da primeira.

## 107.1 · RESTAURAR POR CIMA DO QUE AINDA EXISTE NÃO PROVA NADA

É a armadilha central, e ela passa despercebida porque o resultado **parece**
certo: restaura-se o backup sobre o banco que ainda tem os dados, confere-se, e
está tudo lá. Só que uma tabela que o restauro **não trouxe** também continua lá.

```
O VERDE E DO BANCO ANTIGO, E NAO DO BACKUP.
```

Por isso a ordem é: backup → **destruir** → provar que o original desapareceu →
banco vazio → provar que está vazio → restaurar. Duas medições positivas
(`ORIGINAL_DATABASE_AVAILABLE = NO`, `RESTORE_TARGET_EMPTY = YES`) **antes** de
o restauro correr, e não uma frase a dizer que se teve esse cuidado.

## 107.2 · `exit 0` DO RESTAURO NÃO É PROVA DE RESTAURO

Medido, e não suposto: com o índice do arquivo (`pg_restore --list`) filtrado
para deixar cair as linhas do livro-razão, o `pg_restore` restaura **menos** e
devolve **0**. O livro voltou com zero linhas, e o código de saída não mudou.

```
RESTORE PARCIAL COM EXIT 0 E O MODO NORMAL DE FALHAR, NAO O EXCEPCIONAL.
```

Quem confia no código de saída fica com um banco incompleto e um log verde.

## 107.3 · UMA IMPRESSÃO DE SETE SECÇÕES, E NÃO UM NÚMERO

Um total só diz «mudou». Sete secções dizem **o quê**, e a diferença é metade do
diagnóstico — porque as perguntas não são a mesma:

```
TABELAS · LINHAS · LEDGER · SENTINELAS · TRAVAS · INDICES · SEQUENCIAS
```

Medido, ataque a ataque: restaurar só o schema move `LINHAS`, `SENTINELAS`,
`LEDGER` e `SEQUENCIAS` e **não** move `TABELAS`; perder uma trava move `TRAVAS`
e **não** move `LINHAS`; mudar um ID move `SENTINELAS` e **não** move `LINHAS`.
Com um número só, os três seriam a mesma frase.

```
SCHEMA_RESTORED != DATA_RESTORED != RELATIONS_RESTORED != PODE_OPERAR
```

## 107.4 · A CONFERÊNCIA CORRE EM SESSÃO SÓ-LEITURA — E ISSO É A PROVA, NÃO A CAUTELA

O `§106.1` usa `begin read only` como **tranca** contra escrever em produção.
Aqui ela serve outra coisa: é o que transforma *«não consertei nada antes de
conferir»* de **promessa** em **medição**. Com o servidor a recusar escrita — e
a recusa **conferida**, não pedida — o conserto não foi apenas não-feito: era
impossível.

```
REPAROS_MANUAIS_ANTES_DA_CONFERENCIA = 0, e ha quem prove que sim.
```

## 107.5 · PROVAR UM MECANISMO NÃO PROVA O OUTRO

`pg_dump` é backup **lógico**. Backup de provedor e PITR são outra coisa.
Exercer o primeiro até ao fim, com zero sobreviventes no red team, dá
`RESTORE_MECHANISM = PROVEN` — e **não** move `SAME_CLASS_RESTORE`.

```
FERRAMENTA PROVADA != FONTE PROVADA.
CHAMAR DE EQUIVALENTE O QUE NAO SE MEDIU E O UNICO VERDE QUE NAO SE PODE DAR.
```

Por isso o portão é uma **função** com cinco entradas, e não uma frase de
conclusão — e dois ataques do red team batem directamente nela, com
`SAME_CLASS` em `UNKNOWN` e em `NO`. Uma frase não se consegue atacar.

## 107.6 · UM VEREDITO QUE SE AFIRMA POR VARIÁVEL DE AMBIENTE OBEDECE A QUEM O CORRE

A tentação é passar `LIVE_BACKUP_STATUS` por `env` para a prova poder fechar o
portão «quando alguém souber». Isso faz do veredito uma preferência.

A medição do LIVE tem de nascer de olhar para sítios que existem — credencial de
gestão no ambiente, workflow que **produza** backup, registo datado de um
restauro — a **cada corrida**. Assim a resposta muda sozinha no dia em que os
factos mudarem, e não no dia em que alguém escrever outra coisa.

## 107.7 · O MAPA NÃO VÊ UM `.py` A CORRER UM `.sh`

Achado lateral, e durável. No scanner, a aresta `RUNS` só nasce de `.yml` e de
`.sh`. Uma prova escrita em Python que chama `motor/cadeia_canonica.sh` por
`subprocess` produz apenas `READS` — que o gerador **vira**, e portanto entra
na peça em vez de sair dela. Como a regra de `kind: test` exige aresta **de
saída**, a peça fica 🟡 com a frase *«teste que nao toca em nada do
repositorio»* — tendo três ligações provadas a apontar para ela.

```
PENDING POR REGRA DO MAPA != PECA DESLIGADA.
```

O caminho canónico escreve-se num literal só
(`os.path.join(RAIZ, "motor/cadeia_canonica.sh")`), porque é dessa linha que a
prova da ligação sai. Partido em dois literais, o scanner ainda acha o ficheiro
pelo nome, mas deixa de conseguir apontar a linha que o chama.

**E não se deforma o código para a bolinha mudar de cor.** A peça fica amarela,
a frase fica errada, e isso regista-se — em vez de se trocar `kind` ou de se
inventar uma aresta.

## 107.8 · POLÍTICA PROVADA NÃO É ARTEFATO PROVADO — E MEDIR APERTA

Apareceu depois do hard stop, quando a medição externa chegou: plano **Pro**,
Postgres **17.6.1.166**, e a documentação a dizer que acima de `15.8.1.079` o
backup é **físico**. Três tentações de uma vez.

```
POLITICA PROVADA != ARTEFATO PROVADO.
«O PLANO PREVE BACKUP DIARIO» NAO E «ESTE BACKUP EXISTE, E E DESTE INSTANTE».
```

`PLATFORM_BACKUP_POLICY = PROVEN` e `LIVE_BACKUP_STATUS = NOT_MEASURED`
imprimem-se **lado a lado**, e é entre essas duas linhas que mora a tentação.
Enquanto ninguém listar um backup concreto e o datar, a fonte continua
`NOT_PROVEN` — por mais generoso que o plano seja.

E a segunda lição é contra-intuitiva, e é a boa:

```
MEDIR A PLATAFORMA APERTOU O VEREDITO, EM VEZ DE O AFROUXAR.
```

`SAME_CLASS_RESTORE` estava em `UNKNOWN` por ignorância. Sabida a classe do
LIVE (`PHYSICAL`) contra a da bancada (`LOGICAL`), passou a `NO`. Uma medição
que só podia melhorar a resposta não é uma medição — é uma procura de
confirmação. **Um facto externo só entra num portão se ele conseguir piorar o
resultado.**

Daí a forma: os factos que a sessão não mede vivem num **ficheiro versionado
com proveniência** (`COORDINATION_MEASURED / LOCAL_NOT_REMEASURED`), e não
cravados dentro da função de medição — onde um facto de fora passa a parecer
medido. E a comparação do portão passou a ser entre **classes**, nunca entre
nomes de ferramenta: era isso que `SAME_CLASS_*` sempre quis perguntar.

## 107.9 · CONSEQUÊNCIA

```
· backup so se prova com o original destruido, e a destruicao mede-se
· destino do restauro prova-se VAZIO antes, e nao depois
· exit 0 nao e prova; a impressao e
· a impressao parte-se por pergunta, senao esconde qual delas falhou
· a sessao so-leitura na conferencia e prova de «nao consertei», nao cautela
· mecanismo provado nao promove fonte por medir
· o portao e funcao com entradas, para o red team poder bater nele
· veredito que se passa por env obedece a quem corre, nao ao que existe
· aresta que o mapa nao consegue provar fica amarela, e nao se pinta
· politica da plataforma nao promove o artefato, e imprimem-se juntas
· facto externo so entra num portao se puder PIORAR o resultado
· facto que a sessao nao mede vive em ficheiro com proveniencia,
  nunca dentro da funcao que mede
· o portao compara CLASSES de backup, e nao nomes de ferramenta
```

**Medido:** PostgreSQL 16.13 descartável · 29 migrations pela cadeia canónica ·
impressão `041c4dee…` idêntica antes e depois · `RESTORE_COMMAND_EXIT = 0` com
`SECOES_DIFERENTES = NENHUMA` · segunda passagem da cadeia sobre o restaurado
= 29 `SKIP HASH=MATCH`, 0 reaplicadas · 5 travas mordidas · **21 ataques, 0
sobreviventes** · regressão 123 alvos, `NEW_FAILURES = 0` ·
**`LIVE_WRITES_PERFORMED = 0`**.

**Addendum (2026-09-13, pos-hard-stop):** medicao externa da coordenacao —
plano Pro, Postgres 17.6.1.166, backup do LIVE de classe `PHYSICAL` —
moveu `SAME_CLASS_RESTORE` de `UNKNOWN` para **`NO`**. O portao continua
`BLOCKED`, por um motivo mais nitido. `A21` nasceu dessa medicao.
