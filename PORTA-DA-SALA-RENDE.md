# PORTA-DA-SALA-RENDE — quanto a régua deixa de fora, porquê, e uma proposta DESLIGADA

Branch `claude/porta-sala-rende-k4gunr`, base `b273660b` (= `origin/servico-20260923-0923`), 2026-09-28.
Offline: sem rede, sem Sala, sem livros vivos tocados. **A régua ligada não mudou**
(`PORTA_SALA_RENDE_LIGADA = False`, `VERSAO_DA_REGRA = "10"`).

```
LIVRO DESTA ÁRVORE        1.243 julgamentos (NÃO 1.459: o número do coordenador vem do livro vivo — NÃO SEI daqui)
COM TEXTO NO REPO           643 julgamentos · 236 pares distintos (documento × universo) · 193 documentos
SEM TEXTO NO REPO           600 — 594 são o portão `legivel` («veio sem texto»): nenhuma régua os muda
SIM A MAIS NA SALA          0   (replay do livro inteiro, porta inteira)
SIM A MENOS NA SALA         1   (efeito da peça MOLDURA — ver riscos)
NÃO → NÃO_SEI               53  (peça NAO_COM_DOIS_SINAIS; ninguém mais é descartado por uma palavra solta)
T8 / T12                    não existem no livro desta árvore → medidos em hipótese sobre o acervo (259 docs)
MUTAÇÃO                     17/17 mortos · TESTES 25/25 · BATERIA 0 falhas novas por nome
```

---

## 1 · Diagnóstico — onde está a matéria que não entra

### 1a · O livro que existe aqui não é o livro que o coordenador mediu

`data/samples/LIVRO-DE-DECISOES.json` tem **1.243** decisões, versões **1 a 5**, em
`b273660b`, em `origin/servico-20260923-0923` e em `origin/nuvem/porta-da-sala-rende-v1`. Os
1.459 julgamentos, a R03 de hoje (5 documentos, `1119` terraevita) e a Sala por versão
(v10=148…) vivem no banco. **Não os vi.** Tudo o que se segue é sobre o livro e o acervo
versionados; a R03 está **modelada** nos testes (E1), não relida.

### 1b · 594 dos 813 NÃO_SEI do livro não são problema de régua

| universo | julgamentos sem texto no repo | portão | o que é |
|---|---|---|---|
| T4 | 326 NAO_SEI | `legivel` | registos sem texto (item `?`, v1) — é o «T4 326 todos NÃO_SEI» |
| T9 | 118 NSA + 38 NAO_SEI | `legivel` | fichas de conta/catálogo e itens vazios |
| T7 / T10 / T5 / T3 | 42 / 39 / 4 / 3 NAO_SEI | `legivel` | URLs sem texto colhido |
| T7 | 24 NSA | `legivel` | fichas de catálogo |

**Uma régua não julga o que não foi colhido.** Estes pedem coleta, não régua.

### 1c · Os pares COM texto, relidos pela regra de hoje (v10)

Dos 236 pares, a porta inteira de hoje dá: T10 17 SIM · 61 NÃO · 33 NÃO_SEI; T7 0 SIM · 22 NÃO ·
57 NÃO_SEI; T5 2 SIM · 4 NÃO · 40 NÃO_SEI. Quem parou cada um (`PORTAO_QUE_PAROU_HOJE`):

- **T7 36 e T5 36 param no portão `origem`**, não na régua: os PDF de 2026-09-08 têm
  `SOURCE_ID = NAO SEI` no registo (`data/derivados/REGISTO-DE-ARTEFATOS.json`). Linhagem.
- T10 13, T5 3, T7 3 param no portão `materia` (capa/quarentena do detector).
- O resto para na régua do universo.

### 1d · Amostra estratificada LIDA (109 pares, `scripts/porta_sala_rende/AMOSTRA-LIDA-V1.json`)

Até 20 NÃO + 20 NÃO_SEI por universo (T5 só tem 9 NÃO_SEI), semente 20260928. Rótulo meu
(modelo), `VALIDADO_POR_HUMANO = NÃO`.

| universo | n | útil p/ ESTE universo, perdido | já recuperado pela v10 | útil p/ OUTRO universo | não é matéria útil | NÃO SEI |
|---|---|---|---|---|---|---|
| T7  | 40 | **0** (1 discutível: balanço de cooperativa) | 0 | 18 | 22 | 0 |
| T10 | 40 | **3** | 5 | 6 | 24 | 2 |
| T5  | 29 | **0** | 0 | 29 | 0 | 0 |
| **total** | **109** | **3 (2,8%)** | 5 | **53 (49%)** | 46 (42%) | 2 |

