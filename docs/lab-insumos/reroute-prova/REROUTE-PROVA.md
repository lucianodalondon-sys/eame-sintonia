# REROUTE-PROVA — ÚTEIS × FALSOS DO REROUTE D56, E O RUÍDO QUE JÁ ENTRA (MISSAO-07 · D129)

SINTONIA LAB · 28/09/2026 10:52–11:35 BRT · só leitura (nada alterado: produção, Sala, ramo, portal, livros).
Triangulação COMPLETA 3/3 (Opus 5.5 + GPT-6 Sol + DeepSeek 4.1 Flash, identidade provada no MANIFEST).
Nenhum rótulo deste estudo é humano: HUMAN_REVIEW = NOT_DONE (D110).

---

## PRIMEIRO, EM PALAVRAS SIMPLES

1. **O reroute não suja a Sala, mas hoje quase não traz nada.** Rodei o reroute sobre tudo o que a coleta trouxe
   sozinha hoje (76 documentos). Ele colocaria só **2 documentos a mais** na Sala: dois textos da CIA, um sobre o
   custo do leite (58 centavos para produzir, 49 pagos) e outro sobre preços e custos na Calábria. **Os 2 são úteis.
   Nenhum falso entrou por ele.** Só que 2 é pouco para dizer «está provado». E os 2 são de **preço** (gaveta T10),
   que o senhor ainda não liberou (a D127 libera só clima e cultura). Em clima e cultura, hoje, ele trouxe **zero**.
