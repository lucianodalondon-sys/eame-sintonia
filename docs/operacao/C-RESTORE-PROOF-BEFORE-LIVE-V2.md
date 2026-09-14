# PROVA DE RESTAURO — A CLASSE CERTA, DESTA VEZ

```
MISSAO             C-RESTORE-PROOF-BEFORE-LIVE-V2
MEDIDO_EM          2026-09-14T00:50Z
RAMO_DESTA_MISSAO  claude/restore-proof-before-live-v2
BASE               f888776dffd789053fbaf39fc9fe630c74dde3ef  (linha funcional)
LIVE_READS         0
LIVE_WRITES        0
LIVE_DDL           0
MIGRATION_031_APPLIED  NO
```

> Esta missão responde a **uma** pergunta: antes de aplicar a `031` no LIVE,
> conseguimos **provar** uma recuperação real contra tecnologia da mesma
> classe do LIVE, sem usar produção como laboratório?
>
> **Resposta: provámos a CLASSE. Não provámos a PLATAFORMA.** E as duas
> coisas não se substituem uma à outra.

---

## 1 · EM PORTUGUÊS FÁCIL

**1. Existe backup de verdade?**
Do LIVE, **continuamos sem saber**. Esta sessão não tem credencial de gestão
do Supabase — medido, não suposto — e por isso ninguém listou, datou nem
tocou num backup concreto deste projeto. O que se sabe é a **política** do
plano, que é uma frase sobre um produto, não sobre este banco.

**2. Conseguimos restaurar de verdade?**
**Sim** — e desta vez com o mecanismo da classe certa. Um banco foi
destruído e voltou inteiro a partir de uma cópia física mais o WAL.

**3. Onde testámos?**
Numa bancada descartável, PostgreSQL **17** (o LIVE corre 17), que nasce e
morre dentro da prova. **Nunca em produção.** Nenhum byte do LIVE saiu, e a
trava recusa qualquer endereço que não seja local.

**4. O que quebrámos de propósito?**
Quatro coisas diferentes, e todas confirmadas depois de feitas: apagámos
dados, deitámos abaixo a tabela da Sala inteira, tirámos uma trava e um
índice e metemos uma migration falsa no livro-razão, e adulterámos um JSON
e uma contagem.

**5. O que voltou?**
Tudo. As 93 tabelas, a Sala, a trava, o índice, o livro-razão sem a
migration falsa, o JSON limpo e a contagem certa.

**6. Voltaram os mesmos dados ou só a mesma quantidade?**
**Os mesmos.** A conferência não conta linhas: hasheia o conteúdo inteiro de
cada linha. Trocar uma palavra numa sentinela, deixando a contagem igual,
faz a conferência acusar — e isso foi testado de propósito.

**7. As relações/constraints voltaram?**
Sim, e não foram só contadas: as oito foram **provocadas** uma a uma, e o
banco **recusou** as oito. Uma trava que não recusa nada é um desenho.

**8. Quanto tempo levou?**
`0,55 s` para recuperar, nesta bancada, com este tamanho. **Este número não
é o do LIVE** e não se promete que seja.

**9. O mecanismo testado é o mesmo disponível para o LIVE?**
**Da mesma classe, sim. Da mesma plataforma, não.** Provámos base backup
físico + WAL + recuperação a um instante — a mecânica que o Supabase
embrulha. Não carregámos no botão de Restore do Supabase, porque esta sessão
não lhe chega.

**10. Tocámos no banco real?**
**Não.** Zero leituras, zero escritas, zero DDL.

**11. A migration 031 foi aplicada?**
**Não no LIVE.** Foi aplicada na bancada descartável, de propósito, para que
o restauro tivesse a Sala para devolver.

**12. Agora estamos prontos para aplicar no LIVE?**
**Não.** Falta uma coisa só, e está nomeada no `§8`.

---

## 2 · O QUE ESTA MISSÃO ENCONTROU E A ANTERIOR NÃO PODIA ENCONTRAR

