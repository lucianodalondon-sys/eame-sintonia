# EXTRATOR-EVENTO-V2 — mais itens com data do fato, e os boletins com cultura, praga e fase

Missão EXTRATOR-EVENTO-V2 + ajuste de prioridade D84 (26/09, 07:30). Ramo `extrator-evento-v2`, a partir do vivo
`69b0e23f` + `periodo-chaves-v1 @ 91ab4eb3` (avanço simples, sem commit de junção). **Sem mapa** (PRONTO-SEM-MAPA).
Só leitura da Sala (`default_transaction_read_only=on`), do armazém e da cópia do livro; sem rede; nada instalado.

## 1. O que mudou

### D84 (em primeiro lugar) — os boletins T3/T2
| peça | o quê |
|---|---|
| `leis/boletim_do_campo.py` (novo, puro) | lê **cultura + praga/doença + fase** por **secção de cultura**, cada uma com o trecho. Uma linha curta que nomeia a cultura abre a secção («OLIVO», «COLTURA … ACTINIDIA»). A praga com a cultura no nome («tignoletta della **vite**») vai para essa cultura, e a linha toda com ela. **«Non presente», «assente», «non si riscontrano/non riscontrate catture» = AUSENTE — nunca ocorrência.** Sem marca = CITADA; «presente/rilevato/catture/sintomi» = PRESENTE. |
| `admissao/admissao.py` (`janela_declarada`, `janela_para_o_ready`) | em **T2/T3** a porta usa o leitor: **CULTURA** (só onde a régua e o título/lugar nada disseram), **FASE** (só onde a régua T1 nada disse) e a chave nova **PROBLEMA** (as pragas não ausentes; `AUSENTES` à parte; `SECOES` = cultura → pragas com estado → fases, que é o par que a FINESTRE COLTURALI cruza). Viaja no READY ao lado das quatro chaves, **fora** da contagem delas. |
| `leis/fato_do_texto.py` · período do cabeçalho | «Settimanale N. 37 / **09 - 15 settembre 2026**» (ARIF) → `fact_time = 09 - 15 settembre 2026`, base `CAMPO · CABECALHO_DO_BOLETIM · WEEK`, período `2026-09-09/2026-09-15`. Só nas primeiras 12 linhas, só num texto que se declara boletim, só se a linha **inteira** é o período. «N° 27 del 16/09/2026» é **publicação** e fica de fora. Período que começa depois da publicação provada = futuro. A data de campo presa a um acontecimento vence o cabeçalho. |
| `leis/fato_do_texto.py` · ano de comparação | «rispetto al / confronto con il / stesso periodo del / contro il … 2025» → `COMPARACAO_NAO_E_FATO` (tapa e pergunta de novo). |

### EXTRATOR-EVENTO-V2 — o acontecimento e o título
| peça | o quê |
|---|---|
| `leis/fato_local.py` | `ANCORAS_DE_ACONTECIMENTO_DO_TEMPO`: incendi, grandin, gelata/e, brinata/e, alluvion, esondazion, nubifragi, siccit, venti forti/intensi, raffiche, tromba d'aria, mareggiata, maltempo, frana, ondata di calore, calamit, evento atmosferico/meteo/estremo. «gelato» (sorvete) não; «vento» sozinho não. |
| `leis/fato_do_texto.py` | **data PERTO do acontecimento** (≤ 50 letras, só para as âncoras novas) · **futuro não é fato**: marca de previsão/possibilidade perto da data (60 letras antes / 30 depois: allerta, previste, domani, possibili, potrebbe…), data depois da publicação provada, «domani/prossima settimana» de campo · **data do ato** (decreto, delibera, Gazzetta…) não é do fato · **título** (texto de uma linha curta, ou sem nenhuma frase longa) entra na leitura, sem o nome do sítio · `campos_do_fato(titulo=, descricao=)`. O **evento técnico anunciado** («il convegno si terrà domani») continua EVENTO (D62). |
| `coleta/youtube_janela.py`, `admissao/reprocessar_tempo_lugar.py`, `orquestrador/orquestrador.py` | título e **descrição** do vídeo (o `shortDescription` do player guardado; nunca a frase genérica do YouTube) levados até ao leitor. |

