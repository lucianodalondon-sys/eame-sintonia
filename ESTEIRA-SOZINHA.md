# ESTEIRA-SOZINHA — o que faltava pro SINTONIA rodar sozinho, e o que foi ligado

> Pergunta do dono (27/09 21:35): **«o que falta pro sintonia rodar todo sozinho?»**
> Base: produção **`a2aa73f42`** (`origin/servico-20260923-0923`, rebase de 28/09). Ramo: `claude/autonomous-pipeline-closure-rebase-h6fxjn`
> (a entrega anterior era `claude/autonomous-pipeline-6s66x9` @ `8be5e3405`, sobre `b273660b6`).
> Offline: nenhum site externo, nenhum livro vivo tocado. Tudo é **extensão do supervisor** que já roda
> (`curadoria/supervisor.py`, tarefa SINTONIA-Arranque). Não existe segundo orquestrador.

```
REBASE    sobre a2aa73f: conflito SÓ em gerados (13 system-map/*.generated.json, o state do cliente,
          CENSO-DAS-LIGACOES) -> ficou a produção e o mapa foi REGERADO pela cadeia. Código: 0 conflitos.
COMMITS   de83e54 · dbd9860 · a6fe6df · 7c704e2  (a entrega anterior, rebaseada)
          35aa769  FECHO: porta que falha · retenção · READ_ONLY em qualquer SO · harness CRLF
          c1ce36c  mapa regerado  (+ este relatório e o mapa de novo: SHA final no fim da entrega)
TESTES    tests/test_esteira_sozinha.py 47/47 + tests/test_harness_mutacao_esteira.py 1/1
          bateria inteira por NOME, a2aa73f × ramo: ver §5
MUTAÇÃO   44/44 mortos em LF · 44/44 com os alvos em CRLF e o teste de shebang desligado (Windows simulado)
E2E       PASS num PostgreSQL 16 descartável, agora com a porta a falhar de verdade (Sala morta) e a poda
MAPA      REGERAR → VALIDAR = SYSTEM_MAP_CHECK=PASS · --conferir-carimbo = IGUAL
```

---

## 1 · Por que documento novo não vira item da Sala (R03: raw +5, derived +5, Sala +0)

**A passagem não é um passo manual esquecido.** Na rodada, a porta corre **dentro da mesma corrida**:

```
rodadas.py → onda_web.py → micro_coleta.correr → orquestrador.correr()
   RAW (pela_entrada) → DERIVED → STRUCTURED → pela_porta()        orquestrador/orquestrador.py:1169-1211
   pela_porta: decidir → escrever o livro → só SIM → espera.pousar   orquestrador/orquestrador.py:771-785
```

Então o `+0` vem de uma de quatro causas, todas no código:

| | causa | onde |
|---|---|---|
| **A** | **universo sem régua → `NAO_SE_APLICA` sempre.** A régua conhece `T1 T2 T3 T4 T5 T7 T9 T10`. A coorte congelada tem **13 fontes T8 e 6 T12**, e `micro_coleta.plano` não pergunta se o universo tem régua | `admissao/admissao.py:859`, `:996`; `scripts/micro_coleta/micro_coleta.py:120-127` |
| B | veredito `NAO` / `NAO_SEI` (capa, uma palavra só, língua sem régua) | `admissao/admissao.py:586-990` |
| C | dedup da Sala: SIM, mas o documento já estava lá por outra corrida → `REUSED`, 0 linhas | `admissao/sala_de_espera.py:810-843` |
| D | a corrida caiu no `pousar` (conflito / Sala indisponível) depois de gravar RAW | `admissao/sala_de_espera.py:861-871` |

**O que aponta para A na R03:** a Rodada 3 do plano da 4.ª onda é **IT-T8-021 (edagricole) + IT-T7-135 (cia.it)**
(`ferramentas/big_collection/onda4/ORDEM-RENDIMENTO-ONDA4.md`, «Rodada 3»). São duas corridas, como o
`collection_run +2` medido. T8 não tem régua. E **toda rodada da 3 em diante leva uma T8 da edagricole**.
Medido no código, e não por palpite: `admissao.decidir(item, "T8")` → `NAO_SE_APLICA` («nao ha regra escrita
do que conta como «T8»»). O teste `test_t8_e_t12_nao_tem_regua_na_admissao` fixa isso.
**Se foi A, B, C ou D na R03 real: NÃO SEI daqui.** O livro de decisões e o `RELATORIO-PASSAGEM.json` da
rodada estão na máquina do coordenador. A partir de hoje, o vigia e o `--plano` dizem isso sozinhos.

