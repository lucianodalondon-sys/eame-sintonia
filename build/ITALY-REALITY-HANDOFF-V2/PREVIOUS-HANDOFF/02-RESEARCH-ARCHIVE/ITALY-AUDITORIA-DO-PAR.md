# AUDITORIA — pares cultura × alvo, rótulo italiano ADAMA

**Arquivo auditado (somente leitura):** `data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json`, encontrado em `origin/claude/adama-it-local-catalog`. Cópia de trabalho: `C:\eame-sintonia\.wfaudit.json` (278.429 bytes). Nada foi escrito no repositório.

**Contadores internos conferem:** 163 produtos, 49 linhas de uso, 90 pares distintos, 13 linhas com dose. Recontei os 90 pares a partir das 49 linhas e deu 90. O arquivo não mente sobre si mesmo — o problema está em como os pares foram montados.

---

## 1. Pares biologicamente incompatíveis — SIM. 27 dos 90 (30,0%)

O mecanismo é o mesmo do Brasil, mas ao contrário: lá o apelido casou com o nome científico errado; aqui **a linha do rótulo tem VÁRIAS culturas e o sistema escolheu UMA e deu todos os alvos para ela**. Em 21 das 49 linhas o próprio campo `EVIDENCE` cita mais de uma cultura.

### CLASSE A — provado dentro do próprio texto guardado

**A1. POTATO × Agrotis spp** — `LEBRON 0.5 G` (008189) e `SCHERMO 0.5 G` (014479)
Evidência completa (82 caracteres, não truncada):
> `Patata Agriotes spp. 12-15 Tabacco Agriotes spp., Agrotis spp., Tipula spp. 12-15`

A batata tem **só Agriotes**. *Agrotis* está na linha do **Tabacco** (fumo). O sistema colou o alvo do fumo na batata — e perdeu o fumo, que nem existe como cultura no arquivo.

**A2. APPLE × Myzus persicae / Brachycaudus helichrysi / Hyalopterus pruni** — `APYZA WG` (018156) e `APYZA 500 WG` (018165)
> `melo (Dysaphis plantaginea). Non effettuare più di 3 trattamenti/anno com un intervallo di 14 giorni tra le applicazioni. Pesco e susino: contro afidi (Myzus persicae, Brachycaudus helichrysi, Hyalopterus pruni) intervenire all'inizio dell'`

A frase da macieira fecha com ponto final em *Dysaphis plantaginea*. Os três pulgões estão dentro da frase seguinte, **"Pesco e susino"** (pessegueiro e ameixeira). *Hyalopterus pruni* é o pulgão-farinhento da ameixeira. O corte da frase é visível dentro do trecho guardado — não depende do que veio depois. **Este é o caso Nabo-bravo em forma italiana.** 3 pares × 2 produtos.

### CLASSE B — atribuição insustentável: 18 culturas numa linha só

**B1. TOMATO × 8 alvos** — `LEBRON 0.5 G` e `SCHERMO 0.5 G`
> `Pomodoro, Melanzana, Rapa, Navone, Melone, Cetriolo, Cocomero, Finocchio, Sedano, Dolcetta/valerianella/ gallinella, Crescione, Rucola, Barbarea, Senape juncea, Fagiolo, Fagiolino, Pisello, Carota Agriotes sp., Agrotis sp., Ceutorhynchus pl`

A linha lista **18 culturas** e depois a lista de alvos. O sistema gravou `CROP=TOMATO` e deu os 8 alvos ao tomate:

| par gravado | de quem o alvo realmente é |
|---|---|
| TOMATO × *Chamaepsila rosae* | mosca-da-cenoura → **Carota** |
| TOMATO × *Delia radicum* | mosca-da-raiz-das-brássicas → Rapa / Navone / Rucola / Barbarea |
| TOMATO × *Ceutorhynchus pleurostigma* | gorgulho-da-galha das brássicas → mesmas brássicas |
| TOMATO × *Chaetocnema tibialis* | altica da beterraba |
| TOMATO × *Blaniulus guttulatus*, *Melolontha melolontha*, *Agriotes sp*, *Agrotis sp* | polífagos de solo, sem dono definido nessa linha |

Nenhum desses 8 pares pode ser sustentado pelo tomate sozinho. E as **outras 17 culturas da mesma linha ganharam ZERO linha própria** — berinjela, melão, pepino, melancia, funcho, aipo, rúcula, feijão, ervilha, cenoura estão literalmente no rótulo e são invisíveis para o sistema.

