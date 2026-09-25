# FUNIL-RESTO — o que sobra do funil, fonte a fonte

> Só leitura. Rede **fechada**. Nada escrito nos livros nem no serviço vivo.

| o que foi lido | onde | sha256 (16) |
|---|---|---|
| o plano do coordenador (06:40) | `%LOCALAPPDATA%/Temp/plano-agora.json` | `cde456ed3adb35b2` |
| livro do Curator, **vivo** | `source-curator-service-v1/curadoria/LIFECYCLE-LEDGER-V1.json` (sujo, 7cdb7ea4) | `b53743af25997319` |
| evidência do Curator, **viva** | `…/curadoria/LIFECYCLE-EVIDENCE-V1.json` | `5e34c76dd36feebc` |
| contratos do Curator (marca D9) | `…/curadoria/italy_contracts_curator.json` | `42f0d9afab997aa6` |
| rotas M3 | `…/curadoria/ROTAS-ELEGIVEIS-V1.json` | `850b3626f667447f` |
| contratos que o coletor carrega | `regras/italy_contracts.mjs` (lido pelo `node`) | — |
| receitas | `pedido/receitas.py` (`EXECUTORES`) | — |
| decisões | `auditoria-madrugada/DECISOES-DONO-2026-09-23.md` | `c077d2a3b2a9aebd` |

Leitura crua: `data/derivados/QUATRO-CHAVES-V1/funil-resto-leitura.txt`.

## 1 · As 22 SEM_RECEITA_WEB (T8 14 · T12 7 · T9 1)

**São TODAS páginas web. 0 YouTube, 0 rede social.** Prova: o endereço que o Curator validou
e abriu no canário, no livro vivo.

| grupo | fontes | o que são |
|---|---|---|
| T8 — revistas Edagricole | IT-T8-021, 022, 024, 028, 029, 030, 034, 039, 040, 041, 042, 051, 068 | Terra e Vita, Frutticoltura, Contoterzista, Informatore Zootecnico, Macchine Agricole News, Orticoltura, Suinicoltura, Vigne Vini e Qualità (13) |
| T8 — universidade | IT-T8-062 | `agrariaweb.uniss.it/it/notizie` (Univ. Sassari) |
| T12 — regiões / política agrícola | IT-T12-024, 104, 117, 129, 130, 131, 137 | Regione Veneto, Geoportale Lombardia, Calabria Impresa (energia), Regione Sicilia, Terra e Vita PAC/PSR (2), PSRN (Rete Rurale) |
| T9 | IT-T9-021 | `fieradidacta.indire.it` (feira Didacta) |

**Porque estão bloqueadas** (`pedido/receitas.py`, `EXECUTORES`, medido no vivo):

```text
T7  -> italia-recorrente (coleta/italy_executor.py)   ← web
T10 -> italia-recorrente (coleta/italy_executor.py)   ← web
T8  -> scrap-colheita  (so fases sociais: youtube, bluesky, telegram…)
T9  -> comunicacao-publica + scrap-colheita
T12 -> NENHUM executor
```

Uma página web de T8/T9/T12 não tem quem a colha pela porta canónica — **não é falta de fonte, é
falta de receita**. O próprio ficheiro já resolveu um caso igual para o YouTube: registou o mesmo
executor, por referência, noutro universo (`EXECUTORES["T8"] = … scrap-colheita`, com a lei
«TERRITORY ≠ PLATFORM ≠ ROUTE»). O mesmo gesto com `italia-recorrente` para T8/T9/T12 abre a
porta web **sem** dizer que «todo o T8 é web».

**Caminho pela onda social (`social-onda2-v1` @ `d7e31802`): 0 das 22.** Elas aparecem nesse ramo
só em ficheiros herdados da linha (contratos, gabaritos do detector de capa, funil da coorte) —
nenhuma rota social as nomeia.

**Quantas ficam prontas só com a receita:** as **10 que já têm contrato** — IT-T12-137, IT-T8-021,
028, 029, 030, 034, 039, 040, 051, IT-T9-021 (o plano não lhes aponta outra falta; a rota M3 está
`NAO_MEDIDA`, que o plano não conta como bloqueio). As outras **12 também não têm contrato**
(IT-T12-024, 104, 117, 129, 130, 131; IT-T8-022, 024, 041, 042, 062, 068) — são da bancada
CONTRATO-44 antes de serem desta.

⚠️ Relevância não medida aqui: várias Edagricole são zootecnia (Informatore Zootecnico,
Suinicoltura) — a saúde animal está fora do foco por decisão do dono (23/09). A receita abre a
porta; a Admissão decide item a item.

## 2 · As 6 HUMAN_REVIEW_REQUIRED

**O motivo é o mesmo nas 6:** `ITEM_PARECE_SECCAO` — o último pedaço do endereço do item aberto
tem menos de 4 palavras e nenhum número (`curadoria/collection_gate.py:90-100`,
`revisao_humana_do_url`). É uma **regra sobre o endereço**, não sobre a página.