## 2 · O que foi ligado (três passos do supervisor, nesta ordem, a cada volta)

| passo | ficheiro | o que faz |
|---|---|---|
| **PASSAGEM** | `admissao/passagem_para_a_sala.py` | Para cada corrida **reconciliada** (fechada no livro de corridas **e** com observações no livro de observações) que ainda **não passou pela porta**, leva a colheita à **porta canônica**: `italy_executor.colher` refaz o envelope e `orquestrador --so-a-porta --colheita-da-corrida=<RUN_ID>`, com o pedido de `micro_coleta.comando()` (o mesmo da rodada). Antes de gravar, faz o backup **PROVA_VALE** (`provar_backup_da_sala.provar`), `:298`. Há **um só escritor** (`sala_de_espera._Trava`), `:277`, e `PARAR.flag` é respeitado antes e entre corridas, `:250`, `:307`. **Porta que falha não passou** (§2-bis). **Não passa, e diz o porquê:** universo sem régua (T8/T12), corrida com várias fontes, corrida aberta, passado anterior a `PAS_DESDE`. |
| **INTELLIGENCE** | `admissao/gatilho_da_inteligencia.py` | Pergunta à Sala, só com SELECT e de 5 em 5 min, quantos READY pousaram depois da última tentativa. A regra: **10 novos OU ≥1 novo esperando há 4 h**, `decidir()` `:131`. O **trinco** está em `:246`. A corrida usa o **motor que já existe**: backup → **cópia descartável** (PROVA_VALE) → export read-only **da cópia** (RUNBOOK-R7 §2, `READ_ONLY=on` conferido, `exportar()` `:160`) → `motor_das_capacidades.rodar` → `pote_intelligence_casco` → **fiscal `validar_pote_v2` sobre o ficheiro candidato**. Só se o fiscal disser PASSA há `os.replace` para `italia-portale/client/sintonia-pote.js`, `subir_o_pote()` `:202`, `:221`. Um pote reprovado **não sobe**: fica guardado com as violações. Depois de falha há recuo de 30 min. |
| **VIGIA** | `medidas/vigia_da_esteira.py` | De hora a hora escreve `curadoria/ESTEIRA-SAUDE.json` (e uma linha em `ESTEIRA-SAUDE-HISTORICO.ndjson`) com a última vez que cada etapa andou. **ALERTA** quando uma etapa passa de N horas **ou quando não se sabe** quando ela andou. |
| gancho | `curadoria/supervisor.py` `_passos_da_esteira`, `_hook_esteira` | Quem liga é **o serviço**, no `main()`: por omissão, `esteira=True`. Se `_loop` for chamado sem `esteira=True` (os testes), os passos não correm. `--sem-esteira` desliga. Um passo que rebenta fica no diário (`ESTEIRA_ERRO`) e não derruba o supervisor. |

**N por etapa (declarado em `medidas/vigia_da_esteira.py::ETAPAS`)**

| etapa | lida de | N |
|---|---|---|
| fonte | batimento do worker | 24 h |
| coleta | maior `FINISHED_AT` nos livros de corridas (árvore + `ITALY_OPS_ROOT`) | 26 h (D86: 24 h + folga) |
| agendador | última linha do `logs/runs.log` da tarefa ForwardOnly (e aviso se a trava existe) | 2 h |
| passagem | `PAS_VERIFICADO_EM` | 1 h |
| sala | `max(pousado_em)` | 48 h |
| intelligence | `INT_ULTIMA_CORRIDA_EM` | 24 h |
| pote | `INT_ULTIMA_SUBIDA_EM` | 24 h |
| portal | mtime de `italia-portale/client/sintonia-pote.js` | 24 h |
| portal público (D126) | — | **NÃO SEI**: medir exige rede, e o vigia não sai para a rede |

Pequenas mudanças de apoio, declaradas:

