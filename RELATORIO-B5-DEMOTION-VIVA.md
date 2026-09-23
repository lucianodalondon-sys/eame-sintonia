# RELATÓRIO — B5 · DEMOTION_PROVEN AO VIVO

Missão: `C:/Users/London1/auditoria-madrugada/missao-b5-demotion-viva.txt`.
Ramo `b5-demotion-viva-v1`, base `origin/unificacao-v1` @ `a8812861`. Data 2026-09-23.

```
RESULTADO                  = NINGUEM SAIU DO PORTAO, porque NENHUMA das 37 elegiveis falha hoje
CANDIDATA_VIVA_REAL        = NENHUMA (§1)
DEMOTION_PROVEN_AO_VIVO    = NAO — sem falha real nao ha saida honesta (instrucao 19:37: nao forcar)
PROVA_EM_COPIA_FIEL        = FEITA (§6): 37/37 re-medidas contra os sites reais pela VPN IT
                             28 canario OK (sairam do portao durante a medicao e voltaram sozinhas)
                              9 robots ilegivel = RETRY, ficam no portao (ligacao != fonte morta)
                              0 reprovadas · ELIGIBLE 37 -> 37 · ponte (copia) SAIRAM []
SERVICO_VIVO_TOCADO        = NAO (so leitura; regra de um escritor respeitada)
EGRESSO                    = IT verificado antes de CADA tarefa (91), 0 paragens; IT no fim (22:41Z)
```

## 1 · Não há candidata real no vivo (FATO MEDIDO, só leitura, livro do bot 21:0xZ)

- **Portão:** 37 elegíveis. A ponte viva (`ponte-viva/curadoria/PONTE-AUTOMATICA-LOG.ndjson`)
  registou 29 travessias hoje, todas com `SAIRAM: []`. **Nunca saiu ninguém do portão ao
  vivo.**
- **As 20 quedas para DEGRADED do livro** (18 ainda DEGRADED, marcadas `owner=COLLECTION`,
  evidência `BCR-2026-09-20:*`, e 1 `RUN-PROVA-E`): avaliei cada uma com o livro cortado no
  instante da própria queda. **20 de 20 eram READY_LEGACY**, ou seja, já estavam fora do
  portão. Nenhuma prova DEMOTION do portão.
- **Coleta real:** a última falha no `data/collection-ledger/italy/observations.ndjson` é de
  21/09 (IT-T10-018 DISCOVERY_FAILED 19:03Z, IT-T7-043 IDENTITY_FAILED 19:19Z, e mais 4 das 7
  D10). As 6 têm observações HEALTHY depois. A corrida de 22/09 18:54Z deu 9 de 9 HEALTHY.
  Nada em 22-23/09.
- **IT-T5-049:** elegível. O canário do bot passou às 12:37Z. O BC2 de 23/09
  (`big-collection-runbook-v1/ferramentas/big_collection/BC2-FONTES-27.json`) reprovou-a
  (`CAPABILITY_BLOCK`, «alvo sem corpo útil: HTML_KIND=MIXED» em avisos de aulas e exames).
  **São duas medições que discordam, e isso não é falha limpa.** A re-medição do bot só a
  apanha daqui a 7 dias (`REVALIDAR_ELEGIVEIS_DIAS`).
- **IT-T7-053 / IT-T7-058:** elegíveis, CANARY FAILED por `URLError` (transporte). Falha de
  ligação não é fonte morta: não servem.
- **IT-T5-041** (proposta da B1): saiu de READY às 12:31Z pela reconciliação do corte, que é
  uma operação humana. Voltou elegível depois; não serve.

## 2 · Os caminhos de DEMOTION que existem, e o estado de cada um no vivo