**Porquê**, por causa, com o item:

- **Pergunta errada — a causa dominante (53/109).** Boletins fitossanitários e
  agrometeorológicos (IT-T2/T3, FEM, ARPAV, Lazio, Veneto) perguntados a T7 e a T5. São matéria
  de T2/T3/T4 — e o livro nunca lhes fez essa pergunta, porque **o universo vem do pedido**.
  Mais 5 são de T12 (DdL «Coltiva Italia», Manifesto do Biocontrolo, crise do vinho), que não
  tem régua.
- **Léxico curto (T10, 3/40).** #40 «nuovo mercato ortofrutticolo di Bari»: `mercato` saiu da
  régua (era menu) e a notícia caiu em NÃO por **uma** palavra de T9 (`annuncio`). #60 (PPWR no
  sector) e #65 (barómetro de consumo) têm um só sinal (`prezzo`/`prezzi`).
- **Língua (T10, 5/40)** — os artigos avícolas ingleses (Zootecnica) estavam NÃO_SEI no livro
  (antes da D3) e **já são SIM com a régua de hoje**. Não é trabalho desta proposta.
- **Menu/rodapé.** Nesta amostra quase nenhum NÃO nasce do menu: das palavras que provaram NÃO,
  as que estão só na moldura são 4 (`etichetta`, `ricerca` ×2, `registrazione`), todas ao lado
  de outras do corpo. O efeito de menu que existe está do lado do **SIM falso** (a nuvem de
  etiquetas «prezzi» do myfruit, já medida no RELATORIO-DIAGNOSTICO-SALA). A R03 (`campagna`
  do menu CIA) **não tem par neste acervo** — está reproduzida no teste E1.
- **Não é matéria útil (46/109):** comunicação de marca de cantina (Riunite/Cavicchioli),
  eventos de consórcio, prémios. A régua acerta em não os admitir.

---

## 2 · Proposta (PROPOSTA — decisão do bot Luciano / dono)

Tudo em `admissao/admissao.py`, atrás de `PORTA_SALA_RENDE_LIGADA = False`
(`admissao/admissao.py:1407`; núcleo `:831`, NÃO-com-dois `:975`, moldura `:1500`, secção `:1531`, invólucro `:1572`). Desligada, `_do_universo` chama `_do_universo_regua` sem extras —
a porta de hoje, byte a byte (teste `A_ChaveDesligada`). Cinco peças, cada uma mensurável
sozinha (`PORTA_SALA_RENDE_PECAS`):

| peça | o que faz | onde |
|---|---|---|
| `MOLDURA` | julga o **corpo** da página HTML, não o menu/cabeçalho/rodapé. **Não há extrator novo**: é `leis/fato_do_texto.corpo()` (+`sem_vizinhos` D19). Só em HTML (quem traz `retrato_do_detector`). Corpo < 200 caracteres → julga o texto inteiro, como hoje (`MOLDURA_NAO_SEPARAVEL`). A língua mede-se na página inteira, como hoje. | `_sem_moldura` |
| `NAO_COM_DOIS_SINAIS` | NÃO pede o que o SIM pede: ≥ 2 termos de **um** outro universo. Menos → NÃO_SEI (`UM_SO_SINAL_DE_OUTRO_UNIVERSO`). | `_do_universo_regua`, parâmetro `nao_com_dois` |
| `T8` | a régua YT2 (`youtube-regua-t8-v1` @ `4f39e8c0`), **sem uma palavra mudada**, por conceito, palavra inteira, transversal. | `REGUAS_PSR["T8"]` |
| `T12` | régua **nova, NÃO MEDIDA** (não há gabarito). Ver abaixo. | `REGUAS_PSR["T12"]` |
| `SECAO` | página HTML cuja morada acaba num segmento de < 5 palavras sem algarismos (`/attualita/chi-e-dove/`) não vira SIM → NÃO_SEI. Critério **lido** de `curadoria/reparar_contrato._palavras` + `MENU_PALAVRAS_MAX`. | `_e_secao` |

E uma regra que atravessa todas: **nenhum SIM sai da proposta sem trecho** do texto julgado
(`evidencia.trechos`; sem trecho → `SEM_TRECHO`, NÃO_SEI).