A `C-RECOVERY-PROOF-BEFORE-LIVE-V1` fechou com `SAME_CLASS_RESTORE = NO`:
provou a classe **lógica** (`pg_dump`) e descobriu, depois, que o LIVE é da
classe **física**. Esta missão ataca exactamente essa lacuna.

```
                          V1                V2
DISPOSABLE_BACKUP_CLASS   LOGICAL           PHYSICAL
LIVE_BACKUP_CLASS         PHYSICAL          PHYSICAL
SAME_CLASS_RESTORE        NO           ->   YES
SAME_PLATFORM_RESTORE     (nao medido) ->   NO
```

A lacuna **mudou de sítio**, e isso é um avanço: deixou de ser sobre a
classe da ferramenta e passou a ser só sobre **quem opera o botão**.

---

## 3 · A BANCADA, E ELA É DESCARTÁVEL DE VERDADE

```
POSTGRES_VERSION      17.11      (o LIVE corre 17; o major e o que conta
                                  para um backup FISICO)
DATA_CHECKSUMS        on
WAL_LEVEL             replica
ARCHIVE_MODE          on
MIGRATIONS_APLICADAS  29  (001-007, 009-030; a 008 confere e nao cria)
CONFERENCIA_008       PASS
MIGRATION_031         PASS
SHA_031               9414b4f7becd81382512ce2af5b5a28f334aa70b6cea127bdb6ff8c52eb306e3
CORPUS_DO_LIVE_IMPORTADO  NAO
```

A 031 é **lida do ramo que é dono dela**
(`claude/sala-persistente-preflight-real-v1`) e não copiada para esta linha.
Esta missão tem autoridade para a **pôr à prova**, não para a alterar.

O schema é construído pelo **aplicador canónico**
(`motor/cadeia_canonica.sh`) e por nenhum segundo. Se esta prova montasse o
banco de outra maneira, provaria o restauro de um banco que a casa não tem.

---

## 4 · O DESASTRE — quatro famílias, e todas confirmadas

Um restauro pode acertar numa família e falhar noutra.

| | o que se fez | confirmado por |
|---|---|---|
| **A** | `delete` das linhas da Sala e dos documentos de uma corrida | `documentos_restantes = 0` |
| **B** | `drop table public.sala_de_espera cascade` | `sala_existe = 0` |
| **C** | tirar um `CHECK`, tirar um índice, juntar uma coluna, e meter a migration falsa `999` no livro | `trava_existe = 0`, `ledger_tem_999 = 1` |
| **D** | adulterar um `jsonb` e uma contagem | `json_adulterado = true`, `contagem_adulterada = 999` |

```
DESTRUICAO_REAL = SIM
```

### E duas coisas que o banco **recusou** estragar

```
D0a_identidade_da_observacao  RECUSOU
D0b_sha_da_copia              RECUSOU
```

A primeira tentativa de corrupção era adulterar o `sha256` da observação. O
banco recusou, com uma trava da FASE 10 — *«a identidade da observacao nao se
reescreve»* — e a segunda, o `sha256` da cópia, bateu na FK composta
`a_observacao_e_a_copia_falam_do_mesmo_conteudo`.

Isto é **boa notícia sobre a casa** e ficou registado. Mas obrigou a
reescrever o desastre, e a razão vale mais do que o desastre:

```
UM DESASTRE QUE O BANCO RECUSA NAO E UM DESASTRE.
Tratar a recusa como estrago deixaria esta prova a restaurar de um
estrago que nunca aconteceu — e a chamar-lhe verde.
```

---

## 5 · O RESTAURO — e o original desaparece antes

