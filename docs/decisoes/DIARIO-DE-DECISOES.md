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
- **Decisão:** toda cadeia que produz um fato do piloto vive em `provas/chain.py` e
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
  digitado — `regras/proveniencia.py` passa a ser o dono do diretório `raw-paid/`;
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
nos cabeçalhos de `coleta/rotulos_ler.py`, `regras/rotulos_censo.py` e
`coleta/cruzar_regua_rotulo.py`.

---

### D-027 — A Bíblia Canônica da Coleta, e a emenda V1.1
- **Data:** 2026-09-07
- **Estado:** DECIDIDO
- **Contexto:** As leis da coleta viviam espalhadas por 63 sítios — cabeçalho de script,
  README, prompt de aba e `if` solto. Espalhadas assim não se consultam: redescobrem-se, e a
  lei redescoberta nunca é igual à que já existia.
- **Decisão:** `BIBLIA-CANONICA-DA-COLETA.md`, na raiz, passa a ser o **dono canônico da lei
  da coleta**. `AGENTS.md` continua dono da lei do mapa, `README.md` do método e `CLAUDE.md`
  do design — a Bíblia aponta para eles e não os repete. Ela separa `LAW_STATUS` de
  `IMPLEMENTATION_STATUS`: **«é lei» nunca significa «já funciona»**.
  - **V1** (48 leis) consolidou o que já existia. Nenhuma lei antiga foi apagada: 58 das 63
    ficam `KEEP`.
  - **V1.1** (+30 leis, total 78) incorporou duas emendas: a **observabilidade** (PARTE XVI —
    o System Map é a camada oficial de observabilidade visual, e tudo tem de ser
    renderizável) e as **leis roubadas** de sistemas maduros de coleta (PARTE XVII —
    artefato ≠ fato, watermark, corrida `COMPLETE`, corrida de reparo, três eixos de
    confiança).
- **Motivo:** Sem uma constituição, cada missão de coleta reabria decisões já tomadas e
  pagava de novo o preço de aprendê-las. E sem separar lei de implementação, «está escrito»
  passava por «está funcionando» — foi assim que `EAME_COLLECTION_ENTRY_GATE` chegou a dizer
  `READY` ao lado de `LOCATION_CONTRACT_COMPLETE = NO`.
- **Consequência:**
  - `docs/biblia/leis.json` é **derivado** do texto, nunca escrito à mão, e
    `provas/valida_biblia.py` + `tests/test_biblia.py` provam que os dois dizem a mesma
    coisa. Ambos entram no CI.
  - A matriz `docs/biblia/CONFORMIDADE-ITALIA.md` mede a Itália contra as 78:
    24 `IMPLEMENTED` · 42 `PARTIAL` · 11 `ABSENT` · 1 `NOT_APPLICABLE`.
  - Oito conflitos ficaram registrados com ficheiro e linha
    (`docs/biblia/MATRIZ-DE-CONFLITOS.md`). **Nenhum foi consertado**: missão fundacional.
  - Fica **uma decisão em aberto para o dono** (C-003): o sentinela do desconhecido tem cinco
    grafias no repositório (`NAO_SEI` 344 · `NOT_KNOWN` 123 · `UNKNOWN` 95 · `NÃO SEI` 57 ·
    `NAO SEI` 35). A Bíblia fixou o **significado** e deixou a **grafia** como
    `DECISION_REQUIRED` — escolher agora quebraria dado já gravado.
  - Nenhuma plataforma foi instalada. Nenhum coletor, workflow, orquestrador, executor,
    admissão, banco ou pipeline de produção foi alterado funcionalmente.
- **Quem decidiu:** Luciano, nas missões fundacionais «Bíblia Canônica da Coleta» e nas duas
  emendas («GPU do SINTONIA» e «pós-pesquisa de arquiteturas maduras»). As escolhas de
  consolidação — o que virou lei nova e o que foi absorvido por lei existente — estão
  registradas em `docs/biblia/EMENDA-V1-1.md`.

---

### D-028 — GitHub guarda a engenharia; Supabase guarda a memória operacional
- **Data:** 2026-09-08
- **Estado:** DECIDIDO
- **Contexto:** O SINTONIA já tem infraestrutura real — GitHub e Supabase — e nenhuma lei
  dizia o que pertence a cada um. A missão mandava **medir antes de definir**, e a medição
  está em `docs/biblia/CENSO-DA-INFRAESTRUTURA.md`.
- **Decisão:** Bíblia **V1.1 → V1.2** (+22 leis, total 100). Duas partes novas:
  - **PARTE XVIII · A INFRAESTRUTURA** (`COL-LAW-301`–`316`) —
    `INFRASTRUCTURE ≠ SEMANTIC AUTHORITY`. O GitHub responde *«qual engenharia estava
    valendo?»*; o Supabase responde *«o que aconteceu, e como está agora?»*; a Bíblia
    governa os dois. Nenhum produtor escreve no canônico por conhecer a tabela; o GitHub
    Actions não é orquestrador; agenda não é política de coleta; bytes não são metadata.
  - **PARTE XIX · O PLANO DE REFERÊNCIA** (`COL-LAW-401`–`406`) — dado de referência não é
    configuração, declara autoridade, distingue `LAST_CHECKED` de `LAST_CHANGED` e preserva
    `VALID_FROM`/`VALID_TO`. **`ABSENT` por inteiro** — é `TARGET`, e o mapa não o desenha
    como `CURRENT`.
- **Motivo:** Sem papéis declarados, a conveniência decide — e a conveniência escreve JSON no
  Git porque é fácil. Foi exatamente o que aconteceu com a Itália.
