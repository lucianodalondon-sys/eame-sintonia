# L2-DISPARADOR-INTELLIGENCE — o disparador automático SOMENTE-LEITURA da Intelligence

> **D140** (dono real, 28/09): *«Intelligence Owner constrói/conclui o disparador automático SOMENTE-LEITURA permitido pela
> TRAVA: detectar material novo → snapshot/cópia segura da Sala → rodar motor → gerar cruzamentos → produzir pote
> canônico. consumido_em é outra decisão — não misturar.»*
> Ramo `claude/l2-disparador-v1`, nascido sobre a produção **`fd8c94698`** e juntado com a produção atual **`852ec0f0b`** (`origin/servico-20260923-0923`, §6-bis).
> Red team: *«não criar outro disparador; integrar seletivamente a ESTEIRA sobre fd8c94698; f85b4138a NÃO é ancestral de
> fd8c94698 — enxerto cego pode perder peças; DSN no arranque»*.

```
ENSAIO     DISPARADOR_INTELLIGENCE = PASS (Postgres descartável, 15/15) · POTE_NOVO_GERADO_SEM_MAO_HUMANA = FAIL (ENTITY_SOURCE)
MUTAÇÃO    47/47 mortos · ficheiros restaurados byte a byte · italia-portale/ igual no fim (provas/l2/MUTANTES.json)
TESTES     tests/test_disparador_intelligence.py 59/59 · tests/test_harness_mutacao_l2.py 2/2
R9        OBJETOS_LIBERADOS_AUTO = 0 (manual = 2) · GERADOR_CANONICO = FAIL — provas/l2/R9-AUTO-VS-MANUAL.md
ESTADO    D152: código pronto, NÃO agendado, NÃO instalado. Isto prova o DISPARADOR, não o laço até à tela.
BATERIA    por nome, base 852ec0f0b (produção atual) × ramo e76f695aa: 7.492 → 7.553 testes, 166 → 166 falhas · NOVAS 0 · SUMIDAS 0
MAPA       REGERAR → VALIDAR = SYSTEM_MAP_CHECK=PASS · --conferir-carimbo = IGUAL (sobre a junção com 852ec0f0b)
```

---

## 1 · O que entrou da ESTEIRA, o que ficou de fora, e porquê

**Não é um disparador novo.** É o gatilho da ESTEIRA-SOZINHA (`f85b4138a`) trazido **ficheiro a ficheiro**.
`f85b4138a` não é antepassado de `fd8c94698`, mas a **base** dele (`a2aa73f42`) é (`git merge-base --is-ancestor` → sim;
16 commits de produção no meio: D124 teto adaptativo e C6-REPETIDO). Medido antes de trazer:
**nenhum** dos ficheiros que a esteira toca mudou na produção entre `a2aa73f42` e `fd8c94698`
(`git diff --quiet a2aa73f42 fd8c94698 -- <f>` em cada um). Trazer não apagou linha nenhuma da produção.

| ficheiro | entrou? | porquê |
|---|---|---|
| `admissao/gatilho_da_inteligencia.py` | **sim, e mudado** | o gatilho D90-5. Mudanças: corte vigente (§3), entrega com MANIFESTO+SHA256SUMS, `--uma-volta` com estado próprio e trinco da volta, DSN só pelo nome |
| `medidas/vigia_da_esteira.py` | **sim, e mudado** | sem a etapa `passagem` (não foi portada); lê o estado do disparador; alerta `DEFEITO_NA_SALA` |
| `scripts/micro_coleta/provar_backup_da_sala.py` | **sim, igual** | `provar()` como função (devolve a DSN ao ambiente) e `podar()` = a retenção |
| `scripts/micro_coleta/ensaio_offline.py` | **sim, igual** | `SINTONIA_PG_BIN` (4 linhas) |
| `curadoria/.gitignore`, `italia-portale/client/.gitignore` | sim, adaptados | runtime do disparador fora do Git |
| `admissao/passagem_para_a_sala.py` | **NÃO** | **escreve na Sala** (`pousar` pela porta). O disparador da D140 é só-leitura; e a produção já leva cada corrida pela porta dentro da coleta contínua (`ferramentas/big_collection/coleta_continua.py`, D124). Duas mãos a levar corridas à Sala = colisão. Se o dono a quiser, é outra missão |
| `curadoria/supervisor.py` (gancho `_hook_esteira`) | **NÃO** | o supervisor (tarefa SINTONIA-Arranque) não tem a DSN, e a regra desta missão é a DSN **no arranque do processo** pelo método do `coleta_continua.cmd`, sem `setx`. Um processo próprio, pelo Agendador, cumpre isso sem mexer no serviço que já roda |
| `tests/test_esteira_sozinha.py` | **não; portado em parte** | os testes do gatilho, da retenção e do vigia foram para `tests/test_disparador_intelligence.py`; os da passagem e do gancho não, porque o código deles não entrou |
| `provas/esteira_sozinha/*` (ensaio, mutantes, baterias) | não | provas daquele ramo; as desta missão estão em `provas/l2/` |
| `ESTEIRA-SOZINHA.md`, `docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`, gerados do mapa | não | relatório de outro ramo / gerados (o mapa é regerado pela cadeia aqui) |