```
ORIGINAL_DATABASE_AVAILABLE   NO      <- o PGDATA da primaria foi APAGADO
RESTORE_MECHANISM             PITR: base backup fisico + restore_command
                                    + recovery_target_time
BACKUP_CLASS                  PHYSICAL
BACKUP_BYTES                  53 102 427
BACKUP_FICHEIROS              1 724
BACKUP_INTEGRITY_CHECK        PASS    (pg_verifybackup, sha256 por ficheiro)
RESTORE_EXECUTED              YES
EM_RECUPERACAO_DEPOIS         f
```

> **RESTAURAR POR CIMA DO QUE AINDA EXISTE NÃO PROVA NADA.** Se a primária
> continuasse de pé, uma tabela que o restauro não trouxesse continuaria lá,
> e o verde seria do banco velho em vez de ser do backup.

### E o WAL foi **mesmo** reproduzido

```
MARCO_POS_BACKUP_VOLTOU   SIM
WAL_FOI_REPRODUZIDO       SIM
```

Este campo nasceu de um **defeito desta própria prova**. Na primeira versão
a impressão de referência era tirada **antes** do base backup — e então um
restauro que reproduzisse **zero** WAL batia certo na mesma. A prova teria
aprovado um PITR que nunca fez PITR.

```
COPIAR O BASE BACKUP NAO E REPRODUZIR O WAL.
UMA IMPRESSAO QUE O BASE BACKUP SOZINHO SATISFAZ NAO PROVA RECUPERACAO.
```

A correcção é um **marco**: linhas escritas depois do backup e antes do
instante de destino. Não estão nos ficheiros copiados — só no WAL.

### A impressão, onze secções

```
IMPRESSAO_ANTES   06414b799445c1b5209346ec2e2a77707738d0f22236688a03725fbf38aa367c
IMPRESSAO_DEPOIS  06414b799445c1b5209346ec2e2a77707738d0f22236688a03725fbf38aa367c
SECOES_DIFERENTES NENHUMA
```

`TABELAS` · `LINHAS` · `LEDGER` · `SENTINELAS` · `TRAVAS` · `INDICES` ·
`SEQUENCIAS` · `EXTENSOES` · `DONOS` · `AMBIENTE` · `TIPOS`

`SENTINELAS` hasheia o **conteúdo inteiro** de cada linha, via `to_jsonb`.
Contar linhas apanharia a linha que sumiu e não apanharia a linha trocada.

### As sequências têm regra própria, e a regra nasceu de um erro

```
SEQUENCIAS_CONFERIDAS      64
SEQUENCIAS_FORA_DA_REGRA   NENHUMA
REGRA                      nunca para tras; no maximo um bloco de WAL a frente
```

Na primeira corrida esta prova **reprovou o seu próprio restauro**, com
`SECOES_DIFERENTES = ['SEQUENCIAS']`. O restauro estava certo; a regra de
comparação é que estava errada. O PostgreSQL regista as sequências no WAL aos
saltos de 32, de propósito, para que uma recuperação nunca devolva uma
sequência **atrasada**.

```
SEQUENCIA ADIANTADA DEPOIS DE UM RESTAURO E CORRECTO.
SEQUENCIA ATRASADA E UM ID DUPLICADO A ESPERA DE ACONTECER.
```

---

## 6 · O BANCO RESTAURADO **OPERA**

```
CADEIA_CANONICA_EXIT                 0
CADEIA_SKIP_HASH_MATCH               29
CADEIA_REAPLICADAS                   0
CONFERENCIA_008                      PASS
LINHAGEM_LIDA_ATE_A_OBSERVACAO       RESTAURO-FISICO-DOC-1
CORRIDA_DA_ARESTA_E_A_DA_DERIVACAO   SIM
SESSAO_SO_LEITURA_RECUSA_ESCRITA     SIM
REPAROS_MANUAIS_ANTES_DA_CONFERENCIA 0
```

As **29 SKIP com `HASH=MATCH` e zero reaplicações** são o que mais diz: o
livro-razão voltou coerente com os ficheiros do repositório, e o aplicador
canónico opera o banco restaurado sem tocar em nada.

