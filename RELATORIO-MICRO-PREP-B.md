# RELATÓRIO — MISSÃO 6-PREP-b · O FILTRO DA 3b A SÉRIO, E O DETECTOR DE CAPA MEDIDO

Branch `micro-prep-v1`, a partir de `0ca000d6`. Motor: `claude-opus-5-5`.

```
NETWORK_REQUESTS = 0 · DB_WRITES = 0 (só SELECT, default_transaction_read_only=on)
DETECTOR DE CAPA  = NÃO ALTERADO · ADMISSION / RÉGUA / CONTRATOS = intocados
```

---

## 1 — O FILTRO DA 3b: O MEU PALPITE ESTAVA ERRADO, E CALADO

O coordenador mediu: a 6-PREP lia `curadoria/RELEVANCIA-POR-FONTE-V1.json` com
a forma `{"LINHAS": [...]}` — nome e forma **inventados por mim** — e tratava
ficheiro ausente como «sem opinião». A 3b real escreveu outro ficheiro, com
outra forma. **Filtro da 3b aplicado = nenhum, sem aviso.** O filtro da M3
tinha o mesmo buraco: lia um ficheiro que não existe nesta linha.

### O que mudou (`scripts/micro_coleta/micro_coleta.py`, bloco FILTROS)

* **Lê o ficheiro real, da branch do dono, por `git show`**, sem merge, pelo
  **nome da branch** (não por um hash fixo, que mataria o filtro futuro em
  silêncio). O hash resolvido sai no plano: M3 `88ce30a8`, 3b `3b5080b9`.
* **A decisão por fonte, com regra escrita.** O JSON da 3b
  (`curadoria/RELEVANCIA-ELEGIVEIS-V1.json`) **não tem veredito de coorte**: tem
  2 amostras por fonte com o `DECIDIR` de cada uma. A decisão é do dono da 3b e
  está na coluna «coorte» do relatório dele
  (`RELATORIO-RELEVANCIA-ELEGIVEIS.md`). Derivar das amostras daria **outra
  coorte** — a myfruit tem 2 amostras NAO_SEI e ENTRA (histórico 5/9 na Sala);
  a feira escolar tem 2 SIM e FICA_FORA. Seria a minha decisão por cima da
  dele. Por isso:

  ```
  ENTRA_NA_MICRO                → passa
  qualquer outra decisão        → bloqueia (RELEVANCIA:<decisão>)
  fonte que a 3b não mediu      → bloqueia (RELEVANCIA_NAO_MEDIDA_PELA_3b)
  relatório e JSON com fontes diferentes → FALHA ALTA
  ```

  As contagens das amostras vão ao lado, em cada linha do plano
  (`AMOSTRAS_3b`), para quem quiser ver onde o dono discordou da régua.
* **FILTRO DECLARADO E AUSENTE = FALHA ALTA.** Ficheiro ausente, ilegível, de
  forma inesperada, vazio ou desencontrado → `FiltroAusente`; o `plano` e o
  `correr` saem com **código 3** e dizem que ficheiro falta. Nada é lançado.
* **A 3c (régua T2/T12)** ainda não publicou no remoto (`regua-t2-t12-v1` não
  existe em `origin`). O ponto de leitura está **declarado e desligado** em
  `FILTROS` (`M3c-REGUA-T2-T12`, `ATIVO: False`) e o plano lista-o como
  `DESLIGADOS`. Não adivinhei nome nem forma: liga-se quando a branch publicar.

### Provas

```
23/23 provas verdes, 0 saltadas.
Mutantes (cada um tem de pôr uma prova a vermelho):
  «ausente = sem opinião» (o defeito antigo, reposto)   → 6 vermelhos
  fonte não medida pela 3b passa                        → 1 vermelho
  relatório e JSON sem conferência                      → 1 vermelho
  FICA_FORA ignorado                                    → 1 vermelho  (sobreviveu
                                                          à 1.ª bateria; acrescentei a prova que faltava)
  RENOMEAR o ficheiro da 3b no código                   → 7 vermelhos, e `plano` sai com 3:
     FILTRO_AUSENTE — origin/relevancia-elegiveis-v1:curadoria/RELEVANCIA-POR-FONTE-V1.json:
     fatal: path ... does not exist
```

