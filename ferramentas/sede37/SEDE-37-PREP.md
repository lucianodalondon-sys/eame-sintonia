# SEDE-37-PREP — onde fica quem publica: o que já se prova sem rede, e o plano para o resto

Ramo `sede-37-v1`, a partir do vivo `83de0ccd`. **NÃO instalado. Rede: 0 pedidos.** Vivo, Sala e RAW não tocados
(só leitura de páginas já guardadas; a escrita foi ensaiada em **cópias** dos dois livros, depois apagadas).

## EM PALAVRAS SIMPLES

Queremos saber, para cada fonte, **onde fica quem publica** (a sede): por exemplo, a ARPA da Toscana fica em
Florença. Hoje isso aparece em só 5 de 94 coisas na Sala. Olhei as 65 fontes da próxima coleta **sem ir à
internet**, só nas páginas que já guardamos. Resultado:

- **28 fontes já têm a sede provada** — o endereço está escrito no rodapé das páginas delas (li os trechos um por um).
  Antes eram 14; as outras 14 apareceram nas páginas que a 3.ª onda trouxe.
- **Para 34 das 37 que faltam, já sei qual página visitar** (a de "contatti", "dove siamo" etc.), porque o link está
  escrito nas páginas guardadas — não inventei nenhum endereço. Visitar essas páginas custa **32 pedidos**, no máximo
  **2 por site**, numa ida só, com a VPN da Itália. Para 3 fontes não achei a página e fica "não sei".
- Fiz a peça que **escreve** a sede no contrato de cada fonte: só escreve quando há prova; quando não há, fica
  "não sei" (nunca um palpite). A sede **nunca** vira o lugar do fato.

Se o coordenador instalar, as 27 fontes provadas (a 28.ª, Image Line, espera decisão) passam a levar a sede para
as coletas novas, e cerca de **37 das 94** coisas da Sala podem ganhar sede num reprocessamento (hoje: 5).

## 1 · As fontes sem sede provada, e a página que provavelmente a prova

Alvo = a coorte congelada da produção (**64**) ∪ as **61** prontas do ensaio consolidado = **65** fontes
(`PAGINAS-DE-SEDE.json`; lista das 51 em **`LISTA-51.md`**).

| sede | fontes |
|---|---|
| provada na própria página (SEDE-DAS-FONTES) | 14 |
| só pelo mesmo site | 9 |
| NAO SEI | 37 |
| fora da lista da SEDE-DAS-FONTES (novas na coorte: IT-T2-006, IT-T5-025, IT-T9-009, IT-T9-011; e a ISTAT IT-T5-090) | 5 |

**Onde procurei (só com sha256 certo):** o armazém da Sala e árvores de trabalho (raw.json da ACERVO, 31 raízes —
inclui a 3.ª onda), a loja do vivo, os 14 índices D40 guardados e a evidência do Curator.

**Sede provada sem rede, agora: 28** (as 14 de antes + **14 novas**: IT-T12-024 Venezia, IT-T12-129 Palermo,
IT-T12-130 Milano, IT-T2-006 Napoli, IT-T5-025 Pisa, IT-T5-056 Roma, IT-T5-186 Roma, IT-T7-019 Milano,
IT-T7-048 Roma, IT-T7-049 Roma, IT-T7-103 Roma, IT-T7-118 Roma, IT-T7-125 Bari, IT-T7-139 Roma).
**Li os 14 trechos novos: são todos o rodapé da própria organização** (ex.: «Regione del Veneto · Palazzo Balbi ·
30123 Venezia»; «CIA PUGLIA via Nicola Cacudi, 40 70132 Bari»). Notas: a IT-T12-130 (Edagricole) mostra a sede
legal da editora-mãe, **Tecniche Nuove Spa** (Via Eritrea 21, Milano); a IT-T7-139 (Florovivaisti) mostra a morada
da CIA em Roma — é uma associação da CIA, no rodapé do próprio site.

**Página de sede provável nas 51 sem prova na própria página: 48** — 28 por link na página da própria fonte,
20 por link numa página de **outra fonte do mesmo domínio** (dito na coluna: ex. as 14 da Edagricole pelo link visto
na IT-T12-130). Classes: contatti 40 · dove-siamo 3 · note-legali 5. **NAO SEI: 3** (IT-T2-034, IT-T7-172,
IT-T8-062 — nenhuma página guardada tem o link).

Filtros medidos na 1.ª volta: um ficheiro de estilo (`contact-form-7/…/styles.css`, IT-T7-017) e «La-societa-
circolare» (IT-T7-103, iniciativa, não "a sociedade") saíam como página de sede — corrigido.

## 2 · Plano da MICRO-SEDE (`micro_sede.py`, `MICRO-SEDE-PLANO.json`)

Só as fontes que **ainda** precisam (sem prova própria nem pelas páginas guardadas): **37**; com página: **34**.

