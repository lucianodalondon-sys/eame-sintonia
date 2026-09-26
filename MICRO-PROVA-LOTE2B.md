# MICRO-PROVA-LOTE2B · o leitor de prova consertado e 20 consorzi di difesa

Ramo **`micro-prova-lote2b-v1`**, a partir de `micro-prova-lote2-v1` @ `6c0207c4` (que desce do vivo `69b0e23f`).
Feito a 26/09 depois das 10:30, **sem rede**. Nada no vivo; a Sala não foi tocada.

## 1 · O defeito do lote 1, consertado (`curadoria/colher_prova_territorio.py`)

**O que estava errado.** A «página de conteúdo» escolhia-se SÓ pelo endereço: um ano ou 3 hífens bastavam.
Nos bytes reais do lote 1 (07:10), 7 das 9 «provas completas» tinham como conteúdo: o `favicon.ico` da TESAF (a
pasta do tema chama-se `unipd_2017`), a ajuda do Agriligurianet (`2013-04-04-08-54-42/help.html`), «Assicurazione
della Qualità» e «Struttura e sedi» (DAGRI), a taxa de publicação e a ética de uma revista (IJFS), a história e o
plano estratégico (Foggia), um formulário de «Segnalazioni» (D3A)…

**O conserto, em duas camadas:**
1. **Endereço** — fora: ficheiros estáticos (ico, svg, imagens, fontes, docx…), pastas de tema/assets, páginas de
   serviço (ajuda, qualidade, sedes, órgãos, história, plano estratégico, transparência, taxa, ética, didática,
   cursos, newsletter…); o ano tem de estar solto (`tema_2017` não conta). Ordem: primeiro o que tem data no
   endereço, depois o que tem cara de notícia/comunicado/boletim (com o teto de 5 pedidos só há 2–3 tiros).
2. **Os bytes decidem** — `juizo_de_conteudo`: é HTML; tem **≥ 600 letras** de texto sem menu, cabeçalho e rodapé;
   e tem **data de publicação** (metadados, `<time>`, endereço, título ou início do texto). **A data de hoje não
   conta** — é o aviso do dia no topo do site (LaMMA mostra «Sabato 26 Settembre 2026» em todas as páginas).
   A página que falha fica em `REJEITADAS` (bytes guardados + motivo), **nunca** em `PROVAS`.
   A institucional com **< 300 letras** também não completa a prova (Foggia: 14; Laimburg: 35; Veneto Agricoltura: 8).

**Calibrado nos bytes reais do lote 1:** as 4 páginas dos Condifesa (Ravenna, TVB) **passam**; as 14 erradas são
barradas por pelo menos uma das camadas; a notícia da FEM (Noce da frutto, 24/09) também passa.
Testes `test_colher_prova_territorio` **27/27** (eram 8); mutação **11/11 mortas** — na 1.ª volta 6 sobreviveram:
4 eram testes fracos meus (um endereço de teste tinha «ricerca», que contém «cerca», e nunca chegava à regra), 2
eram código repetido (duas guardas de binário que faziam o mesmo; ficou a do byte NUL).

## 2 · O LOTE 2B (`curadoria/MICRO-PROVA-LOTE2B.json`) — 20 consorzi di difesa

**Porque não os da lista 1 da GAPS:** as 20 fito/agrometeo da lista 1 **já têm SOURCE_ID** (IT-T2-136 … IT-T3-058) —
estão paradas no **canário** (receita de página), não no território. A micro-prova só serve a quem ainda não tem
número. **Porque não outras da porta:** as únicas fito/agrometeo sem número e sem recusa são a Condifesa Lombardia
Nord-Est e a FEM (visitadas hoje no lote 1), contas sociais (política) e cascas JS (Laimburg, Veneto Agricoltura).

**Então:** os consorzi da lista 2 da GAPS (lista Asnacodi, P1g 24/09) — **nenhum está na porta**. Vão como
`FICHAS_NOVAS` com id provisório `L2B-01..20`; **só se registam na porta os que a prova aprovar** (passo 9B), para não
encher a fila com consórcios de seguro que não publicam aviso nenhum. ⚠️ Esperar poucos SIM (a própria GAPS avisa).

