# LACUNAS E VEREDITO — MISSÃO EAME 03

**Data:** 2026-08-28 · Contrato em `../apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md`

---

## AS LACUNAS, POR TIPO

### Tipo 1 · Só o tempo resolve — **começar hoje**
| # | Lacuna | Bloqueia | O que fazer |
|---|---|---|---|
| **G1** | **Linha de base histórica** de qualquer camada de conversa ou de catálogo | DECK-009, 011, 016, 022, 028 | **arquivar já** as versões semanais do E-Phy, do CSV italiano, do RAIF e dos boletins. Cada semana perdida não volta. |

### Tipo 2 · Falta pesquisa dirigida
| # | Lacuna | Bloqueia | Estado |
|---|---|---|---|
| **G2** | **manufacturer · fonte autorizada · país de origem** | DECK-006, 012, 029 | **nunca investigado**. Confirmado que o registro nacional **não** contém: `titulaire` e `ragione_sociale` são titular de registro. |
| **G5** | comunicação de concorrente (anúncios, campanhas, claims) | DECK-005, 011, 028 | 403/502/404 nos três sites testados |
| **G6** | patente e marca | DECK-015 (contexto) | EUIPO API 401 · EPO OPS 403 · Espacenet 403 · PatentsView bloqueado |
| **G7** | distribuição na Espanha e na Itália | DECK-008, 021 | França resolvida (4.646 empresas); ES e IT não investigadas |
| **G8** | catálogo e acordos de distribuição | DECK-021 | nenhuma fonte — a base francesa dá **rede**, não **fluxo** |

### Tipo 3 · Falta engenharia, o dado existe
| # | Lacuna | Bloqueia | Custo |
|---|---|---|---|
| **G3** | normalização FR→EPPO acima de 23,5% do uso | DECK-013, 019, 020 | médio — o gargalo é **cultura-grupo** francesa |
| **G4** | normalização de titular → grupo empresarial | DECK-015 | baixo |
| **G9** | versionamento semanal do registro para detectar "novo" | DECK-012 | baixo — e é o mesmo trabalho de G1 |

### Tipo 4 · Falta decisão humana
| # | Pergunta | Bloqueia |
|---|---|---|
| **P-003** | portfólio **comercial** da ADAMA (o registrado já resolvemos por fonte pública) | prioridade real |
| **P-006** | criar conta EPPO para a API | nada crítico — o índice já foi construído por HTML |
| **P-007** | uso de coordenadas de parcela do RAIF | qualquer exposição externa |
| **P-008** | perfilamento de pesquisadores nomeados | área SCIENCE |
| **P-009** | chave YouTube e decisão sobre perfilar criadores | DECK-007, 009 |
| **P-010** | **anexar o arquivo da apresentação** e reconciliar os 30 claims | precisão do contrato |
| **P-011** | acesso ao registro espanhol de produtos | DECK-001 na Espanha |

---

## VEREDITO

**Pergunta:** *se construíssemos amanhã o casco exatamente de acordo com a apresentação que
a ADAMA recebeu, quais partes seriam alimentadas por capacidade REAL, quais seriam PARCIAIS
e quais ainda seriam apenas conceito?*

### Alimentado por capacidade REAL — pode ir para o design agora
1. **REGULATORY REVIEW** — ato da UE com CELEX e data, ligado ao produto nacional e ao
   portfólio registrado da ADAMA, em quatro línguas. (DECK-001, 010)
2. **MOLECULE WATCH no eixo substância** — a mesma molécula atravessando FR, ES e IT, com
   **82,1% do uso** normalizado. (DECK-014)
3. **SCIENCE & EXPERTS** — quem trabalha repetidamente num problema, por país, com a
   armadilha da consulta larga medida e evitada. (DECK-002)
4. **PEST & DISEASE na Andaluzia** — incidência medida por província e por semana, incluindo
   infecção latente. (DECK-007 parcial, mas a Andaluzia é real)
5. **CROPS & CLIMATE como contexto** — área por NUTS 2 com 25 anos e clima por janela
   fenológica. (DECK-003)
