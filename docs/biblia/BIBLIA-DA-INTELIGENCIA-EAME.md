# BÍBLIA DA INTELIGÊNCIA — SINTONIA EAME

**Data:** 2026-09-08 · **Linha:** paralela (documentação, contratos, casos adversariais,
decisões) · **Implementação nesta linha:** nenhuma.

---

## 0 · O QUE ESTA BÍBLIA É

É o **livro de leis** deste repositório, reunido num lugar só.

As leis já existiam. Estavam escritas — e é por isso que este documento pôde ser
escrito. O que não existia era o **índice**: uma varredura deste repositório encontra
**259 formas escritas distintas** de lei do tipo `A ≠ B`, espalhadas por **56
documentos**. Duzentas e cinquenta e nove formas não são duzentas e cinquenta e nove
leis: a mesma lei
aparece como `SOURCE FAILURE != ZERO`, `SOURCE_FAILURE != ZERO` e `FONTE BLOQUEADA !=
FONTE INEXISTENTE`. Três grafias, uma lei.

> **UMA LEI COM TRÊS NOMES É UMA LEI QUE NINGUÉM INDEXA.**
> **E UMA LEI QUE NINGUÉM INDEXA É REDESCOBERTA PELO CUSTO.**

Este documento não inventa lei nenhuma. Cada linha abaixo aponta para onde a lei foi
aprendida — quase sempre um erro real, cometido aqui, com data — e diz se hoje existe
**alguém executável** que a recusa.

### O que ela NÃO é

- **Não é decisão de produto.** Decisão de produto entra em
  `docs/decisoes/DIARIO-DE-DECISOES.md`, e só quando dada por quem decide.
- **Não é medidor.** Nenhum número deste documento é fonte: todos apontam para o dono.
  Um número que vive num documento é lembrança de que alguém mediu.
- **Não é substituto dos documentos canônicos.** `ARQUITETURA-DE-PRODUTO-ATUAL.md`
  continua vencendo quando dois documentos discordarem sobre o produto.
- **Não fecha portão nenhum.** Nada aqui muda o estado de nada. O estado vive nos
  medidores da seção 6.

### Como se lê a coluna GUARDA

Cada lei carrega o estado da sua defesa, e o estado foi **medido** — por varredura de
`tests/`, `supabase/tests/`, `scripts/` e `italia-portale/audit/` — não presumido:

| GUARDA | Significado |
|---|---|
| **EXECUTÁVEL** | existe teste, portão ou medidor que reprova a violação. O nome está escrito. |
| **SÓ PROSA** | a lei está escrita e nada a defende. Violá-la hoje não acende nada. |
| **NÃO MEDIDO** | não se procurou, ou não se conseguiu procurar daqui. |

**SÓ PROSA não é acusação, é inventário.** Uma lei sem guarda ainda é melhor que uma lei
esquecida. O que ela não pode é passar por defendida.

---

## 1 · A CADEIA, E O QUE CADA FRONTEIRA PROMETE

```
FONTE → EVIDÊNCIA → DADO → CRUZAMENTO → CAPACIDADE → FERRAMENTA → PORTAL
```

A cadeia do README diz a **ordem**. Esta seção diz o **contrato** de cada travessia: o
que se promete ao entregar do lado esquerdo para o lado direito, e o que a travessia
tem direito de recusar.

| # | Fronteira | O que quem entrega promete | O que quem recebe pode recusar |
|---|---|---|---|
| F1 | FONTE → EVIDÊNCIA | que a fonte existe, que é acessível por método descrito, e que sobrou artefato preservável | evidência sem artefato: fica HIPÓTESE |
| F2 | EVIDÊNCIA → DADO | que o dado sai da evidência por derivação escrita, e que a derivação tem dono | dado cuja derivação não está escrita |
| F3 | DADO → CRUZAMENTO | que existe **chave** declarada, e que a chave é a mesma dos dois lados | cruzamento por semelhança de nome |
| F4 | CRUZAMENTO → CAPACIDADE | que o cruzamento sustenta a afirmação, e que a afirmação diz o que **não** prova | capacidade sem os cinco itens do README |
| F5 | CAPACIDADE → FERRAMENTA | que a ferramenta entrega a capacidade sem inventar nada além dela | ferramenta que afirma mais que a capacidade |
| F6 | FERRAMENTA → PORTAL | que o que atravessa foi declarado campo a campo — lista de permissão, não de proibição | campo não declarado: fica de fora, e o silêncio é o padrão |
| F7 | PORTAL → PESSOA | que a tela carrega o estado visível do que mostra | tela que apresenta DEMONSTRATION sem dizer |

**A fronteira que este repositório mediu e sabe que perde é a F6-anterior** — a que o
CHECKPOINT chama `ACERVO → PACOTE`. Não é a última, é a que precede a última: o pacote
não pede campos que o acervo tem. Ver seção 6.

### A lei das fronteiras

> **O QUE NÃO ATRAVESSA UMA LINHA NÃO PRECISA SER FILTRADO DEPOIS DELA.**