```
RELEVANCE_FILTER_READS_REAL_FILE = YES
MISSING_FILTER_FAILS_LOUD        = YES (mutação: renomear → exit 3 e 7 provas vermelhas)
```

### A coorte depois da 3b

| SOURCE_ID | decisão da 3b | outros bloqueios | estado |
|---|---|---|---|
| **IT-T10-018** myfruit | ENTRA_NA_MICRO | — | **PRONTA** |
| IT-T10-022 Zootecnica | FICA_FORA (inglês) | — | bloqueada |
| IT-T7-043 Agrofarma | NAO_SEI | — | bloqueada |
| IT-T2-034 · T2-051 · T2-056 | FICA_FORA (sem régua T2) | sem contrato | bloqueadas |
| IT-T12-041 · T12-057 · T12-074 | FICA_FORA (sem régua T12) | sem contrato, sem receita | bloqueadas |
| IT-T9-021 | FICA_FORA (feira escolar) | sem contrato, sem receita web | bloqueada |
| IT-T10-021 · IT-T7-021 | **não medida** pela 3b | — | bloqueadas |
| IT-T5-041 · IT-T5-049 | **não medida** pela 3b | rota UNKNOWN / CAPABILITY_BLOCK | bloqueadas |

```
COHORT_AFTER_3b = 1  (IT-T10-018)
```

⚠️ **Duas fontes com tudo o resto pronto ficam fora só porque a 3b não as
mediu** (IT-T10-021 Plantgest, IT-T7-021 Villoresi). É fail-closed de
propósito: relevância que ninguém mediu não é relevância aprovada. Se o dono
quiser que entrem, é a 3b que as mede, não o instrumento que as deixa passar.

---

## 2 — O DETECTOR DE CAPA

```
CAPA_DETECTOR_OWNER = curadoria/retrato_html.py:80  (kind_de — a regra)
                      curadoria/retrato_html.py:113 (gate_capa_nao_e_materia — o portão)
                      limiares em :45-47 (PARAGRAFO_MINIMO 800 · FRACCAO 0.35 · 40 caracteres/ligação)
```

O próprio ficheiro declara gémeos com os **mesmos** limiares:
`coleta/retrato_html.mjs` (existe só noutra branch, commit `b3099bd5`) e
`executor_texto_de_html.py::_kind` «na outra linha» — nesta árvore
`coleta/executor_texto_de_html.py` **não** tem `_kind`. Nesta linha o dono é um
só. Uma mudança teria de mudar os gémeos no mesmo passo — «um gate com limiares
diferentes do coletor julgaria outra página».

### Os 6 do lote-76 e a «capa» de 21/09, lidos um a um

| raw | derived | fonte | o que é, lido | data | veredito humano | o detector |
|---|---|---|---|---|---|---|
| 1361 | 870 | IT-T7-017 | Riunite no Raduno degli Alpini (wine-truck) | 24/10/2025 | **MATÉRIA** | CAPA |
| 1374 | 869 | IT-T7-017 | prémios dos vinhos Cavicchioli (Tre Bicchieri, Falstaff) | — | **MATÉRIA** | CAPA |
| 1375 | 879 | IT-T7-017 | Cavicchioli no Merano Wine Festival | — | **MATÉRIA** | CAPA |
| 1381 | 895 | IT-T7-033 | «E-learning: vuoi diventare un esperto di Chianti Classico?» | 07/11/2024 | **MATÉRIA** | CAPA |
| 1395 | 884 | IT-T7-033 | Chianti Classico Collection 2026 (anúncio do evento) | 17/12/2025 | **MATÉRIA** | CAPA |
| 1396 | 902 | IT-T7-042 | web app «Modena Balsamic Genius» | 22/09/2026 | **MATÉRIA** | CAPA |
| — | — | IT-T7-033, 21/09 | **é o raw 1381**: mesmos números (88 ligações, 1.920 caracteres, 646 em parágrafos) | | **MATÉRIA** | CAPA |