| domínio | fontes | página | pedidos | ronda |
|---|---|---|---|---|
| arpa.veneto.it | 2 | https://www.arpa.veneto.it/note-legali | 2 | 1 |
| arpacampania.it | 1 | https://www.arpacampania.it/contatti | 2 | 1 |
| calabriaimpresa.eu | 1 | https://energia.calabriaimpresa.eu/note-legali/ | 2 | 1 |
| casalasco.com | 1 | https://www.casalasco.com/it/contatti | 2 | 1 |
| chianticlassico.com | 1 | https://www.chianticlassico.com/contatti/ | 2 | 1 |
| cia.it | 3 | https://www.cia.it/chi-siamo/contatti/ | 2 | 1 |
| ciatoscana.eu | 1 | https://www.ciatoscana.eu/home/presentazione/dove-siamo/ | 2 | 1 |
| cifo.it | 1 | https://www.cifo.it/contatti/ | 2 | 1 |
| crea.gov.it | 3 | https://www.crea.gov.it/contatti | 2 | 1 |
| **edagricole.it** | **14** | https://terraevita.edagricole.it/contatti/ | 2 | 1 |
| enea.it | 1 | https://sostenibilita.enea.it/contact | 2 | 1 |
| indire.it | 1 | https://fieradidacta.indire.it/it/contatti/ | 2 | 1 |
| istat.it | 1 | https://www.istat.it/contatti/ | 2 | 1 |
| koppert.it | 1 | https://www.koppert.it/contatti | 2 | 1 |
| psrn.it | 1 | https://www.psrn.it/contatti/ | 2 | 1 |
| zootecnicainternational.com | 1 | https://zootecnicainternational.com/contact/ | 2 | 1 |

**16 domínios · 16 páginas · 32 pedidos (1 robots + 1 página por domínio) · máximo 2 por domínio · 1 ronda.**
A mesma página com e sem «www.» pede-se uma vez (cia.it).

**Porque NÃO pelo orquestrador:** ele colhe ITENS pelo contrato de cada fonte e produz RAW de coleta; a página de
contactos não é matéria e não deve virar RAW. O orquestrador não tem rota de página única, e o `capturador` do
Curator não lê o robots e procura um "item". A MICRO-SEDE usa as **mesmas peças do canário das rotas**
(`gate_de_rota.robots_de/permitido` + `canario.buscar`), com o **portão de egresso IT** antes de pedir (sem PASS, 0
pedidos), guarda os bytes com sha256 e **só propõe** — não escreve contrato, tabela, livro, Sala nem RAW.
Decisão do coordenador se quiser outra rota.

Comando (com ordem; D38/D41.3):
```bash
py superficie/rede.py --portao-de-egresso IT      # PASS
py ferramentas/sede37/micro_sede.py --paginas ferramentas/sede37/PAGINAS-DE-SEDE.json --saida-plano <plano> \
   --correr --ronda=1 --autorizado=<coordenador> --saida C:/Users/London1/sede37-micro
py ferramentas/sede37/achar_paginas_de_sede.py --saida <novo PAGINAS-DE-SEDE.json> --micro C:/Users/London1/sede37-micro/MICRO-SEDE-RONDA-1.json
py ferramentas/sede37/escrever_sede.py --paginas <novo> --contratos … --tabela …        # mostrar; depois --aplicar
```
As 3 sem página (IT-T2-034, IT-T7-172, IT-T8-062) pediriam antes 1 pedido à entrada para achar o link — fase 2.

## 3 · Como a sede entra no contrato

- **Dono da regra:** `curadoria/sede_da_fonte.py` (a regra da SEDE-DAS-FONTES: CAP + comune + (SIGLA); ≥ 2 páginas ou
  «sede/contatti» ao lado; empate = NAO SEI; nunca o REGION do Atlas). Devolve os **4 campos** do contrato do Curator,
  na forma que a lei social já lê do mesmo livro:
  `SOURCE_LOCATION` (nome do gazetteer) · `SOURCE_LOCATION_BASIS` (página, sha256, morada, nº de páginas) ·
  `SOURCE_LOCATION_PRECISION` (PROVINCE/REGION) · `SOURCE_LOCATION_RULE` («<nome> (sede: …; prova: PAGINA_GUARDADA) — fixo»).
- **Conferido pelo leitor do contrato** (`regras/contratos_de_fonte`): a regra só sai se o leitor devolver o mesmo nome.
- **Precisão:** comune no gazetteer → o próprio (ex.: Firenze); fora dele → a **província da sigla**, só para as 8 siglas
  **declaradas** (MO, RE, RM, MI, FI, BO, GE, RA — as da SEDE-DAS-FONTES); outra sigla → **NAO SEI (NOT_IN_GAZETTEER)**,
  nunca palpite. Nome em MAIÚSCULAS confere (medido: IT-T7-043 «20149 - MILANO»).
- **UNKNOWN fica UNKNOWN:** sem prova, os 4 campos **não se escrevem**; a tabela não declara e o coletor lê «NAO SEI».
- **A ponte** (`onboardar_rotas_provadas.linha_da_tabela`) leva `SOURCE_LOCATION_RULE` do contrato do Curator para a
  tabela quando lá está. Não muda o `CONTRATO_SHA256` (só cobre SOURCE_ID, OUTPUT_TYPE, ACQUISITION): as provas de
  rota continuam válidas.