É a razão pela qual `site_v21_ingest.py` usa lista de permissão campo a campo. Recusar
na tela significa que o texto **viajou até o navegador do cliente** para só então ser
escondido. Uma cor de CSS trocada, um `title=` esquecido, um `JSON.stringify` num painel
de depuração, e ele aparece.

> **PROSA QUE NÃO EMBARCA NÃO VAZA.**

---

## 2 · OS ESTADOS, E A REGRA DE TRÂNSITO ENTRE ELES

Os quatro estados de evidência (`COMPROVADO` · `INFERÊNCIA` · `HIPÓTESE` · `NÃO SEI`) e
os quatro estados de tela (`REAL DATA` · `REAL DATA + DERIVED ANALYSIS` ·
`DEMONSTRATION` · `CONCEPT ONLY`) estão no README. O que o README não diz — e a bíblia
diz — é **como se anda entre eles**:

| Movimento | Permitido? | Exigência |
|---|---|---|
| COMPROVADO → HIPÓTESE | **sempre** | nenhuma. Rebaixar nunca é retrocesso. |
| HIPÓTESE → COMPROVADO | condicional | evidência preservável anexada |
| NÃO SEI → qualquer coisa | condicional | a medição, não a plausibilidade |
| qualquer coisa → NÃO SEI | **sempre** | descobrir que não se sabia é resultado |
| NÃO MEDIDO → ZERO | **nunca** | não há exigência que autorize: são coisas diferentes |

A última linha é a lei mais cara deste repositório e a que ele já violou. Está na seção
4, caso A-02.

### As três ausências que não se colapsam

Este repositório distingue **três** maneiras de não ter um dado, e confundi-las é o modo
de falha mais silencioso que existe aqui:

| Ausência | Significa | Quem é o dono |
|---|---|---|
| `NÃO SEI` | a fonte não informa | a fonte |
| `NOT_PRESERVED` | tivemos e não guardamos — **confissão** | nós |
| `NÃO MEDIDO` | não olhamos, ou não podemos olhar daqui | a medição |

`NOT_PRESERVED` foi criado porque oito execuções antigas de coleta não têm
`ACTOR_VERSION`, `STARTED_AT`, `FINISHED_AT`, `DATASET_ID` nem `COST_USD`, e nunca terão:
não foram capturados. Chamar isso de `NÃO SEI` seria culpar a fonte por um descuido
nosso.

---

## 3 · A LEI DAS DISTINÇÕES

Organizada por família. A coluna **APRENDIDA EM** diz onde custou. A coluna **GUARDA**
foi medida em 2026-09-08.

### 3.1 · FONTE E MEDIÇÃO

| Lei | O erro que ela impede | Aprendida em | GUARDA |
|---|---|---|---|
| **SOURCE FAILURE ≠ ZERO** | publicar zero quando a resposta é «não medimos». Zero é uma afirmação sobre o mundo; não medir não é. | seção I do RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA, corrigido depois de publicado | EXECUTÁVEL — 4 arquivos de teste, 11 medidores |
| **HTTP 200 ≠ FONTE VIVA** | tratar resposta de servidor como prova de que o dado existe | ATLAS-DE-FONTES-EAME | EXECUTÁVEL — 18 medidores |
| **SUCCEEDED DA PLATAFORMA ≠ EXECUÇÃO BEM-SUCEDIDA** | um ator devolveu `SUCCEEDED`, `exitCode` limpo e **zero itens**, com `statusMessage: free user run limit reached`. Cota esgotada que se apresenta como sucesso. | MISSÃO 10B, portão `RUN_MANIFEST` | EXECUTÁVEL — `SUCCEEDED` com zero itens vira `PARTIAL` carregando a mensagem da plataforma |
| **FONTE BLOQUEADA ≠ FONTE INEXISTENTE** | converter recusa técnica em ausência do mundo | RELATORIO-DE-ROTAS-APIFY-ES | EXECUTÁVEL |
| **FIRST SNAPSHOT ≠ NO CHANGE** | a primeira captura não prova estabilidade; prova só que houve uma captura | REGUA-DE-CHANGE-EVENT-EAME | **SÓ PROSA** — 3 documentos, 0 testes, 0 medidores |
| **PRESENÇA NO INVENTÁRIO ≠ BYTES CONFERIDOS** | contar arquivo listado como arquivo íntegro | gate do RAW espanhol | EXECUTÁVEL — `RAW_CONTENT_INTEGRITY_GATE`, 196 sha256 reconferidos |
| **DINHEIRO GASTO ≠ DADO PRESERVADO** | rota paga que devolveu e não guardou o bruto | `PAID_RAW_POLICY` | EXECUTÁVEL |

### 3.2 · LUGAR

