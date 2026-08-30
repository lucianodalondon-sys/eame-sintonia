# O QUE PODEMOS DIZER — E O QUE NÃO

Frases comerciais sustentadas por evidência, e as que o piloto **não pode sugerir**.
Cada frase segura aponta para o arquivo que a prova.

---

## SAFE CLAIMS — sustentadas hoje

1. **"We can connect an EU active-substance decision to national registrations and identify
   the affected registered products — including ADAMA's and competitors'."**
   → CELEX 32025R0787 → protioconazol → 77 produtos na França (ADAMA 3, Bayer 32) e 85 na
   Itália (ADAMA 5, Bayer 18). `CROSS-MARKET-prothioconazole-cereal.json`

2. **"The same molecule can be followed across markets, with measured coverage of 82% of
   real registry usage."** → X-006, amostra cega 77,4%. `X-006-substance-normalisation.json`

3. **"We can read the same regulatory act in English, French, Spanish and Italian, keeping
   the official wording of each — not a translation."** → CAP-002.

4. **"We can show, week by week and province by province, measured disease incidence in
   Andalusia — with eleven seasons of history behind it."**
   → 44.584 leituras, 2016–2026. `ES-T3-001-repilo-serie-historica.json`

5. **"We can tell a real rise from a change of sample."** → controle de coorte: Huelva sobe
   nas mesmas parcelas, Jaén fica plano.

6. **"We can distinguish latent infection from visible symptom — the difference that decides
   whether a treatment is preventive or late."** → repilo incubado × visível.

7. **"We can find who repeatedly works on a specific agronomic problem in a given country —
   and we can show why a loose query would return the wrong people."**
   → 2.627 trabalhos × 27 na consulta estrita.

8. **"We can list, from the official register, which companies hold authorised uses against
   the same agronomic problem."** → trigo × septoriose FR: BASF 22, Bayer 20, ADAMA 6.

9. **"Every number leads back to a source file, a date and an original statement — and the
   system refuses to answer when it cannot."** → <!--M:TEST_COUNT_CURRENT-->807<!--/M--> provas automatizadas; 35 perguntas de benchmark,
   **20 respondidas, 14 recusadas, 1 parcial, 0 erradas**.

10. **"We can show that brand identity is not registration identity."** → na lista oficial
    espanhola, **1.786 denominações comuns** sobre **720 registros de referência**; **363
    registros em vigor (18,2% dos 1.993 em vigor)** carregam mais de uma denominação; máximo
    **25**. Contar cada denominação como uma autorização faria o registro em vigor ser
    contado como **3.039** em vez de 1.993 — **1,52×**. `ES-T4-004-denominaciones-medida.json`

11. **"We can detect that a registered product was renamed without the registration
    changing — an event a brand-based radar would read as one product leaving and another
    arriving."** → ES-01717: MAXENTIS (MAPA 28/05/2025) → SORATEL MAX (MAPA 26/08/2026),
    corroborado pelo trâmite `MODIFICACION NOMBRE` do próprio registro.
    `CHANGE-EVENTS-es-2025-2026.json`

12. **"We can show when the obvious explanation is wrong."** → CASE-008: Córdoba choveu mais
    que Huelva e teve 4× menos doença.

13. **"Comparing two archived versions of the same public document surfaces changes the
    source itself no longer shows."** → o registro espanhol publica só o **último** trâmite:
    das 5 renomeações confirmadas em 15 meses, **4 já não aparecem** no registro de hoje.
    5 confirmadas, 2 reprovadas como artefato de leitura, 3 sem veredito — **a verificação
    reprovou metade dos candidatos brutos**. `CHANGE-EVENTS-es-2025-2026.json`

14. **"For a Spanish registration we can state holder, manufacturer, plant, composition,
    status, dates, authorised crops and every commercial name over it — all from the
    official register."** → ES-01717, duas rotas independentes da mesma autoridade (ficha
    JSON e ficha oficial em PDF). `ES-T4-005-ficha-primaria-es01717.json`

## FORBIDDEN / PREMATURE CLAIMS — o piloto não pode sugerir

