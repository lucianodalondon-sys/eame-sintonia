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

**A tarefa existente de coleta contínua de sites não deve ser desligada apenas para priorizar social.** Se estiver saudável, continua rodando. Social entra junto; não substitui o que já funciona.

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

Para Instagram e YouTube, uma semente manual é válida: perfil, canal, post, reel ou vídeo pode ser indicado manualmente pelo Owner, Bot de Fontes ou equipe. Não esperar descoberta automática perfeita para capturar conteúdo público já identificado.

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

## 7A. Entrada da Intelligence por CONTEÚDO, não por MIME de web

A Intelligence precisa ler o **texto útil**, independentemente do canal de origem.

Entram no Opus:

```text
HTML → texto extraído
PDF → texto extraído
LinkedIn → texto/legenda e TRANSCRIPTION, quando houver vídeo
Instagram → legenda/texto e TRANSCRIPTION, quando houver reel/vídeo
YouTube → título/descrição e TRANSCRIPTION
áudio/vídeo → TRANSCRIPTION
```

O FAST não pode filtrar semanticamente por `text/html` ou `application/pdf` e, com isso, ignorar conteúdo social já transcrito.

Correção mínima permitida neste fim de semana:

```text
selecionar TEXTO_EXTRAÍDO + TRANSCRIPTION
→ mandar para Opus
```

**Não** considerar envelope técnico `application/json` vazio como conteúdo. JSON de transporte/erro/observação só entra se contiver conteúdo real útil; caso contrário, fica fora sem criar nova régua semântica.

O critério para `ENTROU_NA_INTELLIGENCE = SIM` é simples:

```text
existe texto/transcrição real
+
Opus leu
+
a leitura ficou registrada e ligada ao item/documento
```

Não é necessário o conteúdo entrar no CASE-001. O Opus pode dizer:

```text
FORA_DO_CASE
```

e ainda assim a leitura social está funcionando.

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

## 12. Casco: É O CASCO ORIGINAL — MAS O PREVIEW VISUAL ATUAL NÃO ESTÁ APROVADO

**Não criar uma nova interface simplificada para substituir o produto.**

**Também não interpretar "Casco original" como autorização para congelar o visual atual do preview.**

As telas escuras/genéricas atualmente servidas no preview de resgate NÃO são autoridade visual e NÃO estão aprovadas para cliente. Preservar o Casco significa preservar a arquitetura de produto, as ferramentas, a navegação e os contratos de dados — não preservar um styling ruim ou uma tela de diagnóstico.

### Autoridade visual

Usar como referência obrigatória:

```text
docs/design/CONTRATO-DE-DESIGN-SINTONIA.md
CASCO-CLIENT-DEMO.md
italia-portale/BASELINE/_ds/adama-brandwell/
ADAMA Design System já incorporado ao repositório
```

O contrato visual já determina:

```text
ADAMA corporate green
LL Brown / Aleo
A Shape
ícones ADAMA
espaço em branco generoso
hierarquia editorial
categorias com semântica visual correta
fato ≠ interpretação ≠ ação
NÃO SEI visível sem parecer erro técnico
```

### O que está REPROVADO no preview atual

```text
tela quase toda preta/marrom
cards genéricos iguais
paredes de texto
microtipografia cinza
falta de ícones/categorias ADAMA
falta de hierarquia visual
títulos em português dentro do produto italiano
"testo in italiano non ancora fornito"
"non noto" repetido como linguagem de sistema
selo SPERIMENTALE com peso de debug
listas cruas de evidência dominando o detalhe
campos vazios ocupando grandes blocos
aparência de console/auditoria em vez de produto comercial
```

Esses elementos podem existir em debug interno, mas não na superfície de demonstração.

### Regra de implementação

```text
MANTER:
arquitetura do Casco
ferramentas existentes
rotas
potes/gavetas
dados reais
links de evidência

REFAZER/RESTAURAR:
apresentação visual
cards
hierarquia
tipografia
espaçamento
ícones
uso das cores ADAMA
detalhe do caso
timeline
blocos visuais
idioma italiano
```