2. **O lixo que está entrando hoje NÃO vem do reroute** (ele está desligado). Vem da porta atual da gaveta de
   **ciência (T5)**. Ela aceita qualquer página que tenha duas palavras como «ricerca» e «università», **até no menu
   do site**. Dos 22 itens de ciência que entraram hoje de manhã: **5 são agro de verdade, 8 são duvidosos e 9 não
   têm nada a ver com agro** (poluição do ar, conferência polar, nanotecnologia, radiação no cérebro, ecodesign…).
   Os 9 vêm todos do site da ENEA. Durante o estudo entraram mais 4 do mesmo tipo (Sant'Anna).
3. **O item canário (Xylella, derived:1149) entrou na Sala por acidente:** a régua achou a palavra «tesi» dentro de
   «attesi». A notícia é boa; o motivo gravado é falso.
4. **O que perdemos de bom não é culpa do reroute:** regras da PAC, registro obrigatório de tratamentos, regras da UE
   para granjas, crise da avelã com o clima — param em outras etapas (gaveta de política sem régua, portão que
   desconfia se a página é matéria, páginas cujo corpo o sistema não consegue separar do menu).
5. **O ramo do reroute ainda não obedece a D127**: lá a chave está LIGADA e com 4 gavetas (clima, cultura, pragas,
   preço). Se alguém integrar o ramo como está, passa por cima da decisão do senhor.

**O que o LAB recomenda (o senhor decide):**
- Reroute: pode integrar **só como a D127 manda** (anota tudo; entra só clima e cultura). Risco medido = zero; ganho
  medido hoje = zero. Pragas e preço: o senhor decide se libera (2 de 2 e 3 de 3 certos, lidos por máquina).
- Mais urgente que o reroute: **tirar o lixo da ciência**. O caminho mais simples e reversível: parar de admitir
  automaticamente as 2 rotas da ENEA até a régua de ciência exigir assunto agro. Hoje isso tira os 9 lixos e não
  perde nenhum útil.

---

## 1. ESTUDO A — PRECISÃO DO REROUTE COM MATERIAL NOVO

### 1.1 Replay do autor reproduzido — FATO MEDIDO
- Clone do ramo `origin/nuvem/reroute-fecho-v1` = `origin/claude/reroute-d56-admission-gjuys1` @ `ebde8b876`
  (`git archive`, sem rede, sem Sala, variáveis de Sala removidas). `py provas/reroute_d56/replay_reroute_d56.py`.
- Saída: `REPLAY-REROUTE-D56.json` e `NOVOS-SIM-D56.json` **idênticos byte a byte** aos versionados (fora CRLF).
  Livro 19→25 itens / 19→37 gavetas; acervo 38→40 / 38→51; SIM perdidos 0; 18 novos SIM do livro + 13 do acervo.
- Leitura do autor (`LEITURA-NOVOS-SIM-D56.json`, modelo Claude, VALIDADO_POR_HUMANO = NÃO): T1 7/7, T2 10/10,
  T3 3/3, T4 1/7, T5 1/12 (+4 discutíveis), T7 1/1. **Não há nenhum T10 na leitura do autor.** 8 dos 10 T2 vêm de
  uma só fonte (IT-T2-002, boletins ARPAV quase iguais).

### 1.2 Conjunto novo e independente — FATO MEDIDO
- Sala só leitura (`transaction_read_only = on`): `raw_asset.created_at >= 2026-09-28 03:00+00` → **81 brutos**
  (11:13–13:52 UTC), sha256 recalculado no armazém **81/81 ok**; **76 com texto** (`documento_estruturado`, hash
  76/76); 5 JSON sem derivado (T8 ×4, T12 ×1).
- Fontes: CREA IT-T5-111/113/056/167 (19), ENEA IT-T5-185/186 (26), CIA IT-T7-112/118/123 (11), myfruit IT-T10-018
  (6), zootecnica IT-T10-022 (4), Terra e Vita «Esperto risponde» IT-T12-131 (10).
- Porta do ramo sobre os 76, offline, **pelo mesmo caminho da produção** (`orquestrador.item_documental_para_a_porta`
  com o retrato do detector recalculado dos bytes do RAW → `admissao.decidir_todas(pedido)`); sem `escrever()`, sem
  `pousar()`, sem banco. **Controle: decisão do pedido = a gravada pela produção no livro em 76/76.**
  Script: `scripts/rodar_porta_novos.py` → `PORTA-NOVOS.json`.

### 1.3 O que o reroute faria com os 76 — FATO MEDIDO

| resultado | nº | detalhe |
|---|---|---|
| novos SIM promovidos | **2** | T10: derived:1189, derived:1187 (CIA IT-T7-123, pedido T7 = NÃO) |
| retidos (régua sem medida) | 5 | T5: 1191, 1193, 1192, 1197 (CIA Donne in Campo) · T7: 1198 (Invitalia × Melinda) |
| reroute cego (CORPO_NAO_SEPARAVEL, `corpo()` = 0 caracteres) | **20 (26 %)** | todos os CREA T5-111/113/056 (16) + os 4 zootecnica |
| pararam no portão `materia` antes do reroute | 7 | 1154, 1156, 1158, 1168, 1199, 1200, 1201 |
| T1 / T2 / T3 novos SIM | **0 / 0 / 0** | nenhum boletim nem texto de cultura no fluxo de hoje |
| itens que entrariam SÓ por reroute | **2** | = +2 itens sobre 76 documentos |

### 1.4 Leitura por gaveta (ÚTIL / FALSO / DISCUTÍVEL) — critério fixado antes (`CRITERIO-ROTULO-V1.md`, sha256
`2e5f491f…`); rótulos do LAB gravados ANTES de abrir os motores (`LAB-ROTULOS-V1.json`, sha256 `60f593e6…`)

| gaveta | item | LAB | Opus | GPT | DeepSeek | porquê |
|---|---|---|---|---|---|---|
| T10 (SIM) | 1189 | ÚTIL | ÚTIL | ÚTIL | ÚTIL | «produrre un litro di latte costa fino a 58 centesimi… 49» |
| T10 (SIM) | 1187 | ÚTIL | ÚTIL | ÚTIL | ÚTIL | «prezzi riconosciuti all'origine… prezzo minimo garantito… costi medi Ismea» |
| T5 (retido) | 1191, 1193, 1192, 1197 | FALSO ×4 | FALSO ×4 | FALSO ×4 | FALSO ×4 | convegno/assembleia de associação; «ricerca/università» de passagem |
| T7 (retido) | 1198 | DISC | DISC | ÚTIL | DISC | consórcio de 16 cooperativas, mas o assunto é visita institucional |

Amostra dos NÃO (14 de 49 documentos que não entram por nada), 4 leitores:
falsos negativos claros em todos os 4 = **1199** (avelã: área, produção, «estreme condizioni meteo» → T1/T2; parou no
portão `materia`), **1205** (regras UE para granjas grandes → T4; corpo não separável), **1134** (registro obrigatório de
tratamentos → T4/T12; T12 sem régua), **1140** (sanção PAC por rotação → T12 sem régua). Prováveis: 1195 (selo
biológico Masaf). Os outros 9 estão bem fora ou são discutíveis. **Nenhum dos 4 claros seria recuperado pelo reroute
como ele é hoje** (portão anterior, corpo cego, T4 retido, T12 sem régua). 4/14, Wilson 12–55 %, n pequeno.