| Lei | O erro que ela impede | Aprendida em | GUARDA |
|---|---|---|---|
| **SOURCE_LOCATION ≠ FACT_LOCATION** | o país de quem publica virar o país do fato | contrato de proveniência, desde o início | EXECUTÁVEL — envelope obrigatório em toda amostra publicada |
| **PLACE_MENTION ≠ FACT_LOCATION** | lugar citado num texto sustentar sozinho o lugar do fato. O comentário do código dizia que `CITADO` é «o balde mais fraco» e a trava deixava `CITADO` sustentar o lugar sozinho: **o comentário e a trava discordavam**. | migration 015, corrigido na 017 | EXECUTÁVEL — 3 testes, 6 medidores; `v_conteudo_localizacao` publica `fact_sustentado_apenas_por_mencao` |
| **BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT** | quatro lugares diferentes de uma mesma pessoa colapsados em um | conferência de localização, cicatriz A | EXECUTÁVEL — hoje PROVED; foi PARTIAL até a 018 |
| **PROVINCIAL ≠ REGIONAL** | subir a precisão de uma medida sem que a fonte a tenha dado | régua italiana | EXECUTÁVEL |
| **NOT_IN_GAZETTEER ≠ NOT_A_PLACE** | o dicionário incompleto virar juízo sobre o mundo | camada de geografia | EXECUTÁVEL — 3 testes, 6 medidores |
| **SOURCE SAYS REGION ≠ INVENT MUNICIPALITY** | descer a escada de precisão por conveniência de tela | RELATORIO-LUGAR-DO-FATO | EXECUTÁVEL |
| **ETIQUETA DE LUGAR DA PLATAFORMA ≠ FATO** | a geo-tag do Instagram virar local do fato agronômico | conferência de localização, cicatriz J | EXECUTÁVEL |

### 3.3 · TEMPO

| Lei | O erro que ela impede | Aprendida em | GUARDA |
|---|---|---|---|
| **PUBLISHED_AT ≠ FACT_TIME** | `f_relevancia_ao_caso` devolvia `UNRELATED` para documento publicado **depois** da janela do caso — tratando data de publicação como data do fato. Um documento de setembro relata um fato de junho. | migration 015, corrigido na 017 | EXECUTÁVEL — 4 testes, 29 medidores; hoje devolve `CONTEXT_ONLY` |
| **CAPTURE ≠ REGISTRATION** | a hora em que olhamos virar a hora em que o fato foi registrado | migration 013 | EXECUTÁVEL — 5 testes, 6 medidores |
| **SOURCE_DATE ≠ CAPTURED_AT** | a data do documento virar a data da coleta | contrato de captura | EXECUTÁVEL |
| **ACTIVE ≠ ACTIVE NA DATA QUE SE PODE NOMEAR** | o selo ATTIVO afirma o **presente**. Sem data de verificação, afirma hoje o que se observou num dia que ninguém consegue nomear. 27 anúncios declaram ACTIVE; nenhum traz a data — que existe no acervo em 414/414. | CHECKPOINT §6 | EXECUTÁVEL desde esta missão — `fronteira-acervo-pacote.mjs` mede e devolve 0 |
| **EXPIRY ≠ WITHDRAWAL** | vencimento de registro virar retirada de produto | camada regulatória espanhola | EXECUTÁVEL — 5 testes |
| **PRORROGAÇÃO ≠ RENOVAÇÃO** | dois atos administrativos diferentes contados como um | régua italiana | EXECUTÁVEL |

### 3.4 · IDENTIDADE

| Lei | O erro que ela impede | Aprendida em | GUARDA |
|---|---|---|---|
| **NAME ≠ HANDLE ≠ URL ≠ PROFILE ≠ PERSON ≠ ORGANIZATION** | seis coisas diferentes tratadas como uma. É a cadeia de identidade inteira em uma linha. | MODELO-DE-IDENTIDADE-EAME | EXECUTÁVEL |
| **SEARCH_HIT ≠ PERSON** | o envelope de uma busca virar uma pessoa cadastrada | BR-16 | EXECUTÁVEL — `SEARCH_HIT_NAO_E_PESSOA` |
| **AGGREGATOR ≠ HUMAN_VOICE** | uma página que republica virar sensor humano | BR-16 | EXECUTÁVEL — `AGGREGATOR_NAO_E_HUMAN_SENSOR` |
| **PERFIL DE PESSOA ≠ FICHA DE PESSOA** | ler a página e cadastrar a origem são **dois atos**, e um só não basta. Este caso não estava na lista da missão e existe mesmo assim. | BR-16, sexto caso | EXECUTÁVEL — `PERFIL_DE_PESSOA_SEM_FICHA_DE_PESSOA` |
| **NAME_MATCH ≠ PERSON_PROOF** | homonímia virar identificação | camada de voz | EXECUTÁVEL — 4 medidores, 0 testes |
| **A IDENTIDADE NÃO CARREGA A RODADA** | `TOKEN`, `RUN_ID`, `DATASET_ID` e `CAPTURED_AT` entrarem na chave, fazendo duas rodadas produzirem dois conteúdos | BR-14 | EXECUTÁVEL — teste lê a definição real da constraint e procura os quatro nomes lá dentro |
| **UM NOME QUE DIFERE SÓ NA CAIXA NÃO É UM NOME DIFERENTE** | `rm -rf Scripts` apagou os 75 arquivos de `scripts/` porque no Windows são a mesma pasta | madrugada EAME | SÓ PROSA — e o custo já foi pago |

### 3.5 · COLETA E RESILIÊNCIA

