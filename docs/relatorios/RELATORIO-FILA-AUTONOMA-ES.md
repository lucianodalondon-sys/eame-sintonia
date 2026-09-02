# Relatório da fila autônoma — Espanha

Data de fechamento: 2026-08-30
Branch: `claude/sintonia-eame-collection-es`
Escopo: milho → cereais de inverno → olivar → ciência → voz → casos herói. Parou antes de portal/UI, como pedido.

---

## A. O que rodou

Dez commits nesta rodada, todos com artefato medido no repositório. Nenhuma rota paga nova foi aberta: tudo saiu de API pública gratuita (ORCID, RAIF/Junta de Andalucía, Generalitat de Catalunya, opendata.aragon.es) ou de derivação sobre dado que já estava aqui.

O orçamento do OpenAlex zerou no meio da rodada (HTTP 429 por crédito, não por taxa de IP) e não foi reaberto. Tudo que depende dele está declarado como limite de leitura, nunca como ausência.

## B. Ciência por par — `ES-CIENCIA-PARES-AUTORES.json`

Rota: CROP × ISSUE lido do ROPF espanhol → papers → autores → identidade ORCID. Nunca o inverso.

| par | papers | autores distintos | desde 2023 |
|---|---|---|---|
| OLIVE × REPILO | 10 | 49 | 3 |
| MAIZE × AMARANTHUS | 31 | 83 | 16 |
| WHEAT × SEPTORIA | 47 | 200 | 26 |

- `PAIRS_SENT_TO_SCIENCE` = 3
- `PAPERS` = 88
- `RESEARCHERS` persistidos = 36 (topo por obras no par)
- `IDENTITIES`: 5 CONFIRMADA (só com `num-found=1` no ORCID), 8 CANDIDATA com candidatos listados, 2 não encontradas, 21 não testadas
- `OLD_152_SURVIVES` = 6 · `NEW_RESEARCHERS` = 30

Ambiguidade não foi colapsada em vencedor em lugar nenhum.

## C. Ciência → voz — `ES-CIENCIA-PARA-VOZ.json`

11 pesquisadores consultados no ORCID (`/person` + `/employments`), 22 chamadas, 22 HTTP 200.

**Canais sociais autodeclarados: 0 de 11.** As 7 URLs que existem são página de grupo, de instituição ou índice acadêmico. A camada científica prova papel e dá identidade estável; ela não entrega voz pública. A ponte não foi atravessada.

Isso é silêncio da fonte, não ausência no mundo: a pessoa pode ter canal e não o ter declarado ali.

**O par é espanhol; a autoria não precisa ser.** MILHO × AMARANTHUS entregou 3 de 3 identidades confirmadas com vínculo aberto na Espanha — Navarra (2) e Lleida (1). TRIGO × SEPTORIA entregou as 2 confirmadas **fora** da Espanha: Lukas Meile saiu do CBGP em 2024 e está na ETH Zurique; Alassimone nunca declarou vínculo espanhol. Não existe, nesta medição, voz científica espanhola confirmada para trigo × septoria.

Das 6 URLs autodeclaradas, resolvidas uma a uma: 4 vivas, 1 morta, 1 que nem é canal.

## D. Voz × matriz de prioridade — `ES-VOZ-x-MATRIZ-DE-PRIORIDADE.json`

Quase todo o acervo de voz é cego por construção: 7 de 7 termos do YouTube e 17 de 17 termos de post do LinkedIn são de olivar/Andaluzia.

Sobram 54 perfis de busca por cargo em "Spain" inteira — cegos a cultura e a região. Milho declarado: 0.

**E esse zero também não conclui nada**: 48 dos 54 não nomeiam nenhuma cultura no título. O zero mede a convenção do título, não a população. Estado: INDETERMINADO.

O que é legível é a geografia: Andaluzia 22 de 54 contra 5 de 54 em todo o eixo Aragón+Catalunya+Navarra. Com o confound dito: a Andaluzia é a maior empregadora agrícola do país. n=54, sinal fraco.

