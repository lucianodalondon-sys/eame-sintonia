# SEDE DAS FONTES — onde está quem publica, para as 60 da coorte da 3.ª onda (só relatório)

- **Ramo:** `sede-fontes-v1`, a partir do vivo `e5cd691f`.
- **Rede: 0 pedidos.**
- **Nenhum contrato foi escrito.** Lidos só em modo leitura: o armazém do vivo, os índices D40 guardados
  e o livro do Curator.

**Porquê este trabalho.** A MICRO-VERIFICAÇÃO mostrou que **nenhuma das 28 fontes da coorte congelada
declara a sede no contrato**. Por isso `source_location` sai `NAO SEI` em todos os itens. Para as 60 é igual:
`SOURCE_LOCATION` está vazio no livro do Curator nas 60.

As 60 = as 40 da coorte provisória da 3.ª onda + as 20 que só esperam a RECEITA-T8 (`COORTE-60.json`).
⚠️ Esta composição é leitura minha.

## 1 · O resultado: 23 de 60 com sede provável, 37 NAO SEI

| | Fontes |
|---|---|
| **Sede provada numa página guardada da própria fonte** | **14** |
| Sede pelo **mesmo site** de uma fonte provada (mesmo host) | 9 |
| **NAO SEI** | **37**: 32 sem nenhuma página guardada nesta máquina; 5 com páginas, mas sem prova bastante |

**Regra da prova** (`medir_sede.py`, escrita antes de ler os trechos):
- conta uma **morada italiana** na página: CEP de 5 dígitos + comune + (SIGLA);
- o comune tem de ter a sigla entre parêntesis, ou estar no gazetteer;
- a morada tem de aparecer em **≥ 2 páginas** (o rodapé repete-se) **ou** junto de «sede / indirizzo / contatti»;
- **nunca** conta o `REGION` do Atlas (é cobertura ou amostra, não morada), nem o nome da instituição.

Depois **li os 14 trechos à mão**: todos são o rodapé da própria organização.

### As 14 com prova na própria página

| Fonte | Organização | Sede | O contrato devolveria | Trecho (rodapé guardado) |
|---|---|---|---|---|
| IT-T10-018 | myfruit (editora NCX Drahorad srl) | Spilamberto (MO) | **Modena** (província) | «NCX Drahorad srl Via Prov.le Sassuolo Vignola 315/1 41057 Spilamberto (MO)» — 57 páginas |
| IT-T10-021 | Plantgest / Image Line | Roma (**sede legal**) | Roma | «Sede legale via Giovanni Nicotera 29 00195 Roma · Sede operativa via Gallo Marcucci 23-24 48018» (Faenza) ⚠️ |
| IT-T2-032 | ARPA Liguria | Genova | Genova | «ARPAL - Via Bombrini 8 - 16149 Genova» |
| IT-T2-037 | ARPAT Toscana | Firenze | Firenze | «Contatti Via del Ponte alle Mosse, 211 - 50144 Firenze» |
| IT-T2-051 | Arpae Emilia-Romagna | Bologna | Bologna | «DIREZIONE GENERALE Via Po, 5 – 40139 Bologna» |
| IT-T5-160 | CNR-IBBA | Milano | Milano | «Sede centrale: Via Alfonso Corti nr. 12, 20133 Milano» |
| IT-T5-167 | CREA | Roma | Roma | «Sede principale Via della Navicella 2/4, 00184 Roma» |
| IT-T5-185 | ENEA — Dip. SSPT | Roma (RM) | Roma | «C.R. ENEA Casaccia - Via Anguillarese 301, 00123 Roma (RM)» (sede do departamento) |
| IT-T7-017 | Riunite & CIV | Campegine (RE) | **Reggio nell'Emilia** (província) | «VIA BRODOLINI, 24 - 42040 CAMPEGINE (RE)» — 41 páginas |
| IT-T7-021 | Consorzio Est Ticino Villoresi | Milano | Milano | «Direzione centrale - Milano Via Lodovico Ariosto, 30 - 20145 Milano» |
| IT-T7-042 | Consorzio Aceto Balsamico di Modena | Modena | Modena | «Contatti Via Ganaceto, 113 – 41121 Modena» |
| IT-T7-043 | Agrofarma — Federchimica | Milano | Milano | «SEDE Via Giovanni da Procida, 11 20149 - MILANO» |
| IT-T7-112 | CIA — AGIA | Roma | Roma | «CIA - Agricoltori Italiani Via Mariano Fortuny, 20 - 00196 Roma» |
| IT-T7-117 | CAF CIA | Roma | Roma | «Lungotevere Michelangelo, 9 - 00192 Roma» |

**Pelo mesmo site (9):**
- CREA IT-T5-056, IT-T5-111, IT-T5-113 → Roma, como a IT-T5-167.
- ENEA IT-T5-186, IT-T5-187 → Roma, como a IT-T5-185.
- CIA IT-T7-118, IT-T7-121, IT-T7-123, IT-T7-135 → Roma, como a IT-T7-112. A 121 e a 135 mostram a
  mesma morada numa página própria.

A base é mais fraca (o mesmo host), e fica dita como `MESMO_SITE de <SID>`.

