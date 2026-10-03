# SINTONIA — MAPA DE RESGATE OPERACIONAL v0.3

**Data:** 03/10/2026  
**Objetivo único:** ter um Sintonia demonstrável e comercialmente útil na segunda-feira, 05/10/2026.  
**Status:** substitui o mapa v0.2 para o trabalho deste fim de semana.  
**Regra do Owner:** simplificar até funcionar.

---

## 0. A ordem

Durante este fim de semana, o Sintonia não será tratado como um projeto de engenharia completo.

Ele será tratado como um produto que precisa entregar inteligência visível.

A pergunta para qualquer tarefa é:

```text
ISSO AJUDA A COLOCAR CONTEÚDO REAL
→ NA IA
→ NO CASCO
→ ATÉ SEGUNDA?
```

Se NÃO:

```text
BACKLOG
```

Não apagar trabalho antigo. Não reconstruir a fundação. Apenas parar de deixar a fundação bloquear o produto.

---

## 1. O Sintonia deste fim de semana

A arquitetura inteira cabe nisto:

```text
SITES / PDF
INSTAGRAM
LINKEDIN
YOUTUBE
OUTRAS FONTES QUE JÁ CONSEGUIMOS CAPTURAR
        ↓
CAPTURA
        ↓
TEXTO / LEGENDA / TRANSCRIÇÃO
        ↓
OPUS
        ↓
ENTENDE
SEPARA
AGRUPA
CRUZA
        ↓
SINAL / LEAD / GAP / OPORTUNIDADE
        ↓
CASCO
```

Nada além disso pode ser requisito para o conteúdo andar.

---

## 2. Princípio LLM-FIRST

### Código faz

```text
captura
download
transcrição
armazenamento
URL
datas técnicas
hash
ID técnico simples
dedupe técnico
execução
publicação
```

### LLM faz

```text
relevância
tema
cultura
região
problema
praga/doença
mercado
clima
concorrência
ciência
campo
fato x opinião
credibilidade contextual
relações entre conteúdos
agrupamentos
casos
sinais
leads
gaps
oportunidades
ação
o que falta saber
```

**Não criar regra determinística para substituir uma decisão semântica que o Opus consegue tomar lendo o conteúdo.**

Se o LLM não puder concluir:

```text
NAO_SEI
```

---

## 3. Fontes AGORA

O Sintonia coleta **tudo o que já consegue capturar**.

```text
SITES      = ATIVO
PDF        = ATIVO
INSTAGRAM  = ATIVO
LINKEDIN   = ATIVO
YOUTUBE    = ATIVO
OUTRAS ROTAS EXISTENTES = ATIVAS, se já funcionam
```

Não existe competição entre site e social. O objetivo é **volume útil vindo de todos os canais**.

A prioridade operacional é simples:

```text
NÃO PARAR O QUE JÁ FUNCIONA
+
LIGAR TAMBÉM INSTAGRAM / LINKEDIN / YOUTUBE
+
MANDAR TUDO PARA A IA
```

Sites e PDFs continuam fazendo parte da coleta. Social também. O erro a evitar é voltar a uma coleta que, na prática, só entrega sites.

### Fontes podem ser escolhidas manualmente

Neste fim de semana não precisamos de descoberta perfeita.

Pode haver uma lista manual de:

- agrônomos;
- cooperativas;
- associações;
- produtores;
- pesquisadores;
- universidades;
- organizações agrícolas;
- concorrentes;
- canais técnicos;
- eventos;
- páginas regionais.

Se sabemos que vale acompanhar, capturamos.

---

## 4. Regra de captura: primeiro entra, depois a IA decide

Não bloquear captura por relevância semântica.

Fluxo:

```text
CONSEGUIU CAPTURAR?
        ↓
SIM
        ↓
GUARDA
        ↓
MANDA PARA OPUS
```

Se 1.000 conteúdos entrarem e 700 forem inúteis, o Opus descarta os 700.