### 1.5 Precisão com intervalo (Wilson 95 %)

| conjunto | úteis/lidos | intervalo | observação |
|---|---|---|---|
| T1 (autor) | 7/7 | 65–100 % | só livro antigo; 0 caso novo hoje |
| T2 (autor) | 10/10 | 72–100 % | 8 da mesma fonte (ARPAV); 0 caso novo hoje |
| T3 (autor) | 3/3 | 44–100 % | 0 caso novo hoje |
| T10 (LAB, novo) | 2/2 | 34–100 % | mesma fonte (CIA T7-123); autor não tem T10 |
| **tudo o que o ramo promove** (autor+LAB) | **22/22** | **85–100 %** | rótulo de modelo; casos quase repetidos |
| T4 (autor) | 1/7 | 3–51 % | — |
| T5 (autor + LAB) | 1/16 | 1–28 % | os 4 de hoje: 0/4 |

### 1.6 VEREDITO POR GAVETA (critério D, a Sala não vira lixo)

| gaveta | veredito | n que sustenta | por quê |
|---|---|---|---|
| **T1** cultura | **MEDIR MAIS** (pode ficar ligada como a D127 manda) | 7 (autor) + 0 novo | nenhum falso em lugar nenhum, mas nenhum caso independente hoje |
| **T2** clima | **MEDIR MAIS** (idem) | 10 (autor, 8 da mesma fonte) + 0 novo | idem |
| **T3** pragas | **PRONTO PARA PROPOR** (escopo = dono) | 3 + 0 novo | 3/3; HIPÓTESE: quando o corpo dos CREA for separável, virá o 1.º falso (1144, nomeação de diretores cujos currículos citam «peronospora, oidio») |
| **T10** preço | **PRONTO PARA PROPOR** (escopo = dono) | 2 novos | 2/2, 0 falso; mesma fonte; fora da D127 |
| **T4** regulatório | **NÃO LIGAR** | 7 | 1/7 |
| **T5** ciência | **NÃO LIGAR** | 16 | 1/16; os 4 de hoje falsos |
| **T7** rede técnica | **MEDIR MAIS** | 1 | 1 discutível; falta definição da régua |
| **T9** concorrentes | **MEDIR MAIS** | 0 | nenhum caso |

**Resposta às duas provas da D129 (material de hoje):** ÚTEIS que passam a entrar = **2** (T10); FALSOS junto = **0**.
Dentro do escopo que o dono autorizou (T1/T2): **+0 úteis, +0 falsos**. O reroute **não transforma a Sala em lixo**
(22/22 no que promove, modelo); mas o **ganho real hoje é pequeno (+2/76)** e ele é **cego em 26 %** do fluxo.

---

## 2. ESTUDO B — O RUÍDO QUE JÁ ENTRA SEM REROUTE (T5)

### 2.1 Os 22 itens T5 pousados em 28/09 (08:22–08:31 BRT) — leitura (modelo, 4 leitores independentes)

| fonte | itens | ÚTIL-AGRO | DISCUTÍVEL | NÃO-AGRO | GAVETA T5 correta (ciência com resultado) |
|---|---|---|---|---|---|
| CREA (T5-111/113/056) | 10 (9 textos: 1146 = 1160, mesmo hash) | 5 (LAB) · 4–6 (motores) | 5 | **0** | ÚTIL 4 · DISC 2 · FALSO 4 (LAB) |
| ENEA (T5-185/186) | 12 | **0** | 3 (LAB) · 2–3 | **9 (LAB) · 9–10 (motores)** | **FALSO 12/12** (os 4 leitores) |
| **total** | **22** | **5** (Wilson 10–43 %) | 8 | **9** (Wilson 23–61 %) | ÚTIL 4/22 (7–39 %) |