Os seis têm a mesma forma: **corpo curto** (522–786 caracteres em parágrafos,
abaixo dos 800) dentro de um **menu grande** (66–93 ligações), o que dá 20–26
caracteres por ligação — abaixo dos 40 — e o detector conclui NAVIGATION.

### Taxa de erro, nos dois sentidos

| conjunto | N | veredito humano | o detector hoje |
|---|---|---|---|
| lote-76 (bytes brutos, sha256 conferido) | 76 | 76 matérias individuais | 68 MATÉRIA · 2 NAO_SEI · **6 CAPA** |
| páginas de índice da M3 (só o retrato) | 14 | 14 capas/listagens¹ | 6 CAPA · 3 NAO_SEI · **5 MATÉRIA** |

```
FALSE_CAPA   = 6/76    matéria chamada capa (o erro que eu tinha visto)
FALSE_MATERIA = 5/14   capa chamada matéria — O ERRO MAIS GRAVE, e eu não o tinha visto:
                       bura.regione.abruzzo.it · giovani.regione.lombardia.it ·
                       openinnovation.regione.lombardia.it · chianticlassico.com/news/ ·
                       fieradidacta (¹)
CAPA QUE ATRAVESSA O PORTÃO = 8/14 — o portão só reprova NAVIGATION; MIXED (NAO_SEI) também passa
```

¹ ⚠️ **Limites destes números, declarados.**
* As 14 capas são o `NEGATIVE_CONTROL` que a M3 mediu **com egresso BR**; eu
  não tenho os bytes, só o retrato que ela gravou. Não os remedi.
* IT-T9-021: o `INDEX_URL` do contrato é uma página de evento
  («visita-didacta-italia-edizione-abruzzo»), não uma listagem óbvia. Sem ela:
  **FALSE_MATERIA = 4/13**, atravessam 7/13.
* O conjunto de matérias é todo de 4 fontes de marca/mercado; não sei como o
  detector se porta noutros sites.

### PROPOSTA (não aplicada) — uma mudança só: a MORADA antes da estrutura

**O critério que falha:** o detector julga **só a estrutura** (quantos
caracteres em parágrafo, quantas ligações). A estrutura não separa as duas
coisas: as capas verdadeiras que ele apanha têm 21,6–38 caracteres por ligação;
as notícias que ele chama capa têm 20–26. **Nenhum limiar de tamanho resolve**
— baixar `PARAGRAFO_MINIMO` para 500 recupera só **2 das 6** (as outras 4 têm
entre 32% e 34,9% do texto em parágrafos e falham a fracção de 0,35), e não
toca nas 5 capas chamadas matéria.

**A proposta:** o contrato de cada fonte **já declara** a forma da morada de um
item de detalhe (`ACQUISITION.LINK_PATTERN`) e a da capa (`INDEX_URL`). O
portão passaria a perguntar primeiro isso:

```
morada NÃO casa LINK_PATTERN, ou é o INDEX_URL   → CAPA
morada de detalhe + estrutura NAVIGATION         → NAO_SEI (uma pessoa lê)
morada de detalhe + outra estrutura              → o que a estrutura disser
```

**O número que ela mudaria** (`py scripts/micro_coleta/medir_detector_de_capa.py`):

| | hoje | com a proposta |
|---|---|---|
| matéria chamada capa (76) | 6 | **0** (as 6 passam a NAO_SEI: visto humano) |
| capa chamada matéria (14) | 5 | **0** |
| capa apanhada (14) | 6 | **14** |
| capas verdadeiras que hoje acerta e continua a apanhar | 6/6 | **6/6** |

⚠️ **O que esta proposta NÃO prova, e porquê:**
* nos 76, a morada casa o `LINK_PATTERN` em **76/76 por construção** — foram
  colhidos precisamente por casarem. Esse lado da medição é quase circular.
* ela confia no contrato: um `LINK_PATTERN` largo demais (que deixe passar
  `/news/page/2`) faria uma listagem ser julgada pela estrutura — e cairia, no
  pior caso, em NAO_SEI ou MATÉRIA. Custa rever os padrões das fontes da coorte.