### «Gerar cruzamentos» — o que isto é hoje, medido

Os cruzamentos que o disparador gera são **os que o motor canónico produz**: relações D112 e janelas CAP-WIN × estudos
CAP-SCI (`motor_das_capacidades.rodar`). `pacote/pote_cruzamentos_max.py` (CRUZAMENTOS-MAX) **não** entra: lê
`docs/intelligence/r7/ANALISE-R7.json`, um estudo fixo com `CROSSINGS`, e o motor de hoje não escreve `CROSSINGS`.
Ligá-lo a um corte novo é motor novo — decisão do dono, não desta missão.

## 2 · O que o disparador faz (uma volta)

```
Agendador (a cada 30 min) -> disparador_intelligence.cmd  (set /p SINTONIA_SALA_DSN=<SALA_DSN.txt)
  -> py admissao\gatilho_da_inteligencia.py --uma-volta
       trinco da volta -> lê curadoria\ESTEIRA-INTELLIGENCE-ESTADO.json
       PARAR.flag? -> sai
       SELECT count/min/max(pousado_em) na Sala, depois da marca       (só leitura, de 5 em 5 min)
       10 novos OU 1 novo à espera há 4 h?  não -> SEM_DELTA / POUCOS_E_RECENTES
       trinco da corrida -> pg_dump da Sala -> cópia descartável (PROVA_VALE)
         -> export READ_ONLY da CÓPIA + hora de pouso de cada linha
         -> CORTE VIGENTE (§3) -> motor_das_capacidades -> pote v2 -> fiscal validar_pote_v2
            PASSA:    PARA-O-CASCO\ (POTE.json + MANIFESTO.json + SHA256SUMS.txt) — e PARA aí (fronteira)
            REPROVA:  nada sobe; POTE-REPROVADO-<RUN>.js guardado com as violações
         -> poda dos backups velhos
       grava o estado -> sai
  -> py medidas\vigia_da_esteira.py   (curadoria\ESTEIRA-SAUDE.json)
```

**Nunca escreve na Sala**: não chama `pousar`, `rever` nem `retirar`, não escreve `consumido_em`; a Sala só é lida por
`SELECT` (duas travas: o cliente recusa o que não é SELECT, e `default_transaction_read_only=on`) e por `pg_dump`.
Provado por teste (escritores trocados por dublês que rebentam; SQL só `select`), por prova estática (o código não
contém escritor nem `consumido_em`), por mutação (L1–L6) e no ensaio (impressão da Sala igual antes e depois de cada disparo).

## 3 · Defeito (a): ITEM_ID repetido — tratado sem o esconder

A vista `sala_de_espera_atual` tem uma linha por `(run_id, ordem)`; o mesmo `ITEM_ID` pode pousar por duas corridas
(o coordenador mediu na Sala real: `derived:6/56/57/60/62/66`, duas linhas cada). O motor recusa o corte **inteiro**
(`LeiViolada: ITEM_ID repetido no corte`, `motor/motor_das_capacidades.py:770`). O disparador:

- leva ao motor **uma linha por ITEM_ID: a de `pousado_em` mais recente** (desempate `run_id`, `ordem`) — a revisão vigente;
- tira do corte, e **declara**, as outras; tira também `ITEM_ID` sem identidade (`?`, vazio, `NAO SEI`: a migration 031
  diz que não é endereço) e os repetidos cuja hora de pouso não se lê (NÃO SEI qual é a vigente);
- escreve a declaração em `CORTE-VIGENTE.json` (pasta da corrida), em `INT_ULTIMO_CORTE` (estado), no resultado da volta,
  no `MANIFESTO.json` da entrega (`CORTE_VIGENTE`), e o vigia levanta `DEFEITO_NA_SALA` com os ITEM_ID.