As leis que **não** mudam e estão testadas: a publicação nunca vira data do fato (data igual à publicação é carimbo) · «ieri» só com publicação provada (D63/D64) · UNKNOWN continua UNKNOWN.

## 2. Antes → depois (os 1.252: 94 linhas da Sala + 1.158 brutos do acervo, mesma estrada do reprocesso)
Saídas: `data/derivados/EXTRATOR-EVENTO-V2/MEDIDA-ANTES.json`, `MEDIDA-DEPOIS.json`, `ANTES-DEPOIS.txt`.

| | antes | depois |
|---|---|---|
| **data do fato** (1.252) | 57 | **106** (+49 · **0 perdidos · 0 trocados**) |
| período com ano | 36 | 79 |
| região do fato | 62 | 90 (os títulos agora lidos) |
| cultura | 70 | 76 |
| fase | 0 | 14 |
| praga/doença (chave nova) | 0 | 8 |
| as 3 chaves juntas (período + região + cultura) | 6 | 7 |
| **Sala, 5 T3 + 1 T2** — cultura / fase / praga | 1 / 0 / 0 | **6 / 6 / 5** |
| Sala, 5 T3 + 1 T2 — data do fato / período | 1 / 0 | 3 / 2 (as duas semanas do ARIF) |
| acervo, 124 boletins T2/T3 com texto — cultura / fase / praga | 0 / 0 / 0 | 1 / 8 / 3 |

Os ganhos de data: **32 EVENTO** (datas de convegni/webinar/feiras escritas nas **descrições** dos vídeos), 15 CAMPO, 2 relativas.

## 3. Lidos à mão: 20 (os 6 boletins da Sala + 14 ganhos de data, semente 20260926, fontes distintas)
| # | item | veredito |
|---|---|---|
| 1 | IT-T3-010 | ✔ olivo · 6 fases · mosca, occhio di pavone, lebbra, xylella… (data: o coletor declarou validade, não observação → NAO SEI certo) |
| 2, 4 | IT-T3-002 Salerno (a mesma página duas vezes na Sala) | ✔ 12 culturas com as suas fases e pragas; cimice asiatica **AUSENTE** na actinídia e presente no ciliegio. Nota: «afide/afidi» saem como dois nomes (forma não normalizada) |
| 3, 5 | IT-T3-008 ARIF | ✔ semana do cabeçalho; ⚠→✔ **corrigido depois da leitura**: a Lobesia (vite) ia para o olivo e «non riscontrate catture» não era ausente. Continua um limite: «peronospora (Plasmopara viticola)» fica no olivo (o nome não diz «vite») |
| 6 | IT-T2-034 | ✔ olivo, fioritura; «maggio» sem ano → período NAO SEI certo |
| 7, 8, 9, 10, 11, 14, 19, 20 | eventos (Expo, Agriumbria, webinar, Giornate di Studio, convegno, RetePAC, Life Atena, premiação) | ✔ EVENTO (D62) |
| 12 | IT-T7-034 «annata 2020» | ✔ a safra avaliada |
| 15 | IT-T2-051 incêndio de Pontenure | ✔ 7 settembre 2026 |
| 16 | IT-T8-004 «campagna 2025/26 del frumento duro» | ✔ |
| 17 | IT-T10-017 «Buone prospettive di mercato della campagna 2025» | ⚠ duvidoso: «prospettive» é expectativa |
| 13 | IT-T2-026 «ieri» → 2023-12-01 | ⚠ não conferido: a medida guarda só a base, sem o trecho |
| 18 | IT-T2-028 «Lanciato nel 2021, il progetto ha **raccolto** dati» | ✘ errado — âncora ANTIGA «raccolt» (dado recolhido ≠ colheita) |

