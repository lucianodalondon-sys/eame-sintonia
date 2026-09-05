# DIÁRIO DE DECISÕES — SINTONIA EAME

Registro cronológico de **toda** decisão que afeta o repositório: estrutura, método,
escopo, fonte, ferramenta, corte.

Regras do diário:

- Uma decisão por entrada, com **data**, **motivo** e **estado**.
- Decisão revertida **não se apaga**: abre-se nova entrada que a revoga, citando a original.
- Decisão tomada por falta de informação é marcada como **SUPOSIÇÃO ASSUMIDA** e vira
  pergunta pendente até ser confirmada por quem tem autoridade.
- Nenhuma decisão de produto é registrada aqui sem ter sido dada por quem decide.

**Formato:**

```
### D-000 — Título
- Data:
- Estado: DECIDIDO | SUPOSIÇÃO ASSUMIDA | REVOGADA (por D-000) | PENDENTE
- Contexto:
- Decisão:
- Motivo:
- Consequência:
- Quem decidiu:
```

---

### D-001 — Repositório próprio, sem herdar artefatos do Sintonia Brasil
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Existe um Sintonia Brasil em operação, com código, réguas, banco e classificadores.
- **Decisão:** O SINTONIA EAME nasce em repositório próprio e vazio. O Brasil entra apenas
  como referência metodológica. Não se copia código, régua instável, banco ou classificador,
  e não se altera o repositório brasileiro.
- **Motivo:** Realidade regulatória, fontes, idiomas e mercado da EAME são outros; herdar
  artefato pronto importaria pressupostos brasileiros não verificados na Europa.
- **Consequência:** Todo aproveitamento vindo do Brasil precisa de entrada própria neste diário.
- **Quem decidiu:** Enunciado da tarefa.

### D-002 — Estrutura inicial de pastas conforme sugerida
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Primeira tarefa é preparar a casa antes de pesquisar ou implementar.
- **Decisão:** Adotada a estrutura sugerida: `docs/` (01 a 08), `data/` (samples, raw,
  normalized), `research/` (europe, france, spain, italy, people, competitors),
  `prototype/portal`, `tests/`, `scripts/`.
- **Motivo:** A estrutura já reflete a cadeia SOURCE → … → PORTAL e o recorte por país.
- **Consequência:** Diretórios ainda sem conteúdo carregam `.gitkeep` para existirem no versionamento.
- **Quem decidiu:** Enunciado da tarefa.

### D-003 — `data/raw` e `data/normalized` fora do versionamento
- **Data:** 2026-08-28
- **Estado:** SUPOSIÇÃO ASSUMIDA
- **Contexto:** Não houve instrução sobre o que versionar dentro de `data/`.
- **Decisão:** `data/raw/` e `data/normalized/` ficam ignorados pelo Git (exceto os
  `.gitkeep`). `data/samples/` é versionado.
- **Motivo:** Bruto e normalizado tendem a ser grandes, refazíveis e sujeitos a licença de
  redistribuição; amostras pequenas com procedência são justamente o que precisa viajar
  junto com a evidência.
- **Consequência:** Evidência preservável de uma fonte deve ir para `data/samples/`, não
  para `data/raw/`. Se alguma fonte exigir versionar bruto, revogar esta entrada.
- **Quem decidiu:** Assumido na ausência de instrução — **confirmado** pela MISSÃO 02 §0 (P-001 encerrada).

### D-005 — Estrutura de `docs/` realinhada ao briefing da MISSÃO EAME 01
- **Data:** 2026-08-28
- **Estado:** DECIDIDO (revoga parcialmente D-002)
- **Contexto:** D-002 adotou `docs/01-descoberta` … `docs/08-decisoes`, com prefixos
  numéricos e uma pasta `06-arquitetura`. O briefing da MISSÃO EAME 01, recebido depois,
  especifica `docs/descoberta`, `fontes`, `capacidades`, `cruzamentos`, `ferramentas`,
  `decisoes`, `apresentacao` — sem prefixos e sem pasta de arquitetura — e diz
  "não criar estrutura adicional sem necessidade comprovada".
- **Decisão:** Pastas renomeadas para a forma do briefing; `06-arquitetura` removida.
- **Motivo:** O briefing da missão é a especificação vigente e é mais restritivo.
  Arquitetura não tem necessidade comprovada nesta fase.
- **Consequência:** Os caminhos de D-002 não valem mais. Se o desenho técnico precisar de
  lugar próprio mais adiante, abre-se nova entrada justificando a necessidade.
- **Quem decidiu:** Briefing MISSÃO EAME 01, §0 e §17.