| caminho | dono | vivo hoje |
|---|---|---|
| Collection → `interface_collection.source_repair_needed` → DEGRADED + REPAIR | Collection | **sem chamador de produção.** Só `provar_divisao.py` (IDs de prova) e `orquestrador/fontes_prontas.reportar_avaria`, que ninguém chama. O coletor real nunca reporta avaria |
| DEGRADED → REPAIR → canário | Curator (`alimentar_fila`) | **não corre no ciclo vivo.** O gatilho não chama `alimentar_fila`; as 18 DEGRADED não têm nenhuma tarefa REPAIR na fila desde 21/09 |
| REVALIDAR elegíveis (B3) → VALIDATE_ROUTE → sai para CANARY_PENDING → CANARY → FAIL = CONTRACTED_CANARY_FAILED / robots = ROUTE_BLOCKED | Curator (gatilho) | **ligado**, mas só dispara com prova de mais de 7 dias ou contrato novo. Hoje: 0 candidatas (as 37 foram promovidas entre 21 e 23/09) |

**INFERÊNCIA:** uma fonte elegível que avaria hoje na coleta **não sai do portão sem humano**
antes de a prova fazer 7 dias. O único caminho automático é o relógio da B3. A porta da
Collection existe e está testada, mas não tem quem bata nela. Este defeito não é desta
missão; fica registado para quem é dono da Collection.

## 3 · A prova em cópia fiel (montada, NÃO corrida)

- Cópia: `C:\Users\London1\AppData\Local\Temp\b5-copia-1810` = `git archive` do bot vivo
  @ `3d62e87d` + os livros sujos do vivo copiados. O sha256 de LEDGER, QUEUE, EVIDENCE e
  contratos é igual ao vivo.
- Plano: correr **o gatilho e o worker da própria cópia**, com o relógio do gatilho em
  +8 dias (a única coisa simulada), `descobrir_fn` desligado (sem discovery) e o feeder
  real (sem rede). A re-medição mede os sites de verdade, pela VPN IT, com robots e pausa.
  Sai do portão da cópia quem falhar de verdade hoje. Portão antes/depois medido com
  `collection_gate.elegiveis()` na cópia, e a travessia pela ponte com `--lane` a apontar
  para a cópia.
- **Parado aqui:** às 21:12Z o portão de egresso deu `EGRESS_COUNTRY_CODE = BR`, BLOCKED.
  O bot vivo já estava parado pela guarda da BC3 (`PARAR.flag` às 20:54Z, «egresso BLOCKED
  BR desde ~20:49Z»). A última atividade dele foi às 20:04Z, com 0 pedidos à rede.

## 4 · Para retomar

1. `py superficie/rede.py --portao-de-egresso IT` = PASS.
2. Refazer a cópia: os livros vivos podem ter mudado; conferir o sha256.
3. Correr o §3 e registar o portão antes/depois, `SAIRAM` e as linhas do livro.

## 5 · Segunda tentativa (23/09, 21:30Z): a VPN oscila

A coordenação mediu IT às 18:22 (-03). As minhas medições, pela mesma porta
(`superficie/rede.py --portao-de-egresso IT`):

| hora (UTC) | país |
|---|---|
| 21:30 | BR — BLOCKED |
| 21:31:14 | BR — BLOCKED |
| 21:31:46 | IT — PASS |

A guarda da BC3 parou o bot vivo às 21:27Z («UNKNOWN») e às ~21:32Z («BR x4 18:30:51–18:31:32»),
e religou-o às 21:30Z entre as duas paragens.

**Decisão:** a prova em cópia faz dezenas de pedidos durante minutos. Um portão medido só antes
e depois não cobre uma queda a meio, e a VPN caiu duas vezes em 10 minutos. **Não corri.**
Pedidos à rede desta B5 no intervalo BR: 0. Só corri as sondas do portão, que apenas perguntam
o país ao `ipinfo.io`.

A cópia continua igual ao vivo: sha256 de LEDGER, QUEUE, EVIDENCE, contratos e porta conferidos
às 21:30Z.

Para retomar: a VPN IT tem de ficar estável (por exemplo, 3 medições PASS em 5 min). Idealmente
correr a cópia com uma guarda de egresso entre voltas do worker, que é o que a BC3 já faz para o
bot vivo.

## 6 · A prova em cópia fiel (23/09, 21:46Z–22:41Z)

