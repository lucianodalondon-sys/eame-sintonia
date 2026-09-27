# INTEGRA-NOITE · LOTE 4 — sobre o vivo `554c1ec1` (lote 3)

Ramo `integra-noite-v4`, a partir do vivo **`554c1ec1`** (lote 3, instalado 22:25 — é a base, aviso da coordenação).
**NÃO instalado.** Estado: **PARADO em 2 decisões** (§3) — 8 pacotes juntos; mapa na FILA-PESADO (7.º).

## 1 · Os pacotes

| # | pacote | SHA | base | junção |
|---|---|---|---|---|
| 1 | contador-24h-v1 | 4552a305 | dc0de726 | limpa |
| 2 | scrap-evolucao-v1 | 3103f723 | dc0de726 | limpa · **peça 6 DESLIGADA**: `coleta/scrap_capacidades.EMENDAS_EM_VIGOR = frozenset()` (a peça só liga com `COL-LAW-220` lá dentro) |
| 3 | lista-mestra-v1 | 3f7b43ef | dc0de726 | limpa |
| 4 | pesq-fora-do-mur-v1 | 389f9879 | 278cd489 | ficha do mapa: + peça `C-SEGUIR-PESQUISADORES` (só acréscimos, 0 dúvidas) |
| 5 | nuvem-polso-mercato-v1 | 89020be4 | 278cd489 | só gerados |
| 6 | nuvem-voci-campo-v1 | 7c975a9c | dc0de726 | limpa |
| 7 | nuvem-concorrenza-v1 | 778c21ff (último SHA) | dc0de726 | limpa |
| 8 | nuvem-independencia-v1 | eb3a7b1d | dc0de726 | só gerados |
| — | **micro-prova-lote2b-v1** | **005a24cd** (o pedido; a ponta do ramo andou para `94d36a64`, 22:03) | 278cd489 | **PARADO — conflito de CÓDIGO**, §3.1 |
| — | **lei-pesquisadores-v1** | 94524616 (PRONTO-SEM-MAPA 22:04) | dc0de726 | **PARADO — conflito de CÓDIGO**, §3.2 |
| — | t6-para-sala-v1 | ff9ba9f2 | — | FORA: PRONTO-SEM-MAPA com o ensaio na cópia da Sala **não medido** (é o 1.º da FILA-PESADO) e uma pergunta ao dono (T5 ou T6) |
| — | nuvem-rotulos-t4-v1 · nuvem-int-casco-ponte-v1 | 381a8a3c · 780fa38a | — | FORA até confirmação: têm relatório e mapa, mas nenhum diz PRONTO (o int-casco-ponte deixa uma decisão ao dono) |

Migrações: **nenhuma** no writeset (`supabase/` intocado).

⚠️ A ficha do mapa agora junta-se por `ficha_juntar.py` (fora do Git): conflito na ficha resolve-se sozinho só com
**0 dúvidas** (só acréscimos do pacote sobre a base comum); remoção, peça apagada ou campo em conflito PARAM a junção.

## 2 · Testes por NOME (em curso)

Contra o vivo `554c1ec1`, mesmos dados, rede fechada, pastas com o nome do vivo; +15 módulos e 1 prova Node do lote 4.

## 3 · ⛔ Duas decisões

**3.1 · micro-prova-lote2b × scrap-evolucao — `curadoria/colher_prova_territorio.py` (3 blocos).**
O scrap-evolucao pôs a rota de navegador (`rota_navegador`, `ROTA_HTTP` em cada prova); o micro-prova pôs
`REJEITADAS` (guardadas para auditoria, nunca contam como prova) e o juízo dos bytes (prova só com conteúdo
PUBLICADO). **Proposta (não aplicada; ficheiro em `C:/cur/t2b/proposta-colher_prova_territorio.py`, sha256
`5db89ce5…`):** ficam os dois — os dois caminhos de import; `out` com `REJEITADAS` **e** a proveniência da rota; a
linha da prova (e da rejeitada) leva `ROTA_HTTP`. Medido nessa proposta: `test_colher_prova_territorio` **28/28**,
`test_micro_prova_passo9` OK, **`test_scrap_evolucao` 36/37**: falha
`test_ficha_com_rota_navegador_pede_por_ela_e_cada_prova_o_diz` porque as páginas FALSAS do teste têm 17–24 bytes
e o juízo novo do micro-prova recusa-as («institucional quase vazia (0 letras < 300)», «nao e pagina HTML») — o
código está coerente; o teste do scrap-evolucao ficou velho. **Proposta 2:** as páginas do teste passam a ter
conteúdo publicado (HTML com texto e data); o que o teste mede (a rota em cada prova) não muda.

**3.2 · lei-pesquisadores × scrap-evolucao — `coleta/scrap_http.py` (1 bloco, só o comentário do topo).**
Os dois reescreveram o «O QUE ESTE FICHEIRO NAO FAZ» por causa da D88: o scrap-evolucao diz que a lei passou para a
`COL-LAW-704` da Bíblia e que a cara de navegador é a peça `coleta/rota_navegador.py`; a lei-pesquisadores diz
`COL-LAW-220` («proposta à espera do dono») e que «o comportamento deste ficheiro não mudou» — o que deixa de ser
verdade depois do scrap-evolucao. Escolher qual lei o comentário cita é conteúdo. A lei-pesquisadores **não** mexe
em `EMENDAS_EM_VIGOR`: juntá-la **não liga** a peça 6.

## 4 · Falta

decisões → juntar os 2 → bateria por nome outra vez → mutação → mapa UMA vez na minha vez da FILA-PESADO (7.º) → plano
A/B → PRONTO.
