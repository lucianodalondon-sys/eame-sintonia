# PROMPT PARA A NOVA CONTA CLAUDE — SINTONIA EAME

Copie o bloco abaixo inteiro e cole como primeira mensagem na nova conta.

---

```
# SINTONIA EAME — ACEITE DE HANDOFF
# NÃO ALTERE NADA. NÃO COLETE NADA. NÃO ABRA NOVA FRENTE.
# Sua única entrega nesta primeira missão é um HANDOFF ACCEPTANCE REPORT.

Você está assumindo um repositório construído por outra conta Claude que se esgotou.
Todo o contexto foi externalizado para o Git. Você NÃO tem a conversa anterior.

Repositório: lucianodalondon-sys/eame-sintonia
Branch:      claude/sintonia-eame-repo-setup-xccfob

==================================================
PASSO 1 — MEDIR O ESTADO. NÃO CONFIAR EM MEMÓRIA.
==================================================

git fetch
git branch --show-current
git rev-parse HEAD
git rev-parse origin/claude/sintonia-eame-repo-setup-xccfob
git status --short
git log -3 --oneline
Confirme e reporte: BRANCH · LOCAL_HEAD · REMOTE_HEAD · WORKING_TREE_CLEAN.

NÃO procure tag de handoff: o proxy git deste ambiente RECUSA push de tag (HTTP 403)
e o remoto não tem tag nenhuma. O marcador do handoff é o COMMIT cuja mensagem começa
com "handoff: transferencia completa para nova conta Claude" — ache com:

  git log --oneline --grep='^handoff: transferencia completa'
Se LOCAL_HEAD != REMOTE_HEAD, PARE e reporte antes de qualquer coisa.

==================================================
PASSO 2 — LER O HANDOFF
==================================================

Leia INTEIRO, sem pular:

  HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md

Depois leia, NESTA ORDEM (é o mapa da seção AA do handoff):

  1. docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md      <- se dois documentos discordarem, ESTE vence
  2. docs/regras/MODELO-DE-IDENTIDADE-EAME.md
  3. docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md
  4. docs/operacao/PORTOES-DE-COLETA-10B.md
  5. docs/descoberta/CAMADA-DE-VOZ-ESPANHA.md
  6. docs/fontes/ATLAS-DE-FONTES-EAME.md
  7. docs/decisoes/DIARIO-DE-DECISOES.md
  8. docs/apresentacao/MATRIZ-DE-PROVA-EAME.md

==================================================
PASSO 3 — RODAR A SUÍTE
==================================================

python3 -m unittest discover -s tests

Esperado: 345 testes, OK, 0 falhas, 0 erros.
Se divergir, reporte o número real e o teste que falhou. NÃO conserte ainda.

Nota: pytest NÃO está instalado. Use unittest. Só biblioteca padrão do Python 3.11.

==================================================
PASSO 4 — REPRODUZIR AS MÉTRICAS SENTINELA
==================================================

python3 scripts/metricas_canonicas.py
python3 scripts/portao.py
python3 scripts/proveniencia.py

Confira estas sentinelas contra o que o handoff afirma:

  TEST_COUNT_CURRENT              = 330
  SOURCE_ID_COUNT                 = 37
  RAIF_SEASONS_AVAILABLE          = 23
  RAIF_READINGS_TOTAL             = 148964
  ES_EXPIRING_6M                  = 486     (ADAMA 36)
  ES_EXPIRING_12M                 = 1004    (ADAMA 61)
  ES_ACTIVE_WITH_PAST_EXPIRY      = 34
  VOICE_ES_RESEARCHERS            = 152
  VOICE_ES_VIDEO_CONTENTS         = 252     (origens 157 — NUNCA some as duas)
  VIDEO_COUNT_CLASSIFIED          = 252
  VIDEO_ORIGINALITY_UNKNOWN       = 241
  QUEUE_RESEARCHERS_ES            = 20
  ASK_WRONG                       = 0

E o portão deve imprimir READY_FOR_NEXT_ES_COLLECTION = YES com os seis PROVED.

Qualquer divergência é ACHADO, não erro seu. Registre.

==================================================
PASSO 5 — NÃO ALTERE NADA
==================================================

Nesta missão você NÃO deve:
  · editar arquivo
  · rodar coleta
  · gastar chave Apify
  · abrir França ou Itália
  · atacar o backlog dos 47

Se encontrar um bug, ANOTE. Não conserte ainda.

==================================================
PASSO 6 — DEVOLVER O HANDOFF ACCEPTANCE REPORT
==================================================

Responda com exatamente estas onze seções, cada uma com evidência medida
(caminho de arquivo, número, saída de comando). Sem adjetivo, sem resumo vago.

A. HEAD ENTENDIDO
   branch, local, remoto, árvore limpa, e o SHA do commit de handoff.

B. ARQUITETURA ENTENDIDA
   quais são as três ferramentas, qual documento manda, e por que MT3
   NÃO pode ser apresentada como oportunidade.

C. ESPANHA ENTENDIDA
   vídeo, comentários, LinkedIn, Instagram, ciência, mídia técnica —
   com os números que VOCÊ derivou, não os que leu.

D. VOICE ENTENDIDA
   incluindo os resultados NEGATIVOS. Diga qual é o número acionável de
   vozes técnicas de olivar e por que não é 67.

E. SCIENCE ENTENDIDA
   como o corpus foi construído, o caso do ID conflacionado, e por que
   SCIENCE -> PUBLIC VOICE está NOT_REACHED.

F. REGULATORY ENTENDIDO
   números de expiry, o que são os 34 registros anômalos, e por que
   EXPIRY != WITHDRAWAL.

G. BUSINESS CASE ENTENDIDO
   por que ECONOMIC_VALUE não está provado e por que isso NÃO é falha.

H. AUDITORIA ENTENDIDA
   os 206 achados, o erro de auditar árvore em movimento, a regra do SHA
   congelado, e por que 47 NAO_ATENDIDO != 47 tarefas.

I. BACKLOG ENTENDIDO
   o que está FECHADO e o que está ABERTO, conferido contra o repositório.

J. PRÓXIMO PASSO ENTENDIDO
   qual é o NEXT_MISSION recomendado e por que ele vem antes da ponte Brasil.

K. DIVERGÊNCIAS ENCONTRADAS
   tudo que o handoff afirma e o repositório contradiz. Se não houver
   nenhuma, diga "nenhuma" — mas só depois de ter conferido as sentinelas.

==================================================
LEIS QUE VOCÊ HERDA E NÃO PODE REABRIR SEM EVIDÊNCIA
==================================================

Estão na seção O do handoff. As que mais custam se esquecidas:

  NAME != HANDLE != URL != PROFILE != PERSON != ORGANIZATION
  SOURCE_LOCATION != FACT_LOCATION
  EXPIRY != WITHDRAWAL
  FIELD PRESSURE != DEMAND
  FOLLOWERS != AUTHORITY
  SOURCE FAILURE != ZERO
  FIRST SNAPSHOT != NO CHANGE
  HTTP 200 != FONTE VIVA
  SUCCEEDED DA PLATAFORMA != EXECUÇÃO BEM-SUCEDIDA
  COBERTURA ALTA != COBERTURA CORRETA
  GEOGRAPHIC CONCORDANCE != TEMPORAL ANTICIPATION

E a premissa que define o produto:
  NÃO HAVERÁ DADOS INTERNOS DA ADAMA. NUNCA.
  Nenhuma saída pode afirmar REVENUE, MARGIN, SALES ou ROI REALIZED.

Não comece trabalho nenhum antes de entregar o acceptance report.
```

---

## Notas para quem cola o prompt

- O prompt acima é auto-suficiente: a nova conta não precisa de nada desta conversa.
- Se o `HEAD` tiver avançado depois do handoff, o **passo 1 detecta** e manda parar.
- As sentinelas do passo 4 são deliberadamente **verificáveis em um comando**. Se o ledger
  divergir do handoff, o ledger vence e a divergência é o primeiro achado da nova conta.
- O relatório de aceite é o **filtro de qualidade**: se ele vier vago, a nova conta não leu.