Não se diz "o Ebro fala pouco". Diz-se que **o acervo** tem pouco do Ebro.

## E. Casos herói com mapa de ação

Três casos, três pedidos diferentes. Cada ação aponta para um fato já no repositório; onde a função não pode agir, o arquivo diz o que falta.

**Milho × Amaranthus (`ES-HERO-001`)** — SCIENCE é a única função com material verificado; REGULATORY tem a lacuna nomeada (1 registro em toda a Espanha declara Amaranthus como alvo em milho, nenhum da ADAMA); COMMERCIAL e SUPPLY são NÃO SEI. Janela agronômica de 2026 fechada — a ação é chegar preparado em abril de 2027.

**Olivar × repilo (`ES-HERO-002`)** — o único onde "agora" cabe, e cabe pelas datas da fonte: XML do RAIF gerado 6 dias antes da captura, janela de outono abrindo. REGULATORY tem o item mais datado do repositório: NEPTUNE ES-00211 vigente com caducidade vencida há 15 dias. Contradição **na fonte**, não conclusão de que o produto saiu.

**Cereais de inverno × septoriose (`ES-HERO-003`)** — o inverso exato do milho: o dobro do portfólio (36 pares contra 16) sobre a maior área do país e sem sinal atual localizado.

## F. Cereais de inverno: a correção — `ES-T3-002-raif-cereales-invierno.json`

Eu tinha escrito `NO_CURRENT_EVIDENCE_FOUND` depois de procurar no ITACyL, de Castilla y León. A fonte está no RAIF da Andaluzia — o mesmo portal que eu já usava há dois dias para o olivar, e que publica 10 culturas. Nunca perguntei se tinha cereal.

15 campanhas de amostragem observada, septoriose como campo próprio, 21.838 muestreos históricos e 388 em 2026.

Resultado: **2026 foi um ano fraco de septoriose** — 2,68% de superfície com sintomas, o segundo menor da série com n≥100.

Continua em aberto: Castilla y León, que é onde está o cereal espanhol, segue sem fonte encontrada.

## G. O eixo do milho não é mudo — `ES-T6-001-adv-catalunya.json`

Eu disse que MARKETING não pode agir no milho porque "não há voz pública no território". A frase era sobre LinkedIn e YouTube e eu a escrevi como se fosse sobre o território.

Uma chamada ao registro oficial da Generalitat: 122 Agrupacions de Defensa Vegetal na Catalunha, **50 na planície de Lleida**, em 39 municípios, todas com contato declarado. Segrià sozinha tem 30.

Ausência de voz em plataforma não é ausência de interlocutor organizado. Eu estava medindo o território pelas rotas que já tinha aberto, e as rotas que eu tinha eram sociais.

Mas: densidade de ADV não prova pressão no milho. Segrià e Pla d'Urgell são o coração agrícola da Catalunha inteira. São **interlocutores localizados**, não vozes de milho.

## H. Onde está o milho, de fato — `ES-T2-002-pac-maiz-aragon.json`

Declarações PAC de Aragón 2025: 102 MB, 1.293.690 parcelas. Aragón 51.752 ha de milho; Huesca 37.236, Zaragoza 13.410, Teruel 1.106.

Contracheque: o repositório já tinha 39.945 ha para Huesca pelo SCOT do MAPA. **6,8% de diferença entre declaração de subsídio e levantamento estatístico nacional.** Dois instrumentos independentes. Não se somam.

**81 municípios declaram milho em Huesca; 10 concentram 47,7% da área e 20 concentram 68,4%.** Este caso nunca precisou de ação provincial — metade do milho cabe em 10 municípios.

Os nomes dos municípios ficam NÃO SEI: o CSV traz código catastral e a tabela de nomes do portal só sai por exportação Oracle Analytics que exige sessão. Catastral e INE coincidem em muitos municípios e não em todos, e nomear a cidade errada num mapa de ação é pior do que não nomear.