### D-006 — Documentos canônicos como memória externa
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Instrução de modo de execução com economia de contexto.
- **Decisão:** Todo achado é gravado imediatamente no documento canônico correspondente,
  com a evidência preservada e commit próprio. Nada de inventário grande vivendo só no
  contexto da conversa. Checkpoints referenciam arquivo em vez de reproduzir conteúdo.
- **Motivo:** Evidência sobrevive à conversa; contexto não.
- **Consequência:** Prioridade operacional: EVIDÊNCIA > CONTEXTO, ARQUIVO > MEMÓRIA,
  MEDIÇÃO > EXPLICAÇÃO.
- **Quem decidiu:** Instrução do usuário (modo de execução).

### D-004 — Documentos-base criados como esqueleto, sem conteúdo inventado
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Os documentos de fontes, capacidades, cruzamentos, ferramentas e casos de
  apresentação foram pedidos antes de qualquer pesquisa.
- **Decisão:** Cada um nasce com propósito, regra de preenchimento e formato de ficha —
  e com o registro de fontes/capacidades **vazio**.
- **Motivo:** Preencher exemplos plausíveis antes de pesquisar violaria o princípio
  SOURCE → EVIDENCE e contaminaria o atlas com conteúdo que ninguém verificou.
- **Consequência:** Os atlas mostram zero registros. Isso é o estado correto da Fase 0.
- **Quem decidiu:** Enunciado da tarefa (princípio e regra).

### D-007 — Claude descobre o produto; Claude Design desenha o produto
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** o protótipo da MISSÃO 02 provou que os dados sustentam blocos reais, mas
  continuar a desenvolvê-lo misturaria descoberta com design.
- **Decisão:** `prototype/portal` fica **congelado como artefato histórico** — não é
  desenvolvido, não é atualizado e **não é base de decisão**. A MISSÃO 03 passa a ser
  100% texto, dados, evidência e arquitetura conceitual de informação. Todo o trabalho
  visual vai para missão separada, com Claude Design.
- **Motivo:** o Design não deve precisar descobrir o produto; deve transformar uma
  arquitetura de informação já fechada em experiência visual.
- **Consequência:** o fluxo desta missão termina em INFORMATION REQUIREMENTS e **não**
  continua para UI, componente, página ou portal. O estado `PROTOTYPE` deixa de ser usado
  em ficha de ferramenta.
- **Quem decidiu:** cliente, redirecionamento de 2026-08-28.

---

### D-008 — A versão de que um change event depende é evidência, não dado bruto

- **Data:** 2026-08-29
- **Estado:** DECIDIDO (estende D-003, não o revoga)
- **Contexto:** D-003 mantém `data/raw` fora do versionamento. Mas a detecção de mudança
  só existe porque **duas versões do mesmo documento** estavam guardadas — e o contêiner
  onde elas estavam é efêmero. Se a versão de 28/05/2025 se perder, o evento
  `MAXENTIS → SORATEL MAX` deixa de ser verificável por qualquer pessoa, inclusive por nós.
- **Decisão:** dado bruto continua fora do versionamento, **exceto** a versão específica de
  que um `CHANGE EVENT` publicado depende. Essa versão vai para `data/samples/`, com o nome
  carregando a data da versão e um `LEIA-ME.md` declarando SHA-256 e como reproduzir.
- **Motivo:** evidência que não sobrevive ao contêiner não é evidência.
- **Consequência:** `data/samples/ES-T4-004-versoes/` (2 PDFs, 581 KB) e
  `data/samples/ES-T4-005/ropf_20260829.json.gz` (projeção, 147 KB) passam a ser
  versionados. A projeção guarda só os campos que entram em change event — não o export
  inteiro de 14 MB.
- **Quem decidiu:** decisão técnica da MISSÃO 07, registrada para revisão.

---

### D-009 — Número declarado tem de ser número derivado

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** o fim da MISSÃO 06 deixou `37/37` num relatório e `38/38` na mensagem do
  commit `e37911a`. A suíte tinha 37. Nenhum dos dois números era derivado da suíte — os
  dois eram digitados.
- **Decisão:** todo total publicado num documento canônico tem de ter uma prova que o
  derive da coisa contada. Vale para: total de testes, placar do benchmark, contagens de
  fontes, números de denominações.
- **Motivo:** um número digitado diverge em silêncio; um número derivado quebra o teste.
- **Consequência:** `tests/test_canonico.py` ganhou
  `test_o_total_de_testes_declarado_vem_da_suite` (conta a suíte com
  `unittest.defaultTestLoader.discover`), o placar do benchmark passou a ser lido do JSON,
  e as contagens de denominação passaram a ser comparadas com o arquivo de medida.
- **Quem decidiu:** decisão técnica da MISSÃO 07.

---

