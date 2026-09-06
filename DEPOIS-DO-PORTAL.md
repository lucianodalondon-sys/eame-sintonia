# DEPOIS DO PORTAL — o que ficou por fazer em 06-09-2026, e porquê

Missão do dia: pôr o portal a funcionar num endereço público e provar que
funciona. O que está aqui NÃO foi feito, e cada linha diz porquê. Nada nesta
lista foi descoberto tarde demais: tudo foi medido, e a decisão de adiar é
explícita.

    UMA DÍVIDA ESCRITA É UMA DÍVIDA. UMA DÍVIDA ESQUECIDA É UMA SURPRESA.

---

## 1 · O PACOTE CANÓNICO NÃO ESTÁ NO REPOSITÓRIO  · bloqueia 5 controlos

**O que é.** O portal serve `V21-69bf448ac934a6d9`, 43 casos. O pacote que o
produziu — `build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/` — não está
versionado: *gera-se, não se guarda*. No repositório existe apenas o ZIP
histórico `V21-99226fbb90dcdbc2` (37 casos, sem `MEETING_SURFACE_RULE`), que o
próprio `CANONICAL-PACKAGE-CONTRACT.json` nomeia como safra velha e que o
portão da build recusa como controlo negativo.

**Consequência medida.** Cinco controlos não podem correr e passam a declarar
`NON MISURATO`: `W2`, `O1`, `BR6`, `CANONICAL_PACKAGE_ACCEPTED` e
`43_CASE_IDS_PRESERVED`.

**Porque não hoje.** A cadeia é explícita: esta linhagem é CONSUMIDORA. Corrida
aqui produz `V21-5d312cb90a0de01d` — safra velha, com `PREPARE_NOW` revogado em
onze casos. O gerador canónico é `claude/opportunity-commercial-priority-v1 @
55c2674`.

**Como se fecha.** Gerar na linhagem canónica e trazer o pacote. Não o
contrário.

---

## 2 · O PACOTE DE ACÇÃO NÃO SE ALCANÇA A PARTIR DE UMA OPORTUNIDADE · P13

**O que é.** `[data-download-pdf]` vive na tela `case` antiga. O radar abre o
detalhe da reunião, que tem a MAPPA DELLE AZIONI com os cinco departamentos mas
nenhum controlo de descarga. As pastilhas da tela de Finestre Colturali chamam
`openBrief(wdR.legacyCaseId, …)`, e `legacyCaseId` é `null` nos 43 casos do
motor.

**Medido no browser**, sobre os bytes publicados: a partir do radar e a partir
das Finestre Colturali, zero pastilhas de brief e zero controlos de descarga.

**O que NÃO falta.** O conteúdo por público está no ecrã: cinco departamentos
— Sviluppo Mercato, Commerciale, Marketing, Tecnico/Scientifico, Supply — cada
um com acção, dependência e o que a desbloqueia. O que falta é o formato de
distribuição.

**Porque não hoje.** Ligar o gerador de briefs a um caso da reunião exige um
adaptador novo, e o gerador escreve em inglês. Produzir prosa de cliente à
pressa, em inglês, para uma demonstração italiana, é pior do que não a
produzir.

---

## 3 · BW3 · UM TÍTULO DE 25 px EM CAIXA ALTA

`"AZOXYSTROBIN + PROTHIOCONAZOLE"` vem do dado — `italy-casa.js`, gerado por
`scripts/it_casa_dados.py` — e não do estilo. Uma transformação genérica de
caixa arriscaria estragar nomes de substância activa. Corrige-se a montante,
no gerador.

---

## 4 · O QUE ESTA MISSÃO NÃO TOCOU, DE PROPÓSITO

- **Traduções aprovadas dos campos narrativos.** Medido na linhagem canónica
  (a de 496 KB, hoje guardada em `salvaguarda/portal-canonico-2nknje`): 378
  campos `narrative()` em todo o modelo, ZERO com variante localizada
  aprovada. Não é a linhagem que está no ar, e a que está no ar não tem este
  problema à mesma escala. Fica medido, não fica resolvido.
- **A promoção para o apex.** `sintonia-eame-preview.vercel.app` continua a
  servir `cfbd8a4`. A promoção é um clique no painel da Vercel (o deploy actual
  do apex foi criado por `action: promote`) e não há ferramenta neste ambiente
  que o faça.
- **Brasil → EAME, Passaporte, Universal, Label Intelligence, Disease
  Forecast, Supabase, nova recolha externa.** Fora do âmbito do dia, por
  instrução.

---

## 5 · O QUE MUDOU DE BASE, E PORQUÊ IMPORTA

O portal do ar NÃO é o da `sintonia/canonical`. São duas linhagens:

| | canónica | a que está no ar |
|---|---|---|
| `portale.html` | 496 KB, 02-09 | 871 KB, 05-09 |
| auditoria | 40 controlos | 71 controlos, 53 módulos |
| casa.html, adama-relevance.js, vendor/, upstream/ | não tem | tem |

Trabalhar na primeira e publicá-la teria apagado três dias de trabalho e a
regra «só é oportunidade o que se liga a um produto ADAMA». O trabalho feito
na linhagem canónica antes de a base mudar está guardado em
`salvaguarda/portal-canonico-2nknje`, empurrado, não apagado.
