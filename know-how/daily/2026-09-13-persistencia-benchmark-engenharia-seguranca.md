# DAILY KNOW-HOW — 2026-09-13 — PERSISTÊNCIA ENTRE ABAS + BENCHMARK DE ENGENHARIA + SEGURANÇA

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra conhecimento durável; **não cria um segundo KNOW-HOW** e não substitui `SINTONIA-EAME-KNOW-HOW.md`, Bíblias, contratos, decisões arquiteturais, Git, System Map, código, runtime ou provas.

## PRINCÍPIO GERAL

O SINTONIA é desenvolvido por múltiplas abas, agentes e IAs. O projeto não pode depender de memória de conversa nem de conhecimento técnico tácito de uma única pessoa ou agente.

Duas obrigações passam a andar juntas:

```text
1. O QUE APRENDEMOS PRECISA SER PERSISTIDO.
2. O QUE CONSTRUÍMOS PRECISA SER CONFRONTADO COM ENGENHARIA MADURA.
```

Nenhuma conversa, IA ou fornecedor externo vira fonte de verdade por si só.

---

# 1 · CHAT NÃO É MEMÓRIA DO PROJETO

```text
CHAT ONLY != PROJECT MEMORY
TAB ONLY != DURABLE KNOWLEDGE
AI REMEMBERS != PROJECT KNOWS
MISSION FINISHED WITHOUT REQUIRED PERSISTENCE != FULLY CLOSED
```

Tudo que surgir numa missão e tiver consequência durável para outra aba/agente deve aterrissar no Git, no owner correto.

Exemplos obrigatórios de persistência:

```text
DECISÃO ARQUITETURAL
LEI NOVA OU ALTERADA
CONTRATO NOVO OU ALTERADO
OWNER DE CONCEITO ALTERADO
SOLUÇÃO VALIDADA
ERRO IMPORTANTE
LIMITAÇÃO PROVADA
FERRAMENTA CANÔNICA OU APOSENTADA
MUDANÇA DE DIREÇÃO
NOVO RISCO CONHECIDO
APRENDIZADO QUE OUTRA ABA NÃO PODE PERDER
REGRA DE SEGURANÇA RELEVANTE
```

Toda missão estrutural deve fechar com:

```text
KNOW_HOW_DELTA = NENHUM
```

ou:

```text
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

Se houver atualização necessária, ela precisa ser persistida no owner apropriado.

---

# 2 · “AUTO-PERSISTÊNCIA” É O ALVO, NÃO UMA CAPACIDADE JÁ PROVADA

A direção desejada é que missões relevantes possuam um mecanismo obrigatório de fechamento que impeça conhecimento durável de morrer na aba.

Até existir prova executável desse mecanismo:

```text
AUTO_PERSISTENCE = NOT_PROVED
```

Não afirmar que o sistema “grava sozinho” enquanto não houver hook, gate, CI ou outro mecanismo real que prove isso.

Enquanto isso, a obrigação continua processual: cada missão deve classificar e persistir seu delta.

---

# 3 · O SINTONIA NÃO DEVE SER DESENVOLVIDO POR IMPROVISAÇÃO

Quando houver dúvida arquitetural, de dados, segurança, operação, observabilidade, IA, infraestrutura, governança ou produto técnico, o caminho padrão é:

```text
PROBLEMA
→ AUTORIDADE INTERNA EXISTENTE
→ ESTADO REAL MEDIDO
→ BENCHMARK EXTERNO RELEVANTE
→ PRINCÍPIOS / PADRÕES MADUROS
→ DESENHO ADEQUADO AO SINTONIA
→ IMPLEMENTAÇÃO MÍNIMA
→ TESTES
→ RED TEAM ADEQUADO AO RISCO
→ REGRESSÃO
→ PROVA
→ VEREDITO
```

Não implementar a primeira solução plausível apenas porque uma IA consegue escrevê-la.

```text
AI CAN GENERATE CODE != ENGINEERING IS CORRECT
POPULAR PATTERN != FIT FOR SINTONIA
VENDOR FEATURE != SINTONIA REQUIREMENT
```

---

# 4 · BENCHMARK EXTERNO É ETAPA DE ENGENHARIA QUANDO O PROBLEMA É NOVO OU ESTRUTURAL

O SINTONIA deve procurar referências externas maduras quando estiver desenhando algo que:

- ainda não possui solução canônica interna;
- altera arquitetura;
- cria novo tipo de control plane, catálogo, lineage ou observabilidade;
- envolve segurança, identidade, autenticação, autorização ou segredo;
- envolve banco, concorrência, retry, persistência ou consistência;
- envolve IA, RAG, agentes ou novos limites de automação;
- envolve deploy, CI/CD, isolamento de ambientes ou produção;
- envolve governança de dados e procedência;
- envolve novo modelo operacional com padrão industrial conhecido.

Referências externas devem ser escolhidas pela pergunta, não por marca favorita.

Exemplos já utilizados como benchmark arquitetural, quando pertinentes:

```text
Databricks / Unity Catalog
Snowflake / Horizon
Palantir Foundry / Ontology
DataHub
OpenMetadata
Atlan
Backstage
Dagster
dbt
```

Essas plataformas são **referências de estudo**, não autoridades do SINTONIA.

```text
EXTERNAL BENCHMARK != CANONICAL AUTHORITY
```

Depois da decisão interna, Bíblia, contrato, decisão arquitetural ou Know-how passam a ser o owner conforme o tipo de conhecimento.

---

# 5 · HIERARQUIA DE FONTES PARA BENCHMARK TÉCNICO

Preferência de evidência externa:

```text
1. documentação oficial da tecnologia ou padrão;
2. standards e frameworks reconhecidos;
3. reference architectures oficiais;
4. documentação de projetos open-source maduros;
5. papers e engenharia publicada por organizações reconhecidas;
6. estudos independentes confiáveis;
7. comunidade e relatos como sinal, não como única prova para decisão crítica.
```

Para segurança, priorizar quando aplicável referências como:

```text
OWASP
NIST
CIS
CWE / MITRE
orientação oficial de segurança do fornecedor utilizado
```

Não copiar checklist inteiro sem relação com o risco real.

---

# 6 · BENCHMARK NÃO É CARGO CULT

O objetivo não é “fazer igual Databricks”.

O fluxo correto é:

```text
QUAL PROBLEMA ELES RESOLVEM?
QUAL PRINCÍPIO ESTÁ POR TRÁS?
QUAL PARTE SE APLICA AO SINTONIA?
QUAL PARTE NÃO SE APLICA?
QUAL CUSTO / COMPLEXIDADE INTRODUZ?
COMO PROVAR QUE NOSSA ADAPTAÇÃO FUNCIONA?
```

Toda adoção externa deve separar:

```text
FATO OBSERVADO NA REFERÊNCIA
INFERÊNCIA PARA O SINTONIA
DECISÃO INTERNA
PROVA DA IMPLEMENTAÇÃO
```

Não importar arquitetura enterprise desnecessária para resolver problema pequeno.

---

# 7 · SEGURANÇA É PARTE DA ARQUITETURA, NÃO UMA REVISÃO NO FIM

Security-by-design passa a ser regra de engenharia do SINTONIA.

Antes de alterações que cruzem fronteiras de confiança, dados, credenciais, usuários, rede ou produção, perguntar explicitamente:

```text
QUAL É O ATIVO?
QUAL É A FRONTEIRA DE CONFIANÇA?
QUEM PODE LER?
QUEM PODE ESCREVER?
QUEM PODE EXECUTAR?
QUAL SEGREDO EXISTE?
ONDE ELE VIVE?
QUAL É O MENOR PRIVILÉGIO NECESSÁRIO?
QUAL É O IMPACTO SE FALHAR?
COMO AUDITAMOS?
COMO REVOGAMOS?
COMO RECUPERAMOS?
```

Princípios mínimos, quando aplicáveis:

```text
LEAST PRIVILEGE
DENY BY DEFAULT
NO SECRETS IN GIT
ENVIRONMENT SEPARATION
PRODUCTION != LABORATORY
INPUT VALIDATION
AUTHENTICATION != AUTHORIZATION
AUDITABILITY
ROTATABLE CREDENTIALS
FAIL CLOSED FOR SECURITY GATES
DEPENDENCY / SUPPLY-CHAIN AWARENESS
BACKUP / RECOVERY WHERE DATA MATTERS
```

Não declarar segurança apenas por ausência de falhas conhecidas.

```text
NO KNOWN VULNERABILITY != SECURE
```

---

# 8 · SEGURANÇA E COMPORTAMENTO CRÍTICO PRECISAM DE PROVA CONTRA A TECNOLOGIA REAL

Quando o risco depende de comportamento real, testar contra a tecnologia real e em ambiente seguro.

Exemplos:

```text
POSTGRESQL → provar comportamento em PostgreSQL
AUTH / PERMISSIONS → provar allow e deny com identidades controladas
CONCORRÊNCIA → provar concorrência quando houver risco concorrente
RETRY / CRASH → provar persistência e recuperação quando isso importar
DEPLOY → validar em ambiente descartável antes de LIVE
SEGREDOS → provar que não aparecem em artefatos e logs previstos
```

Mocks são úteis, mas não substituem prova onde o risco depende do runtime real.

---

# 9 · REVISÃO ADVERSARIAL É OBRIGATÓRIA QUANDO O RISCO JUSTIFICAR

Mudanças de risco relevante devem incluir uma revisão que tente encontrar falhas de desenho, autorização, isolamento, recuperação, auditoria, dependências e consistência.

A revisão deve ser proporcional ao componente e documentar:

```text
RISCO CONSIDERADO
PROVA EXECUTADA
LIMITAÇÃO DA PROVA
RESULTADO
RISCO RESIDUAL
```

Não transformar um checklist genérico em “segurança provada”.

---

# 10 · IA EXTERNA TAMBÉM É FERRAMENTA, NÃO AUTORIDADE

Claude, ChatGPT, Codex ou qualquer outro agente podem pesquisar, propor, implementar e revisar.

Mas:

```text
AI SAID SO != PROOF
AI GENERATED != REVIEWED
AI REVIEWED != RUNTIME PROVED
```

Toda recomendação estrutural deve voltar para:

```text
Git
Bíblias
Contratos
Know-how
Código
Banco/runtime
Testes
Provas
```

---

# 11 · QUANDO BENCHMARK EXTERNO É DISPENSÁVEL

Não transformar toda alteração pequena em pesquisa infinita.

Benchmark profundo não é obrigatório quando:

- a solução já está definida por Bíblia/contrato maduro;
- a alteração é mecânica e local;
- existe padrão interno já provado exatamente para o caso;
- não há nova decisão arquitetural, de segurança ou operacional.

Mesmo nesses casos, regressão e prova continuam obrigatórias conforme o risco.

---

# 12 · CONSEQUÊNCIA PARA O COLD START DE QUALQUER IA

Uma IA nova precisa descobrir não apenas “como o SINTONIA funciona”, mas também **como o SINTONIA toma decisões de engenharia**.

Ela deve aprender pelo repositório que:

```text
NÃO INVENTAR QUANDO PODE MEDIR
NÃO IMPROVISAR QUANDO EXISTE AUTORIDADE
NÃO CRIAR PADRÃO NOVO SEM VER SE JÁ EXISTE OWNER
QUANDO O PROBLEMA É NOVO/ESTRUTURAL, BENCHMARKAR ENGENHARIA MADURA
SEGURANÇA ENTRA NO DESENHO DESDE O INÍCIO
ADAPTAR PADRÕES EXTERNOS, NÃO COPIÁ-LOS CEGAMENTE
PROVAR NA TECNOLOGIA REAL
PERSISTIR O QUE FOI APRENDIDO
```

---

# 13 · GATE ANTES DE INTELLIGENCE

Antes de iniciar a construção estrutural da Intelligence, a governança atual deve integrar e provar pelo menos:

```text
1. cold start por qualquer IA;
2. Sala de Controle / governance entrypoint;
3. registro das autoridades e owners;
4. Bíblias / contratos / Know-how encontráveis;
5. persistência obrigatória de deltas entre missões;
6. System Map capaz de representar governança sem virar autoridade;
7. caminho de benchmark externo para decisões novas;
8. security-by-design como regra transversal;
9. governance gate sem falsas garantias de automação.
```

Isso não exige implementar todos os controles de segurança futuros antes da Intelligence.

Exige que **o método que obrigará cada nova parte a considerar engenharia e segurança esteja estabelecido, encontrável e aplicável**.

---

## O QUE MUDOU

Foram formalizadas duas leis complementares:

1. conhecimento durável produzido em qualquer aba/agente deve ser persistido no Git/owner correto;
2. decisões novas ou estruturais devem buscar referências externas maduras e incorporar segurança desde o desenho.

## POR QUÊ

O SINTONIA é um sistema novo, desenvolvido por múltiplas IAs/agentes. A arquitetura precisa impedir dependência de memória de chat ou de conhecimento técnico tácito, usando processo, autoridades, benchmark, prova e segurança explícitos.

## PROVA / ORIGEM

- perda operacional/encontrabilidade de autoridades entre branches demonstrou que conversa ou branch isolada não serve como memória única;
- benchmark de governance/control plane realizado em 2026-09-13 mostrou padrões maduros de ownership, lineage, control plane, applied state e observabilidade;
- as próprias leis do SINTONIA já exigem engenharia por prova, runtime real e revisão adversarial.

## CONSEQUÊNCIA

O SINTONIA passa a exigir uma disciplina de engenharia reproduzível por qualquer IA, independentemente da aba.

A futura Sala de Controle deve rotear também para estas regras de engenharia e governança.

## O QUE NÃO MUDOU

- nenhuma Bíblia foi alterada;
- nenhum contrato operacional foi alterado;
- nenhum código/runtime foi alterado;
- nenhum System Map foi alterado;
- nenhuma Intelligence foi iniciada;
- nenhuma capacidade automática de persistência foi declarada como existente sem prova.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