- `scripts/micro_coleta/provar_backup_da_sala.py` virou a função `provar()`, e o CLI continua igual. Ela também **devolve `SINTONIA_SALA_DSN` ao ambiente**. Antes a prova apagava essa variável e não a repunha: dentro do serviço, a escrita seguinte perderia a Sala. O `pg_restore` passou a funcionar fora do Windows.
- `scripts/micro_coleta/ensaio_offline.py`: `PG_BIN` agora lê `SINTONIA_PG_BIN`, quando existe.
- **O gatilho mora em `admissao/` e não em `motor/`.** Na primeira versão ele estava em `motor/`, e a bateria apanhou o erro: `test_system_map::a_coleta_nao_conversa_com_o_motor_as_centenas` subiu de 12 para 14. O motor passava a abrir a Sala (`sala_de_espera`, `cliente_postgres`), o contrário do que o motor declara. **O teste não foi mexido.** A peça foi para ao lado do dono da Sala, porque ela decide **quando a espera acaba** e entrega uma **cópia** ao motor, sem analisar nada.

## 2-bis · FECHO (28/09): o que o verificador independente mandou corrigir

| # | defeito / pedido | o que mudou | onde |
|---|---|---|---|
| 2 | **a porta falha e a corrida fica marcada como passada.** `CODIGO=1` (SalaIndisponivel) → 1.ª volta `PASSOU` com STATUS «NAO SEI», 2.ª volta `NADA_A_PASSAR`, para sempre | Só passou quem voltou com `CODIGO 0` **e** a linha `CORRIDA <STATUS> · <RUN>` (`passou_pela_porta`). O resto é **FALHA**: não entra em `PAS_PASSAGENS`, fica em `PAS_FALHAS` com a causa (stderr da porta) e as tentativas, e `PAS_ULTIMA_FALHA_EM` anda (recuo de 30 min da passagem inteira). A corrida volta a ser tentada com **recuo próprio**: 30 min × 2^(tentativas−1), teto de 6 h. No plano, aparece como `RECUO_DEPOIS_DE_FALHA_DA_PORTA`. Uma porta que rebenta (exceção) também é falha e não derruba a volta. A ação diz `FALHOU` / `PASSOU_COM_FALHAS` / `PASSOU`. O vigia alerta `FALHA_NA_PORTA` enquanto `PAS_FALHAS` não esvaziar | `admissao/passagem_para_a_sala.py:126`, `:133`, `:194`, `:312`, `:317`, `:322`, `:334` · `medidas/vigia_da_esteira.py:205` |
| 3 | **disco**: cada passagem e cada corrida da Intelligence deixava ~50–54 MB em `curadoria/esteira/*/<hora>/backup/pg` | Retenção **declarada** em `provar_backup_da_sala.podar` (o dono do formato do backup). Por pasta (`passagem/`, `intelligence/`) **ficam inteiras**: a **em curso** (sempre, mesmo que o nome não seja o mais novo), as **3 mais novas** (`GUARDAR_BACKUPS`), e a **mais nova com PROVA_VALE**. As outras perdem **só o pesado** (`backup/pg`, o dump, `EXPORT-DA-COPIA.json`, que tem texto da Sala). O recibo `PROVA-BACKUP-SALA.json` fica sempre. A poda corre **depois** do trabalho, **dentro** da trava/trinco. Se a poda rebentar, fica escrito em `PAS_ULTIMA_PODA` / `INT_ULTIMA_PODA` e a passagem não é desfeita. Teto de disco: ~4 × 54 MB por pasta | `scripts/micro_coleta/provar_backup_da_sala.py:110`, `:123`, `:139`, `:142` · `admissao/passagem_para_a_sala.py:284` · `admissao/gatilho_da_inteligencia.py:253` |
| 4a | a guarda do `READ_ONLY` só era provada fora do Windows (`skipIf nt`, psql em shebang) → **E12 sobreviveu no Windows** | Nova prova **independente do SO**: `subprocess.run` dublê que escreve o export no `-o`. Confere também o comando (`begin transaction read only`, DSN por último) e o `PGOPTIONS`. `off`, `None` e `ON` são recusados. O teste de shebang continua como prova extra fora do Windows. **Provado**: com o shebang desligado (Windows simulado), E12 e E43 morrem por este teste | `tests/test_esteira_sozinha.py:183` · `provas/esteira_sozinha/MUTANTES-CRLF-WINDOWS-SIMULADO.json` |
| 4b | mutantes com alvo de várias linhas falhavam em CRLF (`autocrlf=true`) | `aplicar()` procura o alvo no texto em LF e devolve o mutante com as quebras **originais**. O restauro continua byte a byte, conferido por SHA-256. Medido: o harness antigo dava `ALVO_NAO_UNICO (0)` em **16** alvos em CRLF; o novo dá 44/44. `tests/test_harness_mutacao_esteira.py` confere cada alvo em LF e CRLF, **fora** da bateria que o harness corre (lá dentro ele mataria todo mutante sozinho e esconderia teste em falta: aconteceu na primeira tentativa, e foi por isso que saiu) | `provas/esteira_sozinha/mutantes.py:147` |
| 5 | `ENTITY_SOURCE` (objeto no motor × string no schema `POTE_INTELLIGENCE_CASCO-v2`) | **Não mexido.** É decisão do dono do pote, já pedida. O gatilho continua a recusar (`POTE_REPROVADO`, nada sobe), e isso está escrito no próprio gatilho | `admissao/gatilho_da_inteligencia.py:48` · §4.1 |

