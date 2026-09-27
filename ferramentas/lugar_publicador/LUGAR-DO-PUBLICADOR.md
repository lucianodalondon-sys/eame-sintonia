# LUGAR-DO-PUBLICADOR — onde fica quem publica, do contrato até a Sala — 26/09/2026

Ramo `lugar-do-publicador-v1`, a partir do vivo **`2ef6fef8`** (antes 554c1ec1; ff, só o mapa declarado mudou) + `sede-37-v1` (`9fdcc799`, juntada aqui).
**NÃO instalado. Rede: 0. Mapa: não regerado** (peça `C-LUGAR-PUBLICADOR` declarada). Sala real e vivo **só
lidos**; a escrita foi ensaiada em **cópias** (livros do vivo copiados + Sala copiada para um Postgres descartável,
depois apagado), sob a LOCK-PESADO (22:39–22:43, FILA-PESADO 5.º; passada à SALA-LEITURA-D9-D10).

## EM PALAVRAS SIMPLES

Cada linha da Sala devia dizer **onde fica quem publicou** (a sede). Hoje diz isso em **5 de 104** linhas. A sede de
muitas fontes **já estava provada** no rodapé das páginas que guardámos — só não chegava à Sala. Fiz o caminho:
a sede provada vai para o contrato da fonte e, do contrato, para a Sala, como uma correção guardada à parte (a
linha original nunca muda). Numa cópia da Sala: **de 5 para 60 linhas com sede (de 104), de 3 para 16 fontes.**
Nenhum outro campo mudou. As 44 que sobram ficam "não sei": ou não guardámos nenhuma página delas (quase todas
PDFs de universidades), ou a página não mostra a sede com segurança.

## 1 · Medida sem rede: quantas fontes da Sala já têm sede provada

- Sala real (só leitura, pela vista `sala_de_espera_atual`): **104 linhas, 46 fontes**; com sede **5** (IT-T3-002
  Napoli ×2, IT-T3-008 Bari ×2, IT-T3-010 Lecce — contratos à mão). Na 1.ª medida (10:40) eram 94 linhas / 43 fontes.
- `achar_paginas_de_sede.py --alvo` (novo: aceita a lista de fontes da Sala) sobre as 43: **12 fontes com sede
  provada na própria página**, cobrindo 50 linhas; mais **IT-T7-103** (Roma, provada pela SEDE-37), que chegou
  depois → **13 fontes, 55 linhas** a ganhar.
- **Lidas à mão (`medida/PROVAS-LIDAS.json`): as 12 são o rodapé da própria organização** — ex.: «NCX Drahorad srl
  Via Prov.le Sassuolo Vignola 315/1 41057 Spilamberto (MO)» (Myfruit); «CREA … Sede principale Via della Navicella
  2/4, 00184 Roma»; «CNR IBBA … Sede centrale: Via Alfonso Corti 12, 20133 Milano»; «CASALASCO SOCIETÀ AGRICOLA
  S.p.A. … 26036 RIVAROLO DEL RE (CR)».
- **Recusadas, e bem:** IT-T7-033 Chianti (Milano = local de um evento) · IT-T7-041 Bonifica Romagna (só sedes
  operativas Ravenna/Forlì, a legal não aparece — D83: conta a legal) · IT-T5-015 CNR IBBR Bari e IT-T5-039 Portici
  (rodapé certo, mas numa página só e sem «sede» ao lado: a regra não aceita; ficam NAO SEI).
- Das 43 fontes medidas às 10:40: **16 sem nenhuma página HTML guardada** (3 são as T3 que já têm sede pelo
  contrato; 13 são T5 de universidades e arquivos, cujos itens são PDF) e **15 com páginas mas sem sede segura**
  (IT-T2-034, IT-T5-015, IT-T5-024, IT-T5-033, IT-T5-034/035/036 Georgofili, IT-T5-039, IT-T5-090 ISTAT,
  IT-T7-013, IT-T7-033, IT-T7-041, IT-T9-009, IT-T9-011, IT-T9-021).

## 2 · D83 aplicada (bot Luciano, 06:39)

