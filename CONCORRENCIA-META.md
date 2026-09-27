# CONCORRENCIA-META — a captura Meta de 31/08 vira linha de coleta recorrente (T9)

Branch `claude/concurrency-meta-collection-qp35vu`, nascida da produção `554c1ec1`. **Sem rede externa**: nada foi
coletado aqui. A nuvem não tem Chrome com janela nem saída pela Itália. Tudo o que diz «funciona» abaixo foi
provado **offline**: com a fixture declarada e um leitor falso injetado.

## 1 · O que veio do ramo `claude/eame-meta-competitor` (a2fad2d0) — só código e lei

| origem (ramo antigo) | destino | gaveta (AGENTS.md) |
|---|---|---|
| `scripts/meta_navegador.py` | `ferramentas/meta_biblioteca.py` | FERRAMENTA — fala com o Chrome por `ferramentas/cdp.py` (a da casa), e não por um `cdp.py` fora do Git |
| `scripts/meta_identidade.py` + `meta_adama.py` (a guarda) | `regras/meta_identidade.py` | RÉGUA QUE CARIMBA — corre antes da visita |
| `scripts/meta_anunciante.py` | `coleta/meta_anunciante.py` | AÇÃO de descoberta. Só escreve **PROPOSTA** em `data/colheita/meta/PROPOSTAS/` |
| regra de `meta_temporal.comparar` + `meta_relogio` | `coleta/concorrencia_meta.py` | AÇÃO — a linha recorrente |

**NÃO trazidos:** `meta_leitura` (cultura/praga no texto — é a Intelligence que lê), `meta_convergencia`,
`meta_piloto`, `meta_handoff`, `meta_porta`, `meta_coleta`/`meta_temporal` inteiros (a regra de comparação foi
portada), o clique no painel de páginas irmãs, **e nenhum dos 18 JSON de dados como dado de hoje.**

A lista de páginas, `data/samples/CONCORRENCIA-META/PAGINAS-META-IT-V1.json`, tem 25 páginas: 23 de concorrentes
com PAGE_ID provado pela Meta, mais 2 da ADAMA. Cada linha carrega a prova (`identity_proof` + `evidence_url`) e o
blob de origem. **Entram 23 na linha.** Ficam fora, com o motivo escrito:
- `Instytut Adama Mickiewicza`: recusado pela guarda de identidade;
- `FMC Moto Srl`: `NAO_AGRO_DECLARADO`.

## 2 · A linha (`coleta/concorrencia_meta.py`)

- **Lista → carimbo** (`paginas_da_linha` :130 → `regras/meta_identidade.py:91 carimbar`). Só passa PAGE_ID com
  prova da Meta, e o token da empresa tem de ABRIR o nome da página. PAGE_ID repetido é visitado 1 vez.
- **1 visita por página por rodada** (`visitar` :166, `rodada` :226). Não há repetição até o número agradar.
- **Na visita:**
  - o RAW da página é gravado antes de qualquer leitura (cabeçalho + cartões), com sha256;
  - `OBSERVED_AT` por recorte, e a rodada é uma janela (início/fim);
  - se a página não mostrar «Log in», a rodada **para** (`:195`, D88).
- **Comparação** (`comparar` :285) com a **última leitura boa de cada recorte** (`anterior_por_recorte` :475). Assim
  uma rodada que caiu não vira linha de base. A regra é a de 31/08:
  - *novo* só conta se a leitura anterior foi pelo menos tão funda (`:322`);
  - *terminado* só conta com as duas leituras fechadas pela fonte;
  - sem snapshot anterior, o resultado é `BASELINE_ONLY`, e nunca «nada mudou».
- **Saída pela Admission normal:**
  - cada cartão **visto pela primeira vez** vira uma unidade `COLHEITA` (`unidade` :378, `envelope` :438) no
    envelope COL-LAW-505, com `SOURCE_ID=EU-T9-002`;
  - `OBSERVACAO` leva a rota, a porta, o login, `COUNTRY_REACHED=IT`, `TARGET_LOCATION_STATE=NOT_PROVED`,
    `RAW_PAGINA{path,sha256}`, `SPEND=None` e o rótulo de novidade (`BASELINE` / comparável / não afirmável por
    profundidade);
  - o texto do criativo vai como `AUTHOR_TEXT` / `SCRAPED_FROM_RENDERED_PAGE`.
- **Receita T9** `concorrencia-meta` (`pedido/receitas.py:639`): `serve_fases=["meta-anuncios"]`, filtros nomeados
  `pais` e `teto`. Um pedido T9 **sem fase** abre o mesmo executor que abria antes.