| Lei | O erro que ela impede | Aprendida em | GUARDA |
|---|---|---|---|
| **PROCESS_CRASH ≠ LOST_COLLECTION** | o progresso morar na memória do processo | BR-19/BR-20 | EXECUTÁVEL — o progresso mora no banco; teste A→H |
| **TOKEN_EXHAUSTED ≠ COLLECTION_LOST** | a chave acabar e a coleta recomeçar do zero | BR-21 | EXECUTÁVEL — token 2 assume e chama só `u3 u4 u5` |
| **POOL É RESILIÊNCIA, NÃO VOLUME** | trocar de chave para coletar mais do que o teto do alvo | BR-21 | EXECUTÁVEL — o teto não muda ao trocar de chave |
| **UNKNOWN_FAILURE NÃO ROTACIONA** | uma falha não identificada queimar o pool inteiro | BR-21 | EXECUTÁVEL |
| **NÃO GASTAR É O PADRÃO** | gastar rota paga sem checkpoint aberto. `pode_gastar()` responde **NÃO por padrão**, com motivo. | BR-19 | EXECUTÁVEL — mutação `MUT4 K1 PEGOU` |
| **DUPLICATE_COUNT = 0 NÃO PROVA DEDUPE** | um dedupe que não faz nada passaria igual. Por isso o portão **exerce** o dedupe num caso conhecido em vez de confiar num zero. | MISSÃO 10B, §D | EXECUTÁVEL |
| **EMPATE SILENCIOSO ESCONDE** | a primeira taxonomia jogou **169 de 252** em `OTHER` porque um empate virava `OTHER`. Esconder não é ordenar. | MISSÃO 10B, §E | EXECUTÁVEL — precedência declarada, e `CONTENT_TYPE_ALL` mantém os demais visíveis |

### 3.6 · O QUE O DADO NÃO PROVA

Esta família é a que mais protege o cliente, porque cada linha é uma frase verdadeira a
um passo de uma frase falsa.

| Lei | A frase falsa que ela impede |
|---|---|
| **META AD ≠ SALES ≠ STOCK ≠ MARKET SHARE ≠ INVESTIMENTO ≠ CAMPAIGN SUCCESS** | «o concorrente está vendendo mais» a partir de um anúncio existir |
| **REGISTRATION ≠ COMMERCIAL AVAILABILITY** | «o produto está à venda» a partir de estar registrado |
| **TITULAR DE AUTORIZAÇÃO ≠ VENDEDOR** | «esta empresa vende» a partir de ela deter o registro |
| **FIELD PRESSURE ≠ DEMAND** | «há demanda» a partir de haver pressão de praga |
| **VOICE ≠ DEMAND** · **VOZ ≠ INCIDÊNCIA** | «está acontecendo no campo» a partir de estarem falando |
| **FOLLOWERS ≠ AUTHORITY** · **ENGAGEMENT ≠ INFLUENCE** | «esta pessoa é referência técnica» a partir de contagem |
| **PUBLIC SILENCE ≠ COMMERCIAL SILENCE** | «o concorrente parou» a partir de ele não postar |
| **CRUZAMENTO ≠ OPORTUNIDADE** | «há oportunidade» a partir de dois dados se tocarem |
| **VENCIMENTO FUTURO ≠ OPORTUNIDADE COMERCIAL** | «vai abrir espaço» a partir de uma data de expiração |
| **CROP_TERM_PRESENT ≠ ABOUT_THAT_CROP** | «este material é sobre milho» a partir da palavra «milho» aparecer |
| **TERMO DA CULTURA PRESENTE ≠ AUTORIZADO NA CULTURA** | «pode aplicar nesta cultura» a partir do rótulo citar a cultura |
| **JANELA ABERTA ≠ APLICAR AGORA** | «aplique» a partir de «é permitido neste estágio» |
| **COMENTÁRIO ≠ AGRICULTOR** | «o produtor diz» a partir de alguém ter comentado |
| **PORTFOLIO GLOBAL ≠ PORTFOLIO LOCAL** | «a ADAMA tem» a partir do catálogo de outro país |

`ENGAGEMENT ≠ INFLUENCE` está em **SÓ PROSA**: 2 documentos, nenhum teste, nenhum
medidor. É a lei desta família com a defesa mais fraca, e é a que um painel de «top vozes»
violaria primeiro.

### 3.7 · TRANSPORTE E TELA