| ID | Região | Consórcio | Última data na página (P1g) |
|---|---|---|---|
| L2B-01 | Puglia | Condifesa Foggia | 2026-09-24 |
| L2B-02 | Calabria | CODIPACAL | 2026-09-18 |
| L2B-03 | Emilia-Romagna | Condifesa Modena | 2026-09-17 |
| L2B-04 | Piemonte | Condifesa Vercelli Biella | 2026-09-16 |
| L2B-05 | Lombardia | Condifesa Brescia | 2026-08-12 |
| L2B-06 | FVG | Condifesa FVG | 2026-07-31 |
| L2B-07 | Lombardia | CODIMA Mantova | 2026-06-30 |
| L2B-08 | Trentino | CODIPRA Trento | 2026-06-30 |
| L2B-09 | Piemonte | Condifesa Cuneo | 2026-06-30 |
| L2B-10 | Emilia-Romagna | Condifesa Emilia | 2026-06-18 |
| L2B-11 | Puglia | Agridifesa del Mediterraneo | 2026-05-15 |
| L2B-12 | Umbria | Condifesa Umbria | 2026-05-15 |
| L2B-13 | Piemonte | COSMAN Piemonte | 2026-05-15 |
| L2B-14 | Alto Adige | Hagelschutzkonsortium | 2026-04-24 |
| L2B-15 | Lombardia | COPROVI | 2026-04-03 |
| L2B-16 | Veneto | CODIVE | 2026-04-02 |
| L2B-17 | Lombardia | Condifesa Lombardia (federazione) | 2025-11-16 |
| L2B-18 | Abruzzo | CODIPE | nenhuma |
| L2B-19 | Toscana | CODIPRA Toscano | nenhuma |
| L2B-20 | Basilicata | Condifesa Basilicata | nenhuma |

**Fora (10):** os 5 com robots ilegível na P1g (condifesa.it, Ancona-Macerata, Cagliari, Piemonte, Veneto Est —
1 pedido e param) e 5 sem data cuja região já tem consórcio no lote (Milano Lodi, Sassari, Catania, Novara, Oristano).

## 3 · Colisão = 0 (medida contra o VIVO)

`micro_prova_colisao.py --vivo=<vivo>`: 20 domínios distintos; **RODADA 1 da 4.ª onda: 38 domínios, 0 em comum**;
**colhidos pelo coletor nas últimas 24 h: 33 domínios, 0 em comum**; 0 em comum com o lote 1 de hoje; 0 de
CNR/Coldiretti/ANGA/Unaprol. ⚠️ Sem `--vivo`, a ferramenta lia as observações da árvore onde corre — na cópia do
meu ramo são antigas (521 linhas contra 678 no vivo) e davam «0 domínios» às cegas. O teu clone `C:/g/mprova`
tinha as do vivo (a última colheita, 25/09 22:58 UTC, é igual): **o lote 1 foi conferido bem**. A partir de agora,
`--vivo` sempre.

## 4 · O COMANDO (coordenador, VPN IT; o robô pode continuar ligado — nada disto escreve livro)

```bash
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
M=C:/g/mprova
S=C:/Users/London1/sintonia-sala-italia/micro-prova/lote2b-$(date +%H%M) ; mkdir -p $S
git -C $M fetch origin micro-prova-lote2b-v1 && git -C $M rev-parse FETCH_HEAD   # = o SHA do relatório
git -C $M checkout --detach FETCH_HEAD            # os livros copiados no clone não mudam (o ramo não lhes toca)
cd $M
py superficie/rede.py --portao-de-egresso IT | tee $S/PORTAO-ANTES.txt       # EGRESS_GATE=PASS, senão PARAR
py curadoria/micro_prova_colisao.py --rodadas=C:/Users/London1/auditoria-madrugada/C2-ONDA4/rodadas.txt \
   --lote=curadoria/MICRO-PROVA-LOTE2B.json --vivo=$V                          # código 0, PODE_CORRER true
py curadoria/colher_prova_territorio.py --lote=curadoria/MICRO-PROVA-LOTE2B.json --vivo=$V \
   --bytes=$S/provas-lote2b --saida=$S/PROPOSTAS-LOTE2B.json | tee $S/stdout.txt
py superficie/rede.py --portao-de-egresso IT | tee $S/PORTAO-DEPOIS.txt
```
≤ 5 pedidos por domínio (teto D38), 20 domínios → **≤ 100 pedidos**, pausa de 3 s → ~10 min. Portão antes de cada
consórcio; robots lido e cumprido. **Nada é registado, nada vai para RAW nem para a Sala.**