### D-010 — Cobertura menor e declarada vence cobertura maior e silenciosa

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** para separar as colunas coladas da lista de *denominaciones comunes* foram
  testadas duas regras. A heurística "cortar na primeira forma jurídica" resolveu **96,9%**
  das linhas — e produziu `INDUSTRIAS A` + `FRASA, S.A.` e `ECOLOGIA Y PROTECCION AG` +
  `RICOLA`. A regra ancorada em fontes externas (nome oficial do produto e vocabulário de
  titulares, ambos do export do ROPF) resolve **68,8%** e erra zero nas linhas que resolve.
- **Decisão:** fica a regra de 68,8%. O restante fica `UNRESOLVED`, com o motivo por linha.
- **Motivo:** erro silencioso é pior do que lacuna declarada. Uma tabela plausível e falsa
  passa pela revisão; uma lacuna não passa.
- **Consequência:** a cobertura é publicada junto com o número, sempre.
- **Quem decidiu:** decisão técnica da MISSÃO 07.

---

### D-011 — Toda cadeia declara os seus passos por natureza

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** até a MISSÃO 07 a coleta estava em script e a **análise** estava na cabeça
  de quem a fez. Um engenheiro novo conseguia baixar o E-Phy e não conseguia chegar a
  "77 produtos, ADAMA 3". O RAIF era pior: a troca de host que faz o download funcionar
  estava em prosa no atlas.
- **Decisão:** toda cadeia que produz um fato do piloto vive em `scripts/chain.py` e
  declara cada passo como `AUTOMATIC`, `MANUAL` ou `HUMAN_JUDGMENT`.
- **Motivo:** o objetivo não é zerar julgamento humano — é saber **onde ele está**.
  Um dicionário de grupo empresarial não é dado; é decisão nossa, e move números.
- **Consequência:** as quatro cadeias somam 17 passos automáticos, **0 manuais** e 5 de
  julgamento. Toda contagem por grupo sai acompanhada da contagem por **entidade legal**,
  que não depende de dicionário nenhum.
- **Quem decidiu:** decisão técnica da MISSÃO 08.

---

### D-012 — Falhar fechado, sempre; e rebaixamento nunca é silencioso

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** um pipeline que degrada tem duas saídas possíveis: parar, ou entregar um
  número menor com a mesma cara de sempre. A segunda é a que destrói confiança.
- **Decisão:** `HTTP 200` não basta para `HEALTHY` — exige schema completo, identidade
  única e conteúdo. Lista vazia é `FAILED`, nunca "zero resultados". Cobertura abaixo do
  piso **levanta**. E quando algo é rebaixado para funcionar — como aceitar `SECLEVEL=1`
  no TLS do host italiano — o rebaixamento é **registrado como passo da cadeia**.
- **Motivo:** "não consegui ver" e "não há nada" produzem o mesmo número e significam o
  oposto.
- **Consequência:** 11 formas de degradação testadas; nenhuma produz número errado.
  Verificação de certificado **nunca** é desligada — há teste que proíbe `CERT_NONE` e
  `check_hostname = False` no código das cadeias.
- **Quem decidiu:** decisão técnica da MISSÃO 08.

---

### D-013 — Inventário de população que muda é derivado, e número corrente tem dono

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** a MISSÃO 10C encontrou a mesma classe de defeito em quatro lugares.
  `POLITICA-RAW-ROTA-PAGA.json` era uma **lista digitada** do diretório `raw-paid/`: um
  bruto novo entrou no commit de handoff, o DATA CLOCK (derivado) o pegou, a política
  (digitada) não, e ficou publicando 10 arquivos e 2.121.837 bytes onde havia 11 e
  2.182.917 — internamente consistente e falsa. **Nenhum teste lia a política.** No mesmo
  movimento: o handoff publicava `26 fichas` com o dono derivando 25, porque `--sync` só
  andava por `docs/` e o handoff mora na **raiz**; a porta canônica, que vence qualquer
  conflito, carregava 486/1.004/36/61/34 **sem marcador**; e o rótulo do benchmark do Ask
  dizia "20 perguntas" com 35 no arquivo.
- **Decisão:** (a) inventário de população que muda é **derivado da população real**, nunca
  digitado — `scripts/proveniencia.py` passa a ser o dono do diretório `raw-paid/`;
  (b) quando duas coisas inventariam a mesma população, cada uma **declara seu escopo** e
  existe **reconciliação executável** entre elas e o disco; (c) todo número **corrente**
  publicado em `.md` tem marcador ligado ao ledger — e o `--sync` passa a alcançar a raiz;
  (d) documento feito para ser **copiado e colado** não leva marcador: o dono dele é o teste.
- **Motivo:** um inventário digitado de uma população que muda envelhece em silêncio, e
  soma consistente consigo mesma dá aparência de correção. `COBERTURA ALTA ≠ COBERTURA
  CORRETA` vale também para inventário: **lista coerente ≠ lista completa**.
