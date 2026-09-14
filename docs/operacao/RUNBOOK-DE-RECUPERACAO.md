# RUNBOOK DE RECUPERAÇÃO — o banco do SINTONIA EAME

```
DONO_CANONICO     este ficheiro
CRIADO_EM         2026-09-14
CRIADO_POR        C-RESTORE-PROOF-BEFORE-LIVE-V2
PROVA_QUE_O_SUSTENTA  provas/recuperacao_fisica_provada_no_postgres.py
MEDICAO               provas/RECUPERACAO-FISICA-MEDIDA.json
```

> ## ⚠️ ESTE RUNBOOK TEM UMA METADE PROVADA E UMA METADE NÃO PROVADA
>
> A **classe** do mecanismo — base backup físico + WAL + recuperação a um
> instante — está exercida, com desastre real e conferência forte, e o
> `§6` diz exactamente onde.
>
> A **plataforma** — carregar no Restore do Supabase, neste projeto, com
> esta conta — **nunca foi exercida**. O `§7` diz o que falta, e este
> runbook não finge que essa parte está provada.
>
> ```
> MESMA CLASSE  !=  MESMA PLATAFORMA.
> CAN DO        !=  DID DO.
> ```

---

## 1 · QUANDO USAR

Use este runbook quando o banco **perdeu estado** e o estado tem de voltar:

| situação | é caso de restauro? |
|---|---|
| `DELETE`/`UPDATE` em massa sem `where`, já confirmado | **sim** |
| `DROP TABLE` / `DROP COLUMN` em produção | **sim** |
| migration aplicada que estragou dados e não tem caminho para a frente | **sim** |
| corrupção lógica descoberta horas depois | **sim** — e o instante é o que importa |
| migration aplicada que só precisa de ser desfeita | **não** — ver `§8`, isso é *rollback* |
| aplicação a ler dados errados por causa de um bug no código | **não** — o banco está bem |
| um único registo errado que alguém sabe corrigir | **não** — corrija o registo |

> **RESTAURAR É CARO E APAGA O QUE VEIO DEPOIS.** Um restauro a um instante
> anterior deita fora **todas** as escritas entre esse instante e agora,
> incluindo as boas. Antes de restaurar, pergunte se o estrago é mesmo
> maior do que o que se perde.

---

## 2 · QUEM EXECUTA

| papel | o quê |
|---|---|
| **coordenador** | decide QUE se restaura e para QUE INSTANTE. Sem esta decisão, nada começa. |
| **administrador do projeto Supabase** | é quem TEM as credenciais e quem carrega no botão. Nenhuma sessão de agente tem acesso de gestão a este projeto — medido, não suposto. |
| **agente / CI** | corre a conferência do `§5`, e **não** executa o restauro. |

```
NENHUM AGENTE DESTA CASA TEM CREDENCIAL DE GESTAO DO SUPABASE.
Um runbook que fingisse o contrario nao correria no dia em que fosse preciso.
```

---

## 3 · QUAL MECANISMO — e há dois, com donos diferentes

Nomeá-los é metade do trabalho, porque confundi-los é como se perde um dia
numa emergência.

| | `A · RESTAURO DA PLATAFORMA` | `B · CADEIA CANÓNICA` |
|---|---|---|
| o que é | backup **físico** do provedor + WAL, recuperado a um instante | reaplicar `supabase/migrations/` num banco vazio |
| classe | `PHYSICAL` | não é restauro — é **construção** |
| devolve dados? | **sim** | **não** |
| quem executa | administrador, na consola do Supabase | `motor/cadeia_canonica.sh` |
| quando | perda de estado (`§1`) | banco novo, bancada, ambiente descartável |

### ⚠️ E O `A` TEM DOIS SABORES, COM RPO MUITO DIFERENTE

Medido na documentação oficial em 2026-09-14 (`C-SUPABASE-LIVE-RECOVERY-PREFLIGHT-V1`):

| | `BACKUP DIÁRIO` | `PITR` |
|---|---|---|
| vem com o plano? | **sim** (Pro: 7 dias) | **não — é add-on PAGO** |
| granularidade | **um ponto por dia** | até ao **segundo** |
| RPO na prática | **até 24 horas** | ~2 minutos no pior caso |
| ligado neste projeto? | **SIM — 7 backups físicos medidos** | **NÃO — `pitr_enabled` = `false`, medido** |