- **Não** muda a Sala, **não** muda o motor nem o SQL do motor (a hora de pouso lê-se numa segunda consulta, só-leitura, na
  mesma cópia).

A regra «a mais recente é a vigente» é **minha leitura** de «revisão vigente». Se o dono quiser outra (por exemplo, a
primeira que pousou), muda-se `cortar_vigente` e só ela.

## 4 · Bloqueio (b): ENTITY_SOURCE — o pote de hoje não passa no fiscal

O motor escreve `ENTITY_SOURCE` como **mapa** por chave (D112: `{VALOR, ENTITY_SOURCE, POR_ITEM}`,
`motor/motor_das_capacidades.py:493-498`); o schema pede **texto** (`POTE_INTELLIGENCE_CASCO-v2.schema.json:49`).
Sem conversão, o fiscal reprova «devia ser string» (7/7 na fixture).

**Decisão do Intelligence owner (D142), aplicada:** no pote, `ENTITY_SOURCE` = o valor da lei COL-LAW-221
(`SPAN|PARAGRAPH_CONTEXT|SECTION_TITLE|DOCUMENT_TITLE|UNKNOWN`) quando o bloco o tiver, senão `UNKNOWN`; **proibido**
achatar o mapa ou escolher uma entrada. Feito em `admissao/gatilho_da_inteligencia.py::montar_o_pote`, o ponto de
montagem do pote **do disparador**, explícito e testado (`TestEntitySourceNoPote`, mutantes L43–L47). **Não** no gerador
partilhado: lá o acervo já escreve `ENTITY_SOURCE` achatado e há teste que o exige
(`tests/test_acervo_na_intelligence.py::test_B11`); mudar isso é do dono do pote. O mapa inteiro continua em `MOTOR.json`.

**Medido depois da conversão:** todo objeto do motor traz o mapa → todos viram `UNKNOWN` → o fiscal reprova
**«ENTITY_SOURCE esconde a ignorancia»** (`pacote/pote_intelligence_casco.py:825-827`: só «NAO SEI» é ignorância
escrita). Fixture 7/7, ensaio 7/7, Sala da R9 15/15. Nem o motor, nem o schema, nem o fiscal foram tocados:
**`POTE_NOVO = FAIL`**, motivo = **conflito de duas leis no mesmo campo** (D142 manda `UNKNOWN`, `conferir_pote` recusa
`UNKNOWN`). Quem decide é o dono do pote. (As propostas A/B da primeira versão deste relatório ficaram superadas pela D142.)

## 5 · Provas

### 5.1 · Ensaio num PostgreSQL descartável — `provas/l2/ensaio_disparador.py` → `provas/l2/ENSAIO-DISPARADOR.json`

Banco novo numa porta livre, **34 migrations**, semeado com a fixture SINTÉTICA do R7 pelos **donos** da Sala (`pousar`,
`rever`). O defeito (a) foi **plantado**: a linha `SINT-R7-APOL-38-BRLE#0` pousa outra vez por outra corrida, noutro
universo (a Sala já recusa o mesmo ITEM_ID no mesmo universo vindo de outra corrida — lido no SQL de `pousar`). Sem rede.
O caminho é a volta agendada de verdade (`uma_volta`).