| Lei | O erro que ela impede | Aprendida em | GUARDA |
|---|---|---|---|
| **VIDEO_EXISTS ≠ TRANSCRIPT_EXISTS ≠ TRANSCRIPT_USABLE ≠ TRANSCRIPT_USED_AS_EVIDENCE** | URL de vídeo passar por conteúdo analisado. Cinco estados, e a distância entre o primeiro e o último é hoje **184 → 0**. | CHECKPOINT §5 | EXECUTÁVEL — era SÓ PROSA quando esta seção foi escrita; a linha da coleta transformou a lei em contrato de campo em `site_v21_ingest.py`, e `fronteira-acervo-pacote.mjs` mede a escada degrau a degrau |
| **FICHA CHEGOU ≠ TEXTO CHEGOU** | os 88 registos de ciência chegam com link para o paper; o texto que permitiria cruzar o que o paper **prova** com o caso não chega | CHECKPOINT §3 | EXECUTÁVEL desde esta missão — `fronteira-acervo-pacote.mjs` |
| **CONSULTAR ≠ USAR** | 1.032 consultas de família por cartão viram «24 famílias cruzadas». `EVIDENCE_SCAN`: 1.529 encontradas · 359 usadas · 1.170 omitidas. | CHECKPOINT §3 | EXECUTÁVEL |
| **CONTADO ≠ RENDERIZADO** | 147 cartões de vídeo eram contados e chegavam vazios em duas fronteiras | commit `1c14c36` | EXECUTÁVEL |
| **ALIAS NÃO É SINÔNIMO** | `events` era alias de `futureEvents`: o registro do setor tinha 40 eventos e a tela mostrava 2 | commit `f3854a4` | EXECUTÁVEL |
| **UM NÚMERO NUMA MENSAGEM DE COMMIT NÃO É UM MEDIDOR** | a conta 711 → 213 existia só na mensagem de `5880b80` | commit `1d442a3` | EXECUTÁVEL — `reconciliacao-do-catalogo.mjs` |
| **PALAVRA QUE AFIRMA ATO EXIGE O ATO** | «Validato» impresso em 29 janelas que ninguém validou | commit `ad491c8` | EXECUTÁVEL |
| **PASTILHA QUE PROMETE TEM DE ENTREGAR** | pastilha verde prometia OPPORTUNITY e seis caíam em CASO NON TROVATO | commit `6f79552` | EXECUTÁVEL |

---

## 4 · OS CASOS ADVERSARIAIS

Um caso adversarial não é um teste: é um **ataque escrito**, com o resultado que ele
produziria se ninguém o recusasse. Todos os casos abaixo **aconteceram neste
repositório**. Nenhum é hipotético — e o último aconteceu enquanto este documento era
escrito.

O formato é fixo: **o ataque** · **o que ele produziria** · **quem o recusa hoje**.

---

### A-01 · A cota esgotada que se apresenta como sucesso
- **O ataque.** A plataforma devolve `SUCCEEDED`, `exitCode` limpo e **zero itens**.
  Escondida no `statusMessage`: `free user run limit reached`.
- **O que produziria.** «A rota não devolveu nada» — uma afirmação sobre o mundo — a
  partir de uma cota nossa que acabou.
- **Quem recusa hoje.** `scripts/coletor.py`: `SUCCEEDED` com zero itens vira `PARTIAL`
  carregando a mensagem da plataforma. **EXECUTÁVEL.**
- **A generalização.** *Nenhum resultado do ator ≠ nenhum resultado na plataforma.*

### A-02 · O zero publicado no lugar do não-medido
- **O ataque.** Não medir e publicar zero. Soa cauteloso.
- **O que produziria.** `RAW_ASSETS = 0` e o veredito «zero enviado dos 196» — quando a
  medição real da máquina espanhola dizia 184 verificados e 12 falhados.
- **Quem recusa hoje.** A correção está publicada com o erro à vista, na seção I do
  relatório. Nos artefatos novos, o campo `MEDIDO_DAQUI` é obrigatório e
  `tests/test_fundacao_coleta.py` reprova quem contar um pilar não medido como fechado.
  **EXECUTÁVEL.**
- **A generalização.** *Publicar zero é uma afirmação sobre o mundo, igual a qualquer
  outra. Não medir não é.*

### A-03 · O nome que faz dois trabalhos
- **O ataque.** Um portão chamado `EAME_COLLECTION_ENTRY_GATE` declarado `READY` no
  mesmo bloco em que `LOCATION_CONTRACT_COMPLETE = NO`.
- **O que produziria.** `READY` significando «o EAME inteiro pode coletar», que era
  falso — sem que ninguém tivesse mentido sobre nenhuma medição.
- **Quem recusa hoje.** `scripts/portoes_eame.py` **deriva** o estado das cicatrizes.
  Um portão não pode mais ser declarado READY por quem escreve o relatório.
  **EXECUTÁVEL.**
- **A generalização.** *O erro não foi de medição. Foi de nome. Um nome fazendo dois
  trabalhos produz contradição sem que nenhum número esteja errado.*

### A-04 · A edição de escopo que colhe verde
- **O ataque.** Tirar `LOCALIZACAO_CONFERENCIA` da lista de famílias do portão da
  coleta. O portão vira READY e nenhuma lacuna foi resolvida.
- **O que produziria.** Verde por edição, indistinguível de verde por trabalho.
- **Quem recusa hoje.** `tests/test_portoes_eame.py` reprova a edição, e uma mutação
  confirma que o teste tem dentes. Desde esta missão, `tests/test_fundacao_coleta.py`
  fecha a saída equivalente no pilar `TRAVESSIA` — mutação executada, **MUT PEGOU**.
  **EXECUTÁVEL.**
- **A generalização.** *Escolher o escopo depois de ver o resultado é a fraude mais
  barata que existe, e a única defesa é um teste que conheça a lista.*

### A-05 · A auditoria de árvore em movimento
- **O ataque.** Auditar um branch que continua recebendo commits.
- **O que produziria.** Um auditor afirmou que a regra não existia em `docs/regras/` e
  listou 4 arquivos onde havia 5 — tinha lido antes do commit que a criou. O achado
  parecia real.