6. **ASK SINTONIA** — a camada de evidência **é consultável**: 4 perguntas respondidas com
   FACT/DERIVED/UNKNOWN e 1 corretamente recusada. (DECK-023)
7. **A disciplina de evidência** — toda resposta leva à fonte; "não sabemos ainda" é
   comportamento testado. (DECK-024, 025)

### PARCIAIS — o design pode mostrar, com a limitação visível
8. **COMPETITIVE** — forte no registro (quem tem direito de uso em cada combate), **vazio**
   na comunicação.
9. **MARKET** — variável a variável: área ✅, rendimento nacional ✅, preço por praça ✅,
   rendimento regional ❌, comércio exterior ⚠️.
10. **DISTRIBUTION** — a rede francesa existe e é boa; o fluxo não existe; ES e IT não foram vistas.
11. **SAME ISSUE entre mercados** — o identificador comum existe do lado espanhol e resolve
    **23,5%** do uso francês.

### Apenas CONCEITO — o design **não** pode apresentar como capacidade
12. **ALERT** — a régua existe, a porta BASELINE não abre. Hoje o sistema emite **WATCH** e
    **INVESTIGATE**, não ALERT.
13. **"rises" / "increases"** em qualquer camada — sem histórico, snapshot não é tendência.
14. **FIELD VOICES** — sem fonte. Só REACH seria mensurável, e depois de alguém escolher os canais.
15. **MANUFACTURER, ORIGEM e SUPPLY WATCH** — nunca investigados; o registro não os contém.
16. **MARKETING OPPORTUNITY** — dois dos quatro lados estão fracos. Estágio atual:
    **PARTIAL CONNECTION**, não oportunidade.

### Resposta em uma frase
> **PARCIAL — e com um eixo pronto.** O eixo **REGULATÓRIO → MOLÉCULA → PORTFÓLIO** está
> provado ponta a ponta, em três mercados, com identificador, data e evidência preservável:
> dá para desenhar e apresentar amanhã. O eixo **CAMPO → COMUNICAÇÃO → TENDÊNCIA** não
> está, e não é por falta de pesquisa: **falta linha de base histórica**, que nenhuma
> pesquisa cria — só o tempo. Começar a arquivar hoje é a decisão mais valiosa disponível.

---

## RECOMENDAÇÃO DE PILOTO

**Mercados:** França, Espanha, Itália (já é o recorte).

**Duas business questions — e só duas:**

1. **REGULATORY & PORTFOLIO** — *"O que mudou, o que isso toca e onde?"*
   **Por quê:** é o único eixo `PROVED` ponta a ponta, tem alinhamento HIGH com o radar
   público da ADAMA (cereal nos três países) e já tem HERO CASE pronto (CASE-011).

2. **PEST PRESSURE & TIMING (Espanha)** — *"Onde a pressão está subindo e o que ela exige
   esta semana?"*
   **Por quê:** é a capacidade mais próxima da operação encontrada em toda a missão — o
   repilo incubado decide a semana da aplicação — e tem alinhamento HIGH (Neptune, Plan STAR
   Olivar). Limitação declarada: **só Andaluzia**.

**Não recomendar como business question do piloto:** qualquer coisa que dependa de
"increasing", de comunicação de concorrente ou de vozes do campo. Seriam promessas que a
matéria-prima não sustenta hoje.

## HERO CASES RECOMENDADOS — 4
| # | Caso | Por que |
|---|---|---|
| 1 | **CASE-011** protioconazol | prova 5 dos 6 elos da cadeia CONNECT do deck, num só caso |
| 2 | **CASE-008** o clima não explica a doença | prova que o sistema **recusa** a correlação fácil — sustenta a confiabilidade de todo o resto |
| 3 | **CASE-012** repilo incubado no olivar | a capacidade mais operacional, alinhada ao portfólio espanhol |
| 4 | **CASE-003** calendário de vencimentos na Itália | 58 autorizações ADAMA vencendo em ≤6 meses, contra 20,9% do mercado |