**Depois (sem rede):** eu leio os bytes e escrevo `DECIDIDAS-LOTE2B.json` só com as provas que aguentam leitura;
o passo 9B (robô parado) regista pela porta **só essas**, aplica a decisão pelo validador do canal e enfileira o
QUALIFY de cada uma — script entregue com a decisão.

## 5 · O passo 9 genérico (`curadoria/micro_prova_passo9.py`) — pronto, testado

Robô PARADO (`PARAR.flag`, senão recusa). Copia o canal e a porta do vivo para ao lado das DECIDIDAS (sha256);
para cada decisão com id provisório **passa primeiro pelo validador do canal** e só então regista pela porta do
vivo (`fonte_nova.registar`, PAIS da prova, `ID_PROVISORIO` na NOTA); aplica pelo canal; enfileira o QUALIFY das
novas e reabre **só** a tarefa barrada das que já estavam na porta. Os módulos da porta/fila/canal são os DO VIVO.
Testes 5/5; mutação 3/4 (a que sobrevive é redundante: o validador também barra o «A_DECIDIR»).

## 6 · LOTE 3 (`curadoria/MICRO-PROVA-LOTE3.json`) — 10, não 20: não há mais deste tipo sem número

Pedido: 20 servizi fitosanitari regionais + agrometeo com cultura. **Medido nos livros** (P1g: 90 células; GAPS
VARRIDO; DISCOVERY-VISITED/SIGNAL do vivo): dos **56** fito/agrometeo regionais da P1g, **todos os abertos já têm
SOURCE_ID** (IT-T2-…, IT-T3-…) — estão parados no **canário** (receita de página), não no território, e a
micro-prova não os ajuda. Os sem número estão **fechados por robots**: Lombardia SFR (proíbe), Puglia SIT e
emergenzaxylella (302), SIAS Sicília, Beratungsring, meteo VdA, IAR, fitosanitario.venezia.it. As restantes pistas
do tipo (46 endereços em 19 domínios) são **páginas de sites que já são fonte** (ERSA, ARPAE, arsacweb,
regione.veneto…) — servem para **trocar a entrada** dessas fontes, não para fontes novas.
**Então o LOTE 3 são os 10 consorzi que sobram da lista Asnacodi:** 5 sem data (Milano Lodi, Sassari, Catania,
Novara, Oristano) e 5 com robots ilegível a 24/09 (condifesa.it, Ancona-Macerata, Cagliari, Piemonte, Veneto Est —
re-medir: falha de ligação não é fonte morta; se continuar ilegível, 1 pedido e para). **Colisão 0** (vivo: 33
domínios em 24 h, 38 na rodada 1). ⚠️ **CODIPRA:** `codipra.it` já é **IT-T3-063**; o `codipratn.it` do lote 2B
(L2B-08) pode ser a mesma organização — confiro na decisão antes de dar número.
Comando: o mesmo do §4 com `--lote=curadoria/MICRO-PROVA-LOTE3.json` e `S=…/lote3-$(date +%H%M)`
(≤ 5 pedidos por domínio, ≤ 50 pedidos).

## EM PALAVRAS SIMPLES

- **O conserto:** o programa que junta provas aceitava qualquer página cujo endereço tivesse um ano — até o ícone do
  site. Agora ele **lê a página**: só conta se tiver texto de verdade e uma data de publicação (que não seja a de
  hoje, porque essa é o aviso do dia no topo do site). Testado com as páginas reais de hoje: as 4 boas passam, as
  14 ruins são barradas.
- **O lote 2B:** 20 consórcios de defesa (os «Condifesa» de outras regiões). A lista 1 da GAPS não servia: aquelas
  fontes já têm número; o problema delas é outro.
- **Nada colide** com a 4.ª onda nem com o que o robô colheu nas últimas 24 horas — medido no registro do robô vivo.
- **Esperar poucos SIM:** muitos consórcios só vendem seguro contra granizo e não publicam avisos. Só os que
  provarem que publicam entram no cadastro.