Isso é aceitável.

Não gastar dias tentando programar um filtro que adivinhe antes quais 300 serão úteis.

---

## 5. Registro mínimo de cada conteúdo

Para funcionar agora, cada item capturado precisa apenas de:

```text
ITEM_ID
PLATAFORMA
URL
AUTOR_OU_PERFIL
PUBLICADO_EM
CAPTURADO_EM
TEXTO_OU_LEGENDA
TRANSCRICAO, se houver
MIDIA_URL, se houver
HASH, se já for simples gerar
```

Campos ausentes:

```text
NAO_SEI
```

### Não são requisito de entrada neste fim de semana

```text
SOURCE CONTRACT
SOURCE_ID canônico novo
CASE_ID prévio
coorte
READY_FOR_COLLECTION
score
régua de relevância
gate editorial
lineage perfeita
Atlas perfeito
```

Esses mecanismos podem continuar existindo no projeto, mas **não bloqueiam o RESGATE OPERACIONAL**.

---

## 6. Caminho manual é permitido

Para segunda-feira, manual não é falha.

Se necessário:

```text
abrir conta/canal manualmente
→ coletar URLs
→ executar capturador manualmente
→ baixar mídia manualmente
→ transcrever
→ jogar conteúdo em um único inbox
→ rodar Opus em lotes
→ gravar saída
→ alimentar Casco
```

O objetivo é provar o produto.

Automação completa volta depois.

---

## 7. Um inbox simples

Todo conteúdo capturado — site, PDF, Instagram, LinkedIn, YouTube ou outra rota existente — pode ir para uma entrada única do RESGATE.

Formato recomendado:

```text
RESGATE-INBOX.jsonl
```

Um registro por conteúdo.

Nenhuma estrutura paralela complexa.

Deduplicação técnica mínima:

```text
mesma plataforma + mesma URL
ou
mesmo hash do conteúdo
```

Nada de dedupe semântico em código.

O Opus resolve equivalência semântica.

---

## 8. Opus — primeira passada: entender tudo

O Opus lê os itens em lotes e devolve para cada um:

```text
ITEM_ID
RELEVANTE
RESUMO
TIPO_CONTEUDO
FATO_OU_OPINIAO
CULTURA
LOCAL_DO_FATO
DATA_DO_FATO
PROBLEMA
PRAGA_DOENCA
CLIMA
MERCADO
CONCORRENTE
PESQUISA
CAMPO
PRODUTO_MENCIONADO
NUMEROS
EVIDENCIA_LITERAL
IMPORTANCIA
```

Não inferir:

```text
local do autor = local do fato
data do post = data do fato
opinião = fato
propaganda = evidência independente
```

Quando não houver prova:

```text
NAO_SEI
```

---

## 9. Opus — segunda passada: olhar o conjunto

Depois de ler os conteúdos individualmente, o Opus recebe o conjunto útil.

Perguntas:

```text
quais itens falam do mesmo assunto?
quais repetem a mesma origem?
quais são independentes?
quais se reforçam?
quais se contradizem?
o que está aparecendo em várias fontes?
o que parece novo?
o que está crescendo?
o que merece atenção agora?
```

Ele cria agrupamentos simples.

Não precisa existir CASE_ID para o conteúdo entrar.

Se for útil persistir o agrupamento:

```text
CASE_ID
```

é criado **depois** pela Intelligence.

CASE é consequência da inteligência, não portão de entrada.

---

## 10. Cruzamento comercial

A Intelligence cruza os melhores agrupamentos com as referências ADAMA que já existem.

Usar o que já está disponível de:

```text
portfólio
produto
label
uso autorizado
cultura
alvo
crop window
fenologia
clima
mercado
concorrência
histórico
```

Não reconstruir essas bases neste fim de semana.

### Oportunidade

Só chamar de OPORTUNIDADE quando houver evidência suficiente para:

```text
FATO / NECESSIDADE REAL
+
CULTURA
+
LOCAL
+
PROBLEMA
+
TIMING / POR QUE AGORA
+
JANELA AGRONÔMICA, quando necessária
+
PRODUTO ADAMA
+
LABEL / USO COMPATÍVEL
+
AÇÃO COMERCIAL
```

Se faltar:

- muito contexto → SINAL;
- uma peça comercial importante → LEAD;
- necessidade real sem solução ADAMA comprovada → GAP.

**Meta comercial do fim de semana:** procurar agressivamente pelo menos 1 oportunidade defensável e alguns leads/sinais fortes. Não fabricar oportunidade para cumprir meta.

---

## 11. Caça manual de oportunidade é permitida

Depois da primeira leitura em massa:

```text
OPUS seleciona os 10 assuntos mais promissores
        ↓
humano + LLM escolhem os que têm maior chance comercial
        ↓
buscar MAIS conteúdo sobre esses assuntos
        ↓
Sites / PDFs / Instagram / LinkedIn / YouTube
        ↓
Opus relê
        ↓
cruza com ADAMA
```

Isso pode ser totalmente manual neste fim de semana.

Não precisamos esperar um agente autônomo investigar.

---

## 12. Casco: mostrar, não explicar engenharia

O Casco precisa parecer um produto cheio de inteligência.

Primeira camada:

```text
AGORA
CAMPO
FITOSSANITÁRIO
MERCADO
CLIMA
CONCORRÊNCIA
CIÊNCIA
SINAIS
OPORTUNIDADES
```

Cada card mostra:

```text
TÍTULO
O QUE ACONTECEU
POR QUE IMPORTA
CULTURA · LOCAL
DATA
ORIGEM: Site / PDF / Instagram / LinkedIn / YouTube
STATUS
ESPLORA →
```

No detalhe:

```text
resumo
fontes
timeline, se houver
evidências
cruzamentos
produto ADAMA, quando comprovado
ação, quando defensável
```

Nenhum SHA, commit, branch, run id, gate ou código técnico na camada do cliente.

---

## 13. Arquivo de saída para o Casco

Usar o caminho que o Casco já consome.

Preferência:

```text
CRUZAMENTO-COMERCIAL.json
```

A saída do RESGATE pode ser gravada manualmente nesse formato.

Não criar banco novo.

Não criar ponte nova.

Não criar pipeline novo se copiar um JSON resolve para segunda-feira.

---

## 14. Papéis neste fim de semana

### Coordenador

Só:

```text
mantém todos nesta missão
remove bloqueios
impede novas frentes
cobra conteúdo → IA → Casco
```

### Scrap Engineer

Só:

```text
Sites
PDF
Instagram
LinkedIn
YouTube
captura
mídia
texto
áudio
transcrição
```

Não redesenha a coleta.

### Bot de Fontes

Só ajuda a montar rapidamente listas de fontes, contas e canais que valem capturar.

Não cria processo de aprovação.

### Intelligence Owner

É o cérebro.

```text
Opus lê
separa
agrupa
cruza
caça oportunidade
gera saída do Casco
```

### Casco Owner

Só renderiza o que a Intelligence entregar.

Não reclassifica.

### LAB

Audita depois que houver produto visível.

Não bloqueia execução.

---

## 15. O que fica PAUSADO até depois da demonstração

Durante o RESGATE:

```text
revalidar READY_LEGACY
consertar todas as coortes
Source Contract como gate
Atlas perfeito
alocação canônica completa de novas fontes
case lineage perfeita
investigação autônoma perfeita
nova taxonomia
novos scores
novos gates
nova régua semântica
novo benchmark
limpeza dos 280 arquivos da produção
System Engineering Baseline
regerar mapas auxiliares
grandes merges
grandes repins
```

Nada disso é apagado.

Apenas não pode roubar o fim de semana.

---

## 16. Limpeza imediata do trabalho