**Casos lidos à mão:**
- **Image Line tem duas sedes:** a legal em Roma e a operacional em Faenza (RA). Qual conta é decisão do dono.
- **CIA Toscana (IT-T7-141):** o rodapé diz «Via di Novoli 91/N – 50127 Firenze», mas numa só página
  guardada. Fica `NAO SEI` pela regra, como candidata forte.
- **Chianti Classico (IT-T7-033):** a única morada achada é o **local de um evento** (The Westin Palace
  Milan). A regra recusou-a, e bem: morada de evento não é sede.
- **Precisão:** Spilamberto e Campegine não estão no gazetteer (ele tem 20 regiões + 85 províncias,
  nenhum comune). O contrato devolveria a **província** (Modena, Reggio nell'Emilia), com precisão
  `PROVINCE`. É verdade, mas menos precisa do que a morada.

### As 37 NAO SEI
- **32 não têm nenhuma página guardada nesta máquina.** São sobretudo as 20 T8/T12/T9, que o coletor
  nunca colheu, e várias T7.
- **Para as fechar é preciso 1 pedido à página «contatti» / «chi siamo» de cada site** (rede, teto D38):
  - são 22 domínios registáveis;
  - **14 das 37 são da Edagricole** (terraevita e revistas `*.edagricole.it`, a mesma editora). Uma página
    de contactos provavelmente prova as 14, se o rodapé o confirmar.
- **Pistas sem prova, só para orientar essa missão.** O cadastro-mestre
  (`candidatas/ITALY-SOURCE-MASTER-V1.json`) dá:
  - ARPAV (IT-T2-145/146) → **Padova**;
  - Regione Siciliana (IT-T12-129) → **Palermo**.
  - O cadastro **não guarda prova por linha**, por isso não conta como prova.

## 2 · Como escrever pelo caminho canónico (proposta; nada foi escrito)

**O que já existe e funciona:**
- `regras/italy_contracts.mjs` já lê `linha.SOURCE_LOCATION_RULE` da tabela `regras/italy_contracts_onboarded.json`
  (hoje, por omissão, `"NAO SEI"`).
- `regras/contratos_de_fonte.lugar_declarado_pela_fonte()` confere o texto contra o gazetteer, e
  `lugar_da_fonte()` põe-no no item com `BASE = CONTRATO`.
- Os 15 contratos escritos à mão já usam o formato `"<nome> (<aparte>) — fixo"`.

**O que falta (o fio):**
- `curadoria/onboardar_rotas_provadas.linha_da_tabela()` só copia `OWNER`, `NAME`, `TERRITORY`, `BATCH_ID`,
  `OUTPUT_TYPE` e `ACQUISITION`.
- O Curator também **não tem** a sede nas 60.

**Proposta, com um dono só:**
1. **O dono é o contrato do Curator** (`curadoria/italy_contracts_curator.json`), como já é da aquisição e
   do `DOCUMENT_ID_RULE`.
   - Usar os **três campos que a lei social já lê do mesmo livro** (`leis/lugar_da_organizacao.do_contrato`):
     `SOURCE_LOCATION` (o nome do gazetteer), `SOURCE_LOCATION_BASIS` (a prova: página, sha256 do bruto,
     trecho, data) e `SOURCE_LOCATION_PRECISION`.
   - Assim, web e social ficam com **uma** convenção no **mesmo** livro, e não com duas.
2. **A ponte leva-os:**
   - `linha_da_tabela()` passa a escrever `SOURCE_LOCATION_RULE = "<SOURCE_LOCATION> (<base curta>) — fixo"`.
     É o formato de `PROPOSTA-SOURCE-LOCATION-RULE-V1.json`, **sem parêntesis dentro do aparte**: o leitor
     do contrato corta no primeiro «)». Medido aqui: 9 propostas davam `NOT_IN_GAZETTEER` antes de eu o
     corrigir.
   - As linhas que **já estão** na tabela recebem-no por **um preenchimento único**, com o bot parado. É o
     mesmo molde da instalação do `entrada_final`: a tabela é da lane do bot, um só escritor, cópia de
     segurança e desfazer.
3. **Não é preciso voltar a provar as rotas.** `curadoria/sha_do_contrato.do_contrato()` só cobre
   `SOURCE_ID`, `OUTPUT_TYPE` e `ACQUISITION`. Pôr a sede não muda a impressão digital do contrato, e as
   provas de rota continuam válidas.
4. **Conferir antes de escrever:** para cada fonte, `lugar_declarado_pela_fonte()` tem de devolver o
   `VALOR` da coluna «O contrato devolveria». Isso já foi medido: as 23 propostas passam o gazetteer.
5. **Decisões do dono antes de escrever:**
   - Image Line: sede legal (Roma) ou operacional (Faenza)?
   - A precisão PROVINCE para comunes fora do gazetteer é aceitável, ou traz-se a lista oficial de comuni?
   - As 9 por «mesmo site» podem entrar com essa base, ou só com página própria?

## Ficheiros (sha256 em `SHA256SUMS.txt`)
- `medir_sede.py` → `SEDE-DAS-FONTES-V1.json` (as moradas vistas por fonte, com os trechos);
- `propor_regra.py` → `PROPOSTA-SOURCE-LOCATION-RULE-V1.json` (a regra proposta e o que o contrato devolveria);
- `COORTE-60.json`, `NOMES-60.json` (os nomes, do livro do Curator do vivo).