| passo | resultado medido |
|---|---|
| Sala semeada | 10 linhas na vista (a fixture tem 9; a Sala **fundiu** `SINT-R7-ARIF-38#1` com o `#0`, mesmo documento — C6), o repetido na vista: `SINT-R7-APOL-38-BRLE#0` × 2 |
| **dois disparos**: o 2.º com o trinco da corrida preso | `OCUPADO`, **nenhuma cópia feita**, Sala igual |
| **item novo → dispara** (10 novos) | `DEZ_OU_MAIS_NOVOS (10)` → cópia `PROVA_VALE`, igual à Sala, export `READ_ONLY=on` da **cópia** → corte vigente **10 → 9 linhas**, `ITEM_ID_REPETIDO = [SINT-R7-APOL-38-BRLE#0]` **declarado** → motor real correu (`IR-…`): windows 1 · science 3 · future 1 · sources 3; cruzamentos: 4 relações D112, 1 janela CAP-WIN, 3 estudos CAP-SCI → pote gerado → fiscal **REPROVA** (7 violações, as 7 `ENTITY_SOURCE`) → **nada sobe**; casco sem pote, entrega inexistente |
| **sem item novo** | `SEM_DELTA` |
| 1 item novo, recente | `POUCOS_E_RECENTES (1 novos)` — espera |
| o mesmo, +4 h 30 | `NOVO_A_ESPERA_HA_4H (1 novos)` → corre → pote reprovado outra vez (7, `ENTITY_SOURCE`) |
| **.cmd real** (`set /p SINTONIA_SALA_DSN=<SALA_DSN.txt`, ambiente sem nenhuma `SINTONIA_*`) → `--medir` | código 0, `NOVOS = 11`, `DECISAO = CORRER`; a DSN **não** aparece na saída (nem a porta) |
| **motor DUBLÊ** (declarado: a corrida sintética válida de `tests/fixtures/pote`, com o `ENTITY_SOURCE` do único objeto que o traz trocado por `DOCUMENT_TITLE`, valor da lei) | `POTE_SUBIU`; `PARA-O-CASCO/` = `MANIFESTO.json`, `POTE.json`, `SHA256SUMS.txt`; os sha **batem** — o caminho da subida funciona quando o pote é válido |
| **a fronteira** | `italia-portale/` fotografado inteiro (tamanho e mtime de cada ficheiro) no início e no fim do ensaio: **igual** |
| vigia | escreveu; `ALERTA`: `sala DEFEITO_NA_SALA`, `coleta PARADA`, `fonte/agendador/portal NAO SEI` (é ensaio: sem worker, sem tarefa, sem pote aprovado) |
| **a Sala em cada disparo** | impressão (md5 das linhas de `sala_de_espera`, n.º de revisões, n.º de `consumido_em`) **igual antes e depois dos 6 disparos**; `consumido_em` preenchido: **0** no fim |

15 conferências, 15 verdes → `DISPARADOR_INTELLIGENCE = PASS`. `POTE_NOVO_GERADO_SEM_MAO_HUMANA = FAIL` (o motor gerou o
pote sozinho; o fiscal reprovou-o por `ENTITY_SOURCE`, §4). **Isto prova o disparador, não o laço:** nenhum pote real
chegou à entrega, e a R9 automática libera 0 objetos (`provas/l2/R9-AUTO-VS-MANUAL.md`).

Dois tropeções do **ensaio** (não do disparador), corrigidos e ditos: (1) a fixture trazia a janela incompleta dentro do
item e a trava `janela_declara_as_quatro_chaves` recusou o pouso — o ensaio passou a pousar com `JANELA_NAO_MEDIDA` e a
janela da fixture entra por `rever`, como o dono faz; (2) o ensaio casava as revisões por posição, e a fusão do `#1`
desalinhava-as — passou a casar pelo ITEM_ID.

### 5.2 · Testes — `tests/test_disparador_intelligence.py` 53/53 · `tests/test_harness_mutacao_l2.py` 2/2

Regra do gatilho (8), volta do gatilho (12, incluindo o **motor verdadeiro** sobre o export R7 e o bloqueio
`ENTITY_SOURCE` medido), corte vigente (8, incluindo: o motor verdadeiro **recusa** o export com repetido e **aceita** o
corte), só-lê-a-Sala (3: escritores trocados por dublês que rebentam; toda a SQL é `select`; o código não contém
escritor nem `consumido_em`), entrega (3), volta agendada (5: sem DSN não corre e não a diz; a DSN nunca aparece no
resultado nem no estado; duas voltas ao mesmo tempo — a segunda não grava), retenção (5), vigia (9).

### 5.3 · Mutação — `provas/l2/mutantes.py` → `provas/l2/MUTANTES.json`: **47/47 mortos**, restaurados byte a byte

Os quatro que a missão pediu: **escreve na Sala** (L1 `pousar`, L3 UPDATE pela consulta, L4/L5/L6 export sem as travas
só-leitura), **marca consumido_em** (L2 `retirar`), **sem trinco** (L7 corrida, L8 volta, L9 volta ocupada que grava),
**pote inválido entregue** (L10 fiscal ignorado, L11 entrega antes do fiscal, L12 sha errado, L13 entrega meia),
**a fronteira** (L42 o disparador escreve sob `italia-portale/`; o harness limpa o que ele criou e confere o portal
igual no fim), **ENTITY_SOURCE** (L43 mapa achatado, L44 escolhe uma entrada, L45 texto fora da lei passa, L46 sem
conversão, L47 conversão que estraga a saída do motor). E mais:
corte vigente torto (L14–L18), vigia que cala o defeito (L19), DSN no resultado (L20), sem DSN corre (L21), e os
herdados da esteira (regra, recuo, cópia, PARAR, intervalo, poda, vigia, retenção: L22–L41). Testes com `-B` (sem `.pyc`).

