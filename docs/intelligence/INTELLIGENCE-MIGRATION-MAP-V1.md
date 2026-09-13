# MAPA DE MIGRAÇÃO DA INTELLIGENCE — V1

```
MISSAO   C-INT-ARB-01 · 2026-09-13
ESTADO   ESTE DOCUMENTO NAO EXECUTA MIGRACAO NENHUMA.
```

> Cada linha diz **o que fazer**, **porquê** e **o que corre mal se for feito**.
> Nenhuma foi executada. A coluna `ACTION_FUTURE` é trabalho de outra missão.

---

## AS 12 PEÇAS

| # | CURRENT | TARGET | ACTION_FUTURE | WHY | RISK |
|---|---|---|---|---|---|
| 1 | `C-CADEIA-V21` (2 ficheiros) | duas peças | **NEEDS_SPLIT**: `motor/v21_cadeia.sh` fica na Intelligence; `motor/cadeia_canonica.sh` vai para a Coleta/infra | um aplica migrations de banco e o outro constrói o pacote analítico | dividir mexe no mapa declarado da linha funcional; e `cadeia_canonica.sh` é corrido por 2 workflows — errar a gaveta parte o CI |
| 2 | `C-V21-INGEST` | KEEP_CANONICAL | isolar `normalize_agro.py` do import de `coleta/eppo_gd` | a ingestão é canónica; o caminho directo não é | mexer no dicionário agronómico sem o reconstruir perde trabalho real |
| 3 | `C-V21-CRUZAMENTO` | KEEP_CANONICAL | nenhuma | dono provado de CROSSING e CONVERGENCE | — |
| 4 | `C-V21-OPORTUNIDADE` | KEEP_CANONICAL | renomear o conceito de `v21_dominio_da_alegacao.py` para `CLAIM_DOMAIN_JUDGMENT` na documentação | a palavra «alegação» colide com o `CLAIM` da Collection | renomear o **ficheiro** partiria 8 referências; renomeia-se o **conceito**, não o path |
| 5 | `C-V21-CONTRATO` | KEEP_SUBORDINATE | declarar no mapa que o dono do contrato é o JSON | dois lados do mesmo contrato, um dono só | — |
| 6 | `C-V21-COMERCIAL` | KEEP_SUBORDINATE | nenhuma | leitura comercial subordinada | — |
| 7 | `C-V21-FONTES` | KEEP_SUBORDINATE | nenhuma | religação de fontes do pacote | — |
| 8 | `C-V2-LEGADO` (7 ficheiros) | LEGACY | congelar; resolver `handoff/paused-v2/auditoria-pacote.json` antes de qualquer remoção | 0 chamadores, 0 runtime | apagar agora perderia a ordem dos passos, que é conhecimento — foi por isso que a V2.1 manteve a sua cadeia |
| 9 | `lineage_generator` | MOVE_TO_GOVERNANCE | mover `Z-LINEAGE` para `F-GOVERNANCA` | é portão e facto de linhagem, não motor analítico | mover território reclassifica 4 peças de uma vez |
| 10 | `lineage_package` | MOVE_TO_GOVERNANCE | idem | idem | as três partilham **um** ficheiro: separá-las exige decidir 3 donos para 1 documento |
| 11 | `lineage_stale` | MOVE_TO_GOVERNANCE | idem | idem | idem |
| 12 | `lineage_consumer` | ASSERTION_NOT_COMPONENT | deixar de ser peça; se o facto importa, vira campo do registo de linhagem | zero ficheiros, e o mapa chama-lhe `PROVEN` | remover uma peça `PROVEN` do mapa baixa a contagem de verdes e parece regressão |

---

## AS AUTORIDADES

| CURRENT | TARGET | ACTION_FUTURE | WHY | RISK |
|---|---|---|---|---|
| Bíblia V0.2 em `research/intelligence-bible-engineering-v1` | `CANONICAL`, num snapshot integrado | integrar num commit que contenha também runtime, know-how e registo | condição 5 da própria Bíblia | trazer só o `.md` para outra branch lateral **não** resolve — muda de qual ramo ela é invisível |
| Motor V2 em `claude/intelligence-backlog-canonical` | `SUBORDINATE`, ao lado da Bíblia | integrar junto | um contrato subordinado longe da constituição é um contrato órfão | — |
| `A-BIBLIA-INTELIGENCIA` (`RECOVERY_PENDING`) | apontar para a V0.2 | ✅ **feito nesta missão** no registo | o inventário recusa o título de bíblia | — |
| cabeçalho de `motor/v21_cadeia.sh:35,47` | nomear `51010733` | corrigir o comentário na linha funcional | nomeia um gerador cuja safra o contrato lista como velha | é edição na linha funcional, que esta missão não toca |

---

## OS DEFEITOS MEDIDOS

| CURRENT | TARGET | ACTION_FUTURE | WHY | RISK |
|---|---|---|---|---|
| 50 funções pytest em 4 ficheiros | unittest | converter os 4 | 148/152 ficheiros da casa já são unittest; CI corre unittest 5× e não tem pytest | converter mal transforma 50 testes invisíveis em 50 testes vermelhos — que é **melhor**, mas precisa de quem os leia |
| 82 arestas `technical/PROVEN` | vocabulário de 6 níveis | mudar o classificador do gerador | 56 das 135 provas são co-acesso a ficheiro | `"kind": "technical"` está fixo em **7 sítios**, em **dois geradores divergentes**: missão própria |
| `motor/normalize_agro.py` → `coleta/eppo_gd.py` | `KEEP_BUT_BLOCK` | substituir a chamada de rede por leitura de dicionário já preservado | `INT-LAW-020` proíbe o coletor directo | o dicionário construído é trabalho real: bloquear a rota sem o preservar perde-o |
| `italy-v21.js` (10 MB, 0 carregadores) | remover ou declarar | decidir se é resíduo | `BUILD_ID` que o contrato não reconhece | define a mesma global que o bundle canónico: se alguém os carregar aos dois, o último vence |

---

## A ORDEM QUE ESTAS MIGRAÇÕES PEDEM

Não é a ordem da tabela. É esta, e a razão de cada posição:

```
1. INTEGRAR AS AUTORIDADES NUM SNAPSHOT
   sem isto, toda decisao abaixo fica escrita numa branch que ninguem le.

2. CONVERTER OS 4 FICHEIROS DE TESTE
   e o unico item sem dependencia de nada, e devolve 50 testes a suite.

3. DIVIDIR C-CADEIA-V21
   antes de mexer no motor, saber quais ficheiros SAO o motor.

4. BLOQUEAR O CAMINHO DIRETO
   depois da divisao, porque ele vive na peca que a divisao esclarece.

5. O CLASSIFICADOR DE ARESTAS
   por ultimo, e em missao propria: e o unico que toca os dois geradores.
```

```
COMECAR PELO CLASSIFICADOR SERIA CONSERTAR O TERMOMETRO
ANTES DE SABER SE O DOENTE TEM FEBRE.
```
