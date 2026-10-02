# SINTONIA — PROJETO OPERACIONAL DE FIM DE SEMANA v0.2

**Status:** baseline operacional provisória  
**Objetivo:** colocar o Sintonia em condição de demonstração e venda sem perder o rumo arquitetural.  
**Escopo:** Itália / EAME.  
**Regra:** este documento orienta o trabalho do fim de semana até ser substituído pelo System Engineering Baseline definitivo.

---

## 1. O que é o Sintonia

O Sintonia não é um agregador de notícias e não é um dashboard.

Sua função é:

```text
OBSERVAR O MUNDO AGRÍCOLA
        ↓
ENTENDER O QUE ESTÁ ACONTECENDO
        ↓
CRUZAR COM CONTEXTO AGRONÔMICO, COMERCIAL E ADAMA
        ↓
IDENTIFICAR O QUE IMPORTA
        ↓
TRANSFORMAR EM AÇÃO COMERCIAL OU ALERTA
```

O produto deve responder, em linguagem simples:

- O que está acontecendo?
- Onde?
- Em qual cultura?
- Qual problema, mudança ou oportunidade existe?
- Quando isso importa?
- O que pode acontecer a seguir?
- Existe produto ADAMA relacionado?
- O produto está autorizado para essa cultura/alvo?
- Existe oportunidade de venda?
- Se ainda não existe, o que falta?
- O que o comercial deveria fazer?

---

## 2. Princípio arquitetural

### Código

Código é responsável por captura, roteamento técnico, transporte, armazenamento temporário, hashes, integridade, deduplicação técnica, scheduling, persistência, publicação e observabilidade operacional.

### LLM

LLM é responsável por leitura, entendimento, validação semântica, extração de fatos, classificação, contextualização, relações, cruzamentos, interpretação agronômica, síntese, raciocínio comercial e redação para o usuário.

Não criar regras determinísticas apenas para imitar raciocínio que um LLM consegue executar melhor.

Regra determinística nova só entra quando existir erro real, recorrente e medido, e quando for a menor correção possível.

---

## 3. Arquitetura-mãe

```text
┌─────────────────────────────────────────────────────────────┐
│                    UNIVERSO POSSÍVEL DE FONTES              │
│                                                             │
│ Sites · PDFs · Instagram · LinkedIn · YouTube · Vídeos      │
│ Agrônomos · Pesquisadores · Instituições · Cooperativas     │
│ Clima · Fitossanitário · Regulatório · Mercado              │
│ Concorrentes · Ciência · Produtores · Eventos               │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT DE FONTES + LLM                      │
│                                                             │
│ PROCURA → ENTRA → LÊ → ENTENDE → VALIDA → CLASSIFICA       │
│                                                             │
│ Decide QUEM entra no Universo Oficial de Fontes             │
│ Entrega fonte já validada e pronta para coleta              │
└─────────────────────────────┬───────────────────────────────┘
                              │ SOURCE CONTRACT
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SINTONIA SCRAP                          │
│              FERRAMENTA + ORQUESTRADOR TÉCNICO             │
│                                                             │
│ Decide COMO capturar tecnicamente a fonte já aprovada       │
│ Roteia HTML/PDF/social/vídeo/áudio/transcrição              │
│ Tenta a melhor capacidade já existente                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   STAGING / RAW TEMPORÁRIO                  │
│                                                             │
│ Original existe apenas tempo suficiente para:               │
│ validar captura → extrair → produzir texto → provar hash    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 CONTEÚDO CANÔNICO / EVIDÊNCIA              │
│                                                             │
│ texto limpo · transcrição · URL · fonte · datas · hash      │
│ evidências literais · metadados · proveniência              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       OPUS — LEITOR                         │
│                                                             │
│ conteúdo → fatos estruturados                               │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPUS — INTELLIGENCE                      │
│                                                             │
│ fatos → sinais → temas → mudanças → relações                │
│ usa todos os domínios de conhecimento disponíveis           │
└──────────────────────┬──────────────────────┬───────────────┘
                       │                      │
                       ▼                      ▼
             CONTEXTO DINÂMICO       REFERÊNCIA CONFIÁVEL
             clima                   portfólio
             mercado                 labels
             campo/social            usos autorizados
             concorrência            produto
             ciência                 fenologia
             pesquisadores           crop windows
             fitossanitário          regulatório
             histórico               geografia
                       │                      │
                       └─────────────┬────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────┐
│               OPUS — MOTOR DE CRUZAMENTOS                   │
│                                                             │
│ cruza 2, 3, 4 ou mais dimensões quando fizer sentido        │
│ não limitado a pares hardcoded                              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 OPUS — CAMADA COMERCIAL                     │
│                                                             │
│ SINAL · LEAD · GAP · OPORTUNIDADE                           │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       CASCO ORIGINAL                        │
│                                                             │
│ Produto para usuário leigo                                  │
│ boxes · hierarquia · texto grande · linguagem clara         │
│ nenhum código técnico na camada principal                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Bot de Fontes

### Missão

O Bot de Fontes é o dono do **Universo Oficial de Fontes**.

Não é apenas um crawler de descoberta. Ele usa LLM para fazer o trabalho longo e chato antes de uma fonte ser entregue ao Scrap.

```text
DESCOBRIR
   ↓