Medido em 2026-09-14 pela Management API, em `C-SUPABASE-BACKUP-READONLY-MEASURE-V1`
(`provas/SUPABASE-LIVE-BACKUP-MEASURED.json`): sete backups `COMPLETED`, todos
físicos, de `2026-09-07 03:07` a `2026-09-13 03:05` UTC, `walg_enabled = true`,
região `eu-west-1`.

```
LIVE_RECOVERY_MECHANISM = SUPABASE_BACKUP_RESTORE   (backup diario fisico)
```

> **NÃO CONTE COM RECUPERAÇÃO AO SEGUNDO.** Ligar PITR é uma decisão de
> dinheiro que ninguém tomou. Isto já não é uma suposição prudente — está
> **medido**: `pitr_enabled = false`.
>
> ```
> RPO REAL DESTE PROJETO = ATE ~24 HORAS.
> ```
>
> E há uma precisão que a média esconde: o backup é das **~03:07 UTC**. Uma
> perda às 02:00 UTC custa ~23 horas de escritas; uma perda às 04:00 UTC
> custa ~1 hora. **O RPO não é uniforme ao longo do dia** — diga ao
> coordenador a hora, e não só o número, no passo `§5.1.3`.
>
> E há uma armadilha ao contrário: a documentação diz que **ligar PITR
> DESLIGA o backup diário**. Não são duas redes de segurança empilhadas.

> **B NÃO É UMA ALTERNATIVA A A.**
> Reconstruir o schema a correr migrations devolve um banco **vazio** com a
> forma certa. Se alguém chamar a isso «recuperámos», a casa perdeu os dados
> e ainda assim declarou verde.
>
> ```
> REBUILD POR MIGRATIONS NAO E RESTORE.
> REINSERT DE DADOS NAO E RESTORE.
> ```

O mecanismo desta casa para uma emergência real é o **A**. É por isso que
provar o **B** — que é o que a `C-RECOVERY-PROOF-BEFORE-LIVE-V1` provou, com
`pg_dump` — não fecha esta pergunta.

---

## 4 · PRÉ-CONDIÇÕES — todas, antes de tocar em alguma coisa

Se **qualquer** uma falhar, pare e vá ao `§7`.

```
[ ] 1. o coordenador decidiu, por escrito, o INSTANTE de destino
[ ] 2. o project ref foi lido da consola AGORA, e conferido contra o §9
[ ] 3. a consola mostra um backup/PITR que COBRE esse instante
[ ] 4. a janela de retencao ainda nao passou por cima do instante
[ ] 5. o destino do restauro esta decidido: projeto NOVO, ou in-place
[ ] 6. quem executa tem acesso de gestao ao projeto
[ ] 7. esta escrito o que se perde entre o instante e agora
[ ] 8. a coleta esta PARADA — nada escreve durante o restauro
```

> O ponto **3** é o que mais se assume e menos se mede. «O plano Pro tem
> backup diário» é uma frase sobre um produto, não sobre este projeto.
>
> Para **medir** em vez de assumir, há agora uma porta que o faz sem escrever
> nada e sem credencial de banco:
>
> ```
> .github/workflows/supabase-backup-readonly.yml   (um GET, zero escritas)
> ```
>
> Ela lista os backups deste projeto com data, e diz se o PITR está ligado.
> **Corra-a antes do ponto 3**, e leia a janela real em vez de a presumir. E
> note que a medição envelhece: um artefacto de ontem não cobre o instante
> de hoje.
>
> ```
> POLITICA DA PLATAFORMA PROVADA  !=  ESTE BACKUP EXISTE, E E DESTE INSTANTE.
> ```

---

## 5 · PASSOS

### 5.1 · antes (e isto é o passo que se salta e depois faz falta)

1. **Fotografe o estado estragado** antes de o deitar fora. Um restauro
   apaga a prova do que aconteceu, e a seguir ninguém consegue explicar
   porquê.
2. **Pare a coleta.** Uma escrita a meio de um restauro é uma escrita que
   ninguém vai conseguir explicar depois.
3. **Escreva o instante** de destino, em UTC, com segundos.

### 5.2 · o restauro (mecanismo `A`)

4. Consola do Supabase → projeto → **Database → Backups**.
5. Confirme, **no ecrã**, que existe ponto de recuperação que cobre o
   instante do passo 3.
6. **Restaure para um projeto NOVO quando puder.** In-place destrói o
   estado actual e, se o restauro sair errado, já não há para onde voltar.
7. Espere. Não cancele a meio — ver `§5.4`.

### 5.3 · a conferência (`§6` diz porque é que ela é assim)

8. Corra a impressão contra o banco restaurado e compare com a de
   referência. Secção a secção, nunca um número só.