NÃO-AGRO (ENEA): 1174 FAIRMODE qualidade do ar · 1166 ecodesign · 1163 conferência polar · 1179 qualidade do ar ·
1161 radiação/meduloblastoma · 1162 biomedicina espacial · 1181 ICOS carbono ar-mar · 1185 NanoInnovation ·
1183 webinar ecodesign. DISCUTÍVEIS ENEA: 1167 viveiro florestal · 1178 Research Week UniBa · 1172 INNOVA EXPO.
ÚTEIS (CREA): 1149 Xylella/oliveira · 1148 Macfrut · 1145 sementes biológicas · 1152 acarologia/defesa de culturas ·
1142 cochonilha do pinheiro (DISCUTÍVEL para Opus/GPT: hospedeiro florestal). Os 3 T10 de hoje (zootecnica 1206,
1207, 1204) = ÚTIL-AGRO nos 4 leitores. Tabela completa por item: `LAB-ROTULOS-V1.json` e `triangulacao/`.

Coordenador tinha estimado ~8 agro / ~14 não-agro. Medido: **5 agro + 8 duvidosos + 9 não-agro**. A ordem de grandeza
se confirma; o número exato depende dos 8 duvidosos (decisão de régua do dono).

### 2.2 A regra que deixou entrar os não-agro — FATO MEDIDO (arquivo:linha)
Produção `origin/servico-20260923-0923` @ `e24139702` = disco do vivo (conteúdo comparado: igual), `admissao/admissao.py`:
- **:1559** `decidir()` chama `_do_universo(item, universo, PERGUNTAS_DO_UNIVERSO…)` para o pedido;
- **:861–862** o texto julgado é o **item inteiro** (`texto`, `title`…) — **menu, cabeçalho e rodapé incluídos**;
- **:876** T5 não está em `PALAVRA_INTEIRA` (:793) → `achadas = [p for p in palavras if _dobrar(p) in texto]` = **substring**;
- **:932–934** `if len(achadas) >= SINAIS_MINIMOS: return SIM` com `SINAIS_MINIMOS = 2` (:768);
- **:1015–1021** a lista T5: `ricerca, universita, istituto, convegno, studio, rivista, articolo, tesi, revista…`
  — **nenhuma exige assunto agro**.
- Medido nos 22 (`scripts/onde_casou.py`): **12/12 ENEA** casam «ricerca» no menu («Infrastrutture di ricerca»);
  **1149** entrou por `tesi` ⊂ «at**tesi**» (+ricerca); **1145** por `revista` ⊂ «p**revista**»; 1151 tinha `tesi` ⊂
  «ipo**tesi**/sin**tesi**» mas outras 3 palavras reais.
- Contrato da fonte: `curadoria/italy_contracts_curator.json` FONTES[695]/[696] — IT-T5-185/186 «ENEA —
  Dipartimento Sostenibilità (SSPT)», TERRITORY T5. A rota foi cadastrada como ciência; o departamento é de
  sustentabilidade em geral.
- Continua entrando: às 11:06 BRT pousaram 4 IT-T5-025 (Sant'Anna); pelo título, 3 parecem não-agro (Fitto com
  estudantes, sócios dos Lincei, Internet Festival) e 1 agro (INNOFLORENERG floricultura) — leitura rápida, fora da
  amostra rotulada. Sala hoje: 30 itens (medido 11:18 BRT).

### 2.3 Isso muda o veredito do reroute?
**Não muda o veredito, muda a prioridade.** O reroute segurou 4/4 falsos de T5, e a régua dele (corpo + início de
palavra) teria recusado 2 dos 12 ENEA. O lixo vem do **pedido**. A condição da D129 «sem transformar a Sala em lixo»
**já está sendo violada pela porta atual**: ~41 % dos T5 de hoje não são agro. Consertar T5 tira ~9 lixos por dia;
ligar o reroute acrescenta ~2 úteis.

### 2.4 Menor correção do ruído T5 — divergência dos motores decidida por medição (`scripts/confronto_t5.py`)