| Não dizer | Porque |
|---|---|
| *"We predict disease outbreaks."* | medimos incidência passada e presente; nada foi validado como previsão |
| *"We know market share."* | contagem de **registros** ≠ mercado. Vale para ADAMA e para concorrentes |
| *"We know supply dependency."* | **authorized source ≠ proven supply dependency** (o próprio deck já ressalva). Nenhuma fonte de fabricante foi encontrada |
| *"We measure field influence."* | nenhuma fonte de vozes do campo. Só REACH seria mensurável, e nem isso hoje |
| *"Competitor communication is increasing."* | sem linha de base comparável |
| *"Weather caused the disease."* | X-009 **refuta** com dado |
| *"The EU expiry date determines the national expiry date."* | **não afirmável** — 199 produtos italianos vencem em 31/03/2027, incluindo nicosulfuron, que não tem ato europeu recente |
| *"ADAMA registered 18 months before the competitor."* | **retirado nesta missão** — na Espanha as marcas estão em relação de denominação comum |
| *"This substance will be withdrawn."* | expiração abre renovação; o protioconazol já foi prorrogado 6 vezes |
| *"Andalusia has rising repilo."* | sobe em **2 de 7** províncias; a média regional não descreve nenhuma |
| *"Spain publishes its product registry as open data."* | **não**. Lemos o registro inteiro (3.084 registros) pela rota de exportação da própria aplicação oficial. É primária e é completa, mas **não é um dataset publicado com garantia de estabilidade** — pode mudar sem aviso |
| *"Syngenta is the holder of ES-01717."* | é **concessionária de denominação comum**. Erro observado ao vivo num resumo automático |
| *"ADAMA sells through Syngenta in Spain."* | denominação comum é ato administrativo, não acordo comercial revelado |
| *"MAXENTIS was discontinued in Spain."* | foi **renomeado**; o registro é o mesmo |
| *"We have EAME-wide comparability."* | só **área de cultura** e **preço de cereal** são comparáveis nos três países |
| *"Half the Spanish market is sold under more than one brand."* | **retirado na MISSÃO 07**. Os 50,7% eram a fração **dentro da lista de quem já tem denominação**. Sobre o registro em vigor são **18,2%** — e nenhum dos dois números é "mercado" |
| *"Counting by brand inflates the Spanish market ~2.45×."* | **retirado na MISSÃO 07**. `market` não é medível aqui: o documento não tem volume, preço nem venda. O fator medido é de **contagem de autorizações**, e sobre o registro inteiro é **1,52×** |
| *"ADAMA is the leader of the Spanish market."* | **proibida**, mesmo sendo verdade que a ADAMA é o **titular com mais registros** (188 de 3.084). Número de registros não é venda, volume nem participação |
| *"ADAMA depends on Israel for supply."* | a ficha nomeia **um** fabricante e **uma** planta para **um** registro. Não é a cadeia de suprimento da empresa |
| *"The rename shows a commercial relaunch."* | prova apenas `OFFICIAL RECORD NAME CHANGED`. Ver `../regras/REGUA-DE-CHANGE-EVENT-EAME.md` §4 |

---

## PALAVRAS SOB CONTROLE

Sete palavras só podem aparecer quando existe medida do próprio tipo por trás. Auditadas
nesta missão, uma por uma:

| palavra | onde é permitida hoje | onde foi removida |
|---|---|---|
| `market` | **em nenhuma frase segura** | claims 10 e o red team de CASE-015 |
| `leadership` | em nenhuma | — (nunca foi usada; fica proibida junto com "titular com mais registros" como sinônimo) |
| `dependency` | em nenhuma | mantida na lista proibida (fabricante ≠ cadeia) |
| `exposure` | em nenhuma | — |
| `opportunity` | em nenhuma | — |
| `inflation` | só como **excesso de contagem de autorizações**, com denominador dito | claim 10 |
| `competition` | só como **contagem de registros por titular**, com a ressalva de que não é venda | claim 1 e 8, que já dizem "registered products" e "authorised uses" |

O que temos, dito com as palavras certas: `registration` · `denomination` · `count` ·
`coincidence` · `public signal` · `record change`.