ABRIR A FONTE
   ↓
ENTENDER QUEM É
   ↓
LER AMOSTRAS REAIS
   ↓
ENTENDER O QUE PUBLICA
   ↓
VALIDAR VALOR AGRÍCOLA
   ↓
VALIDAR LOCAL/REGIÃO
   ↓
VALIDAR FREQUÊNCIA
   ↓
VALIDAR CONFIABILIDADE
   ↓
CLASSIFICAR DOMÍNIOS
   ↓
IDENTIFICAR MELHOR ROTA DE CAPTURA
   ↓
ENTREGAR SOURCE CONTRACT
   ↓
READY FOR COLLECTION
```

### O LLM do Bot de Fontes deve responder

Para cada candidata:

```text
Quem é esta fonte?
É real?
É agrícola?
Em que país/região atua?
Que culturas cobre?
Que temas cobre?
Publica conteúdo original ou só replica?
Qual a frequência?
Qual o valor potencial?
É institucional, técnico, comercial, científico ou social?
Tem histórico útil?
Tem conteúdo atual?
Quais URLs/perfis/canais devem ser monitorados?
Qual tipo de conteúdo costuma publicar?
Qual capacidade do Scrap parece adequada?
Vale entrar no universo?
```

Se não puder provar algo: `NAO_SEI`.

### Source Contract

Uma fonte aprovada deve chegar ao Sintonia Scrap com:

```text
SOURCE_ID
NOME
URL / PERFIL / CANAL
TIPO_DE_FONTE
PAIS
REGIAO
IDIOMA
DOMINIOS
CULTURAS_CONHECIDAS
TEMAS_CONHECIDOS
TIPOS_DE_CONTEUDO
FREQUENCIA_ESPERADA
ROTA_PREFERIDA
ROTAS_ALTERNATIVAS
DATA_DA_ULTIMA_VALIDACAO
STATUS
EVIDENCIA_DA_VALIDACAO
```

### O Bot de Fontes não faz

- scraping de produção;
- download;
- transcrição;
- geração de oportunidade;
- classificação comercial;
- publicação;
- Casco.

---

## 5. Universo de Fontes deve ser balanceado

O Sintonia não pode virar uma máquina que lê apenas sites.

O universo precisa conter de forma contínua:

1. **Oficial / institucional:** ministérios, regiões, CREA, fitossanitário, reguladores, órgãos meteorológicos, estatística oficial.
2. **Agronômico regional:** boletins, cooperativas, consórcios, técnicos, extensão, associações.
3. **Social de campo:** LinkedIn, Instagram, YouTube, agrônomos, produtores, consultores, organizações agrícolas.
4. **Pesquisa:** pesquisadores, universidades, papers, projetos, conferências, laboratórios.
5. **Clima / agrometeorologia:** previsão, estações, boletins, anomalias, alertas.
6. **Mercado:** preço, custo, oferta, demanda, exportação, importação, produção, área, margens.
7. **Concorrência:** empresas, produtos, campanhas, eventos, field days, registros, mídia social, comunicação comercial.
8. **Regulatório:** autorizações, cancelamentos, modificações, restrições, novas regras.
9. **ADAMA / referência:** portfólio, labels, usos autorizados, doses, produtos, registros.

### Regra de diversidade

Não existe quota rígida artificial. Mas nenhuma fonte, domínio ou canal pode dominar sozinho a visão do Sintonia.

Uma rodada saudável pode combinar:

```text
boletim regional
+
post de agrônomo
+
alerta fitossanitário
+
previsão agrometeorológica
+
movimento de concorrente
+
pesquisa
+
mercado
```

Não aceitar como padrão:

```text
20 páginas consecutivas do mesmo site
```

---

## 6. Sintonia Scrap

### Definição

```text
FERRAMENTA DE CAPTURA
+
ORQUESTRADOR TÉCNICO DE CAPACIDADES
```

O Bot de Fontes decide **quem merece ser acompanhado**.

O Sintonia Scrap decide **como capturar tecnicamente uma fonte já aprovada**.

### Responsabilidades

Recebe Source Contract e:

- escolhe adaptador/capacidade;
- executa captura;
- usa fallback técnico quando necessário;
- extrai corpo útil;
- captura mídia;
- extrai áudio;
- gera transcrição;
- preserva URL;
- preserva data;
- preserva autor/perfil/canal;
- produz hash;
- entrega conteúdo normalizado;
- registra falha técnica.

O Scrap não decide relevância comercial.

### Capacidades existentes a aproveitar

- HTML;
- PDF;
- YouTube;
- Instagram;
- LinkedIn;
- download de mídia;
- áudio;
- transcrição local;
- busca/descoberta assistida;
- OpenAlex / ORCID;
- Apify quando necessário.

No fim de semana, capacidade existente deve ser conectada antes de construir capacidade nova.

---

## 7. O que captar por canal

### HTML

```text
URL
SOURCE_ID
título
autor
data de publicação
data de coleta
texto principal
links relevantes
hash
```

### PDF

```text
URL
SOURCE_ID
título
data
texto
páginas relevantes
tabelas quando recuperáveis
hash
```

### Instagram

```text
URL
perfil
data do post
legenda
texto visível
transcrição
hashtags úteis
links
comentários selecionados quando houver motivo
```

### LinkedIn

```text
URL do post
autor
organização
data
texto
vídeo
legenda
transcrição
links/documentos associados
```

### YouTube

```text
canal
URL
data
título
descrição
legenda
transcrição
comentários relevantes quando aplicável
```

### Áudio / vídeo

```text
origem
URL
data
transcrição
timestamps quando úteis
idioma
```

### Ciência / pesquisadores

```text
pesquisador
instituição
obra
data
tema
culturas
alvos
abstract/resumo permitido
URL/DOI
```

### Comentários

Comentários podem ajudar a identificar reação, linguagem regional, perguntas recorrentes, dores e novos sinais.

Mas:

- comentário não vira automaticamente fato;
- repost não vira fonte independente;
- comentário não substitui evidência agronômica forte.

---

## 8. Política de RAW — temporário por padrão

O Sintonia não deve acumular milhões de arquivos brutos indefinidamente.

### Regra padrão

```text
CAPTURA RAW
    ↓