9. Confirme que as **travas mordem** — que existirem não chega.
10. Confirme o **livro-razão**: `select versao, sha256 from
    public.schema_migracao`, e cada `sha256` tem de bater com o ficheiro em
    `supabase/migrations/`.

### 5.4 · se o restauro for interrompido

Medido na bancada, não suposto:

| pergunta | resposta medida |
|---|---|
| o estado intermédio é utilizável? | **não** — o servidor **recusa ligações** enquanto reproduz |
| pode ser retomado? | **sim** — arrancar outra vez continua de onde ia |
| é preciso recomeçar do zero? | **não** |
| como sei que terminou? | `pg_is_in_recovery()` devolve `f`, e só então há ligações |

> O estado intermédio ser **bloqueado** é a boa notícia: um banco meio
> recuperado que aceitasse ligações serviria dados incompletos a quem
> perguntasse.

---

## 6 · COMO VALIDAR — e porque é que contar linhas não chega

```
100 LINHAS ANTES E 100 DEPOIS NAO PROVA QUE SAO AS MESMAS 100.
```

A impressão tem **onze secções** e cada uma sela uma família de factos que
um restauro pode acertar ou errar sem mexer nas outras:

`TABELAS` · `LINHAS` · `LEDGER` · `SENTINELAS` · `TRAVAS` · `INDICES` ·
`SEQUENCIAS` · `EXTENSOES` · `DONOS` · `AMBIENTE` · `TIPOS`

Exija, com estes nomes:

```
SCHEMA_DIFF_AFTER_RESTORE = 0
DATA_SENTINEL_DIFF        = 0
BROKEN_FK                 = 0
MISSING_INDEX             = 0
MISSING_CONSTRAINT        = 0
UNEXPECTED_ROWS           = 0
```

### As duas regras que não são igualdade

**As sequências não se comparam por igualdade.** O PostgreSQL regista o
valor de uma sequência no WAL aos saltos (32 de cada vez), de propósito:
assim uma recuperação nunca devolve uma sequência **atrasada**, que
entregaria um id já usado. O preço é que ela volta **adiantada**.

```
SEQUENCIA ADIANTADA DEPOIS DE UM RESTAURO E CORRECTO.
SEQUENCIA ATRASADA E UM ID DUPLICADO A ESPERA DE ACONTECER.
```

A regra é: nunca para trás, e no máximo um bloco de WAL à frente.

**O servidor arrancar não prova que o restauro chegou ao instante pedido.**
Medido, e é o achado mais perigoso desta prova:

| alvo pedido | o que o PostgreSQL faz |
|---|---|
| **à frente** do WAL disponível | `FATAL`, e **não** promove — defende-se |
| **atrás** do início do backup | **PROMOVE, calado**, no estado do backup |

No segundo caso o log escreve «database system is ready to accept
connections», o `exit` é `0`, e o banco entregue está **silenciosamente
atrasado**. Quem confiasse no arranque levava isso para produção.

```
EXIT 0 E «READY TO ACCEPT CONNECTIONS» NAO SAO PROVA
DE QUE O RESTAURO CHEGOU AO INSTANTE PEDIDO.
```

A defesa é um **marco**: uma linha escrita **depois** do backup e **antes**
do instante de destino. Ela não está nos ficheiros copiados — só no WAL. Se
ela voltar, o WAL foi mesmo reproduzido. Se não voltar, o restauro parou
cedo, por muito verde que o log esteja.

---

## 7 · QUANDO ABORTAR

Pare, e **não** continue a improvisar, se:

- a consola não mostrar ponto de recuperação que cubra o instante;
- o instante estiver fora da janela de retenção;
- o `project ref` no ecrã não for o do `§9`;
- a conferência do `§6` acusar **qualquer** secção;
- o marco pós-restauro não voltar (o restauro parou cedo);
- as sequências vierem **atrasadas**;
- alguém propuser «reaplicar as migrations» como substituto (ver `§3`).

> **UM RESTAURO PARCIAL TRATADO COMO COMPLETO É PIOR DO QUE NENHUM**, porque
> a casa volta ao trabalho a acreditar que voltou.

---

## 8 · ROLLBACK NÃO É RESTORE

| | `ROLLBACK` | `RESTORE` |
|---|---|---|
| desfaz | **uma alteração conhecida** | **o estado do banco** |
| custo | baixo | alto: apaga tudo o que veio depois |
| dono | a migration que a fez | este runbook |
| perde dados de terceiros? | não | **sim** |