### CLASSE C — suspeita forte, NÃO provada (evidência truncada)

**C1. TOMATO × Puccinia spp** — `BLAISE ULTRA` (017358), `CUSTODIA ULTRA` (015232), `MIRADOR TURBO` (017824)
*Puccinia* é ferrugem de cereal. No trecho do tomate aparece só oídio:
> `Pomodoro Melanzana (uso in serra) Oidio (Leveillula taurica, Sphaerotheca spp., Erysiphe spp.) 0,5 - 1 500-1000 10 ... Peperone (uso in serra) Oidio (...) ... Agli`

A palavra *Puccinia* **não aparece** no trecho do tomate — aparece nas linhas de Triticale e Orzo do mesmo rótulo. Mas a evidência bate no teto de 240 caracteres, então **NÃO SEI** se o suporte está depois do corte. Marcar como suspeita, não como erro provado.

**C2. BARLEY × Puccinia recondita** — `MAXENTIS` (018067), `KOJAMI` (019095). *P. recondita* é ferrugem-parda do trigo; a da cevada é *P. hordei*. O trecho da cevada mostra `Ruggini (Puccinia sp.)` e está truncado; *P. recondita* aparece na linha do Frumento do mesmo rótulo. **NÃO SEI.**

### O que NÃO é erro (verifiquei e absolvo)

- **SOYBEAN × Chaetocnema tibialis** e **WHEAT_GENERIC × Bibio hortulanus / Melolontha melolontha** — parecem estranhos, mas as evidências estão **completas** (70 e 122 caracteres) e o próprio rótulo faz esse par. É o rótulo falando, não o parser errando.
- **OLIVE × 4 ervas** e **MAIZE × 6 ervas** — herbicida contra planta daninha em olival e milho. Coerente.

### Nomes científicos cortados no meio (quebram busca exata)

`Ramularia collo` (é *collo-cygni*) · `Echinochloa crus` (é *crus-galli*) · `Abutilon theophras` (é *theophrasti*) · `Leersia oryzoidea` (é *oryzoides*). Mais 3 pares afetados além dos 27.

---

## 2. Alvo que é na verdade uma CULTURA — SIM, e o caso mais grave é o inverso

### 2A. A cultura RICE inteira foi pescada de dentro de um nome de erva daninha

**14 dos 90 pares (15,6%) — 4 produtos: `GLIPHOGAN TOP CL PFNPE` (018270), `HERBITOTAL CL PFNPE` (018271), `SHAMAL MK PLUS CL PFNPE` (018277), `TAIFUN MK CL PFNPE` (018279).**

A evidência começa assim:
> `Riso crodo), Ammi majus (Visnaga maggiore), Amaranthus sp. (Amaranto), Calendula sp. (Calendula), Chenopodium sp. (Farinaccio), Orobanche (Succhiamele), Portulaca sp. (Porcellana comune), Raphanus sp. (Rafano), Senecio sp. (Senecio), Sinapi`

Três provas dentro do próprio texto:

1. O trecho **abre com um parêntese que fecha sem nunca ter aberto** — `Riso crodo)`. Ou seja, a string começa **dentro** de um parêntese.
2. **Todos** os outros itens da mesma lista têm o formato `NomeLatino (NomeItaliano)`. Logo `Riso crodo` é o nome italiano dentro do parêntese de uma **erva daninha**, não uma cultura. "Riso crodo" é o arroz-vermelho/arroz-daninho.
3. `TARGETS_FROM_LABEL` desses produtos é uma lista de **65 plantas** que inclui `Acer sp.` (bordo), `Salix sp.` (salgueiro), `Rubus sp.` (amora-silvestre), `Juncus sp.` (junco), `Tipha sp.`, `Phragmines sp.` (caniço), `Erica`, `Calluna`, `Genista`, `Cistus` — espectro de vegetação total, não de lavoura de arroz. E o ingrediente é **GLYPHOSATE**, HRAC G, não seletivo.

**Consequência:** o par `RICE × ...` desses 4 produtos não é "produto para arroz". A palavra "Riso" veio da coluna do alvo. Um sistema que responder "temos 4 produtos com uso lido em arroz" estará oferecendo glifosato não seletivo para uma lavoura de arroz.
*Ressalva honesta:* **NÃO SEI** se o rótulo completo traz arroz como cultura em outro lugar. Só sei que **esta linha de evidência não sustenta isso**.