- **Consequência, e duas surpresas da medição:**
  - **Bypass para dentro do Supabase: ZERO.** Os 7 caminhos de escrita medidos são todos
    canônicos. O padrão da casa já é `artefato → gerador → .sql versionado → Actions →
    Supabase`, e funciona porque **a credencial só existe como segredo do runner**.
  - **O bypass real é ao contrário.** `coleta/italy_recurrent_collect.mjs:144` grava recibo,
    144 observações **e 12 MB de bytes** dentro do Git, enquanto `collection_run`,
    `raw_asset` e o bucket `raw` existem, estão provados por round-trip com hash, e estão
    vazios. Registrado como **G-30**, e é a mesma fratura da C-002 vista pela
    infraestrutura — por isso **G-02 e G-30 passam a ser a mesma missão**.
  - Itália contra 100 leis: 34 `IMPLEMENTED` · 46 `PARTIAL` · 18 `ABSENT` ·
    2 `NOT_APPLICABLE`. O `IMPLEMENTED` subiu 10 **sem ninguém programar**: era
    infraestrutura já certa que não tinha lei que a reconhecesse.
  - **Nada foi migrado, criado ou alterado**: nenhuma tabela, migration, bucket, byte,
    writer, workflow funcional ou credencial.
- **Quem decidiu:** Luciano, na missão «Infraestrutura oficial — GitHub + Supabase + System
  Map». As escolhas de consolidação — o que virou lei e o que foi absorvido — estão em
  `docs/biblia/EMENDA-V1-2.md`.

---

### D-029 — Caminho não é captura, e o banco já sabia representar isso

- **Data:** 2026-09-08
- **Decisão:** **não criar tabela de ocorrência.** O menor delta de esquema é **uma** tabela
  nova, `derived_artifact`, e mais nada. Projetada, **não aplicada**.
- **Por quê:**
  - O censo anterior concluiu que os 6 PDFs repetidos eram «o mesmo documento em dois
    sítios» — palpite lido no **nome da pasta**. Medido pela prova de captura de cada
    caminho (`system-map/scripts/censo_de_identidade_it.py`): **6 de 6 são
    `INDEPENDENT_CAPTURES_SAME_CONTENT`** — duas idas reais à fonte que trouxeram os mesmos
    bytes, e num dos casos com **5 dias e outra rota** entre elas. O próprio servidor datou a
    resposta; a prova não é auto-declarada.
  - E isso vale mais do que a contagem: **duas capturas do mesmo byte em dias diferentes
    provam que o documento não mudou nesse intervalo.**
  - `raw_asset.sha256` **nunca foi `UNIQUE`** — é índice (`001:119`). O `unique` é do
    `storage_path` (`001:106`). O diagnóstico do P-011 tinha lido um pelo outro, e daí
    inventou um bloqueador. As 49 cópias cabem hoje, **sem tocar no esquema**.
  - `conteudo_visto_em` já escreve a lei certa — «um conteúdo, duas observações» — mas na
    entidade «item de canal» (`UNIQUE (canal_id, content_id)`), não nos bytes. `PARCIAL`.
  - A única lacuna real é o **artefato derivado**: `transcricao` é de vídeo,
    `catalogo_produto_documento` é de catálogo, e `derivacao` é conclusão analítica, não
    artefato. E `raw_asset` **não pode** ganhar `parent_sha256`: seria apagar a COL-LAW-007
    dentro da tabela chamada «bruto».
- **O que ficou registrado, não consertado:** `G-39` (falta `derived_artifact`) · `G-40`
  (11 das 49 cópias sem prova de captura) · `G-41` (21 de 21 migrations dizem «NÃO
  EXECUTADA» e pelo menos 001–016 estão aplicadas — deriva de comentário; **migration é
  história e não se reescreve**).
- **Duas leis desceram para `PARTIAL`, e ninguém desfez trabalho.** COL-LAW-106 e
  COL-LAW-210 tinham sido dadas por cumpridas medindo **uma** estrada. Medido: `PILOT_RUN`
  aparece **0 vezes** no mapa, e as 6 linhas do `runs.ndjson` não têm campo de fecho. Placar:
  **37 `IMPLEMENTED` · 47 `PARTIAL` · 18 `ABSENT` · 2 `NOT_APPLICABLE`**.
- **Nada foi escrito, copiado, migrado nem apagado:** 0 escritas no Supabase, 0 uploads,
  0 deletes, 0 migrations aplicadas, 0 bytes italianos movidos. `PADRAO_DA_COLETA` continua
  exatamente no estado herdado do G-36 — sem `--fixar`.
- **Detalhe completo:** [`../operacao/IDENTIDADE-DO-ARTEFATO.md`](../operacao/IDENTIDADE-DO-ARTEFATO.md).


### D-030 — Os bytes italianos já estão no Supabase; a memória operacional deles não

- **Data:** 2026-09-08
- **O que se descobriu:** deixou de ser verdade dizer «a Itália não está no Supabase».
  Há **195 objetos** sob o prefixo `IT/` no bucket `raw`, **80,7 MB** — e **zero** linhas de
  `raw_asset` e **zero** de `collection_run` a reclamá-los. Um armazém cheio com o livro de
  entrada em branco.
- **Quem os pôs lá, medido:** a cadeia tem dois passos e ninguém obriga os dois a andarem
  juntos. O passo 1 (`scripts/storage_preservar.py --enviar`) vive **fora deste
  repositório** — é a máquina do operador, listada como não integrada em
  `docs/adama/INTEGRACAO-CATALOGO-ADAMA-ES.md:69`, com teste que reprova se entrar. O passo 2
  (`guarda/catalogo_importar.py`) vive aqui e **está preso à Espanha pela própria escrita do
  ficheiro**: entradas `ADAMA-ES-*`, saída `ADAMA-ES-CATALOGO-*.sql`. Não há equivalente
  italiano. E as duas importações italianas que existem (`IT-CAMADAS`, `IT-LASTMILE`)
  **nunca mencionam `raw_asset` nem `collection_run`** — a Itália importou camadas
  analíticas e nunca importou a procedência.
- **Classificação:** `STORAGE_ONLY_PIPELINE`. Não é legado (`raw_asset` existe desde a `001`),
  não é escrita falhada (não existe importador italiano do bruto para ter falhado), e não é
  decisão (não há decisão escrita — **ausência de decisão não é decisão**).