Ligar = mudar a linha e subir `VERSAO_DA_REGRA` para `"11"` no mesmo commit.

### T12 · POLICY / AGRICULTURAL ENVIRONMENT — PROPOSTA

**O que conta:** o texto fala de uma **mudança de política** que afeta produtor, mercado ou
portfólio (Atlas: CAP, políticas, redução de insumos, agricultura regenerativa, restrições).
SIM pede **dois conceitos distintos**, palavra inteira; T12 é transversal (nunca prova NÃO a
outro universo).

Sinais positivos (it): `politica agricola comune|pac` · `sviluppo rurale|psr|feasr` ·
`ecoschema…|condizionalita` · `green deal|farm to fork` · `disegno di legge|ddl|legge di bilancio|decreto-legge` ·
`emendamento|emendamenti` · `uso sostenibile dei prodotti fitosanitari|piano d'azione nazionale|riduzione dei fitofarmaci…` ·
`agricoltura rigenerativa|conservativa|carbon farming|crediti di carbonio` · `nuove tecniche genomiche|TEA` ·
`aiuti di stato|de minimis` · `direttiva nitrati` · `normativa europea|quadro normativo…` · `dazi|mercosur|tensioni commerciali`.

Exemplos **reais** do acervo:
- ✅ SIM — IT-T7-042 «DdL Coltiva Italia: Federvini e Consorzio… plaudono all'emendamento»
  (trecho: «…l'approvazione dell'emendamento al disegno di legge coltiva italia…»). 3 SIM = 3 versões da mesma página.
- ◻ NÃO_SEI (1 conceito) — IT-T7-043 Manifesto per il Biocontrollo («…dentro la politica agricola comune…»);
  IT-T10-018 «Certificazioni e Ppwr».

Sinais negativos, **medidos** no acervo e deixados de fora: `politiche agricole` (69 só na
moldura/cabeçalho — é o nome do ministério e da «Direzione generale»), `masaf` («finanziata dal
MASAF»), `sostenibilità` (24 corpos, todos slogan), `regolamento (ue)` (GDPR), `parlamento
europeo` (citação do Reg. 1107/2009 = T4), `normativa` solta, `agricoltura biologica`
(prática nos boletins T3), `biocontrollo` (categoria de produto).

### T8 · FARMERS & INFLUENCERS — a régua YT2, e o problema dela em documentos

Medida em **vídeos** de canais (precisão 0,769 · recall 0,50, dentro da amostra, rótulo de
modelo). ⚠️ O pedido chama T8 a «redes/mídia/eventos institucionais»; o Atlas (dono) chama-lhe
**FARMERS & INFLUENCERS** e manda eventos para T11. A proposta segue o Atlas.

---

## 3 · Replay offline (`scripts/porta_sala_rende/replay_porta_sala_rende.py` → `REPLAY-PORTA-SALA-RENDE-V1.json`)

### 3a · Julgamentos do livro (1.243), porta inteira

| universo | LIVRO (como escrito) | HOJE v10 (mesmo texto) | PROPOSTA |
|---|---|---|---|
| T10 | 24 SIM · 110 NÃO · 120 NS | 34 SIM · 116 NÃO · 104 NS | 32 SIM · 49 NÃO · 173 NS |
| T7  | 36 SIM · 72 NÃO · 313 NS · 24 NSA | 0 SIM · 66 NÃO · 355 NS · 24 NSA | 0 SIM · 14 NÃO · 407 NS · 24 NSA |
| T5  | 18 SIM · 22 NÃO · 13 NS | 2 SIM · 4 NÃO · 47 NS | 2 SIM · 0 NÃO · 51 NS |
| T3  | 2 · 4 · 3 | igual (sem texto) | igual |
| T4  | 326 NS | igual (sem texto) | igual |
| T9  | 38 NS · 118 NSA | igual (sem texto) | igual |

(Os 36 SIM de T7 no livro são das v1/v2, com o léxico português antigo; a v10 já não os dá — não é
efeito da proposta.)

### 3b · Pares distintos (236) — o que muda na Sala

| universo | HOJE v10 | PROPOSTA | Δ SIM |
|---|---|---|---|
| T10 (111) | 17 SIM · 61 NÃO · 33 NS | 16 SIM · 26 NÃO · 69 NS | **−1** |
| T7 (79)   | 0 · 22 · 57 | 0 · 7 · 72 | 0 |
| T5 (46)   | 2 · 4 · 40 | 2 · 0 · 44 | 0 |