**Mutantes novos** (todos mortos): E27 porta falha e é marcada passada · E28 «passou» = qualquer recibo · E29 falha sem `PAS_ULTIMA_FALHA_EM` (loop apertado) · E30 falha sem causa · E31 corrida falhada nunca volta · E32 sem recuo por corrida · E33 recuo sem teto · E34 porta que rebenta derruba a volta · E35 **retenção apaga o backup em curso** · E36 retenção apaga a última PROVA_VALE · E37 retenção apaga o recibo · E38 retenção não poda (o disco cresce) · E39 guarda N−1 · E40/E41 passagem/Intelligence não podam · E42 poda **antes** da corrida · E43 export sem a transação só-leitura · E44 vigia cala a porta que falha.

## 3 · Provas

**Ensaio de ponta a ponta sem rede** (`provas/esteira_sozinha/ensaio_ponta_a_ponta.py`). Corre numa cópia da árvore, com PostgreSQL 16 descartável e **34 migrations**. A coleta usada é a **real** que o repo guarda: corridas verbatim do `runs.ndjson`/`observations.ndjson` e bytes em `data/collection-store/`.

| passo | resultado |
|---|---|
| passagem com outra escritora a segurar a trava | `OCUPADO` |
| **FECHO** · passagem com a **Sala morta só no subprocesso da porta** (o backup vê a Sala viva) | `PASSOU_COM_FALHAS`: IT-T10-018 → **CODIGO 1**, `psql: … port 9 failed: Connection refused` em `PAS_FALHAS`, **fora** de `PAS_PASSAGENS`; IT-T7-043 → CODIGO 0 (só NAO/NAO_SEI: a porta decide e não precisa da Sala, e isso é verdade). **Sala 0** |
| **FECHO** · 6 min depois | `RECUO_DEPOIS_DE_FALHA` (nem backup, nem porta) |
| **FECHO** · passado o recuo (+31 min), Sala de volta | `PASSOU`: IT-T10-018 **tentada outra vez** → **6 SIM**, 10 NAO, 14 NAO_SEI; `PAS_FALHAS` vazio; a corrida ForwardOnly → `VARIAS_FONTES` (fica) |
| armazém e Sala | raw 0→62 · storage_object 0→32 · derived 0→32 · collection_run 0→3 · **Sala 0→6**. Cada tentativa deixa o seu RAW e a sua `collection_run`, e os bytes deduplicam-se: é o rasto verdadeiro da tentativa que falhou |
| passagem outra vez | `NADA_A_PASSAR` (não repete) |
| **FECHO** · retenção (o ensaio declara `GUARDAR_BACKUPS = 1`) | o backup da falha perde `pg/` e o dump (**53.449.586 bytes**), e a pasta fica com 2.225 bytes, o recibo incluído. O da passagem em curso fica inteiro (54.263.529 bytes) |
| gatilho agora | `ESPERA`: `POUCOS_E_RECENTES (6 novos)` |
| segunda corrida da Intelligence com o trinco preso | `OCUPADO` |
| gatilho às +4 h | corre: cópia provada → motor → pote → fiscal: **`POTE_REPROVADO` → não sobe**, e o casco fica sem pote |
| gatilho depois | `SEM_DELTA` |
| vigia | escreveu; `ALERTA=true` (fonte, agendador, pote e portal em NÃO SEI no ensaio; coleta PARADA desde 22/09) |