- **Consequência:** `POLITICA-RAW-ROTA-PAGA.json` publica `ARQUIVOS`, `TAMANHO_ATUAL_BYTES`,
  `TOTAL_POR_CLASSE` e `BRUTOS_ORFAOS` derivados; a suíte foi de 280 para 295 provas — e a
  primeira coisa que as novas provas pegaram foi a própria deriva que elas introduziram.
- **Quem decidiu:** decisão técnica da MISSÃO 10C.

---

### D-014 — A cadeia de proveniência vale nas duas direções

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** `CONTENT → RUN_ID → MANIFEST` estava provada. A direção inversa,
  `ARQUIVO BRUTO → EXECUÇÃO`, não: `GATE-TEST-RUNMANIFEST-2026-08-29-b.raw.json.gz`
  existia em disco, aparecia na política e **não tinha execução nenhuma no manifesto**.
  Era artefato de teste — mas nada no repositório dizia isso, e um bruto **operacional**
  órfão teria passado igual.
- **Decisão:** o bruto de rota paga carrega **classe declarada**: `PRODUCTION_RAW` ou
  `GATE_TEST_RAW`. Todo `PRODUCTION_RAW` **tem de** ser reivindicado por uma execução do
  manifesto — `BRUTOS_ORFAOS` é sempre vazio. `GATE_TEST_RAW` pode não ter execução, mas
  **nunca em silêncio**: carrega `EXCLUDED_WITH_REASON`.
- **Motivo:** sem classe, "artefato de teste corretamente sem run" e "evidência sem
  procedência" são o mesmo arquivo aos olhos do portão. `NÃO COLETADO ≠ NÃO EXISTE`
  precisa do seu par: **`SEM EXECUÇÃO ≠ SEM EXPLICAÇÃO`**.
- **Consequência:** `pv.brutos_orfaos()`, `pv.runs_por_bruto()` e a reconciliação da
  política; e um teste que **exerce a falha** num diretório temporário, porque uma
  reconciliação que nunca reprova prova tão pouco quanto um `DUPLICATE_COUNT = 0`.
- **Quem decidiu:** decisão técnica da MISSÃO 10C.

---

### D-015 — A amostra de concorrentes sai do registro, não da lista de nomes
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** o COMPETITOR FORESIGHT PILOT nomeou oito concorrentes e pediu 4–6
  bem feitos. Aceitar os seis primeiros da lista teria escolhido a amostra por
  reputação.
- **Decisão:** contar os titulares do ROPF espanhol (3.084 registros, 262 titulares)
  e escolher os seis maiores por registros com `Estado = Vigente`. O agrupamento de
  razões sociais é **declarado por prefixo**, string por string, e cada razão social
  somada fica visível no artefato.
- **Motivo:** um número que ninguém consegue reabrir não é evidência. E agrupar por
  parecença junta o que a lei separa — o inverso do falso positivo de `HOLDER_CHANGE`
  que a `REGUA-DE-CHANGE-EVENT-EAME §6` já mediu.
- **Consequência:** amostra = NUFARM, SYNGENTA, BAYER, CORTEVA, BASF, UPL. FMC e
  CERTIS BELCHIM ficaram de fora por medida, não por opinião. Conferência que dá
  confiança na contagem: a ADAMA deu 96 vigentes, exatamente os 96 da fundação
  `ES-REGULATORIO-ROPF-2026-08-29`, importada por outro caminho.
- **Quem decidiu:** Luciano, na abertura da missão.

### D-016 — TMview é a rota de marca; os quatro portais nacionais recusam robô
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** OEPM (403), INPI (403) e UIBM (não conecta) recusam acesso
  programático. O TMview, agregador oficial da EUIPO, responde 200 e cobre os
  quatro escritórios numa rota só.
- **Decisão:** coletar marca **exclusivamente** pelo TMview, preservando o
  `tmOfficeURL` de cada resultado — o link de volta para a ficha no portal de origem.
- **Motivo:** a evidência continua rastreável até a fonte primária mesmo quando ela
  recusa o robô.
- **Consequência:** ausência no TMview é `NOT_OBSERVED_IN_TMVIEW`, nunca "a marca
  não existe". **O atraso de sincronização entre escritório nacional e TMview não
  foi medido nesta rodada** — fica como limitação declarada.
- **Quem decidiu:** decisão técnica do COMPETITOR FORESIGHT PILOT.

### D-017 — Parâmetro ignorado em silêncio vira portão obrigatório
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a API do TMview **ignora sem erro** parâmetro cujo nome ela não
  conhece. Pedir `applicantName` devolveu **HTTP 200 e 1.068.402 resultados** — a
  Espanha inteira — com cara de busca bem-sucedida. O piloto quase publicou
  "1.068.402 marcas da Syngenta".
