# Realidade regional italiana — cultura, fonte e o viés entre as duas

**Data:** 2026-09-01

---

## 1 · Cobertura de fonte: 8 de 20 regiões

`ITALY-REGIONAL-COVERAGE-MATRIX` mede 8 das 20 regiões italianas com fonte de campo. As outras 12 são
`NOT_MEASURED`, **não** "sem fonte".

---

## 2 · O viés medido, que é o achado mais importante desta camada

**A cobertura de fonte não segue a área da cultura.** Medido, não suposto:

| Cultura | Onde está a área | Onde está a fonte medida |
|---|---|---|
| **Milho** | Veneto, Lombardia, Piemonte, FVG = ~70% da produção; as três primeiras somam **71,6% da área** | **nenhuma delas tem boletim de milho medido**. O Piemonte publica boletim de milho (10 números em 2026, último de 12/08) mas é a 5ª região, com **6,7%** da área |
| **Trigo duro** | Puglia, Sicilia, Basilicata, Marche, Toscana | as duas maiores regiões de trigo duro **nunca entraram no painel**; o boletim que temos é da **Toscana (Grosseto, 3,7% da área nacional)** |
| **Vite** | Veneto 101,0 mil ha (2º, 17,2%), Puglia, Sicilia, Toscana, Piemonte | Veneto ✅, Emilia-Romagna ✅, FVG/Collio ✅, Lombardia ✅, Piemonte ✅ (via decreto), Trentino ✅ (via boletim especial) |

Consequência direta: **quando o Sintonia disser "X% de cobertura de sinal para uma cultura", precisa dizer
de qual denominador está falando** — número de regiões, ou área da cultura. São respostas diferentes, e o
artefato `ITALY-PANEL-BIAS` foi escrito exatamente para isso.

---

## 3 · As fontes regionais que temos, por região

| Região | Fonte | Documento preservado | Data |
|---|---|---|---|
| **Toscana** | Consorzio LaMMA (Regione Toscana / CNR) | bollettino fitosanitario Grosseto (HTML + JSON) | 2026-04-23 |
| **Friuli-Venezia Giulia** | ERSA FVG | Difesa integrata colture erbacee — frumento/orzo n.07 | 2026-04-20 |
| **Friuli-Venezia Giulia** | Consorzio Collio (Enol. Dario Maurigh) | Bollettino difesa integrata vite n.06 | 2026-05-15 |
| **Marche** | AMAP — Centro Agrometeo Locale, Ancona | Notiziario di produzione integrata n.615 | 2026-04-22 |
| **Marche** | AMAP — Ancona | Notiziario n.616 | 2026-04-29 |
| **Umbria** | Servizio Fitosanitario Regionale | Bollettino cereali n.04 | 2026 |
| **Veneto** | Servizio Fitosanitario | Bollettino vite n.19 (citado) · DDR n.13645 | 2026-08-13 · 2026-05-14 |
| **Lombardia** | Giunta Regionale | Comunicato n.39 — lotta obbligatoria | 2026-05-25 |
| **Piemonte** ⭐ | Settore Fitosanitario | Det. Dirigenziale n.280 — piano operativo 2026 | 2026-03-16 |
| **Trentino** ⭐ | — | Bollettino speciale Flavescenza dorata n.1 | 2026-05-29 |
| **Emilia-Romagna** ⭐ | Settore Fitosanitario e Difesa delle Produzioni | piano triennale desde 2023; série de capturas em armadilha apresentada em 26/02/2026 | 2026 |
| **Puglia** | Agrometeo Puglia · Assoproli Bari (olivo) | sondados, `GREEN`, sem documento preservado | — |

⭐ **Regiões novas desta pesquisa** — não estavam no acervo.

---

## 4 · Um comportamento italiano que o modelo precisa respeitar

**O modelo de publicação difere por região.** O artefato `IT-lotta-obbligatoria-flavescenza-2026` já
registra isso para Lombardia e Veneto, e a pesquisa de hoje confirmou o padrão em mais quatro:

- **Lombardia**: comunicado da Giunta com janelas fixas de data (2–14/06 e 17–29/06)
- **Veneto**: decreto + bollettino semanal que **define a janela em função da fenologia**, com referentes
  científicos nomeados (Dafnae-UniPD, DB-UniVR, CREA-VE)
- **Piemonte**: determinação dirigencial + bollettini com épocas e ativos admitidos, mais uma proibição
  legal própria (L.R. 1/2019 — proibido tratar durante a floração)
- **Trentino**: bollettino especial dedicado

Ou seja: **"a Itália" não publica de um jeito só.** Uma tela que trate "fonte Itália" como um único
objeto esconde exatamente a informação que decide — em que região, sob qual regra, e com que janela.

---

## 5 · Escala das culturas (ISTAT / Eurostat)

| Cultura | Área nacional | Observação |
|---|---:|---|
| Frumento (duro + mole) | ~1.700 mil ha | fonte: site ADAMA |
| Vite (DOP+IGP+mesa) | **588,8 mil ha** | ISTAT · ⚠️ Eurostat W1000 dá **715,8** — definição diferente, **não trocar um número pelo outro** |
| Soia | ~350 mil ha | site ADAMA |
| Orzo | ~260 mil ha | site ADAMA |
| Riso | ~220 mil ha | site ADAMA · ~60% das risaie europeias; Piemonte + Lombardia = 92% da área |
| Trigo duro | **1.177,4 mil ha** | ISTAT (`IT-CASE-DURUM-FUSARIUM-001`) |
| Pomodoro da industria | **75.863 ha** (2024) | site ADAMA · 5,3 Mt transformadas, 45% bacino Nord, 55% Centro-Sud |

**Regiões líderes de vite:** Veneto 101,0 mil ha (2º, 17,2%) · Lombardia 18,2 mil ha (7º, 3,1%).
**Regiões líderes de milho:** Lombardia, Piemonte, Veneto, FVG — ~70% da produção.

---

## 6 · Camada de organização de produtor — o que acontece quando a região para de publicar

`ITALY-OP-FIELD-LAYER` responde a uma pergunta boa: *quando o serviço regional para de publicar
fitopatologia, de onde vem o sinal de campo?* Resposta medida: **muda de dono** — passa para
organizações de produtores (Assoproli Bari no olivo, na Puglia e Umbria) e consórcios
(Consorzio Collio na vite, no FVG; Co.Pro.B. na barbabietola).

O boletim do Collio, por exemplo, é assinado por um **enólogo nomeado** (Dario Maurigh), não por um
serviço regional. É sinal de campo real, com outra classe de dono.

---

## 7 · Onde estão os buracos

1. **12 das 20 regiões** sem fonte medida
2. **Nenhum boletim de milho** nas três maiores regiões de milho
3. **Puglia e Sicilia** — as duas maiores de trigo duro — sem documento preservado
4. **Nenhuma fonte** para olivo, barbabietola, patata e girassol, culturas com registro ADAMA
5. Rotas ao vivo que falharam hoje: **Veneto bloqueia por IP** (mensagem explícita com o IP ecoado),
   Emilia-Romagna e ERSA FVG deram 404 nos caminhos tentados