**O ensaio apanha o defeito antigo:** com E27 plantado (porta que falha = passada), o mesmo ensaio dá **FAIL**. A 1.ª volta diz `PASSOU`, a 2.ª `NADA_A_PASSAR`, e a **Sala fica em 0 para sempre** (`provas/esteira_sozinha/ENSAIO-MUTANTE-E27-PORTA-FALHA-MARCADA-PASSADA.json`). É o achado do verificador, reproduzido com Postgres de verdade.

**Mutação** (`provas/esteira_sozinha/mutantes.py`): **44/44 mortos**, ficheiros restaurados byte a byte. Também **44/44** numa cópia com os 6 ficheiros-alvo em **CRLF** e o teste de shebang desligado (`MUTANTES-CRLF-WINDOWS-SIMULADO.json`).
Os mutantes simulam: duas corridas sobrepostas (Intelligence e passagem), Admission sem backup (duas formas), gatilho sem delta, limiar 10→1, regra das 4 h, delta não medido virando zero, marca que não anda, sem recuo, pote reprovado que sobe, export sem READ_ONLY, cópia sem PROVA_VALE, PARAR.flag ignorado (duas formas), universo sem régua, repetição, passado que atravessa sozinho, várias fontes, e o **vigia calado** (quatro formas). Há ainda três mutantes do gancho do supervisor.

## 4 · Achados que precisam de decisão (não mudei, e o porquê)

1. **O pote de hoje nunca sobe.** *(FECHO 28/09: continua igual, de propósito. Motor e schema não foram tocados; a decisão já foi pedida ao dono do pote.)* O motor escreve `ENTITY_SOURCE` como **objeto** (D112: valor, origem e itens), e o contrato do pote v2 exige **string** (`docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json:48`). Medido: 7 violações na fixture R7 e 1 no ensaio real. O gatilho faz o certo: não sobe. Quem decide o contrato é o **dono do pote**; afrouxar o fiscal ou achatar o motor aqui seria comprar o verde com a lei.
2. **T8 e T12 colhem sem régua na Admissão.** Isso gasta pedidos que nunca chegam à Sala, e toda rodada da 3 em diante tem uma T8. Há duas saídas: escrever a régua (a lei não se inventa aqui) ou fazer o plano pular a fonte. A passagem já não as leva à porta (`SEM_REGUA_NO_UNIVERSO`, à vista no plano e no vigia).
3. **Corridas de várias fontes (a tarefa ForwardOnly) não atravessam pela passagem**, porque a porta pergunta **um** universo por corrida. Julgar um T3 como T7 escreveria um NAO falso no livro. Separar por fonte exige envelope por fonte, e isso é decisão do dono.
4. **Na Sala real, o motor pode recusar o corte.** `motor_das_capacidades.rodar` levanta `LeiViolada` se o corte tiver `ITEM_ID` repetido (`motor/motor_das_capacidades.py:753-754`). Nesse caso o gatilho registra `MOTOR_ERRO` no diário, recua 30 min, e o vigia alerta a etapa `intelligence` parada. Se isso acontece na Sala real: **NÃO SEI** até a primeira corrida lá.
5. **D90-5 não está escrita no repo.** Li «+4 h» como «o READY novo mais velho já espera 4 h». Se for «4 h desde a última corrida», muda-se só `decidir()`.

## 5 · Testes — antes/depois, pelo NOME

`provas/integra_noite/bateria_inteira_por_nome.py`, com rede fechada, base `b273660` × ramo `b3993b8` (código final + mapa):

| | base `b273660` | ramo `b3993b8` |
|---|---|---|
| ficheiros de teste | 411 | 412 (+`tests/test_esteira_sozinha.py`, 36/36) |
| testes corridos | 7.940 | 7.976 |
| ficheiros vermelhos | 77 | 77 (os mesmos) |
| falhas por nome | 338 | 338 |
| **falhas novas / sumidas** | | **0 / 0** |

