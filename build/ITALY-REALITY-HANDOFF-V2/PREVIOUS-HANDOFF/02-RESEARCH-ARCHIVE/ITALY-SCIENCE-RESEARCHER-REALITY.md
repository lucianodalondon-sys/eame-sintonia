# Ciência e pesquisadores italianos

**Data:** 2026-09-01
**Fontes:** OpenAlex (rota REST gratuita) e `pub.orcid.org`. Zero execução paga.

---

## 1 · O que já existia

### 1.1 Universo italiano por corte (`ITALY-RESEARCHER-UNIVERSE`)

**25 pesquisadores italianos**, todos com ORCID, **22 ativos desde 2024**.
Corte construído: `MAIZE_MYCOTOXIN` — 208 obras percorridas, **452 autores com afiliação italiana**,
25 detalhados.

**Instituições líderes (obras no corte):**
Università Cattolica del Sacro Cuore **193** · Institute of Sciences of Food Production (CNR-ISPA) **115** ·
National Research Council **88** · University of Milan **67** · University of Turin **67** ·
University of Parma 43 · University of Udine 28 · Sapienza 26 · University of Sassari 22

**Os cinco primeiros do corte de micotoxina em milho:**

| Pesquisador | ORCID | Instituição | Publicações no corte |
|---|---|---|---:|
| **Antonio Logrieco** | 0000-0002-8606-451X | CNR-ISPA | 27 |
| **Paola Battilani** | 0000-0003-1287-1711 | Università Cattolica del Sacro Cuore | 24 |
| **Antonio Gallo** | 0000-0002-4700-4450 | Università Cattolica del Sacro Cuore | 18 |
| **Alessandra Lanubile** | 0000-0002-1868-4469 | Università Cattolica del Sacro Cuore | 16 |
| **Antonio Moretti** | 0000-0002-5232-6972 | CNR-ISPA | 15 |

⚠️ **Confundidor declarado no próprio artefato:** as instituições líderes (Cattolica-Piacenza, Torino,
Milano, Udine) ficam **nas mesmas regiões que lideram a área de milho**. A concordância pode ser sinal
ou pode ser geografia. Não sabemos.

### 1.2 Cortes que NÃO foram construídos

`VINE_FLAVESCENCE` (135 obras) · `DURUM_FUSARIUM` (78) · `OLIVE_BACTROCERA` (70) ·
`MAIZE_BORER_DIABROTICA` (30)

Motivo medido: **HTTP 429 do OpenAlex**. O achado técnico está registrado: *"rajada, não volume diário:
paginar de 100 em 100 a cada 1,6 s derrubou o IP inteiro"*; parar ~45 s devolveu 200 imediatamente.

Estado: **`NOT_COLLECTED`, e NÃO "sem pesquisadores".** Esta é a lacuna científica mais cara — o corte da
flavescência (135 obras) é justamente o do nosso melhor caso italiano, e ele **não tem pesquisador
nomeado**.

### 1.3 Corpus profundo EAME (`RESEARCHER-CORPUS-EAME-V1`)

12 identidades provadas · **763 materiais achados** · **582 servindo de evidência** ·
118 só com coincidência de nome (descartados como prova) · 86 fora de domínio · 62 duplicados
interceptados · 505 com resumo · **88 com `COUNTRY_OF_FACT = IT`**

Recência: 23 nos últimos 180 dias, 52 nos últimos 365.

**Regra de prova registrada no artefato, que vale ouro:** *"NAME_MATCH ALONE ≠ PERSON_PROOF. O ORCID que
o OpenAlex mostra na autoria é HERDADO do perfil e não prova nada."* Só conta como evidência a obra que
passa nas **duas** portas: identidade forte **e** domínio.

Nomes italianos com corpus próprio no piloto de sensores: **Antonio Logrieco**, **Massimo Blandino**,
**F. Quaglino**, **Nicola Mori** — os dois últimos exatamente na frente da flavescência/vetor.

---

## 2 · O que a pesquisa de hoje acrescentou

### 2.1 A camada que faltava: ciência de herbicida

O acervo científico italiano é **inteiramente de doença e micotoxina**. A ciência de **resistência a
herbicida**, que é a maior linha do portfólio ADAMA, não estava mapeada.

**GIRE — Gruppo Italiano di lavoro sulla Resistenza agli Erbicidi**, hospedado pelo **CNR-IPSP**
(`gire.ipsp.cnr.it`). É a instituição de referência italiana no assunto. Publica:

- linhas-guia por espécie e cultura (*"Gestione della resistenza ad Amaranthus spp. nella soia"*,
  edições 2018 e 2022; *"Linee guida colture sarchiate"*, 2023)