### 2B. Alvos que são gêneros de cultura (colisão de nome)

13 dos alvos dos 90 pares são gêneros que também nomeiam cultura:

| alvo gravado | por que colide |
|---|---|
| **`Raphanus sp`** (glosa do rótulo: *Rafano*) | **exatamente o gênero do caso Nabo-bravo brasileiro** — *Raphanus raphanistrum*. E "Rafano" é o nome da hortaliça rabanete |
| **`Avena sp`** (glosa: *Avena*) | *Avena* = aveia, cultura. Aparece em `OLIVE × Avena sp`, 4 produtos |
| **`Sorghum halepense`** | **SORGHUM é cultura neste mesmo arquivo** (9 menções, 2 produtos com linha). Busca pelo token "Sorghum" colide |
| `Sinapis sp` | mostarda, cultura |
| `Lolium sp` | azevém, forrageira cultivada na Itália |
| `Chenopodium sp` | gênero da quinoa |
| `Amaranthus sp`, `Portulaca sp`, `Calendula sp`, `Cyperus rotundus`, `Glyceria sp`, `Echinochloa crus`, `Leersia oryzoidea` | todos com parente cultivado |

Fora dos 90 pares, em produto com zero linha, `CLEAVE` (016475) tem o alvo **`Daucus carota`** — o binômio exato da cenoura cultivada.

---

## 3. Cobertura real: 19 de 163. E a frase que o sistema pode dizer

| medida | valor |
|---|---|
| produtos com **ao menos 1** linha de uso lida | **19 / 163 = 11,7 %** |
| produtos com **ZERO** linha de uso | **144 / 163 = 88,3 %** |
| dos 144: tabela de dose **detectada** mas nenhuma linha extraída | 61 |
| dos 144: nenhuma tabela detectada | 83 |
| dos 144: **têm cultura E têm alvo no rótulo, mas sem ligação entre os dois** | **82** |
| dos 144: não têm nem cultura nem alvo | 40 |

E um detalhe que o próprio arquivo se contradiz: a definição da classe diz
> `AUTHORIZED_USE_ROW: "cultura, alvo e dose na MESMA linha da tabela. Estreita e com ligação."`

Mas **só 13 das 49 linhas têm dose**. **36 das 49 (73,5%) não cumprem a definição da própria classe em que foram postas.**

Cuidado com o número de capa: `LABEL_COVERAGE: "163/163 (100%)"`. Isso é **rótulo baixado**, não uso lido. Ao lado dos 11,7% de uso lido, esse "100%" é o número mais perigoso do arquivo.

### A frase que o sistema TEM direito de dizer sobre os 144

> "Nesta leitura do rótulo publicado no site do Ministero della Salute, capturada em 30/08/2026, **não encontramos** nenhuma linha que ligue cultura e alvo para este produto. Isso é o que a nossa coleta leu — **não é** o que o registro contém. Se você precisa saber se existe uso autorizado para essa cultura, essa resposta ainda não temos: **não sei**."

### A frase que o sistema NÃO tem direito de dizer

> ~~"Este produto não tem uso autorizado para [cultura]."~~
> ~~"A ADAMA não tem produto para [alvo] em [cultura] na Itália."~~
> ~~"Não há registro / não existe / não consta."~~

Este é o erro do Nimitz EC — 3 culturas no catálogo, 19 no registro. **Afirmar que o cliente não tem produto para um alvo quando ele TEM é o pior erro possível deste sistema.**

O arquivo já carrega o aviso certo, e ele deve ser propagado literalmente para qualquer tela:
> `COVERAGE_IS_A_FLOOR: "tabela detectada em 80 de 163 rótulos; verificador de gênero é o dicionário EPPO espanhol, que não cobre gêneros só italianos (Scaphoideus não está nele). Linha ausente NÃO é uso não autorizado."`

Repare no meio dessa frase: **o verificador de gênero de um rótulo italiano é o dicionário EPPO espanhol.** É por isso que gêneros só italianos passam sem conferência.

---

## 4. Distância entre "menciona a cultura" e "tem linha de uso" — onde o Nimitz mora