- **Quem recusa hoje.** `scripts/auditoria.py` cria worktree `--detach` num SHA fixo. A
  auditoria é **INVÁLIDA** — não «com ressalva» — em quatro casos testados.
  **EXECUTÁVEL.**
- **A generalização.** *A medição pode falhar antes do objeto medido, e o resultado se
  parece com um achado.* Este padrão apareceu **quatro vezes** neste projeto.

### A-06 · A função testada que nenhum caminho invoca
- **O ataque.** Ter dedupe implementado, com teste unitário verde, e nenhum caminho
  reprodutível que o chame.
- **O que produziria.** `DUPLICATE_COUNT = 0`, verdadeiro e inútil. Um dedupe que não
  faz nada passa igual.
- **Quem recusa hoje.** `voz.pipeline_video()` faz RAW → normaliza → classifica →
  originalidade → dedupe → saída, e o portão **exerce** o dedupe num caso conhecido.
  Os 252 foram regerados lendo o bruto preservado. **EXECUTÁVEL.**
- **A generalização.** *Um teste unitário da função nunca teria pego isso. A cadeia
  precisa ser exercida, não afirmada.*

### A-07 · O segundo dono da mesma lei
- **O ataque.** A migration 016 criou um índice novo com as mesmas duas colunas de uma
  constraint que existia desde a 003.
- **O que produziria.** Duas travas para a mesma lei, que divergem quando uma for
  alterada — e a divergência aparece quando já custou.
- **Quem recusa hoje.** O banco recusou a duplicata na primeira execução. E a lição
  virou regra: **o dono da normalização é um só**, razão pela qual
  `reconciliacao-do-catalogo.mjs` prova por aritmética de conjuntos em vez de
  reimplementar a normalização. **EXECUTÁVEL.**

### A-08 · A palavra que afirma um ato
- **O ataque.** Imprimir «Validato» ao lado de 29 janelas.
- **O que produziria.** A afirmação de um ato de validação que ninguém praticou — e que
  ninguém pode mostrar.
- **Quem recusa hoje.** Trocado por «Dati al» / «Data as of», que afirma só a data.
  **EXECUTÁVEL.**
- **A generalização.** *Toda palavra de interface que nomeia um ato é uma afirmação de
  que o ato ocorreu.*

### A-09 · O denominador que melhora sozinho
- **O ataque.** Tirar do denominador os 12 arquivos que falharam no envio. A taxa vai
  de 184/196 para 184/184.
- **O que produziria.** 100%, apagando o problema em vez de resolvê-lo.
- **Quem recusa hoje.** Os 12 **pertencem ao denominador**: cada um tem `ARQUIVO_LOCAL`,
  `BYTES` e `SHA256`. Existem, foram baixados, foram conferidos — o que falhou foi o
  envio, não a obtenção. **EXECUTÁVEL.**
- **O irmão deste ataque.** Guardar só a melhor de duas tentativas. A segunda medição
  deu **um a menos** que a primeira (185/11 → 184/12), e a diferença de 1 ficou
  registrada porque é parte do diagnóstico.

### A-10 · O portão que usa como porta um campo que não é porta
- **O ataque.** Um check de auditoria (`O1`) usando como critério de visibilidade um
  campo que o contrato declara **não ser** porta de visibilidade.
- **O que produziria.** Dois resultados `NÃO MENSURÁVEL` que pareciam limitação do
  mundo e eram escolha de campo errado.
- **Quem recusa hoje.** Corrigido em `audit/checks.mjs`: 71/71. **EXECUTÁVEL.**

### A-11 · A tela que promete o que a partição não entrega
- **O ataque.** Uma pastilha verde anunciando OPPORTUNITY em janelas cujo caso cai em
  `CASO NON TROVATO`.
- **O que produziria.** Seis promessas falsas na véspera da reunião.
- **Quem recusa hoje.** Corrigido: 6 → 0. **EXECUTÁVEL.**
- **O que continua aberto.** As duas linhagens **discordam sobre o que é uma
  oportunidade** (`MEETING_SURFACE_RULE` × `relevanceSurface`), e `surface-contract.mjs`
  está 3/8 — medido **idêntico** no DEMO_HEAD intocado, portanto conflito de contrato,
  não regressão. É `INTEGRATION_DEPENDENCY`, e não se resolve de um lado só.

### A-12 · O alias que come 38 eventos
- **O ataque.** `events` definido como alias de `futureEvents`.
- **O que produziria.** O registro do setor tem 40 eventos; a tela mostrava 2.
- **Quem recusa hoje.** Corrigido: 2 → 18 cartões, e os 22 recusados são **contados**,
  com a razão (sem nome). **EXECUTÁVEL.**
- **A generalização.** *Recusa contada é informação. Recusa silenciosa é perda.*

### A-13 · O ataque que esta missão deixou explicitamente em aberto
- **O ataque.** Ligar título e link nos 147 cartões de vídeo orgânico antes da reunião.
- **O que produziria.** `CASE_ID` diz **111 IT · 26 ES · 10 FR**, e `COUNTRY_REACHED` é
  nulo em 147/147. Ligar poria 36 cartões em espanhol e francês numa tela italiana.
