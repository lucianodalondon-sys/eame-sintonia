# SOURCE PACK DO PILOTO — 13 fontes, não 35

O atlas tem **<!--M:SOURCE_ID_COUNT-->40<!--/M--> SOURCE_IDs**. O piloto não precisa deles. Estas são as fontes que
realmente alimentam as três business questions e os três hero cases.

**Dependência:** `CRITICAL` (sem ela o piloto não existe) · `USEFUL` · `OPTIONAL`.

---

## EUROPA

### EU-T4-001 · CELLAR / Publications Office — `CRITICAL`
Jornal Oficial da UE. Ato regulatório com **CELEX, data e texto integral em 24 línguas**.
SPARQL + content negotiation, sem chave. Acervo completo. Licença pública.
→ **BQ1 · BQ3 · CASE-014.** Evidência: XHTML integral por língua.

### EU-T5-001 · OpenAlex — `USEFUL`
Autoria, afiliação, país, DOI, ano. REST sem chave, décadas de histórico.
→ CASE-009, CASE-010. **Limite:** afiliação ≠ local do experimento. **GDPR:** pessoas identificadas.

### EU-T2-001 · NASA POWER + EU-T2-002 · GISCO — `USEFUL`
Série climática diária por ponto + pontos-rótulo NUTS 2. Sem chave.
→ **CASE-008** (o case de TRUST). **Limite:** é um ponto, não média regional.

### EU-T1-001 / EU-T1-002 · Eurostat — `OPTIONAL`
Área por NUTS 2 (25 anos) e rendimento por país. **Rendimento por região não existe.**

### EU-T10-001 · Agri-food Data Portal — `OPTIONAL`
Preço semanal de cereal por praça (39 praças em FR/ES/IT). REST sem chave.

## FRANÇA

### FR-T4-001 · ANSES E-Phy — `CRITICAL`
15.140 produtos · 18.558 usos autorizados **com cultura × alvo**, dose, BBCH, ZNT · titular
público. CSV via API do data.gouv, **semanal**, Licence Ouverte.
→ **BQ1 · BQ3 · CASE-014.** **É FORWARD-ONLY: precisa ser arquivado toda semana.**

### FR-T13-001 · Base SIRENE aberta — `OPTIONAL`
4.646 atacadistas de grãos, com comuna e porte. Dá **rede**, não fluxo.

## ESPANHA

### ES-T3-001 · RAIF Andalucía — `CRITICAL`
Incidência **medida em %**, por **parcela com coordenadas**, semanal, **2006–2026**,
10 culturas, CC BY 4.0.
→ **BQ2 · CASE-013 · CASE-008 · CASE-012.** É a fonte mais rica do repositório.
**Nota de acesso:** a URL que a API CKAN devolve aponta para um host inalcançável; trocando
por `www.juntadeandalucia.es` o mesmo caminho baixa.

### ES-T4-002 · Autorizaciones excepcionales — `USEFUL`
45 necessidades sem solução autorizada, com cultura, praga, substância e prazo.
**Só as vigentes** — sem histórico.

### ES-T4-005 · ROPF — rotas públicas da aplicação oficial — `CRITICAL` *(novo na MISSÃO 07)*
O registro espanhol inteiro: **3.084 registros** (1.993 em vigor), com **titular,
fabricante, planta, formulado, estado, datas** e, na ficha em PDF, **cultura × alvo**.
Um POST devolve o conjunto filtrado inteiro. → **BQ1 · BQ3 · CASE-015.**
**Limite duro:** **não é dataset publicado.** É a rota da própria aplicação — primária e
completa, mas pode mudar sem aviso. **Arquivar cada versão.**

### ES-T4-004 · Denominaciones comunes (MAPA) — `USEFUL`
Ponte entre **registro de referência** e as **marcas comerciais** que o vendem.
Versão de 26/08/2026, 90 páginas, **1.786 linhas**. → **CASE-015.**
**Limite duro:** não traz cultura, alvo nem substância; o **titular** vem do `ES-T4-005`.
A separação de colunas resolve **68,8%** das linhas com regra ancorada em fonte externa;
o resto fica `UNRESOLVED`. A heurística de forma jurídica foi testada e **descartada**.

### ES-T4-001 · Vocabulário EPPO do MAPA — `USEFUL`
492 culturas e 1.381 pragas com código EPPO e nome científico. Infraestrutura de normalização.

## ITÁLIA

### IT-T4-001 · Ministero della Salute — `CRITICAL`
17.695 produtos · 3.712 em vigor · **data de vencimento por autorização** · motivo e data de
revogação. CSV datado, CC BY 4.0.
→ **BQ1 · BQ3 · CASE-014 · CASE-015.** **Não traz cultura × alvo.**

---

## O QUE FICA DE FORA DO PILOTO — e por quê

| Fonte | Motivo |
|---|---|
| FR-T3-001 BSV · IT-T3-001 bollettini | PDF regional sem formato processável — `COMING SOON` |
| ES-T4-003 registro de produtos ES | grade renderizada por JS, sem dump aberto |
| EU-T3-001 EPPO API | exige token (o índice foi construído por HTML) |
| Sites de concorrentes | 403 / 502 / 404 |
| YouTube · Meta · TikTok | exigem credencial |
| EUIPO · EPO · Espacenet | 401 / 403 |
| FAOSTAT | passou a exigir credencial (401) |

## RESUMO DE DEPENDÊNCIA
**5 CRITICAL:** `EU-T4-001` · `FR-T4-001` · `ES-T3-001` · `ES-T4-005` · `IT-T4-001`

> Corrigido na MISSÃO 09. O resumo anterior listava quatro delas, acrescentava a
> `EU-T2-001` — que é `USEFUL` na própria ficha — e **omitia a `ES-T4-005`**, que é a
> fonte crítica sem fallback equivalente. A lista agora é derivada das fichas por
> `scripts/metricas_canonicas.py` e há prova que reprova a divergência.
**Se qualquer uma das quatro primeiras cair, o piloto perde uma business question inteira.**
Todas são públicas, gratuitas e de licença aberta. **Nenhuma exige contrato.**