VALIDA INTEGRIDADE
    ↓
EXTRAI TEXTO / TRANSCRIÇÃO
    ↓
GERA HASH
    ↓
GERA CÁPSULA DE EVIDÊNCIA
    ↓
RAW EXPIRA
```

### O que fica permanentemente

```text
SOURCE_ID
URL ORIGINAL
DOCUMENT_ID
DATA DE PUBLICAÇÃO
DATA DE COLETA
AUTOR / PERFIL / CANAL
TIPO DE FONTE
IDIOMA
HASH DO ORIGINAL
TEXTO CANÔNICO
TRANSCRIÇÃO, SE HOUVER
TRECHOS DE EVIDÊNCIA USADOS
METADADOS NECESSÁRIOS
PROVENIÊNCIA
```

### Exceções de retenção do original

Manter por mais tempo quando for:

- label/bula;
- documento regulatório;
- referência ADAMA;
- documento que muda por versão;
- conteúdo sem URL reproduzível;
- conteúdo social ou vídeo com alto risco de desaparecer;
- evidência de uma oportunidade publicada;
- documento explicitamente marcado como histórico/canônico.

Mesmo nesses casos, retenção pode ser seletiva e comprimida.

**Princípio:** RAW é staging, não museu.

---

## 9. Opus Leitor — fatos

A primeira Intelligence não tenta vender. Ela lê o conteúdo e produz fatos.

```text
FACT_ID
O_QUE_ACONTECEU
DATA_DO_FATO
PRECISAO_DA_DATA
DATA_DA_PUBLICACAO
LOCAL_DO_FATO
REGIAO
PAIS
CULTURA
FASE_DA_CULTURA
PRAGA
DOENCA
PROBLEMA
NECESSIDADE
EMPRESA
ORGANIZACAO
PESSOA
PESQUISADOR
PRODUTO_MENCIONADO
CONCORRENTE
NUMEROS
UNIDADES
EVIDENCIA_LITERAL
SOURCE_ID
DOCUMENT_ID
```

Regras:

```text
data do post != data do fato
local do autor != local do fato
local da empresa != local do fato
publicação != validade
edição != acontecimento
```

Se não souber: `NAO_SEI`.

---

## 10. Opus Intelligence — sinais

Um sinal responde: **algo está acontecendo que merece atenção?**

Exemplos:

- aumento de doença;
- nova pressão de praga;
- calor/chuva mudando risco;
- custo subindo;
- preço mudando;
- concorrente lançando produto;
- pesquisador alertando resistência;
- mudança regulatória;
- janela agronômica se aproximando;
- produtor relatando problema;
- nova prática ganhando tração.

```text
SIGNAL_ID
TEMA
CULTURA
PROBLEMA
LOCAL
PERIODO
O_QUE_MUDOU
POR_QUE_IMPORTA
O_QUE_PODE_ACONTECER
FACT_IDS
SOURCE_IDS
FONTES_INDEPENDENTES
CONFIANCA
O_QUE_FALTA_CONFIRMAR
```

---

## 11. Domínios de conhecimento

Todos os domínios ficam disponíveis ao motor de cruzamentos.

### Portfólio ADAMA
produto, ativo, categoria, culturas, alvos, registros, doses, restrições, status, frescor.

### Label / regulatório
produto, cultura, alvo, autorização, dose, restrição, carência, data, versão, mudança.

### Fenologia
cultura, região, fase atual, fase seguinte, período, fonte, atualização.

### Crop Window
cultura, região, janela, tipo de ação, início, fim, precisão, fonte.

### Clima
região, período, chuva, temperatura, umidade, vento, anomalia, previsão, confiança.

### Fitossanitário
cultura, praga/doença, região, pressão, fase, data, severidade, evidência.

### Mercado
cultura, região, indicador, preço, produção, área, oferta, demanda, custo, variação, período.

### Concorrência
empresa, produto, cultura, alvo, região, campanha, evento, mensagem, registro, movimento, data.

### Ciência
tema, descoberta, resistência, prática, mecanismo, culturas, alvos, impacto, data.

### Pesquisadores
nome, instituição, região, especialidade, culturas, alvos, publicações, projetos, eventos, LinkedIn, YouTube, temas emergentes.

### Social / Campo
autor, tipo, região, cultura, problema, observação, data, evidência.

### Geografia
país, região, província, comuna/local, culturas relevantes, contexto agrícola.

### Histórico
tema, cultura, região, período histórico, evento, frequência, anomalia.

---

## 12. Motor de cruzamentos — todos podem conversar com todos

O sistema não deve ter uma lista rígida de "se A então B".

**Regra:** o Opus recebe os objetos relevantes e pode cruzar qualquer combinação de dimensões quando houver relação lógica e evidência.

### Clima

- Clima × Fenologia → risco climático na fase atual.
- Clima × Crop Window → janela favorável, antecipada, atrasada ou inviável.
- Clima × Fitossanitário → aumento/redução de pressão de doença/praga.
- Clima × Portfólio → categorias potencialmente relevantes.
- Clima × Label → soluções autorizadas possíveis.
- Clima × Mercado → risco de produção, oferta e preço.
- Clima × Social/Campo → confirmar efeito real no campo.
- Clima × Geografia → intensidade regional.
- Clima × Histórico → normalidade ou anomalia.

### Fenologia

- Fenologia × Crop Window → momento agronômico real.
- Fenologia × Fitossanitário → problemas relevantes na fase.
- Fenologia × Portfólio → produtos potencialmente relevantes.
- Fenologia × Label → uso compatível.
- Fenologia × Clima → risco específico da fase.
- Fenologia × Mercado → impacto econômico sobre cultura relevante.
- Fenologia × Social/Campo → checar relatos contra fase real.

### Crop Window

- Crop Window × Portfólio → produtos que podem ter ação agora.
- Crop Window × Label → usos autorizados.
- Crop Window × Fitossanitário → alvo presente no momento correto.
- Crop Window × Clima → timing operacional.
- Crop Window × Mercado → prioridade por valor econômico.
- Crop Window × Concorrência → campanha concorrente na mesma janela.
- Crop Window × Histórico → janela antecipada/atrasada.

### Fitossanitário

- Fitossanitário × Portfólio → existe solução ADAMA relacionada?
- Fitossanitário × Label → existe autorização real?
- Fitossanitário × Fenologia → problema faz sentido na fase?
- Fitossanitário × Clima → ambiente favorece o problema?
- Fitossanitário × Ciência → resistência, nova pressão ou mudança técnica.
- Fitossanitário × Pesquisadores → quem estuda/monitora o problema?
- Fitossanitário × Social/Campo → confirmação precoce e dispersão territorial.
- Fitossanitário × Histórico → surto novo ou recorrente?
- Fitossanitário × Mercado → impacto econômico potencial.
- Fitossanitário × Concorrência → quem está posicionando solução.

### Portfólio

- Portfólio × Label → vendabilidade real.
- Portfólio × Fitossanitário → aderência ao problema.
- Portfólio × Crop Window → timing.
- Portfólio × Mercado → prioridade comercial.
- Portfólio × Concorrência → defesa, diferenciação e lacunas.
- Portfólio × Ciência → adequação técnica e futuras pressões.
- Portfólio × Geografia → onde o produto faz sentido.
- Portfólio × Histórico → padrões recorrentes de uso/oportunidade.

### Label / Regulatório

- Label × Portfólio → uso autorizado.
- Label × Fitossanitário → alvo comprovado.
- Label × Crop Window → timing compatível.
- Label × Regulatório → mudança de autorização/restrição.
- Label × Concorrência → comparação de espaço autorizado.
- Label × Mercado → nova autorização em cultura relevante.
- Label × Geografia → aplicabilidade territorial quando pertinente.

### Mercado

- Mercado × Cultura × Região → onde existe maior valor econômico.
- Mercado × Clima → risco de oferta/preço.
- Mercado × Fitossanitário → custo potencial de um problema.
- Mercado × Portfólio → priorização comercial.
- Mercado × Concorrência → intensidade competitiva.
- Mercado × Histórico → anomalia.
- Mercado × Social → confirmação de dor econômica.

### Concorrência

- Concorrência × Portfólio → defesa de categoria/produto.
- Concorrência × Fitossanitário → problema que o concorrente tenta capturar.
- Concorrência × Crop Window → campanha no momento agronômico.
- Concorrência × Mercado → pressão em culturas valiosas.
- Concorrência × Social → intensidade de comunicação e reação.
- Concorrência × Regulatório → novo registro ou limitação.
- Concorrência × Geografia → onde está investindo.

### Ciência / Pesquisadores

- Ciência × Fitossanitário → resistência, mecanismos e mudanças.
- Ciência × Portfólio → relevância técnica ou gap.
- Ciência × Label → potencial futuro, nunca confundido com autorização atual.
- Ciência × Pesquisadores → quem lidera o tema.
- Ciência × Geografia → onde a pesquisa ocorre.
- Ciência × Social → adoção/conversa no campo.
- Pesquisador × Cultura × Região → especialistas importantes para aquela realidade.

### Social / Campo

- Social × Oficial → sinal precoce versus confirmação institucional.
- Social × Fitossanitário → pressão percebida.
- Social × Clima → efeito real no campo.
- Social × Mercado → dor econômica percebida.
- Social × Concorrência → mensagem e recepção.
- Social × Pesquisadores → circulação de conhecimento.
- Social × Geografia → localização real do relato.

### Histórico

Histórico pode cruzar com qualquer domínio para detectar recorrência, anomalia, antecipação, atraso ou mudança estrutural.

---

## 13. Cruzamentos de alta ordem

### Oportunidade comercial

```text
CLIMA
+
FENOLOGIA
+
CROP WINDOW
+
PRESSÃO FITOSSANITÁRIA
+
PORTFÓLIO
+
LABEL
+
REGIÃO
=
POSSÍVEL OPORTUNIDADE
```

### Alerta precoce

```text
SOCIAL DE CAMPO
+
BOLETIM OFICIAL
+
PESQUISADOR
+
CIÊNCIA
+
REGIÃO
=
SINAL VALIDADO
```

### Priorização comercial

```text
MERCADO
+
CULTURA
+
REGIÃO
+
CROP WINDOW
+
PORTFÓLIO
+
LABEL
=
PRIORIDADE DE AÇÃO
```

### Defesa competitiva

```text
CONCORRENTE
+
CAMPANHA
+
CROP WINDOW
+
MERCADO
+
PORTFÓLIO ADAMA
+
LABEL
=
AÇÃO DEFENSIVA / CONTRAPOSICIONAMENTO
```

### Oportunidade futura

```text
CIÊNCIA
+
PESQUISADORES
+
RESISTÊNCIA
+
FITOSSANITÁRIO
+
FENOLOGIA
+
GEOGRAFIA
=
FUTURE RADAR
```

---

## 14. Camada comercial

### OPORTUNIDADE

Só existe quando houver:

```text
FATO/SINAL REAL
+
CULTURA
+
LOCAL
+
PROBLEMA/NECESSIDADE
+
JANELA AGRONÔMICA
+
TIMING / POR QUE AGORA
+
PRODUTO ADAMA
+
LABEL/AUTORIZAÇÃO COMPATÍVEL
+
AÇÃO COMERCIAL CONCRETA
=
OPORTUNIDADE
```

### LEAD

Existe contexto comercial interessante, mas falta uma peça para oferta fechada.

### SINAL

Algo merece atenção, mas ainda não há caminho comercial suficientemente fechado.

### GAP

Existe necessidade real, mas nenhuma solução ADAMA foi comprovada.

Zero oportunidades é uma saída válida.

---

## 14A. Caso vivo e investigação ativa

O Sintonia não deve terminar o raciocínio no primeiro lote de documentos.

Quando um fato gerar SINAL, LEAD, GAP ou possível OPORTUNIDADE, a Intelligence deve tratar isso como um **caso vivo**:

```text
SINAL INICIAL
↓
CASE_ID
↓
O QUE JÁ SEI?
↓
O QUE FALTA?
↓
EVIDENCE_REQUEST
↓
BOT DE FONTES PROCURA FONTES ADICIONAIS
↓
SINTONIA SCRAP CAPTURA
↓
INTELLIGENCE INCORPORA AO MESMO CASO
↓
LINHA DO TEMPO
↓
NOVOS CRUZAMENTOS
↓
RECLASSIFICA
```

A busca deve procurar convergência entre fontes independentes quando isso puder mudar a interpretação, priorizando conforme o caso:

```text
órgão oficial
boletim regional
cooperativa
associação
agronomia de campo
pesquisador
clima
mercado
concorrência
social
```

Não gerar vários cards para documentos sobre o mesmo caso. Documentos novos alimentam o mesmo `CASE_ID`.

### Timeline obrigatória para casos

Todo SINAL, LEAD, GAP ou OPORTUNIDADE deve poder montar uma linha do tempo:

```text
TIMELINE_EVENT
data
título curto
o que acrescentou ao caso
tipo de fonte
URL original
SOURCE_ID
DOCUMENT_ID
```

No Casco, Opportunity Radar e Future Radar usam a timeline como forma principal de mostrar **como o caso evoluiu**.

Cada ponto da timeline é clicável e abre o documento original.

Não mostrar uma parede de documentos e trechos na primeira experiência do usuário. A lista completa de evidências fica recolhida para auditoria.

---

## 15. Separação por ferramenta do Casco

### Opportunity Radar

Recebe somente `OPORTUNIDADE`.

Cada card deve responder, sem código técnico:

- o que está acontecendo;
- onde;
- cultura;
- problema;
- por que agora;
- janela;
- produto ADAMA;
- ação recomendada.

### Future Radar

Recebe `LEAD` e `SINAL`.

O usuário deve entender:

- o que está se formando;
- por que acompanhar;
- o que falta para virar ação;
- quando pode ficar importante.

### Portafoglio

Mostra:

```text
PORTFÓLIO ATUAL
+
USOS
+
LABEL
+
GAPS
```

### Crop Windows

Recebe:

```text
CULTURA
REGIÃO
FASE
JANELA ATUAL
PRÓXIMA JANELA
PROBLEMAS ASSOCIADOS
CLIMA RELEVANTE
```

#### Confiança e frescor da Crop Window — obrigatório por cultura

A Crop Window não pode mostrar apenas uma janela. O usuário precisa saber imediatamente **quando aquela leitura foi verificada e se ainda é confiável para decisão**.

Cada cultura/região exibida deve carregar um box visual curto de confiança:

```text
AGGIORNAMENTO
Verificata il: DD MMM YYYY