- **A procedência perdeu-se? NÃO.** Ela não está no banco, está no Git:
  `research/adama-italy-product-intelligence-deep/LABEL-MANIFEST.json` traz **141 de 141**
  documentos com `SHA256`, `BYTES`, `CAPTURED_AT`, `SOURCE_URL` e `SOURCE_ID`. **Mas a
  corrida é `RUN_NOT_PROVABLE`** — nenhum registo declara `run_id`. Procedência recuperável
  **não autoriza** procedência inventada: nenhuma corrida histórica foi criada.
- **Dois acervos, não um.** Comparado por impressão digital: **0 dos 43** conteúdos do Golden
  Path estão no armazém. O armazém é o catálogo comercial da ADAMA Itália; o Golden Path são
  boletins fitossanitários regionais.
- **Três contagens que não batem, e ficam as três escritas:** 141 documentos no manifesto ·
  138 conteúdos únicos · 139 objetos `DOCUMENT`. `NÃO_RECONCILIADO` — a medição externa
  trouxe contagens por prefixo, não a lista de chaves, e sem elas qualquer explicação seria
  inventada. **É exatamente a conta que uma linha de `raw_asset` por objeto tornaria trivial.**
- **A decisão de ontem não mudou:** não é preciso tabela de ocorrência, e `derived_artifact`
  continua sendo a única mudança de esquema proposta. O que se achou não é lacuna de
  **esquema** — é lacuna de **caminho de escrita**.
- **Gap registrado, um só:** `G-42 · ITALY_STORAGE_METADATA_RECONCILIATION`.
- **Nada foi escrito, enviado, apagado ou retrocriado:** 0 `INSERT`/`UPDATE`/`DELETE`, 0
  uploads, 0 DDL, 0 migrations aplicadas, 0 bytes movidos, 0 corridas históricas.
- **Detalhe completo:** [`../operacao/ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md`](../operacao/ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md).


### D-031 — A conta do armazém fecha; a garantia é para a frente, e o passado não se fabrica

- **Data:** 2026-09-08
- **A conta fechou, e com causa.** 141 registos · 138 conteúdos · 139 objetos deixaram de ser
  «três números que não batem». As duas diferenças têm causas **diferentes**, e é isso que
  faltava dizer: `141 − 138 = 3` documentos que servem a **dois produtos cada um**;
  `139 − 138 = 1` conteúdo que a ADAMA **publicou em duas URLs** (`media/731` e `media/6321`).
  Prova: a `SOURCE_URL` de cada grupo repetido no manifesto — os outros dois grupos têm **uma**
  URL cada e **um** objeto cada. Objetos previstos pelo manifesto = **139** = objetos medidos.
  **Nenhum byte perdido.**
- **E a prova tem força declarada:** `PREFIX_MATCH`, não `FULL_SHA256_MATCH`. A chave carrega
  16 caracteres do hash, que é **endereço, não identidade**. Subir para igualdade completa
  exige ler os bytes de volta, e esta sessão não tem credencial.
- **Decisão sobre o histórico: NÃO backfillar.** Os 195 objetos ficam como classe explícita de
  dívida — `HISTORICAL_STORAGE_WITHOUT_OPERATIONAL_RUN`. Preservados, com procedência
  documental recuperável (141 de 141) e `RUN` `NOT_PROVABLE`. **Sem `LEGACY-IT`, sem
  `UNKNOWN-RUN`, sem `BACKFILL-RUN`** — e **sem relaxar o `run_id NOT NULL`**, que cederia a
  lei para acomodar a exceção. A migration `001` já dizia que proveniência é prospectiva.
- **Decisão sobre o futuro: um dono canônico da escrita**, `guarda/preservar_coleta.py`.
  Censo dos escritores atuais: **cinco, e nenhum dono do par byte+memória** — dois workflows
  presos a uma rota, três geradores de SQL de um país ou entidade só. Por isso não havia quem
  estender, e por isso o dono é novo. **Mas o padrão é reusado:** gera SQL auditável em vez de
  falar com o banco, como `guarda/catalogo_importar.py` já fazia, e passa no portão da casa
  (`guarda/sql_conferir.py`), apóstrofes italianas incluídas.
- **A doutrina que ele aplica:** `EXECUTOR` produz artefato e não conhece banco; `DONO
  CANÔNICO` persiste o par. Nenhum executor grava só porque conhece a `SUPABASE_URL`.
- **Atomicidade, respondida:** envio passa + memória falha → `RUN_STATE = PARTIAL`,
  `PENDÊNCIA = UPLOAD_PENDING_METADATA`, **nunca `COMPLETE`**. E o byte **não** é apagado para
  fingir atomicidade — a porta do armazém tem três métodos e nenhum é «remover». Retry repete
  **só** a etapa em falta, sem subir byte outra vez e sem duplicar linha
  (`on conflict (storage_path) do nothing`).
- **Estado novo no banco: nenhum.** A pendência mora no manifesto e mapeia para o `parcial`
  que o enum de `001` já tem. Era o candidato mais provável a virar uma sexta alteração de
  esquema, e não virou.
- **`derived_artifact` continua sendo a única lacuna de esquema.** Continua **não aplicada**.
- **G-42 passa a ter duas dimensões no mesmo gap:** forward **FECHADO** em código e teste;
  histórico **ABERTO de propósito**.
- **Nada foi escrito, enviado, apagado ou migrado:** 0 escritas LIVE, 0 uploads, 0 deletes,
  0 migrations aplicadas, 0 corridas retrocriadas, 0 bytes movidos. Tudo provado com armazém
  de mentira — sem banco, sem rede, sem instalar nada.
- **Detalhe completo:** [`../operacao/ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md`](../operacao/ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md).


### D-032 — SQL aceite não é linha gravada: a garantia forward passa a ler o banco

- **Data:** 2026-09-08
- **O red team tinha razão, duas vezes, e era o mesmo erro:**
  1. `escrever_memoria(sql)` era dada por bem-sucedida **por não ter rebentado**, e o número
     de linhas era o **esperado** copiado para o lugar do **observado**. Com
     `on conflict do nothing`, o SQL pode correr inteiro, **não gravar nada** e não se
     queixar — corrida verde sobre banco vazio, que é o estado italiano em pequeno.
  2. A corrida abria `'rodando'` e **nunca era promovida**. Era possível ter
     `RUN_STATE = COMPLETE` no manifesto e `status = 'rodando'` no Postgres.
