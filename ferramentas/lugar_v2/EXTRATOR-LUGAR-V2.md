# EXTRATOR-LUGAR-V2 — mais lugar do fato, com a mesma lei

Ramo `extrator-lugar-v2`, a partir do vivo `69b0e23f` + `periodo-chaves-v1` `91ab4eb3` (a região é dela; não
mexi no dono da região). **NÃO instalado. Rede: 0. Mapa: não regerado (a peça `C-LUGAR-V2` está declarada).**
Sala e RAW não tocados: a medida usa as entradas da ACERVO (lidas da Sala por SELECT só-leitura, sha256 conferido).

## EM PALAVRAS SIMPLES

O leitor que descobre **onde aconteceu** um fato tinha três pontos cegos, medidos pela RENDIMENTO-POR-FONTE:
cidades pequenas (não estão na lista de lugares), "na província de Verona" e títulos curtos (eram jogados fora).
Ensinei os três, **sem mudar a regra principal**: um lugar só vira "lugar do fato" se estiver ligado a um
acontecimento (praga, colheita, chuva registrada, mercado…). O nome de quem publica, o nome de um órgão e a
morada do rodapé **nunca** entram.

O que muda de verdade hoje, medido nos 1.252 conteúdos: **3 itens da Sala ganham lugares mais precisos, e os 3
estão certos** (Lecce, com chuva registrada; Milano e Asti, com lojas abertas; Ragusa, com o mercado de Vittoria);
**4 itens ganham a data do evento** que estava no título. O número de itens com lugar **não sobe** hoje, e digo
porquê: a **lista oficial dos comuni do ISTAT não existe nesta máquina** (deixei o mecanismo pronto para quando o
ficheiro vier), e a maior parte dos casos que a RENDIMENTO achou fala de **vento forte, incêndio ou evento
atmosférico**, que a lei de hoje **não conta como acontecimento do campo** — isso é decisão do dono, não do leitor.

## 1 · Comune pela lista oficial do ISTAT

- **Procurei a lista, sem rede:** no repositório (todos os ramos), no disco (`C:/`, `C:/Users/London1`) e nos
  pacotes Python. **Não existe.** Só aparecem nomes soltos dentro de outros dados. Não a escrevi de memória: a lei
  do gazetteer é «cobertura declarada, não presumida».
- **O mecanismo** (`leis/fato_local.comuni()`): lê `leis/dados/Elenco-comuni-italiani.csv` (o CSV do ISTAT, «;»,
  latin-1), pelos nomes das colunas; o comune sai com **precisão MUNICIPALITY**, a sua **província** e **região**
  (`FACT_LOCATION_PROVINCE/REGION/SIGLA`); só entra escrito com maiúscula; **homónimo** (Castro BG × Castro LE) só se
  resolve com a sigla «(LE)» a seguir — sem ela fica de fora. `cobertura()` diz `MUNICIPALITIES_SOURCE` com o sha256
  do ficheiro, ou **«AUSENTE — sem a lista oficial do ISTAT, nenhum comune»**.
- **Estimativa do que a lista daria aqui** (`estimar_comuni.py`, teto): dos **969** itens sem lugar e com texto,
  **0** têm «Nome (XX)» preso a um acontecimento. Os exemplos da RENDIMENTO («a Pontenure», «Finale Emilia») estão em
  frases sem âncora agro (padrão B). **A lista ajuda pouco neste acervo; a âncora é o gargalo.**
- **Para a trazer:** 1 pedido autorizado ao ISTAT (egresso IT, D38), gravar com sha256 em `leis/dados/`, e medir de novo.

## 2 · «provincia di X» / «in provincia di X» / «nel X-ese»

- «(in / nella / della) provincia di X» → X com **PROVINCE**, e ganha ao nome solto no mesmo ponto.
- «nel / del / dal / sul X-ese» → a província (ou região) cujo nome, sem a vogal final, + «ese» dá o adjectivo
  (veronese → Verona, modenese → Modena). **Derivado da lista**, não escrito à mão; «francese», «paese» não casam.
- ⚠️ **Conflito com uma lei antiga, resolvido sem a apagar:** `provincia di` era âncora **negativa** («BOLLETTINO
  FITOSANITARIO **DELLA** PROVINCIA DI SALERNO» — o âmbito do boletim, não um fato). Ficou negativa **salvo** quando
  vem **«in / nella provincia di»** (o sítio onde aconteceu). O boletim de Salerno continua recusado (testado).

## 3 · Título curto

- `fato_do_texto.titulo()`: a 1.ª linha do texto (o `<title>`), **sem o último pedaço depois de « - », « — », « – »,
  « | »** — que é o **nome do site** (quem publica: nunca lugar do fato) — **salvo se esse pedaço tiver números**
  («Evento RetePAC … - 26 Maggio 2026» fica inteiro). Entra se sobrarem ≥ 3 palavras e não for rodapé.
- `corpo()` põe o título à frente e **deixa de ler a 1.ª linha crua** (antes, um título com ≥ 8 palavras entrava com o
  nome do site: «… — Arpae **Emilia-Romagna**»).
- Uma página guardada **numa linha só** (menu + rodapé + artigo) não é título (medido: IT-T9-009).

## 4 · O que nunca entra (testado)