- fichas por espécie: *Avena sterilis*, *Lolium* spp., *Papaver rhoeas*, *Phalaris paradoxa*, *Alopecurus*
- referência bibliográfica de peso: **Collavo e Sattin, *Weed Research*, 2014** — os primeiros biótipos
  europeus de *Lolium* resistentes a glifosato foram identificados na Itália

⚠️ **`gire.ipsp.cnr.it` devolveu certificado expirado hoje** e não abriu. Tudo acima vem de resultado de
busca e de citação de terceiros — inclusive da **Bayer Itália**, que cita o GIRE por nome no seu magazine.
**Precisa ser lido na fonte antes de virar peça do demo.**

### 2.2 Autores técnicos italianos nomeados publicamente (fora do OpenAlex)

| Nome | Papel | Onde apareceu |
|---|---|---|
| **Stefano Boncompagni** | Responsabile Settore Fitosanitario e Difesa delle Produzioni, Regione Emilia-Romagna | assina as determinações de lotta obbligatoria; palestrante no convegno Coldiretti 26/02/2026; palestra "Flavescenza dorata in Emilia-Romagna: un piano triennale di contrasto integrato" no 52º Congresso MIVA (out/2025) |
| **Luca Casoli** | Consorzio Fitosanitario Provinciale di Modena | palestrante na mesma série de convegni |
| **Fabio Mantovani** | Università di Ferrara | idem |
| **Riccardo Bugiani** e **Massimo Bariselli** | autores de *"Contro le micotossine serve l'agronomia"*, Terra e Vita, 29/04/2026 | imprensa técnica |
| Referentes científicos das janelas do Vêneto | **Dafnae-UniPD**, **DB-UniVR**, **CREA-VE** | citados no decreto e no bollettino como quem define as janelas |
| **Mirco Casagrandi** | Marketing Technical Manager, ADAMA Italia | entrevistado no blog da própria ADAMA sobre resistência de amaranto |

Estes nomes **não são pesquisadores no sentido do OpenAlex** — são a camada de **técnico institucional**,
que na Itália é quem realmente escreve o boletim e define a janela obrigatória. É uma camada distinta e o
demo ganha em mostrá-la separada.

---

## 3 · Temas científicos italianos com massa medida

| Tema | Obras no corte italiano | Estado |
|---|---:|---|
| WHEAT_FUSARIUM | **243** | maior agrupamento medido |
| MAIZE_MYCOTOXIN | **208** | 25 pesquisadores persistidos |
| GRAPEVINE_PHYTOPLASMA | **135** | **corte não construído** |
| DURUM_FUSARIUM | 78 | não construído |
| MAIZE_WEED | 79 | não construído |
| OLIVE_BACTROCERA | 70 | não construído |
| SCAPHOIDEUS_TITANUS | **66** | medido no caso IT-HERO-001 |
| MAIZE_BORER | 30 | não construído |
| MAIZE_DIABROTICA | 11 | — |
| Cercospora beticola | 5 | abaixo do limiar |
| Milho × Ostrinia × micotoxina | **5** | ⚠️ a ligação tentadora que a própria branch italiana **recusou** |

Esse último item merece destaque como exemplo de disciplina: havia a tentação de ligar o produto novo de
piralide ao grande cluster de micotoxina pela porta do Fusarium. A medição deu **5 trabalhos**. A branch
registrou: *"cinco é pouco demais. A ligação é plausível e não está provada."*

---

## 4 · Lacunas científicas, por ordem de custo

1. **Construir o corte `VINE_FLAVESCENCE`** (135 obras) — é o nosso melhor caso e não tem pesquisador
   nomeado. Rota gratuita, só precisa de paginação com pausa.
2. **Abrir o GIRE na fonte** — certificado expirado hoje; é a única camada de ciência de herbicida.
3. **Construir `MAIZE_WEED`** (79 obras) — ciência de infestante do milho, alinhada com a maior linha do
   portfólio.
4. **Ligar os 88 materiais com `COUNTRY_OF_FACT = IT`** aos casos italianos — hoje eles existem soltos.

---

## 5 · O que a camada científica NUNCA prova

- **afiliação de autor não é geografia do estudo.** O artefato repete isto em todo lugar:
  `FACT_LOCATION = "NÃO SEI — a afiliação é do AUTOR, não do estudo"`
- volume de publicação não é pressão de campo
- 208 obras dizem que o tema é **grande**; não dizem se está **crescendo** (não há série por ano)
- pesquisador ativo não é pesquisador disponível, nem endosso de produto