## 6 · Instalar — **NÃO FAZER AGORA (D152)**

> Coordenador (D151/D152): o gatilho fica **pronto, NÃO agendado, NÃO instalado**. O que segue é só o registo de
> **como** se instalaria quando o dono mandar.

```bat
cd %USERPROFILE%\orca\workspaces\eame-sintonia\<arvore do servico>
git fetch origin claude/l2-disparador-v1
git rev-parse HEAD                    & rem tem de ser 852ec0f0b... (a producao de hoje)
git merge-base --is-ancestor HEAD origin/claude/l2-disparador-v1 && echo FF_OK
git merge --ff-only origin/claude/l2-disparador-v1
rem Se o HEAD NAO for 852ec0f0b (a producao andou), NAO force: e preciso outra juncao.
```

**O ficheiro de arranque** (fora do repo, como o `coleta_continua.cmd`): `%SI%\disparador_intelligence.cmd`

```bat
@echo off
cd /d %USERPROFILE%\orca\workspaces\eame-sintonia\<arvore do servico>
set SI=%USERPROFILE%\sintonia-sala-italia
set SINTONIA_SALA_BACKEND=POSTGRES
set /p SINTONIA_SALA_DSN=<%SI%\SALA_DSN.txt
set SINTONIA_PSQL_EXE=%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe
py admissao\gatilho_da_inteligencia.py --uma-volta >> %SI%\DISPARADOR-INTELLIGENCE.log 2>&1
py medidas\vigia_da_esteira.py >> %SI%\DISPARADOR-INTELLIGENCE.log 2>&1
```

A DSN só existe dentro desse processo (sem `setx`), e o disparador nunca a imprime (só o **nome** da variável, se faltar).