- **Cópia:** `git archive` do bot vivo @ `3d62e87d` + os livros vivos e o SUPERVISOR-STATE
  (sha256 conferido às 21:45Z) + a ponte viva @ `5c02bbe4` com o livro e o estado dela.
  As duas cópias ficaram em `%TEMP%`, fora de todo o repositório, e foram apagadas no fim.
  As provas estão em `curadoria/provas-b5/`.
- **O que foi simulado, e só isto:** o relógio do gatilho, +8 dias (o limiar é
  `REVALIDAR_ELEGIVEIS_DIAS = 7`). Na 2.ª passagem também as datas das tarefas feitas durante
  a prova, que ficam no mesmo relógio (§6.1). Discovery desligado (`descobrir_fn`). Tudo o
  resto é o gatilho, o worker, o canário, o livro e a ponte do vivo, a medir os sites reais.
- **Guarda:** `superficie/rede.py --portao-de-egresso IT` antes de cada tarefa, com paragem
  automática se não for IT. Correu 91 vezes e nunca parou.

| | fontes |
|---|---|
| re-medidas (VALIDATE_ROUTE → CANARY) com canário OK: saíram do portão durante a medição (READY → CANARY_PENDING) e voltaram sozinhas (→ READY_FOR_COLLECTION) | 28 |
| robots.txt ilegível, só RETRY: ficam READY e no portão, como manda `etapa_validate_route` («UM TIMEOUT NÃO É UM DISALLOW») | 9: IT-T5-101, IT-T7-053, T7-058, T7-112, T7-115, T7-118, T7-121, T7-123, T7-135 |
| reprovadas (CONTRACTED_CANARY_FAILED / ROUTE_BLOCKED) | **0** |

91 tarefas: 56 OK, 35 RETRY. O portão do bot ficou em 37 → 37. A travessia da cópia da ponte
deu `ATRAVESSOU_SEM_NOVIDADE`, 37 → 37, `SAIRAM []`, 0 linhas acrescentadas: o estado final
de todas as 37 é o mesmo de antes.

**IT-T5-049** foi re-medida e o canário do bot **passou** outra vez. A reprovação do BC2
(«corpo útil: HTML_KIND=MIXED») continua a ser outra régua, que o canário do bot não aplica.
Fica registado como divergência entre as duas réguas, não como falha da fonte.

### 6.1 · Um erro meu na 1.ª passagem

Com o relógio a +8 dias, a guarda anti-eco da B3 («VALIDATE_ROUTE há menos de 7 dias não
volta a ser pedida») via as medições feitas minutos antes como velhas. Resultado: as mesmas
5 fontes inalcançáveis voltavam ao topo em todas as voltas, e 22 nunca foram pedidas. Isto
foi um artefacto da simulação, não um defeito do bot. Corrigi na 2.ª passagem datando no
relógio simulado as tarefas mexidas durante a prova, e as 22 foram medidas.

### 6.2 · O que isto prova e o que não prova

- **Prova:** o caminho automático existe e corre sem humano. Uma fonte elegível re-medida sai
  do portão no primeiro passo e só volta se o canário passar, com a régua dos quatro passos.
  Hoje as 28 que responderam passaram todas.
- **Não prova:** a saída **definitiva** de uma fonte que falha. Hoje nenhuma falha, e o
  resultado certo é ninguém sair (instrução da coordenação às 19:37: não forçar saída). O
  portão só pode provar a saída definitiva quando houver uma falha real.
- **Continua aberto (§2):** o coletor real não chama `source_repair_needed`, e o gatilho não
  corre `alimentar_fila`, por isso DEGRADED não vira REPAIR. Uma fonte que avarie **na
  coleta** só sai do portão quando a prova fizer 7 dias.
- **9 fontes que esta máquina não alcança** (robots ilegível, sobretudo T7) ficam no portão
  por desenho. Se a rota real também não as alcança, a coleta vai falhar nelas e ninguém vai
  avisar o curator: é o mesmo buraco da linha acima.