| CULTURA | produtos que MENCIONAM | produtos com LINHA de uso | distância | % sem ligação |
|---|---:|---:|---:|---:|
| **GRAPEVINE** | 61 | **1** | **60** | **98,4 %** |
| **WHEAT_GENERIC** | 61 | 3 | **58** | 95,1 % |
| **TOMATO** | 57 | 7 | **50** | 87,7 % |
| **APPLE** | 48 | 2 | 46 | 95,8 % |
| SUGARBEET | 48 | 3 | 45 | 93,8 % |
| POTATO | 45 | 2 | 43 | 95,6 % |
| BARLEY | 46 | 5 | 41 | 89,1 % |
| MAIZE | 36 | 3 | 33 | 91,7 % |
| **SUNFLOWER** | 32 | **0** | 32 | **100 %** |
| SOYBEAN | 33 | 2 | 31 | 93,9 % |
| **ALFALFA** | 25 | **0** | 25 | **100 %** |
| COMMON_WHEAT | 24 | 2 | 22 | 91,7 % |
| TRITICALE | 25 | 5 | 20 | 80,0 % |
| **DURUM_WHEAT** | 14 | **0** | 14 | **100 %** |
| RICE | 15 | 4 | 11 | 73,3 % |
| OLIVE | 12 | 4 | 8 | 66,7 % |
| SORGHUM | 9 | 2 | 7 | 77,8 % |
| **TOTAL** | **591** | **45** | **546** | **92,4 %** |

**A distância é maior em VITE (uva): 61 menções, 1 ligação.** E essa única ligação é frágil. A evidência inteira é:
> `vite consente di prevenire e contenere in misura apprezzabile le infezioni di Botrytis cinerea.`

"consente di prevenire e contenere in misura apprezzabile" = "permite prevenir e conter em medida apreciável". A frase **não diz "autorizzato contro"**. E o `TARGETS_FROM_LABEL` do `SESTO GOLD` (015317) é **vazio: `[]`**. Ou seja: a cultura mais citada do portfólio italiano tem uma única ligação, e ela está apoiada numa frase de contenção. **NÃO SEI** se, no direito regulatório italiano, essa frase é uma indicação autorizada ou uma ação colateral — isso precisa de leitura jurídica, não de parser.

### As três culturas com ZERO e o caso mais caro

**DURUM_WHEAT: 14 menções, 0 linhas.** E o trigo duro está **escrito com todas as letras** dentro de uma linha de uso que o sistema leu:
> `Frumento tenero e duro (invernale e primaverile) Septoria (Zymoseptoria tritici, Septoria nodorum), Oidio (Blumeria graminis), Ruggini (Puccinia striiformis, Puccinia recondita) Fusarium (Fusarium spp., Microdochium spp.)` — `MAXENTIS` (018067) e `KOJAMI` (019095)

e ainda:
> `Frumento (duro/tenero): intervenire alla dose di 1,0–1,2 L/ha contro Septoria (Septoria tritici)` — `STAVENTO` (017752)

O rótulo diz **"duro"**. O sistema gravou só `COMMON_WHEAT`. Se alguém perguntar "a ADAMA tem produto para Septoria em trigo duro na Itália?", este arquivo responde zero — **e a resposta zero está errada, provada pelo texto que o próprio arquivo guardou.** É o Nimitz EC, palavra por palavra.

**ALFALFA (25 menções, 0) e SUNFLOWER (32 menções, 0)** têm o mesmo risco, mas aí **não sei** — não há linha lida que os cite. Só sei que 25 e 32 rótulos falam neles.

Vale registrar também: `GLIPHOGAN TOP CL` (015096), glifosato não seletivo, tem `CROP_TERMS_PRESENT` com **11 culturas** (APPLE, BARLEY, GRAPEVINE, MAIZE, OLIVE, POTATO, RICE, SOYBEAN, SUGARBEET, TOMATO, WHEAT_GENERIC). Rótulos de glifosato inflam a coluna "menciona a cultura" — parte dos 591 é ruído desse tipo. A distância medida é real, mas o lado esquerdo da tabela está inflado.

---

## Resumo em uma linha

Dos 90 pares, **27 (30,0%) têm defeito de pareamento**; a cultura **RICE inteira (14 pares, 4 produtos) foi pescada de dentro do nome de uma erva daninha**; **88,3% dos produtos não têm nenhuma ligação cultura-alvo lida**; e **o trigo duro, escrito literalmente no rótulo, aparece com zero** — o erro do Nimitz já está dentro deste arquivo, não é risco futuro.