E as oito travas foram **mordidas**, não contadas — as oito recusaram:

`CHECK forward_identificado_exige_identidade` ·
`PK sala_de_espera (run_id, ordem)` ·
`FK sala_de_espera -> collection_run` · `FK sala_de_espera -> raw_asset` ·
`CHECK consumo_diz_quem_e_quando` · `CHECK corrida_sha_tem_formato` ·
`PK participacao_na_derivacao` · `FK etapa_da_corrida -> collection_run`

A conferência corre dentro de `begin read only`, e a recusa do servidor é
**conferida** antes de se acreditar nela — conserto não foi apenas não-feito,
foi **impossível**.

```
PEDIR NAO E OBTER.
```

---

## 7 · O ACHADO MAIS PERIGOSO

Medido, e é a coisa mais importante que esta missão descobriu:

| alvo pedido | o que o PostgreSQL faz |
|---|---|
| **à frente** do WAL disponível | `FATAL`, e **não** promove |
| **atrás** do início do backup | **PROMOVE, calado**, no estado do backup |

No segundo caso o servidor escreve *«database system is ready to accept
connections»*, o `exit` é `0`, e o banco entregue está **silenciosamente
atrasado**, sem nunca dizer que não chegou onde lhe pediram.

```
EXIT 0 E «READY TO ACCEPT CONNECTIONS» NAO SAO PROVA
DE QUE O RESTAURO CHEGOU AO INSTANTE PEDIDO.
```

Quem confiasse no arranque do servidor levava um banco atrasado para
produção. Quem defende é o **marco pós-backup** do `§5`.

---

## 8 · INTERRUPÇÃO, RTO E RPO

```
MORTO_DURANTE_A_REPRODUCAO      SIM   (kill -9 a meio)
ESTADO_INTERMEDIO_UTILIZAVEL    NAO   <- e isto e a boa noticia
PODE_SER_RETOMADO               SIM
PRECISA_REINICIAR_DO_ZERO       NAO
IMPRESSAO_IGUAL_AO_RESTAURO_LIMPO  SIM
COMO_SABEMOS_QUE_TERMINOU       pg_is_in_recovery() = f
```

```
DISPOSABLE_RTO_SEGUNDOS   0.55
DISPOSABLE_RPO_SEGUNDOS   2.22
```

> **Estes números são da bancada e só dela.** O LIVE tem outro tamanho, outra
> rede e outro orquestrador. Medir não é prometer.

---

## 9 · CONTRAPROVA E RED TEAM

```
CONTRAPROVA        13 sabotagens, 13 ACUSOU
ARENA_INTACTA      SIM   (o DDL corre em transacao e e desfeito)
RED_TEAM_ATTACKS   28
RED_TEAM_SURVIVORS 0
```

Três ataques sobreviveram à primeira corrida e **cada um apontou um defeito
real desta prova**, não do restauro:

| ataque | o que ele ensinou |
|---|---|
| `A02` | o servidor **promove** com alvo impossível → nasceu o marco pós-backup |
| `A03` | a defesa é diferente nos dois sentidos do alvo → ver `§7` |
| `A12` | `setval` **não é transaccional**: sabotar a arena para testar a regra deixaria a arena sabotada. E `raw_asset_id_seq` valia `1`: «pô-la em 1» não é pô-la para trás — uma sabotagem que não sabota mede o nada e diz PASS |

O `A23` é o que fecha o portão desta missão:

```
A23 · restore de banco local tratado como prova de Supabase   APANHADO
      o portao exige SAME_PLATFORM_RESTORE = YES, e esta missao NAO o tem
```

---

## 10 · O LIVE — somente leitura, e nem isso foi preciso

```
LIVE_READS   0
LIVE_WRITES  0
LIVE_DDL     0
```

Não houve leitura do LIVE porque **não há por onde**: nenhuma credencial
existe nesta sessão.

