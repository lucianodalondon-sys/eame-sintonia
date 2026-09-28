# L2-DISPARADOR-INTELLIGENCE — o disparador automático SOMENTE-LEITURA da Intelligence

> **D140** (dono real, 28/09): *«Intelligence Owner constrói/conclui o disparador automático SOMENTE-LEITURA permitido pela
> TRAVA: detectar material novo → snapshot/cópia segura da Sala → rodar motor → gerar cruzamentos → produzir pote
> canônico. consumido_em é outra decisão — não misturar.»*
> Ramo `claude/l2-disparador-v1`, sobre a produção **`fd8c94698`** (`origin/servico-20260923-0923`).
> Red team: *«não criar outro disparador; integrar seletivamente a ESTEIRA sobre fd8c94698; f85b4138a NÃO é ancestral de
> fd8c94698 — enxerto cego pode perder peças; DSN no arranque»*.

```
ENSAIO     __ENSAIO__
MUTAÇÃO    41/41 mortos · ficheiros restaurados byte a byte (provas/l2/MUTANTES.json)
TESTES     tests/test_disparador_intelligence.py 53/53 · tests/test_harness_mutacao_l2.py 2/2
BATERIA    __BATERIA__
MAPA       __MAPA__
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
            PASSA:    PARA-O-CASCO\ (POTE.json + MANIFESTO.json + SHA256SUMS.txt) e sintonia-pote.js
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

Medido na fixture: o motor gera o pote sem mão humana, e o fiscal **reprova com 7 violações, as 7 de `ENTITY_SOURCE`**
(`$.COMPARTIMENTOS.<x>.OBJETOS[i].ENTITY_SOURCE: devia ser string`). O motor escreve um **objeto** por chave (D112:
`{VALOR, ENTITY_SOURCE, POR_ITEM}`, `motor/motor_das_capacidades.py:493-498`); o schema pede **texto**
(`docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json:49`). Não mudei nem um nem outro.

**Proposta ao dono do pote (a menor correção, escolha dele):**

- **(A) — 1 linha no schema:** `"ENTITY_SOURCE": {"type": ["string", "object"]}`. O contrato já diz «ENTITY_SOURCE? D112,
  quando a Intelligence o diz», e o D112 do motor é o objeto. Custo: o casco mostra `ENTITY_SOURCE` com `par(c, o[c])`
  (`italia-portale/client/sintonia-pote-casco.js:193`); um objeto ali aparece como objeto, e o Casco disse «nenhum campo
  novo» — tem de aceitar a forma.
- **(B) — no gerador do pote (`pacote/pote_intelligence_casco.py`, dono do pote):** achatar para texto na saída
  (p.ex. `"CROP_ID:TRECHO_DA_AFIRMACAO; REGION_ID:NAO SEI"`) e levar o objeto em `FORA_DO_CONTRATO`. O schema e o casco
  não mudam; é o que o pote R9 já faz (`ENTITY_SOURCE: "TRECHO_DA_AFIRMACAO"`, e passou no fiscal).

Eu recomendaria (B): o Casco já aceitou o formato como está, e (B) não o obriga a nada.

## 5 · Provas

__PROVAS__

## 6 · Instalar (na máquina do bot; Windows)

```bat
cd %USERPROFILE%\orca\workspaces\eame-sintonia\<arvore do servico>
git fetch origin claude/l2-disparador-v1
git rev-parse HEAD                    & rem tem de ser fd8c94698... (a producao de hoje)
git merge-base --is-ancestor HEAD origin/claude/l2-disparador-v1 && echo FF_OK
git merge --ff-only origin/claude/l2-disparador-v1
rem Se o HEAD NAO for fd8c94698 (a producao andou), NAO force: e preciso outro rebase.
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
**Desfazer:** `git reset --keep fd8c94698` + apagar a tarefa. Nenhum livro vivo nem a Sala são escritos pela instalação.
**Códigos de saída de `--uma-volta`:** 0 feito/esperou · 1 cópia/motor falhou (recua 30 min) · 3 outra volta a decorrer · 4 falta a DSN.
**Disco:** `curadoria\esteira\intelligence\` guarda no máximo ~4 backups inteiros (~50 MB cada); os velhos ficam só com o recibo.
**Ler a saúde:** `curadoria\ESTEIRA-SAUDE.json` → `ALERTA`, `ALERTAS[]`, `ETAPAS{}`, `ULTIMO_DELTA_DA_INTELLIGENCE`, `ULTIMO_CORTE_DA_INTELLIGENCE`.

**Hoje, instalado, o que acontece:** dispara quando houver material novo, faz a cópia, corre o motor, e o fiscal **reprova**
o pote (§4). Nada sobe para o casco até o dono do pote decidir. O vigia mostra `pote` parado e `DEFEITO_NA_SALA` (os 6 repetidos).

## 7 · Design

Nenhuma superfície visual tocada. `ADAMA_DESIGN_SYSTEM_MATCH = NAO SE APLICA` (sem UI).

## EM PALAVRAS SIMPLES

__SIMPLES__