- **O código estava certo na lógica e cego no resultado.** Corrigido: `LINHAS_OBSERVADAS`
  vem de um `SELECT`; `sql_de_fecho()` promove a `concluida` e o estado é **lido de volta**;
  as condições de fecho passaram de 6 para **9**, com `reconciliacao_observada` e
  `banco_diz_concluida`.
- **`do nothing` deixou de ser esconderijo.** A linha existente é lida e comparada **antes**
  de escrever: tudo igual → `REUSED_METADATA`; `sha256` ou corrida diferentes →
  `METADATA_CONFLICT`; identidade congelada da corrida diferente (COL-LAW-211) →
  `RUN_ID_CONFLICT`. Em conflito **nada é escrito**.
- **Provado contra banco de verdade, e nenhum deles é produção:** 18 provas contra SQLite
  real em memória, e a mesma bateria contra **Postgres 16** com a `migration 001`
  **original**, em contentor que morre no job (`banco-descartavel.yml`). A prova em Postgres
  **recusa-se a arrancar** se o endereço não for local — lista de permissão, não de bloqueio,
  porque lista de bloqueio falha por omissão. O próprio workflow testa a recusa.
- **`DB_TESTED (SQLITE)` não se escreve como `DB_TESTED (POSTGRES)`.** SQLite não tem `enum`
  nem `timestamptz`; o esquema local é **tradução declarada**, não cópia.
- **CAN DO ≠ DID DO.** Medido: **zero consumidores reais** — só testes, provas e o adaptador
  descartável. Há teste que reprova se alguém ligar a peça e esquecer de atualizar o estado.
  Primeiro consumidor designado: `coleta/golden_path_pdf.py`. **Não foi ligado.**
- **Estado do G-42 forward:** `FORWARD_IMPLEMENTED_AND_DB_TESTED` · `LIVE_OBSERVATION_PENDING`.
  Não é `OPERATIONAL`, não é `OBSERVED_LIVE`.
- **`derived_artifact` continua sendo a única lacuna de esquema.** E reforçou-se: nenhum dos
  estados novos (`METADATA_CONFLICT`, `RUN_ID_CONFLICT`, `UPLOAD_PENDING_METADATA`,
  `RUN_NOT_CLOSED_IN_DB`) pediu coluna ou enum — todos vivem no manifesto e mapeiam para o
  `parcial` que a `001` já tem.
- **Nada tocou produção:** 0 escritas LIVE, 0 uploads, 0 deletes, 0 migrations aplicadas em
  produção, 0 corridas retrocriadas.
- **Detalhe completo:** [`../operacao/ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md`](../operacao/ARMAZEM-ITALIANO-SEM-LIVRO-DE-ENTRADA.md) §J2.


### D-033 — Postgres subir não é Postgres passar

- **Data:** 2026-09-08
- **A promoção anterior era prematura, e o erro foi meu.** Escrevi `DB_TESTED` **sem ler o
  resultado do CI**. O workflow `banco-descartavel`, execução `34233443996`, deu **FAILURE**:
  `ValueError: invalid literal for int() with base 10: 'count
0
(1 row)'`. O contentor
  arrancou, a ligação passou, a `migration 001` foi aplicada — e a prova rebentou no primeiro
  `count`.
- **A causa era de ferramenta, não de arquitetura.** O comando do `psql` era montado por
  índice: `cmd[3:3] = ["-t","-A","-F",sep]` inseria os sinalizadores **entre** o `-v` e o
  `ON_ERROR_STOP=1`. O `psql` leu «define uma variável chamada `-t`», a saída voltou alinhada
  com cabeçalho e rodapé, e tudo a jusante leu lixo. **Não se conserta aprendendo a apanhar
  `count`/`(1 row)` com as mãos — pede-se a saída certa:** `-X -q -A -t -F`.
- **Três brechas fechadas na mesma passagem:**
  1. **`CONTAR NÃO É CONFERIR`.** Entre a leitura prévia e o nosso `insert`, outro escritor
     pode meter uma linha divergente no mesmo caminho; o `do nothing` cala-se e a **contagem
     bate na mesma**. Agora cada linha é lida de volta **depois** da escrita e comparada campo
     a campo (`CONFERENCIA_POS_ESCRITA`), com caso de corrida encenado a prová-lo.
  2. **`STARTED_AT` NÃO É `FINISHED_AT`.** O fecho caía para o `started_at` quando não tinha
     hora de fim — a corrida dizia ter acabado no instante em que começou, falso e com cara de
     medido. Sem hora declarada, a autoridade é o `now()` do **próprio banco**.
  3. **A tranca comparava pedaços de texto.** `db.exemplo.com` contém `db.`;
     `localhost.atacante.example` contém `localhost`. Agora a URL é **decomposta**: `hostname`
     exatamente local **e** banco exatamente `descartavel`.
- **CI verde, lido:** execução `34235362771` — **19/19** cenários contra **Postgres 16 real**,
  e as **4 recusas** da tranca. O passo negativo corre com `if: always()`, porque uma tranca
  que só se testa quando está tudo bem não é uma tranca.
- **Os 19 cenários passam a correr também em SQLite, como ENSAIO local.** Não substituem o
  Postgres — substituem o **ciclo de espera** que deixou a correção anterior ir para o ar
  quebrada.
- **O nome da prova encolheu para o que ela mede:** `POSTGRES16_FOUNDATION_SCHEMA_TESTED`. Só
  a `migration 001`; as `002`–`021` não entram, e alargar isso não era o assunto.
- **Estado do G-42 forward:** `FORWARD_IMPLEMENTED` · `SQLITE_DB_TESTED` ·
  `POSTGRES16_FOUNDATION_SCHEMA_TESTED` · `LIVE_OBSERVATION_PENDING`. **Ainda não
  `OPERATIONAL`:** medido, zero consumidores reais.
