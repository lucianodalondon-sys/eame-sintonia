# ACHADO — o registro oficial italiano tem arquivo historico semanal

Medido nesta sessao, na fonte oficial, com HTTP real.

## O que se descobriu

O Ministero della Salute publica o dataset `Prodotti Fitosanitari` em
`https://www.dati.salute.gov.it/it/dataset/fitosanitari`, com frequencia de
atualizacao **semanal** (declarada na propria pagina) e ultimo carregamento
declarado em 31/08/2026.

O que a pagina mostra e so o arquivo mais recente. Mas os arquivos ficam em uma
URL com a data no nome:

    https://www.dati.salute.gov.it/sites/default/files/opendata/PROD_FTS_6_AAAAMMDD.csv

**E as semanas anteriores continuam online.** Verificado por HTTP 200 com
`content-length` distinto e `sha256` distinto, sem redirecionamento
(`num_redirects=0`), semana a semana de 2026-08-31 para tras ate 2025-07-14 sem
falha, e com pontos isolados ainda em 2024-09-02.

    2026-08-31  4594276 bytes  sha256 13537cd10b9fa59a...
    2026-08-24  4594315 bytes  sha256 8fe401895592c41e...
    2026-08-17  4594315 bytes  sha256 2aacee0bd516acf2...

As duas de agosto tem o **mesmo tamanho e hash diferente**: mudou conteudo sem
mudar tamanho. Por isso a identidade de versao neste piloto e por `sha256`,
nunca por tamanho, nome de arquivo ou data de captura.

Ha semanas com `content-length` identico repetido (por exemplo 2026-01-12 ate
2026-02-23, todas 4525133). Essas sao candidatas a **republicacao sem mudanca**.
A regra da missao vale: duas capturas do mesmo documento sao **uma** versao. So
o sha256 decide.

O arquivo nao e contiguo: 2024-11-04 responde 404 enquanto 2024-09-02 responde
200. A profundidade real precisa ser enumerada, nao assumida.

## Por que isso importa para a missao

Versionamento e diff historico **reais** deixam de depender de termos guardado
capturas antigas. A propria fonte oficial guarda. Nao e preciso inventar
historico, e nao e preciso esperar meses para ter a segunda versao.

Isso vale para a camada de **registro** (autorizacao, titular, estado, validade,
substancias ativas). Nao vale, por si so, para a camada de **rotulo** — ver abaixo.

## O limite honesto deste achado

O dicionario do dataset lista o que ele carrega:

    num_registrazione, denominazione_prodotto, ragione_sociale,
    <endereco do titular>, data_registrazione, data_scadenza_autorizzazione,
    indicazioni_di_pericolo, attivita, codice_formulazione,
    descrizione_formulazione, sostanze_attive, contenuto_per_100g_di_prodotto,
    importazione_parallela, PFnPO, PFnPE, stato_amministrativo,
    motivo_della_revoca, data_decreto_revoca, data_decorrenza_revoca

Nao ha **cultura**, nao ha **alvo**, nao ha **dose**, nao ha **intervallo**,
nao ha **numero maximo de aplicacoes**.

    REGISTRY_HAS_USE_ROWS = NAO

Essa e a diferenca estrutural com a Franca. La, o E-Phy da ANSES publica os usos
autorizados como dado aberto — por isso `FR-T4-001-adama-crop-target.json` conta
504 usos ADAMA sem ninguem abrir um PDF. Na Italia isso nao existe como dado
aberto. Cultura x alvo x dose na Italia **so sai lendo a etichetta em PDF**.

    ITALY_USE_ROWS_SOURCE = OFFICIAL_LABEL_PDF_ONLY