**Resultado (20): 15 certos · 2 corrigidos depois da leitura (as duas páginas do ARIF) · 2 duvidosos · 1 errado.** Também achados na leitura dos 48 e corrigidos
antes da medida final: data da atualização de dados como data do temporal (IT-T2-051, «18 settembre … a seguito degli
eventi meteorologici»), «possibili gelate tardive … ad aprile» (IT-T10-021), e «raccolta 2026 … è appena iniziata» que a
guarda de futuro apagava (IT-T10-018).

**Erros das âncoras ANTIGAS que os títulos/descrições agora expõem** (não mexi — é régua do dono do LUGAR-FATO):
«raccolto» = dado recolhido (IT-T2-028); «monitoraggio» no nome de uma Giornata di Studio sai CAMPO em vez de EVENTO
(IT-T7-035 «Salute e monitoraggio degli alberi»); «webinar … monitoraggio … 2020» (IT-T2-025) idem.

## 4. Testes e mutação (rede fechada)
- `tests/test_extrator_evento_v2.py` 30 · `tests/test_boletim_do_campo.py` 18 — casos reais marcados com o SOURCE_ID.
- Mutação `data/derivados/EXTRATOR-EVENTO-V2/mutacao.py.txt`: **38/38** (cada mutante com `git diff`).
- Regressão: 82 ficheiros de teste ligados (leitor, porta, Sala, quatro chaves…), base `91ab4eb3` × este ramo, comparados
  pelo nome: **base 1.933 testes · este ramo 1.981 (os 48 novos) · as MESMAS 210 falhas/erros de base (202 + 8), nenhuma
  nova.** Três testes antigos foram **ajustados** por mudança de contrato pedida pela D84 (as chaves da
  janela ganham PROBLEMA; «fioritura» escrita no TEXTO de um boletim T2 passa a fase — a regra «as palavras de clima da
  régua T2 não são fase» continua cobrada) e um pela assinatura do leitor (`titulo`, `descricao`).

## 5. O que falta / limites declarados
- **Mapa** por correr (PRONTO-SEM-MAPA): `leis/boletim_do_campo.py` é ficheiro novo e precisa de peça (P9).
- A Sala guarda a janela como JSON: a chave `PROBLEMA` viaja sem migração; **colunas próprias** para praga/fase são
  decisão do dono da Sala.
- Os boletins T2 (ARPA) quase não têm secção por cultura: cultura 1/124 no acervo.
- Formas não normalizadas (afide/afidi; nome comum + nome científico contam como dois) — não é EPPO nem BBCH.
- O período do cabeçalho vira `fact_time` (tipo CAMPO, precisão WEEK): é o período a que o boletim se refere, não um
  acontecimento datado — **decisão do dono** se prefere guardá-lo só como JANELA.
- Âncoras antigas (secção 3) e «prospettive» como expectativa — para o dono do LUGAR-FATO.

## 6. Instalar / desfazer
Ficheiros de código: `leis/boletim_do_campo.py` (novo), `leis/fato_do_texto.py`, `leis/fato_local.py`,
`admissao/admissao.py`, `admissao/reprocessar_tempo_lugar.py`, `orquestrador/orquestrador.py`, `coleta/youtube_janela.py`;
testes `tests/test_extrator_evento_v2.py`, `tests/test_boletim_do_campo.py`, `tests/test_fato_do_texto.py`,
`tests/test_quatro_chaves.py`, `tests/test_quatro_chaves_na_sala.py`; registos em `data/derivados/EXTRATOR-EVENTO-V2/`.
Desfazer: voltar o vivo ao commit anterior (`reset --keep`). Nada é escrito na Sala por esta entrega; os itens já
pousados só mudam se alguém correr o reprocesso (revisões append-only da 033).