- **Decisão:** toda busca roda uma consulta de CONTROLE **sem filtro** e é RECUSADA
  quando o total filtrado é igual ao total sem filtro (`FiltroIgnorado`).
- **Motivo:** HTTP 200 não é prova de que o pedido foi entendido. `SEM FILTRO ≠ SEM
  RESULTADO` é o par que faltava a `NÃO COLETADO ≠ NÃO EXISTE`.
- **Consequência:** uma requisição a mais por escritório; `CONTROLE_SEM_FILTRO`
  gravado no artefato e verificado em `tests/test_concorrente.py`.
- **Quem decidiu:** decisão técnica do COMPETITOR FORESIGHT PILOT.

### D-018 — Classe 5 de Nice não é sinal agro, e a régua tem três estados
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a primeira régua tratou classe 5 como sinal agroquímico. A classe 5
  cobre `farmacêuticos, veterinários, higiênicos **e** pesticidas` na mesma classe, e
  carimbou `GINECANES` e `BEPANTHENSENSICALMSOS`, da Bayer, como defensivo. São remédio.
- **Decisão:** três estados em vez de dois — `CLASSE_1_E_5`, `SO_CLASSE_1` (as duas
  são sinal forte), `SO_CLASSE_5` (**AMBÍGUO**, nunca sinal agro sozinho).
- **Motivo:** medido nas 9.661 marcas: **4.496 são `SO_CLASSE_5`**, e **2.551 delas
  são da Bayer**, que tem divisão farmacêutica. Somar as duas forças diria que a
  Bayer é quem mais se movimenta em marca agroquímica na EAME — o que é efeito da
  classe compartilhada, não do dado.
- **Consequência:** reclassificação sobre o dado já coletado (derivação, não segunda
  captura): 8.028 marcas mudaram de estado. E um achado que **enfraquece a própria
  régua**: o `VERDALIS` da Corteva foi depositado na classe 1 na Itália e na França e
  na classe 5 na Espanha — mesma marca, mesmo titular, classe diferente por país. A
  classe **marca**, e nunca **descarta**.
- **Quem decidiu:** decisão técnica do COMPETITOR FORESIGHT PILOT.

### D-019 — Patente: DEMOTED, porque a porta abre e a chave não existe
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** `curl` e a API OPS da EPO devolvem 403. O Espacenet abre por
  navegador com janela gráfica e a busca por titular devolve 6.333 resultados só
  para a Syngenta — o volume existe.
- **Decisão:** rebaixar a camada de patente. Ela não entra na timeline nem no
  Supabase desta rodada.
- **Motivo:** teste com o nome exato de 5 marcas do piloto em texto completo:
  **0 de 5** recuperaram patente do titular correto. `LIBERATOR` devolve coldre de
  bolso; `DUAL GOLD`, um implante hospitalar chinês; `VERDALIS`, zero. Patente nomeia
  MOLÉCULA; marca e registro nomeiam PRODUTO COMERCIAL, e nenhum campo os une.
- **Consequência:** `data/samples/COMPETITOR-PATENT-DEMOTE.json`. A porta fica
  documentada e reabre sem trabalho perdido quando houver chave de OPS. Cinco casos
  não são amostra estatística — são cinco casos, todos negativos, apresentados assim.
- **Quem decidiu:** Luciano escolheu tentar pelo navegador; a medida decidiu o resto.

### D-020 — Antecedência só sobre identidade provada, e a trava desce para o banco
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a missão manda medir `LEAD_DAYS` "somente quando a relação for
  defensável". Medido nos 209 pares provados, a amplitude bruta vai de **-15.700 a
  +11.033 dias** — 43 anos para trás e 30 para frente. Redepósito de marca, reuso de
  nome comercial e colisão de nome genérico produzem esses extremos.
- **Decisão:** `lead_days` só existe sobre link `PROVED` (constraint
  `lead_days_exige_identidade_provada`), e `lead_days_defensavel` exige ordem
  marca→registro **e** que o depósito seja o mais antigo daquela marca no grupo
  (constraint `defensavel_exige_ordem_e_valor`). **Sem corte de tempo arbitrário.**
- **Motivo:** a regra não pode ficar só no script — um dia alguém carrega a tabela
  por outro caminho. E um limiar de dias escolhido a dedo produziria a antecedência
  que se quisesse.
- **Consequência:** 155 pares defensáveis de 209, mediana 2.179 dias. Os **51 pares
  em que o registro precede a marca REFUTAM a hipótese do piloto e continuam na
  base** — apagá-los produziria 100% de confirmação.