**Conferir sem gravar nada:** `py admissao\gatilho_da_inteligencia.py --medir` (só SELECT: o delta e a decisão).
**Ligar:** `schtasks /Create /TN "SINTONIA-DISPARADOR-INTELLIGENCE" /SC MINUTE /MO 30 /TR "%SI%\disparador_intelligence.cmd" /F`
**Parar:** `curadoria\PARAR.flag` (para o disparador e o resto do serviço) · `schtasks /Change /TN "SINTONIA-DISPARADOR-INTELLIGENCE" /DISABLE`.
**Desfazer:** `git reset --keep 852ec0f0b` + apagar a tarefa. Nenhum livro vivo nem a Sala são escritos pela instalação.
**Códigos de saída de `--uma-volta`:** 0 feito/esperou · 1 cópia/motor falhou (recua 30 min) · 3 outra volta a decorrer · 4 falta a DSN.
**Disco:** `curadoria\esteira\intelligence\` guarda no máximo ~4 backups inteiros (~50 MB cada); os velhos ficam só com o recibo.
**Ler a saúde:** `curadoria\ESTEIRA-SAUDE.json` → `ALERTA`, `ALERTAS[]`, `ETAPAS{}`, `ULTIMO_DELTA_DA_INTELLIGENCE`, `ULTIMO_CORTE_DA_INTELLIGENCE`.

**Se fosse instalado hoje:** dispara quando houver material novo, faz a cópia, corre o motor, e o fiscal **reprova**
o pote (§4). Nada entra na entrega até o dono do pote decidir. O vigia mostra `pote` parado e, se os 6 repetidos medidos pelo coordenador continuarem na Sala, `DEFEITO_NA_SALA`.

## 6-bis · Base: a produção andou (fd8c94698 → 852ec0f0b)

A produção avançou durante a missão (V-BUSCA: `linha_busca` + mapa). Medido: `fd8c94698` é antepassado de `852ec0f0b`,
e o único ficheiro que os dois lados mexeram é `system-map/data/architecture.declared.json`, em trechos diferentes.
Juntei-a no ramo com um **merge** (`37ca629ae`, sem reescrever o que já estava publicado), regerei o mapa pela cadeia,
e a bateria por nome foi medida **contra `852ec0f0b`**: `provas/l2/BATERIA-BASE-852ec0f.json` ×
`provas/l2/BATERIA-DEPOIS-e76f695.json` → 0 novas, 0 sumidas (`provas/int_r7/bateria_por_nome.py`, rede fechada,
3 trabalhadores, worktrees limpas). Instalar seria `merge --ff-only` sobre `852ec0f0b` — **mas não se instala (D152)**.

## 7 · Design

Nenhuma superfície visual tocada. `ADAMA_DESIGN_SYSTEM_MATCH = NAO SE APLICA` (sem UI).

## EM PALAVRAS SIMPLES

1. **Fiz o robô que liga a Intelligence sozinho.** A cada meia hora ele olha a Sala, só olhando: é como espiar pela
   janela sem abrir a porta. Se chegaram 10 itens novos, ou se um item novo já espera há 4 horas, ele tira uma cópia da
   Sala, roda o motor em cima da cópia e monta o pote. Ele nunca escreve na Sala e nunca marca nada como «usado».
   Nunca rodam dois ao mesmo tempo. Provei com um banco de mentira: a Sala ficou igualzinha antes e depois de cada vez.
2. **O pote que ele monta hoje é recusado pelo fiscal, e por isso nada é entregue.** Um campo (`ENTITY_SOURCE`, «de
   onde veio o nome») vem do motor como uma caixinha com várias coisas dentro. A regra nova do dono manda escrever ali
   «UNKNOWN» (não sei) quando não há um valor da lei. Fiz isso. Mas o fiscal do pote só aceita «não sei» escrito como
   «NAO SEI», e chama «UNKNOWN» de ignorância escondida. São duas regras brigando no mesmo campo; quem desempata é o
   dono do pote. Com um pote de exemplo que respeita as duas, a entrega chegou certa, com a conferência (sha) batendo.
   E o robô **para na entrega**: quem põe na tela é o Casco, nunca ele. Não está ligado nem instalado (D152).
3. **Medi a R9 sem a mão humana: 0 objetos, contra 2 feitos à mão.** As 2 frases do clima da R9 foram escritas por
   uma pessoa dentro do script. Não existe ainda quem as ache sozinho no boletim — e isso é trabalho da Coleta, não da
   Intelligence. Deixei escrito o menor passo (`provas/l2/R9-AUTO-VS-MANUAL.md`), sem construir.
4. **Um defeito da Sala não trava mais o motor, mas continua à vista.** Alguns itens estão na Sala duas vezes, e o motor
   recusava tudo por causa deles. Agora o robô usa só a versão mais nova de cada item, e escreve num papel quais ficaram
   de fora. O boletim de saúde grita «defeito na Sala» enquanto eles lá estiverem.

## 8 · GERADOR (diretiva do Intelligence owner, 29/09) — D-GER-1 e D-GER-2

Entrega completa, com a tabela da diretiva: `C:/Users/London1/auditoria-madrugada/ENTREGA-L2-GERADOR.md`.

- **D-GER-1** (`pacote/pote_intelligence_casco.py::conferir_pote`): `ENTITY_SOURCE` só com o vocabulário da COL-LAW-221,
  importado do dono (`leis/afirmacao_da_fonte.ENTITY_SOURCES`), com `UNKNOWN` incluído. «NAO SEI», mapa, texto achatado,
  `TRECHO_DA_AFIRMACAO`, vazio e `?` reprovam. O gerador já não traduz `ENTITY_SOURCE` para «NAO SEI». A conversão D142
  (mapa → UNKNOWN) passou para **antes** do gerador (`montar_o_pote`).
- **D-GER-2** (`motor/r7_export_da_copia.sql`, `motor/motor_das_capacidades.py`, gerador): `RAW_SHA256` e
  `RAW_STORAGE_PATH` do `raw_asset` em cada PROVA, ou «NAO SEI». O fiscal só aceita sha de 64 hex.
- **Sobre a Sala da R9:** pote do motor real **válido** (15 objetos, 0 violações), `RAW_SHA256` do banco em 21/21 provas,
  **0 objetos liberados**. Ensaio no Postgres descartável 16/16, com `POTE_NOVO = PASS` e o byte da prova igual ao
  `raw_asset` em 15/15. Mutação **60/60**. A entrega passou a ser escrita em LF (`sha256sum -c` falhava no Windows).
- **Efeito medido (bateria contra `852ec0f0b`):** 37 falhas novas — 34 da fixture `CORRIDA-SINTETICA-V2-UNICO`
  (texto fora da lei), 2 do acervo (texto achatado «POR_CHAVE»), 1 do ponto fixo do mapa (resolvido pela cadeia) e
  1 que não reproduz sozinha (`test_a_regra_de_t2`). Não corrigidas aqui, por ordem da diretiva.