- **Espécie:** a casa não tem `COMUNICACAO_DE_CONCORRENTE` nem `ANUNCIO_PAGO` em lado nenhum (medido por grep). Não
  inventei espécie nova. A unidade é `COLHEITA` e o anúncio pago é dito pela fonte (`EU-T9-002`) e pelo universo
  `T9`. **NÃO SEI se o dono quer uma espécie própria**: é decisão dele.

## 3 · As outras frentes, em lista (`medidas/concorrencia_frentes.py`)

Lê só: `candidatas/FONTES-CANDIDATAS.json`, `curadoria/italy_contracts_curator.json`,
`COMPETITOR-PUBLIC-COMM/CONTAS-V1.json` e a lista Meta. Escreve `FRENTES-PUBLICAS-IT-V1.json`: 12 empresas ×
5 frentes, cada célula com o degrau e o executor que já sabe colhê-la.

| frente | na linha / conta IT provada | resto | executor · limite |
|---|---|---|---|
| META_ADS | 9 NA_LINHA | 3 FALTA (Sipcam, Gowan, Ascenza) | concorrencia-meta · D88 |
| LINKEDIN_EMPRESA | 0 | 3 conta global · 2 na fila (POLICY_BLOCK) · 7 FALTA | scrap `video-linkedin` · D23 |
| YOUTUBE | 2 (Bayer, Syngenta) | 10 FALTA | scrap `canal-youtube` |
| INSTAGRAM | 2 (Bayer, Syngenta) | 1 global · 9 FALTA | scrap `captura-reel` · **D22: só Reel por URL direta — a conta sozinha não chega** |
| SITE_NOVIDADES | 0 | 1 na fila (Sipcam) · 11 FALTA | italia-recorrente · D91 |

O curador de contratos tem **0** entradas destas 12 empresas. `FALTA_NOS_LIVROS != A_CONTA_NAO_EXISTE`.

## 4 · Achados que mudam números

- **Os «414 anúncios» de 31/08 são 414 CARTÕES = 601 anúncios representados** (fixture, teste
  `test_o_414_de_31_08_sao_cartoes_e_nao_anuncios`). Por empresa: BASF 127/156, FMC 98/130, Corteva 79/178,
  Bayer 69/86, Syngenta 30/36, UPL 11/15.
- **A FMC dos 98 inclui 11 cartões da `FMC Moto Srl`**, que vende motocicletas. A FMC agro em IT são 87 cartões.
- **A página `Syngenta Italia` (PAGE_ID candidato `2007689772789481`) não está nos 414.** O site oficial liga-a
  (`CONTAS-V1`). A nota do ramo antigo fala em ~530 resultados em IT, número que eu **não verifiquei**. Ela entra na
  linha só depois de a Meta a confirmar (`meta_anunciante.py`). O mesmo vale para `Nufarm Italia` (`2312073685546312`).
- Na comparação de 31/08 em IT **nada mudou de forma afirmável**:
  - 4 recortes ficaram confundidos por profundidade (+101 cartões lidos mais fundo);
  - 19 recortes eram comparáveis, com 56 presentes nas duas leituras, 0 novos e 0 terminados.
- A ficha `EU-T9-002` no Atlas continua «NÃO TESTADO». **Não a mudei**: promover a ficha é gesto do dono.

## 5 · Testes, mutação, mapa

- `tests/test_concorrencia_meta.py`: **32 testes, OK**, fixture DECLARADA em `tests/dados/concorrencia_meta/`
  (recorte IT de 31/08, com o blob de origem no cabeçalho). O que cobrem:
  - a comparação nova reproduz **recorte a recorte** a de 31/08;
  - ponta a ponta envelope → `ingresso.receber` → `admissao.decidir(T9)` = **SIM** → READY;
  - login, ferramenta caída (`BROWSER_NOT_REACHED`), rodada que caiu, 1 visita, sem reenvio à Sala;
  - quadro das frentes = o que os livros produzem.
- Novo passo de CI `4q2` no COLETA CHECK (`.github/workflows/system-map.yml:681`).
- **Mutação** `tests/mutacao_concorrencia_meta.py` → **12/12 morderam**, com verde antes e depois
  (`provas/concorrencia_meta/MUTACAO-V1.json`).
- **Bateria por nome**, contra a base `554c1ec1` (285 módulos, rede fechada), ficheiro
  `provas/concorrencia_meta/BATERIA-COMPARACAO.json`: ver §7.