FONTE
fonte canônica / boletim que sustenta a fase

COPERTURA
região / território ao qual a leitura se aplica

STATO
AGGIORNATA | PARZIALE | DA AGGIORNARE | NON VERIFICATA
```

Regras:

- **AGGIORNATA**: existe evidência recente suficiente para a cultura/região e a verificação está dentro da cadência definida para aquele tipo de dado.
- **PARZIALE**: existe evidência recente, mas faltam parte da geografia, fase ou cobertura necessária.
- **DA AGGIORNARE**: existe referência, mas ela já saiu da cadência de atualização esperada.
- **NON VERIFICATA**: não existe evidência recente suficiente para afirmar que a janela representa o estado atual.

Não escrever “segura”, “confiável” ou equivalente apenas porque existe uma data. A confiança vem da combinação:

```text
FONTE
+
DATA
+
REGIÃO
+
FASE
+
COBERTURA
+
FRESCOR
```

Se a fonte declarar um período de validade, mostrar também:

```text
VALIDA FINO A
DD MMM YYYY
```

Se a fonte não declarar validade, **não inventar data de validade**.

Na primeira camada, o box deve ser compacto e visual, por exemplo:

```text
✓ AGGIORNATA
Verificata 02 OTT 2026
Veneto
```

ou:

```text
! DA AGGIORNARE
Ultima verifica 02 SET 2026
```

O detalhe pode explicar fonte, evidência, cobertura e limitações.

A cor do estado deve reutilizar o Design System ADAMA; não criar uma paleta paralela.

Importante: enquanto houver versões concorrentes de Crop Windows ou fenologia sem atualização corrente, o Casco não pode apresentar a janela como verificada. Deve mostrar o estado real de frescor.

### Label Intelligence

Recebe mudanças de autorização, produtos, culturas, alvos, restrições, doses e frescor da referência.

### Market Pulse

Recebe preços, produção, área, oferta, demanda, custos, movimentos e impactos.

### Research / Science / Researchers

Recebe pesquisadores, instituições, temas, papers, resistência, tendências, ciência emergente e especialistas por cultura/região.

### Competition

Recebe produto, campanha, evento, novo registro, mensagem, cultura, alvo, região e timing.

### Action Brief

Síntese por LLM:

```text
O QUE PRECISA DE AÇÃO AGORA
O QUE PRECISA SER MONITORADO
RISCO PRINCIPAL
OPORTUNIDADE PRINCIPAL
MOVIMENTO DE CONCORRENTE
JANELA QUE ESTÁ CHEGANDO
```

---

## 16. Casco — produto para leigo

O Casco é produto, não console de engenharia.

### Regra visual atualizada

Opportunity, Lead e Signal pertencem à mesma família visual de caso. O card usa a linguagem visual forte do Opportunity Radar e o Design System ADAMA:

```text
ÍCONE / CATEGORIA DO PROBLEMA
COR ADAMA DA CATEGORIA
PROBLEMA
CULTURA · REGIÃO
STATUS
JANELA
PRODUTO, QUANDO COMPROVADO
ESPLORA
```

O card deve ter o mínimo de lettering possível.

```text
PRIMEIRA CAMADA = VER
CLIQUE = ENTENDER
DETALHE = PROVAR
```

No clique, a tela vira um dashboard do caso, priorizando blocos visuais e a timeline:

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
```

Somente os blocos com informação útil aparecem.

As fontes reais não ficam empilhadas como uma lista longa. A timeline é o caminho principal; clicar em um evento abre a fonte original. Evidências completas continuam disponíveis em área recolhida de auditoria.

### Regra principal

O usuário deve conseguir abrir o portal e entender a página sem conhecer:
