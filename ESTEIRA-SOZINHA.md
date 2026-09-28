# ESTEIRA-SOZINHA — o que faltava pro SINTONIA rodar sozinho, e o que foi ligado

> Pergunta do dono (27/09 21:35): **«o que falta pro sintonia rodar todo sozinho?»**
> Base: produção `b273660b6` (`origin/servico-20260923-0923`). Ramo: `claude/autonomous-pipeline-6s66x9`.
> Offline: nenhum site externo, nenhum livro vivo tocado. Tudo é **extensão do supervisor** que já roda
> (`curadoria/supervisor.py`, tarefa SINTONIA-Arranque). Não existe segundo orquestrador.

```
COMMITS   1144e6e  código + provas        b253c65  mapa regerado
          (+ este relatório e o mapa regerado de novo: SHA final no fim da entrega)
TESTES    tests/test_esteira_sozinha.py 36/36 · bateria inteira por NOME: 0 falhas novas (§5)
MUTAÇÃO   26/26 mortos (provas/esteira_sozinha/MUTANTES.json)
E2E       PASS num PostgreSQL 16 descartável (provas/esteira_sozinha/ENSAIO-PONTA-A-PONTA.json)
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
| **PASSAGEM** | `admissao/passagem_para_a_sala.py` | Para cada corrida **reconciliada** (fechada no livro de corridas **e** com observações no livro de observações) que ainda **não passou pela porta**, leva a colheita à **porta canônica**: `italy_executor.colher` refaz o envelope e `orquestrador --so-a-porta --colheita-da-corrida=<RUN_ID>`, com o pedido de `micro_coleta.comando()` (o mesmo da rodada). Antes de gravar, faz o backup **PROVA_VALE** (`provar_backup_da_sala.provar`), `:245`. Há **um só escritor** (`sala_de_espera._Trava`), `:244`, e `PARAR.flag` é respeitado antes e entre corridas, `:217`, `:253`. **Não passa, e diz o porquê:** universo sem régua (T8/T12), corrida com várias fontes, corrida aberta, passado anterior a `PAS_DESDE`. |
| **INTELLIGENCE** | `admissao/gatilho_da_inteligencia.py` | Pergunta à Sala, só com SELECT e de 5 em 5 min, quantos READY pousaram depois da última tentativa. A regra: **10 novos OU ≥1 novo esperando há 4 h**, `decidir()` `:121-142`. O **trinco** está em `:236`. A corrida usa o **motor que já existe**: backup → **cópia descartável** (PROVA_VALE) → export read-only **da cópia** (RUNBOOK-R7 §2, `READ_ONLY=on` conferido, `:150-166`) → `motor_das_capacidades.rodar` → `pote_intelligence_casco` → **fiscal `validar_pote_v2` sobre o ficheiro candidato**. Só se o fiscal disser PASSA há `os.replace` para `italia-portale/client/sintonia-pote.js`, `:192-212`. Um pote reprovado **não sobe**: fica guardado com as violações. Depois de falha há recuo de 30 min. |
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

## 3 · Provas

**Ensaio de ponta a ponta sem rede** (`provas/esteira_sozinha/ensaio_ponta_a_ponta.py`). Corre numa cópia da árvore, com PostgreSQL 16 descartável e **34 migrations**. A coleta usada é a **real** que o repo guarda: corridas verbatim do `runs.ndjson`/`observations.ndjson` e bytes em `data/collection-store/`.

| passo | resultado |
|---|---|
| passagem com outra escritora a segurar a trava | `OCUPADO` |
| passagem, com backup **PROVA_VALE** | `PASSOU`: IT-T10-018 (30 obs.) → **6 SIM**, 10 NAO, 14 NAO_SEI; IT-T7-043 → 1 NAO, 1 NAO_SEI; a corrida ForwardOnly → `VARIAS_FONTES` (fica) |
| armazém e Sala | raw 0→32 · derived 0→32 · collection_run 0→2 · **Sala 0→6** |
| passagem outra vez | `NADA_A_PASSAR` (não repete) |
| gatilho agora | `ESPERA`: `POUCOS_E_RECENTES (6 novos)` |
| segunda corrida da Intelligence com o trinco preso | `OCUPADO` |
| gatilho às +4 h | corre: cópia provada → motor → pote → fiscal: **`POTE_REPROVADO` → não sobe**, e o casco fica sem pote |
| gatilho depois | `SEM_DELTA` |
| vigia | escreveu; `ALERTA=true` (fonte, agendador, pote e portal em NÃO SEI no ensaio; coleta PARADA desde 22/09) |

**Mutação** (`provas/esteira_sozinha/mutantes.py`): **26/26 mortos**, ficheiros restaurados byte a byte.
Os mutantes simulam: duas corridas sobrepostas (Intelligence e passagem), Admission sem backup (duas formas), gatilho sem delta, limiar 10→1, regra das 4 h, delta não medido virando zero, marca que não anda, sem recuo, pote reprovado que sobe, export sem READ_ONLY, cópia sem PROVA_VALE, PARAR.flag ignorado (duas formas), universo sem régua, repetição, passado que atravessa sozinho, várias fontes, e o **vigia calado** (quatro formas). Há ainda três mutantes do gancho do supervisor.

## 4 · Achados que precisam de decisão (não mudei, e o porquê)

1. **O pote de hoje nunca sobe.** O motor escreve `ENTITY_SOURCE` como **objeto** (D112: valor, origem e itens), e o contrato do pote v2 exige **string** (`docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json:48`). Medido: 7 violações na fixture R7 e 1 no ensaio real. O gatilho faz o certo: não sobe. Quem decide o contrato é o **dono do pote**; afrouxar o fiscal ou achatar o motor aqui seria comprar o verde com a lei.
2. **T8 e T12 colhem sem régua na Admissão.** Isso gasta pedidos que nunca chegam à Sala, e toda rodada da 3 em diante tem uma T8. Há duas saídas: escrever a régua (a lei não se inventa aqui) ou fazer o plano pular a fonte. A passagem já não as leva à porta (`SEM_REGUA_NO_UNIVERSO`, à vista no plano e no vigia).
3. **Corridas de várias fontes (a tarefa ForwardOnly) não atravessam pela passagem**, porque a porta pergunta **um** universo por corrida. Julgar um T3 como T7 escreveria um NAO falso no livro. Separar por fonte exige envelope por fonte, e isso é decisão do dono.
4. **Na Sala real, o motor pode recusar o corte.** `motor_das_capacidades.rodar` levanta `LeiViolada` se o corte tiver `ITEM_ID` repetido (`motor/motor_das_capacidades.py:753-754`). Nesse caso o gatilho registra `MOTOR_ERRO` no diário, recua 30 min, e o vigia alerta a etapa `intelligence` parada. Se isso acontece na Sala real: **NÃO SEI** até a primeira corrida lá.
5. **D90-5 não está escrita no repo.** Li «+4 h» como «o READY novo mais velho já espera 4 h». Se for «4 h desde a última corrida», muda-se só `decidir()`.

## 5 · Testes — antes/depois, pelo NOME

`provas/integra_noite/bateria_inteira_por_nome.py`, com rede fechada, base `b273660` × ramo `b253c65` (código + mapa):

BATERIA_AQUI

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
git fetch origin claude/autonomous-pipeline-6s66x9
git merge --ff-only origin/claude/autonomous-pipeline-6s66x9   # base b273660: fast-forward

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
- **Desfazer:** `git reset --keep b273660` e reiniciar o supervisor. Nenhum livro vivo é escrito pela instalação.
- **Ler a saúde:** `curadoria\ESTEIRA-SAUDE.json` → `ALERTA`, `ALERTAS[]`, `ETAPAS{}`, `PLANO_DA_PASSAGEM`, `ULTIMO_DELTA_DA_INTELLIGENCE`. Os eventos estão no diário do supervisor: `EVENTO=ESTEIRA`.

## 8 · Design

Nenhuma superfície visual foi tocada. O único artefato do casco é o mesmo `sintonia-pote.js`, e só se o fiscal disser PASSA.
`ADAMA_DESIGN_SYSTEM_MATCH = NAO SE APLICA` (sem UI).

## EM PALAVRAS SIMPLES

Hoje o robô de fontes já roda sozinho. O resto dependia de alguém apertar o botão. Agora o mesmo robô, a cada volta, faz mais três coisas:

1. **Leva o que foi colhido até a Sala.** Antes faz uma cópia de segurança e confere que ela volta, e deixa só um escritor por vez. Descobri por que a Sala não cresceu na rodada 3: metade daquela rodada era de um tipo de fonte (T8) para o qual a porta **não tem regra**, então ela sempre responde «não se aplica». Isso precisa de decisão sua.
2. **Liga a Intelligence sozinha** quando chegam 10 itens novos, ou quando um item novo espera 4 horas. Nunca roda duas vezes ao mesmo tempo. Só publica o resultado se o fiscal do pote aprovar. Hoje ele **não aprova**, porque o motor e o pote discordam num campo (`ENTITY_SOURCE`). Por isso nada sobe até o dono do pote decidir.
3. **Escreve um boletim de saúde de hora em hora** (`ESTEIRA-SAUDE.json`). Ele diz quando cada etapa andou pela última vez e grita quando uma parou, ou quando não dá para saber.

A tarefa ForwardOnly **deve continuar**. O «0» dela provavelmente é uma trava esquecida no disco, e o boletim passa a mostrar isso.