- **Quem decidiu:** decisão técnica do COMPETITOR FORESIGHT PILOT.

### D-021 — A camada de concorrente é derivada e não vira dona de nada
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** seria confortável escrever `competidor text`, `registro text`,
  `anuncio text` e ter tudo num lugar só. Isso criaria uma **segunda verdade** sobre
  empresa, registro e anúncio, ao lado das que já existem — o defeito que a 016
  cometeu com um índice e a 018 corrigiu aposentando uma coluna.
- **Decisão:** `evento_concorrente` só APONTA: `organizacao`, `registro_regulatorio`,
  `catalogo_produto`, `canal`, `crop`, `issue`, `raw_asset`. Marca é **texto num
  evento**, não tabela. `META` e `CREATOR` só podem existir apontando para
  `canal_id`, por constraint.
- **Motivo:** §6 da missão — META continua dona dos anúncios, CREATOR MAP dos
  creators, FOUNDATIONS do registro local.
- **Consequência:** o registro espanhol é apontado por **texto**
  (`registration_id_texto`), porque a fundação importou só os 96 da ADAMA e os
  registros dos concorrentes não estão no banco. O texto **espera** o dono em vez de
  criar um segundo. E o portão verifica que os 96 sobrevivem ao import.
- **Quem decidiu:** decisão técnica do COMPETITOR FORESIGHT PILOT.

### D-022 — Link que não pode existir é declarado, não engolido pelo SQL
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** um `insert ... select` cujo evento não existe **não dá erro: produz
  zero linhas, em silêncio**. Medido: 33 dos 242 pares do crosswalk caíam assim. O
  piloto teria afirmado 242 links e gravado 209.
- **Decisão:** a viabilidade de cada link é decidida **antes** de gerar o SQL, e a
  perda vai escrita no cabeçalho do arquivo, com o motivo de cada lado.
- **Motivo:** a diferença entre o que se afirma e o que existe é exatamente o que
  este repositório existe para não produzir.
- **Consequência:** `PARES_QUE_NAO_VIRAM_LINK` no relatório do gerador; o portão
  verifica 209 e não 242. E, no caminho, foi encontrado um erro real: 15 `CHAIN_ID`
  colidiam quando a chave era `grupo:nome:registro` — a marca nacional e a da UE, com
  o mesmo nome e o mesmo registro. O importador colava a antecedência de uma marca na
  outra. O `ST13` entrou na chave.
- **Quem decidiu:** decisão técnica do COMPETITOR FORESIGHT PILOT.

---

### D-023 — Paridade EAME: os três países, a MESMA régua, e nenhum matcher novo
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a rodada 1 mediu `TRADEMARK ↔ LOCAL REGISTRATION` só na Espanha,
  numa missão que é EAME. Antes de recoletar qualquer coisa, as foundations
  foram lidas: a Itália publica o registro inteiro em CSV aberto (CC BY 4.0,
  17.695 produtos) e a França publica o E-Phy pelo data.gouv.fr (Licence
  Ouverte, 15.140 produtos). **As duas portas já existiam.**
- **Decisão:** criar `scripts/registro_local.py`, que põe os três registros na
  MESMA forma, e `scripts/concorrente_paridade.py`, que **importa** `normalizar`,
  `cruzar` e `contrafactual_frouxo` de `concorrente_crosswalk.py`.
- **Motivo:** três matchers produziriam três resultados que ninguém consegue
  comparar. Um teste em Python guarda a identidade das funções (`assertIs`) para
  que a divergência não volte em silêncio.
- **Consequência:** **1.683 cadeias ligadas** — 209 ES, 334 IT, 1.140 FR — com
  126 falsos links recusados. A Espanha saiu com os números **idênticos** aos da
  rodada 1 (209/24/9/5.335, 158/51), e essa igualdade é o teste que prova que a
  refatoração não mexeu no que já estava medido.
- **Quem decidiu:** Luciano, na rodada final.

### D-024 — Titular antecessor não é agrupado, mas é CONTADO
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** os registros de IT e FR carregam décadas de razões sociais que
  hoje se associam a outros grupos: `AVENTIS CROPSCIENCE ITALIA` (771 IT),
  `DU PONT DE NEMOURS ITALIANA` (467), `DOW AGROSCIENCES` (267 FR),
  `RHONE POULENC` (257), `CIBA GEIGY` (222), `MONSANTO` (182).
- **Decisão:** **não agrupar**. Elas ficam listadas em
  `ANTECESSORES_NAO_AGRUPADOS` e são contadas — 1.351 registros na Itália e
  1.458 na França.
- **Motivo:** dobrar uma razão social antecessora no grupo de hoje é uma
  afirmação **societária** que este piloto não tem. É a mesma recusa que separa
  `SHARDA CROPCHEM ESPAÑA` de `SHARDA EUROPE`.