Sede de quem publica (nome do site; morada do rodapé com CAP) · nome de órgão («La Provincia di Verona ha approvato…»;
e, lido à mão na medida, **a palavra de produção dentro do nome de um órgão**: «l'Istituto … per la **Coltivazione**
dei Tabacchi» dava Salerno como CAMPO — corrigido) · homónimo sem sigla · página com vários eventos (regra do
CONSERTO-REGUA, intacta).

## 5 · Testes e mutação

`tests/test_extrator_lugar_v2.py` **20/20** (frases reais: IT-T12-024, IT-T12-008, IT-T3-008, IT-T10-018, IT-T5-010) ·
os que já existiam, iguais: `test_fato_do_texto` 44 · `test_lugar_do_fato` 23 (8 saltados, como antes) ·
`test_periodo_e_chaves` 22 · `test_tempo_e_lugar_atravessa` 43 · `test_conserto_regua` 10 ·
`test_a_collection_preserva_o_fato` 47 · `test_c7_lugar_do_fato` 20 · `test_quatro_chaves` 11.
**Mutação 8/8** (`MUTACAO-LUGAR-V2.json`): sem «provincia di» · qualquer adjectivo em -ese · homónimo fica com o 1.º ·
título com o nome do site · «in provincia di» volta a ser negativa · título de qualquer tamanho · âncora dentro de
órgão conta · título corta a data.

## 6 · Antes → depois nos 1.252 (só leitura; `medida/`)

Mesmas entradas nos dois lados; «antes» = `91ab4eb3`, «depois» = `a1dd6e24`.

| | fora da Sala (1.158) | Sala (88 conteúdos / 94 linhas) |
|---|---|---|
| **itens com lugar do fato** | 71 → 71 | 17 → 17 — **3 itens ganham 4 lugares a mais**, todos certos |
| data do fato | 66 → **70** (+4, datas de evento em títulos) | 20 → 20 |
| publicação · lugar da fonte | iguais | iguais |
| só o texto do porquê mudou | 204 (lugar) · 10 (data) | 6 (lugar) |

Grandes ficheiros fora do Git (sha256 em `medida/FORA-DO-GIT.sha256`): `C:/Users/London1/reproc-acervo/lugar-v2/antes.json`, `depois.json`.

## 7 · 20 lidos à mão (`medida/LIDOS-A-MAO-20.json`: as 7 mudanças de valor + 13 «só o porquê» por sorteio)

| # | fonte | mudança | veredito |
|---|---|---|---|
| 1 | IT-T3-008 (Sala) | Puglia → Puglia ; **Lecce** — «si sono registrati in provincia di Lecce a Nociglia e Otranto» (chuva) | ✔ |
| 2 | IT-T10-018 (Sala) | + **Milano ; Asti** — «inaugura due nuovi punti di vendita a Cisliano, in provincia di Milano, e Castell'Alfero, in provincia di Asti» (MERCADO) | ✔ |
| 3 | IT-T10-018 (Sala) | + **Ragusa** — «Al mercato ortofrutticolo di Vittoria, in provincia di Ragusa» (MERCADO) | ✔ |
| 4 | IT-T7-036 | data **3 luglio 2025** — «Life Atena: evento finale - 3 luglio 2025» (EVENTO) | ✔ |
| 5 | IT-T12-011 | data **18 giugno** — «seminario del 18 giugno SQNPI 2026» (EVENTO) | ✔ (sem ano: «2026» é o nome do SQNPI — comportamento que já existia) |
| 6–7 | IT-T12-011 | **26** e **27 maggio 2026** — «Evento RetePAC Valutazioni ex post - 26/27 Maggio 2026» | ✔ |
| 8–20 | vários | só o porquê: «o texto não tem corpo» passa a dizer o que foi mencionado («só mencionados: Lazio»); o trecho perde «- YouTube»; uma data de lista descartada fica dita | ✔ nenhum valor mudou |

**20/20 certos.** O único erro visto durante a medida (Salerno, IT-T5-010) foi corrigido antes desta leitura (§4).
E um «ganho» da 1.ª medida (IT-T9-009, Piacenza) **não era real**: vinha de meia página numa linha tratada como título.

## 8 · Plano de instalação (coordenador; um escritor)

1. `git -C $VIVO rev-parse --short HEAD` = **69b0e23f**; o ramo tem por baixo a `periodo-chaves-v1` (91ab4eb3): instalar
   **depois** dela (ou junto, pela INTEGRA-NOITE). 2. backup dos livros + `HEAD-ANTES`. 3. `git merge --ff-only <SHA>`.
4. livros iguais. 5. testes do §5. 6. mapa (VALIDAR, com a LOCK-PESADO). 7. push. 8. **Sala:** o reprocessamento de
tempo/lugar (`admissao/reprocessar_tempo_lugar.py`, sem `--aplicar` primeiro) daria, pela previsão, **3 itens com lugares
a mais**; aplicar é decisão do coordenador (revisões append-only). **Desfazer:** `git reset --keep <HEAD-ANTES>`.

## 9 · Decisões do dono

1. **Trazer a lista oficial do ISTAT** (1 pedido autorizado) — ganho estimado aqui: pequeno (§1).
2. **Vento forte, incêndio, evento atmosférico** contam como acontecimento para o lugar e a data do fato? É o que
   destrava a maior parte dos casos da RENDIMENTO (padrão B) — mexe na lei D62, não no extrator.