- **Quem recusa hoje.** Ninguém, tecnicamente — a decisão foi **não atravessar a
  terceira fronteira** e escrever por quê. `fronteira-acervo-pacote.mjs` mede
  `SEM_COUNTRY_REACHED` para que a dívida não dependa de alguém se lembrar.
- **A generalização.** *Não atravessar uma fronteira é uma decisão legítima quando está
  escrita, datada e medida. Sem isso é esquecimento.*

### A-14 · O medidor que contou o rótulo do estado como se fosse o texto
- **O ataque.** Contar como «fala transcrita» os caracteres de qualquer campo cujo
  nome case `/transcript/`.
- **O que produziu.** Este erro **não é histórico: foi cometido nesta missão.** Quando
  a família `transcripts` chegou ao artefato, o medidor devolveu **809 caracteres de
  fala** que não eram fala nenhuma — eram os rótulos `true`, `false` e `INCLUDED` dos
  campos `TRANSCRIPT_EXISTS`, `TRANSCRIPT_USABLE` e irmãos.
- **A ironia, que é o ponto.** O medidor construído para instrumentar a lei
  `TRANSCRIPT_EXISTS ≠ TRANSCRIPT_USED_AS_EVIDENCE` violou **exatamente essa lei**, na
  primeira vez em que o mundo lhe deu ocasião. Uma lei em SÓ PROSA não protege nem quem
  a cita.
- **Quem recusa hoje.** Duas listas separadas de campos — os que **carregam** texto e os
  que **declaram estado** sobre esse texto — e um campo de estado nunca entra na conta de
  caracteres. `tests/test_fundacao_coleta.py::test_rotulo_de_estado_nunca_conta_como_texto`.
  **EXECUTÁVEL.**
- **Por que fica escrito.** Porque a alternativa era corrigir em silêncio e publicar um
  medidor que sempre soube distinguir. Rebaixar nunca é retrocesso; apagar é.

---

## 5 · AS DECISÕES QUE ESTA BÍBLIA REGISTA

Registradas em `docs/decisoes/DIARIO-DE-DECISOES.md` como **D-027** e **D-028**. Aqui
ficam o contexto e o raciocínio; lá fica a forma canônica.

### D-027 — A fundação da coleta é conjunção, não herança

`EAME_COLLECTION_ENTRY_GATE = READY` responde «podemos abrir coleta?». Não responde «o
que coletamos chega?». Deixar a fundação herdar o READY da entrada autorizaria coletar
mais para dentro de um funil que não entrega — o modo de falha mais caro possível aqui,
porque cada rodada paga produz acervo e o acervo não vira inteligência.

> **A COLETA ESTÁ FUNDADA QUANDO SE PODE COLETAR *E* O QUE SE COLETA CHEGA.**

### D-028 — Um lado medido e outro alegado não produzem uma perda quantificada

O CHECKPOINT publica `5.033.374 → 0`. O primeiro número vem do acervo, que **não está
neste repositório**; o segundo é medível daqui. Subtrair um do outro produz um número com
cara de fato.

Por isso a fronteira tem três estados e não dois: `FECHADA`,
`ABERTA_MEDIDA_DE_UM_LADO`, `NÃO_MEDIDA`. Hoje as quatro famílias estão no segundo — nem
fechadas, nem inventadas. Quando o acervo for medível pelo mesmo medidor, a perda vira
número; até lá, é **fronteira aberta com dono**, e o dono está nomeado:
`claude/opportunity-commercial-priority-v1`.

---

## 6 · O PONTO DE ENCONTRO

As duas linhas se encontram em `COLLECTION_FOUNDATION_CLOSED`. O estado **não se declara
aqui** — este documento não fecha portão nenhum. Deriva-se:

```bash
node italia-portale/audit/fronteira-acervo-pacote.mjs      # o lado que chega
python3 scripts/fundacao_coleta.py                         # a conjunção
python3 -m unittest tests.test_fundacao_coleta             # a saída fácil, fechada
```

### Estado medido em 2026-09-08, safra `V21-06c6421d001ea52a`

| PILAR | ESTADO | Medidor | O que falta |
|---|---|---|---|
| ENTRADA | **FECHADO** | `scripts/portoes_eame.py` | — (35/35 cicatrizes PROVED) |
| PRESERVAÇÃO | **FECHADO** | `scripts/portoes_eame.py` | — (196/196, sha256 reconferido; prova EXTERNA) |
| TRAVESSIA | **ABERTO** | `italia-portale/audit/fronteira-acervo-pacote.mjs` | 3 famílias de 4 |

```
COLLECTION_FOUNDATION_CLOSED = NÃO
```

### O que a fronteira mede hoje