1. **Sede LEGAL:** IT-T10-021 Image Line = **Roma**; «sede operacional: Faenza» fica escrito na BASE, não noutro
   campo. Sai de «PENDENTE_DO_DONO» (não está na Sala; vale para as coletas novas).
2. **Cidade fora da lista → província:** a tabela declarada de siglas cresce **só** com as que a Sala pediu: **PD**
   (Legnaro → Padova), **CR** (Rivarolo del Re → Cremona), **NA** (Portici → Napoli; ainda não usada — a prova de
   Portici é fraca). O texto original fica na regra («Padova (sede: Legnaro PD, …)»). Testado: toda sigla da tabela
   aponta para uma província do gazetteer.
3. **Edagricole:** nenhuma das 14 revistas está na Sala; nada muda aqui.
4. **Rota da MICRO-SEDE:** só plano (abaixo); 0 pedidos.

## 3 · O que mudou no código

- `curadoria/sede_da_fonte.py`: +3 siglas (D83.2).
- `ferramentas/sede37/escrever_sede.py`:
  - **fontes fora do Curator mas com linha na tabela do coletor** (as universidades da Sala) — antes eram
    **SALTADAS**; agora escreve-se só a `SOURCE_LOCATION_RULE` da tabela (é o contrato que a Sala lê);
  - D83.1;
  - **só escreve se reescrever o livro igual byte a byte** (forma medida: recuo 1, CRLF, sem ASCII forçado; os dois
    livros do vivo passam).
- `ferramentas/sede37/achar_paginas_de_sede.py`: `--alvo`; e a **trava de plataforma da TRAVA-SEDE-V2**
  (`leis/lugar_da_organizacao.e_plataforma`: conta YouTube/Instagram… não herda o «contatti» do host) — 0 casos
  nas fontes da Sala, nada muda hoje.
- **Nova porta da Sala** `ferramentas/lugar_publicador/preencher_sede_na_sala.py`: SOURCE_LOCATION pela **mesma
  função da produção** (`contratos_de_fonte.lugar_da_fonte`); escreve **só** `source_location` e a
  `completude_tempo_lugar` (só a chave LOCAL_DA_FONTE muda, PROVADAS recontada), por `sala_de_espera.rever`
  (append-only); nunca pisa uma sede que existe; NAO SEI nunca entra; mostra por omissão.
  **Porque não o `reprocessar_tempo_lugar.py`:** ele refaz os quatro campos com o código do dia e mexeria na
  publicação e no facto, fora desta missão.

## 4 · Testes e mutação

`tests/test_lugar_do_publicador.py` **13/13** (rodapés reais; a corrida inteira pelo envelope real
`{RUN_ID, ITENS}` de `ler_atual`) · existentes, iguais: `test_sede_da_fonte` 12 · `test_escrever_sede` 6 ·
`test_micro_sede` 7 · `test_onboardar_rotas_provadas` 29 · `test_soc_tempo_publicacao_e_lugar` 14 ·
`test_tempo_e_lugar_atravessa` 43 · `test_extrator_lugar_v2` 20. **Mutação 9/9** (`medida/MUTACAO.json`).
Erro meu apanhado antes do ensaio: a porta lia `ler_atual` como lista (é um envelope) — corrigido, testado (M9).

## 5 · Ensaio (cópias; `ensaio_sede_na_sala.sh`, saída em `medida/ensaio/`)

| passo | resultado |
|---|---|
| livros do vivo copiados (sha256 em `1-LIVROS-DO-VIVO.sha256`) | escrever SEDE-37: **APLICA 28** → 2.ª **JA_APLICADA 28**; escrever Sala: **APLICA 5 · JA_APLICADA 7** → 2.ª **JA_APLICADA 12** |
| o que mudou nos livros (contra a cópia do vivo, não o Git) | Curator: **32 fontes, só os 4 campos da sede** · tabela: **33 fontes, só `SOURCE_LOCATION_RULE`** · `CONTRACTS` do .mjs carrega (240) |
| cópia da Sala (pg_dump só-leitura → Postgres descartável 54393) | **104 linhas**, restauro sem erro |
| porta da sede: mostrar | GANHAM 55 · JÁ TINHAM 5 · FICAM NAO SEI 44 |
| aplicar | **110 revisões** (55 × sede + completude) |
| 2.ª passagem | **0** novas (60 JÁ TINHAM) |
| outros campos, linha a linha | publicação **0** · data do facto **0** · lugar do facto **0** mudaram → **PASS** |
| sede depois | **60 de 104 linhas, 16 fontes**: Modena 24 · Roma 10 · Cremona 6 · Catania 4 · Milano 3 · Udine/Napoli/Padova/Pisa/Bari/Teramo 2 · Lecce 1 · NAO SEI 44 |