- **`derived_artifact` continua sendo a única lacuna de esquema.** Reforçado: os quatro
  estados de pendência e a conferência pós-escrita não pediram coluna nem enum.
- **Nada tocou produção:** 0 escritas, 0 migrations aplicadas em produção, 0 corridas
  retrocriadas.


### D-034 — A casa do derivado: uma tabela, medida antes de desenhada

- **Data:** 2026-09-08 · **Estado:** `DESIGNED` · `IMPLEMENTED` · `DB_TESTED` ·
  **`LIVE_APPLIED = NÃO`** · **`OBSERVED = NÃO`**
- **O censo veio primeiro.** 7 produtores medidos, e **só 3** são de espécie
  `DERIVED_ARTIFACT`. A legenda que o YouTube entrega com o vídeo é `RAW_CAPTURE` — **nós não
  a produzimos**, e metê-la na tabela declararia uma linhagem que não existe. Campos extraídos
  são `STRUCTURED_RECORD`; um juízo de admissão é outro andar (COL-LAW-502).
- **O vocabulário já existia** em `leis/artefato.py`, com os 9 campos conferidos. A tabela
  **traduz** esse contrato em vez de inventar outro.
- **GRÃO:** uma linha é **um artefato que nós produzimos, de um conteúdo bruto, por uma
  ferramenta numa versão, com uns parâmetros, numa posição da série.** Testado contra os oito
  casos que a quebrariam.
- **IDENTIDADE:** `(parent_sha256, kind, producer, producer_version, parameters_hash,
  serie_posicao)`. **O `sha256` sozinho NÃO serve** — ele identifica bytes, não linhagem, e
  duas rotas podem chegar aos mesmos bytes. E o `sha256` **do filho fica fora da chave** de
  propósito: se entrasse, a mesma régua com resultado diferente viraria duas linhas caladas em
  vez de dar conflito.
- **`serie_posicao` é o único campo que existe por um caso que ainda não temos** — dez frames
  do mesmo vídeo colidiriam na mesma chave. Existe porque sem ele a chave é falsa no dia em
  que ele aparecer.
- **VERSÃO DA FERRAMENTA é obrigatória.** `whisper` não basta: `base` e `small` sobre o mesmo
  áudio dão textos diferentes e **os dois são legítimos** — está em
  `ferramentas/youtube_transcrever.py`. Versão histórica que não se prova entra `UNKNOWN`;
  **não se adivinha** a do `pdftotext` dos 43 legados.
- **O que ficou de fora, com motivo:** `parent_derived_artifact_id` (**zero** casos medidos;
  aditivo e barato depois) · `derivation_run` (sem prova; ficou um `derivation_batch` de texto,
  **rótulo e não entidade**, sem FK — e `collection_run` **não** foi esticada para significar
  algo que não é coleta) · coluna de `status` com erros (**a tabela guarda só o que existe**;
  derivação falhada não tem bytes e vive no manifesto) · corpo do texto no Postgres (bytes no
  Storage, memória no banco).
- **O LEGADO NÃO FOI REMENDADO.** 43 derivados · 0 linhas de `raw_asset` IT · **0 ligáveis
  honestamente**. Classe `LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT`. `raw_asset_id` é
  `NOT NULL` — que os 43 de hoje **não caibam é o desenho a funcionar**. Inventar as linhas em
  falta para a chave estrangeira ficar bonita seria fabricar a coleta que nunca foi registada.
- **`ON DELETE RESTRICT`, não `CASCADE`:** apagar um bruto com filhos levaria a linhagem junto,
  em silêncio. O banco recusa — a evidência vale mais do que a comodidade.
- **PROVA:** `banco-descartavel` execução **`34237653804` = SUCCESS**, lida. `17/17` casos da
  `022` + `19/19` da garantia forward + `4/4` recusas da tranca. Escopo declarado:
  **`FOUNDATION_MAIS_022`** — só a `001` e a `022`, porque a `022` não precisa das outras.
- **Um caso deu FAIL antes de dar PASS, e ainda bem:** o caso B (`sem raw, a FK recusa`) foi
  recusado pela trava de **unicidade**, não pela chave estrangeira — o órfão tinha a mesma
  identidade do caso A. **Recusar não é recusar pelo motivo certo.**
- **Nada aplicado em produção:** 0 migrations, 0 escritas, 0 uploads, 0 backfill, 0 corridas
  retrocriadas. **Primeiro produtor designado:** o Golden Path **para a frente** — nunca o
  legado retroativo.
- **Detalhe completo:** [`../operacao/A-CASA-DO-DERIVADO.md`](../operacao/A-CASA-DO-DERIVADO.md).


### D-035 — O pai por ID e o pai por SHA têm de ser o mesmo pai; e o grão é conteúdo

- **Data:** 2026-09-08 · **Estado:** `DB_TESTED` · **`LIVE_APPLIED = NÃO`**
- **A brecha era real, e foi REPRODUZIDA antes de fechada.** `raw_asset_id` podia apontar
  para o pai A enquanto `parent_sha256` dizia os bytes de B: as duas travas passavam, e a
  linha ficava a declarar dois pais. No Postgres descartável o resultado foi literal —
  `ACEITOU DOIS PAIS DIFERENTES`. **FK existir não basta.**
- **Fechado por chave estrangeira COMPOSTA, declarativa, sem gatilho:**
  `(raw_asset_id, parent_sha256) → raw_asset(id, sha256)`, com um
  `unique (id, sha256)` aditivo no pai — que **não pode reprovar sobre dado nenhum**, porque
  `id` já é chave primária. É a única coisa que a `022` toca fora da sua tabela.
- **`parent_sha256` FICA.** Removê-lo obrigaria a identidade a passar por `raw_asset_id`, e
  isso mudaria o grão de conteúdo para captura **pela porta dos fundos**. A coluna redundante
  não é conveniência: é o que torna o grão certo expressável.