A limpeza agora é operacional, não destrutiva.

### Parar de executar

- missões de prova que não colocam conteúdo no portal;
- refatorações de arquitetura;
- investigação de drift sem impacto imediato na demo;
- criação de contratos e gates que impeçam conteúdo capturável de chegar à IA;
- testes adicionais depois que a captura básica já estiver funcionando.

### Manter

- capturadores que funcionam;
- transcrição;
- armazenamento simples;
- Opus;
- referências ADAMA existentes;
- Casco;
- deploy de preview.

### Não deletar código

Git já preserva histórico.

Depois da demonstração fazemos limpeza estrutural com calma.

---

## 17. Plano até segunda-feira

### Sábado — ENCHER

Objetivo:

```text
capturar tudo em volume
```

Meta operacional, não gate:

```text
Sites/PDF: continuar captando o que já funciona
Instagram: o máximo útil possível
LinkedIn:  o máximo útil possível
YouTube:   o máximo útil possível
TOTAL:     centenas de itens de todos os canais, se as capacidades permitirem
```

Ao mesmo tempo, Opus já começa a ler os primeiros lotes.

### Domingo — PENSAR E MOSTRAR

```text
Opus termina leitura
→ elimina lixo
→ agrupa temas
→ cruza referências ADAMA
→ seleciona melhores sinais/leads/oportunidades
→ gera CRUZAMENTO-COMERCIAL.json
→ Casco recebe
```

Rodar novas capturas direcionadas para fortalecer os casos comercialmente mais promissores.

### Segunda de manhã — CONFERIR

Apenas:

```text
abrir preview
conferir cards
conferir fontes
conferir oportunidades/leads
corrigir erros visíveis
```

Não iniciar engenharia nova.

---

## 18. Definition of Done para a demonstração

O trabalho do fim de semana está entregue quando:

```text
SITES_PDF_CAPTURADOS > 0
INSTAGRAM_CAPTURADOS > 0
LINKEDIN_CAPTURADOS > 0
YOUTUBE_CAPTURADOS > 0

TOTAL_CAPTURADO = volume suficiente para parecer um sistema vivo

OPUS_LEU = SIM
OPUS_DESCARTOU_LIXO = SIM
OPUS_AGRUPOU = SIM
OPUS_CRUZOU_COM_ADAMA = SIM

CASCO_TEM_CONTEUDO_REAL = SIM
CASCO_TEM_SINAIS = SIM
CASCO_TEM_LEADS = SIM, se existirem

OPORTUNIDADE_REAL = pelo menos 1, se a evidência permitir
```

Se não existir oportunidade defensável, não inventar.

Mas o sistema precisa mostrar inteligência útil e explicar claramente por que os melhores casos ainda são SINAL ou LEAD.

---

## 19. Checkpoint único

Nenhum relatório longo.

Responder apenas:

```text
SITES_PDF_CAPTURADOS =
INSTAGRAM_CAPTURADOS =
LINKEDIN_CAPTURADOS =
YOUTUBE_CAPTURADOS =
TOTAL_CAPTURADO =

OPUS_LEU =
DESCARTADOS =
UTEIS =
AGRUPAMENTOS =

SINAIS =
LEADS =
GAPS =
OPORTUNIDADES =

3_MELHORES_CASOS =

APARECE_NO_CASCO =
LINK_PREVIEW =

BLOQUEIO_REAL, SE HOUVER =
```

---

## 20. Regra final

```text
CAPTA TUDO QUE CONSEGUIR
→ IA PENSA
→ MOSTRA POUCO E BOM
```

Se estivermos gastando mais tempo provando a infraestrutura do que entregando conteúdo para o LLM, estamos indo na direção errada.

Até segunda-feira:

```text
FAZER FUNCIONAR > FAZER PERFEITO
```

Depois da demonstração, o projeto de engenharia profissional retoma com base nos problemas que realmente aparecerem em produção.