- **Consequência:** o agrupamento por titular **SUBCONTA** o concorrente em IT e
  FR, e a subcontagem tem tamanho publicado em vez de virar nota de rodapé.
- **Quem decidiu:** decisão técnica da rodada final.

### D-025 — Quatro pares semânticos: a frase verdadeira a um passo da falsa
- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a rodada 1 produziu cinco afirmações que estavam a um passo de
  virar falsas por generalização.
- **Decisão:** cada uma vira um PAR de estados, e nenhum lado pode ser publicado
  sem o outro:

  | observado | e o que continua NÃO PROVADO |
  |---|---|
  | `HISTORICAL_PRECEDENCE_OBSERVED` = 1.087/1.652 | `OPERATIONAL_EARLY_WARNING_VALUE = NOT_PROVED` |
  | `RECENT_TRADEMARK_ACTIVITY_EXISTS = YES` | `DAILY_VALUE = NOT_PROVED` |
  | `REGULATORY_CHANGE_IN_THIS_INTERVAL = 0 OBSERVED` | `REGULATORY_CHANGE_CADENCE = NOT_PROVED` |
  | `PATENT_BRAND_LINKAGE_ROUTE = REFUTED_FOR_PILOT` | `PATENT_WATCH = NOT_TESTED` |

- **Motivo:** mediana de antecedência de ~4 anos pode significar **cedo demais**,
  e não aviso prévio útil. Uma fotografia não mede cadência. Dois dias são dois
  dias. E refutar uma camada com o teste de UMA rota é o erro que este piloto
  passou a rodada inteira evitando.
- **Consequência:** `COMPETITOR-EAME-VEREDITOS.json`, quatro testes em
  `tests/test_concorrente.py` (`OsQuatroParesSemanticos`) e um veredicto POR
  CAPACIDADE — `A PROMISING · B PROVED · C PARTIAL · D DEMOTED/NOT_USED` —
  porque um veredicto único apagaria três resultados diferentes.
- **Quem decidiu:** Luciano, na rodada final.

### D-026 — `NOT_JOINED_IN_THIS_MISSION` substitui `NOT_AVAILABLE`
- **Data:** 2026-08-30
- **Estado:** DECIDIDO · **REVOGA** a redação da rodada 1
- **Contexto:** a rodada 1 escreveu que META e CREATOR "não existem no
  repositório". **Estava errado**, e do jeito mais caro: era uma afirmação
  GLOBAL feita a partir de um SNAPSHOT. Medido: o Creator Map está **congelado
  com handoff canônico** em `claude/eame-agro-creators-map-77c4ld`, e a missão
  Meta corre em paralelo com **1.111 anúncios** dos mesmos seis concorrentes.
- **Decisão:** o vocabulário passa a ser
  `<CAMADA>_DATA_AVAILABLE_IN_THIS_SNAPSHOT = NO` +
  `ESTADO = NOT_JOINED_IN_THIS_MISSION` + o lugar onde a outra missão vive.
- **Motivo:** uma branch só pode declarar o que ELA juntou. O refresh final
  junta os **HANDOFFS**, não os branches.
- **Consequência:** medida a prontidão da junção em vez de esperá-la — leitura
  somente-leitura da branch da Meta, casando nome de produto com a MESMA
  `normalizar()` do crosswalk: **145 produtos provados na Meta, 70 com marca
  correspondente no TMview, e 36 destes com registro local também `PROVED`**.
  São **36 cadeias de três camadas** prontas para o refresh. Nenhum merge foi
  feito. E um teste proíbe que a frase de ausência global volte.
- **Quem decidiu:** Luciano, na rodada final.

---

## D-2026-09-02 · A MADRUGADA DOS RÓTULOS

**O que se decidiu:** ler os 163 rótulos autorizados por dentro, em vez de seguir
declarando 11,7% de cobertura como limitação permanente.

**Por que agora:** a cobertura de uso lido era a limitação mais cara do projeto — ela
alimenta o pior erro possível do sistema, que é dizer que o cliente não tem produto para
um alvo quando ele tem. A lição foi paga pelo Brasil: o Nimitz EC tinha 3 culturas no
catálogo e 19 no registro.

### As seis leis que nasceram nesta noite