- **A porta de escrita** (`escrever_sede.py`, mostra por omissão): só fontes com prova **da própria página**; nunca
  pisa uma sede que já existe; `IT-T10-021` fica **PENDENTE_DO_DONO**; invariantes (só os campos da sede mudam).
  **Ensaio em cópias dos dois livros do vivo:** APLICA 27 · PENDENTE 1 · 2.ª passagem 27 JA_APLICADA · 27 fontes
  mudadas só nos 4 campos (contrato) e só em `SOURCE_LOCATION_RULE` (tabela) · ACQUISITION igual · as 27 regras
  passam no leitor do contrato. Mostrar não mudou nenhum byte.

**Testes (sem rede):** `test_sede_da_fonte` 12/12 (amostras = excertos reais da loja do vivo, sha256 em
`tests/dados/sede37/ORIGEM.json`; a página inteira conferida quando está na máquina) · `test_micro_sede` 7/7 ·
`test_escrever_sede` 6/6 · `test_onboardar_rotas_provadas` 29/29 · `test_soc_tempo_publicacao_e_lugar` 11/11 ·
`test_tempo_e_lugar_da_publicacao` 42/42 · `regras/italy_contract_test.mjs` 348 OK / 77 falham — **as mesmas 77, por
nome, na produção `83de0ccd`** (herdadas). **Mutação 4/4** (`MUTACAO-SEDE.json`): uma página sem «sede» basta ·
sigla desconhecida vira Roma · a ponte escreve sempre · NAO SEI escreve no contrato. (Um 1.º mutante — adivinhar o
próprio comune — sobrevivia porque a conferência pelo leitor do contrato já o trava; troquei-o pelo palpite perigoso.)

## 4 · Plano de instalação (executa: o coordenador; um escritor; bot parado nos passos 7–8)

1. Parar o robô (`PARAR.flag`; 0 processos).
2. `git -C $VIVO rev-parse --short HEAD` = **83de0ccd**; backup dos livros sujos com sha256 + `HEAD-ANTES.txt`.
3. O ramo não toca livros no Git: `git diff --name-only HEAD <SHA> -- $LIVROS | wc -l` → 0.
4. `git merge --ff-only <SHA>` (ponta de `origin/sede-37-v1`).
5. Livros iguais (sha256).
6. Testes: os 6 ficheiros acima + `node regras/italy_contract_test.mjs` (só as 77 herdadas).
7. **Escrever a sede das 27** (livros vivos, bot parado):
   `py ferramentas/sede37/escrever_sede.py --paginas ferramentas/sede37/PAGINAS-DE-SEDE.json --contratos curadoria/italy_contracts_curator.json --tabela regras/italy_contracts_onboarded.json`
   → conferir `APLICA 27 · PENDENTE_DO_DONO 1` → o mesmo com `--aplicar` → 2.ª passagem `JA_APLICADA 27`.
8. Mapa (VALIDAR com a LOCK-PESADO; neste ramo o mapa **não** foi regerado — a peça `C-SEDE-37` está declarada) e push.
9. Religar o robô. As coletas novas das 27 já saem com `source_location`.
10. **Sala (decisão do coordenador):** `py admissao/reprocessar_tempo_lugar.py --livros … --raizes …` sem `--aplicar`
    para conferir; previsão pelas fontes: **37 das 94 linhas** são das 27 (hoje 5 com sede) — não medido pela ferramenta.
11. **MICRO-SEDE** (§2), com ordem e portão IT; depois 12.
12. `achar_paginas_de_sede.py --micro …` → `escrever_sede.py` (mostrar → `--aplicar`) para as novas.

**DESFAZER:** passo 7 — repor as cópias de `italy_contracts_curator.json` e `italy_contracts_onboarded.json` do backup
(só os campos da sede mudaram); código — `git reset --keep <HEAD-ANTES>`.

## 5 · Decisões do dono

1. **IT-T10-021 Image Line:** sede legal (Roma) ou operacional (Faenza)? (fica fora até decidir)
2. **Precisão PROVINCE** para comunes fora do gazetteer (Spilamberto → Modena, Campegine → Reggio nell'Emilia): aceitável?
3. **Prova "pelo mesmo domínio"** (as 14 da Edagricole por uma só página de contactos da editora): aceitável depois
   da MICRO-SEDE? Hoje a porta **não** escreve nada que não tenha prova na página da própria fonte.
4. A MICRO-SEDE pela rota do canário (e não pelo orquestrador) — §2.

## Ficheiros

`PAGINAS-DE-SEDE.json` · `LISTA-51.md` · `MICRO-SEDE-PLANO.json` · `ESCREVER-SEDE-MOSTRAR.txt` · `MUTACAO-SEDE.json` ·
`achar_paginas_de_sede.py` · `micro_sede.py` · `escrever_sede.py` · `mutar_sede.py` · `curadoria/sede_da_fonte.py` ·
`tests/test_sede_da_fonte.py` · `tests/test_micro_sede.py` · `tests/test_escrever_sede.py` · `tests/dados/sede37/`.