* `gate_capa_nao_e_materia(contrato, retrato)` hoje **não recebe a morada**;
  a mudança acrescenta um argumento, e os gémeos (`.mjs` e `_kind`) teriam de
  mudar no mesmo passo.

```
PROPOSED_FIX = morada antes da estrutura (LINK_PATTERN / INDEX_URL do contrato);
               FALSE_CAPA 6/76 → 0/76 (6 NAO_SEI) · FALSE_MATERIA 5/14 → 0/14 ·
               capas apanhadas 6/14 → 14/14 · NÃO APLICADO. Dono: curadoria/retrato_html.py.
```

---

## 3 — R1, ACTUALIZADO

```
R1 = PROTEGIDO POR CÓPIA, NÃO RESOLVIDO.
     O coordenador copiou lote-76-v1/XX (76 ficheiros, 7,4 MB) para
     C:/Users/London1/sintonia-acervo-backup/lote-76-XX-20260922,
     sha256 idênticos 76/76 (lista em ../lote-76-XX-SHA256.txt). Mesmo disco.
     ⚠️ A cópia guarda o CONTEÚDO de XX/ (começa em it-t10-018/…), e o
        raw_asset.storage_path começa em «XX/…». Para a usar como armazém é
        preciso uma raiz com XX/ por cima — apontar SINTONIA_ARMAZEM_RAIZ para
        a pasta da cópia dá SEM_BYTES em 76/76.
     O armazém oficial continua com 2/76. Resolver é da unificação.
```

---

## SYSTEM MAP

Ficheiro de código novo: `scripts/micro_coleta/medir_detector_de_capa.py`,
declarado na peça `C-MICRO-COLETA-INSTRUMENTO`. Ver a entrega para o resultado
da cadeia.

---

## ENTREGA

```
RELEVANCE_FILTER_READS_REAL_FILE = YES   (git show origin/relevancia-elegiveis-v1 @ 3b5080b9)
MISSING_FILTER_FAILS_LOUD        = YES   (renomear → exit 3; 5 mutantes mortos; 23/23)
COHORT_AFTER_3b                  = 1     (IT-T10-018)
CAPA_DETECTOR_OWNER              = curadoria/retrato_html.py:80 (kind_de) · :113 (portão)
FALSE_CAPA                       = 6/76
FALSE_MATERIA                    = 5/14  (4/13 sem a IT-T9-021, cujo índice é duvidoso)
PROPOSED_FIX                     = morada antes da estrutura — não aplicado
R1                               = actualizado (cópia 76/76; raiz sem XX/)
```

---

## EM PALAVRAS SIMPLES

**Primeira coisa: um filtro que eu tinha montado estava a dormir.**
Outra equipa (a 3b) diz que fontes valem a pena. Eu tinha adivinhado o nome do
papel onde ela ia escrever — e adivinhei mal. Pior: quando o papel não
aparecia, o meu programa seguia em frente como se estivesse tudo bem. Agora ele
lê o papel verdadeiro e, se o papel faltar, **pára e grita**. Testei tirando o
papel do sítio: parou e disse qual faltava. Com o filtro a funcionar, das 14
fontes sobra **1** pronta para colher: o site de preços de fruta (myfruit).

**Segunda coisa: o detector de "capa" erra para os dois lados.**
É ele que separa uma notícia de uma página de índice (a primeira página de um
site, cheia de links).
- Chama **capa** a notícias curtas: 6 em 76. É como achar que um bilhete é um
  catálogo só porque vem dentro de um envelope cheio de publicidade.
- E, mais grave, chama **notícia** a páginas de índice: 5 em 14. Isso deixa
  entrar coisa vazia como se fosse matéria.

O problema é que ele só olha o **formato** da página. Proponho que olhe primeiro
a **morada**: cada site já nos disse como é a morada de uma notícia. Nos
números que tenho, isso zerava os dois erros. Não mudei nada — é só proposta, e
tem um ponto fraco que está escrito no relatório.

**Terceira coisa:** a cópia de segurança das 76 notícias que o coordenador fez
está boa (76 de 76 iguais), mas está guardada numa pasta com um nível a menos
do que o programa espera. Se um dia for precisa, alguém tem de saber isso.