```
SUPABASE_ACCESS_TOKEN      AUSENTE
SUPABASE_MANAGEMENT_TOKEN  AUSENTE
SUPABASE_DB_URL            AUSENTE
SUPABASE_SERVICE_ROLE_KEY  AUSENTE
WORKFLOW_QUE_PRODUZ_BACKUP NENHUM
```

Capacidade e prova, separadas de propósito:

```
LIVE_BACKUP_CAPABILITY   PROVIDER_PHYSICAL (politica do plano, lida em documentacao)
LIVE_BACKUP_ENABLED      NOT_MEASURED
LIVE_BACKUP_EXISTS       NOT_MEASURED
PITR_STATUS              NOT_MEASURED
LATEST_BACKUP_AVAILABLE  NOT_MEASURED
RETENTION_WINDOW         NOT_MEASURED
RESTORE_EXECUTED         NO   (no LIVE)
RESTORE_VERIFIED         NO   (no LIVE)
```

```
POLITICA DA PLATAFORMA PROVADA != ESTE BACKUP EXISTE, E E DESTE INSTANTE.
```

---

## 11 · HARD STOP — O RECURSO QUE FALTA

Provar a **plataforma** exige um projeto Supabase descartável da mesma
classe do LIVE. Backup físico e PITR são do plano **Pro**. Não existe
projeto sandbox autorizado, e esta prova **não gasta**.

```
RESOURCE_REQUIRED   um projeto Supabase DESCARTAVEL em plano Pro, OU
                    uma credencial de gestao (SUPABASE_ACCESS_TOKEN) do
                    projeto actual, para LISTAR e DATAR os backups
EXPECTED_COST       plano Pro: ~25 USD/mes por projeto (confirmar no ecra;
                    esta sessao nao consultou preco). A credencial de
                    gestao NAO custa nada.
WHY_REQUIRED        so um restauro executado PELA PLATAFORMA move
                    SAME_PLATFORM_RESTORE de NO para YES. Nenhuma prova
                    local, por mais forte, atravessa essa linha — e o
                    ataque A23 existe para garantir que nao atravessa.
```

**Há um passo intermédio que não custa nada** e que já apertaria muito o
veredito: com uma credencial de gestão do projeto actual, esta casa
conseguiria **listar e datar** os backups — movendo `LIVE_BACKUP_EXISTS`,
`PITR_STATUS`, `LATEST_BACKUP_AVAILABLE` e `RETENTION_WINDOW` de
`NOT_MEASURED` para medidos, sem escrever nada e sem restaurar nada.

---

## 12 · PRE-FLIGHT PARA A 031 — sem aplicar nada

A `031` **só cria**: uma tabela nova, três índices, comentários. Não altera
nem apaga nenhuma tabela existente.

```
MIGRATION_031_DEFECT = NO
```

Lida inteira e aplicada com sucesso na bancada. A chave `(run_id, ordem)`
está certa: `item_id` pode valer `"?"` e repetir-se dentro da mesma corrida,
e a própria migration documenta porquê.

### ⚠️ A 031 NÃO PODE SER A PRÓXIMA A ENTRAR

O retrato do LIVE (`PREFLIGHT-LIVE-READONLY-V1`) diz que o livro-razão de lá
tem `001`–`007` e `009`–`027`. **Faltam a `028`, a `029` e a `030`.** A `031`
referencia `collection_run` e `raw_asset`, que existem — mas a cadeia
canónica é uma **ordem**, e saltar três migrations não é uma opção.

```
APLICAR A 031 ANTES DA 028/029/030 E APLICAR FORA DA CADEIA.
```

### A sequência segura, quando houver autorização