**Itens a mais na Sala: 0.** Mudam 55 pares:
- 53 NÃO → NÃO_SEI pela peça `NAO_COM_DOIS_SINAIS` (T10 34 · T7 15 · T5 4). Ex.: 4 boletins
  ARPAV em T7 que eram NÃO só por `ovideposizione`; 10 comunicados Riunite que eram NÃO por
  `evento`/`prodotto`; o Manifesto do Biocontrolo (`ricerca` + `evento`).
- 1 NÃO → NÃO_SEI pela `MOLDURA`.
- **1 SIM → NÃO_SEI pela `MOLDURA`** — myfruit «Annamaria Medici: in ortofrutta vince il
  valore percepito»: o corpo do artigo é **uma linha de 7.034 caracteres** que contém
  «accessibilità»; o `RODAPE` de `corpo()` deita a linha inteira fora, com `commodity` e
  `prezzo` dentro. **SIM verdadeiro perdido.**

Lista completa com motivo e trecho: `MUDAM` no JSON. **Nenhum SIM da proposta está sem trecho**
(regra testada).

### 3c · Os que continuam fora, e porquê (pares, proposta)

| causa | T10 | T7 | T5 |
|---|---|---|---|
| portão `origem` (`SOURCE_ID = NAO SEI`) | 0 | 36 | 36 |
| capa / quarentena do detector | 13 | 3 | 3 |
| um só sinal **deste** universo (léxico curto) | 19 | 17 | 1 |
| um só sinal de **outro** universo (era NÃO) | 34 | 15 | 4 |
| NÃO com ≥ 2 sinais de outro universo | 20 | 4 | 0 |
| nenhum sinal | 9 | 4 | 0 |

Só a pergunta do universo (sem portões de prontidão): T5 15 → 12 SIM; T10 19 → 18; T7 1 → 1.
A queda de T5 é a peça `MOLDURA` em IT-T5-049 (di3a.unict.it: «avvisi esami», «avvisi lezioni»,
«welcome day» — os sinais de T5 estavam no menu da universidade): **SIM falsos que saem**. Na
porta inteira estes pares já paravam antes (portão `materia`/`origem`), por isso não aparecem em 3b.

### 3d · T8 e T12 em hipótese (acervo inteiro, 259 documentos)

| | SIM |
|---|---|
| T12 | 3 (a mesma página DdL, 3 versões) — **3/3 corretos** pela leitura |
| T8 | **36** — IT-T10-022 17 (revista avícola), IT-T10-018 8 (notícias de fruta), IT-T7-017 4 (cantina), boletins IT-T2/T3 7 |

Lidos os trechos: **nenhum dos 36 é a voz do agricultor ou de um criador**; são mídia de
sector e serviços técnicos a falar **de** agricultores («le aziende agricole…», «livestock
farms…»). Com a definição do Atlas, são falsos SIM. Com a definição do pedido
(«mídia/redes»), talvez não. **Decisão.**

### 3e · O tamanho da decisão «pergunta errada» (hipótese D2 REROUTE)

Se cada documento do acervo fosse perguntado a **todas** as réguas: **103/259** teriam SIM em
pelo menos um universo hoje (T9 56 · T5 34 · T10 28 · T3 16 · T2 10 · T4 10 · T1 8 · T7 1).
Contra os **19** SIM que os 236 pares do livro dão. ⚠️ Os 56 de T9 são, pela leitura da
amostra, maioritariamente comunicação de cantina (`evento`, `prodotto`, `campagna`): o
número é o tamanho da pergunta, não matéria provada.

---

## 4 · Riscos (falso SIM e o resto)

1. **MOLDURA apaga corpo verdadeiro.** `corpo()` trabalha por linha, e `limpar()` junta a
   página em poucas linhas: 28/216 páginas (IT-T10-022, minificadas) dão corpo vazio (fica o
   fallback), e **14/216** (IT-T10-018 12, IT-T7-033 2) perdem uma linha longa de corpo por uma
   palavra de rodapé. Medido: 1 SIM verdadeiro perdido. O menu escrito numa linha só
   (Chianti Classico) **sobrevive** ao `corpo()`. **Não recomendo ligar MOLDURA** antes de o dono
   de `leis/fato_do_texto.py` (LUGAR-FATO) tornar o corpo robusto a linhas longas.
