# PROPOSTA · a taxonomia mínima do FACT_KIND (D62)

**Proposta escrita, para decisão do dono.** Nenhuma coluna foi criada; nada foi instalado.

FACTO (D62) = o que muda no campo + eventos técnicos como tipo próprio + todo o ecossistema do
agronegócio. O `fact_kind` é **uma etiqueta**: não descarta, não muda veredito, e `NAO_SEI` é válido.

Os exemplos são **reais**, do gabarito e da prova cega (`rotulos/`). Os textos estão fora do Git em
`%USERPROFILE%/sintonia-gabarito/REGUA-FATO-V1/textos/<ID>.txt`; o sha256 de cada um está em
`A-ROTULAR-FATO.json`. Rotulador: Claude, `VALIDADO_POR_HUMANO = NAO`.

| FACT_KIND | O que é | Exemplo real 1 | Exemplo real 2 |
|---|---|---|---|
| `CAMPO_FITOSSANITARIO` | praga, doença, monitorização, capturas, limiar, defesa | `63430c6290ceed39` · Sala · IT-T3-010: «I monitoraggi territoriali … non si sono rilevate … superamenti della soglia di intervento … mosca dell'olivo» | `1261b230914353e5` · acervo: «Bollettino Fitosanitario ZONA PROGETTUALE PIANURA INTERNA VITERBESE … Mosca dell'olivo … Soglia di intervento» |
| `CAMPO_CLIMA` | tempo ou clima que muda o campo | `ddf0b4cb4cb59c4b` · acervo: «Agrometeo… Informa Zona 24 Alto Polesine … Il tempo previsto nei prossimi giorni» | `5190041491dddcb5` · acervo: «Caldo record e siccità: danni ingenti all'agricoltura» |
| `CAMPO_PRODUCAO_COLHEITA` | fenologia, colheita, rendimento, produção | `9f97f572c5f0af98` · acervo: «il biologico registra una resa superiore del 2,3% … nelle annate calde e asciutte» | `f663281bf77867a2` · acervo: «Presentazione Brunello Forma 2021 - Valutazione annata» (só título) |
| `MERCADO_PRECO` | preço, cotação, volumes, exportação, consumo | `c8a70fb6b3177d3f` · Sala · IT-T10-018: «le quotazioni dell'uva da tavola restano … L'uva bianca con semi si attesta intorno a 3 euro/kg» | `c306abc7b0b30965` · Sala · IT-T10-018: «prezzi compresi tra le 170 e le 180 lire turche» (nocciole) |
| `EVENTO_TECNICO` | feira, congresso, workshop, dia de campo, curso técnico do agro | `c9da6dbf9fa87724` · acervo: «Interpoma 2026, fiera internazionale della mela in programma dal 25 al 27 novembre a Fiera Bolzano» | `910c5b1c6ec428fd` · Sala · IT-T10-018: «44esima edizione del Salone, in programma a Rimini dal 20 al 22 aprile 2027» (Macfrut) |
| `REGULATORIO_MOLECULA` | registo, autorização, revogação de produto; substância ativa; LMR | ⚠️ **0 textos em prosa** no gabarito e na prova cega. Exemplo real só em **tabela**: `IT-T4-001` (armazém, cópia `C:/ajustes/brutos-t4t5t9/it-t4-001/…PROD_FTS_6_20260914.csv`, registo do Ministero della Salute), linha `000002;CONTRAX STANGE;KEMIO;…;WARFARIN;…;Revocato;REVOCA PER MANCATA RISPOSTA A RICHIESTE UFFICIO;-;05/03/1997` | a mesma tabela, linha `000001;ENOVIT;SIPCAM S.P.A.;…;14/04/1970;…;THIOPHANATE-METHYL;…;Revocato;…;14/07/1983` |
| `NEGOCIO_AGRO` | empresa, produto comercial, lançamento, investimento, apoio ao setor | `aae3bdef0c33d972` · Sala · IT-T10-018: «Alkelux, la startup deeptech … additivi … per allungare la shelf-life dei berries» | `925a2a0f7c570077` · Sala · IT-T10-018: «Vog … dà ufficialmente il via alla nuova stagione commerciale delle sue mele biologiche» |
| `INSTITUCIONAL_NAO_FATO` | menu, administração, outro setor | `5318cc3dbefa62d5` · Sala · IT-T5-019: «Padua Research Archive (PRA) è l'archivio istituzionale della produzione scientifica» | `3cf76f39efd4d05b` · Sala · IT-T5-030: «Cybermafie: ad UniTe Ivano Gabrielli, direttore della Polizia Postale» |
| `NAO_SEI` | curto demais, ou mistura sem assunto dominante | `01b015f3d06d6fd8` · acervo: «21 aprile 2026 - Nature Restoration Law e Piano nazionale di ripristino della natura - YouTube» (só título) | `e3db40903238b87a` · Sala · IT-T5-010: um número inteiro da revista «La Pianura», com vários artigos agro e de história |

## Fronteiras que o dono decide (aparecem no gabarito e mudam os números)

1. **GDO (supermercado).** Abertura de supermercado generalista, logística da GDO. Rotulei
   `INSTITUCIONAL_NAO_FATO` pela D62 («loja só se for do ecossistema agro»); o classificador diz
   `MERCADO_PRECO` ou `NEGOCIO_AGRO`. **3 dos 10 erros do gabarito vêm daqui.** Se o dono disser que
   a GDO é do ecossistema, esses erros passam a acertos.
2. **Empresa a falar da técnica** (Koppert e os ácaros predadores): é `NEGOCIO_AGRO` (quem fala) ou
   `CAMPO_FITOSSANITARIO` (de que fala)? Rotulei `NEGOCIO_AGRO`.
3. **Investigação e zootecnia sem tipo** (floricultura com menos energia, aditivos e metano,
   avicultura): `NAO_SEI` com `SEM_TIPO`. **3 de 114 no gabarito (2,6 %)**, abaixo do limite de 10 %
   do protocolo: **nenhum tipo novo proposto**.
4. **Veterinária** (D26, fora do foco): `INSTITUCIONAL_NAO_FATO`.

## Nome

`superficie/ask_sintonia.py:246` já usa `FACT_KIND` para **outra coisa**: frescura da resposta do
benchmark (`CURRENT` / `HISTORICAL` / `STRUCTURAL`). São dois conceitos com o mesmo nome. Proponho que o
campo do item se chame `fact_kind` (minúsculas, como as colunas da Sala). O do benchmark deve passar a
ter nome próprio, ou ficar documentado como diferente.