## I. Números que quase viraram frases erradas

Quatro, e todos foram contra-checados antes de publicar.

1. **0 de 12 sobreviventes da fila de 152 no par do milho.** Parecia descoberta sobre a comunidade científica do milho. A fila exige "pelo menos um tema OLIVE" para entrar — medido, OLIVE em 152/152 e MAIZE em 0/152. O zero é a regra de entrada falando. Não sustenta nada.
2. **51,57% de colmos com septoriose em 2026, máximo 81%.** Parecia alarme. Esse campo só tem uso real em três campanhas, e 2026 fica entre 2024 e 2025. Antes de comparar um indicador com a série, contar quantas campanhas realmente o mediram.
3. **Zero leituras de septoriose em 15 campanhas históricas.** Era bug meu: `clear()` nos filhos durante o `iterparse` apaga o texto. O resultado do bug era exatamente "não há histórico" — e com ele eu teria publicado 2026 como sem precedente, quando a série diz que 2026 é dos anos mais fracos. O que denunciou foi contar a tag por um caminho (19.058) e extrair por outro (0). **Ausência produzida pelo meu próprio código tem a mesma cara de ausência do mundo.**
4. **37.236 ha de milho em Huesca.** Grande demais para publicar sem cruzar. Cruzou com o MAPA a 6,8%.

E uma ressalva que eu escrevi mal e corrigi: o aviso sobre vínculo ORCID sem data de fim estava redigido como dúvida sobre a pessoa. Uma cátedra de 1978 e um registro esquecido de 2013 produzem o mesmo campo. Virou aviso sobre a idade do campo.

## J. Limites, custos e o que não foi feito

- **OpenAlex zerado.** Os conjuntos completos de autores por par (49/83/200) não foram baixados. Toda taxa de sobrevivência tem denominador 12.
- **Rotas pagas: nenhuma nova.** Apify não foi tocada nesta rodada.
- **Bloqueios de rede desta sessão:** `grem.udl.cat` e `gdc-pdpopendata-ckan.paas.junta-andalucia.es` recusados pelo proxy de egresso. O segundo foi contornado pelo host `www.juntadeandalucia.es`. Limite meu, não da fonte — e o arquivo separa as duas coisas.
- **Nomes de municípios de Aragón:** não resolvidos, motivo declarado.
- **Castilla y León:** sem fonte de aviso de cereal.
- **Aragón:** o portal não tem registro de ATRIA nem boletim fitossanitário. O equivalente aragonês das ADV catalãs segue sem par.
- **Ramos paralelos:** `claude/adama-es-commercial-intelligence` e `claude/sintonia-italy-pilot` não existem no remoto. Nada foi mesclado.
- **Portal/UI:** não tocado, como pedido.

## K. O que eu faria a seguir, em ordem

1. **Nomear os 10 municípios de Huesca.** É o item de maior retorno por esforço: transforma a concentração medida em mapa de visita. Falta só uma tabela oficial código→nome.
2. **Ler as obras de Joel Torra no par** antes de qualquer contato — saber se ele trabalha *palmeri* espanhol ou *Amaranthus* em geral muda a conversa inteira. Depende do orçamento do OpenAlex.
3. **Procurar o equivalente aragonês das ADV.** O caso do milho depende de Huesca tanto quanto de Lleida, e Lleida já tem 50 interlocutores mapeados.
4. **Coleta de voz desenhada por cultura E região.** Mais consulta de olivar não resolve. E ler conteúdo das origens do Ebro, porque o título declara cargo e só o conteúdo declara cultura.
5. **Fonte de aviso de cereal para Castilla y León.**
6. **As outras 8 culturas do RAIF** (algodão, amêndoa, arroz, cítricos, morango, hortícolas, beterraba, vinha) estão a uma chamada de distância, no portal que já funciona.