| lei | onde doeu |
|---|---|
| **FERRAMENTA QUE RECUSA NÃO É PORTA FECHADA** | o `curl` devolvia 0 bytes com HTTP 200; o `urllib` devolveu 222 KB |
| **O CORPUS É AMOSTRA DAS NOSSAS CONSULTAS** | herbicida «caiu» de 1º para 3º porque *nós* abrimos outros recortes |
| **SOMAR AS DUAS PLATEIAS NÃO DESCREVE NENHUM MUNDO** | 54 dos 116 pares eram horta doméstica |
| **ESPECTRO DE PRODUTO NÃO É ESPECTRO NA CULTURA** | o herbicida declara duas listas separadas; juntá-las é ato nosso |
| **LUZ VERDE SÓ VALE PARA O QUE ELA OLHA** | a validação de órfãos usava lista fechada e ignorava as famílias novas |
| **CENSO E AMOSTRA NÃO SÃO A MESMA AUSÊNCIA** | «0 de 163» é afirmável; «não achamos em 102 de 163» não é |

### Os números

| | antes | depois |
|---|---|---|
| cobertura de uso lido | 19/163 (11,7%) | **102/163 (62,6%)** |
| pares do rótulo | 219 | **2.030** |
| pares da conversa | 46 | **116** |
| objetos no pacote | 1.688 | **3.756** |

### O erro operacional da noite, e o que ele ensinou

`rm -rf /c/eame-sintonia/Scripts` apagou os **75 arquivos de `scripts/`**, porque no
Windows `Scripts` e `scripts` são a mesma pasta. Nada se perdeu — tudo estava commitado —
mas se houvesse trabalho não-commitado teria ido embora. O `pip` sem `--target` é a causa
raiz: ele instalou dentro do repositório.

> **UM NOME QUE DIFERE SÓ NA CAIXA NÃO É UM NOME DIFERENTE.**

### Uma afirmação nossa foi ao chão

O resumo executivo dizia que o corpus de vídeo «confirmava por rota independente» que
herbicida era a maior categoria. Não confirmava — confirmava que tínhamos aberto mais
recortes de daninha. A frase foi corrigida no lugar onde estava, com a data e o motivo, em
vez de apagada.

**Quem decidiu:** Luciano autorizou a missão da madrugada («continuar até as 10 da manhã,
sempre organizando material para um piloto»). As escolhas técnicas de cada bloco foram
tomadas na execução e estão em `docs/regras/REGUA-ITALIA-FITOSSANITARIA.md` (leis 8 e 9) e
nos cabeçalhos de `scripts/rotulos_ler.py`, `scripts/rotulos_censo.py` e
`scripts/cruzar_regua_rotulo.py`.

---

## PERGUNTAS PENDENTES

| # | Pergunta | Bloqueia | Aberta em |
|---|---|---|---|
| P-001 | ~~Confirmar D-003~~ — **resolvida** pela MISSÃO 02 §0: não versionar dumps grandes, amostras em `data/samples`, bruto temporário em `data/raw` local. | — | resolvida 2026-08-28 |
| P-002 | Quem é a audiência da apresentação e qual a data-alvo? | `07-apresentacao` | 2026-08-28 |
| P-003 | ~~Que dados internos da ADAMA EAME estarão disponíveis?~~ — **resolvida: NENHUM.** O produto é EXTERNAL-ONLY por decisão do cliente, e nenhuma saída pode afirmar REVENUE, MARGIN, SALES ou ROI REALIZED. O portfólio **registrado** ficou resolvido por fonte pública (ROPF/E-Phy — ver CAP-003/CAP-004); o portfólio **comercial** (vendas, foco, pipeline) não é público e continua `NÃO SEI` — por premissa, não por falta de esforço. | — | resolvida 2026-08-29 |
| P-004 | Idioma exigido nos entregáveis finais? | Todos os docs | 2026-08-28 |
| P-005 | Restrições jurídicas / GDPR / licença aplicáveis ao uso pretendido? | `fontes`, `capacidades` | 2026-08-28 |
| P-006 | Criar conta institucional EPPO para obter token da API (EU-T3-001)? É gratuita, mas fica em nome de alguém. | EU-T3-001 | 2026-08-28 |
| P-009 | Obter chave da YouTube Data API e decidir se a ADAMA quer perfilar criadores individuais (T8). Questão de GDPR distinta da de T5. | T8 inteiro | 2026-08-28 |
| P-008 | Perfilamento de pesquisadores identificados (EU-T5-001/OpenAlex): revisão GDPR antes de qualquer tela que liste pessoas nomeadas. **Continua ABERTA.** A MISSÃO 10C registrou os limites provisórios em `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md` — `NAMED_RESEARCHER_PUBLIC_SCREEN = BLOCKED_PENDING_LEGAL_REVIEW`. Isso **não** é parecer jurídico e não fecha a pendência. | T6, people graph, protótipo, filas de 20 | 2026-08-28 |
| P-007 | Uso e difusão de coordenadas de parcela do RAIF (ES-T3-001): revisão jurídica antes de expor em tela externa. | ES-T3-001, protótipo | 2026-08-28 |