Os resultados estão em `provas/esteira_sozinha/BATERIA-ANTES-b273660.json` e `BATERIA-DEPOIS-b3993b8.json`. Na comparação, os **números dentro do texto** de cada falha foram normalizados. `test_cadeia_declara_io::o_MEDIDO_VARRE_declarado_bate_com_a_corrida` já falha na base e escreve no próprio nome quantos ficheiros o scanner mediu, e a árvore ganhou ficheiros. É a mesma falha, com outra contagem.
A **primeira** bateria `depois` (`b253c65`) apanhou uma falha nova real: `a_coleta_nao_conversa_com_o_motor_as_centenas`. Ela foi consertada mudando o gatilho de gaveta, e o teste não foi mexido (§2).
Os 3 vermelhos de `curadoria/test_supervisor.py` (tasklist/wmic do Windows) já falham igual na base.

## 6 · SINTONIA-Italy-ForwardOnly — deve existir? (proposta; nada apagado)

- **Ainda deve existir.** É o **agendador canônico** da coleta forward (`docs/biblia/CENSO-DA-INFRAESTRUTURA.md:36-42`, `BIBLIA-CANONICA-DA-COLETA.md:2465-2470`, `REFERENCIA-MANUTENCAO.md:15`). O «vivo» (supervisor + ciclo_continuo) é o **robô de fontes** e **não chama o coletor**. O `rodadas.py` é manual e escreve noutro livro. Nenhuma decisão no repo a retira.
- **O «0 com runs.ndjson parado em 23/09» não prova que ela trabalha.** Ela só escreve em `runs.ndjson` quando coleta de verdade, às 20 h de Roma (`coleta/italy_recurrent_collect.mjs:122-129`). Em todas as outras horas sai com 0. O suspeito nº 1 é a **trava órfã** `C:\eame-sintonia-ops\.italy-forward-only.lock`: não tem PID nem idade (`:66-69`, `:112-117`, só se apaga no `finally` `:373`). Se o processo morrer, por exemplo pelo limite de 30 min ou por reboot, cada tique seguinte devolve `SKIPPED_LOCK_HELD` com 0, para sempre. Isso **já aconteceu** de 07/09 a 21/09: foram 343 tiques (`RELATORIO-CUTOVER.md:131-157`).
- **Proposta:**
  - (a) ler `C:\eame-sintonia-ops\data\collection-ledger\italy\logs\runs.log` e ver se a trava existe;
  - (b) se estiver órfã e nenhum `node` estiver rodando, o coordenador a remove;
  - (c) dar à trava PID e idade, que é missão do dono do coletor;
  - (d) o vigia já mostra a etapa `agendador` (N = 2 h) e avisa `TRAVA PRESENTE`.

## 7 · Instalar (na máquina do bot; Windows)

```powershell
cd <arvore do bot>                                   # a mesma do supervisor
git fetch origin servico-20260923-0923 claude/autonomous-pipeline-closure-rebase-h6fxjn
git rev-parse HEAD                                   # tem de dar a2aa73f42... (a produção de hoje)
git merge-base --is-ancestor HEAD origin/claude/autonomous-pipeline-closure-rebase-h6fxjn && echo FF_OK
git merge --ff-only origin/claude/autonomous-pipeline-closure-rebase-h6fxjn   # sobre a2aa73f: fast-forward
# Se o HEAD NÃO for a2aa73f (a produção andou outra vez), NÃO force: é preciso outro rebase.

# o ambiente do SERVIÇO (a tarefa SINTONIA-Arranque) precisa das mesmas variáveis da rodada:
setx SINTONIA_SALA_BACKEND POSTGRES
setx SINTONIA_SALA_DSN       "<o de ~\sintonia-sala-italia\SALA_DSN.txt>"
setx SINTONIA_COLLECTION_DSN "<o mesmo DSN>"
setx SINTONIA_PSQL_EXE       "%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe"
setx SINTONIA_ARMAZEM_RAIZ   "%USERPROFILE%\sintonia-sala-italia\armazem"
setx ITALY_OPS_ROOT          "C:\eame-sintonia-ops"

# conferir SEM gravar nada:
py admissao\passagem_para_a_sala.py --plano          # o que passaria, e o que fica, e porque
py admissao\gatilho_da_inteligencia.py --medir          # o delta da Sala e a decisão (só SELECT)
py medidas\vigia_da_esteira.py                       # escreve curadoria\ESTEIRA-SAUDE.json

# reiniciar o supervisor (ele só carrega código novo ao arrancar): tarefa SINTONIA-Arranque
```