| fonte | endereço do item | pela forma do endereço (não visto a olho) |
|---|---|---|
| IT-T2-143 | `sar.sardegna.it/…/2000/01.A/riepilogo.asp` | parece **item** (resumo mensal; os números estão antes) |
| IT-T7-170 | `conaf.it/news/conaf-crea-accordo/` | parece **item** (notícia) |
| IT-T7-174 | `conaf.it/news/assemblea-agronomi-udine/` | parece **item** (notícia) |
| IT-T3-053 | `regione.umbria.it/agricoltura/servizio-fitosanitario-regionale` | parece **secção** |
| IT-T5-064 | `dafnae.unipd.it/ricerca/assegni-di-ricerca` | parece **secção** (lista de bolsas) |
| IT-T8-050 | `noisiamoagricoltura.com/categorie/blog/curiosita-dalla-natura/` | parece **secção** (categoria) |

**A IA-CUR ou a revisão da R1 podem resolver pelo caminho canónico? Hoje, não por registo.** O
portão **não tem onde gravar** «uma pessoa viu e é item»: `avaliar()` (`:121-175`) recalcula a
cada vez a partir do endereço do último item aberto. O único caminho canónico que existe é o
Curator **voltar a medir** e abrir um item mais fundo (endereço com 4+ palavras ou número). Isso
serve às 3 «secção»; para as 3 que já parecem item, a regra é falso positivo e só um registo de
decisão humana — que não existe no portão — as libertava sem nova medição.

## 3 · As 5 RETIRADA_POR_DECISAO

**Decisão D9** — `DECISOES-DONO-2026-09-23.md:56`, decidida pelo bot Luciano por delegação
(23/09): aplicar a proposta de catálogo; **RETIRAR = marca `RETIRADA_POR_DECISAO`, reversível,
nunca apagar**; «se uma retirada tiver notícia com SINTONIA_RELEVANT=YES provada, vale D2
(REROUTE), não retirada». A marca e o motivo estão no contrato do Curator (`CATALOGO_D9`).

| fonte | motivo escrito (D9) |
|---|---|
| IT-T12-041 | boletim oficial geral: 0 de 3 com ato agrícola; «PAC» = Piano Attuativo Comunale |
| IT-T12-057 | juventude |
| IT-T12-074 | inovação e startups |
| IT-T12-086 | saúde |
| IT-T12-095 | hub de sítios regionais |

**Continua válida?** Sim, pelo que está escrito: nenhuma decisão posterior as reabriu (procurei as
5 nos relatórios e no ficheiro de decisões). O livro do Curator continua a dar as 5 como
`READY_FOR_COLLECTION` — a rota funciona; a retirada é de **relevância**, não de rota, e é por isso
que o portão a lê do contrato e não do livro. **Não medido:** se alguma delas tem notícia
`SINTONIA_RELEVANT=YES` provada (a exceção da D2).

## 4 · A 1 CAPABILITY_BLOCK — IT-T5-049 (UNICT Di3A, notícias)

**Capacidade que falta:** extrair **corpo útil** de uma página de notícia do tipo `MIXED`.
Prova (`ROTAS-ELEGIVEIS-V1.json`, verificação M3): os 2 alvos abertos
(`…/notizie/avvisi-lezioni`, `…/notizie/kit-di-sopravvivenza-…`) deram «alvo sem corpo útil:
HTML_KIND=MIXED» → `VEREDITO = CAPABILITY_BLOCK`.

⚠️ **Contradição a registar:** o livro vivo do Curator diz o contrário **depois** —
23/09 12:37 «canário resolveu, abriu um item real e passou o gate de detalhe (CAPA_NAO_E_MATERIA/v1)»
— e a Sala real já tem **4 itens** desta fonte (inventário SALA-PRONTA). O bloqueio vem da
fotografia M3 (filtro `88ce30a8` do plano), não do estado vivo. Resolver = **re-medir a M3** desta
fonte — exige rede: **ESPERA VPN / ordem**. Nota: os alvos amostrados são avisos de aulas e apoio
a estudantes; a relevância agrícola é duvidosa, e isso é da Admissão.

## Em palavras simples

- As 22 «sem receita» são sites normais. Falta só dizer ao sistema que o coletor de sites também
  serve para esses três grupos (T8, T9, T12). 10 ficariam prontas logo; as outras 12 ainda
  precisam de contrato.
- As 6 «revisão humana» são um aviso pelo formato do endereço. 3 parecem mesmo páginas de secção;
  3 parecem notícias normais. O portão não tem onde anotar «já vi, está bem» — hoje só sai com o
  Curator a medir de novo.
- As 5 retiradas foram tiradas de propósito (D9, 23/09): saúde, juventude, startups, etc. A
  decisão continua de pé.
- A 1 bloqueada não conseguiu ler o texto das notícias numa medição antiga; o Curator conseguiu
  depois. Precisa de ser medida outra vez, com rede.