| proposta | de quem | nos 22 de hoje: fica | perde ÚTIL? | fora de hoje (Sala T5 inteira, 180) | veredito LAB |
|---|---|---|---|---|---|
| C2: pedido T5 julgado só no corpo | DeepSeek | 10 (**7 NÃO-AGRO** + 3 DISC) | **perde os 5** (CREA sem corpo) | — | **REJEITAR** (mata o útil, mantém o lixo) |
| C1: T5 exige +1 termo de praga (T3) ou cultura (T1) | Opus | 8 (5 ÚTIL + 3 DISC), **0 NÃO-AGRO** | 0 | EU-T5-001 (artigos em inglês) 98/100 ficam; IT antes 15/54 ficam — sai agro sem cultura/praga nomeada (ex.: derived:57 escola de verão «sistemi zootecnici», derived:58 «Produzioni Vegetali»); 1146 só passa por «mele» | **TESTAR** (com gabarito; tem falso negativo medido) |
| C3: conter as rotas ENEA IT-T5-185/186 até provar assunto agro | GPT | 10 (5 ÚTIL + 5 DISC CREA), **0 NÃO-AGRO** | 0 | os 5 ENEA de antes na Sala: 0 termo de praga/cultura | **PRONTO PARA PROPOR** (reversível, sem código; dono = Collection/curadoria) |

---

## 3. FATO MEDIDO · INFERÊNCIA · HIPÓTESE · NÃO SEI

**FATO MEDIDO** (comandos e scripts em `scripts/`, saídas nesta pasta)
- F1 Replay do autor reproduzido idêntico.
- F2 76/76 decisões do pedido reproduzidas iguais à produção (controle do método).
- F3 Reroute sobre o fluxo de hoje: +2 itens (T10), 2/2 úteis nos 4 leitores, 0 falso; T1/T2/T3 = 0.
- F4 Reroute cego em 20/76 (CREA, zootecnica: `corpo()` = 0 caracteres).
- F5 22 T5 de hoje: 9 NÃO-AGRO (ENEA), 12/12 ENEA FALSO para T5 nos 4 leitores; regra = admissao.py:861–862, 876,
  932–934, lista 1015–1021 (e24139702).
- F6 Canário 1149 admitido por `tesi` ⊂ «attesi».
- F7 Ramo ebde8b876 mantém `REROUTE_ENTRA_NA_SALA = True` e `REROUTE_PROMOVE = {T1,T2,T3,T10}` — **D127 não aplicada
  no ramo** (a D127 registra «volta a False, gavetas {T1,T2}»).
- F8 `sala_de_espera_gaveta` = 0 linhas (nada entrou por reroute).
- F9 C2 perde os 5 úteis e mantém 7 não-agro; C1 e C3 tiram os 9 não-agro sem perder úteis hoje; C1 derruba 39/54
  T5 italianos anteriores, entre eles agro sem cultura/praga nomeada.

**INFERÊNCIA**
- I1 O reroute, como está, não é a causa do lixo e não o aumentaria (0 falso no que promove, em 22 casos).
- I2 O ganho do reroute depende de boletins/cultura no fluxo; num dia sem boletins ele quase não rende.
- I3 Integrar o ramo sem aplicar a D127 promoveria T3/T10 sem decisão do dono.

**HIPÓTESE (precisa de teste)**
- H1 Consertar a separação do corpo nos CREA traria úteis (T3 em 1142, 1149) e o 1.º falso de T3 (1144). Medido só
  num corte manual, não no extrator.
- H2 C1 com a régua na língua do texto é a correção durável; precisa de gabarito para não perder ciência agro sem
  cultura/praga nomeada.

**NÃO SEI**
- N1 Precisão real com olho humano (nenhum rótulo é humano).
- N2 Como T1/T2 se comportam em fluxo novo com boletins (0 caso hoje).
- N3 Se o T2 do pedido também deixa passar não-agro: às 11:00 BRT pousou derived:1224 (IT-T2-006, algas no mar em
  Licola) — um caso, não medido.
- N4 Se a Intelligence já foi afetada pelos não-agro (o motor de 10:48 leu o delta de 22 itens; não medi os objetos).

---

## 4. DECISÕES DO DONO (escolha concreta · consequência · recomendação)

1. **Escopo do reroute** — (a) só T1/T2, como a D127: ganho hoje 0, risco 0; (b) T1/T2/T3/T10: ganho hoje +2 úteis,
   0 falso (n pequeno, lido por máquina). **Recomendação: (a) agora**; (b) quando houver mais casos independentes.
2. **Rotas ENEA IT-T5-185/186** — conter a admissão automática até a régua de ciência exigir assunto agro?
   Consequência: tira ~9 lixos/dia medidos hoje; pode perder agro futuro da ENEA. **Recomendação: SIM, reversível.**