- **Na primeira volta**, a passagem grava `PAS_DESDE = agora`, e o histórico **não** atravessa sozinho. Levar o passado é decisão do coordenador: `py admissao\passagem_para_a_sala.py --plano --desde=<ISO>` mostra o que seria levado.
- **Se faltar variável:** a passagem registra `PRECONDICOES` no diário e não grava nada. O vigia continua, com a Sala em NÃO SEI.
- **Parar:** `curadoria\PARAR.flag` para tudo. `supervisor.py --sem-esteira` desliga só a esteira.
- **Desfazer:** `git reset --keep a2aa73f42` e reiniciar o supervisor. Nenhum livro vivo é escrito pela instalação.
- **Porta que falha:** a corrida fica em `PAS_FALHAS` no estado do supervisor, com a causa. O vigia mostra `FALHA_NA_PORTA`, e a passagem tenta outra vez sozinha (30 min, 1 h, 2 h … até 6 h entre tentativas). Não há nada a fazer à mão, a não ser tratar a causa, por exemplo a Sala em baixo.
- **Disco:** `curadoria\esteira\passagem\` e `curadoria\esteira\intelligence\` guardam no máximo ~4 backups inteiros cada (~54 MB cada). Os mais velhos ficam só com o recibo.
- **Ler a saúde:** `curadoria\ESTEIRA-SAUDE.json` → `ALERTA`, `ALERTAS[]`, `ETAPAS{}`, `PLANO_DA_PASSAGEM`, `ULTIMO_DELTA_DA_INTELLIGENCE`. Os eventos estão no diário do supervisor: `EVENTO=ESTEIRA`.

## 8 · Design

Nenhuma superfície visual foi tocada. O único artefato do casco é o mesmo `sintonia-pote.js`, e só se o fiscal disser PASSA.
`ADAMA_DESIGN_SYSTEM_MATCH = NAO SE APLICA` (sem UI).

## EM PALAVRAS SIMPLES

Hoje o robô de fontes já roda sozinho. O resto dependia de alguém apertar o botão. Agora o mesmo robô, a cada volta, faz mais três coisas:

1. **Leva o que foi colhido até a Sala.** Antes faz uma cópia de segurança e confere que ela volta, e deixa só um escritor por vez. Descobri por que a Sala não cresceu na rodada 3: metade daquela rodada era de um tipo de fonte (T8) para o qual a porta **não tem regra**, então ela sempre responde «não se aplica». Isso precisa de decisão sua.
2. **Liga a Intelligence sozinha** quando chegam 10 itens novos, ou quando um item novo espera 4 horas. Nunca roda duas vezes ao mesmo tempo. Só publica o resultado se o fiscal do pote aprovar. Hoje ele **não aprova**, porque o motor e o pote discordam num campo (`ENTITY_SOURCE`). Por isso nada sobe até o dono do pote decidir.
3. **Escreve um boletim de saúde de hora em hora** (`ESTEIRA-SAUDE.json`). Ele diz quando cada etapa andou pela última vez e grita quando uma parou, ou quando não dá para saber.

**O que mudou no fecho (28/09), depois do verificador:**

- **Se a porta da Sala estiver fechada**, a corrida não fica mais marcada como «passou». Antes ficava, e nunca mais era tentada: o item se perdia em silêncio. Agora ela fica numa lista de falhas, com o motivo, o boletim avisa, e o robô tenta outra vez sozinho, esperando cada vez mais entre as tentativas (meia hora, uma hora, duas… até seis). Provei isso com um banco de verdade: com a Sala desligada, nada entrou; quando a Sala voltou, os 6 itens entraram.
- **O disco não enche mais.** Cada passagem deixava ~50 MB de cópia de segurança para trás. Agora ficam só as 3 últimas, mais a última que se provou boa. A cópia da passagem que está rodando nunca é apagada.
- **As provas valem no Windows também.** Uma delas só rodava em Linux, e o teste de mutação se perdia com o fim de linha do Windows. As duas foram consertadas e provadas.
- **O pote continua sem subir.** Isso é de propósito: a discordância do campo `ENTITY_SOURCE` é decisão do dono do pote, e eu não mexi.

A tarefa ForwardOnly **deve continuar**. O «0» dela provavelmente é uma trava esquecida no disco, e o boletim passa a mostrar isso.