⚠️ Lição: a 1.ª corrida do ensaio mostrou «22 mil linhas diferentes» no livro do Curator e pensei que a porta
reformatava o livro. **Era falso:** o guião comparava com o Git, e os livros vivos já diferem do Git. Corrigido
(compara com a cópia do vivo) e a porta ganhou a guarda de forma.

## 6 · MICRO-SEDE para o resto (só plano, `medida/MICRO-SEDE-SALA-PLANO.json`)

12 domínios, 24 pedidos, máx. 2 por domínio. **Tirar antes de correr:** `cnr.it` (fora por regra da coordenação; e a
página escolhida é a do IBBA, **outro instituto**) · IT-T5-016 AIR UNIMI e IT-T5-019 IRIS UNIPD (a página escolhida
é a de um **departamento**, não a do arquivo). Ficam **9 domínios, 18 pedidos** — só com ordem, portão IT e D38.

## 7 · Plano de instalação (coordenador; um escritor; robô parado nos passos 4–5)

1. `git -C $VIVO rev-parse --short HEAD` = **2ef6fef8**; backup dos livros sujos (sha256) + `HEAD-ANTES`.
2. `git diff --name-only HEAD <SHA> -- $LIVROS | wc -l` → 0; `git merge --ff-only <SHA>`; livros iguais.
3. Testes do §4.
4. **Livros (robô parado):** `escrever_sede.py --paginas ferramentas/sede37/PAGINAS-DE-SEDE.json --contratos
   curadoria/italy_contracts_curator.json --tabela regras/italy_contracts_onboarded.json` → conferir **APLICA 28**
   → `--aplicar`; o mesmo com `--paginas ferramentas/lugar_publicador/medida/PAGINAS-DE-SEDE-SALA.json` → **APLICA
   5** → `--aplicar`; 2.ª passagem só JA_APLICADA.
5. Religar o robô (as coletas novas dessas fontes já saem com sede).
6. **Sala (decisão do coordenador):** `SINTONIA_SALA_BACKEND=POSTGRES SINTONIA_SALA_DSN=… SINTONIA_PSQL_EXE=…
   py ferramentas/lugar_publicador/preencher_sede_na_sala.py` (mostrar: **GANHAM 55**) → `--aplicar` → 2.ª
   passagem 0.
7. Mapa pela INTEGRA (lote).

⚠️ O ensaio foi feito sobre a Sala de 26/09 22:42 (104 linhas). O coordenador reprocessou a Sala a 27/09 (~11:00):
o passo 6 mostra primeiro, e os números podem mudar (linhas novas; e se o reprocesso já tiver escrito a sede, a porta
diz JA_TINHAM e não repete).

**DESFAZER:** livros — repor do backup; Sala — as revisões são append-only e identificadas por
`extrator = ferramentas/lugar_publicador/preencher_sede_na_sala.py …` (não se apagam; uma revisão nova volta a
NAO SEI se for preciso); código — `git reset --keep <HEAD-ANTES>`.

## 8 · Decisões / atenção

1. **CNR IBBA, CREA, ENEA:** a sede é a do **instituto/centro** que publica (Milano; Roma) — num instituto do CNR a
   sede legal da entidade (CNR) seria Roma. Li a D83.1 como «legal do publicador, não da operação»; se o dono quiser
   a do ente-mãe, muda só IT-T5-160 (Milano → Roma).
2. As 44 linhas que ficam NAO SEI: quase todas pedem a MICRO-SEDE (§6) ou uma página guardada.