- **GRÃO DECIDIDO: `CONTEÚDO POR RECEITA`.** Duas capturas dos mesmos bytes, derivadas com a
  mesma régua, dão **UMA** linha. **A assimetria com `raw_asset` é deliberada:** lá o grão é a
  ocorrência porque duas capturas são **dois factos sobre o mundo**; aqui há **um** facto — a
  nossa ferramenta, sobre estes bytes, com esta régua, dá este resultado. Correr duas vezes é
  trabalho repetido, não informação nova.
- **A procedência da captura não se perde, porque nunca morou aqui:** mora em `raw_asset`, uma
  linha por captura, e todas as irmãs acham-se com `where sha256 = <parent_sha256>`. O
  `raw_asset_id` do derivado é **testemunha — de qual cópia se leu — e não identidade**, e
  está escrito assim no comentário da coluna. **Nenhuma tabela nova foi criada.**
- **Duas frases minhas prometiam mais do que o banco cumpre, e foram corrigidas:**
  `derived_at NOT NULL` **não** garante que a data não foi copiada do `captured_at` (o banco
  vê um timestamptz, não vê de onde veio), e o banco confere o **formato** de
  `parameters_hash`, **não** a correspondência com o JSON. `DB_PROVES_PRESENT ≠
  DB_PROVES_NOT_COPIED`. Há teste que **insere uma linha com a data copiada e mostra que ela
  entra** — para que ninguém volte a escrever que o banco cumpre essa lei. **A autoridade é o
  writer**, e um gatilho que adivinhasse a serialização canónica seria uma segunda
  implementação da regra, livre para divergir da primeira.
- **A `022` foi corrigida NO PRÓPRIO FICHEIRO**, que é o padrão da casa para migration ainda
  não aplicada — precedente medido: a `014` nasceu `010` e foi renumerada. **Não se criou
  `023_corrige_022`** para simular a história de algo que nunca existiu em produção.
- **PROVA:** `banco-descartavel` execução **`34246698477` = SUCCESS**, lida. **23/23** casos da
  `022` + 19/19 da garantia forward + 4/4 recusas da tranca.
- **Nada em produção:** 0 migrations aplicadas, 0 escritas, 0 backfill, 0 corridas retrocriadas.
- **Detalhe completo:** [`../operacao/A-CASA-DO-DERIVADO.md`](../operacao/A-CASA-DO-DERIVADO.md) §B2 e §B3.


### D-036 — O dono canônico da escrita do derivado

- **Data:** 2026-09-08 · **Estado:** `WRITER` ✅ · `DB_TESTED` ✅ ·
  **`LIVE_APPLIED = NÃO`** · **`OBSERVED = NÃO`** · **`WRITER_READY_FOR_LIVE = SIM`**
- **Censo primeiro:** o único escritor de derivado hoje é `coleta/executor_texto_de_pdf.py`,
  que escreve um JSON. **Nada escreve na tabela.** `guarda/preservar_coleta.py` é o dono do
  **bruto** e é específico dele — forçá-lo a ser genérico faria dele uma coisa que não é de
  ninguém. Criou-se **um** dono novo ao lado, reusando as portas `Armazem` e `Memoria` e o
  `sha256`, e mais nada.
- **A lei central:** `ON CONFLICT DO NOTHING NÃO É IDEMPOTÊNCIA.` O banco recusa a linha
  repetida; se quem escreve ler esse silêncio como «tudo igual», uma derivação que passou a
  produzir **outro resultado** entra como `REUSED`. O `insert` deste dono **não tem
  `on conflict`**, de propósito: ele quer o erro para ir **ler** e comparar.
- **O que o dono possui, e ninguém mais:** `parent_sha256` (lido do `raw_asset`), `sha256` e
  `bytes` do filho (calculados dos bytes reais), `parameters_hash` (uma função canónica),
  `derived_at` (o relógio do writer) e `storage_path` (derivado da receita).
  **`DB_PROVES_PRESENT ≠ DB_PROVES_MEASURED`; `WRITER_PROVES_MEASURED`.**
- **Serialização canónica:** `sort_keys`, sem espaços, `ensure_ascii=False`, UTF-8; ausência
  de parâmetros = `b""`, cujo hash é o da cadeia vazia — o valor que a `022` já usava.
  ⚠️ **Não é RFC 8785**, e números de vírgula flutuante ficam declarados como fora do que ela
  resolve.
- **Seis estados, não quinze:** `INSERTED`, `REUSED`, `REUSED_AFTER_RACE`,
  `DERIVATION_DRIFT`, `STORAGE_CONFLICT`, `METADATA_NOT_RECONCILED`. **Nenhuma tabela de
  falhas.**
- **O caso adversarial fecha:** a mesma receita com outro resultado dá `DERIVATION_DRIFT` — o
  antigo não é apagado, não é sobrescrito, e nenhum byte novo sobe. **As duas versões são
  factos, e um deles é um defeito por descobrir.**
- **Corrida tratada:** violação de unicidade **não é sucesso automático**. Lê-se a linha que
  venceu e compara-se: igual → `REUSED_AFTER_RACE`; diferente → `DERIVATION_DRIFT`.
- **Bytes guardados + banco falha → `METADATA_NOT_RECONCILED`, e os bytes NÃO são apagados.**
  É a lei do G-42 aplicada ao derivado.
- **A ponte para o executor está DESLIGADA:** `entregar_ao_dono=None` por omissão, e o
  caminho antigo continua igual. Ela passa **só a receita** — nem o `sha256` do pai viaja
  nela, porque um campo que ninguém usa é um campo que um dia alguém usa mal.
- **Um limite declarado:** `REUSED` sai da leitura da **linha**; o writer não confirma no
  armazém que o objeto continua lá. Está documentado como é hoje, com teste, e é o próximo
  passo do dono.
- **PROVA:** `banco-descartavel` execução **`34249905763` = SUCCESS**. **32/32** casos
  Postgres (9 são do writer) + 19/19 da garantia forward + 4/4 recusas da tranca. **37**
  provas locais do writer.
- **Legado intocado:** 43 históricos, 0 migrados. **Produção intocada:** 0 escritas, 0
  migrations aplicadas.