2. **T8 em documentos:** 36 SIM hipotéticos, 0 com voz de campo pela leitura.
3. **T12 não tem gabarito:** 3 SIM, todos certos, n = 1 página. Precisão real NÃO SEI.
4. **NAO_COM_DOIS_SINAIS** não cria SIM — só troca 53 descartes por «ir ver». O custo é fila:
   +36 NÃO_SEI em T10.
5. **SECAO** só atua com morada conhecida e HTML; morada numérica passa. 0 pares mudaram no livro.

## 5 · O que precisa de decisão (bot Luciano / dono)

1. **Ligar `NAO_COM_DOIS_SINAIS` + `SECAO`** (seguras: 0 SIM falso, 0 SIM perdido no replay)?
2. **MOLDURA:** esperar pelo corpo robusto a linhas longas (recomendado) ou aceitar −1 SIM medido?
3. **T8 = quem?** Voz do campo (Atlas) → a régua YT2 só em vídeo/redes; «mídia/eventos» (pedido) → outra régua, e T11 fica com os eventos.
4. **T12:** aprovar a lista como está, ou pedir gabarito (como T1/T2) antes de ligar?
5. **A decisão grande:** a matéria-prima está na **pergunta**, não na régua. «O universo vem do
   pedido» deixa 49% da amostra fora por pergunta errada. Perguntar a mais do que um universo é
   uma mudança de lei (D2 REROUTE), não de régua.
6. **Coleta/linhagem:** 594 julgamentos sem texto e 72 pares parados por `SOURCE_ID = NAO SEI`.

---

## 6 · Provas

- Testes: `tests/test_porta_sala_rende.py` — **25/25**. E1 (R03 modelada: hoje 2 NÃO + 3 NSA, 0 SIM),
  E2 (menu CIA não dá NÃO; corpo T7 positivo entra com trecho do corpo), E3 (T8/T12 sem régua =
  NSA literal), E4 (`chi-e-dove` não vira SIM; a mesma página numa morada de matéria entra).
- Bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada, Linux):
  base `b273660` 320 módulos · 7.190 testes · **125** falhas; depois 321 · 7.216 · **124**.
  **Novas: 0.** Sumida: 1 (`test_c3_youtube_cutover.test_gravar_raw_respeita_o_redirecionamento`
  — falha na base só porque o worktree da base estava em `/tmp` e o caminho relativo saía dele;
  ambiente, não esta mudança). A 1.ª volta depois deu 2 «novas» (`test_candidatos_tematicos`,
  `test_gate_de_aceitacao_tematica`): verificam que `admissao/` não tem mudança **por commitar** —
  passam depois do commit. JSON: `scripts/porta_sala_rende/BATERIA-*.json`.
- System Map: `correr_a_cadeia.py REGERAR` + `VALIDAR` → `SYSTEM_MAP_CHECK=PASS`;
  `impressao_da_arvore.py --conferir-carimbo` → `IGUAL`. `C-ADMISSAO` continua 🟡 PENDING
  (já estava na base: descrição por reler por gente) — **não recarimbei**.
- Mutação: `scripts/porta_sala_rende/mutar_porta_sala_rende.py` numa cópia → **17/17 mortos**
  (`MUTACAO-PORTA-SALA-RENDE-V1.json`). Na primeira volta 2 sobreviveram (teste do «NÃO com
  dois» usava 3 palavras; teste do ministério não tinha segundo conceito): os testes foram
  **apertados**, não a régua afrouxada.
- Erros meus apanhados pela medição: (a) ligar só T8 ligava também o NÃO-com-dois (53=53=53 na
  tabela por peça) — corrigido e testado; (b) a língua passou a ser medida no corpo e um artigo
  italiano saiu «en» — corrigido e testado.

## EM PALAVRAS SIMPLES

A porta não está a deitar fora muita coisa boa **por causa das palavras**: na amostra lida,
só 3 em 109 eram matéria útil para o universo que foi pedido. O que fica de fora é, na metade
dos casos, coisa boa **perguntada à gaveta errada** (um boletim de pragas perguntado como se
fosse rede técnica) e, no resto, publicidade de cantina. A proposta deixa de rejeitar coisas
por uma palavra solta (53 passam de «não» a «vai ver»), traz uma régua para política (T12) e
a de agricultores (T8) — mas, sobre o livro que existe aqui, **não põe nenhum item a mais na
Sala**, e a limpeza de menu, como está, **perdeu um item bom**. Para ter muita matéria-prima,
a decisão que conta é deixar cada documento ser perguntado a mais do que uma gaveta. Isso é
com o dono. Nada foi ligado.