3. (opcional) **10 casos em sim/não para o senhor** (os 2 T10, 4 CREA, 4 ENEA) — é a única forma de ter prova humana.

## 5. PEDIDOS INTERNOS (o LAB não executa)

- **Equipe nuvem-reroute / coordenador** — aplicar a D127 no ramo (`REROUTE_ENTRA_NA_SALA = False` ou gavetas {T1,T2}) e
  o teste que prende isso, ANTES de qualquer integração. BLOQUEIA a integração: SIM. Destrava: grep da chave no ramo.
- **Collection/curadoria (dono do contrato da fonte)** — decisão 2 acima. BLOQUEIA o canário: NÃO.
- **Dono da porta (Admission)** — replay offline de C1 (régua na língua do texto) sobre os 76 de hoje + os 180 T5 da Sala;
  sucesso = 5 úteis de hoje ficam, ≥ 9 não-agro saem, e a lista do que sai fora de hoje é lida. BLOQUEIA: NÃO.
- **Extração (texto de HTML)** — `leis/fato_do_texto.corpo()` devolve 0 caracteres nas páginas CREA e zootecnica
  (20/76). BLOQUEIA o reroute nessas fontes: SIM.
- **Canário 1149** — qualquer rejulgamento do pedido T5 com «início de palavra» o reprovaria (fica só «ricerca»).
  Quem reprocessar o 1149 (nuvem-canario-1149-v1) precisa saber. BLOQUEIA o canário: NÃO, se ninguém rejulgar a pertença.

## 6. TRIANGULAÇÃO E CUSTO
STUDY-20260928T111040-741362 · COMPLETA · 3/3 · 0 sessões alheias. Opus 411 s, 227.277 tokens (custo NÃO SEI);
GPT-6 Sol 245 s, 314.656 tokens (incluído na assinatura); DeepSeek 107 s, 184.679 tokens, US$ 0,0064 (sem 402).
Confronto e divergências decididas por medição: `CONFRONTO.md`. Nada foi recarregado.

## 7. CONTENT_CLASSIFICATION (D109)
KNOW_HOW = YES · ITALIAN_AGRO_BRAIN = NO · BIBLE_CHANGE = NO · HANDOFF_ONLY = NO
- Know-how (candidato, o LAB não escreve): T5 do pedido casa substring no texto inteiro (menu) → lixo de sites de
  pesquisa geral; `corpo()` = 0 em CREA/zootecnica cega o reroute; canário admitido por acidente de substring; o ramo
  não aplicava a D127; «0 falsos» num dia sem casos não é prova.
- Bíblia — candidatas (só se o dono decidir): «régua de ciência exige assunto agro»; «reroute julga o corpo».
- Handoff: Sala 30 itens hoje (11:18 BRT); ramo reroute com D127 não aplicada.

## ARQUIVOS
`REROUTE-PROVA.md` (este) · `RASCUNHO-45MIN.md` · `CRITERIO-ROTULO-V1.md` · `LAB-ROTULOS-V1.json` · `PACOTE.md` ·
`triangulacao/` (3 respostas + MANIFEST) · `CONFRONTO.md` · `CONFRONTO-T5-MEDIDO.json` · `PORTA-NOVOS.json` ·
`CONTRAFACTUAL.json` · `ONDE-CASOU-T5.json` · `scripts/`. Cópia de trabalho do ramo e export da Sala ficam fora do LAB
(`%LOCALAPPDATA%/Temp/lab-reroute-prova/`).

## EM PALAVRAS SIMPLES
O reroute passou no teste «não suja a Sala»: hoje ele traria 2 notícias boas, de preço do leite e custos, e nenhuma
ruim. Mas ainda não passou no teste «vale a pena»: nas gavetas que o senhor liberou (clima e cultura), hoje ele trouxe
zero, e ele não consegue ler um quarto das páginas. A sujeira que está entrando agora vem da porta de ciência, que
aceita qualquer página com «pesquisa» e «universidade», até no menu. Por isso 9 das 22 notícias de ciência de hoje não
são de agro. O mais simples e reversível é parar de admitir sozinhas as 2 rotas da ENEA até a porta de ciência exigir
assunto agro. Integrar o reroute pode esperar e, quando entrar, deve entrar como o senhor mandou (só clima e cultura).
Tudo isto foi lido por máquina, não por gente. A decisão é do senhor.