```
1. BACKUP/PITR CHECK
   [ ] a consola mostra ponto de recuperacao que cobre AGORA
   [ ] a janela de retencao esta escrita, com data
   [ ] o runbook de recuperacao esta lido e o projeto confirmado (§9 dele)

2. CURRENT LIVE SCHEMA CHECK
   [ ] `provas/auditoria_live.sh` corrido HOJE, em begin read only
   [ ] LEDGER sem duplicados, sem sha em falta, sem drift
   [ ] nenhuma versao no LIVE que nao exista no repositorio

3. EXPECTED PRE-MIGRATION STATE
   [ ] ledger = 001-007, 009-030   <- as tres pendentes ja aplicadas
   [ ] `public.sala_de_espera` NAO existe
   [ ] `collection_run` e `raw_asset` existem
   [ ] a coleta esta PARADA

4. APPLY 031
   [ ] por `motor/cadeia_canonica.sh migrations`, e por nenhum segundo
   [ ] --single-transaction: entra inteira ou nao entra

5. POST-APPLY VALIDATION
   [ ] ledger ganhou UMA linha: 031, com o sha de cima
   [ ] a tabela existe, com 3 indices e as travas da migration
   [ ] as travas MORDEM (provocar, nao contar)
   [ ] conferencia 008 = PASS

6. CANARY
   [ ] UMA corrida, UM item, e depois PARAR
   [ ] a linha pousa com estado WAITING
   [ ] a transicao para CONSUMED exige autor e hora

7. AUDIT
   [ ] `auditoria_live.sh` outra vez, e o retrato datado
```

### E o caminho para a frente, que não é um restauro

```
FORWARD_RECOVERY_PLAN (031):
    drop table public.sala_de_espera;
    delete from public.schema_migracao where versao='031';
```

Barato, porque a `031` não toca em nada que já existisse. **Isto é rollback,
e rollback não é restore** — ver `§8` do runbook.

---

## 13 · VEREDITOS

```
RESTORE_PROOF            = BLOCKED
LIVE_RECOVERY_CAPABILITY = NOT_MEASURED
READY_FOR_LIVE_APPLY     = NO
MIGRATION_031_DEFECT     = NO

LIVE_READS               = 0
LIVE_WRITES              = 0
LIVE_DDL                 = 0
MIGRATION_031_APPLIED    = NO
REAL_COLLECTION          = 0
```

E o que **está** provado, com o nome certo:

```
PHYSICAL_CLASS_RESTORE      PASS
SAME_CLASS_RESTORE          YES     (era NO na V1)
SAME_PLATFORM_RESTORE       NO
PLATFORM_RESTORE_EXERCISED  NO
DISPOSABLE_RESTORE          PASS
COUNTERPROOF_WORKS          YES
RED_TEAM_SURVIVORS          0
BLOCKER                     PLATFORM_RESTORE_NOT_EXERCISED
```

> **UM BLOQUEIO MEDIDO HONESTAMENTE NÃO É UMA FALHA DA MISSÃO.**
> **UM VERDE SEM AS PROVAS TODAS É UMA MENTIRA DA MISSÃO.**

`RESTORE_PROOF` é `BLOCKED` e não `PASS` por uma razão que o portão executa,
e não por cautela: o mecanismo que uma emergência do LIVE usaria é o
**Restore da plataforma**, e esse não foi exercido.

```
ONE RECOVERY PLAN -> ONE PROOF.
```

`LIVE_RECOVERY_CAPABILITY` é `NOT_MEASURED` e não `BLOCKED` porque não se
mediu nada do lado do LIVE — declarar `BLOCKED` seria afirmar que se olhou e
se viu que falta.

---

## 14 · O QUE ESTA MISSÃO NÃO FEZ

- não aplicou a `031` — nem no LIVE nem em lado nenhum que conte como LIVE;
- não escreveu, leu, criou nem alterou nada no LIVE;
- não reescreveu a `031` (ela pertence à missão da Sala);
- não tocou em Collection, Portal, Intelligence, SCRAP nem no legado italiano;
- não exportou corpus real;
- não criou recurso pago;
- não promoveu `SEC-015`, que continua a exigir um backup **do LIVE**
  restaurado uma vez, datado;
- não fez merge para lado nenhum.