Uma migration precisa de **`FORWARD_RECOVERY_PLAN`** — o caminho para a
frente que desfaz o que ela fez. A operação precisa de
**`DISASTER_RESTORE_PLAN`** — este ficheiro. Não são a mesma coisa, e
tratá-las como se fossem leva a restaurar o banco inteiro para desfazer um
`create table`.

Para a **031** (`sala_de_espera`), o caminho para a frente é
`drop table public.sala_de_espera` mais apagar a linha `031` do livro-razão:
ela **cria** uma tabela nova e **não altera** nenhuma existente, por isso
desfazê-la não toca em dados de mais ninguém. Isso é *rollback*, é barato, e
**não** é caso para este runbook.

E isto deixou de ser uma promessa: `provas/preflight_da_cadeia_ate_031.py`
**executa** esse rollback contra um banco descartável e confere que o estado
volta exactamente ao da `030` — mesmas tabelas, livro-razão em `030`.

```
FORWARD_RECOVERY_031_EXECUTADO      SIM
DEVOLVEU_O_ESTADO_030               SIM
```

---

## 9 · COMO EVITAR RECUPERAR O PROJETO ERRADO

O erro mais caro desta lista, e o mais fácil de cometer, porque acontece
num ecrã com vários projetos parecidos.

```
PROJECT        eame-sintonia
PROJECT_REF    odhdwvugikjdvkapbowe
REGIAO         eu-west-1        (historica; CONFIRMAR no ecra)
ENGINE         PostgreSQL 17
```

> ⚠️ Estes valores são **referência histórica**, medidos pela coordenação em
> 2026-09-13 e **não** remedidos por esta missão. Confirme-os no ecrã. Um
> runbook que se deixe ler como se fosse a consola vira o segundo dono de
> uma verdade que já tem dono.

Antes de carregar em Restore:

```
[ ] o project ref no URL do browser e, caracter a caracter, o de cima
[ ] o nome do projeto no cabecalho e `eame-sintonia`
[ ] nao ha uma segunda aba aberta noutro projeto
```

E há uma conferência **de fora** que custa um comando e não precisa de
credencial nenhuma — o gateway devolve o `ref` que serviu:

```bash
curl -sS -D - -o /dev/null https://odhdwvugikjdvkapbowe.supabase.co/rest/v1/ \
  | grep -i sb-project-ref
# sb-project-ref: odhdwvugikjdvkapbowe     <- tem de bater, caracter a caracter
```

E depois, **de dentro do banco** — é a única conferência que não depende de
ter olhado para o ecrã certo:

```sql
select current_database(),
       (select count(*) from public.schema_migracao) as migrations,
       (select max(versao) from public.schema_migracao) as ultima;
```

E **como sei que voltou**: o número de migrations e a última versão batem
com o esperado, a impressão do `§6` não acusa nenhuma secção, e a aplicação
liga à DSN do projeto restaurado — não à antiga.

```
RESTORE TERMINA, E A APLICACAO CONTINUA A LIGAR AO BANCO VELHO:
o restauro esta certo e a casa continua partida.
```

---

## 10 · COMO CORRER A PROVA OUTRA VEZ

A prova constrói tudo e deita tudo fora. Ela **não** toca no LIVE, e
recusa-se a arrancar contra um endereço que não seja local.

```bash
# PostgreSQL 17 (a bancada corre no mesmo major do LIVE)
apt-get install -y postgresql-17

PG_BIN=/usr/lib/postgresql/17/bin \
BANCADA=/var/lib/postgresql/bancada \
python3 provas/recuperacao_fisica_provada_no_postgres.py
```

Exige, para passar: `SECOES_DIFERENTES = NENHUMA`,
`WAL_FOI_REPRODUZIDO = SIM`, `SEQUENCIAS = PASS`, contraprova a acusar as
treze sabotagens, e `RED_TEAM_SURVIVORS = 0`.

> ⚠️ **ESTA PROVA AINDA NÃO CORRE SOZINHA.** Não está ligada a nenhum
> workflow: `banco-descartavel.yml` levanta o Postgres como *service
> container*, e esta prova precisa de um cluster próprio (arquivo de WAL,
> paragem e arranque), que um *service container* não dá. Ligá-la ao CI é o
> passo seguinte, e está por fazer.
>
> ```
> UMA PROVA QUE DEPENDE DE ALGUEM SE LEMBRAR DELA ENVELHECE EM SILENCIO —
> que e a unica maneira de uma prova deixar de valer sem ninguem notar.
> ```