- **Próxima missão:** aplicar a `022` LIVE, verificar, e ligar o Golden Path **para a frente**.
- **Detalhe:** [`../operacao/A-CASA-DO-DERIVADO.md`](../operacao/A-CASA-DO-DERIVADO.md) §G2 e §G3.


### D-037 — Red team do writer: três brechas, e uma delas eu tinha etiquetado como limite

- **Data:** 2026-09-08 · **`WRITER_READY_FOR_LIVE = SIM`** (era prematuro antes) ·
  **`LIVE_APPLIED = NÃO`**
- **1 · `REUSED` não confirmava que o byte ainda existia.** O writer respondia a partir da
  leitura da **linha**, sem perguntar ao armazém: uma ficha viva sobre um artefato apagado
  passava por «reaproveitado, está tudo bem». ⚠️ **E eu tinha escrito um teste que EXIGIA
  esse comportamento**, chamando-lhe «limite conhecido» — um teste assim impede quem vem
  consertar e dá ao defeito um ar de decisão. **`UMA LINHA NO BANCO NÃO É PROVA DE QUE O BYTE
  AINDA EXISTE.`** Agora `REUSED` exige cinco provas, e há **um** estado novo,
  `STORAGE_MISSING` — porque «o artefato sumiu» e «a ficha não entrou» são avarias diferentes
  com conserto diferente. E **não se reenvia o byte por conta própria:** curar em silêncio
  apagaria o rasto de que houve um buraco.
- **2 · O `storage_path` colapsava identidades que o banco distingue.** Ele não incluía o
  `parameters_hash`: o mesmo PDF a 150 e a 300 dpi são duas derivações legítimas pela `022` e
  **disputavam o mesmo endereço**. **`SE A IDENTIDADE DO BANCO DIZ QUE SÃO DUAS DERIVAÇÕES, O
  ENDEREÇO TEM DE PERMITIR QUE AS DUAS EXISTAM.`** O discriminante passou a ser o `sha256`
  **completo** da receita inteira — não um prefixo de 16 caracteres. O `sha256` do **filho**
  continua fora: se entrasse, um `DERIVATION_DRIFT` ganharia endereço novo e deixaria de ser
  drift. **A identidade da tabela NÃO mudou; a `022` está igual.**
- **3 · A ponte para o executor não carregava o `raw_asset_id`.** O dono ficava sem saber
  qual linha era o pai, e o meu teste só verificava que o callback fora chamado — **o que não
  prova nada**. A ponte foi removida; entrou `derivar_um(raw_asset_id, pdf, armazem,
  memoria)`, com o pai como contexto da unidade de trabalho. **Legado e forward ficam
  separados:** `correr()` continua a não conhecer o writer, e os 43 históricos continuam sem
  pai canónico.
- **4 · E o país deixou de ser do chamador.** Vem do `source_country` da corrida do pai, por
  `join` só de leitura, **sem coluna nova**. Onde o pai não prova, `NAO_SEI`.
- **PROVA:** `banco-descartavel` execução **`34255823282` = SUCCESS** — **38/38** casos
  Postgres (15 do writer) + 19/19 da garantia forward + 4/4 recusas da tranca. **50** provas
  locais do writer, incluindo o teste de ponta a ponta com o dono real e dois brutos
  distintos.
- **Nada em produção:** 0 escritas, 0 migrations aplicadas, 0 backfill. `022` continua
  **NOT LIVE**.
- **Próxima missão:** aplicar a `022` LIVE → verificar → ligar o Golden Path **forward** →
  primeiro derivado `OBSERVED`.
- **Detalhe:** [`../operacao/A-CASA-DO-DERIVADO.md`](../operacao/A-CASA-DO-DERIVADO.md) §G4.


### D-038 — O primeiro caminho forward real: 022 aplicada e o primeiro derivado italiano

- **Data:** 2026-09-08 · **`022 LIVE_APPLIED = SIM`** · **`RAW_FORWARD_OBSERVED = SIM`** ·
  **`DERIVED_FORWARD_OBSERVED = SIM`**
- **O portão antes do DDL, e por que ele existia.** `motor/cadeia_canonica.sh` percorre TODAS
  as migrations e pula pelo seu próprio livro-razão (`public.schema_migracao` — **não** o
  `supabase_migrations` do Supabase). Se esse livro estivesse vazio, a cadeia tentaria
  reaplicar 001–021 — e o próprio ficheiro avisa que **reaplicar a 015 RESSUSCITARIA uma
  coluna que a 018 aposentou**, porque `add column if not exists` passa em silêncio. Por isso
  o pré-voo (só leitura, run `34257470111`) mediu o livro **antes**: 20 versões lá,
  `APPLIED_SET_PREVISTO={022}`, **portão aberto por prova**.
- **Aplicada pelo mecanismo canónico** (run `34257805728`): 20 `SKIP`, `MIGRATION_022=PASS`.
  SHA do ficheiro aplicado: **`230be77d…`** — ⚠️ **a entrega original publicou `7f46ea93…`,
  e estava errado**: esse é o `sha256` do ficheiro **neste disco Windows**, com CRLF. O que a
  produção recebeu foi o blob do Git, com LF. Medi do lado errado da conversão de fim de
  linha, e o banco tinha o valor certo o tempo todo. Corrigido em D-039. **Readback de 30 provas** (run `34259433336`): tabela,
  15 colunas, FK composta com `ON DELETE RESTRICT`, os dois `unique`, os 4 `check`, os 4
  índices — e **0 linhas**. *A migration não cria história.* Invariantes intactos:
  `collection_run` 8→8, `raw_asset` 251→251.
- **O canário nasceu de uma captura NOVA**, não de história velha: `GET` real ao boletim da
  ARPAV (`IT-T2-002`), HTTP 200, `application/pdf`, 463.630 bytes, assinatura `%PDF-`
  conferida nos bytes — não no `content-type`.
- **⚠️ E o SHA veio IGUAL ao do ledger.** A minha suposição de que o ficheiro rolante teria
  mudado estava errada: o documento **não mudou** desde a captura histórica. Isso não invalida
  nada — é **uma captura nova de um conteúdo já conhecido**, que é exatamente a lei desta
  casa: *mesmos bytes não apagam a diferença entre duas capturas*.