- **Ajuste DECLARADO de 2 testes.** Os dois pedem-no quando nasce um executor novo em T9:
  - `tests/test_italia_na_porta_canonica.py:232`: `concorrencia-meta` entra em `PEDEM_A_CORRIDA`. O teste diz
    «o nome dele entra em PEDEM_A_CORRIDA — nunca em silêncio».
  - `tests/test_receita_web_t8_t9_t12.py:104`: `POSTERIORES_A_D48`. A linha sai da fotografia da D48 **pelo nome**;
    qualquer outro executor novo continua a reprovar.
- **System Map:** 4 peças novas, carimbadas só nos ficheiros delas. As 3 peças de código ficam 🟢 PROVEN; a de
  medida (`C-FRENTES-CONCORRENCIA`) fica 🟡 PENDING, porque o gerador não tem regra de prova para o tipo `scanner`.
  - `C-META-BIBLIOTECA` (ferramentas)
  - `C-META-IDENTIDADE` (regras)
  - `C-COLETA-META` (coleta)
  - `C-FRENTES-CONCORRENCIA` (medidas)
  - `C-RECEITAS` continua 🟡 como **já estava na base**: o blob declarado era anterior à minha mudança. **Não usei
    `--stamp` global**, porque ele recarimbaria 125 ficheiros que eu não reli.

## 6 · Comando para o coordenador (máquina local, VPN italiana ligada)

```
# 1. Chrome COM JANELA na porta da Meta, perfil proprio (nunca a 9222/9223)
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9224 --user-data-dir=%USERPROFILE%\.sintonia-browser\meta\chrome-profile
py ferramentas/meta_biblioteca.py                      # tem de dizer PORTA_ABERTA
# 2. canario: 2 paginas, pela porta canonica (receita T9 -> envelope -> ingresso -> Admissao)
py orquestrador/orquestrador.py "colete anuncios dos concorrentes" --filtro fase=meta-anuncios --filtro universo=T9 --filtro pais=IT --filtro teto=2
# 3. a rodada inteira (23 paginas, ~2-3 min cada)
py orquestrador/orquestrador.py "colete anuncios dos concorrentes" --filtro fase=meta-anuncios --filtro universo=T9 --filtro pais=IT
# 4. paginas que faltam (Sipcam, Gowan, Ascenza, Certis Italia) -> so PROPOSTA
py coleta/meta_anunciante.py Sipcam Gowan Ascenza "Certis Belchim"
```

O estado da linha fica em `data/colheita/meta/` (`SNAPSHOTS/`, `COMPARACOES/`, `RAW/`, envelope por corrida), e
não vai para o Git. A **1.ª rodada é linha de base**: a comparação só existe a partir da 2.ª.

Ensaio feito aqui, sem Chrome:
- o orquestrador achou o envelope, respeitou `teto=2`, e a corrida saiu `FAILED` com `BROWSER_NOT_REACHED` e 0
  colheita (nada inventado);
- em linha de comando direta, 2 visitas deram `SLICE_FAILED` com o mesmo estado.

## 7 · Bateria — antes/depois pelo NOME

Base `554c1ec1` vs ramo `29a427a`, 285 módulos, rede fechada:

| | antes | depois |
|---|---|---|
| testes | 5.899 | 5.929 (+30, os novos) |
| vermelhos | 114 | 114 (os MESMOS, herdados) |

**NEW_FAILURES_BY_NAME = []** · CURADAS = [] · SO_ANTES = []. Na corrida intermédia (`fcecea8`) houve 3 novas, e ficaram assim:
- 2 eram os testes que exigem a declaração de um executor novo em T9: ajustados de forma declarada, ver §5;
- 1 era o carimbo, porque renomeei o passo do CI depois de regerar: fechado ao regerar.


## EM PALAVRAS SIMPLES

Em 31/08 alguém tirou **uma foto** dos anúncios que os concorrentes mostram na Itália pelo Facebook/Instagram. Essa
foto nunca chegou ao sistema. Agora há uma **máquina de fotografar** que se liga sempre que se quiser. Ela visita as
mesmas 23 páginas, uma vez cada, guarda a foto original e compara com a anterior. Só diz «apareceu» ou «sumiu»
quando as duas fotos foram tiradas com o mesmo cuidado. Os anúncios novos seguem pela porta normal até a Sala. Ela
**só funciona no computador do coordenador**, com Chrome aberto e VPN italiana; aqui na nuvem apenas se provou que
funciona com dados de ensaio. Aprendemos também que:
- os «414 anúncios» eram 414 cartões (601 anúncios);
- 11 deles eram de uma loja de motos;
- a página italiana da Syngenta nunca foi fotografada.
