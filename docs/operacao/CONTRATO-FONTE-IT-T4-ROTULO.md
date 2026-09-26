# CONTRATO DE FONTE — IT-T4-001 · documento RÓTULO (EtichettaServlet)

**Data:** 2026-09-26 · **Missão:** ROTULOS-T4 (`nuvem-rotulos-t4-v1`)

Este contrato **não cria SOURCE_ID novo**. O rótulo autorizado é um documento do
mesmo dono e do mesmo registo que já tem contrato — `IT-T4-001`, em
[`CONTRATOS-DAS-FONTES-EAME.md`](CONTRATOS-DAS-FONTES-EAME.md) — e é sob esse ID
que `referencia/adama/AUTHORIZED-USES.json` e `LABEL-DOCUMENTS.json` já o citam.
Inventar outro ID seria a proibição `INTELLIGENCE MUST NOT FABRICATE SOURCE_ID`
(Bíblia § 28). Aqui fica só o que é próprio do **documento rótulo**.

O parser é [`coleta/rotulo_t4_it.py`](../../coleta/rotulo_t4_it.py). A medida nos
163 rótulos reais é [`medidas/ROTULO-T4-MEDIDA-163.json`](../../medidas/ROTULO-T4-MEDIDA-163.json).

---

## O contrato

```
SOURCE_ID                 IT-T4-001  (documento: ROTULO_AUTORIZADO)
OWNER                     Ministero della Salute (Itália) — Banca dati fitosanitari
COUNTRY                   ITALY
PRIMARY/SECONDARY         PRIMARY · documento oficial por produto
PURPOSE                   CAP-LABEL e CAP-PORT (Bíblia § 34): produto × cultura × alvo
                          × dose × época × restrição × versão
CANONICAL_URL             https://www.fitosanitari.salute.gov.it/fitosanitariws_new/
                          EtichettaServlet?id=<ID_ETICHETTA>
DESCOBERTA_DO_ID          o id do servlet NÃO é o número de registo. Vem da ficha do
                          produto na banca dati. 163/163 URLs estão no
                          data/raw/IT-ROTULOS/_MANIFESTO.json (capturado 2026-09-02)
RETRIEVAL_METHOD          coleta/rotulos_baixar.py  (urllib; o curl 8 recusa o
                          cabeçalho malformado do servlet e devolve 0 bytes)
HTTP_METHOD               GET
AUTH_REQUIRED             não
OUTPUT_TYPE               application/pdf (medido: 163/163 começam com %PDF)
IDENTITY_KEYS             num_registrazione (6 dígitos, zeros à esquerda) + SHA256 dos bytes
VERSION_FIELD             SHA256 do PDF + «Etichetta autorizzata con Decreto
                          Dirigenziale del <data>» (140/163 escrevem-no) + «valida
                          dal … al …» (117/163)
JOIN_KEY_COM_O_REGISTO    o número escrito no rótulo = num_registrazione do CSV
                          PROD_FTS_6 → CONFERENCIA.REGISTO = VERIFICADO (144/163)
EXPECTED_FIELDS           por linha de uso: CULTURA · ALVO · DOSE(+unidade) · EPOCA ·
                          RESTRICOES · MAX_APLICACOES · INTERVALO_ENTRE_APLICACOES ·
                          INTERVALO_DE_SEGURANCA — cada um com o seu estado
UPDATE_BEHAVIOR           o PDF muda a cada decreto de modificação; o id do servlet
                          pode mudar com ele. O antigo não fica garantido online
HISTORICAL_OR_FORWARD     FORWARD-ONLY na prática: o que não for guardado com o
                          sha256 perde-se quando o decreto seguinte o substitui
EXPECTED_FAILURES         0 bytes com HTTP 200 (curl) · HTML no lugar do PDF ·
                          PDF de imagem sem texto · rótulo de OUTRO registo
FAIL_CLOSED_RULE          sem %PDF → ERRO. Texto < 40 caracteres → ERRO. Número do
                          rótulo ≠ registo → ERRO e ZERO linhas atribuídas
ARCHIVE_REQUIREMENT       obrigatório: PDF cru + sha256 no manifesto
DEPENDENT_TOOLS           Portafoglio / Label Intelligence (italia-portale) — hoje
                          NÃO consomem este parser (MATERIAL ≠ FERRAMENTA)
```

## Os quatro estados — e o quinto que não existe

| estado | quando |
|---|---|
| `VERIFICADO` | o registo oficial e a letra do rótulo dizem o mesmo (número, titular), ou o par vem da **linha da tabela** de um rótulo conferido como deste registo |
| `ENCONTRADO` | está escrito, citado, mas ninguém conferiu — inclui todo par vindo de **bloco de prosa** |
| `NAO_CONHECIDO` | não achámos. **Não** quer dizer que não existe |
| `ERRO` | o documento não abriu, ou registo e rótulo contradizem-se |

```
NAO_PROVADO                  !=  NAO_AUTORIZADO
APROVACAO_UE_DA_SUBSTANCIA   !=  AUTORIZACAO_NACIONAL_DO_PRODUTO
```

`NAO_AUTORIZADO` não é estado deste parser e não pode ser (`campo()` recusa-o; o
mutante M08 prova que o teste apanha quem o tentar). A aprovação europeia vive em
`aprovacao_ue()`, lê a amostra `EU-T4-001`, e nunca escreve em
`AUTORIZACAO_NACIONAL_VIVA`, que vem só de `stato_amministrativo` do Ministero.

## O que o rótulo NÃO sustenta

- «a ADAMA não tem produto para X» — 94/163 rótulos saem sem linha lida;
- eficácia, recomendação, prioridade — o rótulo autoriza, não recomenda;
- dose comparável entre produtos ou países — unidade e base diferem (CAP-LABEL
  `MUST_NOT_DO`);
- dose ligada a um alvo quando a linha tem várias doses: a lista é da linha.

---

## PLANO DE COLETA (nada disto foi executado nesta missão — sem rede)

1. **Os 163 PDFs de 02/09 já existem** fora do Git, em
   `C:/eame-sintonia/data/raw/IT-ROTULOS/` (163/163 com o sha256 do manifesto,
   conferido em 26/09). Primeiro passo, sem rede: levá-los ao armazém
   `data/collection-store/italy/IT-T4-001/` com o mesmo sha256, como já está o CSV
   `MINSALUTE_FTS6_20260907`. Quem decide se entram no Git (≈30 MB) é o dono.
2. **Revisita por mudança, não por calendário.** Comparar o CSV novo com o
   anterior: produto com `stato_amministrativo` ou `data_scadenza` mudado é o único
   que pede novo PDF. Teto D38: 5 pedidos por domínio por rodada, pausa de 1,2 s
   (a de `rotulos_baixar.py`).
3. **Guardar a versão, não substituir.** PDF novo com sha256 diferente = nova
   versão ao lado da antiga; a linha de uso aponta para o sha256 que a leu.
4. **Universo além da ADAMA** (Concorrenza, CAP-COMP): o registo tem 17.695
   produtos; 163 são de titular ADAMA e vivos. Alargar pede a descoberta do id do
   servlet por produto — **não** se chuta a partir do número de registo.
5. **O que destrava a dose.** O texto corrido perde a coluna: com duas unidades
   no cabeçalho, o parser cala-se (NAO_CONHECIDO). A geometria da página
   (`pdftotext -bbox-layout`, já usada em `IT-DOSES-2026-09-06.json`) é a porta
   para ligar número a coluna. Fica como próximo passo, não feito aqui.