- **A cadeia inteira pelos donos canónicos:** `preservar_coleta` → `RUN_STATE=COMPLETE`,
  `raw_asset 890`, byte conferido no armazém · `derivar_um` → `preservar_derivado` →
  `derived_artifact id=1`, pai 890, `texto-de-pdf` v1, 4.968 bytes, `derived_at` medido,
  país **lido do pai**. **Retry: `REUSED`**, sem upload novo, sem linha nova, com o byte
  conferido.
- **Um erro meu, e o que ele ensinou.** A primeira execução preservou o RAW e **rebentou no
  RELATÓRIO** (`len()` num inteiro). A produção ficou correta; o relato é que morreu. A
  correção não foi recomeçar — recomeçar criaria uma **segunda** corrida italiana, que a
  autorização não cobre. Foi **retomar só a etapa em falta**, sem segundo `GET`, com os bytes
  vindos do armazém. É a mesma lei do retry que esta casa já tinha escrito.
- **Escritas em produção, por espécie:** DDL 1 · `collection_run` 1 · `raw_asset` 1 ·
  `derived_artifact` 1 · Storage RAW 1 · Storage DERIVED 1. **Nada mais.**
- **Legado intocado:** os 43 derivados históricos e os 195 objetos continuam exatamente como
  estavam. **0 migrados, 0 ligados retroativamente, 0 `raw_asset` falso, 0 corrida inventada.**
- **O verde do mapa é do CANÁRIO**, e diz isso: uma unidade. OCR, outras fontes, outros
  executores e outros países continuam de fora.
- **Próximo passo:** a segunda fonte italiana pelo mesmo caminho, ou OCR para os PDFs sem
  camada de texto. **Uma coisa de cada vez.**

---

### D-039 — A porta de produção está lacrada, e o SHA publicado estava errado

- **Data:** 2026-09-08 · **`PRODUCTION_GATE_SEALED = SIM`** · produção nesta missão: **só
  `SELECT`**
- **A correção factual.** Publiquei `MIGRATION_022 SHA = 7f46ea93…`. **Errado.** Esse é o
  `sha256` do ficheiro **neste disco Windows**, com CRLF; a produção recebeu o **blob do
  Git**, com LF: **`230be77d…`** — que é o que está em `public.schema_migracao`. Medi do lado
  errado da conversão de fim de linha, e o banco tinha o valor certo o tempo todo. Corrigido
  no diário e no recibo, com teste que fixa a referência no **blob**, não no disco.
- **A `022` NÃO foi editada.** Trocar «NAO EXECUTADA» por «executada» mudaria o SHA e faria o
  livro-razão apontar para um ficheiro que nunca correu. **Migration aplicada é artefato
  imutável**; o estado live mora nos docs, no mapa e no ledger.
- **O migrador pulava cego.** `cadeia_canonica.sh` via a versão no livro e dava `SKIP` **sem
  comparar o hash do ficheiro**. Uma migration aplicada e depois editada continuava a ser
  pulada, para sempre. Agora `SKIP` exige `HASH=MATCH`; hash diferente é
  `MIGRATION_APLICADA_MUDOU`, **falha fechada antes de qualquer DDL**, e nenhuma migration
  posterior corre. Reproduzido e provado contra Postgres descartável.
- **A porta one-shot foi APOSENTADA.** O `canario-022` fez o que tinha de fazer e ficou
  pendurado com poder de escrever produção — DDL, corrida, `raw_asset`, derivado, Storage — e
  **disparado por empurrão de código**. E havia um segundo buraco no mesmo sítio: o pré-voo
  corria com `|| true` e o job de aplicar **não recebia o veredito dele** — um portão fechado
  era um aviso, não uma tranca. O workflow e o `canario_forward_it.py` foram **removidos**.
- **O que sobrou tem valor e nenhum poder:** `auditoria-live.yml`, só `SELECT`, com
  `SUPABASE_DB_URL` e nada mais — sem `SUPABASE_SECRET_KEY` e sem `SUPABASE_URL`, que só
  existiam para escrever no Storage.
- **Auditoria live lida (run `34261681486`):** 21 versões no livro, **21 com SHA igual ao
  ficheiro, zero drift**; a `022` byte a byte; **1** corrida `IT-CANARY`, **1** bruto
  italiano, **1** derivado.
- **A contagem corrigida.** A missão anterior disse «seis coisas e nada mais». Faltou uma, e
  não é de domínio: **`DOMAIN_MUTATIONS = 5`** (corrida, `raw_asset`, derivado, 2 objetos no
  Storage) · **`DDL = 1`** · **`MIGRATION_BOOKKEEPING = 1`**, a linha que o aplicador escreveu
  em `public.schema_migracao`. Não é dado de domínio; também não é nada.
- **Um teste apanhou-me a escrever de cabeça.** Listei quatro workflows com poder de escrita;
  são **seis** — `supabase-conexao` e `calendario-regressoes` já tinham a chave antes desta
  missão. Não são portas novas: são portas que eu não tinha visto. A lista passou a ser
  **medida**, não lembrada.
- **Próximo passo:** a **segunda fonte italiana** pelo mesmo caminho forward, sem arquitetura
  nova.


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
| P-010 | **A grafia canônica do desconhecido.** Hoje há cinco no repositório. Proposta a decidir: `UNKNOWN` como valor gravado, `NÃO SEI` como texto de tela, com uma função única de comparação. Escolher agora quebra dado já gravado; escolher tarde faz a migração crescer. | `COL-LAW-035` por inteiro | 2026-09-07 |
| P-011 | **Onde ficam os bytes brutos da Itália?** Hoje: Git (12 MB e crescendo). O bucket `raw` do Supabase existe, é privado e tem round-trip provado. Mover exige decidir o que fazer com o histórico do Git, que não se apaga. | `COL-LAW-303` · `COL-LAW-311` · G-30 | 2026-09-08 |
