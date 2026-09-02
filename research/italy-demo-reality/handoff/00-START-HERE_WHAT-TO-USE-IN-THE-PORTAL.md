# O QUE USAR NO PORTAL

Quatro gavetas. A diferença entre elas não é qualidade — é **o que a tela tem direito de
afirmar** sobre cada objeto.

---

## ✅ USAR DIRETO — vai à tela como fato, com fonte e data

| o quê | onde | quantos |
|---|---|---:|
| Produto ADAMA com registro, ativo, categoria e vencimento | `ADAMA/adama-italy-products.json` | 163 |
| Rótulo autorizado (URL do PDF oficial) | idem, `LABEL_URL` | 163 |
| Linha de uso: cultura + alvo + dose na mesma linha | `ADAMA/adama-crop-problem-product.json` | 219 |
| **Boletim fitossanitário corrente, com fase fenológica** | `CROP-WINDOWS/current-phenology.json` | **73** |
| Ato regional de lotta obbligatoria, com número e data | `CROP-WINDOWS/crop-windows.json` | 5 regiões |
| Ato europeu de aprovação de substância, lido na íntegra | `FUTURE-RADAR/future-signals.json` | 15 atos |
| Resistência confirmada pelo GIRE | `SCIENCE/herbicide-resistance.json` | 34 |
| Pesquisador com ORCID e obras no recorte | `SCIENCE/researchers.json` | 60 |
| Registro científico com DOI | `SCIENCE/scientific-records.json` | 88 |
| Anúncio de concorrente com texto, data e link | `COMPETITOR-WATCH/competitor-activities.json` | 414 |
| Vídeo de canal de concorrente | idem | 147 |
| Preço por praça, com período e unidade | `MARKET-PULSE/market-pulse.json` | 195 |
| Capacidade de fonte de mercado | `MARKET-PULSE/market-capabilities.json` | 111 |
| Evento com participação confirmada | `EVENTS/events.json` | 18 |
| Notícia com veículo, autor, data e tipo | `NEWS/news.json` | 8 |

**A condição:** cada um vai à tela **com a fonte e a data ao lado**. E os que trazem
`WHAT_IT_DOES_NOT_PROVE` levam essa frase junto — não é rodapé, é parte do dado.

---

## ⚠️ USAR COM INTERPRETAÇÃO DECLARADA — precisa do «por quê» aberto

| o quê | onde | o rótulo obrigatório |
|---|---|---|
| Temperatura de mercado | `MARKET-PULSE/crop-summary-*.md` | **INTERPRETAÇÃO DO SINTONIA**, com as setas de cada componente |
| Voz de campo | `VOCI-DAL-CAMPO/field-voices.json` | ⭐ **a classe de plateia do canal vai junto** — profissional e horta não se somam |
| Par cultura × alvo da conversa pública | `IT-PARES-CULTURA-ALVO-V0.json` | o par é **INFERIDO pelo sistema** |
| Distância entre «menciona» e «tem linha de uso» | `ADAMA/adama-italy-crops.json` | é o que **ainda não sabemos** |
| Candidato a oportunidade | `OPPORTUNITIES/opportunities.json` | **«convergência que merece investigação»** |
| Sinal de futuro | `FUTURE-RADAR/future-signals.json` | fato e interpretação em campos separados |
| Cultura de boletim marcada `INFERRED_FROM_PESTS` | `CROP-WINDOWS/current-phenology.json` | a cultura foi **deduzida das avversità**, não declarada |

⛔ Um objeto desta gaveta apresentado **sem o «por quê»** vira caixa-preta — e caixa-preta é
exatamente o que este projeto existe para não ser.

---

## 🎭 SÓ DEMO — o Design cria, e nasce marcado

Nada disto está no pacote. Cada objeto deve nascer com `PROVENANCE: SYNTHETIC_DEMO`
visível:

```
mensagem de Field Sales · notificação · fluxo de trabalho · geração de Action Brief
estado de leitura · atividade de interface · usuário fictício · alerta simulado
```

⚠️ **A camada operacional pode ser simulada. O mundo agrícola, não.** Um vendedor fictício
pode mandar uma mensagem fictícia — **sobre um produto real, uma cultura real e uma janela
real**.

---

## ⛔ NÃO USAR — não tem lastro

| o quê | por quê |
|---|---|
| «a ADAMA não tem produto para X» | cobertura de uso lido é 11,7% |
| relação produto × cultura não verificada | `CROP_TERM_PRESENT` ≠ `AUTHORIZED_ON_CROP` |
| «o produtor italiano relatou» | comentário é plateia; 32 de 58 são de horta doméstica |
| «o anúncio foi dirigido à Itália» | a fonte diz **alcançou** |
| incidência regional a partir de um boletim | 6 regiões de 20; província não é região |
| participação futura em feira | nunca se infere de participação passada |
| venda, share, estoque, demanda | exige dado interno |
| preço de praça com série parada | ex.: azeite Salerno €630, de **2015** |
| «a ISMEA não tem dado» | ela responde para outros — o bloqueio é do nosso IP |

---

## Como resolver as ligações

Todo objeto tem `ID` estável. As ligações vivem em
`01-DESIGN-READY/RELATIONSHIPS/entity-links.json` e **só carregam IDs**. Para resolver:
`06-HANDOFF-MANIFEST/ID-INDEX.json` diz em que arquivo cada ID mora.

```
IT-PRD-xxx    produto ADAMA           IT-CPP-xxx    ligação cultura×alvo×produto
IT-OPP-xxx    candidato a oportunidade IT-FUT-xxx    sinal de futuro
IT-WIN-xxx    janela de cultura       IT-PHEN-xxx   boletim de fenologia corrente
IT-MKT-xxx    observação de preço     IT-MKTCAP-xxx capacidade de fonte de mercado
IT-COMP-ACT-xxx atividade de concorrente  IT-VOICE-xxx  voz de campo
IT-SCI-xxx    registro científico     IT-PER-xxx    pessoa
IT-NEWS-xxx   notícia                 IT-EVT-xxx    evento
IT-SRC-xxx    fonte                   IT-RES-xxx    resistência confirmada
IT-CHAN-xxx   canal italiano          IT-ARC-xxx    ponteiro de acervo
```

---

## A ordem que economiza retrabalho

1. `05-GAPS-AND-LIMITS/DO-NOT-CLAIM.md` — **antes** de escrever qualquer texto de tela
2. `ADAMA/` — é a fundação: tudo se pendura no produto e no rótulo
3. `SOURCES/sources.json` — toda tela precisa mostrar a fonte
4. `RELATIONSHIPS/entity-links.json` — o que aparece junto com o quê
5. o resto, por tela