**Não redesenhar o produto do zero. Reaplicar o Design System e a linguagem visual já definidos ao conteúdo real.**

O Casco da demonstração é o mesmo produto que já existia antes, com a identidade visual ADAMA, navegação, ferramentas, hierarquia e linguagem visual já construídas.

O resgate simplifica **a alimentação de dados**, não o produto.

```text
CAPTURA SIMPLES
→ OPUS
→ SAÍDA SIMPLES
→ CASCO ORIGINAL
```

O Casco deve continuar com as ferramentas e áreas já existentes, incluindo quando houver dados:

```text
Opportunity Radar
Future Radar
Crop Windows
Market Pulse
Competition
Research / Science / Researchers
Portafoglio
Label Intelligence
Archive / Sources / Field
demais áreas já existentes no produto
```

Não transformar o Sintonia em um feed genérico de notícias.

### Cards e casos

Opportunity, Lead e Signal continuam usando a família visual forte já definida no Casco/ADAMA:

```text
ÍCONE / CATEGORIA
PROBLEMA
CULTURA · REGIÃO
STATUS
JANELA, quando existir
PRODUTO, quando comprovado
ESPLORA →
```

Pouco texto na primeira camada.

```text
PRIMEIRA CAMADA = VER
CLIQUE = ENTENDER
DETALHE = PROVAR
```

No detalhe, usar os blocos existentes e só mostrar os que tiverem informação útil:

```text
O QUE SIGNIFICA
AÇÃO
TIMELINE
CLIMA
FENOLOGIA
CROP WINDOW
MERCADO
PORTFÓLIO
LABEL
CONCORRÊNCIA
FONTES
```

Conteúdo vindo de Instagram, LinkedIn e YouTube aparece como **mais uma origem de evidência dentro do Casco original**, com plataforma/fonte visível. Não ganha uma interface paralela.

Nenhum SHA, commit, branch, run id, gate ou código técnico na camada do cliente.

### feed.html

Se existir `feed.html`, ele é apenas:

```text
DEBUG / DIAGNÓSTICO / VALIDAÇÃO DE DADOS
```

Não é o produto da demonstração e não substitui `/portale` nem o Casco original.

---

## 13. Saída do resgate para o Casco original

A Intelligence pode gerar um arquivo simples intermediário para acelerar o fim de semana, inclusive `CASCO_FEED.json`, **mas ele é apenas um adaptador de dados**.

O destino final é alimentar as estruturas que o Casco original já entende.

Preferir reaproveitar:

```text
CRUZAMENTO-COMERCIAL.json
+
estruturas existentes das ferramentas do Casco
```

Mapeamento conceitual:

```text
conteúdo útil de domínio
→ ferramenta correspondente do Casco

SINAL / LEAD
→ Future Radar

OPORTUNIDADE
→ Opportunity Radar

GAP
→ Portafoglio

mercado
→ Market Pulse

janela/fenologia
→ Crop Windows

regulatório/label
→ Label Intelligence

concorrência
→ Competition

ciência/pesquisadores
→ Research / Science / Researchers
```

Se o caminho mais rápido for gerar `CASCO_FEED.json` e convertê-lo manualmente para os arquivos que o Casco já consome, fazer assim.

Não criar banco novo.

Não criar uma segunda interface.

Não criar uma segunda arquitetura de produto.

**Simplificar a tubulação; preservar o Casco.**

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

Mantém a **arquitetura do Casco original**, mas é responsável por restaurar/aplicar o Design System ADAMA aprovado.

O preview visual atual não é aceito como baseline só porque usa as rotas e componentes antigos.

Só conecta/renderiza o que a Intelligence entregar nas ferramentas corretas, porém deve apresentar isso com qualidade de produto para cliente: hierarquia, tipografia, espaçamento, ícones, categorias, cores e idioma corretos.

Não cria produto paralelo, não troca o Casco por feed genérico e não reclassifica.

**DONE do Casco não é "dados apareceram". DONE é "dados reais apareceram no Casco original com apresentação visual aprovada".**

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
→ gera saída simples
→ adapta para as estruturas existentes
→ Casco original recebe
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