| Família | ESTADO | CHEGOU (medido daqui) | Ação mínima · Dono |
|---|---|---|---|
| TRANSCRIÇÕES | **FECHADA_COM_FRONTEIRA_DECLARADA** | 184 registos, escada completa, SHA em 160, 5.167.243 caracteres **declarados** pela origem · **0 caracteres de fala** | o texto não embarca **de propósito**, com a razão escrita em `site_v21_ingest.py` |
| CIÊNCIA_TEXTO | ABERTA_MEDIDA_DE_UM_LADO | 0 caracteres · 88 registos, 86 com DOI, 88 com URL, nenhum campo de texto | campo de texto científico em `SCIENCE.json` · `opportunity-commercial-priority-v1` |
| ANÚNCIOS_DATA | ABERTA_MEDIDA_DE_UM_LADO | 0 anúncios com data de observação · 577 registos, 27 declaram ACTIVE | transportar `last_observed` · `opportunity-commercial-priority-v1` |
| VÍDEO_ORGÂNICO | ABERTA_MEDIDA_DE_UM_LADO | 147 cartões, 139 com título+link+data, **147 sem `COUNTRY_REACHED`** | `COUNTRY_REACHED` por cartão · `opportunity-commercial-priority-v1` |

**A família das transcrições fechou entre a primeira e a segunda corrida deste medidor, e
o medidor não foi editado para acompanhar: ele mediu.** A linha da coleta fez a escada
inteira atravessar. O texto continua a não atravessar — e isso agora é **fronteira
declarada**, não perda silenciosa.

> **UMA FRONTEIRA DELIBERADA DEIXA VESTÍGIO MEDÍVEL. UM ESQUECIMENTO DEIXA SÓ SILÊNCIO.**

O estado `FECHADA_COM_FRONTEIRA_DECLARADA` não se conquista escrevendo a frase: exige,
mecanicamente, registos presentes + os cinco degraus da escada + SHA do texto + a
contagem da origem. Mutação executada — colar a frase numa família sem vestígio **não** a
fecha.

### O degrau que continua aberto, e que não bloqueia a fronteira

`TRANSCRIPT_USED_AS_EVIDENCE` é falso em **184/184**. A fala existe, é utilizável, está no
pacote — e nenhum cartão apoia afirmação nela.

> **A FRONTEIRA PERGUNTA SE O QUE SE COLETOU CHEGA. O DEGRAU PERGUNTA SE O QUE CHEGOU É
> USADO. COLAPSÁ-LAS FARIA A COLETA REFÉM DO MOTOR.**

Por isso o degrau tem dono próprio — o motor do portal — e é reportado separadamente das
famílias abertas.

**Nenhuma das três famílias abertas se resolve deste lado.** O campo que falta falta no
**pacote**, e o pacote não se escreve nesta linhagem.

### O que muda quando fechar

Quando as quatro famílias atravessarem, `fundacao_coleta.py` devolve `SIM` **sozinho**,
sem edição de documento. Nesse dia, e só nesse dia, a linha paralela e a principal deixam
de ser duas: a bíblia passa a descrever um sistema onde o que se coleta chega, e a
engenharia da coleta passa a poder abrir cadência recorrente.

---

## 7 · O QUE ESTA BÍBLIA NÃO SABE

Registrado como `NÃO SEI`, que é resposta válida e obrigatória.

1. **Quantas leis realmente existem.** Foram encontradas 240 **formas escritas**. Quantas
   leis distintas elas são, não se sabe: a deduplicação semântica não foi feita, e fazê-la
   por semelhança de string produziria um número errado com cara de contagem.
2. **Quantas estão em SÓ PROSA.** A varredura da seção 3 cobre as leis **citadas neste
   documento**, não as 259. Duas continuam em SÓ PROSA (`FIRST SNAPSHOT ≠ NO CHANGE` e
   `ENGAGEMENT ≠ INFLUENCE`); a terceira, `VIDEO_EXISTS ≠ TRANSCRIPT_EXISTS`, deixou de
   estar **enquanto este documento era escrito**. Quantas mais existem é `NÃO MEDIDO`.
3. **Se a guarda EXECUTÁVEL de cada lei realmente tem dentes.** A varredura prova que
   existe teste ou medidor **nomeando** a lei. Não prova que o teste reprovaria a
   violação. Só a mutação prova isso, e a mutação foi executada para `TRAVESSIA` e para
   as cicatrizes — não para as 240.
4. **O tamanho real da perda na fronteira.** Ver D-028. Enquanto o acervo não for medível
   pelo mesmo medidor, `5.033.374 → 0` é uma alegação com origem escrita, não uma medição.
   E há agora um **terceiro** número: os `5.167.243` caracteres que o pacote declara por
   registo. Ele viaja dentro do artefato versionado — logo é reproduzível daqui — mas
   continua a ser declaração da origem sobre um texto que o artefato não carrega.
   **Transportar a contagem não é transportar o texto**, e os dois números não batem
   entre si: são denominadores diferentes, e reconciliá-los é trabalho de quem tem o
   acervo.
5. **Qual das duas leis sobre oportunidade vence.** O conflito da seção A-11 é
   `INTEGRATION_DEPENDENCY`. Esta bíblia registra que as duas existem, ambas testadas, e
   que discordam. Não escolhe — não é dela a escolha.

---

```
BIBLIA_ESCRITA_CONTRA           medidores executáveis, não memória
IMPLEMENTACAO_NESTA_LINHA       nenhuma
PORTAO_QUE_ESTA_BIBLIA_FECHA    nenhum
COLLECTION_FOUNDATION_CLOSED    derivado em scripts/fundacao_coleta.py
```
