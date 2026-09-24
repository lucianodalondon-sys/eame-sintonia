# RELATÓRIO — YT1 · CANÁRIO REAL DE 1 VÍDEO DO YOUTUBE (ÁUDIO PÚBLICO)

2026-09-23 · branch `youtube-oficial-v1` · rota declarada pelo Sintonia Scrap (D17) · 1 vídeo ·
VPN IT medida antes · base DESCARTÁVEL (nada na Sala real) · custo US$ 0.

```
VIDEO            7Ps4g3juOIU (IT-T8-001 AgroNotizie)
RAW              PASS · audio/wav · 7.112.072 bytes · sha256 7785c5059749335040a059bf55812d5bc2c7ddd929eb1672a886f557aeff2bda
DERIVED          PASS · transcrição it · 3.346 bytes (faster-whisper small, CPU)
DOCUMENT_ID      NAO SEI (o envelope do áudio não traz)
PROVENIENCIA     CAPTURED_AT presente · PUBLISHED_AT ausente (a rota não consulta a API) ·
                 FACT_TIME não perguntado no estágio DOCUMENTO — nenhuma data trocada por outra
ADMISSION        1.ª corrida: UNIVERSO_NAO_DECLARADO (o comando não traz universo) · RC 1
                 2.ª (reprocesso, sem rede, universo=T8): 5 SIM e NAO_SE_APLICA em
                 «pertence ao universo» — não há régua T8
SALA (teste)     0
```

**O que falta:** (1) `--filtro universo=…` no comando; (2) a régua T8 da Admissão — decisão do
dono; (3) `PUBLISHED_AT` na rota de áudio, vinda da fase `video-youtube` (engenheiro do Scrap,
`scrap-portas-v1`).

**Em palavras simples.** O sistema pegou o som do vídeo, guardou-o com a "impressão digital"
dele e escreveu o que foi dito. O porteiro da Sala conferiu cinco coisas e todas estavam certas;
na sexta — "isto é assunto de agricultores?" — ele não tem lista do que conta, e por isso não
deixa entrar nem joga fora. Falta escrever essa lista.

Detalhe e armadilhas de ambiente: §199 do `SINTONIA-EAME-KNOW-HOW.md` (era §196 na lane; renumerado na UNIFICACAO-V1-E). Evidência (fora do Git):
`%TEMP%\yt1-evidencia`.
